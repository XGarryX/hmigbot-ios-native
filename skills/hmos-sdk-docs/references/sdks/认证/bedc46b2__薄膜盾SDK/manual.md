上海方付通科技服务股份有限公司 

# 方付通薄膜盾 SDK 接口说明 _Harmony 

#### 文档属性: 

|文档名称:|薄膜盾SDK接口说明|||
|---|---|---|---|
|项目名称:|薄膜盾SDK|||
|当前版本号:|1.0.5|||
|创建者:||创建日期:|2024/8/21|
|复核者:||复核日期:||
|审批者:||审批日期:||

#### 版权声明: 

此文档的版权归上海方付通科技服务股份有限公司所有,作为其它项目合作方,可以拥有该 份文档的使用权,但未征得上海方付通科技服务股份有限公司的书面批准,不得向第三方借阅、 出让、出版该文档。 

#### 版本历史: 

|版本历史 版本号|: 修改内容|撰写者|发布日期|
|---|---|---|---|
|1.0.0|初稿||2024/8/21|
|1.0.2|修复证书更新中P10 的补位问题||2025/3/3|
|1.0.3|增加BIP 通道配置参数||2025/7/9|
|1.0.4|修改老卡判断逻辑问题||2025/10/11|
|1.0.5|1.添加通信模式控制逻辑 2.添加BIP 模式下绑定校验设备逻辑||2026/1/7|

1 

上海方付通科技服务股份有限公司 

## 目录 

|方付通薄膜盾S|DK接口说明_Harmony ............................................................................................... 1|
|---|---|
|1 SDK基础信|息................................................................................................................................. 3|
|2 使用说明....|...................................................................................................................................... 3|
|3 名词解释....|...................................................................................................................................... 3|
|4 厂商标示....|...................................................................................................................................... 4|
|5 常量说明....|...................................................................................................................................... 4|
|5.1 TM|KeyCertType说明........................................................................................................ 4|
|5.2 TM|KeyAlgType说明......................................................................................................... 4|
|5.3 TM|KeyAutoShutDownType说明..................................................................................... 5|
|6 接口定义....|...................................................................................................................................... 5|
|6.1 卡片|管理接口类FFTTMKeyManager .............................................................................. 5|
|6.1.1|初始化..................................................................................................................... 5|
|6.1.2|获取SDK版本号................................................................................................... 5|
|6.1.3|设置BIP模式参数................................................................................................. 6|
|6.1.4|获取BIP模式参数................................................................................................. 6|
|6.1.5|判断是否有贴膜卡................................................................................................. 7|
|6.1.6|关闭通信通道......................................................................................................... 7|
|6.1.7|获取卡号................................................................................................................. 8|
|6.1.8|获取卡片载体信息................................................................................................. 8|
|6.1.9|读取证书信息......................................................................................................... 9|
|6.1.10|卡片是否是初始密码............................................................................................. 9|
|6.1.11|校验Pin码........................................................................................................... 10|
|6.1.12|初始密码时,设置PIN码接口.......................................................................... 10|
|6.1.13|修改密码............................................................................................................... 11|
|6.1.14|获取Pin码当前剩余输入次数............................................................................ 12|
|6.1.15|重置密码-第一步:获取重置Pin码的身份验证信息................................... 12|
|6.1.16|重置密码-第二步:密码重置验证,下发服务器信息.................................. 13|
|6.1.17|自动开闭签名模式-仅NXY卡支持............................................................... 13|
|6.1.18|数据签名............................................................................................................... 14|
|6.1.19|COS在线更新...................................................................................................... 15|
|6.1.20|NXY证书更新 初始化....................................................................................... 15|
|6.1.21|NXY证书更新 导入证书信息........................................................................... 16|
|6.1.22|CFCA证书更新 初始化..................................................................................... 16|
|6.1.23|CFCA证书更新 导入证书信息......................................................................... 17|
|6.1.24|设置UIContext ..................................................................................................... 17|
|6.1.25|设置开启设备绑定验证相关逻辑....................................................................... 18|
|6.1.26|设置每次通信时对设备的校验码....................................................................... 18|
|6.2 Mod|el类数据.................................................................................................................... 19|
|6.2.1|TMKeyResponse ....................................................................................................... 19|
|6.2.2|TMKeyDeviceModel ................................................................................................ 20|
|6.2.3|TMKeyCertModel ..................................................................................................... 22|
|6.2.4|BIPServiceParams ..................................................................................................... 23|

2 

上海方付通科技服务股份有限公司 

|6.2.5|TMKeyNXYCertUpdateModel ................................................................................. 24|
|---|---|
|6.2.6|TMKeyCFCAPTenModel ......................................................................................... 26|
|6.2.7|TMKeyCFCAImportCertModel ................................................................................ 26|
|6.2.8|TMKeyReadResultStatus .......................................................................................... 27|
|6.2.9|TMKeySmsParams.................................................................................................... 29|
|7 密码键盘|使用说明– CFCA证书使用....................................................................................... 30|
|7.1 TM|KeyKeyboard组件..................................................................................................... 30|
|7.2 例|子展示........................................................................................................................... 31|

# **1 SDK** 基础信息 

SDK 版本:V1.0.5 SDK 包名:libtmk SDK 包 MD5 Hash 值:5CC1AC6501E86D27B6DF40A718A1BEDD 

# **2** 使用说明 

1. 为了与贴膜卡正常交互,将建立通道以及数据交互部分封装成 SDK,方便嵌入第三方 APP 进行二次开发; 

2. SDK 提供了判断是否存在薄膜盾,查看证书,签名等功能,具体见后面接口定义 

3. SDK 使用需要开启网络相关权限,否则无法正常使用 

4. SDK 是以 har 包方式提供 

5. 使用此 SDK 功能需要配置相应权限(网络权限)。在 main/module.json5 文件中添加: 

<!-- 网络权限 --> 

```
"requestPermissions": [
  {
"name": "ohos.permission.INTERNET"
}
]
```

# **3** 名词解释 

|OMA|卡片通道建立方式,|OpenMobileApi模式|
|---|---|---|
|BIP|卡片通道建立方式,|BIP模式|

3 

上海方付通科技服务股份有限公司 

# **4** 厂商标示 

|序号|厂商名称|厂商名称简写|
|---|---|---|
|83|方付通|FFT|

注:厂商标示获取方式:通过获取卡号接口获取到卡号信息,然后截取前两字节即可。 

# **5** 常量说明 

## **5.1 TMKeyCertType** 说明 

```
export enum TMKeyCertType {
```

`FFT` `_` `CERTTYPE` `_` `RSA1024` `_` `SIGN         = 1,            //RSA1024` 签 名证书,只支持签名验签 `FFT` `_` `CERTTYPE` `_` `RSA1024` `_` `ENCRYPT      = 2,            //RSA1024` 加 密证书,只支持加解密 `FFT` `_` `CERTTYPE` `_` `RSA2048` `_` `SIGN         = 3,            //RSA2048` 签 名证书,只支持签名验签 `FFT` `_` `CERTTYPE` `_` `RSA2048` `_` `ENCRYPT      = 4,            //RSA2048` 加 密证书,只支持加解密 `FFT` `_` `CERTTYPE` `_` `SM2` `_` `SIGN             = 5,            //SM2` 签名证 书,只支持签名验签 `FFT` `_` `CERTTYPE` `_` `SM2` `_` `ENCRYPT          = 6,            //SM2` 加密证 书,只支持加解密 `}` 

## **5.2 TMKeyAlgType** 说明 

**`export enum`** `TMKeyAlgType { FFT` `_` `Algorithm` `_` `MD5    = 1,           // MD5` 摘要算法 `FFT` `_` `Algorithm` `_` `SHA1   = 2,           // sha1` 摘要算法 `FFT` `_` `Algorithm` `_` `SHA256 = 3,          // sha256` 摘要算法 `FFT` `_` `Algorithm` `_` `SM3    = 4            //` 国密 `SM3` 摘要算法 `}` 

4 

上海方付通科技服务股份有限公司 

## **5.3 TMKeyAutoShutDownType** 说明 

```
export enum TMKeyAutoShutDownType {
```

`FFT` `_` `AutoShutDown` `_` `OPEN   = 1,          //` 功能 开启 `FFT` `_` `AutoShutDown` `_` `CLOSE  = 2,          //` 功能 关闭 `FFT` `_` `AutoShutDown` `_` `AUTO   = 3,          //` 功能 自动 `}` 

# **6** 接口定义 

6 接口定义
6.1  卡片管理接口类  FFTTMKeyManager
6.1.1 初始化
函数原型
public static getInstance()
函数名称 getInstance
说明 初始化相关类属性,通过 FFTTMKeyManager 类实现单例对象
getInstance()进行调用
请求参数
参数名 参数名称 类型 描述 必填
响应参数
参数名 参数名称 类型 描述
调用:FFTTMKeyManager.getInstance()
返回:无
异常:无

### **6.1.2** 获取 **SDK** 版本号 

函数原型 

public getSDKVersion() 

|函数名称|getSDKVersion|||
|---|---|---|---|
|说明|获取SDK的版本号信息|||
|请求参数||||
|参数名|类型|描述|必|

5 

上海方付通科技服务股份有限公司 

|响应参数 |||填|
|---|---|---|---|
|参数名|类型|描述||
||string|SDK  API的版本信息|Y|

调用:FFTTMKeyManager.getInstance().getSDKVersion(); 

返回:string 

异常:无 

#### 函数原型 

### **6.1.3** 设置 **BIP** 模式参数 

public setBipServiceParams(bsp: BIPServiceParams | null) 

|函数名称|setBipServiceParams|||
|---|---|---|---|
|说明|设置BIP模式通讯的参|数信息||
|请求参数||||
|参数名|类型|描述|必 填|
|bsp|BIPServiceParams|参数信息 见BIPServiceParams描述|N|
|响应参数||||
|参数名|类型|描述||
|配置参数||||

调用:FFTTMKeyManager.getInstance().setBipServiceParams (obj); 返回:无 异常:无 

### **6.1.4** 获取 **BIP** 模式参数 

#### 函数原型 

public getBipServiceParams() 

|函数名称|getBipServiceParams|||
|---|---|---|---|
|说明|获取BIP模式通讯的|参数信息||
|请求参数 ||||
|参数名|类型|描述|必 填|
|响应参数 ||||
|参数名|类型|描述||
|配置参数|BIPServiceParams||
参数信息 见BIPServiceParams 描述|N|

6 

上海方付通科技服务股份有限公司 

null 

调用:FFTTMKeyManager.getInstance().getBipServiceParams (); 返回:BIPServiceParams | null 异常:无 

### **6.1.5** 判断是否有贴膜卡 

#### 函数原型 

public fftHasVCard(block: TMKCompleteResBlock) 

|函数名称|fftHasVCard|||
|---|---|---|---|
|说明|检测手机上是否有可|正常使用的贴膜卡||
|请求参数 ||||
|参数名 响应参数 |类型 |描述 |必 填|
|参数名|类型|描述||
|回参信息体|TMKeyResponse|返回的结果类,参见TMKeyResponse类 若status = FFT_SUCCESS,则参考 hasCard,true有卡,false无卡|Y|

调用:FFTTMKeyManager.getInstance().fftHasVCard (); 返回:TMKeyResponse 结果类 异常:无 

### **6.1.6** 关闭通信通道 

#### 函数原型 

public closeChannel() 

|函数名称|closeChannel|||
|---|---|---|---|
|说明|关闭通信通道|||
|请求参数||||
|参数名|类型|描述|必 填|
|响应参数||||
|参数名|类型|描述||

7 

上海方付通科技服务股份有限公司 

调用:FFTTMKeyManager.getInstance().closeChannel (); 返回:无 异常:无 

。 

### **6.1.7** 获取卡号 

函数原型 

public fftGetCardNumber (block: TMKCompleteResBlock) 

|函数名称|fftGetCardNumber|||
|---|---|---|---|
|说明|获取卡号 83开头表示方付通|||
|请求参数 ||||
|参数名|类型|描述|必 填|
|响应参数 ||||
|参数名|类型|描述||
|回参信息体|TMKeyResponse|返回的结果类,参见TMKeyResponse类 若status = FFT_SUCCESS, 则msg返 回卡号信息|Y|

调用:FFTTMKeyManager.getInstance().fftGetCardNumber (); 

返回:TMKeyResponse 结果类 异常:无 

### **6.1.8** 获取卡片载体信息 

#### 函数原型 

public fftGetDeviceInfo (block: TMKCompleteResBlock) 

|函数名称|fftGetDeviceInfo|||
|---|---|---|---|
|说明|获取卡贴载体信息|||
|请求参数||||
|参数名|类型|描述|必 填|
|响应参数||||
|参数名|类型|描述||
|回参信息体|TMKeyResponse|返回的结果类,参见TMKeyResponse类|Y|

8 

上海方付通科技服务股份有限公司 

若 status = FFT_SUCCESS ,则参考 deviceModel 信息体 

调用:FFTTMKeyManager.getInstance().fftGetDeviceInfo (); 返回:TMKeyResponse 结果类 异常:无 

### **6.1.9** 读取证书信息 

#### 函数原型 

fftGetCertInfo(certType: TMKeyCertType, hashFlag: boolean, block: TMKCompleteResBlock) 

|函数名称|fftGetCertInfo|||
|---|---|---|---|
|说明|根据参数读取卡片里|对应的证书信息||
|请求参数 ||||
|参数名|类型|描述|必 填|
|certType|TMKeyCertType|证书类型,RSA | SM2参见 TMKeyCertType说明|Y|
|hashFlag|boolean|是否是读取证书的Hash值信息|Y|
|响应参数 ||||
|参数名|类型|描述||
|回参信息体|TMKeyResponse|返回的结果类,参见TMKeyResponse类 若status = FFT_SUCCESS,则参考 certModel信息体|Y|

调用:FFTTMKeyManager.getInstance().fftGetCertInfo (‘’, false); 返回:TMKeyResponse 结果类 异常:无 

### **6.1.10** 卡片是否是初始密码 

#### 函数原型 

public fftIsInitialPin (block: TMKCompleteResBlock) 

|函数名称|fftIsInitialPin|||
|---|---|---|---|
|说明|判断当前卡片是否是初始密码|||
|请求参数||||
|参数名|类型|描述|必 填|
|响应参数||||

9 

上海方付通科技服务股份有限公司 

|参数名|类型|描述||
|---|---|---|---|
|回参信息体|TMKeyResponse|返回的结果类,参见TMKeyResponse类 若status = FFT_SUCCESS,则参考 isInitPin值,true是初始密码,false不是 初始密码|Y|

调用:FFTTMKeyManager.getInstance().fftIsInitialPin (); 

返回:TMKeyResponse 结果类 

异常:无 

6.1.11 校验 Pin 码
函数原型
public fftVerifyPin (pinHex: string, block: TMKCompleteResBlock)
函数名称 fftVerifyPin
说明 校验 PIN 码是否正确
请求参数
参数名 类型 描述 必
填
pinHex  string  Hex 编码格式的密文 Pin  Y
响应参数
参数名 类型 描述
回参信息体 TMKeyResponse  返回的结果类,  参见 TMKeyResponse 类 Y
若 status = FFT_SUCCESS,则表示校验
通 过 , status  =
FFT_PASSWORD_INVALID  状态时,
pNum 表示密码剩余可操作次数

调用:FFTTMKeyManager.getInstance().fftVerifyPin (); 返回:TMKeyResponse 结果类 异常:无 

### **6.1.12** 初始密码时,设置 **PIN** 码接口 

#### 函数原型 

public fftSetNewPin (pinHex: string, block: TMKCompleteResBlock) 

|函数名称|fftSetNewPin|
|---|---|
|说明|设置密码信息|
||注:只有密码是初始密码时,此接口才能正常调用|

10 

上海方付通科技服务股份有限公司 

请求参数
参数名 类型 描述 必
填
pinHex  string  Hex 编码格式的密文 Pin  Y
响应参数
参数名 类型 描述
回参信息体 TMKeyResponse  返回的结果类,  参见 TMKeyResponse 类 Y
若 status = FFT_SUCCESS,则表示校验
通 过 , status  =
FFT_PASSWORD_INVALID  状态时,
pNum 表示密码剩余可操作次数

调用:FFTTMKeyManager.getInstance().fftSetNewPin (); 

返回:TMKeyResponse 结果类 

异常:无 

### **6.1.13** 修改密码 

#### 函数原型 

public fftChangePin (oldPinHex: string, pinHex: string, block: TMKCompleteResBlock) 

|
函数名称|
fftChangePin|||
|---|---|---|---|
|说明|修改密码接口,输|入旧Pin和新Pin||
|请求参数 ||||
|参数名|类型|描述|必 填|
|oldPinHex|string|Hex编码格式的密文原Pin|Y|
|pinHex|string|Hex编码格式的密文新Pin|Y|
|响应参数 ||||
|参数名|类型|描述||
|回参信息体|TMKeyResponse|返回的结果类,参见TMKeyResponse类 若status = FFT_SUCCESS,则表示校验 通 过 , status = FFT_PASSWORD_INVALID状态时, pNum表示密码剩余可操作次数|Y|

调用:FFTTMKeyManager.getInstance().fftChangePin (); 返回:TMKeyResponse 结果类 异常:无 

11 

上海方付通科技服务股份有限公司 

### **6.1.14** 获取 **Pin** 码当前剩余输入次数 

#### 函数原型 

public fftGetPinRemainNums (block: TMKCompleteResBlock) 

|函数名称|fftGetPinRemainNum|s||
|---|---|---|---|
|说明 请求参数 |获取Pin 码剩余输 试机会后锁卡 |入次数,通过此接口可以知道卡片还剩多少 |次尝 |
|参数名 响应参数 |类型 |描述 |必 填|
|参数名|类型|描述||
|回参信息体|TMKeyResponse|返回的结果类,参见TMKeyResponse类 若status = FFT_SUCCESS,pNum表示 密码剩余可操作次数|Y|

调用:FFTTMKeyManager.getInstance().fftGetPinRemainNums (); 返回:TMKeyResponse 结果类 异常:无 

### **6.1.15** 重置密码 **-** 第一步:获取重置 **Pin** 码的身份验证信息 

#### 函数原型 

public fftGetResetCiphertext (certType: TMKeyCertType, block: TMKCompleteResBlock) 

|
函数名称|
fftGetResetCiphertext||
|---|---|---|
|说明|重置Pin 第一步,获取重置密码的身份验证信息,需要发送服 校验|务器|
|请求参数 |||
|参数名|类型 描述|必 填|
|certType 响应参数|TMKeyCertType 加密时使用的证书类型 NXY卡片使用: FFT_CERTTYPE_RSA2048_SIGN CFCA卡片使用: FFT_CERTTYPE_SM2_ENCRYPT|Y|
|参数名|类型 描述||
|回参信息体|TMKeyResponse 返回的结果类,参见TMKeyResponse类 若status = FFT_SUCCESS,msg表示卡|Y|

12 

上海方付通科技服务股份有限公司 

片返回的密文信息体 

调用:FFTTMKeyManager.getInstance().fftGetResetCiphertext (); 返回:TMKeyResponse 结果类 异常:无 

### **6.1.16** 重置密码 **-** 第二步:密码重置验证,下发服务器信息 

函数原型
public fftResetPin (encryptHex: string, block: TMKCompleteResBlock)
函数名称 fftResetPin
说明 重置 Pin 第二步,重置 Pin 信息接口,需要下发服务器返回的信息
体
请求参数
参数名 类型 描述 必
填
encryptHex  string  服务器下发的加密信息。 Y
在服务器校验了 5.1.15 接口返回的信息
后,对上送的信息做加密,得到的密文
Hex 编码格式
响应参数
参数名 类型 描述
回参信息体 TMKeyResponse  返回的结果类,  参见 TMKeyResponse 类 Y
若 status = FFT_SUCCESS,表示重置成
功,卡片密码会被重置为初始密码

调用:FFTTMKeyManager.getInstance().fftResetPin (); 返回:TMKeyResponse 结果类 异常:无 

### **6.1.17** 自动开闭签名模式 **-** 仅 **NXY** 卡支持 

函数原型 

public fftAutoShutDown(autoType: TMKeyAutoShutDownType, block: TMKCompleteResBlock) 

|函数名称|fftAutoShutDown||
|---|---|---|
|说明|自动开闭签名确认模式, 注:农信银证书支持,CFCA不支持||
|请求参数|||
|参数名|类型 描述|必 填|

13 

上海方付通科技服务股份有限公司 

|autoType 响应参数 |TMKeyAutoShutDown Type |开启自动关闭模式 或者 模 式 - 类 型 值 TMKeyAutoShutDownType |关闭自动关闭 , 参 见 说明|Y|
|---|---|---|---|---|
|参数名|类型|描述|||
|回参信息体|TMKeyResponse|返回的结果类,参见TMKe 若status = FFT_SUCCESS|yResponse类 ,表示成功|Y|

调用:FFTTMKeyManager.getInstance().fftAutoShutDown (); 

返回:TMKeyResponse 结果类 异常:无 

### **6.1.18** 数据签名 

#### 函数原型 

public fftSign(plainHex: string, certType: TMKeyCertType, algType: TMKeyAlgType, pinHex: string, sdkHash: boolean, 

block: TMKCompleteResBlock) 

|函数名称|fftSign|||
|---|---|---|---|
|说明|下发待签数据,返处|理好的PKCS7格式签名结果||
|请求参数 ||||
|参数名|类型|描述|必 填|
|plainHex|string|Hex编码格式的原始签名信息体|Y|
|certType|TMKeyCertType|签名时需要用的证书类型,参见 TMKeyCertType说明 默认支持 : FFT_CERTTYPE_RSA2048_SIGN FFT_CERTTYPE_SM2_SIGN|Y|
|algType|TMKeyAlgType|签名时使用的摘要算法,参见 TMKeyAlgType说明 FFT_Algorithm_SM3只对应SM2 国密 签名|Y|
|pinHex|string|Hex编码格式的密文Pin|Y|
|sdkHash|boolean|是否是SDK做Hash值处理|Y|
|响应参数||||
|参数名|类型|描述||
|回参信息体|TMKeyResponse|返回的结果类,参见TMKeyResponse类 若status = FFT_SUCCESS,则msg是 base64格式的PKCS7签名信息|Y|

调用:FFTTMKeyManager.getInstance().fftSign (); 

14 

上海方付通科技服务股份有限公司 

返回:TMKeyResponse 结果类 

异常:无 

### **6.1.19 COS** 在线更新 

#### 函数原型 

public fftCosUpdate(url: string, block: TMKCompleteResBlock) 

|函数名称|fftCosUpdate|||
|---|---|---|---|
|说明|在线进行卡片的CO|S信息更新操作||
|请求参数 ||||
|参数名|类型|描述|必 填|
|url|string|请求COS后台服务器的URL信息|Y|
|响应参数 ||||
|参数名|类型|描述||
|回参信息体|TMKeyResponse|返回的结果类,参见TMKeyResponse类 若status = FFT_SUCCESS,表示升级成 功|Y|

调用:FFTTMKeyManager.getInstance().fftCosUpdate (); 返回:TMKeyResponse 结果类 异常:无 

### **6.1.20 NXY** 证书更新 初始化 

#### 函数原型 

public fftCertInitialNXY(pinHex: string, certList: Array<TMKeyNXYCertUpdateModel>, block: TMKeyNXYCertUpdateResBlock) 

|函数名称|fftCertInitialNXY||||
|---|---|---|---|---|
|说明|NXY证书更新,初始|化卡片,获取P10签名|||
|请求参数 |||||
|参数名|类型|描述||必 填|
|pinHex|string|Hex编码格式的密文Pin||Y|
|certList|Array<TMKeyNXYCe rtUpdateModel>|需要更新的证书类型信息目录, 型参见TMKeyNXYCertUpdateM|结构类 odel|Y|
|响应参数 |||||
|参数名|类型|描述|||
|回参信息体|Block|返 回 的 结 果 类 , TMKeyNXYCertUpdateModel|参 见 和|Y|

15 

上海方付通科技服务股份有限公司 

|TMKeyResponse 类|
|---|
|若status = FFT_SUCCESS,p10Model就|
|是返回的初始化信息体,base64格式|

调用:FFTTMKeyManager.getInstance().fftCertInitialNXY (); 返回:TMKeyResponse 结果类 异常:无 

#### 函数原型 

### **6.1.21 NXY** 证书更新 导入证书信息 

public fftCertImportNXY(certUpdateModel: TMKeyNXYCertUpdateModel, block: TMKCompleteResBlock) 

|函数名称|fftCertImportNXY|||
|---|---|---|---|
|说明|NXY更新证书导入证|书及秘钥对信息||
|请求参数 ||||
|参数名|类型|描述|必 填|
|certUpdateModel|TMKeyNXYCertUpdat eModel|服务器返回的证书信息,参见 TMKeyNXYCertUpdateModel说明|Y|
|响应参数 ||||
|参数名|类型|描述||
|回参信息体 |TMKeyResponse |返回的结果类,参见TMKeyResponse类 若status = FFT_SUCCESS,表示证书更 新成功 |Y|

调用:FFTTMKeyManager.getInstance().fftCertImportNXY (); 返回:TMKeyResponse 结果类 异常:无 

### **6.1.22 CFCA** 证书更新 初始化 

#### 函数原型 

public fftCertInitialCFCA(pinHex: string, block: TMKeyCFCACertUpdateResBlock) 

|函数名称|fftCertInitialCFCA||
|---|---|---|
|说明|CFCA证书更新,初始化卡片,获取P10签名||
|请求参数|||
|参数名|类型 描述|必 填|

16 

上海方付通科技服务股份有限公司 

|pinHex|string|Hex编码格式的密文Pin||Y|
|---|---|---|---|---|
|响应参数 |||||
|参数名|类型|描述|||
|回参信息体|Block|返 回 的 结 果 类 TMKeyCFCAPTenModel TMKeyResponse 类 若status = FFT_SUCCESS, 就是返回的初始化信息体,|, 参 见 和 pTenModel base64格式|Y|

调用:FFTTMKeyManager.getInstance().fftCertInitialCFCA (); 

返回:TMKeyResponse 结果类 异常:无 

### **6.1.23 CFCA** 证书更新 导入证书信息 

函数原型 public fftCertImportCFCA(certList: Array<TMKeyCFCAImportCertModel>, block: TMKCompleteResBlock) 

|函数名称|fftCertImportCFCA|||
|---|---|---|---|
|说明|CFCA更新证书导入证|书及秘钥对信息||
|请求参数 ||||
|参数名|类型|描述|必 填|
|certList|Array<TMKeyCFCAI mportCertModel>|服务器返回的证书信息体,参见 TMKeyCFCAImportCertModel说明|Y|
|响应参数 ||||
|参数名|类型|描述||
|回参信息体|TMKeyResponse|返回的结果类,参见TMKeyResponse类 若status = FFT_SUCCESS,表示证书更 新成功|Y|

调用:FFTTMKeyManager.getInstance().fftCertImportCFCA (); 返回:TMKeyResponse 结果类 

异常:无 

### **6.1.24** 设置 **UIContext** 

函数原型 

public setUIContext (context: UIContext) 

17 

上海方付通科技服务股份有限公司 

|函数名称|setUIContext|||
|---|---|---|---|
|说明|设置UIContext,用|于设备绑定验证弹框时使用||
|请求参数||||
|参数名|类型|描述|必 填|
|context|UIContext|应用上下文对象|N|
|响应参数||||
|参数名|类型|描述||

调用:FFTTMKeyManager.getInstance().setUIContext (ctx); 返回:无 异常:无 

### **6.1.25** 设置开启设备绑定验证相关逻辑 

#### 函数原型 

public setTMKeySmsParams(smsParams: TMKeySmsParams | null) 

|函数名称|setTMKeySmsParams|||
|---|---|---|---|
|说明|设置开启设备绑定验证|相关逻辑||
|请求参数||||
|参数名|类型|描述|必 填|
|smsParams|TMKeySmsParams|参数信息 见TMKeySmsParams 描述|N|
|响应参数||||
|参数名|类型|描述||

调用:FFTTMKeyManager.getInstance().setTMKeySmsParams (obj); 返回:无 异常:无 

### **6.1.26** 设置每次通信时对设备的校验码 

#### 函数原型 

public setVerifyCode(smsCode: string) 

|函数名称|setVerifyCode|
|---|---|
|说明|设置每次通信时对设备的校验码|
|请求参数||

18 

上海方付通科技服务股份有限公司 

|参数名|类型||描述|必 填|
|---|---|---|---|---|
|smsCode|string|一次性验证码||N|
|响应参数|||||
|参数名|类型||描述||

调用:FFTTMKeyManager.getInstance().setVerifyCode (smsCode); 返回:无 

异常:无 

# 6.2 **Model** 类数据 

### **6.2.1 TMKeyResponse** 

```
/**
```

`*` 返回结果的 `Model` 类 

```
 */
export class TMKeyResponse {
/**
```

`*` 接口状态值 `*/` 

```
public status: TMKeyReadResultStatus =
TMKeyReadResultStatus.FFT_OPERATION_CANCEL
/**
```

`*` 接口状态码 可能为空 

```
   */
public code: string = ''
/**
```

`*` 接口描述 返回值信息 `|` 错误信息 可能为空 `*/` 

```
public msg: string = ''
/**
```

`*` 若是带 `PIN` 接口 为 `PIN` 剩余可试次数 `*/` 

```
public pNum: number = -1
```

19 

上海方付通科技服务股份有限公司 

/**
   *  是否有卡
   */
public  hasCard: boolean =  false ;
/**
   *  是否是农信银 CA  证书
   */
public  isNxyOrgCert: boolean =  false ;
/**
   *  是否是初始密码
   */
public  isInitPin: boolean =  false ;
/**
   *  卡片信息
   */
public  deviceModel: TMKeyDeviceModel| null =  null ;
/**
   *  卡片证书信息
   */
public  certModel: TMKeyCertModel| null =  null ;
}

### **6.2.2 TMKeyDeviceModel** 

/**
 *  设备信息类
 */
export class  TMKeyDeviceModel {
/**
   *  卡片状态 信息
   */
public  dataCardStatus: number[] = []
/**
   *  商户信息
   */
public  merchantInfo: string = ''

20 

上海方付通科技服务股份有限公司 

/**
   * COS  版本
   */
public  cosVersion: string = ''
/**
   *  序列号
   */
public  serialNumber: string = ''
/**
   * SDK  版本号
   */
public  sdkVersion: string = ''
/**
   *  所有数据
   */
public  deviceArray: number[] = []
//00 :已个人化未生成密钥对
//01 :已生成密钥对未预制证书
//10 :已预制证书
// 其他值:状态异常
/**
   * RSA1024  证书状态
   */
public  rsa1024Status: number = -1
/**
   * RSA2048  证书状态
   */
public   rsa2048Status: number = -1
/**
   *  国密签名证书状态
   */
public  sm2SignStatus: number = -1
/**
   *  国密加密证书状态
   */
public  sm2EnStatus: number = -1
/**

21 

上海方付通科技服务股份有限公司 

`* CFCA` 证书状态 `*/` **`public`** `cfcaCertStatus: string = ""; /** * CFCA COS ATR` 信息 `*/` **`public`** `cfcaCosAtrStr: string = ""; /** * CFCA` 证书版本信息 `*/` **`public`** `cfcaCertVersionStr: string = ""; }` 

### **6.2.3 TMKeyCertModel** 

`/** *` 证书信息类 `*/` **`export class`** `TMKeyCertModel { /** *` 证书序列号 `*/` **`public`** `hexSerialNumber: string = '' /** *` 大数表示的证书序列号 `*/` **`public`** `bigNumSerialNumber: string = '' /** *` 证书版本号 `*/` **`public`** `certVersion: string = '' /** *` 颁发者信息 `*/` **`public`** `issuerInfo: string = '' /** *` 持有者信息 `*/` **`public`** `holderInfo: string = '' /**` 

22 

上海方付通科技服务股份有限公司 

   *  有效期开始日期

```
   */
```

**`public`** `startDate: string = '' /** *` 有效截止日期 `*/` 

**`public`** `endDate: string = '' /** *` 公钥信息 `*/` 

**`public`** `publicKeyInfo: string = '' /** *` 指纹 `*/` 

**`public`** `fingerprint: string = '' /** *` 证书信息体 `*/` **`public`** `certData: number[] = []; }` 

### **6.2.4 BIPServiceParams** 

**`export class`** `BIPServiceParams { /** *` 服务器域名信息 `*/` **`public`** `serverBaseUrl: string = ""; /** *` 集成方 `APP` 绑定的对象 卡号 `No` (必须) `*/` **`public`** `appBindCardNo: string = ""; /** *` 申请使用的 `SDK` 键值对 `key */` **`public`** `bindApiKey: string = ""; /** *` 申请使用的 `SDK` 键值对 `value */` **`public`** `bindApiSecret: string = ""; /** * SDK` 工作的环境 默认是 `false` 

23 

上海方付通科技服务股份有限公司 

```
   */
public sdkReleaseFlag: boolean = false;
}
```

### **6.2.5 TMKeyNXYCertUpdateModel** 

export class  TMKeyNXYCertUpdateModel {
/**
   *  证书类型
   * certInitial -  入参使用
   */
public  certType: TMKeyCertType =
TMKeyCertType.FFT_CERTTYPE_SM2_SIGN
/**
   *  算法标识
   * certInitial -  入参使用
   */
public  algType: TMKeyAlgType =
TMKeyAlgType.FFT_Algorithm_SM3
/**
   *  证书  DN  信息值
   * certInitial -  入参使用
   */
public  certDNStr: string = ''
/**
   * RSA  公钥 ,  失败时为 ""
   * certInitial -  出参使用
   */
public  rsaPK = ''
/**
   * RSA  签证书请求  Base64 , 失败时为 ""
   * certInitial -  出参使用
   */
public  rsaP10 = ''
/**

24 

上海方付通科技服务股份有限公司 

   * SM2  签名证书请求  Base64,  失败时为 ""
   * certInitial -  出参使用
   */
public  sm2P10 = ''
/**
   * SM2  公钥 ,  失败时为 ""
   * certInitial -  出参使用
   * certImport -  入参使用
   */
public  sm2PK = ''
/**
   * RSA  签名证书 ( 空时为 "")
   * certImport -  入参使用
   */
public  rsaSignCert = ''
/**
   * SM2  签名证书 ( 空时为 "")
   * certImport -  入参使用
   */
public  sm2SignCert = ''
/**
   * SM2  加密证书 ( 空时为 "")
   * certImport -  入参使用
   */
public  sm2EncCert = ''
/**
   *  加密证书私钥密文(使用保护密钥加密)空时为 ""
   * certImport -  入参使用
   */
public  encPriKey = ''
/**
   *  加密证书私钥保护密钥密文(使用 SM2  签名证书公钥加密)空时为 ""
   * certImport -  入参使用
   */
public  encPriProKey = ''
}

25 

上海方付通科技服务股份有限公司 

### **6.2.6 TMKeyCFCAPTenModel** 

export class  TMKeyCFCAPTenModel {
/**
   *   证书  keyId
   */
public  cfcaCode: string = ''
/**
   *   证书  List
   */
public  list: Array<TMKeyCFCAPTenKey> = []
}
export class  TMKeyCFCAPTenKey {
/**
   *   证书  SN
   */
public  serialNum: string = ''
/**
   *   证书  P10  信息
   */
public  pTen: string = ''
/**
   *   证书 类型
   */
public  certType: string = ''
/**
   *   生成的加密公钥
   */
public  pubKey: string = ''
}

### **6.2.7 TMKeyCFCAImportCertModel** 

```
export class TMKeyCFCAImportCertModel {
```

26 

上海方付通科技服务股份有限公司 

`/** *` 证书 索引值 `*/` **`public`** `certRefKey: string = '' /** *` 证书 种类标识符 `*/` **`public`** `keyAlg: string = '' /** *` 证书 类型 长度 `*/` **`public`** `keyLength: string = '' /** *` 证书 等级 `*/` **`public`** `certLevel: string = '' /** *` 证书 签名证书 `*/` **`public`** `signatureCert: string = '' /** *` 证书 加密证书 `*/` **`public`** `encryptionCert: string = '' /** *` 证书 保护秘钥对 `*/` **`public`** `encryptionPrivateKey: string = '' }` 

### **6.2.8 TMKeyReadResultStatus** 

```
export enum TMKeyReadResultStatus {
FFT_START,
```

`FFT` `_` `SUCCESS,                        //` 操作成功 `FFT` `_` `CHECK` `_` `DEVICE` `_` `FAIL,              //` 未找到卡 `FFT` `_` `SEND` `_` `CMD` `_` `FAIL,                  //` 发送指令数据失败 `FFT` `_` `RECEIVE` `_` `DATA` `_` `FAIL,              //` 接收响应数据失败 `FFT` `_` `OPERATION` `_` `FAILED,               //` 操作失败 `FFT` `_` `OPERATION` `_` `CANCEL,               //` 操作取消 `FFT` `_` `DEVICE` `_` `BUSY,                    //` 设备忙 `FFT` `_` `INVALID` `_` `PARAMETER,              //` 参数错误 

27 

上海方付通科技服务股份有限公司 

`FFT` `_` `PASSWORD` `_` `INVALID,               //` 密码错误 `FFT` `_` `NO` `_` `CERT,                        //` 没有找到证书或对应密钥对 `FFT` `_` `CERT` `_` `INVALID,                   //` 证书格式不正确 `FFT` `_` `OTHER` `_` `ERROR,                    //` 其他错误 `FFT` `_` `MAC` `_` `ERROR,                      //MAC` 错误 `FFT` `_` `PERMISSION` `_` `DENIED,              //` 安全状态不满足 `FFT` `_` `INVALID` `_` `DATA,                   //` 数据无效 `FFT` `_` `NOT` `_` `MET` `_` `CONDITION,              //` 条件不满足 `FFT` `_` `APPLICATION` `_` `NOT` `_` `OPEN,           //` 应用未打开 `FFT` `_` `APPLICATION` `_` `OPEN,               //` 应用已打开 `FFT` `_` `FUNCTION` `_` `NOT` `_` `SUPPORT,           //` 功能不支持 `FFT` `_` `SPACE` `_` `INSUFFICIENT,             //` 空间不足 `FFT` `_` `DATA` `_` `ERROR,                     //` 数据错误 `FFT` `_` `CONTAINER` `_` `NOT` `_` `FOUND,            //` 容器未找到 `FFT` `_` `CERT` `_` `TYPE` `_` `NOT` `_` `FOUND,            //` 证书类型未找到 `FFT` `_` `CERT` `_` `DATA` `_` `ERROR,                //` 证书数据错误 `FFT` `_` `CONTAINER` `_` `NOT` `_` `OPEN,             //` 容器未打开 `FFT` `_` `INSTRUCTION` `_` `NOT` `_` `SUPPORT,        //` 指令不支持 `FFT` `_` `INSTRUCTION` `_` `FORMAT` `_` `ERROR,       //` 指令格式错误 `FFT` `_` `CLA` `_` `DOESNOT` `_` `SUPPORT,            //CLA` 不支持 `FFT` `_` `GROUND` `_` `API` `_` `OPERATION` `_` `ERROR,     //` 底层接口运算错误 `FFT` `_` `COUNTER` `_` `ERROR,                  //Counter` 值错误 `FFT` `_` `PIN` `_` `LOCK,                       //PIN` 码锁定 `FFT` `_` `COMM` `_` `ERROR,                     //` 通讯错误 `FFT` `_` `CERT` `_` `EXPIRED,                   //` 证书过期 `FFT` `_` `CERT` `_` `NOT` `_` `FROM` `_` `FUTURE,           //` 证书未生效 `FFT` `_` `PASSWORD` `_` `INVALID` `_` `LENGTH,        //` 密码长度错误 `FFT` `_` `CERT` `_` `NOTMATCHIZE,               //` 应用已存在 `FFT` `_` `SIGN` `_` `MESSAGE` `_` `ERROR,             //` 签名报文格式不正确 `FFT` `_` `SIGN` `_` `ALG` `_` `ERROR,                 //` 签名算法错误 `FFT` `_` `FILEINFO` `_` `NOT` `_` `EXIST,             //` 文件信息不存在 `FFT` `_` `CREAT` `_` `P10` `_` `ERROR,                //` 生成 `P10` 错误 `FFT` `_` `BIP` `_` `CARD` `_` `DROPS,                 //BIP` 服务卡片不在线 `FFT` `_` `BIP` `_` `CARD` `_` `NOTMATCH,              //BIP` 服务未匹配到卡片 `FFT` `_` `BIP` `_` `CARD` `_` `DESTROY,               //BIP` 服务检测到卡片注销、停 用、挂失 `FFT` `_` `SMS` `_` `VERIFY` `_` `CANCEL,              //STK` 界面 验证码取消操作 `FFT` `_` `SMS` `_` `VERIFY` `_` `FAILED,              //STK` 界面 验证码验证失败操作 `FFT` `_` `SMS` `_` `BINDING` `_` `CARD` `_` `REFUSED,       //` 绑定验证码弹出框 拒绝授权 `}` 

28 

上海方付通科技服务股份有限公司 

### **6.2.9 TMKeySmsParams** 

export class  TMKeySmsParams {
/**
   *  设置 SDK  是否验证卡片唯一性 默认不校验
   *  校验标识  true  校验,  false  不校验
   */
public  sdkVerifyCardUnique: boolean =  false ;
/**
   *  状态改变时的 提示语
   */
public  cardSMSChangeBindingMsg: string = ' 设备已更换,请输入
授权码进行绑定操作 ';
/**
   *  首次时的 提示语
   */
public  cardSMSFirstBindingMsg: string = ' 首次使用薄膜盾,请输
入授权码进行绑定操作 '
/**
   *  首次时 绑定的  STK  提示语
   */
public  cardSMSBindCodeSTKShowMsg: string = ' 请输入授权码,取
消或验证失败将终止交易 '
/************************  增加外部配置信息变量
*********************/
  /**
   * App  设置需要验证卡片唯一性时 验证码 弹框上显示的标题内容颜色
   */
public  cardSMSBindCodeTitleColor: Color = Color.Blue
/**
   * App  设置需要验证卡片唯一性时 验证码 弹框上显示的内容颜色
   */
public  cardSMSBindCodeMsgColor: Color = Color.Black
/**
   * App  设置需要验证卡片唯一性时 验证码 弹框上显示的取消颜色
   */
public  cardSMSBindCodeCancelColor: Color = Color.Blue
/**
   * App  设置需要验证卡片唯一性时 验证码 弹框上显示的确定颜色

29 

上海方付通科技服务股份有限公司 

```
   */
public cardSMSBindCodeConfirmColor: Color = Color.Blue
}
```

# **7** 密码键盘使用说明 **– CFCA** 证书使用 

7.1 TMKeyKeyboard  组件
包含以下对外使用的属性
/**
 *  双向关联集成界面的输入框内容信息
 */
@Link showInputValue: string
/**
 *  键盘上的标题文案
 */
public  bankTitle: string = " 安全键盘 "
/**
 *  控制键盘的  VC
 */
public  controller: TextInputController | null =  null
/**
 *  最大输入 长度,  > 0  有效,   <= 0  时 不控制长度
 */
public  maxLen: number = 0
/**
 *  不允许输入的 字符串集合
 */
public  unAllowList: Array<string> = []
/**
 *  允许输入的 字符串集合
 */
public  allowList: Array<string> = []
/**
 *  密码信息 回调函数
 */
public  callBack: ( (status: boolean, msg: string, hash:
string) => void ) | null =  null

30 

上海方付通科技服务股份有限公司 

## **7.2** 例子展示 

private  enNewValue: string = ''
private  enNewHash: string = ''
pwdNewController: TextInputController =  new
TextInputController()
@Builder
tmkKeyboardNew() {
if  ( this .pinType == PinDialogType.CFCA) {
TMKeyKeyboard({
showInputValue: $newPin,
controller:  this .pwdNewController,
maxLen: 6,
callBack: (status: boolean, msg: string, hash: string)
=> {
if  (status) {
this .enNewValue = msg
this .enNewHash = hash
          LibLogUtils.logD( this .TAG, " 密文信息  = " + msg)
LibLogUtils.logD( this .TAG, "hash  比对信息  = " + hash)
}  else  {
promptAction.showToast({
message: msg,
duration: 3000
})
}
      }
    })
}
}
build() {
Column() {
Row() {
Text(" 新密码 :")
.align(Alignment.Start)
.fontSize(16)
.height(45)
.fontWeight(FontWeight.Normal)

31 

上海方付通科技服务股份有限公司 

`.margin({ left: 10, right: 10 }) TextInput({ placeholder: '` 请输入新密码 `', text:` **`this`** `.newPin, controller:` **`this`** `.pwdNewController }) .maxLength(6) .type(` **`this`** `.pinType != PinDialogType.CFCA ? InputType.NUMBER_PASSWORD : InputType.Normal) .height(45) .width('70%') .onChange((value: string) => {` **`if`** `(` **`this`** `.pinType != PinDialogType.CFCA )` **`this`** `.newPin = value }) .customKeyboard(` **`this`** `.pinType == PinDialogType.CFCA ?` **`this`** `.tmkKeyboardNew() :` **`null`** `, {supportAvoidance:` **`true`** `} ) } .margin({ top: 20 }) .width('90%') .justifyContent(FlexAlign.End) }` 

32
