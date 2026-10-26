> 来源: 厂商官方文档页(T2 信源) | https://cloud.tencent.com/document/product/647/43019 | 抓取: 2026-07-17
> 注意: 单页快照,站内其余页面见来源链接

[_腾讯云_](https://cloud.tencent.com)

  * [最新活动](https://cloud.tencent.com/act)
  * 大模型
  * [产品](https://cloud.tencent.com/product)
  * [解决方案](https://cloud.tencent.com/solution)
  * [定价](https://buy.cloud.tencent.com/pricing)
  * [企业中心](https://cloud.tencent.com/act/pro/center)
  * [云市场](https://market.cloud.tencent.com)
  * [开发者](https://cloud.tencent.com/landing/developer-ecology)
  * [客户支持](https://cloud.tencent.com/act/event/service-support)
  * [合作与生态](https://cloud.tencent.com/landing/partner-ecology)
  * [了解腾讯云](https://cloud.tencent.com/about)

[](https://cloud.tencent.com/)

______

搜索

 __[实时音视频](/document/product/647) __

  * [文档中心](https://cloud.tencent.com/document/product)
  * [入门中心](https://cloud.tencent.com/guide)
  * [API 中心](https://cloud.tencent.com/document/api)
  * [SDK 中心](https://cloud.tencent.com/document/sdk)
  * [文档活动](https://cloud.tencent.com/document/act)
  * 我的反馈

[WorkBuddy|助力打造全场景智能体工作搭子 -> 点击了解 _HOT_](https://cloud.tencent.com/act/pro/workbuddy?from=30163&Is=home)

 __

[文档中心](/document/product "文档中心") _>_[实时音视频](/document/product/647 "实时音视频") _>_[TRTC SDK](/document/product/647/32164 "TRTC SDK") _>_[常见问题](/document/product/647/115281 "常见问题") _>_ Android&iOS

# Android&iOS

最近更新时间:2024-12-13 21:47:43

 __[__](https://main.qcloudimg.com/raw/document/product/pdf/647_32164_cn.pdf)

__

  * __微信扫一扫

  *  __QQ
  *  __新浪微博
  *  __复制链接

 __链接复制成功

 ___我的收藏_

## 本页目录:

  * 移动端(Android/iOS)支持哪几种系统音量模式?
  * 移动端 SDK 推流怎么设置1080p分辨率?
  * 在小程序端创建了一个房间,移动端能否进入该房间?
  * TRTC 移动端怎么实现录屏(屏幕分享)?
  * TRTC Android 端能不能支持64位的 arm64-v8a 架构?
  * 在 Android 端怎么实现动态加载 so 库?
  * 在 Android 端为什么蓝牙耳机连接成功仍然无声或外放?
  * 使用 startPlayMusic 接口播放背景音乐报错 -4001 是什么含义?
  * 在 iOS 端是否支持 Swift 集成?
  * iOS 端 SDK 与其它三方库冲突报错问题该如何解决?
  * 在 Xcode 15 集成 iOS 端 SDK 遇到编译报错、提交 AppStore 报错问题该如何解决?
  * TRTC SDK 是否支持 iOS 后台运行?
  * iOS 端是否可以监听远端离开房间的事件?
  * 手机锁屏状态、App 在后台或 App 被关闭,音视频如何拨通?
  * Android 端 App 退后台、锁屏等情况下麦克风采集无声,onWarning 回调 -1208,该如何处理?
  * 是否支持 Android 和 Web 端互通?
  * 主播和粉丝在直播过程中连麦,是否双方都可以主动发起连麦?
  * 多人音视频房间中,移动端和 Web 端是否可以进入同一房间?
  * 同一个页面中,是否可以创建 N 个 TRTC 对象,通过 N 个 UserID,分别登录到 N 个房间?
  * 如何查询 SDK 最新版本号?
  * 集成 Android 端 SDK 出现 <queries> 元素编译报错该如何解决?

### 移动端(Android/iOS)支持哪几种系统音量模式?

支持2种系统音量类型,即通话音量类型和媒体音量类型:

通话音量,手机专门为通话场景设计的音量类型,使用手机自带的回声抵消功能,音质相比媒体音量类型较差, 无法通过音量按键将音量调成零,但是支持蓝牙耳机上的麦克风。

媒体音量,手机专门为音乐场景设计的音量类型,音质相比于通话音量类型要好,通过音量按键可以将音量调成零。 使用媒体音量类型时,如果要开启回声抵消(AEC)功能,SDK 会开启内置的声学处理算法对声音进行二次处理。 在媒体音量模式下,蓝牙耳机无法使用自带的麦克风采集声音,只能使用手机上的麦克风进行声音采集。

### 移动端 SDK 推流怎么设置1080p分辨率?

1080P在 TX_Enum_Type_VideoResolution 定义是114,直接设置分辨率传枚举值即可。详情请参见 [设置画面质量](https://cloud.tencent.com/document/product/647/32236)。

**注意:**

目前 Android 和 iOS 暂不支持2K及以上的分辨率设置。

### 在小程序端创建了一个房间,移动端能否进入该房间?

可以,实时音视频支持全平台互通。

### TRTC 移动端怎么实现录屏(屏幕分享)?

**Android 端** :Version 7.2 及以上版本支持手机录屏,具体实践方法请参见 [实时屏幕分享(Android)](https://cloud.tencent.com/document/product/647/45751)。

**iOS 端** :Version 7.2 及以上版本支持 App 内录屏;Version 7.6 及以上版本支持手机录屏和 App 内录屏。具体实践方法请参见 [实时屏幕分享(iOS)](https://cloud.tencent.com/document/product/647/45750)。

### TRTC Android 端能不能支持64位的 arm64-v8a 架构?

TRTC 6.3 版本开始已提供 arm64-v8a 架构 ABI 支持。

### 在 Android 端怎么实现动态加载 so 库?

具体的操作步骤请参考 [Android 端实现动态加载 so 库](https://cloud.tencent.com/developer/article/1541517)。

### 在 Android 端为什么蓝牙耳机连接成功仍然无声或外放?

**场景1:**

**问题:** Android 12 及以上版本设备连接蓝牙后,有蓝牙图标,可是蓝牙外放或无声,换成 Android 12 以下的版本正常。

**解决方案:** 需要在 Manifest 中申请权限 `Manifest.permission.BLUETOOTH_CONNECT`,并且也需要动态申请。详情请参考 [Android 官方文档](https://developer.android.google.cn/about/versions/12/features/bluetooth-permissions?hl=zh-cn)。如果确认已经添加权限,可以查看`TRTCCloudListener.onWarning` 的 `warningCode` 是否有收到 `TXLiteAVCode.WARNING_BLUETOOTH_DEVICE_CONNECT_FAIL`,如果有,就表示被其他应用影响了,可以退出其他应用试试。

**场景2:**

**问题:** 出现蓝牙外放或无声问题后,清空后台应用后恢复正常,可能是被三方 App 影响导致。

**解决方案:** SDK 版本更新至10.7+。

**场景3:**

**问题:** 使用有类似入耳检测功能的耳机概率性出现蓝牙外放或无声。

**解决方案:** SDK 版本更新至10.3+。

**场景4:**

**问题:** 在重进房或修改音质时概率性出现蓝牙外放或无声,比如调用频繁调用 exitRoom、enterRoom、setAudioQuality。

**解决方案:** SDK 版本更新至10.3+。

### 使用 startPlayMusic 接口播放背景音乐报错 -4001 是什么含义?

startPlayMusic 接口在遇到错误时会返回以下错误码:

**-4001** :打开文件失败,如音频文件格式不支持、本地音频文件不存在、网络音频文件无法访问等。

**-4002:** 解码失败,如音频文件损坏、网络音频文件服务器无法访问等。

在遇到这类错误码时,可以尝试切换网络或者更换音频资源来解决问题。

### 在 iOS 端是否支持 Swift 集成?

支持,直接按照支持集成三方库的流程集成 SDK 即可,详情请参见 [跑通Demo(iOS&Mac)](https://cloud.tencent.com/document/product/647/32396)。

### iOS 端 SDK 与其它三方库冲突报错问题该如何解决?

详情请参见 [iOS 端 TXLiteAVSDK 与其它三方库冲突报错问题](https://cloud.tencent.com/developer/article/1499740)。

### 在 Xcode 15 集成 iOS 端 SDK 遇到编译报错、提交 AppStore 报错问题该如何解决?

出现此类问题的场景一般有以下几种。

场景1:编译时报 `duplicate symbol 'xxx'` 符号冲突错误,例如打印类似下图的信息。

  

场景2:编译成功,在特定系统版本或者特定的机型出现异常崩溃,例如 iOS 11 及以下系统的真机运行崩溃。

场景3:上传到 TestFlight 苹果检测误报“Non-public API usage”,例如下图所示的检测误报。

  

问题原因:

Xcode 15 项目中的 `-ObjC` 符号加载行为被调整为类似于 `-all_load` 的效果,导致重复加载相同符号,从而出现上述问题,解决的办法是将**Other Linker Flags** 配置为 `-ld_classic`。

### TRTC SDK 是否支持 iOS 后台运行?

支持,您只需选中当前工程项目,在 **Capabilities** 下的设置 **Background Modes** 为 **ON** ,并勾选 **Audio,AirPlay and Picture in Picture** 即可实现后台运行,详情如下图所示: 

### iOS 端是否可以监听远端离开房间的事件?

可以使用 [onRemoteUserLeaveRoom](https://liteav.sdk.qcloud.com/doc/api/zh-cn/group__TRTCCloudDelegate__ios.html#afa7d16e1e4c66d938fc2bc69f3e34c28) 来监听用户离开房间事件,且该接口仅在 VideoCall 的所有用户和 LIVE 模式下的主播离开房间时会触发回调,观众离开房间不会有回调。 

### 手机锁屏状态、App 在后台或 App 被关闭,音视频如何拨通?

实现离线接听等功能,详情请参见 [实现离线接听](https://cloud.tencent.com/document/product/647/78729#389063ee-23c7-4029-81e7-f8e60f4f0f68)。

### Android 端 App 退后台、锁屏等情况下麦克风采集无声,onWarning 回调 -1208,该如何处理?

**场景1** :被第三方应用打断(如系统电话、语音助手等)。

**解决方案** :关闭第三方应用后尝试 startLocalAudio 重启采集。

  

**场景2** :项目未启动 foregroundService 前台服务。

**解决方案** :请在项目中启动 foregroundService 前台服务,确保后台时 App 可以保持麦克风采集。

  

**场景3** :项目的 targetSdkVersion 设置为 30 及以上,或问题机型涉及到 Android 10 及更高系统版本。

**解决方案** :

若设置项目的 targetSdkVersion 30 及以上,除启动 foregroundService 外,还要求前台服务类型指定为 `android:foregroundServiceType:microphone`,以确保退后台可以保持麦克风正常采集。

若设置项目 targetSdkVersion 34 及以上,还需在 manifest 中配置 FOREGROUND_SERVICE_MICROPHONE 权限:`<uses-permission android:name="android.permission.FOREGROUND_SERVICE_MICROPHONE"/>`

### 是否支持 Android 和 Web 端互通?

支持。使用相同的 [SDKAppID](https://console.cloud.tencent.com/trtc/app),并进入同一个房间进行通话。详情请参见下列文档链接配置 Demo:

[跑通 Demo(Android)](https://cloud.tencent.com/document/product/647/32166)

[跑通 Demo(Web)](https://cloud.tencent.com/document/product/647/32398)

### 主播和粉丝在直播过程中连麦,是否双方都可以主动发起连麦?

双方都可以主动发起,观众和主播发起逻辑一致,具体操作请参见 [跑通直播模式(Android)](https://cloud.tencent.com/document/product/647/35428) 。

### 多人音视频房间中,移动端和 Web 端是否可以进入同一房间?

可以。需保证 [SDKAppID](https://console.cloud.tencent.com/trtc/app) 和房间号一致,且用户 ID 不一致。

### 同一个页面中,是否可以创建 N 个 TRTC 对象,通过 N 个 UserID,分别登录到 N 个房间?

可以。[Version 7.6 版本](https://cloud.tencent.com/document/product/647/32689) 开始支持一个用户进入多个房间了。

### 如何查询 SDK 最新版本号?

若您使用自动加载的方法,`latest.release` 为匹配最新版并进行自动加载,不需要对版本号进行修改。具体集成方法请参见 [一分钟集成 SDK](https://cloud.tencent.com/document/product/647/32173)。

当前 SDK 最新版本号可通过发布日志查看,具体请参见:

iOS & Android 端,请参见 [发布日志(App)](https://cloud.tencent.com/document/product/647/46907)。

Web 端,请参见 [发布日志(Web)](https://cloud.tencent.com/document/product/647/38958)。

Electron 端,请参见 [发布日志(Electron)](https://cloud.tencent.com/document/product/647/43117)。

### 集成 Android 端 SDK 出现 <queries> 元素编译报错该如何解决?

解决方案:

Android 11 版本新增了软件包可见性过滤条件,需要在 AndroidManifest 添加 <queries> 元素来查看系统上的应用列表,但是 <queries> 元素声明与老版本 Gradle 插件不兼容,所以需要您升级项目中的 Gradle 插件版本,具体版本请查阅 [Android Gradle 插件](https://developer.android.com/build/releases/past-releases/agp-4-0-0-release-notes?hl=zh-cn) 。

[上一篇: 小程序](/document/product/647/45532 "上一篇: 小程序")[下一篇: uni-app](/document/product/647/81008 "下一篇: uni-app")

 __中国站

  * 中文
  * [International](https://www.tencentcloud.com/)

[文档“捉虫”活动检视指定产品文档,发现和反馈有效问题,奖!](https://cloud.tencent.com/developer/article/1610407)

[API专项"捉虫"反馈API文档问题,代金券、周边好礼奖不停!](https://cloud.tencent.com/developer/article/1630768)

[文档建议,你提了吗快来使用腾讯云产品文档,提出有效建议,奖!](https://cloud.tencent.com/developer/article/1523112)

咨询
