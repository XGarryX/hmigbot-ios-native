# **壹证通HarmonyOS国密SDK集成说明文档** 

##### 南京壹证通信息科技有限公司 

##### **修订历史** 

|**时间**|**版本**|**描述**|**作者**|
|---|---|---|---|
|2024/10/29|1.0.2|1.修复单证场景导入失败bug 2.新增更新协签、中台地址 updateServer|Zhanghe|

##### **目录** 

1 引言 1.1 概述 1.2 开发平台及开发语言 1.3 构架 1.4 运行环境 1.5 主要功能 2 SDK集成 2.1 SDK内容说明 2.2 导入SDK 2.3 授权文件 3. API 接入说明 3.1 SDK 调用流程说明 3.2 配置与初始化 3.2.0日志打印开关 3.2.1 初始化SDK服务 3.2.2 配置必要参数 3.2.3 绑定/解绑账户 3.2.3.1 绑定账户 3.2.3.2 解绑当前账户 3.2.4 检查账户是否已绑定 3.3 检测本地设备中数字证书的状态 3.3.1 有网络交互的证书状态检测 3.3.2 无网络交互的证书状态检测 3.4 证书的签发 3.5 数字证书查询 3.5.1 查询当前绑定账户的本地证书 3.5.2 根据交易账号查询该账号下申请的所有证书 3.5.3 通过交易账号检测该账号在本地是否存在证书 3.6 证书PIN码校验 3.7 证书PIN码修改 3.8 延期 3.9 注销 3.9.1 注销本地数字证书 3.9.2 注销其他设备的数字证书 3.9.3 枚举出SDK绑定的所有账户 3.9.4 删除SDK绑定的账户 3.9.5 删除本地证书 3.10 证书重置 3.11 国密SSL 3.11.0 注册gmssl 3.11.1 配置证书链,以及配置是否开启证书链验证和主机验证 3.11.3 基于TCP协议的国密SSL 3.11.4 基于HTTP协议的国密SSL 3.12 PKI基础功能 3.12.1 生成SM4密钥 3.12.2 SM2加密 

3.12.3 SM4 对称加密与解密 3.12.4 SM3 摘要计算 3.12.5 HMAC-SM3 3.13 SDK错误日志上报 

4 注意事项说明 5 版权说明 

## **1 引言** 

### **1.1 概述** 

本文档主要介绍了国密 SDK 的集成要求、接口调用方式,以及在集成过程中需要注意的地方;本文 仅适用于业务方集成国密SDK 的 Android 客户端开发人员在集成过程中参考使用。 

国密 SDK 是基于智能移动终端的安全服务软件,致力于为 第三方应用开发者提供可靠便捷的PKI服 务和基于GMSSL协议的网络安全通信。该产品包含了基于国密算法的数字签名与验签,非对称加密(公 钥加密/私钥解密),数字信封封包与解包,国密双向SSL等常用安全功能,支持SM2/SM3/SM4等国产 密码算法,为第三方应用提供有效且全面的安全功能支持。 

国密 SDK 的设计严格遵照国密算法的规范和要求,如《GM/T 0003-2012 SM2 椭圆曲线公钥密码算 法》、《GM/T 0004-2012 SM3密码杂凑算法》等,提供安全有效的PKI服务。 

国密 SDK 的集成和使用请仔细阅读本手册,对需要特别注意的地方,文档中将特别加以提醒。 

### **1.2 开发平台及开发语言** 

开发平台: **DevEco Studio** 开发语言: **C/C++ , ArkTS, TS** 

### **1.3 构架** 

支持 CPU架构平台:arm64-v8a 

### **1.4 运行环境** 

国密SDK 的HarmonyOS目前最低支持版本为  API 12。 

### **1.5 主要功能** 

##### **SDK主要功能提供有:** 

- 数字证书的签发 

- 本地设备证书状态检测 

- 本地数字证书查询 

- 根据交易账号查询该交易账号申请的所有证书 

- 证书的PIN码校验 

- 修改证书的PIN码 

- 证书延期 

- 证书注销 

- 证书重置 

- PKI基础功能 

- 国密SSL 

## **2 SDK集成** 

### **2.1 SDK内容说明** 

国密SDK 提供给第三方开发者使用的库文件 unitid_harmony_gm_sdk_xxx.har中包含pki基础业务 库和底层动态链接库 

### **2.2 导入SDK** 

在工程中需要引入SDK包的模块的oh-package.json5中添加如下配置 

"dependencies": { "gm_sdk_library": "file:har存放路径" // 如:"file:libs/unitid_harmony_gm_sdk.har" } 

##### 依赖完成后需要执行 

ohpm install 

### **2.3 授权文件** 

国密sdk需要license授权文件才能正常使用。每个应用对应一个license。license的获取需要提供项 目应用包名,由壹证通配置并生成合法可用的license授权文件。license授权文件命名为 unitid_harmonyos_gm.license 且不能随意更改命名,否则无法正常使用sdk。license授权文件存放 在rawfile目录下。 

## **3. API 接入说明** 

### **3.1 SDK 调用流程说明** 

##### **流程图说明** 

- 首先是配置SDK 

- 1)配置协同服务,包含 地址 、 appId 、 appSecret 

- 2)配置密码中台服务,包含 地址 、 appKey 、 appSecret 

- 初始化SDK,初始化SDK的目的是为了校验SDK的授权。 

- SDK初始化完成后,需要绑定账户 

- 可以进行证书的签发 

- 证书签发下来后,可以进行国密SSL的双向通信。在建立国密SSL双向通信之前需要注册GMSSL服 务,且注册成功才可进行国密双向ssl的通信。如果是单向的国密ssl则不需要注册GMSSL服务 

### **3.2 配置与初始化** 

#### **3.2.0日志打印开关** 

导包: import {GmManager} from 'gm_sdk_library'; 

/** 

- 日志打印开关设置 

- @param open true:开启,false:关闭。默认开启 

*/ GmManager.getInstance().setLog(open: boolean)=>Void 

#### **3.2.1 初始化SDK服务** 

SDK的初始化,需要在每次启动应用的时候进行。 

GmManager.getInstance().initService(getContext()) .then((initResult) => { if (initResult.success) { // 初始化成功 }else{ // 初始化失败 initResult.message//错误信息描述 } }) .catch((error: Error) => { // 异常捕获 }); 

##### **注:** 初始化操作只需要调用一次 

#### **3.2.2 配置必要参数** 

国密的所有配置包含两个部分,一个协同服务器的相关配置(包括ip地址,端口,appId和appSecret) 和 云服务器的相关配置(包括应用的key和秘钥secret,以及服务器地址)。相关配置可在demo中查 看 

##### **注:具体使用可参照demo** 

导包: import {GmManager} from 'gm_sdk_library'; 

##### **中台与协签配置** 

/** 

* 配置中台/协签相关信息 

* @param serverUrl 密码中台服务地址 

* @param appKey 中台appKey 

* @param appSecret 中台appSecret 

- @param cosignUrl 协签服务地址 

* @param appId 协签appId 

- @param cosignSecret 协签cosignSecret 

*/ 

GmManager.getInstance().configServer(serverUrl, appKey, appSecret, cosignUrl, appId, cosignSecret); 

##### **更新中台与协签配置** 

/** 

* 更新中台/协签相关信息 

* @param serverUrl 密码中台服务地址 

- @param cosignUrl 协签服务地址 

*/ GmManager.getInstance().updateServer(serverUrl, cosignUrl); 

##### **SDK内部通讯组件证书链验证、主机验证的开启与关闭** 

/** 

- 设置SDK内部服务验证方式 

- @param verifyChain 是否开启证书链验证 

- @param verifyPeerCertExpiryDate 是否验证对端证书有效期 

* @param verifyHostname 是否验证主机 */ GmManager.getInstance().setInnerTrustServer(verifyChain: boolean, verifyPeerCertExpiryDate: boolean, verifyHostname: boolean); 

**注** :SDK内部通讯组件证书验证与主机验证的设置,全局只需设置一次即可。SDK内部通讯默认开启证 书链验证,如果不需要验证,可通过上述配置关闭 

#### **3.2.3 绑定/解绑账户** 

导包: import {GmManager,BindResult} from 'gm_sdk_library'; 

##### **3.2.3.1 绑定账户** 

/** * 绑定账户 * @param accountId 账户 * @returns -{@link BindResult} */ GmManager.getInstance().bind(accountId: string)=>Promise<BindResult> 

BindResult.SUCCESS // 绑定成功 BindResult.SDK_NOT_INIT //SDK未初始化 BindResult.ACCOUNT_UPPER_LIMIT // 绑定账户已达上限 BindResult.FAILURE //绑定失败 

##### 示例: 

GmManager.getInstance().bind(this.account) .then((result) => { //todo }) .catch((error: Error) => { //todo }); 

**注** :务必完成账户的绑定操作,否则SDK将无法正常使用。同时SDK最多支持绑定100个账户,达到上 限后,不再支持新账户的绑定。如果要绑定新的账户,则需要删除原先已经绑定的账户。 

##### **3.2.3.2 解绑当前账户** 

##### 退出交易登录,或者切换交易账户的时候需要解除绑定重新绑定新的交易账户 

GmManager.getInstance().unBind()=>void 

#### **3.2.4 检查账户是否已绑定** 

导包: import {GmManager} from 'gm_sdk_library'; 

/** * 检测账户是否已绑定,检查的是当前绑定的账户 * @param accountId * @return */ GmManager.getInstance().isBound(String accountId)=>boolean 

##### 备注:调用前已完成SDK的初始化工作。 

### **3.3 检测本地设备中数字证书的状态** 

#### **3.3.1 有网络交互的证书状态检测** 

导包: import {GmManager,CertStatus,BisCode} from 'gm_sdk_library'; 

GmManager 

/** 

* 检测本地证书状态,与中台进行交互。状态是否可用,是否被注销,是否已过期 * @returns */ GmManager.getInstance().checkLocalCertStatus()=>Promise<CertStatus> 

##### 示例: 

GmManager.getInstance().checkLocalCertStatus() .then((certStatus) => { this.loadingController?.close(); switch (certStatus.status) { case BisCode.CERT_ISSUED: case BisCode.CERT_REVOKED: case BisCode.CERT_EXPIRED: this.toast(`${certStatus.message},剩余有效期: ${certStatus.expireInDays}`); break; default: console.error(`${certStatus.message}`); break; } }) .catch((error: Error) => { console.error(`${error.message}`); 

}); 

CertStatus 描述: 

CertStatus { /** * 已签发; * 已过期; * 已注销, * 证书私钥丢失,需要注销证书重新签发; * 密码中台服务异常; * 国密ssl链接建立失败; * 其他错误; * 本地无证书 */ status = 0; /** * 证书有效期,单位天数 * 证书有效期内该值为正,过期为负数 */ expireInDays = 0; /** * 描述信息 */ message = ''; /** * 证书 */ cert: Certificate | undefined; } 

BisCode 业务码集合 

BisCode { /** * 其他错误 */ FAILURE = -1, /** * 成功状态码 */ SUCCESS, /** * 操作被取消 */ OPERATION_CANCELED, 

/** * SDK未初始化 */ SDK_NOT_INITIALIZED, /** * 未绑定账户 */ ACCOUNT_NOT_BOUND, /** * 中台服务异常(包含中台关联的RA服务的异常); */ PASSWORD_SERVER_ERROR, /** * 用户申请的证书已达上限 */ CERT_UPPER_LIMIT, /** * 协签服务异常,包括协同网关无法建立链接一样 */ CO_SIGN_ERROR, /** * 本地证书已存在,不允许重复签发 */ CERT_EXIST_CAN_NOT_ISSUE, /** * 未经允许的操作,非法操作 */ INVALID_OPERATION, /** * 非法的PIN码 */ INVALID_PIN, /** * PIN码错误 */ PIN_ERROR, /** * PIN码已锁定 */ PIN_LOCKED, /** * 发证限流 */ ISSUE_CERT_LIMIT, 

/** * 交易认证失败 */ TRANSACTION_AUTH_FAILURE, /** * 证书不存在 */ CERT_NOT_FOUND, /** * 请求取消 */ REQUEST_CANCELED, /** * 协签服务端密钥丢失 */ COSIGN_SERVER_KEY_DIVISION_LOST, /** * 证书已签发 */ CERT_ISSUED, /** * 证书已过期 */ CERT_EXPIRED, /** * 证书已注销 */ CERT_REVOKED, } 

备注:证书为已签发状态下课解析得到证书的剩余有效期,单位(天)。其他状态下解析无效。 

#### **3.3.2 无网络交互的证书状态检测** 

无网络的证书状态检测,检测本地是否有证书,检测证书是否已过期 

导包: import {GmManager,CertStatus,BisCode} from 'gm_sdk_library'; 

GmManager 

/** 

- 检查本地证书是否已过期,该方法只能检测该证书是否已过期,无法检测证书是否被注销 

- @param timestamp 时间戳(毫秒),如果传递,则与该时间戳比较,若不传,则与当前系统时间比较 */ 

GmManager.getInstance().checkLocalCertExpiryDate(timestamp?: number)=>Promise<CertStatus> 

### **3.4 证书的签发** 

导包: import {GmManager,CertParam,BisCode} from 'gm_sdk_library'; 

类: GmManager 

/** * 证书签发 * @param certParam 证书参数 * @param pin PIN码 * @returns 返回 Promise<OptData> */ 

GmManager.getInstance().issueCert(certParam: CertParam, pin: string)=>Promise<OptData> 

CertParam 入参 

CertParam { /** * 交易账号 */ accountId = ''; /** * 交易密码 */ password = ''; /** * 交易扩展信息 */ extend = ''; /** * 媒体介质 */ medium = ''; /** * 组织 */ organization = ''; /** * 组织单位 */ organizationUnit = ''; } 

OptData 返回信息 

OptData { 

/** * 错误码 * {@link BisCode} */ code = -1; /** * 描述性信息 */ message = ''; /** * 交易认证失败响应信息,是个json串 */ transErrorRep = ''; /** * PIN码剩余可重试次数 * 当 code 未PIN码错误code或PIN码锁定时的code有效 */ pinTryNum = 0; /** * 证书 */ cert?: Certificate | undefined; /** * 操作成功/失败 */ isSuccessful() { return this._code == BisCode.SUCCESS; } /** * 账户列表 */ accounts = new ArrayList<string>(); } 

**示例** : 

```arkts
let certParam = new CertParam(); certParam.accountId = this.account; certParam.password = 'password'; certParam.extend = 'extend'; certParam.medium = `HUAWEI MATE60 PRO`; GmManager.getInstance().issueCert(certParam, pin) .then((optData) => { if (optData.isSuccessful()) { // 签发成功 } else { // TODO 解析具体错误 BisCode.FAILURE :其他错误; 
```

BisCode.SUCCESS :成功; BisCode.PASSWORD_SERVER_ERROR:中台服务异常(包含中台关联的RA服务的异常); BisCode.CERT_UPPER_LIMIT:当前账户申请的证书数量已达上限 BisCode.CO_SIGN_SERVER_ERROR:协同服务不可用;(包含协同网关链接建立失败) BisCode.CERT_EXIST:证书已存在,不可重复申请 BisCode.INVALID_OPERATION:未经允许的操作 BisCode.ISSUE_CERT_LIMIT:发证限流,暂时无法进行证书的签发 BisCode.TRANSACTION_AUTH_FAILURE = 10:交易认证失败 } }) .catch((error: Error) => { // todo 捕获错误 }); 

### **3.5 数字证书查询** 

#### **3.5.1 查询当前绑定账户的本地证书** 

导包: import {GmManager,OptData,BisCode} from 'gm_sdk_library'; 

GmManager 

/** 

- 获取签名证书(不存在多证的情况使用) 

* @param sign true:签名证书,false:加密证书;默认为true,签名证书 */ GmManager.getInstance().getCertificate(sign?: boolean)=>Promise<OptData> 

##### 示例: 

GmManager.getInstance().getCertificate() .then((optData) => { this.loadingController?.close(); if (optData.isSuccessful()) { 

```arkts
if (optData.cert) { let before = dateFormat(optData.cert.notBefore); let after = dateFormat(optData.cert.notAfter); let cert = new Cert(); cert.name = optData.cert.name; cert.serial = optData.cert.serialNumber; cert.expireDate = `${before}-${after}`; cert.subject = optData.cert.subject; cert.issuer = optData.cert.issuer; ... } } else { // todo } }) 
```

.catch((error: Error) => { // todo }); 

Certificate 实体类描述: 

Certificate { /** * 证书id */ id: string = ''; /** * 证书名称 */ name: string = ''; /** * 证书序列号,16进制字符串 */ serialNumber: string = ''; /** * 证书主题项 */ subject: string = ''; /** * 证书颁发者 */ issuer: string = ''; /** * 证书起始时间 */ notBefore: Date; /** * 证书截止时间 */ notAfter: Date; /** * 是否存在私钥 */ isPriKeyAccessible: boolean; /** * 证书二进制 */ encode: Uint8Array; /** * 证书二进制公钥 */ ppubKey: Uint8Array; } 

#### **3.5.2 根据交易账号查询该账号下申请的所有证书** 

**注意** :同一个账号在不同设备上申请的证书(证书状态为已签发状态)都会被查询出来。数据来源于密 码中台 

导包: import {GmManager,AccountCert,BisCode} from 'gm_sdk_library'; 

API类: GmManager 

/** * 查询该账户下申请的所有证书 * @param account 账户 */ GmManager.getInstance().queryCertsByAccount(account)=>Promise<AccountCert> 

##### AccountCert 实体信息描述 

AccountCert { /** * 错误码,-1:其他错误 */ code = 0; /** * 错误信息描述 */ message = ''; /** * 证书列表,json数组字符串 * [{"certSerial":"00A7858EBDE916D39238457B2F","notBefore":"2024-0422","notAfter":"2024-05-22","medium":"M2102J2SC"}, {"certSerial":"00AE982AE4E13C4328DB3EB510","notBefore":"2024-0329","notAfter":"2026-01-28","medium":"M2102J2SC"}, {"certSerial":"00FEFC6CFB5A349FCC429DF1C1","notBefore":"2023-1021","notAfter":"2024-05-17","medium":"M2011K2C"}, {"certSerial":"781760BDA75BC849CE5FE937343CF035F3FCA0BA","notBefore":"2024-0424","notAfter":"2024-08-24","medium":"M2102J2SC"}] */ certs = new ArrayList<NetCert>(); } 

##### **示例** : 

GmManager.getInstance().queryCertsByAccount(account) .then((data) => { if (BisCode.SUCCESS == data.code) { data.certs } else { BisCode.SUCCESS:成功, BisCode.PASSWORD_SERVER_ERROR:密码中台服务异常; 

BisCode.FAILURE:其他错误 hilog.error(0x101,'AccountCertPage',data.message); } }) .catch((error: Error) => { // todo }); 

#### **3.5.3 通过交易账号检测该账号在本地是否存在证书** 

##### 该接口支持检测非当前绑定的交易账号在本地是否存在证书 

导包: import {GmManager,OptData,BisCode} from 'gm_sdk_library'; 

类: GmManager 

##### 对应API如下: 

/** * 查询该账户下在本地是否存在证书 * @param account 账户 * @returns */ GmManager.getInstance().checkCertExistByAccount(account: string)=>Promise<OptData> 

##### 示例: 

GmManager.getInstance().checkCertExistByAccount(this.account) .then((optData)=>{ if (optData.code == BisCode.SUCCESS) { // 存在 }else if (BisCode.CERT_NOT_FOUND){ // 不存在 }else{ // 查询失败 } }) .catch((error:Error)=>{}) 

### **3.6 证书PIN码校验** 

导包: import {GmManager,OptData,BisCode} from 'gm_sdk_library'; 

GmManager 

对应API如下: 

/** * 验证PIN码 * @param pin */ GmManager.getInstance().verifyPin(pin)=>Promise<OptData> 

##### 示例: 

GmManager.getInstance().verifyPin(pin) .then((optData) => { optData.code; BisCode.SDK_NOT_INITIALIZED: SDK未初始化 BisCode.ACCOUNT_NOT_BOUND: 未绑定账户 BisCode.SUCCESS: 成功 BisCode.PIN_ERROR: PIN码错误 BisCode.PIN_LOCKED: PIN码锁定 BisCode.CO_SIGN_ERROR: 协签错误 BisCode.CERT_NOT_FOUND: 本地无证书 BisCode.FAILURE: 其他错误 }) .catch((error: Error) => { // todo }) 

##### 错误码信息描述: 

BisCode.SDK_NOT_INITIALIZED: SDK未初始化 BisCode.ACCOUNT_NOT_BOUND: 未绑定账户 BisCode.SUCCESS: 成功 BisCode.PIN_ERROR: PIN码错误 BisCode.PIN_LOCKED: PIN码锁定 BisCode.CO_SIGN_ERROR: 协签错误 BisCode.CERT_NOT_FOUND: 本地无证书 BisCode.FAILURE: 其他错误 

### **3.7 证书PIN码修改** 

导包: import {GmManager,OptData,BisCode} from 'gm_sdk_library'; 

GmManager 

##### 对应API如下: 

/** * 修改PIN码 * @param oldPin 原PIN码 * @param newPin 新PIN码 */ GmManager.getInstance().modifyPIN(oldPin: string, newPin: string)=>Promise<OptData> 

示例: 

GmManager.getInstance().modifyPIN(oldPin, newPin) .then((optData) => { optData.code; BisCode.SDK_NOT_INITIALIZED: SDK未初始化 BisCode.ACCOUNT_NOT_BOUND: 未绑定账户 BisCode.SUCCESS: 成功 BisCode.PIN_ERROR: PIN码错误 BisCode.PIN_LOCKED: PIN码锁定 BisCode.CO_SIGN_ERROR: 协签错误 BisCode.CERT_NOT_FOUND: 本地无证书 BisCode.FAILURE: 其他错误 }) .catch((error: Error) => { // todo }) 

##### 错误码信息描述 

BisCode.SDK_NOT_INITIALIZED: SDK未初始化 BisCode.ACCOUNT_NOT_BOUND: 未绑定账户 BisCode.SUCCESS: 成功 BisCode.PIN_ERROR: PIN码错误 BisCode.PIN_LOCKED: PIN码锁定 BisCode.CO_SIGN_ERROR: 协签错误 BisCode.CERT_NOT_FOUND: 本地无证书 BisCode.FAILURE: 其他错误 

### **3.8 延期** 

导包: import {GmManager,OptData,BisCode} from 'gm_sdk_library'; 

GmManager 

##### API接口 

/** 

* 证书延期,多证的情况,延期时需要传入证书序列号,指明需要延期的证书。国密改造每个账户只能有一 张或一对证书 * @param pin */ GmManager.getInstance().extendCert(pin: string)=>Promise<OptData> 

##### 示例: 

GmManager.getInstance().extendCert(pin) .then((optData) => { if (optData.isSuccessful()) { // todo success 

} else { // todo failure optData.code: ' BisCode.SDK_NOT_INITIALIZED, 'SDK未初始化 ' ' BisCode.ACCOUNT_NOT_BOUND, 未绑定账户 ' ' BisCode.INVALID_PIN, 非法PIN码 ' BisCode.PIN_ERROR, 'PIN码错误 BisCode.PIN_ERROR: 'PIN码错误' BisCode.PIN_LOCKED: 'PIN码锁定' BisCode.CO_SIGN_ERROR: '协签错误' BisCode.CERT_NOT_FOUND: '本地无证书' BisCode.COSIGN_SERVER_KEY_DIVISION_LOST: '协签密钥丢失' ' ' BisCode.PASSWORD_SERVER_ERROR, 服务响应信息异常 ' ' BisCode.FAILURE 其他错误 } }) .catch((error: Error) => { this.loadingController?.close(); ` this.toast( 证书延期失败,${error.message}`); }); 

##### 错误码信息描述 

' BisCode.SDK_NOT_INITIALIZED, 'SDK未初始化 ' ' BisCode.ACCOUNT_NOT_BOUND, 未绑定账户 ' ' BisCode.INVALID_PIN, 非法PIN码 ' BisCode.PIN_ERROR, 'PIN码错误 BisCode.PIN_ERROR: 'PIN码错误' BisCode.PIN_LOCKED: 'PIN码锁定' BisCode.CO_SIGN_ERROR: '协签错误' BisCode.CERT_NOT_FOUND: '本地无证书' BisCode.COSIGN_SERVER_KEY_DIVISION_LOST: '协签密钥丢失' ' ' BisCode.PASSWORD_SERVER_ERROR, 服务响应信息异常 ' ' BisCode.FAILURE 其他错误 

### **3.9 注销** 

#### **3.9.1 注销本地数字证书** 

GmManager 

导包: import {GmManager,OptData,BisCode} from 'gm_sdk_library'; 

API接口 

/** 

* 注销本地证书 

* @param account 账户 

* @param password 密码 * @param extend 扩展信息 */ GmManager.getInstance().revokeLocalCert(account: string, password: string, extend: string)=>Promise<OptData> 

##### 示例: 

GmManager.getInstance().revokeLocalCert(account, password, extend) .then((optData) => { this.loadingController?.close(); if (optData.isSuccessful()) { // 成功 } else { // 失败 ' BisCode.SDK_NOT_INITIALIZED, 'SDK未初始化 ' ' BisCode.ACCOUNT_NOT_BOUND, 未绑定账户 ' ' BisCode.FAILURE 其他错误 ; BisCode.PASSWORD_SERVER_ERROR:'中台服务异常(包含中台关联的RA服务的异常)'; BisCode.TRANSACTION_AUTH_FAILURE:'认证失败'; ' ' BisCode.CERT_NOT_FOUND: 证书不存在 } }) .catch((error: Error) => { // todo }) 

##### 错误码描述: 

' BisCode.SDK_NOT_INITIALIZED, 'SDK未初始化 ' ' BisCode.ACCOUNT_NOT_BOUND, 未绑定账户 ' ' BisCode.FAILURE 其他错误 ; BisCode.PASSWORD_SERVER_ERROR:'中台服务异常(包含中台关联的RA服务的异常)'; BisCode.TRANSACTION_AUTH_FAILURE:'认证失败'; ' ' BisCode.CERT_NOT_FOUND: 证书不存在 

#### **3.9.2 注销其他设备的数字证书** 

导包: import {GmManager,OptData,BisCode} from 'gm_sdk_library'; 

GmManager 

API接口 

/** 

* 注销其他设备证书 

* @param account 账号 

* @param password 密码 

* @param extend 扩展信息 * @param serialNum 证书序列号 */ 

GmManager.getInstance().revokeOtherDeviceCert(account: string, password: string, extend: string, serialNum: string)=>Promise<OptData> 

##### 示例: 

GmManager.getInstance().revokeOtherDeviceCert(account, password, extend, item.certSerial) .then((optData) => { if (optData.isSuccessful()) { // 成功 } else { // 失败 ' BisCode.SDK_NOT_INITIALIZED, 'SDK未初始化 ' ' BisCode.ACCOUNT_NOT_BOUND, 未绑定账户 ' ' BisCode.FAILURE 其他错误 ; BisCode.PASSWORD_SERVER_ERROR:'中台服务异常(包含中台关联的RA服务的异常)'; BisCode.TRANSACTION_AUTH_FAILURE:'认证失败'; ' ' BisCode.CERT_NOT_FOUND: 证书不存在 } }) .catch((error: Error) => { // todo }) 

##### 错误码描述: 

' BisCode.SDK_NOT_INITIALIZED, 'SDK未初始化 ' ' BisCode.ACCOUNT_NOT_BOUND, 未绑定账户 ' ' BisCode.FAILURE 其他错误 ; BisCode.PASSWORD_SERVER_ERROR:'中台服务异常(包含中台关联的RA服务的异常)'; BisCode.TRANSACTION_AUTH_FAILURE:'认证失败'; 

#### **3.9.3 枚举出SDK绑定的所有账户** 

导包: import {GmManager,OptData,BisCode} from 'gm_sdk_library'; 

GmManager 

API接口 

/** * 枚举账户 */ GmManager.getInstance().enumAccounts()=>Promise<OptData> 

##### 示例: 

GmManager.getInstance().enumAccounts() .then((data) => { if (data.isSuccessful()) { data.accounts } else { // 枚举失败 ' BisCode.SDK_NOT_INITIALIZED, 'SDK未初始化 ' ' BisCode.FAILURE, 失败 data.message } }) .catch((error: Error) => { // todo }); 

#### **3.9.4 删除SDK绑定的账户** 

导包: import {GmManager,OptData,BisCode} from 'gm_sdk_library'; 

GmManager 

##### API接口 

/** * 删除账户 * @param account 账户 */ GmManager.getInstance().deleteAccount(account: string)=>Promise<OptData> 

示例: 

GmManager.getInstance().deleteAccount(account) .then((optData) => { if (optData.isSuccessful()) { // todo } else { // todo BisCode.SUCCESS:'成功'; ' BisCode.SDK_NOT_INITIALIZED, 'SDK未初始化 ' ' BisCode.FAILURE 其他错误 ; } }) .catch((error: Error) => { }) 

##### 错误码信息描述: 

BisCode.SUCCESS:'成功'; ' BisCode.SDK_NOT_INITIALIZED, 'SDK未初始化 ' ' BisCode.FAILURE 其他错误 ; 

#### **3.9.5 删除本地证书** 

导包: import {GmManager,OptData,BisCode} from 'gm_sdk_library'; 

/** * 删除本地证书 */ GmManager.getInstance().deleteLocalCert()=>Promise<OptData> 

##### 示例: 

GmManager.getInstance().deleteLocalCert() .then((optData) => { if (optData.isSuccessful()) { // todo } else { // todo BisCode.SUCCESS 删除成功 BisCode.CERT_NOT_FOUND 本地无证书 BisCode.FAILURE 删除失败 } }) .catch((error: Error) => { }) 

错误码 

BisCode.SUCCESS 删除成功 BisCode.CERT_NOT_FOUND 本地无证书 BisCode.FAILURE 删除失败 

### **3.10 证书重置** 

当PIN码锁定后,证书将无法继续使用,需要引导用户进行证书重置。用户通过输入新的PIN码执行重置 证书的操作,新证书下发下来后,原先被锁定的证书将会被注销。 

导包: import {GmManager,OptData,BisCode} from 'gm_sdk_library'; 

GmManager 

##### API接口 

/** 

* 重置证书,不适合多证场景 

* @param certParam 证书延期相关参数 

* @param pin PIN码 * @returns */ 

GmManager.getInstance().resetCert(certParam: CertParam, pin: string)=>Promise<OptData> 

##### 示例: 

```arkts
let certParam = new CertParam(); certParam.accountId = Config.get().getAccount(); certParam.password = 'password'; certParam.extend = 'extend'; certParam.medium = `HUAWEI MATE 60 PRO`; GmManager.getInstance().resetCert(certParam, pin) .then((optData) => { if (optData.isSuccessful()) { // 成功 } else { // 失败 } }) .catch((e: Error) => { //TODO }); 
```

错误码信息描述: 

' BisCode.SDK_NOT_INITIALIZED, 'SDK未初始化 ' ' BisCode.ACCOUNT_NOT_BOUND, 未绑定账户 ' ' BisCode.INVALID_PIN, 非法PIN码 ' ' BisCode.PASSWORD_SERVER_ERROR, 服务响异常 ' ' BisCode.FAILURE, 失败 ' ' BisCode.CERT_NOT_FOUND, 本地无证书 ' ' BisCode.TRANSACTION_AUTH_FAILURE 交易认证失败 ' ' BisCode.CO_SIGN_ERROR 协签异常 

### **3.11 国密SSL** 

#### **3.11.0 注册gmssl** 

/** * 注册gmssl * @param pin */ GmManager.getInstance().registerGMSSL(pin:string)=>Promise<OptData> 

##### **注** :使用双向国密ssl之前务必完成gmssl的注册。 

#### **3.11.1 配置证书链,以及配置是否开启证书链验证和主机验证** 

导包: import {GmManager} from 'gm_sdk_library'; 

##### **配置证书链** 

/** * 全局配置验证对端身份 * 注意:需要在配置中台与协签之前,发起请求之前完成配置 

* @param chains 证书链 */ GmManager.getInstance().setTlsTrustCerts(chains: ArrayList<string>)=>void 

##### **示例** : 

let rootCa = 

"MIICGzCCAcGgAwIBAgINAOvu3NaAifr0KF9WQjAKBggqgRzPVQGDdTBgMQswCQYDVQQGEwJDT" + 

"jESMBAGA1UECAwJ5rGf6IuP55yBMRIwEAYDVQQHDAnljZfkuqzluIIxETAPBgNVBAoMCEFCQyBsdGQ uMRYwFAYDVQQDDA10ZXN0U00" + 

"yUm9vdENBMB4XDTIxMDcyNjE2MDAwMFoXDTMxMDcyNDE2MDAwMFowYDELMAkGA1UEBhMCQ04xEjAQB gNVBAgMCeaxn+iLj+ecgTESMBAG" + 

"A1UEBwwJ5Y2X5Lqs5biCMREwDwYDVQQKDAhBQkMgbHRkLjEWMBQGA1UEAwwNdGVzdFNNMlJvb3RDQT BZMBMGByqGSM49AgEGCCqBHM9VAYI" + 

"tA0IABF43svwjEXT0jpdblqyKBO0srsurZVkypu2srs1n7Fu3+WMPqjgfSMw2FxlsP1PMHGLC+KIPg xp74VtCIrYg7gajYDBeMAwGA1UdEwQF" + 

"MAMBAf8wHQYDVR0OBBYEFGdT8R3n4u0TN1deqxKqvJcQli5tMB8GA1UdIwQYMBaAFGdT8R3n4u0TN1 deqxKqvJcQli5tMA4GA1UdDwEB/wQEAw" + 

"IBhjAKBggqgRzPVQGDdQNIADBFAiEAhUJSP/lA6sw+GeXN9b9yvHRKU7Vv98jW0ZVJvXKK7QMCIAZd QI8Le9rhZ4+4td4F5xseEpCarU6UVkAXRQiGMzba"; 

let ca = "MIICBDCCAaqgAwIBAgINAMMDt+7PyG6Kq093ajAKBggqgRzPVQGDdTBgMQswCQYDVQ" + 

"QGEwJDTjESMBAGA1UECAwJ5rGf6IuP55yBMRIwEAYDVQQHDAnljZfkuqzluIIxETAPBgNVBAoMCEFC QyBsdGQuMRYwFAYDVQ" + 

"QDDA10ZXN0U00yUm9vdENBMB4XDTIxMDcyODA4MDQxOFoXDTMxMDcyODA4MDQxOFowSTELMAkGA1UE BhMCQ04xEjAQBgNVBAg" + 

"MCeaxn+iLj+ecgTESMBAGA1UEBwwJ5Y2X5Lqs5biCMRIwEAYDVQQDDAl0ZXN0U00yQ0EwWTATBgcqh kjOPQIBBggqgRzPVQGCLQN" + 

"CAASZn9V1+P2VMzpOu1j/zxrwu4KBB0WPnHsyjsYUWOx9X2ZmZjcFTUyS8quASseifdAYZD85nrJOX 3qz4rvYTKRpo2AwXjAMBg" + 

"NVHRMEBTADAQH/MB0GA1UdDgQWBBQTcZFDuLKDKvEWLGWUNnpKpY0mJzAfBgNVHSMEGDAWgBRnU/Ed 5+LtEzdXXqsSqryXEJYubTA" + 

"OBgNVHQ8BAf8EBAMCAYYwCgYIKoEcz1UBg3UDSAAwRQIgK29UBHeObl/oxWng1RPiLdDciUsvascyX xtllhQPzNYCIQCZ0WoBVac" + 

```arkts
"XIA4S2VJa3rbpMycU51/hGjwOzmZChiJfGQ==" let certs = new ArrayList<string>(); certs.add(rootCa); certs.add(ca); GmManager.getInstance().setTlsTrustCerts(certs); 
```

##### 证书链验证默认开启状态。是否开启,根据自身业务需要决定。 

##### **设置SDK内部通讯验证方式** 

/** 

* 设置SDK内部服务验证方式 

* @param verifyChain 是否开启证书链验证 

* @param verifyPeerCertExpiryDate 是否验证对端证书有效期 

* @param verifyHostname 是否验证主机 

*/ GmManager.getInstance().setInnerTrustServer(verifyChain: boolean, verifyPeerCertExpiryDate: boolean, verifyHostname: boolean) 

#### **3.11.3 基于TCP协议的国密SSL** 

基于TCP协议的国密ssl通讯相关的api请阅览 **《鸿蒙版国密SDK-网络库使用文档》** 

#### **3.11.4 基于HTTP协议的国密SSL** 

基于Http协议的国密ssl通讯相关的api请阅览 **《鸿蒙版国密SDK-网络库使用文档》** 

### **3.12 PKI基础功能** 

SDK中提供了基于国密SM2/SM3/SM4等算法封装了一整套PKI基础功能,可根据业务需要选择适合的功 能使用。 

##### 导包: 

import {CryptoHelper} from 'gm_sdk_library'; 

import cryptoFramework from '@ohos.security.cryptoFramework'; 

#### **3.12.1 生成SM4密钥** 

CryptoHelper 

##### 生成16位SM4对称密钥 

/** * 生成128位16字节的SM4对称密钥 * 使用示例: 

* e.g. CryptoHelper.generateSM4Key().then((symKey)=>{const sm4Key = symKey.getEncoded().data;}).catch((error:Error)=>{}) 

* e.g. const symKey = await CryptoHelper.generateSM4Key();const sm4Key = symKey.getEncoded().data; 

* @returns */ 

CryptoHelper.generateSM4KeyPair()=>Promise<cryptoFramework.SymKey> 

##### 示例: 

```arkts
CryptoHelper.generateSM4KeyPair() .then((keyPair) => { let sm4Key = keyPair.getEncoded().data; }) 
```

#### **3.12.2 SM2加密** 

通过国密SM2椭圆曲线算法,利用公钥对数据进行非对称加密 

CryptoHelper 

/** * SM2加密,输出ASN.1结构 * @param message 待加密数据 * @param pubKey 公钥 */ CryptoHelper.sm2Encrypt(message: string | Uint8Array, pubKey: Uint8Array)=>Promise<cryptoFramework.DataBlob> 

##### 示例: 

let cipherData = await CryptoHelper.sm2Encrypt(data, pubkey); //ASN.1结构 cipherData.data //C1C3C2结构 let cipher = CryptoHelper.sm2Asn1ToC1C3C2(cipherData.data); 

注:SDK中SM2加密API加密结果是ASN.1结构的密文,如果需要转成裸的C1C3C2结构,需要通过 CryptoHelper.sm2Asn1ToC1C3C2(sm2Asn1Ciphertext: Uint8Array | string) 进行转换 

#### **3.12.3 SM4 对称加密与解密** 

##### **SM4CBC加密** 

CryptoHelper 

/** * SM4 CBC模式加密,P5补码 * @param sm4Key SM4对称密钥 * @param plainText 待加密原文 * @param iv 初始向量 */ CryptoHelper.sm4CBCEncryptP5Padding(sm4Key: Uint8Array, plainText: string | Uint8Array, iv?: Uint8Array) => Promise<cryptoFramework.DataBlob> 

/** * SM4 CBC模式加密,P7补码 * @param sm4Key SM4对称密钥 * @param plainText 待加密原文 * @param iv 初始向量 */ CryptoHelper.sm4CBCEncryptP7Padding(sm4Key: Uint8Array, plainText: string | Uint8Array, iv?: Uint8Array) => Promise<cryptoFramework.DataBlob> 

##### **SM4CBC解密** 

CryptoHelper 

/** 

* SM4 CBC解密 p5补码 

- @param cipher 密文 

- @param sm4Key 对称密钥 

- @param iv 初始向量 

- @returns */ 

CryptoHelper.sm4CBCDecryptP5Padding(cipher: Uint8Array, sm4Key: Uint8Array, iv?: Uint8Array)=>Promise<cryptoFramework.DataBlob> 

/** * SM4 CBC解密 p7补码 * @param cipher 密文 

- @param sm4Key 对称密钥 

* @param iv 初始向量 

- @returns */ 

CryptoHelper.sm4ECBDecryptP7Padding(cipher: Uint8Array, sm4Key: Uint8Array, iv?: Uint8Array)=>Promise<cryptoFramework.DataBlob> 

#### **3.12.4 SM3 摘要计算** 

##### **SM3摘要计算API** 

CryptoHelper 

/** * sm3摘要计算 * @param data 字符串/二进制原文 * @returns */ 

CryptoHelper.sm3(data: string | Uint8Array)=>Promise<cryptoFramework.DataBlob> 

#### **3.12.5 HMAC-SM3** 

##### **HMAC-SM3摘要计算API** 

CryptoHelper 

/** * HMAC-SM3 * @param keyData 密钥 * @param message 待处理数据 */ 

CryptoHelper.hmacSm3(keyData: string | Uint8Array, message: string | Uint8Array) 

### **3.13 SDK错误日志上报** 

导包: import {GmManager} from 'gm_sdk_library'; 

##### **注册日志监听器** 

GmManager.getInstance().setErrorLogCallback(callback: AsyncCallback<string>) 

AsyncCallback :日志监听器,注册日志监听后,SDK会将错误日志通过监听器回调给日志监听器的注 册者 

示例: 

GmManager.getInstance().setErrorLogCallback((log)=>{ // log为json字符串,具体包含字段如下 hilog.info(0x0012, "LOG", log); }); 

##### **日志中的字段描述** 

/** * 当前账户 */ account /** * SDK版本号 */ sdkVersion /** * 系统类型 */ osType /** * 系统版本/系统软件API版本 */ osFullName /** * 应用二进制接口(Abi)列表。 */ abiList /** * 设备类型,如phone */ deviceType /** * 品牌名称 */ brand /** * 产品版本 */ productModel 

/** * 错误信息 */ errorMsg 

## **4 注意事项说明** 

为了正确使用国密SDK,请务必仔细阅读以下列出的相关注意事项。 

##### **注意:** 国密SDK务必需要完成的操作 

- 1)国密SDK完成初始化后需进行初始化的操作,必须要成功完成初始化工作,否则SDK无法正常 使用 

- 2)国密SDK使用之前需配置相关参数 

- 3)国密SDK初始换完成后,需绑定账户 

- **注意:切换账户** ,如果是Socket通讯请勿关闭连接,并重新构建新的socket 。如果是http通讯, 在切换账户时需要重新构建新的client,否则的话,新用户将会使用上一个账户构建的国密ssl隧 道。 

- **注意:PIN码的限制** ,PIN码6-12位,只允许0-9,a-z,A-Z 

- **注意:PIN码锁定** ,PIN码输错6次,证书将会被锁定,并且无法再继续使用。用户需要重置证书, 重置证书输入新的PIN码,会下发一对新的证书 

- **注意:SDK中证书链验证** ,SDK中内部通讯默认开启证书链验证,若要关闭证书链验证,需手动关 闭 

GmManager.getInstance().setInnerTrustServer(verifyChain: boolean, verifyPeerCertExpiryDate: boolean, verifyHostname: boolean); 

## **5 版权说明** 

版权归南京壹证通信息科技有限公司所有,未经许可禁止翻印。
