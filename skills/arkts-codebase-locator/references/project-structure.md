# HarmonyOS项目结构与文件定位指南

## HarmonyOS应用架构概述

HarmonyOS应用主要采用Stage模型架构，本文档详细介绍ArkTS语言Harmony应用的典型项目结构和各目录功能，帮助技能准确定位各类功能实现位置。

> **V1 / V2 兼容说明**：项目锁 V2（API 12+），但仓库可能同时存在 V1 与 V2 装饰器。本文中所有 grep / find 命令默认采用 V1+V2 兼容模式（如 `@Component(V2)?\b`、`@State|@Local`、`@Observed|@ObservedV2`、`@StorageLink|AppStorageV2`），以避免漏检。新增/示例代码应使用 V2 写法。

## 标准项目结构

### 1. 项目根目录结构

```
HarmonyOS-Project/
├── entry/                          # 主模块目录
│   ├── src/main/
│   │   ├── ets/
│   │   │   ├── application/        # 应用入口
│   │   │   │   └── AppStage.ets    # 应用入口文件
│   │   │   ├── common/             # 公共资源
│   │   │   │   └── constants.ets   # 公常量定义
│   │   │   └── pages/              # 页面文件
│   │   │       ├── Index.ets       # 首页
│   │   │       └── Login.ets       # 登录页
│   │   └── module.json5            # 模块配置文件
│   └── hvigorfile.ts               # 构建配置文件
├── features/                       # 功能模块
│   ├── user/                       # 用户功能
│   │   ├── src/main/ets/
│   │   │   ├── components/         # 用户相关组件
│   │   │   ├── pages/              # 用户相关页面
│   │   │   ├── services/           # 用户服务
│   │   │   └── stores/             # 用户状态管理
│   │   └── module.json5            # 用户模块配置
│   └── order/                      # 订单功能
│       └── src/main/ets/
│           ├── components/         # 订单相关组件
│           ├── pages/              # 订单相关页面
│           ├── models/             # 订单数据模型
│           └── services/           # 订单服务
├── common/                         # 公共模块
│   ├── src/main/ets/
│   │   ├── components/             # 公共组件
│   │   ├── utils/                  # 工具函数
│   │   ├── constants/              # 公共常量
│   │   └── themes/                 # 主题配置
│   └── module.json5                # 公共模块配置
└── ohos-build.json                 # 项目构建配置
```

### 2. 核心目录功能说明

#### 2.1 模块目录 (`entry/`, `features/`)
**功能**：应用模块，包含页面、组件、服务等
**定位目标**：功能模块的具体实现
**关键文件**：
- `src/main/ets/pages/` - 页面组件
- `src/main/ets/components/` - 可复用组件
- `src/main/ets/services/` - 业务服务
- `src/main/ets/stores/` - 状态管理
- `module.json5` - 模块配置

#### 2.2 应用入口 (`application/`)
**功能**：应用生命周期管理和全局配置
**定位目标**：应用初始化和全局逻辑
**关键文件**：
- `AppStage.ets` - 应用入口文件
  ```typescript
  import AbilityStage from '@ohos.application.AbilityStage';
  
  export default class MyApplication extends AbilityStage {
    onCreate(want, launchParam) {
      // 应用创建逻辑
    }
  }
  ```

#### 2.3 页面目录 (`pages/`)
**功能**：应用页面实现
**定位目标**：页面UI和逻辑实现
**关键文件**：
- `*.ets` - 页面组件文件（V2 推荐写法）
  ```typescript
  @Entry
  @ComponentV2
  struct Index {
    build() {
      // 页面构建逻辑
    }
  }
  ```
  V1 历史写法：`@Entry @Component struct Index { ... }`

#### 2.4 组件目录 (`components/`)
**功能**：可复用UI组件
**定位目标**：组件定义和使用
**关键文件**：
- `*.ets` - 组件定义文件（V2 推荐写法）
  ```typescript
  @ComponentV2
  struct MyButton {
    @Param @Once text: string = ''
    build() {
      Button(this.text)
    }
  }
  ```
  V1 历史写法：`@Component struct MyButton { @Prop text: string; ... }`

#### 2.5 公共模块 (`common/`)
**功能**：跨模块共享的代码和资源
**定位目标**：公共功能和资源
**关键文件**：
- `src/main/ets/components/` - 公共组件
- `src/main/ets/utils/` - 工具函数
- `src/main/ets/constants/` - 公共常量
- `src/main/ets/themes/` - 主题配置

#### 2.6 服务目录 (`services/`)
**功能**：业务逻辑和数据服务
**定位目标**：数据处理和业务逻辑
**关键文件**：
- `*.ets` - 服务实现文件
  ```typescript
  export class UserService {
    getUserInfo() {
      // 用户信息获取逻辑
    }
  }
  ```

#### 2.7 状态管理目录 (`stores/` / `viewmodel/`)
**功能**：应用状态管理
**定位目标**：全局和局部状态管理
**关键文件**：
- `*.ets` - 状态管理文件（V2 推荐写法）
  ```typescript
  @ObservedV2
  class UserStore {
    @Trace userInfo: UserInfo = new UserInfo()
  }
  ```
  V1 历史写法：`@Observed class UserStore { userInfo: UserInfo; ... }`

  V2 全局共享：`@Local user: UserStore = AppStorageV2.connect(UserStore, 'user', () => new UserStore())!`
  V1 历史写法：`@StorageLink('user') user: UserStore = new UserStore()`

## 文件类型定位指南

### 1. 页面文件定位

#### 文件模式
- 路径：`**/pages/*.ets`
- 装饰器（V1+V2）：`@Entry` + `@Component(V2)?\b`
- 特征：包含页面构建逻辑和导航调用

#### 搜索模式
```bash
# V1+V2 兼容：搜索页面文件
find . -path "*/pages/*.ets" -exec grep -lE "@Entry|@Component(V2)?\b" {} \;
```

#### 示例文件（V2 推荐）
```typescript
// entry/src/main/ets/pages/Login.ets
@Entry
@ComponentV2
struct Login {
  @Local username: string = ''
  @Local password: string = ''

  build() {
    Row() {
      Column() {
        TextInput({ placeholder: '用户名' })
          .onChange(value => this.username = value)
        Button('登录')
          .onClick(() => this.login())
      }
    }
  }

  private login() {
    // 登录逻辑
  }
}
```

### 2. 组件文件定位

#### 文件模式
- 路径：`**/components/*.ets`
- 装饰器（V1+V2）：`@Component(V2)?\b`
- 特征：可复用的UI组件定义

#### 搜索模式
```bash
# V1+V2 兼容：搜索组件文件
find . -path "*/components/*.ets" -exec grep -lE "@Component(V2)?\b" {} \;
```

#### 示例文件（V2 推荐）
```typescript
// common/src/main/ets/components/MyButton.ets
@ComponentV2
export struct MyButton {
  @Param @Once text: string = ''
  @Event onAction: () => void = () => {}

  build() {
    Button(this.text)
      .onClick(() => this.onAction())
  }
}
```

### 3. 服务文件定位

#### 文件模式
- 路径：`**/services/*.ets`
- 特征：业务逻辑和数据服务实现

#### 搜索模式
```typescript
// 搜索服务文件
find . -path "*/services/*.ets" -exec grep -l "class.*Service\|export.*=" {} \;
```

#### 示例文件
```typescript
// entry/src/main/ets/services/UserService.ets
export class UserService {
  private userStorage: Preferences;
  
  constructor() {
    this.userStorage = ...; // 初始化存储
  }
  
  async getUserInfo(): Promise<UserInfo> {
    // 获取用户信息逻辑
  }
  
  async saveUserInfo(info: UserInfo): Promise<void> {
    // 保存用户信息逻辑
  }
}
```

### 4. 状态管理文件定位

#### 文件模式
- 路径：`**/stores/*.ets` 或 `**/viewmodel/*.ets`
- 装饰器（V1+V2）：V1 `@Observed|@State|@Prop|@Link|@StorageLink|@StorageProp`，V2 `@ObservedV2|@Local|@Param|@Event|@Trace|AppStorageV2|PersistenceV2|@Monitor|@Computed`
- 特征：状态管理和数据流

#### 搜索模式
```bash
# V1+V2 兼容：搜索状态管理文件
find . -path "*/stores/*.ets" -exec grep -lE "@Observed(V2)?\b|@State|@Local|@Prop|@Param|AppStorageV2|@Trace" {} \;
```

#### 示例文件（V2 推荐）
```typescript
// entry/src/main/ets/stores/UserStore.ets
import { UserInfo } from '../models/UserInfo';

@ObservedV2
export class UserStore {
  @Trace userInfo: UserInfo | null = null
  @Trace isLoading: boolean = false

  async loadUserInfo() {
    this.isLoading = true
    // 加载用户信息逻辑
    this.isLoading = false
  }
}

// 全局共享：
// @Local userStore: UserStore = AppStorageV2.connect(UserStore, 'userStore', () => new UserStore())!
```

### 5. 工具函数文件定位

#### 文件模式
- 路径：`**/utils/*.ets`
- 特征：工具函数和辅助方法

#### 搜索模式
```typescript
// 搜索工具函数文件
find . -path "*/utils/*.ets" -exec grep -l "export.*function\|export.*=" {} \;
```

#### 示例文件
```typescript
// common/src/main/ets/utils/DateUtils.ets
export class DateUtils {
  static formatDate(date: Date): string {
    // 日期格式化逻辑
  }
  
  static parseDate(dateString: string): Date {
    // 日期解析逻辑
  }
}
```

### 6. 常量定义文件定位

#### 文件模式
- 路径：`**/constants/*.ets`
- 关键字：`const`, `let`
- 特征：常量定义和配置

#### 搜索模式
```typescript
// 搜索常量定义文件
find . -path "*/constants/*.ets" -exec grep -l "const\|let.*=" {} \;
```

#### 示例文件
```typescript
// common/src/main/ets/constants/ApiConstants.ets
export const API_BASE_URL = 'https://api.example.com';
export const API_TIMEOUT = 10000;
export enum ErrorCode {
  SUCCESS = 0,
  NETWORK_ERROR = 1001,
  SERVER_ERROR = 1002
}
```

### 7. 配置文件定位

#### 文件模式
- 路径：`**/module.json5`
- 特征：模块配置和权限声明

#### 示例文件
```json
// entry/src/main/module.json5
{
  "module": {
    "name": "entry",
    "type": "entry",
    "description": "$string:module_desc",
    "mainElement": "MainAbility",
    "deviceTypes": [
      "phone",
      "tablet"
    ],
    "deliveryWithInstall": true,
    "installationFree": false,
    "pages": "$profile:main_pages",
    "abilities": [
      {
        "name": "MainAbility",
        "srcEntrance": "./ets/Application/MyAbility.ts",
        "description": "$string:MainAbility_desc",
        "icon": "$media:icon",
        "label": "$string:MainAbility_label",
        "startWindowIcon": "$media:icon",
        "startWindowBackground": "$color:start_window_background"
      }
    ],
    "requestPermissions": [
      {
        "name": "ohos.permission.INTERNET",
        "reason": "$string:permission_internet_reason",
        "usedScene": {
          "abilities": ["MainAbility"],
          "when": "always"
        }
      }
    ]
  }
}
```

## 配置文件定位

### 1. 应用配置文件

#### 位置
- 项目根目录：`AppScope/app.json5`
- 模块目录：`entry/src/main/module.json5`

#### 内容特征
- 应用基本信息
- 模块配置
- 权限声明
- 资源引用

### 2. 构建配置文件

#### 文件模式
- `ohos-build.json` - 项目构建配置
- `hvigorfile.ts` - 模块构建配置

#### 搜索模式
```bash
find . -name "ohos-build.json" -o -name "hvigorfile.ts"
```

### 3. 资源配置文件

#### 文件模式
- `resources/` - 资源目录
- `resources/base/element/` - 字符串资源
- `resources/base/media/` - 媒体资源

#### 搜索模式
```bash
find . -path "*/resources/*"
```

## 特殊结构模式

### 1. 多模块项目结构

```
Project/
├── entry/              # 入口模块
├── feature_user/       # 用户功能模块
├── feature_order/      # 订单功能模块
├── feature_payment/    # 支付功能模块
└── common/             # 公共模块
```

### 2. 分层架构结构

```
Project/
├── presentation/       # 表现层
│   ├── pages/         # 页面
│   └── components/    # 组件
├── business/          # 业务层
│   ├── services/     # 服务
│   └── stores/        # 状态管理
├── data/              # 数据层
│   ├── models/        # 数据模型
│   └── repositories/  # 数据仓库
└── domain/            # 领域层
    └── entities/      # 领域实体
```

### 3. 微服务结构

```
Project/
├── gateway/           # 网关模块
├── auth_service/      # 认证服务
├── user_service/      # 用户服务
├── order_service/     # 订单服务
└── payment_service/   # 支付服务
```

## 文件搜索策略

### 1. 基于文件扩展名搜索
```bash
find . -name "*.ets"           # 所有ArkTS文件
find . -name "*.json5"         # 配置文件
find . -name "*.ts"           # TypeScript文件
```

### 2. 基于装饰器搜索（V1+V2 兼容）
```bash
# 页面和组件（V1+V2）
grep -rE "@Entry|@Component(V2)?\b" --include="*.ets" .

# 状态管理（V1+V2）
grep -rE "@State|@Local|@Prop|@Param|@Link|@Event|@Provide|@Provider|@Consume|@Consumer" --include="*.ets" .

# 观察者模式（V1+V2）
grep -rE "@Observed(V2)?\b|@ObjectLink|@Trace" --include="*.ets" .

# 全局/本地/持久化存储（V1+V2）
grep -rE "@StorageLink|@StorageProp|AppStorageV2|@LocalStorageLink|@LocalStorageProp|PersistentStorage|PersistenceV2" --include="*.ets" .

# 监听/派生（V1+V2）
grep -rE "@Watch|@Monitor|@Computed" --include="*.ets" .
```

### 3. 基于功能关键词搜索
```bash
grep -r "router\|navigation" --include="*.ets" .     # 导航相关
grep -r "http\|axios" --include="*.ets" .           # 网络请求
grep -r "requestPermissions" --include="*.ets" .    # 权限申请
```

### 4. 基于类和方法搜索
```bash
grep -r "class.*Service" --include="*.ets" .         # 服务类
grep -r "interface.*" --include="*.ets" .            # 接口定义
grep -r "export.*=" --include="*.ets" .              # 导出函数
```

## 定位优先级

### 1. 高优先级文件
- `AppStage.ets` - 应用入口
- `pages/Index.ets` - 主页
- `main/module.json5` - 主模块配置

### 2. 中优先级文件
- `services/*.ets` - 服务实现
- `stores/*.ets` - 状态管理
- `components/*.ets` - 组件定义

### 3. 低优先级文件
- `utils/*.ets` - 工具函数
- `constants/*.ets` - 常量定义
- 配置文件

## 总结

本指南详细说明了HarmonyOS ArkTS应用的典型项目结构和文件定位方法。通过理解这些结构和模式，可以快速定位各类功能实现的具体位置，提高开发效率和代码导航能力。