# **天翼账号认证** SDK **接入指南** 

SDK API V0.2.6 

天翼数字生活科技有限公司 2026 年 04 月 27 日 

|版本历史:|
|---|

|版本号|作者|时间|内容|
|---|---|---|---|
|0.1.0|21cn|2024.09.12|本版本仅供接入方前期调试使用 1、版本功能实现;|
|0.2.0|21cn|2024.10.31|本版本仅供接入方前期调试使用 1、修复ASAN 扫描问题;|
|0.2.1|21cn|2024.12.16|本版本仅供接入方前期调试使用 1、新增自定义导航栏配置; 2、修复authCode 校验失败问题;|
|0.2.2|21cn|2025.01.21|本版本仅供接入方前期调试使用 1.优化蜂窝网络激活延迟导致取号失败问 题; 2.修复首次取号失败问题;|
|0.2.3|21cn|2025.05.16|本版本仅供接入方前期调试使用 1.完善蜂窝网络激活流程; 2. 适配鸿蒙系统和最新编译环境。 3.优化自定义协议功能; 4.优化导航栏嵌入问题;|
|0.2.4|21cn|2025.12.11|本版本仅供接入方前期调试使用 1.新增mini 弹框类型及其配置项;|
|0.2.5|21cn|2026.02.02|1、优化控件锚点,增加可控制空间 2、协议页选择按钮增加对外配置项 3、协议页文字增加对外配置项 4、增加关闭全屏、mini 框方法 5、沉浸式闪动问题优化 6、登录按钮配置项增加背景图片 7、协议按钮为勾选时弹框页面对外增加文 字可配置项 8、部分功能兼容api16 9、登录按钮长按的高亮效果对外配置 10、5个自定义按钮的backgroundImage的|

地址:中国广州市天河区龙口中路211 号华天国际广场首层 

PAGE 1 

总机:+86 020 85115000 传真:+86 020 85115111 邮编:510630 HTTP://WWW.21CN.COM 

||||对齐方式对外配置|
|---|---|---|---|
||||11、协议页导航栏居中|
|0.2.6|21cn|2026.04.27|1. 优化协议文字对齐格式;|
||||2. 新增预留按钮文字颜色属性;|

地址:中国广州市天河区龙口中路211 号华天国际广场首层 总机:+86 020 85115000 传真:+86 020 85115111 邮编:510630 HTTP://WWW.21CN.COM 

PAGE 2 

#### 目录 

|1. 概述................................................................................................................................................5|
|---|
|1.1. 接入前必读(重要)........................................................................................................ 5|
|1.2. 快速接入指南.................................................................................................................... 6|
|1.3. 登录流程说明.................................................................................................................... 9|
|2. HarmonyOS NEXT 接入指南......................................................................................................... 9|
|2.1. 接入说明............................................................................................................................ 9|
|2.2. 导入har 包......................................................................................................................... 9|
|2.3. 配置权限清单.................................................................................................................. 10|
|2.4. SDK 接口调用说明...........................................................................................................10|
|2.4.1. 初始化................................................................................................................... 10|
|2.4.2. 预取号接口........................................................................................................... 11|
|2.4.3. 打开登录界面....................................................................................................... 14|
|3. 附录及常见问题......................................................................................................................... 22|
|3.1. SDK 错误码定义...............................................................................................................22|

地址:中国广州市天河区龙口中路211 号华天国际广场首层 

PAGE 3 

总机:+86 020 85115000 传真:+86 020 85115111 邮编:510630 HTTP://WWW.21CN.COM 

地址:中国广州市天河区龙口中路211 号华天国际广场首层 

PAGE 4 

总机:+86 020 85115000 传真:+86 020 85115111 

邮编:510630 HTTP://WWW.21CN.COM 

## 1. 概述 

### 1.1. 接入前必读(重要) 

为了确保用户在登录过程中将手机号码信息授权给接入方使用的知情权,天翼账号 登录认证需要接入方满足如下要求: 

(1)接入方在调用登录认证方法前,必须显示出授权页面,授权页面需明确告知 用户操作会将用户本机号码信息授权给应用;(天翼账号服务与隐私协议url 地址: https://e.189.cn/sdk/agreement/detail.do?hidetop=true) 

(2)接入方需展示“天翼账号”品牌露出,不得通过任何技术手段,将授权页面 的隐私栏、品牌露出内容隐藏、覆盖; 

(3)接入方上线前需要将授权页面提交给我方进行审核,审核通过后才可正式开 放登录功能调用使用量。 

若有出现未按要求设计授权页面的行为或有非正常调用行为,为了保护用户的隐私 安全,我方有权将接入方应用的登录功能下线。 

如下是天翼账号标准页面的设计规范,供合作方参考; 

为满足以上要求,接入资料中未包含相应的导入包,需合作方将如下信息提交给天翼账 号进行配置,我方即可提供导入包: 

地址:中国广州市天河区龙口中路211 号华天国际广场首层 

PAGE 5 

总机:+86 020 85115000 传真:+86 020 85115111 

邮编:510630 HTTP://WWW.21CN.COM 

一个APPID 对应一个应用,故需要提供如下信息,用于校验该APPID 对应的应用 请求: 

Android 端:APPID、包名packagename、包签名(签名证书的MD5 值) 

iOS 端:APPID、bundleID(可配置测试和正式的bundleID) 

HarmonyOS 端:APPID、bundleName(可配置测试和正式的bundleName) 

### 1.2. 快速接入指南 

(1)访问快速接入网址(http://id.189.cn/convention/developer?ac=null),合作方业务联 系人在4G 环境下打开微信,扫描网页内二维码,免密登录开放平台。 

(2)完成表格内容填写,点击“提交申请”,等待管理员审核,审核通过后系统将自 动向表格中填写的邮箱发送邮件通知。 

地址:中国广州市天河区龙口中路211 号华天国际广场首层 

PAGE 6 

总机:+86 020 85115000 

传真:+86 020 85115111 

邮编:510630 HTTP://WWW.21CN.COM 

(3)访问天翼账号开放平台的“能力商店” 

(http://id.189.cn/selfApply/abilityShop/homePage),自助申请所需的能力,等待管理员审核, 审核通过后系统将自动向业务联系人邮箱发送邮件通知。 

地址:中国广州市天河区龙口中路211 号华天国际广场首层 

PAGE 7 

总机:+86 020 85115000 传真:+86 020 85115111 邮编:510630 HTTP://WWW.21CN.COM 

(4)访问天翼账号开放平台的“管理中心”(http://id.189.cn/manageCenter/app/appList), 可查询接口调用所需参数,配置服务器IP 白名单(服务端接口有IP 鉴权),若服务端接口 不是采用IP 鉴权的方式,可忽略此步。 

地址:中国广州市天河区龙口中路211 号华天国际广场首层 

PAGE 8 

总机:+86 020 85115000 传真:+86 020 85115111 邮编:510630 HTTP://WWW.21CN.COM 

### 1.3. 登录流程说明 

### 接入说明: 

1. SDK 预登录接口 

2. SDK 内部处理 

3. 合作方处理 

4. 合作方服务端调用天翼账号授权接口 

## 2. HarmonyOS NEXT 接入指南 

### 2.1. 接入说明 

- (1) 接入前请先确认 

   - A. 已申请AppID、AppSecret。 

若无,请按1.2 的指引申请 

### 2.2. 导入 **har** 包 

- (1) 参考鸿蒙官网推荐方法导入 har 包 

地址:中国广州市天河区龙口中路211 号华天国际广场首层 

总机:+86 020 85115000 传真:+86 020 85115111 

PAGE 9 

邮编:510630 HTTP://WWW.21CN.COM 

### 2.3. 配置权限清单 

(1) 在module.json5 配置权限 

"requestPermissions" :[ 

{ 

"name" : "ohos.permission.INTERNET" , 

}, { 

"name" : "ohos.permission.GET_NETWORK_INFO" 

} 

(2)配置权限说明 

|权限|用途|
|---|---|
|ohos.permission.INTERNET|允许应用程序联网|
|ohos.permission.GET_NETWORK_INFO|允许程序访问网络状态信息|

### 2.4. **SDK** 接口调用说明 

#### 2.4.1. 初始化 

【接口说明】 

在调用该接口前,需先做SDK 初始化,调用后再调用预取号 

【调用示例】 

onWindowStageCreate(windowStage: window.WindowStage): void { 

BusinessAuth.init(getContext( **this** ), "xxx", "xxx") 

} 

#### 【请求参数】 

|参数名|类型|必填|说明|
|---|---|---|---|

地址:中国广州市天河区龙口中路211 号华天国际广场首层 

PAGE 10 

总机:+86 020 85115000 传真:+86 020 85115111 

邮编:510630 HTTP://WWW.21CN.COM 

|Ctx|Context|是|上下文|
|---|---|---|---|
|Appid|string|是|平台申请的Appid|
|APPsecret|string|是|平台申请的appSecret|

#### 2.4.2. 预取号接口 

#### 【接口说明】 

在调用该接口前,建议先做本地预判断处理,符合条件再调用预登录接口。预登录接口 可获取脱敏手机号、accessCode 等信息,其中脱敏手机号可用于登录界面的展示,accessCode 默认有效期为60 分钟。 

#### 【调用示例】 

**import** { BusinessAuth,AuthResultListener,AuthResult,CtSetting } **from** 'ctaccount' 

CtAuth.g **let** setting: CtSetting = **new** CtSetting() setting.setConnTimeout(6000) setting.setReadTimeout(6000) 

BusinessAuth.requestPreLogin(setting, **new** AuthResultAdapter()) 

// 创建一个AuthResultListener 的实现类 

**class** AuthResultAdapter **implements** AuthResultListener { 

onResult(result: AuthResult): void { 

- **if** (result != **null** ) { 

**const** code: string = result.code; 

**const** accessCode: string = result.accessCode; 

**const** msg: string = result.msg; 

**const** expiredTime: string = result.expiredTime; 

**const** operatorType: string = result.operatorType; 

地址:中国广州市天河区龙口中路211 号华天国际广场首层 总机:+86 020 85115000 传真:+86 020 85115111 

|PAGE 11|
|---|

邮编:510630 HTTP://WWW.21CN.COM 

**const** number: string = result.number; 

**const** reqID: string = result.reqID; console.log("DebugLog:" + 'code:' + code + '&msg:' + msg + '&accessCode:' + accessCode + "&expiredTime:" + 

expiredTime + "&number:" + number + "&operatorType:" + operatorType) 

AlertDialog.show( { title: '提示', message: 'code:' + code + '&msg:' + msg + '&accessCode:' + accessCode + "&expiredTime:" + 

expiredTime + "&number:" + number + "&operatorType:" + operatorType + "&reqID:" + reqID, autoCancel: **true** , alignment: DialogAlignment.Center, gridCount: 3, confirm: { value: '确认', action: () => { } } } ) } } } 

【请求参数】 

|参数名|类型|必填|说明|
|---|---|---|---|

PAGE 12 

地址:中国广州市天河区龙口中路211 号华天国际广场首层 总机:+86 020 85115000 传真:+86 020 85115111 邮编:510630 HTTP://WWW.21CN.COM 

|Ct Listener|CtSetting AuthResultListener|是 是|请求时间控制器 平台申请的appSecret|
|---|---|---|---|

#### 【响应参数】 

返回结果result 的json 格式说明: 

|参数名|类型|字段含义|说明|
|---|---|---|---|
|result|AuthResult|请求结果|请求结果|
|result 格式说明:||||
|参数名|类型|字段含义|说明|
|code|String|结果码|返回参数结果码,0表示成功, 详细参考错误码定义(3.1)|
|Msg|String|结果信息|返回参数结果信息 详细参考错误码定义(3.1)|
|accessCode|String|授权码|天翼账号授权码,默认时效性60分钟|
|operatorType|String|运营商标 识|CT电信,CU联通,CM移动,UN其他|
|expiredTime|int|code失效 时间|表示该accessCode 的有效时间,时间单 位为s|
|reqID|String|请求ID|当次请求ID,异常时进行排障使用|

地址:中国广州市天河区龙口中路211 号华天国际广场首层 总机:+86 020 85115000 传真:+86 020 85115111 邮编:510630 HTTP://WWW.21CN.COM 

PAGE 13 

#### 2.4.3. 打开登录界面 

#### 【接口说明】 

- 1.使用该接口前,必须先完成调用初始化和预登录接口。在预登录成功后,才调用该接 

- 口打开登录界面,用户点击一键登录按钮,将立即返回登录结果(无网络请求)。 

   - 2.如果无动态配置页面的需求,传入默认的config 即可。 

#### 【调用示例】 

**import** { AuthConfig, BusinessAuth, AuthResultListener, AuthResult, CtSetting, AuthEventResult, ProtocolModel} **from** 'ctaccount' 

//初始化登录界面配置模型 

**let** config: AuthConfig = **new** AuthConfig(); 

**let** config: AuthConfig = **new** AuthConfig(); config.logoResource = $r('app.media.homeLOGO'); config.btn5Hidden = Visibility.Hidden; config.navHidden = Visibility.Hidden; config.navBackBtnHidden = Visibility.Hidden; config.navBackgroundColor = '#007DFF'; 

//适配接入方沉浸式的情况 windowStage 从mainWindow 中获取 

config.windowStage = BusinessAuth.windowStage; 

config.isFullScreen = **false** ; 

//自定义协议 

**let** protocolModels = **new** ArrayList<ProtocolModel>(); **let** protocol = **new** ProtocolModel(); protocol.PAUrl = "协议地址"; " " protocol.partnerPAText = 《自定义协议 1》 ; protocol.partnerPANameColor = $r('app.color.common_blue_color'); ' ' protocol.paUrlTitle = 协议标题 1 ; protocolModels.add(protocol); 

**let** protocol2= **new** ProtocolModel(); protocol2.PAUrl = "协议地址"; " " protocol2.partnerPAText = 《自定义协议 2》 ; ' ' protocol2.paUrlTitle = 协议标题 2 ; 

地址:中国广州市天河区龙口中路211 号华天国际广场首层 总机:+86 020 85115000 传真:+86 020 85115111 邮编:510630 HTTP://WWW.21CN.COM 

PAGE 14 

protocol2.partnerPANameColor = $r('app.color.common_blue_color'); protocolModels.add(protocol2); config.protocolModels = protocolModels.convertToArray(); config.logoResource = $r('app.media.homeLOGO'); config.btn5Hidden = Visibility.Visible; 

//更多设置请参考 AuthConfig 

#### //打开登录页 

BusinessAuth.openAtuhHY(config, **new** AuthLoginResultAdapter()); 

//页面button 点击事件回调 

BusinessAuth.customOperationWithEventHandler((authEventResult:AuthEventResult)=>{ console.log("--------点击事件中断回调--------") console.log("--------点击的 view 是"+authEventResult.viewId+"--------") console.log("--------点击的 clickEvent 是"+authEventResult.clickEvent+"--------") 

**if** (authEventResult.viewId === "loginButton") 

//如果是登录按钮必须调用continueExecutionWithParams,登录流程才会继续; authEventResult.eventHandle?.continueExecutionWithParams( **false** ); 

}) 

// 创建一个AuthResultListener 的实现类 

**class** AuthLoginResultAdapter **implements** AuthResultListener { onResult(result: AuthResult): void { 

**if** (result != **null** ) { **const** code: string = result.code; **const** accessCode: string = result.accessCode; **const** msg: string = result.msg; **const** expiredTime: string = result.expiredTime; **const** operatorType: string = result.operatorType; **const** number: string = result.number; **const** reqID: string = result.reqID; console.log("DebugLog:" + 'code:' + code + '&msg:' + msg + '&accessCode:' + accessCode + "&expiredTime:" + expiredTime + "&number:" + number + "&operatorType:" + operatorType) 

|地址:中国广州市天河区龙口中路211 号华天国际广场首层|PAGE 15|
|---|---|
|总机:+86 020 85115000||
|传真:+86 020 85115111||
|邮编:510630 HTTP://WWW.21CN.COM||

AlertDialog.show( { title: '提示', 

message: 'code:' + code + '&msg:' + msg + '&accessCode:' + accessCode + "&expiredTime:" + 

expiredTime + "&number:" + number + "&operatorType:" + operatorType + "&reqID:" + reqID + "&authCode:" + result.authCode + "&gwAuth:" + result.gwAuth, autoCancel: **true** , alignment: DialogAlignment.Center, gridCount: 3, confirm: { value: '确认', action: () => { 

} } } ) 

} 

} 

} 

#### 【请求参数】 

|参数名|类型|必填|说明|
|---|---|---|---|
|config|AuthConfig|是|登录页面控件属性配置|
|authLisener|AuthResultListener|是|登录结果回调监听|

#### 【响应参数】 

#### 【响应参数】 

#### 返回结果result 的json 格式说明: 

|参数名|类型|字段含义|说明|
|---|---|---|---|
|result|AuthResult|请求结果|请求结果|

地址:中国广州市天河区龙口中路211 号华天国际广场首层 

总机:+86 020 85115000 传真:+86 020 85115111 

PAGE 16 

邮编:510630 HTTP://WWW.21CN.COM 

result 格式说明: 

|参数名|类型|字段含义|说明|
|---|---|---|---|
|code|String|结果码|返回参数结果码,0表示成功, 详细参考错误码定义(3.1)|
|Msg|String|结果信息|返回参数结果信息 详细参考错误码定义(3.1)|
|accessCode|String|授权码|天翼账号授权码,默认时效性60分钟|
|operatorType|String|运营商标 识|CT电信,CU联通,CM移动,UN其他|
|expiredTime|int|code失效 时间|表示该accessCode 的有效时间,时间单 位为s|
|reqID|String|请求ID|当次请求ID,异常时进行排障使用|
|gwAuth|String|||
|authCode|String|校验码|天翼账号校验码,用于获取信息接口传 参|

#### 2.4.4. 打开 Mini 登录界面 

#### 【接口说明】 

- 1.使用该接口前,必须先完成调用初始化和预登录接口。在预登录成功后,才调用该接 

- 口打开登录界面,用户点击一键登录按钮,将立即返回登录结果(无网络请求)。 

   - 2.如果无动态配置页面的需求,传入默认的config 即可。 

#### 【调用示例】 

**let** config: AuthConfig = **new** AuthConfig(); 

config.btn5Hidden = Visibility.Hidden; 

// config.otherWayMiniLogBtnHidden = Visibility.Hidden; 

//沉浸式适配配置当设置沉浸式时,要同时修改弹窗 options 参数的 offset 的 dy 为 0 

// config.isFullScreen = true; 

#### //协议页配置 

**let** protocolModels = **new** ArrayList<ProtocolModel>(); 

地址:中国广州市天河区龙口中路211 号华天国际广场首层 

PAGE 17 

总机:+86 020 85115000 传真:+86 020 85115111 

邮编:510630 HTTP://WWW.21CN.COM 

**let** p1: ProtocolModel = **new** ProtocolModel(); 

" " p1.partnerPAText = 登录即同意 ; 

p1.partnerPANameColor = $r('app.color.common_grey_color'); 

protocolModels.add(p1); 

**let** p2: ProtocolModel = **new** ProtocolModel(); p2.PAUrl = "https://e.189.cn/sdk/agreement/detail.do?hidetop=true&appKey=zhpt_inner_test"; 

" " p2.partnerPAText = 《天翼账号服务与隐私协议》 ; 

p2.partnerPANameColor = $r('app.color.common_blue_color'); 

' ' p2.paUrlTitle = 天翼账号服务与隐私协议 ; protocolModels.add(p2); 

**let** p3: ProtocolModel = **new** ProtocolModel(); 

" " p3.partnerPAText = 及 ; p3.partnerPANameColor = $r('app.color.common_grey_color'); protocolModels.add(p3); 

**let** p4: ProtocolModel = **new** ProtocolModel(); 

p4.PAUrl = "https://id.dlife.cn/open/portal/index.html#/"; 

" " p4.partnerPAText = 《自定义协议 1》 ; ' p4.paUrlTitle = 自定义协议标题 1'; 

p4.partnerPANameColor = $r('app.color.common_blue_color'); 

protocolModels.add(p4); 

**let** p5: ProtocolModel = **new** ProtocolModel(); 

p5.PAUrl = "https://id.dlife.cn/open/portal/index.html#/"; " " p5.partnerPAText = 《自定义协议 2》 ; ' p5.paUrlTitle = 自定义协议标题 2'; p5.partnerPANameColor = $r('app.color.common_blue_color'); protocolModels.add(p5); 

**let** p6: ProtocolModel = **new** ProtocolModel(); " " p6.partnerPAText = 并授权应用名获取本机号码 ; p6.partnerPANameColor = $r('app.color.common_grey_color'); protocolModels.add(p6); 

|地址:中国广州市天河区龙口中路211 号华天国际广场首层|PAGE 18|
|---|---|
|总机:+86 020 85115000||
|传真:+86 020 85115111||
|邮编:510630 HTTP://WWW.21CN.COM||

config.miniProtocolModels = protocolModels.convertToArray(); 

**let** options : promptAction.BaseDialogOptions = { 

offset: {dx: 0, dy: 30},// y 轴偏移用于覆盖底部安全区域的情况 

alignment: DialogAlignment.Bottom, maskColor: Color.Transparent, autoCancel: **false** , 

dialogTransition: // 设置弹窗内容显示的过渡效果 

TransitionEffect.translate({ x: 0, y: 490, z: 0 }) 

.animation({ duration: 500, curve: Curve.Smooth }) 

} 

BusinessAuth.openAtuhHYMini(config, **this** .getUIContext(),options, **new** 

AuthLoginResultAdapter()) 

//认证页面 button 点击事件回调 

BusinessAuth.customOperationWithEventHandler((authEventResult:AuthEventResult)=>{ 

console.log("--------点击事件中断回调--------") 

console.log("--------点击的 view 是"+authEventResult.viewId+"--------") 

console.log("--------点击的 clickEvent 是"+authEventResult.clickEvent+"--------") 

**if** (authEventResult.viewId === "miniLoginButton") 

//如果是登录按钮必须调用 continueExecutionWithParams,登录流程才会继续;mini 弹框传 true, 

全屏弹框传 fales 

authEventResult.eventHandle?.continueExecutionWithParams( **true** ); 

}) 

// 创建一个AuthResultListener 的实现类 

**class** AuthLoginResultAdapter **implements** AuthResultListener { 

onResult(result: AuthResult): void { 

**if** (result != **null** ) { 

**const** code: string = result.code; 

**const** accessCode: string = result.accessCode; 

**const** msg: string = result.msg; 

**const** expiredTime: string = result.expiredTime; 

**const** operatorType: string = result.operatorType; 

**const** number: string = result.number; 

**const** reqID: string = result.reqID; 

地址:中国广州市天河区龙口中路211 号华天国际广场首层 PAGE 19 总机:+86 020 85115000 传真:+86 020 85115111 邮编:510630 HTTP://WWW.21CN.COM 

console.log("DebugLog:" + 'code:' + code + '&msg:' + msg + '&accessCode:' + accessCode + "&expiredTime:" + 

expiredTime + "&number:" + number + "&operatorType:" + operatorType) AlertDialog.show( 

{ 

title: '提示', 

message: 'code:' + code + '&msg:' + msg + '&accessCode:' + accessCode + "&expiredTime:" + 

expiredTime + "&number:" + number + "&operatorType:" + operatorType + "&reqID:" + reqID + "&authCode:" + result.authCode + "&gwAuth:" + result.gwAuth, autoCancel: **true** , alignment: DialogAlignment.Center, gridCount: 3, confirm: { value: '确认', action: () => { 

} } 

} 

) 

} 

} 

} 

#### 【请求参数】 

|参数名|类型|必填|说明|
|---|---|---|---|
|config|AuthConfig|是|登录页面控件属性配置|
|uctx|UIContext|是|当前页面的上下文|
|options|promptAction.Base DialogOptions|是|弹窗配置,可参考鸿蒙官方文档 https://developer.huawei.com/cons umer/cn/doc/harmonyos-reference s/js-apis-promptaction#basedialog|

地址:中国广州市天河区龙口中路211 号华天国际广场首层 

PAGE 20 

总机:+86 020 85115000 传真:+86 020 85115111 

邮编:510630 HTTP://WWW.21CN.COM 

||||options11|
|---|---|---|---|
|authLisener|AuthResultListener|是|登录结果回调监听|

#### 【响应参数】 

#### 【响应参数】 

返回结果result 的json 格式说明: 

|参数名|类型|字段含义|说明|
|---|---|---|---|
|result|AuthResult|请求结果|请求结果|

result 格式说明: 

|参数名|类型|字段含义|说明|
|---|---|---|---|
|code|String|结果码|返回参数结果码,0表示成功, 详细参考错误码定义(3.1)|
|Msg|String|结果信息|返回参数结果信息 详细参考错误码定义(3.1)|
|accessCode|String|授权码|天翼账号授权码,默认时效性60分钟|
|operatorType|String|运营商标 识|CT电信,CU联通,CM移动,UN其他|
|expiredTime|int|code失效 时间|表示该accessCode 的有效时间,时间单 位为s|
|reqID|String|请求ID|当次请求ID,异常时进行排障使用|
|gwAuth|String|||
|authCode|String|校验码|天翼账号校验码,用于获取信息接口传 参|

地址:中国广州市天河区龙口中路211 号华天国际广场首层 总机:+86 020 85115000 传真:+86 020 85115111 邮编:510630 HTTP://WWW.21CN.COM 

PAGE 21 

## 3. 附录及常见问题 

### 3.1. **SDK** 错误码定义 

|错误码|含义|
|---|---|
|0|请求成功|
|-64|permission-denied(无权限访问)|
|-65|API-request-rates-Exceed-Limitations(调用接口超限)|
|-10001|取号失败|
|-10002|参数错误|
|-10003|解密失败|
|-10004|ip 受限|
|-10005|异网取号回调参数异常|
|-10006|Mdn 取号失败,且属于电信网络|
|-10007|重定向到异网取号|
|-10008|超过预设取号阈值|
|-10009|时间戳过期|
|-20005|sign-invalid(签名错误)|
|-20006|应用不存在|
|-20007|公钥数据不存在|
|-20100|内部解析错误|
|-20102|加密参数解析失败|
|-30001|时间戳非法|
|-30003|topClass 失效|

地址:中国广州市天河区龙口中路211 号华天国际广场首层 总机:+86 020 85115000 传真:+86 020 85115111 

PAGE 22 

邮编:510630 HTTP://WWW.21CN.COM 

|51002|参数为空|
|---|---|
|51114|无法获取手机号数据|

#### SDK 自定义错误码 

|80000|请求超时|
|---|---|
|80001|请求网络异常|
|80002|响应码错误|
|80003|无网络连接|
|80004|移动网络未开启|
|80006|域名解析异常|
|80007|IO 异常|
|80008|No route to host|
|80009|nodename nor servname provided, or not known|
|80010|Socket closed by remote peer|
|80100|登录结果为空|
|80101|登录结果异常|
|80102|预登录异常|
|80103|SDK 未初始化|
|80104|未调用预登录接口|
|80200|用户关闭界面|
|80201|其他登录方式|
|80800|WIFI 切换异常|
|80801|WIFI 切换超时|

地址:中国广州市天河区龙口中路211 号华天国际广场首层 PAGE 23 总机:+86 020 85115000 传真:+86 020 85115111 邮编:510630 HTTP://WWW.21CN.COM 

|80999|未预期的Crash 问题|
|---|---|

### 3.2. **AuthConfig** 属性说明 

**export class** AuthConfig { 

//所有界面控件均相对于导航栏居中,Margin 定义了控件左、上、右、下的偏移量,注意锚点是 父控件!!。 

/*----------------------------以下为全屏模式配置 ----------------------------------------*/ /* * 导航栏 * */ // 导航栏是否隐藏 **public** navHidden:Visibility; // 返回按钮是否隐藏 **public** navBackBtnHidden:Visibility; // 导航栏背景颜色 **public** navBackgroundColor: ResourceColor; // 导航栏标题 **public** navTitle:string; //针对沉浸式兼容,如果 mainWindow 设置了沉浸式,必传以兼容全局沉浸式的情况 **public** windowStage:window.WindowStage|null; //针对沉浸式兼容,如果 mainWindow 设置了沉浸式,isFullScreen 传 true **public** isFullScreen:boolean; /* * 主体背景图片 * */ **public** backgroundResource?: ResourceStr; **public** backgroundColor: ResourceColor; /*logo 图片 * */ 

地址:中国广州市天河区龙口中路211 号华天国际广场首层 PAGE 24 总机:+86 020 85115000 传真:+86 020 85115111 邮编:510630 HTTP://WWW.21CN.COM 

**public** logoResource: ResourceStr; 

//logo 位置 

**public** logoMargin: Margin; 

// LOGO 图片是否隐藏 

**public** logoHidden: Visibility; 

/**LOGO 宽度*/ 

**public** logoWidth: number | string; 

/**LOGO 高度*/ 

**public** logoHeight: number | string; 

/*----------------------------手机号标签配置 ----------------------------------------*/ /**手机号码字体颜色*/ 

**public** numberColor: ResourceColor; 

/**手机号码字体大小*/ 

**public** numberTextSize: number | string; 

//手机号 

**public** numberTextMargin: Margin; 

/*----------------------------中部小 logo 及标签配置 ------------------------------*/ 

/**品牌标签文字颜色*/ 

**public** brandLabelTextColor: ResourceColor; 

/**品牌标签字体大小*/ 

**public** brandLabelTextSize: number | string; //提供商 **public** ispTextMargin: Margin; //运营商图标 

地址:中国广州市天河区龙口中路211 号华天国际广场首层 总机:+86 020 85115000 传真:+86 020 85115111 邮编:510630 HTTP://WWW.21CN.COM 

PAGE 25 

**public** ispIconMargin: Margin; 

/*----------------------------登录按钮配置 

-------------------------------------*/ 

//登录按钮 

**public** loginBtnMargin: Margin; /**登录按钮文本*/ 

**public** logBtnText: ResourceStr; 

/**登录按钮文本颜色*/ 

**public** logBtnTextColor: ResourceColor; 

/**登录按钮宽度*/ 

**public** logBtnWidth: number | string; 

/**登录按钮高度 

若需单独修改登录按钮的高度,宽度logBtnWidth 不传值或者传0 即可 

*/ 

**public** logBtnHeight: number | string; 

/**登录按钮字体大小*/ 

**public** logBtnTextSize: number | string; 

/** 

* 登录按钮的背景颜色 

*/ 

**public** logBtnBackground: ResourceColor; 

/** 

- 登录按钮的背景图片 

*/ 

**public** logBtnBackgroundImage?: ResourceStr | PixelMap; 

/** 

地址:中国广州市天河区龙口中路211 号华天国际广场首层 总机:+86 020 85115000 传真:+86 020 85115111 

PAGE 26 

邮编:510630 HTTP://WWW.21CN.COM 

- 登录按钮的背景图片对齐方式 

*/ 

**public** logBtnBackgroundImagePosition: Position | Alignment; 

/** 

- 登录按钮的背景图片的宽度和高度 

*/ 

**public** logBtnBackgroundImageSize: SizeOptions | ImageSize; 

/** 

- 登录按钮的挤压态显示效果可选设置是否开启按压态显示效果 

*/ 

**public** logBtnStateEffect: boolean; 

/**登录按钮圆角设置*/ 

**public** logBtnCornerRadius: number | string; 

/*----------------------------其他登录方式按钮配置 --------------------------------*/ /**文本*/ 

**public** otherWayLogBtnText: ResourceStr; 

/**字体大小*/ 

**public** otherWayLogBtnTextSize: number | string; 

/**是否隐藏*/ 

**public** otherWayLogBtnHidden: Visibility; 

#### // 字体颜色 

**public** otherWayLogBtnTextColor: ResourceColor; 

#### //其他登录方式按钮 

**public** otherLoginMargin: Margin; 

/*----------------------------勾选按钮和隐私协议标签 

--------------------------------------*/ 

地址:中国广州市天河区龙口中路211 号华天国际广场首层 总机:+86 020 85115000 传真:+86 020 85115111 

PAGE 27 

邮编:510630 HTTP://WWW.21CN.COM 

#### /**隐私协议确认按钮宽度*/ 

**public** PACheckBtnWidth: number | string; 

#### /**隐私协议确认按钮高度*/ 

**public** PACheckBtnHeight: number | string; 

#### /**隐私协议确认按钮圆角*/ 

**public** PACheckBtnBorderRadius: Length | BorderRadiuses | LocalizedBorderRadiuses; 

/**隐私协议确认按钮勾选状态图片*/ 

**public** PACheckBtnSeletedBackgroundImage: ResourceStr | PixelMap; 

#### /**隐私协议确认按钮未勾选状态图片*/ 

**public** PACheckBtnUnSeletedBackgroundImage: ResourceStr | PixelMap; 

/**隐私协议标签完整文字 

如: 登录即同意《天翼账号服务与隐私协议》与《自定义协议》并授权[应用名]获本机号码 

注意: 1.登录即同意《天翼账号服务与隐私协议》这段文案不允许改变,具体按设计规范设置 2.[应用名]必须替换为具体的app 名字 

*/ 

**public** PALabelText: string; 

#### /**隐私协议标签字体大小*/ 

**public** PALabelTextSize: number; 

#### /**隐私协议标签字体行间距*/ 

**public** PALabelTextLineSpacing: number; 

/**隐私协议标签上的其他文字的颜色 

除了隐私协议名称的其他文字的颜色 

*/ 

**public** PALabelOtherTextColor: ResourceColor; 

/**运营商隐私协议名称的颜色*/ 

**public** PANameColor: ResourceColor; 

地址:中国广州市天河区龙口中路211 号华天国际广场首层 

PAGE 28 

总机:+86 020 85115000 传真:+86 020 85115111 

邮编:510630 HTTP://WWW.21CN.COM 

#### // 接入方自定义协议 

**public** protocolModels: Array<ProtocolModel>|null; 

#### // 协议中显示的 app 名称 

**public** appName: string; 

#### //协议栏 

**public** agreementMargin: Margin; 

**public** customBuilder?: MethodDecorator; 

// ---------------------------------预留按钮自行修改配置全屏和 Mini 模式均生效 

------------------------------------------ 

/*背景图片 

* */ 

**public** btn1Resource: ResourceStr; 

#### //按钮位置 

**public** btn1Margin: Margin; 

// 是否隐藏 

**public** btn1Hidden: Visibility; 

/**宽度*/ 

**public** btn1Width: number | string; 

/**LOGO 高度*/ 

**public** btn1Height: number | string; 

/**标题*/ 

**public** btn1Title: string; 

/* 

背景颜色 

地址:中国广州市天河区龙口中路211 号华天国际广场首层 总机:+86 020 85115000 传真:+86 020 85115111 邮编:510630 HTTP://WWW.21CN.COM 

PAGE 29 

* */ 

**public** btn1Color: ResourceColor; 

/** 

- 背景图片对齐方式 

*/ 

**public** btn1BackgroundImagePosition: Position | Alignment; 

/** 

- 背景图片的宽度和高度 

*/ 

**public** btn1BackgroundImageSize: SizeOptions | ImageSize; 

/** 

- 挤压态显示效果 

*/ 

**public** btn1StateEffect: boolean; 

/*背景图片 

* */ 

**public** btn2Resource: ResourceStr; 

#### //按钮位置 

**public** btn2Margin: Margin; 

#### // 是否隐藏 

**public** btn2Hidden: Visibility; 

/**宽度*/ 

**public** btn2Width: number | string; 

/**LOGO 高度*/ 

**public** btn2Height: number | string; 

/**标题*/ 

**public** btn2Title: string; 

地址:中国广州市天河区龙口中路211 号华天国际广场首层 总机:+86 020 85115000 传真:+86 020 85115111 邮编:510630 HTTP://WWW.21CN.COM 

PAGE 30 

/* 

背景颜色 

* */ 

**public** btn2Color: ResourceColor; 

/** 

- 背景图片对齐方式 

*/ 

**public** btn2BackgroundImagePosition: Position | Alignment; 

/** 

- 背景图片的宽度和高度 

*/ 

**public** btn2BackgroundImageSize: SizeOptions | ImageSize; 

/** 

- 挤压态显示效果 

*/ 

**public** btn2StateEffect: boolean; 

/*背景图片 

* */ 

**public** btn3Resource: ResourceStr; 

//按钮位置 

**public** btn3Margin: Margin; 

#### // 是否隐藏 

**public** btn3Hidden: Visibility; 

/**宽度*/ 

**public** btn3Width: number | string; 

/**LOGO 高度*/ 

**public** btn3Height: number | string; 

地址:中国广州市天河区龙口中路211 号华天国际广场首层 总机:+86 020 85115000 传真:+86 020 85115111 

PAGE 31 

邮编:510630 HTTP://WWW.21CN.COM 

/**标题*/ 

**public** btn3Title: string; 

/* 

背景颜色 

* */ 

**public** btn3Color: ResourceColor; 

/** 

- 背景图片对齐方式 

*/ 

**public** btn3BackgroundImagePosition: Position | Alignment; 

/** 

- 背景图片的宽度和高度 

*/ 

**public** btn3BackgroundImageSize: SizeOptions | ImageSize; 

/** 

- 挤压态显示效果 

*/ 

**public** btn3StateEffect: boolean; 

/*背景图片 

* */ 

**public** btn4Resource: ResourceStr; 

//按钮位置 

**public** btn4Margin: Margin; 

// 是否隐藏 

**public** btn4Hidden: Visibility; 

/**宽度*/ 

**public** btn4Width: number | string; 

地址:中国广州市天河区龙口中路211 号华天国际广场首层 总机:+86 020 85115000 传真:+86 020 85115111 邮编:510630 HTTP://WWW.21CN.COM 

PAGE 32 

/**LOGO 高度*/ 

**public** btn4Height: number | string; 

/**标题*/ 

**public** btn4Title: string; 

/* 

背景颜色 

* */ 

**public** btn4Color: ResourceColor; 

/** 

- 背景图片对齐方式 

*/ 

**public** btn4BackgroundImagePosition: Position | Alignment; 

/** 

- 背景图片的宽度和高度 

*/ 

**public** btn4BackgroundImageSize: SizeOptions | ImageSize; 

/** 

- 挤压态显示效果 

- */ 

**public** btn4StateEffect: boolean; 

#### /*背景图片 

* */ 

**public** btn5Resource: ResourceStr; 

//按钮位置 

**public** btn5Margin: Margin; 

// 是否隐藏 

**public** btn5Hidden: Visibility; 

地址:中国广州市天河区龙口中路211 号华天国际广场首层 总机:+86 020 85115000 传真:+86 020 85115111 邮编:510630 HTTP://WWW.21CN.COM 

PAGE 33 

/**宽度*/ 

**public** btn5Width: number | string; 

#### /**LOGO 高度*/ 

**public** btn5Height: number | string; 

/**标题*/ 

**public** btn5Title: string; 

/* 

背景颜色 

* */ 

**public** btn5Color: ResourceColor; 

/** 

- 背景图片对齐方式 

*/ 

**public** btn5BackgroundImagePosition: Position | Alignment; 

/** 

- 背景图片的宽度和高度 

*/ 

**public** btn5BackgroundImageSize: SizeOptions | ImageSize; 

/** 

- 挤压态显示效果 

*/ 

**public** btn5StateEffect: boolean; 

// ---------------------------------协议提醒弹框配置全屏和 Mini 模式均生效 

------------------------------------------ 

/**弹框标题*/ 

**public** agreementReminderAlertDialogTitle: string; 

地址:中国广州市天河区龙口中路211 号华天国际广场首层 

PAGE 34 

总机:+86 020 85115000 传真:+86 020 85115111 

邮编:510630 HTTP://WWW.21CN.COM 

/**弹框内容*/ 

**public** agreementReminderAlertDialogMessage: string; 

/*----------------------------以下为 mini 模式配置 ----------------------------------------*/ /*----------------------------主体配置 ----------------------------------------*/ 

#### /**主体背景图片*/ 

**public** miniBackgroundResource?: ResourceStr; 

/**主体背景颜色*/ 

**public** miniBackgroundColor: ResourceColor; 

/**主体高度*/ 

**public** miniComponetHeight: Length; 

/**主体宽度*/ 

**public** miniComponetWidth: Length; 

/**主体圆角*/ 

**public** miniComponetBorderRadius: Length | BorderRadiuses | LocalizedBorderRadiuses; 

/*----------------------------顶部标题标签配置 ----------------------------------------*/ //顶部标题 **public** topTitleMargin: Margin; /**顶部标题字体颜色*/ 

**public** topTitleColor: ResourceColor; /**顶部标题字体大小*/顶部标题字体大小*/*/ **public** topTitleTextSize: number | string; //顶部标题文字 **public** topTitleText: string; 

/**顶部标题字体大小*/顶部标题字体大小*/*/ 

地址:中国广州市天河区龙口中路211 号华天国际广场首层 PAGE 35 总机:+86 020 85115000 传真:+86 020 85115111 邮编:510630 HTTP://WWW.21CN.COM 

/*----------------------------关闭按钮配置 

----------------------------------------*/ 

// 关闭按钮采用绝对布局,使用 Position 

//logo 位置 

**public** closeBtnPosition: Position | Edges | LocalizedEdges; 

// LOGO 图片是否隐藏 

**public** closeBtnHidden: Visibility; 

/**LOGO 宽度*/ 

**public** closeBtnWidth: number | string; 

/**LOGO 高度*/ 

**public** closeBtnHeight: number | string; 

/*背景图片 

* */ 

**public** closeBtnResource: ResourceStr; 

/*----------------------------手机号标签配置 

----------------------------------------*/ 

/**手机号码字体颜色*/ 

**public** miniNumberColor: ResourceColor; 

/**手机号码字体大小*/ 

**public** miniNumberTextSize: number | string; 

#### //手机号 

**public** miniNumberTextMargin: Margin; 

/*----------------------------登录按钮配置 -------------------------------------*/ //登录按钮 

**public** miniLoginBtnMargin: Margin; /**登录按钮文本*/ 

地址:中国广州市天河区龙口中路211 号华天国际广场首层 总机:+86 020 85115000 传真:+86 020 85115111 邮编:510630 HTTP://WWW.21CN.COM 

PAGE 36 

**public** miniLogBtnText: ResourceStr; 

/**登录按钮文本颜色*/ 

**public** miniLogBtnTextColor: ResourceColor; 

/**登录按钮宽度*/ 

**public** miniLogBtnWidth: number | string; 

/**登录按钮高度 

若需单独修改登录按钮的高度,宽度logBtnWidth 不传值或者传0 即可 

*/ 

**public** miniLogBtnHeight: number | string; 

/**登录按钮字体大小*/ 

**public** miniLogBtnTextSize: number | string; 

/** 

- 登录按钮的背景颜色 

- */ 

**public** miniLogBtnBackground: ResourceColor; 

/** 

- 登录按钮的背景图片 

*/ 

**public** miniLogBtnBackgroundImage?: ResourceStr | PixelMap; 

/** 

- 登录按钮的背景图片对齐方式 

- */ 

**public** miniLogBtnBackgroundImagePosition: Position | Alignment; 

/** 

- 登录按钮的背景图片的宽度和高度 

- */ 

**public** miniLogBtnBackgroundImageSize: SizeOptions | ImageSize; 

地址:中国广州市天河区龙口中路211 号华天国际广场首层 PAGE 37 总机:+86 020 85115000 传真:+86 020 85115111 邮编:510630 HTTP://WWW.21CN.COM 

/** 

* 登录按钮的挤压态显示效果可选设置是否开启按压态显示效果 

*/ 

**public** miniLogBtnStateEffect: boolean; 

#### /**登录按钮圆角设置*/ 

**public** miniLogBtnCornerRadius: number | string; 

/*----------------------------其他登录方式按钮配置 --------------------------------*/ 

/**文本*/ 

**public** otherWayMiniLogBtnText: ResourceStr; 

/**字体大小*/ 

**public** otherWayMiniLogBtnTextSize: number | string; 

/**是否隐藏*/ 

**public** otherWayMiniLogBtnHidden: Visibility; 

#### // 字体颜色 

**public** otherWayMiniLogBtnTextColor: ResourceColor; 

#### //其他登录方式按钮 

**public** otherWayMiniLoginMargin: Margin; 

/*----------------------------勾选按钮和隐私协议标签 

--------------------------------------*/ 

#### /**隐私协议确认按钮宽度*/ 

**public** miniPACheckBtnWidth: number | string; 

#### /**隐私协议确认按钮高度*/ 

**public** miniPACheckBtnHeight: number | string; 

#### /**隐私协议确认按钮圆角*/ 

**public** miniPACheckBtnBorderRadius: Length | BorderRadiuses | LocalizedBorderRadiuses; 

地址:中国广州市天河区龙口中路211 号华天国际广场首层 总机:+86 020 85115000 传真:+86 020 85115111 邮编:510630 HTTP://WWW.21CN.COM 

|PAGE 38|
|---|

#### /**隐私协议确认按钮勾选状态图片*/ 

**public** miniPACheckBtnSeletedBackgroundImage: ResourceStr | PixelMap; 

#### /**隐私协议确认按钮未勾选状态图片*/ 

**public** miniPACheckBtnUnSeletedBackgroundImage: ResourceStr | PixelMap; 

#### /**隐私协议文案 

如: 登录即同意《天翼账号服务与隐私协议》与《自定义协议》并授权[应用名]获本机号码 

注意:《天翼账号服务与隐私协议》这段文案与协议页URL 不允许改变,具体按设计规范设置, 

协议url 为https://e.189.cn/sdk/agreement/detail.do?hidetop=true&appKey=appid(appid 为 接入方的真实appid) 

*/ 

/**隐私协议字体大小*/ 

**public** miniPALabelTextSize: number; 

#### // 接入方自定义协议 

**public** miniProtocolModels: Array<ProtocolModel>|null; 

#### //协议栏 

**public** miniAgreementMargin: Margin; 

**public** miniCustomBuilder?: MethodDecorator; 

**constructor** () { 

} 

} 

地址:中国广州市天河区龙口中路211 号华天国际广场首层 

PAGE 39 

总机:+86 020 85115000 传真:+86 020 85115111 

邮编:510630 HTTP://WWW.21CN.COM
