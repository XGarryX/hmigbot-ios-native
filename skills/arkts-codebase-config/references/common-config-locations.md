# 常见配置位置索引

本文档提供了HarmonyOS应用中常见配置项的位置索引，帮助快速定位配置。

## 快速查找指南

### 按功能类型查找
- [功能开关](#功能开关)
- [权限配置](#权限配置)
- [网络配置](#网络配置)
- [存储配置](#存储配置)
- [UI配置](#ui配置)
- [日志配置](#日志配置)
- [应用信息](#应用信息)
- [模块信息](#模块信息)
- [资源配置](#资源配置)
- [构建配置](#构建配置)

### 按文件类型查找
- [app.json5](#appjson5)
- [module.json5](#modulejson5)
- [build-profile.json5](#build-profilejson5)
- [常量文件](#常量文件)
- [资源文件](#资源文件)

## 功能开关

### 定义位置
```
src/main/ets/common/Constants.ets
src/main/ets/config/FeatureFlag.ets
src/main/ets/utils/Config.ets
src/main/ets/appconfig/
resources/rawfile/config/feature_flags.json
```

### 读取位置
```
src/main/ets/pages/*Page.ets         // Page组件中读取
src/main/ets/ability/*Ability.ets     // Ability中读取
src/main/ets/feature/*Feature.ets     // 功能代码中读取
```

### 常见开关名称
```typescript
ENABLE_NEW_UI
ENABLE_ANIMATION
ENABLE_PAYMENT
ENABLE_CACHE
DEBUG_MODE
VERBOSE_LOG
USE_NEW_API
```

### 搜索关键词
```
FeatureFlag
ENABLE_
DEBUG_
getFlag
setFlag
```

## 权限配置

### 声明位置
```
AppScope/app.json5           // 全局权限
entry/src/main/module.json5  // 模块权限
feature/src/main/module.json5  // 特性模块权限
```

### 请求位置
```
src/main/ets/ability/*Ability.ets     // Ability的onCreate
src/main/ets/pages/*Page.ets           // Page的aboutToAppear
src/main/ets/utils/PermissionUtil.ets  // 权限工具类
```

### 使用位置
```
src/main/ets/utils/PermissionUtil.ets  // 权限检查
src/main/ets/network/*NetUtil.ets      // 网络权限使用
src/main/ets/storage/*Storage.ets      // 存储权限使用
```

### 常见权限
```json5
ohos.permission.INTERNET
ohos.permission.CAMERA
ohos.permission.READ_MEDIA
ohos.permission.WRITE_MEDIA
ohos.permission.LOCATION
ohos.permission.READ_CONTACTS
```

### 搜索关键词
```
requestPermissions
checkAccessToken
abilityAccessCtrl
GrantStatus
```

## 网络配置

### 基础URL配置
```
src/main/ets/common/Constants.ets      // 常量定义
src/main/ets/config/NetworkConfig.ets // 网络配置
resources/rawfile/config/network.json  // 配置文件
```

### 超时配置
```
src/main/ets/common/Constants.ets      // 超时常量
src/main/ets/utils/HttpUtil.ets        // HTTP工具
build-profile.json5                    // 构建时配置
```

### 代理配置
```
src/main/ets/config/NetworkConfig.ets
build-profile.json5
```

### 常见配置项
```typescript
BASE_URL
API_TIMEOUT
REQUEST_TIMEOUT
CONNECT_TIMEOUT
READ_TIMEOUT
```

### 搜索关键词
```
BASE_URL
TIMEOUT
HttpUtil
NetworkConfig
```

## 存储配置

### 数据库配置
```
src/main/ets/database/RdbStore.ets      // 关系数据库
src/main/ets/database/OrmStore.ets      // ORM配置
```

### 缓存配置
```
src/main/ets/cache/CacheManager.ets     // 缓存管理
src/main/ets/common/Constants.ets      // 缓存大小
```

### 文件路径配置
```
src/main/ets/common/Constants.ets      // 路径常量
src/main/ets/utils/PathUtil.ets        // 路径工具
```

### 常见配置项
```typescript
DB_NAME
DB_VERSION
CACHE_SIZE
CACHE_EXPIRE
FILE_PATH
```

### 搜索关键词
```
DB_NAME
CACHE_SIZE
RdbStore
CacheManager
```

## UI配置

### 主题配置
```
resources/base/element/color.json       // 颜色主题
resources/base/element/float.json       // 尺寸配置
resources/base/profile/theme.json       // 主题配置
```

### 字体配置
```
resources/base/element/string.json      // 字符串资源
resources/base/element/float.json       // 字体大小
```

### 布局配置
```
resources/base/element/float.json       // 间距、边距
src/main/ets/common/Constants.ets      // 布局常量
```

### 常见配置项
```typescript
PRIMARY_COLOR
SECONDARY_COLOR
FONT_SIZE_LARGE
PADDING_NORMAL
MARGIN_DEFAULT
```

### 搜索关键词
```
PRIMARY_COLOR
FONT_SIZE
PADDING
theme
```

## 日志配置

### 日志开关
```
src/main/ets/common/Constants.ets      // 开关常量
src/main/ets/utils/Logger.ets          // 日志工具
```

### 日志级别
```
src/main/ets/common/Constants.ets      // 级别常量
src/main/ets/utils/Logger.ets          // 日志实现
```

### 日志输出
```
src/main/ets/utils/Logger.ets          // 输出配置
```

### 常见配置项
```typescript
LOG_ENABLED
LOG_LEVEL
LOG_FILE
LOG_MAX_SIZE
```

### 搜索关键词
```
LOG_ENABLED
LOG_LEVEL
Logger
console
```

## 应用信息

### 包名和版本
```
AppScope/app.json5                    // 全局配置
entry/src/main/module.json5           // 模块配置
```

### 应用签名
```
AppScope/app.json5                    // 签名配置
build-profile.json5                    // 构建签名
```

### 应用图标和名称
```
resources/base/media/                  // 图标资源
resources/base/element/string.json     // 名称资源
```

### 常见配置项
```json5
bundleName
versionCode
versionName
icon
label
```

### 搜索关键词
```
bundleName
versionCode
app.json5
```

## 模块信息

### 模块列表
```
entry/src/main/module.json5           // 入口模块
feature/src/main/module.json5         // 特性模块
har/module.json5                      // 静态库
hsp/module.json5                      // 动态库
```

### 模块依赖
```
entry/build-profile.json5             // 入口模块依赖
feature/build-profile.json5           // 特性模块依赖
oh-package.json5                      // 包依赖
```

### Ability配置
```
entry/src/main/module.json5           // Ability列表
feature/src/main/module.json5         // 特性Ability
```

### 常见配置项
```json5
module.name
module.type
abilities
dependencies
```

### 搜索关键词
```
module.name
module.type
abilities
dependencies
```

## 资源配置

### 字符串资源
```
resources/base/element/string.json
resources/zh_CN/element/string.json
resources/en_US/element/string.json
```

### 颜色资源
```
resources/base/element/color.json
resources/dark/element/color.json
```

### 尺寸资源
```
resources/base/element/float.json
```

### 媒体资源
```
resources/base/media/
resources/base/profile/
```

### 常见配置项
```json
string.name
color.name
float.name
```

### 搜索关键词
```
$string:
$color:
$float:
$media:
```

## 构建配置

### 构建选项
```
build-profile.json5                   // 项目构建
entry/build-profile.json5             // 模块构建
```

### 编译选项
```
build-profile.json5                   // ArkTS选项
```

### 代码混淆
```
build-profile.json5                   // 混淆配置
obfuscation-rules.txt                 // 混淆规则
```

### 签名配置
```
build-profile.json5                   // 构建签名
AppScope/app.json5                    // 应用签名
```

### 常见配置项
```json5
buildMode
targets
apiType
arkOptions
```

### 搜索关键词
```
buildMode
targets
build-profile
```

## 配置文件详解

### app.json5

**位置**：`AppScope/app.json5`

**作用**：应用级全局配置

**关键字段**：
```json5
{
  "app": {
    "bundleName": "com.example.app",     // 应用包名
    "versionCode": 1000000,               // 版本号
    "versionName": "1.0.0",               // 版本名称
    "icon": "$media:app_icon",           // 应用图标
    "label": "$string:app_name",         // 应用名称
    "targetAPIVersion": 9,               // 目标API版本
    "minAPIVersion": 9                   // 最低API版本
  }
}
```

**常见问题**：
- 应用包名在哪里配置？ → bundleName
- 版本号在哪里配置？ → versionCode、versionName
- 应用图标在哪里配置？ → icon

### module.json5

**位置**：每个模块根目录

**作用**：模块级配置

**关键字段**：
```json5
{
  "module": {
    "name": "entry",                     // 模块名称
    "type": "entry",                      // 模块类型
    "mainElement": "EntryAbility",        // 主入口
    "abilities": [                        // Ability列表
      {
        "name": "EntryAbility",
        "exported": true,
        "skills": [...]
      }
    ],
    "requestPermissions": [              // 权限列表
      {
        "name": "ohos.permission.INTERNET",
        "usedScene": {...}
      }
    ]
  }
}
```

**常见问题**：
- 如何添加Ability？ → abilities数组
- 如何声明权限？ → requestPermissions
- 模块类型有哪些？ → type字段

### build-profile.json5

**位置**：项目根目录和模块目录

**作用**：构建配置

**关键字段**：
```json5
{
  "apiType": "stageMode",
  "buildOption": {
    "arkOptions": {
      "obfuscation": {...}               // 混淆配置
    }
  },
  "targets": [                           // 多包构建
    {
      "name": "default",
      "runtimeOS": "HarmonyOS"
    }
  ]
}
```

**常见问题**：
- 如何开启代码混淆？ → arkOptions.obfuscation
- 如何配置多包构建？ → targets

### 常量文件

**位置**：
```
src/main/ets/common/Constants.ets
src/main/ets/config/Config.ets
src/main/ets/utils/Constants.ets
```

**作用**：定义应用常量和配置

**常见内容**：
```typescript
export class Constants {
  // 应用信息
  static readonly APP_NAME = "MyApp";
  static readonly VERSION = "1.0.0";
  
  // 功能开关
  static readonly ENABLE_NEW_UI = true;
  static readonly DEBUG_MODE = false;
  
  // 网络配置
  static readonly BASE_URL = "https://api.example.com";
  static readonly TIMEOUT = 30000;
  
  // 存储配置
  static readonly DB_NAME = "app.db";
  static readonly DB_VERSION = 1;
}
```

### 资源文件

**位置**：
```
resources/base/element/string.json    // 字符串
resources/base/element/color.json     // 颜色
resources/base/element/float.json     // 尺寸
resources/base/media/                 // 媒体
resources/base/profile/               // profile
```

**作用**：应用资源和主题配置

**常见内容**：
```json
{
  "string": [
    {"name": "app_name", "value": "应用名称"},
    {"name": "button_ok", "value": "确定"}
  ]
}
```

## 配置查找流程

### 1. 确定配置类型
- 功能开关 → 常量文件
- 权限 → module.json5
- 网络 → 配置文件或常量
- UI → 资源文件

### 2. 确定查找范围
- 全局配置 → app.json5
- 模块配置 → module.json5
- 构建配置 → build-profile.json5

### 3. 使用搜索工具
- 搜索配置名称：`rg "CONFIG_NAME"`
- 搜索文件类型：`glob "**/module.json5"`
- 搜索关键词：`grep "KEYWORD"`

### 4. 读取相关文件
- 按优先级读取配置文件
- 检查默认值
- 查看使用场景

## 配置修改建议

### 修改前的准备
1. 备份原始配置
2. 了解配置影响范围
3. 确认配置类型和位置

### 修改时的注意事项
1. 遵循配置格式规范
2. 保持配置一致性
3. 更新相关引用

### 修改后的验证
1. 重新编译构建
2. 测试相关功能
3. 检查配置生效
