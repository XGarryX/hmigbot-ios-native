# **Shiply Harmony SDK** 使用指南 

## 产品概述 

### 什么是 **Shiply SDK** 

Shiply 专业版 SDK 是为移动开发者提供的一套完整解决方案,主要功能包括: 

- 动态配置下发 : 实时更新应用配置,无需发版即可调整应用行为 

- 动态资源下发 : 支持图片、音频、视频等资源的动态更新 

### 核心优势 

- 零发版更新 : 配置和资源可实时下发,无需应用商店审核 

- 精准投放 : 支持无限扩展的条件规则和千万级规模人群包 

- 高可用性 : 99.9% 的服务可用性保障 

- 安全可靠 : 企业级安全防护,数据传输加密 

### 使用场景 

#### 远程配置使用场景: 

- 特性开关:快速开启或关闭特定功能,响应市场变化。 

- 功能实验:进行 A/B 测试,优化用户体验。 

- 参数动态化:实时调整应用参数,提升灵活性和适应性。 

#### 远程资源使用场景: 

- App 包体积优化:通过远程按需加载资源(如 H5 离线包、模型、运营素材),显著减少软件 包大小,提升下载转化率。 

- 运营活动分钟级发布:如双 11 、奥运会等大型活动期间,需要快速上线运营页面,传统的更 新方式难以满足分钟级发布的需要。而通过远程配置、远程资源,实现动态加载页面素材和 活动规则,可以实现分钟级的更新和优化。 

- 端智能模型管理:在端智能模型时代,功能优化往往通过更新模型实现,为了更新模型提审 

- 一个版本未免大费周章,通过远程资源部署模型可实现发布即更新。 

- 远程资源按需更新:将部分资源(如图片、配置文件、素材等)存放在远程服务器上, App 

- 在运行时按需下载。这种方式可以有效减小 App 的初始包体积,同时实现资源的动态更新。 

- 功能插件化:将 App 的功能模块化,以插件的形式存在。根据用户的需求和使用场景,动态 加载和更新插件,从而避免了整体 App 的频繁更新。 

- 构建用户个性化体验:对于只有 VIP 用户需要的动画、素材资源,可以实现定向发布更新, 按需下载,还能避免占用普通用户的存储空间。 

- 主题、字体、皮肤管理:如何灵活地管理 App 的字体、皮肤和主题,以满足不同用户的个性 化需求。 

### 系统要求 

- 鸿蒙系统 : API 9 及以上版本 

- 开发工具 : DevEco Studio 4.0 及以上 

- 网络要求 : 支持 HTTPS 网络访问 

## 安装和设置步骤 

### **1.** 创建 **Shiply** 项目 

1. 访问 Shiply 管理平台 

2. 注册账号并登录 

3. 创建新项目,选择平台为 `Harmony` 

4. 获取项目的 `APP ID` 和 `APP Key` 

### **2.** 配置开发环境 

#### **2.1** 设置 **ohpm** 仓库源 

ohpm config set registry https://ohpm.openharmony.cn/ohpm/ 

#### **2.2** 自动集成(推荐) 

在项目根目录执行以下命令: 

# 安装 Shiply SDK ohpm install shiply@latest 

# 安装依赖库 ohpm install aki 

#### **2.3** 手动集成 

如果无法使用 ohpm ,可以手动集成: 

1. 下载 `shiply.har` 文件 

2. 在模块下创建 `libs` 目录 

3. 将 `shiply.har` 放入 `libs` 目录 

4. 在 `oh-package.json5` 中添加依赖: 

{ "dependencies": { "@ohos/shiply": "file:../shiply", "@ohos/aki": "^1.2.6" } } 

### **3.** 权限配置 

在 `module.json5` 文件中添加网络权限: 

{ "requestPermissions": [ { "name": "ohos.permission.INTERNET" }, { "name": "ohos.permission.GET_NETWORK_INFO" } ] } 

## 功能操作指南 

### 配置发布功能 

#### **1.** 初始化 **SDK** 

```arkts
import { RDelivery, RDeliveryConfig } from '@ohos/shiply' import hilog from '@ohos.hilog'; import common from '@ohos.app.ability.common'; 
```

// 创建配置对象 let config: RDeliveryConfig = new RDeliveryConfig(); "" config.logicEnvironment = ; // 正式环境 config.appId = "your_app_id"; // 替换为实际的 APP ID config.appKey = "your_app_key"; // 替换为实际的 APP Key config.userId = "user_123"; config.deviceId = "device_456"; config.language = "zh-CN"; config.appVersion = "1.0.0"; config.osVersion = "4.0.0"; config.bundleId = "com.example.myapp"; 

// 设置日志回调 let logOutput = (level: number, log: string) => { hilog.info(0x0000, 'ShiplyLog', '%{public}s', log); }; // 设置数据初始化完成回调 RDelivery.ExpectOnLocalDataInitComplete((error_code: number) => { if (error_code === 0) { console.log('SDK 初始化成功 '); } else { console.error('SDK 初始化失败 :', error_code); } }); // 获取应用上下文和文件目录 let context = getContext(this) as common.UIAbilityContext; let filesDir = context.filesDir; // 启动 SDK RDelivery.SdkStart(filesDir, config, logOutput); 

#### **2.** 拉取配置 

// 拉取全量配置 let customProperties = { userLevel: 5, region: "beijing" }; RDelivery.RequestFullRemoteData(customProperties, (error_code: number, configList: Array<RDeliveryData>) => { if (error_code === 0) { configList.forEach((config) => { console.log(` 配置项 : ${config.key}, 值 : ${config.value}`); }); } }); 

// 按场景拉取配置 let sceneId = 100780; RDelivery.RequestBatchRemoteDataByScene(sceneId, customProperties, (error_code, configList) => { 

// 处理配置数据 }); 

#### **3.** 读取配置 

// 同步读取单个配置 const config = RDelivery.SyncGetRDeliveryDataByKey("feature_switch"); if (config) { console.log(` 配置值 : ${config.value}`); console.log(` 开关状态 : ${config.switchState}`); } 

// 异步读取配置 RDelivery.GetRDeliveryDataByKey("user_config", (errorCode, data) => { if (errorCode === 0 && data) { console.log(` 配置内容 : ${data.value}`); } }); 

// 读取所有配置 const allConfigs = RDelivery.SyncGetRDeliveryAllDataMap(); allConfigs.forEach((config, key) => { console.log(`${key}: ${config.value}`); }); 

#### **4.** 用户和环境切换 

// 切换用户 RDelivery.SwitchUserId("new_user_id", (error_code) => { if (error_code === 0) { // 切换成功,重新拉取配置 RDelivery.RequestFullRemoteData({}, (error_code, configList) => { // 处理新用户的配置 }); } }); // 切换环境 RDelivery.SwitchEnvironment("test", (error_code) => { if (error_code === 0) { // 环境切换成功 console.log(' 已切换到测试环境 '); } }); 

### 资源发布功能 

#### **1.** 初始化资源中心 

import { ResHub, ResHubParam } from '@ohos/shiply' 

// 创建参数对象 let param: ResHubParam = new ResHubParam(); param.appVersion = "1.0.0"; param.deviceType = "Phone"; param.systemVersion = "4.0.0"; param.qimei = "device_unique_id"; param.isDebugPackage = false; // 生产环境设为 false param.callbackOnMainThread = true; 

// 设置存储路径 let context = getContext(this) as common.UIAbilityContext; let filesDir = context.filesDir; param.resConfigStoragePath = filesDir + "/reshub/config"; param.resStoragePath = filesDir + "/reshub/resource"; 

// 设置日志回调 let logger = (level: number, log: string) => { hilog.info(0x0000, 'ResHubLog', '%{public}s', log); }; // 初始化资源中心 ResHub.initResHubCenter( param, "your_app_id", "your_app_key", "online", // 正式环境 logger ); 

#### **2.** 加载资源 

// 异步加载资源(锁定版本) let resId = "my_resource_001"; let progressCallback = (progress: number) => { console.log(` 下载进度 : ${progress}%`); }; let completionCallback = (success: boolean, error: ResHubError, resModel: ResHubModel) => { if (success) { console.log(` 资源加载成功 : ${resModel.localPath}`); console.log(` 资源 MD5: ${resModel.md5}`); // 使用资源文件 useResource(resModel.localPath); } else { console.error(` 资源加载失败 : ${error.code}`); } }; 

ResHub.loadWithId(resId, progressCallback, completionCallback); 

// 同步获取最新资源 let resModel = ResHub.latestResWithId(resId, true); if (resModel) { console.log(` 本地资源路径 : ${resModel.localPath}`); } 

#### **3.** 资源管理 

// 加载最新资源 ResHub.loadLatestWithId(resId, progressCallback, completionCallback); 

// 加载实时最新资源 ResHub.loadRealtimeLatestWithId(resId, progressCallback, completionCallback); // 获取资源配置信息 ResHub.fetchResConfigWithId(resId, (success, error, resModel) => { if (success) { console.log(` 资源版本 : ${resModel.version}`); console.log(` 资源大小 : ${resModel.size} bytes`); } }); // 删除指定资源 ResHub.deleteWithId(resId); // 清空所有资源 ResHub.deleteAll(); 

## 最佳实践 

### **1.** 初始化时机 

建议在应用启动时尽早初始化 SDK ,通常在 `UIAbility` 的 `onCreate` 方法中进行: 

export default class EntryAbility extends UIAbility { onCreate(want: Want, launchParam: AbilityConstant.LaunchParam) { // 初始化 Shiply SDK this.initShiplySDK(); } private initShiplySDK() { // SDK 初始化代码 } } 

### **2.** 错误处理 

一 // 统 错误处理函数 function handleShiplyError(errorCode: number, operation: string) { switch (errorCode) { case 0: console.log(`${operation} 成功 `); break; case -1: console.error(`${operation} 网络错误 `); break; case -2: console.error(`${operation} 参数错误 `); break; default: console.error(`${operation} 未知错误 : ${errorCode}`); } } 

### **3.** 配置缓存策略 

// 设置配置更新策略 config.updateStrategy = RDUpdateStrategy.SdkInit | RDUpdateStrategy.EnterForceground; config.updateInterval = 3600; // 1 小时更新一次 

### **4.** 资源预加载 

// 应用启动时预加载关键资源 const criticalResources = ["splash_image", "main_config", "user_guide"]; 

criticalResources.forEach(resId => { ResHub.loadWithId(resId, (progress) => {}, // 静默加载 (success, error, resModel) => { if (success) { console.log(` 预加载成功 : ${resId}`); } } ); }); 

## 常见问题解答 

### **Q1: SDK** 初始化失败怎么办? 

**A** : 检查以下几点: 

1. 确认 APP ID 和 APP Key 是否正确 

2. 检查网络权限是否已添加 

3. 确认设备网络连接正常 

4. 查看日志输出获取详细错误信息 

### **Q2:** 配置拉取失败如何处理? 

**A** : 可能的原因和解决方案: 

1. 网络问题 : 检查网络连接,重试请求 

2. 认证失败 : 验证 APP ID 和 APP Key 

3. 参数错误 : 检查自定义属性格式是否正确 

4. 服务器错误 : 联系技术支持 

### **Q3:** 资源下载速度慢怎么优化? 

- **A** : 优化建议: 

   1. 使用资源预加载策略 

   2. 合理设置资源更新策略 

   3. 压缩资源文件大小 

   4. 使用 CDN 加速 

## 故障排除 

### 日志调试 

启用详细日志输出: 

// 详细日志回调 let detailedLogger = (level: number, log: string) => { const logLevels = ['VERBOSE', 'DEBUG', 'INFO', 'WARN', 'ERROR']; const levelName = logLevels[level] || 'UNKNOWN'; console.log(`[${levelName}] ${log}`); 

// 可以将日志写入文件用于调试 writeLogToFile(`[${levelName}] ${log}`); }; 

### 网络问题诊断 

// 网络连接检查 import connection from '@ohos.net.connection'; 

function checkNetworkConnection() { connection.getDefaultNet().then((netHandle) => { connection.getNetCapabilities(netHandle).then((netCapabilities) => { if 

(netCapabilities.hasCapability(connection.NetCap.NET_CAPABILITY_INTERNET)) { console.log(' 网络连接正常 '); 

} else { console.log(' 网络连接异常 '); } }); }); } 

### 常见错误码处理 

function handleCommonErrors(errorCode: number, context: string) { switch (errorCode) { case 0: return ' 操作成功 '; case -1: return ' 网络连接失败,请检查网络设置 '; case -2: return ' 参数错误,请检查传入参数 '; case -3: return 'SDK 未初始化或初始化失败 '; case -4: return ' 请求的资源或配置不存在 '; case -5: return ' 文件校验失败,可能文件已损坏 '; case -6: return ' 存储空间不足,请清理设备存储 '; case -7: return ' 权限不足,请检查应用权限设置 '; case -8: return ' 配置解析失败,请联系技术支持 '; case -9: return ' 服务器错误,请稍后重试 '; case -10: return ' 请求超时,请检查网络连接 '; default: return ` 未知错误 (${errorCode}) ,请联系技术支持 `; } } 

## 技术支持 

#### 如果遇到无法解决的问题,请通过以下方式获取技术支持: 

   - 官方文档 : https://shiply.tencent.com/docs 

   - 在线客服 : 登录 Shiply 管理平台,点击右下⻆客服图标 

- 提交问题时,请提供以下信息: 

#### SDK 版本号 

- 鸿蒙系统版本 

- 详细的错误日志 

- 问题复现步骤 

- 相关的代码片段 

## 版本更新日志 

### **v1.0.22 (2024-12-25)** 

- 新增资源预加载功能 

- 优化网络请求性能 

- 修复已知问题 

- 增强错误处理机制 

### **v1.0.21 (2024-12-01)** 

- 支持多环境切换 

- 新增配置变化监听 

- 优化资源下载策略 

- 修复内存泄漏问题
