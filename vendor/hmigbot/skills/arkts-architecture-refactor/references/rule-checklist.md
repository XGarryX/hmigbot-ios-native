# 规则全量 checklist（audit 阶段使用）

> ⚠️ **先读 [`ai-baseline.md`](./ai-baseline.md)**——AI 工程是 ground truth。本表中的"严格度"列已按 AI 工程实际做法 + 客户最新 customer-checklist.md 校准；如本表与 ai-baseline.md 冲突，**以 ai-baseline.md 为准**；客户已明确升级的规则严格度（见下"客户校准记录"）以**客户校准为准**。


**严格度分级**（来自规范原文措辞）：

| 级别 | 触发措辞 | audit 处理 |
|---|---|---|
| **MUST** | "必须 / 务必 / 统一 / 请使用" | 列入 P0/P1，必改 |
| **SHOULD** | "应 / 请尽量 / 尽量使用 / 应尽量 / 避免" | 列入 warnings，**让用户决定改不改** |
| **MAY** | "可 / 可利用 / 以下是实例 / 例如" | 仅作提示，不计入差距 |

> **私仓优先原则**：本表中提到的 lib_common / lib_widget / lib_network / lib_payment / lib_starburst / lib_umeng / lib_hmiap 均来自公司私仓 `repo.dadoubk.cn`，相关类（RouterUtils / RequestUtil / ExternalReqUtil / PreferenceUtil / ColorUtils / BaseViewModel / BreakpointModel / WindowModel）均带"（私仓）"标注。**能用私仓就用私仓**，不要绕过。

---

## 客户校准记录（最新一轮，2026-04）

客户在阅读 customer-checklist.md 后明确要求以下规则严格度调整（**必须采纳**）：

| 规则 | 旧严格度 | 新严格度 | 备注 |
|---|---|---|---|
| R0.1 ArkTS 官方文档遵循 | — | **MUST**（新增） | 见客户清单"〇、ArkTS 语法基线"|
| R4.1 webp/svg | MAY | **MUST** | 静态图必须 webp/svg |
| R4.2 webp 3x 倍图 | MAY | **MUST** | 对应 Android xxhdpi |
| R4.3 动画 webp 不 gif | MAY | **MUST** | 对齐 Android |
| R4.4 单色 webp 着色样例 | — | **MUST**（新增） | 必须用 `ColorUtils.hexToColorMatrix`（私仓）+ `colorFilter` 实现 |
| R6.1b Repeat 替代 LazyForEach | SHOULD | **MUST** | 列表必须用 Repeat |
| R6.3b DTO interface 优先 | MAY | **SHOULD** | 新代码优先 interface |
| R6.3c/d/e AbortController | MAY | **拆三条** | **R6.3c 全局=MUST NOT abort**（误挂报警）；**R6.3d 非全局=MUST abort**（漏 abort 必报、无豁免）；**R6.3e 第三方=SHOULD abort**（默认报、可豁免）|
| R6.5a 沉浸式安全距 | SHOULD | **MUST** | 必须预留顶/底安全距 |
| R6.5b-1 List/Grid 列数动态化 | SHOULD | **MUST** | List/Grid 必须用 BreakpointModel（私仓）动态取列数（R6.5b-2 普通容器仍 SHOULD）|
| R6.6 buildProfileFields | MAY | **MUST** | 壳工程必须配置 |

---

| rule_id | 严格度 | 规则要点（含原文核心措辞） | 检测方法 |
|---|---|---|---|
| **R0.1** | MUST | "参考鸿蒙官方开发文档" —— ArkTS 语法基线 | 客户已明确要求遵循 <https://developer.huawei.com/consumer/cn/doc/harmonyos-guides-V5/arkts-coding-style-guide-V5>；audit 时不强制逐条扫语法（依赖 IDE 提示），但 SKILL.md / customer-checklist 必须显式声明此规范作为基线 |
| **R1.1** | MUST | "整体采用 壳工程+业务组件工程+公共独立组件工程"——三段式 products/features/components | 检查根目录是否齐三段；缺哪段记哪段 |
| **R1.2** | MUST | "**务必**将不同业务代码拆分为独立的 business 组件工程" | (1) `features/business_* (排除 business_common) >= 2` —— 仅 1 个 business（如 `business_main`）等价于把所有业务堆进单模块，**违反规则字面**，标 P0 FAIL；(2) 双 baseline 实证：AI 6 个 + business_common，Scan 4 个 + business_common，**最低基准 2-3 个非 common business**；(3) 检查 entry/单模块里是否堆砌多业务（多个 page 域属不同 business）|
| **R1.3** | MUST | "三段式 = products + features + **components**" —— components/ 层不能省 | (1) 项目根 `components/` 目录必存在；(2) 至少 1 个 `components/module_*`（双 baseline 各有 6 个 module_*）；(3) 完全缺 `components/` 标 P0 FAIL，已有 `components/` 但里面是空目录标 P1。**注**：跨 business 复用的 UI 组件、第三方 SDK 封装（如分享/广告/转场）应放此层 |
| **R2.0** | MUST | **私仓优先原则**：能用私仓 (`repo.dadoubk.cn`) 提供的能力，一律用私仓 | 检查方式：grep 业务代码里有没有自造 RouterUtils / 自造 PreferenceUtil / 自造 HTTP 封装等"重复轮子"；命中 → P1 改用私仓 |
| **R2.1** | MUST | "**必须**接入...仓库地址" | `.ohpmrc` 必须含 `repo.dadoubk.cn` |
| **R2.2-a** | MUST | lib_common（私仓）—— 提供 BaseViewModel / RouterUtils / PreferenceUtil / ColorUtils / BreakpointModel / WindowModel 等基础能力 | `oh-package.json5` 必须引用 lib_common；缺失 → P0 |
| **R2.2-b** | MUST（条件） | lib_network（私仓）—— 仅当工程用到 HTTP 网络请求时必接入 | grep 业务 HTTP 调用，命中 → 必须有 lib_network；单点特殊封装（下载等）可豁免 |
| **R2.2-c** | MUST（条件） | lib_payment（私仓）—— 仅当工程有支付场景时必接入 | 直连三方支付 SDK 而未走 lib_payment → P1 |
| **R2.2-d** | MUST（条件） | lib_starburst（私仓）= **客户内容提供平台 SDK**（**非数据上报库**）—— 业务调用客户内容平台接口（素材列表、运营位、推荐内容等）时必须直接复用此私仓提供的 API | 业务侧自己写 HTTP/类型定义/响应解析去对接客户内容平台 → P1（应直接 import lib_starburst 用现成 API）。无相关接口调用就不引此包 |
| **R2.2-e** | MUST（条件） | lib_umeng（私仓）—— 仅当工程有推送需求时必接入 | 直连 umeng SDK 而未走 lib_umeng → P1 |
| **R2.2-f** | MUST（条件） | lib_hmiap（私仓）—— 仅当工程用应用内购时必接入 | 直接调华为 IAP 而未走 lib_hmiap → P1（参见 R2.3 版本约束） |
| **R2.2-g** | MUST | lib_widget（私仓）—— 公共 ArkUI 组件优先 | 自造重复轮子（已有 lib_widget 同款实现）→ P1 |
| **R2.3** | MUST | "如**无需**启用鸿蒙联运，请引入 lib_hmiap 的 1.0.0 版本即可" | 仅当工程引用了 lib_hmiap（私仓）时才检测：未启用联运但版本 ≠ 1.0.0 标违规 |
| **R2.4** | MAY（best practice） | 根 `oh-package.json5` `overrides` 锁版本 | **双工程实证**：AI 有 / Scan **没有**——两者都合规。仅在多模块 lib_*（私仓）实际版本漂移时建议补 |
| **R2.5** | INFO | lib_*（私仓）具体版本号 | **双工程实证**：AI 用一组版本（lib_common 1.1.5）/ Scan 用更新组（lib_common 1.1.8）。模板**不硬编码版本**，按工程当时稳定版本 |
| **R3.1** | SHOULD | "各业务代码类**应按照**模块功能进行拆分放置...**以下是实例**：components/constants/pages/viewmodel/bean/util" | **不要按目录名拼写判违规**。检测：(a) 是否有混业务现象（比如 dialogue 页面和 mine 页面同处一个 pages/ 下却语义关联很重）；(b) 是否单文件超大（>500 行 + 多 public 方法），违反"职责单一" |
| **R3.2** | SHOULD | "应保证类职责单一性" | 单 .ets > 500 行 或单 class > 10 public 方法标 warning |
| **R4.1** | **MUST**（客户升级） | "静态图片资源，**统一**采用 webp/svg 格式" | 静态图必须 webp/svg；**新增**资源不得 png/jpg；存量 png 列入资源迁移待办，标 P1 |
| **R4.2** | **MUST**（客户升级） | "webp 图片**应**采用 3 倍图，对应 Android xxhdpi" | 抽样验证 webp 像素尺寸 ≥ 3× 设计稿（无法静态判定时仅 P2 提示，但客户验收要点） |
| **R4.3** | **MUST**（客户升级） | "动画资源**应统一**采用 webp 格式实现，**避免**使用 gif（对齐 Android）" | grep `*.gif`，命中 → P1 必改 |
| **R4.4** | **MUST**（客户新增） | "对于 webp 格式图片如需改动着色，**可采用** lib-common（私仓）/ ColorUtils（私仓）类的 hexToColorMatrix 方法配合组件 colorFilter 方法实现" | 需要不同色版的图标场景必须用此样例（详见 [`03-layering-styles.md` § 单色 webp 着色](./03-layering-styles.md)）；预生成多色版本 → P1 |
| **R5.1-a** | MAY（已降级） | 规范列的 19 个通用 token 是**跨平台同名建议**，不是必填白名单 | **AI 实证**：business_common 仅 2 个 token（cancel_btn_bg/common_page_bg），products/phone 用 app_theme/text_color/btn_*_Color 等自有命名——都不算违规 |
| **R5.1-b** | MAY | 业务自有色（播放器轨道色等）允许业务模块自己定义 | 不视为违规 |
| **R5.2** | SHOULD | "对于加粗字体，**请尽量使用** UI 稿提供的 weight 数值...**避免**统一采用 Bold（**尤其在迁移 Android 代码**时）" | `FontWeight.Bold` 数量列 warning；不强制改 |
| **R5.3** | SHOULD | "**页面左右间距**...统一采用 BreakpointModel（私仓）.pagePadding" | 只针对页面最外层容器的 `padding({left/right: N})`，非组件内部间距 |
| **R6.1a** | **MUST（客户校准为全局）** | "**统一**使用 v2 状态管理" — 客户校准为**无场景豁免**：业务页面、普通组件、widget/dialog/builder/特殊渲染/引导组件**全部**必须 v2 | audit 命中 v1 装饰器（@Component/@State/@Prop/@Link/@Provide/@Consume/@Observed/@ObjectLink/@StorageProp/@StorageLink）一律 P1 改造。**AI/Scan baseline 中残留的 v1 实例**（widget/dialog/builder/Guide*）**不再视为合规豁免**，按 P1 整改。无例外 |
| **R6.1b** | **MUST**（客户升级） | "**尽量使用** Repeat 替代 LazyForEach" —— 客户校准为 MUST：列表必须用 Repeat | grep `LazyForEach`，命中 → P1 改 Repeat。**例外**：已知 Repeat 不支持的极个别场景（如某些 SDK 内置组件强制 LazyForEach）可豁免，但要在报告里记录 |
| **R6.1b'** | MUST | "若涉及到列表 item 子项单独拆分 @Builder 方法场景，**请将 RepeatItem 对象整体**传递至 @Builder 方法，否则会出现刷新问题" | 改造 LazyForEach→Repeat 时强制约束：@Builder 参数必须是整个 `RepeatItem<T>`，不能解构成 `(item: T, index: number)`。否则 `@Trace` 字段更新无法触发刷新——这是规范特别强调的"坑" |
| **R6.1c** | SHOULD | "**对于复杂页面**应利用 ViewModel...请将 ViewModel **继承自** BaseViewModel（私仓）" | **仅约束主页面 VM**——命名以 `*PageVM / *PageViewModel` 结尾的链顶层。其他 *VM / *ViewModel（辅助型 / 工具型 / 计数型）即使未继承也合规。**实证**：Scan 的 PreviewViewModel / UseCountViewModel / QqShareViewModel / WxShareViewModel 都未继承且合规 |
| **R6.2a** | MUST | "项目整体路由**采用** Navigation...请**使用** RouterUtils（私仓）进行**统一**处理" | grep 旧 `router.pushUrl/replaceUrl/back/clear` 必改；同时检查是否引入 RouterUtils（私仓） |
| **R6.2b** | **MUST**（客户新增） | 路由名称**必须**用常量类（RouterMap 或同等），业务调用**禁止**裸字符串 | 客户反馈核心痛点：业务代码 40+ 处 `RouterUtils.pushPathByName('XxxPage')` 字面量 → 改名/重构噩梦。**audit grep**：`RouterUtils\.(push\|replace)PathByName\(['"][A-Z]` 命中即 P1。**正确做法**：调用方 `RouterUtils.pushPathByName(RouterMap.MEMBER_CENTER_PAGE)`；page 上的 `@RouterMap({ name: ... })` 注解也用同一套常量 |
| **R6.3a** | MUST（带豁免） | HTTP 公司请求走 RequestUtil（私仓）；第三方走 ExternalReqUtil（私仓） | grep `@ohos/axios / http.createHttp`，**大量命中**（业务全用 axios）→ P1；**单点命中**（个位数特殊场景如文件下载、特殊 header）→ MAY。**AI 实证**：1 处 axios 在 ReadCoverCreate（特殊场景）。WebSocket 不在范围 |
| **R6.3b** | **SHOULD**（客户升级） | "请**采用** interface 接收 json...**避免使用** class，可空字段加 `?` 或 `\| undefined`" | 客户已校准为 SHOULD：新写代码优先 interface（裸 class → P2 建议改）；项目历史 `extends BaseBean / HSData` 模式因双 baseline 实证容许保留（不阻塞验收） |
| **R6.3c** | **MUST NOT abort** | **全局请求**：App 级初始化 / 跨页轮询 / 用户态预加载 / `IonBusiness.loadPrices` / `UseCountManager.preloadAllCounts` 等"必须存活到下个页面"的请求 | **禁止**在页面 `aboutToDisappear` / `onPageHide` abort 这类请求；signal 一般也不传（无意义）。**audit 命中"全局请求被挂上了页面级 abort" → 必报 P1（误杀风险）**。强行 abort 会让下个页面拿不到登录态/价格表/全局配置，是真实运行时 bug |
| **R6.3d** | **MUST abort** | **非全局请求**：页面专属业务接口、详情页拉取、列表分页、上传/下载任务等 | **必须**传 `signal` + 在 `aboutToDisappear` / `onPageHide` abort。**分两层检测**：(1) **API 层**（`*Api.ets` / `*Service.ets`）函数签名应含 `signal?: AbortSignal` 参数；(2) **调用层**（页面 / ViewModel）必须 `new AbortController()` 把 `.signal` 传入 API 调用、并在生命周期回调里 abort。**audit 命中"未传 signal 或未 abort" → 必报 P1，无豁免**——内存泄漏 + 页面销毁后 setState 错乱是真实 bug。**实现样例**详见 [`05-network-persistence.md` § R6.3c-R6.3e](./05-network-persistence.md) |
| **R6.3e** | **SHOULD abort** | **第三方请求**：ExternalReqUtil（私仓） + 外部 SDK 网络（含 Web SDK、广告 SDK、推送 SDK 网络层等） | **一般应该**带 signal + abort（第三方接口超时/失败概率高，及时 abort 释放连接对资源关键）。**audit 默认报 P1**，execution-log 给出明确业务理由（如埋点 fire-and-forget 容忍丢失）后可降级豁免 |
| **R6.4a** | MUST | KV 走 PreferenceUtil（私仓） | grep `@ohos.data.preferences` 直接调用且未走 PreferenceUtil（私仓）→ P1 |
| **R6.4b** | **MUST**（客户校准升级） | 关系型数据库**必须**用 `@ohos/dataorm` 实体注解，禁止裸 `relationalStore` | **客户明确反馈**：必须用 `@ohos/dataorm` 框架 + `@entity/@column` 实体映射表，避免手写 CREATE TABLE / RdbPredicates / parseResultSet 样板代码。`oh-package.json5` 必须依赖 `@ohos/dataorm`。**DAO 层 raw `@kit.ArkData / @ohos.data.relationalStore` 实现的 baseline 豁免已撤销**——AI baseline 的 WorksDao 模式视为遗留待整改。**audit grep**：`from ['"]@kit\.ArkData['"]\|from ['"]@ohos\.data\.relationalStore['"]` 且无 `@ohos/dataorm` 依赖 → P1 |
| **R6.5a** | **MUST**（客户升级） | "开启沉浸式全面屏后，**应**利用 WindowModel（私仓）...windowTopPadding/BottomPadding" | 客户已校准为 MUST。鸿蒙工程必须预留顶/底安全距：顶部用 `WindowModel.windowTopPadding`，底部用 `windowBottomPadding`；**禁止**写死 `padding({top:36})` 这种固定值。BaseViewModel（私仓）已直接暴露这两个属性 |
| **R6.5b-1** | **MUST**（客户升级） | List 的 `lanes` / Grid 的 `columnsTemplate` 必须用 BreakpointModel（私仓）动态取列数 | grep `lanes(数字)` 或 `columnsTemplate('1fr 1fr...')` 写死，命中 → P1。正确做法：`.lanes(this.vm.breakpoint.gridColumns)` |
| **R6.5b-2** | SHOULD | 普通容器布局应用 GridRow + GridCol + BreakpointModel（私仓）适配折叠屏/小窗 | 单一 Column/Row 写死宽度且无 GridRow/GridCol 替代 → P2 warning；phone-only 项目可豁免 |
| **R6.5c** | SHOULD | "**应尽量避免**使用 Stack/Column/Row/Flex 嵌套过多层级，**可**利用 RelativeContainer" | 单文件最大嵌套 > 6 层 标 warning；不强制 |
| **R6.5e** | SHOULD | "对于**复杂布局**，**应尽量避免**将所有的布局代码全部集中在一个方法内部，可利用 @Builder/@LocalBuilder/自定义组件 @ComponentV2 进行拆分" | 单 `build() {...}` 方法体超过 ~150 行 → P2 warning，建议拆 @Builder/@LocalBuilder |
| **R6.5d** | MUST | "若父容器为 List、Scroll，**应尽量避免**子容器使用 RelativeContainer（无法自动计算宽高导致**无法滑动**）" | 此条措辞虽是"应尽量避免"但**后果是 bug**，必须改：grep List/Scroll 子树包含 RelativeContainer |
| **R6.6** | **MUST**（客户升级） | "**请于**壳工程下 build-profile.json5 配置 buildProfileFields（appName / appBaseType / ChanelId / WXAppId / WXAppSecret / umengId 等）" | 客户已校准为 MUST。即使工程没有 WX/umeng 等三方 key，**appName / appBaseType / ChanelId 也必须填**（运营基础信息）。三方 key 按工程实际有的再加 |

---

## audit 报告的输出结构

```markdown
# Refactor Audit

## P0 必改（MUST，影响后续所有改造或会引发运行 bug）
- ...

## P1 必改（MUST，影响代码可维护性）
- ...

## P2 警告（SHOULD，建议改但用户可豁免）
- ...

## 提示（MAY / 信息）
- ...
```

## audit 不应该做什么（AI baseline 强约束）

- ❌ 把 `viewmodels`（复数）/`services`/`dialog` 等目录命名当违规
- ❌ 把业务自有色（slide_track_color、digital_video_bg）当违规
- ❌ 把 WebSocket 用法当 HTTP 网络请求违规
- ❌ 把链中间继承层（class A extends ParentVM）的 ViewModel 当未继承 BaseViewModel（私仓）
- ❌ 把组件内部 padding 当页面间距违规
- ❌ 把所有 SHOULD 项放进 P1 强制改造
- ❌ **强制要求 business_common color.json 包含全部 19 个通用 token**——这只是建议
- ❌ **把 products/phone 的 `app_theme / text_color / btn_*_Color` 等命名标违规**——非规范名仍允许
- ❌ **把"业务 VM 未继承 BaseViewModel（私仓）"标违规**——仅复杂页面 VM 要求
- ⚠️ ~~**把 widget/dialog/builder/特殊渲染组件的 v1 装饰器标违规**——这些场景容许~~ → **客户校准为 MUST 全局 v2，无场景豁免**。所有 v1 装饰器（含 widget/dialog/builder/特殊渲染）一律 P1 改造
- ❌ **把单点 axios 使用标违规**——特殊场景容许，仅大面积命中才报
- ⚠️ ~~**把 DAO 层用 raw relationalStore 标违规**——封装实现合理~~ → **客户校准为 MUST 用 @ohos/dataorm**，DAO 层 raw 实现也算违规，按 P1 整改
- ❌ **要求根 oh-package.json5 配 overrides**——Scan 没配也合规
- ❌ **强制 lib_common（私仓）用某个具体版本**——AI 用 1.1.5、Scan 用 1.1.8，按工程当时稳定版即可
- ❌ **把 `*VM/*ViewModel` 未继承 BaseViewModel（私仓）一律标违规**——只有 `*PageVM/*PageViewModel` 主页面状态容器才约束
- ⚠️ ~~**把引导组件（Guide*）的 v1 装饰器标违规**——Scan 的 GuideCheckMark 在豁免范围~~ → **客户校准为 MUST**，引导组件也必须 v2。Scan baseline 中 GuideCheckMark 的 v1 残留视为遗留待整改
- ❌ **把 `import { ... } from '@ohos/axios'` 类型导入当 axios 调用违规**——Scan 4 处类型导入合规
- ❌ **把存量 png 标 P0** —— R4.1 客户升级为 MUST 后，**新增** png 才算 P0；存量 png 走 P1 资源迁移待办
- ❌ **把 `extends BaseBean` 类型 DTO 标 P0** —— R6.3b 升级为 SHOULD 但项目历史模式容许保留，新写代码才优先 interface
