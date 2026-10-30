# 友盟应用性能监控 U-APM 鸿蒙版 SDK 使用指南 

# 系统 API 要求 

鸿蒙 NEXT API12 及以上 stage 模式的普通应用,暂不支持元服务。 

快速开始 

安装 sdk 

# 在项目的根目录下执行如下命令 

ohpm install @umeng/common --registry=https:// ohpm.openharmony.cn/ohpm 

ohpm install @umeng/analytics --registry=https:// ohpm.openharmony.cn/ohpm 

ohpm install @umeng/apm --registry=https:// ohpm.openharmony.cn/ohpm 

# 重要 

common 版本需要在 1.1.1 及以上 

# 集成 

在项目的 AppScope/resources/rawfile 目录下新增一个配置文件 umconfig.json 

# 内容如下 

{ 

"appKey": " 你的 apppkey", 

"channel": " 你的渠道 " 

} 

在应用模块目录下,添加 abilityStage 工程文件 , 例如 entry/src/main/ ets/abilityStage/MyAbilityStage.ets ,具体位置如截图 

# 参考代码如下 

import AbilityStage from '@ohos.app.ability.AbilityStage'; 

import { preInit, InternalPlugin, setLogEnabled, init } from '@umeng/analytics'; 

import { ApmPlugin } from '@umeng/apm'; 

setLogEnabled(true); // 开发时,打开调试日志,可观察 sdk 是否集成 成功 

export default class MyAbilityStage extends AbilityStage { 

onCreate() { 

preInit({ 

context: this.context.getApplicationContext(), 

plugins: [new InternalPlugin(), new ApmPlugin()] 

}); 

init(); // 在用户同意隐私政策后再调用此方法 

} 

} 

在模块的的 module.json5 文件中添加 srcEntry ,指向 abilityStage 文 件的地址 

在模块的 module.json5 文件中添加权限声明 

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

"value": " 采集 oaid 信息用于崩溃、性能分析 " 

}, 

] 

} 

在适当位置 (preInit 方法调用之后 ) ,经用户授权同意隐私政策后调用 init 方法,才会开始日志的采集和传输 

方法说明 

preInit(context:common.ApplicationContext,plugins: [internalPlugin,ApmPlugin]) 

预初始化 , 需要在 abilityStage 的 onCreate 方法内调用 

init() 

用户同意隐私政策后调用 , 方法调用后才会进行采集和日志传输 , 需要 开发者自行记录用户是否同意了隐私政策,并在判断用户同意隐私政 策时才可调用 init 方法 

setLogEnabled(enable:boolean) 

日志开关,默认关闭 

更多内容请参考友盟官方文档说明: https://developer.umeng.com/ docs/193624/detail/2835970
