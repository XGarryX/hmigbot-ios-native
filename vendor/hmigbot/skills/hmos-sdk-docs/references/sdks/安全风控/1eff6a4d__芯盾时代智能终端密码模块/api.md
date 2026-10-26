芯盾时代 

GM 产品 

SDK 集成手册 

# 北京芯盾时代科技有限公司 

2022 年 06 月 

修订记录 

版本号 修订人 修订日期 修订描述 

V1.0 

杨航天 

2022.06 

初次创建,产品版本 V1.1 

V1.1 

韩元 

2022.7.14 

客户端 sdk 增加设置渠道密钥接口;服务端优化渠道密钥格式 

目 录 

1. 文档说明 5 

1.1 文档目的 5 

1.2 阅读对象 5 

1.3 基本概念 5 

1.4 密码模块功能说明 5 

1.4.1 客户端加密服务端解密 6 

1.4.2 服务端加密客户端解密 7 

2. 服务端 Java SDK 集成方法 8 

2.1. 集成流程 8 

2.1.1. 初始化 8 

2.1.2. 获取渠道信息方法 8 

2.1.3. 数字信封加密方法 9 

2.1.4. 数字信封解密方法 10 

2.1.5 获取 js 端动态密钥 11 

2.1.6. 服务端本地加密方法 12 

2.1.7. 服务端本地解密方法 12 

2.2. 函数错误码说明 13 

3. 服务端 C SDK 集成方法 13 

3.1. 兼容性说明 13 

3.2.SDK 集成说明 14 

3.2.1.SDK 内容 14 

3.2.2. 集成方法 14 

3.2.3. 使用方法 14 

3.3.SDK 接口 API 详细说明 15 

3.3.1. 国密数字信封相关接口 15 

3.4.SDK 接口错误码说明 19 

3.4.1. 终端侧错误码和操作 19 

4. 安卓客户端 SDK 集成说明 21 

4.1.SDK 集成方法 21 

4.2.SDK 接口 API 详细说明 21 

4.2.1.ApiWrapperForGuomi.initEnv 21 

4.2.2.ApiWrapperForGuomi.setAppKey 22 

4.2.3.ApiWrapperForGuomi.enEncryptByAppKey 22 

4.2.4.ApiWrapperForGuomi.enDecryptByAppKey 23 

4.2.5.ApiWrapperForGuomi.updateSeed 23 

5.iOS 客户端 SDK 集成说明 25 

5.1. 集成 SDK 25 

5.2.SDK 接口 API 详细说明 26 

5.2.1. 初始化 SDK 运行环境接口 26 

5.2.2.[TrusfortGM setAppkey:version:withKeyToken:] 26 

5.2.3.[TrusfortGM enEncryptByAppKey:withData:] 27 

5.2.4.[TrusfortGM enDecryptByAppKey:withData:] 27 

5.2.5.[TrusfortGM setRandomSeed:] 28 

6.WEB 端 SDK 集成文档 29 

6.1. 总体流程 29 

6.2 集成说明 29 

6.2 接口清单 30 

6.2.1.commonEncrypt 30 

6.2.2.commonDecrypt 30 

7.Windows 客户端 C 语言 SDK 集成说明 31 

7.1.SDK 集成方法 31 

7.2.SDK 接口 API 详细说明 31 

7.2.1.initEnv 31 

7.2.2.SetAppKey 31 

7.2.3.enEncryptByAppKey2 32 

7.2.4.enDecryptByAppKey2 33 

7.2.5 xindun_rbg_rseed_update 33 

8.linux 客户端 SDK 集成说明 34 

8.1. 兼容性说明 34 

8.2.SDK 集成说明 35 

8.2.1.SDK 内容 35 

8.2.2. 集成方法 35 

8.2.3. 使用方法 35 

8.3.SDK 接口 API 详细说明 36 

8.3.1. 国密数字信封相关接口 36 

8.4.SDK 接口错误码说明 40 

8.4.1. 终端侧错误码和操作 40 

9.Windows 客户端 JAVA SDK 集成说明 43 

9.1.SDK 集成方法 43 

9.2.SDK 接口 API 详细说明 43 

9.2.1.ApiWrapperForAlgorithmSSE.platform 43 

9.2.2.ApiWrapperForAlgorithmSSE.ResLocationPath 43 

9.2.3.ApiWrapperForAlgorithmSSE.boverwrite 43 

9.2.4.ApiWrapperForAlgorithmSSE.initEnv 43 

9.2.5.ApiWrapperForAlgorithmSSE.setAppKey 44 

9.2.6.ApiWrapperForAlgorithmSSE.getDevinfo 44 

9.2.7.ApiWrapperForAlgorithmSSE.enEncryptByAppKey2 45 

9.2.8.ApiWrapperForAlgorithmSSE.enDecryptByAppKey2 46 

9.2.9.ApiWrapperForAlgorithmSSE.sseRBGRseedUpdate 46 

# 10. 微信小程序客户端 SDK 集成说明 47 

10.1.SDK 集成方法 47 

10.2.SDK 接口 API 详细说明 47 

10.2.1.setAppKey 47 

10.2.2.enEncryptByAppKey2 49 

10.2.3.enDecryptByAppKey2 49 

10.2.4. 状态码说明 50 

文档说明 

# 文档目的 

本文档主要介绍国密产品 SDK 集成方式,为产品集成提供参考。 阅读对象 

国密产品开发者。 

基本概念 

术语名称 

含义 

客户端应用 

需要集成芯盾客户端 SDK 的应用 应用服务器 

与客户端应用配合的后台服务器 

businessID 

业务渠道标识, 32 字节随机字符串。客户端应用与应用服务器需要陪 配置该字段。 

# 渠道密钥 bkey 

为特定 businessID 分配的,用于数字信封加解密的一组密钥集合。 

渠道密钥在客户端主要包含服务端根公钥,通过工具内置与 sdk 中。 

渠道密钥在服务器端主要包含服务端根私钥,由应用服务负责保存, 保存时需要与渠道标识 businessID 和渠道密钥版本 bkey_version 对应 (例如保存到数据库)。 

渠道密钥版本 bkey_version 

渠道密钥对应的版本 

# 密码模块功能说明 

本文提到的国密密码模块,可以实现对金融密码应用客户端、服务器 之间通信报文(或者指定敏感数据)的加密。 

非对称加密算法使用国密 SM2 ,对称加密算法使用国密 SMS4 ,完整 性校验基于国密 SM3 摘要算法。 

客户端加密服务端解密 

1 )针对需要使用国密算法加密的敏感数据,客户端直接调用芯盾 sdk 提供的数据加密接口,传入待加密的敏感数据明文 plain 与 businessID 。 

2 )芯盾 sdk 生成随机因子 seed 并保存,派生出会话密钥 wkey ,使用 wkey 加密明文数据,同时计算 hmac 值。使用渠道密钥 bkey_client 加 密 seed 。 

- 3 )将 seed 密文,数据密文, hamc 值拼接成 sToken 返回给客户端。 

客户端将密文 sToken 发送到业务服务器端。 

- 5 )业务服务器收到请求后,根据业务上下文,得知需要调用芯盾服 务端 sdk 的数字信封解密接口,首先需要调用芯盾服务端 sdk 接口获取 

渠道标识 businessID 与密钥版本 bkey_version 。 

- 6 )服务端 sdk 返回渠道标识 businessID 与密钥版本 bkey_version 。 

- 7 )应用服务根据渠道标识与密钥版,获取渠道密钥 bkey_server 。 

8 )应用服务将渠道密钥 bkey_server ,密文 sToken ,作为参数,调用 芯盾服务端 SDK 解密。 

9 )芯盾服务端 sdk 使用 bkey_server 解密 seed ,派生出会话密钥 wkey ;然后使用 wkey 验证 sToken 内密文并解密。 

10 )解密成功则返回数据原始明文 plain ,否则返回相应错误码。 

- 11 )业务服务器得到明文数据 plain 后,继续根据业务逻辑进行处理。 服务端加密客户端解密 

1 , 2 )客户端发送业务请求,并附带一段数字信封加密的数据密文; 服务端收到客户端请求,并执行相应的业务处理。 

3 )业务服务器根据业务上下文,得知需要调用芯盾服务端 sdk 的加密 接口,首先需要调用芯盾服务端 sdk 接口获取渠道标识 businessID 与密 钥版本 bkey_version 。 

- 4 )服务端 sdk 返回渠道标识 businessID 与密钥版本 bkey_version 。 

- 5 )应用服务根据渠道标识与密钥版,获取渠道密钥 bkey_server 。 

6 )针对服务端需要下发给客户端的敏感数据,为保证安全,需要调 用芯盾服务端 sdk 提供的数据加密接口,传入待加密的明文数据 plain ,对应的渠道密钥 bkey_server ,以及上行的密文。 

7 )芯盾服务端 sdk 接口使用上行报文中的 seed ,派生出会话密钥 wkey 。然后使用 wkey 加密数据明文 plain ,生成密文数据,使用 bkey_server 中服务端私钥对报文签名,将密文与签名值拼接成 sToken 。 

- 8 )服务端 sdk 将 sToken 返回给业务服务。 

- 9 )业务服务器将敏感数据密文 sToken 下发到指定的客户端。 

10 )客户端收到服务器下发的密文后,根据业务上下文,得知需要调 用芯盾 SDK 的数据解密接口,传入 sToken ,请求芯盾 SDK 解密。 

11 )芯盾 sdk 使用缓存 seed ,派生出会话密钥 wkey ;使用渠道密钥 bkey_client 对报文验签,验签失败返回错误码,成功后使用 wkey 对 sToken 解密,解密成功则返回原始明文 plain ,否则返回相应错误 码。 

12 )将明文数据返回给客户端,客户端得到明文数据 plain 后,继续根 据业务逻辑进行处理。 

# 4. 鸿蒙客户端 SDK 集成说明 

# 4.1.SDK 集成方法 

Harmony SDK 包含如下内容: 

-har 文件: trusfort-gm-xxx.har 

4.1.1 集成方法 

1. 将 har 文件复制到应用代码工程源目录(有自定义依赖库路径的,也 可复制到自定义路径内) 

2. 打开应用的 oh-package.json5 文件,设置三方包依赖,配置示例如 下: 

"dependencies": { 

"trusfort": "file:./libs/trusfort-gm-x.x.x.har" 

} 

3. 配置完成后示例如下(自定义依赖库路径为 libs ): 

4.1.2 调用方法 

接口类: TrusfortApiForGm 

导入模块: import { TrusfortApiForGm } from 'trusfort' 

# 4.2.SDK 接口 API 详细说明 

4.2.1.ApiWrapperForGm.initEnvForTrusfort 

功能描述:本方法需要在加密和解密接口之前调用,建立起 SDK 运行 需要的环境,否则加解密接口返回错误。 

API 方法原型: 

Promise<string> 

注意:如果集成了芯盾多个产品能力调用一次接口即可 , 根据产品能力 设置相应参数。 

参数: 

参数名 

类型 

必填 

说明 

InitTrusfortEnvParameter 

string 

是 

芯盾为客户应用服务器分配的 APPID 

context 

context 

是 

# 应用上下文 

AbilityStage :this.context.getApplicationContext() 

自定义组件 :getContext().getApplicationContext() 

InitTrusfortEnvParameter 参数: 

参数 

必选 

类型 

描述 

appid 

是 

string 

由芯盾分配,授权当前 app 。注意如果集成了芯盾多个产品能力 appid 最好保持统一。 

返回值: 

类型 

说明 

string 

json 格式,需要解析对应的 key 

“status”: 状态码。 0- 完成 

测试 businessId : 786495cad1024fb99462be2389cbbc08 

示例代码: 

import AbilityStage from '@ohos.app.ability.AbilityStage'; import type Want from '@ohos.app.ability.Want'; 

export default class MyAbilityStage extends AbilityStage { onCreate(): void { 

// 应用的 HAP 在首次加载的时,为该 Module 初始化操作 

let initParmas = new InitTrusfortEnvParameter(); initParmas.appid = "com.example.demo" 

initEnvForTrusfort(initParmas , this.context.getApplicationContext()).then((data)=>{ console.log(data); 

}).catch((err: Error) => { 

console.info(`initEnvForTrusfort err: ${JSON.stringify(err)}`) 

}); 

...... 

} 

} 

import AbilityStage from '@ohos.app.ability.AbilityStage'; import type Want from '@ohos.app.ability.Want'; 

export default class MyAbilityStage extends AbilityStage { 

onCreate(): void { 

// 应用的 HAP 在首次加载的时,为该 Module 初始化操作 

let initParmas = new InitTrusfortEnvParameter(); initParmas.appid = "com.example.demo" 

initEnvForTrusfort(initParmas , this.context.getApplicationContext()).then((data)=>{ console.log(data); 

}).catch((err: Error) => { 

console.info(`initEnvForTrusfort err: ${JSON.stringify(err)}`) 

}); 

...... 

} 

} 

# 4.2.2.ApiWrapperForGm.setAppKey 

功能描述:设置 appkey 。 

API 方法原型: 

setAppKey(businessId:string,keyVersion:string,keyToken:string): string; 

输入参数 参数 必选 类型 

描述 

businessId 

是 

String 

业务 ID ,由芯盾分配,测试 businessId : 786495cad1024fb99462be2389cbbc08 

keyVersion 

是 

String 

渠道密钥版本,测试 keyVersion : 001 

keyToken 

是 

String 

# 渠道密钥,测试值见下文 

测试 keyToken: 

GoHUqRYQiT5b2L/ 

jF2kvH4If5vI/ 

I+RnzE0klXkQpmJYXVmXWJkviKRKb321nx+2O4Nk+ufN4/ 

# API 方法返回值 

参数 

类型 描述 

status 

String 

状态码, 0 :操作成功 

4.2.3.ApiWrapperForGm.enEncryptByAppKey 

功能描述:使用 appKey 进行信封加密。 

API 方法原型: 

enEncryptByAppKey(businessId:string,inData:ArrayBuffer): string; 

输入参数 

参数 

必选 

类型 

描述 

businessId 

是 

String 

业务 ID ,由芯盾分配,测试 businessId : 786495cad1024fb99462be2389cbbc08 

inData 

是 

ArrayBuffer 

待加密数据 

API 方法返回值 

参数 

类型 

描述 

status 

String 

状态码, 0 :操作成功 

cipher 

String 

密文 

示例代码: 

const encoder = new util.TextEncoder(); 

let buffer = new ArrayBuffer(this.input_rawdata.length); 

let dest = new Uint8Array(buffer); 

let result= new Object(); 

result = encoder.encodeIntoUint8Array(this.input_rawdata, dest); 

let data = TrusfortApiForGm.enEncryptByAppKey(this.BUSINESS_ID,buffer); console.info(data) const retmap: Map<string, string> =JSON.parse(data) 

this.message =this.cipherdata = retmap["cipher"] const encoder = new util.TextEncoder(); 

let buffer = new ArrayBuffer(this.input_rawdata.length); 

let dest = new Uint8Array(buffer); 

let result= new Object(); 

result = encoder.encodeIntoUint8Array(this.input_rawdata, dest); 

let data = TrusfortApiForGm.enEncryptByAppKey(this.BUSINESS_ID,buffer); console.info(data) 

const retmap: Map<string, string> =JSON.parse(data) this.message =this.cipherdata = retmap["cipher"] 

4.2.4.ApiWrapperForGm.enDecryptByAppKey 

# 功能描述:解密服务端发来的密文。 

API 方法原型: 

enDecryptByAppKey(businessId:string,cipherdata:string): string; 输入参数 

参数 

必选 

类型 

描述 

businessId 

是 

String 

业务 ID ,由芯盾分配,测试 businessId : 786495cad1024fb99462be2389cbbc08 

encryptedPkt 

是 

String 

密文 

API 方法返回值 

参数 

类型 

描述 

status 

String 

状态码, 0 :操作成功 

data 

String 

解密的明文。 

# 4.2.5.ApiWrapperForGm.updateSeed 

功能描述:设置随机种子。 

API 方法原型: 

updateSeed(rSeed:ArrayBuffer): string; 输入参数 参数 必选 类型 描述 rSeed 是 ArrayBuffer 随机数 API 方法返回值 参数 类型 描述 status String 状态码, 0 :操作成功
