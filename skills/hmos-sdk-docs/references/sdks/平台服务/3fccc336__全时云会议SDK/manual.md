# 鸿蒙 sdk 使用指南 

# 简介 

全时云会议 SDK 是为用户集成全时云会议提供的一组 Native 

SDK ,基于云会议 SDK ,只需要少量代码,用户就可以快速定制自己 的会议客户端。云会议 SDK 提供完整的会议功能和界面,用户可以通 过配置文件对会议客户端进行定制。 

关于其他更多问题,您可以访问我们的官方文档: https:// developer.quanshi.com/cn 

快速上手 

前提条件 

DevEco Studio 5.1.0 Release 或以上版本 

支持最低系统版本为: 5.0.2 ( 14 ) 

执行安装命令 

ohpm install meetingsdk 

调用 

# // 使用密码入会 

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

// 开始入会 

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

# // 监听会议状态监听 

TangInterface.getInstance() 

.setMeetingStatusBlock((meetingStatus: QSMeetingStatus, error: ErrorDomain | null) => { 

logWithTag('demo', '', 'meetingStatus :', meetingStatus) 

})
