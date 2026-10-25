# 屹通安全加密 SDK 使用文档 

本文档面向集成 YTCryptoLib 的 HarmonyOS 开发者,说明 SDK 的 安装、初始化、报文加解密、国密算法、通用加密、摘要计算、随机 密钥生成和使用建议。 

项目 

说明 

SDK 名称 

屹通安全加密 SDK 

包名 

@yitong/ytcryptolib 

主入口 

index.ets 

SDK 类型 

HarmonyOS HAR 

当前版本 

1.0.0 

# 1. 功能概览 

YTCryptoLib 是面向 HarmonyOS 应用的加解密能力库,覆盖报文加 解密、国密算法( SM2/SM3/SM4 )、通用对称加密( AES/ DES/3DES )、随机密钥生成等能力。核心算法通过 native 库 libytcrypto.so 实现,通用加密通过 CryptoJS 封装。 

能力模块 

主要 API 

用途 

# 报文加密 V1 (国密) 

requestEncodeV1 

SM4 加密数据 + SM2 加密密钥 + SM3/SM3-HMAC 摘要,三段式 报文格式。 

报文加密 V2 (国密 Token ) 

requestEncodeV2 

SM4 加密数据 + SM3/SM3-HMAC 摘要,使用 Token 替代 SM2 加 密密钥段。 

报文加密 V3 (国密签名) 

requestEncodeV3 、 responseDecodeV3 

SM4 加密数据 + SM2 加密密钥 + SM2 签名校验,附带 PKCS5 填 充。 

# 响应解密 

responseDecode 

V1/V2 解密响应报文,支持混淆处理。 

国密算法 

sm2Encode 、 sm3Encode 、 sm3HmacEncode 、 sm4Encode 、 sm4Decode 

标准 SM2 加密、 SM3/SM3-HMAC 摘要、 SM4 对称加解密。 通用对称加密 

aesEncrypt 、 aesDecrypt 、 aesCBCEncrypt 、 aesCBCDecrypt 、 desEncrypt 、 desDecrypt 、 tripleDesEncrypt 、 tripleDesDecrypt 

基于 CryptoJS 的 AES 、 AES-CBC 、 DES 、 3DES 加解密。 

随机密钥 

genRandomKey 

基于系统加密框架生成指定长度的随机字符串。 

# 2. 安装与引入 

在宿主工程中引入 HAR 依赖后,可从包入口按需导入需要的能力。 包名以 oh-package.json5 中的 name 值为准。 

// oh-package.json5 

{ 

"dependencies": { 

"@yitong/ytbasiccorelib": "file:../YTBasicCoreLib" 

"@yitong/ytcryptolib": "file:./libs/YTCryptoLib.har" 

} 

} 

import { 

YTCryptoUtil, 

YTDigestType, 

YTGeneralCryptoUtil 

} from '@yitong/ytcryptolib'; 

# 3. 初始化建议 

YTCryptoLib 的静态方法无需实例化即可调用。 native 库 libytcrypto.so 在首次调用时自动加载,无需额外初始化。但建议在 使用前注意以下事项: 

报文加密 V0 方案依赖 RSA 证书文件(默认 server_rsa.cer ),应确 保证书已放入 rawfile 目录。 

报文加密 V1/V3 方案需要 SM2 公钥( pubKeyX 、 pubKeyY ),应从 

# 服务端获取并妥善保管。 

密钥应使用 genRandomKey 生成,不要使用固定字符串作为密钥。 

生产环境避免在日志中输出密钥、明文数据或密文摘要。 

如需 RSA 证书加密或解密,应先通过 YTAppFramework 初始化应用 上下文以支持 rawfile 读取。 

# 4. 常用能力示例 

# 4.1 随机密钥生成 

genRandomKey 基于系统 cryptoFramework.createRandom 生成随机 字符串,可用于作为 SM4 或 AES 的对称密钥。 

// 生成 16 位随机密钥(默认长度) 

const key = YTCryptoUtil.genRandomKey(16); 

// 生成 32 位随机密钥 

const longKey = YTCryptoUtil.genRandomKey(32); 

4.2 SM4 对称加解密 

SM4 支持空间填充和 PKCS5 填充两种方式,输出可选择 hex 或 base64 编码。 

const key = YTCryptoUtil.genRandomKey(16); 

// SM4 加密(空间填充, hex 编码) 

const cipherText = YTCryptoUtil.sm4Encode('hello', key, 

YTCryptoUtil.SM4_PADDING_TYPE_SPACE, 

YTCryptoUtil.UINT8_ENCODE_HEX); 

// SM4 解密 

const plainText = YTCryptoUtil.sm4Decode(cipherText, key, 

YTCryptoUtil.SM4_PADDING_TYPE_SPACE, 

YTCryptoUtil.UINT8_ENCODE_HEX); 

// SM4 加密( PKCS5 填充, base64 编码) 

const cipherB64 = YTCryptoUtil.sm4Encode('hello', key, 

YTCryptoUtil.SM4_PADDING_TYPE_PKCS5, 

YTCryptoUtil.UINT8_ENCODE_BASE64); 

const plainB64 = YTCryptoUtil.sm4Decode(cipherB64, key, 

YTCryptoUtil.SM4_PADDING_TYPE_PKCS5, 

YTCryptoUtil.UINT8_ENCODE_BASE64); 

4.3 国密 SM2/SM3 标准算法 

SM2 用于非对称加密, SM3 用于摘要计算, SM3-HMAC 用于带密钥 的摘要。 

// SM2 加密(需提供公钥 X/Y 坐标) 

const sm2Cipher = YTCryptoUtil.sm2Encode( 

'hello', 

'sm2_public_key_x', 

'sm2_public_key_y', 

YTCryptoUtil.UINT8_ENCODE_HEX 

); 

// SM3 摘要 

const sm3Digest = YTCryptoUtil.sm3Encode( 

new Uint8Array([1, 2, 3]), 

YTCryptoUtil.UINT8_ENCODE_HEX 

); 

// SM3-HMAC 摘要 

const sm3HmacDigest = YTCryptoUtil.sm3HmacEncode( 

new Uint8Array([1, 2, 3]), 

'hmac_key', 

YTCryptoUtil.UINT8_ENCODE_HEX 

); 

4.4 通用 AES/DES/3DES 加密 

YTGeneralCryptoUtil 基于 CryptoJS 封装了 AES 、 AES-CBC 、 DES 和 3DES 等通用对称加密算法。 

// AES 加密和解密 

const aesCipher = YTGeneralCryptoUtil.aesEncrypt('hello', 'your_key'); 

const aesPlain = YTGeneralCryptoUtil.aesDecrypt(aesCipher, 'your_key'); 

// AES-CBC 加密和解密(自定义 IV ) 

const cbcCipher = YTGeneralCryptoUtil.aesCBCEncrypt('hello', 'your_key', 'your_iv'); 

const cbcPlain = YTGeneralCryptoUtil.aesCBCDecrypt(cbcCipher, 'your_key', 'your_iv'); 

# // DES 加密和解密 

const desCipher = YTGeneralCryptoUtil.desEncrypt('hello', 'your_key'); 

const desPlain = YTGeneralCryptoUtil.desDecrypt(desCipher, 'your_key'); 

# // 3DES 加密和解密 

const tripleCipher = YTGeneralCryptoUtil.tripleDesEncrypt('hello', 'your_key'); 

const triplePlain = YTGeneralCryptoUtil.tripleDesDecrypt(tripleCipher, 'your_key'); 

# 4.6 报文加密 V0 ( AES + RSA 国际方案) 

V0 方案使用 AES 加密业务数据,使用 RSA 公钥证书加密 AES 密 钥,摘要默认使用 MD5 。返回 ASCII 29 分隔的三段式报文。 

const key = YTCryptoUtil.genRandomKey(16); 

```arkts
const data = JSON.stringify({ name: 'Tom' }); 
```

# // V0 请求加密 

const v0Request = YTCryptoUtil.requestEncodeV0( 

data, 

key, 

'', // iv (可选,默认 '' ) 

'server_rsa.cer', // RSA 证书路径 

YTCryptoUtil.RSA_CER_TYPE_DER, // 证书类型( 1=DER , 2=PEM ) 

YTDigestType.MD5 // 摘要算法( 0=MD5 , 1=SHA256 ) 

); 

// V0 响应解密 

const v0Response = YTCryptoUtil.responseDecodeV0( 

encryptedResponse, 

key, 

'', 

YTCryptoUtil.RESPONSE_CONFUSE_DEFAULT // 混淆类型 

); 

4.7 报文加密 V1 ( SM4 + SM2 + SM3 国密方案) 

V1 方案使用 SM4 加密数据、 SM2 加密密钥、 SM3/SM3-HMAC 生成 摘要,返回 #10 或 #11 前缀的三段式报文。 

const key = YTCryptoUtil.genRandomKey(16); 

// V1 请求加密( SM3 模式) 

const v1Request = YTCryptoUtil.requestEncodeV1( 

JSON.stringify({ name: 'Tom' }), 

key, 

'sm2_public_key_x', 

'sm2_public_key_y', 

false, // isHmac: false=SM3, true=SM3-HMAC 

'YTBASE' // 摘要盐值 

); 

// V1/V2 响应解密 

const v1Response = YTCryptoUtil.responseDecode( 

encryptedResponse, 

key, 

YTCryptoUtil.RESPONSE_CONFUSE_DEFAULT 

); 

4.8 报文加密 V2 ( SM4 + SM3 + Token 方案) 

V2 方案与 V1 类似,但使用服务端下发的 Token 替代 SM2 加密的密 钥段,返回 #20 或 #21 前缀的三段式报文。 

const key = YTCryptoUtil.genRandomKey(16); 

// V2 请求加密( SM3-HMAC 模式) 

const v2Request = YTCryptoUtil.requestEncodeV2( 

JSON.stringify({ name: 'Tom' }), 

key, 

'server_token', // 服务端握手获取的 token 

true, // isHmac: true=SM3-HMAC 

'YTBASE' // 摘要盐值 

); 

// 响应解密同 V1 ,使用 responseDecode 

4.9 报文加密 V3 ( SM4 + SM2 加密 + SM2 签名方案) 

V3 方案在 V1 基础上增加了 SM2 签名校验,并采用 PKCS5 填充, 返回 #30 前缀的三段式报文。 

const key = YTCryptoUtil.genRandomKey(16); 

// V3 请求加密 

const v3Request = YTCryptoUtil.requestEncodeV3( 

JSON.stringify({ name: 'Tom' }), 

key, 

'sm2_public_key_x', 

'sm2_public_key_y', 

'sign_private_key' // SM2 签名私钥 

); 

// V3 响应解密( PKCS5 填充) 

const v3Response = YTCryptoUtil.responseDecodeV3( 

encryptedResponse, 

key, 

YTCryptoUtil.RESPONSE_CONFUSE_DEFAULT 

); 

# 5. 报文加解密协议说明 

报文加解密采用三段式结构,以 ASCII 29 ( \u001D )作为分隔符。 各版本差异如下: 

# 5.1 协议版本对照 

版本 

前缀 

数据加密 

# 密钥加密 

摘要 / 签名 填充 V0 无 AES RSA 证书公钥 MD5/SHA256 (key+data) PKCS7 V1 SM3 #10 SM4 SM2 公钥 SM3 (data+key) + YTBASE 无填充 V1 HMAC #11 SM4 SM2 公钥 SM3-HMAC (data+key) + YTBASE 无填充 

V2 SM3 

#20 

SM4 

Token 

SM3 (data+key) + YTBASE 

无填充 

V2 HMAC #21 

SM4 

Token 

SM3-HMAC (data+key) + YTBASE 

无填充 

V3 

#30 

SM4 

SM2 公钥 

SM2 签名 (data+key) 

PKCS5 

# 5.2 三段式报文结构 

所有版本的报文均由三个数据段通过 ASCII 29 分隔符拼接而成: // 报文格式(以 V1 为例) 

// #10 + SM4 密文 + CHAR_SPLIT(29) + SM2 加密后的密钥 + CHAR_SPLIT(29) + SM3 摘要 

# // 前缀 段 1 段 2 段 3 

段 1 :业务数据密文( SM4 或 AES 加密)。 

段 2 :密钥密文或 Token ( SM2 加密的对称密钥,或服务端下发的 Token )。 

段 3 :摘要或签名( SM3/SM3-HMAC 摘要或 SM2 签名)。 

三段以 ASCII 29 ( \u001D )分隔, V1/V2/V3 报文头部附带版本前 缀。 

5.3 加密流程(以 V1 为例) 

调用 genRandomKey 生成 16 位随机 SM4 密钥。 

用 SM4 密钥对业务数据加密,得到段 1 ( SM4 密文)。 

用 SM2 公钥加密 SM4 密钥,得到段 2 (密钥密文)。 

将 data + key 拼接后,用 SM3/SM3-HMAC + tag 生成摘要,得到 段 3 。 

以 #version + 段 1 + \u001D + 段 2 + \u001D + 段 3 格式拼接返 回。 

# 6. 常量与枚举参考 

6.1 填充类型 

常量 

值 

说明 

SM4_PADDING_TYPE_SPACE 

1 

SM4 空间字符填充。 

SM4_PADDING_TYPE_PKCS5 

2 

SM4 PKCS5 标准填充。 

# 6.2 编码类型 

常量 

值 

说明 

UINT8_ENCODE_HEX 1 

输出十六进制字符串编码。 UINT8_ENCODE_BASE64 2 

输出 Base64 字符串编码。 6.3 RSA 证书类型 

常量 

值 

说明 

RSA_CER_TYPE_DER 

1 

DER 编码的 .cer 证书文件。 RSA_CER_TYPE_PEM 

2 

PEM 编码的证书文件。 

# 6.4 响应混淆类型 

常量 

值 

说明 

RESPONSE_CONFUSE_NONE 

0 

不解混淆。 

RESPONSE_CONFUSE_DEFAULT 

1 

默认混淆模式。 

6.5 摘要算法类型 枚举值 数值 说明 

YTDigestType.MD5 

0 

MD5 摘要( V0 请求默认)。 

YTDigestType.SHA256 

1 SHA256 摘要。 

6.6 其他常量 

常量 

值 

说明 

CHAR_SPLIT 

29 (ASCII) 

三段式报文分隔符。 

DEFAULT_RANDOM_LENGTH 

16 

genRandomKey 默认长度。 

DEFAULT_SM3_TAG 

"YTBASE" 

SM3/SM3-HMAC 默认盐值。 

DEFAULT_AES_IV 

"" 

AES 默认 IV (空字符串)。 

DEFAULT_RSA_CER 

"server_rsa.cer" 

默认 RSA 证书 rawfile 路径。 

7. YTGeneralCryptoUtil API 参考 

YTGeneralCryptoUtil 基于 @ohos/crypto-js 封装,提供 AES 、 DES 、 3DES 、 SHA256 、 MD5 等通用算法能力。所有方法均为静态方 法。 

方法 

签名 

# 说明 

aesEncrypt 

(data: string, key: string): string 

AES 加密, CBC 模式, PKCS7 填充。 

aesDecrypt 

(data: string, key: string): string AES 解密,返回 UTF-8 字符串。 

aesCBCEncrypt 

(data: string, key: string, iv?: string): string AES-CBC 加密,自定义密钥和 IV 。 

aesCBCDecrypt 

(data: string, key: string, iv?: string): string AES-CBC 解密,自定义密钥和 IV 。 

desEncrypt 

(data: string, key: string): string 

DES 加密。 

desDecrypt 

(data: string, key: string): string 

DES 解密。 

tripleDesEncrypt 

(data: string, key: string): string 

3DES 加密。 

# tripleDesDecrypt 

(data: string, key: string): string 

3DES 解密。 

# 8. 权限与合规说明 

YTCryptoLib 的 HAR 模块自身未声明系统权限。 SDK 主要处理开发 者主动传入的明文、密钥、证书、公钥、密文和摘要数据,不主动采 集设备信息、位置信息、通讯录、相册、短信等个人信息。 

能力 

可能涉及权限或系统能力 

建议 

随机密钥生成 

调用 cryptoFramework.createRandom 系统能力,通常不需要运行时 权限。 

密钥生成在本地完成,不涉及网络传输。 

RSA 证书读取 

读取 rawfile 中的证书文件,依赖应用上下文。 

使用前建议初始化 YTAppFramework 以获取 resourceManager 。 

native 加解密 

调用 libytcrypto.so native 库,在应用沙箱内运行。 

加解密均在本地完成,不涉及网络通信。 

CryptoJS 加密 

纯 ArkTS 层计算,不涉及系统权限。 

密钥由开发者自行管理。 

开发者应自行保护密钥、证书和明文数据,避免将敏感信息写入日 志、明文文件或不安全的本地缓存。 

# 9. 最佳实践 

每次请求使用 genRandomKey 生成新密钥,不要使用固定密钥。 

V1/V3 方案的 SM2 公钥从服务端获取,本地不要硬编码生产密钥 对。 

报文加密选择:国内业务推荐 V1/V3 国密方案,国际 / 通用场景可采 用 V0 。 

加密模式下,确保 SM4 解密时使用的填充类型与加密时一致(空间 填充或 PKCS5 )。 

生产环境避免在日志中输出 genRandomKey 生成的密钥、 SM4 明 文、 SM2 公私钥。 

RSA 证书文件应放在 rawfile 目录下,通过相对路径引用。 

CryptoJS 的 AES/DES 密钥应避免使用弱密钥,推荐使用 genRandomKey 生成。 

# 10. 常见问题 

# 问题 

# 说明 

V0 、 V1 、 V2 、 V3 应该如何选择? 

V0 是国际方案( AES+RSA ),适合海外业务或与存量非国密系统对 接。 V1 是国密方案( SM4+SM2+SM3 ),适合国内合规场景。 V2 在 V1 基础上用 Token 替代 SM2 加密密钥,适合已完成握手的会话 复用场景。 V3 在 V1 基础上增加了 SM2 签名校验,适合高安全场 景。 

SM4 解密返回空字符串是什么原因? 

常见原因:密文长度不是 16 的整数倍、编码格式不匹配( hex vs base64 )、填充类型不一致(空间填充 vs PKCS5 )、密钥不匹配。 

genRandomKey 生成的密钥安全吗? 

genRandomKey 优先使用系统 cryptoFramework.createRandom 生成 随机数,熵源来自系统安全随机数生成器。仅在系统能力不可用时回 退到 Math.random 。 

RSA 证书加密需要什么格式的证书? 

支持 DER 编码的 .cer 文件和 PEM 编码的证书文件,通过 RSA_CER_TYPE_DER(1) 或 RSA_CER_TYPE_PEM(2) 指定类型。 

CryptoJS 加密和 native 加密有什么区别? 

YTGeneralCryptoUtil 使用 CryptoJS (纯 ArkTS 实现),适合通用 AES/DES/3DES 场景。 YTCryptoUtil 的 SM2/SM3/SM4 使用 native C++ 实现( libytcrypto.so ),性能更高且支持国密算法。 

SM3 和 SM3-HMAC 有什么区别? 

SM3 是标准哈希摘要。 SM3-HMAC 在 SM3 基础上增加了密钥参与, 提供消息认证码能力,适合防篡改场景。 

文档结束
