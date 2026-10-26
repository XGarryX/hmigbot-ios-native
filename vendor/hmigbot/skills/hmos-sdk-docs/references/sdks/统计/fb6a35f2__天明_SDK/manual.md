# 集成 SDK

在开始集成之前,请在App 管理页面中创建您的应用以获得AppKey,并且确保下载了

Harmony版本的 SDK。

## 1 集成步骤

SDK 集成分单 HAP 项目、多 HAP 项目两种环境,集成方式有所区别,请注意区分。

### 1.1 单 HAP 项目

在Terminal窗口中进入HAP目录,执行如下命令:

```
ohpm install tianming
在AbilityStage的onCreate方法中初始化 SDK:
```

// entry/src/main/ets/abilitystage/MyAbilityStage.ts

import AbilityStage from"@ohos.app.ability.AbilityStage";

import{ AppInsight, AppInsightConfiguration }from"tianming";

exportdefaultclassMyAbilityStageextendsAbilityStage{

onCreate(){

const config =newAppInsightConfiguration({

      serverUrl:"http://localhost:8082",

      appKey:"appKey",

      isEnableLog:true,

}as AppInsightConfiguration);

    AppInsight.startWithConfiguration(this.context, config);

}

}

注 1:AppKey 请从 App 管理页面获取;

注 2:如果服务器 IP 地址格式不合法或者不正确,服务端无法收到数据。

### 1.2 多 HAP 项目

多 HAP 情况下, 直接引入 HAR 会导致存在多份相同拷贝,需要在 HSP 中间接引入

在Terminal窗口中进入HSP目录,执行如下命令:

```
ohpm install tianming
```

通过HSP导入再导出,保证多个HAP共享一份 SDK 实例:

// library/src/main/ets/index.ts

import{ AppInsight, AppInsightConfiguration }from"tianming";

const config =newTianmingConfig({

  serverUrl:"http://localhost:8082",

  appKey:"appKey",

  isEnableLog:true,

});

export{ AppInsight, config };

注 1:AppKey 请从 App 管理页面获取;

注 2:如果服务器 IP 地址格式不合法或者不正确,服务端无法收到数据。

```
在AbilityStage的onCreate方法中初始化 SDK:
```

// entry/src/main/ets/abilitystage/MyAbilityStage.ts

import AbilityStage from"@ohos.app.ability.AbilityStage";

import{ AppInsight, config }from"library";

exportdefaultclassMyAbilityStageextendsAbilityStage{

onCreate(){

    AppInsight.startWithConfiguration(this.context, config);

}

}

## 2 API 说明

AppInsight 提供多种 API 接口设置,从而实现对行为以及特定数据的追踪。

### 2.1 初始化应用,启动 SDK

2.1.1 初始化配置

```
startWithConfiguration(ctx: common.Context, config: AppInsightConfiguration):
void;
```

启动 AppInsight SDK,开始对应用数据捕获、上传,该方法需要在AbilityStage的

onCreate方法中执行,其他事项请参考1 集成步骤。

// entry/src/main/ets/abilitystage/MyAbilityStage.ts

import AbilityStage from"@ohos.app.ability.AbilityStage";

import{ AppInsight, AppInsightConfiguration }from"tianming";

const config =newAppInsightConfiguration({

  serverUrl:"http://localhost:8082",

  appKey:"appKey",

});

exportdefaultclassMyAbilityStageextendsAbilityStage{

onCreate(){

    AppInsight.startWithConfiguration(this.context, config);

}

}

```
AppInsightConfiguration可以进行配置的内容如下:
```

classAppInsightConfiguration{

// 数据上报的地址,如果是私有化部署,地址为部署的服务器地址

  serverUrl:string;

// Appkey 请从App管理页面获取

  appKey:string;

// 是否打开日志输出

  isEnableLog:boolean=false;

// 桥接 webinsight

  jsBridge:boolean=true;

// 数据上报间隔

  flushInterval:number=15_000;

// 进入后台多久结束会话,单位秒

  sessionBackgroundTime:number=5;

// 自动追踪页面事件

  autoTrackPage:boolean=false;

// 自动录制会话视频

  autoTrackReplay:boolean=false;

// 业务回放停止后,额外继续录制时长(毫秒)

  replayExtraTime:number=0;

// 是否采集屏幕分辨率($screen_width/$screen_height)

  enableScreenResolution:boolean=false;

}

2.1.2 设置会话后台时间

```
setSessionBackgroundTime(second: number): void;
```

注:单位为秒。

2.1.3 设置业务回放额外录制时长

```
setReplayExtraTime(replayExtraTime: number): void;
```

注:单位为毫秒,默认0。当值大于0时,调用stopTransactionReplay会延迟停止录

制。

### 2.2 设置用户信息

2.2.1 标识用户

```
setUserId(userId: string): void;
```

userId 作为唯一标识,请尽可能关联您的业务

该方法在startWithConfiguration之后任何时刻都可以被调用。

可以包含字母或数字。

最大长度不能超过 255 个字节。

2.2.2 设置用户属性

```
setUserProperty(propertyName: string, propertyValue: PropValue): void;
```

如果设置的用户属性名称在之前设置过,则会用新属性值替换旧属性值。该方法在

```
startWithConfiguration之后任何时刻都可以被调用。
```

propertyName:属性名

标识符,只允许大小写英文、数字以及下划线,且不能以数字开头。

不超过255字节长度,如果超长会被丢弃。

propertyValue:属性值

```
类型可以是String、Number、Boolean字符集合。
```

不超过500字节长度,如果超长度会被截断上报。

```
日期类型请参照yyyy-MM-dd HH:mm:ss或yyyy-MM-dd格式上报。
```

// 给当前用户设置单个属性

AppInsight.setUserProperty("Role","Admin");

2.2.3 设置多组用户属性

```
setUserProperties(userProperties: Props): void
```

用户属性值变化后会替换之前的旧的属性值。

userProperties:设置的用户的属性的 Props 对象。

// 给当前用户设置多个属性

const props: Props ={

  age:13,// 设置用户年龄,数值类型

  height:"1.75",// 请注意,这种将被识别成字符串类型

  height:1.75,// 设置用户身高,数值类型

  gender:"male",// 设置用户性别,字符串类型

  isVip:true,// 设置vip客户,布尔值类型

// 请注意,以下的情况都将识别为布尔值类型;

// 对于字符串的布尔值类型比对,将忽略大小写

// isVip, "false",

// isVip, "FalSe",

// isVip, "TRUE",

// isVip, "tRue",

// isVip, "true",

// 日期类型格式参照: yyyy-MM-dd HH:mm:ss或yyyy-MM-dd

  birthday:"2000-01-01",// 设置用户出生日期,日期类型

  registerTime:"2020-01-01 14:23:11",// 设置用户注册时间,日期类型

};

AppInsight.setUserProperties(props);

2.2.4 数值型累加属性

```
incUserProperty(propertyName: string, value: number = 1): void;
```

对用户的某个数字类型的属性进行累加操作。

propertyName:用户属性标识符

value:数字属性的值,可以递增或递减(设置为负值)

AppInsight.incUserProperty("score",100.12);// 增加用户的得分

2.2.5 删除用户属性

```
removeUserProperty(propertyName: string): void;
```

propertyName:已存在的用户属性标识符

AppInsight.removeUserProperty("source");// 删除用户的来源属性

|  | : |
|---|---|
|  | : |
| : |  |

2.2.6 设置经纬度

```
setLocation(latitude: number, longitude: number): void;
```

根据地理坐标来设置用户的位置信息

latitude : 纬度

longitude : 经度

AppInsight.setLocation(22.5431,114.0579);// 设置地理位置

2.2.7 设置 distinctId

如果不设置 distinctId,SDK 会自动生成一个 distinctId。如果想设置一个自定义的 distinctId,可

以在SDK初始化的时候调用以下接口:

```
identify(distinctId: string): void;
```

注:上面的接口只能在 SDK 初始化的时候调用。

2.2.8 设置 deviceID

在需要设置自定义设备标识时,可以使用此方法设定自定义设备 ID:

```
setCustomDeviceID(deviceID: string): void;
```

注:如果需要在打开应用等初始化事件中携带该属性,则需要在 startWithConfiguration 之

前调用

### 2.3 设置事件

2.3.1 添加自定义事件

```
addEvent(eventName: string): void;
```

该方法在startWithConfiguration之后任何时刻都可以被调用。

eventName

事件的标识符,只允许大小写英文、数字以及下划线,且不能以数字开头

不超过 255 字节长度的字符串

必须与平台中设置->事件设置中保持一致,否则数据无法正常入库会被服务器端丢弃

// 设置无属性事件:Login

AppInsight.addEvent("Login");

2.3.2 添加自定义事件并传入属性

```
addEvent(eventName: string, properties: Props = {}): void;
```

注:属性名称是指属性的标识符,标识符只允许大小写英文、数字以及下划线,且不能以数

字开头

可对事件添加一组或多组相关属性值:

eventName : 事件标识符

properties:事件属性的 Props 对象

key:属性的标识符

是指属性的标识符,只允许大小写英文、数字以及下划线,且不能以数字开头

不超过 255 字节长度的字符串

必须与平台中设置->事件设置中事件属性值保持一致,否则数据无法正常入库会被服

务器端丢弃,前端报表无法显示

value:属性的值

类型可以是字符串、数值、布尔值、字符串数组、数值数组

字符串字符长度不超过500字节,如果超过字符长度会被截断

```
日期类型请参照yyyy-MM-dd HH:mm:ss或yyyy-MM-dd格式上报
```

// 设置带属性事件:Purchase

const props: Props ={

  itemType:"Shoes",// 设置购买品类,字符串类型

  payModel:"Alipay",// 设置付款方式,字符串类型

  quantity:6,// 设置商品数量,数值类型

  price:"3.2",// 请注意,这种将被识别成字符串类型

  discount:false,// 设置是否使用优惠券,布尔值类型

// 请注意,以下的情况都将识别为布尔值类型;

// 对于字符串的布尔值类型比对,将忽略大小写

// discount, "false",

// discount, "FalSe",

// discount, "TRUE",

// discount, "tRue",

// discount, "true",

// 日期类型格式参照: yyyy-MM-dd HH:mm:ss或yyyy-MM-dd

  orderTime:"2020-11-11 23:59:59",// 设置订单时间

};

AppInsight.addEvent("Purchase", props);

### 2.4 设置敏感信息遮挡

2.4.1 设置遮挡区域

```
setReplayPrivacy(...privacy: Privacy[]): void;
```

设置了遮挡后,在回放中敏感信息将会被黑色条框遮挡住。

注 1:该方法应只在需要时设置,不需要时配合clearReplayPrivacy清除

注 2:可同时设置多个Privacy,每个Privacy一个图层,层级递增

注 3:每次调用setReplayPrivacy只保留最新的遮挡设置

Privacy类型定义如下:

|  | : |
|---|---|
| : |  |

interfacePrivacy{

  ids?:string[];// 需要遮挡范围

  rects?: Rect[];// 需要遮挡的范围

  includeId?:string;// 限制最大遮挡范围,溢出部分不遮挡,适用滚动场景

  includeRect?: Rect;// 限制最大遮挡范围,溢出部分不遮挡,适用滚动场景

  excludeId?:string;// 排除局部遮挡范围,适用于弹窗下面有遮挡导致弹窗被遮挡的场景

  excludeRect?: Rect;// 排除局部遮挡范围,适用于弹窗下面有遮挡导致弹窗被遮挡的场景

}

注:应优先使用组件 ID(可实时获取),仅在无法获取组件 ID 的情况下使用 Rect 范围,

比如系统弹窗等场景

AppInsight.setReplayPrivacy({

  ids:["inputBoxId"],// 遮挡 inputBoxId 对应的输入框

  includeId:"scrollBoxId",// 假设输入框在滚动组件中,限制遮挡不溢出滚动组件

});

2.4.2 清除遮挡区域

```
clearReplayPrivacy(): void;
```

注:应在不需要遮挡时立即调用

### 2.5 应用内嵌 WebView

要采集应用内嵌 WebView 的数据,需要打通原生和 H5

2.5.1 初始化 Web 组件

如果内嵌 h5 集成了 webinsight.js,需要配置 jsBridge: true

```
在Web组件onControllerAttached方法中执行registerWebview跟
initWebviewOnControllerAttached
```

onControllerAttached(()=>{

  AppInsight.registerWebview(this.controller,this.webId);

  AppInsight.initWebviewOnControllerAttached(this.controller);

});

```
在Web组件onPageBegin方法中执行initWebviewOnPageBegin跟activeWebview
```

| ? | : |  |  |
|---|---|---|---|
|  |  | ? | : |

| ? | : |  |  |
|---|---|---|---|
|  |  | ? | : |
| ? | : |  |  |
|  |  | ? | : |

onPageBegin(()=>{

  AppInsight.initWebviewOnPageBegin(this.controller,this.webId);

  AppInsight.activeWebview(this.controller);

});

2.5.2 更新 WebView 状态

在Web组件从不可见变成可见时,调用activeWebview

在Web组件从可见变成不可见时,调用inactiveWebview

2.5.3 埋点

打通原生和 H5 之后,会给 window 添加一个 webinsight 对象,可以通过这个对象直接在 h5 中

埋点。

// 用法同 addEvent

window.webinsight.track("eventId",{

  propertyKey1:"123",

  propertyKey2:2222,

});

2.5.4 内容遮挡

在管理后台应用管理里可以设置隐私遮挡策略,目前有三种策略,不遮挡用户的所有输入、仅遮

挡用户的密码输入和遮挡用户的所有输入,默认为遮挡用户的所有输入。内嵌的
WebView 默认

遮挡 input/textarea。

```
data-private
```

SDK 默认会对包含自定义属性 data-private 的元素进行遮挡,如果希望元素被遮挡,可以添

加自定义属性 data-private。

this is a sensitive div

```
window.webinsight.addSensitiveView(selector)
```

添加敏感视图,参数可以参考 HTML DOM querySelectorAll() 方法。将对应的 selector 进行

标记,SDK 会遮挡对应的元素。

if(window.webinsight){

  webinsight.addSensitiveView("#id");// by id

  webinsight.addSensitiveView("button");// by tagName

  webinsight.addSensitiveView(".example");// by className

}

### 2.6 开启和结束业务回溯

2.6.1 开启业务回溯

开启业务回溯需要调用下面的接口:

```
startTransactionReplayWithIdentifier(identifier: string): AppInsightTransaction;
```

上面的 identifier 参数是业务回溯的标志符,用来区分不同的业务回溯。

2.6.2 添加业务回溯相关属性

如果需要给业务回溯添加额外属性,则可以调用 AppInsightTransaction 类的 addProperties 方法

进行添加:

```
addProperties(key: string, value: PropValue): void;
```

key:属性的标识符

是指属性的标识符,只允许大小写英文、数字以及下划线,且不能以数字开头

不超过 255 字节长度的字符串

必须与平台中设置->事件设置中事件属性值保持一致,否则数据无法正常入库会被服务器

端丢弃,前端报表无法显示

value:属性的值

类型可以是字符串、数值、布尔值、字符串数组、数值数组

字符串字符长度不超过500字节,如果超过字符长度会被截断

```
日期类型请参照yyyy-MM-dd HH:mm:ss或yyyy-MM-dd格式上报
```

const transaction = AppInsight.startTransactionReplayWithIdentifier("下单业务");

transaction.addProperties("itemType","Shoes");// 设置购买品类,字符串类型

transaction.addProperties("payModel","Alipay");// 设置付款方式,字符串类型

transaction.addProperties("quantity",6);// 设置商品数量,数值类型

transaction.addProperties("price","3.2");// 请注意,这种将被识别成字符串类型

transaction.addProperties("price",3.2);// 设置商品价格,数值类型

transaction.addProperties("orderTime","2020-11-11 23:59:59");// 设置订单时间,日

期类型。eg: yyyy-MM-dd HH:mm:ss或yyyy-MM-dd

transaction.addProperties("discount",false);// 设置是否使用优惠券,布尔值类型

2.6.3 结束业务回溯

结束业务回溯需要调用下面的接口:

```
stopTransactionReplay(uploadVideo: boolean, callback?: VideoUploadCallback):
void;
```

uploadVideo参数用来控制是否上传回溯视频。如果该参数为true时上传回溯视频,否

则不上传。

当视频上传完毕后,会把上传结果传给callback参数。如果没有特殊需要,不用设置

```
callback
```

注意事项:

```
1、在uploadVideo为false的情况下不会触发callback
```

2、在退出应用等拿不到网络回调的场景也不会触发callback

3、callback中拿到失败参数仅代表当前上传失败,sdk有缓存重试机制,会多次尝试上

报

### 2.7 上报自定义页面

```
addScreen(screenName: string, screenTitle?: string): void;
```

### 2.8 获取会话 ID

```
getSessionID(): string;
```

### 2.9 采集性能数据

采集性能数据需要打开远程配置里面的 APM 开关网络数据采集需要使用 sdk 提供的代理网

络接口

2.9.1 采集 axios 请求数据

```
useAxiosIntercept(axios: AxiosInstance): void;
```

在使用axios进行网络请求之前,调用useAxiosIntercept注册监听器,之后的axios网络

请求即可被sdk采集

2.9.2 采集 rcp.createSession 请求数据

```
使用AppInsight.createSession替代rcp.createSession创建session请求,后续使用该
```

session的请求即可被sdk采集

2.9.3 采集 http.createHttp 请求数据

```
使用AppInsight.createHttp替代http.createHttp创建http请求,该请求即可被sdk
```

采集

2.9.4 采集崩溃数据

打开远程的 APM 配置后,崩溃数据会自动采集,但由于应用发生崩溃时是立即退出的,崩溃数

据只能在下一次打开应用时采集上报,具有延迟的特点
