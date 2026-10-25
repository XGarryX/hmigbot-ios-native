# 屹通基础工具 SDK 使用文档 

本文档面向集成 YTBasicCoreLib 的 HarmonyOS 开发者,说明 SDK 的安装、初始化、常用能力调用方式、权限要求和使用建议。 

项目 

说明 

SDK 名称 

屹通基础工具 SDK 

包名 

@yitong/ytbasiccorelib 

主入口 

index.ets 

SDK 类型 

HarmonyOS HAR 

当前版本 

1.0.0 

# 1. 功能概览 

YTBasicCoreLib 是面向 HarmonyOS 应用的基础能力库,覆盖应用框 架、存储、设备、编码、权限、文件、压缩、图片、媒体、定位和系 统工具等常用场景。 

能力模块 

主要 API 

用途 

应用框架 

YTAppFramework 、 BaseConfig 、 DefaultConfig 

统一保存应用上下文和基础配置,为存储、资源、权限等能力提供运 行环境。 

本地存储 

YTStore 、 YTSimpleStoreImp 、 MMKVStoreImp 

封装 MMKV 和 Preferences 键值存储能力。 

设备与编码 

YTDeviceID 、 YTDeviceUtil 、 YTHexUtil 、 YTBase64Util 、 YTDigestUtil 

提供设备标识、设备信息、编码转换和摘要计算能力。 

权限管理 

YTPermissionCheck 、 YTPermissionDialogProvider 

封装权限检查、权限申请、权限说明弹窗和系统设置跳转。 文件与压缩 

ytfs 、 YTSafeRawFile 、 YTSafeInputFile 、 YTSafeOutputFile 、 YTMiniZip 

支持文件读写、安全文件和 ZIP 压缩解压。 

图片与媒体 

ImageCache 、 CustomerImage 、 YTPhotoUtil 、 YTCarmeraUtil 、 YTCameraManager 

提供图片缓存、相册选择、拍照和相机管理能力。 

系统工具 

YTLocationManagerService 、 YTContactUtil 、 YTSmsUtil 、 YTCallUtil 、 YTWindowUtil 、 YTToast 

封装定位、通讯录、短信、拨号、窗口和 Toast 等系统能力。 

# 2. 安装与引入 

在宿主工程中引入 HAR 依赖后,可从包入口按需导入需要的能力。 包名以 oh-package.json5 中的 name 值为准。 

// oh-package.json5 

{ 

"dependencies": { 

"@yitong/ytbasiccorelib": "file:../YTBasicCoreLib" 

} 

} 

import { 

YTAppFramework, 

YTStore, 

YTPermissionCheck, 

YTToast, 

YTMiniZip 

# } from '@yitong/ytbasiccorelib'; 

# 3. 初始化建议 

建议在应用启动阶段完成框架初始化,并在用户同意隐私政策后再调 用涉及个人信息或系统权限的能力。 

// 示例:在 AbilityStage 或 UIAbility 初始化阶段保存上下文 

YTAppFramework.getInstance().init(this.context); 

存储、 rawfile 读取、 RSA 证书读取等能力依赖应用上下文时,应确 

# 保先完成初始化。 

相机、相册、定位、通讯录等能力应在具体业务场景触发后再申请权 限。 

生产环境建议关闭不必要日志,避免输出用户个人信息或敏感业务数 据。 

# 4. 常用能力示例 

# 4.1 本地存储 

YTStore 提供统一的键值读写入口,底层可使用 MMKV 或 Preferences 。 

YTStore.setString('user_name', 'Tom'); 

const userName = YTStore.getString('user_name', ''); 

YTStore.setBoolean('first_open', false); 

const firstOpen = YTStore.getBoolean('first_open', true); 

# 4.2 权限检查与申请 

YTPermissionCheck 可用于运行时权限检查和申请。宿主应用需要先 在自身 module.json5 中声明对应权限。 

YTPermissionCheck.requestPermissions( 

this.context, 

['ohos.permission.CAMERA'], 

(status: boolean, msg: string) => { 

if (status) { 

# // 已授权,继续调用相机能力 

} else { 

# // 根据 msg 提示用户或引导至设置页 

} 

} 

); 

# 4.3 Toast 提示 

YTToast.showToast(' 操作成功 '); 

# 4.4 编码、摘要与字符串工具 

const base64Text = YTBase64Util.encode('hello'); 

const hexText = YTHexUtil.encode(new Uint8Array([1, 2, 3])); 

const digest = YTDigestUtil.md5Encode('hello'); 

const masked = YTStringMaskUtil.maskMobile('13800138000'); 

# 4.5 文件读写与 rawfile 

通用文件操作可使用 ytfs ;包内 rawfile 或安全文件读取可使用 YTSafeRawFile 、 YTSafeInputFile 、 YTSafeOutputFile 。 

# // 示例:根据业务路径写入文件 

ytfs.manager.writeTextSync('/data/storage/el2/base/files/ demo.txt', 'hello'); 

# // 示例:读取 rawfile 

const rawFile = new YTSafeRawFile(resourceManager, 'config.json'); 

# 4.6 压缩与解压 

YTMiniZip 封装 native MiniZip 能力,适用于文件打包、资源解包和 离线数据处理。 

// 具体参数以项目中 YTMiniZip 导出的接口定义为准 

// const result = YTMiniZip.unzip(zipPath, targetDir); 

4.7 图片、相册与相机 

ImageCache / CustomerImage :用于图片缓存和图片加载展示。 

YTPhotoUtil :用于相册选择、图片 URI 处理和图片信息读取。 

YTCarmeraUtil / YTCameraManager :用于拍照或更底层的相机管理 场景。 

4.8 定位、通讯录、短信与拨号 

YTLocationManagerService :封装定位服务,适合在授权后获取位置 或地址信息。 

YTContactUtil :封装联系人读取能力,适合联系人选择或通讯录业务 场景。 

YTSmsUtil :封装短信拉起能力,适合按业务参数发起短信发送。 

YTCallUtil :封装拨号拉起能力,适合按号码进入拨号流程。 

# 5. 权限与合规说明 

YTBasicCoreLib 的 HAR 模块自身未声明系统权限。宿主应用应按实 际启用能力声明和申请权限。 

能力 

可能涉及权限 

建议 

相机 

ohos.permission.CAMERA 

在用户触发拍照、扫码等场景时申请。 

定位 

ohos.permission.LOCATION 、 ohos.permission.APPROXIMATELY_LOCATION 

完成位置用途告知后再申请。 

通讯录 

ohos.permission.READ_CONTACTS 

仅在联系人选择或通讯录业务中申请。 

相册 / 媒体 

READ_MEDIA 、 WRITE_MEDIA 、 READ_IMAGEVIDEO 、 WRITE_IMAGEVIDEO 

按系统版本和实际读写场景声明。 

持久化数据 

ohos.permission.STORE_PERSISTENT_DATA 

仅在需要卸载后保留数据时声明。 

# 6. 最佳实践 

按需导入 API ,避免业务模块依赖整个基础库实现细节。 

涉及权限的能力放在具体业务触发点,不在应用启动时集中申请敏感 权限。 

本地存储只保存业务必要数据;敏感信息应加密、脱敏或避免落盘。 

相册、通讯录、定位等个人信息处理场景,应在宿主 App 隐私政策 中披露。 

文件和解压目录应设置清理策略,避免临时文件长期留存。 

生产环境避免输出含个人信息、密钥、证件号、手机号等敏感内容的 日志。 

# 7. 常见问题 

问题 

说明 

调用存储或 rawfile 相关能力前需要做什么? 

建议先初始化 YTAppFramework ,确保 SDK 能获取应用上下文和资 源管理器。 

SDK 是否会主动申请权限? 

不会。 HAR 模块自身未声明权限,宿主应用需要按实际功能自行声明 和申请。 

设备 ID 能力是否必须使用? 

不是。只有业务需要本地设备或安装实例标识时再调用相关接口。 

图片、定位、通讯录数据会默认上传吗? 

不会。 SDK 只提供本地工具封装,数据上传由宿主应用业务逻辑自行 决定并负责合规。 

文档结束
