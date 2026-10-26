2025/10/31 13:54

版本记录--ShowDoc

|   |   |   |   |
|---|---|---|---|

###  

云播2.0

|  |  |  |  |  |   版本记录 版本记录 版本号 时间 描述 V1.0.0 2024-9-26 初始版本 V1.1.0 2025-10-31 修复bug,完善接入规范 |  |
|---|---|---|---|---|---|---|
| 输入关键字后按回车以搜索     云播产品介绍   直播SDK     说明     直播Web-SDK     直播安卓-SDK     直播IOS-SDK   鸿蒙-SDK     鸿蒙版SDK介绍   鸿蒙-FastSDK     版本记录   接入方式   快速使用     鸿蒙-FineSDK     回放SDK     对接方案及资源 | 输入关键字后按回车以搜索   |  |  |  |  |   版本记录 |
|  |  |  |  |  |  | 版本记录 版本号 时间 描述 V1.0.0 2024-9-26 初始版本 V1.1.0 2025-10-31 修复bug,完善接入规范 |
|  |  |  |  |  |  |  |

| 版本记录 |  |  |
|---|---|---|
|  |  |  |
| 版本号 | 时间 | 描述 |
| V1.0.0 | 2024-9-26 | 初始版本 |
| V1.1.0 | 2025-10-31 | 修复bug,完善接入规范 |
|  |  |  |

+

 

 

https://developer.263.net/web/#/28/1031

2025/10/31 13:54

接入方式--ShowDoc

|   |   |   |   |
|---|---|---|---|

###  

云播2.0

|  |  |  |  |  |   接入方式 接入方式 1. 下载最新的sdk和demo包 下载地址: https://simupdate.263.net/263ProductSDK/263LiveFastSDK OhosDemo.zip _ 2. 将fastsdk.har包复制到项目的libs目录下,并在配置文件中添加依赖 复制 "dependencies": { // ... "@cloudlive/fastsdk": "file:libs/fastsdk.har" } 试着直接运行项目,若无报错则接入成功。 |  |
|---|---|---|---|---|---|---|
| 输入关键字后按回车以搜索     云播产品介绍   直播SDK     说明     直播Web-SDK     直播安卓-SDK     直播IOS-SDK   鸿蒙-SDK     鸿蒙版SDK介绍   鸿蒙-FastSDK     版本记录   接入方式   快速使用     鸿蒙-FineSDK     回放SDK     对接方案及资源 | 输入关键字后按回车以搜索   |  |  |  |  |   接入方式 |
|  |   云播产品介绍 |  |  |  |  |  |
|  |   直播SDK   |  |  |  |  |  |
|  |  |  |  |  |  | 接入方式 1. 下载最新的sdk和demo包 下载地址: https://simupdate.263.net/263ProductSDK/263LiveFastSDK OhosDemo.zip _ 2. 将fastsdk.har包复制到项目的libs目录下,并在配置文件中添加依赖 复制 "dependencies": { // ... "@cloudlive/fastsdk": "file:libs/fastsdk.har" } 试着直接运行项目,若无报错则接入成功。 |
|  |   说明 |  |  |  |  |  |
|  |     直播Web-SDK |  |  |  |  |  |
|  |     直播安卓-SDK |  |  |  |  |  |
|  |     直播IOS-SDK |  |  |  |  |  |
|  |   鸿蒙-SDK   |  |  |  |  |  |
|  |   鸿蒙版SDK介绍 |  |  |  |  |  |
|  |   鸿蒙-FastSDK   |  |  |  |  |  |
|  |   版本记录 |  |  |  |  |  |
|  |   接入方式 |  |  |  |  |  |
|  |   快速使用 |  |  |  |  |  |
|  |     鸿蒙-FineSDK |  |  |  |  |  |
|  |     回放SDK |  |  |  |  |  |
|  |  |  |  |  |  |  |
|  |     对接方案及资源 |  |  |  |  |  |
|  |  |  |  |  |  |  |

+

 

 

https://developer.263.net/web/#/28/1032

2025/10/31 13:55

快速使用--ShowDoc

|   |   |   |   |
|---|---|---|---|

###  

云播2.0

|  |  |  |  |  |   快速使用 快速使用 1. 在项目的 UIAbility 的 onWindowStageCreate 方法中添加以下代 码 复制 import gsFastSDK from '@cloudlive/fastsdk'; //. onWindowStageCreate(windowStage: window.WindowStage): void { gsFastSDK.onWindowStageCreate(this.context,windowStage) windowStage.loadContent('pages/LauncherPage', (err, data) => { if (err.code) { hilog.error(0x0000, 'testTag', 'Failed to load the content. return; } hilog.info(0x0000, 'testTag', 'Succeeded in loading the conten // 设置软键盘的弹出模式,为压缩已有ui而不是上抬ui windowStage.getMainWindowSync().getUIContext().setKeyboardAvoi }); } 2. 初始化Fastsdk let option = new FastSDKOption() option.server = Server.ON_LINE // 可以切换服务器地址 gsFastSDK.init(option) 3. 构造登录参数,并登录 let fastSdk = gsFastSDK let param: LoginParams = { webcastId: webcastId, // 直播间id nickname: nickname, // 用户昵称 password: livePassword, // 登录密码,如果使用主播密码登录则是主播身份 guestId: guestId, // 指定指定嘉宾id remarksInfo: "", // 第三方备注信息 thirdPartyId: "", } fastSdk.login(param) |  |
|---|---|---|---|---|---|---|
| 输入关键字后按回车以搜索     云播产品介绍   直播SDK     说明     直播Web-SDK     直播安卓-SDK     直播IOS-SDK   鸿蒙-SDK     鸿蒙版SDK介绍   鸿蒙-FastSDK     版本记录   接入方式   快速使用     鸿蒙-FineSDK     回放SDK     对接方案及资源 | 输入关键字后按回车以搜索   |  |  |  |  |   快速使用 |
|  |  |  |  |  |  |  |

https://developer.263.net/web/#/28/1033

2025/10/31 13:55

快速使用--ShowDoc

|  |  |  |  |  |  |  |  |  |  |  |
|---|---|---|---|---|---|---|---|---|---|---|
|     云播2.0 |  |  |  |  |  |  |  |  |  |  |
|  |  |  |  |  |  |  |  | .then(() => { // 登录成功,页面会自动跳转,这里可以不进行任何处理,也可以加提示。         }) .catch((error: GSError) => { // 登录失败,此处可以添加一些提醒Toast或对话框 |  |  |
|  |  |  |  |  |  | }) 登录成功后会自动跳转到直播页面,直播结束或手动返回会回到打开前的页 面。 | }) 登录成功后会自动跳转到直播页面,直播结束或手动返回会回到打开前的页 面。 | }) |  |  |
|     云播产品介绍   直播SDK     说明     直播Web-SDK     直播安卓-SDK     直播IOS-SDK   鸿蒙-SDK     鸿蒙版SDK介绍   鸿蒙-FastSDK     版本记录   接入方式   快速使用     鸿蒙-FineSDK     回放SDK     对接方案及资源 |  |  |  |  |  |  |  |  |  |  |
|  |   云播产品介绍 |  |  |  |  |  |  |  |  |  |
|  |   直播SDK   |  |  |  |  |  |  |  |  |  |
|  |   说明 |  |  |  |  |  |  |  |  |  |
|  |     直播Web-SDK |  |  |  |  |  |  |  |  |  |
|  |  |  |  |  |  |  |  |  |  |  |
|  |     直播安卓-SDK |  |  |  |  |  |  |  |  |  |
|  |     直播IOS-SDK |  |  |  |  |  |  |  |  |  |
|  |   鸿蒙-SDK   |  |  |  |  |  |  |  |  |  |
|  |   鸿蒙版SDK介绍 |  |  |  |  |  |  |  |  |  |
|  |   鸿蒙-FastSDK   |  |  |  |  |  |  |  |  |  |
|  |   版本记录 |  |  |  |  |  |  |  |  |  |
|  |   接入方式 |  |  |  |  |  |  |  |  |  |
|  |   快速使用 |  |  |  |  |  |  |  |  |  |
|  |     鸿蒙-FineSDK |  |  |  |  |  |  |  |  |  |
|  |     回放SDK |  |  |  |  |  |  |  |  |  |
|  |     对接方案及资源 |  |  |  |  |  |  |  |  |  |
|  |  |  |  |  |  |  |  |  |  |  |

| 不进行任   | 何处理,也   | 可以加提   | 示。   |
|---|---|---|---|

+

 

 

https://developer.263.net/web/#/28/1033
