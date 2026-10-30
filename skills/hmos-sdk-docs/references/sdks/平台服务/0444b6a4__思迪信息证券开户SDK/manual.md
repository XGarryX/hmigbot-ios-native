2025-04-09 

思迪综合SDK集成说明文档-[HarmonyOS SDK集成].md 

# 思迪综合SDK集成说明文档-[HarmonyOS SDK集成] 

--> 

- 1 设计说明 

   - 1.1 SDK架构设计 

   - 1.2 业务流程设计 

- 2 集成说明 

   - 2.1 集成环境 

   - 2.2 集成SDK配置文件和授权文件 

   - 2.3 开启useNormalizedOHMUrl 

   - 2.4 集成har并安装 

   - 2.5 集成验证 

   - 2.6 权限配置 

- 3 SDK使用 

   - 3.1 导入头文件 

   - 3.2 启动服务 

   - 3.3 SDK简单使用示例 

   - 3.4 TKOpenSDK主要方法 

   - 3.5 实现转发事件 

   - 3.6 获取SDK版本 

   - 3.7 获取当前WebController 

   - 3.8 设置SDK全局配置 

## 1 设计说明 

### 1.1 SDK架构设计 

思迪鸿蒙开户SDK是一个通用的前端混合开发容器,除了满足证券开户、业务办理、理财商城、交易等 业务系统的常用功能(如身份证拍照、银行卡拍照、双向视频见证、单向视频录制等),还支持加载其 他标准H5页面。仅需对三方业务系统的H5页面进行轻量调整,即可完美支持和调用SDK功能,在鸿蒙生 态中拓展业务。 

2025-04-09 

思迪综合SDK集成说明文档-[HarmonyOS SDK集成].md 

### 1.2 业务流程设计 

- 1、三方平台APP调用打开思迪SDK并传入券商H5地址; 

- 2、思迪SDK初始化内核和WebView组件,并加载券商H5页面地址; 

- 3、券商H5页面加载成功后,按照业务需求,调用思迪SDK插件中心的原生功能,如身份证拍照、双向 视频、单向视频等功能; 

- 4、原生功能完成后,把结果返回H5页面处理,提交到后台业务系统或继续进行其他业务; 

- 5、券商H5业务结果或者退出时,调用思迪SDK关闭页面,并返回到三方平台APP; 

2025-04-09 

思迪综合SDK集成说明文档-[HarmonyOS SDK集成].md 

## 2 集成说明 

### 2.1 集成环境 

#### 序号 开发环境 

|1|操作系统|HarmonyOS NEXT|
|---|---|---|
|2|开发软件|DevEco-Studio(v5.0.5.315)|
|3|软件运行支撑环境|nodejs(v18.14.1)|
|4|鸿蒙SDK版本|HarmonyOS5.0.1ReleaseSDK|
|5|模型|Stage|
|6|鸿蒙API版本|5.0.1(API13)|
|7|开发语言|ArkTs|
|8|OS系统版本|>=5.0.0.115|

### 2.2 集成SDK配置文件和授权文件 

`1.` 将 `thinkive` 文件夹放到模块 `resources/rawfile` 下,如 `entry/resources/rawfile` 下 

`2. thinkive` 文件夹包括如下文件: 

- 环境配置文件: `Environment.xml` ,选择 `dev` 或者 `pro` 环境 

- 插件配置文件: `SystemPlugin.xml` (底层库插件)、 `TKH5SDKPlugin.xml` (综合库插件)。可 一 

- 以直接放在 `default` 下。也可以 `dev` 和 `pro` 各 份。 

- 全局配置文件: `Configuration.xml` 全局配置文件。 `dev` 和 `pro` 各一份 

- 授权配置文件: `TKSDKAuth.lic` ,只有一份 

- 示例如下: 

2025-04-09 

思迪综合SDK集成说明文档-[HarmonyOS SDK集成].md 

### 2.3 开启useNormalizedOHMUrl 

`// build-profile.json5` 中设置开启 `useNormalizedOHMUrl` 为 `true "products": [ { "name": "default", "signingConfig": "default", "compatibleSdkVersion": "5.0.0(12)", "runtimeOS": "HarmonyOS", "buildOption": { "strictMode": { "useNormalizedOHMUrl": true,  //` 需要开启该属性,支持字节码打包 `har } }, } ]` 

2025-04-09 

思迪综合SDK集成说明文档-[HarmonyOS SDK集成].md 

#### 示例如下: 

### 2.4 集成har并安装 

`1.` 将 `TKOpenFramework.har` 等放到模块目录下,如工程目录下的 `3Lib` 文件夹 

`2.` 修改根目录下的 `oh-package.json5` 文件 

`3.` 增加依赖,在 `dependencies` 下配置如下 

- `"dependencies": {` 

- 一 

- `//` 必须依赖 `(` 依赖库名称必须 致,路径可以动态修改 `)` 

- `"@thinkive/tk-harmony-base" : "file:./3Lib/thinkive-framework-` 

- `0.2.2.har",  //` 思迪底层库 

- `"@thinkive/tk-harmony-open":` 

`"file:./3Lib/tk_open_framework_v1.0.0.har",  //` 思迪开户库 

- 一 

- `//` 可选依赖 `(` 依赖库名称必须 致,路径可以动态修改 `) "@thinkive/tk-harmony-tchat":` 

`"file:./3Lib/tchatsdk_framework_v9.0.3_20240319.har", //` 思迪 `tchat` 库,若有 `TChat` 双向、 `TChat` 活体、 `TChat` 录制请添加该依赖 

`"sdk_liveness": "file:./3Lib/ssid_liveness_3.0.0.beta.har",  //` 若有商汤 活体,请添加该依赖 

`"exocrdomsdk": "file:./3Lib/exocrdomsdk_1.0.8.har", //` 若有易道 `OCR` ,请添 加该依赖 

`"class-transformer": "^0.5.1" //` 若有易道 `OCR` ,请添加该依赖 

`"hisignlive" : "file:./3Lib/hisignlive.har" //` 若有易道活体,请添加该依赖 

- `"library": "file:./3Lib/intsig_library_6.0.3.har",  //` 若有合合 `OCR` ,请添 

2025-04-09 

思迪综合SDK集成说明文档-[HarmonyOS SDK集成].md 

#### 加该依赖 

`"@bdmap/locsdk": "file:./3Lib/locsdk_1.0.0.har",  //` 若有百度定位,请添加 该依赖 

`"anychat_sdk":  "file:./3Lib/anychat_sdk_1.0.0.har", //` 若有 `anychat,` 请添 加该依赖 

`"@aisp/aipharmonysdk": "file:./3Lib/aipharmonysdk_v1.0.9.har",  //` 若有 讯飞语音,请添加该依赖 

一一 `//` 具体项目需要集成的三方库请根据项目需求和集成 `demo` ,此处不 演示 

- `}` 

`4.` 运行安装 `'ohpm install'` 

安装成功如下图: 

2025-04-09 

思迪综合SDK集成说明文档-[HarmonyOS SDK集成].md 

### 2.5 集成验证 

`//` 使用的 `ets` 文件,如 `Index.ets` 导入 `tk-harmony-open import { TKOpenEntryVO, TKOpenSDK } from '@thinkive/tk-harmony-open'` 

以上步骤完成之后,运行不报错,则sdk集成完毕。 

`1.` 选中要集成的模块(如 `entry` ) 

`2.` 选择菜单栏 `"build"` 

`3.` 选择 `"Generate Build Profile 'entry'"` 

`4.` 查看 `"Build Output"` 运行结果,若为 `0` 则集成完毕 

2025-04-09 

思迪综合SDK集成说明文档-[HarmonyOS SDK集成].md 

### 2.6 权限配置 

#### 2.6.1 思迪鸿蒙SDK所需权限列表 

|权限名称|用途|必 选/|权限 是否 需要|
|---|---|---|---|
|||可选|动态 申请|
||||不需|
|ohos.permission.INTERNET|发起网络请求|必选|要动 态申|
||||请|
||||不需|
|ohos.permission.GET_NETWORK_INFO|允许订阅应用网络信息|必选|要动 态申|
||||请|
||||不需|
|ohos.permission.GET_WIFI_INFO|允许订阅WIFI信息权限|必选|要动 态申|
||||请|
|ohos.permission.CAMERA|允许应用使用相机,进行身份证拍照、视 频见证、视频录制|必选|动态 申请|
|ohosermissionMICROPHONE|允许应用使用麦克风,视频录制、视频见|必选|动态|
|.p.|证过程中录制声音||申请|

2025-04-09 

思迪综合SDK集成说明文档-[HarmonyOS SDK集成].md 

|权限名称|用途|必 选/|权限 是否 需要|
|---|---|---|---|
|||可选|动态 申请|
|ohos.permission.STORE_PERSISTENT_DATA|允许应用存储持久化的数据,该数据直到 设备恢复出厂设置或重装系统才会被清除 (用于持久化保存设备id,以标记该设备,|可选 (建 议选|不需 要动 态申|
||使用50001插件和原生网络请求需申请)|择)|请|
||||不需|
|ohosermissionPRIVACYWINDOW|允许应用将窗口设置为隐私窗口,禁止截|可选|要动|
|.p._|屏录屏(使用60094插件需申请)||态申 请|
|ohos.permission.APPROXIMATELY_LOCATION|允许应用获取设备模糊位置信息,查询附 近营业部(使用60010插件或h5定位需申 请)|可选|动态 申请|
|ohos.permission.LOCATION|允许应用获取设备位置信息,查询附近营 业部(使用60010插件或h5定位需申请)|可选|动态 申请|
||||ACL|
|ohos.permission.READ_PASTEBOARD|允许应用读取剪贴板(使用60018插件需 申请)|可选|使 能, 动态|
||||申请|

#### 2.6.2 权限配置示例 

`1.` 修改引用模块(如 `entry` )的 `module.json5` 文件 

`2.` 在 `'module'` 模块在增加 `'requestPermissions',` 并配置权限 

2025-04-09 

思迪综合SDK集成说明文档-[HarmonyOS SDK集成].md 

`//` 代码示例: `"requestPermissions": [ { //` 允许订阅应用网络信息 `"name": "ohos.permission.GET_NETWORK_INFO", }, { //` 网络访问 `"name": "ohos.permission.INTERNET" }, { //WIFI` 信息权限 `"name": "ohos.permission.GET_WIFI_INFO" }, { //` 允许应用存储持久化的数据,该数据直到设备恢复出厂设置或重装系统才会被清除 `"name": "ohos.permission.STORE_PERSISTENT_DATA" }, { //` 允许应用将窗口设置为隐私窗口,禁止截屏录屏 `"name": "ohos.permission.PRIVACY_WINDOW", }, { "name": "ohos.permission.APPROXIMATELY_LOCATION", //` 模糊地理位置信息 `"reason": "` 打开您的位置权限,以便开户时为您选择最近的营业部;同时我们可能会根据您的 位置信息为您提供更契合您需求的页面展示、产品或服务;如果您关闭位置权限,我们将停止对您的位 置信息的收集,不影响您的交易 `", "usedScene": { "abilities": [ "TKOpenAbility" ], "when": "inuse" } }, { "name": "ohos.permission.LOCATION", //` 申请精确地理位置信息,需要先申请模糊位置权限 `"reason": "` 打开您的位置权限,以便开户时为您选择最近的营业部;同时我们可能会根据您的 位置信息为您提供更契合您需求的页面展示、产品或服务;如果您关闭位置权限,我们将停止对您的位 置信息的收集,不影响您的交易 `", "usedScene": { "abilities": [ "TKOpenAbility" ], "when": "inuse" } }, { "name": "ohos.permission.CAMERA", //` 相机 `"reason": "` 打开您的摄像头权限,以便您可以进行视频照片拍摄和上传,完成对应视频见证、 

2025-04-09 

思迪综合SDK集成说明文档-[HarmonyOS SDK集成].md 

人脸识别、活体检测、身份证件和银行卡识别业务操作流程 `", "usedScene": { "abilities": [ "TKOpenAbility" ], "when": "inuse" } }, { "name": "ohos.permission.MICROPHONE", //` 麦克风 `"reason": "` 打开您的麦克风权限,以便您在进行开户、购买产品业务办理时,我们可以进行视 频声音采集或者进行视频对话,同时在您使用搜索等功能时候,可以使用语音输入功能 `", "usedScene": { "abilities": [ "TKOpenAbility" ], "when": "inuse" } }, //        //` 允许应用读取剪贴板 `//        "name": "ohos.permission.READ_PASTEBOARD", //        "reason": "` 尊敬的客户,请在设置中开启读取剪切板权限,以便可以正常获取剪切板 中数据。 `", //        "usedScene": { //          "abilities": [ //            "TKOpenAbility" //          ], //          "when": "inuse" //        } //      } ]` 

#### 2.6.3 ACL权限 

`1.` 申请部分核心权限,需要配置支持 `ACL` 权限。具体请查看华为官方文档,搜索关键字为【支持 `ACL` 权限】 

`2. ACL` 权限开发阶段可以使用自动签名直接申请,上架时需要主动向华为报备申请 

#### 2.7 三方授权文件介绍(有商汤活体、易道OCR和易道活体请看该章节) 

`1. dom_exocr.lic` 是易道的授权文件,需要放在 `src/main/resources/rawfile/exocr` 下 

`2. SenseID_Liveness_Silent.lic` 是商汤的授权文件,需要放在 `src/main/resources/rawfile/liveness` 下 

`3. Ex_Live_harmony.lic` 是易道活体的授权文件,需要放在 `src/main/resources/rawfile/liveness` 下 

2025-04-09 

思迪综合SDK集成说明文档-[HarmonyOS SDK集成].md 

## 3 SDK使用 

### 3.1 导入头文件 

`//` 使用的 `ets` 文件,如 `Index.ets` 导入 `tk-harmony-open import { TKOpenEntryVO, TKOpenSDK } from '@thinkive/tk-harmony-open'` 

### 3.2 启动服务 

`/** *` 启动类选项 `*/ export interface TKAppEngineStartOption { /** *` 上下文 `*/ context?: common.UIAbilityContext; /** *` 动态库的模块名称 `*/ hspModuleName?: string; /** *` 回调函数 `*/` 

2025-04-09 

思迪综合SDK集成说明文档-[HarmonyOS SDK集成].md 

`finishCallBack?: TKAppEngineStartFinishCallBack; } /** *` 启动开户服务 `* @param context` 上下文对象 `*/ static startOpenService(option: TKAppEngineStartOption)` 

`//` 使用示例 `onWindowStageCreate(windowStage: window.WindowStage): void { // Main window is created, set main page for this ability hilog.info(0x0000, 'testTag', '%{public}s', 'Ability onWindowStageCreate');` 

`//` 启动思迪服务 `TKOpenSDK.startOpenService({ context: this.context as common.UIAbilityContext, hspModuleName: '' //` 包装的 `hsp` 名字,和 `module.json5` 中 `name` 对应 

```
  })
  windowStage.loadContent('pages/Index', (err) => {
if (err.code) {
      hilog.error(0x0000, 'testTag', 'Failed to load the content. Cause: %
{public}s', JSON.stringify(err) ?? '');
return;
    }
    hilog.info(0x0000, 'testTag', 'Succeeded in loading the content.');
  });
}
```

### 3.3 SDK简单使用示例 

`//` 在需要打开开户的地方增加如下示例代码 `let openEntryVO = new TKOpenEntryVO() openEntryVO.isH5GoBack = true // h5` 处理侧滑返回和物理返回键返回逻辑 

`openEntryVO.srcPageLayoutFullScreen = false //` 源页面是否是全屏 `openEntryVO.srcPageStatusBarEnable = false //` 源页面系统栏隐藏 `/` 显示状态 `openEntryVO.srcPageStatusBarStyle = '0' //` 源页面状态栏风格(状态栏小图标颜色), `0-` 黑色, `1-` 白色 

`openEntryVO.url = 'https://operation.thinkive.com:18090/tk-stkkhview/views/index.html?showPrivacy=0' //` 配置加载的 `h5` 页面地址 

`//` 打开 `h5` 页面 `this.openSDK .openEntryVO(openEntryVO)` 

`// .url('https://www.xxx.com')  //` 会替换 `openEntryVO` 中设置的 `url` 

```
// .openAccountEventCallBack((actionType:number, params:Record<string,
```

2025-04-09 

思迪综合SDK集成说明文档-[HarmonyOS SDK集成].md 

`Object>) => { // console.log(`` 收到开户事件, `actionType = ${actionType}, params=${JSON.stringify(params)}`) // }) .openMainPage({ params: {'token' : '123456', 'phoneNo' : '18888888888'}, isMerge: false }) //` 必须最后调用该方法。此处参数是业务参数,传递给 `h5` 

### 3.4 TKOpenSDK主要方法 

#### 3.4.1 设置启动参数 

`/** *` 设置 `SDK` 启动参数 `*/ openEntryVO(openEntryVO?: TKOpenEntryVO); /** *` 开户页面参数实体类 `*` 用于配置开户页面的各种参数和状态 `*/ @Observed export class TKOpenEntryVO { /** *` 加载的目标页面 `URL */ '' url: string = /** *` 点击物理返回键时是否通知 `H5` 返回 `*` 默认为 `false,` 即不通知 `H5 */ isH5GoBack: boolean = false /** *` 渠道参数 `,` 用于传递渠道相关信息 `*/ channelParams?:Record<string, Object> = undefined /** *` 渠道参数 `,` 兼容旧版本 `*` 请使用 `channelParams */ channelParam?:Record<string, Object> = undefined // =====` 源页面配置 `===== /** *` 源页面是否是全屏 `*` 不传需要在 `onPageShow` 自行恢复 `*` 默认 `false` 

2025-04-09 

思迪综合SDK集成说明文档-[HarmonyOS SDK集成].md 

`*/ srcPageLayoutFullScreen?: boolean; /** *` 源页面状态栏风格(状态栏小图标颜色) `* 0-` 黑色, `1-` 白色 `*` 默认 `0-` 黑色,不传需要在 `onPageShow` 自行恢复 `*/ srcPageStatusBarStyle?: string; /** *` 源页面状态栏小图标颜色 `*` 不传需要在 `onPageShow` 自行恢复 `*/ srcPageStatusBarContentColor?: string; /** *` 源页面系统栏隐藏 `/` 显示状态 `*` 不传需要在 `onPageShow` 自行恢复 `*/ srcPageStatusBarEnable?: boolean; /** *` 源页面 `navigation` 隐藏 `/` 显示状态 `*` 不传需要在 `onPageShow` 自行恢复 `*/ srcPageNavBarEnable?: boolean; /** *` 源页面底部指示条隐藏 `/` 显示状态 `*` 不传需要在 `onPageShow` 自行恢复 `*/ srcPageBottomBarEnable?: boolean; // =====` 新页面配置 `===== /** *` 新页面是否是全屏 `*` 默认 `true */ routerPageLayoutFullScreen: boolean = true; /** *` 新页面状态栏风格(状态栏小图标颜色) `* 0-` 黑色, `1-` 白色 `*` 默认 `0-` 黑色 `*/ routerPagestatusBarStyle?: string; /** *` 新页面状态栏小图标颜色 `*/ routerPageStatusBarContentColor?: string; /**` 

2025-04-09 

思迪综合SDK集成说明文档-[HarmonyOS SDK集成].md 

`*` 新页面系统栏隐藏 `/` 显示状态 `*` 默认 `true */ routerPageStatusBarEnable: boolean = true; /** *` 新页面 `navigation` 隐藏 `/` 显示状态 `*` 默认 `false *` 不传需要在 `onPageShow` 自行恢复 `*/ routerPageNavBarEnable?: boolean = false /** *` 新页面底部指示条隐藏 `/` 显示状态 `*` 默认 `true */ routerPageBottomBarEnable: boolean = true /** *` 新页面自定义导航头(标题栏)隐藏 `/` 显示状态 `*` 默认 `false *` 只有 `routerPageStatusBarEnable == true` 该值才有效 `*/ routerPageTitleBarEnable: boolean = false /** *` 新页面自定义导航头(标题栏)隐藏 `/` 显示状态 `*` 默认 `true *` 只有 `routerPageStatusBarEnable == true && routerPageTitleBarEnable == true` 该值才有效 `*/ routerPageBackPressEnable: boolean = true } //` 使用示例 `//` 在需要打开开户的地方增加如下示例代码 `let openEntryVO = new TKOpenEntryVO() openEntryVO.isH5GoBack = true // h5` 处理侧滑返回和物理返回键返回逻辑 `openEntryVO.url = 'https://operation.thinkive.com:18090/tk-stkkhview/views/index.html?showPrivacy=0'` 

#### 3.4.2 设置加载的页面url 

`/** *` 设置 `SDK` 加载 `url */ url(str?: string); //` 使用示例 `1 this.openSDK.url('https://www.xxx.com')` 

2025-04-09 

思迪综合SDK集成说明文档-[HarmonyOS SDK集成].md 

`//` 使用示例 `2 let openEntryVO = new TKOpenEntryVO() openEntryVO.isH5GoBack = true // h5` 处理侧滑返回和物理返回键返回逻辑 `openEntryVO.url = 'https://operation.thinkive.com:18090/tk-stkkhview/views/index.html?showPrivacy=0'` 

`this.openSDK.openEntryVO(openEntryVO) .url('https://www.xxx.com')  //` 会替换 `openEntryVO` 中设置的 `url` 

#### 3.4.3 加载SDK 主页面 

`/** *` 开户主页面选项接口 `*/ export interface TKOpenMainPageOption { /**` 业务参数 `*/ params?: Record<string, Object> /**` 是否合并业务参数 `,` 追加到内存中已有的业务参数集中 `*/ isMerge?: boolean /**` 当前 `Nav` 子组件对象或者堆栈对象 `*/ navComponentOrPathStack?: CustomComponent | NavPathStack } /** *` 打开主页面 `* params` :业务参数 `*/ async openMainPage(option?: TKOpenMainPageOption) //` 使用示例 `this.openSDK .url('https://www.xxx.com')  //` 会替换 `openEntryVO` 中设置的 `url .openMainPage({ params: {'token' : '123456', 'phoneNo' : '18888888888'}, }) //` 必须最后调用该方法 

#### 3.4.4 同步业务数据给sdk 

`/** *` 保存数据选项接口 `*/ export interface TKOpenSaveDataOption { /**` 保存的结果 `*/ value?: Object, /**` 保存的 `key` 。若有值,则保存结果为 `{key : value}` 。否则为 `{'fxcAccountInfo' : value} */ key?: string, /**` 保存的结果是否通知 `h5 */` 

2025-04-09 

思迪综合SDK集成说明文档-[HarmonyOS SDK集成].md 

`notifyH5?: boolean, /**` 登录类型 `*/ actionType?: TKOpenLoginType, /**` 是否合并业务参数 `,` 追加到内存中已有的业务参数集中 `*/ isMerge?: boolean } /** *` 同步业务数据给 `sdk * @param option` 保存数据选项 `* @returns this` 实例 `*/ saveDataToMemory(option: TKOpenSaveDataOption) //` 使用示例 `this.openSDK.saveDataToMemory({ value: {'phone' : '13888888888'} as Record<string, Object>, notifyH5: false }) //` 保存结果为 `{'fxcAccountInfo' : {'phone' : '13888888888'}} this.openSDK.saveDataToMemory({ value: {'phone' : '13888888888'} as Record<string, Object>, key: 'test', notifyH5: false }) //` 保存结果为 `{'test' : {'phone' : '13888888888'}} ------------------------------------------------------------/** *` 登录选项接口 `*/ export interface TKOpenLoginOption { /**` 保存的结果 `*/ value?: Object, /**` 保存的 `key` 。若有值,则保存结果为 `{key : value}` 。否则为 `{'fxcAccountInfo' : value} */ accountKey?: string, /**` 登录数据类型。 `accountKey` 为空, `accountType` 有值,保存的结果为 `{'fxcAccountInfo_[accountType` 有值 `]' : value}. *` 比如 `accountType` 为 `ygt,` 则结果为 `{'fxcAccountInfo_ygt' : value} */ accountType?: string, /**` 保存的结果是否通知 `h5 */ notifyH5?: boolean, /**` 是否合并业务参数 `,` 追加到内存中已有的业务参数集中 `*/ isMerge?: boolean } /** *` 便捷 `api:` 同步登录信息到内存中 `* @param option` 登录选项 `* @returns this` 实例 `*/ login(option: TKOpenLoginOption)` 

2025-04-09 

思迪综合SDK集成说明文档-[HarmonyOS SDK集成].md 

`//` 使用示例 `this.openSDK.login({ value: {'123' : '123'} as Record<string, string> })  //` 保存结果为 `{'fxcAccountInfo' : {'123' : '123'}} this.openSDK.login({ value: {'123' : '123'} as Record<string, string>, accountType: 'test' })  //` 保存结果为 `{'fxcAccountInfo_test' : {'123' : '123'}} ------------------------------------------------------------/** *` 登出选项接口 `*/ export interface TKOpenLogoutOption { /**` 清除指定 `accountKey` 的登录信息。默认为 `'fxcAccountInfo'` 。 `*` 若没有指定,则所有 `'fxcAccountInfo_[accountType` 有值 `]'` 的登录信息都会被清空 `*/ accountKey?: string, /**` 登录数据类型。 `accountKey` 为空, `accountType` 有值,结果为 `{'fxcAccountInfo_[accountType` 有值 `]' : undefined}. *` 比如 `accountType` 为 `ygt,` 则结果为 `{'fxcAccountInfo_ygt' : undefined} */ accountType?: string, /**` 保存的结果是否通知 `h5 */ notifyH5?: boolean } /** *` 便捷 `api:` 清空登录信息 `* @param option` 登出选项 `* @returns this` 实例 `*/ logout(option?: TKOpenLogoutOption) //` 使用示例 `//` 清除指定 `key` 的登录信息 `this.openSDK.logout({ accountKey: 'test' }) //` 结果为 `{'test' : undefined} this.openSDK.logout({ accountType: 'test' }) //` 结果为 `{'fxcAccountInfo_test' : undefined} //` 清除所有登录信息 `this.openSDK.logout() //` 结果为 `{'fxcAccountInfo' : undefined} //` 结果为 `{'fxcAccountInfo_test' : undefined}` 。假设之前保存过该类型的登录信息 `// ...` 

3.5 实现转发事件 

2025-04-09 

思迪综合SDK集成说明文档-[HarmonyOS SDK集成].md 

为方便思迪 `SDK` 上运行的 `h5` 能和 `app` 通讯,增加下面的通道方法,常见的转发事件清单如下: 

|参数名 类型 说明 描述|
|---|
|1:登陆|
|actionType String 事件类型 2:退出登陆 3:开户完成事件 4:通知主题改变 5:业务办理结束 6:打开业务办理 7:跳转商城页面 8:打开客服服务页面 9:打开分享 10:通知进行埋点 11:打开活动页面 1001:微信小确灵授权页面 或其他扩展类型(10X开头,如100,101) externalRadio:直接将数据给外部发广播通知|
|params Json 事件的参数 根据事件不同情况参数内容不一样,有些事件不需要参数就没有|
|`/**` `*` `* actionType`事件类型 `* params`事件参数 `*/` `openAccountEventCallBack(callBack: (actionType:number,` `params:Record<string, Object>) =>void) `|
|20 / 22 `//`使用示例 `this.openSDK.openAccountEventCallBack((actionType:number,` `params:Record<string, Object>) => {` `console.log(``收到开户事件,`actionType = ${actionType},` `params=${JSON.stringify(params)}`) ` `switch (actionType) {` `case 1: ` `//`登录 `// let errorNo = params.error_no` `// let errorInfo = params.error_info` `// //`以下参数请根据项目情况获取 `// let stock_account = params.stock_account` `// let mobilecode = params.mobilecode` `// let password = params.password` `break; ` `case 2: ` `//`退出登录 `break; `|

2025-04-09 

思迪综合SDK集成说明文档-[HarmonyOS SDK集成].md 

`case 3: //` 开户完成 `break; case 5: //` 业务办理结束 `let errorNo = params.error_no // let errorInfo = params.error_info switch (errorNo) { case 0: //` 正常通过 `break; case 1: //` 超出错误次数 `break; case -1: //` 用户主动返回 `break; case -2: //` 认证码过期 `break; default: break; } break; default: break; } })` 

### 3.6 获取SDK版本 

`/** *` 获取 `SDK` 版本号 `* @returns SDK` 版本号 `*/ static getSDKVersion(): string //` 使用示例 `TKOpenSDK.getSDKVersion()  // '3.2.0'` 

### 3.7 获取当前WebController 

`/** *` 获取当前 `WebController * @returns WebController` 实例 `*/ static getCurrentWebController(): WebviewController | undefined` 

2025-04-09 

思迪综合SDK集成说明文档-[HarmonyOS SDK集成].md 

`//` 使用示例 

```
TKOpenSDK.getCurrentWebController()
```

### 3.8 设置SDK全局配置 

`export interface TKOpenSDKConfigOption { /**` 合合 `ocr` 授权 `key */ HHOCRKey?: string; /**` 百度授权 `key */ BaiDuAuthKey?: string; /**` 商汤活体授权文件路径 `,` 默认是 `rawfile` 文件下的 `liveness/SenseID_Liveness_Silent.lic */ STLivenessLicPath?: string; /**` 易道 `OCR` 授权文件路径 `,` 默认是 `rawfile` 文件下的 `exocr/dom_exocr.lic */ EXOCRLicPath?: string; /**` 易道活体授权文件路径 `,` 默认是 `rawfile` 文件下的 `liveness/Ex_Live_harmony.lic */ EXLivenessLicPath?: string; } /** *` 设置 `SDK` 全局配置 `* @param config` 配置选项 `*/ static setSDKConfig(config: TKOpenSDKConfigOption) //` 使用示例 `TKOpenSDK.setSDKConfig({ HHOCRKey: 'xxx', // BaiDuAuthKey: 'xxx', STLivenessLicPath: 'liveness/SenseID_Liveness_Silent.lic', EXOCRLicPath: 'exocr/dom_exocr.lic', EXLivenessLicPath: 'liveness/Ex_Live_harmony.lic' })`
