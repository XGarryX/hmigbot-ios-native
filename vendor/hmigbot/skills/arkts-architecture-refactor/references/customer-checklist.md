# 鸿蒙客户端原生开发规范 — 合规自检清单（通用模板）

> 依据：五方合创《鸿蒙客户端原生开发规范》(develop_rule.docx) + AI/Scan 双 baseline 工程校准
> 适用：任何 HarmonyOS / ArkTS 项目的架构合规自检
> 用法：逐条勾选，记录每条规则的实证情况

---

## 严格度分级

| 级别 | 规范措辞 | 处理 |
|---|---|---|
| **MUST** | "必须 / 务必 / 统一" | 必达成 |
| **SHOULD** | "应 / 尽量 / 避免" | 建议达成，可豁免 |
| **MAY** | "可 / 例如 / 以下是实例" | 信息项，不计入差距 |

> **私仓声明**：本清单中凡标注"（私仓）"的依赖（lib_common / lib_network / lib_widget 等）以及类（RouterUtils / RequestUtil / ExternalReqUtil / PreferenceUtil / ColorUtils / BaseViewModel / BreakpointModel / WindowModel 等）均来自公司自有私仓 `repo.dadoubk.cn`。**优先原则**：能用私仓的能力，就一定要用私仓——不要自己造轮子，也不要绕过私仓直接用底层 API。

---

## 〇、ArkTS 语法基线（R0）

| ☐ | ID | 严格度 | 检查点 | 通过条件 |
|---|---|---|---|---|
| ☐ | R0.1 | **MUST** | 遵循鸿蒙官方 ArkTS 编码规范 | 参考鸿蒙官方文档：<https://developer.huawei.com/consumer/cn/doc/harmonyos-guides-V5/arkts-coding-style-guide-V5> —— 命名 / 缩进 / 类型注解 / null safety 等基础语法约束都按官方走 |

---

## 一、工程结构（R1）

| ☐ | ID | 严格度 | 检查点 | 通过条件 |
|---|---|---|---|---|
| ☐ | R1.1 | **MUST** | 三段式骨架是否齐备 | 根目录有 `products/<shell>` + `features/business_*` + （可选 `components/module_*`） |
| ☐ | R1.2 | **MUST** | 不同业务代码已拆为独立 business 工程 | 没有把多个不同业务域的 page 堆在同一个 module 里（避免 entry 单模块大杂烩）|
| ☐ | R1.3 | **MUST** | 三段式 = products + features + **components**，components/ 不能省 | 项目根 `components/` 必存在；至少 1 个 `components/module_*`；空目录或缺 components 都不合规 |

## 二、私仓接入 / 依赖（R2）

> ⚠️ **私仓优先**：能从私仓 `repo.dadoubk.cn` 获取的能力（路由 / 网络 / 持久化 / 颜色工具 / 通用组件 / 基类等），**一律用私仓**。禁止以"自己写更灵活"或"赶进度"为由绕过私仓——这是规范第二章的核心要求。

| ☐ | ID | 严格度 | 检查点 | 通过条件 |
|---|---|---|---|---|
| ☐ | R2.0 | **MUST** | 私仓优先原则（无重复轮子） | 业务代码**禁止**自造 RouterUtils / PreferenceUtil / HTTP 封装 / ColorUtils / BaseViewModel / BreakpointModel / WindowModel 等已在私仓 lib_common / lib_network / lib_widget 提供的能力。以"自己写更灵活/赶进度"为由绕过私仓即视为违反 R2.0|
| ☐ | R2.1 | **MUST** | `.ohpmrc` 配置（私仓） | 文件存在且 `registry=` 含 `repo.dadoubk.cn`（其他公共/字节镜像保留即可）|
| ☐ | R2.2-a | **MUST** | lib_common（私仓）接入 | `oh-package.json5` 引用 lib_common，提供 BaseViewModel（私仓）/ RouterUtils（私仓）/ PreferenceUtil（私仓）/ ColorUtils（私仓）/ BreakpointModel（私仓）/ WindowModel（私仓）等基础能力 |
| ☐ | R2.2-b | **MUST** | lib_network（私仓，仅当用到 HTTP 网络请求）| 业务 HTTP 调用走 `RequestUtil`（私仓）/ `ExternalReqUtil`（私仓）；单点特殊封装（如下载）可豁免 |
| ☐ | R2.2-c | **MUST** | lib_payment（私仓，仅当有支付）| 支付走 lib_payment 而非直连三方 SDK |
| ☐ | R2.2-d | **MUST（条件）** | lib_starburst（私仓）= **内容提供平台 SDK**，**不是数据上报库** | 当业务**调用内容平台接口**时（如素材列表、运营位、推荐内容等），**必须直接复用 lib_starburst 私仓提供的 API**，禁止自己写 HTTP/类型定义/响应解析等。无相关接口调用就不引此包 |
| ☐ | R2.2-e | **MUST** | lib_umeng（私仓，仅当有推送）| 接入 lib_umeng |
| ☐ | R2.2-f | **MUST** | lib_hmiap（私仓，仅当用应用内购）| 接入 lib_hmiap |
| ☐ | R2.2-g | **MUST** | lib_widget（私仓） | 公共 ArkUI 组件优先用 lib_widget 提供的，避免自造重复轮子 |
| ☐ | R2.3 | **MUST** | lib_hmiap 版本约束 | 未启用鸿蒙联运 → lib_hmiap 必须 1.0.0；启用 → 按要求版本 |
| ☐ | R2.4 | MAY | 根 oh-package.json5 overrides 锁版本 | 多模块 lib_* 出现版本漂移时配；否则可不配 |

## 三、代码分层（R3）

| ☐ | ID | 严格度 | 检查点 | 通过条件 |
|---|---|---|---|---|
| ☐ | R3.1 | SHOULD | 业务代码按模块功能拆分 | `ets/` 下能看到 components / constants / pages / viewmodel / bean / util 等子目录（命名复数/单数都允许）|
| ☐ | R3.2 | SHOULD | 类职责单一 | 单 .ets 文件不超过 ~500 行 / 单 class 不超过 ~10 public 方法 *(skill 建议值，docx 仅要求"职责单一"未给具体阈值)* |

## 四、静态资源（R4）

| ☐ | ID | 严格度 | 检查点 | 通过条件 |
|---|---|---|---|---|
| ☐ | R4.1 | **MUST** | 图片用 webp/svg | 静态图片资源必须 webp 或 svg；新增资源不允许 png/jpg；存量 png 列入资源迁移待办 |
| ☐ | R4.2 | **MUST** | webp 3 倍图 | webp 应按设计稿 3 倍尺寸出图（对应 Android xxhdpi 倍率）|
| ☐ | R4.3 | **MUST** | 动画用 webp 不用 gif | 动画资源用 webp，**禁止使用 gif**（对齐 Android）|
| ☐ | R4.4 | **MUST** | 单色 webp 着色 | 需要不同色版的图标，**采用单色 webp + ColorUtils.hexToColorMatrix（私仓）+ Image.colorFilter** 实现，不要预生成多色版本|

## 五、公共样式（R5）

| ☐ | ID | 严格度 | 检查点 | 通过条件 |
|---|---|---|---|---|
| ☐ | R5.1-a | MAY | 19 个跨平台同名 token 建议补全 | 信息项，业务自有命名（app_theme / text_color 等）允许 |
| ☐ | R5.1-b | MAY | 业务自有色定义 | 业务模块可自定义色（如 slide_track_color），不算违规 |
| ☐ | R5.2 | SHOULD | 字体 weight 优先 UI 稿数值 | 避免大量 `FontWeight.Bold`，按 UI 稿 weight 数值；尤其 Android 迁移代码 |
| ☐ | R5.3 | SHOULD | 页面左右间距统一 BreakpointModel.pagePadding（私仓）| 仅检查页面最外层容器，组件内部 padding 不算 |

## 六、其他规范（R6）

### 6.1 状态管理 v2

| ☐ | ID | 严格度 | 检查点 | 通过条件 |
|---|---|---|---|---|
| ☐ | R6.1a | **MUST** | 业务页面/普通组件统一 v2 | 普通业务 `@ComponentV2` + `@Local/@Param/@Provider`；widget / dialog / builder / 特殊渲染组件容许 v1 |
| ☐ | R6.1b | **MUST** | Repeat 替代 LazyForEach | **列表必须用 Repeat**——LazyForEach 已被规范明确"尽量替代"；仅在已知 Repeat 不支持的极少数场景（如某些 SDK 内置组件强制 LazyForEach）才豁免 |
| ☐ | R6.1b' | **MUST** | LazyForEach→Repeat 时 RepeatItem 整体传 @Builder | `Repeat<T>().each((obj: RepeatItem<T>) => { ... })`；**严禁**解构成 `(item, idx) => {}`（@Trace 字段更新会失效）。**拆 @Builder 渲染 item 时同样必须传整个 `obj: RepeatItem<T>`，不能传 `obj.item`**——客户反馈实证：传 `obj.item` 会让 @Trace 字段刷新失效（item 变更不触发 UI 重绘），audit 命中即 P1 |
| ☐ | R6.1b'' | **MUST** | Repeat 渲染懒加载列表必须加 `.virtualScroll()` | 客户反馈：长列表 / 分页列表 / 任何需要懒加载（窗口外不渲染）的场景，`Repeat<T>(...).each(...).virtualScroll({ totalCount: ... })` 链上**必须有 `.virtualScroll()`**，否则会一次性创建全部 item，等价于 ForEach。短列表（< 屏 + 一屏）可豁免，但要在报告里声明 |
| ☐ | R6.1c | SHOULD | 主页面 VM 继承 BaseViewModel（私仓） | 仅约束 `*PageVM / *PageViewModel`；辅助型 / 工具型 VM 可不继承 |
| ☐ | R6.1d | **MUST** | 业务页面禁止重复 `AppStorageV2.connect(WindowModel, ...)` | 客户反馈实证：**业务 page 已通过 BaseViewModel（私仓，含 `windowModel: WindowModel` 字段）拿到 windowModel，不应该再写 `windowModel = AppStorageV2.connect(WindowModel, () => new WindowModel())!`**——重复 connect 是冗余且违背"VM 暴露状态"的分层原则。**audit grep**：业务 page 文件（非 ability / 非全局状态层 / 非无 vm 的纯组件）出现 `AppStorageV2.connect(WindowModel` → P1。**正确写法**：`this.vm.windowModel.windowTopPadding` / `this.vm.windowModel.windowBottomPadding`（vm 必须继承 BaseViewModel）。**例外**：纯展示组件（如 NavHeaderBar 等）若没有 vm 注入，可直接 connect；全局状态层（GlobalStateModels）作为单一真理源应当保留 |
| ☐ | R6.1f | **MUST** | page 上禁止 `pathStack: NavPathStack = ...` 字段声明（2026-05-07 客户实证）| 客户反馈：**page 不应该单独声明 pathStack 字段**。AIPPT_ArkTS_rebuild 参考实现中 page 仅有 `private vm: XxxVM = new XxxVM()` 一个业务字段。pathStack 通过 `RouterUtils.getStack()` 在调用点 inline 取，或在 vm 上加 `@Trace stack: NavPathStack` 让 onReady 同步给 vm。**audit grep**：`grep -rn "pathStack\s*:\s*NavPathStack\s*=" features/*/src/main/ets/pages` 命中 → P1 |
| ☐ | R6.1g | **MUST** | page 顶部业务 `@Local` 字段必须 ≤ 3 个（2026-05-07 客户实证）| 客户原话："已经有了 vm，那个这些状态都应该收敛到 vm 里面去"。除了**纯 UI 控制 flag**（弹窗显隐 / 动画角度 / 滚动位置等），所有业务字段（输入值、列表、loading、disabled、倒计时、第三方授权状态等）必须 `@Trace` 挪到 VM。page 持有 `private vm: XxxVM = new XxxVM()` 后，page 顶部 `@Local` 数量超过 3 通常意味着没收敛。**audit**：每页统计 `@Local`，>3 个进 P1 名单（重灾区 page 需抽 VM）|
| ☐ | R6.1h | **MUST** | 业务 VM 不能再手动 `UserPreferences.setX(userData.x)` 30+ 行（2026-05-07 客户实证）| 客户反馈：LoginViewModel.loginWithSms 内 30+ 行 `UserPreferences.setNickname / setAvatar / setVipLevel / setVipDays / ...` 是 R6.8-C 反模式。**正确做法**：用私仓 `AccountApi.bindPhone` / `AccountApi.wechatLogin` 等私仓 API 替代业务自建 `UserApiService.bindMobileBySmsCode` 等——私仓 API 内部已写 LibUserData 并落盘。**audit grep**：单文件出现连续 5+ 个 `UserPreferences.set` 调用 → P0 违规 |
| ☐ | R6.8-F | **MUST** | LoginViewModel 必须用 `lib_network.AccountApi`，禁止业务自建登录链 + 手动 mirror 用户字段（**2026-05-08 客户实证第 4 次**）| 客户截图圈出 LoginViewModel 内 13+ 行 `lib.token = userData.token / lib.userId = userData.userId / lib.vipLevel = userData.vipLevel / ...` 手动赋值并附 `LoginVM(1).ets` 标准实现要求重写。**正确做法**：业务侧持 `private accountApi: AccountApi = new AccountApi()`，登录全部走 `accountApi.bindPhone/wechatLogin/harmonyLogin/sendSmsCode/signOut/closeAccount`，私仓自治写 LibUserData。**audit grep**：① `grep -rn "applyUserDataToLib\|mirrorUserData\|copyUserData" features` 期望 0；② `grep -rn "userApiService\.\(bindMobile\|bindWx\|bindAli\|logout\)" features/business_login` 期望 0（应全部 AccountApi）；③ `grep -rn "lib\.\(token\|userId\|vipLevel\|nickName\|headUrl\|avatar\|phoneAuth\|userState\|fromChannel\)\s*=" features/business_login` 期望 0；④ `business_login/oh-package.json5` 必含 `lib_network` 直接依赖。**详见 [05-network-persistence.md § R6.8-F](./05-network-persistence.md#r68-f)**，含完整 LoginViewModel 模板代码 |
| ☐ | R6.4a | **MUST** | dataorm entity 主键字段必须 `id: number \| null = null`，DAO 必须用 `dao.insertOrReplace(entity)` 原生调用，禁止业务自己拼 `ValuesBucket` + raw RdbStore.insert（**2026-05-08 客户实证**）| 客户原话："dao 层 插入数据 应该用 @ohos/dataorm 封装好的 直接插入对象就可以，不需要把字段列出来 然后用原生 api 插入"。**根因**：`id: number = 0` 字面 0 不被 bindValues 跳过 → INSERT 时 id 字面写入 → sqlite 不 autoincrement → 所有新行 id=0 互相覆盖。**正确**：① entity `@Id() id: number \| null = null`；② DAO `async insertX(form) { return await this.dao.insertOrReplace(form) }` 一行；③ 业务侧消费 `entity.id` 时用 `entity.id!` 非空断言（DB 加载的一定有 id）。**audit grep**：① `grep -B1 "id:\s*number\s*=\s*0" features/business_common/src/main/ets/model/entities/*.ets` 期望 0；② `grep -rn "ValuesBucket\s*=\s*{" features --include="*Dao.ets"` 期望 0；③ runtime 验证：生成多条数据 → 列表 dbId 应递增非 0 |
| ☐ | R6.9-A | **MUST** | page 同时持 vm + 单独 `@Local windowModel/breakpointModel` 是冗余声明（**2026-05-08 客户复审实证 — 44 + 13 处漏改**）| 客户原话："其他页面也出现了 已经有 vm，但是还是单独定义了 WindowModel，应该直接从 vm 获取。这个逻辑是所有页面通用的，详细检查下所有页面有没有这个问题。" **根因**：抽 VM 的 batch agent 看到 `@Local windowModel = AppStorageV2.connect(...)` 把它当 AppStorageV2 binding 保留。但 BaseViewModel 已自带 `windowModel`，**page 不需要单独绑**。**audit grep**：`for f in $(find features products -name '*Page.ets'); do has_vm=$(grep -cE '(private\|@Local) vm:\s*\w+ViewModel' "$f"); has_redundant=$(grep -cE '@Local (windowModel\|breakpointModel):' "$f"); [ "$has_vm" -gt 0 ] && [ "$has_redundant" -gt 0 ] && echo "VIOLATION: $f"; done` 期望 0 命中。⚠️ **大小写陷阱**：BaseViewModel 字段是 `breakPointModel`（大写 P），不是 `breakpointModel` —— 替换时全文 sed 必须连同改名 |
| ☐ | R6.10 | **MUST** | 登录态 / VIP 态判定**必须**走私仓 `LibUserData.getInstance().isBinding()` / `.isVip()`，禁止业务自建判定逻辑（**2026-05-08 客户实证**）| 客户原话："判断是否登录，采用 UserData.getInstance().isBinding() 判断，判断是否开通 vip，采用 UserData.getInstance().isVip() 判断"。**禁止**：① `await UserPreferences.isLogin()` 读独立 KV ② `userInfoModel.isLogin` 字段读 ③ `vipLevel > 0` / `vipLevel <= 0` 显式数值比较。**根因**：私仓 isBinding/isVip 内部包含完整判定逻辑（双条件 token+userId / 5min VIP 保护窗口 / userState 注销态等），业务侧手写比较会绕过这些细节，且不能跟随服务端语义演进。**audit grep**：① `grep -rn "await\s\+UserPreferences\.isLogin\s*("` 期望 0；② `grep -rn "userInfoModel\.isLogin\b"` 期望 0；③ `grep -rEn "vipLevel\s*(>\|<=\|>=\|===\|!==)\s*[0-9]"` 期望 0（除 MembershipRefresher 5min 保护窗口业务可豁免）。**详见 [05-network-persistence.md § R6.10](./05-network-persistence.md#r610)** |
| ☐ | R6.1b''' | **MUST** | Repeat 不能配合 LazyDataSource，virtualScroll() 不传参（**2026-05-09 客户实证**）| 客户原话："如果已经是 Repeat 组件了，数据源就不需要用 LazyDataSource 包裹，直接使用 Array 即可。然后 virtualScroll 属性后面不需要传参数"。**判定**：① `Repeat<T>(this.dataSource.getDataList())` ❌ 数据源残留 LazyDataSource；② `Repeat<T>(this.list).virtualScroll({ totalCount: ... })` ❌ virtualScroll 不传参；③ `Repeat<T>(this.list).virtualScroll()` ✅ 标准写法（list 是 `T[]`）。**配套清理**：删除 `private dataSource: LazyDataSource<T>` 字段、`dataSource.setData/reloadData/getDataList` 调用，改为直接赋值 `this.list = arr`。**audit grep**：`grep -rnE 'Repeat<[^>]+>\([^)]*\.getDataList\(\)' --include='*.ets'` + `grep -rnE '\.virtualScroll\(\s*\{' --include='*.ets'` + `grep -rn 'LazyDataSource' --include='*.ets'`，命中即 P1 |
| ☐ | R6.1e-2 | **MUST** | Page 业务逻辑必须下沉 VM，page 仅做 UI 编排（**2026-05-09 客户实证强化**）| 客户原话："page 页面中的 UI 和数据/状态没有剥离，所有交互都混杂在一起了 ... page 页面中的接口交互等无关 UI 交互的逻辑期望放到 vm 中去处理，现在 vm 基本是空闲状态"。**判定（page 文件命中即 P0）**：① `await\s+\w+(Service\|Api\|Repository\.getInstance\(\)\|MembershipRefresher\|UseCountManager\|IonBusiness)` —— 业务调用必须移 vm；② `setInterval\|setTimeout` —— 定时器移 vm（vm.cancel() 释放）；③ `new AbortController` —— vm 持有 + dispose；④ `private async \w+(submit\|fetch\|load\|create\|generate\|process)` —— 业务方法必须命名 `vm.start()/onXxxClick()` 后挪 vm；⑤ page 文件 > 300 行业务代码（去除 UI 模板后）通常代表违规。**正确做法**：page 内只剩 ① `private vm: XxxVM = new XxxVM()` 一个业务字段、② `aboutToAppear() { this.vm.start() }` + `aboutToDisappear() { this.vm.dispose() }` 两行生命周期、③ UI 事件回调一行 `.onClick(() => this.vm.onSubmit())`、④ build() 只用 `this.vm.@Trace 字段`。客户参考实现：VFXCreateViewModel 把 sourceImageUri / functionType / generatingText / errorType / canClose 都 @Trace 在 vm，page 只负责 UI 渲染 |
| ☐ | R5.4 | **MUST** | 标题栏统一用私仓 `lib_widget.NavHeaderBar`（**2026-05-09 客户实证**）| 客户原话："底层封装了通用的标题组件 NavHeaderBar，期望现有布局中的非特殊标题样式使用通用标题组件，现在好多页面都是写的重复代码自定义的标题"。**判定**：① 任何 `Image($r('app.media.ic_title_white_back'))` / `Image($r('app.media.back'))` / `Image($r('app.media.ic_back'))` + onClick pop 的手写返回按钮 → ❌；② 配套的 `Text(title).fontSize(18).fontColor(...)` 顶部标题文字组合 → ❌。**正确做法**：`import { NavHeaderBar } from 'lib_widget'`；`NavHeaderBar({ title: 'xxx', rightPartBuilder: this.RightArea })` —— 默认右上角空、点击返回走 `RouterUtils.pop()`，通过 `onBack` event 自定义返回逻辑、`rightPartBuilder` @BuilderParam 注入右侧自定义内容、`bgColor` / `titleColor` / `backColor` / `backImg` 调主题。**例外**：① 特殊定制标题（如带搜索框 / Tab 切换 / 大量自定义视觉）保留自写并在 ADR 记录；② 全屏沉浸式页面（无标题栏）不适用。**audit grep**：`grep -rln "ic_title_white_back\|app.media.back\|app.media.ic_back" features/*/src/main/ets/pages` 命中 → P1，统一替换 |
| ☐ | R6.1c-2 | **MUST** | Page-scope / Fragment-scope ViewModel **禁止单例**（**2026-05-09 客户实证**）| 客户原话："HomeViewModel 没必要写成单例的"，并要求**全局排查**所有 ViewModel。**判定**：① `*PageViewModel` / `*FragmentViewModel` / `*PageVM` / `*FragmentVM` —— ❌ 禁止 `private static instance` + `getInstance()` + `clearInstance()` 三件套；② `*Manager` / `*Service` / `*Repository` / `*Refresher` —— ✅ 单例可接受（属于 Service / 全局态层）。**根因**：page-scope VM 单例会导致同页面多次进入复用旧状态、@Trace 字段跨页面污染、clearInstance 时机模糊。**整改**：① 删三件套；② page 调用方从 `XxxViewModel.getInstance()` → `new XxxViewModel()`（用 `@Local` 持有）；③ 跨页共享改用 `AppStorageV2.connect(VM, () => new VM())`。**audit grep**：`grep -rnE 'private\s+static\s+instance.*ViewModel' --include='*.ets'` + `grep -rnE 'static\s+getInstance\(\)\s*:\s*\w+ViewModel' --include='*.ets'`，排除合法单例后命中即 P1 |
| ☐ | R6.1e | **MUST** | Page 仅做编排，业务逻辑必须下沉到 ViewModel | 客户反馈实证：**Page 文件已经持有 vm，就不应该再在 page 内写网络请求、定时器、本地存储读写、复杂状态计算、长串业务流程编排等**。Page 的职责仅限：① 解析路由参数 → 调 `vm.applyRouterContext(...)` 转交；② 在生命周期回调（`aboutToAppear` / `aboutToDisappear` / `NavDestination.onShown` 等）一两行调 `vm.start()` / `vm.cancel()`；③ UI 事件回调一行调 `vm.onXxxClick()`；④ 渲染基于 `vm.@Trace` 字段。**禁止**写法：page 内 `private xxxTimer: number = -1` / `private async fetchXxx(...)` / `setInterval(...)` / `await someService(...)` / 本地 sqlite / preferences 直接读写。**audit grep**：page 文件 `private \w+Timer\|setInterval\|setTimeout\|new AbortController\|async \w+\|await \w+\.|preferences\.\|relationalStore\.\|http\.` 命中且不在 vm 转发处 → P1。**正确做法**：把这些逻辑搬到 `*ViewModel.ets`，在 vm 内提供 `start() / cancel() / onSomethingClick()` 等方法供 page 一行调用。"page 越薄越好"是分层原则，page 文件超 300 行业务逻辑通常意味着违规 |

### 6.2 路由

| ☐ | ID | 严格度 | 检查点 | 通过条件 |
|---|---|---|---|---|
| ☐ | R6.2a | **MUST** | Navigation + RouterUtils（私仓）统一路由 | 0 处 `router.pushUrl/replaceUrl/back/clear`；统一走 `RouterUtils.pushPathByName` 等 |
| ☐ | R6.2b | **MUST** | 路由名称用常量类，禁止业务代码裸字符串 | 工程里有 `RouterMap`（或同等）常量类集中定义所有页面名；**业务代码调 `RouterUtils.pushPathByName/replacePathByName/getNavParam` 等的第一个参数必须是常量引用**（如 `RouterMap.MEMBER_CENTER_PAGE`），**禁止裸字符串字面量**（如 `'MemberCenterPage'`）。客户反馈核心痛点：散落在 40+ 处的字符串"魔法值"无法重构、改名易漏。同步要求：page 自身的 `@RouterMap({ name: ... })` 注解也用常量。**audit 命中裸字符串 → 必报 P1** |
| ☐ | R6.2c | **MUST** | NavDestination 必须由 page 自身的 `build()` 返回，禁止由 `RouterBuilders.ets` 在外层包 | 客户反馈实证：**`NavDestination()` 是 page 的"运行时载体"**，需要 page 自身订阅 `onShown` / `onHidden` / `onBackPressed` / `onWillAppear` 等生命周期回调，并按业务设置 `mode` / `systemBarStyle` / `hideTitleBar` 等属性。**错误写法**（在 RouterBuilders.ets 外层包）：`@Builder function XxxPageBuilder() { NavDestination() { XxxPage() }.hideTitleBar(true) }` ——这种写法 page 内部拿不到 NavDestination 引用，无法挂生命周期回调。**正确写法**：RouterBuilders 只 wrap page（`@Builder function XxxPageBuilder() { XxxPage() }`），page 自身 `build() { NavDestination() { ... }.hideTitleBar(true).onShown(...).onBackPressed(...) }`。**audit grep**：`RouterBuilders` 文件中 `NavDestination()\s*\{` 命中 → P1 |
| ☐ | R6.2d | **MUST** | Navigation + NavDestination 模式下生命周期必须挂在 NavDestination 上 | 客户反馈实证：**`@Component struct` 上的 `onPageShow` / `onPageHide` / `onBackPress` 是 @Entry + 老 router 的钩子**，在 Navigation + NavDestination 路由栈中**根本不会触发**。必须改为 NavDestination 链式 `.onShown(() => {...})` / `.onHidden(() => {...})` / `.onBackPressed(() => { ...; return true })` / `.onWillShow(...)` / `.onWillHide(...)`。**对应关系**：`onPageShow` → `.onShown`（页面进入前台）；`onPageHide` → `.onHidden`（页面退到后台）；`onBackPress(): boolean` → `.onBackPressed(() => boolean)`（系统返回拦截，return true 表示已消费）。**audit grep**：业务 page 文件出现 `^\s+(onPageShow\|onPageHide\|onBackPress)\s*\(\s*\)` 即 P1（需移到 NavDestination 链式调用）。**audit 反向**：page build() 返回 NavDestination 但既无 `.onShown(` 也无任何业务初始化代码外露 → 自检是否漏挂回调 |

### 6.3 网络

| ☐ | ID | 严格度 | 检查点 | 通过条件 |
|---|---|---|---|---|
| ☐ | R6.3a | **MUST** | 公司 API 走 RequestUtil（私仓）；第三方走 ExternalReqUtil（私仓）| 业务 axios/http 大面积使用 → 必改；单点特殊场景（如文件下载、特殊 header）可豁免 |
| ☐ | R6.3b | SHOULD | DTO 用 interface 优先 class | 反序列化优先用 interface（可空字段加 `?` 或 `\| undefined`）；`extends BaseBean / HSData` 模式因项目历史允许保留，但新写代码应优先 interface |
| ☐ | R6.3c | **MUST NOT** | **全局性请求 — 禁止在页面退出时 abort** | **App 级初始化 / 跨页存活的轮询 / 用户态预加载 / IonBusiness.loadPrices / UseCountManager.preloadAllCounts** 等。这类请求的生命周期**跨页面**，强行 abort 会误杀核心数据流，导致下个页面拿不到登录态 / 价格表 / 全局配置。**audit 命中"全局请求在页面 aboutToDisappear/onPageHide 里被 abort 了" → 必报 P1（误杀风险）**。execution-log 必须把这类请求归类为"全局"并明确不挂页面 abort |
| ☐ | R6.3d | **MUST** | **非全局请求 — 必须传 signal 并在退出时 abort** | **页面专属业务接口、详情页拉取、列表分页、上传/下载任务** 等。**audit 命中"非全局请求未传 signal 或未在 aboutToDisappear/onPageHide abort" → 必报 P1**。不允许借口豁免——内存泄漏 + 页面销毁后 setState 错乱是真实 bug，不是审美问题 |
| ☐ | R6.3d-i | **MUST** | abort 后禁止立刻 `new AbortController()` 重建 | 客户反馈实证：**`abort()` 是"该 controller 完成使命、生命周期结束"的语义**，紧跟一行 `this.xxxController = new AbortController()` **没有意义**——若 page 已销毁不会再有请求；若需要"再次发起请求"（如重新生成 / 下拉刷新），应在**重启操作的方法入口**（如 `startGeneration`、`reload`）开头 `new` 新 controller，而不是塞在 cancel 收尾。**audit grep**：`\.abort\(\)\s*\n\s*this\.\w*[Cc]ontroller\s*=\s*new\s+AbortController` → P1 |
| ☐ | R6.3d-ii | **SHOULD（重点关注）** | 一个 page 多个并发请求，禁止共用单一 AbortController | 客户反馈实证：当前项目反模式——**每个 page 用一个 `private abortController` 兜住所有请求**。这在多请求并发场景下有问题：①「重新生成大纲」会误杀同时进行的「拉用户信息」；②单步取消能力丢失（无法只 abort 一个慢请求）。**正确做法**：按"用户视角的同一操作"分组——同一操作内的串行子请求共用一个 controller，不同操作各持自己的 controller（如 `loginAbortController` / `smsAbortController` / `productListAbortController`）。**audit 反向**：page 内只有 1 个 `abortController` 但 vm/page 发起 ≥ 3 个不同业务请求 → P2 警告，建议拆分。**实操**：单请求 page（详情页、设置页）保留 1 个 controller 是合理的；多并发请求 page（登录页同时发短信+登录+三方授权 / 首页多 Tab 各自加载）应按业务拆 |
| ☐ | R6.3e | **SHOULD（重点关注）** | **第三方请求 — 一般建议 abort，业务理由可豁免** | **ExternalReqUtil（私仓）+ 外部 SDK 网络**（Web SDK / 广告 SDK / 推送 SDK 网络层等）。第三方接口超时/失败概率高，及时 abort 释放连接对资源很关键。**audit 默认报 P1**；execution-log 给出明确业务理由（如埋点 fire-and-forget 容忍丢失）后可降级为豁免 |

### 6.4 持久化

| ☐ | ID | 严格度 | 检查点 | 通过条件 |
|---|---|---|---|---|
| ☐ | R6.4a | **MUST** | KV 存储统一 PreferenceUtil（私仓） | 业务代码不直接 `@ohos.data.preferences`，走 PreferenceUtil 封装 |
| ☐ | R6.4b | **MUST** | 关系型数据库统一 @ohos/dataorm，禁止裸 relationalStore | 客户明确反馈：**关系型数据必须用 `@ohos/dataorm` 框架，通过 `@entity` + `@column` 实体注解映射数据库表**，避免手写 `CREATE TABLE` SQL / 手拼 `RdbPredicates` / 手写 `parseResultSet` 这类样板代码。`oh-package.json5` 必须依赖 `@ohos/dataorm`。**DAO 层也不允许裸 `@kit.ArkData` / `@ohos.data.relationalStore`**——之前 baseline 里 DAO 层 raw 实现的豁免**已撤销**。**audit 命中业务代码或 DAO 层 import `relationalStore` 且未走 dataorm → 必报 P1** |

### 6.5 页面布局

> **核心要求**：鸿蒙工程必须**预留顶部 + 底部安全距离**，**所有布局必须用动态布局**以适配折叠屏 / 小窗，**List 和 Grid 必须用动态布局**取列数。

| ☐ | ID | 严格度 | 检查点 | 通过条件 |
|---|---|---|---|---|
| ☐ | R6.5a | **MUST** | 沉浸式安全距用 WindowModel（私仓）| 顶部用 `WindowModel.windowTopPadding`、底部用 `windowBottomPadding`；**禁止**写死 `padding({ top: 36, bottom: 24 })` 等固定值。BaseViewModel（私仓）已直接暴露这两个属性 |
| ☐ | R6.5b-1 | **MUST** | List / Grid 列数动态化 | List 的 `lanes` / Grid 的 `columnsTemplate` 必须由 BreakpointModel（私仓）的 `gridColumns` 等属性动态获取，**禁止**写死 `lanes(2)` 这种 |
| ☐ | R6.5b-2 | SHOULD | 普通布局多端适配 | 优先用 GridRow + GridCol + BreakpointModel（私仓）实现折叠屏 / 小窗适配；仅 phone 设备项目可豁免 |
| ☐ | R6.5c | SHOULD | 嵌套层级避免过深 | 单文件嵌套深度 ≤ 6 层；可用 RelativeContainer 拍平 *(skill 建议值，docx 仅要求"避免过深"未给具体层数)* |
| ☐ | R6.5d | **MUST** | List/Scroll 子项不能用 RelativeContainer | 否则**无法滑动**（已知 bug，硬性约束）|
| ☐ | R6.5e | SHOULD | 复杂布局拆 @Builder / @LocalBuilder | 单 `build()` 方法不超过 ~150 行 *(skill 建议值，docx 仅要求"避免集中在一个方法"未给具体行数)* |

### 6.6 其他配置

| ☐ | ID | 严格度 | 检查点 | 通过条件 |
|---|---|---|---|---|
| ☐ | R6.6 | **MUST** | build-profile.json5 配 buildProfileFields | 壳工程 `build-profile.json5` 的 `targets[].config.buildOption.arkOptions.buildProfileFields` 必须配置 app 基础信息（appName / appBaseType / ChanelId）以及工程实际用到的三方 key（WXAppId / WXAppSecret / umengId 等）。即使没有三方 key，appName/appBaseType/ChanelId 也必须填 |

---

## 验收说明

### 必达成（MUST）红线
- 全部 MUST 项必须通过，否则视为**不合规**
- MUST 中带"仅当用到 X"的（如 lib_network 仅当用 HTTP），按工程实际业务判断
- 私仓优先原则：能用私仓的能力一律用私仓，自己造轮子或绕过私仓视作违反 **R2.0**

### 软规则（SHOULD）
- 建议达成，但项目方可基于业务复杂度、迁移成本豁免
- 豁免理由需在最终报告中记录

### 信息项（MAY）
- 不计入合规差距
- 可作为下一阶段优化方向

---

## 常见误判（参考公司双 baseline 工程实证）

> 以下写法**不是违规**，请勿当差距记录：

- ❌ `viewmodels`（复数）/ `services` / `dialog` / `vm` / `api` 等目录命名 — **MAY**，按职责拆分即可
- ❌ business_common 的 color.json 仅 2-3 个 token — **MAY**，跨平台 19 token 是建议非强制
- ❌ products/phone 用 `app_theme / text_color / btn_*_Color` 等业务命名 — **MAY**
- ❌ 简单/辅助/计数型 VM 未继承 BaseViewModel（私仓）— **MAY**，仅 *PageVM 要求
- ⚠️ widget/dialog/builder/特殊渲染/引导组件保留 v1 装饰器 — **MUST**：全局统一 v2，**无场景豁免**。AI/Scan baseline 中的 v1 残留视为遗留待整改
- ❌ 单点 axios 调用（特殊场景如文件下载）— **MAY**
- ❌ DAO 层 `@ohos.data.relationalStore` 直用 — **MAY**，封装实现合理
- ❌ 根 `oh-package.json5` 缺 `overrides` — **MAY**
- ❌ WebSocket 调用 — **MAY**，不在 HTTP 网络规则范围
- ❌ `import { GenericAbortSignal } from '@ohos/axios'` 类型导入 — **MAY**，类型来源容许
- ❌ `lib_*` 具体版本号差异 — **按工程当时稳定版本**，不硬编码
- ❌ `extends BaseBean / HSData` 类型 DTO — 项目历史决策；新代码优先 interface（R6.3b SHOULD）

---
