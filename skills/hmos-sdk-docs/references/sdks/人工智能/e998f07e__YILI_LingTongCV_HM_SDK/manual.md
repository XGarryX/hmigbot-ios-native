# **YILI LingTongCV HM SDK 集成指南** 

> SDK 版本:1.0.2 | 文档修订:2026-07-10 | 适用于 HarmonyOS 5.0+ (API 12+) | arm64-v8a > **第三方宿主集成请以本 文档为准** ;内部打包与交付流程见 `SDK 打包与集成操作文档 .md` 。 

--- 

## **1. 概述** 

YILI LingTongCV HM SDK 提供基于 OpenCV 的鸿蒙原生照片拼接能力,支持: 

- **单张拍摄** — 快速拍摄 

- **多图拼接** — 拍摄多张图片并智能拼接全景图 

- **视频拼接** — 录制视频后自动抽帧拼接 

### **集成方式** 

SDK 以 **HAR(HarmonyOS Archive)** 形式提供,集成后代码与 Native 库一并编译进宿主应用。 

|**安装方式**|**命令 / 配置**|**说明**|
|---|---|---|
|OHPM|`ohpm i yili-lingtongcv-hm-sdk`|**推荐**,1.0.0 已发布至OHPM 中心仓 并验证可装|
|本地 HAR|`"yili-lingtongcv-hm-sdk":` `"file:./libs/yili_sdk.har"`|离线 / 定制场景,随交付包提供|

--- 

## **2. 集成步骤** 

### **2.1 添加依赖** 

SDK 1.0.0 已发布至 OHPM 中心仓 并验证可装, **推荐使用 OHPM 远程安装** ;离线或需定制 har 时可改用本地 HAR。两种 方式二选一, **不要在同一工程中混用** `file:` 引用与版本号依赖。 

##### **OHPM(推荐):** 

```
ohpm i yili-lingtongcv-hm-sdk
```

或在使用 SDK 的模块 `oh-package.json5` 中声明版本号: 

```
{
  "dependencies": {
    "yili-lingtongcv-hm-sdk": "^1.0.0"
  }
}
```

> 包名 `yili-lingtongcv-hm-sdk` 与 `yili_sdk/oh-package.json5` 中 `name` 字段一致。 

**本地 HAR(离线 / 定制场景):** 将 Release 构建的 `yili_sdk.har` 放入宿主工程的 `libs/` ,然后在 **使用 SDK 的模块** `ohpackage.json5` 中声明依赖。 `file:` 路径必须相对正在编辑的 `oh-package.json5` ,且文件须真实存在。 单模块工程或根 `oh-package.json5` 示例: 

```
{
  "dependencies": {
    "yili-lingtongcv-hm-sdk": "file:./libs/yili_sdk.har"
  }
}
```

多模块工程示例:若 HAP 模块为 `entry/` ,并将 HAR 放在工程根 `libs/yili_sdk.har` ,则编辑 `entry/ohpackage.json5` : 

```
{
  "dependencies": {
    "yili-lingtongcv-hm-sdk": "file:../libs/yili_sdk.har"
  }
}
```

> **说明:** 上文多模块示例对应第三方验证工程(如 `hjtest` )。本仓库( `yili-hm-sdk-multi` )内部示例工程开发期直接依 赖源码模块: `entry/oh-package.json5` 中使用 `"yili-lingtongcv-hm-sdk": "file:../yili_sdk"` 。 > > **避坑:** `file:` 后只能跟本地路径, **不可** 写成 `"file:^1.0.0"` (版本号);若 `libs/` 下没有对应 har 文件, `ohpm install` 会报 `Fetch local file package error` (见 Q10)。改用远程安装时,请先从根目录与各模块 `oh-package.json5` 中移除所有 `file:` 引用,再执行 `ohpm install` 。 

执行 `ohpm install` 或 DevEco **Sync Now** 。 

### **2.2 宿主工程配置要求** 

#### **build-profile.json5** 

宿主 `build-profile.json5` 建议满足: 

|**配置项**|**建议值**|**说明**|
|---|---|---|
|`compatibleSdkVersion`|`5.0.0(12)`或更高|低于 API 12 可能无法运行|
|设备类型|`default`/ `phone`/ `tablet`|SDK 已声明支持|
|CPU|**arm64-v8a 真机**|HAR 内 Native 库仅含 arm64,x86 模拟器不可用|
|`signingConfig`|与 `signingConfigs`同名|**真机安装必须**,见下方签名说明|
|`useNormalizedOHMUrl`|`true` (推荐)|集成 HAR 命名路由时建议开启,与 SDK 保持一致|

##### **签名配置(真机 Run 必需):** 

DevEco 自动生成签名材料后,除在 `app.signingConfigs` 中声明外,还必须在对应 `products` 条目上关联: 

```
{
  "app": {
    "signingConfigs": [
      {
        "name": "default",
        "type": "HarmonyOS",
        "material": { /* DevEco 自动签名生成 */ }
      }
    ],
    "products": [
      {
        "name": "default",
        "signingConfig": "default",
        "compatibleSdkVersion": "5.0.0(12)"
      }
    ]
  }
}
```

若仅生成 `signingConfigs` 而未在 `products` 中写 `"signingConfig": "default"` ,构建日志会出现 `No signingConfig found for product default` ,产出未签名 HAP,真机安装报 `code:9568320 / no signature file` 。 

推荐在 `products[].buildOption.strictMode` 中开启 `useNormalizedOHMUrl` : 

```
"buildOption": {
  "strictMode": {
    "useNormalizedOHMUrl": true
  }
}
```

#### **main_pages.json(宿主页路由)** 

宿主模块须保留自己的 `main_pages.json` ,路径: 

```
entry/src/main/resources/base/profile/main_pages.json
```

##### **只注册宿主页** (与 `loadContent` 加载的页面一致),不要把 SDK 页面写入此文件: 

```
{
  "src": [
    "pages/Index"
  ]
}
```

SDK 页面( `GuidePage` 等)由 HAR 内 `route_map.json` 提供命名路由, **无需** 也 **不应** 写入宿主 `main_pages.json` 。 

格式要求: 

- 标准 JSON, `src` 数组至少包含 1 个页面路径 

• **UTF-8 无 BOM** (带 BOM 会导致编译报 `main_pages.json file format is invalid` ) 

编译时若出现 `main_pages.json is defined repeatedly` 警告,通常是因为 HAR 内也有一份同名文件,可忽略;宿主只需 维护自己的宿主页列表。 

#### **module.json5 权限** 

宿主 `module.json5` **无需重复声明** SDK 权限(HAR 编译时自动合并),除非宿主自身还有独立用途;运行时仍需调用 `YiliSDK.requestPermissions()` 。 

### **2.3 初始化 SDK(EntryAbility)** 

```
import { UIAbility, Want } from '@kit.AbilityKit';
import { window } from '@kit.ArkUI';
import { hilog } from '@kit.PerformanceAnalysisKit';
import { YiliSDK, YiliSDKResult } from 'yili-lingtongcv-hm-sdk';
// 命名路由:建议在宿主 EntryAbility 显式 force-import(与示例 entry 工程一致)
import 'yili-lingtongcv-hm-sdk/src/main/ets/pages/GuidePage';
import 'yili-lingtongcv-hm-sdk/src/main/ets/pages/CameraSDK_V2';
import 'yili-lingtongcv-hm-sdk/src/main/ets/pages/AlgorithmResult';
export default class EntryAbility extends UIAbility {
  onCreate(want: Want, launchParam: ESObject): void {
    YiliSDK.init(this.context, { workDirName: 'yiliPhoto' });
    YiliSDK.setResultCallback((result: YiliSDKResult) => {
      // result.imagePaths — 沙箱绝对路径,位于 filesDir/yiliPhoto
      hilog.info(0x0000, 'HostApp', `SDK 结果: ${JSON.stringify(result)}`);
    });
  }
  onForeground(): void {
    YiliSDK.onForeground();
  }
  onBackground(): void {
    YiliSDK.onBackground();
  }
  onWindowStageCreate(windowStage: window.WindowStage): void {
    windowStage.loadContent('pages/Index', (err: ESObject) => {
      if (err?.code) {
        hilog.error(0x0000, 'HostApp', `loadContent 失败: ${JSON.stringify(err)}`);
      }
    });
  }
}
```

> **关于 force-import:** SDK 包的 `Index.ets` 内已 side-import 上述三个页面,但 HAR 命名路由在部分宿主工程下仍需 EntryAbility 显式 import,否则可能出现 `Named route error` 。示例工程 

`entry/src/main/ets/entryability/EntryAbility.ets` 采用双保险写法。 

SDK 对外命名路由仅包含: `GuidePage` 、 `CameraSDK_V2` 、 `AlgorithmResult` (见 HAR 内 `route_map.json` )。 `LoginPage` / `SettingsPage` / `OnlineTrial` 为内部遗留页面, **不在** 对外集成路径中。 

### **2.4 宿主页面调用入口** 

```
import { YiliSDK } from 'yili-lingtongcv-hm-sdk';
// 在按钮点击等时机调用
async function openSdk(): Promise<void> {
  if (!YiliSDK.isInitialized()) {
    console.error('请先调用 YiliSDK.init');
    return;
  const granted = await YiliSDK.requestPermissions();
  if (!granted) {
部分权限被拒绝,SDK 功能可能受限
    return;
多图拼接模式,先展示引导页
  YiliSDK.open({ initialMode: 'multi' });
跳过引导页,直接进入拍摄页(可选)
  // YiliSDK.open({ initialMode: 'video', skipGuide: true });
}
```

--- 

## **3. API 参考** 

### **YiliSDK.init(context, config?)** 

```
YiliSDK.init(context: Context, config?: YiliSDKConfig): void
```

|**字段**||**类型**|**说明**|
|---|---|---|---|
|workDirName|string||工作目录名,默认 `yiliPhoto` ,位于|
||||宿主 `filesDir`下|

须在 UIAbility `onCreate` 中、任何 `open()` 之前调用。重复调用会被忽略。 

### **YiliSDK.isInitialized()** 

返回 SDK 是否已完成 `init` 。 

### **YiliSDK.getWorkDir()** 

返回工作目录绝对路径(如 `.../files/yiliPhoto` ),宿主可直接读取 SDK 产出的图片/视频。未调用 `init` 时会抛错。 

### **YiliSDK.setResultCallback(callback)** 

用户于结果页点击 **「上传图片」** 时触发(非自动回调),回传拼接/拍摄结果路径。 

```
interface YiliSDKResult {
  success: boolean;
  imageUris: string[];   // file:// URI
  imagePaths: string[];  // 沙箱绝对路径(推荐宿主使用)
  mode?: string;         // 拍摄模式:single / multi / video
}
```

传入 `null` 可取消注册。 

### **YiliSDK.open(params?)** 

|**字段**|**类型**|**说明**|||
|---|---|---|---|---|
|initialMode|`'single' \|'multi' \|'video'`|拍摄模式:单拍 / 多 图拼接 / 视频拼接 (内部映射为 0 / 1 / 2)|
|skipGuide|boolean|为 `true`时跳过引导 页,直接进入|||
|||`CameraSDK_V2`|||
|extras|Record<string,|自定义透传(预留,|||
||string>|当前未消费)|||

未传 `params` 时默认进入引导页,拍摄模式为单拍。 

### **YiliSDK.requestPermissions()** 

请求相机、麦克风、媒体读写权限,返回是否 **全部** 授予( `authResults` 均为 0)。 

### **YiliSDK.onForeground() / onBackground()** 

在 UIAbility 对应生命周期中透传,用于 SDK 内部 UI 刷新与相机结果检查。 

--- 

## **4. 权限说明** 

SDK 所需权限已在 HAR `module.json5` 中声明,编译时自动合并至宿主应用: 

|**权限**|**用途**|
|---|---|
|`ohos.permission.CAMERA`|自定义相机预览与拍照|
|`ohos.permission.MICROPHONE`|系统录像时录音|
|`ohos.permission.READ_MEDIA`|读取相册 / 媒体库|
|`ohos.permission.WRITE_MEDIA`|保存到系统相册(结果页保存按钮)|

`requestPermissions()` 会一次性请求以上四项;宿主无需在 `module.json5` 重复声明,除非宿主自身还有其他 Ability 需 要单独说明用途。若宿主确实重复声明同名权限,需确保 `usedScene` 覆盖调用 SDK 的 Ability。 

--- 

## **5. 约束与限制** 

|**项**|**值**|
|---|---|
|最低运行系统|HarmonyOS 5.0+(API 12)|
|compatibleSdkVersion|5.0.0(12)+|
|CPU 架构|**arm64-v8a 真机**(不含 x86 模拟器)|
|DevEco Studio|5.0+(工程当前 compileSdk 6.1.0(23))|
|HAR 体积|Release 约 3 MB 量级(含 OpenCV Native,以实际构建 为准)|
|独立 HAP 体积|约 6 MB(entry + SDK,供参考)|

--- 

## **6. 集成检查清单** 

||**#**|**检查项**|
|---|---|---|
|1||使用 SDK 的模块 `oh-package.json5`已添加 `yili-` `lingtongcv-hm-sdk` ,且 `file:`路径相对该文件正确|
|2||`ohpm install`/ Sync 成功,oh_modules 中可见包|
|3||宿主 `main_pages.json`仅含宿主页(如|
|||`pages/Index` ),UTF-8 无 BOM|

||**#**|**检查项**|
|---|---|---|
|4||`build-profile.json5`的 `products`已关联 `signingConfig` (真机安装必需)|
|5||`EntryAbility.onCreate`中调用 `YiliSDK.init`|
|6||EntryAbility 已 force-import 三个命名路由页面|
|7||`onWindowStageCreate`已 `loadContent`宿主首页,且该 页已在 `main_pages.json`中注册|
|8||打开 SDK 前调用 `requestPermissions()`|
|9||如需回传结果,已注册 `setResultCallback`|
|10||**arm64 真机**验证单拍 / 多图 / 视频流程|

--- 

## **7. 常见问题** 

### **Q1: Cannot find module 'yili-lingtongcv-hm-sdk'** 

- 确认使用 SDK 的模块 `oh-package.json5` 中包名与路径正确( `yili-lingtongcv-hm-sdk` ,非 `yili_sdk` ) 

- 执行 `ohpm install` 后 **Sync Now** 

- 多模块工程确认 HAP 模块的 `oh-package.json5` 声明了依赖,且 `file:` 路径按该模块目录计算 

### **Q2: Named route error / 页面跳转失败** 

- 在宿主 `EntryAbility.ets` 显式 import 三个页面(见 2.3 节) 

- Clean Project 后 Rebuild 

### **Q3: main_pages.json file format is invalid** 

- 检查 `entry/src/main/resources/base/profile/main_pages.json` 是否为合法 JSON 

- 确认文件为 **UTF-8 无 BOM** (Windows 编辑器保存时易带入 BOM) 

- `src` 数组至少包含 1 个宿主页路径 

### **Q4: Install Failed — no signature file(code:9568320)** 

- DevEco 已生成签名材料,但 `build-profile.json5` 的 `products` 未关联 `signingConfig` 

- 在对应 product 中添加 `"signingConfig": "default"` (名称与 `signingConfigs[].name` 一致) 

- Clean 后重新构建,确认产出 `entry-default-signed.hap` 

### **Q5: main_pages.json is defined repeatedly(警告)** 

- HAR 与宿主各有一份 `main_pages.json` ,属正常现象 

• 宿主只需维护自己的宿主页列表,无需合并 SDK 页面 

### **Q6: 如何读取 SDK 生成的文件** 

```
const dir = YiliSDK.getWorkDir(); // .../files/yiliPhoto
```

或在 `setResultCallback` 中使用 `result.imagePaths` (推荐,已是绝对路径)。 

### **Q7: OpenCV 未加载 / 模拟器无法拼接** 

SDK Native 库仅 **arm64-v8a** ,x86 模拟器不支持。请使用鸿蒙真机调试。 

### **Q8: 权限弹窗不出现或部分功能不可用** 

- 确认已调用 `YiliSDK.init` 后再 `requestPermissions()` 

- 检查系统设置中是否曾经拒绝了权限 

- 宿主不要在 `module.json5` 中用错误的 `usedScene` 重复声明同名权限;如需重复声明,确保覆盖调用 SDK 的 Ability 

### **Q9: setResultCallback 没有触发** 

回调仅在结果页用户点击 **「上传图片」** 时触发,点击「重新拍摄」或系统返回不会触发。 

### **Q10: ohpm install 报 "Fetch local file package error" / 00617202** 

- **现象** :执行 `ohpm install` (即便指定远程包名 `yili-lingtongcv-hm-sdk` )报 `Fetch local file package error, .../libs/yili_sdk.har does not exist` ,整体安装失败。 

- **原因** : `oh-package.json5` 中存在本地 `file:` 依赖,但引用的 har 文件不存在;或误写成 `"file:^1.0.0"` 这类无效语法 ( `file:` 后只能跟本地路径,不能跟版本号)。ohpm 会校验所有已声明的本地 `file:` 依赖,任一缺失即整体失败,并 阻断远程包安装。 

##### • **解决** : 

- 走远程 OHPM:将根目录与使用模块的 `oh-package.json5` 中依赖统一改为 `"yili-lingtongcv-hm-sdk": "^1.0.0"` , **删 除所有** **`file:` 引用** 后重新 `ohpm install` (必要时先 `ohpm clean` )。 

- 走本地 HAR:将 `yili_sdk.har` 放到 `file:` 路径指向的目录,确保路径相对 `oh-package.json5` 解析正确。 

- **提示** :远程安装前务必移除或补齐本地 `file:` 引用,二者不可混用。 

--- 

## **附录** 

||**日期**|**说明**|
|---|---|---|
|2026-07||首版公开发布|
|2026-07-06||审计修订:补全 EntryAbility 示例、依赖路径、权限与|
|||build-profile 说明|

||**日期**|**说明**|
|---|---|---|
|2026-07-07||对照 `hjtest`验证工程修订:补充 main_pages.json、签 名关联、useNormalizedOHMUrl、FAQ|
|2026-07-08||OHPM 远程安装验证通过(1.0.0 已发布);集成方式推荐|
|||顺序调整为 OHPM 优先,新增 `file:`语法误用 / 本地 har 缺失导致 `ohpm install`失败的 FAQ(Q10)|

许可证:Proprietary(闭源),详见 SDK 包内 LICENSE。 第三方:OpenCV(Apache 2.0)。 --- 

## **8. 当前代码交互更新说明** 

以下内容对应当前代码实现,第三方宿主在验收和联调时需要同步理解: 

- 结果页点击“确认”后,会回传结果给宿主,并清空结果页本地状态;返回拍摄页时会清空拍摄页的缩略图列表。 

- 拍照按钮左侧的箭头现在是“返回宿主页/上一页”,不再用于删除最后一张照片。 

- 拍摄页缩略图右上角增加了红色圆形 `×` 删除按钮,支持逐张删除已拍照片。 

- 视频拼接开始前会先显示 3 秒倒计时,样式为预览框下方的红色圆圈数字提示;倒计时结束后才进入抽帧/拼接流程。 

- 以上交互变更不影响宿主接入方式,仍按 `YiliSDK.init()` 、 `requestPermissions()` 、 `open()` 、 `setResultCallback()` 的流程使用。
