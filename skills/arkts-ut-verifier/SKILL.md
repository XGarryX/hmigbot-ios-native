---
name: arkts-ut-verifier
description: 'ArkTS/HarmonyOS Spec 驱动的**单元测试（逻辑层）**验证工具。从 Spec 验收标准 + 源码出发，

  三步流水线（测试设计 → 测试生成 → 执行）自动产出 arkxtest（`@ohos/hypium`）单元测试，

  在真机/模拟器上跑出逻辑层实现率。


  **使用场景**：


  - "验证逻辑层实现率"、"从 spec 生成单元测试"、"单元测试 TDD 验证"

  - "测量逻辑层覆盖/通过率"、"哪些业务逻辑没实现"

  - "逻辑层 RED/GREEN 报告"、"单元实现率报告"


  **不负责 UI 层**（页面渲染 / 控件 / 导航 / 交互）—— UI 层验证用 `arkts-ui-verifier`。

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
  - 验证
  - 测试
  - 单元测试
  - 逻辑层
  - 实现率
---
# ArkTS Spec 单元测试（逻辑层）验证工具

三步流水线（设计 → 生成 → 执行）+ 一段 **fix-loop**（默认开），从 Spec `## 验收标准` + 源码出发，生成 arkxtest 单元测试，跑出逻辑层实现率，并自动派 `spec-fixer-ut` 修 RED 直到全 GREEN 或达到上限。

> **框架**：arkxtest 的 ArkTS 单元框架 `@ohos/hypium`（`describe/it/expect`），编译进测试 HAP、随
> `aa test` 在设备上跑。与 PC 端的 DevEco Testing Hypium（Python 黑盒）无关。
>
> **只做逻辑层**：UI 层（页面/控件/导航/交互）由 `arkts-ui-verifier` 负责，两者独立。
>
> **MODE 参数**：`verify_only` = 只跑三步出报告；`verify_fix`（默认）= 三步跑完后若有 RED 自动进 fix-loop。

## 执行模型

**入口**：必须用 `$arkts-ut-verifier` 在主对话中调用。三步都派 Agent 执行（每个用 子代理派发、通用子代理、**原文读取**对应 prompt 文件传入；各 agent 需授予的工具与输入写在其文件「输入」区）。设计和生成按 Feature **并发派多个 agent**，主线程负责分批、把住 barrier、串接产出。

| 步骤 | 做什么 | 并发？ | Agent prompt |
|------|--------|------|------|
| 第一步：测试用例设计 | 读 Spec + 源码，每个功能点输出一份测试设计 → `spec/test/ut-design/` | ✅ 按 Feature 分批并发 | `references/agent-prompts/step1-design-agent.md` |
| 第二步：测试用例生成 | 读设计 → 生成 `.test.ets`；最后单发一次重建 `List.test.ets` | ✅ 生成并发 + 注册单发 | `references/agent-prompts/step2-generate-agent.md` |
| 第三步：执行 | 补基础设施 → 编译双 HAP → 跑设备 → 出报告 | ❌ 全局单步 | `references/agent-prompts/step3-execute-agent.md` |

```
主线程：枚举 Feature → 分批（每批 ≤5）→ 建 spec/test/ut-design/
  ↓
Step 1  ┌ [设计 批1] [设计 批2] [设计 批3] … ┐  并发
        └──────────── barrier① 等全部返回 ───┘
  ↓
Step 2  ┌ [生成 批1] [生成 批2] [生成 批3] … ┐  并发（各写各的 .test.ets，不碰 List）
        └──────────── barrier② 等全部返回 ───┘
        [生成 agent · MODE=register]           单发一次，重建 List.test.ets
  ↓
Step 3  执行（编译 + 跑设备 + spec/test/ut-report.md + 双写 spec/fix/round-0/ut/）  全局单步
  ↓
[MODE=verify_fix 且 round-0/ut/ 有失败]
  ↓
fix-loop  循环：派 spec-fixer-ut → commit → 重编 → execute(ROUND=N+1) → reconcile → 收敛
```

每个 agent 返回结构化摘要；任一 `BLOCKERS != none` → 主线程停下反馈用户，不进入下一阶段。

> **barrier**：前一阶段的并发 agent **全部返回**后才派下一阶段（生成要读设计的产出、注册要 glob 全部测试文件）。实操：把同一批 agent 放在**一条消息**里并发派出，自然等齐。

## Fix-Loop 主线程编排（MODE=verify_fix）

第三步 execute 跑完写完 `spec/fix/round-0/ut/`（baseline）后，主线程依据下列伪代码循环修复直到收敛。详细字段定义见 `references/fix-file-schema.md` + `references/reconcile-rules.md`；fixer 行为见 `references/agent-prompts/spec-fixer.md`。

```pseudocode
if MODE == "verify_only":  exit
if round-0/ut/ 失败数 == 0:  write final-summary.md (PASS); exit

N = 0; no_progress = 0
MAX_ROUNDS = 10; NO_PROGRESS_ROUNDS = 2

while N < MAX_ROUNDS:
  # Step 1: 派 spec-fixer-ut（按 ut 层；可按 Feature 分批并发，一条消息内派完）
  Agent(general-purpose, prompt=references/agent-prompts/spec-fixer.md,
        LAYER=ut, ROUND=N+1, INPUT_DIR=spec/fix/round-{N}/, ...)
  → EDITED / SKIPPED / BLOCKED / FILES_MODIFIED / DISPOSITION_HINTS

  if EDITED.count == 0 and BLOCKED.count == 0:
      write final-summary.md (FAIL, "无可修条目"); break

  # Step 2: 按 DISPOSITION_HINTS 更新 round-{N}/ut/<id>.md frontmatter
  apply disposition_hints to prev round files

  # Step 3: 主线程 git commit（每轮独立 commit，方便审计/回退）
  git add <FILES_MODIFIED>
  git commit -m "autofix-ut: round-{N+1}"

  # Step 4: 重编双 HAP（hvigorw assembleHap × 2）
  if compile fails:  write compile-failure.md; FAIL; break

  # Step 5: 重派 step3-execute（current_round=N+1）→ 写 round-{N+1}/ut/ + _ut_delta.md
  通用子代理

  # Step 6: 收敛判定（读 round-{N+1}/_ut_delta.md）
  if round-{N+1}/ut/ 失败数 == 0:        write final-summary.md (PASS); break
  if delta.REGRESSED.count > 0:           # 自动 mark manual_review，不回滚
      for id in delta.REGRESSED: set disposition=manual_review on round-{N+1}/ut/<id>.md
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
| baseline round-0/ut/ 失败数 == 0 | PASS | `spec/fix/round-0/_ut_summary.md` |
| 循环收敛 round-{N}/ut/ 失败数 == 0 | PASS | `spec/fix/round-{N}/final-summary.md` |
| 达 MAX_ROUNDS | FAIL | 同上 |
| 连续 NO_PROGRESS_ROUNDS 轮无进展 | FAIL | `spec/fix/round-{N}/stalled.md` |
| Step 1 EDITED==0 且 BLOCKED==0 | FAIL | `final-summary.md` |
| Step 4 编译反复失败 | FAIL | `compile-failure.md` |

### 铁律（3 条，违反 = 流程作废）

1. **每轮 commit**：Step 3 失败禁止跳过；丢 commit 历史 = 丢回退能力
2. **fixer EDITED ≠ PASS**：fixer 报"修了 N 个"是机械计数；真假由下轮 execute 实测（reconcile）
3. **REGRESSED 不回滚**：自动 mark `disposition: manual_review` 防来回反复，但**不 git reset**；本轮其它 RESOLVED 的进展保留

## 前置准备

### 目录约定

```
<project_root>/
├── spec/
│   ├── baseline/features/      ← 输入：功能 Spec（F001_xxx.md …）
│   └── test/
│       ├── ut-design/          ← 第一步产出：测试设计（每功能点一份）
│       └── ut-report.md        ← 第三步产出：执行报告
└── entry/src/
    ├── main/ets/               ← 源码（设计/生成时读；spec-fixer-ut 改 services/viewmodels/repository/database 等）
    └── ohosTest/ets/test/spec/ ← 第二步产出：测试代码

spec/fix/                       ← fix-loop 产物（共用 round-N/，本 skill 写 ut/ 子目录）
├── _state.yaml
├── round-0/                    ← baseline = step3 execute 首跑
│   ├── _ut_index.md / _ut_summary.md
│   └── ut/<id>.md
├── round-1/                    ← fix-loop 第 1 轮回跑
│   ├── _ut_index.md / _ut_summary.md / _ut_delta.md
│   ├── fixer-summary-ut.md
│   └── ut/<id>.md
└── round-N/ …
```

### 环境变量

```bash
export HDC=/Applications/DevEco-Studio.app/Contents/sdk/default/openharmony/toolchains/hdc
export BUNDLE=com.example.your_app      # 实际包名（AppScope/app.json5）
export DEVICE=127.0.0.1:5555            # 模拟器 / 真机设备 ID
```

## 前置检查（派发前）

```bash
ls spec/baseline/features/F*.md 2>/dev/null | head -1   # 为空 → 提示先生成 Spec，终止
$HDC list targets                                        # 第三步前必须有设备
```

Spec 为空 → 告知用户先运行 Spec 生成 skill，**终止**，不要让 Agent 自己造 Spec。

## 输出清单

1. **测试设计**：`spec/test/ut-design/F*.md`（第一步）
2. **测试代码**：`entry/src/ohosTest/ets/test/spec/F*.test.ets` + `List.test.ets`（第二步）
3. **测试基础设施 + 双 HAP**：`entry/src/ohosTest/...` + `entry/build/.../*-signed.hap`（第三步）
4. **执行报告**：`spec/test/ut-report.md`（第三步）
5. **Fix-loop 产物**（仅 `MODE=verify_fix`）：`spec/fix/round-N/ut/<id>.md` + `_ut_index.md` + `_ut_summary.md` + `_ut_delta.md`（N≥1）+ `fixer-summary-ut.md`（N≥1）+ `final-summary.md`（退出时）

## 快速检查清单

- [ ] `spec/baseline/features/` 下有 Feature 文件
- [ ] 第一步后：`spec/test/ut-design/` 每个 Feature 一份设计，每条逻辑层 AC 有用例行
- [ ] 第二步后：每 Feature 的 `it()` 数 ≥ 设计行数，无占位断言；注册（MODE=register）后 `List.test.ets` 已含所有测试文件
- [ ] 第三步后：双 HAP 编译通过，设备已连接，报告基于真实运行日志；`spec/fix/round-0/ut/` 已就位 + `_state.yaml.current_round=0`
- [ ] **Fix-loop 退出后**：`spec/fix/round-{final}/final-summary.md` 含 PASS / FAIL 结论 + 每轮实现率演进表 + 端到端对比（round-0 → round-final）
