# 安卓 oracle 采集协议（step0 与 step1 共读）

> **本协议项目无关。** 不硬编码任何仓名 / 目录嵌套 / 模块根 / 计数。所有结构在运行时由
> `scripts/android-oracle.sh` 以「锚点 path 后缀匹配」发现 —— 单层/双层嵌套/monorepo/扁平布局都成立。
> 文中出现的具体类名（如 `FDBrushType`）仅为**示例**，换任何 Android→HarmonyOS 迁移项目协议不变。

## 0. 为什么要这一步（确认 Android 实际行为）

spec `## 验收标准` 是粗粒度散文（"10 种笔刷全部可选"、"按时间倒序兜底"），**缺 UT 真正要的具体值**：
枚举数值、proto 字段+wire tag、算法输入→输出、完整集清单、golden 字节。这些在 spec 正文里**不存在**。
但 spec frontmatter 已带 `android_source_anchors`（指向安卓实现的锚点），这是现成但**此前未接通**的 oracle 通道。
step0 的职责：从锚点出发自探索到安卓真正的实现，把行为分支、状态变化、副作用及具体值抽成一张**机读 oracle 表**，
供设计、生成与修复使用。Android 源码实际行为是迁移功能点完善、修改、新增实现与测试预期的依据，不能仅凭 Spec 散文推测业务。

## 验证范围（SKILL.md 与 ut-report.md 保持一致）

> **android-oracle 提供行为与预期依据，不自动增加已执行的调用链。**
> 渲染与 UI 交互不属于本 skill；跨模块逻辑和可从 ArkTS 调用的系统/native 接口，应按真实入口、环境与可观测结果判断可测性，不能一概判不可达。
> 被 mock 的依赖行为未获真实验证；`golden-degraded` 项**不等于已覆盖**。
> 加密/运行时常量的真值静态拿不到是**结构性缺口**，step0 缓解但不能消除。
> `partial` 表示部分预期值尚未取得，应列明缺口；不能据此推定已采集的预期值或真实执行证据失效。

## 1. 职责边界（一句话）

- **Spec 管 Feature 范围、AC 追溯与明确批准的平台差异**，只读；缺失即终止。Spec 的概述、遗漏或猜测不能自行变成 Android 没有的业务要求。
- **Android 源码实际行为管范围内的行为与预期**：包括分支、输入输出、状态变化、副作用、枚举完整性和具体值；已核验且仍适用的证据可复用。
- 初次生成与 fixer 后续更新/新增测试使用同一强断言标准，见 [fixer 测试更新策略](fixer-test-policy.md)。缺少证据时保留待核验项，不编预期、不放宽断言凑绿。

## 2. ANDROID_SOURCE_ROOT（调用方提供，不硬编码）

- 由 env `ANDROID_SOURCE_ROOT` 传入（指向被迁移的安卓源码仓根）。**skill 不假设它在哪。**
- 缺失 / 不可达 → step0 整体 `SKIPPED` 并记录原因；可继续设计盘点和执行已有有效测试，复用已核验且仍适用的 Android 证据。受影响且缺证据的行为/预期标 `needs_review`、未验证，不能退回猜测 Spec 的自动实现或测试生成。
- 发现提示（非强制）：安卓源常与鸿蒙仓平级、目录名含 `_android` 或同名工程；但**一律由调用方确认**，协议不写死路径。

## 3. 锚点解析（确定性，交脚本，不靠 LLM 算路径）

spec frontmatter `android_source_anchors` 有两种形态，解析适配层都要兼容：
- **list-style**：`- role: <角色>` + `path: "<相对模块根的路径>"`
- **map-style**：`<role>: <FQCN 或 相对 path 列表>`

对每个锚点 path，调用：
```bash
scripts/android-oracle.sh resolve "$ANDROID_SOURCE_ROOT" "<锚点path>" ["<FQCN或包路径提示>"]
```
返回首列状态：
- `OK` / `OK_SUFFIX`：命中（后缀匹配，**布局无关**，无需知道嵌套几层）。
- `DRIFT`：锚点 path 中段漂移，靠 basename 兜底命中（记 drift，仍可用）。
- `AMBIGUOUS`：同名多命中且无包名提示 → **必须用 role/FQCN/包路径消歧，禁止取首个**；无法消歧标 `ambiguous-unresolved` 交人工。
- `MISS`：anchor 解析不到 → **不要停在这里**，进 §3.1 发现阶梯主动搜索补回。

## 3.1 ★目标发现阶梯（信息缺失时**主动搜索补回**，不消极 SKIP）

**核心原则：anchor 只是「第一跳线索」，不是硬依赖。** 无 anchor / anchor 全 MISS / 自探索断链时，
**必须主动去安卓仓搜索把实现找回来**，而不是退回 spec 散文了事。逐级降级，命中即停：

1. **L1 anchor 路径** —— `resolve`（后缀匹配，§3）。
2. **L2 basename + 包名消歧** —— `resolve` 内置（drift 恢复）。
3. **L3 符号定义搜索（最强）** —— 迁移工程**鸿蒙类名常沿用安卓类名**。拿「spec 提到的类型名」或「鸿蒙被测符号名」直接搜安卓定义：
   `scripts/android-oracle.sh find-sym "$ANDROID_SOURCE_ROOT" <SymbolName> [class|enum|object|fun]`。
   支持 Kotlin/Java 类型与方法声明候选，包括常见 Kotlin 扩展/泛型函数；读取命中上下文确认声明、重载与包名，不能把文本候选当语义解析证明。
4. **L4 鸿蒙侧溯源反查** —— 读**鸿蒙被测源码**的溯源注释（`// 溯源 Android XxxKt` / `对应 Android …` / `FD* 同名`），
   拿到它声称的安卓来源符号，回 L3 `find-sym` 搜。
5. **L5 关键词全仓发现** —— `grep-kw "$ANDROID_SOURCE_ROOT" <Feature名/关键词正则> 8`（按命中行数排序取前 8 个 Kotlin/Java 非测试源文件，覆盖 main/debug/commonMain 等 source set）。
6. **L6 现成单测反查** —— `tests "$ANDROID_SOURCE_ROOT" <关键词>`：安卓单测文件名/内容常直接点出被测的类与算法。

搜索后端为同目录 `android_source.py`，需 Python 3。`find-sym/grep-kw` 排除测试源；三类搜索均排除 `.git/.gradle/.idea/build/out/generated/node_modules/vendor/third_party` 目录。`tests` 在 test、androidTest、testDebug、commonTest 等测试 source set 内查 `.kt/.java`，关键词按路径或内容字面量匹配，不再要求文件名以 Test 结尾。输出的是测试源文件候选（可能含 helper/fixture），须阅读真实测试注解/断言后才能复用 IO；不会替你执行 Android 测试。被排除的外部源码确有明确锚点时按该锚点只读核查。MISS/空候选只表示本次扫描未命中，须报告扫描范围，不能证明实现或测试不存在。

**终止状态（L1–L6 全落空才标，且绝不臆造）**
- `spec_only(no-android-impl)`：在已记录的搜索范围内未找到实现，可能是源码残缺或确实不存在；显式记录证据与原因，不能据此批准新增业务。
- 某条 oracle 链断（找到类但叶子值拿不到）→ 该项标 `unresolved`，受影响设计行标 `needs_review`，**不编值**。

> 🔴 **缺失即诚实降级，绝不臆造**：anchor/代码找不到时，该 oracle 项**绝不能**变成 LLM 猜的硬编码值。
> 标 `unresolved`/`spec_only(no-android-impl)`/`golden-degraded` 并保留缺口；禁止以 Spec 猜测、非空、条数大于零或其他弱断言替代未知预期。
>
> **护栏**：发现阶梯整体仍受 `FILE_BUDGET=12` / 每 Feature `ROUND≤2` 约束；L3/L5 搜不到就走下一级，全失就诚实降级，**不无限搜**。

## 4. 自探索协议（锚点是链头，oracle 在 1–3 跳外）

锚点多指向「页面级编排类」（Activity/Fragment/ViewModel/Manager），真 oracle 在它引用的模型/算法里：

1. 在锚点文件 `grep` 出引用的类型/常量/管理器（迁移工程常见前缀如 `FD*` / 项目自有前缀）。
2. 跟 import 路径跳到定义文件（用 `resolve` 或 `grep -r "class X"`）。
3. **落叶子**：`enum class` 成员 / `data object` 的 value / `data class` companion 默认值 / `when(this) -> 具体值`（算法 I-O） / `writeTo`-`parseFrom`（wire）。
4. value 又指向另一个常量 → 再跳一跳；每跳记溯源链 `file:line`。
5. **HOP_LIMIT=3**（经验值，够用）；跨多仓 / 算法链长的 Feature 允许按需提到 4–5 并**在 oracle 表记录**；超限仍未落叶子 → 该项标 `golden`/`unresolved`，不卡死。

## 5. 五类 oracle × 去哪找

| 类别 | 安卓去哪找 | 确定性手段 |
|---|---|---|
| **enum-value** | Kotlin `enum class` / Java `enum` / `data object` 字面量 | `scripts/android-oracle.sh enum <FILE> <Name>` 解析 enum 成员；每个成员字段值另核源码，data object 不由 enum 命令提取 |
| **completeness** | enum 全 entry / sealed 继承集合 / proto enum / 包目录 | Kotlin/Java enum 用 `enum`；其它类型继续核实各自声明及完整性边界，不将目录条数或局部子类搜索当业务全集 |
| **wire-tag** | **实际 `writeTo`/`parseFrom` Kotlin 行为为依据**；注释态 `.proto` 作字段名/tag/ordinal **参照** | 不一致时追踪真实读写路径；已确认实际行为则按其断言并记差异，仍有歧义则标 `wire-uncertain`/`needs_review`。round-trip 仅为补充，不能替代独立字段/tag 预期 |
| **algo-IO** | **优先核查 Kotlin/Java 测试源中的现成 IO 对**；否则从 `when`/`if` 分支 + companion 默认值手提三元组 | `scripts/android-oracle.sh tests <ROOT> [KEYWORD]` 列测试源候选；核对真实断言后复用，**必须**标 `cross_test=<test path:line>` |
| **golden** | 加密/运行时常量、序列化二进制、渲染像素 —— **静态拿不到** | 标 `golden-degraded` + 降级原因 |

> **陷阱1：锚点文件名 ≠ 主类名。** `X.kt` 里的主类未必叫 `X`（如本仓 `FDBrushType.kt` 里实际是 `FDPenType`）。
> `enum <FILE> <Name>` 返回非零时先看诊断、实际声明和模块，不能当作空集。仅退出 0 且输出 `MEMBERS <Name> size=N` 才证明脚本已完整解析该 enum 的成员列表（包括无末尾逗号、同行多成员、参数与成员体）；不支持的语法、同名多声明或截断文件返回 `UNSUPPORTED`，不输出部分 size。字段值另核源码，不将成员位置直接当业务 code。
>
> **sealed 不等于 enum。** 单文件无法证明跨文件直接/间接子类型全集，因此脚本明确拒绝 sealed。继续沿同模块完整源码和继承关系核验，取得可复核的闭合清单后才能记录 size；否则标 `unresolved`/完整性缺口，仅保留有证据的成员事实，不能声称 full。散列 data object、proto 或动态注册集合也须用匹配其语义的证据，不能套用 enum 输出。
>
> **陷阱2：同概念不同层的枚举不可互相回填 size。** 同一域常有「数据模型层枚举」与「工具/UI 层枚举」两套，成员数不同
> （如数据层 `FDBrushType`=6 vs 工具层 `FDPenType`=11）。spec 的"N 种"指哪一层要**核对清楚**；**绝不**拿一层的 size 去断另一层的 spec 声称数，
> 层级/范围仍对不上时记 `diff` + `needs_review`，不自动二选一；已核实同一口径的差异按 §8 处理。
>
> **建议：每 Feature 必先跑一次 `tests <ROOT> <Feature关键词>`**——它不仅给 algo-IO 现成 IO 对，还会**反向暴露 agent 没想到的可测算法**（如吸附/分级/识别器），把它们补进 oracle。

## 🔴 6. golden 分流的硬禁令（最易踩的雷）

- 加密/运行时常量（如 `decrypt(byteArrayOf(...))` + 资源查表 / `FDConst.get(...)`）的**真值静态拿不到**。
- **严禁**把以下当 oracle 硬编码进断言：`/// value: X` 注释、fileKey 名、未经运行时验证的 `strings.xml` 值。
  （实测这类注释常是 fileKey 名而非明文真值 → 当 oracle = **假 oracle，比无 oracle 更危险**。）
- 正确做法：记录 `golden-degraded` + 原因，受影响设计/生成项标 `needs_review`、未验证；其它已有独立证据的断言可保留，但不得把该 golden 行为计为已覆盖。禁止新增占位 `it()`、宽松断言或缩减验证范围冒充完成。
- 只有当该值能被**独立证据**（安卓 `src/test` 实跑断言）交叉确认时，才可升级为真 oracle。

## 7. 完整性闸门（逐 Feature，机检为主，三态都放行）

**可检查清单（全过 = `full`）**
- **A 目标可达**：每条线索经 `resolve` 或发现阶梯（`find-sym`/溯源反查/`grep-kw`，§3.1）命中真实文件；全失才标 `spec_only(no-android-impl)`（并记原因），**不可静默当无锚点跳过**。
- **B 叶子到达**：自探索链落到叶子，链尾不再有未跟踪的间接引用；否则标 `unresolved`/`golden`。
- **C 完整性全集**：Kotlin/Java enum 用成功的脚本结果记录 size + 逐成员，非抽查；sealed/其它集合须有完整源码及闭合范围证据，脚本失败不能过此门。与 spec 声称数量比对，不一致记 `diff`。
- **D wire 已核实**：Kotlin `writeTo`/`parseFrom` 与注释态 `.proto` 交叉核对；差异有实际调用链证据则按 Android 实际行为并记注脚，无法确定的字段标 `wire-uncertain`，不得用往返断言代替外部兼容性证明。
- **E 算法 I-O 有值**：有具体数值三元组，或复用了安卓现成 `src/test`（记 `cross_test`）。
- **F 溯源齐全**：oracle 表每行有 `anchor=<abs>:<line>` + `category`；无来源行不允许存在。
- **G golden 分流**：加密/序列化/像素已标 `golden-degraded`，未对它们写硬字面量。

**反信号（出现即再探一跳或降级）**：断言值无来源注释 / 用宽松断言（`>0`、非空、`size>0`）替代等值 / enum 抽查没点全集 / 对间接常量写了硬字面量 / 链尾仍是未跟踪间接引用。

**终止上限（防无限探索 / token 爆炸）**
- `HOP_LIMIT=3`（跨多仓/长算法链 Feature 可调 4–5 并记录）。
- `FILE_BUDGET=12`：单 Feature 最多打开 12 个安卓文件。
- `GREP_FANOUT=8`：无锚点 Feature 关键词全仓 grep 取前 8 个最相关。
- `READ_CAP≈2500 行 / ~30k tokens`：只读相关段（grep 定位行号 + 窗口读），**禁整文件 dump**。
- `ROUND≤2`：一轮直查 + 一轮 find/grep 兜底，不反复重跳。
- 达任一上限 → oracle 表写 `gate=partial` + 未勾选清单，使下游知道哪些预期尚未核实；这些行为保持未验证，不降低断言标准。

**三态**：`full`（全勾）/ `partial`（已核验行可用，缺证据行待复核）/ `spec_only`（未取得可用 Android 事实）。
**三态都可进 step1 做范围盘点**；仅已有适用证据或明确批准的平台差异支撑的行为可生成可执行强断言，其余行标 `needs_review`。oracle 不全不阻断其它有效用例。

## 8. 明确批准的平台差异

迁移工程可以存在明确批准的平台差异，但必须给出批准依据、受影响行为及预期；不能把推测、未落实的建议或一个无依据的 `diverges_from_android` 标记当作授权。
- 仅对已批准的差异范围采用对应契约；其余行为仍采集并遵循 Android。整个 Feature 均明确偏离时才标 `oracle_status=spec_only(diverges)` 并跳过该范围回填。
- 复用安卓 `src/test` 的行带 `cross_test` 标记，须核对其与当前 Android 实际实现及迁移平台的适用性；已核验仍适用的证据无需逐轮重复人工确认。存在未解决的平台语义冲突才标 `needs_review`，不直接改实现或预期。
- Spec 与 Android 表面冲突时先核对层级、范围和批准差异。实际行为清楚且无批准偏离时以 Android 为准并记录 Spec 差异；口径或来源仍不明时标 `needs_review`，不凭空二选一。

## 9. 确定性与可复现（交脚本，不靠 LLM）

- 锚点解析、枚举全集成员+size、溯源行号回校（`verifyln`）、安卓现成单测枚举 —— **全部由 `scripts/android-oracle.sh` 给**；LLM 只做语义归类（这条 oracle 属哪类、对应哪个鸿蒙符号）。
- oracle 表落盘后按 `(spec 内容 hash + 安卓源 hash)` 做缓存键：两者未变 → step0 跳过重收集，跨轮可复现、不重复烧 token。
