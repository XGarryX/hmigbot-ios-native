# 鸿蒙 IMLib SDK 接口文档

本教程旨在帮助开发者快速了解和掌握 IMLib SDK (融云即时通讯能力库) 的基础集成流程与核心通信

能力。通过本教程,您将完成 IMLib SDK 导入、初始化、设置监听、建立连接和发送消息等全流程操

作。

## 环境要求

-
DevEco Studio NEXT Release(5.0.3.900) 及以上。

-
HarmonyOS SDK API 12 及以上。

-
手机系统版本号:NEXT.0.0.31。

-
真机华为 Mate 系列。真机运行需要配置证书,详情参考鸿蒙的签名指南文档。

-
模拟器。详情参考鸿蒙的模拟器运行指南文档。

## 准备工作

1.访问融云控制台,注册您的开发者账号。注册成功后,控制台自动在开发环境中为您创建一个应

用。

2.在控制台的基本信息页,获取您的应用在开发环境的 AppKey。您可在基本信息页查看应用的信

息,如 App Key、App Secret、所属数据中心(默认为北京)。 

1.如您想自己创建应用,参考如何创建应用,并获取对应环境 App Key 和 App Secret。

2.提示

3.每个应用均拥有两个不同的 App Key,分别对应开发环境与生产环境,且两个环境之间数据相互隔

离。在您的应用正式上线前,建议切换到生产环境的 App Key,以便完成上线前全流程测试和最终

发布。

## 导入 SDK

融云支持从OpenHarmony三方库中心仓添加依赖和将 IMLib 相关的 SDK 文件本地库导入应用工程两

种集成方式。

以下介绍如何使用从OpenHarmony三方库中心仓添加依赖方式将 IMLib SDK 导入工程:

1.在鸿蒙主工程 entry 目录中的 oh-package.json5 中添加 SDK 依赖,然后点击 "Sync Now"。

2.JSON

```
// entry 目录中的 oh-package.json5
{
"name": "entry",
"version": "1.0.0",
"description": "Please describe the basic information.",
"main": "",
"author": "",
"license": "",
"dependencies": {
"@rongcloud/imlib" : "x.y.z"
  }
}
```

1.提示

2.各个 SDK 的最新版本号可能不相同,具体 x.y.z 值,可前往融云官网 SDK 下载页面或

OpenHarmony三方库中心仓查询。

3.安装 SDK 成功后,您可以在项目根目录的oh_modules/.ohpm/中找到融云 IMLib SDK。

## 初始化 SDK

IMLib SDK 初始化接口的调用需要引入对应的声明:

```
1
import { IMEngine } from'@rongcloud/imlib';
```

为确保您可以正常连接融云服务器和使用融云即时通讯服务(IM 服务),您须调用 init 方法初始化

IMKit SDK。初始化前,您须在融云控制台中获取 App Key,并设置好 InitOption(初始化配置)。

InitOption 中封装了 areaCode (数据中心的区域码),naviServer(导航服务地址)、

statisticServer(数据统计服务地址)。

如果您使用北京数据中心,则不需设置 InitOption,IMKit SDK 默认连接北京数据中心。

```
// 初始化 SDK
let initOption = newInitOption();
IMEngine.getInstance().init(getContext(), "Your_AppKey", initOption);
```

如果您使用海外数据中心,则须传入海外数据中心对应的 AreaCode。

```
// 初始化 SDK
let initOption = newInitOption();
initOption.areaCode = AreaCode.SG;
IMEngine.getInstance().init(getContext(), "Your_AppKey", initOption);
```

初始化详细说明参见初始化。

## 监听消息

通过设置消息接收监听器,用户可接收所有类型的实时消息和离线消息。

提示

为确保接收所有离线消息,请在初始化 SDK 后,连接 IM 融云服务器之前设置监听器。

```
IMEngine.getInstance().setMessageReceivedListener((message: Message, info:
ReceivedInfo) => {
```

//  针对接收离线消息时,服务端会将 200 条消息打成一个包发到客户端,客户端对这包数据进行

解析。该参数表示每个数据包数据逐条上抛后,还剩余的条数

```
let left = info.left;
// 消息是否离线消息
let isOffline = info.isOffline;
// 是否在服务端还存在未下发的消息包
let hasPackage = info.hasPackage;
});
```

## 连接融云 IM 服务器

用户 Token 是与用户 ID 对应的身份验证令牌,是应用程序的用户在融云的唯一身份标识。应用客户端

在使用融云即时通讯功能前必须与融云建立 IM 连接,连接时必须传入 Token。

在实际业务运行过程中,应用客户端需要通过应用的服务端调用 IM Server API 申请取得 Token。详见

Server API 文档注册用户。

在本教程中,为了快速体验和测试 SDK,我们将使用控制台「北极星」开发者工具箱,从 API 调试页

面调用获取 Token接口,获取到userId为 1 的用户的 Token。提交后,可在返回正文中取得 Token

字符串。

1.为模拟用户通过融云 IM 服务器收发消息,您需要首先注册一个用户。在实际业务中,应用客户端

通过应用服务端调用融云 IM Server API 获取 token。详见 Server API 文档注册用户。在本教程

中,为了快速体验融云服务,您可在控制台「北极星」的 API 调试页面调用获取 Token接口,获取

到 userId 为 1 的用户的 Token。调用返回如下:

```
HTTP/1.1200 OK
Content-Type: application/json; charset=utf-8
{"code":200,"userId":"1","token":"gxld6GHx3t1eDxof1qtxxYrQcjkbhl1V@sgyu.cn.exam
ple.com;sgyu.cn.example.com"}
```

2.设置连接监听器来实时获取连接状态。您可以将连接状态通过 UI 反馈给用户(例如提示“网络连

接中断”或“已重新连接”),提高用户体验。建议在应用生命周期内,初始化 SDK 之后,连接

IM 之前设置 IM 连接状态监听器。详见设置连接状态监听。

```
1
IMEngine.getInstance().setConnectionStatusListener((status: ConnectionStatus)
=> {
2
});
```

3.调用 connect 方法,将 userId 为 1 的用户连接融云 IM 服务。注:IMLib SDK 有重连机制,因此一

个应用生命周期内调用一次 connect 即可,详见连接。

```
let token = "IMToken";
let timeout = 30;
IMEngine.getInstance().connect(token, timeout)
  .then(result => {
  });
```

## 发送消息

最后,您可以模拟向 userId 为 2 的用户发送一条文本消息。除了文本消息,您还可发送图片、文件、

语音、文件等不同类型的消息,详见[消息类型]。

```
1
// 创建会话标识
let conId = newConversationIdentifier();
conId.conversationType = ConversationType.Private;
conId.targetId = "2"; // 按需填写实际的会话 id
// 创建文本消息
let textMsg = newTextMessage();
textMsg.content = "from 鸿蒙 ";
textMsg.extra = "TestExtra";
letoption: ISendMsgOption = {};
// 创建消息体
let msg = newMessage(conId, textMsg);
// 发送消息
IMEngine.getInstance().sendMessage(msg,option,(msg: Message) => {
// 消息入库回调
}).then(result => {
// 消息发送结果
22
})
```

## 更多功能

更多的功能请访问融云官网的鸿蒙 SDK 文档: https://docs.rongcloud.cn/harmonyOS-imlib
