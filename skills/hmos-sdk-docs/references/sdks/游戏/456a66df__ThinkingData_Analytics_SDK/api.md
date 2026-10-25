# OpenHarmony SDK接口文档

# API接口概览

## 初始化

## init

| 接口参数列表 | 描述 |
|---|---|
| context | 上下文 |
| appId | 您的项目的 APPID,可通过在 TE 项目管理页面获取 |
| serverUrl | 数据上传的 URL |

## initWithConfig

| 接口参数列表 | 描述 |
|---|---|
| context | 上下文 |
| config | 初始化参数 |
| config.appId | 您的项目的 APPID,可通过在 TE 项目管理页面获取 |
| config.serverUrl | 数据上传的 URL |
| config.enableAutoCalibrated | 是否允许自动开启时间校准 |
| config.mode | SDK上报模式,默认为Normal模式 |
| config.version | 加密公钥版本 |
| config.publicKey | 加密公钥 |
| config.defaultTimeZone | 默认时区 |
| config.disablePresetProperties | 预置属性开关 |
| config.dataExpression | 本地数据过期时间 |

## 访客 ID

## setDistinctId

| 接口参数列表 | 描述 |
|---|---|
| distinctId | 访客 ID |

```
// 将访客ID设置为Thinker
TDAnalytics.setDistinctId("Thinker");
```

## getDistinctId

```
//返回访客ID
let distinctId = TDAnalytics.getDistinctId();
```

## 账号ID

## login

```
1
```

//用户的登录唯一标识,此数据对应上报数据里的#account_id,此时#account_id的值为TA

| 接口参数列表 | 描述 |
|---|---|
| accountId | 账号ID |

```
2
TDAnalytics.login("TA");
```

## logout

```
// 去除上报数据里的 "#account_id",之后的数据将不带有 "#account_id"
TDAnalytics.logout();
```

## getAccountId

```
//返回账号ID
let accountId = TDAnalytics.getAccountId();
```

## 发送事件

## track

| 接口参数列表 | 描述 |
|---|---|
| options | 事件上报参数 |
| options.eventName | 事件名称 |
| options.properties | 事件属性 |
| options.time | 事件时间 |
| options.timeZone | 事件时区 |

```
TDAnalytics.track({
eventName: "product_buy", // 事件名称
properties: {
product_name: "商品名"
    } //事件属性
});
```

## trackFirst

| 接口参数列表 | 描述 |
|---|---|
| options | 事件上报参数 |

```
TDAnalytics.trackFirst({
eventName: "device_activation",
firstCheckId: "TA",
properties: {
key: "value"
    }
 });
```

options.eventName

事件名称

| options.properties | 事件属性 |
|---|---|
| options.firstCheckId | 自定义事件ID |
| options.time | 事件时间 |
| options.timeZone | 事件时区 |

## trackUpdate

| 接口参数列表 | 描述 |
|---|---|
| options | 事件上报参数 |
| options.eventName | 事件名称 |
| options.properties | 事件属性 |
| options.eventId | 事件ID |
| options.time | 事件时间 |
| options.timeZone | 事件时区 |

```
TDAnalytics.trackUpdate({
eventName: "UPDATABLE_EVENT",
properties: { status: 3, price: 100 },
eventId: "test_event_id"
});
```

## trackOverwrite

```
TDAnalytics.trackOverwrite({
eventName: "OVERWRITE_EVENT",
properties: { status: 3, price: 100 },
eventId: "test_event_id"
});
```

| 接口参数列表 |  |
|---|---|
| options | 事件上报参数 |
| options.eventName | 事件名称 |
| options.properties | 事件属性 |
| options.eventId | 事件ID |
| options.time | 事件时间 |
| options.timeZone | 事件时区 |

## flush

```
TDAnalytics.flush();
1
```

## 公共事件属性

## setSuperProperties

```
1
```

// 设置公共事件属性,所有数据事件中都会带有这些属性

| 接口参数列表 | 描述 |
|---|---|
| properties | 静态公共属性 |

```
TDAnalytics.setSuperProperties({
channel: "渠道名",
user_name: "用户名"
});
```

## getSuperProperties

```
// 获取静态公共事件属性
let superProperties = TDAnalytics.getSuperProperties();
```

## unsetSuperProperty

```
1
```

// 清除一条静态公共事件属性,比如将之前设置 'channel' 属性清除,之后的数据将不会该属性

| 接口参数列表 | 描述 |
|---|---|
| property | 静态公共属性的key |

```
2
TDAnalytics.unsetSuperProperty("channel");
```

## clearSuperProperties

```
// 清除所有静态公共事件属性
TDAnalytics.clearSuperProperties();
```

## setDynamicSuperProperties

```
1
```

// 设置动态公共属性,在事件上报时触发回调函数,并把返回的JSON对象加入到事件属性中

| 接口参数列表 | 描述 |
|---|---|
| callback | 动态公共属性函数 |

```
TDAnalytics.setDynamicSuperProperties(() => {
return {
dy_name: 'xxx',
dy_age: 18
  }
})
```

## 记录事件时长

## timeEvent

```
//以下示例,完成用户在某个商品页面停留时长的统计
TDAnalytics.timeEvent("stay_shop");
/**do someting
    .......
**/
//用户离开商品页面,计时结束,"stay_shop" 这一事件中将会带有表示事件时长的属性
#duration
```

| 接口参数列表 | 描述 |
|---|---|
| eventName | 事件名称 |

```
TDAnalytics.track({
eventName: "stay_shop",
properties: {
product_name: "商品名"
    }
});
```

## 用户属性

## userSet

| 接口参数列表 | 描述 |
|---|---|
| options | 事件上报参数 |
| options.properties | 用户属性 |
| options.time | 用户属性上报时间 |
| options.timeZone | 用户属性上报时区 |

```
TDAnalytics.userSet({
properties: {
username: "TA"
    }
});
```

## userSetOnce

```
TDAnalytics.userSetOnce({
properties: {
first_payment_time: "2018-01-01 01:23:45.678"
    }
});
```

| 接口参数列表 |  |
|---|---|
| options | 事件上报参数 |
| options.properties | 用户属性 |
| options.time | 用户属性上报时间 |
| options.timeZone | 用户属性上报时区 |

## userAdd

| 接口参数列表 | 描述 |
|---|---|
| options | 事件上报参数 |
| options.properties | 用户属性 |
| options.time | 用户属性上报时间 |
| options.timeZone | 用户属性上报时区 |

```
TDAnalytics.userAdd({
properties: {
total_revenue: 30
    }
});
```

## userUnset

```
1
```

// 清空该用户属性名为 userPropertykey 的用户属性值,即设置成 NULL

| 接口参数列表 | 描述 |
|---|---|
| options | 事件上报参数 |
| options.property | 用户属性key |

```
TDAnalytics.userUnset({
property: "userPropertykey"
});
```

options.time

用户属性上报时间

| options.timeZone | 用户属性上报时区 |
|---|---|

## userDelete

```
TDAnalytics.userDelete();
1
```

## userAppend

| 接口参数列表 | 描述 |
|---|---|
| options | 事件上报参数 |
| options.properties | 用户属性 |
| options.time | 用户属性上报时间 |
| options.timeZone | 用户属性上报时区 |

```
TDAnalytics.userAppend({
properties: {
user_list: ["apple", "ball"]
    }
});
```

## userUniqAppend

| 接口参数列表 | 描述 |
|---|---|
| options | 事件上报参数 |

```
TDAnalytics.userUniqAppend({
properties: {
user_list: ["apple", "cube"]
    }
});
```

options.properties

用户属性

| options.time | 用户属性上报时间 |
|---|---|
| options.timeZone | 用户属性上报时区 |

## 开启与 H5 页面的打通

| 接口参数列表 | 描述 |
|---|---|
| controller | Webview控制器 |

```
controller: webview.WebviewController = new webview.WebviewController();
TDAnalytics.setJsBridge(controller)
```

## 自动采集

## enableAutoTrack

| 接口参数列表 | 描述 |
|---|---|
| context | 上下文 |
| types | 自动采集事件枚举 |

```
//APP安装事件 TDAutoTrackEventType.APP_INSTALL
//APP启动事件 TDAutoTrackEventType.APP_START
//APP关闭事件 TDAutoTrackEventType.APP_END
//APP浏览页面事件 TDAutoTrackEventType.APP_VIEW_SCREEN
//APP点击控件事件 TDAnalytics.TDAutoTrackEventType.APP_CLICK
//APP崩溃事件 TDAutoTrackEventType.APP_CRASH
TDAnalytics.enableAutoTrack(context,TDAutoTrackEventType.APP_START |
TDAutoTrackEventType.APP_INSTALL | TDAutoTrackEventType.APP_END |
TDAutoTrackEventType.APP_VIEW_SCREEN | TDAutoTrackEventType.APP_CLICK |
TDAutoTrackEventType.APP_CRASH)
```
