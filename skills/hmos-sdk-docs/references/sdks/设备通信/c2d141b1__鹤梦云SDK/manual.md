# 鹤梦云 SDK (鸿蒙版)合规使用指南 

SDK 包名: hmviewersdk 

SDK 版本: 1.0.1 

开发者:南京鹤梦信息技术有限公司 

生效日期: 2026 年 6 月 22 日 

一、最新 SDK 版本说明 

本合规使用指南适用于鹤梦云 SDK (鸿蒙版)的最新发布版本。请开 发者在集成或升级本 SDK 时,使用本指南所对应的版本,以确保满 足个人信息保护相关法律法规及监管要求。 

项目 

说明 

SDK 名称 

鹤梦云 SDK (鸿蒙版) 

SDK 包名 

hmviewersdk 

最新版本号 

1.0.1 

BundleName 

com.huiyun.care.har.viewerpro 

适用系统 

HarmonyOS NEXT ( API Level 12 及以上) 

最低 SDK 依赖 

HarmonyOS SDK 5.0.0.13 (SP4) 及以上 

建议:请开发者将应用中的本 SDK 升级至上述最新版本,以获得完 整的个人信息保护能力与功能支持。后续版本如有涉及个人信息处理 规则的重大变化,我们将适时更新本指南。 

二、权限调用合规要求 

本 SDK 涉及以下系统权限,所有权限的申请与使用均遵循最小必要 原则,仅在用户触发对应功能时按需申请,不与 SDK 业务功能无关 的系统权限。本 SDK 不使用其未声明但 SDK 使用者应用软件已申请 的相关系统权限。 

权限名称 

权限说明 

使用目的 

权限申请时机 

ohos.permission.INTERNET 

允许使用 Internet 网络 

用于设备配网、视频直播、录像回放、报警推送、云服务访问等联网 功能 调用 SDK 联网相关功能时 

ohos.permission.GET_NETWORK_INFO 

允许获取当前网络状态信息 

用于判断当前网络连接状态( WiFi / 移动网络 / 断网),以决策是否 发起网络请求 

SDK 初始化及网络功能调用时 

ohos.permission.GET_WIFI_INFO 

允许获取 WiFi 状态及连接信息 

用于获取当前连接的 WiFi SSID 、 BSSID 等信息,以完成设备网络配 置 

用户触发 WiFi 配网、 AP 配网时 

ohos.permission.ACCESS_BLUETOOTH 

允许访问蓝牙设备能力 

用于搜索附近蓝牙设备、建立蓝牙连接以完成设备配网 

用户触发蓝牙配网时 

ohos.permission.APPROXIMATELY_LOCATION 

允许获取设备粗略位置 

用于获取 WiFi 列表、扫描周围网络信息以完成网络配置 ( HarmonyOS 系统中 WiFi 扫描需配合粗略位置权限) 

用户触发 AP 配网、 WiFi 配网时 

ohos.permission.CAMERA 

# 允许使用相机 

用于扫描设备二维码以添加设备;用于显示摄像头实时预览画面 用户触发扫码配网、视频预览时 

ohos.permission.MICROPHONE 

# 允许使用麦克风 

用于采集用户语音并传输至设备端,实现双向语音对讲;用于录制自 定义提示音 

用户触发对讲、自定义提示音录制时 

ohos.permission.WRITE_IMAGEVIDEO 

允许读写图片和视频文件 

# 用于将录像文件或截图保存至终端本地相册 

用户触发录像下载、截图保存时 

ohos.permission.VIBRATE 

允许控制设备振动 

用于在收到报警事件推送时通过设备振动提醒用户 

收到报警推送时 

ohos.permission.PRIVACY_WINDOW 

允许将窗口设置为隐私窗口 

用于在视频直播及录像回放时将视频播放窗口设置为隐私窗口,防止 视频画面内容被截屏或录屏泄露 

视频播放窗口启动时 

权限分类说明: 

必选权限: ohos.permission.INTERNET 。无此权限 SDK 无法连接服 务端,核心功能无法实现。 

可选权限:其余 9 项均为可选权限,用户拒绝授权仅影响对应功能, 不影响 SDK 其他功能正常使用。 

三、延迟初始化要求 

为避免在未获取用户同意前 SDK 提前处理用户个人信息,本 SDK 支 持延迟初始化机制。开发者必须在用户阅读并同意应用《隐私政策》 后,才能调用 SDK 初始化接口。 

# 3.1 初始化接口 

本 SDK 提供 HmSdk.getInstance() 获取 SDK 单例,提供 init() 接口 进行初始化。 

// SDK 初始化示例(必须在用户同意隐私政策后调用) 

import { HmSdk } from 'hmviewersdk'; 

import { ServerEnvEnum, RegionIdEnum } from 'hmviewersdk'; 

const sdk: IZJViewerSDK = HmSdk.getInstance(); 

// 设置区域(国内 =0x01 ,海外 =0x02 ) 

sdk.setRegionid(RegionIdEnum.DOMESTIC); 

// 初始化 SDK 

const success: boolean = sdk.init( 

getContext(), // 上下文 

'your_companyId', // 公司 ID 

'your_appId', // 应用 ID 

ServerEnvEnum.PRODUCTION // 环境: PRODUCTION= 生产环 境, TEST= 测试环境 

); 

if (success) { 

console.info('SDK 初始化成功 '); 

} 

# 3.2 初始化时机合规指引 

应用首次启动时,应在用户阅读并同意《隐私政策》后,再调 用 init() 接口; 

若用户拒绝《隐私政策》或撤回同意,不得调用 init() 接口; 

对于第三方登录(微信、支付宝)等扩展功能,开发者应当在用户主 动选择对应登录方式并触发登录时,再调用相关登录接口 ( loginByThirdParty ),不应在 SDK 初始化时即开始获取第三方账 

# 号信息; 

对于音视频对讲、蓝牙配网等功能,应在用户主动点击对应功能按钮 时,再调用 MICROPHONE 、 ACCESS_BLUETOOTH 等权限并执行相 应业务逻辑,不得在后台静默申请。 

# 四、最小化使用功能要求 

本 SDK 提供了一系列配置能力,允许开发者根据业务诉求按需启用 或关闭扩展业务功能及可选个人信息的收集。开发者应根据实际业务 需求进行最小化配置,避免过度收集。 

# 4.1 区域与服务器环境配置 

SDK 通过 RegionIdEnum 控制数据处理区域,通 过 ServerEnvEnum 控制服务器环境。 

# // 国内环境(默认) 

sdk.setRegionid(RegionIdEnum.DOMESTIC); // 0x01 

# // 海外环境(如需) 

sdk.setRegionid(RegionIdEnum.FOREIGN); // 0x02 

// 服务器环境:生产环境(应用上线时使用) 

sdk.init(context, companyId, appId, ServerEnvEnum.PRODUCTION); // 0 

# // 服务器环境:测试环境(仅在联调测试时使用) 

sdk.init(context, companyId, appId, ServerEnvEnum.TEST); // 1 

# 4.2 关闭扩展业务功能(可选) 

本 SDK 的扩展业务功能(如微信登录、 AI 智能分析等)未提供独立 的开启 / 关闭配置接口。开发者可通过 " 不调用对应业务接口 " 的方式, 使终端用户无法使用相应功能,从而避免相关个人信息的收集与处 理。 

SDK 涉及的可选扩展业务功能及关闭方式如下: 

扩展功能 

涉及个人信息 

关闭方式(开发者侧) 

关闭后的影响 

微信账号登录 

微信 OpenID 、 UnionID 、 AccessToken 

" " 不在应用界面展示 微信登录 入口,不调用第三方登录相关接口 终端用户无法使用微信快捷登录 

支付宝登录 / 支付 

支付宝用户标识、订单信息 

不在应用界面展示 " 支付宝登录 / 支付 " 入口,不调用第三方登录及云 存储套餐购买相关接口 

终端用户无法使用支付宝登录及支付 

AI 智能分析(人脸识别、区域入侵) 

人脸特征数据、监测区域配置坐标 

不在应用界面展示 AI 智能分析相关功能入口,不调用对应业务接口 人脸识别、区域入侵报警等 AI 报警功能不可用 

自定义提示音 

用户录制的音频数据 

不在应用界面展示自定义提示音录制入口,不调用对应业务接口 终端用户无法使用自定义报警提示音 

# 本地相册时光管理 

# 本地相册数据 

不在应用界面展示时光相册功能入口,不调用对应业务接口 

本地相册时光管理功能不可用 

—— 说明:上述关闭方式由开发者自行控制 只需在应用前端不展示对 应功能入口、不触发对应业务接口调用, SDK 内部即不会收集相关个 人信息。 SDK 本身不会主动发起这些扩展功能的数据采集。 

# 4.3 日志与诊断功能 

SDK 在本地保存运行日志和崩溃信息用于故障排查,不会自动向服务 端上报。仅当用户主动反馈问题(如在应用内点击 " 反馈问题 / 上报 " 日志 按钮)时,相关日志才会被打包发送至云端用于问题定位。 

此外, SDK 提供 setDebugMode 接口控制本地调试日志输出,开发者 可在正式发布版本中关闭调试日志: 

# // 关闭调试日志输出 

sdk.setDebugMode(false); 

# 4.4 本地缓存清理(可选) 

SDK 在本地缓存了用户头像、录像缩略图、设备配置等数据,开发者 可通过 cleanLocalCache 接口按需清理: 

// 清理 7 天前的本地缓存数据(保留 7 天内的缓存) 

const userModule = sdk.newUserModule(); 

userModule.cleanLocalCache(7, { 

onSuccess: () => console.info(' 清理成功 '), 

onError: (code, msg) => console.error(' 清理失败 :', msg) 

}); 

// 清理全部本地缓存( days=0 表示清除所有缓存) 

userModule.cleanLocalCache(0, { 

onSuccess: () => console.info(' 已清除全部本地缓存 '), 

onError: (code, msg) => console.error(' 清除失败 :', msg) 

# }); 

说明: days 参数表示保留缓存的天数,传入 0 表示清除全部可清理 的本地缓存数据。 

五、隐私政策披露要求与示例说明 

在应用接入、使用本 SDK 服务前,开发者必须在应用的《隐私政 策》中向用户告知本 SDK 的相关信息,并获取用户的同意。如涉及 处理敏感个人信息(如摄像头画面、麦克风音频、人脸特征数据)或 向中华人民共和国境外提供个人信息,建议开发者单独弹框获取用户 的单独同意。 

# 5.1 文字披露示例 

开发者可在应用《隐私政策》中按以下文字示例向用户告知: 第三方 SDK 名称:鹤梦云 SDK (鸿蒙版) 

第三方公司名称:南京鹤梦信息技术有限公司 

# 收集个人信息类型: 

应用基本信息(设备型号、操作系统版本、网络状态、 SDK 运行日 志、崩溃信息)、应用内设备标识符(设备 ID 、设备序列号、 MAC 地址)、网络信息( WiFi SSID 、 WiFi 密码)、用户注册信息(手机 号码、邮箱地址、密码、微信 OpenID/UnionID/AccessToken 、支付 宝用户标识)、音视频数据(摄像头实时画面、麦克风音频)、智能 报警数据(报警事件记录、关联截图、人脸特征数据)、 IoT 设备信 息(设备类型、设备 ID 、开关状态)、云服务订单信息。 

使用目的: 

为开发者应用提供 IoT 智能设备(摄像头、 NVR 、门锁、传感器等) 的配网接入、音视频预览、云端录像回放、智能报警、 IoT 设备联 动、云存储套餐购买及账号管理等能力。 

# 隐私政策链接: 

https://websvr.smartcloudcon.com/mallservices/#/H5Agreement/ harmony-sdk 

# 5.2 表格披露示例 

如应用《隐私政策》采用表格形式披露,可参考下表: 

第三方 SDK 名称 

第三方公司名称 

收集个人信息类型 

使用目的 

隐私政策链接 

鹤梦云 SDK (鸿蒙版) 

南京鹤梦信息技术有限公司 

应用基本信息、应用内设备标识符、网络信息、用户注册信息、音视 频数据、智能报警数据、 IoT 设备信息、云服务订单信息 

提供 IoT 智能设备的配网接入、音视频预览、云端录像、智能报警、 IoT 联动及云存储等服务 

https://websvr.smartcloudcon.com/mallservices/#/H5Agreement/ harmony-sdk 

# 5.3 敏感个人信息与跨境传输单独同意 

本 SDK 涉及以下敏感个人信息处理及跨境传输场景,开发者应显著 提示用户并获取单独同意: 

摄像头画面、麦克风音频:涉及摄像头、麦克风等敏感权限,建议在 用户首次触发视频预览、对讲等功能时单独弹框告知; 

人脸特征数据:仅在用户主动订阅 AI 智能分析扩展功能时收集,建 议单独弹框获取用户同意; 

跨境传输:当 SDK 服务于海外用户( RegionIdEnum.FOREIGN ) 时,涉及将用户个人信息传输至境外服务器(南京鹤梦信息技术有限 公司境外云服务节点),建议在用户选择海外服务时单独弹框告知并 获取同意。 

六、最终用户授权同意的建议方式 

建议开发者采用以下方式获取用户的授权同意,确保符合个人信息保 护相关法律法规: 

6.1 首次启动时的隐私政策同意 

应用首次启动时,应显著展示《隐私政策》全文及摘要; 

用户主动点击同意后方可调用 HmSdk.getInstance().init() 接口; 

若用户拒绝,应不调用 SDK 初始化接口,并退出或限制使用需要本 SDK 提供能力的功能; 

SDK 初始化时建议进行二次确认(如弹出权限申请说明对话框),告 知用户 SDK 将收集的信息类型及用途。 

# 6.2 敏感权限的运行时申请 

HarmonyOS 系统下,涉及用户隐私的敏感权限(位置、相机、麦克 风、蓝牙等)需在运行时动态申请,并向用户明确说明申请目的。建 议采用 " 业务场景前置说明 + 权限申请 " 模式: 

// 示例:进入实时视频预览页面时申请相机权限 

```arkts
import { abilityAccessCtrl, common } from '@ohos.app.ability.accessibility'; 
```

const atManager = abilityAccessCtrl.createAtManager(); 

try { 

await atManager.requestPermissionsFromUser(context, ['ohos.permission.CAMERA']); 

// 用户同意后,再开始视频预览 

startLivePreview(deviceId); 

} catch (err) { 

console.error(' 用户拒绝授权 :', err); 

} 

# 6.3 第三方登录的单独同意 

" 对于微信、支付宝等第三方登录功能,建议在用户主动选择 微信登 " " " 录 或 支付宝登录 按钮时,再调用相关登录接口,并向用户明确告 知: 

// 用户主动点击 " 微信登录 " 按钮后调用 

sdk.newLoginModule().loginByThirdParty( 

AccountTypeEnum.WECHAT, 

thirdPartyUid, 

thirdPartyToken, 

{ 

onSuccess: (result) => { /* 登录成功 */ }, 

onError: (code, msg) => { /* 登录失败 */ } 

} 

); 

# 6.4 撤回同意的机制 

开发者应在应用内提供便捷的撤回同意入口,如: 

" - - " 在 我的 设置 隐私设置 页面,提供《隐私政策》重新查看入口; 

提供 " 撤回授权 " 按钮,撤回后调用 SDK 登出接口 logout() 并停止 SDK 数据处理; 

提供 " 删除账号 / 注销账号 " 入口,调用 deleteAccount() 接口删除用 户账户及关联数据。 

七、保障个人信息主体权利 

为保障用户便捷地行使访问、复制、更正、删除个人信息等权利,本 SDK 提供了相关接口供开发者调用。 

7.1 获取用户数据副本(访问权 / 复制权) 

// 获取当前登录用户的账号信息 

const userModule = sdk.newUserModule(); 

const ownerAccount: UserBean = userModule.getOwnerAccountInfo(); 

# // 获取当前登录用户的个人信息 

const ownerVCard: UserVCardBean = userModule.getOwnerVCardInfo(); 

# // 获取用户 ID 

const userId: string = userModule.getUserId(); 

7.2 修改用户数据(更正权) 

// 修改用户个人信息 

const userModule = sdk.newUserModule(); 

const vCard: UserVCardBean = { 

nickName: ' 新昵称 ', 

# // ... 其他字段 

}; 

const result: number = userModule.setOwnerVCardInfo(vCard); 

if (result === 0) { 

console.info(' 修改成功 '); 

} 

# 7.3 删除用户数据(删除权 / 注销权) 

SDK 提供账号登出与账号删除两个层级的接口,开发者应根据用户实 际诉求调用: 

( 1 )账号登出(仅清空登录态,账号仍保留) 

// 用户点击 " 退出登录 " 时调用 

const loginModule = sdk.newLoginModule(); 

await loginModule.logout(); 

console.info(' 已退出登录 '); 

- ( 2 )账号删除(彻底删除账号及关联数据) 

// 用户点击 " 注销账号 " 时调用(不可恢复,请谨慎使用) 

const userModule = sdk.newUserModule(); 

userModule.deleteAccount({ 

onSuccess: () => { 

console.info(' 账号已删除 '); 

# // 跳转至应用退出页面或登录页面 

}, 

onError: (code, msg) => { 

console.error(' 账号删除失败 :', msg); 

} 

# }); 

# 7.4 清除本地缓存 

用户有权要求清除 SDK 在本地存储的缓存数据,开发者可调 用 cleanLocalCache 接口: 

// 清除所有本地缓存( keepDays=0 表示清除所有可清理的缓存) 

const userModule = sdk.newUserModule(); 

userModule.cleanLocalCache(0, { 

onSuccess: () => console.info(' 本地缓存已清除 '), 

onError: (code, msg) => console.error(' 清除失败 :', msg) 

# }); 

# 7.5 登录态查询 

// 查询用户当前是否登录 

const loginModule = sdk.newLoginModule(); 

const isLogin: boolean = loginModule.isLogin(); 

# 7.6 PaaS AccessToken 刷新 

当用户登录态过期( AccessToken 失效)时, SDK 内部会在调用接口 时自动检测并调用 getPaasAccessToken 刷新 Token ,开发者无需手 动处理。如下示例展示如何主动获取最新的 AccessToken : 

// 获取当前有效的 PaaS AccessToken 

const loginModule = sdk.newLoginModule(); 

const accessToken: string = await loginModule.getPaasAccessToken(); 

# 7.7 响应时效承诺 

对于用户行使权利的请求,开发者应在收到请求后的 15 个工作日 内 予以响应。如需本 SDK 提供方协助处理用户权利请求,可通过本指 南第八条中的联系方式与我们联系。 

八、其他合规使用补充说明 

# 8.1 关于日志上报 

本 SDK 不会在后台自动收集或上报用户的个人信息、日志或设备数 据。具体说明如下: 

SDK 在运行过程中仅在本地记录运行日志和崩溃信息,不会自动上传 至云端; 

仅当用户主动在应用内触发反馈(如点击 " 反馈问题 / 上报日志 " 按 钮)时,本地保存的日志才会被打包发送至云端用于问题定位; 

SDK 不会在后台静默获取用户个人信息,所有数据采集与上报均需用 户主动操作触发。 

8.2 关于权限最小化原则 

本 SDK 严格遵循权限最小化原则: 

仅声明与 SDK 业务功能合理关联的系统权限; 

不声明与 SDK 功能无关的系统权限; 

不使用其未声明但 SDK 使用者应用软件已申请的相关系统权限; 

建议开发者在自身应用中也仅申请与业务功能相关的权限,不要因为 使用了本 SDK 就无差别申请所有列出的权限。 

# 8.3 关于隐私政策链接 

本 SDK 的完整隐私政策文本请参考 

https://websvr.smartcloudcon.com/mallservices/#/H5Agreement/ harmony-sdk 建议开发者在应用的《隐私政策》显著位置披露本链 接,便于用户查阅。 

# 8.4 联系方式 

如开发者在接入或使用本 SDK 过程中遇到任何合规相关问题,或需 要协助处理用户权利请求,请通过以下方式联系我们: 

联系方式 

信息 

公司名称 

南京鹤梦信息技术有限公司 

官方网站 

https://www.smartcloudcon.com/ 

电子邮箱 

support@smartcloudcon.com 

联系电话 

18851948911 

响应时效 

15 个工作日内 

文档版本: v1.2 | 更新日期: 2026 年 6 月 22 日 

开发者:南京鹤梦信息技术有限公司 

版权所有:南京鹤梦信息技术有限公司 保留一切权利。
