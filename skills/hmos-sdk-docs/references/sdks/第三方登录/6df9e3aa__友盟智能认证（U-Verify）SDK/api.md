# 智能认证 SDK 接口调用说明 

# SDK 方法说明 

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

// ( 必选 ) 设置密钥,即当前应用创建的方案秘钥 

LoginAuth.setSecret(this.secret); 

# // ( 必选 ) 配置授权页界面参数 

const uiConfig: AuthUiConfig = new AuthUiConfig(); 

const component: WrappedBuilder<[]> = wrapBuilder(clauseComponent); // 页面模式组件 

const modal: WrappedBuilder<[]> = wrapBuilder(modalComponent); // 弹窗模式组件 

uiConfig.loginPageComponent = component; // 页面模式使用 component ,弹窗模式使用 modal 

uiConfig.numberMagin = { top: 200 }; 

uiConfig.numberFontColor = Color.Black; 

uiConfig.loginBtnMagin = { left: 30, top: 260, right: 30 }; uiConfig.loginBtnWidth = 200; uiConfig.loginBtnHeight = 72; uiConfig.loginBtnFontSize = 18; 

uiConfig.loginBtnFontColor = Color.Red; uiConfig.loginBtnAlignRuleOption = { 

middle: { anchor: '__container__', align: HorizontalAlign.Center }, top: { anchor: '__container__', align: VerticalAlign.Top }, }; uiConfig.privacyCbWidth = 20; uiConfig.privacyCbHeight = 20; uiConfig.privacyCbMargin = { left: 20, bottom: 30 }; uiConfig.privacyCbAlignRuleOption = { left: { anchor: '__container__', align: HorizontalAlign.Start }, bottom: { anchor: '__container__', align: VerticalAlign.Bottom } 

}; 

uiConfig.privacyMargin = { left: 30, right:10 }; uiConfig.privacyAlignRuleOption = { 

middle: { anchor: '__container__', align: HorizontalAlign.Center }, top: { anchor: 'clause_checkBox', align: VerticalAlign.Top } 

}; 

uiConfig.privacySpanBeforeText = " 请阅读并勾选 ,"; 

uiConfig.privacySpanEndText = ' 协议 '; 

uiConfig.pricacyCbClipText = ' 请你选择同意协议 '; 

LoginAuth.setUIConfig(uiConfig); 

// ( 可选 ) 设置弹窗模式, true 或 false 

LoginAuth.setDialog(false); 

// ( 必选 ) 拉起授权页界面 , 设置超时时间,单位 ms 

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

// console.log(` 加速接口的回调 : ${result}`); 

// }); 

}) 

} 

.padding(10) 

} 

.width("100%") 

} 

} 

# // 页面模式组件示例 

@Builder 

export function clauseComponent(): void { 

Image($r('app.media.app_icon_camera')) 

.width('80vp') 

.height('80vp') 

.margin({top:120}) 

.alignRules({ 

middle: { anchor: '__container__', align: HorizontalAlign.Center }, top: { anchor: '__container__', align: VerticalAlign.Top }, 

# }) 

} 

# // 弹窗模式组件示例 

@Builder 

function modalComponent(): void { 

Column(){ 

Image($r('app.media.app_icon_camera')) 

.width('80vp') 

.height('80vp') 

.margin({top:40}) 

.onClick((event)=>{ 

// 

// Index.quitLoginPage() 

}) 

.alignRules({ 

middle: { anchor: '__container__', align: HorizontalAlign.Center }, top: { anchor: '__container__', align: VerticalAlign.Top }, 

}) 

Text("text123") 

.width('100%') .height('20vp') .margin({ top:3 }) 

.textAlign(TextAlign.Center) 

.fontColor(Color.Gray) .fontSize('15fp') 

Text(' 切换到短信登录 ') 

.width('100%') .height('40vp') 

.margin({ 

top: 80 }) 

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

// ( 可选 ) 检测运行环境,判断设备环境是否适合 SDK 运行 , 结果会在 接口回调监控中返回 

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

} } 

更多内容请参考友盟官方文档说明: https://developer.umeng.com/ docs/143070/
