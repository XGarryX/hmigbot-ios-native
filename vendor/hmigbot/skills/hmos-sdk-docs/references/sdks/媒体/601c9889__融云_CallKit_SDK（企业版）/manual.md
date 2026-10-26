# 鸿蒙 CallKit 接入文档

# 导入 CallKit SDK

融云支持使用 DevEco Studio 中自动导入和手动导入两种方式,将 CallKit SDK 导入到您的应用工程

中。

## 环境要求

-
DevEco Studio NEXT Release(5.0.3.900) 及以上。

-
HarmonyOS SDK API 12 及以上。

-
手机系统版本号:NEXT.0.0.31

## 自动导入 SDK 

CallKit 1.6.0 版本开始支持OpenHarmony三方库中获取 SDK

1.在当前项目目录(示例 entry)中的oh-package.json5中添加 SDK 依赖,然后点击

```
"Sync Now"。
``````
// entry 目录中的 oh-package.json5
{
"name": "entry",
"version": "1.0.0",
"description": "Please describe the basic information.",
"main": "",
"author": "",
"license": "",
"dependencies": {
"@rongcloud/callkit": "x.y.z",
"@rongcloud/calllib": "x.y.z",
"@rongcloud/imlib": "x.y.z",
"@rongcloud/imkit": "x.y.z",
  }
}
```

## ❗注意

各个 SDK 的最新版本号可能不相同,具体 x.y.z 值可前往融云官网 SDK 下载页面或

OpenHarmony三方库中心查询。

1. 安装 SDK 成功后,您可以在项目根目录的oh_modules/.ohpm/中找到融云 CallKit SDK。

2.查看更多其他融云 SDK。

打开OpenHarmony三方库中心,搜索关键字rongcloud

## 手动导入 SDK 

1.在导入 SDK 前,您需要前往融云官网 SDK 下载页面,将音视频通话(包含 UI)SDK 下载到本地。

2. 创建./libs文件夹,将所需 SDK har 包 `CallKit.har`、`CallLib.har`、`RongIMLib.har`、

`RongIMKit.har`、`RTCLib.har` 放入其中。

## 执行命令行

1.在工程根路径下执行以下命令行:
```
1
ohpm install libs/CallKit.har
```

2.执行完后,Studio 根据工程路径在oh-package.json5自动添加依赖。

## entry  配置文件依赖 SDK

在entry同级目录的 `oh-package.json5` 手动配置 SDK 依赖。
```
// entry 同级目录下的 oh-package.json5 需要手动配置
{
"name": "xxx",
"version": "1.0.0",
"description": "Please describe the basic information.",
"main": "",
"author": "",
"license": "",
"dependencies": {
"@rongcloud/callkit": "file:../libs/CallKit.har",  // 该配置手动依赖
"@rongcloud/calllib": "file:../libs/CallLib.har",  // 该配置手动依赖
"@rongcloud/imlib": "file:../libs/RongIMLib.har",  // 该配置手动依赖
"@rongcloud/imkit": "file:../libs/RongIMKit.har",  // 该配置手动依赖
```

| 1 1 1 1 1 1 | 4 }, 5 "devDependencies": { 6 "@ohos/hypium": "1.0.16", 7 "@ohos/hamock": "1.0.0" 8 } 9 } |
|---|---|
| 同步项目 在 `entry/oh-package.json5` 中点击 Sync Now 同步工程,同步成功之后即可正常使用 CallKit SDK。 💡 提示 如果您同步之后依然无法导入 SDK,这可能是 DevEco Studio 的编译缓存导致的问题。您可 以尝试把 DevEco Studio 完全关闭之后重新打开项目工程来解决问题。 添加 SDK 依赖权限 SDK 需要权限如下: 权限名称 权限说明 使用目的 ohos.permission.GET NET 获取网络信息 网络变化之后获取网络信息, _ WORK INFO 进行 IM 重连 _ ohos.permission.INTERNET 使用网络 连接 IM 、收发消息需要网络 连接 ohos.permission.STORE PE 数据存储 消息数据库需要本地存储 _ RSISTENT DATA _ ohos.permission.MICROPH 麦克风权限 音频通话需要麦克风采集能力 ONE ohos.permission.CAMERA 摄像头权限 视频通话需要摄像头采集能力 ohos.permission.KEEP BAC 后台任务 后台保活用于音视频通话 _ KGROUND RUNNING _ ohos.permission.VIBRATE 响铃 来电提醒 ohos.permission.RUNNING 熄屏 音频通话时附耳熄屏 LOCK _ |  |

| 权限名称 | 权限说明 | 使用目的 |
|---|---|---|
| ohos.permission.GET NET _ WORK INFO _ | 获取网络信息 | 网络变化之后获取网络信息, 进行 IM 重连 |
| ohos.permission.INTERNET | 使用网络 | 连接 IM 、收发消息需要网络 连接 |
| ohos.permission.STORE PE _ RSISTENT DATA _ | 数据存储 | 消息数据库需要本地存储 |
| ohos.permission.MICROPH ONE | 麦克风权限 | 音频通话需要麦克风采集能力 |
| ohos.permission.CAMERA | 摄像头权限 | 视频通话需要摄像头采集能力 |
| ohos.permission.KEEP BAC _ KGROUND RUNNING _ | 后台任务 | 后台保活用于音视频通话 |
| ohos.permission.VIBRATE | 响铃 | 来电提醒 |
| ohos.permission.RUNNING LOCK _ | 熄屏 | 音频通话时附耳熄屏 |

```
1.找到项目entry/src/main/目录下的module.json5文件,添加
```

requestPermissions配置,以配置摄像头权限为例:
```
"requestPermissions": [
  {
"name": "ohos.permission.CAMERA",
"reason": "$string:Camera",
"usedScene": {
"abilities": [
"EntryAbility",
      ],
"when": "always"
    }
  },
   ... // 配置其他权限
]
```

具体权限配置参数含义,请参考鸿蒙的应用权限管控文档。

2. 配置权限时,按照规则需要考虑国际化问题。在项目 `entry/src/main/resources/base/element`

目录下找到 `string.json` 文件,对应增加配置字符变量,以配置摄像头字符变量为例:
```
{
    "string": [
        {
            "name": "Camera",
            "value": "Camera in RTC"
        },
        ... // 定义其他
    ]
}
```

# 实现音视频通话

CallKit 基于 CallLib SDK 基础增加了一套默认呼叫界面,包含了单人、多人音视频呼叫的各种场景和

功能。

## 💡房间人数上限

1.考虑移动设备的带宽(主要是在多路视频情况下)和 UI 交互效果,建议单次通话或房间

内,视频不超过 16 人,纯音频不超过 32 人。超过此上限可能影响通话效果。

2.CallKit 代码中已设置人数上限。默认发起视频呼叫时,最多可选 7 人。发起音频呼叫

时,最多可选 20 人。如需调整,建议不超过默认上限。

## 前置条件

-
创建融云开发者账号,获取App Key。注册成功后,融云控制台会默认自动创建您的首个应用,默

认生成开发环境下的 App Key,使用国内数据中心。注意:同一个应用的开发环境与生产环境提供

不同的 App Key,两个环境之间数据隔离。

-
开通音视频通话服务。

## 快速上手

## 步骤 1 导入 SDK

导入融云音视频通话能力 UI 库 CallKit,具体步骤请参阅导入 CallKit SDK

## 步骤 2 初始化

RTC 音视频能力是基于 IM 作为信令通道的,CallKit 又依赖于 IMKit & CallLib,所以要先初始化 IM。

如果不换 AppKey,在整个应用生命周期中,初始化一次即可。建议调用位置放在应用启动位置处,或

在音视频功能模块的加载位置处。在 UIAbility 的onCreate()方法中,调用初始化方法,传入生产

或开发环境的 App Key。
```
// 在 UIAbility 中获取 context
let context = this.context
let initOption = newInitOption();
let appKey = "从融云后台获取的 appKey";
IMEngine.getInstance().init(context, appKey, initOption);
```

## 步骤 3 连接 IM 服务

音视频用户之间的信令传输依赖于融云的即时通信(IM)服务,因此需要先调用connect与 IM 服

务建立好 TCP 长连接。建议在功能模块的加载位置处调用,之后再进行音视频呼叫业务。当模块退出

后调用disconnect或logout断开该连接。
```
// 连接 IM
IMEngine.getInstance().connect(token, 20).then(result => {
if (EngineError.Success === result.code) {
// 连接成功
let userId = result.userId;
return
    }
if (EngineError.ConnectTokenExpired === result.code) {
// Token 过期,从 APP 服务请求新 token,获取到新 token 后重新 connect()
    } elseif (EngineError.ConnectionTimeout === result.code) {
// 连接超时,弹出提示,可以引导用户等待网络正常的时候再次点击进行连接
    } else {
//其它业务错误码,请根据相应的错误码作出对应处理。
    }
});
```

## 步骤 4 实现监听

在通话前需要设置RCCall的RCCallListener监听,在 CallKit 页面跳转时提供必要的 UI 组件。
```
RCCall.getInstance().callListener = {
/**
     * 获取当前 Ability 页面对应的 WindowStage 实例。
     * 
     * 说明:
     * - 在 Ability 的生命周期方法 `onWindowStageCreate` 中,首次创建并缓存
`windowStage`。
     * - 通过 `didWindowStage` 方法获取缓存的 `windowStage`,方便在其他逻辑中调用。
     * 
     * 示例:
     * ```ts
     * onWindowStageCreate(windowStage: window.WindowStage): void {
     *   // 主窗口创建完成,缓存 windowStage 以便后续使用
     *   AppStorage.setOrCreate('windowStage', windowStage);
     * }
     * ```
     * 
     * @return s当前 Ability 缓存的 WindowStage 实例
     */
```

| 1 2 2 2 2 2 2 2 2 2 2 3 3 3 3 3 3 3 3 3 3 4 4 4 4 4 4 4 4 4 4 5 5 5 5 5 5 5 5 5 5 6 6 6 6 6 | 9 didWindowStage: () => { 0 let windowStage = AppStorage.get('windowStage') as window.WindowStage 1 return windowStage 2 }, 3 /** 4 * 多人通话选人页面导航栈, 用于选人页面导航, 必须设置, 否则无法导航到选人页面 5 * ⚠ ️ 注意: 6 * 该方法必须返回当前页面中实际使用的 Navigation 容器绑定的 NavPathStack 对象。 7 *  8 * * 正确示例(页面中定义并绑定了 navStack): 9 *  0 * ```ts 1 * private navStack: NavPathStack = new NavPathStack(); 2 *  3 * Navigation({ stack: this.navStack }) { 4 * // 页面内容 5 * } 6 */ 7 didMultiCallNavPathStack: () => { 8 return this.navStack; // ✅ 返回实际绑定在 UI 上的导航栈 9 }, 0 /** 1 * 点击 CallKit 横幅或左上角胶囊后跳转回到的 Ability 页面名 2 * ⚠ ️ 注意: 3 * 此处的页面名须使用 module.json5 中 module -> abilities -> name 定义字义的字 符串 4 */ 5 didCallKitNavAbilityName: () => { 6 /// 该方法返回,所集成项目的 UIAbility 7 return 'CallKitEntryAbility' 8 }, 9 /** 0 * 是否允许选择某个用户 1 * 非必传,默认允许选择 2 * @param userId 用户 userId 3 */ 4 didUserSelectable: async (userId: string): Promise<boolean> => { 5 /** 6 * 根据条件判断是否允许选择该用户 7 * 不允许时返回 false 8 */ 9 return false; 0 }, 1 /** 2 * 按钮插件过滤 3 * 非必传,插件默认显示 4 * @param id 会话对象 |
|---|---|

| 6 6 6 6 6 7 7 7 7 7 | 5 * @param mediaType 媒体类型,音频或视频 6 * @returns boolean 7 */ 8 didPluginFilter: (id: ConversationIdentifier, mediaType: RCCallMediaType): boolean => { 9 // 如需过滤掉视频插件 0 if (mediaType === RCCallMediaType.VIDEO) { 1 return false; 2 }; 3 } 4 } |
|---|---|
| 步骤 5 呼叫方 通常 App 内呼叫和被叫方逻辑会同时存在,所以需要分别集成。 发起单人呼叫 代码块 1 /** 2 * 发起单聊呼叫 3 * @param targetId 被叫端Id 4 * @param mediaType 呼叫媒体类型 5 */ 6 public startSingleCall(targetId: string, mediaType: RCCallMediaType) 参数 类型 必填 说明 targetId string 是 对方的用户ID mediaType RCCallMediaType 是 媒体类型 • 示例代码: 代码块 1 // 使用时填写真实 id 2 let targetId = '被叫端UserId' 3 // 媒体类型 RCCallMediaType 4 let mediaType = RCCallMediaType.VIDEO  5 RCCall.getInstance().startSingleCall(targetId, mediaType) |  |

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| targetId | string | 是 | 对方的用户ID |
| mediaType | RCCallMediaType | 是 | 媒体类型 |

### 发起多人呼叫

1.调用startMultiCall会先弹出群组选择成员界面,所以发起多人呼叫前,需要优先实现 IMKit 的

UserDataProvider接口,来提供群组信息,群成员信息等数据来源。
```
RongIM.getInstance().userDataService().setUserDataProvider({        
/**
```

     * 获取群组信息数据,当需要展示群组头像、名称时,如果 SDK 没有对应的信息时触发该方法

```
     *```
```

     * 获取到群组信息后,SDK 会缓存该数据,并触发监听

```
6
```

     * SDK 缓存之后就会一直使用,不会自动更新。如果群组信息发生变化,需要调用

```
UserDataService.updateUserInfo 主动刷新 SDK 信息
     *```
     * @param groupId 群 id
```

     * @returns群组信息。注意:如果返回 undefined ,SDK则不会更新缓存。

```
     */
fetchUserInfo: (userId: string) => {
return newPromise<UserInfoModel | undefined>((resolve, reject) => {
// 调试代码
if (userId === 'test1') {
let userInfo = newUserInfoModel(userId, 'test1_name',
'https://xxx.png')
resolve(userInfo)
            }                           
        })
    },
/**
```

     * 获取群组成员信息数据,当需要展示群组成员头像、名称时,如果 SDK 没有对应的信息时触

发该方法

```
     *```
```

     * 获取到群组成员信息后,SDK 会缓存该数据,并触发监听

```
24
```

     * SDK 缓存之后就会一直使用,不会自动更新。如果群组成员信息发生变化,需要调用

```
UserDataService.updateGroupMemberInfo 主动刷新 SDK 信息
     *```
     * @param groupId 群 id
     * @param userId 用户 Id
```

     * @returns群组成员信息。注意:如果返回 undefined ,SDK则不会更新缓存。

```
     */
fetchGroupMemberInfo: (groupId: string, userId: string) => {
return newPromise<GroupMemberInfoModel | undefined>((resolve, reject)
=> {
// 调试代码
letmember: GroupMemberInfoModel = new
GroupMemberInfoModel(groupId, userId, '', '')
if (userId === 'test1') {
```

| 3 3 3 3 3 4 4 4 4 4 4 4 4 4 4 5 5 5 5 5 5 5 5 5 5 6 6 6 6 6 6 6 6 6 6 7 7 7 7 7 | 5 member = new GroupMemberInfoModel(groupId, userId, 'test1 name', _ 6 'https://xxx') 7 } 8 resolve(member) 9 }) 0 }, 1 /** 2 * 获取群成员信息数据列表,当需要展示群成员头像、名称时,如果 SDK 没有对应的信息时触 发该方法 3 *``` 4 * 获取到群组成员信息后,SDK 会缓存该数据,并触发监听 5 * SDK 缓存之后就会一直使用,不会自动更新。如果群组成员信息发生变化,需要调用 UserDataService.updateGroupMemberInfo 主动刷新 SDK 信息 6 *``` 7 * @param groupId 群 id 8 * @returns 群成员信息列表 9 */ 0 fetchGroupMemberInfos: (groupId: string) => { 1 return new Promise<Array<GroupMemberInfoModel> \| undefined>((resolve, reject) => { 2 /// 使用 app server 提供的群成员列表信息,以下是示例测试数据 3 let members: Array<GroupMemberInfoModel> = new Array<GroupMemberInfoModel>() 4 for (let i = 0; i < 5; i++) { 5 let member: GroupMemberInfoModel = new GroupMemberInfoModel('', '', '', '') 6 member.userId = `test${i + 1}` 7 members.push(member) 8 } 9 resolve(members)  0 }); 1 }, 2 /** 3 * 获取群组信息数据,当需要展示群组头像、名称时,如果 SDK 没有对应的信息时触发该方法 4 *``` 5 * 获取到群组信息后,SDK 会缓存该数据,并触发监听 6 * SDK 缓存之后就会一直使用,不会自动更新。如果群组信息发生变化,需要调用 UserDataService.updateGroupInfo 主动刷新 SDK 信息 7 *``` 8 * @param groupId 群 id 9 * @returns 群组信息。注意:如果返回 undefined ,SDK则不会更新缓存。 0 */ 1 fetchGroupInfo: (groupId: string) => { 2 return new Promise<GroupInfoModel \| undefined>((resolve, reject) => { 3 if (groupId === 'test group') { _ 4 let model = new GroupInfoModel('test group', '测试群', '', 3) _ |
|---|---|

| 7 7 7 7 7 8 8 8 | 5 resolve(model) 6 } 7 else { 8 resolve(undefined) 9 } 0 }) 1 } 2 }) |
|---|---|
| 1. 实现了步骤1 中的相关协议方法提供了群信息数据,调用 startMultiCall 会先弹出选择成员界面。 如下图所示,选择联系人点击 确认 后 CallKit 发起多人呼叫。 |  |
```
/**
```

  * 发起群聊呼叫

```
  * @param targetId 群组Id
  * @param mediaType 呼叫媒体类型
  */
public startMultiCall(targetId: string, mediaType: RCCallMediaType)
```

-
参数说明:

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| targetId | string | 是 | 群组ID |
| mediaType | RCCallMediaType | 是 | 媒体类型 |

-
示例代码:
```
// 多人呼叫时,需要填写 IM 群组id
let targetId = 'groupId'
// 媒体类型 RCCallMediaType
let mediaType = RCCallMediaType.VIDEO
RCCall.getInstance().startMultiCall(targetId, mediaType)
```

## 步骤 6 接听方

鸿蒙 CallKit 中已经默认实现了 CallLib 库提供RCCallClientListener监听回调。被叫端收到呼叫,会

自动弹出通话界面,点击来电页面的接听按钮即可接听通话。

当App在后台或者未启动时会收到来电通知,点击来电通知条App打开后会显示来电页面。
