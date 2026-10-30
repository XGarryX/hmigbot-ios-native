# 友盟消息推送 U-Push 鸿蒙版 SDK 使用指南 

概述 

运行环境 

鸿蒙 NEXT API12 及以上 stage 模式的普通应用,暂不支持元服务。 

服务说明 

友盟 + 鸿蒙消息推送,消息推送组件,提供给用户准时的 Push 通知功 能,支持友盟在线通道、华为厂商通道。 

权限授予 

为确保 SDK 正确使用,需在开发者应用中授予以下权限。 

权限 

用途 

ohos.permission.INTERNET 

允许使用 Internet 网络。即允许应用程序联网和发送推送数据的权 限,以便提供消息推送服务。 

ohos.permission.GET_NETWORK_INFO 

允许应用获取数据网络信息。检测在网络异常状态下避免数据发送, 节省流量。 

ohos.permission.APP_TRACKING_CONSENT 

获取设备信息用于生成脱敏的终端用户设备标识,以提供统计分析服 务 

# 注意事项 

U-Push SDK 不可单独集成使用,需同时集成 @umeng/ common@umeng/analytics@umeng/utunnel@umeng/push 方可成 

# 功使用。 

# 快速开始 

一、安装 SDK 

在项目的根目录下执行如下四个命令, @umeng/common 确保 v1.0.24 版本及以上。 

ohpm install @umeng/common --registry=https:// ohpm.openharmony.cn/ohpm 

ohpm install @umeng/analytics --registry=https:// ohpm.openharmony.cn/ohpm 

ohpm install @umeng/utunnel --registry=https:// ohpm.openharmony.cn/ohpm 

ohpm install @umeng/push --registry=https:// ohpm.openharmony.cn/ohpm 

二、集成 SDK 

1. 前往友盟消息推送平台创建鸿蒙应用,输入你的应用包名,创建应 用后得到 AppKey 和 Umeng Message Secret 。 

# 示例图 

2. 在项目的 AppScope/resources/rawfile 目录下新增一个配置文件 umconfig.json 

# 内容如下 

{ 

"appKey": " 你的 apppkey", // 注意: appkey 必须和你的应用包名对应 正确 

"channel": " 你的渠道 " // 开发者自定义命名渠道 

} 

3. 在应用模块目录下,添加 abilityStage 工程文件,例如 entry/src/ main/ets/abilityStage/MyAbilityStage.ets ,具体位置如下图 

# 文件内容如下 

// entry/src/main/ets/abilityStage/MyAbilityStage.ets 

import AbilityStage from '@ohos.app.ability.AbilityStage'; 

import { init, preInit, InternalPlugin, setLogEnabled, onEventObject } from '@umeng/analytics'; 

import { PushPlugin } from "@umeng/push"; 

export default class MyAbilityStage extends AbilityStage { 

onCreate() { 

preInit({ 

context: this.context.getApplicationContext(), 

enableLog: true, // 开发时,打开调试日志,可观察 sdk 是否集成成功 

plugins: [new InternalPlugin(), new PushPlugin({ 

// 注意: appMessageSecret 必须和你的应用包名对应正确 

appMessageSecret: " 你在友盟 push 后台创建应用得到的 Umeng Message Secret 值 " 

})] 

}); 

# init(); // 在用户同意隐私政策后再调用此方法 

} 

} 

4. 在模块的的 module.json5 文件中添加 srcEntry ,指向 abilityStage 文件的地址 

5. 在模块的 module.json5 文件中添加权限声明 

"requestPermissions": [ 

{ 

"name": "ohos.permission.APP_TRACKING_CONSENT", 

"reason": "$string:reason", // 如果 IDE 提示错误,需自行在 entry/src/ main/resources/base/element/string.json ,中添加对应信息 

"usedScene": {} 

}, 

{ 

"name": "ohos.permission.INTERNET" 

}, 

{ 

"name": "ohos.permission.GET_NETWORK_INFO" 

}, 

], 

注意上述代码中, "$string:reason" 为用户自定义内容,如果 IDE 提 示 "$string:reason", 错误,需自行在 entry/src/main/resources/base/ element/string.json 文件中添加对应信息,一个简单的示范如下 

{ 

"string": [ 

{ 

"name": "reason", 

"value": " 采集 oaid 信息用于分析 " 

}, 

] 

} 

参见下图 

6. 注意在适当位置 preInit 方法调用之后,经用户授权同意隐私政策后 调用 init 方法,才会开始日志的采集和传输。 三、集成验证 

1. 添加初始化回调方法,在需要使用消息推送的 entryability 中增加如 下配置,初始化回调获得 device token 即表示集成成功。 

注意当有多个 EntryAbility 时,要同样添加接收或上报的方法。 

// entry/src/main/ets/entryability/EntryAbility.ets 

```arkts
import { AbilityConstant, UIAbility, Want } from '@kit.AbilityKit'; 
```

import { PushAgent, MsgContent } from '@umeng/push'; 

export default class EntryAbility extends UIAbility { 

onCreate(want: Want, launchParam: AbilityConstant.LaunchParam) { 

// 应用需要获取用户授权才能发送通知, v1.0.14 版本支持。可选 

// 调用此方法,弹窗让用户选择是否允许发送通知,仅弹出一次,后 续再次调用此方法时,则不再弹窗。 

PushAgent.enableNotification(this.context, (res: Record<string, string>) => { 

console.log(' 通知是否允许 ', JSON.stringify(res)); 

}); 

// 消息推送初始化回调,成功即可得到 data.data 返回值,即 device token 。 

PushAgent.initCallback((data: Record<string, string>) => { console.log(' 消息推送初始化 ', JSON.stringify(data)); 

}); 

} 

}; 

四、接入完成 

成功获取到 device token 后可在友盟消息推送后台中创建通知消息, 选择下图目标人群,即可收到消息通知。 

注意示例消息成功接收后,请前往集成文档,完善初始化方法及自定 义功能方法。 

更多内容请参考友盟官方文档说明: https://developer.umeng.com/ docs/67966/detail/2808149
