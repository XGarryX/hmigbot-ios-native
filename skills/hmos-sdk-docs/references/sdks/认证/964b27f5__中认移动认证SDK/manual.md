# 中认移动认证 **SDK** 使用指南 

## **1.** 下载安装 

- 通过本地 har 集成 

- (1) 下载 url:blob:https://www.cqcca.com/464b29d3-d08c-4cef-91fb-994d7fad2d6f 或联系北京中认环宇信息安全技术有限公司获取最新的 SDK。 

- (2) 将获取的 ZIP 文件解压缩后(解压获取的 har 文件)放进指定目录,如下图 所示: 

## **2.** 配置权限 

- 在引用模块 module.json5 文件中配置所需权限 

"requestPermissions": [{ "name": "ohos.permission.INTERNET", "reason": "$string:reason", "usedScene": { ... }, },{ "name": "ohos.permission.KEEP_BACKGROUND_RUNNING", "reason": "$string:background_reason", "usedScene": { ... 

} 

} ] 

## **3.** 初始化 **SDK** 

用户在接入 SDK 后,在 app 每次启动后,调用 SDK 接口之前需进行一次 SDK 初 始化操作。其中第二第三个参数请联系北京中认环宇信息安全技术有限公司获取。 

AuthApi.init(getContext(), appId, addrServer); 

## **4.** 调用接口 

按照《中认移动认证 SDK(harmony)接口说明文档》操作完成接口调用。
