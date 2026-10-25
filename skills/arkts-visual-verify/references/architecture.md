# 架构：图遍历 + 真实点击

> arkts-visual-verify 的核心架构。SKILL.md §12 引用本文档。

---

## 1. 设计动机

静态截图对比对**纯展示页**有效，但对**有交互的页**失效。盲区类型：

| 盲区 | 例子 |
|---|---|
| 按钮 `onClick` 接错 / 没接 | HMOS 按钮看起来对，点了没反应 |
| 路由参数传递错 | 跳转到了但参数丢失，页面缺数据 |
| 跨页流转故障 | "我的→账号→修改头像→相册"任一断点 |
| Back 按钮失效 | HMOS 页 back 不能回 parent |
| 拦截弹窗逻辑差 | 未登录访问 VIP 页该弹拦截，HMOS 直接进 |

am-start 直跳 + mock 数据掩盖真实流程 → 这些 bug 全漏。

## 2. 核心策略

```
把 fact-tree 当有向图遍历（不是按 reach_paths 路径罗列）
  → 真实点击 trigger 完成跨页跳转
  → 每条 edge 测一次：先 iOS 验证 edge 存在 → 再 HMOS 验证 edge 可点
  → 失败 edge 阻塞子树，等修复后下轮自动重测
```

**不再用** am-start 直跳目标页。**不再用** mock 数据掩盖真实数据流转。**保留** scenario YAML 但只用于"登录/态切换"等 app 初始态准备，不用于绕过流程。

### 为什么 iOS 源端先验证

fact-tree 是 toolkit 静态分析产物，**已知存在错识别**（lambda 控制流追不到、自循环边等）。直接报"HMOS NAV_FAILED"会冤枉 HMOS：

- fact-tree 把废弃方法识别成跳转 → iOS 也跳不了 → HMOS 跳不了 → 误报 HMOS bug
- 自循环边 (`from == to`) → 两端都点不出新页 → 同上

**iOS 能点 HMOS 不能 = 真 HMOS bug；iOS 也不能点 = fact-tree 错**。这个区分对报告可信度至关重要。

---

## 3. 两趟图遍历

```
Trip 1: logged_out 态
  visited_1 = {}
  起点 = launcher (SplashActivity)
  覆盖 = Login / Splash / Guide / Agreement / 隐私页 等 ~9 个

Trip 2: logged_in (VIP)
  reset app + run login.yaml (测试账号本身是 VIP)
  visited_2 = {}
  起点 = HomeActivity
  覆盖 = 剩余 ~100+ 页
```

**明确放弃的覆盖**（后续真需要时加 Trip 3 logged_in_no_vip）——
即 SKILL.md §1.1 第 4 条里的**「iOS真没有」= 合法出界**那一类：iOS两趟都不覆盖，
鸿蒙侧自然也无 GT 可对，**不算债、不出单**。与"iOS ⊆ 鸿蒙一个都不许丢"不冲突——
后者管的是iOS**覆盖到了**的东西。切勿把本节当成"漏采也可以放弃"的依据：

- VIP 拦截弹窗（"开通会员" CTA）
- 免费次数耗尽提示
- "升级 VIP" 按钮态变化

剩 80%+ UI 都能覆盖。

**visited set 两趟独立**：HomePage 在 logged_out 和 logged_in 下 UI 不同（顶栏显示登录按钮 vs 用户名），必须各遍历一次。

### 数据态：sub-agent 现场决定

遍历到需要数据态的页面（如 ContentActivity 要"有文档"）时：

```python
def handle_data_state_required(page, required_state):
    if data_already_exists(required_state):
        return OK  # 测试账号 DB 通常有真实数据
    if can_walk_creation_flow(required_state):
        try:
            walk_real_creation_flow(required_state)  # 真去拍照→OCR→保存
            return OK
        except: pass
    log_finding(kind="SKIPPED_DATA_REQUIRED", severity="P3", page=page,
                reason=f"无法获取 {required_state}，跳过本页")
    return SKIP
```

**好处**：0 个 mock yaml 维护成本；真实数据 + 真实创建流程比 mock 更接近用户场景；跳过的页有 finding 记录不会沉默丢失。

**代价**：sub-agent 每次行为可能略有不同；如果 VIP 账号 DB 空了，相关页会都跳过。

---

## 4. 失败 edge 核心算法

```python
for edge in fact_tree.flow_graph.edges_from(current):
    target = edge.to
    if target in visited[trip]:
        continue

    # 数据态按需注入
    for pc in target.preconditions:
        if pc not yet satisfied:
            inject_scenario(pc.scenario_name)

    # ─── 步骤 1: iOS 源端先点（基准侧）─────────────────
    ios_ok = click_and_verify(edge, device="ios")
    if not ios_ok:
        log_finding(kind="FACT_TREE_INVALID_EDGE", severity="P2",
                    edge=edge, fix_owner="app-relationship-tree")
        continue  # fact-tree 错，跳本 edge 不冤枉 HMOS

    # ─── 步骤 2: HMOS 端点 ──────────────────────────────
    hmos_ok = click_and_verify(edge, device="harmonyos")
    if not hmos_ok:
        log_finding(kind="CRASH_NAV_FAILED", severity="P0",
                    edge=edge, block_subtree=True)
        mark_subtree_blocked(target,
            blocked_by=f"{current}→{target}",
            blocked_by_md=f"CRASH_NAV_FAILED_{current}_to_{target}.md")
        continue

    # ─── 两端都能跳 → 截图对比 + 递归 ──────────────────
    screencap_both(target)
    multimodal_compare(target)

    # ─── 步骤 3: back 按钮验证 ──────────────────────────
    press_back(device="harmonyos")
    if current_page() != current:
        log_finding(kind="BACK_FAILED",
                    severity="P0" if back_critical(target) else "P1",
                    edge=edge)
        am_start(current)  # 恢复，不让 back bug 卡住遍历

    visited[trip].add(target)
    queue.append(target)

    if len(visited[trip]) % 15 == 0:
        reset_and_replay_scenario(trip)  # 每 N 页做一次 hygiene
```

---

## 5. 阻塞子树语义

### 5.1 阻塞 markdown 写什么

**Root cause finding**（一份正经 P0）：

```markdown
---
kind: CRASH_NAV_FAILED
severity: P0
edge: {from: HomePage, to: MinePage, trigger: {label: "我的", resource_id: tab_mine}}
ios_verified: true
hmos_failed_reason: button_no_response
blocks_subtree: [AccountInfoActivity, AboutUsActivity, ManageRenewActivity, RefundProgressActivity, ...]
---
# HomePage → MinePage 跳转失效
iOS 源端点击底部"我的" tab 正常跳转。HMOS 端点击同位置按钮无响应（3 次重试 verify_signal 未出现）。
阻塞 MinePage 子树 8 个页面本轮无法测试。修复后下轮自动重测。
```

**子树 placeholder**（每个被阻塞页一份，不算正经 finding）：

```markdown
---
status: blocked
blocked_by: spec/fix/round-N/ui/CRASH_NAV_FAILED_HomePage_to_MinePage.md
page_id: AccountInfoActivity
disposition: pending_upstream_fix
---
本页可达性依赖 HomePage → MinePage 这条 edge。修复 root cause 后本轮自动重测。
```

### 5.2 _summary.md 报告样式

```markdown
## 严重故障 (P0, 1 root + 8 blocked)
- 🔴 CRASH HomePage → MinePage 跳转失效 (HMOS button 无响应)
  └─ 阻塞 8 个下游页面: AccountInfo, AboutUs, ManageRenew, ...
       待 root cause 修复后下一轮自动重测
```

### 5.3 carry-forward 自动重测

```
Round N: HomePage → MinePage 失败 → 8 page 阻塞
Round N+1 (修复 onClick 后):
  Phase 3.5 batch 切分时扫上一轮 CRASH_NAV_FAILED_*.md，对应 blocks_subtree 标 retry_priority=high
  Trip 2 走到 HomePage → 检测到上轮失败 edge 优先重测
    click → success → 解锁子树 → 继续遍历
```

每轮**剥一层** failed edge，多轮后达到稳定。

---

## 6. HMOS 架构约束

**HMOS app 典型架构**：单一 `PhoneAbility`（或 `EntryAbility`），所有"page"是该 ability 内的 NavDestination，由 NavPathStack / RouterUtils 路由。

**意味着**：
- `hdc shell aa start -a PhoneAbility -b <bundle>` 只能启动到 launcher 屏（HomePage）
- **无法用 am-start 直跳内部页**（如 AccountInfoActivity / MemberCenterActivity）—— ability 是同一个，aa start 不会让 NavPathStack 自动 push 到目标
- 唯一到达内部页的方式：**从 launcher 真实点击链路**走过去（或 app 自己实现 deep link，scan 项目未实现）

**对 walk_to.py 的影响**：
- am-start fallback **仅对 launcher 类目标有效**
- 内部页只能走 Mode A (real_click via reach_path)
- 若 reach_path 不完整（label=null / 长度=1）→ 直接报 no_path，**不要尝试 am-start**（必失败 + 浪费 8s timeout）

**对 sub-agent 的影响**：
- 每个 batch 起点必须是 launcher / home（aa start 能到的位置）
- 内部页必须通过 click_and_verify_edge 链式跳转
- 跨 batch 间如果终点不是 home，下一 batch 开始必须 reset 回 home
- fact-tree.flow_graph.edges 是导航的唯一数据源（reach_path 在很多页是单点 = 不可用）

**对 iOS 源端的影响**（未实测）：
- iOS Activity 模型允许 `am start -n com.x/.PageActivity` 直跳任何 activity（如 manifest exported=true）
- 所以 iOS 源端 am-start fallback **大概率可用**，有 exported=false 限制时也会失败

---

## 7. 性能预算

| 趟 | 页数 | 单页耗时 | 趟总耗时 |
|---|---|---|---|
| Trip 1 (logged_out) | 9 | ~20s | ~3 min |
| Trip 2 (logged_in_vip) | ~100 (含 fragments/dialogs)| ~45s（含 click+verify+back+screencap+多模态）| ~75 min |
| 跨 trip 聚类 + 汇总 | - | - | ~5 min |
| **总计** | ~109 | - | **~80 min** |

值不值看优先级。CI 场景下夜间跑全量，开发期跑 trip_1 + 少量 batch 子集，是合理折中。
