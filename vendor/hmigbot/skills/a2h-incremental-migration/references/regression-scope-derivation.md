# §SR 回归范围派生（references 详细版）

主 SKILL.md §SR 的详细执行手册。**所有模式共享，必跑**。

包含两阶段派生：
- **SR.1 改前派生 → 清单 A**（左移预测）
- **SR.2 改后审查 → 清单 B**（事实校准）
- **SR.3 R = A ∪ B**（最终回归清单）

## 1. 目的与两阶段设计

清单 A 是基于 `expected_files` 的**预测**——能识别大多数受影响 baseline AC，但有盲区：
- 实际代码可能多碰了 expected_files 之外的共享方法（跨调用链）
- 实际改动引入了新的 EventBus 事件 / @Provider/@Consumer key（派生时这些还不存在）
- LLM 实际生成的代码命中了 §SR.1 没预见的 baseline AC

清单 B 用**实际改动**重跑同样的派生规则，把上述盲区抓回来。**两者并集 R = A ∪ B 才是完整回归清单**。

`only_in_B`（B 抓到但 A 没预见的）是高价值信号——意味着派生 SR.1 漏了，需要追加到漏报模式知识库让下次更准。

**确定性 grep + LLM 兜底**，不是凭印象判断。

## 2. SR.1 + SR.2 派生规则（机械执行，同一套 7 维 grep）

**SR.1（改前清单 A）输入**：差异条目的 `expected_files`（§M3 即 H_TARGETS）

**SR.2（改后清单 B）输入**：
```bash
cd {hmos_project}
git diff --name-only HEAD > /tmp/actual_files.txt    # evolver execute 后的实际改动
git diff HEAD > /tmp/actual_diff.patch
# 注意：SR.2 触发时机是 evolver execute 完成、verify 前。incremental-migration 重新介入跑本节
```

两阶段都用下面的 7 维 grep + LLM 语义补全，**只是输入不同**：
- SR.1: 输入 = `expected_files`
- SR.2: 输入 = `actual_files`（实际改动文件 + diff）



```bash
HMOS={hmos_project}
H_TARGETS=("entry/src/main/ets/pages/MainPage.ets" "entry/src/main/ets/viewmodels/ItemsViewModel.ets")

# (a) 文件粒度反查：对 H_TARGETS 每个文件，找哪些 baseline AC 引用它
> /tmp/regression_files.txt
for FILE in "${H_TARGETS[@]}"; do
  BASE=$(basename "$FILE")
  COMP=$(echo "$BASE" | sed 's/\.ets$//')
  echo "=== $FILE ==="
  grep -rln -E "$BASE|$COMP" $HMOS/spec/baseline/features/ $HMOS/spec/baseline/ui/ 2>/dev/null
done | tee /tmp/regression_files.txt

# (b) 子组件/struct 粒度反查
SUB_STRUCTS=("ItemsView" "ItemBuilder")
for S in "${SUB_STRUCTS[@]}"; do
  grep -rln "$S" $HMOS/spec/baseline/ 2>/dev/null
done >> /tmp/regression_files.txt

# (c) 共享方法/字段粒度反查
SHARED_METHODS=("loadItemsList" "deleteSelected")
for M in "${SHARED_METHODS[@]}"; do
  grep -rln "$M" $HMOS/spec/baseline/ 2>/dev/null
done >> /tmp/regression_files.txt

# (d) 从命中的 baseline 文件中提取 AC ID
sort -u /tmp/regression_files.txt | xargs -I{} grep -HnoE "AC[0-9]+|F[0-9]{3}-AC[0-9]+|P[0-9]{4}-UI-(SMOKE|COMP|NAV|INTERACT)[-_a-zA-Z0-9]*" {}

# (e) 事件层耦合：扫 EventBus / emitter event id，反查谁订阅
EVENT_IDS=$(grep -hoE "EventId\.[A-Z_]+|emit\(['\"][a-zA-Z_]+['\"]|emitter\.(emit|on)\(['\"][a-zA-Z_]+['\"]" "${H_TARGETS[@]}" 2>/dev/null \
            | grep -oE "[A-Z_]{2,}|['\"]([a-zA-Z_]+)['\"]" | tr -d "'\"" | sort -u)
for eid in $EVENT_IDS; do
  echo "=== event $eid ==="
  grep -rln "$eid" $HMOS/spec/baseline/ 2>/dev/null
done | tee -a /tmp/regression_files.txt

# (f) 状态层耦合：扫 v1+v2 状态装饰器 + AppStorage/AppStorageV2 key
#     v1: @Provide/@Consume/@StorageLink/@StorageProp（识别 legacy 老代码用）
#     v2: @Provider/@Consumer（生成范本统一用 v2，但扫描需兼容两版）
STATE_KEYS=$(grep -hoE "@(Provide|Consume|Provider|Consumer|StorageLink|StorageProp)\(['\"][a-zA-Z_]+['\"]|AppStorage(V2)?\.(set|get|link|connect)Or?Default?\(['\"][a-zA-Z_]+['\"]" "${H_TARGETS[@]}" 2>/dev/null \
             | grep -oE "['\"][a-zA-Z_]+['\"]" | tr -d "'\"" | sort -u)
for key in $STATE_KEYS; do
  echo "=== state-key $key ==="
  grep -rln "$key" $HMOS/spec/baseline/ 2>/dev/null
done | tee -a /tmp/regression_files.txt

# (g) 路由层耦合：扫 pushPath / pushUrl 目标，反查目标页面所在 baseline
ROUTE_TARGETS=$(grep -hoE "pushPath(ByName)?\(['\"][a-zA-Z_]+['\"]|pushUrl\(\{\s*url:\s*['\"][a-zA-Z_/]+['\"]" "${H_TARGETS[@]}" 2>/dev/null \
                | grep -oE "['\"][a-zA-Z_/]+['\"]" | tr -d "'\"" | sort -u)
for r in $ROUTE_TARGETS; do
  echo "=== route $r ==="
  grep -rln "$r" $HMOS/spec/baseline/ui/ 2>/dev/null
done | tee -a /tmp/regression_files.txt

# 重新去重 + 提取 AC ID（合并 (a)-(g) 全部命中）
sort -u /tmp/regression_files.txt | xargs -I{} grep -HnoE "AC[0-9]+|F[0-9]{3}-AC[0-9]+|P[0-9]{4}-UI-(SMOKE|COMP|NAV|INTERACT)[-_a-zA-Z0-9]*" {} | sort -u
```

## 3. 输出格式（写入 increment spec 的 `## 回归范围` 栏目）

```markdown
## 回归范围

> 本节由 a2h-incremental-migration §M3.2.5 自动派生，evolver Verify 阶段消费。
> 派生时间：YYYY-MM-DD HH:mm
> 派生命中数：feature_acs={N}, page_acs={M}, baseline_screenshots={K}

### feature_acs（受改动影响的 baseline 功能 AC）
- F006-AC1：示例 AC 描述（来源 `loadItemsList` 改动）

### page_acs（受改动影响的 baseline 页面级 AC）
- P0009-UI-SMOKE_works_tab_renders
- P0009-UI-INTERACT_tab_switch

### shared_files / shared_symbols（派生根因）
- `entry/src/main/ets/pages/MainPage.ets` (struct: ItemsView, ItemBuilder)
- `entry/src/main/ets/viewmodels/ItemsViewModel.ets` (method: loadItemsList, deleteSelected)

### affected_visual_pages（受影响的页面 + 对照入口，affects 含 ui 时必填）
- page_id: page_0009
  state_label: works_my_create_with_local_upload
  hmos_entry_path: 冷启 → 底 Tab "我的作品" → 默认在"我创建的"
  android_reference: ItemsFragment, tab=TAB_TYPE_MY_CREATE
  android_entry_path: 冷启 → 底 Tab "我的作品"

### rationale
F-xxx 改动 `ItemBuilder` 的渲染分支和 `loadItemsList` 的数据源，所有走该 Builder 渲染或读 `loadItemsList` 输出的 baseline AC 都需在 Verify 阶段回归。
```

**affected_visual_pages 说明**：
- 视觉验证不做"改代码前 baseline 截图"，以**同期 Android 应用**为真值
- 字段：`page_id` / `hmos_entry_path` / `android_reference` / `android_entry_path` / `state_label`
- 清单 = 新增功能涉及状态 + page_acs 涉及的所有状态

## 4. dt-verifier baseline AC 索引（首次跑前置）

dt-verifier 需要 `entry/src/ohosTest/ets/test/tdd-ac-index.md` 才能做"GREEN 不退化"判断。

若不存在 → 提示用户先跑一次 `arkts-dt-verifier` 落 baseline AC 索引（**仅首次需要**）。

## 5. 爆炸阈值（硬性闸门，避免基础设施改动炸穿）

```
TOTAL_REGRESSION_AC = len(feature_acs) + len(page_acs)

IF TOTAL_REGRESSION_AC > 10:
  停下，向用户出示三选一：

  ⚠ 回归范围爆炸：{N} 条 baseline AC (>10 阈值)
    根因：{shared_files / shared_symbols 列表}
    
    可能原因：
      - 触碰基础设施层（PreferenceHelper / EventBus / 全局 store）
      - H_TARGETS 选错了
      - baseline AC 颗粒度过细
    
    (a) 确认全量回归（接受 {N} 条成本）
    (b) 缩小改动范围（拆分本次差异为多个 spec）
    (c) 显式 opt-out（标 explosion=true + opt_out_reason，只回归手挑关键 N 条）
```

**用户回复 (a/b/c) 前禁止进入 §S3 evolver 委托**。

### opt-out 时 spec 栏目格式

```markdown
## 回归范围

> ⚠️ explosion=true（派生命中 {N} > 10）
> opt_out_reason: PreferenceHelper API 改造，所有读写偏好的功能理论上都受影响
> opt_out_approved_by: user @ YYYY-MM-DD

### feature_acs（手挑关键路径，非穷举）
- F002-AC1：登录 token 持久化（PreferenceHelper 写）
- F005-AC2：会员状态读取（PreferenceHelper 读）

### 全量派生结果（仅供审计，不参与回归）
- 共 {N} 条命中，详见 /tmp/regression_files.txt
```

## 6. LLM 语义补全（grep 之后必跑，零人工兜底盲区）

grep 派生 (a)-(g) 的结果是"机器看到的代码耦合"。仍可能漏：

- **业务语言 vs 技术语言**：baseline 用中文（"首页输入框默认主题"），grep 不命中 `MainPage.ets`
- **命名漂移**：代码已改名 baseline 未同步
- **隐性依赖**：方法间接调用链超 1 层

跑完 (a)-(g) 后必须执行 LLM 二次扫描：

```
LLM 输入：
  1. grep 派生结果（当前 regression_scope 候选 AC）
  2. baseline AC 全集（仅描述文本，不读源码）— 从 baseline/features/*.md + baseline/ui/*.md 提取
  3. 改动文件 diff（H_TARGETS 修改前后）
  4. spec/features/regression-miss-patterns.md（漏报模式知识库）

LLM 任务：
  「现有 baseline AC 里，有没有读起来会被这次改动影响、但 grep 没命中的？
   参考漏报模式知识库的同类漏报。保守扩大：宁可错拉，不能漏。」

LLM 输出：补充 AC 列表（直接合并进 regression_scope）
```

合并后再跑一次爆炸阈值检查。LLM 加的 AC 必须在 `## 回归范围 → rationale` 标注"由 LLM 语义扫描补充"。

## 7. 漏报模式知识库（自动维护，越用越准）

**文件**：`spec/features/regression-miss-patterns.md`

| 时机 | 动作 |
|------|------|
| 首次创建 | 项目首次启动时 evolver create 阶段自动创建空文件（含表头模板）|
| 写入时机 | evolver Verify Step 11a 采样回归抓到漏报时自动追加 |
| 读取时机 | 本节 §6 LLM 语义补全每次必读 |

**格式**：

```markdown
## 已知漏报模式

### 模式 #N（来源 spec id，发现于 YYYY-MM-DD）
- 改动特征：触碰 {file/struct/method}
- 漏报 AC：{ac_id} ({描述})
- 漏报根因：{方法间接调用 / 事件订阅 / 状态共享 / 业务语言 / 命名漂移 / ...}
- 调用链 / 依赖路径：{a → b → c}
- 后续派生提示：改 {特征} 时，连带把 {AC 域} 纳入回归
```

## 8. SR.3 取并集 R = A ∪ B（必跑）

evolver execute 完成、SR.2 产出清单 B 之后，立即合并：

```python
R = {
    "feature_acs": list(set(A["feature_acs"]) | set(B["feature_acs"])),
    "page_acs": list(set(A["page_acs"]) | set(B["page_acs"])),
    "shared_files": list(set(A["shared_files"]) | set(B["shared_files"])),
    "affected_visual_pages": A["affected_visual_pages"] + [
        p for p in B["affected_visual_pages"]
        if p["state_label"] not in [a["state_label"] for a in A["affected_visual_pages"]]
    ],
    "explosion": A["explosion"] or B["explosion"],
    "opt_out_reason": A.get("opt_out_reason") or B.get("opt_out_reason"),
    "derivation_provenance": {
        "A_count": len(A["feature_acs"]) + len(A["page_acs"]),
        "B_count": len(B["feature_acs"]) + len(B["page_acs"]),
        "only_in_A_count": <仅 A 抓到的>,
        "only_in_B_count": <仅 B 抓到的>,
        "intersection_count": <A∩B>,
    }
}
```

**写入 spec 的 `## 回归范围` 栏目**，用 R 覆盖原来只有 A 的版本。rationale 必须标注：
> "本次 SR.1 派生 A_count = X，SR.2 改后审查派生 B_count = Y，并集后 R_count = Z。only_in_B = N 条已追加到 `spec/features/regression-miss-patterns.md` 漏报模式 #M"

### 漏报反哺：only_in_B > 0 时的自动追加

若 SR.2 抓到 SR.1 没预见的 AC（only_in_B > 0），按下面格式追加到 `spec/features/regression-miss-patterns.md`：

```markdown
### 模式 #N（来源 {spec_id}，发现于 YYYY-MM-DD，由 SR.3 自动追加）
- 改动特征：{触碰的 file/struct/method}
- SR.1 派生时未识别的 AC：{only_in_B 列表}
- 漏报根因：{LLM 分析：方法间接调用 / 事件订阅 / 状态共享 / 业务语言 / 命名漂移 / ...}
- 修复指引：下次 SR.1 LLM 语义补全读到本模式时，应主动识别该类间接依赖
```

下次另一个 spec 跑 SR.1 时 LLM 必读此知识库，触发同类改动会主动识别——**机制越用越准**。

## 9. §S2 用户对齐时展示

§S2 差异清单的每条差异底下追加 `## 回归范围` 派生摘要，让用户在确认"差异是否要做"时同时看到"做这条差异需要回归多少 AC"——避免在 evolver Verify 阶段才被回归成本"惊吓"。

格式示例：
```
1. 🔴 作品页批量上传
   ...原有字段...
   📊 回归范围：feature_acs=3, page_acs=3, total=6（< 10 阈值，正常派生）
       关键 AC：F006-AC1/AC3/AC4 + P0009-UI-SMOKE/INTERACT_tab/INTERACT_manage
```
