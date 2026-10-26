> 来源: ohpm 中央仓 README(T1 信源) | 包: `@zego/zego-express-engine` | ohpm 最新版: 3.23.0 | 抓取: 2026-07-16
> 注意: 版本可能比市场快照新,以此为准时核对 CHANGELOG

# ZegoExpressEngine SDK

即构科技 (ZEGO) 极速音视频 OHOS SDK 是一个基于 [ZegoExpressEngine](https://doc-zh.zego.im/zh/693.html) 鸿蒙Next原生开发,提供视频直播以及实时音视频服务。仅需几行代码,30分钟即可轻松接入。

了解更多解决方案:[https://www.zego.im](https://www.zego.im)

## 下载安装

```bash

ohpm i @zego/zego-express-engine

```

OpenHarmony ohpm 环境配置等更多内容,请参考 [如何安装 OpenHarmony ohpm 包](https://ohpm.openharmony.cn/#/cn/help/downloadandinstall)

## 使用方法

### 申请 ZEGO AppID

登录 [ZEGO 官网](https://www.zego.im) 注册账号,根据自身实际业务需求选择场景,获取 AppID 与 AppSign,用于初始化 SDK。

### 创建Arkts项目

使用鸿蒙官方IDE DevecoStudio,创建Arkts类型的项目

### 集成 ZegoExpressOHOS SDK

开发者需要从 ohpm 处下载或 ZEGO SDK 官网下载 sdk,然后在项目中引入对 sdk 的依赖,SDK提供的是Har包的形式。

 ### 基础使用

#### 初始化引擎

```typescript

import ZegoExpressEngine, {

  ZegoBarrageMessageInfo,

  ZegoBroadcastMessageInfo,

  ZegoLogConfig,

  ZegoPlayerConfig,

  ZegoPublishChannel,

  ZegoPublisherConfig,

  ZegoRoomConfig,

  ZegoRoomExtraInfo,

  ZegoRoomState,

  ZegoScenario,

  ZegoSoundLevelConfig,

  ZegoStreamResourceMode,

  ZegoView,

  ZegoEngineProfile

} from '@zego/zego-express-engine'

//  使用从 ZEGO 控制台申请到的 appID 用于初始化

let profile:ZegoEngineProfile = new ZegoEngineProfile(KeyCenter.appID, KeyCenter.appSign, ZegoScenario.General, Context);

ZegoExpressEngine.createEngine(profile).then((engineInst) => {

    this.ZegoExpressInstance = engineInst;

})

```

#### 登入房间

```typescript

let user:ZegoUser = new ZegoUser();

user.userID = this.currentUserID;

user.userName = this.currentUserName;

let roomConfig:ZegoRoomConfig = new ZegoRoomConfig();

roomConfig.isUserStatusNotify = true;

this.ZegoExpressInstance.loginRoom(this.currentRoomID, user, roomConfig);

```

#### 开启音视频通话

在成功登入房间后,可调用 `startPreview` 开启音视频:

```typescript

// 需要在登入房间之后才能开启音视频通话

let view:ZegoView = new ZegoView();

view.view = this.previewID;

view.viewMode = this.viewMode;

this.ZegoExpressInstance.startPreview(view, ZegoPublishChannel.Main);

```

#### 将本地视频画面推向云服务

```typescript

let publisherConfig:ZegoPublisherConfig = new ZegoPublisherConfig();

publisherConfig.roomID = this.currentRoomID;

publisherConfig.forceSynchronousNetworkTime = 1;

this.ZegoExpressInstance.startPublishingStream(this.currentStreamID, publisherConfig, ZegoPublishChannel.Main);

```

#### 拉取其他用户音视频

登入房间后主动监听 `onRoomStreamUpdate`,在收到其他用户推出的音视频流,即可拉取:

```typescript

// 监听 roomStreamUpdate

this.ZegoExpressInstance.on('onRoomStreamUpdate', (roomID: string, updateType: zego.ZegoUpdateType, streamList: zego.ZegoStream[], extendedData: string) => {

    this.currentPlayStreamID = streamList[0].streamID;

})

let view:ZegoView = new ZegoView();

view.view = this.playerViewID;

view.viewMode = this.viewMode;

let playerConfig:ZegoPlayerConfig = new ZegoPlayerConfig();

playerConfig.resourceMode = ZegoStreamResourceMode.Default;

this.ZegoExpressInstance.startPlayingStream(this.currentPlayStreamID, view, playerConfig);

```

#### 退出房间

```typescript

// 退出房间

this.ZegoExpressInstance.logoutRoom(this.currentRoomID);

```

#### 销毁引擎

```typescript

// 销毁引擎

ZegoExpressEngine.destroyEngine();

```
