海泰方圆协同签名客户端 SDK 使用文档 V1.0 For Harmony OS 

修订记录: 

# 修订日期 

版本 修订内容 撰写人 

2024-8-11 V1.0 首版创建 Kent 

目录 

一、 SDK 使用说明 3 

1.1 SDK 文件说明 3 

# 1.2 SDK 使用配置 3 

- 一、 SDK 使用说明 

# 1.1 SDK 文件说明 

海泰方圆协同签名客户端 SDK 参考手册 V1.0 For Harmony OS 是基 于鸿蒙系统平台开发的,针对鸿蒙系统提供的一个集成 HAR 包。我们 将提供的压缩包含有以下文件夹: 

doc :该文件夹下的内容是开发参考手册。 

SDK :该文件夹下的内容是集成包文件。 

demo :该文件夹下的内容是使用本 SDK 的 Harmony OS 示例工程。 

1.2 SDK 使用配置 

. 首先将 SDK 目录文件 mobileukey.har 放到您的工程目录的某个文件夹 下。 

. 在您的工程目录下的 oh_package.json5 文件中的 dependencies 

节点添加 package ,如截图所示: 

. 使用 import 导入您需要调用的 HAR 提供的 API 函数,即可调用我司提 供的功能,具体可参考 DEMO 。 

. 添加权限 , 在您工程的模块的文件夹中找到 module.json5 文件中的 requestPermissions 节点中添加需要的权限,如截图所示:
