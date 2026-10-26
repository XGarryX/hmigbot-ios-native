# 友盟统计分析 U-App 鸿蒙版 SDK 使用指南 

系统 API 要求 

HarmonyOS NEXT API12 以上,仅支持普通应用 stage 模式,暂不支 持元服务。 

快速开始 

安装 sdk 

在项目的跟目录下执行如下命令 

ohpm install @umeng/common --registry=https:// ohpm.openharmony.cn/ohpm 

ohpm install @umeng/analytics --registry=https:// ohpm.openharmony.cn/ohpm 

# 集成 

在项目的 AppScope/resources/rawfile 目录下新增一个配置文件 umconfig.json 

{ 

"appKey": " 你的 apppkey", 

"channel": " 你的渠道 " 

} 

在应用模块目录下,添加 abilityStage 工程文件,例如 entry/src/ main/ets/abilityStage/MyAbilityStage.ets ,具体位置如截图: 

# 参考代码如下: 

import AbilityStage from '@ohos.app.ability.AbilityStage'; 

import { preInit, InternalPlugin, setLogEnabled, init, onEventObject } from '@umeng/analytics'; 

setLogEnabled(true); // 开发时,打开调试日志,可观察 sdk 是否集成 成功 

export default class MyAbilityStage extends AbilityStage { 

onCreate() { 

preInit({ 

context: this.context.getApplicationContext(), 

plugins: [new InternalPlugin()] 

}); 

init(); // 在用户同意隐私政策后再调用此方法 

onEventObject("eventA", { 

"key": "value" 

}); // 埋个点 

} 

} 

在模块的的 module.json5 文件中添加 srcEntry ,指向 abilityStage 文 件的地址 在模块的 module.json5 文件中添加权限声明 

"requestPermissions": [{ 

"name": "ohos.permission.APP_TRACKING_CONSENT", 

"reason": "$string:reason", // 如果 IDE 提示错误,需自行在 entry/src/ main/resources/base/element/string.json ,中添加对应信息 

"usedScene": {} 

} , { 

"name": "ohos.permission.INTERNET" 

} , { 

"name": "ohos.permission.GET_NETWORK_INFO" 

} 

] 

注意上述代码中, "$string:reason" 为用户自定义内容,如果 IDE 提 示 "$string:reason", 错误,需自行在 entry/src/main/resources/base/ element/string.json ,中添加对应信息,一个简单的示范如下: 

{ 

"string": [ 

{ 

"name": "reason", 

"value": " 采集 oaid 信息用于统计分析 " 

}, 

] 

} 

5. 注意!!!!在适当位置 (preInit 方法调用之后 ) ,经用户授权同意 

隐私政策后调用 init 方法,才会开始日志的采集和传输。 

方法说明 

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

# 账号登出,用户同意隐私政策后调用 

setLogEnabled(enable:boolean) 

日志开关,默认关闭 

# 自定义事件 

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

- @param e message data 

*/ 

workerPort.onmessage = function (e: MessageEvents) { 

onEventObject("workerevent4", {a: 1}) 

} 

/** 

* Defines the event handler to be called when the worker receives a message that cannot be deserialized. 

* The event handler is executed in the worker thread. 

* 

* @param e message data 

*/ 

workerPort.onmessageerror = function (e: MessageEvents) { 

} 

/** 

* Defines the event handler to be called when an exception occurs during worker execution. 

* The event handler is executed in the worker thread. 

* 

* @param e error message 

*/ 

workerPort.onerror = function (e: ErrorEvent) { 

} 

暂未提供 c++ 中直接调用的方法,需要参考鸿蒙官网 c++ 和 arkts 互 通的知识,通过 NAPI 的方式来调 onEventObject 方法实现埋点。 

更多内容请参考友盟官方文档说明: https://developer.umeng.com/ docs/119267/detail/2712046
