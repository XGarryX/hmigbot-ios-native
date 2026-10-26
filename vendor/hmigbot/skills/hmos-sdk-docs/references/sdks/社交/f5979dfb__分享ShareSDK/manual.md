# **ShareSDK-Ohos** 

# **SDK-集成** 

## **一** **.添加SDK依赖** 

#### 在 **Terminal** 窗口中,执行如下命令进行安装 

ohpm install @zztsdk/zztcore 

ohpm install @zztsdk/sharesdk 

## **二.权限** 

ohos.permission.INTERNET 

### **建议权限** 

ohos.permission.APP_TRACKING_CONSENT // 用于产生设备ID ohos.permission.GET_NETWORK_INFO // 用于判断网络类型,进行连接与数据传输优化 ohos.permission.APPROXIMATELY_LOCATION ohos.permission.GET_WIFI_INFO 

## **三.导入模块** 

import { ZztSDK } from '@zztsdk/zztcore'; 

import mobShare from '@zztsdk/sharesdk'; 

## **四.华为账号服务配置** 

在工程中entry模块的module.json5文件中,新增metadata,配置name为client_id,value为AppGallery Connect平台中申请的Client ID 

Client ID申请教程:https://developer.huawei.com/consumer/cn/doc/harmonyos-guides/account-preparatio ns-0000001650283393 

"module": { "name": "xxx", "type": "entry", "description": "xxx", "mainElement": "xxx", "deviceTypes": [], "pages": "xxx", "abilities": [], 

"metadata": [ // 配置信息如下 { "name": "client_id", "value": "xxx" } ] } 

## **五.微博集成** 

使用微博sdk授权和分享时,请确保你的AppKey、RedirectURI、Scope、PackageName和开发者官网中填写的一 致. 

### **1.添加微博SDK依赖** 

在oh-package.json5中添加微博SDK离线依赖 

//示例 { "name": "sharesdkforhosnext", "version": "1.0.0", "description": "Please describe the basic information.", "main": "", "author": "", "license": "", "dependencies": { "@zztsdk/zztcore": "^1.0.0", '@zztsdk/sharesdk': "^1.0.0", 'core': "您微博SDK的har文件的路径地址,例:file:./Libs/Weibo-1.0.0.har" }, "devDependencies": { "@ohos/hypium": "1.0.16", "@ohos/hamock": "1.0.0" }, "dynamicDependencies": {} } 

### **2.获取开发平台注册所需签名** 

在任意位置调用如下代码,获取debug和release包对应的签名,用于开放平台注册。获取完成可删除此代码 

import { Utility, WBAPI } from 'Weibo'; 

new Utility().getSign().then(sign => { // 获取debug和release包对应的签名,用于开放平台注册。获取完成可删除此代码。 console.log("Weibo get sign: " + sign); }) 

### **3.设置微博AppKey、RedirectURI、Scope参数** 

在分享/授权前设置微博SDK使用的AppKey、RedirectURI、Abiltiy 

##### //示例代码 

let map = new HashMap<string, Object>() " map.set(mobShare.Platform_Info.APP_KEY, 您的微博AppKey") " map.set(mobShare.Platform_Info.REDIRECT_URL, 您的微博RedirectURI") " map.set(mobShare.Platform_Info.CALLBACK_ABILITY_NAME, 您的微博分享/授权回呼Abiltiy") await mobShare.ShareSDK.getInstance().setPlatformDevInfoAsync(mobShare.Platform.SinaWeibo, map) 

### **4.添加微博回调解析方法** 

在您设置的微博授权/分享后的回呼abiltiy的onCreate和onNewWant中调用 mobShare.ShareSDK.getInstance().handlerWant(want, this.context)进行回调解析 

//示例 import { Utility, WBAPI } from 'Weibo'; 

```arkts
export default class EntryAbility extends UIAbility { onCreate(want: Want, launchParam: AbilityConstant.LaunchParam): void { hilog.info(0x0000, 'testTag', '%{public}s', 'Ability onCreate'); 
```

//如需要同步获取分享/授权结果 使用await mobShare.ShareSDK.getInstance().handlerWant(want, this.context) 

mobShare.ShareSDK.getInstance().handlerWant(want, this.context) } 

onNewWant(want: Want, launchParam: AbilityConstant.LaunchParam): void { //如需要同步获取分享/授权结果 使用await mobShare.ShareSDK.getInstance().handlerWant(want, this.context) 

mobShare.ShareSDK.getInstance().handlerWant(want, this.context) } ....... } 

## **六.微信集成** 

使用微信sdk授权和分享时,请确保你的AppKey、AppSecret和开发者官网中填写的一致. 

### **1.设置微信AppKey和AppSecret** 

在分享/授权前设置微信SDK使用的AppKey和AppSecret 

##### //示例代码 

let map = new HashMap<string, Object>() 

map.set(mobShare.Platform_Info.APP_KEY, "您的微信APPKEY") 

" map.set(mobShare.Platform_Info.APP_SECRET, 您的微信AppSecret") 

await mobShare.ShareSDK.getInstance().setPlatformDevInfoAsync(mobShare.Platform.Wechat, map) 

### **2.添加微信回调解析方法** 

在您进行微信授权/分享的abiltiy的onCreate和onNewWant中调用 

mobShare.ShareSDK.getInstance().handlerWant(want, this.context)进行回调解析 

//示例 

import { Utility, WBAPI } from 'Weibo'; 

export default class EntryAbility extends UIAbility { 

onCreate(want: Want, launchParam: AbilityConstant.LaunchParam): void { 

hilog.info(0x0000, 'testTag', '%{public}s', 'Ability onCreate'); 

- //如需要同步获取分享/授权结果 使用await mobShare.ShareSDK.getInstance().handlerWant(want, 

- this.context) 

mobShare.ShareSDK.getInstance().handlerWant(want, this.context) 

} 

onNewWant(want: Want, launchParam: AbilityConstant.LaunchParam): void { 

//如需要同步获取分享/授权结果 使用await mobShare.ShareSDK.getInstance().handlerWant(want, this.context) 

mobShare.ShareSDK.getInstance().handlerWant(want, this.context) 

} 

....... 

} 

# **SDK-API** 

## **约束** 

本模块首批接口从 OpenHarmony SDK API version 12 开始支持。 

## **初始化** 

#### **注意:请确保传入context非空** 

init()接口内部会做隐私授权状态的判断,在应用向ZztSDK提交隐私授权同意状态之前不会做任何业务的初始化, 可放心调用 

" " ZztSDK.init(context, 您的AppKey", 您的AppSecret") 

## **隐私提交** 

#### **注意:请确保在调用初始化方法后调用该方法** 

应用在向终端用户展示“隐私声明”弹框,并获取终端用户的隐私授权结果后,需将隐私授权结果回传给ZztSDK。 

//仅当授权结果为“true”时,ZztSDK各项功能才可正常使用。 

ZztSDK.submitPolicyGrantResult(granted) 

#### **初始化示例代码** : 

//初始化 " " ZztSDK.init(context, 您的AppKey", 您的AppSecret") //隐私提交 

ZztSDK.submitPolicyGrantResult(true) 

## **获取指定的平台** 

#### 通过平台名获取指定平台对象 

//此接口已废弃 请使用 getPlatformAsync()方法 getPlatform(name: string): IPlatform //name:平台名 

getPlatformAsync(name: string): Promise<IPlatform> 

##### //代码示例: 

let plat = await 

mobShare.ShareSDK.getInstance().getPlatformAsync(mobShare.Platform.SYSTEM) 

mobShare.ShareSDK.getInstance().getPlatformAsync(mobShare.Platform.SYSTEM).then((plat) => {}) 

## **设置回调接口** 

#### 设置分享/授权的结果回调(成功/失败/取消) 

##### setPlatformActionListener(platformListener: PlatformActionListener): void 

##### //代码示例: 

let receive: mobShare.PlatformActionListener = { 

onComplete: (platform: mobShare.IPlatform, action: number, res: Map<string, Object>) => { 

//成功回调 platform:平台对象 action:表示当前的动作(分享:1,授权:2,获取用户信息:3) }, 

onError: (platform: mobShare.IPlatform, action: number, error: Error) => { 

//异常回调 platform:平台对象 action:表示当前的动作(分享:1,授权:2,获取用户信息:3) }, 

onCancel: (platform: mobShare.IPlatform, action: number) => { 

//取消回调 platform:平台对象 action:表示当前的动作(分享:1,授权:2,获取用户信息:3) } 

} 

let plat = await 

mobShare.ShareSDK.getInstance().getPlatformAsync(mobShare.Platform.SYSTEM) plat.setPlatformActionListener(receive) 

## **注册平台信息** 

#### 为指定平台设置平台信息且返回设置结果 

//此接口已废弃 请使用setPlatformDevInfoAsync()方法 setPlatformDevInfo(platformName: string, devInfo: HashMap<string, Object>) //platformName:平台名 

//devInfo:平台信息 

setPlatformDevInfoAsync(platformName: string, devInfo: HashMap<string, Object>): Promise<boolean> 

##### //示例代码: 

let map = new HashMap<string, Object>() "" map.set(mobShare.Platform_Info.APP_KEY, ) "" map.set(mobShare.Platform_Info.REDIRECT_URL, ) "" map.set(mobShare.Platform_Info.CALLBACK_ABILITY_NAME, ) let isSuccess = await mobShare.ShareSDK.getInstance().setPlatformDevInfoAsync(mobShare.Platform.SinaWeibo, map) 

## **设置UIAbilityContext** 

为分享/授权设置需要的UIAbilityContext 

setUIAbilityContext(context: common.UIAbilityContext) 

##### //示例代码: 

await mobShare.ShareSDK.getInstance().setUIAbilityContext(getContext() as common.UIAbilityContext) 

## **接收解析三方平台回调方法** 

#### 三方平台分享/授权回调解析方法 

handlerWant(want: Want, context: common.UIAbilityContext) 

##### //示例代码: 

await mobShare.ShareSDK.getInstance().handlerWant(want, this.context) 

## **分享** 

分享到第三方平台 

//records:分享参数 //context:拉起分享面板的上下文对象 

//options:分享控制器配置项 

share(records: SharedParam[], context?: Context, options?: ShareControllerOptions): void 

//代码示例: 

```arkts
let records: Array<mobShare.SharedParam> = new Array() records.push({utd: mobShare.ShareType.TEXT,content: "测试分享文本",}) let receive: mobShare.PlatformActionListener = { onComplete: (platform: mobShare.IPlatform, action: number, res: Map<string, Object>) => { //成功回调 }, onError: (platform: mobShare.IPlatform, action: number, error: Error) => { //异常回调 }, onCancel: (platform: mobShare.IPlatform, action: number) => { //取消回调 } } let plat = await mobShare.ShareSDK.getInstance().getPlatformAsync(mobShare.Platform.SYSTEM) plat.setPlatformActionListener(receive) plat.share(records, getContext(), { previewMode: mobShare.SharePreviewMode.DEFAULT, selectionMode: mobShare.SelectionMode.SINGLE }) 
```

## **授权** 

#### 第三方平台授权 

//params:scope权限 选填 authorize(params?: Map<string, Object>): void 

//代码示例: let params = new Map<string, Object>() params.set("scopes", ['profile']) params.set("permissions", ['idtoken']) let plat = await mobShare.ShareSDK.getInstance().getPlatformAsync(mobShare.Platform.HUAWEI) let receive: mobShare.PlatformActionListener = { onComplete: (platform: mobShare.IPlatform, action: number, res: Map<string, Object>) => { //成功回调 }, onError: (platform: mobShare.IPlatform, action: number, error: Error) => { //异常回调 }, onCancel: (platform: mobShare.IPlatform, action: number) => { //取消回调 } } 

plat.setPlatformActionListener(receive) plat.authorize(params) 

## **获取用户信息** 

#### 获取指定账号的用户信息 

//account:账号Id 选填 showUser(account?: string | null): void 

//代码示例: 

let plat = await mobShare.ShareSDK.getInstance().getPlatformAsync(mobShare.Platform.HUAWEI) let receive: mobShare.PlatformActionListener = { 

```arkts
onComplete: (platform: mobShare.IPlatform, action: number, res: Map<string, Object>) => { let msg = "showUser onComplete:" + platform.getName() + ",action:" + action + ",map:" + HashonHelper.fromMap(res) //输出所有授权信息 let dbMsg = platform.getDb().export Data() console.log(msg) console.log("dbMessage:" + dbMsg) }, onError: (platform: mobShare.IPlatform, action: number, error: Error) => { //异常回调 }, onCancel: (platform: mobShare.IPlatform, action: number) => { //取消回调 } } plat.setPlatformActionListener(receive) plat.showUser() 
```

## **判断是否授权** 

判断是否已经存在授权状态,可以根据自己的登录逻辑设置 

isAuthValid(): Promise<boolean> 

//代码示例: mobShare.ShareSDK.getInstance() 

.getPlatformAsync(mobShare.Platform.HUAWEI).then((plat) => { 

plat.isAuthValid().then((isAuth) => { this.showMessage("HUAWEI isAuth:" + isAuth) 

}) }) 

## **取消授权** 

移除授权状态和本地缓存,下次授权会重新授权获取新的授权信息 

removeAccount(removeCookie?: boolean): void 

//代码示例: 

await 

mobShare.ShareSDK.getInstance().getPlatformAsync(mobShare.Platform.HUAWEI).removeAccount() 

## **设置三方平台通用回调** 

setCommandReceive(receiver: PlatformCommandReceive): void 

//代码示例: 

let plat = await mobShare.ShareSDK.getInstance().getPlatformAsync(mobShare.Platform.Wechat) let receive: mobShare.PlatformCommandReceive = { 

onCommandReceive: (platform: mobShare.IPlatform, action: number, res: Map<string, Object>): void => { 

//通用回调 platform:平台对象 action:表示当前的动作(分享:1,授权:2,获取用户信息:3) res:信息 内容 

let msg = "launchMiniProgram onResp:" + platform.getName() + ",action:" + action + ",map:" + res.get("extMsg") 

console.log(msg) this.showMessage(msg) } } plat.setCommandReceive(receive) plat.share(records, getContext(this) as common.UIAbilityContext) 

## **授权数据** 

/** * 获取授权账户的token */ getToken(): string 

/** 

- 获取token的有效时常(单位:秒) 

*/ getExpiresIn(): number 

/** 

* 获取token的有效截止时间(单位:毫秒) */ getExpiresTime(): number 

/** * 设置用户id */ getUserId(): string 

/** * 返回用户登陆账号的名称 */ getUserName(): string 

/** * 返返回用户登陆账号的头像 */ getUserIcon(): string /** * 删除授权账户 */ removeAccount(): void 

/** 

* 批量导出JSON格式的数据 */ exportData(): string /** 

* 返回登陆账号的openid */ getOpenID(): string /** 

* 返回登陆账号的unionID */ getUnionID(): string 

/** * 返回登陆账号的邮箱 */ getEmail(): string 

//代码示例: 

let token = await 

mobShare.ShareSDK.getInstance().getPlatformAsync(mobShare.Platform.HUAWEI).getDb().getToke n() 

## **授权权限范围** 

scope权限 

|**名称**|**类型**|**说明**|
|---|---|---|
|scopes|string[]|scope列表,用于获取用户数据。与permissions属性不能同时为空,否则会返回 1001502003输入参 数值无效错误码。如果传入不合法的scope(例如空值等)则直接返回openID和unionID。scope取值 范围:profile:华为账号用户的基本信息,如昵称头像等(元服务不支持该scope)。openid:华为 账号用户的OpenID、UnionID。phone:华为账号快速验证手机号。realTimePhone:华为账号实时 验证手机号(该scope只能和openid同时使用)。quickLoginAnonymousPhone:获取华为账号绑定 的匿名手机号(该scope只能与openid同时使用)。identity:华为账号用户实名信息。 verifyRealName:华为账号用户实名信息校验(该scope需和openid同时使用,且只能与openid同时 使用)。verifyFace:人脸核身(该scope需和openid同时使用,且只能与openid同时使用)。|
|permissions|string[]|permission列表。与scopes属性不能同时为空,否则会返回 1001502003输入参数值无效错误码。如 果传入不合法的permission(例如空值等)则直接返回openID和unionID。permission取值范围: serviceauthcode:用户授权临时凭据。idtoken:用户身份认证信息。|
|forceAuthorization|boolean|用户是否需要登录授权,默认为true。如果该值为true且用户未登录或未授权,则会拉起用户登录或授 权页面。另外,AuthorizationWithHuaweiIDRequest必须在ArkUI页面上下文中执行,否则会抛出异 常。如果该值为false并且用户未登录,则在执行AuthorizationWithHuaweiIDRequest情况下将返回 1001502001华为账号未登录。|
|idTokenSignAlgorithm|IdTokenSignAlgorithm|默认为PS256,用于指定ID Token的签名算法。|

## **三方平台配置信息** 

|**名称**|**值**|**说明**|
|---|---|---|
|APP_KEY|appKey|注册三方平台使用的appkey|
|APP_SECRET|appSecret|注册三方平台使用的appSecret|
|REDIRECT_URL|redirectUrl|注册三方平台使用的授权回调地址链接|
|SCOPE|scope|注册三方平台时申请的权限名|
|CALLBACK_ABILITY_NAME|callbackAbility|Name 三方平台授权/分享后的回呼abiltiy名|
|**名称统一数据类型mobShare.ShareT**|**值ype**|**说明**|
|ENTITY|'general.entity'|所有表示物理存储类型的基类型,无归属类型。|
|OBJECT|'general.object'|所有表示逻辑内容类型的基类型,无归属类型。|
|COMPOSITE_OBJECT|'general.composite-object'|所有组合内容类型(例如PDF文件类型混合了文本和图片类数据)的基类型,归属 类型为OBJECT。|
|TEXT|'general.text'|所有文本的基类型,归属类型为OBJECT。|
|PLAIN_TEXT|'general.plain-text'|未指定编码的文本类型,没有标识符,归属类型为TEXT。|
|HTML|'general.html'|HTML文本类型,归属类型为TEXT。|
|HYPERLINK|'general.hyperlink'|超链接类型,归属类型为TEXT。|
|XML|'general.xml'|XML文本类型,归属类型为TEXT。|
|SOURCE_CODE|'general.source-code'|所有源代码的基类型,归属类型为PLAIN_TEXT。|

|SCRIPT|'general.script'|所有脚本语言源代码的基类型,归属类型为SOURCE_CODE。|
|---|---|---|
|SHELL_SCRIPT|'general.shell-script'|shell脚本类型,归属类型为SCRIPT。|
|CSH_SCRIPT|'general.csh-script'|C-shell脚本类型,归属类型为SHELL_SCRIPT。|
|PERL_SCRIPT|'general.perl-script'|Perl脚本类型,归属类型为SHELL_SCRIPT。|
|PHP_SCRIPT|'general.php-script'|PHP脚本类型,归属类型为SHELL_SCRIPT。|
|PYTHON_SCRIPT|'general.python-script'|Python脚本类型,归属类型为SHELL_SCRIPT|
|RUBY_SCRIPT|'general.ruby-script'|Ruby脚本类型,归属类型为SHELL_SCRIPT。|
|TYPE_SCRIPT|'general.type-script'|TypeScript源代码类型,归属类型为SCRIPT。|
|JAVA_SCRIPT|'general.java-script'|JavaScript源代码类型,归属类型为SCRIPT。|
|C_HEADER|'general.c-header'|C头文件类型,归属类型为SOURCE_CODE。|
|C_SOURCE|'general.c-source'|C源代码类型,归属类型为SOURCE_CODE。|
|C_PLUS_PLUS_HEADER|'general.c-plus-plus-header'|C++头文件类型,归属类型为SOURCE_CODE。|
|C_PLUS_PLUS_SOURCE|'general.c-plus-plus-source'|C++源代码类型,归属类型为SOURCE_CODE。|
|JAVA_SOURCE|'general.java-source'|Java源代码类型,归属类型为SOURCE_CODE。|
|EBOOK|'general.ebook'|所有电子书文件格式的基类型,归属类型为COMPOSITE_OBJECT。|
|EPUB|'general.epub'|电子出版物(EPUB)文件格式类型,归属类型为EBOOK。|
|AZW|'com.amazon.azw'|AZW电子书文件格式类型,归属类型为EBOOK。|
|AZW3|'com.amazon.azw3'|AZW3电子书文件格式类型,归属类型为EBOOK。|
|KFX|'com.amazon.kfx'|KFX电子书文件格式类型,归属类型为EBOOK。|
|MOBI|'com.amazon.mobi'|MOBI电子书文件格式类型,归属类型为EBOOK。|
|MEDIA|'general.media'|所有媒体的基类型,归属类型为OBJECT。|
|IMAGE|'general.image'|所有图片的基类型,归属类型为MEDIA。|
|JPEG|'general.jpeg'|JPEG图片类型,归属类型为IMAGE。|
|PNG|'general.png'|PNG图片类型,归属类型为IMAGE。|
|RAW_IMAGE|'general.raw-image'|所有原始图像格式的基类型,归属类型为IMAGE。|
|TIFF|'general.tiff'|TIFF图片类型,归属类型为IMAGE。|
|BMP|'com.microsoft.bmp'|WINDOWS位图图像类型,归属类型为IMAGE。|
|ICO|'com.microsoft.ico'|WINDOWS图标图像类型,归属类型为IMAGE。|
|PHOTOSHOP_IMAGE|'com.adobe.photoshop-image'|Adobe Photoshop图片类型,归属类型为IMAGE。|
|AI_IMAGE|'com.adobe.illustrator.ai- image'|Adobe Illustrator图片类型,归属类型为IMAGE。|
|WORD_DOC|'com.microsoft.word.doc'|Microsoft Word数据类型,归属类型为COMPOSITE_OBJECT。|
|EXCEL|'com.microsoft.excel.xls'|Microsoft Excel数据类型,归属类型为COMPOSITE_OBJECT。|
|PPT|'com.microsoft.powerpoint.ppt'|Microsoft PowerPoint演示文稿类型,归属类型为COMPOSITE_OBJECT。|
|PDF|'com.adobe.pdf'|PDF数据类型,归属类型为COMPOSITE_OBJECT。|
|POSTSCRIPT|'com.adobe.postscript'|PostScript数据类型,归属类型为COMPOSITE_OBJECT。|
|ENCAPSULATED_POSTSCRIPT|'com.adobe.encapsulated- postscript'|Encapsulated PostScript类型,归属类型为POSTSCRIPT。|
|VIDEO|'general.video'|所有视频的基类型,归属类型为MEDIA。|
|AVI|'general.avi'|AVI视频类型,归属类型为VIDEO。|
|MPEG|'general.mpeg'|MPGE-1或MPGE-2视频类型,归属类型为VIDEO。|
|MPEG4|'general.mpeg-4'|MPGE-4视频类型,归属类型为VIDEO。|
|VIDEO_3GPP|'general.3gpp'|3GPP视频类型,归属类型为VIDEO。|

|VIDEO_3GPP2|'general.3gpp2'|3GPP2视频类型,归属类型为VIDEO。|
|---|---|---|
|WINDOWS_MEDIA_WM|'com.microsoft.windows- media-wm'|WINDOWS WM视频类型,归属类型为VIDEO。|
|WINDOWS_MEDIA_WMV|'com.microsoft.windows- media-wmv'|WINDOWS WMV视频类型,归属类型为VIDEO。|
|WINDOWS_MEDIA_WMP|'com.microsoft.windows- media-wmp'|WINDOWS WMP视频类型,归属类型为VIDEO。|
|AUDIO|'general.audio'|所有音频的基类型,归属类型为MEDIA。|
|AAC|'general.aac'|AAC音频类型,归属类型为AUDIO。|
|AIFF|'general.aiff'|AIFF音频类型,归属类型为AUDIO。|
|ALAC|'general.alac'|ALAC音频类型,归属类型为AUDIO。|
|FLAC|'general.flac'|FLAC音频类型,归属类型为AUDIO。|
|MP3|'general.mp3'|MP3音频类型,归属类型为AUDIO。|
|OGG|'general.ogg'|OGG音频类型,归属类型为AUDIO。|
|PCM|'general.pcm'|PCM音频类型,归属类型为AUDIO。|
|WINDOWS_MEDIA_WMA|'com.microsoft.windows- media-wma'|WINDOWS WMA音频类型,归属类型为AUDIO。|
|WAVEFORM_AUDIO|'com.microsoft.waveform- audio'|WINDOWS波形音频类型,归属类型为AUDIO。|
|WINDOWS_MEDIA_WMX|'com.microsoft.windows- media-wmx'|WINDOWS WMX音频类型,归属类型为AUDIO。|
|WINDOWS_MEDIA_WVX|'com.microsoft.windows- media-wvx'|WINDOWS WVX音频类型,归属类型为AUDIO。|
|WINDOWS_MEDIA_WAX|'com.microsoft.windows- media-wax'|WINDOWS WAX音频类型,归属类型为AUDIO。|
|FILE|'general.file'|所有文件的基类型,归属类型为ENTITY。|
|DIRECTORY|'general.directory'|所有目录的基类型,归属类型为ENTITY。|
|FOLDER|'general.folder'|所有文件夹的基类型,归属类型为DIRECTORY。|
|SYMLINK|'general.symlink'|所有符号链接的基类型,归属类型为ENTITY。|
|ARCHIVE|'general.archive'|所有文件和目录存档文件的基类型,归属类型为OBJECT。|
|BZ2_ARCHIVE|'general.bz2-archive'|BZ2存档文件类型,归属类型为ARCHIVE。|
|DISK_IMAGE|'general.disk-image'|所有可作为卷装载项的文件类型的基类型,归属类型为ARCHIVE。|
|TAR_ARCHIVE|'general.tar-archive'|TAR存档文件类型,归属类型为ARCHIVE。|
|ZIP_ARCHIVE|'general.zip-archive'|ZIP存档文件类型,归属类型为ARCHIVE。|
|JAVA_ARCHIVE|'com.sun.java-archive'|JAVA存档文件类型,归属类型为ARCHIVE。|
|GNU_TAR_ARCHIVE|'org.gnu.gnu-tar-archive'|GUN存档文件类型,归属类型为ARCHIVE。|
|GNU_ZIP_ARCHIVE|'org.gnu.gnu-zip-archive'|GZIP存档文件类型,归属类型为ARCHIVE。|
|GNU_ZIP_TAR_ARCHIVE|'org.gnu.gnu-zip-tar-archive'|GZIP TAR存档文件类型,归属类型为ARCHIVE。|
|CALENDAR|'general.calendar'|所有日程类数据的基类型,归属类型为OBJECT。|
|CONTACT|'general.contact'|所有联系人类数据的基类型,归属类型为OBJECT。|
|DATABASE|'general.database'|所有数据库文件的基类型,归属类型为OBJECT。|
|MESSAGE|'general.message'|所有消息类数据的基类型,归属类型为OBJECT。|
|VCARD|'general.vcard'|所有电子名片类数据的基类型,归属类型为OBJECT。|
|NAVIGATION|'general.navigation'|所有导航类数据的基类型,归属类型为OBJECT。|
|LOCATION|'general.location'|导航定位类型,归属类型为NAVIGATION。|

|OPENHARMONY_FORM|'openharmony.form'|系统定义的卡片类型,归属类型为OBJECT。|
|---|---|---|
|OPENHARMONY_APP_ITEM|'openharmony.app-item'|系统定义的桌面图标类型,归属类型为OBJECT。|
|OPENHARMONY_PIXEL_MAP|'openharmony.pixel-map'|系统定义的像素图类型,归属类型为IMAGE。|
|OPENHARMONY_ATOMIC_SERVICE|'openharmony.atomic-service'|系统定义的元服务类型,归属类型为OBJECT。|
|OPENHARMONY_PACKAGE|'openharmony.package'|系统定义的包(即目录的打包文件),归属类型为DIRECTORY。|
|OPENHARMONY_HAP|'openharmony.hap'|系统定义的能力包,归属类型为OPENHARMONY_PACKAGE。|
|OPEN_WXMINIPROGRAM|'openWXMiniProgram'|APP拉起微信小程序功能|

## **分享参数类型** 

### **mobShare.SharedParam** 

分享数据记录 

|**参数名**|**类型**|**说明**|
|---|---|---|
|utd|string|统一数据类型,参考mobShare.ShareType|
|title|string|如果是文本、链接等内容,填入title标识其标题。|
|label|string|标识当前数据记录类型的标签,缺省为类型相应的标 签,如图片、视频等。|
|description|string|数据记录的描述。|
|thumbnail|Uint8Array|数据记录缩略图|
|uri|string|数据记录的uri(content和uri二者至少有一个不为 空)。|
|content|string|数据记录内容,包括文本/html/url(content和uri二者 至少有一个不为空)。|
|extraData|Record<string, string |
number | boolean |
Array<string | number |
boolean>>|扩展数据,用于向目标应用/设备分享自定义的扩展内
容。|
|imagePath|string|本地图片文件绝对路径|
|imageUrl|string|网络图片url地址|
|imageUri|string|本地图片文件uri地址|
|imageUris|string[]|多个本地图片文件uri地址|
|videoPath|string|本地视频文件绝对路径|
|videoUrl|string|网络视频url地址|
|videoUri|string|本地视频文件uri地址|
|videoCoverPath|string|视频封面图片文件绝对路径|
|videoCoverUrl|string|视频封面图网络图片url地址|
|videoCoverUri|string|视频封面图片文件uri地址|
|imageData|Uint8Array|图片数据|
|imageDataString|string|图片数据string格式|
|miniProgramUserName|string|拉起的小程序的原始id|
|miniProgramPath|string|拉起小程序页面的可带参路径,不填默认拉起小程序首 页,对于小游戏,可以只传入query部分,来实现传 参效果,如:传入"?foo=bar"|
|miniProgramType|number|拉起小程序的类型0-正式版1-开发版2-体验版,不填 默认为正式版(0)|

## **分享控制器配置项** 

### **mobShare.ShareControllerOptions** 

分享视图选项 

|**名称**|**类型**|**必填**|**说明**|
|---|---|---|---|
|anchor|mobShare.ShareControllerAnchor |
string|否(2in1、tablet设备必
填)|锚点、组件id,在2in1/tablet设备中,此字段为
必填项|
|previewMode|mobShare.SharePreviewMode|否|预览的模式,缺省为卡片模式|
|selectionMode|mobShare.SelectionMode|否|选择的模式,缺省为单选模式|

### **mobShare.SharePreviewMode** 

分享预览模式:卡片模式、预览图模式 

|**类型**|**值**|**说明**|
|---|---|---|
|DEFAULT|0|默认模式(缩略图卡片)|
|DETAIL|1|详细预览图模式|

### **mobShare.SelectionMode** 

|**类型**|**值**|**说明**|
|---|---|---|
|SINGLE|0|单选模式,传入一个记录则单传,多个则n选1,|
|BATCH|1|批量模式|

### **mobShare.ShareControllerAnchor** 

分享悬浮窗视图依附锚点,分享面板会根据屏幕大小选择是否悬浮于指定的位置显示悬浮窗,例如,手机类设备屏 幕宽度较小时,则不会以悬浮形态展示,而是以模态形式/弹窗形式显示。 

在2in1&tablet类型屏幕规格较大的设备中,必须指定锚点,否则会产生非法参数异常。 

|**名称**|**类型**|**必填**|**说明**|
|---|---|---|---|
|windowOffset|Offset|是|相对锚点的窗体偏移值。|
|size|Size|否|锚点矩形的尺寸,缺省时,锚点是一个点,即宽高都为0。|

### **mobShare.Offset** 

可以设置的相对锚点的窗口偏移值 

|**名称**|**类型**|**必填**|**说明**|
|---|---|---|---|
|x|number|是|位置的坐标x。|
|y|number|是|位置的坐标y。|

### **mobShare.Size** 

锚点矩形的尺寸,缺省时,锚点是一个点,即宽高都为0。 

|**名称**|**类型**|**必填**|**说明**|
|---|---|---|---|
|width|number|是|定义宽度属性。|
|height|number|是|定义高度属性。|
