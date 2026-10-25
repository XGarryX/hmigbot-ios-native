# 鸿蒙 **IMSDK** 快速开始 

本文介绍如何快速集成环信即时通讯 IM HarmonyOS SDK 实现单聊。 

## 实现原理 

下图展示在客户端发送和接收一对一文本消息的工作流程。 

## 前提条件 

- DevEco Studio NEXT Developer Beta1(5.0.3.300)及以上; 

- HarmonyOS SDK API 12 及以上; 

- 有效的环信即时通讯 IM 开发者账号和 App key,见 环信即时通讯云控制台。 

## 准备开发环境 

本节介绍如何创建项目,将环信即时通讯 IM HarmonyOS SDK 集成到你的项目中, 并添加相应的设备权限。 

### **1.** 创建 **HarmonyOS** 项目 

参考以下步骤创建一个 HarmonyOS 项目。 

1. 打开 DevEco Studio,点击 **Create Project** 。 

2. 在 **Choose Your Ability Template** 界面,选择 **Application > Empty Ability** , 然后点击 **Next** 。 

3. 在 **Configure Your Project** 界面,依次填入以下内容: 

   - **Project name** :你的 HarmonyOS 项目名称,如 HelloWorld。 

   - **Bundle name** :你的项目包的名称,如 com.hyphenate.helloworld。 

- 

      - **Save location** :项目的存储路径。 

   - **Compatible SDK** :项目的支持的最低 API 等级,选择 `5.0.0(12)` 及 以上。 

   - **Module name** :module 的名称,默认为 `entry` 。 

4. 点击 **Finish** 。根据屏幕提示,安装所需插件。 

上述步骤使用 **DevEco Studio NEXT Developer Beta1** ( **5.0.3.300** ) 示例。 

### **2.** 集成 **SDK** 

打开 SDK 下载页面,获取最新版的环信即时通讯 IM HarmonyOS SDK,得到 `har` 形 式的 SDK 文件。 

将 SDK 文件,拷贝到 `Harmony` 工程,例如放至 `HelloWorld` 工程下 `entry` 模块下的 `libs` 目录。 

修改模块目录的 `oh-package.json5` 文件,在 `dependencies` 节点增加依赖声明。 

```
{
  "name": "entry",
  "version": "1.0.0",
  "description": "Please describe the basic information.",
  "main": "",
  "author": "",
  "license": "",
  "dependencies": {
    "@easemob/chatsdk": "file:./libs/chatsdk-x.x.x.har"
  }
}
```

最后单击 **File > Sync and Refresh Project** 按钮,直到同步完成。 

### **3.** 添加项目权限 

在模块的 `module.json5` ,例如: `HelloWorld` 中 `entry` 模块的 `module.json5` 中, 配置示例如下: 

```
{
module: {
requestPermissions: [
      {
name: "ohos.permission.GET_NETWORK_INFO",
      },
      {
name: "ohos.permission.INTERNET",
      },
    ],
  },
}
```

## 实现单聊 

本节介绍如何实现单聊。 

### **1. SDK** 初始化 

**`let`** `options =` **`new`** `ChatOptions("Your appkey"); ......` _`//`_ 其他 _`ChatOptions`_ 配置。 _`//`_ 初始化时传入上下文以及 _`options`_ `ChatClient.getInstance().init(context, options);` 

### **2.** 创建账号 

测试期间,可以使用如下代码创建账户: 

```
ChatClient.getInstance().createAccount(userId, pwd).then(()=> {
// success logic
});
```

该注册模式为在客户端注册,主要用于测试,简单方便,但不推荐在正式环境中使 用,需要在环信控制台中手动开通开放注册功能;正式环境中应使用服务器端调用 Restful API 注册,具体见注册单个用户。 

### **3.** 登录账号 

使用如下代码实现用户登录: 

```
ChatClient.getInstance().login(userId, pwd).then(() => {
// success logic
})
```

1. 除了注册监听器,其他的 SDK 操作均需在登录之后进行。 

### **4.** 发送一条单聊消息 

_`// `content``_ 为要发送的文本内容, _``toChatUsername``_ 为对方的账号。 **`let`** `message = ChatMessage.createTextSendMessage(toChatUsername, conten t);` **`if`** `(!message) {` **`return`** `; }` _`//`_ 发送消息 `ChatClient.getInstance().chatManager()?.sendMessage(message);` 

## 参考 

环信官网:https://www.easemob.com/ 

鸿蒙开发官 网 :https://developer.huawei.com/consumer/cn/
