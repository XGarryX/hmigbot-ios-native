# 鸿蒙接口文档 

使用 SDK 接口文档 

初始化 SDK 

getInstance(); 

设置运行环境 

setEvnOnline ( isOnline: boolean ) ;// 初始化云会议系统的环境,默 认为: Online 如果需要切换到 Beta 环境,请调 用 此 API 加入会议 

joinConfrenceWithReq(uiContext: UIContext, pathStack: NavPathStack, req: MeetingReq, 

completion: (success: boolean, error: ErrorDomain | null) => void) ;//uiContext 

ui 上下文用于相关弹出提示; pathStack 任务栈界面跳转; MeetingReq 为参数,其中 name 和 pcode 必传,详细请参见: MeetingReq ; completion 

# 结果回调 

# 监听会议状态 

setMeetingStatusBlock(block: (meetingStatus: QSMeetingStatus, error: ErrorDomain | null) => void) ;// 用于监听会议状态 

, meetingStatus 会议状态回调 

# 定制化会议服务 

setCasDomain(casDomain: string, completion: (success: boolean, error: ErrorDomain | null) => void) ;// 用于定制化会议服务 

- , casDomain :服务域名; completion 结果回调 

自定义 

# /// 是否跳过等待界面 

/// 默认关; Deafult: false 

/// 

isJumpJoin: Number; 

/// 

/// 入会是否开启音频 /// 默认开; Deafult: true /// isShowAudio : Number; 

/// 

/// 入会是否开启视频预览 /// 默认开; Deafult: true /// 

isShowVideo : Number; 

/// 

/// 使用链接入会 

/// 默认关; Deafult: false 

/// 

useJoinLink : Number; 

调用实例 

// 使用密码入会 

this.code = '887-444-482-582' 

# // 使用链接入会 

// this.code = 'https://n.qsh1.cn/d/auG8PQY7nKH' 

const paramReq: MeetingReq = new MeetingReq() 

paramReq.isShowAudio = true; // 默认打开音频 voip paramReq.isShowVideo = true; // 默认开启视频 

paramReq.isJumpJoin = false; // 是否跳过预览 

paramReq.name = "hm sdk" // 名称 

// paramReq.userId = 22465942; // 用户 id ,不传默认为访客 

if (this.isLinkJoinMeeitng) { 

paramReq.pcode = this.code; 

paramReq.useJoinLink = true; // 标记使用链接入会 

} else { 

paramReq.pcode = this.code.replace(/-/g, ""); 

console.log('pcode', paramReq.pcode) 

paramReq.useJoinLink = false; 

} 

# // 开始入会 

// TangInterface.getInstance() 

// .setCasDomain("https://newcas.quanshi.com", (success: boolean, error: ErrorDomain | null) => { 

// if (success) { 

TangInterface.getInstance() 

.joinConfrenceWithReq(this.getUIContext(), this.pathStack, paramReq, 

(success: boolean, error: ErrorDomain | null) => { 

logWithTag('demo', '', 'joinConfrenceWithReq ', success, 'error:', error ? error.code : -1) 

PromptActionClass.closeCustomDialogById('loading') 

if (error || !success) { 

return 

} 

}); 

// 监听会议状态监听 

TangInterface.getInstance() 

.setMeetingStatusBlock((meetingStatus: QSMeetingStatus, error: ErrorDomain | null) => { 

logWithTag('demo', '', 'meetingStatus :', meetingStatus) 

})
