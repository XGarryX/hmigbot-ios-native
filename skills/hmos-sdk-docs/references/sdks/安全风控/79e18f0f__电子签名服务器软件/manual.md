# **电子签名服务器软件 产品使用说明书** 

### **itrus-esa-2025-1** 

**v1.0** 

#### **北京天威诚信电子商务服务有限公司** 

#### **2025 年1 月** 

#### **文件编制/修订记录** 

|**版本号**|**编制/修订说明**|**编制/修订部门**|**审核人**|**批准人**|**生效日期**|
|---|---|---|---|---|---|
|D/0|新建|研发中心|||2024.12|

北京天威诚信电子商务服务有限公司 总部电话:010-50947500 / 400-666-3999 总部地址:北京市海淀区上地八街7 号院4 号楼4 层 

## **目录** 

|**初始化SDK.............................................................................................................................5**|
|---|
|设置默认ProviderType.............................................................................................................5|
|设置自定义数据库路径...........................................................................................................5|
|设置license...............................................................................................................................5|
|初始化密钥分割配置...............................................................................................................5|
|**生成证书库.............................................................................................................................6**|
|**生成Csr.................................................................................................................................. 6**|
|**安装证书................................................................................................................................ 7**|
|**裸签名验签.............................................................................................................................7**|
|**P7 签名验签........................................................................................................................... 9**|
|**裸加密解密...........................................................................................................................10**|
|**P7 加密解密..........................................................................................................................12**|
|**修改pin 码........................................................................................................................... 13**|
|**对称加解密...........................................................................................................................14**|
|**摘要计算.............................................................................................................................. 16**|
|**证书过滤.............................................................................................................................. 18**|
|**1. 错误码定义.....................................................................................................18**|
|**2. 补充说明.........................................................................................................23**|

###### 北京天威诚信电子商务服务有限公司 

总部电话:010-50947500 / 400-666-3999 总部地址:北京市海淀区上地八街7 号院4 号楼4 层 

|**关于构造方法和对象初始化方法........................................................................................ 23**|
|---|
|**关于对象生命周期............................................................................................................... 23**|
|**关于对象状态的说明........................................................................................................... 24**|

北京天威诚信电子商务服务有限公司 总部电话:010-50947500 / 400-666-3999 总部地址:北京市海淀区上地八街7 号院4 号楼4 层 

##### **初始化SDK** 

### 设置默认 **ProviderType** 

ESACSGlobal.getInstance().setDefaultProviderType(7); 

### 设置自定义数据库路径 

const dbPath = getContext(this).filesDir + "/topnesa.db";
console.log('dbpath : ' + dbPath);
let code =
ESACustomGlobalConfig.getInstance().setDefaultDBPath(dbPath);
if(code !== 0){
this.showResult('setDefaultDBPath',ESACustomGlobalConfig.getInsta
nce());
return;
}

### 设置 **license** 

**private static readonly** demoLicense: string = '' // _TODO:_ 这里输入您 申请的 _license_ 许可字符串 ESACSGlobal.getInstance().setLicense(HomePage.demoLicense); 

### 初始化密钥分割配置 

@State serverAddress:string = 

'http://192.168.100.68:10316/apigate/esa-openapi/openApi' @State permissionAccount:string = 'e46e66c74f594f' @State permissionPassword:string = '0df4a3418bd14123a2d6123cc585acf0' ESAOLGlobalConfig.getInstance().setConfig( **this** .serverAddress, "" **this** .permissionAccount, **this** .permissionPassword, ); 

###### 北京天威诚信电子商务服务有限公司 

5 

总部电话:010-50947500 / 400-666-3999 总部地址:北京市海淀区上地八街 7 号院 4 号楼 4 层 

##### **生成证书库** 

// 构造 ESACertDeviceUnit 实例 

**let** certDU = **new** ESACertDeviceUnit(); **let** ret = certDU.initInstance(); 

**if** (ret !== 0) { **this** .showResult('构造 ESACertDeviceUnit 实例 - initInstance()', certDU) **return** 

} // 创建证书库 ret = certDU.createCertStore( **this** .storeName, **this** .adminPin, **this** .userPin); 

**this** .showResult('创建证书库 - createCertStore()', certDU) 

##### **生成Csr** 

**let** hashAlg: number = HashAlgEnumType[ **this** .hashText] 

// 构造 ESACertStore 实例 

**let** certStore = **new** ESACertStore(); 

**let** ret = certStore.initInstance( **this** .storeName); 

**if** (ret !== 0){ **this** .showResult('构造 ESACertStore 实例 - initInstance()',certStore) **return** 

} 

// login 

ret = certStore.login( **this** .userPin); **if** (ret !== 0){ **this** .showResult('登录证书库 - login()',certStore) **return** 

} // gen csr **let** csr = certStore.genCsr( **this** .subject,asymmAlg,hashAlg); **if** (csr.length === 0) { **this** .showResult('生成 csr - genCsr()',certStore) **return** 

} certStore.logout() **this** .resultText = csr 

申请证书 demo 中采用的是 webService 方式请求证书,在实际项目中可与实施人 员沟通采用例如 http 方式请求证书。 

###### 北京天威诚信电子商务服务有限公司 

6 

总部电话:010-50947500 / 400-666-3999 总部地址:北京市海淀区上地八街 7 号院 4 号楼 4 层 

##### **安装证书** 

// 构造 ESACertStore 实例
let certStore = new ESACertStore()
let code = certStore.initInstance( this .storeName)
if (code !== 0){
'
this .showResult( 构造 ESACertStore 实例-initInstance',certStore)
return
}
let signCertB64 = this .signCert;
let signCertObj = certStore.installCert(signCertB64);
if (signCertObj === null ){
'
this .showResult( 安装签名证书-installCert',certStore)
return
}
this .resultText += '安装签名证书成功' + signCertObj.getSerialNumber() +
' \n ';
let encryCertB64 = this .encryCert ?? '';
let encryKeyB64 = this .encryKey ?? '';
if (encryCertB64 && encryKeyB64){
code = certStore.login( this .userPin);
if (code !== 0){
'
this .showResult( 登录证书库-login',certStore)
return
}
let encryCertObj =
certStore.installEncCert(signCertB64,encryCertB64,encryKeyB64);
if (encryCertObj === null ){
'
this .showResult( 安装加密证书-installEncCert',certStore)
return
}
this .resultText += '安装加密证书成功' + encryCertObj.getSerialNumber() +
' \n ';
}

##### **裸签名验签** 

##### 裸签名: 

|**let** hashAlg:numbe //|r = HashAlgEnumType[**this**.hashText];|
|---|---|

###### 北京天威诚信电子商务服务有限公司 

7 

总部电话:010-50947500 / 400-666-3999 总部地址:北京市海淀区上地八街 7 号院 4 号楼 4 层 

**let** store :ESACertStore = **new** ESACertStore() **let** code = store.initInstance( **this** .storeName) **if** (code !== 0){ **this** .showResult('ESACertStore - initInstance',store) **return** } code = store.login( **this** .userPin) **if** (code !== 0){ **this** .showResult('ESACertStore - login',store) **return** } **let** cert :ESACertificate = **new** ESACertificate() code = cert.initInstance( **this** .certB64) **if** (code !== 0){ **this** .showResult('ESACertificate - initInstance',cert) **return** } **let** esaCert = store.getCert(cert.getSerialNumber(), cert.getIssuer()); **if** (esaCert=== **null** ){ **this** .showResult('ESACertStore - getCert',store) **return** } // sign p1 **let** plainData: ArrayBuffer = StringUtils.stringToArrayBuffer( **this** .plain) **let** signValue = esaCert.signP1(hashAlg, plainData) **if** (signValue=== **null** ){ **this** .showResult('ESACertificate - signP1',cert) **return** } // 展示结果 **let** signData = StringUtils.arrayBufferToBase64(signValue) **this** .resultText = "裸签名:" + signData; 

##### 裸验: 

**let** hashAlg:number = HashAlgEnumType[ **this** .hashText]; 

**let** plainData: ArrayBuffer = StringUtils.stringToArrayBuffer( **this** .plain) **let** signData = **new** util.Base64Helper().decodeSync( **this** .extraText) **let** cert :ESACertificate = **new** ESACertificate() **let** code = cert.initInstance( **this** .certB64) **if** (code !== 0){ **this** .showResult('ESACertificate - initInstance',cert) **return** } 

###### 北京天威诚信电子商务服务有限公司 

8 

总部电话:010-50947500 / 400-666-3999 总部地址:北京市海淀区上地八街 7 号院 4 号楼 4 层 

**let** result = cert.verifyP1(hashAlg, plainData, signData.buffer **as** ArrayBuffer) **if** (result === 0){ **this** .resultText = '验签通过' } **else** { ' ' **this** .showResult( 验签失败 ,cert) } 

##### **P7 签名验签** 

##### p7 签名: 

**let** hashAlg:number = HashAlgEnumType[ **this** .hashText]; // ESACertificate **let** store :ESACertStore = **new** ESACertStore() **let** code = store.initInstance( **this** .storeName) **if** (code !== 0){ **this** .showResult('ESACertStore - initInstance',store) **return** } code = store.login( **this** .userPin) **if** (code !== 0){ **this** .showResult('ESACertStore - login',store) **return** } **let** cert :ESACertificate = **new** ESACertificate() code = cert.initInstance( **this** .certB64) **if** (code !== 0){ **this** .showResult('ESACertificate - initInstance',cert) **return** } **let** esaCert = store.getCert(cert.getSerialNumber(),cert.getIssuer()) **if** (esaCert === **null** ){ **this** .showResult('ESACertStore - getCert',store) **return** } // sign p7 **let** bContainContent : boolean = **this** .isOn **let** plainData = StringUtils.stringToArrayBuffer( **this** .plain) **let** signValue = esaCert.signP7(hashAlg, plainData , bContainContent); **if** (signValue=== **null** ){ **this** .showResult('P7 签名:',esaCert); **return** 

9

###### 北京天威诚信电子商务服务有限公司 

总部电话:010-50947500 / 400-666-3999 

总部地址:北京市海淀区上地八街 7 号院 4 号楼 4 层 

}
// 显示结果
let signB64 = StringUtils.arrayBufferToBase64(signValue)
this .resultText = "P7 签名结果:" + signB64

P7 验签:
let binData = new util.Base64Helper().decodeSync( this .extraText)
let signData = new ESACMSSignData()
let code = signData.initInstance(binData.buffer as ArrayBuffer)
if (code !== 0){
this .showResult('ESACMSSignData - initInstance',signData)
return
}
let hasContent = signData.containContent()
let contentData : ArrayBuffer | null = null ;
if (hasContent){
contentData = signData.getContent();
} else {
if (StringUtils.isEmpty( this .plain)){
this .resultText = 'P7 签名值中不包含原文,继续验证请输入原文!'
return
}
contentData = StringUtils.stringToArrayBuffer( this .plain)
}
if (contentData=== null ){
this .resultText = '原文为空'
return
}
let result = signData.verify(contentData as ArrayBuffer)
if (result === 0){
this .resultText = '验签通过'
} else {
' '
this .showResult( 验签失败 ,signData)
}

##### **裸加密解密** 

##### 裸加密: 

**let** cert = **new** ESACertificate() **let** code = cert.initInstance( **this** .certB64) **if** (code !== 0) { 

10

###### 北京天威诚信电子商务服务有限公司 

总部电话:010-50947500 / 400-666-3999 总部地址:北京市海淀区上地八街 7 号院 4 号楼 4 层 

this .showResult('ESACertificate - initInstance', cert)
return

}

**let** plainData : ArrayBuffer= StringUtils.stringToArrayBuffer( **this** .plain) **let** encData = cert.encryptP1(plainData) 

**if** (encData === **null** ) { **this** .showResult('裸加密 - encryptP1', cert) **return** } **let** encResult = StringUtils.arrayBufferToBase64(encData) **this** .resultText = '裸加密:' + encResult 

##### 裸解密: 

**let** binCipher = **new** util.Base64Helper().decodeSync( **this** .extraText, util.Type.MIME) 

###### // 构建证书库 

**let** store = **new** ESACertStore() 

**let** code = store.initInstance( **this** .storeName) 

**if** (code !== 0) { **this** .showResult('ESACertStore - initInstance', store) 

###### **return** 

} 

// login 

code = store.login( **this** .userPin) 

**if** (code !== 0) { 

**this** .showResult('ESACertStore - login', store) 

###### **return** 

} 

// 构建证书 

**let** cert = **new** ESACertificate() 

code = cert.initInstance( **this** .certB64) 

**if** (code !== 0) { 

**this** .showResult('ESACertificate - initInstance', cert) 

###### **return** 

} 

**let** esaCert = store.getCert(cert.getSerialNumber(),cert.getIssuer()) **if** (esaCert === **null** ) { 

**this** .showResult('ESACertStore - getCert', store) 

###### **return** 

} 

**let** plainData = esaCert.decryptP1(binCipher.buffer **as** ArrayBuffer) **if** (plainData === **null** ) { 

**this** .showResult('裸解密结果 - decryptP1', esaCert) 

###### 北京天威诚信电子商务服务有限公司 

11 

总部电话:010-50947500 / 400-666-3999 总部地址:北京市海淀区上地八街 7 号院 4 号楼 4 层 

###### **return** 

} **let** plainStr = StringUtils.uint8ArrayToString( **new** Uint8Array(plainData)) **this** .resultText = '裸解密:' + plainStr 

##### **P7 加密解密** 

##### p7 加密: 

**let** symmAlg: number = SymmEncAlgEnumType[ **this** .symmAlgText] **let** plainData : ArrayBuffer = StringUtils.stringToArrayBuffer( **this** .plain); **let** cert = **new** ESACertificate() **let** code = cert.initInstance( **this** .certB64) **if** (code !== 0) { **this** .showResult('initInstance', cert) **return** } // encryptP7 **let** result = cert.encryptP7(plainData, symmAlg) **if** (result === **null** ) { **this** .showResult('encryptP7', cert) **return** } // show result **let** encValue = StringUtils.arrayBufferToBase64(result) **this** .resultText += 'P7 密文:' + encValue 

##### p7 解密: 

**let** binCipher = **new** util.Base64Helper().decodeSync( **this** .extraText, util.Type.MIME) **let** cmsEnvelopeData = **new** ESACMSEnvelopeData() **let** code = cmsEnvelopeData.initInstance2(binCipher.buffer **as** ArrayBuffer) **if** (code !== 0) { **this** .showResult('ESACMSEnvelopeData - initInstance2', cmsEnvelopeData) **return** 

} // get certStore **let** store = cmsEnvelopeData.getRecipCertStore() **if** (store === **null** ) { **this** .showResult('ESACMSEnvelopeData - getRecipCertStore', cmsEnvelopeData) **return** 

12

###### 北京天威诚信电子商务服务有限公司 

总部电话:010-50947500 / 400-666-3999 总部地址:北京市海淀区上地八街 7 号院 4 号楼 4 层 

} 

code = store.login( **this** .userPin) 

**if** (code !== 0) { 

**this** .showResult('ESACMSEnvelopeData - login', store) **return** 

} // 解密 P7 

**let** plainData = cmsEnvelopeData.getContent() 

**if** (plainData === **null** ) { 

**this** .showResult('ESACMSEnvelopeData - getContent', cmsEnvelopeData) **return** 

} store.logout() 

**let** plainStr = StringUtils.uint8ArrayToString( **new** Uint8Array(plainData)) **this** .resultText = 'P7 解密:' + plainStr 

##### **修改pin 码** 

##### 修改管理员 pin: 

**this.changePinWithType(this.storeName, this.adminPin, this.newPin, 1)** 

**private** changePinWithType(storeName:string, oldPin:string, newPin:string, type:number ){ // ESACertStore 实例构建 

**let** store = **new** ESACertStore() 

**let** code = store.initInstance(storeName) **if** (code !== 0){ 

**this** .showResult('ESACertStore 实例构建 - initInstance', store) **return** 

} 

code = store.changePin(oldPin,newPin,type); **this** .showResult('修改' + (type === 1 ? '管理员' : '用户') + 'pin - changePin', store) } 

##### 修改用户 pin: 

###### **his.changePinWithType(this.storeName, this.adminPin, this.newPin, 2)** 

**private** changePinWithType(storeName:string, oldPin:string, newPin:string, type:number ){ // ESACertStore 实例构建 **let** store = **new** ESACertStore() 

13

###### 北京天威诚信电子商务服务有限公司 

总部电话:010-50947500 / 400-666-3999 

总部地址:北京市海淀区上地八街 7 号院 4 号楼 4 层 

**let** code = store.initInstance(storeName) **if** (code !== 0){ **this** .showResult('ESACertStore 实例构建 - initInstance', store) **return** } code = store.changePin(oldPin,newPin,type); **this** .showResult('修改' + (type === 1 ? '管理员' : '用户') + 'pin - changePin', store) } 

##### 重置用户 pin: 

// 重置 pin **let** certStore = **new** ESACertStore(); **let** code = certStore.initInstance( **this** .storeName) **if** (code !== 0){ **this** .showResult('ESACertStore 实例构建 - initInstance', certStore) **return** } code = certStore.resetUserPin( **this** .newPin, **this** .adminPin) **this** .showResult('重置用户 pin - resetUserPin', certStore) 

##### **对称加解密** 

##### 生成对称秘钥: 

|**let** alg: number = SymmEncAlgEnumType[**this**.symmetricAlgorithmText]|
|---|
|**let** secretKey = **new** ESASecretKey()|
|**let** code = secretKey.initInstance(alg)|
|**if**(code !== 0){|
|**this**.resultText = 'symmetric key init failed, code:' + code|
|**return** }|
|**let** symmetricKey = secretKey.getEncoded()|
|**if**(symmetricKey == **null**){|
|**this**.showResult('symmetric key get failed', secretKey)|
|**return** }|
|**this**.symmetricKey = StringUtils.arrayBufferToBase64(symmetricKey)|
|**if**(**this**.symmetricAlgorithmText.includes('CBC')){|
|**this**.vectorIV = **new** util.Base64Helper().encodeToStringSync(**new**|
|Uint8Array(secretKey.getIv())); |
|} **this**.showResult('symmetric key generate', secretKey)|
|14|

14

###### 北京天威诚信电子商务服务有限公司 

总部电话:010-50947500 / 400-666-3999 总部地址:北京市海淀区上地八街 7 号院 4 号楼 4 层 

##### 对称加密: 

**let** plainData : ArrayBuffer = StringUtils.stringToArrayBuffer( **this** .plain) **let** keyData = **new** util.Base64Helper().decodeSync( **this** .symmetricKey) **if** ((ivData === **null** ) && **this** .symmetricAlgorithmText.includes('CBC')){ **this** .resultText = 'CBC 模式需要指定初始向量 iv(base64 编码)' **return** 

} **let** symmEncAlg: number = SymmEncAlgEnumType[ **this** .symmetricAlgorithmText] **let** secretKey = **new** ESASecretKey() 

**let** code = secretKey.initInstance2(symmEncAlg, keyData.buffer **as** ArrayBuffer, ivData?.buffer **as** ArrayBuffer) **if** (code !== 0){ **this** .showResult('symmetric key init failed', secretKey) **return** 

} 

**let** cipherData = secretKey.encrypt(plainData) **if** (cipherData == **null** ){ **this** .showResult('symmetric encrypt failed', secretKey) **return** } **this** .cipherText = StringUtils.arrayBufferToBase64(cipherData) **this** .resultText = 'symmetric encrypt result :' + **this** .cipherText 

##### 对称解密: 

**let** cipherData = **new** util.Base64Helper().decodeSync( **this** .cipherText) **let** keyData = **new** util.Base64Helper().decodeSync( **this** .symmetricKey) **let** symmEncAlg: number = SymmEncAlgEnumType[ **this** .symmetricAlgorithmText] **let** secretKey = **new** ESASecretKey() **let** code = secretKey.initInstance2(symmEncAlg, keyData.buffer **as** ArrayBuffer, ivData?.buffer **as** ArrayBuffer) **if** (code !== 0){ **this** .showResult('symmetric key init failed', secretKey) **return** } 

**let** plainData = secretKey.decrypt(cipherData.buffer **as** ArrayBuffer) **if** (plainData == **null** ){ **this** .showResult('symmetric decrypt failed', secretKey) **return** } **this** .plain = StringUtils.uint8ArrayToString( **new** Uint8Array(plainData)) **this** .resultText = 'symmetric decrypt result :' + **this** .plain 

###### 北京天威诚信电子商务服务有限公司 

15 

总部电话:010-50947500 / 400-666-3999 总部地址:北京市海淀区上地八街 7 号院 4 号楼 4 层 

##### **摘要计算** 

##### ESAMessageDigest: 

**let** hashAlg : number = HashAlgEnumType[ **this** .symmetricAlgorithmText] **let** plainData: ArrayBuffer = 

StringUtils.stringToArrayBuffer( **this** .plainText) **let** digest = **new** ESAMessageDigest() **let** code = digest.initInstance(hashAlg) **if** (code !== 0){ **this** .showResult('ESAMessageDigest - initInstance', digest) **return** 

} 

code = digest.doInit(); 

**if** (code !== 0){ 

**this** .showResult('ESAMessageDigest - doInit', digest) **return** 

} 

code = digest.doUpdate(plainData) **if** (code !== 0){ **this** .showResult('ESAMessageDigest - doUpdate', digest) **return** 

} **let** hashData = digest.doFinal() **if** (hashData === **null** ){ **this** .showResult('ESAMessageDigest - doFinal', digest) **return** } **this** .resultText = StringUtils.uint8ArrayToHexStr( **new** Uint8Array(hashData)) 

##### ESAHMC: 

**let** hashAlg : number = HashAlgEnumType[ **this** .symmetricAlgorithmText1] **let** keyData = **new** util.Base64Helper().decodeSync( **this** .secretKey) **let** plainData: ArrayBuffer = 

StringUtils.stringToArrayBuffer( **this** .plainText) 

**let** hmac = **new** ESAHMac() 

**let** code = hmac.initInstance(keyData.buffer **as** ArrayBuffer, hashAlg) **if** (code !== 0){ 

**this** .showResult('ESAHMac - initInstance', hmac) **return** } code = hmac.doInit(); 

###### 北京天威诚信电子商务服务有限公司 

总部电话:010-50947500 / 400-666-3999 总部地址:北京市海淀区上地八街 7 号院 4 号楼 4 层 

16 

**if** (code !== 0){ **this** .showResult('ESAHMac - doInit', hmac) **return** 

} 

code = hmac.doUpdate(plainData) 

**if** (code !== 0){ **this** .showResult('ESAHMac - doUpdate', hmac) 

**return** 

} 

**let** hmacData = hmac.doFinal() **if** (hmacData === **null** ){ **this** .showResult('ESAHMac - doFinal', hmac) **return** } 

**this** .resultText = StringUtils.uint8ArrayToHexStr( **new** Uint8Array(hmacData)) 

##### ESAZSM3MessageDigest: 

**let** plainData: ArrayBuffer = 

StringUtils.stringToArrayBuffer( **this** .plainText) 

**let** zsm3 = **new** ESAZSM3MessageDigest() 

**let** code = zsm3.initInstanceWithCert( **this** .certBase64) 

**if** (code !== 0){ 

**this** .showResult('ESAZSM3MessageDigest - initInstanceWithCert', zsm3) 

###### **return** 

} 

code = zsm3.doInit(); 

**if** (code !== 0){ 

**this** .showResult('ESAZSM3MessageDigest - doInit', zsm3) 

###### **return** 

} 

code = zsm3.doUpdate(plainData) 

**if** (code !== 0){ 

**this** .showResult('ESAZSM3MessageDigest - doUpdate', zsm3) 

###### **return** 

} 

**let** hashData = zsm3.doFinal() 

**if** (hashData === **null** ){ 

**this** .showResult('ESAZSM3MessageDigest - doFinal', zsm3) 

**return** 

} **this** .resultText = StringUtils.uint8ArrayToHexStr( **new** Uint8Array(hashData)) 

###### 北京天威诚信电子商务服务有限公司 

17 

总部电话:010-50947500 / 400-666-3999 总部地址:北京市海淀区上地八街 7 号院 4 号楼 4 层 

##### **证书过滤** 

**let** cs = **new** ESACertStore() **let** code = cs.initInstance( **this** .storeName) **if** (code !== 0) { **this** .showResult('ESACertStore - initInstance()', cs) **return** } **let** cf = cs.getCertFilter(); **if** (cf === **null** ) { **this** .showResult('getCertFilter()', cs) **return** } **if** ( **this** .subjectName.length > 0) { cf.setSubject( **this** .subjectName) } **if** ( **this** .serialNumber.length > 0) { cf.setSerialNumber( **this** .serialNumber) } **let** certs = cs.getCerts(); **if** (certs === **null** ) { **this** .showResult('getCerts()', cs) **return** } **if** (certs.length === 0){ **this** .resultText = "当前证书库内未列举到证书!"; **return** } **let** cert= certs[0] 

#### **1. 错误码定义** 

|预定义值|说明|
|---|---|
|0x00000000|成功|
|0xFFFFFFFF|失败|
|0x06000001|入参为空|

###### 北京天威诚信电子商务服务有限公司 

18 

总部电话:010-50947500 / 400-666-3999 总部地址:北京市海淀区上地八街 7 号院 4 号楼 4 层 

|0x06000002|无效参数|
|---|---|
|0x06000003|创建实例失败|
|0x06000004|实例未初始化|
|0x06000005|实例已经初始化|
|0x06000006|句柄不存在|
|0x06000007|license过期 |
|0x06000008|验证license 状态异常|
|0x06000009|平台不匹配|
|0x0600000A|包名不匹配 |
|0x0600000B|内部返回对象错误|
|0x0600000C|内部返回对象句柄错误|
|0x0600000D|license内容错误|
|0x0600000E|获取包名为空|
||C层错误码 |
|0x00000101|申请内存失败|
|0x00000102|申请内存失败|
|0x00000103|实例已经初始化|
|0x00000104|实例没有初始化|
|0x00000105|参数为空|
|0x00000106|参数无效|
|0x00000107|方法不支持|
|0x00000108|数据结构拷贝失败|
|0x00000109|对象拷贝失败|
|0x0000010A|访问越界|
|0x0000010B|Base64 编码失败|
|0x0000010C|Base64 解码失败|
|0x0000010D|Hex 编码失败|
|0x0000010E|Hex 解码失败|
|0x0000010F|缺少必要的配置参数|
|0x00000110|调用错误|
|0x00000111|三次调用失败|
|0x00000112|数据格式错误|
|0x00000113|动态库加载失败|
|0x00000114|加载动态库方法失败|
|0x00010001|数据库读写失败|
|0x00010002|库中数据不存在|
|0x00010003|库中数据已存在|
|0x00020001|访问拒绝|
|0x00020010|无效的License|
|0x00020011|License已到期|
|0x00020020|未知的PIN 类型|

19 

北京天威诚信电子商务服务有限公司 

总部电话:010-50947500 / 400-666-3999 总部地址:北京市海淀区上地八街 7 号院 4 号楼 4 层 

|0x00020021|PIN 码错误|
|---|---|
|0x00020022|已登录|
|0x00030001|Provider已存在|
|0x00030002|指定的Provider 不存在|
|0x00040001|http 请求类型不支持|
|0x00040002|http 请求超时|
|0x00040003|http 请求失败|
|0x00040004|http 请求失败 |
|0x00040005|http 请求失败|
|0x01010001|随机数生成失败|
|0x01020001|对称加密算法不支持|
|0x01020002|对称密钥长度不够|
|0x01020003|对称密钥和算法不匹配 |
|0x01030001|对称加密算法不支持|
|0x01030002|对称加密需要IV|
|0x01030003|对称加密IV 长度不够|
|0x01030004|对称加密init 失败|
|0x01030005|对称加密update 失败|
|0x01030006|对称加密final 失败|
|0x01030007|对称解密init 失败 |
|0x01030008|对称解密update 失败|
|0x01030009|对称解密final 失败|
|0x01040001|非对称算法不支持|
|0x01040002|密钥对生成失败|
|0x01040003|公钥编码失败|
|0x01040004|私钥编码失败|
|0x01040005|公钥解码失败|
|0x01040006|私钥解码失败|
|0x01040007|私钥不可导出|
|0x01040008|私钥不支持导出PKCS8|
|0x01040009|生成私钥失败|
|0x01040301|生成私钥失败|
|0x01040302|生成私钥失败|
|0x01040303|生成公钥失败|
|0x01040304|获取私钥失败|
|0x01040401|生成PP1 或PP2 失败|
|0x01040402|导入PP1 或PP2 失败|
|0x01050001|非对称加密算法不支持|
|0x01050002|非对称加密失败|
|0x01050003|非对称加密init 失败|
|0x01050004|非对称加密update 失败|

###### 北京天威诚信电子商务服务有限公司 

20 

总部电话:010-50947500 / 400-666-3999 总部地址:北京市海淀区上地八街 7 号院 4 号楼 4 层 

|0x01050005|非对称加密final 失败|
|---|---|
|0x01050006|非对称解密失败|
|0x01050007|非对称解密1 失败|
|0x01050008|非对称解密2 失败|
|0x01050009|非对称解密3 失败|
|0x0105000A|非对称解密init 失败|
|0x0105000B|非对称解密update 失败|
|0x0105000C|非对称解密final 失败 |
|0x0105000D|非对称解密C3 检查失败|
|0x0105000E|SM2 加密数据编码失败|
|0x0105000F|SM2 加密数据解码失败|
|0x01060001|摘要算法不支持|
|0x01060002|摘要init 失败 |
|0x01060003|摘要update 失败|
|0x01060004|摘要final 失败|
|0x01060005|摘要p1 结构编码失败|
|0x01070001|签名算法不支持|
|0x01070002|签名没有初始化|
|0x01070003|签名失败|
|0x01070004|签名1 失败|
|0x01070005|签名2 失败|
|0x01070006|签名3 失败|
|0x01070007|验签失败|
|0x01070008|摘要算法不支持|
|0x01070009|SM2签名数据编码失败|
|0x0107000A|SM2签名数据解码失败|
|0x01080001|鉴别码init 失败|
|0x01080002|鉴别码update 失败|
|0x01080003|鉴别码final 失败|
|0x01090001|设备单元不存在|
|0x01090002|指定的设备单元不存在|
|0x01090003|设备单元不止一个|
|0x010A0001|设备没有注册|
|0x010A0002|指定的设备没有注册|
|0x010A0003|没有设置默认的设备|
|0x010A0004|没有设备|
|0x010A0005|指定的设备不存在|
|0x010A0006|设备不止一个|
|0x010A0007|容器是空的|
|0x010A0008|签名密钥不可以解码|
|0x010A0009|加密密钥不可以签名|

###### 北京天威诚信电子商务服务有限公司 

21 

总部电话:010-50947500 / 400-666-3999 总部地址:北京市海淀区上地八街 7 号院 4 号楼 4 层 

|0x010A000A|导出证书长度为0|
|---|---|
|0x010A000B|没有应用|
|0x00000000|成功|
|0x0A000001|失败|
|0x0A000002|异常错误|
|0x0A000003|不支持的服务|
|0x0A000004|文件操作错误|
|0x0A000005|无效的句柄 |
|0x0A000006|无效的参数|
|0x0A000007|读文件错误|
|0x0A000008|写文件错误|
|0x0A000009|名称长度错误|
|0x0A00000A|密钥用途错误 |
|0x0A00000B|模的长度错误|
|0x0A00000C|未初始化|
|0x0A00000D|对象错误|
|0x0A00000E|内存错误|
|0x0A00000F|超时|
|0x0A000010|输入数据长度错误|
|0x0A000011|输入数据错误|
|0x0A000012|生成随机数错误|
|0x0A000013|HASH 对象错误|
|0x0A000014|HASH运算错误|
|0x0A000015|产生RSA 错误|
|0x0A000016|RSA 密钥模长错误|
|0x0A000017|CSP 服务导入公钥错误|
|0x0A000018|RSA 加密错误|
|0x0A000019|RSA 解密错误|
|0x0A00001A|HASH 值不相等|
|0x0A00001B|密钥未发现|
|0x0A00001C|证书未发现|
|0x0A00001D|对象未导出|
|0x0A00001E|解密时做补丁错误|
|0x0A00001F|MAC 长度错误|
|0x0A000020|缓冲区不足|
|0x0A000021|密钥类型错误|
|0x0A000022|无事件错误|
|0x0A000023|设备已移除|
|0x0A000024|PIN 不正确|
|0x0A000025|PIN 被锁死|
|0x0A000026|PIN 长度错误|

###### 北京天威诚信电子商务服务有限公司 

22 

总部电话:010-50947500 / 400-666-3999 总部地址:北京市海淀区上地八街 7 号院 4 号楼 4 层 

|0x0A000027|用户已登录|
|---|---|
|0x0A000028|应用不存在|
|0x0A000029|没有初始化用户口令|
|0x0A00002A|PIN 类型错误|
|0x0A00002B|应用名称无效|
|0x0A00002C|应用已经存在|
|0x0A00002D|用户没有登录|
|0x0A00002E|应用不存在|
|0x0A00002F|文件已经存在|
|0x0A000030|空间不足|
|0x0A000031|文件不存在|
|0x0A000032|已达到最大可管理容器数|
|0x0A000033|导入密钥错误|
|0x0A000034|生成对称密钥错误|
|0x0A000035|容器已经存在|
|0x0A000036|容器不存在|
|0x0A000037|容器没有打开|

#### **2. 补充说明** 

##### **关于构造方法和对象初始化方法** 

构造方法只负责实例对象的构建;对象初始化方法负责具体对象的实例化。两个 方法需要配合使用,即先调用构造方法,再调用对象初始化方法完成对象实例化, 进而使用该实例对象进行对应类的其他功能方法的调用。(注:单例对象不适用 该规则) 

##### **关于对象生命周期** 

**1** 、直接构建的对象符合生命周期和作用域的一般通用规则。 

- 2、 通过 **A** 对象获得的 **B** 对象, **B** 对象依赖于 **A** 对象, **B** 对象生命周期包含在 **A** 对象生命周期中,即 **A** 对象释放后 **B** 对象也会被释放。 通过如下代码说明: 

public exampleFunc1(){ 

```arkts
let cert: ESACertificate = exampleFunc2(); let base64: string = cert.getB64Encoded(); } public fun exampleFunc2():ESACertificate { let certStore : ESACertStore = new ESACertStore( ); let ret:number = certStore.initInstance("storeName"); let cert: ESACertificate = certStore.getCert("证书序列号","issuer"); 
```

###### 北京天威诚信电子商务服务有限公司 

总部电话:010-50947500 / 400-666-3999 总部地址:北京市海淀区上地八街 7 号院 4 号楼 4 层 

23 

```arkts
let certB64:string = cert.getB64Encoded(); return cert; } 
```

该例中,exampleFun2()方法中的 store 对象即为 A,cert 对象即为 B,运行程 序可知 

exampleFun2()中的 certB64 有值,exampleFun1()方法中的 certB64 无法正常获取 值;原因是 cert 对象生命周期与 store 对象生命周期关联,即 store 对象在 exampleFunc2 出了作用域后被回收的同时,cert 对象也会被回收。 

可通过改变 store 对象的作用域解决该问题,如更改 store 对象局部作用域为 文件作用域或全局作用域。代码如下: 

certStore = null; public exampleFunc1(){ 

```arkts
let cert: ESACertificate = exampleFunc2(); let base64: string = cert.getB64Encoded(); } public exampleFunc2():ESACertificate { let certStore = new ESACertStore( ); let ret:number = certStore.initInstance("storeName"); let cert: ESACertificate = certStore.getCert("证书序列号","issuer"); let certB64: string = cert.getB64Encoded(); return cert; } 
```

##### **关于对象状态的说明** 

通过 SDK 接口返回的对象,是带状态的,集成者主动构建的对象是无状态的, 这里的状态是指对私钥的访问权限状态。以 ESACertificate 为例说明: 情形一:主动构建 

cert1: ESACertificate = new ESACertificate( ); ret:number = cert1 .initInstance("base64"); 说明:cert1 对象没有状态,即没有访问私钥的权限,当进行签名、解密等需要私钥访问权限的功能时,上 述构建对象的方式不能满足需求。 

情形二:主动构建 certStore: ESACertStore = new ESACertStore( ); ret:number = certStore.initInstance("storeName"); ret = certStore. Login("userPin"); cert: ESACertificate = certStore.getCert("证书序列号","issuer"); 说明:certStore 未登录时, cert2 对象无状态;certStore 登录后, cert2 对象有状态, 可进行签名、解密等 功能。 

北京天威诚信电子商务服务有限公司 

总部电话:010-50947500 / 400-666-3999 总部地址:北京市海淀区上地八街 7 号院 4 号楼 4 层 

24 

25 

###### 北京天威诚信电子商务服务有限公司 

总部电话:010-50947500 / 400-666-3999 总部地址:北京市海淀区上地八街 7 号院 4 号楼 4 层
