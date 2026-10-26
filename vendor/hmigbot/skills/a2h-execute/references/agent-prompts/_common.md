<!-- when: 派发任何 converter / worker subagent 时【始终随读】——所有 agent-prompts/N-*.md 的公共前置 -->
<!-- topics: 占位规则 §2.1, 6 类 kind, HANDOFF 移交, Stage 3 单写者纪律, forward-ref -->

# 子代理派发 prompt — 公共规则（所有派发点必读）

> 本文件是 `agent-prompts/` 下各单段 prompt（`1-converter.md` … `8-group-closer.md`）的**公共前置规则**。
> 派发任一 worker 时，**先 Read 本文件 + 对应单段文件**两个即构成完整派发规范——不必再读其它段。

## §2.1 占位延迟分类法（所有派发点统一遵循）

合法占位 = 已登记的 **6 类 kind** 占位：
- `// FWD-REF:` → forward-ref / resource-pending-asset
- `// PLACEHOLDER:` → thirdparty-sdk
- 已登记 `// TODO:` → forward-ref-uncertain
- 资源 `[TODO: translate]` → resource-pending-translation
- **`// HANDOFF:` → handoff（把责任移交给另一个 skill / 另一处调用点，见 §2.1b）**

**未登记 / 自由文本一律 FAIL。**

### §2.1b `// HANDOFF:` —— 责任移交必须带机械断言

<HARD-GATE>

**什么时候用**：你的代码**结构完整、编译通过**，但你知道它要靠**别处**才算真正完成 —— 典型两类：

1. **交给另一个 skill 处理**（如"尺寸交 icon-sizing 自愈"）
2. **交给另一处调用点**（如"由启动序列在 EntryAbility.onCreate 调 setDebug()"）

**为什么必须机械化**（AIPPT 2026-07 两次真实事故，同一根因）：
- `// ...固有尺寸交 icon-sizing 自愈` → 那轮 icon-sizing 根本没跑 → 图标撑满父容器，整页塌陷
- `// 由启动序列在 EntryAbility.onCreate 调 setDebug()` → 没人调 → release 正则拦掉测试账号，登录不通

两处**都写了注释**，但注释是**散文**：skeleton / wiring / dangling-fwd-ref 全查不出（代码结构本就完整），编译 / 结构审计 / 债务闸 / 终态编译四道门**一致放行**，只有真机跑才暴露。

**形态**（`verify=` 必填，缺了直接 FAIL）：

```
// HANDOFF: owner=<谁负责> what=<做什么> verify=<断言>
```

**三种断言，都由 `verify_closure_ledger.py` 在 pipeline 末尾机械对账**：

| 断言 | 语义 | 用于 |
|---|---|---|
| `grep:<正则>` | 全工程 `.ets` 必须存在匹配（marker 行自身不计，防自证） | 启动期初始化、跨文件调用点 |
| `artifact:<文件>#<字段>` | 产物存在且该字段非空/非零（文件名可不带路径，自动取 `spec/execution/autofix-log/` 下最新同名（旧项目 docs/autofix-log 兜底）） | 委托给别的 skill 自愈 |
| `slice:<N>` | 归属切片；该切片终态仍未兑现 → GAP(FAIL) | 业务接线（等价 FWD-REF） |

**示例**：
```ets
// HANDOFF: owner=arkts-icon-sizing what=补图标尺寸 verify=artifact:icon-pipeline-iter1.json#fixed_count
Image($r('app.media.icon_mine_right_arrow'))

// HANDOFF: owner=EntryAbility.onCreate what=调setDebug verify=grep:HttpLog\.setDebug\(
static setDebug(value: boolean): void { ... }
```

**判定**：断言成立 → INFO；不成立 → **FAIL**（`ledger-handoff-unmet`）；无 `verify=` → **FAIL**（`ledger-handoff-no-assertion`）。

⚠️ **不要用散文替代**。"待接入 xxx 后替换"、"由 xxx 负责"这类注释若不写成本 marker，等于把缺陷交给运气。

</HARD-GATE>

### §2.1c P-ID 发号协议（所有铸号者——converter / worker / closer / repair）

<HARD-GATE>

1. 前缀 = slice 命名空间：`P-S{N}-{seq}`（converter 用页面 `owning_slice` 的 Slice 编号；Base 任务 `P-B{N}-{seq}`）；禁止自造前缀。
2. registry 唯一发号处，**登记即占号**：写 marker 前先向 `spec/placeholder-registry.md` append 该行（6 字段齐全）。
3. 发号前 `grep "P-S{N}-"` 取本前缀 max seq，新号 = max+1。

</HARD-GATE>

## 单写者纪律（全 Stage 无条件；Stage 3 任意组大小含 size-1 组）

Stage 1 converter 同样只写自身页面文件，享受同样两项 append-only 例外；batch-closer 对资源仅残量兜底。

Stage 3 一律以 parallel_group 为粒度执行，`5-step3b-vm.md` / `6-step3c-data.md`（§4/§5/§6）的 slice worker **只写自身 page / VM / repository 文件**，**禁止编辑共享文件**（包含但不限于 `spec/baseline/plans/feature-plan.md`）。`7-step3d-wiring.md`（§7）Step 3d 的**跨文件接线**一律移交 **`8-group-closer.md`（§8）group-closer** 统一单写；slice worker 只接自身页内的 VM/handler。

**仅两项 append-only 例外**（其余共享文件仍绝对禁碰）：
1. `spec/placeholder-registry.md` 的 **P-ID 登记行 append**（§2.1c 发号协议——登记即占号）；
2. **共享资源 JSON 直写**（见下方资源直写纪律）。

**plan 产物只读**：feature-plan.md 索引与 `plans/slices/` 文件生成后只读——任何 agent 不得回填 checkbox / evidence / 状态（完成性 = verify_slice_wiring 机械判定 + brief 记录）。**拆分越界禁令**：按依赖断面拆分派发的 worker（§5a 安全阀）只写划给自己的文件集，禁碰兄弟 worker 文件。

## 资源直写纪律（converter / worker）

共享资源 JSON（`color/string/float.json` 等）允许直写，仅限：写前 Read 最新文件、只 append 缺失键（禁重排 / 重写 / 删除既有条目）；键已存在即复用。冲突由 closer 编译门自曝。

## 返回报告信封契约（所有 agent）

判据：主线程是否据此做分支决策？是 → 进报告；否 → 落 brief / 产物文件，报告只留指针。
- 最终报告 = 结构化信封 ≤30 行：状态枚举、计数、失败项（仅 ID/路径）、产物与 brief 路径、≤3 条短句风险。
- 禁止粘贴：逐文件清单全文、evidence 明细、资源核对清单、修复叙述、build 日志、dispatch_prompt 全文（一律以路径传递）。
- 各单段 prompt 的"返回报告必须含"即信封字段；超出部分写对应 brief（落 `spec/execution/briefs/`；**closer 的 brief 与账本变更经 writeback manifest 由主线程 apply 落盘**，turn 内不直写——协议见 a2h-closer 定义）。

## 校验性读取纪律（grep-first，所有 agent）

作者性读取不受限（spec / anchors 源码 / 快照 / 自己要改的文件）。校验性读取一律 grep 定位 + 窗口读：
- 查页面状态 / 复用组件：grep ui-manifest 对应行（禁整读、禁扫 components/ 目录）
- **白名单例外（设计令牌）**：`ui-manifest.md` 的 `## 全局约定` 节**允许整节读**（`sed -n '/^## 全局约定/,/^## /p'`，通常 ≤20 行），任何产出 UI 代码的 agent（converter / Step 3a / fixer）**必须**在写样式前读取本节。理由：设计令牌（主色 / 主题 / 排版 / 图标方案）是 Android 侧样式真值的唯一落点，被 grep-first 挡在生成现场之外会导致主题色、字号、间距整体丢失，或诱发自创平行令牌体系（历史事故：DiceRoller 主题紫全丢、AIPPT 自创 `DesignTokens.ets` 架空 `float.json`）
- 查占位：按本 slice 前缀 `grep "P-S{N}-"` registry
- 定位 marker / handler / @Builder 槽位：grep 后 Read ±30 行窗口，禁整读 .ets

## impl: 指针语义（Step 3b / 3c worker 定向精读 addenda）

feature spec `## 验收标准` 的 `###` 组标题（或单条 AC）尾部 `impl: <addendum>.md §<节>` = 该组实现细节的权威归宿（组级默认、单条覆盖、多目标逗号分隔；addendum 位于 feature spec 同目录）。worker 实现某 AC 组前：

- 该组带 `impl:` 且目标 addendum 的 `consumed_at`（frontmatter，缺省按 a2h-spec C4-pre 第 5 项 slug 默认表：state-machine/races/lifecycle→3b，api/persistence→3c，mapping→随组）匹配本步骤 → **按标题 grep 目标 §节精读**（`grep -A 40 "<节标题>" <addendum 路径>`），随 spec / 源码一并纳入理解
- **禁止整目录扫读 addenda**；每次派发精读 **≤3 节 / 总量 ≤150 行**，超出按 AC 组顺序取前 3、其余写入返回报告 `deferred_addenda` 字段
- AC 断言本身以主文件为准（指针不转移断言）；无指针的组照旧只依据主文件


## 策略决策 ≠ 免除装配义务（压舱条款，两次实录后 HARD）

ledger 里「显式失败 / 禁止伪成功 / fail-closed」类**错误处理策略**只约束**失败路径语义**
（失败时不许假装成功、不许静默吞错），**不得外延为架构级拒绝服务**：

- **禁止**把「未配置/未 hydrate/未登录」实现成「守卫直接 throw、功能整片不可用」——
  行为基线永远 = Android 侧可观察行为（例：Android 未登录时 token=空串**照样发请求**，
  由服务端返回未登录态；那 HarmonyOS 也必须如此，而不是端上先抛"未配置"）。
- 任何 fail-closed 守卫骨架（ready 标志 + 未就绪即 throw + 装配方法）**必须在启动组装根
  真实接线**（实例化 + 调装配方法 + 接到消费方）；写完守卫不装配 = P0
  （structural-closure pipeline 的 assembly_gate 会 FAIL，修法是补调用点，不是删守卫）。
- 事故实录：D-022（AIPPT 0821）"fail-closed 可重试"被读成不装 ApiClient → 登录/模板全灭；
  D-012（aippt_codex_v2 0823）"显式失败"被读成 NetworkRuntimeState 未 hydrate 即抛 →
  模板加载不出/登录不可用/H5 空白/组件点不动，四症状同源。

## 能力交付契约（组装根收货制，2026-08-24 起）

- 全工程唯一组装根 `AppAssembly.ets`（closer 单写）：`capabilityTable` 直接对象字面量逐键收货；
  含 hydrate/install 族装配方法的能力经 `installCapabilities(ctx)` 在 EntryAbility.onCreate 装配。
- **消费方一律从组装根取依赖；组装根之外禁止 `new` 槽位类**——"表里喂一个实例、
  自己另用一个"的装饰性登记 = capability_ledger_gate FAIL。
- **废止 Unavailable*/Noop*/空对象占位模式**：能力不可用的唯一合法表达 = 槽位缺席 +
  registry P-ID（kind=handoff）绑 D-编号且该 D 点名此键。写一个"类型正确但全 throw/
  返回假值"的类塞槽 = stub-in-slot FAIL（定义闭包 lint，藏到别的文件一样抓）。
- 键集是机械生成闭集（plan 产物派生），不接受"我认为这个能力不算"的现场裁量；
  对键集有异议 → 回 plan 修正来源产物，不改表。

## 显隐绑定铁律（「我的」页四按钮消失事故后 HARD，CC/CX 同病实录）

安卓的条件显隐（`xxx.visibility = when(config.field)…` / XML `android:visibility="gone"`）
迁移时三条硬规矩：

1. **默认极性 = 安卓默认**。条件渲染开关的初始值必须照抄安卓侧默认行为
   （XML 无 visibility 属性 = 默认可见 = 初始 true；显式 gone = 初始 false）。
   **禁止用 fail-closed 本能选 false**——绑定债两侧都可能欠，初始值忠实的欠了债
   用户看不出，反极性的欠一笔债就丢一块界面（showServiceCenter=false 实录）。
2. **声明即接线**。声明了条件渲染开关（@Local/@State boolean + if 渲染），必须
   同步写赋值链（从模型/store/config 到组件）——binding_gate 的 dead-render-flag
   会把零赋值开关判 FAIL（默认 false）/ WARN（默认 true）。
3. **逐条核销清单**。`spec/baseline/ui/visibility-bindings.json`（spec 期从安卓源
   抽取的显隐绑定真值账）里本页的 runtime-toggle 条目必须逐条有对应实现——
   数据驱动名零出现 = binding-dropped FAIL。确属决策批准砍掉的（如 D-010 渠道
   unavailable），登记 P-ID 留痕，不许静默丢。

## ArkUI 布局语义铁律（.align 误用事故后 HARD，60 处实锤）

`.align()` 只对齐**组件自身内容**，**不定位 Stack 子项**——安卓 FrameLayout gravity
直觉直接迁移是错的（实录：搜索图标叠在标题正中、「立即生成」按钮浮到卡片顶部遮内容，
aippt_codex_v2 全 app 60 处）。FrameLayout gravity 的合法映射只有三种：

1. 全部子项同向 → `Stack({ alignContent: Alignment.X })`
2. 逐子项异向 → `RelativeContainer` + `alignRules`
3. 标题栏左中右 → `Row` + 两端对称占位块（保持中间真居中）

`.align()` 的唯一合法场景：子项已撑满（`layoutWeight(1)` / `height('100%')`）后
钉自身内容。转换含 FrameLayout/层叠布局的页面前 **MUST `$arkts-ui-alignment`**
读 references/layout-mapping.md（binding_gate 的 stack-align-misuse 会机械拦截误用）。