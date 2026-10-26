<!-- when: 手上是 Android 三方 SDK(build.gradle 依赖/包名),要找鸿蒙对应项时读本文件 -->
<!-- topics: Android SDK 映射, 依赖替换, 同厂鸿蒙版, 能力对等替代 -->

# Android 三方 SDK → 鸿蒙对应映射表

匹配类型：**同厂** = 同一厂商官方鸿蒙版（迁移首选，概念/后台/账号体系可复用）；**对等** = 无同厂版时的能力对等替代（需评估改动量）。
本表增量维护：遇到表中没有的 Android SDK，先 Grep `l0-index.md` 按能力分类找，再按 `online-lookup.md` 搜 ohpm；确认后**把结果补进本表**。

## 推送

| Android SDK | Android 标识 | 鸿蒙对应 | ohpm 包名 | 匹配 |
|---|---|---|---|---|
| 极光推送 JPush | cn.jpush.android | 极光推送 | `@jg/push` | 同厂 |
| 友盟推送 U-Push | com.umeng.message | 友盟消息推送（U-Push） | `@umeng/push`（依赖 `@umeng/common` `@umeng/utunnel`） | 同厂 |
| 个推 | com.igexin | 个推消息推送 | `@getui/push` | 同厂 |
| 华为推送 HMS Push | com.huawei.hms.push | 官方 Push Kit（非三方） | `@kit.PushKit` | 官方 |

## IM / 社交

| Android SDK | Android 标识 | 鸿蒙对应 | ohpm 包名 | 匹配 |
|---|---|---|---|---|
| 环信 IM | com.hyphenate | 环信即时通讯 IM SDK | `@easemob/chatsdk` | 同厂 |
| 融云 IM | io.rong.imkit / imlib | 融云 IMKit（含企业版） | `@rongcloud/imkit` | 同厂 |
| ShareSDK（Mob） | cn.sharesdk | 分享ShareSDK | `@zztsdk/sharesdk` | 同厂 |
| 友盟分享 U-Share | com.umeng.socialize | 友盟社会化分享（U-Share） | `@umeng/share` | 同厂 |

## 音视频 / RTC

| Android SDK | Android 标识 | 鸿蒙对应 | ohpm 包名 | 匹配 |
|---|---|---|---|---|
| 声网 Agora RTC | io.agora.rtc | 声网音频/视频 SDK | `@shengwang/rtc-voice` / `@shengwang/rtc-full` | 同厂 |
| 融云音视频 | cn.rongcloud.rtc | 融云 CallKit/CallLib/RTCLib | `@rongcloud/callkit` 等 | 同厂 |
| 阿里云播放器 | com.aliyun.player | 阿里云播放器SDK | `@aliyun_video_cloud/aliyun_player` | 同厂 |
| 腾讯云播放器/直播 | com.tencent.liteav | 腾讯云播放器/直播 SDK | `LiteAVSDK` / `TXLiteAVSDK` | 同厂 |

## 统计 / 归因 / 监控

| Android SDK | Android 标识 | 鸿蒙对应 | ohpm 包名 | 匹配 |
|---|---|---|---|---|
| 友盟统计 U-App | com.umeng.analytics | 友盟 common（统计基座） | `@umeng/common`（+ ohpm 上的 `@umeng/analytics`） | 同厂 |
| 友盟性能 U-APM | com.umeng.umcrash | 友盟应用性能监控（U-APM） | `@umeng/apm` | 同厂 |
| GrowingIO | com.growingio | GrowingIO Analytics | `@growingio/analytics` | 同厂 |
| AppsFlyer / Adjust（归因） | com.appsflyer / com.adjust | 热力引擎 SolarEngine（归因分析） | `@solarengine/core` | 对等 |
| 阿里云 ARMS | com.alibaba.arms | 阿里云用户体验监控 | `@alibabacloud_rum/harmony_sdk` | 同厂 |

## 支付 / 登录 / 认证

| Android SDK | Android 标识 | 鸿蒙对应 | ohpm 包名 | 匹配 |
|---|---|---|---|---|
| 支付宝 SDK | com.alipay.sdk | cashier_alipay/cashiersdk | `@cashier_alipay/cashiersdk` | 同厂 |
| 极光认证（一键登录） | cn.jiguang.verifysdk | 极光认证 | `@jg/verify` | 同厂 |
| 友盟智能认证 U-Verify | com.umeng.umverify | 友盟智能认证（U-Verify） | `@umeng/verify` | 同厂 |
| 个推一键认证 | com.g.gysdk | 个推一键认证 | `@getui/gysdk` | 同厂 |
| 微博登录/分享 | com.sina.weibo.sdk | 微博分享登录SDK | 见 sdks/7afe7ff8（薄，走线上） | 同厂 |
| 极验验证码 | com.geetest.sensebot | 极验行为验证第四代 | `@geetest/captcha` | 同厂 |

## 广告

| Android SDK | Android 标识 | 鸿蒙对应 | ohpm 包名 | 匹配 |
|---|---|---|---|---|
| 穿山甲 | com.byted.pangle | 穿山甲广告SDK | 见 sdks/2f4ea5c4（薄，走线上） | 同厂 |
| TopOn / Taku | com.anythink | Taku 聚合广告SDK | `anythink_sdk` | 同厂 |
| Sigmob | com.sigmob | Sigmob广告SDK | `@sigmob/adsdk` | 同厂 |

## 地图 / 定位 / 工具

| Android SDK | Android 标识 | 鸿蒙对应 | ohpm 包名 | 匹配 |
|---|---|---|---|---|
| 高德地图 | com.amap.api | 高德地图 / 高德定位 | 见 sdks/2e3feb4c、3c4f6d01（薄，走线上） | 同厂 |
| 智齿客服 | com.sobot.chat | 智齿客服 SDK | `@sobot/chat_client` | 同厂 |
| 福昕 PDF | com.foxit | 福昕 PDF SDK | 见 sdks/63a2a6c6 | 同厂 |
| MobLink 深度链接 | com.mob.moblink | MobLink | 见 l0-index | 同厂 |

## 未收录高频项（确认过市场快照里没有，直接走 online-lookup）

- 神策 SensorsData、个推 GTC、百度地图、腾讯地图：2026-07 快照未见同厂鸿蒙版；先搜 ohpm，再按能力对等在 l0-index 对应分类里选。
- 微信 OpenSDK / QQ 互联：走华为官方与腾讯的适配公告核实，勿凭记忆写包名。
