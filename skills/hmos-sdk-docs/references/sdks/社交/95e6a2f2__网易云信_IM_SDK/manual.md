# 网易云信IM HarmonyOS SDK 开发使用

# 指南

网易云信即时通讯 SDK(NetEase Instant Messaging SDK,简称 NIM SDK)为 HarmonyOS 项目提供

完善的即时通信功能开发能力。NIM HarmonyOS SDK 屏蔽其内部复杂细节,对外提供较为简洁的

API,方便您快速集成即时通信功能。

# 功能模块

IM HarmonyOS SDK 提供的功能包括登录、会话、消息、群组、用户、好友、存储服务、推送、自定义

通知、设置、信令、聊天室、圈组等功能。

对应上述功能提供业务组件 har 包,包括 connversation、conversationgroup、localconversation、

message、team、user、friend、signalling、chatroom。模块架构如下图所示:

# 开发环境要求

DevEco Studio NEXT Developer Beta1(5.0.3.300)及以上。

HarmonyOS SDK API 12 及以上。

运行环境 HarnomyOS NEXT 2.1.2.5 (Canary1) 以上。

# 集成 SDK

通过

1.

下载.har形式的 NIM SDK 产物。

NIMApiDemo/entry/libs

将 SDK 文件拷贝到 HarmonyOS 工程,例如放至

2.

entry模块下的libs目录。

修改模块目录的

3.

oh-package.json5文件,在dependencies节点增加依赖声明。

```
JSON{
    "name": "entry",
    "version": "1.0.0",
    "description": "Please describe the basic information.",
    "main": "",
    "author": "",
    "license": "",
    ...
    "dependencies": {
        <!-- 业务模版 har 包,可以按需添加 -->
        "@nimsdk/conversation": "file:../../libs/conversation.har",
        "@nimsdk/conversationgroup": "file:../../libs/conversationgroup.har",
        <!-- 业务模版 localconversation 与 conversation 和 conversationgroup 为互斥关系,不
>
        "@nimsdk/localconversation": "file:../../libs/localconversation.har",
        <!-- 业务模版 localconversation 与 conversation 和 conversationgroup 为互斥关系,不
>
        "@nimsdk/message": "file:../../libs/message.har",
        "@nimsdk/team": "file:../../libs/team.har",
        "@nimsdk/user": "file:../../libs/user.har",
        "@nimsdk/friend": "file:../../libs/friend.har",
        "@nimsdk/signalling": "file:../../libs/signalling.har",
        <!-- HarmonyOS IMSDK 基础业务模块,必须添加 -->
        "@nimsdk/nim": "file:../../libs/nim.har",
        "@nimsdk/base": "file:../../libs/base.har"
    }
 ...
}
```

示例代码中的插件关系如下(实线箭头表示强引用关系,虚线箭头表示弱引用关系):

单击

4.

File > Sync and Refresh Project按钮,直到同步完成。

# 调用 API

集成 NIM SDK 后,所有 SDK 能力均通过 NIM SDK 实例提供的service进行调用,例如:

通过

loginService进行登录:

```
TypeScriptconst nim: NIMInterface = NIMSdk.newInstance(context, initializeOptions,
serviceOptions)
nim.loginService.on('onLoginStatus', loginStatus => {
console.log('收到 V2NIMLoginService 模块的 onLoginStatus 事件', loginStatus);
})
await nim.loginService.login("YOUR_ACCOUNT", "YOUR_TOKEN")
```

通过

messageService进行消息发送:

```
TypeScriptconst message = nim.messageCreator.createTextMessage("hello")
nim.messageService?.sendMessage(message, 'YOUR_ACCOUNT|1|RECEIVER_ACCOUNT')
```

# API 参考

您可以参考

,查看并了解 NIM SDK API。

API 概览

# 下一步

完成 SDK 集成后,您可以尝试

。

初始化
