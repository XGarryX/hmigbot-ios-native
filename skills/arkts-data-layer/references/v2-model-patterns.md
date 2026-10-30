# ArkTS V2 数据模型模式参考

> 本文档基于 **ArkTS V2（API 12+）** 装饰器体系。本项目锁 V2，本文档为主参考。V1 历史写法见 [`model-patterns.md`](./model-patterns.md)（已加 legacy 标识）。
>
> 完整的 V2 数据模型模式，涵盖 `@ObservedV2 + @Trace` 模型、单例（配合 `AppStorageV2.connect`）、JSON 转换、嵌套模型、枚举、`@Computed` 计算属性和表单验证。

---

## 1. 基础 @ObservedV2 + @Trace 模型

V2 用 `@ObservedV2` 装饰类，每个需要 UI 观察的属性单独加 `@Trace`。属性级精确观察，未加 `@Trace` 的属性变化不会触发 UI 刷新。

```typescript
// ==========================================
// 基础 @ObservedV2 模型 —— 包含常见字段类型
// ==========================================

@ObservedV2
export class UserModel {
  // 基本类型字段（需要观察的全部加 @Trace）
  @Trace id: number = 0
  @Trace name: string = ''
  @Trace email: string = ''
  @Trace age: number = 0
  @Trace isActive: boolean = true
  @Trace balance: number = 0

  // 可选字段（需要观察的也加 @Trace）
  @Trace avatar?: string
  @Trace bio?: string

  // 数组字段
  @Trace tags: string[] = []

  // 日期用时间戳表示
  @Trace createdAt: number = 0
  @Trace updatedAt: number = 0

  constructor(
    id: number = 0,
    name: string = '',
    email: string = '',
    age: number = 0,
    isActive: boolean = true,
    balance: number = 0,
    avatar?: string,
    bio?: string,
    tags: string[] = [],
    createdAt: number = Date.now(),
    updatedAt: number = Date.now()
  ) {
    this.id = id
    this.name = name
    this.email = email
    this.age = age
    this.isActive = isActive
    this.balance = balance
    this.avatar = avatar
    this.bio = bio
    this.tags = tags
    this.createdAt = createdAt
    this.updatedAt = updatedAt
  }

  // 从 JSON 对象构造（网络请求返回后使用）
  static fromJson(json: Record<string, Object>): UserModel {
    return new UserModel(
      json['id'] as number,
      json['name'] as string,
      json['email'] as string,
      (json['age'] as number) ?? 0,
      (json['isActive'] as boolean) ?? true,
      (json['balance'] as number) ?? 0,
      json['avatar'] as string | undefined,
      json['bio'] as string | undefined,
      (json['tags'] as string[]) ?? [],
      (json['createdAt'] as number) ?? Date.now(),
      (json['updatedAt'] as number) ?? Date.now()
    )
  }

  // 转为 JSON 对象（提交到服务端时使用）
  toJson(): Record<string, Object> {
    let result: Record<string, Object> = {
      'id': this.id as Object,
      'name': this.name as Object,
      'email': this.email as Object,
      'age': this.age as Object,
      'isActive': this.isActive as Object,
      'balance': this.balance as Object,
      'tags': this.tags as Object,
      'createdAt': this.createdAt as Object,
      'updatedAt': this.updatedAt as Object
    }
    if (this.avatar !== undefined) {
      result['avatar'] = this.avatar as Object
    }
    if (this.bio !== undefined) {
      result['bio'] = this.bio as Object
    }
    return result
  }
}
```

**在组件中使用（V2）：**

```typescript
// 父组件用 @Local 持有，子组件直接用 @Param 接收（不再用 @ObjectLink）
@Entry
@ComponentV2
struct UserPage {
  @Local user: UserModel = new UserModel(1, '张三', 'zhangsan@example.com', 28)

  build() {
    Column() {
      // 直接传 @ObservedV2 实例
      UserCard({ user: this.user })

      Button('修改姓名')
        .onClick(() => {
          // 直接修改 @Trace 属性即可触发 UI 更新
          this.user.name = '李四'
        })
    }
  }
}

@ComponentV2
struct UserCard {
  // V2 直接用 @Param 接收 @ObservedV2 实例
  @Param user: UserModel = new UserModel()

  build() {
    Column() {
      Text(this.user.name)
      Text(this.user.email)
      Text(`年龄: ${this.user.age}`)
      Text(this.user.isActive ? '已激活' : '未激活')
    }
  }
}
```

---

## 2. 单例模型模式（V2 推荐：AppStorageV2.connect）

V1 时代常用 `private static instance + getInstance()` 单例模式，配合 `@State` / `@StorageLink` 在组件中持有。V2 推荐直接用 `AppStorageV2.connect(...)` —— 框架负责单实例 + 跨页同步，不需要手写单例样板。

```typescript
import { AppStorageV2 } from '@kit.ArkUI'   // 真实导出，必须 import（漏了报 Cannot find name 'AppStorageV2'）

// ==========================================
// V2 全局共享配置 —— 用 AppStorageV2 替代手写单例
// ==========================================

@ObservedV2
export class AppConfig {
  @Trace apiBaseUrl: string = 'https://api.example.com/v1'
  @Trace appVersion: string = '1.0.0'
  @Trace debugMode: boolean = false
  @Trace pageSize: number = 20
  @Trace theme: string = 'light'
  @Trace language: string = 'zh-CN'

  // 从服务端配置初始化
  applyJson(json: Record<string, Object>): void {
    if (json['apiBaseUrl'] !== undefined) {
      this.apiBaseUrl = json['apiBaseUrl'] as string
    }
    if (json['debugMode'] !== undefined) {
      this.debugMode = json['debugMode'] as boolean
    }
    if (json['pageSize'] !== undefined) {
      this.pageSize = json['pageSize'] as number
    }
    if (json['theme'] !== undefined) {
      this.theme = json['theme'] as string
    }
    if (json['language'] !== undefined) {
      this.language = json['language'] as string
    }
  }

  toJson(): Record<string, Object> {
    return {
      'apiBaseUrl': this.apiBaseUrl as Object,
      'appVersion': this.appVersion as Object,
      'debugMode': this.debugMode as Object,
      'pageSize': this.pageSize as Object,
      'theme': this.theme as Object,
      'language': this.language as Object
    }
  }

  // 重置为默认值（用于退出登录等场景）
  reset(): void {
    this.apiBaseUrl = 'https://api.example.com/v1'
    this.debugMode = false
    this.pageSize = 20
    this.theme = 'light'
    this.language = 'zh-CN'
  }
}

// ---- 统一 key 常量 ----
export class StorageKeys {
  static readonly APP_CONFIG = 'app_config'
}
```

**使用示例（V2）：**

```typescript
// 在任意位置获取配置（普通 TS 上下文）
const config: AppConfig = AppStorageV2.connect(
  AppConfig,
  StorageKeys.APP_CONFIG,
  () => new AppConfig()
)!
console.info(`API地址: ${config.apiBaseUrl}`)
config.theme = 'dark'

// 在 @ComponentV2 中使用，自动响应变化
@Entry
@ComponentV2
struct SettingsPage {
  @Local config: AppConfig = AppStorageV2.connect(
    AppConfig,
    StorageKeys.APP_CONFIG,
    () => new AppConfig()
  )!

  build() {
    Column() {
      Text(`主题: ${this.config.theme}`)
      Text(`每页数量: ${this.config.pageSize}`)

      Button('切换深色模式')
        .onClick(() => {
          this.config.theme = this.config.theme === 'light' ? 'dark' : 'light'
          // 自动同步到所有 connect(APP_CONFIG) 的组件
        })
    }
  }
}
```

> **如需持久化（应用重启保留）**，把 `AppStorageV2.connect` 换成 `PersistenceV2.globalConnect({ type: AppConfig, key: StorageKeys.APP_CONFIG, defaultCreator: () => new AppConfig() })!`，无需任何其他改动。

---

## 3. fromJson / toJson 完整转换模式

处理复杂 JSON 结构的完整模式，包含类型安全和默认值处理。`JsonHelper` 工具类与 V1 完全一致（与装饰器无关）。

### 为什么必须走 toJson()/fromJson()：@ObservedV2 直接序列化的 `__ob_` 前缀陷阱

对 `@ObservedV2` 实例直接 `JSON.stringify`，`@Trace` 属性的 key 会带框架改名前缀 `__ob_`（V2 靠字段重命名 + getter/setter 代理实现观测，`JSON.stringify` 只读 own properties、不走 getter）：

```typescript
// ✘ WRONG：把 @ObservedV2 实例直接序列化当请求体 / 落盘
let body: string = JSON.stringify(product)
// '{"__ob_id":1,"__ob_title":"..."}' —— 后端不识别；编译零提示、接口可能仍 200，真机联调才暴露
```

**规矩**：凡序列化发给后端 / 落盘的对象，走本节 `toJson()` 显式映射（`JSON.stringify(product.toJson())`），或改用**无装饰器的纯 DTO 类**（请求专用类不需要响应式）。嵌套模型逐层 `toJson()`。反序列化同理：`JSON.parse` 直接得到的不是类实例、无观察能力，走本节 `fromJson()`。

**负向守卫**：这不是剥掉 `@ObservedV2` 的理由——UI 要观察的模型照常装饰，只在序列化出口转 `toJson()`；也别用 `replaceAll('__ob_', '')` 之类字符串 hack 当请求体修法。

```typescript
// ==========================================
// JSON 转换工具 —— 安全的类型转换辅助（V1/V2 通用）
// ==========================================

export class JsonHelper {
  static getString(json: Record<string, Object>, key: string, defaultVal: string = ''): string {
    let value = json[key]
    if (value === undefined || value === null) {
      return defaultVal
    }
    return value as string
  }

  static getNumber(json: Record<string, Object>, key: string, defaultVal: number = 0): number {
    let value = json[key]
    if (value === undefined || value === null) {
      return defaultVal
    }
    return value as number
  }

  static getBoolean(json: Record<string, Object>, key: string, defaultVal: boolean = false): boolean {
    let value = json[key]
    if (value === undefined || value === null) {
      return defaultVal
    }
    return value as boolean
  }

  static getArray<T>(json: Record<string, Object>, key: string): T[] {
    let value = json[key]
    if (value === undefined || value === null) {
      return []
    }
    return value as T[]
  }

  static getObject(json: Record<string, Object>, key: string): Record<string, Object> | null {
    let value = json[key]
    if (value === undefined || value === null) {
      return null
    }
    return value as Record<string, Object>
  }
}

// ==========================================
// V2 模型示例（@ObservedV2 + @Trace）
// ==========================================

@ObservedV2
export class ProductModel {
  @Trace id: number = 0
  @Trace title: string = ''
  @Trace description: string = ''
  @Trace price: number = 0
  @Trace originalPrice: number = 0
  @Trace stock: number = 0
  @Trace images: string[] = []
  @Trace categoryId: number = 0
  @Trace isOnSale: boolean = true

  constructor(
    id: number = 0,
    title: string = '',
    description: string = '',
    price: number = 0,
    originalPrice: number = 0,
    stock: number = 0,
    images: string[] = [],
    categoryId: number = 0,
    isOnSale: boolean = true
  ) {
    this.id = id
    this.title = title
    this.description = description
    this.price = price
    this.originalPrice = originalPrice
    this.stock = stock
    this.images = images
    this.categoryId = categoryId
    this.isOnSale = isOnSale
  }

  static fromJson(json: Record<string, Object>): ProductModel {
    return new ProductModel(
      JsonHelper.getNumber(json, 'id'),
      JsonHelper.getString(json, 'title'),
      JsonHelper.getString(json, 'description'),
      JsonHelper.getNumber(json, 'price'),
      JsonHelper.getNumber(json, 'originalPrice'),
      JsonHelper.getNumber(json, 'stock'),
      JsonHelper.getArray<string>(json, 'images'),
      JsonHelper.getNumber(json, 'categoryId'),
      JsonHelper.getBoolean(json, 'isOnSale', true)
    )
  }

  toJson(): Record<string, Object> {
    return {
      'id': this.id as Object,
      'title': this.title as Object,
      'description': this.description as Object,
      'price': this.price as Object,
      'originalPrice': this.originalPrice as Object,
      'stock': this.stock as Object,
      'images': this.images as Object,
      'categoryId': this.categoryId as Object,
      'isOnSale': this.isOnSale as Object
    }
  }

  static fromJsonArray(jsonArray: Record<string, Object>[]): ProductModel[] {
    let result: ProductModel[] = []
    for (let json of jsonArray) {
      result.push(ProductModel.fromJson(json))
    }
    return result
  }
}
```

---

## 4. 嵌套模型模式（V2）

V2 嵌套同样精确：内层 `@ObservedV2` 类的 `@Trace` 属性变化也能触发外层 UI 刷新。

```typescript
// ==========================================
// 嵌套 @ObservedV2 模型
// ==========================================

@ObservedV2
export class AddressModel {
  @Trace id: number = 0
  @Trace province: string = ''
  @Trace city: string = ''
  @Trace district: string = ''
  @Trace street: string = ''
  @Trace isDefault: boolean = false

  constructor(
    id: number = 0,
    province: string = '',
    city: string = '',
    district: string = '',
    street: string = '',
    isDefault: boolean = false
  ) {
    this.id = id
    this.province = province
    this.city = city
    this.district = district
    this.street = street
    this.isDefault = isDefault
  }

  static fromJson(json: Record<string, Object>): AddressModel {
    return new AddressModel(
      JsonHelper.getNumber(json, 'id'),
      JsonHelper.getString(json, 'province'),
      JsonHelper.getString(json, 'city'),
      JsonHelper.getString(json, 'district'),
      JsonHelper.getString(json, 'street'),
      JsonHelper.getBoolean(json, 'isDefault')
    )
  }

  // V2 中可用 @Computed 缓存派生属性（getter 方案也可，但 @Computed 自动缓存）
  @Computed
  get fullAddress(): string {
    return `${this.province}${this.city}${this.district}${this.street}`
  }
}

@ObservedV2
export class OrderItemModel {
  @Trace productId: number = 0
  @Trace productName: string = ''
  @Trace price: number = 0
  @Trace quantity: number = 1
  @Trace imageUrl: string = ''

  constructor(
    productId: number = 0,
    productName: string = '',
    price: number = 0,
    quantity: number = 1,
    imageUrl: string = ''
  ) {
    this.productId = productId
    this.productName = productName
    this.price = price
    this.quantity = quantity
    this.imageUrl = imageUrl
  }

  static fromJson(json: Record<string, Object>): OrderItemModel {
    return new OrderItemModel(
      JsonHelper.getNumber(json, 'productId'),
      JsonHelper.getString(json, 'productName'),
      JsonHelper.getNumber(json, 'price'),
      JsonHelper.getNumber(json, 'quantity', 1),
      JsonHelper.getString(json, 'imageUrl')
    )
  }

  @Computed
  get subtotal(): number {
    return this.price * this.quantity
  }
}

@ObservedV2
export class OrderModel {
  @Trace id: string = ''
  @Trace orderNumber: string = ''
  @Trace status: number = 0
  @Trace address: AddressModel = new AddressModel()       // 嵌套 @ObservedV2
  @Trace items: OrderItemModel[] = []                     // 嵌套 @ObservedV2 数组
  @Trace totalAmount: number = 0
  @Trace createdAt: number = 0
  @Trace remark: string = ''

  constructor(
    id: string = '',
    orderNumber: string = '',
    status: number = 0,
    address: AddressModel = new AddressModel(),
    items: OrderItemModel[] = [],
    totalAmount: number = 0,
    createdAt: number = Date.now(),
    remark: string = ''
  ) {
    this.id = id
    this.orderNumber = orderNumber
    this.status = status
    this.address = address
    this.items = items
    this.totalAmount = totalAmount
    this.createdAt = createdAt
    this.remark = remark
  }

  static fromJson(json: Record<string, Object>): OrderModel {
    let addressJson = JsonHelper.getObject(json, 'address')
    let address = addressJson !== null
      ? AddressModel.fromJson(addressJson)
      : new AddressModel()

    let itemsJson = JsonHelper.getArray<Record<string, Object>>(json, 'items')
    let items: OrderItemModel[] = []
    for (let itemJson of itemsJson) {
      items.push(OrderItemModel.fromJson(itemJson))
    }

    return new OrderModel(
      JsonHelper.getString(json, 'id'),
      JsonHelper.getString(json, 'orderNumber'),
      JsonHelper.getNumber(json, 'status'),
      address,
      items,
      JsonHelper.getNumber(json, 'totalAmount'),
      JsonHelper.getNumber(json, 'createdAt', Date.now()),
      JsonHelper.getString(json, 'remark')
    )
  }
}
```

**嵌套模型在组件中的使用（V2）：**

```typescript
@Entry
@ComponentV2
struct OrderDetailPage {
  @Local order: OrderModel = new OrderModel(
    '001', 'ORD-20240101-001', 1,
    new AddressModel(1, '广东省', '深圳市', '南山区', '科技路100号', true),
    [
      new OrderItemModel(1, 'HarmonyOS手机', 4999, 1, ''),
      new OrderItemModel(2, '手机壳', 29, 2, '')
    ],
    5057
  )

  build() {
    Column({ space: 12 }) {
      // V2 直接用 @Param 接收嵌套的 @ObservedV2 实例
      AddressCard({ address: this.order.address })

      ForEach(this.order.items, (item: OrderItemModel) => {
        OrderItemCard({ item: item })
      }, (item: OrderItemModel) => item.productId.toString())

      Text(`总金额: ¥${this.order.totalAmount}`)

      Button('修改地址街道')
        .onClick(() => {
          // 修改嵌套对象的 @Trace 属性，UI 自动刷新
          this.order.address.street = '科技路200号'
        })

      Button('修改第一项数量')
        .onClick(() => {
          if (this.order.items.length > 0) {
            this.order.items[0].quantity += 1
          }
        })
    }
  }
}

@ComponentV2
struct AddressCard {
  @Param address: AddressModel = new AddressModel()  // 替代 V1 @ObjectLink

  build() {
    Column() {
      Text(`收货地址: ${this.address.fullAddress}`)
      if (this.address.isDefault) {
        Text('默认地址').fontColor(Color.Orange)
      }
    }
  }
}

@ComponentV2
struct OrderItemCard {
  @Param item: OrderItemModel = new OrderItemModel()

  build() {
    Row() {
      Text(this.item.productName).layoutWeight(1)
      Text(`x${this.item.quantity}`)
      Text(`¥${this.item.subtotal}`)
    }
    .width('100%')
  }
}
```

---

## 5. 枚举 + 模型模式

枚举本身与装饰器无关，V1/V2 完全一致。区别仅在模型类装饰器：

```typescript
// ==========================================
// 枚举定义 —— 订单状态（V1/V2 完全相同）
// ==========================================

export enum OrderStatus {
  PENDING = 0,       // 待付款
  PAID = 1,          // 已付款
  SHIPPED = 2,       // 已发货
  DELIVERED = 3,     // 已送达
  COMPLETED = 4,     // 已完成
  CANCELLED = 5,     // 已取消
  REFUNDING = 6,     // 退款中
  REFUNDED = 7       // 已退款
}

export class OrderStatusUtil {
  static getText(status: OrderStatus): string {
    switch (status) {
      case OrderStatus.PENDING:   return '待付款'
      case OrderStatus.PAID:      return '已付款'
      case OrderStatus.SHIPPED:   return '已发货'
      case OrderStatus.DELIVERED: return '已送达'
      case OrderStatus.COMPLETED: return '已完成'
      case OrderStatus.CANCELLED: return '已取消'
      case OrderStatus.REFUNDING: return '退款中'
      case OrderStatus.REFUNDED:  return '已退款'
      default:                    return '未知'
    }
  }

  static getColor(status: OrderStatus): ResourceColor {
    switch (status) {
      case OrderStatus.PENDING:   return '#FF9800'
      case OrderStatus.PAID:      return '#2196F3'
      case OrderStatus.SHIPPED:   return '#4CAF50'
      case OrderStatus.DELIVERED: return '#4CAF50'
      case OrderStatus.COMPLETED: return '#9E9E9E'
      case OrderStatus.CANCELLED: return '#F44336'
      case OrderStatus.REFUNDING: return '#FF5722'
      case OrderStatus.REFUNDED:  return '#9E9E9E'
      default:                    return '#000000'
    }
  }

  static fromValue(value: number): OrderStatus {
    if (value >= OrderStatus.PENDING && value <= OrderStatus.REFUNDED) {
      return value as OrderStatus
    }
    return OrderStatus.PENDING
  }

  static canCancel(status: OrderStatus): boolean {
    return status === OrderStatus.PENDING || status === OrderStatus.PAID
  }

  static canRefund(status: OrderStatus): boolean {
    return status === OrderStatus.PAID ||
           status === OrderStatus.SHIPPED ||
           status === OrderStatus.DELIVERED
  }
}

// ==========================================
// 在 V2 模型中使用枚举
// ==========================================

@ObservedV2
export class OrderWithStatus {
  @Trace id: string = ''
  @Trace orderNumber: string = ''
  @Trace status: OrderStatus = OrderStatus.PENDING
  @Trace totalAmount: number = 0

  constructor(
    id: string = '',
    orderNumber: string = '',
    status: OrderStatus = OrderStatus.PENDING,
    totalAmount: number = 0
  ) {
    this.id = id
    this.orderNumber = orderNumber
    this.status = status
    this.totalAmount = totalAmount
  }

  static fromJson(json: Record<string, Object>): OrderWithStatus {
    return new OrderWithStatus(
      json['id'] as string,
      json['orderNumber'] as string,
      OrderStatusUtil.fromValue(json['status'] as number),
      json['totalAmount'] as number
    )
  }

  // V2 用 @Computed 自动缓存派生状态
  @Computed
  get statusText(): string {
    return OrderStatusUtil.getText(this.status)
  }

  @Computed
  get statusColor(): ResourceColor {
    return OrderStatusUtil.getColor(this.status)
  }

  @Computed
  get canCancel(): boolean {
    return OrderStatusUtil.canCancel(this.status)
  }
}
```

**使用示例（V2）：**

```typescript
@ComponentV2
struct OrderStatusBadge {
  @Param order: OrderWithStatus = new OrderWithStatus()  // 替代 V1 @ObjectLink

  build() {
    Row() {
      Text(this.order.orderNumber).layoutWeight(1)
      Text(this.order.statusText)
        .fontColor(this.order.statusColor)
        .fontSize(14)

      if (this.order.canCancel) {
        Button('取消订单')
          .onClick(() => {
            this.order.status = OrderStatus.CANCELLED
          })
      }
    }
    .width('100%')
    .padding(12)
  }
}
```

---

## 6. 模型计算属性（V2 推荐 @Computed）

V2 引入 `@Computed`，自动缓存 + 依赖追踪。比 V1 的普通 getter 更高效（多次访问只计算一次，依赖变化时自动失效）。

```typescript
// ==========================================
// 计算属性模式 —— 购物车模型（V2）
// ==========================================

@ObservedV2
export class CartItemModel {
  @Trace productId: number = 0
  @Trace productName: string = ''
  @Trace price: number = 0
  @Trace quantity: number = 1
  @Trace imageUrl: string = ''
  @Trace isSelected: boolean = true

  constructor(
    productId: number = 0,
    productName: string = '',
    price: number = 0,
    quantity: number = 1,
    imageUrl: string = '',
    isSelected: boolean = true
  ) {
    this.productId = productId
    this.productName = productName
    this.price = price
    this.quantity = quantity
    this.imageUrl = imageUrl
    this.isSelected = isSelected
  }

  // V2: @Computed 自动缓存
  @Computed
  get subtotal(): number {
    return this.price * this.quantity
  }

  @Computed
  get formattedPrice(): string {
    return `¥${this.price.toFixed(2)}`
  }

  @Computed
  get formattedSubtotal(): string {
    return `¥${this.subtotal.toFixed(2)}`
  }
}

@ObservedV2
export class CartModel {
  @Trace items: CartItemModel[] = []

  constructor(items: CartItemModel[] = []) {
    this.items = items
  }

  // ---- @Computed 计算属性 ----

  @Computed
  get selectedItems(): CartItemModel[] {
    return this.items.filter((item: CartItemModel) => item.isSelected)
  }

  @Computed
  get selectedCount(): number {
    let count = 0
    for (let item of this.items) {
      if (item.isSelected) {
        count += item.quantity
      }
    }
    return count
  }

  @Computed
  get totalAmount(): number {
    let total = 0
    for (let item of this.items) {
      if (item.isSelected) {
        total += item.subtotal
      }
    }
    return total
  }

  @Computed
  get formattedTotal(): string {
    return `¥${this.totalAmount.toFixed(2)}`
  }

  @Computed
  get isAllSelected(): boolean {
    if (this.items.length === 0) {
      return false
    }
    for (let item of this.items) {
      if (!item.isSelected) {
        return false
      }
    }
    return true
  }

  @Computed
  get isEmpty(): boolean {
    return this.items.length === 0
  }

  // ---- 操作方法 ----

  toggleSelectAll(): void {
    let newState = !this.isAllSelected
    for (let item of this.items) {
      item.isSelected = newState
    }
  }

  increaseQuantity(productId: number): void {
    for (let item of this.items) {
      if (item.productId === productId) {
        item.quantity += 1
        break
      }
    }
  }

  decreaseQuantity(productId: number): void {
    for (let item of this.items) {
      if (item.productId === productId && item.quantity > 1) {
        item.quantity -= 1
        break
      }
    }
  }

  removeItem(productId: number): void {
    this.items = this.items.filter((item: CartItemModel) => item.productId !== productId)
  }

  clearSelected(): void {
    this.items = this.items.filter((item: CartItemModel) => !item.isSelected)
  }
}
```

**使用示例（V2）：**

```typescript
@Entry
@ComponentV2
struct CartPage {
  @Local cart: CartModel = new CartModel([
    new CartItemModel(1, 'HarmonyOS手机', 4999, 1),
    new CartItemModel(2, '蓝牙耳机', 299, 2),
    new CartItemModel(3, '手机壳', 29, 3)
  ])

  build() {
    Column() {
      ForEach(this.cart.items, (item: CartItemModel) => {
        CartItemRow({ item: item })
      }, (item: CartItemModel) => item.productId.toString())

      Row() {
        Checkbox()
          .select(this.cart.isAllSelected)
          .onChange(() => {
            this.cart.toggleSelectAll()
          })
        Text('全选')

        Blank()

        Text(`合计: ${this.cart.formattedTotal}`).fontColor(Color.Red)

        Button(`结算(${this.cart.selectedCount})`)
          .enabled(this.cart.selectedCount > 0)
      }
      .width('100%')
      .padding(12)
    }
  }
}

@ComponentV2
struct CartItemRow {
  @Param item: CartItemModel = new CartItemModel()  // 替代 V1 @ObjectLink

  build() {
    Row({ space: 8 }) {
      Checkbox()
        .select(this.item.isSelected)
        .onChange((value: boolean) => {
          this.item.isSelected = value
        })
      Text(this.item.productName).layoutWeight(1)
      Text(this.item.formattedPrice)
      Text(`x${this.item.quantity}`)
      Text(this.item.formattedSubtotal).fontColor(Color.Red)
    }
    .width('100%')
    .padding(8)
  }
}
```

---

## 7. 模型验证模式（V2）

`ValidationResult` 工具类与装饰器无关，模型类装饰器为 `@ObservedV2`，配合 `@Monitor` 实现实时验证。

```typescript
// ==========================================
// 验证结果类（V1/V2 通用）
// ==========================================

export class ValidationResult {
  isValid: boolean
  errors: Map<string, string>

  constructor() {
    this.isValid = true
    this.errors = new Map()
  }

  addError(field: string, message: string): void {
    this.errors.set(field, message)
    this.isValid = false
  }

  getError(field: string): string {
    return this.errors.get(field) ?? ''
  }

  hasError(field: string): boolean {
    return this.errors.has(field)
  }

  get allErrors(): string {
    let messages: string[] = []
    this.errors.forEach((value: string) => {
      messages.push(value)
    })
    return messages.join('\n')
  }
}

// ==========================================
// 带验证的用户注册模型（V2）
// ==========================================

@ObservedV2
export class RegisterFormModel {
  @Trace username: string = ''
  @Trace password: string = ''
  @Trace confirmPassword: string = ''
  @Trace email: string = ''
  @Trace phone: string = ''
  @Trace age: number = 0
  @Trace agreeTerms: boolean = false

  validate(): ValidationResult {
    let result = new ValidationResult()

    if (this.username.length === 0) {
      result.addError('username', '用户名不能为空')
    } else if (this.username.length < 3) {
      result.addError('username', '用户名不能少于3个字符')
    } else if (this.username.length > 20) {
      result.addError('username', '用户名不能超过20个字符')
    }

    if (this.password.length === 0) {
      result.addError('password', '密码不能为空')
    } else if (this.password.length < 6) {
      result.addError('password', '密码不能少于6位')
    } else if (this.password.length > 32) {
      result.addError('password', '密码不能超过32位')
    }

    if (this.confirmPassword !== this.password) {
      result.addError('confirmPassword', '两次输入的密码不一致')
    }

    if (this.email.length === 0) {
      result.addError('email', '邮箱不能为空')
    } else if (!this.email.includes('@') || !this.email.includes('.')) {
      result.addError('email', '邮箱格式不正确')
    }

    if (this.phone.length === 0) {
      result.addError('phone', '手机号不能为空')
    } else if (this.phone.length !== 11) {
      result.addError('phone', '手机号必须为11位')
    }

    if (this.age < 1 || this.age > 150) {
      result.addError('age', '请输入有效年龄')
    }

    if (!this.agreeTerms) {
      result.addError('agreeTerms', '请同意用户协议')
    }

    return result
  }

  validateField(field: string): string {
    switch (field) {
      case 'username':
        if (this.username.length === 0) return '用户名不能为空'
        if (this.username.length < 3) return '用户名不能少于3个字符'
        return ''
      case 'password':
        if (this.password.length === 0) return '密码不能为空'
        if (this.password.length < 6) return '密码不能少于6位'
        return ''
      case 'email':
        if (this.email.length > 0 && (!this.email.includes('@') || !this.email.includes('.'))) {
          return '邮箱格式不正确'
        }
        return ''
      case 'phone':
        if (this.phone.length > 0 && this.phone.length !== 11) {
          return '手机号必须为11位'
        }
        return ''
      default:
        return ''
    }
  }

  toJson(): Record<string, Object> {
    return {
      'username': this.username as Object,
      'password': this.password as Object,
      'email': this.email as Object,
      'phone': this.phone as Object,
      'age': this.age as Object
    }
  }
}
```

**使用示例（V2，可选用 @Monitor 实现实时验证）：**

```typescript
@Entry
@ComponentV2
struct RegisterPage {
  @Local form: RegisterFormModel = new RegisterFormModel()
  @Local errors: Map<string, string> = new Map()
  @Local isSubmitting: boolean = false

  // V2: @Monitor 自动监听字段变化，实时校验
  @Monitor('form.username')
  onUsernameChange(monitor: IMonitor): void {
    let err = this.form.validateField('username')
    if (err.length > 0) {
      this.errors.set('username', err)
    } else {
      this.errors.delete('username')
    }
  }

  @Monitor('form.password')
  onPasswordChange(monitor: IMonitor): void {
    let err = this.form.validateField('password')
    if (err.length > 0) {
      this.errors.set('password', err)
    } else {
      this.errors.delete('password')
    }
  }

  build() {
    Column({ space: 16 }) {
      TextInput({ placeholder: '用户名', text: this.form.username })
        .onChange((value: string) => { this.form.username = value })
      if (this.errors.has('username')) {
        Text(this.errors.get('username')).fontColor(Color.Red).fontSize(12)
      }

      TextInput({ placeholder: '密码', text: this.form.password })
        .type(InputType.Password)
        .onChange((value: string) => { this.form.password = value })
      if (this.errors.has('password')) {
        Text(this.errors.get('password')).fontColor(Color.Red).fontSize(12)
      }

      TextInput({ placeholder: '邮箱', text: this.form.email })
        .onChange((value: string) => { this.form.email = value })

      TextInput({ placeholder: '手机号', text: this.form.phone })
        .onChange((value: string) => { this.form.phone = value })

      Row() {
        Checkbox()
          .select(this.form.agreeTerms)
          .onChange((value: boolean) => { this.form.agreeTerms = value })
        Text('我已阅读并同意用户协议')
      }

      Button('注册')
        .enabled(!this.isSubmitting)
        .width('100%')
        .onClick(() => {
          let validation = this.form.validate()
          if (!validation.isValid) {
            this.errors = validation.errors
            return
          }
          this.isSubmitting = true
          let jsonData = this.form.toJson()
          console.info(`提交注册: ${JSON.stringify(jsonData)}`)
        })
    }
    .padding(20)
  }
}
```

---

## V1 → V2 速查对照

| V1 写法 | V2 写法 | 备注 |
|---|---|---|
| `@Observed class X { name: string = '' }` | `@ObservedV2 class X { @Trace name: string = '' }` | 必须显式 `@Trace` 才能观察 |
| `@Component struct Y { @State x: X = new X() }` | `@ComponentV2 struct Y { @Local x: X = new X() }` | 父持有 |
| `@Component struct Z { @ObjectLink x: X }` | `@ComponentV2 struct Z { @Param x: X = new X() }` | 子接收（`@Param` 必须给默认值） |
| `private static instance + getInstance()` | `AppStorageV2.connect(Cls, key, () => new Cls())!` | 单例 → 框架托管 |
| `get derived(): T { return ... }` | `@Computed get derived(): T { return ... }` | 自动缓存（推荐） |
| `@Watch('field') onChange()` | `@Monitor('field') onChange(m: IMonitor)` | 方法装饰器 |
