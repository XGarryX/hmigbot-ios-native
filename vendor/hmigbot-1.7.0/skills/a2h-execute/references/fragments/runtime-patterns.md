# runtime-patterns — 运行期 API 语义陷阱（编译不拦、真机才炸）

每条都是「编译绿、跑起来坏」：写码对照，审计按条 grep。

## 1. `$r()` 返回 Resource 对象，不是字符串
`$r('app.string.app_name')` 进网络载荷 / 日志 / 字符串拼接会变成 `"$string:app_name"` 或序列化残骸。UI 属性可直接吃 Resource；任何离开 UI 的路径必须先解：`getContext(this).resourceManager.getStringSync($r('app.string.app_name').id)`。

## 2. 系统回调的 err 成功时是 undefined，不是 null
`callback(err, data)` 型 API 成功时 err 常为 `undefined`，`if (err !== null)` 会把成功当失败（jscrash）。一律 `if (err) { ... }`，禁 `!== null` / `=== null` 判空。

## 3. 拦截器跳登录前先查栈顶
token 失效码（-1001 等）触发跳登录时，栈顶已是登录页再 push 会刷掉正在输入的表单。守卫：`if (stack.getAllPathName().pop() !== 'Login') { stack.pushPathByName('Login', …) }`；决策卡的 boundary 通常也要求「登录页内不自跳」。

## 4. 弹窗形态以 ui-forms.json 为准：DIALOG 模式弹窗页，禁 STANDARD 路由页当弹窗、禁宿主页内联渲染
安卓窗口级组件（Dialog / DialogFragment / BottomSheet）一律做 `NavDestination` + `.mode(NavDestinationMode.DIALOG)` 透明弹窗页：调用方 `pushPathByName` 打开、页内 `pop()` 关闭（E259，脚本按安卓判定，写在任务书「界面形态」段，落账 ui_form_lint 核对）。STANDARD 路由页当弹窗 = 整页盖掉底下页面；把弹窗组件内联渲染进宿主页 = 自发明命中控制与返回语义，隐藏时全屏壳照样吞点击（ds 首页全点不动）。无自定义布局的系统 AlertDialog → `getPromptAction().showDialog`；自定义布局 toast → ComponentContent + `openCustomDialog`（见任务书标准写法）。
层级半句（易漏）：这些弹窗默认全局级、盖住所有路由页；源端 Dialog/DialogFragment 是页面级语义（弹窗开着跳新页、新页盖住弹窗）时，`openCustomDialog` options 配 `levelMode: LevelMode.EMBEDDED`（`import { LevelMode } from '@kit.ArkUI'`，API 15+、仅非子窗模式）；宿主在 Navigation navBar/首页内容时 EMBEDDED 会静默退化回盖住后续 push 页，此时改用 `NavDestinationMode.DIALOG` 透明弹窗页。负向守卫：用完即关、不跨路由的确认框/Toast/Sheet 不配。

## 5. 遮罩吞点击的正确写法是空 onClick，不是 hitTestBehavior(Block)
蒙层挡底下点击：`.onClick(() => {})` 吃掉事件，不是 `.hitTestBehavior(HitTestMode.Block)`；Block 连自己子孙一起排除，蒙层里的按钮全部点不动（首屏死区）。语义表见 arkui-enums。

<!-- provenance: runtime（aippt_new_v3 真机期实证，2026-08-21）
     source: aippt_new_v3/RETROSPECTIVE-aippt_new_v3.md §2.2 F-001/F-002/F-006/F-008 + NetworkMonitor;
     arkts-component-builder/references/v2-dialogs-and-sheets.md §2c（levelMode）-->

## 模块加载期禁止触碰运行期才初始化的单例（冷启 ReferenceError）
- `private static readonly x = new XxxApiService()`、`export const x = new Xxx()` 这类静态字段/模块级 const 在**模块加载期**求值，此时 RetrofitFactory / UserData / 各 SDK 尚未在 EntryAbility 初始化 → 冷启即 `XXX is not initialized` 崩（token2 实证 4 处）。
- 规则：依赖运行期初始化服务的成员一律惰性——静态 getter 首次访问再 `new`，或在 aboutToAppear/onCreate 里赋值；默认参数里也不得写 `RetrofitFactory.instance`。
- 机械检查：`static_runtime_lint.py` 的 `module-init-runtime-dependency`（落账时 land_results 按白名单自动跑并 `--fix` 把类内 `static x = new Y()` 改成惰性 getter；剩余 P0 打回 RETRY，round0 兜底）。
- 同理 **import 环**：A↔B 互相 import 时谁先求值由入口决定，后求值那一方的绑定被前一方在加载期读到就是 `ReferenceError: X is not initialized`（类型全对，编译门看不见）。环内模块的顶层语句、顶层 const、类 static 字段初始化式、`class X extends Y` 的 Y **禁止**读对方导出的值；只在函数体/方法体里用是安全的。修法：把双方共用的类型/常量抽到第三个模块断环，或改惰性 getter。
- 机械检查：同一脚本的 `module-init-cycle-tdz`（落账 `--fix` 把能定类型的单行 static 字段改惰性 getter；顶层 const 与被别处赋值的字段只报不改，打回 RETRY）。
