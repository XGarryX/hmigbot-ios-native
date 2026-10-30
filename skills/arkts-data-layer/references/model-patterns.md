# ArkTS 数据模型模式参考（**V1 历史文档 — Legacy**）

> ⚠️ **本项目锁 ArkTS V2**。本文档为 **V1 历史参考**（`@Observed / @ObjectLink / @State` 等），仅用于阅读老代码或迁移老项目时查阅。
>
> **新代码请使用 V2 装饰器**：参阅 [`v2-model-patterns.md`](./v2-model-patterns.md)（V2 主参考）和 [`SKILL.md`](../SKILL.md)。
>
> V1 → V2 关键映射：
> - `@Observed` → `@ObservedV2`（类装饰器）
> - 类内属性 → 加 `@Trace` 显式标记可观察
> - 子组件 `@ObjectLink xxx: Cls` → `@Param xxx: Cls = new Cls()`（直接传 `@ObservedV2` 实例）
> - 父组件 `@State model: Cls = new Cls()` → `@Local model: Cls = new Cls()`

---

> 完整的 ArkTS 数据模型模式，涵盖 @Observed 模型、单例、JSON 转换、嵌套模型、枚举、计算属性和验证。

---

## 1. 基础 @Observed 模型

`@Observed` 装饰器使类的属性变化可被 UI 框架追踪。配合 `@ObjectLink` 在子组件中使用。

```typescript
// ==========================================
// 基础 @Observed 模型 —— 包含常见字段类型
// ==========================================

@Observed
export class UserModel {
  // 基本类型字段
  id: number
  name: string
  email: string
  age: number
  isActive: boolean
  balance: number

  // 可选字段
  avatar?: string
  bio?: string

  // 数组字段
  tags: string[]

  // 日期用时间戳表示（ArkTS 中 Date 序列化不便）
  createdAt: number
  updatedAt: number

  constructor(
    id: number,
    name: string,
    email: string,
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

**在组件中使用：**

```typescript
// 父组件持有 @State，子组件用 @ObjectLink 接收
@Entry
@Component
struct UserPage {
  @State user: UserModel = new UserModel(1, '张三', 'zhangsan@example.com', 28)

  build() {
    Column() {
      // 子组件通过 @ObjectLink 接收，属性变化自动刷新
      UserCard({ user: this.user })

      Button('修改姓名')
        .onClick(() => {
          // 直接修改属性即可触发 UI 更新
          this.user.name = '李四'
        })
    }
  }
}

@Component
struct UserCard {
  @ObjectLink user: UserModel

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

## 2. 单例模型模式（getInstance）

用于全局共享的数据管理器，例如用户登录状态、应用配置。

```typescript
// ==========================================
// 单例模式 —— 全局共享数据管理
// ==========================================

@Observed
export class AppConfig {
  // 应用配置字段
  apiBaseUrl: string
  appVersion: string
  debugMode: boolean
  pageSize: number
  theme: string
  language: string

  // 私有静态实例
  private static instance: AppConfig | null = null

  // 私有构造函数，防止外部 new
  private constructor() {
    this.apiBaseUrl = 'https://api.example.com/v1'
    this.appVersion = '1.0.0'
    this.debugMode = false
    this.pageSize = 20
    this.theme = 'light'
    this.language = 'zh-CN'
  }

  // 获取单例
  static getInstance(): AppConfig {
    if (AppConfig.instance === null) {
      AppConfig.instance = new AppConfig()
    }
    return AppConfig.instance!
  }

  // 从服务端配置初始化
  static fromJson(json: Record<string, Object>): void {
    let config = AppConfig.getInstance()
    if (json['apiBaseUrl'] !== undefined) {
      config.apiBaseUrl = json['apiBaseUrl'] as string
    }
    if (json['debugMode'] !== undefined) {
      config.debugMode = json['debugMode'] as boolean
    }
    if (json['pageSize'] !== undefined) {
      config.pageSize = json['pageSize'] as number
    }
    if (json['theme'] !== undefined) {
      config.theme = json['theme'] as string
    }
    if (json['language'] !== undefined) {
      config.language = json['language'] as string
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
```

**使用示例：**

```typescript
// 在任意位置获取配置
let config = AppConfig.getInstance()
console.info(`API地址: ${config.apiBaseUrl}`)

// 修改配置
config.theme = 'dark'
config.pageSize = 30

// 在组件中使用
@Entry
@Component
struct SettingsPage {
  // 注意：单例需要通过 @State 包裹才能触发组件刷新
  @State config: AppConfig = AppConfig.getInstance()

  build() {
    Column() {
      Text(`主题: ${this.config.theme}`)
      Text(`每页数量: ${this.config.pageSize}`)

      Button('切换深色模式')
        .onClick(() => {
          this.config.theme = this.config.theme === 'light' ? 'dark' : 'light'
        })
    }
  }
}
```

---

## 3. fromJson / toJson 完整转换模式

处理复杂 JSON 结构的完整模式，包含类型安全和默认值处理。

```typescript
// ==========================================
// JSON 转换工具 —— 安全的类型转换辅助
// ==========================================

export class JsonHelper {
  // 安全取字符串，带默认值
  static getString(json: Record<string, Object>, key: string, defaultVal: string = ''): string {
    let value = json[key]
    if (value === undefined || value === null) {
      return defaultVal
    }
    return value as string
  }

  // 安全取数字
  static getNumber(json: Record<string, Object>, key: string, defaultVal: number = 0): number {
    let value = json[key]
    if (value === undefined || value === null) {
      return defaultVal
    }
    return value as number
  }

  // 安全取布尔值
  static getBoolean(json: Record<string, Object>, key: string, defaultVal: boolean = false): boolean {
    let value = json[key]
    if (value === undefined || value === null) {
      return defaultVal
    }
    return value as boolean
  }

  // 安全取数组
  static getArray<T>(json: Record<string, Object>, key: string): T[] {
    let value = json[key]
    if (value === undefined || value === null) {
      return []
    }
    return value as T[]
  }

  // 安全取嵌套对象
  static getObject(json: Record<string, Object>, key: string): Record<string, Object> | null {
    let value = json[key]
    if (value === undefined || value === null) {
      return null
    }
    return value as Record<string, Object>
  }
}

// ==========================================
// 使用 JsonHelper 的模型示例
// ==========================================

@Observed
export class ProductModel {
  id: number
  title: string
  description: string
  price: number
  originalPrice: number
  stock: number
  images: string[]
  categoryId: number
  isOnSale: boolean

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

  // 批量从 JSON 数组转换
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

## 4. 嵌套模型模式

`@Observed` 类引用其他 `@Observed` 类时，内层属性变化也能被追踪。

```typescript
// ==========================================
// 嵌套 @Observed 模型
// ==========================================

// 地址模型
@Observed
export class AddressModel {
  id: number
  province: string
  city: string
  district: string
  street: string
  isDefault: boolean

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

  // 完整地址字符串
  get fullAddress(): string {
    return `${this.province}${this.city}${this.district}${this.street}`
  }
}

// 订单项模型
@Observed
export class OrderItemModel {
  productId: number
  productName: string
  price: number
  quantity: number
  imageUrl: string

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

  // 小计金额
  get subtotal(): number {
    return this.price * this.quantity
  }
}

// 订单模型 —— 嵌套引用地址和订单项
@Observed
export class OrderModel {
  id: string
  orderNumber: string
  status: number
  address: AddressModel          // 嵌套 @Observed 对象
  items: OrderItemModel[]        // 嵌套 @Observed 数组
  totalAmount: number
  createdAt: number
  remark: string

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
    // 解析嵌套地址对象
    let addressJson = JsonHelper.getObject(json, 'address')
    let address = addressJson !== null
      ? AddressModel.fromJson(addressJson)
      : new AddressModel()

    // 解析嵌套订单项数组
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

  toJson(): Record<string, Object> {
    let itemsJson: Record<string, Object>[] = []
    for (let item of this.items) {
      itemsJson.push({
        'productId': item.productId as Object,
        'productName': item.productName as Object,
        'price': item.price as Object,
        'quantity': item.quantity as Object,
        'imageUrl': item.imageUrl as Object
      })
    }
    return {
      'id': this.id as Object,
      'orderNumber': this.orderNumber as Object,
      'status': this.status as Object,
      'address': {
        'province': this.address.province as Object,
        'city': this.address.city as Object,
        'district': this.address.district as Object,
        'street': this.address.street as Object
      } as Object,
      'items': itemsJson as Object,
      'totalAmount': this.totalAmount as Object,
      'createdAt': this.createdAt as Object,
      'remark': this.remark as Object
    }
  }
}
```

**嵌套模型在组件中的使用：**

```typescript
@Entry
@Component
struct OrderDetailPage {
  @State order: OrderModel = new OrderModel(
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
      // 地址组件 —— 用 @ObjectLink 接收嵌套对象
      AddressCard({ address: this.order.address })

      // 订单项列表
      ForEach(this.order.items, (item: OrderItemModel) => {
        OrderItemCard({ item: item })
      }, (item: OrderItemModel) => item.productId.toString())

      Text(`总金额: ¥${this.order.totalAmount}`)

      Button('修改地址街道')
        .onClick(() => {
          // 修改嵌套对象的属性，UI 自动刷新
          this.order.address.street = '科技路200号'
        })

      Button('修改第一项数量')
        .onClick(() => {
          // 修改嵌套数组元素的属性
          if (this.order.items.length > 0) {
            this.order.items[0].quantity += 1
          }
        })
    }
  }
}

@Component
struct AddressCard {
  @ObjectLink address: AddressModel

  build() {
    Column() {
      Text(`收货地址: ${this.address.fullAddress}`)
      if (this.address.isDefault) {
        Text('默认地址')
          .fontColor(Color.Orange)
      }
    }
  }
}

@Component
struct OrderItemCard {
  @ObjectLink item: OrderItemModel

  build() {
    Row() {
      Text(this.item.productName)
        .layoutWeight(1)
      Text(`x${this.item.quantity}`)
      Text(`¥${this.item.subtotal}`)
    }
    .width('100%')
  }
}
```

---

## 5. 枚举 + 模型模式

用枚举管理状态字段，配合辅助方法实现状态文本和颜色映射。

```typescript
// ==========================================
// 枚举定义 —— 订单状态
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

// 枚举辅助工具类
export class OrderStatusUtil {
  // 状态 -> 显示文本
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

  // 状态 -> 颜色
  static getColor(status: OrderStatus): ResourceColor {
    switch (status) {
      case OrderStatus.PENDING:   return '#FF9800'  // 橙色
      case OrderStatus.PAID:      return '#2196F3'  // 蓝色
      case OrderStatus.SHIPPED:   return '#4CAF50'  // 绿色
      case OrderStatus.DELIVERED: return '#4CAF50'
      case OrderStatus.COMPLETED: return '#9E9E9E'  // 灰色
      case OrderStatus.CANCELLED: return '#F44336'  // 红色
      case OrderStatus.REFUNDING: return '#FF5722'
      case OrderStatus.REFUNDED:  return '#9E9E9E'
      default:                    return '#000000'
    }
  }

  // 从服务端数字值转换为枚举
  static fromValue(value: number): OrderStatus {
    if (value >= OrderStatus.PENDING && value <= OrderStatus.REFUNDED) {
      return value as OrderStatus
    }
    return OrderStatus.PENDING
  }

  // 是否可取消
  static canCancel(status: OrderStatus): boolean {
    return status === OrderStatus.PENDING || status === OrderStatus.PAID
  }

  // 是否可退款
  static canRefund(status: OrderStatus): boolean {
    return status === OrderStatus.PAID ||
           status === OrderStatus.SHIPPED ||
           status === OrderStatus.DELIVERED
  }
}

// ==========================================
// 在模型中使用枚举
// ==========================================

@Observed
export class OrderWithStatus {
  id: string
  orderNumber: string
  status: OrderStatus
  totalAmount: number

  constructor(
    id: string,
    orderNumber: string,
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

  // 状态显示文本
  get statusText(): string {
    return OrderStatusUtil.getText(this.status)
  }

  // 状态颜色
  get statusColor(): ResourceColor {
    return OrderStatusUtil.getColor(this.status)
  }

  // 能否取消
  get canCancel(): boolean {
    return OrderStatusUtil.canCancel(this.status)
  }
}
```

**使用示例：**

```typescript
@Component
struct OrderStatusBadge {
  @ObjectLink order: OrderWithStatus

  build() {
    Row() {
      Text(this.order.orderNumber)
        .layoutWeight(1)
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

## 6. 模型计算属性（getter 方法）

通过 getter 方法实现派生数据，避免冗余字段。

```typescript
// ==========================================
// 计算属性模式 —— 购物车模型
// ==========================================

@Observed
export class CartItemModel {
  productId: number
  productName: string
  price: number
  quantity: number
  imageUrl: string
  isSelected: boolean

  constructor(
    productId: number,
    productName: string,
    price: number,
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

  // 计算属性：小计金额
  get subtotal(): number {
    return this.price * this.quantity
  }

  // 计算属性：格式化价格
  get formattedPrice(): string {
    return `¥${this.price.toFixed(2)}`
  }

  // 计算属性：格式化小计
  get formattedSubtotal(): string {
    return `¥${this.subtotal.toFixed(2)}`
  }
}

@Observed
export class CartModel {
  items: CartItemModel[]

  constructor(items: CartItemModel[] = []) {
    this.items = items
  }

  // ---- 计算属性 ----

  // 选中的商品列表
  get selectedItems(): CartItemModel[] {
    return this.items.filter((item: CartItemModel) => item.isSelected)
  }

  // 选中商品总数量
  get selectedCount(): number {
    let count = 0
    for (let item of this.items) {
      if (item.isSelected) {
        count += item.quantity
      }
    }
    return count
  }

  // 选中商品总金额
  get totalAmount(): number {
    let total = 0
    for (let item of this.items) {
      if (item.isSelected) {
        total += item.subtotal
      }
    }
    return total
  }

  // 格式化总金额
  get formattedTotal(): string {
    return `¥${this.totalAmount.toFixed(2)}`
  }

  // 是否全选
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

  // 购物车是否为空
  get isEmpty(): boolean {
    return this.items.length === 0
  }

  // ---- 操作方法 ----

  // 全选 / 取消全选
  toggleSelectAll(): void {
    let newState = !this.isAllSelected
    for (let item of this.items) {
      item.isSelected = newState
    }
  }

  // 增加数量
  increaseQuantity(productId: number): void {
    for (let item of this.items) {
      if (item.productId === productId) {
        item.quantity += 1
        break
      }
    }
  }

  // 减少数量（最少为1）
  decreaseQuantity(productId: number): void {
    for (let item of this.items) {
      if (item.productId === productId && item.quantity > 1) {
        item.quantity -= 1
        break
      }
    }
  }

  // 移除商品
  removeItem(productId: number): void {
    this.items = this.items.filter((item: CartItemModel) => item.productId !== productId)
  }

  // 清空选中商品
  clearSelected(): void {
    this.items = this.items.filter((item: CartItemModel) => !item.isSelected)
  }
}
```

**使用示例：**

```typescript
@Entry
@Component
struct CartPage {
  @State cart: CartModel = new CartModel([
    new CartItemModel(1, 'HarmonyOS手机', 4999, 1),
    new CartItemModel(2, '蓝牙耳机', 299, 2),
    new CartItemModel(3, '手机壳', 29, 3)
  ])

  build() {
    Column() {
      // 商品列表
      ForEach(this.cart.items, (item: CartItemModel) => {
        CartItemRow({ item: item })
      }, (item: CartItemModel) => item.productId.toString())

      // 底部结算栏 —— 使用计算属性
      Row() {
        Checkbox()
          .select(this.cart.isAllSelected)
          .onChange(() => {
            this.cart.toggleSelectAll()
          })
        Text('全选')

        Blank()

        Text(`合计: ${this.cart.formattedTotal}`)
          .fontColor(Color.Red)

        Button(`结算(${this.cart.selectedCount})`)
          .enabled(this.cart.selectedCount > 0)
      }
      .width('100%')
      .padding(12)
    }
  }
}

@Component
struct CartItemRow {
  @ObjectLink item: CartItemModel

  build() {
    Row({ space: 8 }) {
      Checkbox()
        .select(this.item.isSelected)
        .onChange((value: boolean) => {
          this.item.isSelected = value
        })

      Text(this.item.productName)
        .layoutWeight(1)
      Text(this.item.formattedPrice)
      Text(`x${this.item.quantity}`)
      Text(this.item.formattedSubtotal)
        .fontColor(Color.Red)
    }
    .width('100%')
    .padding(8)
  }
}
```

---

## 7. 模型验证模式

在提交数据前进行字段验证，收集所有错误信息。

```typescript
// ==========================================
// 验证结果类
// ==========================================

export class ValidationResult {
  isValid: boolean
  errors: Map<string, string>  // 字段名 -> 错误信息

  constructor() {
    this.isValid = true
    this.errors = new Map()
  }

  // 添加错误
  addError(field: string, message: string): void {
    this.errors.set(field, message)
    this.isValid = false
  }

  // 获取指定字段的错误
  getError(field: string): string {
    return this.errors.get(field) ?? ''
  }

  // 是否有指定字段的错误
  hasError(field: string): boolean {
    return this.errors.has(field)
  }

  // 获取所有错误信息（拼接为一个字符串）
  get allErrors(): string {
    let messages: string[] = []
    this.errors.forEach((value: string) => {
      messages.push(value)
    })
    return messages.join('\n')
  }
}

// ==========================================
// 带验证的用户注册模型
// ==========================================

@Observed
export class RegisterFormModel {
  username: string
  password: string
  confirmPassword: string
  email: string
  phone: string
  age: number
  agreeTerms: boolean

  constructor() {
    this.username = ''
    this.password = ''
    this.confirmPassword = ''
    this.email = ''
    this.phone = ''
    this.age = 0
    this.agreeTerms = false
  }

  // 完整验证
  validate(): ValidationResult {
    let result = new ValidationResult()

    // 用户名验证
    if (this.username.length === 0) {
      result.addError('username', '用户名不能为空')
    } else if (this.username.length < 3) {
      result.addError('username', '用户名不能少于3个字符')
    } else if (this.username.length > 20) {
      result.addError('username', '用户名不能超过20个字符')
    }

    // 密码验证
    if (this.password.length === 0) {
      result.addError('password', '密码不能为空')
    } else if (this.password.length < 6) {
      result.addError('password', '密码不能少于6位')
    } else if (this.password.length > 32) {
      result.addError('password', '密码不能超过32位')
    }

    // 确认密码
    if (this.confirmPassword !== this.password) {
      result.addError('confirmPassword', '两次输入的密码不一致')
    }

    // 邮箱验证（简单格式检查）
    if (this.email.length === 0) {
      result.addError('email', '邮箱不能为空')
    } else if (!this.email.includes('@') || !this.email.includes('.')) {
      result.addError('email', '邮箱格式不正确')
    }

    // 手机号验证（中国大陆格式）
    if (this.phone.length === 0) {
      result.addError('phone', '手机号不能为空')
    } else if (this.phone.length !== 11) {
      result.addError('phone', '手机号必须为11位')
    }

    // 年龄验证
    if (this.age < 1 || this.age > 150) {
      result.addError('age', '请输入有效年龄')
    }

    // 协议勾选
    if (!this.agreeTerms) {
      result.addError('agreeTerms', '请同意用户协议')
    }

    return result
  }

  // 单字段验证（实时提示）
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

  // 转为提交用的 JSON
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

**使用示例：**

```typescript
@Entry
@Component
struct RegisterPage {
  @State form: RegisterFormModel = new RegisterFormModel()
  @State errors: Map<string, string> = new Map()
  @State isSubmitting: boolean = false

  build() {
    Column({ space: 16 }) {
      // 用户名
      TextInput({ placeholder: '用户名', text: this.form.username })
        .onChange((value: string) => {
          this.form.username = value
          // 实时验证
          let err = this.form.validateField('username')
          if (err.length > 0) {
            this.errors.set('username', err)
          } else {
            this.errors.delete('username')
          }
        })
      if (this.errors.has('username')) {
        Text(this.errors.get('username'))
          .fontColor(Color.Red)
          .fontSize(12)
      }

      // 密码
      TextInput({ placeholder: '密码', text: this.form.password })
        .type(InputType.Password)
        .onChange((value: string) => {
          this.form.password = value
        })
      if (this.errors.has('password')) {
        Text(this.errors.get('password'))
          .fontColor(Color.Red)
          .fontSize(12)
      }

      // 邮箱
      TextInput({ placeholder: '邮箱', text: this.form.email })
        .onChange((value: string) => {
          this.form.email = value
        })

      // 手机号
      TextInput({ placeholder: '手机号', text: this.form.phone })
        .onChange((value: string) => {
          this.form.phone = value
        })

      // 协议
      Row() {
        Checkbox()
          .select(this.form.agreeTerms)
          .onChange((value: boolean) => {
            this.form.agreeTerms = value
          })
        Text('我已阅读并同意用户协议')
      }

      // 提交
      Button('注册')
        .enabled(!this.isSubmitting)
        .width('100%')
        .onClick(() => {
          let validation = this.form.validate()
          if (!validation.isValid) {
            this.errors = validation.errors
            return
          }
          // 验证通过，提交数据
          this.isSubmitting = true
          let jsonData = this.form.toJson()
          console.info(`提交注册: ${JSON.stringify(jsonData)}`)
        })
    }
    .padding(20)
  }
}
```
