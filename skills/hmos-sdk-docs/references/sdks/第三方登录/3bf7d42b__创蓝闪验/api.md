# 接入文档

一.准备工作

概述

前置条件

能力介绍

创建应用

快速体验Demo

开发环境搭建

二.SDK使用说明

1.初始化

2.预取号

3.拉起授权页

4.关闭授权页

5.其他API

a.设置log开关

三.授权界面修改

1.设计规范

2.页面可调整属性、布局

四.本机认证

1.初始化

2.本机认证

3.手机号后台服务端校验

五.返回码对照

外层错误码

内层错误码

六.常见问题

1.code:1001msg:初始化请求异常

2.code:10029msg:用户不存在

3.code:19msg:包名校验不通过

1

# 一.准备工作

# 概述

本文是创蓝闪验 SDK_HarmonyOS 端接入文档,用于指导 SDK 的集成使用。在对接之前您需要花 5-

10 分钟阅读以下条目,可减少对接过程中的问题。

●

全国SDK管理服务平台【创蓝闪验SDK】

●

HarmonyOS Developer生态市场地址【创蓝闪验SDK】

●

OpenHarmony三方库中心仓地址【创蓝闪验SDK】

●

APP个人信息披露请参考【创蓝闪验SDK合规使用指南】

●

常见问题请移步至【对接问题】

●

版本升级详细说明请移步至【升级指南】

# 前置条件

●

SDK支持中国移动、联通、电信的取号能力。

●

SDK支持网络环境为:

○

纯数据网络

○

数据网络与wifi网络双开

●

对于双卡手机,SDK取当前流量卡号码

●

SDK使用DevEco Studio 5.0.1 Release(5.0.5.315, built on January 3, 2025)开发,支持API12

及以上版本。

# 能力介绍

一键登录:SDK获取当前流量卡对应的token,通过服务端可置换当前流量卡的手机号码。

本机校验:SDK获取当前流量卡对应的token,提供手机号码,通过服务端可校验提供的手机号是否为当

前流量卡的手机号码。

| 注意:本机校验和一键登录是两个单独的能力,两者的token不能互用,否则会报"应用能力不匹配", |  |
|---|---|

|  | 请根据需求选择对应能力。 |
|---|---|

2

# 创建应用

应用的创建流程及APPID的获取,请查看「账号创建」文档

注意:应用 AppId 与包名、包签名一一绑定,调试和正式版本由于证书不一样,需要分别创建应用,否

则初始化会报包签名校验不通过。

# 快速体验Demo

将创建应用时获得的bundleName和appid,appkey分别填入Demo工程中即可体验(appid和appkey在

文件AppConfig中配置)

demo示例代码:https://github.com/253CL/CLShanYan_Harmony/tree/main/ShanYanDemo

# 开发环境搭建

1.导入har:

●

本地导入方式:将SDK压缩包中har添加到工程中。在oh-package.json5中配置如下内容:

```
"dependencies": {
"@shanyan/shanyansdk": "file:../ShanYanSDK"
  }
```

●

OHPM仓库导入方式:

```
ohpminstall@shanyan/shanyansdk
1
```

2.在model.json5中配置如下权限:

```
"requestPermissions": [
  { "name": "ohos.permission.INTERNET"},
  { "name": "ohos.permission.GET_NETWORK_INFO"},
  { "name": "ohos.permission.SET_NETWORK_INFO" }
]
```

权限说明

| 权限 | 使用场景 | 使用目的 | 申请时机 |
|---|---|---|---|
| ohos.permission.INTE RNET(必选) | 网络通信 | 允许应用程序联网,用 于访问网关和认证服务 器 | 调用网关取号功能时申 请 |

3

|  |  |  |  |
|---|---|---|---|
| ohos.permission.GET NETWORK INFO _ _ (必选) | 查看网络状态 | 获取网络状态,判断是 否开启数据、WiFi等 | 调用功能接口的前置检 查 |
| ohos.permission.SET _ NETWORK INFO(必 _ 选) | 进行网络切换通信 | 允许程序改变网络连接 状态,当用户未使用数 据流量时,切换为数据 流量,以获取用户手机 号码 | Wi-Fi和蜂窝网络双开 且需要使用功能接口时 申请 |

# 二.SDK使用说明

# 1.初始化

使用场景

●

在app启动时进行调用

●

保证在预取号或一键登录前至少调用一次

●

只需调用一次,多次调用不会多次初始化,与一次调用效果一致

请求示例代码

1.导入SDK头文件

```
import { CLResult, CLSDKManager } from'@shanyan/shanyansdk'
1
```

2.初始化方法

```
static asyncinit(context: Context, appId: string): Promise<CLResult>
letresult: CLResult=awaitCLSDKManager.init(getContext(this), "APP_ID")
```

参数说明:

| 参数 | 类型 | 说明 |
|---|---|---|
|  |  |  |

4

|  |  |  |
|---|---|---|
| context | Context | 调用者的上下文环境。 |
| appId | string | 应用的appid |

返回值说明:

| 参数 | 类型 | 说明 |
|---|---|---|
| code | number | SDK外层code |
| message | string | SDK外层message |
| data | HashMap<string, string> | SDK外层data |
| innerCode | number | SDK内层code |
| innerDesc | string | SDK内层message |

# 2.预取号

使用场景

●

建议在执行一键登录的方法前,提前一段时间调用此方法,此调用将有助于提高拉起授权页的速度

和成功率

●

不建议调用后立即调用拉起授权页方法(此方法是异步)

●

此方法需要1~2s的时间取得临时凭证,因此也不建议和拉起授权页方法一起串行调用

●

不建议频繁的多次调用和在拉起授权页后调用

●

建议在判断当前用户属于未登录状态时使用,已登录状态用户请不要调用该方法

接口作用

电信、联通、移动预取号 :初始化成功后,如果当前为电信/联通/移动,将调用预取号,可以提前获知当

前用户的手机网络环境是否符合一键登录的使用条件,成功后将得到用于一键登录使用的临时凭证,默

认的凭证有效期60min(三大运营商一致)。

请求示例代码

```
static asyncpreGetPhoneNumber(): Promise<CLResult>
1
```

5

```
letresult: CLResult=awaitCLSDKManager.preGetPhoneNumber()
1
```

返回值说明:

| 参数 | 类型 | 说明 |
|---|---|---|
| code | number | SDK外层code |
| message | string | SDK外层message |
| data | HashMap<string, string> | SDK外层data |
| innerCode | number | SDK内层code |
| innerDesc | string | SDK内层message |

# 3.拉起授权页

使用场景

●

用户进行一键登录操作时,调用一键登录方法,如果初始化成功,SDK将会拉起授权页面,用户授

权后,SDK将返回取号 token给到应用客户端。

●

可以在多处调用

●

需在调用预初始化方法之后调用

一键登录逻辑说明

●

存在调用预初始化时获取的临时凭证,调用一键登录方法将立即拉起授权页面

●

let pgResult: CLResult = await CLSDKManager.quickAuthLoginWithConfigure(): pgResult获

取拉起授权页成功或者失败的结果

●

oneKeyLoginListener:一键登录监听,拉起授权页成功后的后续操作回调,包括点击SDK内置的

(非外部自定义)取消登录按钮,以及点击本机号码一键登录的回调。点击授权页自定义按钮不触发此

回调

●

不存在临时凭证或临时凭证过期时(临时凭证有效期电信60min、联通60min、移动60min),调用一

键登录方法,将有一个很短的时延,待取号成功后拉起授权页面

●

取号失败时,返回失败

在预取号成功后调用,预取号失败不建议调用。调用拉起授权页方法后将会调起运营商授权页面。该方

法会拉起登录界面,已登录状态请勿调用。

6

请求示例代码

```
static asyncquickAuthLoginWithConfigure(clUIConfigure: CLUIConfigure,
oneKeyLoginListener: (result: CLResult) =>void, isReplace?: boolean):
Promise<CLResult>
letconfig=newCLUIConfigure()
letpgResult: CLResult=
awaitCLSDKManager.quickAuthLoginWithConfigure(config, async (result: CL
Result) => {
//点击一键登录结果
  })
//返回拉起授权页结果Promise<CLResult>
letmessage='拉起授权页 : code:'+pgResult.code+' msg:'+pgResult.mes
sage+' innerCode:'+pgResult.innerCode
+' innerMsg:'+pgResult.innerDesc
HiLogUtils.info(message)
// 窗口模式配置
config.windowMode=true
letdialogViewController=newCustomDialogController({
builder:(awaitconfig.getAuthBuilder()).builder,
maskColor:Color.Transparent,
width:'100%',
height:'60%',
offset: { dx:0,dy:'5%' },
alignment:DialogAlignment.Bottom,
   })
config.dialogViewController=dialogViewController
```

参数说明:

| 参数 | 类型 | 说明 |
|---|---|---|
| clUIConfigure | CLUIConfigure | 授权页配置 |
| oneKeyLoginListener | (result: CLResult) => void | 一键登录回调 |
| isReplace | boolean | 设置是否使用 router replace 方式拉起授权页。true 为 replace, false 为 push,默认 为 false。 |

7

返回值说明:

| 参数 | 类型 | 说明 |
|---|---|---|
| code | number | SDK外层code |
| message | string | SDK外层message |
| data | HashMap<string, string> | SDK外层data |
| innerCode | number | SDK内层code |
| innerDesc | string | SDK内层message |

●

用户取消登录(授权页点击返回) 【处理建议:若无特殊需求可不做处理】

●

用户选择其他方式登录(点击授权页自带的其他方式登录): 【处理建议:可根据实际情况跳转其他登

录方式】

●

其他错误【处理建议:使用通道失败,可根据实际情况跳转其他登录方式】

# 4.关闭授权页

建议在置换手机号成功后销毁授权页。

关闭授权页时机

a.SDK拉起授权页方法直接回调失败时

b.置换手机号有返回结果时

授权页销毁

销毁授权页界面

```
static closeAuthLoginPage()
CLSDKManager.closeAuthLoginPage()
```

# 5.其他API

### a.设置 log 开关

控制台日志输出控制(true:开启,false:关闭,默认false)

8

```
CLSDKManager.printConsoleEnable(true)
1
```

# 三.授权界面修改

# 1.设计规范

注意:

1、开发者不得通过任何技术手段,破解授权页,或将授权页面的号码栏、隐私栏、品牌露出内容隐藏、

覆盖。

2、登录按钮文字描述必须包含“登录”或“注册”等文字,不得诱导用户授权。

3、对于接入SDK并上线的应用,我方会对上线的应用授权页面做审查,如果有出现未按要求弹出或设

计授权页面的,将关闭应用的认证取号服务。

# 2.页面可调整属性、布局

9

**注:授权页基本控件布局通过布局对象设置,布局定位更加方便快捷,

10

```
export classCLUIConfigure {
// 设置导航栏、状态栏属性
systemBarProperties?: window.SystemBarProperties
// 设置服务条款标题字体大小
navTextSize?: number
// 设置服务条款标题字体颜色
navTextColor?: ResourceColor
// 设置服务条款标题颜色
navColor?: ResourceColor
// 设置服务条款标题栏自定义view
clauseComponent?: () =>void
// 设置授权页布局自定义View
loginPageComponent?: () =>void
// 设置授权页灰度值,范围0-1
loginPageGrayScale?: number
// 设置号码栏字体大小
numberSize?: number
// 设置号码栏字体字体粗细
numberIsBold?: boolean
// 设置手机号码字体颜色
numberColor?: ResourceColor
// 设置号码栏偏移
numberMargin?: Margin
// 设置号码栏相对布局偏移规则
numberAlignRuleOption?: AlignRuleOption
// 设置登录按钮宽度
loginBtnWidth?: Length
// 设置登录按钮高度
loginBtnHeight?: Length
// 设置登录按钮文本内容
loginBtnText?: string
// 设置授权登录文本字体大小
loginBtnTextSize?: number
// 设置授权登录按钮字体颜色
loginBtnTextColor?: ResourceColor
// 设置登录按钮边缘边距
loginBtnMargin?: Margin
// 设置登录按钮相对布局偏移规则
loginBtnAlignRuleOption?: AlignRuleOption
// 设置登录按钮背景图片
loginBtnImgPath?: ResourceStr
// 设置登录按钮背景颜色
loginBtnColor?: ResourceColor
// 设置登录按钮是否显示按压效果
loginBtnStateEffect?: boolean
// 设置登录按钮圆角
loginBtnBorderRadius?: Length|BorderRadiuses|LocalizedBorderRadiuses
```

11

```
// 设置登录按钮点击监听事件
loginClickListener?: CLLoginClickListener
// 设置隐私条款的协议文本,自定义条款,自定义条款链接、字体颜色
clauses?: PrivacyEntity[]
// 设置隐私条款偏移边距
clauseMargin?: Margin
// 设置隐私条款相对布局偏移规则
clauseAlignRuleOption?: AlignRuleOption
// 设置隐私条款勾选框宽度
checkBoxWidth?: Length
// 设置隐私条款勾选框高度
checkBoxHeight?: Length
// 设置隐私条款勾选框勾选状态
clauseState?: boolean
// 设置隐私条款勾选框偏移边距
checkBoxMargin?: Margin
// 设置勾选框类型(圆角矩形/圆形)
checkBoxShape?: CheckBoxShape
// 设置隐私条款勾选框相对布局偏移规则
checkBoxAlignRuleOption?: AlignRuleOption
// 设置 checkbox 勾选和未勾选图片(需同时设置checkedImage、unCheckedImage)
checkedImage?: ResourceStr
unCheckedImage?: ResourceStr
// 设置授权页勾选框和登录按钮的监听事件
checkBoxListener?: CLCheckBoxListener
// 设置授权页勾选框是否勾选的监听事件
checkedChangeListener?: CLCheckedChangeListener
// 设置未勾选提示的自定义提示文案。不设置则无提示。
checkTipText?: string
// 设置勾选颜色
checkedColor?: ResourceColor
// 设置协议页标题栏margin.top,范围为 0-99
clauseNavMarginTop?: number
// 设置默认元素语言,0.中文简体 1.中文繁体 2.英文
appLanguageType?: number
// 设置授权页返回键监听事件
backPressedListener?: CLBackPressedListener
```

// 设置授权按钮监听事件,入参回调CLAuthLoginListener,用户点击登录按钮时如果未勾

选协议,

```
// 触发CLAuthLoginListener的 (context: UIContext,callBack:CLAuthLoginCall
```

Back) 方法。可以实现二次弹窗确认的功能

```
authLoginListener?: CLAuthLoginListener
//设置当前页面的UIContext
uiContext?:UIContext
// 设置窗口模式,默认false
windowMode?:boolean
// 窗口模式下必传
dialogViewController?:CustomDialogController
```

12

```
}
94
```

13

```
letconfig=newCLUIConfigure()
letsystemBarProperties: window.SystemBarProperties= {
statusBarColor: '#ff00ff',
navigationBarColor: '#00ff00',
statusBarContentColor: '#ffffff',
navigationBarContentColor: '#00ffff'
}
config.systemBarProperties=systemBarProperties
config.navTextColor=Color.White
config.navColor=Color.Pink
config.appLanguageType=1
// 登录按钮点击监听事件(勾选后进入正常的授权登录)
config.loginClickListener= ({
onLoginClickStart(context: UIContext) {
HiLogUtils.info("loginClickListener:开始登录授权")
  }
, onLoginClickComplete(context: UIContext) {
HiLogUtils.info("loginClickListener:登录授权结束")
  }
})
config.loginPageComponent=authPageComponent
// 设置授权页返回键监听事件
config.backPressedListener= ({
async onBackPressed() {
HiLogUtils.info("backPressedListener:返回")
letsystemBarProperties: window.SystemBarProperties= {
statusBarColor: '#ffffff'
    }
letwindowClass: window.Window=awaitwindow.getLastWindow(getContex
t(this))
awaitwindowClass.setWindowSystemBarProperties(systemBarProperties)
  }
})
// 授权按钮监听 1
config.authLoginListener= ({
onAuthLoginListener(context: UIContext, callBack: CLAuthLoginCallBack)
{
promptAction.showDialog({
message: '是否登录授权',
buttons: [
        {
text: '确定',
color: '#000000'
        },
```

14

```
        {
text: '取消',
color: '#000000'
        }
      ],
    })
      .then(data=> {
// 授权回调,通过onAuthLoginCallBack(b:boolean)决定是否继续登录流程。
```

可以实现二次弹窗确认的功能

```
if (data.index==0) {
CLSDKManager.clearScripCache()
callBack.onAuthLoginCallBack(true)
        } else {
callBack.onAuthLoginCallBack(false)
        }
      })
  }
})
// 设置授权页勾选框和登录按钮的监听事件
config.checkBoxListener= ({
onLoginClick() {
HiLogUtils.info("checkBoxListener:未勾选时点击一键登录回调")
  }
})
// 设置授权页勾选框是否勾选的监听事件
config.checkedChangeListener= ({
onCheckedChanged(b) {
HiLogUtils.info("checkedChangeListener:勾选状态改变:"+b)
  }
})
config.checkBoxShape=CheckBoxShape.ROUNDED_SQUARE
config.checkTipText="没选中- -- ~"
config.clauses= [{
text: "同意",
isProtocol: false,
fontColor: Color.Black,
fontSize: 16,
fontWeight: FontWeight.Bold,
},
  {
text: "《**CLAUSE**》",
isProtocol: true,
fontColor: Color.Red,
fontSize: 16,
fontWeight: FontWeight.Bold,
  },
```

15

```
  {
text: "、",
isProtocol: false,
fontColor: Color.Black,
fontSize: 16,
fontWeight: FontWeight.Bold
  },
  {
text: "自定义协议1",
isProtocol: true,
fontColor: Color.Red,
fontSize: 16,
fontWeight: FontWeight.Bold,
url: "https://www.baidu.com/"
  },
  {
text: "、",
isProtocol: false,
fontColor: Color.Black,
fontSize: 16,
fontWeight: FontWeight.Bold
  },
  {
text: "自定义协议2",
isProtocol: true,
fontColor: Color.Red,
fontSize: 16,
fontWeight: FontWeight.Bold,
url: "https://www.sina.com/"
  },
  {
text: "并使用本机号码校验",
isProtocol: false,
fontColor: Color.Black,
fontSize: 16,
fontWeight: FontWeight.Bold
  }]
```

状态栏配置:

| 参数 | 类型 | 说明 |
|---|---|---|
| systemBarProperties | window.SystemBarProperties | 设置导航栏、状态栏属性 |

服务条款配置:

| 参数 | 类型 | 说明 |
|---|---|---|
|  |  |  |

|  |  |  |
|---|---|---|
| navTextSize | number | 设置服务条款标题字体大小 |
| navTextColor | ResourceColor | 设置服务条款标题字体颜色 |
| navColor | ResourceColor | 设置服务条款标题颜色 |
| clauseComponent | () => void | 设置服务条款标题栏自定义 view |

授权页布局:

| 参数 | 类型 | 说明 |
|---|---|---|
| loginPageComponent | () => void | 设置授权页布局自定义View |
| loginPageGrayScale | number | 设置授权页灰度值,范围0-1 |

授权页号码配置:

| 参数 | 类型 | 说明 |
|---|---|---|
| numberSize | number | 设置号码栏字体大小、字体粗细 |
| numberColor | ResourceColor | 设置手机号码字体颜色 |
| numberMargin | Margin | 设置号码栏偏移 |
| numberAlignRuleOption | AlignRuleOption | 设置号码栏相对布局偏移规则 |
| numberIsBold | boolean | 设置号码栏字体字体粗细 |

授权页登录按钮配置:

| 参数 | 类型 | 说明 |
|---|---|---|
| loginBtnWidth | Length | 设置登录按钮宽度 |
| loginBtnHeight | Length | 设置登录按钮高度 |
| loginBtnText | string | 设置登录按钮文本内容 |
| loginBtnTextSize | number | 设置授权登录文本字体大小 |
| loginBtnTextColor | ResourceColor | 设置授权登录按钮字体颜色 |
| loginBtnMargin | Margin | 设置登录按钮边缘边距 |
|  |  |  |

|  |  |  |
|---|---|---|
| loginBtnAlignRuleOption | AlignRuleOption | 设置登录按钮相对布局偏移规则 |
| loginBtnImgPath | ResourceStr | 设置登录按钮背景图片 |
| loginBtnColor | ResourceColor | 设置登录按钮背景颜色 |
| loginClickListener | CLLoginClickListener | 设置登录按钮点击监听事件 |
| loginBtnBorderRadius | Length | BorderRadiuses |
| loginBtnStateEffect | boolean | 设置是否显示按压效果:false无 按压效果;true或空有按压效果 |

授权页隐私条款配置:

| 参数 | 类型 | 说明 |
|---|---|---|
| clauses | Array | 设置隐私条款的协议文本,自定 义条款,自定义条款链接、字体 颜色 |
| clauseMargin | Margin | 设置隐私条款偏移边距 |
| clauseAlignRuleOption | AlignRuleOption | 设置隐私条款相对布局偏移规则 |
| clauseNavMarginTop | number | 设置协议页标题栏margin.top, 范围为 0-99 |
| checkBoxWidth | Length | 设置隐私条款勾选框宽度 |
| checkBoxHeight | Length | 设置隐私条款勾选框高度 |
| clauseState | boolean | 设置隐私条款勾选框勾选状态 |
| checkBoxMargin | Margin | 设置隐私条款勾选框偏移边距 |
| checkBoxShape | CheckBoxShape | 设置勾选框类型(圆角矩形/圆 形) |
| checkBoxAlignRuleOption | AlignRuleOption | 设置隐私条款勾选框相对布局偏 移规则 |
| checkBoxListener | CLCheckBoxListener | 设置授权页勾选框和登录按钮的 监听事件 |

|  |  |  |
|---|---|---|
| checkedChangeListener | CLCheckedChangeListener | 设置授权页勾选框是否勾选的监 听事件 |
| checkTipText | string | 设置未勾选提示的自定义提示文 案。不设置则无提示。 |
| checkedColor | ResourceColor | 设置勾选颜色 |
| checkedImage | ResourceStr | 设置 checkbox 勾选图片(需同 时设置checkedImage、 unCheckedImage) |
| unCheckedImage | ResourceStr | 设置 checkbox 未勾选图片(需 同时设置checkedImage、 unCheckedImage) |

授权页语言配置:

| 参数 | 类型 | 说明 |
|---|---|---|
| appLanguageType | number | 设置默认元素语言,0.中文简体 1.中文繁体 2.英文 |

授权页拉返回监听:

| 参数 | 类型 | 说明 |
|---|---|---|
| backPressedListener | CLBackPressedListener | 设置授权页返回键监听事件 |

授权按钮布局:

| 参数 | 类型 | 说明 |
|---|---|---|

|  |  |  |
|---|---|---|
| authLoginListener | CLAuthLoginListener | 设置授权按钮监听事件,入参回 调CLAuthLoginListener,用户 点击 登录按钮时如果未勾选协 议, 触发CLAuthLoginListener的 (context: UIContext,callBack:CLAuthLo ginCallBack) 方法。可以实现 二次弹窗确认的功能。 |

# 四.本机认证

# 1.初始化

同“二、SDK使用说明-->初始化”

# 2.本机认证

接口作用

本机号码校验 : 验证指定手机号与本机SIM卡是否一致。(此接口仅返回token,手机号验证需调用服务

端)

使用场景

●

在初始化接口后调用

●

输入手机号后进行校验

请求示例代码

```
static asyncmobileCheckWithLocalPhoneNumberComplete(): Promise<CLResult>
1
letresult: CLResult=awaitCLSDKManager.mobileCheckWithLocalPhoneNumberC
omplete()
1
```

返回值说明:

| 参数 | 类型 | 说明 |
|---|---|---|

20

|  |  |  |
|---|---|---|
| code | number | SDK外层code |
| message | string | SDK外层message |
| data | HashMap<string, string> | SDK外层data |
| innerCode | number | SDK内层code |
| innerDesc | string | SDK内层message |

# 3.手机号后台服务端校验

当一键登录外层 code 为 2000 时,会获取到检验手机号所需的 token。请参考「服务端」文档来实现

检验手机号码的步骤。

# 五.返回码对照

# 外层错误码

同一外层码可能对应不同的内层码

| 外层返回码 | 返回码描述 |
|---|---|
| 1000 | 初始化、预取号、获取token成功码,解析 result,可得到网络请求参数 |
| 1001 | SDK初始化失败 |
| 1010 | 初始化出错 |
| 1011 | 用户取消免密登录(点击返回按钮) |
| 1020 | 预取号出错 |
| 1023 | 预取号/取号失败 |
| 1003 | 拉起授权页失败/一键登录失败/获取token失败 |
| 1030 | 拉起授权页出错 |
| 1032 | 账户禁用 |
|  |  |

21

|  |  |
|---|---|
|  |  |
| 2000 | 本机校验:获取token成功 |
| 2003 | 本机校验:联通获取token失败 |
| 2004 | 本机校验:电信获取token失败 |
| 2005 | 本机校验:移动获取token失败 |
| 2023 | 本机校验:超时 |
| 2010 | 本机号认证获取token出错 |
| 其他 | 其他错误 |

# 内层错误码

联通返回码

| 返回码 | 状态码 | 报错信息 |
|---|---|---|
| 510000 | 请求超时 |  |
| 510002 | 服务响应解析异常 |  |
| 510003 | 无法切换至数据网络 |  |
| 510004 | 数据网络未开启 |  |
| 510005 | 网络判断异常 |  |
| 510010 | 状态码是 200,302 之 外的值 |  |
| 510011 | Https 通讯抛出异常 |  |
| 510012 | 200 但 body 为空 |  |
| 510013 | 跳转地址错误 |  |
| 510021 | 初始化失败或者操作频繁 |  |
| 510023 | 取号进行中,请勿重复调用 |  |
| 510024 | Http 通讯抛出异常 |  |
| -2 | unknow province! |  |
|  |  |  |
|  |  | 22 |

电信返回码

| 返回码 | 返回描述 |
|---|---|
| 0 | 请求成功 |
| -64 | permission-denied(无权限访问) |
| -65 | API-request-rates-Exceed-Limitations(调用 接口超限) |
| -10001 | 取号失败 |
| -10002 | 参数错误 |
| -10003 | 解密失败 |
| -10004 | ip受限 |
| -10005 | 异网取号回调参数异常 |
| -10006 | Mdn取号失败,且属于电信网络 |
| -10007 | 重定向到异网取号 |
| -10008 | 超过预设取号阈值 |
| -10009 | 时间戳过期 |
| -20005 | sign-invalid(签名错误) |
| -20006 | 应用不存在 |
| -20007 | 公钥数据不存在 |
| -20100 | 内部解析错误 |
| -20102 | 加密参数解析失败 |
| -30001 | 时间戳非法 |
| -30003 | topClass失效,请查看5.3+5.4常见问题。 |
| 51002 | 参数为空 |
| 51114 | 无法获取手机号数据 |

23

|  |  |
|---|---|
| 80000 | 请求超时 |
| 80001 | 请求网络异常 |
| 80002 | 响应码错误 |
| 80003 | 无网络连接 |
| 80004 | 移动网络未开启 |
| 80006 | 域名解析异常 |
| 80007 | IO异常 |
| 80008 | No route to host |
| 80009 | nodename nor servname provided, or not known |
| 80010 | Socket closed by remote peer |
| 80100 | 登录结果为空 |
| 80101 | 登录结果异常 |
| 80102 | 预登录异常 |
| 80103 | SDK未初始化 |
| 80104 | 未调用预登录接口 |
| 80200 | 用户关闭界面 |
| 80201 | 其他登录方式 |
| 80800 | WIFI切换异常 |
| 80801 | WIFI切换超时 |
| 80999 | 未预期的Crash问题 |
|  |  |

移动返回码

| 返回码 | 返回码描述 |
|---|---|
| 103000 | 成功 |

24

|  |  |
|---|---|
| 102101 | 无网络 |
| 102102 | 网络异常 |
| 102103 | 未开启数据网络 |
| 102203 | 输入参数错误 |
| 102223 | 数据解析异常,一般是卡欠费 |
| 102508 | 数据网络切换失败。 |
| 103101 | 请求签名错误(若发生在客户端,可能是appkey 传错,可检查是否跟appsecret弄混,或者有空 格。若发生在服务端接口,需要检查验签方式是 MD5还是RSA,如 果是 MD5,则排查signType 字段,若为appsecret,需确认是否误用了 appkey 生签。如果 是RSA,需要检查使用的私 钥跟报备的公钥是否对应和报文拼接是 否符合文 档要求。) |
| 103102 | 包签名错误(社区填写的appid和对应的包名包签 名必须一致) |
| 103111 | 错误的运营商请求(可能是用户正在使用代理或者 运营商判断失败导致) |
| 103119 | appid不存在(检查传的appid是否正确或是否有空 格) |
| 103211 | 其他错误,(常见于报文格式不对,先请检查是否 符合这三个要求: a、json形 式的报 文交互必须 是标准的json格式; b、发送时请设置content type为 application/json; c、参数类型都是 String。如有需要请联系移动认证开发) |
| 103412 | 无效的请求(1.加密方式错误; 2.非json格式; 3.空 请求等) |
| 103414 | 参数校验异常 |
| 103511 | 服务器ip白名单校验失败 |
| 103811 | token为 空 |

25

|  |  |
|---|---|
| 103902 | scrip失效(短时间内重复登录) |
| 103911 | token请求过于频繁,10分钟内获取token且未使 用的数量不超过30个 |
| 104201 | token已失效或不存在(重复校验或失效) |
| 105001 | 联通取号失败 |
| 105002 | 移动取号失败(一般是物联网卡) |
| 105003 | 电信取号失败 |
| 105012 | 不支持电信取号 |
| 105013 | 不支持联通取号 |
| 105018 | token权限不足(使用了本机号码校验的token获取 号码) |
| 105019 | 应用未授权(未在互联网能力开放平台勾选能力) |
| 105021 | 当天已达取号限额 |
| 105302 | appid不在白名单 |
| 105312 | 移动能力余量不足(体验版到期或套餐用完) |
| 105422 | 电信能力余量不足(体验版到期或套餐用完) |
| 105423 | 联通能力余量不足(体验版到期或套餐用完) |
| 105313 | 非法请求 |
| 105315 | 不支持的运营商类型 |
| 105317 | 受限用户 |
| 200002 | 用户未安装sim卡 |
| 200010 | 无法识别sim卡或没有sim卡 |
| 200005 | 用户未授权(READ PHONE STATE) _ _ |
| 200020 | 授权页关闭 |
| 200021 | 数据解析异常(一般是卡欠费) |
| 200022 | 无网络 |

26

|  |  |
|---|---|
| 200023 | 请求超时 |
| 200024 | 数据网络切换失败 |
| 200025 | 其他错误(socket、系统未授权数据蜂窝权限等, 如需要协助,请联系移动认证开发) |
| 200026 | 输入参数错误 |
| 200027 | 未开启数据网络或网络不稳定 |
| 200028 | 网络异常 |
| 200038 | 异网取号网络请求失败 |
| 200039 | 异网取号网关取号失败 |
| 200040 | UI资源加载异常 |
| 200050 | EOF异常 |
| 200072 | CA根证书校验失败,证书校验异常 |
| 200080 | 本机号码校验仅支持移动手机号 |
| 200082 | 服务器繁忙,请稍后重试 |
| 200087 | 授权页成功调起 |
|  |  |

# 六.常见问题

1.code:1001 msg:初始化请求异常

一般是初始化网络请求问题,建议检查网络是否正常

2.code:10029 msg:用户不存在

appid参数错误

3.code:19 msg:包名校验不通过

bundleName错误

27

28
