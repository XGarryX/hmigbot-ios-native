# data — 数据层规则（V2）

## JSON 字段改名（Gson `@SerializedName` 在 ArkTS 无等价物——V21 硬规则）
- `JSON.parse(text) as T` 是纯类型断言，不改字段名：`@SerializedName("avatar") headUrl` 类改名字段照抄属性名后运行期静默 `undefined`。
- 做法：接口层一次显式映射（`obj.headUrl = raw['avatar']`）或让 ArkTS 属性名 = 服务端字段名；禁靠 `if (resp.X !== undefined)` 守卫掩盖。
- 改名表 `spec/ref/serialized-name-map.json`（bean → [{json, prop}]）：本域 bean 有条目的，实现逐条落映射，审计逐条核对。

## 存储决策树
- 远程数据 → HttpUtil + Service 层（`import { http } from '@kit.NetworkKit'`，禁 @ohos.net.http）
- 键值偏好：仅持久化不驱动 UI → Preferences（`@kit.ArkData`，put 后必须 await flush）；持久化+UI 响应 → PersistenceV2.globalConnect
- 结构化/需 SQL → RdbStore(relationalStore)：单例初始化 + SecurityLevel；手写 CREATE TABLE；DAO 类 + querySql()；ResultSet 必须 close()
- 跨页全局运行时态（不持久） → `AppStorageV2.connect(Cls, key, () => new Cls())`
- 组件间事件通信 → EventHub

## EventHub 骨架
```typescript
import { common } from '@kit.AbilityKit'
const ctx = this.getUIContext().getHostContext() as common.UIAbilityContext
ctx.eventHub.emit('cartUpdated', { count: 5 })
// aboutToAppear: ctx.eventHub.on('cartUpdated', (d: Record<string, number>) => { this.cartCount = d.count })
// aboutToDisappear: ctx.eventHub.off('cartUpdated')   // 必须取消订阅防泄漏
```
事件名常量集中定义。祖先→后代用 @Provider/@Consumer；无层级全局态用 AppStorageV2；EventHub 只用于"主动 emit + 被动 on"广播（如登录态变更）。

## 错误速记
| 症状/错误 | 修法 |
|---|---|
| HTTP 请求没 destroy | try-finally 中 httpRequest.destroy() |
| BasicDataSource 整体 reload | notifyDataAdd/Change/Delete 增量通知 |
| Preferences 没 flush | put 后 await flush() |
| EventHub 泄漏 | aboutToDisappear 里 off() |
| Model 属性漏 @Trace | 需观察属性加 @Trace |
| 混入 V1 装饰器 | 全 V2 |
| AppStorageV2 key 不一致 | key 常量集中定义 |
| 自定义错误类裸 throw | 必须 extends Error 且构造器调 super(message)，否则 arkts-limited-throw |
| ResultSet.getColumnType 当同步用 | API18+ 为 async，须 await；已知列类型直接 getBlob(getColumnIndex('col')) |
| 组件内 getContext(this) 旧写法 | this.getUIContext().getHostContext() as common.UIAbilityContext |
| catch 形参标 unknown/any | `catch (error)` 省略标注（arkts-no-types-in-catch）；下传的形参/变量用 Object，再 instanceof/as 收窄 |
| 裸对象字面量 / `{} as T` | 字面量必须对应已声明 class/interface 且字段补齐（arkts-no-untyped-obj-literals）；空/缺省用 `T \| null` 返回 null 或 new 真实实例 |
| multipart 直传选择器路径 | 先 fileIo.copyFile 落沙箱（cacheDir/filesDir），filePath 用沙箱路径、文本项用 data，否则后端收空（接口仍 200） |
| 直接 JSON.stringify @ObservedV2 实例 | @Trace 字段 key 全变 __ob_ 前缀；序列化出口走 toJson() 或无装饰器纯 DTO |

<!-- source: arkts-data-layer/SKILL.md:L59-86,L97-136,L153-175 -->
