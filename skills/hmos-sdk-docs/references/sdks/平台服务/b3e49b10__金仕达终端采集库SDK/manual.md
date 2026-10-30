# 0. 说明 

1. 采集库文件由上海金仕达软件科技股份有限公司提供,用于完成对鸿蒙终端的信息采集。 

2. 使用者需对 HAR 文件进行妥善保管和正确使用,不得进行非法篡改、非法分发等。 

3. HarmonyOS Next 版本更新较快,若在使用过程中发现问题,请及时反馈。 

# # 1. HAR 

采集库以 HAR(Harmony Archive)静态共享包方式提供,当前支持的架构为 arm64-v8a,x86_64。 

# ## 1.1 编译环境 

``` 

"compileSdkVersion": "5.0.0(12)", 

"compatibleSdkVersion": "5.0.0(12)", 

"targetSdkVersion": "5.0.0(12)" 

``` 

## 1.2 使用 

在需要引入三方包的模块的 oh-package.json5 中设置本地 HAR 包。 

以 HAR/HSP 包在工程根目录下为例,配置示例如下(实际配置时请以 HAR/HSP 包实际目录 为准) 

``` 

"dependencies": { 

"libkcy_hm": "file:path/to/libkcy_hm.har" // 此处也可以是以当前 oh-package.json5 所在目 录为起点的相对路径 

} 

``` 

## 1.3 权限 

HAR 内部不检查使用方是否具备系统接口需要的权限,权限的申请和管理由使用方自行处理。 若使用方不具备接口需要的权限,则采集信息中部分字段的信息为空。 

# # 2. 接口说明 

``` 

```

## 2.1 接口说明 

getSystemInfo ## 获取采集信息 getApiVersion ## 获取采集版本 ``` 

## 2.2 导入接口 

``` 

import { getSystemInfo, getApiVersion } from 'libkcy_hm'; ``` 

# ## 2.3 调用接口示例 

private testApiDemo() { // 获取采集库版本 let libraryVersion = getApiVersion(); console.log("系统的版本为:" + libraryVersion); 
```

// 获取采集信息 let systemInfo = getSystemInfo(); systemInfo.then(result => { console.log("系统的加密信息为:" + result); }); 

} ``` 

## 2.4 安装 

``` 

ohpm install libkcy_hm ```

```
