# **GSFastSDK 接入文档** 

## **一、概述** 

GSFastSDK 是基于鸿蒙平台 PlayerSDK(直播)和 VodSDK(点播)开发的一站式音视频播放快速集成 SDK,包含 

@gensee/fastsdk_ui (UI 模块)和 @gensee/fastsdk_core (核心逻辑模块)。提供 UI 源码依赖、HAR 包依赖两种方式, 满足用户「直接使用」或「微调 UI」的不同需求,无需自行开发 UI 即可快速接入直播/点播能力。 

## **二、环境要求** 

操作系统:HarmonyOS 

编程语言:ArkTS 

最低版本要求:5.0.1(13) 

依赖基础:需确保项目已兼容 PlayerSDK/VodSDK 基础依赖(如 @ohos/axios": "2.2.6" ) 

## **三、依赖配置** 

### **3.1 两种 UI 模块依赖方式** 

根据是否需要修改 UI,选择对应的依赖方式。 

#### **方式1:UI 源码依赖(需微调 UI 时)** 

忽略 fastsdk_ui.har 文件,将 fastsdk_ui 文件夹配置依赖到项目根目录的 build-profile.json5 中: 

ts "modules": [ { "name": "fastsdk_ui", "srcPath": "../fastsdk_ui",// 具体路径需按项目配置更改,可参考Demo项目 } ] 在 oh-package.json5 中配置: ts "dependencies": { "@gensee/fastsdk_ui": "@module:fastsdk_ui", } 

注意:采用源码依赖方式时,fastsdk _ui_ 模块的版本更新、功能差异适配需由您自行维护; _fastsdk_ core 核心模块仍需您手动替换 libs 目录下的 fastsdk_core.har 包以完成版本更新。 

#### **方式2:HAR 包依赖(无需修改 UI 时)** 

将 fastsdk_ui.har 文件放到项目libs目录下(具体看项目配置) 

ts "dependencies": { "@gensee/fastsdk_ui": "file:libs/fastsdk_ui.har",// 具体路径需按项目配置更改 } 

说明:通过该方式依赖接入无需关注 fastsdk_core.har ,后续更新只需替换 fastsdk_ui.har 文件即可。 

## **四、基础配置** 

### **4.1 UIAbility 生命周期配置** 

在应用的 UIAbility 中配置 SDK 生命周期回调,确保 SDK 感知应用前后台状态: ```typescript import { GSFastSDK } from '@gensee/fastsdk_ui'; 

```arkts
export default class EntryAbility extends UIAbility { // 应用切到前台时调用 onForeground(): void { hilog.info(0x0000, 'testTag', '% {public}s', 'Ability onForeground'); GSFastSDK.onForeground(); } 
```

// 应用切到后台时调用 onBackground(): void { hilog.info(0x0000, 'testTag', '%{public}s', 'Ability onBackground'); GSFastSDK.onBackground(); } 

// 其他生命周期方法... } ``` 

## **五、核心功能接入** 

### **5.1 初始化参数说明** 

FastInitParam 继承自 PlayerSDK 的 InitParam ,新增播放模式配置,参数说明如下: 

|**参数名**|**类型**|**必填**|**说明**|
|---|---|---|---|
|playMode|FastSDKPlayMode|是|播放模式, LIVE (直播)/ VOD (点播)|
|domain|string|是|直播/点播域名/IP|
|number|string|是|直播ID/点播ID|
|nickName|string|是|昵称|
|joinPwd|string|否|加入密码|
|groupCode|string|否|分组号(分组课堂使用)|
|serviceType|string|否|服务类型(如traning/webcast)|
|userId|string|否|自定义用户ID ,id大于10亿才会生效|
|loginAccount|string|否|站点登录账号|
|loginPwd|string|否|站点登录密码|
|k|string|否|认证K值|
|userData|string|否|用户自定义参数|

### **5.2 加入直播/点播** 

通过 fastSDK.join() 方法快速接入直播/点播,示例代码: ```typescript import { FastSDK, FastInitParam, FastSDKPlayMode } from '@gensee/fastsdk_ui'; 

// 1. 创建 FastSDK 实例 const fastSDK = new FastSDK(); 

// 2. 构建初始化参数 let initParam = new FastInitParam(); initParam.playMode = FastSDKPlayMode.LIVE; // 直播模式(VOD 为点播模 式) initParam.domain = this.vodDomin; // 域名/IP initParam.number = this.vodId; // 直播/点播 ID initParam.nickName = this.nickname; // 昵称 initParam.joinPwd = this.passcode; // 加入密码 initParam.groupCode = this.groupCode; // 分组号 initParam.serviceType = this.serviceType; // 服务类型 initParam.userId = this.userId; // 自定义用户ID initParam.loginAccount = this.userAccountName; // 站点登 录账号 initParam.loginPwd = this.userAccountPW; // 站点登录密码 initParam.k = this.kValue; // 认证 K 值 initParam.userData = this.userExtraData; // 用户自定义参数 

// 3. 加入直播/点播 fastSDK.join(this.getUIContext(), initParam) `` 调用 join`方法后,会跳转至具体的页面,参数如果有误,会在页面 中弹出具体的错误信息。 

## **六、全局 UI 配置** 

通过 GSFastConfig 类可自定义 FastSDK 内置 UI 的显示/隐藏及样式,配置需在 fastSDK.join() 之前设置。 

### **6.1 配置项说明** 

|**配置项**|**类型**|**默认值**|**说明**|
|---|---|---|---|
|showDoc|boolean|true|是否显示文档模块|
|showChapter|boolean|true|是否显示章节模块|
|showChat|boolean|true|是否显示聊天模块|
|showQa|boolean|true|是否显示问答模块|
|showIntro|boolean|true|是否显示简介模块|
|showHandUp|boolean|true|是否显示举手模块|
|showSwitchNet|boolean|true|是否显示优选网络按钮|
|showDanmu|boolean|true|是否显示弹幕模块|
|marquee|Marquee | undefned|undefned|跑马灯配置(无则不显示)|
|fxedMoneyArray|number[]|[]|打赏固定金额列表(最多6个),金额单位为分|
|portraitLiveVideo|boolean|false|是否进入竖屏观看直播视频模式|

### **6.2 Marquee 跑马灯配置** 

export class Marquee { content: string = ""; // 跑马灯文本内容 textColor: string = ''; // 文本颜色(如 #FFFFFF) textSize: number = 1; // 文本大小 speed: number = 1; // 滚动倍速(数值越大越快) } 

### **6.3 配置示例** 

import { GSFastConfig, Marquee } from '@gensee/fastsdk_ui'; 

// 1. 基础 UI 显隐配置 GSFastConfig.showDoc = false; // 隐藏文档模块 GSFastConfig.showIntro = false; // 隐藏简介模块 

// 2. 跑马灯配置 const marquee = new Marquee(); marquee.content = "欢迎使用 GSFastSDK"; marquee.textColor = "#FF0000"; marquee.textSize = 30; marquee.speed = 2; GSFastConfig.marquee = marquee; 

// 3. 打赏金额配置 GSFastConfig.fixedMoneyArray = [1, 5, 10, 20, 50, 100]; // 最多6个金额 

// 4. 完成配置后,调用 join 方法加入直播/点播 fastSDK.join(this.getUIContext(), initParam); 

## **七、注意事项** 

1. 依赖路径需根据实际项目结构调整,确保 file: 路径指向正确的源码目录/HAR 包位置; 2. GSFastConfig 配置需在 fastSDK.join() 前完成,否则配置不生效; 

3. 打赏金额列表 fixedMoneyArray 最多支持6个数值,超出部分会被忽略; 

4. 必须在 UIAbility 中添加应用前后台状态切换的通知代码,否则在特定连麦场景下,应用切后台时,SDK 会有异常崩溃问题。
