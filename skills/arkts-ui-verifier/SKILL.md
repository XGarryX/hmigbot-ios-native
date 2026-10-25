---
name: arkts-ui-verifier
description: 'ArkTS/HarmonyOS Spec 驱动的**UI 测试（UI 层）**验证工具。从页面 Spec + 功能 Spec 的 UI 验收

  标准 + 源码出发，三步流水线（测试设计 → 测试生成 → 执行）自动产出 arkxtest UI 测试，在真机/

  模拟器上跑出 UI 层实现率。


  **使用场景**：


  - "验证 UI 层实现率"、"从 spec 生成 UI 测试"、"UI TDD 验证"

  - "测量 UI 层覆盖/通过率"、"哪些页面/控件没实装"

  - "UI 层 RED/GREEN 报告"


  **不负责逻辑层**（业务逻辑 / Repository / Service unit 行为）—— 逻辑层验证用 `arkts-ut-verifier`。

  '
metadata:
  type: domain
  domain: migration
  tags:
  - verification
  - testing
  - tdd
  - coverage
  - hypium
  - arkxtest
  - uitest
  - 验证
  - 测试
  - UI测试
  - UI层
  - 实现率
---
# ArkTS Spec UI 测试（UI 层）验证工具

四步流水线（设计 → ID 注入 → 生成 → 执行）+ 一段 **fix-loop**（默认开），从页面 Spec + 功能 Spec 的 UI AC + 源码出发，生成 arkxtest UI 测试，跑出 UI 层实现率，并自动派 `spec-fixer-ui` 修 RED（同时满足"意图层 + 状态层"双重断言）直到全 GREEN 或达到上限。

> **框架**：arkxtest 的 `@kit.TestKit` Driver / ON / findComponent，编译进测试 HAP，随 `aa test` 在设备上跑（与单元测试同一套 hypium harness）。
>
> **只做 UI 层**：业务逻辑 unit 行为由 `arkts-ut-verifier` 负责，两者独立。
>
> **MODE 参数**：`verify_only` = 只跑四步出报告；`verify_fix`（默认）= 四步跑完后若有 RED 自动进 fix-loop。

## 执行模型

四步都派 Agent 执行（每个用 子代理派发、通用子代理、**原文读取**对应 prompt 文件传入；各 agent 需授予的工具与输入写在其文件「输入」区）。设计、ID 注入、生成按**页面 (Page)** **并发派多个 agent**，主线程负责分批、把住 barrier、串接产出。

| 步骤 | 做什么 | 并发？ | Agent prompt |
|------|--------|------|------|
| 第一步：测试用例设计 | 读页面 Spec + 功能 Spec + 源码，每页输出**两份**设计：测试设计 → `spec/test/ui-test/design/` + ID 注入设计 → `spec/test/ui-test/id-inject/` | ✅ 按 Page 分批并发 | `references/agent-prompts/step1-design-agent.md` |
| **第二步：ID 注入 + manifest** | **读 `ui-test/id-inject/P*.md` → 注入 `.id()` 到 `pages/components` 源码 → 产 `testable-id-manifest.md`（含字符串映射、组件复用图、NEEDS_REVIEW、未注入实装缺失表）** | ✅ 按 Page 分批并发 | `references/agent-prompts/step2-id-inject-agent.md` |
| 第三步：测试用例生成 | **（前置：ID 已注入 + manifest 已就位）**按设计 §C/§F 写 TestDataSetup + 桥 + 生成 `P*_UI.test.ets`；最后单发一次重建 `List.test.ets` | ✅ 生成并发 + 注册单发 | `references/agent-prompts/step3-generate-agent.md` |
| 第四步：执行 | 补基础设施 → 编译双 HAP → daemon 链式启动跑设备 → 出报告 | ❌ 全局单步 | `references/agent-prompts/step4-execute-agent.md` |

```
主线程：枚举 Page → 分批（每批 ≤5）→ 建 spec/test/ui-test/
  ↓
Step 1   ┌ [设计 批1] [设计 批2] [设计 批3] … ┐  并发
         └──────────── barrier① 等全部返回 ───┘
  ↓
Step 2   ┌ [ID 注入 批1] [ID 注入 批2] [ID 注入 批3] … ┐  并发（各注各的 pages/components，manifest 按段追加）
         └──────────── barrier② 等全部返回 ───┘
  ↓
Step 3   ┌ [生成 批1] [生成 批2] [生成 批3] … ┐  并发（各写各的 P*_UI.test.ets，不碰 List）
         └──────────── barrier③ 等全部返回 ───┘
         [生成 agent · MODE=register]           单发一次，重建 List.test.ets
  ↓
Step 4   执行（编译 + 跑设备 + spec/test/ui-report.md + 双写 spec/fix/round-0/ui/）  全局单步
  ↓
[MODE=verify_fix 且 round-0/ui/ 有失败]
  ↓
fix-loop  循环：派 spec-fixer-ui → commit → 重编 → execute(ROUND=N+1) → reconcile → 收敛
```

每个 agent 返回结构化摘要；任一 `BLOCKERS != none` → 主线程停下反馈用户，不进入下一阶段。

> **barrier**：前一阶段并发 agent **全部返回**后才派下一阶段（ID 注入读 `id-inject/P*.md`、生成读 `design/P*.md` + manifest、注册 glob 全部测试文件）。实操：把同一批 agent 放在**一条消息**里并发派出，自然等齐。

## Fix-Loop 主线程编排（MODE=verify_fix）

第四步 execute 跑完写完 `spec/fix/round-0/ui/`（baseline）后，主线程依据下列伪代码循环修复直到收敛。详细字段见 `references/fix-file-schema.md` + `references/reconcile-rules.md`；fixer 行为见 `references/agent-prompts/spec-fixer.md`。

```pseudocode
if MODE == "verify_only":  exit
if round-0/ui/ 失败数 == 0:  write final-summary.md (PASS); exit

N = 0; no_progress = 0
MAX_ROUNDS = 10; NO_PROGRESS_ROUNDS = 2

while N < MAX_ROUNDS:
  # Step 1: 派 spec-fixer-ui（按 ui 层；可按 Page 分批并发，一条消息内派完）
  Agent(general-purpose, prompt=references/agent-prompts/spec-fixer.md,
        LAYER=ui, ROUND=N+1, INPUT_DIR=spec/fix/round-{N}/,
        TESTABLE_ID_MANIFEST=entry/src/main/ets/test/testable-id-manifest.md, ...)
  → EDITED / SKIPPED / BLOCKED / FILES_MODIFIED / DISPOSITION_HINTS

  if EDITED.count == 0 and BLOCKED.count == 0:
      write final-summary.md (FAIL, "无可修条目"); break

  # Step 2: 按 DISPOSITION_HINTS 更新 round-{N}/ui/<id>.md frontmatter
  apply disposition_hints to prev round files

  # Step 3: 主线程 git commit（每轮独立 commit，方便审计/回退）
  git add <FILES_MODIFIED>
  git commit -m "autofix-ui: round-{N+1}"

  # Step 4: 重编双 HAP（hvigorw assembleHap × 2）
  if compile fails:  write compile-failure.md; FAIL; break

  # Step 5: 重派 step4-execute（current_round=N+1，daemon 链式启动必须保留）→ 写 round-{N+1}/ui/ + _ui_delta.md
  通用子代理

  # Step 6: 收敛判定（读 round-{N+1}/_ui_delta.md）
  if round-{N+1}/ui/ 失败数 == 0:        write final-summary.md (PASS); break
  if delta.REGRESSED.count > 0:           # 自动 mark manual_review，不回滚
      for id in delta.REGRESSED: set disposition=manual_review on round-{N+1}/ui/<id>.md
      write regressed.md                  # 记录但继续
  if delta.RESOLVED == 0 and delta.NEWLY_OPEN == 0:
      no_progress += 1
      if no_progress >= NO_PROGRESS_ROUNDS:
          write stalled.md (FAIL); break
  else:
      no_progress = 0

  N += 1

if N >= MAX_ROUNDS:  write final-summary.md (FAIL, "达 MAX_ROUNDS")
```

### 退出条件

| 场景 | 状态 | 产物 |
|---|---|---|
| baseline round-0/ui/ 失败数 == 0 | PASS | `spec/fix/round-0/_ui_summary.md` |
| 循环收敛 round-{N}/ui/ 失败数 == 0 | PASS | `spec/fix/round-{N}/final-summary.md` |
| 达 MAX_ROUNDS | FAIL | 同上 |
| 连续 NO_PROGRESS_ROUNDS 轮无进展 | FAIL | `spec/fix/round-{N}/stalled.md` |
| Step 1 EDITED==0 且 BLOCKED==0 | FAIL | `final-summary.md` |
| Step 4 编译反复失败 | FAIL | `compile-failure.md` |

### 铁律（4 条，违反 = 流程作废）

1. **每轮 commit**：Step 3 失败禁止跳过；丢 commit 历史 = 丢回退能力
2. **fixer EDITED ≠ PASS**：机械计数；真假由下轮 execute 实测（reconcile）
3. **REGRESSED 不回滚**：自动 mark `disposition: manual_review` 防来回反复；不 git reset
4. **双重断言全过才算 PASS**：spec-fixer-ui 修 ui 时**必须**同时让意图层 (`assertComponentExist(...)`) + 状态层 (`AppStorage.get('key')`) 都通过；只过一层下轮仍 RED

## 前置准备

### 目录约定

```
<project_root>/
├── spec/
│   ├── baseline/
│   │   ├── features/         ← 功能 Spec（含 类型=ui 的 AC）
│   │   └── ui/               ← 页面 Spec（page_NNNN_*.md，UI 测试主来源）
│   └── test/
│       ├── ui-test/
│       │   ├── design/      ← 第一步产出：测试设计（每页一份，§A/§B/§C/§D/§F）
│       │   └── id-inject/   ← 第一步产出：ID 注入设计（每页一份，§1 ID 表/§2 跨页面/§3 NEEDS_REVIEW/§4 未注入/§5 page_short）
│       └── ui-report.md      ← 第四步产出：执行报告
└── entry/src/
    ├── main/ets/{pages,components}/  ← 源码（第二步注入 .id；设计/生成时读；spec-fixer-ui 改 pages/components 接 onClick + AppStorage 双重断言状态）
    │   ├── test/TestDataSetup.ets    ← 第三步产出：测试数据预制
    │   └── test/testable-id-manifest.md ← 第二步产出：ID + 字符串映射清单
    └── ohosTest/ets/test/ui/         ← 第三步产出：UI 测试代码

spec/fix/                            ← fix-loop 产物（与 ut-verifier 共用 round-N/，本 skill 写 ui/ 子目录）
├── _state.yaml
├── round-0/                         ← baseline = step4 execute 首跑
│   ├── _ui_index.md / _ui_summary.md
│   └── ui/<id>.md
├── round-1/                         ← fix-loop 第 1 轮回跑
│   ├── _ui_index.md / _ui_summary.md / _ui_delta.md
│   ├── fixer-summary-ui.md
│   └── ui/<id>.md
└── round-N/ …
```

### 环境变量

```bash
export HDC=/Applications/DevEco-Studio.app/Contents/sdk/default/openharmony/toolchains/hdc
export BUNDLE=com.example.your_app
export DEVICE=127.0.0.1:5555
```

## 前置检查（派发前）

```bash
ls spec/baseline/ui/page_*.md 2>/dev/null | head -1     # 页面 Spec 必须有
ls spec/baseline/features/F*.md 2>/dev/null | head -1   # feature 派生 UI AC 来源
$HDC list targets                                        # 第四步前必须有设备
```

**UI 测试三项设备前置（任一缺失 → 整批 ERROR）**：

```bash
# (1) 系统 ArkUI 测试模式（缺失 → Get windows failed）
$HDC -t $DEVICE shell param set persist.ace.testmode.enabled 1
$HDC -t $DEVICE shell reboot   # 改完需重启生效

# (2) auto-sign（缺失 → NapiDefineClass occur exception, Driver.create() 返回 null）
#     DevEco Studio → Project Structure → Signing Configs → 勾 Automatically generate signature

# (3) uitest daemon —— 跑测时**与 aa test 同一条 hdc shell 链式启动**（第四步处理，不在此处）
```

Spec 缺失 → 提示先跑 spec 生成 skill，终止。

## 输出清单

1. **测试设计**：`spec/test/ui-test/design/P*.md`（第一步，每页一份，§A 需求 / §B 矩阵 / §C 用例 / §D 缺口 / §F 测试数据计划）
1b. **ID 注入设计**：`spec/test/ui-test/id-inject/P*.md`（第一步同实例同时产，每页一份，§1 ID 表 / §2 跨页面策略 / §3 NEEDS_REVIEW / §4 未注入清单 / §5 page_short 映射）
2. **源码 `.id()` 注入 + manifest**：`entry/src/main/ets/{pages,components}/` 修改 + `entry/src/main/ets/test/testable-id-manifest.md`（**第二步**）
3. **测试数据 + 桥**：`entry/src/main/ets/test/TestDataSetup.ets` + EntryAbility / 根页桥（第三步）
4. **测试代码**：`entry/src/ohosTest/ets/test/ui/P*_UI.test.ets` + `List.test.ets`（第三步）
5. **测试基础设施 + 双 HAP**：`entry/src/ohosTest/...` + `entry/build/.../*-signed.hap`（第四步）
6. **执行报告**：`spec/test/ui-report.md`（第四步）
7. **Fix-loop 产物**（仅 `MODE=verify_fix`）：`spec/fix/round-N/ui/<id>.md` + `_ui_index.md` + `_ui_summary.md` + `_ui_delta.md`（N≥1）+ `fixer-summary-ui.md`（N≥1）+ `final-summary.md`（退出时）

## 快速检查清单

- [ ] `spec/baseline/ui/` 下有页面规格、`features/` 下有功能 Spec
- [ ] 设备已连接 + `persist.ace.testmode.enabled=1`（已重启）+ auto-sign 已开
- [ ] 第一步后：`spec/test/ui-test/design/` 每页一份测试设计 + `spec/test/ui-test/id-inject/` 每页一份 ID 注入设计；两份文件用例 ID 双向对得上
- [ ] **第二步后**：源码 `.id()` 注入到位（按 id-inject §1 表，§4 列出的不创造源码）+ `testable-id-manifest.md` 各段已写（Page ID 表 / 字符串映射 / 组件复用图 / NEEDS_REVIEW / 未注入实装缺失）
- [ ] 第三步后：每页 `P*_UI.test.ets` 中 `it()` 数 ≥ 设计行数；注册（MODE=register）后 `List.test.ets` 已含所有测试文件
- [ ] 第四步后：双 HAP 编译通过，daemon 链式启动，报告基于真实运行日志；`spec/fix/round-0/ui/` 已就位 + `_state.yaml.current_round=0`
- [ ] **Fix-loop 退出后**：`spec/fix/round-{final}/final-summary.md` 含 PASS / FAIL 结论 + 每轮 UI 层实现率演进表 + 端到端对比（round-0 → round-final）+ 意图层/状态层分别通过率
