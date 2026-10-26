# 鸿蒙接入指南

简介

下载开发工具包

搭建开发环境

使用开发工具包

发送请求调用支付宝社交分享能力

示例说明

接收和处理支付宝返回的响应消息

示例说明

# 简介

本文为鸿蒙终端开发工具的新手使用教程,涉及到支付宝鸿蒙分享开发工具包的使用方法,默认读者已经熟

悉应用开发 IDE 的基本使用方法(本文以 DevEco Studio 为例),以及具有一定的编程知识基础。

支付宝社交分享开放接口免费并默认向开发者开放,所以无需进行签约申请。

接入前请完成相关准备工作,详情可查看接入准备。

●

平台选择Android

●

签名使用SDK中的CommonUtils.getSign()方法获取

# 下载开发工具包

点击下载支付宝鸿蒙分享SDK包

和鸿蒙分享DEMO

。集

📎shareoutersdk.har.zip

📎AlipayShareDemo.zip

成分享到支付宝鸿蒙 SDK 前,请仔细阅读 App 支付宝客户端 SDK 隐私说明。

开发工具包主要包含 3 部分内容(其中 shareoutersdk.har 是必须的):

●

shareoutersdk.har:需要被第三方应用导入的 SDK 库,通过该库可以实现对支付宝社交分享能力接口的

1

调用和通信。

●

APShareDemo.zip:Demo 实例及源代码,供开发者参考开发。

●

CommonUtils.getSign():应用签名获取方法。

# 搭建开发环境

1.在 DevEco Studio 创建 DevEco 应用工程;

2.将开发工具包中的 shareoutersdk.har 复制到libs文件夹中;

3.在entry/oh-package.json5文件中,添加SDK依赖。

Dart

```
"dependencies": {
"@alipay/shareoutersdk": "file:./libs/shareoutersdk.har"
}
```

# 使用开发工具包

# 发送请求调用支付宝社交分享能力

鸿蒙应用要发送请求到支付宝,可以通过 IAPApi 的 sendReq 方法,发送包装好的分享消息请求对象给支付宝

客户端来实现。发送分享消息会唤起支付宝客户端,并在用户完成分享操作后,可以选择回到鸿蒙应用界面。

2

## 示例说明

下面将通过一个简单的发送文本类分享信息给好友作为例子演示如何发送请求调用支付宝社交分享能力。

1.首先,使用到开发工具包中的如下类,来实现发送请求:

Dart

```
import {
```

APAPIFactory, //社交分享开放工具工厂类,用于创建工具实例

```
APImageObject, //图片消息内容定义类
APMediaMessage, //分享消息定义类
```

APTextObject, //普通文本消息内容定义类

```
APWebPageObject, //网页内容定义类
```

IAPApi, //社交分享开放工具接口类,便于对社交分享开放接口的调用

```
SendMessageToZFB//分享消息请求包装类
  } from'@alipay/shareoutersdk';
```

1.在事件触发代码中加入如下代码:

Dart

```
```

//创建工具对象实例,此处的APPID为上文提到的,申请应用生效后,在应用详情页中可以查到的支

付宝应用唯一标识

```
letapi=APAPIFactory.createZFBApi(this.context, Constants.APP_ID);
//组装文本消息内容对象
lettextObject=newAPTextObject();
textObject.text="需要发送的内容";
//组装分享消息对象
letmediaMessage=newAPMediaMessage();
mediaMessage.mediaObject=textObject;
//将分享消息对象包装成请求对象
letreq=newSendMessageToZFB.Req();
req.message=mediaMessage;
//发送请求
api.sendReq(req);
```

1.完成后,生成鸿蒙安装文件到移动端。

注意:移动端需要安装好支付宝客户端。

3

# 接收和处理支付宝返回的响应消息

当应用成功将分享请求消息发送给支付宝客户端后,用户将在客户端完成分享操作,在用户完成操作后,支付宝

将会把用户操作的结果消息返回给开发者的鸿蒙应用。当开发者需要处理该响应消息时,可以通过实现

IAPAPIEventHandler 接口的 onResp 方法来处理消息。

## 示例说明

下面将实现接收和处理上文中文本消息分享后支付宝返回的响应消息,来说明如何接收和处理支付宝返回的响应

消息。

1.使用到开发工具包中的如下类,来实现接收和处理响应消息:

4

Dart

```
import {
```

APAPIFactory, //社交分享应用工具工厂类,用于创建工具实例

BaseReq,  //社交分享应用的通用请求对象

BaseResp, //社交分享应用的通用响应对象

ErrCode, //社交分享应用错误码

IAPAPIEventHandler//社交分享应用工具通用事件处理接口

```
  } from'@alipay/shareoutersdk';
```

2.新增一个 EntryAbility 类,该类继承自 UIAbility(@kit.AbilityKit);

3.在module.json5文件中设置 EntryAbility 的exported为true:

Dart

```
"name": "EntryAbility",
"export ed": true,
```

4.通过实现 IAPAPIEventHandler 接口,来定义如何处理返回的响应消息,要处理返回的响应消息,需要实

现 onResp(baseResp: BaseResp) 方法;

注意:本文为方便,直接让 EntryAbility 实现 IAPAPIEventHandler 接口。

5

Dart

```
export defaultclassEntryAbilityextendsUIAbilityimplementsIAPAPIEventH
andler {
  ...
onResp(baseResp: BaseResp){
promptAction.showToast({
message: baseResp.errCode?.toString(),
duration: 3000
      });
  }
}
```

5.在 EntryAbility 中将接收到的 want 及实现了 IAPAPIEventHandler 接口的对象传递给 IAPApi 接口的

handleIntent 方法,此方法最好在 EntryAbility 的 onNewWant 方法中完成调用。

Dart

```
```

//创建工具对象实例,此处的APPID为上文提到的,申请应用生效后,在应用详情页中可以查到的支付

宝应用唯一标识

//通过调用工具实例提供的handleIntent方法,绑定消息处理对象实例,

```
if (want.parameters) {
letapi=APAPIFactory.createZFBApi(this.context, Constants.APP_ID)
api.handleIntent(want.parameters, this);
}
```

6.完成后,生成鸿蒙安装文件到移动端。

注意:移动端需要安装好支付宝客户端。

6
