# 锐动视频编辑SDK 使用指南 

@rdsdk/vecore HarmonyOS ArkTS 接入说明 

|**项目**|**说明**|
|---|---|
|文档用途|SDK 上架审核及接入方开发参考|
|示例来源|entry 模块对@rdsdk/vecore 的真实调用|
|适用平台|HarmonyOS / ArkTS|
|文档版本|V1.0|
|生成日期|2026-06-18|

提示:本文档聚焦demo 已跑通的接入链路,不作为SDK 全量API Reference。 AppKey 和AppSecret 请使用授权方提供的正式值,文档示例使用占位符。 

## 修订记录 

|**版本**|**日期**|**说明**|
|---|---|---|
|V1.0|2026-06- 18|基于entry 模块当前实现整理SDK 初始化、预览、编辑、导出与 相册保存流程。|

## 目录 

- 1. 文档范围与整体流程 

- 2. 集成准备与VECore 初始化 

- 3. 媒体选择、沙箱路径与最小权限 

- 4. 创建预览与构建视频工程 

- 5. 播放控制与进度监听 

- 6. 编辑能力接入示例 

- 7. 导出视频 

- 8. 保存到系统相册 

- 9. Demo 文件与接口映射 

- 10. 常见问题 

## 1. 文档范围与整体流程 

本文基于HarmonyOS entry 模块中对@rdsdk/vecore 的调用整理,覆盖从SDK 初 始化、媒体选择、预览构建、播放控制、编辑功能开关到导出并保存相册的完整链 路。 

|**阶段**|**核心动作**|**关键接口/类**|
|---|---|---|
|初 始 化|用户点击初始化后建立 VECore 运行环境|VECore.isInitialized, VECore.initialize|
|媒 体 准|通过系统Picker 选择图片或 视频,并复制到应用沙箱|PhotoViewPicker, fs.openSync, fs.copyFileSync|
|备|||

|工 程 构 建|使用媒体路径创建主素材、 场景和VirtualVideo composition|MediaObject, Scene, VirtualVideo.addScene, VirtualVideo.build|
|---|---|---|
|预 览 播 放|绑定预览视图,控制播放、 暂停、拖动进度|VirtualVideoView, setOnPlaybackListener, start, pause, resume, seekTo|
|编 辑 增 强|动态插入或删除背景、文 字、特效、贴纸、配乐等对 象|CaptionExtObject, CaptionLiteObject, EffectInfo, Music, updateScene, insertPip, deletePip|
|导 出 保 存|按当前组合重新组装导出, 成功后保存到系统相册|VideoConfig, ExportListener, VirtualVideo.export, showAssetsCreationDialog|

提示:entry 当前采用“首页初始化- 选择媒体- 跳转编辑页”的流程。选择媒体之 前不构建VECore 预览,避免空路径创建MediaObject。 

## 2. 集成准备与VECore 初始化 

业务侧通过@rdsdk/vecore 引入VECore,并在用户主动点击初始化后执行初始化。 初始化封装需要保持幂等,重复调用时先判断当前状态。 

import { VECore } from '@rdsdk/vecore'; 

const APP_KEY = '<由锐动分配的 AppKey>'; const APP_SECRET = '<由锐动分配的 AppSecret>'; 

```arkts
export class VECoreInitializer { public static initialize(context: Context): void { if (VECore.isInitialized()) { return; } VECore.initialize(context, 'vecore', APP_KEY, APP_SECRET, 
```

'', true); } 

public static isInitialized(): boolean { return VECore.isInitialized(); 

} 

} 

• 建议在业务入口提供明确的初始化动作,初始化成功后再开放媒体选择和编辑入 口。 

• AppKey 和AppSecret 属于授权信息,正式集成时请从安全配置或授权流程中获 取,不要在公开文档中暴露完整密钥。 

• AbilityStage.onCreate 中不强制自动初始化,有利于减少启动开销并让用户动作 与SDK 初始化时机一致。 

## 3. 媒体选择、沙箱路径与最小权限 

entry 使用系统PhotoViewPicker 选择单个图片或视频。该方式由系统选择器完成用 户授权,不需要在module.json5 中声明READ_IMAGEVIDEO 或 WRITE_IMAGEVIDEO,也不需要调用requestPermissionsFromUser 申请媒体读写 权限。 

```arkts
const selectOptions = new photoAccessHelper.PhotoSelectOptions(); = selectOptions.MIMEType photoAccessHelper.PhotoViewMIMETypes.IMAGE_VIDEO_TYPE; = selectOptions.maxSelectNumber 1; 
const photoPicker = new photoAccessHelper.PhotoViewPicker(); const selectResult = await photoPicker.select(selectOptions); const mediaUri = selectResult.photoUris[0]; 
```

Picker 返回的是URI。为了让VECore 按普通文件路径读取媒体,demo 会将URI 内 容复制到应用沙箱目录,再把沙箱路径作为路由参数传入编辑页。 

```arkts
const sourceFile = fs.openSync(mediaUri, fs.OpenMode.READ_ONLY); const targetFile = fs.openSync( targetPath, fs.OpenMode.READ_WRITE | fs.OpenMode.CREATE | fs.OpenMode.TRUNC ); fs.copyFileSync(sourceFile.fd, targetFile.fd); router.pushUrl({ url: 'pages/Index', params: { mediaPath: targetPath } }); 
```

|**权限项**|**是否需要**|**原因**|
|---|---|---|
|ohos.permission.READ_IMAGEVIDEO|不需 要|媒体读取通过PhotoViewPicker 的 用户选择授权完成。|
|ohos.permission.WRITE_IMAGEVIDEO|不需 要|保存相册通过系统创建确认弹窗完 成。|
|requestPermissionsFromUser|不需 要|当前流程没有运行时媒体权限申 请。|

## 4. 创建预览与构建视频工程 

编辑页通过VirtualVideoView 获取VirtualVideo 实例,并基于路由传入的 mediaPath 创建主媒体、场景和composition。 

```arkts
VirtualVideoView({ onLoadEvent: (virtualVideo: VirtualVideo, surfaceId?: string): void => { this.virtualVideo = virtualVideo; this.onVirtualVideoViewLoad(virtualVideo, surfaceId); this.veBuild(); 
} }); 
const mediaObject = new MediaObject(mediaPath); mediaObject.setShowAngle(10); mediaObject.setIntrinsicDuration(20); 
const scene = new Scene(mediaObject); virtualVideo.addScene(scene); virtualVideo.build(0, 0x000000); 
```

• MediaObject 接收的是应用可访问的本地文件路径,demo 中来自PhotoPicker URI 复制后的沙箱路径。 

- Scene 是主视频场景容器,背景、转场等场景级能力挂载在Scene 上。 

- VirtualVideo 是组合视频工程对象,addScene、addPip、addMusic、build、 export 均围绕该对象完成。 

## 5. 播放控制与进度监听 

预览播放器通过VirtualVideo 提供的控制接口完成播放、暂停、恢复、停止和跳转。 页面使用setOnPlaybackListener 接收准备完成、进度更新、播放完成和错误事件。 

```arkts
virtualVideo.setOnPlaybackListener({ onPlayerPrepared: (): void => { = this.currentPlaybackS virtualVideo.getCurrentPosition(); = this.totalPlaybackS virtualVideo.getDuration(); }, onGetCurrentPosition: (position: number): void => { = this.currentPlaybackS virtualVideo.getCurrentPosition(); }, onPlayerCompletion: (): void => { = this.isPlaying false; }, onPlayerError: (what: number, extra: number, info?: string): boolean => { = this.isPlaying false; return true; 
```

} }); 

|**用户动作**|**调用接口**|**说明**|
|---|---|---|
|播放|virtualVideo.start()|从当前位置开始预览。|
|暂停|virtualVideo.pause()|暂停当前预览并保留播放位置。|
|恢复|virtualVideo.resume()|从暂停位置继续预览。|
|停止|virtualVideo.stop()|停止预览,导出前会先停止当前播放。|
|拖动进度|virtualVideo.seekTo(timeS)|按秒跳转到指定时间点。|

## 6. 编辑能力接入示例 

entry 使用Checkbox 动态启用或关闭背景、文字、特效、贴纸和配乐。为了避免重 复叠加对象,页面会保存当前对象引用,开启时创建并插入,关闭时按引用删除。 

|**能力**|**开启方式**|**关闭方式**|
|---|---|---|
|背 景|Scene.setBackground(0xBB0000) + VirtualVideo.updateScene(scene, true)|Scene.clearBackground() + updateScene|
|文 字|CaptionExtObject + CaptionItem + insertPip(caption, null, true)|deletePip(caption, true)|
|贴 纸|CaptionLiteObject + setShowRectF + setTimelineRange + insertPip|deletePip(captionLite, true)|
|特 效|EffectInfo(configPath) + setTimelineRange + insertPip|deletePip(effect, true)|
|配 乐|Music.create(path) + setTimelineRange + addMusic + updateMusic|clearMusic + updateMusic|

### 6.1 文字 

```arkts
const caption = new CaptionExtObject(); caption.setAutoSize(true); caption.setConfigJsonPath(configPath, false); 
const item = new CaptionItem(); item.setStartTime(0); item.setDuration(10); item.setTextContent('示例文字'); item.setTextColor(0xAA00FF00); item.setFontFile(fontPath); caption.addLabel(item); 
```

caption.setTimeline(0, 20); caption.refreshShowRectF(Rect.create(0.0, 0.2, 1, 1), false); caption.setParentSize(previewWidth, previewHeight, true); virtualVideo.insertPip(caption, null, true); 

### 6.2 贴纸与特效 

```arkts
const sticker = new CaptionLiteObject(stickerPath); sticker.setShowRectF(showRect); sticker.setTimelineRange(0, 20); virtualVideo.insertPip(sticker, null, true); 
const effect = new EffectInfo(effectConfigPath); effect.setTimelineRange(0, 20); virtualVideo.insertPip(effect, null, true); 
```

### 6.3 配乐 

```arkts
const music = Music.create(musicPath); music.setTimelineRange(0, 12); virtualVideo.addMusic(music); virtualVideo.updateMusic(); 
```

virtualVideo.clearMusic(); virtualVideo.updateMusic(); 

### 6.4 其他demo 能力 

|**能力**|**相关接口**|**说明**|
|---|---|---|
|滤镜 /调 节|VisualFilterConfig, EffectInfo, EffectMultiple|可将滤镜和调节作为 EffectInfo 组合后插入 PIP。|
|遮罩|MaskObject, MediaObject.setMaskObject, MediaObject.refresh|对指定媒体对象应用遮 罩资源。|
|转场|Transition, TransitionType.TRANSITION_FOLDER, Scene.setTransition|通过转场资源目录配置 场景转场。|
|默认 媒体 信息|PreviewPlayerService.getDefaultMediaInfo|用于读取媒体默认信 息,demo 中作为辅助 能力示例。|
|截图|VirtualVideo.getSnapshot|用于获取预览帧 PixelMap,demo 中 包含保存示例。|

## 7. 导出视频 

导出前demo 会停止当前预览、reset VirtualVideo,然后按当前媒体路径和功能开 关重新组装composition。导出不依赖系统相册权限,输出路径先落到应用沙箱 exports 目录。 

virtualVideo.stop(); virtualVideo.reset(); setupComposition(virtualVideo); 

```arkts
const outputPath = `${context.filesDir}/export s/export _${Date.now()}.mp4`; virtualVideo.export(outputPath, videoConfig, listener); 
```

### 7.1 VideoConfig 

```arkts
const videoConfig = new VideoConfig(); videoConfig.setVideoSize(alignedWidth, alignedHeight); videoConfig.setVideoFrameRate(30); videoConfig.setVideoEncodingBitRate(8 * 1000 * 1000); videoConfig.setAudioEncodingParameters(2, 44100, 128 * 1000); videoConfig.enableHWDecoder(true); videoConfig.enableHWEncoder(true); 
```

- 预览尺寸可用时使用当前预览尺寸,宽度按16 对齐,高度按2 对齐。 

- 预览尺寸不可用时回退到720 x 1280。 

- 导出期间禁用重复点击,并在onExporting 中更新导出进度。 

### 7.2 ExportListener 

```arkts
const listener: ExportListener = { onExportStart: (): void => { = this.export Progress 0; }, onExporting: (progress: number, total: number): boolean => { this.export Progress = Math.floor(progress * 100 / Math.max(total, 1)); return true; }, onExportEnd: (result: number, extra: number, info?: string): void => { const success = result === VirtualVideo.RESULT_SUCCESS; // success 时保存相册,failed 时提示错误并恢复预览 } }; 
```

提示:onExporting 必须返回true 才会继续导出;如果返回false,导出流程会被中 断。 

## 8. 保存到系统相册 

导出成功后,demo 将沙箱mp4 转为file URI,并调用系统相册创建确认弹窗。用户 确认后,再把沙箱文件复制到系统返回的目标URI。该流程符合最小权限原则,不新 增媒体读写权限。 

```arkts
const srcFileUris: Array<string> = [fileUri.getUriFromPath(outputPath)]; const configs: Array<photoAccessHelper.PhotoCreationConfig> = [{ fileNameExtension: 'mp4', photoType: photoAccessHelper.PhotoType.VIDEO, subtype: photoAccessHelper.PhotoSubtype.DEFAULT }]; 
const helper = photoAccessHelper.getPhotoAccessHelper(context); const result = await helper.showAssetsCreationDialog(srcFileUris, configs); if (result.length > 0) { const srcFile = fs.openSync(srcFileUris[0], fs.OpenMode.READ_ONLY); const desFile = fs.openSync(result[0], fs.OpenMode.READ_WRITE | fs.OpenMode.CREATE); fs.copyFileSync(srcFile.fd, desFile.fd); } 
```

   - 保存成功后,页面Toast 提示“视频已保存到相册”。 

   - 用户取消系统弹窗时,不显示保存成功提示,只在页面状态中说明取消保存。 

   - 保存完成或取消后,demo 会清理沙箱导出文件并恢复预览。 

9. Demo 文件与接口映射 

|**文件**|**职责**|**关键SDK/系统接口**|
|---|---|---|
|application/VECoreInitializer.ets|封装|VECore.initialize, VECore.isInitialized|

||VECore 初始化 和初始 化状态 判断||
|---|---|---|
|pages/Home.ets|首页初 始化入 口和媒 体选择 入口|PhotoViewPicker, VECoreInitializer|
|pages/MediaHelper.ets|复制 Picker URI 和 rawfile 资源到 应用沙 箱|fs.openSync, fs.copyFileSync|
|pages/Index.ets|预览、 播放、 编辑开 关、导 出和保 存相册 主流程|VirtualVideoView, VirtualVideo, Scene, MediaObject, VideoConfig, ExportListener|
|pages/LoadHelper.ets|准备特 效资源 并触发 build|EffectInfo, VirtualVideo.build|
|pages/TextHelper.ets|准备字 体和文 字素材 资源|CaptionExtObject 相关素材路径|
|pages/PathUtils.ets|导出文|fileUri,|

|件保存|photoAccessHelper.showAssetsCreationDialog|
|---|---|
|到系统||
|相册||

## 10. 常见问题 

|**问题**|**处理建议**|
|---|---|
|选择媒体按钮不可用|确认VECoreInitializer.initialize(context) 已成功执行,且 VECore.isInitialized() 返回true。|
|MediaObject 创建 失败或预览为空|确认传入的是应用可访问的沙箱文件路径,不要直接把Picker URI 传给MediaObject。|
|文字、贴纸或特效重 复叠加|开启时保存对象引用,关闭时使用同一引用deletePip;重新导 出前reset 并统一setupComposition。|
|导出中断|确认ExportListener.onExporting 返回true,并检查 outputPath 所在目录已创建。|
|保存相册没有成功提 示|用户可能取消了系统创建确认弹窗;只有result 返回目标URI 且复制成功后才提示保存成功。|
|是否需要媒体权限|当前PhotoPicker + 系统相册创建确认流程不需要 READ_IMAGEVIDEO、WRITE_IMAGEVIDEO 或运行时媒体权 限申请。|
