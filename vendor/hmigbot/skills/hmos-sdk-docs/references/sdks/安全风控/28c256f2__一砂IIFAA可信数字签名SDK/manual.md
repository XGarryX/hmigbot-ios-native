# 一砂 IIFAA 可信数字签名鸿蒙 SDK 使用指南 

版本号 

作者 

修订内容 

v1.0 

@wmding 

编辑初版 

1 概述 

1.1 编写目的 

本设计说明文档的编写目的是为了方便接入方快速接入 eTDS SDK 。 

1.2 适用范围 

本文档适用 Harmony OS 端需要接入 eTDS SDK 的接入方。 

2 引入资源 

2.1 引入 SDK 包 

需要引入的 SDK : 

etdsLibrary.har 

在 entry 模块下的 oh-package.json5 中添加依赖: 

{ "name": "entry", "version": "1.0.0", "description": "Please describe the basic information.", "main": "", "author": "", "license": "", "dependencies": { // 引用 .har 包 "etdsLibrary": "file:../entry/src/libs/ etdsLibrary.har", } } 

如图所示: 

# 2.2 引入资源文件 

将授权文件复制到 entry/src/main/resources/rawfile/etds 目录下。 etds_keystore.lic 文件是移动端授权文件,和应用绑定。 

# 3 API 说明 

# 3.2 手机盾管理类 EtdsManager 

# 3.2.1 网络请求 

移动端和服务端进行交互的网络请求由 App 实现。 

方法定义: 

调用 etdsManager.setRequestMsgProcessor() 方法,设置网络请求。 

# 参数 

RequestMsgProcessor , requestMsgProcessor 包含用于规范 SDK 和 服务器进行数据交换接口的类对象 

返回值 

# 无 

/** * 设置网络请求的实现 * @param value 网络请求的实现,由 APP 实现 */ public setRequestMsgProcessor(value: RequestMsgProcessor) { } 

# 示例: 

```arkts
let etdsManager = new EtdsManager(); // 创建实现了接口的具体类 的实例 const requestMsgHandler = new RequestMsgHandler(); // 使用 setRequestMsgProcessor 方法设置 requestMsgProcessor etdsManager.setRequestMsgProcessor(requestMsgHandler); // RequestMsgHandler 的具体实现示例: export class 
RequestMsgHandler implements RequestMsgProcessor { async request(processor: number, req: string): Promise<string> { // 服务 端请求地址 let url = baseUrl + "/etds/demo"; let resp = ""; try { resp = await HttpUtils.request(url, req); } catch (err) { 
```

Logger.error(TAG, err); } Logger.info(TAG, " 获取到响应: " + resp); return resp; } } 

# 3.2.2 TA 生命周期管理 

# 3.2.2.1 TA 版本检查 

TA 版本检查,对手机盾需要使用的 TA 进行版本检查。在使用手机盾 之前需要先对 TA 版本进行检查。 

TA 使用流程如下: 

方法定义: 

public void checkTAVersion(Callback callback) { } 

字段 

类型 

描述 

callback 

Callback 

结果回调,实现对 TA 版本检查的结果回调 

根据 etdsResult.code 的返回直接后续处理 

返回 ETDS_TA_INSTALL("28", "TA 需要安装 ") 时, TA 安装, APP 调用 TA 安装 

返回 ETDS_TA_UPDATE("29", "TA 需要更新 ") 时, TA 更新, APP 调用 TA 更新 

返回 SUCCESS("0", " 成功 ") 时, TA 没有问题,不用后续流程 

示例: 

final EtdsManager etdsManager = new EtdsManager(this); // 网络 请求, APP 实现 RequestMsgProcessor 中的 request ,进行同步网络请 

求 etdsManager.setRequestMsgProcessor(new RequestMsgProcessor() { @Override public String request(int processor, String req) { String url = mUrl + CommonConstants.URL; String post = HttpUtil.synRequest(url, req); return post; } }); // 检查 TA 版本 

etdsManager.checkTAVersion(new Callback() { @Override public void onResult(Result result) { if(SUCCESS.getCode().equals(result.getCode())){ // TA 版本不需要 更新 }else if (ETDS_TA_UPDATE.getCode().equals(result.getCode())) { // TA 版本需要更新 ,todo } } }); 

3.2.2.2 TA 生命周期管理 

TA 生命周期管理接口,分为 TA 下载、 TA 更新、 TA 删除。根据 TA 版本检查 返回的结果进行后续处理 

过程 

# 方法定义: 

/** * * @param commandId TA 生命周期流程 * @param callback 回 调 */ public void tamBusiness(String commandId, Callback callback) { } 

字段 

类型 

描述 

commandId 

String 

TA 生命周期流程: 

InstallTA :下载 TA 

UpdateTA :更新 TA 

DeleteTA :删除 TA 

callback 

Callback 

# 结果回调,实现对 TA 版本检查的结果回调 

当 etdsResult.code 为 ETDS_SUCCESS 时,操作成功 

# 示例: 

final EtdsManager etdsManager = new EtdsManager(this); // 网络 请求, APP 实现 RequestMsgProcessor 中的 request ,进行同步网络请 求 etdsManager.setRequestMsgProcessor(new 

RequestMsgProcessor() { @Override public String request(int processor, String req) { String url = mUrl + CommonConstants.URL; String post = HttpUtil.synRequest(url, req); return post; } }); 

new Callback() { @Override public void onResult(Result result) { } }); 

# 3.2.3 查看终端支持信息 

方法定义: 

public async getSupportInfo(): Promise<Result> { } 

调用 etdsManager.getSupportInfo() 方法,查看当前设备的支持信 息。 

# 参数 

当 result.getCode() 为 SUCCESS.getCode() 时, result 获取 getSupportInfo() 不为空,获取该设备的支持情况成功,否则获取该设 备的支持情况失败 

# 返回值 

无 

SupportInfo 类,如下: 

export class SupportInfo { /** * 返回当前支持的手机盾种类 */ supportMode: number[] = []; /** * 返回当前激活的手机盾种类。返 回 null 表示未激活。 */ activatedMode: EtdsModeEnum | null; /** * 是否支持 IFAA 生物认证 */ isSupportIfaa: boolean; /** * 支持的 IFAA 生物认证类型 */ authType: number[]; /** * 是否支持软盾 */ isSupportSoft: boolean; /** * 软盾激活状态, 0 :未激活; 1 :已经激 活 */ softStatus: number; /** * 是否支持 TEE 盾 */ isSupportTee: boolean; /** * TEE 盾激活状态, 0 :未激活; 1 :已经激活 */ teeStatus: number; /** * 是否支持 SE 盾 */ isSupportSe: boolean; /** * SE 盾激活状态, 0 :未激活; 1 :已经激活 */ seStatus: number; /** * 是否是 NXP 芯片手机 */ isNxp: boolean; } 

# 示例: 

// 实例化 EtdsManager let etdsManager = new EtdsManager(); let result = await etdsManager.getSupportInfo(); let supportInfo = result.getSupportInfo(); // 返回当前支持的手机盾种类 let supportMode = supportInfo.getSupportMode(); // 当前激活的手机 盾种类,返回 null 表示未激活。 let activateMode = supportInfo.getActivatedMode(); 

3.2.4 激活手机盾 

创建 EtdsManager 实例,调用 etdsManager.activate() 完成手机盾激 活。 

# TEE 手机盾激活: 

TEE+SE 手机盾激活: 

# 方法定义: 

/** * 手机盾激活接口 * * @param mode EtdsModeEnum 中的枚举值 */ public async activate(mode: EtdsModeEnum): Promise<Result> { } 

# 字段 

类型 

# 描述 

mode 

EtdsModeEnum 中的枚举 

激活的手机盾种类。需要调用 supportInfo.getSupportMode() 来判 断。 

# 示例: 

// 实例化 EtdsManager let etdsManager = new EtdsManager(); // 设备支持的手机盾模式 let mode = EtdsModeEnum.ETDS_MODE_SOFT; // 创建实现了接口的具体类的 实例 const requestMsgHandler = new RequestMsgHandler(); // 使 用 setRequestMsgProcessor 方法设置 requestMsgProcessor etdsManager.setRequestMsgProcessor(requestMsgHandler); // 激活 let result = await etdsManager.activate(mode); let msg = ''; if (EtdsConstantsEnum.SUCCESS == result.code) { msg = ' 激活成功 '; } else { msg = ' 激活失败: ' + result.msg; } 

3.2.5 手机盾去激活 

客户端需要对已经激活的手机盾的状态进行清除时,使用该接口进行 手机盾去激活,即注销手机盾。 

当调用成功后,手机盾中保存的证书等都会被删除。 

TEE 手机盾去激活 

TEE+SE 手机盾去激活 

# 方法定义: 

/** * 手机盾去激活接口 */ public async deActivate(): Promise<Result> { } 

# 示例: 

// 实例化 EtdsManager let etdsManager = new EtdsManager(); // 创建实现了接口的具体类的实例 const requestMsgHandler = new 

RequestMsgHandler(); // 使用 setRequestMsgProcessor 方法设置 requestMsgProcessor 

```arkts
etdsManager.setRequestMsgProcessor(requestMsgHandler); // 手机 盾去激活 let result = await etdsManager.deActivate(); Logger.info(TAG, result.toString()); let msg = ''; if (EtdsConstantsEnum.SUCCESS == result.code) { msg = ' 去激活成 功 '; } else { msg = ' 去激活失败: ' + result.msg; } 
```

3.3 证书管理 CertManager 

CertManager 提供了证书的管理功能。 

3.3.2 网络请求 (APP) 

在使用软盾时, SDK 需要和手机盾服务端进行通信。 APP 需要设置 setRequestMsgProcessor ,进行网络请求实现。 

# 方法定义: 

/** * 设置网络请求实现 */ public setRequestMsgProcessor(value: RequestMsgProcessor) { } 

字段 

类型 

描述 

mRequestMsgProcessor 

RequestMsgProcessor 

mRequestMsgProcessor 包含用于规范 SDK 和服务器进行数据交换接 口的类对象, 

示例: 

// 实例化 CertManager let certManager = new CertManager(); let openSessionResult = await certManager.openSession(alias); Logger.info(TAG, "openSessionResult: " + openSessionResult.toString()); // 创建实现了接口的具体类的实例 const requestMsgHandler = new RequestMsgHandler(); // 使用 

```arkts
setRequestMsgProcessor 方法设置 requestMsgProcessor certManager.setRequestMsgProcessor(requestMsgHandler); // RequestMsgHandler 的具体实现示例: export class RequestMsgHandler implements RequestMsgProcessor { async request(processor: number, req: string): Promise<string> { Logger.info(TAG, "processor: " + processor); Logger.info(TAG, "req: " + req); let url = baseUrl + "/etds/demo"; let resp = ""; try { resp = await HttpUtils.request(url, req); } catch (err) { Logger.error(TAG, err); } Logger.info(TAG, " 获取到响应: " + resp); return resp; } } 
```

3.3.3 打开会话 Session 

该方法需要在每一次手机盾业务操作流程最前面调用。 

方法定义: 

/** * 用来控制打开应用和容器 * * @param aliasName 证书别名 * @return openSession 的结果 */ public async openSession(aliasName: string): Promise<Result> { } 

字段 

类型 

描述 

aliasName 

String 

证书别名,调用方需保证其唯一性。 

3.3.4 关闭会话 Session 

该方法需要在每一次手机盾业务操作流程结束时(无论是成功还是失 败结果)调用。 

方法定义: 

/** * 关闭会话 Session */ public async closeSession(): Promise<Result> { } 

# 3.3.5 获取证书 

调用 certManager.exportCert(alias) 获取本地证书。 

# 方法定义: 

/** * 获取证书 */ public async exportCert(): Promise<Result> { } 

# 示例: 

// 实例化 CertManager let certManager = new CertManager(); // 打 开会话 let openSessionResult = await certManager.openSession(alias); Logger.info(TAG, 

"openSessionResult: " + openSessionResult.toString()); // 获取证书 let result = await certManager.exportCert(); 

this.saveLog(`certManager.exportCert: code:${result.code}, message:${result.msg}`); if (EtdsConstantsEnum.SUCCESS == result.code) { // 有证书 this.cert = result.cert[0]; } // 关闭会话 certManager.closeSession(); 

# 3.3.6 申请证书 

3.3.6.1 生成 P10 包 

方法定义: 

/** * 生成申请证书用的 P10 包 * @param certCfg 证书配置 * @param pinCfg PIN 码配置 * @returns */ public async genP10(certCfg: CertConfig, pinCfg: PinConfig): Promise<Result> { } 

CertConfig : 

export class CertConfig { // 证书别名,全局唯一 alias: string; // 证 书主题,类似于 (c=cn,cn=test) ,不同项目格式由服务器确定 subject: string; // 密钥类型 1: RSA 2: ECC 3: SM2 keyType: number; // 密钥长度(生成 SM2 的 p10 此处填写 0, 生成 RSA 的 P10 ,具体 长度根据项目方案确定) keySize: number; // ECC 曲线,其他类型 证书为 0 curveFlag: number; } 

PinConfig : 

export class PinConfig { /** * 是否使用 SDK 提供的默认的 UI ,默认 为 false * 如设置 false , APP 需自定义 */ useDefaultPinUI: boolean = false; /** * useDefaultPinUI 为 false 时, pin 不可为空 */ pin: string = ''; /** * useDefaultPinUI 为 true 时,使用 PIN 认证的重试次 数,默认为 5 次 * 触发锁定后,需重新申请生成 P10 包进行申请证书 */ maxRetryCount: number = 5; /** * 在 changePin 时需要设置 * pin: 为新 PIN * oldPin: 为老 PIN */ oldPin: string = ''; /** * 吊销证 书删除密钥时,是否使用默认 PIN 页面进行 PIN 认证 */ deleteCertUsePinView: boolean = true; /** * PIN 策略 */ etdsPinPolicy: EtdsPinPolicy = new EtdsPinPolicy(); } 

# 示例: 

// 实例化 CertManager let certManager = new CertManager(); // 打 开会话 let openSessionResult = await certManager.openSession(alias); Logger.info(TAG, 

```arkts
"openSessionResult: " + openSessionResult.toString()); // 创建实现 网络接口的具体类的实例 const requestMsgHandler = new RequestMsgHandler(); // 设置网络请求实现 requestMsgProcessor certManager.setRequestMsgProcessor(requestMsgHandler); let certCfg: CertConfig = new CertConfig(); // 密钥类型 certCfg.keyType = KeyTypeEnum.SM2; // 证书别名 certCfg.alias = alias; // 证书主题 certCfg.subject = 'cn=1'; let pinCfg: PinConfig = new PinConfig(); // PIN 码 pinCfg.pin = pin; // 生成 P10 包 let result = await certManager.genP10(certCfg, pinCfg); if 
```

(EtdsConstantsEnum.SUCCESS == result.code) { // p10 包数据 let p10 = result.msg; // todo 请求服务端申请证书 // ... }else { msg = `certManager.genP10 error, code:${result.code}, message: ${result.msg}`; } 

# 3.3.6.2 导入证书 

# 证书申请成功后,调用 certManager.importCert() 方法将服务端申请 好的证书导入到密码模块中。 

# 方法定义: 

/** * 导入证书 * * @param cert 证书数据 * @param doubleCert 加 密证书 * @param doubleEncryptedPrivateKey 加密私钥 * @param sessionKeyAlg 保护私钥对称算法 * @param doubleEncSessionKey 加密对称密钥 */ public async importCert(cert: string, doubleCert: 

string, doubleEncryptedPrivateKey: string, sessionKeyAlg: number, doubleEncSessionKey: string): Promise<Result> { } 

# 示例: 

// todo 请求服务端申请证书 // 导入证书 result = await certManager.importCert(cert, doubleCert, encryptKey, sessionKeyAlg, encryptSessionKey); if 

(EtdsConstantsEnum.SUCCESS == result.code) { msg = ' 导入证书 成功 '; } else { msg = ` 导入证书失败: code:${result.code}, message: ${result.msg}`; } this.saveLog(msg); // 关闭会话 certManager.closeSession(); 

3.3.7 吊销证书 

# 方法定义: 

/** * 删除证书 * * @param certCfg 证书相关密码学算法设置 * @param pinConfig PIN 相关配置 * @param callBack 结果回调 */ public void deleteCert(CertConfig certCfg, PinConfig pinConfig, Callback callBack) { } 

# 示例: 

// 实例化 CertManager let certManager = new CertManager(); // 打 开会话 let openSessionResult = await certManager.openSession(alias); Logger.info(TAG, 

```arkts
"openSessionResult: " + openSessionResult.toString()); // 创建实现 网络接口的具体类的实例 const requestMsgHandler = new RequestMsgHandler(); // 设置网络请求实现 requestMsgProcessor certManager.setRequestMsgProcessor(requestMsgHandler); let certCfg: CertConfig = new CertConfig(); // 证书别名 certCfg.alias = alias; let pinCfg: PinConfig = new PinConfig(); // PIN 码 pinCfg.pin = pin; // 删除证书 let result = await 
```

certManager.deleteCert(certCfg, pinCfg); this.saveLog(`deleteCert: code:${result.code}, message:${result.msg}`); if (EtdsConstantsEnum.SUCCESS == result.code) { } // 关闭会话 certManager.closeSession(); 

3.3.9 签名 

# 使用私钥对待签名数据进行签名。 

# 方法定义: 

/** * 证书签名 * * @param alias 证书别名 * @param plainData 待 签名数据字节数组 * @param signType 签名类型 取 SignTypeEnum 中 的值 * @param signAlgorithm 签名算法 取 SignAlgorithmEnum 中的 值 * @param pinCfg PIN 相关配置,软盾时需要设置输入的 pin */ public async sign(alias: string, plainData: Uint8Array, signType: number, signAlgorithm: number, pinCfg: PinConfig): Promise<Result> { } 

# 示例: 

// 实例化 CertManager let certManager = new CertManager(); // 打 开会话 let openSessionResult = await certManager.openSession(alias); Logger.info(TAG, 

```arkts
"openSessionResult: " + openSessionResult.toString()); // 创建实现 网络接口的具体类的实例 const requestMsgHandler = new RequestMsgHandler(); // 设置网络请求实现 requestMsgProcessor certManager.setRequestMsgProcessor(requestMsgHandler); let pinCfg: PinConfig = new PinConfig(); // PIN 码 pinCfg.pin = pin; // 待签名数据 let plainData: Uint8Array = StringUtil.stringToUint8Array(plainDataStr); // 签名类型,取 SignTypeEnum 的值, P1 、 P7 let signType: number = SignTypeEnum.PKCS1; // 签名算法,取 SignAlgorithmEnum 中的值 let signAlgorithm: number = SignAlgorithmEnum.SM3WITHSM2; // 签名 let result = await certManager.sign(alias, plainData, signType, signAlgorithm, pinCfg); if (EtdsConstantsEnum.SUCCESS == result.code) { // 签名成功,获取签名结果 this.p1SignData = result.msg; } else { // 签名失败 // 获取重试次数 let msg = ` 还可以 重试 : ${result.retryNum} 次 `; } // 关闭会话 certManager.closeSession(); 
```

# 3.3.10 绑定生物认证 

# 方法定义: 

/** 绑定生物认证 * @param alias 证书别名,调用方需保证其唯一 

性。 * @param reasonTitle 指纹认证弹框页面 title 。 * @param fallbackTitle 只有在认证流程中的指纹认证弹框页面,在错误一次的 后显示出的可选项按钮标题 * @param authType 绑定的生物认证类 型 * @param pinCfg 软盾场合适用。硬盾场合为 null * @param callback 绑定生物认证结果回调,当 etdsResult.code 为 ETDS_SUCCESS 时,绑定生物认证成功 , 否则绑定生物认证失败。 */ public void bindBio(String alias, String reasonTitle, String fallbackTitle, int authType, final PinConfig pinCfg, Callback callback) { } 

# 示例: 

// 实例化 CertManager let certManager = new CertManager(); // 打 开会话 let openSessionResult = await certManager.openSession(alias); Logger.info(TAG, 

```arkts
"openSessionResult: " + openSessionResult.toString()); // 创建实现 网络接口的具体类的实例 const requestMsgHandler = new RequestMsgHandler(); // 设置网络请求实现 requestMsgProcessor certManager.setRequestMsgProcessor(requestMsgHandler); // 指纹 认证弹框页面 title let reasonTitle: string = "reasonTitle"; // 只有在 认证流程中的指纹认证弹框页面,在错误一次的后显示出的可选项按 钮标题 let fallbackTitle: string = ""; // 认证类型 let authType: number = 1; let pinCfg: PinConfig = new PinConfig(); // PIN 码 pinCfg.pin = pin; // 绑定 IFAA 生物认证 let result = await certManager.bindBio(alias, reasonTitle, fallbackTitle, authType, pinCfg); this.saveLog(` 绑定生物认证结果 : code:${result.code}, message:${result.msg}`); // 关闭会话 certManager.closeSession(); 
```

# 3.3.11 解绑生物认证 

# 方法定义: 

/** * 解绑生物认证 * @param alias 证书别名,调用方需保证其唯一 性 * @param authType 绑定的生物认证类型 * @returns */ public async unbindBio(alias: string, authType: number): Promise<Result> { } 

# 示例: 

// 实例化 CertManager let certManager = new CertManager(); // 打 

开会话 let openSessionResult = await certManager.openSession(alias); Logger.info(TAG, 

```arkts
"openSessionResult: " + openSessionResult.toString()); // 创建实现 网络接口的具体类的实例 const requestMsgHandler = new RequestMsgHandler(); // 设置网络请求实现 requestMsgProcessor certManager.setRequestMsgProcessor(requestMsgHandler); // 认证 类型 let authType: number = 1; // 解绑 IFAA 生物认证 let result = await certManager.unbindBio(alias, authType); // 关闭会话 certManager.closeSession(); this.saveLog(` 解绑生物认证结果 : code: ${result.code}, message:${result.msg}`); 
```

# 3.3.12 生物认证签名 

# 方法定义: 

/** * 生物认证进行签名 * @param alias 证书别名,调用方需保证其 唯一性 * @param plainData 待签名数据字节数组 * @param signType 签名类型 取 SignTypeEnum 中值 * @param signAlgorithm 签名算法 * @param reasonTitle 指纹弹框上的提示文字 * @param fallbackTitle 指纹弹框上【取消】的文字 * @param authType 绑定 的生物认证类型 * @returns */ public async bioSign(alias: string, plainData: Uint8Array, signType: number, signAlgorith m: number, reasonTitle: string, fallbackTitle: string, authType: number): Promise<Result> { } 

# 示例: 

// 实例化 CertManager let certManager = new CertManager(); // 打 开会话 let openSessionResult = await certManager.openSession(alias); Logger.info(TAG, 

```arkts
"openSessionResult: " + openSessionResult.toString()); // 创建实现 网络接口的具体类的实例 const requestMsgHandler = new RequestMsgHandler(); // 设置网络请求实现 requestMsgProcessor certManager.setRequestMsgProcessor(requestMsgHandler); // 待签 名数据 let plainData: Uint8Array = StringUtil.stringToUint8Array(plainDataStr); // 签名类型,取 SignTypeEnum 的值, P1 、 P7 let signType: number = SignTypeEnum.PKCS1; // 签名算法,取 SignAlgorithmEnum 中的值 let signAlgorithm: number = SignAlgorithmEnum.SM3WITHSM2; // 指纹认证弹框页面 title let reasonTitle: string = "reasonTitle"; // 
```

只有在认证流程中的指纹认证弹框页面,在错误一次的后显示出的可 选项按钮标题 let fallbackTitle: string = " 密码认证 "; // 认证类型 let authType: number = 1; // 生物认证签名 let result = await certManager.bioSign(alias, plainData, signType, signAlgorithm, reasonTitle, fallbackTitle, authType); this.saveLog(` 生物认证签名结 果 : code:${result.code}, message:${result.msg}`); if (EtdsConstantsEnum.SUCCESS == result.code) { // 签名后的数据 this.p1SignData = result.msg; } // 关闭会话 certManager.closeSession(); 

# 3.3.13 生物认证更新 

当 certManager.bioSign 的 etdsResult.code 为 

ETDS_WRONG_AUTHDATAINDEX (需要进行生物认证更新)的 code 时,可调用该方法实现生物认证更新。 

# 方法定义: 

/** * 更新生物认证 * @param alias 证书别名,调用方需保证其唯一 性 * @param pinCfg 软盾场合适用。硬盾场合为 null * @param updateMsg 生物认证更新所需要的更新信息,当 certManager.bioSign 的 etdsResult.code 为 ETDS_WRONG_AUTHDATAINDEX 需要进行生 物认证更新的 code 时, etdsResult.msg 即为 updateMsg * @param authType 绑定的生物认证类型 * @returns */ public async updateBio(alias: string, pinConfig: PinConfig, updateMsg: string, authType: number): Promise<Result> { } 

# 示例: 

// 实例化 CertManager let certManager = new CertManager(); // 打 开会话 let openSessionResult = await certManager.openSession(alias); Logger.info(TAG, 

```arkts
"openSessionResult: " + openSessionResult.toString()); // 创建实现 网络接口的具体类的实例 const requestMsgHandler = new RequestMsgHandler(); // 设置网络请求实现 requestMsgProcessor certManager.setRequestMsgProcessor(requestMsgHandler); let pinCfg: PinConfig = new PinConfig(); // 设置 PIN pinCfg.pin = pin; // 更新生物认证 let result = await certManager.updateBio(alias, pinCfg, updateMsg, authType); // 关闭会话 await certManager.closeSession(); this.saveLog(` 更新生物认证结果 : code: ${result.code}, message:${result.msg}`); this.saveLog("------- 更新生 
```

物认证结束 -----"); // 更新生物认证成功后,调用生物认证进行签名 if (EtdsConstantsEnum.SUCCESS == result.code) { this.bioSign() } 

# 3.3.15 私钥解密 

# 服务端使用对应的公钥做加密得到加密数据,调用 SDK 的解密方法对 加密后数据进行解密得到原数据。 

# 方法定义: 

/** * 证书解密 * @param alias 证书别名 * @param pinCfg PIN 相关 配置 * @param encryptData 加密后的数据 * @returns */ public async decrypt(alias: string, pinCfg: PinConfig, encryptData: string): Promise<Result> { } 

# 示例: 

// 实例化 CertManager let certManager = new CertManager(); // 打 开会话 let openSessionResult = await certManager.openSession(alias); Logger.info(TAG, 

```arkts
"openSessionResult: " + openSessionResult.toString()); // 创建实现 网络接口的具体类的实例 const requestMsgHandler = new RequestMsgHandler(); // 设置网络请求实现 requestMsgProcessor certManager.setRequestMsgProcessor(requestMsgHandler); let result = await certManager.export Cert(); if (EtdsConstantsEnum.SUCCESS != result.code) { this.saveLog("verify error: 请先申请证书 "); } let certs: ArrayList<CertEntry> = result.cert; let cert: CertEntry = certs[1]; if (cert == null || cert == undefined) { this.saveLog("verify error: 请先申请加密证书 "); } let serialNumber = cert.serialNumber; let dataEncrypt = new DataEncrypt(); dataEncrypt.serialNumber = serialNumber.toString(); let dataEncryptJson = JSON.stringify(dataEncrypt); let url = baseUrl + "/data/encrypt"; let res = await HttpUtils.request(url, dataEncryptJson); let dataEncryptResponse = JSON.parse(res) as DataEncryptResponse; if ("0000" != dataEncryptResponse.code) { this.saveLog(" 请求服务端异常: " + dataEncryptResponse.msg); return; } // 服务端使用加密证书加密后的数据 let encryptData = dataEncryptResponse.encryptData; let pinCfg: PinConfig = new PinConfig(); // 设置 PIN pinCfg.pin = pin; // 解密 result = await certManager.decrypt(alias, pinCfg, encryptData); if 
```

(EtdsConstantsEnum.SUCCESS == result.code) { // 解密后的数据 

this.saveLog(" 解密结果 : " + result.msg); } else { this.saveLog(`decrypt: code:${result.code}, message:${result.msg} `); } // 关闭会话 certManager.closeSession(); 

# 3.3.16 解锁 PIN 

当 PIN 码多次输入错误之后,调用此接口进行解锁 PIN ,调用该接口前 请 APP 端进行身份认证。 

# 方法定义: 

/** * 解锁 PIN * @param alias 证书别名,调用方需保证其唯一性 * @param pinCfg PIN 相关配置 * @returns */ public async unblockPin(alias: string, pinCfg: PinConfig): Promise<Result> { } 

# 示例: 

// 实例化 CertManager let certManager = new CertManager(); // 打 开会话 let openSessionResult = await certManager.openSession(alias); Logger.info(TAG, 

```arkts
"openSessionResult: " + openSessionResult.toString()); // 创建实现 网络接口的具体类的实例 const requestMsgHandler = new RequestMsgHandler(); // 设置网络请求实现 requestMsgProcessor certManager.setRequestMsgProcessor(requestMsgHandler); let pinCfg: PinConfig = new PinConfig(); // 设置 PIN pinCfg.pin = pin; // 解锁 PIN let result = await certManager.unblockPin(alias, pinCfg); // 关闭会话 certManager.closeSession(); 
```

# 3.4 访问控制 

# 3.4.1 基本逻辑 

eTDS 根据终端种类不同,支持以下两种手机盾: 

硬盾:利用终端上的 TEE/SE 安全设施,实现手机盾的逻辑。此时, PIN 管理逻辑是 eTDS 利用 TUI (运行在 TEE 中的可信 UI )来实现的。 软盾:协同密钥软盾中需要 APP 来实现安全键盘。 

# 3.4.2 修改 PIN 

调用 CertManager.changePin 方法将本地证书的 PIN 码进行: 

# 方法定义: 

/** * 修改 PIN * * @param alias 证书别名,调用方需保证其唯一 性。 * @param pinCfg 软盾场合适用。硬盾场合为 null */ public async changePin(alias: string, pinCfg: PinConfig): Promise<Result> { } 

# 示例: 

// 实例化 CertManager let certManager = new CertManager(); // 打 开会话 let openSessionResult = await certManager.openSession(alias); Logger.info(TAG, 

```arkts
"openSessionResult: " + openSessionResult.toString()); // 创建实现 网络接口的具体类的实例 const requestMsgHandler = new RequestMsgHandler(); // 设置网络请求实现 requestMsgProcessor certManager.setRequestMsgProcessor(requestMsgHandler); let pinCfg: PinConfig = new PinConfig(); // 设置旧 PIN pinCfg.oldPin = oldPin; // 设置修改后的 PIN pinCfg.pin = newPin; // 修改 PIN 码 let result = await certManager.changePin(alias, pinCfg); this.saveLog(`changePin: code:${result.code}, message: ${result.msg}`); if (EtdsConstantsEnum.SUCCESS == result.code) { } // 关闭会话 certManager.closeSession(); 
```

3.4.4 TUI 设置 

PIN 码输入采用了安全 TUI ,在 PIN 设置、 PIN 认证、 PIN 修改、 PIN 签 名信息确认中都会自动调起 TUI ,如图所示: 

SDK 中提供 SecureTuiConfig 作为安全页面 TUI 的配置类,该类中的 属性有: 

/** * @describe 安全页面 TUI 的配置类 */ public class SecureTuiConfig { /** * logo */ private String logoImgName = "etds_logo.png"; private int logoWidth = 100; private int logoHeight = 100; private int logoOffsetY = 80; /** * 键盘输入框 了类型: * NUMERICAL(0), * ALPHANUMERICAL(1); */ private SecureEditText.InputType inputType = SecureEditText.InputType.NUMERICAL; /** * 输入密码标签 */ private String padLabelText = " 请输入密码 (6~8 个数字 )"; /** * 确 定密码标签 */ private String raptPadLabelText = " 再次输入密码 

(6~8 个数字 )"; /** * 修改 PIN 码页面输入新密码 */ private String newPadLabelText = " 输入新密码 (6~8 个数字 )"; /** * 确定按钮 */ private String confirmBtnText = " 确定 "; /** * 取消按钮 */ private String cancelBtnText = ""; /** * 提示信息 */ private String promptText = ""; private int promptTextColor = 0xFF000000; private int promptOffsetY = 200; } 

字段详细说明: 

字段 

说明 

类型 

logoImgName 

TUI 上展示 Logo 的文件名称,该文件需放在 access/etds 目录下 

String 

logoWidth 

TUI 上展示 Logo 的宽度,单位 dp 

int 

logoHeight 

TUI 上展示 Logo 的高度,单位 dp 

int 

logoOffsetY 

TUI 上展示 Logo 的垂直方向的距离,单位 dp 

int 

inputType 

TUI 上展示键盘的类型 

SecureEditText.InputType : 

NUMERICAL(0), 

ALPHANUMERICAL(1); 

padLabelText 

TUI 上展示输入密码标签文字 

String 

raptPadLabelText 

TUI 上展示确定密码标签文字 

String 

newPadLabelText 

TUI 上展示修改 PIN 码页面输入新密码标签文字 

String 

confirmBtnText 

TUI 上展示确定按钮文字 

String 

cancelBtnText 

TUI 上展示取消按钮文字 

String 

promptText 

TUI 上展示确认信息文字 

String 

promptTextColor 

# TUI 上展示确认信息文字颜色 

int 

promptOffsetY 

# TUI 上展示确认信息垂直方向的距离,单位 dp 

int 

SecureTuiConfig 的使用示例: 

// 安全页面设置 SecureTuiConfig secureTuiConfig = new SecureTuiConfig(); secureTuiConfig.setPromptText(mPrompt); secureTuiConfig.setCancelBtnText(" 取消 "); certManager.setSecureTuiConfig(secureTuiConfig); 

3.5 错误码 

EtdsConstantsEnum 中的 code 

常量名 

值( String ) 

描述 

SUCCESS 

0 

成功 

CLIENT_ERROR 

1 

客户端错误 

SERVER_ERROR 

2 

# 服务端错误 

NETWORK_ERROR 

3 

# 网络错误 

CERT_NOT_EXIST 4 本地证书不存在 USER_CANCEL 5 用户取消 

PIN_TOO_SHORT 6 输入密码过短 

PIN_INCONSISTENT 

7 两次密码不匹配 

AUTH_FAILED 

8 密码认证失败 

AUTH_LOCK 

9 错误次数太多,认证被锁定 

# AUTH_TIME_OUT 

10 

认证超时 

DEVICE_IS_ROOT 

11 

设备被 Root 

ETDS_AUTH_WEAK_PWD 

12 

密码过于简单 

ETDS_AUTH_SIMILAR_PWD 

13 

与关联密码相似 

ETDS_TUI_ERROR 

14 

TUI 错误 

ETDS_WRONG_AUTHDATAINDEX 

15 

指位 / 人脸不匹配,需要更新指位 / 人脸 

ETDS_WRONG_LICENSE 

16 

无效的授权文件 

ETDS_LICENSE_OVERDUE 

17 

授权文件过期 

ETDS_UNSUPPORTED_ALG 

18 

不支持的算法 

ETDS_SIGN_FAILED 19 

签名失败 

ETDS_VERIFY_FAILED 

20 

验签失败 

ETDS_ENCRYPT_FAILED 21 

加密失败 

ETDS_DECRYPT_FAILED 

22 

解密失败 

ETDS_APP_INACTIVATE 

23 

应用未激活 

ETDS_BAD_CERT 

24 

# 证书格式错误 

ETDS_NOT_SUPPORT_CERT 

25 

不支持的证书 

ETDS_CERT_NOT_FOUND 

26 

证书不存在 

ETDS_CERT_EXPIRED 

27 

证书过期 

ETDS_PIN_SAME 

28 

修改后的 PIN 与当前 PIN 相同 

ETDS_TA_UPDATE 

29 

TA 需要更新 

生物认证相关接口中的错误码 

ETDS_STATUS_PASSCODE_NOT_SET 

100 

尚未设置屏幕锁密码 ( IFAA 需要设置屏幕锁后才能进行,此处可引 导用户去设置屏幕锁) 

IFAA_STATUS_NOT_SUPPORT 

101 

# 终端不支持 IFAA 

IFAA_STATUS_FINGERPRINT 

102 

终端支持 IFAA 的指纹服务( Touch ID ) 

IFAA_STATUS_FACE_ID 

103 

终端支持 IFAA 的人脸服务( Face ID ) 

IFAA_STATUS_NOT_ENROLLED 

104 

终端没有录入指纹 / 人脸 ( 此时可以引导用户去录入指纹 / 人脸再做操 作 ) 

IFAA_STATUS_NOT_REGISTERED 

105 

IFAA 尚未注册 ( 比如认证 / 注销 / 指位更新等操作都需要注册后才可以 进行 ) 

IFAA_STATUS_REGISTERED 

106 

IFAA 已经注册 ( 这只是一个状态,并不是错误 ) 

IFAA_STATUS_PASSCODE_NOT_SET 

107 

尚未设置屏幕锁密码 ( IFAA 需要设置屏幕锁后才能进行,否则不安 全,此处可引导用户去设置屏幕锁) 

# IFAA_CLIENT_ERROR 

108 

本地执行异常 

IFAA_SERVER_ERROR 

109 

服务器错误 

IFAA_NETWORK_ERROR 

110 

网络错误 

IFAA_WRONG_AUTHDATAINDEX 

111 

指位不匹配,需要更新指位 

IFAA_POLICY_REJECTED 

112 

被风险策略拒绝时 

IFAA_USER_REJECTED 

113 

用户被禁用时 

IFAA_APPID_NOT_FOUNDAPPID_NOT_FOUND 

114 

应用白名单中未设置 

IFAA_DEVICE_MODEL_NOT_FOUND 

115 

设备型号不存在 

IFAA_ERR_SIGNATURE_FAIL 

116 

未获取到签名数据 

IFAA_STATUS_DELETED 

117 

本地指纹已经注册,但是注册的指纹模组数据已经被删除 

IFAA_CLIENT_ERROR_MULTI_FP_NOT_SUPPORT 

118 

此手机不支持多指位 

IFAA_STATUS_RESULT_CANCELED 

119 

用户取消 

IFAA_STATUS_RESULT_TIMEOUT 

120 

超时 (Android 独有 ) 

IFAA_STATUS_RESULT_AUTH_FAIL 

121 

验证失败,系统指纹不匹配 

IFAA_STATUS_RESULT_SYSTEM_BLOCK 

122 

# 连续多次校验失败,指纹校验被暂时锁定 ( 暂时 Android 独有 ) 

IFAA_STATUS_RESULT_FALLBACK 

123 

点击了 FALLBACK 按钮 

IFAA_STATUS_RESULT_TEE_ERROR 

124 

TEE 错误 (Android 独有 ) 

IFAA_STATUS_RESULT_SYSTEM_ERROR 

125 

手机系统问题,请升级系统版本 (Android 独有 ) 

IFAA_PERMISSION_DENIED 

126 

-Android: 当前设备未获取相机权限 

-IOS: 当前应用未获取 Face ID 权限 

IFAA_AUTHENTICATOR_DISABLE 

127 

认证器被禁用 

IFAA_AUTHENTICATOR_NOT_FOUND 

128 

未找到相应的认证器 

IFAA_DEVICE_KEY_NOT_FOUND 

129 

# 设备密钥被禁用 

IFAA_PROTECT_PAYLOAD_NOT_MATCH 

130 

# 受保护的业务数据不匹配
