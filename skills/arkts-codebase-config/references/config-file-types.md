# HarmonyOS配置文件类型详解

本文档详细说明HarmonyOS应用中各种配置文件的用途、结构和关键字段。

## app.json5

### 位置
`AppScope/app.json5`

### 作用
应用级全局配置文件，定义应用的基本信息、签名信息、权限等全局属性。

### 关键字段

```json5
{
  "app": {
    "bundleName": "com.example.app",        // 应用包名（必填）
    "vendor": "example_vendor",              // 应用厂商
    "versionCode": 1000000,                   // 版本号（数字）
    "versionName": "1.0.0",                   // 版本名称
    "icon": "$media:app_icon",               // 应用图标
    "label": "$string:app_name",             // 应用名称
    "distributedNotificationEnabled": false, // 是否支持分布式通知
    "apiReleaseType": "Release",             // API版本类型
    "targetAPIVersion": 9,                   // 目标API版本
    "minAPIVersion": 9                       // 最低API版本
  },
  "appSignature": {
    "signingConfigs": [                      // 签名配置
      {
        "name": "default",
        "type": "HarmonyOS",
        "material": {
          "certpath": "证书路径",
          "storePassword": "密码",
          "keyAlias": "别名",
          "keyPassword": "密码"
        }
      }
    ]
  }
}
```

### 常见配置问题
- 版本号和版本名称在哪里配置？ → versionCode、versionName
- 应用包名在哪里定义？ → bundleName
- 目标API版本如何配置？ → targetAPIVersion、minAPIVersion
- 应用图标和名称在哪里配置？ → icon、label

## module.json5

### 位置
每个模块的根目录，例如：
- `entry/src/main/module.json5`
- `feature/src/main/module.json5`

### 作用
模块级配置文件，定义模块的能力、页面、权限等。

### 关键字段

```json5
{
  "module": {
    "name": "entry",                         // 模块名称
    "type": "entry",                          // 模块类型：entry/feature/har/hsp
    "description": "$string:module_desc",    // 模块描述
    "mainElement": "EntryAbility",           // 主入口Ability
    "deviceTypes": [                         // 设备类型
      "default",
      "tablet",
      "car"
    ],
    "deliveryWithInstall": true,             // 是否随应用安装
    "installationFree": false,                // 是否免安装
    "pages": "$profile:main_pages",          // 页面配置文件
    "abilities": [                           // Ability列表
      {
        "name": "EntryAbility",
        "srcEntry": "./ets/entryability/EntryAbility.ets",
        "description": "$string:entryability_desc",
        "icon": "$media:icon",
        "label": "$string:entryability_label",
        "exported": true,                    // 是否可被其他应用访问
        "skills": [                          // 技能/意图过滤
          {
            "actions": ["action.system.home"],
            "entities": ["entity.system.home"]
          }
        ],
        "continuable": true,                // 是否可跨设备迁移
        "startWindowIcon": "$media:icon",   // 启动窗口图标
        "startWindowBackground": "$color:start_window_background"
      }
    ],
    "extensionAbilities": [                  // 扩展Ability
      {
        "name": "FormExtension",
        "srcEntry": "./ets/formability/FormAbility.ets",
        "type": "form",                     // 扩展类型：form/serviceProvider等
        "description": "$string:form_desc",
        "exported": true
      }
    ],
    "requestPermissions": [                  // 权限请求列表
      {
        "name": "ohos.permission.INTERNET",
        "reason": "$string:internet_permission_reason",
        "usedScene": {
          "abilities": ["EntryAbility"],
          "when": "always"                  // always/inuse
        }
      }
    ],
    "dependencies": [                       // 模块依赖
      {
        "moduleName": "library",
        "moduleType": "har"
      }
    ]
  }
}
```

### 常见配置问题
- 如何添加新页面？ → 在pages数组中添加页面路径
- 如何配置Ability的启动属性？ → abilities中配置exported、continuable等
- 如何声明权限？ → 在requestPermissions数组中声明
- 模块类型有哪几种？ → type字段：entry/feature/har/hsp
- 如何配置页面路由？ → pages字段引用的profile文件

## build-profile.json5

### 位置
- 项目根目录：`build-profile.json5`
- 模块目录：`模块名/build-profile.json5`

### 作用
构建配置文件，定义构建选项、产品配置、多包构建等。

### 项目级build-profile.json5

```json5
{
  "apiType": "stageMode",                   // 开发模式：stageMode/FA模式
  "buildOption": {},                        // 构建选项
  "targets": [                              // 多包构建目标
    {
      "name": "default",
      "runtimeOS": "HarmonyOS"
    },
    {
      "name": "phone",
      "runtimeOS": "HarmonyOS"
    }
  ]
}
```

### 模块级build-profile.json5

```json5
{
  "apiType": "stageMode",
  "buildOption": {
    "arkOptions": {                         // ArkTS编译选项
      "obfuscation": {                      // 代码混淆
        "ruleOptions": {
          "enable": true,
          "files": ["./obfuscation-rules.txt"]
        }
      }
    },
    "nativeLib": {                          // 原生库选项
      "filter": {
        "externalNativeLibs": [
          "**/*.so"
        ]
      }
    }
  },
  "targets": [
    {
      "name": "default",
      "runtimeOS": "HarmonyOS"
    }
  ]
}
```

### 常见配置问题
- 如何开启代码混淆？ → buildOption.arkOptions.obfuscation.enable
- 如何配置多包构建？ → targets数组配置不同产品
- 如何过滤so库？ → buildOption.nativeLib.filter
- 项目模式是什么？ → apiType字段

## oh-package.json5

### 位置
项目根目录和模块根目录

### 作用
依赖管理文件，定义项目依赖和包信息。

```json5
{
  "name": "entry",
  "version": "1.0.0",
  "description": "entry module",
  "main": "",
  "author": "",
  "license": "",
  "dependencies": {                         // 外部依赖
    "@ohos/library": "^1.0.0"
  },
  "devDependencies": {                      // 开发依赖
    "@ohos/hypium": "1.0.16"
  },
  "dynamicDependencies": {},                // 动态依赖
  "overrides": {}                           // 依赖覆盖
}
```

### 常见配置问题
- 如何添加第三方库依赖？ → dependencies中添加
- 依赖版本如何指定？ → 使用语义化版本号（^1.0.0、~1.0.0、1.0.0）

## resources目录配置文件

### string.json
位置：`src/main/resources/base/element/string.json`

```json
{
  "string": [
    {
      "name": "app_name",
      "value": "应用名称"
    },
    {
      "name": "module_desc",
      "value": "模块描述"
    }
  ]
}
```

### color.json
位置：`src/main/resources/base/element/color.json`

```json
{
  "color": [
    {
      "name": "start_window_background",
      "value": "#FFFFFF"
    },
    {
      "name": "primary_color",
      "value": "#007DFF"
    }
  ]
}
```

### float.json
位置：`src/main/resources/base/element/float.json`

```json
{
  "float": [
    {
      "name": "font_size_large",
      "value": "20"
    },
    {
      "name": "padding_normal",
      "value": "16"
    }
  ]
}
```

### 常见配置问题
- 字符串资源在哪里？ → string.json
- 颜色如何定义？ → color.json
- 尺寸单位是什么？ → float.json，单位为vp
- 如何引用资源？ → $string:name、$color:name、$float:name

## 配置文件引用关系

### resource引用格式
- `$string:name` - 字符串资源
- `$color:name` - 颜色资源
- `$float:name` - 尺寸资源
- `$media:name` - 媒体资源
- `$profile:name` - profile文件

### 页面配置文件
位置：`src/main/resources/base/profile/main_pages.json`

```json
{
  "src": [
    "pages/IndexPage",
    "pages/DetailPage"
  ]
}
```

### 配置文件查找优先级
1. 特定资源目录（如zh_CN、en_US）
2. base资源目录
3. 系统默认资源

## 模块类型说明

### entry（入口模块）
- 应用主入口
- 必须有且只能有一个
- 包含应用图标、启动页面等

### feature（特性模块）
- 功能模块
- 可以有多个
- 提供特定的业务功能

### har（HarmonyOS Archive）
- 静态共享库
- 可以被其他模块引用
- 编译时静态链接

### hsp（HarmonyOS Shared Package）
- 动态共享库
- 运行时动态加载
- 多个应用共享

## 权限配置层次

### 系统权限（ohos.permission.*）
- 系统级权限，在app.json5中声明
- 部分需要用户授权

### 自定义权限
- 应用自定义权限
- 在module.json5中定义

## 配置文件修改建议

### 修改配置时的注意事项
1. 修改后需要重新编译构建
2. 权限相关配置可能需要重新签名
3. 资源文件修改后需要同步更新引用
4. 模块配置修改可能影响其他模块

### 配置验证方法
- DevEco Studio会自动验证配置文件格式
- 构建时会检查配置合法性
- 可以使用工具检查配置完整性
