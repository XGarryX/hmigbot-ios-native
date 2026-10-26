# IFAA 鸿蒙生物识别SDK下载与接入 

- N. 概述 

- O. 开发工具 

- P. SDK接入流程 

   - P.N. 添加 IFAA 生物认证服务SDK 

##### P.O. 初始化 IfaaBaseInfo 

   - P.P. 查询设备支持的所有 IFAA 认证类型 

   - P.Q. 检查是否录入指纹 

   - P.S. 查看接入sdk版本 

- Q. IFAA 功能 

   - Q.N. IFAA状态查询 

   - Q.O. IFAA注册 

   - Q.P. IFAA认证 

   - Q.Q. IFAA指纹更新 

   - Q.S. IFAA注销 

- S. 错误码 

S.N. IfaaErrorCodeEnum 的枚举值 

- T. SDK下载地址 

- V. 常见问题 

V.N. 注册流程报The service is abnormal错误 

- V.O. 拉起系统设置指纹界面方法 

## **1.** 概述 

IFAA 鸿蒙生物识别SDK 为应用提供本地免密登录,保障身份认证安全、交易安全,简化用户认 证流程、保护个人隐私数据,降低运营风险和认证成本。 

- IFAA鸿蒙生物识别SDK后续可能会根据手机厂商的ROM进行适配调整 

- 建议手机使用鸿蒙系统next版本3.0.0.22及以上版本,较早系统版本可能存在认证错误(如指 纹不匹配,需要更新指纹)的问题 

1 

## **2.** 开发工具 

推荐使用新版 IDE 进行开发。IDE下载地址: 

- 华为 DevEco Studio NEXT Beta1 

- 开发环境版本信息: ● 版本: DevEco Studio 5.0.3.806 ● 构建时间: 2024年9月18日 ● 运行环境: macOS 14.6.1, OpenJDK 64-Bit Server VM 17.0.10+1-b1087.17 aarch64 

## **3.** SDK接入流程 

### **3.1.** 添加 IFAA 生物认证服务SDK 

添加 SDK 包到项目中,如图所示: 

entry模块的oh-package.json5 增加依赖: 

JSON

1 {
2   ...
3 "dependencies": {
4     //  引用 .har 包
5 "etaslibrary": "file:../entry/src/libs/etasLibrary.har"
6   }
7 }

### **3.2.** 初始化 IfaaBaseInfo 

2 

在使用 SDK 前需要初始化 IfaaBaseInfo 类。IfaaBaseInfo 类定义: 

TypeScript 

- `class IfaaBaseInfo { 2 authType: IfaaAuthTypeEnum = IfaaAuthTypeEnum.AUTHTYPE_FINGERPRINT;` 

- `transactionID: string = "";` 

- `userID: string = "";` 

- `transactionPayload: string = "";` 

- `transactionType: string = "";` 

- `reasonTitle: string = "";` 

- `fallbackTitle: string = ""; 9 }` 

#### IfaaBaseInfo 类字段说明 

|字段|类型|描述|
|---|---|---|
|authType|number|认证方式。取值详见IfaaAuthTypeEnum中的枚举值。|
|userID|string|用户ID或者能够区别用户的唯一标识信息。|
|transactionID|string|能够唯一区别本次IFAA操作的交易ID。此交易ID可以唯 一定位此次操作。|
|transactionPayload|string|业务的附加信息,记录在ifaa log中,作为扩展字段, 可不设置。|
|transactionType|string|业务场景,比如登录:"Login",支付:"Pay"|
|reasonTitle|string|指纹认证弹框页面Title。|
|fallbackTitle|string|只有在认证流程中的指纹认证弹框页面,在错误一次的 后显示出的可选项按钮标题。|

### **3.3.** 查询设备支持的所有 IFAA 认证类型 

ETASManager 中提供了查询当前设备支持的所有 IFAA 认证类型的方法。定义如下: 

3 

- `/** 2 *` 获取支持的生物认证类型 

- `* @returns { IfaaAuthTypeEnum } IfaaAuthTypeEnum` 生物认证类型枚举 `4 */ 5 static getSupportBIOTypes(): Array<IfaaAuthTypeEnum>{}` 

#### IfaaAuthTypeEnum定义如下: 

ArkTS 

- `/**` 

- `*` 生物认证类型枚举 

- `*/ 4 export enum IfaaAuthTypeEnum {` 

- `//` 指纹 

- `AUTHTYPE_FINGERPRINT = 1,` 

- `//` 人脸 `8 AUTHTYPE_FACE = 4 9 }` 

#### 示例代码: 

4 

TypeScript 

- `1` 

- `import { 3 EtasManager, 4 IfaaAuthTypeEnum, 5 } from 'etaslibrary';` 

- `6` 

- `7` 

- `8` 

- `let list = EtasManager.getSupportBIOTypes();` 

- `this.saveLog("getSupportBIOTypes` : `" + JSON.stringify(list));` 

- `12` 

- `//` 是否支持指纹 `14 if (list.includes(IfaaAuthTypeEnum.AUTHTYPE_FINGERPRINT)) {` 

- `" "` 

- `this.saveLog(` 支持指纹 `); 16 }` 

- `17` 

- `//` 是否支持人脸 `19 if (list.includes(IfaaAuthTypeEnum.AUTHTYPE_FACE)) {` 

- `" "` 

- `this.saveLog(` 支持人脸 `); 21 }` 

### **3.4.** 检查是否录入指纹 

ETASManager 中提供了查询当前设备支持的所有 IFAA 认证类型的方法。定义如下: 

- `/**` 

- `*` 检查是否录入指纹 

- `*` 

- `* @param { IfaaAuthTypeEnum } IfaaAuthTypeEnum` 生物认证类型枚举 

- `* @returns { boolean }` 是否录入指纹结果 

- `*/ 7 public static hasEnrolled(authType: IfaaAuthTypeEnum): boolean` 

示例代码: 

5 

- `let result = EtasManager.hasEnrolled(IfaaAuthTypeEnum.AUTHTYPE_FINGERPRINT) ;` 

- `this.saveLog("` 指纹是否录入 `: " + result);` 

- `3` 

- `let result = EtasManager.hasEnrolled(IfaaAuthTypeEnum.AUTHTYPE_FACE); 5 this.saveLog("` 人脸是否录入 `: " + result);` 

### **3.5.** 查看接入sdk版本 

## **4.** IFAA 功能 

### **4.1.** IFAA状态查询 

使用场景:状态查询主要用于客户APP在需要确定用户是否已经在该终端注册过指纹的场景使用,如用 户启动新安装的客户APP时,需要检查该用户是否已在该设备上注册过指纹,以避免用户重复注册。 

SDK 提供 `EtasStatus` 类进行 IFAA状态查询,主要有如下函数: 

6 

- `//` 查询 `ifaa` 注册状态初始化 

- `checkStatusInit() :Promise<EtasResult>` 

- `3` 

- `//` 查询手机终端是否已经注册 

- `checkLocalStatus(ifaaRes: string) :Promise<EtasResult>` 

客户App eTAS_SDK App业务服务器 eTAS_BizServer
1 注册状态初始化
2 返回
1、当code为STATUS_REGISTERED时,流程结束
2、当code为SUCCESS时,需继续执行
3 检查注册状态(action为request/cap)
4 检查注册状态
透传报文
根据userId、authType、transType、
appId等查询注册状态
5 返回
6 返回
7 检查本地状态
8 返回注册状态
客户App eTAS_SDK App业务服务器 eTAS_BizServer

1. 需要调用 checkStatusInit() 方法来进行状态查询初始化。 

   - a. 当 result.code 为 IfaaErrorCodeEnum.STATUS_REGISTERED 时,表示本地取到了 token, 已经是注册状态,无需请求服务端。 

   - b. 当 result.code 为 IfaaErrorCodeEnum.SUCCESS 时,result.msg 为发送到服务端的报文。 

   - c. 当 result.code 为其他 code 时,APP 根据错误码进行处理。 

- 一 

- 2. 调用 checkLocalStatus() 方法来查询手机终端是否已经注册。传入参数为注册第 次请求服务端 返回的报文。 

   - a. 当 result.code 为 IfaaErrorCodeEnum.SUCCESS 时,已经注册。 

   - b. 当 result.code 为 IfaaErrorCodeEnum.STATUS_NOT_REGISTERED 时,未注册。 

   - c. 当 result.code 为其他 code 时,APP 根据错误码进行处理。 

7 

#### 示例代码: 

8 

TypeScript 

- `//` 导入 

- `import {` 

- `EtasStatus,` 

- `EtasResult,` 

- `IfaaErrorCodeEnum,` 

- `IfaaBaseInfo,` 

- `} from 'etaslibrary';` 

- `8` 

- `//` 初始化 `IfaaBaseInfo` 

- `@State ifaabaseinfo: IfaaBaseInfo = new IfaaBaseInfo();` 

- `// todo` , `IfaaBaseInfo` 的初始化 

- `12` 

- `13` 

- `//` 初始化 `EtasStatus` 

- `let status = new EtasStatus(this.ifaabaseinfo);` 

- `16` 

- `//` 调用查询状态初始化 

- `let result: EtasResult = await status.checkStatusInit();` 

- `19` 

- `//` 当 `result.code` 为 `STATUS_REGISTERED` 时,已经注册。流程结束 

- `if (IfaaErrorCodeEnum.STATUS_REGISTERED == result.code) {` 

- `" "` 

- `this.saveLog(` 已经注册 `);` 

- `return;` 

- `}` 

- `25` 

- `//` 当 `result.code` 为 `SUCCESS` 时,发送请求到服务端查询 

- `if (IfaaErrorCodeEnum.SUCCESS == result.code) {` 

- `Logger.info(TAG, result.msg);` 

- `let ifaaResp = "";` 

- `try {` 

- `ifaaResp = await HttpUtils.request(this.url, result.msg);` 

- `} catch (err) {` 

- `Logger.error(TAG, err);` 

- `this.saveLog("` 网络错误: `" + err);` 

- `return;` 

- `}` 

- `Logger.info(TAG, "` 获取到响应: `" + ifaaResp);` 

- `let result1 = await status.checkLocalStatus(ifaaResp);` 

- `this.saveLog("checkLocalStatus` : `" + JSON.stringify(result1));` 

- `40` 

- `//` 当 `result.code` 为 `SUCCESS` 时,已经注册 

- `if (IfaaErrorCodeEnum.SUCCESS == result1.code) {` 

- `" "` 

- `this.saveLog(` 已经注册 `); 44 } else if (IfaaErrorCodeEnum.STATUS_NOT_REGISTERED == result1.code) { " "` 

- `this.saveLog(` 未注册 `);` 

9 

46   } else {
47 this.saveLog(" 异常: " + result1.toString());
48
  }
49
} else {
50
this.saveLog("status.checkStatusInit error: " + result.msg);
51
}

### **4.2.** IFAA注册 

SDK 对外提供 EtasRegister 类实现 IFAA 的注册流程,以下是主要的函数定义:

1 //  注册初始化
2 regInit(): EtasResult
3 //  执行注册操作
4 register(ifaaresp: string): Promise<EtasResult>
5 //  完成注册操作
6 regFinish(): EtasResult

10 

客户App eTAS_SDK App业务服务器 eTAS_BizServer
1 注册初始化
2 返回注册第一次请求报文
3 注册第一次请求(action为request/register)
4 注册第一次请求
透传报文
5 返回
6 返回
7 注册
8 用户指纹认证/人脸认证(可选)
9 注册第二次请求报文
1 0 注册第二次请求(action为response/register)
1 1 注册第二次请求
透传报文
校验设备合法性
保存用户公钥
1 2 返回
1 3 返回
1 4 注册完成
1 5 返回注册结果
客户App eTAS_SDK App业务服务器 eTAS_BizServer

1. 需要调用 regInit() 方法来进行注册初始化,获取注册需要发送到服务端的报文。 

   - a. 当 result.code 为 IfaaErrorCodeEnum.SUCCESS 时,result.msg 为发送到服务端的报文。 

   - b. 当 result.code 为其他 code 时,APP 根据错误码进行处理。 

- 一 

- 2. 调用 register() 方法来进行注册操作。传入参数为注册第 次请求服务端返回的报文。 

   - a. 当 result.code 为 IfaaErrorCodeEnum.SUCCESS 时,result.msg 为发送到服务端的报文。 

   - b. 当 result.code 为其他 code 时,APP 根据错误码进行处理。 

3. 调用 regFinish() 方法来完成注册操作。传入参数为注册第二次请求服务端返回的报文。 

   - a. 当 result.code 为 IfaaErrorCodeEnum.SUCCESS 时,注册成功。 

   - b. 当 result.code 为其他 code 时,APP 根据错误码进行处理。 

11 

示例代码: 

12 

TypeScript 

- `//` 导入 `2 import { 3 EtasRegister,` 

- `EtasResult,` 

- `IfaaErrorCodeEnum,` 

- `IfaaBaseInfo,` 

- `} from 'etaslibrary';` 

- `8` 

- `//` 初始化 `IfaaBaseInfo` 

- `@State ifaabaseinfo: IfaaBaseInfo = new IfaaBaseInfo();` 

- `// todo` , `IfaaBaseInfo` 的初始化 

- `12` 

- `//` 初始化 `EtasRegister` 

- `let ifaaRegister = new EtasRegister(this.ifaabaseinfo);` 

- `15` 

- `//` 调用注册初始化接口 

- `let result: EtasResult = ifaaRegister.regInit();` 

- `18` 

- `//` 当 `result.code` 异常时,流程中断 

- `if (IfaaErrorCodeEnum.SUCCESS != result.code) {` 

- `this.saveLog("ifaaRegister.regInit error: " + result.msg);` 

- `return;` 

- `}` 

- `24` 

- `//` 当 `result.code` 为 `IfaaErrorCodeEnum.SUCCESS` 时,发送请求到服务端 

- `Logger.info(TAG, "regInit: " + result.msg);` 

- `27` 

- `let ifaaResp = "";` 

- `try {` 

- `ifaaResp = await HttpUtils.request(this.url, result.msg);` 

- `} catch (err) {` 

- `Logger.error(TAG, err);` 

- `this.saveLog("` 网络错误: `" + err);` 

- `return;` 

- `}` 

- `Logger.debug(TAG,"ifaa request` 结果: `" + JSON.stringify(ifaaResp));` 

- `37` 

- `//` 调用注册接口,传入服务端返回报文 

- `let ifaaResult = await ifaaRegister.register(ifaaResp);` 

- `Logger.debug(TAG,"ifaa register` 结果: `" + JSON.stringify(ifaaResult));` 

- `41` 

- `//` 当 `ifaaResult.code` 异常时,流程中断 

- `if (IfaaErrorCodeEnum.SUCCESS != ifaaResult.code) { 44 this.saveLog("ifaaRegister.register error: " + ifaaResult.msg); 45 return;` 

13 

```
}
```

- `// let` 当 `ifaaResp1 ifaaResult.code = "";` 为 `IfaaErrorCodeEnum.SUCCESS` 时,发送请求到服务端 `50 try {` 

- `ifaaResp1 = await HttpUtils.request(this.url, ifaaResult.msg);` 

- `52` 

- `} catch (err) {` 

- `this.saveLog("` 网络错误 `1` : `" + err); 54 return;` 

- `}` 

- `56` 

- `//` 调用注册完成接口,传入服务端返回报文 

- `let ifaaResult2 = ifaaRegister.regFinish(ifaaResp1);` 

- `this.saveLog("ifaa respose` 结果: `" + JSON.stringify(ifaaResult2));` 

- `60` 

- `//` 当 `ifaaResult2.code` 为 `IfaaErrorCodeEnum.SUCCESS` 时,注册成功 

- `if (IfaaErrorCodeEnum.SUCCESS == ifaaResult2.code) {` 

- `63` 

   - `" "` 

   - `this.saveLog(` 注册成功 `);` 

- `64` 

   - `} else {` 

- `65` 

- `" "` 

- `this.saveLog(` 注册失败 `);` 

- `}` 

### **4.3.** IFAA认证 

#### SDK 对外提供 EtasAuthentication 类实现 IFAA 的认证流程,以下是主要的函数定义: 

- `//` 认证初始化 

- `authInit(): EtasResult` 

- `//` 执行认证操作 

- `auth(ifaaresp: string): Promise<EtasResult>` 

- `//` 完成认证操作 `6 authFinish(): EtasResult` 

客户App eTAS_SDK App业务服务器 eTAS_BizServer
1 认证初始化
2 返回认证第一次请求报文
3 认证第一次请求(action为request/auth)
4 认证第一次请求
透传报文
5 返回
6 返回
7 认证
8 用户指纹认证/人脸认证
9 认证第二次请求报文
1 0 认证第二次请求(action为response/auth)
1 1 认证第二次请求
透传报文
用户公钥验证认证结果
1 2 返回
1 3 返回
1 4 认证完成
1 5 返回认证结果
客户App eTAS_SDK App业务服务器 eTAS_BizServer

1. 调用 authInit() 方法来进行认证初始化,获取认证需要发送到服务端的报文。 

   - a. 当 result.code 为 IfaaErrorCodeEnum.SUCCESS 时,result.msg 为发送到服务端的报文。 

   - b. 当 result.code 为其他 code 时,APP 根据错误码进行处理。 

- 一 

- 2. 调用 auth() 方法来进行认证操作。传入参数为认证第 次请求服务端返回的报文。 

   - a. 当 result.code 为 IfaaErrorCodeEnum.SUCCESS 时,result.msg 为发送到服务端的报文。 

   - b. 当 result.code 为其他 code 时,APP 根据错误码进行处理。 

3. 调用 authFinish() 方法来完成认证操作。传入参数为认证第二次请求服务端返回的报文。 

   - a. 当 result.code 为 IfaaErrorCodeEnum.SUCCESS 时,认证成功。 

   - b. 当 result.code 为 IfaaErrorCodeEnum.WRONG_AUTHDATAINDEX 时,APP侧进行有效身 份认证后,调用指纹更新流程。 

   - c. 当 result.code 为其他 code 时,APP 根据错误码进行处理。 

#### 示例代码: 

TypeScript 

- `//` 导入 

- `import {` 

- `EtasAuthentication,` 

- `EtasResult,` 

- `IfaaErrorCodeEnum,` 

- `IfaaBaseInfo,` 

- `} from 'etaslibrary';` 

- `8` 

- `//` 初始化 `IfaaBaseInfo` 

- `@State ifaabaseinfo: IfaaBaseInfo = new IfaaBaseInfo(); 11 // todo` , `IfaaBaseInfo` 的初始化 

- `12` 

- `//` 初始化 `EtasAuthentication` 

- `let ifaaAuth = new EtasAuthentication(this.ifaabaseinfo);` 

- `15` 

- `//` 调用认证初始化接口 

- `let result: EtasResult = ifaaAuth.authInit();` 

- `18` 

- `//` 当 `result.code` 异常时,流程中断 

- `if (IfaaErrorCodeEnum.SUCCESS != result.code) {` 

- `this.saveLog("ifaaAuth.authInit error: " + result.msg);` 

- `return;` 

- `}` 

- `24` 

- `//` 当 `result.code` 为 `IfaaErrorCodeEnum.SUCCESS` 时,发送请求到服务端 

- `Logger.info(TAG, "authInit: " + result.msg);` 

- `27` 

- `let ifaaResp = "";` 

- `try {` 

- `ifaaResp = await HttpUtils.request(this.url, result.msg);` 

- `} catch (err) {` 

- `Logger.error(TAG, err);` 

- `this.saveLog("` 网络错误: `" + err);` 

- `return;` 

- `}` 

- `Logger.debug(TAG,"ifaa request` 结果: `" + JSON.stringify(ifaaResp));` 

- `37` 

- `//` 调用认证接口,传入服务端返回报文 

- `let ifaaResult = await ifaaAuth.auth(ifaaResp); 40 Logger.debug(TAG,"ifaa register` 结果: `" + JSON.stringify(ifaaResult));` 

- `41` 

- `//` 当 `ifaaResult.code` 异常时,流程中断 

- `if (IfaaErrorCodeEnum.SUCCESS != ifaaResult.code) { 44 this.saveLog("ifaaAuth.auth error: " + result.msg); 45 return;` 

```
46}
47
```

- `// let` 当 `ifaaResp1 ifaaResult.code = "";` 为 `IfaaErrorCodeEnum.SUCCESS` 时,发送请求到服务端 `50 try {` 

- `ifaaResp1 = await HttpUtils.request(this.url, ifaaResult.msg);` 

- `} catch (err) {` 

- `this.saveLog("` 网络错误 `1` : `" + err); 54 return;` 

- `}` 

- `56` 

- `//` 调用认证完成接口,传入服务端返回报文 `let ifaaResult2 = ifaaAuth.authFinish(ifaaResp1);` 

- `//` 当 `ifaaResult2.code` 为 `IfaaErrorCodeEnum.SUCCESS` 时,认证成功 `if (IfaaErrorCodeEnum.SUCCESS == ifaaResult.code) {` 

- `" " this.saveLog(` 认证成功 `);` 

- `} else {` 

- `" " this.saveLog(` 认证失败 `);` 

- `}` 

- `//` 如 `code` 为 `WRONG_AUTHDATAINDEX` 时,触发指纹更新,调用指纹更新流程 

- `if (IfaaErrorCodeEnum.WRONG_AUTHDATAINDEX == ifaaResult2.code) {` 

- `let updater = new EtasTemplateUpdater(this.ifaabaseinfo);` 

- `//` 调用指纹更新初始化接口 

- `let result: EtasResult = updater.templateUpdaInit(ifaaResult2.msg);` 

- `Logger.info(TAG, "` 指位更新报文: `" + result.msg); 72 73 try {` 

- `ifaaResp = await HttpUtils.request(this.url, result.msg);` 

- `} catch (err) {` 

- `this.saveLog("` 网络错误: `" + err); 77 return;` 

- `}` 

- `//` 指纹更新 

- `let result2 = updater.templateUpdaFinish(ifaaResp);` 

- `this.saveLog("` 更新指位结果: `" + JSON.stringify(result2)); 82 }` 

### **4.4.** IFAA指纹更新 

当IFAA认证流程中 authFinish 返回的 code 为 WRONG_AUTHDATAINDEX 时,触发指纹更新,调用 指纹更新流程。 

SDK 对外提供 EtasTemplateUpdater 类实现 IFAA 的指纹更新流程,以下是主要的函数定义: 

18 

ArkTS

- `//` 指纹更新初始化 `2 templateUpdaInit(ifaaMessage: string):EtasResult 3 //` 执行指纹更新操作 `4 templateUpdaFinish(ifaaResp: string):EtasResult` 

客户App eTAS_SDK App业务服务器 eTAS_BizServer
1 authFinish返回的msg
2 指纹更新初始化
3 返回指纹更新请求报文
4 指纹更新请求(action为request/addtemplateid)
5 指纹更新请求
透传报文
6 返回
7 返回
8 指纹更新
9 移动端指纹更新
1 0 指纹更新结果
客户App eTAS_SDK App业务服务器 eTAS_BizServer

1. 调用 templateUpdaInit() 方法来进行指纹更新初始化,传入认证流程 authFinish 返回的 msg。获 取指纹更新需要发送到服务端的报文。 

   - a. 当 result.code 为 IfaaErrorCodeEnum.SUCCESS 时,result.msg 为发送到服务端的报文。 

   - b. 当 result.code 为其他 code 时,APP 根据错误码进行处理。 

2. 调用 templateUpdaFinish() 方法来进行认证操作。传入参数为指纹更新请求服务端返回的报文。 

   - a. 当 result.code 为 IfaaErrorCodeEnum.SUCCESS 时,指纹更新成功。 

   - b. 当 result.code 为其他 code 时,APP 根据错误码进行处理。 

### **4.5.** IFAA注销 

SDK 对外提供 EtasDeregister 类实现 IFAA 的注销流程,以下是主要的函数定义: 

19 

- `//` 注销初始化 `2 deregInit():EtasResult` 

- `//` 执行注销操作 `4 dereg(ifaaDeRegResponse: string) :Promise<EtasResult>` 

客户App eTAS_SDK App业务服务器 eTAS_BizServer
1 注销初始化
2 返回注销请求报文
3 注销请求(action为request/unregister)
4 注销请求
透传报文
5 返回
6 返回
7 注销
8 移动端本地注销
9 注销结果
客户App eTAS_SDK App业务服务器 eTAS_BizServer

1. 调用 deregInit() 方法来进行注销初始化,获取注销需要发送到服务端的报文。 

   - a. 当 result.code 为 IfaaErrorCodeEnum.SUCCESS 时,result.msg 为发送到服务端的报文。 

   - b. 当 result.code 为其他 code 时,APP 根据错误码进行处理。 

- 一 

- 2. 调用 dereg() 方法来进行注销操作。传入参数为认证第 次请求服务端返回的报文。 

   - a. 当 result.code 为 IfaaErrorCodeEnum.SUCCESS 时,注销成功。 

   - b. 当 result.code 为其他 code 时,注销失败。 

示例代码: 

20 

ArkTS 

- `//` 导入 `2 import { 3 EtasDeregister,` 

- `EtasResult,` 

- `IfaaErrorCodeEnum,` 

- `IfaaBaseInfo,` 

- `} from 'etaslibrary';` 

- `8` 

- `//` 初始化 `IfaaBaseInfo` 

- `@State ifaabaseinfo: IfaaBaseInfo = new IfaaBaseInfo();` 

- `// todo` , `IfaaBaseInfo` 的初始化 

- `12` 

- `//` 初始化 `ifaaDeregister` 

- `let ifaaDeregister = new EtasDeregister(this.ifaabaseinfo);` 

- `//` 调用注销初始化接口 `17 let result: EtasResult = ifaaDeregister.deregInit();` 

- `18` 

- `//` 当 `result.code` 异常时,流程中断 

- `if (IfaaErrorCodeEnum.SUCCESS != result.code) {` 

- `this.saveLog("ifaaDeregister.deregInit error: " + result.msg); 22 return;` 

- `}` 

- `24` 

- `//` 当 `result.code` 为 `IfaaErrorCodeEnum.SUCCESS` 时,发送请求到服务端 

- `Logger.info(TAG, "deregInit: " + result.msg);` 

- `27` 

- `let ifaaResp = "";` 

- `try {` 

- `ifaaResp = await HttpUtils.request(this.url, result.msg);` 

- `} catch (err) {` 

- `Logger.error(TAG, err);` 

- `this.saveLog("` 网络错误: `" + err);` 

- `return;` 

- `35` 

   - `}` 

- `Logger.debug(TAG,"ifaa request` 结果: `" + JSON.stringify(ifaaResp));` 

- `//` 调用注销接口,传入服务端返回报文 

- `let ifaaResult = await ifaaDeregister.dereg(ifaaResp);` 

- `Logger.debug(TAG,"ifaaDeregister dereg` 结果: `" + JSON.stringify(ifaaResul t));` 

- `41` 

- `// ifaaResult.code` 为 `IfaaErrorCodeEnum.SUCCESS` 时,注册成功 

- `if (IfaaErrorCodeEnum.SUCCESS == ifaaResult.code) { 44 this.saveLog("` 注销成功 `");` 

21 

`45 } else { 46 this.saveLog("` 注销失败 `"); 47 }` 

## **5.** 错误码 

### **5.1.** IfaaErrorCodeEnum 的枚举值 

EtasResult 实体类中的 code 的枚举 

|枚举值|值|业务意义|
|---|---|---|
|SUCCESS|0|成功|
|STATUS_NOT_SUPPORT|1|终端不支持IFAA|
|STATUS_NOT_ENROLLED|4|终端没有录入指纹/人脸(此时可以引导用户去录 入指纹/人脸再做操作)|
|STATUS_NOT_REGISTERED|5|IFAA尚未注册(比如认证/注销/指位更新等操作 都需要注册后才可以进行)|
|STATUS_REGISTERED|6|IFAA已经注册(checkStatusInit中返回,表示已 经是注册状态,无需发送请求到服务端查询)|
|CLIENT_ERROR|8|SDK本地执行异常|
|SERVER_ERROR|9|服务器错误|
|WRONG_AUTHDATAINDEX|11|指纹不匹配,需要更新指纹(authFinish中返回 时,进行更新指纹流程)|
|POLICY_REJECTED|12|被风险策略拒绝时(IFAA服务端返回)|
|USER_REJECTED|13|用户被禁用时(IFAA服务端返回)|
|APPID_NOT_FOUNDAPPID_NO T_FOUND|14|应用标识白名单中未设置,需要在IFAA服务端添 加该应用标识(IFAA服务端返回)|
|DEVICE_MODEL_NOT_FOUND|15|设备型号不存在(IFAA服务端返回)|
|ERR_SIGNATURE_FAIL|16|未获取到签名数据(IFAA服务端返回)|

22 

|STATUS_RESULT_CANCELED|19|用户取消,APP侧可切换其他认证方式。|
|---|---|---|
|STATUS_RESULT_TIMEOUT|20|认证流程开始时,长时间未进行生物认证,认证 超时,APP侧可切换其他认证方式。|
|STATUS_RESULT_AUTH_FAIL|21|验证失败,生物认证不匹配,APP侧可切换其他 认证方式。|
|STATUS_RESULT_SYSTEM_BL OCK|22|连续多次校验失败,指纹校验被暂时锁定,APP 侧可切换其他认证方式。|
|STATUS_RESULT_FALLBACK|23|点击了生物认证页面的FALLBACK按钮,APP 侧可切换其他认证方式。|
|STATUS_RESULT_TEE_ERROR|24|TEE错误,APP侧可提示系统异常|
|PERMISSION_DENIED|26|Android:当前设备未获取相机权限 IOS:当前应用未获取Face ID权限 ● ●|
|AUTHENTICATOR_DISABLE|27|认证器被禁用(IFAA服务端返回)|
|AUTHENTICATOR_NOT_FOUN D|28|未找到相应的认证器(IFAA服务端返回)|
|DEVICE_KEY_NOT_FOUND|29|设备密钥被禁用(IFAA服务端返回)|

## **6.** SDK下载地址 

XML 

- `http://esand-file-sharing.oss-cn-beijing.aliyuncs.com/ifaa/etas-sdk/etasSdk Demo-HarmonyOS_1.1.1_release_1fe535.zip?OSSAccessKeyId=LTAI5tMByCwCzwpPSLLY scgr&Expires=3601734315006&Signature=6BD5fkirPlpJCRwd0lN74i1ewOI%3D` 

## **7.** 常见问题 

### **7.1.** 注册流程报The service is abnormal错误 

23 

#### 原因1 

服务端application.yml中配置可能有问题,需要确认下ios和安卓是否能够正常注册。 原因2 

鸿蒙系统需要请求华为服务器(非sdk需要)获取到匿名化证书。 

解决方案: 

需要在行内网络环境下,配置白名单,服务信息如下: 

域名:dacms-drcn.security.dbankcloud.cn 

- 124.70.116.200 

- 49.4.35.130 

验证方法: 

在行内网络环境下执行命令查看证书: 

- curl --insecure -v https://dacms-drcn.security.dbankcloud.cn 

正常返回: 

24 

### **7.2.** 拉起系统设置指纹界面方法 

ArkTS

`1 Button('` 跳转设置指纹页面 `') 2 .onClick(() => { 3 let context = getContext() as common.UIAbilityContext; 4 let want: Want = { 5 bundleName: 'com.huawei.hmos.settings', 6 abilityName: 'com.huawei.hmos.settings.MainAbility', 7 uri: 'biometrics_and_password_settings' 8 }; 9 10 context.startAbility(want) 11 .then(() => { 12 // ... 13 }) 14 .catch((err: BusinessError) => { 15 console.error(`Failed to startAbility. Code: ${err.code}, messag e: ${err.message}`); 16 }); 17 })` 

25
