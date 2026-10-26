# FaceID SDK 接入文档 

V5.8.13 

变更和修订历史记录 

文档编号: 版本号 更新日期 修改记录 

5.0.3 

2021-12-24 SDK 增强版全新上线,好体验、更安全 

5.0.4 

2022-02-15 

SDK 验证过程中质量检测效果优化 

5.1.0 

2022-03-24 SDK 活体界面增加 “ 小提示 ” 配置功能 

5.1.1 

2022-04-08 

SDK 示例代码优化,集成更便捷 

5.2.0 

# 2022-04-20 

SDK 设备风险检测功能优化提升 

5.3.0 

2022-05-18 

SDK 防注入能力显著提升 

5.3.1 

2022-05-31 

SDK 引入全新相机签名算法,显著提升防注入攻击能力 

5.5.1 

# 2022-09-06 

SDK 增加动作 + 炫彩组合活体,双重保障更安全;如需请前往控台进 行配置 

5.5.2 

2022-11-21 

SDK 通过率提升 

5.5.3 

2022-11-29 

SDK 可采集高清照片,提升检出能力 

5.5.4 

2022-12-01 

# SDK 界面提示功能优化 

5.5.5 

2022-12-21 

SDK 动作活体视频留存优化 

5.5.6 

2023-02-17 

SDK 风控策略优化 

5.5.7 

2023-04-06 

SDK 优化检测逻辑 

5.5.8 

2023-04-20 

SDK 支持活体录屏留证功能 

5.6.2 

2023-08-07 

SDK 眼镜场景通过率优化提升 

5.6.5 

2023-09-14 

SDK 新增距离活体,更安全,更放心 

5.6.6 

2023-09-28 

# SDK 性能优化 

5.6.8 

2023-10-26 

SDK 活体数据加密保护优化 

5.6.9 

2023-11-17 

SDK 相机签名逻辑优化 

5.7.0 

2023-12-04 

SDK 海外模式 UI 样式优化 

5.7.1 

2023-12-06 

SDK 安全校验逻辑优化 

5.7.2 

2023-12-29 

SDK 动作活体通过率策略优化 

5.7.3 

2024-01-22 

SDK 数据安全策略优化 

5.7.4 

2024-01-24 

SDK 性能优化 & 问题修复 

5.7.5 

# 2024-03-05 

# SDK 视频录制存储优化 

—— 

# 2024-03-21 

鸿蒙初版( V5.7.0H )可集成,补充鸿蒙集成说明,请关注文档 2.3 与 3.3 

5.7.6 

2024-04-19 

# 获取配置环节增加缓冲页 

5.7.7 

2024-04-29 

SDK 集成方案增加兼容模式 

5.7.8 

2024-05-11 

SDK 兼容横屏 & 本地存储模式优化 

5.7.9 

2024-05-22 

SDK 增加兼容模式及问题修复 

5.7.10 

2024-06-07 

SDK 支持静音功能 

# 5.7.11 

# 2024-06-24 

# SDK 界面 UI 配置功能优化 

5.7.12 

2024-07-11 

SDK 动作活体支持指定动作 

5.7.13 

2024-07-22 

SDK 距离活体支持语音功能 

5.7.14 

2024-08-19 

SDK 性能优化 & 返回后台逻辑优化 

5.7.15 

2024-09-29 

SDK 设备风险检测功能增强 

5.7.18 

2024-10-18 

SDK 性能及兼容性优化 

5.7.19 

2024-11-15 

SDK 设备指纹优化 

5.7.20 

2024-11-29 

SDK 兼容模式优化 

5.7.21 

2024-12-09 

SDK 支持透传模式 

5.8.1 

2025-02-28 

SDK 动作活体支持极速模式及灵动活体优化 

目 录 

5.7.6 3 

1 活体认证简介 6 

1.1 MegLiveStill SDK 6 

1.2 SDK 兼容性 6 

1.3 活体认证逻辑 6 

2 SDK 集成 6 

2.1 Android 集成 6 

2.2 iOS 集成 9 

2.2.1 添加 Framework 文件到项目 9 

2.2.2 添加资源文件到项目 9 

2.2.3 引入所需的系统库 9 

2.2.4 添加项目权限 9 

2.3 鸿蒙集成 10 

3 SDK 接口 10 

3.1 Android 接口 10 

3.1.1 入口类 MegLiveManager 10 

3.1.2 MegLiveDetectConfig 检测配置类 13 

3.1.3 MegLiveDetectListener 检测监听回调 14 

3.1.4 MegLiveImageDataListener 兼容模式检测结果回调 16 

3.1.5 MegDataSyncCallback 透传模式同步接口回调 16 

3.1.6 MegDataSyncResponse 透传模式通知 SDK 同步结果接口 17 

3.1.7 错误码 18 

3.2 iOS 接口 20 

3.2.1 类 MegLiveV5DetectManager 20 

3.2.2 可配置类 26 

3.2.3 类 MegLiveV5DetectError 29 

3.2.4 枚举 29 

3.3 鸿蒙接口 31 

3.3.1 入口类 MegLiveManager 31 

3.3.2 检测配置类 34 

3.3.2.1 MegLiveDetectConfig 34 

3.3.2.2 MegLiveDetectModel 34 

3.3.3 检测监听回调 34 

3.3.4 错误码 37 

# 4 SDK 使用说明 39 

# 4.1 UI 自定义 39 

# 4.1.1 Android UI 自定义 39 

4.1.2 iOS UI 自定义 39 

# 4.3 资源外部加载 40 

# 4.3.1 Android 资源外部加载 40 

4.3.2 iOS 资源外部加载 40 

附录 A :语音资源列表 41 

附录 B :图片资源列表 42 

附录 C :文本资源列表 43 

附录 D : host 取值列表 45 

附录 E : UI 可配置项 46 

附录 F : SDK 兼容模式图片列表 48 

# 1 活体认证简介 

# 1.1 FaceID SDK 

本 SDK 为旷视提供的新版本活体认证 SDK 。在一个 SDK 中支持多种活 体方式,在保证安全性的基础上提供了完善的体验,同时具备对接方 便,体积小巧,易于集成,使用简单,服务于大中小各类互联网企 业。 

# ohpm 获取地址: 

"dependencies": { 

"@megvii/lv5_sdk": "5.8.13" } 

# 开发者:北京旷视科技有限公司 

包名: @megvii/lv5_sdk 

版本: 5.8.13 

MD5 : 9462d3cd7373979be720350e5f43aa75 

隐私政策: FaceID 个人信息与隐私保护政策 

合规使用说明:旷视 SDK&API 合规与安全指南 2026.pdf 

# 1.2 SDK 兼容性 

MegLive SDK 同时支持 Android 和 iOS 双平台,其中 Android 版本支持 5.0-14.0 , ARM 架构需要支持 NONE 指令集; iOS 版本支持 iOS9iOS16 。 

在 Android9 以上设备的调试过程中,第一次安装会系统弹框提示非 SDK 接口的使用显示(只在调试过程出现,仅弹一次),发布模式不 会出现此现象。 

1.3 活体认证逻辑 

活体认证逻辑大致分为五步: 

通过 FaceID 后台获取 api_key 和 api_secrect 进行 SDK 的鉴权获取 sign ,详细可参考鉴权文档; 

获取鉴权 sign 之后调用 Get_biz_token API ,获取 biz_token (业务串 号); 

使用 biz_token 完成 SDK 预处理,预处理通过之后进入认证页面; 

用户通过认证流程后,返回用户界面,并通过回调告知结果( error code 、 error message ); 

使用 biz_token 调用 Verify API 获取本次活体比对判断结果,详细可参 考 Verify 文档。 

2 SDK 集成 

# 2.1 Android 集成 

将 res 目录下的资源文件拷贝到项目 app 的 res 下,若果不需要多语种适 配可以将 res 下的中英文适配文件夹删除,如果需要适配其他语种则需 要建立对应语种目录(图片资源如果需要区分多语种也需要建立对应 目录), demo 中提供了默认(中文)、英文、中文三种示例(图 1 )。 

图 1 

把 arr 文件复制进入 libs 文件夹中(图 2 ) 

# 图 1 

在 APP 的 build.gradle 中加入 flatDir ,并在 dependencies 中加入 implementation(name:'faceidv5', ext:'aar') (图 3 ) 

图 3 

录屏功能说明: 

1. 录屏权限的申请有两种方式,一种是 App 层申请,通过 MegLiveDetectConfig.setMediaProjection() 方法设置进来;另一种是 App 不申请,由 SDK 层申请。建议使用第二种方式。另外,如果 App 申请录屏权限,则 App 要负责释放,否则会出现不可控的问题。 

2. 如果 targetSdkVersion 高于 28 (如图 4 ),则需要在 AndroidManifest.xml 中增加 

<service 

android:foregroundServiceType="mediaProjection" 

# /> (如图 5 ) 

图 4 

图 5 

# 2.2 iOS 集成 

# 2.2.1 添加 Framework 文件到项目 

在 Xcode 工具中点击 TARGETS->Build Phases-> Link Binary With Libaries 中点击 “+” 按钮,在弹出的窗口中点击 “Add Other” 按钮,选 择 MGFaceIDBaseKit.framework 和 MGFaceIDLiveDetect.framework 同 时添加到工程中。 

注:静态库中采用 Objective-C++ 实现,因此需要您保证您工程中至 少有一个 .mm 后缀的源文件 ( 您可以将任意一个 .m 后缀的文件改名 为 .mm) ,或者在工程属性中指定编译方式,即在 Xcode 的 Project -> Edit Active Target -> Build Setting 中找到 Compile Sources As ,并 将其设置为 "Objective-C++" 。 

# 2.2.2 添加资源文件到项目 

选中工程名,在右键菜单中选择 Add Files to “ 工程名 ”... ,选择 bundle 文件,并勾选 “Copy items if needed” 复选框,单击 “Add” 按 钮,将资源文件添加到工程中,需要勾选 “(Add to targets)” 到指定 的 “target” 。关于资源的其他加载方式,可以查看该文档 4.3.2 iOS 资 源外部加载的说明。 

# 2.2.3 引入所需的系统库 

需要在您的 Xcode 工程中引入 AVFoundation.framework 、 CoreMedia.framework 、 CoreMotion.framework 、 SystemConfiguration.framework 、 WebKit.framework 、 MediaPlayer.framework 、 ReplayKit.framework 、系统库。 

# 2.2.4 添加项目权限 

因活体认证 SDK 需要使用设备相机,请在 “info.plist” 中添加 “PrivacyCamera Usage Description” 权限。 

# 2.3 鸿蒙集成 

将 sdk(lv5_sdk.har) 放在应用模块 libs 目录下 

在应用模块下的 oh-package.json5 配置文件中添加 sdk 依赖 

"dependencies": { "@megvii/lv5_sdk": "file:./libs/lv5_sdk.har" } 

3 SDK 接口 

# 3.1 Android 接口 

3.1.1 入口类 MegLiveManager 

MegLiveManager 类是管理活体认证的类,此类不可以初始化,只能 通过 getInstance 获得其单例。 

# 3.1.1.1 获取 MegLiveManager 单例对象 

函数名 

getInstance 

MegLiveManager getInstance() 

名称 

获取 MegLiveManager 的实例 

类型说明 

函数 

# 说明 

获取 MegLiveManager 的单例 

返回值 

MegLiveManager 

一个实例 

3.1.1.2 开始检测 

函数名 

startDetect 

void startDetect(Context context, MegLiveDetectConfig config, MegLiveDetectListener callback) 

名称 

开始活体认证 

类型说明 

函数 说明 

开启活体检测接口。 

变量名 

说明 类型 

context 

Android 上下文 

Context 

config 

参数配置,详见 3.1.3MegLiveDetectConfig 说明 

MegLiveDetectConfig 

callback 

MegLiveDetectListener 接口的实现类,接受活体结果的接口,详见回 调函数 3.1.4 MegLiveDetectListener 说明 

MegLiveDetectListener 

3.1.1.3 设置透传模式数据同步接口回调 

函数名 

setDataSyncCallback 

void setDataSyncCallback(MegDataSyncCallback callback) 

名称 

透传数据同步回调 

类型说明 

函数 

说明 

在透传模式下通过本回调接口接收需要同步的数据 

变量名 

说明 

类型 

callback 

MegDataSyncCallback 接口的实现类,接收需要同步的类型及数据, 

# 详见回调函数 3.1.5 MegDataSyncCallback 

MegDataSyncCallback 

3.1.1.4 获取活体认证过程中的日志信息 

函数名 

getSDKLog 

String getSDKLog() 

名称 

获取活体认证过程中的日志信息 

类型说明 

函数 

说明 

无 

返回值 

String 

活体认证过程中的加密日志信息 

3.1.1.5 解密活体检测过程中的视频和图片文件 

函数名 

startDetectForLivenessFile 

LivenessFileResult getLivenessFiles(String filePath, String decryptionKey) 

名称 

获取解密活体文件 

# 类型说明 

函数 

说明 

返回值 LivenessFileResult 详见 3.1.5 变量名 说明 类型 filePath 端上活体成功后 sdk 返回的活体加密文件路径 String decryptionKey 调用 verify 后拿到的解密 key String 

3.1.1.6 获取 SDK 版本号信息 

函数名 

getVersion String getVersion() 

名称 获取 SDK 的版本号 

类型说明 

函数 

说明 

无 

返回值 

String 

当前 SDK 的版本号 

3.1.1.7 获取 SDK 构建版本信息 

函数名 

getBuildInfo String getBuildInfo() 

名称 获取 SDK 的构建信息 类型说明 函数 说明 无 返回值 

String 

一个字符串 

3.1.1.8 兼容模式设置回调方法 

函数名 

setImageDataListener 

void setImageDataListener(MegLiveImageDataListener listener) 

名称 设置回调方法 类型说明 函数 说明 无 变量名 说明 类型 

listener 

兼容模式的回调函数,详见 MegLiveImageDataListener 的类说明 MegLiveImageDataListener 

3.1.2 MegLiveDetectConfig 检测配置类 

变量 类型 描述 

bizToken 

String 

请求 token ,必传 

# modelPath 

String 

模型路径 

host 

String 

faceid 服务 host ,见附录 D 

默认为国内 

language 

String 

sdk 语言,参数按照 Language codes-ISO 639 标准传入 

isShowLogo 

boolean 

是否展示底部 logo 

autoAdjustVolume 

boolean 

是否自动调节动作活体语音提示音量,兼容模式选填,默认 false suggestVolume 

int 

调节音量建议值,兼容模式 autoAdjustVolume 为 true 时选填,默认值 50 

verticalDetection 

int 

# 垂直检测 1 一直; 2 前两秒; 3 不检测 

mediaProjection 

MediaProjection 

申请录屏权限后的对象 

isEnterLoadingPage 

boolean 

是否进入 Loading 页 

isLandscape 

boolean 

是否 pad 横屏(不支持手机横屏) 

mode 

int 

0 :普通模式 3 :兼容模式 5: 透传模式 

customTimeout 

int 

透传模式下的接口等待超时时间,默认 30s 

configData 

String 

活体配置信息,当 mode 等于 3 时, configData 为必选项 

hostList 

List<String> 

备用的 host 列表,当 mode 等于 3 时有效。当 host 请求失败时,尝试 

# hostList 中的地址 

isMute 

boolean 

是否静音 

3.1.3 MegLiveDetectListener 检测监听回调 

3.1.3.1 onPreDetectFinish 

函数名 

onPreDetectFinish 

void onPreDetectFinish(int errorCode, String errorMessage); 名称 预处理结果回调 类型说明 函数 说明 

返回值 

变量名 说明 类型 

errorCode 

错误码 见 3.1.4 

int 

errorMessage 

错误描述 

String 

3.1.3.2 onDetectFinish 

函数名 

onDetectFinish 

void onDetectFinish(int errorCode, String errorMessage,String bizToken) 

名称 

检测结果回调 

类型说明 

函数 说明 

返回值 

变量名 说明 类型 

errorCode 

错误码 见 3.1.4 

int 

errorMessage 

# 错误描述 

String 

bizToken 

业务号 

String 

3.1.3.3 onLivenessFileCallback 

函数名 

onLivenessFileCallback 

void onLivenessFileCallback(String livenessFilePath) 名称 活体数据留存结果回调 类型说明 函数 

说明 返回值 变量名 说明 类型 

livenessFilePath 活体留存文件路径 

String 

# 3.1.3.4 onLivenessLocalFileCallBack 

函数名 

onLivenessLocalFileCallBack 

void onLivenessLocalFileCallBack(MegliveLocalFileInfo fileInfo) 

名称 

活体数据留存结果回调 , 包含活体留存和录屏留存 

类型说明 

函数 

说明 

返回值 

变量名 

说明 类型 

fileInfo 

本地留存文件类 , 详见 MegliveLocalFileInfo 类 

MegliveLocalFileInfo 

3.1.3.5 MegliveLocalFileInfo 

名称 

本地留存文件类 

类型说明 

类 

说明 

返回值 

变量名 

说明 类型 

filePath 

活体数据留存文件路径 

String 

scrrenFilePath 

录屏数据留存文件路径 

String 

3.1.4 MegLiveImageDataListener 兼容模式检测结果回调 

3.1.4.1 onImageData 

函数名 

onImageData 

void onImageData(HashMap<String,byte[]> imageData, byte[] delta) 

名称 

兼容模式检测结果回调 

类型说明 

函数 

说明 

# imageData 中 key 值见 附录 F 

返回值 

变量名 

说明 类型 bestImage best 图 HashMap 

delta 

活体检测结果数据 

byte[] 

3.1.5 MegDataSyncCallback 透传模式同步接口回调 

3.1.5.1 performDataSync 函数名 

performDataSync 

void performDataSync(String bizToken,int syncType, String syncData, MegDataSyncResponse response); 

名称 

数据同步回调 

类型说明 

函数 

说明 

返回值 

变量名 说明 类型 

bizToken 当前请求 bizToken String syncType 数据同步类型 

int 

syncData 需要同步的数据 

String 

response 

通知 sdk 接口请求后的结果回调,见 3.1.6 MegDataSyncResponse MegDataSyncResponse 3.1.5.2 onGetMegliveData 

函数名 

onGetMegliveData 

void onGetMegliveData(byte[] megliveData); 

名称 

# megliveData 数据回调 

# 类型说明 

函数 

说明 

透传模式下 sdk 返回 megliveData 数据 

返回值 

变量名 

说明 

类型 

megliveData 活体检测数据 

byte[] 

3.1.6 MegDataSyncResponse 透传模式通知 SDK 同步结果接口 

3.1.6.1 onResponse 

函数名 

onResponse void onResponse(int syncType, String response); 

名称 

透传模式回传 sdk 同步结果接口 

类型说明 

函数 

# 说明 

请求服务端同步接口后调用 返回值 

变量名 说明 类型 syncType 数据同步类型 int 

response 数据同步结果 String 

3.1.7 错误码 ErrorCode ErrorMessage 说明 1000 LIVENESS_FINISH 活体完成 

GET_CONFIG_SUCCESS 

# 获取配置成功 

1001 

BIZ_TOKEN_DENIED 传入的 biz_token 不符合要求 1002 

ILLEGAL_PARAMETER:{livenesstype} ILLEGAL_PARAMETER:{Context} ILLEGAL_PARAMETER:{MegLiveDetectConfig} ILLEGAL_PARAMETER:{MegLiveDetectConfig:model} ILLEGAL_PARAMETER:{MegLiveDetectConfig:appKey} ILLEGAL_PARAMETER:{MegLiveDetectConfig:livenessId} ILLEGAL_PARAMETER:{MegLiveDetectConfig:bizToken} ILLEGAL_PARAMETER:{MegLiveDetectConfig:host} ILLEGAL_PARAMETER:{MegLiveDetectConfig:modelPath} ILLEGAL_PARAMETER:{missing_liveness_config} ILLEGAL_PARAMETER:{response_result_is_null} ILLEGAL_PARAMETER:{request_data_is_null} ILLEGAL_PARAMETER:{request_data_error} ILLEGAL_PARAMETER:{jsonexception_200} ILLEGAL_PARAMETER:{jsonexception_400} 传入参数不合法, {} 内为具体原因 1003 

AUTHENTICATION_FAIL:{illegal_param} 

AUTHENTICATION_FAIL:{illegal_handle} AUTHENTICATION_FAIL:{illegal_index} AUTHENTICATION_FAIL:{expire} 

AUTHENTICATION_FAIL:{bundleid_error} AUTHENTICATION_FAIL:{license_error} AUTHENTICATION_FAIL:{liveness_id_error} AUTHENTICATION_FAIL:{model_error} AUTHENTICATION_FAIL:{algo_error} 

AUTHENTICATION_FAIL:{opengl_context_error} 

鉴权失败, {} 内为具体原因 

1004 

MOBILE_PHONE_NOT_SUPPORT 

手机在不支持列表里 

1005 

具体的异常信息,格式:异常类型 _ 代码类名 _ 代码行数 示例: 

NullPointException_com.megvii.xx.Test_1101 

若出现此类错误,建议及时联系 FaceID 技术支持 

1006 

REQUEST_FREQUENTLY 

同一台设备同时存在多次调用时,第一次调用正常运行,其他次调用 返回此类错误 

1007 

NETWORK_TIME_OUT 

网络请求超时 

1008 

INTERNAL_ERROR 

网络配置错误,当此类错误发生时请再次请求,如果持续出现此类错 误,请及时联系 FaceID 客服或商务 

1009 

INVALID_BUNDLE_ID 

信息验证失败,请重启 

程序或设备后重试 

1010 

NETWORK_ERROR 

连不上互联网,请连接上互联网后重试 

1011 

USER_CANCEL 

用户取消 

1012 

NO_CAMERA_PERMISSION 

没有打开相机的权限,请开启权限后重试 

1013 

DEVICE_NOT_SUPPORT 

无法启动相机,请确认摄像头功能完好 

1014 

FACE_INIT_FAIL 

无法启动人脸识别,请稍后重试 

1016 

LIVENESS_FAILURE 活体失败 

1017 

GO_TO_BACKGROUND 

应用退到后台,活体检测失败 1018 

LIVENESS_TIME_OUT 操作超时,由于用户在长时间没有进行操作 1019 

DATA_UPLOAD_FAIL 数据上传失败 

1022 

MOBILE_PHONE_NOT_SUPPORT_SCRN 

机型不支持录屏 

1023 

# SCRN_AUTHORIZATION_FAIL 

录屏授权失败 

1024 

SCRN_RECORD_FAIL 

# 视频录制失败 

1025 

VIDEO_SAVE_FAIL 

视频保存失败 

1026 

NO_AUDIO_RECORD_PERMISSION 

没有语音录制权限 

3.2 iOS 接口 

# 3.2.1 类 MegLiveV5DetectManager 

MegLiveV5DetectManager 类是管理活体认证的核心类,活体认证相 关功能都需要使用该类进行。 

3.2.1.1 开启 FaceID 活体认证 

# 函数名 

+megFaceIDLiveDetectManagerWithBizToken: configInfo: extraData: startCallBack: detectVC: endCallBack: dismissCallBack: 

*/ 

+ (void)megFaceIDLiveDetectManagerWithBizToken:(NSString 

*__nonnull)bizTokenStr 

configInfo:(MegLiveV5DetectInitConfigItem *__nullable)configItem 

extraData:(NSDictionary *__nullable)extraDict 

startCallBack:(MegLiveV5StartDetectBlock)startBlock 

detectVC:(UIViewController *)detectVC 

endCallBack:(MegLiveV5EndDetectBlock)endBlock 

dismissCallBack:(MegLiveV5DismissBlock)dismissBlock; 

名称 

开启 FaceID 活体认证 

# 说明 

设置不同的启动类型,通过 block 返回校验结果。不同阶段返回不同 的 block 。如果该阶段 block 中的内容已经提示失败,则不会进行下一 阶段的 block 返回 

变量名 

说明 

类型 

bizTokenStr 

设置 FaceID 活体检测的启动配置 

NSString *__nonnull 

configItem 

设置 FaceID 活体检测的自定义配置 

MegLiveV5DetectInitConfigItem *__nullable 

extraDict 

预留参数,当前为 nil 。 

如果需要开启启动缓冲页面,请设置预览配置 @{@"ShowV5Loading" : @YES} 

NSDictionary *__nullable 

startBlock 

活体检测初始化完成 block 

MegLiveV5StartDetectBlock 

detectVC 

开启活体检测的 VC 页面,一般为当前 ViewController 

UIViewController * 

endBlock 

活体检测完成时 block 

MegLiveV5EndDetectBlock 

dismissBlock 

活体检测结束,页面收起时 block 

MegLiveV5DismissBlock 

3.2.1.2 开启 FaceID 活体认证 

函数名 

+megFaceIDLiveDetectManagerWithBizToken: configInfo: extraData: networkCallBack: startCallBack: detectVC: endCallBack: dismissCallBack: 

*/ 

+ (void)megFaceIDLiveDetectManagerWithBizToken:(NSString 

*__nonnull)bizTokenStr 

configInfo:(MegLiveV5DetectInitConfigItem *__nullable)configItem 

extraData:(NSDictionary *__nullable)extraDict 

networkCallBack:(MegLiveV5NetworkRequestBlock)networkBlock 

startCallBack:(MegLiveV5StartDetectBlock)startBlock 

detectVC:(UIViewController *)detectVC 

endCallBack:(MegLiveV5EndDetectBlock)endBlock 

dismissCallBack:(MegLiveV5DismissBlock)dismissBlock; 

名称 

开启 FaceID 活体认证 

# 说明 

设置不同的启动类型,通过 block 返回校验结果。不同阶段返回不同 的 block 。如果该阶段 block 中的内容已经提示失败,则不会进行下一 阶段的 block 返回 

变量名 

说明 

类型 

bizTokenStr 

设置 FaceID 活体检测的启动配置 

NSString *__nonnull 

configItem 

设置 FaceID 活体检测的自定义配置 

MegLiveV5DetectInitConfigItem *__nullable 

extraDict 

# 预留参数,当前为 nil 。 

如果需要开启启动缓冲页面,请设置预览配置 @{@"ShowV5Loading" : @YES} 

NSDictionary *__nullable 

networkBlock 

网络请求 block 。当 configItem.model 为 MegLiveV5DetectModel_C 时,该参数必须。该 block 会进行多次返回,请根据 networkType 分别 进行操作 

MegLiveV5NetworkRequestBlock 

startBlock 

活体检测初始化完成 block 

MegLiveV5StartDetectBlock 

detectVC 

开启活体检测的 VC 页面,一般为当前 ViewController 

UIViewController * 

endBlock 

活体检测完成时 block 

MegLiveV5EndDetectBlock 

dismissBlock 

活体检测结束,页面收起时 block 

MegLiveV5DismissBlock 

3.2.1.3 获取活体认证过程中的日志信息 

# 函数名 

+queryMGFaceIDLiveDetectLogInfo: 

+ (NSData *)queryMGFaceIDLiveDetectLogInfo; 

名称 

# 获取活体检测过程中的日志信息 

# 说明 

该日志信息为加密数据,请通过 FaceID 服务进行解密处理 

变量名 

说明 

类型 

无参数 

返回值类型 

说明 

NSData * 

加密后的日志数据 

3.2.1.4 解密活体检测过程中的视频和图片文件 

# 函数名 

+encodeMGFaceIDLiveDetectFileWithFilePath: encodeKey: 

+ (NSDictionary *)encodeMGFaceIDLiveDetectFileWithFilePath: (NSString *)filePath encodeKey:(NSString *)encodeStr; 

# 名称 

解密活体检测过程中的视频和图片文件 

# 说明 

针对加密数据进行解密处理,需要用户提供 key 进行解密 变量名 

说明 类型 

filePath 

存储加密文件的路径 

NSString * encodeStr 用于解密的 key 

NSString * 返回值类型 说明 

NSDictionary* 

解密后的文件信息。该信息为解密后暂存到沙盒中的路径组合 3.2.1.5 获取 SDK 版本号信息 函数名 

+getSDKVersion: 

+ (NSString *_Nonnull)getSDKVersion; 

名称 

获取 SDK 版本号信息 

说明 

无 

变量名 说明 类型 无参数 返回值类型 说明 NSString * SDK 版本号 3.2.1.6 获取 SDK 构建版本信息 函数名 +getSDKBuild: + (NSString *_Nonnull)getSDKBuild; 名称 获取 SDK 构建版本信息 

说明 无 变量名 说明 类型 无参数 

返回值类型 

# 说明 

NSString * 

# SDK 构建版本信息 

3.2.1.7 MegLiveV5StartDetectBlock 

# 函数名 

MegLiveV5StartDetectBlock 

typedef void(^MegLiveV5StartDetectBlock)(MegLiveV5DetectError* error, NSDictionary* extraOutDict); 

# 名称 

FaceID 活体检测配置接口管理器加载状态 Block 

说明 

无 

变量名 

说明 

类型 

error 

错误信息对象 

MegLiveV5DetectError * 

extraOutDict 

检测返回数据 

NSDictionary * 

返回值类型 

# 说明 

无 

# 3.2.1.8 MegLiveV5EndDetectBlock 

# 函数名 

MegLiveV5EndDetectBlock 

typedef void(^MegLiveV5EndDetectBlock)(MegLiveV5DetectError* error, NSString* bizTokenStr, NSDictionary* extraOutDict); 

名称 

FaceID 活体检测配置接口检测完成时 Block 

说明 

无 变量名 

说明 

类型 

error 

错误信息对象 

MegLiveV5DetectError * 

bizTokenStr 

bizToken 

NSString * 

extraOutDict 

# 检测完成返回的结果。 

返回结果对应 key 参考 附录 F : SDK 兼容模式图片列表 

NSDictionary * 

返回值类型 

说明 

无 

3.2.1.9 MegLiveV5DismissBlock 

函数名 

MegLiveV5DismissBlock 

typedef void(^MegLiveV5DismissBlock)(void); 

名称 

FaceID 活体检测配置接口页面收起完成时 Block 说明 

无 

变量名 说明 类型 

无参数 返回值类型 

说明 

无 

# 3.2.1.10 MegLiveV5NetworkRequestBlock 

# 函数名 

MegLiveV5NetworkRequestBlock 

typedef void(^MegLiveV5NetworkRequestBlock)(int networkType, NSString* bizTokenStr, NSString* dataStr, MegLiveV5NetworkResponseBlock configResponse); 

# 名称 

FaceID 活体检测配置接口管理器网络请求状态 Block 

# 说明 

该参数仅在集成方案 E 时有效。该 block 内部为子线程。如果需要进行 UI 操作,请手动回到主线程。 

当 networkType 为 1 时, bizTokenStr 和 dataStr , configResponse 有 效。请使用 datasync 接口,并配置 data_type 为 1 。 

当 networkType 为 2 时, bizTokenStr 和 dataStr 有效。请使用 datasync 接口,并配置 data_type 为 2 。 

# 变量名 

说明 

类型 

networkType 

参数类型 

int 

bizTokenStr 

业务串号 

NSString* 

dataStr 

请求体数据 

NSString* 

configResponse 

回到到 SDK 内部 Block 

MegLiveV5NetworkResponseBlock 

返回值类型 

说明 

无 

3.2.1.11 MegLiveV5NetworkResponseBlock 

函数名 

MegLiveV5NetworkResponseBlock 

typedef void(^MegLiveV5NetworkResponseBlock)(NSDictionary* responseDict) 

名称 

FaceID 活体检测配置接口管理器网络响应状态 Block 

说明 

该参数仅在集成方案 E 时有效。请在默认线程或者非主线程中调用该 block 。回到主线程中调用该 block ,会导致网络卡顿,直到超时。 变量名 

说明 

类型 

responseDict 

网络请求的响应体内容 

NSDictionary* 

返回值类型 

说明 

无 

3.2.2 可配置类 

该类文件中包括了用户可以自定义的配置。该 SDK 为 V5 版本活体,同 时兼容 V3 版本。 V5 版本下,部分自定义的配置会被 FaceID 控制台更 改。 

3.2.2.1 MegLiveV5DetectInitConfigItem 

变量名 

说明 

类型 

languageType 

必选。指定活体 V5 语言类型,关于 SDK 语言资源加载的方式,详情见 文档中资源说明 

MegLiveV5DetectLanguageType 

hostURL 

必选。指定活体 V5 拉取配置的 HOST 地址。默认为 “https:// api.megvii.com” 即国内;具体见附录 D 

NSString* 

# model 

指定 FaceIDV5SDK 集成方式。默认为 `MegLiveV5DetectModel_A` 。 必需 

MegLiveV5DetectModel 

configInfo 

指定活体配置。当 model 为 `MegLiveV5DetectModel_C` 时,该参数必 需。其他 

model 类型该参数无效。如果 model 设置 

`MegLiveV5DetectModel_C` ,但是该参数为 nil ,会导致 SDK 初始化失 败。 

该配置参数为加密后的信息。需要通过 get_biz_token 接口获取。 

NSString* 

standbyURLList 

授权请求的备用 URL 列表。当使用 `hostURL` 参数请求失败后,使用该 List 中的 URL 进行重试。当 model 为 `MegLiveV5DetectModel_C` 时, 该参数非必需。其他 model 类型该参数无效。 

NSArray<NSString *>* 

customUI 

指定活体 V5 的 UI 样式。非必需 

MegLiveV5DetectUIConfigItem* 

bundleFilePath 

指定 SDK 资源绝对路径,以 ‘bundle’ 为结尾。如果该值为 nil 或者 “” , 则从 MainBundle 中读取资源。关于资源加载的方式,详情见文档中资 源说明。非必需 

NSString* 

phoneVertical 

指定活体检测过程中设备垂直检测类型。默认为 `MegLiveV5DetectPhoneVerticalTypeDisable` 。非必需 

MegLiveV5DetectPhoneVerticalType 

isAdjustPhoneVolume 

非必选。是否进行音量调节。其中 YES 为开启, NO 为不开启。开启 后,会将当前设备音量调节到 ‘maxPhoneVolume’ ,默认为 NO 

BOOL 

# adjustPhoneVolume 

音量调节后最大音量。阈值范围为 [0, 100] ,默认为 0 。该参数仅在 `isAdjustPhoneVolume` 值为 YES 时生效。非必需 

Int 

# isMute 

设置为静音模式。 YES 为设置静音模式, NO 为不设置。默认值为 NO 。非必需 

BOOL 

showPoweryby 

指定是否显示活体检测页面底部 powerby 图片。默认值为 NO ,不显 示。非必需 

BOOL 

3.2.2.2 MegLiveV5DetectUIConfigItem 

变量名 

说明 

# 类型 

livenessHomeNormalRemindTextColor 

提示文字颜色正常状态,默认颜色为 0x292929 

UIColor * 

livenessHomeProcessBarColor 

活体阶段进度条颜色,仅动作活体模式、炫彩活体不打光模式 

- - 距离活体 远近距离阶段和距离活体 炫彩不打光阶段生效,默认颜色 为 0x267CE0 。炫彩活体打光模 

式不生效 

UIColor * 

livenessHomeBackgroundColor1 

主题上部圆圈颜色,默认颜色为 0x79DDF0 

UIColor * 

livenessHomeBackgroundColor2 

主题下部圆圈颜色,默认颜色为 0x0678FC 

UIColor * 

livenessHomeActionHatColor 

动作活体过程中顶部阴影颜色,默认颜色为 0x0678FC 

UIColor * 

livenessHomeDeviceVerticalRemindColor 

手机竖向垂直提示字体颜色,默认颜色为 0xFFFFFF 

UIColor * 

livenessHomeCheckingLineStartColor 

验证阶段进度条颜色,渐变色。默认结束颜色为 0xF2F4F5 

UIColor * 

livenessHomeCheckingLineEndColor 

验证阶段进度条颜色,渐变色。默认结束颜色为 0xF2F4F5 

UIColor * 

livenessHomeExitPopupwindowTextSize 

退出弹窗标题字号 

CGFloat 

livenessHomeExitPopupwindowBodySize 

退出弹窗正文字号 

CGFloat 

livenessHomeConfirmButtonColor 

# 确认按钮颜色 

UIColor * 

livenessHomeCancelButtonColor 

# 取消按钮颜色 

UIColor * 

livenessHomeAgreementpageTitleTextSize 

协议页面顶部标题字体大小 

CGFloat 

livenessHomeAgreementpageBottomTitleTextSize 

# 协议页面底部提示字体大小 

CGFloat 

livenessHomeAgreementpageBottomButtonBeforeClickColor 协议页面按钮正常态 

UIColor * 

livenessHomeAgreementpageBottomButtonAfterClickColor 协议页面按钮高亮态度 

UIColor * 

3.2.3 类 MegLiveV5DetectError 

变量名 

说明 

类型 

errorCode 

活体认证返回值 code 

MegLiveV5DetectErrorType 

errorMessage 

活体认证返回值 message 

NSString * 

3.2.4 枚举 

3.2.4.1 MegLiveV5DetectLanguageType 

活体检测语言类型 

枚举名 

说明 

枚举值 

MegLiveV5DetectLanguageTypeCh 

中文模式 

# 0- 默认值 

3.2.4.2 MegLiveV5DetectModel 

活体检测集成方式 

枚举名 

说明 

枚举值 

MegLiveV5DetectModel_A 

默认集成方式,在 SDK 内部通过网络请求进行授权和活体配置的获 取,需要配合指定的 `hostURL` 参数使用。 

1- 默认值 

MegLiveV5DetectModel_C 

兼容性集成方式,在 SDK 内部通过网络请求仅进行授权,活体配置需 要用户主动传入,需要配合指定的 `hostURL` 和 `configInfo` 参数使 用。 

3 

3.2.4.3 MegLiveV5DetectPhoneVerticalType 

活体检测设备垂直检测类型 

枚举名 

说明 

# 枚举值 

MegLiveV5DetectPhoneVerticalTypeContinue 持续启用设备垂直检测功能 

1 

MegLiveV5DetectPhoneVerticalTypeFront2 

仅在检测开启的 2 秒内启用,之后关闭该功能 2 

MegLiveV5DetectPhoneVerticalTypeDisable 禁用设备垂直检测功能 

3 

3.2.4.4 MegLiveV5DetectSignType 

活体检测错误类型 

枚举名 

说明 

枚举值 

MegLiveV5DetectErrorTypeOK 

SDK 活体成功 

1000 

MegLiveV5DetectErrorTypeBizTokenDenied 

传入的 biz_token 不符合要求 

1001 

MegLiveV5DetectErrorTypeIllegalParameter 

# 传入的参数不合法 

1002 

MegLiveV5DetectErrorTypeAuthenticationFail 

SDK 鉴权失败 

1003 

MegLiveV5DetectErrorTypeMobileNotSupport 

手机不在支持列表里 

1004 

MegLiveV5DetectErrorTypeNullPointException 

若出现此类错误,请联系 FaceID 技术支持 

1005 

MegLiveV5DetectErrorTypeRequestFrequently 

同一台设备同时存在多次调用 

1006 

MegLiveV5DetectErrorTypeNetworkTimeout 

网络请求超时 

1007 

MegLiveV5DetectErrorTypeInternalError 

网络配置错误。当出现此类错误,请重试。如果此类错误持续出现, 请联系 FaceID 技术支持 

1008 

MegLiveV5DetectErrorTypeInvalidBundleID 

# 信息验证失败,请重试 

1009 

MegLiveV5DetectErrorTypeNetworkError 

网络连接失败,请查看网络状态 

1010 

MegLiveV5DetectErrorTypeUserCancel 

用户取消 

1011 

MegLiveV5DetectErrorTypeNoCameraPermission 

没有使用相机的权限,请开启相机权限后重试 

1012 

MegLiveV5DetectErrorTypeNoCameraSupport 

无法启动相机,请确定相机功能完好 

1013 

MegLiveV5DetectErrorTypeFaceInitFail 

无法启动人脸识别,请重试 

1014 

MegLiveV5DetectErrorTypeLivenessFailure 

SDK 活体检测失败 

1016 

MegLiveV5DetectErrorTypeGotoBackground 

应用推到后台,活体检测失败 

1017 

MegLiveV5DetectErrorTypeLivenessTimeout 

应用操作超时,活体检测失败 

1018 

MegLiveV5DetectErrorTypeDataUploadFail 

活体验证上传异常,活体检测失败 

1019 

MegLiveV5DetectErrorTypeNFCUserQuit 

用户退出 NFC 检测流程 

1020 

MegLiveV5DetectErrorTypeNFCSystemQuit 

NFC 检测流程系统异常退出 

1021 

MegLiveV5DetectErrorTypeScreenNoSupport 

设备不支持录屏功能 

1022 

MegLiveV5DetectErrorTypeScreenNoPermission 用户拒绝录屏功能的授权 

1023 

MegLiveV5DetectErrorTypeScreenRecordFail 录屏功能录制失败 

1024 

# MegLiveV5DetectErrorTypeScreenWriteFail 

# 录屏功能完成后的视频文件保存失败 

1025 

# 3.3 鸿蒙接口 

# 3.3.1 入口类 MegLiveManager 

MegLiveManager 类是管理活体认证的类,此类不可以初始化,只能 通过 getInstance 获得其单例。 

3.3.1.1 获取 MegLiveManager 单例对象 

函数名 

getInstance 

getInstance(): MegLiveManager 

名称 

获取 MegLiveManager 的实例 

类型说明 

函数 

说明 

获取 MegLiveManager 的单例 

返回值 

MegLiveManager 

一个实例 

3.3.1.2 开始检测 

# 函数名 

# startDetect 

public startDetect(context: Context, config: MegLiveDetectConfig, callback: MegLiveDetectListener) 

名称 

开始活体认证 

类型说明 

函数 

说明 

开启活体检测接口。 变量名 

说明 类型 

context 

鸿蒙上下文 

Context 

config 

参数配置,详见 3.3.2MegLiveDetectConfig 说明 

MegLiveDetectConfig 

callback 

MegLiveDetectListener 接口的实现类,接受活体结果的接口,详见回 调函数 3.3.3 MegLiveDetectListener 说明 

MegLiveDetectListener 

# 3.3.1.3 获取活体认证过程中的日志信息 

函数名 

getSDKLog 

public getSDKLog(): string 

名称 

获取活体认证过程中的日志信息 

类型说明 

函数 

说明 

无 

返回值 

string 

活体认证过程中的加密日志信息 

3.3.1.4 解密活体检测过程中的视频和图片文件 

函数名 

getLivenessFiles 

public getLivenessFiles(filePath: string, decryptionKey: string): LivenessFileResult 

名称 

获取解密活体文件 

类型说明 

函数 

说明 

# 返回值 

LivenessFileResult 详见 3.3.4 

变量名 说明 类型 

filePath 端上活体成功后 sdk 返回的活体加密文件路径 string decryptionKey 调用 verify 后拿到的解密 key 

string 3.3.1.5 获取 SDK 版本号信息 

函数名 

getVersion public getVersion(): string 

名称 

获取 SDK 的版本号 

类型说明 

函数 说明 

无 

返回值 

String 

当前 SDK 的版本号 

3.3.1.6 获取 SDK 构建版本信息 

函数名 

getBuildInfo 

public getBuildInfo(): string 

名称 获取 SDK 的构建信息 类型说明 函数 说明 无 

返回值 

string 一个字符串 

3.3.1.7 设置透传模式请求回调 

函数名 

setRequestCallback 

public setRequestCallback(requestCallback: 

MegLiveDetectRequestCallback) 

名称 设置请求回调 类型说明 函数 说明 无 返回值 无 变量名 说明 类型 

requestCallback 

请求回调参数。详见 MegLiveDetectRequestCallback 说明 MegLiveDetectRequestCallback 

3.3.2 检测配置类 3.3.2.1 MegLiveDetectConfig 

变量 类型 描述 

bizToken 

string 

# 请求 token ,必传 

modelPath 

string 

模型路径 

host 

string 

faceid 服务 host ,见附录 

默认为国内 

language (预留字段) 

string 

【鸿蒙暂不支持】 sdk 语言,参数按照 Language codes-ISO 639 标准传 入 isShowLogo (预留字段) 

boolean 

【鸿蒙暂不支持】是否展示底部 logo 

autoAdjustVolume (预留字段) 

boolean 

【鸿蒙暂不支持】是否自动调节动作活体语音提示音量,兼容模式选 填,默认 false 

suggestVolume (预留字段) 

number 

【鸿蒙暂不支持】调节音量建议值,兼容模式 autoAdjustVolume 为 true 时选填,默认值 50 

# verticalDetection (预留字段) 

number 

【鸿蒙暂不支持】垂直检测 1 一直; 2 前两秒; 3 不检测; 

mode 

MegLiveDetedtModel 

检测模式,详见 MegLiveDetedtModel 说明。默认: MODEL_A 

requestMaxTime 

number 

透传模式下使用,最大网络请求结果回传等待时间。单位 s, 默认: 30s 

secureCamera 

boolean 

是否开启安全相机。默认: false 不开启 

3.3.2.2 MegLiveDetectModel 

对应值 

说明 

MODEL_A 

0 

默认集成方式,在 SDK 内部通过网络请求进行授权和活体配置的获 取,需要配合指定的 `hostURL` 参数使用。 

MODEL_B 

3 

兼容模式,在 SDK 内部通过网络请求仅进行授权,活体配置需要用户 主动传入,需要配合指定的 `hostURL` 和 `configInfo` 参数使用。 

# MODEL_C 

4 

v2 模式 

MODEL_D 

5 

透传模式 

# 3.3.3 检测监听回调 

3.3.3.1 MegLiveDetectListener 检测监听回调 

3.3.3.1.1 onPreDetectFinish 

函数名 

onPreDetectFinish 

onPreDetectFinish(errorCode: number, errorMessage: string): void; 

名称 

预处理结果回调 

类型说明 

函数 说明 

返回值 

变量名 

说明 

类型 

errorCode 

错误码 见 3.3.4 

number 

errorMessage 

错误描述 

string 

3.3.3.1.2 onDetectFinish 

函数名 

onDetectFinish 

onDetectFinish(errorCode: number, errorMessage: string, bizToken: string): void; 

名称 

检测结果回调 

类型说明 

函数 说明 

返回值 

变量名 说明 

# 类型 

errorCode 错误码 见 3.3.4 number errorMessage 错误描述 string bizToken 业务号 string 3.3.3.1.3 onLivenessFileCallback 函数名 onLivenessFileCallback onLivenessFileCallback(livenessFilePath: string): void; 名称 活体数据留存结果回调 类型说明 函数 说明 返回值 变量名 

说明 

类型 

livenessFilePath 

活体留存文件路径 

string 

3.3.3.1.4 onLivenessLocalFileCallBack 

函数名 

onLivenessLocalFileCallBack 

onLivenessLocalFileCallBack(fileInfo: MegliveLocalFileInfo| undefined): void; 

名称 

活体数据留存结果回调 , 包含活体留存 

类型说明 

函数 

说明 

返回值 

变量名 说明 类型 

fileInfo 

本地留存文件类 , 详见 MegliveLocalFileInfo 类 

MegliveLocalFileInfo|undefined 

3.3.3.1.5 MegliveLocalFileInfo 

名称 

本地留存文件类 类型说明 

类 说明 

返回值 变量名 说明 类型 filePath 活体数据留存文件路径 

string scrrenFilePath 

录屏数据留存文件路径 

string 

3.3.3.2 MegLiveDetectRequestCallback 请求监听回调 

3.3.3.2.1 onNetworkRequest 

函数名 

onNetworkRequest 

onNetworkRequest:(networkType: number, bizToken: string, data: string, finishCallback: MegliveRequestFinishCallback)=> void; 

名称 透传模式网络请求回调 

类型说明 

函数 说明 透传模式下使用 返回值 无 变量名 说明 类型 

networkType 网络请求类型 

1: 获取配置信息 2: 上传日志信息 

number 

bizToken 

bizToken 

string 

data 

请求参数,从 sdk 内部返回,作为 /syncdata 接口 data 参数传入 

string 

finishCallback 

网络请求完成,回传返回结果到 sdk 。详见 MegliveRequestFinishCallback 说明 

MegliveRequestFinishCallback 

3.3.3.3 MegliveRequestFinishCallback 网络请求结果回传 

3.3.3.3.1 onFinish 

函数名 

onFinish 

onFinish:(response: string)=> void; 

名称 

网络请求结果回传 

类型说明 

函数 

说明 

透传模式下使用,网络请求结果回传到 sdk 内部 返回值 

无 

变量名 

说明 类型 

response 

/syncdata 请求结果 

string 

3.3.4 错误码 

ErrorCode 

ErrorMessage 说明 1000 LIVENESS_FINISH 活体完成 

GET_CONFIG_SUCCESS 获取配置成功 

1001 

BIZ_TOKEN_DENIED 传入的 biz_token 不符合要求 

1002 

ILLEGAL_PARAMETER:{livenesstype} 

ILLEGAL_PARAMETER:{Context} ILLEGAL_PARAMETER:{MegLiveDetectConfig} 

ILLEGAL_PARAMETER:{MegLiveDetectConfig:model} ILLEGAL_PARAMETER:{MegLiveDetectConfig:appKey} 

ILLEGAL_PARAMETER:{MegLiveDetectConfig:livenessId} ILLEGAL_PARAMETER:{MegLiveDetectConfig:bizToken} ILLEGAL_PARAMETER:{MegLiveDetectConfig:host} ILLEGAL_PARAMETER:{MegLiveDetectConfig:modelPath} ILLEGAL_PARAMETER:{missing_liveness_config} ILLEGAL_PARAMETER:{response_result_is_null} ILLEGAL_PARAMETER:{request_data_is_null} ILLEGAL_PARAMETER:{request_data_error} 

ILLEGAL_PARAMETER:{jsonexception_200} ILLEGAL_PARAMETER:{jsonexception_400} 

传入参数不合法, {} 内为具体原因 

1003 

AUTHENTICATION_FAIL:{illegal_param} AUTHENTICATION_FAIL:{illegal_handle} AUTHENTICATION_FAIL:{illegal_index} AUTHENTICATION_FAIL:{expire} AUTHENTICATION_FAIL:{bundleid_error} AUTHENTICATION_FAIL:{license_error} AUTHENTICATION_FAIL:{liveness_id_error} AUTHENTICATION_FAIL:{model_error} AUTHENTICATION_FAIL:{algo_error} 

AUTHENTICATION_FAIL:{opengl_context_error} 

鉴权失败, {} 内为具体原因 

1004 

MOBILE_PHONE_NOT_SUPPORT 

手机在不支持列表里 

1005 

具体的异常信息,格式:异常类型 _ 代码类名 _ 代码行数 

示例: 

NullPointException_com.megvii.xx.Test_1101 

若出现此类错误,建议及时联系 FaceID 技术支持 

1006 

REQUEST_FREQUENTLY 

同一台设备同时存在多次调用时,第一次调用正常运行,其他次调用 返回此类错误 

1007 

NETWORK_TIME_OUT 

网络请求超时 

1008 

INTERNAL_ERROR 

网络配置错误,当此类错误发生时请再次请求,如果持续出现此类错 误,请及时联系 FaceID 客服或商务 

1009 

# INVALID_BUNDLE_ID 

信息验证失败,请重启程序或设备后重试 

1010 

NETWORK_ERROR 

连不上互联网,请连接上互联网后重试 

1011 

USER_CANCEL 

用户取消 

1012 

NO_CAMERA_PERMISSION 

没有打开相机的权限,请开启权限后重试 

1013 

DEVICE_NOT_SUPPORT 

无法启动相机,请确认摄像头功能完好 

1014 

FACE_INIT_FAIL 

无法启动人脸识别,请稍后重试 

1016 

LIVENESS_FAILURE 

活体失败 

1017 

GO_TO_BACKGROUND 

# 应用退到后台,活体检测失败 

1018 

LIVENESS_TIME_OUT 

操作超时,由于用户在长时间没有进行操作 1019 DATA_UPLOAD_FAIL 数据上传失败 

1022 MOBILE_PHONE_NOT_SUPPORT_SCRN 机型不支持录屏 1023 SCRN_AUTHORIZATION_FAIL 录屏授权失败 1024 SCRN_RECORD_FAIL 视频录制失败 

1025 VIDEO_SAVE_FAIL 视频保存失败 

1026 NO_AUDIO_RECORD_PERMISSION 

没有语音录制权限 

# 4 SDK 使用说明 

4.1 UI 自定义 

4.1.1 Android UI 自定义 

UI 可自定义内容包括: 

1 )修改尺寸、颜色、文案内容 

在 values 文件夹下修改文字内容、尺寸、颜色等参数。 

# 2 )替换图片资源 

替换 drawable 文件夹下存放图片资源,资源 key 值需要按照规定格式 定义。 

# 3 )替换语音资源 

替换 raw 文件夹下的音频文件。 

详细配置项见附录 A 【语音资源列表】、附录 B 【图片资源列表】、附 录 C 【文本资源列表】、附录 E 【 UI 可配置项】。 

# 4.1.2 iOS UI 自定义 

在使用 SDK 进行活体认证时,设置 ` MegLiveV5DetectInitConfigItem` 类的 `customUI` 为自定义的 ` MegLiveV5DetectUIConfigItem` 对象。 该对象的属性有默认参数,请针对自己需要调节的参数,自行进行调 整。 

# * 鸿蒙暂不支持 UI 定义 

# 4.3 资源外部加载 

# 4.3.1 Android 资源外部加载 

将模型通过网络或其他方式存储到本地,将模型文件路径传入 sdk ; 

# 资源文件需提前内置到主工程 res 中。 

# 4.3.2 iOS 资源外部加载 

通过网络下载或其他方式,将 `bundle` 资源包添加到沙盒中; 

在使用 SDK 进行活体认证时,设置 ` MegLiveV5DetectInitConfigItem` 类的 ` bundleFilePath` 为进行路径指定,该路径以 `bundle` 为后缀; 

如果没有指定文件路径或者指定路径异常,同时没有在项目中添加资 源,在启动 SDK 会进行活体认证时,会返回 `NO_ADD_RESOURCE` 错 误。 

* 鸿蒙暂不支持资源加载 

附录 A :语音资源列表 

Key 

释义 

livenessHomePromptBlinkText 

“ ” 请眨眼 

livenessHomePromptOpenMouthText 

“ ” 请张嘴 

livenessHomePromptShakeHeadText 

“ ” 请左右转头 

livenessHomePromptNodText 

- “ ” 请上下点头 

livenessHomePromptStayStillText 

“ ” 很好 

liveness_blink.m4a 

“ ” 请眨眼 音频 

liveness_nod.m4a 

“ 请上下点头 ” 音频 

liveness_mouth.m4a 

“ 请张嘴 ” 音频 

liveness_shakehead.m4a 

“ 请左右转头 ” 音频 

liveness_well_done.m4a 

“ 很好 ” 音频 

liveness_action_confirme 

默认空,灵动活体确认模式提示文案对应音频 

liveness_move_back.m4a 

“ ” 请离远一些 

liveness_move_forward.m4a 

“ ” 请离近一些 

liveness_approach_slowly.m4a 

“ ” 请缓慢靠近屏幕 

liveness_hold_still.m4a 

“ ” 很好,保持不动 

附录 B :图片资源列表 

Key 

释义 

liveness_action_normal 

动作活体中机器人正常状态的图片 

liveness_action_down 点头动画中的低头图片 

liveness_action_up 点头动画中的抬头图片 

liveness_action_eye_close 眨眼动画中的闭眼图片 

liveness_action_mouth_close 张嘴动画中的闭嘴图片 

liveness_action_mouth_open 张嘴动画中的张嘴图片 

liveness_action_left 摇头动画中的向左摇头图片 liveness_action_right 摇头动画中的向右摇头图片 

liveness_agreement_noselected 

协议勾选框未选中图片 

liveness_agreement_selected 

协议勾选框选中图片 

liveness_logo_icon 

底部 logo 图片 

liveness_home_agreement 

协议页中间的图片 

liveness_home_back_highlight 

协议页返回图标深色版图片 

liveness_home_back_normal 

协议页返回图标正常版图片 

liveness_home_close 

# 退出图片 

liveness_home_vertical_remind 

垂直提示图片 

liveness_action_success_icon 灵动活体确认模式下,动作成功提示 icon 

附录 C :文本资源列表 

Key 

内容描述 

livenessHomeExitPopupwindowTitleText 

提示 

livenessHomeAgreementpageTopTitleText 

# 活体验证 

livenessHomeAgreementpageBottomTitleText 

请正对屏幕,勿遮挡面部 

livenessHomeAgreementpageBottomButtonText 

开始 

livenessHomeExitPopupwindowBodyText 您确认退出验证吗? 

livenessHomeAgreementText 

《用户协议》 

livenessHomePromptReadyText 请将面部对准框内,保证光线充足 livenessHomePromptDarkerText 光太亮,请前往较暗的环境 livenessHomePromptBrighterText 

光太暗,请前往较亮的环境 

livenessHomePromptTooBrightText 

光太亮,请前往较暗的环境 

livenessHomePromptVerticalText 

请保持手机竖向垂直 

livenessHomePromptFrontalFaceText 

请将面部对齐到人脸框 

livenessHomePromptCloserText 

请离近一点 

livenessHomePromptFurtherText 

请离远一点 

livenessHomePromptFrontalFaceInBoundingBoxText 

# 请将面部对齐人脸框 

livenessHomePromptAngleOffsetText 

# 请摆正头部角度 

livenessHomePromptNoEyesOcclusionText 

# 勿遮挡眼睛 

livenessHomePromptNoMouthOcclusionText 

# 勿遮挡嘴巴 

livenessHomePromptMotionBlurText 

# 请保持拍摄清晰 

livenessHomePromptGaussianBlurText 

# 请保持拍摄清晰 

livenessHomePromptNodText 

请上下点头 

livenessHomePromptBlinkText 

# 请眨眼 

livenessHomePromptOpenMouthText 

# 请张嘴 

livenessHomePromptShakeHeadText 

请左右转头 

livenessHomePromptStayStillText 

很好,请保持不动 

livenessHomePromptCheckMultiFaceText 

请确保单人核验 

livenessHomePromptFaceEreaText 

人脸有效面积太小 

livenessHomePromptWaitText 

验证中,请稍候 ... 

livenessHomeScrnAuthorizedRejectText 

本业务办理需要授予录屏权限,请重新操作并允许授权或者联系平台 的人工客服 

livenessHomeScrnAuthorizedRejectButtonText 

确定离开 

附录 D : host 取值列表 

Host 取值 

含义 

https://api.megvii.com 

中国集群(默认) 

https://api-sgp.megvii.com 

新加坡 

https://api-idn.megvii.com 

印尼 

附录 E : UI 可配置项 

UI 页面 

参数名 参数含义 基础配置值 通用 

livenessHomeBackgroundColor1 背景颜色 1 

livenessHomeBackgroundColor2 背景颜色 2 

livenessHomeProcessBarColor 活体录制进度条颜色(动作、炫彩不打光、 loading ) 

livenessHomeDeviceVerticalRemindColor 

垂直提示字体颜色 

协议页 

livenessHomeAgreementpageTopTitleText 

# 协议页面顶部标题文案 

活体验证 

livenessHomeAgreementpageTitleTextSize 

协议页面顶部标题字体大小 

livenessHomeAgreementpageBottomTitleText 

协议页面底部提示文案 请正对屏幕,勿遮挡面部 

livenessHomeAgreementpageBottomTitleTextSize 协议页面底部提示字体大小 

livenessHomeAgreementpageBottomButtonText 

底部按钮文案 

开始 

livenessHomeAgreementpageBottomButtonBeforeClickColor 点击前按钮颜色、协议颜色、返回颜色 浅蓝色 

livenessHomeAgreementpageBottomButtonAfterClickColor 点击后按钮颜色、协议颜色、返回颜色 深蓝色 

livenessHomeAgreementText 

协议文案 

livenessHomePromptReadyText 

准备提示文案 

请将面部对准框内,保证光线充足 

livenessHomePromptDarkerText 

光太亮提示 

光太亮,请前往较暗的环境 

livenessHomePromptBrighterText 

光太暗提示 

光太暗,请 前往较亮的环境 

livenessHomePromptTooBrightText EV 太强提示 

光太亮,请前往较暗的环境 

livenessHomePromptVerticalText 

手机不垂直提示 请保持手机竖向垂直 

livenessHomePromptFrontalFaceText 

检测不到脸提示 

# 请将面部对齐到人脸框 

livenessHomePromptCloserText 

脸太远提示 

请离近一点 

livenessHomePromptFurtherText 

脸太近提示 请离远一点 

livenessHomePromptFrontalFaceInBoundingBoxText 脸不在偏移范围提示 请将面部对齐人脸框 

livenessHomePromptAngleOffsetText 

角度不符合提示 请摆正头部角度 

livenessHomePromptNoEyesOcclusionText 

遮挡眼睛提示 勿遮挡眼睛 

livenessHomePromptNoMouthOcclusionText 

遮挡嘴巴提示 

勿遮挡嘴巴 

livenessHomePromptMotionBlurText 

运动模糊提示 

请保持拍摄清晰 

livenessHomePromptGaussianBlurText 

高斯模糊提示 请保持拍摄清晰 

livenessHomePromptCheckMultiFaceText 单人核验提醒文案 请确保单人核验 

livenessHomePromptFaceEreaText 

人脸有效面积提示文案 人脸有效面积太小 

活体采集页 

livenessHomeCustomPromptBackgroundColor 

自定义业务提示背景颜色 

livenessHomeCustomPromptTextColor 

自定义业务提示字体颜色 

interface_prompt_text 

自定义业务提示内容 

ivenessCustomPromptColor 

自定义业务提示内容对应 icon 颜色 

livenessHomeActionHatColor 

动作活体录制中小帽子颜色 

livenessHomePromptNodText 

点头提示 请上下点头 

livenessHomePromptBlinkText 

眨眼提示 请眨眼 

livenessHomePromptOpenMouthText 

张嘴提示 

请张嘴 

livenessHomePromptShakeHeadText 

摇头提示 

请左右转头 

livenessHomePromptStayStillText 

照镜子成功保持提示 

很好,请保持不动 

livenessHomeNormalRemindTextColor 

炫彩不打光活体录制提示文字颜色 

livenessHomeFlashRemindTextColor 

炫彩打光活体录制提示文字颜色 

livenessHomePromptWaitText 

验证中文案 验证中,请稍候 ... 

退出弹窗 

livenessHomeExitPopupwindowTitleText 退出弹窗标题文案 

提示 

livenessHomeExitPopupwindowTextSize 

退出弹窗标题字号 

livenessHomeExitPopupwindowBodyText 退出弹窗正文文案 

您确认退出验证吗? 

livenessHomeExitPopupwindowBodySize 

退出弹窗正文字号 

livenessHomeConfirmButtonColor 

确认按钮颜色 

livenessHomeCancelButtonColor 取消按钮颜色 

附录 F : SDK 兼容模式图片列表 

活体方式 返回图片名称 图片含义 备注说明 动作活体 

image_best 端上最佳人脸图 

image_mirror 照镜子阶段质量最好的图 

image_nod 

动作阶段点头动作图 

根据配置动作数量和类型,返回相应的动作图 

image_shake 动作阶段摇头动作图 

image_mouth 动作阶段张嘴动作图 

image_blink 动作阶段眨眼动作图 

炫彩活体 

image_best 端上最佳人脸图 

image_flash1 炫彩阶段图 1 

image_flash2 炫彩阶段图 2 

image_flash3 

# 炫彩阶段图 3 

距离活体 

image_best 端上最佳人脸图 

image_near_mirror 近距离照镜子阶段质量最好的图 image_far_mirror 远距离照镜子阶段质量最好的图 image_flash1 炫彩阶段图 1 

image_flash2 炫彩阶段图 2 

image_flash3 炫彩阶段图 3 

灵动活体 

image_best 

端上最佳人脸图 

image_nod 动作阶段点头动作图 根据配置动作类型,返回相应的动作图 image_shake 动作阶段摇头动作图 

image_mouth 动作阶段张嘴动作图 

image_blink 动作阶段眨眼动作图 

image_flash1 炫彩阶段图 1 

image_flash2 炫彩阶段图 2 

image_flash3 炫彩阶段图 3
