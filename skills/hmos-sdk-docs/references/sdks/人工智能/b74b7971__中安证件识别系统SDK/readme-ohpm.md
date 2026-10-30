> 来源: ohpm 中央仓 README(T1 信源) | 包: `idcard_har` | ohpm 最新版: 1.0.0 | 抓取: 2026-07-16
> 注意: 版本可能比市场快照新,以此为准时核对 CHANGELOG

# 鸿蒙证件SDK开发文档

[![文档版本](https://img.shields.io/badge/版本-1.0.0-blue.svg)](https://github.com)

[![SDK版本](https://img.shields.io/badge/SDK-6.8.2.0-green.svg)](https://github.com)

[![HarmonyOS](https://img.shields.io/badge/HarmonyOS-SDK-orange.svg)](https://developer.harmonyos.com)

[![License](https://img.shields.io/badge/license-Commercial-red.svg)](LICENSE)

> **起草时间**: 2024年04月  

> **最新更新**: 2024年07月

---

## 📋 目录

- [基本说明](#基本说明)

- [功能特性](#功能特性)

- [平台要求](#平台要求)

- [集成步骤](#集成步骤)

- [主要类说明](#主要类说明)

- [识别服务设置](#识别服务设置)

- [错误码说明](#错误码说明)

- [可选功能](#可选功能)

- [使用示例](#使用示例)

- [版本历史](#版本历史)

- [常见问题](#常见问题)

---

## 📖 基本说明

本开发包是专为鸿蒙(HarmonyOS)系统设计的**二代身份证识别SDK**,提供高效、准确的身份证信息识别服务。

### 核心能力

- 🎥 **实时扫描识别**: 通过相机实时扫描身份证

- 📷 **图片导入识别**: 支持从相册或文件系统导入身份证图片进行识别

- 🔍 **高精度识别**: 采用先进的OCR技术,识别准确率高

- ⚡ **离线识别**: 完全离线处理,保护用户隐私

- 🛡️ **安全可靠**: 授权机制保障SDK安全使用

---

## ✨ 功能特性

### 支持识别的信息

- ✅ **姓名**: 身份证持有人姓名

- ✅ **性别**: 男/女

- ✅ **民族**: 民族信息

- ✅ **出生日期**: YYYY-MM-DD格式

- ✅ **住址**: 详细住址信息

- ✅ **身份证号码**: 18位身份证号

- ✅ **签发机关**: 证件签发机关(背面)

- ✅ **有效期限**: 证件有效期(背面)

### 识别模式

| 模式 | 说明 | 使用场景 |

|------|------|---------|

| 📹 **视频识别** | 实时相机扫描 | 现场采集身份证信息 |

| 🖼️ **导入识别** | 从相册/文件导入 | 已拍摄的身份证照片识别 |

---

## 🖥️ 平台要求

- **操作系统**: HarmonyOS

- **最低API等级**: API 9+

- **开发工具**: DevEco Studio 4.0+

- **语言**: ArkTS / TypeScript

- **架构支持**: ARM64

---

## 🚀 集成步骤

> ⚠️ **注意**: 当前版本暂时只适配主工程集成

> 下载安装 ohpm i idcard_har

### 步骤1️⃣: 导入模块

将 `idCardLibrary` module 导入到工程中

```

your-project/

├── entry/

├── idCardLibrary/          ← 导入此模块

└── oh-package.json5

```

### 步骤2️⃣: 添加依赖

在项目根目录的 `oh-package.json5` 中的 `dependencies` 添加:

```json

{

  "dependencies": {

    "idCardLibrary": "file:../idCardLibrary"

  }

}

```

### 步骤3️⃣: 配置授权文件

复制鸿蒙授权文件 `authmodehar.lsc` 到以下目录:

```

idCardLibrary/src/main/resources/rawfile/idcard/authmodehar.lsc

```

> 📌 **重要提示**: 授权文件路径必须完全正确,否则会导致授权失败

### 步骤4️⃣: 配置开发码

在代码中替换开发码:

```typescript

import { Config } from 'idCardLibrary'

Config.devcode = "YOUR_DEVELOPER_CODE_HERE"

```

### 步骤5️⃣: 同步依赖

```bash

# 在终端执行

hvigorw clean

hvigorw assembleHap

```

---

## 📂 主要类说明

### 核心文件结构

```

idCardLibrary/

├── src/

│   └── main/

│       ├── ets/

│       │   ├── pages/

│       │   │   ├── Index.ets              # 入口页面

│       │   │   ├── CameraPage.ets         # 相机页面

│       │   │   └── ResultPage.ets         # 结果页面

│       │   ├── camera/

│       │   │   └── CameraServer.ets       # 相机服务

│       │   ├── config/

│       │   │   └── Config.ets             # 配置类

│       │   └── utils/

│       │       └── OCRUtils.ets           # OCR工具类

│       └── resources/

│           └── rawfile/

│               └── idcard/

│                   └── authmodehar.lsc    # 授权文件

└── oh-package.json5

```

### 主要类详细说明

| 文件路径 | 类名/作用 | 功能描述 |

|---------|----------|---------|

| `pages/Index.ets` | 入口页面 | 提供视频识别、导入识别两种入口 |

| `pages/CameraPage.ets` | 相机页面 | 实时相机拍摄界面,支持身份证框引导 |

| `pages/ResultPage.ets` | 结果页面 | 展示识别结果,包含所有字段信息 |

| `camera/CameraServer.ets` | 相机服务 | 相机初始化、参数配置、识别调用 |

| `config/Config.ets` | 配置类 | SDK全局配置,开发码、回调设置 |

---

## ⚙️ 识别服务设置

### 基本配置

```typescript

import { Config } from 'idCardLibrary'

// 必需:设置开发码

Config.devcode = "YOUR_DEVELOPER_CODE"

// 可选:配置回调函数

Config.resultCallback = (result) => {

  console.info('识别结果:', JSON.stringify(result))

}

Config.backCallback = () => {

  console.info('用户点击返回')

}

Config.permissionCallback = (granted) => {

  console.info('权限请求结果:', granted)

}

```

### 启动识别

#### 方式1: 视频识别

```typescript

import router from '@ohos.router'

// 跳转到相机页面

router.pushUrl({

  url: 'pages/CameraPage',

  params: {

    cardType: 'front'  // 'front': 正面, 'back': 反面

  }

})

```

#### 方式2: 导入图片识别

```typescript

import { photoAccessHelper } from '@kit.MediaLibraryKit'

import { OCRUtils } from 'idCardLibrary'

// 选择图片

const photoSelectOptions = new photoAccessHelper.PhotoSelectOptions()

photoSelectOptions.MIMEType = photoAccessHelper.PhotoViewMIMETypes.IMAGE_TYPE

photoSelectOptions.maxSelectNumber = 1

const photoViewPicker = new photoAccessHelper.PhotoViewPicker()

const result = await photoViewPicker.select(photoSelectOptions)

if (result.photoUris.length > 0) {

  // 识别图片

  const recognizeResult = await OCRUtils.recognizeIdCard(result.photoUris[0])

  console.info('识别结果:', recognizeResult)

}

```

---

## ⚠️ 错误码说明

### 授权相关错误

| 错误码 | 说明 | 解决方案 |

|-------|------|---------|

| `-10401` | 授权文件未找到 | 检查 `authmodehar.lsc` 是否存在于 `rawfile/idcard/` 目录 |

| `-10601` | 开发码错误 | 核对 `Config.devcode` 是否正确 |

| `-10602` | bundleName错误 | 确保 `module.json5` 中的 bundleName 与授权文件匹配 |

| `-10603` | 授权过期 | 联系服务商更新授权文件 |

| `-10604` | 核心版本号错误 | SDK版本与授权文件不匹配,检查版本兼容性 |

| `-10605` | 项目名称错误 | 检查项目名称配置 |

| `-10606` | 公司名称错误 | 检查公司名称配置 |

| `-10608` | 未找到company_name | 在配置文件中添加 company_name 字段 |

| `-10610` | 版本号文件未找到 | 检查SDK版本配置文件 |

| `-10611` | 其他错误 | 查看详细日志,联系技术支持 |

| `-10612` | 未匹配到授权类型 | 检查授权类型配置 |

| `-10613` | 非鸿蒙授权 | 使用鸿蒙专用授权文件 |

| `-10701` | libraryName未找到 | 检查库名称配置 |

### 错误处理完整示例

```typescript

import { Config } from 'idCardLibrary'

import promptAction from '@ohos.promptAction'

Config.resultCallback = (result) => {

  if (result.errorCode) {

    let errorMsg = '识别失败'

    

    switch (result.errorCode) {

      case -10401:

        errorMsg = '授权文件未找到,请联系技术支持'

        break

      case -10601:

        errorMsg = '开发码错误,请检查配置'

        break

      case -10602:

        errorMsg = 'Bundle名称不匹配,请检查授权文件'

        break

      case -10603:

        errorMsg = '授权已过期,请更新授权文件'

        break

      case -10604:

        errorMsg = 'SDK版本不匹配'

        break

      default:

        errorMsg = `识别错误: ${result.errorCode}`

    }

    

    promptAction.showToast({

      message: errorMsg,

      duration: 2000

    })

    

    console.error('识别错误:', result.errorCode, errorMsg)

  } else {

    // 识别成功

    console.info('识别成功')

    handleSuccessResult(result)

  }

}

function handleSuccessResult(result: any) {

  // 处理识别成功的结果

  const idCardInfo = {

    name: result.name,              // 姓名

    gender: result.gender,          // 性别

    nation: result.nation,          // 民族

    birthDate: result.birthDate,    // 出生日期

    address: result.address,        // 住址

    idNumber: result.idNumber,      // 身份证号

    authority: result.authority,    // 签发机关(背面)

    validPeriod: result.validPeriod // 有效期(背面)

  }

  

  console.info('身份证信息:', JSON.stringify(idCardInfo))

}

```

---

## 🔧 可选功能

### 1. 自定义相机返回处理

```typescript

import { Config } from 'idCardLibrary'

import router from '@ohos.router'

Config.backCallback = () => {

  console.info('用户点击返回按钮')

  

  // 自定义返回逻辑

  router.back({

    url: 'pages/Index'

  })

  

  // 或者显示确认对话框

  // showExitConfirmDialog()

}

```

### 2. 自定义处理扫描结果

```typescript

import { Config } from 'idCardLibrary'

import router from '@ohos.router'

import promptAction from '@ohos.promptAction'

Config.resultCallback = (result) => {

  if (result.errorCode) {

    // 处理错误

    promptAction.showToast({

      message: `识别失败: ${getErrorMessage(result.errorCode)}`

    })

    return

  }

  

  // 识别成功

  console.info('识别结果:', JSON.stringify(result))

  

  // 跳转到自定义结果页面

  router.pushUrl({

    url: 'pages/CustomResultPage',

    params: {

      idCardData: result

    }

  })

  

  // 或者直接处理数据

  saveIdCardInfo(result)

}

function getErrorMessage(errorCode: number): string {

  const errorMap = {

    '-10401': '授权文件未找到',

    '-10601': '开发码错误',

    '-10603': '授权已过期',

    // ... 更多错误码

  }

  return errorMap[errorCode] || `未知错误: ${errorCode}`

}

async function saveIdCardInfo(data: any) {

  // 保存到数据库或发送到服务器

  try {

    // await database.save(data)

    console.info('身份证信息已保存')

  } catch (error) {

    console.error('保存失败:', error)

  }

}

```

### 3. 自定义权限请求返回结果处理

```typescript

import { Config } from 'idCardLibrary'

import promptAction from '@ohos.promptAction'

import common from '@ohos.app.ability.common'

import abilityAccessCtrl from '@ohos.abilityAccessCtrl'

Config.permissionCallback = (granted: boolean) => {

  if (!granted) {

    console.warn('用户拒绝了相机权限')

    

    // 显示权限说明对话框

    promptAction.showDialog({

      title: '需要相机权限',

      message: '识别身份证需要使用相机权限,请在设置中开启',

      buttons: [

        { text: '取消', color: '#999999' },

        { text: '去设置', color: '#007DFF' }

      ]

    }).then((result) => {

      if (result.index === 1) {

        // 跳转到应用设置页面

        openAppSettings()

      }

    })

  } else {

    console.info('相机权限已授予')

  }

}

function openAppSettings() {

  const context = getContext(this) as common.UIAbilityContext

  const bundleInfo = context.applicationInfo

  

  // 跳转到应用设置

  context.startAbility({

    bundleName: 'com.huawei.hmos.settings',

    abilityName: 'com.huawei.hmos.settings.MainAbility',

    uri: `application_info_entry://com.huawei.hmos.settings/application_info_entry?bundle=${bundleInfo.name}`

  })

}

```

---

## 💡 使用示例

### 完整示例: 身份证识别应用

```typescript

import { Config } from 'idCardLibrary'

import router from '@ohos.router'

import promptAction from '@ohos.promptAction'

@Entry

@Component

struct IdCardRecognitionDemo {

  @State idCardData: any = null

  @State isScanning: boolean = false

  

  aboutToAppear() {

    this.setupSDK()

  }

  

  setupSDK() {

    // 1. 设置开发码

    Config.devcode = "YOUR_DEVELOPER_CODE"

    

    // 2. 配置回调

    Config.resultCallback = this.handleResult.bind(this)

    Config.backCallback = this.handleBack.bind(this)

    Config.permissionCallback = this.handlePermission.bind(this)

  }

  

  handleResult(result: any) {

    this.isScanning = false

    

    if (result.errorCode) {

      promptAction.showToast({

        message: `识别失败: ${result.errorCode}`

      })

      return

    }

    

    // 识别成功

    this.idCardData = result

    console.info('识别成功:', JSON.stringify(result))

    

    promptAction.showToast({

      message: '识别成功'

    })

  }

  

  handleBack() {

    this.isScanning = false

    router.back()

  }

  

  handlePermission(granted: boolean) {

    if (!granted) {

      promptAction.showDialog({

        title: '需要相机权限',

        message: '识别身份证需要使用相机权限'

      })

    }

  }

  

  // 启动相机扫描(正面)

  scanFrontSide() {

    this.isScanning = true

    router.pushUrl({

      url: 'pages/CameraPage',

      params: {

        cardType: 'front'

      }

    })

  }

  

  // 启动相机扫描(反面)

  scanBackSide() {

    this.isScanning = true

    router.pushUrl({

      url: 'pages/CameraPage',

      params: {

        cardType: 'back'

      }

    })

  }

  

  // 从相册导入

  async importFromGallery() {

    // 实现图片选择逻辑

    // ...

  }

  

  build() {

    Column() {

      // 标题

      Text('身份证识别')

        .fontSize(24)

        .fontWeight(FontWeight.Bold)

        .margin({ top: 20, bottom: 30 })

      

      // 功能按钮

      Button('扫描身份证正面')

        .width('80%')

        .height(50)

        .onClick(() => this.scanFrontSide())

        .enabled(!this.isScanning)

      

      Button('扫描身份证反面')

        .width('80%')

        .height(50)

        .margin({ top: 15 })

        .onClick(() => this.scanBackSide())

        .enabled(!this.isScanning)

      

      Button('从相册导入')

        .width('80%')

        .height(50)

        .margin({ top: 15 })

        .onClick(() => this.importFromGallery())

        .backgroundColor('#52c41a')

      

      // 显示识别结果

      if (this.idCardData) {

        Divider()

          .margin({ top: 30, bottom: 20 })

        

        Text('识别结果')

          .fontSize(20)

          .fontWeight(FontWeight.Bold)

        

        Column() {

          this.buildResultItem('姓名', this.idCardData.name)

          this.buildResultItem('性别', this.idCardData.gender)

          this.buildResultItem('民族', this.idCardData.nation)

          this.buildResultItem('出生日期', this.idCardData.birthDate)

          this.buildResultItem('住址', this.idCardData.address)

          this.buildResultItem('身份证号', this.idCardData.idNumber)

          

          if (this.idCardData.authority) {

            this.buildResultItem('签发机关', this.idCardData.authority)

          }

          if (this.idCardData.validPeriod) {

            this.buildResultItem('有效期限', this.idCardData.validPeriod)

          }

        }

        .width('90%')

        .backgroundColor('#f5f5f5')

        .borderRadius(10)

        .padding(15)

        .margin({ top: 20 })

      }

    }

    .width('100%')

    .height('100%')

    .padding(20)

  }

  

  @Builder

  buildResultItem(label: string, value: string) {

    Row() {

      Text(label + ':')

        .fontSize(16)

        .fontColor('#666666')

        .width(100)

      

      Text(value || '-')

        .fontSize(16)

        .fontColor('#333333')

        .layoutWeight(1)

    }

    .width('100%')

    .margin({ bottom: 10 })

  }

}

```

---

 

## 🎯 常见问题

### Q1: 授权文件应该放在哪里?

**A**: 授权文件 `authmodehar.lsc` 必须放在以下路径:

```

idCardLibrary/src/main/resources/rawfile/idcard/authmodehar.lsc

```

注意路径是 `rawfile` 不是 `rewfile`(文档中可能有拼写错误)

### Q2: 如何获取开发码?

**A**: 联系SDK提供商获取专属开发码,每个应用对应一个唯一的开发码。

### Q3: 识别准确率如何?

**A**: 在以下条件下,识别准确率可达 99% 以上:

- 光线充足

- 身份证摆放平整

- 镜头对焦清晰

- 身份证无严重污损

### Q4: 是否支持离线识别?

**A**: 是的,本SDK完全支持离线识别,无需网络连接。

### Q5: 支持识别哪些证件?

**A**: 当前版本仅支持中国大陆二代身份证(正反面)。

### Q6: 能否同时识别多张身份证?

**A**: 当前版本暂不支持批量识别,需要逐张识别。

### Q7: 识别速度如何?

**A**: 单张身份证识别通常在 1-3 秒内完成(视设备性能而定)。

### Q8: 遇到 -10602 错误怎么办?

**A**: 检查以下内容:

1. `module.json5` 中的 `bundleName`

2. 授权文件是否与当前 bundleName 匹配

3. 联系服务商重新申请授权文件

### Q9: 如何处理光线不足的情况?

**A**: 可以在 `CameraPage` 中开启闪光灯功能,或提示用户移至光线充足的地方。

### Q10: 识别结果包含哪些字段?

**A**: 识别结果包含以下字段:

- **正面**: 姓名、性别、民族、出生日期、住址、身份证号

- **反面**: 签发机关、有效期限

---

## 📱 应用场景

### 适用场景

- ✅ 金融App实名认证

- ✅ 政务服务身份核验

- ✅ 酒店入住登记

- ✅ 票务实名购买

- ✅ 企业员工信息录入

- ✅ 在线教育实名注册

---

## 🔒 安全与隐私

### 数据安全

- 🔐 **离线处理**: 所有识别过程在本地完成,不上传用户数据

- 🛡️ **授权机制**: 采用授权文件+开发码双重验证

- 🔑 **数据加密**: 敏感信息建议加密存储

- 📝 **合规性**: 符合《个人信息保护法》相关要求

### 最佳实践

```typescript

// 1. 识别后立即清除敏感数据

Config.resultCallback = (result) => {

  if (!result.errorCode) {

    // 使用完数据后立即清除

    const tempData = { ...result }

    processIdCardData(tempData)

    

    // 清除内存中的敏感数据

    result = null

  }

}

// 2. 加密存储身份证信息

import cryptoFramework from '@ohos.security.cryptoFramework'

async function encryptAndSave(idCardData: any) {

  // 使用AES加密

  const encrypted = await encryptData(JSON.stringify(idCardData))

  // 存储加密后的数据

  await saveToDatabase(encrypted)

}

// 3. 添加水印或时间戳

function addWatermark(idCardData: any) {

  return {

    ...idCardData,

    timestamp: Date.now(),

    source: 'mobile_sdk'

  }

}

```

---

## 🔧 高级配置

### 性能优化

```typescript

// 1. 预加载SDK

import { Config, OCRUtils } from 'idCardLibrary'

// 在应用启动时初始化

export default class EntryAbility extends UIAbility {

  onCreate() {

    // 预加载OCR模型

    OCRUtils.preloadModel()

    Config.devcode = "YOUR_CODE"

  }

}

// 2. 内存管理

Config.resultCallback = (result) => {

  // 处理完立即释放大对象

  if (result.imageData) {

    processImage(result.imageData)

    result.imageData = null  // 释放图片数据

  }

}

// 3. 相机参数优化

// 在 CameraServer.ets 中调整

const cameraConfig = {

  resolution: '1920x1080',  // 根据需求调整

  focusMode: 'continuous',  // 连续对焦

  exposureMode: 'auto'      // 自动曝光

}

```

---

---

## 📄 许可证

本SDK为商业软件,使用前请确保已获得有效授权。

Copyright © 2025. All rights reserved.

---

## ⚡ 快速开始指南

```bash

# 1. 克隆或下载项目

git clone your-project-url

# 2. 导入 idCardLibrary 模块到项目

# 3. 配置 oh-package.json5

{

  "dependencies": {

    "idCardLibrary": "file:../idCardLibrary"

  }

}

# 4. 添加授权文件

# 复制 authmodehar.lsc 到 

# idCardLibrary/src/main/resources/rawfile/idcard/

# 5. 配置开发码

# 在代码中设置

Config.devcode = "YOUR_DEVELOPER_CODE"

# 6. 同步项目

hvigorw clean

# 7. 编译运行

hvigorw assembleHap

```

---

## ⚙️ 系统权限

### 必需权限

在 `module.json5` 中添加:

```json

{

  "module": {

    "requestPermissions": [

      {

        "name": "ohos.permission.CAMERA",

        "reason": "$string:camera_permission_reason",

        "usedScene": {

          "abilities": ["EntryAbility"],

          "when": "inuse"

        }

      },

      {

        "name": "ohos.permission.READ_MEDIA",

        "reason": "$string:media_permission_reason",

        "usedScene": {

          "abilities": ["EntryAbility"],

          "when": "inuse"

        }

      }

    ]

  }

}

```

---

**最后更新**: 2024年07月03日

**文档维护**: SDK开发团队

**反馈与建议**: 欢迎通过 Issue 或邮件提供反馈
