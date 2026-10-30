# **使用前须知** 

- 1、创建账号:请前往https://www.umeng.com/完成账号注册,如有友盟+账号,可直接登 

录 

- 2、实名认证,如已完成认证,可忽略 

- 3、选择移动统计分析进入https://mobile.umeng.com/platform/apps/list 

- 4、创建鸿蒙应用类型,获取Appkey; 

- 5、具体使用指南,请参考 https://developer.umeng.com/docs/119267/detail/126044 

# **集成说明** 

## **系统API 要求** 

鸿蒙NEXT API(12)以上,仅支持普通应用stage 模式,暂不支持元服务 

## **快速开始** 

### **安装sdk** 

1. 在DevEco Studio 5.x 版本的IDE 中,从顶部菜单Tools->Partner SDK 

的Analysis 分类中找到【友盟common SDK】点击install 按钮,然后 再找到【友盟统计分析(U-APP)】的包,点击install 按钮 

### **集成** 

1. 在项目的 AppScope/resources/rawfile 目录下新增一个配置文件 

umconfig.json 

{
  "appKey": "你的apppkey",
  "channel": "你的渠道"
}

2. 在应用模块目录下,添加 abilityStage 工程文件,例如 

entry/src/main/ets/abilityStage/MyAbilityStage.ets ,具体位置如截图 

参考代码如下: 

import AbilityStage from '@ohos.app.ability.AbilityStage'; 

import { preInit, InternalPlugin, setLogEnabled, init, onEventObject } from 

'@umeng/analytics'; 

setLogEnabled(true); // 开发时,打开调试日志,可观察sdk 是否集成成功 

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

3. 在模块的的module.json5 文件中添加 srcEntry ,指向abilityStage 文件 

的 地 址 

### 4. 在模块的module.json5 文件中添加权限声明 

"requestPermissions": [ 

{ 

"name": "ohos.permission.INTERNET" 

}, { 

"name": "ohos.permission.GET_NETWORK_INFO" 

} ], 

### 5. 注意!!!!在适当位置(preInit 方法调用之后),经用户授权同意隐私政策后 

### 调用init 方法,才会开始日志的采集和传输。 

### **方法说明** 

- preInit(context:common.ApplicationContext,plugins:[internalPlugi 

n]) 

`o` 预初始化,需要在abilityStage 的onCreate 方法内调用 

- init() 

      - 用户同意隐私政策后调用,方法调用后才会进行采集和日志传输,需 要开发者自行记录用户是否同意了隐私政策,并在判断用户同意隐 私政策时才可调用init 方法 

- onEventObject(eventID: string, params?: Record<string, string | 

   - number>) 

      - 自定义事件,可在用户同意init 之前调用,最多缓存1000 事件 

      - eventID,事件id,字符串128 位以内的非空字符串 

      - params, 事件属性,可选参数,属性key,128 位以内的非空字符 

串,value 为256 位以内的数值或字符串 

   - 特别的 ,事件id 和属性key 不能为一下保留关键字[“id”, “ts”, “du”, “ds”, “duration”, “pn”, “token”, “ device_name ”, “ device_model ” , “device_brand ” , “country”, “city”, “channel”, “province”, “appkey”, “app_version”, “access”, “launch”, “pre_app_version”, “terminate”, “no_first_pay”, “is_newpayer”, “first_pay_at”, “first_pay_level”, “first_pay_source”, “first_pay_user_level”, 

      - “first_pay_version”, “type”]; 

- onProfileSignIn(provider:string,puid:string) 

   - 账号登入,用户同意隐私政策后调用 

   - provider 开发者自定义的账号类型,非空字符串,且长度不超过 

      - 32 

   - puid 开发者自定义的账号,非空字符串,且长度不超过64 

- onProfileSignOff() 

   - 账号登出,用户同意隐私政策后调用 

- setLogEnabled(enable:boolean) 

   - 日志开关,默认关闭 

### **自定义事件** 

- 在UI 线程中埋点,以下代码演示了如何在某个页面的某个按钮的点击事 

   - 件埋点 

import { onEventObject } from '@umeng/analytics'; 

Button('自定义事件X1').onClick(() => { 

onEventObject("eventid", { 

}); 

### • 在worker 线程中, 以下代码演示了如何在worker 线程中埋点 

**import** worker, { ThreadWorkerGlobalScope, MessageEvents, ErrorEvent } **from** 

'@ohos.worker'; 

**import** { onEventObject } **from** '@umeng/analytics'; 

**const** workerPort: ThreadWorkerGlobalScope = worker.workerPort; 

/** 

* Defines the event handler to be called when the worker thread receives a 

message sent by the host thread. 

* The event handler is executed in the worker thread. 

* 

* **@param** e message data 

*/ 

workerPort.onmessage = **function** (e: MessageEvents) { 

onEventObject("workerevent4", { 

a: 1 

}) 

} 

/** 

- Defines the event handler to be called when the worker receives a message that 

cannot be deserialized. 

- The event handler is executed in the worker thread. 

* 

* **@param** e message data 

*/ 

workerPort.onmessageerror = **function** (e: MessageEvents) { 

} 

/** 

- Defines the event handler to be called when an exception occurs during worker 

execution. 

* The event handler is executed in the worker thread. 

* 

* **@param** e error message 

*/ 

workerPort.onerror = **function** (e: ErrorEvent) { 

} 

- 暂未提供c++中直接调用的方法,需要参考鸿蒙官网c++和arkts 互通 

的知识,通过NAPI 的方式来调onEventObject 方法实现埋点
