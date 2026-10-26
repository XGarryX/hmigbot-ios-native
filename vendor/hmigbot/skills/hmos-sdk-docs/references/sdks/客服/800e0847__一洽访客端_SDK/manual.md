# **接入一洽SDK** 

集成基础功能 

### **开发环境** 

- DevEco Studio 版本号:5.0.3.900 

- 系统API版本: 5.0.0(12) 

### **初始化SDK** 

#### **申请AppId AppSecret** 

?> 开启推送,指一洽将未读消息,通过上图配置的地址,下发到开发者服务器,开发者在App集成的远程推送 SDK,由开发者将未读消息信息推送至用户手机。 

!> 推送配置选择Android。 

#### **在项目中安装依赖** 

##### 执行ohpm安装命令 

ohpm i @echat/echat_sdk 

或 打开工程目录或模块目录下的 oh-package.json5 中的 dependencies 添加 "@echat/echat_sdk": "^{{sdkVersion}}" 

##### 例如: 

{ "dependencies": { "@echat/echat_sdk": "^1.0.0" } } 

#### **配置APP权限** 

需要在entry类型的模块目录中,找到 src/main/module.json5 , 加入下面命令 

{ "module": { "name": "entry", "type": "entry", //...省略其他配置 "requestPermissions": [ { "name": "ohos.permission.INTERNET" }, { "name": "ohos.permission.GET_NETWORK_INFO" }, { "name": "ohos.permission.VIBRATE" }, { "name": "ohos.permission.MICROPHONE", "reason": "$string:echat_permission_record_audio_description", "usedScene": { "abilities": [ "EntryAbility" ], "when": "inuse", } }, ], //...省略其他配置 

} } 

开发者,可以对以上权限补充完善使用原因。 

#### **SDK配置和初始化** 

在App主要的 Ability , onCreate 生命周期回调中执行以下代码初始化配置 SDK EChatSDK.setConfig(this.context, config); 。后续根据实际情况,调用 EChatSDK.init(); 进行 SDK初始化。 

!> 注意: 

1. 必须先配置SDK参数,再初始化SDK。 

2. 使用SDK的功能/API,必须完成SDK初始化。 

##### **SDK配置接口** 

##### 当前接口仅配置SDK参数,不会启动SDK。 

- !> 请务必在App首个启动的 Ability , onCreate 生命周期回调中调用配置SDK参数。 

```arkts
let config = new SDKConfig(); config.appId = '.....'; config.appSecret = '.....'; config.serverToken = '.....'; config.serverAppId = '.....'; config.serverEncodingKey = '.....'; config.companyId = 1; EChatSDK.setConfig(this.context, config); 
```

##### **SDKConfig参数:** 

|**参数**|**类型**|**描述**|**必须**|
|---|---|---|---|
|appId|String|SDK参数,详情咨询技术支持。|是|
|appsecret|String|SDK参数,详情咨询技术支持。|是|
|serverToken|String|SDK参数,详情咨询技术支持。|是|
|serverAppId|String|SDK参数,详情咨询技术支持。|是|
|serverEncodingKey|String|SDK参数,详情咨询技术支持。|是|
|companyId|number|SDK参数,详情咨询技术支持。|是|
|hostUrl|String|非必填,不填为,默认为国内环境 服务器地址格式:**https://xx.echatsoft.com** 例如: -国内环境 **https://e.echatsoft.com** -雅加达环境 **https://id.echatsoft.com** -德国环境 **https://fr.echatsoft.com** -本地化私有化服务器 服务器地址格式错误,会抛出Exception信息,且功能异常。|否|

##### **接口:** 

| 参数           | 类型     | 描述                                                         | 必须 | 

| context | common.UIAbilityContext| UIAbility 组件的上下文环境 | 是 | 

| config | SDKConfig| SDK参数对象 | 是 | 

请将 appId , appsecret , serverToken , serverAppId , serverEncodingKey , platformId ,替换成对应参数, 详情咨询技术支持。 

##### **SDK初始化接口** 

当前接口将会启动SDK,需要用户同意隐私协议等操作。 

!> 使用SDK的功能/API,必须完成SDK初始化。 

await EChatSDK.init(); 

##### **示例** 

import { EChatSDK, SDKConfig } from '@echat/echat_sdk'; 

export default class EntryAbility extends UIAbility { async onCreate(want: Want, launchParam: AbilityConstant.LaunchParam): Promise<void> { 

// ************* 初始化配置 begin ************* let config = new SDKConfig(); config.appId = 'SDKJYBJCUXNUFZM3VTU'; config.appSecret = 'WU2ZM9IRYWFTKPZFAGJWQESYBGLPCTSAYHH2PSFLYJK'; config.serverToken = 'H5kYtPMFasd'; 

config.serverAppId = 'B6D767D2F8ED5D21A44B0E5886680CB9'; config.serverEncodingKey = 'j9pmjIpzUjepvwYGWZvvj59VR9UYRyJ5Q9bQX476wzn'; config.companyId = 22; EChatSDK.setConfig(this.context, config); // ************* 初始化配置 end ************* // 初始化SDK await EChatSDK.init(); } // 省略其它代码 } 

### **启动对话窗口** 

请在需要打开对话窗口的地方,调用如下代码: 

EChatSDK.getInstance().openChat(new ParamsConfig(22)); 

##### **接口定义** 

async openChat(params: ParamsConfig) 

|**参数**|**类型描述**|**必须**|
|---|---|---|
|paramConfig|ParamsConfig 对话参数|否|
|**参数对话参数** 一洽提供ParamsConfig类,|**类型描述** 用于配置对话参数。具体使用方法,请咨询一洽专属客服。|**必须**|
|companyId|number 商户/平台Id|是|
|echatTag|String 对话入口标识|否|
|routeEntranceId|number 咨询入口|否|
|visEvt|VisEvt 图文消息|否|
|myData|String 会员补充信息|否|
|acdStaffId|String 指派接待客服的ID|否|
|acdType|String 分配优先级,0-优先,1-指派|否|
|fm|Record<String, String>|否|

fm参数请查看 **Echat-接入对话带入访客消息** 文档。 

**使用例子:** 

import { EChatSDK, ParamsConfig } from '@echat/echat_sdk'; 

```arkts
let params = new ParamsConfig(22); params.myData = 'this is my data'; params.echatTag = 'android'; EChatSDK.getInstance().openChat(params); 
```

##### **附加对话参数:** 

##### 携带文本消息 

import { EChatSDK, ParamsConfig } from '@echat/echat_sdk'; 

```arkts
let params = new ParamsConfig(22); let fm: Record<string, string> = {} fm['msgType'] = 'text'; fm['content'] = '测试内容'; params.fm = fm; EChatSDK.getInstance().openChat(params); 
```

##### 携带图片消息 

```arkts
import { EChatSDK, ParamsConfig } from '@echat/echat_sdk'; let params = new ParamsConfig(22); let fm: Record<string, string> = {} fm['msgType'] = 'image'; fm['picUrl'] = 'https://qnfile.echatsoft.com/7bf5ba09-4d5a-4158-b175-bdef6f094c69'; fm['thumbUrl'] = 'https://qnfile.echatsoft.com/7bf5ba09-4d5a-4158-b175-bdef6f094c69?imageView2/0/w/200/h/150'; params.fm = fm; EChatSDK.getInstance().openChat(params); 
```

##### 其他类型消息以此类推 

### **启动消息盒子窗口** 

请在需要打开消息盒子窗口的地方,调用如下代码: 

EChatSDK.getInstance().openBox(); 

|**参数**|**类型**|**描述**|**必须**|
|---|---|---|---|
|echatTag|String|对话入口标识|否|

### **图文消息** 

访客在对话的过程中需要选择了某个需要制定的订单或者商品等,发送至客服,可以调用以下方法,以图文消息的 形式发送给客服,VisEvt为Java对象。 

#### **图文消息对象VisEvt** 

|**参数**|**类型**|**作用**|
|---|---|---|
|eventId|String|图文消息的ID,可自定义前缀或者其他格式来通知业务系统图文消息的消 息类型:比如:prod-123 ,order-123等|
|title|String|图文消息的标题,如:新款风衣|
|content|String|图文消息的描述,支持div span style属性,如:产品的价格,优化信息等|
|imageUrl|String|图文消息的图片地址|
|urlForVisitor|String|图文消息提供给访客打开的url,可以为空。 url只允许为http[s]协议,支持新窗口打开以及对话窗口的互动窗口打开。 协议格式:http(url,openType) 新窗口打开:http('**http://m.echatsoft.com**','blank') 互动窗口打开:http('**http://m.echatsoft.com**','inner')|
|urlForStaff|String|图文消息提供给客服打开的url,可以为空。支持http[s]协议和apiUrl协议。 http协议和urlForVisitor参数中的http协议一致. apiUrl协议:apiUrl(pageId,openType). pageId:业务系统的页面ID openType:打开类型reload:重载打开hash:不刷新已有的业务系统页面. 重载打开: apiUrl(123,'reload'); hash打开: apiUrl(123,'hash');|
|memo|number|图文消息的描述,如:产品评价等|
|visibility|number|图文消息的可见范围. 1:访客客服都可见(默认) 2:只有客服可见,访客不可见|
|customizeMsgType|number|此消息的类型,关系到消息响应时长和访客会话条数指标。 1:访客/客服消息 2:系统消息 默认:首次打开对话窗口时携带的图文消息为系统消息|

#### **打开消息窗口时携带图文消息** 

##### 以下情况图文消息将不再发送 

##### 最近一条消息和打开消息窗口携带的图文消息一致 

import { EChatSDK, ParamsConfig, VisEvt } from '@echat/echat_sdk'; 

```arkts
let params = new ParamsConfig(22); let visEvt = new VisEvt(); visEvt.eventId = 'cook1002'; visEvt.content = 
```

'原价:¥185.50促销:¥104.70运费:卖家承担运费'; visEvt.title = '⻄⻄里#韩国秋冬百搭纯色V领衬衫'; 

visEvt.imageUrl = 

'https://demo.echatsoft.com/web/html/demoMall/url/visitorUrl/myproduct/images/2.jpg'; visEvt.urlForVisitor = 

'http("https://demo.echatsoft.com/web/html/demoMall/url/staffUrl/myproduct/? eventId=cook1002","inner")'; 

visEvt.urlForStaff = 

'http("https://demo.echatsoft.com/web/html/demoMall/url/staffUrl/myproduct/? eventId=cook1002","inner")'; visEvt.memo = '评价(2958)'; params.visEvt = visEvt; EChatSDK.getInstance().openChat(params); 

#### **SDK接口发送** 

可在非对话界面直接向客服发送图文消息。 

- !> 目标公司正在对话中,才可以通过该接口发送图文消息。 

let visEvt = new VisEvt(); visEvt.eventId = 'cook1002'; visEvt.content = 

'原价:¥185.50促销:¥104.70运费:卖家承担运费'; visEvt.title = '⻄⻄里#韩国秋冬百搭纯色V领衬衫'; visEvt.imageUrl = 

'https://demo.echatsoft.com/web/html/demoMall/url/visitorUrl/myproduct/images/2.jpg'; visEvt.urlForVisitor = 

'http("https://demo.echatsoft.com/web/html/demoMall/url/staffUrl/myproduct/? eventId=cook1002","inner")'; 

visEvt.urlForStaff = 

'http("https://demo.echatsoft.com/web/html/demoMall/url/staffUrl/myproduct/? eventId=cook1002","inner")'; 

visEvt.memo = '评价(2958)'; 

let result = await EChatSDK.getInstance().sendVisEvt(visEvt); 

##### **回调返回参数** 

|**参数**|**类型**|**作用**|
|---|---|---|
|||发送成功失败标记|
|返回值|boolean|true发送成功 false发送失败|

### **关闭对话** 

关闭该用户的所有对话。 

关闭通信连接,参考 **更多 - 关闭通信** 

public async closeAllChats(): Promise<boolean> 

|**参数**|**类型**|**作用**|
|---|---|---|
|||发送成功失败标记|
|返回值|boolean|true发送成功 false发送失败|

##### **例子** 

let result = await EChatSDK.getInstance().closeAllChats(); if (result) { 

// 关闭全部对话调用成功 } else { // 关闭全部对话调用失败 } 

### **关闭通信** 

关闭SDK通信,不会影响对话状态。 

##### **其他情况** 

App重新初始化时,检测到本地有暂未结束的通话,则会重新打开通信。 

开启某些特殊场景功能,则会周期性的通信。 

public async closeConnection() 

##### **例子** 

await EChatSDK.getInstance().closeConnection(); ' ' ToastUtil.showToast( 关闭通知完成调用 , { alignment: Alignment.Bottom }) 

# **合规处理建议** 

在国家新规要求下,App必须满足合规需求,建议进行以下处理。 

## **合规处理建议步骤** 

**请您务必告知目标用户选择了一洽客服系统SDK服务,说明App中使用的一洽SDK名称,一洽SDK收集和使用的最终 用户的个人信息的目的、方式范围,并获得用户对于使用App期间一洽SDK收集、使用最终用户相关个人信息的完 整、合法、持续有效的授权同意。** 

### **方式一** 

以文本形态向用户展示,例如: 

我们的产品集成一洽客服系统SDK,一洽客服系统SDK需要 收集、采集设备信息、设备标识信息、手机系统 信息、当前应用信息、网络信息, 用于单次安装设备标识,以便将用户操作日志与错误日志提交上报,分析判 断运行环境,分析用户使用情况,分析错误异常问题的原因; 需要采集网络信息(WIFI状态、蜂窝网状态、IP 地址),用于了解设备的网络状态和变化,从而最大程度保持网络连接的稳定性。 

### **方式二** 

以表格形态向用户展示,例如: 

|**SDK名称**|**第三方名称**|**使用目的**|**搜集个人信息类型**|**隐私权政策链接**|
|---|---|---|---|---|
|一洽客|深圳市虹红|提供客|收集类型:设备信息、设备标识信息、||
|服系统|科技有限公|服会话|手机系统信息、当前应用信息、网络信|**https://www.echatsoft.com/privacy/privacy.html**|
|SDK|司|服务|息||

## **延迟初始化SDK方案** 

##### SDK提供setConfig与init方法: 

1. EChatSDK.setConfig(this.context, config); 用于配置SDK参数,不会启动SDK,但务必在App 首个启动的Ability中进行配置。 

2. EChatSDK.init(); 用于初始化SDK,启动SDK,务必在用户同意隐私协议后调用。其他SDK API调用 前,务必确保SDK初始化完成。 

### **1. 设置SDK配置** 

- !> 请务必在App首个启动的Ability中进行配置,否则可能造成SDK配置信息异常,调用SDK配置不会启动SDK。 

import { EChatSDK, SDKConfig } from '@echat/echat_sdk'; 

export default class EntryAbility extends UIAbility { async onCreate(want: Want, launchParam: AbilityConstant.LaunchParam): Promise<void> { 

// 初始化配置满足隐私合规,不会启动任何与SDK相关功能。 // 请务必在此处配置。 // ************* 初始化配置 begin ************* let config = new SDKConfig(); config.appId = 'SDKJYBJCUXNUFZM3VTU'; config.appSecret = 'WU2ZM9IRYWFTKPZFAGJWQESYBGLPCTSAYHH2PSFLYJK'; config.serverToken = 'H5kYtPMFasd'; config.serverAppId = 'B6D767D2F8ED5D21A44B0E5886680CB9'; config.serverEncodingKey = 'j9pmjIpzUjepvwYGWZvvj59VR9UYRyJ5Q9bQX476wzn'; config.companyId = 22; EChatSDK.setConfig(this.context, config); 

// ************* 初始化配置 end ************* } onWindowStageCreate(windowStage: window.WindowStage): void { windowStage.loadContent('pages/Index', (err) => { if (err.code) { return; } // 用于记录用户是否同意隐私协议 PersistentStorage.persistProp('agreePrivacy', false); }); } // 省略其它代码 } 

### **2. 初始化SDK** 

此时开始判断,用户是否已经同意隐私协议: 

1. 已经同意协议,则立刻初始化SDK 

2. 未同意协议,则不初始化SDK,不调用SDK的业务接口,弹出隐私协议弹窗,等待用户同意后再初始化 SDK。 

```arkts
import { EChatSDK, ParamsConfig } from '@echat/echat_sdk'; import { promptAction } from '@kit.ArkUI'; 
```

@Entry @Component struct Index { @StorageLink('agreePrivacy') agreePrivacy: boolean = false; 

async aboutToAppear(): Promise<void> { if (this.agreePrivacy) { // 隐私协议已同意,进行SDK初始化 await EChatSDK.init(); } else { // 隐私协议未同意,弹出隐私协议弹窗 this.showPrivacyDialog(); } } showPrivacyDialog() { promptAction.showDialog({ title: '隐私政策授权', message: '隐私政策说明...', buttons: [ { text: '不同意', color: '#ffff0000' }, 

{ text: '同意协议', color: '#ff0041ff' } ] }, async (err, data) => { if (err) { // 未点击按钮,直接关闭弹窗 return; } if (data.index === 1) { // 同意隐私协议 // StorageLink + PersistentStorage 自动保存用户同意状态 this.agreePrivacy = true; // SDK 初始化 await EChatSDK.init(); } }); } build() { // 省略其它代码 } } 

# **会员接入** 

会员接入又名:用户信息接入、接入会员信息、接入会员、业务系统集成。 

## **会员登录** 

设置会员信息,变成会员身份。 

##### **生效时机** : 

1. 当前对话结束 且 通信结束,再次打开对话时。 

2. 当前为匿名访客身份,应用被关闭,下次打开对话时,变成会员身份。 

##### **调用时机** : 

   1. 需要以会员身份对话,打开对话窗口前 

   2. 需要以会员,调用SDK接口前 

- !> **注意事项:** 

1. 请确保SDK初始化完成. 

2. 调用SDK初始化,禁止立刻执行该接口。 

调用代码如下: 

EChatSDK.getInstance().setUserInfo(userInfo) 

public setUserInfo(userInfo: UserInfo) 

##### **UserInfo参数** 

|**参数**|**类型**|**描述**|**必须**|
|---|---|---|---|
|uid|String|会员的唯一值,支持数字、英文大小写、字符。 其中支持字符如下:!, #,$,(,),*,+,-,.,@,_,{,~,}传入不支持字符当做匿名访客处 理,最长不超过50位|是|
|grade|String|会员级别 传值:0 / 1 / 2 / 3 ...|否|
|category|String|会员类别,最长不超过50位 例如:金牌会员|否|
|name|String|会员姓名,最长不超过50位 例如:王宝|否|
|nickName|String|会员的昵称,最长不超过50位 例如:宝宝|否|
|gender|int|会员的性别 传值:0-未知,1-男,2-女|否|
|age|int|会员的年龄>=0; <=100|否|
|birthday|String|会员的生日,格式yyyy-MM-dd例如:1990-08-01|否|
|maritalStatus|int|婚姻状况1:未婚2:已婚0:未知|否|
|phone|String|会员的联系电话,最长不超过50位|否|
|qq|String|会员的QQ号码,最长不超过50位|否|
|wechat|String|会员的微信号码,最长不超过50位|否|
|email|String|会员的邮箱,最长不超过50位|否|
|nation|String|会员的国家,最长不超过50位|否|
|province|String|会员的省份,最长不超过50位|否|
|city|String|会员的城市,最长不超过50位|否|
|address|String|会员的地址,最长不超过50位|否|
|photo|String|会员的头像地址,最长不超过255位|否|
|memo|String|会员备注信息,最长不超过255位|否|
|c1-c20|String|会员自定义字段,最长不超过255位|否|

##### **例子** 

let info = new UserInfo(); 

info.uid = uid;//唯一值, 不同用户该值不同 info.vip = 1 info.name = "旭宝宝4" info.nickName = "旭宝宝4" info.gender = 2 info.grade = "3" info.category = "金牌会员" info.age = 30 info.birthday = "1990-01-01" info.maritalStatus = 2 info.phone = "13888888888" info.qq = "493888489" info.wechat = "xubbb" info.email = "xubbb3212@qq.com" info.nation = "中国" info.province = "广东" info.city = "深圳市" info.address = "广东省深圳市南山区粤海街道100号" info.photo = "https://vfile.rainbowred.com/group1/M00/A9/A7/wKhCBGMiglSAaHezAAARhGlFe90967.png" info.memo = "高价值会员" EChatSDK.getInstance().setUserInfo(info); 

## **会员退出** 

清空会员信息,退出当前会员。 

**生效时机** : 

1. 当前对话结束,且通信结束,下次接入对话。 

##### **调用时机** : 

1. App自身会员退出时 

   2. App自身会员切换时 

- !> **注意事项:** 

1. 请确保SDK初始化完成. 

2. 调用SDK初始化,禁止立刻执行该接口。 

调用代码如下: 

##### 接口为耗时接口,请在子线程执行。 

EChatSDK.getInstance().clearUserInfo() 

public setUserInfo(userInfo: UserInfo) 

## **获取会员信息** 

##### 获得当前配置的会员信息。 

- !> 1. 请确保SDK初始化完成. 

调用代码如下: 

public getUserInfo(): UserInfo | null 

let userInfo = EChatSDK.getInstance().getUserInfo(); 

## **Q&A问题** 

1. 调用setUserInfo(userInfo)接口后,客服端的访客信息并未发生变动? 

   - A:需要等待本次对话结束且通信结束,再次接入对话,则访客信息将会被更新。 

2. 怎么才能使会员信息快速生效? 

   - A:App执行退出当前会员操作时,执行以下操作 

##### **退出会员时:** 

// 关闭当前客户全部对话 

// 该接口为网络接口,因网络情况可能会失败。 await EChatSDK.getInstance().closeAllChats(); // 关闭当前通信 await EChatSDK.getInstance().closeConnection(); EChatSDK.getInstance().clearUserInfo(); 

##### **更新会员信息时:** 

// 关闭当前客户全部对话 // 该接口为网络接口,因网络情况可能会失败。 await EChatSDK.getInstance().closeAllChats(); // 关闭当前通信 await EChatSDK.getInstance().closeConnection(); EChatSDK.getInstance().setUserInfo(....); // 如需更新会员信息后,打开对话窗口 

// 建议通过setTimeout延迟打开对话窗口 setTimeout(() => { EChatSDK.getInstance().openChat(); }, 400); 

# **消息推送通知** 

一洽将消息通知区分为: 

本地消息通知 

远程消息通知 

- 三方推送消息 

- 厂家推送消息 

本地消息出现的条件满足以下条件: 

App存活 

- 收到需要提醒的消息 

不在业务界面,以下为解释: 

- App在后台运行 

前台界面不是一洽对话界面或一洽消息盒子 

远程消息通知,通过一洽客服系统配置了开发者的服务器API,当App网络被阻断 或 App被系统销毁或暂停,有新 的需要提醒的消息,一洽后端会主动访问配置好的地址,告知开发者推送的消息内容与各种参数。开发者可以通过 这些参数,通过App集成的推送SDK,进行远程消息通知。 

由于鸿蒙Next系统限制,默认情况下,直接入一洽客服系统Android SDK,不做其他操作,不会有本地通知, 也不会有远程通知。需要开发者自行集成推送SDK,进行消息推送通知。 

## **本地消息接口介绍** 

### **监听本地新消息接口** 

一洽SDK,在App存活阶段,非一洽界面,收到新消息,会通过接口告知。 

开发者若需要实现通知(Notification),可以通过以下接口进行实现: 

##### **调用实际:** 

1. 确保一洽SDK已经初始化。 

2. 满足1.的情况下,App启动第一个 UiAbility 时,在 onCreate 中注册。 

##### **接口定义** 

public registerNewMessage(callback: (sdkMessage: SDKMessage) => void) 

EChatSDK.getInstance().registerNewMessage((message) => { 

}); 

##### **SDKMessage参数:** 

|**参数**|**类型**|**描述**|**必须**|
|---|---|---|---|
|title|string|推荐通知标题|是|
|content|string|推荐通知内容|是|
|companyId|number|当前消息所属公司Id|是|
|companyName|string|当前消息所属公司名称|是|
|interval|number|推荐消息通知间隔时间|是|
|msgType|number|消息类型|是|
|tm|number|消息时间戳|是|

##### **例子** 

##### 监听本地新消息,并弹出通知。 

```arkts
import { EChatSDK, NotificationUtil } from '@echat/echat_sdk'; import { AbilityConstant, common, UIAbility, Want, wantAgent } from '@kit.AbilityKit'; 
EChatSDK.getInstance().registerNewMessage((message) => { let context = getContext() as common.UIAbilityContext; let parameters: Record<string, Object> = {} parameters['companyId'] = message.companyId; parameters['companyName'] = message.companyName; let wantAgentInfo: wantAgent.WantAgentInfo = { wants: [ { deviceId: '', bundleName: context.abilityInfo.bundleName, moduleName: context.abilityInfo.moduleName, abilityName: context.abilityInfo.name, action: 'echat_new_message', entities: [], uri: '', parameters: parameters } ], actionType: wantAgent.OperationType.START_ABILITY | wantAgent.OperationType.SEND_COMMON_EVENT, requestCode: 0, actionFlags: [wantAgent.WantAgentFlags.CONSTANT_FLAG] }; 
```

// 获取WantAgent wantAgent.getWantAgent(wantAgentInfo).then((wantAgent) => { let id = NotificationUtil.generateNotificationId(); let basicOptions: NotificationBasicOptions = { 

id: id, title: message.title, text: message.content, tapDismissed: true, wantAgent: wantAgent } NotificationUtil.publishBasic(basicOptions); }); }); 

##### 用户点击通知,打开对话窗口 

export default class EntryAbility extends UIAbility { 

async onCreate(want: Want, launchParam: AbilityConstant.LaunchParam): Promise<void> { // 省略其它代码 

// 处理通知 this._handleNotification(want); } 

```arkts
onNewWant(want: Want, launchParam: AbilityConstant.LaunchParam): void { // 处理通知 this._handleNotification(want); } _handleNotification(want: Want) { if (want.action == 'echat_new_message' && want.parameters) { let companyId = want.parameters['companyId'] as number; let companyName = want.parameters['companyName'];) let params = new ParamsConfig(companyId); EChatSDK.getInstance().openChat(params); NotificationUtil.cancelAll(); } } // 省略其它代码 } 
```

### **取消监听本地新消息接口** 

##### **调用实际:** 

1. 确保一洽SDK已经初始化。 

2. 满足1.的情况下,App启动第一个 UiAbility 时,在 onDestory 中调用。 

##### **接口定义** 

public unregisterNewMessage() 

EChatSDK.getInstance().unregisterNewMessage(); 

## **未读消息数接口** 

- 一洽SDK的未读消息数接口,原则以SDK本地的未读消息的数量为准。即SDK与一洽服务器通信后,获取未读消 息,APP进行数量上的更新显示。 

- !> 当APP(SDK)与一洽服务器建立通信出现障碍,则未读消息数不会进行更新。 

若通过远程推送等其他方式更新,加大了未读消息数的维护难度,同时容易导致数据不准确等问题。不建议 通过远程推送方式,统计未读消息数总数。 

### **获得未读消息数** 

该接口为静态接口: 

   1. 未指定公司Id,查询当前用户,全部商户当前未读消息数。 

   2. 指定公司Id,查询当前用户,指定商户当前未读消息数。 

- !> 为耗时接口,强烈建议不要进行频繁调用。 

public async getUnreadCount(companyId?: number): Promise<number> 

let unreadCount = await EChatSDK.getInstance().getUnreadCount(); let unreadCount = await EChatSDK.getInstance().getUnreadCount(22); 

##### **传入参数** 

|**参数**|**类型**|**描述**|**必须**|
|---|---|---|---|
|companyId|number|公司id|否|

##### **返回参数** 

|**返回参数类型**|**说明**|
|---|---|
|number|未读消息数|

### **监听未读消息数变动** 

一洽SDK,在App存活阶段,非一洽界面,收到新消息,未读消息数变动时,会通过接口告知。 

未读消息数变动条件: 

   1. 收到需要通知的本地消息,告知当前商户/公司的未读消息数。 

   2. 用户点击进入对话窗口,未读消息已读,告知当前商户/公司的未读消息数已清空。 

- !> 注册监听后,注意鸿蒙Next的生命周期变动,及时取消监听。 

##### **接口定义** 

public addUnreadCountChange(callback: (companyId: number, count: number) => void) 

EChatSDK.getInstance().addUnreadCountChange(async (companyId: number, unreadCount: number) => { 

}); 

##### **参数:** 

|**参数**|**类型**|**描述**|**必须**|
|---|---|---|---|
|companyId|number|公司Id,所属公司的未读消息数|是|
|unreadCount|number|未读消息数|是|

### **取消监听未读消息数变动** 

取消全部未读消息数变动监听。 

##### **接口定义** 

public removeUnreadCountChange() 

EChatSDK.getInstance().removeUnreadCountChange();
