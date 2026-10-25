# HarmonyOS uniMap 室内地图集成文档 

文档信息 

文档版本 : 1.0 

最低适配版本 : HarmonyOS 5.0.1 

目录 

概述 

环境准备 

集成步骤 

代码实现 

常见问题 

附录 

概述 

本文档介绍如何在 HarmonyOS Next 应用中集成 DXIntegratedLibrary.har 库实现 LiteMap 室内地图功能。该库提供了 室内地图展示、导航等核心功能,最低适配 HarmonyOS 5.0.1 版本。 

# 环境准备 

开发工具 : DevEco Studio 最新版本 SDK: HarmonyOS Next SDK 目标 设备 : 支持 HarmonyOS 5.0.1 及以上的设备 依赖库 : DXIntegratedLibrary.har 

# 集成步骤 

# 3.1 添加依赖库 

将 DXIntegratedLibrary.har 文件复制到项目的 libs 目录下 在 oh- 

package.json5 文件中添加依赖 : 

"dependencies": { 

'dxintegratedlibrary': "file:./lib/DXIntegratedLibrary.har" 

} 

# 这里的 lib 就是存放 har 文件目录名称 

# 3.2 初始化依赖库 

运行 ohpm install 

代码实现 

4.1 创建 ViewModel 

import {DXMapMainPageInterface} from "dxintegratedlibrary" 

```arkts
import { promptAction } from "@kit.ArkUI"; 
```

@ObservedV2 

export class DXIntegratedIndexModel implements DXMapMainPageInterface{ 

@Trace showMapview = true; 

onWebViewIndoorBuildingLoaded(_: string): void { 

} 

onWebViewLoadFailed(errorMsg: string): void { 

promptAction.showToast({ 

message: errorMsg 

}) this.showMapview = false; 

} 

onMapViewExit(): void { 

console.info("onMapViewExit") this.showMapview = false; 

} 

} 

# 4.2 实现地图页面 

@Local vm:DXIntegratedIndexModel = new DXIntegratedIndexModel(); 

// 这里 buildingId 如果传空,会根据 GPS 定位结果来弹出建筑列表 

DXMapMainPage({ 

token: " 同大希科技获取 ", serverUrl: " 基础 server 地址 ", 

buildingId: " 建筑 ID", 

mainPageInterface: this.vm 

}) 

.width('100%') 

.height('100%') 

# 常见问题 

Q1: 地图加载失败怎么办? 

检查 token 是否有效 

检查网络连接是否正常 

检查 buildingId 是否正确 

查看 onWebViewLoadFailed 返回的错误信息 

Q2: 如何更换建筑 ID ? 

修改 DXMapMainPage 组件中的 buildingId 参数 

确保该建筑 ID 在您的账户下有效 

附录 DXMapMainPage 参数说明 

参数名 

类型 必填 说明 

token 

string 

是 

开发者 token ,用于鉴权 

serverUrl 

string 

是 

# 配置服务器地址 

buildingId string 是 

要加载的建筑 ID 

mainPageInterface DXMapMainPageInterface 

是 

回调接口实现 

注意事项 : 

请确保使用的 token 和 buildingId 有效 

正式发布前请替换测试 token 为正式环境 token 最低适配版本为 HarmonyOS 5.0.1 ,请确保设备兼容性
