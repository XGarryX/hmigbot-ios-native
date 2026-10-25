ESI 科蓝软件Harmony 生态安全底座组件 (HarmonyOS SDK) 用户手册 

北京科蓝软件系统股份有限公司 

2024 年 04 月 3 日 

### 文档修改记录 

|版本 内容|编写时间|编写|审核|
|---|---|---|---|
|1.0 新建|2024-04-3|吕宝鹏|曲正平|

#### 版权申明: 

本文档的版权属于北京科蓝软件系统股份有限公司,任何人或组织未经许可, 不得擅自修改、拷贝或以其它方式使用本文档中的内容。 

## 目 录 

|一、引言......................................................................................................................... 1|
|---|
|1.1编写目的........................................................................................................... 1|
|1.2背景知识及参考资料....................................................................................... 1|
|1.3使用环境........................................................................................................... 1|
|二、控件概述................................................................................................................. 2|
|2.1系统构成........................................................................................................... 2|
|2.2功能特点........................................................................................................... 2|
|2.3技术特点........................................................................................................... 2|
|2.4接口描述........................................................................................................... 2|
|2.4.1 接口调用............................................................................................... 2|
|三、DevEcoStudio相关设置说明.................................................................................4|
|3.1 SDK文件引入.................................................................................................. 4|
|四、代码示例................................................................................................................. 5|

用户手册 

Harmony ESI 生态安全底座组件 

# 一、引言 

## **1.1** 编写目的 

“Harmony ESI 生态安全底座组件”为鸿蒙生态设备提供可信安全管理,基于可 信设备的 TEE 安全环境,封装满足金融行业安全架构服务能力,包括:可信设备认 证、可信设备指纹、可信时间戳、秘钥协商、设备远程证明、数字信封、设备证书、 国家标准密码算(SM2、SM3、SM4)、加解密、签名验签等可信设备安全基础功能。 

本《用户手册》中将具体介绍组件的 API 使用方式,使开发人员能够快速掌握组 件的使用。 

## **1.2** 背景知识及参考资料 

假定读者对下列技术有一定的理解: 

|技术|有关内容|
|---|---|
|Harmony SDK|Harmony SDK的基本常识|
|ArkTS|ArkTS的基本使用|
|通信|Ability的通信方法(非必须)|
|NAPI|NAPI相关知识(非必须)|

## **1.3** 使用环境 

DevEco Studio 4.0.0 Release(及以上含) 

第 1页 

用户手册 

Harmony ESI 生态安全底座组件 

# 二、控件概述 

## **2.1** 系统构成 

Harmony ESI 生态安全底座组件由 HarmonyOS SDK 与 so 动态库两部分构成: 安全模块——由 C++实现的 so 动态库。 

—— 接口模块 由 ArkTS 实现。 

## **2.2** 功能特点 

- 依托鸿蒙 TEE 可信安全环境。 

- 具备设备可信远程认证、可信生物特征识别、国密算法等基础安全能力。 

## **2.3** 技术特点 

- 支持 SM2、SM3、SM4 等加密算法 

- 支持密码信封形式加密数据 

- 支持 ECDH 密钥协商算法导入密钥 

- 支持为密钥生成证书链校验能力 

- 支持检测出现新增指纹、人脸特征能力 

- 支持对敏感操作进行签名验签能力 

## **2.4** 接口描述 

### **2.4.1** 接口调用 

|接口|说明|
|---|---|
|createEccForAgree: () => string|创建用于协商的ecc密钥,返回ecc公钥|
|importServerKey:(agreePubkey:string,impor tKey:string)=>number;|导入服务端密钥,参数agreePubkey为服务 端用于协商密钥的公钥,importKey为将要 导入的密钥的密文,返回number,0代表成 功,1代表导入失败。|
|encryptionBody: (input:string) => string;|密码信封加密数据,参数input为待加密数 据,返回密文。|

第 2页 

用户手册 

Harmony ESI 生态安全底座组件 

|decryptionBody: (input:string) => string;|解密数据,参数input为待解密数据,返回 明文。|
|---|---|
|register(deviceId: string, phoneNum: string): Promise<Boolean>|注册可信设备,参数deviceId为唯一设备标 识,phoneNum为手机号,返回是否注册成 功。|
|GetSignData(signData: string)|对数据进行签名,参数signData为待签名的 数据。|
|DeviceVerify(phoneNum: string, deviceId: string, publicKey: string, deviceSigned: string, cert: string):boolean|设备远程证明,参数phoneNum为手机号, deviceId为唯一设备号,publicKey为签名公 钥,deviceSigned为签名信息, cert为签名公 钥的证书链,返回证明结果bool值。|
|initFingerVerifyKey(): Promise<string>|初始化指纹认证密钥,用于绑定当前指纹环 境,当指纹出现新增时,进行提示,返回初 始化结果。|
|startFingerVerify(resultCb): Promise<void>|开启指纹认证,参数resultCb为回调函数, 回调结果为指纹认证结果码。|

第 3页 

用户手册 

Harmony ESI 生态安全底座组件 

# 三、DevEcoStudio 相关设置说明 

## **3.1** SDK 文件引入 

- 1、在调用文件中导入 so 库 

import * as cryptoNapi from 'liblib_mtc.so'; 

- 2、在调用的文件中引入 arkts 文件 

import { DeviceTrustService } from '../deviceIdentification/DeviceTrustService' 

第 4页 

用户手册 

Harmony ESI 生态安全底座组件 

# 四、代码示例 

#### **createEccForAgree** 导入协商公钥: 

let eccPub: string = cryptoNapi.createEccForAgree(); 

#### **importServerKey** 导入密钥: 

let importResult = cryptoNapi.importServerKey(enPubKeyEnc, pubKeyEnc); 

#### **encryptionBody** 加密报文: 

let enc: string = cryptoNapi.encryptionBody(JSON.stringify(paramClient)); 

#### **decryptionBody** 解密报文: 

let body = cryptoNapi.decryptionBody(value1.msg) 

#### **initFingerVerifyKey** 初始化指纹认证密钥: 

FingerLoginHuksHelper.initFingerVerifyKey().then((code) => { 

if (listener != undefined) { listener(code) 

} 

}) 

#### **GetSignData** 获取签名信息: 

let sign = await DeviceTrustService.GetSignData(signData) 

#### **startFingerVerify** 开始指纹认证: 

SMFAFingerClient.buildInstance().startFingerVerify((data: string) => { 

if (data == '0') { this.toast("认证成功") } else if (data == "12000007") { this.toast("检测系统指纹变更,是否重新设置!") 

} else { this.toast("错误码:" + data) 

} 

}) 

第 5页
