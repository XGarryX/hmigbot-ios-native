## 思迪商城 **sdk** 集成使用文档 

# 思迪商城 **sdk** 集成使用文档 

### 一、安装配置 

- 1、修改工程 oh-package.json5 增加库的引用 

JavaScript 

"@thinkive/tk-harmony-base": 

"file:./libs/thinkive-harmony-base-release-V1.0.0-20240919.har", 

"@thinkive/tk-harmony-mall": "file:./libs/thinkive-harmony-mall.har", 

##### 2、将 sdk 包中的思迪框架配置 thinkive 目录拷 贝到 entry/src/main/resources/rawfile 目录 

- 3、开启工程 build-profile.json5 的 useNormalizedOHMUrl 

JSON 

"buildOption": { 

"strictMode": { 

"useNormalizedOHMUrl": true, 

} 

} 

4、ohpm install 安装更新工程库 

### 二、使用 

#### **1** 、初始化思迪框架 

项目 entry 的 UIAbility 中 

TypeScript 

```arkts
onCreate(want: Want, launchParam: AbilityConstant.LaunchParam): void { TKAppEngine.shareInstance().start({context: **this** .context}) 
```

} 

#### **2** 、增加权限 

需要在项目 entry 中的 module.json5 中增加如下配置 

TypeScript 

"requestPermissions": [ 

{ 

// 网络请求权限 

"name": "ohos.permission.INTERNET" }, 

{ 

"name": "ohos.permission.GET_NETWORK_INFO" }, { //WIF 信息权限 

"name": "ohos.permission.GET_WIFI_INFO" 

}, .... ] 

#### **3** 、引用 

##### JavaScript 

import { TKMallSDK, TKMallWeb,TKMallActionType ,TKMallAction} from '@thinkive/tk-harmony-mall' 

#### **4** 、注册商城代理事件 

##### JavaScript 

##### //注册代理事件 

TKMallSDK.shareInstance().registerDelegateEvent((action: TKMallAction) => { **let** type:string = action.actionType 

**if** (type == TKMallActionType.Login) { 

//登录事件 

- } **else if** (type == TKMallActionType.LoginOut) { //登录退出事件 

} **else if** (type == TKMallActionType.Share) { //分享事件 

/** 

* action.params 参数说明 

businessType String 分享类型,如图片分享、链接分享 

shareTypeList String 分享平台的类型,多个用,分割(数据字典) title String 标题 link String 链接 

content String 内容 

imgUrl String 图片 

webpageUrl String 微信兼容低版本小程序分享,低版本转成链接分享 userName String 微信小程序ID type String 小程序版本 path String 小程序页面路径 withShareTicket String 内容 description String 小程序描述 params JSON 可选参数 */ **let** sharaParams = action.params 

} **else** { //其他自定义事件 } 

#### **5** 、代理事件完成回调商城 

JavaScript 

**let** result: Record<string, Object> = { 'xxx': 'xxx' } TKMallSDK.shareInstance().onDelegateEventBack(TKMallActionType.Login, result) 

#### **6** 、打开商城 

##### 支持设置的参数 

JavaScript params:{ url Web 加载的url isLayoutFullScreen 是否是全屏默认true 

statusBarEnable 状态栏显示/隐藏,入口页设置了全屏才会生效,非全屏无法隐 藏系统状态栏默认false 

bottomBarEnable 是否展示底部安全区默认true tabBarEnable 是否有tabbar(嵌入tab 容器) title 标题文本 isChangeTitle 是否跟着浏览器进行title 切换 isEncodeURL 是否进行URL 编码 customUserAgent 自定义userAgent titleColor 标题的颜色 titleBgColor 标题栏背景颜色 bottomAreaBgColor 底部栏非安全区背景颜色 backgroundColor Web 背景色 statusStyle 状态栏风格,状态栏上的小图标颜色风格(0:黑色,1:白色) backPressEnable 返回按钮的显示/隐藏 

} 

##### 1)组件集成方式打开 

JavaScript @Entry 

@Component 

##### **export struct** Index { 

@Provide onBackPressChanged: boolean = **false** ; 

@Provide onBackPressFilter: boolean = **false** ; 

// 实现H5 内部页面的逐级返回 onBackPress(): boolean | void { **this** .onBackPressChanged = ! **this** .onBackPressChanged; **return this** .onBackPressFilter; } build() { 

Column({ space: 10 }) { 

TKMallWeb({ 

params: { 

'url': 'http://xx.xx.xx/lcsm/mall/index', 

'tabBarEnable': **true** , 

'bottomBarEnable': **false** 

} 

}) 

} } 

} 

##### 2)路由方式打开 

JavaScript 

TKMallSDK.shareInstance().openWebPage({ 'url': 'http://www.xxx.xx' } **)** 

##### 3)Navigation 方式打开 

JavaScript 

//Navigation 的路由栈 

pathStack: NavPathStack = **new** NavPathStack() 

##### **TKMallSDK.shareInstance().openWebPage(** 

**{ 'url': }, pathStack** 

**'url': 'http://www.xxx.xx'** 

**)** )
