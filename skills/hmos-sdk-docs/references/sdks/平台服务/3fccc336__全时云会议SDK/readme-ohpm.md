> 来源: ohpm 中央仓 README(T1 信源) | 包: `meetingsdk` | ohpm 最新版: 1.0.4 | 抓取: 2026-07-16
> 注意: 版本可能比市场快照新,以此为准时核对 CHANGELOG

### 简介

全时云会议SDK是为用户集成全时云会议提供的一组Native
SDK,基于云会议SDK,只需要少量代码,用户就可以快速定制自己的会议客户端。云会议SDK提供完整的会议功能和界面,用户可以通过配置文件对会议客户端进行定制。

关于其他更多问题,您可以访问我们的官方文档:https://developer.quanshi.com/cn

###快速上手

###前提条件

DevEco Studio 5.1.0 Release 或以上版本
支持最低系统版本为:5.0.2(14)

#####导入SDK

- 执行安装命令

```
ohpm install meetingsdk
```

#####使用SDK

- 初始化SDK

```
getInstance();
```

- 设置运行环境

```
setEvnOnline(isOnline: boolean);//初始化云会议系统的环境,默认为:Online 如果需要切换到Beta环境,请调用此API
```

- 加入会议

```
joinConfrenceWithReq(uiContext: UIContext, pathStack: NavPathStack, req: MeetingReq,
completion: (success: boolean, error: ErrorDomain | null) => void) ;//uiContext
ui上下文用于相关弹出提示;pathStack任务栈界面跳转;MeetingReq 为参数,其中name和pcode必传,详细请参见:MeetingReq;completion
结果回调
```

- 监听会议状态

```
setMeetingStatusBlock(block: (meetingStatus: QSMeetingStatus, error: ErrorDomain | null) => void) ;//用于监听会议状态
,meetingStatus 会议状态回调
```

- 定制化会议服务

```
setCasDomain(casDomain: string, completion: (success: boolean, error: ErrorDomain | null) => void) ;//用于定制化会议服务
,casDomain:服务域名;completion 结果回调
```

- 自定义

```
    /// 是否跳过等待界面
    /// 默认关;Deafult: false
    ///
    isJumpJoin: Number;
    
    ///
    /// 入会是否开启音频
    /// 默认开;Deafult: true
    ///
    isShowAudio : Number;
    
    ///
    /// 入会是否开启视频预览
    /// 默认开;Deafult: true
    ///
    isShowVideo : Number;
    
    ///
    /// 使用链接入会
    /// 默认关;Deafult: false
    ///
    useJoinLink : Number;
```

###调用实例

```
//使用密码入会
this.code = '887-444-482-582'
//使用链接入会
// this.code = 'https://n.qsh1.cn/d/auG8PQY7nKH'

            const paramReq: MeetingReq = new MeetingReq()
            paramReq.isShowAudio = true; //默认打开音频voip
            paramReq.isShowVideo = true; //默认开启视频
            paramReq.isJumpJoin = false; //是否跳过预览
            paramReq.name = "hm sdk" // 名称
            // paramReq.userId = 22465942; //用户id,不传默认为访客
            if (this.isLinkJoinMeeitng) {
              paramReq.pcode = this.code;
              paramReq.useJoinLink = true; //标记使用链接入会
            } else {
              paramReq.pcode = this.code.replace(/-/g, "");
              console.log('pcode', paramReq.pcode)
              paramReq.useJoinLink = false;
            }
            //开始入会
            // TangInterface.getInstance()
            //   .setCasDomain("https://newcas.quanshi.com", (success: boolean, error: ErrorDomain | null) => {
            //     if (success) {
            TangInterface.getInstance()
              .joinConfrenceWithReq(this.getUIContext(), this.pathStack, paramReq,
                (success: boolean, error: ErrorDomain | null) => {
                  logWithTag('demo', '', 'joinConfrenceWithReq ', success, 'error:', error ? error.code : -1)
                  PromptActionClass.closeCustomDialogById('loading')

                  if (error || !success) {
                    return
                  }
                });
            //监听会议状态监听
            TangInterface.getInstance()
              .setMeetingStatusBlock((meetingStatus: QSMeetingStatus, error: ErrorDomain | null) => {
                logWithTag('demo', '', 'meetingStatus :', meetingStatus)
              })
```
