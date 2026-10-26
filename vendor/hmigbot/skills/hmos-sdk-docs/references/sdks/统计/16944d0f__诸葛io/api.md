# **HarmonyOS SDK API** 

## **设置上传地址** 

私有部署客户可以通过zhugeioConfig.setServerUrl()方法设置数据上传地址,请不要给 serverUrl直接赋值,会导致上传地址出错。 

url为服务器端数据采集接口所在 完整路径,参考示例如下: 

let zhugeioConfig = new ZhugeioConfig() zhugeioConfig.appKey = "appkey" zhugeioConfig.appChannel = "hm" zhugeioConfig.encrypt = true zhugeioConfig.autoTrackEnable = true zhugeioConfig.setServerUrl("https://su.zhugeio.com/apipool") Zhugeio.getInstance().startWithConfig(this.context,zhugeioConfig) 

## **隐私弹窗处理** 

在用户同意您App中的隐私政策后,调用 agreePrivacy() 接口,开始采集及上报数据, 在调用之前采集的数据不会被上报。 

// 注意:此处需要使用 Zhugeio 类调用,全局生效 Zhugeio.agreePrivacy() 

调用此方法后隐私协议同意状态数据存储在应用缓存中,如缓存被清理,需重新调用 agreePrivacy() 接口。 

## **开启日志** 

若需开启或关闭诸葛相关的日志,请在初始化之前调用如下接口 

Zhugeio.setLogEnable(enable:boolean);// 注意:此处需要使用 Zhugeio 类调用,全 

## **识别用户** 

为了保持对用户的跟踪,你需要为他们记录一个识别码,你可以使用用户id、email等唯一值 

来作为用户的识别码。另外,你可以在跟踪用户的时候, 记录用户更多的属性信息,便于你 更了解你的用户: 

sdk.identify(uid:string, prop?: HashMap<string, object>); 

### 参数说明: 

|**参数**|**说明**|
|---|---|
|uid|用户唯一标识|
|prop|用户属性|

### 代码示例: 

//定义用户识别码 let userid = user.getUserId(); //定义用户属性 let personObject = new HashMap<string,Object>() personObject.set("avatar", "http://tp4.sinaimg.cn/5716173917/1") personObject.set("name", "张三");personObject.put("gender", "男") personObject.set("等级", 90) //标识用户 sdk.identify(userid, personObject) 

## **自定义事件** 

### 在你希望记录用户行为的位置,自定义事件,调用如下代码: 

sdk.track(eventName: string, prop?: HashMap<string, Object>) 

### 参数说明: 

|**参数**|**说明**|
|---|---|
|eventName|事件名称|
|prop|事件属性|

代码示例: 

//定义与事件相关的属性信息 let eventObject = new HashMap<string,Object>() eventObject.set("分类", "手机") eventObject.set("名称", "iPhone6 plus 64g") //数值型属性不要带引号 eventObject.set("价格",  5888) //记录事件 sdk.track("购买",  eventObject) 

**注意:** 在添加事件属性时,需注意事件属性类型。如果事件属性类型为「数值型属性」,需 要在上传数据时修改数据类型为「数值型」,并且在诸葛io后台埋点管理中修改为「数值 型」。 

## **事件时长统计** 

若你希望统计一个事件发生的时长,比如视频的播放,页面的停留,那么可以调用如下接口来 进行: 

sdk.startTrack(eventName: string) 

说明:调用 startTrack() 来开始一个事件的统计,eventName为一个事件的名称 

sdk.endTrack(eventName: string, prop?: HashMap<string, object>) 

说明:调用 endTrack() 来记录事件的持续时长。调用 endTrack() 之前,相同 eventName的事件必须已经调用过 startTrack() ,否则这个接口并不会产生任何事件。 

代码示例: 

//视频播放开始 sdk.startTrack("观看视频") //视频观看结束 let pro = new HashMap<string,Object>() pro.put("名称","非诚勿扰") pro.put("期数","2016-11-02") sdk.endTrack("观看视频",pro) 

**注意:** startTrack() 与 endTrack() 必须成对出现( eventName 一致),单独调 用一个接口是无效的。 

## **在内嵌 WebView 采集** 

如果你的页面中使用了 WebView 嵌入 HTML、JavaScript 的代码,并且希望统计 HTML 中 

的事件,那么可以通过下面的文档来进行跨平台的统计。 

SDK版本要求:鸿蒙SDK版本 >=v1.0.5 ,H5使用的 js sdk 版需 >=v4.1.0 。 

### 在web组件初始化时进行如下操作: 

```arkts
import { webview } from '@kit.ArkWeb'; @Entry @Component struct WebPage { controller: webview.WebviewController = new webview.WebviewController() 
```

build() { //找到web组件 Web({ src: "https.url", controller: this.controller }) //设置zhuge对象 .javaScriptProxy({ object: new ZhugeioJS(), name: ZhugeioJS.NAME_ZHUGEJS, methodList:ZhugeioJS.METHOD_ARRAY, controller:this.controller }) .domStorageAccess(true) } } 

## **设置全局属性** 

### 该接口设置的属性会覆盖之前所设置的: 

Zhugeio.getInstance().setSuperProperty(prop :Record<string, Object>) 

## **设置单个key、value全局属性** 

### 该接口会合并到之前已设置的全局属性中 

Zhugeio.getInstance().setSuperPropertyKey(key:string,value:Object) 

## **添加全局属性,会合并到之前的全局属性中** 

Zhugeio.getInstance().addSuperProperties(prop :Record<string, Object>) 

## **删除单个全局属性** 

Zhugeio.getInstance().deleteSuperPropertyKey(key:string) 

## **删除全部全局属性** 

Zhugeio.getInstance().deleteAllSuperProperty()
