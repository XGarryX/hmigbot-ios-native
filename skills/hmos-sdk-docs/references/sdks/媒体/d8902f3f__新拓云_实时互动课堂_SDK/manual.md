新拓云 实时互动课堂 SDK TKUISdk.har 使用指南 

# 1. 前言 

1.1 在您阅读此文档时,我们假定您已经具备了基础的 iOS 应用开发 经验,并能够理解相关基础概念。 1.2 请到拓课官方网站下载 Talkcloud SDK HarmonyOS NEXT 版 , https://www.talk-cloud.com/ download/uisdk/ 。 1.3 版本兼容 适用于 API Version 12(5.0.0.25) 以上 

# 2. 工程设置 

2.1 开发环境 DevEco Studio NEXT Beta1+ 2.2 添加 TKUISdk.har 依 赖 在模块级的 oh-package.json5 中添加依赖 , 例如 : 

"dependencies": { 

"tkuisdk": "file:../ 存放 sdk 路径 /TKUISdk.har" 

} 

2.3 TKUISdk.har 中已经添加对 网络 / 摄像头 / 麦克风的权限申请 

3. SDK 使用 

3.1 频道管理类 TKRoomManager 3.1.1 初始化 

// 参数 1. 页面栈 NavPathStack, 2. 实现 TKRoomCallback 的回调类 ( 可选 ) 

roomManger = new TKRoomManager(this.pageStack, new RoomCallback(this)) 

3.1.2 使用 

// 进入频道 public joinRoomWithParams(options: RoomOption): Promise<api.IGetEnterRoomUrlResponse> 

// 进入回放频道 public joinRoomWithPlaybackParams(options: 

PlaybackRoomOption): Promise<api.IGetRoomPlayUrlResponse> 

// 进入频道(通过链接进入 )public joinRoomWithUrl(url: string): Promise<api.IGetEnterRoomUrlResponse> 

// 进入回放 Mp4public joinRoomWithPlaybackPath(path:string) 

参数 : 

/** 

# * 进入频道的所需的参数 

* */export class RoomOption { 

/** 

# * 频道号 

* */ 

serial: string = "0" 

/** 

* 昵称 

* */ 

userName: string = "tk test" 

/** 

# * 用户角色 

* */ 

userRole: string = "0" || "2" 

/** 

* 企业域名(当使用 thridRoomId 时,此字段必传) 

* */ 

domain?: string 

/** 

- 第三方教室号 (serial 和 thirdRoomId 二则必传一个 ) 

* */ 

thirdRoomId?: string 

/** 

* 用户密码,格式为: 128 位 AES 加密串加密密钥默认为 5NIWjlgmvqwbt494 

* */ 

userPwd?: string 

/** 

* 第三方系统的用户 id 

* */ 

userId?: string 

} 

export class PlaybackRoomOption extends RoomOption { 

/** 

* 录制件 title 

*/ 

recordTitle?: string 

} 

# 3.2 回调类 TKRoomCallback 

// 进入成功 

onEntrySuccess?():void; 

// 进入失败 

onEntryError?(result:number):void; 

/** 

# * 教室状态 

- @returns 1 上课 , 0 下课 

*/ 

onRoomState?(state:number):void; 

// 离开频道成功 

onLeaveRoom?():void; 

// 被踢回调 

onKickOut?(reason:EventParticipantEvictedEnum):void; 

// 课堂页面消失 

onRoomDestroy():void;
