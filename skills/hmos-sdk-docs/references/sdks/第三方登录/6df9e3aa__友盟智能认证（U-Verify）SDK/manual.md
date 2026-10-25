# 智能认证 SDK 集成接入指南 

概述 

运行环境 

鸿蒙 NEXT API12 及以上 stage 模式的普通应用,需在工程级别开启字 节码,暂不支持元服务。 

服务说明 

智能认证一键登录本机号码校验 

友盟 + 智能认证,整合三大运营商号码认证能力和短信验证能力,可 简化 App 登录流程,提升注册转化;也可以用于密码找回、支付校 验、业务风控等多种业务场景。 

# 权限授予 

为确保 SDK 正确使用,需在开发者应用中授予以下权限。 

权限 

用途 

ohos.permission.INTERNET 

允许应用程序联网,用于访问网关和认证服务器。 

ohos.permission.GET_NETWORK_INFO 

获取网络状态,判断是否数据、 wifi 等。 

ohos.permission.SET_NETWORK_INFO 

允许应用配置数据网络,取号时需要切换到蜂窝网络。 

ohos.permission.APP_TRACKING_CONSENT 

获取设备信息用于生成脱敏的终端用户设备标识, 

以提供统计分析服务 

# 注意事项 

智能认证 SDK 不可单独集成使用,需同时集成 @umeng/ common@umeng/analytics@umeng/verify 方可成功使用。 

集成文档 

一、安装 SDK 

在项目的根目录下执行如下命令。 

ohpm install @umeng/common --registry=https:// ohpm.openharmony.cn/ohpm 

ohpm install @umeng/analytics --registry=https:// ohpm.openharmony.cn/ohpm 

ohpm install @umeng/verify --registry=https:// ohpm.openharmony.cn/ohpm 

二、集成 SDK 

在项目的 AppScope/resources/rawfile 目录下新增一个配置文件 umconfig.json, 

# 文件内容如下 

{ 

"appKey": " 你的 apppkey", 

"channel": " 你的渠道 " 

} 

在应用模块目录下,添加 abilityStage 工程文件,例如 entry/src/ main/ets/abilityStage/MyAbilityStage.ets ,具体位置如下图 

# 文件内容如下 

// entry/src/main/ets/abilityStage/MyAbilityStage.ets 

import AbilityStage from '@ohos.app.ability.AbilityStage'; 

import { init, preInit, InternalPlugin } from '@umeng/analytics'; // 引用统计分析 

import { VerifyPlugin } from "@umeng/verify"; // 智能认证 

export default class MyAbilityStage extends AbilityStage { 

onCreate() { 

preInit({ 

context: this.context.getApplicationContext(), 

enableLog: true, // 开发时,打开调试日志,可观察 sdk 是否集成成功 plugins: [new InternalPlugin(), new VerifyPlugin()] 

}); 

init(); // 初始化(用户在同意隐私政策后调用此方法) 

} 

} 在模块的的 module.json5 文件中添加 srcEntry ,指向 abilityStage 文 件的地址 

在模块的 module.json5 文件中添加权限声明 

"requestPermissions": [ 

{ 

"name": "ohos.permission.INTERNET" 

}, 

{ 

"name": "ohos.permission.GET_NETWORK_INFO" 

}, 

{ 

"name": "ohos.permission.SET_NETWORK_INFO" 

} 

], 

参考下图 

注意在适当位置先调用 preInit 方法,经用户授权同意隐私政策后调用 init 方法,才会开始日志的采集和传输。 

三、创建 SDK 密钥 

通过以下鸿蒙官方代码,获取应用的包名、包签名、应用唯一标识 (需开发者先在 IDE 中配置签名或自动签名后,才可获取到标识), 用于创建 sdk 密钥。 

```arkts
import { bundleManager } from '@kit.AbilityKit'; 
```

=> { 

const packageName = bundleInfo.name; 

console.log(" 包名 :" + packageName); 

const sign = bundleInfo.signatureInfo.fingerprint; 

console.log("sign:" + sign); 

const appIdentifier = bundleInfo.signatureInfo.appIdentifier; 

console.log("appid:" + appIdentifier); 

# }); 

打开友盟智能认证后台页面 https://ai.login.umeng.com/apps/list , 创建鸿蒙应用后选择配置方案,输入取到的包名、包签名、 AppId 创 建方案,得到认证方案密钥用于集成 SDK 。 

四、 SDK 方法说明 

1. 一键登录方法,在需要使用页面进行如下配置。 

// entry/src/main/ets/pages/Index.ets 

```arkts
import { bundleManager } from '@kit.AbilityKit'; 
```

import { LoginAuth, AuthUiConfig, PhoneVerify } from "@umeng/ verify"; 

@Entry 

@Component 

struct Index { 

@State secret: string = " 你的方案密钥 " 

build() { 

Column({ space: 0 }) { 

Row() { 

Button(' 一键登录场景 ') 

.onClick(() => { 

// ( 必选 ) 创建实例,即 SDK 的功能入口,整个登录流程状态都在此回 调中返回 

const callback = (result: string) => { 

console.log(` 一键登录回调 : ${result}`); 

const obj: object = JSON.parse(result); 

const code: string = obj['_code']; 

if (code === "600000") { 

// ( 必选 ) 清除流程回调监听,调用后再次拉起页面需重新初始化实例 

LoginAuth.clearAuthHelper(); 

// ( 可选 ) 退出授权页界面,调用后仅关闭页面,可以不初始化实例再 次拉起页面 

// LoginAuth.quitPage(); 

} 

}; 

LoginAuth.createHelper(callback); 

# // ( 必选 ) 设置密钥,即当前应用创建的方案秘钥 

LoginAuth.setSecret(this.secret); 

// ( 必选 ) 配置授权页界面参数 

const uiConfig: AuthUiConfig = new AuthUiConfig(); 

const component: WrappedBuilder<[]> = wrapBuilder(clauseComponent); // 页面模式组件 

const modal: WrappedBuilder<[]> = 

wrapBuilder(modalComponent); // 弹窗模式组件 

uiConfig.loginPageComponent = component; // 页面模式使用 component ,弹窗模式使用 modal 

uiConfig.numberMagin = { top: 200 }; 

uiConfig.numberFontColor = Color.Black; 

uiConfig.loginBtnMagin = { left: 30, top: 260, right: 30 }; 

uiConfig.loginBtnWidth = 200; 

uiConfig.loginBtnHeight = 72; 

uiConfig.loginBtnFontSize = 18; 

uiConfig.loginBtnFontColor = Color.Red; 

uiConfig.loginBtnAlignRuleOption = { 

middle: { anchor: '__container__', align: HorizontalAlign.Center }, top: { anchor: '__container__', align: VerticalAlign.Top }, 

}; 

uiConfig.privacyCbWidth = 20; 

uiConfig.privacyCbHeight = 20; 

uiConfig.privacyCbMargin = { left: 20, bottom: 30 }; 

uiConfig.privacyCbAlignRuleOption = { 

left: { anchor: '__container__', align: HorizontalAlign.Start }, bottom: { anchor: '__container__', align: VerticalAlign.Bottom } 

}; 

uiConfig.privacyMargin = { left: 30, right:10 }; 

uiConfig.privacyAlignRuleOption = { 

middle: { anchor: '__container__', align: HorizontalAlign.Center }, 

top: { anchor: 'clause_checkBox', align: VerticalAlign.Top } 

}; 

uiConfig.privacySpanBeforeText = " 请阅读并勾选 ,"; 

uiConfig.privacySpanEndText = ' 协议 '; uiConfig.pricacyCbClipText = ' 请你选择同意协议 '; LoginAuth.setUIConfig(uiConfig); 

// ( 可选 ) 设置弹窗模式, true 或 false 

LoginAuth.setDialog(false); 

# // ( 必选 ) 拉起授权页界面 , 设置超时时间,单位 ms 

LoginAuth.getToken(5000); 

// ( 可选 ) sdk 界面点击事件监听接口 , 即授权页拉起后监听授权页及 二次弹窗页点击事件 

const cb = (code: string, jsonString: string) => { 

console.log("sdk 界面点击事件监听 :" + code + " " + jsonString); 

}; 

LoginAuth.setUIClick(cb); 

// ( 可选 ) 检测运行环境。判断设备环境是否适合 SDK 运行 , 结果会在 接口回调监控中返回。 

// LoginAuth.checkEnvAvailable(); 

// ( 可选 ) 获取运营商类型。 CMCC :中国移动; CUCC :中国联通; CTCC :中国电信。 

// LoginAuth.getCurrentCarrierName((res: string) => { 

// console.log(" 运营商类型 :" + res); 

// }); 

# // ( 可选 ) 获取复选框状态 

// LoginAuth.queryCheckBoxIsChecked((checked: boolean) => { 

// console.log(" 查询复选框状态 :" + checked); 

// }); 

- // ( 可选 ) 一键登录加速接口,可设置超时时间 , 单位 ms 

// 注意:此方法会提前预取号,要在 getToken 前 2~3 秒以上先调用。 

// LoginAuth.accelerate(5000, (result: string) => { 

- // console.log(` 加速接口的回调 : ${result}`); 

// }); 

# }) 

} 

.padding(10) 

} 

.width("100%") 

} 

} 

# // 页面模式组件示例 

@Builder 

export function clauseComponent(): void { Image($r('app.media.app_icon_camera')) .width('80vp') 

.height('80vp') 

.margin({top:120}) 

.alignRules({ 

middle: { anchor: '__container__', align: HorizontalAlign.Center }, top: { anchor: '__container__', align: VerticalAlign.Top }, 

}) 

} 

# // 弹窗模式组件示例 

@Builder 

function modalComponent(): void { Column(){ Image($r('app.media.app_icon_camera')) .width('80vp') .height('80vp') 

.margin({top:40}) 

.onClick((event)=>{ 

# // 

// Index.quitLoginPage() 

}) 

.alignRules({ 

middle: { anchor: '__container__', align: HorizontalAlign.Center }, top: { anchor: '__container__', align: VerticalAlign.Top }, 

}) 

Text("text123") .width('100%') .height('20vp') 

.margin({ 

top:3 

}) 

.textAlign(TextAlign.Center) 

.fontColor(Color.Gray) 

.fontSize('15fp') 

Text(' 切换到短信登录 ') 

.width('100%') 

.height('40vp') 

.margin({ 

top: 80 

}) 

.textAlign(TextAlign.Center) 

.fontColor(Color.Gray) 

.fontSize('15fp') 

} 

.width('95%') 

.height('90%') 

.backgroundColor(Color.Orange) 

} 

2. 本机号码校验方法,在需要使用页面进行如下配置。 

// entry/src/main/ets/pages/Index.ets 

```arkts
import { bundleManager } from '@kit.AbilityKit'; 
```

import { LoginAuth, AuthUiConfig, PhoneVerify } from "@umeng/ verify"; 

@Entry 

@Component 

struct Index { 

@State secret: string = " 你的方案密钥 " 

build() { 

Column({ space: 0 }) { 

Row() { 

Button(' 本机号码验证场景 ') 

.onClick(() => { 

// ( 必选 ) 创建实例,即 SDK 的功能入口,整个登录流程状态都在此回 调中返回 

const callback = (result: string) => { 

console.log(` 本机号码校验回调 : ${result}`); 

const obj: object = JSON.parse(result); 

const code: string = obj['_code']; 

if (code === "600000") { 

// ( 必选 ) 清除流程回调监听 

PhoneVerify.clearAuthHelper(); 

} 

}; 

PhoneVerify.createHelper(callback); 

// ( 必选 ) 设置密钥,即当前应用创建的方案秘钥 

PhoneVerify.setSecret(this.secret); 

// ( 必选 ) 获取本机号码校验 token ,设置超时时间,单位 ms 

PhoneVerify.getToken(5000); 

// ( 可选 ) 检测运行环境,判断设备环境是否适合 SDK 运行 , 结果会在 

# 接口回调监控中返回 

// PhoneVerify.checkEnvAvailable(); 

// ( 可选 ) 本机号码校验加速接口,可设置超时时间 , 单位 ms 。 

// 注意:加速方法可以加快本机号码校验接口获取 token 速度,可提 前调用,如 hap 初始化时。 

// PhoneVerify.accelerate(5000, (result: string) => { 

// console.log(` 开发者调用加速接口的回调 : ${result}`); 

// }); 

}) 

} 

.padding(10) 

} 

.width("100%") 

} 

} 

更多内容请参考友盟官方文档说明: 

https://developer.umeng.com/docs/143070/detail/2923915 https://developer.umeng.com/docs/143070/detail/3024935 https://developer.umeng.com/docs/143070/detail/3022007
