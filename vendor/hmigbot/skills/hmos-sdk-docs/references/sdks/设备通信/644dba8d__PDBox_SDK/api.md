PDBoxService 接口文档 

API Reference — ArkTS 集成指南 

OHPM 包名: @gkhos/pdboxservice 

# 概述 

本文档依据 src/main/ets/sdk/PDBoxService.ts 实现,并与 test/ devicetest 调用方式对齐。适用于宿主在 ArkTS 中集成 @gkhos/ pdboxservice 。 

SDK 名称: PDBox SDK ;公共事件名(驱动状态): pdboxservice.driver.event.state 

合规与权限:本 SDK 不直接向用户申请系统权限。宿主须在 module.json5 声明并向系统申请。典型权限: 

ohos.permission.CAMERA (相机) — 人脸 FACIAL_RECOGNITION 、高拍仪 DOCUMENT_SCANNER 

DDK / USB 外设 — refresh/open 中非相机路径的 USB 枚举与 bindDeviceDriver 

建议:用户同意宿主隐私政策后再调用 getInstance ;在 requestCameraPermission() 通过后再 initCamera / startPreview 。 

# 相关类型 

类型 

说明 

Device<T> 

info: DeviceInfo ; api?: T 为打开成功后注入的代理或相机服务 

DeviceInfo 

vid, pid, name, alias, model, modelAlias, deviceId 

DeviceState 

CONNECT = 0x102, DISCONNECT = 0x103 

SubscribeCallback 

(state: DeviceState, deviceInfo?: DeviceInfo | null) => void 

# **1. getInstance** 

项目 

说明 

接口名称 

PDBoxService.getInstance 

调用方式 静态方法,非异步 

请求参数 

context: Context (通常为 UIAbilityContext ,如 getHostContext() ) 

#### 返回参数 

PDBoxService 单例;多次调用返回同一实例 

import { PDBoxService } from '@gkhos/pdboxservice'; 

```arkts
import { common } from '@kit.AbilityKit'; 
```

const ctx = this.getUIContext().getHostContext() as common.UIAbilityContext; 

const pdbox = PDBoxService.getInstance(ctx); 

# **2. getSupportDevices** 

项目 

说明 

接口名称 

getSupportDevices 

调用方式 实例方法,同步 

请求参数 

无 

#### 返回参数 

Array<Device<any>> :配置中声明的「支持设备」列表 

pdbox.getSupportDevices().forEach((item) => { console.info(item.info.name, item.info.model); 

}); 

# **3. getCurrentDevices** 

项目 说明 

接口名称 

getCurrentDevices 调用方式 实例方法,同步 请求参数 无 返回参数 Array<Device<any>> :当前 USB 枚举并映射成功的设备 

# **4. refresh** 

项目 说明 接口名称 refresh 

调用方式 实例方法,异步 

请求参数 

无 

返回参数 

Promise<void> :完成后内部已重新执行 USB 枚举 

await PDBoxService.getInstance(this.context).refresh(); 

PDBoxService.getInstance(this.context).refresh().then(() => { /* 刷新 UI 列表 */ }); 

# **5. open** 

项目 说明 

接口名称 

open 

调用方式 实例方法,异步 返回参数 

Promise<Device<any>> : resolve 时 device.api 已就绪 

## **5.1** 参数说明 

参数名 

类型 / 必填 

说明 

name 

string / 是 

设备品类,使用 NameCommon ,如 IdCardReader 、 ReceiptPrinter 、 FacialRecognition 、 DocumentScanner 

model 

string / 否 

型号;多型号外设必须匹配 getCurrentDevices() 中 info.model 

params 

string / 否 

JSON 字符串。人脸 / 高拍仪用于分辨率等 

## **5.2 params** 示例 

人脸识别: 

{"width":640,"height":480} 

高拍仪: 

{"width":1920,"height":1080} 

可选字段 "previewFormat":"jpeg" 或 "yuv" 

## **5.3** 调用示例 

### **USB** 外设:身份证 

PDBoxService.getInstance(this.context) 

.open(NameCommon.ID_CARD_READER, ModelCommon.MT625) 

.then((device) => { device.api?.read(10, (code, data) => { ... }); }) 

.catch((err) => { console.error(JSON.stringify(err)); }); 

### **USB** 外设:小票打印机 

.then((device) => { /* device.api */ }); 

### 人脸识别相机 

.then((device) => { this.cameraService = device.api; }); 

### 高拍仪 

```arkts
const params = JSON.stringify({ width: 1920, height: 1080 }); this.device = await PDBoxService.getInstance(this.context).open( NameCommon.DOCUMENT_SCANNER, undefined, params); 
```

## **5.4** 错误码 

code 

含义与典型场景 

-3 

支持设备配置缺失: loadSupportDevices 中 getConfig 得到空字符串 

-5 

未找到设备: currentDevices 中无匹配的 name/model 

-6 

设备断开: USB bindDeviceDriver 断开回调 

-7 

打开流程异常: open 外层 catch , BusinessError 无 code 时的兜底 

其它负数 

驱动或系统错误: bindDeviceDriver 异步失败时 reject , code 为系统 BusinessError.code 

# **6. close** 

项目 说明 

接口名称 

close 

调用方式 

实例方法,异步 

请求参数 

device: Device<any> ;传入 undefined/null 时等价于立即 resolve 返回参数 

Promise<void> 

高拍仪示例(先释放在关闭): 

if (this.device?.api) { 

await (this.device.api as DocumentScannerCameraService).releaseCamera(); 

} 

if (this.device && this.context) { 

await PDBoxService.getInstance(this.context).close(this.device); 

} 

# **7. on** 

项目 说明 接口名称 

on 

调用方式 

实例方法,同步发起异步订阅 

#### 请求参数 

event: string (传 connectState );实现固定监听 pdboxservice.driver.event.state 

#### 回调 

SubscribeCallback : (state, deviceInfo) => void 

this.pdboxService.on('connectState', (state, deviceInfo) => { console.info(`state: ${state}, info: ${JSON.stringify(deviceInfo)}`); this.pdboxService.refresh().then(() => this.refreshDeviceList()); 

}); 

# **8. off** 

项目 说明 接口名称 off 调用方式 实例方法 请求参数 

event: string (与 on 配对使用,测试中为 connectState ) 

PDBoxService.getInstance(this.context).off('connectState'); 

# **9. release** 

项目 说明 

接口名称 

release 

调用方式 实例方法,同步 行为概要 

调用 off(connectState) ,对 currentDevices 逐个 close ,清理资源 / 事 件 / 状态管理器 

PDBoxService.getInstance(this.context).release(); 

# **A DeviceState** 附录 : 数值 

枚举 十六进制 十进制 

DeviceState.CONNECT 

0x102 

258 

DeviceState.DISCONNECT 

0x103 259 

# **B** 附录 :与测试工程对照 

能力 测试文件 列表 + on/off/refresh 

DeviceList.ets 身份证读卡 IDCardTestPage.ets 小票机 TicketPrinterTestPage.ets 指纹 

FingerprintScannerTestPage.ets 人脸预览与活体 CameraPreview.ets 、 CameraTestPage.ets 

高拍仪 

DocumentScannerTestPage.ets 

# **C** 附录 :接口与权限申请时机(摘 要) 

接口 / 行为 

合规相关说明 

getInstance 

将触发 initConfig() ,进而可能异步执行 USB 枚举、 authPDBox 等; 建议在用户同意隐私政策后再调用 

refresh/getCurrentDevices 

依赖 ExternalDevice 能力及宿主已声明的外设 /USB 能力 

open ( USB 品类) 

将 bindDeviceDriver ;宿主须具备合法的外设访问能力声明 

open ( FACIAL_RECOGNITION / DOCUMENT_SCANNER ) 

创建相机服务后,在 initCamera/startPreview 前由宿主完成 ohos.permission.CAMERA 授权 

close/release 

回收资源,降低持续采集风险
