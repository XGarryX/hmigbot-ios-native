> 来源: 厂商官方文档页(T2 信源) | https://cloud.tencent.com/document/product/647/130532 | 抓取: 2026-07-17
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

[文档中心](/document/product "文档中心") _>_[实时音视频](/document/product/647 "实时音视频") _>_[TRTC SDK](/document/product/647/32164 "TRTC SDK") _>_[快速接入](/document/product/647/116543 "快速接入") _>_ HarmonyOS

# HarmonyOS

最近更新时间:2026-05-13 16:39:02

 __[__](https://main.qcloudimg.com/raw/document/product/pdf/647_32164_cn.pdf)

__

  * __微信扫一扫

  *  __QQ
  *  __新浪微博
  *  __复制链接

 __链接复制成功

 ___我的收藏_

## 本页目录:

  * 前提条件
    * 开通服务
    * 环境准备
  * 创建项目
  * 集成并引入 SDK
    * 步骤1:导入 SDK
    * 步骤2:配置工程
    * 步骤3:(可选)通过 C++ 接口使用 SDK
  * 实现步骤
    * 步骤1:创建 TRTC 实例
    * 步骤2:打开/关闭麦克风
    * 步骤3:打开/关闭摄像头
    * 步骤4:进入房间
    * 步骤5:订阅音视频流
    * 步骤6:发布音视频流(含角色切换)
    * 步骤7:退出房间
    * 步骤8:销毁实例
  * 编译并运行
  * 常见问题
  * 下一步
  * 联系我们

本文将介绍如何快速完成腾讯云 TRTC(实时音视频)鸿蒙(HarmonyOS)SDK 的接入,实现一个基本的音视频通话。

## 前提条件

### 开通服务

1. 登录 [实时音视频控制台](https://console.cloud.tencent.com/trtc),单击**创建应用** 。如果您已经完成创建,可以跳过该操作。

2. 在创建应用成功后,您可以在**应用管理** 中获取到您的 **SDKAppID** 和 **SDK 密钥** 。

SDKAppID:控制台创建的 TRTC 应用的唯一标识。

UserSig(SDK 密钥):用户鉴权凭证,由您的业务服务器生成。

### 环境准备

在开始之前,请确保您已满足下列要求(不同 TRTC 版本对 DevEco 与系统版本要求不同):

**TRTC 12.1、12.2**

集成开发环境:5.0.3.800 或以上。

手机操作系统:HarmonyOS Beta1 或以上。

API Version:12 或以上。

**TRTC 12.3、12.6、12.8、13.0**

集成开发环境:5.0.3.900 或以上。

手机操作系统:HarmonyOS 5.0.0 或以上。

API Version:12 或以上

**TRTC 13.2**

集成开发环境:6.0.0.858 或以上。

手机操作系统:HarmonyOS 5.0.5 或以上。

API Version:17 或以上。

## 创建项目

参考华为官方指引 [创建工程](https://developer.huawei.com/consumer/cn/doc/harmonyos-guides-V5/ide-hello-world-V5)(如果您已有项目可跳过)。

## 集成并引入 SDK

### 步骤1:导入 SDK

通过 ohpm 导入 SDK

通过链接下载手动导入 SDK

开发工具 `DevEco Studio` 自带 `ohpm`,无需单独安装,只需在环境变量中导出 `ohpm` 即可。

1. 通过环境变量导出 `ohpm`,如已经在环境变量中导出了 `ohpm` ,可跳过该步骤:

Mac平台

Windows平台

`ohpm` 一般安装该目录:`/Applications/DevEco-Studio.app/Contents/tools/ohpm/bin`。

请您编辑您所在机器的环境变量文件,根据您安装的实际 `ohpm` 路径添加如下命令
    
    
    export OHPM_HOME="/Applications/DevEco-Studio.app/Contents/tools/ohpm"
    
    export PATH="$OHPM_HOME/bin:$PATH"

`ohpm` 一般在 `DevEco-Studio` 安装目录下:`xxxxx\\DevEco Studio\\tools\\ohpm\\bin`。

打开环境变量:

1. 新建用户变量:

变量名:`OHPM_HOME`

变量值:`xxxxx\\DevEco Studio\\tools\\ohpm`

2. 编辑 `Path` 用户变量,点 "新建",加入:`%OHPM_HOME%\\bin`。

3. 保存。

2. 进入您创建工程的 `entry` 目录下执行如下命令下载导入 `TRTC SDK` 库文件。
    
    
    ohpm install @tencentcloud/liteavsdk_professional

此时 `TRTC` 的 `LiteAVSDK_Professional_xxxxxx.har` 库文件已成功导入到您的工程。的

通过链接下载 [TRTC SDK](https://sdk-liteav-1252463788.cos.ap-hongkong.myqcloud.com/download/latest/v1/TXLiteAVSDK_Professional_OHOS_latest.zip) 库文件

1. `LiteAVSDK_Professional_xxxxxx.har`(`xxxxxx` 为具体版本号)复制到项目 `entry/libs` 目录下。

2. 在 `entry/oh-package.json5` 中添加本地依赖并同步:
    
    
    // entry/oh-package.json5
    
    {
    
      // ...
    
      "dependencies": {
    
        "liteavsdk": "file:libs/LiteAVSDK_Professional_xxxxxx.har"
    
      }
    
    }
    
      
    

点击 **Sync** 完成同步后,即可在工程内 **import** 并使用 `liteavsdk`。

### 步骤2:配置工程

#### 1\. 声明权限(module.json5)

在 `entry/module.json5` 的 `module` 中声明权限(按需增删):
    
    
    // entry/module.json5
    
    {
    
      // ...
    
      "module": {
    
        // ...
    
        "requestPermissions": [
    
          { "name": "ohos.permission.INTERNET" },
    
          { "name": "ohos.permission.USE_BLUETOOTH" },
    
          { "name": "ohos.permission.GET_BUNDLE_INFO" },
    
          { "name": "ohos.permission.GET_NETWORK_INFO" },
    
          { "name": "ohos.permission.GET_WIFI_INFO" },
    
          { "name": "ohos.permission.MODIFY_AUDIO_SETTINGS" },
    
          {
    
            "name": "ohos.permission.MICROPHONE",
    
            "reason": "$string:module_desc",
    
            "usedScene": { "abilities": [ "EntryAbility" ], "when": "always" }
    
          },
    
          {
    
            "name": "ohos.permission.CAMERA",
    
            "reason": "$string:module_desc",
    
            "usedScene": { "abilities": [ "EntryAbility" ], "when": "always" }
    
          }
    
        ]
    
      }
    
    }

#### 2\. 动态申请权限(麦克风示例)

在调用 TRTC 相关接口(例如 `startLocalAudio` / `startLocalPreview`)前,需要动态向用户申请麦克风/摄像头权限。
    
    
    import abilityAccessCtrl from '@ohos.abilityAccessCtrl'
    
    import promptAction from '@ohos.promptAction'
    
    import type { BusinessError } from '@ohos.base'
    
    import type { PermissionRequestResult } from '@ohos.abilityAccessCtrl'
    
      
    
    
    let atManager: abilityAccessCtrl.AtManager = abilityAccessCtrl.createAtManager();
    
    try {
    
      atManager.requestPermissionsFromUser(getContext(), ['ohos.permission.MICROPHONE'], (err: BusinessError, data: PermissionRequestResult) => {
    
        console.info('request MICROPHONE result=' + JSON.stringify(data));
    
        // AuthResult: -1 denied, 0 granted, 2 invalid call
    
        if (data.authResults[0] === 0) {
    
          share.trtc.startLocalAudio(this.audioConfig.audioQuality);
    
        } else {
    
          try { promptAction.showToast({ message: '申请麦克风权限失败', duration: 1000 }); } catch (e) {}
    
        }
    
      });
    
    } catch (e) {
    
      try { promptAction.showToast({ message: '申请麦克风权限失败', duration: 1000 }); } catch (e2) {}
    
    }

#### 3\. 后台运行(按需接入)

应用退到后台时,是否需要继续音视频业务由您自行决定:

**不需要后台运行** :退后台时建议主动关闭采集,避免被系统杀死导致异常。
    
    
    trtc.stopLocalAudio();

**需要后台运行** :

在 `entry/module.json5` 声明权限:
    
    
    {
    
      "module": {
    
        "requestPermissions": [
    
          { "name": "ohos.permission.KEEP_BACKGROUND_RUNNING" }
    
        ]
    
      }
    
    }

在 TRTC 音频存续期间接入 **AVSession** 与 **BackgroundTask** :通常在进房前开启,在退房后关闭。

**重要****说明:**

华为官方文档:

[音频播放开发概述](https://developer.huawei.com/consumer/cn/doc/harmonyos-guides-V5/audio-playback-overview-V5)

[音频录制开发概述](https://developer.huawei.com/consumer/cn/doc/harmonyos-guides-V5/audio-recording-overview-V5)

BackgroundTask 可能会在无音频活动时被系统自动取消,建议每次退后台按音频状态按需 `startBackgroundRunning`。

AVSession 建议在 App 前台状态下开启;推荐是让 `createAVSession` 由 UI 操作触发。

### 步骤3:(可选)通过 C++ 接口使用 SDK

如果您更倾向于使用 C++ 接口而不是 ArkTS,可以执行此步骤;如果您仅使用 ArkTS 调用 TRTC SDK,请忽略本步骤。

1. 通过导入 `.har` 的方式集成 TRTC SDK(同上)。

2. 拷贝头文件:将 SDK 中的 C++ 头文件拷贝到项目中(路径示例:`SDK/LiteAVSDK_TRTC_xxx/libs/include`),并在 `CMakeLists.txt` 中配置 include 与 so 链接。
    
    
    cmake_minimum_required(VERSION 3.6)
    
    include_directories(${NATIVE_ROOT_PATH}
    
                        ${NATIVE_ROOT_PATH}/include)
    
      
    
    
    target_link_libraries(entry PUBLIC ${NATIVE_ROOT_PATH}/../../../oh_modules/liteavsdk/libs/${OHOS_ARCH}/libliteavsdk.so)

3. 初始化 Context(无性能消耗,建议尽早调用):
    
    
    import { LiteAVBase } from 'liteavsdk'
    
      
    
    
    @Entry
    
    @Component
    
    struct EntryView {
    
      aboutToAppear(): void {
    
        LiteAVBase.setContext(getContext());
    
      }
    
    }

4. C++ 全平台接口的方法、类型等均定义在 `trtc` 命名空间中,建议直接 `using namespace trtc;`。

**说明:**

DevEco Studio C/C++ 环境参考 [NDK 工程构建概述](https://developer.huawei.com/consumer/cn/doc/harmonyos-guides-V5/build-with-ndk-overview-V5)。

目前只有 TRTC 版本的 SDK 支持 C++ 接口;更多使用方式请参见 [API 概览](https://cloud.tencent.com/document/product/647/32268)。

5. ArkTS + C++ 混合:可通过隐藏接口桥接获取 Native Handle(示例):
    
    
    // ArkTS side
    
    EntryNative.setTRTCCloudInstance(share.trtc.callExperimentalAPI(`{ "api" : "getNativeHandle" }`));
    
    
    // C++ side
    
    napi_value setTRTCCloudInstance(napi_env env, napi_callback_info info) {
    
      size_t argc = 1;
    
      napi_value args[1] = {nullptr};
    
      
    
    
      napi_get_cb_info(env, info, &argc, args, nullptr, nullptr);
    
      
    
    
      size_t len = 0;
    
      char address[32] = {0};
    
      napi_get_value_string_utf8(env, args[0], address, 32, &len);
    
      
    
    
      liteav::ITRTCCloud* trtcCloud = reinterpret_cast<liteav::ITRTCCloud*>(std::stoull(address));
    
      // Now you can call C++ APIs with the native pointer.
    
      
    
    
      napi_value ret;
    
      napi_get_undefined(env, &ret);
    
      return ret;
    
    }

## 实现步骤

### 步骤1:创建 TRTC 实例

导入并创建 `TRTCCloud` 实例,设置事件监听器:
    
    
    import { getTRTCShareInstance, destroyTRTCShareInstance, TRTCCloud, TRTCCloudCallback } from 'liteavsdk';
    
      
    
    
    this.trtc = getTRTCShareInstance(getContext());
    
      
    
    
    private onEnterRoom = (result: number) => {
    
      // result > 0: success (ms cost), result < 0: error code
    
    };
    
      
    
    
    private onCallback: TRTCCloudCallback = {
    
      onEnterRoom: this.onEnterRoom,
    
    };
    
      
    
    
    this.trtc.addCallback(this.onCallback);

### 步骤2:打开/关闭麦克风

申请麦克风权限成功后,调用 `startLocalAudio(quality)` 开启采集:

`SPEECH`:偏语音通信,抗弱网能力强

`MUSIC`:偏高保真音乐

`DEFAULT`:默认策略
    
    
    share.trtc.startLocalAudio(this.audioConfig.audioQuality);
    
    // ...
    
    share.trtc.stopLocalAudio();

### 步骤3:打开/关闭摄像头

1. 在界面中创建 `XComponent`,并将 `id` 作为 viewId 传入 `startLocalPreview`。
    
    
    build() {
    
      Column() {
    
        // Note: libraryname must match the sdk so name: 'liteavsdk'
    
        XComponent({ id: 'self_cameraViewID', type: XComponentType.SURFACE, libraryname: 'liteavsdk' })
    
          .backgroundColor(Color.Black)
    
      }
    
    }

2. 摄像头权限申请成功后开启预览:
    
    
    share.trtc.startLocalPreview(this.videoConfig.isFrontCamera, 'self_cameraViewID');
    
    // ...
    
    share.trtc.stopLocalPreview();

### 步骤4:进入房间

准备 `TRTCParams` 与 `TRTCAppScene`,调用 `enterRoom`:
    
    
    let params = new TRTCParams();
    
    params.sdkAppId = 1400000123;  // Please replace with your own SDKAppID
    
    params.userId = 'denny';       // Please replace with your own userid
    
    params.roomId = 123321;        // Please replace with your own room number
    
    params.userSig = 'xxx';        // Please replace with your own userSig
    
    params.role = TRTCRoleType.TRTCRoleAnchor;
    
      
    
    
    trtc.enterRoom(params, TRTCAppScene.TRTCAppSceneLIVE);

进房结果通过 `onEnterRoom(result)` 回调:

`result > 0`:进房成功,值为耗时(ms)

`result < 0`:进房失败,值为错误码

计费说明请见 [音视频时长计费说明](https://cloud.tencent.com/document/product/647/44248)。

### 步骤5:订阅音视频流

1. 设置订阅模式(可选)

可在 `enterRoom` 前调用 `setDefaultStreamRecvMode` 选择:

自动订阅(默认)

手动订阅(需通过 `muteRemoteAudio(userId, false)` 触发播放)

2. 音频流播放/静音
    
    
    trtc.muteRemoteAudio('denny', true);
    
    trtc.muteRemoteAudio('denny', false);

3. 视频流播放

播放远端视频需提前创建对应 `XComponent`,并把 `XComponent` 的 `id` 传给 SDK:
    
    
    // remote render view
    
    XComponent({ id: 'denny_cameraViewID', type: XComponentType.SURFACE, libraryname: 'liteavsdk' })
    
      .backgroundColor(Color.Black)
    
    
    trtc.startRemoteView('denny', TRTCVideoStreamType.TRTCVideoStreamTypeBig, 'denny_cameraViewID');
    
    // ...
    
    trtc.stopRemoteView('denny', TRTCVideoStreamType.TRTCVideoStreamTypeBig);
    
    trtc.stopAllRemoteView();

如需在播放中切换渲染控件,可使用 `updateRemoteView`;渲染参数使用 `setRemoteRenderParams`。

### 步骤6:发布音视频流(含角色切换)

在通话场景(视频通话/语音通话)中,用户默认是主播(Anchor)。

在直播场景(视频直播/语音直播)中,需要区分 `Anchor`(可推流)与 `Audience`(不可推流)。

从观众切到主播后可开启采集与预览:
    
    
    trtc.switchRole(TRTCRoleType.TRTCRoleAnchor);
    
    trtc.startLocalAudio(TRTCAudioQualityDefault);
    
    trtc.startLocalPreview(true, 'self_cameraViewID');

监听切换结果:
    
    
    private onSwitchRole = (errCode: number, errMsg: string) => {
    
      if (errCode !== 0) {
    
        this.showToast('Switching operation failed...');
    
      }
    
    };
    
      
    
    
    private onCallback: TRTCCloudCallback = {
    
      onSwitchRole: this.onSwitchRole,
    
    };
    
      
    
    
    this.trtc.addCallback(this.onCallback);

**注意:**

如果房间中已有主播过多可能导致 `switchRole` 失败;当不再需要推流(下麦)时,应切回观众。

更多进阶说明请参见 [功能相关](https://cloud.tencent.com/document/product/647/43020)。

### 步骤7:退出房间

调用 `exitRoom()` 开始退房流程,并监听 `onExitRoom(reason)`:
    
    
    trtc.exitRoom();
    
    
    private onExitRoom = (reason: number) => {
    
      // 0: normal exit, 1: kicked, 2: room dissolved
    
    };
    
      
    
    
    private onCallback: TRTCCloudCallback = {
    
      onExitRoom: this.onExitRoom,
    
    };
    
      
    
    
    this.trtc.addCallback(this.onCallback);

**说明:**

SDK 会通知房间内其他用户触发 `onRemoteUserLeaveRoom`,并释放摄像头/麦克风等资源。

建议在收到 `onExitRoom` 后再释放 `TRTCCloud` 实例。

### 步骤8:销毁实例

当不再使用时销毁共享实例(按项目封装方式调用):
    
    
    destroyTRTCShareInstance();

## 编译并运行

1. 使用真机(鸿蒙设备)运行与调试。

2. 在 DevEco Studio 中完成 Sync 依赖后,直接 Run 安装到设备。

3. 首次运行请在系统弹窗中授予麦克风/摄像头权限。

## 常见问题

您可以在 [API 概览](/document/product/647/129075) 查看所有函数列表及其描述。

如果您的接入和使用中遇到问题,请参见 [常见问题](https://cloud.tencent.com/document/product/647/43019)。

## 下一步

至此,您已成功实现基本的音视频通话,您还可以参考下列文档了解更多核心功能:

[调整视频画质](/document/product/647/32236)

[调整画面方向](/document/product/647/32237)

## 联系我们

如果您在接入或使用过程中有任何疑问或者建议,欢迎 [联系我们](/document/product/647/19906) 提交反馈。

[上一篇: Unity](/document/product/647/127563 "上一篇: Unity")[下一篇: Android&iOS&HarmonyOS](/document/product/647/32236 "下一篇: Android&iOS&HarmonyOS")

 __中国站

  * 中文
  * [International](https://www.tencentcloud.com/)

[文档“捉虫”活动检视指定产品文档,发现和反馈有效问题,奖!](https://cloud.tencent.com/developer/article/1610407)

[API专项"捉虫"反馈API文档问题,代金券、周边好礼奖不停!](https://cloud.tencent.com/developer/article/1630768)

[文档建议,你提了吗快来使用腾讯云产品文档,提出有效建议,奖!](https://cloud.tencent.com/developer/article/1523112)

咨询
