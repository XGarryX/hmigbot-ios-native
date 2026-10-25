格尔 SMF-SDK 

(HarmonyOS-ArkTS) 

接口规范 

格尔软件股份有限公司 

2024 年 9 月 

声明: 

Copyright ©2024 格尔软件股份有限公司 

版权所有,保留一切权利 

非经本公司书面许可,任何单位和个人不得擅自摘抄、复制本书内容 的部分或全部,并不得以任何形式传播。 

由于产品版本升级或其他原因,本手册内容会不定期进行更新。除非 另有约定,本手册仅作为使用指导,本手册中的所有陈述、信息和建 议不构成任何明示或暗示的担保。 

目录 

1 前言 7 

2 范围 7 

3 规范性引用文件 7 

4 术语及缩略语 8 

4.1 术语表 8 

4.2 缩略语 11 

5 层次模型 12 

5.1 文件结构 12 

5.1.1 目录结构 12 

5.1.2 文件结构说明 13 

5.1.3 接口文件说明 13 

5.2 层次关系 13 

6 数据类型定义 14 

6.1 枚举类型 14 

6.1.1 证书管理模式 14 

6.1.2 证书管理选项 15 6.1.3 证书状态类型 15 6.1.4 认证方式类型 17 6.1.5 摘要算法类型 18 6.1.6 对称算法类型 18 6.1.7 填充模式类型 19 6.1.8 认证方法 19 

# 6.1.9 证书链文件类型 20 

6.1.10 证书项类型 20 

6.1.11 非对称密文格式类型 23 

6.1.12 通用信息类型 23 

6.1.13 非对称算法密钥类型 23 

6.1.14 对称算法密钥模式 24 

6.1.15 Mac 算法类型 24 

6.1.16 全局选项类型 25 

6.1.17 私钥类型 26 

6.1.18 公钥类型 26 

6.1.19 会话密钥分量角色 27 

6.1.20 会话密钥生成方式类型 27 

6.1.21 签名数据项类型 28 

6.1.22 PKCS#7 签名标志 28 

6.1.23 签名格式类型 29 

6.1.24 对称算法密钥类型 29 

6.1.25 Tlcp 证书链标志 29 

6.1.26 证书验证标志 30 

6.1.27 协议选择参数 30 

6.2 数据类型 30 

6.2.1 证书管理配置 30 

6.2.2 证书选项配置 33 

6.2.3 异常信息 35 

6.2.4 商密双向通信客户端参数 36 

6.2.5 商密通信参数 37 

6.2.6 非对称密钥对 38 

7 接口函数 39 

7.1 接口命名规范 39 

7.2 SDK 管理 39 

7.2.1 概述 39 

7.2.2 获取 SDK 版本号 40 

7.2.3 设置全局通用选项 40 

7.2.4 获取通用信息 40 

7.3 密钥管理 41 

7.3.1 概述 41 

7.3.2 构造方法 42 

7.3.3 生成随机数 42 

7.3.4 生成对称密钥 43 

7.3.5 生成外部密钥对 43 

7.3.6 生成内部密钥对 44 

7.3.7 导出公钥 45 

7.3.8 导入会话密钥 45 

7.3.9 获取会话密钥分量 46 

7.3.10 生成会话密钥 47 

# 7.4 证书管理 47 

7.4.1 概述 47 

7.4.2 用户环境初始化 49 

7.4.3 关闭证书管理上下文 49 

7.4.4 设置全局通用选项 50 

7.4.5 证书生命周期管理 50 

7.4.6 获取公钥 ID 57 

7.4.7 验证 PIN 码 58 

7.4.8 修改 PIN 码 58 

7.4.9 导入证书 59 

7.4.10 获取证书信息 59 

7.4.11 清除认证信息 60 

7.4.12 获取额外认证信息 60 

7.4.13 获取证书剩余过期时间 60 

7.4.14 删除当前用户本地证书 61 

7.4.15 认证初始化 61 

7.4.16 认证 62 

7.4.17 导入 pfx 证书 63 

7.4.18 使用本地证书进行初始化 64 

7.4.19 查询所有终端证书 64 

7.4.20 获取证书状态 65 

7.4.21 查询本地所有证书 66 

7.4.22 导出证书 66 

7.4.23 重置 PIN 码 67 

7.4.24 生成 PKCS#10 证书请求 68 

7.5 密钥运算 68 

7.5.1 概述 68 

7.5.2 构造方法 70 

7.5.3 对称算法 71 7.5.4 摘要算法 75 

7.5.5 Mac 计算 77 

7.5.6 公钥加密 77 7.5.7 私钥解密 78 

7.5.8 PKCS#1 签名 79 7.5.9 PKCS#1 验签 81 

7.5.10 PKCS#7 签名 82 

7.5.11 PKCS#7 验签 83 

7.5.12 PKCS#7 验签扩展接口 83 

7.5.13 数字信封加密 84 

7.5.14 数字信封解密 84 

7.5.15 数字信封加密并签名 85 

7.5.16 数字信封验签并解密 86 7.5.17 加密会话密钥并签名 87 7.5.18 解密会话密钥并验签 88 

# 7.5.19 加密业务数据和会话密钥 89 

7.5.20 解密会话密钥和业务数据 90 

7.5.21 协商密钥并使用协商密钥加密 90 

7.5.22 协商密钥并使用协商密钥解密 91 

7.6 工具方法 92 

7.6.1 概述 92 

7.6.2 根据证书链验证证书 93 

7.6.3 公钥格式转换 94 

# 7.6.4 私钥格式转换 94 

7.6.5 解析 PKCS#7 签名数据 95 

7.6.6 SSL 测速 95 

7.6.7 二进制数据转 16 进制字符串 96 

7.7 安全通道 96 

7.7.1 商密 socket 96 

7.7.2 商密 WebSocket 98 

7.7.3 商密 https 99 

7.7.4 商密 axios 101 

8 附录 A 103 

8.1 错误码说明及定义 103 

# 前言 

本文档是基于 ArkTS 开发语言提供的密码开发套件规范文档。 

本接口说明书由格尔软件股份有限公司 ( 以下简称格尔软件 ) 提出并归 口,包含格尔软件股份有限公司的专有商业信息和保密信息。 

接受方同意维护本文档所提供信息的保密性,承诺不对其进行复制, 或向非直接相关的人员公开此信息。对于以下三种信息,接受方不向 格尔公司承担保密责任: 

接受方在接收该文档前,已经掌握的信息 

可以通过与接受方无关的其它渠道公开获得的信息 

可以从第三方,以无附加保密要求方式获得的信息 

本文档适用于 SMF-SDK(ArkTS) : V2.5.4 。 

注:本 SDK 基于方舟编程语言 ArkTS API 12 。 

范围 

本文档密码相关算法应用接口,适用于 SDK 接入人员参考使用。主要 包括: SDK 管理、密钥管理、证书管理、密钥运算、安全通道、工具 方法。 

规范性引用文件 

下列文件对于本文件的应用是必不可少的。凡是注日期的引用文件, 仅注日期的版本适用于本文件。凡是不注日期的引用文件,其最新版 本 ( 包括所有的修改单 ) 适用于本文件。 

表 1 规范性引用 

引用规范 

解释 

时间 

GM/Z 0001-2013 

密码术语 

GM/T 0016-2012 

智能密码钥匙密码应用接口规范 

GM/T 0120-2022 

基于云计算的电子签名服务技术实施指南 

GM/T 0110-2021 

密钥管理互操作协议规范 

术语及缩略语 

术语表 

表 2 术语 

术语 定义 

密文 ciphertext 

加密后的数据。 

加密 encryption 

对数据进行密码变换以产生密文的过程。 

解密 decryption 

加密过程对应的逆过程。 

密钥 key 

控制密码算法运算的关键信息或参数。 

数字签名 digital signature 

签名者使用私钥对待签名数据的杂凑值做密码运算得到的结果,该结 果只能用签名者的公钥进行验证,用于确认待签名数据的完整性、签 名者身份的真实性和签名行为的抗抵赖性。 

数字信封 digital envelope 

一种数据结构、包含用对称密钥加密的密文和公钥加密的该对称密 钥。 

证书认证机构 certification authority (CA) 

对数字证书进行全生命周期管理的实体。也称为电子认证服务机构。 

数字证书 digital certificate 

也称公钥证书,由证书认证机构( CA )签名的包含公开密钥拥有者信 息、公开密钥、签发者信息、有效期以及扩展信息的一种数据结构。 按类别可分为个人证书、机构证书和设备证书,按用途可分为签名证 书和加密证书。 

非对称密码算法 / 公钥密码算法 asymmetric cryptographic algorithm/public key 

cryptographic algorithm 

加密和解密使用不同密钥的密码算法。其中一个密钥(公钥)可以公 开,另一个密钥(私钥)必须保密,且由公钥求解私钥是计算不可行 的。 

SM2 算法 SM2 algorithm 

一种椭圆曲线公钥密码算法,其密钥长度为 256 比特。 

RSA 算法 Rivest-Shamir-Adleman algorithm ( RSA ) 

一种基于大整数因子分解问题的公钥密码算法。 

密码杂凑算法 hash algorithm 

又称杂凑算法、密码散列算法或哈希算法。该算法将一个任意长的比 特串映射到一个固定长的比特串,且满足下列三个特性: 

( 1 )为一个给定的输出找出能映射到该输出的一个输入是计算上困 

# 难的; 

( 2 )为一个给定的输入找出能映射到同一个输出的另一个输入是计 算上困难的; 

( 3 )要发现不同的输入映射到同一输出是计算上困难的。 

消息摘要 message digest 

消息经过密码杂凑运算得到的结果。 

杂凑值 hash value 

密码杂凑运算的结果。 

消息鉴别码 message authentication (MAC) 

又称消息认证码,是消息鉴别算法的输出。 

消息鉴别算法 MAC algorithm 

使用密码算法计算消息鉴别码的计算方法,可用于数据完整性的鉴 别。 

MD5 算法 MD5 algorithm 

Message Digest Algorithm 5 一种常用的哈希算法,用于将任意长度 的数据转换为固定长度的哈希值。 

SHA-1 算法 secure hash algorithm (SHA) 

一种密码杂凑算法,其输出为 160 比特。 

SHA-256 算法 

一种密码杂凑算法,其输出为 256 比特。 

SM3 算法 SM3 algorithm 

一种密码杂凑算法,其输出为 256 比特。 

对称密码算法 symmetric cryptographic algorithm 

# 加密和解密使用相关密钥的密码算法。 

分组密码算法 block cipher algorithm 

将输入数据划分成固定长度的分组进行加解密的一类对称密码算法。 

对称密钥 secret key 

用于对称密码算法的密钥。 

会话密钥 session key 

在一次会话中使用的数据加密密钥 

DES 算法 Data Encryption Standard 

一种使用对称密钥加密的块算法, 1977 年被美国联邦政府的国家标准 局确定为联邦资料处理标准( FIPS ),并授权在非密级政府通信中使 用。 

3-DES 算法 Triple Data Encryption Algorithm 

三重数据加密算法。相当于是对每个数据块应用三次 DES 加密算法 

AES 算法 Advanced Encryption Standard 

高级加密标准( Advanced Encryption Standard ),是美国 NIST 在 2001 年发布的,旨在代替 DES 称为广泛使用的标准。 AES 是一种对称 分组密码算法,分组长度 128 位。 

AES-128 

AES-128 是 AES 算法的一种,采用 128 位的密钥长度和块大小 

AES-256 

AES-256 是 AES 算法的一种,采用 256 位的密钥长度和 128 位的数据块 大小。 

SM4 算法 SM4 algorithm 

一种国家商用密码分组加密算法,分组长度为 128 比特,密钥长度为 128 比特 

电码本工作模式 electronic codebook operation mode (ECB) 

分组密码算法的一种工作模式,其特征是将明文分组直接作为算法的 输入,对应的输出作为密文分组。 

密文分组链接工作模式 cipher block chaining operation mode (CBC) 

分组密码算法的一种工作模式,其特征是将当前的明文分组与前一密 文分组进行异或运算后再进行加密得到当前的密文分组。 

输出反馈工作模式 output feedback operation mode (OFB) 

用分组密码算法构造序列密码的一种工作模式,其特征是,将算法当 前时刻输出的若干比特与明文逐比特异或得到密文,同时算法当前时 刻的输出作为算法下一时刻的输入。 

密文反馈工作模式 cipher feedback operation mode (CFB) 

用分组密码算法构造序列密码的一种工作模式。其特征是,使用分组 算法当前输出的若干比特,与明文逐比特异或得到密文,该密文同时 更新算法下一时刻的输入序列。 

计数器工作模式 counter operation mode(CTR) 

用分组密码算法构造序列密码的一种工作模式。其特征是,使用计数 器的值作为算法的输入序列进行分组运算,将运算输出的若干比特与 明文逐比特异或得到密文,然后对计数器作增量或者减量运算作为算 法下一时刻的输入序列。 

The Galois Counter Mode of Operation (GCM) 

一种可鉴别的加密机制。 

密钥管理 key management 

根据安全策略,对密钥的产生、分发、存储、使用、更新、归档、撤 销、备份、恢复和销毁等密钥全生存周期的管理。 

密钥管理系统 key management system 

实现密钥管理功能的系统。 

签名验签服务器 signature verification server 

用于服务端的,为应用实体提供基于 PKI 体系和数字证书的数字签 名、验证签名等运算功能的服务器,保证关键业务信息的真实性、完 整性、不可否认性。 

用户 PIN user PIN 

用户的个人密码,为 ASCII 字符串 

缩略语 

表 3 缩略语 

缩略语 

解释 

3DES 

三重 DES 加密算法 

AES-128 

采用 128 位的密钥长度和块大小的 AES 对称算法 

AES-256 

采用 256 位的密钥长度和 128 位的数据块大小的 AES 对称算法 

CA 

证书认证机构 (certification authority) 

CBC 

密码分组链接模式 (cipher block chaining) 

CFB 

密文反馈模式 (cipher feedback) 

CTR 

# 计数器工作模式 (counter) 

# DER 

识别名编码规则,为每一个 ASN.1 类型定制唯一的编码方案 

DES 

使用对称密钥加密的块算法 (Data Encryption Standard) 

DN 

可识别名 (distinguished name) 

ECB 

电码本模式 (electronic code book) 

GCM 

the Galois Counter Mode of Operation 

HMAC 

带密钥的杂凑算法 (keyed-hash message authentication code) 

IV 

初始化向量 / 值 ( initialization vector/initialization value) 

KMS 

密钥管理系统 (key management system) 

MAC 

消息鉴别码 (message authentication) 

MD5 

杂凑算法 (Message Digest Algorithm 5) 

OFB 

# 输出反馈模式 (output feedback) 

# PKCS#1 

公钥密码使用标准系列规范中的第 1 部分,定义 RSA 公开密钥算法加 密和签名机制 (the Public-Key Cryptography Standard Part 1) 

PKCS#7 

公钥密码使用标准系列规范中的第 7 部分,描述一种利用从口令派生 出来的安全密钥加密字符串的方法 (the Public-Key Cryptography Standard Part 7) 

RSA 

RSA 算法 (Rivest-Shamir-Adleman algorithm) 

SDK 

软件开发工具包 (Software Development Kit) 

SHA-1 

SHA-1 算法 (secure hash algorithm-1) 

SHA-256 

SHA-256 算法 (secure hash algorithm-256) 

层次模型 

文件结构 

# 目录结构 

SMF-SDK-Harmony-2.5.4-ArkTS.zip -- SDK 发布包 (名称以实际提取 的包名为准) 

`├──` smf.har -- 用于集成开发的 har 包 

`├──` smf_harmony_demo.zip -- 使用示例 

`├──` readme.md -- 说明文档 

`└──` changelog.md -- 更新记录 

文件结构说明 

表 4 SDK 文件结构 

目录 文件 说明 根目录 smf.har 对外发布的 har 包 smf_harmony_demo.zip SDK 功能演示源码 

readme.md 说明文档 

changelog.md SDK 更新内容记录 

数据类型定义 详细数据定义可以联系我司获取。 接口函数 接口命名规范 

SDK 部分接口同时提供了异步和同步形式,异步接口通常会有联网耗 时操作,为避免阻塞主线程,建议使用异步接口。异步接口 以 “Async” 结尾,接口内部新开了一个线程执行。 

SDK 管理 

概述 

类名: SMFManager 

SDK 管理主要是通过类 SMFManager 获取 SDK 的版本号、全局选项、 获取通用信息等操作。 

表 39 SDK 管理类 SMFManager 接口 

函数名称 

功能 

getVersion 

获取 SDK 的版本号 

setOption 

设置全局通用选项 

getInfo 

获取通用信息 

获取 SDK 版本号 

函数原型 

public getVersion(): string 

功能描述 

获取 SDK 版本号。 

参数 

无 

返回值 

String: 版本号 

异常 

SMFException 。 

备注 无。 示例 

smfManager.getVersion() 

设置全局通用选项 函数原型 

public setOption(option: OptionType, value: OptionValueType): void 

功能描述 设置全局通用选项。 参数 

option 

置选项类型,用于指定具体配置 

value 

具体配置值 返回值 

无。 

异常 

SMFException 。 

备注 

OptionType 仅支持不带 USER 的项,带 USER 的项请使用 certManager 中的 setOption 接口。 

示例 

smfManager.setOption(OptionType.TRACE_ID, 'smf_trace_id_0229') 

# 获取通用信息 

函数原型 

public getInfo(infoType: CommonInfoType): string 

功能描述 

获取通用信息。 

参数 

infoType 类型,指定获取信息的类型 

返回值 

String: 具体的信息值 

异常 

SMFException :类定义见 “6.2.3” 章节 

备注 

无 

示例 

let tranceId = smfManager.getInfo(CommonInfoType.TRACE_ID) 

# 密钥管理 

概述 

类名: KeyManager 

密钥管理主要是通过类 KeyManager 来完成随机数生成、对称 / 非对称 密钥的生成、导出公钥操作。 

构造方法 

函数原型 

public constructor(certManager ? : CertManager) 

功能描述 

构造方法。 

参数 

certManager 

选填参数,证书管理实例,默认使用 CertManager 单例 

返回值 

KeyManager: 密钥管理实例 

异常 

SMFException :类定义见 “6.2.3” 章节 

备注 

推荐使用单例,多用户场景使用 new 创建实例。 

示例 

let certManager = new CertManager() 

// 初始化证书管理 

... 

let keyManager = new KeyManager(certManager) 

其他模块更多接口说明可以联系我司获取。 

证书管理 

概述 

类名: CertManager 

证书管理主要用来对证书整个生命周期进行管理,包括:签发、延 期、废除、生成证书 PKCS#10 请求、导入导出证书等操作。调用证书 管理接口前需要先调用 initSmf 完成用户环境初始化。 

网络耗时接口均提供了异步 Promise 形式。异步接口是在同步接口签 名上附加 “Async” 字符串,接口参数相同,返回 Promise 。 

推荐使用单例,多用户场景使用 new 创建实例。 

其他模块更多接口说明可以联系我司获取。 

密钥运算 

概述 

类名: AlgorithmApi 

密钥运算主要提供非对称加密解密、签名验签、对称加密解密、计算 摘要等功能。使用密钥运算前,需要先初始化 SDK 管理类,密钥运算 依赖 SDK 的上下文环境。网络耗时接口均提供了异步 Promise 形式。 

构造方法 

函数原型 

public constructor(certManager ? : CertManager) 

功能描述 

# 构造方法。 

参数 

certManager 

选填参数,证书管理实例,默认使用 CertManager 单例 返回值 

AlgorithmApi: 密钥运算实例 

异常 

SMFException :类定义见 “6.2.3” 章节 

备注 

推荐使用默认实例,多用户场景使用 new 创建实例。 示例 

let certManager = new CertManager() 

// 初始化证书管理 

... 

let algorithmApi = new AlgorithmApi (certManager) 

工具方法 

概述 

类名: SMFTools 

工具方法主要提供公私钥格式转换、证书链验证、 SSL 测速、二进制 数据转换等功能。 其他模块更多接口说明可以联系我司获取。 

商密 WebSocket 

# 概述 

命名空间: kWebSocket 

本功能可创建商密 WebSocket 。 

使用安全通道双向认证前,需要保证是已发证状态,安全通道依赖 SDK 的本地证书。 

其他模块更多接口说明可以联系我司获取。 

商密 axios 

概述 

命名空间: kHttpAxios 

kHttpAxios 可用于创建商密 axios 实例或适配器。基于 axios adapter 接口实现。创建实例对象和适配器仅是接口层次不同,参数和功能完 全一致。 

使用安全通道双向认证前,需要保证是已发证状态,安全通道依赖 SDK 的本地证书。 

其他模块更多接口说明可以联系我司获取。 

附录 A 

错误码说明及定义 

SDK 上层错误码定义 

表 48 SDK 上层错误码定义 

数据项 

枚举值 

说明 

SDK_NOT_INIT 

1001 

SDK 未初始化 

CERT_MANAGER_NOT_INIT 

1002 证书管理未初始化 ISSUE_CERT_MODE_ERR 1003 发证模式错误 CONVERT_TYPE_ERR 1004 转换类型错误 WRONG_CERT_OPTION 1005 错误的证书操作 NOT_SUPPORT_THE_OPTION 1006 不支持的操作 

其他模块更多错误说明可以联系我司获取。
