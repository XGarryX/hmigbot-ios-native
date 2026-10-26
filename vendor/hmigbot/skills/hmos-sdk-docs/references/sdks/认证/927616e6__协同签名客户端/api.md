海泰方圆协同签名 SDK 接口文档 V1.0 For Harmony OS 

修订记录: 

# 修订日期 

版本 

修订内容 撰写人 

2024-12-6 

V1.0 首版创建 

Kent 

目录 海泰方圆协同签名 SDK 接口文档 1 

V1.0 For Harmony OS 1 

一、 SDK 使用说明 3 

1.1 SDK 文件说明 3 

1.2 SDK 使用配置 4 

二、接口说明 5 

2.1 设置 ip 端口 5 

2.2 设置当前设备标识 5 

2.3 下载证书 5 

2.4 协同签名 5 

2.5 验证签名 6 

2.6 修改 PIN 码 6 

2.7 SM2 数据加密 6 

2.8 SM2 数据解密 7 

2.9 SM4 加密 7 

2.10 SM4 解密 7 

3.1 证书续期申请 8 

3.2 证书续期状态 8 

3.3 证书续期 8 

# 一、 SDK 使用说明 

# 1.1 SDK 文件说明 

海泰方圆协同签名 SDK 接口文档 V1.0 For Harmony OS 是基于鸿蒙系 统平台开发的,针对鸿蒙系统提供的一个集成 HAR 包。我们将提供的 压缩包含有以下文件夹: 

doc :该文件夹下的内容是开发参考手册。 

SDK :该文件夹下的内容是集成包文件。 

demo :该文件夹下的内容是使用本 SDK 的 Harmony OS 示例工程。 

# 1.2 SDK 使用配置 

. 首先将 SDK 目录文件 ble.har 放到您的工程目录的某个文件夹下。 

. 使用 import 导入您需要调用的 HAR 提供的 API 函数,即可调用我司提 供的功能,具体可参考 DEMO 。 

. 添加权限 , 在您工程的模块的文件夹中找到 module.json5 文件中的 requestPermissions 节点中添加需要的权限,如截图所示: 

二、接口说明 

# 2.1 设置 ip 端口 

# 函数 

initServer(serverAddress: string, serverPort: string): number 

参数说明 

serverAddress 

ip 

serverPort 

端口号 

备注 

# 2.2 设置当前设备标识 

# 函数 

initDeviceID(deviceID: string): number 参数说明 deviceID 设备唯一标识 备注 

2.3 下载证书 

# 函数 

downloadCert(userName: string, pin: string, authCode: string, 

softCipherDownloadCertCallback: SoftCipherCallback<CertResul>) 

参数说明 

userName 

用户名 

pin 

用户 PIN 码 

authCode 

授权码 

softCipherDownloadCertCallback 

回调函数 

备注 

# 2.4 协同签名 

# 函数 

softCipherDataSign(userName: string, pin: string, privateKey: string, signData: string,softCipherSignDataCallback: SoftCipherCallback<string>) 

# 参数说明 

userName 

用户名 

pin 

用户 PIN 码 

privateKey 

本地保存的部分私钥 

signData 

# 待签名数据 

softCipherSignDataCallback 

回调函数 

备注 

# 2.5 验证签名 

# 函数 

softVerifySignData(signCert: string, origin: string, signature: string) 

参数说明 

signCert 

签名证书 

origin 

原文 

signature 

签名结果 

备注 

# 2.6 修改 PIN 码 

# 函数 

softChangePin(userName: string, oldPin: string, newPin: string, softCipherChangePinCallback: SoftCipherCallback<boolean>) 

参数说明 

userName 用户名 

oldPin 原 PIN 码 

newPin 新 PIN 码 

softCipherChangePinCallback 回调函数 备注 

2.7 SM2 数据加密 

# 函数 

softSm2EncData(data: string, cert: string) 参数说明 

data 

# 待加密数据 

cert 

加密证书 备注 

# 2.8 SM2 数据解密 

# 函数 

softSm2DecData(userName: string, pin: string, privateKey: string, encData: string) 

参数说明 

userName 

用户名 

pin 

用户 PIN 码 

privateKey 

本地保存的部分私钥 

encData 

待解密数据 

备注 

2.9 SM4 加密 

# 函数 

softSm4EncData(encMod: number, encData: string, encKey: string) 参数说明 

encMod 

加密模式 ECB , CBC , 

encData 

待加密数据 

encKey 

私钥 备注 

2.10 SM4 解密 

# 函数 

softSm4DecData(decMod: number, decData: string, decKey: string) 参数说明 

decMod 

加密模式 ECB , CBC , 

decData 

# 待解密数据 

decKey 

私钥 备注 

# 3.1 证书续期申请 

# 函数 

softCertDelayApply(userName: string,usrPin:string , certNotAfter:string,months:string, softCertDelayApplyCallback: SoftCipherCallback<boolean>) 

参数说明 

userName 

用户名 

usrPin 

用户 PIN 码 

certNotAfter 

证书失效日期 

months 

证书续期时间 

softCertDelayApplyCallback 

回调函数 

备注 

# 3.2 证书续期状态 

# 函数 

softCertDelayStatus(userName: string, softCertDelayStatusCallback: SoftCipherCallback<number>) 

参数说明 

userName 

用户名 

softCertDelayStatusCallback 

回调函数, 60123( 表示续期通过 ),60122( 续期状态未审核 ),60121( 不 存在续期状态 ) 

备注 

# 3.3 证书续期 

# 函数 

softCertDelay(userName: string,usrPin:string, softCertDelayCallback: SoftCipherCallback<ResultUpDataCert>) 

参数说明 

userName 

用户名 

usrPin 用户 PIN 码 callback 回调函数 备注
