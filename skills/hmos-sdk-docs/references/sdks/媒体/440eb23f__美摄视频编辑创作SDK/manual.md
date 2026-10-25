# 美摄视频编辑创作 **SDK** 集成指南 

适用于 HarmonyOS 开发者 

## 使用提示 

本文是美摄视频编辑创作SDK标准的集成指南文档。用以指导 SDK 的使用方法,默认读者已 一 经熟悉 DevEco Studio 的基本使用方法,以及具有 定的 HarmonyOS 编程知识基础。目前 支持 HarmonyOS API 12 及其以上版本。 

## 产品功能说明 

美摄视频编辑创作SDK,其包含了视频拍摄、编辑、特效渲染等各种功能,其应用场景主要 是完全依赖于美摄能力的视频全流程产品开发,后期视频编辑制作等,开发者可以根据自己 的创意创建APP,实现各种音视频处理功能,美摄公司会随时根据手机系统、手机硬件、使 用场景的变化,快速调整,完善,升级SDK工具包,保证SDK包的稳定性、高效率、高兼容 性、给开发者带来良好的服务体验。 

## 试用与正式使用 

美摄视频编辑创作SDK免费给任何开发者提供试用机会,只需通过在美摄网站完成开发者注 册,即可进行SDK下载试用,但是在生成作品中,会带有试用水印,以保证美摄公司权益, 如果想获得完整的使用体验,请联系商务团队,进行沟通洽谈。 

网站:www.meishesdk.com 

商务邮箱:bd@meishesdk.com 

## 主要功能 

视频拍摄、视频编辑、特效渲染、滤镜等。 

## 主要特点 

稳定、高效率、高兼容性、给开发者带来良好的服务体验。 

## 集成方式 

美摄视频编辑创作SDK提供了两种集成方式,分别是自动集成和手动集成。 

### 依赖包说明 

`@meishe/libnvstreamingsdkcore_base` :美摄视频编辑创作SDK 

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

`"dynamicDependencies": { "libNvStreamingSdkCore": "file:../../lib/ohos_arm64/libNvStreamingSdkC }`     

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

说明:sdk的拍摄和编辑过程中会使用到一些授权,可以提前配置 

|权限|说明|是否必 须|
|---|---|---|
|ohos.permission.READ_MEDIA|允许应用读取用戶外部存储中的媒体文件 信息|否|
|ohos.permission.WRITE_MEDIA|允许应用读取用戶外部存储中的媒体文件 信息|否|
|ohos.permission.CAMERA|视频录制功能需要开启摄像头|是|
|ohos.permission.MICROPHONE|视频录制功能需要开启麦克风|是|
|ohos.permission.ACCELEROMETER|判断手机的旋转方向,和人脸特效有关|否|
|ohos.permission.INTERNET|SDK网络在线鉴权|是|

说明 **2** :在 entry 模块下的 module.json5 文件添加,reason的字段可以在 resources/base/element/string.json下配置 

```
"requestPermissions ":[
  {
    "name ": "ohos.permission.READ_MEDIA ",
    "reason ": "$string:read_permission ",
    "usedScene ": {
      "abilities ": [ "EntryAbility " ],
      "when ": "always "
    }
  },
  {
    "name ": "ohos.permission.WRITE_MEDIA ",
    "reason ": "$string:write_permission ",
    "usedScene ": {
      "abilities ": [ "EntryAbility " ],
      "when ": "always "
    }
  },
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

拍摄预览 

调用接口之前,需要自行申请摄像头和麦克风的授权,权限申请通过之后再调用sdk的API 

在您的工程内创建一个capturePage组件,调用sdk的摄像头预览,示例如下 

```
import meiShe, { NvsLiveWindow, NvsLiveWindowContent, NvsStreamingEngineCapt
@Builder
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

  

  

## 拍摄使用字幕特技 

对拍摄预览画面增加字幕特效 

```
this.caption = meishe.getInstance()?.appendCaptureCaption("测试字幕", 0, 100
```

  

  

## 编辑预览 

可以在工程里内置一个素材,或者调用系统的相册去获取素材 

在您的工程内创建一个editPage组件,拿到素材资源,创建timeline,播放,示例如下 

```
wContent, NvsLiveWindowFillMode, NvsTimeline, NvsVideoPreviewSizeMode, NvsVide
indowContent) => {
lMode_PreserveAspectFit)
height( "100% ")
Depth: NvsBitDepth.NvsBitDepth_8Bit, imagePAR: { num: 1, den: 1 } };
imeline, this.liveWindowContent)
 this.timeline?.ge tDuration(), NvsVideoPreviewSizeMode.NvsVideoPreviewSizeMo
```

## 编辑使用滤镜特技 

对编辑预览画面增加滤镜特技 

如果使用到了滤镜效果包,需要先安装 

```
const id = MsInstallUtil.installFx(FX_Path)
const result = this.timeline.addPackagedTimelineVideoFx(0, this.timeline.get
```

    

## 其他功能 

参考官网的文档:https://www.meishesdk.com/harmony/doc_ch/html/index.html 

## 技术支持 

当出现问题时: 

- 给我们发送邮件:bd@meishesdk.com
