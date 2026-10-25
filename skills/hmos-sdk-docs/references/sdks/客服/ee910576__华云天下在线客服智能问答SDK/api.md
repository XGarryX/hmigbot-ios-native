华云天下在线客服智能问答 SDK 接口文档 V1.0 For Harmony OS 

修订记录: 

# 修订日期 

版本 修订内容 撰写人 

2025-1-16 

V1.0 首版创建 wuzc 

目录 

SDK 接口文档 1 

V1.0 For Harmony OS 1 

一、 SDK 使用说明 3 

1.1 SDK 文件说明 3 

1.2 SDK 使用配置 4 

二、接口说明 5 

2.1 初始化 5 

2.2 创建访客 5 

2.3 登录聊天账号 5 

2.4 开启新会话 5 

2.5 关闭会话 6 

2.6 获取历史会话列表 6 

2.7 访客提交留言 6 

2.8 转人工 7 

2.9 发送 emoji 富文本 7 

2.10 发送文本消息 7 

3.1 发送相机拍照 8 

3.2 发送相册图片 / 视频 8 

3.3 解析消息 8 

一、 SDK 使用说明 

# 1.1 SDK 文件说明 

华云天下在线客服智能问答 SDK 接口文档 V1.0 For Harmony OS 是基 于鸿蒙系统平台开发的,针对在线客服智能问答系统提供的一个集成 HAR 包。 

# 1.2 SDK 使用配置 

. 首先将 SDK 目录文件 hyworld_znkf.har 放到您的工程目录的某个文件 夹下。 

. 使用 import 导入您需要调用的 HAR 提供的 API 函数,即可调用我司提 供的功能。 

. 添加权限 , 在您工程的模块的文件夹中找到 module.json5 文件中的 requestPermissions 节点中添加需要的权限,如截图所示: 

二、接口说明 

# 2.1 初始化 

调用方式 

init(options: string):void 

参数说明 

options 

带有一些私密信息的可解析的 json 串 

备注 

# 2.2 创建访客 

调用方式 

createCustomer(accout:string):Promise<CustomerResult> 请求参数 

accout 

访客账号 返回参数 

Promise<CustomerResult> 回调函数 备注 

# 2.3 登录聊天账号 

调用方式 loginChatAccount(username:string, password:string): string 请求参数 

username 访客姓名 

password 统一密码 

返回参数 

message 

登录回调信息 

备注 

2.4 开启新会话 调用方式 startNewSession(): void 

参数说明 

备注 

2.5 关闭会话 调用方式 

handleGiveUp(sessionId: string ):void 

参数说明 

sessionId 

会话 id 

备注 

2.6 获取历史会话列表 

调用方式 

getUnFinishSession(account: string): Promise<ChatRecords> 参数说明 

account 访客账号 返回参数 Promise<ChatRecords> 历史会话列表 备注 

2.7 消息入库 

调用方式 

async insertMessage(msg: ChatMessage): void 

参数说明 

msg 聊天消息实体类 

备注 

2.8 转人工 

调用方式 changeToAgent(sessionId: string): string 请求参数 sessionId 会话 id 返回参数 string 转人工通知 

备注 

2.9 发送 emoji 富文本 

# 调用方式 

send(reason?: string, matches?:string[] ): void 

参数说明 

reason 

消息类型, 

matches ? 

富文本消息 

备注 

# 2.10 发送文本消息 

# 调用方式 

send(reason?: string, content?: string ): void 

参数说明 

reason 

消息类型, 

content 

文本内容 

备注 

# 3.1 发送相机拍照 

调用方式 

handleCameraButtonClick(): void 

参数说明 

备注 

# 3.2 发送相册图片 / 视频 

调用方式 

send(mediaUrl?: string, isVideo?:boolean): void 参数说明 mediaUrl 

图片 / 视频地址 

isVideo 

是否为视频 

备注 

# 3.3 解析消息 

调用方式 

parseMsg(reason:string, type:string, sessionId:string, waitingPosition:string, messageId:string, speakerName:string, 

userAccount:string, speakTime:string, body:string, needPost: boolean): void 

参数说明 

reason 

消息类型 

type 

消息来源 

sessionId 

会话 id 

waitingPosition 

等待位数 

messageId 消息序号 

speakerName 访客姓名 

userAccount 

账号 

speakTime 

消息时间戳 

needPost 

是否需要在列表里显示出来( UI 控制) 

body 

消息主题 

备注
