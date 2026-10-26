# 锐动视频编辑SDK 

## 1.安装 

添加到模块oh-package.json5 

"dependencies": { "@rdsdk/vecore": "~1.0.0", 

} 

## 2.部分接口说明 

VECore.ets 

VECore 是SDK 初始化入口,建议在应用启动阶段只初始化一次,初始化完成后再创建 VirtualVideo。 

|**接口**|**说明**|
|---|---|
|VECore.initialize(context, rootPath, appKey, appSecret, licenseKey?, debuggable?, forceSWDecoder?)|初始化VECore。context为应用上下文; rootPath为SDK 工作目录标识;appKey、 appSecret为授权信息;licenseKey可选; debuggable、forceSWDecoder为可选开关。重 复调用会直接返回。|
|VECore.isInitialized()|获取VECore 是否已经初始化。|
|VECore.getVersion()|获取当前VECore 版本号。|

### VirtualVideo.ets 

> VirtualVideo 是虚拟视频编辑和播放入口,负责管理场景、叠加元素、音频、预览、缩略图和导出。 

|**接口**|**说明**|
|---|---|
|bindSurface(context, surfaceId)|绑定预览渲染surface。通常由 VirtualVideoView创建后自动调用。|
|setPreviewer(param, maxSide?)|设置预览参数和最大输出边长。|
|addScene(scene)|添加主媒体场景。Scene下包含 MediaObject。|
|addPip(pip)|添加叠加元素,例如字幕、贴纸、特效、滤镜组 合等。|

|addMusic(music)|添加配乐。|
|---|---|
|setWatermark(watermark)|设置或清除全局水印,传入null表示清除。|
|setPreviewAspectRatio(aspectRatio)|设置预览画面宽高比。未设置时会根据场景自动 计算。|
|build(seekTo?, bgColor?)|构建并加载预览,seekTo单位为秒,bgColor 为背景色。调用前必须已经绑定surface。|
|release()/reset()|释放或重置当前虚拟视频内部资源。|
|getLoadResult()|获取构建后的加载结果,包含底层视频句柄。|
|getPreviewSize()|获取当前预览输出尺寸。|
|start()/pause()/resume()/ stop()|播放控制。|
|seekTo(timeS)|跳转到指定时间点,单位为秒。|
|getDuration()/getCurrentPosition()/ isPlaying()|获取总时长、当前播放进度和播放状态。|
|setOnPlaybackListener(listener)|设置播放器监听,接收准备完成、错误、播放完 成、进度等回调。|
|insertPip(pip, insertAt, refresh)|在build()后实时插入叠加元素。|
|updatePIPInsertAt(pip, insertAt, refresh)|在build()后实时修改叠加元素层级。|
|updatePip(pip, refresh)|在build()后实时更新叠加元素参数。|
|deletePip(pip, refresh)|在build()后实时删除叠加元素。|
|insertScene(scene, index?, refresh?)|在build()后实时插入场景。|
|updateScene(scene, refresh)|在build()后实时更新场景媒体内容。|
|removeScene(scene, refresh?)|在build()后实时删除场景。|
|clearMusic()/updateMusic()|清空或刷新配乐列表。|
|fastCaptionLite(lite, refresh)|字幕资源未变化时,快速刷新字幕参数。|
|updateSubtitleObject(pip, refresh)|字幕资源路径变化时刷新字幕对象。|
|getSnapshot(timeSecond, snapshot)|获取指定时间点缩略图,timeSecond单位为 秒,结果写入PixelMap。|

|getSnapshotData(timeSecond, width, height, bufferSize)|获取指定时间点缩略图原始数据。|
|---|---|
|measureLabel(width, height, callback)|测量字幕尺寸。|
|export(path, videoConfig, listener)|按VideoConfig导出视频,并通过 ExportListener接收导出进度和结果。|

#### 注意事项: 

- 所有实时操作应在 build() 之后调用,主要影响预览。 

- 导出和获取缩略图会按当前素材数据重新加载,建议不要与预览实例共用同一个 VirtualVideo。 

- 获取缩略图时建议创建新的 VirtualVideo 和新的素材对象,避免与预览实例共享状态。 

## 3.示例 

### 初始化 

```arkts
import { AbilityStage } from '@kit.AbilityKit'; 
```

import { VECore } from '@rdsdk/vecore'; 

const APP_KEY = 'your app key'; const APP_SECRET = 'your app secret'; 

```arkts
export default class MyStage extends AbilityStage { onCreate(): void { VECore.initialize(this.context, 'vecore', APP_KEY, APP_SECRET, '', true); } } 
```

### 创建预览并加载素材 

import { MediaObject, Scene, VirtualVideo, VirtualVideoView } from '@rdsdk/vecore'; 

import common from '@ohos.app.ability.common'; 

@Component struct PreviewPage { 

private context = getContext(this) as common.UIAbilityContext; 

private virtualVideo: VirtualVideo | null = null; 

private loadMedia(mediaPath: string): void { 

if (this.virtualVideo === null) { 

return; 

} 

const media = new MediaObject(mediaPath); 

const scene = new Scene(media); 

this.virtualVideo.addScene(scene); 

this.virtualVideo.setOnPlaybackListener({ 

onPlayerPrepared: (): void => { 

const size = this.virtualVideo!.getPreviewSize(); 

console.info(`preview ready: ${size.width}x${size.height}`); 

}, 

onPlayerError: (what: number, extra: number, errorInfo?: string): boolean => { 

console.error(`preview error: ${what}, ${extra}, ${errorInfo ?? ''}`); 

return true; 

}, 

onGetCurrentPosition: (position: number): void => { 

console.info(`position: ${position}`); 

}, 

onPlayerCompletion: (): void => { 

console.info('preview completed'); 

}, 

}); 

this.virtualVideo.build(0, 0xFF000000); 

} 

build() { 

VirtualVideoView({ 

onLoadEvent: (virtualVideo: VirtualVideo, surfaceId?: string): void => { 

this.virtualVideo = virtualVideo; console.info(`surfaceId: ${surfaceId ?? ''}`); 

this.loadMedia(`${this.context.filesDir}/input.mp4`); 

}, 

}) 

.width('100%') 

.height('100%') 

} 

} 

### 播放控制 

this.virtualVideo?.start(); 

this.virtualVideo?.pause(); this.virtualVideo?.resume(); this.virtualVideo?.seekTo(3); 

this.virtualVideo?.stop(); 

const duration = this.virtualVideo?.getDuration() ?? 0; 

const position = this.virtualVideo?.getCurrentPosition() ?? 0; const playing = this.virtualVideo?.isPlaying() ?? false; 

### 实时更新叠加元素 

import { CaptionLiteObject, Rect } from '@rdsdk/vecore'; 

```arkts
const caption = new CaptionLiteObject(`${this.context.filesDir}/sticker.png`); 
```

caption.setTimelineRange(0, 5); 

caption.setShowRectF(Rect.create(0.1, 0.1, 0.5, 0.5)); 

// build() 前添加到素材列表。 

this.virtualVideo?.addPip(caption); 

// build() 后修改参数并刷新预览。 

caption.setShowRectF(Rect.create(0.2, 0.2, 0.6, 0.6)); 

this.virtualVideo?.updatePip(caption, true); 

### 获取缩略图 

import { MediaObject, Scene, VirtualVideo } from '@rdsdk/vecore'; 

import image from '@ohos.multimedia.image'; 

const width = 320; 

const height = 180; 

const pixelMap = image.createPixelMapSync({ 

size: { width, height }, 

pixelFormat: image.PixelMapFormat.RGBA_8888, 

editable: true, 

}); 

const snapshotVideo = new VirtualVideo(); 

snapshotVideo.addScene(new Scene(new MediaObject(`${this.context.filesDir}/input.mp4`))); 

snapshotVideo.getSnapshot(1, pixelMap); 

snapshotVideo.release(); 

### 导出视频 

import { MediaObject, Scene, VideoConfig, VirtualVideo } from '@rdsdk/vecore'; 

const exportVideo = new VirtualVideo(); 

exportVideo.addScene(new Scene(new MediaObject(`${this.context.filesDir}/input.mp4`))); 

```arkts
const config = new VideoConfig(); config.setVideoSize(1280, 720); config.setVideoFrameRate(30); 
config.setVideoEncodingBitRate(8 * 1024 * 1024); 
export Video.export(`${this.context.filesDir}/output.mp4`, config, { onExportStart: (): void => { console.info('export start'); }, onExporting: (progress: number, max: number): boolean => { console.info(`export progress: ${progress}/${max}`); return true; }, onExportEnd: (result: number, extra: number, info?: string): void => { console.info(`export end: ${result}, ${extra}, ${info ?? ''}`); export Video.release(); }, 
```

});
