# **爱加密移动应用密钥白盒SDK** 

## **集成手册(Harmony)** 

**V2.4.0** 

文档密级:完全公开 

北京智游网安科技有限公司 

爱加密移动应用密钥白盒SDK 集成手册(HarmonyOS) 

###### **■ 版权声明** 

本文档中出现的文字叙述、文档格式、插图、照片、方法、过程等内容,除另有特别 注明,版权均属智游网安所有,受到有关产权及版权法保护。任何个人、机构未经智游网 安的书面授权许可,不得以任何方式复制或引用本文的任何片断。 

###### **■免责条款** 

本文档所含内容仅用于为平台最终用户提供信息,如内容有更改或撤回,恕不另行通 知。本公司已尽最大努力保证资料的准确可靠,但不提供任何形式的担保。 

北京智游网安科技有限公司 

第i 页 

爱加密移动应用密钥白盒SDK 集成手册(HarmonyOS) 

###### **目录** 

|**1 文档定义....................................................................................................................1**|
|---|
|1.1 编写目的.................................................................................................................................. 1|
|1.2 适用范围.................................................................................................................................. 1|
|1.3 术语与缩略语..........................................................................................................................1|
|1.4 运行环境.................................................................................................................................. 1|
|**2 使用场景介绍.............................................................................................................2**|
|**3 鸿蒙移动端SDK 集成................................................................................................3**|
|3.1 集成环境.................................................................................................................................. 3|
|3.2 Deveco Studio 导入har 包.................................................................................................3|
|**4 接口说明....................................................................................................................3**|
|4.1 初始化白盒模块......................................................................................................................3|
|4.2 获取白盒密钥..........................................................................................................................4|
|4.3 AES 加解密...............................................................................................................................4|
|4.3.1 加密(ECB).................................................................................................................... 4|
|4.3.2 解密(ECB).................................................................................................................... 5|
|4.3.3 加密(CBC)....................................................................................................................5|
|4.3.4 解密(CBC)....................................................................................................................6|
|4.3.5 加密(GCM).................................................................................................................. 7|
|4.3.6 解密(GCM).................................................................................................................. 8|
|4.4 SM4 加解密............................................................................................................................. 9|
|4.4.1 加密(ECB).................................................................................................................... 9|
|4.4.2 解密(ECB)..................................................................................................................10|
|4.4.3 加密(CBC)..................................................................................................................11|
|4.4.4 解密(CBC)..................................................................................................................12|
|4.4.5 加密(GCM)................................................................................................................12|
|4.4.6 解密(GCM)................................................................................................................13|
|4.5 JS 调用加解密接口...............................................................................................................14|
|4.6 具体样例使用解析...............................................................................................................15|
|4.6.1 字符串加解密示例................................................................................................... 15|
|**5 公司介绍................................................................................................................. 18**|

北京智游网安科技有限公司 

第i 页 

爱加密移动应用密钥白盒SDK 集成手册(HarmonyOS) 

### **1 文档定义** 

#### **1.1 编写目的** 

为了用户更好的了解使用爱加密移动应用安全密钥白盒SDK,使用爱加密移动应用 密钥白盒SDK 的相关功能,特编写该文档。 

#### **1.2 适用范围** 

本文档适用于使用爱加密移动应用密钥白盒SDK 的客户公司内部安全技术人员、测 试人员,爱加密安全技术人员、测试人员、售后实施人员。 

#### **1.3 术语与缩略语** 

###### 说明:本部分主要是对本文档所出现的重要缩略语进行解释 

|**编写、术语**|**解释**|
|---|---|
|AES|高级加密标准,在密码学又称Rijndael 加密法。|
|SM4|国家标准对称分组密码算法。|
|DES|数据加密标准,一种使用密钥加密的块算法。|
|3DES|三重数据加密算法块密码的通称,相当于是对每个数据块应 用三次DES 加密算法。|

#### **1.4 运行环境** 

鸿蒙3.1 (API 9)及以上版本。 

北京智游网安科技有限公司 

第1 页 

爱加密移动应用密钥白盒SDK 集成手册(HarmonyOS) 

### **2 使用场景介绍** 

以下为每个平台下面算法的具体集成步骤以及接口的说明,和自带使用样例的简单解 

释。 

对于网络通信场景下面的加解密,一般常用的场景为: 

- 1 对于参数内容的加密:比如HTTP 的GET 请求里面包含token=“username”, 此时username 假设为账号,比较重要,则可以使用爱加密提供的字符串加密 接口对username 进行加密,假设加密后数据为A,则此时可HTTP 发送数据 里面的token 为:token=“A“。 

- 2 服务端接收到token=“A”以后,可以拿到数据A,然后调用自己的字符串解 密接口对A 进行解密,然后获取到原始数据“username”。 

3 对于有一些数据流的安全防护需求的情形:比如HTTP 的POST 分块请求,其
中一块数据为一个比较重要的图片,原始HTTP 请求为配置信息+ 明文图片
内容,此时可以使用爱加密提供的数据流加密算法,对明文图片内容进行加密,
然后产生密文图片内容。然后HTTP 请求,发送数据为配置信息+ 密文图片
内容。
4 对于服务端接收到:配置信息+ 密文图片内容的POST 请求后,则可以使用自
己的数据流解密接口,对密文图片内容进行解密,然后获取到原始明文图片内容
即可。

- 3 对于有一些数据流的安全防护需求的情形:比如HTTP 的POST 分块请求,其 中一块数据为一个比较重要的图片,原始HTTP 请求为配置信息+ 明文图片 内容,此时可以使用爱加密提供的数据流加密算法,对明文图片内容进行加密, 然后产生密文图片内容。然后HTTP 请求,发送数据为配置信息+ 密文图片 内容。 

- 4 对于服务端接收到:配置信息+ 密文图片内容的POST 请求后,则可以使用自 己的数据流解密接口,对密文图片内容进行解密,然后获取到原始明文图片内容 即可。 

北京智游网安科技有限公司 

第2 页 

爱加密移动应用密钥白盒SDK 集成手册(HarmonyOS) 

### **3 鸿蒙移动端SDK 集成** 

#### **3.1 集成环境** 

DevEco Studio 5.0.3.900 及以上版本。 

#### **3.2 Deveco Studio 导入har 包** 

如图将har 包复制到项目的目录下如图3-1,在oh-package.json5 中增加如图3-1 

**图3-1** 

### **4 接口说明** 

#### **4.1 初始化白盒模块** 

SDK 成功安装以后,需要在调用的代码里面导入需要使用的包,就可以直接使用SDK 中提供的接口进行加解密功能,导入代码如下: 

北京智游网安科技有限公司 

第3 页 

爱加密移动应用密钥白盒SDK 集成手册(HarmonyOS) 

import {IjmWhiteBoxSM4, IjmWhiteBoxAES, ResultObject} from "@ohos/whitebox" ResultObject 对象使用方法参考文末示例 

#### **4.2 获取白盒密钥** 

动态白盒密钥与白盒SDK 绑定进行绑定,获取动态白盒秘钥,需要在爱加密密钥白 盒平台生成。 

#### **4.3 AES 加解密** 

##### **4.3.1 加密(ECB)** 

将字符串进行加密并用Base64 编码,定义如下: 

|/**||
|---|---|
|* * *|将字符串进行AES(ECB 模式)加密 @param key 动态白盒秘钥|
|*|@param inData 待加密字符串|
|*|@param altype 加密类型1 aes128 2 aes192 3 aes256|
|* ** stat|@return ResultObject 加密后的结果对象 / ic aes_ecb_encrypt_string(key: string, inData: string, altype: number)|
|/**||
|* * *|将字节码进行AES(ECB 模式)加密 @param key 动态白盒秘钥|
|*|@param inData 待加密字节码|
|*|@param altype 加密类型1 aes128 2 aes192 3 aes256|
|*|@return ResultObject 加密后的结果对象|
|**|/|

北京智游网安科技有限公司 

第4 页 

爱加密移动应用密钥白盒SDK 集成手册(HarmonyOS) 

static aes_ecb_encrypt_byte(key: string, inData: ArrayBuffer, altype : number) 

##### **4.3.2 解密(ECB)** 

将Base64 解密回原字符串,定义如下: 

/** * 将字符串(base64 字符串)进行AES(ECB 模式)解密 * * @param key 动态白盒秘钥 * @param inData 待加密字符串 * @param altype 加密类型1 aes128 2 aes192 3 aes256 * @return ResultObject 加密后的结果对象 **/ static aes_ecb_decrypt_string(key: string, inData: string, altype : number ) /** * 将字节码进行AES(ECB 模式)解密 * * @param key 动态白盒秘钥 * @param inData 待加密字节码 * @param altype 加密类型1 aes128 2 aes192 3 aes256 * @return ResultObject 加密后的结果对象 **/ static aes_ecb_decrypt_byte(key: string, inData: ArrayBuffer, altype : number ) 

* @param inData 待加密字符串
* @param altype 加密类型1 aes128 2 aes192 3 aes256
* @return ResultObject 加密后的结果对象
**/
static aes_ecb_decrypt_string(key: string, inData: string, altype : number )
/**
* 将字节码进行AES(ECB 模式)解密
*
* @param key 动态白盒秘钥
* @param inData 待加密字节码
* @param altype 加密类型1 aes128 2 aes192 3 aes256
* @return ResultObject 加密后的结果对象
**/
static aes_ecb_decrypt_byte(key: string, inData: ArrayBuffer, altype : number )

##### **4.3.3 加密(CBC)** 

###### 将字符串进行加密并用Base64 编码,定义如下: 

/** 

- 将字符串进行AES(CBC 模式)加密 

* 

北京智游网安科技有限公司 

第5 页 

爱加密移动应用密钥白盒SDK 集成手册(HarmonyOS) 

- @param key 动态白盒秘钥 

- * @param inData 待加密字符串 

- @param altype 加密类型1 aes128 2 aes192 3 aes256 

- * @param iv 填充模式向量,十六进制字符串,32 位 

- @return ResultObject 加密后的结果对象 

**/ 

static aes_cbc_encrypt_string(key: string, inData: string, altype : number, iv: string) 

/** 

- 将字节码进行AES(CBC 模式)加密 

- 

- @param key 动态白盒秘钥 

- * @param inData 待加密字节码 

- @param altype 加密类型1 aes128 2 aes192 3 aes256 

* @param iv 填充模式向量,十六进制字符串,32 位 * @return ResultObject 加密后的结果对象 

- **/ 

static aes_cbc_encrypt_byte(key: string, inData: ArrayBuffer, altype : number, iv: string) 

##### **4.3.4 解密(CBC)** 

###### 将Base64 解密回原字符串,定义如下: 

/** 

- 将字符串(base64 字符串)进行AES(CBC 模式)解密 

- * @param key 动态白盒秘钥 * @param inData 待加密字符串 * @param altype 加密类型1 aes128 2 aes192 3 aes256 * @param iv 填充模式向量,十六进制字符串,32 位 * @return ResultObject 加密后的结果对象 

北京智游网安科技有限公司 

第6 页 

爱加密移动应用密钥白盒SDK 集成手册(HarmonyOS) 

**/ 

static aes_cbc_decrypt_string(key: string, inData: string, altype : number , iv: string) 

/** 

- 将字节码进行AES 解密 

- @param key 动态白盒秘钥 

- @param inData 待加密字节码 

- @param altype 加密类型1 aes128 2 aes192 3 aes256 

- @param iv 填充模式向量,十六进制字符串,32 位 

- @return ResultObject 加密后的结果对象 

- **/ 

static aes_cbc_decrypt_byte(key: string, inData: ArrayBuffer, altype : number , iv: string) 

##### **4.3.5 加密(GCM)** 

###### 将字符串进行加密并用Base64 编码,定义如下: 

###### /** 

- 将字符串进行AES(GCM 模式)加密 

- 

- @param key 动态白盒秘钥 

- @param inData 待加密字符串 

- @param altype 加密类型1 aes128 2 aes192 3 aes256 

- @param iv 填充模式向量,标准推荐12 个字节,24 位长度的16 进制字符串(不超过 

- 12 个字节) 

- @param add 附加认证数据,长度建议不要超过32 字节 

- @param tagLen 指定tag 数据长度,1-16,推荐16 

- @return String 加密后的ResultObject 字段,通过对象提供的方法获取加密后的tag 

- 以及加密后的密文 

**/ 

static aes_gcm_encrypt_string(key: string, inData: string, altype: number, iv: string, 

北京智游网安科技有限公司 

第7 页 

爱加密移动应用密钥白盒SDK 集成手册(HarmonyOS) 

- add: string, tagLen: number) : ResultObject /** * 将字节码进行AES(GCM 模式)加密 * * @param key 动态白盒秘钥 * @param inData 待加密字节码 * @param altype 加密类型1 aes128 2 aes192 3 aes256 * @param iv 填充模式向量,标准推荐12 个字节,24 位长度的16 进制字符串(不超过 

- 12 个字节) * @param add 附加认证数据,长度建议不要超过32 字节 * @param tagLen 指定tag 数据长度,1-16,推荐16 * @return String 加密后的ResultObject 字段,通过对象提供的方法获取加密后的tag 

- 以及加密后的密文 **/ 

- static aes_gcm_encrypt_byte(key: string, inData: ArrayBuffer, altype: number, iv: string, add: string, tagLen: number): ResultObject 

* @param add 附加认证数据,长度建议不要超过32 字节
* @param tagLen 指定tag 数据长度,1-16,推荐16
* @return String 加密后的ResultObject 字段,通过对象提供的方法获取加密后的tag
以及加密后的密文
**/
static aes_gcm_encrypt_byte(key: string, inData: ArrayBuffer, altype: number, iv:
string, add: string, tagLen: number): ResultObject
4.3.6 解密(GCM)
将Base64 解密回原字符串,定义如下:
/**
* 将字符串(base64 字符串)进行AES(GCM 模式)解密
*
* @param key 动态白盒秘钥
* @param inData 待加密字符串
* @param altype 加密类型1 aes128 2 aes192 3 aes256
* @param iv 填充模式向量,十六进制字符串,24 位(12 个字节)
* @param add 附加数据,长度建议不要超过32 字节

- /** * 将字符串(base64 字符串)进行AES(GCM 模式)解密 * * @param key 动态白盒秘钥 * @param inData 待加密字符串 * @param altype 加密类型1 aes128 2 aes192 3 aes256 * @param iv 填充模式向量,十六进制字符串,24 位(12 个字节) * @param add 附加数据,长度建议不要超过32 字节 * @param tag TAG 数据,从加密接口返回 * @return 解密后的ResultObject 对象,通过对象的方法获取解密后的数据 

北京智游网安科技有限公司 

第8 页 

爱加密移动应用密钥白盒SDK 集成手册(HarmonyOS) 

**/ 

static aes_gcm_decrypt_string(key: string, inData: string, altype: number , iv: string, add: string, tag: string): ResultObject 

/** 

- 将字节码进行AES 解密 

- @param key 动态白盒秘钥 

- @param inData 待加密字节码 

- @param altype 加密类型1 aes128 2 aes192 3 aes256 

- @param iv 填充模式向量,十六进制字符串,24 位(12 个字节) 

- @param add 附加数据,长度建议不要超过32 字节 

- @param tag TAG 数据,从加密接口返回 

- @return 解密后的ResultObject 对象,通过对象的方法获取解密后的数据 

- **/ 

static aes_gcm_decrypt_byte(key: string, inData: ArrayBuffer, altype: number , iv: string, add: string, tag: string): ResultObject 

#### **4.4 SM4 加解密** 

##### **4.4.1 加密(ECB)** 

###### 将字符串进行加密并用Base64 编码,定义如下: 

/** 

- 将字符串进行SM4(ECB 模式)加密 

- * @param key 动态白盒秘钥 * @param inData 待加密字符串 * @padding 保留字段,填0 即可 * @return ResultObject 加密后的结果对象 

北京智游网安科技有限公司 

第9 页 

爱加密移动应用密钥白盒SDK 集成手册(HarmonyOS) 

**/ 

|stat|ic sm4_ecb_encrypt_string(key: string, inData: string, padding: number)|
|---|---|
|/**||
|*|将字节码进行SM4(ECB 模式)加密|
|*||
|*|@param key 动态白盒秘钥|
|*|@param inData 待加密字节码|
|*|@padding 保留字段,填0 即可|
|*|@return ResultObject 加密后的结果对象|
|**|/|
|stat|ic sm4_ecb_encrypt_byte(key: string, inData: ArrayBuffer, padding: number)|

##### **4.4.2 解密(ECB)** 

将Base64 解密回原字符串,定义如下: 

- /** * 将字符串(base64 字符串)进行SM4(ECB 模式)解密 * * @param key 动态白盒秘钥 * @param inData 待加密字符串 * @padding 保留字段,填0 即可 * @return ResultObject 加密后的结果对象 **/ 

- static sm4_ecb_decrypt_string(key: string, inData: string, padding: number ) /** * 将字节码进行SM4(ECB 模式)解密 * * @param key 动态白盒秘钥 * @param inData 待加密字节码 

北京智游网安科技有限公司 

第10 页 

爱加密移动应用密钥白盒SDK 集成手册(HarmonyOS) 

* @padding 保留字段,填0 即可 * @return ResultObject 加密后的结果对象 **/ 

static sm4_ecb_decrypt_byte(key: string, inData: ArrayBuffer, padding: number ) 

##### **4.4.3 加密(CBC)** 

/** 

- 将字符串进行SM4(CBC 模式)加密 

- * @param key 动态白盒秘钥 

- @param inData 待加密字符串 

- @padding 保留字段,填0 即可 

- @param iv 填充模式向量,十六进制字符串,32 位 

- * @return ResultObject 加密后的结果对象 **/ 

static sm4_cbc_encrypt_string(key: string, inData: string, padding: number, iv: string) 

- /** 

- 将字节码进行SM4(CBC 模式)加密 

- * * @param key 动态白盒秘钥 * @param inData 待加密字节码 * @padding 保留字段,填0 即可 * @param iv 填充模式向量,十六进制字符串,32 位 * @return ResultObject 加密后的结果对象 **/ 

- static sem_cbc_encrypt_byte(key: string, inData: ArrayBuffer, padding: number, iv: string) 

北京智游网安科技有限公司 

第11 页 

爱加密移动应用密钥白盒SDK 集成手册(HarmonyOS) 

##### **4.4.4 解密(CBC)** 

/** 

- 将字符串(base64 字符串)进行SM4(CBC 模式)解密 

- @param key 动态白盒秘钥 

- @param inData 待加密字符串 

- @padding 保留字段,填0 即可 

- @param iv 填充模式向量,十六进制字符串,32 位 

- @return ResultObject 加密后的结果对象 

**/ 

static sm4_cbc_decrypt_string(key: string, inData: string, padding: number , iv: string) 

/** 

- 将字节码进行SM4 解密 

- @param key 动态白盒秘钥 

- @param inData 待加密字节码 

- @padding 保留字段,填0 即可 

- @param iv 填充模式向量,十六进制字符串,32 位 

- @return ResultObject 加密后的结果对象 

**/ 

static sm4_cbc_decrypt_byte(key: string, inData: ArrayBuffer, padding: number , iv: string) 

##### **4.4.5 加密(GCM)** 

###### 将字符串进行加密并用Base64 编码,定义如下: 

/** 

- 将字符串进行SM4(GCM 模式)加密 

- 

- @param key 动态白盒秘钥 

- @param inData 待加密字符串 

北京智游网安科技有限公司 

第12 页 

爱加密移动应用密钥白盒SDK 集成手册(HarmonyOS) 

- @param iv 填充模式向量,标准推荐12 个字节,24 位长度的16 进制字符串(不超过 

- 12 个字节) 

- @param add 附加认证数据,长度建议不要超过32 字节 

- @param tagLen 指定tag 数据长度,1-16,推荐16 

- @return String 加密后的ResultObject 字段,通过对象提供的方法获取加密后的tag 

- 以及加密后的密文 

**/ 

static sm4_gcm_encrypt_string(key: string, inData: string, iv: string, add: string, tagLen: number ): ResultObject 

/** 

- 将字节码进行SM4(GCM 模式)加密 

- 

- @param key 动态白盒秘钥 

- @param inData 待加密字节码 

- @param iv 填充模式向量,标准推荐12 个字节,24 位长度的16 进制字符串(不超过 

- 12 个字节) 

- @param add 附加认证数据,长度建议不要超过32 字节 

- @param tagLen 指定tag 数据长度,1-16,推荐16 

- @return String 加密后的ResultObject 字段,通过对象提供的方法获取加密后的tag 

- 以及加密后的密文 

**/ 

static sm4_gcm_encrypt_byte(key: string, inData: ArrayBuffer, iv: string, add: string, tagLen: number): ResultObject 

##### **4.4.6 解密(GCM)** 

###### 将Base64 解密回原字符串,定义如下: 

/** 

- 将字符串(base64 字符串)进行AES(GCM 模式)解密 

- 

- @param key 动态白盒秘钥 

北京智游网安科技有限公司 

第13 页 

爱加密移动应用密钥白盒SDK 集成手册(HarmonyOS) 

- @param inData 待加密字符串 

- @param iv 填充模式向量,十六进制字符串,24 位(12 个字节) 

- @param add 附加数据,长度建议不要超过32 字节 

- @param tag TAG 数据,从加密接口返回 

- @return 解密后的ResultObject 对象,通过对象的方法获取解密后的数据 

**/ 

static sm4_gcm_decrypt_string(key: string, inData: string, iv: string, add: string, tag: string): ResultObject 

/** 

- 将字节码进行AES 解密 

- @param key 动态白盒秘钥 

- @param inData 待加密字节码 

- @param iv 填充模式向量,十六进制字符串,24 位(12 个字节) 

- @param add 附加数据,长度建议不要超过32 字节 

- @param tag TAG 数据,从加密接口返回 

- @return 解密后的ResultObject 对象,通过对象的方法获取解密后的数据 

- **/ 

static sm4_gcm_decrypt_byte(key: string, inData: ArrayBuffer, iv: string, add: string, tag: string): ResultObject 

#### **4.5 JS 调用加解密接口** 

###### 可以通过桥接的方式调用SDK 提供的加解密接口在web 层实现加解密。 

为了方便客户使用,SDK 中导出方法皆为静态方法,静态的方法无法使用桥接方式 注册到js 代码中,因此需要通过对接口进行一次包装,将包装类注册到js 里面实现js 调 用SDK 提供的加解密功能,具体操作步骤: 

- 1 编写包装类,可以参考以下示例: 

WhiteBoxAdapter.ets 

北京智游网安科技有限公司 

第14 页 

爱加密移动应用密钥白盒SDK 集成手册(HarmonyOS) 

2 声明导出接口: 

###### // 先构造包装类 

@State WhiteBoxAdpterObj: WhiteBoxAdpter = new WhiteBoxAdpter(); 

// 构造webview 

Web({ src: '', controller: this.controller }) 

.javaScriptAccess(true) 

.onControllerAttached(() => { 

this.controller.loadUrl($rawfile("Htmldemo.html")); //this.controller.loadUrl($rawfile("index.html")); let whiteBoxFun: 

###### // 导出方法列表 

Array<string>=["Sm4ECBEncrypt","Sm4ECBDecrypt","Sm4CBCEncrypt","Sm4CBCDe crypt","AesECBEncrypt","AesECBDecrypt","AesCBCEncrypt","AesCBCDecrypt"]; 

// 注册js 方法 this.controller.registerJavaScriptProxy(this.WhiteBoxAdpterObj, "objTestName", whiteBoxFun); 

}) 

3 调用导出接口进行加解密: 

// js 端调用AES ECB 加密 

objTestName.AesECBEncrypt(strkey, data) 

#### **4.6 具体样例使用解析** 

##### **4.6.1 字符串加解密示例** 

###### **4.6.1.1 AES** 

var iv = '000102030405060708090a0b0c0d0eef'; 

var data = '这是一个真实的测试例子,hello world' 

sk = 

'b5421fcedc35b0edbe556036e6e54bd7b1b6468dfe393773dbfc4d9186ff3665a69ec2 4019d17541ebad976be1cf440e207bd1de7753024aec1af17f2610b482c8367eda5405 

北京智游网安科技有限公司 

第15 页 

爱加密移动应用密钥白盒SDK 集成手册(HarmonyOS) e5d25d04f5e3aca69821c0325786678b49406b06d0e46b022648bc4baba17d527cf4b 2036a727c2c2f283171ee1382216cf7d6dc3c7d4199aae9fdf0eb522ff29d3a5f6d16b3d 33e5dc721534b7e492ef58c072ac36785af7db1964fd0172281fc5141479a714b9394b 4c0a93faf'; 

// aes ecb 

```arkts
let retEnc = IjmWhiteBoxAES.aes_ecb_encrypt_string(Test.strKeyAes, data, 1); hilog.info(0x0000, 'test_data', 'aes ecb ret = %{public}d len = %{public}d encrypt = %{public}s', retEnc.getResult(), retEnc.getDataLen(), retEnc.getDataBase64()); 
```

let retDec = IjmWhiteBoxAES.aes_ecb_decrypt_string(Test.strKeyAes, retEnc.getDataBase64(), 1); 

retEnc.getDataBase64(), 1);
hilog.info(0x0000, 'test_data', 'aes ecb ret = %{public}d len = %{public}d encrypt
= %{public}s', retDec.getResult(), retDec.getDataLen(), retDec.getData());
// aes cbc
let retEnc = IjmWhiteBoxAES.aes_cbc_encrypt_string(Test.strKeyAes, data, 1,
Test.strIV);
hilog.info(0x0000, 'test_data', 'aes ecb ret = %{public}d len = %{public}d encrypt
= %{public}s', retEnc.getResult(), retEnc.getDataLen(), retEnc.getDataBase64());
let retDec =
IjmWhiteBoxAES.aes_cbc_decrypt_string(Test.strKeyAes,retEnc.getDataBase64() ,1,Tes
t.strIV);
hilog.info(0x0000, 'test_data', 'aes ecb ret = %{public}d len = %{public}d encrypt
= %{public}s',retDec.getResult(),retDec.getDataLen(), retDec.getData() );

###### **4.6.1.2 SM4** 

var iv = '000102030405060708090a0b0c0d0eef'; 

var sk = 

"92c777ab937339be92bf6266a23620f2e23bb2e6fa31e807977c7eee18c0d1175c530 535a9457c7cc94a1f97bb5914af838c4140dca301247c02b2d2a61f18eddbb3df61a395 f070b662e88a8155e02928d2cd60cbf93db016bca20b4012c5a1aa4047704707de12b 0fd1334a2b48812239dc7b2fc6cc4429d790054af79c009ec79be1a"; 

北京智游网安科技有限公司 

第16 页 

爱加密移动应用密钥白盒SDK 集成手册(HarmonyOS) 

var data = '这是一个真实的测试例子,hello world' 

// sm4 ecb 

let retEnc : ResultObject = 

IjmWhiteBoxSM4.sm4_ecb_encrypt_string(Test.strKeysm4,data,0); 

hilog.info(0x0000, 'test_data', 'sm4 ecb ret = %{public}d len = %{public}d encrypt = %{public}s',retEnc.getResult(),retEnc.getDataLen(), retEnc.getDataBase64() ); 

let retDec = 

IjmWhiteBoxSM4.sm4_ecb_decrypt_string(Test.strKeysm4,retEnc.getDataBase64() ,0); hilog.info(0x0000, 'test_data', 'sm4 ecb ret = %{public}d len = %{public}d encrypt = %{public}s',retDec.getResult(),retDec.getDataLen(), retDec.getData() ); 

// sm4 cbc
let retEnc =
IjmWhiteBoxSM4.sm4_cbc_encrypt_string(Test.strKeysm4,data,0,Test.strIV);
hilog.info(0x0000, 'test_data', 'sm4 ecb ret = %{public}d len = %{public}d encrypt
= %{public}s',retEnc.getResult(),retEnc.getDataLen(), retEnc.getDataBase64() );
let retDec =
IjmWhiteBoxSM4.sm4_cbc_decrypt_string(Test.strKeysm4,retEnc.getDataBase64() ,0,T
est.strIV);
hilog.info(0x0000, 'test_data', 'sm4 ecb ret = %{public}d len = %{public}d encrypt
= %{public}s',retDec.getResult(),retDec.getDataLen(), retDec.getData() );

北京智游网安科技有限公司 

第17 页 

爱加密移动应用密钥白盒SDK 集成手册(HarmonyOS) 

### **5 公司介绍** 

北京智游网安科技有限公司(爱加密)成立于2013 年,总部位于北京,研发及运营 中心位于深圳,同时在全国各地设立了12 个分支机构,拥有员工400 多人。 

爱加密(www.ijiami.cn)是专业的移动信息安全服务提供商,专注于移动应用安全、 大数据、物联网及工业互联网安全,坚持以用户需求为导向、持续不断的创新,致力于为 客户提供全方位、一站式的移动安全全生命周期解决方案。爱加密的服务宗旨是通过革新 性安全方案和7x24 小时全天候的专业服务,打造和谐、强大、高度安全的万物互联生态 环境。 

爱加密拥有安全防护、安全检测、安全管理、业务运营、威胁感知、安全监管、安全 服务七大产品体系,贯穿了应用设计评估、安全开发测试、应用优化、应用安全发布及应 用上线运营阶段的整个生命周期。目前行业用户遍及金融、运营商、政府、电商、能源、 教育、游戏等多个行业。至今共服务企业及开发者用户50 万+,保护移动应用100 万+, 监测互联网应用1500 万+,累计覆盖10 亿移动终端。 

北京智游网安科技有限公司 

第18 页
