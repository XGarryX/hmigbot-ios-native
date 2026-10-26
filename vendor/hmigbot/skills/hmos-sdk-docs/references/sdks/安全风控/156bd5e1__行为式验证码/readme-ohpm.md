> 来源: ohpm 中央仓 README(T1 信源) | 包: `@geetest/captcha`(市场登记名 `@tianyu/captcha`) | ohpm 最新版: 1.1.5 | 抓取: 2026-07-16
> 注意: 版本可能比市场快照新,以此为准时核对 CHANGELOG

> 同族其它包: @yidun/captcha, captcha_lib, xd_captcha, @hzw/zcaptchacode, @wuyo/anjipluscaptcha

---
title: 验证4.0-鸿蒙-部署文档
type: 验证4.0-鸿蒙-部署文档
order: 0
---

# 概述与资源

极验行为验-验证码  `HarmonyOS Next SDK` 提供给集成 `HarmonyOS Next` 原生客户端开发的开发者使用。

## 产品简介

| 条目 | 说明                                                                                |
| ---------------- |-----------------------------------------------------------------------------------|
| SDK名称          | 极验-行为验证第四代                                                                        |
| 开发者信息       | 武汉极意网络科技有限公司                                                                      |
| 最新版本号       | v1.1.5                                                                            |
| 最新版本发布时间 | 2025/11/10                                                                        |
| 主要功能         | 新一代验证码,更智能地解决机器脚本程序自动化攻击带来的业务损失与安全隐患                                              |
| SDK隐私政策      | [行为验证第四代-隐私政策](https://www.geetest.com/Private/gt4)                               |
| SDK合规指南      | [行为验证第四代-合规指南](https://docs.geetest.com/gt4/compliance)                           |
| 资源链接         | [登录后台获取 SDK](https://auth.geetest.com/product) 登录后,点击右上角账号>SDK 下载中心>选择对应产品 SDK |

## 环境需求

| 条目         | 资源                            |
|------------|-------------------------------|
| 开发目标       | `HarmonyOS Next`              |
| 开发环境       | `DevEco Studio 5.1.0 Release` |
| 编译版本       | `API Version 20 Release`      |
| `SDK` 三方依赖 | 无                             |
| 包增量        | 验证 `SDK`: `110K`              |

## 相关资源

| 条目         | 资源地址                                                                                       |
| ------------ |--------------------------------------------------------------------------------------------|
| 产品结构流程 | [通讯流程](/gt4/overview/flowchart/#通讯流程), [交互流程](/gt4/overview/flowchart/#交互流程)               |
| 常见问题     | [Error Code 列表](/gt4/apirefer/errorcode/android)                                       |

# 安装

## 集成 `SDK`

### 手动下载集成

从 `SDK` 资源包链接下载 `.zip` 文件获取最新的 `sdk`。

#### 导入 `SDK`

将 `zip` 包中的 `.har` 文件(包括 `geetest_captcha_harmonyos_vx.y.z_date.har` )拖拽到工程中的 `libs` 文件夹下,在拖入 `.har` 到 `libs` 文件夹后,还要检查 `.har` 是否被添加到 `Library`,要在项目的 `oh-package.json5` 下添加如下代码:

```groovy
"dependencies": {
    "@geetest/captcha": "file:./libs/geetest_captcha_harmonyos_vx.y.z_date.har"
}
```

### OHPM仓库集成

执行`ohpm`安装命令即可安装`sdk`。

```bash
ohpm i @geetest/captcha
```

### `添加权限`

   ```json5
      "requestPermissions": [
      {
        "name": "ohos.permission.INTERNET",
        "usedScene": {
          "abilities": [
            ...
          ],
          ...
        }
      }
    ],
   ```

### 混淆规则

极验 `SDK` 已做混淆处理,集成时请带上混淆规则,勿再次混淆 `SDK`

## 配置接口

### 调用逻辑

1. 配置初始化
2. 启动验证
3. 获取验证回调
4. 销毁资源

> 参考行为验证的[产品结构流程](/gt4/overview/flowchart/#通讯流程), 必须要先在您的后端搭建相应的**服务端接口**(请参考服务端部署文档),并配置从[极验管理后台](https://account.geetest.com/login) 获取的 `captchaId` 和 `Key`

#### 初始化

`SDK` 初始化配置信息,可放在 `onCreate` 或者 `onCreateView` 方法进行初始化

**方法描述**

```typescript
public static getClient(context: UIContext): GTCaptcha4Client;
public init(captchaId: string, config?: GTCaptcha4Config): GTCaptcha4Client;
```

**参数说明**

| 参数      | 类型                 | 说明                   |
| --------- |--------------------|----------------------|
| `context` | `UIContext`        | UI实例对象,必须为 `page` 实例 |
| `captchaId`   | `string`           | `APP_ID`,必须参数        |
| `config`  | `GTCaptcha4Config` | 参数配置对象,非必须           |

#### 启动验证

开始验证流程

**方法描述**

```typescript
public void verifyWithCaptcha();
```

#### 取消验证

取消验证流程,关闭验证窗口

**方法描述**

```typescript
public void cancel();
```

#### 开启/关闭日志监控

设置开启或关闭日志打印监控

**方法描述**

```typescript
public void setLogEnable(enable: boolean);
```

#### 获取验证回调

```typescript
public GTCaptcha4Client addOnSuccessListener(OnSuccessListener listener);
public GTCaptcha4Client addOnFailureListener(OnFailureListener listener);
public GTCaptcha4Client addOnWebViewShowListener(OnWebViewShowListener listener);
```

**代码示例**

```typescript
this.gtCaptcha4Client.addOnSuccessListener({
  async onSuccess(status: boolean, response: string) {
    if(status){
      // TODO 开启二次验证
    }else {
      // TODO 用户答案验证错误
    }
  }
})
  .addOnFailureListener({
    onFailure: function (error: string) {
      console.log('onFailure' + error);
    }
  })
  .addOnWebViewShowListener({
    onWebViewShow: function () {
      console.log(`onWebViewShow`);
    }
  })
```

##### 正常加载代码示例

```typescript
onClick(() => {
    gtCaptcha4Config: GTCaptcha4Config =  new GTCaptcha4Config()
            .setIsDebug(false) // TODO 线上务必关闭
            .setLanguage("zh")
            .setTimeOut(10000)
            .setIsCanceledOnTouchOutside(true);
    gtCaptcha4Client: GTCaptcha4Client = GTCaptcha4Client.getClient()
            .init("your captcha_id", config)
            .addOnSuccessListener({
            async onSuccess(status: boolean, response: string) {
              AlertDialog.show({ message: response })
                if(status){
                    // TODO 开启二次验证
                }else {
                    // TODO 用户答案验证错误
                }
            }
          })
           .addOnFailureListener({
             onFailure: function (error: string) {
               console.log('onFailure' + error);
             }
          })
           .addOnWebViewShowListener({
             onWebViewShow: function () {
               console.log(`onWebViewShow`);
             }
          })
           .verifyWithCaptcha();
})
```

> 示例代码细节参考官方提供的 Demo

##### 参数配置

通过 `GTCaptcha4Config.Builder` 类配置参数

| 定义                        | 说明                                       |
| --------------------------- |------------------------------------------|
| `setParams`                 | 额外的参数,会被会传递到前端 `js` 中使用                  |
| `setIsDebug`                  | 是否 `debug` 模式,默认 `false`,线上请置为 `false`   |
| `setLanguage`               | 指定语言,默认跟随应用语言                            |
| `setIsCanceledOnTouchOutside` | 点击区域外是否消失,默认 `true`                      |
| `setTimeOut`                | 设置超时,单位 `ms`,默认 10000                    |
| `setResourcePath`           | 设置中间地址,默认加载极验公共 `html` 文件                |
| `setBackgroundColor`        | 设置背景颜色,默认透明                              |
| `setDialogStyle`            | 设置对话框的主题样式,默认值`{alignment: DialogAlignment.Center}` | 

可通过 `setParams` 接口配置参数见接口文档

> `setParams` 接口只能接收基本数据类型、字符串、`JSONArray` 类型的数据

### 处理错误

验证过程中可能发生一些预料之外的错误, 您可以通过实现 `addOnFailureListener`接口后, 在下面的回调方法中进行处理:

注意:错误回调包括用户主动取消验证,可单独过滤掉

```typescript
gtCaptcha4Client.addOnFailureListener({
  onFailure: function (error: string) {
    // 返回error内容示例
    // {"code":"-34460","msg":"验证会话已取消","desc":{"description":"User cancelled 'Captcha'"}}
    // 可对error做json解析,自行替换错误描述,保留错误码
  }
})
```

**强烈建议在向用户展示验证错误原因时,同时展示错误码,方便后续排查线上问题。**

可能遇到的错误码请参考后面的列表: [Error Code 列表](/gt4/apirefer/errorcode/android)
