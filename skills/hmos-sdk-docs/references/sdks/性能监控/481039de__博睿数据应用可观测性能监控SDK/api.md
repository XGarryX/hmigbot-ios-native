# SDK API功能 

## 一、启动配置接口 

启动配置类的接口通过链式调用方式随  Bonree.withAppID("<#AppID#>").start(this.context.getApplicationContext()); 一同配置,需要在调用 start  函数之前 withAppID  之后进行相关配置,可同时配置多项,start函数后配置无效。 

AppID 请于平台上获取或联系技术支持。 

### 设置config地址 

One平台或私有化部署用户启动时需要设置私有部署的config地址。 

接口说明 

|withConfigAddres|(configAddress ) Bonree s : string :||
|---|---|---|
|参数|说明 参数限制|失败结果|
|configAddress|私有化config地址 字符串长度大于0,小于等于2083,否则接口调用失败|探针停止|

#### 示例 

Config地址 请于平台上获取或联系技术支持。 

Bonree.withAppID("<#AppID#>") .withConfigAddress("<#Config地址#>") .start(this.context.getApplicationContext()) 

### 设置自定义APP版本 

通过此方法设置了自定义设备App版本号,那么SDK将会上报此版本号,不再使用默认获取的版本号. 

接口说明 

withAppVersion(version : string) Bonree: 

|参数|说明|参数限制|失败结果|
|---|---|---|---|
|version|自定义的版本号|字符串长度大于0,小于等于64,否则接口调用失败|当次设置无效|

#### 示例 

Bonree.withAppID("<#AppID#>") .withAppVersion("custom app version") .start(this.context.getApplicationContext()); 

### 设置自定义应用环境 

#### 通过此方法设置应用环境字段 

Bonree withAppEnvironment(environment AppEnvironment): ; 

|参数|说 明|参数限制|失 败 结 果|
|---|---|---|---|
|environment|应|仅可使用预置枚举单位,否则接口调用失败,枚举类型「0:NONE无环境配置,1:PROD线|当|
||用|上环境,2:GRAY灰度环境,3:PRE预发环境,4:DAILY日常环境,5:LOCAL本地环境」|次|
||环||设|
||境||置|
||枚||无|
||举||效|

#### 示例 

Bonree.withAppID("<#AppID#>") .withAppEnvironment(AppEnvironment.NONE) //   .withAppEnvironment(AppEnvironment.PROD) //   .withAppEnvironment(AppEnvironment.GRAY) //   .withAppEnvironment(AppEnvironment.PRE) //   .withAppEnvironment(AppEnvironment.DAILY) //   .withAppEnvironment(AppEnvironment.LOCAL) .start(this.context.getApplicationContext()); 

#### 注意:SDK内部预置了应用环境枚举单位,预置单位类型见AppEnvironment枚举类。 

### 使用自定义冷启动结束时间 

#### 是否使用自定义冷启动结束时间 

#### 接口说明 

|(used ) Bonree withUseCustomLaunch : boolean :||
|---|---|
|参数|说明|
|used|true 使用自定义结束 false 不使用|

示例 

Bonree.withAppID("<#AppID#>") .withUseCustomLaunch(true) .start(this.context.getApplicationContext()); 

### 设置SDK自身请求Header 

#### 本接口用于设置对于SDK自身发起的网络请求中添加自定义请求头 

#### 接口说明 

withSDKRequestHeaders(headers Map: <string, string>) Bonree: 

|参数|说明|失败结果|
|---|---|---|
|headers|要设置的请求头键值对(最多设置64个,key长度限制256个字符,value|key,value长度限制则单条数|
||长度限制512个字符)|据无效|

#### 示例 

```arkts
const headers:Map<string,string> = new Map(); headers.set("headerKey1","headerValue1"); headers.set("headerKey2","headerValue2"); headers.set("headerKey3","headerValue3"); Bonree.withAppID("<#AppID#>") .withSDKRequestHeaders(headers) .start(this.context.getApplicationContext()); 
```

### 设置用户渠道ID 

#### 区分应用发布的渠道, 渠道信息会在平台的性能数据中做展示 

#### 接口说明 

withChannelID(channelID : string) Bonree: 

|参数|说明|参数限制|失败结果|
|---|---|---|---|
|channelID|自定义的渠道号|符串长度大于0,小于等于256,否则接口调用失败|当次设置无效|

#### 示例 

Bonree.withAppID("<#AppID#>") .withChannelID("channelID") .start(this.context.getApplicationContext()); 

## 二、数据获取接口 

### 获取设备ID 

#### 如果在SDK启动时设置了 withDeviceID  接口,那么会返回自定义的ID 

接口说明 

static getDeviceID() : string 

示例 

const deviceID  Bonree= .getDeviceID(); console.log("BRSDK: "+deviceID); 

### 获取SDK当前版本 

获取当前SDK的版本 

接口说明 

static getSdkVersion() : string 

#### 示例 

const sdkVersion  Bonree= .getSdkVersion(); console.log("BRSDK: "+sdkVersion); 

## 三、自定义信息设置接口 

### 自定义用户信息 

BonreeSDK支持设置与用户相关的信息,从而完成性能数据与实际用户相关联的需求场景。 

设置用户信息有两种方式: 

设置用户ID,以字符串形式给用户做标识 

|(userID ) setUserID : string ;|||
|---|---|---|
|参数 说明|参数限制|失 败 结 果|
|userID 以字符串|字符串可为空或空串。|当|

|参数|说明|参数限制|失 败 结 果|
|---|---|---|---|
|示例|形式给用 户做标识|字符串小于等于256,且不包含特殊字符(只允许数字、字母、中文、冒号、空格、斜 杠、下划线、连字符、英文句号、星号、叹号、@、#,空或空串无效),否则接口调用 失败|次 设 置 无 效|
|Bonree .|( setUserID "18|) 988888888" ;||

### 设置用户附加信息 

#### 设置用户更加详细的附加信息。 

|static set|UserEx|(extraInfo Map Object ) traInfo : <string, > ;||
|---|---|---|---|
||||失|
||||败|
||说||结|
|参数|明|参数限制|果|
|extraInfo|用|Map中kv最多64对 超过则保留其中64个,key长度小于256,超过则该key无效,且不包含特|当|
||户|殊字符(只允许数字、字母、冒号、空格、斜杠、下划线、连字符、英文句号、@,空或空串|次|
||附|无效);value小于512,超过则截取|设|
||加||置|
||信||无|
||息||效|

#### 示例 

```arkts
const userInfo  = new Map<string, Object>(); userInfo.set("phoneNumber", "18988888888"); userInfo.set("clientID", "harmony device id"); userInfo.set("type", "vip"); Bonree.setUserExtraInfo(userInfo); 
```

### 追加用户附加信息 

追加用户附加信息 

static addUserExtraInfo(key : string, value Object): ; 

|参数|说明|参数限制|失败 结果|
|---|---|---|---|
|key|追加的key|key长度小于256,超过则该key无效,且不包含特殊字符(只允许数字、字母、冒号、 空格、斜杠、下划线、连字符、英文句号、@,空或空串无效);|当次 设置 无效|
|value|key对应的 value|value小于512,超过则截取|当次 设置|
||||无效|

#### 示例 

Bonree.addUserExtraInfo("age","18"); 

### 移除用户附加信息 

#### 移除用户附加信息 

|static removeUs|(key ) erExtraInfo : string ;||
|---|---|---|
|参||失败结|
|数 说明|参数限制|果|
|key 追加的 key|key长度小于256,超过则该key无效,且不包含特殊字符(只允许数字、字母、冒号、空 格、斜杠、下划线、连字符、英文句号、@,空或空串无效);|当次设 置无效|
|示例 Bonree .removeUs|( ) erExtraInfo "age" ;||

### 累加用户数值信息 

#### 累加用户数值信息 

|static|
increaseUserE|(key
value
)
xtraInfo
: string,
: number ;||
|---|---|---|---|
|参数|说明|参数限制|失败 结果|
|key|追加的key|key长度小于256,超过则该key无效,且不包含特殊字符(只允许数字、字母、冒号、|当次|

|参数|说明|参数限制|失败 结果|
|---|---|---|---|
|||空格、斜杠、下划线、连字符、英文句号、@,空或空串无效);|设置 无效|
|value|key对应的|value 仅支持Number类型|当次|
||value||设置|
||||无效|

#### 示例 

Bonree.increaseUserExtraInfo("number",1); 

### 添加事件的公共属性 

#### 添加事件的公共属性 

|static addEv|(attributes Map entAttributes : <string|Object isSaveLocal ) , >, : boolean ;||
|---|---|---|---|
|参数|说明|参数限制|失 败 结 果|
|attributes|要添加的信息,相同的key会覆盖 之前的设置|map中kv最多64对 超过则保留其中64个;key长度小于 256,超过则该key无效,且不包含特殊字符(只允许数字、 字母、冒号、空格、斜杠、下划线、连字符、英文句号、@,|当 次 设|
|||空或空串无效);|置|
||||无|
||||效|
|isSaveLocal|是否持久化本地,true:公共属性||当|
||会持久化到本地,下次打开应用还||次|
||会带上公共属性。false:仅本次使||设|
||用期间生效||置|
||||无|
||||效|

#### 示例 

```arkts
const attributes  = new Map<string, Object>(); attributes.set("onclick", "1"); attributes.set("page", "1"); attributes.set("type", "vip"); Bonree.addEventAttributes(attributes true), ; 
```

### 添加单条事件的公共属性 

添加单条事件的公共属性 

|static (key addEventAttribute :|
 string,|value

:|Object

,|isSaveLocal
)

: boolean ;|
|---|---|---|---|---|

|参数|说明|参数限制 失败 结果|
|---|---|---|
|key|要添加信息 的key|key长度小于等于256,超过则该key无效,且不包含特殊字符(只允许数字、字母、冒 号、空格、斜杠、下划线、连字符、英文句号、@,空或空串无效); 当次 设置 无效|
|value|要添加信息 的value|value长度小于等于512,超过则截取 当次|

isSaveLocal | 是否持久化本地,true:公共属性会持久化到本地,下次打开应用还会带上公共属性。false:仅本次使用期 间生效 | | 当次设置无效 | 

示例 

Bonree.addEventAttribute("onclick",1,true); 

### 移除事件公共属性 

移除事件公共属性 

static removeEventAttribute(keys : string[]) 

|参数|说明|参数限制|失败结 果|
|---|---|---|---|
|keys|要删除|key长度小于等于256,超过则该key无效,且不包含特殊字符(只允许数字、字母、冒|当次设|
||key的数 组|号、空格、斜杠、下划线、连字符、英文句号、@,空或空串无效);|置无效|

#### 示例 

const removeKeys=["name","age"]; Bonree.removeEventAttribute(removeKeys); 

### 移除所有事件公共属性 

移除所有事件公共属性 

static removeAllEventAttributes(); 

#### 示例 

Bonree.removeAllEventAttributes(); 

### 自定义异常 

#### 调用接口并传入相应参数,可完成自定义异常数据的统计功能。 

static setCustomException(error Error) : ; //推荐使用,直接将Exception或Throwable对象传入即可 

|参数|说明|参数限制|失败结果|
|---|---|---|---|
|throwable|异常对象|系统抛出的异常对象,非null|当次设置无效|

#### 示例 

try { throw new Error("Test"); } catch (err) { Bonree.setCustomException(err); } 

//此重载配置更灵活,可用于业务型异常上报,有关参数可填充符合参数限制的任意内容,平台直接展示。 static setCustomException(errorType : string, causeBy?: string, errorDump?: string); 

|参数|说明|参数限制|失败结果|
|---|---|---|---|
|exceptionType|异常类型(必 要)|字符串长度大于0,小于等于256,否则接口调用 失败。|当次设置无效|
|causeBy|异常原因|字符串可为空或空串。 字符串小于等于512,超长截取。|-|
|errorDump|异常信息|超出10000字符时会被切割|字符串可为空或空串。 字符串小于等于10000,超长截 取。|

#### 示例 

try { throw new Error("Test"); } catch (err) { 

if (err instanceof Error) { Bonree.setCustomException(err.name, err.message, err.stack); } } 

### 自定义视图 

#### 调用接口并传入相应参数,可完成自定义视图数据统计功能。 

//自定义视图-页面开始,与页面结束需成对调用,一般调用位置:onPageShow name视图名称为必填字段,如果为空则调用失败。 static setCustomPageStart(pageName : string, param?: string); 

//自定义视图-页面结束,与页面开始成对调用,一般调用位置:onPageHide static setCustomPageEnd(pageName : string, param?: string); 

|参数|说明|参数限制|失败结果|
|---|---|---|---|
|pageName|视图名字(必要)|字符串长度大于0,小于等于256,否则接口调用失败。|当次设置无效|
|param|附加信息,可设置为视图别名|字符串可为空或空串。 字符串小于等于256,超长截取。|-|

#### 示例 

onPageShow() { Bonree.setCustomPageStart("Index", "首页"); } onPageHide() { Bonree.setCustomPageEnd("Index", "首页"); } 

### 自定义事件(完整版) 

#### 分别调用开始与结束接口并传入相应参数,可完成自定义事件数据与事件持续时间的统计功能。 

static setCustomEventStart(eventID : string, name?: string, label?: string, param?: string, info?: Map<string, string static setCustomEventEnd(eventID : string, name?: string, label?: string, param?: string, info?: Map<string, string> 

|参数|说明|参数限制|失败结果|
|---|---|---|---|
|eventID|事件ID(必要)|字符串长度大于0,小于等于256,否则接口调用失败。|当次设置无 效|
|name|事件名称|字符串可为空或空串。 字符串小于等于256,超长截取。|-|
|label|事件标签|字符串可为空或空串。|-|

|参数|说明 参数限制|失败结果|
|---|---|---|
||字符串小于等于256,超长截取。||
|param|附加信息(预留字段,暂无使用场 景) 字符串可为空或空串。 字符串小于等于7000,超长截取。|-|
|info|kv存储信息 可为空,转JSON后长度在7000字符以内,否则接口调用 失败。|-|

#### 示例 

```arkts
Bonree.setCustomEventStart("vip-login","验证码发送","登录"); Bonree.setCustomEventEnd("vip-login","验证码发送","登录"); //带有info字段的调用 const info  = new Map<string, string>(); info.set("eventNumber", "10001"); info.set("eventName", "bonree"); info.set("eventXX", "xx"); Bonree.setCustomEventStart("vip-login", "验证码发送", "登录", undefined info), ; Bonree.setCustomEventEnd("vip-login", "验证码发送", "登录", undefined info), ; 
```

### 自定义事件(精简版) 

#### 调用接口并传入相应参数,可完成自定义事件数据统计功能。 

|static s|(eventID name etCustomEvent : string, ?|label param info Map : string, ?: string, ?: string, ?: <st|) ring, string> ;|
|---|---|---|---|
|参数|说明|参数限制|失败结果|
|eventID|事件ID(必要)|字符串长度大于0,小于等于256,否则接口调用失败。|当次设置无 效|
|name|事件名称|字符串可为空或空串。 字符串小于等于256,超长截取。|-|
|label|事件标签|字符串可为空或空串。 字符串小于等于256,超长截取。|-|
|param|附加信息(预留字段,暂无使用场 景)|字符串可为空或空串。 字符串小于等于7000,超长截取。|-|
|info|kv存储信息|可为空,转JSON后长度在7000字符以内,否则接口调用 失败。|-|

示例 

Bonree.setCustomEvent("001","注册"); 

```arkts
const info  = new Map<string, string>(); info.set("eventNumber", "10001"); info.set("eventName", "bonree"); info.set("eventXX", "xx"); Bonree.setCustomEvent("vip-login", "登录失败", undefined undefined info), , ; 
```

### 自定义日志 

#### 调用接口并传入相应参数,可完成自定义日志数据统计功能。 

static setCustomLog(logInfo : string); 参数 说明 参数限制 失败结果 logInfo 日志信息(必要) 字符串长度大于0,否则接口调用失败。 当次设置无效 字符串小于等于10000,超长截取。 示例 Bonree.setCustomLog("login successful..."); 

### 自定义指标 

#### 调用接口并传入相应参数,可完成自定义指标数据统计功能。 

|static s|(name etCustomMetric :|
value
)
 string,
: number||
|---|---|---|---|
|参数|说明|参数限制|失败结果|
|name|指标名称(必要)|字符串长度大于0,小于等于256,否则接口调用失败。|当次设置无效|
|value|指标值(必要)|Long.MAX_VALUE|-|

#### 示例 

Bonree.setCustomMetric("自定义指标",systemDateTime.getTime(false)); 

### 自定义方法 

调用接口并传入相应参数,可完成自定义指标数据统计功能。自定义方法埋点多用于不在SDK自动采集范围内的业务方法或 异步方法的手动埋点。 

static setCustomMethodStart(name : string); static setCustomMethodEnd(name : string); 

|参数|说明|参数限制|失败结果|
|---|---|---|---|
|name|方法名称(必要)|字符串长度大于0,小于等于256,否则接口调用失败。|当次设置无效|

#### 示例 

onNetworkLoad(){ Bonree.setCustomMethodStart("onNetworkLoad"); //do something Bonree.setCustomMethodEnd("onNetworkLoad"); } 

### 自定义网络 

调用接口并传入相应参数,可完成自定义指标数据统计功能。自定义方法埋点多用于不在SDK自动采集范围内的业务方法或 异步方法的手动埋点。 

|static (networkCustomEvent NetworkCustomEvent setCustomNetwork : .Ne |) tworkCustomEventBean ||
|---|---|---|
|参数 说明|参数限制|失败结果|
|networkCustomEvent 实体结构(必要) 指标|结构对象。必传参数。|当次设置无效|
|@param requestUrl :string @param method HttpMethod : @param targetIp :string | undefined @param targetPort :number @param dnsTimeUs :number @param connectTimeUs :number @param sslTimeUs :number @param requestTimeUs :number @param responseTimeUs :number @param downloadTimeUs :number @param downloadSizeByte :number @param protocolType ProtocolType :|//请求地址 //请求方式 //目标IP //目标端口 //dns查询时间 //tcp建连时间 //ssl时间 //请求时间 //响应时间 //下载用时 //响应数据大小 //协议类型 ||
|@param cnameArray Array : <string> | undefined @param errorCode :number | undefined|//cname的集合 //错误码 ||
|@param errorMessage :string | undefined @param errorOccurrentProcess ErrorOccurrentProcess : | undefined @param requestDataSize :number | undefined @param resourceType :string | undefined @param requestHeader Map : <string, string> | undefined @param responseHeader Map : <string, string> | undefined;|//错误描叙信息 //错误发生的过程阶段 //请求大小的字段 //资源类型 //请求header //响应header||

#### 示例 

Bonree.setCustomNetwork( new NetworkCustomEvent.NetworkCustomEventBean("https://www.bonree.com", NetworkCustomEvent.HttpMethod.GET, "127.0.0.1", 

443, 20000, 10000, 50000, 20000, 500000, 10000, 55, NetworkCustomEvent.ProtocolType.HTTPS)); 

### 自定义冷启动结束 

在启动配置中配置了 withUseCustomLaunch  接口后,调用此自定义接口可以设置当前时刻为自定义冷启动事件的结束点 

static recordCustomLaunchEnd(); 

#### 示例 

Bonree.recordCustomLaunchEnd();
