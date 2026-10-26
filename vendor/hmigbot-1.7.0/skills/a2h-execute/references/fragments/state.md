# state — V2 状态管理规则

## 装饰器选择决策树
- 仅当前组件内 → `@Local`（值类型直接观察；类实例靠 @ObservedV2+@Trace 触发）
- 父→子只读 → `@Param @Once`
- 父→子可改本地副本（不回传） → `@Param`（V2 强制默认值）
- 父↔子双向（V1 @Link 替代） → 子 `@Param value` + `@Event $value`（事件名 = $+属性名），父 `Child({ value: this.value!! })`；或手工 `@Event onValueChange`（此时父不能用 !!）
- 跨层级祖先→后代 → `@Provider()`/`@Consumer()`：必须带括号，Consumer 必须给默认值
- 引用类实例 → `@Param` 直接持有 @ObservedV2 实例（V2 取消 @ObjectLink），类属性加 @Trace
- 全局共享 → `AppStorageV2.connect(Cls, key, () => new Cls())!` 配 @ObservedV2 类
- 页面子树共享（不进全局） → @Provider/@Consumer，或页面根 @Local 持实例 @Param 下传；禁 LocalStorageV2（不存在，import 即报 has no exported member）
- 持久化 → `PersistenceV2.globalConnect({type: Cls, key, defaultCreator})!`
- V1→V2：@State→@Local；@Prop→@Param(+@Once)；@Watch→`@Monitor('prop') m(m: IMonitor)`；@StorageLink→AppStorageV2.connect；新增 @Computed（派生缓存）、@Trace（属性级观察）

## AppStorageV2 初始化时机
首次 connect() 自动用 defaultCreator 创建，同 key 后续 connect 共享同一实例；禁 V1 式在 EntryAbility.onCreate 提前 setOrCreate。需预热持久数据时可在 onCreate 中 connect 并写字段。

## 持久化决策树
- 仅运行时 → AppStorageV2.connect（退出即丢）；持久化、不驱动 UI → Preferences；持久化 + UI 实时刷新 → PersistenceV2.globalConnect 一站式，禁 V1 双层模式；结构化数据 → RdbStore
- 场景对照：临时 UI 态→@Local；登录用户→AppStorageV2；主题/偏好/token→PersistenceV2；收藏/历史→RdbStore

## 五大陷阱
1. @ObservedV2 类属性漏 @Trace → UI 不刷新；需观察属性必须加 @Trace。
2. AppStorageV2 key 拼写不一致 → 两个独立实例；key 必须常量集中定义。
3. @Builder 是函数，禁在其内声明状态（写 @Local 即编译错）；状态放 @ComponentV2 struct，@Builder 只收参数。
4. @ComponentV2 内禁 V1 装饰器（@State/@Prop/@Link 编译错）；同一文件不混 V1/V2。
5. @Monitor 回调禁改被监听属性本身（无限循环），只改其他变量。

## 观察能力速记
简单类型=重新赋值；@ObservedV2 类=@Trace 属性赋值（未加 @Trace 不观察）；数组=整体赋值或 push/splice（下标改对象属性需对象为 @ObservedV2 且属性带 @Trace）；Map/Set=set/delete/clear。

## Web 与首帧绑定（E1-5）
`Web({src})` 的 src 只在创建时生效，不能靠状态变量动态更改（`@Local url` 照样白屏）：URL 后到时 `controller.loadUrl(url)` 重载，或 `if (this.url.length > 0) { Web({src: this.url, controller}) }` 条件创建。其余非首帧赋值且绑定 UI 的字段（`Image(this.x)`/Text 内容）必须 @Local。

<!-- source: arkts-state-manager/SKILL.md:L52-97,L104-111,L115-132,L133-265 -->
