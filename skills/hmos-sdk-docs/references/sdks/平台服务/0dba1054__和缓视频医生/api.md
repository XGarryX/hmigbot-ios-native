2025/11/10 12:11 

和缓视频医生HarmonyOS_SDK_API文档 

#### 和缓视频医生 HarmonyOS SDK API 文档 

#### 📋 目录 

1. 文档说明 1.1 概述 1.2 功能特性 1.3 技术要求 2. 快速开始 2.1 安装 SDK 2.2 配置权限 2.3 导入 SDK 2.4 基本使用流程 

3. API 接口详情 

3.1 初始化 SDK 

3.2 用户登录 

3.3 用户登出 3.4 直接呼叫视频医生 

3.5 进入信息流页面 

3.6 问诊详情页面 

   - 3.7 配置视频中邀请家人 

4. 数据模型 

4.1 HHSDKOptions 4.2 HHCallInfo 4.3 回调接口 5. 附录 5.1 完整示例代码 5.2 权限配置模板 

# 和缓视频医生 HarmonyOS SDK API 文档 

版本: v1.1.1 更新日期: 2025-11-10 文档类型: API 接口文档 

## 📋 目录 

1. 文档说明 

2. 快速开始 

3. API 接口详情 

4. 数据模型 

5. 附录 

file:///Users/iOS/Desktop/%E5%92%8C%E7%BC%93%E8%A7%86%E9%A2%91%E5%8C%BB%E7%94%9FHarmonyOS_SDK_API%E6%96%87%E6%A1%... 

2025/11/10 12:11 

和缓视频医生HarmonyOS_SDK_API文档 

## 1. 文档说明 

### 1.1 概述 

一 和缓视频医生 HarmonyOS SDK 是 款为 OpenHarmony 应用提供在线视频问诊服务的开发工具包。 通过集成本 SDK,开发者可以快速实现视频问诊、即时通讯、病历查看等医疗健康功能。 

### 1.2 功能特性 

- ✅ 视频问诊:实时音视频通话,支持医患远程交流 

- ✅ 智能分诊:自动分配医生,支持排队管理 

- ✅ 即时通讯:图文消息、语音消息、图片分享 

- ✅ 病历管理:查看历史问诊记录和病历详情 ✅ 家人邀请:支持视频中邀请家人参与问诊(v1.0.7+) 

### 1.3 技术要求 

#### 项目 

#### 要求 

系统版本 OpenHarmony 3.0+ 

开发语言 ArkTS / TypeScript 

网络要求 需要联网使用 

权限要求 摄像头、麦克风、网络、后台任务 

## 2. 快速开始 

### 2.1 安装 SDK 

通过 ohpm 包管理器安装: 

```
ohpm install @hh-medic/hhsdk
```

#### 参考官方文档:安装 OpenHarmony ohpm 包 

### 2.2 配置权限 

在 `module.json5` 配置文件中添加后台长时任务权限: 

```
{
"module":{
"abilities":[
{
"backgroundModes":[
"voip"
]
}
```

file:///Users/iOS/Desktop/%E5%92%8C%E7%BC%93%E8%A7%86%E9%A2%91%E5%8C%BB%E7%94%9FHarmonyOS_SDK_API%E6%96%87%E6%A1%... 

2025/11/10 12:11 

和缓视频医生HarmonyOS_SDK_API文档 

```
],
"requestPermissions":[
{
"name":"ohos.permission.INTERNET"
},
{
"name":"ohos.permission.CAMERA"
},
{
"name":"ohos.permission.MICROPHONE"
}
]
}
}
```

说明: `voip` 配置用于避免应用切换到后台时音视频通话异常中断。 

### 2.3 导入 SDK 

#### 在需要使用 SDK 的文件中导入: 

```
import { HHDoctor } from'@hh-medic/hhsdk';
```

### 2.4 基本使用流程 

_`// 1.`_ 初始化 _`SDK`_ **`let`** `options =` **`new`** `HHSDKOptions() options.sdkProductId = YOUR_PRODUCT_ID` _`//`_ 联系商务获取 `options.isDev =` **`false`** _`//`_ 生产环境设置为 _`false`_ `HHDoctor.init(options)` 

_`// 2.`_ 登录 `HHDoctor.login(userToken, { onSuccess: ()` **`=>`** `{ " " console.log(` 登录成功 `) }, onFail: (code: number, msg: string)` **`=>`** `{ " " console.error(` 登录失败 `, code, msg) } })` _`// 3.`_ 调用功能 `HHDoctor.home()` _`//`_ 进入信息流页面 

## 3. API 接口详情 

### 3.1 初始化 SDK 

##### **`HHDoctor.init(options: HHSDKOptions): void`** 

描述: 初始化和缓视频医生 SDK,应用启动时调用一次即可。 

#### 参数: 

file:///Users/iOS/Desktop/%E5%92%8C%E7%BC%93%E8%A7%86%E9%A2%91%E5%8C%BB%E7%94%9FHarmonyOS_SDK_API%E6%96%87%E6%A1%... 

2025/11/10 12:11 

和缓视频医生HarmonyOS_SDK_API文档 

参数名 类型 必填 说明 

options HHSDKOptions 是 SDK 初始化配置对象 

#### HHSDKOptions 对象: 

#### 属性名 类型 必填 

#### 说明 

sdkProductId number 是 产品 ID,联系和缓商务分配获取 isDev boolean 是 是否为测试环境。true=测试环境,false=生产环境 

#### 示例代码: 

**`let`** `options =` **`new`** `HHSDKOptions() options.sdkProductId = 12345` _`//`_ 替换为实际的产品 _`ID`_ `options.isDev =` **`false`** `HHDoctor.init(options)` 

#### 注意事项: 

⚠ 必须在使用其他 API 之前调用此方法 

- 一 

- ⚠ 应用生命周期内只需调用 次 

- ⚠ sdkProductId 请妥善保管,不要泄露 

### 3.2 用户登录 

##### **`HHDoctor.login(userToken: string, listener: HHLoginListener): void`** 

描述: 登录和缓账号,获取用户身份认证。 

#### 参数: 

参数名 类型 必填 说明 userToken string 是 用户安全标志,由视频医生提供方分配 listener HHLoginListener 是 登录结果回调接口 

#### HHLoginListener 接口: 

#### 方法名 

#### 参数 

说明 

onSuccess () => void 登录成功回调 onFail (code: number, msg: string) => void 登录失败回调 

#### 示例代码: 

`HHDoctor.login("user_token_12345", { onSuccess: ()` **`=>`** `{ " " console.log(` 登录成功 `)` _`//`_ 可以进行后续操作,如进入信息流页面 

file:///Users/iOS/Desktop/%E5%92%8C%E7%BC%93%E8%A7%86%E9%A2%91%E5%8C%BB%E7%94%9FHarmonyOS_SDK_API%E6%96%87%E6%A1%... 

2025/11/10 12:11 

和缓视频医生HarmonyOS_SDK_API文档 

`HHDoctor.home() }, onFail: (code: number, msg: string)` **`=>`** `{ ` console.error(` 登录失败 `: code=${code}, msg=${msg}`)` _`//`_ 显示错误提示给用户 `} })` 

#### 注意事项: 

⚠ userToken 需要从服务端获取,不要写死在客户端代码中 ⚠ 登录成功后才能调用需要登录态的接口 

### 3.3 用户登出 

##### **`HHDoctor.logOut(): void`** 

描述: 退出和缓账号登录,清除本地登录态。 

#### 参数: 无 

#### 返回值: 无 

#### 示例代码: 

`HHDoctor.logOut() " " console.log(` 用户已登出 `)` 

#### 注意事项: 

- ⚠ 登出后需要重新登录才能使用需要登录态的功能 ⚠ 建议在用户主动退出登录或切换账号时调用 

### 3.4 直接呼叫视频医生 

##### **`HHDoctor.call(userToken: string, listener: HHCallListener | null): void`** 

描述: 直接发起视频问诊,系统将自动分配医生并建立视频通话。 

#### 参数: 

参数名 类型 必填 说明 userToken string 是 用户安全标志 listener HHCallListener | null 否 呼叫事件回调接口,可传 null 

#### HHCallListener 接口: 

file:///Users/iOS/Desktop/%E5%92%8C%E7%BC%93%E8%A7%86%E9%A2%91%E5%8C%BB%E7%94%9FHarmonyOS_SDK_API%E6%96%87%E6%A1%... 

2025/11/10 12:11 

和缓视频医生HarmonyOS_SDK_API文档 

#### 方法名 

#### 参数 

#### 说明 

onStart (orderId: string) => void 启动呼叫时回调,返回订单 ID onCalling () => void 呼叫中(等待医生接听) onChatting () => void 通话中(医生已接听) onLineUp () => void 需要排队等待 onHangup (chatTime: number) => void通话结束,返回通话时长 (秒) onCancel () => void 用户取消呼叫 (code: number, msg: string) onFail 呼叫失败 => void onLoadDoctor (doctor: HHCallInfo) => void 分配医生成功,返回医生信息 

#### HHCallInfo 对象: 

属性名 类型 说明 doctorId string 医生 ID doctorName string 医生姓名 hospitalName string 医院名称 departmentName string 科室名称 title string 职称 avatar string 医生头像 URL 

#### 示例代码: 

`HHDoctor.call("user_token_12345", { onStart: (orderId: string)` **`=>`** `{ ` console.log(` 订单创建成功 `: ${orderId}`) }, onCalling: ()` **`=>`** `{ " console.log(` 正在呼叫医生 `...") }, onChatting: ()` **`=>`** `{ " " console.log(` 医生已接听,通话中 `) }, onLineUp: ()` **`=>`** `{ " " console.log(` 当前医生忙碌,需要排队等待 `) }, onHangup: (chatTime: number)` **`=>`** `{ ` ` console.log(` 通话结束,通话时长 `: ${chatTime}` 秒 `) }, onCancel: ()` **`=>`** `{ " " console.log(` 用户取消呼叫 `) },` file:///Users/iOS/Desktop/%E5%92%8C%E7%BC%93%E8%A7%86%E9%A2%91%E5%8C%BB%E7%94%9FHarmonyOS_SDK_API%E6%96%87%E6%A1%... 

2025/11/10 12:11 

和缓视频医生HarmonyOS_SDK_API文档 

`onFail: (code: number, msg: string)` **`=>`** `{ ` console.error(` 呼叫失败 `: code=${code}, msg=${msg}`) }, onLoadDoctor: (doctor: HHCallInfo)` **`=>`** `{ ` console.log(` 分配医生 `: ${doctor.doctorName}`) } })` 

#### 注意事项: 

- ⚠ 需要先调用 `init()` 初始化 SDK 

- ⚠ 需要用户授权摄像头和麦克风权限 

- ⚠ 建议实现所有回调方法以便更好地处理各种状态 

### 3.5 进入信息流页面 

##### **`HHDoctor.home(): void`** 

描述: 打开信息流(消息列表)页面,查看历史问诊记录和消息。 

#### 参数: 无 

#### 返回值: 无 

前置条件: ⚠ 必须先调用 `login()` 登录成功 

#### 示例代码: 

_`//`_ 确保已登录 `HHDoctor.login(userToken, { onSuccess: ()` **`=>`** `{` _`//`_ 登录成功后进入信息流页面 `HHDoctor.home() }, onFail: (code, msg)` **`=>`** `{ " " console.error(` 登录失败,无法进入信息流 `) } })` 

#### 注意事项: 

⚠ 如果未登录调用此方法,会自动跳转到登录页面 ⚠ 信息流页面展示所有历史问诊会话 

### 3.6 问诊详情页面 

##### **`HHDoctor.medicDetail(userToken: string, mid: string): void`** 

file:///Users/iOS/Desktop/%E5%92%8C%E7%BC%93%E8%A7%86%E9%A2%91%E5%8C%BB%E7%94%9FHarmonyOS_SDK_API%E6%96%87%E6%A1%... 

2025/11/10 12:11 

和缓视频医生HarmonyOS_SDK_API文档 

#### 描述: 打开指定病历的详情页面,查看完整的问诊记录。 

#### 参数: 

#### 参数名 类型 必填 

#### 说明 

userToken string 是 用户安全标志 mid string 是 病历存档 ID,由视频医生提供方同步 

#### 返回值: 无 

#### 示例代码: 

_`//`_ 打开指定病历详情 `HHDoctor.medicDetail("user_token_12345", "medic_id_67890")` 

#### 注意事项: 

- ⚠ mid(病历 ID)需要从服务端获取 

- ⚠ 只能查看属于当前用户的病历记录 

### 3.7 配置视频中邀请家人 

##### **`HHDoctor.setWxMiniInviteHandler(handler: HHWXMiniInviteApi): void`** 

#### 描述: 配置视频问诊中邀请家人功能,通过微信小程序实现。 

版本要求: v1.0.7+ 

前置条件: 1. ✅ 联系和缓商务开通”视频中邀请家人”权益 2. ✅ 接入微信 SDK 

#### 参数: 

参数名 类型 必填 说明 handler HHWXMiniInviteApi 是 微信小程序邀请回调接口 

#### HHWXMiniInviteApi 接口: 

onInvite 

#### 方法名 

参数 (path: string, wxAppId: string) => void 

说明 邀请回调,path=小程序路 径,wxAppId=小程序ID 

#### 示例代码: 

_`// 1.`_ 实现 _`HHWXMiniInviteApi`_ 接口 

```
class HHInviteWXMini implements HHWXMiniInviteApi {
/**
```

_`*`_ 邀请家人回调 

file:///Users/iOS/Desktop/%E5%92%8C%E7%BC%93%E8%A7%86%E9%A2%91%E5%8C%BB%E7%94%9FHarmonyOS_SDK_API%E6%96%87%E6%A1%... 

2025/11/10 12:11 

和缓视频医生HarmonyOS_SDK_API文档 

```arkts
_`*`_ **_`@param path`_** 小程序 _`path *`_ **_`@param wxAppId`_** 小程序 _`ID */`_ `onInvite(path: string, wxAppId: string): void { ` console.log(` 打开小程序 `: ${wxAppId}, path: ${path}`)` _`// 3.`_ 调用微信 _`SDK`_ 打开小程序 _`//`_ 这里需要接入实际的微信 _`SDK`_ `wx.miniProgram.navigateTo({ url: path, appId: wxAppId, success: ()` **`=>`** `{ " " console.log(` 成功打开微信小程序 `) }, fail: (err)` **`=>`** `{ " " console.error(` 打开小程序失败 `, err) } }) } }` _`// 2.`_ 创建实例 **`export const`** `hhInviteMini =` **`new`** `HHInviteWXMini()` _`// 3.`_ 向和缓 _`SDK`_ 注册监听器 `HHDoctor.setWxMiniInviteHandler(hhInviteMini)` 
```

#### 注意事项: 

- ⚠ 需要先联系商务开通此功能权益 

- ⚠ 需要集成微信 SDK 才能正常使用 

- ⚠ 仅在视频通话过程中有效 

## 4. 数据模型 

### 4.1 HHSDKOptions 

#### SDK 初始化配置对象 

**`class`** `HHSDKOptions { sdkProductId: number` _`//`_ 产品 _`ID`_ (必填) `isDev: boolean` _`//`_ 是否测试环境(必填) `}` 

### 4.2 HHCallInfo 

#### 医生信息对象 

**`interface`** `HHCallInfo { doctorId: string` _`//`_ 医生 _`ID`_ `doctorName: string` _`//`_ 医生姓名 `hospitalName: string` _`//`_ 医院名称 `departmentName: string` _`//`_ 科室名称 

file:///Users/iOS/Desktop/%E5%92%8C%E7%BC%93%E8%A7%86%E9%A2%91%E5%8C%BB%E7%94%9FHarmonyOS_SDK_API%E6%96%87%E6%A1%... 

和缓视频医生HarmonyOS_SDK_API文档 

2025/11/10 12:11 `title: string` _`//`_ 职称 `avatar: string` _`//`_ 医生头像 _`URL`_ `experience?: string` _`//`_ 从业经验(可选) `expertise?: string[]` _`//`_ 擅长领域(可选) `}` 

### 4.3 回调接口 

#### HHLoginListener 

```
interface HHLoginListener {
  onSuccess: () =>void
  onFail: (code:number, msg:string) =>void
}
```

#### HHCallListener 

```
interface HHCallListener {
  onStart: (orderId:string) =>void
  onCalling: () =>void
  onChatting: () =>void
  onLineUp: () =>void
  onHangup: (chatTime:number) =>void
  onCancel: () =>void
  onFail: (code:number, msg:string) =>void
  onLoadDoctor: (doctor: HHCallInfo) =>void
}
```

#### HHWXMiniInviteApi 

```
interface HHWXMiniInviteApi {
  onInvite: (path:string, wxAppId:string) =>void
}
```

## 5. 附录 

### 5.1 完整示例代码 

**`import`** `{ HHDoctor, HHSDKOptions }` **`from`** `'@hh-medic/hhsdk'` _`//`_ 应用启动时初始化 **`function`** `initSDK() {` **`let`** `options =` **`new`** `HHSDKOptions() options.sdkProductId = 12345` _`//`_ 实际产品 _`ID`_ `options.isDev =` **`false`** `HHDoctor.init(options) }` _`//`_ 用户登录 **`function`** `login(userToken: string) { HHDoctor.login(userToken, { onSuccess: ()` **`=>`** `{ " " console.log(` 登录成功 `)` 

file:///Users/iOS/Desktop/%E5%92%8C%E7%BC%93%E8%A7%86%E9%A2%91%E5%8C%BB%E7%94%9FHarmonyOS_SDK_API%E6%96%87%E6%A1%... 

2025/11/10 12:11 

和缓视频医生HarmonyOS_SDK_API文档 

_`//`_ 登录成功后可以调用其他功能 `}, onFail: (code: number, msg: string)` **`=>`** `{ ` console.error(` 登录失败 `: ${code} - ${msg}`) } }) }` _`//`_ 发起视频问诊 **`function`** `startVideoCall(userToken: string) { HHDoctor.call(userToken, { onStart: (orderId: string)` **`=>`** `{ ` console.log(` 订单 `ID: ${orderId}`) }, onLoadDoctor: (doctor)` **`=>`** `{ ` console.log(` 医生 `: ${doctor.doctorName}`) }, onChatting: ()` **`=>`** `{ " " console.log(` 通话中 `) }, onHangup: (chatTime: number)` **`=>`** `{ ` console.log(` 通话结束,时长 `: ${chatTime}s`) }, onFail: (code: number, msg: string)` **`=>`** `{ ` console.error(` 呼叫失败 `: ${code} - ${msg}`) } }) }` _`//`_ 进入信息流 **`function`** `enterHome() { HHDoctor.home() }` _`//`_ 查看病历详情 **`function`** `viewMedicDetail(userToken: string, mid: string) { HHDoctor.medicDetail(userToken, mid) }` _`//`_ 用户登出 **`function`** `logout() { HHDoctor.logOut() " " console.log(` 已登出 `) }` 

### 5.2 权限配置模板 

```
{
"module":{
"abilities":[
{
"name":"EntryAbility",
"srcEntry":"./ets/entryability/EntryAbility.ts",
"description":"$string:EntryAbility_desc",
"icon":"$media:icon",
"label":"$string:EntryAbility_label",
"startWindowIcon":"$media:icon",
"startWindowBackground":"$color:start_window_background",
"export ed":true,
```

file:///Users/iOS/Desktop/%E5%92%8C%E7%BC%93%E8%A7%86%E9%A2%91%E5%8C%BB%E7%94%9FHarmonyOS_SDK_API%E6%96%87%E6%A1%... 11/12 

2025/11/10 12:11 和缓视频医生HarmonyOS_SDK_API文档 `"skills": [ { "entities": [ "entity.system.home" ], "actions": [ "action.system.home" ] } ], "backgroundModes": [ "voip" ] } ], "requestPermissions": [ { "name": "ohos.permission.INTERNET", "reason": "$string:internet_permission_reason", "usedScene": { "abilities": ["EntryAbility"], "when": "inuse" } }, { "name": "ohos.permission.CAMERA", "reason": "$string:camera_permission_reason", "usedScene": { "abilities": ["EntryAbility"], "when": "inuse" } }, { "name": "ohos.permission.MICROPHONE", "reason": "$string:microphone_permission_reason", "usedScene": { "abilities": ["EntryAbility"], "when": "inuse" } } ] } }` 

文档版本: v1.1.1 最后更新: 2025-11-10 © 2025 和缓医疗科技有限公司 版权所有 

file:///Users/iOS/Desktop/%E5%92%8C%E7%BC%93%E8%A7%86%E9%A2%91%E5%8C%BB%E7%94%9FHarmonyOS_SDK_API%E6%96%87%E6%A1%... 12/12
