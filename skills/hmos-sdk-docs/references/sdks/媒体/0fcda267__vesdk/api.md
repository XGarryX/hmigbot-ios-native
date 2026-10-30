# 接口文档 

class SXTemplate 

/** * 初始化一个模板实例 * @param templateFolder 模板文件夹路 径 * @param templateUsage 该模板的使用模式。注意,这里设置完 使用模式后模板的使用方式要和模式一致,不然不会生效 */ public static createWithFolder(templateFolder: string, templateUsage: TemplateUsage): SXTemplate { 

/** * 使用初始化一个模板实例 * @param templateFolder 模板文件 夹路径 * @param json 模板 json 内容 * @param templateFolder 模板 文件夹路径 * @param configType 模板类型 * @param templateUsage 该模板的使用模式。注意,这里设置完使用模式后模 板的使用方式要和模式一致,不然不会生效 */ 

public static createWithJson(templateFolder: string, json: string, configType: ConfigType, templateUsage: TemplateUsage): SXTemplate 

/** * 获取配置文件内记录的主视频合成宽度 * @return 视频宽度, 像素为单位,如果为 0 表示模板载入失败 */ public mainCompWidth(): number { 

/** * 获取配置文件内记录的主视频合成高度 * @return 视频高度, 像素为单位,如果为 0 表示模板载入失败 */ public mainCompHeight(): number { 

/** * 获取模板版本 * @return 模板版本 */ public getVersion(): string { 

/** * 检测模板的 version 是否被当前引擎全部支持 

* @return 1 表示模板版本高于引擎版本,不是完整支持, 返回 0 , -1 表示可以完整支持 */ public compareWithCurrentVersion(): number { 

/** * 获取当前 VE 引擎版本号 * 可用来和 template 实例中的版本号作 

对比 , 模板是否被当前引擎全部支持 * @return VE 引擎版本号 */ public static getVECurrentVersion(): string { 

/** * 获取配置文件内记录的视频帧速率 * @return 视频帧速率 */ public frameRate(): number { 

/** * 配置文件中记录的模板时长,对于动态模板不可靠 * @return 模板时长,单位为帧 */ public configDuration(): number { 

/** * 获取视频背景颜色 * @return 视频背景颜色 */ public backgroundColor(): number { 

/** * 设置视频背景颜色 * @param color 视频背景颜色 ARGB */ public setBackgroundColor(color: number): void { 

/** * 设置用户可修改素材文件路径 * * @param filePaths 要替换的 素材路径数组 * @param adapt 是否适配视频素材时长,只对动态模 板有效 * @warning 该接口只有在 commit 之前调用有效 * @note 对 于标准模板,这里设置的文件路径的顺序要和 config.json 内 assets 数组 中素材的先后顺序保持一致 

* 对于动态模板,这里直接传入用户添加的所有主图片文件路径即可 */ public setReplaceableFilePathsIfAdapt(filePaths, adapt: boolean): void { 

/** * 设置用户可修改素材文件路径 * * @param filePaths 要替换的 素材路径数组 * @param adapt 是否适配视频素材时长,只对动态模 板有效 * @param checkUnsupportedFiles 是否检查 sdk 不支持的文 件,如果检查,可以通过 {@link #getUnsupportedFiles()} 获取不支 持的素材路径数组 * @warning 该接口只有在 commit 之前调用有效 * @note 对于标准模板,这里设置的文件路径的顺序要和 config.json 内 assets 数组中素材的先后顺序保持一致,对于动态模板,这里直接传 入用户添加的所有主图片文件路径即可 */ public setReplaceableFilePathsIfCheck(filePaths: string[], adapt: boolean, checkUnsupportedFiles: boolean): void { 

/** * 设置用户可修改素材文件路径 * * @param filePaths 要替换的 

素材路径数组 * @warning 该接口只有在 commit 之前调用有效 * 对 于标准模板,这里设置的文件路径的顺序要和 config.json 内 assets 数组 中素材的先后顺序保持一致 * 对于动态模板,这里直接传入用户添加 的所有主图片文件路径即可 */ public setReplaceableFilePaths(filePaths: string[]): void { 

/** * 根据 UI key 来修改某个指定素材的文件路径 * @warning 该接 口只有在 commit 之前调用有效 * @param filePath 新的文件路径 * @param uiKey 指定的 UI key */ public setFileForAsset(uiKey: string, filePath: string): void { 

/** * 根据一个 UI Key 来获取 config.json 中记录的某个指定素材文件 的配置信息 * @param uiKey 指定的 UI key * @return 该素材对应的 配置信息 */ public getAssetJsonForUIKey(uiKey: string): string { 

/** * commit 模板配置信息,创建底层渲染对象 * @return 成功或已 经 commit 过返回 ture ,否则返回 false */ public commit(): boolean { 

/** * 获取模板的真实时长 * @warning 该接口只有在 commit 之后调 用有效 * @return 时长,帧为单位 */ public realDuration(): number { 

/** * 添加水印 * @warning 该接口只有在 commit 之后调用有效 * @param path 水印图片路径 * @param position 水印起始坐标,以左 上角为原点 * @param scale 水印缩放值,以水印自身左上角为原 点, x 、 y 都为 1 时为原图大小 * @param startTime 开始时间,以秒为 单位 * @param duration 水印持续时长,以秒为单位, 0 表示整个视 频时长 * @return 水印 ID , {@linkplain #removeWatermark 删除水 印 } 时使用 */ public addWatermark(path: string, positionX: number, positionY: number, scaleX: number, scaleY: number, startTime: number, duration: number): string { 

/** * 添加水印序列帧,循环播放 * @warning 该接口只有在 commit 之后调用有效 * @param paths 帧动画图片路径集合 * @param position 水印起始坐标,以左上角为原点 * @param scale 水印缩放 值,以水印自身左上角为原点, x 、 y 都为 1 时为原图大小 * @param startTime 开始时间,以秒为单位 * @param duration 水印持续时 长,以秒为单位 * @return 水印 ID , {@linkplain #removeWatermark 删除水印 } 时使用 */ public 

addWatermarks(paths: string[], positionX: number, positionY: 

number, scaleX: number, scaleY: number, startTime: number, duration: number): string { 

/** * 删除水印 * @param watermarkId 水印 ID */ 

public removeWatermark(watermarkId: string): void { 

/** * 开启素材预加载 * 开启后会提升渲染速度,同时会增加内存的 使用,小内存手机谨慎启用 * * @warning 在 commit 之前调用有效 */ public enableSourcePrepare(): void { this.mEnableSourcePrepare = true; } 

/** * 设置素材预加载缓存大小 * @param MB 缓存大小,单位为 M 字 节 */ public setCacheSize(MB: number): void { this.mCacheSize = MB * 1024 * 1024; } 

/** * 获取当前的滤镜对象 * @return 滤镜对象 */ public getCurrentFilter(): SXFilter { return this.mFilter; } 

/** * 设置滤镜 * @param filter 滤镜对象 * @return 滤镜 ID */ public setFilter(filter: SXFilter): string { if (this.mFilter != null) { SXVideo.getSDKContext().sxvideo_template_remove_filter(this.mRenderContext, this.mFilterId); } this.mFilter = filter; if (filter == null) { return null; } this.mFilterId = 

SXVideo.getSDKContext().sxvideo_template_add_filter(this.mRenderContext, filter.mNativeConfig, this.mFilterId); // Log.e("TEST", "setFilter: id = " + mFilterId); return this.mFilterId; } 

/** * 设置模板可替换素材,实现高级字幕替换和图片替换 * 默认不 适配视频素材时长 * 使用此接口替换文字需文字渲染器或者设置文字 生成图片的缓存目录、字体文件或字体目录 * 替代 {@link #setReplaceableFilePaths(String[])} 和 {@link 

#setDynamicSubFiles(String)} * * @param json json 格式参考下面链 接 * @return 是否替换成功 * * @see 

#setTextRender(SXTextRender) * @see #setFontFiles(String[]) * @see #setFontFolder(String) * @see <a href="http:// www.seeshiontech.com/docs/page_103.html">ReplaceableJson 说 明与规范 </a> */ public setReplaceableJson(json: string): boolean { 

/** * 设置模板可替换素材,实现高级字幕替换和图片替换 * 使用此 接口替换文字需文字渲染器或者设置文字生成图片的缓存目录、字体 文件或字体目录 * 替代 {@link #setReplaceableFilePaths(String[])} 和 {@link #setDynamicSubFiles(String)} * * @param json json 格式 参考下面链接 * @param adapt 是否适配视频素材时长,只对动态模 板有效 * @return 是否替换成功 * * @see 

#setTextRender(SXTextRender) * @see #setFontFiles(String[]) * @see #setFontFolder(String) * @see <a href="http:// www.seeshiontech.com/docs/page_103.html">ReplaceableJson 说 明与规范 </a> */ public setReplaceableJsonIfAdapt(json: string, adapt: boolean): boolean { 

/** 

* 设置字体文件,使用 replaceJson 替换的文字会使用此字体 * @param fontFiles 字体文件 */ public static setFontFiles(fontFiles: string[]): void { 

/** * 设置字体目录,自动查找目录下的字体 * @param fontFolder 字体目录 */ public static setFontFolder(fontFolder: string): void { 

/** * 设置输出分辨率比例 * @param ratio 分辨率比例 */ public setResolutionRatio(ratio: SXResolutionRatio): void { 

/** * 获取设置分辨率后实际输出宽度 * @return 设置分辨率后实际 输出宽度 */ public getOutputWidth(): number { 

/** * 获取设置分辨率后实际输出高度 * @return 设置分辨率后实际 输出高度 */ public getOutputHeight(): number { 

/** * 设置是否保留替换的视频素材中的音频 * @param keep 是否保 留 */ public setKeepAssetAudio(keep: boolean): void { 

class SXTemplatePlayer 

/** * 替换背景音乐 ,回到视频开始位置 * @param path 新的背景音 乐文件路径 */ public replaceAudio(path: string): void { /** 

* 开始预览 */ public start(): void { 

/** * 设置时间进度 * @param frame 新的时间进度,帧为单位 */ public seek(frame: number): void { 

/** * 暂停预览 */ public pause(): void { 

/** * 获取视频总长度,帧为单位 * @return 长度 */ public getDuration(): number {
