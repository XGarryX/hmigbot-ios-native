# IIFAA 鸿蒙本地免密SDK 接口文档 

# 初始化IfaaBaseInfo 

在使用SDK 前需要初始化IfaaBaseInfo 类。IfaaBaseInfo 类定义: 

class IfaaBaseInfo { authType: IfaaAuthTypeEnum = IfaaAuthTypeEnum.AUTHTYPE_FINGERPRINT; transactionID: string = ""; userID: string = ""; = transactionPayload: string ""; = transactionType: string ""; reasonTitle: string = ""; fallbackTitle: string = ""; } 

## IfaaBaseInfo 类字段说明 

|字段|类型|描述|
|---|---|---|
|authType|number|认证方式。取值详见IfaaAuthTypeEnum 中的枚 举值。|
|userID|string|用户ID 或者能够区别用户的唯一标识信息。|
|transactionID|string|能够唯一区别本次IFAA 操作的交易ID。此交易 ID 可以唯一定位此次操作。|
|transactionPayload|string|业务的附加信息,记录在ifaa log 中,作为扩|

|||展字段,可不设置。|
|---|---|---|
|transactionType|string|业务场景,比如登录:"Login",支付:"Pay"|
|reasonTitle|string|指纹认证弹框页面Title。|
|fallbackTitle|string|只有在认证流程中的指纹认证弹框页面,在错误 一次的后显示出的可选项按钮标题。|

# 查询设备支持的所有IFAA 认证类型 

ETASManager 中提供了查询当前设备支持的所有IFAA 认证类型的方法。定义如下: 

/** * 获取支持的生物认证类型 * @returns { IfaaAuthTypeEnum } IfaaAuthTypeEnum 生物认证类型枚举 */ static getSupportBIOTypes(): Array<IfaaAuthTypeEnum>{} 

IfaaAuthTypeEnum 定义如下: 

/** * 生物认证类型枚举 */ export enum IfaaAuthTypeEnum { // 指纹 AUTHTYPE_FINGERPRINT = 1, // 人脸 AUTHTYPE_FACE = 4 } 

示例代码: 

import { EtasManager, IfaaAuthTypeEnum, 

} from 'etaslibrary'; 

let list = EtasManager.getSupportBIOTypes(); 

this.saveLog("getSupportBIOTypes:" + JSON.stringify(list)); 

// 是否支持指纹 

if (list.includes(IfaaAuthTypeEnum.AUTHTYPE_FINGERPRINT)) { 

this.saveLog("支持指纹"); 

} 

// 是否支持人脸 

if (list.includes(IfaaAuthTypeEnum.AUTHTYPE_FACE)) { 

this.saveLog("支持人脸"); 

} 

# 检查是否录入指纹 

ETASManager 中提供了查询当前设备支持的所有IFAA 认证类型的方法。定义如下: 

/** * 检查是否录入指纹 * 

* @param { IfaaAuthTypeEnum } IfaaAuthTypeEnum 生物认证类型枚举 * @returns { boolean } 是否录入指纹结果 */ 

public static hasEnrolled(authType: IfaaAuthTypeEnum): boolean 

## 示例代码: 

let result = EtasManager.hasEnrolled(IfaaAuthTypeEnum.AUTHTYPE_FINGERPRINT); this.saveLog("指纹是否录入: " + result); 

let result = EtasManager.hasEnrolled(IfaaAuthTypeEnum.AUTHTYPE_FACE); this.saveLog("人脸是否录入: " + result); 

# 查看接入sdk 版本 

# IFAA 状态查询 

使用场景:状态查询主要用于客户APP 在需要确定用户是否已经在该终端注册过指纹的场景使 用,如用户启动新安装的客户APP 时,需要检查该用户是否已在该设备上注册过指纹,以避免 用户重复注册。 

SDK 提供EtasStatus 类进行IFAA 状态查询,主要有如下函数: 

// 查询ifaa 注册状态初始化 checkStatusInit() :Promise<EtasResult> // 查询手机终端是否已经注册 checkLocalStatus(ifaaRes: string) :Promise<EtasResult> 

@startumlautonumberparticipant "客户App" as App #skyBlueparticipant "eTAS_SDK" as SDK #darkOrangeparticipant "App 业务服务器" as AppServer #skyBlueparticipant "eTAS_BizServer" as Server #darkOrangeactivate AppApp ->SDK: 注册状态初始化 activate SDKSDK -> App: 返回note right App: 1、当code 为STATUS_REGISTERED 时,流 程结束\n2、当code 为SUCCESS 时,需继续执行deactivate SDKApp -> AppServer: 检查注 册状态(action 为request/cap)activate AppServerAppServer -> Server: 检查注册状态 note right of AppServer: 透传报文activate Servernote right of Server: 根据 userId、authType、transType、\nappId 等查询注册状态Server -> AppServer: 返回 deactivate ServerAppServer -> App: 返回deactivate AppServerApp -> SDK: 检查本地状 态activate SDKSDK -> App: 返回注册状态deactivate SDK@enduml 

1. 需要调用checkStatusInit() 方法来进行状态查询初始化。 

   - a. 当result.code 为IfaaErrorCodeEnum.STATUS_REGISTERED 时,表示本地取到了 token,已经是注册状态,无需请求服务端。 

   - b. 当result.code 为IfaaErrorCodeEnum.SUCCESS 时,result.msg 为发送到服务端的 报文。 

   - c. 当result.code 为其他code 时,APP 根据错误码进行处理。 

2. 调用checkLocalStatus() 方法来查询手机终端是否已经注册。传入参数为注册第一次请 求服务端返回的报文。 

   - a. 当result.code 为IfaaErrorCodeEnum.SUCCESS 时,已经注册。 

   - b. 当result.code 为IfaaErrorCodeEnum.STATUS_NOT_REGISTERED 时,未注册。 

   - c. 当result.code 为其他code 时,APP 根据错误码进行处理。 

## 示例代码: 

// 导入 import { EtasStatus, EtasResult, IfaaErrorCodeEnum, 

IfaaBaseInfo, 

} from 'etaslibrary'; 

// 初始化IfaaBaseInfo 

@State ifaabaseinfo: IfaaBaseInfo = new IfaaBaseInfo(); 

// todo,IfaaBaseInfo 的初始化 

// 初始化EtasStatus 

let status = new EtasStatus(this.ifaabaseinfo); 

// 调用查询状态初始化 

let result: EtasResult = await status.checkStatusInit(); 

// 当result.code 为STATUS_REGISTERED 时,已经注册。流程结束 

if (IfaaErrorCodeEnum.STATUS_REGISTERED == result.code) { this.saveLog("已经注册"); 

return; 

} 

// 当result.code 为SUCCESS 时,发送请求到服务端查询 

if (IfaaErrorCodeEnum.SUCCESS == result.code) { 

Logger.info(TAG, result.msg); 

let ifaaResp = ""; 

try { 

ifaaResp = await HttpUtils.request(this.url, result.msg); 

} catch (err) { Logger.error(TAG, err); this.saveLog("网络错误:" + err); return; } Logger.info(TAG, "获取到响应:" + ifaaResp); 

let result1 = await status.checkLocalStatus(ifaaResp); 

this.saveLog("checkLocalStatus:" + JSON.stringify(result1)); 

// 当result.code 为SUCCESS 时,已经注册 

if (IfaaErrorCodeEnum.SUCCESS == result1.code) { this.saveLog("已经注册"); } else if (IfaaErrorCodeEnum.STATUS_NOT_REGISTERED == result1.code) { this.saveLog("未注册"); } else { this.saveLog("异常:" + result1.toString()); } } else { this.saveLog("status.checkStatusInit error: " + result.msg); } 

# IFAA 注册 

SDK 对外提供EtasRegister 类实现IFAA 的注册流程,以下是主要的函数定义: 

// 注册初始化 regInit(): EtasResult // 执行注册操作 register(ifaaresp: string): Promise<EtasResult> // 完成注册操作 regFinish(): EtasResult 

1. 需要调用regInit() 方法来进行注册初始化,获取注册需要发送到服务端的报文。 

   - a. 当result.code 为IfaaErrorCodeEnum.SUCCESS 时,result.msg 为发送到服务端的 报文。 

   - b. 当result.code 为其他code 时,APP 根据错误码进行处理。 

2. 调用register() 方法来进行注册操作。传入参数为注册第一次请求服务端返回的报文。 

   - a. 当result.code 为IfaaErrorCodeEnum.SUCCESS 时,result.msg 为发送到服务端的 报文。 

   - b. 当result.code 为其他code 时,APP 根据错误码进行处理。 

3. 调用regFinish() 方法来完成注册操作。传入参数为注册第二次请求服务端返回的报 文。 

   - a. 当result.code 为IfaaErrorCodeEnum.SUCCESS 时,注册成功。 

   - b. 当result.code 为其他code 时,APP 根据错误码进行处理。 

## 示例代码: 

// 导入 import { EtasRegister, EtasResult, IfaaErrorCodeEnum, IfaaBaseInfo, 

} from 'etaslibrary'; 

// 初始化IfaaBaseInfo @State ifaabaseinfo: IfaaBaseInfo = new IfaaBaseInfo(); // todo,IfaaBaseInfo 的初始化 

// 初始化EtasRegister 

let ifaaRegister = new EtasRegister(this.ifaabaseinfo); 

// 调用注册初始化接口 

let result: EtasResult = ifaaRegister.regInit(); 

// 当result.code 异常时,流程中断 

if (IfaaErrorCodeEnum.SUCCESS != result.code) { 

this.saveLog("ifaaRegister.regInit error: " + result.msg); 

return; } 

// 当result.code 为IfaaErrorCodeEnum.SUCCESS 时,发送请求到服务端 Logger.info(TAG, "regInit: " + result.msg); 

let ifaaResp = ""; 

try { 

ifaaResp = await HttpUtils.request(this.url, result.msg); } catch (err) { Logger.error(TAG, err); this.saveLog("网络错误:" + err); return; } Logger.debug(TAG,"ifaa request 结果:" + JSON.stringify(ifaaResp)); 

// 调用注册接口,传入服务端返回报文 let ifaaResult = await ifaaRegister.register(ifaaResp); Logger.debug(TAG,"ifaa register 结果:" + JSON.stringify(ifaaResult)); 

// 当ifaaResult.code 异常时,流程中断 if (IfaaErrorCodeEnum.SUCCESS != ifaaResult.code) { this.saveLog("ifaaRegister.register error: " + ifaaResult.msg); return; } 

// 当ifaaResult.code 为IfaaErrorCodeEnum.SUCCESS 时,发送请求到服务端 let ifaaResp1 = ""; 

try { ifaaResp1 = await HttpUtils.request(this.url, ifaaResult.msg); } catch (err) { this.saveLog("网络错误1:" + err); return; } 

// 调用注册完成接口,传入服务端返回报文 let ifaaResult2 = ifaaRegister.regFinish(ifaaResp1); this.saveLog("ifaa respose 结果:" + JSON.stringify(ifaaResult2)); 

// 当ifaaResult2.code 为IfaaErrorCodeEnum.SUCCESS 时,注册成功 if (IfaaErrorCodeEnum.SUCCESS == ifaaResult2.code) { this.saveLog("注册成功"); } else { 

this.saveLog("注册失败"); } 

# IFAA 认证 

SDK 对外提供EtasAuthentication 类实现IFAA 的认证流程,以下是主要的函数定义: 

// 认证初始化 authInit(): EtasResult // 执行认证操作 auth(ifaaresp: string): Promise<EtasResult> // 完成认证操作 authFinish(): EtasResult 

1. 调用authInit() 方法来进行认证初始化,获取认证需要发送到服务端的报文。 

   - a. 当result.code 为IfaaErrorCodeEnum.SUCCESS 时,result.msg 为发送到服务端的 报文。 

   - b. 当result.code 为其他code 时,APP 根据错误码进行处理。 

2. 调用auth() 方法来进行认证操作。传入参数为认证第一次请求服务端返回的报文。 

   - a. 当result.code 为IfaaErrorCodeEnum.SUCCESS 时,result.msg 为发送到服务端的 报文。 

   - b. 当result.code 为其他code 时,APP 根据错误码进行处理。 

3. 调用authFinish() 方法来完成认证操作。传入参数为认证第二次请求服务端返回的报 文。 

   - a. 当result.code 为IfaaErrorCodeEnum.SUCCESS 时,认证成功。 

   - b. 当result.code 为IfaaErrorCodeEnum.WRONG_AUTHDATAINDEX 时,APP 侧进行有效身 份认证后,调用指纹更新流程。 

## c. 当result.code 为其他code 时,APP 根据错误码进行处理。 

## 示例代码: 

// 导入 import { EtasAuthentication, EtasResult, IfaaErrorCodeEnum, IfaaBaseInfo, 

} from 'etaslibrary'; 

// 初始化IfaaBaseInfo 

@State ifaabaseinfo: IfaaBaseInfo = new IfaaBaseInfo(); // todo,IfaaBaseInfo 的初始化 

// 初始化EtasAuthentication 

let ifaaAuth = new EtasAuthentication(this.ifaabaseinfo); 

// 调用认证初始化接口 

let result: EtasResult = ifaaAuth.authInit(); 

// 当result.code 异常时,流程中断 

if (IfaaErrorCodeEnum.SUCCESS != result.code) { this.saveLog("ifaaAuth.authInit error: " + result.msg); 

return; } 

// 当result.code 为IfaaErrorCodeEnum.SUCCESS 时,发送请求到服务端 Logger.info(TAG, "authInit: " + result.msg); 

```arkts
let ifaaResp = ""; try { ifaaResp = await HttpUtils.request(this.url, result.msg); } catch (err) { Logger.error(TAG, err); 
```

this.saveLog("网络错误:" + err); return; } Logger.debug(TAG,"ifaa request 结果:" + JSON.stringify(ifaaResp)); 

// 调用认证接口,传入服务端返回报文 let ifaaResult = await ifaaAuth.auth(ifaaResp); Logger.debug(TAG,"ifaa register 结果:" + JSON.stringify(ifaaResult)); 

// 当ifaaResult.code 异常时,流程中断 if (IfaaErrorCodeEnum.SUCCESS != ifaaResult.code) { this.saveLog("ifaaAuth.auth error: " + result.msg); return; } 

// 当ifaaResult.code 为IfaaErrorCodeEnum.SUCCESS 时,发送请求到服务端 let ifaaResp1 = ""; try { ifaaResp1 = await HttpUtils.request(this.url, ifaaResult.msg); } catch (err) { this.saveLog("网络错误1:" + err); return; } 

// 调用认证完成接口,传入服务端返回报文 let ifaaResult2 = ifaaAuth.authFinish(ifaaResp1); // 当ifaaResult2.code 为IfaaErrorCodeEnum.SUCCESS 时,认证成功 if (IfaaErrorCodeEnum.SUCCESS == ifaaResult.code) { this.saveLog("认证成功"); } else { this.saveLog("认证失败"); } 

// 如code 为WRONG_AUTHDATAINDEX 时,触发指纹更新,调用指纹更新流程 if (IfaaErrorCodeEnum.WRONG_AUTHDATAINDEX == ifaaResult2.code) { let updater = new EtasTemplateUpdater(this.ifaabaseinfo); 

// 调用指纹更新初始化接口 let result: EtasResult = updater.templateUpdaInit(ifaaResult2.msg); Logger.info(TAG, "指位更新报文:" + result.msg); try { ifaaResp = await HttpUtils.request(this.url, result.msg); } catch (err) { this.saveLog("网络错误:" + err); return; } // 指纹更新 let result2 = updater.templateUpdaFinish(ifaaResp); this.saveLog("更新指位结果:" + JSON.stringify(result2)); } 

# IFAA 指纹更新 

## 当IFAA 认证流程中authFinish 返回的code 为WRONG_AUTHDATAINDEX 时,触发指纹更 新,调用指纹更新流程 。 

SDK 对外提供EtasTemplateUpdater 类实现IFAA 的指纹更新流程,以下是主要的函数定 

义: 

// 指纹更新初始化 templateUpdaInit(ifaaMessage: string):EtasResult // 执行指纹更新操作 templateUpdaFinish(ifaaResp: string):EtasResult 

1. 调用templateUpdaInit() 方法来进行指纹更新初始化,传入认证流程authFinish 返回 的msg。获取指纹更新需要发送到服务端的报文。 

   - a. 当result.code 为IfaaErrorCodeEnum.SUCCESS 时,result.msg 为发送到服务端的 报文。 

   - b. 当result.code 为其他code 时,APP 根据错误码进行处理。 

2. 调用templateUpdaFinish() 方法来进行认证操作。传入参数为指纹更新请求服务端返回 的报文。 

   - a. 当result.code 为IfaaErrorCodeEnum.SUCCESS 时,指纹更新成功。 

   - b. 当result.code 为其他code 时,APP 根据错误码进行处理。 

# IFAA 注销 

SDK 对外提供EtasDeregister 类实现IFAA 的注销流程,以下是主要的函数定义: 

### // 注销初始化 

deregInit():EtasResult 

// 执行注销操作 

dereg(ifaaDeRegResponse: string) :Promise<EtasResult>

1. 调用deregInit() 方法来进行注销初始化,获取注销需要发送到服务端的报文。 

   - a. 当result.code 为IfaaErrorCodeEnum.SUCCESS 时,result.msg 为发送到服务端的 报文。 

   - b. 当result.code 为其他code 时,APP 根据错误码进行处理。 

2. 调用dereg() 方法来进行注销操作。传入参数为认证第一次请求服务端返回的报文。 

   - a. 当result.code 为IfaaErrorCodeEnum.SUCCESS 时,注销成功。 

   - b. 当result.code 为其他code 时,注销失败。 

示例代码: 

// 导入 import { EtasDeregister, EtasResult, IfaaErrorCodeEnum, IfaaBaseInfo, } from 'etaslibrary'; 

// 初始化IfaaBaseInfo @State ifaabaseinfo: IfaaBaseInfo = new IfaaBaseInfo(); // todo,IfaaBaseInfo 的初始化 

// 初始化ifaaDeregister 

let ifaaDeregister = new EtasDeregister(this.ifaabaseinfo); 

// 调用注销初始化接口 

let result: EtasResult = ifaaDeregister.deregInit(); 

// 当result.code 异常时,流程中断 if (IfaaErrorCodeEnum.SUCCESS != result.code) { this.saveLog("ifaaDeregister.deregInit error: " + result.msg); return; } 

// 当result.code 为IfaaErrorCodeEnum.SUCCESS 时,发送请求到服务端 Logger.info(TAG, "deregInit: " + result.msg); 

```arkts
let ifaaResp = ""; try { ifaaResp = await HttpUtils.request(this.url, result.msg); } catch (err) { Logger.error(TAG, err); this.saveLog("网络错误:" + err); return; } Logger.debug(TAG,"ifaa request 结果:" + JSON.stringify(ifaaResp)); 
```

// 调用注销接口,传入服务端返回报文 

let ifaaResult = await ifaaDeregister.dereg(ifaaResp); 

Logger.debug(TAG,"ifaaDeregister dereg 结果:" + JSON.stringify(ifaaResult)); 

// ifaaResult.code 为IfaaErrorCodeEnum.SUCCESS 时,注册成功 

if (IfaaErrorCodeEnum.SUCCESS == ifaaResult.code) { 

this.saveLog("注销成功"); 

} else { this.saveLog("注销失败"); 

} 

# 错误码IfaaErrorCodeEnum 的枚举值 

## EtasResult 实体类中的code 的枚举 

|枚举值|值|业务意义|
|---|---|---|
|SUCCESS|0|成功|
|STATUS_NOT_SUPPORT|1|终端不支持IFAA|
|STATUS_NOT_ENROLLED|4|终端没有录入指纹/人脸(此时可以引 导用户去录入指纹/人脸再做操作)|
|STATUS_NOT_REGISTERED|5|IFAA 尚未注册(比如认证/注销/指位 更新等操作都需要注册后才可以进行)|
|||IFAA 已经注册(checkStatusInit 中|
|STATUS_REGISTERED|6|返回,表示已经是注册状态,无需发 送请求到服务端查询)|
|CLIENT_ERROR|8|SDK 本地执行异常|

|SERVER_ERROR|9|服务器错误|
|---|---|---|
|WRONG_AUTHDATAINDEX|11|指纹不匹配,需要更新指纹 (authFinish 中返回时,进行更新指 纹流程)|
|POLICY_REJECTED|12|被风险策略拒绝时(IFAA 服务端返 回)|
|USER_REJECTED|13|用户被禁用时(IFAA 服务端返回)|
|||应用标识白名单中未设置,需要在|
|APPID_NOT_FOUNDAPPID_NOT_FOUND|14|IFAA 服务端添加该应用标识(IFAA 服 务端返回)|
|DEVICE_MODEL_NOT_FOUND|15|设备型号不存在(IFAA 服务端返回)|
|ERR_SIGNATURE_FAIL|16|未获取到签名数据(IFAA 服务端返 回)|
|STATUS_RESULT_CANCELED|19|用户取消,APP 侧可切换其他认证方 式。|
|STATUS_RESULT_TIMEOUT|20|认证流程开始时,长时间未进行生物 认证,认证超时,APP 侧可切换其他认 证方式。|
|STATUS_RESULT_AUTH_FAIL|21|验证失败,生物认证不匹配,APP 侧可 切换其他认证方式。|
|STATUS_RESULT_SYSTEM_BLOCK|22|连续多次校验失败,指纹校验被暂时 锁定,APP 侧可切换其他认证方式。|

|STATUS_RESULT_FALLBACK|23|点击了生物认证页面的FALLBACK 按 钮,APP 侧可切换其他认证方式。|
|---|---|---|
|STATUS_RESULT_TEE_ERROR|24|TEE 错误,APP 侧可提示系统异常|
|PERMISSION_DENIED|26| 
Android:当前设备未获取相机权限
 
IOS:当前应用未获取Face ID 权限|
|AUTHENTICATOR_DISABLE|27|认证器被禁用(IFAA 服务端返回)|
|AUTHENTICATOR_NOT_FOUND|28|未找到相应的认证器(IFAA 服务端返 回)|
|DEVICE_KEY_NOT_FOUND|29|设备密钥被禁用(IFAA 服务端返回)|

# 拉起系统设置指纹界面方法 

Button('跳转设置指纹页面') 

```arkts
.onClick(() => { let context = getContext() as common.UIAbilityContext; let want: Want = { bundleName: 'com.huawei.hmos.settings', abilityName: 'com.huawei.hmos.settings.MainAbility', uri: 'biometrics_and_password_settings' }; context.startAbility(want) .then(() => { // ... }) .catch((err: BusinessError) => { 
```

console.error(`Failed to startAbility. Code: ${err.code}, message: 

${err.message}`); 

}); })
