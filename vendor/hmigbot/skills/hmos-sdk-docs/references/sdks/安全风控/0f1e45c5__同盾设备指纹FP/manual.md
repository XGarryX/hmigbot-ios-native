# **集成要求** 

## **合规说明** 

请注意,在贵司的App中集成同盾提供的SDK产品时: 

1.1  根据《网络安全法》《电信条例》《电信和互联网用户个人信息保护规定》等相关法律法规要求及监管实践中 的标准,在贵司的最终用户首次启动App并在贵司开始采集信息之前,贵司应以交互界面或设计(如隐私政策弹窗 等)向最终用户完整告知收集、使用、与第三方共享最终用户个人信息的目的、方式和范围,并征得最终用户的明 示同意。 

- 1.2  为向贵司提供业务安全和风控服务,同盾设备指纹SDK将采集、处理、使用用户的手机终端唯一标志信息 

(IMEI/IDFA)、Android ID、OAID、IMSI、MEID、MAC 地址、SIM 卡序列号、设备序列号、设备类型、设备型 号、系统类型、地理位置、登录 IP 地址等设备信息。为确保贵司使用相关服务的合规性,前述隐私政策应涵盖对 同盾设备指纹SDK提供服务并采集、处理、使用相关信息的授权,以下条款内容供贵司参考,具体表述可由贵司根 据贵司隐私协议的整体框架和内容自行确定: 

同盾设备指纹SDK:为了业务安全和风控,我司使用了同盾 SDK,该 SDK 需要获取您的手机终端唯一标志信 息(IMEI/IDFA/ODID)、Android ID、OAID、IMSI、MEID、MAC 地址、SIM卡序列号、设备序列号、设备 类型、设备型号、系统类型、地理位置、登录 IP 地址、应用程序列表、运行中进程信息、传感器(光传感 器、重力传感器、磁场传感器、加速度传感器、陀螺仪传感器、心率传感器)相关设备信息,用于设备欺诈风 险识别。 

同盾隐私协议:https://www.tongdun.cn/other/privacy/id=4 

## **环境要求** 

||**说明**|
|---|---|
|兼容版本|API12及以上系统|
|支持架构|arm64-v8a, x86_64|

# **集成步骤** 

## **安装配置** 

##### **安装说明** 

ohpm install @trustdecision/mobrisk 

##### **集成 SDK** 

在工程的 oh-package.json5 中设置三方包依赖,配置示例如下: 

"dependencies": { "@trustdecision/mobrisk": "1.2.7" } 

### **SDK信息** 

**SDK名称** :同盾设备指纹SDK 

**开发者名称** :同盾科技有限公司 

**使用目的** :提供业务安全和风控服务 

**SDK包名** : @trustdecision/mobrisk 

**版本号** :1.2.7 

**MD5值** :fd2da4a90b3b9caa6cd17c8aa89726cd **个人信息类处理规则(隐私政策)** :https://www.tongdun.cn/other/privacy/id=4 

##### **使用说明:** 合规使用指导 

##### **SDK下载地址** 

https://ohpm.openharmony.cn/ohpm/@trustdecision/mobrisk/-/mobrisk-1.2.7.har 

##### **OpenHarmony三方库中心仓** 

https://ohpm.openharmony.cn/#/cn/detail/@trustdecision%2Fmobrisk 

### **权限声明** 

在工程的 module.json5 中声明以下权限: 

<!--必选权限--> ohos.permission.INTERNET ohos.permission.GET_NETWORK_INFO ohos.permission.GET_WIFI_INFO ohos.permission.STORE_PERSISTENT_DATA 

#### **权限说明** 

|**权限**|**说明**|
|---|---|
|**ohos.permission.INTERNET**(必选)|允许程序访问网络连接,发送请求与服务器进行 通信|
|**ohos.permission.GET_NETWORK_INFO**(必选)|获取网络连接状态信息|
|**ohos.permission.GET_WIFI_INFO**(必选)|获取当前WiFi接入的状态以及WLAN热点的信 息|
|**ohos.permission.STORE_PERSISTENT_DATA**(必 选)|允许应用存储持久化的数据|
|**ohos.permission.APPROXIMATELY_LOCATION**(可 选)|允许当前应用获取模糊定位信息|

## **加载和采集** 

### **注意事项** 

确保在用户同意隐私协议后,再进行SDK加载 

### **方法定义** 

public static async initWithOptions(context: Context, params: TDRiskOption): Promise<void> 

## **获取blackBox** 

### **注意事项** 

- 请在 initWithOptions 后调用 getBlackBoxAsync 

- 不要在 App 内对返回的 blackBox 进行缓存,获取 blackBox 请依赖 getBlackBoxAsync 方法 

### **方法定义** 

- /** 

- 异步方式获取blackbox 

- @param priorityCache blackbox获取优先级, 默认false 

- false: 等待数据上报完成后, 返回blackbox 

- true: 发起数据上报后, 优先使用缓存中的blackbox, 立即返回blackbox */ 

public static async getBlackBoxAsync(priorityCache: boolean = false): Promise<string> 

## **最佳实践** 

##### 1. 在应用首次加载时的 onCreate 方法中加载,并异步获取 blackBox 

```arkts
import AbilityStage from '@ohos.app.ability.AbilityStage'; import { TDRisk, TDRiskOption } from '@trustdecision/mobrisk'; 
export default class MyAbilityStage extends AbilityStage { async onCreate() { // 应用的HAP在首次加载时加载sdk const options: TDRiskOption = { /*************************** 必传 ***************************/ partnerCode: 'demo', // 同盾的合作方编码,请填写自身的合作方编码 appKey: 'appKey', // 配置AppKey,请联系同盾运营获取 country: TDRisk.COUNTRY_CN, // 国家地区参数,列表可以参考下文全部配置说明 /*************************** 必传 ***************************/ } if (用户同意隐私协议) { await TDRisk.initWithOptions(this.context, options) const blackbox: string = await TDRisk.getBlackBoxAsync() console.log('TD_TS', `init & get success blackbox:${blackbox}`) } } } 
```

##### 2. 在实际业务节点获取 blackbox 

###### // 比如注册的时候 

async function register(): Promise<void> { // ... 

```arkts
const blackbox: string = await TDRisk.getBlackBoxAsync(true) console.log('TD_TS', `get blackbox:${blackbox}`) //... } 
```

## **状态检查** 

1. 加载成功会在 logcat 中打印以下日志: 

TD_TS: td sdk init success 

2. SDK 上报数据成功,getBlackBoxAsync()返回的结果长度为26位字符串。 

3. 异常情况下,getBlackBoxAsync()返回的结果长度可能达到5000字符,详情可查看正常blackBox和降级 blackBox的差异 

# **其他说明** 

## **获取版本号** 

|**配置 key全部配置** const version:|**说明** string= TDRisk.getSDKVersion()|**示例代码**|
|---|---|---|
|partnerCode(必须)|合作方编码,请联系运营获取|options["partnerCode"] = "请输入您的合作方编 码"|
|appKey(必须)|应用标识,提供App的包名bundleName后联系运营获取appKey **bundleName获取方式:**AppScope/app.json5内bundleName对应的 value|options["appKey"] = "请输入您的appKey"|
|country(必须)|数据中心地区:TDRisk.COUNTRY_CN (中国)|options["country"] = "请输入您所在的国家地区"|
|appName|应用名称,请联系运营获取|options["appName"] = "请输入您的appName"|
|disableWifiInfo|禁止采集wifi信息(包含BSSID、SSID、Mac地址),默认允许|options["disableWifiInfo"] = true|
|disableODID|禁止采集odid,默认允许|options["disableODID"] = true|
|disableIP|禁止采集IP地址,默认允许|options["disableIP"] = true|
|disableWifiStatus|禁止采集WIFI状态,默认允许|options["disableWifiStatus"] = true|
|disableStorageInfo|禁止采集存储空间状态,默认允许|options["disableStorageInfo"] = true|
|disableScreenResolution|禁止采集屏幕分辨率,默认允许|options["disableScreenResolution"] = true|
|disableBatteryInfo|禁止采集电池电量状态,默认允许|options["disableBatteryInfo"] = true|
|disableCarrierInfo|禁止采集运营商信息,默认允许|options["disableCarrierInfo"] = true|
|disablePrivacyData|禁止隐私相关信息,默认允许|options["disablePrivacyData"] = true|
|httpTimeOut|网络请求回调的超时时间,单位毫秒,默认60000|options["httpTimeOut"] = 60000|
|customMessage|自定义消息,SDK支持透传和存储|options["customMessage"] = "customMessage"|
