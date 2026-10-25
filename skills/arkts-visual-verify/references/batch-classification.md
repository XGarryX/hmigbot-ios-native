> **iOS 源输入**：读取 Swift/Objective-C、SwiftUI/UIKit、Xcode 工程及原生资源；实际源构建与设备观测依赖可用的源平台环境。鸿蒙侧构建和验收保持原流程。源侧操作详见 `a2h-spec/references/native-input.md`。

# batch-classification — `page_queue → batches.json` 分类规则

> 主 SKILL.md Phase 3.5 引用本文件。`scripts/build_batches.py` 实现下面的全部规则；本文件是规则的人类可读版本（同时是脚本的设计文档）。

---

## 1. 设计目标

把 `spec/visual-verify/page_queue.json` 里的 N 条目（典型 30-80 条，含 page / fragment / dialog）切成 **7-9 个 batch**，每个 batch：

- 内部页面**类型相近**（命名、模块路径、功能域）
- **共享 scenario_chain**（同一个 login 状态 / 同一份 mock 数据）
- **总规模 5-10 条**（太大 sub-agent 上下文吃紧，太小调度成本不摊薄）
- **可独立 reset**（precondition / postcondition 明确，主会话能在 batch 间清干净）

dialogs / fragments 视具体能否触发：能 trigger 的归入对应业务 batch；无法 trigger 的统一进 `dialogs_overlays` 走 fast_path。

---

## 2. 分类匹配规则（按优先级，从上到下首次命中即固定）

| # | batch_id | 命中条件（任一 OR 命中） | scenario_chain | precondition | postcondition | fast_path |
|---|---|---|---|---|---|---|
| 1 | `auth_account` | `name ~= /(Login|Account|Auth|Bind|Phone|Verify|SMS)/i` 且不在 PPT/支付/会员模块 | `[]` | `data_cleared` | `logged_out` | false |
| 2 | `shell_launch` | `name ~= /(Splash|Guide|Launch|Welcome|Onboard|Agreement|Privacy)/i` 或 kind=dialog 且 name 含 `(Launch|Agreement|Permission)` | `[]` | `data_cleared` | `cold_started` | false |
| 3 | `home_main_tab` | `name ~= /^Home|^Main|FragmentHome|FragmentRecommend|FragmentTab|HomeTab|FragmentExample/i` 且不在 mine/payment | `[login]` | `logged_in_clean` | `logged_in_clean` | false |
| 4 | `mine_settings` | path 含 `business_mine` / `business_settings` 或 `name ~= /^Mine|Setting|About|Privacy|Policy|Feedback/i` | `[login]` | `logged_in_clean` | `logged_in_clean` | false |
| 5 | `ppt_create_flow` | path 含 `business_create` / `business_template` / `business_file` 或 `name ~= /(PPT|Outline|CreateOut|Template|FileUpload|FileList)/i` | `[login]`，必要时附 `upload_image` | `logged_in_clean` | `logged_in_clean` | false |
| 6 | `works_output` | path 含 `business_home/.*Works` 或 `name ~= /(Works|Video|Landscape|Player|Preview|Result)/i` | `[login, mock_works]` | `logged_in_clean` | `logged_in_clean` | false |
| 7 | `payment_member` | path 含 `business_payment` 或 `name ~= /(Member|Vip|Renew|Refund|SaleCenter|Pay|Subscribe|Iap)/i` | `[login, mock_member]` | `logged_in_clean` | `logged_in_clean` | false |
| 8 | `web_pages` | path 含 `business_webview` 或 `name ~= /(WebView|Web$|CustomerServiceWeb|H5)/i` | `[login]`（视 url） | `logged_in_clean` | `logged_in_clean` | false |
| 9 | `dialogs_overlays` | kind=dialog 且未被前述命中；或前述命中后被本规则后追加（dialog 触发链路不明） | 无 | `any` | `any` | **true** |
| 10 | `_misc` | 剩余无法归类的 page | `[login]` | `logged_in_clean` | `logged_in_clean` | false |

> **优先级解释**：例如 `BaseMemberCenterDialogFragment` 是 dialog，但因匹配 `MemberCenter` 关键字先归入 `payment_member`（规则 7），不会落到 `dialogs_overlays`。这是有意的——能 trigger 的 dialog 跟着主页面一起跑。

---

## 3. 规模约束（脚本必须执行）

> ⚠️ **抄iOS分批时本节整体不适用（2026-07-25）**：`build_batches.py` 检测到iOS Phase 2
> `phase2_batches/*/manifest.json` 时，**trip 归属与分批一起抄iOS**（batch 带 `ios_chunk_id`
> 可追溯，trip 带 `batching_source: ios_chunk_manifest`）。此时 batch 数量与大小**由iOS决定**，
> 本节的 7-9 个 batch / 上限 10 / 下限 3 合并 **全部不生效**，实测会出现 2-4 个 batch、单 batch 3 页
> 的情况——这是**预期**，不是要"修"的偏差。取舍：放弃鸿蒙侧自主规模控制，换取与iOS逐组一一对应
> （分组反映真实导航代价与顺序，重推 BFS 会切出不同组合）。
> 本节仅在**无iOS产物的兜底路径**（纯鸿蒙项目 / 未跑 Phase 2）生效。

每个 batch 最终 pages 数量必须满足：

| batch_id | 上限 | 触发拆分 |
|---|---|---|
| 业务类 batch | 10 | 超 10 时按 priority + page_id 字母序拆 `_a` / `_b`（如 `ppt_create_flow_a` / `ppt_create_flow_b`） |
| `dialogs_overlays` | 20 | 超 20 时按 dialog 命名首字母拆 `dialogs_overlays_a-l` / `dialogs_overlays_m-z` |
| `_misc` | 10 | 同业务类 |

下限：单 batch < 3 条时合并到最近的语义相邻 batch（合并表见下方）。

| 单条 batch | 合并目标 |
|---|---|
| 只剩 1 条 `web_pages` | 并入 `mine_settings` |
| 只剩 1 条 `works_output` | 并入 `home_main_tab` |
| `_misc` < 3 | 拆给最近 batch |

---

## 4. scenario_chain 推断细则

| 条件 | scenario_chain |
|---|---|
| 业务 batch 默认 | `[login]` |
| 涉及 upload/picker 类页面（FileUpload, PPTFile） | `[login, upload_image]` |
| 涉及 works/作品列表 | `[login, mock_works]` |
| 涉及会员/支付状态依赖 | `[login, mock_member]` |
| `auth_account` / `shell_launch` | `[]`（不能登录） |
| `dialogs_overlays` fast_path | `[]`（不跑 scenario） |

`mock_works` / `mock_member` 等 scenario 若 `spec/scenarios/` 下不存在，build_batches.py 写入 `scenario_chain` 时不删除，但额外标 `missing_scenarios: [mock_works]`，主会话 Phase 4 派发前提示用户先补 scenario yaml（或临时降级到 `[login]`）。

---

## 5. precondition / postcondition 状态机

主会话在 batch 间需要根据这两个字段判断是否插入 reset 步骤：

```
状态机：
  data_cleared    --(冷启动)-->  cold_started
  cold_started    --(scenario login)-->  logged_in_clean
  logged_in_clean --(scenario logout)-->  logged_out
  logged_out      --(bm clean -d)-->     data_cleared

如果 batch[i].precondition != batch[i-1].postcondition:
  执行对应 reset 命令
```

常见 reset 命令：

| 目标态 | HMOS 命令 | iOS 命令 |
|---|---|---|
| `data_cleared` | `hdc shell bm clean -d -n {bundle}` | `adb shell pm clear {package}` |
| `cold_started` | `hdc shell aa force-stop {bundle}` 再 `hdc shell aa start -a EntryAbility -b {bundle}`（两条依次跑）| `adb shell am force-stop {package}` 再 `adb shell am start -n {launcher}` |
| `logged_out` | scenario_run.py `--scenario logout` | 同左 |

---

## 6. dialogs_overlays fast_path 行为

`fast_path=true` 的 batch 里，sub-agent **不**尝试 scenario / 不导航 / 不截图，对每个 page 直接产 `CRASH(scenario_required_undefined)` markdown：

- 文件名：`CRASH_P{page_id}_scenario_required_undefined.md`
- `fixer_layer: feat`（scenario yaml 改动归 scenario-runner 层）
- `suggested_files: ["spec/visual-verify/page_scenarios.json"]`
- Section 5 修复建议指向：在 page_scenarios.json 声明 scenario / 在 spec/scenarios/ 新建 YAML / 评审是否豁免

manifest 中 fast_path batch 的 `pages_status[*].status` 全为 `blocked`，`scenario_results` 为空数组。

---

## 7. 错分容忍 + 主会话审批

build_batches.py 跑完后**主会话必须速览一遍**（python 一行式，跨平台）：

```text
python3 -c "import json;print(json.dumps([{'id':b['batch_id'],'n':len(b['pages']),'sc':b.get('scenario_chain'),'fp':b.get('fast_path')} for t in json.load(open('spec/visual-verify/batches.json'))['trips'] for b in t['batches']],ensure_ascii=False,indent=1))"
```

主会话发现错分（典型：登录页跑进 home_main_tab、详情页跑进 dialogs_overlays）后**必须手动改 batches.json 再进 Phase 4**，不接受默默错过。

如果有 ≥3 条错分 → 当成脚本规则缺陷，反馈给本文件补规则后重跑。

---

## 7.5 反哺节点归 parent 同 batch（2026-05-23 新加）

Phase 2 把 iOS 黑盒发现物反哺成 fact-tree `pages[]` 时，会产出 page_id 形如 `MoreActivity#via=证件扫描` 的虚拟 variant。这些 variant 必须跟 parent 同 batch、同 scenario_chain，否则 sub-agent 跑到 variant 时无法在干净的 batch 起点直接导航。

**分类规则**：

```
FOR page IN page_queue:
    IF page.name 含 "#via=":
        parent_id = page.name.split("#via=")[0]
        # 反哺节点跟 parent 归同一 batch
        target_batch = batch_that_contains(parent_id)
        IF target_batch:
            target_batch.pages.append(page)
            CONTINUE   # 跳过规则 1-10 的常规命中
        ELSE:
            # parent 没被任何 batch 接住（罕见，应当抛 warning）
            log_warn(f"variant {page.name} 的 parent {parent_id} 不在任何 batch，归入 _misc")
            assign_to("_misc")
            CONTINUE
    # 普通 page 走规则 1-10
```

**约束**：
- 反哺 variant 不算进单 batch 上限 10（容器型页一旦反哺 N 个 variant 就直接超 10，强拆会破坏 scenario_chain 共享）。改在 batch_id 后缀加 `_with_variants`，主会话 Phase 4 派发时按 fact-tree 顺序逐个走，超 60 分钟主代理可拆 sub-batch 重派
- variant 的 `priority` 继承 parent 的（fact-tree 反哺时已写好）
- variant 的 `reachability` 标 `via_parent`（区别于 public / login_walled）

**验证**：

```text
# 反哺节点应该都跟 parent 同 batch：对每个 name 含 "#via=" 的 variant，打印 (variant, parent, variant所在batch, parent所在batch)，
# 每行后两列应一致（python 一行式，跨平台）
python3 -c "import json;bs=[b for t in json.load(open('spec/visual-verify/batches.json'))['trips'] for b in t['batches']];loc=lambda n:[b['batch_id'] for b in bs if any(p['name']==n for p in b['pages'])];[print(v,par,loc(v),loc(par)) for b in bs for p in b['pages'] for v in [p['name']] if '#via=' in v for par in [v.split('#via=')[0]]]"
```

---

## 8. 与 progress.json 的关系

`progress.json` 的 `pages_meta.{name}.reachability` 字段是 build_batches.py 的额外输入（priority 之外的二级排序键）。同 batch 内：

1. 按 priority asc (P0 在前)
2. 按 reachability asc (public → login_walled → data_dependent)
3. 按 name 字母序

便于 sub-agent 内部 scenario chain 准备一次后从 public 页开始跑，需要更深状态时再追加。

---

## 9. 执行入口（Phase 3.5 主会话调用）

### 9.a 跑 build_batches.py

```text
python3 $SKILLS_ROOT/arkts-visual-verify/scripts/build_batches.py \
    --fact-tree spec/toolkit-fact-tree.json \
    --out       spec/visual-verify/batches.json \
    --hmos-project .            # 功能维度闸用；缺省=fact-tree 上两级目录
    # [--batch-size 8]          # 仅兜底路径生效（抄iOS时批大小由iOS chunk 决定）
```

> **入口不吃 page_queue.json**（2026-07-25 更正，此前文档写 `--queue/--progress` 是过期的，照抄必崩）：
> 数据源是 fact-tree + iOS Phase 2 产物。退出码：`0` OK / `2` fact-tree 缺字段 / `3` 写入失败 /
> `4` **不变式违反**（有入队页无iOS baseline=无 GT）/ `40|41|42|43|44` 三维度就绪闸未过（见 SKILL.md §4 Phase 3.5）。

### 9.b batches.json schema（**顶层是 `trips[]` 不是 `batches[]`** —— 2026-07-25 更正）

```jsonc
{
  "schema_version": "v4-batches/1",
  "generated_at": "2026-07-25T02:00:00Z",
  "generated_from": "/abs/path/spec/toolkit-fact-tree.json",
  "trips": [                                   // ★顶层按 trip 分组，batch 嵌在 trip 内
    {
      "trip_id": "trip_1_logged_out",
      "trip_label": "Trip 1: 未登录态",
      "scenario_chain": [],                    // trip 级，不是 batch 级
      "starting_page": "SplashActivity",
      "total_pages": 13, "total_batches": 2,
      "batching_source": "ios_chunk_manifest",  // 抄iOS时才有；兜底路径无此字段
      "batches": [
        {
          "batch_id": "trip_1_logged_out_batch_01",
          "ios_chunk_id": "phase2_trip_1_logged_out_chunk_01",  // 可追溯到iOS哪一批
          "starting_page": "SplashActivity",
          "page_count": 8,
          "pages": [
            {"page_id": "SplashActivity", "kind": "Activity",
             "verify_signal": "...", "preconditions": [], "purpose": "...",
             "ios_file": "...", "edges_to_test": [/* {to_page,trigger,verify_signal,...} */]}
          ]
        }
      ]
    }
  ],
  "stats": {"total_records": 70, "trip_1_pages": 13, "trip_2_pages": 18, "total_batches": 6}
}
```

**取 batch 清单的正确写法**（顶层 `.batches[]` 取不到，会报 `Cannot iterate over null`）：
```text
python3 -c "import json;print([b['batch_id'] for t in json.load(open('spec/visual-verify/batches.json'))['trips'] if t['trip_id']=='trip_1_logged_out' for b in t['batches']])"
python3 -c "import json;print(json.dumps([{'batch_id':b['batch_id'],'pages':len(b['pages']),'ios_chunk_id':b.get('ios_chunk_id')} for t in json.load(open('spec/visual-verify/batches.json'))['trips'] for b in t['batches']],ensure_ascii=False,indent=1))"
```

> `scenario_chain` 在 **trip 级**（同 trip 内所有 batch 共享建态）。历史文档写的 batch 级
> `precondition` / `postcondition` / `fast_path` / `expected_run_minutes` **当前脚本不产**，
> 消费方按存在性判断，勿假定必有。

### 9.c 主会话审批 batches.json

主会话速览 batches.json 概况（python 一行式）：

```text
python3 -c "import json;print(json.dumps([{'batch_id':b['batch_id'],'pages':len(b['pages']),'scenario_chain':b.get('scenario_chain'),'fast_path':b.get('fast_path')} for t in json.load(open('spec/visual-verify/batches.json'))['trips'] for b in t['batches']],ensure_ascii=False,indent=1))"
```

确认无明显错分（如 LoginActivity 跑进了 home_main_tab）后进入 Phase 4。错分时**手动改 batches.json 或重跑脚本**，不要默默接受。
