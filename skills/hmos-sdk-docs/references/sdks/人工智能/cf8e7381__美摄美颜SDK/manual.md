# 美摄美颜 **SDK** 集成指南 

适用于 HarmonyOS 开发者 

## 使用提示 

本文是美摄美颜SDK标准的集成指南文档。用以指导 SDK 的使用方法,默认读者已经熟悉 一 DevEco Studio 的基本使用方法,以及具有 定的 HarmonyOS 编程知识基础。目前支持 HarmonyOS API 12 及其以上版本。 

## 产品功能说明 

美摄美颜SDK,其包含了拍摄美颜、编辑美颜功能,美摄公司会随时根据手机系统、手机硬 件、使用场景的变化,快速调整,完善,升级SDK工具包,保证SDK包的稳定性、高效率、 高兼容性、给开发者带来良好的服务体验。 

## 试用与正式使用 

美摄美颜SDK免费给任何开发者提供试用机会,只需通过在美摄网站完成开发者注册,即可 进行SDK下载试用,但是在生成作品中,会带有试用水印,以保证美摄公司权益,如果想获 得完整的使用体验,请联系商务团队,进行沟通洽谈。 

网站:www.meishesdk.com 

商务邮箱:bd@meishesdk.com 

## 主要功能 

美摄美颜特效渲染主要特点:稳定、高效率、高兼容性、给开发者带来良好的服务体验。 

## 集成方式 

美摄美颜SDK提供了两种集成方式,分别是自动集成和手动集成。 

### 依赖包说明 

`@meishe/libnvstreamingsdkcore` :美摄美颜SDK 

#### 自动集成 **har** 依赖说明: 

在 entry 模块下的 oh-package.json5 文件添加: 

```
"dependencies": {
  "@meishe/libnvstreamingsdkcore": "x.x.x"
  //填写对应版本号,如:"@meishe/libnvstreamingsdkcore": "^3.14.3"
},
```

说明 **2** :现在har为字节码,需升级ide到5.0.3.500以上,并在工程级(最外层)buildprofile.json5,配置"useNormalizedOHMUrl": true 

```
"products ": [
  {
    "name ": "default ",
    "signingConfig ": "default ",
    "compatibleSdkVersion ": "5.0.0(12) ",
    "runtimeOS ": "HarmonyOS ",
    "buildOption ": {
      "strictMode ": {
        "useNormalizedOHMUrl ": true
      }
    }
  }
],
```

#### 手动集成 

#### 集成压缩包下载链接: 

https://www.meishesdk.com/downloadsNvStreamingSdk_Harmony_xxx.zip 

#### 集成压缩包内容 

`libNvStreamingSdkCore-signed.har` :核心业务包 

`doxygen` :文档 

`edit` :是一个鸿蒙 demo 项目代码,通过这个演示了基本用法,可以用来做参考。 

#### **har** 文件集成 

1. 解压缩 NvStreamingSdk_Harmony_xxx.zip 集成压缩包。 

2. 复制 libNvStreamingSdkCore-signed.har 到你的工程的外部目录下。(这个目录可以自定 义,也可以放到放到工程内部) 

说明:关联libNvStreamingSdkCore-signed.har,如,你复制 har 到 lib/ohos_arm64/ 目 一 录下,工程的目录是samples/edit,sample和 lib在同 级目录,那么在 entry 模块下的 oh-package.json5 文件添加 

```
"dynamicDependencies": {
  "libNvStreamingSdkCore": "file:../../lib/ohos_arm64/libNvStreamingSdkC
}
```

    

说明 **2** :现在har为字节码,需升级ide到5.0.3.500以上,并在工程级(最外层)buildprofile.json5,配置"useNormalizedOHMUrl": true 

```
"products ": [
  {
    "name ": "default ",
    "signingConfig ": "default ",
    "compatibleSdkVersion ": "5.0.0(12) ",
    "runtimeOS ": "HarmonyOS ",
    "buildOption ": {
      "strictMode ": {
        "useNormalizedOHMUrl ": true
      }
    }
  }
],
```

## 配置权限信息 

#### 说明:sdk的拍摄和编辑过程中会使用到一些授权,可以提前配置 

|权限|说明|是否必须|
|---|---|---|
|ohos.permission.CAMERA|使用相机录制视频|是|
|ohos.permission.MICROPHONE|使用相机录制视频|是|
|ohos.permission.ACCELEROMETER|允许应用读取加速度传感器的数据|否|

|权限|说明|是否必须|
|---|---|---|
|ohos.permission.INTERNET|sdk在线授权验证|是|

说明 **2** :在 entry 模块下的 module.json5 文件添加,reason的字段可以在 resources/base/element/string.json下配置 

```
"requestPermissions ":[
  {
    "name ": "ohos.permission.CAMERA ",
    "reason ": "$string:camera ",
    "usedScene ": {
      "abilities ": [ "EntryAbility " ],
      "when ": "always "
    }
  },
  {
    "name ": "ohos.permission.MICROPHONE ",
    "reason ": "$string:microphone ",
    "usedScene ": {
      "abilities ": [ "EntryAbility " ],
      "when ": "always "
    }
  },
  {
    "name ": "ohos.permission.ACCELEROMETER ",
    "reason ": "$string:accelerometer ",
    "usedScene ": {
      "abilities ": [ "EntryAbility " ],
      "when ": "always "
    }
  },
  {
    "name ": "ohos.permission.INTERNET ",
    "reason ": "$string:internet ",
    "usedScene ": {
      "abilities ": [ "EntryAbility " ],
      "when ": "always "
    }
  }
],
```

## 配置 **sdk** 初始化 

在您的工程内创建一个AbilityStage类型的组件,如MyAbilityStage.ets,进行sdk的初始化 

初始化需要传入sdk的授权文件lic,如果暂时没有,可以传入空,如果需要正式授权,需要 联系商务 

#### 示例如下 

```
export default class MyAbilityStage extends AbilityStage {
  onCreate() {
    let licPath = "rawfile:/sdkLic/com.example.edit.lic"
    let ctx = meishe.init(this.context, licPath, 0);
  }
}
```

### 初始化人脸模型 

初始化人脸模型是拍摄预览人脸特效和编辑预览人脸的基础 

首先把模型放到资源目录下,红色框需要用到的模型文件 

A71038DE-D045-460D-8C8F-8196E75CB5D6.1.arscene是人脸道具包,可以根据自己的选择 添加 

初始化人脸相关模型,可以在MyAbilityStage中进行初始化模型 

##### `onCreate() {` 

```
  let licPath = "rawfile:/sdkLic/com.example.edit.lic "
  let ctx = NvsStreamingContext.init(this.context, licPath, 0);
  let facePath = "rawfile:/face/ms_face240_v3.1.1.next.model "
  let fakeFacePath = "rawfile:/face/fakeface_v1.0.1.dat "
  let avatarPath = "rawfile:/face/ms_avatar_v2.0.0.next.model "
  let handPath = "rawfile:/face/ms_hand_common_v2.0.0.next.model "
  let humansegPath = "rawfile:/face/ms_humansegment_medium_v2.0.0.next.model
  let facecommonPath = "rawfile:/face/facecommon_v1.0.1.dat "
  let eyecontourPath = "rawfile:/face/ms_eyecontour_v2.0.0.next.model "
  let advancedbeautyPath = "rawfile:/face/advancedbeauty_v1.0.1.dat "
  let skysegPath = "rawfile:/face/ms_skysegment_v1.0.5.next.model "
  this.initHumanDetection(facePath, fakeFacePath, avatarPath, handPath, huma
  Logger.info(TAG,'SDK 初始化完成! '+ctx);
}
```

  

  

#### **/** *** 初始化人体检测功能 ***** 

- **@param facePath** 人脸检测模型路径 

- **@param fakeFacePath** 假脸检测模型路径 

- **@param avatarPath** 虚拟形象表情检测模型路径 

- **@param handPath** 手势检测模型路径 

- **@param humansegPath** 人像分割模型路径 

- **@param facecommonPath** 人脸通用模型路径 

- **@param eyecontourPath** 眼部轮廓检测模型路径 

- **@param advancedbeautyPath** 高级美颜模型路径 

- **@param skysegPath** 天空分割模型路径 

#### *** /** 

```
initHumanDetection(facePath: string, fakeFacePath: string, avatarPath: strin
  let result = NvsStreamingContext.initHumanDetection(facePath, " ", NvsHuma
  Logger.info(TAG, `facePath result: ${ result}`)
  result = NvsStreamingContext.setupHumanDetectionData(NvsHumanDetectionData
  Logger.info(TAG, `fakeFacePath result: ${result}`)
  result = NvsStreamingContext.initHumanDetectionExt(avatarPath, " ", NvsHum
  Logger.info(TAG, `avatarPath result: ${result}`)
  result = NvsStreamingCont ext.initHumanDetectionExt(handPath, " ", NvsHuma
  Logger.info(TAG, `handPath result: ${ result}`)
  result = NvsStreamingContext.initHumanDetectionExt(humansegPath, " ", NvsH
  Logger.info(TAG, `humansegPath result: ${result}`)
  result = NvsStrea mingContext.setupHumanDetectionData(NvsHumanDetectionDat
  Logger.info(TAG, `facecommonPath result: ${result}`)
  result = NvsStreamingConte xt.initHumanDetectionExt(eyecontourPath, " ", N
  Logger.info(TAG, `eyecontourPath result: ${result}`)
  result = NvsStreamingC ontext.setupHumanDetectionData(NvsHumanDetectionDat
  Logger.info(TAG, `advancedbeautyPath result: ${result}`)
  result = NvsStreami ngContext.initHumanDetectionExt(skysegPath, " ", NvsHu
  Logger.info(TAG, `skysegPath result: ${result}`)
}
```

    

## 拍摄预览 

调用接口之前,需要自行申请摄像头和麦克风的授权,权限申请通过之后再调用sdk的API 在您的工程内创建一个capturePage组件,调用sdk的摄像头预览,示例如下 

```
import meiShe, { NvsLiveWindow, NvsLiveWindowContent, NvsStreamingEngineCapt
```

##### `@Builder` 

```
export function pageBuilder(name: string, param: Object) {
  if (name == "capturePage ") {
    capturePage()
  }
}
@Component
struct capturePage {
  liveWindowContent : NvsLiveWindowContent | null = null;
  onContentLoad: (content : NvsLiveWindowContent) => void = (content : NvsLi
    this.liveWindowContent = content;
  }
  build() {
    NavDestination(){
      Stack(){
        NvsLiveWindow({ onContentLoad: this.onContentLoad }).width( "100% ")
          .onAppear(() => {
            if (this.liveWindowContent) {
              const suc = meiShe.getInstance()?.connectCapturePreviewWithLiv
              if (suc) {
                this.startCapturePreview()
              }
            }
          })
      }.width('100%').height('100%')
    }.width('100%').height('100%').title( "拍摄 " )
  }
  startCapturePreview() {
    let flags = NvsStreamingEngineCaptureFlag.NvsStreamingEngineCaptureFlag_
    meiShe.getInstance()?.startCapturePreview( 0, NvsVideoCaptureResolutionG
  }
}
```

## 拍摄使用人脸特技 

对拍摄预览画面进行人脸相关特效,例如美颜、美型等     如果使用到了道具效果包,需要先安装 

```
this.arsceneId = Tool.installAssetPackage(ARSCENE_PATH, " ", NvsAssetPackage
if (!this.arSecenFx) {
  this.arSecenFx = Tool.getSDK()?.appendBuiltinCaptureVideoFx('AR Scene')||n
}
this.arSecenFx?.setNum berVal( "Beauty Whitening ", 1)
this.arSecenFx?.setBooleanVal( "Advanced Beauty Enable ", true)
this.arSecenFx?.setNumberVal( "Advanced Beauty Type ", 0)
this.arSecenFx?.setNumberVal( "Advanced Beauty Intensity ", 1)
this.arSecenFx?.setBooleanVal( "Single Buffer Mode ", false)
/// 人脸遮挡
this.arSecenFx?.setBooleanVal( "AI Face Occlusion Enabled ",true)
this.arSecenFx?.setStringVal('Scene Id',this.arsceneId)
```

## 编辑预览 

可以在工程里内置一个素材,或者调用系统的相册去获取素材 

在您的工程内创建一个editPage组件,拿到素材资源,创建timeline,播放,示例如下 

    `import meiShe, { NvsAudioResolution, NvsBitDepth, NvsLiveWindow, NvsLiveWind @Builder export function pageBuilder(name: string, param: Object) { if (name == "editPage ") { editPage() } }` 

```
@Component
struct editPage {
  videoPath: string = " "
  liveWindowContent: NvsLiveWindowContent | null = null;
  onContentLoad: (content: NvsLiveWindowContent) => void = (content: NvsLive
    this.liveWindowContent = content;
    this.liveWindowContent.setFillMode(NvsLiveWindowFillMode.NvsLiveWindowFi
  timeline: NvsTimeline | null = null;
  aboutToAppear(): void {
    this.timeline = this.createTimeline();
  build() {
    NavDestination() {
      Stack() {
        NvsLiveWindow({ onContentLoad: this.on ContentLoad }).width( "100% "
          .onAppear(() => {
            if (this.liveWindowContent) {
              this.createLiveWindow()
            }
          })
      }.width('100%').height('100%')
    }.width('100%').height('100% ').title( "拍摄 " )
  createTimeline(): NvsTimeline | null {
    const vr: NvsVideoResolution = { imageWidth: 1920, imageHeight: 1080, bi
    const ar: NvsAudioResolution = { sampleRate: 48000, channelCount: 2 };
    const ctx = meiShe.getInstance();
    if (ctx != null) {
      ctx.setDefaultCaptionFade(false)
      const timeline = ctx?.createTimeline(vr, { num: 30, den: 1 }, ar, 0);
      if (!timeline) {
        return null;
      }
      const vt rack = timeline?.appendVideoTrack();
      vtrack?.appendClip( "rawfile:/test.mp4 " )
      return timeline;
    } else {
    }
    return null;
  }
  createLiveWindow() {
    if (this.timeline) {
      const suc = meiShe.getInstance()?.connectTimelineWithLiveWi ndow(this.
      if (suc) {
      } else {
      }
      const seekSuc = meiShe.getInstance()?.playbackTimeline(this.timeline,
    }
  }
}
```

## 编辑使用人脸特技 

对编辑预览画面进行人脸相关特效,例如美颜、美型等 

如果使用到了道具效果包,需要先安装 

```
this.arsceneId = Tool.installAssetPackage(ARSCENE_PATH, " ", NvsAssetPackage
let track = this.timeline?.getVideoTrackByIndex(0)
let clip = track?.getClipByIndex(0)
if (!this.arSecenFx && clip != null) {
  this.arSecenFx = clip.appendRawBuiltinFx('AR Scene')
}
this.arSecenFx?.getARSceneManipulate().setDetectionMode(32768)
this.arSecenFx?.setNumberVal( "Beauty Whitening ", 1)
this.arSecenFx?.setBooleanVal( "Advanced Beauty Enable ", true)
this.arSecenFx?.setNumberVal( "Advanced Beauty Type ", 0)
this.arSecenFx?.setNumberVal( "Advanced Beauty Intensity ", 1)
this.arSecenFx?.setBooleanVal( "Single Buffer Mode ", false)
/// 人脸遮挡
this.arSecenFx?.setBooleanVal( "AI Face Occlusion Enabled ", true)
this.arSecenFx?.setStringVal('Scene Id', this.arsceneId)
```

## 其他功能 

参考官网的文档:https://www.meishesdk.com/harmony/doc_ch/html/index.html 

## 技术支持 

当出现问题时:
   

- 给我们发送邮件:bd@meishesdk.com 

- 联系与您对接的同事,寻求帮助,我们会建立一个支持群为您服务
