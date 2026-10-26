## PLVWebSDK 

## 简介 

PLVWebSDK/Users/mac/Downloads/polyv-harmony-webviewdemo-master/README.md 项目从属于广州易方信息科技股份有限公 司,对保利威云直播、云点播系列产品的直播、回放观看做了良好的 适配,极大优化了用户的观看体验,并支持浮窗播放等扩展功能,也 可作为其他网页的展示容器。 

# 本项目包含功能如下: 

- 支持基础 Web 功能 

- 支持应用内浮窗播放 

- 支持系统级浮窗播放 

- 支持悬浮窗手势拖动 

- 支持视频全屏播放 

- 支持 feed 流 

# ## 下载安装 

``` 

ohpm install plvwebsdk 

``` 

OpenHarmony ohpm 环境配置等更多内容,请参考 [ 如何安装 OpenHarmony ohpm 包 ](https://gitee.com/openharmony-tpc/ docs/blob/master/OpenHarmony_har_usage.md) 

# ## 需要权限 

``` 

ohos.permission.INTERNET 

ohos.permission.GET_NETWORK_INFO 

``` 

# ## 使用示例 

### 基础使用 

**1 、绑定 WindowStage** 

首先需要在 Ability 中为 PLVWebViewWindowManager 绑定用到 windowStage 

```ts 

onWindowStageCreate(windowStage: window.WindowStage): void { 

// Main window is created, set main page for this ability 

PLVLogger.info(TAG, 'Ability onWindowStageCreate'); 

// demo 核心代码 

PLVWebViewWindowManager.setWindowStage(windowStage) 

windowStage.loadContent(CONTENT, new LocalStorage(), (err, data) => { 

if (err.code) { 

PLVLogger.info(TAG, 'Failed to load the content. Cause: ' + 

JSON.stringify(err) ?? ''); 

return; 

} 

PLVLogger.info(TAG, 'Succeeded in loading the content. Data: ' + JSON.stringify(data) ?? ''); 

}); 

} 

``` 

**2 、使用 PLVWeb 组件 ** 

```ts 

@Entry 

@Component 

struct PLVWebPage { 

@StorageLink('inputWebConfig') config: PLVWebViewConfig = new PLVWebViewConfig().setUrl("") 

@State controller: PLVWebController = new PLVWebController({ config: this.config!! }) 

aboutToAppear(): void { 

this.controller.registerHandler(" 自定义事件 ", (data: string) => { 

// 监听自定义事件的处理 

}) 

this.controller.callHandle(" 发送原生事件 ", "xxx", () => { 

# // 发送原生事件 

# }) 

this.controller.registerCustomerContainEvent({ 

onShare: () => { 

# // 监听到 onShare 事件时的操作 

return true // return true 表示拦截掉分享事件 false 就继续由 sdk 往下 执行 

} 

}) 

} 

build() { 

Column() { 

PLVWeb({ controller: this.controller }) 

} 

.width(PLVCommonConstants.FULL_PERCENT) 

} 

onBackPress(): boolean | void { 

if (this.controller.accessBackward()) { 

this.controller.backward() 

return true 

} 

return false 

} 

} 

``` 

` 注意该组件需要放在一个单独的 pages 页面中,因为创建的 Web 窗口 需要一个单独 page 页面 ` 

**3 、 Demo 使用 ** 

```ts 

@Entry(storage) 

@Component 

struct PLVInputPage { 

inputUrl: string = 'https://www.polyv.net' 

config: PLVWebViewConfig = new PLVWebViewConfig().setUa("Android" + PLVUAConfig.defaultUA) .setUrl(this.inputUrl) 

.setAllowFloatingWindow(true) 

build() { 

Stack({ alignContent: Alignment.Top }) { 

... 

Button(" 打开 Web") 

.margin(24) 

.onClick(() => { 

if (!PLVWebViewWindowManager?.getWebViewWindow()) { 

this.config.setUrl(this.inputUrl) 

AppStorage.setOrCreate('inputWebConfig', this.config); 

// 为 webWindow 绑定一个 page 页面,用于窗口的显示 

// true 表示初始化后立刻打开 webWindow 

PLVWebViewWindowManager?.initWindow(true, "pages/ PLVWebPage") 

return 

} 

}) 

} 

.... 

} 

} 

``` 

为 PLVWebViewWindowManager 绑定了 WindowStage 后,可以通过 `PLVWebViewWindowManager?.initWindow(true, "pages/ PLVWebPage")` 

来进行初始化化,如果传入参数 true 时,当初始化后立刻展示 WebWindow ,也可以选择传入 false ,初始化后不立刻展示 WebWindow 

再通过 `PLVWebViewWindowManager.showWebViewWindow()` 来 进行展示 

### Feed 流使用 

# 1 、使用 Feed 流控件 

```ts 

build() { 

Column() { 

PLVFeedWeb({ 

data: this.data, // 拆入的 feed 数据 onLoadMore: this.onLoadMore, // 加载更多时的回调 onRefresh: this.onRefresh, // 刷新时的回调 

index: this.index 

}) 

} 

.width('100%') 

} 

# // 回退时的处理 

onBackPress(): boolean | void { 

let controller = this.data.getData(this.index) 

if (controller.accessBackward()) { 

controller.backward() 

return true 

} 

return false 

} 

``` 

# 2 、设置需要加载的数据 

```ts 

private onLoadMore?: () => Promise<string> = () => { return new Promise<string>((resolve, reject) => { setTimeout(() => { 

resolve('') 

let urls: string[] = [ 

'https://www.polyv.net/' 

] 

let config: PLVWebViewConfig = new PLVWebViewConfig() 

.setUa("Android" + 

for (let element of urls) { 

let tempConfig: PLVWebViewConfig = config.clone().setUrl(element) 

let controller: PLVWebController = new PLVWebController({config: tempConfig}) 

this.data.pushData(controller) 

} 

}, 3000); 

}); 

} 

private onRefresh?: () => Promise<string> = () => { 

return new Promise<string>((resolve, reject) => { 

setTimeout(() => { 

resolve("success") 

}, 1000) 

}) 

} 

``` 

# 3 、设置需要加载的数据 

```ts 

@Entry 

@Component 

struct PLVFeedWebPage { 

@StorageLink('inputWebConfigFeed') listUrl: ArrayList<string> = new ArrayList() 

@State data: PLVFeedData = new PLVFeedData() 

@State index: number = 0 

private urls: string[] = [ 

'https://www.polyv.net/', 

'https://www.polyv.net/' 

] 

... 

aboutToAppear(): void { 

let config: PLVWebViewConfig = new PLVWebViewConfig() 

.setUa("Android" + PLVUAConfig.defaultUA).setSupportAutoFloating(false).setAllowFloatingWindow(true) 

if (this.listUrl.length > 0) { 

for (let item of this.listUrl) { 

console.info("===" + item) 

let tempConfig: PLVWebViewConfig = config.clone().setUrl(item) 

let controller: PLVWebController = new PLVWebController({config: tempConfig}) 

this.data.pushData(controller) 

} 

} else { 

for (let url of this.urls) { 

let tempConfig: PLVWebViewConfig = config.clone().setUrl(url) 

let controller: PLVWebController = new PLVWebController({config: tempConfig}) 

this.data.pushData(controller) 

} 

} 

} 

} 

``` 

接下来打开这个 PLVFeedWebPage 就可以了 

# ## 功能说明 

### PLVWebViewConfig 

**1. 设置 UA** 

当前可以通过下面的方式来设置需要的 UA 

`PLVWebViewConfig().setUa("Android" + PLVUAConfig.defaultUA)` 

注意:如果需要到 Saas 页面的小窗功能的情况,必须在 UA 中带上 Android 和 PLVUAConfig.defaultUA 字段 

**2. 设置 url** 

可以通过下面的方式来设置需要加载的 url 

PLVWebViewConfig().setUrl(" 需要加载的 url") 

**3. 设置是否允许小窗悬浮 ** 

可以通过下面的方式来设置是否允许开启小窗功能,默认是开启的, 如不需要可以设置为 false 

`PLVWebViewConfig().setAllowFloatingWindow(true)` 

### 自定义注册事件 

# 当前 SDK 内部已经注册好与前端页面通信的事件,当接入 sdk 后就能直 接使用这些事件。 

SDK 也支持注册自定义事件,可以通过下面的方式来进行注册 

```ts 

this.controller.registerHandler(" 自定义事件 ", (data: string) => { 

// 监听自定义事件的处理 

# }) 

this.controller.callHandle(" 发送原生事件 ", "xxx", () => { 

// 发送原生事件 

# }) 

``` 

如果需要监听 / 拦截 SDK 内部已经实现了的事件,可以通过下面的方式 继续监听 / 拦截,这里以 onShare 事件为例子,如果需要监听 / 拦截其 他事件可以仿照这里来完成 

```ts 

this.controller.registerCustomerContainEvent({ 

onShare: () => { 

# // 监听到 onShare 事件时的操作 

return true // return true 表示拦截掉分享事件 false 就继续由 sdk 往下 执行 

# } 

# }) 

```
