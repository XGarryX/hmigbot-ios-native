# 一砂可信数字签名(eTDS)HarmonyOS SDK 接入 

# 文档 

# 1. 说明 

以下为基于EtdsManager 和CertLifecycleManager 的接口说明及使用示例,用于指导如何 在应用中接入手机盾相关功能。 

关于数字盾的系统能力的说明: 

https://developer.huawei.com/consumer/cn/doc/harmonyos-guides/devicesecuritytrustedauth-overview 

# 2. 引入资源和配置 

## 2.1. 引入eTDS 密码模块服务SDK 

在项目entry 模块下的oh-package.json5 文件中,添加密码模块SDK:etdslibrary.har 的引 用,如下: 

{ "name": "entry", "version": "1.0.0", "description": "Please describe the basic information.", "main": "", "author": "", "license": "", "dependencies": { // 引用.har 包 "@esand/etdslibrary": "file:../entry/src/libs/etdslibrary.har" } 

} 

## 2.2. 鸿蒙开发者平台开通数字盾服务权限并更新 Profile(.p7b)文件 

因为鸿蒙官方的要求,使用鸿蒙数字盾功能的App,必须在鸿蒙的开发者网站上在项目中申请 “数字盾服务”权限,且在申请权限之后,无论之前是否申请生成过.p7b 开发者Profile,都需 要重新申请和生成新的.p7b 文件,申请流程链接如下: 

https://developer.huawei.com/consumer/cn/doc/harmonyos-guides/devicesecuritydeviceverify-activateservice ,只需要开通里面的 数字盾服务 权限即可,如下图: 

## 2.3. 配置eTDS SDK 的源码混淆规则 

(1)确认需要引入使用eTDS SDK 的模块开启了代码混淆,在模块级的buildprofile.json5 配置文件中开启源码混淆功能配置如下: 

"arkOptions": { "obfuscation": { "ruleOptions": { "enable": true // 配置true,即可开启源码混淆功能 "files": [ " ./obfuscation-rules.txt " // 混淆规则文件 

] } } } 

- (2)当确认开启了源码混淆规则之后,需要配置具体的混淆规则,如下: 

-enable-property-obfuscation -enable-toplevel-obfuscation -enable-filename-obfuscation -enable-export-obfuscation 

# 3. 模块概述 

## 3.1. EtdsManager 

EtdsManager 是用于管理手机盾核心功能的类,主要负责设备支持信息获取、激活/去激活手 机盾等操作。 

## 3.2. CertLifecycleManager 

CertLifecycleManager 用于证书生命周期管理,包括申请、查询、吊销、签名、验签、绑定 生物认证等功能。 

4. 

# 接口说明与使用示例 

## 4.1. EtdsManager 接口 

### 4.1.1. 初始化EtdsManager 

在使用EtdsManager 前,需要先初始化该类的实例。传入Context 对象以完成初始化。 

const etdsManager = new EtdsManager(context); 

context 是ArkTS 环境中的上下文对象,通常在Ability 或UI 组件中获取。 

### 4.1.2. 设置网络请求处理器(必接项) 

EtdsManager 需要一个实现了RequestMsgProcessor 的网络请求处理器,用于与服务端通 信。 

class MyRequestMsgProcessor implements RequestMsgProcessor { // 实现对应的方法 } etdsManager.setRequestMsgProcessor(new MyRequestMsgProcessor()); 

如果不设置此处理器,调用activate()、deActivate() 等方法时会返回错误码: CLIENT_ERROR。 

export interface RequestMsgProcessor { 

/** * @param processor 当前流程, * @param req SDK 生成的初始化请求报文 * @return 获得响应报文 */ request(processor: number, req: string): Promise<string>; } 

BIO_MGT= 0, // 生物认证管理 ETDS_ACTION_ACTIVATE_APP = 1, // 激活 = ETDS_ACTION_DE_ACTIVATE_APP 2, //去激活 

ETDS_REQUEST_PROCESS_APPLY_CERT_INIT = 101, // 申请证书初始化 ETDS_REQUEST_PROCESS_APPLY_CERT = 102, // 申请证书 ETDS_REQUEST_PROCESS_CHECK_CERT = 103, // 检查证书 ETDS_REQUEST_PROCESS_DELETE_CERT_INIT = 104, // 删除证书初始化 ETDS_REQUEST_PROCESS_DELETE_CERT = 105, // 删除证书 ETDS_REQUEST_PROCESS_CHANGE_PIN = 106, // 修改PIN ETDS_REQUEST_PROCESS_SIGN_DATA = 107, // 数字签名 ETDS_REQUEST_PROCESS_VERIFY_DATA = 108, // 验签 ETDS_REQUEST_PROCESS_DEVICE_POLICY = 109, // 设备策略 

### 4.1.3. 获取服务端配置的设备策略 

async getDevicePolicy(transId: string): Promise<Result> {} 

#### 功能说明: 

根据设备信息查询服务端配置的设备策略。 

#### 参数: 

- transId: 业务流水号。 

#### 返回值: 

- Result: 包含devicePolicy 字段,表示服务端配置的设备策略。 

   - devicePolicy.supportTee:是否支持TEE(1 支持;0:不支持)。 

   - devicePolicy.supportSe:是否支持SE(1 支持;0:不支持)。 

   - devicePolicy.supportTui:是否支持TUI(1 支持;0:不支持)。 

- Result.code: 

   - SUCCESS 

   - CLIENT_ERROR 

   - NETWORK_ERROR 

   - SERVER_ERROR 

#### 使用示例: 

// 实例化CertLifecycleManager 

- let context = getContext(); 

- let certManager = new CertLifecycleManager(context, this.alias); 

- // 创建实现网络接口的具体类的实例 

- const requestMsgHandler = new RequestMsgHandler(this.baseUrl); 

- // 设置网络请求实现requestMsgProcessor 

- certManager.setRequestMsgProcessor(requestMsgHandler); 

- let transId = AppUtil.getTransId('etds'); 

- let devicePolicy = ''; 

- let result = await certManager.getDevicePolicy(transId); 

- let msg = `certManager.getDevicePolicy, code:${result.code}, message:${result.msg}`; 

this.saveLog(msg); 

if (EtdsConstantsEnum.SUCCESS === result.code) { 

devicePolicy = result.devicePolicy; 

} 

this.saveLog("设备策略:" + devicePolicy); 

- //{"supportTee":"1","supportSe":"1","supportTui":"1"} 

### 4.1.4. 获取设备支持情况 

async getSupportInfo(devicePolicy: string = ''): Promise<Result> {} 

功能说明: 获取设备支持的手机盾类型(软盾、TEE 盾、SE 盾)以及当前是否已激活等信息。 

#### 参数: 

- devicePolicy,服务端返回的设备策略,如服务端需要限制设备时,则传入服务端返回的 设备策略,否则可不传入。 

#### 返回值: 

- Result: 包含supportInfo 字段,其中supportInfo.supportMode 表示支持的模式列 表。 

- Result.code: 

   - SUCCESS 

   - ETDS_ERR_DEVICE_IS_ROOT 

export enum EtdsModeEnum { /** * 软盾 */ ETDS_MODE_SOFT = 1, /** * TEE 手机盾 */ ETDS_MODE_TEE = 2, /** * SE 手机盾 */ ETDS_MODE_SE = 3, } 

#### 使用示例: 

let etdsManager = new EtdsManager(context); let result = await etdsManager.getSupportInfo(); 

if (result.code === EtdsConstantsEnum.SUCCESS) { 

let supportModes = result.supportInfo?.getSupportMode(); // 支持的模式 

} 

### 4.1.5. 激活手机盾 

async activate(mode: EtdsModeEnum): Promise<Result> 

#### 功能说明: 激活指定类型的手机盾。 

#### 参数: 

- mode: 指定激活的模式,如EtdsModeEnum.ETDS_MODE_SOFT(软盾)、 EtdsModeEnum.ETDS_MODE_TEE(TEE 盾)等。 

#### 返回值: 

- Result.code: 

   - SUCCESS 

   - CLIENT_ERROR 

#### 使用示例: 

let etdsManager = new EtdsManager(context); 

let result = await etdsManager.activate(EtdsModeEnum.ETDS_MODE_SOFT); if (result.code === EtdsConstantsEnum.SUCCESS) { 

console.log("激活成功"); 

} 

### 4.1.6. 去激活手机盾 

async deActivate(): Promise<Result> 

#### 返回值: 

- Result.code: 

   - SUCCESS 

   - CLIENT_ERROR 

功能说明: 清除手机盾数据,即去激活当前已激活的手机盾。 

#### 使用示例: 

```arkts
let etdsManager = new EtdsManager(context); let result = await etdsManager.deActivate(); if (result.code === EtdsConstantsEnum.SUCCESS) { console.log("去激活成功"); } 
```

## 4.2. CertLifecycleManager 接口 

### 4.2.1. 初始化CertLifecycleManager 

在使用证书生命周期管理功能前,需初始化CertLifecycleManager 实例。构造函数参数如 下: 

const certLifecycleManager = new CertLifecycleManager(context, aliasName); 

- context: 应用上下文对象(通常由Ability 提供) 

- aliasName: 证书别名,用于标识当前操作的证书 

### 4.2.2. 设置网络请求处理器 

public setRequestMsgProcessor(value: RequestMsgProcessor): void 

#### 功能说明: 设置网络请求实现,由应用层提供。 

#### 使用示例: 

const requestMsgHandler = new RequestMsgHandler(baseUrl); certLifecycleManager.setRequestMsgProcessor(requestMsgHandler); 

### 4.2.3. 申请证书初始化 

public async applyCertInit(transId: string, certCfg: CertConfig): Promise<Result> 

#### 功能说明: 生成P10 请求包,用于后续提交证书申请。 

#### 参数: 

- transId: 业务流水号。 

- certCfg: 证书配置对象,包含密钥类型、别名、主题等信息。 

#### 返回值: 

- Result.code: 

   - SUCCESS 

   - ETDS_ERR_APP_INACTIVATE 

   - CLIENT_ERROR 

#### 使用示例: 

```arkts
let certCfg = new CertConfig(); certCfg.keyType = EtdsKeyTypeEnum.SM2; certCfg.alias = "user_alias"; = certCfg.subject "cn=1"; 
let result = await certLifecycleManager.applyCertInit("trans123", certCfg); if (result.code === EtdsConstantsEnum.SUCCESS) { let p10 = result.msg; // P10 数据 } 
```

### 4.2.4. 提交证书申请 

public async applyCert(transId: string, caRequest: string): Promise<Result> 

功能说明: 将P10 包和用户信息提交至CA 中心,完成证书申请。 

#### 参数: 

- transId: 业务流水号。 

- caRequest: 用户申请报文,通常为JSON 格式。 

#### 返回值: 

- Result.code: 

   - SUCCESS 

   - ETDS_ERR_APP_INACTIVATE 

   - CLIENT_ERROR 

   - NETWORK_ERROR 

   - SERVER_ERROR 

#### 使用示例: 

```arkts
let userApply = new UserApply(); = userApply.idNumber "123456"; = userApply.userName "张三"; userApply.type = 1; userApply.duration = 12; userApply.p10 = p10; userApply.isDouble = false; 
```

let caRequest = JSON.stringify(userApply); 

let result = await certLifecycleManager.applyCert("trans123", caRequest); 

### 4.2.5. 查询证书 

public async checkCert(transId: string): Promise<Result> 

#### 功能说明: 查询当前用户的证书状态。 

#### 参数: 

- transId: 业务流水号。 

#### 返回值: 

- Result.code: 

   - SUCCESS 

   - CLIENT_ERROR 

   - NETWORK_ERROR 

   - ETDS_ERR_CERT_NOT_FOUND 

   - ETDS_ERR_CERT_EXPIRED 

   - ETDS_ERR_CERT_STATUS_ERROR 

- SERVER_ERROR 

- ETDS_ERR_DATA_NEEDS_RECOVERY 

#### 使用示例: 

```arkts
let result = await certLifecycleManager.checkCert("trans123"); if (result.code === EtdsConstantsEnum.SUCCESS) { let certs = result.cert; // 返回证书列表 } 
```

### 4.2.6. 修改PIN 码 

public async changePIN(transId: string): Promise<Result> 

功能说明: 修改用户PIN 码,需通过TUI 输入旧PIN 并确认新PIN。 

#### 参数: 

  transId: 业务流水号。 

#### 返回值: 

- Result.code: 

   - SUCCESS 

   - ETDS_ERR_APP_INACTIVATE 

   - CLIENT_ERROR 

   - ETDS_ERR_PIN_SECURE_POLICY 

   - ETDS_ERR_UNSUPPORTED_SVR 

使用示例: 

let result = await certLifecycleManager.changePIN("trans123"); 

### 4.2.7. 吊销证书 

public async deleteCert(transId: string): Promise<Result> 

#### 功能说明: 吊销当前用户的证书。 

#### 参数: 

- transId: 业务流水号。 

#### 返回值: 

- Result.code: 

   - SUCCESS 

   - CLIENT_ERROR 

   - SERVER_ERROR 

   - NETWORK_ERROR 

#### 使用示例: 

let result = await certLifecycleManager.deleteCert("trans123"); 

### 4.2.8. 对数据进行签名(PIN 码/指纹/人脸) 

public async signData(transId: string, plainData: string, signType: number, authType: number = EtdsAuthType.AUTHTYPE_PIN): Promise<Result> 

#### 功能说明: 对指定数据进行签名。 

#### 参数: 

- transId: 业务流水号。 

- plainData: 待签名数据。 

- signType: 签名类型,如EtdsSignTypeEnum.PKCS1(P1 签名), EtdsSignTypeEnum.PKCS7_ATTACH(P7 签名)。 

- authType: 认证方式,0:PIN 码;1:指纹;4:人脸。 

#### 返回值: 

- Result.code: 

   - SUCCESS 

   - ETDS_ERR_APP_INACTIVATE 

   - CLIENT_ERROR 

   - NETWORK_ERROR 

   - ETDS_ERR_CERT_NOT_FOUND 

   - ETDS_ERR_CERT_EXPIRED 

   - ETDS_ERR_CERT_STATUS_ERROR 

   - SERVER_ERROR 

   - ETDS_ERR_UNSUPPORTED_ALG 

   - ETDS_ERR_KEY_NOT_FOUND 

   - ETDS_TUI_ERROR 

   - ETDS_ERR_BIO_TEMPORARILY_LOCKED 

   - ETDS_ERR_BIO_NOT_FOUND 

#### 使用示例: 

let result = await certLifecycleManager.signData("trans123", "待签名内容", EtdsSignTypeEnum.PKCS1, EtdsAuthType.AUTHTYPE_PIN); 

### 4.2.9. 验证签名 

public async verifyData(transId: string, caRequest: string): Promise<Result> 

#### 功能说明: 验证签名结果。 

#### 参数: 

- transId: 业务流水号。 

- caRequest: 验签报文,通常为JSON 格式。 

#### 返回值: 

- Result.code: 

   - SUCCESS 

   - ETDS_ERR_APP_INACTIVATE 

   - CLIENT_ERROR 

   - NETWORK_ERROR 

   - ETDS_ERR_BIO_MISMATCH_FROM_SERVER 

   - SERVER_ERROR 

#### 使用示例: 

let result = await certLifecycleManager.verifyData("trans123", "验签报文"); 

### 4.2.10. 绑定生物认证 

public async bindBio(transId: string, authType: number): Promise<Result> 

#### 功能说明: 将用户生物特征与手机盾绑定。 

#### 参数: 

- transId: 业务流水号。 

- authType: 要绑定的生物认证类型,1:指纹;4:人脸。 

#### 返回值: 

- Result.code: 

   - SUCCESS 

   - ETDS_ERR_APP_INACTIVATE 

   - CLIENT_ERROR 

   - NETWORK_ERROR 

   - ETDS_ERR_CERT_NOT_FOUND 

   - ETDS_ERR_CERT_EXPIRED 

   - ETDS_ERR_CERT_STATUS_ERROR 

   - ETDS_ERR_BIO_TEMPORARILY_LOCKED 

   - ETDS_TUI_ERROR 

   - ETDS_ERR_UNSUPPORTED_SVR 

   - SERVER_ERROR 

   - ETDS_ERR_KEY_NOT_FOUND 

o ETDS_ERR_BIO_NOT_FOUND 

#### 使用示例: 

let result = await certLifecycleManager.bindBio("trans123", 1); // 1 表示指纹认证 

### 4.2.11. 解绑生物认证 

public async unbindBio(transId: string, authType: number): Promise<Result> 

#### 功能说明: 解除生物特征与手机盾的绑定。 

#### 参数: 

- transId: 业务流水号。 

- authType: 要解绑的生物认证类型,1:指纹;4:人脸。 

#### 返回值: 

- Result.code: 

   - SUCCESS 

   - CLIENT_ERROR 

   - NETWORK_ERROR 

   - SERVER_ERROR 

   - ETDS_ERR_UNSUPPORTED_SVR 

#### 使用示例: 

let result = await certLifecycleManager.unbindBio("trans123", 1); 

# 5. 使用流程总结 

1. 初始化EtdsManager :调用getSupportInfo() 获取设备支持信息。 

2. 激活手机盾 :根据支持信息选择模式调用activate()。 

3. 设置网络处理器 :为CertLifecycleManager 设置RequestMsgProcessor。 

4. 申请证书 : 

   - 调用applyCertInit() 生成P10 包; 

   - 构建用户申请信息并调用applyCert() 完成申请。 

5. 其他操作 :根据需要调用checkCert(), changePIN(), deleteCert(), signData(), verifyData() 等方法。 

6. 生物认证 :可选绑定指纹等生物特征,并使用bioSign() 进行签名。 

# 6. 注意事项 

- 所有网络请求必须实现RequestMsgProcessor 接口。 

- 所有敏感操作(如签名、修改PIN)都需要用户交互(TUI)或生物认证。 

# 7. 错误码 

EtdsConstantsEnum 中的code 

/** * 成功 */ SUCCESS = 0, /** * 客户端错误 */ 

CLIENT_ERROR = 1, /** * 服务端返回报文错误 */ SERVER_ERROR = 2, /** * 网络错误 */ NETWORK_ERROR = 3, /** * 不支持的服务。调用SDK 不支持的功能接口时会返回该错误码 */ ETDS_ERR_UNSUPPORTED_SVR = 4, /** * 无效的LICENSE */ ETDS_ERR_LICENSE_INVALID = 5, /** * 会话忙,请稍后重试 */ ETDS_ERR_SESSION_BUSY = 6, /** * 不支持的算法 */ ETDS_ERR_UNSUPPORTED_ALG = 7, /** * 未知的密码算法异常或获取匿名证书链失败 */ ETDS_ERR_CRYPTO_FAILED = 8, /** * 设备被Root。出现该错误码后:该设备无法使用 */ 

ETDS_ERR_DEVICE_IS_ROOT = 9, 

/** 

* 应用未激活,在未激活状态下使用手机盾功能时openSession 接口会返回该错误码 

*/ 

ETDS_ERR_APP_INACTIVATE = 10, 

/** 

* 证书不存在,出现该错误码后:需要走申请证书流程 

*/ 

ETDS_ERR_CERT_NOT_FOUND = 11, 

/** 

* 证书格式错误,导入证书失败时会返回该错误码。 

* 出现该错误码后:需要走申请证书流程 

*/ 

ETDS_ERR_BAD_CERT = 12, 

/** 

* 证书过期,导入证书失败时会返回该错误码。 

- 出现该错误码后:需要走申请证书流程 

*/ 

ETDS_ERR_CERT_EXPIRED = 13, 

/** 

* 用户取消,在TUI 页面上用户点击【取消】按钮。 * 出现该错误码后:可结束流程,使用其他方式 

*/ ETDS_ERR_CANCEL = 14, 

/** 

* 输入密码过短,在TUI 页面设置密码长度过短,默认6-8 位,可自定义。 * 出现该错误码后:需要提示用户输入密码长度过短 */ 

ETDS_ERR_PIN_TOO_SHORT = 15, 

/** 

* 两次密码不匹配,调用生成P10 包接口、修改PIN 码接口时,在TUI 页面两次密码不匹配。 * 出现该错误码后:需要提示用户输入密码不匹配 

*/ 

ETDS_ERR_PIN_NOT_MATCH = 16, 

/** 

* 密码认证失败,在进行身份认证时密码错误 

*/ ETDS_ERR_PIN_AUTH_FAILED = 17, 

/** 

* 错误次数太多,认证被锁定。 

* 出现该错误码后: 

* ● 调用解锁PIN 接口,重新设置密码 

* ● 重新申请证书 

*/ 

ETDS_ERR_PIN_LOCKED = 18, 

/** 

* 认证超时,在TUI 页面长时间未输入密码。 

* 出现该错误码后:重新调用流程 

*/ 

ETDS_ERR_TUI_TIME_OUT = 19, 

/** 

* 密码过于简单,调用生成P10 包接口、修改PIN 码接口时密码太简单,提示用户输入复杂密码。 * 出现该错误码后:需要提示用户密码过于简单 

*/ 

ETDS_ERR_PIN_WEAK = 20, 

/** 

* 与关联数据相似,调用生成P10 包接口、修改PIN 码接口时设置的密码与关联数据相似。 * 出现该错误码后:需要提示用户输入与关联数据无关的密码 

*/ ETDS_ERR_PIN_SIMILAR = 21, 

/** 

* PIN 安全策略不满足 */ ETDS_ERR_PIN_SECURE_POLICY = 22, 

/** 

* 修改后的PIN 与当前PIN 相同 */ ETDS_ERR_PIN_SAME = 23, 

/** * TUI 上输入为空 */ ETDS_ERR_TUI_INPUT_IS_NULL = 24, 

/** 

* TUI 错误,在进行身份认证时,TUI 页面异常 */ ETDS_TUI_ERROR = 25, 

/** * 签名失败 */ ETDS_SIGN_FAILED = 26, 

/** 

* 验签失败 */ ETDS_VERIFY_FAILED = 27, 

/** 

* 加密失败 */ ETDS_ENCRYPT_FAILED = 28, 

/** 

* 解密失败,在调用解密接口时,如解密失败会返回该错误码 */ ETDS_DECRYPT_FAILED = 29, 

/** * 密钥不存在 */ ETDS_ERR_KEY_NOT_FOUND = 30, 

/** * 证书被禁用 */ ETDS_ERR_CERT_STATUS_ERROR = 31, 

/** 

* 移动端和服务端数据不一致时,重新激活当前盾,提示再试一次 */ ETDS_ERR_TRY_AGAIN = 33, 

/** 

* 有数据需要恢复 */ ETDS_ERR_DATA_NEEDS_RECOVERY = 34, 

/** 

* 未录入认证信息 */ 

ETDS_ERR_BIO_NOT_ENROLLED = 35, 

/** 

* 生物识别未绑定 */ ETDS_ERR_BIO_NOT_FOUND = 36, 

/** 

* 生物认证本地比对不匹配,请使用绑定生物识别进行验证 */ ETDS_ERR_BIO_MISMATCH = 37, 

/** * 点击了FALLBACK 按钮 */ STATUS_RESULT_FALLBACK = 38, /** * 认证超时 */ ETDS_ERR_BIO_TIMEOUT = 39, /** * 生物认证被临时锁定 */ ETDS_ERR_BIO_TEMPORARILY_LOCKED = 40, /** * 生物认证被永久锁定,系统默认错误25 次后锁定 */ ETDS_ERR_BIO_PERMANENT_LOCKED = 41, /** * 生物认证服务端比对不匹配,请使用绑定生物识别进行验证 */ ETDS_ERR_BIO_MISMATCH_FROM_SERVER = 42,
