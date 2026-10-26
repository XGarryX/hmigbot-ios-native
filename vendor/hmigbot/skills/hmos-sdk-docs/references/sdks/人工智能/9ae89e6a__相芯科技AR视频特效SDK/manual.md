# SDK 集成与使用指南

## 示例Demo的目录结构介绍

```
├── ets
```

│├── auth

```
││└── FUNMAuth.ets                           //鉴权文件
│├── components                                  //自定义UI组件
││├── beauty                                 //美颜自定义UI组件
│││├── BeautyFilterView.ets                        
│││├── BeautyShapeView.ets
│││└── BeautySkinView.ets
││├── common                                 //模块间通用的自定义UI组件
│││├── CaptureButton.ets
│││├── CustomDialog.ets
│││└── FUBackButton.ets
││├── floatComponent                         //浮窗自定义UI组件
│││├── FPSFloatView.ets
│││└── FPSManager.ets
││├── headToolBar                            //顶部工具栏自定义UI组件
│││├── FUHeadToolBar.ets
│││├── HeadToolBarController.ets
│││├── MorePopView.ets
│││└── PixelBufferView.ets
││├── home                                    //首页相关的自定义UI组件
│││├── DataConfig.ets
│││└── ItemContanerView.ets
││├── lightingView        
│││└── LightingView.ets
││└── sticker
││└── HorizontalScrollView.ets
│├── constants
││└── BeautyConstants.ets
│├── entryability
││└── EntryAbility.ets
│├── entrybackupability
││└── EntryBackupAbility.ets
│├── models                                       //业务模型
││└── beauty                                  //美颜业务模型
││├── BeautyFilterModel.ets
││├── BeautyShapeModel.ets
││└── BeautySkinModel.ets
│├── pages                                        //页面
││├── AssetsPreViewPage.ets                                   
││├── BeautyPage.ets                           //美颜页面
││├── ImageRenderPage.ets                      //相册图片特效渲染页面
││├── Index.ets                                //首页  
││├── SelectLocalMediaPage.ets                 //相册图片选择页面     
││├── StickerPage.ets                          //贴纸页面
```

││└── hook

```
││└── WithComponentLifeCycleHook.ets
│├── router
││├── RouterModel.ets                           //首页子页面配置中心
││└── RouterPages.ets
│├── service
││├── BeautyDataService.ets                     //美颜模块数据服务
││└── RenderKitService.ets                      //FUNMRenderKit服务
│├── utils
││├── AssetsUtil.ets
││├── FUSafeAreaUtil.ets
││└── RequestPermission.ets
│└── viewModels                                     //页面模型
│└── beauty                                     //美颜模块页面模型
│├── BeautyFilterViewModel.ets               
│├── BeautyShapeViewModel.ets
│└── BeautySkinViewModel.ets
├── module.json5
└── resources
├── base
│├── element
│├── media
│└── profile
│├── backup_config.json
│├── main_pages.json
│└── router_map.json                         //路由配置表
└── rawfile                                          
├── ai_face_processor.bundle                 //AI道具文件
├── face_beautification.bundle               //美颜道具文件
└── beauty
├── beauty_filter.json                //美颜滤镜配置文件
├── beauty_shape.json                 //美颜美型配置文件
└── beauty_skin.json                  //美颜美肤配置文件
```

## 关键资源文件

### 1、ai_face_processor.bundle 

如果不加载就没有AI检测能力

### 2、face_beautification.bundle 

如果不加载就没有美颜效果

### 3、beauty_skin.json

```
[
    {
"name":"磨皮",
"imeName":"mopi",
"type":0,
"currentValue":3.6,
"defaultValue":3.6,
"defaultValueInMiddle":false,
"ratio":6,
"performanceLevel": -1
    },
    ....
]
```

使用此配置文件创建BeautySkinModel模型数组,以便后续美肤参数的调整。

### 4、beauty_shape.json

```
[
    {
"name":"瘦脸",
"imeName":"shoulian",
"type":0,
"currentValue":0.0,
"defaultValue":0.0,
"defaultValueInMiddle":false,
"performanceLevel": -1
    },
    ....
]
```

使用此配置文件创建BeautyShapeModel模型数组,以便后续美形参数的调整。

### 5、beauty_filter.json

```
[
    {
"filterIndex":0,
"filterName":"origin",
"filterLevel":0.4
    },
    ....
]
```

使用此配置文件创建BeautyFilterModel模型数组,以便后续美颜滤镜参数的调整。

## 功能集成

## 1、设置SDK内部的 UIAbility 上下文

程序启动之初,需要设置SDK内部的 UIAbility 上下文,否则SDK内部依赖此上下文的所有功能将无法

正常运行。

```
onWindowStageCreate(windowStage: window.WindowStage): void {
FUNMGlobalContext.getContext().setUIAbilityContext(this.context);
```

」

```
3
```

## 2、初始化RenderKit

```
// 初始化 RenderKit
initRenderKit() {
let byte = new Uint8Array(g_auth_package)
const config = new FUNMSetupConfig(byte.buffer as ArrayBuffer, byte.length);
FUNMRenderKit.setup(config);
FUNMRenderKit.setLogLevel(FULOGLEVEL.FU_LOG_LEVEL_INFO);
FUNMRenderKit.sharedInstance().autoRenderConfig.isFrontCamera = true;
FUNMRenderKit.sharedInstance().autoRenderConfig.camaraResolution =
AutoRenderResolution;
FUNMRenderKit.sharedInstance().autoRenderConfig.fps = 30;
FUNMRenderKit.sharedInstance().renderDelegate = this;
}
```

g_auth_package为证书文件中的信息,证书信息获取详见 

参考示例-Demo运行说明文档

## 3、初始化AIKit

```
// 初始化AIKit
initAIKit() {
FUNMAIKit.loadAIModeWithAIType(FUAITYPE.FUAITYPE_FACEPROCESSOR, {
rawfilePath: 'ai_face_processor.bundle' });
FUNMAIKit.shareKit().maxTrackFaces = 2;
FUNMAIKit.shareKit().faceProcessorDetectMode =
FUNMFaceProcessorDetectMode.Video;
FUNMAIKit.shareKit().faceProcessorFaceLandmarkQuality =
FUNMFaceProcessorFaceLandmarkQuality.High;
}
```

## 4、加载美颜道具

```
loadBeauty() {
if (!FUNMRenderKit.sharedInstance().beauty) {
// 创建美颜道具
const beauty = new FUNMBeauty({ rawfilePath: 'face_beautification.bundle'
});
    beauty.heavyBlur = 0;
// 默认均匀磨皮
    beauty.blurType = 3;
// 默认精细变形
    beauty.faceShape = 4;
// 高性能设备设置去黑眼圈、去法令纹、大眼、嘴型最新效果
    beauty.addBeautyPropertyMode(FUNMBeautyPropertyMode.Mode2,
FUNMModeKey.RemovePouchStrength);
    beauty.addBeautyPropertyMode(FUNMBeautyPropertyMode.Mode2,
FUNMModeKey.RemoveNasolabialFoldsStrength);
    beauty.addBeautyPropertyMode(FUNMBeautyPropertyMode.Mode3,
FUNMModeKey.EyeEnlarging);
    beauty.addBeautyPropertyMode(FUNMBeautyPropertyMode.Mode3,
FUNMModeKey.IntensityMouth);
FUNMRenderKit.sharedInstance().beauty = beauty;
  }
}
```

## 5、修改美颜参数

### 5.1、修改美肤参数

```
//修改美肤参数
BeautySkinViewModel
private setValue(value: number, type: FUBeautySkin): void {
const beauty = FUNMRenderKit.sharedInstance().beauty;
if (beauty === undefined) {
FULogger.error('The beauty of FUNMRenderKit is undefined');
return;
  }
switch (type) {
case FUBeautySkin.BlurLevel:
      beauty.blurLevel = value;
break;
case FUBeautySkin.ColorLevel:
      beauty.colorLevel = value;
break;
case FUBeautySkin.RedLevel:
      beauty.redLevel = value;
break;
case FUBeautySkin.Sharpen:
      beauty.sharpen = value;
break;
case FUBeautySkin.FaceThreed:
      beauty.faceThreed = value;
break;
case FUBeautySkin.EyeBright:
      beauty.eyeBright = value;
break;
case FUBeautySkin.ToothWhiten:
      beauty.toothWhiten = value;
break;
case FUBeautySkin.RemovePouchStrength:
      beauty.removePouchStrength = value;
break;
case FUBeautySkin.RemoveNasolabialFoldsStrength:
      beauty.removeNasolabialFoldsStrength = value;
break;
case FUBeautySkin.AntiAcneSpot:
      beauty.antiAcneSpot = value;
break;
case FUBeautySkin.Clarity:
      beauty.clarity = value;
break;
  }
}
```

### 5.1、修改美形参数

```
BeautyShapeViewModel
private setValue(value: number, type: FUBeautyShape): void {
const beauty = FUNMRenderKit.sharedInstance().beauty;
if (beauty === undefined) {
FULogger.error('The beauty of FUNMRenderKit is undefined');
return;
  }
switch (type) {
case FUBeautyShape.CheekThinning:
      beauty.cheekThinning = value;
break;
case FUBeautyShape.CheekV:
      beauty.cheekV = value;
break;
case FUBeautyShape.CheekNarrow:
      beauty.cheekNarrow = value;
break;
case FUBeautyShape.CheekShort:
      beauty.cheekShort = value;
break;
case FUBeautyShape.CheekSmall:
      beauty.cheekSmall = value;
break;
case FUBeautyShape.Cheekbones:
      beauty.intensityCheekbones = value;
break;
case FUBeautyShape.LowerJaw:
      beauty.intensityLowerJaw = value;
break;
case FUBeautyShape.EyeEnlarging:
      beauty.eyeEnlarging = value;
break;
case FUBeautyShape.EyeCircle:
      beauty.intensityEyeCircle = value;
break;
case FUBeautyShape.Chin:
      beauty.intensityChin = value;
break;
case FUBeautyShape.Forehead:
      beauty.intensityForehead = value;
break;
case FUBeautyShape.Nose:
      beauty.intensityNose = value;
break;
case FUBeautyShape.Mouth:
      beauty.intensityMouth = value;
break;
case FUBeautyShape.LipThick:
      beauty.intensityLipThick = value;
break;
case FUBeautyShape.EyeHeight:
      beauty.intensityEyeHeight = value;
break;
case FUBeautyShape.Canthus:
      beauty.intensityCanthus = value;
break;
case FUBeautyShape.EyeLid:
      beauty.intensityEyeLid = value;
break;
case FUBeautyShape.EyeSpace:
      beauty.intensityEyeSpace = value;
break;
case FUBeautyShape.EyeRotate:
      beauty.intensityEyeRotate = value;
break;
case FUBeautyShape.LongNose:
      beauty.intensityLongNose = value;
break;
case FUBeautyShape.Philtrum:
      beauty.intensityPhiltrum = value;
break;
case FUBeautyShape.Smile:
      beauty.intensitySmile = value;
break;
case FUBeautyShape.BrowHeight:
      beauty.intensityBrowHeight = value;
break;
case FUBeautyShape.BrowSpace:
      beauty.intensityBrowSpace = value;
break;
case FUBeautyShape.BrowThick:
      beauty.intensityBrowThick = value;
break;
  }
}
```

### 5.3、修改美颜滤镜参数

```
BeautyFilterViewModel
/// 设置单项滤镜值
/// @param value 当前选中单项的值
setFilterValue(model: BeautyFilterModel, value: number) {
this.currentModel = model;
  model.filterLevel = value;
this.setFilter(model.filterLevel, model.filterName);
}
```

## 6、加载/移除贴纸道具

```
//道具贴纸示例
const rawfilePath = `sticker/bundles/${this.selectItem?.id}.bundle`;
const sticker = new FUNMItem({ rawfilePath: rawfilePath });
//添加贴纸
FUNMRenderKit.sharedInstance().sticker = sticker;
//移除贴纸
FUNMRenderKit.sharedInstance().sticker = undefined;
```

## 7、截图保存到相册

### 7.1、使用自动渲染时的相机截图

```
RenderKitService
private async captureImageFromAutoRenderHandle(renderOutput:
FUNMRenderOutput) {
const outputType =
FUNMRenderKit.sharedInstance().autoRenderConfig.outputType;
if (this.captureImageFromAutoRender && outputType !==
FUNMOutputType.XCOMPONENT_WITH_RGBA_BUFFER) {
FUNMRenderKit.sharedInstance().autoRenderConfig.outputType =
FUNMOutputType.XCOMPONENT_WITH_RGBA_BUFFER;
FUNMRenderKit.sharedInstance().refreshAutoRenderInput();
  }
if (this.captureImageFromAutoRender && renderOutput.dataType ===
FUNMOutputDataType.RGBA_BUFFER && renderOutput.pixelBuffer) {
FULogger.info('YYYY 保存照片调用了');
this.captureImageFromAutoRender = false;
let pixelMap =
FUNMImageUtil.getRGBAPixelMapFromPixelBuffer(renderOutput.pixelBuffer,
image.PixelMapFormat.RGBA_8888,
      { width: renderOutput.outputSize.width, height:
renderOutput.outputSize.height });
const encodeBuffer = await
FUNMImageUtil.encodePixelMapToGetFileBuffer(pixelMap, 'image/jpeg', 98);
await pixelMap.release();
await FUNMImageUtil.saveToPhotoAlbum(encodeBuffer);
    promptAction.showToast({ message: '照片保存成功!' });
FUNMRenderKit.sharedInstance().autoRenderConfig.outputType =
FUNMOutputType.XCOMPONENT;
FUNMRenderKit.sharedInstance().refreshAutoRenderInput();
  }
}
```

### 7.2、使用相册中的图片渲染截图

```
ImageRenderPage
async aboutToAppear() {
this.assetData = Object(this.routerParams?.params)?.assetData as
AssetsDataInterface;
const pixelMap = this.assetData.thumbnail;
if (pixelMap === undefined) {
return;
  }
let input_buffer: ArrayBuffer = new
ArrayBuffer(pixelMap.getPixelBytesNumber());
  pixelMap.readPixelsToBufferSync(input_buffer);
let info = pixelMap.getImageInfoSync();
await pixelMap.release();
const nInput = new FUNMNormalInput();
  nInput.pixelBuffer = input_buffer;
  nInput.pixelFormat = FUNMInputBufferFormat.RGBA_BUFFER;
const configT = new FUNMRenderConfig();
  configT.xcomponentId = xcomponentIdG;
  configT.outputType = FUNMOutputType.XCOMPONENT;
const input = new FUNMRenderInput(configT);
  input.normalInput = nInput;
  input.inputSize = { width: info.size.width, height: info.size.height };
this.input = input;
// TODO:待完善
RenderKitService.sharedInstance().finalImageOrientation(FUNMImageOrientation.U
P);
this.renderTimer = setInterval(async () => {
if (this.input) {
if (this.captureImage && this.input.renderConfig.outputType !==
FUNMOutputType.XCOMPONENT_WITH_RGBA_BUFFER) {
this.input.renderConfig.outputType =
FUNMOutputType.XCOMPONENT_WITH_RGBA_BUFFER;
      }
FUNMRenderKit.renderWithInput(this.input).then(async (output:
FUNMRenderOutput) => {
if (this.captureImage && output.dataType ===
FUNMOutputDataType.RGBA_BUFFER && output.pixelBuffer) {
FULogger.info('YYYY 保存照片调用了');
this.captureImage = false;
let pixelMap =
FUNMImageUtil.getRGBAPixelMapFromPixelBuffer(output.pixelBuffer,
image.PixelMapFormat.RGBA_8888,
              { width: output.outputSize.width, height:
output.outputSize.height });
const encodeBuffer = await
FUNMImageUtil.encodePixelMapToGetFileBuffer(pixelMap, 'image/jpeg', 98);
await pixelMap.release();
await FUNMImageUtil.saveToPhotoAlbum(encodeBuffer);
          promptAction.showToast({ message: '照片保存成功!' });
if (this.input) {
this.input.renderConfig.outputType = FUNMOutputType.XCOMPONENT;
          }
        }
      }).catch((Error: Error) => {
FULogger.error(`保存照片失败了${Error.message}`)
      });
    }
  }, 166);
}
```

## 8、相机前后摄像头切换

```
RenderKitService
async cameraSwitch() {
const camera = FUNMRenderKit.sharedInstance().camera;
if (camera) {
const isFrontCamera = !camera.isFrontCamera;
FUNMRenderKit.sharedInstance().autoRenderConfig.isFrontCamera =
isFrontCamera;
await FUNMRenderKit.stopAutoRender();
await FUNMRenderKit.startAutoRender();
FUNMAIKit.shareKit().isFrontCamera = isFrontCamera;
  }
}
```

## 9、相机分辨率切换

```
RenderKitService
async changeCamaraResolution(resolution: Size, displayResolutionHandle:() =>
void) {
FUNMRenderKit.sharedInstance().autoRenderConfig.camaraResolution =
resolution;
await FUNMRenderKit.stopAutoRender();
RenderKitService.sharedInstance().clearXComponent();
displayResolutionHandle();
await FUNMRenderKit.startAutoRender();
}
```

## 10、美颜效果对比

```
BeautyPage
Button({ stateEffect: true }) {
Image($r('app.media.demo_icon_contrast'))
}
.alignRules({
bottom: { anchor: "beautyView", align: VerticalAlign.Top },
left: { anchor: "beautyView", align: HorizontalAlign.Start }
})
.width(40)
.height(40)
.id("compareButton")
.offset({ x: 10, y: -20 })
.onTouch((event: TouchEvent) => {
switch (event.type) {
case TouchType.Up:
case TouchType.Cancel:
if (!this.shouldDoRender) {
RenderKitService.sharedInstance().shouldDoRender = true;
this.shouldDoRender = true;
      }
break;
case TouchType.Down:
case TouchType.Move:
if (this.shouldDoRender) {
RenderKitService.sharedInstance().shouldDoRender = false;
this.shouldDoRender = false;
      }
break;
  }
});
```

## 11、获取渲染后的数据

```
RenderKitService
didAutoRender(renderOutput: FUNMRenderOutput) {
this.captureImageFromAutoRenderHandle(renderOutput);
}
```

通过实现 FUNMAutoRenderDelegate 接口获取。

## 12、获取帧率、单帧渲染时间

```
RenderKitService
renderFPSInfo(fps: number, renderTime: number) {
AppStorage.set('FPSValue', FUNMNumberUtil.formatNumber(fps, 0, true));
AppStorage.set('renderTime', FUNMNumberUtil.formatNumber(renderTime, 0,
true));
}
```

通过实现 FUNMFPSDelegate 接口获取。
