**IM 融云即时通讯 ( ) SDK 客户端** 快速 入门 HarmonyOS IMKit SDK 

# **鸿蒙 IMKit 架构** 

IMKit 分为如下核心服务 

ConnectionService : 连接服务。 IMKit 的连接服务功能单薄,主要是做 IM 连接状态的监听,方便 UI 做连接状态的展示。 实际的 IM 连接,由 IMLib 负责。 

MessageService: 消息服务。IMKit 的消息服务主要用于 UI 页面,里面调用的各种方法会触发页面的各种监听方法。 IMLib 的消息相关方法并不会触发 UI 页面的各种监听。 

UserDataService:用户服务。和 iOS、Android 用户信息提供者相同的能力,用于从 App 获取用户信息刷新会话列表,聊 天页面的用户头像、名称等 

ConversationService:会话服务。主要处理聊天页面相关。功能涵盖: 

1. 会话配置 

2. 自定义消息与 provider 绑定 

3. 消息长按事件增加 

4. 各种聊天页面的事件监听 

5. 输入框 + 号扩展栏插件 

6. 会话的部分接口(如置顶、免打扰等) 

7. 聊天页面 UI 

ConversationListService:会话列表服务。主要处理会话列表页面相关。功能涵盖: 

1. 会话列表 provider 替换、移除 

2. 会话列表的事件监听 

3. 会话列表长按事件增加 

4. 会话列表页面 UI 

# **快速上手** 

本教程旨在帮助开发者快速了解和掌握 IMKit SDK (融云即时通讯 UI 库) 的基础集成流程与核心能力。通过本教程,您将完成 IMKit SDK 导入、初始化、建立连接、展示会话列表与会话页面、测试收发消息等全流程操作。 

### **环境要求** 

DevEco Studio NEXT Release(5.0.3.900) 及以上。 

- HarmonyOS SDK API 12 及以上。 

- 16 - 

手机系统版本号:NEXT.0.0.31。 

- 真机华为 Mate 系列。真机运行需要配置证书,详情参考鸿蒙的[签名指南]文档。 

- 模拟器。详情参考鸿蒙的[模拟器运行指南]文档。 

### **准备工作** 

1. 访问融云控制台,注册您的开发者账号。注册成功后,控制台自动在开发环境中为您创建一个应用。 

2. 在控制台的基本信息页,获取您的应用在开发环境的 AppKey。您可在基本信息页查看应用的信息,如 App Key、 App Secret、所属数据中心(默认为北京)。 

如您想自己创建应用,参考如何创建应用,并获取对应环境 App Key 和 App Secret。 

#### 提示 

每个应用均拥有两个不同的 App Key,分别对应开发环境与生产环境,且两个环境之间数据相互隔离。在您的 应用正式上线前,建议切换到生产环境的 App Key,以便完成上线前全流程测试和最终发布。 

### **导入 SDK** 

融云支持从 OpenHarmony三方库中心仓 添加依赖和将 IMKit 相关的 SDK 文件本地库导入应用工程两种集成方式。 

以下介绍如何使用从 OpenHarmony三方库中心仓 添加依赖方式将 IMKit SDK 导入工程: 

1. 在鸿蒙主工程 entry 目录中的 oh-package.json5 中添加 SDK 依赖,然后点击 "Sync Now"。 

#### **JSON** 

- 17 - 

// entry 目录中的 oh-package.json5 

{ 

"name": "entry", "version": "1.0.0", 

"description": "Please describe the basic information.", "main": "", "author": "", "license": "", "dependencies": { "@rongcloud/imkit" : "x.y.z", 

"@rongcloud/imlib" : "x.y.z" 

} } 

#### **注意** 

各个 SDK 的最新版本号可能不相同,具体 x.y.z 值可前往 融云官网 SDK 下载页面 或 OpenHarmony三方库中心 仓 查询。 

2. 安装 SDK 成功后,您可以在项目根目录的 **oh_modules/.ohpm/** 中找到融云 IMKit SDK。 

3. 添加 SDK 依赖权限 

#### 添加如下权限: 

- 18 - 

|权限名称|权限说明|使用目的|
|---|---|---|
|ohos.permission.GET_NETWORK_INFO|获取网络信息|网络变化之后获取网络信息,进行IM重连|
|ohos.permission.INTERNET|使用网络|连接IM、收发消息需要网络连接|
|ohos.permission.STORE_PERSISTENT_DATA|数据存储|消息数据库需要本地存储|
|ohos.permission.MICROPHONE|麦克风|提供发送语音消息功能,需要开启麦克风|
|详情参考鸿蒙应用权限配置文档。|||

4. 配置 useNormalizedOHMUrl 

#### 1.0.3 版本开始 SDK 支持字节码,为了支持字节码,app 需要在项目根路径配置 **useNormalizedOHMUrl** 。 

// app 根路径下的 build-profile.json5 { "app": { "products": [ { "buildOption": { "strictMode": { "useNormalizedOHMUrl": true } } } ] } } 

详细信息请参考 FAQ。 

### **初始化 SDK** 

IMKit SDK 初始化接口的调用需要引入对应的声明: 

#### **TypeScript** 

import { IMEngine } from '@rongcloud/imkit'; 

为确保您可以正常连接融云服务器和使用融云即时通讯服务(IM 服务),您须调用 init 方法初始化 IMKit SDK。初始化前, 您须在融云控制台中获取 App Key,并设置好 InitOption(初始化配置)。 

InitOption 中封装了 areaCode (数据中心的区域码),naviServer(导航服务地址)、statisticServer(数据统计服务地 址)。 

- 19 - 

如果您使用北京数据中心,则不需设置 InitOption,IMKit SDK 默认连接北京数据中心。 

#### **TypeScript** 

// 初始化 SDK let initOption = new InitOption(); IMEngine.getInstance().init(getContext(), "Your_AppKey", initOption); 

如果您使用海外数据中心,则须传入海外数据中心对应的 AreaCode。 

#### **TypeScript** 

// 初始化 SDK let initOption = new InitOption(); initOption.areaCode = AreaCode.SG; IMEngine.getInstance().init(getContext(), "Your_AppKey", initOption); 

### **连接融云 IM 服务器** 

用户 Token 是与用户 ID 对应的身份验证令牌,是应用程序的用户在融云的唯一身份标识。应用客户端在使用融云即时通讯功 能前必须与融云建立 IM 连接,连接时必须传入 Token。 

在实际业务运行过程中,应用客户端需要通过应用的服务端调用 IM Server API 申请取得 Token。详见 Server API 文档 注 册用户。 

在本教程中,为了快速体验和测试 SDK,我们将使用控制台「北极星」开发者工具箱,从 API 调试页面调用 获取 Token 接 口,获取到 **userId** 为 1 的用户的 Token。提交后,可在返回正文中取得 Token 字符串。 

1. 为模拟用户通过融云 IM 服务器收发消息,您需要首先注册一个用户。在实际业务中,应用客户端通过应用服务端调用融 云 IM Server API 获取 token。详见 Server API 文档注册用户。在本教程中,为了快速体验融云服务,您可在控制台 「北极星」的 API 调试页面调用获取 Token 接口,获取到 userId 为 1 的用户的 Token。调用返回如下: 

#### **HTTP** 

HTTP/1.1 200 OK 

Content-Type: application/json; charset=utf-8 

{"code":200,"userId":"1","token":"gxld6GHx3t1eDxof1qtxxYrQcjkbhl1V@sgyu.cn.example.com;sgyu.cn.exam 

2. 监听 IM 连接状态的变化。建议在应用生命周期内设置。为了避免内存泄露,请在不需要监听时,将设置的监听器移除。 

#### **TypeScript** 

- 20 - 

let statusListener : ConversationStatusListener = { 

onConversationStatusChange: (items: List<ConversationStatusInfo>): void => { 

} } IMEngine.getInstance().addConversationStatusListener(statusListener); 

3. 在自定义登录页面,使用上一步获取的 token, 连接融云,即模拟 userId 为 1 的用户连接到融云服务器。 

#### **TypeScript** 

```arkts
let token = "IMToken"; let timeout = 30; IMEngine.getInstance().connect(token, timeout).then(result => { 
if (EngineError.Success === result.code) { // 连接成功 let userId = result.userId; return; } if (EngineError.ConnectTokenExpired === result.code) { 
```

// Token 过期,从 APP 服务请求新 token,获取到新 token 后重新 connect() 

- } else if (EngineError.ConnectionTimeout === result.code) { 

// 连接超时,弹出提示,可以引导用户等待网络正常的时候再次点击进行连接 

} else { //其它业务错误码,请根据相应的错误码作出对应处理。 } }); 

SDK 已实现自动重连机制,请参见连接。 

### **展示会话列表** 

IMKit SDK 提供基于 Page 类和基于 Component 类实现的会话列表页面。 在 IM 连接成功后可跳转至 SDK 会话列表页。 下面以 IMKit SDK 默认提供的会话列表 ConversationListPage 为例: 

#### **TypeScript** 

import { ConversationListPage } from '@rongcloud/imkit' import promptAction from '@ohos.promptAction' 

@Entry @Component export struct MainPage { build() { 

- 21 - 

Column() { Tabs({ barPosition: BarPosition.End }) { 

TabContent() { Column() { // 直接使用 SDK 内置的会话列表页面 // SDK 有内置的导航,可以自定义导航的左侧、中间、右侧组件 ConversationListPage({ customLeftView: this.customLeftView(), customCenterView: this.customCenterView(), customRightView: this.customRightView() }) } }.tabBar("会话列表-页面") } } } 

// 导航栏自定义左侧组件(可选) @Builder private customLeftView() { Text("左侧标题").onClick(() => { promptAction.showToast({message : "点击了左侧标题"}) }).layoutWeight(1) } 

// 导航栏自定义中间组件(可选) @Builder private customCenterView() { Text("中间标题").onClick(() => { promptAction.showToast({message : "点击了中间标题"}) 

}).layoutWeight(1).textAlign(TextAlign.Center) } 

// 导航栏自定义右侧组件(可选) 

@Builder private customRightView() { Text("右侧标题").onClick(() => { promptAction.showToast({message : "点击了右侧标题"}) 

}).layoutWeight(1).textAlign(TextAlign.End) } } 

用户首次连接时一般没有会话,因此会显示一个空会话列表。客户端接收到消息后,会自动在会话列表页面展示新会话。更多 详情请参见会话列表页面。 

- 22 - 

### **展示会话页面** 

IMKit SDK 提供基于 Page 类和基于 Component 类实现的会话页面。您可以在会话列表页面点击会话 Cell 自动跳转到默认 的会话页面,或者您可以单独跳转到指定的会话页面: 

#### **TypeScript** 

import('@rongcloud/imkit/src/main/ets/conversation/page/ConversationPage'); 

// 进入 SDK ConversationPage // 参数必须是 Conversation 对象,必须有有效的 conversationType targetId let params = new Conversation() params.conversationType = ConversationType.Private; params.targetId = "2"; params.lastSentTime  = 0; router.pushNamedRoute({ name: 'ConversationPage', params: params }) 

实际开发中建议使用自定义会话页面或者会话组件的方式,具体参见会话页面 

## **测试收发消息** 

对融云来说,只要提供对方的 userId,融云就可支持跟对方发起聊天。例如,A 需要 发送消息给 B,只需要将 B 的 userId 告知融云服务即可发送消息。 

在本教程中,为了快速体验和测试 SDK,我们从控制台「北极星」开发者工具箱 [IM Server API 调试]页面向当前登录的用 户发送一条文本消息,模拟单聊会话。在实际业务运行过程中,应用客户端可以通过用户 userId、群聊会话 targetId、或聊 天室 targetId 等接收消息。 

1. 访问控制台「北极星」开发者工具箱的 [IM Server API 调试]页面。 

2. 在 **消息** 标签下,找到 **消息服务** > **发送单聊消息** 接口。 

以下模拟了从 UserId 为 2 的用户向 UserId 为 1 的用户发送一条文本消息。 

- 23 - 

3. 客户端接收到消息后,自动在会话列表页面展示新的单聊会话。 

4. 点击会话,即可进入消息列表页面,发送消息。 

- 24 - 

## **后续步骤** 

以上步骤即 IMKit SDK 的快速集成与新手体验流程,您体验了基础 IM 通信能力和 UI 界面,更多详细介绍请参考后续各章节 详细说明。 

# **导入 SDK** 

融云支持在 DevEco Studio 中自动导入和手动导入 IMKit SDK。 

提示 

- 25 - 

您可以打开OpenHarmony三方库中心仓,搜索关键字 **rongcloud** 查看融云相关的 SDK。 

### **环境要求** 

DevEco Studio NEXT Release(5.0.3.900) 及以上。 

- HarmonyOS SDK API 12 及以上。 

- 手机系统版本号:NEXT.0.0.31。 

- 真机华为 Mate 系列。真机运行需要配置证书,详情参考鸿蒙的[签名指南]文档。 

- 模拟器。详情参考鸿蒙的[模拟器运行指南]文档。 

### **自动导入 SDK** 

IMKit SDK 支持从 OpenHarmony三方库中心仓 获取 SDK。 

- 1.在鸿蒙主工程 entry 目录中的 oh-package.json5 中添加 SDK 依赖,然后点击 "Sync Now"。 

#### **JSON** 

// entry 目录中的 oh-package.json5 

- { "name": "entry", "version": "1.0.0", 

- "description": "Please describe the basic information.", 

- "main": "", 

- "author": "", 

- "license": "", 

- "dependencies": { 

- "@rongcloud/imkit" : "x.y.z", 

- "@rongcloud/imlib" : "x.y.z" 

- } 

} 

**注意** 

各个 SDK 的最新版本号可能不相同,具体 x.y.z 值可前往 融云官网 SDK 下载页面 或 OpenHarmony三方库中心 

- 26 - 

仓 查询。 

#### 2.安装 SDK 成功后,您可以在项目根目录的 **oh_modules/.ohpm/** 中找到融云 IMKit SDK。 

### **手动导入 SDK** 

#### 1.将 SDK 放入 App 仓库 

在项目根路径创建 libs 目录,将从融云官网 SDK 下载页面下载的 IMLib.har 和 IMKit.har 放到 libs 目录。 

- 2.重写 IMLib 依赖 

在项目根路径 oh-package.json5 中重写 IMLib 的依赖,如果没有这一步,IMKit 无法正确依赖 IMLib。 

原因:IMKit 无法扫描工程目录自动找到 IMLib 所在位置,所以通过 overrides 配置指明 IMLib 所在位置,然后 IMKit 就可 以正常依赖 IMLib。 

overrides 配置参考:https://developer.huawei.com/consumer/cn/doc/harmonyos-guides-V5/ide-oh-packagejson5-V5#zh-cn_topic_0000001792256137_overrides 。 

#### **TypeScript** 

- 27 - 

// 项目根路径 oh-package.json5 { "modelVersion": "5.0.0", "description": "Please describe the basic information.", "dependencies": { }, "devDependencies": { "@ohos/hypium": "1.0.19", "@ohos/hamock": "1.0.0" }, // 重写 imlib 的位置,确保 IMKit 能够正确依赖 IMLib "overrides": { "@rongcloud/imlib" :"file:./libs/RongIMLib.har" } } 

#### 3.进入到 entry 目录中执行相关命令使 App 依赖 IMLib & IMKit 

#### **sh** 

# 1. 进入 entry 目录 cd entry 

# 2. 依赖 IMLib ohpm install ../libs/RongIMLib.har 

# 3. 依赖 IMKit ohpm install ../libs/RongIMKit.har 

### **配置项目** 

## **配置 useNormalizedOHMUrl** 

1.0.3 版本开始 SDK 支持字节码,为了支持字节码,app 需要在项目根路径配置 **useNormalizedOHMUrl** 。 

- 28 - 

// app 根路径下的 build-profile.json5 { "app": { "products": [ { "buildOption": { "strictMode": { "useNormalizedOHMUrl": true } } } ] } } 

详细信息请参考 FAQ 

## **配置 abi** 

DevEco Studio 当前支持的平台分别为 **Windows(64-bit)** 、 **Mac(x86)** 、 **Mac(Arm)** 。 

鸿蒙 IMSDK 支持 **arm64-v8a** 、 **x86_64** 两种 abi 架构。 

提示 

DevEco Studio NEXT Developer Beta1 5.0.3.403 不支持编译 armeabi-v7a,会报错 ""armeabi-v7a" not supported for HarmonyOS. " 

DevEco Studio 和 SDK abi 映射关系如下 

|DevEco Studio平台|设备|SDK abi|SDK是否支持|
|---|---|---|---|
|Windows(64-bit)|真机|arm64-v8a|支持|
|Windows(64-bit)|模拟器|x86_64|支持|
|Mac(x86)|真机|arm64-v8a|支持|
|Mac(x86)|模拟器|x86_64|支持|
|Mac(Arm)|真机|arm64-v8a|支持|
|Mac(Arm)|模拟器|arm64-v8a|支持|

**DevEco Studio 默认仅支持 arm64-v8a** ,因此 **Windows(64-bit)- 模拟器** 和 **Mac(x86)- 模拟器** 需要做此项配置。 

配置如下: 

- 29 - 

#### **JSON** 

// 在 entry 目录下的 build-profile.json5 

{ 

"apiType": "stageMode", "buildOption": { "externalNativeOptions": { // 配置 abi 支持 arm64-v8a、x86_64 "abiFilters": [ "arm64-v8a", "x86_64" ] } }, "buildOptionSet": [ { "name": "release", "arkOptions": { "obfuscation": { "ruleOptions": { "enable": true, "files": [ "./obfuscation-rules.txt" ] } } } }, ], "targets": [ { "name": "default" }, { "name": "ohosTest", } ] } 

## **移除 x86_64 架构** 

x86_64 架构用于 **Windows(64-bit)- 模拟器** 和 **Mac(x86)- 模拟器** 。当 app 发版时可以移除 x86_64 架构,减小包体 积。 

- 30 - 

**JSON** 

// 在 entry 目录下的 build-profile.json5 { "apiType": "stageMode", "buildOption": { "nativeLib": { "filter": { "excludes": [ // 过滤 x86_64 目录下的所有 so "x86_64/*" ] } } }, "buildOptionSet": [ { "name": "release", "arkOptions": { "obfuscation": { "ruleOptions": { "enable": true, "files": [ "./obfuscation-rules.txt" ] } } } }, ], "targets": [ { "name": "default" }, { "name": "ohosTest", } ] } 

参考鸿蒙文档中的 excludes 字段 :https://developer.huawei.com/consumer/cn/doc/harmonyos-guides-V5/idehvigor-build-profile-V5 

### **添加 SDK 依赖权限** 

- 31 - 

#### SDK 需要权限如下: 

|权限名称|权限说明|使用目的|
|---|---|---|
|ohos.permission.GET_NETWORK_INFO|获取网络信息|网络变化之后获取网络信息,进行IM重连|
|ohos.permission.INTERNET|使用网络|连接IM、收发消息需要网络连接|
|ohos.permission.STORE_PERSISTENT_DATA|数据存储|消息数据库需要本地存储|
|ohos.permission.MICROPHONE|麦克风|提供发送语音消息功能,需要开启麦克风|

具体权限配置参考鸿蒙的应用权限管控文档。 

- 32 -
