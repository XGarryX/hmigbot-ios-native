PDBox SDK 使用指南 

HarmonyOS 应用集成文档 

OHPM 包名: @gkhos/pdboxservice 

# **1.** 概述 

本指南说明如何在 HarmonyOS 应用中集成 PDBox SDK ,主要内容包 括: 

源码: src/main/ets/sdk/PDBoxService.ts 

示例工程: test/devicetest 

OHPM 三方库中心仓: @gkhos/pdboxservice 

更细的逐接口参数与错误码见同目录 PDBoxService-API.docx ;安装 与集成条目见仓库根目录 README.docx 。 

项 

说明 

SDK 名称 

PDBox SDK 

软件包名( OHPM ) 

@gkhos/pdboxservice 

开源许可 

Apache-2.0 

作者 

gkhos 

# **2.** 环境与兼容性 

项 

说明 

SDK 类型 

HarmonyOS 侧应用集成 

USB 外设 

需支持 SystemCapability.Driver.ExternalDevice 相机类权限 

需在 module.json5 等配置中声明并动态申请 ohos.permission.CAMERA 

人脸 / 活体依赖 

包依赖 iv_live_ohos (中心仓会随本包解析) 

# **3.** 安装依赖 

## **3.1** 从中心仓安装(推荐) 

在工程根目录或 HAP 模块目录执行: 

ohpm install @gkhos/pdboxservice 

简写命令: 

ohpm i @gkhos/pdboxservice 

成功后对应模块的 oh-package.json5 会出现依赖项,再执行: 

ohpm install 

拉全量依赖树。 

## **3.2** 本地源码依赖(调试用) 

在 oh-package.json5 中写 file: 指向本仓 sdk/pdboxservice 路径(详 见 README.docx )。 

# **4.** 核心概念 

概念 

说明 

单例 PDBoxService 

getInstance(context) 获取唯一实例,并登记 Context 

支持列表 

getSupportDevices() :配置里声明过、可作为品类展示的设备定义 

当前列表 

getCurrentDevices() :当前已枚举到的 USB 设备 

### 异步初始化 

首次 getInstance 后会异步加载配置、枚举 USB ;首帧列表可能为空 

device.api 

open 成功后挂载: USB 类为 IDL 代理,人脸 / 高拍仪为相机服务 

### 热插拔 

通过公共事件 pdboxservice.driver.event.state 上报;用 on(connectState, ...) 封装 

# **5.** 推荐集成步骤 

## 步骤 **1** :在页面或 **Ability** 中取单例 

import { PDBoxService } from '@gkhos/pdboxservice'; 

```arkts
import { common } from '@kit.AbilityKit'; 
```

const ctx = this.getUIContext().getHostContext() as common.UIAbilityContext; 

const pdbox = PDBoxService.getInstance(ctx); 

## **2** 步骤 :需要列表时先刷新(可选但推荐) 

await pdbox.refresh(); 

const supported = pdbox.getSupportDevices(); 

const connected = pdbox.getCurrentDevices(); 

## **3** 步骤 :打开设备并调用业务能力 

const device = await pdbox.open(NameCommon. 某品类 , 型号可选 , params 可选 ); 

// USB: device.api 为 IdCardReader / PrinterServiceProxy 等 

// 人脸 / 高拍仪 : device.api 为 CameraService / DocumentScannerCameraService 

## **4** 步骤 :释放 

单品类: close(device) (高拍仪等宜先 device.api.releaseCamera() 再 close ) 进程级退出: release() (会 off 、 close 全部并清空内部列表) 

# **6.** 典型场景与示例 

## **6.1 +** 设备列表 插拔刷新 

参考: test/devicetest/.../DeviceList.ets 

aboutToAppear : on(connectState, (state, info) => { 

refresh().then(...); }) 

aboutToDisappear : off(connectState) 

首次可用 setTimeout 短延迟再 refreshDeviceList() 

## **6.2** 身份证读卡器(多型号) 

参考: IDCardTestPage.ets 

open(NameCommon.ID_CARD_READER, ModelCommon.MT625) 

device.api.read(timeout, callback) ,结果类型 IDCardInfo 

## **6.3** 小票打印机 

参考: TicketPrinterTestPage.ets 

open(NameCommon.RECEIPT_PRINTER) (单型号场景可省略 model ) 

## **6.4** 指纹仪 

参考: FingerprintScannerTestPage.ets 

open(NameCommon.FINGERPRINT_SCANNER) 

## **6.5 +** 人脸识别 活体 

参考: CameraPreview.ets 、 CameraTestPage.ets 

open(NameCommon.FACIAL_RECOGNITION, undefined, JSON.stringify({ width: 640, height: 480 })) 

流程: requestCameraPermission → initCamera → startPreview → LiveManager.getInstance(context).feedCameraData(...) 

## **6.6** 高拍仪 **/** 文档扫描 

参考: DocumentScannerTestPage.ets 

open(NameCommon.DOCUMENT_SCANNER, undefined, JSON.stringify({ width, height })) 

关闭:先 releaseCamera() ,再 PDBoxService.getInstance(ctx).close(device) 

# **7. open** 参数小结 

参数 必填 

说明 

name 

是 

NameCommon ,如 ID_CARD_READER 、 RECEIPT_PRINTER 、 FACIAL_RECOGNITION 、 DOCUMENT_SCANNER 

model 

视品类 

多型号必填;单型号可省略 

params 

否 

仅人脸 / 高拍仪常用: JSON 字符串,含分辨率等 

# **8.** 与宿主 **Entry** 共存( **PDBox USB** ) 

若宿主 Entry 已对 PDBox 设备执行 USB 绑定,为避免重复绑定导致 原生层异常, Entry 可在全局设置: 

globalThis['com.gkhos.pdbox.entryBound'] = true 

未设置时, SDK 仍会在满足条件时自行完成 PDBox 认证路径;无设 备时不绑定。 

# **9.** 常见问题( **FAQ** ) 

现象 

建议 

getCurrentDevices() 一直为空 

是否真机、是否具备 ExternalDevice ;稍后再 refresh() ;确认 USB 已插入 

open 报找不到设备 

先 refresh() ;核对 name/model 与列表中 info 是否一致 

相机黑屏 / 无预览 

权限、 Surface/XComponent 是否就绪;高拍仪需在合适时机调用 startPreview 

# **10.** 文档与源码索引 

资源 

路径 / 链接 

OHPM 详情 

https://ohpm.openharmony.cn/#/cn/detail/ @gkhos%2Fpdboxservice 

SDK 个人信息处理规则 

http://gkhos.com:8809/privacy_policy.html 

SDK 合规使用指南 

PDBoxService-SDK 合规使用指南 .docx 

接口文档 

sdk/pdboxservice/docs/PDBoxService-API.docx 

示例应用 

仓库 test/devicetest 

服务入口源码 

sdk/pdboxservice/src/main/ets/sdk/PDBoxService.ts
