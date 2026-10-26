中认移动认证 SDK 接口说明文档 V1.0.0 

文档提供者:北京中认环宇信息安全技术有限公司 

说明:本SDK V1.0.0 版本接口从OpenHarmony SDK API version 13 开始提供支持。 

# **1. AuthApi.init** 

init(context: Context, appId: string, serverAddr: string):void; 

## **接口说明** : 

## 用于完成SDK 初始化 

## **参数说明:** 

|**参数名**|**类型**|**是否必传**|**备注说明**|
|---|---|---|---|
|context|string|是|上下文context 请在 @Component 页面中通过let context = getContext(this) 获取请勿在UIAbility 中用|
||||this.context 获取|
|appId|string|是|app 授权唯一id,由文档提供方提 供|
|serverAddr|string|是|移动认证模块服务地址|

## **返回值:** 

|**返回值**|**类型**|**备注说明**|
|---|---|---|
|void|void||

## **调用示例:** 

AuthApi.init(getContext(), "a2d9", "http://172.18.101.89:10042"); 

# **2. AuthApi.register** 

register(account: string, userName: string, idCard: string, idCardType: string, phoneNo: string, province: string, city: string, country: string, address: string, certType: string, pin: string, callback: AuthCallback<AuthApiResp>):void; 

## **接口说明** : 

用于完成用户注册,并在注册完成后为用户下发本机构SM2 算法个人/企业数字证 书(本接口不进行注册用户信息真实性核对,如有需要由调用者自行完成),本接口 通过回调结果返回注册结果,AuthApiResp 类中data 字段即为用户accountId, accountId 为本移动认证模块用户唯一账户id。 

## **参数说明:** 

|**参数名**|**类型**|**是否必传**|**说明**|
|---|---|---|---|
|account|string|是|调用者业务系统账户|
|userName|string|是|姓名|
|idCard|string|是|身份证件号码:1 个人,2 企业|
||||身份证件类型: "SF"身份证,|
|idCardType|string|是|"USCC”企业统一社会信用代|
||||码|
|phoneNo|string|是|手机号码|
|province|string|是|所在省份|
|city|string|是|所在城市|
|country|string|是|所在国家|
|address|string|是|通讯地址|
|certType|string|是|证书类型:1 个人,2 企业,3|

||||事件,4 法人|
|---|---|---|---|
|pin|string|是|证书PIN|
|callback|AuthCallback|是|接口调用结果回调|

## **返回值:** 

|**返回值**|**类型**|**说明**|
|---|---|---|
|void|void||

## **调用示例:** 

AuthApi.register("exa223ic", "张三","123456789123456789", "SF", 

"155121345678", "北京市", "北京市", "丰台区", "北京市丰台区长虹科技大厦4 层", "2", "123456",{ onSuccess: (result) => { 

```arkts
let accountId = result.data; this.result = JSON.stringify(result); }, onFailed: (errorCode, errorMsg) => { this.result = JSON.stringify(errorCode + errorMsg); }}); 
```

# **3. AuthApi.queryCert** 

queryCert(accountId: string,callback:AuthCallback<CertRecord>):void; 

## **接口说明** : 

查询本地证书信息。 

## **参数说明:** 

|**参数名**|**类型**|**是否必传**|**说明**|
|---|---|---|---|
|accountId|string|是|账户唯一id|
|callback|AuthCallback|是|接口调用结果回调|

## **返回值:** 

|**返回值**|**类型**|**说明**|
|---|---|---|
|void|void||

## **调用示例:** 

AuthApi.queryCert("8c8270be-e1f7-4e5b-b482-94ecf68ba102", { 

onSuccess: (result) => { this.result = JSON.stringify(result); }, onFailed: (errorCode, errorMsg) => { this.result = JSON.stringify(errorCode + errorMsg); }}); 

# **4. AuthApi.queryCertSync** 

queryCertSync(accountId: string):CertRecord; 

## **接口说明** : 

查询本地证书信息。 

## **参数说明:** 

|**参数名**|**类型**|**是否必传说明**|
|---|---|---|

accountId string 是 账户唯一id 

## **返回值:** 

|**返回值类型**|**类属性**|**属性类型**||
|---|---|---|---|
||encrypt_cert|string|加密证书|
||sign_cert|string|错误信息|
||key_pair|string|密钥对|
||device_id|string|设备id|
||gesture|string|手势|
||cert_type|string|证书类型|
||cert_id|number|证书id|
|certRecord CertRecord|account|string|证书账户|
||account_id|string|证书账号id|
||not_before|string|证书有限期起始时间|
||not_after|string|证书有限期结束时间|
||cert_uuid|string|证书用户id|
||cn|string|证书主题|
||private_key|string|协同本地私钥|
||public_key|string|协同公钥|

## **调用示例:** 

let result: CertRecord = 

AuthApi.queryCertSync("8c8270be-e1f7-4e5b-b482-94ecf68ba102"); 

# **5. AuthApi.applyUpdateCert** 

applyUpdateCert(accountId:string, isApply: boolean, pin: string, 

callback:AuthCallback<AuthApiResp>):void; 

## **接口说明** : 

更新用户证书。(该接口调用前需预先在系统中导入用户信息, 可定制化) 

## **参数说明:** 

|**参数名**|**类型**|**是否必传**|**说明**|
|---|---|---|---|
|accountId|string|是|账户唯一id|
|isApply|boolean|是|申请证书:true 更新证书:false|
|pin|string|是|证书pin(证书更新时传””)|
|callback|AuthCallback|是|接口调用结果回调|

## **返回值:** 

|**返回值**|**类型**|**说明**|
|---|---|---|
|void|void||

## **调用示例:** 

AuthApi.applyUpdateCert("8c8270be-e1f7-4e5b-b482-94ecf68ba102", false, 

"123456", { 

onSuccess: (result) => { 

this.result = JSON.stringify(result); 

}, 

onFailed: (errorCode, errorMsg) => { 

this.result = JSON.stringify(errorCode + errorMsg); 

}}); 

# **6. AuthApi.recoverCert** 

recoverCert(accountId: string, callback: AuthCallback<AuthApiResp>): 

void; 

## **接口说明** : 

## 恢复用户本地证书。 

## **参数说明:** 

|**参数名**|**类型**|**是否必传**|**说明**|
|---|---|---|---|
|accountId|string|是|账户唯一id|
|callback|AuthCallback|是|接口调用结果回调|

## **返回值:** 

|**返回值**|**类型**|**说明**|
|---|---|---|
|void|void||

## **调用示例:** 

AuthApi.recoverCert("8c8270be-e1f7-4e5b-b482-94ecf68ba102", { 

onSuccess: (result) => { 

this.result = JSON.stringify(result); 

}, 

onFailed: (errorCode, errorMsg) => { 

this.result = JSON.stringify(errorCode + errorMsg); 

}}); 

# **7. AuthApi.clearCert** 

clearCert(accountId: string, callback: AuthCallback<AuthApiResp>): void; 

## **接口说明** : 

## 清除用户本地证书。 

## **参数说明:** 

|**参数名**|**类型**|**是否必传**|**说明**|
|---|---|---|---|
|accountId|string|是|账户唯一id|
|callback|AuthCallback|是|接口调用结果回调|

## **返回值:** 

|**返回值**|**类型**|**说明**|
|---|---|---|
|void|void||

## **调用示例:** 

AuthApi.clearCert("8c8270be-e1f7-4e5b-b482-94ecf68ba102", { 

onSuccess: (result) => { 

this.result = JSON.stringify(result); 

}, 

onFailed: (errorCode, errorMsg) => { 

this.result = JSON.stringify(errorCode + errorMsg); 

}}) 

# **8. AuthApi.clearCertSync** 

clearCertSync(accountId: string): AuthApiResp; 

## **接口说明** : 

## 清除用户本地证书。 

## **参数说明:** 

|**参数名**|**类型**|**是否必传**|**说明**|
|---|---|---|---|
|accountId|string|是|账户唯一id|

## **返回值:** 

|**返回值**|**类型**|**类属性**|**属性类型**||
|---|---|---|---|---|
|||error_code|number|错误码|
|authApiResp|AuthApiResp|error_message data|string string|错误信息 接口返回数据,无特 殊说明则忽略|

## **调用示例:** 

let this.result: AuthApiResp = 

AuthApi.clearCertSync("8c8270be-e1f7-4e5b-b482-94ecf68ba102") 

# **9. AuthApi.updatePin** 

updatePin(accountId: string, oldPin: string, newPin: string, callback: 

AuthCallback<AuthApiResp>): void; 

## **接口说明** : 

修改用户证书Pin。 

## **参数说明:** 

|**参数名**|**类型**|**是否必传**|**说明**|
|---|---|---|---|
|accountId|string|是|账户唯一id|
|oldPin|string|是|证书旧pin|
|newPin|string|是|证书新pin|
|callback|AuthCallback|是|接口调用结果回调|

## **返回值:** 

|**返回值**|**类型**|**说明**|
|---|---|---|
|void|void||

## **调用示例:** 

AuthApi.updatePin("8c8270be-e1f7-4e5b-b482-94ecf68ba102", "123456", 

"12345678", { onSuccess: (result) => { this.result = JSON.stringify(result); }, onFailed: (errorCode, errorMsg) => { this.result = JSON.stringify(errorCode + errorMsg); }}); 

# **10. AuthApi.updatePinSync** 

updatePinSync(accountId: string, oldPin: string, newPin: string): 

AuthApiResp; 

## **接口说明** : 

修改用户证书Pin。 

## **参数说明:** 

|**参数名**|**类型**|**是否必传**|**说明**|
|---|---|---|---|
|accountId|string|是|账户唯一id|
|oldPin|string|是|证书旧pin|
|newPin|string|是|证书新pin|

## **返回值:** 

|**返回值**|**类型类属性**|**属性类型**||
|---|---|---|---|
||error_code|number|错误码|
|authApiResp|AuthApiResp error_message data|string string|错误信息 接口返回数据,无特 殊说明则忽略|

## **调用示例:** 

let result: AuthApiResp = 

AuthApi.updatePinSync("8c8270be-e1f7-4e5b-b482-94ecf68ba102", 

"123456", "12345678"); 

# **11. AuthApi.authLogin** 

authLogin(context: Context, accountId: string, pin: string, callback: 

AuthCallback<AuthApiResp>): void; 

## **接口说明** : 

用户证书登录。 

## **参数说明:** 

|**参数名**|**类型**|**是否必传**|**说明**|
|---|---|---|---|
|context|Context|是|上下文context 请在 @Component页面中通过let context = getContext(this) 获取请勿在UIAbility 中用|
||||this.context 获取|
|accountId|string|是|账户唯一id|
|pin|string|是|证书pin|
|callback|AuthCallback|是|接口调用结果回调|

## **返回值:** 

|**返回值**|**类型**|**说明**|
|---|---|---|
|void|void||

## **调用示例:** 

AuthApi.authLogin(context, "8c8270be-e1f7-4e5b-b482-94ecf68ba102", 

"123456", { 

onSuccess: (result) => { this.result = JSON.stringify(result); }, 

onFailed: (errorCode, errorMsg) => { 

this.result = JSON.stringify(errorCode + errorMsg); 

}}); 

# **12. AuthApi.authCosign** 

authCosign(accountId: string, plainMsg: string, hashMsg: string, callback: AuthCallback<AuthApiResp>): void; 

## **接口说明** : 

用户证书完成协同签名。 

## **参数说明:** 

|**参数名**|**类型**|**是否必传**|**说明**|
|---|---|---|---|
|accountId|string|是|账户唯一id|
|plainMsg|string|是|待签名内容原文(原文/哈希值 二选一)|
|hashMsg|string|是|待签名内容哈希值(原文/哈希 值二选一)|
|callback|AuthCallback|是|接口调用结果回调|

## **返回值:** 

|**返回值**|**类型**|**说明**|
|---|---|---|
|void|void||

## **调用示例:** 

AuthApi.authCosign("8c8270be-e1f7-4e5b-b482-94ecf68ba102", "123456", 

"", { 

onSuccess: (result) => { 

this.result = JSON.stringify(result); 

}, 

onFailed: (errorCode, errorMsg) => { 

this.result = JSON.stringify(errorCode + errorMsg); 

}}); 

# **13. AuthApi.encrypt** 

encrypt(accountId: string, plainBase64: string, callback: 

AuthCallback<AuthApiResp>): void; 

## **接口说明** : 

用户证书完成协同加密。 

## **参数说明:** 

|**参数名**|**类型**|**是否必传**|**说明**|
|---|---|---|---|
|accountId|string|是|账户唯一id|
|plainBase64|string|是|待加密内容base64 编码|
|callback|AuthCallback|是|接口调用结果回调|

## **返回值:** 

|**返回值**|**类型**|**说明**|
|---|---|---|
|void|void||

## **调用示例:** 

AuthApi.encrypt("8c8270be-e1f7-4e5b-b482-94ecf68ba102", 

"cT6OGKQXCu3S2uwbCyENRiOp5Y67XJxbDPy52STUlxY=", { onSuccess: (result) => { 

this.result = JSON.stringify(result); 

}, 

onFailed: (errorCode, errorMsg) => { 

this.result = JSON.stringify(errorCode + errorMsg); 

}}); 

# **14. AuthApi.encryptSync** 

encryptSync(accountId: string, plainBase64: string): AuthApiResp; 

## **接口说明** : 

用户证书完成协同加密。 

## **参数说明:** 

|**参数名**|**类型**|**是否必传**|**说明**|
|---|---|---|---|
|accountId|string|是|账户唯一id|
|plainBase64|string|是|待加密内容base64 编码|

## **返回值:** 

|**返回值**|**类型**|**类属性**|**属性类型**||
|---|---|---|---|---|
|||error_code|number|错误码|
|authApiResp|AuthApiResp|error_message|string|错误信息|
|||data|string|已加密数据|

## **调用示例:** 

let result: AuthApiResp = 

AuthApi.encryptSync("8c8270be-e1f7-4e5b-b482-94ecf68ba102", "cT6OGKQXCu3S2uwbCyENRiOp5Y67XJxbDPy52STUlxY="); 

# **15. AuthApi.decrypt** 

decrypt(accountId: string, message: string, callback: 

AuthCallback<AuthApiResp>): void; 

## **接口说明** : 

用户证书完成协同加密。 

## **参数说明:** 

|**参数名**|**类型**|**是否必传**|**说明**|
|---|---|---|---|
|accountId|string|是|账户唯一id|
|message|string|是|待解密内容|
|callback|AuthCallback|是|接口调用结果回调|

## **返回值:** 

|**返回值**|**类型**|**说明**|
|---|---|---|
|void|void||

## **调用示例:** 

AuthApi.decrypt("8c8270be-e1f7-4e5b-b482-94ecf68ba102", 

"cT6OGKQXCu3S2uwbCyENRiOp5Y67XJxbDPy52STUlxY=", { onSuccess: (result) => { 

this.result = JSON.stringify(result); 

}, 

onFailed: (errorCode, errorMsg) => { 

this.result = JSON.stringify(errorCode + errorMsg); 

}}); 

# **16. AuthApi.decryptSync** 

decryptSync(accountId: string, message: string): AuthApiResp; 

## **接口说明** : 

用户证书完成协同加密。 

## **参数说明:** 

|**参数名**|**类型**|**是否必传**|**说明**|
|---|---|---|---|
|accountId|string|是|账户唯一id|
|message|string|是|待解密内容|

## **返回值:** 

|**返回值**|**类型**|**类属性**|**属性类型**||
|---|---|---|---|---|
|||error_code|number|错误码|
|authApiResp|AuthApiResp|error_message|string|错误信息|
|||data|string|已解密数据|

## **调用示例:** 

let result : AuthApiResp = 

AuthApi.decryptSync("8c8270be-e1f7-4e5b-b482-94ecf68ba102", 

"cT6OGKQXCu3S2uwbCyENRiOp5Y67XJxbDPy52STUlxY="); 

# **17. AuthApi.authLoginByQr** 

## authLoginByQr(context: Context, accountId: string, callback: AuthCallback<AuthApiResp>): void; 

## **接口说明** : 

## 用户扫码授权登录。 

## **参数说明:** 

|**参数名**|**类型**|**是否必传**|**备注说明**|
|---|---|---|---|
|context|string|是|上下文context 请在 @Component 页面中通过let context = getContext(this)|
||||获取请勿在UIAbility 中用|
||||this.context 获取|
|accountId|string|是|账户唯一id|
|callback|AuthCallback|是|接口调用结果回调|

## **返回值:** 

|**返回值**|**类型**|**类属性**|**属性类型**||
|---|---|---|---|---|
|||error_code|number|错误码|
|authApiResp|AuthApiResp|error_message|string|错误信息|
|||data|string|已解密数据|

## **调用示例:** 

AuthApi.authLoginByQr(getContext(), 

"8c8270be-e1f7-4e5b-b482-94ecf68ba102", { 

onSuccess: (result) => { 

this.result = JSON.stringify(result); 

}, 

onFailed: (errorCode, errorMsg) => { 

this.result = JSON.stringify(errorCode + errorMsg); 

}}); 

# **18. 关键类说明** 

## AuthCallback: 接口回调类,用于通知用户错误提示及返回接口执行结果。 

|**类名**|**类方法**|**类方法参数**|**参数类型**|**说明**|
|---|---|---|---|---|
||onSuccess|T|泛型|接口执行结果类|
|AuthCallback|onFailed|error_code error_message|number string|错误码 错误描述|

## AuthApiResp: 接口执行结果类,返回执行结果。 

|**参数名**|**属性**|**类型**|**说明**|
|---|---|---|---|
||error_code|string|错误码|
|AuthApiResp|error_message|string|错误描述|
||data|string|接口返回数据|

# **19. 错误码** 

|**错误码**|**说明**|
|---|---|
|0|成功|

|1008|用户未找到|
|---|---|
|1009|用户账户错误|
|1010|用户手机号错误|
|1011|验证码错误|
|1012|账户错误|
|1014|认证失败|
|1026|错误的token|
|2011|网络异常|
|2012|数据解析失败|
|2013|生成私钥失败|
|2014|获取证书公钥失败|
|2015|数字信封解析失败|
|2016|证书加密失败|
|2017|加密数字证书私钥获取失败|
|2018|签名失败|
|2023|预授权数据解析失败|
|2027|证书不存在|
