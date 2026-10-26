# §4 架构映射表（references 详细版）

主 SKILL.md §4 的详细映射查询手册。**噪声过滤器**——看到 Android 侧有、HMOS 侧找不到同名类时，先查此表，**不是直接报缺失**。所有模式共享。

> ⛔ **生成范本统一 v2 — HARD CONSTRAINT**
> 本表"HMOS 等价形式"列即下游生成器的目标范本，**只允许出现 v2 装饰器 + 客户私仓 API**。
> 禁出现：`@Entry/@Component/@State/@Prop/@Link/@Provide/@Consume/@Observed/@ObjectLink/@StorageLink/@StorageProp`、`LazyForEach`、`router.pushUrl/pushUrl/back/clear`、`axios/http.createHttp`、`@ohos.data.preferences/@kit.ArkData/@ohos.data.relationalStore`。
> 识别既有 v1 老代码（grep 扫描场景）允许命中 v1 符号，但**写出来的范本/示例/对照表必须 v2**。

## 4.1 架构工具层（Android 独有，HMOS **不需要**等价类）

| Android 概念 | HMOS 等价形式（v2 范本） | 不要做什么 |
|---|---|---|
| `Activity` / `Fragment` | `@ComponentV2 struct` + page 自身 `build() { NavDestination(){...}.onShown/.onHidden/.onBackPressed }`；Tab 子页嵌入父页 | 不要为每个 Fragment 新建独立 Page；不要写 `@Entry struct` |
| `ViewPager2` + `FragmentStateAdapter` | `Tabs` + `TabContent` + `@Builder` | 不要找 `ViewPagerAdapter` |
| `RecyclerView` + `Adapter` + `ViewHolder` | `List` + `Repeat<T>(arr).each((obj: RepeatItem<T>) => {...}).key(...).virtualScroll()` + 子 `@ComponentV2` | 不要找 `Adapter` 类；不要用 `LazyForEach` |
| `DialogFragment` | `@CustomDialog` + `CustomDialogController` | 不要判"Dialog 类是否存在" |
| `ViewModel` + `LiveData.observe` | `*PageVM extends BaseViewModel`（lib_common）+ `@Trace` 字段 + `emitter` / 单例 manager | 不要 grep `*ViewModel`；不要用 `@State` |
| `DataBinding binding.xxId` | 声明式组件树（`@Local` / `@Param` 父子传递） | 不要用 layout id 命中率判业务对齐；不要用 `@Link` |
| `RxJava` / `Flow` | `async/await` + `Promise` + `emitter` | 不要找 Rx 类 |
| `EventBus` | `EventHubUtils`（lib_common）/ `emitter`（`@kit.BasicServicesKit`） | 不要找 `EventBus` 类 |
| `Retrofit` interface | `RequestUtil.getInstance().requestPromise<T>(RequestUrlMap.X, { signal, showLoad })`（lib_network 公司 API）/ `ExternalReqUtil`（第三方） | endpoint 字符串差集可用；接口类差集不用；不要用 `axios` / `http.createHttp` |
| `SharedPreferences` | `PreferenceUtil.getInstance(this.context).put/get`（lib_common；UIAbility scope 必须显式传 ctx） | 不要找 `SharedPreferences` 类；不要 import `@ohos.data.preferences` / `@kit.ArkData` |
| `Room` / SQLite | `@ohos/dataorm` Entity + DAO（`id: number \| null = null`；`dao.insertOrReplace(entity)`） | 不要 import `@ohos.data.relationalStore` |
| `Intent` + `startActivity` | `RouterUtils.pushPathByName(RouterMap.X, params)`（lib_common）+ page 在 module 的 `route_map.json` 注册 + `@Builder export function XxxPageBuilder` | 不要找 `Intent` 类；不要用 `router.pushUrl/replaceUrl/back/clear`；不要用裸字符串路由名 |
| `BroadcastReceiver` | `commonEventManager` | 不要找 `Receiver` 类 |
| `Glide` / `Picasso` | `Image($r('app.media.x'))` 内置；自定义封装优先看 lib_common 是否已导出 | 不要找图片加载库 |
| Android `Toolbar` / `ActionBar` | `NavHeaderBar({ title, rightPartBuilder?, onBack? })`（lib_widget；默认 onBack = RouterUtils.pop） | 不要手写 `Image($r('app.media.ic_back')) + Row` 标题栏 |
| 状态栏 / 安全区适配 | `this.vm.windowModel.windowTopPadding` / `.windowBottomPadding`（BaseViewModel 已注入） | 不要写死 `padding({ top: 36 })`；不要在 page 内 `AppStorageV2.connect(WindowModel,...)` |
| 多端列数 / 折叠屏 | `.lanes(GridRowColSetting.getWindowColumn(this.vm.breakPointModel.currentBreakpoint))`（注 P 大写） | 不要写 `.lanes(2)`；不要用 `BreakpointModel.gridColumns`（字段不存在） |

## 4.2 UI 控件层映射（语义同名词典）

| Android | HMOS | 备注 |
|---|---|---|
| `TextView` | `Text` | |
| `Button` / `ImageView` + click | `Button` / `Image().onClick(...)` | |
| `EditText` | `TextInput` / `TextArea` | |
| `CheckBox` / `Switch` | `Checkbox` / `Toggle` | |
| `RadioButton` + `RadioGroup` | `Radio({ group: 'x' })` | |
| `ProgressBar` | `Progress` / `LoadingProgress` | |
| `SeekBar` | `Slider` | |
| `Toast` | `promptAction.showToast` | |
| `AlertDialog` / `BottomSheetDialog` | `AlertDialog.show` / `@CustomDialog` | |
| `SwipeRefreshLayout` | `Refresh` | |
| `ConstraintLayout` | `RelativeContainer` / `Stack`+布局 | |
| FAB | `Button().position(...)` 浮层 | |

## 4.3 权限映射（Android → OHOS，非 1:1）

**HARD-GATE**：加权限前**必须 grep HMOS 代码确认 API 被使用**，否则 ACL 权限会卡签名。

| Android | OHOS | 何时加 |
|---|---|---|
| `INTERNET` | `ohos.permission.INTERNET` | 用了 `http`/`request` 就加 |
| `ACCESS_NETWORK_STATE` | `ohos.permission.GET_NETWORK_INFO` | 用了 `connection.getNetworkInfo` 才加 |
| `READ_EXTERNAL_STORAGE` | **多数情况不用加** | 走 `PhotoViewPicker`/`DocumentViewPicker` 免权限 |
| `MANAGE_EXTERNAL_STORAGE` | `ohos.permission.FILE_ACCESS_MANAGER`（ACL） | 需签名证书 ACL |
| `SET_WALLPAPER` | `ohos.permission.SET_WALLPAPER`（ACL） | HMOS 有壁纸 API 才加 |
| `VIBRATE` | `ohos.permission.VIBRATE` | 用了 `vibrator` 才加 |
| `INSTALL_SHORTCUT` | 无公共映射 | 跳过 |
