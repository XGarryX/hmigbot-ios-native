# GStarSDKLib 对外接口参考 

## 1. 接口 

### 1.1 GStarSDK 

##### **`1.1.1 static get shared(): GStarSDK`** 

SDK 单例实例,一般业务侧以静态方法为主,按需使用。 

##### **`1.1.2 static get info(): GStarSDKInfo`** 

返回 SDK 版本与发版说明等元信息。 

##### **`1.1.3 static initSDK(context: common.UIAbilityContext, params: GStarSDKInitParams): Promise<void>`** 

完成 SDK 初始化;需在用户同意隐私政策等前置条件满足后调用。 

|参数|类型|说明|
|---|---|---|
|`context`|`common.UIAbilityContext`|UIAbility上下文,用于模块配置与窗口相关 能力|
|`params`|`GStarSDKInitParams`|证书与应用标识等初始化参数|

##### **`1.1.4 static updateCer(params: GStarSDKInitParams)`** 

在已初始化前提下刷新证书与客户信息;未完成初始化时调用无效果。 

|参数|类型|说明|
|---|---|---|
|`params`|`GStarSDKInitParams`|与 `initSDK` 相同结构|

##### **`1.1.5 static setWatermark(options: GSWatermarkOptions)`** 

#### 配置看图时的自定义水印;未完成初始化时调用无效果。 

|参数|类型|说明|
|---|---|---|
|`options`|`GSWatermarkOptions`|水印文案、几何与颜色等选项|

### 1.2 GSDrawViewController 

##### **`1.2.1 set onDrawClosed(callback: () => void)`** 

图纸关闭时的回调,用于关闭页面或导航回退等。 

|参数|类型|说明|
|---|---|---|
|`callback`|`() => void`|无参回调|

##### **`1.2.2 onBackPressed(): boolean`** 

在页面 `onBackPress` 中转发调用;返回 `true` 表示已消费返回事件。 

##### **`1.2.3 set privacyMode(privacyMode: boolean)`** 

是否启用隐私模式(如防截屏/录屏);默认 `true` ,宜在开图前设置。 

|参数|类型|说明|
|---|---|---|
|`privacyMode`|`boolean`|是否开启隐私模式|

### 1.3 GSDrawView 

由 SDK 提供的 ArkUI 自定义组件( `@Component struct` ),用于在业务页面中嵌入 浩辰 CAD 图纸视图;内部承载开图页面并保持全宽全高布局。 

##### **`1.3.1 filePath: string = ""`** 

待打开图纸的本地文件路径;业务侧应传入有效路径。 

##### **`1.3.2 controller: GSDrawViewController = new GSDrawViewController()`** 

与视图绑定的控制器,用于关闭回调、返回拦截与隐私模式等配置。 

## 2. 数据模型 

### 2.1 GStarSDKInitParams 

初始化与更新证书时使用的参数集合: `applic` 为必选,其余按商务与网络环境选填。 

|字段|类型|说明|
|---|---|---|
|`applic`|`Uint8Array`|证书中的应用侧数据,必填|
|`customer`|`string`|可选,客户名称或标识字符串|
|`customerKey`|`Uint8Array`|可选,与客户标识配套的密钥数据;与 `customer` 成 对使用|
|`proxyUrl`|`string`|可选,HTTPS等网络请求的代理地址|

```
export interface GStarSDKInitParams {
  applic: Uint8Array
  customer?: string
  customerKey?: Uint8Array
  proxyUrl?: string
}
```

### 2.2 GStarSDKInfo 

通过 `GStarSDK.info` 获取的当前 SDK 版本概况及历史版本列表入口。 

|字段|类型|说明|
|---|---|---|
|`currentVersion`|`string`|当前对外展示的版本号字符串|
|`currentVersionCoe`|`number`|当前版本数值码(字段名与源码一|
|||致)|
|`versionList`|`GStarSDKVersionInfo[]`|历史版本条目数组|

```
export interface GStarSDKInfo {
  currentVersion: string
  currentVersionCoe: number
  versionList: GStarSDKVersionInfo[]
}
```

### 2.3 GStarSDKVersionInfo 

#### 描述单个发布版本的编号、说明与日期,供关于页或更新日志展示。 

|字段|类型|说明|
|---|---|---|
|`version`|`string`|该条目的版本号|
|`versionCode`|`number`|该条目的版本数值码,用于比较新旧|
|`versionDesc`|`string[]`|该版本的多条说明文案|
|`releaseDate`|`string`|发布日期字符串|

```
export interface GStarSDKVersionInfo {
  version: string
  versionCode: number
  versionDesc: string[]
  releaseDate: string
}
```

### 2.4 GSWatermarkOptions 

一 自定义水印的可选几何与样式;未传字段由 SDK 内部采用默认值(与源码实现 致)。 

|字段|类型|说明|
|---|---|---|
|`content`|`string`|水印文字内容,必填|
|`show`|`boolean`|是否显示水印;默认 `true`|
|`width`|`number`|水印单元宽度;未传时实现默认 `300`|
|`height`|`number`|水印单元高度;未传时实现默认 `300`|
|`textHeight`|`number`|文字字高;未传时实现默认 `20`|
|`xSpace`|`number`|起始X方向间距;默认 `0`|
|`ySpace`|`number`|起始Y方向间距;默认 `0`|
|`color`|`GSWatermarkColor`|文字颜色;未传时默认RGBA `(226,226,226,77)`|
|`angle`|`number`|旋转⻆,单位度;可选|

```
export interface GSWatermarkOptions {
  content: string
  show?: boolean
  width?: number
  height?: number
  textHeight?: number
  xSpace?: number
  ySpace?: number
  color?: GSWatermarkColor
  angle?: number
}
```

### 2.5 GSWatermarkColor 

#### 水印颜色,使用 RGBA 四个分量描述。 

|字段|类型|说明|
|---|---|---|
|`r`|`number`|红色分量|
|`g`|`number`|绿色分量|
|`b`|`number`|蓝色分量|
|`a`|`number`|透明度分量|

```
export interface GSWatermarkColor {
  r: number
  g: number
  b: number
  a: number
}
```
