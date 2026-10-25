# 360 智语即时通讯 SDK 接口文档 

本文档主要介绍 360 智语 HarmonyOS NEXT 版本 UI-SDK 集成方式。 

UI-SDK 使用 ArkTS 语言进行编码,目前包含会话列表、聊天、组织架 构等页面,适用于鸿蒙系统 API>=14(5.0.2) 。 

一、导入 SDK 

# 1 、手动导入 SDK 

UI-SDK 目前只支持手动导入 SDK 

创建 entry/libs 目录,将 ccsdk_ui_xxx.har (集成中替换为具体 har 文件 名)放入其中。 

entry 找到 oh-package.json5 文件, dependencies 字段内增加 har 依赖 

{ 

"name": "entry", 

"version": "1.0.0", 

"description": "Please describe the basic information.", 

"main": "", 

"author": "", 

"license": "", 

"dependencies": { 

"@cc/uisdk": "file:libs/ccsdk_ui_xxx.har" // @cc/uisdk 不可更改, xxx 请替换为具体 har 文件名 

} 

} 

添加成功后 点击 DevEco Studio 右上角提示 Sync Now 

安装 SDK 成功后,可以在项目根目录的 oh_modules/.ohpm/ 中找到 @cc/uisdk 

添加 SDK 依赖权限 

需要添加如下权限 

权限名称 

权限说明 

使用目的 

ohos.permission.GET_NETWORK_INFO 

获取网络信息 

网络变化之后获取网络信息,进行重连 

ohos.permission.INTERNET 

使用网络 

连接 IM 、收发消息等需要网络连接 

ohos.permission.MICROPHONE 

访问麦克风设备 

用于录制语音消息 

ohos.permission.PRIVACY_WINDOW 

设置应用窗口为隐私模式 

用于部分页面截屏管控 

配置 useNormalizedOHMUrl 

UI-SDK 是以字节码方式导出的 har 包,在工程的 build-profile.json5 中 useNormalizedOHMUrl 字段必须设置为 true 。 

{ 

"app": { 

... 

"products": [ 

{ 

"buildOption": { 

"strictMode": { 

"useNormalizedOHMUrl": true // 此处必现设置为 true 

} 

} 

} 

] 

} 

} 

二、初始化 

在使用 SDK 其它功能前,必须先进行初始化。 

在 UIAbility 的 onWindowStageCreate() 方法中,调用初始化方法, 可以参考 demo EntryAbility 

onWindowStageCreate(windowStage: window.WindowStage): void { 

// 1. 配置初始化 

CCKit.getInstance().init(this, windowStage); 

windowStage.loadContent('pages/Index', (err, data) => { 

if (err.code) { 

hilog.error(0x0000, 'testTag', 'Failed to load the content. Cause: %{public}s', JSON.stringify(err) ?? ''); 

return; 

} 

// 2. UIAbilityContext 初始化成功后再次进行初始化 

CCKit.getInstance().initAfterLoadContent(windowStage); 

}); 

} 

在调用 UI-SDK 登录成功后,由于 UI-SDK 内部页面跳转使 用 Navigation , 需要初始化 UI-SDK 内部路由 NavPathStack ,可以参 考 demo HomePage 

// 定义 NavPathStackprivate ccsdkPathStack: NavPathStack = new NavPathStack();private context: common.UIAbilityContext = this.getUIContext().getHostContext() as common.UIAbilityContext; 

aboutToAppear(): void { 

// 注册 NavPathStack 便于 ccsdk 内部跳转 

CCKit.getInstance().initNavPath(this.context, this.ccsdkPathStack); 

} 

// 使用 Navigation 组件 

Navigation(this.ccsdkPathStack) {} 

.mode(NavigationMode.Stack) 

.navDestination(this.PagesMap) 

监听错误事件( onFatalError ) 

监听用户错误事件,全局调用一次即可,建议在初始化完成后立即注 册。 

当服务端主动断开当前用户的登录状态时触发,例如:密码被修改、 账号被停用等情况。收到回调后,建议对接方清理本地状态并跳转到 登录页面。 

event 枚举值说明: 

部分枚举值 

含义 

1 

密码修改 

2 

员工停用 

3 

员工删除 

4 

强制修改密码 

10 

被踢下线 

11 

服务器透传 

CCKit.getInstance().onFatalError((event, reason) => { 

# // 处理错误事件,例如跳转登录页 

console.log(' 错误原因: ', reason); 

// 建议清理本地状态并跳转登录页 

}); 

三、登录 / 登出 

# 登录 

使用 UI-SDK 使用 360 智语账号进行登录,可以参考 demo LoginPage 

async login() { 

// 此处示例为账密登录 , 1 表示账密登录 5 oauth 登录 

// login 为异步结果,结果成功时表示登录成功,失败时,需要处理 框架错误 Error 以及 SDK 内部自定义错误,可以使用 SDK 内部提供的错 误类 CCSdkError 

await CCKit.getInstance().login(this.account, this.password, 1, this.server); 

router.replaceUrl({ url: 'pages/HomePage' }) 

} 

# 轻登录 

轻登录是指在用户已经登录过的情况下,使用登录后保存的缓存信息 以及 token ,自动进行与服务器的连接,达到用户登录一次后续一直 可以使用的目的。 具体实现可以参考 demo Index 

CCKit.getInstance().autoLogin() 

.then(() => { 

// 轻登录成功 

promptAction.showToast({ message: " 轻登录成功 " }) 

router.replaceUrl({ url: 'pages/HomePage' }) 

}) 

.catch((err: CCSdkError) => { 

# // 轻登录失败 

router.replaceUrl({ url: 'pages/LoginPage' }) 

}); 

# 登出 

退出登录状态,回到登录页面进行重新登录情况下,需要添加如下代 码。可以参考 demo MinePage 

// logout() 传参 true 表示 退出失败时,也清理缓存。适用于不管退 出接口结果如何,都处理为退出成功。 

CCKit.getInstance().logout(true).then((result) => { 

if (result) { 

router.replaceUrl({ url: 'pages/LoginPage' }) 

router.clear(); 

} 

}).catch((err:Error) =>{ 

# // 退出请求失败,但也清理缓存数据 

router.replaceUrl({ url: 'pages/LoginPage' }) 

router.clear(); 

}); 

# 四、会话管理 

# 集成会话页面 

目前提供了 ConversationListPage 组件用于显示会话列表,可以参考 demo HomePage ,以 tab 的形式集成到项目中,也可以自定义 Page 集 成组件的方式。 

build() { 

Column() { 

ConversationListPage() 

} 

} 

消息未读数管理 

获取未读数 

// 返回缓存中的未读总数 <0 表示 未读数不显示,只展示小红点 0 表示未读数为 0 

CCKit.getInstance().getUnreadCount() 

监听未读数变化 

# // unreadListenerId 监听事件 id 

this.unreadListenerId = CCKit.getInstance().onUnreadCountChange((unreadCount) => { 

# // 接收消息未读数 

# }) 

注意:调用了监听未读数变化,需要在页面生命周期结束时停止监 听 CCKit.getInstance().offUnreadCountChange(listenerId: string | undefined) 

# 创建群聊 

// @param includeSelf boolean 是否包含自己 // @param initSelectedUids 初始选中的用户,传入用户 uid 数组。如果 includeSelf=true 那么初始会选中自己 // @param disableSelectUids 不可选择的用户,传入用户 uid 数组。如果 includeSelf=true 那么自 己将不能被点击 

CCKit.getInstance().createGroup(true); 

五、用户信息 

获取缓存内自己的用户信息 

// 获取缓存内的用户信息,注意判空 

CCKit.getInstance().getCacheMyUserInfo(); 

获取缓存内的用户信息 

// 获取缓存内的用户信息,注意判空 // 参数 uid 目标用户 uid 

CCKit.getInstance().getCacheUserInfo(uid) 

# 获取用户信息 

// 异步操作,获取用户信息,注意判空,当缓存内没有数据时,会去 服务器请求用户数据,服务器用户信息通过 onUserInfoChange 返 回 // 参数 uid 目标用户 uid 

CCKit.getInstance().getUserInfo(uid) 

# 监听用户信息变化 

监听用户信息变化,当获取了服务器用户信息数据,或者其他修改了 用户信息的操作,都将触发回调。 需要注意在页面销毁时 移除监听 

// 参数 uid 目标用户 uid// 参数 callback 获取服务器用户信息结果回 调,或者其他方式更新了用户信息 let listenerId = CCKit.getInstance().onUserInfoChange(uid, (userInfo) => { 

}) 

# 删除用户信息监听 

// listenerId 用户信息监听事件 id// 参数 uid 目标用户 uid 

CCKit.getInstance().offUserInfoChange(listenerId, uid) 

# 页面跳转 

# 跳转消息页面 

// 第一个参数 uid 用户 id// 第二个参数 会话类型 1 单聊、 2 群聊、 3 公众号 

CCKit.getInstance().pushPathByName(NavigationPath.chatPage, new ChatPageParams(this.userInfo.uid, 1)); 

查看用户详细信息 

// uid 目标用户 uid 

CCKit.getInstance().pushPathByName(NavigationPath.userDetailPage, uid); 

# 六、日志管理 

SDK 提供内部 sdk 日志输出,包含发送到会话,通过日志目录获取日志 文件。 SDK 内部的日志包含 业务日志、 crash 日志。 发送到会话 

private context: common.UIAbilityContext = this.getUIContext().getHostContext() as common.UIAbilityContext; 

CCKit.getInstance().sendLogToChat(this.context) 

获取日志所在目录 

let logDir = CCKit.getInstance().getLogFolder(); 

七、其他 

# 扫一扫 

对接方可自行集成扫一扫功能,如果需要使用 SDK 内部业务处理扫码 结果,可以调用以下代码。 SDK 内部处理逻辑如下: 

当检测到是 360 智语小程序协议,那么会自动跳转到小程序页面; 

如果是 url ,那么会使用内置的 webview 打开; 

如果是群聊二维码,那么会跳转去申请加群; 

如果是用户二维码,那么会跳转用户详情; 

其他文本内容,会显示扫码结果页。 

// qrCodeResult 扫码结果 

CCKit.getInstance().handleQrScanResult(qrCodeResult); 

离线推送消息的点击 

当收到服务器推送的离线推送,内容为 IM 消息时,此时 点击离线推 送的消息通知,可以跳转到对应的聊天页面。 需要在 Ability 上进行 处理。 

onCreate 接收 want 对象 

在 onWindowStageCreate loadContent() 回调成功后处理 Want 

unHandledWant?: Want; 

onCreate(want: Want, launchParam: AbilityConstant.LaunchParam): void { 

this.unHandledWant = want 

} 

async onWindowStageCreate(windowStage: window.WindowStage): Promise<void> { 

windowStage.loadContent(RoutePath.PATH_SPLASH, this.storage, (err, data) => { 

if (this.unHandledWant) { 

CCKit.getInstance().handleWant(this.unHandledWant); 

this.unHandledWant = undefined 

} 

}); 

} 

链接点击拦截( onLinkClick ) 

注册链接点击拦截回调。当 SDK 内部发生链接点击时,会优先调用 此回调: 返回 true 表示外部已消耗该事件, SDK 不再进行内部路由处理; 

返回 false 表示继续执行 SDK 内部逻辑。 

传入 undefined 可取消已注册的回调。 

// 注册拦截 

CCKit.getInstance().onLinkClick((url) => { 

if (url.startsWith('myapp://')) { 

// 自定义处理逻辑 

return true; // 阻止 SDK 内部处理 

} 

return false; // 继续 SDK 内部处理 

}); 

// 取消注册 

CCKit.getInstance().onLinkClick(undefined); 

八、 API 汇总 

# 初始化相关 

init 

SDK 初始化,在 EntryAbility 的 onWindowStageCreate 中调用。 

init(ability: UIAbility, windowStage: window.WindowStage): void 参数: 

ability: UIAbility - UIAbility 实例 

windowStage: window.WindowStage - WindowStage 实例 

# 使用示例: 

async onWindowStageCreate(windowStage: window.WindowStage): Promise<void> { 

// 在 EntryAbility onWindowStageCreate() 中调用 

CCInitManager.init(this, windowStage); 

} 

initAfterLoadContent 

在 sdk 初始化后调用,在 EntryAbility 的 onWindowStageCreate 中 windowStage.loadContent() 成功后的回调中调用。 

initAfterLoadContent(windowStage: window.WindowStage): void 

# 参数: 

windowStage: window.WindowStage - WindowStage 实例 

使用示例: 

async onWindowStageCreate(windowStage: window.WindowStage): Promise<void> { 

windowStage.loadContent(RoutePath.PATH_SPLASH, this.storage, (err, data) => { 

// 在 EntryAbility onWindowStageCreate() 内 windowStage.loadContent() 成功后的回调中调用 

CCInitManager.initAfterLoadContent(windowStage); 

} 

} 

initNavPath 

初始化 NavPathStack ,仅需要初始化一次,将 NavPathStack 对象与 Ability 上下文关联,用于 sdk 内部页面路由管理。 

initNavPath(abilityContext: common.UIAbilityContext, navPathStack: NavPathStack): void 

参数: 

abilityContext: common.UIAbilityContext - UIAbility 上下文对象 

navPathStack: NavPathStack - 导航路径栈对象 

onFatalError 

监听用户错误事件,全局调用一次即可。 

当服务端主动断开当前用户的登录状态时触发,例如:密码被修改、 账号被停用等情况。收到回调后,建议对接方清理本地状态并跳转到 登录页面。 

onFatalError(callback?: (event: number, reason: ResourceStr) => void): void 

参数: 

callback?: (event: number, reason: ResourceStr) => void - 事件回 

# 调函数,可选 

event: number - 原因枚举值: 1= 密码修改、 2= 员工停用、 3= 员工 删除、 4= 强制修改密码、 10= 被踢下线、 11= 服务器透传等 

reason: ResourceStr - 错误原因的可读描述文本,可直接用于界面展 示 

使用示例: 

CCKit.getInstance().onFatalError((event, reason) => { 

// 处理错误事件,例如跳转登录页 

console.log(' 错误原因: ', reason); 

}); 

登录相关 

autoLogin 

轻登录,主要用于当用户已经通过账号密码方式登录成功过,本地存 在登录缓存的情况下,使用此登录方式进行轻登录。 

async autoLogin(): Promise<void> 

返回值: 

Promise<void> - 如果没有抛出异常,表示轻登录成功 

异常: 

CCSdkError - SDK 内部错误, BusinessError 子类, sdk 内部错误码请 参考 CCSdkErrorCode 

Error - 系统框架错误 

备注:异步调用 

login 

用户登录。 

async login(account: string, password: string, authType: number, server: string): Promise<void> 

参数: 

account: string - 账号 

password: string - 密码或 oauth 

authType: number - 登录类型, 1 账号密码; 5 oauth 登录 

server: string - 服务器地址,例如 https://www.xxx.com:8282 

返回值: 

Promise<void> - 如果没有抛出异常,表示登录成功 

异常: 

CCSdkError - SDK 内部错误, BusinessError 子类, sdk 内部错误码请 参考 CCSdkErrorCode 

备注:异步调用 

logout 

登出。 

async logout(failStillClear: boolean = false): Promise<boolean> 

参数: 

failStillClear: boolean - true 表示登出失败时也清理缓存数据, false 则 不清理。默认 false 

返回值: 

Promise<boolean> - true 登出成功, false 登出失败 

异常: 

Error - 系统框架错误 

# 备注: 

# 异步任务 

# 需要对接方登出后自行处理路由跳转 

# 路由导航相关 

pushPathByName 

# 通过页面名称进行页面跳转(压栈操作)。 

pushPathByName(navPath: string, param?: number | string | object | Map<string, string>, callback?: Callback<PopInfo>): void 

# 参数: 

navPath: string - 目标页面名称 

param?: number | string | object | Map<string, string> - 可选参 数,传递给目标页面的数据对象,不同页面不同的参数对象 

callback?: Callback<PopInfo> - 可选参数,页面回调 

使用示例: 

# // 跳转到用户详情页 

CCKit.getInstance().pushPathByName(NavigationPath.userDetailPage, uid); 

# // 跳转聊天页 

CCKit.getInstance().pushPathByName(NavigationPath.chatPage, new ChatPageParams(uid, 1)); 

replacePathByName 

# 通过页面名称替换当前页面(栈顶替换)。 

replacePathByName(navPath: string, param?: number | string | object | Map<string, string>): void 

# 参数: 

navPath: string - 目标页面名称,需与路由配置中的名称一致 

param?: number | string | object | Map<string, string> - 可选参 数,传递给目标页面的数据对象(建议使用 JSON 格式) 

异常: 

当 pageName 未注册或导航栈为空时将抛出路由异常 

消息未读数相关 

getUnreadCount 

返回缓存中的未读总数。 

getUnreadCount(): number 

返回值: 

number - 未读数, <0 表示未读数不显示,只展示小红点; 0 表示未 读数为 0 

onUnreadCountChange 

监听消息未读数变化。 

onUnreadCountChange(callback: Callback<number>): string | undefined 

参数: 

callback: Callback<number> - 消息变更回调函数,接收最新未读数 返回值: 

string | undefined - 监听事件 id 

offUnreadCountChange 

移除监听消息未读数变化。 

offUnreadCountChange(listenerId: string | undefined): void 

参数: 

listenerId: string | undefined - 监听事件 id 

群聊相关 

createGroup 

创建群聊,打开选人控件页面,进行选择用户,确定选中的用户后将 进行创建群聊并跳转到群聊聊天页面。 

createGroup(includeSelf: boolean = true, initSelectedUids: string[] = [], disableSelectUids: string[] = []): void 

参数: 

includeSelf: boolean - 是否包含自己,默认为 true 

initSelectedUids: string[] - 初始选中的用户,传入用户 uid 数组。如 果 includeSelf=true 那么初始会选中自己 

disableSelectUids: string[] - 不可选择的用户,传入用户 uid 数组。如 果 includeSelf=true 那么自己将不能被点击 

用户信息相关 

getCacheMyUserInfo 

获取缓存内自己的用户信息。 

getCacheMyUserInfo(): UserInfo | undefined 

返回值: 

UserInfo | undefined - 用户信息,可能为空数据,注意判空 

getCacheUserInfo 

只获取本地缓存的用户数据。 

getCacheUserInfo(uid: string): UserInfo | undefined 

参数: 

uid: string - 用户 uid 

返回值: 

UserInfo | undefined - 用户信息,可能为空数据,注意判空 

getUserInfo 

获取用户数据,先取本地缓存,如果没有,则会获取远程数据,远程 用户数据通过 onUserInfoChange 返回。 

getUserInfo(uid: string): UserInfo | undefined 

参数: 

uid: string - 用户 uid 

返回值: 

UserInfo | undefined - 用户信息,可能为空数据,注意判空 

onUserInfoChange 

监听用户信息变化。 

onUserInfoChange(uid: string, callback: Callback<UserInfo>): string | undefined 

参数: 

uid: string - 用户 uid 

callback: Callback<UserInfo> - 监听回调 

返回值: 

string | undefined - 返回此时监听 id , undefined 表示监听失败 

offUserInfoChange 

删除用户信息监听。 

offUserInfoChange(listenerId: string | undefined, uid: string): void 

参数: 

listenerId: string | undefined - 监听 id 

uid: string - 用户 id 

扫码和推送相关 

handleQrScanResult 

处理扫码结果。 

handleQrScanResult(qrcode: string): void 

参数: 

qrcode: string - 二维码结果 

备注: 

当检测到是 360 智语小程序协议,那么会自动跳转到小程序页面 如果是 url ,那么会使用内置的 webview 打开 如果是群聊二维码,那么会跳转去申请加群 如果是用户二维码,那么会跳转用户详情 其他文本内容,会显示扫码结果页 

handlePush 

处理离线推送的点击,跳转到对应的聊天页面。 

handlePush(want: Want): void 

参数: 

want: Want - 推送 Intent 

onLinkClick 

注册链接点击拦截回调。当 SDK 内部发生链接点击时,会优先调用 此回调。传入 undefined 可取消已注册的回调。 

onLinkClick(callback?: (url: string) => boolean): void 

参数: 

callback?: (url: string) => boolean - 链接点击回调,可选 url: string - 被点击的链接地址 

返回 true :外部已消耗该事件, SDK 不再进行内部路由处理 返回 false :继续执行 SDK 内部处理逻辑 

使用示例: 

// 注册拦截 

CCKit.getInstance().onLinkClick((url) => { 

if (url.startsWith('myapp://')) { 

// 自定义处理逻辑 

return true; // 阻止 SDK 内部处理 

} 

return false; // 继续 SDK 内部处理 

}); 

# // 取消注册 

CCKit.getInstance().onLinkClick(undefined); 

日志相关 

getLogFolder 

获取 sdk 内部日志存储路径。 

getLogFolder(): string 

返回值: 

string - 文件目录路径 

sendLogToChat 

发送 sdk 日志给聊天对象。 

async sendLogToChat(context: common.UIAbilityContext): Promise<void> 

参数: 

context: common.UIAbilityContext - 上下文对象 

返回值: 

Promise<void> 

备注: 

调用后会收集最近日志文件,文件数不超过 30 条,包含 sdk 内部日志 文件、 crash 文件 内部增加了 try-catch 处理,可直接调用 

异步请求
