# 浩辰 CAD 鸿蒙端 SDK 基础版使用指南 

最低支持 Harmony 版本:5.0.0 API12 

## 1. 开发基本流程 

### 1.1 注册应用并生成证书 

使用应用 bundleId(app.json5 中的 bundleName)、应用名(customer)、应用水印 图标给生成证书: 

`cert_key.ts` :证书信息 

`customer_3_GstarSDK.ts` :应用信息 

### 1.2 集成证书 

将证书存档至同 bundleId 的应用中 

### 1.3 获取并集成 SDK 

1. 从浩辰客服人员处获取 SDK 包:GStarSDKLib.har 

2. 将 GStarSDKLib.har 放置项目根目录下 

3. 在 DevEco 中打开 Terminal tab,调用命令: `ohpm install` 

   - `GStarSDKLib.har` 

4. 安装成功后在项目根目录的 `oh-package.json5` 看到如下配置则代表安装成 

   - 功: 

```
"dependencies": {
    "gstarsdklib": "file:GStarSDKLib.har"
}
```

参考文档:引用及管理共享包官方文档 

### 1.3 初始化 SDK 

- 在项目中集成 SDK 成功后,即可初始化 SDK,样例代码如下: 

```
import { GStarSDK } from 'gstarsdklib'
import { customer_key } from 'customer_3_GstarSDK';
import { applic } from 'cert_key';
```

`// EntryAblity` 中 `const context = this.context` 

`//` 组件中 `const context = this.getUIContext().getHostContext() as common.UIAbility GStarSDK.initSDK(context, { applic: applic, customer: "` 你的 `customer", customerKey: customer_key, })` 

SDK 证书流程需要访问网络,项目需在 entry/src/main/module.json5 中配置网 络访问权限 

`// module.json5 "requestPermissions": [ { "name": "ohos.permission.INTERNET", "reason": "$srting:auth_request_network_text", "usedScene": { "abilities": [ "EntryAbility" ], "when": "inuse" } } ] // string.json { "name": "auth_request_network_text", "value": "` 请求访问网络 `" }` 

#### 注意: 

初始化 SDK 内部会保存必要文件到沙盒,并访问网络进行证书验证。因此建 议初始化方法在用户同意隐私政策协议之后。 

初始化 SDK 成功后,SDK 会在应用的 hap/files/ 中新建一个文件夹 .gstarsdk 并保存绘图所需的必要文件。 

若展示文件列表,请过滤不显示此文件夹,更不要更改或删除文件夹及其中的 任何文件,否则会导致开图错误甚至失败。 

1.4 更新证书 

一 如果第 次初始化 SDK 的时候没有网络,会导致证书验证失败,从而无法开图。 

因此提供了一个独立接口用来更新证书,例如在网络重新连通后再次调用,即可发 起一次证书验证: 

```
GStarSDK.updateCer({
   applic: applic,
   customer: "GstarSDK",
   customerKey: customer_key,
})
```

#### 注意: 

GStarSDK.updateCer 必须在初始化成功之后调用,否则会出现崩溃 

### 1.5 自定义水印 

一 V1.0.3 版本支持配置 层新的自定义水印。水印支持配置项如下: 

`/** *` 水印设置选项 `*/ export interface GSWatermarkOptions { //` 水印内容 `content: string //` 是否生效,默认为 `true show?: boolean //` 水印宽度,默认为 `50 width?: number //` 水印高度 `,` 默认为 `50 height?: number //` 水印内容字高,默认为 `50 textHeight?: number //` 水印起始位置 `X` 坐标,默认 `0 xSpace?: number //` 水印起始位置 `Y` 坐标,默认 `0 ySpace?: number //` 水印颜色,默认( `226` , `226` , `226` , `77` ) `color?: GSWatermarkColor //` 旋转⻆度,默认 `-30` 度 `(` 顺时针 `30` 度 `)` ,单位度 `angle?: number } //` 水印颜色 `export interface GSWatermarkColor { r: number g: number b: number` 

```
  a: number
}
```

#### 使用方法: 

```
// SettingsPage.ets
GStarSDK.setWatermark({
      content: this.watermarkText,
      show: this.watermarkEnabled,
      width: Number(this.watermarkWidth),
      height: Number(this.watermarkHeight),
      textHeight: Number(this.watermarkTextHeight),
      xSpace: Number(this.watermarkX),
      ySpace: Number(this.watermarkY),
      color: {r: Number(this.watermarkColorR), g: Number(this.watermarkC
      angle: Number(this.watermarkAngle)
    })
```

### 1.6 开图 

为了方便使用,浩辰 CAD 鸿蒙端 SDK 未使用页面的方式提供开图,使用组件 GSDrawView 即可实现开图。 

##### 1.6.1 GSDrawView 

GSDrawView 是开图基础组件,需要传递文件路径 `filePath: string` 、开图控 制器 `controller: GSDrawViewController` 两个参数。 

#### 注意: 

理论上 GSDrawView 可以实现任何大小,但目前代码是仅针对全屏进行处理 的,因此在使用上需全屏展示。 

##### 1.6.2 GSDrawViewController 

一 GSDrawViewController 用来管理回调,并提供 定的方法允许外部调用。 

```
export class GSDrawViewController {
  /**
```

`*` 图纸关闭了,需要外部监听一下,用来退出页面等操作。 `*/ set onDrawClosed(callback: () => void)` 

```
  /**
```

`*` 系统返回按钮被点击 `/` 屏幕边缘滑动返回触发 

`* @returns` 是否拦截 

```
   */
  onBackPressed(): boolean
```

`/** *` 设置隐私模式(即防截屏 `/` 录屏),默认是 `true *` 开图过程中设置无效,在初始化成功后,开图之前配置 `*/ set privacyMode(privacyMode: boolean) }` 

##### 1.6.3 沉浸式页面访问 

鸿蒙推荐使用沉浸式页面访问,因此本 SDK 看图 UI 也是在此基础上开发的。 

如果源项目已经是全局沉浸式,则无需做特殊处理。 

如果源项目未使用全局沉浸式,需在页面展示的时候调用 

`mainWindow.setWindowLayoutFullScreen(true)` 来将页面临时设置为沉浸 式,并在退出的时候设置为 `false` 。 

##### 1.6.4 使用样例 

#### Router 页面管理方式: 

```
import { GSDrawView, GSDrawViewController } from "gstarsdklib"
export interface RouterDrawPageParams {
  filePath: string
}
@Entry
@Component
export struct RouterDrawPage {
  filePath: string = ""
  drawViewController: GSDrawViewController = new GSDrawViewController()
  aboutToAppear(): void {
    const params = this.getUIContext().getRouter().getParams() as Router
    this.filePath = params.filePath
    this.drawViewController.onDrawClosed = () => {
      this.getUIContext().getRouter().back()
  onBackPress(): boolean | void {
    return this.drawViewController.onBackPressed()
  build() {
    Stack() {
      GSDrawView({
        filePath: this.filePath,
        controller: this.drawViewController
      })
        .width('100%')
        .height('100%')
    }
  }
}
```

#### Navigation 页面管理方式 

import { GSDrawView, GSDrawViewController } from "gstarsdklib"
export const NavigationDrawPageName = "NavigationDrawPage"
@Builder
export function NavigationDrawPageBuilder() {
  NavigationDrawPage()
}
@Component
export struct NavigationDrawPage {
  filePath: string = ""
  drawViewController: GSDrawViewController = new GSDrawViewController()
  navPathStack: NavPathStack = new NavPathStack();
  aboutToAppear(): void {
    this.drawViewController.onDrawClosed = () => {
      this.navPathStack.pop()
    }
  }
  onBackPress(): boolean | void {
    return this.drawViewController.onBackPressed()
  }
  build() {
    NavDestination() {
      GSDrawView({
        filePath: this.filePath,
        controller: this.drawViewController
      })
        .width('100%')
        .height('100%')
    }
    .onReady((context) => {

```
      this.filePath = context.pathInfo.param as string;
      this.navPathStack = context.pathStack
    })
    .onBackPressed(() => {
      return this.drawViewController.onBackPressed()
    })
    .hideTitleBar(true)
  }
}
```
