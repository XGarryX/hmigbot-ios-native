# **快速开始实时音视频** 

本文旨在指导您如何便捷地利用阿里云资源,创建属于自己的 RTC 应用。 

## **操作流程** 

|**操作**|**说明**|
|---|---|
|步骤一:开通应用|您可在视频直播控制台,创建实时音视频应用。创建完成后,获取Appid、Appkey。 **说明** 实例名称支持中英文。 开通应用默认不产生费用,实际按照您在云上具体的使用量收费。|
|步骤二:服务器集成|获取Appid、Appkey后,服务器端根据开发语言拷⻉阿里云提供的鉴权代码。|
|步骤三:SDK集成|完成服务器端的配置后,请使用CocoaPods(对于iOS)或Maven(对于Android)来集成并获取SDK。 iOS pod 'AliVCSDK_ARTC', 'x.x.x' Android com.aliyun.aio:AliVCSDK_ARTC:x.x.x Windows 下载请参见SDK下载 Web 参见快速使用阿里云ARTC Web SDK Linux 下载请参见SDK下载 ARTC Linux SDK Java快速接入 ARTC Linux SDK Python快速接入 ARTC Linux SDK C++快速接入 ARTC Linux SDK Golang快速接入|

## **步骤一:开通应用** 

1. 登录视频直播控制台。 

2. 在左侧导航栏单击 **直播+ > 实时音视频 > 应用管理** 。 

3. 单击 **创建应用** 。 

4. 填写自定义的 **实例名称** ,勾选 **服务协议** 后,点击 **立即购买。** 

5. 提示开通成功后,刷新 **应用管理** 页面,即可查看您新建的实时音视频应用。 

##### **说明** 

创建应用默认不产生费用 , 实际按照您具体云上用量后付费。更多信息,请参见实时音视频费用。 

## **步骤二:服务器集成** 

1 将阿里云提供的鉴权代码集成到您的服务器端环境中,以 Java 语言单参数入会为例,详情请参见 Token 鉴权。 

1. 将阿里云提供的鉴权代码集成到您的服务器端环境中,以 Java 语言单参数入会为例,详情请参见 Token 鉴权。 

2. 服务器端提供 API ,方便移动应用( APP )端调用。 

## **步骤三:SDK集成** 

根据具体的业务需求,可以选择适用于互动娱乐场景的 **互动模式** ,或者适合一对一或一对多广播的 **通信模式** 。正确的模式选择 能够确保用户体验的流畅性并有效利用网络资源。您可以根据业务场景选择合适的模式。 

|**模式**|**推流**|**拉流**|**模式介绍**|
|---|---|---|---|
|互动模式|有角色限制,只有被赋予主 播身份的用户可以进行推流 操作。 在整个过程中,参与者可以 灵活地切换角色。|无角色限制,所有参与者都 拥有拉流的权限。|在互动模式中,主播加入或退出会议、以及开始推送 直播流的事件都会实时通知给观众端,确保观众能够 及时了解主播的动态。反之,观众的任何活动不会通 告给主播,保持了主播的直播流程不受干扰。 在互动模式下,主播角色负责进行直播互动,而观众 角色则主要接收内容,通常不参与直播的互动过程。 若业务需求未来可能发生变化,导致不确定是否需要 支持观众的互动参与,建议默认采用互动模式。这种 模式具有较高的灵活性,可通过调整用户角色权限来 适应不同的互动需求。|
|通信模式|无角色限制,所有参与者都拥 有推流权限。|无角色限制,所有参与者都 拥有拉流的权限。|在通信模式下,会议参与者能够相互察觉到彼此的存 在。 该模式虽然没有区分用户角色,但实际上与互动模式 中的主播角色相对应;目的是为了简化操作,让用户 能够通过调用更少的API来实现所需的功能。|

### **1. 工程化配置** 

#### **Android端** 

##### 推荐使用 Maven 仓库来集成所需的依赖库。 

##### 1. 在根级别 build.gradle 文件中添加 Maven 仓库地址。 

allprojects { repositories { google() jcenter() // 添加 RTC 需要的 Maven 地址 maven { url "https://maven.aliyun.com/nexus/content/repositories/releases" } } } 

##### 2. 在项目的 app/build.gradle 文件中,添加以下代码行。 

// 引入依赖的实时通信 SDK (RTC SDK) implementation 'com.aliyun.aio:AliVCSDK_ARTC:${latest version}' 

3. 在 app/src/main/AndroidManifest.xml 文件中添加如下代码,获取相应的设备权限。 

<uses-permission android:name="android.permission.CAMERA" /> 

<uses-permission android:name="android.permission.RECORD_AUDIO" /> 

<uses-permission android:name="android.permission.INTERNET" /> 

<uses-permission android:name="android.permission.WRITE_EXTERNAL_STORAGE" /> 

<!-- Request legacy Bluetooth permissions on older devices. --> 

<uses-permission 

android:name="android.permission.BLUETOOTH" android:maxSdkVersion="30" /> 

<uses-permission 

android:name="android.permission.BLUETOOTH_ADMIN" android:maxSdkVersion="30" /> 

<!-- Needed only if your app communicates with already-paired Bluetooth devices. --> <uses-permission android:name="android.permission.BLUETOOTH_CONNECT" /> <uses-permission android:name="android.permission.CHANGE_NETWORK_STATE" /> <uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" /> <uses-permission android:name="android.permission.MODIFY_AUDIO_SETTINGS" /> <uses-permission android:name="android.permission.READ_PHONE_STATE" /> 

<uses-permission android:name="android.permission.WRITE_SETTINGS" tools:ignore="ProtectedPermissions" /> 

<uses-permission android:name="android.permission.FOREGROUND_SERVICE" /> 

##### **说明** 

##### **其中部分权限需要动态申请, 需要动态申请的权限包含:** 

Manifest.permission.CAMERA 

Manifest.permission.WRITE_EXTERNAL_STORAGE Manifest.permission.RECORD_AUDIO Manifest.permission.READ_EXTERNAL_STORAGE 

- **当Android系统版本>=12(API_LEVEL>=31) 时, 需要额外动态申请以下权限:** Manifest.permission.BLUETOOTH_CONNECT 

##### 4. (可选)添加混淆规则。 

-keep class com.aliyun.allinone.** { *; } -keep class com.aliyun.rts.network.AliHttpTool { *; } -keep class com.aliyun.common.AlivcBase { *; } -keep class com.huawei.multimedia.alivc.** { *; } -keep class com.alivc.rtc.** { *; } -keep class com.alivc.component.** { *; } -keep class org.webrtc.** { *; } 

5. 配置完成。 

#### **iOS端** 

推荐使用 CocoaPods 集成。 

1. 在终端窗口中输入以下命令,安装 CocoaPods 。 

##### **重要** 

在开始使用 CocoaPods 之前,请确保您的 Mac 已经安装了 Ruby 环境。 

sudo gem install cocoapods 

2. 进入项目所在路径,在终端窗口中输入以下命令,创建 Podfile 文件。 

pod init 

3. 编辑 Podfile 文件,添加 RTC SDK 依赖。 

pod 'AliVCSDK_ARTC', '~> ${latest version}' 

4. 在终端窗口中输入以下命令更新项目中的 CocoaPods 依赖库。执行完这个命令后,将生成一个包含集成 SDK 的 .xcworkspace 后缀的工程文件,双击该文件即可更新并安装 SDK 。 

pod update 

5. 添加请求权限。 

**重要** 请务必添加录音权限和相机权限。 

##### i. 在 **Info.plist** 文件中添加摄像头和麦克风权限 **Privacy - Camera Usage Description** 、 **Privacy - Microphone Usage Description** 。 

- ii. 开启音频后台采集模式。如图所示,勾选 **Audio,AirPlay,and Picture in Picture** 即可。 

##### 6. 找到 **Enable Bitcode** 选项,并将其设置为 **No** 来关闭 Bitcode 。 

#### **Windows端** 

推荐使用 VS2015 进行集成。 

##### 2. 添加运行库路径。 

## **Linux端** 

Java 准备工作 Python 准备工作 C++ 准备工作 Golang 准备工作 

#### **Harmony端** 

#### 1. **环境准备** 

在开始集成 阿里音视频 SDK 前,请确保开发环境满足以下要求: 

- **已联系华为商务人员,签署合作计划,开通相关权限** ,获取 DevEco Studio 5.0.3.900 Release 或以上版本。 

- 获取配套 API Version 12 的 HarmonyOS NEXT SDK 或以上版本。 

- 获取配套 API Version 12 的 HarmonyOS NEXT 5.0.0.102 操作系统或以上版本,支持音视频的鸿蒙设备,且已开 启 “ 允许调试 ” 选项。 

如果需要使用真机调试,请参考 鸿蒙官网文档 进行配置。 

- 鸿蒙设备已经连接到 Internet 。 

- 已 注册华为开发者账号 并完成实名认证。 

#### 2. **工程化配置** 

#### i. **手动引入** 

##### 下载 AliVCSDK_ARTC-6.11.0-Beta.har 包,放到工程 libs 中。在工程中配置引用: 

"dependencies": { 

"@aliyun_video_cloud/alivcsdk_artc":"file:./libs/AliVCSDK_ARTC-6.11.0-beta.har", } 

#### ii. **ohpm引入** 

在工程中配置: 

"dependencies": { "@aliyun_video_cloud/alivcsdk_artc":"6.11.0-beta", } 

##### 运行命令: 

ohpm install @aliyun_video_cloud/alivcsdk_artc 

### **2. SDK集成** 

#### **1、初始化RTC引擎及回调注册** 

##### **重要** 

SDK 设计为在遇到异常情况时,首先尝试内部重试机制以恢复正常状态。对于那些 SDK 无法自行解决的错误,会通过明 确定义的回调接口( API )通知到您的应用程序。 

|**异常发生原因**|**回调及参数**|**解决方案**|**说明**|
|---|---|---|---|
|鉴权失败|onJoinChannelResult回 调中的result返回 AliRtcErrJoinBadToken|发生错误时App需要检查Token是 否正确。|在用户主动调用API时,若鉴权失败,系 统将在调用API的回调中返回鉴权失败的 错误信息。|
|鉴权将要过期|onWillAuthInfoExpire|发生该异常时App需要重新获取最 新的鉴权信息后,再调用 refreshAuthInfo刷新鉴权信息。|鉴权过期错误在两种情况下出现:用户调 用API或程序执行期间。因此,错误反馈 将通过API回调或通过独立的错误回调通 知。|

|鉴权过期|onAuthInfoExpired|发生该异常时App需要重新入会。|鉴权过期错误在两种情况下出现:用户调 用API或程序执行期间。因此,错误反馈 将通过API回调或通过独立的错误回调通 知。|
|---|---|---|---|
|网络连接异常|onConnectionStatusCha nge回调返回 AliRtcConnectionStatus Failed。|发生该异常时APP需要重新入会。|SDK具备一定时间断网自动恢复能力,但 若断线时间超出预设阈值,会触发超时并 断开连接。此时,App应检查网络状态并 指导用户重新加入会议。|
|被踢下线|onBye|AliRtcOnByeUserReplaced: 当发生该异常时排查用户userid 是否相同。 AliRtcOnByeBeKickedOut: 当发生该异常时,表示被业务踢 下线,需要重新入会。 AliRtcOnByeChannelTermin ated:当发生该异常时,表示 房间被销毁,需要重新入会。|RTC服务提供了管理员可以主动移除参与 者的功能。|
|本地设备异常|onLocalDeviceException|发生该异常时App需要检测权限、 设备硬件是否正常。|RTC服务支持设备检测和异常诊断的能 力;当本地设备发生异常时,RTC服务会 通过回调的方式通知客户本地设备异常, 此时,若SDK无法自行解决问题,则App 需要介入以查看设备是否正常。|

#### **Android平台** 

private void createEngine() { mAliRtcEngine = AliRtcEngine.getInstance(getApplicationContext()); mAliRtcEngine.setRtcEngineEventListener(new AliRtcEngineEventListener() { 

- /* SDK 与服务器的链接状态通知,务必处理链接失败的情况 */ 

@Override public void onConnectionStatusChange(AliRtcEngine.AliRtcConnectionStatus aliRtcConnectionStatus, AliRtcEngine.AliRtcConnectionStatusChangeReason aliRtcConnectionStatusChangeReason) { super.onConnectionStatusChange(aliRtcConnectionStatus, aliRtcConnectionStatusChangeReason); if (aliRtcConnectionStatus == AliRtcEngine.AliRtcConnectionStatus.AliRtcConnectionStatusFailed) { /* TODO: 务必处理;建议业务提示客户,此时 SDK } else { /* TODO: 可选处理;增加业务代码,一般用于数据统计、 UI 变化 */ } } 

务必处理;建议业务提示客户,此时 SDK 内部已经尝试了各种恢复策略已经无法继续使用时才会上报 */ 

- /* SDK 尝试控制本地设备异常 */ 

@Override public void OnLocalDeviceException(AliRtcEngine.AliRtcEngineLocalDeviceType aliRtcEngineLocalDeviceType, AliRtcEngine.AliRtcEngineLocalDeviceExceptionType aliRtcEngineLocalDeviceExceptionType, String s) { super.OnLocalDeviceException(aliRtcEngineLocalDeviceType, aliRtcEngineLocalDeviceExceptionType, s); /* TODO: 务必处理;建议业务提示客户错误,此时 SDK 内部已经尝试了各种恢复策略已经无法继续使用时才会上报 */ } 

@Override public void onJoinChannelResult(int result, String channel, String userId, int elapsed) { super.onJoinChannelResult(result, channel, userId, elapsed); 

/* TODO: 可选处理;增加业务代码,一般用于数据统计、 UI 变化 */ Log.i(TAG, "onJoinChannelResult result=" + result + ",channel=" + channel + ",userId=" + u serId + ",elapsed=" + elapsed); } @Override public void onLeaveChannelResult(int result, AliRtcEngine.AliRtcStats stats) { super.onLeaveChannelResult(result, stats); Log.i(TAG, "onLeaveChannelResult result=" + result); } }); mAliRtcEngine.setRtcEngineNotify(new AliRtcEngineNotify() { 

/* 鉴权距离过期还有 30s 时会回调,务必进行鉴权时间刷新 */ @Override public void onAuthInfoWillExpire() { super.onAuthInfoWillExpire(); /* TODO: 务必处理;业务触发重新获取当前 channel , user 的鉴权信息,然后设置 refreshAuthInfo 即可 */ } /* 业务可能会触发踢人的动作,所以这个地方也需要处理 */ @Override public void onBye(int code) { super.onBye(code); /* TODO: 建议业务根据自己的场景,进行对应的处理 */ } @Override public void onRemoteUserOnLineNotify(String uid, int elapsed) { super.onRemoteUserOnLineNotify(uid, elapsed); Log.i(TAG, "onRemoteUserOnLineNotify uid=" + uid + ",elapsed=" + elapsed); } @Override public void onRemoteUserOffLineNotify(String uid, AliRtcEngine.AliRtcUserOfflineReason aliRtcU serOfflineReason) { super.onRemoteUserOffLineNotify(uid, aliRtcUserOfflineReason); Log.i(TAG, "onRemoteUserOnLineNotify uid=" + uid + ",aliRtcUserOfflineReason=" + aliRtcUserOfflineReason); } @Override public void onRemoteTrackAvailableNotify(String uid, AliRtcEngine.AliRtcAudioTrack aliRtcAudio Track, AliRtcEngine.AliRtcVideoTrack aliRtcVideoTrack) { super.onRemoteTrackAvailableNotify(uid, aliRtcAudioTrack, aliRtcVideoTrack); Log.i(TAG, "onRemoteUserOnLineNotify uid=" + uid + ",aliRtcAudioTrack=" + aliRtcAudioTrack + ",aliRtcVideoTrack=" + aliRtcVideoTrack); mMainHandler.post(new Runnable() { @Override public void run() { if (aliRtcVideoTrack == AliRtcEngine.AliRtcVideoTrack.AliRtcVideoTrackCamera || aliRtcVideoTrack == AliRtcEngine.AliRtcVideoTrack.AliRtcVideoTrackBoth) { AliRtcEngine.AliRtcVideoCanvas remote_canvas = new AliRtcEngine.AliRtcVideoCanvas(); SurfaceView remoteView = mAliRtcEngine.createRenderSurfaceView(mContext); if (remoteView != null) { remoteView.setZOrderOnTop(true); remoteView.setZOrderMediaOverlay(true); } remote_canvas.view = remoteView; mLocalSurfaceContainer.addView(remote_canvas.view, new 

FrameLayout.LayoutParams( 

findViewById(R.id.local_surface_container).getWidth()/4, findViewById(R.id.local_surface_container).getHeight()/4)); mAliRtcEngine.setRemoteViewConfig(remote_canvas,uid,AliRtcEngine.AliRtcVideoTrack.AliRtcVideoTrackCamera } else { mAliRtcEngine.setRemoteViewConfig(null, uid, AliRtcEngine.AliRtcVideoTrack.AliRtcVideoTrackCamera); } } }); } }); } 

#### **iOS平台** 

- (AliRtcEngine *)engine{ if (!_engine) { NSString *extras = @""; /* 构造引擎并传入 delegate */ _engine = [AliRtcEngine sharedInstance:self extras:extras]; } 

return _engine; } 

- #pragma mark - "Delegates of engine" 

- /* 鉴权距离过期还有 30s 时会回调,务必进行鉴权时间刷新 */ 

- (void)onAuthInfoWillExpire{ /* TODO: 务必处理;业务触发重新获取当前 channel\user 的鉴权信息,然后设置 refreshAuthInfo 即可 */ } 

- /* SDK 与服务器的链接状态通知,务必处理链接失败的情况 */ 

- (void)onConnectionStatusChange:(AliRtcConnectionStatus)status reason: 

- (AliRtcConnectionStatusChangeReason)reason { 

if (status == AliRtcConnectionStatusFailed) { 

/* TODO: 务必处理;建议业务提示客户,此时 SDK 内部已经尝试了各种恢复策略已经无法继续使用时才会上报 */ } else { /* TODO: 可选处理;增加业务代码,一般用于数据统计、 UI 变化 */ 

} } 

- /* SDK 尝试控制本地设备异常 */ 

- (void)onLocalDeviceException:(AliRtcLocalDeviceType)deviceType exceptionType: 

- (AliRtcLocalDeviceExceptionType)exceptionType message:(NSString *_Nullable)msg { 

- /* TODO: 务必处理;建议业务提示客户错误,此时 SDK 内部已经尝试了各种恢复策略已经无法继续使用时才会上报 */ } 

- /* 业务可能会触发踢人的动作,所以这个地方也需要处理 */ 

- /* 业务可能会触发踢人的动作,所以这个地方也需要处理 */ 

- (void)onBye:(int)code { 

- /* TODO: 建议业务根据自己的场景,进行对应的处理 */ } 

- /* 远端推流通知,自动订阅时这个时候设置窗口黑屏时间和首帧可以兼顾 */ 

- (void)onRemoteTrackAvailableNotify:(NSString *_Nonnull)uid audioTrack:(AliRtcAudioTrack)audioTrack v ideoTrack:(AliRtcVideoTrack)videoTrack { 

   - /* TODO: 务必处理;给 SDK 设置一个视频渲染窗口 */ 

   - dispatch_async(dispatch_get_main_queue(), ^{ 

   - if (videoTrack & AliRtcVideoTrackCamera) { 

AliVideoCanvas *canvas = [[AliVideoCanvas alloc] init]; canvas.view = self.remoteRenderView; canvas.renderMode = AliRtcRenderModeAuto; [self.engine setRemoteViewConfig:canvas uid:uid forTrack:AliRtcVideoTrackCamera]; } else { /* 这里清空远端用户的渲染窗口,但是有可能远端用户直接离会 */ [self.engine setRemoteViewConfig:nil uid:uid forTrack:AliRtcVideoTrackCamera]; } }); } - (void)onRemoteUserOffLineNotify:(NSString *)uid offlineReason:(AliRtcUserOfflineReason)reason { dispatch_async(dispatch_get_main_queue(), ^{ /* 这里也清空远端用户的渲染窗口 */ [self.engine setRemoteViewConfig:nil uid:uid forTrack:AliRtcVideoTrackBoth]; }); } - (void)onJoinChannelResult:(int)result channel:(NSString *)channel userId:(NSString *)userId elapsed:(int)elapsed { /* TODO: 可选处理;增加业务代码,一般用于数据统计、 UI 变化 */ } - (void)onLeaveChannelResult:(int)result stats:(AliRtcStats)stats { /* TODO: 可选处理;增加业务代码,一般用于数据统计、 UI 变化 */ } 

#### **Windows平台** 

class AliEngineEventListenerImpl : public AliEngineEventListener { public: AliEngineEventListenerImpl(AliEngine* engine, HWND hWnd) { mAliRtcEngine = engine; mHWnd = hWnd; }; virtual AliEngineEventListenerImpl() {}; virtual void OnConnectionStatusChange(int status, int reason) override { if (status == AliEngineConnectionFailed) { /* TODO: 务必处理;建议业务提示客户,此时 SDK 内部已经尝试了各种恢复策略已经无法继续使用时才会上报 */ } else { /* TODO: 可选处理;增加业务代码,一般用于数据统计、 UI 变化 */ } }; virtual void OnLocalDeviceException(AliEngineLocalDeviceType deviceType, AliEngineLocalDeviceExceptionType exceptionType, const char* msg) override { /* TODO: 务必处理;建议业务提示客户错误,此时 SDK 内部已经尝试了各种恢复策略已经无法继续使用时才会上报 */ }; virtual void OnJoinChannelResult(int result, const char *channel, const char *userId, int elapsed) override { /* TODO: 可选处理;增加业务代码,一般用于数据统计、 UI 变化 */ }; virtual void OnLeaveChannelResult(int result, AliEngineStats stats) override { }; virtual void OnAuthInfoWillExpire() override { /* TODO: 务必处理;业务触发重新获取当前 channel , user 的鉴权信息,然后设置 refreshAuthInfo 即可 */ 

}; 

virtual void OnBye(int code) override { /* TODO: 建议业务根据自己的场景,进行对应的处理 */ }; 

virtual void OnRemoteUserOnLineNotify(const char *uid, int elapsed) override { }; virtual void OnRemoteUserOffLineNotify(const char *uid, AliEngineUserOfflineReason reason) overrid e { }; 

```arkts
virtual void OnRemoteTrackAvailableNotify(const char *uid, AliEngineAudioTrack audioTrack, AliEngineVideoTrack videoTrack) { AliEngineVideoCanvas remote_canvas; if (videoTrack == AliEngineVideoTrackCamera || videoTrack == AliEngineVideoTrackBoth) { RECT rect; ::GetWindowRect(mHWnd, &rect); remote_canvas.displayView = remoteView; remote_canvas.renderMode = AliEngineRenderModeAuto; mAliRtcEngine->SetRemoteViewConfig(remote_canvas,uid,AliEngineVideoTrackCamera); } else { mAliRtcEngine->SetRemoteViewConfig(remote_canvas, uid, AliEngineVideoTrackCamera); } } private: AliEngine* mAliRtcEngine = nullptr; /* windows 窗口句柄 */ HWND mHWnd; }; private: void createEngine() { mAliRtcEngine = AliRtcEngine.Create(""); mLisenter = new AliEngineEventListenerImpl(mAliRtcEngine, mHWnd); mAliRtcEngine->SetEngineEventListener(mLisenter); } 
```

## **Linux 平台** 

Java 初始化 SDK Pyhon 初始化 SDK C++ 初始化 SDK Golang 初始化 SDK 

#### **Harmony端** 

this.rtcSdk = AliRtcEngine.getInstance(NULL, getContext(this)); this.engineEventListener: AliRtcEngineEventListener = new AliRtcEngineEventListener(); this.engineEventListener .onRemoteUserOnline((uid: string, elapsed: boolean)=> { // 有人入会 }) .onRemoteUserOffline((uid:string, reason: AliRtcUserOfflineReason)=> { / 有人离会 }) .onJoinChannel((result : number, channel : string, userId : string, elapsed : number)=> { // 入会时触发 }) .onLeaveChannel((result : number, stat : AliRtcStats)=> { // 离会时触发 }) .onBye((code : AliRtcOnByeType)=> { // 被服务器踢出或者频道关闭时回调 }) .onOccurError((error : number, msg : string)=> { // 发生错误时回调 }) .onConnectionStatusChange((status : number, reason : number)=> { // 网络连接变化时回调 }) ; this.rtcSdk?.setRtcEngineEventListener(this.engineEventListener); 

#### **2、设置入会前的参数** 

##### **重要** 

在互动模式和主播角色设定下, SDK 默认会自动推送本地音视频流,并接收其他主播的音视频流。 在互动模式和观众角色设定下, SDK 不会推送本地的音视频流,但会接收其他主播的音视频流。 SDK 默认是自动推拉流模式,用户也可以关闭自动推拉流模式。 

#### **Android平台** 

private void initEngineBeforeJoin() { /* 可选:入会前的参数设置 */ 

mAliRtcEngine.setChannelProfile(AliRtcEngine.AliRTCSdkChannelProfile.AliRTCSdkInteractiveLive); mAliRtcEngine.setClientRole(AliRtcEngine.AliRTCSdkClientRole.AliRTCSdkInteractive); /* 设置音频的属性 */ 

mAliRtcEngine.setAudioProfile(AliRtcEngine.AliRtcAudioProfile.AliRtcEngineStereoHighQualityMode, AliRt cEngine.AliRtcAudioScenario.AliRtcSceneMusicMode); 

可选:摄像头预览 , 不设置也会进行推流 */ 

AliRtcEngine.AliRtcVideoCanvas canvas = new AliRtcEngine.AliRtcVideoCanvas(); canvas.view = mAliRtcEngine.createRenderSurfaceView(mContext); mLocalSurfaceContainer.removeAllViews(); if (canvas.view != null) { mLocalSurfaceContainer.addView(canvas.view, new FrameLayout.LayoutParams(FrameLayout.LayoutParams.MATCH_PARENT, FrameLayout.LayoutParams.MATCH_PARENT)); } mAliRtcEngine.setLocalViewConfig(canvas, AliRtcEngine.AliRtcVideoTrack.AliRtcVideoTrackCamera); } 

#### **iOS平台** 

- (void)initBeforeJoin { /* 可选:入会前的参数设置 */ 

[self.engine setChannelProfile:AliRtcInteractivelive]; [self.engine setClientRole:AliRtcClientRoleInteractive]; /* 设置音频的属性 */ 

[self.engine setAudioProfile:AliRtcEngineStereoHighQualityMode audio_scene:AliRtcSceneMusicMode]; /* 可选:摄像头预览 , 不设置也会进行推流 */ AliVideoCanvas *canvas = [[AliVideoCanvas alloc] init]; canvas.view = self.previewView; canvas.renderMode = AliRtcRenderModeAuto; [self.engine setLocalViewConfig:canvas forTrack:AliRtcVideoTrackCamera]; return; } 

#### **Windows平台** 

private: void initEngineBeforeJoin() { /* 可选:入会前的参数设置 */ 

mAliRtcEngine->SetChannelProfile(AliEngineInteractiveLive); mAliRtcEngine->SetClientRole(AliEngineClientRoleInteractive); /* 设置音频的属性 */ mAliRtcEngine->SetAudioProfile(AliEngineBasicQualityMode, AliEngineSceneMusicMode); 

/* 可选:摄像头预览 , 不设置也会进行推流 */ 

AliEngineVideoCanvas canvas; /* windows 窗口句柄 */ canvas.view = mHWnd; mAliRtcEngine.setLocalViewConfig(canvas, AliEngineVideoTrackCamera); } 

## **Linux 平台** 

Java 设置入会参数 Python 设置入会参数 C++ 设置入会参数 

Golang 设置入会参数 

#### **Harmony端** 

initEngineBeforeJoin = (surfaceId: string) => { 

let encoderConfig : AliRtcVideoEncoderConfiguration = new AliRtcVideoEncoderConfiguration(); encoderConfig.dimensions = new AliRtcVideoDimensions(); 

encoderConfig.dimensions.width = 480 

encoderConfig.dimensions.height = 640 

encoderConfig.frameRate = AliRtcFrameRate.AliEngineFrameRateFps15 

this.rtcSdk?.setVideoEncoderConfiguration(encoderConfig) 

let profile : AliRtcChannelProfile = AliRtcChannelProfile.AliEngineInteractiveLive 

if (this.mainPageParams.interactive_mode == 0) { 

profile = AliRtcChannelProfile.AliEngineCommunication 

} else if (this.mainPageParams.interactive_mode == 2) { 

profile = AliRtcChannelProfile.AliEngineInteractiveWithLowLatencyLive 

this.rtcSdk?.setChannelProfile(profile); 

this.rtcSdk?.setClientRole(this.mainPageParams.is_anchor ? 

AliRtcClientRole.AliEngineClientRoleInteractive : AliRtcClientRole.AliEngineClientRoleLive); 

this.localVideoCanvas.surfaceId = surfaceId; 

this.rtcSdk?.setLocalViewConfig(this.localVideoCanvas, this.componentController, AliRtcVideoTrack.AliEngineVideoTrackCamera); 

} 

#### **3、入会** 

##### **重要** 

入会后会按照入会前设定的参数执行相应的推流和拉流。 

SDK 默认会自动推拉流,以减少客户端需要调用的 API 数量。 

#### **Android平台** 

initEngineBeforeJoin(); mAliRtcEngine.joinChannel(" 您的鉴权信息 ", null, null, "testUserName"); 

#### **iOS平台** 

[self initBeforeJoin]; /* 这个地方 channlid,userid 完全取决于服务器下发的值, app 不感知 */ [self.engine joinChannel:@" 您的鉴权信息 " channelId:nil userId:nil name:@"testUserName" onResultWithUserId:nil]; 

#### **Windows平台** 

initEngineBeforeJoin(); mAliRtcEngine->joinChannel(" 您的鉴权信息 ", null, null, "testUserName"); 

## **Linux平台** 

Java 入会 Python 入会 C++ 入会 

Golang 入会 

#### **Harmony端** 

this.initEngineBeforeJoin(); this.rtcSdk?.joinChannel(" 您的鉴权信息 ", null, null, "testUserName"); 

#### **4、切换角色** 

##### **重要** 

- 当用户从主播角色转换到观众角色时(通常被称作 “ 下麦 ” ),系统将停止推送本地的音视频流,已经订阅的音视频流 不受影响。 

- 当用户从观众播角色转换到主播角色时(通常被称作 “ 上麦 ” ),系统将会推送本地的音视频流,已经订阅的音视频流 不受影响。 

#### **Android平台** 

/* TODO: 根据业务设置角色 */ 

/* 设置参与互动角色(主播角色) */ 

mAliRtcEngine.setClientRole(AliRtcEngine.AliRTCSdkClientRole.AliRTCSdkInteractive); /* 设置观看角色(观众角色) */ 

mAliRtcEngine.setClientRole(AliRtcEngine.AliRTCSdkClientRole.AliRTCSdkLive); 

#### **iOS平台** 

/* TODO: 根据业务设置角色 */ /* 设置参与互动角色(主播角色) */ 

[self.engine setClientRole:AliRtcClientRoleInteractive]; /* 设置观看角色(观众角色) */ 

[self.engine setClientRole:AliRtcClientRolelive]; 

#### **Windows平台** 

/* TODO: 根据业务设置角色 */ /* 设置参与互动角色(主播角色) */ 

mAliRtcEngine->SetClientRole(AliEngineClientRoleInteractive); /* 设置观看角色(观众角色) */ 

mAliRtcEngine->SetClientRole(AliEngineClientRoleLive); 

## **Linux平台** 

Java 切换角色 

Python 切换角色 C++ 切换角色 Golang 切换角色 

#### **Harmony端** 

/* TODO: 根据业务设置角色 */ /* 设置参与互动角色(主播角色) */ 

this.rtcSdk?.setClientRole(AliRtcClientRole.AliEngineClientRoleInteractive); /* 设置观看角色(观众角色) */ this.rtcSdk?.setClientRole(AliRtcClientRole.AliEngineClientRoleLive); 

##### **5、离会** 

#### **Android平台** 

mAliRtcEngine.leaveChannel(); 

#### **iOS平台** 

[self.engine leaveChannel]; 

#### **Windows平台** 

mAliRtcEngine->LeaveChannel(); 

## **Linux平台** 

Java 离会 

Python 离会 C++ 离会 Golang 离会 

#### **Harmony端** 

this.rtcSdk?.leaveChannel(); 

#### **6、销毁引擎** 

#### **Android平台** 

mAliRtcEngine.destroy(); mAliRtcEngine = null; 

#### **iOS平台** 

[AliRtcEngine destroy]; 

#### **Windows平台** 

mAliRtcEngine->Destroy(); mAliRtcEngine = nullptr; 

## **Linux平台** 

Java 销毁引擎 Python 销毁引擎 C++ 销毁引擎 Golang 销毁引擎 

#### **Harmony端** 

AliRtcEngine.destroyInstance(); this.rtcSdk? = null; 

#### **效果展示** 

集成上述代码后,将得到如下结果,您也可以根据业务进行相应的调整。 

#### **Android平台** 

#### **ios平台** 

#### **Windows平台** 

#### **其他API** 

更多 API 的调用,详情请参见实时音视频 ARTC SDK 。
