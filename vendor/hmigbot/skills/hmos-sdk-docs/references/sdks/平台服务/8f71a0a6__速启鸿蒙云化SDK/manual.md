# 鸿蒙云应用SDK对接文档 

一、集成准备 引入SDK 二、接口对接 2.1 SDK初始化 

2.2 启动云应用 2.3 结束SDK 

2.4 发送自定义消息到云机内应用 三、 错误码说明 

## 一、集成准备 

请从鸿蒙官方渠道或者速启官网https://suqi.tech/获取对应版本的云应用SDK包(squnisdk-hcs-xxx.har) 

### 引入SDK 

步骤1:工程创建 libs 目录,将sdk squnisdk-hcs-1.0.x.har 存放到该目录下 

步骤2: 工程对应模块的 oh-package.json5 加入依赖配置 

示例: 

"dependencies": { "@sqcloud/squnisdk": "file:../../libs/squnisdk-hcs-1.0.1.har" } 

## 二、接口对接 

### 2.1 SDK初始化 

CloudSdk.init(appContext: Context, initConfig: SdkInitConfig, navStack?: NavPathStack): boolean 

功能描述:APP启动的时候调用,建议放在EntryAbility 类的 onCreate()调用。 参数描述: 

|参数|是否必传|类型|描述|
|---|---|---|---|
|appContext|是|ApplicationContext|应用上下文|
|initConfig|是|SdkInitConfig|初始化配置参数|
|navStack|是|NavPathStack|APP层已创建的页面路由栈|
|配置参数介绍-SdkInitConfig:||||
|参数|是否必传|类型|描述|
|sdkInitConfig.businessInfo.appL icenseKey|是|String|申请接入云应用平台预先获得的 appKey, 建议存放在您的后台,然后再由app 走http向您的后台获取|

sdkInitConfig.onSdkInitListener 是 函数 回调消息体结构介绍: export interface CloudSdkCbMessage { action: CloudSdkCallbackAction,//执行事 件类型(ON_SDK_INIT_RESULT) data: string | null, code: string | null, //错误码(CloudSdkCallbackCode. SUCCESS|CloudSdkCallbackCode.F AILURE) } 

示例: 

let sdkInitConfig = new SdkInitConfig(); 

sdkInitConfig.businessInfo = new BusinessInfo(); sdkInitConfig.businessInfo.appLicenseKey = "通过商务渠道分配给您的appKey字符串"; sdkInitConfig.onSdkInitListener = (message: string) => {};// 在这里实现初始化回调的监听器逻辑 NavigationManager.init(new NavPathStack());//先创建app上层自己的页面路由管理栈并传入到sdk CloudSdk.init(context, sdkInitConfig, NavigationManager.getInstance()); 

### 2.2 启动云应用 

CloudSdk.start(uiContext: UIContext, startConfig: SdkStartConfig): Promise<boolean> 

#### 功能描述:执行启动云应用串流 

#### 参数描述: 

|参数|是否必传|类型|描述|
|---|---|---|---|
|uiContext|是|UIContext|UI 上下文|
|startConfig|是|SdkStartConfig|启动参数配置类|

#### 配置参数介绍-SdkStartConfig: 

|参数|是否必传|类型|描述|
|---|---|---|---|
|userId|是|string|您的APP注册用户唯一ID|
|pkgName|是|string|您要启动云机应用(Android)的ap p包名|
|appConfig|是|string|如果启动前用户已执行登录APP,请 将APP的登录态信息传入到云机Andr oid应用,云机Android应用如何接 收?请另参考文档《安卓APP云化修 改文档》第2.2 章节。 如果启动前用户未登录,可传空或 不传。 如果启动前用户未登录,在进入云 机应用后再执行登录操作,登录态 需要走自定义消息通道透传,参见 本文档以下回调事件“ON_EXTRA_MS 和 本文档的第2.4 章节接口。 G”|

|onCloudSdkListener|是|函数|接收SDK的回调消息函数,比如接收 来自android云应用的消息通信【发 起订单支付、 自定义透传消息(如:动态登录) 】 支付( )和自定义消息( ON_PAYMENT ON )的消息发送源请另参考 _EXTRA_MSG 文档:《安卓APP云化修改文档》第 2.3 章节、第2.4 章节。 示范代码及描述: // 设置云SDK监听器 startConfig.onCloudSdkListener = (jsonMessage: string) => { const msg: CloudSdkCbMessage = JSON.parse(jsonMessage); }; // 回调消息体结构 export interface CloudSdkCbMessage { action: CloudSdkCallbackAction; // 执行事件类型 data: string | null; // 消息数据 code: string | null; // 错误码(SUCCESS/FAILURE) } // 执行事件类型定义 enum CloudSdkCallbackAction { ON_LAUNCH_SUCCESS = "onLaunchSuccess", // 进入云应用成功 ON_LAUNCH_FAILURE = "onLaunchFailure", // 进入云应用失败 ON_TERMINATED = "onTerminated", // 结束云应用串流 ON_USER_EXIT = "onUserExit", //
用户主动退出云应用串流
ON_PAYMENT = "onPayment", //
云应用发起订单支付消息
ON_EXTRA_MSG = "onExtraMsg" //
云应用发送自定义消息到鸿蒙app端
}|
|---|---|---|---|

示例: 

```arkts
let startConfig = new SdkStartConfig(); startConfig.userId = "您的注册用户唯一ID"; startConfig.pkgName = "您要启动云机应用(Android)的app包名"; startConfig.appConfig = "已登录APP的状态信息透传到云机内Android应用消息"; startConfig.onCloudSdkListener = (jsonMessage: string) => { //接收SDK的回调消息函数 } CloudSdk.start(uiContext, startConfig); 
```

### 2.3 结束SDK 

CloudSdk.fini(); 

功能描述:结束SDK,释放sdk资源,建议在退出app 的时候调用,fini 与 init 两个接口是匹配对应使用。 

### 2.4 发送自定义消息到云机内应用 

CloudSdk.sendExtraMsgToCloud(extraMsg: string) 

功能描述:从鸿蒙app端侧发送自定义消息到云机Android应用端,云机Android应用端如何接收?请另参考文档《安卓APP云化修改文档》 第2.1 章节。 

参数描述: 

|参数|是否必传|类型|描述|
|---|---|---|---|
|extraMsg|是|string|自定义的透传消息数据体|

## 三、 错误码说明 

|5021002|CLOUD_APP_RET_CODE_INVALID_TOKEN|启动token失效|
|---|---|---|
|5021009|CLOUD_APP_RET_CODE_DUPLICATE_USER|用户在其它端有重复登录|
|5021018|CLOUD_APP_RET_CODE_GAME_MAINTENANCE|应用内部维护|
|5021019|CLOUD_APP_RET_CODE_POOR_NETWORK|当前网络状态不稳定|
|5021202|CLOUD_APP_RET_CODE_REQUEST_ERROR_APP_A PPLY|启动云应用失败|
|5021305|ERR_CODE_NETWORK_UNAVAILABLE|网络不可用|
