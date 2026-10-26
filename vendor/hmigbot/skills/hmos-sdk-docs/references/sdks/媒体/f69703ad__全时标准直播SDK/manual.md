# 全时标准直播 SDK(HarmonyOS) 

## 全时标准直播 SDK(HarmonyOS) 

### 简介 

一 全时标准直播 SDK 是 套用于在 HarmonyOS 应用中快速集成全时直播能力的 Native SDK。 只需少量代码,即可在现有应用中嵌入完整的直播间界面、直播互动,以及连麦等相关能力, 并支持通过配置对客戶端进行定制。 

SDK 同时支持基于 WebRTC 的低延迟实时拉流与音视频渲染,集成简单、接入成本低,适合具 一 备 定开发能力、希望在自有应用中直接集成直播或视频会议能力的客戶。依托全时云直播后 台,单场直播可支持百万级并发。 

更多问题可参考官方文档:https://developer.quanshi.com/cn 

### 快速集成 

#### 1.添加模块依赖 

##### 在宿主工程的 oh-package.json5 中添加本地依赖: 

Plain Text 

1 ohpm install livesdk 

并在工程 build-profile.json5 的 modules 中注册 livesdk 模块。 

#### 2.导入 SDK 

TypeScript 

1 import { QSLiveSDK, QSLiveReq } from 'livesdk' 

#### 3.初始化并调用 

TypeScript 

- 1 // 应用启动时初始化(可选,预留扩展) 

- 2 QSLiveSDK.init(this.pathStack) 

- 3 

- 4 // 加入直播间 

- 5 const req: QSLiveReq = { 

- 6 pcode: "", 

- 7 liveCode: "", 

- 8 liveUrl: "", 

- 9 userName: " 张三 ", 

- 10 userId: "", 

- 11 conferenceId: "", 

- 12 audienceJoinUrl: "https://example.com/live/xxx", 

- 13 phone: "", 

- 14 email: "user@example.com", 

- 15 openId: "", 

- 16 countryCode: "86", 

- 17 company: "", 

- 18 umsToken: "", 

- 19 isGuest: "", 

- 20 extUserId: "" 

- 21 } 

- 22 

- 23 await QSLiveSDK.joinLive(req, (resultCode: number) => { 

- 24 if (resultCode === 0) { 

- 25 // 加入成功 

- 26 } else { 

- 27 // 加入失败, resultCode 为错误码 

- 28 } 

- 29 }) 

- 30 

- 31 // 退出直播间 

- 32 await QSLiveSDK.exitLive((resultCode: number) => { 

- 33 if (resultCode === 0) { 

- 34 // 退出成功 

- 35 } 

- 36 }) 

### API 说明 

#### QSLiveSDK.init() 

一
初始化 SDK,预留全局配置、日志等扩展能力。当前为空实现,建议在应用启动阶段调用
次。

- TypeScript 1 QSLiveSDK.init(): void 

#### QSLiveSDK.joinLive() 

##### 加入直播间。 

TypeScript 

- 1 QSLiveSDK.joinLive( 

- 2 req: QSLiveReq, 3 callback?: (resultCode: number) => void 4 ): Promise<void> 

参数 类型 说明
req QSLiveReq 入会请求参数
callback (resultCode: number) =>  可选,加入结果回调
void

##### resultCode 说明: 

值 说明
0 加入成功
-1 参数校验失败(如 pcode、观众链接为空)
其他 服务端返回的业务错误码

#### QSLiveSDK.exitLive() 

退出直播间,释放聊天室、心跳、WebSocket 等资源,并通知直播间页面关闭。 

TypeScript 

1 QSLiveSDK.exitLive(
2   callback?: (resultCode: number) => void
3 ): Promise<void>
参数 类型 说明
callback (resultCode: number) =>  可选,退出结果回调
void
resultCode 说明:
值 说明
0 退出成功(含当前未在直播间内的幂等场景

### QSLiveReq 参数说明 

|字段|类型|说明|
|---|---|---|
|pcode|string|入会密码。主持人为pcode�,参会人 pcode�|
|liveCode|string|分享直播码|
|liveUrl|string|链接入会时的直播URL|
|userName|string|用戶名|
|userId|string|用戶ID|
|conferenceId|string|会议ID|
|audienceJoinUrl|string|观众入会链接( 为空时必填) pcode|
|phone|string|手机号|
|email|string|邮箱|
|openId|string|OpenID|
|countryCode|string|手机国家码,不带 ,默认 + 86|
|company|string|部门|
|umsToken|string|UMS Token|
|isGuest|string|落地页进入直播间传 1|
|extUserId|string|外部用戶ID|

> pcode 与 audienceJoinUrl 至少传一个;通过观众链接入会时,SDK 会自动从链接中解 析 pcode 和 ukey 。 

### 典型调用流程 

###### Plain Text 

- 1 应用启动 2 └── QSLiveSDK.init() 3 用戶点击「进入直播」 4 └── QSLiveSDK.joinLive(req, callback) 5 └── callback(0) → 进入直播间页面 6 用戶离开 / 点击关闭 

- 7 └── QSLiveSDK.exitLive(callback) 8 └── 释放资源,关闭直播间
