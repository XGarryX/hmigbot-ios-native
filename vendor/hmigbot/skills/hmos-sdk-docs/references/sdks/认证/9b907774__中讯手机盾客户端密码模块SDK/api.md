手机盾客户端密码模块 V2.10.1 东方中讯数字证书认证有限公司 

2025 年 8 月 

API 接口说明 

数据常量定义 

数据常量标识的定义如下表所示。 常量名 

取值 描述 

SIGN_KEY_TYPE 1 签名密钥 ENCRYPT_KEY_TYPE 

2 加密密钥 

LOCAL_VERIFY _MODE _PIN 

0 本地认证方式为口令 LOCAL_VERIFY_MODE_TOUCH 1 本地认证方式为指纹 LOCAL_VERIFY_MODE_FACE 

2 本地认证方式为人脸 LOCAL_AUTH_MODE_SEC 

3 

本地认证方式为 IOS 系统验证 

模块状态 MODULE_STATE 

MODULE_STATE_NOT_ACTIVED 

0 

密码模块未激活 

MODULE_STATE_ACTIVED 

1 

密码模块已激活 

MODULE_STATE_AUTHED 

2 

密码模块已激活且已校验过身份 MODULE_STATE_INVALID 

4 

用户已在其他设备激活 

数据结构描述 

统一信息 

class Unified { constructor() {} // 错误码 public code:number = 0; } 

# 密码验证统一信息 

class PaswordUnified extends Unified{ constructor() {super()} // 密 码剩余验证次数 public uiRetryCount:number = 0; } 

# 用户信息 

export class WTXT_USERINFO { constructor() {} // 版本号 public nVersion:number = 0; // 用户名 public szUserName:string = ""; // 手机号 public szMobileNum:string = ""; // 应用唯一标识 public szAppID:string = ""; // 用户唯一标识 public szUUID:string = ""; // 单位 UTF8 编码 public szUnit:string = ""; } 

SM2 属性 

export class WTXT_SM2ATTR { constructor() {} // 版本号 public nVersion:number = 0; // 密钥索引 public uiKeyIndex:number = 0; // 密钥状态 SIGN_KEY_TYPE | ENCRYPT_KEY_TYPE public uiKeyState:number = 0; // 证书状态 SIGN_KEY_TYPE | ENCRYPT_KEY_TYPE public uiCertState:number = 0; } 

# 模块信息 

export class WTXT_MODULEINFO extends Unified{ constructor() {super()} // 版本号 public nVersion:number = 0; // 用户信息 public userInfo:WTXT_USERINFO = new WTXT_USERINFO; // 索引个数 public nIndexNum:number = 0; //SM2 属性 public pSM2Attr:WTXT_SM2ATTR = new WTXT_SM2ATTR; } 

# 配置信息 

export class WTXT_SystemConfig extends Unified{ constructor() {super()} // 配置信息( json 字符串,具体解析和服务端匹配) public szConfig:string = ""; } 

# 模块状态 

export class WTXT_ModuleState extends Unified{ constructor() {super()} // 模块状态 public puiState:number = 0; } 

# 鉴别模式 

export class WTXT_LocalPinMode extends Unified{ constructor() {super()} // 鉴别模式 public uiMode:number = 0; } 

# 鉴别密码 

export class WTXT_LocalPin extends Unified{ constructor() {super()} // 鉴别密码 public szPassword:string = ""; } 

# 服务端验证模式 

export class WTXT_ServerPinMode extends Unified{ constructor() {super()} // 鉴别模式 public uiMode:number = 0; } 

# 密码剩余次数 

export class WTXT_PasswordCount extends PaswordUnified{ constructor() {super()} } 

ArrayBuffer 

export class WTXT_ArrayBuffer extends Unified{ constructor() {super()} //ArrayBuffer public arrayBuffer:ArrayBuffer = new ArrayBuffer(1); } 

# 生成 sm2 协同公私钥 

export class WTXT_GenSM2CoKeyPair extends PaswordUnified 

{ constructor() {super()} // 密码索引 public uiKeyIndex:number = 0; } 

# ECC 公钥结构 

export class WTXT_ECCPUBLICKEYBLOB extends Unified{ constructor() {super()} // 比特长度 public ulBitLen:number = 0; // x 坐标 public XCoordinate:ArrayBuffer = new ArrayBuffer(64); //y 坐标 public YCoordinate:ArrayBuffer = new ArrayBuffer(64); } 

# ECC 签名结构 

export class WTXT_ECCSIGNATUREBLOB extends PaswordUnified{ constructor() {super()} //r public r:ArrayBuffer = new ArrayBuffer(64); //s public s:ArrayBuffer = new ArrayBuffer(64); } 

# ECC 密文结构 

export class WTXT_ECCCIPHERBLOB extends Unified{ constructor() {super()} //x public XCoordinate:ArrayBuffer = new ArrayBuffer(64); //y public YCoordinate:ArrayBuffer = new ArrayBuffer(64); //bHash public bHash:ArrayBuffer = new ArrayBuffer(32); //pbCipher public pbCipher:ArrayBuffer = new ArrayBuffer(1); } 

# 解密原文数据 

export class WTXT_SM2CoDecryptPlain extends PaswordUnified{ constructor() {super()} // 原文 public pbPlain:ArrayBuffer = new ArrayBuffer(1); } 

# Asn1 数据 

export class Asn1 extends Unified{ constructor() {super()} //asn1 public asn1:ArrayBuffer = new ArrayBuffer(1); } 

# 句柄 

export class WTXT_HANDLE extends Unified{ constructor() {super()} // 句柄地址 public handle:number = 0; } 

# 摘要 

export class WTXT_HashData extends Unified{ constructor() {super()} // 摘要值 public pbHash:ArrayBuffer = new ArrayBuffer(1); } 

# 会话密钥 

export class WTXT_ExportSessionKey extends Unified{ constructor() {super()} // 密文 public pWrappedKey:WTXT_ECCCIPHERBLOB = new WTXT_ECCCIPHERBLOB; // 句柄地址 public handle:number = 0; } 

# 会话秘钥句柄 

export class WTXT_SessionHandle extends PaswordUnified{ constructor() {super()} // 句柄地址 public handle:number = 0; } 

# 对称密码算法参数 

export class WTXT_BLOCKCIPHERPARAM { constructor() {} //IV public bIV:ArrayBuffer = new ArrayBuffer(1); // 填充模 式 ,NO_PADDING 为 0 或 PKCS5_PADDING 为 1 public uiPaddingType:number = 0; // 反馈值的位长度, CFB 、 OFB 有效 public uiFreeBitLen:number = 0; } 

# 加密结果 

export class WTXT_Cipher extends Unified{ constructor() {super()} // 密文 public pbCipher:ArrayBuffer = new ArrayBuffer(1); } 

# 解密结果 

export class WTXT_Plain extends Unified{ constructor() {super()} // 明文 public pbPlain:ArrayBuffer = new ArrayBuffer(1); } 

# 请求证书返回值 

export class WTXT_RequestCertOut extends PaswordUnified{ constructor() {super()} } 

# 证书 

export class WTXT_Cert extends Unified{ constructor() {super()} // 证书 public pbCert:ArrayBuffer = new ArrayBuffer(1); } 

# 更新证书返回值 

export class WTXT_UpdateCertOut extends PaswordUnified{ constructor() {super()} } 

# 配置信息 

export class SdkConfig { 

// sdk 调用后台的地址 

url: string = ''; 

//appKey 

appKey: string = ''; 

// appSecret 

appSecret: string = ''; 

//appId 

appId: string = ''; // // 单位 

unit: string = ''; 

} 

其它信息 

export class SzOther { 

orderNo?: string 

} 

接口定义 

接口描述 

设置配置 

函数原型 setDefaultConfig(configs: (config: SdkConfig) => void): void { 

configs(WtxtgmHelper.config); 

} 

功能描述 SDK 设置配置,使用 SDK 之前需要配置 

参数 configs SdkConfig 配置西悉尼 

返回值 

其他: 错误码。 

切换用户 

函数原型 switchUser( 

mobileNum: string, 

userName: string = '', 

uuId: string, 

appId?: string, 

unit?: string): number 

功能描述 初始化 SDK 并切换用户 

参数 mobileNum 手机号码 

参数 userName 用户名 

参数 uuId 用户唯一标识 

参数 appId 应用唯一标识 参数 unit 单位编码 

返回值 Err_WTXT_OK : 成功。 其他: 错误码。 获取服务端配置 

函数原型 systemConfig( appId?: string, unit?: string ) :WTXT_SystemConfig 

功能描述 获取服务端配置 

参数 appId 应用唯一标识。 

unit 单位 UTF-8 编码。 

返回值 WTXT_SystemConfig 配置信息对象。 

获取模块信息 

函数原型 moduleInfo( 

) :WTXT_MODULEINFO 

功能描述 获取模块信息,包括版本号、用户名、密钥标识与对应的证 书标识等信息 

参数 

返回值 WTXT_MODULEINFO 模块信息对象。包括版本号、用户名、 密钥标识与对应的证书标识等信息。 

获取模块状态 

函数原型 moduleState( 

) :WTXT_ModuleState 

功能描述 获取模块状态 

参数 

返回值 模块状态对象。模块状态取值 MODULE_STAT 或 MODULE_STATE 按位或 

模块置零 

函数原型 resetModule( 

) :number 

功能描述 模块置零 

参数 

返回值 Err_WTXT_OK : 成功。 

其他: 错误码。 

设置本地身份鉴别模式 

函数原型 setAuthenticateMode( 

authMode:number 

) : Promise<number> 

功能描述 设置本地身份鉴别模式,支持口令验证、与手机本地生物验 证(如指纹、人脸识别)。使用 await 关键字调用,可实现同步等待 调用结果。 

参数 authMode 支持以下值 

LOCAL_AUTH_MODE_PIN 

LOCAL_AUTH_MODE_SEC 

LOCAL_AUTH_MODE_FACE 

返回值 Err_WTXT_OK : 成功。 

其他: 错误码。 

获取本地身份鉴别模式 

函数原型 getAuthenticateMode( 

) :WTXT_LocalPinMode 

功能描述 获取本地身份鉴别模式,支持口令验证、与手机本地生物验 证(如指纹、人脸识别)。 参数 

返回值 身份鉴别模式对象。支持以下值 

LOCAL_AUTH_MODE_PIN 

LOCAL_AUTH_MODE_SEC 

LOCAL_AUTH_MODE_FACE 

请求短信验证码 

函数原型 requestSmsAck( 

userInfo:WTXT_USERINFO 

) :number 

功能描述 请求短信验证码 

参数 

返回值 Err_WTXT_OK : 成功。 

# 其他: 错误码。 

修改口令 

函数原型 changePassword( 

szSmsAck:string, 

szOldPassword:string, 

szNewPassword:string 

) :WTXT_PasswordCount 

功能描述 修改口令 

参数 szSmsAck 短信验证码。 szOldPassword 旧口令。 szNewPassword 新口令。 返回值 密码操作结果对象。 忘记密码 

函数原型 forgetPassword( szSmsAck:string, 

szNewPassword:string 

) :number 功能描述 生成随机数 

参数 szSmsAck 短信验证码。 szNewPassword 新口令。 

返回值 Err_WTXT_OK : 成功。 其他: 错误码。 

# 生成随机数 

函数原型 genRandom( 

randomLen:number 

) :WTXT_ArrayBuffer 

功能描述 生成随机数 

参数 randomLen 随机数字节长度。 返回值 随机数结果对象。 SM2 协同签名 

函数原型 sm2Sign( inData: ArrayBuffer 

) : Asn1 功能描述 SM2 协同签名。 

参数 inData [IN] 待签名数据。 返回值 签名值对象。 SM2 验签 函数原型 sm2Verify( signData: ArrayBuffer, inData: ArrayBuffer 

) :number 功能描述 SM2 验签 

参数 signData 签名值 inData 签名原文 

返回值 Err_WTXT_OK : 成功。 

其他: 错误码。 

SM2 加密 

函数原型 sm2Encrypt( 

intData:ArrayBuffer 

) :Asn1 

功能描述 SM2 加密 

参数 data 待加密的数据。 

返回值 Asn1 密文数据结构对象。 

SM2 解密 

函数原型 sm2Decrypt( 

encData: ArrayBuffer 

) : WTXT_SM2CoDecryptPlain 

功能描述 SM2 协同解密。使用 await 关键字调用,可实现同步等待调 用结果。 

参数 WTXT_SM2CoDecryptPlain 密文数据。 

返回值 原文数据结构对象。 

请求生成证书(指定 CA ) 

函数原型 requestCertWithCA( 

smsCode: string, password: string, 

szCA: string, 

szOther: SzOther, 

certUseType: number) : Promise<WTXT_RequestCertOut> 

功能描述 请求生成证书。使用 await 关键字调用,可实现同步等待调 用结果。 

参数 smsCode 短信验证码,可为空。 

password sdk pin 码 

szCA 指定 CA 

szOther SzOther 

certUseType 证书用途 1= 签名; 2= 签名和加密 

返回值 证书申请结果对象。 

读签名证书 

函数原型 readSignCert() :WTXT_Cert 

功能描述 读证书 

参数 

返回值 证书对象。 

读加密证书 

函数原型 readSignCert() :WTXT_Cert 

功能描述 读证书 

参数 

返回值 证书对象。 

解析证书 

函数原型 getCertInfo(szCert: ArrayBuffer, 

iNameID: number, 

iSubNameID: number): WTXT_CertGB 

功能描述 更新证书。使用 await 关键字调用,可实现同步等待调用结 果。 

参数 szCert 证书数据。 

iNameID 证书信息项。 

iSubNameID 证书信息子项 

返回值 WTXT_CertGB 

其他: 错误码。 

校验口令 

函数原型 verifyPassword(password: string): WTXT_PasswordCount 

功能描述 校验口令 

参数 password 口令。 

返回值 验证结果对象。返回连续出错后剩余的重试次数。 

上传日志 

函数原型 uploadLogs(appName: string): number 

功能描述 切换用户 

参数 appName 应用名 

返回值 Err_WTXT_OK : 成功。 

其他: 错误码。 

错误码 

错误码常量 

# 错误码值 

错误码描述 

Err_WTXT_OK 

0 

成功 

Err_WTXT_BASE 0x000F0000 

无(错误码起始值) 

Err_WTXT_NOT_INITIALIAZE 0x000F0001 未初始化模块 

Err_WTXT_NEED_RESET _MODULE 0x000F0002 需要重置模块 

Err_WTXT_INVALID_ARGS 

0x000F0003 

参数无效 

Err_WTXT_MEM_LESS 

0x000F0004 

内存不足 

Err_WTXT_GEN_SM2_COKEYPAIR 

0x000F0005 

生成 SM2 协同公私钥对失败 

Err_WTXT_SM2 _SIGN 0x000F0006 

SM2 协同私钥签名失败 Err_WTXT_SM2_VERIFY 0x000F0007 

SM2 验证签名失败 Err_WTXT_SM2_ENCRYPT 0x000F0008 

SM2 加密出错 

Err_WTXT_SM2_DECRYPT 0x000F0009 

SM2 协同私钥解密出错 

Err_WTXT_HASH 0x000F000A 

HASH 出错 

Err_WTXT_CIPHER 

0x000F000B 

# 对称加解密出错 

Err_WTXT_CERT_NOT_FOUND 

0x000F000C 

未找到证书 

Err_WTXT_WRITE_CERT 

0x000F000D 

写证书错误 

Err_WTXT_GEN_RANDOM 

0x000F000E 

生成随机数失败 

Err_WTXT_NOT_SUPPORT_FUNCTION 

0x000F000F 

不支持该功能 

Err_WTXT_USER_CANCEL_OP 

0x000F0010 

用户取消操作 

Err_WTXT_NET_CONNECT 

0x000F0100 

# 网络连接错误 

Err_WTXT_NET _RECV_PARSE 

0x000F0101 

网络数据无法解析 

Err_WTXT_NET _RECV_DATA 

0x000F0102 

接受网络数据出错 

Err_WTXT_SRV_MOBILE_NUM_NOT_FOUND 

0x00100001 

服务器返回手机号未注册 

Err_WTXT_SRV_APP_INVALID_CONFIG 

0x00100002 

服务器返回应用设置不正确 

Err_WTXT_SRV_DEVICE_FP_NOT_MATCH 

0x00100003 

服务器返回设备指纹不匹配 

Err_WTXT_SRV_SMS_ACK_ERR 

0x00100004 

# 服务器返回手机验证码不正确 

Err_WTXT_SRV_DEVICE_NOT_SAFE 

0x00100005 

服务器返回设备不安全(通常为手机被 Root 或越狱) 

Err_WTXT_SRV_MOBILE_NUM_CONFLICTS 

0x00100006 

服务器返回多个手机同时使用同一手机号码操作 

Err_WTXT_SRV_VERIFY_PASSWORD_FAIL 

0x00100007 

服务器返回用户口令错误 

Err_WTXT_SRV_PASSWORD_LOCKED 

0x00100008 

服务器返回用户口令锁死 

Err_WTXT_SRV_COPRIVATEKEY_NOT_FOUND 

0x00100009 

服务器返回 SM2 协同私钥未发现 

Err_WTXT_SRV_INVALID_SIGNATURE 

0x00100010 

服务器返回无效签名值 

Err_WTXT_FAIL 

0xFFFFFFFF 

通用错误
