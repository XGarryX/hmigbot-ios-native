## HarmonyOS SDK 接入文档 

# 1.引言 

## **1.1** 文档概述 

以国密核心专利算法为依托,为手机提供硬件级别的数字证书安全服务。 本接口文档,描述 SDK 为第三方业务平台集成调用提供的接口定义等内容。适用于第三方 业务平台系统集成的程序开发人员、测试人员、项目管理人员及系统运营人员、管理人员等。 

## **1.2** 开发环境 

开发环境:DevEco Studio 开发语言: ArkTS 

# 2.SDK 使用配置 

## **2.1** 下载安装 

ohpm install @hnxaca/hnxacasdk OpenHarmony ohpm 环境配置等更多内容,请参考 如何安装 OpenHarmony ohpm 包 

## **2.2** 手动引入 **har** 

将 hnxacasdk.har 包文件放入项目适当的文件夹中,如 libs 或 assets 目录,并把该 har 包 文件加载到项目中。路径确定以后在开发工具的终端中执行 ohpm install,执行成功,在目 录中出现 oh_modules 文件夹。 

## **2.3** 权限设置 

集成该 har 包需要 app 具有网络权限,在 entry 的 module.json5 文件中添加 ohos.permission.INTERNET 权限。 

# 3 SDK API 文档说明 

## **3.1** 获取当前版本号 

接口说明:获取版本号 接口定义: getVersion(): string 参数说明: 参数 类型 说明 是否必须 参数选项 无 

## **3.2** 初始化 **sdk** 

接口说明:初始化 sdk 接口定义: 

initSdk(context:Context,thirdAppKey:string,thirdAppUserName:string,keySupplier:SoftKeySupplie rs,callBack:(result: HnResponseObj) => void): void 参数说明: 

|参数|类型|说明|是否 必须|参数选项|
|---|---|---|---|---|
|context|Context|调用者的上下文 环境|是||
|thirdAppKey|string|App调用sdk的授 权码|是|为开发者分配的业务授权 码|
|thidAUN|ti|调用者 App 用|是|调用者业务APP用户唯一|
|rppserame|srng|户唯一标识||标识|
|keySupplier|SoftKeySuppliers|证书类型|是|SoftKeySuppliers.ZY|
|callBack|HnResponseObj|结果回调|是||

## **3.3** 申请证书 

接口说明:进行数字证书申请 接口定义: 

applyCertNoPage(pin: string, userCertInfo: UserCertInfo, callBack: (result: HnResponseObj) => void):void 

参数说明: 参数 类型 说明 是否必须 参数选项 pin string 数字证书 pin 码 是 userCertInfo UserCertInfo 数字证书信息类 是 callBack HnResponseObj 结果回调 是 

## **3.4 PKCS1** 签名 

接口说明:进行 PKCS1 签名 接口定义: 

signDataNoPage(pin: string, businessNo: string, data: string,callBack:(result: HnResponseObj)=> void): void 参数说明: 参数 类型 说明 是否必须 参数选项 pin string 数字证书 pin 码 是 businessNo string 事务标识 是 data string 原文 是 callBack HnResponseObj 结果回调 是 

## **3.5 PKCS7** 签名 

接口说明:组织 P7 格式签名 接口定义: signDataP7NoPage(pin: string, businessNo: string, data: string,callBack:(result: HnResponseObj)=> void): void 参数说明: 参数 类型 说明 是否必须 参数选项 pin string 数字证书 pin 码 是 businessNo string 事务标识 是 data string 原文 是 callBack HnResponseObj 结果回调 是 

## **3.6** 对称加密 

接口说明:进行对称算法加密 接口定义: symmEncrypt(businessNo: string, algorithm: number, data: ArrayBuffer,key :ArrayBuffer,callBack:(result: HnResponseObj)=> void): void 参数说明: 参数 类型 说明 是否必须 参数选项 businessNo string 事务标识 是 algorithm number 对称算法标识 是 data ArrayBuffer 原文 是 key ArrayBuffer 对称密钥 是 callBack HnResponseObj 结果回调 是 

## **3.7** 对称解密 

接口说明:使用对称密钥进行解密 接口定义: symmDecrypt(businessNo: string, algorithm: number, data: ArrayBuffer,key :ArrayBuffer,callBack:(result: HnResponseObj)=> void): void 参数说明: 参数 类型 说明 是否必须 参数选项 businessNo string 事务标识 是 algorithm number 对称算法标识 是 data ArrayBuffer 原文 是 key ArrayBuffer 对称密钥 是 callBack HnResponseObj 结果回调 是 

## **3.8** 数据摘要 

接口说明:对传入数据进行摘要 接口定义: 

hashData(pin: string, businessNo: string, algorithm: number, data: ArrayBuffer,callBack:(result: HnResponseObj)=> void): void 

参数说明: 

参数 类型 说明 是否必须 参数选项 pin string 数字证书 pin 码 是 businessNo string 事务标识 是 

algorithm number 摘要算法 是 data ArrayBuffer 原文 是 callBack HnResponseObj 结果回调 是 

## **3.9** 加密封装数字信封 

接口说明:使用加密证书对原文进行加密封装为数字信封 接口定义: 

makeEnvelopeNoPage(pin: string, businessNo: string,inputData: string, cert: string,callBack:(result: HnResponseObj)=> void): void 参数说明: 参数 类型 说明 是否必须 参数选项 pin string 数字证书 pin 码 是 businessNo string 事务标识 是 用于标识本次接口调用 inputData string 原文 是 cert string 数字证书 base64 字符串 是 callBack HnResponseObj 结果回调 是 

## **3.10** 解密拆解数字信封 

接口说明:拆解数字信封获取原文 接口定义: 

openEnvelopeNoPage(pin: string, businessNo: string, envelopedData: string,callBack:(result: HnResponseObj)=> void): void 

参数说明: 

参数 类型 说明 是否必须 参数选项 pin string 数字证书 pin 码 是 businessNo string 事务标识 是 用于标识本次接口调用 envelopedData string 数字信封数据 是 callBack HnResponseObj 结果回调 是 

## **3.11** 获取证书 

接口说明:读取保存的证书 接口定义: 

getCert(type: number,callBack:(result: HnResponseObj)=> void):void 参数说明: 

参数 类型 

说明 是否必须 参数选项 

1- 加密证书 type number 证书类型 是 2- 签名证书 callBack HnResponseObj 结果回调 是 

## **3.12** 解析数字证书信息 

接口说明:获取对应的数字证书信息 接口定义: 

getCertInfo(certBase64: string, item: number,callBack:(result: HnResponseObj)=> void): void 参数说明: 

|参数|类型|说明|是 否 必须 参|数选项|
|---|---|---|---|---|
|certBase64|string|数字证书 base64 字符串|是||
||||1、 2、 3、 4、|证书版本; 证书序列号; 证书签名算法标识; 证书颁发者国家(C);|
||||5、 6、 7、 区 8、 9、 区(|证书颁发者组织名(O); 证书颁发者部门名(OU); 证书颁发者所在的省、自治 、直辖市(S); 证书颁发者通用名称(CN); 证书颁发者所在的城市、地 L);|
||||10|、证书颁发者Email;|
|item|number|需要解析的项|是 11 12 13 14 15 16 区 17 18 区(|、证书有效期:起始日期; 、证书有效期:终止日期; 、证书拥有者国家(C ); 、证书拥有者组织名(O); 、证书拥有者部门名(OU); 、证书拥有者所在的省、自治 、直辖市(S); 、证书拥有者通用名称(CN); 、证书拥有者所在的城市、地 L);|
||||19|、证书拥有者Email;|
||||20|、证书颁发者DN;|
||||21|、证书拥有者DN;|
|callBack|HnResponseObj|结果回调|是||

## **3.13** 获取数字证书全部信息 

接口说明:获取数字证书全部信息 接口定义: 

getCertInfoAll(cert: string,callBack:(result: HnResponseObj)=> void): void 参数说明: 

参数 类型 说明 是否必须 参数选项 cert string 数字证书 base64 字符串 是 callBack HnResponseObj 结果回调 是 

## **3.14** 修改 **PIN** 码 

接口说明:修改 PIN 码 接口定义: 

modifyPinNoPage(pin: string, newPin: string, callBack:(result: HnResponseObj)=> void): void 参数说明: 

参数 类型 说明 是否必须 参数选项 pin string 数字证书 pin 码 是 newPin string 新 pin 码 是 callBack HnResponseObj 结果回调 是 

## **3.15** 验证 **PIN** 码 

接口说明:验证 PIN 码 接口定义: 

checkPinNoPage(pin: string, businessNo: string, callBack:(result: HnResponseObj)=> void): void 参数说明: 

参数 类型 说明 是否必须 参数选项 pin string 数字证书 pin 码 是 businessNo string 事务标识 是 callBack HnResponseObj 结果回调 是 

## **3.16** 生成随机数 

接口说明:生成随机数 接口定义: 

genRandom(businessNo: string, size: number,callBack:(result: HnResponseObj)=> void): void 参数说明: 

|参数|类型|说明|是否必须|参数选项|
|---|---|---|---|---|
|businessNo|string|事务标识|是||
|size|number|生成随机数长度|是||
|callBack|HnResponseObj|结果回调|是||

# 4. 附录 

## **4.1** 错误码( **16** 进制,括号内对应 **10** 进制) 

|错误码|描述|
|---|---|
|0X0000000(0)|成功|
|0X0001001(4097)|未知错误|
|0X0001002(4098)|参数错误|
|0X0001003(4099)|不支持参数错误|
|0X0001004(4100)|内存错误|
|0X0001005(4101)|base64编码错误|
|0X0001006(4102)|base64解码错误|
|0X0001007(4103)|读取文件错误|
|0X0001008(4104)|写文件错误|
|0X0001009(4105)|不支持的算法错误|
|0X0001010(4112)|未初始化错误|
|0X0001011(4113)|算法提供者错误,或者不支持|
|0X0001100(4352)|CSP名称错误或者CSP驱动未安装|
|0X0001101(4353)|请求CSP 错误|
|0X0001102(4354)|获取USER KEY 错误|
|0X0001104(4356)|未找到设备|
|0X0001105(4357)|设备中没有证书|
|0X0001106(4358)|连接设备失败|
|0X0001107(4359)|枚举APP失败|
|0X0001108(4360)|打开APP失败|
|0X0001109(4361)|打开容器失败|
|0X0001110(4368)|遍历容器失败|
|0X0001111(4369)|创建容器失败|
|0X0002001(8193)|P7数据格式错误|
|0X0002002(8194)|P7类型错误|
|0X0002003(8195)|P7数据中无证书错误|
|0X0002004(8196)|X509证书错误|
|0X0002005(8197)|读取X509中公钥错误|
|0X0002006(8198)|P12数据格式错误|

|0X0002007(8199)|P12数据PIN码错误|
|---|---|
|0X0002008(8200)|创建P12数据错误|
|0X0002009(8201)|随机数长度错误|
|0X0002010(8208)|生成随机数错误|
|0X0002011(8209)|计算数据摘要错误|
|0X0002012(8210)|计算文件摘要错误|
|0X0002013(8211)|创建HASH 对象错误|
|0X0002014(8212)|证书解析错误|
|0X0002015(8213)|对称加密错误|
|0X0002016(8214)|对称解密错误|
|0X0002017(8215)|签名错误|
|0X0002018(8216)|签名摘要错误|
|0X0002019(8217)|验签错误|
|0X0002020(8224)|非对称加密错误|
|0X0002021(8225)|非对称解密错误|
|0X0002022(8226)|生成密钥对错误|
|0X0002023(8227)|导入密钥对错误|
|0X0002024(8228)|导出公钥错误|
|0X0002025(8229)|读取证书错误|
|0X0002026(8230)|保存证书错误|
|0X0002027(8231)|保存密钥对错误|
|0X0002028(8232)|读取密钥对错误|
|0X0002029(8233)|私钥转换错误|
|0X0002030(8240)|公钥转换错误|
|0X0002031(8241)|取消输入密码错误|
|0X0002032(8242)|输错密码次数过多错误|
|0X0002033(8243)|不支持的证书类型|
|0X0002034(8244)|创建X509_REQ 对象错误|
|0X0002035(8245)|DN 格式错误|
|0X0002036(8246)|删除证书错误|
|0X0002037(8247)|控件过期|
|0X0002038(8248)|签名值格式错误|
|0X0002039(8249)|导出会话密钥错误|
|0X0002040(8256)|导入会话密钥错误|
|0X0002041(8257)|证书和密钥不匹配错误|

0X0002042(8258) 取消操作 0X0002043(8259) P7 签名错误 0X0002044(8260) 验证 PIN 码错误 0X0000BC6 (3014) 密钥禁用 

## **4.2** 附录 **2** 

Hash 算法 

|ALGID_HASH_SHA1|1|
|---|---|
|ALGID_HASH_SHA256|2|
|ALGID_HASH_SHA512|3|
|ALGID_HASH_MD5|4|
|ALGID_HASH_MD4|5|
|ALGID_HASH_SM3|6|

对称算法 

|ALGID_DES_ECB|1|
|---|---|
|ALGID_DES_CBC|2|
|ALGID_3DES_ECB|3|
|ALGID_3DES_CBC|4|
|ALGID_AES_128_ECB|5|
|ALGID_AES_128_CBC|6|
|ALGID_AES_192_ECB|7|
|ALGID_AES_192_CBC|8|
|ALGID_AES_256_ECB|9|
|ALGID_AES_256_CBC|10|
|ALGID_SM4|11|
