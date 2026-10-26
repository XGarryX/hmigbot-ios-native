# SDK 接入配置 

鸿蒙中心仓库接入 

步骤一:添加仓库 

项目根目录 .ohpmrc 配置仓库地址 registry=https:// ohpm.openharmony.cn/ohpm/,https://ohpm.sigmob.com/repos/ ohpm 

备注: 

可以配置多个仓库地址,以英文逗号间隔,多个仓库地址的优先级按 照配置顺序排序。 https://ohpm.sigmob.com/repos/ohpm 为 Sigmob 鸿蒙远程仓库。 

步骤二:添加依赖 

在工程主 module 的 oh-package.json5 文件中需要引入穿山甲 SDK 的模 块,以远程包形式引入: 在 oh-package.json5 添加依赖 

"dependencies": { "@sigmob/adsdk": "${version}"} 

"dependencies": { "@sigmob/adsdk": "${version}"} 

注意: 如果之前接入了 har 或者本次为替换 har 包更新版本,可先执行 hvigorw clean 清除缓存,避免更新 har 包失败。 

SDK 默认构建字节码 HAR ,工程的工程级 build-profile.json5 的 useNormalizedOHMUrl 字段 true 

鸿蒙集成编译环境 

在下述版本验证通过: 

DevEco Studio NEXT Developer Beta6 

构建版本: 5.0.3.402 

# SDK: API12 

添加权限 

# 1. 打开 app 模块的 module.json5 文件 

# 2. 添加以下权限 : 访问网络、获取网络状态 ( 可选 ) 、获取广告追踪标识 (oaid)( 可选 ) 、获取位置信息 ( 可选 ) 

"requestPermissions": [ 

{ 

"name": "ohos.permission.INTERNET", 

"reason": "$string:permission_reason", 

}, 

{ 

"name": 'ohos.permission.APP_TRACKING_CONSENT', 

"reason": '$string:permission_reason', 

}, 

{ 

"name": 'ohos.permission.APPROXIMATELY_LOCATION', 

"reason": '$string:permission_reason', 

}, 

{ 

"name": 'ohos.permission.GET_WIFI_INFO', 

"reason": '$string:permission_reason', 

}, 

{ 

"name": 'ohos.permission.GET_NETWORK_INFO', 

"reason": '$string:permission_reason', 

} 

] 

"requestPermissions": [ 

{ 

"name": "ohos.permission.INTERNET", 

"reason": "$string:permission_reason", 

}, 

{ 

"name": 'ohos.permission.APP_TRACKING_CONSENT', "reason": '$string:permission_reason', 

}, 

{ 

"name": 'ohos.permission.APPROXIMATELY_LOCATION', "reason": '$string:permission_reason', 

}, 

{ 

"name": 'ohos.permission.GET_WIFI_INFO', 

"reason": '$string:permission_reason', 

}, 

{ 

"name": 'ohos.permission.GET_NETWORK_INFO', 

"reason": '$string:permission_reason', 

} 

] 

# 权限名称 

说明 

必要性 

ohos.permission.APP_TRACKING_CONSENT 

' 允许应用读取开放匿名设备标识符 ' , SDK 用于获取 oaid ;可选,影响 转化 

可选 

ohos.permission.INTERNET 

' 允许使用 Internet 网络 ' , SDK 用于网络请求; 

必选 

ohos.permission.GET_WIFI_INFO 

- ' 允许应用获取 Wi-Fi 信息 ' , SDK 用于判断设备连接 wifi 状态 

可选 

ohos.permission.GET_NETWORK_INFO 

- ' 允许应用获取 Network 信息 ', SDK 检查蜂窝数据业务是否启用 可选 

ohos.permission.APPROXIMATELY_LOCATION 

' 允许应用获取设备模糊位置信息 ', SDK 用于获取经纬度 

可选 

ohos.permission.ACCELEROMETER 

# 允许应用读取加速度传感器的数据 

可选 

ohos.permission.VIBRATE 

# 允许应用控制马达振动 

可选 

SDK 初始化 

SDK 初始化 

import { sigmob, sig, SIGConfigBuilder } from '@sigmob/adsdk'; 

onWindowStageCreate(windowStage: window.WindowStage): void { let initData: sig.InitData = { 

appId: 'your app id', appKey: 'your app key', 

windowStage: windowStage, 

context: context 

} let adConfig = builder 

.param(initData) // 设置初始化必要参数 

.privacyController(customController) // 设置自定义设备信息 controller 

.userId('your user id') // 设置用户 ID ,方便后续问题查询 

.builder(); 

sigmob.initialized(adConfig).then(() => { 

Logger.debug(Constants.TAG, 'SigmobAd 初始化成功 ') 

}).catch((err: BusinessError) => { 

Logger.debug(Constants.TAG, 'SigmobAd 初始化失败 ' + JSON.stringify(err)) 

}); 

} 

import { sigmob, sig, SIGConfigBuilder } from '@sigmob/adsdk'; 

onWindowStageCreate(windowStage: window.WindowStage): void { 

let initData: sig.InitData = { 

appId: 'your app id', 

appKey: 'your app key', 

windowStage: windowStage, 

context: context 

} 

let adConfig = builder 

.param(initData) // 设置初始化必要参数 

.privacyController(customController) // 设置自定义设备信息 

controller 

.userId('your user id') // 设置用户 ID ,方便后续问题查询 

.builder(); 

sigmob.initialized(adConfig).then(() => { 

Logger.debug(Constants.TAG, 'SigmobAd 初始化成功 ') 

}).catch((err: BusinessError) => { 

Logger.debug(Constants.TAG, 'SigmobAd 初始化失败 ' + JSON.stringify(err)) 

}); 

} 

SIGConfigBuilder 

export class SIGConfigBuilder { 

/** 

# * 设置初始化的必要参数 

* @param value 

* @returns 

*/ 

param(value: sig.InitData): SIGConfigBuilder; 

/** 

# * 设置自定隐私信息 

* @param value 

- @returns 

*/ 

privacyController(value: SIGCustomPrivacyController): SIGConfigBuilder; 

/** 

# * 设置用户 ID 

- @param value 

- @returns 

*/ 

userId(value: string): SIGConfigBuilder; 

/** 

- 设置用户年龄状态 

- @param value 

*/ 

ageState(value: sig.Age): SIGConfigBuilder; 

/** 

- 设置用户年龄状态 

- @param value 

*/ 

userAge(value: number): SIGConfigBuilder; 

} 

export class SIGConfigBuilder { 

/** 

# * 设置初始化的必要参数 

- @param value 

- @returns 

*/ 

param(value: sig.InitData): SIGConfigBuilder; 

/** 

# * 设置自定隐私信息 

- @param value 

- @returns 

*/ 

privacyController(value: SIGCustomPrivacyController): SIGConfigBuilder; 

/** 

- 设置用户 ID 

- @param value 

- @returns 

*/ 

userId(value: string): SIGConfigBuilder; 

/** 

# * 设置用户年龄状态 

* @param value 

*/ 

ageState(value: sig.Age): SIGConfigBuilder; 

/** 

# * 设置用户年龄状态 

* @param value 

*/ 

userAge(value: number): SIGConfigBuilder; 

} 

# 激励视频广告 

# 场景介绍 

激励广告是一种全屏播放的广告,用户可以在观看完整的广告后获取 奖励 , 视频广告播放结束后会显示结束页面,引导用户进行后续动作。 目前鸿蒙上激励广告的表现形式为:视频播放完展示 Endcard 页面, 或者直接出现广告落地页。 

# 接口说明 

export class SIGRewardVideoAd extends SIGBaseAd { 

/** 

* 设置广告加载监听器 

*/ 

set loadListener(listener: SIGAdLoadListener); 

/** 

- 设置广告交互监听器 

*/ 

set interactionListener(listener: SIGRewardAdInteractionListener) ; 

/** 

- 设置广告交互监听器 

*/ 

set videoListener(listener: SIGVideoListener); 

/** 

- 检查广告是否准备完成,处于可播放状态。 

*/ 

ready(): boolean ; 

/** 

- 加载广告 

*/ 

loadAdData(); 

/** 

# * 播放广告 

- @param options 播放扩展参数 

*/ 

show(options?: sig.AdDisplayOptions); 

/** 

- 销毁资源 

*/ 

destory(): void; 

} 

export class SIGRewardVideoAd extends SIGBaseAd { 

/** 

- 设置广告加载监听器 

*/ 

set loadListener(listener: SIGAdLoadListener); 

/** 

- 设置广告交互监听器 

*/ 

set interactionListener(listener: SIGRewardAdInteractionListener) ; 

/** 

- 设置广告交互监听器 

*/ 

set videoListener(listener: SIGVideoListener); 

/** 

- 检查广告是否准备完成,处于可播放状态。 

*/ 

ready(): boolean ; 

/** 

- 加载广告 

*/ 

loadAdData(); 

/** 

- 播放广告 

- @param options 播放扩展参数 

*/ 

show(options?: sig.AdDisplayOptions); 

/** 

- 销毁资源 

*/ 

destory(): void; 

} 

# 广告加载监听器 

export interface SIGAdLoadListener { 

/** 

- 广告素材缓存成功,此时广告处于等待播放状态 

*/ 

onAdDidLoad: () => void; 

/** 

- 广告加载失败 

- @param error 错误描述信息 

*/ 

onAdLoadError: (error: BusinessError) => void; 

/** 

- 广告数据请求成功,此时广告依然处于不可播放状态 

*/ 

onAdRequestSuccess: () => void; 

} 

export interface SIGAdLoadListener { 

/** 

- 广告素材缓存成功,此时广告处于等待播放状态 

*/ 

onAdDidLoad: () => void; 

/** 

- 广告加载失败 

- @param error 错误描述信息 

*/ 

onAdLoadError: (error: BusinessError) => void; 

/** 

- 广告数据请求成功,此时广告依然处于不可播放状态 

*/ 

onAdRequestSuccess: () => void; 

} 

广告交互监听器 

export interface SIGRewardAdInteractionListener { 

/** 

# * 广告展示 

- @param adInfo 当前渠道信息 

*/ 

onAdShow(): void; 

/** 

# * 调用播放时出错 

- @param error 错误描述信息 

*/ 

onAdShowError(error: BusinessError<void>): void; 

/** 

- 广告点击 

- @param adInfo 当前渠道信息 

*/ 

onAdClick(): void; 

/** 

- 广告关闭 

- @param adInfo 当前渠道信息 

*/ 

onAdClose(): void; 

/** 

# * 用户在观看时点击了跳过 

- @param adInfo 当前渠道信息 

*/ 

onSkipped(): void; 

/** 

# * 奖励发放 

- @param reward 奖励信息 

- @param adInfo 当前渠道信息 

*/ 

onRewardArrived(reward: SIGReward): void; 

} 

export interface SIGRewardAdInteractionListener { 

/** 

# * 广告展示 

- @param adInfo 当前渠道信息 

*/ 

onAdShow(): void; 

/** 

- 调用播放时出错 

- @param error 错误描述信息 

*/ 

onAdShowError(error: BusinessError<void>): void; 

/** 

- 广告点击 

- @param adInfo 当前渠道信息 

*/ 

onAdClick(): void; 

/** 

- 广告关闭 

- @param adInfo 当前渠道信息 

*/ 

onAdClose(): void; 

/** 

- 用户在观看时点击了跳过 

- @param adInfo 当前渠道信息 

*/ 

onSkipped(): void; 

/** 

- 奖励发放 

- @param reward 奖励信息 

- @param adInfo 当前渠道信息 

*/ 

onRewardArrived(reward: SIGReward): void; 

} 

# 视频交互监听器 

export interface SIGVideoListener { 

/** 

- 频播放开始首帧渲染 

*/ 

onVideoStartRenderFrame: () => void; 

/** 

- 视频开始播放 

*/ 

onVideoPlayStart: () => void; 

/** 

- 视频暂停 

*/ 

onVideoPaused: () => void; 

/** 

# * 视频暂停 

*/ 

onVideoPlayCompleted: () => void; 

/** 

- 广告加载失败 

- @param error 错误描述信息 

*/ 

onVideoPlayError: (error: BusinessError) => void; 

} 

export interface SIGVideoListener { 

/** 

- 频播放开始首帧渲染 

*/ 

onVideoStartRenderFrame: () => void; 

/** 

- 视频开始播放 

*/ 

onVideoPlayStart: () => void; 

/** 

# * 视频暂停 

*/ 

onVideoPaused: () => void; 

/** 

# * 视频暂停 

*/ 

onVideoPlayCompleted: () => void; 

/** 

# * 广告加载失败 

* @param error 错误描述信息 

*/ 

onVideoPlayError: (error: BusinessError) => void; 

} 

# 服务端回调说明 

服务器回调模式不是必须的,只是增加了一次第三方服务器的验证判 断。具体的奖励发放由客户端完成。 

服务端回调逻辑: Sigmob 根据 “** 奖励发放条件 “ , ** 先通过 “Simgob ” “ ” 服务端 访问 开发者服务端 向开发者确认是否进行奖励发放,再依 据 “ 开发者服务端 ” 返回的 true/false ,在客户端给出是 / 否发放奖励的 回调。 

Reward 接口说明 

export interface SIGReward { 

/** 

# * 奖励的交易 ID 

*/ 

trans_id: string; 

/** 

# * 本次奖励是否有效 

*/ 

is_verify: boolean; 

/** 

- 当前是否走了服务端回调链路 

*/ 

is_server_callback: boolean; 

/** 

# * 错误信息 

*/ 

error?: BusinessError; 

} 

export interface SIGReward { 

/** 

# * 奖励的交易 ID 

*/ 

trans_id: string; 

/** 

# * 本次奖励是否有效 

*/ 

is_verify: boolean; 

/** 

* 当前是否走了服务端回调链路 

*/ 

is_server_callback: boolean; 

/** 

# * 错误信息 

*/ 

error?: BusinessError; 

} 

# 加载激励视频广告 

# // 创建广告请求参数 

let request: sig.AdRequest = { placementId: placementId, userId: 'YOUR USER ID', 

options: { 

'name': 'codi', 

'id': 't6xu' 

} 

} 

# // 创建广告加载对象 

let rewardVideoAd = new SIGRewardVideoAd(request); 

// 设置广告监听 

rewardVideoAd.adLoadListener = this; 

rewardVideoAd.adInteractionListener = this; 

// 加载广告 

rewardVideoAd.loadAdData(); 

// 创建广告请求参数 

let request: sig.AdRequest = { placementId: placementId, 

userId: 'YOUR USER ID', 

options: { 

'name': 'codi', 

'id': 't6xu' 

} 

} 

# // 创建广告加载对象 

let rewardVideoAd = new SIGRewardVideoAd(request); 

// 设置广告监听 

rewardVideoAd.adLoadListener = this; 

rewardVideoAd.adInteractionListener = this; 

// 加载广告 

rewardVideoAd.loadAdData(); 

# 展示激励视频广告 

广告加载成功后即可展示开屏广告,收到 onAdDidLoad 回调代表广告 加载成功,建议在广告展示前通过 ready 方法判断广告是否准备完 成。 

// 展示广告 

if (rewardVideoAd.ready()) { 

rewardVideoAd.showAd() 

} 

// 展示广告 

if (rewardVideoAd.ready()) { 

rewardVideoAd.showAd() 

} 

插屏广告 

场景介绍 

插屏广告是一种在应用开启、暂停或退出时以全屏或半屏的形式弹出 的广告形式,展示时机巧妙避开用户对应用的正常体验,尺寸大,曝 光效果好。 

接口说明 

export class SIGInterstitialAd extends SIGBaseAd { 

/** 

# * 设置广告加载监听器 

*/ 

set loadListener(listener: SIGAdLoadListener); 

/** 

- 设置广告交互监听器 

*/ 

set interactionListener(listener: SIGInterstitialAdInteractionListener); 

/** 

- 设置广告交互监听器 

*/ 

set videoListener(listener: SIGVideoListener); 

/** 

- 检查广告是否准备完成,处于可播放状态。 

*/ 

ready(): boolean; 

/** 

- 加载广告 

*/ 

loadAdData() ; 

/** 

# * 播放广告 

*/ 

show(options: sig.AdDisplayOptions); 

/** 

# * 销毁数据 

*/ 

destory(); 

} 

export class SIGInterstitialAd extends SIGBaseAd { 

/** 

- 设置广告加载监听器 

*/ 

set loadListener(listener: SIGAdLoadListener); 

/** 

- 设置广告交互监听器 

*/ 

set interactionListener(listener: SIGInterstitialAdInteractionListener); 

/** 

# * 设置广告交互监听器 

*/ 

set videoListener(listener: SIGVideoListener); 

/** 

- 检查广告是否准备完成,处于可播放状态。 

*/ 

ready(): boolean; 

/** 

- 加载广告 

*/ 

loadAdData() ; 

/** 

- 播放广告 

*/ 

show(options: sig.AdDisplayOptions); 

/** 

# * 销毁数据 

*/ 

destory(); 

} 

# 广告加载监听器 

export interface SIGAdLoadListener { 

/** 

- 广告素材缓存成功,此时广告处于等待播放状态 

*/ 

onAdDidLoad: () => void; 

/** 

- 广告加载失败 

- @param error 错误描述信息 

*/ 

onAdLoadError: (error: BusinessError) => void; 

/** 

- 广告数据请求成功,此时广告依然处于不可播放状态 

*/ 

onAdRequestSuccess: () => void; 

} 

export interface SIGAdLoadListener { 

/** 

- 广告素材缓存成功,此时广告处于等待播放状态 

*/ 

onAdDidLoad: () => void; 

/** 

- 广告加载失败 

- @param error 错误描述信息 

*/ 

onAdLoadError: (error: BusinessError) => void; 

/** 

- 广告数据请求成功,此时广告依然处于不可播放状态 

*/ 

onAdRequestSuccess: () => void; 

} 

广告交互监听器 

export interface SIGInterstitialAdInteractionListener extends SIGAdInteractionListener { 

/** 

- 广告展示 

- @param adInfo 当前渠道信息 

*/ 

onAdShow(): void; 

/** 

# * 调用播放时出错 

- @param error 错误描述信息 

*/ 

onAdShowError(error: BusinessError<void>): void; 

/** 

- 广告点击 

- @param adInfo 当前渠道信息 

*/ 

onAdClick(): void; 

/** 

- 广告关闭 

- @param adInfo 当前渠道信息 

*/ 

onAdClose(): void; 

/** 

- 用户在观看时点击了跳过 

- @param adInfo 当前渠道信息 

*/ 

onSkipped(): void; 

} 

export interface SIGInterstitialAdInteractionListener extends SIGAdInteractionListener { 

/** 

- 广告展示 

- @param adInfo 当前渠道信息 

*/ 

onAdShow(): void; 

/** 

# * 调用播放时出错 

- @param error 错误描述信息 

*/ 

onAdShowError(error: BusinessError<void>): void; 

/** 

- 广告点击 

- @param adInfo 当前渠道信息 

*/ 

onAdClick(): void; 

/** 

# * 广告关闭 

* @param adInfo 当前渠道信息 

*/ 

onAdClose(): void; 

/** 

# * 用户在观看时点击了跳过 

* @param adInfo 当前渠道信息 

*/ 

onSkipped(): void; 

} 

# 加载插屏广告 

// 创建广告请求参数 

let request: sig.AdRequest = { 

placementId: placementId, 

userId: 'YOUR USER ID', 

options: { 

'name': 'codi', 

'id': 't6xu' 

} 

} 

# // 创建广告加载对象 

let interstitialAd = new SIGInterstitialAd(request); 

// 设置广告监听 

interstitialAd.adLoadListener = this; 

interstitialAd.adInteractionListener = this; 

// 加载广告 

interstitialAd.loadAdData(); 

// 创建广告请求参数 

let request: sig.AdRequest = { placementId: placementId, 

userId: 'YOUR USER ID', 

options: { 'name': 'codi', 

'id': 't6xu' 

} 

} 

// 创建广告加载对象 

let interstitialAd = new SIGInterstitialAd(request); 

// 设置广告监听 

interstitialAd.adLoadListener = this; 

interstitialAd.adInteractionListener = this; 

// 加载广告 

interstitialAd.loadAdData(); 

# 广告展示 

广告加载成功后即可展示开屏广告,收到 onAdDidLoad 回调代表广告 加载成功,建议在广告展示前通过 ready 方法判断广告是否准备完 成。 

// 展示广告 

if (interstitialAd.ready()) { 

interstitialAd.showAd() 

} 

// 展示广告 

if (interstitialAd.ready()) { 

interstitialAd.showAd() 

} 

隐私设置 

隐私合规 

设置个性化推荐开关状态 

sigmob.personalizedAdvertising(state: sig.PersonalizedAdvertising); sigmob.personalizedAdvertising(state: sig.PersonalizedAdvertising); 

/** 

# * 个性化状态 

*/ 

export enum PersonalizedAdvertising { 

on = 0, // 开启 

off = 1, // 关闭 

} 

/** 

# * 个性化状态 

*/ 

export enum PersonalizedAdvertising { 

on = 0, // 开启 

off = 1, // 关闭 

} 

# 开发者可以通过自定义隐私设备信息,来控制位置信息的获取和广告 标识符 OAID 的获取 

export class SIGCustomPrivacyController { 

/** 

# * 是否允许 SDK 主动使用地理位置信息 

- @return true 可以获取, false 禁止获取。默认为 true 

*/ 

isCanUseLocation(); 

/** 

- isCanUseLocation=false 时,可传入地理位置信息 

- @returns 地理位置信息 SGLocation 

*/ 

getLocation(): sig.Location; 

/** 

- 是否可以使用 oaid 

- @returns true: 可以使用; false: 不可以使用 

*/ 

isCanUseAppTrackingConsent(): boolean; 

/** 

- isCanUseOaid=false 时,开发者可以传入 oaid 

* 

- @return oaid 

*/ 

async getDevOaid(): Promise<string>; 

} 

export class SIGCustomPrivacyController { 

/** 

- 是否允许 SDK 主动使用地理位置信息 

- @return true 可以获取, false 禁止获取。默认为 true 

*/ 

isCanUseLocation(); 

/** 

- isCanUseLocation=false 时,可传入地理位置信息 

- @returns 地理位置信息 SGLocation 

*/ 

getLocation(): sig.Location; 

/** 

- 是否可以使用 oaid 

- @returns true: 可以使用; false: 不可以使用 

*/ 

isCanUseAppTrackingConsent(): boolean; 

/** 

- isCanUseOaid=false 时,开发者可以传入 oaid 

* 

- @return oaid 

*/ 

async getDevOaid(): Promise<string>; 

} 

# 错误码 

错误码 

说明 

备注 

# 200000 

无广告填充 

偶发属于正常现象。如频繁发生建议开发者自查: 1. 确保 App 可以获 取设备标识符 (OAID\ODID) ; 2. 频繁请求不展示会触发屏蔽机制,请 勿频繁请求 

# 600000 

广告位 ID 为空 

开发者请求时没传入 Sigmob 广告位 id 

600001 

当前版本不支持该功能 

# 600002 

返回的 Response 的 body 是 undefined 

# 600003 

广告正在加载中,请稍后再加载 

# 600004 

广告加载过于频繁,请稍后再加载 

600005 

# 广告请求时传入 token 为空 

开发者没有传入 header bidding 的 token 

600006 

视频加载或播放错误 

内部错误,请联系技术支持 

600008 

请求出错 

Sigmob SDK 判断由于网络错误原因造成请求超时 

600009 

下载出错 

sdk 在进行资源下载时发生了错误 

600010 

广告加载超时 

# 600011 

MD5 校验失败 

600014 

广告不支持的创意类型 

600015 

广告不支持的素材类型 

600016 

非法请求 URL 

610000 

初始化失败 

610001 

未初始化 

610002 数据库错误 

内部错误,请联系技术支持 610003 参数错误 

610004 接口错误 

610005 解密错误 

620000 

代理服务错误 

620002 attribution is empty
