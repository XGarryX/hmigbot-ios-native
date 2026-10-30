# 下载安装 

目前云眼 AB 测试 SDK 通过外部依赖包引入项目。eyeofcloud 包是 eyeofcloud 静态共享包 

在项目入口模块(默认是 entry 模块)下创建 libs 文件夹,将依赖包放入 libs 文件夹 

下面是导入依赖的配置 

在 oh-package 中配置如下代码: 

dependencies { “eyeofcloud”: “file:./libs/eyeofcloud.har” } 

# 初始化 

使用 createInstance 方法初始化开发工具包,并实例化公开 API 方法 

import{createInstance, UserAttributes} from“eyeofcloud/src/packages/eyeofcloud-sdk/lib/index.node” 

const eyeofcloudClient = createInstance ({ sdkKey: “<Your_SDK_Key>” }) 

# 进行分桶 

使用 decide 方法进行分桶并发送对应事件 

eyeofcloudClient.onReady().then(() => { let user = eyeofcloudClient.createUserContext(“user123”) let decision = user.decide(“flagKey”) user.trackEvent(“eventName”) })
