# 实战踩坑百科（22 条）

> 来自 AntennaPod Android→ArkTS 迁移实战（17 Session, 96 文件）。按 7 大类组织。
>
> **装饰器版本**：本项目锁 ArkTS V2，下文部分踩坑（如 #11 AppStorage 时序）的现象在 V1 装饰器（`@StorageLink`）下出现，**V2 等价问题在 `AppStorageV2.connect` 模式下不再存在**（V2 自动用 `defaultCreator` 初始化）。仍保留 V1 描述以便阅读老代码。

---

## AVPlayer（3 条）

### #1: 本地文件必须用 fd:// 协议
**问题**：`file://` + 绝对路径设置 `avPlayer.url`，AVPlayer 直接进入 error 状态。
**根因**：HarmonyOS AVPlayer 不支持 `file://` 协议，本地文件必须通过文件描述符播放。
**方案**：`fileIo.openSync(path, READ_ONLY)` → `'fd://' + file.fd.toString()`
**预防**：所有本地音视频播放都使用 fd:// 协议，永远不要尝试 file://。

### #2: 状态机必须严格按顺序
**问题**：在 Initialized 状态直接调用 `play()` 无效，或在未 Prepared 时调用 `seek()` 静默失败。
**根因**：AVPlayer 状态机是严格的：`Idle → Initialized → Prepared → Playing/Paused`，不能跳过。
**方案**：在 `on('stateChange')` 回调中按状态执行操作：initialized→prepare, prepared→play。
**预防**：所有 AVPlayer 操作在对应状态回调中执行，不能"凭感觉"调用。

### #3: PlaybackSpeed 是离散枚举
**问题**：`avPlayer.setSpeed(1.3)` 不生效或报错。
**根因**：`media.PlaybackSpeed` 只有 6 个有效值：0.75x, 1.0x, 1.25x, 1.5x, 1.75x, 2.0x。
**方案**：`snapToValidSpeed()` 映射到最近的有效值 + `mapToPlaybackSpeed()` 转枚举。
**预防**：UI 上的倍速选择器只展示这 6 个有效值。

---

## 下载（4 条）

### #4: http.request() 约 5MB 限制
**问题**：`http.createHttp().request()` + `ARRAY_BUFFER` 下载播客音频，报错 `2300023`。
**根因**：`http.request()` 的 ARRAY_BUFFER 模式将整个响应加载到内存，有约 5MB 限制。
**方案**：使用 `request.agent` API（`import { request } from '@kit.BasicServicesKit'`）。
**预防**：任何超过 1MB 的文件下载都使用 `request.agent`。

### #5: requestInStream 不可靠
**问题**：`httpRequest.requestInStream()` 返回的 Promise 在收到响应头后即 resolve，`dataEnd` 事件不触发。
**根因**：`requestInStream` 的事件机制在当前版本不稳定。
**方案**：完全弃用 `requestInStream`，直接使用 `request.agent` API。
**预防**：不要使用 `requestInStream` 下载文件。

### #6: request.agent 下载到 cacheDir
**问题**：`moveFileSync` 到目标目录时报 `13900002`（ENOENT）。
**根因**：`fileIo.mkdir()` 默认不递归创建，目标目录不存在。
**方案**：`fileIo.mkdirSync(downloadDir, true)` 递归创建后再移动。
**预防**：移动文件前先确保目标目录存在。

### #7: URL 中 &amp; 需解码
**问题**：RSS XML 中的下载 URL 包含 `&amp;` 实体编码，HTTP 请求返回 400。
**根因**：XML 解析器输出的 URL 保留了 HTML 实体编码。
**方案**：`cleanUrl = downloadUrl.replace(/&amp;/g, '&')`。
**预防**：所有从 XML/RSS 解析出的 URL 在使用前做实体解码。

---

## UI（5 条）

### #8: Tab 栏被 NavDestination 覆盖
**问题**：`Navigation` 包裹 `Tabs` 时，NavDestination 子页面覆盖整个 Navigation 区域。
**根因**：Tabs 在 Navigation 内部，NavDestination 会覆盖包括 Tabs 在内的整个区域。
**方案**：将 Tab 栏放在 Navigation 外部，使用自定义 Row 实现。
**预防**：Tab 栏用自定义 Row，放在 Navigation 外部。

### #9: Emoji vs SymbolGlyph
**问题**：Unicode emoji（📋📥📡）与普通 Unicode 字符渲染大小差异巨大。
**根因**：emoji 按平台图片渲染，大小不受 `fontSize` 精确控制。
**方案**：统一使用 `SymbolGlyph($r('sys.symbol.xxx'))` + `.fontSize()` + `.fontColor([])`。
**预防**：所有图标统一使用 SymbolGlyph，不要混用 emoji。

### #10: sys.symbol 名称不存在
**问题**：部分 SF Symbol 名称在 HarmonyOS 中不存在，编译报 `Unknown resource name`。
**根因**：HarmonyOS 的 symbol 集与 Apple SF Symbols 不完全一致。
**方案**：从已验证清单（22 个）中选取，或编译验证。
**预防**：只从已验证列表中选取 symbol 名称，新名称先编译验证。

### #11: AppStorage 时序（V1 问题；V2 已自动处理）
**问题**（V1）：`@StorageLink('someKey')` 在组件创建时找不到对应的 AppStorage key，UI 不刷新。
**根因**：V1 `@StorageLink` 在组件实例化时绑定，如果此时 key 尚未通过 `setOrCreate` 注册，绑定失败。
**方案**（V1）：在 `GlobalState.initAppStorage()` 中统一注册所有 key，确保在任何组件创建前执行。
**预防**（V1）：新增 `@StorageLink` key 时必须同时在 `GlobalState.initAppStorage()` 中添加 `setOrCreate`。
**V2 等价**（推荐）：`AppStorageV2.connect(Cls, 'someKey', () => new Cls())!` 第一次调用自动用 `defaultCreator` 初始化，**无需提前 `setOrCreate`**，时序问题不存在。详见 [`v2-migration-patterns.md`](./v2-migration-patterns.md) §3.4。

### #12: ForEach key 生成器
**问题**：`ForEach` 列表更新数据后，UI 不刷新或刷新异常。
**根因**：key 只用 `id`，属性变化时 ArkUI 认为该条目未变化，跳过重渲染。
**方案**：`(item) => item.id.toString() + '_' + item.playState.toString()`。
**预防**：ForEach 的 key 必须包含所有会影响 UI 显示的字段。

---

## ArkTS 语言（3 条）

### #13: 对象字面量不能做类型声明
**问题**：编译报错 `arkts-no-obj-literals-as-types`。
**根因**：ArkTS 严格模式禁止对象字面量作为类型声明。
**方案**：定义独立的 class 替代（如 `class DownloadReceiveProgress { receiveSize: number = 0; }`）。
**预防**：所有回调参数类型都使用 class 定义。

### #14: 类型转换只能用 `as T`（禁 `<Type>x` 与 `as const`）
**问题**：用 `<Type>value` 尖括号语法转换编译报错；或误把 `as` 当成被禁而绕路。
**根因**：ArkTS 中 `as` 是类型转换的**唯一合法语法**（官方："as 关键字是类型转换的唯一语法…不支持 `<type>` 语法"，rule `arkts-as-casts`）；只有 `as const` 被禁（rule `arkts-no-as-const`）。`as T` 本身合法且推荐。
**方案**：写 `value as Type`；运行时不确定类型时再配合 `instanceof` 收窄：`if (data instanceof FeedItem) { useItem(data) }`。
**预防**：转换用 `x as Type`，不用 `<Type>x`、不用 `as const`。

### #15: any 类型被完全禁止
**问题**：编译报错 `arkts-no-any-unknown`。
**根因**：ArkTS 严格模式禁止所有 `any` 和 `unknown` 类型。
**方案**：使用具体类型或 `Object`：`let data: string = response.result.toString()`。
**预防**：所有变量必须有明确类型标注。

---

## 导航（2 条）

### #16: NavDestination 参数在 onReady 中获取
**问题**：在 `aboutToAppear()` 中获取参数得到 `undefined`。
**根因**：`aboutToAppear` 在组件实例化时调用，此时 NavDestination 上下文尚未就绪。
**方案**：`.onReady((ctx: NavDestinationContext) => { const param = ctx.pathInfo.param; })`。
**预防**：所有 NavDestination 参数获取放在 `onReady` 回调中。

### #17: ActionMenuSuccessResponse 命名
**问题**：使用 `promptAction.ShowActionMenuSuccessResponse` 编译报 "does not exist"。
**根因**：正确名称是 `ActionMenuSuccessResponse`，没有 `Show` 前缀。
**方案**：`promptAction.showActionMenu({}).then((result: promptAction.ActionMenuSuccessResponse) => {})`。
**预防**：API 名称不确定时查阅官方文档。

---

## 数据库（3 条）

### #18: INSERT OR REPLACE 改变 id
**问题**：使用 `INSERT OR REPLACE` 更新已有记录时，自增 id 被重新分配。
**根因**：`INSERT OR REPLACE` 实际执行 DELETE + INSERT，触发新的 AUTOINCREMENT。
**方案**：使用 `INSERT INTO ... ON CONFLICT(id) DO UPDATE SET ...`。
**预防**：需保持 id 稳定时，使用 `ON CONFLICT DO UPDATE`。

### #19: ResultSet 必须 close()
**问题**：查询后未关闭 ResultSet，后续查询报数据库锁错误。
**根因**：`relationalStore` 的 ResultSet 持有数据库连接，不关闭会导致连接泄漏。
**方案**：`try { /* 处理 */ } finally { resultSet.close(); }`。
**预防**：所有 DAO 方法的 ResultSet 使用 `try/finally` 模式。

### #20: Preferences 只支持基础类型
**问题**：`preferences.putSync()` 不支持存储对象或数组。
**根因**：只支持 string, number, boolean, string[] 类型。
**方案**：复杂数据用 `JSON.stringify` / `JSON.parse` 序列化。
**预防**：Preferences 存储复杂数据统一用 JSON 序列化。

---

## 网络（2 条）

### #21: http 实例必须 destroy()
**问题**：频繁创建 `http.createHttp()` 而不 destroy，出现内存泄漏。
**根因**：每个 `http.createHttp()` 实例持有底层 CURL 句柄。
**方案**：`try { await httpRequest.request(); } finally { httpRequest.destroy(); }`。
**预防**：封装 HttpClient 工具类，确保每次请求后 destroy。

### #22: 响应头提取需 JSON 桥接
**问题**：`response.header` 类型是 `Object`，不能用 `[]` 索引访问（会引入 `any`）。
**根因**：ArkTS 严格模式下 `Object` 不能通过 `[]` 访问属性。
**方案**：`JSON.stringify(response.header)` → `JSON.parse(headerStr)` 桥接。
**预防**：系统 API 返回 `Object` 类型时，用 JSON.stringify → JSON.parse 桥接。
