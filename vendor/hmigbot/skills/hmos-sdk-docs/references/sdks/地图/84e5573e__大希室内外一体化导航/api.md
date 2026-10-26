# DXMapSDK 接口文档 

DXMapMainPage 组件接口文档 

组件概述 

DXMapMainPage 是一个地图主页面组件,用于显示室内地图和导航 功能。 基本用法 

DXMapMainPage({ 

token: "your_access_token", serverUrl: "baseUrl", 

buildingId: "getFromDaXi", 

mainPageInterface: this.VM 

}) 

.width('100%') .height('100%') 

参数说明 配置参数 参数名 类型 必填 说明 token 

string 

是 

访问令牌,用于身份验证 

serverUrl 

string 

是 

# 数据服务接口地址 

buildingId 

string 

是 

建筑 ID 

mainPageInterface 

object 

是 

回调接口对象,包含事件处理方法 

回调接口 (mainPageInterface) 

回掉接口对象需要遵循 DXMapMainPageInterface 协议 

export class DXIntegratedIndexModel implements DXMapMainPageInterface {} 

回调接口对象需要实现以下方法: 

onWebViewIndoorBuildingLoaded 

说明 

# 当地图室内建筑数据加载完成时触发 

方法签名 

onWebViewIndoorBuildingLoaded(buildingId: string): void 

参数 

buildingId (string): 加载完成的建筑物 ID 

示例 

onWebViewIndoorBuildingLoaded(buildingId: string): void { // 处理建筑加载完成逻辑 

console.log(` 建筑 ${buildingId} 加载完成 `); 

} 

onWebViewLoadFailed 

说明 

# 当地图加载失败时触发 

方法签名 

onWebViewLoadFailed(errorMsg: string): void 

参数 

errorMsg (string): 错误信息描述 

示例 

onWebViewLoadFailed(errorMsg: string): void { 

promptAction.showToast({ 

message: errorMsg 

}) 

this.showMapview = false; 

} 

onMapViewExit 

说明 当用户退出地图视图时触发 方法签名 

onMapViewExit(): void 

示例 

onMapViewExit(): void { console.info("onMapViewExit") 

} 

完整实例 

// 在 ArkTS/TypeScript 中的使用示例 

@Entry 

@Component 

struct MapPage { 

@State showMapview: boolean = true; 

# // 创建回调接口对象 

VM: MapCallbacks = new MapCallbacks(); 

aboutToAppear() { 

this.VM.setContext(this); 

} 

build() { 

Column() { 

if (this.showMapview) { 

DXMapMainPage({ 

token: "token", 

serverUrl: "https://map1a.daxicn.com/proxyDataEngine/ appConfig", 

buildingId: "building id", 

mainPageInterface: this.VM 

}) 

.width('100%') 

.height('100%') 

} 

} 

} 

} 

# // 回调接口实现类 

class MapCallbacks { private context: MapPage | null = null; 

setContext(ctx: MapPage) { 

this.context = ctx; 

} 

```arkts
onWebViewIndoorBuildingLoaded(buildingId: string): void { console.log(` 建筑 ${buildingId} 加载完成 `); } 
```

onWebViewLoadFailed(errorMsg: string): void { promptAction.showToast({ 

message: errorMsg 

# }) 

if (this.context) { this.context.showMapview = false; 

} 

} 

onMapViewExit(): void { 

console.info("onMapViewExit") if (this.context) { this.context.showMapview = false; 

} 

} 

}
