# 接口文档 

## **DuiAsr SDK** 接口文档 

版本: 1.0.0 (基于提供的代码,可能与实际SDK版本有差异) 

### **DUILiteSDK** 

#### **init:** 初始化 

|参数|说明|是否必填|
|---|---|---|
|context|上下文对象|是|
|debug|是否开启debug模式|否|

let appContext = this.context.getApplicationContext()
DUILiteSDK.init(appContext, DEBUG)
DUILiteSDK.setLogLevel(hilog.LogLevel.DEBUG)

#### **doAuth** 授权 

|参数|说明|是否必填|
|---|---|---|
|config|配置文件|是|
|deviceInfo|设备信息|是|
|authCallback|授权回调|是|
|cleanBefore|清理之前授权文件|否|

let authConfig = new AuthConfigBuilder()
   .setCustomDeviceName(this.deviceName)
   .setAuthServer(AuthManager.AUTH_HOST)
   .build()
let updateConfig = new UploadConfigBuilder()
   .setUploadLogEnable(false)
   .create()
let config = new DuiLiteConfigBuilder(

this.apiKey,
this.productId, //  替换为实际的 productId
this.productKey, //  替换为实际的 productKey
this.productSecret, //  替换为实际的 productSecret
this.deviceName
 ).setAuthConfig(authConfig)
   .setUploadConfig(updateConfig)
   .create()
}
DUILiteSDK.doAuth<DUILiteError>(config, DUILiteSDK.deviceInfo, (result:
DUILiteError) => {
}, cleanBefore);

### **DUILiteConfig** 

##### 配置文件 

参数

是否必填

|参数|说明|是否必填|
|---|---|---|
|authConfig|授权配置文件|是|

#### **AuthConfig** 

|参数|说明|是否必填|
|---|---|---|
|apiKey|集成SDK时需用到的鉴权参数|是|
|productId|集成SDK时需用到的鉴权参数|是|
|productKey|集成SDK时需用到的鉴权参数|是|
|productSecret|集成SDK时需用到的鉴权参数|是|
|deviceName|设备名称|是|

### **CloudASREngine** 

**init** 初始化 

参数

说明

是否必填

|参数|说明|是否必填|
|---|---|---|
|config|配置文件|是|

#### 识别回调函数 

函数

说明

|函数|说明|
|---|---|
|onInit|初始化完成|
|onResults|识别结果|
|onError|错误信息|

class SimpleAsrCallbackImpl implements AsrListener {
onInit(): void {
   LogUtils.log("init finish")
 }
onResults(text: string): void {
 }
onError(text: string): void {
   LogUtils.log("onError " + text)
 }
}
let asrEngine =  CloudASREngine.createInstance();
asrEngine.setCallback(new SimpleAsrCallbackImpl())
asrEngine.init(new Map<string, string>([
 ['productId', DUILiteSDK.config.getProductId()],
 ['deviceId', DUILiteSDK.deviceInfo.deviceId!]
]));
