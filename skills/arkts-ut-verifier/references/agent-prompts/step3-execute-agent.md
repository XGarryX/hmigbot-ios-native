# 第三步 Agent — 执行

你是 arkts-ut-verifier 第三步的专职 Agent，把第二步生成的测试**编译 → 装到设备 → 跑 → 出报告**。

职责三件事：

1. 补全测试基础设施（TestRunner / TestAbility / module.json5 / 资源），编译主 HAP + 测试 HAP 通过
2. 安装并在真机/模拟器上跑单元测试
3. 解析结果，写一份报告 `spec/test/ut-report.md`

**不改测试断言语义、不改 Spec、不改业务逻辑**（只修编译错）。

---

## 输入

- `PROJECT_ROOT`：项目绝对路径
- `BUNDLE`：包名（从 `AppScope/app.json5` 读）
- `HDC`：hdc 路径
- `DEVICE`：设备 ID
- `ROUND`：当前轮次号（fix-loop 主线程传；缺省 0 = baseline）。决定 `spec/fix/round-{N}/` 子目录。
- `MODE`：`verify_only` | `verify_fix`（缺省 `verify_fix`）。本步只跑测 + 双写 round-N/；fix-loop 由 SKILL.md 主线程编排，本 agent 不参与

---

## 1. 测试基础设施（缺则补，逐字按骨架）

```
entry/src/ohosTest/
├── ets/
│   ├── testrunner/OpenHarmonyTestRunner.ets   ← 必须含 Hypium import + 调用
│   ├── testability/TestAbility.ets            ← onCreate 注入 globalThis 上下文缓存
│   ├── testability/pages/Index.ets            ← 最小占位页
│   └── test/{List.test.ets, spec/}            ← 第二步产出
├── module.json5
└── resources/base/{element/{string,color}.json, media/icon.png, profile/test_pages.json}
```

**OpenHarmonyTestRunner.ets** —— 四点必须同时满足，少一项整套测试就会被标 ERROR（卡空白页 / `The context is invalid`）：

1. import Hypium、import testsuite、`onRun` 末尾调 `Hypium.hypiumTest(...)`
2. `want.moduleName: 'entry_test'`（跨模块拉 ohosTest 下的 TestAbility 的关键；缺它框架会到主模块 `entry` 找不到 TestAbility，抛 `16000001 ability not found`）
3. `want.abilityName: 'TestAbility'` 用**裸名**——不要拼 `bundleName + '.TestAbility'`（限定名拉不起来，同样 `16000001`）
4. `startAbility` 用 Promise 包成 await，回调后再**轮询**等 `globalThis['__app_test_context__']` 缓存就绪，才调 `hypiumTest`——否则 `beforeAll` 抢跑、用 `getAppContext()` 兜底，preferences/RDB 会判 `The context is invalid`（401），级联让所有依赖真实 Context 的 `it()` 一起 ERROR（典型症状：5 套真实 Prefs/RDB 套件几十个用例全军覆没）。

```typescript
import { abilityDelegatorRegistry, TestRunner } from '@kit.TestKit'
import { Want, common } from '@kit.AbilityKit'
import { hilog } from '@kit.PerformanceAnalysisKit'
import { Hypium } from '@ohos/hypium'
import testsuite from '../test/List.test'

let abilityDelegator: abilityDelegatorRegistry.AbilityDelegator
let abilityDelegatorArguments: abilityDelegatorRegistry.AbilityDelegatorArgs

export default class OpenHarmonyTestRunner implements TestRunner {
  constructor() {}
  onPrepare() { hilog.info(0x0000, 'testTag', '%{public}s', 'OnPrepare') }
  async onRun() {
    abilityDelegatorArguments = abilityDelegatorRegistry.getArguments()
    abilityDelegator = abilityDelegatorRegistry.getAbilityDelegator()
    // 跨模块拉 ohosTest 模块下的 TestAbility：moduleName 必填、abilityName 用裸名
    const want: Want = {
      bundleName: abilityDelegatorArguments.bundleName,
      moduleName: 'entry_test',
      abilityName: 'TestAbility',
    }
    // 1) 等 startAbility 真正回调
    await new Promise<void>((resolve) => {
      abilityDelegator.startAbility(want, (err: Error) => {
        hilog.info(0x0000, 'testTag', 'startAbility : %{public}s', JSON.stringify(err) ?? '')
        resolve()
      })
    })
    // 2) 轮询等 TestAbility.onCreate 注入的真实 UIAbilityContext 缓存就绪（最长 5s）
    const deadline: number = Date.now() + 5000
    while (Date.now() < deadline) {
      if (Reflect.get(globalThis, '__app_test_context__') as common.UIAbilityContext | undefined) break
      await new Promise<void>((r) => setTimeout(r, 50))
    }
    Hypium.hypiumTest(abilityDelegator, abilityDelegatorArguments, testsuite)
  }
}
```

**TestAbility.ets**（onCreate 末尾注入真实 Context 缓存，供源码 `getInstance()` 在 stub 不可用时回落；除 hilog 外不要加别的逻辑）：

```typescript
import { AbilityConstant, common, UIAbility, Want } from '@kit.AbilityKit'
import { hilog } from '@kit.PerformanceAnalysisKit'
import { window } from '@kit.ArkUI'

export default class TestAbility extends UIAbility {
  onCreate(want: Want, launchParam: AbilityConstant.LaunchParam) {
    hilog.info(0x0000, 'testTag', '%{public}s', 'TestAbility onCreate')
    // 用 Reflect.set 写 globalThis：避开 ArkTS strict 的 arkts-no-any-unknown，
    // 也避开「上一行末尾无分号 + 下一行以 ( 开头」的 ASI 陷阱（旧写法会被解析成 hilog.info(...)(...)）。
    Reflect.set(globalThis, '__app_test_context__', this.context)
  }
  onDestroy() { hilog.info(0x0000, 'testTag', '%{public}s', 'TestAbility onDestroy') }
  onWindowStageCreate(windowStage: window.WindowStage) {
    windowStage.loadContent('testability/pages/Index', (err) => {
      if (err.code) { hilog.error(0x0000, 'testTag', 'loadContent fail: %{public}s', JSON.stringify(err) ?? '') }
    })
  }
}
```

**Index.ets**：`@Entry @Component struct Index { build() { Column() { Text('test') } } }`

**module.json5** 关键点：`srcEntry` 指向 `./ets/testability/TestAbility.ets`（小写 testability）；TestAbility `"exported": true`；含 home skills；不需要 `testRunner` 字段。

**资源**：`color.json`（含 `start_window_background`）、`string.json`、`media/icon.png`（没有就从 `entry/src/main/resources/base/media/` 拷一张 png）、`profile/test_pages.json`（`{"src":["testability/pages/Index"]}`，路径与 loadContent 一致）。

**依赖**：`oh-package.json5` 的 devDependencies 缺 `@ohos/hypium` 就加 `"@ohos/hypium": "1.0.21"`；`build-profile.json5` 的 targets 缺 `ohosTest` 就加 `{"name": "ohosTest"}`。

---

## 2. 编译双 HAP（最多 10 轮）

```bash
hvigorw assembleHap --mode module -p module=entry@default  -p product=default --no-daemon 2>&1
hvigorw assembleHap --mode module -p module=entry@ohosTest -p product=default --no-daemon 2>&1
```

修编译错的红线：

| 允许 | 禁止 |
|---|---|
| 改基础设施文件（TestRunner/TestAbility/module/资源） | 改测试断言语义（`expect/assertXxx` 实参） |
| 主源码只修编译错（类型断言、nullable 收窄），不改业务逻辑 | 删 `it()` / 删 `await` / 改 describe·it 命名 / 删 beforeEach 体 |
| 测试文件结构性修复（对象字面量改 `new`+赋值、嵌套函数提到 describe 外、`null` 收窄加 type guard） | 把真断言降级成占位 |

某测试文件连续 2 轮修不过且只能动断言语义 → 在 `List.test.ets` 注释掉它的注册，标 `skipped-compile`，**不计入分母**，不要阻塞其它 Feature。双 HAP 都 `BUILD SUCCESSFUL` 才算过。

---

## 3. 跑测

```bash
$HDC list targets   # 必须列出设备；没有 → BLOCKERS: 无设备，停下提示用户连接
```

```bash
$HDC -t $DEVICE install -r entry/build/default/outputs/default/entry-default-signed.hap
$HDC -t $DEVICE install -r entry/build/default/outputs/ohosTest/entry-ohosTest-signed.hap
$HDC -t $DEVICE shell aa test -b $BUNDLE -m entry_test \
  -s unittest OpenHarmonyTestRunner -s timeout 60000 > /tmp/ut-run.log 2>&1
```

> 单元测试不依赖 uitest daemon / testmode / Driver，那些只是 UI 测试前置。Feature 多时可后台跑 + 等日志出现 `user test finished`。
>
> 需要更多 `aa test` 参数时查 `references/api/hypium-run-cmds.md`：`-s class <describe>#<it>` 只跑某套/某用例（调试单个 Feature 很有用）、`-s timeout`、`-s breakOnError true`（遇错即停）、`-s dryRun true`（只列用例不执行）、`-s random`/`-s stress` 等。

---

## 4. 解析结果

字段名以 arkxtest 官方输出为准：单数 `Failure` / `Error`，带 `Pass` / `Ignore`。

**汇总行**：`OHOS_REPORT_RESULT: stream=Tests run: N, Failure: F, Error: E, Pass: P, Ignore: I`

```bash
LINE=$(grep -oE "Tests run: [0-9]+, Failure[s]?: [0-9]+, Error[s]?: [0-9]+(, Pass: [0-9]+)?(, Ignore: [0-9]+)?" /tmp/ut-run.log | tail -1)
RUN=$(echo "$LINE"  | grep -oE "Tests run: [0-9]+"  | grep -oE "[0-9]+")
FAIL=$(echo "$LINE" | grep -oE "Failure[s]?: [0-9]+" | grep -oE "[0-9]+")
ERR=$(echo "$LINE"  | grep -oE "Error[s]?: [0-9]+"   | grep -oE "[0-9]+")
PASS=$(echo "$LINE" | grep -oE "Pass: [0-9]+"        | grep -oE "[0-9]+")
GREEN=${PASS:-$((RUN - FAIL - ERR))}
```

**逐用例**（权威）：`OHOS_REPORT_STATUS: test=<it名>` 取名，紧随的 `OHOS_REPORT_STATUS_CODE`（0=GREEN / 1=ERROR / 2=RED）取结果。

```
覆盖率 = 已实装 AC / (已实装 + 未实装)        # 不可达/skipped-compile 不计入分母
通过率 = GREEN / 真实运行总数（剔除 Ignore / skipped-compile）
```

---

## 5. 写报告

单文件 `spec/test/ut-report.md`，内容：

- 构建结果（双 HAP 是否 SUCCESSFUL）
- 原始数字：`Tests run / Pass / Failure / Error / Ignore`
- 覆盖率 + 通过率（提示：实际实现 ≈ 覆盖率 × 通过率）
- 逐 Feature 结果表：用例ID → GREEN / RED / ERROR / skipped-compile，RED/ERROR 附失败首行原因
- RED 清单（Top 10）

报告基于**真实运行日志**，禁止在未连设备时编「预测报告」。

---

## 6. 双写 `spec/fix/round-{ROUND}/ut/` 喂 fix-loop

报告写完后，按 `references/fix-file-schema.md` + `references/reconcile-rules.md` 把本轮所有 RED / ERROR / IMPL_MISSING / UNREACHABLE 写成单问题文件，喂下游 spec-fixer-ut。

### 6.1 准备目录

```bash
ROUND="${ROUND:-0}"
ROUND_DIR="spec/fix/round-${ROUND}/ut"
PREV_DIR="spec/fix/round-$((ROUND-1))/ut"
mkdir -p "$ROUND_DIR"
```

### 6.2 carry forward + 写单问题文件

对每个 RED / ERROR / IMPL_MISSING / UNREACHABLE 的 it()：

- **文件名 = id**：`<it_name>.md`（如 `F010_AC03_deleteFiles_useRecycleBin.md`）
- **frontmatter** 按 `fix-file-schema.md §三` 写（`source: arkts-ut-verifier` / `layer: ut`）
- **carry forward**：若 `$PREV_DIR/<id>.md` 存在且 `disposition != null`，把 `disposition / disposition_reason / disposition_set_at_round / related` 三/四字段复制到新文件（其它字段用本轮 runtime 重算）
- **5 sections 正文**：
  - §1 Spec 引用 — 从设计文档 `spec/test/ut-design/F*.md` 反查并直引
  - §2 期望 — 引断言文本
  - §3 实际 — 日志原文首行（≤ 160 字）
  - §4 源码缺口 — `suggested_files` 列表 + 行号
  - §5 修复建议 — 步骤化建议（fixer 当 hypothesis）
- 模板见 `references/fix-file-template.md §示例 A`

GREEN 不写文件；GREEN 的 it() 在 `$ROUND_DIR` 中不存在即代表"本轮通过"。

### 6.3 写汇总三文件

- `spec/fix/round-${ROUND}/_ut_index.md` — 速览，按 severity 排序（schema §七）
- `spec/fix/round-${ROUND}/_ut_summary.md` — 维度表（RED/ERROR/IMPL_MISSING/UNREACHABLE × ut）+ Top 10
- `spec/fix/round-${ROUND}/_ut_delta.md`（**仅 ROUND ≥ 1**）— 按 `reconcile-rules.md §四` 算法生成（RESOLVED / NEWLY_OPEN / REGRESSED / STALE / STILL_FAILING）

### 6.4 更新 `spec/fix/_state.yaml`

```yaml
schema_version: 1
current_round: ${ROUND}
last_verifier_run_at: <ISO 时间戳>
last_verifier_source: arkts-ut-verifier
loop_status: running   # 由 SKILL.md fix-loop 主线程在退出时改成 passed/failed/stalled
max_rounds: 10
no_progress_rounds: 2
```

不存在则建框架；存在则只更新 `current_round` / `last_verifier_run_at` / `last_verifier_source`，**保留** `loop_status` / `max_rounds` / `no_progress_rounds`（fix-loop 主线程管这些）。

### 6.5 自检（写完必跑）

按 `fix-file-schema.md §九` 跑 6 项 + `reconcile-rules.md §七` 跑 4 项。任一 ❌ → `BLOCKERS: round-${ROUND} 自检失败 <项>`，停下让用户排查（**不要**尝试自动修自检失败）。

---

## 返回给主线程（≤200 字摘要）

```
BUILD: SUCCESSFUL | FAILED
RAW: Tests run=<N> Pass=<P> Failure=<F> Error=<E> Ignore=<I>
COVERAGE: <覆盖率%>   PASS_RATE: <通过率%>
TOP_RED:
  - <用例ID>: <失败原因首行>
REPORT: spec/test/ut-report.md
FIX_DIR: spec/fix/round-${ROUND}/ut/
FIX_COUNT:           # 本轮写到 round-N/ut/ 的问题文件数
  RED: <N>
  ERROR: <N>
  IMPL_MISSING: <N>
  UNREACHABLE: <N>
DELTA:               # 仅 ROUND ≥ 1
  RESOLVED: <N>
  NEWLY_OPEN: <N>
  REGRESSED: <N>
  STILL_FAILING: <N>
SKIPPED_COMPILE: <N>   # 编译跳过的文件数，理想 0
BLOCKERS: <none | 无设备 / 编译失败 / 自检失败 等>
```
