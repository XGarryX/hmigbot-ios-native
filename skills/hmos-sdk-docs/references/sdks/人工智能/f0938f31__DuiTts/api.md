# **tts** 接口文档 

# **DuiTts SDK** 接口文档 

版本: 1.0.2 (基于提供的代码,可能与实际SDK版本有差异) 

## **DUILiteSDK** 

### **Init:** 初始化 

参数

说明

是否必填

|参数|说明|是否必填|
|---|---|---|
|context|上下文对象|是|
|debug|是否开启debug模式|否|

#### let appContext = this.context.getApplicationContext() DUILiteSDK.init(appContext, DEBUG) 

#### DUILiteSDK.setLogLevel(hilog.LogLevel.DEBUG) 

let appContext = this.context.getApplicationContext()
DUILiteSDK.init(appContext, DEBUG)
DUILiteSDK.setLogLevel(hilog.LogLevel.DEBUG)

### **doAuth** 授权 

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

## **DUILiteConfig** 

#### 配置文件 

参数

是否必填

|参数|说明|是否必填|
|---|---|---|
|authConfig|授权配置文件|是|

### **AuthConfig** 

|参数|说明|是否必填|
|---|---|---|
|apiKey|集成SDK时需用到的鉴权参数|是|
|productId|集成SDK时需用到的鉴权参数|是|
|productKey|集成SDK时需用到的鉴权参数|是|
|productSecret|集成SDK时需用到的鉴权参数|是|
|deviceName|鉴权唯一标识,一机一号固定不可变|是|

## **AICouldTTSEngine** 

### **Init** 初始化 

|参数|说明|是否必填|
|---|---|---|
|AITTSListener|回调函数|是|

### 合成回调函数 

函数

说明

|函数|说明|
|---|---|
|onInit|初始化完成|
|onResults|识别结果|
|onError|错误信息|

interface AITTSListener {
  /**   *  合成引擎初始化结束后执行
   *   * @param status   *
   *    {@link AIConstant#OPT_SUCCESS}: 初始化成功;
   *    {@link AIConstant#OPT_FAILED}: 初始化失败 ,
   */
     onInit(status: number): void;
  /**
   *  发生错误时执行
   * @param utteranceId  本次合成对应的 ID
   * @param error   错误信息
   */
   onError(utteranceId: string, error: AIError): void;
  /**
   *  数据准备就绪,可以播放时执行
   * @param utteranceId  本次合成对应的 ID
   */
   onReady(utteranceId: string): void;
  /**   *  播放完毕后执行
   * @param utteranceId  本次合成对应的 ID
   */

   onCompletion(utteranceId: string): void;
  /**  *  播放进度
   *   * @param currentTime   *             当前播放时间  ( 单位 :100ms)
   * @param totalTime   *             已经送入内核的文本合成的总时长  ( 单位 :100ms)
   *             云端合成没有此项
   */
   onProgress(currentTime: number, totalTime: number): void;
  /**   *  合成开始的回调 , 在子线程,若需要更新 UI 控件需要做线程转换
   *   * @param utteranceId utteranceId   */
   *
   onSynthesizeStart(utteranceId: string): void;
  /**  合成完成的回调  , 在子线程,若需要更新 UI 控件需要做线程转换
   *  @param utteranceId utteranceId   */
   onSynthesizeFinish(utteranceId: string): void;
