# **HarmonyOS SDK** 

## **注意事项** 

### **版本说明** 

暂不支持多线程 / 多进程,鸿蒙系统比较特殊,采取线程间进程隔离,需额外适配方案。 

## **1. 集成SDK** 

诸葛 HarmonyOS SDK 要求最低接入的鸿蒙版本为 API 12 及以上。 

### **1.1 获取SDK** 

您需要联系诸葛技术支持获取 zhugeio.har 文件,该文件为鸿蒙 SDK 的离线包。 

### **1.2 添加 zhugeioSDK 到项目中** 

将 zhugeio.har 文件,放到主工程目录 entry 的 libs 目录下,然后在 DevEco Studio 的 Termial 窗口中切换到需要引入本地模块源码的模块,即 entry 模块下,执行如下命令进行安装,该命令会在该模块下的 oh-package.json5 中自动添加 依赖。 

cd path/to/your/project/entry ohpm install path/to/zhugeiosdk/zhugeio.har 

##### 看到如下输出即代表成功引入 

install completed in 0s 84ms 

### **1.3添加所需权限** 

在 entry 的 module.json5 文件中,添加如下权限: 

{ "module": { ... "requestPermissions": [ { "name": "ohos.permission.INTERNET", "reason": "$string:internet_permission" }, { "name": "ohos.permission.GET_NETWORK_INFO", "reason": "$string:internet_permission" } ] } } 

### **权限说明** 

|**权限**|**说明**|**使用场景和目的**|
|---|---|---|
|ohos.permission.INTERNET|发送网络请 求|上报数据到服务器|
|ohos.permission.GET_NETWORK_INFO|获取网络状 态|数据采集,获取设备网络信 息|

## **2. 初始化SDK** 

说明 

建议您在用户同意您App中的隐私政策后,再进行 SDK 初始化。 

### **2.1 获取 APPKEY** 

在开始集成前,首先拥有一个应用/主体,进行SDK集成前,您需要获取对应应用/主体的App Key信息。 

您可以在「应用管理」->「主体管理」->「设置」中可查看您的App Key 

### **2.2 获取数据上送地址** 

私有化部署版本需要获取数据上报地址。 

如您不清楚此地址,请联系您的项目经理或技术支持。 

### **2.3 初始化 SDK** 

- 鸿蒙将 startWithConfig 与 agreePrivacy 完全分离。 

   - startWithConfig 之后才可以调用 SDK 的各种方法,SDK 不支持 

   - startWithConfig 之前进行埋点。 

   - agreePrivacy 之后才开始采集及上报数据,调用前触发的埋点会被暂存,待同意隐 

   - 私协议之后进行上传。 

   - 如果创建了 AbilityStage ,可以将 startWithConfig 放在 

   - AbilityStage 的 onCreate 中,可以在这里初始化 SDK,然后在隐私弹窗后再 

   - 调用 agreePrivacy 。 

- 使用 ZhugeioConfig 实体类来定义信息,然后使用该参数初始化SDK: 

import {Zhugeio, ZhugeioConfig } from 'zhugeio'; 

// 创建实例 let config = new ZhugeioConfig() config.appKey = "appkey" config.appChannel = "appchannel" // 设置上报地址(默认为saas地址) config.setServerUrl("https://su.zhugeio.com/apipool") // 开启兼容模式(旧版本分析平台需开启此配置,saas已支持,可忽略此配置项) config.compatible = true let sdk = Zhugeio.getInstance() sdk.startWithConfig(this.context,config) 

// 用户同意隐私后调用该方法 Zhugeio.agreePrivacy() 

Zhugeio.getInstance() 该方法返回Zhugeio SDK全局默认的实例对象,若无多主体需 要,下方的所有接口均可通过该方法返回的实例调用。 

##### 参数说明: 

|**参数**|**说明**|
|---|---|
|context|应用上下文|
|appKey|官网申请的appKey|
|appChannel|应用分发渠道|

上述三个参数为SDK必须的参数,不能为空。 

#### **2.3.1 ZhugeioConfig 参数选项** 

ZhugeioConfig 是SDK初始化的配置参数载体,各项功能开关及自定义选项均通过该参数 来传递,可选配置项有: 

|**参数名称**|**类型**|**含义**|**默认值**|
|---|---|---|---|
|appKey|string|应用标识|无默认,必传参数|
|appChannel|string|应用渠道|无默认,必传参数|
|did|string|设备did|可选配置,若需要自己定义用户 设备标识,可在初始化时传入|
|debug|boolean|是否开启实时调试|false,不开启|
|compatible|boolean|是否开启兼容上传 模式|false,不开启|
|business|string|该实例对应业务ID|空|
|sendLimit|number|触发上传时本地数 据数量|默认为1,实时上传|
|sessionExceed|number|会话间隔,当应用 从后台回到前台 时,相距多长时间 算同一会话,秒为 单位|30秒|
|encrypt|boolean|是否开启加密|默认为false|
|RSAPubKey|string|ras加密公钥|默认密钥(saas不支持修改秘钥)|
|autoTrackEnable|boolean|是否开启全埋点|默认为false|
|durationOnPage|boolean|是否开启页面时长 统计|默认为false|
|encryptType|number|加密类型|ZhugeioConfg.ENCRYPT_RSA|
|exceptionEnable|boolean|是否开启崩溃采集|默认为false|

#### **2.3.2 设置上传地址** 

私有部署客户可以通过zhugeioConfig.setServerUrl()方法设置数据上传地址,请不要给 serverUrl直接赋值,会导致上传地址出错。 

url为服务器端数据采集接口所在 完整路径,参考示例如下: 

let zhugeioConfig = new ZhugeioConfig() zhugeioConfig.appKey = "appkey" zhugeioConfig.appChannel = "hm" zhugeioConfig.encrypt = true zhugeioConfig.autoTrackEnable = true zhugeioConfig.setServerUrl("https://su.zhugeio.com/apipool") Zhugeio.getInstance().startWithConfig(this.context,zhugeioConfig) 

### **2.4 多实例初始化(可选,多主体/多实例 场景)** 

调用 new Zhugeio() 来获得一个新的SDK实例。然后针对每一个实例,定义上方的 ZhugeioConfig ,然后通过 ZhugeioConfig 来初始化对应的实例 

import {Zhugeio, ZhugeioConfig } from 'zhugeio'; 

// 创建实例 let config = new ZhugeioConfig() config.appKey = "appkey" config.appChannel = "appchannel" // 开启兼容模式(旧版本分析平台需开启此配置,saas已支持,可忽略此配置项) config.compatible = true let zg_user = new Zhugeio() zg_user.startWithConfig(this.context,config) 

// 用户同意隐私后调用该方法 Zhugeio.agreePrivacy() 

### **2.5 隐私弹窗处理** 

在用户同意您App中的隐私政策后,调用 agreePrivacy() 接口,开始采集及上报数据, 在调用之前采集的数据不会被上报。 

// 注意:此处需要使用 Zhugeio 类调用,全局生效 Zhugeio.agreePrivacy() 

调用此方法后隐私协议同意状态数据存储在应用缓存中,如缓存被清理,需重新调用 agreePrivacy() 接口。 

### **2.6 开启日志** 

若需开启或关闭诸葛相关的日志,请在初始化之前调用如下接口 

Zhugeio.setLogEnable(enable:boolean);// 注意:此处需要使用 Zhugeio 类调用,全 

## **3. 埋点采集** 

以下接口,对应的SDK实例,均需初始化过才可使用 

注意:下面调用方法是基于 sdk.xxx 进行调用,其中 sdk 为初始化后的SDK实例对 象,参考 2.3 章节。 

### **3.1 识别用户** 

为了保持对用户的跟踪,你需要为他们记录一个识别码,你可以使用用户id、email等唯一值 来作为用户的识别码。另外,你可以在跟踪用户的时候, 记录用户更多的属性信息,便于你 更了解你的用户: 

sdk.identify(uid:string, prop?: HashMap<string, object>); 

##### 参数说明: 

|**参数**|**说明**|
|---|---|
|uid|用户唯一标识|
|prop|用户属性|

##### 代码示例: 

//定义用户识别码 let userid = user.getUserId(); //定义用户属性 let personObject = new HashMap<string,Object>() personObject.set("avatar", "http://tp4.sinaimg.cn/5716173917/1") personObject.set("name", "张三");personObject.put("gender", "男") personObject.set("等级", 90) //标识用户 sdk.identify(userid, personObject) 

### **3.2 自定义事件** 

在你希望记录用户行为的位置,自定义事件,调用如下代码: 

sdk.track(eventName: string, prop?: HashMap<string, Object>) 

参数说明: 

|**参数**|**说明**|
|---|---|
|eventName|事件名称|
|prop|事件属性|

代码示例: 

//定义与事件相关的属性信息 let eventObject = new HashMap<string,Object>() eventObject.set("分类", "手机") eventObject.set("名称", "iPhone6 plus 64g") //数值型属性不要带引号 eventObject.set("价格",  5888) //记录事件 sdk.track("购买",  eventObject) 

**注意:** 在添加事件属性时,需注意事件属性类型。如果事件属性类型为「数值型属性」,需 要在上传数据时修改数据类型为「数值型」,并且在诸葛io后台埋点管理中修改为「数值 型」。 

### **3.3 事件时长统计** 

若你希望统计一个事件发生的时长,比如视频的播放,页面的停留,那么可以调用如下接口来 进行: 

sdk.startTrack(eventName: string) 

说明:调用 startTrack() 来开始一个事件的统计,eventName为一个事件的名称 

sdk.endTrack(eventName: string, prop?: HashMap<string, object>) 

说明:调用 endTrack() 来记录事件的持续时长。调用 endTrack() 之前,相同 eventName的事件必须已经调用过 startTrack() ,否则这个接口并不会产生任何事件。 

代码示例: 

//视频播放开始 sdk.startTrack("观看视频") //视频观看结束 let pro = new HashMap<string,Object>() pro.put("名称","非诚勿扰") pro.put("期数","2016-11-02") sdk.endTrack("观看视频",pro) 

**注意:** startTrack() 与 endTrack() 必须成对出现( eventName 一致),单独调 用一个接口是无效的。 

### **3.4 在内嵌 WebView 采集** 

如果你的页面中使用了 WebView 嵌入 HTML、JavaScript 的代码,并且希望统计 HTML 中 的事件,那么可以通过下面的文档来进行跨平台的统计。 

SDK版本要求:鸿蒙SDK版本 >=v1.0.5 ,H5使用的 js sdk 版需 >=v4.1.0 。 

##### 在web组件初始化时进行如下操作: 

```arkts
import { webview } from '@kit.ArkWeb'; @Entry @Component struct WebPage { controller: webview.WebviewController = new webview.WebviewController() 
```

build() { //找到web组件 Web({ src: "https.url", controller: this.controller }) //设置zhuge对象 .javaScriptProxy({ object: new ZhugeioJS(), name: ZhugeioJS.NAME_ZHUGEJS, methodList:ZhugeioJS.METHOD_ARRAY, controller:this.controller }) .domStorageAccess(true) } } 

### **3.5 全局属性设置** 

如果有一些属性是每个事件都需要采集的,可以通过设置为全局属性实现,设置后,后续的每 个事件都会自动添加该属性。 

如果有相同的属性名,事件自身传入的属性值会覆盖全局属性的设置。 

#### **3.5.1 设置全局属性** 

该接口设置的属性会覆盖之前所设置的: 

Zhugeio.getInstance().setSuperProperty(prop :Record<string, Object>) 

#### **3.5.2 设置单个key、value全局属性** 

该接口会合并到之前已设置的全局属性中 

Zhugeio.getInstance().setSuperPropertyKey(key:string,value:Object) 

#### **3.5.3 添加全局属性,会合并到之前的全局属性中** 

Zhugeio.getInstance().addSuperProperties(prop :Record<string, Object>) 

#### **3.5.4 删除单个全局属性** 

Zhugeio.getInstance().deleteSuperPropertyKey(key:string) 

#### **3.5.5 删除全部全局属性** 

Zhugeio.getInstance().deleteAllSuperProperty() 

## **4. 注意事项** 

- 必须在 UIAbility 的 onCreate 方法调用 

- Zhugeio.getInstance().startWithConfig() 完成初始化。 

- 隐私合规:只有在调用 Zhugeio.agreePrivacy() 后,SDK 才会上传数据。 SuperProperty 建议只保存小体量 KV 数据,不要存储大对象。 

## **更新记录** 

### **v1.1.0** 

发布时间:2025-10-16 

- 新增 鸿蒙全埋点(pv、click)采集支持 

- 新增 鸿蒙页面浏览时长(dr)采集支持 

- 新增 鸿蒙国密加密上报支持 

- 新增 鸿蒙修改数据上报机制:异步改成并发上报 

- 新增 支持上报时间配置,默认5s上报一次 

- 新增 鸿蒙事件全局属性采集支持 

- 新增 鸿蒙崩溃事件采集支持 

**v1.0.5** 

发布时间:2025-03-15 

增加 H5 内嵌 WebView 采集功能 

### **v1.0.4** 

发布时间:2025-02-26 

- 修复 断网场景下数据处理bug 

- 修改 上报地址设置方式(由只设置域名改为设置完整路径,客户升级需要重新设置) 

### **v1.0.1** 

发布时间:2024-09-30 

- 增加隐私协议合规处理方法 agreePrivacy (注意:v1.0.0升级后,需在客户同意隐私 协议后调用此方法,否则无法采集数据) 

Zhugeio.agreePrivacy() 

### **v1.0.0** 

发布时间:2024-08-12 

- 初始化版本 

- 采集用户信息 

- 采集自定义事件 

- 采集事件时长
