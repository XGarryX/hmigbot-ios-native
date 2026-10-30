# **-** **卓信ID开发者手册 鸿蒙** 

**版本:V2.1.1** 

#### **更新时间:2024年09月12日** 

**中国信息通信研究院联合中国互联网协会共建 统一移动基础服务平台** 

**1. 鸿蒙 ZXSDK 集成文档** 准备工作 1.1 概述 1.2 APP 方集成指南 1.2.1 获取har 包 1.2.2 配置依赖 1.2.3 配置 appId/channelId 1.2.4 配置 ZXSDK 1.2.5 初始化 SDK 1.2.6 获取 ZXID 1.2.7 获取 SAID 1.2.8 获取 ZXSDK 版本 1.3 服务商集成使用 

1.3.1 申请 channelId 和 appId 1.3.2 配置 channelId 和 appId 1.3.3 初始化 SDK 1.3.4 获取 ZXID 

**2. 安全与合规指南** 2.1 隐私协议 

# **1.** **鸿蒙 ZXSDK 集成文档** 

## **准备工作** 

1. 申请主体应下载《附件一、“卓信ID”保密承诺书》,并加盖公章。 

2. 如果申请主体申请成为开发者,需要在APP中集成卓信SDK,则填写《附件二、“卓信ID”开发者申请表》。 

3. 如果申请主体申请成为服务商,计划调用卓信服务端接口,则填写《附件三、“卓信ID”服务商申请表》。 

4. 如果申请主体申请成为开发者+服务商,则填写附件二及附件三。 

5. 通过卓信ID服务申请后,可获取相应接口文档、SDK资料包、以及用于标识申请方的 PartnerId ,标识应用 (APP / SDK)的 APPID 及标识身份签名的 AccessKeyId / AccessKeySecret 。 

- 注*  附件下载及具体的申请流程可参考卓信ID官网:https://zxid.mobileservice.cn 

## **1.1 概述** 

- 本文档介绍 DevEco Studio NEXT  Beta1,鸿蒙API HarmonyOS NEXT  Beta1,ZXSDK的集成方式。早期需 要联系华为技术人员获取,在其指导下搭建好开发环境 

- 本文档适用 ZXSDK 版本:2.1.0.0 及以后 

#### 本文默认开发者已经具有基础的鸿蒙知识,项目工程结构如下: 

ZXSDKDemo/ 

|- entry/ (项目主模块) | |- libs/ (第三方库,用户手动创建) | |- src/ (代码目录) | |- oh-package.json5(模块级oh-package.json5文件) | |- build-profile.json5 |- hvigorfile.ts |- oh-package.json5 (顶层oh-package.json5文件) | ...... #### 集成并使用卓信sdk需要配置以下权限 1. ohos.permission.GET_NETWORK_INFO 2. ohos.permission.INTERNET 3. ohos.permission.STORE_PERSISTENT_DATA 4. ohos.permission.APPROXIMATELY_LOCATION 5. ohos.permission.APP_TRACKING_CONSENT ## **1.2 APP 方集成指南** #### 本地集成。 ohpm三方库集成: ohpm install @zx/zxsdk ### **1.2.1 获取har 包** 1. 通过官网下载或联系技术支持获取 zxsdk.har 2. 在项目主模块 entry 下创建 libs 文件夹 3. 将下载好的 zxsdk.har 放到 libs 文件夹下 ZXSDKDemo/ - |- entry/ (项目主模块) - | |- libs/ (第三方库,用户手动创建) | |-zxsdk.har (ZXSDK) | ...... ### **1.2.2 配置依赖** 1. 配置工程级目录中的 build-profile.json5 文件,将 useNormalizedOHMUrl 设置为 true ##### ZXSDKDemo/ |- entry/ (项目主模块) - |- build-profile.json5 build-profile.json5 配置如下: { "app": { "products": [ { "buildOption": { "strictMode": { "useNormalizedOHMUrl": true } } } ] } } 2. 找到 entry 模块级 oh-package.json5 文件,添加依赖 zxsdk.har ZXSDKDemo/ |- entry/ (项目主模块) | |- libs/ (第三方库,用户手动创建) | |-zxsdk.har (ZXSDK) | |- src/ (代码目录) | |- oh-package.json5(模块级oh-package文件) oh-package.json5 配置如下: { "license": "", "devDependencies": {}, "author": "", "name": "entry", "description": "Please describe the basic information.", "main": "", "version": "1.0.0", "dependencies": { // 依赖zxsdk.har "@zx/zxsdk": "file:./libs/zxsdk.har" } } 3. 在控制台进入 entry 目录,执行 ohpm install ,在 entry 目录下出现 oh_modules 文件夹,代表依赖成功 ### **1.2.3 配置 appId/channelId** 在使用zxsdk之前,需在 “entry/src/main/resources/rawfile/zxConfig.json” 路径下先配置appId/channelId ZXSDKDemo/ |- entry/ (项目主模块) | |- src/ (代码目录) | | |- main | | | |- resources | | | | |- rawfile | | | | | |- zxConfig.json 在上述路径下的rawfile中新建zxConfig.json文件,做如下配置: { "appId": "#appId#", "channelId": "#channelId#" } - 官网客户:需在zxConfig.json文件中配置appId SDK 服务商推广的 APP 客户:需在zxConfig.json文件中配置channelId ### **1.2.4 配置 ZXSDK**

在初始化 ZXSDK 之前,用户可按需配置 ZXSDK 。 

// 引入 ZXSDK 以及配置相关类 import { ZXSDKConfigOption, ZXSDK } from '@zx/zxsdk' 

// 获取默认配置 const config = ZXSDKConfigOption.defaultConfig() 

// 按照需要修改配置 config.privacy = 0 ······ 

// 设置zxsdk配置 ZXSDK.setConfigOption(config) 

#### 其中,可配置项如下: 

- privacy:AID 隐私模式。如已开通 AID 能力, 默认是不加密返回( privacy = 0 )。如需设置加密 **(防 止其他方获取到自己的 aids )** ,可将 privacy 设置为 1 。 

### **1.2.5 初始化 SDK** 

- 调用 ZXSDK.startSDK(context) 进行 SDK 的初始化,推荐在EntryAbility.ets的onCreate方法中初始化 

// entry/src/main/ets/entryability/EntryAbility.ets 

// 引入ZXSDK import { ZXSDK } from '@zx/zxsdk'; import { BusinessError } from '@kit.BasicServicesKit'; ... 

```arkts
onCreate(want: Want, launchParam: AbilityConstant.LaunchParam): void { hilog.info(0x0000, 'testTag', '%{public}s', 'Ability onCreate'); // app方初始化 ZXSDK.startSDK(this.context) .then(() => { console.log('app: init success') }) .catch( (e: BusinessError) => { console.log('app: sdk start fail', e.name, e.code, e.message) }) } ... 
```

### **1.2.6 获取 ZXID** 

开发者可通过调用 getZXID 方法来获取 ZXID ,参考以下代码: 

```arkts
import { ZXSDK, ZXIDResult } from '@zx/zxsdk'; /** export interface ZXIDResult { zxid: string expireTime: string openid: string tags: Object aaid: string, vaid: string } */ try { const zxResult: ZXIDResult = await ZXSDK.getZXID() console.log('zxResult', JSON.stringify(zxResult)); } catch (err) { console.log(`ZXSDKError: code: ${err.code} message: ${err.message}`); } 
```

### **1.2.7 获取 SAID** 

SDK 提供直接获取SAID的能力。参考以下代码: 

```arkts
import { ZXSDK } from '@zx/zxsdk'; try { // const res = await ZXSDK.startSDK('', '') const partnerId = '' const accessKeyId = '' const said = await ZXSDK.getSAID({ AccessKeyId: accessKeyId, 
```

PartnerId: partnerId, SignatureMethod: "HMAC-SHA256", SignatureNonce: "", Timestamp: 0, Signature: "" }) this.message = JSON.stringify(said) console.log(`said result: ${JSON.stringify(said)}`); } catch (e) { console.info(`error: ${e.code} - ${e.message}`) this.message = `error: ${e.code} - ${e.message}` } 

#### 请求参数解释如下( **参数推荐由服务端获取** ) 

|**参数**|**解释**|
|---|---|
|**AccessKeyId**|通过服务申请后分配的密钥标识|
|**PartnerId**|通过服务申请后给到的id|
|**SignatureMethod**|信息签名方法,目前固定为HMAC-SHA256|
|**SignatureNonce**|64字节以内的随机串,用于防止重放攻击,每次请求必须提供不同的值|
|**Timestamp**|UTC时间戳,从UTC1970年1月1日0时0分0秒起至现在的总秒数。如 1632634877|
|**Signature**|信息签名字符串|

#### **签名方式:** 

1. 使用请求参数构造标准请求字符串(Standard Query String),包括文档中的“公共请求参数”,但不包 括“公共请求参数”中的 Signature 参数。将标准请求字符串进行排序,此排序是大小写敏感的,请使用标 准文档中的大小写格式。 

具体排序示例: AccessKeyId, PartnerId, SignatureMethod, SignatureNonce, Timestamp 。 

将参数值使用英文等号 & 进行连接,即得到标准请求字符串。 

示例: accesskeyid&partnerid&HMAC-SHA256&67a4ac92-c53e-440d-b7772b14f7a61a5c&1632634877 

2. 按照 RFC2104 对上面的 StringToSign 字符串计算签名 HMAC 值。计算签名时使用的 Key 就是用户持有 的 AccessKeySecret ,使用的哈希算法为 SHA256 。 

3. 按照标准 Base64 编码规则,把上面的 HMAC 值编码为字符串,得到签名值(Signature)。 

4. 将得到的签名值作为 Signature 请求头的值,即完成请求签名的过程。 

### **1.2.8 获取 ZXSDK 版本** 

如需获取 ZXSDK 版本, 可调用 version 方法。参考以下代码: 

import { ZXSDK } from '@zx/zxsdk'; 

console.log(ZXSDK.version()); 

## **1.3 服务商集成使用** 

前言:  需要到官网提交资料, 申请 channelId 和 appId , 一般是服务商⻆色。 

### **1.3.1 申请 channelId 和 appId** 

联系官方技术支持, 申请唯一的渠道号ID  (即 channelId )  和 appId 。 

**注: SDK 服务商推广的 APP 客户配置 channelId 后, 不用单独申请 appId 就可以使用卓信能力。** 

### **1.3.2 配置 channelId 和 appId** 

在使用zxsdk之前,需提示app开发者在 “entry/src/main/resources/rawfile/zxConfig.json” 路径下先配置 channelId 

ZXSDKDemo/ |- entry/ (项目主模块) | |- src/ (代码目录) | | |- main | | | |- resources | | | | |- rawfile | | | | | |- zxConfig.json 

在上述路径下的rawfile中新建zxConfig.json文件,做如下配置: 

{ "channelId": "#channelId#" } 

SDK 服务商:需在自己模块的module.json5配置metadata, key为ZX_APPID_${服务商唯一标识} **eg.ZX_APPID_AWS** , value为服务商appId, 示例如下: 

{ "metadata": [ { "name": "ZX_APPID_${服务商唯一标识}", "value": "#服务商appId#" } ] } 

### **1.3.3 初始化 SDK** 

服务商需要自己初始化 ZXSDKInstance 的对象, 并维护其生命周期。 

- 调用 ZXSDK.initWith(context, appId) 获取 ZXSDKInstance 实例,推荐在EntryAbility.ets的onCreate方 法中初始化 

// entry/src/main/ets/entryability/EntryAbility.ets // 引入ZXSDK import { ZXSDK, ZXSDKInstance } from '@zx/zxsdk'; import { BusinessError } from '@kit.BasicServicesKit'; ... onCreate(want: Want, launchParam: AbilityConstant.LaunchParam): void { hilog.info(0x0000, 'testTag', '%{public}s', 'Ability onCreate'); // 服务商初始化 ZXSDK.initWith(this.context, '#服务商appId#') .then((zxInstance: ZXSDKInstance) => { // 服务商需自己维护该实例 // 存储、赋值.... }) .catch( (e: BusinessError) => { console.log('sdk: sdk start fail', e.name, e.code, e.message) }) } ... 

### **1.3.4 获取 ZXID** 

服务商可通过调用 getZXID 方法来获取 ZXID ,参考以下代码: 

import { ZXSDK, ZXIDResult } from '@zx/zxsdk'; /** export interface ZXIDResult { zxid: string expireTime: string openid: string tags: Object 

aaid: string, vaid: string } */ try { const zxResult: ZXIDResult = await zxInstance.getZXID()// zxInstance为1.3.3中服务商自 己维护的ZXSDK实例 

console.log('zxResult', JSON.stringify(zxResult)); } catch (err) { console.log(`ZXSDKError: code: ${err.code} message: ${err.message}`); } 

# **2.** **安全与合规指南** 

卓信ID的技术流程设计充分考虑了数据安全和合规方面的要求,不过仅仅靠卓信SDK和卓信服务的合规还不足以覆 盖所有的合规流程,还需要CP方也协助完成一定的工作,这些工作是简单便捷的,但也是完整应用合规方案所不能 或缺的重要组成部分。 

## **2.1 隐私协议** 

1. 卓信SDK具备完整的隐私协议声明,具体可参见: 卓信ID隐私政策。开发者在 APP 隐私政策的 “与授权合作伙 伴共享”条款中,添加卓信ID的用户隐私声明内容及隐私协议链接。 

2. 开发者需要向用户逐一明示APP中所嵌入的各SDK(包括卓信SDK)收集使用个人信息的目的、方式和范围, 可以采用类似如下表格形式: 

|**SDK名称**|**合作伙伴名称**|**合作目的**|**收集个人信息字段**|**申请的权限**|**SDK隐私政策**|
|---|---|---|---|---|---|
||中互智安||**设备信息** 包括:设备制造商、设备 型号、设备系统信息|**网络权限**:用于与卓信服||
|卓信 SDK|(北京)科 技有限公司 (中国互联 网协会全资 子公司)|为APP 提供反 欺诈匿 名可变 ID|**设备网络信息** 包括:设备联网方式和状 态信息 **设备环境信息** 包括:设备的屏幕亮度、 设备的电池状态及设备所 在地区(如中国与美国)|务器通讯,上传设备弱特 征指纹信息,获取匿名可 变的卓信ID **持久化存储权限**:用于持 久化存储卓信ID弱特征 指纹信息|卓信 ID隐 私政 策|
