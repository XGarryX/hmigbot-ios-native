// 参数 1. 页面栈 NavPathStack, 2. 实现 TKRoomCallback 的回调类 ( 可选 ) 

roomManger = new TKRoomManager(this.pageStack, new RoomCallback(this)) 

# // 进入频道 

public joinRoomWithParams(options: RoomOption): Promise<api.IGetEnterRoomUrlResponse> 

# // 进入回放频道 

public joinRoomWithPlaybackParams(options: PlaybackRoomOption): Promise<api.IGetRoomPlayUrlResponse> 

# // 进入频道(通过链接进入 ) 

public joinRoomWithUrl(url: string): Promise<api.IGetEnterRoomUrlResponse> 

// 进入回放 Mp4 

public joinRoomWithPlaybackPath(path:string) 

/** 

# * 进入频道的所需的参数 

* */ 

export class RoomOption { 

/** 

# * 频道号 

* */ 

serial: string = "0" 

/** 

* 昵称 

* */ 

userName: string = "tk test" 

/** 

* 用户角色 

* */ 

userRole: string = "0" || "2" 

/** 

- 企业域名(当使用 thridRoomId 时,此字段必传) 

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

- 第三方系统的用户 id 

* */ 

userId?: string 

} 

export class PlaybackRoomOption extends RoomOption { 

/** 

* 录制件 title 

*/ 

recordTitle?: string 

} 

// 进入成功 

onEntrySuccess?():void; 

// 进入失败 

onEntryError?(result:number):void; 

/** 

# * 教室状态 

- @returns 1 上课 , 0 下课 

*/ 

onRoomState?(state:number):void; 

# // 离开频道成功 

onLeaveRoom?():void; 

# // 被踢回调 

onKickOut?(reason:EventParticipantEvictedEnum):void; 

// 课堂页面消失 

onRoomDestroy():void;
