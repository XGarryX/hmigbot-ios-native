> **iOS .33 采集与配对**：执行及 wire 规则以 [native-xcode-source](native-xcode-source.md) 为准。source baseline 使用公开 XCTest PNG/native JSON/原生 XML，经 source placement 落入本文件的 iOS canonical 目录；下方 adb/uiautomator 源端动作仅为历史分支。若缩图，PNG 与 XML bounds 同步变换，raw 原件/hash 保留在工作证据目录；不在 baseline 白名单中新增 raw JSON。

> **iOS 源输入**：读取 Swift/Objective-C、SwiftUI/UIKit、Xcode 工程及原生资源；实际源构建与设备观测依赖可用的源平台环境。鸿蒙侧构建和验收保持原流程。源侧操作详见 `a2h-spec/references/native-input.md`。

# 输出目录与文件路径规范（visual-verify 视角）

本文档是 visual-verify 在仓库内所有写盘行为的**唯一事实来源（SSOT）**。任何 skill / 脚本 / agent 读写下列路径必须遵守约定。其它消费者（a2h-spec / app-relationship-tree / visual-fixer / a2h-verify）按本文档约定读取。

> **变更纪律**：任何路径变更 / 新增产物 / 改变生命周期都要先改本文档，再改 SKILL.md，最后改脚本。文档没改而代码改了视为契约违反。

---

## 一、目录树（完整）

```
<repo_root>/
├── spec/
│   ├── ios-fact-index.json                ← toolkit-fact-indexer 产
│   ├── app-relationship-tree.json             ← app-relationship-tree 产
│   │
│   ├── baseline/                              ← a2h-spec 产
│   │   ├── ui-manifest.md
│   │   ├── feature-index.md
│   │   ├── ui/page_NNNN_*.md
│   │   └── features/F-xxx.md
│   │
│   ├── fix/                                   ★ 跨 round 永久保留（git 必跟踪）
│   │   ├── _state.yaml                        ← visual-verify 单写者（轮次字段归 round_budget.py）；调用方只读
│   │   ├── round-0/                           ← 首轮（baseline）
│   │   │   ├── _index.md
│   │   │   ├── _summary.md
│   │   │   ├── _delta.md                      ← round-0 不写，round-1+ 才写
│   │   │   ├── ui/
│   │   │   │   ├── ALIGN_P{page_id}_*.md
│   │   │   │   ├── URL_P{page_id}_*.md
│   │   │   │   ├── CRASH_P{page_id}_*.md
│   │   │   │   └── _systemic/
│   │   │   │       └── SYSTEMIC_*.md
│   │   │   └── feat/                          ← dt-verifier 写，visual-verify 不动
│   │   │       ├── F{id}_AC{n}_*.md
│   │   │       └── _systemic/
│   │   ├── round-1/                           ← 同上结构
│   │   └── round-N/
│   │
│   ├── scenarios/
│   │   └── artifacts/<ts>_<scenario>/         ← scenario-runner 产
│   │       └── result.json
│   │
│   ├── visual-verify/                         ★ visual-verify 私有空间
│   │   ├── progress.json                      ← 内部状态机（断点续跑）
│   │   ├── report.md                          ← 人类可读总览
│   │   ├── page_scenarios.json                ← 用户维护：页面 → scenario 映射
│   │   │
│   │   ├── screenshots/                       ← 单 run 临时工作目录（可 .gitignore）
│   │   │   ├── ios/
│   │   │   │   ├── {page_id}.png              ← 主截图（single 模式）
│   │   │   │   ├── {page_id}_long.png         ← 长图拼接（long 模式）
│   │   │   │   ├── {page_id}_long.json        ← 拼接 metadata
│   │   │   │   └── {page_id}_seg_*.png        ← 长图段图（Phase 6 清理）
│   │   │   ├── harmony/
│   │   │   │   ├── {page_id}.jpeg
│   │   │   │   └── {page_id}_long.png         ← (HMOS long 模式产物，扩展名沿用 png 兼容拼接脚本)
│   │   │   ├── sbs/                           ← side-by-side 合成图
│   │   │   │   └── {page_id}.jpeg
│   │   │   └── blocks/                        ← long 模式按锚点切块
│   │   │       └── {page_id}_block_NN_sbs.png
│   │   │
│   │   └── cache/                             ★ 跨 round 持久数据（应 .gitignore）
│   │       └── dismissals.json                ← 启动弹窗速关坐标表（iOS + HMOS 共用）
│   │
│   └── .cache/                                ★ 其它 skill 的中间产物（应 .gitignore）
│       └── fact-index/                        ← toolkit-fact-indexer 中间
│           ├── draft.json
│           └── source-index.json
│
├── docs/
│   └── autofix-log/round-N/                   ★ visual-fixer 产，git 必跟踪
│       ├── batch.md
│       ├── fixer-summary.md
│       └── rollback.md
│
└── 设备端（不在仓库内，仅过渡用）
    ├── /sdcard/vv_*.png                       ← iOS 源端截图临时文件
    └── /data/local/tmp/vv_*.jpeg              ← HarmonyOS 端截图临时文件
```

---

## 二、每个文件的完整规约表

### A. 对外契约（跨 skill 接口，schema-versioned）

| 路径 | 产出者 | 消费者 | 生命周期 | 清理时机 | git |
|---|---|---|---|---|---|
| `spec/ios-fact-index.json` | toolkit-fact-indexer | a2h-spec / app-relationship-tree | 持久，仅在 toolkit 重跑时刷新 | 手动 `rm`（toolkit 重跑会覆盖） | ✅ 必跟踪 |
| `spec/app-relationship-tree.json` | app-relationship-tree skill | visual-verify Phase 1.2 | 持久 | 手动；该 skill 重跑覆盖 | ✅ 必跟踪 |
| `spec/baseline/ui/page_NNNN_*.md` | a2h-spec | visual-verify, app-relationship-tree | 持久 | a2h-spec 重跑覆盖 | ✅ 必跟踪 |
| `spec/fix/round-N/ui/*.md` | visual-verify Step 4.4 | visual-fixer, a2h-verify | 永久，**只增不删** | **从不**删除（schema 铁律） | ✅ 必跟踪 |
| `spec/fix/round-N/ui/_systemic/SYSTEMIC_*.md` | visual-verify Phase 6 聚合 | visual-fixer | 同上 | **从不**删除 | ✅ 必跟踪 |
| `spec/fix/round-N/_index.md` `_summary.md` `_delta.md` `_run_state.json` | visual-verify Phase 6 / 6.4 整轮闸 | humans, a2h-verify | 永久，每轮新写 | **从不**删除 | ✅ 必跟踪 |
| `spec/fix/_state.yaml` | **visual-verify 单写者**（Phase 6.4 + `round_budget.py`；调用方含 a2h-verify 只读） | 所有 verifier 检查 schema_version | 持久 | 手动；版本升级时迁移 | ✅ 必跟踪 |
| `spec/scenarios/artifacts/<ts>_<scenario>/result.json` | scenario-runner | visual-verify Step 4.-1, CRASH_*.md evidence | 持久（debug 用） | scenario-runner 自管（可加 TTL） | ✅ 必跟踪（CRASH 引用） |
| `spec/visual-verify/page_scenarios.json` | **用户手写** | visual-verify Step 4.-1 | 持久 | 用户手动维护 | ✅ 必跟踪 |
| `docs/autofix-log/round-N/*.md` | visual-fixer | a2h-verify, humans | 永久 | **从不**删除 | ✅ 必跟踪 |

### B. visual-verify 私有持久产物

| 路径 | 产出者 | 消费者 | 生命周期 | 清理时机 | git |
|---|---|---|---|---|---|
| `spec/visual-verify/progress.json` | visual-verify 每页 Step 4.5 + Phase 6 | 本 skill 下次启动断点续跑 | 持久，跨 run 复用 | 进入新全局 round 时部分字段重置（如 queue_remaining，不论轮次由谁触发）；不删 | ⚠️ 建议跟踪（断点续跑要用） |
| `spec/visual-verify/page_queue.json` | `build_page_queue.py` | sub-agent 派发前；python 一行式切片 | 每次 visual-verify run 重生 | 自动覆盖 | ❌ 可 gitignore（重生 5s） |
| `spec/visual-verify/batches.json` | `build_batches.py` | 主会话调度循环；sub-agent prompt 填充 | 同上 | 同上 | ❌ 同上 |
| `spec/visual-verify/orphan_dialogs.md` | `build_orphan_dialogs_doc.py` | 人工调研触发条件 + 补 page_scenarios.json | 每次脚本跑覆盖**孤儿表格**部分；**保留**「调研记录」「人工豁免」段 | 工具不删人工段 | ⚠️ 建议跟踪（含调研笔记） |

### B.1 page_queue.json / batches.json entry 字段

iOS .45 在队列或批次同目录保存 `<输出文件名>.native-mapping.json` 静态定位旁路凭据。它区分原解析与规格合同探测，记录 Source、规格、完整 ETS 集、工具指纹及原 core 返回；主 JSON 的身份、顺序、分母、分组与门禁不变，只补已核实的定位字段。凭据随队列或批次重建；Source、规格或目标文件结构变化须从该准备断点重建，不代表运行期路由或设备通过。

`page_queue.json.entries[]` / `batches.json.trips[].batches[].pages[]` (v4-batches/1; legacy flat: `batches.json.batches[].pages[]`) 中每个 page 条目包含：

| 字段 | 说明 | 例 |
|---|---|---|
| `name` | tree.pages/fragments/dialogs[].name | `"AboutUsActivity"` |
| `kind` | `page` / `fragment` / `dialog` | `"page"` |
| `priority` | P0 / P1 / P2 | `"P2"` |
| `feature_ids` | 所属功能域 | `["F003"]` |
| `layer` | dependency_graph.layers 派生 | `"Foundation"` |
| `file` / `file_resolved` | resolver 找到的真实 HMOS ets 路径；null = page_missing_hmos 候选 | `"features/business_settings/.../AboutUsPage.ets"` |
| `file_candidates` | basename 多命中时全列出（让 fixer 选） | `["...A.ets","...B.ets"]` |
| `host_page` | fragment 寄生的 page name（tree 给的或推断的） | `"HomeActivity"` |
| `triggered_by` | dialog 由哪些 page 触发 | `["MinePage"]` |
| `parent_file_resolved` | host_page / triggered_by[0] 解出的真实 ets，用于嵌入式 dialog/fragment 修复时定位 | `"products/phone/.../SplashPage.ets"` |
| `parent_used` | 解析时用的是哪个 parent name | `"SplashActivity"` |
| `reach_path` | compute_reach_paths.py 产，导航 token 序列 | `["HomeActivity","tap","MineFragment","tap","AboutUsActivity"]` |

批次额外字段：`page_id` / `reachability`（以实际原 core 输出为准）。

批次按 `page_id`（旧形态按 `name`）连接队列。各趟保留自己的成员与顺序；`android_file` 是原源字段，不写入目标 ETS。只有已核实的 `file_resolved`、`parent_file_resolved`、`parent_used`、`file_candidates` 作为目标代码定位提示，不能代替到达、路由或行为证据。旁路凭据按趟记录匹配、未匹配和定位字段修改数。
| `spec/visual-verify/report.md` | Phase 6.6 | humans | 每次 run 整体覆盖 | 自动覆盖；旧版不保留 | ⚠️ 可跟踪（人类速查用） |

### C. 单 run 临时（screenshots/）

> 整个 `spec/visual-verify/screenshots/` **建议加 .gitignore**——这些是过渡产物，每次 run 重新生成。

#### C.0 目录结构

```
spec/visual-verify/screenshots/
├── ios/   ← {page_id}.png       iOS 源端单页（resize ≤1800px）
├── harmony/   ← {page_id}.jpeg      HMOS 端单页
├── sbs/       ← {page_id}.jpeg      compose_side_by_side 合成图
└── blocks/    ← {page_id}_block_NN.png  仅长页 Step 4.1.3-d
```

- 跨轮跑同 page → 直接覆盖旧文件；markdown `evidence:` 引用稳定路径，内容跟着变
- 不准创建其它子目录（`*_round*` / `*_final` / `fragments/` / `dialogs/` 等都不行）
- 文件名不准加后缀（`_round6` / `_post` / `_logged` 等），多状态用独立 page_id

#### C.1 文件清单

| 路径 | 产出者 | 消费者 | 生命周期 | 清理时机 |
|---|---|---|---|---|
> **路径骨架**：`{trip_id}` ∈ {`trip_1_logged_out`, `trip_2_logged_in_vip`}。双态页（如 HomePage）在两态 UI 完全不同，必须 trip 分目录避免互覆盖。

> **screenshots/ios/{trip_id}/ 目录白名单（HARD-GATE，防目录污染）**：本目录**只准**放下列文件名模式，
> 每个 page_id **最多一份配对 dump**（`{page_id}.ios.xml`，供 HMOS 结构 diff / 功能 grounding 复用）：
> `{page_id}.png` / `{page_id}.ios.xml` / `{page_id}_long.png` / `{page_id}_long.json` / `{page_id}_seg_*.png`。
> **禁止**：① `{page_id}.png.xml`（路径拼接 bug——dump 后缀应替换 .png 为 .ios.xml，不是追加 .xml）；
> ② 业务语义命名的中间态 dump（如 `login_page.ios.xml` / `member_center_coldstart.ios.xml`
> / `works_tab_populated.ios.xml`）——这些是 **Phase 2.5 grounding 导航/实操途中的现场证据**，
> **归 `spec/visual-verify/phase2_batches/{chunk_id}/grounding_dumps/`**（随 chunk manifest 生命周期），
> 绝不堆进正式截图目录（污染目录、混淆"目标页最终产物"与"过程证据"）。
> 违反 = sub-agent 落盘规约不合规，主会话 Phase 6 应清理并回填正确位置。

> **★回放产物同受本布局约束（2026-07-25 新增铁律）**：`visual-verify/replay/<run>/` 是**工作区**，
> 不是交付位。跑完 `replay_exec.py` **必须**跑 `replay_place_artifacts.py` 摆进 canonical 布局，
> 再跑 `assert_replay_artifacts.py` 验齐，才允许进判定。
> 反面教训（实测一整轮）：回放自建了一套目录约定，canonical `screenshots/harmony/round-1/` 里
> 躺的还是上一次页粒度采集的 4 张陈图，而本轮 60 张真货只住在回放私有目录；`screenshots/sbs/`
> 近乎空目录，judge 出单时**在 markdown 里把 evidence 路径改指回放目录绕了过去**。
> **下游一绕，缺陷就静默存活** —— 这正是"没有机械闸的规约等于没有规约"。
> canonical 布局是 visual-fixer / a2h-verify / Phase 6 自检**共同认的接口**，谁自建约定谁出局。

| 路径 | 产出者 | 消费者 | 生命周期 | 清理时机 |
|---|---|---|---|---|
| `screenshots/ios/{trip_id}/{page_id}.png` | Phase 2 产 baseline（Step 4.1 缺失才补截：XCTest capture + source placement） | Step 4.2 多模态 | 跨轮复用（iOS frozen） | run 结束**保留** |
| `screenshots/ios/{trip_id}/{page_id}.ios.xml` | Step 4.1 同次 XCTest snapshot + 原生 XML 桥接（**配对，每页至多一份**） | HMOS 结构 diff + Phase 2.5 功能 grounding | 同 png | 同 png |
| `phase2_batches/{chunk_id}/grounding_dumps/{语义名}.ios.xml` | Phase 2.5 grounding 导航/实操途中留证 | grounding 现场追溯 | 随 chunk manifest | chunk 归档时一并留/清 |
| `screenshots/harmony/round-{N}/{trip_id}/{page_id}.jpeg` | Step 4.1 (hdc + resize)　**或**　回放 `replay_place_artifacts.py` | Step 4.2 多模态 | 每轮独立 | 永久按轮归档 |
| `screenshots/harmony/round-{N}/{trip_id}/{page_id}.hmos.json` | 同上（**与 jpeg 配对，缺一即闸红**） | 三分归因（判缺控件/没定位到/handler 空实现） | 同 jpeg | 同 jpeg |
| `screenshots/harmony/round-{N}/{trip_id}/_evidence/*` | 回放执行器 `_shot()` 的旁路截图+dump（`__el*` / `__weak` / `__probe*` / `__notfound` / `step*`） | judge 归因复核 | 每轮独立 | 随本轮 |
| `screenshots/harmony/round-{N}/{trip_id}/_placement.json` | `replay_place_artifacts.py` | 落位与覆盖对账追溯 | 每轮独立 | 随本轮 |
| `screenshots/sbs/round-{N}/{trip_id}/{page_id}.jpeg` | Step 4.2 `compose_side_by_side.py`　**或**　回放 `build_judge_input.py` | Step 4.2 多模态 + markdown evidence | 每轮独立 | 被 markdown 的 `evidence:` 引用就**必须**留 |
| `visual-verify/replay/<run>/{shots,dumps,run.jsonl,capture_manifest.json}` | `replay_exec.py` | **工作区，不是交付位** | 单次运行 | 落位后可留作追溯 |
| `screenshots/ios/{trip_id}/{page_id}_long.png` | Step 4.1.3 拼接 (已存在即复用，缺失才 stitch) | Step 4.2 多模态 | 同 ios | 同上 |
| `screenshots/ios/{trip_id}/{page_id}_long.json` | 同上 | 调试 / 重拼接 | 同上 | 同上 |
| `screenshots/ios/{trip_id}/{page_id}_seg_*.png` | Step 4.1.3-b 分段截图 | 仅 Step 4.1.3-c 拼接用 | 单次拼接过程 | **Phase 6.5 自检后立即删** |
| `screenshots/harmony/round-{N}/{trip_id}/{page_id}_long.png` | Step 4.1.3 拼接（HMOS 端） | Step 4.2 多模态 | 每轮独立 | 同 ios long |
| `screenshots/sbs/round-{N}/{trip_id}/blocks/{page_id}_block_NN_sbs.png` | Step 4.1.3-d 锚点切块 | Step 4.2 多模态分块对比 | 每轮独立 | 同上 |

### D. 设备端临时文件（不在仓库）

| 路径 | 产出者 | 生命周期 | 清理时机 |
|---|---|---|---|
| iOS `/sdcard/vv_{page_id}.png` | `screencap` | 秒级 | `adb pull` 完成后**立即** `adb shell rm`（每条 capture 命令最后一行） |
| HMOS `/data/local/tmp/vv_{page_id}.jpeg` | `snapshot_display` | 秒级 | `hdc file recv` 完成后**立即** `hdc shell rm` |
| iOS `/sdcard/ui.xml`（dumpLayout 副产） | `uiautomator dump` | 秒级 | pull 完立即删 |

**铁律**：脚本崩溃也不能留设备端垃圾——所有 capture 命令必须保证清理（`capture_or_reuse.py` / `capture_page_e2e.py` 内部已用 try/finally 兜住；手工敲时依次跑 screencap → pull → rm，pull 失败就不删）：
```text
# 原源平台历史命令（iOS 按本文件适配说明执行）: adb shell screencap ...      # 1) 截
# 原源平台历史命令（iOS 按本文件适配说明执行）: adb pull ...                 # 2) 拉（失败则停在这，别删）
# 原源平台历史命令（iOS 按本文件适配说明执行）: adb shell rm ...             # 3) 删设备端临时文件
# bash 里可 `&&` 串联 / `trap ... EXIT` 兜底；PowerShell 语法不同（见 windows-setup.md），最稳是走 py 脚本
```

---

## 三、`.gitignore` 推荐

```gitignore
# visual-verify 临时与缓存
spec/visual-verify/screenshots/
spec/visual-verify/cache/

# 其它 skill 的中间产物
spec/.cache/

# 设备/构建产物
*.png.bak
*.jpeg.bak
```

**绝对不要 gitignore 的目录**（这些是契约产物）：
- `spec/fix/`
- `spec/baseline/`
- `spec/scenarios/artifacts/`（CRASH markdown evidence 引用）
- `docs/autofix-log/`
- `spec/ios-fact-index.json` `spec/app-relationship-tree.json`

---

## 四、清理时机汇总

| 时机 | 该清的 | 该留的 |
|---|---|---|
| **每页 Step 4.1 结束** | 设备端 `/sdcard/vv_*` `/data/local/tmp/vv_*.jpeg` | screenshots/ 工作副本 |
| **每页 Step 4.1.3 拼接结束** | `_seg_*.png` 段图 | `_long.png` `_long.json` `_block_NN_sbs.png` |
| **Phase 6 收尾** | 仅清确认未被任何 markdown evidence 引用的过期 sbs | 所有被 round-N/ui/*.md 的 `evidence:` 引用的文件 |
| **进入下一全局 round**（round_budget.py 自增后，不论调用方是谁） | progress.json.queue_remaining 重置 | progress.json 其它字段、所有历史 round-N/ |
| **用户说"重截 iOS"** | 整个 `screenshots/ios/`（`--invalidate-ios-cache`） | 不动其它 |
| **toolkit 重跑** | `spec/.cache/fact-index/` 旧的 draft.json | 用户保留的 fact-index.json（覆盖前提示 diff） |
| **从不应主动删** | `spec/fix/round-*/` 任何文件 / `docs/autofix-log/` / `_state.yaml` |  |

---

## 五、跨 skill 接口路径（**严格按此路径读写**）

按"谁产 → 谁读"列出契约：

```
toolkit-fact-indexer
    ├─→ 产: spec/ios-fact-index.json
    │       spec/.cache/fact-index/draft.json (中间)
    │       spec/.cache/fact-index/source-index.json (中间)
    │
    └─→ 被读: app-relationship-tree (Phase 1 探测组 D)
              a2h-spec (Phase 2.5 探测)

app-relationship-tree
    ├─→ 读: spec/ios-fact-index.json (若存在，组 D)
    │      spec/baseline/ui/page_*.md (组 A)
    │      Screen/Component/Navigation/Containment.json (组 B)
    │      entry/src/main/ets/ (组 C)
    │
    └─→ 产: spec/app-relationship-tree.json

visual-verify
    ├─→ 读: spec/app-relationship-tree.json
    │      spec/visual-verify/page_scenarios.json
    │      spec/fix/_state.yaml (拿 current_round)
    │      spec/fix/round-(N-1)/ui/*.md (carry forward disposition)
    │      spec/scenarios/artifacts/.../result.json
    │
    ├─→ 产: spec/fix/round-N/ui/*.md
    │      spec/fix/round-N/_index.md _summary.md _delta.md
    │      spec/fix/_state.yaml (更新 last_verifier_results.visual-verify)
    │      spec/visual-verify/progress.json
    │      spec/visual-verify/report.md
    │      spec/visual-verify/screenshots/...
    │
    └─→ 被读: a2h-verify (读 round-N/_summary.md 决定下一步)
              visual-fixer (读 round-N/ui/*.md 改代码)

visual-fixer (离线 agent)
    ├─→ 读: spec/fix/round-N/ui/*.md
    │      spec/app-relationship-tree.json (定位 ets 文件)
    │      spec/ios-fact-index.json (拿 purpose / source_anchor 参考)
    │
    └─→ 产: 修改 entry/src/main/ets/*.ets (改代码)
            docs/autofix-log/round-N/{batch,fixer-summary,rollback}.md

a2h-verify (上游调用方之一，非编排器)
    ├─→ 读: spec/fix/round-N/_summary.md + VERDICT (映射成 CHECK-6 结论)
    │      spec/fix/_state.yaml.current_round (只读，定位 round-N/ 目录)
    │
    └─→ 产: 无（_state.yaml 轮次字段由 visual-verify 的 round_budget.py 单写；
            需要再跑时直接再调一次 visual-verify，差值预算天然累计）
```

---

## 六、命名规则速查

| 元素 | 模板 | 例 |
|---|---|---|
| page_id | 与 fact-index / app-relationship-tree 中的 `id` 一致 | `P0010` 或 `MainActivity` |
| fix-markdown id | 见 [`fix-file-schema.md`](fix-file-schema.md) §二 | `ALIGN_P0010_color_mismatch_titlebar-bg` |
| screenshot 主文件 | `{page_id}.png` (ios) / `{page_id}.jpeg` (harmony) | `MainActivity.png` |
| 长图段图 | `{page_id}_seg_NN.png`（NN 从 00 起） | `MainActivity_seg_03.png` |
| 长图拼接图 | `{page_id}_long.png` + `{page_id}_long.json` | 同上 |
| sbs 合成 | `{page_id}.jpeg`（放在 `sbs/` 下） | `MainActivity.jpeg` |
| 块 sbs | `{page_id}_block_NN_sbs.png`（NN 从 00） | `MainActivity_block_02_sbs.png` |
| scenario 工件目录 | `<ISO8601_ts>_<scenario_name>/` | `20260509T152311Z_login/` |

---

## 七、变更日志

| 版本 | 日期 | 变更 |
|---|---|---|
| 1.0 | 2026-05-09 | 首版。覆盖 v2 缓存策略 + fix-markdown schema + 跨 skill 接口路径 |
