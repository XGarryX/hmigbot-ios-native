## **初始化** 

### **方法定义** 

/** 

- 设备指纹初始化 

- @param context 上下文 

- @param params 初始化参数 

- */ 

public static async initWithOptions(context: Context, params: TDRiskOption): Promise<void> 

## **获取blackBox** 

### **注意事项** 

- 请在 initWithOptions 后调用 getBlackBoxAsync 

- 不要在 App 内对返回的 blackBox 进行缓存,获取 blackBox 请依赖 getBlackBoxAsync 方法 

### **方法定义** 

/** 

- 异步方式获取blackbox 

- @param priorityCache blackbox获取优先级, 默认false 

- false: 等待数据上报完成后, 返回blackbox 

- true: 发起数据上报后, 优先使用缓存中的blackbox, 立即返回blackbox 

- */ 

public static async getBlackBoxAsync(priorityCache: boolean = false): Promise<string> 

## **最佳实践** 

1. 在应用首次加载时的 onCreate 方法中调用初始化并异步获取 blackBox 

```arkts
import AbilityStage from '@ohos.app.ability.AbilityStage'; import { TDRisk, TDRiskOption } from '@trustdecision/mobrisk'; 
```

export default class MyAbilityStage extends AbilityStage { async onCreate() { 

// 应用的HAP在首次加载的时,为该Module初始化操作 

const options: TDRiskOption = { 

/*************************** 必传 ***************************/ partnerCode: 'demo', // 同盾的合作方编码,请填写自身的合作方编码 appKey: 'appKey', // 配置AppKey,请联系同盾运营获取 

country: TDRisk.COUNTRY_CN, // 国家地区参数,列表可以参考下文全部配置说明 /*************************** 必传 ***************************/ 

} 

if (用户同意隐私协议) { 

await TDRisk.initWithOptions(this.context, options) 

const blackbox = await TDRisk.getBlackBoxAsync() 

console.log('TD_TS', `init & get success blackbox:${blackbox}`) } 

} 

} 

#### 1. 在实际业务节点获取 blackbox 

##### // 比如注册的时候 

async function register(): Promise<void> { 

// ... 

const blackbox = await TDRisk.getBlackBoxAsync(true) 

console.log('TD_TS', `get blackbox:${blackbox}`) //... 

} 

## **状态检查** 

1. 初始化成功会在 logcat 中打印以下日志: 

TD_TS: td sdk init success 

1. SDK 上报数据成功,getBlackBoxAsync()返回的结果长度为26位字符串。 

2. 异常情况下,getBlackBoxAsync()返回的结果长度可能达到5000字符,详情可查看正常blackBox和降级 blackBox的差异 

# **其他说明** 

## **获取版本号** 

TDRisk.getSDKVersion() 

## **全部配置** 

|**配置 key**|**说明**|**示例代码**|
|---|---|---|
|partnerCode(必 须)|合作方编码,请联系运营获取|options["partnerCode"] = "请输入您的合作方编码"|
|appKey(必须)|应用标识,提供App的包名bundleName后联系运营获取appKey **bundleName获取方式:**AppScope/app.json5内bundleName对应的 value|options["appKey"] = "请输 入您的appKey"|
|country(必须)|数据中心地区:TDRisk.COUNTRY_CN (中国)|options["country"] = "请输 入您所在的国家地区"|
|appName|应用名称,请联系运营获取|options["appName"] = "请 输入您的appName"|
|disableGPS|禁止采集GPS位置信息,默认允许|options["disableGPS"] = true|
|disableWifiInfo|禁止采集wifi信息,默认允许|options["disableWifiInfo"] = true|
|disableODID|禁止采集odid,默认允许|options["disableODID"] = true|
|httpTimeOut|网络请求回调的超时时间,单位毫秒,默认60000|options["httpTimeOut"] = 60000|
|customMessage|自定义消息,SDK支持透传和存储|options["customMessage"] = "customMessage"|
