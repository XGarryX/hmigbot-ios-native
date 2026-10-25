# SenseAR Effects SDK开发指南

本项目是北京大甜绵白糖科技有限公司提供的特效引擎 SDK HAR包,您可以集成SDK实现各类人脸特效、贴

纸、美颜、滤镜等功能。

## 功能亮点

人脸检测与跟踪

美颜效果(磨皮、美白、瘦脸等)

AR 贴纸/道具实时叠加

实时滤镜效果

视频流处理与渲染

高性能渲染支持(基于 OpenGL ES)

## 环境要求

DevEco Studio 5.0 及以上

OpenHarmony api12 及以上

真机运行(部分功能依赖相机)

## 1.SDK集成

导入SDK

导入检测模型

导入资源文件

添加Xcomponent组件

```
build(){
Stack(){
XComponent({
         id: Common.XCOMPONENT_ID,
         type: XComponentType.TEXTURE,
         libraryname: Common.LIBRARY_NAME,
      })
      .onLoad(()=>{
this.onXcomponentLoad()
       })
       .width('100%')
       .aspectRatio(this.photoAspectRatio)
    }
  }
//注意事项:XComponent的libraryname需要与sdk so库一致,默认值为entry
(libentry.so)
```

## 2.SDK基本功能

SDK基本功能接口都在cpp/types/libentrt/Index.d.ts中

### 2.1 鉴权

//在页面将要显示的时候生成激活码:

```
aboutToAppear(): void {
//获取上下文
let context = getContext()
let resourceManager = context.resourceManager
//获取license.lic文件
let licenseContent =
resourceManager.getRawFileContentSync('license/license.lic')
const buffer = licenseContent.buffer.slice(0)
let outputPixelBuffer = newArrayBuffer(10240)
//开始鉴权
let result = libstmobile.checkLicenseByBuffer(buffer)
if (!this.result) {
      promptAction.showToast({
        message: `check license error ${this.result}`,
        duration: 2000
      })
    }
```

注意:只有在鉴权成功后才能使用特效相关功能

### 2.2 初始化

初始化操作需要在Xcomponent加载成功回调后,加载模型,设置窗口渲染大小等

```
onXcomponentLoad(): void {
//初始化
let result = libstmobile.InitializeByMode(EffectsMode.PREVIEW)
//添加模型
const models = resourceManager.getRawFileListSync(`models`)
    models.forEach(model => {
const subModelPath = this.writeModelToSandbox(model,'models')
const result = libstmobile.addSubModelByPath(subModelPath)
    })
//添加动物模型
const aniModels = resourceManager.getRawFileListSync(`aniModels`)
    aniModels.forEach(model => {
const subModelPath = this.writeModelToSandbox(model,'aniModels')
const result = libstmobile.addAnimalSubModelByPath(subModelPath)
    })
//更新window size 以设备实际宽度为准
let displayInfo = display.getDefaultDisplaySync()
    libstmobile.updateWindowSize(displayInfo.width, displayInfo.width
/this.photoAspectRatio)
  }
```

注意事项:初始化有三种模式,渲染方式不一样,参考以下定义

```
export constenumEffectsMode{
PREVIEW = 0,  //适用实时预览
PHOTO,        //适用图片单帧渲染
```

VIDEO//适用视频模式

```
}
```

## 2.3 SDK参数设置

```
export const setParamByEffectParam:(param:EffectParam, value: number) => boolean;
```

参数说明:

param:需要设置的参数:

```
export constenumEffectParam{
EFFECT_PARAM_MIN_FRAME_INTERVAL,        ///< \~chinese 贴纸前后两个序列帧切换的最
```

小时间间隔,单位为毫秒。当两个相机帧处理的间隔小于这个值的时候,当前显示的贴纸序列帧会继续

显示,直到显示的时间大于该设定值贴纸才会切换到下一阵,相机帧不受影响。 \~english The

```
minimum time interval between two sequential frames of stickers, in milliseconds.
When the interval between two camera frame processing is less than this value, the
current displayed sticker sequential frame will continue to display until the
displayed time is greater than this set value, and then the sticker will switch to
the next formation, and the camera frame will not be affected.
EFFECT_PARAM_MAX_MEMORY_BUDGET_MB,      ///< \~chinese 设置贴纸素材资源所占用的最
```

大内存(MB),当估算内存超过这个值时,将不能再加载新的素材包 \~english Set the maximum

```
memory (MB) occupied by sticker material resources. When the estimated memory
exceeds this value, new material packages can no longer be loaded.
EFFECT_PARAM_QUATERNION_SMOOTH_FRAME,   ///< \~chinese 设置相机姿态平滑参数,表示
平滑多少帧, 越大延迟越高,抖动越微弱 \~english Set camera attitude smoothing
parameters, indicating how many frames to smooth, the larger the delay, the weaker
the jitter.
EFFECT_PARAM_USE_INPUT_TIMESTAMP,       ///< \~chinese 设置贴纸是否使用外部时间戳
更新 \~english Set whether the sticker uses an external timestamp update
EFFECT_PARAM_PREFER_MEMORY_CACHE,       ///< \~chinese 倾向于空间换时间,传0的话,
```

则尽可能清理内部缓存,保持内存最小。目前主要影响3D共享资源 \~english Prefer space for

```
time. If 0 is passed, it will clean up the internal cache as much as possible to
keep the memory at a minimum. Currently, it mainly affects 3D shared resources.
EFFECT_PARAM_DISABLE_BEAUTY_OVERLAP,    ///< \~chinese 传入大于0的值,禁用美颜
```

Overlap逻辑(贴纸中的美颜会覆盖前面通过API或者贴纸生效的美颜效果,贴纸成组覆盖,API单个覆

```
盖),默认启用Overlap \~english Enter a value greater than 0 to disable the beauty
overlap logic (the beauty in the sticker will cover the beauty effect that has
taken effect through the API or the sticker, the stickers are overlapped in
groups, and the API is overlapped individually), overlap is enabled by default
EFFECT_PARAM_DISABLE_MODULE_REORDER,    ///< \~chinese 传入大于0的值,强制按素材包
```

添加顺序显示贴纸、美妆效果,后添加的在上层显示,该选项只会影响设置之后添加的素材。默认(0)

会对v3.1之前的素材包重排module的渲染顺序。重新排序是为了在与美妆、风格素材包叠加时达到最

```
佳效果 \~english Input a value greater than 0 to render modules strictly by add
package order. stickers and makeups added late would render on top of others. This
option will only affect materials added after setting. default value (0) will
reorder the rendering order of modules from packages version less than v3.1. The
reorder is to achieve the best effect when overlaying with beauty makeup and style
material packages.
EFFECT_PARAM_3D_POSE_SOLUTION,          ///< \~chinese 3DPose计算方案,传入0使用
```

106旧模型方案,传1使用基于282模型优化的Pose方案,默认值为1 \~english 3DPose

```
calculation solution, input 0 to use the old 106 model solution, input 1 to use
the Pose solution optimized based on the 282 model, the default value is 1.
EFFECT_PARAM_RENDER_DELAY_FRAME,        ///< \~chinese 设置未来帧帧数,默认值是0,
需要是大于等于0的值,0表示不开未来帧 \~english Set the number of future frames, the
default value is 0, it needs to be a value greater than or equal to 0, 0 indicates
that future frames are not opened.
EFFECT_PARAM_GREEN_COLOR_BALANCE,       ///< \~chinese 设置去绿程度,0表示不去绿,
1表示最大程度去绿,默认值为1 \~english Set the degree of green removal, 0 indicates
no green removal, 1 indicates the maximum degree of green removal, the default
value is 1.
EFFECT_PARAM_GREEN_SPILL_BY_ALPHA,      ///< \~chinese 设置去绿色彩平衡, 和去绿程
```

度配套使用, 平衡因去绿导致的主体颜色变化, 范围[0.0, 1.0], 默认0.5(不进行平衡) \~english

```
Set green removal color balance, used in conjunction with green removal intensity
to balance the color change caused by green removal. Range [0.0, 1.0], default 0.5
(no balance).
EFFECT_PARAM_EXPLICIT_OUT_TEX_BLIT,     ///< \~chinese 设置Render接口的输出纹理是
```

否做一次显示拷贝,在传入的输入纹理与D3D纹理绑定共享时需要传1弃用,默认0不做。 \~english

```
set whether do an explicit texture copy for render output texture.  When output
texture is bound with a D3D texture, this option needs turn on with 1, default is
0 (disabled).
EFFECT_PARAM_GREEN_SEGMENT_COLOR,       /// \~chinese 设置绿幕分割颜色RGB值,默认为
绿色,将颜色值(16进制数0xFFFFFF,按R、G、B排列)按float类型传入 \~english Set the RGB
color value for green screen segmentation. The default color is green (hexadecimal
value 0xFFFFFF, arranged as R, G, B). The color value should be passed as a float
type
EFFECT_PARAM_PLASTIC_FACE_OCCLUSION,    ///< \~chinese 微整形效果遮挡,目前支持白
```

牙、亮眼,默认值为0, 表示没有效果遮挡,1表示开启效果遮挡 \~english MicroPlastic effect

```
occlusion, and currently supports teeth whitening and eye brightening. default
value is 0, means no effect occlusion, 1 means open effect occlusion.
EFFECT_PARAM_MAKEUP_PERFORMANCE_HINT,   ///< \~chinese 设置美妆性能/效果优先级倾
```

向,性能优先适用于多人脸的场景,引擎内部会根据设置调整渲染策略, 0表示效果优先, 1表示性能

```
优先,默认值为0 \~english Configure the priority preference for makeup
performance/effects. Performance priority is suitable for scenarios with multiple
faces, and the engine internally will adjust the rendering strategy according to
the setting. A value of 0 indicates a preference for effects, while a value of 1
indicates a preference for performance. The default value is 0.
EFFECT_PARAM_DISABLE_TRIGER_OVERLAP,    ///< \~chinese 传入大于0的值,禁用贴纸触发
```

逻辑对Overlap的影响(贴纸中的美颜触发会覆盖前面通过API或者贴纸生效的美颜效果),默认触发逻

```
辑会对Overlap的影响 \~english Pass a value greater than 0 to disable the effect of
sticker trigger logic on Overlap (beautification triggered by stickers will
override the beautification effects applied earlier through API or stickers). By
default, the trigger logic will affect Overlap.
}
```

value:设置参数的值

### 2.4 贴纸、风格妆

### 2.4.1 添加、切换贴纸

```
export const changePackageByPath:(path: string) => number;
export const changePackageByBuffer:(buffer: ArrayBuffer) => number;
```

参数说明 path:贴纸素材包的路径返回值:素材包id(通过id可以移除贴纸、修改其中某些参数、动画贴纸重

新播放等)

### 2.4.2 移除贴纸

```
export const removePackage:(id: number) => boolean;
```

参数说明 id:添加素材包时获取的id

### 2.4.3 移除所有贴纸

```
export const clearPackages:() => boolean;
```

### 2.4.4 修改风格强度

```
export const setPackageBeautyStrength:(id:number, type:EffectBeautyGroup, value:
number) => boolean;
```

参数说明:

id:添加素材包时获取的id

type:修改风格的哪种类型参数(美妆or滤镜...)

```
export constenumEffectBeautyGroup{
EFFECT_BEAUTY_GROUP_BASE,           ///< \~chinese 基础美颜组 \~english Basic
beauty group
EFFECT_BEAUTY_GROUP_RESHAPE,        ///< \~chinese 美型组 \~english Reshape
group
EFFECT_BEAUTY_GROUP_PLASTIC,        ///< \~chinese 微整形组 \~english Micro
Plastic group
EFFECT_BEAUTY_GROUP_TONE,           ///< \~chinese 图像微调组 \~english Tone
adjustment group
EFFECT_BEAUTY_GROUP_BOKEH,          ///< \~chinese 背景模糊微调组 \~english bokeh
group
EFFECT_BEAUTY_GROUP_MAKEUP,         ///< \~chinese 美妆组 \~english Makeup group
EFFECT_BEAUTY_GROUP_FILTER,         ///< \~chinese 滤镜组 \~english Filter group
}
```

strength:需要修改的特效强度,范围一般为[0,1]

### 2.4.5 贴纸重播

```
export const replayPackage:(id:number) => boolean;
```

参数说明:

id:添加素材包时获取的id

## 2.5 美妆、美颜、滤镜

一般使用流程:加载素材包(若有)-> 设置强度

### 2.5.1 设置素材包

一般美妆、滤镜都会有素材包,某些美颜也需要先加载素材包

```
export const setBeautyPackageByPath:(type:BeautyType, path: string) => boolean;
export const setBeautyPackageByBuffer:(type:BeautyType, buffer: ArrayBuffer) =>
boolean;
```

参数说明:

type:类型:

```
/**
 * Beauty Type
 */
export constenumBeautyType{
// \~chinese 基础美颜 base
// \~english Basic beauty
EFFECT_BEAUTY_BASE_WHITTEN                      = 101,  ///< \~chinese 美白,
[0,1.0], 默认值0.30, 0.0不做美白 \~english Whitening, [0,1.0], default value 0.30,
0.0 means no whitening
EFFECT_BEAUTY_BASE_REDDEN                       = 102,  ///< \~chinese 红润,
[0,1.0], 默认值0.36, 0.0不做红润 \~english Redden, [0,1.0], default value 0.36, 0.0
means no reddening
EFFECT_BEAUTY_BASE_FACE_SMOOTH                  = 103,  ///< \~chinese 磨皮,
[0,1.0], 默认值0.74, 0.0不做磨皮 \~english Face smoothing, [0,1.0], default value
0.74, 0.0 means no face smoothing
EFFECT_BEAUTY_BASE_SKIN_SMOOTH                  = 104,  ///< \~chinese 身体皮肤祛
皱, [0,1.0],默认值0.0, 0.0不做身体皮肤祛皱 \~english Body skin wrinkle removal, [0,
1.0], default value 0.0, 0.0 disables wrinkle removal
// \~chinese 美形 reshape
// \~english Beauty reshaping
EFFECT_BEAUTY_RESHAPE_SHRINK_FACE               = 201,  ///< \~chinese 瘦脸,
[0,1.0], 默认值0.11, 0.0不做瘦脸效果 \~english Face slimming, [0,1.0], default
value 0.11, 0.0 means no face slimming effect
EFFECT_BEAUTY_RESHAPE_ENLARGE_EYE               = 202,  ///< \~chinese 大眼,
[0,1.0], 默认值0.13, 0.0不做大眼效果 \~english Eye enlargement, [0,1.0], default
value 0.13, 0.0 means no eye enlargement effect
EFFECT_BEAUTY_RESHAPE_SHRINK_JAW                = 203,  ///< \~chinese 小脸,
[0,1.0], 默认值0.10, 0.0不做小脸效果 \~english Jaw slimming, [0,1.0], default value
0.10, 0.0 means no jaw slimming effect
EFFECT_BEAUTY_RESHAPE_NARROW_FACE               = 204,  ///< \~chinese 窄脸,
[0,1.0], 默认值0.0, 0.0不做窄脸 \~english Narrow face, [0,1.0], default value 0.0,
0.0 means no narrow face effect
EFFECT_BEAUTY_RESHAPE_ROUND_EYE                 = 205,  ///< \~chinese 圆眼,
[0,1.0], 默认值0.0, 0.0不做圆眼 \~english Round eyes, [0,1.0], default value 0.0,
0.0 means no round eyes effect
// \~chinese 微整形 plastic
// \~english Micro Plastic group
EFFECT_BEAUTY_PLASTIC_THINNER_HEAD              = 301,  ///< \~chinese 小头, [0,
1.0], 默认值0.0, 0.0不做小头效果 \~english Smaller head, [0, 1.0], default value
0.0, 0.0 means no smaller head effect
EFFECT_BEAUTY_PLASTIC_THIN_FACE                 = 302,  ///< \~chinese 瘦脸型,
[0,1.0], 默认值0.0, 0.0不做瘦脸型效果 \~english Thinner face shape, [0,1.0], default
value 0.0, 0.0 means no thinner face shape effect
EFFECT_BEAUTY_PLASTIC_CHIN_LENGTH               = 303,  ///< \~chinese 下巴,
[-1, 1], 默认值为0.0,[-1, 0]为短下巴,[0, 1]为长下巴 \~english Chin length, [-1,
1], default value is 0.0, [-1, 0] means shorter chin, [0, 1] means longer chin
EFFECT_BEAUTY_PLASTIC_HAIRLINE_HEIGHT           = 304,  ///< \~chinese 额头,
[-1, 1], 默认值为0.0,[-1, 0]为低发际线,[0, 1]为高发际线 \~english Hairline height,
[-1, 1], default value is 0.0, [-1, 0] means lower hairline, [0, 1] means higher
hairline
EFFECT_BEAUTY_PLASTIC_APPLE_MUSLE               = 305,  ///< \~chinese 苹果肌,
[0, 1.0],默认值为0.0,0.0不做苹果肌 \~english Apple muscle, [0, 1.0], default value
is 0.0, 0.0 means no apple muscle effect
EFFECT_BEAUTY_PLASTIC_NARROW_NOSE               = 306,  ///< \~chinese 瘦鼻翼,
[0, 1.0], 默认值为0.0,0.0不做瘦鼻 \~english Narrow nose wings, [0, 1.0], default
value is 0.0, 0.0 means no narrow nose wings effect
EFFECT_BEAUTY_PLASTIC_NOSE_LENGTH               = 307,  ///< \~chinese 长鼻,
[-1, 1], 默认值为0.0, [-1, 0]为短鼻,[0, 1]为长鼻 \~english Longer nose, [-1, 1],
default value is 0.0, [-1, 0] means shorter nose, [0, 1] means longer nose
EFFECT_BEAUTY_PLASTIC_PROFILE_RHINOPLASTY       = 308,  ///< \~chinese 侧脸隆鼻,
[0, 1.0],默认值为0.0,0.0不做侧脸隆鼻效果 \~english Profile rhinoplasty, [0, 1.0],
default value is 0.0, 0.0 means no profile rhinoplasty effect
EFFECT_BEAUTY_PLASTIC_MOUTH_SIZE                = 309,  ///< \~chinese 嘴型,
[-1, 1],默认值为0.0,[-1, 0]为放大嘴巴,[0, 1]为缩小嘴巴 \~english Mouth shape, [-1,
1], default value is 0.0, [-1, 0] means larger mouth, [0, 1] means smaller mouth
EFFECT_BEAUTY_PLASTIC_PHILTRUM_LENGTH           = 310,  ///< \~chinese 缩人中,
[-1, 1], 默认值为0.0,[-1, 0]为长人中,[0, 1]为短人中 \~english Philtrum length,
[-1, 1], default value is 0.0, [-1, 0] means longer philtrum, [0, 1] means shorter
philtrum
EFFECT_BEAUTY_PLASTIC_EYE_DISTANCE              = 311,  ///< \~chinese 眼距,
[-1, 1],默认值为0.0,[-1, 0]为减小眼距,[0, 1]为增加眼距 \~english Eye distance,
[-1, 1], default value is 0.0, [-1, 0] means reducing eye distance, [0, 1] means
increasing eye distance
EFFECT_BEAUTY_PLASTIC_EYE_ANGLE                 = 312,  ///< \~chinese 眼睛角度,
```

[-1, 1],默认值为0.0,[-1, 0]为左眼逆时针旋转,[0, 1]为左眼顺时针旋转,右眼与左眼相对

```
\~english Eye angle, [-1, 1], default value is 0.0, [-1, 0] means rotating left
eye counterclockwise, [0, 1] means rotating left eye clockwise, relative to right
eye
EFFECT_BEAUTY_PLASTIC_OPEN_CANTHUS              = 313,  ///< \~chinese 开眼角,
[0, 1.0],默认值为0.0, 0.0不做开眼角 \~english Eye opening, [0, 1.0], default value
is 0.0, 0.0 means no eye opening effect
EFFECT_BEAUTY_PLASTIC_BRIGHT_EYE                = 314,  ///< \~chinese 亮眼,[0,
1.0],默认值为0.0,0.0不做亮眼 \~english Brighten eyes, [0, 1.0], default value is
0.0, 0.0 means no eye brightening effect
EFFECT_BEAUTY_PLASTIC_REMOVE_DARK_CIRCLES       = 315,  ///< \~chinese 祛黑眼圈,
[0, 1.0],默认值为0.0,0.0不做去黑眼圈 \~english Remove dark circles, [0, 1.0],
default value is 0.0, 0.0 means no dark circles removal effect
EFFECT_BEAUTY_PLASTIC_REMOVE_NASOLABIAL_FOLDS   = 316,  ///< \~chinese 祛法令纹,
[0, 1.0],默认值为0.0,0.0不做去法令纹 \~english Remove nasolabial folds, [0, 1.0],
default value is 0.0, 0.0 means no nasolabial folds removal effect
EFFECT_BEAUTY_PLASTIC_WHITE_TEETH               = 317,  ///< \~chinese 白牙,[0,
1.0],默认值为0.0,0.0不做白牙 \~english White teeth, [0, 1.0], default value is
0.0, 0.0 means no teeth whitening effect
EFFECT_BEAUTY_PLASTIC_SHRINK_CHEEKBONE          = 318,  ///< \~chinese 瘦颧骨,
[0, 1.0], 默认值0.0, 0.0不做瘦颧骨 \~english Shrink cheekbones, [0, 1.0], default
value is 0.0, 0.0 means no cheekbone shrinking effect
EFFECT_BEAUTY_PLASTIC_OPEN_EXTERNAL_CANTHUS     = 319,  ///< \~chinese 开外眼角比
例,[0, 1.0],默认值为0.0, 0.0不做开外眼角 \~english Open external canthus, [0,
1.0], default value is 0.0, 0.0 means no opening of the outer canthus effect
EFFECT_BEAUTY_PLASTIC_SHRINK_JAWBONE            = 320,  ///< \~chinese 瘦下颔,
[0, 1.0], 默认值0.0, 0.0不做瘦下颔 \~english Shrink jawbone, [0, 1.0], default
value is 0.0, 0.0 means no jawbone shrinking effect
EFFECT_BEAUTY_PLASTIC_SHRINK_ROUND_FACE         = 321,  ///< \~chinese 圆脸瘦脸,
[0, 1.0], 默认值0.0, 0.0不做瘦脸 \~english Shrink round face, [0, 1.0], default
value is 0.0, 0.0 means no face slimming effect for round face
EFFECT_BEAUTY_PLASTIC_SHRINK_LONG_FACE          = 322,  ///< \~chinese 长脸瘦脸,
[0, 1.0], 默认值0.0, 0.0不做瘦脸 \~english Shrink long face, [0, 1.0], default
value is 0.0, 0.0 means no face slimming effect for long face
EFFECT_BEAUTY_PLASTIC_SHRINK_GODDESS_FACE       = 323,  ///< \~chinese 女神瘦脸,
[0, 1.0], 默认值0.0, 0.0不做瘦脸 \~english Shrink goddess face, [0, 1.0], default
value is 0.0, 0.0 means no face slimming effect for goddess face
EFFECT_BEAUTY_PLASTIC_SHRINK_NATURAL_FACE       = 324,  ///< \~chinese 自然瘦脸,
[0, 1.0], 默认值0.0, 0.0不做瘦脸 \~english Shrink natural face, [0, 1.0], default
value is 0.0, 0.0 means no face slimming effect for natural face
EFFECT_BEAUTY_PLASTIC_SHRINK_WHOLE_HEAD         = 325,  ///< \~chinese 整体缩放小
头,[0, 1.0], 默认值0.0, 0.0不做整体缩放小头效果 \~english Shrink the whole head,
[0, 1.0], default value is 0.0, 0.0 means no shrinking of the whole head effect
EFFECT_BEAUTY_PLASTIC_EYE_HEIGHT                = 326,  ///< \~chinese 眼睛位置比
例,[-1, 1],默认值0.0, [-1, 0]向下移动眼睛,[0, 1]向上移动眼睛 \~english Eye
position ratio, [-1, 1], default value is 0.0, [-1, 0] means moving eyes downward,
[0, 1] means moving eyes upward
EFFECT_BEAUTY_PLASTIC_MOUTH_CORNER              = 327,  ///< \~chinese 嘴角上移比
例,[0, 1.0],默认值0.0, 0.0不做嘴角调整 \~english Mouth corner lifting ratio, [0,
1.0], default value is 0.0, 0.0 means no mouth corner adjustment
EFFECT_BEAUTY_PLASTIC_HAIRLINE                  = 328,  ///< \~chinese 新发际线高
低比例,[-1, 1],默认值0.0, [-1, 0]为低发际线,[0, 1]为高发际线 \~english Hairline
height ratio, [-1, 1], default value is 0.0, [-1, 0] means lower hairline, [0, 1]
means higher hairline
EFFECT_BEAUTY_PLASTIC_FULLER_LIPS               = 329,  ///< \~chinese 丰唇,
[-1, 1],默认值0.0,[-1, 0]为嘴唇变薄,[0, 1]为丰唇 \~english Lip fullness
adjustment, [-1, 1], default value is 0.0; [-1, 0] reduces lip fullness, [0, 1]
increases lip fullness
EFFECT_BEAUTY_PLASTIC_MOUTH_WIDTH               = 330,  ///< \~chinese 嘴巴宽度,
[-1, 1],默认值0.0,[-1, 0]为嘴巴变宽,[0, 1]为嘴巴变窄 \~english Mouth width
adjustment, [-1, 1], default value is 0.0; [-1, 0] increases width, [0, 1]
decreases width
EFFECT_BEAUTY_PLASTIC_BROW_HEIGHT               = 331,  ///< \~chinese 眉毛高度,
[-1, 1],默认值0.0,[-1, 0]为眉毛上移,[0, 1]为眉毛下移 \~english Eyebrow height
adjustment, [-1, 1], default value is 0.0; [-1, 0] raises brows, [0, 1] lowers
brows
EFFECT_BEAUTY_PLASTIC_BROW_THICKNESS            = 332,  ///< \~chinese 眉毛粗细,
[-1, 1],默认值0.0,[-1, 0]为眉毛变细,[0, 1]为眉毛增粗 \~english Eyebrow thickness
adjustment, [-1, 1], default value is 0.0; [-1, 0] makes brows thinner, [0, 1]
makes brows thicker
EFFECT_BEAUTY_PLASTIC_BROW_DISTANCE             = 333,  ///< \~chinese 眉毛间距,
[-1, 1],默认值0.0,[-1, 0]为眉毛间距变大,[0, 1]为眉毛间距变小 \~english Eyebrow
distance adjustment, [-1, 1], default value is 0.0; [-1, 0] increases distance
between brows, [0, 1] decreases it
EFFECT_BEAUTY_PLASTIC_FACE_V_SHAPE              = 334,  ///< \~chinese V脸,从下
颌角到下巴的V脸效果,[0, 1.0],默认值0.0, 0.0不做V脸 \~english V-shaped face effect
(jawline to chin), [0, 1.0], default value is 0.0; 0.0 applies no V-shape effect
EFFECT_BEAUTY_PLASTIC_FACE_FULL_V_SHAPE         = 335,  ///< \~chinese V脸,整脸
的V脸效果,[0, 1.0],默认值0.0, 0.0不做V脸 \~english Full V-shaped face effect, [0,
1.0], default value is 0.0; 0.0 applies no V-shape effect
EFFECT_BEAUTY_PLASTIC_NOSE_TIP                  = 336,  ///< \~chinese 瘦鼻头,
[0, 1.0],默认值0.0, 0.0不做瘦鼻头 \~english Nose tip refinement, [0, 1.0], default
value is 0.0; 0.0 applies no nose tip refinement
EFFECT_BEAUTY_PLASTIC_NOSE_BRIDGE               = 337,  ///< \~chinese 鼻梁调整,
[0, 1.0],默认值0.0, 0.0不做鼻梁调整 \~english Nose bridge adjustment, [0, 1.0],
default value is 0.0; 0.0 applies no nose bridge adjustment
EFFECT_BEAUTY_PLASTIC_ENLARGE_PUPIL             = 338,  ///< \~chinese 放大瞳孔,
[0, 1.0],默认值0.0, 0.0不做瞳孔放大 \~english Pupil enlargement, [0, 1.0], default
value is 0.0; 0.0 applies no pupil enlargement
// \~chinese 调整 tone
// \~english Tone adjustment
EFFECT_BEAUTY_TONE_CONTRAST                     = 601,  ///< \~chinese 对比度,
[0,1.0], 默认值0.05, 0.0不做对比度处理 \~english Contrast, [0,1.0], default value
0.05, 0.0 means no contrast adjustment
EFFECT_BEAUTY_TONE_SATURATION                   = 602,  ///< \~chinese 饱和度,
[0,1.0], 默认值0.10, 0.0不做饱和度处理 \~english Saturation, [0,1.0], default value
0.10, 0.0 means no saturation adjustment
EFFECT_BEAUTY_TONE_SHARPEN                      = 603,  ///< \~chinese 锐化, [0,
1.0], 默认值0.0, 0.0不做锐化 \~english Sharpening, [0, 1.0], default value 0.0, 0.0
means no sharpening
EFFECT_BEAUTY_TONE_CLEAR                        = 604,  ///< \~chinese 清晰度,
清晰强度, [0,1.0], 默认值0.0, 0.0不做清晰 \~english Clarity, clarity strength,
[0,1.0], default value 0.0, 0.0 means no clarity adjustment
EFFECT_BEAUTY_TONE_BOKEH                        = 605,  ///< \~chinese 背景虚化强
度, [0,1.0], 默认值0.0, 0.0不做背景虚化 \~english Bokeh intensity, [0,1.0], default
value 0.0, 0.0 means no bokeh effect
EFFECT_BEAUTY_TONE_DENOISING                    = 606,  ///< \~chinese 去噪,[0,
1.0], 默认值0.0, 0.0不做去噪处理 \~english denoising intensity, [0, 1.0], default
value 0.0 means off
EFFECT_BEAUTY_TONE_COLOR_TONE                   = 607,  ///< \~chinese 色调,
[-1.0, 1.0], 默认值0.0, 0.0不做色调处理 \~english Color tone adjustment, [-1.0,
1.0], default value 0.0 means off
EFFECT_BEAUTY_TONE_COLOR_TEMPERATURE            = 608,  ///< \~chinese 色温,
[-1.0, 1.0], 默认值0.0, 0.0不做色温处理 \~english Color tempareture adjustment,
[-1.0, 1.0], default value 0.0 means off
// \~chinese 美妆 makeup
// \~english Makeup group
EFFECT_BEAUTY_MAKEUP_HAIR_DYE                   = 401,  ///< \~chinese 染发
\~english Hair dye
EFFECT_BEAUTY_MAKEUP_LIP                        = 402,  ///< \~chinese 口红
\~english Lipstick
EFFECT_BEAUTY_MAKEUP_CHEEK                      = 403,  ///< \~chinese 腮红
\~english Blush
EFFECT_BEAUTY_MAKEUP_NOSE                       = 404,  ///< \~chinese 修容
\~english Nose contouring
EFFECT_BEAUTY_MAKEUP_EYE_BROW                   = 405,  ///< \~chinese 眉毛
\~english Eyebrow
EFFECT_BEAUTY_MAKEUP_EYE_SHADOW                 = 406,  ///< \~chinese 眼影
\~english Eyeshadow
EFFECT_BEAUTY_MAKEUP_EYE_LINE                   = 407,  ///< \~chinese 眼线
\~english Eyeliner
EFFECT_BEAUTY_MAKEUP_EYE_LASH                   = 408,  ///< \~chinese 眼睫毛
\~english Eyelash
EFFECT_BEAUTY_MAKEUP_EYE_BALL                   = 409,  ///< \~chinese 美瞳
\~english Eye color
EFFECT_BEAUTY_MAKEUP_PACKED                     = 410,  ///< \~chinese 打包的美妆
```

素材,可能包含一到多个单独的美妆模块,与其他单独美妆可以同时存在 \~english Packed makeup

```
material, may contain one or more individual makeup modules, can coexist with
other individual makeups
EFFECT_BEAUTY_MAKEUP_EYE_PAINTING               = 411,  ///< \~chinese 眼妆
\~english Eye painting
// \~chinese 滤镜 filter
// \~english Filter group
EFFECT_BEAUTY_FILTER                            = 501,  ///< \~chinese 滤镜
\~english Filter
// \~chinese 试妆 tryon
// \~english Makeup tryon
EFFECT_BEAUTY_TRYON_HAIR_COLOR                  = 701,  ///< \~chinese 染发,可设
置的参数包括:颜色,强度,明暗度,高光 \~english Hair dye, configurable parameters
include: color, intensity, brightness, highlight
EFFECT_BEAUTY_TRYON_LIPSTICK                    = 702,  ///< \~chinese 口红,可设
置的参数包括:颜色,强度,高光(特定材质:水润、闪烁、金属),质地类型 \~english Lipstick,
configurable parameters include: color, intensity, highlight (specific textures:
moisturizing, shimmering, metallic), texture type
EFFECT_BEAUTY_TRYON_LIPLINE                     = 703,  ///< \~chinese 唇线,可设
置的参数包括:颜色,强度,唇线线宽 \~english Lip line, configurable parameters
include: color, intensity, lip line width
EFFECT_BEAUTY_TRYON_BLUSH                       = 704,  ///< \~chinese 腮红,可设
置的参数包括:颜色,强度 \~english Blush, configurable parameters include: color,
intensity
EFFECT_BEAUTY_TRYON_BROW                        = 705,  ///< \~chinese 眉毛,可设
置的参数包括:颜色,强度 \~english Eyebrow, configurable parameters include: color,
intensity
EFFECT_BEAUTY_TRYON_FOUNDATION                  = 706,  ///< \~chinese 粉底,可设
置的参数包括:颜色,强度 \~english Foundation, configurable parameters include:
color, intensity
EFFECT_BEAUTY_TRYON_CONTOUR                     = 707,  ///< \~chinese 修容,可设
置的参数包括:强度(整体),区域信息(区域id,颜色,强度) \~english Contouring,
configurable parameters include: intensity (overall), area information (area id,
color, intensity)
EFFECT_BEAUTY_TRYON_EYESHADOW                   = 708,  ///< \~chinese 眼影,可设
置的参数包括:强度(整体),区域信息(区域id,颜色,强度) \~english Eyeshadow,
configurable parameters include: intensity (overall), area information (area id,
color, intensity)
EFFECT_BEAUTY_TRYON_EYELINER                    = 709,  ///< \~chinese 眼线,可设
置的参数包括:强度(整体),区域信息(区域id,颜色,强度) \~english Eyeliner,
configurable parameters include: intensity (overall), area information (area id,
color, intensity)
EFFECT_BEAUTY_TRYON_EYELASH                     = 710,  ///< \~chinese 眼睫毛,可
设置的参数包括:颜色,强度 \~english Eyelash, configurable parameters include:
color, intensity
EFFECT_BEAUTY_TRYON_STAMPLINER                  = 711,  ///< \~chinese 眼印,可设
置的参数包括:颜色,强度 \~english Eye stamp, configurable parameters include:
color, intensity
// \~chinese 3D 微整形
// \~english 3D micro plastic
EFFECT_BEAUTY_3D_MICRO_PLASTIC                  = 801,
}
```

path:素材包路径

buffer:素材包缓存

### 2.5.2 设置模式

类似美白、磨皮通过mode来区分使用不同类型的美白

```
export const setBeautyMode:(type:BeautyType,mode: number) => boolean;
```

参数说明:

1. type:类型(见2.5.1);

2. mode:需要设置的mode。

美白mode

```
/// \~chinese
/// @brief 美白模式,主要有 3 种不同的美白效果,同时兼容了老的美白效果
/// \~english
/// @brief whiten mode, four modes supported
typedef enum {
    EFFECT_WHITEN_1      = 0,      ///< \~chinese 美白1 \~english mode 1
    EFFECT_WHITEN_2      = 1,      ///< \~chinese 美白2 \~english mode 2
    EFFECT_WHITEN_3      = 2,      ///< \~chinese 美白3 \~english mode 3
    EFFECT_WHITEN_LEGACY = 3,      ///< \~chinese 老美白效果 \~english legacy mode.
} st_effect_whiten_mode;
```

磨皮mode

```
/// \~chinese
/// @brief 磨皮模式
/// \~english
/// @brief smooth mode supported
typedef enum {
    EFFECT_SMOOTH_FACE_ONLY     = 0,      ///< \~chinese 只针对人脸做磨皮处理
\~english smooth only on face
    EFFECT_SMOOTH_FULL_IMAGE    = 1,      ///< \~chinese 对全图做磨皮处理 \~english
whole image smooth
    EFFECT_SMOOTH_FACE_DETAILED = 2,      ///< \~chinese 针对脸部做精细化磨皮处理
\~english high quality smooth on face
    EFFECT_SMOOTH_FACE_REFINE   = 3,      ///< \~chinese 对脸部皮肤细化和改善质感的
磨皮处理 \~english refining and improving the texture of facial skin
} st_effect_smooth_mode;
```

### 2.5.3 设置强度

```
export const setBeautyStrength:(type:BeautyType,value: number) => boolean;
```

参数说明:

type:类型(见2.5.1)

strength:需要设置的强度,范围一般为[0, 1]

### 2.5.4 设置参数

```
export const setBeautyParam:(type:BeautyParamType,value: number) => boolean;
```

参数说明

type:需要设置的类型

```
export constenumBeautyParamType{
//是否为美白开启皮肤分割, 默认为不启用.
EFFECT_BEAUTY_PARAM_ENABLE_WHITEN_SKIN_MASK
}
```

value:是否为美白开启皮肤分割,0 表示不启用,非0表示启用

## 2.6 渲染画面

设置了特效后,将图像原始pixel buffer传入process接口,会自动将添加特效后的画面渲染到Xcomponent组件

上。

```
export const process:(srcBuffer: ArrayBuffer,
format:PixelFormat,width:number,height:number,stride:number,rotate:RotateType,mirr
or:boolean,
  time_stamp:number, outBuffer:ArrayBuffer, outFormat:PixelFormat,
orientation:RotateType, isOrigin:boolean,immediately:boolean) => boolean;
```

参数说明

srcBuffer:图像原始pixel buffer

format:输入图像格式,定义如下

```
export constenumPixelFormat{
ST_PIX_FMT_GRAY8 = 0,   ///< Y    1        8bpp ( \~chinese 单通道8bit灰度像素
\~english Single-channel 8-bit grayscale pixel)
ST_PIX_FMT_YUV420P = 1, ///< YUV  4:2:0   12bpp ( \~chinese 3通道, 一个亮度通道,
另两个为U分量和V分量通道, 所有通道都是连续的. 只支持I420 \~english 3 channels, one
luminance channel, and the other two are U and V component channels, all channels
are contiguous. Only supports I420)
ST_PIX_FMT_NV12 = 2,    ///< YUV  4:2:0   12bpp ( \~chinese 2通道, 一个通道是连续
的亮度通道, 另一通道为UV分量交错 \~english 2 channels, one channel is a contiguous
luminance channel, and the other channel is interleaved UV components)
ST_PIX_FMT_NV21 = 3,    ///< YUV  4:2:0   12bpp ( \~chinese 2通道, 一个通道是连续
的亮度通道, 另一通道为VU分量交错 \~english 2 channels, one channel is a contiguous
luminance channel, and the other channel is interleaved VU components)
ST_PIX_FMT_BGRA8888 = 4,///< BGRA 8:8:8:8 32bpp ( \~chinese 4通道32bit BGRA 像素
\~english 4-channel 32-bit BGRA pixel)
ST_PIX_FMT_BGR888 = 5,  ///< BGR  8:8:8   24bpp ( \~chinese 3通道24bit BGR 像素
\~english 3-channel 24-bit BGR pixel)
ST_PIX_FMT_RGBA8888 = 6,///< RGBA 8:8:8:8 32bpp ( \~chinese 4通道32bit RGBA 像素
\~english 4-channel 32-bit RGBA pixel)
ST_PIX_FMT_RGB888 = 7,  ///< RGB  8:8:8   24bpp ( \~chinese 3通道24bit RGB 像素
\~english 3-channel 24-bit RGB pixel)
ST_PIX_FMT_FLOAT = 8///< Y    1       32bpp ( \~chinese 1通道 32bit float 像
素 \~english Single-channel 32-bit float pixel)
}
```

width:图像宽度

height:图像高度

stride:图像每行像素字节长度

rotate:图像旋转角度,定义如下

```
export constenumRotateType{
ROTATE_0 = 0,
ROTATE_90,
ROTATE_180,
ROTATE_270,
}
```

mirror:图像是否镜像

time_stamp:图像时间戳

outBuffer:经过处理的输出图像pxelBuffer(可为空,只渲染Xcomponent画面。若需保存输出结果,如截图、

录制等,传入的数组长度需保证正确,由图像宽高和输出格式计算得到)

outFormat:输出图像的格式,参考PixelFormat定义

orientation:人像旋转角度,参考RotateType定义

isOrigin:可选,Xcomponent渲染原始画面还是处理后的画面

immediately:可选,是否立即渲染(natvie内部会延迟一帧渲染,用于检测人脸,建议单帧渲染选择是,预

览、视频模式选择否)

## 2.7 其它功能

### 2.7.1 重置内部缓存

```
export const resetPixelReader:() => boolean;
```

sdk内部会延迟一帧渲染,建议截图保存时调用process前调用一次重置,保证输出的图像是输入的图像

### 2.7.2 设置渲染缩放模式

```
export const setResizingMode:(mode:RenderingResizingMode) => void;
```

参数说明

mode:渲染缩放模式,不设置默认为AspectFit模式,定义参考如下

```
/**
```

 * 渲染时的图像缩放模式。

 * 定义了图像在渲染时如何适应目标区域的大小。

```
 */
export constenumRenderingResizingMode {
/**
```

   * 无比例拉伸。

   * 图像会被拉伸以完全填充目标区域,可能会导致图像变形。

```
   */
Stretch,
/**
```

   * 等比例缩放以适应目标区域。

   * 图像会被等比例缩放,以确保图像的宽高比例不变,并且完全适应目标区域。

   * 如果目标区域的宽高比例与图像不同,图像可能会在某些方向上留白。

```
   */
AspectFit,
/**
```

   * 等比例缩放以填充目标区域。

   * 图像会被等比例缩放,以确保图像的宽高比例不变,并且完全填充目标区域。

   * 如果目标区域的宽高比例与图像不同,图像可能会超出目标区域的某些部分。

```
   */
AspectFill,
}
```

### 2.7.3 设置渲染窗口大小

```
export const updateWindowSize:(width:number,height:number) => void;
```

参数说明

width:渲染窗口宽度

height:渲染窗口高度
