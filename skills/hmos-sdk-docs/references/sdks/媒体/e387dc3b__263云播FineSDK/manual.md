# **鸿蒙版云播 FineSDK** 

不带界面的 SDK,几乎包含直播的所有⻆色与功能,适合于高定制化的项目,需要的开发较 多。如果只是集成嘉宾或者主播端,可以选择使用 FastSDK。 

## **支持的⻆色身份** 

1. 观众端 

2. 嘉宾端 

3. 主播端 

4. 助手端 

## **下载** 

SDK 文件下载 

- 网盘下载地址:https://drive.263.net/link/wkha72KciczFM0o 

点击下载即可。 

## **概述** 

- 该 SDK 是用于客户端接入 263 云播服务 

- SDK 包内不包含 UI,不包含直播播放器 

## **登录流程** 

本 SDK 支持使用直播 ID,相应的密码进入。 

## **版本记录** 

|**版本号**|**时间**|**描述**|
|---|---|---|
|V1.0.0|2024-9-26|初始版本|

# **快速开始** 

## **1. SDK 初始化** 

this.gsCloudLive = new GSCloudLive() this.gsCloudLive?.init(getContext(this)) 

## **2. 站点后台直播信息** 

站点后台:https://www.263live.net/clm/# 

#### 登录后可创建或查看已有直播信息: 

## **3. 准备加入** 

##### // 构建加入参数对象 

let param = new GSJoinParam(webcastId, nickname) // 直播间 id 和用户昵称 param.passCode = passCode // 加入密码 param.type = role // 加入身份 

class MyCallback implements JoinLiveCallback { 

onJoinSuccess(liveRoomData: LiveRoomData): void { showToast("加入成功") LogUtils.info(TAG, "加入成功") } 

```arkts
onJoinFail(message: string): void { // showToast("加入失败:" + message) LogUtils.info(TAG, "加入失败:" + message) reject(new GSError(message)) } } 
```

##### // 设置回调 

this.gsCloudLive?.setJoinLiveCallback(new MyCallback()) // 加入直播 this.gsCloudLive?.joinLive(param) 

## **4. GSCloudLive 接口列表** 

#### GSCloudLive 类中包含以下方法: 

// 加入直播间 

joinLive(joinParam: GSJoinParam): void 

// 判断嘉宾是否有显示观众列表的权限 

getGuestShowAudience(): boolean 

// 更改直播间开启/关闭状态 

webcast(status: LiveCtrlStatus): Promise<void> 

##### // 更改直播间录制开启/关闭状态 

record(status: RecordCtrlStatus): Promise<void> 

##### // 设置直播间中的回调 

setLiveCallback(liveCallback: LiveCallback) 

// 设置加入直播的结果回调 

setJoinLiveCallback(joinLiveCallback: JoinLiveCallback) 

// 获取当前登录用户的详细信息 getSelfData(): SelfUserData | undefined 

// 主动离开直播间 leaveLiveRoom() // 获取主控用户 id getMainControlUid(): string // 获取演示用户 id getShowControlUid(): string 

## **5. 功能 API 分类** 

API 按功能分为直播相关、文档相关、聊天相关、用户相关、视频流相关几大块。 

每个 API 通过以下方式获取: 

this.gsCloudLive.liveApi this.gsCloudLive.docApi this.gsCloudLive.chatApi this.gsCloudLive.userApi this.gsCloudLive.streamApi 

文档、聊天、用户三个模块都有其专属的 callback 回调,比如用户加入、收到聊天等,这些 callback 需要通过对应的 api 类对象进行注册: 

this.gsCloudLive.setLiveCallback(this) this.gsCloudLive.docApi.setDocCallback(this.docModel) this.gsCloudLive.chatApi.setCallback(this.chatModel) this.gsCloudLive.userApi.setCallback(this.userModel) 

#### 每个 API 具体的功能和 callback 见功能模块描述。 

# **功能模块** 

## **直播间相关 API (LiveApi)** 

### **ILiveApi 接口** 

export interface ILiveApi { /** * 获取点赞数量 */ getPraiseCount(): Promise<number> /** * 设置音频主控模式 * @param enable 是否启用 */ setAudioMainControlEnable(enable: boolean): void /** * 设置视频主控模式 * @param enable 是否启用 */ setVideoMainControlEnable(enable: boolean): void /** * 全体音频控制 * @param enable 是否启用 */ setLiveAudioEnable(enable: boolean): void /** * 设置嘉宾显示观众列表 * @param enable 是否启用 */ setGuestSeeAuth(enable: boolean): Promise<void> } 

### **LiveCallback 回调接口** 

export interface LiveCallback { /** * 直播状态变更 * @param liveStatus 直播状态 */ onLiveStatus(liveStatus: YBLiveStatus): void /** * 录制状态变更(1 录制停止,0 录制中) * @param recordStatus 录制状态 */ onRecordStatus(recordStatus: YBRecordStatus): void /** * 直播简介(introduce 为富文本,需用 webview 展示) * @param introduce 直播简介 */ onLiveIntroduce(introduce: string): void /** * 互动模块列表 * @param tags 互动标签列表 */ onLiveTags(tags: LiveTag[]): void /** * 主控权变更 * @param userId 用户 ID */ onMainControlUserId(userId: string): void /** * 演示权变更 * @param userId 用户 ID */ onShowingUserId(userId: string): void /** * 嘉宾权限变更(是否显示观众列表) * @param status 1-有权限,2-无权限 */ onGuestSeeAuth(status: number): void 

/** * Mic 主控状态 * @param open true-开启主控状态(嘉宾不能打开自己的 mic),false-关闭主控 

*/ onMicMainControlStatus(open: boolean): void 

/** * 摄像头主控状态 * @param open true-开启主控(嘉宾不能主动打开 Camera),false-关闭主控 */ onCameraMainControlStatus(open: boolean): void 

/** * 退出直播间 * @param reason 退出原因 */ onLiveLeave(reason: YBLeaveReason): void /** * 流数据更新 * @param streamUrl 拉流地址 */ onLivePullStreamUrl(streamUrl: PullStreamUrl): void /** * 重连中 */ onLiveReconnecting(): void /** * 直播设置更新 * @param settingInfo 直播设置信息 */ onLiveSetting(settingInfo: BroadcastSettingInfo): void /** * 直播源设置切换 * @param opType 0-直播流,1-接收第三方推流,2-拉取第三方推流 */ onLiveVideoSourceSwitch(opType: number): void /** * 直播源结束 */ onLiveVideoSourceStop(): void /** * 观看配置更新 * @param config 观看配置 */ onWatchConfig(config: WatchConfig): void 

/** * 直播间主播变更 * @param uid 用户 ID * @param cid ⻆色 ID * @param name 主播名称 */ onLiveAnchorChange(uid: string, cid: string, name: string): void /** * 自身⻆色变更 * @param role 用户⻆色 */ onSelfRoleChange(role: YBUserRole): void /** * 点赞数量更新 * @param count 点赞数 */ onPraise(count: number): void /** * 多媒体插播状态通知 * @param state 插播状态 */ onMultiMediaNotify(state: boolean): void } 

## **文档模块 API (DocApi)** 

### **IDocApi 接口** 

export interface IDocApi { /** * 增加白板 * @param title 名称(可传空字符串) * @param whiteBoardId 白板 id */ addWhiteBoard(title: string, whiteBoardId: string): Promise<void> /** * 白板共享与文档共享切换 * @param type 白板或文档类型 */ switchShareType(type: DocType): Promise<void> 

/** 

* 获取当前共享的文档 * @returns 共享的文档数据(也可能是白板) */ getShareDoc(): Promise<IDocData | null> 

/** 

* 获取文档资源列表(主播、嘉宾、助手) 

* @param size 要取的数量(建议 20) 

* @param skip 从第几个开始(等同分页),最开始取 skip 应为 0 */ 

getDocList(size: number, skip: number): Promise<LiveResource<DocResourc 

/** 

* 发布/取消发布文档(需要有演示权) 

* @param resource 文档资源 

* @param publish true-发布,false-取消发布 */ 

publish(resource: Resource<DocResource>, publish: boolean): Promise<voi 

/** 

* 绑定资源到直播间 

* @param bindType 1-仅绑定到场次,2-同时绑定到场次和直播间(一般传 2) * @param resourceIds 要绑定的资源 id 列表 */ 

bindDoc(bindType: ResourceBindType, resourceIds: string[]): Promise<voi 

/** * 取消绑定 * @param resourceId 资源 id */ cancelBindDoc(resourceId: string): Promise<void> 

/** * 删除文档 * @param resourceId 文档资源 id */ deleteDoc(resourceId: string): Promise<void> 

/** 

* 共享/取消共享指定文档(转码成功的文档才能共享) * @param resourceData 文档资源 data * @param share true-共享,false-停止共享 */ shareDoc(resourceData: Resource<DocResource>, share: boolean): Promise< 

/** 

##### * 预览文档(可供无演示权时获取文档信息) 

* @param resourceData 文档资源 

*/ previewDoc(resourceData: Resource<DocResource>): Promise<IDocData> 

/** * 翻页跟随设置 * @param follow true-跟随有演示权之人翻页、标注(默认),false-不跟随 */ followDoc(follow: boolean): void /** * 获取到演示权后,同步当前的内容 * @param page 当前页(h5 webview 回调的 page) * @param stepIndex 步骤索引 */ syncShare(page: number, stepIndex: number): Promise<void> 

/** * 直播中上传文档 * @param filePath 文件路径(最大 4MB) * @param fileName 文件名 * 支持格式:ppt, pptx, dps, doc, docx, wps, pdf, png, jpg, jpeg, bmp, t */ uploadFile(filePath: string, fileName: string): Promise<void> /** * 切换白板页数 * @param page 目标页数 */ turnWhiteBoardPage(page: number): Promise<void> /** * 设置文档相关的 callback * @param callback 文档回调接口 */ setDocCallback(callback: DocCallback): void } 

### **DocCallback 回调接口** 

export interface DocCallback { /** * 直播过程中更新文档内容(app 执行 js 代码 doc.getNoticeJs()) * @param docData 更新的文档显示内容 */ onDocUpdate(docData: IDocData): void 

/** 

* 共享类型变更(切换文档和白板共享时会通知) * @param type DocType.SHARE_TYPE_WB-白板,DocType.SHARE_TYPE_DOC-文档 */ onShareType(type: DocType): void /** 

* 文档状态变更(当直播中上传文档后,有转码相关的状态变更) 

* @param fileId 文件 id 

* @param transFileId 转码后的文档 id 

* @param status 文件状态(0-未上传,1-上传成功,2-上传失败,3-上传中,4-转码中 */ 

onDocStatus(fileId: string, transFileId: string, status: number): void 

/** 

* 文档发布状态(主播、嘉宾、助手才会收到) * @param fileId 文档 id * @param isPublish true-已发布,false-未发布 */ onDocPublish(fileId: string, isPublish: boolean): void /** 

- 文档共享开始/停止(开始和停止指单个文档) 

* 文档使用 webview 来显示,如果 webview 的初始化不在加直播之前,请记录 doc, * webview 初始化后加载 url,并在 js 回调 oncreat 之后执行 initjs * @param doc 文档对象 * @param isShared true-文件共享,false-文件共享结束 */ onDocShare(doc: IDocData, isShared: boolean): void /** * 新白板页添加通知 * @param wb 新的白板页 */ onWhiteBoardAdd(wb: IDocData): void } 

**聊天模块 API (ChatApi)** 

### **IChatApi 接口** 

export interface IChatApi { /** 

* 获取历史聊天记录 * 加入直播之后获取加入之前的聊天消息,可根据需要调用 * @param size 条数 */ getChatHistory(size: number): Promise<ChatMsg[]> 

/** * 发送聊天消息 * @param msg 聊天内容(自己发送的消息通过 sdk 返回,如果是开启审核,需要审核之后 */ chat(msg: string): Promise<void> 

/** * 聊天消息撤回 * @param msgId 聊天消息 id */ chatRecall(msgId: string): Promise<void> /** * 消息回复/引用 * @param msg 被回复的消息 * @param replayMsg 回复内容 */ chatReply(msg: ChatMsg, replayMsg: string): Promise<void> /** * 直播间禁言控制 * @param enable true-允许聊天,false-禁止聊天 */ setLiveChatEnable(enable: boolean): Promise<void> /** 

* 直播间聊天审核控制开关 

* @param enable true-开启审核(开启后发送的聊天消息要审核通过后才会发给其他人和 */ setAuditEnable(enable: boolean): Promise<void> 

/** 

* 获取历史待审核的聊天消息 * @param topSize 预设最新条数 */ getChatAuditList(topSize: number): Promise<ChatMsg[]> 

/** 

##### * 主播/助手聊天审核 

- @param msgs 需要审核的消息列表 

* @param isAll true-所有通过审核(此时 msgs 无效,所有待审核消息会全部通过), */ 

chatAudit(msgs: ChatMsg[], isAll: boolean): Promise<void> 

/** 

* 主播、助手删除消息/全部删除 

* isAll 为 true 的情况下,删除 msgs 中第一条消息发送者的所有消息 

* @param msgs 需要删除的消息列表 

* @param isAll true-代表删除某个用户对应的所有聊天消息(此时 msgs 对应该用户的 */ chatDelete(msgs: ChatMsg[], isAll: boolean): Promise<void> 

/** * 删除指定用户的所有消息记录 * @param audience 指定用户 */ chatDeleteWithUser(audience: GSAudience): Promise<void> 

/** * 聊天消息高亮(主播/助手) * @param msg 需要高亮的消息 * @param highLight true-高亮,false-取消高亮 */ chatHighLight(msg: ChatMsg, highLight: boolean): Promise<void> /** * 聊天消息置顶(主播/助手) * @param msg 需要置顶的消息 * @param isTop true-置顶,false-取消置顶 */ chatTop(msg: ChatMsg, isTop: boolean): Promise<void> /** * 设置单人或多人禁言 * @param audiences 被禁言用户列表 * @param enable false-禁言,true-允许聊天 */ setAudienceChatEnable(audiences: GSAudience[], enable: boolean): Promis /** * 设置聊天相关的 callback * @param callback 聊天回调接口 */ setCallback(callback: ChatCallback): void } 

### **ChatCallback 回调接口** 

export interface ChatCallback { /** * 聊天禁言状态变更 * @param enable false-禁言,true-解除禁言 */ onChatEnable(enable: boolean): void /** * 聊天审核状态变更 * @param enable true-开启审核,false-关闭审核 */ onChatAudit(enable: boolean): void /** * 收到聊天消息 * @param msg 聊天消息 */ onChatMsg(msg: ChatMsg): void /** * 消息置顶/取消置顶 * @param msgId 消息 id * @param isTop true-置顶,false-取消置顶 */ onMsgTop(msgId: string, isTop: boolean): void /** * 消息高亮/取消高亮 * @param msgId 消息 id * @param isHighLight true-高亮,false-取消高亮 */ onHighlight(msgId: string, isHighLight: boolean): void /** * 某条消息撤回 * @param msgId 消息 id */ onMsgRecall(msgId: string): void /** * 某条消息删除 * @param msgId 消息 id */ onMsgDelete(msgId: string): void /** 

* 删除某个人的所有消息 * @param userId 用户 id */ onMsgDeleteByUserId(userId: string): void /** * 收到待审核消息 * @param msgs 待审核消息列表 */ onChatVerify(msgs: ChatMsg[]): void /** * 消息审核通过 * @param msgs 审核通过的消息列表 */ onChatVerifyPass(msgs: ChatMsg[]): void } 

## **用户模块 API (UserApi)** 

### **IUserApi 接口** 

export interface IUserApi { /** * 获取观众列表 * @param count 数量 * @param name 名称筛选 * @param sortID 排序 ID */ getAudienceList(count: number, name: string, sortID: number): Promise<G /** * 获取管理员列表 */ getManagerList(): Promise<GSManager[]> /** * 踢出观众 * @param uid 用户 id */ kickOutAudience(uid: string): Promise<void> /** * 助教归还主控权 */ 

giveMainControlBack(): Promise<void> 

/** 

* 主播收回主控权 

*/ 

takeBackMainControl(): Promise<void> 

/** 

##### * 助手根据主播密码获取主控权 

* @param hostPwd 主播密码 */ 

snatchMainControl(hostPwd: string): Promise<void> 

/** 

* 主播将主控权转移给助教 

* @param assistantId 目标助手 id 

*/ 

giveMainControlToAssistant(assistantId: string): Promise<void> 

/** * 主控权用户将演示权交给主播 */ returnShowControl(): Promise<void> 

/** 

* 主控权用户将演示权交给嘉宾 

* @param guestId 目标嘉宾用户 id */ giveShowControl(guestId: string): Promise<void> 

/** 

* 修改用户名(昵称) 

* @param newName 新的昵称 

* @param targetUserId 被修改人的 id(修改别人只支持主播和助手去修改嘉宾名称;不 */ 

updateName(newName: string, targetUserId: string): Promise<void> 

/** 

* 嘉宾通过主播密码升级为主播 * @param passCode 主播密码 */ upgradeHost(passCode: string): Promise<void> 

/** * 设置嘉宾为主播 * @param guestId 嘉宾 id */ grantGuestToHost(guestId: string): Promise<void> 

/** * 设置用户相关的 callback * @param callback 用户回调接口 */ setCallback(callback: UserCallback): void } 

### **UserCallback 回调接口** 

export interface UserCallback { /** * 用户加入 * @param userInfo 用户信息列表 */ onUserJoin(userInfo: GSManager[]): void 

/** * 用户更新 * @param userInfo 用户信息 */ onUserUpdate(userInfo: GSManager): void /** * 用户退出 * @param userInfo 用户信息 */ onUserLeave(userInfo: GSManager): void /** * 观众更新 * @param audienceInfo 观众信息 */ onAudienceUpdate(audienceInfo: GSAudience): void 

/** * 用户名称变更 * @param userId 用户 id * @param newName 新名称 */ onUserNameChanged(userId: string, newName: string): void 

/** * 观众列表变更 * @param count 观众数量 */ 

onAudienceListChanged(count: number): void 

/** * 用户数变更 * @param count 用户数 */ onUserCount(count: number): void 

/** 

* 用户禁言列表更新 

* @param silenceList 禁言列表 */ onUserSilenceList(silenceList: MuteAudienceInfo[]): void 

/** 

* 用户权限变更 

* @param groupUserBaseInfo 用户信息 

* @param roomUserPermission 权限列表 

* @param value 权限值(1-有权限,0-无权限) */ 

onUserPermissionChanged(groupUserBaseInfo: string, roomUserPermission: 

/** 

* 用户数显示配置 * @param isOnlineNumber true-显示在线人数,false-不显示 */ onUserConfig(isOnlineNumber: boolean): void /** * 单人禁言状态变更 * @param cid ⻆色 id * @param userId 用户 id * @param enable false-单人禁言,true-单人解除禁言 */ onUserChatEnable(cid: string, userId: string, enable: boolean): void } 

## **视频流模块 API (StreamApi)** 

### **IStreamApi 接口** 

export interface IStreamApi { /** * 发布视频流 

- 如果不发布或者 PubOption 都传入 Disable,其他端观看设备为禁用状态 

* @param micOption 麦克风选项 

* @param cameraOption 摄像头选项 

*/ 

pubStream(micOption: PubOption, cameraOption: PubOption): void 

/** 

* 订阅直播流 

* 传入的分辨率不一定为实际分辨率,会根据网络和设备情况动态变化,传入的只是一个期望值 * @param resolution 期望分辨率 

*/ 

subLiveStream(resolution: Resolution): void 

/** 

* 设置视频镜像 

* @param isMirror true-开启镜像,false-关闭镜像 

*/ 

setMirror(isMirror: boolean): void 

/** 

* 打开某人的摄像头 

* @param user 目标用户(不传则为自己) */ openCamera(user?: GSManager): void 

/** 

* 关闭某人的摄像头 

* @param user 目标用户(不传则为自己) */ closeCamera(user?: GSManager): void 

/** * 打开麦克风 * @param user 目标用户(不传则为自己) */ openMic(user?: GSManager): void /** * 关闭麦克风 * @param user 目标用户(不传则为自己) */ closeMic(user?: GSManager): void /** * 翻转自己的摄像头 */ switchCamera(): void } 

文档版本: _V1.0.0 |_ 更新日期: _2024-9-26_
