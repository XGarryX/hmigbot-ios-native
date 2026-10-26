> 来源: ohpm 中央仓 README(T1 信源) | 包: `bank_har` | ohpm 最新版: 1.0.0 | 抓取: 2026-07-16
> 注意: 版本可能比市场快照新,以此为准时核对 CHANGELOG

# 鸿蒙银行卡SDK开发文档

[![文档版本](https://img.shields.io/badge/版本-1.0.0-blue.svg)](https://github.com)

[![HarmonyOS](https://img.shields.io/badge/HarmonyOS-SDK-orange.svg)](https://developer.harmonyos.com)

[![License](https://img.shields.io/badge/license-Commercial-green.svg)](LICENSE)

> **起草时间**: 2024年04月

---

## 📋 目录

- [基本说明](#基本说明)

- [平台要求](#平台要求)

- [集成步骤](#集成步骤)

- [主要类说明](#主要类说明)

- [识别服务设置](#识别服务设置)

- [错误码说明](#错误码说明)

- [可选功能](#可选功能)

- [版本历史](#版本历史)

---

## 📖 基本说明

本开发包集成了支持各类银行卡(储蓄卡、信用卡)识别功能,具体特性包括:

### 核心功能

- ✅ **卡号识别**: 支持 15~19 位凸面数字及平面数字的图片文件转数字字符

- ✅ **银行信息**: 自动识别并显示银行行名、行号

- ✅ **卡片信息**: 识别卡片名称、卡片类型

- ✅ **有效期识别**: 支持信用卡有效日期识别

- ✅ **多种输入方式**: 支持视频识别和图片导入识别

---

## 🖥️ 平台要求

- **操作系统**: HarmonyOS

- **最低版本**: API 9+

- **开发工具**: DevEco Studio 4.0+

---

## 🚀 集成步骤

> ⚠️ **注意**: 暂时只适配主工程集成

> 下载安装 ohpm i bank_har

### 1. 导入模块

将 `bankCardLibrary` module 导入到工程中

```

your-project/

├── entry/

├── bankCardLibrary/        ← 导入此模块

└── oh-package.json5

```

### 2. 添加依赖

在 `oh-package.json5` 的 `dependencies` 中添加:

```json

{

  "dependencies": {

    "bankCardLibrary": "file:../bankCardLibrary"

  }

}

```

### 3. 配置授权文件

复制鸿蒙授权文件 `authmodehar.lsc` 到以下目录:

```

bankCardLibrary/src/main/resources/rawfile/bank/authmodehar.lsc

```

### 4. 配置开发码

在代码中替换开发码:

```typescript

Config.devcode = "YOUR_DEV_CODE_HERE"

```

---

## 📂 主要类说明

### 核心页面

| 文件路径 | 说明 | 功能描述 |

|---------|------|---------|

| `pages/Index.ets` | 项目入口 | 视频识别、导入识别的入口页面 |

| `pages/CameraPage.ets` | 相机页面 | 实时拍摄识别界面 |

| `pages/ResultPage.ets` | 结果显示页面 | 展示识别结果 |

### 核心服务

| 文件路径 | 说明 | 功能描述 |

|---------|------|---------|

| `camera/CameraServer.ets` | 相机服务 | 相机相关设置以及识别调用 |

### 项目结构

```

bankCardLibrary/

├── src/

│   └── main/

│       ├── ets/

│       │   ├── pages/

│       │   │   ├── Index.ets              # 入口页面

│       │   │   ├── CameraPage.ets         # 相机页面

│       │   │   └── ResultPage.ets         # 结果页面

│       │   ├── camera/

│       │   │   └── CameraServer.ets       # 相机服务

│       │   └── config/

│       │       └── Config.ets             # 配置类

│       └── resources/

│           └── rawfile/

│               └── bank/

│                   └── authmodehar.lsc    # 授权文件

└── oh-package.json5

```

---

## ⚙️ 识别服务设置

### 基本配置

```typescript

import { Config } from 'bankCardLibrary'

// 设置开发码

Config.devcode = "YOUR_DEV_CODE"

// 启动识别

// 详见 pages/Index.ets

```

### 使用示例

```typescript

import { CameraServer } from 'bankCardLibrary'

// 1. 视频识别

router.pushUrl({

  url: 'pages/CameraPage'

})

// 2. 导入图片识别

// 详见 pages/Index.ets 实现

```

---

## ⚠️ 错误码说明

### 授权相关错误

| 错误码 | 说明 | 解决方案 |

|-------|------|---------|

| `-10401` | 授权文件未找到 | 检查 `authmodehar.lsc` 是否放置在正确目录 |

| `-10601` | 开发码错误 | 检查 `Config.devcode` 是否正确 |

| `-10602` | bundleName错误 | 确保 bundleName 与授权文件中绑定的信息匹配 |

| `-10603` | 授权过期 | 联系服务提供商更新授权文件 |

| `-10604` | 核心版本号错误 | 检查SDK版本是否与授权匹配 |

| `-10605` | 项目名称错误 | 检查项目名称配置 |

| `-10606` | 公司名称错误 | 检查公司名称配置 |

| `-10608` | 未找到company_name | 配置文件中添加 company_name |

| `-10610` | 版本号文件未找到 | 检查版本配置文件 |

| `-10611` | 其他错误 | 查看详细日志信息 |

| `-10612` | 未匹配到授权类型 | 检查授权类型配置 |

| `-10613` | 非鸿蒙授权 | 使用正确的鸿蒙授权文件 |

| `-10701` | libraryName未找到 | 检查库名称配置 |

### 错误处理示例

```typescript

import { Config } from 'bankCardLibrary'

Config.resultCallback = (result) => {

  if (result.errorCode) {

    switch (result.errorCode) {

      case -10401:

        console.error('授权文件未找到')

        break

      case -10601:

        console.error('开发码错误')

        break

      case -10603:

        console.error('授权已过期')

        break

      default:

        console.error('识别失败:', result.errorCode)

    }

  } else {

    console.info('识别成功:', result)

  }

}

```

---

## 🔧 可选功能

### 自定义回调配置

```typescript

import { Config } from 'bankCardLibrary'

// 1. 自定义相机返回处理

Config.backCallback = () => {

  console.info('用户点击返回按钮')

  // 自定义返回逻辑

  router.back()

}

// 2. 自定义处理扫描结果

Config.resultCallback = (result) => {

  console.info('识别结果:', JSON.stringify(result))

  

  if (result.errorCode) {

    // 处理错误

    promptAction.showToast({

      message: `识别失败: ${result.errorCode}`

    })

  } else {

    // 处理成功结果

    const cardInfo = {

      cardNumber: result.cardNumber,      // 卡号

      bankName: result.bankName,          // 银行名称

      bankCode: result.bankCode,          // 银行代码

      cardType: result.cardType,          // 卡片类型

      validDate: result.validDate         // 有效期

    }

    

    // 跳转到结果页面或执行其他操作

    router.pushUrl({

      url: 'pages/ResultPage',

      params: { cardInfo }

    })

  }

}

// 3. 自定义权限请求返回结果处理

Config.permissionCallback = (granted: boolean) => {

  if (!granted) {

    console.warn('用户拒绝了相机权限')

    promptAction.showDialog({

      title: '需要相机权限',

      message: '识别银行卡需要使用相机权限',

      buttons: [

        { text: '取消' },

        { text: '去设置' }

      ]

    })

  }

}

```

### 完整使用示例

```typescript

import { Config, CameraServer } from 'bankCardLibrary'

import router from '@ohos.router'

import promptAction from '@ohos.promptAction'

@Entry

@Component

struct BankCardDemo {

  

  aboutToAppear() {

    // 配置SDK

    this.setupSDK()

  }

  

  setupSDK() {

    // 1. 设置开发码

    Config.devcode = "YOUR_DEV_CODE"

    

    // 2. 配置回调

    Config.resultCallback = this.handleResult.bind(this)

    Config.backCallback = this.handleBack.bind(this)

    Config.permissionCallback = this.handlePermission.bind(this)

  }

  

  handleResult(result: any) {

    if (result.errorCode) {

      promptAction.showToast({

        message: `识别失败: ${result.errorCode}`

      })

    } else {

      console.info('识别成功:', result.cardNumber)

      // 处理识别结果

    }

  }

  

  handleBack() {

    router.back()

  }

  

  handlePermission(granted: boolean) {

    if (!granted) {

      promptAction.showToast({

        message: '需要相机权限才能识别银行卡'

      })

    }

  }

  

  startScan() {

    // 启动相机识别

    router.pushUrl({

      url: 'pages/CameraPage'

    })

  }

  

  build() {

    Column() {

      Button('扫描银行卡')

        .onClick(() => this.startScan())

    }

  }

}

```

## 📄 许可证

本SDK为商业软件,使用前请确保已获得有效授权。

Copyright © 2024. All rights reserved.

---

## ⚡ 快速开始

```bash

# 1. 克隆项目

git clone your-project-url

# 2. 导入 bankCardLibrary 模块

# 3. 配置 oh-package.json5

{

  "dependencies": {

    "bankCardLibrary": "file:../bankCardLibrary"

  }

}

# 4. 添加授权文件

# 复制 authmodehar.lsc 到 

# bankCardLibrary/src/main/resources/rawfile/bank/

# 5. 配置开发码

Config.devcode = "YOUR_DEV_CODE"

# 6. 运行项目

hvigorw assembleHap

```

---

## 🎯 常见问题

### Q1: 授权文件放在哪里?

A: 放在 `bankCardLibrary/src/main/resources/rawfile/bank/authmodehar.lsc`

### Q2: 如何获取开发码?

A: 联系SDK提供商获取专属开发码

### Q3: 支持哪些银行卡?

A: 支持所有标准格式的储蓄卡和信用卡(15-19位卡号)

### Q4: 识别准确率如何?

A: 在良好光线条件下,识别准确率可达 98% 以上

### Q5: 是否支持离线识别?

A: 是的,本SDK支持完全离线识别

---

**最后更新**: 2024年07月03日
