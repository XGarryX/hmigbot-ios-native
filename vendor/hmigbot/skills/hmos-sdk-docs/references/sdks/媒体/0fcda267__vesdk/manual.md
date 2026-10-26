# 使用说明 

# 标准模板创建流程 

调用 SXTemplate 类的构造函数,并传入模板路径和 SXTemplate.TemplateUsage 作为参数构建一个 SXTemplate 实例对 象。 

调用 SXTemplate 实例的 setReplaceableJson 函数,并传入需要替换素 材的 Json 字符串作为参数来实现高级素材替换。 

( 可选 ) 在上一步中替换文字时需要设置文字生成图片缓存目录,调用 SXTemplate 实例的 setDrawTextCacheDir 函数,并传入缓存目录作为 参数。 

( 可选 ) 开启素材预加载,开启后会提升渲染速度,同时会增加内存的 使用,小内存手机谨慎启用,调用 SXTemplate 实例的 enableSourcePrepare 函数。 

调用 SXTemplate 实例的 commit 函数创建渲染对象。 

( 可选 ) 利用 UI Key 等自定义逻辑对模板渲染对象进行精细修改调节。 

( 可选 ) 调用 SXTemplateRender 的构造函数,并传入 SXTemplate 实 例、音乐路径、输出文件路径作为参数构建一个 SXTemplateRender 实例对象。 

调用 SXTemplateRender 实例的 setRenderListener 函数, 并传入 SXRenderListener 对象设置视频渲染状态监听。 

调用 SXTemplateRender 实例的 start 方法开始渲染。 

# 代码示例 

String path = "";// 模板根目录 

String json = "";// 替换资源 json 

SXTemplate mTemplate = new SXTemplate(path, SXTemplate.TemplateUsage.kForRender); 

mTemplate.setReplaceableJson(json); 

mTemplate.enableSourcePrepare(); 

mTemplate.setDrawTextCacheDir(getExternalCacheDir().getPath()); 

mTemplate.commit(); 

String outputPath = // 生成的视频路径 

// 音频路径传 null 会默认寻找模板根目录下的 music.mp3 或 music.aac 音频文件 

SXTemplateRender render = new SXTemplateRender(mTemplate, null, outputPath); 

//listener 方法在 UI 线程回调 

render.setRenderListener(new SXRenderListener() { 

@Override 

public void onStart() { 

} 

@Override 

public void onUpdate(int progress) { 

// 进度回调, progress 为第几帧 

} 

@Override 

public void onFinish(boolean success, String msg) { 

//success 为 true 渲染成功,为 false 时渲染失败, msg 是失败原因 

} 

@Override 

public void onCancel() { 

} 

}); 

render.start(); 

错误码 

onFinish 回调 success 为 false 时可调用 SXTemplateRender 的 getErrorCode 方法获取错误码 

NO_ERROR = 0; 

UNKNOWN_ERROR = 1; // 其它异常,可在 onFinish 回调的 msg 参数 中查看具体信息 

CANCELLED = 2; // 渲染取消 

LICENSE_ERROR = 3; // license 包名不匹配,过期,不包含模板所 需所有功能等错误 

CODEC_ERROR = 4; // 硬件编码器 MediaCodec 配置错误 

NETWORK_ERROR = 5; // 按次付费类型请求网络异常 

AUDIO_NOT_SUPPORT = 6; // 音频文件不支持
