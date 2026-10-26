# **RTC 融云音视频 ( ) SDK 客户端 文档** HarmonyOS CallKit 1.x 

2025-06-26 

## **目录** 

|导入CallKit SDK|5|
|---|---|
|环境要求|5|
|自动导入SDK|5|
|手动导入SDK|6|
|执行命令行|6|
|entry配置文件依赖SDK|6|
|同步项目|7|
|添加SDK依赖权限|7|
|实现音视频通话|8|
|环境要求|9|
|前置条件|9|
|快速上手|9|
|步骤1导入SDK|9|
|步骤2初始化|9|
|步骤3连接IM服务|10|
|步骤4实现监听|10|
|步骤5呼叫方|12|
|发起单人呼叫|12|
|发起多人呼叫|13|
|步骤6接听方|17|
|AI智能流式语音识别和翻译|17|
|AI智能流式语音识别|17|
|准备工作|18|
|设置是否显示语音识别UI|18|
|参数说明|18|
|示例代码|19|
|语音识别语言代码列表|19|
|AI智能流式语音翻译|21|

- 2 - 

|全场景适用|21|
|---|---|
|前置条件|21|
|翻译设置|21|
|语音翻译语言代码列表|22|
|AI智能总结|30|
|全场景适用|30|
|前置条件|30|
|服务开通|30|
|功能依赖|30|
|使用方式|31|
|通话进行中|31|
|通话结束后|31|
|总结内容说明|31|
|推送管理|31|
|鸿蒙管理后台配置推送|32|
|APP申请通知权限|32|
|APP获取推送token|32|
|IMLib设置推送token|32|
|接口原型|33|
|示例代码|33|
|点击推送唤起APP|33|
|管理通知角标|34|
|CallKit客户端API|34|
|版本说明|35|
|26.1.0 - 2026-2-3|35|
|新增|35|
|25.12.0 - 2025-12-31|35|
|新增|35|
|25.11.0 - 2025-11-28|35|
|修复|35|
|1.10.0 - 2025-10-31|36|
|新增|36|

- 3 - 

修复 

|修复|36|
|---|---|
|1.9.0 - 2025-09-26|36|
|新增|36|
|1.8.0 - 2025-08-29|36|
|新增|36|
|修复|36|
|1.7.0 - 2025-07-24|36|
|新增|36|
|修复|37|
|1.6.0 - 2025-06-27|37|
|新增|37|
|状态码|37|
|合规指南|38|
|实时音视频CallKit SDK合规使用说明|38|
|一、App个人信息保护的合规要求|38|
|二、App使用CallKit SDK时的合规指引|38|
|1. SDK所需的系统权限的说明|38|
|HarmonyOS操作系统SDK功能、接口配置方式及示例说明:|39|
|2. SDK初始化及业务功能调用时机说明|39|
|3. SDK隐私政策披露要求与示例说明|40|
|4.最终用户同意方式的建议方式说明及示例|40|
|5.最终用户行使权利的配置说明|44|
|三、合规文件指引|44|
|四、联系方式|44|

- 4 - 

#### **导入 CallKit SDK** 

融云支持使用 DevEco Studio 中自动导入和手动导入两种方式,将 CallKit SDK 导入到您的应用工程中。 

###### **环境要求** 

- DevEco Studio NEXT Release(5.0.3.900) 及以上。 

- HarmonyOS SDK API 12 及以上。 手机系统版本号:NEXT.0.0.31 

###### **自动导入 SDK** 

CallKit 1.6.0 版本开始支持 OpenHarmony三方库中心 获取 SDK 

1. 在当前项目目录(示例 entry)中的 oh-package.json5 中添加 SDK 依赖,然后点击 "Sync Now" 。 

###### **JSON** 

// entry 目录中的 oh-package.json5 { "name": "entry", "version": "1.0.0", "description": "Please describe the basic information.", "main": "", "author": "", "license": "", "dependencies": { "@rongcloud/callkit": "x.y.z", "@rongcloud/calllib": "x.y.z", "@rongcloud/imlib": "x.y.z", "@rongcloud/imkit": "x.y.z", } } 

###### **注意** 

各个 SDK 的最新版本号可能不相同,具体 x.y.z 值可前往 融云官网 SDK 下载页面 或 OpenHarmony三方库中心 查 询。 

1. 安装 SDK 成功后,您可以在项目根目录的 **oh_modules/.ohpm/** 中找到融云 CallKit SDK。 

- 5 - 

2. 查看更多其他融云 SDK。 打开 OpenHarmony三方库中心 ,搜索关键字 **rongcloud** 

###### **手动导入 SDK** 

1. 在导入 SDK 前,您需要前往融云官网 SDK 下载页面,将音视频通话(包含 UI)SDK 下载到本地。 

2. 创建 **./libs** 文件夹,将所需 SDK **har 包** 

CallKit.har 、 CallLib.har 、 RongIMLib.har 、 RongIMKit.har、 RTCLib.har 放入其中。 

##### **执行命令行** 

1. 在工程根路径下执行以下命令行: 

###### **shell** 

ohpm install libs/CallKit.har 

2. 执行完后,Studio 根据工程路径在 oh-package.json5 自动添加依赖。 

##### **entry 配置文件依赖 SDK** 

在 **entry** 同级目录的 oh-package.json5 手动配置 SDK 依赖。 

###### **JSON** 

- // entry 同级目录下的 oh-package.json5 需要手动配置 { "name": "xxx", "version": "1.0.0", 

"description": "Please describe the basic information.", 

"main": "", "author": "", 

- "license": "", 

"dependencies": { 

- "@rongcloud/callkit": "file:../libs/CallKit.har",  // 该配置手动依赖 

"@rongcloud/calllib": "file:../libs/CallLib.har",  // 该配置手动依赖 

"@rongcloud/imlib": "file:../libs/RongIMLib.har",  // 该配置手动依赖 

"@rongcloud/imkit": "file:../libs/RongIMKit.har",  // 该配置手动依赖 

}, 

"devDependencies": { 

"@ohos/hypium": "1.0.16", "@ohos/hamock": "1.0.0" } } 

- 6 - 

##### **同步项目** 

在 entry/oh-package.json5 中点击 **Sync Now** 同步工程,同步成功之后即可正常使用 CallKit SDK。 

###### 提示 

如果您同步之后依然无法导入 SDK,这可能是 DevEco Studio 的编译缓存导致的问题。您可以尝试把 DevEco Studio 完全关闭之后重新打开项目工程来解决问题。 

###### **添加 SDK 依赖权限** 

###### SDK 需要权限如下: 

|权限名称|权限说明|使用目的|
|---|---|---|
|ohos.permission.GET_NETWORK_INFO|获取网络信息|网络变化之后获取网络信息,进行IM重连|
|ohos.permission.INTERNET|使用网络|连接IM、收发消息需要网络连接|
|ohos.permission.STORE_PERSISTENT_DATA|数据存储|消息数据库需要本地存储|
|ohos.permission.MICROPHONE|麦克风权限|音频通话需要麦克风采集能力|
|ohos.permission.CAMERA|摄像头权限|视频通话需要摄像头采集能力|
|ohos.permission.KEEP_BACKGROUND_RUNNING|后台任务|后台保活用于音视频通话|
|ohos.permission.VIBRATE|响铃|来电提醒|
|ohos.permission.RUNNING_LOCK|熄屏|音频通话时附耳熄屏|

1. 找到项目 entry/src/main/ 目录下的 module.json5 文件,添加 requestPermissions 配置,以配置摄像头权限为例: 

###### **JSON** 

- 7 - 

"requestPermissions": [ { "name": "ohos.permission.CAMERA", "reason": "$string:Camera", "usedScene": { "abilities": [ "EntryAbility", ], "when": "always" } }, ... // 配置其他权限 ] 

###### 具体权限配置参数含义,请参考鸿蒙的应用权限管控文档。 

2. 配置权限时,按照规则需要考虑国际化问题。在项目 entry/src/main/resources/base/element 目录下找到 string.json 文件,对应增加配置字符变量,以配置摄像头字符变量为例: 

###### **JSON** 

{ "string": [ { "name": "Camera", "value": "Camera in RTC" }, ... // 定义其他 ] } 

#### **实现音视频通话** 

CallKit 基于 CallLib SDK 基础增加了一套默认呼叫界面,包含了单人、多人音视频呼叫的各种场景和功能。 

###### 提示 

###### **房间人数上限** 

1. 考虑移动设备的带宽(主要是在多路视频情况下)和 UI 交互效果,建议单次通话或房间内,视频不超过 16 人, 纯音频不超过 32 人。超过此上限可能影响通话效果。 

2. CallKit 代码中已设置人数上限。默认发起视频呼叫时,最多可选 7 人。发起音频呼叫时,最多可选 20 人。如需 

- 8 - 

调整,建议不超过默认上限。 

###### **环境要求** 

适用于 HarmonyOS 的 CallKit SDK 的最低要求是: 

- DevEco Studio NEXT Release(5.0.3.900) 及以上。 

- HarmonyOS SDK API 12 及以上。 

- 手机(真机)系统版本号:NEXT.0.0.31 

###### **前置条件** 

- 创建融云开发者账号,获取 App Key。注册成功后,融云控制台会默认自动创建您的首个应用,默认生成 **开发** 环境下的 App Key,使用国内数据中心。 **注意** :同一个应用的 **开发** 环境与 **生产** 环境提供不同的 App Key,两个环境之间数据隔 离。 

开通 **音视频通话** 服务。 

###### **快速上手** 

##### **步骤 1 导入 SDK** 

导入融云音视频通话能力 UI 库 CallKit,具体步骤请参阅 导入 CallKit SDK。 

##### **步骤 2 初始化** 

重要提示 

- 从 1.9.0 版本开始,必须先调用 RCCall.install() 方法加载 CallKit 模块,且该方法必须在 IM 初始化之前调用。 

RTC 音视频能力是基于 IM 作为信令通道的,CallKit 又依赖于 IMKit & CallLib,所以要先初始化 IM。如果不换 AppKey, 在整个应用生命周期中,初始化一次即可。建议调用位置放在应用启动位置处,或在音视频功能模块的加载位置处。在 UIAbility 的 onCreate() 方法中,调用初始化方法,传入生产或开发环境的 App Key。 

###### **TypeScript** 

- 9 - 

//1.9.0 版本新增方法:加载 CallKit 模块,必需在 IM 初始化之前调用。 RCCall.install(); 

// 在 UIAbility 中获取 context let context = this.context let initOption = new InitOption(); let appKey = "从融云后台获取的 appKey"; IMEngine.getInstance().init(context, appKey, initOption); 

##### **步骤 3 连接 IM 服务** 

音视频用户之间的信令传输依赖于融云的即时通信(IM)服务,因此需要先调用 connect 与 IM 服务建立好 TCP 长连接。建 议在功能模块的加载位置处调用,之后再进行音视频呼叫业务。当模块退出后调用 disconnect 或 logout 断开该连接。 

###### **TypeScript** 

// 连接 IM 

IMEngine.getInstance().connect(token, 20).then(result => { 

if (EngineError.Success === result.code) { 

- // 连接成功 let userId = result.userId; 

return } 

if (EngineError.ConnectTokenExpired === result.code) { 

   - // Token 过期,从 APP 服务请求新 token,获取到新 token 后重新 connect() 

- } else if (EngineError.ConnectionTimeout === result.code) { 

   - // 连接超时,弹出提示,可以引导用户等待网络正常的时候再次点击进行连接 

- } else { 

- //其它业务错误码,请根据相应的错误码作出对应处理。 

- } }); 

##### **步骤 4 实现监听** 

在通话前需要设置 RCCall 的 RCCallListener 监听,在 CallKit 页面跳转时提供必要的 UI 组件。 

###### **TypeScript** 

RCCall.getInstance().callListener = { /** 

* 获取当前 Ability 页面对应的 WindowStage 实例。 * * 说明: 

- - 在 Ability 的生命周期方法 `onWindowStageCreate` 中,首次创建并缓存 `windowStage`。 

- - 通过 `didWindowStage` 方法获取缓存的 `windowStage`,方便在其他逻辑中调用。 

* 

- 10 - 

* 

* 示例: 

* ```ts 

- onWindowStageCreate(windowStage: window.WindowStage): void { 

- // 主窗口创建完成,缓存 windowStage 以便后续使用 

- AppStorage.setOrCreate('windowStage', windowStage); 

* } 

* ``` * 

- @returns 当前 Ability 缓存的 WindowStage 实例 

*/ 

didWindowStage: () => { 

- let windowStage = AppStorage.get('windowStage') as window.WindowStage 

- return windowStage 

}, /** 

- 多人通话选人页面导航栈, 用于选人页面导航, 必须设置, 否则无法导航到选人页面 

* ⚠️ 注意: 

- 该方法必须返回当前页面中实际使用的 Navigation 容器绑定的 NavPathStack 对象。 

* 

- * 正确示例(页面中定义并绑定了 navStack): 

- 

* ```ts 

- private navStack: NavPathStack = new NavPathStack(); 

* 

- Navigation({ stack: this.navStack }) { 

- // 页面内容 

* } 

*/ 

didMultiCallNavPathStack: () => { 

return this.navStack; // � 返回实际绑定在 UI 上的导航栈 }, /** 

- 点击 CallKit 横幅或左上角胶囊后跳转回到的 Ability 页面名 

###### * ⚠️ 注意: 

- 此处的页面名须使用 module.json5 中 module -> abilities -> name 定义字义的字符串 */ 

didCallKitNavAbilityName: () => { 

- /// 该方法返回,所集成项目的 UIAbility 

return 'CallKitEntryAbility' }, /** 

- 是否允许选择某个用户 

- 非必传,默认允许选择 

- @param userId 用户 userId 

*/ 

- 11 - 

*/ didUserSelectable: async (userId: string): Promise<boolean> => { /** * 根据条件判断是否允许选择该用户 * 不允许时返回 false */ return false; }, /** * 按钮插件过滤 * 非必传,插件默认显示 * @param id 会话对象 * @param mediaType 媒体类型,音频或视频 * @returns boolean */ didPluginFilter: (id: ConversationIdentifier, mediaType: RCCallMediaType): boolean => { // 如需过滤掉视频插件 if (mediaType === RCCallMediaType.VIDEO) { return false; }; } } 

##### **步骤 5 呼叫方** 

通常 App 内呼叫和被叫方逻辑会同时存在,所以需要分别集成。 

##### **发起单人呼叫** 

###### **TypeScript** 

/** 

* 发起单聊呼叫 

- @param userId 被叫端Id 

- @param mediaType 呼叫媒体类型 

*/ 

public startSingleCall(targetId: string, mediaType: RCCallMediaType) 

|参数|类型|必填|说明|
|---|---|---|---|
|targetId|string|是|对方的用户ID|
|mediaType|RCCallMediaType|是|媒体类型|

示例代码: 

- 12 - 

**TypeScript** 

###### // 使用时填写真实 id 

let targetId = '被叫端UserId' // 媒体类型 RCCallMediaType 

let mediaType = RCCallMediaType.VIDEO RCCall.getInstance().startSingleCall(targetId, mediaType) 

##### **发起多人呼叫** 

1. 调用 startMultiCall 会先弹出群组选择成员界面,所以发起多人呼叫前,需要优先实现 IMKit 的 UserDataProvider 接 口,来提供群组信息,群成员信息等数据来源。 

###### **TypeScript** 

RongIM.getInstance().userDataService().setUserDataProvider({ /** 

- 获取群组信息数据,当需要展示群组头像、名称时,如果 SDK 没有对应的信息时触发该方法 *``` 

- 获取到群组信息后,SDK 会缓存该数据,并触发监听 

- SDK 缓存之后就会一直使用,不会自动更新。如果群组信息发生变化,需要调用 

UserDataService.updateUserInfo 主动刷新 SDK 信息 

- *``` 

- @param groupId 群 id 

- @returns 群组信息。注意:如果返回 undefined ,SDK则不会更新缓存。 

*/ 

fetchUserInfo: (userId: string) => { 

return new Promise<UserInfoModel | undefined>((resolve, reject) => { 

- // 调试代码 

- if (userId === 'test1') { 

let userInfo = new UserInfoModel(userId, 'test1_name', 'https://xxx.png') 

- resolve(userInfo) 

} }) }, /** 

- 获取群组成员信息数据,当需要展示群组成员头像、名称时,如果 SDK 没有对应的信息时触发该方法 *``` 

- 获取到群组成员信息后,SDK 会缓存该数据,并触发监听 

- SDK 缓存之后就会一直使用,不会自动更新。如果群组成员信息发生变化,需要调用 

UserDataService.updateGroupMemberInfo 主动刷新 SDK 信息 

*``` 

- @param groupId 群 id 

- @param userId 用户 Id 

- @returns 群组成员信息。注意:如果返回 undefined ,SDK则不会更新缓存。 

*/ 

- 13 - 

/ 

fetchGroupMemberInfo: (groupId: string, userId: string) => { 

return new Promise<GroupMemberInfoModel | undefined>((resolve, reject) => { 

// 调试代码 

let member: GroupMemberInfoModel = new GroupMemberInfoModel(groupId, userId, '', '') if (userId === 'test1') { 

member = new GroupMemberInfoModel(groupId, userId, 'test1_name', 

'https://xxx') } resolve(member) }) }, /** 

- 获取群成员信息数据列表,当需要展示群成员头像、名称时,如果 SDK 没有对应的信息时触发该方法 *``` 

- 获取到群组成员信息后,SDK 会缓存该数据,并触发监听 

* SDK 缓存之后就会一直使用,不会自动更新。如果群组成员信息发生变化,需要调用 UserDataService.updateGroupMemberInfo 主动刷新 SDK 信息 *``` 

- @param groupId 群 id 

- @returns 群成员信息列表 

*/ 

fetchGroupMemberInfos: (groupId: string) => { 

return new Promise<Array<GroupMemberInfoModel> | undefined>((resolve, reject) => { /// 使用 app server 提供的群成员列表信息,以下是示例测试数据 

```arkts
let members: Array<GroupMemberInfoModel> = new Array<GroupMemberInfoModel>() for (let i = 0; i < 5; i++) { 
let member: GroupMemberInfoModel = new GroupMemberInfoModel('', '', '', '') member.userId = `test${i + 1}` members.push(member) } resolve(members) }); }, /** * 获取群组信息数据,当需要展示群组头像、名称时,如果 SDK 没有对应的信息时触发该方法 *``` 
```

- 获取到群组信息后,SDK 会缓存该数据,并触发监听 

- SDK 缓存之后就会一直使用,不会自动更新。如果群组信息发生变化,需要调用 UserDataService.updateGroupInfo 主动刷新 SDK 信息 *``` 

* @param groupId 群 id 

- @returns 群组信息。注意:如果返回 undefined ,SDK则不会更新缓存。 */ 

fetchGroupInfo: (groupId: string) => { 

return new Promise<GroupInfoModel | undefined>((resolve reject) => { 

- 14 - 

```arkts
return new Promise<GroupInfoModel | undefined>((resolve, reject) > { if (groupId === 'test_group') { let model = new GroupInfoModel('test_group', '测试群', '', 3) resolve(model) } else { resolve(undefined) } }) } }) 
```

1. 实现了步骤1 中的相关协议方法提供了群信息数据,调用 startMultiCall 会先弹出选择成员界面。如下图所示,选择联 系人点击 确认 后 CallKit 发起多人呼叫。 

- 15 - 

###### **TypeScript** 

- 16 - 

/** 

###### * 发起群聊呼叫 

- @param targetId 群组Id 

- @param mediaType 呼叫媒体类型 

*/ 

public startMultiCall(targetId: string, mediaType: RCCallMediaType) 

###### 参数说明: 

|参数|类型|必填|说明|
|---|---|---|---|
|targetId|string|是|群组ID|
|mediaType|RCCallMediaType|是|媒体类型|

示例代码: 

###### **TypeScript** 

// 多人呼叫时,需要填写 IM 群组id 

let targetId = 'groupId' // 媒体类型 RCCallMediaType let mediaType = RCCallMediaType.VIDEO RCCall.getInstance().startMultiCall(targetId, mediaType) 

##### **步骤 6 接听方** 

鸿蒙 CallKit 中已经默认实现了 CallLib 库提供 RCCallClientListener 监听回调。被叫端收到呼叫,会自动弹出通话界面, 点击来电页面的接听按钮即可接听通话。 

当 App 在后台或者未启动时会收到来电通知,点击来电通知条 App 打开后会显示来电页面。 

### **AI 智能流式语音识别和翻译** 

###### **AI 智能流式语音识别** 

该功能支持在音视频通话、音视频会议、语聊房以及直播等多种场景下实时转写音频内容。AI 智能流式语音识别具有高准确率 和低延迟的特点。 

目前支持超过 50 种语言的识别,包括中文、英文、日语、韩语、阿拉伯语、法语、西班牙语、泰语、印尼语等,详见语言代 码列表。 

- 17 - 

##### **准备工作** 

AI 智能流式语音识别是融云 RTC SDK 的高级功能。若要使用,请在 AI 服务的服务购买页面开通此功能。 

##### **设置是否显示语音识别 UI** 

您可以通过 setDisplayASRUI 方法设置是否显示语音识别功能 UI。默认为显示。 

##### **参数说明** 

- 18 - 

参数 类型 

说明 

display boolean true:显示语音识别 UI false:隐藏语音识别 UI 

##### **示例代码** 

###### **typescript** 

RCCall.getInstance().setDisplayASRUI(true); 

###### **语音识别语言代码列表** 

|序号|语种中文首字母|语种中文名称|语种英文名称|语言代码|
|---|---|---|---|---|
|1|H|汉语|Chinese|zh|
|2|Y|英语|English|en|
|3|R|日语|Japanese|ja|
|4|X|西班牙语|Spanish|es|
|5|A|阿拉伯语|Arabic|ar|
|6|H|哈萨克语|Kazakh|kk|
|7|H|韩语|Korean|ko|
|8|T|泰语|Thai|th|
|9|Y|印尼语|Indonesia|id|
|10|E|俄语|Russian|ru|
|11|Y|越南语|Vietnamese|vi|
|12|F|法语|French|fr|
|13|D|德语|German|de|
|14|Y|意大利语|Italian|it|
|15|Y|印地语|Hindi|hi|
|16|M|马来语|Malay|ms|
|17|F|菲律宾语|Filipino|fl|

- 19 - 

|18|T|泰米尔语|Tamil|ta|
|---|---|---|---|---|
|19|P|葡萄牙语|Portuguese|pt|
|20|T|土耳其语|Turkish|tr|
|21|B|波兰语|Polish|pl|
|22|L|罗马尼亚语|Romanian|ro|
|23|H|荷兰语|Dutch|nl|
|24|X|希腊语|Modern Greek|el|
|25|X|匈牙利语|Hungarian|hu|
|26|Z|爪哇语|Javanese|jv|
|27|M|孟加拉语|Bengali|bn|
|28|M|缅甸语|Burmese|my|
|29|L|老挝语|Lao|lo|
|30|S|斯瓦希里语|Swahili|sw|
|31|A|阿塞拜疆语|Azerbaijani|az|
|32|B|波斯语|Persian|fa|
|33|S|僧伽罗语|Sinhala|si|
|34|J|加泰罗尼亚语|Catalan|ca|
|35|G|高棉语|Khmer|km|
|36|X|希伯来语|Hebrew|he|
|37|K|克罗地亚语|Serbo-Croatian|hbs|
|38|H|豪萨语|Hausa|ha|
|39|M|马拉地语|Marathi|mr|
|40|T|泰卢固语|Telugu|te|
|41|P|旁遮普语|Panjabi|pa|
|42|R|瑞典语|Swedish|sv|
|43|B|保加利亚语|Bulgarian|bg|
|44|D|丹麦语|Danish|da|
|45|N|挪威语|Norwegian|no|

- 20 - 

|46|K|坎纳达语|Kannada|kn|
|---|---|---|---|---|
|47|M|马拉雅拉姆语|Malayalam|ml|
|48|J|捷克语|Czech|cs|
|49|W|乌尔都语|Urdu|ur|
|50|N|尼泊尔语|Nepali|ne|
|51|M|蒙古语(外蒙)|Mongolian|mn|
|52|W|乌兹别克语|Uzbek|uz|

###### **AI 智能流式语音翻译** 

AI 智能流式语音翻译是在 AI 智能流式语音识别功能基础上增加的文本翻译功能。具备翻译延迟低、准确度高等特点,支持 200+ 语种的翻译,支持的语种详见语音翻译语言代码。 

##### **全场景适用** 

- **音视频通话** :跨国亲友聊天、海外客户对接,实时翻译让对话像母语交流般自然。 

- **多语言会议** :全球团队协作、国际研讨会,主讲内容同步译成多语言,参会者各取所需,决策效率翻倍。 

- **跨境直播** :电商出海直播、文化内容输出,实时翻译帮助主播触达全球观众,打破地域与语言的流量边界。 

##### **前置条件** 

AI 智能流式语音翻译是融云 RTC SDK 的高级功能。若要使用,请在 AI 服务的服务购买页面开通此功能。 

注意 

- AI 智能流式语音翻译是基于 AI 智能流式语音识别开发的功能,客户端使用该功能需要先集成 AI 智能流式语音识别并打开语 音识别。 

##### **翻译设置** 

您可以设置 翻译显示 和 字幕同时显示双语言。 

通过点击语音识别显示 UI 进入字幕设置页面,可以设置 翻译显示 和 字幕同时显示双语言。 

###### 提示 

CallKit 支持两种字幕展示方式: 

**仅看译文** :完全不懂源语言也能秒懂核心信息,高效获取内容。 

**原文 + 译文对照** :略懂源语言时可校验翻译准确性,专业场景(如商务会议、学术研讨)更安心。 

- 21 - 

###### **语音翻译语言代码列表** 

|序号|语种中文首字母|语种中文名称|语种英文名称|语言代码|
|---|---|---|---|---|
|1|A|阿布哈兹语|Abkhazian|ab|
|2||阿尔巴尼亚语|Albanian|sq|
|3||阿肯语|Akan|ak|
|4||阿拉伯语|Arabic|ar|
|5||阿拉贡语|A||

- 22 - 

|5|阿拉贡语|Aragonese|an|
|---|---|---|---|
|6|阿姆哈拉语|Amharic|am|
|7|阿萨姆语|Assamese|as|
|8|阿塞拜疆语|Azerbaijani|az|
|9|阿斯图里亚斯语|Asturian|ast|
|10|阿兹特克语|Central Huasteca Nahuatl|nch|
|11|埃维语|Ewe|ee|
|12|艾马拉语|Aymara|ay|
|13|爱尔兰语|Irish|ga|
|14|爱沙尼亚语|Estonian|et|
|15|奥杰布瓦语|Ojibwa|oj|
|16|奥克语|Occitan|oc|
|17|奥里亚语|Oriya|or|
|18|奥罗莫语|Oromo|om|
|19|奥塞梯语|Ossetian|os|
|20 B|巴布亚皮钦语|Tok Pisin|tpi|
|21|巴什基尔语|Bashkir|ba|
|22|巴斯克语|Basque|eu|
|23|白俄罗斯语|Belarusian|be|
|24|柏柏尔语|Berber languages|ber|
|25|班巴拉语|Bambara|bm|
|26|邦阿西楠语|Pangasinan|pag|
|27|保加利亚语|Bulgarian|bg|
|28|北萨米语|Northern Sami|se|
|29|本巴语|Bemba (Zambia)|bem|
|30|比林语|Blin|byn|
|31|比斯拉马语|Bislama|bi|
|32|俾路支语|Baluchi|bal|
|33|冰岛语|Icelandic|is|

- 23 - 

|33|冰岛语|Icelandic|is|
|---|---|---|---|
|34|波兰语|Polish|pl|
|35|波斯尼亚语|Bosnian|bs|
|36|波斯语|Persian|fa|
|37|博杰普尔语|Bhojpuri|bho|
|38|布列塔尼语|Breton|br|
|39 C|查莫罗语|Chamorro|ch|
|40|查瓦卡诺语|Chavacano|cbk|
|41|楚瓦什语|Chuvash|cv|
|42|聪加语|Tsonga|ts|
|43 D|鞑靼语|Tatar|tt|
|44|丹麦语|Danish|da|
|45|掸语|Shan|shn|
|46|德顿语|Tetum|tet|
|47|德语|German|de|
|48|低地德语|Low German|nds|
|49|低地苏格兰语|Scots|sco|
|50|迪维西语|Dhivehi|dv|
|51|侗语|Kam|kdx|
|52|杜順語|Kadazan Dusun|dtp|
|53 E|俄语|Russian|ru|
|54 F|法罗语|Faroese|fo|
|55|法语|French|fr|
|56|梵语|Sanskrit|sa|
|57|菲律宾语|Filipino|fl|
|58|斐济语|Fijian|fj|
|59|芬兰语|Finnish|f|
|60|弗留利语|Friulian|fur|
|61|富尔语|Fur|fvr|

- 24 - 

|61|富尔语|Fur|fvr|
|---|---|---|---|
|62 G|刚果语|Kongo|kg|
|63|高棉语|Khmer|km|
|64|格雷罗纳瓦特尔语|Guerrero Nahuatl|ngu|
|65|格陵兰语|Kalaallisut|kl|
|66|格鲁吉亚语|Georgian|ka|
|67|格罗宁根方言|Gronings|gos|
|68|古吉拉特语|Gujarati|gu|
|69|瓜拉尼语|Guarani|gn|
|70 H|哈萨克语|Kazakh|kk|
|71|海地克里奥尔语|Haitian|ht|
|72|韩语|Korean|ko|
|73|豪萨语|Hausa|ha|
|74|荷兰语|Dutch|nl|
|75|黑山语|Montenegrin|cnr|
|76|胡帕语|Hupa|hup|
|77 J|基里巴斯语|Gilbertese|gil|
|78|基隆迪语|Rundi|rn|
|79|基切语|K'iche'|quc|
|80|吉尔吉斯斯坦语|Kirghiz|ky|
|81|加利西亚语|Galician|gl|
|82|加泰罗尼亚语|Catalan|ca|
|83|捷克语|Czech|cs|
|84 K|卡拜尔语|Kabyle|kab|
|85|卡纳达语|Kannada|kn|
|86|卡努里语|Kanuri|kr|
|87|卡舒比语|Kashubian|csb|
|88|卡西语|Khasi|kha|
|89|康沃尔语|Cornish|kw|

- 25 - 

|89|康沃尔语|Cornish|kw|
|---|---|---|---|
|90|科萨语|Xhosa|xh|
|91|科西嘉语|Corsican|co|
|92|克里克语|Creek|mus|
|93|克里米亚鞑靼语|Crimean Tatar|crh|
|94|克林贡语|Klingon|tlh|
|95|克罗地亚语|Serbo-Croatian|hbs|
|96|克丘亚语|Quechua|qu|
|97|克什米尔语|Kashmiri|ks|
|98|库尔德语|Kurdish|ku|
|99 L|拉丁语|Latin|la|
|100|拉特加莱语|Latgalian|ltg|
|101|拉脱维亚语|Latvian|lv|
|102|老挝语|Lao|lo|
|103|立陶宛语|Lithuanian|lt|
|104|林堡语|Limburgish|li|
|105|林加拉语|Lingala|ln|
|106|卢干达语|Ganda|lg|
|107|卢森堡语|Letzeburgesch|lb|
|108|卢森尼亚语|Rusyn|rue|
|109|卢旺达语|Kinyarwanda|rw|
|110|罗马尼亚语|Romanian|ro|
|111|罗曼什语|Romansh|rm|
|112|罗姆语|Romany|rom|
|113|逻辑语|Lojban|jbo|
|114 M|马达加斯加语|Malagasy|mg|
|115|马恩语|Manx|gv|
|116|马耳他语|Maltese|mt|
|117|马拉地语|Marathi|mr|

- 26 - 

|117|马拉地语|Marathi|mr|
|---|---|---|---|
|118|马拉雅拉姆语|Malayalam|ml|
|119|马来语|Malay|ms|
|120|马里语(俄罗斯)|Mari (Russia)|chm|
|121|马其顿语|Macedonian|mk|
|122|马绍尔语|Marshallese|mh|
|123|玛雅语|Kekchí|kek|
|124|迈蒂利语|Maithili|mai|
|125|毛里求斯克里奥尔语|Morisyen|mfe|
|126|毛利语|Maori|mi|
|127|蒙古语|Mongolian|mn|
|128|孟加拉语|Bengali|bn|
|129|缅甸语|Burmese|my|
|130|苗语|Hmong|hmn|
|131|姆班杜语|Umbundu|umb|
|132 N|纳瓦霍语|Navajo|nv|
|133|南非语|Afrikaans|af|
|134|尼泊尔语|Nepali|ne|
|135|纽埃语|Niuean|niu|
|136|挪威语|Norwegian|no|
|137 P|帕姆语|Pam|pmn|
|138|帕皮阿门托语|Papiamento|pap|
|139|旁遮普语|Panjabi|pa|
|140|葡萄牙语|Portuguese|pt|
|141|普什图语|Pushto|ps|
|142 Q|齐切瓦语|Nyanja|ny|
|143|契维语|Twi|tw|
|144|切罗基语|Cherokee|chr|
|145 R|日语|Japanese|ja|

- 27 - 

|5|日语|Japa ese|ja|
|---|---|---|---|
|146|瑞典语|Swedish|sv|
|147 S|萨摩亚语|Samoan|sm|
|148|桑戈语|Sango|sg|
|149|僧伽罗语|Sinhala|si|
|150|上索布语|Upper Sorbian|hsb|
|151|世界语|Esperanto|eo|
|152|斯洛文尼亚语|Slovenian|sl|
|153|斯瓦希里语|Swahili|sw|
|154|索马里语|Somali|so|
|155|斯洛伐克语|Slovak|sk|
|156 T|他加禄语|Tagalog|tl|
|157|塔吉克语|Tajik|tg|
|158|塔希提语|Tahitian|ty|
|159|泰卢固语|Telugu|te|
|160|泰米尔语|Tamil|ta|
|161|泰语|Thai|th|
|162|汤加语(汤加群岛)|Tonga (Tonga Islands)|to|
|163|汤加语(赞比亚)|Tonga (Zambia)|toi|
|164|提格雷尼亚语|Tigrinya|ti|
|165|图瓦卢语|Tuvalu|tvl|
|166|图瓦语|Tuvinian|tyv|
|167|土耳其语|Turkish|tr|
|168|土库曼语|Turkmen|tk|
|169 W|瓦隆语|Walloon|wa|
|170|瓦瑞语(菲律宾)|Waray (Philippines)|war|
|171|威尔士语|Welsh|cy|
|172|文达语|Venda|ve|
|173|沃拉普克语|Volapük|vo|

- 28 - 

|174|沃拉普 沃洛夫语|p Wolof|wo|
|---|---|---|---|
|175|乌德穆尔特语|Udmurt|udm|
|176|乌尔都语|Urdu|ur|
|177|乌孜别克语|Uzbek|uz|
|178 X|西班牙语|Spanish|es|
|179|西方国际语|Interlingue|ie|
|180|西弗里斯兰语|Western Frisian|fy|
|181|西里西亚语|Silesian|szl|
|182|希伯来语|Hebrew|he|
|183|希利盖农语|Hiligaynon|hil|
|184|夏威夷语|Hawaiian|haw|
|185|现代希腊语|Modern Greek|el|
|186|新共同语言|Lingua Franca Nova|lfn|
|187|信德语|Sindhi|sd|
|188|匈牙利语|Hungarian|hu|
|189|修纳语|Shona|sn|
|190|宿务语|Cebuano|ceb|
|191|叙利亚语|Syriac|syr|
|192|巽他语|Sundanese|su|
|193 Y|亚美尼亚语|Armenian|hy|
|194|亚齐语|Achinese|ace|
|195|伊班语|Iban|iba|
|196|伊博语|Igbo|ig|
|197|伊多语|Ido|io|
|198|伊洛卡诺语|Iloko|ilo|
|199|伊努克提图特语|Inuktitut|iu|
|200|意大利语|Italian|it|
|201|意第绪语|Yiddish|yi|

- 29 - 

|202|因特语|Interlingua|ia|
|---|---|---|---|
|203|印地语|Hindi|hi|
|204|印度尼西亚语|Indonesia|id|
|205|印古什语|Ingush|inh|
|206|英语|English|en|
|207|约鲁巴语|Yoruba|yo|
|208|越南语|Vietnamese|vi|
|209 Z|扎扎其语|Zaza|zza|
|210|爪哇语|Javanese|jv|
|211|中文|Chinese|zh|
|212|中文繁体|Traditional Chinese|zh-tw|
|213|中文粤语|Cantonese|yue|
|214|祖鲁语|Zulu|zu|

###### **AI 智能总结** 

AI 智能总结是在 AI 智能流式语音识别功能基础上增加的智能总结功能。该功能能够自动分析通话内容,生成通话摘要、章节 摘要、待办事项、话题提取等多种形式的总结内容,帮助用户快速回顾通话要点。 

##### **全场景适用** 

- **音视频通话** :自动生成通话纪要,记录通话要点、决策事项和待办任务,提升通话效率。 

- **在线培训** :生成培训内容摘要和知识点总结,帮助学员快速回顾重点内容。 **客户沟通** :记录客户需求、沟通要点和后续跟进事项,确保信息不遗漏。 

##### **前置条件** 

AI 智能总结是融云 RTC SDK 的高级功能。使用前需要满足以下条件: 

##### **服务开通** 

请提交工单开通。 

##### **功能依赖** 

- 30 - 

注意 

AI 智能总结是基于 AI 智能流式语音识别开发的功能。使用该功能需要: 

1. 先集成 AI 智能流式语音识别 功能 

2. 在初始化 CallKit 时开启语音识别功能(具体配置方法请参考 AI 智能流式语音识别 文档) 

##### **使用方式** 

##### **通话进行中** 

1. 在通话界面右上角找到 **AI 总结** 按钮(或总结图标) 

2. 点击进入 AI 总结页面,您可以: 

   - 点击 **开启总结** 按钮启用 AI 智能总结功能 

   - 点击 **切换语言** 按钮切换总结的语言(支持中文和英文) 

   - 点击 **刷新总结** 按钮获取最新的总结内容 

##### **通话结束后** 

1. 在会话列表中找到对应的会话,会显示 **AI 总结完成** 的消息气泡 

2. 点击消息气泡进入 AI 总结界面 

3. 在总结界面中,您可以: 

   - 查看完整的通话纪要内容 

   - 点击 **切换语言** 按钮切换总结的语言 

   - 点击 **刷新总结** 按钮重新生成总结内容 

##### **总结内容说明** 

CallKit 支持智能总结功能,可以在通话结束后自动生成通话纪要,包括: 

- **通话摘要** :对整个通话的高度概括 

- **章节摘要** :按时间线或话题划分的通话段落总结 

- **待办事项** :自动识别通话中达成的共识和分配的任务 

- **话题提取** :自动提取通话中的关键话题 

#### **推送管理** 

###### 提示 

鸿蒙的推送已经整合到鸿蒙系统中,在正确的获取到推送 token 前的所有步骤,您都需在鸿蒙平台操作。如有疑问, 可在鸿蒙平台提工单咨询。 

- 31 - 

###### **鸿蒙管理后台配置推送** 

客户端配置推送,需要先确保鸿蒙后台推送配置和融云后台推送配置已完成。 您也可参考鸿蒙的推送服务文档。 

###### **APP 申请通知权限** 

App 申请通知权限,可以在 **手机** > **设置** > **应用和服务** > **应用管理** 中查看 APP 的通知权限。 如果没有申请通知权限,收到的推 送无法在通知栏出现。 

详情请参考鸿蒙的请求通知授权文档。 

###### **APP 获取推送 token** 

鸿蒙系统已经内置获取推送 token 的逻辑,不需要像 Android 平台一样依赖各个手机厂商的推送 SDK 

获取推送 token 失败时,请根据错误码对照鸿蒙ArkTS API 错误进行排查。如果您不确定具体的错误,可以向鸿蒙提工单咨 询具体的报错信息。 

参考:获取鸿蒙推送 token 

###### **TypeScript** 

// 在 EntryAbility.ets 中 

onCreate(want: Want, launchParam: AbilityConstant.LaunchParam): void { 

hilog.info(0x0000, 'IM-ArkTS', 'Get message data successfully: %{public}s', 

JSON.stringify(want.parameters)); 

hilog.info(0x0000, 'IM-ArkTS', '%{public}s', 'Ability onCreate'); 

pushService.getToken((error: BusinessError, token: string) => { 

hilog.info(0x0000, 'IM-ArkTS', 'getPushToken error:%{public}s token:%{public}s', error, token); if (token) { 

- // 设置推送 token 

- IMEngine.getInstance().setPushToken(token); 

- } else { 

- // 获取推送 token 错误,根据 code 值请向鸿蒙提工单咨询具体原因 let code = error.code; 

} }); } 

###### **IMLib 设置推送 token** 

- 32 - 

在正常获取推送 token 后,把推送 token 设置给 IMLib 

##### **接口原型** 

###### **TypeScript** 

// 见 IMEngine.ts 

/** 

* 设置鸿蒙推送 token * ``` 

- 1. SDK 初始化之前设置:SDK 会将推送 token 缓存,连接成功后上报 

- 2. SDK 初始化之后连接之前设置:连接成功后上报 

- 3. SDK 连接成功后设置:SDK 立即上报 

* ``` 

* @param pushToken 推送 token */ public setPushToken(pushToken: string): void 

##### **示例代码** 

###### **TypeScript** 

// 设置推送 token IMEngine.getInstance().setPushToken(token); 

###### **点击推送唤起 APP** 

###### 获取推送数据 

参考鸿蒙文档: https://developer.huawei.com/consumer/cn/doc/harmonyos-guides-V5/push-send-alertV5#section1792616175914 

###### **TypeScript** 

- 33 - 

###### // 鸿蒙推送示例内容 

{ 

"_push_notifyid": 1590297100, "component.startup.newRules": true, "debugApp": false, "isCallBySCB": false, "moduleName": "entry", "ohos.aafwk.param.callerAbilityName": "PushServiceInnerAbility", "ohos.aafwk.param.callerBundleName": "com.huawei.hms.pushservice", "ohos.aafwk.param.callerPid": 39626, "ohos.aafwk.param.callerToken": 537231324, "ohos.aafwk.param.callerUid": 20004, "ohos.ability.launch.reason": 1, "ohos.dlp.params.sandbox": false, "rc": " 

{\"conversationType\":\"1\",\"targetId\":\"1234\",\"sourceType\":\"0\",\"fromUserId\":\"1234\",\"voip\":\"0\",\"obj 8NO9-O305-DBM8\",\"bId\":\"\",\"tId\":\"0987\"}", 

"send_to_erms_targetAppDistType": "none", "send_to_erms_targetAppProvisionType": "debug", "send_to_erms_targetBundleType": 0 } 

###### 此处为鸿蒙推送从 want.parameters 中获取到的数据, **rc** 中的字段描述如下 

- conversationType : 会话类型 

- targetId : 会话 id 

- fromUserId : 发送方 id 

- objectName : 消息类型 

- msgTime : 消息发送时间 

- id : 消息 uid 

###### **管理通知角标** 

参考鸿蒙文档:https://developer.huawei.com/consumer/cn/doc/harmonyos-guides-V5/notification-badge-V5 

#### **CallKit 客户端 API** 

以下是 HarmonyOS CallKit 的 API 参考文档: 

CallKit 音视频通话(含 UI) 

- 34 - 

#### **版本说明** 

版本说明按时间顺序列出了 Callkit 的所有新功能、变更、和已修复的问题。格式基于 Keep a Changelog。 

变动类型: 

- **新增** ( Added ):新添加的功能。 

- **变更** ( Changed ):对现有功能的变更。 

- **废弃** ( Deprecated ):已经不建议使用,即将移除的功能。 

- **移除** ( Removed ):已经移除的功能。 

- **修复** ( Fixed ):对 bug 的修复。 

- **安全改进** ( Security ):对安全性的改进。 

###### **26.1.0 - 2026-2-3** 

##### **新增** 

- 新增了 AI 智能总结展示页面。 

- 新增了 AI 智能总结消息气泡。 

###### **25.12.0 - 2025-12-31** 

##### **新增** 

- 适配鸿蒙 PC:增加针对 PC 平台的新 UI,支持使用外接摄像头用于视频通话。 

- 优化在三折叠手机上的 UI 表现。 

###### **25.11.0 - 2025-11-28** 

重要说明 

为更好的对 HarmonyOS SDK 进行版本管理,从此版本开始原版本号的第一位 1 改为年份 25,后面二、三位版本号 规则保持不变。 

更新后版本号第一位为年份、第二位为功能迭代版本号、第三位为补丁修复 hotfix 版本号。 

**修复** 

- 35 - 

修复了单人视频呼叫页面显示逻辑问题:接通前应显示自己的名字,接通后显示对端用户名字。 

###### **1.10.0 - 2025-10-31** 

##### **新增** 

新增语音识别、实时翻译功能。 

##### **修复** 

- 修复了视频通话默认音频输出设备未使用扬声器的问题。 

- 修复了音频通话呼叫时,设置音频为扬声器输出,通话建立后未生效的问题。 

###### **1.9.0 - 2025-09-26** 

##### **新增** 

RCCall 中新增 install 方法,用于提前加载模块。 

###### **1.8.0 - 2025-08-29** 

##### **新增** 

国际化中新增了英文。 

- 接口 RCCallListener 中新增了 didMultiCallNavMarginTop 和 didMultiCallNavMarginBottom 方法,用于用户自 定义设置群组选人页面的上边距和下边距。 

##### **修复** 

修复了群组视频通话接通后开关摄像头的按钮状态不正确的问题。 

###### **1.7.0 - 2025-07-24** 

##### **新增** 

适配了双折叠屏、平板的 UI。 

- 36 - 

适配了双折叠屏闭合状态切换时前置摄像头的切换逻辑,确保一直使用正确的前置摄像头。 

支持了读取 IMKit 的会话列表头像圆角控制的配置(矩形/圆形),来决定 Callkit 各个页面的头像形状。 

##### **修复** 

UI 和图标样式跟 Android Callkit 对齐。 

###### **1.6.0 - 2025-06-27** 

##### **新增** 

首次发布 Callkit SDK,提供 1v1、群组、选人页面。 

#### **状态码** 

RCCallErrorCode 状态码包含如下内容: 

0 SUCCESS 成功。 1 FAILED 失败 **排查建议** :接口调用失败。 2 ONE_CALL_EXISTED 已经处于通话中了 

**排查建议** :当前正在通话中,例如重复发起通话时会出现此错误码。 

3 NOT_IN_CALL 不在通话中 

**排查建议** :有些接口调用限制在通话中状态,例如非通话状态切换媒体类型。 

4 OPERATION_UNAVAILABL 

E 

- 37 - 

无效操作 

**排查建议** :该返回表示非法调用,或者是多余调用。 

5 

INVALID_PARAM 参数错误 

**排查建议** :请检查当前接口的入参是否符合该接口要求 

#### **合规指南** 

#### **实时音视频** CallKit SDK **合规使用说明** 

根据中国法律法规和监管部门规章要求,App 开发运营者(以下简称"开发者"或"您")在提供网络产品服务时应尊重和保护最 终用户个人信息,不得违法违规收集使用个人信息,保证和承诺个人信息处理行为获得最终用户的授权同意,遵循最小必要原 则,并且应当采取有效的技术措施和组织措施,确保个人信息安全。 

为帮助开发者在使用 SDK 的过程中更好地落实用户个人信息保护相关要求,避免出现侵害用户个人信息权益情形,北京云中 融信网络科技股份有限公司(以下简称"我们")特制定本 SDK 合规使用说明文档(以下简称"文档")。 

###### **一、 App 个人信息保护的合规要求** 

为保护 App 最终用户的个人信息,App 及 App 的开发者需要满足如下合规要求: 

- App 开发者应该制定隐私政策,并在 App 界面中显著展示。 

- App 隐私政策应该单独成文,而不是作为用户协议等文件中的一部分进行展示。 

- App 隐私政策应该明示收集和使用个人信息的目的、方式和范围,并且确保隐私政策链接正常有效,易于访问和阅读。 

- App 隐私政策应逐项说明 App 各项业务功能以及对应收集的个人信息类型,不应使用"等、例如"等方式概括说明。 

- App 隐私政策应显著标识个人敏感信息类型(如:字体加粗等)。 

- App 隐私政策应逐项说明调用的第三方 SDK,包括明示 SDK 名称、SDK 开发者名称;SDK 收集和处理的个人信息类 型、目的、方式、范围;SDK 隐私政策链接。 

###### **二、 App 使用** CallKit SDK **时的合规指引** 

##### **1. SDK 所需的系统权限的说明** 

CallKit SDK 功能所需的权限,您可以参考如下表格,了解相关权限功能和时机。SDK 只会检查 App 是否获得相应授权,不 会主动向最终用户申请权限。 

- 38 - 

权限配置,请查阅 实现音视频通话 。 

##### **HarmonyOS 操作系统 SDK 功能、接口配置方式及示例说明:** 

|系统|业 务 功 能|相关个人信息|功能|
|---|---|---|---|
|HarmonyOS|登 录|IP地址、网络接入方式和类型、App Key下的用户ID、用户Token|用户登 录连接|
||连||时|
||接|||
|HarmonyOS|推|应用包名|使用推|
||送||送功能|
||功||时|
||能|||
|HarmonyOS|故 障 排|设备品牌、设备型号、操作系统版本、内存使用情况、App的AppKey、融云SDK版本号、 接口调用的错误码、链接失败的错误码、App版本号、时区、语言、运营商代码MNO(可 选)|故障排 查时|
||查|||

配置方式及示例: 

###### **TypeScript** 

// 连接 IM 

IMEngine.getInstance().connect(token, 20).then(result => { 

if (EngineError.Success === result.code) { 

// 连接成功 

let userId = result.userId; 

return 

- } 

if (EngineError.ConnectTokenExpired === result.code) { 

- // Token 过期,从 APP 服务请求新 token,获取到新 token 后重新 connect() 

- } else if (EngineError.ConnectionTimeout === result.code) { 

- // 连接超时,弹出提示,可以引导用户等待网络正常的时候再次点击进行连接 

- } else { 

- //其它业务错误码,请根据相应的错误码作出对应处理。 

- } 

}); 

##### **2. SDK 初始化及业务功能调用时机说明** 

您应确保在登录注册页面及 App 首次运行时,通过简洁、明显且易于访问方式向最终用户告知涵盖个人信息处理主体、处理 

- 39 - 

目的、处理方式、处理类型、保存期限等内容的 App 个人信息处理规则(App 隐私政策)。 

您应确保在最终用户同意 App 隐私政策后,再进行 SDK 的初始化。并且,在用户同意隐私政策前,您应避免动态申请涉及用 户个人信息的敏感设备权限;也应避免私自采集和上报个人信息。如果最终用户不同意 App 隐私政策,则不能初始化 SDK, 无法使用 SDK 功能。 

SDK 初始化和相关功能配置,请查阅 HarmonyOS CallKit SDK 实现音视频通话 。 

##### **3. SDK 隐私政策披露要求与示例说明** 

请您根据集成 CallKit SDK 的实际情况,在您的 App 隐私政策中披露:第三方 SDK 名称、SDK 公司名称、SDK 使用目的和 功能场景、SDK 涉及个人信息类型、实现 SDK 功能所需的权限、SDK 隐私政策链接。 

请在您的 App 隐私政策中,以文字或列表的方式向公众披露第三方SDK的相关信息。 

第三方 SDK 披露示例(仅供参考): 

###### **HarmonyOS 示例** 

SDK 名称:HarmonyOS CallKit SDK 

- SDK 公司名称:北京云中融信网络科技股份有限公司 

- SDK 使用目的和功能场景:提供音视频服务功能和服务 

- SDK 涉及的个人信息类型:设备品牌、设备型号、操作系统版本、内存使用情况、IP地址、网络接入方式和类型、App Key 下的用户 ID、应用包名、时区、语言、App 版本号、App 的 AppKey、用户 Token、融云 SDK 版本号、运营商代 码 MNO(可选)、接口调用的错误码、链接失败的错误码 

- 实现 SDK 功能所需权限:麦克风权限(ohos.permission.MICROPHONE,必要)、相机权限 

- (ohos.permission.CAMERA,必要)、网络相关权限(ohos.permission.GET_NETWORK_INFO、 ohos.permission.INTERNET,必要) 

SDK 隐私政策链接:https://docs.rongcloud.cn/guides/privacy 

##### **4. 最终用户同意方式的建议方式说明及示例** 

App 首次运行时应当有隐私弹窗,隐私弹窗中应公示隐私政策内容并附完整隐私政策链接,并明确提示最终用户阅读并选择是 否同意隐私政策; 隐私弹窗应提供同意按钮和拒绝同意的按钮,并由最终用户主动选择。 App 取得敏感权限前,应通过隐私 弹窗获得用户单独授权同意。 

隐私政策授权和敏感个人信息授权弹窗示例: 

- 40 - 

- 41 - 

图 1:敏感个人信息授权弹窗示例 

- 42 - 

图 2:隐私政策授权弹窗示例 

- 43 - 

##### **5. 最终用户行使权利的配置说明** 

开发者在其 App 中集成 SDK 后,SDK 的正常运行会收集和处理必要的最终用户的个人信息用于提供音视频服务。 

SDK 提供以下接口配置,以便您帮助最终用户实现其个人信息权利的请求。在最终用户撤销同意处理其个人信息的授权时, 您可以通过调用接口,停止和关闭 SDK 功能,并停止收集相应的用户数据。 

App 开发者应根据相关法律法规为最终用户提供行使个人信息主体权利的路径功能,需要 SDK 配合的,请与 SDK 及时进行 联系。 

###### **三、合规文件指引** 

1. 《个人信息保护法》 

2. 《工业和信息化部关于开展信息通信服务感知提升行动的通知》 

3. 《工业和信息化部关于开展纵深推进 App 侵害用户权益专项整治行动的通知》 

4. 《工业和信息化部关于开展 App 侵害用户权益专项整治工作的通知》 

5. 《App 违法违规收集使用个人信息行为认定方法》 

6. 《App 违法违规收集使用个人信息自评估指南》 

7. 《常见类型移动互联网应用程序必要个人信息范围规定》 

8. 《GB/T 35273-2020信息安全技术个人信息安全规范》 

9. 《网络安全标准实践指南—移动互联网应用程序(App)使用软件开发工具包(SDK)安全指引》 

###### **四、联系方式** 

我们设立了专门的个人信息保护团队和负责人,如果您和/或最终用户对本规则或个人信息保护相关事宜有疑问或投诉、建议 时,可以通过提交工单与我们联系: 

我们将尽快审核所涉问题,并在 15 个工作日或法律法规规定的期限内予以反馈。 

- 44 -
