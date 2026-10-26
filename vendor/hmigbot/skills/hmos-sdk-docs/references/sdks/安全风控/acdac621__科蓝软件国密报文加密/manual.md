CSIITM 标准文档 

文档编号:CSII-PS-PEC-2016003 

# 报文加密 SMEncryption ( **Harmony** 版) 用户手册 

###### 北京科蓝软件系统股份有限公司 

2024 年 2 月 2 日 

###### 文档修改记录 

|版本|内容|编写|审核|
|---|---|---|---|
|1.0|新建|彭佳星|赵阳|
|1.0|新增验证License|彭佳星|赵阳|

###### 版权申明: 

本文档的版权属于北京科蓝软件系统股份有限公司,任何人或组织未经许可, 

不得擅自修改、拷贝或以其它方式使用本文档中的内容。 

##### 目   录 

|一、 引言........................................................................................................................1|
|---|
|1.1编写目的...........................................................................................................1|
|1.2背景知识及参考资料.......................................................................................1|
|二、 控件概述................................................................................................................2|
|2.1控件组成...........................................................................................................2|
|2.2功能特点...........................................................................................................2|
|2.3技术特点...........................................................................................................3|
|2.4控件接口描述...................................................................................................3|
|2.4.1编辑控件................................................................................................3|
|三、DevEcoStudio相关设置说明................................................................................4|
|3.1 Har文件导入.....................................................................................................4|
|3.1.1 Har文件导入..........................................................................................4|
|4.1代码示例...........................................................................................................5|

用户手册 

SMEncryption 报文加密 

## 一、引言 

##### **1.1** 编写目的 

“SMEncryption 报文加密”是保护用户敏感信息输入的重要手段,能对客户端操作 系统进行安全增强,可大幅提升“木马”程序非法获取用户敏感输入信息“成本”的软件 集合。 

“SMEncryption 报文加密”的 Harmony 版本由加密模块组成。本《用户手册》中将以 一个典型的开发部署为例,为读者叙述一个典型开发的全过程,使读者能独立应用 SMEncryption 报文加密。 

##### **1.2** 背景知识及参考资料 

假定读者对下列技术有一定的理解: 

|技术|有关内容|
|---|---|
|Harmony SDK|Harmony SDK的基本常识|
|Harmony|Harmony的Ability基本知识|
|Ability||
|通信|Ability的通信方法(非必须)|
|NAPI|NAPI相关知识(非必须)|

文件编号:CSII-PS-PEC-2016003 

第 1 页 

用户手册 

SMEncryption 报文加密 

## 二、控件概述 

##### **2.1** 控件组成 

SMEncryption 报文加密 Harmony 版本两部分构成: 

加密核心实现模块——由 C++实现的 so 动态库。 

加密模块——提供 SMEncryption 报文加密的 HAR 包,供 Harmony SDK 调用通过 

NAPI 方式调用加密核心实现模块动态库。 

##### **2.2** 功能特点 

- 防止 Hook 类木马程序攻击。 

- 防止网络传输泄密 

- 防破解保护 

##### **2.3** 技术特点 

- 敏感信息通过加密后有效防止敏感信息泄露。 

##### **2.4** 控件接口描述 

###### **2.4.1** 编辑控件 

###### 函数说明: 

|函数|说明|备注|
|---|---|---|
|setCipheVersion(version : number)|选择加密类型版本|1 //对明文进行SM3计算 2 // SM4的密钥和明文进 行SM3计算 3 // HMAC密钥和明文进 行SM3计算 4 // HMAC密钥和明文进 行标准的HMAC计算 5 // HMAC密钥和明文进 行标准的HMAC计算, SM4密钥和HMAC密钥 分别用SM2密钥进行加 密/|

文件编号:CSII-PS-PEC-2016003 

第 2 页 

用户手册 

SMEncryption 报文加密 

|/密文是用|分割的4段 base64密文|
|---|
|6 //总共三个随机对称秘 钥,分别是随机秘钥E,报 文加密随机秘钥, sm3hmac随机秘钥 // 1、在原来的基础上,在产 生一个随机的对称秘钥E // 2、使用SM2公钥对随机 对称秘钥E进行加密,得 到密文1 // 3、使用随机秘钥E对报 文加密随机秘钥加密,得 到密文2 // 4、使用随机秘钥E 对 sm3hmac随机秘钥加密, 得到密文3 // 5、使用报文加密随机秘 钥对报文加密,得到密文 4 // 6、使用sm3hmac随机秘 钥对报文计算hmac,得到 密文5 // 7、把这五个密文使用竖 线分割进行返回|
|7 // SM2(SM4key) + "|" +SM2(SM3Hmackey)  +|
|"|" + SM4(SM4key,报文) + "|" + SM3Hmac|

文件编号:CSII-PS-PEC-2016003 

第 3 页 

用户手册 

SMEncryption 报文加密 

|||(SM3Hmackey,pkcs5(报 文)) 8 //对明文进行SM3 计 算,解密不校验SM3|
|---|---|---|
|telecomSMEncrypt(encipher : string , key : string)|
用于加密报文。
参数1:需要加密的明文
数据
参数2:公钥|-1     //加密原文为空
-2     //密文指针为空
-3     //加密原文长度错误
-4     //解密时密文长度错误
-5     // SM2公钥为空
-6     // SM2私钥为空
-7     //加密上下文错误
-8     // SM2参数group错误
-9     // SM2加密错误
-10    // SM2解密错误
-11    // SM4密钥错误
-12    // SM4初始化失败
-13    // SM4的UPDATE错误
-14    // SM4的FINAL错误
-15    // SM3缓冲区错误|
|telecomSMDecrypt(decrypt : string)|
用于解密
参数1:需要解密的数据|-1     //加密原文为空
-2     //密文指针为空
-3     //加密原文长度错误
-4     //解密时密文长度错误
-5     // SM2公钥为空
-6     // SM2私钥为空
-7     //加密上下文错误
-8     // SM2参数group错误
-9     // SM2加密错误
-10    // SM2解密错误|

文件编号:CSII-PS-PEC-2016003 

第 4 页 

用户手册 

SMEncryption 报文加密 

|||-11    // SM4密钥错误 -12    // SM4初始化失败 -13    // SM4的UPDATE错误 -14    // SM4的FINAL错误 -15    // SM3缓冲区错误|
|---|---|---|
|setTelecomSMKeyFormat (randomKey : boolean)|True:一次一密密钥是随 机的针对非异步调用。 False:密钥初始化后不会 改变,针对异步调用||
|License解析xml错误码:||错误码: -901 : component为空 -902 : bankName为空 -903 : xml 文件中的 packageName为空 -904 : expiration为空 -905 : signValue为空 -906 : bundleName获取为 空 -907 : packageName 与 bundleName不一致 -908 :没有发现许可文件 -909 :无效的许可文件 -910 :许可文件过期|

文件编号:CSII-PS-PEC-2016003 

第 5 页 

用户手册 

SMEncryption 报文加密 

## 三、 **DevEcoStudio** 相关设置说明 

##### **3.1HAR** 文件导入 

首先在 entry 目录下创建 libs-har 目录,将 SDK 放入这个目录, 然后在 entry 目录下有个 oh-package.json5 文件,打开这个文件, 找到 dependencies 属性添加” cryptionlibrary“ : ” file:../entry/libs- 

#### har/ cryptionlibrary.har“ 

文件编号:CSII-PS-PEC-2016003 

第 6 页 

用户手册 

SMEncryption 报文加密 

##### **3.2** 将 **License** 文件导入 

##### 注意:文件名不可修改 

##### **3.3** 解析 **License** 文件 

文件编号:CSII-PS-PEC-2016003 

第 7 页 

用户手册 

SMEncryption 报文加密 

##### 在 **EntryAbility.ets** 中 的 **onCreate** 函 数 中 调 用 **PEJniLibbckSM.getInstance().handleAbilityCryptoAction(t** 

**his.context)** 方法 

文件编号:CSII-PS-PEC-2016003 

第 8 页 

用户手册 

SMEncryption 报文加密 

## **4.1** 、代码示例 

### EntryAbility.ets 中代码: 

```arkts
import { AbilityConstant, UIAbility, Want } from '@kit.AbilityKit'; import { hilog } from '@kit.PerformanceAnalysisKit'; import { window } from '@kit.ArkUI'; import { PEJniLibbckSM } from 'cryptionlibrary'; 
export default class EntryAbility extends UIAbility { onCreate(want: Want, launchParam: AbilityConstant.LaunchParam): void { hilog.info(0x0000, 'testTag', '%{public}s', 'Ability onCreate'); PEJniLibbckSM.getInstance().handleAbilityCryptoAction(this.context) } onDestroy(): void { hilog.info(0x0000, 'testTag', '%{public}s', 'Ability onDestroy'); } 
onWindowStageCreate(windowStage: window.WindowStage): void { // Main window is created, set main page for this ability hilog.info(0x0000, 'testTag', '%{public}s', 'Ability onWindowStageCreate'); 
```

windowStage.loadContent('pages/Index', (err, data) => { if (err.code) { 

hilog.error(0x0000, 'testTag', 'Failed to load the content. Cause: %{public}s', JSON.stringify(err) ?? ''); 

return; } hilog.info(0x0000, 'testTag', 'Succeeded in loading the content. Data: %{public}s', JSON.stringify(data) ?? ''); 

}); } onWindowStageDestroy(): void { // Main window is destroyed, release UI related resources hilog.info(0x0000, 'testTag', '%{public}s', 'Ability onWindowStageDestroy'); } 

onForeground(): void { 

文件编号:CSII-PS-PEC-2016003 

第 9 页 

用户手册 

SMEncryption 报文加密 

// Ability has brought to foreground hilog.info(0x0000, 'testTag', '%{public}s', 'Ability onForeground'); } 

```arkts
onBackground(): void { // Ability has back to background hilog.info(0x0000, 'testTag', '%{public}s', 'Ability onBackground'); } } 
```

## Index.ets 中代码 

import { PEJniLibbckSM } from 'cryptionlibrary'; 

//测试公钥 

let key = 

"CCCA565FB60E106C098361958627DBB47C4118E8517F6202BD2672147CB61687FD 

9B132F6D939E4ECCAD37C8D099C8398C997387B8FEE9C982304546A2317598"; 

@Entry @Component 

export struct Index { 

@State message: string = 'Hello World'; 

@State mi: string = 'Hello World'; 

aboutToAppear(): void { 

PEJniLibbckSM.getInstance().setTelecomSMKeyFormat(false); 

PEJniLibbckSM.getInstance().setCipherVersion(4); 

} 

build() { 

文件编号:CSII-PS-PEC-2016003 

第 10 页 

用户手册 

SMEncryption 报文加密 

Row() { 

Column() { 

Text(this.message) 

.fontSize(20) 

.fontWeight(FontWeight.Bold) 

Button("加密").onClick(async (event: ClickEvent) => { 

let encrypt = 

PEJniLibbckSM.getInstance().telecomSMEncrypt("2123123123", key); 

this.message = encrypt; }) 

Button("解密").onClick((event: ClickEvent) => { 

let encryptBody = this.message.split("|"); 

PEJniLibbckSM.getInstance().telecomSMDecrypt(encryptBody[1]+"|"+encryptBody[2 

]); }) } .width('100%') .height('100%') 

.justifyContent(FlexAlign.SpaceBetween) 

} .height('100%') 

} 

文件编号:CSII-PS-PEC-2016003 

第 11 页 

用户手册 

SMEncryption 报文加密 

} 

###### 错误码: 

#define ERR_PLAIN_TEXT_NULL       -1  // 加密原文为空 #define ERR_CIPHER_TEXT_NULL      -2  // 密文指针为空 #define ERR_PLAIN_TEXT_LEN        -3  // 加密原文长度错误 #define ERR_CIPHER_TEXT_LEN       -4  // 密文长度错误 #define ERR_SM2_PUBLIC_KEY_NULL   -5  // SM2 公钥为空 #define ERR_SM2_PRIVATE_KEY_NULL  -6  // SM2 私钥为空 #define ERR_SM2ED_CTXT_NULL       -7  // SM2 上下文错误 #define ERR_SM2_GROUP_NULL        -8  // SM2 参数 group 错误 #define ERR_SM2_ENCRYPT           -9  // SM2 加密错误 #define ERR_SM2_DECRYPT           -10 // SM2 解密错误 #define ERR_SM4_KEY               -11 // SM4 密钥错误 #define ERR_SM4_INIT               -12 // SM4 初始化错误 

#define ERR_SM4_UPDATE           -13 // SM4 的 UPDATE 错误 #define ERR_SM4_FINAL             -14 // SM4 的 FINAL 错误 #define ERR_SM3_MD_BUFF          -15 // SM3 缓冲区错误 #define ERR_MALLOC_FAIL          -16 // 申请内存失败 #define ERR_BASE64                 -17 // BASE64 编解码错误 #define ERR_CIPHER_FORMAT        -18 // 密文格式错误 #define ERR_HMAC                  -19 // HMAC 失败 

-901 : component 为空 

文件编号:CSII-PS-PEC-2016003 

第 12 页 

用户手册 

SMEncryption 报文加密 

||-902 : bankName为空|
|---|---|
|空|-903 : xml文件中的packageName为|
||-904 : expiration为空|
||-905 : signValue为空|
||-906 : bundleName获取为空|
|不|-907 : packageName 与bundleName 一致|
||-908 :没有发现许可文件|
||-909 :无效的许可文件|
||-910 :许可文件过期|

文件编号:CSII-PS-PEC-2016003 

第 13 页
