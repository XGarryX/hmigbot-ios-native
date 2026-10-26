密级: 公开/ 一般/ 保密 

# 白盒安全组件 鸿蒙ArkTS 接口文档 

##### 北京信长城科技发展有限公司 

- 1 

- 

北京信长城科技发展有限公司 

网址:www.i-wall.cn 

密级: 公开/ 一般/ 保密 

##### 文档记录 

|编号|日期||描述|版本|作者|
|---|---|---|---|---|---|
|1|2024-05-27|文档创建||v1.0|刘文柠|

2 

- 

- 

北京信长城科技发展有限公司 

网址:www.i-wall.cn 

密级: 公开/ 一般/ 保密 

###### 目录 

|1 ArkTS 接口定义.......................................................................................5|
|---|
|1.1 基础接口......................................................................................5|
|1.1.1 获取版本号.........................................................................5|
|1.1.2 注册授权码.........................................................................5|
|1.1.3 初始化SDK......................................................................... 5|
|1.1.4 初始化证书链..................................................................... 6|
|1.1.5 生成CSR.............................................................................6|
|1.1.6 私钥签名............................................................................6|
|1.1.7 证书验签............................................................................7|
|1.1.8 证书链验证.........................................................................7|
|1.1.9 非对称加密(证书)........................................................... 8|
|1.1.10 非对称解密.......................................................................8|
|1.1.11 对称加解密.......................................................................8|
|1.1.12 对称算法扩展....................................................................9|
|1.1.13 CMAC 运算........................................................................10|
|1.1.14 写全局文件..................................................................... 10|
|1.1.15 读全局文件..................................................................... 10|
|1.1.16 删全局文件..................................................................... 11|
|1.1.17 写用户文件..................................................................... 11|
|1.1.18 读用户文件..................................................................... 11|
|1.1.19 删用户文件..................................................................... 12|
|1.1.20 清除用户文件..................................................................12|
|1.1.21 关闭释放SDK...................................................................12|
|1.2 扩展接口.................................................................................... 13|
|1.2.1 生成ECC P256 临时密钥对................................................. 13|
|1.2.2 删除ECC P256 临时密钥对................................................. 13|
|1.2.3 临时密钥对ECDH 密钥交换运算.......................................... 13|

- - 3 

北京信长城科技发展有限公司 

网址:www.i-wall.cn 

密级: 公开/ 一般/ 保密 

|1.2.4 ECC 公钥编码.................................................................... 14|
|---|
|1.2.5 ECC 公钥解码.................................................................... 14|
|2 参数说明.............................................................................................. 14|
|2.1 userId......................................................................................... 14|
|2.2 PIN ............................................................................................. 15|
|3 错误码................................................................................................. 15|

- 4 

- 

北京信长城科技发展有限公司 

网址:www.i-wall.cn 

密级: 公开/ 一般/ 保密 

## 1 ArkTS 接口定义 

#### 1.1 基础接口 

### 1.1.1 获取版本号 

接口原型 public getVersion(): string 功能描述 获取har 库版本信息 参数 返回值 版本号 

### 1.1.2 注册授权码 

接口原型 public registerLicense(license: string): number 功能描述 注册授权码 参数 license [IN] 授权码 返回值 0 成功/ 非0 失败,返回错误码。 备注 接口内部需要获取context,如果无法获取context 抛出异常 

### 1.1.3 初始化SDK 

接口原型 public initSDK(uuid: string): number 功能描述 初始化SDK 参数 uuid [IN] 设备标识信息 返回值 0 成功/ 非0 失败,返回错误码。 备注 接口内部需要获取context,如果无法获取context 抛出异常 

北京信长城科技发展有限公司 

网址:www.i-wall.cn 

密级: 公开/ 一般/ 保密 

### 1.1.4 初始化证书链 

接口原型 public initCertificates(oscp_chains: string[], ca_chains: string[]): number 功能描述 初始化证书链,ca_chains 为必传项 参数 ocsp_chains [IN] OCSP 证书链 ca_chains [IN] CA 证书链 

返回值 0 成功/ 非0 失败,返回错误码。 

### 1.1.5 生成CSR 

接口原型 public generateCSR(userid: string, pin: string, alg: PublicKeyAlgorithm, mod_len: number, subjectInfo: SubjectInfo): string 功能描述 生成证书请求CSR 报文 

userid [IN] 用户标识 pin [IN] 用户PIN 码 alg [IN] 算法类型 参数 mod_len [IN] 算法模长 subjectInfo [IN] 证书主题信息 

返回值 成功返回CSR 报文,失败返回undefined。 

### 1.1.6 私钥签名 

接口原型 public sign(userid: string, pin: string, data: Uint8Array, 

- - 6 

北京信长城科技发展有限公司 

网址:www.i-wall.cn 

密级: 公开/ 一般/ 保密 

alg: SignatureAlgorithm): Uint8Array | undefined 

功能描述 私钥签名 参数 userid [IN] 用户标识 pin [IN] 用户PIN 码 data [IN] 待签名数据 alg [IN] 签名算法 

返回值 成功返回签名值,失败返回undefined。 

### 1.1.7 证书验签 

接口原型 public verifyByCertificate(data: Uint8Array, signature: Uint8Array, certificate: Uint8Array,alg: SignatureAlgorithm) 功能描述 证书验签 参数 data [IN] 待验签数据 signature [IN] 签名值 certificate [IN] 验签证书 alg [IN] 签名算法 

返回值 true 验签成功/ false 验签失败。 

### 1.1.8 证书链验证 

接口原型 public certsCheckWithChain(certificates: Uint8Array[]): number[] | undefined 功能描述 离线证书链验证 参数 certificates [IN] 待验证证书 

北京信长城科技发展有限公司 

网址:www.i-wall.cn 

密级: 公开/ 一般/ 保密 

返回值 

成功返回验证结果(状态0 表示证书有效,非0 表示证书失效), 失败返回undefined。 

### 1.1.9 非对称加密(证书) 

接口原型 public asymmEncrypt(certificate: Uint8Array, plain: Uint8Array): Uint8Array | undefined 功能描述 使用公钥证书进行非对称算法加密数据 参数 certificate [IN] 公钥证书 plain [IN] 明文数据 

返回值 成功返回加密后的密文,失败返回undefined。 

### 1.1.10 非对称解密 

接口原型 public asymmDecrypt(userid: string, pin: string, cipher: Uint8Array): Uint8Array | undefined 功能描述 使用私钥进行非对称算法解密数据 参数 userid [IN] 用户标识 pin [IN] 用户PIN 码 cipher [IN] 密文数据 

返回值 成功返回解密后的明文,失败返回undefined。 

### 1.1.11 对称加解密 

接口原型 public symmCompute(key: Uint8Array, ivec: Uint8Array, input: 

- - 8 

北京信长城科技发展有限公司 

网址:www.i-wall.cn 

密级: 公开/ 一般/ 保密 

Uint8Array, alg: SymmAlgorithm, 

enc: boolean): Uint8Array | undefined 

功能描述 对称加解密算法的密码运算 参数 key [IN] 对称密钥 ivec [IN] 初始化向量 明文数据(加密)/密文 input [IN] 数据(解密) 加密模式(ECB、CBC、 alg [IN] CTR) enc [IN] true 加密/false 解密 

返回值 成功返回密文数据(加密)/明文数据(解密),失败返回undefined。 

### 1.1.12 对称算法扩展 

接口原型 public symmExCompute(key: Uint8Array, nonce: Uint8Array, aad: Uint8Array, input: Uint8Array, alg: SymmExAlgorithm, enc: boolean): Uint8Array | undefined 

功能描述 对称加解密算法的密码运算 参数 key [IN] 对称密钥 nonce [IN] 初始化向量 aad [IN] 附加数据 明文数据(加密)/密文 input [IN] 数据(解密) alg [IN] 加密模式(GCM) enc [IN] true 加密/false 解密 

返回值 成功返回密文数据(加密)/明文数据(解密),失败返回undefined。 

9 

- 

- 

北京信长城科技发展有限公司 

网址:www.i-wall.cn 

密级: 公开/ 一般/ 保密 

### 1.1.13 CMAC 运算 

接口原型 public cmacCompute(key: Uint8Array, input: Uint8Array): Uint8Array | undefined 功能描述 CMAC-AES 运算 参数 key [IN] AES 密钥 input [OUT] 输入数据 

返回值 成功返回CMAC 值,失败返回undefined。 

### 1.1.14 写全局文件 

接口原型 public writeFile(filename: string, data: Uint8Array): number 功能描述 写全局文件 filename [IN] 文件名 参数 data [IN] 待写入数据 返回值 0 成功/ 非0 失败,返回错误码。 

### 1.1.15 读全局文件 

接口原型 public readFile(filename: string): Uint8Array | undefined 功能描述 读取全局文件 参数 filename [IN] 文件名 

返回值 成功返回读取的文件内容,失败返回undefined。 

- 10 

- 

北京信长城科技发展有限公司 

网址:www.i-wall.cn 

密级: 公开/ 一般/ 保密 

### 1.1.16 删全局文件 

接口原型 public delFile(filename: string): number 功能描述 删全局文件 参数 filename [IN] 文件名 

返回值 0 成功/ 非0 失败,返回错误码。 

### 1.1.17 写用户文件 

接口原型 public writeUserFile(userid: string, filename: string, data: Uint8Array): number 功能描述 写用户文件 参数 userid [IN] 用户标识 filename [IN] 文件名 data [IN] 待写入数据 

返回值 0 成功/ 非0 失败,返回错误码。 

### 1.1.18 读用户文件 

接口原型 public readUserFile(userid: string, filename: string): Uint8Array | undefined 功能描述 读用户文件 参数 userid [IN] 用户标识 filename [IN] 文件名 

返回值 成功返回读取的文件内容,失败返回undefined。 

- 11 

- 

北京信长城科技发展有限公司 

网址:www.i-wall.cn 

密级: 公开/ 一般/ 保密 

### 1.1.19 删用户文件 

接口原型 public delUserFile(userid: string, filename: string): number 功能描述 删除用户文件 参数 userid [IN] 用户标识 filename [IN] 文件名 

返回值 0 成功/ 非0 失败,返回错误码。 

### 1.1.20 清除用户文件 

接口原型 public clearUserFiles(userid: string): number 功能描述 清除用户文件 参数 userid [IN] 用户标识 filename [IN] 文件名 

返回值 0 成功/ 非0 失败,返回错误码。 

### 1.1.21 关闭释放SDK 

接口原型 public destroySDK(): number 功能描述 关闭释放SDK 参数 返回值 0 成功/ 非0 失败,返回错误码。 

- 12 

- 

北京信长城科技发展有限公司 

网址:www.i-wall.cn 

密级: 公开/ 一般/ 保密 

#### 1.2 扩展接口 

### 1.2.1 生成ECC P256 临时密钥对 

接口原型 public eccP256GenTempKeyPair(): Uint8Array | undefined 功能描述 生成ECC P256 临时密钥对 参数 返回值 0 成功/ 非0 失败,返回错误码。 

### 1.2.2 删除ECC P256 临时密钥对 

接口原型 public eccP256DelTempKeyPair(): number 功能描述 删除ECC-P256 临时密钥对 

参数 

返回值 0 成功/ 非0 失败,返回错误码。 

### 1.2.3 临时密钥对ECDH 密钥交换运算 

接口原型 public eccP256CalECDH(sharedPublicKey: Uint8Array): ECDHInfo | undefined 功能描述 临时密钥对ECDH 密钥交换运算 参数 sharedPublicKey [IN] 对方ECC-P256 公钥 (DER 编码) 

返回值 0 成功/ 非0 失败,返回错误码。 

- 13 

- 

北京信长城科技发展有限公司 

网址:www.i-wall.cn 

密级: 公开/ 一般/ 保密 

### 1.2.4 ECC 公钥编码 

接口原型 public eccEncodePub2Der(alg: PublicKeyAlgorithm, x: Uint8Array, y: Uint8Array): Uint8Array | undefined 功能描述 ECC 公钥编码,从04+X+Y 的二进制格式编码为DER 格式 参数 alg [IN] ECC 公钥算法类型 x [IN] X 坐标的大数 y [IN] Y 坐标的大数 

返回值 成功返回DER 编码的公钥,失败返回undefined。 

### 1.2.5 ECC 公钥解码 

接口原型 public eccDecodeDer2Pub(derPublicKey: Uint8Array): Uint8Array | undefined 功能描述 ECC 公钥解码,从DER 编码解析到04+X+Y 的二进制格式 参数 derPublicKey [IN] DER 编码的公钥 返回值 成功返回二进制的公钥(04+X+Y),失败返回undefined。 

## 2 参数说明 

#### **2.1 userId** 

类型:字符串 

定义:每个唯一的 userId 可以用于管理一个密钥对及证书,方便通过 userId 关 联索引指定的证书或者密钥对; 

说明:无。 

北京信长城科技发展有限公司 

网址:www.i-wall.cn 

密级: 公开/ 一般/ 保密 

#### **2.2 PIN** 

###### 类型:字符串 

定义:密钥对(私钥)的生命周期管理,需要设置 PIN 进行身份校验管理; 说明:无。 

## 3 错误码 

|错误类型|错误码|错误描述|
|---|---|---|
|SVKD_ERR_OK|0x00000000|成功|
|SVKD_ERR_FAIL|0x0D000001|失败|
|SVKD_ERR_KEYPAIR_BROKEN|0x0D000002|密钥对损坏|
|SVKD_ERR_INVALIDPARAMERR|0x0D000006|无效的参数|
|SVKD_ERR_CONFIG_LOAD_FAIL|0x0D000007|配置文件加载失败|
|SVKD_ERR_BUFFER_TOO_SMALL|0x0D000020|缓存空间不足|
|SVKD_ERR_PIN_INCORRECT|0x0D000024|PIN 错误|
|SVKD_ERR_PIN_LOCKED|0x0D000025|PIN 锁定|
|SVKD_ERR_PIN_INVALID|0x0D000026|PIN 无效|
|SVKD_ERR_PIN_LEN_RANGE|0x0D000027|PIN 长度错误|
|SVKD_ERR_PIN_MODE_WITH_SPLIT|0x0D000028|PIN 模式不匹配|
|SVKD_ERR_PIN_MODE_WITH_THRESHOLD|0x0D000029|PIN 模式不匹配|
|SVKD_ERR_CONTAINER_EXISTS|0x0D00002C|密钥容器已存在|
|SVKD_ERR_CONTAINER_NOT_EXISTS|0x0D00002E|密钥容器不存在|
|SVKD_ERR_SDK_NOT_INITIALIZED|0x0D000030|SDK 未初始化|
|SVKD_ERR_FILE_NOT_EXISTS|0x0D000031|文件不存在|
|SVKD_ERR_FILE_ALREADY_EXIST|0x0D000032|文件已存在|
|SVKD_ERR_FILE_OPERATION_FAIL|0x0D000033|文件操作失败|
|- 1 SVKD_ERR_FILE_HASH_ERROR|- 5 0x0D000034|文件完整性校验失|

北京信长城科技发展有限公司 

网址:www.i-wall.cn 

密级: 公开/ 一般/ 保密 

|||级: 公开/ 一般/ 保密 败|
|---|---|---|
|SVKD_ERR_ATTR_NOT_FOUND|0x0D000035|容器属性不存在|
|SVKD_ERR_ASN1_PARSE_FAIL|0x0D000061|ASN1 解析失败|
|SVKD_ERR_VERIFY_PROTOCOL_FAIL|0x0D000062|验签报文签名失败|
|SVKD_ERR_EXT_RSA_SIGN_ERR|0x0D000063|RSA 签名失败|
|SVKD_ERR_EXT_RSA_VERIFY_ERR|0x0D000064|RSA 验签失败|
|SVKD_ERR_EXT_ECC_SIGN_ERR|0x0D000065|ECC 签名失败|
|SVKD_ERR_EXT_ECC_VERIFY_ERR|0x0D000066|ECC 验签失败|
|SVKD_ERR_EXT_SM2_SIGN_ERR|0x0D000067|SM2 签名失败|
|SVKD_ERR_EXT_SM2_VERIFY_ERR|0x0D000068|SM2 验签失败|
|SVKD_ERR_EXT_RSA_ENCRYPT_ERR|0x0D000069|RSA 加密失败|
|SVKD_ERR_EXT_RSA_DECRYPT_ERR|0x0D00006A|RSA 解密失败|
|SVKD_ERR_EXT_ECC_ENCRYPT_ERR|0x0D00006B|ECC 加密失败|
|SVKD_ERR_EXT_ECC_DECRYPT_ERR|0x0D00006C|ECC 解密失败|
|SVKD_ERR_EXT_SM2_ENCRYPT_ERR|0x0D00006D|SM2 加密失败|
|SVKD_ERR_EXT_SM2_DECRYPT_ERR|0x0D00006E|SM2 解密失败|
|SVKD_ERR_EXT_SYMM_KEY_ERR|0x0D00006F|对称密钥错误|
|SVKD_ERR_CERT_GET_ERR|0x0D000070|证书获取失败|
|SVKD_ERR_CERT_FORMAT_ERR|0x0D000071|证书格式错误|
|SVKD_ERR_CERT_PASSWORD_ERR|0x0D000072|P12 证书密码错误|
|CRYPTO_ERR_INVALID_KEY_SIZE|0x0D000080|无效的密钥长度|
|CRYPTO_ERR_INVALID_INPUT|0x0D000081|无效的数据输入|
|CRYPTO_ERR_INVALID_INPUT_LENGTH|0x0D000082|无效的数据长度|
|CRYPTO_ERR_BUFFER_TOO_SMALL|0x0D000083|缓存空间不足|
|SVKD_ERR_CHANGE_PIN_FAIL|0x0D00010F|修改PIN 失败|
|SVKD_GET_PIN_INFO_ERR|0x0D000110|获取PIN 提示失败|
|SVKD_VERIFY_PIN_ERR|0x0D000111|验证PIN 失败|
|SVKD_UNBLOCK_PIN_ERR|0x0D000112|解锁PIN 失败|

- - 16 

北京信长城科技发展有限公司 

网址:www.i-wall.cn 

密级: 公开/ 一般/ 保密 

|SVKD_CERT_PARSE_ERROR|0x0D020001|证书解析失败|
|---|---|---|
|SVKD_CERTPATH_LOAD_ERROR|0x0D020002|证书链加载失败|
|SVKD_CERT_ALGOR_GET_ERROR|0x0D020003|证书算法获取失败|
|SVKD_CERT_NOT_EXIT|0x0D020004|证书不存在|
|SVKD_CERT_TIME_ERROR|0x0D020005|证书时间错误|
|SVKD_CRL_LAST_UPDATE_FIELD|0x0D020006|CRL 最后更新时间 错误|
|SVKD_CRL_NEXT_UPDATE_FIELD|0x0D020007|CRL 下次更新时间 错误|
|SVKD_CERT_SIGN_VERIFY_FIELD|0x0D020008|证书签名验证失败|
|SVKD_CERT_HASBEEN_REVOKED|0x0D020009|证书已吊销|
|SVKD_CHECK_OVER_MAX_COUNT|0x0D020010|批量查询数量限制|
|SVKD_OCSP_SIGN_VERIFY_FIELD|0x0D020011|OCSP 响应结果验签 失败|
|SVKD_OCSP_RESPONSE_STATUS_ERR|0x0D020012|OSCP 响应结果状态 异常|

- - 17 

北京信长城科技发展有限公司 

网址:www.i-wall.cn
