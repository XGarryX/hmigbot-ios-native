百家云-开发文档 

https://docs.baijiayun.com/rtc/quick/run_demo/HarmonyOS.html 

#### **开发者中心文档中心 (https://www.baijiayun.com/brtcDeveloperCenter) 下载中心 (/resources/docs/open/download/tpl.html)** 实时音视频 (/rtc/index.html) > 快速入门 > 一分钟跑通 DEMO (/rtc/quick/run_demo/Android.html) 

**www.baijiayun.cfrom=brtc) 注册 (https://auth?/ 登录** 

##### 实时音视频 

# **一分钟跑通 DEMO** 

产品介绍 性能数据 (/rtc/performance/ performance.html) Android (/rtc/quick/run_demo/Android.html) iOS (/rtc/quick/run_demo/iOS.html) Web (/rtc/quick/run_demo/Web.html) 发版说明 (/rtc/release/ uni-app (/rtc/quick/run_demo/uniapp.html) HarmonyOS (/rtc/quick/run_demo/HarmonyOS.html) Android.html) 快速入门 BRTC HarmonyOS demo 程序是您快速了解和熟悉 BRTC HarmonyOS SDK 的最佳途径。本文主要介绍如何下载 BRTC HarmonyOS demo 程序并运行。 一分钟跑通 DEMO (/rtc/ quick/run_demo/Android.html) 

一分钟集成 SDK (/rtc/quick/ 注:由于 HarmonyOS 系统及其周边开发环境、工具迭代更新速度很快,本文部分超链接如果打开异常,请先自行至华为开发者中心 run_sdk/Android.html) (https://developer.huawei.com/) 查找最新页面。 实现一个音视频直播 (/rtc/ quick/run_live/Android.html) **前提条件** 

基础功能 

已注册开通了 BRTC 服务 

进阶功能 已经拥有华为开发者账号(没有的话请先注册 (https://developer.huawei.com/consumer/cn/doc/start/registration-and客户端 API verification-0000001053628148)) 服务端 API 一部已经更新为 HarmonyOS NEXT 版本的真机( **BRTC HarmonyOS SDK 不提供模拟器版本** ) 常见问题 **环境要求** 最佳实践 

DevEco Studio (https://developer.huawei.com/consumer/cn/deveco-studio/) 最新版本 

### **创建新的应用** 

在百家云后台 -> BRTC -> 首页,创建对应的应用 

第1页 共8页 

2025/2/12 18:53 

百家云-开发文档 

https://docs.baijiayun.com/rtc/quick/run_demo/HarmonyOS.html 

 (https://www.baijiayun.com/brtcDeveloperCenter) 下载中心 (/resources/docs/open/download/tpl.html) (/resources/docs/open/download/tpl.html) www.baijiayun.cfrom=brtc)from=brtc) 注册 (https://auth?/auth?// 登录

**开发者中心文档中心 (https://www.baijiayun.com/brtcDeveloperCenter) 下载中心 (/resources/docs/open/download/tpl.html) (/resources/docs/open/download/tpl.html) www.baijiayun.cfrom=brtc)from=brtc) 注册 (https://auth?/auth?// 登录** 实时音视频 产品介绍 性能数据 (/rtc/performance/ performance.html) 发版说明 (/rtc/release/ Android.html) 快速入门 一分钟跑通 DEMO (/rtc/ quick/run_demo/Android.html) 一分钟集成 SDK (/rtc/quick/ run_sdk/Android.html) 实现一个音视频直播 (/rtc/ quick/run_live/Android.html) 基础功能 进阶功能 客户端 API 服务端 API 常见问题 最佳实践 

第2页 共8页 

2025/2/12 18:53 

百家云-开发文档 

https://docs.baijiayun.com/rtc/quick/run_demo/HarmonyOS.html 

开发者中心文档中心 (https://www.baijiayun.com/brtcDeveloperCenter) 下载中心 (/resources/docs/open/download/tpl.html) www.baijiayun.cfrom=brtc) 注册 (https://auth?/ 登录
实时音视频
产品介绍
性能数据  (/rtc/performance/
performance.html)
发版说明  (/rtc/release/
Android.html)
快速入门
一分钟跑通 DEMO (/rtc/
quick/run_demo/Android.html)
一分钟集成 SDK (/rtc/quick/
run_sdk/Android.html)
实现一个音视频直播  (/rtc/
quick/run_live/Android.html)
基础功能

一分钟跑通 DEMO (/rtc/ quick/run_demo/Android.html) 一分钟集成 SDK (/rtc/quick/ run_sdk/Android.html) 实现一个音视频直播 (/rtc/ quick/run_live/Android.html) 基础功能 进阶功能 客户端 API **生成 Sig** 服务端 API 常见问题 Sig 是 App 用户在加入房间时采用的一种安全的鉴权方式,目的是为了阻止恶意攻击者盗用您的云服务使用权。生成 Sig 文档 (/brtc/ auth/sig/sig.html) 最佳实践 为了快速跑通 DEMO 您可以先使用百家云后台生成的临时 Sig 做测试 

#### 建议您在生成临时 Sig 的时候在 userID 后加 0 来生成对应的 Sig 。 

第3页 共8页 

2025/2/12 18:53 

百家云-开发文档 

https://docs.baijiayun.com/rtc/quick/run_demo/HarmonyOS.html 

 (https://www.baijiayun.com/brtcDeveloperCenter) 下载中心 (/resources/docs/open/download/tpl.html) (/resources/docs/open/download/tpl.html) www.baijiayun.cfrom=brtc)from=brtc) 注册 (https://auth?/auth?// 登录

#### **下载中心 (/resources/docs/open/download/tpl.html) (/resources/docs/open/download/tpl.html) www.baijiayun.cfrom=brtc)from=brtc) 注册 (https://auth?/auth?// 登录** 

#### **开发者中心文档中心 (https://www.baijiayun.com/brtcDeveloperCenter)** 

##### 实时音视频 

##### 产品介绍 

性能数据 (/rtc/performance/ performance.html) 

发版说明 (/rtc/release/ Android.html) 

##### 快速入门 

一分钟跑通 DEMO (/rtc/ quick/run_demo/Android.html) 

一分钟集成 SDK (/rtc/quick/ run_sdk/Android.html) 

实现一个音视频直播 (/rtc/ quick/run_live/Android.html) 

### **下载 Demo 源码** 

##### 基础功能 

访问 https://git2.baijiashilian.com/open-android/brtc/brtcdemo-ohos (https://git2.baijiashilian.com/open-android/brtc/brtcdemo-ohos) 克隆或直接 进阶功能 下载下面仓库代码: 

客户端 API 

服务端 API 

git clone https://git2.baijiashilian.com/open‐android/brtc/brtcdemo‐ohos.git 

常见问题 

### **配置 DEMO 工程文件** 

最佳实践 

#### 下载 Demo 源码后,使用 DevEco Studio 打开 Demo 工程源码 

Demo 中目前只提供了 Quick Start 接口回调集成演示页面,对应工程中的 pages\QuickStart.ets 。其他页面为辅助性页面或 UI 组件。未来版本会补充更多场景化页面。 

工程中的 KeyCenter.ets 是运行 Demo 必需的配置信息,包括 AppID、UserSig 等。您必须在这里填写正确的配置项才可以正常运 行 Demo。 

第4页 共8页 

2025/2/12 18:53 

百家云-开发文档 

https://docs.baijiayun.com/rtc/quick/run_demo/HarmonyOS.html 

|**开发者中心文档中**|**心 (https://www.baijiayun.com/brtcDeveloperCenter)下载中心 (/resources/docs/open/download/tpl.html)**|**注册/登录(https://www.baijiayun.cauth?from=brtc)**|
|---|---|---|
|实时音视频|||
|产品介绍|||
|性能数据(/rtc/performance/|||
|performance.html)|||
|发版说明(/rtc/release/|||
|Android.html)|||
|快速入门|||
|一分钟跑通DEMO (/rtc/|||
|quick/run_demo/Android.html)|||
|一分钟集成SDK (/rtc/quick/|||
|run_sdk/Android.html)|||
|实现一个音视频直播(/rtc/|||
|quick/run_live/Android.html)|||
|基础功能|||
|进阶功能|||
|客户端API|||
|服务端API|||
|常见问题|||
|最佳实践|为Demo App进行签名在真机上运行Demo App必需进行签名请参考应用/服务签名(https://developerhu|weicom/|

为 Demo App 进行签名。在真机上运行 Demo App,必需进行签名。请参考应用/服务签名 (https://developer.huawei.com/ consumer/cn/doc/harmonyos-guides-V5/ide-signing-V5)完成签名。 

### **体验各项功能** 

第5页 共8页 

2025/2/12 18:53 

百家云-开发文档 

https://docs.baijiayun.com/rtc/quick/run_demo/HarmonyOS.html 

Demo 成功运行后,从首页点击 Quick Start 按钮,体验 SDK 提供的各项接口、回调演示: **开发者中心文档中心 (https://www.baijiayun.com/brtcDeveloperCenter) 下载中心 (/resources/docs/open/download/tpl.html)** 

**www.baijiayun.cfrom=brtc) 注册 (https://auth?/ 登录** 

##### 实时音视频 

##### 产品介绍 

性能数据 (/rtc/performance/ performance.html) 发版说明 (/rtc/release/ Android.html) 

##### 快速入门 

一分钟跑通 DEMO (/rtc/ quick/run_demo/Android.html) 

一分钟集成 SDK (/rtc/quick/ run_sdk/Android.html) 

实现一个音视频直播 (/rtc/ quick/run_live/Android.html) 

基础功能 进阶功能 客户端 API 服务端 API 常见问题 

最佳实践 

第6页 共8页 

2025/2/12 18:53 

百家云-开发文档 

https://docs.baijiayun.com/rtc/quick/run_demo/HarmonyOS.html 

 (https://www.baijiayun.com/brtcDeveloperCenter) 下载中心 (/resources/docs/open/download/tpl.html)

#### **下载中心 (/resources/docs/open/download/tpl.html) www.baijiayun.cfrom=brtc) 注册 (https://auth?/ 登录** 

#### **开发者中心文档中心 (https://www.baijiayun.com/brtcDeveloperCenter)** 

##### 实时音视频 

##### 产品介绍 

性能数据 (/rtc/performance/ performance.html) 

发版说明 (/rtc/release/ Android.html) 

##### 快速入门 

一分钟跑通 DEMO (/rtc/ quick/run_demo/Android.html) 

一分钟集成 SDK (/rtc/quick/ run_sdk/Android.html) 

实现一个音视频直播 (/rtc/ quick/run_live/Android.html) 

基础功能 进阶功能 客户端 API 服务端 API 常见问题 最佳实践 

第7页 共8页 

2025/2/12 18:53 

百家云-开发文档 

https://docs.baijiayun.com/rtc/quick/run_demo/HarmonyOS.html 

 (https://www.baijiayun.com/brtcDeveloperCenter) 下载中心 (/resources/docs/open/download/tpl.html)

**下载中心 (/resources/docs/open/download/tpl.html) www.baijiayun.cfrom=brtc) 注册 (https://auth?/ 登录** 

#### **开发者中心文档中心 (https://www.baijiayun.com/brtcDeveloperCenter)** 

实时音视频 产品介绍 性能数据 (/rtc/performance/ performance.html) 发版说明 (/rtc/release/ Android.html) 快速入门 一分钟跑通 DEMO (/rtc/ quick/run_demo/Android.html) 一分钟集成 SDK (/rtc/quick/ run_sdk/Android.html) 实现一个音视频直播 (/rtc/ quick/run_live/Android.html) 

基础功能 进阶功能 客户端 API 服务端 API 常见问题 最佳实践 

第8页 共8页 

2025/2/12 18:53 

百家云-开发文档 

https://docs.baijiayun.com/rtc/quick/run_sdk/HarmonyOS.html 

#### **开发者中心文档中心** 实时音视频 **(https://www.baijiayun.com/brtcDeveloperCenter)** (/rtc/index.html) > 快速入门 > 一分钟集成 SDK (/rtc/quick/run_sdk/Android.html) **下载中心 (/resources/docs/open/download/tpl.html) www.baijiayun.cfrom=brtc) 注册 (https://auth?/ 登录** 

实时音视频 **一分钟集成 SDK** 产品介绍 性能数据 (/rtc/performance/ performance.html) Android (/rtc/quick/run_sdk/Android.html) iOS (/rtc/quick/run_sdk/iOS.html) Web (/rtc/quick/run_sdk/Web.html) uni-app (/rtc/quick/run_sdk/uni-app.html) 发版说明 (/rtc/release/ HarmonyOS (/rtc/quick/run_sdk/HarmonyOS.html) Android.html) 快速入门 本文主要介绍如何集成 BRTC HarmonyOS SDK 到您的项目中。 一分钟跑通 DEMO (/rtc/ quick/run_demo/Android.html) **环境要求** 一分钟集成 SDK (/rtc/quick/ run_sdk/Android.html) DevEco Studio (https://developer.huawei.com/consumer/cn/deveco-studio/) 最新版本 实现一个音视频直播 (/rtc/ quick/run_live/Android.html) **前提条件** 

基础功能 

#### 已注册开通了 BRTC 服务 

进阶功能 已经拥有华为开发者账号(没有的话请先注册 (https://developer.huawei.com/consumer/cn/doc/start/registration-and客户端 API verification-0000001053628148)) 服务端 API 一部已经更新为 HarmonyOS NEXT 版本的真机( **BRTC HarmonyOS SDK 不提供模拟器版本** ) 常见问题 

### **集成步骤** 

最佳实践 

#### **一、获取 SDK** 

BRTC HarmonyOS SDK 通过 har 文件提供给开发者集成使用。您可以在 BRTC 的开发者文档中心的下载页面获取,也可以在 BRTC HarmonyOS Demo App 源码工程中找到。 

第1页 共4页 

2025/2/12 18:53 

百家云-开发文档 

https://docs.baijiayun.com/rtc/quick/run_sdk/HarmonyOS.html 

**开发者中心文档中心 (https://www.baijiayun.com/brtcDeveloperCenter) 下载中心 (/resources/docs/open/download/tpl.html) www.baijiayun.cfrom=brtc) 注册 (https://auth?/ 登录 二、导入 SDK** 

##### 实时音视频 

产品介绍 

性能数据 (/rtc/performance/ performance.html) 发版说明 (/rtc/release/ Android.html) 

##### 快速入门 

## **2.1 引入 SDK 包** 

如果您尚未创建 HarmonyOS 应用程序项目,请先创建一个应用程序项目。然后将下载到的 brtcohossdk.har 放到工程 entry/libs 目录下(如果没有 libs 目录,请手动创建一个) 

打开 entry/oh‐package.json5 文件,添加 SDK 依赖: 

"dependencies": { "@ohos/brtcohossdk": "file:./libs/brtcohossdk.har" } 

一分钟跑通 DEMO (/rtc/ quick/run_demo/Android.html) 

## **2.2 添加权限申请** 

一分钟集成 SDK (/rtc/quick/ run_sdk/Android.html) 

音视频应用必需要求您的应用具备麦克风、摄像头、网络、蓝牙等权限。请参考 Demo App 源码在您的应用中添加相应的权限。通常 位于 entry/src/main 目录下的 module.json5 文件。 

实现一个音视频直播 (/rtc/ quick/run_live/Android.html) 

基础功能 

另外,我们也强烈建议您动态申请敏感权限,例如在 Demo App 的 entry/src/main/ets/entryability/EntryAbility.ets 中,您可以 找到动态申请权限的示例代码。 

进阶功能 

客户端 API **2.3 添加后台保活任务** 

服务端 API 

常见问题 

在 HarmonyOS 上,应用必需添加后台保活任务,否则在应用退到后台后,音视频功能将无法继续工作。例如声音无法播放、屏幕共享 会自动停止等。因此,请参考 Demo App 的源码,为您的应用添加后台保活任务。请在 Demo 源码中找到 entry/src/main/ets/ common/BackgroundUtil.ets ,并参考示例使用方法,拷贝移植到您的应用中。 

最佳实践 

#### **三、导入相关模块并编码** 

推荐您参考 BRTC HarmonyOS Demo App 导入必要的模块,利用 BrtcEngine 提供的接口完成业务逻辑。下方是一些示例说明: 

第2页 共4页 

2025/2/12 18:53 

百家云-开发文档 

https://docs.baijiayun.com/rtc/quick/run_sdk/HarmonyOS.html 

## **导入模块 开发者中心文档中心 (https://www.baijiayun.com/brtcDeveloperCenter)** 

#### **下载中心 (/resources/docs/open/download/tpl.html) www.baijiayun.cfrom=brtc) 注册 (https://auth?/ 登录** 

```arkts
import BrtcEngine, { 实时音视频 BrtcRoomParams, BrtcVideoStreamType, BrtcVideoEncParam, 产品介绍 BrtcVideoResolutionMode, BrtcEngineAdvancedConfig } from '@ohos/brtcohossdk/Index' 性能数据 (/rtc/performance/ performance.html) 发版说明 (/rtc/release/ **创建实例** Android.html) BrtcEngine.createEngine(this.engineConfig).then((engineInstance) => { 快速入门 this.brtcEngine = engineInstance; 一分钟跑通 DEMO (/rtc/ }).catch((err: BusinessError) => { }) quick/run_demo/Android.html) 一分钟集成 SDK (/rtc/quick/ run_sdk/Android.html) **监听回调** 实现一个音视频直播 (/rtc/ quick/run_live/Android.html) this.brtcEngine.on(' 回调方法名 ', ( 参数 ) => {}) 
```

基础功能 

## **进入房间** 

进阶功能 客户端 API let roomParams = new BrtcRoomParams(); roomParams.appId = this.keyCenter.getAppId(); 服务端 API roomParams.roomId = this.roomId; roomParams.userId = this.userId; 常见问题 roomParams.userSig = sig; 最佳实践 this.brtcEngine.enterRoom(roomParams); 

## **开启视频预览** 

this.brtcEngine?.startLocalPreview(true or false); 

第3页 共4页 

2025/2/12 18:53 

百家云-开发文档 

https://docs.baijiayun.com/rtc/quick/run_sdk/HarmonyOS.html 

#### **开发者中心文档中心显示远端用户的视频 (https://www.baijiayun.com/brtcDeveloperCenter) 下载中心 (/resources/docs/open/download/tpl.html) www.baijiayun.cfrom=brtc) 注册 (https://auth?/ 登录** 

this.brtcEngine?.startRemoteView(userId, streamType); 实时音视频 产品介绍 **销毁实例** 性能数据 (/rtc/performance/ BrtcEngine.destroyEngine(); performance.html) 发版说明 (/rtc/release/ Android.html) 更多的功能需要您的探索,可以结合 demo 程序以及官网开发者中心的 API 接口文档来进行编码。 快速入门 一分钟跑通 DEMO (/rtc/ quick/run_demo/Android.html) 一分钟集成 SDK (/rtc/quick/ run_sdk/Android.html) 实现一个音视频直播 (/rtc/ quick/run_live/Android.html) 基础功能 进阶功能 客户端 API 服务端 API 常见问题 最佳实践 

第4页 共4页 

2025/2/12 18:53
