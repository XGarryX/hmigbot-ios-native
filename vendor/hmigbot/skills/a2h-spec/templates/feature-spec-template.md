<!-- when: Phase C Step C4 生成 features/F00x.md 时加载 -->
<!-- topics: feature spec, complexity, android_source_anchors, 数据流, 服务层, API 接口, 对接点, 验收标准 -->

# F00x 功能分 Spec 模板

````markdown
# F001: 音频播放

```yaml
complexity: simple | complex            # ★ 必填，二选一（见 Step C4-pre 第 1 项）
tier: core | standard | peripheral      # ★ 必填，深度预算分档（见 Step C4-pre 第 1b 项）
depth: full | stub                      # ★ 必填，core/standard=full，peripheral=stub

android_source_anchors:                 # ★ complexity=complex 必填，simple 可选
  - role: presenter                     # presenter|viewmodel|service|repository|controller|manager|interceptor|base_class|util|data_model|partial_class
    path: "app/src/main/java/.../AudioPlayerPresenter.kt"
  - role: service
    path: "app/src/main/java/.../PlaybackService.kt"
  - role: interceptor
    path: "app/src/main/java/.../AuthInterceptor.kt"
  - role: base_class
    path: "app/src/main/java/.../BaseMediaActivity.kt"
  - role: util
    path: "app/src/main/java/.../PlaybackUtil.kt"
```

## 范围
涉及页面: AudioPlayerPage, MainPage(ExternalPlayerBar)
依赖: feature-base (Models, DB)

## 数据流
PlaybackService → @Local in AudioPlayerPage / ExternalPlayerBar
  ├─ 播放状态 (playing/paused/stopped)
  ├─ 进度 (position/duration)
  └─ 当前曲目 (title/author/cover)

PD-C6-F001-01 替代路径：`<替代机制产出值（含值域）>` → `<域转换步骤（若产出域 ≠ 消费域）>` → `<消费端>`
（凡 §实现映射 有 HARD-DIV 行，本段必有对应「PD-xxx 替代路径：」行——从替代机制的产出值域推导到消费端，域转换显式在链上；lint 校验 PD-ID 在本节出现）

## 服务层（ArkTS 目标接口，非 Kotlin 源签名）
（必须是 **ArkTS/TypeScript 目标接口签名**，不是 Kotlin 源签名的转抄；`complexity=complex` 必填。Kotlin/源 API 表面归入「源码 5-role 摘要」——服务层回答「ArkTS 端要建什么」，5-role 摘要回答「源码现在是什么」。）
PlaybackService (singleton):
  - play(feedItemId: number): void
  - pause(): void
  - seekTo(ms: number): void
  - getCurrentItem(): FeedItem | undefined
  - onStateChange: callback

## API 接口
（可选段；本功能涉及外部 API 时填写，数据源 = api-inventory.json）
- 对应 api-inventory 候选: F-xxx（path_prefixes: /xxx/*）
- 端点清单（method + path + protocol + auth），**字段路径**：`method/path/protocol` 取自 `services[].endpoints[].static.{http_method, path, protocol}`；`auth` 取自所属 `services[].auth_type`（service 层）:

| method | path | protocol | auth | 迁移关注点 |
|--------|------|----------|------|-----------|
| POST | /xxx/list | REST | Token | — |
| GET | /xxx/stream | SSE | Token | HarmonyOS SSE 支持有限 |

- 迁移关注点直接取 api-inventory 的 `coverage.feature_candidates[].migration_concerns`（SSE/WebSocket/自定义签名/multipart/异步轮询）
- **公共约定不重复列**：鉴权头 / App 凭证 / 全局业务状态码 / 公参（platformInfo 等）若属公共约定（已在 `spec/baseline/api-inventory/common.md` 中收录），**不在本 F spec 重复展开**，引 `common.md` 对应节即可；本 F spec 只展开**本功能专有**的请求/响应字段

## 实现映射（Source→ArkTS）
（complexity=complex 必填）逐条把非平凡的源类型 / idiom / API 映射到 ArkTS 等价物。可引用 feature-base 的「跨栈映射基线」避免重复。

**契约列（触发规则，机械判定）**：凡 `ArkTS 目标` 列引用**平台 API**（`@kit.*` / 系统服务 / NAPI 边界）且该行跨端传递**值**（路径 / 句柄 / URI / token / id / 回调对象 / 描述符…）→ 契约列**必填**：写明该值的**输入/输出域与签名约束**（哪些下游 API 接受该域、域间转换由谁做）。纯语言构造 / 纯 UI 属性映射行免填。**证据来源（三选一引用，禁止凭模型记忆）**：① 项目配置的 SDK d.ts 该 API 的 doc 注释（能力条款的有无即域证据，同族 API 的条款差异划定域边界）；② `$arkts-knowledge-verifier` 查证结论；③ `hmos-references-collection.md` 收录条目。无引用 → lint WARN。

**难度分级**：`低/中` | `HARD`（实现难但**行为等价**，如 NAPI 重写）| `HARD-DIV`（平台无对等能力 → **行为差异**，替代方案改变可观察行为）。

**HARD-DIV 行协议（每行强制 4 件套，缺一 lint FAIL；含「无 1:1 等价 / 无对等 / 替代方案」措辞但无决策 ID 的行同判 FAIL）**：
1. **决策 ID**：就地铸 `PD-<类目C编号>-<F编号>-<序号>`（proposed decision），同步写入 decision-ledger「待批决策」段（grill 议程由机械 grep PD-* 汇集，防散文式升级被漏收）
2. **替代数据流**：在本文件 §数据流 追加「`PD-xxx 替代路径：`」行——从替代机制的**产出值域**推导到消费端，域转换步骤显式在链上
3. **supersedes 清单**：在决策列写 `supersedes: [F00x-ACnn, ...]`（被本决策作废/改写的 parity AC；确无则写 `supersedes: []`），并对每条被列 AC 在其行尾就地标注 `〔superseded by PD-xxx〕`
4. **差异 AC ≥1 条**：在 §验收标准 为替代行为发行 `决:` 锚点 AC（见该节锚点二型）

| 源（Kotlin/iOS idiom） | ArkTS 目标 | 契约（值域/签名约束 + 依据） | 难度 | 决策 / 备注 |
|---|---|---|---|---|
| `<平台专有 UI/图形类型>` | `<ArkUI/ArkTS 等价>` | —（不跨端传值） | 低/中 | — |
| `<自定义序列化/编解码框架>` | 手写编解码 + 字段号表 | —（纯语言构造） | HARD | 无三方等价库；字段号见符号级 anchor；行为等价 |
| `<原生/GPU/桥接原语>` | NAPI C++ 实现 | `<跨 NAPI 边界的 buffer/句柄域约束>`（依据：d.ts §…） | HARD | 无 JS 等价；占位归属见对应 feature；行为等价 |
| `<平台专有能力 X（例：系统级悬浮窗歌词）>` | 无 1:1 等价 → `<系统受控通道 Y（例：应用内歌词页 + 通知栏）>` 替代 | `<Y 的产出值域>` ≠ `<下游消费 API 接受域>`：转换步骤属本决策产物（依据：d.ts §…） | **HARD-DIV** | **PD-C6-F001-01** · supersedes: [F001-AC0x] |

## 状态管理
AppStorageV2 keys: currentPlaybackState, currentEpisodeId

## 对接点（与 UI 页面的接口）
AudioPlayerPage:
  - @Local isPlaying ← PlaybackService.isPlaying
  - @Local playPosition ← PlaybackService.currentPosition
  - onPlayPause() → PlaybackService.togglePlayPause()

ExternalPlayerBar:
  - @Local episodeTitle ← PlaybackService.currentItem.title
  - @Local isPlaying ← PlaybackService.isPlaying
  - onBarClicked() → NavPathStack.push('AudioPlayerPage')

（**跨 feature hand-off 工件契约**：当任一 HARD-DIV 决策改变了跨 feature 传递工件的性质时，对应 hand-off 条目必须补 `工件契约: <值域/类型> + <归一化责任方>`——值域用该 seam 的实际域词汇（继承自 §实现映射 契约列），模板不预设枚举；接收方 feature 的 spec 以此为准，不各自臆断）

## 验收标准
（每条 AC 原子可断言，且带**稳定 ID** `F{编号}-AC{序号}` 紧跟 `- [ ]`——一次分配、永不复用（删除不回收、拆分/新增取新号），前缀 = 本文件 feature 编号，格式/唯一性由 Step C4.6e linter 强制；complexity=complex 时末尾附锚点追踪，见 Step C4 AC 原子性铁律；穷举所有可枚举分支，见 Step C4-pre 第 6 项。实现细节落在 addendum 的 `###` 子组，在**组标题行尾**标 `impl: <addendum>.md §<节>` 指针——组内 AC 默认继承、单条行尾可覆盖、多目标逗号分隔；指针只标注实现归宿，**AC 断言永不移出主文件**；闭环校验见 Step C4.6e）

**锚点二型（每条 AC 二选一，不得缺省）**：
- `源:<Kotlin 符号> → 标:<ArkTS 方法>` — **parity AC**（默认，~97%）：断言与 Android 行为一致
- `决:<PD/D/G-ID> → 标:<ArkTS 方法>` — **差异 AC**：转写**已批/待批决策**的替代行为，仅当该 ID 存在于 decision-ledger（含「待批决策」段）时合法；AC 作者是决策的**转写者而非设计者**，禁止自由发挥。仅真机可验证的断言行尾标 `[真机]`（`[真机]` 只允许出现在 决: 锚 AC 上）

**判定二锚（每条 AC 必填，Spec 期决定，验证期不得降级）**：

`标:` 是一个**符号名**。只写到这里，最省事的检查就是「这个符号存在吗 / 能编译吗」——
迁移的目标却是行为正确。所以每条 AC 还必须写清**怎么判**和**期望值从哪来**：

- `判:<class> | <可观察结果>` — 判定方式。`class` 取值（由弱到强）：
  `static`（代码形态断言，仅在确无更强手段时使用）· `unit` · `contract`（请求/响应比对）·
  `route`（可达性）· `ui`（驱动交互后断言状态）· `visual`（截图比对）· `device`（真机行为/性能）。
  最低强度由证据决定（见 `scripts/coverage-rules.json`）：权限→`ui`、数值/公式→`unit`、
  渲染→`visual`、平台能力→`device`。**写 Spec 时定，验证时只能用更强的，不能用更弱的**；
  设备不可用时结论是 `blocked`，不是 `pass`。
- `真:<来源>` — 真值来源。只接受 Android 侧事实或已批准决策：
  `真:src:<path>:<line>` · `真:test:<Android 测试路径>` · `真:trace:<抓包/录制>` ·
  `真:device:<真机观察>` · `真:decision:<PD/D-ID>`（差异 AC 用）。
  **禁止** `真:arkts-impl` / 「以当前实现为准」——那会让测试对着自己写的代码打勾。

单行完整形态（三组反引号，用全角空格分隔）：

```text
- [ ] F001-AC01 <断言>　`源:<符号> → 标:<ArkTS 方法>`　`判:<class> | <可观察结果>`　`真:<来源>`
```

**可枚举事实逐项交代（`组:` 声明）**：证据画像会枚举出具名事实清单——埋点事件名、
`@JavascriptInterface` 桥方法、枚举取值、命名常量、比较阈值、权限调用点、三方 SDK 接缝。
**每一项都必须被交代**，三选一：

1. 某条 AC 的文本**点名**它（事件名 / 方法名 / 常量名 / 数值原样出现）；
2. 确属同构的一批，在**一条** AC 上声明 `组:{a, b, c}` 合并覆盖——组声明是覆盖记账，
   不是断言内容，不影响 assertion digest；成员写实例 ID 或裸名均可；
3. 不迁移的，在 `spec/baseline/skip-list.md` 登记 `` `实例ID` `` + 理由。

示例（27 个埋点事件合并为按通道分组的三条 AC）：

```text
- [ ] F015-AC03 支付类事件经火山+个推双通道上报，事件名与 Android 一致
      `源:VolcEnginManger.onEvent → 标:TrackService.report`　`判:contract | 抓包比对事件名与13个服务端字段`　`真:src:event-track/.../VolcEnginManger.kt:88`
      `组:{payment_fail, payment_support, vip_pay_click}`
```

静默漏掉任何一项 = 🔴 `SPEC.INSTANCE_UNACCOUNTED`，Gate C 不可通过。

### A. 播放控制（状态机）  impl: F001-audio-playback.state-machine.md §状态机与转移表
- [ ] F001-AC01 点击播放按钮开始/暂停播放　`源:AudioPlayerPresenter.togglePlay() → 标:PlaybackService.togglePlayPause()`　`判:ui | 播放中点击后 isPlaying=false 且进度停止推进`　`真:src:app/.../AudioPlayerPresenter.kt:88`
- [ ] F001-AC02 进度条实时更新　`源:AudioPlayerPresenter.onProgress() → 标:PlaybackService.currentPosition`　`判:unit | 每 500ms 回调一次，position 单调不减且 ≤ duration`　`真:src:app/.../AudioPlayerPresenter.kt:141`

### B. 外部播放条
- [ ] F001-AC03 ExternalPlayerBar 显示当前曲目信息　`源:ExternalPlayerBar.bind() → 标:ExternalPlayerBar.build()`　`判:ui | 切歌后标题/作者/封面三处同步刷新`　`真:src:app/.../ExternalPlayerBar.kt:52`
- [ ] F001-AC04 后台播放不中断　`源:PlaybackService.onStartCommand() → 标:PlaybackService.start()`　`判:device | 切后台 60s 后音频仍在播且进度连续`　`真:device:Android 真机录屏 2026-08-06`　impl: F001-audio-playback.lifecycle.md §后台播放
- [ ] F001-AC05 `<被替代的平台专有行为（例：系统级悬浮窗歌词常驻）>`　`源:<LyricOverlayController.show()> → 标:—`　〔superseded by PD-C6-F001-01〕

### B'. 决策差异行为（决:PD-C6-F001-01，替代面 源:<LyricOverlayController>）
- [ ] F001-AC06 `<替代行为断言 1（例：播放页入口可打开应用内歌词页，歌词随进度滚动）>`　`决:PD-C6-F001-01 → 标:<LyricPage>`　`判:ui | 打开歌词页后当前行随 position 高亮下移`　`真:decision:PD-C6-F001-01`
- [ ] F001-AC07 `<替代行为断言 2（例：通知栏展示当前行歌词，切歌即时刷新）>`　`决:PD-C6-F001-01 → 标:<AVSessionController.updateMeta>`　`判:device | 通知栏文本在切歌后 1s 内更新`　`真:decision:PD-C6-F001-01` [真机]
- [ ] F001-AC08 `<替代通道不可用时的兜底断言（例：通知权限未授予 → 应用内歌词页仍完整可用，无崩溃）>`　`决:PD-C6-F001-01 → 标:<catch 分支>`　`判:device | 拒绝通知权限后进入播放页不崩溃且歌词页可用`　`真:decision:PD-C6-F001-01` [真机]
````

每个功能 Spec 必须包含：
- **complexity / tier / depth（顶部 YAML 块，必填）**：complexity 见 Step C4-pre 第 1 项；tier + depth 见第 1b 项（决定本轮深度预算与是否按需深挖）
- **android_source_anchors（顶部 YAML 块）**：`complexity=complex` 时必填，至少 1 条；`simple` 可选
- **范围**：涉及的页面和依赖
- **数据流**：从数据源到 UI 的完整链路
- **服务层（ArkTS 目标接口）**：必须是 ArkTS/TypeScript 目标接口签名，不是 Kotlin 源签名转抄；`complexity=complex` 必填
- **API 接口**（可选）：本功能涉及外部 API 时填写，端点清单从 `api-inventory.json` 选取本功能对应候选的端点；公共约定（鉴权 / 公参 / 信封 / 状态码）引 `common.md`，**不在 F spec 内重复展开**
- **实现映射（Source→ArkTS）**（complexity=complex 必填）：非平凡源类型/idiom/API → ArkTS 等价物映射表；平台 API 跨端传值行必填**契约列**（值域/签名约束 + 三源引用之一）；行为等价的难实现行标 `HARD`；平台无对等致行为差异的行标 `HARD-DIV` 并履行 **4 件套协议**（PD-ID / §数据流替代路径 / supersedes 清单 / ≥1 条差异 AC）；可引用 feature-base 跨栈映射基线
- **状态管理**：AppStorageV2 / @Local 键名和类型
- **对接点**：与 UI 页面的 @Local 变量对应关系（引用 Phase B 分页 Spec 的状态接口）
- **验收标准**：可验证的功能检查项；每条带稳定 ID `F{编号}-AC{序号}`（紧跟 `- [ ]`，一次分配永不复用，前缀 = 本文件 feature 编号）；每条必带 `判:`（判定方式 + 可观察结果）与 `真:`（真值来源），缺任一项由 `lint_coverage.py` 报 findings；实现细节在 addendum 时，`###` 子组标题（或单条 AC）尾标 `impl: <addendum>.md §<节>` 指针（组级默认 + 单条覆盖；多子仓场景可指向 `cross-module-contracts.md §<节>`）；AC 断言永不移出主文件；ID 与指针闭环由 Step C4.6e linter 确定性校验，a2h-execute Step 3b/3c worker 按指针定向精读

**AC 数量没有下限、上限或偏差带。** 充分性由 `scripts/lint_coverage.py` 按证据判定：Android 源码里检出什么行为信号（权限 / 错误 / 状态机 / 并发 / 序列化 / 生命周期 / 网络 / 持久化 / 数值 / 导航 / 渲染 / 平台 / 跨模块），就要求覆盖对应的行为**种类**，每条要求都带 `file:line` 证据。多写的 AC 永远不会导致失败。
