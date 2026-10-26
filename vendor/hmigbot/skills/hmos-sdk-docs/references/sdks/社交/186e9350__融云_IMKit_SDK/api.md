# **IM 融云即时通讯 ( ) SDK 客户端 文档** HarmonyOS IMKit SDK 

## **目录** 

|鸿蒙IMKit架构|16|
|---|---|
|快速上手|16|
|环境要求|16|
|准备工作|17|
|导入SDK|17|
|初始化SDK|19|
|连接融云IM服务器|20|
|展示会话列表|21|
|展示会话页面|23|
|测试收发消息|23|
|后续步骤|25|
|导入SDK|25|
|环境要求|26|
|自动导入SDK|26|
|手动导入SDK|27|
|配置项目|28|
|配置useNormalizedOHMUrl|28|
|配置abi|29|
|移除x86_64架构|30|
|添加SDK依赖权限|31|
|聊天界面|32|
|会话列表页面|32|
|会话列表界面-Page|32|
|示例代码|34|
|会话列表组件-Component|35|
|示例代码|36|
|会话页面|38|
|会话界面-Page|38|

- 2 - 

|直接跳转|39|
|---|---|
|使用ConversationPage组件|39|
|会话组件-Component|40|
|示例代码|41|
|用户与群组管理|43|
|用户概述|43|
|注册用户|43|
|删除用户|44|
|注销用户|44|
|用户信息|44|
|好友关系|44|
|用户管理接口|44|
|群组概述|45|
|服务配置|45|
|客户端SDK使用须知|46|
|群组管理功能|46|
|用户信息|47|
|用户信息提供者|48|
|流程|48|
|设置用户信息提供者|48|
|动态提供用户信息|48|
|示例代码|48|
|缓存策略|50|
|刷新用户信息|50|
|流程|50|
|实现|50|
|获取用户信息|51|
|流程|51|
|实现|51|
|群组信息|51|
|群组信息提供者|52|
|设置群组信息提供者|52|

- 3 - 

|动态提供群组信息|52|
|---|---|
|缓存策略|54|
|刷新群组信息|54|
|获取群组信息|54|
|群成员用户信息|55|
|群成员用户信息提供者|55|
|设置群成员用户信息提供者|55|
|动态提供群成员用户信息|55|
|缓存策略|56|
|刷新群成员用户信息|57|
|获取群成员用户信息|57|
|群组成员列表|57|
|群组成员提供者|58|
|设置群组成员提供者|58|
|动态提供群组成员列表|58|
|获取群成员用户信息列表|59|
|功能特性|60|
|图片和GIF消息|60|
|局限|63|
|用法|63|
|定制化|64|
|修改默认文件保存位置|64|
|调整图片压缩质量|64|
|自定义图片、GIF消息的UI|64|
|隐藏扩展面板中的图片入口|65|
|小视频消息|65|
|局限性|66|
|用法|67|
|从本地相册选择小视频|67|
|录制小视频消息|67|
|定制化|67|
|调整小视频压缩质量|67|

- 4 - 

|自定义小视频消息的UI|67|
|---|---|
|隐藏小视频插件的录制视频功能|68|
|隐藏相册插件中的视频文件|68|
|语音消息|68|
|局限性|69|
|用法|69|
|发送语音消息|70|
|消息列表中的语音消息|70|
|配置高清语音连续播放|71|
|示例代码|71|
|配置自动下载高清语音|72|
|示例代码|72|
|定制化|72|
|自定义语音消息的UI|72|
|文件消息|72|
|局限|73|
|用法|73|
|发送文件消息|73|
|定制化|74|
|修改默认文件保存位置|74|
|替换文件消息默认的文件图标|74|
|自定义文件消息的UI|74|
|替换文件消息插件|75|
|隐藏文件消息插件|75|
|位置消息|75|
|发送位置消息|76|
|自定义位置插件|77|
|添加自定义插件到扩展面板|78|
|发送位置/查看位置页面示例|79|
|示例代码中引用到的类|97|
|处理位置消息点击事件|100|
|定制化|101|

- 5 - 

|自定义位置消息的UI|101|
|---|---|
|Emoji与贴纸表情|101|
|Emoji符号表情|103|
|禁用表情面板中的内置Emoji表情|103|
|自定义表情组件|104|
|添加自定义表情组件|104|
|动态配置表情面板|107|
|隐藏表情面板入口|108|
|自定义表情面板添加按钮|108|
|@消息|111|
|局限|112|
|用法|112|
|定制化|113|
|自定义选择成员界面|113|
|关闭@功能|114|
|输入状态|114|
|局限|115|
|用法|115|
|在自定义会话页面监听输入状态|115|
|示例代码|116|
|定制化|116|
|设置发送输入状态消息的默认时间间隔|117|
|关闭输入状态功能|117|
|已读回执|117|
|阅读回执开关|117|
|单聊阅读回执|117|
|群聊阅读回执|118|
|消息未读数|119|
|用法|120|
|定制化|120|
|获取会话未读数|120|
|获取单个会话的未读数|121|

- 6 - 

|示例代码|121|
|---|---|
|参数说明|121|
|按会话类型列表获取未读数,可以选择是否包含免打扰|121|
|示例代码|121|
|参数说明|122|
|清除会话未读数|122|
|清除指定会话的未读数|122|
|清除指定会话指定时间戳前的未读数|123|
|监听会话未读数变化|123|
|多端同步阅读状态|123|
|主动同步消息未读状态|124|
|监听消息未读状态同步数据|124|
|示例代码|124|
|参数说明|125|
|未读消息气泡提醒|125|
|是否显示未读消息数提醒|126|
|是否显示新消息提醒|126|
|转发消息|127|
|局限|127|
|单条转发|127|
|合并转发(1.4.3支持)|128|
|预览页面事件监听|128|
|示例代码|129|
|预览页面样式设置|129|
|合并转发兼容不支持的类型消息|129|
|构建合并转发消息|129|
|参数说明|130|
|拦截Html页面的JS事件|130|
|自定义html内容说明|131|
|完整示例|132|
|添加转发按钮|135|
|转发消息示例代码|137|

- 7 - 

|撤回消息|140|
|---|---|
|用法|141|
|定制化|141|
|修改消息可撤回的最大时间|141|
|修改撤回后可重新编辑的时间|141|
|其他定制化|141|
|关闭撤回功能|142|
|引用回复|142|
|局限|142|
|用法|143|
|关闭引用回复功能|143|
|自定义引用消息的UI|143|
|会话草稿|143|
|用法|144|
|定制化|144|
|保存/删除会话草稿|144|
|接口原型|144|
|参数说明|145|
|示例代码|145|
|获取会话草稿|145|
|参数说明|145|
|会话置顶|146|
|用法|147|
|定制化|147|
|设置会话置顶|147|
|示例代码|148|
|参数说明|148|
|监听置顶状态同步|148|
|获取会话置顶状态与置顶会话|148|
|水印组件|149|
|功能概述|149|
|设置水印组件配置|149|

- 8 - 

|主要接口与类型说明|149|
|---|---|
|参数说明|151|
|示例代码|151|
|定制化|152|
|发送消息|152|
|构造消息|153|
|发送普通消息|153|
|接口原型|153|
|参数说明|153|
|示例代码|153|
|发送媒体消息|154|
|接口原型|154|
|参数说明|154|
|示例代码|155|
|发送多媒体消息并且上传到自己的服务器|155|
|接收消息|155|
|设置/移除消息接收监听器|156|
|添加消息监听器|156|
|移除消息监听器|156|
|消息接收监听器|156|
|接口原型|156|
|参数说明|156|
|消息收取完毕|157|
|获取历史消息|157|
|拦截消息|158|
|消息拦截器说明|158|
|接口说明|158|
|设置消息拦截器|161|
|删除消息|162|
|同时删除本地与远端消息|162|
|通过消息对象删除消息|162|
|接口原型|162|

- 9 - 

|示例代码|163|
|---|---|
|参数说明|163|
|通过会话删除消息|163|
|接口原型|164|
|示例代码|164|
|参数说明|164|
|仅删除本地消息|164|
|仅删除服务端消息|165|
|撤回消息|165|
|示例代码|165|
|参数说明|165|
|监听他人撤回消息事件|165|
|示例代码|165|
|插入消息|166|
|功能描述|166|
|插入本地消息|166|
|接口原型|166|
|示例代码|166|
|搜索消息|167|
|自定义消息和provider|168|
|自定义普通消息|168|
|1.编写自定义普通消息的代码|168|
|示例代码|168|
|2.将自定义普通消息注册给IMLib|170|
|3.编写普通消息provider|170|
|示例代码|170|
|4.将消息和provider进行绑定|171|
|示例代码|171|
|5.使用自定义消息普通消息|172|
|示例代码|172|
|自定义小灰条消息|172|

- 10 - 

|1.编写自定义小灰条消息的代码|172|
|---|---|
|示例代码|172|
|2.将自定义小灰条消息注册给IMLib|174|
|示例代码|174|
|3.编写小灰条消息provider|174|
|示例代码|174|
|4.将自定义小灰条消息和provider进行绑定|175|
|5.使用自定义小灰条消息|175|
|移除消息Provider|176|
|示例代码|176|
|替换消息Provider|176|
|示例代码|176|
|自定义长按消息菜单|177|
|自定义长按消息弹窗的菜单选项|177|
|示例代码|177|
|参数说明|178|
|自定义消息多选操作菜单|178|
|示例代码|178|
|获取会话|179|
|删除会话|179|
|删除指定会话|180|
|示例代码|180|
|参数说明|181|
|按类型删除会话|181|
|多端同步免打扰/置顶|181|
|监听器说明|181|
|接口原型|182|
|参数说明|182|
|示例代码|182|
|自定义会话列表provider|184|
|会话列表自定义会话展示模板|184|
|编写自定义展示模版|184|

- 11 - 

|示例代码|184|
|---|---|
|绑定自定义会话列表模板|185|
|移除指定会话类型展示模版|185|
|会话列表自定义|186|
|会话列表控制需要展示的会话类型|186|
|示例代码|186|
|会话列表组件自定义聚合展示|186|
|示例代码|186|
|会话列表增加长按事件|187|
|示例代码|187|
|会话列表头像圆角控制|188|
|示例代码|188|
|会话列表点击事件|188|
|示例代码|189|
|会话列表添加自定义空布局|189|
|示例代码|189|
|会话列表页面事件|190|
|接口原型|190|
|示例代码|192|
|自定义会话列表Item扩展组件|192|
|资源自定义|193|
|自定义颜色|193|
|自定义图片|194|
|会话页面自定义|194|
|消息点击事件|194|
|示例代码|195|
|增加消息气泡的长按事件|197|
|示例代码|197|
|参数说明|197|
|配置消息气泡的长按更多选项|197|
|示例代码|198|
|修改消息气泡的UI配置|198|

- 12 - 

|修改边框圆角大小|198|
|---|---|
|示例代码|198|
|修改边框色|199|
|示例代码|199|
|修改背景色|200|
|示例代码|200|
|自定义输入框按钮UI|201|
|自定义会话页面按钮UI|203|
|增加+号扩展栏插件|207|
|内置插件说明|207|
|实现自定义插件|208|
|自定义插件UI|209|
|将插件放到扩展栏里面|210|
|添加插件|210|
|将插件放到指定位置|210|
|替换指定位置的插件,如果没有对应的索引,会将插件放到最后|211|
|移除特定的插件|211|
|根据插件名移除特定的插件|211|
|清空当前的插件。|211|
|动态配置扩展面板插件|212|
|示例代码|212|
|消息头像圆角控制|212|
|示例代码|212|
|修改消息可撤回的最大时间|213|
|示例代码|213|
|修改撤回后可重新编辑的时间|213|
|示例代码|213|
|文本消息字体高亮颜色|213|

- 13 - 

|示例代码|213|
|---|---|
|文本和引用消息内容自定义渲染|213|
|设置文件消息的文件类型图标|214|
|示例代码|214|
|获取文件消息内的文件类型图标map|215|
|示例代码|215|
|修改消息重发开关|215|
|群消息回执配置|216|
|引用消息点击跳转行为配置|216|
|会话页面事件|216|
|示例代码|217|
|设置/移除会话页面事件监听|217|
|示例代码|217|
|输入@时跳转页面并返回数据|217|
|输入状态发生变化|218|
|会话页面代理接口|218|
|获取ViewModel|219|
|ViewModel能力说明|220|
|通知与免打扰|222|
|设置会话免打扰|222|
|设置会话的免打扰状态|222|
|示例代码|222|
|监听会话的免打扰状态同步|223|
|接口原型|223|
|示例代码|223|
|获取会话的免打扰状态|224|
|示例代码|224|
|全局免打扰时段配置|224|
|设置全局免打扰时段配置|225|
|示例代码|225|
|参数说明|225|

- 14 - 

|获取全局免打扰时段配置|226|
|---|---|
|示例代码|226|
|删除已设置的全局免打扰时段配置|226|
|示例代码|226|
|本地通知|227|
|什么是本地通知|227|
|拦截本地通知|227|
|示例代码|228|
|本地通知展示样式|228|
|本地通知铃声与震动|228|
|本地通知点击事件|228|
|示例代码|228|
|常见问题|229|
|SDK字节码支持|229|
|如何解决鸿蒙集合的List类型和UI的List组件类名冲突的问题?|229|
|安卓系统迁移到鸿蒙系统|229|

- 15 - 

#### **鸿蒙 IMKit 架构** 

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

#### **快速上手** 

本教程旨在帮助开发者快速了解和掌握 IMKit SDK (融云即时通讯 UI 库) 的基础集成流程与核心能力。通过本教程,您将完成 IMKit SDK 导入、初始化、建立连接、展示会话列表与会话页面、测试收发消息等全流程操作。 

###### **环境要求** 

DevEco Studio NEXT Release(5.0.3.900) 及以上。 

- HarmonyOS SDK API 12 及以上。 

- 16 - 

手机系统版本号:NEXT.0.0.31。 

- 真机华为 Mate 系列。真机运行需要配置证书,详情参考鸿蒙的[签名指南]文档。 

- 模拟器。详情参考鸿蒙的[模拟器运行指南]文档。 

###### **准备工作** 

1. 访问融云控制台,注册您的开发者账号。注册成功后,控制台自动在开发环境中为您创建一个应用。 

2. 在控制台的基本信息页,获取您的应用在开发环境的 AppKey。您可在基本信息页查看应用的信息,如 App Key、 App Secret、所属数据中心(默认为北京)。 

如您想自己创建应用,参考如何创建应用,并获取对应环境 App Key 和 App Secret。 

###### 提示 

每个应用均拥有两个不同的 App Key,分别对应开发环境与生产环境,且两个环境之间数据相互隔离。在您的 应用正式上线前,建议切换到生产环境的 App Key,以便完成上线前全流程测试和最终发布。 

###### **导入 SDK** 

融云支持从 OpenHarmony三方库中心仓 添加依赖和将 IMKit 相关的 SDK 文件本地库导入应用工程两种集成方式。 

以下介绍如何使用从 OpenHarmony三方库中心仓 添加依赖方式将 IMKit SDK 导入工程: 

1. 在鸿蒙主工程 entry 目录中的 oh-package.json5 中添加 SDK 依赖,然后点击 "Sync Now"。 

###### **JSON** 

- 17 - 

// entry 目录中的 oh-package.json5 

{ 

"name": "entry", "version": "1.0.0", 

"description": "Please describe the basic information.", "main": "", "author": "", "license": "", "dependencies": { "@rongcloud/imkit" : "x.y.z", 

"@rongcloud/imlib" : "x.y.z" 

} } 

###### **注意** 

各个 SDK 的最新版本号可能不相同,具体 x.y.z 值可前往 融云官网 SDK 下载页面 或 OpenHarmony三方库中心 仓 查询。 

2. 安装 SDK 成功后,您可以在项目根目录的 **oh_modules/.ohpm/** 中找到融云 IMKit SDK。 

3. 添加 SDK 依赖权限 

###### 添加如下权限: 

- 18 - 

|权限名称|权限说明|使用目的|
|---|---|---|
|ohos.permission.GET_NETWORK_INFO|获取网络信息|网络变化之后获取网络信息,进行IM重连|
|ohos.permission.INTERNET|使用网络|连接IM、收发消息需要网络连接|
|ohos.permission.STORE_PERSISTENT_DATA|数据存储|消息数据库需要本地存储|
|ohos.permission.MICROPHONE|麦克风|提供发送语音消息功能,需要开启麦克风|
|详情参考鸿蒙应用权限配置文档。|||

4. 配置 useNormalizedOHMUrl 

###### 1.0.3 版本开始 SDK 支持字节码,为了支持字节码,app 需要在项目根路径配置 **useNormalizedOHMUrl** 。 

// app 根路径下的 build-profile.json5 { "app": { "products": [ { "buildOption": { "strictMode": { "useNormalizedOHMUrl": true } } } ] } } 

详细信息请参考 FAQ。 

###### **初始化 SDK** 

IMKit SDK 初始化接口的调用需要引入对应的声明: 

###### **TypeScript** 

import { IMEngine } from '@rongcloud/imkit'; 

为确保您可以正常连接融云服务器和使用融云即时通讯服务(IM 服务),您须调用 init 方法初始化 IMKit SDK。初始化前, 您须在融云控制台中获取 App Key,并设置好 InitOption(初始化配置)。 

InitOption 中封装了 areaCode (数据中心的区域码),naviServer(导航服务地址)、statisticServer(数据统计服务地 址)。 

- 19 - 

如果您使用北京数据中心,则不需设置 InitOption,IMKit SDK 默认连接北京数据中心。 

###### **TypeScript** 

// 初始化 SDK let initOption = new InitOption(); IMEngine.getInstance().init(getContext(), "Your_AppKey", initOption); 

如果您使用海外数据中心,则须传入海外数据中心对应的 AreaCode。 

###### **TypeScript** 

// 初始化 SDK let initOption = new InitOption(); initOption.areaCode = AreaCode.SG; IMEngine.getInstance().init(getContext(), "Your_AppKey", initOption); 

###### **连接融云 IM 服务器** 

用户 Token 是与用户 ID 对应的身份验证令牌,是应用程序的用户在融云的唯一身份标识。应用客户端在使用融云即时通讯功 能前必须与融云建立 IM 连接,连接时必须传入 Token。 

在实际业务运行过程中,应用客户端需要通过应用的服务端调用 IM Server API 申请取得 Token。详见 Server API 文档 注 册用户。 

在本教程中,为了快速体验和测试 SDK,我们将使用控制台「北极星」开发者工具箱,从 API 调试页面调用 获取 Token 接 口,获取到 **userId** 为 1 的用户的 Token。提交后,可在返回正文中取得 Token 字符串。 

1. 为模拟用户通过融云 IM 服务器收发消息,您需要首先注册一个用户。在实际业务中,应用客户端通过应用服务端调用融 云 IM Server API 获取 token。详见 Server API 文档注册用户。在本教程中,为了快速体验融云服务,您可在控制台 「北极星」的 API 调试页面调用获取 Token 接口,获取到 userId 为 1 的用户的 Token。调用返回如下: 

###### **HTTP** 

HTTP/1.1 200 OK 

Content-Type: application/json; charset=utf-8 

{"code":200,"userId":"1","token":"gxld6GHx3t1eDxof1qtxxYrQcjkbhl1V@sgyu.cn.example.com;sgyu.cn.exam 

2. 监听 IM 连接状态的变化。建议在应用生命周期内设置。为了避免内存泄露,请在不需要监听时,将设置的监听器移除。 

###### **TypeScript** 

- 20 - 

let statusListener : ConversationStatusListener = { 

onConversationStatusChange: (items: List<ConversationStatusInfo>): void => { 

} } IMEngine.getInstance().addConversationStatusListener(statusListener); 

3. 在自定义登录页面,使用上一步获取的 token, 连接融云,即模拟 userId 为 1 的用户连接到融云服务器。 

###### **TypeScript** 

```arkts
let token = "IMToken"; let timeout = 30; IMEngine.getInstance().connect(token, timeout).then(result => { 
if (EngineError.Success === result.code) { // 连接成功 let userId = result.userId; return; } if (EngineError.ConnectTokenExpired === result.code) { 
```

// Token 过期,从 APP 服务请求新 token,获取到新 token 后重新 connect() 

- } else if (EngineError.ConnectionTimeout === result.code) { 

// 连接超时,弹出提示,可以引导用户等待网络正常的时候再次点击进行连接 

} else { //其它业务错误码,请根据相应的错误码作出对应处理。 } }); 

SDK 已实现自动重连机制,请参见连接。 

###### **展示会话列表** 

IMKit SDK 提供基于 Page 类和基于 Component 类实现的会话列表页面。 在 IM 连接成功后可跳转至 SDK 会话列表页。 下面以 IMKit SDK 默认提供的会话列表 ConversationListPage 为例: 

###### **TypeScript** 

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

###### **展示会话页面** 

IMKit SDK 提供基于 Page 类和基于 Component 类实现的会话页面。您可以在会话列表页面点击会话 Cell 自动跳转到默认 的会话页面,或者您可以单独跳转到指定的会话页面: 

###### **TypeScript** 

import('@rongcloud/imkit/src/main/ets/conversation/page/ConversationPage'); 

// 进入 SDK ConversationPage // 参数必须是 Conversation 对象,必须有有效的 conversationType targetId let params = new Conversation() params.conversationType = ConversationType.Private; params.targetId = "2"; params.lastSentTime  = 0; router.pushNamedRoute({ name: 'ConversationPage', params: params }) 

实际开发中建议使用自定义会话页面或者会话组件的方式,具体参见会话页面 

##### **测试收发消息** 

对融云来说,只要提供对方的 userId,融云就可支持跟对方发起聊天。例如,A 需要 发送消息给 B,只需要将 B 的 userId 告知融云服务即可发送消息。 

在本教程中,为了快速体验和测试 SDK,我们从控制台「北极星」开发者工具箱 [IM Server API 调试]页面向当前登录的用 户发送一条文本消息,模拟单聊会话。在实际业务运行过程中,应用客户端可以通过用户 userId、群聊会话 targetId、或聊 天室 targetId 等接收消息。 

1. 访问控制台「北极星」开发者工具箱的 [IM Server API 调试]页面。 

2. 在 **消息** 标签下,找到 **消息服务** > **发送单聊消息** 接口。 

以下模拟了从 UserId 为 2 的用户向 UserId 为 1 的用户发送一条文本消息。 

- 23 - 

3. 客户端接收到消息后,自动在会话列表页面展示新的单聊会话。 

4. 点击会话,即可进入消息列表页面,发送消息。 

- 24 - 

##### **后续步骤** 

以上步骤即 IMKit SDK 的快速集成与新手体验流程,您体验了基础 IM 通信能力和 UI 界面,更多详细介绍请参考后续各章节 详细说明。 

#### **导入 SDK** 

融云支持在 DevEco Studio 中自动导入和手动导入 IMKit SDK。 

提示 

- 25 - 

您可以打开OpenHarmony三方库中心仓,搜索关键字 **rongcloud** 查看融云相关的 SDK。 

###### **环境要求** 

DevEco Studio NEXT Release(5.0.3.900) 及以上。 

- HarmonyOS SDK API 12 及以上。 

- 手机系统版本号:NEXT.0.0.31。 

- 真机华为 Mate 系列。真机运行需要配置证书,详情参考鸿蒙的[签名指南]文档。 

- 模拟器。详情参考鸿蒙的[模拟器运行指南]文档。 

###### **自动导入 SDK** 

IMKit SDK 支持从 OpenHarmony三方库中心仓 获取 SDK。 

- 1.在鸿蒙主工程 entry 目录中的 oh-package.json5 中添加 SDK 依赖,然后点击 "Sync Now"。 

###### **JSON** 

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

###### 2.安装 SDK 成功后,您可以在项目根目录的 **oh_modules/.ohpm/** 中找到融云 IMKit SDK。 

###### **手动导入 SDK** 

###### 1.将 SDK 放入 App 仓库 

在项目根路径创建 libs 目录,将从融云官网 SDK 下载页面下载的 IMLib.har 和 IMKit.har 放到 libs 目录。 

- 2.重写 IMLib 依赖 

在项目根路径 oh-package.json5 中重写 IMLib 的依赖,如果没有这一步,IMKit 无法正确依赖 IMLib。 

原因:IMKit 无法扫描工程目录自动找到 IMLib 所在位置,所以通过 overrides 配置指明 IMLib 所在位置,然后 IMKit 就可 以正常依赖 IMLib。 

overrides 配置参考:https://developer.huawei.com/consumer/cn/doc/harmonyos-guides-V5/ide-oh-packagejson5-V5#zh-cn_topic_0000001792256137_overrides 。 

###### **TypeScript** 

- 27 - 

// 项目根路径 oh-package.json5 { "modelVersion": "5.0.0", "description": "Please describe the basic information.", "dependencies": { }, "devDependencies": { "@ohos/hypium": "1.0.19", "@ohos/hamock": "1.0.0" }, // 重写 imlib 的位置,确保 IMKit 能够正确依赖 IMLib "overrides": { "@rongcloud/imlib" :"file:./libs/RongIMLib.har" } } 

###### 3.进入到 entry 目录中执行相关命令使 App 依赖 IMLib & IMKit 

###### **sh** 

# 1. 进入 entry 目录 cd entry 

# 2. 依赖 IMLib ohpm install ../libs/RongIMLib.har 

# 3. 依赖 IMKit ohpm install ../libs/RongIMKit.har 

###### **配置项目** 

##### **配置 useNormalizedOHMUrl** 

1.0.3 版本开始 SDK 支持字节码,为了支持字节码,app 需要在项目根路径配置 **useNormalizedOHMUrl** 。 

- 28 - 

// app 根路径下的 build-profile.json5 { "app": { "products": [ { "buildOption": { "strictMode": { "useNormalizedOHMUrl": true } } } ] } } 

详细信息请参考 FAQ 

##### **配置 abi** 

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

###### **JSON** 

// 在 entry 目录下的 build-profile.json5 

{ 

"apiType": "stageMode", "buildOption": { "externalNativeOptions": { // 配置 abi 支持 arm64-v8a、x86_64 "abiFilters": [ "arm64-v8a", "x86_64" ] } }, "buildOptionSet": [ { "name": "release", "arkOptions": { "obfuscation": { "ruleOptions": { "enable": true, "files": [ "./obfuscation-rules.txt" ] } } } }, ], "targets": [ { "name": "default" }, { "name": "ohosTest", } ] } 

##### **移除 x86_64 架构** 

x86_64 架构用于 **Windows(64-bit)- 模拟器** 和 **Mac(x86)- 模拟器** 。当 app 发版时可以移除 x86_64 架构,减小包体 积。 

- 30 - 

**JSON** 

// 在 entry 目录下的 build-profile.json5 { "apiType": "stageMode", "buildOption": { "nativeLib": { "filter": { "excludes": [ // 过滤 x86_64 目录下的所有 so "x86_64/*" ] } } }, "buildOptionSet": [ { "name": "release", "arkOptions": { "obfuscation": { "ruleOptions": { "enable": true, "files": [ "./obfuscation-rules.txt" ] } } } }, ], "targets": [ { "name": "default" }, { "name": "ohosTest", } ] } 

参考鸿蒙文档中的 excludes 字段 :https://developer.huawei.com/consumer/cn/doc/harmonyos-guides-V5/idehvigor-build-profile-V5 

###### **添加 SDK 依赖权限** 

- 31 - 

###### SDK 需要权限如下: 

|权限名称|权限说明|使用目的|
|---|---|---|
|ohos.permission.GET_NETWORK_INFO|获取网络信息|网络变化之后获取网络信息,进行IM重连|
|ohos.permission.INTERNET|使用网络|连接IM、收发消息需要网络连接|
|ohos.permission.STORE_PERSISTENT_DATA|数据存储|消息数据库需要本地存储|
|ohos.permission.MICROPHONE|麦克风|提供发送语音消息功能,需要开启麦克风|

具体权限配置参考鸿蒙的应用权限管控文档。 

### **聊天界面** 

###### **会话列表页面** 

IMKit SDK 会话的产生依赖本地数据库中的消息,会话列表页面展示了当前用户设备上的所有本地会话。一但 SDK 的本地消 息数据库生成消息,SDK 就会生成对应的会话,并按照时间倒序排列,置顶会话会排在最前。 

###### 提示 

如果开启了多设备消息同步,在 **换新设备登录** 或 **应用卸载重装** 场景下,离线补偿机制仅可获取到最近(默认离线补 偿天数为 1 天,最大 7 天)的单聊、群聊会话消息。早于该天数的会话无法通过离线补偿机制获取。因此,离线补偿 后的会话列表可能与原设备上或卸载前的会话列表并不一致(您可能会有丢失部分会话的错觉)。 

IMKit 提供基于 Page 类和基于 Component 类实现的会话列表页面。 

**基于 Page** :IMKit SDK 默认提供的会话列表 ConversationListPage 。页面支持一个标题栏和一个会话列表。 

- **基于 Component** :您可以在应用 Page 中集成 IMKit 提供的会话列表 ConversationListComponent ,即自定义会 话列表 Page。 

注意 

Android 的 Activity 或 Fragment 可以被继承,但是鸿蒙的 Page 或者 Component 都无法被继承。 

##### **会话列表界面 -Page** 

会话列表页面支持基于 Page 类的实现方式,包含标题栏和会话列表两部分组。 

优点:可以直接使用,点击跳转聊天页面已经完成 

缺点:定制化能力弱 

- 32 - 

- 33 - 

**示例代码** 

###### **TypeScript** 

import { ConversationListPage } from '@rongcloud/imkit' import promptAction from '@ohos.promptAction' 

```arkts
@Entry @Component export struct MainPage { build() { Column() { Tabs({ barPosition: BarPosition.End }) { 
```

TabContent() { Column() { // 直接使用 SDK 内置的会话列表页面 // SDK 有内置的导航,可以自定义导航的左侧、中间、右侧组件 ConversationListPage({ customLeftView: this.customLeftView(), customCenterView: this.customCenterView(), customRightView: this.customRightView() }) } }.tabBar("会话列表-页面") } } } 

// 导航栏自定义左侧组件(可选) @Builder private customLeftView() { Text("左侧标题").onClick(() => { 

promptAction.showToast({message : "点击了左侧标题"}) }).layoutWeight(1) } 

// 导航栏自定义中间组件(可选) 

@Builder private customCenterView() { Text("中间标题").onClick(() => { 

- promptAction.showToast({message : "点击了中间标题"}) }).layoutWeight(1).textAlign(TextAlign.Center) 

- 34 - 

y g 

g 

g 

} 

// 导航栏自定义右侧组件(可选) @Builder private customRightView() { Text("右侧标题").onClick(() => { promptAction.showToast({message : "点击了右侧标题"}) 

}).layoutWeight(1).textAlign(TextAlign.End) } } 

##### **会话列表组件 -Component** 

会话列表页面支持基于 Component 类的实现方式,此方式需要自行实现标题栏。 

优点:定制化容易。整个 Page 可以开发者自己构建,只需要把会话列表组件嵌入到开发者自己的 Page 中 

缺点:如果开发者想做自定义的导航栏,需要自己实现。每个会话的点击事件需要 App 处理 

- 35 - 

**示例代码** 

###### **TypeScript** 

- 36 - 

```arkts
import { Conversation, ConversationListComponent, RCTitleBar } from '@rongcloud/imkit' import { router } from '@kit.ArkUI' 
```

###### @Entry 

- @Component 

export struct ChatListPage { 

" " @State model: RCTitleBar.Model = new RCTitleBar.Model().setTitleName( 会话列表 ).setLeftIcon(null) 

build() { Column() { RCTitleBar({ model: this.model 

}) 

ConversationListComponent({ 

// 实现会话列表的点击事件 

onConversationItemClick: this.onConversationItemClick, 

// 实现没有会话的空白页面 

emptyComponent: () => { 

this.emptyBuilder(); 

- } 

- }).layoutWeight(1) 

- }.width('100%').height('100%') 

} 

###### @Builder 

emptyBuilder() { 

Text(`空白页面`).width('95%').fontColor("#FF0000").padding(10) 

} 

private onConversationItemClick(conversation: Conversation, index: number): void { 

// let params = new Conversation() 

// params.conversationType = ConversationType.Private 

// params.targetId = "会话 Id" 

// 参数必须是 Conversation 对象,必须有有效的 conversationType targetId router.pushUrl({ url: "pages/ChatPage", params: conversation },); 

} } 

###### 提示 

SDK 默认未处理点击事件,设置会话列表点击事件具体参考会话列表事件。 

- 37 - 

###### **会话页面** 

会话页面即应用程序中的聊天页面,主要由消息列表和输入区两部分组成。IMKit 提供默认的会话页面 Page 类和基于 Component 类实现的会话页面。 

- **基于 Page** :IMKit SDK 提供了默认会话页面 ConversationPage 。页面包含标题栏、消息列表和输入区域。在会话列 表页点击某条会话时,会跳转到对应的会话页面。应用程序可以直接使用 ConversationPage 。 

**基于 Component** :您可以在应用 Page 中集成 IMKit 提供的会话 ConversationComponent。 

注意 

Android 的 Activity 或 Fragment 可以被继承,但是鸿蒙的 Page 或者 Component 都无法被继承。 

##### **会话界面 -Page** 

会话页面支持基于 Page 类的实现方式,包含标题栏、消息列表和底部工具栏组成。 

优点:可以直接使用 

缺点:定制化能力弱 

###### 提示 

默认 ConversationPage 不支持沉浸式状态栏模式,如果应用层设置了沉浸式状态栏模式,建议基于 ConversationComponent 构建会话页面,自行适配沉浸式状态栏模式。 

- 38 - 

直接跳转

###### 跳转到 ConversationPage 组件,支持不通过会话列表直接跳转 

###### **TypeScript** 

import('@rongcloud/imkit/src/main/ets/conversation/page/ConversationPage'); 

###### // 进入 SDK ConversationPage 

// 参数必须是 Conversation 对象,必须有有效的 conversationType targetId let params = new Conversation() params.conversationType = ConversationType.Private; params.targetId = "2"; params.lastSentTime  = 0; router.pushNamedRoute({ name: 'ConversationPage', params: params }) 

> **使用** ConversationPage **组件** 

- 39 - 

###### **TypeScript** 

import { ConversationIdentifier, ConversationPage, ConversationType } from '@rongcloud/imkit'; 

/** 

- 自定义会话页面,仅集成了ConversationPage 

- */ 

- @Entry 

- @Component 

struct CustomConversationPage { 

build() { 

- Column() { ConversationPage({ 

conId: ConversationIdentifier.createWith2(ConversationType.Private, "会话ID targetId") 

- }).layoutWeight(1) 

- }.width('100%') 

- .height('100%') 

- } 

} 

##### **会话组件 -Component** 

会话页面支持基于 Component 类的实现方式,此方式需要自行实现标题栏。 

- 40 - 

优点:定制化容易。整个 Page 可以开发者自己构建,只需要把聊天页面组件嵌入到开发者自己的 Page 中。 缺点:如果您想做自定义的导航栏,需要自己实现。 

###### **示例代码** 

###### **TypeScript** 

// 使用 ConversationComponent 自行创建聊天页面 

```arkts
import { Conversation, ConversationComponent, ConversationComponentData, ConversationIdentifier, RCTitleBar } from '@rongcloud/imkit'; import { promptAction, router } from '@kit.ArkUI'; 
```

- 41 - 

po { p o p c o , ou e } o @ 

U ; 

###### @Entry 

- @Component 

export struct ChatPage { 

- @State pageShow: boolean = true 

- @State isEdit: boolean = false 

- " 

- @State model: RCTitleBar.Model = new RCTitleBar.Model().setLeftTitleName( 返 

回").setOnLeftClickListener(() => { 

router.back(); 

- }).setRightTitleName("设置").setOnRightClickListener(() => { 

promptAction.showToast({ message: '点击了设置...' }) 

- }) 

private conId: ConversationIdentifier = new ConversationIdentifier(); 

private conversationComponentData: ConversationComponentData | undefined 

###### aboutToAppear(): void { 

- // router 传入下个页面数据类型会丢失 

- // 此处虽然 as Conversation ,但本质还是 Object 对象 

- // 如果按照 Conversation 对象调用 params 的方法会发生崩溃 

const params = router.getParams() as Conversation; 

if (params && params.conversationType) { 

this.conId.conversationType = params.conversationType; 

- } 

if (params && params.targetId) { 

this.conId.targetId = params.targetId; 

###### } 

this.conversationComponentData = new ConversationComponentData(this.conId) 

- // 1.6.0 及以上版本,跳转到指定消息,只传消息的sentTime即可,不需要再传消息Id(内部不再使用此参数),如果 

- 不传则滚动到底部。 

- // this.conversationComponentData.timestamp = 跳转的消息时间 

- //  1.6.0 以下版本,则需要传入消息的sentTime 与消息Id,如果不传则滚动到底部。 

- // this.conversationComponentData.timestamp = 跳转的消息时间 

- // this.conversationComponentData.messageId = 跳转的消息ID 

- } 

onPageShow(): void { 

this.pageShow = true; 

- } 

onPageHide(): void { this.pageShow = false; 

} 

- 42 - 

} 

- build() { Column() { RCTitleBar({ model: this.model }) ConversationComponent({ // 聊天页面数据,必须指定具体的会话,聊天页面才能加载对应会话的消息 

- conversationData: this.conversationComponentData, // 聊天页面控制多选功能的是否开启。 // 传入 true 聊天页面消息开始多选,传入 false 消息关闭多选 // SDK 内部有多选功能,建议 App 不需要开启多选,只需要在合适的时间关闭(比如 App 多选完消息做某些操作, 

- 完成之后可以通过该字段关闭多选) isEdit : this.isEdit, // 聊天页面监听消息长按后底部菜单的更多按钮点击事件。 onClickMoreAction: (isEdit: boolean) => { this.onClickMoreAction(isEdit) 

- }, // 聊天页面组件需要在 onPageShow & onPageHide 做一些业务逻辑,例如设置键盘状态,停止播放语音消息等 // 而组件是无法直接监听到 onPageShow & onPageHide 事件,所以需要 Page 将该事件传递给聊天页面组件 

- pageShow: this.pageShow }).layoutWeight(1) // layoutWeight 自适应填充剩余空间,可以避免底部的输入框超出屏幕 

- } } private onClickMoreAction(isEdit: boolean) : void { // 处理逻辑 

- } } 

### **用户与群组管理** 

###### **用户概述** 

App 用户需要接入融云服务,才能使用即时通讯服务。对于融云来说,用户是指持有由融云分发的有效 Token,接入并使用 即时通讯服务的 App 用户。 

##### **注册用户** 

- 43 - 

应用服务端(App Server)应向融云服务端提供 App 用户的用户 ID(userId),以向融云换取唯一用户 Token。对融云来 说,这个以 userId 获取 Token 的步骤即注册用户,且必须通过调用 Server API 来完成。 

应用客户端必须持有有效 Token,才能成功连接到融云服务端,使用融云即时通讯服务。当 App 客户端用户向服务器发送登 录请求时,服务器会查询数据库以检查连接请求是否匹配。 

###### **注册用户数限制** 

- **开发环境** ?中的注册用户数上限为 100 个。 

- 在 **生产环境** ?中,升级为 **IM 旗舰版** 或 **IM 尊享版** 后不限制注册用户数。 

##### **删除用户** 

删除用户是指在应用的 **开发环境** 中,通过控制台删除已注册的测试用户,以控制开发环境中的测试用户总数。 **生产环境** 不支持 该操作。 

##### **注销用户** 

注销用户是指在融云服务中删除用户数据。App 可使用该能力实现自身的用户销户功能,满足 App 上架或合规要求。 

融云返回注销成功结果后,与用户 ID 相关数据即被删除。您可以向融云查询所有已注销用户的 ID。如有需要,您可以重新激 活已被注销的用户 ID(注意,用户个人数据无法被恢复)。 

仅 IM Server API 提供上述能力。 

##### **用户信息** 

用户信息泛指用户的昵称、头像,以及群组的群昵称、群头像等数据。融云默认不存储和维护您应用的用户信息数据,需要在 应用侧自行维护用户数据。如果您需要将应用下用户的资料信息存储在融云,可开启并使用融云的信息托管服务,将用户的资 料信息存储到融云进行托管维护。 

##### **好友关系** 

默认融云即时通讯服务不会同步或保存 App 端的好友关系数据,需要由应用服务器(App Server)自行维护。如果您需要使 用融云的好友关系管理服务,可开启融云的信息托管服务,开启后可通过融云提供的好友关系管理服务,进行用户的好友关系 管理。 

在未使用融云好友关系管理服务情况下,如果需要对客户端用户之间的消息收发行为进行限制(例如,App 的所有 userId 泄 漏,导致某个恶意用户可越过好友关系向任意用户发送消息),可以考虑使用用户白名单服务。用户一旦开启并设置白名单, 则仅可接收来自该白名单中用户的消息。 

如使用融云提供的好友关系管理服务,默认非好友间也可以正常发送消息,如需要限制为仅好友可以发送消息,可以在融云控 制台( **应用配置** > **IM 服务** > **信息托管服务** > **功能设置** > **好友功能配置** )中开启仅好友可以相互发送单聊消息功能。 

##### **用户管理接口** 

- 44 - 

|功能分类|功能描述|客户端API|服务端API|
|---|---|---|---|
|注册用户|使用App用户的用户ID向融云换取Token。|不提供该API|注册用户|
|删除用户|参见上文删除用户。|不提供该API|不提供该API|
|废弃Token|废弃在特定时间点之前获取的Token。|不提供该API|作废Token|
|注销用户|注销用户是指在融云服务中停用用户ID,并删除用户个人数据。|不提供该API|注销用户|
|查询已注销用户|获取已注销的用户ID列表。|不提供该API|查询已注销用户|

重新激活用户 ID | 在融云服务中重新启用已注销用户的 ID。 | 不提供该 API | 重新激活用户 ID | | 设置客户端本地的用户信 息 | 设置用户信息提供者,由应用层负责提供数据。 | 设置用户信息提供者 | 不提供该 API | | 设置融云服务端的用户信息 | 设置在融云推送服务中使用的用户名称与头像。 | 不提供该 API | 未提供单独的设置接口。在注册用户时必须提供用户信息。 | | 获取客户端本地的用户信息 | 获取在会话页面、好友列表等处显示的用户头像、昵称等信息。 | 获取用户信息 | 不提供该 API | | 获取融云服务端的用户信息 | 获取用户在融云注册的信息,包括用户创建时间和服务端的推送服务使用的用户名称、头 像 URL。 | 不提供该 API | 获取信息 | | 修改客户端本地的用户信息 | 修改在客户端本地数据库中保存的用户昵称、头像等信 息。 | 刷新用户信息 | 不提供该 API | | 修改融云服务端的用户信息 | 修改在融云推送服务中使用的用户名称与头像。 | 不提供 该 API | 修改信息 | | 封禁用户 | 禁止用户连接到融云即时通讯服务,并立即断开连接。可按时长解封或主动解封。查询被封 禁用户的用户 ID、封禁结束时间。 | 不提供该 API | 添加封禁用户、解除封禁用户、查询封禁用户 | | 查询用户在线状态 | 查 询某用户的在线状态。 | 不提供该 API | 查询在线状态 | | 黑名单管理 | 在用户的黑名单列表中添加、移除用户。在 A 用户黑 名单的用户无法向 A 发送消息。IMKit 默认已处理被拉黑后的错误,页面会提示 “您的消息已经发出,但被对方拒收”。 

IMKit 未提供该 API 接口。此处客户端 API 为 IMLib 的 API 接口。 | 加入黑名单、移出黑名单、查询用户是否在黑名单 中、获取黑名单列表 | 加入黑名单、移出黑名单、查询黑名单 | | 用户白名单 | 用户一旦开启并设置白名单,则仅可接收来自 该白名单中用户的消息。 | 不提供该 API | 开启用户白名单、用户白名单状态查询、添加白名单、移出白名单、查询白名单 | 

###### **群组概述** 

群聊是即时通讯类应用中常见的多人通讯方式,一般包含两个及以上的用户。融云的群组业务支持丰富的群组成员管理、禁言 管理等特性,支持离线消息推送和历史消息记录漫游,可用于兴趣群、办公群、客服服务沟通等。IMKit 提供开箱即用的群聊 会话 UI 组件。 

##### **服务配置** 

客户端 SDK 默认支持群组业务,不需要申请开通。部分基础功能与增值服务可以在控制台的免费基础功能和 IM 服务管理页 面进行开通和配置。 

- App Key 下可创建的群组数量无限制。单个用户可加入的群组数量无限制。 

- 群组有容量上限,默认群组成员数量上限为 3000 人,可联系客服修改。 

- 默认情况下,App Key 未开通 **单群聊消息云端存储** 服务。您可以自助开通,详见 开通单群聊消息云存储服务。如果是生 产环境的 App Key,仅 **IM 旗舰版** 、 **IM 尊享版** 可开通该服务。 

- 默认情况下,用户只能查看他们加入群组后的群聊消息。开启服务后,新入群用户可以获取他们加入群组之前的群聊历史 消息。详见开通新用户获取加入群组前历史消息服务。 

- 45 - 

##### **客户端 SDK 使用须知** 

- 客户端 SDK(IMKit/IMLib)均不提供群组管理的 API。如需创建群组,必须由 App 服务器请求融云服务端 API 实现。 其他操作例如解散群组、加入群组、退出群组等群组管理操作,均须由 App 服务器请求融云服务端 API 实现。详见下 方群组管理功能。 

- 群主、群管理员、群公告、邀请入群、群号搜索等均为群组业务逻辑,需在 App 侧自行实现。 

- 融云只负责将消息传达给群组中的所有用户,不维护群组成员的资料(头像、名称、群成员名片等)。App 需要自行在 业务服务器上维护相关数据,并实现 IMKit 的相关接口,向 IMKit 提供数据。参见下方文档: 

   - 群组信息 

   - 群成员用户信息 

   - 群组成员列表 

##### **群组管理功能** 

对于客户端开发人员来说,创建群组、解散等基础管理操作只需要与 App 自身的业务服务端交互即可,由 App 服务端负责调 用相应的融云服务端 API(Server API)接口完成相关操作。 

- 46 - 

服务端 API 功能描述 

创建群 提供创建者用户 ID、群组 ID、和群名称,向融云服务端申请建群。如解散群组,则群成员关系不复存在。 组、解散 群组 加入群 加入群组后,默认可查看入群以后产生的新消息。退出群组后,不再接收该群的新消息。 组、退出 群组 刷新群组 修改在融云推送服务中使用的群组信息。 信息 查询群组 查询指定群组所有成员的用户 ID 信息。 成员 查询用户 根据用户 ID 查询该用户加入的所有群组,返回群组 ID 及群组名称。融云不存储群组资料信息,群组资料及群成 所在群组 员信息需要开发者在应用服务器自行维护,如应用服务端维护的用户群组关系有缺失时,可通过此接口来核对校 验。 同步用户 向融云服务端同步指定用户当前所加入的所有群组,防止应用中的用户群组信息与融云服务端的用户所属群信息 所在群组 不一致。如果在集成融云服务前 App Server 上已有群组及成员数据,第一次连接融云服务器时,可使用此接口 向融云同步已有的用户与群组对应关系。 禁言指定 在指定的单个群组中或全部群组中,禁言一个或多个用户。被禁言用户可以接收查看群组中其他用户消息,但不 群成员 能通过客户端 SDK 发送消息。 设置群组 将群组全体成员禁言。被禁言群组的所有成员均不能发送消息,需要某些用户可以发言时,可将此用户加入到群 全体禁言 禁言用户白名单中。 加入群组 群组被整体禁言后,禁言白名单中用户可以发送群消息。 全体禁言 白名单 

###### **用户信息** 

要在 IMKit UI 上展示用户头像、昵称等,需要应用层(App)主动向 IMKit SDK 提供 **用户信息** 。 

IMKit 使用 UserDataService 类统一管理用户信息数据。App 需要使用 UserDataService 向 IMKit 提供用户数据,用于在 UI 上展示。SDK 会在需要使用的时候回调 UserDataService 的相关方法。 

**用户信息** :包含昵称、头像 

**群组信息** :包含群组名称、群组头像 

**群成员用户信息** :仅支持群用户昵称 

- 47 - 

###### 提示 

用户信息、群组信息、群成员用户信息必须由应用您主动从 App 服务端获取,并提供给 IMKit SDK。融云鸿蒙 SDK 不提供 App 用户与群组信息托管服务。融云服务端的用户昵称及头像仅用于推送服务。 

本文仅描述了应用层(App)如何使用 IMKit SDK 提供用户信息: 

##### **用户信息提供者** 

##### **流程** 

用户信息、群组信息、群组成员信息流程完全一致,此处以用户信息为例 

1. IMKit 在收发消息时,会在会话列表和聊天页面展示消息内容,并展示对应的用户信息,此时 IMKit 检查内部是否缓存的 有对应的用户信息 

2. IMKit 如果缓存有用户信息就正常展示 

3. IMKit 没有缓存的用户信息,就需要从 App 获取用户信息。IMKit 会触发 UserDataProvider.fetchUserInfo 方法。 

4. App 没有缓存的情况下,从 APPServer 获取用户信息。 

5. APPServer 将用户信息返给 App,App 可以视情况将用户信息缓存。 

6. App 通过 UserDataProvider.fetchUserInfo 将用户信息 return 给 IMKit 

7. IMKit 获取用户信息,缓存起来,内部通过 UserDataListener.onUserInfoChanged 来刷新消息 UI。 

##### **设置用户信息提供者** 

使用 UserDataService 的 setUserDataProvider 方法设置用户信息提供者。必须在 SDK 初始化之后,建立 IM 连接之前 设置。建议在应用生命周期内设置。 

###### **TypeScript** 

// 设置用户信息提供者 RongIM.getInstance().userDataService().setUserDataProvider(userDataProvider); 

##### **动态提供用户信息** 

如果 IMKit 无法从 userDataService 中获取用户信息,将触发 UserDataProvider.fetchUserInfo 回调方法。App 应在该 回调中提供 SDK 所需要的用户头像与昵称。 

获取用户信息数据后,SDK 会自动设置、刷新用户头像与昵称,以及实现相关 UI 展示。 

###### **示例代码** 

###### **TypeScript** 

let userDataProvider: UserDataProvider = { 

fetchUserInfo: (userId: string): Promise<UserInfoModel> => { 

- 48 - 

fetchUserInfo: (userId: string): Promise<UserInfoModel> > { // app 拿到用户信息后通过 Promise 返给 IMKit 

// App 可以从数据库或者 APPServer 获取用户信息 return new Promise((resolve: Function) => { let userInfo = new UserInfoModel(userId, "用户名称", "用户头像") resolve(userInfo); }); }, 

```arkts
fetchGroupInfo: (groupId: string): Promise<GroupInfoModel> => { // app 拿到群组信息后通过 Promise 返给 IMKit // App 可以从数据库或者 APPServer 获取信息 return new Promise((resolve: Function) => { let info = new GroupInfoModel(groupId, "群组名称", "群组头像") resolve(info); }); }, 
fetchGroupMemberInfo: (groupId: string, userId: string): Promise<GroupMemberInfoModel> => { // app 拿到群组成员信息后通过 Promise 返给 IMKit // App 可以从数据库或者 APPServer 获取信息 return new Promise((resolve: Function) => { let info = new GroupMemberInfoModel(groupId, userId, "群成员名称", "群成员头像") resolve(info); }); }, 
fetchGroupMemberInfos: (groupId: string): Promise<Array<GroupMemberInfoModel>> => { // app 拿到群组所有成员信息后通过 Promise 返给 IMKit // App 可以从数据库或者 APPServer 获取信息 return new Promise((resolve: Function) => { let array = new Array<GroupMemberInfoModel>(); for (let i = 0; i < 10; i++) { let userId = "userId" + i; let info = new GroupMemberInfoModel(groupId, userId, "群成员名称", "群成员头像") array.push(info); } resolve(array); }); }, /** 
```

* 是否持久化存储用户信息到 SDK 的本地数据库, 默认为 true, * @since 1.6.0 */ 

isCacheUserInfo: true, 

- 49 - 

, /** * 是否持久化存储群组信息到 SDK 的本地数据库, 默认为 true, * @since 1.6.0 */ isCacheGroupInfo: true, /** * 是否持久化存储群成员信息到 SDK 的本地数据库, 默认为 true, * @since 1.6.0 */ isCacheGroupMemberInfo: true, } RongIM.getInstance().userDataService().setUserDataProvider(userDataProvider); 

##### **缓存策略** 

在 App 的生命周期中,如果 SDK 获取过用户的信息,便会在内存中缓存该信息。允许持久化存储后,SDK 优先从本地数据 库中获取用户信息,App 下次启动时数据仍然可用。SDK 在处理对应信息时默认行为如下: 

1. 当 SDK 需要在 UI 上显示用户信息时,首先从内存中查询已获取的数据。 

2. 如果 SDK 可从缓存或本地数据库中查询到所需信息,将直接将数据返回 UI 层并刷新 UI。 

3. 如果 SDK 未能从缓存或本地数据库查询到所需信息,则将触发 UserDataProvider 的回调方法,并尝试从应用层获取 信息。收到应用层提供的相应信息后,SDK 将刷新 UI。 

##### **刷新用户信息** 

##### **流程** 

1. IMKit 将用户信息缓存起来之后,是不会主动更新的,因为 IMKit 不知道在什么时机更新。App 需要在发现某个用户信 息发生了变化之后,主动通知 IMKit 

2. App 调用 UserDataService updateUserInfo 刷新 IMKit 的用户信息 

3. IMKit 拿到新的用户信息,更新缓存,并更新 UI 

##### **实现** 

如果 App 本地持有用户信息数据(例如当前登录用户的昵称和头像),可直接刷新本地缓存和数据库中存储的用户信息(头 像与昵称)。刷新后,IMKit UI 会展示最新的用户信息 

提示 

- 50 - 

刷新用户信息必须在 IMKit 已成功建立 IM 连接后操作,否则无法刷新本地数据。 

可能适用场景如下: 

- App 首次启动,并成功建立 IM 连接以后,可以将自身业务所需的用户信息批量提供给 SDK,由 SDK 写入缓存与本地 数据库,供后续使用。 

- 在 IM 建立连接后,如果用户昵称、头像等信息变动,由 App 服务端通知客户端(例如使用消息),客户端调用接口刷 新用户信息。 

###### **TypeScript** 

let userInfo = new UserInfoModel("userId","用户名称","用户头像") RongIM.getInstance().userDataService().updateUserInfo(userInfo); 

如果 App 本地不持有数据,推荐在 IMKit 需要展示数据时动态提供用户信息。 

##### **获取用户信息** 

##### **流程** 

1. App 可以从 IMKit 获取缓存的用户信息。 

2. IMKit 检查本地是否有缓存用户信息。 

3. IMKit 本地有缓存,直接返回对应的用户信息。 

4. IMKit 没有缓存,就走用户信息提供者流程。 

继续走用户信息提供者的流程 

##### **实现** 

App 可以主动调用 UserDataService 的 getUserInfo 方法获取用户信息。SDK 的行为如下: 

1. 首先尝试从本地缓存获取应用层提供的数据。如果在设置用户信息提供者时,已授权 SDK 在本地数据库中存储用户信 息,SDK 还会尝试从本地数据库中获取用户信息。 

2. 如果本地没有相关信息的数据,SDK 会触发 UserInfoProvider 的 fetchUserInfo 回调方法。如果您的 App 应用层已 在该回调中提供数据,则 SDK 可成功获取用户信息 UserInfoModel 。 

###### **TypeScript** 

let userInfo = await RongIM.getInstance().userDataService().getUserInfo("userId") 

###### **群组信息** 

要在 IMKit UI 上展示群组的头像(非群成员的头像)、群名称等,需要应用层(App)主动向 IMKit SDK 提供 **群组信息** 

- 51 - 

IMKit 使用 UserDataService 类统一管理以下数据。App 需要使用 UserDataService 向 IMKit 提供数据,用于在 UI 上展 示。 

**用户信息** :包含昵称、头像 

- **群组信息** :包含群组名称、群组头像 

**群成员用户信息** :仅支持群用户昵称 

###### 提示 

用户信息、群组信息、群成员用户信息必须由应用您主动从 App 服务端获取,并提供给 IMKit SDK。融云鸿蒙 SDK 不提供 App 用户与群组信息托管服务。融云服务端的用户昵称及头像仅用于推送服务。 

本文仅描述了应用层(App)如何为 IMKit SDK 提供 **群组信息** ,以实现在 IMKit UI 上展示群组的头像(非群成员的头像)、 群名称等功能。 

##### **群组信息提供者** 

##### **设置群组信息提供者** 

使用 UserDataService 的 setUserDataProvider 方法设置群组信息提供者。必须在 SDK 初始化之后,建立 IM 连接之前 设置。建议在应用生命周期内设置。 

###### **TypeScript** 

// 设置用户信息提供者 RongIM.getInstance().userDataService().setUserDataProvider(userDataProvider); 

##### **动态提供群组信息** 

如果 IMKit 无法从 UserDataService 中获取群组名称与群组头像,将触发 UserDataProvider 的 fetchGroupInfo 回调方 法。App 应在该回调中提供 SDK 所需要的群组名称与群组头像。 

获取群组信息数据后,SDK 会自动设置、刷新群组的名称和头像,以及实现相关 UI 展示。 

###### **TypeScript** 

let userDataProvider: UserDataProvider = { 

fetchUserInfo: (userId: string): Promise<UserInfoModel> => { 

// app 拿到用户信息后通过 Promise 返给 IMKit // App 可以从数据库或者 APPServer 获取用户信息 return new Promise((resolve: Function) => { let userInfo = new UserInfoModel(userId, "用户名称", "用户头像") resolve(userInfo); }); }, 

- 52 - 

fetchGroupInfo: (groupId: string): Promise<GroupInfoModel> => { 

- // app 拿到群组信息后通过 Promise 返给 IMKit 

- // App 可以从数据库或者 APPServer 获取信息 

return new Promise((resolve: Function) => { 

let info = new GroupInfoModel(groupId, "群组名称", "群组头像") 

resolve(info); 

}); 

}, 

fetchGroupMemberInfo: (groupId: string, userId: string): Promise<GroupMemberInfoModel> => { 

- // app 拿到群组成员信息后通过 Promise 返给 IMKit 

- // App 可以从数据库或者 APPServer 获取信息 

return new Promise((resolve: Function) => { 

let info = new GroupMemberInfoModel(groupId, userId, "群成员名称", "群成员头像") resolve(info); 

}); 

}, 

fetchGroupMemberInfos: (groupId: string): Promise<Array<GroupMemberInfoModel>> => { 

- // app 拿到群组所有成员信息后通过 Promise 返给 IMKit 

- // App 可以从数据库或者 APPServer 获取信息 

return new Promise((resolve: Function) => { 

let array = new Array<GroupMemberInfoModel>(); 

for (let i = 0; i < 10; i++) { 

let userId = "userId" + i; 

let info = new GroupMemberInfoModel(groupId, userId, "群成员名称", "群成员头像") array.push(info); 

} resolve(array); 

}); 

}, 

/** 

- 是否持久化存储用户信息到 SDK 的本地数据库, 默认为 true, 

- @since 1.6.0 

*/ 

isCacheUserInfo: true, 

- /** 

- 是否持久化存储群组信息到 SDK 的本地数据库, 默认为 true, 

- @since 1.6.0 

*/ 

isCacheGroupInfo: true, 

/** 

- 53 - 

/** 

- 是否持久化存储群成员信息到 SDK 的本地数据库, 默认为 true, 

* @since 1.6.0 

*/ isCacheGroupMemberInfo: true, } 

##### **缓存策略** 

在 App 的生命周期中,如果 SDK 获取过群组的信息,便会在内存中缓存该信息。允许持久化存储后,SDK 优先从本地数据 库中获取群组信息,App 下次启动时数据仍然可用。SDK 在处理对应信息时默认行为如下: 

1. 当 SDK 需要在 UI 上显示群组信息时,首先从内存中查询已获取的数据。 

2. 如果 SDK 可从缓存或本地数据库中查询到所需信息,将直接将数据返回 UI 层并刷新 UI。 

3. 如果 SDK 未能从缓存或本地数据库查询到所需信息,则将触发 [UserDataProvider.fetchGroupInfo] 的回调方法,并 尝试从应用层获取信息。收到应用层提供的相应信息后,SDK 将刷新 UI。 

##### **刷新群组信息** 

如果 App 本地持有群组信息数据,可直接刷新本地缓存和数据库中存储的群组信息(群组名称与群组头像)。刷新后,IMKit UI 会展示最新的群组信息。 

刷新群组信息必须在 IMKit 已成功建立 IM 连接后操作,否则无法刷新本地数据。可能适用场景如下: 

- App 首次启动,并成功建立 IM 连接以后,可以将自身业务所需的用户信息批量提供给 SDK,由 SDK 写入缓存与本地 数据库,供后续使用。 

- 在 IM 建立连接后,如果群组名称、头像等信息变动,由 App 服务端通知客户端(例如使用消息),客户端调用接口刷 新群组信息。 

###### **TypeScript** 

let groupInfo = new GroupInfoModel("groupId","群名称","群头像",20,"群备注") RongIM.getInstance().userDataService().updateGroupInfo(groupInfo); 

如果 App 本地不持有数据,推荐在 IMKit 需要展示数据时动态提供群组信息。 

##### **获取群组信息** 

App 可以主动调用 UserDataService 的 getGroupInfo 方法获取群组信息。SDK 的行为如下: 

1. 首先尝试从本地缓存获取应用层提供的数据。如果在设置群组信息提供者时,已授权 SDK 在本地数据库中存储群组信 息,SDK 还会尝试从本地数据库中获取群组信息。 

2. 如果本地没有相关信息的数据,SDK 会触发 UserInfoProvider 的 fetchGroupInfo 回调方法。如果您的 App 应用层 已在该回调中提供数据,则 SDK 可成功获取群组信息。 

###### **TypeScript** 

- 54 - 

let groupInfo = await RongIM.getInstance().userDataService().getGroupInfo("groupId") 

###### **群成员用户信息** 

要在 IMKit UI 上展示群成员昵称,需要应用层(App)主动向 IMKit SDK 提供 **群成员用户信** 

**息** (GroupMemberInfoModel)。 

IMKit 使用 UserDataService 类统一管理以下数据。App 需要使用 UserDataService 向 IMKit 提供数据,用于在 UI 上展 示。 

**用户信息** :包含昵称、头像 

- **群组信息** :包含群组名称、群组头像 

**群成员用户信息** :仅支持群用户昵称 

提示 

用户信息、群组信息、群成员用户信息必须由应用您主动从 App 服务端获取,并提供给 IMKit SDK。融云鸿蒙 SDK 不提供 App 用户与群组信息托管服务。融云服务端的用户昵称及头像仅用于推送服务。 

本文仅描述了应用层(App)如何为 IMKit SDK 提供群成员昵称与头像(GroupMemberInfoModel)。 

##### **群成员用户信息提供者** 

##### **设置群成员用户信息提供者** 

使用 UserDataService 的 setUserDataProvider 方法设置群成员用户信息提供者。必须在 SDK 初始化之后,建立 IM 连 接之前设置。建议在应用生命周期内设置。 

###### **TypeScript** 

// 设置用户信息提供者 RongIM.getInstance().userDataService().setUserDataProvider(userDataProvider); 

##### **动态提供群成员用户信息** 

如果 IMKit 无法从 UserDataService 中获取群成员用户信息,将触发 UserDataProvider 的 fetchGroupMemberInfo 回 调方法。App 应在该回调中提供 SDK 所需要的群成员昵称。 

获取群成员用户信息数据后,SDK 会自动设置、群成员的群内昵称,以及实现相关 UI 展示。 

###### **TypeScript** 

- 55 - 

let userDataProvider: UserDataProvider = { 

fetchUserInfo: (userId: string): Promise<UserInfoModel> => { 

// 用户信息 

return new Promise((resolve: Function) => { 

- let userInfo = new UserInfoModel(userId, "用户名称", "用户头像") 

- resolve(userInfo); 

}); }, 

- fetchGroupInfo: (groupId: string): Promise<GroupInfoModel> => { 

- // 群信息 

return new Promise((resolve: Function) => { 

- let info = new GroupInfoModel(groupId, "群组名称", "群组头像") 

- resolve(info); 

}); 

}, 

- fetchGroupMemberInfo: (groupId: string, userId: string): Promise<GroupMemberInfoModel> => { // 群成员信息 

return new Promise((resolve: Function) => { 

   - let info = new GroupMemberInfoModel(groupId, userId, "群成员名称", "群成员头像") 

   - resolve(info); 

- }); 

}, 

- fetchGroupMemberInfos: (groupId: string): Promise<Array<GroupMemberInfoModel>> => { // 群成员列表信息 

- // App 拿到群组所有成员信息后通过 Promise 返给 IMKit,App 可以从数据库或者 APPServer 获取信息 return new Promise((resolve: Function) => { 

   - let array = new Array<GroupMemberInfoModel>(); 

   - for (let i = 0; i < 10; i++) { 

   - let userId = "userId" + i; 

   - let info = new GroupMemberInfoModel(groupId, userId, "群成员名称", "群成员头像") 

   - push(info); 

resolve(array); 

}); 

} 

} 

##### **缓存策略** 

- 56 - 

在 App 的生命周期中,如果 SDK 获取过群成员用户信息,便会在内存中缓存该信息。允许持久化存储后,SDK 优先从本地 数据库中获取群成员用户信息,App 下次启动时数据仍然可用。SDK 在处理对应信息时默认行为如下: 

1. 当 SDK 需要在 UI 上显示群成员用户信息时,首先从内存中查询已获取的数据。 

2. 如果 SDK 可从缓存或本地数据库中查询到所需信息,将直接将数据返回 UI 层并刷新 UI。 

3. 如果 SDK 未能从缓存或本地数据库查询到所需信息,则将触发 UserDataProvider 的 fetchGroupMemberInfo 回调 方法,并尝试从应用层获取信息。收到应用层提供的相应信息后,SDK 将刷新 UI。 

##### **刷新群成员用户信息** 

如果 App 本地持有群组用户信息数据(群昵称),可直接刷新本地缓存和数据库中存储的群组用户信息数据。刷新后,IMKit UI 会展示最新的群成员用户信息 GroupMemberInfoModel。 

刷新群组用户信息必须在 IMKit 已成功建立 IM 连接后操作,否则无法刷新本地数据。可能适用场景如下: 

- App 首次启动,并成功建立 IM 连接以后,可以将自身业务所需的群组用户信息批量提供给 SDK,由 SDK 写入缓存与 本地数据库,供后续使用。 

- 在 IM 建立连接后,如果群组用户昵称变动,由 App 服务端通知客户端(例如使用消息),客户端调用接口刷新群组用 户信息。 

###### **TypeScript** 

let info = new GroupMemberInfoModel("groupId", "userId", "name", "portraitUri", "alias", "extra"); RongIM.getInstance().userDataService().updateGroupMemberInfo(info); 

如果 App 本地不持有数据,推荐在 IMKit 需要展示数据时动态提供群成员用户信息。 

##### **获取群成员用户信息** 

App 可以主动调用 UserDataService 的 getGroupMemberInfo 方法获取群成员用户信息。SDK 的行为如下: 

1. 首先尝试从本地缓存获取应用层提供的数据。 

2. 如果本地没有相关信息的数据,SDK 会触发 GroupUserInfoProvider 的 fetchGroupMemberInfo 回调方法。如果 您的 App 应用层已在该回调中提供数据,则 SDK 可成功获取群成员用户信息 GroupMemberInfoModel 。 

###### **TypeScript** 

RongIM.getInstance().userDataService().getGroupMemberInfo("groupId", "userId") 

- .then((userInfo: GroupMemberInfoModel | undefined) => { 

- // 返回 GroupMemberInfoModel 

- }) 

###### **群组成员列表** 

- 57 - 

本文描述了应用层(App)如何为 IMKit SDK 提供 **群组成员** 数据,用于在群聊会话中输入 @ 符号时弹出的默认选人界面的选 人界面。设置完成后,在 IMKit UI 中上需要展示群成员列表时可正常显示群组成员的头像、用户名或群内昵称。 

提示 

用户信息、群组信息、群成员用户信息必须由应用您主动从 App 服务端获取,并提供给 IMKit SDK。融云鸿蒙 SDK 不提供 App 用户与群组信息托管服务。融云服务端的用户昵称及头像仅用于推送服务。 

##### **群组成员提供者** 

##### **设置群组成员提供者** 

使用 UserDataService 的 setUserDataProvider 方法设置群成员用户信息提供者。必须在 SDK 初始化之后,建立 IM 连 接之前设置。建议在应用生命周期内设置。 

应用开发者必须实现 UserDataProvider 的 fetchGroupMemberInfos 接口,SDK 才能获取到 App 的群组成员数据。如果 SDK 无法获取到群组成员列表,选人界面会显示为空列表。 

###### **TypeScript** 

// 设置用户信息提供者 RongIM.getInstance().userDataService().setUserDataProvider(userDataProvider); 

##### **动态提供群组成员列表** 

S在 IMKit UI 需要展示群成员列表时,会触发 UserDataProvider 的 fetchGroupMemberInfos 方法,向应用层获取群组成 员信息列表。 

###### **TypeScript** 

let userDataProvider: UserDataProvider = { 

fetchUserInfo: (userId: string): Promise<UserInfoModel> => { 

// 用户信息 return new Promise((resolve: Function) => { let userInfo = new UserInfoModel(userId, "用户名称", "用户头像") resolve(userInfo); }); }, 

fetchGroupInfo: (groupId: string): Promise<GroupInfoModel> => { 

// 群信息 return new Promise((resolve: Function) => { let info = new GroupInfoModel(groupId, "群组名称", "群组头像") resolve(info); }); 

- 58 - 

}) 

###### }, 

fetchGroupMemberInfo: (groupId: string, userId: string): Promise<GroupMemberInfoModel> => { // 群成员信息 

return new Promise((resolve: Function) => { 

let info = new GroupMemberInfoModel(groupId, userId, "群成员名称", "群成员头像") resolve(info); 

}); }, 

fetchGroupMemberInfos: (groupId: string): Promise<Array<GroupMemberInfoModel>> => { // 群成员列表信息 

- // App 拿到群组所有成员信息后通过 Promise 返给 IMKit,App 可以从数据库或者 APPServer 获取信息 return new Promise((resolve: Function) => { 

let array = new Array<GroupMemberInfoModel>(); 

for (let i = 0; i < 10; i++) { 

let userId = "userId" + i; 

let info = new GroupMemberInfoModel(groupId, userId, "群成员名称", "群成员头像") 

array.push(info); 

- } 

resolve(array); 

- }); 

}, 

/** 

- 是否持久化存储用户信息到 SDK 的本地数据库, 默认为 true, 

- @since 1.6.0 

- */ 

isCacheUserInfo: true, 

/** 

- 是否持久化存储群组信息到 SDK 的本地数据库, 默认为 true, 

- @since 1.6.0 

- */ 

isCacheGroupInfo: true, 

/** 

- 是否持久化存储群成员信息到 SDK 的本地数据库, 默认为 true, 

- @since 1.6.0 

- */ 

isCacheGroupMemberInfo: true, } 

##### **获取群成员用户信息列表** 

- 59 - 

App 可以主动调用 UserDataService 的 getGroupMemberInfos 方法获取群成员用户信息。SDK 的行为如下: 

1. 首先尝试从本地缓存获取应用层提供的数据。 

2. 如果本地没有相关信息的数据,SDK 会触发 GroupUserInfoProvider 的 fetchGroupMemberInfos 回调方法。如果 您的 App 应用层已在该回调中提供数据,则 SDK 可成功获取群成员用户信息列表 GroupMemberInfoModel 。 

###### **TypeScript** 

RongIM.getInstance().userDataService().getGroupMemberInfos("groupId") 

.then((memberInfos: GroupMemberInfoModel[] | undefined) => { 

// 群成员用户信息列表 

- }) 

### **功能特性** 

###### **图片和 GIF 消息** 

用户可以通过 IMKit 内置的图片插件发送图片消息和 GIF 消息。消息将出现在会话页面的消息列表组件中。SDK 默认发送消 息包含以下消息内容对象: 

- 图片消息内容类为 ImageMessage (类型标识: RC:ImgMsg ) 

- GIF 消息内容类为 GIFMessage (类型标识: RC:GIFMsg ) 

   - 提示 

示例图中图片消息是方角,现阶段 SDK 的图片消息是圆角。如果您需要方角的图片消息,请自定义 UI 实现。 

###### **正常图片消息** 

- 60 - 

**已读图片消息** 

- 61 - 

**失败图片消息** 

- 62 - 

##### **局限** 

仅支持发送本地图片和 GIF。 

- GIF 文件大小上限为 3 MB。 

图片消息和 GIF 消息中的文件默认会上传到融云的服务器。如需上传到自己的服务器,详见发送消息。 

##### **用法** 

扩展面板里默认带有发送图片消息入口,由 IMKit 内置的 ImagePlugin 实现。用户点击输入栏右侧 + 号按钮可展开扩展面 板,点击图片图标,即可打开本地相册,选择图片、GIF 文件进行发送。 

- 63 - 

##### **定制化** 

##### **修改默认文件保存位置** 

IMKit 目前不支持修改。 

##### **调整图片压缩质量** 

IMKit 目前不支持调整。在发送前,图片会被压缩质量,以及生成缩略图,在聊天界面中展示。GIF 无缩略图,也不会被压 缩。 

- **图片消息的缩略图** :SDK 会以原图 30% 质量生成符合标准大小要求的大图后再上传和发送。压缩后最长边不超过 240 px。缩略图用于在聊天界面中展示。 

- **图片** :发送消息时如未选择发送原图,SDK 会以原图 85% 质量生成符合标准大小要求的大图后再上传和发送。压缩后 最长边不超过 1080 px。 

##### **自定义图片、 GIF 消息的 UI** 

图片消息与 GIF 消息默认使用以下模板展示在消息列表中。 

- ImageMessageItemProvider 

- GIFMessageItemProvider 

如果需要调整内置消息样式,需继承 BaseMessageItemProvider<ImageMessage> 或 BaseMessageItemProvider<GIFMessage> 自行实现消息展示模板类,详见自定义Provider。 

调用 addMessageItemProvider 的接口将该自定义模板提供给 SDK,图片消息 objectName 传 ImageMessageObjectName,GIF消息 objectName 传 GIFMessageObjectName。 

###### **TypeScript** 

- 64 - 

import { ImageMessageObjectName, GIFMessageObjectName, RongIM } from "@rongcloud/imkit"; 

###### // 注册自定义图片消息 provider 给 IMKit 

RongIM.getInstance().conversationService().addMessageItemProvider(ImageMessageObjectName, new CustomImageMessageItemProvider()) 

// 注册自定义GIF消息 provider 给 IMKit 

RongIM.getInstance().conversationService().addMessageItemProvider(GIFMessageObjectName, new CustomGIFMessageItemProvider()) 

##### **隐藏扩展面板中的图片入口** 

IMKit 目前暂不支持隐藏。 

###### **小视频消息** 

用户可以通过 IMKit 图库(本地相册)或小视频插件发送小视频消息。消息将出现在会话页面的消息列表组件中。插件默认发 送的消息包含小视频消息内容对象 SightMessage(类型标识:RC:SightMsg)。 

- 65 - 

##### **局限性** 

###### 小视频功能目前存在以下限制: 

- IMKit 仅单聊会话和群聊会话支持发送小视频消息。 

- 如果使用小视频插件进行录制,支持录制长度不超过 10 秒的小视频。 

- 如果从本地相册中选择视频文件,请注意服务端的默认视频时长上限为 2 分钟。如需调整上限,请联系商务。 

- 仅支持 H.264 + AAC 编码的视频文件,因为 IMKit 的短视频录制、播放只实现了该编码组合的支持。注意:mp4 格 式的视频可以播放并保存到相册,avi/rmvb 格式的视频可以播放,但是无法保存到相册。 

- 如果 App Key 使用 **IM 旗舰版** 或 **IM 尊享版** ,文件存储时长默认为 180 天(不含小视频文件,小视频文件存储 7 天)。注意, **IM 商用版(已下线)默认存储 7 天。如需了解 IM 旗舰版** 或 **IM 尊享版** 的具体功能与费用,请参见融云官 方价格说明页面及计费说明。 

- 66 - 

##### **用法** 

建议通过集成 IMKit 小视频插件使用小视频消息功能。 

##### **从本地相册选择小视频** 

用户点击输入栏右侧 + 号按钮可展开扩展面板,点击 **相册** 图标,打开本地相册时,默认包含视频文件,用户可以选择视频文 件进行发送。 

本地相册使用鸿蒙内置本地相册模块:https://developer.huawei.com/consumer/cn/doc/harmonyos-referencesV13/js-apis-photoaccesshelper-V13 

##### **录制小视频消息** 

用户点击输入栏右侧 + 号按钮可展开扩展面板,点击 **小视频** 图标,即可录制小视频并发送小视频消息。 

小视频的录制使用了鸿蒙内置模块:https://developer.huawei.com/consumer/cn/doc/harmonyos-guidesV5/camera-picker-V5 

##### **定制化** 

##### **调整小视频压缩质量** 

小视频文件默认不会压缩。 小视频首帧画面会被用于生成缩略图,在聊天界面中展示。SDK 默认以原图 80% 质量生成符合 标准大小要求的缩略图后再上传和发送,缩略图最长边不超过 240 px。 

##### **自定义小视频消息的 UI** 

小视频消息使用 SightMessageItemProvider 模板展示在消息列表中。 如果需要调整内置消息样式,需继承 BaseMessageItemProvider<SightMessage> 自行实现消息展示模板类,详见自定义Provider。 

调用下面的接口将该自定义模板提供给 SDK,objectName 传 SightMessageObjectName。 

**TypeScript** 

- 67 - 

import { SightMessageObjectName, RongIM } from "@rongcloud/imkit"; 

// 注册自定义文件消息 provider 给 IMKit 

RongIM.getInstance().conversationService().addMessageItemProvider(SightMessageObjectName, new CustomSightMessageItemProvider()) 

##### **隐藏小视频插件的录制视频功能** 

IMKit 目前暂不支持隐藏。 

##### **隐藏相册插件中的视频文件** 

IMKit 目前暂不支持隐藏。 

###### **语音消息** 

用户可以通过 IMKit 内置的输入组件录制并发送语音消息。消息将出现在会话页面的消息列表组件中。SDK 默认生成和发送 的消息包含高清语音消息内容对象 HQVoiceMessage(类型标识:RC:HQVcMsg)。 

- 68 - 

##### **局限性** 

语音输入功能目前存在以下限制: 

IMKit 仅单聊会话和群聊会话支持发送语音消息。 

用户必须录制至少为 1 秒的音频内容,且必须短于 60 秒钟。 

用户在录制语音消息时无法暂停。 

正在视频通话和语音通话中不能进行语音消息发送。 

##### **用法** 

IMKit 默认在输入栏组件中启用语音消息输入功能。输入栏中默认带有切换语音输入按钮。 

- 69 - 

##### **发送语音消息** 

默认情况下,语音消息图标显示在输入字段的左侧。点击此图标后,就会出现录制按钮(“按住说话”)。用户可以通过点击录 制按钮来录制语音消息。 

录制语音的长度必须至少为 1 秒且短于 60 秒钟。如果在点击停止按钮之前消息不到 1 秒,则不会保存该消息。录制过程中 可以上滑取消录制或放弃取消。一旦松开按钮,SDK 默认发送到目前为止录制的内容。不支持在发送语音消息之前预览且在 播放语音消息中的音频文件时不可暂停。 

##### **消息列表中的语音消息** 

您可以在单聊会话、群聊会话、系统会话中接收语音消息。语音消息显示在消息列表中。 用户可以通过点击播放按钮查看和播放语音消息。未播放的语音消息旁边会显示一个红点,消息可多次播放。但是,用户只能 

- 70 - 

在客户端应用程序中收听语音消息,并且无法将其保存到自己的设备中。 

您在会话页面中一次只能收听一条音频文件,如果您在收听消息时尝试播放另一条消息,则先播放的消息将暂停。 

##### **配置高清语音连续播放** 

IMKit 默认点击播放后连续播放消息下方未收听的语音消息。您可以修改全局配置,设置未听的语音消息不连续播放: 

###### **示例代码** 

###### **TypeScript** 

- 71 - 

let config = RongIM.getInstance().conversationService().getConversationConfig() config.setEnablePlayAudioContinuous(false) 

RongIM.getInstance().conversationService().setConversationConfig(config) 

##### **配置自动下载高清语音** 

IMKit 在线时默认自动下载高清语音消息(1.4.3版本开始支持)。您可以通过全局配置禁用该行为: 

###### **示例代码** 

###### **TypeScript** 

let config = RongIM.getInstance().conversationService().getConversationConfig() config.setEnableAutoDownloadHQVoice(false) RongIM.getInstance().conversationService().setConversationConfig(config) 

##### **定制化** 

##### **自定义语音消息的 UI** 

语音消息使用 HQVoiceMessageItemProvider 模板展示在消息列表中。 如果需要调整内置消息样式,需继承 BaseMessageItemProvider<HQVoiceMessage> 自行实现消息展示模板类,详见自定义Provider。 

调用 addMessageItemProvider 的接口将该自定义模板提供给 SDK,objectName 传 HQVoiceMessageObjectName。 

###### **TypeScript** 

import { HQVoiceMessageObjectName, RongIM } from "@rongcloud/imkit"; // 注册自定义文件消息 provider 给 IMKit 

RongIM.getInstance().conversationService().addMessageItemProvider(HQVoiceMessageObjectName, new CustomHQVoiceMessageItemProvider()) 

###### **文件消息** 

用户可以通过 IMKit 内置的文件插件发送文件消息。消息将出现在会话页面的消息列表组件中。文件插件默认发送的消息包含 文件消息内容对象 [FileMessage](类型标识:RC:FileMsg) 

- 72 - 

##### **局限** 

仅支持发送本地文件。 

文件消息中的文件默认会上传到融云的服务器。如需上传到自己的服务器,详见发送消息。 

不支持在 IMKit 中预览文件,请在 UI 中选择用其他应用打开。 

##### **用法** 

IMKit 内置的 FilePlugin 实现了扩展面板中的文件消息功能。 

##### **发送文件消息** 

扩展面板里默认带有发送文件消息入口。用户点击输入栏右侧 + 号按钮可展开扩展面板,点击文件图标,即可发送文件消 

- 73 - 

息。 

##### **定制化** 

##### **修改默认文件保存位置** 

IMKit 目前不支持修改。 

##### **替换文件消息默认的文件图标** 

文件消息(FileMessage)在会话界面中显示时,会根据消息携带的文件类型展示匹配的图标。SDK 默认为以下类型的文件 提供了匹配的图标,如果为其他类型文件,则默认显示统一的默认图标。 

- **图片类** :jpg、png、gif、jpeg 

- **文本类** :txt 

- **视频类** :rmvb、mp4 

- **音频类** :mp3 

- **Word 类** :doc、docx 

- **PPT 类** :ppt、pptx 

- **Excel 类** :xls、xlsx 

- **PDF 类** :pdf 

- **Apk 类** :apk 

- **Numbers 类** :numbers 

- **Pages 类** :pages 

SDK 支持 App 修改文件类型(扩展名)对应显示的图标。App 可以按需更新指定图标,替换全部图标,或增加文件类型(扩 展名)及图标。详见设置文件类型图标。 

##### **自定义文件消息的 UI** 

文件消息使用 FileMessageItemProvider 模板展示在消息列表中。 如果需要调整内置消息样式,需继承 BaseMessageItemProvider<FileMessage> 自行实现消息展示模板类,详见自定义Provider。 

- 74 - 

调用下面的接口将该自定义模板提供给 SDK,objectName 传 FileMessageObjectName。 

###### **TypeScript** 

import { FileMessageObjectName, RongIM } from "@rongcloud/imkit"; 

// 注册自定义文件消息 provider 给 IMKit RongIM.getInstance().conversationService().addMessageItemProvider(FileMessageObjectName, new CustomFileMessageItemProvider()) 

##### **替换文件消息插件** 

IMKit 默认在扩展面板中启用了文件消息入口。如需动态修改,需要实现 IBoardPlugin 进行自定义插件,详见自定义插件。 

###### **TypeScript** 

let plugin = new CustomFilePlugin() let filePluginIndex = 2 RongIM.getInstance().conversationService().replaceBoardPlugin(filePluginIndex, plugin) 

##### **隐藏文件消息插件** 

IMKit 目前暂不支持隐藏。 

###### **位置消息** 

IMKit 基于高德地图 SDK 提供了位置消息,实现了应用地图预览功能。 

SDK 默认发送的消息包含位置消息内容对象 LocationMessage (类型标识: RC:LBSMsg )。 

###### 提示 

IMKit 默认会话页面未启用位置功能。如需要使用位置功能,需要自定义位置插件开发。下面提供了示例代码进行参 考。 

- 75 - 

##### **发送位置消息** 

通过自定义位置消息插件,在扩展面板里会自动生成位置消息入口。用户点击输入栏右侧 + 号按钮可展开扩展面板,点击位 置图标,即可发送位置消息。 

示例基于鸿蒙 Map Kit SDK,集成于配置请参照鸿蒙开发文档。 

- 76 - 

##### **自定义位置插件** 

LocationPlugin 是提供给开发者借鉴的位置插件示例代码。开发者需要在 sendLocation 方法中编写跳转 LocationPage 的 代码。 

###### **TypeScript** 

```arkts
import { ArrayChecker, ConversationIdentifier } from '@rongcloud/imlib'; import { IBoardPlugin } from '@rongcloud/imkit'; import { PermissionsUtil } from '../../../utils/PermissionsUtil'; import { LocationParams, SelectLocationType } from '../model/LocationParams'; import { common, Permissions } from '@kit.AbilityKit'; 
```

/** 

* 加号扩展栏的位置插件 * @version 1.0.0 */ export class LocationPlugin implements IBoardPlugin { 

obtainTitle(context: Context): ResourceStr { return $r("app.string.rc_location"); } obtainImage(context: Context): ResourceStr { return $r("app.media.rc_input_bar_plugin_location"); } 

onClick void { 

//先检查收否授权地图权限,没有授权的话去设置权限 const permissionArray: Permissions[] = [ 'ohos.permission.LOCATION', 

'ohos.permission.APPROXIMATELY_LOCATION' ]; 

- 77 - 

PermissionsUtil.checkPermissions(permissionArray) 

.then((array: Permissions[]) => { //已经授权 if (array.length === 0) { // 发送位置页面 this.sendLocation(conId); } else { // 没授权,需要申请权限 PermissionsUtil.requestPermissionsFromUser(getContext(this) as common.UIAbilityContext, permissionArray) 

.then((permissions: Array<Permissions>) => { if (ArrayChecker.isValid(permissions)) { 

PermissionsUtil.requestPermissionOnSetting(getContext(this) as common.UIAbilityContext, permissionArray); } else { // 发送位置页面 this.sendLocation(conId); } }); } }); } /** * 发送位置页面 */ private sendLocation(conId: ConversationIdentifier) { 

```arkts
let param: LocationParams = { conId: conId, flag: SelectLocationType.Send } // 跳转到 LocationPage 页面,携带 LocationParams 参数。 } onFilter(conId: ConversationIdentifier): boolean { return true; } } 
```

##### **添加自定义插件到扩展面板** 

###### 添加位置插件到最后位置。 

###### **TypeScript** 

let plugin = new LocationPlugin() RongIM.getInstance().conversationService().addBoardPlugin(plugin) 

- 78 - 

也可以把位置插件插入到指定位置。 

###### **TypeScript** 

let plugin = new LocationPlugin() let filePluginIndex = 1 RongIM.getInstance().conversationService().replaceBoardPlugin(filePluginIndex, plugin) 

##### **发送位置 / 查看位置页面示例** 

LocationPage 是提供给开发者借鉴的发送位置/查看位置示例代码。 

- 支持通过自定义位置插件跳转到此页面,选择位置并发送 LocationMessage ,见 returnSelectLocation 方法。 支持通过点击 LocationMessage 的 UI 跳转到此页面,查看位置。见 自定义位置消息UI。 需要 App 侧在 backPage 方法处理返回上个页面的逻辑。 

###### **TypeScript** 

```arkts
import { ConversationIdentifier, LocationCoordinateType, LocationMessage, Message, RCTitleBar, RongIM, StringChecker } from '@rongcloud/imkit'; import { LocationData } from '../model/LocationData'; import { LocationParams } from '../model/LocationParams'; import { map, mapCommon, MapComponent, site, static Map } from '@kit.MapKit'; import { AsyncCallback, BusinessError } from '@kit.BasicServicesKit'; import { geoLocationManager } from '@kit.LocationKit'; import { router } from '@kit.ArkUI'; import { common, Want } from '@kit.AbilityKit'; import { connection } from '@kit.NetworkKit'; import { image } from '@kit.ImageKit'; import { buffer } from '@kit.ArkTS'; 
```

@Entry @Component export struct LocationPage { // 网络状态 

@State isNetwork: boolean = false; private netCon: connection.NetConnection | undefined; 

// 地图属性 

private mapOptions?: mapCommon MapOptions; 

- 79 - 

private mapOptions?: mapCommon.MapOptions; private callback?: AsyncCallback<map.MapComponentController>; 

private mapController?: map.MapComponentController; 

private mapEventManager?: map.MapEventManager; 

// 当前位置 

private myLatLng: mapCommon.LatLng = LocationHelper.defaultLatLng; 

// 展示的周边列表数据 

@State locationList: Array<LocationData> = []; 

private pageIndexDefault: number = 1; 

// 页码 

private pageIndex: number = this.pageIndexDefault; 

// 每页数量 

private pageSize: number = 20; 

private locationIndexDefault: number = 0; 

// 选择的位置下标 

@State 

private locationIndex: number = -1; 

###### // 是否在获取周边数据 

private nearbySearchType: boolean = false; 

// app内主动移动地图的次数,如果是app内主动移动地图,不需要在地图移动后获取位置信息和周边 

// 初始值为1,是在地图初始化后,会自动回调一下地图移动的回调 

private appRemoveNum: number = 1; 

@State 

private selectAddress: string = ''; 

- // 是否只展示地图 

private isOnlyShowMap: boolean = false; 

- // 地图所需参数 

private locationParams?: LocationParams; 

// 错误码 

private errorCode: string = '' 

// 会话ID 

private conId: ConversationIdentifier = new ConversationIdentifier(); 

// 标题栏 

- @State model: RCTitleBar.Model = new RCTitleBar.Model() 

- .setTitleName(getContext().resourceManager.getStringByNameSync('rc_location')) 

- .setTitleFontSize(18) 

- .setLeftIcon($r("app.media.rc_title_bar_back")) 

- .setRightTitleName(getContext().resourceManager.getStringByNameSync('rc_chat_send')) 

- .setRightTitleFontColor(this.isNetwork ? $r('app.color.rc_color_0195ff') : $r('app.color.rc_color_C7CCD4')) .setOnLeftClickListener(() => { 

this.backPage() 

- }) 

- .setOnRightClickListener(() => { 

if (!this.isNetwork) { 

return; } 

- 80 - 

} 

if (this.errorCode === '3301100') { 

return; 

- } 

if (this.locationIndex === -1) { 

return; 

- } 

if (!this.locationList.length) { 

return; 

- } 

this.returnSelectLocation(); 

- }) 

aboutToAppear(): void { 

- // 网络监听 

this.networkListen() 

- // 获取路由参数 

if (router.getParams()) { 

this.locationParams = router.getParams() as LocationParams; 

- if (this.locationParams.conId && this.locationParams.flag == 1) { 

- this.conId.targetId = this.locationParams.conId?.targetId! 

- this.conId.conversationType = this.locationParams.conId?.conversationType! 

- } else if (this.locationParams.locationData && this.locationParams.flag == 2) { 

- if (this.locationParams.locationData) { 

- // 有位置数据,只展示地图和标记当前要显示的位置 

this.isOnlyShowMap = !this.isOnlyShowMap; 

this.model.setRightTitleName('') 

- } 

- } 

- } 

- // 地图初始化参数,设置地图中心点坐标及层级 

this.initMapData() 

- } 

private initMapData() { 

- // 地图参数 

this.mapOptions = LocationHelper.getMapInitOption(this.isOnlyShowMap); 

- // 地图初始化的回调 

this.callback = async (err, mapController) => { 

if (!err) { 

- // 获取地图的控制器类,用来操作地图 

this.mapController = mapController; 

this.mapEventManager = this.mapController.getEventManager(); 

this.mapEventManager.on('error', (err: BusinessError) => { 

- }); 

//地图加载事件 

- 81 - 

// 地图加载事件 

let mapLoadCallback = () => { 

- //地图加载完成获取定位信息, 

if (!this.isOnlyShowMap) { 

this.getMyLocation(); 

###### } else { 

if (this.mapController !== undefined) { 

LocationHelper.animateCamera(this.locationParams?.locationData?.latitude!, 

- this.locationParams?.locationData?.longitude!, this.mapController); 

LocationHelper.addPointAnnotation(this.locationParams?.locationData?.latitude!, 

this.locationParams?.locationData?.longitude!, this.locationParams?.locationData?.name!, this.mapController); 

} 

} 

}; 

this.mapEventManager.on("mapLoad", mapLoadCallback); 

// 相机移动结束事件 

let cameraIdleCallback = () => { 

// 如果是app内主动移动地图,不需要获取信息 

if (this.appRemoveNum > 0) { 

this.appRemoveNum--; 

return; 

} 

- //获取地图移动后的中心点 

let position: mapCommon.CameraPosition = this.mapController?.getCameraPosition() as mapCommon.CameraPosition; 

this.getLocationDetail(position.target.latitude, position.target.longitude); 

}; 

if (!this.isOnlyShowMap) { 

this.mapEventManager.on("cameraIdle", cameraIdleCallback); 

} 

// 我的位置按钮点击事件 

let myLocationButtonClickCallback = () => { 

this.getMyLocation(); 

}; 

this.mapEventManager.on("myLocationButtonClick", myLocationButtonClickCallback); // 启用我的位置图层 

this.mapController.setMyLocationEnabled(!this.isOnlyShowMap); 

// 启用我的位置按钮 

this.mapController.setMyLocationControlsEnabled(!this.isOnlyShowMap); 

} else { 

} 

}; 

} 

/** 

- 82 - 

/ 

###### * 获取当前位置,并移动地图到当前位置 

*/ 

private getMyLocation() { 

try { 

let currentLocation = geoLocationManager.getCurrentLocation(); 

if (!currentLocation) { 

- return; 

- } 

// 获取用户位置坐标 

currentLocation.then((location: geoLocationManager.Location) => { 

// 设置用户的位置 

// TODO location参数需使用WGS84坐标系。 

this.mapController?.setMyLocation(location); 

let gcj02Position = LocationHelper.wgs84ToGcj02(location.latitude, location.longitude); 

this.myLatLng.latitude = gcj02Position.latitude; 

this.myLatLng.longitude = gcj02Position.longitude; 

if (this.mapController !== undefined) { 

this.appRemoveNum++; 

LocationHelper.animateCamera(this.myLatLng.latitude, this.myLatLng.longitude, this.mapController); } 

this.getLocationDetail(this.myLatLng.latitude, this.myLatLng.longitude); 

}) this.errorCode = ''; 

} catch (e) { 

this.errorCode = e.code; 

if (this.errorCode === '3301100') { 

this.model.setRightTitleFontColor($r('app.color.rc_color_C7CCD4')) 

this.showLocationDialog(); 

} } } 

private showLocationDialog() { AlertDialog.show({ title: '温馨提示', ' ' message: 位置开关已被关闭,打开后才能正常发送 , autoCancel: true, alignment: DialogAlignment.Center, primaryButton: { value: '去开启', fontColor: $r('app.color.rc_color_0195ff'), action: () => { this.openSetting(); 

- 83 - 

g(); 

p 

} 

}, 

cornerRadius: 12, 

width: '80%', 

}); 

} 

###### private openSetting() { 

let context = getContext(this) as common.UIAbilityContext; 

let want: Want = { 

bundleName: 'com.huawei.hmos.settings', //设置应用bundleName 

abilityName: 'com.huawei.hmos.settings.MainAbility', //设置应用abilityName 

uri: "location_manager_settings" 

} context.startAbility(want) 

} 

/** 

* 逆地理编码,根据当前位置经纬度获取详细信息 */ 

###### private getLocationDetail(latitude: number, longitude: number) { 

//重置显示数据 this.errorCode = ''; this.locationList = []; this.pageIndex = this.pageIndexDefault; 

this.locationIndex = this.locationIndexDefault; 

LocationHelper.reverseGeocode(latitude, longitude).then((result: LocationData) => { 

this.selectAddress = result.name; this.locationList.push(result); this.nearbySearch(); 

}) } 

/** * 周边搜索 */ 

###### private nearbySearch() { 

if (this.locationList.length > 0 && this.locationList.length > 0) { 

LocationHelper.nearbySearch(this.locationList[0].latitude, this.locationList[0].longitude, this.pageIndex, this.pageSize) .then((value: Array<LocationData>) => { this.locationList.push(...value); if (this.nearbySearchType) { this.nearbySearchType = !this.nearbySearchType; } 

- 84 - 

}); 

} 

} 

- // 页面每次显示时触发一次,包括路由过程、应用进入前台等场景,仅@Entry装饰的自定义组件生效 onPageShow(): void { 

- // 将地图切换到前台 

if (this.mapController !== undefined) { 

this.mapController.show(); 

- } 

if (this.errorCode === '3301100') { 

if (connection.hasDefaultNetSync()) { 

this.isNetwork = true; 

this.model.setRightTitleFontColor($r('app.color.rc_color_0195ff')) 

- //获取地图移动后的中心点 

let position: mapCommon.CameraPosition = this.mapController?.getCameraPosition() as mapCommon.CameraPosition; 

if (position) { 

this.getLocationDetail(position.target.latitude, position.target.longitude); 

} 

} 

} } 

- // 页面每次隐藏时触发一次,包括路由过程、应用进入后台等场景,仅@Entry装饰的自定义组件生效。 onPageHide(): void { 

- // 将地图切换到后台 

if (this.mapController !== undefined) { 

- // TODO 模拟器加载地图调用此api会崩溃,先抛出 

try { 

this.mapController.hide(); 

} catch (e) { 

console.error(JSON.stringify(e)); 

} 

} 

} 

build() { Column() { 

RCTitleBar({ model: this.model }) 

RelativeContainer() { 

- // 调用MapComponent组件初始化地图 

MapComponent({ mapOptions: this.mapOptions, mapCallback: this.callback }) 

- 85 - 

if (!this.isOnlyShowMap) { Row() { Image($r('sys.media.ohos_ic_public_location')) .width(20) .height(20) Text(this.selectAddress) .layoutWeight(1) } 

.backgroundColor(Color.White) .width('80%') .padding(10) .margin({ top: 10 }) .alignRules({ middle: { anchor: '__container__', align: HorizontalAlign.Center } }) 

Image($r('app.media.rc_map_location_mark')) 

.objectFit(ImageFit.Auto) 

.width(24) .height(58) .alignRules({ center: { anchor: '__container__', align: VerticalAlign.Center }, middle: { anchor: '__container__', align: HorizontalAlign.Center } }) } } .width('100%') .layoutWeight(2) 

if (!this.isOnlyShowMap) { List() { ForEach(this.locationList, (item: LocationData, index: number) => { ListItem() { Row() { Column() { 

Text(item.name) layoutWeight(1) width('100%') 

Text(item.address) width('100%') fontColor(Color.Grey) fontSize(14) maxLines(1) 

- 86 - 

.textOverflow({ overflow: TextOverflow.Ellipsis }) 

.margin({ top: 10 }) 

.visibility(item.address ? Visibility.Visible : Visibility.None) 

} 

.padding(10) 

.height(70) 

.layoutWeight(1) 

Image($r('sys.media.ohos_ic_public_ok_filled')) 

.width(15) 

.height(15) 

.visibility(index === this.locationIndex ? Visibility.Visible : Visibility.None); 

} 

} 

.margin({ right: 20 }) 

.onClick(() => { 

this.locationIndex = index; 

this.selectAddress = item.name 

this.appRemoveNum++; 

LocationHelper.animateCamera(item.latitude, item.longitude, this.mapController!); }) 

}, (item: LocationData, index: number) => { 

return `${item.latitude}${item.longitude}${index}`; 

}) 

} 

.divider({ strokeWidth: 1 }) 

.onScrollVisibleContentChange((start: VisibleListContentInfo, end: VisibleListContentInfo) => { 

//滑动到最后一个item,查询后边的数据 

if (end.index !== this.locationList.length - 1) { 

return; 

} this.searchNextPage(); 

}) 

.layoutWeight(1) 

} 

} 

} 

// 返回上个页面 

private backPage() { // 处理返回上个页面 

} 

/** 

- 87 - 

* 继续搜索下一页数据 

*/ 

private searchNextPage() { 

if (!this.nearbySearchType) { 

this.nearbySearchType = !this.nearbySearchType; 

this.pageIndex++; 

this.nearbySearch(); 

} 

} 

/** 

* 返回选择的位置 

*/ 

###### private returnSelectLocation() { 

LocationHelper.getMapImage(this.locationList[this.locationIndex].latitude, 

- this.locationList[this.locationIndex].longitude).then((value: PixelMap) => { // 返回数据给上个页面 

let selectLocation: LocationData = this.locationList[this.locationIndex]; 

ImageUtil.pixelMapToBase64(value).then((base64: string) => { selectLocation.img = base64; 

let locationMessage: LocationMessage = new LocationMessage(); locationMessage.latitude = selectLocation.latitude; 

locationMessage.longitude = selectLocation.longitude; 

locationMessage.poi = selectLocation.name; 

locationMessage.thumbnailBase64 = selectLocation.img!; 

locationMessage.type = LocationCoordinateType.GCJ02; 

let msg = new Message(this.conId, locationMessage); 

RongIM.getInstance().messageService().sendMessage(msg); 

router.back(); 

- }); 

- }); 

} 

private networkListen() { 

this.netCon = connection.createNetConnection(); 

this.netCon.register((error: BusinessError) => { 

if (error) { 

console.log('networkListen fail' + JSON.stringify(error)) 

return; 

- } 

- }); 

this.netCon.on('netAvailable', (data: connection.NetHandle) => { 

console.info("Succeeded to get netAvailable: " + JSON.stringify(data)); if (connection.hasDefaultNetSync()) { 

- 88 - 

this.isNetwork = true; 

this.model.setRightTitleFontColor($r('app.color.rc_color_0195ff')) 

//获取地图移动后的中心点 

let position: mapCommon.CameraPosition = this.mapController?.getCameraPosition() as mapCommon.CameraPosition; 

if (position) { 

this.getLocationDetail(position.target.latitude, position.target.longitude); 

} 

} 

}); 

###### // 订阅网络丢失事件 

this.netCon.on('netLost', (data: connection.NetHandle) => { 

if (connection.getAllNetsSync().length == 0) { 

this.isNetwork = false; 

this.model.setRightTitleFontColor($r('app.color.rc_color_C7CCD4')) 

} 

console.info("Succeeded to get netLost: " + JSON.stringify(data)); 

}); 

this.netCon.on('netCapabilitiesChange', (data: connection.NetCapabilityInfo) => { 

console.info("Succeeded to get netCapabilitiesChange: " + JSON.stringify(data)); 

}); 

this.netCon.on('netUnavailable', () => { 

console.info("Succeeded to get unavailable net event"); 

this.isNetwork = false; 

this.model.setRightTitleFontColor($r('app.color.rc_color_C7CCD4')) 

}); 

} 

aboutToDisappear(): void { 

this.netCon?.unregister((error: BusinessError) => { 

console.log(JSON.stringify(error)); 

}); 

} 

} 

export class LocationHelper { 

- // 地图默认中心点纬度北京 

private static centerDefaultLat: number = 39.9042; 

- // 地图默认中心点经度北京 

private static centerDefaultLon: number = 116.4074; 

- 89 - 

public static defaultLatLng: mapCommon.LatLng = 

{ latitude: LocationHelper.centerDefaultLat, longitude: LocationHelper.centerDefaultLon }; 

// 地图默认展示的层级 

private static centerDefaultZoom: number = 10; 

// 移动地图到某一点的图层 

private static animateCameraDefaultZoom: number = 15; 

// 输入语言 

private static language: string = "zh"; 

- // 逆地理编码搜索半径 

private static reverseGeocodeRadius: number = 10; 

- // 周边搜索半径 

private static nearbySearchRadius: number = 5000; 

- // 地图移动到指定经纬度的时长 

private static animateCameraDuration: number = 500; 

- // 静态图的图层 

private static mapImageZoom: number = 17; 

- // 静态图的宽高 

private static mapImageWidth: number = 300; 

private static mapImageHeight: number = 200; 

// 静态图的比例 

private static mapImageScale: number = 1; 

/** 

- 地图初始化参数 

* @returns 

*/ 

public static getMapInitOption(isOnlyShowMap: boolean): mapCommon.MapOptions { let mapOptions: mapCommon.MapOptions = { 

position: { 

target: LocationHelper.defaultLatLng, 

zoom: LocationHelper.centerDefaultZoom 

}, 

// 设置地图深色模式 

dayNightMode: mapCommon.DayNightMode.AUTO, 

- // 是否展示我的位置按钮,默认值:false 

myLocationControlsEnabled: !isOnlyShowMap, 

- // 是否展示指南针控件,默认值:true 

compassControlsEnabled: false, 

// 是否展示缩放控件,默认值:true 

zoomControlsEnabled: false 

}; 

return mapOptions; 

} 

/** 

纬度转 转为 

- 90 - 

* 经纬度转换,wgs84转为gcj02 

*/ 

public static wgs84ToGcj02(lat: number, lon: number): mapCommon.LatLng { 

let wgs84Position: mapCommon.LatLng = { 

latitude: lat, 

longitude: lon }; 

// 转换经纬度坐标 

let gcj02Position: mapCommon.LatLng = 

map.convertCoordinateSync(mapCommon.CoordinateType.WGS84, mapCommon.CoordinateType.GCJ02, wgs84Position); 

return gcj02Position; 

} 

/** 

- 逆地理编码,最终返回页面列表显示的数据 

- @param lat 

* @param lon 

* @returns 

*/ 

public static reverseGeocode(lat: number, lon: number): Promise<LocationData> { return new Promise((resolve) => { 

let params: site.ReverseGeocodeParams = { 

// 位置经纬度 location: { latitude: lat, longitude: lon }, isExtension: true, 

language: LocationHelper.language, 

radius: LocationHelper.reverseGeocodeRadius }; 

site.reverseGeocode(params).then((result: site.ReverseGeocodeResult) => { 

let addressName: string = ""; 

let addressLatitude: number = lat; 

let addressLongitude: number = lon; 

let pois: Array<site.ReverseGeocodePoi> = result.pois as Array<site.ReverseGeocodePoi>; if (pois) { 

addressName = StringChecker.getStringSafety(pois[0].name); 

addressLatitude = pois[0].location?.latitude as number; 

addressLongitude = pois[0].location?.longitude as number; 

} else { 

let aois: Array<site.Aoi> = result.aois as Array<site.Aoi>; 

if (aois) { 

addressName = StringChecker.getStringSafety(aois[0].name); 

dd L tit d i [0] l ti ? l tit d b 

- 91 - 

addressLatitude = aois[0].location?.latitude as number; 

addressLongitude = aois[0].location?.longitude as number; 

} else { let roads: Array<site.Road> = result.roads as Array<site.Road>; if (roads) { addressName = StringChecker.getStringSafety(roads[0].name); 

addressLatitude = roads[0].location?.latitude as number; 

addressLongitude = roads[0].location?.longitude as number; 

} else { addressName = result.addressDescription; } } } 

```arkts
let resultData: LocationData = { latitude: addressLatitude, longitude: addressLongitude, name: addressName }; 
```

resolve(resultData); 

}); }); } 

/** 

* 周边搜索 * @param lat 

* @param lon 

* @param pageIndex 

* @param pageSize */ 

public static nearbySearch(lat: number, lon: number, pageIndex: number, 

```arkts
pageSize: number): Promise<Array<LocationData>> { return new Promise((resolve) => { let list: Array<LocationData> = []; let params: site.NearbySearchParams = { // 经纬度坐标 location: { latitude: lat, longitude: lon }, // 指定地理位置的范围半径 radius: LocationHelper.nearbySearchRadius, language: LocationHelper.language, pageIndex: pageIndex, pageSize: pageSize }; 
```

// 返回周边搜索结果 

site.nearbySearch(params).then((result: site.NearbySearchResult) => { lt it ? f E h((it it Sit ) > { 

- 92 - 

result.sites?.forEach((item: site.Site) => { push({ 

latitude: item.location?.latitude as number, 

longitude: item.location?.longitude as number, 

name: StringChecker.getStringSafety(item.name), 

address: StringChecker.getStringSafety(item.formatAddress) 

resolve(list); 

}); 

} 

/** 

- 根据关键词搜索地点 

- @param searchKey 

- @returns 

*/ 

public static searchByTextAndLocation(searchKey: string, location?: mapCommon.LatLng): Promise<Array<LocationData>> { 

return new Promise((resolve) => { 

- let list: Array<LocationData> = []; 

- let params: site.SearchByTextParams = { 

// 指定关键字 

query: searchKey, 

location: location, language: LocationHelper.language 

// 返回关键字搜索结果 

searchByText(params).then((result: site.SearchByTextResult) => { 

result.sites?.forEach((item: site.Site) => { 

push({ 

latitude: item.location?.latitude as number, 

longitude: item.location?.longitude as number, 

name: StringChecker.getStringSafety(item.name), 

address: StringChecker.getStringSafety(item.formatAddress) 

resolve(list); 

}); } 

/** 

- 移动地图到指定的经纬度 

*@param lat 

- 93 - 

* @param lat 

* @param lon 

* @param mapController 

*/ 

public static animateCamera(lat: number, lon: number, mapController: map.MapComponentController) { let latLng: mapCommon.LatLng = { 

latitude: lat, longitude: lon }; 

let cameraUpdate: map.CameraUpdate = map.newLatLng(latLng, 

LocationHelper.animateCameraDefaultZoom); 

- // 以动画方式移动地图相机 

mapController.animateCamera(cameraUpdate, LocationHelper.animateCameraDuration); 

- } 

/** 

- 获取地图静态图 

- @param lat 

- @param lon 

- @returns 

*/ 

public static getMapImage(lat: number, lon: number): Promise<PixelMap> { 

return new Promise((resolve) => { 

- // 设置静态图标记参数 

let markers: Array<staticMap.StaticMapMarker> = [{ 

location: { 

latitude: lat, longitude: lon }, defaultIconSize: staticMap.IconSize.TINY }]; 

// 拼装静态图参数 

let staticMapOptions: staticMap.StaticMapOptions = { 

location: { 

latitude: lat, longitude: lon }, zoom: LocationHelper.mapImageZoom, 

imageWidth: LocationHelper.mapImageWidth, 

imageHeight: LocationHelper.mapImageHeight, 

scale: LocationHelper.mapImageScale, markers: markers }; 

// 获取静态图 

staticMap.getMapImage(staticMapOptions).then((value: PixelMap) => { resolve(value); 

- 94 - 

resolve(value); 

}); 

}); 

} 

/** 

- 在地图上添加标记 

- @param lat 

- @param lon 

- @param mapController 

*/ 

public static async addMarker(lat: number, lon: number, mapController: map.MapComponentController) { if (mapController) { 

- //清除所有的圆、标记、折线等覆盖物 

- mapController.clear(); 

let markerOptions: mapCommon.MarkerOptions = { 

longitude: lon 

0, 

true, 0, 1, 0.5, 

1, true, true, false, 

$r('app.media.rc_portrait_person_default') 

}; 

//给地图中心点添加标记 

await mapController.addMarker(markerOptions); 

- } 

} 

/** 

* 增加点注释 

*/ 

public static addPointAnnotation(lat: number, lon: number, name: string, mapController: 

map.MapComponentController) { 

let pointAnnotationOptions: mapCommon.PointAnnotationParams = { 

// 定义点注释图标锚点 

latitude: lat 

- 95 - 

latitude: lat, longitude: lon 

}, 

// 定义点注释名称与地图poi名称相同时,是否支持去重 

repeatable: true, 

- // 定义点注释的碰撞规则 

collisionRule: mapCommon.CollisionRule.NAME, 

- // 定义点注释的标题,数组长度最小为1,最大为3 

titles: [{ 

// 定义标题内容 

content: name, 

- // 定义标题字体颜色 

color: getContext().resourceManager.getColorSync($r("app.color.rc_color_0E1012")), 

// 定义标题字体大小 

fontSize: 16, 

// 定义标题描边颜色 

- // strokeColor: 0xFFFFFFFF, 

// 定义标题描边宽度 strokeWidth: 2, 

// 定义标题字体样式 

fontStyle: mapCommon.FontStyle.ITALIC 

} 

], 

// 定义点注释的图标,图标存放在resources/rawfile 

icon: "", 

- // 定义点注释是否展示图标 

showIcon: true, 

// 定义点注释的锚点在水平方向上的位置 anchorU: 0.5, 

// 定义点注释的锚点在垂直方向上的位置 

anchorV: 1, 

// 定义点注释的显示属性,为true时,在被碰撞后仍能显示 forceVisible: true, 

- // 定义碰撞优先级,数值越大,优先级越低 

- priority: 3, 

// 定义点注释展示的最小层级 

minZoom: 2, 

// 定义点注释展示的最大层级 maxZoom: 22, 

// 定义点注释是否可见 

visible: true, 

- // 定义点注释叠加层级属性 

- zIndex: 10 

}; 

mapController.addPointAnnotation(pointAnnotationOptions); 

} 

- 96 - 

} } 

export class ImageUtil { 

/** 

* 图像数据转为 Base64 

*/ 

public static pixelMapToBase64(pixelMap: PixelMap): Promise<string> { 

return new Promise((resolve) => { 

const imagePackerApi: image.ImagePacker = image.createImagePacker(); 

```arkts
let packOpts: image.PackingOption = { format: 'image/jpeg', quality: 100 }; imagePackerApi.packing(pixelMap, packOpts).then((data: ArrayBuffer) => { let buf: buffer.Buffer = buffer.from(data); let base64 = buf.toString('base64', 0, buf.length); resolve(base64); 
```

}); 

}); } } 

##### **示例代码中引用到的类** 

###### 权限管理类 

###### **TypeScript** 

```arkts
import { abilityAccessCtrl, common, Permissions } from '@kit.AbilityKit'; import { bundleManager } from '@kit.AbilityKit'; import { ArrayChecker, ObjectChecker } from '@rongcloud/imlib'; 
```

export class PermissionsUtil { /** 

- 检查某个权限是否已授权 

- @param permission 需要检查的权限 

- @returns 授权状态 

*/ 

public static async checkPermission(permission: Permissions): Promise<abilityAccessCtrl.GrantStatus> { let atManager: abilityAccessCtrl.AtManager = abilityAccessCtrl.createAtManager(); 

let grantStatus: abilityAccessCtrl.GrantStatus = abilityAccessCtrl.GrantStatus.PERMISSION_DENIED; 

// 获取应用程序的accessTokenID 

let tokenId: number = await PermissionsUtil.getAccessTokenId(); 

// 校验应用是否被授予权限 

try { 

grantStatus = atManager.checkAccessTokenSync(tokenId, permission); 

- 97 - 

g 

g 

y ( 

p 

) 

} catch (error) { 

// 异常 

} 

return grantStatus; 

} 

/** 

- 检查一个 Array 里未授权的权限 

- @param checkPermissionArray 需要检查的权限 Array 

- @returns 返回未授权的 Array 

- */ 

public static async checkPermissions(checkPermissionArray: Array<Permissions>): Promise<Array<Permissions>> { 

const deniedPermissions: Array<Permissions> = new Array(); 

- if (ArrayChecker.isValid(checkPermissionArray)) { 

for (let checkPermissionArrayElement of checkPermissionArray) { 

- if (!ObjectChecker.isValid(checkPermissionArrayElement)) { 

- continue; 

   - let grantStatus: abilityAccessCtrl.GrantStatus = 

   - await PermissionsUtil.checkPermission(checkPermissionArrayElement); 

   - if (grantStatus === abilityAccessCtrl.GrantStatus.PERMISSION_DENIED) { 

   - //未授权 

   - deniedPermissions.push(checkPermissionArrayElement); 

- } 

- } 

return deniedPermissions; 

- } 

- /** 

- 动态请求权限 

- @param context UIAbilityContext 

- @param permissions 需要申请的权限 

- @returns 被拒绝的权限 

- */ 

- public static async requestPermissionsFromUser(context: common.UIAbilityContext, 

permissions: Array<Permissions>): Promise<Array<Permissions>> { 

- //被拒绝授权的数组 

const deniedPermissions: Array<Permissions> = new Array(); 

let atManager: abilityAccessCtrl.AtManager = abilityAccessCtrl.createAtManager(); 

// requestPermissionsFromUser会判断权限的授权状态来决定是否唤起弹窗 let data = await atManager.requestPermissionsFromUser(context, permissions) 

- 98 - 

let resultPermissions: Array<string> = data.permissions; 

let grantStatus: Array<number> = data.authResults; 

let length: number = grantStatus.length; 

for (let i = 0; i < length; i++) { 

if (grantStatus[i] === abilityAccessCtrl.GrantStatus.PERMISSION_DENIED) { 

   - // 用户拒绝授权,提示用户必须授权才能访问当前页面的功能,并引导用户到系统设置中打开相应的权限 

   - deniedPermissions.push(resultPermissions[i] as Permissions); 

- } 

- } 

###### return deniedPermissions; 

} 

/** 

- 二次向用户申请授权,直接拉起权限设置弹框,引导用户授予权限 

- @param context 

- @param permissions 

*/ 

public static requestPermissionOnSetting(context: common.UIAbilityContext, permissions: Array<Permissions>) { 

let atManager: abilityAccessCtrl.AtManager = abilityAccessCtrl.createAtManager(); 

atManager.requestPermissionOnSetting(context, permissions); 

- } 

- /** 

- 获取当前应用的 AccessTokenId 

- @returns AccessTokenId 

- */ 

public static async getAccessTokenId(): Promise<number> { 

- // 获取应用程序的accessTokenID 

let tokenId: number = 0; 

try { 

let bundleInfo: bundleManager.BundleInfo = 

await 

bundleManager.getBundleInfoForSelf(bundleManager.BundleFlag.GET_BUNDLE_INFO_WITH_APPLICATION); let appInfo: bundleManager.ApplicationInfo = bundleInfo.appInfo; 

   - tokenId = appInfo.accessTokenId; 

- } catch (error) { 

- // 异常 

- } 

return tokenId; 

} 

} 

~~- 99 -~~ 

LocationParams 、 SelectLocationType 

###### **TypeScript** 

import { ConversationIdentifier } from '@rongcloud/imlib'; import { LocationData } from './LocationData'; 

export interface LocationParams { locationData?: LocationData; conId?: ConversationIdentifier; flag: number; } export enum SelectLocationType { Send = 1, Look = 2, } 

LocationData 

###### **TypeScript** 

export class LocationData { latitude: number = 0.0; longitude: number = 0.0; name: string = ''; address?: string = ''; // 地图的静态图像PixelMap转的base64字符串 img?: string = ''; } 

##### **处理位置消息点击事件** 

位置消息与位置消息的 UI 定义在了Kit SDK中,所以需要 App 通过设置消息点击事件的方式来处理。 设置消息点击事件,建 议在 SDK init之后设置。 

###### **TypeScript** 

- 100 - 

let msgClickListener: MessageClickListener = {
onMessageClick(message) {
if (message.objectName === LocationMessageObjectName) {
// 地图消息跳转地图页面查看位置
let messageContent: LocationMessage = message.content as LocationMessage;
let locationData: LocationData = new LocationData();
      locationData.latitude = messageContent.latitude;
      locationData.longitude = messageContent.longitude;
      locationData.name = messageContent.poi;
let param: LocationParams = { locationData: locationData, flag: SelectLocationType.Look }
// 跳转到查看位置页面
return true;
    }
return false;
  }
};
RongIM.getInstance().conversationService().addMessageClickListener(msgClickListener);

##### **定制化** 

##### **自定义位置消息的 UI** 

位置消息使用 LocationMessageItemProvider 模板展示在消息列表中。 

如果需要调整内置消息样式,需继承 BaseMessageItemProvider<LocationMessage> 自行实现消息展示模板类,详见自 定义Provider。 

调用 addMessageItemProvider 的接口将该自定义模板提供给 SDK,objectName 传 LocationMessageObjectName。 

###### **TypeScript** 

import { LocationMessageObjectName, RongIM } from "@rongcloud/imkit"; 

// 注册自定义位置消息 provider 给 IMKit 

RongIM.getInstance().conversationService().addMessageItemProvider(LocationMessageObjectName, new CustomLocationMessageItemProvider()) 

###### **Emoji 与贴纸表情** 

用户可以 IMKit 输入区域发送 Emoji 表情、贴纸表情。点击输入栏的表情(☺)按钮,即可展开表情面板,支持发送 Emoji 表情、贴纸表情。表情消息将出现在会话页面的消息列表组件中。 

- 101 - 

提示 

IMKit 输入区域的表情面板中默认仅包含 emoji。支持添加自定义表情。 

- 102 - 

##### **Emoji 符号表情** 

IMKit 输入区域的表情面板中默认展示内置 Emoji 符号表情。用户点击后可发送 Emoji 符号表情。 

##### **禁用表情面板中的内置 Emoji 表情** 

从 1.5.1 版本开始支持。实现 IExtensionConfig,创建自定义的扩展面板配置类,重写 getEmoticonTabs() 方 法。getEmoticonTabs 不返回 SDK 内置表情组件 EmojiTab 即可。参照动态配置表情面板 

- 103 - 

##### **自定义表情组件** 

从 1.5.1 版本开始,IMKit 支持自定义表情组件。 

##### **添加自定义表情组件** 

以下步骤介绍了如何将自定义贴纸表情加入表情面板。 

1. 创建 MyEmoticonTab 实现 IEmoticonTab 。 

###### **TypeScript** 

export class MyEmoticonTab extends IEmoticonTab { obtainTabName(): string { 

return "MyEmoticonTab" } 

obtainTabDrawable(context: Context): ResourceStr { 

return $r("app.media.rc_custom_emoji_icon") } 

obtainTabPager(context: Context): WrappedBuilder<[Context, ConversationIdentifier, IEmoticonTab]> { return wrapBuilder(buildCustomEmoticonSwiperPageView) 

} 

onTableSelected(context: Context, index: number): void { 

" console.log("index: + index) } } 

2. 在上方的 obtainTabPager 方法中添加想要展示在表情面板上的 View。下方提供了一个比较完整的参考示例: 

###### **TypeScript** 

@Builder 

export function buildCustomEmoticonSwiperPageView(context: Context, convId: ConversationIdentifier, tab: IEmoticonTab) { 

CustomEmoticonSwiperPage({ convId: convId, tab: tab }) 

} 

class CustomDataSource implements IDataSource { private list: EmojiData[][] = [] 

constructor(list: EmojiData[][]) { 

this.list = list 

} 

- 104 - 

totalCount(): number { return this.list.length 

} 

getData(index: number): EmojiData[] { return this.list[index] 

} 

registerDataChangeListener(listener: DataChangeListener): void { 

} 

unregisterDataChangeListener() { } } 

class EmojiData { 

// emoji图标的资源地址,可以是本地路径, public emojiUrl: string = ""; // emoji名字 public name: string = ""; 

constructor(emojiUrl: string, name: string) { this.emojiUrl = emojiUrl; this.name = name; } } 

@Component export struct CustomEmoticonSwiperPage { 

@Require @Prop tab: IEmoticonTab; 

@Require @Prop convId: ConversationIdentifier; private customDataSource: CustomDataSource = new CustomDataSource([]) 

aboutToAppear(): void { 

// 这里是示例,实际数据源需要业务侧处理 let emojiData: EmojiData[] = [ new EmojiData("1.png", "圣诞树"), new EmojiData("2.png", "玫瑰"), new EmojiData("3.png", "西瓜"), new EmojiData("4.png", "烤肉"), new EmojiData("5.png", "冰淇淋"), new EmojiData("6.png", "红酒"), new EmojiData("7.png", "礼物"), new EmojiData("8.png", "蛋糕"), 

- 105 - 

```arkts
new EmojiData("9.png", "圣诞树"), new EmojiData("10.png", "庆祝"), new EmojiData("11.png", "博士"), new EmojiData("12.png", "骏马"), new EmojiData("13.png", "小狗"), new EmojiData("14.png", "猪头"), new EmojiData("15.png", "皇冠"), new EmojiData("16.png", "火苗")] let dataList: EmojiData[][] = [] for (let i = 0; i <= 8; i += 8) { 
```

const emojisSubset = emojiData.slice(i, i + 8); 

dataList.push(emojisSubset) } 

this.customDataSource = new CustomDataSource(dataList) } 

###### build() { 

Swiper() { 

LazyForEach(this.customDataSource, (item: EmojiData[]) => { this.emojiPageView(item) 

}, (item: string[]) => item.toString()) 

} .loop(false) .indicator( 

new DotIndicator().itemWidth(8) 

itemHeight(8) 

selectedItemWidth(9) 

selectedItemHeight(9) 

color(Color.Gray) 

.selectedColor(Color.Black) ) 

.onChange((index: number) => { 

console.info(index.toString()) 

}) 

.width('100%') 

.layoutWeight(1) 

.nestedScroll(SwiperNestedScrollMode.SELF_FIRST) 

} 

@Builder 

emojiPageView(pageData: EmojiData[]) { 

Column() { Grid() { 

ForEach(pageData, (item: EmojiData) => { GridItem() { 

- 106 - 

Column() { Image(item.emojiUrl).width(40).height(40) Text(item.name).fontSize(12) } }.onClick(() => { // 可以监听点击事件,做发送消息的操作 }) }) }.columnsTemplate('1fr 1fr 1fr 1fr').rowsTemplate('1fr 1fr').width('100%').height('100%') }.width('100%').height('100%').padding({ bottom: 20 }) } 

} 

###### 3. 添加自定义表情组件 

###### **TypeScript** 

RongExtensionManager.getInstance().addEmoticonTab(new MyEmoticonTab()) 

除了添加自定义表情,还支持移除自定义表情组件、清除所有自定义表情组件、获取所有添加的自定义表情组件列表: 

###### **TypeScript** 

// 移除自定义表情组件 

RongExtensionManager.getInstance().removeEmoticonTabByName("MyEmoticonTab") 

// 清除所有自定义表情组件 

RongExtensionManager.getInstance().clearAllEmoticonTab() 

// 获取所有添加的自定义表情组件列表 let tabList:List<IEmoticonTab> = RongExtensionManager.getInstance().getEmoticonTabList() 

##### **动态配置表情面板** 

如果应用程序需要动态添加、删除表情面板表情,或者调整自定义表情位置,建议通过创建自定义的表情面板配置实现这些自 定义需求。 

实现 IExtensionConfig,创建自定义的扩展面板配置类,重写 getEmoticonTabs() 方法。您可以增加或删除扩展项,也可 以调整各个表情组件的位置。 

###### **TypeScript** 

- 107 - 

import { EmojiTab, EmojiIEmoticonTabTabName } from '@rongcloud/imkit'; 

```arkts
let mCustomExtensionConfig: IExtensionConfig = { getEmoticonTabs: (convId: ConversationIdentifier) => { let tabs: ArrayList<IEmoticonTab> = new ArrayList<IEmoticonTab>(); // EmojiTab 是 SDK 内置的 emoji Tab tabs.add(new EmojiTab()) // getEmoticonTabList获取当前设置的 Tab 列表 let tabList = RongIM.getInstance().conversationService().getEmoticonTabList() // 可以调整顺序、添加或者移除。 for (let tab of tabList) { tabs.add(tab) } return tabs } } 
```

SDK 初始化之后,调用以下方法设置自定义的输入配置,SDK 会根据此配置展示扩展面板。 

###### **TypeScript** 

RongIM.getInstance().conversationService().setExtensionConfig(mCustomExtensionConfig) 

###### 获取当前插件配置 

###### **TypeScript** 

let config = RongExtensionManager.getInstance().getExtensionConfig() // 根据 ConversationIdentifier 获取对应的插件列表 let convId: ConversationIdentifier let pluginModules = config.getEmoticonTabs(convId) 

##### **隐藏表情面板入口** 

IMKit SDK 暂时还不支持此功能。 

##### **自定义表情面板添加按钮** 

从 1.5.1 版本开始,IMKit 默认允许配置会话页面输入框的一些UI组件。可通过 

setInputAreaComponentConfig(InputAreaComponentConfig) 接口设置自定义组件配置。 默认该组件不展示。 

- 108 - 

###### **TypeScript** 

- 109 - 

export interface InputAreaComponentConfig { 

/** 

* 组件标识 */ identifier: ComponentIdentifier, /** * 组件WrappedBuilder */ component?: WrappedBuilder<[InputAreaComponentData]> | null, } 

/** * 输入区域自定义组件数据,封装必要的参数透传给自定义组件 * @since 1.6.0 */ export class InputAreaComponentData { /** * 上下文 */ context: Context | undefined; /** * 会话标识 */ convId: ConversationIdentifier | undefined; /** * 透传参数 * *``` 

- 当 `identifier` 为某些枚举类型的情况下有值,其余情况下为空。详细说明如下 *  1. ComponentIdentifier.InputBarVoiceButton: "Voice" 语音类型、 "Text" 文本类型。 

- 2. ComponentIdentifier.InputBarEmoticonButton: "Emoticon" 表情类型、 "Text" 文本类型。 

*  3. ComponentIdentifier.DestructBarVoiceButton: "Voice" 语音类型、 "Text" 文本类型。 *``` */ data: string = ""; } 

###### identifier 支持的组件类型说明: 

组件类型 说明 EmoticonBoardAddButton 表情面板左下角的添加按钮 component 说明: WrappedBuilder 第三个参数返回空。 

- 110 - 

###### **TypeScript** 

###### // 设置接口 

let EmoticonBoardAddButton: InputAreaComponentConfig = { 

identifier: ComponentIdentifier.EmoticonBoardAddButton, 

component: wrapBuilder(buildCustomEmoticonBoardAddButtonView), 

} 

RongIM.getInstance().conversationService().setInputAreaComponentConfig(EmoticonBoardAddButton) 

###### // 组件 

###### @Builder 

export function buildCustomEmoticonBoardAddButtonView(componentData: InputAreaComponentData) { CustomEmoticonBoardAddButtonView({ context: componentData.context, convId: componentData.convId }) 

} 

@Component 

export struct CustomEmoticonBoardAddButtonView { 

@Prop context: Context; 

@Prop convId: ConversationIdentifier; 

build() { Row() { 

Button({ type: ButtonType.Normal }) { 

Image($r('app.media.seal_ic_main_more')).size({ width: 20, height: 20 }) } 

.width('60').height('36') 

.backgroundColor($r('app.color.rc_color_00000000')).onClick(() => { 

// 点击事件 

}) } } } 

###### **@ 消息** 

提及(@)是群聊会话中常见功能,允许用户可以会话中提及指定用户,或全部群成员,以增强消息的提示作用。使用 @ 功 能后,消息内容中会额外携带 MentionedInfo 对象。IMKit 默认启用了 @ 功能。 

###### 提示 

选择联系人页面的数据需要由应用程序提供,否则展示空列表。在使用 @ 功能前,请先实现群组成员提供者。 

- 111 - 

##### **局限** 

仅支持群聊会话。 

- IMKit 默认仅实现了在发送文本消息、引用消息时使用 @ 功能。 

- @ 消息可以被转发,但转发的只是纯文本,不再具备 @ 功能。 

##### **用法** 

- 112 - 

提示 

在使用 @ 功能前,请先实现群组成员提供者。 

IMKit 默认在配置中启用了 @ 功能,用法如下: 

- 在会话页面长按用户头像可触发消息编辑,提及(@)该用户。 

- 在会话页面输入 @ 符号之后,IMKit 会跳转到成员列表选择页面。如果应用程序未实现群组成员提供者 

- ( UserDataProvider ),该页面会显示一个空列表。实现群组成员提供者( UserDataProvider )后,IMKit 会通过 UserDataProvider 对象的 fetchGroupMemberInfos 方法取得群成员数据,并展示在该列表页面中。 

##### **定制化** 

###### 提示 

- 基于会话界面-Page实现的会话页面,不支持自定义。 

- 基于会话组件-Component实现的会话页面,可以进行自定义。 

##### **自定义选择成员界面** 

下面展示了基于会话组件-Component自定义的代码 

1. 调用 RongIM 的 addConversationEventListener 添加会话事件监听 ConversationEventListener ,重写 onInputMention 方法,当群聊输入 @ 时会收到 onInputMention 回调。 

2. 在 onInputMention 回调中,判断群聊会话类型后跳转到 App 定义的用户列表选择用户页面。 

3. 选择完用户后,构造 UserInfoModel 调用 select 返回。 

###### **TypeScript** 

- 113 - 

###### @Entry 

###### @Component 

struct ChatPage { 

- // 添加会话事件监听,重写 `onInputMention` 方法。 

private conversationEventListener: ConversationEventListener = { 

onInputMention: (select: (user: UserInfoModel) => void) => { 

- // 判断群聊会话类型后跳转到 App 定义的用户列表选择用户页面 

if (this.conId.conversationType === ConversationType.Group) { 

- // 选择完用户后,构造 UserInfoModel 调用 select 返回。 

const userInfo = new UserInfoModel("userId", "displayName", '') 

select(userInfo); 

- } 

- } 

- } 

aboutToAppear(): void { 

- // 添加监听 

RongIM.getInstance().conversationService().addConversationEventListener(this.conversationEventListener) 

- } 

aboutToDisappear(): void { 

- // 移除监听 

RongIM.getInstance().conversationService().removeConversationEventListener(this.conversationEventListener } 

} 

##### **关闭 @ 功能** 

基于会话组件-Component实现的会话页面,不添加会话事件监听即可。 

###### **输入状态** 

输入状态可让用户直观地了解其他用户是否正在键入消息。在对方用户键入内容时,标题栏会一直显示「对方正在输入」,直 到用户发送消息或完全删除文本。 

如果用户停止打字超过 6 秒,该提示也会消失。SDK 在输入框中有内容变化时,默认向对端用户发送一条正在输入的状态消 息,包含消息内容对象 TypingStatusMessage(类型标识:RC:TypSts)。 

提示 

基于会话界面-Page( ConversationPage )包含了标题栏显示正在输入状态的实现。 

- 114 - 

基于会话组件-Component( ConversationComponent )构建的会话页面,请自行实现标题栏输入状态的展 示与更新。 

##### **局限** 

###### 只支持单聊会话。 

- 因无法确定用户的输入操作,该功能可能会产生大量状态消息,为防止消息发送频繁,默认在 6 秒钟内的多次状态变 化,只产生一条输入状态消息。 

- 该功能可能会导致大量状态消息,如不需要此功能建议关闭。 

##### **用法** 

如果使用 IMKit 会话界面-Page(ConversationPage)集成,该功能默认可用,无需额外处理。 

##### **在自定义会话页面监听输入状态** 

IMKit 的会话组件-Component不含标题栏实现。如果使用这个方式构建自定义会话页面,您需要自行实现输入状态的展示与 更新。 

- 115 - 

IMKit SDK 内部已经处理好逻辑,在输入框中有内容变化时,SDK 会向目标用户发送一条正在输入的状态消息。应用程序仅 需要在自定义会话页面注册监听器,在收到回调通知时更新标题栏,实现类似 **对方正在输入** 的提示。 

在自定义会话页面中注册输入状态的监听器。 建议添加监听后,在合适的时机移除,避免内存泄露。如果在页面中监听,建议 在aboutToAppear调用,在 aboutToDisappear 移除监听。 

###### **示例代码** 

###### **TypeScript** 

private typingStatusListener: TypingStatusListener = { 

- onTypingStatusChange: (conId: ConversationIdentifier, typingStatusList: List<TypingStatus>) => { //当输入状态的会话类型和targetID与当前会话一致时,才需要显示 if (!conId || !StringChecker.equals(conId.targetId, this.conId.targetId) || 

- conId.conversationType !== this.conId.conversationType) { //不是当前会话 return; 

- } // 输入状态列表为空,当前会话没有用户正在输入,标题栏仍显示原来标题 if (!typingStatusList || typingStatusList.length <= 0) { // 展示原标题 return 

- } // 有值代表对方在输入内容匹配对方正在输入的是文本消息还是语音消息 let typingStatus = typingStatusList[0] as TypingStatus if (typingStatus.objectName === TextMessageObjectName) { // 设置标题:对方正在输入... 

- } else if (typingStatus.objectName === HQVoiceMessageObjectName || typingStatus.objectName === VoiceMessageObjectName) { // 设置标题:对方正在说话... 

- } } } // 添加监听 RongIM.getInstance().messageService().addTypingStatusListener(this.typingStatusListener) // 移除监听 

RongIM.getInstance().messageService().removeTypingStatusListener(this.typingStatusListener) 

###### 提示 

当对方正在输入时,本端会触发 onTypingStatusChange,回调里携带有正在输入的用户列表。当对方停止输入时, 该监听还会触发一次,此时回调里的输入用户列表为空。这时您需要取消 **正在输入** 的显示,并显示原有的会话标题栏。 

##### **定制化** 

- 116 - 

##### **设置发送输入状态消息的默认时间间隔** 

SDK 默认间隔配置为 6000 毫秒,您可以通过 IMLib SDK接口进行配置设置输入状态更新时间间隔。 

##### **关闭输入状态功能** 

IMKit 默认开启输入状态功能。目前暂不支持关闭。 

###### **已读回执** 

IMKit 提供了单聊、群聊的已读回执功能。App 用户通过已读回执获知对方是否阅读该消息。 

在 IMKit 内置页面中已默认实现并启用已读回执功能。在单聊会话中,消息默认更新已读状态。在群聊会话中,消息发送者需 要在页面上主动请求获取已读状态。 

##### **阅读回执开关** 

IMKit 中回执功能默认开启,在单聊和群聊中默认会展示消息回执。目前不支持关闭。 

##### **单聊阅读回执** 

在单聊会话中,发送方会实时收到消息的已读状态更新。在 IMKit 内置页面中,单聊已读状态显示在两处: 

- **单聊会话页面(消息列表页面)** :在发送方的单聊会话页面,消息的左下角会显示对号,表示对方已读。 

- **会话列表页面** :会话列表的每条会话会显示会话中的最后一条消息的预览。如果单聊会话最后一条消息被对方阅读,发送 方的会话列表页中对应会话条目的右下角也会显示对号,表示对方已读。 

- 117 - 

##### **群聊阅读回执** 

提示 

IMKit 的群聊已读回执功能仅支持文本消息类型。 

在群聊会话中发送消息后 180 秒之内,发送者可以在会话页面上主动请求获取已读人数数据。在会话页面上,消息的左下角 会显示对号按钮(请求阅读回执的按钮)。点击按钮后,IMKit 才会请求已读回执。IMKit 在收到已读回执结果后会刷新页 面,显示为 “n 人已读”。 

- 118 - 

###### **消息未读数** 

未读消息计数是 IMKit 默认提供的一项功能,可告知用户每个会话中未读消息的数量。 

未读消息计数显示在会话列表 会话组件-Component(ConversationComponent) 的会话条目上。每个会话的未读消息数 显示在会话图标右上角。如果未读消息数超过 100 条,则会显示为 99+ 。 

提示 

为了使用未读消息计数功能,您必须首先构建会话列表页面。IMKit 默认未实现底部导航栏。 

- 119 - 

##### **用法** 

IMKit SDK 默认已经实现了一整套会话未读消息数获取和展示逻辑,使用默认会话列表和会话页面时,不需要额外调用会话相 关 API。 

IMKit 会在用户进入单聊、群聊、系统会话页面时将会话未读数清零。在用户多端登录时,IMKit 会在设备间同步会话的阅读 状态,您也可以按业务需求选择关闭该功能,详见下文多端同步阅读状态。 

##### **定制化** 

如果 IMKit 已有实现无法满足您的需求,可以使用 IMKit 或 IMLib SDK 中相关 API。 

##### **获取会话未读数** 

- 120 - 

**获取单个会话的未读数** 

###### **示例代码** 

###### **TypeScript** 

```arkts
let conId = new ConversationIdentifier(); conId.conversationType = ConversationType.Private; conId.targetId = "TestTargetId"; // 按需填写实际的会话 id 
RongIM.getInstance().conversationService().getUnreadCount(conId).then(result => { if (EngineError.Success !== result.code) { // 获取未读数失败 return; } if (!result.data) { // 未读数为 null return; } let unreadCount = result.data as number; }); 
```

###### **参数说明** 

|参数名|类型|详细说明|
|---|---|---|
|conId|ConversationIdentifer|会话标识,包含会话类型与会话的targetId|

###### **按会话类型列表获取未读数,可以选择是否包含免打扰** 

###### **示例代码** 

###### **TypeScript** 

- 121 - 

let typeList = new List<ConversationType>(); 

typeList.add(ConversationType.Private); typeList.add(ConversationType.Group); 

let isContainBlocked = false; 

RongIM.getInstance().conversationService().getUnreadCountByTypes(conTypeList, isContainBlocked).then(result => { 

if (EngineError.Success !== result.code) { 

// 获取未读数失败 return; } if (!result.data) { 

// 未读数为 null return; } let unreadCount = result.data as number; 

}); 

###### **参数说明** 

|参数名|类型|详细说明|
|---|---|---|
|typeList|List|需要查询的会话类型列表|
|isContainBlocked|boolean|是否包含被屏蔽会话的未读数|

IMKit 未直接提供获取多个或者所有会话未读数的 API。如果您有类似自定义需求,可以调用 IMLib SDK 相关方法:获取所有 会话未读数与获取多个会话的未读消息数 

具体的核心类、API 与 使用方法,详见 IMLib 文档 处理会话未读消息数。 

提示 

IMLib 方法并不提供页面刷新能力,您需要根据业务需求自定义通知机制进行页面刷新。 

##### **清除会话未读数** 

IMKit 支持清除指定会话的未读数,清除完毕后会自动刷新会话列表页面的未读展示。 支持的会话类型: 

- 单聊( ConversationType.PRIVATE ) 

- 群聊( ConversationType.GROUP) 

- 系统( ConversationType.SYSTEM ) 

###### **清除指定会话的未读数** 

您可以使用 IMEngine 的 clearMessagesUnreadStatus() 方法清除指定会话的全部未读数,该方法接受一个会话标识 

- 122 - 

ConversationIdentifier 对象。 

###### **TypeScript** 

```arkts
let conId = new ConversationIdentifier(); conId.conversationType = ConversationType.Private; conId.targetId = "TestTargetId"; // 按需填写实际的会话 id 
```

IMEngine.getInstance().clearMessagesUnreadStatus(conId).then(result => { 

if (EngineError.Success !== result.code) { // 清空未读数失败 return; } / 清空未读数成功 }) 

###### **清除指定会话指定时间戳前的未读数** 

您可以使用 IMEngine 的 clearMessagesUnreadStatus() 方法清除指定会话的全部未读数,该方法接受一个会话标识 ConversationIdentifier 对象与时间戳。 

###### **TypeScript** 

```arkts
let conId = new ConversationIdentifier(); conId.conversationType = ConversationType.Private; conId.targetId = "TestTargetId"; // 按需填写实际的会话 id 
```

let time = Date.now(); 

IMEngine.getInstance().clearMessagesUnreadStatusByTime(conId, time).then(result => { if (EngineError.Success !== result.code) { 

// 清空未读数失败 return; } // 清空未读数成功 }) 

##### **监听会话未读数变化** 

IMKit 目前暂不支持监听未读数变化。 

##### **多端同步阅读状态** 

在即时通讯业务中,同一用户账号可能在多个设备上登录。仅在开通多设备消息同步服务后,融云会在多个设备之间同步消息 数据,但设备上的会话中消息的已读/未读状态仅存储在本地。 

- 123 - 

IMKit SDK 已默认实现了会话多端阅读状态同步功能,在一端发起同步后,其他端可接收通知,按要求同步阅读状态。该功能 默认开启,目前暂不支持关闭。 

##### **主动同步消息未读状态** 

IMKit SDK 默认在进入会话页面后会清理会话消息的未读状态。如需在未进入会话页面时同步未读状态,需要 App 主动同步 消息未读状态。其他端调用该方法将某个会话同步已读之后, 鸿蒙会触发 SyncConversationReadStatusListener 回调。 

IMEngine 提供 syncConversationReadStatus 方法,可在多端登录时,通知其它终端同步某个会话的消息未读状态。该方 法同时按时间戳清除本端会话中传入时间之前的所有消息的未读状态。会话列表页面的会话未读数也会同步刷新。 

###### **TypeScript** 

```arkts
let conId = new ConversationIdentifier(); conId.conversationType = ConversationType.Private; conId.targetId = "会话 Id"; 
```

// 会话中已读的最后一条消息的发送时间戳,此处用了当前时间 let time = Date.now(); IMEngine.getInstance().syncConversationReadStatus(conId,time).then(result => { if (EngineError.Success !== result.code) { // 同步已读失败 return; } // 同步已读成功 }); 

##### **监听消息未读状态同步数据** 

###### 提示 

IMKit 内置的会话列表页面已通过该监听实现了未读状态的同步逻辑,当其它端的消息变为已读时,本端通过监听会清 除对应会话的消息未读数,您不需要额外处理。 

IMEngine 中提供了 SyncConversationReadStatusListener 监听器。客户端设置该监听器后,才能接收来自其他同步的阅 读状态数据。在接收到阅读状态同步数据后,会触发监听器的 onSyncConversationReadStatus 方法。SDK 会将指定会话 中早于等于 syncConversationReadStatus 传入时间戳的消息均置为已读: 

###### **示例代码** 

###### **TypeScript** 

- 124 - 

let listener : SyncConversationReadStatusListener = { 

onSyncConversationReadStatus: (conId: ConversationIdentifier, timestamp: number): void => { 

// 该会话的 timestamp 之前的消息未读已清空 } } IMEngine.getInstance().addSyncConversationReadStatusListener(listener); 

###### **参数说明** 

|参数|类型|说明|
|---|---|---|
|conId|ConversationIdentifer|会话标识|
|timestamp|number|已读的毫秒时间戳,该时间戳前的消息已读|

##### **未读消息气泡提醒** 

IMKit 支持在会话页面中显示未读消息气泡提醒。 

- 125 - 

##### **是否显示未读消息数提醒** 

如果会话的未读消息数已超过 0,可在进入会话页面后在右上角显示提醒气泡。用户点击提醒气泡后,页面会跳转到最开始的 未读消息。 

默认未读消息气泡在未读消息大于 **10 条** 时展示。目前暂不支持关闭,暂不支持自定义样式。 

##### **是否显示新消息提醒** 

如果用户在查看会话页面中的历史消息,且当前视图未显示会话最新消息,此时如果收到新消息,会话页面右下角可显示新消 息气泡提醒,例如 **15 条新消息** 。用户点击提醒按钮,会滚动到会话最新消息处。 

新消息提醒组件默认默认显示,在新消息数量大于 **1 条** 即可展示,超过 **99 条** 显示为 **99+** 。目前暂不支持关闭,暂不支持 自定义样式。 

- 126 - 

###### **转发消息** 

IMKit 默认没有实现对单条、多条消息的转发以及合并转发,下面提供了可以实现单条或多条消息的转发的代码示例进行参 考。 

##### **局限** 

并非所有消息类型均支持合并转发。 

   - 支持的消息类型:文本、图片、图文、GIF、动态表情( RC:StkMsg )、名片、位置、小视频、文件、普通语音、 高清语音、音视频通话( RC:VCSummary )。 

   - 不支持的情况:未在支持列表中的消息类型,例如引用消息,以及未发送成功的消息等特殊情况不支持转发。自定 义消息均不支持合并转发。 

- 合并转发支持合并不能超过 100 条消息。 

##### **单条转发** 

可以增加消息气泡的长按事件来实现转发。在 onClick 中发消息使用 示例代码 的 sendForwardMessage 方法。 

###### **TypeScript** 

- 127 - 

let msgForwardLongClickAction :ItemLongClickAction<Message> = { obtainTitle: (context: Context, data: Message): string | Resource => { 

return "转发消息" 

}, 

onClick: (context: Context, data: Message): void => { 

// 转发消息 

}, 

onFilter: (data: Message): boolean => { 

// 是否显示该长按事件?true 显示;false 不显示 

- // 开发者可以根据 Message 对象的会话类型或者消息类型决定是否显示 return true; 

}, 

- // 自定义的消息长按事件 Id,相同的 Id 的长按事件只会增加一次 

actionId: 'CustomMessageActionId' } 

RongIM.getInstance().conversationService().addMessageItemLongClickAction(msgForwardLongClickAction); 

##### **合并转发 (1.4.3 支持 )** 

SDK 会将选中的消息合并为一条合并转发消息,包含消息内容对象 CombineMessage(类型标识:RC:CombineMsg)。 合并转发的消息默认折叠显示,可点击展开。 

##### **预览页面事件监听** 

您可以通过 addCombineMessageEventListener 方法自定义合并转发预览界面的事件监听: 

- 128 - 

**示例代码** 

###### **TypeScript** 

export interface CombineMessageEventListener { 

/** 

- 合并转发消息预览页面的位置消息点击事件回调 

- @param latitude 纬度, double 类型 

- @param longitude 经度, double 类型 

- @param locationName 地理位置的名称 

*/ 

onLocationMessageClick?: (latitude: number, longitude: number, locationName: string) => void; } 

let combineMessageEventListener: CombineMessageEventListener = { 

onLocationMessageClick: (latitude: number, longitude: number, locationName: string) => { 

// 地图消息跳转地图页面查看位置 

} 

} 

- // 添加事件监听 

- RongIM.getInstance().messageService().addCombineMessageEventListener(combineMessageEventListener) // 移除事件监听 

RongIM.getInstance().messageService().removeCombineMessageEventListener(combineMessageEventListene 

##### **预览页面样式设置** 

您可以通过 ConversationConfig 的 setCombineHtmlStyle 方法配置预览页面的样式: 

###### **TypeScript** 

let config = RongIM.getInstance().conversationService().getConversationConfig() config.setCombineHtmlStyle("样式style") 

RongIM.getInstance().conversationService().setConversationConfig(config) 

##### **合并转发兼容不支持的类型消息** 

##### **构建合并转发消息** 

构建合并转发接口新增 function 类型参数 unsupportedMessageHandler?: (message:Message) => Promise<string>。仅当SDK解析到不支持的类型消息时,会回调此 function,message 是不支持的消息。 这样由开发者 来处理合并转发不支持的类型消息,返回消息对应 HTML body 内容,SDK 会把返回的内容插入到合并转发 HTML 中。 

###### **TypeScript** 

- 129 - 

/** 

###### * 构建合并转发消息 

* 

- @param forwardMessages 用来构建合并转发消息的消息数组 

- @param unsupportedMessageHandler 用于开发者处理合并转发不支持类型的消息转换为 HTML 内容的逻辑。 

- @returns 返回 CombineMessage,如果返回 undefined 则代表构建失败。 

*/ 

obtainCombineMessage(forwardMessages: Message[], unsupportedMessageHandler?: (message:Message) => Promise<string>): Promise<IAsyncResult<CombineMessage>>; 

##### **参数说明** 

|参数名|类型|说明|
|---|---|---|
|forwardMessages|Message[]|用来构建合并转发消息的消息数组|
|unsupportedMessageHandler|(message:Message)|用于开发者处理合并转发不支持类型的消息转换为HTML内容|
||=>|的逻辑。|
||Promise<string>|1.仅当SDK转换forwardMessages遇到不支持的消息类型时|
|||回调此function,message是不支持的消息。如开发者准备渲|
|||染该消息,则需要返回body内容。|
|||2. SDK不会校验function返回的body内容,如内容异常会|
|||导致合并转发页面加载失败,需开发者保证内容有效。如返回空|
|||字符串则不会处理。|

##### **拦截 Html 页面的 JS 事件** 

###### 接口说明 

###### **TypeScript** 

export interface CombineMessageEventListener { 

// ...省略无关代码 

/** 

- 合并转发WebView的JS回调原生的拦截器。此拦截接口优先级高于 onLocationMessageClick。 

- 

- @params jsJson 合并转发Html通过JS透传过来的Json数据 

- @return false 代表SDK继续执行JS事件,true 代表SDK不需再执行JS事件。 

- @since 1.7.0 

*/ 

onJSCallNativeInterceptor?: (jsJson: string) => Promise<boolean>; 

} 

- 130 - 

SDK 返回的 jsJson 数据示例 

###### **TypeScript** 

###### 文件 

type = "RC:FileMsg" fileName = "文件.pdf" fileSize = "123456" fileType = "pdf" fileUrl = "文件地址" 地图 

type = "RC:LBSMsg" latitude = "纬度" locationName = "地理位置" longitude = "经度" 合并转发 type = "RC:CombineMsg" fileUrl = "文件下载地址" title = "标题" 手机号 type = "phone" phoneNum = "13888888888" 超链接 type = "link" link = "超链接" 图片 type = "RC:ImgMsg" fileUrl = "图片地址" imgUrl = "缩略图base64" 视频 type = "RC:SightMsg" duration = "5" fileUrl = "视频地址" imageBase64 = "缩略图base64" Gif type = "RC:GIFMsg" fileUrl = "Gif地址" 

##### **自定义 html 内容说明** 

定义 CUSTOM:MSG 类型消息对应的 html body 内容,支持使用自定义样式,支持点击事件。 

自定义样式可以通过 setCombineHtmlStyle 来设置。 

必须设置 onClick='show()' 来保证 SDK 可以接收 JS 点击事件,例: onClick='show({extra:"自定义透传参 数",title:"标题",type:"CUSTOM:MSG"})'。 

- 131 - 

- 设置合并转发事件接口,可以拦截JS点击事件,参照 

CombineMessageEventListener#onJSCallNativeInterceptor 。 

- 内置标签如: {%portrait%} 、 {%showUser%} 、 {%userName%} 、 {%sendTime%} ,与消息类型无关,由 SDK 进行处理。 

代码示例 

###### **html** 

|<!-- 1,点击事件:必须统一使用show()来进行鸿蒙原生JS回调,内容是Json格式--> <divclass='rong-message {%showUser%}' onClick='show({extra:"自定义透传参数",title:"标 题",type:"CUSTOM:MSG"})'> <divclass='rong-message-user rong-none-user-img'><imgsrc='{%portrait%}' class='rong-message-|
|---|
|user-bg rong-message-user-portrait' /> <divclass='rongcloud-message-body'>|
|<!-- 2,修改name修改为消息的objectName --> <divname='CUSTOM:MSG'> <divclass='rongcloud-message-user-name'>{%userName%}<spanclass='rong-message-time' name='sendTime'>{%sendTime%} <!-- 3,摆放html body标签--> <!--这里rongcloud-message-text是内置的样式--> <divclass='rongcloud-message-text'> <preclass='rongcloud-message-entry'>{%customMsgField1_SDKStyle%}</pre> <!--这里custom-msg-style1、custom-msg-style2是自定义的样式-->|
|<divclass='custom-msg-style1'> <preclass='rongcloud-message-entry'>{%customMsgField2_CustomStyle%}</pre> |
|<divclass='custom-msg-style2'> <preclass='rongcloud-message-entry'>{%customMsgField3_CustomStyle%}</pre> |
||

##### **完整示例** 

###### 1. **定义 CUSTOM:MSG 类型消息的 HTML 内容** 

###### **TypeScript** 

- 132 - 

let customMsgHtmlData:string = 

- "\n" + 

- "        <img src='{%portrait%}' class='rong- 

- message-user-bg rong-message-user-portrait' />\n" + 

- "        \n" + 

- "                <!-- 2,修改name修改为消息的objectName -->\n" + 

- "                \n" + 

- "                        {%userName%} 

- {%sendTime%}\n" + 

- "                        <!-- 3,摆放 html body 标签 -->\n" + 

- "                        <!-- 这里rongcloud-message-text 是内置的样式 -->\n" + 

- "                        \n" + 

- "                                <pre class='rongcloud-message-entry'>{%customMsgField1_SDKStyle%}</pre>\n" 

- + 

- "                        \n" + 

- "                        <!-- 这里 custom-msg-style1、custom-msg-style2 是自定义的样式 -->\n" + 

- "                        \n" + 

- "                                <pre class='rongcloud-message-entry'>{%customMsgField2_CustomStyle%} 

- </pre>\n" + 

- "                        \n" + 

- "                        \n" + 

- "                                <pre class='rongcloud-message-entry'>{%customMsgField3_CustomStyle%} 

- </pre>\n" + 

- "                        \n" + 

- "                \n" + 

- "        \n" + 

- ""; 

###### 2. **定义 HTML 内容中用到的样式** 

###### **TypeScript** 

- 133 - 

import { RongIM } from "@rongcloud/imkit" 

let config = RongIM.getInstance().conversationService().getConversationConfig() let style: string = ".custom-msg-style1 {\n" + 

- "      font-size: 14px;\n" + 

- "      color: #FF0000;\n" + 

- "      margin: 0;\n" + 

- "      padding: 0;\n" + 

- "    }\n" + 

- "    .custom-msg-style2 {\n" + 

- "      font-size: 16px;\n" + 

- "      color: #CC0066;\n" + 

- "      margin: 0;\n" + 

- "      padding: 0;\n" + 

- "    }" 

config.setCombineHtmlStyle(style) 

RongIM.getInstance().conversationService().setConversationConfig(config) 

###### 3. **设置合并转发事件接口,实现拦截 JS 事件方法** 

###### **TypeScript** 

import { CombineMessageEventListener, RongIM } from "@rongcloud/imkit"; 

let combineMessageEventListener: CombineMessageEventListener = { 

onJSCallNativeInterceptor: (jsData: string): Promise<boolean> => { return new Promise((resolve) => { 

let jsonObject: object = JSON.parse(jsData); 

- // 开发者根据 jsonObject 里的值来判断开发者是否需要处理,以及是否需要SDK处理。 

if (jsonObject["CUSTOM:MSG"]) { 

- // 开发者处理跳转逻辑,则返回true,由SDK处理跳转逻辑则返回false。 resolve(true); 

} else { resolve(false); } }); } } 

RongIM.getInstance().messageService().addCombineMessageEventListener(combineMessageEventListener) 

###### 4. **构建转发消息,设置转换 Html 的 function 来返回 Html 内容** 

###### **TypeScript** 

- 134 - 

import { Message, RongIM } from "@rongcloud/imkit" 

// 参照上述 customMsgHtmlData 示例 

let customMsgHtmlData: string = "" 

###### // 待转发消息 

let forwardMessage: Message[] = [] 

let result = await RongIM.getInstance().messageService().obtainCombineMessage(forwardMessage, (message: Message) => { 

return new Promise<string>((resolve) => { 

if (message.objectName === "CUSTOM:MSG") { 

// 示例replaceContent是从Message中取到的字段,准备替换到html模版中。 

let field1 = "SDK样式+自定义消息字段1" 

let field2 = "自定义样式+自定义消息字段2" 

let field3 = "自定义样式+自定义消息字段3" // 如果有多个内容需要替换,则逐个replace替换. 

```arkts
let html = customMsgHtmlData.replaceAll("{%customMsgField1_SDKStyle%}", field1) .replaceAll("{%customMsgField2_CustomStyle%}", field2) .replaceAll("{%customMsgField3_CustomStyle%}", field3); 
```

resolve(html) }else { // 不需要解析的类型,返回空字符串 resolve("") } }) } ) 

##### **添加转发按钮** 

IMKit 提供了 addMessageMoreAction 方法,可以增加长按消息点击“更多”之后,展示聊天页面底部的按钮 示例代码。 需 要在 routeSelectPage 中编写跳转到 App 侧开发选人页面。 

**逐条转发** :多条转发消息使用 示例代码 的 sendForwardMessages 方法。 

**合并转发** :合并转发消息使用 示例代码 的 sendForwardCombineMessage 方法。 

###### **TypeScript** 

forwardDialog: CustomDialogController | undefined forwardMessageArray: Message[] = [] 

async aboutToAppear(): Promise<void> { this.addMessageMoreItems() } 

- 135 - 

private addMessageMoreItems() { 

this.forwardDialog = new CustomDialogController({ 

builder: CustomListDialog({ itemTextAlign: TextAlign.Center, 

viewAllWidth: '95%', 

list: [$r("app.string.rc_stepwise_forwarding"), $r("app.string.rc_combine_forwarding"), $r("app.string.rc_cancel")], onItemClick: (index: number) => { // 关闭弹窗 this.forwardDialog?.close(); if (index === 2) { return 

} // 跳转到 App 侧开发选人页面 let forWardType = index === 0 ? ForWardType.Step : ForWardType.Combine 

```arkts
let params: ForWardMessageParam = { messages: this.forwardMessageArray, forWardType: forWardType }; 
```

this.routeSelectPage(params) 

} }), customStyle: true, offset: { dx: 0, dy: -30 }, alignment: DialogAlignment.Bottom }) 

RongIM.getInstance().conversationService().addMessageMoreAction({ 

actionId: 'message_more_forward', 

icon: $r("app.media.rc_message_more_forward"), 

onClick: (context: Context, messages: Message[]): boolean => { this.forwardMessageArray = messages this.forwardDialog?.open() return true }, 

onFilter: (messages: Message[]): boolean => { return true; }, location: 100 }) } 

private routeSelectPage(params: ForWardMessageParam) { // 跳转逻辑 

} 

export interface ForWardMessageParam { messages: Message[], 

- 136 - 

forWardType?: ForWardType } 

export enum ForWardType { /** * 逐条转发 */ Step = 1, /** * 合并转发 */ Combine = 2, } 

##### **转发消息示例代码** 

###### **TypeScript** 

import { ConversationIdentifier, ConversationType, FileMessage, FileMessageObjectName, GIFMessage, GIFMessageObjectName, ImageMessage, ImageMessageObjectName, HQVoiceMessageObjectName, Message, ObjectChecker, RongIM, TextMessage, SightMessage, TextMessageObjectName, SightMessageObjectName, LocationMessageObjectName, LocationMessage, HQVoiceMessage, RichContentMessageObjectName, RichContentMessage, ReferenceMessageObjectName, ReferenceMessage, MessageContent } from '@rongcloud/imkit'; 

- 137 - 

###### // 转发多条消息 

private async sendForwardMessages(forwardMessage: Message[], conversation: Conversation) { 

```arkts
for (let index = 0; index < forwardMessage.length; index++) { 
```

this.sendForwardMessage(forwardMessage[index], conversation); 

await new Promise<void>(resolve => setTimeout(resolve, 300)); 

} 

} 

###### // 转发单条消息 

private async sendForwardMessage(forwardMessage: Message, conversation: Conversation): Promise<void> { 

return new Promise(async () => { 

let createWithConversation(conversation) 

let msgContent = this.getMessageContent(forwardMessage.content, forwardMessage.objectName); if (!msgContent) { 

###### return 

} 

let msg = new Message(conversationIdentifier, msgContent); 

await RongIM.getInstance().messageService().sendMessage(msg) 

}) 

} 

###### // 合并转发消息 

public async sendForwardCombineMessage(forwardMessage: Message[], conversation: Conversation): Promise<void> { 

return new Promise(async () => { 

let result = await RongIM.getInstance().messageService().obtainCombineMessage(forwardMessage) if (result.code !== EngineError.Success) { 

###### return 

} 

let combineMsg = result.data as CombineMessage 

let msg = new Message(ConversationIdentifier.createWithConversation(conversation), combineMsg) await RongIM.getInstance().messageService().sendMediaMessage(msg) 

}); 

} 

private getMessageContent(messageContent: MessageContent, objName: string): MessageContent | undefined { 

if (objName === TextMessageObjectName) { 

let oldTextMsg = messageContent as TextMessage 

let textMsg = new TextMessage(); 

textMsg.content = oldTextMsg.content; 

return textMsg 

} else if (objName === ImageMessageObjectName) { 

let imageMsg = messageContent as ImageMessage 

- 138 - 

g g g 

g 

g 

let imageMessage = new ImageMessage(); 

imageMessage.isFull = true; 

imageMessage.name = imageMsg.name; 

imageMessage.remoteUrl = imageMsg.remoteUrl; 

- imageMessage.thumbnailBase64 = imageMsg.thumbnailBase64; return imageMessage 

- } else if (objName === FileMessageObjectName) { 

- let fileMsg = messageContent as FileMessage; 

- let fileMessage = new FileMessage(); 

- fileMessage.name = fileMsg.name; fileMessage.remoteUrl = fileMsg.remoteUrl; fileMessage.size = fileMsg.size; fileMessage.type = fileMsg.type; return fileMessage 

- } else if (objName === GIFMessageObjectName) { let imageMsg = messageContent as GIFMessage let imageMessage = new GIFMessage(); 

- imageMessage.name = imageMsg.name; imageMessage.remoteUrl = imageMsg.remoteUrl; return imageMessage 

- } else if (objName === SightMessageObjectName) { let sightMsg = messageContent as SightMessage let sightMessage = new SightMessage(); 

- sightMessage.base64 = sightMsg.base64; sightMessage.duration = sightMsg.duration; sightMessage.size = sightMsg.size; sightMessage.name = sightMsg.name; sightMessage.remoteUrl = sightMsg.remoteUrl; return sightMessage 

- } else if (objName === RichContentMessageObjectName) { let richContentMsg = messageContent as RichContentMessage let richContentMessage = new RichContentMessage(); 

- richContentMessage.title = richContentMsg.title richContentMessage.content = richContentMsg.content richContentMessage.imgUrl = richContentMsg.imgUrl richContentMessage.url = richContentMsg.url return richContentMessage 

- } else if (objName === LocationMessageObjectName) { let locationMsg = messageContent as LocationMessage let locationMessage = new LocationMessage(); 

- locationMessage.latitude = locationMsg.latitude; locationMessage.longitude = locationMsg.longitude; locationMessage.poi = locationMsg.poi; locationMessage.thumbnailBase64 = locationMsg.thumbnailBase64; locationMessage.type = locationMsg.type; 

- 139 - 

return locationMessage 

- } else if (objName === HQVoiceMessageObjectName) { 

let hqVoiceMsg = messageContent as HQVoiceMessage 

let hqVoiceMessage = new HQVoiceMessage(); hqVoiceMessage.name = hqVoiceMsg.name; 

hqVoiceMessage.remoteUrl = hqVoiceMsg.remoteUrl; 

hqVoiceMessage.duration = hqVoiceMsg.duration; 

return hqVoiceMessage 

- } else if (objName === CombineMessageObjectName) { 

let combineMsg = messageContent as CombineMessage 

- let combineMessage = new CombineMessage(); 

combineMessage.name = combineMsg.name; 

combineMessage.title = combineMsg.title; 

combineMessage.conversationType = combineMsg.conversationType; 

- combineMessage.nameList = combineMsg.nameList 

- combineMessage.summaryList = combineMsg.summaryList 

- combineMessage.remoteUrl = combineMsg.remoteUrl 

- return combineMessage 

- } 

return 

} 

###### **撤回消息** 

用户通过 App 成功发送了一条消息之后,可能发现消息内容错误等情况,希望将消息撤回,同时从接收者的消息记录中移除 该消息。IMKit 默认实现了消息撤回功能。 

###### 提示 

IMKit 在撤回消息后,会替换聊天记录中的原始消息为一条 objectName 为 RC:RcNtf 的撤回通知消息 

(RecallNotificationMessage),可参见服务端文档通知类消息格式。 

- 140 - 

##### **用法** 

IMKit 默认启用撤回功能。用户在会话页面长按消息(已发送成功的消息)可打开弹窗,选择撤回。消息撤回后在一定时间内 “ ” 可以 重新编辑 。 

##### **定制化** 

##### **修改消息可撤回的最大时间** 

IMKit 默认允许在消息发送后 180 秒内撤回。您可以通过全局配置调整该上限,需要在会话页面展示前设置。 

###### **TypeScript** 

let config = RongIM.getInstance().conversationService().getConversationConfig() config.setMaxRecallDuration(180) RongIM.getInstance().conversationService().setConversationConfig(config) 

##### **修改撤回后可重新编辑的时间** 

IMKit 默认允许在消息撤回后 30 秒内可点击 **重新编辑** ,仅文本消息支持撤回再编辑。您可以通过全局配置调整该上限,需要 在会话页面展示前设置。 

###### **TypeScript** 

let config = RongIM.getInstance().conversationService().getConversationConfig() config.setMaxEditableDuration(30) RongIM.getInstance().conversationService().setConversationConfig(config) 

##### **其他定制化** 

IMKit SDK 默认已经实现了一套消息撤回和展示逻辑,不需要额外调用会话相关 API。如果已有实现无法满足您的需求,可以 使用 RongIM 中相关 API。详见撤回消息。 

- 141 - 

##### **关闭撤回功能** 

IMKit 目前不支持关闭撤回功能。 

###### **引用回复** 

IMKit 支持引用回复功能,允许用户在聊天页面中回复彼此的消息。消息将出现在会话页面的消息列表组件中。引用回复功能 默认发送的消息包含引用消息内容对象 ReferenceMessage(类型标识:RC:ReferenceMsg)。 

##### **局限** 

- 142 - 

引用回复功能目前有以下限制: 

仅支持文本消息、文件消息、图文消息、图片消息、引用消息的引用。 

引用深度仅支持一度,即只能引用回复原始消息。如果多重引用,只展示上一层被引消息内容。 

##### **用法** 

IMKit 会话页面默认已启用引用回复功能。用户在会话页面长按消息,在弹框里选择 **引用消息** ,即可引用该消息。在输入区添 加消息内容后,SDK 默认会将输入内容与被引消息组合为 ReferenceMessage,并发送到会话中。 

##### **关闭引用回复功能** 

IMKit 目前不支持关闭引用回复功能。 

##### **自定义引用消息的 UI** 

引用回复功能默认发送的消息包含引用消息内容(RC:ReferenceMsg),引用消息使用 ReferenceMessageItemProvider 模板展示在消息列表中。 

如果需要调整内置消息样式,需继承 BaseMessageItemProvider<ReferenceMessage> 自行实现消息展示模板类,详 见自定义Provider。 

调用 addMessageItemProvider 的接口将该自定义模板提供给 SDK,objectName 传 

ReferenceMessageObjectName。 

###### **TypeScript** 

import { ReferenceMessageObjectName, RongIM } from "@rongcloud/imkit"; 

// 注册自定义引用消息 provider 给 IMKit 

RongIM.getInstance().conversationService().addMessageItemProvider(ReferenceMessageObjectName, new CustomReferenceMessageItemProvider()) 

###### **会话草稿** 

IMKit 支持会话草稿功能。 

###### 提示 

用户在会话页面输入框中输入文本后没有发送,退出会话页面到会话列表,会话列表会显示草稿提示及草稿内容。 

- 143 - 

##### **用法** 

IMKit 中默认已实现了获取会话草稿、删除草稿的功能和页面刷新,您不需要额外调用 API。 

##### **定制化** 

如果已有实现无法满足您的需求,可以使用 IMKit 提供的以下 API。 

##### **保存 / 删除会话草稿** 

使用 IMKit 核心类 RongIM 的 saveTextMessageDraft 方法保存或者删除一条草稿内容至指定会话。保存或者删除草稿会触 发会话列表重排序。 

提示 

清除草稿,draft 参数必须传空字符串,如果传 null 会导致接口调用失败。 

###### **接口原型** 

###### **TypeScript** 

- 144 - 

public saveTextMessageDraft(conversationId: ConversationIdentifier, draft: string): Promise<IAsyncResult<void>>; 

###### **参数说明** 

|参数|类型|说明|
|---|---|---|
|conversationId|ConversationIdentifer|会话标识|
|draft|string|草稿,空字符串代表清空草稿|

###### **示例代码** 

###### **TypeScript** 

let conId = ConversationIdentifier.createWith2(ConversationType.Private, "targetId") let draft = "草稿" 

RongIM.getInstance().conversationService().saveTextMessageDraft(conId, draft) .then(result => { 

if (result.code == EngineError.Success) { // 成功 

} else { // 失败 } }) 

##### **获取会话草稿** 

使用 IMKit 核心类 RongIM 的 getTextMessageDraft 方法获取指定会话的草稿。 

###### **TypeScript** 

getTextMessageDraft(conversationId: ConversationIdentifier): Promise<IAsyncResult<string>>; 

###### **参数说明** 

|参数|类型|说明|
|---|---|---|
|conversationId|ConversationIdentifer|会话标识|

###### **TypeScript** 

- 145 - 

let conId = ConversationIdentifier.createWith2(ConversationType.Private, "targetId") 

RongIM.getInstance().conversationService().getTextMessageDraft(conId) 

.then(result => { if (result.code == EngineError.Success) { 

// 成功 } else { // 失败 } }) 

###### **会话置顶** 

###### IMKit 提供设置会话置顶与展示置顶会话。 

- 146 - 

##### **用法** 

设置会话置顶后,该状态将会被同步到服务端。融云会为用户自动在设备间同步会话置顶的状态数据。客户端可以通过监听器 获取同步通知,也可以主动获取最新数据。 

##### **定制化** 

如果 IMKit 默认实现的功能不满足需求,您可以使用 IMKit 提供的 API。 

##### **设置会话置顶** 

设置会话置顶后,会话将在会话列表页面置顶显示。所有置顶会话按照会话时间降序排列。 

- 147 - 

客户端一般通过本地消息数据自动生成会话与会话列表。如果需要置顶的会话在本地尚不存在,您可以通过设置 isNeedCreate 参数为 true 来创建会话。 

###### **示例代码** 

###### **TypeScript** 

// 添加准备置顶/取消置顶的会话 

let conversationIds: List<ConversationIdentifier> = new List(); conversationIds.add(ConversationIdentifier.createWith2(ConversationType.Private, "targetId")); // 会话置顶参数 

```arkts
let option: ISetConversationTopOption = { // 是否置顶 isTop: !conversation.isTop, // 是否创建会话:对应的会话本地不存在时,true 将创建该会话; false 不创建该会话 isNeedCreate: false, // 是否更新会话时间,默认为 true isNeedUpdateTime: true, } RongIM.getInstance().conversationService().setConversationsToTop(conversationIds, option) 
```

###### **参数说明** 

|参数|类型|说明|
|---|---|---|
|conversationIds|List<ConversationIdentifer>|会话id标识列表|
|option|ISetConversationTopOption|置顶配置|

ISetConversationTopOption 参数 

|参数|类型|说明|
|---|---|---|
|isTop|boolean|是否置顶,true设置置顶;false取消置顶|
|isNeedCreate|boolean|是否创建会话:对应的会话本地不存在时,true将创建该会话;false不创建该会话|
|isNeedUpdateTime|boolean|是否更新会话时间,非必选,默认为true|

##### **监听置顶状态同步** 

即时通讯业务支持会话状态(置顶状态数据和免打扰状态数据)同步机制。设置会话状态同步监听器后,如果会话状态改变, 可在本端收到通知。同时也支持监听本端操作的修改置顶和免打扰状态。 

详细说明可参见多端同步免打扰/置顶。 

##### **获取会话置顶状态与置顶会话** 

- 148 - 

您可以从客户端主动获取会话置顶状态数据和置顶会话,但 IMKit SDK 未直接提供相关方法,您需要使用 IMLib 中提供的方 法。 

详见 IMLib 文档会话置顶 中的 **获取会话置顶状态** 与 **获取置顶会话列表** 。 

###### **水印组件** 

IMKit 支持为页面设置自定义水印组件,帮助提升内容安全性和品牌识别度。 

您可以通过配置水印组件,在指定页面展示自定义水印。目前仅支持在合并转发页面(CombinePage)生效。 

##### **功能概述** 

- 支持自定义水印组件的 UI 和参数。 

- 可灵活指定水印生效的页面类型。 

- 通过配置接口一键生效。 

##### **设置水印组件配置** 

通过 setWatermarkComponentConfig 方法设置水印组件配置。SDK 会根据配置决定哪些页面展示水印。 

##### **主要接口与类型说明** 

###### **TypeScript** 

- 149 - 

/** 

###### * 设置水印组件的自定义配置 

- @param componentConfig 组件配置,详见 WatermarkComponentConfig。page 不能为空。 

- @since 1.7.0 

*/ 

setWatermarkComponentConfig(componentConfig: WatermarkComponentConfig): void; 

###### /** 

- 水印组件配置对象 

- @since 1.7.0 

*/ 

export interface WatermarkComponentConfig extends BaseComponentConfig<[WatermarkComponentData]> { 

/** 

- 设置水印生效的页面,详见 WatermarkPageIdentifier。 

*/ 

page: WatermarkPageIdentifier[]; 

} 

/** 

- 水印自定义组件数据,封装必要参数透传给自定义组件 

- @since 1.7.0 

*/ 

export class WatermarkComponentData { /** 

- 上下文对象 */ 

context: Context | undefined; /** 

- 会话标识,可能为 undefined 

*/ 

convId: ConversationIdentifier | undefined; } 

/** 

- 支持展示水印的页面类型 

- @since 1.7.0 

*/ 

export enum WatermarkPageIdentifier { /** 

- 合并转发页面 

*/ CombinePage = 1, } 

- 150 - 

##### **参数说明** 

|参数名|类型|说明|
|---|---|---|
|identifer|ComponentIdentifer|组件标识|
|component|WrappedBuilder<[WatermarkComponentData]>|组件UI|
|page|WatermarkPageIdentifer[]|水印生效页面|
|警告|||

如未指定 page 参数或参数为空,配置将设置失败。 

###### WatermarkComponentData 字段说明 

|字段名|类型|说明|
|---|---|---|
|context|Context | undefned|上下文对象|
|convId|ConversationIdentifer |
undefned|会话标识|

##### **示例代码** 

以下示例展示如何自定义水印组件并应用到合并转发页面: 

###### **TypeScript** 

import { 

WatermarkComponentData, ConversationIdentifier, WatermarkComponentConfig, ComponentIdentifier, 

WatermarkPageIdentifier, RongIM 

- } from '@rongcloud/imkit'; 

###### // 构建自定义水印组件 

###### @Builder 

export function buildCustomWatermarkComponent(data: WatermarkComponentData) { // 传递 context 和 convId 给自定义组件 

CustomWatermarkComponent({ context: data.context, convId: data.convId }); 

} 

###### // 定义自定义水印组件结构 

@Component 

export struct CustomWatermarkComponent { 

- 151 - 

export struct CustomWatermarkComponent { 

@Prop context: Context; 

- @Prop convId: ConversationIdentifier | undefined; 

@State textArray: Array<number> = new Array(50).fill(0).map((_: number, index) => index + 1); 

build() { Flex({ wrap: FlexWrap.Wrap }) { ForEach(this.textArray, (_item: number, index: number) => { Text("默认水印文本") .fontSize(14) .fontColor("#999999") .opacity(0.15) .rotate({ angle: -15 }) .margin({ top: 40, bottom: 40, left: 20 + (index % 4 === 0 ? 0 : 40), right: 20 }) }, (item: number) => item.toString()) }.size({ width: '100%', height: '100%' }).backgroundColor(Color.Transparent) } } 

###### // 配置水印组件 

let WatermarkComponent: WatermarkComponentConfig = { identifier: ComponentIdentifier.WatermarkComponent, component: wrapBuilder(buildCustomWatermarkComponent), page: [WatermarkPageIdentifier.CombinePage] } 

###### // 应用水印组件配置 

RongIM.getInstance().conversationService().setWatermarkComponentConfig(WatermarkComponent); 

### **定制化** 

###### **发送消息** 

IMKit 内置会话页面已实现了发送各类型消息的功能和 UI。当您在自定义页面需要发送消息时,可使用 IMKit 核心类 RongIM 下发送消息的方法。这些方法除了提供发送消息的功能外,还会触发 IMKit 内置页面的更新。 

- 152 - 

IMKit 支持发送普通消息和媒体类消息(参考消息介绍),普通消息父类是 MessageContent,媒体消息父类是 MediaMessageContent。发送媒体消息和普通消息本质的区别为是否有上传数据过程。 

提示 

- 请务必使用 IMKit 核心类 RongIM 下发送消息的方法,否则不会触发页面刷新。 

- 发送普通消息使用 sendMessage 方法,发送媒体消息使用 sendMediaMessage 方法。 

- IMKit SDK 发送消息存在频率限制,每秒最多只能发送 5 条消息。 

##### **构造消息** 

参考 构造消息 

##### **发送普通消息** 

发送消息前需要构造 Message 消息对象。消息的 content 属性中可包含两大类消息内容:普通消息内容和媒体消息内容。 普通消息内容父类是 MessageContent,媒体消息内容父类是 MediaMessageContent。 

当您调用 RongIM 的发送消息方法时,SDK 会触发内置的会话列表和会话页面的更新。 

###### **接口原型** 

###### **TypeScript** 

public sendMessage(msg: Message): Promise<IAsyncResult<Message>>; 

###### **参数说明** 

参数名 类型 详细说明 msg Message 要发送的消息对象 

###### **示例代码** 

###### **TypeScript** 

- 153 - 

let conId = new (); 

conId.conversationType = ConversationType.Private 

conId.targetId = "targetId" 

let textMsg = new TextMessage(); textMsg.content = "内容"; 

RongIM.getInstance().messageService().sendMessage(new Message(conId, textMsg)) 

.then(result => { 

if (EngineError.Success !== result.code) { 

// 发送消息失败 return; } if (!result.data) { // 消息数据为空 return; } let msg = result.data as Message; }) 

##### **发送媒体消息** 

媒体消息 Message 对象的 content 字段必须传入 MediaMessageContent 的子类对象,表示媒体消息内容。例如图片消 息(ImageMessage)、GIF 消息(GIFMessage)等。其他内置媒体消息类型包括文件消息(FileMessage)、高清语音 消息(HQVoiceMessage)、小视频消息(SightMessage),建议先集成相应的 IMKit 插件。 

关于 IMKit SDK 内置媒体消息类型以及构造使用,可以参照 媒体消息 

发送媒体消息需要使用 sendMediaMessage 方法。SDK 会为图片、小视频等生成缩略图,根据默认压缩配置进行压缩,再 将图片、小视频等媒体文件上传到融云默认的文件服务器(文件存储时长),上传成功之后再发送消息。图片消息如已设置为 发送原图,则不会进行压缩。 

当您调用 RongIM 的发送消息方法时,SDK 会根据发送状态同步更新内置的会话列表和会话页面。 

###### **接口原型** 

###### **TypeScript** 

public sendMediaMessage( 

msg: Message, 

progressListener?: (msg: Message, progress: number) => void 

): Promise<IAsyncResult<Message>>; 

###### **参数说明** 

- 154 - 

参数名 类型 详细说明 msg Message 要发送的媒体消息对象,必须包含有效的媒体文件信 息 progressListener (msg: Message, progress: number) => 可选的上传进度回调函数 void 

###### **示例代码** 

###### **TypeScript** 

```arkts
let imageMessage = new ImageMessage(); imageMessage.isFull = true; imageMessage.name = "name"; imageMessage.remoteUrl = "图片地址"; imageMessage.thumbnailBase64 = "缩略图Base64"; let conId = new ConversationIdentifier(); conId.conversationType = ConversationType.Private; conId.targetId = "targetId"; await RongIM.getInstance().messageService().sendMediaMessage( new Message(conId, imageMessage), (msg: Message, progress: number) => { // progress 消息进度 }) .then((result: IAsyncResult<Message>) => { if (result.code == EngineError.Success) { // 发送成功 } else { // 发送失败 } }) 
```

##### **发送多媒体消息并且上传到自己的服务器** 

您可以直接发送您服务器上托管的文件。将媒体文件的 URL(表示其位置)作为媒体消息的 remoteUrl 参数,在构建媒体消 息内容时传入。在这种情况下,您的文件不会托管在融云服务器上。当您发送带有远程 URL 的文件消息时,文件大小没有限 制,您可以直接使用 sendMessage 方法发送消息。 

###### **接收消息** 

IMKit SDK 提供了消息接收监听器 MessageReceivedListener,可接收实时消息或离线消息。您可以拦截 IMKit SDK 接收 的消息,并进行相应的业务操作。 

- 155 - 

##### **设置 / 移除消息接收监听器** 

IMKit SDK 提供了 addMessageReceiveListener / removeMessageReceiveListener 方法,支持设置多个消息接收监听 器。 

建议您在初始化之后,连接 IM 之前注册消息监听,且在应用程序声明周期内保持设置。请注意不要重复添加,避免内存泄 露。如果在页面中监听,建议在 aboutToAppear 调用,在 aboutToDisappear 移除监听。 

##### **添加消息监听器** 

SDK 支持添加监听器。所有接收到的消息都会在此接口方法中回调: 

###### **TypeScript** 

RongIM.getInstance().messageService().addMessageReceiveListener() 

##### **移除消息监听器** 

SDK 支持移除监听器。为了避免内存泄露,请在不需要监听时将监听器移除: 

###### **TypeScript** 

RongIM.getInstance().messageService().removeMessageReceiveListener() 

##### **消息接收监听器** 

当客户端连接成功后,服务端会将所有离线消息以消息包(? Package)的形式下发给客户端,每个 Package 中最多含 200 条消息。客户端会解析 Package 中的消息,逐条上抛并通知应用。 

SDK 接收到消息时会触发以下方法。 

###### **接口原型** 

###### **TypeScript** 

```arkts
interface MessageReceivedListener { /** * 消息接收监听 * @param message 消息体 * @param info 消息接收信息 */ onMessageReceived(message: Message, info: ReceivedInfo): void; } 
```

###### **参数说明** 

- 156 - 

|参数|类型|说明||
|---|---|---|---|
|message|Message|接收的消息||
|info |ReceivedInfo|消息接收信息||
|ReceivedIn|fo说明|||
|参数|类型||说明|
|left|number||还剩余的未接收的消息数|
|hasPackage|boolean|SDK拉取服务器的消息|以包(package)的形式批量拉取,有package存在就意味着远端服务器 还有消息尚未被SDK拉取|
|isOfine|boolean||是否是离线消息|

同时满足以下条件,表示离线消息已收取完毕: 

hasPackage 为 false :表示当前正在解析最后一包消息。 

left 为 0:表示最后一个消息包中最后一条消息已接收完毕。 

##### **消息收取完毕** 

每次连接成功后,离线消息收取完毕时会触发以下回调方法。如果没有离线消息,连接成功后会立即触发。 

###### **TypeScript** 

```arkts
interface MessageReceivedListener { /** * 离线消息接收完成远端消息同步完成回调,每次连接成功触发一次远端没有消息的时候,连接成功后会立即触发 * 远端有大量历史消息的时候,连接成功会等待消息接收完成之后触发 */ onOfflineMessageSyncCompleted(): void; }``` 
```

###### **获取历史消息** 

IMKit SDK 默认已经实现了一整套消息的获取和展示逻辑,使用默认会话列表和会话页面时,不需要额外调用获取消息相关 API。 

如果您有自定义需求,可以调用 IMLib SDK 中获取消息相关的 API。 

请注意,IMLib 方法并不提供页面展示和刷新能力,您需要根据业务需求自定义实现页面展示和刷新。 

- 157 - 

获取本地数据库中的历史消息。 

IMLib 方法:获取本地消息 

获取远端服务器的历史消息。 

IMLib 方法:获取服务器消息 

###### **拦截消息** 

IMKit 支持设置消息拦截器 MessageInterceptor,可在消息发送前前进行拦截,方便应用程序进行自定义处理。 

##### **消息拦截器说明** 

MessageInterceptor 包含了拦截消息(支持同步)、发送媒体消息进行上传媒体资源前拦截、下载媒体消息的拦截器。 

提示 

从 1.4.3 版本开始,onWillSendMessage 支持修改 message 对象,同时支持了同步接口 onWillSendMessageSync。 

###### **接口说明** 

###### **TypeScript** 

interface MessageInterceptor { /** 

- 在发消息前拦截并修改消息体 

- @param message 即将发送的消息体 

- @returns 修改之后的消息体 

- @warning如果返回的 Message 为空或者 Message.content 为空,该消息将不会发送出去 */ 

onWillSendMessage?: (message: Message) => Message | null; 

/** 

- 在发消息前拦截并修改消息体,同步接口 

- @param message 即将发送的消息体 

- @returns 修改之后的消息体 

- @warning如果返回的 Message 为空或者 Message.content 为空,该消息将不会发送出去 

- @version 1.4.3 

- */ 

onWillSendMessageSync?: (message: Message) => Promise<Message | null>; 

/** 

- 158 - 

###### * 发送媒体消息进行上传媒体资源前拦截,同步接口 

- # 示例代码 

*```ts 

* let interceptor: MessageInterceptor = { 

- onWillUploadMessageSync: async (message: Message, localPath: string) => { 

- // 拦截接口,如果决定拦截则返回此接口,在此接口中使用 transfer 做进度回传操作。不拦截返回 null 即可。 

- let transferCallback = (transfer: MediaMessageTransfer) => { 

*         let progress = 0 *         // 此处模拟异步回调上传进度与结果,需根据实际业务处理 *         let timer = setInterval(() => { *           progress += 10 *           if (progress < 100) { *             // 模拟回传进度 *             transfer.updateProgress(progress) *           } else { *             // 模拟上传成功、失败、取消 *             // 上传成功,回传地址 *             transfer.success("业务侧上传后的远端地址") *             // 上传失败 *             // transfer.error() *             // 上传取消 

- // transfer.cancel() 

*             clearInterval(timer); *           } *         }, 100); *       } 

*       return transferCallback *     } 

*   } 

- RongIM.getInstance().messageService().setMessageInterceptor(interceptor) 

*``` 

- @param message 即将上传并发送的消息体 

- @param localPath 即将上传的本地路径 

- @returns 拦截接口。返回 `(transfer: MediaMessageTransfer) => void` 代表由开发者控制上传,返回 null 代表 由SDK执行上传。 

- @version 1.4.3 

*/ 

onWillUploadMessageSync?: (message: Message, 

localPath: string) => Promise<((transfer: MediaMessageTransfer) => void) | null>; 

/** 

- 下载媒体消息的拦截器,同步接口 

- # 示例代码 

*``` 

- *let interceptor: MessageInterceptor = { 

- 159 - 

- onWillDownloadMessageSync: async (message: Message, remoteUrl: string) => { 

- // 拦截接口,如果决定拦截则返回此接口,在此接口中使用 transfer 做进度回传操作。不拦截返回 null 即可。 

- let transferCallback = (transfer: MediaMessageTransfer) => { 

- let progress = 0 

- // 此处模拟异步回调下载进度与结果,需根据实际业务处理 

- let timer = setInterval(() => { 

*        progress += 10 *        if (progress < 100) { 

- // 模拟回传进度 

- transfer.updateProgress(progress) *        } else { 

- // 模拟下载成功、失败、取消 

- // 下载成功,回传地址 

- transfer.success("下载后的本地地址") 

- // 下载失败 

- // transfer.error() 

*          // 下载取消 

*          // transfer.cancel() *          clearInterval(timer); *        } *      }, 100); *    } 

- return transferCallback 

*  }, 

*} 

- *RongIM.getInstance().messageService().setMessageInterceptor(interceptor) 

*``` 

- @param message 即将下载的消息体 

- @param remoteUrl 即将下载的地址 

- @returns 拦截接口。返回 `(transfer: MediaMessageTransfer) => void` 代表由开发者控制下载,返回 null 代表 由SDK执行下载。 

- @version 1.4.3 

*/ 

onWillDownloadMessageSync?: (message: Message, 

remoteUrl: string) => Promise<((transfer: MediaMessageTransfer) => void) | null>; 

/** 

- 下载文件的拦截器,同步接口 

- # 示例代码 

*``` 

- let interceptor: MessageInterceptor = { 

- onWillDownloadFileSync: async (uniqueId: string, remoteUrl: string, fileName: string) => { 

- // 拦截接口,如果决定拦截则返回此接口,在此接口中使用 transfer 做进度回传操作。不拦截返回 null 即可。 

- let transferCallback = (transfer: MediaMessageTransfer) => { 

*       let progress = 0 

- 160 - 

###### *       // 此处模拟异步回调下载进度与结果,需根据实际业务处理 

*       let timer = setInterval(() => { *         progress += 10 *         if (progress < 100) { *           // 模拟回传进度 *           transfer.updateProgress(progress) *         } else { *           // 模拟下载成功、失败、取消 *           // 下载成功,回传地址 *           transfer.success("下载后的本地地址") *           // 下载失败 *           // transfer.error() *           // 下载取消 *           // transfer.cancel() *           clearInterval(timer); *         } *       }, 100); *     } *     return transferCallback *   } * } * RongIM.getInstance().messageService().setMessageInterceptor(interceptor) *``` 

- @param uniqueId 下载标识 

- @param remoteUrl 即将下载的文件地址 

- @param fileName 即将下载的文件名 

- @returns 拦截接口。返回 `(transfer: MediaMessageTransfer) => void` 代表由开发者控制下载,返回 null 代表 由SDK执行下载。 

- @version 1.4.3 

*/ 

onWillDownloadFileSync?: (uniqueId: string, remoteUrl: string, fileName: string) => Promise<((transfer: MediaMessageTransfer) => void) | null>; } 

##### **设置消息拦截器** 

使用 RongIM 的 setMessageInterceptor 设置消息拦截器。代码示例说明如下: 

###### **TypeScript** 

- 161 - 

let intercept: MessageInterceptor = { 

onWillSendMessage: (message: Message) => { 

// 可以根据业务来处理message对象 

return message }, // 按需实现其他接口 } 

RongIM.getInstance().messageService().setMessageInterceptor(intercept) 

###### **删除消息** 

单聊会话、群聊会话的参与者可删除会话中的消息。IMKit 会话页面默认已实现了长按删除消息的功能,支持仅删除单条本地 消息,或同步删除本地和远端的单条消息。 

您可以修改 IMKit 会话页面长按消息菜单中删除按钮的行为,详见会话页面。如果 IMKit 的已有实现无法满足您的需求,可以 直接使用 IMKit SDK 提供的删除消息接口。调用 IMKit 的删除 API 会同时触发会话列表和会话页面的刷新。 

###### 提示 

- App 用户的单聊会话、群聊会话、系统会话的消息默认仅存储在本地数据库中,仅支持从本地删除。如果 App(App Key/环境)已开通单群聊消息云端存储,该用户的消息还会保存在融云服务端(默认 6 个月),可从 远端历史消息记录中删除消息。 

- 针对单聊会话、群聊会话,如果通过任何接口以传入时间戳的方式删除远端消息,服务端默认不会删除对应的离 线消息补偿(该机制仅会在打开多设备消息同步开关后生效)。此时如果换设备登录或卸载重装,仍会因为消息 补偿机制获取到已被删除的历史消息。如需彻底删除消息补偿,请提交工单,申请开通 **删除服务端历史消息时同 时删除多端补偿的离线消息** 。如果以传入消息对象的方式删除远端消息,则服务端一定会删除消息补偿中的对应 消息。 

##### **同时删除本地与远端消息** 

IMKit 提供了删除本地数据库消息 + 服务端消息的接口:通过消息对象删除消息 与 通过会话删除。两个接口均提供了是否删 除远端消息参数 (remoteDelete),设置为 true 则会删除远端消息: 

##### **通过消息对象删除消息** 

您可以使用 RongIM 的 batchDeleteMessage 方法,通过消息对象删除指定会话在本地消息数据中的一条或一组消息,删除 成功后会刷新会话和会话列表页面。请确保所提供的消息对象均属于同一会话。 

- 仅删除本地消息, remoteDelete 参数设置为 false 

- 删除本地 + 远端消息,remoteDelete 参数设置为 true 

**接口原型** 

- 162 - 

###### **TypeScript** 

public batchDeleteMessage( conId: ConversationIdentifier, messages: Message[], remoteDelete?: boolean ): Promise<IAsyncResult<void>>; 

###### **示例代码** 

###### **TypeScript** 

```arkts
let conId = new ConversationIdentifier(); conId.conversationType = ConversationType.Private; conId.targetId = "会话 ID"; 
let messages: Message[] = []; for (let i = 0; i < 10; i++) { // msg 必须是发送成功的消息,此处进行简写 let msg : Message; messages.push(msg); } 
```

// 是否删除远端 

let remoteDelete = true; 

RongIM.getInstance().messageService().batchDeleteMessage(conId, messages, remoteDelete).then(result => { 

if (EngineError.Success !== result.code) { 

// 批量删除消息失败 return; } // 批量删除消息成功 }) 

###### **参数说明** 

|参数|类型|说明|
|---|---|---|
|conId|ConversationIdentifer|会话标识|
|messages|Message[]|消息对象数组,需要属于同一会话|
|remoteDelete|boolean|是否删除远端|

##### **通过会话删除消息** 

- 163 - 

使用 RongIM 的 deleteConversationMessages 方法可删除指定单个会话在本地数据库中的全部消息。删除成功后会刷新 会话和会话列表页面。 

- 仅删除本地消息, remoteDelete 参数设置为 false 

删除本地 + 远端消息,remoteDelete 参数设置为 true 

###### **接口原型** 

###### **TypeScript** 

public deleteConversationMessages(conId: ConversationIdentifier, remoteDelete?: boolean): 

Promise<IAsyncResult<void>>; 

###### **示例代码** 

###### **TypeScript** 

```arkts
let conId = new ConversationIdentifier(); conId.conversationType = ConversationType.Private; conId.targetId = "会话 ID"; 
```

###### // 是否删除远端 

let remoteDelete = true; 

RongIM.getInstance().messageService().deleteConversationMessages(conId, remoteDelete).then(result => 

{ 

if (EngineError.Success !== result.code) { 

- // 删除指定单个会话消息失败 

- return; 

- } 

- // 删除指定单个会话消息成功 

}) 

###### **参数说明** 

|参数|类型|说明|
|---|---|---|
|conId|ConversationIdentifer|会话标识|
|messages|Message[]|消息对象数组|
|remoteDelete|boolean|是否删除远端|

##### **仅删除本地消息** 

如果希望仅删除本地消息,通过消息对象删除消息 与 通过会话删除的 remoteDelete 参数传 false 即可。 

- 164 - 

##### **仅删除服务端消息** 

IMKit 没有仅删除服务端消息接口,可以参照 IMLib 删除消息提供的 cleanRemoteHistoryMessagesByTime 与 deleteRemoteMessages 。 

###### **撤回消息** 

IMKit SDK 默认已经实现了一套消息撤回和展示逻辑,不需要额外调用会话相关 API。如果已有实现无法满足您的需求,可以 使用 RongIM 中相关 API。 

##### **撤回消息** 

您可以在自定义页面调用以下方法撤回消息,该方法会同时触发会话列表和会话页面的刷新。 

###### **示例代码** 

###### **TypeScript** 

RongIM.getInstance().messageService().recallMessage(message) 

###### **参数说明** 

|参数|类型|说明|
|---|---|---|
|message|Message|要撤回的消息。|

##### **监听他人撤回消息事件** 

您可以添加监听器,监听已接收的消息被撤回的事件。 

###### **示例代码** 

###### **TypeScript** 

let recalledListener: MessageRecalledListener = { 

onMessageRecalled: (message: Message, recallMessage: RecallNotificationMessage) => { 

// 收到撤回消息 

} 

} 

RongIM.getInstance().messageService().addMessageRecalledListener(recalledListener) 

###### // 不需要时可移除 

RongIM.getInstance().messageService().removeMessageRecalledListener(recalledListener) 

- 165 - 

###### **插入消息** 

##### **功能描述** 

您可以在会话页面内插入一条消息。通过此方法插入的消息,会将消息实体对应的内容插入数据源中并更新 UI。 

##### **插入本地消息** 

IMKit 从 1.4.3 版本开始支持插入本地消息。 

向本地会话中插入一条发送方向的消息。此消息必须为客户端会存储的消息类型,参考消息介绍文档的 **了解消息存储策略** 。 该方法只是将消息存储在 SDK 本地数据库中,不会实际发送给服务器和对方。插入消息后, 会自动刷新 UI 界面。 

###### **接口原型** 

###### **TypeScript** 

/** * 单条消息入库 * * Message 下列属性会被入库,其他属性会被抛弃: * ``` * conversationType   会话类型 * targetId           会话 ID * direction          消息方向,默认为发送 * senderId           发送者 ID * receivedStatus     接收状态,默认为未读 * sentStatus         发送状态,默认为发送失败 * sentTime           发送时间 * content            消息内容 * objectName         消息类型,设置 content 的时候 SDK 会自动赋值对应的 objectName * messageUid         服务端生产的消息唯一 ID,如要携带该字段需要保证入库后是唯一的 * extra              扩展信息 * ``` 

- @param Message 需要入库的消息,会话类型不支持聊天室和超级群 

- @returns 入库结果 * @version 1.4.3 */ 

public insertMessage(msg: Message): Promise<IAsyncResult<Message>> 

**示例代码** 

- 166 - 

###### **TypeScript** 

```arkts
let conId = new ConversationIdentifier(); conId.conversationType = ConversationType.Private; conId.targetId = "会话 Id"; 
```

let txtMsg = new TextMessage(); txtMsg.content = "文本内容"; 

let msg = new Message(conId, txtMsg); msg.senderId = "发送方 Id"; 

RongIM.getInstance().messageService().insertMessage(msg).then(result => { if (EngineError.Success !== result.code) { 

// 单条消息入库失败 return; } if (!result.data) { 

// 单条入库的消息为空 return; } 

- // 单条入库成功的消息 

let message = result.data as Message; 

}); 

###### **搜索消息** 

您可以通过 IMLib 中提供的消息搜索相关 API 实现消息搜索功能。 

IMKit 中没有提供消息搜索的功能入口及展示页面,您需要根据业务需求在应用层实现消息搜索的 UI 展示。 

IMLib 提供三种搜索消息的方法: 

根据关键字搜索消息 

IMLib 方法:searchConversationsWithResult 

根据用户 Id 搜索 

IMLib 方法:searchMessagesByUser() 

IMLib 方法:searchMessagesByUsers() 

根据关键字,搜索指定会话中指定时间段内的消息 

IMLib 方法:searchMessages() 

- 167 - 

###### **自定义消息和 provider** 

##### **自定义普通消息** 

##### **1. 编写自定义普通消息的代码** 

自定义消息相关内容参考 IMLib 的自定义消息 

###### **示例代码** 

###### **TypeScript** 

- 168 - 

import { MessageTag, MessageContent, MessageFlag, JsonConverter } from '@rongcloud/imkit'; 

/** 

* 消息标识 * @version 1.0.0 */ 

export const CustomTextMessageObjectName = "RCD:TstMsg"; 

/** 

* 自定义文本消息 * */ 

@MessageTag(CustomTextMessageObjectName, MessageFlag.Count) export class CustomTextMessage extends MessageContent { // 文本内容 content: string = ''; 

constructor() { super(); } 

encode(): string { let map = super.encodeBaseData(); 

// 将文本内容放到字典 map.set('content', this.content) 

return JsonConverter.stringifyFrom HashMap(map); 

} 

decode(contentString: string): void { let hashMap = JsonConverter.parseToHashMap(contentString); 

super.decodeBaseData(hashMap); 

// 将文本内容从字典中解出 

if (hashMap.get("content")) { this.content = hashMap.get("content") as string; 

} 

} 

getClassName(): string { return CustomTextMessage.name } 

} 

- 169 - 

##### **2. 将自定义普通消息注册给 IMLib** 

您需要在 SDK 初始化后,IM 连接之前将消息注册给 IMLib,才可以保证消息能够正常的收发。 

###### **TypeScript** 

```arkts
let clazzList : List<MessageContentConstructor> = new List(); clazzList.add(CustomTextMessage); IMEngine.getInstance().registerMessageType(clazzList); 
```

##### **3. 编写普通消息 provider** 

普通消息是指带头像的消息,例如常见的文本图片等。 

###### **示例代码** 

###### **TypeScript** 

/** 

* Created on 2024/07/09 * @author 融云 */ import { BaseMessageItemProvider, MessageBubbleView, UiMessage } from '@rongcloud/imkit'; import { CustomTextMessage } from '../message/CustomTextMessaget'; 

export class CustomTextMessageItemProvider extends BaseMessageItemProvider<CustomTextMessage> { public getMessageWrapBuilder(): WrappedBuilder<[Context, UiMessage, number]> { return wrapBuilder(bindTextMessageData); } 

public isShowSummaryName(context: Context, messageContent: CustomTextMessage): boolean { return true; 

} public getSummaryTextByMessageContent(context: Context, messageContent: CustomTextMessage): Promise<MutableStyledString> { return new Promise((resolve) => { let content = messageContent.content; if (content.concat("\n")) { content = content.replaceAll("\n", " "); } resolve(new MutableStyledString(content)); }); } } 

- 170 - 

###### @Builder 

export function bindTextMessageData(context: Context, uiMessage: UiMessage, position: number) { CustomTextMessageView({ uiMessage: uiMessage }) 

###### } 

###### @Component 

export struct CustomTextMessageView { 

@ObjectLink uiMessage: UiMessage private textMessage: CustomTextMessage = new CustomTextMessage() controller: TextController = new TextController(); 

- @State isClickLook: boolean = false // 是否点击了查看 

private styledString: MutableStyledString = new MutableStyledString('') 

aboutToAppear(): void { 

this.textMessage = this.uiMessage.message.content as CustomTextMessage 

} 

build() { 

MessageBubbleView({ 

this.uiMessage, 

this.uiMessage.senderInfo 

}) { 

// 普通模式 

Text( , { controller: this.controller }). 

fontSize(17). 

fontColor($r('app.color.rc_color_111F2C')). 

lineHeight(21). 

margin(10). 

onAttach(() => { 

- //先让其显示内容 

this.styledString = new MutableStyledString(this.textMessage.content); 

this.controller.setStyledString(this.styledString); 

}) } } } 

##### **4. 将消息和 provider 进行绑定** 

将自定义普通消息和自定义普通消息的 provider 进行绑定,保证该消息能在 UI 上正常展示 

**示例代码** 

###### **TypeScript** 

- 171 - 

###### // 获取会话服务 

let conversationService = RongIM.getInstance().conversationService() 

// 注册自定义文本消息和 provider 给 IMKit,方便聊天页面 UI 展示 conversationService.addMessageItemProvider(CustomTextMessageObjectName, new CustomTextMessageItemProvider()) 

##### **5. 使用自定义消息普通消息** 

###### **示例代码** 

###### **TypeScript** 

```arkts
let conId = new ConversationIdentifier(); conId.conversationType = ConversationType.Private; conId.targetId = "会话 Id"; 
```

let textMsg = new CustomTextMessage(); textMsg.content = '自定义文本消息' 

let msg = new Message(conId, textMsg); 

RongIM.getInstance().messageService().sendMessage(msg).then((result: IAsyncResult<Message>) => { if (result.code === EngineError.Success) { 

promptAction.showToast({ " " message: 发送自定义文本消息成功 , bottom: 400, 

}) } }) 

##### **自定义小灰条消息** 

##### **1. 编写自定义小灰条消息的代码** 

自定义消息相关内容参考 IMLib 的自定义消息 

###### **示例代码** 

###### **TypeScript** 

- 172 - 

/** 

* @date 2024/12/16 

 * @author 融云

*/ 

import { JsonConverter, MessageContent, MessageFlag, MessageTag, StringChecker } from '@rongcloud/imlib'; 

export const CustomInfoMessageObjectName = "RCD:InfoMsg"; 

/** 

* 自定义小灰条消息 */ 

@MessageTag(CustomInfoMessageObjectName, MessageFlag.Save) export class CustomInfoMessage extends MessageContent { /** 

* 小灰条内容 */ message: string = ""; 

constructor() { super(); } 

```arkts
encode(): string { let map = super.encodeBaseData(); if (StringChecker.isValid(this.message)) { map.set("message", this.message); } return JsonConverter.stringifyFromHashMap(map); } 
```

decode(contentString: string): void { let map = JsonConverter.parseToHashMap(contentString); 

super.decodeBaseData(map); 

if (map.get("message")) { this.message = map.get("message") as string; } } 

getClassName(): string { return CustomInfoMessage.name; } 

} 

- 173 - 

##### **2. 将自定义小灰条消息注册给 IMLib** 

您需要在 SDK 初始化后,IM 连接之前将消息注册给 IMLib,才可以保证消息能够正常的收发。 

###### **示例代码** 

###### **TypeScript** 

```arkts
let clazzList : List<MessageContentConstructor> = new List(); clazzList.add(CustomTextMessage); clazzList.add(CustomInfoMessage); IMEngine.getInstance().registerMessageType(clazzList); 
```

##### **3. 编写小灰条消息 provider** 

小灰条消息一般居中显示,无头像,常见的比如撤回消息 

###### **示例代码** 

###### **TypeScript** 

import { BaseNotificationMessageItemProvider, UiMessage } from "@rongcloud/imkit"; import { CustomInfoMessage } from "../message/CustomInfoMessage"; 

/** * 自定义小灰条消息 provider */ export class CustomInfoMessageProvider extends BaseNotificationMessageItemProvider<CustomInfoMessage> { public getMessageWrapBuilder(): WrappedBuilder<[Context, UiMessage, number]> { return wrapBuilder(bindMessageData); 

- } 

public getSummaryTextByMessageContent(context: Context, messageContent: CustomInfoMessage): Promise<MutableStyledString> { return new Promise((resolve, reject) => { 

resolve(new MutableStyledString(messageContent.message)); }); } } 

###### @Builder 

export function bindMessageData(context: Context, messageModel: UiMessage, position: number) { InfoMessageView({ context: context, messageModel: messageModel}) 

} 

- 174 - 

@Component 

struct InfoMessageView { @Require @Prop context: Context; 

@ObjectLink messageModel: UiMessage 

private messageContent: CustomInfoMessage = new CustomInfoMessage(); 

aboutToAppear(): void { 

this.messageContent = this.messageModel.message.content as CustomInfoMessage; } build() { Row() { Text(this.messageContent.message). backgroundColor($r('app.color.rc_color_EDEDED')). borderRadius(8). fontSize(14). fontColor($r('app.color.rc_color_85909C')). padding(10) }.margin({ top: 10, bottom: 10 

}).justifyContent(FlexAlign.Center).alignItems(VerticalAlign.Center).width('100%') } } 

##### **4. 将自定义小灰条消息和 provider 进行绑定** 

将自定义小灰条消息和 provider 进行绑定,保证该消息能在 UI 上正常展示 

###### **TypeScript** 

###### // 获取会话服务 

let conversationService = RongIM.getInstance().conversationService() 

// 注册自定义小灰条消息和 provider 给 IMKit,方便聊天页面 UI 展示 conversationService.addMessageItemProvider(CustomInfoMessageObjectName, new CustomInfoMessageProvider()); 

##### **5. 使用自定义小灰条消息** 

###### **TypeScript** 

- 175 - 

let conId = new (); 

conId.conversationType = ConversationType.Private; conId.targetId = "会话 Id"; 

```arkts
let infoMsg = new CustomInfoMessage(); infoMsg.message = "自定义小灰条消息"; let msg = new Message(conId, infoMsg); 
```

RongIM.getInstance().messageService().sendMessage(msg).then((result: IAsyncResult<Message>) => { if (result.code === EngineError.Success) { 

promptAction.showToast({ " " message: 发送自定义小灰条消息成功 , bottom: 400, }) } }) 

##### **移除消息 Provider** 

IMKit SDK 中 UnknownMessageObjectName 的 provider 是当做占位使用的,可以被覆盖,但是不允许被移除。 

移除 objectName 对应的 provider 之后,如果 SDK 做消息展示时发现对应消息的 objectName 没有对应的 provider,会 使用 UnknownMessageObjectName 的 provider。 

###### **示例代码** 

###### **TypeScript** 

###### // 获取会话服务 

let conversationService = RongIM.getInstance().conversationService() 

// 移除消息 provider,传入消息的objectName 

conversationService.removeMessageItemProvider(TextMessageObjectName); 

##### **替换消息 Provider** 

您可以先移除消息的 provider ,然后将消息和 provider 重新进行绑定。 

###### **示例代码** 

###### **TypeScript** 

- 176 - 

###### // 获取会话服务 

let conversationService = RongIM.getInstance().conversationService() 

###### // 移除消息 provider,传入消息的objectName 

conversationService.removeMessageItemProvider(TextMessageObjectName); 

###### // 将消息和 provider 重新进行绑定 

conversationService.addMessageItemProvider(CustomTextMessageObjectName, new CustomTextMessageItemProvider()) 

###### **自定义长按消息菜单** 

用户在会话页面长按消息可打开弹窗,根据当前消息类型、会话类型提供不同选项。您可以在自定义菜单选项的显示名称、顺 序、以及自行增删菜单选项。 

##### **自定义长按消息弹窗的菜单选项** 

您可以通过 addMessageItemLongClickAction 方法设置会话页面的长按消息事件监听,在相关监听方法中自定义事件: 

###### **示例代码** 

###### **TypeScript** 

- 177 - 

let msgLongClickAction :ItemLongClickAction<Message> = { 

obtainTitle: (context: Context, data: Message): string | Resource => { 

return "自定义的消息长按事件" 

}, 

onClick: (context: Context, data: Message): void => { 

promptAction.showToast({message : "点击了自定义的消息长按事件"}) 

}, 

onFilter: (data: Message): boolean => { 

// 是否显示该长按事件?true 显示;false 不显示 

// 开发者可以根据 Message 对象的会话类型或者消息类型决定是否显示 return true; }, 

// 自定义的消息长按事件 Id,相同的 Id 的长按事件只会增加一次 actionId: 'CustomMessageActionId' } 

RongIM.getInstance().conversationService().addMessageItemLongClickAction(msgLongClickAction); 

###### **参数说明** 

ItemLongClickAction 类属性如下表所示。 

|属性|类型|描述|
|---|---|---|
|obtainTitle|string|显示名称。|
|onClick|(context: Context, data: Message):|长按消息监听函数。|
||void||
|onFilter|int|控制是否会被显示出来的过滤器。|
|actionId|Filter|自定义的消息长按事件Id,相同的Id的长按事件只会增加一次|

##### **自定义消息多选操作菜单** 

在长按消息弹窗的菜单选项选择 **更多** 后,SDK 进入消息多选模式,多选模式下默认提供了删除按钮。您可以增删已有按钮、 添加自定义按钮。 

IMKit SDK没有内置消息转发功能,实现可以参照:转发消息实现。 

###### **示例代码** 

###### **TypeScript** 

- 178 - 

let msgMoreAction : MessageMoreAction = { 

actionId: 'message_more_forward',// 动作 Id 

location: 100, // 按钮将放置在底部,根据 location 值,按照从小到大的顺序依次向右排列。 icon: $r("app.media.rc_message_more_forward"), // 图标 

onClick: (context: Context, data: Message[]): boolean => { // 处理自定义的点击事件 // return true :聊天页面依旧处于多选状态 // return false : 聊天页面退出多选状态 promptAction.showToast({message : "点击了聊天页面底部的更多按钮"}); return true }, onFilter: (data: Message[]): boolean => { // 是否显示该按钮,true 显示,false 不显示 return true; } } RongIM.getInstance().conversationService().addMessageMoreAction(msgMoreAction) 

###### **获取会话** 

IMKit SDK 默认已经实现了一整套会话获取和展示逻辑,使用默认会话列表和会话页面时,不需要额外调用会话相关 API。如 果已有实现无法满足您的需求,可以使用 IMLib SDK 中相关 API,例如: 

- IMEngine#getConversation() :获取指定会话 

- IMEngine#getConversationListByPage() :分页获取会话列表 

- IMEngine#getTopConversationListByPage() :分页获取置顶会话列表 

- IMEngine#getBlockedConversationListByPage() :分页获取免打扰会话列表 

- IMEngine#getUnreadConversations() :获取未读会话列表 

###### 提示 

具体使用方法请参见 IMLib 文档 获取会话。注意,IMLib 的方法并不提供页面刷新能力,您需要根据业务需求自定义 通知机制进行页面刷新。 

###### **删除会话** 

IMKit 默认在长按会话时显示以下弹窗,实现了删除会话功能。 

- 179 - 

如果已有实现无法满足您的需求,可以使用 RongIM 提供的以下 API: 

##### **删除指定会话** 

从会话列表移除会话项目,但不删除会话内的历史消息。该方法会自动触发会话列表页面刷新。 

**示例代码** 

###### **TypeScript** 

- 180 - 

let conId = new (); 

conId.conversationType = ConversationType.Private; conId.targetId = "TestTargetId"; // 按需填写实际的会话 id 

let list = new List<ConversationIdentifier>(); list.add(conId); 

RongIM.getInstance().conversationService().removeConversations(conIdList).then(result => { if (EngineError.Success !== result.code) { // 删除会话失败 return; } }); 

###### **参数说明** 

参数名 类型 详细说明 

conversationIds List 会话标识数组,会话标识包含会话类型与会话的 targetId 

###### 提示 

该方法仅从会话列表移除会话项目,但不会删除会话内的历史消息。如果会话内再来一条消息,该会话会重新出现在列 表中,且历史消息也会被加载。如果需要移除会话并删除会话内的消息,必须同时调用消息的 API,您需要同时删除本 地与远端的历史消息。详见删除消息。 

##### **按类型删除会话** 

从本地数据库中删除指定会话类型的所有会话,并删除这些会话内的消息。IMKit 未直接提供清除全部会话方法的 API。如果 您有类似以下自定义需求,可以调用 IMLib SDK 相关方法 删除会话。 

###### **多端同步免打扰 / 置顶** 

SDK 提供了会话状态(置顶或免打扰)同步机制,通过设置会话状态同步监听器,当在其它端修改会话状态时,可在本端实 时监听到会话状态的改变。 

##### **监听器说明** 

**RongIM** 中提供了 **ConversationListEventListener** 监听器。你可以设置/移除会话状态(置顶和免打扰)多端同步监 听器。 设置监听后,在会话的状态(置顶和免打扰)改变时,会触发以下方法: 

- 其它端修改会话的置顶和免打扰状态,数据同步后,SDK 会触发 ConversationListEventListener 的 onSyncConversationStatus 方法。 

- 181 - 

本端操作的修改置顶和免打扰状态,SDK会触发 ConversationListEventListener 的 onConversationTopStatusChange 方法。 

###### **接口原型** 

###### **TypeScript** 

interface ConversationListEventListener { /** * 当其他端修改会话的免打扰和置顶状态时 */ onSyncConversationStatus?: (items: List<ConversationStatusInfo>) => void; 

/** * 当本端修改会话的置顶状态时 */ 

onConversationTopStatusChange?: (identifierList: List<ConversationIdentifier>, option: ISetConversationTopOption) => void; } 

###### **参数说明** 

###### 方法返回 **ConversationStatusInfo** 的列表,参数如下: 

|参数|类型|描述|
|---|---|---|
|conversationType|**ConversationType**|会话类型。|
|targetId|String|会话ID。|
|updateTime|number|更新时间,毫秒时间戳。|
|isTop|boolean|会话是否被设置为置顶。|
|topTime|number|会话指定时间。|
|level|PushNotifcationLevel|会话的免打扰级别。具体级别说明详见**免打扰功能概述**。|

###### **ISetConversationTopOption** 参数 

|参数|类型|说明|
|---|---|---|
|isTop|boolean|是否置顶,true设置置顶;false取消置顶|
|isNeedCreate|boolean|是否创建会话:对应的会话本地不存在时,true将创建该会话;false不创建该会话|
|isNeedUpdateTime|boolean|是否更新会话时间,非必选,默认为true|

###### **示例代码** 

- 182 - 

###### **TypeScript** 

let conversationListEventListener: ConversationListEventListener = { 

onSyncConversationStatus: (items: List<ConversationStatusInfo>) => { 

//其他端同步会话置顶和免打扰状态 

for (let itemElement of items) { 

// 会话类型 

let conversationType: ConversationType = itemElement.conversationType 

// 会话 ID 

let targetId: string = itemElement.targetId 

// 更新时间,毫秒 

let updateTime: number = itemElement.updateTime 

// 置顶时间,毫秒 

let topTime: number = itemElement.topTime 

// 是否置顶 

let isTop: boolean = itemElement.isTop 

// 免打扰级别 

let 

} 

}, 

- //本端会话置顶和免打扰状态 

onConversationTopStatusChange: (conversationIds: List<ConversationIdentifier>, option: ISetConversationTopOption) => { 

for (let itemElement of conversationIds) { 

- // conversationIds 会话 id 标识列表 

- } 

// 是否置顶 

let isTop: boolean = option.isTop 

// 是否创建会话 

let isNeedCreate: boolean = option.isNeedCreate 

// 是否更新会话时间 

if (option.isNeedUpdateTime) { 

let isNeedUpdateTime: boolean = option.isNeedUpdateTime 

} 

- } 

} 

###### // 设置监听 

RongIM.getInstance().conversationListService().addConversationListEventListener(conversationListEventListen 

###### // 移除监听 

RongIM.getInstance().conversationListService().removeConversationListEventListener(conversationListEventLi 

###### 提示 

建议添加监听后,在合适的时机移除,避免内存泄露。如果在页面中监听,建议在 aboutToAppear 调用,在 

- 183 - 

aboutToDisappear 移除监听。 

###### **自定义会话列表 provider** 

##### **会话列表自定义会话展示模板** 

您可以自定义会话列表模板展示不同类型的会话。 

##### **编写自定义展示模版** 

您需要继承 BaseConversationItemProvider 自定义会话条目展示模版。 

**示例代码** 

###### **TypeScript** 

- 184 - 

import { BaseConversationItemProvider, BaseUiConversation } from "@rongcloud/imkit"; 

export class CustomPrivateConversationItemProvider extends BaseConversationItemProvider { public getConversationWrapBuilder(): WrappedBuilder<[Context, BaseUiConversation, number]> { return wrapBuilder(bindPrivateConversationMessageData) 

} 

} 

###### @Builder 

export function bindPrivateConversationMessageData(context: Context, baseConversation: BaseUiConversation, position: number) { 

CustomPrivateConversationItemView({ conversation: baseConversation }); 

} 

###### @Component 

export struct CustomPrivateConversationItemView { 

@ObjectLink conversation: BaseUiConversation; 

build() { 

this.CustomConversationItemComponent(this.conversation); 

} 

###### @Builder 

CustomConversationItemComponent(baseConversation: BaseUiConversation) { 

// 根据 baseConversation 来渲染UI,下面示范了添加会话头像和会话标题 

// 会话头像 

Image(this.baseConversation.getPortrait()).height(48).width(48) 

// 会话标题 

Text(this.baseConversation.getTitle()).fontColor("#C7CCD4").fontSize(16) 

- } } 

##### **绑定自定义会话列表模板** 

您可以设置 IMKit SDK 内置的指定会话类型的展示模版为您自定义的展示模板,需要在会话列表展示前设置。 

###### **TypeScript** 

let conversationListService = RongIM.getInstance().conversationListService() conversationListService.addConversationItemProvider(ConversationType.Private, new CustomPrivateConversationItemProvider()); 

##### **移除指定会话类型展示模版** 

- 185 - 

IMKit SDK 支持移除内置的指定会话类型的展示模版,需要在会话列表展示前设置。 

提示 

IMKit SDK 如果找不到这个会话类型的展示模版时,会默认返回私聊会话类型的展示模版。 

###### **TypeScript** 

let conversationListService = RongIM.getInstance().conversationListService() conversationListService.removeConversationItemProvider(ConversationType.Private); 

###### **会话列表自定义** 

##### **会话列表控制需要展示的会话类型** 

SDK 会话列表默认仅支持单聊和群聊两种会话。 

您可以通过 setSupportedTypes 传入对应的会话类型枚举来配置会话列表展示的会话类型,需要在会话列表展示前设置,最 多可以支持 单聊、群聊、系统会话。 

###### **示例代码** 

###### **TypeScript** 

// 读取会话列表当前的配置 

let config = RongIM.getInstance().conversationListService().getConversationListConfig() // 设置会话列表仅展示单聊 

config.setSupportedTypes([ConversationType.Private]) 

// 更新会话列表配置 RongIM.getInstance().conversationListService().setConversationListConfig(config) 

##### **会话列表组件自定义聚合展示** 

您可以通过为 ConversationListComponent 组件设置 dataProcessor 参数,实现更灵活的会话列表数据源管理。 

###### 提示 

从 1.7.2 版本开始支持。 

一旦使用该参数,将会覆盖前述通过 setSupportedTypes 配置的会话类型展示方式。 

###### **示例代码** 

- 186 - 

**TypeScript** 

###### // 仅展示单聊会话 

ConversationListComponent({dataProcessor: { 

supportedTypes: [ConversationType.Private] 

}}) 

###### // 仅展示群聊会话 

ConversationListComponent({dataProcessor: { 

supportedTypes: [ConversationType.Group] 

}}) 

- // 自定义聚合(以获取未读数不为 0 的会话列表为例) 

ConversationListComponent({dataProcessor: { 

onFetchConversationList: async (time: number) => { 

- // 自定义请求会话列表数据 

const cons = new List<ConversationType>() 

cons.add(ConversationType.Group) 

cons.add(ConversationType.Private) 

const list: List<Conversation> = new List<Conversation>() 

const res = await IMEngine.getInstance().getUnreadConversations(cons) 

if (res.code === EngineError.Success && res.data && res.data.length > 0) { 

res.data.forEach(item => { 

list.add(item) 

- }) 

options.time = res.data.getLast().lastOperateTime 

- } 

return list 

}, 

- // 设置会话数据过滤方法 

onConversationFilter: (item: Conversation) => { 

return item.unreadMessageCount > 0 

- } 

}}) 

##### **会话列表增加长按事件** 

您可以通过 addConversationItemLongClickActio 方法自行增加会话列表的长按事件: 

**示例代码** 

###### **TypeScript** 

- 187 - 

```arkts
private addConversationListLongClickAction() { let action: ItemLongClickAction<Conversation> = { // 显示标题 obtainTitle: (context: Context, data: Conversation): string | Resource => { return "自定义长按事件"; }, // 长按 item 的点击事件 onClick: (context: Context, data: Conversation) => { promptAction.showToast({ message: "会话列表自定义长按事件" }) }, // 过滤条件,true 代表需要显示,false 代表不会显示 onFilter: (data: Conversation): boolean => { // 可以动态配置特定的 Conversation 才显示该长按 item return true; }, actionId: 'Conversation_Custom' // 动作 Id,可自定义 } 
```

RongIM.getInstance().conversationListService().addConversationItemLongClickAction(action); } 

##### **会话列表头像圆角控制** 

您可以通过 setConversationAvatarStyle 方法修改会话列表头像圆角,会话列表头像默认为矩形,可以修改为圆形,不支 持动态切换矩形和圆形,必须在会话列表展示前设置: 

###### **示例代码** 

###### **TypeScript** 

// 读取会话列表当前的配置 

let config = RongIM.getInstance().conversationListService().getConversationListConfig() // 设置会话列表头像为圆角 config.setConversationAvatarStyle(AvatarStyle.Cycle) // 更新会话列表配置 RongIM.getInstance().conversationListService().setConversationListConfig(config) 

##### **会话列表点击事件** 

当您使用 ConversationListComponent 创建会话列表页面时,可以传入 onConversationItemClick 来处理点击事件。 SDK 默认未处理点击事件,如未设置 onConversationItemClick 则表现为点击无反应。 

提示 

- 188 - 

从 1.4.3 版本开始, 支持通过 addConversationListEventListener 设置会话列表点击事件,见会话列表事件。 但 需要注意,如果传入的 onConversationItemClick 不为空则不会再执行 ConversationListEventListener 的 onConversationClick 回调。 

###### **示例代码** 

###### **TypeScript** 

@Entry @Component export struct ChatListPage { 

build() { Column() { ConversationListComponent({ // 实现会话列表的点击事件 onConversationItemClick: this.onConversationItemClick 

}).layoutWeight(1) 

- }.width('100%').height('100%') } 

private onConversationItemClick(conversation: Conversation, index: number): void { 

// let params = new Conversation() 

// params.conversationType = ConversationType.Private 

// params.targetId = "会话 Id" 

// 参数必须是 Conversation 对象,必须有有效的 conversationType targetId router.pushUrl({ url: "pages/ChatPage", params: conversation },); } } 

##### **会话列表添加自定义空布局** 

IMKit 的 会话列表组件-Component 支持在会话列表中添加空(Empty)视图,您只需在构造 ConversationListComponent 时传入 emptyComponent 即可。 

###### **示例代码** 

###### **TypeScript** 

- 189 - 

@Entry @Component export struct ChatListPage { 

build() { Column() { ConversationListComponent({ // 实现没有会话的空白页面 emptyComponent: () => { this.emptyBuilder(); } }).layoutWeight(1) }.width('100%').height('100%') } @Builder emptyBuilder() { Text(`空白页面`).width('95%').fontColor("#FF0000").padding(10) } } 

##### **会话列表页面事件** 

IMKit 提供了会话列表事件监听器 ConversationListEventListener,可监听保存草稿、会话清除未读数、删除会话、本端 或者其他端修改会话的免打扰和置顶状态、点击会话、长按会话事件。 

您需要使用 RongIM 的 addConversationListEventListener 与 removeConversationListEventListener 方法添加或移 除监听器。 建议添加监听后,在合适的时机移除,避免内存泄露。如果在页面中监听,建议在aboutToAppear调用,在 aboutToDisappear 移除监听。 

提示 

从 1.4.3 版本开始,增加 onConversationLongClick 、 onConversationClick 方法。 

###### **接口原型** 

###### **TypeScript** 

export interface ConversationListEventListener { /** 

* 当某个会话内产生保存草稿的行为时 */ 

onSaveDraft?: (identifier: ConversationIdentifier, content: string) => void; 

/** 

- 190 - 

/ 

###### * 当某个会话清除未读数时 

*/ 

void; 

/** 

- 当批量删除某些会话时 

*/ 

void; 

/** 

- 当其他端修改会话的免打扰和置顶状态时 

*/ 

onSyncConversationStatus?: (items: List<ConversationStatusInfo>) => void; 

/** 

- 当本端修改会话的置顶状态时 

- */ 

onConversationTopStatusChange?: (identifierList: List<ConversationIdentifier>, option: ISetConversationTopOption) => void; 

/** 

- 当本端修改会话的免打扰状态时 

*/ 

onConversationNotificationLevelChange?: (identifierList: List<ConversationIdentifier>, level: PushNotificationLevel) => void; 

/** 

- 长按会话列表中的 item 时执行。 

- 

###### * @param uiConversation 长按时的会话条目。 

- @warning如果存在多个 Listener,只要有1个 Listener 实现了该方法且返回 true,SDK 则不再处理该事件。 

- @returns 是否处理该事件。实现该方法并且返回 true 代表 app 处理该点击事件,SDK 不再处理该点击事件。不实 现该方法或者返回 false,代表由 SDK 处理点击事件。 

- @version 1.4.3 

- */ 

onConversationLongClick?: (uiConversation: BaseUiConversation) => boolean; 

- /** 

- 点击会话列表中的 item 时执行。 

- 

###### * @param uiConversation 会话条目。 

- @warning优先执行 ConversationListComponent 传入的 onConversationItemClick ,没传则执行此接口逻辑。 

- @warning如果存在多个 Listener,只要有1个 Listener 实现了该方法且返回 true,SDK 则不再处理该事件。 

- @returns 是否处理该事件。实现该方法并且返回 true 代表 app 处理该点击事件,SDK 不再处理该点击事件。不实 现该方法或者返回 false,代表由 SDK 处理点击事件。 

- @version 1.4.3 

- 191 - 

@ e s o 3 

*/ 

onConversationClick?: (uiConversation: BaseUiConversation) => boolean; 

} 

###### **示例代码** 

###### **TypeScript** 

let service = RongIM.getInstance().conversationListService(); // 设置监听 service.addConversationListEventListener(conversationListEventListener) // 移除监听 service.removeConversationListEventListener(conversationListEventListener) 

##### **自定义会话列表 Item 扩展组件** 

您可以通过调用 setConversationItemComponentConfig 方法,为会话列表的每个 Item 组件灵活地添加自定义扩展内 容。 

提示 

从 1.7.2 版本开始支持。 

例如,若需为置顶的会话在右上角增加一个自定义图标,可参考以下示例代码: 

###### **TypeScript** 

- 192 - 

###### @Builder 

export function buildCustomConversationItemExtensionComponent(componentData: 

ConversationItemComponentData) { 

CustomConversationItemExtensionComponent({ 

context: componentData.context, 

conversation: componentData.conversation, 

- }) 

} 

@Component 

export struct CustomConversationItemExtensionComponent { 

- @Prop context: Context; 

- @Prop conversation: BaseUiConversation; 

build() { 

// 在会话右上角增加自定义置顶图标 

if (this.conversation.getConversation().isTop) { 

- // 您需要将 “app.media.con_top” 替换为您应用中的图片资源 

Image($r('app.media.con_top')).width(12).height(12).objectFit(ImageFit.Contain) 

.alignRules({ 

top: {anchor: '__container__', align: VerticalAlign.Top}, 

right: {anchor: '__container__', align: HorizontalAlign.End} }) } } } 

let ConversationItemComponent: ConversationItemComponentConfig = { 

identifier: ComponentIdentifier.ConversationItemExtensionComponent, component:wrapBuilder(buildCustomConversationItemExtensionComponent), } 

RongIM.getInstance().conversationListService().setConversationItemComponentConfig(ConversationItemComp 

###### **资源自定义** 

IMKit SDK 允许您通过自定义和替换内置的资源文件,灵活调整颜色和图片样式,以满足应用的个性化视觉需求。 

##### **自定义颜色** 

如需修改 IMKit SDK 的默认颜色,您只需在应用的 entry/src/main/resources/base/element/color.json 文件中,添加与 

- 193 - 

SDK 内置颜色资源同名的配置项,即可覆盖默认颜色。 

###### 目前支持覆盖的颜色资源如下: 

|资源名称|说明|支持版本|
|---|---|---|
|rc_color_voice_message_sent_text|语音消息(发送方)文字颜色|1.7.2+|
|rc_color_voice_message_received_text|语音消息(接收方)文字颜色|1.7.2+|
|rc_color_conversation_top|置顶会话背景颜色|1.7.2+|

##### **自定义图片** 

如需替换 IMKit SDK 的默认图片,您只需在应用的 entry/src/main/resources/base/media 目录下,添加与 SDK 内置图 片资源同名的文件,即可完成覆盖,无需修改任何代码。 

###### 目前支持覆盖的图片资源如下: 

|资源名称|说明||支持版本|
|---|---|---|---|
|rc_conversation_mute.png|会话免打扰图标||1.7.2+|
|rc_to_voice_1.png|语音消息(发送方)|播放图标1|1.7.2+|
|rc_to_voice_2.png|语音消息(发送方)|播放图标2|1.7.2+|
|rc_to_voice_3.png|语音消息(发送方)|播放图标3|1.7.2+|
|rc_from_voice_1.png|语音消息(接收方)|播放图标1|1.7.2+|
|rc_from_voice_2.png|语音消息(接收方)|播放图标2|1.7.2+|
|rc_from_voice_3.png|语音消息(接收方)|播放图标3|1.7.2+|

###### **会话页面自定义** 

##### **消息点击事件** 

为了避免内存泄露,请将监听保存,在必要的时候移除 

您可以通过调用 addMessageClickListener 方法监听消息的点击事件,消息点击监听 MessageClickListener 的所有方法 均为可选方法,可以按需实现,此处为了方便展示,将所有方法都做了默认实现。 

提示 

从 1.4.3 版本开始, onMessageClick 支持语音消息。 

从 1.4.3 版本开始,所有方法均增加 Context 、 ClickEvent/GestureEvent 参数。 

- 194 - 

**示例代码** 

###### **TypeScript** 

- 195 - 

let msgClickListener : MessageClickListener = { 

onMessagePortraitClick: (message: Message, userId: string, context?: Context, event?: ClickEvent) => { 

- // 消息头像点击事件 

- // true 由 App 处理该事件,SDK 不再处理。false 由 SDK 处理 

return false; 

}, 

onMessagePortraitLongClick: (message: Message, user: UserInfoModel, context?: Context, event?: 

GestureEvent) => { 

- // 消息头像长按事件 

- // true 由 App 处理该事件,SDK 不再处理。false 由 SDK 处理 return false; 

- }, 

onMessageClick: (message: Message, context?: Context, event?: ClickEvent) => { 

- // 消息点击事件 

- // true 由 App 处理该事件,SDK 不再处理。false 由 SDK 处理 return false; 

- }, 

onMessageLongClick: (message: Message, context?: Context, event?: GestureEvent) => { 

- // 消息长按事件 

- // true 由 App 处理该事件,SDK 不再处理。false 由 SDK 处理 return false; 

}, 

onMessageRecallEditClick: (message: Message, context?: Context, event?: ClickEvent) => { 

- // 消息撤回编辑事件 

- // true 由 App 处理该事件,SDK 不再处理。false 由 SDK 处理 return false; 

}, 

onMessageLinkClick: (message: Message, url: string, context?: Context, event?: ClickEvent) => { 

- // 文本消息超链接点击事件 

- // true 由 App 处理该事件,SDK 不再处理。false 由 SDK 处理 return false; 

}, 

onMessageEmailClick: (message: Message, email: string, context?: Context, event?: ClickEvent) => { 

- // 文本消息 email 点击事件 

- // true 由 App 处理该事件,SDK 不再处理。false 由 SDK 处理 return false; 

}, 

onMessagePhoneClick: (message: Message, phone: string, context?: Context, event?: ClickEvent) => { 

- // 文本消息手机号点击事件 

- // true 由 App 处理该事件,SDK 不再处理。false 由 SDK 处理 

return false; 

}, 

} 

RongIM.getInstance().conversationService().addMessageClickListener(msgClickListener); 

- 196 - 

##### **增加消息气泡的长按事件** 

您可以通过 addMessageItemLongClickAction 方法设置会话页面的长按消息事件监听,在相关监听方法中自定义事件: 

###### **示例代码** 

###### **TypeScript** 

```arkts
let msgLongClickAction :ItemLongClickAction<Message> = { obtainTitle: (context: Context, data: Message): string | Resource => { return "自定义的消息长按事件" }, onClick: (context: Context, data: Message): void => { promptAction.showToast({message : "点击了自定义的消息长按事件"}) }, onFilter: (data: Message): boolean => { // 是否显示该长按事件?true 显示;false 不显示 // 开发者可以根据 Message 对象的会话类型或者消息类型决定是否显示 return true; }, // 自定义的消息长按事件 Id,相同的 Id 的长按事件只会增加一次 actionId: 'CustomMessageActionId' } RongIM.getInstance().conversationService().addMessageItemLongClickAction(msgLongClickAction); 
```

###### **参数说明** 

ItemLongClickAction 类属性如下表所示。 

|属性|类型|描述|
|---|---|---|
|obtainTitle|string|显示名称。|
|onClick|(context: Context, data: Message):|长按消息监听函数。|
||void||
|onFilter|int|控制是否会被显示出来的过滤器。|
|actionId|Filter|自定义的消息长按事件Id,相同的Id的长按事件只会增加一次|

##### **配置消息气泡的长按更多选项** 

在长按消息弹窗的菜单选项选择 **更多** 后,SDK 进入消息多选模式,多选模式下默认提供了删除按钮。您可以增删已有按钮、 添加自定义按钮。 

IMKit SDK没有内置消息转发功能,实现可以参照:转发消息实现。 

- 197 - 

**示例代码** 

###### **TypeScript** 

let msgMoreAction : MessageMoreAction = { 

actionId: 'message_more_forward',// 动作 Id 

location: 100, // 按钮将放置在底部,根据 location 值,按照从小到大的顺序依次向右排列。 icon: $r("app.media.rc_message_more_forward"), // 图标 

onClick: (context: Context, data: Message[]): boolean => { // 处理自定义的点击事件 // return true :聊天页面依旧处于多选状态 // return false : 聊天页面退出多选状态 promptAction.showToast({message : "点击了聊天页面底部的更多按钮"}); return true }, onFilter: (data: Message[]): boolean => { // 是否显示该按钮,true 显示,false 不显示 return true; } } RongIM.getInstance().conversationService().addMessageMoreAction(msgMoreAction) 

##### **修改消息气泡的 UI 配置** 

IMKit 从 1.4.3 版本开始支持通过 setConversationConfig 方法传入对应的 ConversationConfig 对象修改消息气泡的 UI 配置。支持设置的属性:边框圆角大小、边框色、背景色。 

提示 

仅支持初始化前的配置,若初始化后开发者设置,则不会生效。 

##### **修改边框圆角大小** 

边框圆角大小支持按消息方向来设置: 

- 设置/获取接收的消息气泡边框圆角大 

- 小: setReceivedMessageBorderRadius 、 getReceivedMessageBorderRadius 。 

- 设置/获取发送的消息气泡边框圆角大小: setSentMessageBorderRadius 、 getSentMessageBorderRadius 。 

###### **示例代码** 

###### **TypeScript** 

- 198 - 

let config = RongIM.getInstance().conversationService().getConversationConfig(); let receivedMessageBorderRadius: BorderRadiuses = { 

topLeft: 4, topRight: 8, bottomLeft: 8, bottomRight: 8 } config.setReceivedMessageBorderRadius(receivedMessageBorderRadius); RongIM.getInstance().conversationService().setConversationConfig(config); 

##### **修改边框色** 

边框色支持按消息方向来设置: 

   - 设置/获取接收的消息气泡边框色: setReceivedMessageBorderColor 、 getReceivedMessageBorderColor 。 

   - 设置/获取发送的消息气泡边框色: setSentMessageBorderColor 、 getSentMessageBorderColor 。 

1. 通过指定消息的 objectName 仅修改文本消息类型的边框色为灰色,其他消息类型不修改。 

###### **示例代码** 

###### **TypeScript** 

```arkts
let config = RongIM.getInstance().conversationService().getConversationConfig(); config.setReceivedMessageBorderColor("RC:TxtMsg", Color.Gray); RongIM.getInstance().conversationService().setConversationConfig(config); 
```

2. 修改全部消息类型的边框色为灰色。 

###### **示例代码** 

###### **TypeScript** 

```arkts
let config = RongIM.getInstance().conversationService().getConversationConfig(); config.setReceivedMessageBorderColor("", Color.Gray); RongIM.getInstance().conversationService().setConversationConfig(config); 
```

3. 通过指定消息的 objectName 仅修改文本消息类型的边框色为灰色,同时修改其余消息类型的边框色为蓝色,与接口调 用顺序无关。 

###### **示例代码** 

###### **TypeScript** 

- 199 - 

let config = RongIM.getInstance().conversationService().getConversationConfig(); config.setReceivedMessageBorderColor("RC:TxtMsg", Color.Gray); 

config.setReceivedMessageBorderColor("", Color.Blue); RongIM.getInstance().conversationService().setConversationConfig(config); 

##### **修改背景色** 

背景色支持按消息方向来设置: 

###### 设置/获取接收的消息气泡背景 

- 色: setReceivedMessageBackgroundColor 、 getReceivedMessageBackgroundColor 。 

设置/获取发送的消息气泡背景色: setSentMessageBackgroundColor、 getSentMessageBackgroundColor 。 

1. 通过指定消息的 objectName 仅修改文本消息类型的背景色为灰色,其他消息类型不修改。 

###### **示例代码** 

###### **TypeScript** 

```arkts
let config = RongIM.getInstance().conversationService().getConversationConfig(); config.setReceivedMessageBackgroundColor("RC:TxtMsg", Color.Gray); RongIM.getInstance().conversationService().setConversationConfig(config); 
```

###### 2. 修改全部消息类型的背景色为灰色。 

###### **示例代码** 

###### **TypeScript** 

```arkts
let config = RongIM.getInstance().conversationService().getConversationConfig(); config.setReceivedMessageBackgroundColor("", Color.Gray); RongIM.getInstance().conversationService().setConversationConfig(config); 
```

3. 通过指定消息的 objectName 仅修改文本消息类型的背景色为灰色,同时修改其余消息类型的背景色为蓝色,,与接口 调用顺序无关。 

###### **示例代码** 

###### **TypeScript** 

```arkts
let config = RongIM.getInstance().conversationService().getConversationConfig(); config.setReceivedMessageBackgroundColor("RC:TxtMsg", Color.Gray); config.setReceivedMessageBackgroundColor("", Color.Blue); RongIM.getInstance().conversationService().setConversationConfig(config); 
```

- 200 - 

##### **自定义输入框按钮 UI** 

从 1.5.1 版本开始,IMKit 默认允许配置会话页面输入框的一些UI组件。可通过 

setInputAreaComponentConfig(InputAreaComponentConfig) 接口设置自定义组件配置。 

###### **TypeScript** 

export interface InputAreaComponentConfig { /** 

* 组件标识 */ identifier: ComponentIdentifier, /** 

组件WrappedBuilder @since 1.6.0 

component: WrappedBuilder<[InputAreaComponentData]> | null, } /** 

* 输入区域自定义组件数据,封装必要的参数透传给自定义组件 * @since 1.6.0 */ export class InputAreaComponentData { /** * 上下文 */ context: Context | undefined; /** * 会话标识 */ convId: ConversationIdentifier | undefined; /** * 透传参数 * 

* 当 `identifier` 为某些枚举类型的情况下有值,其余情况下为空。详细说明如下 *  1. ComponentIdentifier.InputBarVoiceButton: "Voice" 语音类型、 "Text" 文本类型。 *  2. ComponentIdentifier.InputBarEmoticonButton: "Emoticon" 表情类型、 "Text" 文本类型。 *  3. ComponentIdentifier.DestructBarVoiceButton: "Voice" 语音类型、 "Text" 文本类型。 *``` */ data: string = ""; } 

- 201 - 

identifier 支持的组件类型说明: 

|组件类型|说明|
|---|---|
|InputBarVoiceButton|输入框左侧语音按钮|
|InputBarEmoticonButton|输入框表情按钮|
|InputBarSendButton|输入框发送按钮|
|InputBarPluginButton|输入框插件加号按钮|
|InputBarExpandTextAreaButton|文本输入组件输入了大于2行文本时,输入框左侧的展开输入按钮|
|EmoticonBoardAddButton|表情面板左下角的添加按钮|

###### **TypeScript** 

- 202 - 

###### // 设置接口 

let InputBarPluginButton: InputAreaComponentConfig = { 

identifier: ComponentIdentifier.InputBarPluginButton, component: wrapBuilder(buildCustomInputBarPluginView), 

} 

RongIM.getInstance().conversationService().setInputAreaComponentConfig(InputBarPluginButton) 

###### // 组件 

@Builder 

export function buildCustomInputBarPluginView(componentData: InputAreaComponentData) { 

CustomInputBarPluginView({ context: componentData.context, convId: componentData.convId, type: componentData.data }) 

} 

@Component 

export struct CustomInputBarPluginView { 

@Prop context: Context; 

@Prop convId: ConversationIdentifier; 

@Prop type: string; 

aboutToAppear(): void { 

console.log("CustomInputBarPluginView  aboutToAppear " + this.type) 

} 

build() { 

Image($r('app.media.default_fmessage')) 

.size({ width: 30, height: 30 }) 

.onTouch(() => { 

promptAction.showToast({ message: `点击了按钮` }) }) } } 

##### **自定义会话页面按钮 UI** 

###### 从 1.6.0 版本开始,IMKit 默认允许配置会话页面的一些UI组件。可通过 

setConversationContentComponentConfig(ConversationContentComponentConfig) 接口设置自定义组件配置。 

ConversationContentComponentConfig 相关接口说明: 

###### **TypeScript** 

export interface ConversationContentComponentConfig { /** 

* 组件标识 

- 203 - 

件标识 

* 

*``` 

* 注意: 

- ConversationContentComponentConfig 支持的类型: 

- - ConversationUnreadMessageButton; 

- - ConversationUnreadMentionedMessageButton; 

- - ConversationNewReceivedUnreadMessageButton 

*``` 

*/ 

identifier: ComponentIdentifier, 

/** 

- 组件WrappedBuilder。 

*/ 

component: WrappedBuilder<[ConversationContentComponentData]> | null, 

} 

###### // 会话自定义组件数据 

export class ConversationContentComponentData { 

/** 

* 上下文 */ 

context: Context | undefined; 

/** 

- 会话标识 

*/ 

convId: ConversationIdentifier | undefined; 

/** 

- 透传参数 

* 

*``` 

- 与 `ConversationContentComponentConfig` 的 identifier` 参数具备对应关系,使用说明如下: 

- 1. 当 `identifier` 是 ConversationNewReceivedUnreadMessageButton, 代表在会话中新收到的未读消息的数 量; 

- 2. 当 `identifier` 是 ConversationUnreadMessageButton, 代表会话中的未读消息数量; 

- 3. 当 `identifier` 是 ConversationUnreadMentionedMessageButton, 代表当前@自己的未读消息的数量; *``` 

*/ 

data: number = 0; /** 

- 会话页面ViewModel,用来执行后续的事件 

* 

*``` 

- 与 `ConversationContentComponentConfig` 的 identifier` 参数具备对应关系,使用说明如下: 

- 1. 当 `identifier` 是 ConversationNewReceivedUnreadMessageButton, 调用 

- 204 - 

- `onClickNewReceivedUnreadMessageButton` 执行新收到未读消息的点击事件; 

- 2. 当 `identifier` 是 ConversationUnreadMessageButton,调用 `onClickUnreadMessageButton` 执行未读 消息的点击事件; 

- 3. 当 `identifier` 是 ConversationUnreadMentionedMessageButton, 调用 

- `onClickUnreadMentionedMessageButton` 执行未读@我的消息的点击事件; 

*``` 

* 

*/ 

conversationViewModel: IConversationViewModel | undefined 

} 

###### // ConversationViewModel的能力接口 

export interface IConversationViewModel { /** 

- 进入会话时展示的未读消息的组件点击事件 

*/ 

onClickUnreadMessageButton(): void; 

/** 

- 进入会话时展示的未读@我的消息的组件点击事件 

- */ 

onClickUnreadMentionedMessageButton(): void; 

/** 

- 在进入会话后收到未读新消息的组件点击事件 

*/ 

onClickNewReceivedUnreadMessageButton(): void; /** 

- 获取输入框当前的文本输入组件的内容 

- @since 1.7.1 

*/ 

getInputTextAreaContent?():string; 

/** 

- 获取消息列表 

* 

- 注意:改返回列表仅用于读取,不建议修改。 

* 

- @returns 消息列表 

- @since 1.7.1 

*/ 

getMessageList?(): UiMessage[]; 

/** 

- 刷新某条消息 

- @since 1.7.1 

*/ 

refreshUiMessage?(message: Message): void; } 

- 205 - 

以下展示了进入会话后收到未读新消息的组件的自定义示例: 

1. 使用 alignRules 控制在屏幕中的位置。 

2. 使用 ConversationContentComponentData#data 观察未读消息数,具体描述见注释。 

3. 使用 ConversationContentComponentData#conversationViewModel 暴露会话页面能力,用来开发者处理点击 事件,具体描述见注释。 

###### **TypeScript** 

###### @Builder 

export function buildCustomConversationTopUnreadMessageButton(data: ConversationContentComponentDat CustomConversationTopUnreadMessageButton({ context: data.context, convId: data.convId, unreadMessage data.data, viewModel:data.conversationViewModel }) 

} 

@Component 

export struct CustomConversationTopUnreadMessageButton { 

@Prop context: Context; 

- @Prop convId: ConversationIdentifier; 

@Prop unreadMessageCount: number; 

@Prop viewModel: IConversationViewModel; 

build() { 

if (this.unreadMessageCount > 10) { 

Row() { 

Image($r('app.media.rc_arrow')).width(12).height(9).objectFit(ImageFit.Contain) 

Text((this.unreadMessageCount > 99 ? "99+" : this.unreadMessageCount) + "条新消息") .fontSize(14) 

.fontColor($r('app.color.rc_color_111F2C')) 

.margin({ left: 6 }) } .borderRadius({ topLeft: 24, bottomLeft: 24 }) 

.height(48) .padding({ left: 10, right: 10 }) .backgroundColor($r('app.color.rc_color_FFFFFF')) .alignRules({ center: { anchor: "__container__", align: VerticalAlign.Center }, right: { anchor: "__container__", align: HorizontalAlign.End } }) .margin({ top: 14 }) .onClick(() => { this.viewModel.onClickUnreadMessageButton() }) } 

- 206 - 

} 

} 

###### // 设置UI组件 

let ConversationUnreadMessageButton: ConversationContentComponentConfig = { 

identifier: ComponentIdentifier.ConversationUnreadMessageButton, 

component: wrapBuilder(buildCustomConversationTopUnreadMessageButton), } 

RongIM.getInstance().conversationService().setConversationContentComponentConfig(ConversationUnreadMe 

###### 进入会话后收到未读新消息的组件、顶部未读@我的消息的组件设置如下 

###### **TypeScript** 

###### // 自定义收到新的未读消息的UI组件 

let ConversationNewReceivedUnreadMessageButton: ConversationContentComponentConfig = { identifier: ComponentIdentifier.ConversationNewReceivedUnreadMessageButton, 

component: wrapBuilder(buildCustomConversationBottomUnreadMessageButton), } 

RongIM.getInstance().conversationService().setConversationContentComponentConfig(ConversationNewRecei 

###### // 自定义顶部未读@我的消息的UI组件 

let ConversationUnreadMentionedMessageButton: ConversationContentComponentConfig = { 

identifier: ComponentIdentifier.ConversationUnreadMentionedMessageButton, 

component: wrapBuilder(buildCustomConversationTopUnreadMentionedMessageButton), } 

RongIM.getInstance().conversationService().setConversationContentComponentConfig(ConversationUnreadMe 

##### **增加 + 号扩展栏插件** 

##### **内置插件说明** 

IMKit 内置插件列表如下所示。其中位置插件 SDK 仅定义,实际需要 App 侧来实现。 

|插件|插件名称|说明|
|---|---|---|
|图片插件|ImagePlugin|ImagePluginName "RC:ImagePlugin"|
|小视频插件|CameraPlugin|CameraPluginName "RC:CameraPlugin"|
|文件插件|FilePlugin|FilePluginName "RC:FilePlugin"|
|阅后即焚插件|DestructPlugin|DestructPluginName "RC:DestructPlugin"|
|位置插件|LocationPlugin|LocationPluginName "RC:LocationPlugin"|

- 207 - 

**实现自定义插件** 

###### **TypeScript** 

```arkts
import { IBoardPlugin } from '@rongcloud/imkit'; import { ConversationIdentifier } from '@rongcloud/imlib'; import { promptAction } from '@kit.ArkUI'; 
```

/** 

* 自定义插件 */ export class CustomInfoMessagePlugin implements IBoardPlugin { 

/** 

- 插件名,用来判断插件唯一标识。如果不设置则无法查找、替换操作 

- @returns 插件名 

- @version 1.4.3 新增 

*/ pluginName(): string { return "CustomInfoMessagePlugin" } 

/** 

- 返回插件的标题 

* @param context 上下文 

* @returns 标题 

*/ 

obtainTitle(context: Context): string | Resource { return "自定义小灰条消息" } 

/** 

- 返回插件的图片 

- @param context 上下文 

- @returns 图片 

*/ obtainImage(context: Context): Resource { return $r("app.media.startIcon"); 

} 

/** 

- 插件的点击事件 

- @param context 上下文 

*/ onClick(context: Context, conId: ConversationIdentifier): void { 

- 208 - 

if (!conId) { 

return; 

// 处理具体的点击事件 // 开发者按照实际情况处理 

promptAction.showToast({ message: '点击了自定义插件' }) 

} /** 

是否在会话中显示该插件 

- @param conId 会话标识 

- @returns 是否显示,true 显示;false 不显示 

onFilter boolean { 

return true; } } 

##### **自定义插件 UI** 

从 1.5.1 版本开始,IMKit 默认允许配置插件的UI组件。可以根据插件名替换自定义插件的UI,如果想替换SDK内置的插件 UI,插件名参照内置插件说明。 

###### **TypeScript** 

- 209 - 

###### @Builder 

export function buildCustomMessagePluginView(context: Context, convId: ConversationIdentifier) { CustomMessagePluginView({ context: context, convId: convId }) 

} 

@Component 

export struct CustomMessagePluginView { 

- @Prop context: Context; 

- @Prop convId: ConversationIdentifier; 

build() { 

Column() { 

Text("自定义插件名").width("100%").fontSize(12).textAlign(TextAlign.Center) 

Image($r("app.media.rc_file_apk_icon")).width(40).height(40) 

}.width("100%").height("100%") 

.justifyContent(FlexAlign.SpaceEvenly).alignItems(HorizontalAlign.Center) 

} 

} 

###### // 替换自定义插件的UI组件 

RongIM.getInstance().conversationService().setBoardPluginView("CustomInfoMessagePlugin", wrapBuilder(buildCustomMessagePluginView)) 

##### **将插件放到扩展栏里面** 

需要在聊天页面出现前调用 

###### **添加插件** 

###### **TypeScript** 

let customInfoMessagePlugin = new CustomInfoMessagePlugin(); RongIM.getInstance().conversationService().addBoardPlugin(customInfoMessagePlugin); 

###### **将插件放到指定位置** 

###### 提示 

1.4.3 版本起,如果想调整 SDK 默认展示的插件以及插件的顺序,需要通过 动态配置扩展面板插件 功能配置。 

###### **TypeScript** 

- 210 - 

let index : number = 0 

let customInfoMessagePlugin = new CustomInfoMessagePlugin(); 

RongIM.getInstance().conversationService().insertBoardPlugin(index, customInfoMessagePlugin); 

###### **替换指定位置的插件,如果没有对应的索引,会将插件放到最后** 

###### 提示 

1.4.3 版本起,如果想调整 SDK 默认展示的插件以及插件的顺序,需要通过动态配置扩展面板插件 功能配置。 

###### **TypeScript** 

let index : number = 0 

let customInfoMessagePlugin = new CustomInfoMessagePlugin(); RongIM.getInstance().conversationService().replaceBoardPlugin(index, customInfoMessagePlugin); 

###### **移除特定的插件** 

###### 提示 

1.4.3 版本起,如果想调整 SDK 默认展示的插件以及插件的顺序,需要通过 动态配置扩展面板插件 功能配置 

###### **TypeScript** 

let customInfoMessagePlugin = new CustomInfoMessagePlugin(); RongIM.getInstance().conversationService().removeBoardPlugin(customInfoMessagePlugin); 

###### **根据插件名移除特定的插件** 

1. 自定义插件实现 pluginName() 接口返回插件名,便可以通过 removeBoardPluginByName 来移除插件。 

2. 系统插件均实现了 pluginName() ,可以参照上面表格中插件对应的名字,通过 removeBoardPluginByName 来移 除插件。 

###### **TypeScript** 

RongIM.getInstance().conversationService().removeBoardPluginByName("插件名"); 

###### **清空当前的插件。** 

###### 提示 

该接口只能清空通过 addBoardPlugin、insertBoardPlugin、replaceBoardPlugin 添加的插件。通过动态配置扩 展面板插件可以做到彻底清空。 

###### **TypeScript** 

- 211 - 

RongIM.getInstance().conversationService().clearBoardPlugin(); 

##### **动态配置扩展面板插件** 

如果应用程序需要动态添加、删除扩展面板插件,或者调整插件位置,建议通过创建自定义的扩展面板配置实现这些自定义需 求。 

您需要实现 IExtensionConfig,创建自定义的扩展面板配置类,重写 getPluginModules() 方法。您可以增加或删除扩展 项,也可以调整各插件的位置。 在 SDK 初始化之后,调用 setExtensionConfig 方法设置好自定义的输入配置,SDK 会根 据此配置展示扩展面板。 

###### **示例代码** 

###### **TypeScript** 

###### // 获取当前的插件配置 

let config = RongIM.getInstance().conversationService().getExtensionConfig() 

let mCustomExtensionConfig: IExtensionConfig = { 

getPluginModules: (convId: ConversationIdentifier) => { 

- // 根据插件配置获取对应会话标识的插件 

let currentPlugins = 

config.getPluginModules(ConversationIdentifier.createWith2(ConversationType.Private, "TargetID")) let plugins: ArrayList<IBoardPlugin> = new ArrayList<IBoardPlugin>() 

- // 这里示范了去除文件插件的操作。当然也可以根据 pluginName 来重新排序插件等操作。 for (let plugin of currentPlugins) { 

if (plugin.pluginName && plugin.pluginName() !== FilePluginName) { 

plugins.add(plugin) 

- } 

- } 

- // 添加业务侧自定义的插件 

plugins.add(new TestPlugin1()) plugins.add(new TestPlugin2()) return plugins } 

} 

/// 在 SDK 初始化之后调用 

RongIM.getInstance().conversationService().setExtensionConfig(mCustomExtensionConfig) 

##### **消息头像圆角控制** 

您可以通过全局配置控制消息头像圆角展示,需要在会话页面展示前设置。 

**示例代码** 

- 212 - 

###### **TypeScript** 

let config = RongIM.getInstance().conversationService().getConversationConfig(); config.setMessageAvatarStyle(AvatarStyle.Cycle); 

RongIM.getInstance().conversationService().setConversationConfig(config); 

##### **修改消息可撤回的最大时间** 

IMKit 默认允许在消息发送后 180 秒内撤回。您可以通过全局配置调整该上限,需要在会话页面展示前设置。 

###### **示例代码** 

###### **TypeScript** 

let config = RongIM.getInstance().conversationService().getConversationConfig() config.setMaxRecallDuration(180) RongIM.getInstance().conversationService().setConversationConfig(config) 

##### **修改撤回后可重新编辑的时间** 

IMKit 默认允许在消息撤回后 30 秒内可点击 **重新编辑** ,仅文本消息支持撤回再编辑。您可以通过全局配置调整该上限,需要 在会话页面展示前设置。 

###### **示例代码** 

###### **TypeScript** 

let config = RongIM.getInstance().conversationService().getConversationConfig() config.setMaxEditableDuration(30) RongIM.getInstance().conversationService().setConversationConfig(config) 

##### **文本消息字体高亮颜色** 

IMKit 默认允许配置 SDK 内置文本消息中的 url、手机号、@ 信息等高亮字体颜色,默认黑色。您可以通过全局配置调整, 需要在会话页面展示前设置。 

###### **示例代码** 

###### **TypeScript** 

let config = RongIM.getInstance().conversationService().getConversationConfig() config.setStyleFontColor(Color.Blue) 

RongIM.getInstance().conversationService().setConversationConfig(config) 

##### **文本和引用消息内容自定义渲染** 

- 213 - 

从 1.6.0 版本开始,IMKit 默认允许配置 SDK 内置文本、引用消息的文本内容渲染拦截事件接口。您可以通过全局配置调 整,需要在会话页面展示前设置。 

该接口如果返回 true ,那么文本消息字体高亮颜色则不会生效。 

###### **TypeScript** 

```arkts
let config = RongIM.getInstance().conversationService().getConversationConfig() let interceptor = (controller: TextController, content: string) => { if ("不需要拦截的场景") { return false } let styledString: MutableStyledString = new MutableStyledString(content) // 内容匹配到regContent则变成红色高亮 let regContent = "融云" let matches = content.matchAll(new RegExp(regContent, 'g')); // 是否匹配到内容 let hasMatch = false for (let match of matches) { hasMatch = true const index = match.index if (index != undefined) { styledString.setStyle({ start: index, length: regContent.length, styledKey: StyledStringKey.FONT, styledValue: new TextStyle({ fontColor: Color.Red }) }) } } controller.setStyledString(styledString) return true } config.setMessageRenderTextInterceptor(interceptor) RongIM.getInstance().conversationService().setConversationConfig(config) 
```

##### **设置文件消息的文件类型图标** 

IMKit 默认允许配置 SDK 内置文件消息的文件类型图标。您可以通过全局配置调整,需要在会话页面展示前设置。 

##### **设置文件消息的文件类型图标** 

您可以通过 setFileMessageIcons 覆盖默认的文件消息的文件类型图标。 

**示例代码** 

- 214 - 

###### **TypeScript** 

let config = RongIM.getInstance().conversationService().getConversationConfig() //设置图片 

let iconsMap: Map<string, Resource> = new Map<string, Resource>(); //覆盖SDK默认图片 

iconsMap.set('doc', $r("app.media.doc_icon")); iconsMap.set('mp3', $r("app.media.mp3_icon")); iconsMap.set('pdf', $r("app.media.pdf_icon")); iconsMap.set('rmvb', $r("app.media.rmvb_icon")); iconsMap.set('default', $r("app.media.rc_default_icon")); config.setFileMessageIcons(iconsMap); RongIM.getInstance().conversationService().setConversationConfig(config) 

##### **获取文件消息内的文件类型图标 map** 

您可以通过 getFileMessageIcons 获取文件消息内的文件类型图标 map。 

###### **示例代码** 

###### **TypeScript** 

let config = RongIM.getInstance().conversationService().getConversationConfig() config.getFileMessageIcons(); 

可以通过 getFileMessageIcon 获取文件消息内的文件类型图标,如果找不到,返回 SDK 内置的默认图标。 

###### **TypeScript** 

let config = RongIM.getInstance().conversationService().getConversationConfig() config.getFileMessageIcon('doc'); 

##### **修改消息重发开关** 

IMKit 从 1.4.3 版本开始支持消息发送失败时自动消息重发。 

###### 提示 

为了跟 iOS、Android 端现有逻辑保持一致,该配置默认值为为 true。 

从 1.4.3 以下版本升级的客户,会改变默认行为,如果不想消息重发,需要主动设置为 false。 

###### **TypeScript** 

- 215 - 

let config = RongIM.getInstance().conversationService().getConversationConfig() config.setEnableResendMessage(false) 

RongIM.getInstance().conversationService().setConversationConfig(config) 

##### **群消息回执配置** 

IMKit 从 1.7.1 版本开始支持群消息回执支持配置每条消息都显示已读未读信息。该配置默认为false。 

###### **TypeScript** 

let config = RongIM.getInstance().conversationService().getConversationConfig() config.setEnableShowAllGroupReceipt(true) RongIM.getInstance().conversationService().setConversationConfig(config) 

##### **引用消息点击跳转行为配置** 

从 1.6.0 版本开始,IMKit 默认允许配置 SDK 内置引用消息的引用消息点击跳转行为。您可以通过全局配置调整,需要在会 话页面展示前设置。 

SDK 配置默认为 JumpToDetailPage。 

###### **TypeScript** 

let config = RongIM.getInstance().conversationService().getConversationConfig() config.setReferencedMessageClickType(ReferencedMessageClickType.ScrollToReferencedMessage) RongIM.getInstance().conversationService().setConversationConfig(config) 

ReferencedMessageClickType 说明 

###### **TypeScript** 

###### // 引用消息的被引用消息体点击后的处理方式 

export enum ReferencedMessageClickType { 

/** 

- 跳转到预览页面。 

*/ JumpToDetailPage, /** 

- 滚动到被引用消息,如果被引用消息在本地数据库中不存在,则不会进行跳转,并提示"未找到被引用消息" */ 

ScrollToReferencedMessage } 

##### **会话页面事件** 

- 216 - 

IMKit 提供了会话页面事件监听器 ConversationEventListener,可监听会话页面中输入 @ 时跳转用户列表选择用户事件、 当输入状态变化时的事件。需要在会话页面展示前设置。 

###### **示例代码** 

###### **TypeScript** 

import { ConversationEventListener } from '@rongcloud/imkit'; 

export interface ConversationEventListener { /** * 输入@时,跳转用户列表选择用户 * @param select 选中的用户信息 */ onInputMention?: (select: (user: UserInfoModel) => void) => void; /** * 当输入状态变化时 * @param isEditing */ onEditChange?: (isEditing: boolean) => void; } 

##### **设置 / 移除会话页面事件监听** 

您可以使用 RongIM 的 addConversationEventListener、removeConversationEventListener 方法添加或者监听器。 

建议添加监听后,在合适的时机移除,避免内存泄露。如果在页面中监听,建议在 aboutToAppear 调用,在 aboutToDisappear 移除监听。 

###### **示例代码** 

###### **TypeScript** 

###### // 添加监听器 

RongIM.getInstance().conversationService().addConversationEventListener(listener); // 移除监听器 RongIM.getInstance().conversationService().removeConversationEventListener(listener); 

##### **输入 @ 时跳转页面并返回数据** 

当会话页面输入框输入 @ 时,会触发以下方法。如果未设置,SDK 默认不处理该事件。 

处理流程: 

- 217 - 

1. 收到 onInputMention 时跳转到用户列表页面选择用户; 

2. 返回到当前页面后,调用 select 回传 UserInfoModel 给 SDK。 

###### **TypeScript** 

```arkts
let conversationEventListener: ConversationEventListener = { onInputMention: (select: (user: UserInfoModel) => void) => { if (this.conId.conversationType === ConversationType.Group) { // 1. 跳转到用户列表页面选择用户; // new NavPathStack().pushPath(); // 2. 调用 select 回传 UserInfoModel 给SDK。 const userInfo = new UserInfoModel('userId', 'userName', '') select(userInfo); } } } 
```

##### **输入状态发生变化** 

当会话页面输入状态发生变化时,会触发 onEditChange 方法。如果未设置,SDK 默认不处理该事件。 

###### **TypeScript** 

```arkts
let conversationEventListener: ConversationEventListener = { onEditChange: (isEditing: boolean) => { // isEditing代表输入状态发生变化 } } 
```

##### **会话页面代理接口** 

IMKit 提供了会话页面代理接口 ConversationComponentDelegate,可监听会话页面生命周期。 

###### **TypeScript** 

- 218 - 

export interface ConversationComponentDelegate { /** * IConversationViewModel的创建回调 * @version 1.7.1 */ onViewModelBind?: (vm: IConversationViewModel) => void; 

/** * IConversationViewModel的清理回调 * @version 1.7.1 */ onViewModelClear?: () => void; } 

##### **获取 ViewModel** 

构建 ConversationComponentDelegate 接口传给 ConversationComponent,在 onViewModelBind 方法中可以拿到 IConversationViewModel。 

代码示例 

###### **TypeScript** 

@Component struct CustomChatPage { 

private vm: IConversationViewModel | undefined 

private delegate: ConversationComponentDelegate = { 

onViewModelBind: (vm: IConversationViewModel) => { 

this.vm = vm; 

}, onViewModelClear: () => { this.vm = undefined 

onViewModelClear: () => { 

} 

} 

build() { 

ConversationComponent({ 

conversationData: this.conversationComponentData, 

this.pageShow, 

this.isEdit, 

this.delegate, 

}).layoutWeight(1) 

} 

} 

- 219 - 

##### **ViewModel 能力说明** 

以下是 IConversationViewModel 接口的能力说明,具备常见的能力如:更新或获取输入框内容、获取消息列表、刷新某条 消息,具体见下方代码示例。 

###### **TypeScript** 

- 220 - 

export interface IConversationViewModel { 

/** 

- 进入会话时展示的未读消息的组件点击事件 

*/ 

onClickUnreadMessageButton(): void; 

/** 

- 进入会话时展示的未读@我的消息的组件点击事件 

*/ 

onClickUnreadMentionedMessageButton(): void; 

/** 

- 在进入会话后收到未读新消息的组件点击事件 

*/ 

onClickNewReceivedUnreadMessageButton(): void; 

/** 

- 更新输入框的文本组件的内容 

- @since 1.7.0 

*/ 

onChangeInputTextAreaContent?(text: string): void; /** 

- 获取输入框当前的文本输入组件的内容 

- @since 1.7.0 

*/ 

getInputTextAreaContent?():string; 

/** 

- 获取消息列表 

* 

- 注意:改返回列表仅用于读取,不建议修改。 

* 

- @returns 消息列表 

- @since 1.7.1 

*/ 

getMessageList?(): UiMessage[]; 

/** 

- 刷新某条消息 

- @since 1.7.1 

*/ refreshUiMessage?(message: Message): void; } 

- 221 - 

### **通知与免打扰** 

###### **设置会话免打扰** 

即时通讯服务支持会话免打扰设置。IMKit SDK 可根据会话标识设置消息提醒状态为 **免打扰** 。设置后如果客户端在后台运行 时,会话中有新的消息,将不会进行通知提醒,可以收到消息内容。如果客户端为离线状态,将不会收到远程通知提醒。 

会话的免打扰状态将会被同步到服务端。融云会为用户自动在设备间同步会话免打扰状态数据。客户端可以通过监听器获取同 步通知,也可以主动获取最新数据。 

PushNotificationLevel 的定义: 

|状态名称|状 态 值|说明|
|---|---|---|
|All|-1|全部消息通知。注意:超级群设置全部消息通知时:1. @消息一定收到推送通知;2.普通消息的推送 频率受到服务端默认推送频率设置的影响,无法做到所有普通消息都通知。|
|Default|0|未设置(向上查询群或者APP级别设置),存量数据中0表示未设置|
|Mention|1|群聊和超级群@所有人+ @自己 时通知;单聊代表消息不通知|
|MentionUsers|2|群聊和超级群@自己 时通知,其它情况不通知;单聊代表消息不通知|
|MentionAll|4|群聊和超级群@所有人 时通知,其他情况都不通知;单聊代表消息不通知|
|Blocked|5|消息通知被屏蔽,不接收任何消息通知|

##### **设置会话的免打扰状态** 

RongIM 类提供 setConversationsNotificationLevel 方法,可根据会话标识列表批量设置消息提醒状态为 **免打扰** 。设置成 功后,客户端在后台运行时或处于用户离线状态时,均不会收到该会话的新消息通知。在会话列表页该会话的右下角将展示一 个灰色小铃铛图标。 

###### **示例代码** 

###### **TypeScript** 

- 222 - 

let conIdList = new List< >(); 

let conId = new ConversationIdentifier() conId.conversationType = ConversationType.Private conId.targetId = "targetId" conIdList.add(conId) 

RongIM.getInstance().conversationService().setConversationsNotificationLevel(conIdList, PushNotificationLevel.Blocked); 

##### **监听会话的免打扰状态同步** 

IMKit SDK 支持会话状态(置顶状态数据和免打扰状态数据)同步机制。设置会话状态同步监听器后,如果会话状态改变,可 在本端收到通知。 

当会话的置顶和免打扰状态数据同步后,SDK 会触发 ConversationListEventListener 的 onSyncConversationStatus 方 法; 如果是本端操作,则会触发 onConversationNotificationLevelChange 方法。 

###### **接口原型** 

###### **TypeScript** 

export interface ConversationListEventListener { 

/** * 当其他端修改会话的免打扰和置顶状态时 */ onSyncConversationStatus?: (items: List<ConversationStatusInfo>) => void; /** * 当本端修改会话的免打扰状态时 */ onConversationNotificationLevelChange?: (identifierList: List<ConversationIdentifier>, level: PushNotificationLevel) => void; } 

您可以通过使用 RongIM 的 addConversationListEventListener 与 removeConversationListEventListener 方法添加 或移除监听器。 

###### **示例代码** 

###### **TypeScript** 

- 223 - 

let conversationListEventListener : ConversationListEventListener = { 

onSyncConversationStatus: (items: List<ConversationStatusInfo>) => { 

- //其他端同步会话置顶和免打扰状态 

for (let itemElement of items) { 

- // 根据 itemElement.level 判断 PushNotificationLevel 具体类型 

- } }, 

- onConversationNotificationLevelChange:(items: List<ConversationIdentifier>, level: PushNotificationLevel) = 

- { 

- //本端同步会话置顶和免打扰状态 

for (let itemElement of items) { 

- // 根据 level 判断 PushNotificationLevel 具体类型 

- } } } // 设置监听 

RongIM.getInstance().conversationListService().addConversationListEventListener(conversationListEventListen 

##### **获取会话的免打扰状态** 

您可以通过 RongIM 类提供 getConversationNotificationLevel 方法,根据会话标识列表获取会话的免打扰状态。 

###### **示例代码** 

###### **TypeScript** 

let conId = new ConversationIdentifier() conId.conversationType = ConversationType.Private conId.targetId = "targetId" 

let service = RongIM.getInstance().conversationService() 

service.getConversationNotificationLevel(this.conId) 

- .then((value: IAsyncResult<PushNotificationLevel>) => { 

- if (value.code === EngineError.Success) { 

let level = value.data as 

- // 根据 level 判断 PushNotificationLevel 具体类型 

- } 

- }) 

###### **全局免打扰时段配置** 

IMKit SDK 支持设置通知静默时段,以实现全局免打扰的效果。 

- 224 - 

- 该接口会设置一个从任意时间点( HH:MM:SS )开始的免打扰时间窗口。在再次设置或删除用户免打扰时间段之前,当 次设置的免打扰时间窗口会每日重复生效。例如,App 用户希望设置永久全天免打扰,可设置 startTime 为 00:00:00 , duration 为 1439 。 

单个用户仅支持设置一个时间段,重复设置会覆盖该用户之前设置的时间窗口。 

在经 SDK 设置的全局免打扰时段内: 

- 如果客户端在后台运行时,会话中有新的消息,将不会进行通知提醒,可以收到消息内容。 如果客户端为离线状态,将不会收到远程通知提醒。 

例外情况:@ 消息属于高优先级消息,不受全局免打扰逻辑控制,会始终进行通知提醒。 

PushNotificationLevel 的定义: 

|状态名称|状 态 值|说明|
|---|---|---|
|All|-1|全部消息通知。注意:超级群设置全部消息通知时:1. @消息一定收到推送通知;2.普通消息的推送 频率受到服务端默认推送频率设置的影响,无法做到所有普通消息都通知。|
|Default|0|未设置(向上查询群或者APP级别设置),存量数据中0表示未设置|
|Mention|1|群聊和超级群@所有人+ @自己 时通知;单聊代表消息不通知|
|MentionUsers|2|群聊和超级群@自己 时通知,其它情况不通知;单聊代表消息不通知|
|MentionAll|4|群聊和超级群@所有人 时通知,其他情况都不通知;单聊代表消息不通知|
|Blocked|5|消息通知被屏蔽,不接收任何消息通知|

##### **设置全局免打扰时段配置** 

您可以通过 RongIM 类提供 setNotificationQuietHoursLevel 方法配置全局免打扰级别,以屏蔽所有通知,包括本地通知 以及远程推送通知。 

###### **示例代码** 

###### **TypeScript** 

let option: IQuietHoursOption = { startTime: "01:31:17", duration: 1200, level: PushNotificationLevel.Blocked } RongIM.getInstance().conversationListService().setNotificationQuietHoursLevel(option) 

###### **参数说明** 

- 225 - 

IQuietHoursOption 的定义: 

|参数|类型|说明|
|---|---|---|
|startTime|String|开始消息免打扰时间,格式为HH:MM:SS,例如01:31:17。|
|duration|number|需要消息免打扰分钟数,支持范围为[1-1439]。比如,您设置的起始时间是00:|
|||00, 结束时间为01:00,则duration为60分钟。设置为1439代表全天免打扰|
|||(23 * 60 + 59 = 1439)|
|level|PushNotifcationLevel|消息通知级别,Default代表移除免打扰|

##### **获取全局免打扰时段配置** 

您可以通过 RongIM 类提供 getNotificationQuietHoursLevel 方法获取当前应用设置的全局免打扰配置。 

###### **示例代码** 

###### **TypeScript** 

RongIM.getInstance().conversationService().getNotificationQuietHoursLevel() 

```arkts
.then(result => { if (EngineError.Success !== result.code) { // 获取免打扰失败 return; } if (!result.data) { // 免打扰数据为空 return; } let info = result.data as IQuietHoursOption; // Info 代表免打扰数据 }) 
```

##### **删除已设置的全局免打扰时段配置** 

您可以通过 RongIM 类提供 removeNotificationQuietHours 方法移除之前设置的全局免打扰配置,移除成功后,会正常收 到本地通知或推送通知。 

###### **示例代码** 

###### **TypeScript** 

- 226 - 

RongIM.getInstance().conversationService().removeNotificationQuietHours() .then(result => { if (EngineError.Success !== result.code) { // 移除免打扰失败 return; } //移除免打扰成功 }); 

###### **本地通知** 

IMKit 已实现本地通知的创建、弹出行为,方便开发者快速构建应用。 

##### **什么是本地通知** 

本地通知指应用在前台运行时,由 IMKit 或应用客户端直接调用系统接口创建并发送的通知 (Notification)。IMKit SDK 内部 已经实现了本地通知功能 (Notification),当应用处于前台接收到新消息时,IMKit 默认会在通知面板弹出通知提醒,即本地 通知。 

IMKit 的本地通知已支持以下场景: 

- 当 App 当应用转为后台时,无法弹出本地通知Notification Kit,本地通知发布通道关闭,开发者需要接入Push Kit进 行云侧离线通知的发布。 

提示 

如果应用已集成第三方厂商推送服务,此时可通过接收推送通知。来自第三方厂商的离线推送通知一般由推送厂 商直接创建并弹出,不属于本文所述的本地通知。 

- 当 App 处于前台,SDK 接收新消息后便会构建通知,但通知响铃、震动与否,由手机系统设置中应用的通知管理来决 定。 

##### **拦截本地通知** 

目前只要 SDK 判断 App 在前台,并且非免打扰状态,便会弹出通知。 

应用在本地通知显示前对通知进行拦截。IMKit 支持在拦截修改 Message 后继续弹出本地通知。 

如果需要更多自定义效果,建议完全拦截,由应用程序自行接管并弹出本地通知。 

提示 

- 从 1.4.3 版本开始,支持使用以下方法设置拦截器。 

请在初始化之后,建立 IM 连接之前设置监听器。 

- 227 - 

**示例代码** 

###### **TypeScript** 

```arkts
let notificationInterceptor: NotificationInterceptor = { onWillHandleMessage: (message: Message) => { // 返回 true 则 SDK 不会处理,不会展示通知 return true } } // 设置拦截器 
```

RongIM.getInstance().notificationService().setNotificationInterceptor(notificationInterceptor) 

// 移除拦截器 

RongIM.getInstance().notificationService().removeNotificationInterceptor(notificationInterceptor) 

##### **本地通知展示样式** 

目前暂不支持自定义本地通知展示样式,如果需要自定义,则需要拦截本地通知自行处理。 

##### **本地通知铃声与震动** 

当 App 处于前台,SDK 接收新消息后便会构建通知,但通知响铃、震动与否,由手机系统设置中应用的通知管理来决定。 

目前暂不支持自定义本地通知是否响铃与震动,如果需要自定义,则需要拦截本地通知自行处理。 

##### **本地通知点击事件** 

点击本地通知时,SDK 默认跳转到当前应用的入口的 UIAbility,可以在 UIAbility 的 onNewWant 方法中拿到通知附带的参 数。 

目前暂不支持自定义点击时的跳转事件,如果需要自定义跳转事件或者不进行跳转,则需要拦截本地通知自行处理。 

###### **示例代码** 

###### **TypeScript** 

- 228 - 

onNewWant(want: Want, launchParam: AbilityConstant.LaunchParam): void { if (want.parameters) { 

```arkts
let params: Record<string, object> = want.parameters as Record<string, object> if (params) { let conversationType = params['conversationType'] let targetId = params['targetId'] let fromUserId = params['fromUserId'] let objectName = params['objectName'] let msgTime = params['msgTime'] let msgUid = params['id'] } } } 
```

#### **常见问题** 

###### **SDK 字节码支持** 

参考 配置说明 

###### **如何解决鸿蒙集合的 List 类型和 UI 的 List 组件类名冲突的问题?** 

为了解决类似的冲突问题,DevEco Studio 可以在导入的时候做重命名。 

###### **TypeScript** 

//导入时重命名 import AList from '@ohos.util.List'; //使用重命名 let clazzList: AList<MessageContentConstructor> = new AList(); 

这样 UI 的 List 组件可以正常用 List,集合类型的 List 被重命名为 AList ,两个即可一起使用。 

###### **安卓系统迁移到鸿蒙系统** 

目前鸿蒙 SDK 还不支持从安卓手机升级到鸿蒙系统的平滑迁移。 

- 229 -
