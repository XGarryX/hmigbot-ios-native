# 友盟统计分析 U-App 鸿蒙版 SDK 接口文档 

# 系统 API 要求 

支持 HarmonyOS NEXT API12 以上,仅支持普通应用 stage 模式,暂 不支持元服务。 

# SDK 方法说明 

preInit(context:common.ApplicationContext,plugins: [internalPlugin]) 

预初始化 , 需要在 abilityStage 的 onCreate 方法内调用 

init() 

用户同意隐私政策后调用 , 方法调用后才会进行采集和日志传输 , 需要 开发者自行记录用户是否同意了隐私政策,并在判断用户同意隐私政 策时才可调用 init 方法 

onEventObject(eventID: string, params?: Record<string, string | number>) 

自定义事件,可在用户同意 init 之前调用,最多缓存 1000 事件 

eventID ,事件 id ,字符串 128 位以内的非空字符串 

params, 事件属性,可选参数,属性 key , 128 位以内的非空字符串, value 为 256 位以内的数值或字符串 

特别的,事件 id 和属性 key 不能为一下保留关键字 [“id”, “ts”, “du”, “ds”, “duration”, “pn”, “token”, “device_name”, “device_model”, “device_brand”, “country”, “city”, “channel”, “province”, “appkey”, “app_version”, “access”, “launch”, “pre_app_version”, “terminate”, “no_first_pay”, “is_newpayer”, “first_pay_at”, “first_pay_level”, “first_pay_source”, “first_pay_user_level”, “first_pay_version”, “type”]; 

onProfileSignIn(provider:string,puid:string) 

账号登入,用户同意隐私政策后调用 

provider 开发者自定义的账号类型,非空字符串,且长度不超过 32 puid 开发者自定义的账号,非空字符串,且长度不超过 64 onProfileSignOff() 

账号登出,用户同意隐私政策后调用 

setLogEnabled(enable:boolean) 

日志开关,默认关闭 

自定义事件 

在 UI 线程中埋点,以下代码演示了如何在某个页面的某个按钮的点击 事件埋点 

import { onEventObject } from '@umeng/analytics'; 

Button(' 自定义事件 X1').onClick(() => { 

onEventObject("eventid", { 

param: "value" 

}); 

}); 

在 worker 线程中 , 以下代码演示了如何在 worker 线程中埋点 

```arkts
import worker, { ThreadWorkerGlobalScope, MessageEvents, ErrorEvent } from '@ohos.worker'; 
```

import { onEventObject } from '@umeng/analytics'; 

const workerPort: ThreadWorkerGlobalScope = worker.workerPort; 

/** 

* Defines the event handler to be called when the worker thread receives a message sent by the host thread. 

- The event handler is executed in the worker thread. 

* @param e message data 

*/ 

workerPort.onmessage = function (e: MessageEvents) { 

onEventObject("workerevent4", {a: 1}) 

} 

/** 

* Defines the event handler to be called when the worker receives a message that cannot be deserialized. 

- The event handler is executed in the worker thread. 

- @param e message data 

*/ 

workerPort.onmessageerror = function (e: MessageEvents) { 

} 

/** 

* Defines the event handler to be called when an exception occurs during worker execution. 

- The event handler is executed in the worker thread. 

- @param e error message 

*/ 

workerPort.onerror = function (e: ErrorEvent) { 

} 

暂未提供 c++ 中直接调用的方法,需要参考鸿蒙官网 c++ 和 arkts 互 通的知识,通过 NAPI 的方式来调 onEventObject 方法实现埋点。 

更多内容请参考友盟官方文档说明: https://developer.umeng.com/ docs/119267/detail/2712046
