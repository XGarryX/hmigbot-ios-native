<!-- when: Phase C Step C4-pre 判定 feature 的 tier/depth、填充 anchor、建立证据画像时加载 -->
<!-- topics: tier 分档, depth full/stub, role 9 类, anchor 自动填充, Kotlin 扩展函数, primary package, 证据画像, profile_feature.py, coverage-rules.json, 必备义务种类, 判定强度, AC 质量护栏, 三无 AC, 广度保底, Section overflow, addendum slug -->

# Step C4-pre 细则：tier/depth 分档、anchor 填充与证据画像

> a2h-spec Step C4-pre 在生成每个 feature spec 前执行。`complexity` 二级判定（complex/simple）的信号表见 SKILL.md body 第 1 项；本文是其余 1b–6 项的完整细则。

## 1b. tier 三级判定（深度预算分档，与 complexity 正交）

complexity 决定「要不要写 addenda」；tier 决定「本轮投入多少深度」。按以下信号给每个 feature 评级（阈值为默认值，按项目总 LOC 等比缩放；边界 case **优先上调一档**）：

| tier | 判定信号（命中其一即归入） |
|------|--------------------------|
| `core` | anchored_LOC ≥ 3000，或 fan-in ≥ 3（被 ≥3 个其他 feature 依赖），或 P0 且处于引擎/业务主链路 |
| `standard` | 500 ≤ anchored_LOC < 3000 且 fan-in 1–2，或有对应 UI 页面 / API 端点支撑 |
| `peripheral` | anchored_LOC < 500 且 fan-in = 0 且无 UI 页面、无 API 端点（典型：源码普查兜底发现的小型引擎 util / 单一交互工具 / 局部持久化） |

**Eager 深度映射（本轮处理）**：

| tier | depth | 本轮要求 | 并行策略 |
|------|-------|---------|---------|
| `core` | `full` | **超过** depth floor（AC 目标 ≈ floor × 1.5，穷举所有分支/常量/专属类，floor 是下限不是上限） | 串行深挖或小批并行 |
| `standard` | `full` | 达到 depth floor（见第 6 项） | 可分批并行 |
| `peripheral` | `stub` | 仅占位：anchors + `## 范围` + 3–8 条核心 AC；不强制穷举，待 Step C4.6c 按需升级 | 由 sub-agent 批量并行轻量生成 |

> 关键：breadth（每个包都有归宿）与 depth（深挖）走不同预算——peripheral 用廉价 stub 保证 breadth，core/standard 集中预算保证 depth，二者不互相挤占。

## 2. role 类型与语义（worker 在 Step 3b 内总结时遵循）

| role | Kotlin/Java 文件命名约定 | worker 必须总结的内容 |
|------|------------------------|---------------------|
| `presenter` / `viewmodel` | `*Presenter.kt` / `*ViewModel.kt` | ① 状态机（所有状态枚举） ② 事件流 ③ 异常分支 |
| `service` / `repository` | `*Service.kt` / `*Repository.kt` | ① 接口列表 ② fromJson 兜底 ③ 缓存策略 |
| `controller` | `*Controller.kt` | ① 所有 public 方法签名 ② 状态字段 ③ 与 view 的回调约定 |
| `manager` | `*Manager.kt` | ① 单例 / 生命周期 ② 暴露的 API ③ 内部状态 |
| `interceptor` | `*Interceptor.kt` | ① 拦截链顺序 ② header/参数注入 ③ 加密路径 |
| `base_class` | `Base*.kt` | ① 基类 lifecycle hook ② opt-in 机制 ③ 共享状态 |
| `util` | `*Util.kt` / `*Helper.kt` | ① 静态方法清单 ② 命中场景 ③ 副作用 |
| `data_model` | `*Model.kt` / `*DocumentModel.kt` / `*PageModel.kt` | ① 字段清单 + 类型 ② 序列化字段 tag ③ 默认值 |
| `partial_class` | `*Private.kt` + `*Private_*.kt` 全体（基类 + Kotlin 扩展函数伴随文件） | ① 每个伴随文件的职责 ② 跨文件方法分组 ③ 主类公开行为表 |

## 3. anchor 自动填充规则

按命名约定扫描 Android 源码：
- 对每个 role，glob 对应文件名模式（**全集**）：
  - `**/*Presenter.kt`、`**/*ViewModel.kt`
  - `**/*Service.kt`、`**/*Repository.kt`
  - `**/*Controller.kt`、`**/*Manager.kt`
  - `**/*Interceptor.kt`
  - `**/Base*.kt`
  - `**/*Util.kt`、`**/*Helper.kt`
  - `**/*Model.kt`、`**/*DocumentModel.kt`、`**/*PageModel.kt`
- 命中文件名含 feature 关键词（如 `AudioPlayer*`、`Playback*`、`Instrument*`、`Lasso*`、`Document*`、`Page*`）→ 加入 anchors

**Kotlin 扩展函数分文件模式（必检）**：
- 当主类定义在 `XxxPrivate.kt` 且存在同级 `XxxPrivate_*.kt` 伴随文件时（伴随文件用 `fun XxxClass.method() { ... }` 形式给主类追加方法），**必须** glob 全部伴随文件并以 role=`partial_class` 加入 anchors
- 适用范围：所有 Android Kotlin 项目；这是 Kotlin 提供的常见代码组织模式，原生 Android 工程与 iOS-port 工程都可能采用
- 例（NotepadCore 实际案例）：`FDNotepadPaginationDocumentPrivate.kt` 命中 → 同级 `_Element.kt / _Layer.kt / _Object.kt / _PDF.kt / _PageAction.kt / _Search.kt / _Update.kt / _CrossPage.kt / _FullScreenText.kt` 伴随文件全部 anchor
- 跳过会导致整个能力域 80%+ LOC 失锚

**Primary package 扩展（达 30% 覆盖率前必跑）**：
- 选定上述 anchors 后，计算其所在包路径前缀（如 `core/canvas/instrument/`）→ 此为 feature 的 primary package
- 统计 primary package 内 `*.kt` 总文件数
- 若 anchors 覆盖率 < 30% → 继续从 primary package 中追加同类型文件（按上述 glob 模式 + feature 关键词），直至 ≥30% 或包内文件耗尽

- 路径**相对** `$ANDROID_SRC`（如 `app/src/main/java/.../AudioPlayerPresenter.kt`）

## 4. anchor 校验（写入 spec 前）

- 逐路径检查 `$ANDROID_SRC/{path}` 存在
- 不存在 → 从列表移除 + 输出警告
- `complexity=complex` 但 anchors 数组为空 → 输出警告（不阻断，由 plan/execute 阶段二次校验）

## 5. Section overflow detection（仅 complexity=complex）

生成 spec 时按 section 估算行数。任一 section >150 行 → 溢出到 sibling addendum，主文件保留 5–10 行摘要 + 链接（如 `详见 F00x-name.<slug>.md`；**`## 验收标准` 内 AC 组的实现归宿则用 `impl:` 指针标注**，见 feature-spec-template 与 Step C4.6e）。

Addendum 命名约定：`F{编号}-{feature-name}.{section-slug}.md`，标准 slug：

| slug | 典型内容 | 默认 consumed_at（frontmatter 缺省时按此推断） |
|---|---|---|
| `api` | 端点详情、auth、重试、payload schema | step-3c |
| `state-machine` | 状态枚举、转移表、不变式 | step-3b |
| `audio-focus` / `lifecycle` | 焦点/生命周期协调规则 | step-3b |
| `cast` / `<sdk-name>` | 第三方 SDK 集成深度 | step-3c |
| `persistence` | 持久化策略、恢复、schema 版本 | step-3c |
| `races` | 竞态分析、时序约束 | step-3b |
| `mapping` | Source→ArkTS 映射表、HARD 项决策、字段号/编解码细节 | 按 impl: 指向的 AC 组归属（3b/3c 皆可） |

自定义 slug 允许（kebab-case，单词为佳）。

**`## 验收标准` 永不溢出**——若 AC 数量过多导致主文件超 500 行，触发"feature 拆分"建议（输出 warning，写入 Phase C 审批摘要），由 Gate C5 人工决策是否拆分；**绝不**将 AC 移出主文件。

## 6. 证据画像、质量护栏与覆盖判定

> **本节在 v3 被重写。** 原「AC 预算：按复杂度动态压缩」（`AC_budget = max(tier_floor,
> decision_count/D)`、`depth=stub` 钳制 [3,8]、±40% 偏差 lint、depth floor 的 AC 数阈值）
> **已全部删除，且不得以任何形式复活**。真实语料实测：12/12 功能预算被 tier floor 主导、
> 实际产出超预算 +80%、9/12 落在 ±40% 带外——门禁是空转的。更根本的是：一个数字无法表达
> 「这个功能漏了权限拒绝路径」，而这正是迁移中最常见的缺口。

**算法级 AC 的符号级 anchor**：当一条 AC 描述的是计算（数学变换 / 序列化字段号 / 缓存淘汰 / 命中判定等可被「转述」掉的逻辑），其实现追踪的「源」必须精确到 **函数 + 行号**（非仅文件级 anchor），或在 `mapping` / 相应 addendum 用伪代码写出算法。否则 converter 易以释义代替实现而留桩——这类 AC 是 spec→code 保真度最薄弱处。

### 6.1 证据画像（取代预算推导）

```bash
python3 <SKILL_ROOT>/scripts/profile_feature.py \
  --src $ANDROID_SRC --features-dir spec/baseline/features
# -> spec/baseline/feature-profiles.json
```

脚本（确定性，非 LLM）读每个 feature 的 `android_source_anchors`，在**去注释后**的源码里检出行为信号，每条带 `file:line` 证据：

| 信号 | 检出依据（示例） |
|---|---|
| `permission` | `checkSelfPermission` / `requestPermissions` / `Manifest.permission.` |
| `error_path` | `throw` / `catch(` / `onError` / `runCatching` |
| `state_machine` | `sealed class` / `enum class` / `MutableStateFlow` / `MutableLiveData` |
| `concurrency` | `launch{` / `withContext` / `Dispatchers.` / `synchronized` / `Atomic*` / `Handler(` |
| `serialization` | `Gson` / `@SerializedName` / `JSONObject` / `Parcelable` / `ByteBuffer` |
| `lifecycle` | `onCreate(` / `onDestroy(` / `onSaveInstanceState(` / `onActivityResult(` |
| `network` | `@GET/@POST/…` / `Retrofit` / `OkHttpClient` / `Call<` |
| `persistence` | `SharedPreferences` / `MMKV` / `@Dao` / `getWritableDatabase` |
| `numeric_const` | `const val X = <数字>` / `static final int X = <数字>` |
| `navigation` | `startActivity(` / `Intent(` / `beginTransaction` |
| `render` | `Canvas` / `Paint(` / `Bitmap` / `Shader` / `PorterDuff` / `SurfaceView` |
| `platform_api` | `Build.VERSION` / `getSystemService` / `Class.forName` |
| `cross_module` | anchors 跨越多个 Gradle 模块 |

**模型不得自报信号。** 自报等于自己给自己定标准——旧门禁失效的根因就在这里。

### 6.2 必备义务种类（`scripts/coverage-rules.json`）

信号 → 必须覆盖的行为**种类** + 该种类的**最低判定强度**。例如：

| 信号 | 必备种类 | 最低 `判:` | 理由 |
|---|---|---|---|
| permission | `permission_granted` / `permission_denied` | `ui` | 拒绝路径最常被漏写 |
| error_path | `error` / `recovery` | `unit` | 抛错与兜底是两件事 |
| state_machine | `state_transition` | `unit` | guard 不同即不同转移，不得合并 |
| serialization | `field_mapping` / `decode_failure` | `unit` | 字段名/类型/顺序属不可压缩事实 |
| numeric_const | `exact_value` | `unit` | 写成「大约」即迁移失真 |
| render | `draw_result` | `visual` | 编译与单测都判不了混合/透明度 |
| platform_api | `platform_behavior` | `device` | 平台差异只能由真机或已批决策确定 |

要新增/调整规则，改 `coverage-rules.json` 一处即可；Markdown 只是它的人读投影。

### 6.3 覆盖判定（Step C4.6f）

```bash
python3 <SKILL_ROOT>/scripts/lint_coverage.py --src $ANDROID_SRC --project-root $PROJECT_ROOT
```

- 🔴 **唯一阻断项** `SPEC.UNCOVERED_ANCHOR_FILE`：某锚定文件检出了行为信号，却没有任何 AC 的
  `源:` 指向它声明的符号。纯集合运算，无歧义，必须清零。
- 🟡 其余（缺 `判:`/`真:`、种类可能漏写、判定强度偏弱、缺专项材料、源码文件无归属）都含判断
  成分，进 findings 队列交 Gate C 由用户裁决，脚本不代拍板。

`score_complexity.py` 保留但**降级为诊断**（→ `spec/baseline/complexity-metrics.json`）：
`decision_count` / 密度用于观察，`split_recommended` 提示 feature 大到不便审阅——**不参与门禁**。

### 6.4 AC 质量护栏（保留）

- **禁三无 AC**：不得写「X 类存在 / getter 返回字段 / 方法可调用」这类无行为断言的平凡 AC；每条必须断言一个**行为 / 约束 / 取值 / 分支结果 / 错误路径**。无法断言行为的符号归入 `## 服务层` 接口表。
- **去重（feature 内）**：同一 `源` 符号不得有两条断言**相同行为**的 AC；多条 AC 当且仅当各自断言**不同**的分支 / 取值 / 边界。
- **去重（feature 间）**：每个源符号被**唯一** feature 认领（C4.6b ownership）；跨 feature 共享 / seam 符号在 `feature-base.md` / `cross-module-contracts.md` 权威规约**一次**，他处引用不重写。
- **不得为凑数造 AC**——现在也没有数可凑：没有下限、上限或偏差带。AC 只能来自枚举真实源码决策（`源→标`）或转写已批/待批平台差异决策（`决→标`）。
- **每条 AC 必带判定二锚** `判:` / `真:`（见 `templates/feature-spec-template.md` §验收标准）。`真:` 指向 ArkTS 实现现状会被 `lint_coverage.py` 判为阻断——那会让测试对着自己写的代码打勾。

### 6.5 广度保底（保留，与深度不互相挤占）

| 指标 | 要求 |
|---|---|
| 锚定文件覆盖率 | ≥30% of files in feature's primary package(s)（不足则扩 anchors 或在 `## 范围` 显式声明 out of scope） |
| 常量/阈值清单 | 穷举 anchored 文件中所有 `var XXX = <literal>` / `const val XXX = ...`，出现在 `## 迁移关注点` 或 `## 状态管理` |
| 操作 / 分支 / 专属类穷举 | ① 锚定文件中每个 public `fun` / enum case 至少在 ACs 或 `## 服务层` 出现一次（core/standard 必须，peripheral stub 暂免）；② 每个代表独立子系统的专属类（`*View` / `*Renderer` / `*Controller` / `*Manager` / `*Session` 且 `loc ≥ 150`）**必须被某 feature anchor**（所有 tier 强制）；其专属 AC 仅 core/standard 要求 |
| 源码文件归属 | 每个生产源码文件要么被某 feature 锚定，要么在 `spec/baseline/skip-list.md` 登记理由（`lint_coverage.py` 的 `SPEC.UNOWNED_FILE`） |
