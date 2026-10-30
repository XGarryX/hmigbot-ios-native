# **0.集成准备** 

### 下载Demo源码 

### **依赖项 {docsify-ignore}** 

HarmonyOS 5.0.0(12) 

### **授权账号  {docsify-ignore}** 

AppKey 和 SecretKey 

## **SDK文件  {docsify-ignore}** 

|**版本号**|**更新日期**|**说明**|
|---|---|---|
|4.0.2|2026.02.09|规范SDK打包|

### 历史版本变动 

### **导入模块   {docsify-ignore}** 

```
ohpm install @chivox/chivoxaiengine --save
import * as chivoxaiengine from '@chivox/chivoxaiengine';
```

## **总体流程 {docsify-ignore}** 

# **1. 创建引擎** 

## **1.1方法原型{docsify-ignore}** 

createEngine(options: CreateEngineOptions): void; 

## **1.2作用 {docsify-ignore}** 

- 创建引擎实例,在产品启动或者进入评测模块时创建一个全局的评测引擎即可,后续评测可以复用 该引擎。 

## **1.3参数{docsify-ignore}** 

|**参数名**|**类型**|**必填**|**说明**|
|---|---|---|---|
|options|CreateEngineOptions|是|引擎参数配置|

## **1.4 CreateEngineOptions参数说明   {docsify-ignore}** 

|**属性名**|**类型**|**必填**|**说明**|
|---|---|---|---|
|cfg|EngineCfg|是|引擎配置信息|
|success|(egn: Engine)=>void|是|成功回调|

|**属性名**|**类型**|**必填**|**说明**|
|---|---|---|---|
|error|(err: AgnError)=>void|是|错误回调|

## **1.5 EngineCfg参数说明   {docsify-ignore}** 

|**属性名**|**类型**|**必填**|**说明**|**缺省值**|
|---|---|---|---|---|
|appKey|string|是|驰声分配给客户的 appKey|-|
|cloud|-|否|云端评测服务配置信 息|undefined|
|- enable|0|1|否|启用云端服务|1|
|- server|string|否|云端服务地址|`wss://cloud.chivox.com`|
|- connectTimeout|number|否|建立连接的超时时 间,单位:秒|10|
|- serverTimeout|number|否|等待结果响应的超时 时间,单位:秒|60|

## **1.6 示例代码  {docsify-ignore}** 

```
chivoxaiengine.createEngine({
cfg: {
appKey: "your appKey",
cloud: {
enable: 1,
connectTimeout: 10,
serverTimeout: 20,
        }
    },
success: (egn)=>{
// 创建成功
    },
error: (err)=>{
// 创建失败, 查看 err.code, err.message
    }
})
```

# **2. 发起请求** 

## **2.1 方法原型   {docsify-ignore}** 

start(startParam: EvalStartParam, listener: EvalListener, recorderListener?: RecorderListener): Eval; 

## **2.2 作用   {docsify-ignore}** 

发起评测请求。调用后,必须对应地调用stop或cancel,以保证释放占用的资源。 

## **2.3 参数   {docsify-ignore}** 

|**参数名**|**类型**|**必填**|**说明**|
|---|---|---|---|
|startParam|EvalStartParam|是|评测请求参数|
|listener|EvalListener|是|评测结果监听|
|recorderListener|RecorderListener|否|录音机事件监听|

### **返回值:** 

|**类型**|**说明**|
|---|---|
|Eval|评测对象|

**异常:** AgnError 

## **2.4  评测请求参数EvalStartParam   {docsify-ignore}** 

|**属性名**|**类型**|**必填**|**说明**|
|---|---|---|---|
|coreProvideType|string|否|设置'cloud',表示使用在线评测功能|
|app|-|是|身份认证信息|
|- applicationId|string|是|驰声授权的appKey|
|- sig|string|是|签名字符串 通过签名算法alg(appKey + timestamp + secretKey)生成|
|- alg|string|是|生成sig签名的算法 目前支持sha256, md5|
|- timestamp|string|是|生成签名的时间戳,单位:毫秒(ms)|
|- userId|string|否|用户在应用中的唯一标识|
|audio|-|是|音频信息|
|- audioType|string|是|音频类型 仅支持wav格式|
|- channel|number|是|声道数|
|- sampleBytes|number|是|每采样字节数,支持双字节2(16位)|
|- sampleRate|number|是|采样率|
|- compress|string|否|音频配置|

|**属性名**|**类型**|**必填**|**说明**|
|---|---|---|---|
|- audioSource|string|是|录音模式,有两种: 1.内置录音模式innerRecorder,sdk内部从麦克风读取 音频数据; 2.外部录音模式OuterFeed,需要客户从业务层自行将 音频数据传入给评分引擎;|
|- recordDuration|number|否|录音时长,内置录音模式使用|
|- request|object|必 选|评测请求,不同题型请求参数有所不同,具体查看 英文 语音评测 , 中文语音评测|

## **2.5 RecorderListener  {docsify-ignore}** 

录音机事件监听器。 

|**属性名**|**类型**|**必填**|**说明**|
|---|---|---|---|
|onRecorderStart|()=>void|否|录音开始回调|
|onRecorderData|(data: ArrayBuffer)=>void|否|录音数据回调(多次)|
|onRecorderStop|()=>void|否|录音结束回调|
|onRecorderError|(err: string)=>void|否|录音机错误回调。一旦发生此回调,其 他回调不会再触发|

## **2.6 代码示例   {docsify-ignore}** 

```
try {
constevl=egn.start(
        { // startParam
coreProvideType: 'cloud',
app: {
applicationId: 'your appKey',   // 填写appKey
sig: 'xxx',             // 填写签名
alg: "sha256",          // 签名算法
timestamp: 'xxx',       // 时间戳
userId: 'xxx',          // 用户Id
            },
audio: {                    // 音频参数
audioType: 'wav',
channel: 1,
sampleBytes: 2,
sampleRate: 16000,
compress: 'raw',
audioSource: 'innerRecorder'
            },
request: {                  // 评测请求参数
coreType: 'en.sent.score',
refText: "I want to know the past and present of Hong Kong.",
            }
        },
        { // 评测结果监听
onJsonResult: (json)=>{
// 评测结果
            },
onError: (json)=> {
// 评测错误. 查看 json.errId, json.error
            },
onBinaryResult: (data)=>{
// 二进制结果
            }
        },
        { // 录音机事件
onRecorderStart: ()=>{
// 录音开始
            },
onRecorderData: (data)=>{
// 录音数据
            },
onRecorderStop: ()=>{
// 录音停止
            },
onRecorderError: (err)=>{
// 录音机错误
            }
        }
    )
} catch (err) {
// 一般是因为接口调用顺序错误
// 检查 err.code, err.message
}
```

# **3. 发送音频数据** 

## **3.1 方法原型  {docsify-ignore}** 

feed(data: ArrayBuffer): void; 

## **3.2 作用  {docsify-ignore}** 

传入音频数据。仅外部录音模式 `outerFeed` 有效。 

## **3.3 参数  {docsify-ignore}** 

|**参数名**|**类型**|**必填**|**说明**|
|---|---|---|---|
|data|ArrayBuffer|是|音频数据|

**返回值:** 无 

**异常:** AgnError 

**3.4 代码示例  {docsify-ignore}** 

```
try {
egn.feed(data)
} catch (err) {
// 一般是因为接口调用顺序错误
// 检查 err.code, err.message
}
```

# **4. 停止请求** 

## **4.1 方法原型  {docsify-ignore}** 

-stop(): void; 

## **4.2 作用  {docsify-ignore}** 

当需要结束传入音频或结束录音时,调用本方法。调用本方法后,将进入等待评测结果状态。 

注:stop( )方法必须与2.发送请求的start( )方法成对调用,否则下次start( )会报错误。 

**参数:** 无 

**返回值:** 无 

**异常:** AgnError 

## **4.3 示例代码  {docsify-ignore}** 

```
try {
egn.stop()
} catch (err) {
// 一般是因为接口调用顺序错误
// 检查 err.code, err.message
}
```

# **5.接收结果** 

## **5.1 EvalListner  {docsify-ignore}** 

评测结果监听器 

该接口在2.发起请求接口中通过listener参数设置 

|**属性名**|**类型**|**必填**|**说明**|
|---|---|---|---|
|onJsonResult|(json: EvalJsonResult)=>void|否|评测结果回调|
|onBinaryResult|(data: ArrayBuffer)=>void|否|二进制结果回调|
|onError|(json: EvalJsonResult)=>void|否|评测错误回调|

**5.2 EvalJsonResult  {docsify-ignore}** 

评测结果 

|**属性名**|**类型**|**必填**|**说明**|
|---|---|---|---|
|errId|number|否|错误码。若存在errId且值非0,表明评测错误|
|error|string|否|错误描述信息,仅在评测错误是有|
|...|-|-|其他评测结果的属性,请参考内核结果文档|

# **6. 取消请求** 

## **6.1 方法原型  {docsify-ignore}** 

cancel(evl?: Eval): void; 

## **6.2 作用  {docsify-ignore}** 

取消评测。 

## **6.3 参数说明 {docsify-ignore}** 

|**参数名**|**类型**|**必填**|**说明**|
|---|---|---|---|
|evl|Eval|否|指定某个特定评测,不填则取消当前评测|

**返回值:** 无 

**异常:** 无 

## **6.4 代码示例 {docsify-ignore}** 

```
egn.cancel()
```

# **7. 销毁引擎** 

## **7.1 方法原型  {docsify-ignore}** 

close(): void; 

## **7.2 作用  {docsify-ignore}** 

销毁评测引擎 

**参数:** 无 

**返回值:** 无 

**异常:** 无 

**7.3 代码示例 {docsify-ignore}** 

```
egn.close()
```

# **8. 其它接口** 

## **8.1 获取SDK版本号 {docsify-ignore}** 

```
hilog.info(0x0000, 'TestDemo','Version: %{public}s',
chivoxaiengine.Version.DOT_STRING )
```

## **8.1 返回数据示例  {docsify-ignore}** 

```
4.0.2
```

## **8.2 错误类型AgnError  {docsify-ignore}** 

|**属性名**|**类型**|**必填**|**说明**|
|---|---|---|---|
|code|number|是|错误码|
|message|string|是|错误描述|
