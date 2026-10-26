#### **Captcha Harmony API Document** 

# **GTCaptcha4Client** 

验证 4.0 主要对外支持工具类 

## **Method** 

### **getClient()** 

获取 GTCaptcha4Client 工具类对象 

#### **Declaration** 

public static getClient(context UIContext): GTCaptcha4Client 

#### Parameters 

|**Param**|**Type**|**Description**|
|---|---|---|
|context|UIContext|UIContext|

#### **Discussion** 

注意:非单例实现,通过 getClient() 获取的 GTCaptcha4Client 对象需要保存,以方便在Page生命周期使用 

### **init(string, GTCaptcha4Config)** 

使用自定义配置初始化 

#### **Declaration** 

public init(captchaId: string, config: GTCaptcha4Config): GTCaptcha4Client 

#### **Parameters** 

|**Param**|**Type**|**Description**|
|---|---|---|
|captchaId|string|在后台申请的captchaId|
|config|GTCaptcha4Config|参数配置对象|

### **addOnSuccessListener(GTCaptcha4Client.OnSuccessListener)** 

添加验证结果监听对象,当验证码加载成功,用户解答验证码结果回调 

#### **Declaration** 

public addOnSuccessListener(response: OnSuccessListener): GTCaptcha4Client 

#### **Parameters** 

|**Param**|**Type**|**Description**|
|---|---|---|
|response|GTCaptcha4Client.OnSuccessListener|验证结果监听对象|

### **addOnFailureListener(GTCaptcha4Client.OnFailureListener)** 

添加加载验证码失败监听对象,加载验证码的过程中报错 

#### **Declaration** 

public addOnFailureListener(listener: OnFailureListener): GTCaptcha4Client 

#### **Parameters** 

|**Param**|**Type**|**Description**|
|---|---|---|
|listener|GTCaptcha4Client.OnFailureListener|加载验证码失败监听对象|

### **addOnWebViewShowListener(GTCaptcha4Client.OnWebViewShowL istener)** 

添加加载验证前端成功的监听对象,验证前端加载成功后回调。预加载已完成的情况下,调用 verifyWithCaptcha 后立即回调。 

#### **Declaration** 

public addOnWebViewShowListener(listener: OnWebViewShowListener): GTCaptcha4Client 

#### **Parameters** 

|**Param**|**Type**|**Description**|
|---|---|---|
|listener|GTCaptcha4Client.OnWebViewShowListener|验证前端加载成功监听对象|

### **verifyWithCaptcha()** 

开启验证流程,加载验证码 

#### **Declaration** 

public verifyWithCaptcha(): GTCaptcha4Client 

#### **Discussion** 

注意:调用 verifyWithCaptcha() 之前需要先调用 init() 、 addOnSuccessListener() 、 addOnFailureListener 否则可能报错 

### **cancel()** 

取消验证,关闭验证窗口 

#### **Declaration** 

public cancel() 

#### **Discussion** 

注意:调用 cancel() 之前需要先调用 init() 、 addOnSuccessListener() 、 addOnFailureListener 否则可 能报错 

### **setLogEnable(enable: boolean)** 

设置开启/关闭打印日志监控 

#### **Declaration** 

public setLogEnable(enable: boolean): GTCaptcha4Client 

#### **Discussion** 

调用 setLogEnable 会控制日志打印功能 

### **destroy()** 

销毁生命周期长的资源 

#### **Declaration** 

public destroy() 

#### **Discussion** 

销毁验证资源,务必调用 

#### **Discussion** 

该方法在客户使用的验证码界面的销毁生命周期中调用 

### **getVersion()** 

获取版本号 

#### **Declaration** 

public static getVersion(): string 

#### **Return Value** 

返回版本号,类型为 string 

# **GTCaptcha4Config** 

参数配置类 

### **setTimeOut(number)** 

设置请求超时时间 

#### **Declaration** 

setTimeOut(timeOut: number): GTCaptcha4Config 

#### **Parameters** 

|**Param**|**Type**|**Description**|
|---|---|---|
|timeOut|number|单位ms,默认10000|

### **setResourcePath(string)** 

设置 webView 加载资源地址 

#### **Declaration** 

setResourcePath(html: string): GTCaptcha4Config 

#### **Parameters** 

|**Param**|**Type**|**Description**|
|---|---|---|
|html|string|webView 加载地址|

### **setLanguage(string)** 

传输 JS 的设置语言,此接口控制加载 webView 的语言 

#### **Declaration** 

setLanguage(language: string): GTCaptcha4Config 

#### **Parameters** 

|**Param**|**Type**|**Description**|
|---|---|---|
|language|string|前端支持语言短码,详见前端文档|

#### **Discussion** 

如果设置为 null 或者未设置,则使用应用默认语言短码传输给前端 

### **setIsCanceledOnTouchOutside(boolean)** 

设置点击灰色区域是否消失,默认消失 

#### **Declaration** 

setIsCanceledOnTouchOutside(isCanceledOnTouchOutside: boolean): GTCaptcha4Config 

#### **Parameters** 

|**Param**|**Type**|**Description**|
|---|---|---|
|isCanceledOnTouchOutside|boolean|true 为消失|

### **setIsDebug(boolean)** 

设置是否是 debug 模式,上线务必置为 false ,或者不配置 

#### **Declaration** 

setIsDebug(isDebug: boolean): GTCaptcha4Config 

#### **Parameters** 

|**Param**|**Type**|**Description**|
|---|---|---|
|debug|boolean|true 为 debug,默认为 false|

### **setBackgroundColor(number)** 

设置 webView 背景色,控制的是 Harmony webView 控件的背景色,和前端 JS 的背景色不同 

#### **Declaration** 

setBackgroundColor(backgroundColor: string): GTCaptcha4Config 

#### **Parameters** 

|**Param**|**Type**|**Description**|
|---|---|---|
|backgroundColor|string|颜色资源|

### **setParams(Map<string, Object>)** 

额外参数配置,当前参数完全传输给 JS 

#### **Declaration** 

setParams(params: Map<string, Object>): GTCaptcha4Config 

#### **Parameters** 

|**Param**|**Type**|**Description**||
|---|---|---|---|
|params **Discussion**|JSONObje|ct Additional configuration parameter||
|**Key** 支持的键值如下表:|**ValueType** |**Description**|**DefaultValue**|
|displayMode|number|主题样式, 0:跟随系统1:普通2:暗黑|0|
|protocol|string|协议头,支持 "https://or http://|https://|
|bgColor|string|验证背景蒙版颜色,遵循css规则,注意最后两位为透明度|#00000000|
|loading|string|自定义loading,webView加载html的loading资源相对路 径,空字符串表示取消loading效果|"/gt4- loading.gif"|
|rem|number|设置验证码整体的缩放比例|1|
|nextWidth|string|验证码弹窗的宽度,需要携带单位,如"300px"|N/A|
|riskType|string|结合风控融合,指定验证形式|N/A|
|hideSuccess|boolean|隐藏验证成功弹窗|FALSE|

#### **Sample Code** 

```arkts
let params = new Map<string, string>(); params.set("displayMode", 0); params.set("protocol", "https://"); params.set("bgColor", "#CC0000FF"); ... 
```

let gtcaptcha4Config = new GTCaptcha4Config() .setParams(params); 

# **GT ha4Client#OnSuccessListener** **Captc** 

验证结果回调监听类 

### **onSuccess(Boolean, string)** 

验证接口回调 

#### **Declaration** 

onSuccess: (status: boolean, response: string) => void; 

#### **Parameters** 

|**Param**|**Type**|**Description**|
|---|---|---|
|status|boolean|用户操作验证结果, true 为成功, false 为失败,失败会刷新验证样式|
|response|string|用户操作验证成功,需要拿 response 数据到服务端验证|

#### **Discussion** 

验证成功描述如: 

{"lot_number":"b150e61198924eff9eaae121e9b67aa8","pass_token":"6fcfba4c35cb57b873c99c5b3b0 2089c58a26244c18f7706aaa1e87aed3aa8f4","gen_time":"1622020720","captcha_output":"Tu6rW0dRN O0NLxMKftwdH00G5whF5HHddthoXSEA1G4="} 

#### 验证失败描述如: 

{"captchaId":"647f5ed2ed8acb4be36784e01556bb71","captchaType":"slide","challenge":"95ed53b 4-95c6-4c6b-9aac-769b29ef74a0"} 

# **GT ha4Client#OnFailureListener** **Captc** 

加载失败回调监听类 

### **onFailure(string)** 

加载失败回调 

#### **Declaration** 

onFailure: (error: string) => void; 

#### **Parameters** 

|**Param**|**Type**|**Description**|
|---|---|---|
|error|string|验证加载失败描述,注意:包括用户主动取消|

#### **Discussion** 

加载失败描述如: 

{"code":"-34460","msg":"验证会话已取消","desc":{"description":"User cancelled 'Captcha'"}} 

# **GT ha4Client#OnWebViewShowListener** **Captc** 

验证前端加载成功回调监听类 

### **onwebViewShow()** 

验证前端加载成功 

#### **Declaration** 

onWebViewShow: () => void; 

#### **Discussion** 

在验证前端加载成功后回调。
