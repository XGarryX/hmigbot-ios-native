# 鸿蒙 IMSDK 快速入门

# 1.环境要求

## 1.1编译环境

-
DevEco Studio 版本号:DevEco Studio NEXT Developer Beta1 5.0.3.403

-
手机系统版本号:NEXT.0.0.26

## 1.2设备要求

-
真机华为 Mate 系列

## ◦

真机运行需要配置证书,参考:

https://developer.huawei.com/consumer/cn/doc/harmonyos-guides/ide-signing-

0000001587684945

-
模拟器

## ◦

参考:https://developer.huawei.com/consumer/cn/doc/harmonyos-guides/ide-run-

emulator-0000001582636200

## 1.3操作步骤

### 1.3.1创建 IM 应用

在融云管理后台创建应用。融云官网:https://www.rongcloud.cn/

获取 appKey 和 Token

### 1.3.2创建鸿蒙应用

鸿蒙创建应用:https://developer.huawei.com/consumer/cn/doc/app/agc-help-createapp-

0000001146718717

# 2. SDK 接入流程

当前 SDK 提供连接、消息、会话、聊天室等功能,详细见接口文档

注:当前仅提供本地依赖方式,SDK 仅支持 arm64-v8a 架构(鸿蒙真机和模拟器均支持 arm64-

v8a)

SDK 需要网络权限和本地存储权限,SDK 已处理好权限的申请,APP 无需额外此类权限

## 2.1导入 SDK

创建 entry/libs 文件夹,将 SDK har 放入其中

## 2.2依赖 SDK 

### 2.2.1命令行安装 SDK

在 APP 根路径下执行

```
ohpm install entry/libs/RongIMLib.har
1
```

执行完,在工程根路径下的 oh-package.json5就会依赖 SDK

```
// app 根路径下的 oh-package.json5
{
  "name": "mydemo",
  "version": "1.0.0",
  "description": "Please describe the basic information.",
  "main": "",
  "author": "",
  "license": "",
  "dependencies": {
"@rongcloud/imlib": "file:entry/libs/RongIMLib.har" // 该配置由命令行生成
  },
  "devDependencies": {
    "@ohos/hypium": "1.0.16",
    "@ohos/hamock": "1.0.0"
  }
}
```

### 2.2.2entry  配置文件依赖 SDK

在entry同级目录的 oh-package.json5 配置 SDK 依赖

```
// entry 同级目录下的 oh-package.json5 需要手动配置
{
  "name": "mydemo",
  "version": "1.0.0",
  "description": "Please describe the basic information.",
  "main": "",
  "author": "",
  "license": "",
  "dependencies": {
"@rongcloud/imlib": "file:./libs/RongIMLib.har"  // 该配置手动依赖
  },
  "devDependencies": {
    "@ohos/hypium": "1.0.16",
    "@ohos/hamock": "1.0.0"
  }
}
```

### 2.2.3同步项目

entry/oh-package.json5 中点击 Sync Now 同步工程

同步之后就可以按照接口文档正常使用 SDK。

假如同步之后无法导入 SDK,原因可能是 DevEco-Studio 的编译缓存问题,尝试把 DevEco-Studio 完

全关闭之后重新打开 APP 工程

## 2.3添加 SDK 依赖权限

SDK 需要权限如下

ohos.permission.GET_NETWORK_INFO

ohos.permission.INTERNET

ohos.permission.STORE_PERSISTENT_DATA

具体权限配置参考鸿蒙文档:https://developer.huawei.com/consumer/cn/doc/harmonyos-

guides/3_2_u5e94_u7528_u6743_u9650_u7ba1_u63a7-0000001820999661

# 3.参考

融云官网:https://www.rongcloud.cn/

鸿蒙开发官网:https://developer.huawei.com/consumer/cn/
