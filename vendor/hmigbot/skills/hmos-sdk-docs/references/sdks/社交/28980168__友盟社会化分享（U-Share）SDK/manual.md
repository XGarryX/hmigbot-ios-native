# 社会化分享 SDK 集成接入指南 

概述 

运行环境 

鸿蒙 NEXT API12 及以上 stage 模式的普通应用,需在工程级别开启字 节码,暂不支持元服务。 

服务说明 

社会化分享微信微博 QQ 

友盟 + 鸿蒙社会化分享,支持三方应用使用多平台分享、第三方登录 等功能。 

注意当前支持微信、微博、 QQ 的分享和登录功能。 

权限授予 

为确保 SDK 正确使用,需在开发者应用中授予以下权限。 

权限 

用途 

ohos.permission.INTERNET 

检测联网方式,在网络异常状态避免数据发送, 

节省流量和电量 

ohos.permission.GET_NETWORK_INFO 

看网络状态,用于 SDK 重连机制等场景。 

# 注意事项 

社会化分享 SDK 不可单独集成使用,需同时集成 @umeng/ common@umeng/analytics@umeng/share 方可成功使用。 

快速开始 

一、安装 SDK 

# 在项目的根目录下执行如下命令 

# 注:当前支持微信好友、微信朋友圈、微博、 QQ 好友、 QQ 空间的分 享和登录功能。 

ohpm install @umeng/common --registry=https:// ohpm.openharmony.cn/ohpm 

ohpm install @umeng/analytics --registry=https:// ohpm.openharmony.cn/ohpm 

ohpm install @umeng/share --registry=https:// ohpm.openharmony.cn/ohpm 

注 @umeng/common 要在 v1.0.24 版本及以上。 

# 二、集成 SDK 

在项目的 AppScope/resources/rawfile 目录下新增一个配置文件 umconfig.json, 

# 文件内容如下 

{ 

"appKey": " 你的 apppkey", 

"channel": " 你的渠道 ", 

} 

在应用模块目录下,添加 abilityStage 工程文件,例如 entry/src/ main/ets/abilityStage/MyAbilityStage.ets ,具体位置如下图 

# 文件内容如下 

// entry/src/main/ets/abilityStage/MyAbilityStage.ets 

import AbilityStage from '@ohos.app.ability.AbilityStage'; 

import { init, preInit, InternalPlugin } from '@umeng/analytics'; 

import { SharePlugin } from "@umeng/share"; 

export default class MyAbilityStage extends AbilityStage { 

onCreate() { 

preInit({ 

context: this.context.getApplicationContext(), 

enableLog: true, // 开发时,打开调试日志,可观察 sdk 是否集成成功 

plugins: [ 

new InternalPlugin(), 

new SharePlugin({ 

// 微信配置,可选 

WX_APPID: 'wx167efce1c3229999', // 微信开放平台审核通过的 APPID 

WX_AppSecret: 'wxwxwxwxwxwxxx', // 微信开放平台审核通过的 AppSecret 

// 微博配置,可选( v1.1.5 版本支持) 

Weibo_Config: { 

appkey: "3313904948", // 必选,微博开放平台的 appkey 

redirect_url: "https://api.weibo.com/oauth2/default.html", // 可 选,开放平台的授权回调页 

scope: "email,direct_messages_read,direct_messages_write," 

+ 

"friendships_groups_read,friendships_groups_write,statuses_to_me_read," 

+ "follow_app_official_microblog," + "invitation_write", // 可选,注 意: scope 为 "" ,表示没有申请的高级权限,则走快捷授权流程 

logEnable: true, // 可选,微博 sdk 的日志,调试时可以打开 log 开关 默认是 false 

}, 

// qq 配置,可选( v1.1.8 版本支持) 

QQ_Config: { 

appId: 1112396455, // qq 互联平台应用的 APPID 

appkey: "xq66VShoCDSUsALB", // qq 互联平台应用的 appkey 

} 

}) 

], 

# }); 

init(); // 初始化,在用户同意隐私政策后再调用此方法 

} 

} 

2.1 微信平台创建应用 微信开放平台获取 APPID 和 AppSecret ,需要审 核通过后可用,参见下图 

2.2 微博平台创建应用 微博开放平台获取 appkey ,需要先调用 sdk 的 Weibo.getSign() 方法得到应用的签名(也可以用户自行通过 bundleManager.getBundleInfoForSelf 获取到 bundleInfo.signatureInfo.appIdentifier 的值,再 md5 加密得到签 名),再前往微博开放平台创建应用输入签名,待审核通过后即可使 

用分享功能。参见下图 

2.3 QQ 互联平台创建应用 QQ 互联平台获取 APPID 和 APPKey ,需要审 核通过后可用,参见下图 

在模块的的 module.json5 文件中添加 srcEntry ,指向 abilityStage 文 件的地址 

在模块的 module.json5 文件中添加权限声明 

"requestPermissions": [ 

{ 

"name": "ohos.permission.INTERNET" 

}, 

{ 

"name": "ohos.permission.GET_NETWORK_INFO" 

} 

], 

参考下图 

注意在适当位置 (preInit 方法调用之后 ) ,经用户授权同意隐私政策后 调用 init 方法,才会开始日志的采集和传输。 

完成以上步骤后,即可按照集成文档中方式调用使用。 

更多内容请参考友盟官方文档说明: 

https://developer.umeng.com/docs/128606/detail/2938159 https://developer.umeng.com/docs/128606/detail/2938161 https://developer.umeng.com/docs/128606/detail/3002400 https://developer.umeng.com/docs/128606/detail/3020975
