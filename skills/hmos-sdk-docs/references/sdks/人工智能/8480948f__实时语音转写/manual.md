## 实时语音转写鸿蒙SDK介绍 

##### 官网 

实时语音转写(ASR, real-time)通过 WebSocket 协议,建立客戶端与服务的长连接,开发者将连 续的音频流内容发送给服务,服务返回对应的文字流内容。 

##### SDK包名 : realtimetranslib 

SDK版本号 : 1.0.0 

##### 约束与限制 

在下述版本通过验证: 

|DevEco Studio版本 号|HarmonyOS SDK版本号|手机操作系统ROM版本号|
|---|---|---|
|DevEco Studio|【API11】HarmonyOS SDK|3.0.0.13(SP6DEVC00E13R6P1)|
|5.0.9.100|5.0.0(12)||
|DevEco Studio6.0.2|【API22】HarmonyOS SDK 6.0.2.130|6.1.0.117(SP6C00E115R4P9patch15)|

# 一 、SDK说明 

语音实时转写通过WebSocket协议建立客戶端与服务的长连接,将连续的音频流内容发送给服 务,服务返回对应的文字流内容。 

SDK详细的接口介绍及说明请参考:HarmonyOS文档。 

示例demo 

SDK包 

二、集成方法

#### 1.1 下载安装 

```
  ohpm i @unisound/realtimetranslib
```

#### 1.2 将SDK的har包拷⻉到工程的libs目录下; 

##### 工程结构图如下: 

##### 在oh-package.json5文件,关联加载实时语音转写库 

```
"dependencies":
  {
    "@unisound/realtimetranslib": "file:libs/realtimetranslib.har"
  }
```

# 三、申请权限 

##### module.json5文件添加ohos.permission.INTERNET和ohos.permission.MICROPHONE权限 

```
 "requestPermissions": [
      {
        "name": "ohos.permission.INTERNET"
      },
      {
        "name": "ohos.permission.MICROPHONE",
        "reason": "$string:EntryAbility_mic",
        "usedScene": {
          "abilities": [
            "FormAbility"
          ],
          "when": "always"
        }
      }
    ]
```

# 四、使用说明 

### SDK设置参数和回调 

```
  private initEngine() {
    this.speechEngine.setEngineParam(this.engineParam)
    this.speechEngine.setCallBack(this.transCallBack)
  }
```

### 开始语音转写识别 

```
  private startEngine(){
    this.speechEngine.start()
  }
```

### 停止语音转写识别 

```
  private stopEngine() {
    this.isStart = false
    this.speechEngine.stop()
  }
```

# 五、识别结果 

```
{
```

`"code": 0, "msg": "success", "sid": "requestid", "type": "fixed", "text": "` 今天天气怎么样 `?",` 

```
"start_time": 58860,
"end_time": 70500,
"end":false
}
```

|---|---||
|---|---|---|
|参数|描述||
|code|错误码||
|msg|结果说明||
|sid|识别的唯一id||
|type|结果类型:"variable":可变|结果,"fxed":固定结果|
|text|识别结果||
|start_ti|me 句子开始时间,单位ms||
|end_ti|me 句子结束时间,单位ms||
|end 六、|是否为最后一次识别结果, end=false 错误码|当发送完type=end消息时,返回end=true,否则|
|错误 码|说明|解决方法|
|0|正确||
|20101|Websocket连接空闲时间超过 10s|检查客戶端代码|
|20102|参数错误|客戶端检查参数是否正确|
|20103|内部错误|建议重试,或者提工单,工单详情请提供sid|
|20104|资源不足|建议重试,或者提工单,工单详情请提供sid|
|20105|音频长度超过120分钟|检查音频文件是否过长,减小音频长度|
|20106|非法的appkey|检查appkey是否合法|
|20107|套餐时长使用完|购买时长套餐|
|20108|并发超限制|减小并发或者购买并发套餐|

20109 客戶端ip不在白名单中 检查是否开启白名单,同时检查客戶端出口ip是否在ip 白名单中 

# 七、SpeechEngine类 

语音实时转写入口,用于设置识别相关参数、发起识别、结束识别等。 

##### setEngineParam(engineParam: EngineParam) 

|-|-|
|---|---|
|说明|设置识别相关配置|
|版本支持|最低1.0.0|
|engineParam|识别相关参数|

setCallBack(callBack: OnTransCallBack) 

|-|-|
|---|---|
|说明|设置识别的回调|
|版本支持|最低1.0.0|
|参数OnTransCallBack|识别回调|

##### EngineParam类说明 

|-|-|
|---|---|
|说明|识别参数|
|版本支持|最低1.0.0|
|appkey|(必填)通过官方申请|
|secret|(必填)通过官方申请|
|host|(必填) wss://ws-rtasr.hivoice.cn/v1/ws|
|userId|(可选值)默认值为UUID,该次请求session_id|

|domain|(可选值)领域,可设置多个(最多4个),general(通用),law(法律);technology(科 技), medical(医疗)。默认值为general,定义参考EngineParamDomain|
|---|---|
|sample|(可选值)采样率: 16k,8k,默认值为16k,@EngineParamSample|
|lang|(可选值)语言: cn(中文);en(英文);cantonese(粤语);sichuanese(四川话),默 认值为cn,@EngineParamLang|
|variable|(可选值)是否返回可变结果: true,false,),默认值为true|
|punctuation|(可选值)是否开启标点符号添加: true,false,默认值为true|
|postProc|(可选值)是否开启数字格式转为阿拉伯数字格式: true,false,默认值为true|

```
  engineParam: EngineParam =
    new EngineParam("appkey", "secret","wss://ws-
rtasr.hivoice.cn/v1/ws", true, util.generateRandomUUID())
```

##### OnTransCallBack 类说明 

|-|-|
|---|---|
|说明|事件和结果回调|
|版本支持|最低1.0.0|
|onConnectSuccess: () => void|调用start()后,连接服务器成功,会回调 onConnectSuccess()|
|onConnectError(): () => void|连接服务器出错,会回调onConnectError()|
|onConnectClose(): () => void|主动调用stop(),会回调onSpeechClose()|
|onTransResult: (result: TransResult) => void|识别结果:TransResult|
|onTransError: (error: string) => void|实时转写出错会回调onTransError()|

##### TransResult类说明 

-

- - 

|说明|识别结果|
|---|---|
|版本支持|最低1.0.0|
|参数code:number|错误码,@SpeechResponseCode|
|参数msg:string|结果说明|
|参数sid:string|识别的唯一id|
|参数end:boolean|请求是否结束|
|参数text:string|识别结果|
|参数type:string|结果类型:"variable":可变结果,"fxed":固定结果|
|参数start_time:string|句子开始时间|
|参数end_time:string|句子结束时间|

ResponseCode 错误码 

|-|-|
|---|---|
|说明|错误码|
|版本支持|最低1.0.0|

0: 成功 401: 签名校验失败 

403: 时钟偏移校验失败 

20101: Websocket连接空闲时间超过10s 20102: 参数错误 20103: 内部错误 20104: 资源不足 20105: 音频长度超过120分钟 20106: 非法的appkey 20107: 套餐时长使用完 20108: 并发超限制 20109: 并发超限制 99999: 其它错误 

start(): void 

开启websocket连接,连接服务成功后进行语音转写 

stop(): void 

关闭websocket连接和录音,停止语音转写 

sendMessage(data: ArrayBuffer): void 

- 发送识别的音频数据 

release(): void 

释放资源
