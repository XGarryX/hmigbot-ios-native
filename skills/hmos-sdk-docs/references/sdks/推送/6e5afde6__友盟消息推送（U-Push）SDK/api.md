# 友盟消息推送 U-Push 鸿蒙版 SDK 使用指南 

一、初始化 API 

初始化 API ,在需要使用消息推送的 entryability 中增加如下配置 

注意建议添加 PushAgent.onNewWant 方法,用于统计通知消息的点 击次数,和点击内容 extra 的接收。 

// entry/src/main/ets/entryability/EntryAbility.ets 

```arkts
import { AbilityConstant, UIAbility, Want } from '@kit.AbilityKit'; 
```

import { PushAgent, MsgContent } from '@umeng/push'; // 消息通 知 

export default class EntryAbility extends UIAbility { 

onCreate(want: Want, launchParam: AbilityConstant.LaunchParam) { // v1.0.14 版本及以上支持 

// 应用需要获取用户授权才能发送通知。可选 

// 调用此方法,弹窗让用户选择是否允许发送通知,仅弹出一次,后 续再次调用此方法时,则不再弹窗。 

PushAgent.enableNotification(this.context, (res: Record<string, string>) => { 

console.log(' 通知是否允许 ', JSON.stringify(res)); 

}); 

// 消息推送初始化回调,成功即可得到 data.data 返回值,即 device token 。 

PushAgent.initCallback((data: Record<string, string>) => { 

console.log(' 消息推送初始化 ', JSON.stringify(data)); 

}); 

// v1.0.14 版本及以上支持 

// 收到通知消息的回调方法,可自定义处理通知消息(支持在线消 息,不支持厂商消息),可选。 

// 若配置 callback 回调,表示正常展示通知消息,也可重置消息内容 后再 callback 展示消息。 

// 若未配置 callback 回调,表示通知消息被开发者拦截,即不会展示 该条消息,由开发者自定义展示。 

PushAgent.onNotificationMessage((msg_content: MsgContent, callback: Callback<MsgContent>) => { 

console.log(' 通知消息的内容 ', JSON.stringify(msg_content)); 

if (msg_content.body?.title) { 

msg_content.body.title = ' 如自定义修改通知标题 '; 

} 

callback(msg_content); 

}); 

// 点击通知消息,可在此接收 extra 内容(用于后续页面跳转等场 景)可选 

// 注意:在 push2.0.0 以下版本要先添加 onNewWant 中的 PushAgent.onNewWant 方法,才可接收成功。 

PushAgent.onClickMessage((obj: Record<string, string>) => { console.log(' 接收 extra 内容 ', JSON.stringify(obj)); 

}); 

# // 接收自定义消息内容,可选 

PushAgent.onCustomMessage((customMsg: MsgContent) => { console.log(' 接收自定义消息内容 ', JSON.stringify(customMsg)); 

}); 

} 

onNewWant(want: Want, launchParam: AbilityConstant.LaunchParam): void { 

// 通知消息点击次数统计,可选 

// 注意:在 push2.0.0 以下版本需要添加此方法, 2.0.0 及以上版本此 方法已废弃。 

PushAgent.onNewWant(want); 

} 

} 

二、功能介绍 

# 通知大图标 

图片要求 pixelmap 在 100kb 以内才可成功展示,图片跟原始文件大小 无关,取 pixelmap 对象字节大小: 像素高 * 像素宽 *4/1024<=100 (单位 KB )可在通知消息中展示大图标,超过 100KB 则不展示图标。 

# 可通过配置应用内图标或上传通知图标: 

1. 应用内图标,位于 AppScope/resources/rawfile 文件夹内的图片, 例如 um_icon.png 

2. 上传通知图标,可通过 api 发送配置 img 字段的图片地址,或友盟后 

台页面上传图片, v1.0.14 版本支持。 

# 通知权限 

可通过调用 API 获取通知栏开关状态 

import { PushAgent } from '@umeng/push'; 

# // 获取通知栏开关状态 

const getStatus = async () => { 

try { 

let res: Record<string, string> = await PushAgent.isNotificationEnabled(); 

console.log(' 开关状态 ', JSON.stringify(res)); 

} catch (e) { 

console.log(e); 

} 

}; 

# 角标 

可调用如下方法设置应用角标,数字要大于等于 0 。 

import { PushAgent } from '@umeng/push'; 

// 设置角标数字,指定数字。 

const setBadge = async (num: number = 0) => { 

try { 

const res: Record<string, string> = await PushAgent.setBadge(num); 

console.log(' 设置角标 ', JSON.stringify(res)) 

} catch (e) { 

console.log(e); 

} 

}; 

// 角标数字递增 

// 可在创建 api 通知消息时,配置 add_badge ,每条消息会递增相应数 字。 

获取厂商 token 

需先在华为后台集成厂商后才可成功获取。 

import { PushAgent } from '@umeng/push'; 

const getToken = async () => { 

try { 

let res = await PushAgent.getThirdToken(); 

console.log('res', JSON.stringify(res)); 

} catch (e) { 

console.log(e); 

} 

}; 

标签与别名 

标签可以给某一类人群推送消息,别名可以给指定用户推送消息。最 佳实践: 

客户端开发者在应用内调用 addTags 或者 addAlias 来设置对应关 系; 

【友盟 + 】消息后台存储相应的关系设置; 

在服务器端推送消息时,指定向之前设置过的别名或者标签推送。 

import { PushAgent } from '@umeng/push'; 

# // 获取服务器端的所有标签 

PushAgent.getTags((res: Record<string, string>) => { 

console.log('res', JSON.stringify(res)); 

# }); 

// 添加标签 示例:将 “ 标签 1” 、 “ 标签 2” 绑定至该设备 

PushAgent.addTags([' 标签 1', ' 标签 2'], (res: Record<string, string>) => { 

console.log('res', JSON.stringify(res)); 

}); 

# // 删除标签 , 将之前添加的标签中的一个或多个删除 

PushAgent.deleteTags([' 标签 1', ' 标签 2'], (res: Record<string, string>) => { 

console.log('res', JSON.stringify(res)); 

# }); 

注: tag 名称请不要加入 URL Encode 等变换处理,请使用原生字符 串。 目前每个用户 tag 限制在 1024 个, 每个 tag 最大 128 字符。 tag 需 使用半角字符,大小写敏感, tag 中请不要使用逗号( , )双竖线 ( || )。 

# 增加、绑定、移除别名 

import { PushAgent } from '@umeng/push'; 

# // 别名增加 

// 将某一类型的别名 ID 绑定至某设备,老的绑定设备信息还在,别名 ID 和 device_token 是一对多的映射关系 

// alias 和 alias_type 两个字段的长度限制分别为 128 , 64 个字符 

// alias 和 alias_type 的格式仅支持半角大小写字母,数字,下划线 

// 默认单个 alias 下同时生效的 deviceToken 数最多 10 个, pro 可调 整,需要绑定大量设备( >1k) 的场景用 tag 更合适 

// 默认单个 Appkey 下同时生效的 alias_type 数最多 10 个 

PushAgent.addAlias(' 别名 ID', ' 自定义类型 ', (res: Record<string, string>) => { 

console.log('res', JSON.stringify(res)); 

}); 

# // 别名绑定 

// 将某一类型的别名 ID 绑定至某设备,老的绑定设备信息被覆盖,别 名 ID 和 deviceToken 是一对一的映射关系 

PushAgent.setAlias(' 别名 ID', ' 自定义类型 ', (res: Record<string, string>) => { 

console.log('res', JSON.stringify(res)); 

}); 

// 移除别名 ID 

PushAgent.deleteAlias(' 别名 ID', ' 自定义类型 ', (res: Record<string, string>) => { 

console.log('res', JSON.stringify(res)); 

}); 

推送功能开启与关闭 

import { PushAgent } from '@umeng/push'; 

// 消息功能开启,开启后可接收消息通知,默认开启。 

PushAgent.enable((res: Record<string, string | number>) => { console.log('res', JSON.stringify(res)); 

# }); 

// 消息功能关闭,关闭后不再接收通知消息。 

PushAgent.disable((res: Record<string, string | number>) => { console.log('res', JSON.stringify(res)); 

# }); 

# 自定义消息 

自定义消息不会被展示到通知栏上, SDK 仅负责将消息透传给 App , 其内容处理由开发者自己控制。 

最佳实践:自定义消息可以用于应用的内部业务逻辑和特殊展示需 求。 

创建消息后台页面如下所示: 

若开发者要使用自定义消息,需使用如下方法接收自定义消息,并在 业务中上报自定义消息的展示次数和点击次数。 

import { PushAgent, MsgContent } from '@umeng/push'; 

# // 接收自定义消息内容 

PushAgent.onCustomMessage((customMsg: MsgContent) => { console.log(' 接收自定义消息内容 ', JSON.stringify(customMsg)); 

}); 

// 统计自定义消息的展示次数,开发者按需上报自定义接收的内容。 PushAgent.trackMsgShow(customMsg); 

- // 统计自定义消息的点击次数,开发者按需上报自定义接收的内容。 

PushAgent.trackMsgClick(customMsg); 

更多内容请参考友盟官方文档说明: https://developer.umeng.com/ docs/67966/detail/2808149
