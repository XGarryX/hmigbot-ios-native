# 跨平台热敏打印机 SDK

- 市场详情页: https://developer.huawei.com/consumer/cn/market/prod-detail/ffca1bf997714582b58aa8ea8291bc8f/PLATFORM
- 分类: 设备通信 > 办公家居设备
- 版本: 0.7.15(市场快照)
- ohpm 包名: @psdk/frame-father
- 语言: ArkTs
- 提供商: 厦门爱印科技有限公司(zhoujb@aiyin.com)
- 市场更新时间: 2026-05-13 10:01:48
- 简介: 一套设计完备的跨平台热敏打印机 SDK,为移动端和桌面端应用提供统一的打印解决方案。

PSDK (Printer SDK) 是专为热敏打印机设计的开发工具包。它提供了简洁易用的 API,支持多种打印指令协议,并在所有平台上实现了统一的接口命名。

## PSDK介绍

PSDK OpenHarmony SDK 是面向 HarmonyOS/OpenHarmony 应用开发的热敏打印机 SDK,适用于 HarmonyOS NEXT 和 OpenHarmony 应用接入热敏打印能力。SDK 提供统一的打印设备连接、打印指令封装和数据写入接口,开发者可通过 ArkTS/TypeScript 在鸿蒙应用中快速完成标签打印、小票打印、条码打印、二维码打印等功能集成。

SDK 通过 OHPM 发布,包名以 @psdk/ 为前缀,按核心框架、打印指令和设备连接能力拆分,便于开发者按需引入。当前 OpenHarmony 版本支持 CPCL、TSPL、ESC 等主流热敏打印指令协议,并支持 BLE 低功耗蓝牙、经典蓝牙、Wi-Fi 网络、USB 等多种连接方式。

主要能力包括:

  * 热敏打印机连接管理:支持 BLE、经典蓝牙、Wi-Fi、USB 等连接方式。
  * 主流打印指令封装:支持 CPCL 标签打印、TSPL 标签条码打印、ESC 小票打印等协议。
  * 链式打印 API:提供文本、条码、二维码、线条、对齐、加粗、字号、走纸、切纸等常用打印能力。
  * 统一生命周期写入:通过 Lifecycle 和 ConnectedDevice 统一管理设备连接和打印数据发送。
  * 分包发送能力:针对 BLE MTU 限制和大数据量打印任务,支持 enableChunkWrite 与 chunkSize 配置。
  * 中文编码适配:SDK 内部处理打印机常用 GBK 编码转换,降低开发者手动处理编码的成本。
  * 模块化接入:开发者可按业务需要选择 @psdk/cpcl、@psdk/tspl、@psdk/esc、@psdk/ohos-bluetooth-le、@psdk/ohos-bluetooth-classic、@psdk/ohos-network、@psdk/ohos-usb 等包。

## 提供商介绍

厦门爱印科技有限公司是一家专注于打印设备连接、打印协议适配和跨平台打印能力建设的技术服务公司,长期服务于标签打印、小票打印、移动打印、行业终端打印等场景。公司围绕热敏打印机、标签打印机、便携式打印机等硬件生态,持续沉淀多端 SDK、打印指令协议、设备连接适配和示例工程能力,帮助应用开发者快速完成打印能力集成。

厦门爱印科技有限公司具备移动端、桌面端、小程序端和鸿蒙端等多平台 SDK 研发经验,支持 CPCL、TSPL、ESC、ESC/POS 等主流热敏打印指令协议,并覆盖蓝牙、BLE、Wi-Fi、USB 等常见设备连接方式。通过统一 API、模块化包结构和示例项目,降低开发者在不同平台、不同打印机型号和不同指令协议之间的适配成本。

## 核心优势

  * 多协议兼容:支持 CPCL、TSPL、ESC 等主流热敏打印协议,覆盖标签打印、条码打印和小票打印等常见业务场景。
  * 多连接方式:适配 BLE、经典蓝牙、Wi-Fi、USB 等连接方式,满足不同鸿蒙设备和打印机硬件组合的接入需求。
  * 鸿蒙系统适配:基于 HarmonyOS/OpenHarmony 应用开发环境进行适配,可通过 ArkTS/TypeScript 在鸿蒙应用中直接集成。
  * 模块化发布:SDK 通过 OHPM 按功能拆包发布,开发者可根据业务选择核心包、指令包和设备包,避免无关能力引入。
  * 统一编程模型:核心框架、设备连接和打印指令采用统一接口组织,便于在不同连接方式和不同打印协议之间复用业务代码。
  * 大数据量打印支持:提供分包写入能力,可缓解 BLE MTU 限制带来的传输问题,提升复杂标签、图片或长小票打印任务的稳定性。
  * 编码处理内置:SDK 内部处理打印机常用 GBK 编码转换,减少中文打印乱码风险。
  * 示例完整:提供 HarmonyOS Demo 和多语言示例,便于开发者参考设备发现、连接、打印和断开连接等完整流程。

## 约束与限制

在下述版本通过验证:

DevEco Studio版本号| HarmonyOS SDK版本号| 手机操作系统ROM版本号  
---|---|---  
DevEco Studio 4.1| 【API12】HarmonyOS SDK 5.0.0.13(SP4)| 3.0.0.13(SP6DEVC00E13R4P1)  
DevEco Studio 5.0.3.100| 【API12】HarmonyOS SDK 5.0.0.13(SP4)| 3.0.0.13(SP6DEVC00E13R6P1)  
  
其他约束说明:

  * 使用蓝牙能力前,需要在 module.json5 中配置 ohos.permission.ACCESS_BLUETOOTH、ohos.permission.DISCOVER_BLUETOOTH、ohos.permission.MANAGE_BLUETOOTH、ohos.permission.APPROXIMATELY_LOCATION、ohos.permission.INTERNET 等权限,并按系统要求进行运行时授权。
  * 使用 Wi-Fi 网络打印能力前,需要配置 ohos.permission.INTERNET 权限。
  * BLE 传输受 MTU 限制影响,大数据量打印任务建议开启分包写入,例如 psdk.write({ enableChunkWrite: true, chunkSize: 20 })。
  * 不同打印机型号支持的指令协议和蓝牙特征值可能不同,接入时需要根据设备规格选择 CPCL、TSPL 或 ESC 指令,并确认写入特征值、读取特征值和连接方式。
  * SDK 适用于热敏打印机相关场景,不包含打印机硬件驱动固件、云端打印服务或业务系统后台能力。

## 成功案例

PSDK OpenHarmony SDK 已完成 HarmonyOS/OpenHarmony 热敏打印能力适配,并提供完整 HarmonyOS 示例工程,覆盖设备发现、设备连接、打印指令构建、数据写入、分包发送和断开连接等典型流程。

典型落地场景包括:

  * 零售门店小票打印:通过 ESC 指令完成订单明细、合计金额、二维码和切纸等小票打印流程。
  * 商品标签打印:通过 CPCL 或 TSPL 指令完成商品名称、规格、价格、条形码、二维码等标签内容打印。
  * 便携式蓝牙打印:通过 BLE 或经典蓝牙连接便携式热敏打印机,支持移动设备现场打印。
  * 网络打印:通过 Wi-Fi 连接局域网打印机,适用于固定点位打印场景。
  * USB 打印:通过 USB 连接打印设备,适用于稳定连接和固定终端场景。

开发者可参考 HarmonyOS Demo 和 OHPM 包页面完成接入验证:

  * HarmonyOS Demo:https://github.com/prtmax/psdk-examples/tree/main/harmony-demo
  * OHPM 包浏览:https://ohpm.openharmony.cn/#/cn/result?sortedType=relevancy&page=1&q=%2540psdk

## 厂商外站链接(域名白名单素材)

- https://example.com
- https://example.com/product/123
- https://github.com/prtmax/psdk-examples/tree/main/harmony-demo
- https://ohpm.openharmony.cn/#/cn/result?sortedType=relevancy&amp;page=1&amp;q=%2540psdk
- https://shop.example.com
