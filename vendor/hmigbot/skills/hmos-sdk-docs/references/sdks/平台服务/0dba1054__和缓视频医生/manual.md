# 和缓视频医生SDK接入文档 

#### 和缓视频医生 SDK 接口文档 

。 目录 。1. 概述 1.1 产品介绍 1.2 核心功能 1.3 适用场景 。 2. 安装配置 2.1 安装 SDK 2.2 配置 module.json5 2.3 导入 SDK 。 3. 核心接口 3.1 初始化 SDK 3.2 用户登录 3.3 用户登出 3.4 直接呼叫视频医生 3.5 进入信息流页面 3.6 问诊详情页面 

3.7 配置视频中邀请家人(高级功能) 

。 4. 代码示例 

4.1 完整接入流程 4.2 最小可用示例 。 5. 常见问题 5.1 SDK 初始化失败 5.2 登录失败 5.3 呼叫医生没有响应 5.4 后台通话中断 

5.5 无法进入信息流 

1 

## 1. 概述 

### 1.1 产品介绍 

和缓视频医生 SDK 是—款面向 Open平台的医疗视频问诊软件开发工具包,为开发者提供便捷的在 线问诊、音视频通话、信息流管理等功能。 

### 1.2 核心功能 

- . 用户登录认证 

- . 视频医生直接呼叫 

- . 

   - 信息流管理 

- . 问诊详情查看 

- . 视频中邀请家人(需开通权益) 

### 1.3 适用场景 

- . 在线问诊应用 

- . 医疗健康类应用 

- . 

- . 

- 企业健康管理平台 

- 保险健康服务 

## 2. 安装配置 

### 2.1 安装 SDK 

步骤 1 :配置 ohpm 环境 

参考官方文档:安装 Openohpm 包步骤 2 : 

安装依赖包 

#### 在项目根目录执行以下命令: 

ohpm install @hh-medic/hhsdk 

### 2 .2 配置 module.json5 

为确保音视频通话在应用进入后台时正常运行,需要在 module.json5 配置文件中添加 VOIP 后台模 式。 

配置示例: 

2 

{ 

"module": { "name" : "entry", "type" : "entry", "abilities": [ { "name" : "EntryAbility" , "backgroundModes" : [ "voip" ] } ] } } 

配置说明: 

参数 类型必填 说明 backgroundModes Array 是 后台长时任务类型 voip String 是 音视频通话模式 

### 2.3 导入 SDK 

在需要使用 SDK 的文件中导入: 

**import** { HHDoctor } **from** '@hh-medic/hhsdk ' ; 

## 3. 核心接口 

### 3.1 初始化 SDK 

接口定义: 

HHDoctor.init(options: HHSDKOptions) : void 

参数说明: 

参数名 类型 必填 说明 

options HHSDKOptions 是 初始化配置对象 

#### HHSDKOptions 对象: 

属性 类型 必填 说明 sdkProductId number 是 SDK 产品 ID(联系商务获取) isDev boolean 是 是否为测试环境 

代码示例: 

3 

和缓视频医生 HarmonySDK接又文档 

2025/11/10 12:57 

// 初始化 SDK **let** options = **new** HHSDKOptions() options.sdkProductId = 12345 // 替换为实际的产品 ID options.isDev = **true** // 测试环境设为 true,生产环境设为 false HHDoctor.init(options) 

注意事项: - ⚠ 必须在使用其他接口前完成初始化 - ⚠ sdkProductId 需联系和缓商务获取 - ⚠ 生 产环境务必将 isDev 设置为 false 

### 3.2 用户登录 

#### 接口定义: 

HHDoctor.login(userToken: string, listener: HHLoginListener) : void 

参数说明: 

参数名 类型 必填 说明 userToken string 是 用户安全令牌(由和缓提供) listener HHLoginListener 是 登录回调监听器 

HHLoginListener 回调: 

方法 参数 说明 onSuccess 无 登录成功回调 onFail code: number, msg: string 登录失败回调 

#### 代码示例: 

HHDoctor.login(userToken, { onSuccess: () **=>** { console.log( I登录成功 I) // 执行登录成功后的逻辑 }, onFail: (code: number, msg: string) **=>** { ` console.error( 登录失败 : ${code} - ${msg}`) // 处理登录失败 } }) 错误码说明: 错误码 说明 处理建议 401 userToken 无效检查 token 是否正确 403 权限不足 联系商务确认权限 500 服务器错误 稍后重试 

#### 错误码说明: 

3.3 用户登出 

4 

#### 接口定义: 

HHDoctor. logOut() : void 

#### 参数说明: 

无参数 

#### 代码示例: 

HHDoctor. logOut( ) ' ' console.log( 已退出登录 ) 

注意事项: - ⚠ 登出后需要重新登录才能使用其他功能 - ⚠ 建议在应用退出或用户主动登出时调用 

### 3.4 直接呼叫视频医生 

接口定义: 

HHDoctor. call(userToken: string, listener: HHCallListener | null) : void 

参数说明: 

参数名 类型 必填 说明 userTokenstring 是 用户安全令牌 listener HHCallListener 否 呼叫事件回调监听器 

#### HHCallListener 回调方法: 

方法 参数 说明 onStart orderId: string 启动呼叫,返回订单 ID onCalling 无 呼叫中(医生接听前) onChatting 无 通话中(医生已接听) onLineUp 无 需要排队等待 onHangup chatTime: number 通话结束,返回通话时长(秒) onCancel 无 取消呼叫 onFail code: number, msg: string 呼叫失败 onLoadDoctordoctor:HHCallInfo 分配医生成功 

#### HHCallInfo 对象: 

属性 类型 说明 doctorId string 医生 ID doctorName string 医生姓名 hospitalName string 医院名称 

5 

属性 类型 说明 

departmentName string 科室名称 title string 职称 avatarUrl string 医生头像 URL 

#### 代码示例: 

HHDoctor.call(userToken, { onStart: (orderId: string) **=>** { ` console.log( 呼叫启动,订单ID: ${orderId}`) }, onCalling: () **=>** { console.log( I正在呼叫医生 ... I) }, onChatting: () **=>** { console.log( I通话中 I) }, onLineUp: () **=>** { console.log( I当前需要排队等待 I) }, onHangup: (chatTime: number) **=>** { ` ` console.log( 通话结束,通话时长 : ${chatTime}秒 ) }, onCancel: () **=>** { console.log( I已取消呼叫 I) }, onFail: (code: number, msg: string) **=>** { ` console.error( 呼叫失败 : ${code} - ${msg}`) }, onLoadDoctor: (doctor: HHCallInfo) **=>** { ` console. log( 已分配医生 : ${ doctor. doctorName}` ) } }) 

### 3.5 进入信息流页面 

接口定义: 

HHDoctor. home() : void 

参数说明: 

无参数 

代码示例: 

6 

和缓视频医生 HarmonySDK接又文档 

2025/11/10 12:57 

// 必须先登录 HHDoctor . login( userToken 卩 { onSuccess : () **=>** { // 登录成功后进入信息流 HHDoctor .home () } 卩 onFail : ( code 卩 msg) **=>** { console . error ( ' 登录失败,无法进入信息流' ) } }) 

注意事项: - ⚠ 调用此接口前必须先完成登录 - ⚠ 信息流页面展示历史问诊记录和消息 

### 3.6 问诊详情页面 

接口定义: 

HH Doctor . medic Detail(userToken : string 卩 mid : string) : void 

参数说明: 

参数名 类型必填 说明 userToken string 是 用户安全令牌 mid string 是 病历存档 ID 

#### 代码示例: 

// 查看指定问诊记录的详情 **const** mid = ' M20251110001 ' // 病历存档ID HHDoctor . medic Detail(userToken mid) 

注意事项: - ⚠ mid 由和缓视频医生提供方同步到接入方 - ⚠ 需要确保 mid 存在且用户有权限查看 

### 3.7 配置视频中邀请家人(高级功能) 

适用版本: v1.0.7 及以上 

前置条件: 1. 联系和缓商务开通”视频中邀请家人 ”权益 2. 接入微信 SDK 

接口定义: 

HH Doctor . set Wx Mini Invite Handler (handler : HHWX Mini InviteApi) : void 

参数说明: 

参数名 类型 必填 说明 

handler HHWXMiniInviteApi 是 微信小程序邀请处理器 

HHWXMiniInviteApi 接口: 

7 

说明 

参数 

方法 

onInvite path: string, wxAppId: string 拉起微信小程序回调 

完整代码示例: 

// 1. 实现 HHWXMiniInviteApi 接口 **class** HHInviteWXMini **implements** HHWXMiniInviteApi { /** * 邀请家人回调 * **@param path** 小程序路径 * **@param wxAppId** 微信小程序 AppId */ onInvite(path: string, wxAppId: string) : void { ` console.log( 拉起小程序 : ${wxAppId}, 路径 : ${path}`) // 调用微信SDK 拉起小程序 // 示例(具体实现依赖微信 SDK): // WXMiniProgram . launch({ // appId: wxAppId, // path: path // }) } } // 2 . 创建处理器实例 **export const** hhInviteMini = **new** HHInviteWXMini( ) // 3 . 向和缓SDK 中添加监听 HHDoctor.setWxMiniInviteHandler(hhInviteMini) 

## 4. 代码示例 

### 4.1 完整接入流程 

**import** { HHDoctor, HHSDKOptions } **from** I@hh-medic/hhsdkI **export class** VideoConsultationService { **private** userToken: string = II /** * 初始化 SDK */ initSDK() { **let** options = **new** HHSDKOptions() options.sdkProductId = 12345 // 替换为实际 ID options.isDev = **true** HHDoctor.init(options) console.log( ISDK 初始化完成 I) } /** * 登录 */ login(token: string) { **this** .userToken = token 

8 

HHDoctor . login (token 卩 { onSuccess : () **=>** { console . log( I登录成功I ) **this** . on LoginSuccess() } 卩 onFail : ( code 卩 msg) **=>** { ` console . error (`登录失败: ${code} - ${msg} ) **this** .on Login Fail(code 卩 msg) } }) } /** * 开始视频问诊 */ start VideoCall () { HHDoctor .call ( **this** . userToken 卩 { on Start : ( order Id) **= >** { ` console . log ( `订单创建: ${ order Id } ) } 卩 onLoad Doctor : (doctor) **=>** { ` console . log (`医生已分配: ${doctor . doctor Name} ) **this** .show Doctor Info (doctor) } 卩 on Ca lli ng : () **= >** { **t hi s** . show Ca lling UI () } 卩 on Chatting : () **=>** { **this** . show Chatting UI() } 卩 on Hangup : (chat Time) **=>** { console . log( ` 通话结束,时长: $ { chatTime} 秒` ) **this** . show Call End UI (chat Time) } 卩 onFail : ( code 卩 msg) **=>** { **this** .showError (code 卩 msg) } }) } /** * 查看历史记录 */ view History() { HHDoctor .home () } /** * 查看问诊详情 */ view Detail ( mid : string ) { HHDoctor . medic Detail ( **this** . userToken 卩 mid) } /** * 登出 */ log out() { HH Doctor . logOut() **this** . userToken = II 

9 

' ' console.log( 已登出 ) 

} 

// 以下为业务相关方法,需根据实际情况实现 **private** onLoginSuccess() { /* . . . */ } **private** onLoginFail(code: number, msg: string) { /* . . . */ } **private** showDoctorInfo(doctor: any) { /* . . . */ } **private** showCallingUI() { /* . . . */ } **private** showChattingUI() { /* . . . */ } **private** showCallEndUI(chatTime: number) { /* . . . */ } **private** showError(code: number, msg: string) { /* . . . */ } } 

### 4.2 最小可用示例 

**import** { HHDoctor, HHSDKOptions } **from** '@hh-medic/hhsdk ' // 1 . 初始化 **let** options = **new** HHSDKOptions() options. sdkProductId = 12345 options.isDev = **true** HHDoctor.init(options) 

// 2 . 登录 **const** userToken = 'your-user-token ' HHDoctor.login(userToken, { onSuccess: () **=>** console.log( '登录成功 '), onFail: (code, msg) **=>** console.error( '登录失败 ', code, msg) }) 

// 3 . 呼叫医生 HHDoctor.call(userToken, **null** ) 

## 5. 常见问题 

### 5.1 SDK 初始化失败 

问题:调用 init() 后出现错误 

解决方案: - 检查 sdkProductId 是否正确 - 确认网络连接正常 - 查看是否正确导入 SDK 

### 5.2 登录失败 

问题:调用 login() 后返回失败 

解决方案: - 确认 userToken 是否有效 - 检查是否已完成 SDK 初始化 - 联系技术支持验证 token 

### 5.3 呼叫医生没有响应 

问题:调用 call() 后没有反应 

- - - 解决方案: 确认是否已登录 检查 module.json5 中是否配置了 voip 模式 验证权限配置是否正确 

10 

### 5.4 后台通话中断 

问题:应用进入后台后通话中断 

- - - 解决方案: 检查 module.json5 中的 backgroundModes 配置 确保 voip 模式已正确配置 检查 系统权限设置 

### 5.5 无法进入信息流 

问题:调用 home() 无响应 

- - - 解决方案: 确认已成功登录 检查网络连接 查看控制台日志 

文档版本: v1.1.2 

最后更新: 2026年0 4 月16日 

维护团队:和缓医疗技术团队 

© 2026�和缓医疗科技有限公司版权所有 

11
