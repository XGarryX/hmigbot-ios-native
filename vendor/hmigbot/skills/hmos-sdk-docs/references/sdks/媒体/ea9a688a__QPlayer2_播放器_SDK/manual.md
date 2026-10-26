# ள᭛୏ত

### ੕ف१文կ

```
import { QPlayerContextFactory, QIPlayerContext,
QLogLevel,QMediaModel,QSurfaceRenderView} from '@qiniu/qplayer2-core/qplayer2-core'
```

### ڡত۸

```
@State mPlayerContext : QIPlayerContext = QPlayerContextFactory.createPlayerContext(
    QLogLevel.LOG_INFO,
    (AppStorage.get("context") as Context).filesDir,
bundleManager.getBundleInfoForSelfSync(bundleManager.BundleFlag.GET_BUNDLE_INFO_DEFAULT).
versionName,
    "")
this.mPlayerContext.init(AppStorage.get('context') as Context , getContext(this) as
common.UIAbilityContext)
```

### ᦡᗝดᐏᥤࢶ

一个 QSurfaceRenderView 对应一个 mPlayerContext , 如果一个 mPlayerContext 对应多个

QSurfaceRenderView 无法保证预期效果

```
QSurfaceRenderView({ mQPlayerContext: this.mPlayerContext, mXComponentId:
this.mXComponentId })
          .width('100%')
          .height('100%')
```

### ඎන

```
let builder : QMediaModelBuilder = new QMediaModelBuilder()
builder.addStreamElement("",QPlayerUrlType.QAUDIO_AND_VIDEO,1080,"http://demo-
videos.qnsdk.com/qiniu-2023-1080p.mp4",true,"","")
let model : QMediaModel = builder.build(is_live)
this.mPlayerContext.get_control_handler().playMediaModel(model,0)
```

### ᲀྪ

```
this.mPlayerContext.get_control_handler().release()
```

更加全面的功能,见接口文档

https://developer.qiniu.io/pili/12702/qplayer2-harmony

Demo介绍

1. demo 工程内的长视频播放页是基于 qplayer2-core 来实现的

2. demo 下载:https://sdk-release.qiniushawn.top/qplayer2-demo-v1.5.0-preview4.hap

3. 电脑连接 harmony next 手机,执行下方命令安装 hap 包

```
hdc install qplayer2-demo-v1.5.0-preview4.hap
```
