# **SDK接入配置** 

# **SDK 接入配置** 

## **1. 概述** 

### **1.1 简介** 

### **1.2 说明** 

本文档旨在帮助Harmony 应用开发者在程序中快速接入优加SDK 提供广告填充,为媒体提供变现途径,作为 应用开发者,您只需要进行简单配置,就可以在您的应用中显示定制的广告.关于SDK 的具体使用方法,请仔细 阅读下面的文档. 

## **2. 开发环境** 

### **2.1 基础配置要求** 

确保您的开发及部署环境符合以下标准: 

- 开发工具:推荐NEXT Developer Beta3 及以上版本 部署目标:HarmonyOS NEXT 及以上版本 SDK 版本:HarmonyOS 12 及以上版本 

### **2.2 部署SDK** 

Harmony SDK 支持通过ohpm(OpenHarmony Package Manager)工具实现自动化部署,该方式可确 保依赖管理的标准化与高效性.以下为详细操作指引,更多关于ohpm 的使用细节可查阅 查阅官方文档 

#### **2.2.1 具体部署步骤** 

#### **方式一:通过ohpm install 命令导入** 

#### **1、准备工作** 将目标SDK 文件(如AMPSSDK_5.3.0.har)存放至本地已知路径(例如D:\ 目录). 

**2、执行命令** 打开命令行工具,切换至项目根目录(示例路径:D:\BeiziAdDemo). 在创建的项目目录下,进 入命令行输入:ohpm install SDK地址输入以下命令安装依赖: 

D:\BeiziAdDemo> ohpm install D:\AMPSSDK_5.3.0.0.har 

#### **方式二:通过oh-package.json5 依赖同步** 

#### **1、文件放置** 在项目entry 目录下创建libs 文件夹,将AMPSSDK_5.3.0.har 复制到该目录中. 

**2、配置依赖** 编辑项目根目录的oh-package.json5 文件,在dependencies 字段中添加以下配置: 

{ 

//... "dependencies": { "biz.beizi.adn": "file:./libs/AMPSSDK_5.3.0.0.har" } } 

至此依赖Harmony SDK 完成. 

## **3. 配置权限说明** 

添加权限 **注意** :SDK不强制获取可选权限, 即使没有获取可选权限SDK也能正常运行; 获取可选 权限将帮助SDK优化投放广告精准度和用户的交互体验, 提高eCPM. **注意** :SDK本身不会发起动 态权限申请. 

### **3.1 SDK内部已有权限** 

SDK内部已经配置添加了[开放权限(系统授权)]、网络权限、加速度权限、陀螺仪权限,SDK内部必要权限. 开发者不用自己声明添加,这里进行说明. 

**注意** : 这三种权限均为系统授权(system_grant)的开放权限,面向所有应用开放.应用申请 了system_grant权限后,系统将在用户安装应用时,自动把相应权限授予给应用. 

//SDK内置权限 

"requestPermissions": [ { "name": "ohos.permission.INTERNET", "reason": "$string:net_work" }, { "name": "ohos.permission.ACCELEROMETER", "reason": "$string:sensor" }, { "name": "ohos.permission.GYROSCOPE", 

"reason": "$string:sensor" 

} 

] 

### **3.2 开发者可选权限** 

开发者可选权限有,获取设备模糊位置信息权限、跨应用关联权限.获取可选权限将帮助SDK优化投放广告精 准度和用户的交互体验, 提高eCPM.如果开发者配置,可以选择在module.json5文件中声明 

//可选权限 

"requestPermissions": [ 

{ "name": "ohos.permission.APPROXIMATELY_LOCATION",//获取设备模糊位置信息权限 "reason": "$string:location_reason", "usedScene": {"abilities": ["entry"]} 

}, 

{ "name": "ohos.permission.APP_TRACKING_CONSENT",//获取OAID所需权限,需要动态申请 "reason": "$string:trancking_reason", "usedScene": { "abilities": [ 

"entry" 

] 

} 

} 

] 

#### 权限说明 

|**系统平台**|**申请权限**|**调用时机**|**使用目的**|
|---|---|---|---|
||访问互联网|初始化时|检查设备连网络状态,确保SDK与服务 端的通讯求|
||加速度传感器数据|展示带有摇一摇和欧拉角组件 并允许使用传感器广告时|优化用户跳转广告方式|
|Harmony|陀螺仪传感器数据|展示带有摇一摇和欧拉角组件 并允许使用传感器广告时|优化用户跳转广告方式|
||允许应用读取开放匿名 设备标识符|广告请求|广告投放及广告监测归因、精准度、 反作弊|
||访问粗略位置(可选)|广告请求|广告投放及广告监测归因、反作弊|
