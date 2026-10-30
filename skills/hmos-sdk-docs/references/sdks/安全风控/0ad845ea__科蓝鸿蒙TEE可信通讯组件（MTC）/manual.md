## 科蓝鸿蒙 TEE 可信通讯组件(MTC)V1.0.0 使用指南 

## 一、集成方式 

### 1.1 工程中引入组件har 包 

步骤1: 将har 包放入entry 目录下的libs 目录中(没有则新建目录) 

步骤2: 修改引用har 包的工程中的oh-package.json5 文件,在 dependencies 节点下增加 "@csii/lib_mtc":"file:./libs/lib_mtc.har"(@csii/lib_mtc 名称可自定义) oh-package.json5 文件案例: 

{ "name": "entry", "version": "1.0.0", "description": "Please describe the basic information.", "main": "", "author": "", "license": "", "dependencies": { "@csii/lib_mtc":"file:./libs/lib_mtc.har" } } 

步骤3:根据IDE Dev studio 提示进行同步,点击“sync now”执行同步 

# 二、使用说明 

### 2.1 添加权限 

在entry 目录下的module.json5 文件中添加requestPermissions 权限 { 

1 

//网络权限 

"name": "ohos.permission.INTERNET" 

} 

### 2.2 初始化加密通讯通道 

CommunicationCryptoBuilder.initCommunicationKey(“地址”).then((res) => { if (res.isSuccess) { console.info("init success") this.toast("初始化成功") } else { this.toast(res.msg) } }) 

### 2.3 发送接口 

//加密 

let enc: ReInfo = CommunicationCryptoBuilder.encryptBody(JSON.stringify(param)) 

if (enc.isSuccess) { 

let value = await httpRequestPost(“url”, enc.msg) if (value.isSuccess) { 

let res = CommunicationCryptoBuilder.decryptBody(value.msg) this.plainText = res.msg 

} 

} 

2
