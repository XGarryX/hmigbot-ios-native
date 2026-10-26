# **YILI LingTongCV HM SDK 接口文档** 

版本号:1.0.2 

更新日期:2026-07-10 

SDK名称:YILI LingTongCV HM SDK 

SDK包名: `yili-lingtongcv-hm-sdk` 

入口文件: `Index.ets` 

本文档用于 SDK 上架时提交接口说明,覆盖接口名称、调用方式、请求参数、返回参数、调用示例和错误码说明。当前版本 SDK 提供设备本地拍摄、拼接、结果保存和结果回调能力。 

## **一、集成方式** 

SDK 1.0.0 已发布至 OHPM 中心仓 并验证可装,推荐使用 OHPM 远程集成;离线或需定制 har 时可改用本地 HAR。两种 方式二选一,不要在同一工程中混用 `file:` 引用与版本号依赖。 

### **1. OHPM 集成(推荐)** 

```
ohpm i yili-lingtongcv-hm-sdk
```

或在使用 SDK 的模块 `oh-package.json5` 中声明版本号依赖: 

```
{
  "dependencies": {
    "yili-lingtongcv-hm-sdk": "^1.0.0"
  }
}
```

### **2. 本地 HAR 集成** 

将 `yili_sdk.har` 放入宿主工程 `libs/` 目录,并在使用 SDK 的模块 `oh-package.json5` 中添加依赖: 

```
{
  "dependencies": {
    "yili-lingtongcv-hm-sdk": "file:./libs/yili_sdk.har"
  }
}
```

> **注意:** `file:` 后只能跟本地路径(目录或 `.har` 文件),不可写成 `"file:^1.0.0"` 这类版本号;且引用的 har 文件必 须真实存在,否则 `ohpm install` 会报 `Fetch local file package error` 。多模块工程中 `file:` 路径相对当前 `ohpackage.json5` 所在目录计算。 

## **二、导入方式** 

```
import {
  YiliSDK,
  YiliSDKConfig,
  YiliSDKParams,
  YiliSDKResult,
  YiliSDKResultCallback
} from 'yili-lingtongcv-hm-sdk';
import 'yili-lingtongcv-hm-sdk/src/main/ets/pages/GuidePage';
import 'yili-lingtongcv-hm-sdk/src/main/ets/pages/CameraSDK_V2';
import 'yili-lingtongcv-hm-sdk/src/main/ets/pages/AlgorithmResult';
```

#### 说明:宿主应用建议显式导入 SDK 页面,确保命名路由可被正确注册。 

## **三、权限说明** 

SDK HAR 中声明以下权限,运行时由宿主应用调用 `YiliSDK.requestPermissions()` 申请: 

|**权限名称**|**使用目的**|
|---|---|
|`ohos.permission.CAMERA`|用于相机预览、拍照和采集拼接所需图片|
|`ohos.permission.MICROPHONE`|用于视频拼接模式下录制视频声音|
|`ohos.permission.READ_MEDIA`|用于读取相册或媒体库中的图片、视频素材|
|`ohos.permission.WRITE_MEDIA`|用于将拼接结果保存到系统相册或媒体目录|

## **四、接口总览** 

|**接口名称**|**调用方式**|**说明**|
|---|---|---|
|`YiliSDK.init(context, config?)`|静态方法|初始化 SDK|
|`YiliSDK.isInitialized()`|静态方法|判断 SDK 是否已初始化|
|`YiliSDK.requestPermissions()`|静态异步方法|申请 SDK 所需权限|
|`YiliSDK.open(params?)`|静态方法|打开 SDK 页面|
|`YiliSDK.setResultCallback(callbac`|静态方法|注册或取消结果回调|
|`k)`|||
|`YiliSDK.getWorkDir()`|静态方法|获取 SDK 工作目录|
|`YiliSDK.onForeground()`|静态方法|宿主前台生命周期透传|
|`YiliSDK.onBackground()`|静态方法|宿主后台生命周期透传|

## **五、类型定义** 

### **1.** **`YiliSDKConfig`** 

```
export interface YiliSDKConfig {
  workDirName?: string;
}
```

|**字段**|**类型**|**必填**|**说明**|
|---|---|---|---|
|`workDirName`|`string`|否|SDK 工作目录名称,位于宿|
||||主应用 `filesDir`下,默认|
||||值为 `yiliPhoto`|

### **2.** **`YiliSDKParams`** 

```
export interface YiliSDKParams {
  initialMode?: 'single' | 'multi' | 'video';
  skipGuide?: boolean;
  extras?: Record<string, string>;
}
```

|**字段**|**类型**|**必填**|**说明**|||
|---|---|---|---|---|---|
|`initialMode`|`'single' \|'multi' \|'video'`|否|初始模式。 `single`表示单 张拍摄, `multi` 表示多图拼接, `video`表示视频 抽帧拼接|
|`skipGuide`|`boolean`|否|是否跳过引导 页,直接进入拍 摄页|||
|`extras`|`Record<string,` `string>`|否|预留透传参数, 当前版本不消费 该字段|||

### **3.** **`YiliSDKResult`** 

```
export interface YiliSDKResult {
  success: boolean;
  imageUris: string[];
  imagePaths: string[];
  mode?: string;
}
```

|**字段**|**类型**|**说明**|
|---|---|---|
|`success`|`boolean`|是否成功返回结果|
|`imageUris`|`string[]`|`file://`格式结果 URI 列表|
|`imagePaths`|`string[]`|宿主应用沙箱中的结果文件绝对路径 列表|
|`mode`|`string`|拍摄或拼接模式,通常为 `single` 、 `multi`或 `video`|

### **4.** **`YiliSDKResultCallback`** 

```
export type YiliSDKResultCallback = (result: YiliSDKResult) => void;
```

## **六、接口详情** 

### **1. 初始化 SDK** 

接口名称: `YiliSDK.init` 

调用方式: 

```
YiliSDK.init(context: Context, config?: YiliSDKConfig): void
```

#### 请求参数: 

|**参数**|**类型**||**必填**|**说明**|
|---|---|---|---|---|
|`context`|`Context`|是||宿主应用 Ability 上下文|
|`config`|`YiliSDKConfig`|否||初始化配置|

返回参数:无。 

调用说明: 

1. 建议在宿主 `UIAbility.onCreate` 中调用。 

2. 必须在调用 `open()` 、 `requestPermissions()` 、 `getWorkDir()` 前完成初始化。 

3. 重复初始化会被 SDK 忽略。 

调用示例: 

```
YiliSDK.init(this.context, { workDirName: 'yiliPhoto' });
```

### **2. 判断初始化状态** 

接口名称: `YiliSDK.isInitialized` 

调用方式: 

```
YiliSDK.isInitialized(): boolean
```

#### 请求参数:无。 

#### 返回参数: 

||**类型**|**说明**|
|---|---|---|
|`boolean`||`true`表示 SDK 已初始化, `false`表示 SDK 未初始化|

#### 调用示例: 

```
if (!YiliSDK.isInitialized()) {
  YiliSDK.init(this.context);
}
```

### **3. 申请权限** 

接口名称: `YiliSDK.requestPermissions` 

#### 调用方式: 

```
YiliSDK.requestPermissions(): Promise<boolean>
```

#### 请求参数:无。 

#### 返回参数: 

||**类型**|**说明**|
|---|---|---|
|`Promise<boolean>`||`true`表示相机、麦克风、媒体读写权限均已授权;|
|||`false`表示未初始化、用户拒绝授权或权限申请异常|

#### 调用说明: 

1. 建议在用户主动点击拍摄、拼接、选择素材等功能入口后调用。 

2. 不建议在应用启动时无业务触发地提前申请权限。 

3. 如果返回 `false` ,宿主应用应停止打开 SDK 页面,并提示用户授权后再使用相关功能。 

#### 调用示例: 

```
const granted = await YiliSDK.requestPermissions();
if (!granted) {
  console.warn('SDK permissions denied');
  return;
}
```

### **4. 打开 SDK 页面** 

接口名称: `YiliSDK.open` 

调用方式: 

```
YiliSDK.open(params?: YiliSDKParams): void
```

|请求参数:|||||
|---|---|---|---|---|
|**参数**|**类型**||**必填**|**说明**|
|`params`|`YiliSDKParams`|否||打开 SDK 的启动参数|
|返回参数:无。|||||

调用说明: 

1. 调用前必须先调用 `YiliSDK.init()` 。 

2. 建议先调用 `YiliSDK.requestPermissions()` 并在返回 `true` 后再打开 SDK。 

3. `skipGuide` 为 `true` 时直接进入拍摄页;否则进入引导页。 

调用示例: 

```
YiliSDK.open({ initialMode: 'multi' });
```

#### 直接进入拍摄页: 

```
YiliSDK.open({
  initialMode: 'video',
  skipGuide: true
});
```

### **5. 注册结果回调** 

接口名称: `YiliSDK.setResultCallback` 

调用方式: 

```
YiliSDK.setResultCallback(callback: YiliSDKResultCallback | null): void
```

#### 请求参数: 

|**参数**|**类型**|**必填**|**说明**||
|---|---|---|---|---|
|`callback`|`YiliSDKResultCallba|null`|是|结果回调函数;传入|
||ck \|||`null`表示取消回调|

#### 返回参数:无。 

#### 触发时机: 

#### 用户在 SDK 结果页点击“确认结果”后触发。 

#### 返回结果: 

|**字段**|**类型**|**说明**|
|---|---|---|
|`success`|`boolean`|是否成功返回结果|
|`imageUris`|`string[]`|结果文件 URI 列表|
|`imagePaths`|`string[]`|结果文件绝对路径列表|
|`mode`|`string`|启动模式|

#### 调用示例: 

```
YiliSDK.setResultCallback((result: YiliSDKResult) => {
  if (!result.success || result.imagePaths.length === 0) {
    return;
  }
  console.info(`result paths: ${JSON.stringify(result.imagePaths)}`);
});
```

#### 取消回调: 

```
YiliSDK.setResultCallback(null);
```

### **6. 获取工作目录** 

接口名称: `YiliSDK.getWorkDir` 

#### 调用方式: 

```
YiliSDK.getWorkDir(): string
```

#### 请求参数:无。 

#### 返回参数: 

||**类型**||**说明**|
|---|---|---|---|
|`string`||SDK 工作目录绝对路径,|默认位于宿主应用|
|||`filesDir/yiliPhoto`||

#### 调用说明: 

1. 调用前必须完成 `YiliSDK.init()` 。 

#### 2. SDK 拍摄、临时处理和结果文件默认保存在该目录下。 

调用示例: 

```
const workDir = YiliSDK.getWorkDir();
console.info(`SDK work dir: ${workDir}`);
```

### **7. 前台生命周期透传** 

接口名称: `YiliSDK.onForeground` 

调用方式: 

```
YiliSDK.onForeground(): void
```

请求参数:无。 

返回参数:无。 

调用示例: 

```
onForeground(): void {
  YiliSDK.onForeground();
}
```

### **8. 后台生命周期透传** 

接口名称: `YiliSDK.onBackground` 

调用方式: 

```
YiliSDK.onBackground(): void
```

请求参数:无。 

返回参数:无。 

调用示例: 

```
onBackground(): void {
  YiliSDK.onBackground();
}
```

## **七、完整调用示例** 

```
import { UIAbility, Want } from '@kit.AbilityKit';
import { window } from '@kit.ArkUI';
import { YiliSDK, YiliSDKResult } from 'yili-lingtongcv-hm-sdk';
import 'yili-lingtongcv-hm-sdk/src/main/ets/pages/GuidePage';
import 'yili-lingtongcv-hm-sdk/src/main/ets/pages/CameraSDK_V2';
import 'yili-lingtongcv-hm-sdk/src/main/ets/pages/AlgorithmResult';
export default class EntryAbility extends UIAbility {
  onCreate(want: Want, launchParam: ESObject): void {
    YiliSDK.init(this.context, { workDirName: 'yiliPhoto' });
    YiliSDK.setResultCallback((result: YiliSDKResult) => {
      if (result.success) {
        console.info(`SDK result: ${JSON.stringify(result.imagePaths)}`);
      }
    });
  }
  onForeground(): void {
    YiliSDK.onForeground();
  }
  onBackground(): void {
    YiliSDK.onBackground();
  }
  onWindowStageCreate(windowStage: window.WindowStage): void {
    windowStage.loadContent('pages/Index');
  }
}
```

#### 宿主页面中打开 SDK: 

```
import { YiliSDK } from 'yili-lingtongcv-hm-sdk';
async function openSdk(): Promise<void> {
  if (!YiliSDK.isInitialized()) {
    return;
  }
  const granted = await YiliSDK.requestPermissions();
  if (!granted) {
    return;
  }
  YiliSDK.open({ initialMode: 'multi' });
}
```

## **八、错误码说明** 

当前版本 SDK 对外接口未返回独立数字错误码。为满足上架接口文档要求,宿主应用可按以下状态进行处理: 

|**错误码**|**场景**|**表现**|**建议处理**|
|---|---|---|---|
|`YILI-0000`|成功|`YiliSDKResult.success` `=== true` ,且 `imageUris` 或 `imagePaths`存在结果|正常读取结果文件|
|`YILI-1001`|SDK 未初始化|`isInitialized()`返回 `false` ,或未初始化时调用 `open()`无页面跳转|先调用 `YiliSDK.init(context)`|
|`YILI-1002`|权限未授权|`requestPermissions()`返 回 `false`|提示用户开启相机、麦克 风、媒体权限|
|`YILI-1003`|用户未确认结果|未触发 `setResultCallback`回调|等待用户在结果页点击“确 认结果”,或引导用户重新 操作|
|`YILI-1004`|结果为空|`success === false`或 `imageUris/imagePaths`为 空|提示用户重新拍摄或重新拼 接|
|`YILI-1005`|工作目录未初始化|调用 `getWorkDir()`前未调 用 `init()`|先完成 SDK 初始化|

说明:以上错误码为接口文档层面的宿主处理建议,当前 SDK 代码未以独立字段返回该错误码。 

## **九、版本说明** 

||**版本**|**说明**|
|---|---|---|
|`1.0.0`||首个发布版本,提供本地拍摄、多图拼接、视频抽帧拼接、 结果保存和结果回调能力|
|`1.0.1`||优化拍摄/结果页交互与拼接效果|
|`1.0.2`||优化视频抽帧策略,用于上架发布|
