---
name: arkts-customer-service
description: 在 ArkTS / HarmonyOS NEXT 项目中集成或替换三方在线客服 / IM SDK 的落地指南，覆盖网易七鱼（@ysf/sdk）、网易云信 NIM（@nimsdk/*）、腾讯云 IM（@tencentcloud/imsdk）三家鸿蒙原生 SDK。当用户提到"在线客服"、"客服 SDK"、"IM 接入"、"聊天功能"、"消息推送"、"@ysf/sdk"、"@nimsdk"、"@tencentcloud/imsdk"、"unicorn"、"七鱼"、"云信"、"腾讯云 IM"、"TIMSDK"、"V2TIMManager"、"客服替换"、"客服选型"，或者要把 Android 端的 Unicorn / NIM / IMSDK 迁移到鸿蒙时，务必触发此 skill。即使用户只是说"客服功能加一下"、"加个聊天"、"换个客服厂商"、"客服后台连不上"、"客服消息收不到"，也应触发——因为客服赛道在鸿蒙原生上选项少且踩坑多，盲选会浪费工期。
metadata:
  type: domain
  domain: system
  tags:
  - domain
  - customer-service
  - im
  - sdk
  - third-party
  - qiyu
  - yunxin
  - tencent-im
---
# ArkTS 三方客服 / IM SDK 集成指南

## 这个 skill 解决什么问题

在鸿蒙 NEXT 项目里集成在线客服 / 即时通讯能力时，本 skill 覆盖**三家有官方鸿蒙原生 SDK** 的厂商：

- **网易七鱼 `@ysf/sdk`** — 客服业务 SDK，自带聊天 UI，业务接入 init / openChat / logout 三个方法即可
- **网易云信 NIM `@nimsdk/*`** — 通用 IM 通道，10+ 个 har 模块按需组合，UI 完全自造
- **腾讯云 IM `@tencentcloud/imsdk`** — 通用 IM 通道，单包 ohpm 安装，V2TIM 系列 API 与 Android/iOS 高度对齐，UI 完全自造

每家详细的安装、配置项、API、踩坑放在对应的 reference 文件，这里只负责**确定走哪家**和**列出三家共性接入步骤**。

## 选型流程：以用户输入为准

**核心原则：不要替用户做选型决策。**SDK 选择有强烈的业务背景因素（已有合同、运营后台已开通、与既有生态兼容等），AI 替用户拍板会浪费工期。按下面优先级走：

### 优先级 1：用户直接说明厂商

用户明确指名时，直接走对应 reference，不要追问、不要建议替代方案：

| 用户输入示例 | 行动 |
|---|---|
| "用七鱼" / "接 @ysf/sdk" / "Qiyu" / "Unicorn" | 读 `references/qiyu.md` |
| "用云信" / "接 NIM" / "@nimsdk" / "yunxin" | 读 `references/yunxin-nim.md` |
| "用腾讯云 IM" / "TIMSDK" / "@tencentcloud/imsdk" / "V2TIMManager" | 读 `references/tencent-im.md` |

### 优先级 2：从用户给出的参考源码 / 配置识别厂商

用户给了 Android 项目源码、`build.gradle`、`oh-package.json5` 或文档片段时，先识别已有依赖：

| 识别到的依赖 / 类名 | 对应 reference |
|---|---|
| `com.qiyukf.unicorn`、`Unicorn.initSdk`、`YSFUserInfo`、`@ysf/sdk` | `references/qiyu.md` |
| `com.netease.nimlib`、`NIMClient.init`、`@nimsdk/nim`、`V2NIMTeamServiceImpl` | `references/yunxin-nim.md` |
| `com.tencent.imsdk`、`V2TIMManager`、`@tencentcloud/imsdk`、`@tencentcloud/timpush` | `references/tencent-im.md` |

识别明确后**直接走对应 reference**，不要建议换厂商，除非用户主动询问"有没有更好的选择"。

### 优先级 3：用户未指明 → 主动询问

如果用户没有提到具体厂商、也没给参考源码，**先问清楚再动手**。问法举例：

> 鸿蒙端有官方 SDK 的客服 / IM 厂商有三家：
>
> 1. **网易七鱼 `@ysf/sdk`** —— 自带聊天 UI 的客服 SDK，最快接入
> 2. **网易云信 NIM `@nimsdk/*`** —— 通用 IM 通道，UI 自造
> 3. **腾讯云 IM `@tencentcloud/imsdk`** —— 通用 IM 通道，UI 自造
>
> 你计划用哪家？或者已经在 Android 端用过哪家、希望延续？

不要在用户回答前自行决策。如果用户回复"你看着办" / "都行" / "随便"，再把下面三家速查表给他看让他敲定。

## 三家鸿蒙原生 SDK 速查对比（用户犹豫时给他看）

| 维度 | `@ysf/sdk`（七鱼） | `@nimsdk/*`（云信） | `@tencentcloud/imsdk`（腾讯云 IM） |
|------|-------|-------|-------|
| 定位 | **客服业务 SDK** | 通用 IM 通道 | 通用 IM 通道 |
| 自带聊天 UI | ✅ 有（SDK 内部渲染） | ❌ 全自造 | ❌ 全自造 |
| 接入复杂度 | ⭐ 极简（3 方法） | ⭐⭐⭐ 多模块组合 | ⭐⭐ 单包多 API |
| 安装方式 | `ohpm i @ysf/sdk` | har 包本地引入（部分模块支持远程 ohpm）| `ohpm i @tencentcloud/imsdk` |
| API 风格 | configXxx + open(uiContext) | nim.xxxService.method() + on(event) | V2TIMManager.getXxxManager().method(args) |
| 异步风格 | 同步 + on() 回调 | Promise + on() 事件 | Promise + addListener |
| 跨端一致性 | 与 Android Unicorn API 不一致（HOS 重写） | 与 V2NIM API 高度一致 | 与 V2TIM API 完全一致 |
| 客服业务（机器人/转人工/留言/工单） | ✅ 内建 | ❌ 自实现 | ❌ 自实现 |
| 离线推送 | 内建（onUnread 事件） | `pushServiceConfig.harmonyCertificateName` | 单独包 `@tencentcloud/timpush` |
| 必需权限 | INTERNET / GET_NETWORK_INFO | INTERNET / GET_NETWORK_INFO | INTERNET / GET_NETWORK_INFO |
| 沉浸式适配 | `setAvoidArea({top, bottom})` | 全自造，按业务页处理 | 全自造，按业务页处理 |
| 运营后台 | 七鱼控制台 → bundleId 绑定 | 云信控制台 → AppKey + 鸿蒙推送证书 | 腾讯云 IM 控制台 → SDKAppID + UserSig |

## 通用接入清单（任选其一都需要）

不管用户最终选哪家，下面这几条是鸿蒙端接 IM/客服 SDK 的共性必做项，跳过会埋雷：

### 1. 权限声明（module.json5）

```json
{
  "module": {
    "requestPermissions": [
      { "name": "ohos.permission.INTERNET" },
      { "name": "ohos.permission.GET_NETWORK_INFO" }
    ]
  }
}
```

三家都强制要求，未声明会让 SDK 在网络握手阶段直接失败。

### 2. 初始化时机（EntryAbility.onCreate）

三家都建议**全局初始化一次**，放在 `EntryAbility.onCreate` 内。使用 fire-and-forget 模式 —— 不 await，避免 SDK 网络握手 hang 住 onCreate 影响首屏：

```ts
// EntryAbility.ets - 任意一家通用模板
SomeSdk.init(this.context).catch((err: Error): void => {
  hilog.warn(DOMAIN, 'tag', '[XxxSdk] init failed: %{public}s', JSON.stringify(err));
});
```

失败时业务侧用 `isReady()` 判断 + 降级，不要让按钮"哑"——可以降级到本地 echo 壳页面或 H5 兜底。

### 3. 登出联动

用户登出时**必须**调 SDK 的 logout，否则下次以新身份登录会拉到旧用户的会话/消息：

```ts
// 在登出 Service / 退出登录的统一入口里调
SomeSdk.logout();   // 七鱼:QiyuService.logout / 云信:nim.loginService.logout / 腾讯:V2TIMManager.logout
```

### 4. 沉浸式 / 安全区

如果项目开了 `setWindowLayoutFullScreen(true)` 沉浸式，客服/聊天页务必做安全区适配：

- 七鱼：调 SDK 自带 `setAvoidArea({top, bottom})`
- 云信 / 腾讯云：自渲染聊天页，按项目自身的安全区方案处理

### 5. UserInfo 透传（客服场景）

客服后台要看到用户的昵称 / 手机 / 注册渠道等信息。三家都支持把这些字段透给 SDK，但**字段命名 / 写入时机不同**：

- 七鱼：`setUserInfo({userId, data: YsfDataItem[]})`，每次 openChat 前调用
- 云信：`nim.userService.updateSelfUserProfile({...})`，登录后调
- 腾讯云：`V2TIMManager.setSelfInfo({...})`，登录后调

详见各 reference 的"用户资料"章节。

### 6. 异常边界：init 容错，业务调用让上层捕获

`init` 失败应吞掉转 warn，让业务降级而不是阻塞启动；`login / sendMessage / openChat` 等业务调用建议把异常抛出，由调用方页面 catch + UI 反馈（与项目自身的 Service / Page 异常约定保持一致）。

## 触发场景与典型问答

| 用户问题 | 应该读哪个 reference |
|---------|---------------------|
| "七鱼 openChat 标题栏样式不对怎么改？" | `references/qiyu.md` |
| "客服后台收不到消息，怎么排查？" | 当前在用的厂商对应 reference |
| "腾讯云 IM 鸿蒙怎么发图片消息？" | `references/tencent-im.md` |
| "@nimsdk 这一堆模块到底要哪几个？" | `references/yunxin-nim.md` |
| "云信 / 腾讯 IM 的初始化都有哪些配置项？" | 对应 reference 的"配置项详解"章节 |
| "客服 SDK 和 Android 端能不能打通？" | 对应 reference 的"跨端一致性"章节 |
| "客服页底部被手势条压住了" | 对应 reference 的"沉浸式适配"章节 |

## 下一步动作建议

1. **先确认厂商**：按"选型流程"三层优先级走，**不要替用户决策**
2. **厂商敲定后**：直接读对应 reference 的"完整接入示例 + 配置项详解"逐步落地
3. **调试**：先看对应 reference 的"常见踩坑"章节，再结合 hilog 定位


---

## See Also

- [arkts-immersive-safearea](../arkts-immersive-safearea/SKILL.md) — 客服/聊天页全屏 + 安全区适配
- [arkts-data-layer](../arkts-data-layer/SKILL.md) — 消息持久化 / 历史会话存储
- [arkts-login](../arkts-login/SKILL.md) / [arkts-payment](../arkts-payment/SKILL.md) / [arkts-ad](../arkts-ad/SKILL.md) — 同属第三方 SDK 系列（共享 module.json5 权限 / EntryAbility 初始化模式）
