开发者支持 关于极光 语言 

产品  解决方案  成功案例  海外消息服务
文档中心  合规指南  开发者社区
极光安全认证  极光文档  >  极光安全认证  >  客户端  SDK  >  HarmonyOS  SDK  >  HarmonyOS  SDK  API
最近更新:2024-09-03
入门指南
HarmonyOS  SDK  接口说明
控制台指南
JVerificationInterface,包含  SDK  所有接口
客户端  SDK
Android  SDK
设置  Debug  模式
HarmonyOS  SDK
支持的版本
HarmonyOS  SDK  集成
开始支持的版本  1.0.0
指南
HarmonyOS  SDK  API  接口定义
HarmonyOS  SDK  错误  JVerificationInterface.setDebugMode(enable:  boolean)
码  接口说明:
iOS  SDK  设置是否开启  debug  模式。true  则会打印更多的日志信息。建议在  init  接口之前调用。
参数说明:
Web  SDK
enable:debug  开关
客户端集成插件
调用示例:
运营商错误码
REST  API
常见问题
JVerificationInterface.setDebugMode( true );
最近更新
资源下载
SDK  初始化
支持的版本
开始支持的版本  1.0.0
接口定义
JVerificationInterface.init(appkey:string,  callback:(code:number, msg:string)=>void)
接口说明:
初始化接口。
参数说明:
appkey:极光appkey
callback:回调接口
回调说明:
code:  返回码,8000  代表初始化成功,其他为失败,详见错误码描述
msg:结果描述
调用示例:
JVerificationInterface. init ( "你的APPKEY" , ( code,  msg )  =>  {
});
获取初始化是否成功标识
支持的版本
开始支持的版本  1.0.0s
接口定义
JVerificationInterface.isInitSuccess()
接口说明:
获取  sdk  是否整体初始化成功的标识
返回结果
boolean  :  true  -  成功,false  -  失败
调用示例:
let  isSuccess  =  JVerificationInterface.isInitSuccess();
判断网络环境是否支持一键登录
支持的版本
开始支持的版本  1.0.0
接口定义
async  JVerificationInterface.checkVerifyEnable()
接口说明:
判断当前的手机网络环境是否可以使用认证。
返回说明:
返回  true  代表可以使用;返回  false  建议使用其他验证方式。
调用示例:
let  verifyEnable  =  await  JVerificationInterface.checkVerifyEnable();
预取号
SDK 会缓存预取号结果,提升之后授权页拉起速度。所以建议拉起授权页前,比如在开屏页或者业务入口页预先调用此接口进行预取号。
请求成功后,不要频繁重复调用。

本页目录 HarmonyOS SDK 接口说明 设置 Debug 模式 SDK 初始化 获取初始化是否成功标识 判断网络环境是否支持一键登录 预取号 判断预取号是否有效 清除预取号缓存 拉起授权页面 关闭授权页面 自定义授权页面 UI 样式 JVerifyUIConfig 一键登录-配置元 素说明 号码认证 

## 不要在预取号回调中重复调用预取号或者拉起授权页接口。 

支持的版本

开始支持的版本 1.0.0 

### 接口定义 

JVerificationInterface.prelogin(callback:(code:number, msg:string, operatorMsg:string)=>void, timeout = 10000) 接口说明: 验证当前运营商网络是否可以进行一键登录操作,该方法会缓存取号信息,提高一键登录效率。建议发起一键登录前先调用此方法。 参数说明: 

timeOut: 超时时间(毫秒), 有效取值范围(5000,30000], 若小于等于 5000 或大于 30000 则取默认值 10000. 推荐设置为 5001-10000. listener:接口回调 

### 回调说明: 

## code: 返回码,7000 代表获取成功,其他为失败,详见错误码描述 

#### content:调用结果信息描述 

### operatorMsg: 运营商信息 

调用示例: 

##### JVerificationInterface. prelogin ( ( code,msg,operateRet )=> { 

console . log ( "code:" + code + ", msg:" + msg + ", operateRet:" + operateRet); }); 

# 判断预取号是否有效 

支持的版本 

开始支持的版本 1.0.0 

接口定义

async  JVerificationInterface.isValidePreloginCache()

接口说明: 

### 判断当前预取号是否有效。 

### 返回说明: 

返回 true 代表可以使用;返回 false 建议使用其他验证方式。 调用示例: 

let  enable  =  await  JVerificationInterface.isValidePreloginCache();

# 清除预取号缓存 

支持的版本 接口定义 

开始支持的版本 1.0.0 

### JVerificationInterface.clearPreLoginCache() 接口说明: 

### 清除 sdk 当前预取号结果缓存。 调用示例: JVerificationInterface .clearPreLoginCache (); 

# 拉起授权页面 

一键登录需要依赖预取号结果,如果没有预取号,一键登录时会自动预取号。
建议拉起授权页前,比如在开屏页或者业务入口页预先调用此接口进行预取号,可以提升授权页拉起速度,优化体验。
一键登录请求成功后,不要频繁重复调用。运营商会限制单位时间内请求次数。
不要在一键登录回调中重复调用预取号或者拉起授权页接口。
支持的版本
开始支持的版本  1.0.0
接口定义
JVerificationInterface.loginAuth(settings:JVerificationLoginSettings,  callback:(code:number,  msg:string,  operatorMsg:string)=>void)
接口说明:
调起一键登录授权页面,在用户授权后获取  loginToken
参数说明:
settings:登录接口设置项。
callback:登录授权结果回调
回调说明:

code: 返回码,6000 代表 loginToken 获取成功,6001 代表 loginToken 获取失败,其他返回码详见描述 content:返回码的解释信息,若获取成功,内容信息代表 loginToken。 

### operatorReturn: 运营商结果信息 

调用示例:

```arkts
let settings = new JVerificationLoginSettings (); JVerificationInterface. loginAuth (settings, ( code,msg,operateRet )=> { console . log ( "code:" + code + ", msg:" + msg + ", operateRet:" + operateRet); }); 
```

一键登录参数JVerificationLoginSettings

export class JVerificationLoginSettings { autoFinish = true ; //自动关闭,仅限联通,电信 timeout = 10 * 1000 ; //超时时间} 

说明 :获取到一键登录的 loginToken 后,将其返回给应用服务端,从服务端调用 REST API 来获取手机号码 

关闭授权页面

支持的版本 开始支持的版本 1.0.0 接口定义 

JVerificationInterface.dismissLoginAuthActivity() 

接口说明:
关闭登录授权页,如果当前授权正在进行,则  loginAuth  接口会立即触发  6002  取消回调。
仅限联通,电信
调用示例:

JVerificationInterface .dismissLoginAuthActivity ()

自定义授权页面  UI  样式
支持的版本
开始支持的版本  1.0.0
接口定义

JVerificationInterface.setCustomUIWithConfig(config:JVerifyUIConfig) 

接口说明: 

修改授权页面主题,开发者可以通过  setCustomUIWithConfig  方法修改授权页面主题,需在  loginAuth  接口之前调用
参数说明:
uiConfig:主题配置对象,开发者在  JVerifyUIConfig.java  类中调用对应的方法配置授权页中对应的元素,详情参考  JVerifyUIConfig  配置元素说明 。
调用示例:
let  uiconfig  =  new  JVerifyUIConfig();
uiconfig.authPageType  = 1 ;
uiconfig.dialogPage  =  this ;
uiconfig.btnName  =  "按钮名字" ;
uiconfig.loginBtnColor  =  0xff0000 ;
uiconfig.loginTextColor  =  0x00ff00 ;
uiconfig.customPolicyLinkColor  =  0x0000ff ;
uiconfig.privacyList  = [

- [ "《自定义协议1》" , "https://opencloud.wostore.cn/authz/resource/html/disclaimer.html?fromsdk=true" ], 

- [ "《自定义协议2》" , "https://opencloud.wostore.cn/authz/resource/html/disclaimer.html?fromsdk=true" ], [ "《自定义协议3》" , "https://opencloud.wostore.cn/authz/resource/html/disclaimer.html?fromsdk=true" ] 

] 

JVerificationInterface.setCustomUIWithConfig(uiconfig); 

# JVerifyUIConfig 一键登录-配置元素说明 

设置授权页背景 支持的版本 :1.0.0 登录页导航栏 方法 参数类型 说明 authPageType number 登录模式0全屏 1弹窗 dialogPage object 展示弹窗的Component页面 btnName string 按钮名字 loginBtnColor number 登录按钮颜色HEX loginTextColor number 登录按钮文本颜色HEX privacyList string[][] 自定义隐私协议,[["隐私协议名","隐私协议地址"]] customPolicyLinkColor number 用户协议文字颜色HEX cmDialogController CustomDialogController 中国移动弹窗一键登录专用,暂时必须要设置该属性才能使用 导入一键登录页面使用的图片 需要将SDK用的图片导入至AppScope/resources/base/media文件夹内 文件名 说明 jverify_background.png 一键登录主背景图片 jverify_ctlogo.png 电信logo jverify_culogo.png 联通logo jverify_dialog_background.png 一键登录弹窗背景图片 jverify_dialog_close.png 一键登录弹窗关闭按钮 

号码认证 支持的版本 开始支持的版本 1.0.0 接口定义 JVerificationInterface.getToken(callback:(code:number, msg:string)=>void, timeout = 10000) 

接口说明: 

在预定时间内获取当前在线的 sim 卡所在运营商及 token,如果超过所设时间,接口回调返回超时。 参数说明: timeOut: 超时时间(毫秒), 有效取值范围(5000,30000], 若小于等于 5000 或大于 30000 则取默认值 10000. 推荐设置为 5001-10000. callback:接口回调 

回调说明: 

code: 返回码,2000 代表获取成功,其他为失败,详见错误码描述 

content:成功时为 token,可用于调用验证手机号接口。token 有效期为 1 分钟,超过时效需要重新获取才能使用。失败时为失败信息 

operatorReturn: 运营商结果信息 

调用示例: 

JVerificationInterface. getToken ( ( code,msg,operateRet )=> { 

console . log ( "code:" + code + ", msg:" + msg + ", operateRet:" + operateRet); 

}); 

文档内容是否对您有帮助? 

提交评分
