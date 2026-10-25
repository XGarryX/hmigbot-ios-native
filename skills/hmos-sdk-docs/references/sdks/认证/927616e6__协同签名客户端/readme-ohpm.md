> 来源: ohpm 中央仓 README(T1 信源) | 包: `mobileukey` | ohpm 最新版: 4.0.0 | 抓取: 2026-07-16
> 注意: 版本可能比市场快照新,以此为准时核对 CHANGELOG

海泰方圆移动智能终端安全密码模块支持SM2、SM3、SM4算法,采用密钥分割、协同分布式签名技术,能够在移动端实现与硬件Key 相同的功能。该产品由移动终端安全密码模块、海泰密钥管理系统两部分组成,手机端和服务器端各存储部分私钥,协同完成签名和解密操作。可应用于金融、加密通话、移动支付、移动办公、电子合同签署等诸多领域,解决移动端的身份认证、业务数据的完整性、防抵赖等问题,为客户在互联网应用模式下的创新业务提供有效的安全服务支撑。

## 一、SDK使用说明 ##

### 1.1 SDK 文件说明 ###

海泰方圆协同签名  SDK接口文档V1.0 For Harmony OS 是基于鸿蒙系统平台开发的,针对鸿蒙系统提供的一个集成HAR包。我们将提供的压缩包含有以下文件夹:

(1)doc:该文件夹下的内容是开发参考手册。

(2)SDK:该文件夹下的内容是集成包文件。

(3)demo:该文件夹下的内容是使用本 SDK 的Harmony OS示例工程。

1.2 SDK 使用配置

(1).首先将SDK目录文件ble.har放到您的工程目录的某个文件夹下。

(2).使用import导入您需要调用的HAR提供的API函数,即可调用我司提供的功能,具体可参考DEMO。

(3).添加权限,在您工程的模块的文件夹中找到module.json5文件中的requestPermissions节点中添加需要的权限,如截图所示:

## 二、接口说明 ##

### 2.1 设置ip端口 ###

	函数	initServer(serverAddress: string, serverPort: string): number

	参数说明	serverAddress	ip

	serverPort	端口号

	备注		

### 2.2 设置当前设备标识 ###

	函数	initDeviceID(deviceID: string): number

	参数说明	deviceID	设备唯一标识

	备注	

### 2.3 下载证书 ###

	函数	downloadCert(userName: string, pin: string, authCode: string,softCipherDownloadCertCallback: SoftCipherCallback<CertResul>)

	参数说明	userName	用户名

	pin	用户PIN码

	authCode	授权码

	softCipherDownloadCertCallback	回调函数

	备注	

### 2.4 协同签名 

	函数	softCipherDataSign(userName: string, pin: string, privateKey: string, signData: string,softCipherSignDataCallback: SoftCipherCallback<string>)

	参数说明	userName	用户名

	pin	用户PIN码

	privateKey	本地保存的部分私钥

	signData	待签名数据

	softCipherSignDataCallback	回调函数

	备注	

### 2.5 验证签名

	函数	softVerifySignData(signCert: string, origin: string, signature: string)

	参数说明	signCert	签名证书

	origin	原文

	signature	签名结果

	备注	

###  2.6 修改PIN码

	函数	softChangePin(userName: string, oldPin: string, newPin: string,softCipherChangePinCallback: SoftCipherCallback<boolean>)

	参数说明	userName	用户名

	oldPin	原PIN码

	newPin	新PIN码

	softCipherChangePinCallback	回调函数

	备注	

### 2.7 SM2数据加密

	函数	softSm2EncData(data: string, cert: string)

	参数说明	data	待加密数据

	cert	加密证书

	备注	

### 2.8 SM2数据解密 

	函数	softSm2DecData(userName: string, pin: string, privateKey: string, encData: string)

	参数说明	userName	用户名

	pin	用户PIN码

	privateKey	本地保存的部分私钥

	encData	待解密数据

	备注	

### 2.9 SM4加密 

	函数	softSm4EncData(encMod: number, encData: string, encKey: string)

	参数说明	encMod	加密模式ECB,CBC,

	encData	待加密数据

	encKey	私钥

	备注	

### 2.10 SM4解密

	函数	softSm4DecData(decMod: number, decData: string, decKey: string)

	参数说明	decMod	加密模式ECB,CBC,

	decData	待解密数据

	decKey	私钥

	备注	

### 3.1 证书续期申请 

	函数	softCertDelayApply(userName: string,usrPin:string , certNotAfter:string,months:string, softCertDelayApplyCallback: SoftCipherCallback<boolean>)

	参数说明	userName	用户名

	usrPin	用户PIN码

	certNotAfter	证书失效日期

	months	证书续期时间

	softCertDelayApplyCallback	回调函数

	备注	

### 3.2 证书续期状态

	函数	softCertDelayStatus(userName: string, softCertDelayStatusCallback: SoftCipherCallback<number>)

	参数说明	userName	用户名

	softCertDelayStatusCallback	回调函数,60123(表示续期通过),60122(续期状态未审核),60121(不存在续期状态)

	备注	

### 3.3证书续期 

	函数	softCertDelay(userName: string,usrPin:string, softCertDelayCallback: SoftCipherCallback<ResultUpDataCert>)

	参数说明	userName	用户名

	usrPin	用户PIN码

	callback	回调函数

	备注	

## 如何使用ohpm安装 ##

	ohpm i mobileukey
