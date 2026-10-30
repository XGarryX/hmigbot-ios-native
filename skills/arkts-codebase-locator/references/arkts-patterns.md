# ArkTS语言模式与最佳实践

## 概述

本文档详细介绍ArkTS语言的编程模式、代码特征和最佳实践，为HarmonyOS功能定位技能提供代码识别和分析的基础。通过理解这些模式，可以快速识别和理解ArkTS代码的结构和功能。

> **V1 / V2 双版本说明**：本项目锁 V2（API 12+），目标代码示例使用 V2 装饰器。但代码仓中可能既存在 V1（`@Component / @State / @Prop / @Link / @Observed / @ObjectLink / @StorageLink / @Watch` 等）也存在 V2（`@ComponentV2 / @Local / @Param / @Once / @Event / @Provider() / @Consumer() / @ObservedV2 / @Trace / AppStorageV2 / PersistenceV2 / @Monitor / @Computed`）。**定位时一律使用 V1+V2 兼容 grep 模式**（如 `@Component(V2)?\b`、`@State|@Local`、`@StorageLink|AppStorageV2`），避免漏检。

## ArkTS语言核心特性

ArkTS是一种设计用于构建高性能应用的编程语言，它在继承TypeScript语法的基础上进行了优化，以提供更高的性能和开发效率。作为HarmonyOS的主力应用开发语言，ArkTS具有以下核心特性：

- **静态类型系统**：强制使用静态类型，在程序运行前确定变量类型，不允许在执行期间更改对象布局
- **TypeScript超集**：保持TypeScript的大部分语法，为TypeScript开发者提供高度兼容的体验
- **声明式UI**：专注于声明式UI能力，以简洁、自然的方式开发高性能应用
- **低运行时开销**：专注于低运行时开销，提供更好的性能
- **严格静态检查**：编译期静态检查与分析机制，提升程序稳定性
- **分布式支持**：提供特定的语法和API简化分布式开发

## ArkTS与TypeScript的区别

**继承与扩展：**
- **超集关系**：ArkTS是TypeScript的超集，继承了TS的所有特性
- **语法兼容**：基本兼容TS语法，帮助开发者更容易上手
- **扩展特性**：主要扩展了声明式UI能力

**关键差异：**

| 特性 | TypeScript | ArkTS |
|------|------------|-------|
| 生态系统 | 庞大的npm生态，跨平台兼容性强 | 深度集成HarmonyOS系统，专注分布式场景 |
| 静态检查 | 支持静态类型检查 | 更严格的静态类型检查，禁止使用any类型 |
| 分布式支持 | 不支持原生分布式特性 | 提供特定的语法和API简化分布式开发 |
| 性能 | 类型检查可能导致性能损失 | 优化性能，低运行时开销 |
| 用途 | 通用前端/后端开发 | 专门针对HarmonyOS应用开发 |

## ArkTS核心语法模式

### 1. 装饰器模式

#### 1.1 @Entry装饰器
**功能**：标记应用入口页面（V1/V2 通用）
**定位特征**：页面级别的入口点
**使用场景**：应用主页面、功能入口页面

```arkts
// V2 推荐写法（项目锁 V2，本风格作为目标代码示例）
@Entry
@ComponentV2
struct Index {
  build() {
    // 页面构建逻辑
  }
}
```

```arkts
// V1 等价写法（仅老代码可能存在；定位时请同时识别）
@Entry
@Component
struct Index {
  build() { /* ... */ }
}
```

**定位策略**：
- 搜索路径：`**/pages/*.ets`
- 识别模式：`@Entry` + `@Component(V2)?\b`（V1+V2 兼容 grep）
- 相关文件：页面导航配置、路由设置

#### 1.2 @Component / @ComponentV2装饰器
**功能**：标记可复用组件
**定位特征**：UI组件定义
**使用场景**：按钮、输入框、弹窗等可复用UI

```arkts
// V2 推荐写法（项目目标风格）
@ComponentV2
struct MyButton {
  @Param @Once text: string = ''
  @Event onAction: () => void = () => {}

  build() {
    Button(this.text)
      .onClick(() => this.onAction())
  }
}
```

```arkts
// V1 等价写法（老项目可能存在）
@Component
struct MyButton {
  @Prop text: string;
  onClick: () => void;
  build() {
    Button(this.text).onClick(this.onClick)
  }
}
```

**定位策略**：
- 搜索路径：`**/components/*.ets`
- 识别模式（V1+V2 兼容）：独立的 `@Component(V2)?\b` 装饰器
- 相关文件：组件使用页面、样式文件

#### 1.3 @State / @Local装饰器（组件内部状态）
**功能**：声明组件内部状态变量
**定位特征**：响应式数据管理
**使用场景**：页面状态、组件状态

```arkts
// V2 推荐写法
@ComponentV2
struct UserProfile {
  @Local userInfo: UserInfo = new UserInfo()
  @Local isLoading: boolean = false

  build() {
    if (this.isLoading) {
      LoadingProgress()
    } else {
      Text(this.userInfo.name)
    }
  }
}
```

```arkts
// V1 等价写法
@Component
struct UserProfile {
  @State userInfo: UserInfo = new UserInfo();
  @State isLoading: boolean = false;
  build() { /* ... */ }
}
```

**定位策略**：
- 搜索模式（V1+V2 兼容）：`@State|@Local` 变量声明
- 识别特征：响应式数据更新触发UI刷新
- 相关文件：状态初始化、数据更新逻辑

#### 1.4 @Observed / @ObservedV2装饰器
**功能**：标记可观察类
**定位特征**：跨组件数据同步
**使用场景**：全局状态、共享数据

```arkts
// V2 推荐写法（属性级精确观察，需在每个可观察属性上加 @Trace）
@ObservedV2
class UserStore {
  @Trace userInfo: UserInfo = new UserInfo()
  @Trace preferences: UserPreferences = new UserPreferences()
}
```

```arkts
// V1 等价写法（粒度较粗，整个第一层属性都被观察）
@Observed
class UserStore {
  userInfo: UserInfo;
  preferences: UserPreferences;
}
```

**定位策略**：
- 搜索模式（V1+V2 兼容）：`@Observed(V2)?\b` 类定义；V2 项目还应搜索 `@Trace` 标记
- 识别特征：跨组件数据同步
- 相关文件：状态管理器、数据更新方法

#### 1.5 @Styles装饰器
**功能**：定义组件重用样式
**定位特征**：样式复用和主题管理
**使用场景**：UI样式定义和主题切换

```arkts
// V2 写法（@Styles / @Extend / @Builder 在 V1/V2 通用，仅 struct 装饰器更换）
@Styles
function commonButton() {
  .width(200)
  .height(50)
  .backgroundColor('#007DFF')
  .borderRadius(8)
  .fontSize(16)
  .fontColor(Color.White)
}

@ComponentV2
struct MyButton {
  @Param @Once text: string = ''

  build() {
    Button(this.text)
      .apply(commonButton())
      .onClick(() => {
        // 按钮点击逻辑
      })
  }
}
```

**定位策略**：
- 搜索模式：`@Styles`函数定义
- 识别特征：样式复用函数
- 相关文件：主题文件，样式配置

#### 1.6 @Type装饰器
**功能**：标记类属性的类型
**定位特征**：序列化类型标记
**使用场景**：数据持久化和跨语言调用

```arkts
// V2 推荐：@Type 通用，@Observed 升级为 @ObservedV2，类成员改用 @Trace
@ObservedV2
class UserProfile {
  @Type(UserInfo)
  @Trace userInfo: UserInfo = new UserInfo()

  @Type(UserPreferences)
  @Trace preferences: UserPreferences = new UserPreferences()
}
```

**定位策略**：
- 搜索模式：`@Type`装饰器使用
- 识别特征：序列化类型标记
- 相关文件：数据模型，持久化配置

#### 1.7 @Builder装饰器
**功能**：修饰函数用于动态构建UI元素
**定位特征**：UI构建函数
**使用场景**：动态UI生成和组件复用

```arkts
// V2 写法（@Builder 在 V1/V2 通用）
@ComponentV2
struct UserProfile {
  @Local userInfo: UserInfo = new UserInfo()

  @Builder
  UserInfoItem(label: string, value: string) {
    Row() {
      Text(label)
        .fontColor('#666666')
        .fontSize(14)

      Text(value)
        .fontColor('#333333')
        .fontSize(16)
        .layoutWeight(1)
    }
    .padding(16)
    .backgroundColor('#F5F5F5')
    .borderRadius(8)
  }

  build() {
    Column() {
      this.UserInfoItem('用户名', this.userInfo.username)
      this.UserInfoItem('邮箱', this.userInfo.email)
    }
  }
}
```

**定位策略**：
- 搜索模式：`@Builder`函数定义
- 识别特征：UI构建函数
- 相关文件：动态UI组件，模板文件

### 2. 生命周期模式

#### 2.1 页面生命周期
**功能**：页面级别的生命周期管理
**定位特征**：页面状态变化处理
**使用场景**：页面初始化、资源管理

```arkts
// V2 写法（生命周期方法名 V1/V2 通用）
@Entry
@ComponentV2
struct MyPage {
  aboutToAppear() {
    // 页面即将出现时调用
    // 适合初始化数据、注册监听器
  }

  aboutToDisappear() {
    // 页面即将消失时调用
    // 适合清理资源、移除监听器
  }

  onShow() {
    // 页面显示时调用
  }

  onHide() {
    // 页面隐藏时调用
  }
}
```

**定位策略**：
- 搜索模式：生命周期方法名称
- 识别特征：`@Entry`组件中的生命周期方法
- 相关文件：页面初始化逻辑、资源管理

#### 2.2 组件生命周期
**功能**：组件级别的生命周期管理
**定位特征**：组件状态变化处理
**使用场景**：组件初始化、资源清理

```arkts
// V2 写法
@ComponentV2
struct MyComponent {
  aboutToAppear() {
    // 组件即将出现时调用
  }

  aboutToDisappear() {
    // 组件即将消失时调用
  }
}
```

**定位策略**：
- 搜索模式：组件中的生命周期方法
- 识别特征（V1+V2 兼容）：`@Component(V2)?\b` 装饰的组件
- 相关文件：组件使用页面、父组件逻辑

### 3. 导航与路由模式

#### 3.1 页面导航
**功能**：页面间跳转逻辑
**定位特征**：路由调用和方法
**使用场景**：页面跳转、参数传递

```arkts
// V2 写法
import router from '@ohos.router';

@ComponentV2
struct LoginPage {
  @Local username: string = ''

  build() {
    Column() {
      TextInput({ placeholder: '用户名' })
        .onChange(value => this.username = value)

      Button('登录')
        .onClick(() => {
          // 页面跳转逻辑
          router.pushUrl({
            url: 'pages/HomePage',
            params: {
              username: this.username
            }
          })
        })
    }
  }
}
```

**定位策略**：
- 搜索模式：`router.pushUrl()`, `router.back()`, `router.replaceUrl()`
- 识别特征：页面跳转方法调用
- 相关文件：路由配置、目标页面

#### 3.2 参数传递
**功能**：页面间参数传递
**定位特征**：参数接收和处理
**使用场景**：数据共享、状态传递

```arkts
// V2 写法
@ComponentV2
struct HomePage {
  @Local username: string = ''

  aboutToAppear() {
    // 接收传递的参数
    const params = router.getParams();
    if (params && params.username) {
      this.username = params.username;
    }
  }

  build() {
    Text(`欢迎, ${this.username}`)
  }
}
```

**定位策略**：
- 搜索模式：`router.getParams()`, `router.params`
- 识别特征：参数获取和处理逻辑
- 相关文件：参数发送页面、数据处理

### 4. 数据绑定与事件处理模式

#### 4.1 双向数据绑定
**功能**：数据与UI的双向同步
**定位特征**：数据变化自动更新UI
**使用场景**：表单输入、状态同步

```arkts
// V2 写法（@Form 在 V2 通用；状态用 @Local）
@ComponentV2
struct FormPage {
  @Local formData: {
    username: string,
    email: string,
    agreed: boolean
  } = {
    username: '',
    email: '',
    agreed: false
  }

  build() {
    Column() {
      TextInput({ placeholder: '用户名' })
        .onChange(value => this.formData.username = value)

      TextInput({ placeholder: '邮箱' })
        .onChange(value => this.formData.email = value)

      Toggle('同意条款')
        .onChange(isChecked => this.formData.agreed = isChecked)

      Button('提交')
        .onClick(() => this.submitForm())
    }
  }

  private submitForm() {
    // 表单提交逻辑
  }
}
```

**定位策略**：
- 搜索模式：`@Form`装饰器，`.onChange()`方法
- 识别特征：数据变化与UI同步
- 相关文件：数据验证、提交逻辑

#### 4.2 事件处理
**功能**：用户交互事件处理
**定位特征**：事件监听和回调
**使用场景**：按钮点击、表单提交

```arkts
// V2 写法
@ComponentV2
struct InteractiveComponent {
  @Local count: number = 0

  build() {
    Column() {
      Button('点击')
        .onClick(() => {
          this.count++
          this.handleClick()
        })
        .onTouch(() => {
          // 触摸事件处理
        })

      Text(`点击次数: ${this.count}`)
    }
  }

  private handleClick() {
    // 点击事件处理逻辑
  }
}
```

**定位策略**：
- 搜索模式：`.onClick()`, `.onTouch()`, `.onLongPress()`
- 识别特征：事件监听器绑定
- 相关文件：事件处理方法、状态更新

## 状态管理模式

### 1. AppStorage / AppStorageV2 全局状态
**功能**：应用级别的全局状态管理
**定位特征**：全局数据访问和更新
**使用场景**：用户信息、应用配置

```arkts
// V2 推荐：AppStorageV2.connect + @ObservedV2 类
@ObservedV2
class UserModel {
  @Trace username: string = 'default'
  @Trace avatar: string = ''
}

// 任意 @ComponentV2 中：
// @Local user: UserModel = AppStorageV2.connect(UserModel, 'userInfo', () => new UserModel())!
```

```arkts
// V1 等价写法（老项目可能仍在用）
import AppStorage from '@ohos.appStorage';

const globalStorage = AppStorage.create();
globalStorage.setOrCreate('userInfo', {
  username: 'default',
  avatar: '',
  preferences: {}
});
const userInfo = globalStorage.get('userInfo');
```

**定位策略（V1+V2 兼容）**：
- 搜索模式：`AppStorage.create()|AppStorage.get()|AppStorage.set(OrCreate)?|AppStorageV2.connect`
- 识别特征：全局状态管理操作
- 相关文件：状态初始化、状态更新方法

### 2. LocalStorage本地存储
**功能**：本地数据持久化
**定位特征**：本地数据读写
**使用场景**：用户偏好设置、缓存数据

```arkts
// V1/V2 通用：Preferences API（不带响应性，需配合状态层）
import preferences from '@ohos.data.preferences';

const store = await preferences.getPreferences(getContext(), 'user_preferences');
await store.put('theme', 'dark');
await store.flush(); // 立即写入磁盘
const theme = await store.get('theme', 'light');
```

```arkts
// V2 推荐：需要"持久化 + UI 实时刷新"时优先 PersistenceV2.globalConnect
@ObservedV2
class Config {
  @Trace theme: string = 'light'
}
// @Local config: Config = PersistenceV2.globalConnect({ type: Config, key: 'config', defaultCreator: () => new Config() })!
```

**定位策略（V1+V2 兼容）**：
- 搜索模式：`preferences.getPreferences()|.put|.get|PersistenceV2.globalConnect`
- 识别特征：本地/持久化存储操作
- 相关文件：存储初始化、数据读写逻辑

### 3. ArkTS状态管理机制详解

#### 3.1 状态管理核心概念
**功能**：状态驱动UI更新的机制
**定位特征**：装饰器标记的状态变量
**使用场景**：响应式UI和数据绑定

ArkTS状态管理核心概念：
- **状态驱动**：状态是指驱动视图更新的数据（被装饰器标记的变量）
- **视图更新**：视图是指UI描述渲染得到的用户页面
- **响应式机制**：通过装饰器实现响应式数据绑定

#### 3.2 状态装饰器生命周期

**@State / @Local 装饰器（组件内状态）**：
- **功能**：组件内状态变量装饰器
- **特征**：使普通变量具备状态属性，状态变量改变时触发UI组件渲染更新
- **使用场景**：组件内部状态管理
- **V1+V2 grep 模式**：`@State|@Local`

```arkts
// V2 推荐写法
@ComponentV2
struct UserProfile {
  @Local userInfo: UserInfo = new UserInfo()
  @Local isLoading: boolean = false
  @Local error: string | null = null

  build() {
    if (this.isLoading) {
      LoadingProgress()
    } else if (this.error) {
      Text(this.error)
        .fontColor(Color.Red)
    } else {
      Text(this.userInfo.name)
        .fontSize(20)
    }
  }
}
```

```arkts
// V1 等价写法
@Component
struct UserProfile {
  @State userInfo: UserInfo = new UserInfo();
  @State isLoading: boolean = false;
  @State error: string | null = null;
  build() { /* ... */ }
}
```

**@Prop / @Param 装饰器（父→子单向）**：
- **功能**：父组件向子组件传递数据
- **特征**：V2 中 `@Param` 必须给默认值；只读用 `@Param + @Once`，可写本地副本省略 `@Once`
- **使用场景**：父子组件数据传递
- **V1+V2 grep 模式**：`@Prop|@Param`

```arkts
// V2 推荐写法
@ComponentV2
struct UserProfileCard {
  @Param @Once userInfo: UserInfo = new UserInfo()  // 只读

  build() {
    Column() {
      Text(this.userInfo.name).fontSize(18)
      Text(this.userInfo.email).fontSize(14).fontColor('#666666')
    }
  }
}

@ComponentV2
struct UserProfilePage {
  @Local currentUser: UserInfo = new UserInfo()

  build() {
    Column() {
      UserProfileCard({ userInfo: this.currentUser })

      Button('更新信息')
        .onClick(() => {
          this.currentUser.name = '新用户名'
        })
    }
  }
}
```

```arkts
// V1 等价写法
@Component
struct UserProfileCard {
  @Prop userInfo: UserInfo;
  build() { /* ... */ }
}
```

**@Link 装饰器（V1）／ @Param + @Event 模式（V2 等价）**：
- **功能**：父子组件之间的双向同步
- **V2 重要变化**：V2 没有 `@Link`，改用 `@Param`（只接收）+ `@Event`（子→父回调）替代
- **使用场景**：需要双向数据绑定的场景
- **V1+V2 grep 模式**：`@Link|@Event`

```arkts
// V2 推荐：@Param + @Event 回调
@ComponentV2
struct CounterComponent {
  @Param count: number = 0
  @Event onCountChange: (v: number) => void = () => {}

  build() {
    Row() {
      Text(`计数: ${this.count}`)
      Button('+')
        .onClick(() => {
          this.onCountChange(this.count + 1)  // 通过事件回调通知父组件
        })
    }
  }
}

@ComponentV2
struct CounterPage {
  @Local total: number = 0

  build() {
    Column() {
      CounterComponent({
        count: this.total,
        onCountChange: (v: number) => { this.total = v }
      })
      Text(`总计: ${this.total}`)
    }
  }
}
```

```arkts
// V1 等价写法（@Link 双向绑定，已被 V2 弃用）
@Component
struct CounterComponent {
  @Link count: number;
  build() {
    Row() {
      Text(`计数: ${this.count}`)
      Button('+').onClick(() => { this.count++ })
    }
  }
}

@Component
struct CounterPage {
  @State total: number = 0;
  build() {
    Column() {
      CounterComponent({ count: $total })
    }
  }
}
```

**@Observed / @ObservedV2 装饰器**：
- **功能**：标记可观察类
- **V2 重要变化**：V2 用 `@ObservedV2` + 类属性 `@Trace` 实现属性级精确观察；V1 是默认观察整个第一层
- **使用场景**：复杂对象状态管理
- **V1+V2 grep 模式**：`@Observed(V2)?\b`，V2 还需搜 `@Trace`

```arkts
// V2 推荐
@ObservedV2
class Address {
  @Trace city: string = ''
  @Trace street: string = ''
}

@ObservedV2
class User {
  @Trace name: string = ''
  @Trace address: Address = new Address()
}

@ComponentV2
struct UserDetail {
  @Param user: User = new User()  // V2 直接 @Param 持有，无需 @ObjectLink

  build() {
    Column() {
      Text(this.user.name)
      Text(`${this.user.address.city} - ${this.user.address.street}`)
    }
  }
}
```

```arkts
// V1 等价
@Observed
class User {
  name: string;
  @Type(Address)
  address: Address;
}

@Component
struct UserDetail {
  @ObjectLink user: User;
  build() { /* ... */ }
}
```

#### 3.3 状态管理最佳实践

**规范化的状态管理**：
**功能**：集中式状态管理
**定位特征**：单例模式，状态管理类
**使用场景**：复杂应用的状态管理

```arkts
// V2 推荐：用 @ObservedV2 类承载所有状态，AppStorageV2.connect 提供全局共享
@ObservedV2
class AppState {
  @Trace currentUser: User | null = null
  @Trace isAuthenticated: boolean = false
  @Trace theme: Theme = Theme.Light
  @Trace language: string = 'zh-CN'

  async login(user: User): Promise<void> {
    this.currentUser = user
    this.isAuthenticated = true
    // V2 token 持久化推荐 PersistenceV2 而非裸 AppStorage
  }

  async logout(): Promise<void> {
    this.currentUser = null
    this.isAuthenticated = false
  }

  updateTheme(theme: Theme): void {
    this.theme = theme
  }
}

// 任意 @ComponentV2 中：
// @Local appState: AppState = AppStorageV2.connect(AppState, 'appState', () => new AppState())!
```

```arkts
// V1 历史写法（老项目可能仍在用，定位时一并识别）
import AppStorage from '@ohos.appStorage';

class AppStore {
  private static instance: AppStore;
  private storage: AppStorage;

  @State currentUser: User | null = null;
  @State isAuthenticated: boolean = false;
  @State theme: Theme = Theme.Light;

  // 旧式：AppStorage.create + .set/.get
  static getInstance(): AppStore {
    if (!AppStore.instance) {
      AppStore.instance = new AppStore();
    }
    return AppStore.instance;
  }
}
```

**定位策略**：
- 搜索模式：单例模式，状态管理类
- 识别特征：集中状态管理
- 相关文件：状态初始化、状态更新方法

## 网络请求与API调用模式

### 1. HTTP请求模式
**功能**：网络请求和数据获取
**定位特征**：HTTP调用和数据处理
**使用场景**：API调用、数据同步

```arkts
import http from '@ohos.net.http';

class ApiService {
  private baseURL: string = 'https://api.example.com';
  private httpClient: http.HttpRequest | null = null;
  
  constructor() {
    // 初始化HTTP客户端
    this.httpClient = http.createHttp();
  }
  
  async login(username: string, password: string): Promise<ApiResponse> {
    try {
      if (!this.httpClient) {
        throw new Error('HTTP client not initialized');
      }
      
      const response = await this.httpClient.request(
        `${this.baseURL}/auth/login`,
        {
          method: http.RequestMethod.POST,
          header: {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
          },
          extraData: {
            username: username,
            password: password
          }
        }
      );
      
      // 处理响应
      const result = response.result as string;
      const responseData = JSON.parse(result);
      
      if (responseData.code === 200) {
        return responseData;
      } else {
        throw new Error(`Login failed: ${responseData.message}`);
      }
    } catch (error) {
      console.error('Login error:', error);
      throw new Error(`Login failed: ${error.message}`);
    } finally {
      // 确保连接关闭
      if (this.httpClient) {
        this.httpClient.destroy();
      }
    }
  }
  
  async getUserProfile(userId: string): Promise<UserProfile> {
    try {
      if (!this.httpClient) {
        throw new Error('HTTP client not initialized');
      }
      
      const response = await this.httpClient.request(
        `${this.baseURL}/users/${userId}`,
        {
          method: http.RequestMethod.GET,
          header: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${this.getAuthToken()}`,
            'Accept': 'application/json'
          }
        }
      );
      
      const result = response.result as string;
      return JSON.parse(result) as UserProfile;
    } catch (error) {
      console.error('Get user profile error:', error);
      throw new Error(`Get profile failed: ${error.message}`);
    }
  }
  
  private getAuthToken(): string {
    // 从AppStorage获取认证token
    return AppStorage.get('authToken') || '';
  }
  
  // 批量请求处理
  async batchRequest(requests: ApiRequest[]): Promise<ApiResponse[]> {
    const promises = requests.map(request => this.executeRequest(request));
    return Promise.all(promises);
  }
  
  private async executeRequest(request: ApiRequest): Promise<ApiResponse> {
    // 实现单个请求逻辑
    return {} as ApiResponse;
  }
}
```

**定位策略**：
- 搜索模式：`http.createHttp()`, `.request()`, HTTP方法调用
- 识别特征：网络请求API调用
- 相关文件：API配置、数据处理逻辑

### 2. 错误处理模式
**功能**：网络请求错误处理
**定位特征**：异常捕获和处理
**使用场景**：网络异常、业务错误

```arkts
class SafeApiService {
  async safeRequest(requestFn: () => Promise<any>): Promise<any> {
    try {
      return await requestFn();
    } catch (error) {
      this.handleError(error);
      throw error;
    }
  }
  
  private handleError(error: Error): void {
    console.error('API Error:', error.message);
    
    // 根据错误类型处理
    if (error instanceof NetworkError) {
      // 网络错误处理
    } else if (error instanceof AuthenticationError) {
      // 认证错误处理
    } else {
      // 其他错误处理
    }
  }
  
  async loginWithRetry(username: string, password: string): Promise<ApiResponse> {
    return this.safeRequest(async () => {
      const apiService = new ApiService();
      return await apiService.login(username, password);
    });
  }
}
```

**定位策略**：
- 搜索模式：`try-catch`，错误处理逻辑
- 识别特征：异常捕获和处理
- 相关文件：错误类型定义，错误处理方法

## 权限管理模式

### 1. 权限申请模式
**功能**：系统权限申请
**定位特征**：权限请求和处理
**使用场景**：相机、位置、存储等权限

```arkts
import abilityAccessCtrl from '@ohos.abilityAccessCtrl';
import common from '@ohos.app.ability.common';

class PermissionManager {
  async requestPermissions(context: Context): Promise<void> {
    const atManager = abilityAccessCtrl.createAtManager();
    
    // 需要申请的权限列表
    const permissions = [
      'ohos.permission.CAMERA',
      'ohos.permission.LOCATION',
      'ohos.permission.READ_EXTERNAL_STORAGE'
    ];
    
    try {
      // 申请权限
      const requestResult = await atManager.requestPermissionsFromUser(context, permissions);
      
      // 检查授权结果
      for (const permission of permissions) {
        const result = requestResult.authResults[permission];
        if (result !== abilityAccessCtrl.GrantStatus.PERMISSION_GRANTED) {
          console.error(`Permission ${permission} denied`);
        }
      }
    } catch (error) {
      console.error('Permission request failed:', error);
    }
  }
  
  checkPermissionStatus(permission: string): boolean {
    // 检查权限状态
    return true; // 实际实现中检查权限状态
  }
}
```

**定位策略**：
- 搜索模式：`requestPermissionsFromUser()`, 权限常量
- 识别特征：权限申请逻辑
- 相关文件：权限配置，权限检查方法

### 2. 运行时权限处理
**功能**：运行时权限管理
**定位特征**：动态权限处理
**使用场景**：需要时申请权限

```arkts
@Component
struct CameraComponent {
  @State hasCameraPermission: boolean = false;
  private context: Context = getContext(this) as Context;
  
  async aboutToAppear() {
    await this.checkAndRequestPermission();
  }
  
  private async checkAndRequestPermission(): Promise<void> {
    const permissionManager = new PermissionManager();
    this.hasCameraPermission = permissionManager.checkPermissionStatus('ohos.permission.CAMERA');
    
    if (!this.hasCameraPermission) {
      await permissionManager.requestPermissions(this.context);
      this.hasCameraPermission = permissionManager.checkPermissionStatus('ohos.permission.CAMERA');
    }
  }
  
  build() {
    Column() {
      if (this.hasCameraPermission) {
        Camera()
          .onError(() => {
            // 相机错误处理
          })
      } else {
        Text('需要相机权限')
          .onClick(() => this.checkAndRequestPermission())
      }
    }
  }
}
```

**定位策略**：
- 搜索模式：权限状态检查，权限申请触发
- 识别特征：权限相关的UI逻辑
- 相关文件：权限管理器，权限UI组件

## 性能优化模式

### 1. 懒加载模式
**功能**：延迟加载资源
**定位特征**：按需加载逻辑
**使用场景**：大列表、复杂组件

```arkts
@Component
struct LazyListComponent {
  @State private items: Item[] = [];
  @State private isLoading: boolean = false;
  
  private loadMoreCallback: AsyncCallback<void> = async () => {
    if (this.isLoading) return;
    
    this.isLoading = true;
    try {
      const newItems = await this.loadMoreItems();
      this.items = [...this.items, ...newItems];
    } finally {
      this.isLoading = false;
    }
  };
  
  private async loadMoreItems(): Promise<Item[]> {
    // 模拟网络请求
    await new Promise(resolve => setTimeout(resolve, 1000));
    return Array(20).fill(0).map((_, i) => ({
      id: this.items.length + i,
      name: `Item ${this.items.length + i}`
    }));
  }
  
  build() {
    Column() {
      List() {
        ForEach(this.items, (item: Item) => {
          ListItem() {
            Text(item.name)
              .width('100%')
              .height(50)
              .textAlign(TextAlign.Center)
          }
        })
        .onReachEnd(this.loadMoreCallback)
      }
      .listDirection(Axis.Vertical)
      .divider({ strokeWidth: 1, color: '#cccccc' })
      
      if (this.isLoading) {
        LoadingProgress()
          .width(30)
          .height(30)
      }
    }
  }
}
```

**定位策略**：
- 搜索模式：`onReachEnd()`, 懒加载回调
- 识别特征：按需加载逻辑
- 相关文件：数据加载方法，滚动处理

### 2. 缓存模式
**功能**：数据缓存优化
**定位特征**：缓存逻辑
**使用场景**：重复访问的数据

```arkts
class CacheManager<T> {
  private cache: Map<string, { data: T; timestamp: number }> = new Map();
  private maxAge: number; // 缓存过期时间（毫秒）
  
  constructor(maxAge: number = 5 * 60 * 1000) { // 默认5分钟
    this.maxAge = maxAge;
  }
  
  get(key: string): T | null {
    const cached = this.cache.get(key);
    if (!cached) return null;
    
    // 检查是否过期
    if (Date.now() - cached.timestamp > this.maxAge) {
      this.cache.delete(key);
      return null;
    }
    
    return cached.data;
  }
  
  set(key: string, data: T): void {
    this.cache.set(key, {
      data,
      timestamp: Date.now()
    });
  }
  
  clear(): void {
    this.cache.clear();
  }
}

// 使用示例
class UserProfileCache extends CacheManager<UserProfile> {
  async getUserProfile(userId: string): Promise<UserProfile> {
    // 尝试从缓存获取
    const cached = this.get(userId);
    if (cached) {
      return cached;
    }
    
    // 从网络获取
    const profile = await this.fetchUserProfileFromNetwork(userId);
    this.set(userId, profile);
    return profile;
  }
  
  private async fetchUserProfileFromNetwork(userId: string): Promise<UserProfile> {
    // 网络请求逻辑
    return {} as UserProfile;
  }
}
```

**定位策略**：
- 搜索模式：缓存逻辑，Map操作，时间戳检查
- 识别特征：数据缓存管理
- 相关文件：缓存配置，缓存清理逻辑

## 代码组织与架构模式

### 1. 分层架构模式
**功能**：代码分层组织
**定位特征**：层次化结构
**使用场景**：复杂应用开发

```
src/
├── presentation/          # 表现层
│   ├── pages/           # 页面
│   ├── components/      # 组件
│   └── router/          # 路由配置
├── business/             # 业务层
│   ├── stores/          # 状态管理
│   ├── services/        # 业务服务
│   └── validators/      # 数据验证
├── data/                 # 数据层
│   ├── models/          # 数据模型
│   ├── repositories/    # 数据仓库
│   └── datasources/     # 数据源
└── domain/              # 领域层
    ├── entities/        # 领域实体
    └── usecases/        # 业务用例
```

**定位策略**：
- 搜索模式：目录结构，层次化文件组织
- 识别特征：按功能分层的代码组织
- 相关文件：各层接口定义，层间调用

### 2. 模块化架构模式
**功能**：模块化开发
**定位特征**：模块边界和接口
**使用场景**：大型团队开发

```arkts
// user模块 - 接口定义
export interface UserService {
  getUser(userId: string): Promise<User>;
  updateUser(user: User): Promise<void>;
  deleteUser(userId: string): Promise<void>;
}

// user模块 - 实现
export class UserServiceImpl implements UserService {
  async getUser(userId: string): Promise<User> {
    // 实现逻辑
    return {} as User;
  }
  
  async updateUser(user: User): Promise<void> {
    // 实现逻辑
  }
  
  async deleteUser(userId: string): Promise<void> {
    // 实现逻辑
  }
}

// user模块 - 导出
export const userService: UserService = new UserServiceImpl();
```

**定位策略**：
- 搜索模式：接口定义，实现类，模块导出
- 识别特征：模块化设计
- 相关文件：模块配置，依赖管理

## ArkTS编程规范指南

### 1. 命名规范

#### 1.1 命名基本原则
- **清晰表达意图**：避免使用单个字母或非标准缩写命名
- **使用正确英文**：使用正确的英文单词并符合英文语法，不要使用中文拼音
- **确保语句清晰**：确保语句清晰，避免歧义

#### 1.2 类型和命名空间命名
**规范**：类名、枚举名、命名空间名采用UpperCamelCase风格

```arkts
// 正确示例
class UserProfile {}
class UserService {}
enum UserStatus {}
namespace UserUtils {}

// 错误示例
class userProfile {}  // 应该首字母大写
class user_service {} // 应该使用UpperCamelCase
```

#### 1.3 变量和函数命名
**规范**：变量名、方法名、参数名采用lowerCamelCase风格

```arkts
// 正确的函数命名示例
function loadUserInfo() {}
function putSetting() {}
function isLoading() {}
function hasPermission() {}
function submit() {}
function updateProfile() {}

// 正确的变量命名示例
let userName: string;
let userEmail: string;
let isLoading: boolean;
```

#### 1.4 常量和枚举值命名
**规范**：常量名、枚举值名采用全部大写，单词间使用下划线隔开

```arkts
// 正确示例
const API_BASE_URL = 'https://api.example.com';
const MAX_RETRY_COUNT = 3;
enum ErrorCode {
  SUCCESS = 0,
  NETWORK_ERROR = 1001,
  SERVER_ERROR = 1002
}
```

#### 1.5 布尔变量命名
**规范**：避免使用否定的布尔变量名，布尔型的局部变量或方法需加上表达是非意义的前缀

```arkts
// 正确示例
let isValid: boolean = true;
let hasPermission: boolean = false;
let canEdit: boolean = true;

// 错误示例
let notValid: boolean = false;
let noPermission: boolean = true; // 双重否定，难以理解
```

### 2. 代码格式规范

#### 2.1 缩进规范
**规范**：使用空格缩进，禁止使用tab字符

```arkts
// 正确示例
@Component
struct MyComponent {
  build() {
    Row() {
      Text("Hello")
        .fontSize(16)
    }
  }
}

// 错误示例（使用Tab）
@Component
struct MyComponent {
	build() {
		Row() {
			Text("Hello")
		}
	}
}
```

#### 2.2 行宽限制
**规范**：行宽不超过120个字符

```arkts
// 正确示例（行宽不超过120字符）
const userProfile = {
  username: 'john_doe',
  email: 'john.doe@example.com',
  age: 25,
  isActive: true
};

// 错误示例（行宽超过120字符）
const userProfile = { username: 'john_doe', email: 'john.doe@example.com', age: 25, isActive: true, lastLogin: '2024-01-15T10:30:00Z', preferences: { theme: 'dark', language: 'zh-CN' } };
```

#### 2.3 条件语句格式
**规范**：条件语句和循环语句的实现建议使用大括号

```arkts
// 正确示例
if (isLoading) {
  showLoading();
} else {
  hideLoading();
}

for (let i = 0; i < items.length; i++) {
  console.log(items[i]);
}

// 错误示例（省略大括号）
if (isLoading)
  showLoading();
else
  hideLoading();
```

#### 2.4 Switch语句格式
**规范**：switch语句的case和default需缩进一层

```arkts
// 正确示例
switch (status) {
  case 'loading':
    showLoading();
    break;
  case 'success':
    showContent();
    break;
  case 'error':
    showError();
    break;
  default:
    showDefault();
}
```

#### 2.5 表达式换行
**规范**：表达式换行需保持一致性，运算符放行末

```arkts
// 正确示例
const result = a + b + c +
               d + e + f;

// 错误示例（运算符放行首）
const result = a + b + c
               + d + e + f;
```

#### 2.6 变量声明
**规范**：多个变量定义和赋值语句不允许写在一行

```arkts
// 正确示例
let username: string = '';
let email: string = '';
let age: number = 0;

// 错误示例
let username: string = ''; let email: string = ''; let age: number = 0;
```

#### 2.7 空格使用规范
**规范**：空格应该突出关键字和重要信息，避免不必要的空格

```arkts
// 正确示例
if (condition) {
  function(param);
} else {
  // 代码
}

// 错误示例（多余的空格）
if ( condition ) {
  function ( param ) ;
} else {
  // 代码
}
```

#### 2.8 字符串引号
**规范**：建议字符串使用单引号

```arkts
// 正确示例
const message = 'Hello World';
const name = 'John';

// 错误示例
const message = "Hello World";
const name = "John";
```

#### 2.9 对象字面量格式
**规范**：对象字面量属性超过4个，需要都换行

```arkts
// 正确示例（属性超过4个）
const userConfig = {
  username: 'john',
  email: 'john@example.com',
  age: 25,
  isActive: true,
  theme: 'dark',
  language: 'zh-CN'
};

// 正确示例（属性不超过4个）
const position = { x: 100, y: 200, width: 300, height: 400 };

// 错误示例（属性超过4个但未换行）
const userConfig = { username: 'john', email: 'john@example.com', age: 25, isActive: true, theme: 'dark', language: 'zh-CN' };
```

#### 2.10 else/catch位置
**规范**：把else/catch放在if/try代码块关闭括号的同一行

```arkts
// 正确示例
if (condition) {
  // 代码
} else {
  // 代码
}

try {
  // 代码
} catch (error) {
  // 错误处理
}

// 错误示例
if (condition) {
  // 代码
}
else {
  // 代码
}

try {
  // 代码
}
catch (error) {
  // 错误处理
}
```

#### 2.11 大括号位置
**规范**：大括号{和语句在同一行

```arkts
// 正确示例
if (condition) {
  // 代码
}

// 错误示例
if (condition)
{
  // 代码
}
```

### 3. 编程实践规范

#### 3.1 可访问修饰符
**规范**：建议添加类属性的可访问修饰符

```arkts
// 正确示例
class UserService {
  private token: string;
  public username: string;
  protected userId: number;
  
  constructor(username: string, userId: number) {
    this.username = username;
    this.userId = userId;
    this.token = '';
  }
  
  private generateToken(): string {
    // 生成token逻辑
    return 'token123';
  }
}

// 错误示例（缺少修饰符）
class UserService {
  token: string;
  username: string;
  userId: number;
}
```

#### 3.2 浮点数写法
**规范**：不建议省略浮点数小数点前后的0

```arkts
// 正确示例
const price = 19.99;
const version = 3.0;
const ratio = 0.5;

// 错误示例
const price = 19.;
const version = .0;
const ratio = .5;
```

#### 3.3 NaN判断
**规范**：判断变量是否为Number.NaN时必须使用Number.isNaN()方法

```arkts
// 正确示例
function isNaNValue(value: number): boolean {
  return Number.isNaN(value);
}

// 错误示例
function isNaNValue(value: number): boolean {
  return value === Number.NaN; // 错误：NaN不等于自身
}
```

#### 3.4 数组遍历
**规范**：数组遍历优先使用Array对象方法

```arkts
// 正确示例
const numbers = [1, 2, 3, 4, 5];
numbers.forEach(num => console.log(num));
const doubled = numbers.map(num => num * 2);
const evenNumbers = numbers.filter(num => num % 2 === 0);

// 错误示例
const numbers = [1, 2, 3, 4, 5];
for (let i = 0; i < numbers.length; i++) {
  console.log(numbers[i]);
}
```

#### 3.5 赋值操作
**规范**：不要在控制性条件表达式中执行赋值操作

```arkts
// 正确示例
let value = 10;
if (value === 10) {
  value = 20;
}

// 错误示例
let value = 10;
if (value = 20) { // 赋值操作，容易导致逻辑错误
  // 代码
}
```

#### 3.6 finally块处理
**规范**：在finally代码块中，不要使用return、break、continue或抛出异常

```arkts
// 正确示例
function safeExecute() {
  try {
    // 执行操作
  } catch (error) {
    // 错误处理
  } finally {
    // 清理资源，但不使用return/break/continue/throw
    cleanupResources();
  }
}

// 错误示例
function safeExecute() {
  try {
    // 执行操作
  } catch (error) {
    // 错误处理
  } finally {
    return; // 错误：在finally中使用return
  }
}
```

#### 3.7 ESObject使用
**规范**：避免使用ESObject（除非在跨语言调用场景）

```arkts
// 正确示例（跨语言调用场景）
function crossLanguageCall(data: ESObject): void {
  // 跨语言调用逻辑
}

// 错误示例（不必要的ESObject使用）
function processData(data: ESObject): void {
  // 普通TypeScript场景，不需要ESObject
  console.log(data.name);
}
```

#### 3.8 数组类型表示
**规范**：使用T[]表示数组类型

```arkts
// 正确示例
function processStrings(items: string[]): void {
  // 处理字符串数组
}

function processNumbers(numbers: number[]): number {
  // 处理数字数组
  return numbers.reduce((sum, num) => sum + num, 0);
}

// 错误示例
function processStrings(items: Array<string>): void {
  // 不推荐的写法
}

function processNumbers(numbers: Array<number>): number {
  // 不推荐的写法
  return numbers.reduce((sum, num) => sum + num, 0);
}
```

## 总结

本文档详细介绍了ArkTS语言的各类编程模式、代码特征和最佳实践，涵盖了装饰器使用、生命周期管理、导航路由、状态管理、网络请求、权限管理、性能优化和编程规范等方面。通过理解和掌握这些模式，可以快速识别和理解ArkTS代码的结构和功能，为HarmonyOS功能定位提供强有力的支持。

特别需要注意的是，ArkTS作为TypeScript的超集，在保持语法兼容的同时，强化了静态类型检查和声明式UI开发能力。在实际开发中，应当严格遵循ArkTS的编程规范，采用适当的装饰器和状态管理机制，编写高性能、可维护的HarmonyOS应用。这些模式不仅有助于代码分析，也对实际的开发工作具有重要的指导意义。