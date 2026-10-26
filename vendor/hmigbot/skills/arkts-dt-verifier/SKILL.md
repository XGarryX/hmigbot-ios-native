---
name: arkts-dt-verifier
description: 'ArkTS/HarmonyOS Spec 驱动 TDD 验证工具。从 Spec 验收标准出发，自动生成单元测试 + UI 测试，测量应用的逻辑层和 UI 层实现率，置信度 ≥ 95%。


  **必须使用此 skill 的场景（包括但不限于）**：


  - "验证功能实现率"、"measure feature coverage"、"spec 合规检查"

  - "从 spec 生成测试"、"TDD 验证"、"功能验收"

  - "迁移后验证"、"Android → HarmonyOS 验收"

  - "测量逻辑层实现率"、"UI 层实现率"、"哪些功能没实现"

  - "生成 spec 测试"、"从验收标准写测试"

  - "自动生成 MockKit 测试"、"批量生成 it() 用例"

  - "RED/GREEN 报告"、"实现率报告"


  **核心能力**：五步流水线（单元测试 → 测试数据 + ID 注入 → UI 测试 → 基础设施+编译 → 跑测+报告），从 Spec 目录自动推导测试用例，用 MockKit 隔离外部依赖，产出 RED/GREEN 实现率报告 + 分层修复清单。

  '
metadata:
  type: domain
  domain: migration
  tags:
  - verification
  - testing
  - tdd
  - coverage
  - mockkit
  - hypium
  - 验证
  - 测试
  - 单元测试
  - UI测试
  - 实现率
  - 验收
---
# ArkTS Spec TDD 验证工具

本 skill 通过五步流水线（前置检查 → 单元测试 → 测试数据 + ID 注入 → UI 测试 → 基础设施+编译 → 跑测+报告），从 Spec 验收标准出发，生成全量测试，测量 ArkTS/HarmonyOS 应用的实现率。

## 执行模型

**入口**：必须用 `$arkts-dt-verifier` 在主对话中调用，禁止 `通用子代理` 嵌套（中间产物会丢）。

| 步骤 | 执行方 | Prompt 位置 |
|------|------|------|
| 第一步：单元测试 | Agent | `references/agent-prompts/step1-unit-test-agent.md` |
| 第二步 a：测试数据 | Agent | `references/agent-prompts/step2-test-data-agent.md` |
| 第二步 b：可测试 ID 注入 | Agent | `references/agent-prompts/step2b-id-injector-agent.md` |
| 第三步：UI 测试 | Agent | `references/agent-prompts/step3-ui-test-agent.md` |
| 第四步：基础设施 + 编译 | Agent | `references/agent-prompts/step4-infra-compile-agent.md` |
| 第五步：执行 + 报告 | 主线程内联 | 见 [第五步](#第五步执行测试并生成报告) |

**派发顺序**：

```
Step 0    前置检查（设备 + MockKit 策略）
  ↓
Step 1    单元测试生成
  ↓
┌─ Step 2a   测试数据预制          ┐
│                                  │ 并发（写不同文件）
└─ Step 2b   ID 注入 + 字符串映射  ┘
  ↓
Step 3    UI 测试生成
  ↓
Step 4    测试基础设施 + 编译通过
  ↓
Step 5    跑测 + 报告
```

依赖关系（**前提假设**：`spec/baseline/` 已经准确，不做任何 snapshot 增强或校正）：
- **Step 1** 读 `spec/baseline/features/`
- **Step 2a** 读 Step 1 的 `tdd-ac-index.md`，提取"涉及页面"做数据预置，**必须等 Step 1 完成**
- **Step 2b** 扫 `entry/src/main/ets/pages/` **+ `entry/src/main/ets/components/`**（被 pages/ import 的子组件视为可达）双根扫描源码 `$r(...)`，独立产出 `testable-id-manifest.md`。**注意**：仅扫 pages/ 会导致 BrowserToolbar / SettingScreen / Dialog 等抽出子组件的可测 id 缺失，UI 测试覆盖率虚低。
- **Step 3** 读 `spec/baseline/ui/page_*.md`，**强依赖** Step 2b 的 `testable-id-manifest.md`；生成 selector 时查 `testable-id-manifest.md` 字符串映射（HarmonyOS 源码实装的文案）
- **Step 4** 读前序所有产出，检查/补全 ohosTest 基础设施（TestRunner + Hypium、TestAbility、module.json5、资源骨架），编译主 HAP + 测试 HAP 直到双 HAP 通过
- **Step 5** 主线程执行，消费前面所有产出（含 Step 4 的 HAP 产物）

主线程（即调用本 skill 的主对话）负责：前置检查（设备 + MockKit 策略）→ 派发 Step 1~4 Agent → 内联执行 Step 5（跑测 + 报告 + 写盘）→ 把结果留在主对话上下文供上层调用方使用。

## 目录

- [前置准备](#前置准备) — 环境变量、目录约定
- [前置检查](#前置检查) — 设备可用性 + MockKit 策略（必须先完成）
- [第一步：派发单元测试 Agent](#第一步派发单元测试-agent)
- [第二步 a：派发测试数据 Agent](#第二步-a派发测试数据-agent)
- [第二步 b：派发 ID 注入 Agent](#第二步-b派发-id-注入-agent)
- [第三步：派发 UI 测试 Agent](#第三步派发-ui-测试-agent)
- [第四步：派发测试基础设施 + 编译 Agent](#第四步派发测试基础设施--编译-agent)
- [第五步：执行测试并生成报告](#第五步执行测试并生成报告)
- [按范围过滤运行](#按范围过滤运行调试用) — 调试单个 Feature / Page / it() 的 `aa test` 过滤命令
- [参考文档](#参考文档) — 测试模式、AC 索引格式、报告模板等
- [输出清单](#输出清单) — 五步跑完后交付用户的全部文件

---

## 前置准备

### 目录约定（可按项目调整）

```
<project_root>/
├── spec/baseline/
│   ├── features/          ← 功能 Spec（F001_xxx.md, F002_xxx.md …）
│   └── ui/                ← 页面 Spec（page_0001.md …）
├── entry/src/
│   ├── main/ets/          ← 源码（models / viewmodels / services / …）
│   └── ohosTest/ets/test/ ← 设备测试入口
└── entry/src/test/        ← 本地单元测试（可选）
```

### 环境变量

```bash
export HDC=/Applications/DevEco-Studio.app/Contents/sdk/default/openharmony/toolchains/hdc
export BUNDLE=com.example.your_app      # 替换为实际包名
export DEVICE=127.0.0.1:5555            # 模拟器或真机设备 ID
```

---

## 前置检查

在派发任何 Agent 之前，主线程**必须**先完成以下两项检查，并将结果作为参数传给 Agent。

### 1. Spec 存在性

```bash
ls spec/baseline/features/F*.md 2>/dev/null | head -1
```

若为空 → 告知用户先运行 `arkts-spec-evolver` skill 生成 Spec，**终止**。不要让 Agent 自己生成。

### 2. 架构 + 测试入口探测（Step 2a 自动做，但主线程必须**透传**两个字段）

#### 2a. MOUNT_STRATEGY（→ Step 3）

skill 原生支持两种应用架构，Step 2a Agent 在 §0 节自动探测：

| 探测条件（在根页 `entry/src/main/ets/pages/<RootPage>.ets`） | MOUNT_STRATEGY |
|---|---|
| 含 `: NavPathStack` 字段 | `NAVIGATION_DIRECT_MOUNT` |
| 不含 `: NavPathStack` 字段 | `ROUTER_LOAD_CONTENT` |

主线程**必须**保存 Step 2a 返回的 `MOUNT_STRATEGY` 字段，并作为输入透传给 Step 3。Step 3 据此选 UI 测试骨架（`ui-test-skeleton.md` vs `router-load-content.md` §B），无需主线程做架构判断。

#### 2b. TEST_ENTRY_ABILITY（→ Step 4）

> **背景**：`aa test -b $BUNDLE -m entry_test` 启动的入口是 `TestAbility`（位于 `entry/src/ohosTest/ets/testability/TestAbility.ets`），**不是** EntryAbility。任何"全程都需要的 globalThis 缓存"必须写在 TestAbility.onCreate，否则源码层 getInstance() 第一次调用时 globalThis 还是空的（5-7 v2 round-1 浪费 ~57min 教训）。

Step 2a Agent 在 §0c 节探测 TestAbility 路径并返回：

| Step 2a 返回字段 | 含义 |
|---|---|
| `TEST_ENTRY_ABILITY: TestAbility` | 默认值；TestAbility.ets 已存在（被本步注入了 globalThis 缓存）|
| `TEST_ENTRY_ABILITY: <某文件名>` | ohosTest/ 下有非默认命名的 UIAbility 文件，本步把缓存注入到那个文件 |
| `TEST_ENTRY_ABILITY: DEFERRED_TO_STEP_4` | ohosTest/ 整个不存在，待 Step 4 创建时一并注入 |
| `TEST_ABILITY_PATH: <路径> \| null` | 上面那个文件的相对仓内路径 |
| `TEST_CONTEXT_CACHE_INJECTED: yes \| deferred` | 本步已注入 / 还没有 |

主线程**必须**透传这三字段给 Step 4。Step 4 据此决定是否在创建/修改 TestAbility.ets 时再注入 globalThis 缓存（见 step4-infra-compile-agent.md §3 §3.2）。

**禁止项**：
- 不要主线程自己重做架构探测得出不同结论
- 不要漏传 `MOUNT_STRATEGY`（漏传 → Step 3 BLOCKER）
- 不要漏传 `TEST_ENTRY_ABILITY`（漏传 → Step 4 不知道是否需要注入 → round-0 立刻产生 db-init 类 ERROR）

### 3. MockKit 策略（必须与用户确认后再派发 Step 1 Agent）

**不要自己读 Spec 判断是否有 MockKit 类 AC**（分类是 Step 1 Agent 的工作）。直接**无条件**向用户抛下述模板：

```
【MockKit 策略确认】
接下来要生成测试。涉及 DB / fileIo / photoAccessHelper / Context / Ability 生命周期的 AC
必须有真实运行环境才能写出有效断言，请选择策略：

  A. full     — 真机/模拟器已连接（$HDC list targets 能列出设备），写完整行为断言
  B. deferred — 暂不连设备，这类 AC 标为 deferred（不生成测试、不计入分母）
                ⚠️ 注意：选 B 会导致第五步（跑测 + 出报告）也无法执行，仅产出代码
  C. weak     — 允许弱断言（方法存在性），会虚高 GREEN 率，报告醒目标注升级路径

回复 A / B / C。
```

用户回复后，将选择转为 `MOCKKIT_POLICY=full|deferred|weak`，传给 Step 1 Agent。

- 选 B → 主线程可继续派发 Step 1~4 Agent 生成代码并编译，但**必须在第四步完成后告知用户"第五步已跳过，待设备就绪后再跑"**，不要静默结束。
- 选 A/C → 正常进入第五步。

**⚠️ weak 策略警告（必读）**：weak 策略产出 `expect(typeof method).assertEqual('function')` 类弱断言（"method_exists"），会让 GREEN 率虚高（典型差异 +18~28pp）。EinkBro 项目实测：Step 1 Agent 私自降级到 weak 风格（27 个 mockkit + 33 个 todo AC 写成 `expect(true).assertTrue()` / 常量自比 / typeof 自检），最终 100% PASS 实际只对应 73.3% 真覆盖（418 个 it() 中 117 条是 C 级伪覆盖）。**只在显式无法接通真实 Context / 没有依赖注入点时选择 weak**；优先看 `references/test-patterns.md §MockKit ArkTS 兼容方案` 三种方案能否套用。

**禁止项**：不要私自降级策略；不要先生成 `{} as Context` 或 `expect(typeof xx).assertEqual('function')` 弱断言再继续后面步骤；不要把 todo AC 写成空 it() 体或 `expect(true).assertTrue()` 占位 —— 真正的 todo 应该写正向行为断言并预期 RED。Step 1 Agent 自检铁律会在生成测试后强 grep 检测，命中即 BLOCKER。

---

## 第一步：派发单元测试 Agent

**Agent prompt 文件**：`references/agent-prompts/step1-unit-test-agent.md`

> 从 AC 生成测试时，complex feature 的每条 AC 末尾带 `源:<Kotlin 符号> → 标:<ArkTS 方法>`——以 `标` 作为测试**断言落点**、`源` 作为期望行为来源，提高用例落点精度、减少「以释义写测试」；透传给 Agent 的 spec 须保留该追踪字段。

### 派发方式

用 子代理派发，通用子代理，工具权限 `Read, Glob, Grep, Edit, Write`。**原文读取** prompt 文件后整段传入 `prompt` 字段，并在末尾附加本次输入：

```
PROJECT_ROOT: <绝对路径>
MOCKKIT_POLICY: full|deferred|weak
```

### 预期产出（Agent 返回的结构化摘要字段）

- `AC_INDEX_PATH`: `entry/src/ohosTest/ets/test/tdd-ac-index.md`
- `UNIT_AC_COUNT` / `UI_AC_COUNT` / `DEFERRED_AC_COUNT` / `WEAK_AC_COUNT`
- `GENERATED_FILES`: `entry/src/ohosTest/ets/test/spec/F*.test.ets` 列表
- `LIST_TEST_UPDATED`: yes/no
- `BLOCKERS`: none 或阻塞原因

若 `BLOCKERS != none` → 主线程停下，向用户反馈阻塞项，不派发后续 Agent。

---

## 第二步 a：派发测试数据 Agent

**Agent prompt 文件**：`references/agent-prompts/step2-test-data-agent.md`

### 前置

Step 1 Agent 必须已完成（`entry/src/ohosTest/ets/test/tdd-ac-index.md` 存在）。Step 2a Agent 依赖该文件提取"涉及页面"列表。

### 派发方式

用 子代理派发，通用子代理，工具权限 `Read, Glob, Grep, Edit, Write`。原文传入 prompt，末尾附加：

```
PROJECT_ROOT: <绝对路径>
DATA_STRATEGY: mock   # 默认 mock；如需 db / hdc-push 由用户显式指定
```

### 与 Step 2b 的并发

Step 2a（改 EntryAbility / Service / Repository + 新增 TestDataSetup）与 Step 2b（注入 .id 到 pages/）**写不同文件**，可在**同一条消息中并发派发**。

### 预期产出

- `MOUNT_STRATEGY`: `NAVIGATION_DIRECT_MOUNT` 或 `ROUTER_LOAD_CONTENT`（Step 2a §0 自动探测，主线程必须保存并透传给 Step 3）
- `CREATED`: `entry/src/main/ets/test/TestDataSetup.ets`
- `MODIFIED`: 入口 Ability、相关 Service/Repository 条件分支
- `DIRECT_MOUNT_BRIDGE` / `ROUTER_LOAD_CONTENT_BRIDGE`: injected | not-applicable | missing
- `MOCK_ENTITIES`: 各类实体数量
- `BLOCKERS`: none 或阻塞原因

---

## 第二步 b：派发 ID 注入 Agent

**Agent prompt 文件**：`references/agent-prompts/step2b-id-injector-agent.md`

### 目的

UI selector 字面量稳定性的根治方案：让源码主动暴露稳定的 `.id('...')` 锚点，配合 `references/testable-id-catalog.md` 定义的命名规范，杜绝"图标按钮没文本所以靠翻译猜中文 selector"这类 False-ERROR。

### 前置

无强依赖（不依赖 Step 1/Step 2a 产出）；建议与 Step 2a 并发派发以节省时间。

### 派发方式

用 子代理派发，通用子代理，工具权限 `Read, Glob, Grep, Edit, Write`。原文传入 prompt，末尾附加：

```
PROJECT_ROOT: <绝对路径>
```

### 预期产出

- `MANIFEST_PATH`: `entry/src/main/ets/test/testable-id-manifest.md`
- `PAGES_SCANNED` / `IDS_INJECTED` / `IDS_RENAMED` / `NEEDS_REVIEW`
- `SOURCE_FILES_MODIFIED`: pages/*.ets 列表
- `STRING_KEYS_RESOLVED` + `LOCALES_FOUND` + `TEST_DEVICE_LOCALE_ASSUMED`
- `BLOCKERS`: none 或阻塞原因

若 `NEEDS_REVIEW > 0`，主线程必须在派发 Step 3 前向用户出示这些条目并请求确认（批准 / 修改），否则 Step 3 selector 会缺锚点。

---

## 第三步：派发 UI 测试 Agent

**Agent prompt 文件**：`references/agent-prompts/step3-ui-test-agent.md`

### 前置

- Step 1 Agent 已完成（`tdd-ac-index.md` 存在）
- **Step 2b Agent 已完成**（`entry/src/main/ets/test/testable-id-manifest.md` 存在）—— Step 3 的 UI selector 强依赖 manifest 里的 `<page_short>_<purpose>_<kind>` id 与"测试设备实际渲染"的字符串值
- Step 2b 中 `[NEEDS_REVIEW]` 项已经过用户确认

### 派发方式

用 子代理派发，通用子代理，工具权限 `Read, Glob, Grep, Edit, Write`。原文传入 prompt，末尾附加：

```
PROJECT_ROOT: <绝对路径>
BUNDLE_NAME: <从 AppScope/app.json5 的 app.bundleName 读取>
ID_MANIFEST: entry/src/main/ets/test/testable-id-manifest.md
MOUNT_STRATEGY: <Step 2a 返回的 MOUNT_STRATEGY，NAVIGATION_DIRECT_MOUNT 或 ROUTER_LOAD_CONTENT；不传 = BLOCKER>
```

**串行**：Step 3 必须在 Step 2b 之后启动，不能与 2a/2b 并发。

**MOUNT_STRATEGY 透传**：必须从 Step 2a 的返回字段拿到这个值再调 Step 3，不要漏传也不要主线程重判。Step 3 据此选 UI 测试骨架（NAVIGATION 用 ui-test-skeleton.md / ROUTER 用 router-load-content.md §B）。

### 预期产出

- `UI_TEST_FILES`: `entry/src/ohosTest/ets/test/ui/P*_UI.test.ets` 列表
- `PAGE_COUNT` / `TOTAL_UI_AC`（含 SMOKE / COMP / NAV / INTERACT / FEATURE_DERIVED 分项）
- `AC_INDEX_APPENDED`: yes
- `LIST_TEST_UPDATED`: yes
- `BLOCKERS`: none 或阻塞原因

---

## 第四步：派发测试基础设施 + 编译 Agent

**Agent prompt 文件**：`references/agent-prompts/step4-infra-compile-agent.md`

### 前置

Step 1~3 已完成（测试代码 + List.test.ets 已生成）。

### 派发方式

用 子代理派发，通用子代理，工具权限 `Read, Glob, Grep, Bash, Edit, Write`。原文读取 prompt 文件并整段传入 `prompt` 字段，并在末尾附加：

```
PROJECT_ROOT: <绝对路径>
BUNDLE_NAME: <从 AppScope/app.json5 读取>
TEST_ENTRY_ABILITY: <Step 2a 返回的 TEST_ENTRY_ABILITY 值；不传 = 默认 TestAbility>
TEST_ABILITY_PATH: <Step 2a 返回的 TEST_ABILITY_PATH 值；不传 = 默认 entry/src/ohosTest/ets/testability/TestAbility.ets>
TEST_CONTEXT_CACHE_INJECTED: <Step 2a 返回的 TEST_CONTEXT_CACHE_INJECTED；yes / deferred>
```

### 职责（Agent 内完成）

1. 检查 + 补全 ohosTest 基础设施（TestRunner + Hypium、TestAbility、module.json5、资源骨架）
2. **若 `TEST_CONTEXT_CACHE_INJECTED=deferred`**（即 Step 2a 没注入 globalThis 上下文缓存）→ 在创建/写入 TestAbility.ets 时按 `step4-infra-compile-agent.md §3` 标准骨架注入 `globalThis['__app_test_context__'] = this.context`；**若 `TEST_CONTEXT_CACHE_INJECTED=yes`** → 不要重复改 TestAbility.onCreate（Step 2a 已写完）
3. 优先从 git 历史分支复用已验证的基础设施文件
4. 编译主 HAP + 测试 HAP：`hvigorw clean --no-daemon assembleHap -p buildMode=debug` + `hvigorw --no-daemon assembleHap --mode module -p product=default -p module=entry@ohosTest`，边跑边解析编译错误并 Edit 源码修复，直到双 HAP `BUILD SUCCESSFUL`（≤ 20 轮）

### 预期产出（Agent 返回的结构化摘要字段）

- `MAIN_HAP` / `TEST_HAP`：两个 signed HAP 路径
- `COMPILE_ROUNDS`：编译轮数
- `MODULE_JSON5_TOUCHED`: yes / no（是否改了 ohosTest/module.json5）
- `TEST_RUNNER_TOUCHED`: yes / no（是否改了 OpenHarmonyTestRunner.ets）
- `TEST_ABILITY_TOUCHED`: yes / no（是否改了 TestAbility.ets）
- `SRC_FILES_TOUCHED`: 列出 entry/src/main 下被改的文件（应为空或最小集 —— Step 4 不允许改业务代码，除非前序步骤引入了编译错误且修复仅限补类型注解）
- `BLOCKERS`: none 或阻塞原因

若 `BLOCKERS != none` → 主线程停下，不派发 Step 5。

---

## 第五步：执行测试并生成报告

前四步产出测试代码、AC 索引和已编译的双 HAP。最后一步**必须**在真机/模拟器上跑完两类测试，并把**真实运行结果**写成报告 —— 不允许跳过运行直接出"静态预测"报告。

### 执行流程

#### 1. 前置检查

```bash
$HDC list targets   # 必须列出至少一个设备
```

若无设备，停下并提示用户连接，不要继续。

**⚠️ 启动 uitest daemon（UI 测试前必做，否则整批 UI 用例会 ERROR）**

**🔴 关键铁律：`uitest start-daemon` 与 `aa test` 必须在同一条 `hdc shell` 命令里链式执行**（用 `;` 或 `&&` 串起来），否则 daemon 会被杀，整批 UI 用例报 `Cannot read property delayMs of null` / `Wait for ApiCaller publish by server timeout`。

```bash
# ❌ 错误：分两条 hdc shell 调用
$HDC -t $DEVICE shell uitest start-daemon 0          # daemon 起在 shell A
$HDC -t $DEVICE shell aa test ...                    # shell A 已退出，daemon 被 reap → 测试全 ERROR

# ✅ 正确：单条 hdc shell 会话内链式执行
$HDC -t $DEVICE shell "uitest start-daemon 0; aa test -b $BUNDLE -m entry_test \
  -s unittest OpenHarmonyTestRunner -s timeout 600000" > /tmp/tdd-run.log 2>&1
```

**根因**：OpenHarmony/HarmonyOS 模拟器上 `uitest start-daemon 0` 自身 daemonize 后，父 shell（hdc session）一旦退出会导致 daemon 进程被清理（观察到 pid 立刻消失，与 `nohup`/`setsid` 组合无关）。`dumpLayout` 命令每次独立 spawn 进程所以"看着能工作"，误导你以为 daemon 活着——但 `Driver.create()` 连的是持久 daemon 的 IPC 频道，所以失败。链式执行让 shell 在 `aa test` 运行期间始终存活，daemon 就不会被收走。

**token 必须是 `0`**（对应默认通道 `uitest.api.caller.publish#default`），传其它 token daemon 的 IPC 订阅频道错位，客户端永远连不上。

daemon 不常驻：**每次跑测都要重新链式启动**。设备重启 / 新装模拟器 / 上轮 daemon 已死都适用。

**三个可能的根因，症状都是"所有 UI 用例 ERROR，`Cannot read property xxx of null` on mountPage"，必须逐项排查**：

| 根因 | hilog 特征 | 修法 |
|---|---|---|
| ① daemon 没起 / 被杀 | `Wait for ApiCaller publish by server timeout` + `ipc connection is dead (17000006)` 或 `Cannot get AbilityDelegator, uitest_daemon need to be pre-started` | 用上方"✅ 正确"链式命令 |
| ② 没开 auto-sign | `NapiDefineClass occur exception, className:Driver` | DevEco → File → Project Structure → Signing Configs → 勾 Automatically generate signature，重编重装 |
| ③ `Driver.create()` 写在了 `beforeAll` | hilog 里没明显 error，但 beforeAll 阶段 `Cannot get AbilityDelegator` | 改成 `beforeEach` + lazy init，详见 `templates/ui-test-skeleton.md` |

三条常同时出现或掩盖彼此——先修 ②（编译期，最好验证），再修 ③（代码），最后跑测前用链式命令保证 ①。**单元测试不依赖 daemon / UiTest Driver**，这三个坑单元测试都不受影响。

**自检 smoke**（链式命令是否生效，跑单条 SMOKE 看一眼）：

```bash
$HDC -t $DEVICE shell "uitest start-daemon 0; aa test -b $BUNDLE -m entry_test \
  -s unittest OpenHarmonyTestRunner -s class MainPage_UI#P0002_UI_SMOKE_page_renders -s timeout 60000" 2>&1 | tail -5
# 期望：OHOS_REPORT_RESULT: Tests run: 1, ... Pass: 1
# 若 Error: 1 且 stream=Cannot read property delayMs of null → 链式命令没生效或 daemon 正被别的进程杀
```

#### 2. 安装 + 后台运行（两类测试同一入口）

单元测试和 UI 测试都注册在 `List.test.ets`，一次 `aa test` 即可跑完。

**⚠️ 测试必须在后台运行**：全量测试（含 UI 测试）通常耗时 10~30 分钟，前台运行会被 CLI 超时中断。使用 `Bash(run_in_background=true)` 或 `> /tmp/tdd-run.log 2>&1` 重定向，然后用 `Monitor` 轮询完成。

**Step 4 已编译好双 HAP**，直接安装并后台跑测：

```bash
# 1. 安装两个 HAP（-r 覆盖旧版）
$HDC -t $DEVICE install -r entry/build/default/outputs/default/entry-default-signed.hap
$HDC -t $DEVICE install -r entry/build/default/outputs/ohosTest/entry-ohosTest-signed.hap

# 2. 后台跑测（daemon + aa test 必须链式在同一条 hdc shell 命令内，详见前一节"关键铁律"）
$HDC -t $DEVICE shell "uitest start-daemon 0; aa test -b $BUNDLE -m entry_test \
  -s unittest OpenHarmonyTestRunner -s timeout 600000" > /tmp/tdd-run.log 2>&1
```

使用 `Bash(run_in_background=true)` 执行上述命令，然后用 `Monitor` 等待 `user test finished` 出现在输出文件中：

```bash
# Monitor 脚本示例
until grep -q "user test finished" /tmp/tdd-run.log 2>/dev/null; do sleep 30; done
echo "DONE"
grep -E "Tests run:|TestFinished" /tmp/tdd-run.log
```

⚠️ **Monitor `timeout_ms` 必须设到最大值 `3600000`（1 小时）**。全量测试（含 P0010 SettingsPage 61 个 UI 用例）单次可能跑 30~50 分钟，默认 `timeout_ms: 300000`（5 分钟）会让 Monitor 提前超时退出，但**后台任务仍在设备上继续跑** —— 导致主线程误以为"测试挂了"而重启测试，造成两次测试并发冲突 + 浪费时间。`Monitor` 超时只杀轮询循环，不杀后台 `aa test` 进程；两者生命周期独立。

测试完成后，从 `/tmp/tdd-run.log`（或 Bash 后台任务的 output 文件）解析结果。

⚠️ **若 Step 4 之后又修改了源码**（如手动修 bug），必须重新编译再安装，否则设备上运行的是旧 HAP。

**自检**：测试结果若出现"大量 SMOKE 测试 ERROR + 全部 selector 命中失败"，第一反应应该是"HAP 版本不一致"——可用 `uitest dumpLayout` 验证：若 dump 里 id 全为空字符串 → 装的是旧主 HAP；若 id 字面量出现 → 装的是新 HAP。

#### 3. 解析测试结果

从日志中提取：

- **汇总行**：`Tests run: N, Failures: F, Errors: E` → GREEN = N − F − E
- **逐用例行**：形如 `[PASS] F001_AC01_xxx` / `[FAIL] P0002_UI_SMOKE_xxx` → 落到每条 AC

按**命名前缀**区分两类：
- `F{编号}_AC...` → 单元测试（逻辑层）
- `P{编号}_UI_{SMOKE|COMP|NAV|INTERACT}_...` / `F{编号}_UI_AC...` → UI 测试（UI 层）

分别计算：

```
逻辑层实现率 = 单元 GREEN / 单元总数
UI 层实现率   = UI GREEN / UI 总数
总实现率     = 总 GREEN / 总数
```

> **stub feature 不计欠账**：`tier: peripheral` / `depth: stub` 的 feature 在 baseline 仅占位 AC（3–8 条，深挖待 a2h-spec Step C4.6c 按需触发）——其 RED 不算「实现欠账」，单列「stub 待深挖」一类，不混入上述实现率分母拉低指标。

#### 4. 回写 AC 索引

`entry/src/ohosTest/ets/test/tdd-ac-index.md` 里有**两组表格**都要回写 `运行结果` 列：

1. **Feature 主表**（Step 1 产出）：行键 `AC` 列（形如 `AC1`），it() 命名前缀 `F{编号}_AC{序号}_…`
2. **Page 来源节**（Step 3 追加的 `## 来源：页面 Spec（P00xx）`）：行键 `AC ID` 列（形如 `P0002_UI_SMOKE`），it() 命名前缀 `P{编号}_UI_{SMOKE|COMP|NAV|INTERACT}_…` 或 `F{编号}_UI_AC{序号}_…`

对每条解析到的 `[PASS]/[FAIL]` 用例：按 it() 名反查所在表，向该行 **`运行结果`** 列写入 `GREEN` / `RED` / `ERROR` / `skipped-compile` / `—`，并附失败原因首行（作为行内备注）。

⚠️ **不要改动 `实现状态` 列**（那是 Step 1 的静态分类标签，跑完后不再更新）。字段语义与取值见 `references/ac-index-format.md`。

#### 5. 写报告

产出**人类阅读版（单文件） + 单问题文件（每问题一文件） + 汇总文件**：

```
docs/
└── dt-verification-report.md            ← 人类阅读版（单文件）

spec/fix/round-{N}/
├── _index.md                            ← 本轮所有问题清单（速览）
├── _summary.md                          ← 统计 + 维度表 + Top 10
├── _delta.md                            ← 与 round-{N-1} 对比（round-1+ 才写）
├── feat/
│   └── <id>.md                          ← 单元测试单问题文件
└── ui/
    └── <id>.md                          ← UI 测试单问题文件

spec/fix/_state.yaml                     ← 全局轻量状态（current_round 等）
```

> **粒度约定**：每个失败 it() / 视觉差异 = 一个独立 markdown 文件，无 SYSTEMIC 聚类（fixer 逐条独立评估，理由见 a2h-fixer.md §5）。

**目录约定与文件 schema 见三份 reference**（必读）：
- `references/report-format.md` — 人类阅读版 + 输出流水线
- `references/fix-file-schema.md` — 单问题文件 schema 权威定义（frontmatter + 5 sections + 状态推导规则）
- `references/fix-file-template.md` — 复制粘贴用模板 + 填法示例
- `references/reconcile-rules.md` — 跨轮 reconciliation + carry forward + delta 生成算法

**核心 invariant**：
- 一个失败 it() / 一个视觉差异 = **一个 markdown 文件**
- 文件名 = ID（ID 推导规则确定性，跨轮稳定）
- **文件存在 ⇔ 本轮该问题为 RED/ERROR/ALIGNMENT_DIFF**；GREEN 不写文件
- round-N 是**本轮快照**，每轮新建独立目录；旧目录保留不动（永久审计）
- 跨轮状态（fixed / regressed / stale）从目录序列推导，不持久化在 frontmatter
- REGRESSED 仅作为 _delta.md 的统计字段，**不再触发回滚**（fixer 通过反向 impact 自检防回归）

**写文件流水线**（按顺序）：

```
1. 跑完 aa test，回写 tdd-ac-index.md 的 运行结果 列
2. 解析 runtime_results: { id → GREEN | RED | ERROR }
3. 读 spec/fix/_state.yaml，取 current_round 作为 N
   （baseline 首跑 → N = 0；autofix 调度 → N 由调用方显式传入）
4. 创建 spec/fix/round-{N}/{feat,ui}/ 目录骨架
5. 对每个 RED/ERROR 的 ID:
   a. 算 layer + path（feat / ui）
   b. 读 round-{N-1}/<layer>/<id>.md（若存在）→ carry forward disposition / related
   c. 拼新 frontmatter + 5 sections（schema 见 fix-file-schema.md）
   d. Write spec/fix/round-{N}/<layer>/<id>.md
6. 生成 _index.md（按 layer 分组列出所有问题，[id title][kind][severity] + 链接）
7. 生成 _summary.md（按维度统计 + Top 10）
8. 若 N ≥ 1 → 计算与 round-{N-1} 的 delta：
   - resolved（上轮存在、本轮不存在）+ stale 区分
   - newly_open（本轮存在、上轮不存在）+ regressed 区分（扫历史轮次）
   - 写 _delta.md（模板见 reconcile-rules.md §四）
9. 更新 spec/fix/_state.yaml（current_round = N，last_verifier_run_at = 当前时间）
10. 写 docs/dt-verification-report.md（人类阅读版，模板见 report-format.md §一）
11. 跑自检（fix-file-schema §十 + reconcile-rules §七）
```

**硬性要求**（缺任一项视为不合格）：

1. 人类阅读版 + `_index.md` + `_summary.md` + 所有失败 ID 的单问题文件全部生成（round-1+ 还要 `_delta.md`）
2. 人类阅读版标注"runtime verified on device" + 设备 ID / bundle / 时间戳 / `aa test` 原始汇总行 + 当前轮次号
3. 人类阅读版**不得**展开逐条 it()；单问题文件**必须**自包含（Spec 引用 + 期望 + 实际 + 源码缺口 + 修复建议）
4. 单问题文件 ID 必须确定性（推导规则见 fix-file-schema §二）；文件名 = ID + `.md`
5. `_state.yaml` 的 `current_round` 必须更新到 N
6. `disposition` 字段必须按 carry forward 算法（reconcile-rules §三）从 round-{N-1} 继承

#### 6. 交付给用户的摘要（≤ 200 字）

- 构建结果
- `Tests run / Failures / Errors` 原始数字
- **Spec 功能覆盖率**（结构维度）：逻辑层 / UI 层 / 总体
- **通过率**（运行维度）：逻辑层 / UI 层 / 总体
- 提示：spec 实际实现 ≈ 覆盖率 × 通过率（两个数都高才算 spec 实现良好）
- Top 5 RED
- 当前轮次号 N
- 输出路径：
  - `docs/dt-verification-report.md`（人类阅读版）
  - `spec/fix/round-{N}/_index.md`（问题清单速览）
  - `spec/fix/round-{N}/{feat,ui}/<id>.md`（每问题一文件，autofix 直接消费）
  - 若 N ≥ 1：`spec/fix/round-{N}/_delta.md`（与上轮对比）

### 禁止项

- ❌ 不允许在未连设备的情况下输出"预测报告"伪装为"运行报告"
- ❌ 不允许把 compile-skip 的用例计入分母（会稀释实现率）
- ❌ 不允许只跑单元或只跑 UI 就出总报告 —— 两类必须都跑

---

## 按范围过滤运行（调试用）

全量跑测由第五步 §2 负责。调试单个 Feature / Page / it() 时可按下表过滤：

```bash
# 单个 Feature（单元测试）
$HDC -t $DEVICE shell aa test -b $BUNDLE -m entry_test \
  -s unittest OpenHarmonyTestRunner -s class F001_MediaScan

# 单个页面（UI 测试）
$HDC -t $DEVICE shell aa test -b $BUNDLE -m entry_test \
  -s unittest OpenHarmonyTestRunner -s class P0002_MainPage_UI

# 单条 it()
$HDC -t $DEVICE shell aa test -b $BUNDLE -m entry_test \
  -s unittest OpenHarmonyTestRunner \
  -s class P0002_MainPage_UI#P0002_UI_SMOKE_page_renders
```

---

## 参考文档

- `references/ac-index-format.md` — AC 索引文件格式、字段说明与使用规则
- `references/test-patterns.md` — 纯函数 / MockKit / UI 测试完整模式与示例
- `references/spec-parsing-guide.md` — Spec 文件 AC 提取规则
- `references/testable-id-catalog.md` — `.id(...)` 命名规范、manifest 格式（Step 2b 必读，Step 3 selector 来源）
- `references/ui-test-antipatterns.md` — UI 测试 False-GREEN 反模式（Step 3 生成必读）
- `references/compile-pitfalls.md` — ArkTS 严格模式 + arkXtest API 编译陷阱（Step 4 必读）
- `references/report-format.md` — 人类阅读版报告模板（Step 5 必读）
- `references/fix-file-schema.md` — 单问题文件 schema 权威定义（Step 5 必读，下游 fixer 共享契约）
- `references/fix-file-template.md` — 单问题文件填法模板 + 三种来源示例
- `references/reconcile-rules.md` — 跨轮 reconciliation + carry forward + delta 算法（Step 5 必读）

---

## 输出清单

完成五步后向用户交付：

1. **AC 索引文件**：`entry/src/ohosTest/ets/test/tdd-ac-index.md` — 全部 AC 的结构化列表（Step 1 产出 + Step 3 追加 + Step 5 回写运行结果）
2. **测试代码**：`entry/src/ohosTest/ets/test/spec/` + `ui/` 下的 `.test.ets` 文件
3. **测试基础设施**：`entry/src/ohosTest/ets/testrunner/` + `testability/` + `module.json5` + 资源（Step 4 产出）
4. **双 HAP 产物**：`entry/build/default/outputs/default/` 和 `ohosTest/` 下 signed HAP（Step 4 产出）
5. **人类阅读版报告**：`docs/dt-verification-report.md`（Step 5 产出）
6. **本轮问题快照**（Step 5 产出）：
   - `spec/fix/round-{N}/_index.md` — 问题清单速览
   - `spec/fix/round-{N}/_summary.md` — 统计 + 维度分布 + Top 10
   - `spec/fix/round-{N}/_delta.md` — 与 round-{N-1} 对比（仅 N ≥ 1 写）
   - `spec/fix/round-{N}/feat/<id>.md` — 单元测试单问题文件（每 RED/ERROR 一个）
   - `spec/fix/round-{N}/ui/<id>.md` — UI 测试单问题文件（每 RED/ERROR 一个）
7. **全局状态**：`spec/fix/_state.yaml`（current_round 等，每轮更新）

---

## 快速检查清单

开始前确认：
- [ ] `spec/baseline/features/` 下有 Feature 文件
- [ ] `spec/baseline/ui/` 下有页面规格（UI 测试需要）
- [ ] 设备已连接：`$HDC -t $DEVICE list targets`
- [ ] 包名和设备 ID 已配置在环境变量中

第一步完成后确认：
- [ ] `entry/src/ohosTest/ets/test/tdd-ac-index.md` 已生成，每条 AC 都有 `类型`、`实现状态`、`运行结果` 三列
- [ ] 所有行 `运行结果` 列初值为 `—`（仅 Step 5 可写）
- [ ] unit AC 总数与 Spec `- [ ]` 数目一致

执行后确认：
- [ ] 编译无报错
- [ ] 至少 50% 用例已运行（没有全部 skip）
- [ ] 准确率抽查 ≥ 90%
