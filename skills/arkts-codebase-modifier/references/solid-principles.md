# SOLID原则在ArkTS中的应用

## 概述

SOLID原则是面向对象设计的五大基本原则，在ArkTS开发中同样适用。本指南结合ArkTS语言特性和HarmonyOS应用开发模式，详细说明如何在功能修改和扩展中应用SOLID原则。

> **V1 / V2 双版本说明**：项目锁 V2（API 12+），新增代码示例采用 V2 风格（`@ComponentV2 / @Local / @Param / @Once / @Event / @Provider() / @Consumer() / @ObservedV2 / @Trace / AppStorageV2 / PersistenceV2 / @Monitor / @Computed`）；V1 等价（`@Component / @State / @Prop / @Link / @Provide / @Consume / @Observed / @ObjectLink / @StorageLink / @Watch`）仅在分析现有 V1 文件时识别。**修改方案不混用 V1/V2** — 若现文件是 V1 且仅做小扩展，保持 V1；若需引入 V2 特性（如 `@Computed`、`@Trace` 属性级观察），先迁移整个文件。

## S - 单一职责原则（Single Responsibility Principle）

### 原则定义
一个类或组件应该只有一个引起它变化的原因。

### 在ArkTS中的应用

#### 组件职责分离（V2 推荐写法）
```typescript
// ❌ 不好的实践：组件承担过多职责
@ComponentV2
struct BadComponent {
  @Local userData: UserInfo = new UserInfo()
  @Local settings: AppSettings = new AppSettings()
  @Local notificationConfig: NotificationConfig = new NotificationConfig()

  build() {
    // 混合了用户信息展示、设置管理、通知配置等多种职责
    Column() {
      UserInfoDisplay({ userData: this.userData })
      SettingsPanel({ settings: this.settings })
      NotificationConfigView({ config: this.notificationConfig })
    }
  }

  // 组件内包含多种业务逻辑
  handleUserUpdate() { }
  handleSettingsChange() { }
  handleNotificationUpdate() { }
}

// ✅ 好的实践：每个组件职责单一
@ComponentV2
struct UserInfoDisplay {
  @Param @Once userData: UserInfo = new UserInfo()

  build() {
    // 只负责用户信息展示
    Column() {
      Text(this.userData.name)
      Text(this.userData.email)
    }
  }
}

@ComponentV2
struct SettingsPanel {
  @Param @Once settings: AppSettings = new AppSettings()

  build() {
    // 只负责设置面板
    Column() {
      // 设置项
    }
  }
}

@ComponentV2
struct NotificationConfigView {
  @Param @Once config: NotificationConfig = new NotificationConfig()

  build() {
    // 只负责通知配置
    Column() {
      // 配置项
    }
  }
}
```

> 老项目 V1 等价：将 `@ComponentV2` 改回 `@Component`，`@Local` 改 `@State`，`@Param @Once` 改 `@Prop`。修改方案不要在同一个 struct 中混用 V1/V2。

#### 服务层职责分离
```typescript
// ❌ 不好的实践：服务承担多种职责
export class UserService {
  async getUserInfo() { }
  async updateUser() { }
  async sendNotification() { } // 不属于用户服务
  async getSettings() { } // 不属于用户服务
}

// ✅ 好的实践：服务职责单一
export class UserService {
  async getUserInfo() { }
  async updateUser() { }
}

export class NotificationService {
  async sendNotification() { }
}

export class SettingsService {
  async getSettings() { }
}
```

### 功能修改中的应用场景
当功能修改涉及多个职责时，应该：
1. 识别不同的职责
2. 将修改限定在单一职责的组件或服务中
3. 避免在一个组件中添加不相关的功能

## O - 开闭原则（Open/Closed Principle）

### 原则定义
软件实体应该对扩展开放，对修改关闭。

### 在ArkTS中的应用

#### 使用装饰器扩展功能（V2 推荐：用 @Param + @Event 替代回调 prop）
```typescript
// ✅ 好的实践：通过组合扩展，不修改原有代码
@ComponentV2
struct ButtonComponent {
  @Param @Once text: string = ''
  @Event onAction: () => void = () => {}

  build() {
    Button(this.text)
      .onClick(() => {
        this.onAction()
      })
  }
}

// 通过组合扩展功能，不修改ButtonComponent
@ComponentV2
struct PrimaryButton {
  @BuilderParam content: () => void = () => {}

  build() {
    ButtonComponent({
      text: '主要操作',
      onAction: () => {
        // 主要按钮的特定逻辑
      }
    })
  }
}

@ComponentV2
struct SecondaryButton {
  @BuilderParam content: () => void = () => {}

  build() {
    ButtonComponent({
      text: '次要操作',
      onAction: () => {
        // 次要按钮的特定逻辑
      }
    })
  }
}
```

> 老项目 V1 等价：`@ComponentV2 → @Component`、`@Param @Once → @Prop`、`@Event onAction: () => void = () => {}` → `onClick?: () => void`。

#### 使用配置扩展功能（V2 推荐）
```typescript
// ✅ 好的实践：通过配置扩展功能
interface ButtonConfig {
  text: string;
  type: 'primary' | 'secondary' | 'danger';
}

@ComponentV2
struct ConfigurableButton {
  @Param @Once config: ButtonConfig = { text: '', type: 'primary' }
  @Event onTap: () => void = () => {}

  getButtonStyle() {
    switch (this.config.type) {
      case 'primary':
        return { backgroundColor: '#007AFF' }
      case 'secondary':
        return { backgroundColor: '#5856D6' }
      case 'danger':
        return { backgroundColor: '#FF3B30' }
    }
  }

  build() {
    Button(this.config.text)
      .onClick(() => this.onTap())
      .style(this.getButtonStyle())
  }
}
```

#### 使用组合扩展功能（V2 推荐）
```typescript
// ✅ 好的实践：通过组合扩展功能
@ComponentV2
struct Card {
  @BuilderParam content: () => void = () => {}
  @Param @Once title: string = ''

  build() {
    Column() {
      Text(this.title).fontSize(18).fontWeight(FontWeight.Bold)
      this.content()
    }
    .padding(16)
    .backgroundColor('#FFFFFF')
    .borderRadius(8)
  }
}

// 通过组合扩展卡片功能
@ComponentV2
struct UserCard {
  @Local userData: UserInfo = new UserInfo()

  build() {
    Card({ title: '用户信息' }) {
      Column() {
        Text(this.userData.name)
        Text(this.userData.email)
      }
    }
  }
}

@ComponentV2
struct ProductCard {
  @Local productData: ProductInfo = new ProductInfo()

  build() {
    Card({ title: '产品信息' }) {
      Column() {
        Text(this.productData.name)
        Text(this.productData.price)
      }
    }
  }
}
```

### 功能修改中的应用场景
当需要扩展功能时，应该：
1. 优先考虑通过装饰器、配置、组合等方式扩展
2. 避免直接修改现有组件的内部逻辑
3. 创建新的组件或服务来承载新功能

## L - 里氏替换原则（Liskov Substitution Principle）

### 原则定义
子类应该能够替换父类而不影响程序的正确性。

### 在ArkTS中的应用

#### 组件继承的一致性（V2 推荐）
```typescript
// ✅ 好的实践：子类可以安全替换父类
@ComponentV2
export struct BaseList {
  @Local items: Array<string> = []
  @Event onItemClick: (item: string) => void = () => {}

  build() {
    List() {
      ForEach(this.items, (item: string, index: number) => {
        ListItem() {
          Text(item)
        }
        .onClick(() => {
          this.onItemClick(item)
        })
      })
    }
  }
}

// 子类可以安全替换父类
@ComponentV2
export struct CustomList extends BaseList {
  @Local customItems: Array<string> = []

  build() {
    Column() {
      super.build()
      // 添加自定义元素
      Text('自定义元素')
    }
  }
}
```

#### 接口实现的一致性
```typescript
// ✅ 好的实践：接口实现保持一致
interface DataService {
  getData(): Promise<any>;
  saveData(data: any): Promise<void>;
}

export class LocalDataService implements DataService {
  async getData(): Promise<any> {
    // 本地数据获取
  }

  async saveData(data: any): Promise<void> {
    // 本地数据保存
  }
}

export class RemoteDataService implements DataService {
  async getData(): Promise<any> {
    // 远程数据获取
  }

  async saveData(data: any): Promise<void> {
    // 远程数据保存
  }
}

// 两个实现可以安全替换使用
@ComponentV2
struct DataDisplay {
  @Local dataService: DataService = new LocalDataService()

  build() {
    Column() {
      Button('加载数据').onClick(async () => {
        const data = await this.dataService.getData()
        // 使用数据
      })
    }
  }
}
```

### 功能修改中的应用场景
当涉及继承和接口实现时，应该：
1. 确保子类行为与父类一致
2. 避免在子类中改变父类的核心行为
3. 保证接口实现的统一性

## I - 接口隔离原则（Interface Segregation Principle）

### 原则定义
客户端不应该依赖它不需要的接口。

### 在ArkTS中的应用

#### 避免臃肿的接口
```typescript
// ❌ 不好的实践：接口包含过多方法
interface SuperInterface {
  methodA(): void;
  methodB(): void;
  methodC(): void;
  methodD(): void;
  methodE(): void;
}

// ✅ 好的实践：接口职责单一
interface FeatureA {
  methodA(): void;
}

interface FeatureB {
  methodB(): void;
}

interface FeatureC {
  methodC(): void;
}

// 组件只依赖需要的接口（V2 推荐）
@ComponentV2
struct ComponentA {
  @Param @Once featureA: FeatureA = { methodA: () => {} }

  build() {
    Column() {
      Button('调用方法A').onClick(() => {
        this.featureA.methodA()
      })
    }
  }
}
```

#### 组件属性分离（V2 推荐）
```typescript
// ❌ 不好的实践：组件属性混合
@ComponentV2
struct ComplexComponent {
  @Param @Once title: string = ''
  @Param @Once description: string = ''
  @Param @Once data: object = {}
  @Event onTap: () => void = () => {}
  @Event onLong: () => void = () => {}
  @Param @Once backgroundColor: string = ''
  @Param @Once textColor: string = ''
  build() { /* 组件实现 */ }
}

// ✅ 好的实践：组件属性分离
interface BaseProps {
  title: string;
  description: string;
}

interface DataProps {
  data: object;
}

@ComponentV2
struct SimpleComponent {
  // 只依赖需要的属性接口
  @Param @Once baseProps: BaseProps = { title: '', description: '' }
  @Event onTap: () => void = () => {}

  build() {
    Column() {
      Text(this.baseProps.title)
      Text(this.baseProps.description)
    }
    .onClick(() => this.onTap())
  }
}
```

### 功能修改中的应用场景
当设计接口和组件属性时，应该：
1. 将大接口拆分为小接口
2. 组件只依赖需要的接口
3. 避免强制组件实现不需要的方法

## D - 依赖倒置原则（Dependency Inversion Principle）

### 原则定义
高层模块不应该依赖低层模块，两者都应该依赖抽象。

### 在ArkTS中的应用

#### 依赖抽象而非具体实现（V2 推荐）
```typescript
// ❌ 不好的实践：依赖具体实现
@ComponentV2
struct UserDataDisplay {
  @Local userData: UserInfo = new UserInfo()
  // 依赖具体的LocalDataService
  private dataService = new LocalDataService()

  async aboutToAppear() {
    this.userData = await this.dataService.getUserInfo()
  }

  build() {
    Text(this.userData.name)
  }
}

// ✅ 好的实践：依赖抽象
interface DataService {
  getUserInfo(): Promise<UserInfo>;
}

@ComponentV2
struct UserDataDisplay2 {
  @Local userData: UserInfo = new UserInfo()
  // 依赖抽象接口
  @Param @Once dataService: DataService = new LocalDataService()

  async aboutToAppear() {
    this.userData = await this.dataService.getUserInfo()
  }

  build() {
    Text(this.userData.name)
  }
}
```

#### 使用依赖注入（V2 推荐）
```typescript
// ✅ 好的实践：使用依赖注入
interface NetworkService {
  request(url: string): Promise<object>;
}

@ComponentV2
struct ApiDataDisplay {
  @Param @Once networkService: NetworkService = new HttpNetworkService()
  @Local data: object = {}

  async loadData() {
    this.data = await this.networkService.request('https://api.example.com')
  }

  build() {
    Button('加载数据').onClick(() => {
      this.loadData()
    })
  }
}

// 在上层注入具体实现
@ComponentV2
struct App {
  build() {
    // 可以灵活注入不同的实现
    ApiDataDisplay({
      networkService: new HttpNetworkService()
    })
  }
}
```

### 功能修改中的应用场景
当设计模块依赖关系时，应该：
1. 定义抽象接口
2. 高层模块和低层模块都依赖抽象
3. 通过依赖注入灵活切换实现

## 功能修改中的SOLID原则综合应用

### 示例场景：给列表项增加长按删除功能

#### 原有代码（V2 风格）
```typescript
@ComponentV2
struct ItemList {
  @Local items: Array<string> = []

  build() {
    List() {
      ForEach(this.items, (item: string) => {
        ListItem() {
          Text(item)
        }
        .onClick(() => {
          // 点击处理
        })
      })
    }
  }
}
```

#### 应用SOLID原则的修改方案

**1. 单一职责原则（S）**
- 将列表组件的职责限制为数据展示
- 删除逻辑放到独立的处理器中

**2. 开闭原则（O）**
- 通过添加事件处理扩展功能，不修改核心列表逻辑
- 使用装饰器模式增强列表项

**3. 里氏替换原则（L）**
- 保持列表组件的核心行为不变
- 新增的事件处理不影响原有功能

**4. 接口隔离原则（I）**
- 定义细粒度的事件接口
- 组件只依赖需要的事件接口

**5. 依赖倒置原则（D）**
- 定义抽象的删除处理器接口
- 组件依赖抽象而非具体实现

#### 修改后的代码（V2 推荐）
```typescript
// 定义抽象接口
interface ItemEventHandler {
  onClick?(item: string): void;
  onLongPress?(item: string): void;
}

// 具体实现
class DefaultItemHandler implements ItemEventHandler {
  onClick(item: string): void {
    console.log('点击了:', item)
  }
}

class DeleteItemHandler implements ItemEventHandler {
  onLongPress(item: string): void {
    console.log('长按删除:', item)
  }
}

// 组件依赖抽象
@ComponentV2
struct ItemList {
  @Local items: Array<string> = []
  @Param @Once eventHandler: ItemEventHandler = new DefaultItemHandler()

  build() {
    List() {
      ForEach(this.items, (item: string) => {
        ListItem() {
          Text(item)
        }
        .onClick(() => {
          this.eventHandler.onClick?.(item)
        })
        .onLongPress(() => {
          this.eventHandler.onLongPress?.(item)
        })
      })
    }
  }
}

// 使用时注入具体实现
@ComponentV2
struct App {
  @Local items: Array<string> = ['item1', 'item2', 'item3']

  build() {
    Column() {
      ItemList({
        items: this.items,
        eventHandler: {
          onClick: (item) => {
            console.log('点击了:', item)
          },
          onLongPress: (item) => {
            console.log('长按删除:', item)
            // 删除逻辑
          }
        }
      })
    }
  }
}
```

> 老项目 V1 等价：`@ComponentV2 → @Component`、`@Local → @State`、`@Param @Once → @Prop`。修改方案要么整个 V1，要么整个 V2，**不要混用**。

## 总结

在ArkTS功能修改中应用SOLID原则可以：

1. **提高代码可维护性**：每个组件和服务的职责清晰
2. **增强可扩展性**：通过扩展而非修改实现新功能
3. **降低耦合度**：模块间依赖抽象而非具体实现
4. **提高代码复用性**：细粒度的接口和组件更易于复用
5. **便于单元测试**：依赖抽象使测试更容易

在实际开发中，应该根据具体场景灵活应用这些原则，避免过度设计。
