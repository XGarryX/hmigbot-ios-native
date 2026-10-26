华云天下在线客服智能问答 SDK 使用文档 V1.0 For Harmony OS 

修订记录: 

# 修订日期 

版本 修订内容 撰写人 

2025-1-16 V1.0 首版创建 wuzc 

目录 

一、 SDK 使用说明 3 

1.1 SDK 文件说明 3 

# 1.2 SDK 使用配置 3 

一、 SDK 使用说明 

# 1.1 SDK 文件说明 

华云天下在线客服智能问答 SDK 参考手册 V1.0 For Harmony OS 是 基于鸿蒙系统平台开发的,针对鸿蒙系统提供的一个集成 HAR 包。 

1.2 SDK 使用配置 

SDK 使用配置 

. 首先将 SDK 目录文件 hyworld_znkf.har 放到您的工程目录的某个文件 夹下。 

. 使用 import 导入您需要调用的 HAR 提供的 API 函数,即可调用我司提 供的功能,具体可参考接口文档。 

. 添加权限 , 在您工程的模块的文件夹中找到 module.json5 文件中的 requestPermissions 节点中添加需要的权限,如截图所示:
