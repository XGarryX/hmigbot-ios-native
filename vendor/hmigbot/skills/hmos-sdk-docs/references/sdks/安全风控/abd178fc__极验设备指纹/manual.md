# **资源与概述** 

GeeGaurd HarmonyOS SDK 提供给集成鸿蒙 Next 原生客户端开发的开发者使用。 

# **环境要求** 

|**条目**|**资源**|
|---|---|
|开发目标|HarmonyOS Next|
|开发环境|DevEco Studio 5.0.3.403|
|API版本|API 12|
|SDK三方依赖|无|

# **集成** 

## **获取 SDK** 

请联系您的对接人。 

## **导入 SDK** 

将 zip 包中的 .har 文件(包括 geetest_geeguard_harmonyos_vx.y.z_date.har )拖拽到工程中的 libs 文件夹下,在拖入 .har 到 libs 文件夹后,还要检查 .har 是否被添加到 Library ,要在项目的 ohpackage.json5 下添加如下代码: 

- 1 "dependencies": { 2 "geeguardSdk": "file:./libs/geetest_geeguard_harmonyos_vx.y.z_date.har" 3 } 

### **添加权限声明** 

- 1 // 必须权限 

- 2 ohos.permission.INTERNET 

- 3 ohos.permission.STORE_PERSISTENT_DATA 

- 4 ohos.permission.GET_NETWORK_INFO 5 // 可选权限 6 ohos.permission.APP_TRACKING_CONSENT 

### **权限说明** 

|**权限名称**|**功能说明**|**使用场景**|**备注**|
|---|---|---|---|
|INTERNET|允许应用程序联网|用于访问服务|必须|
|GET_NETWORK_INFO|访问当前网络状态|判断当前网络处于移动网络或WiFi 网络需要此权限|必须|
|STORE_PERSISTENT_DATA|持久化存储数据|用于安全风控和生成新的设备标识|必须|
|APP_TRACKING_CONSENT|获取开放匿名设备标识 符(OAID)|用于安全风控和生成新的设备标识|动态权 限,可选|

## **配置混淆规则** 

极验 SDK 已做混淆处理,集成时请带上混淆规则,勿再次混淆 SDK 

## **调用逻辑** 

1. 在后台注册 AppID 

2. 使用 AppID 获取 GeeGuardReceipt 

- 集成代码参考下方的代码示例 

# **代码示例** 

该示例适用于 1.0.0+ 版本 

## **应用启动后立即注册 appID** 

- 1 export default class MainAbilityStage extends AbilityStage { 

- 2 // 您申请的 AppID 3 private static readonly GEEGUARD_APP_ID = '123456789012345678901234567890ab' 

- 4 5 onCreate() { 6 GeeGuard.register(this.context, MainAbilityStage.GEEGUARD_APP_ID); 7 } 8 } 

## **获取 GeeToken** 

使用 GeeGuard SDK 对数据进行签名,并获取环境检测 GeeToken: 

- 1 // 直接获取 GeeToken,需在服务端解析结果 

- 2 async function getGeeToken(context: Context) { 3 // 唯一标记本次业务的流水号或凭证,用于防止 GeeToken 从业务场景剥离 4 // 如果无防止 GeeToken 从业务场景剥离的需求,data 可以传入 null 5 let data = '唯一标记本次业务的流水号或凭证,用于防止 GeeToken 从业务场景剥离'; 

- 6 

- 7 let receipt = await GeeGuard.fetchReceipt(context, data); 

|8 9|if(!receipt || !receipt.geeToken) { console.error('无法获取GeeGuardReceipt,请检查是否已通过GeeGuard.register(appId)注 册AppID');|
|---|---|
|10 11|return; }|
|12 13|//随业务数据一同提交,请在服务端获取最终的环境识别结果及指纹|
|14|//接口参数请参考服务端文档|
|15|console.log(`GeeToken: ${receipt.geeToken}`);|
|16|}|
|17||
|18 19|//获取respondedGeeToken,需在服务端解析结果 //此方法回调为异步|
|20|function getRespondedGeeToken(context: Context) {|
|21|//唯一标记本次业务的流水号或凭证,用于防止GeeToken从业务场景剥离|
|22|//如果无防止GeeToken从业务场景剥离的需求,data可以传入null|
|23|let data = '唯一标记本次业务的流水号或凭证,用于防止GeeToken从业务场景剥离';|
|24||
|25|GeeGuard.submitReceipt(context,data, {|
|26|onCompletion: (status: number,receipt: GeeGuardReceipt| undefined)=>{|
|27|if(status === 200) {|
|28|if(!receipt || !receipt.respondedGeeToken) {|
|29|console.error('无法获取respondedGeeToken,请检查是否已通过|
||GeeGuard.register(appId)注册AppID');|
|30|return;|
|31|}|
|32|//随业务数据一同提交,请在服务端获取最终的环境识别结果及指纹|
|33|//接口参数请参考服务端文档|
|34|console.log(`RespondedGeeToken: ${receipt.respondedGeeToken}`);|
|35|}else{|
|36|// SDK获取respondedGeeToken错误,请参考下面的错误码清单|
|37|console.log(`Status: ${status}`);|
|38|}|
|39|}|
|40|});|
|41|}|

### **错误码清单** 

异步获取方法 GeeGuard.submitReceipt(Context, string, GeeGuardCallbackHandler) 中可能返回的错误 码有: 

|**错误码**|**描述**|
|---|---|
|-200|未注册AppID,请在启动后注册AppID|
|-300|网络错误,详细见日志中tag为 GeeGuard 的stacktrace|
|-500|服务响应格式异常,详细请查看 receipt.originalResponse|
|-501|服务响应失败,详细请查看 receipt.originalResponse|

## **查询 GeeToken 结果** 

将 respondedGeeToken 或 GeeToken 跟随业务数据一起提交到业务的服务端,服务端再向极验设备指纹服务查 询结果。详细见服务端文档。 

|**更新说明**||
|---|---|
|**版本号更新内容**|**日期**|
|**1.0.0** 1.修复部分场景下可能出现的崩溃|2024-06-18|
