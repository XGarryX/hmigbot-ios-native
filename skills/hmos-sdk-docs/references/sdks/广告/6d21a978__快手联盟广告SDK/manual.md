# 快手广告 **HarmonyOS-SDK** 使用指南 **1.** 接入准备 

接入快手广告 SDK 前,请在快手广告平台申请您的 AppId,广告位 id 等 注:当前 **SSP** 平台创建鸿蒙应用为白名单机制,如有接入需求请联系对应商务 

## **2. SDK** 集成 

### 手动引入 **har** 包 

在 oh-package.json5 添加依赖 

{ "dependencies": { "ksadsdk": "file:./KSAdSDK-{version}.har" } } 

工程级 build-profile.json5 中设置 useNormalizedOHMUrl 为 true 

{ "app": { "products": [ { "buildOption": { "strictMode": { "useNormalizedOHMUrl": true } } } ] } } 

#### 注: **useNormalizedOHMUrl** 设置需要在 **Build Version: 5.0.3.500** 以上 

### 添加权限 

- 1.打开 app 模块的 module.json5 文件 

- 2.添加以下权限:访问网络、获取网络状态、获取广告追踪标识(oaid)、传感器(可选)、振 动(可选) 

{ "requestPermissions": [ { "name": "ohos.permission.INTERNET", //访问网络 "reason": "$string:request_network" }, { "name": "ohos.permission.GET_NETWORK_INFO", //获取网络状态 "reason": "$string:request_network_info" }, { "name": "ohos.permission.APP_TRACKING_CONSENT", //获取广告标识 "reason": "$string:request_track" }, { "name": "ohos.permission.ACCELEROMETER", // 传感器,用于实现扭动摇动 "reason": "$string:request_sensor" }, { "name": "ohos.permission.GYROSCOPE", // 传感器,用于实现扭动摇动 "reason": "$string:request_sensor" }, { "name": "ohos.permission.VIBRATE", // 振动,用于交互反馈 "reason": "$string:request_vibrate" } ] }
