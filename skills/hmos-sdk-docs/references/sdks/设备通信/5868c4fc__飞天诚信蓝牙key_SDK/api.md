蓝牙 key 鸿蒙 SDK 

接入文档 

# 飞天诚信科技股份有限公司 

网址: www.FTsafe.com 

版权所有 © 2009 北京飞天诚信科技有限公司 

地址:北京市海淀区学院路 40 号研 7A 楼 5 层 100191 

电话: (8610)62304466 传真: (8610)62304477 网址: www.FTsafe.com.cn 

SDK 修订记录: 

# 修订日期 

版本 

修订内容 2025 年 10 月 V1.1.0 第一版发布 

目录 

第 1 章 SDK 详解 3 

1.1 SDK 文件说明 3 

1.2 SDK 使用配置 3 

1.3 接口定义 4 

第 2 章 API 功能介绍 15 

2.1 初始化 15 

2.2 析构 15 

2.3 获取 SDK 版本 15 

2.4 连接蓝牙 Key 16 

2.5 断开蓝牙 key 16 

2.6 取消连接蓝牙 key 17 

2.7 开始扫描蓝牙 key 17 

2.8 停止扫描蓝牙 key 17 

2.9 获取设备序列号 18 

2.10 判断是否初始密码 18 

2.11 获取密码重试次数 18 

2.12 枚举证书 19 

2.13 读取证书 19 

2.14 验证密码 19 

2.15 修改密码 20 

2.16 签名 20 

2.17 初始化 Key 21 

2.18 生成密钥并产生 P10 22 

2.19 导入密钥对 22 

2.20 导入证书 22 

2.21 验 PIN 导入密钥对 23 第 3 章 API 返回码解释 23 

# 第 1 章 SDK 详解 

SDK For Harmony 是飞天诚信科技股份有限公司开发的,基于鸿蒙平 台的,针对飞天诚信蓝牙 Key 整合的一个开发工具包。 

# 1.1 SDK 文件说明 

将我们提供的压缩包解压之后,您将可以看见以下文件夹: 

doc : 

该文件夹下的内容是开发参考手册。 

lib : 

该文件夹下的内容是开发库文件。 

sample : 

该文件夹下的内容是使用本 SDK 的 Harmony 示例工程和示例程序安装 hap 。 

# 1.2 SDK 使用配置 

(1) 将 lib 目录下的 ftkeylib.har 拷贝至应用开发工程对应 entry 的 libs 目 录 ( 无此目录,请新建文件夹 ) 中 

(2) 在 entry 模块的 oh-package.json5 文件内,配置 dependencies 节 点,添加库使用依赖,如: 

"dependencies": { 

"ftkeylib": "file:./libs/ftkeylib.har" 

} 

注意 oh-package.json5 中依赖包使用的别名,必须与依赖包的 ohpackage.json5 中的 name 一致。更换 har 后,需要删除工程模块 on_modules 下的依赖库,再同步工程,重新加载依赖。 

(3) 配置 entry 模块的 module.json5 文件,加入相应的蓝牙权限并申 请: 

"requestPermissions": [{ 

"name": 'ohos.permission.ACCESS_BLUETOOTH', 

"reason": '$string:permission_reason_access_bluetooth', 

"usedScene": { 

"when": "inuse" 

} 

}] 

(4) Har 包为字节码格式,字节码 HAR 被集成使用时,那么该工程的 build-profile.json5 中的 useNormalizedOHMUrl 必须设置为 true 。且 compatibleSdkVersion 要求为 API12 。 

"products": [ { "compatibleSdkVersion": "5.0.0(12)", "buildOption": { "strictMode": { "useNormalizedOHMUrl": true } } } ], 

# 1.3 接口定义 

export namespace FTKey { 

// 用戶证书类型 export enum FTUserCertType { FTO_CERTTYPE_ALL, FTO_CERTTYPE_RSA1024_PLAIN, // RSA1024 普通证书 只支持加解密 FTO_CERTTYPE_RSA1024_REEXAMINE, // RSA1024 复核证书 只支持签名验签 FTO_CERTTYPE_RSA1024_MIX, // RSA1024 混合证书 支持加解密,签名验签 FTO_CERTTYPE_RSA2048_PLAIN, // RSA2048 普通证书 只支持加解 密 FTO_CERTTYPE_RSA2048_REEXAMINE, // RSA2048 复核证书 只 支持签名验签 FTO_CERTTYPE_RSA2048_MIX, // RSA2048 混合证书 支持加解密,签名验签 FTO_CERTTYPE_SM2_PLAIN, // SM2 普通证 书 只支持加解密 FTO_CERTTYPE_SM2_REEXAMINE, // SM2 复核证 书 只支持签名验签 FTO_CERTTYPE_SM2_MIX, // SM2 混合证书 支持 加解密,签名验签 } // 用戶签名算法 export enum FTUserSignAlg { FTM_RSA_MD5, FTM_RSA_SHA1, FTM_RSA_SHA256, 

FTM_RSA_SHA384, FTM_RSA_SHA512, FTM_SM2 } // 用户获取的签 名结果 export enum FTSignResultType { FT_HEXSTR, // 签名结果为 16 进制字符串格式 FT_BASE64, // 签名结果为 base64 格式 FT_P7, // 签名结果为 P7 格式的 base64 数据 } // 用戶证书信息 export class FTUserCertInfo { constructor(time: string, issuerDN: string, subjectDN: string, sn: 

string, certType: number) { this.time = time; this.issuerDN = issuerDN; this.subjectDN = subjectDN; this.sn = sn; this.certType 

= certType; } time: string; // 证书有效期:格式为 4 位年 2 位月 2 位日 4 位年 2 位月 2 位日 issuerDN: string; // 证书颁发者 DN 数据 subjectDN: string; // 证书持有者 DN 数据 sn: string; // 证书序列号 certType: number; // 证书类型 } // 下载证书参数 export class FTCertParam { constructor(dn: string, hashAlg: number, keyType: number, certType: number) { this.dn = dn; this.hashAlg = hashAlg; this.keyType = keyType; this.certType = certType; } dn: string; // 证书持有者 DN 数据 hashAlg: number; // 签名算法, {0:MD5, 1:SHA1, 2:SHA256, 3:SHA384, 4:SHA512, 5:SM3} keyType: number // 密钥类型, {1:RSA1024, 2:RSA2048, 3:SM2} certType: number; // 证书类型, {1: 普通证书 , 2: 复核证书 , 3: 普通 + 复核双证 , 4: 混合证 书 } } // 公钥数据 +P10 数据 export class FTCertPKCS10 extends FTCertParam { constructor(certParam: FTCertParam, pubKey: Array<Uint8Array>, pkcs10: string) { 

super(certParam.dn, certParam.hashAlg, certParam.keyType, certParam.certType); this.pubKey = pubKey; this.pkcs10 = pkcs10; } pubKey: Array<Uint8Array>; //keyType 为双证类型时, 2 组公 钥,第一个为签名公钥,第二个为加解密公钥,其他类型为 1 组公钥 pkcs10: string; //base64 格式的 P10 结果 } // 用户错误码定义 export enum FTUserErrCode { FT_SUCCESS, FT_OPERATION_FAILED, FT_NO_DEVICE, FT_ENERGY_LOW, FT_DEVICE_BUSY, FT_INVALID_PARAMETER, FT_USER_CANCEL, 

FT_OPERATION_TIMEOUT, FT_SN_NOTMATCH, FT_NO_CERT, FT_CERT_INVALID, FT_CERT_EXPIRED, 

FT_CERT_NOT_FROM_FUTURE, FT_CERT_NOTMATCH, 

FT_SIGN_MESSAGE_ERROR, FT_SIGN_ALG_ERROR, FT_PIN_LOCK, FT_SAME_PASSWORD, FT_PASSWORD_INVALID_LENGTH, 

FT_PASSWORD_TOO_SIMPLE, FT_PASSWORD_INVALID, 

FT_PASSWORD_WRONG, FT_DEFAULT_PIN, FT_COMM_ERROR, FT_COMM_TIMEOUT, 

FT_OTHER_ERROR, FT_BLE_PLATFORM_NOT_SUPPORT_BLE, FT_PHONE_BT_CLOSE, FT_BLE_APP_NOT_BLE_AUTHORIZE, 

FT_BLE_CANCEL_CONNECT_DEVICE, FT_BLE_CONNECT_TIMEOUT, FT_NOT_DEFAULT_PIN = 100, FT_BT_CONNECT_SUCCESS, 

FT_BT_DISCONNECT, } export interface FTKeyError extends Error { code: number; // 错误码 } /** * 函数执行结果回调函数 * * @param { FTKeyError } error - 错误码,函数执行的错误信息,代表意义详见 FTUserErrCode. * @param { any } data - 数据,函数执行成功后, 返回执行完成获取的数据 . * @param { number } extra - 密码剩余重 试次数,存在验证密码或获取密码剩余重试次数操作时,返回该值 . 

*/ export type ResultCallback<T> = (error: FTKeyError, data: T, extra?: number) => void; /** * 函数执行 UI 按键提示回调函数 * * @param { number } type - 提示类型 . * @param { string } prompt - 提示语 . * 具体提示类型和提示语如下: * type = 0, prompt = ' 关闭 按键提示 ' // 关闭按键提示响应回调 * type = 1, prompt = ' 验证密码 (您还有 ' + retryPinTimes + ' 次重试机会),请按键确认 ...' // 验证 密码剩余次数 <=2 次时,按键提示响应回调 

* type = 2, prompt = ' 修改密码(您还有 ' + retryPinTimes + ' 次重 试机会),请按键确认 ...' // 修改密码时,按键提示响应回调 * type = 5, prompt = ' 请核对 UKey 屏幕上显示的内容是否正确,如确认请 按 “OK” 键,否则按 “C” 键取消 ' // 签名时,按键提示响应回调 * type = 6, prompt = ' 请再次按键确认 ...' // 需要两次确认按键时,按键提 示响应回调 * type = 7, prompt = ' 请在 UKey 上按键确认 ...' // 初始 化或其他需要按键操作时,按键提示响应回调 */ export type 

```arkts
UiCallback = (type: number, prompt: string) => void; export interface FTKey { /** * 获取 SDK 版本号 * * @return s { string } 版本 号信息 . */ getLibVersion(): string; /** * SDK 初始化函数,在使用 SDK 库时调用 . * * @param { Context | undefined } context - UIAbility 上下文 . * @param { ResultCallback } callback - 函数执行 结果回调函数,错误码代表执行结果 . */ initialize(context: Context | undefined, callback: ResultCallback<void>): void; /** * SDK 析构 函数,在该接口中释放 SDK 必要的资源 */ safeFinalize(): void; /** * 连接蓝牙 KEY * * @param { string } sn - 待连接蓝牙 KEY 的序列号或 蓝牙名称 . 
```

* @param { number } timeout - 连接超时时间,单位秒 . * @param { ResultCallback } callback - 函数执行结果回调函数,错误码代表执行 结果 , * 当错误码为成功时,代表连接成功,错误码为蓝牙断开连接 时,代表断开连接,其他错误参考错误码定义 */ connectKey(sn: string, timeout: number, callback: ResultCallback<void>): void; / ** * 断开蓝牙 KEY 的连接 */ disconnectKey(): void; /** * 取消蓝牙 KEY 的连接 */ cancelConnectKey(): void; /** * 开始扫描蓝牙 KEY * * @param { ResultCallback } callback - 函数执行结果回调函数,错误 码代表执行结果 , * 扫描成功时,持续响应回调函数,数据返回扫描 到的蓝牙 KEY 名称 . */ startScanKey(callback: ResultCallback<string>): void; /** * 停止扫描蓝牙 KEY */ stopScanKey(): void; /** * 获取设备序列号 * * @param { ResultCallback } callback - 函数执行结果回调函数,错误码代表执行 结果 , 

- 当错误码为成功时,数据返回设备序列号 . */ getSN(callback: 

- ResultCallback<string>): void; /** * 检查设备是否初始密码 * * 

@param { ResultCallback } callback - 函数执行结果回调函数,错误 码代表执行结果 , * 当错误码为设备是初始密码或设备不是初始密码 时,代表接口执行成功,其他错误参考错误码定义 */ 

```arkts
isDefaultPin(callback: ResultCallback<void>): void; /** * 获取设 备密码剩余重试次数 . * * @param { ResultCallback } callback - 函数 执行结果回调函数,错误码代表执行结果 , * 当错误码为成功时,回 调响应包含密码剩余重试次数 . */ getPINRemainTimes(callback: ResultCallback<void>): void; /** * 获取设备的所有证书 * * @param { ResultCallback } callback - 函数执行结果回调函数,错误 码代表执行结果 , * 当错误码为成功时,数据返回设备内的所有证书 . 
```

*/ enumCert(callback: 

```arkts
ResultCallback<Array<FTUserCertInfo>>): void; /** * 获取指定 的证书数据 * * @param { FTUserCertInfo } cert - 指定的证书对象 . * @param { ResultCallback } callback - 函数执行结果回调函数,错误 码代表执行结果 , 
```

* 当错误码为成功时,数据返回指定证书的 base64 格式的证书数据 . 

*/ getCert(cert: FTUserCertInfo, callback: ResultCallback<string>): void; /** * 验证设备密码 . * * @param { string } pin - 设备的密码 . * @param { ResultCallback } callback - 函数执行结果回调函数,错误 码代表执行结果 , * 回调响应包含密码剩余重试次数 . * @param { UiCallback } ui - ui 回调函数,等待按键确认时响应 . */ 

```arkts
verifyPin(pin: string, callback: ResultCallback<void>, ui?: UiCallback): void; /** * 修改设备密码 . * * @param { string } oldPin - 设备的旧密码 . * @param { string } newPin - 设备的新密码 . * @param { ResultCallback } callback - 函数执行结果回调函数,错误 码代表执行结果 , * 回调响应包含密码剩余重试次数 . * @param { UiCallback } ui - ui 回调函数,等待按键确认时响应 . */ changePin(oldPin: string, newPin: string, callback: ResultCallback<void>, ui?: UiCallback): void; /** * 签名 * * 
```

@param { string } pin - 设备的密码 . * @param { FTUserCertInfo } cert - 指定的证书对象 . * @param { FTUserSignAlgo } hash - 签名算 法 . * @param { string } plain - 待签名原文 . * @param { FTSignResultType } type - 指定返回的签名结果格式 . 

* @param { ResultCallback } callback - 函数执行结果回调函数,错 误码代表执行结果 , * 当错误码为成功时,数据返回指定格式的签名 结果,回调响应包含密码剩余重试次数 . * @param { UiCallback } ui 

- ui 回调函数,等待按键确认时响应 . */ sign(pin: string, cert: FTUserCertInfo, hash: FTUserSignAlg, plain: string, type: 

```arkts
FTSignResultType, callback: ResultCallback<string>, ui?: UiCallback): void; /** * 初始化设备 * * @param { string } pin - 指 
```

定设备初始化后的默认密码 . * @param { ResultCallback } callback - 函数执行结果回调函数,错误码代表执行结果 . * @param { UiCallback } ui - ui 回调函数,等待按键确认时响应 . */ initKey(pin: string, callback: ResultCallback<void>, ui?: UiCallback): void; /** * 生成密钥对,并产生 P10 数据 * * @param { string } pin - 设备的密 码 . * @param { Array<FTCertParam> } certParams - 请求生成证 书的参数 . * @param { ResultCallback } callback - 函数执行结果回调 函数,错误码代表执行结果 , * 当错误码为成功时,数据返回生成的 密钥的公钥和 P10 数据,回调响应包含密码剩余重试次数 . */ 

genKeyPairsAndPKCS10Sign(pin: string, certParams: 

Array<FTCertParam>, callback: ResultCallback<Array<FTCertPKCS10>>): void; /** * 导入 SM2 加解密证书密钥 ( 带验证密码 ) * 

* @param { string } pin - 设备的密码 . * @param { string } keyPair - SM2 加解密证书的密钥密文 . * @param { ResultCallback } callback - 函数执行结果回调函数,错误码代表执行结果 , * 回调响应包含密码 剩余重试次数 . */ importKeyPairWithPin(pin: string, keyPair: string, callback: ResultCallback<void>): void; /** * 导入 SM2 加解密证书 密钥,需在 genKeyPairsAndPKCS10Sign 接口后,设备不断开连接情 况下调用 * * @param { string } keyPair - SM2 加解密证书的密钥密 文 . * @param { ResultCallback } callback - 函数执行结果回调函数, 错误码代表执行结果 . */ importKeyPair(keyPair: string, callback: ResultCallback<void>): void; /** * 导入证书 * * @param { string } certs - base64 格式的证书数据 , 如果同时导入多张证书 , 则使用 || 进 行关联 . * @param { ResultCallback } callback - 函数执行结果回调函 数,错误码代表执行结果 . */ importCerts(certs: string, callback: ResultCallback<void>): void; } } 

# 第 2 章 API 功能介绍 

2 

# 2.1 初始化 

# 接口: 

initialize(context: Context| undefined, callback: ResultCallback 

<void>): void; 

功能: 

SDK 初始化函数,在使用 SDK 库时必须最先调用。 

参数: 

context: UIAbility 上下文 . callback: 函数执行结果回调函数,错误码代表执行结果 . 

2.2 析构 

接口: 

safeFinalize(): void; 

功能: SDK 析构函数,在该接口中释放 SDK 必要的资源 

参数: 

空。 

2.3 获取 SDK 版本 

接口: 

getLibVersion(): string; 

功能: 

获取厂商驱动库( SDK )的版本号。 参数: 

空。 

# 2.4 连接蓝牙 Key 

接口: 

connectKey( 

sn: string, 

timeout: number, 

callback: ResultCallback<void>): void; 

功能: 

通过设备序列号连接蓝牙 Key 。 

参数: 

sn: 蓝牙设备的序列号 

timeout: 超时时间 单位:秒 

callback: 函数执行结果回调函数,错误码代表执行结果 , 当错误码为 成功时,代表连接成功,错误码为蓝牙断开连接时,代表断开连接, 其他错误参考错误码定义。 

# 2.5 断开蓝牙 key 

接口: 

disconnectKey(): void; 

功能: 

断开已连接的蓝牙 key 。 

参数: 

空。 

# 2.6 取消连接蓝牙 key 

# 接口: 

cancelConnectKey(): void; 

功能: 

取消连接蓝牙 key 。 

参数: 

空。 

# 2.7 开始扫描蓝牙 key 

接口: 

startScanKey(callback: ResultCallback<string>): void; 

功能: 

开始扫描蓝牙 key 。 

参数: 

callback: 函数执行结果回调函数,错误码代表执行结果 , 扫描成功 时,持续响应回调函数,数据返回扫描到的蓝牙 KEY 名称。 

# 2.8 停止扫描蓝牙 key 

接口: 

stopScanKey(): void; 

功能: 

停止扫描蓝牙 key 。 

参数: 

空。 

# 2.9 获取设备序列号 

接口: 

getSN(callback: ResultCallback<string>): void; 

功能: 

获取 key 序列号。 

参数: 

callback: 函数执行结果回调函数,错误码代表执行结果 , 当错误码为 成功时,数据返回设备序列号信息。 

# 2.10 判断是否初始密码 

接口: 

isDefaultPin(callback: ResultCallback<void>): void; 

功能: 

判断 key 是否初始密码。 

参数: 

callback: 错误码代表执行结果 , 当错误码为设备是初始密码或设备不 是初始密码时,代表接口执行成功,其他错误参考错误码定义。 

2.11 获取密码重试次数 

接口: 

getPINRemainTimes(callback: ResultCallback<void>): void; 

功能: 

获取设备密码剩余重试次数。 

参数: 

callback: 函数执行结果回调函数,错误码代表执行结果 , 当错误码为 成功时,回调响应包含密码剩余重试次数。 

# 2.12 枚举证书 

接口: 

enumCert(callback: ResultCallback<Array<FTUserCertInfo>>): void; 

功能: 

枚举出 key 中所有的证书,并以 FTUserCertInfo 类返回证书信息。 

参数: 

callback: 函数执行结果回调函数,错误码代表执行结果 , 当错误码为 成功时,数据返回设备内的所有证书 . 。 

# 2.13 读取证书 

# 接口: 

getCert(cert: FTUserCertInfo, callback: ResultCallback<string>): void; 

功能: 

读取证书内容;证书内容用 base64 编码后通过 callback 返回。 

参数: 

cert: 指定的证书对象 详见 FTUserCertInfo 定义说明 

callback: 函数执行结果回调函数,错误码代表执行结果 , 当错误码为 成功时,数据返回指定证书的 base64 格式的证书数据。 

# 2.14 验证密码 

接口: 

verifyPin( 

pin: string, 

callback: ResultCallback<void>, ui?: UiCallback ): void; 

功能: 

验证 key 密码。 

参数: 

pin: key 的密码 

callback: 函数执行结果回调函数,错误码代表执行结果 , 回调响应包 含密码剩余重试次数。 

ui: ui 回调函数,等待按键确认时响应。 

2.15 修改密码 

接口: 

changePin( 

oldPin: string, newPin: string, 

callback: ResultCallback<void>, ui?: UiCallback ): void; 

功能: 

修改 key 密码。 

参数: 

oldPin: 旧密码 

newPin: 新密码 

callback: 函数执行结果回调函数,错误码代表执行结果 , 回调响应包 含密码剩余重试次数。 

# ui: ui 回调函数,等待按键确认时响应。 

2.16 签名 

接口: 

sign( 

pin: string, cert: FTUserCertInfo, hash: FTUserSignAlg, 

plain: string, type: FTSignResultType, 

callback: ResultCallback<string>, ui?: UiCallback ): void; 

功能: 

签名操作,待签名数据通过 plain 参数传入,签名结果通过回调接口 callback 返回。 

参数: 

pin: key 的密码 

cert: 证书信息 详见 FTUserCertInfo 定义说明 

hash: 签名算法 详见 FTUserSignAlg 定义说明 

plain: 签名原文。 

type: 签名结果返回类型 详见 FTSignResultType 定义说明 

callback: 函数执行结果回调函数,错误码代表执行结果 , 当错误码为 成功时,数据返回指定格式的签名结果,回调响应包含密码剩余重试 次数。 

ui: ui 回调函数,等待按键确认时响应。 

2.17 初始化 Key 

接口: 

initKey( 

pin: string, callback: ResultCallback<void>, 

ui?: UiCallback ): void; 

功能: 

对 key 进行初始化。 

参数: 

pin: 初始化 Key 后的默认初始密码 

callback: 函数执行结果回调函数,错误码代表执行结果。 ui: ui 回调函数,等待按键确认时响应。 

2.18 生成密钥并产生 P10 

接口: 

genKeyPairsAndPKCS10Sign( 

pin: string, certParams: Array<FTCertParam>, 

callback: ResultCallback<Array<FTCertPKCS10>>): void; 

功能: 

根据请求证书参数信息生产密钥对,并产生 P10 数据。 

参数: 

pin: key 的密码 

certParams :请求证书参数信息 详见 FTCertParam 定义说明 

callback: 函数执行结果回调函数,错误码代表执行结果 , 当错误码为 成功时,数据返回生成的密钥的公钥和 P10 数据 , 详见 FTCertPKCS10 定义说明,回调响应包含密码剩余重试次数。 

# 2.19 导入密钥对 

# 接口: 

importKeyPair(keyPair: string, callback: ResultCallback<void>): void; 

# 功能: 

支持导入 SM2 双证时对应的加解密证书的密钥。需在 genKeyPairsAndPKCS10Sign 接口后,设备不断开连接情况下调用。 参数: 

keyPair: 加密的密钥对数据 

callback: 函数执行结果回调函数,错误码代表执行结果。 

2.20 导入证书 

接口: 

importCerts(certs: string, callback: ResultCallback<void>): void; 

功能: 

导入证书。 

参数: 

certs: base64 格式的证书数据,多张证书用 “||” 隔开 

callback: 函数执行结果回调函数,错误码代表执行结果。 

2.21 验 PIN 导入密钥对 

接口: 

importKeyPairWithPin( 

pin: string, keyPair: string, callback: ResultCallback<void>): void; 

# 功能: 

支持导入 SM2 双证时对应的加解密证书的密钥。 

参数: 

pin:key 的密码 

keyPair: 加密的密钥对数据 

callback: 函数执行结果回调函数,错误码代表执行结果,回调响应包 含密码剩余重试次数。 

第 3 章 API 返回码解释 

注 : 对应枚举类 FTUserErrCode 和异常类 FTUKeyError 信息 

返回值 

错误码名称 

错误描述信息 

0 

FT_SUCCESS 

操作成功 

1 

FT_OPERATION_FAILED 

操作失败 

2 

FT_NO_DEVICE 

设备未连接 

3 

# FT_ENERGY_LOW 

设备电量不足,不能进行通讯 

4 

FT_DEVICE_BUSY 

设备忙 

5 

FT_INVALID_PARAMETER 

参数错误 

6 

FT_USER_CANCEL 

用户取消操作 

7 

FT_OPERATION_TIMEOUT 

操作超时 

8 

FT_SN_NOTMATCH 

序列号不匹配 

9 

FT_NO_CERT 

没有找到证书或对应密钥对 

10 

FT_CERT_INVALID 

# 证书格式不正确 

11 

FT_CERT_EXPIRED 

证书过期 

12 

FT_CERT_NOT_FROM_FUTURE 证书未生效 13 

FT_CERT_NOTMATCH 没有匹配到证书 

14 

FT_SIGN_MESSAGE_ERROR 签名报文格式不正确 15 

FT_SIGN_ALG_ERROR 签名算法错误 

16 

FT_PIN_LOCK PIN 码锁定 17 

FT_SAME_PASSWORD 

新旧密码相同 

18 

FT_PASSWORD_INVALID_LENGTH 

密码长度错误 

19 

FT_PASSWORD_TOO_SIMPLE 

简单密码 

20 

FT_PASSSWORD_INVALID 密码包含特殊字符 

21 

FT_PASSWORD_WRONG 密码错误 

22 

FT_DEFAULT_PIN 

设备密码是初始密码 

23 

FT_COMM_ERROR 

通讯错误 

24 

FT_COMM_TIMEOUT 

通讯超时 

25 

# FT_OTHER_ERROR 

# 其他错误 

26 

FT_BLE_PLATFORM_NOT_SUPPORT_BLE 此设备不支持蓝牙 4.0 协议 

27 

FT_PHONE_BT_CLOSE 

手机蓝牙未开启 

28 

FT_BLE_APP_NOT_BLE_AUTHORIZE 

此应用没有得到蓝牙设置的授权 

29 

FT_BLE_CANCEL_CONNECT_DEVICE 

取消连接设备 

30 

FT_BLE_CONNECT_TIMEOUT 

设备连接超时 

100 

FT_NOT_DEFAULT_PIN 

设备密码不是初始密码 

101 

FT_BT_CONNECT_SUCCESS 

# 蓝牙连接成功 

102 

FT_BT_DISCONNECT 

蓝牙连接断开
