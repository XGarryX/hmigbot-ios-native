# 终端威胁感知 MTD 产品使用说明 

修订记录 

版本号 修订人 修订日期 修订描述 

V 1.0 朱志铭 

2024-03-08 完成初稿 

目录 

# 1. 文档说明 3 

# 2. 客户端 SDK 使用说明 3 

2.1 sdk 内容 3 

2.2 集成方法 3 

2.3 SDK 接口 API 详细说明 4 

# 2.4 错误码详细说明 6 

# 文档说明 

本文介绍芯盾终端威胁感知产品的集成方法、接口说明。 供移动端应用开发人员对接开发参考。 

客户端 SDK 使用说明 

sdk 内容 

Harmony SDK 包含如下内容: 

-har 文件: trusfort-x.x.x.har 

# 集成方法 

1. 将 har 文件复制到应用代码工程源目录(有自定义依赖库路径的,也 可复制到自定义路径内) 

2. 打开应用的 oh-package.json5 文件,设置三方包依赖,配置示例如 下: 

"dependencies": { 

"trusfort": "file:./libs/trusfort-x.x.x.har" 

} 

3. 配置完成后示例如下(自定义依赖库路径为 libs ): 

# 4: 调用方法 

接口类: TrusfortApiForMtd 

导入模块: import { 

TrusfortApiForFmtd,initEnvForTrusfort,InitTrusfortEnvParameter } from 'trusfort' 

# SDK 接口 API 详细说明 

initEnvForTrusfort 

API 功能描述: 

# 此接口作用是初始化运行环境。 

导入模块: import { initEnvForTrusfort,InitTrusfortEnvParameter } from 'trusfort' 

# API 调用时机 : 

应用启动时调用 

API 原型: 

Promise<string> 

注意:如果集成了芯盾多个产品能力调用一次接口即可 , 根据产品能力 设置相应参数。 

参数: 

参数 

必选 

类型 

描述 

InitTrusfortEnvParameter 

是 

InitTrusfortEnvParameter 

context 

是 

Context 

应用上下文 

AbilityStage :this.context.getApplicationContext() 

自定义组件 :getContext().getApplicationContext() 

InitTrusfortEnvParameter 参数: 

参数 

必选 

类型 

描述 

appid 

是 

string 

由芯盾分配,授权当前 app 。注意如果集成了芯盾多个产品能力 appid 最好保持统一。 

xdidAppId 

否 

string 

允许当前产品能力使用单独的 appid ,如果当前 xdidAppId 有值,则不 在取值 appid 。 

xdidUrl 

是 

string 

芯盾服务器地址 

xdidAlgorithm 

否 

string 

默认 “1” 。算法 “0” 国密 “1” 非国密, 

API 返回值: 

string 类型的 json 串 

key 

必选 

类型 

描述 

status 

是 

string 

初始化状态码,详情见状态码 

API 调用示例: 

import AbilityStage from '@ohos.app.ability.AbilityStage'; import type Want from '@ohos.app.ability.Want'; 

export default class MyAbilityStage extends AbilityStage { onCreate(): void { 

// 应用的 HAP 在首次加载的时,为该 Module 初始化操作 let initParmas = new InitTrusfortEnvParameter(); initParmas.appid = "com.example.demo" 

initParmas.xdidUrl = "http://xxx.xxx.xxx.xxx/xdid/mapi"; initParmas.xdidAlgorithm = "0"; 

console.log(data); 

}).catch((err: Error) => { 

console.info(`initEnvForTrusfort err: ${JSON.stringify(err)}`) 

}); 

...... 

} 

} 

import AbilityStage from '@ohos.app.ability.AbilityStage'; import type Want from '@ohos.app.ability.Want'; 

export default class MyAbilityStage extends AbilityStage { onCreate(): void { 

// 应用的 HAP 在首次加载的时,为该 Module 初始化操作 let initParmas = new InitTrusfortEnvParameter(); initParmas.appid = "com.example.demo" 

initParmas.xdidUrl = "http://xxx.xxx.xxx.xxx/xdid/mapi"; initParmas.xdidAlgorithm = "0"; 

console.log(data); 

}).catch((err: Error) => { 

console.info(`initEnvForTrusfort err: ${JSON.stringify(err)}`) 

}); 

...... 

} 

} 

preCollectDevInfo (可选) 

API 功能描述: 

收集部分隐私相关的设备信息(预处理一些耗时的采集项)。 

# API 调用时机 : 

因 2021 年有了隐私协议的规定,用户未同意隐私协议前不能获取用户 信息,所以在同意隐私政策后并且在其他接口函数前调用。因敏感信 息需要关联具体业务场景,如果采集个人隐私,尽量在具体业务场景 中调用以满足隐私合规,比如在具体业务场景(如:登录、注册等) 页面组件创建阶段 aboutToAppear?() ,遵循越早调用越有利的原则。 

API 不调用的影响 : 

不收集相关的设备信息(蓝牙,位置,传感器 0 

备注:不影响设备指纹生成。 

# API 原型: 

preCollectDevInfo(filter?: number){} 

# API 参数: 

参数 

必选 

类型 

描述 

filter 

否 

number 

默认 0 ,对于部分需要弹窗让用户授权的数据,在用户未授权情况 下,设置了相应的 filter 也不会收集到数据 支持的 filter 

name 

类型 

描述 

FILTER_PERMISSION_LOCATION 

number 

收集地理位置信息,不传不收集 

FILTER_PERMISSION_BLUETOOTH 

number 

收集蓝牙信息,不传不收集 

FILTER_SENSOR 

number 

收集传感器信息,不传不收集 

API 返回值: 

无返回值 

API 调用示例: 

TrusfortApiForMtd.preCollectDevInfo( 

TrusfortApiForMtd.FILTER_PERMISSION_LOCATION| TrusfortApiForMtd.FILTER_PERMISSION_BLUETOOTH | TrusfortApiForMtd.FILTER_SENSOR); 

TrusfortApiForMtd.preCollectDevInfo( 

TrusfortApiForMtd.FILTER_PERMISSION_LOCATION| 

TrusfortApiForMtd.FILTER_PERMISSION_BLUETOOTH | TrusfortApiForMtd.FILTER_SENSOR); 

setDeviceInfoOption 

API 功能描述: 

设置设备信息采集配置。 

# API 调用时机 : 

因 2021 年有了隐私协议的规定,用户未同意隐私协议前不能获取用户 信息,所以在同意隐私政策后并且在其他接口函数前调用。因敏感信 息需要关联具体业务场景,如果采集个人隐私,尽量在具体业务场景 中调用以满足隐私合规,比如在具体业务场景(如:登录、注册等) 页面组件创建阶段 aboutToAppear?() ,遵循越早调用越有利的原则。 

# API 不调用的影响 : 

# 不收集网络信息相关项。 

备注:不影响设备指纹生成。 

API 原型: 

setDeviceInfoOption(filter?: number){} 

API 参数: 

参数 

必选 

类型 

描述 

filter 

否 

number 

默认 0 ,对于部分需要弹窗让用户授权的数据,在用户未授权情况 下,设置了相应的 filter 也不会收集到数据 支持的 filter 

name 

类型 

描述 

OPTION_FILTER_NETWORK_INFO 

number 

收集网络可选信息,不传会收集 

API 返回值: 

无返回值 

API 调用示例: 

reportDeviceEnvInfo 

API 功能描述: 

上报设备环境信息。返回设备唯一标识字段及其他字段,只解析相关 字段使用即可。 

API 调用时机 : 

初始化且隐私政策同意后,相关业务点 

API 原型: 

reportDeviceEnvInfo(extInfo?: HashMap<string, string>): Promise<string> 

# API 参数: 

参数 

必选 

类型 

描述 

extInfo 

否 

HashMap<string, string> 

传给 mtd 服务器的扩展字段, key 和 value 都需要为 string 类型 

# API 返回值: 

string 类型的 json 串,返回设备唯一标识字段,如果不使用可不必解 析。 字段 

含义 

值 

备注 

devid 

设备唯一标识 

字符串 

call_state 

电话通话状态 

“call_state_idle” : 空闲 

“call_state_offhook” :拨号中、接通、挂起 

“call_state_ringing” :响铃、来电等待 

is_proxy 是否开启网络代理 

“true”/“false” 

is_vpn 是否开启 vpn “true”/“false” 

is_emu 是否模拟器 

“true”/“false” 

debug_on 是否调试中 

“true”/“false” 

is_lied_apksign 二次打包 

“true”/“false” 

is_capture 是否屏幕共享 

“true”/“false” 

audio 

# 音频模式 

- 0 :正常音频模式 : 不振铃,未建立通话。 

- 1 :振铃音频模式。有一个进来的信号。 

- 2 :通话音频模式。一个电话被建立。 

- 3 :在通信音频模式。建立语音 / 视频聊天或 VoIP 通话 

telecom_fraud 

电诈风险 

- “0” :无风险 

“1”: 高风险 

- “2” :高风险 

# API 调用示例: 

let extMap = new HashMap<string, string>(); 

extMap.set('test', 'test'); 

TrusfortApiForMtd.reportDeviceEnvInfo(extMap).then(data=>{ 

console.info(`reportDeviceEnvInfo : ${data}`) 

}).catch((err: Error) => { 

console.info(`reportDeviceEnvInfo err: ${JSON.stringify(err)}`) 

}); 

let extMap = new HashMap<string, string>(); extMap.set('test', 'test'); 

TrusfortApiForMtd.reportDeviceEnvInfo(extMap).then(data=>{ console.info(`reportDeviceEnvInfo : ${data}`) 

}).catch((err: Error) => { console.info(`reportDeviceEnvInfo err: ${JSON.stringify(err)}`) 

}); 

initUnionId (可选) 

API 功能描述: 用于设备统一指纹生成。 

API 调用时机 : 

# 在同意隐私政策后调用。遵循越早调用越有利的原则。 

如若使用此接口,需要将芯盾提供的配置文 件 “trusfort_custom_info” 放置到项目的 resources/rawfile 文件夹下 

# API 原型: 

initUnionId(url:string):boolean 

# API 参数: 

参数 

必选 

类型 

描述 

url 

是 

string 

设备统一指纹认证的服务器地址,根据服务端部署方式决定,默认不 需要传此参数 

API 方法返回值: 

类型 

描述 

boolean 

true 代表初始化成功, false 表示初始化失败,请检测配置文件是否存 在,是否 initEnv 后调用 

API 调用示例: 

let ret = TrusfortApiForMtd.initUnionId("http://192.168.1.170:8101/xdid); 

let ret = TrusfortApiForMtd.initUnionId("http://192.168.1.170:8101/xdid); 

getOnlineDeviceIdFromCache 

API 功能描述: 

获取缓存的设备唯一标识 

# API 调用前提条件 : 

reportDeviceEnvInfo 已经成功返回过,否则值为空。 

API 原型: 

getOnlineDeviceIdFromCache(): string; 

API 参数: 

无 

API 方法返回值: 

类型 

描述 

string 

status: 状态码 0: 成功 , token: 设备唯一标识 

# API 调用示例: 

```arkts
let cache_devid= TrusfortApiForMtd.getOnlineDeviceIdFromCache(); let jsonObj:object|null = JSON.parse(cache_devid); let commObj = (jsonObj as Record<string, Object>); let status:string = commObj["status"] as string if (status=="0") { let devid:string = commObj["token"] as string } 
let cache_devid= TrusfortApiForMtd.getOnlineDeviceIdFromCache(); let jsonObj:object|null = JSON.parse(cache_devid); let commObj = (jsonObj as Record<string, Object>); let status:string = commObj["status"] as string if (status=="0") { 
```

let devid:string = commObj["token"] as string 

} 

startCheckMonitor 

API 功能描述: 

此接口作用是 SDK 周期性检测风险,不涉及网络请求。 

API 调用前提条件 : 

initEnvForTrusfort 后执行 

API 原型: 

Public static startCheckMonitor(interval: number,callback: (result:string)=> void); 

API 参数: 

类型 

描述 

interval 

周期间隔时间,默认 5 秒 

callback 

回调方法 

json 解析字段: 

字段 

含义 

值 

备注 

call_state 电话通话状态 

“call_state_idle” : 空闲 

“call_state_offhook” :拨号中、接通、挂起 

“call_state_ringing” :响铃、来电等待 

is_proxy 是否开启网络代理 

“true”/“false” 

is_vpn 是否开启 vpn 

“true”/“false” 

is_emu 是否模拟器 

“true”/“false” 

debug_on 是否调试中 

“true”/“false” 

is_assistant 

# 系统中是否有辅助模式开启 

“true”/“false” 

is_capture 

# 是否屏幕共享 

“true”/“false” 

audio 

# 音频模式 

- 0 :正常音频模式 : 不振铃,未建立通话。 

- 1 :振铃音频模式。有一个进来的信号。 

- 2 :通话音频模式。一个电话被建立。 

- 3 :在通信音频模式。建立语音 / 视频聊天或 VoIP 通话 

telecom_fraud 

# 电诈风险 

- “0” :无风险 

- “1”: 高风险 

- “2” :高风险 

API 调用示例: 

TrusfortApiForMtd.startCheckMonitor(10000,data=>{ console.info(`riskInfo : ${data}`) 

}); 

TrusfortApiForMtd.startCheckMonitor(10000,data=>{ console.info(`riskInfo : ${data}`) 

}); 

stopCheckMonitor 

功能描述: 此接口作用是停止 SDK 周期性检测风险 API 方法调用的前置条件: 需要在 startCheckMonitor 方法后执行 API 方法原型: public static void stopCheckMonitor(); 输入参数: 

无 

API 方法返回值: 

无 

getRiskLabel 

功能描述: 此接口作用是本地获取风险标签 

API 方法原型: public static void getRiskLabel(): Promise<string>; 输入参数: 

无 API 方法返回值: 

json 解析字段: 字段 含义 

值 备注 call_state 电话通话状态 

“call_state_idle” : 空闲 

“call_state_offhook” :拨号中、接通、挂起 

“call_state_ringing” :响铃、来电等待 

is_proxy 是否开启网络代理 

“true”/“false” 

is_vpn 

# 是否开启 vpn 

“true”/“false” 

is_emu 

# 是否模拟器 

“true”/“false” 

debug_on 是否调试中 

“true”/“false” 

is_assistant 

# 系统中是否有辅助模式开启 

“true”/“false” 

is_capture 

# 是否屏幕共享 

“true”/“false” 

audio 

# 音频模式 

- 0 :正常音频模式 : 不振铃,未建立通话。 

- 1 :振铃音频模式。有一个进来的信号。 

- 2 :通话音频模式。一个电话被建立。 

- 3 :在通信音频模式。建立语音 / 视频聊天或 VoIP 通话 

telecom_fraud 

电诈风险 

“0” :无风险 

“1”: 高风险 

“2” :高风险 

# API 调用示例: 

TrusfortApiForMtd.getRiskLabel().then(data=>{ this.message = data; console.info(`getRiskLabel : ${data}`) 

}).catch((err: Error) => { 

console.info(`getRiskLabel err: ${JSON.stringify(err)}`) 

}); 

TrusfortApiForMtd.getRiskLabel().then(data=>{ this.message = data; console.info(`getRiskLabel : ${data}`) 

}).catch((err: Error) => { 

console.info(`getRiskLabel err: ${JSON.stringify(err)}`) 

}); 

# 错误码详细说明 

错误码 错误码说明 

0 操作成功 -1 未知错误 -5001 参数错误 -5002 内存不足 -5004 网络错误 -5009 服务器返回数据格式错误 1000 服务器接口调用成功 9001 参数错误 

9002 

APPID 错误 

9003 

终端威胁感知 ID 不存在 

9004 内部依赖服务错误 

9005 重放的请求 

9999 服务器内部错误
