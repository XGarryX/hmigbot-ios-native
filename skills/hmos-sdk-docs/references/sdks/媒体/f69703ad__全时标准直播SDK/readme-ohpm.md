> 来源: ohpm 中央仓 README(T1 信源) | 包: `livesdk` | ohpm 最新版: 1.0.1 | 抓取: 2026-07-16
> 注意: 版本可能比市场快照新,以此为准时核对 CHANGELOG

# 全时标准直播 SDK(HarmonyOS)

## 简介

全时标准直播 SDK 是一套用于在 HarmonyOS 应用中快速集成全时直播能力的 Native SDK。只需少量代码,即可在现有应用中嵌入完整的直播间界面、直播互动,以及连麦等相关能力,并支持通过配置对客户端进行定制。

SDK 同时支持基于 WebRTC 的低延迟实时拉流与音视频渲染,集成简单、接入成本低,适合具备一定开发能力、希望在自有应用中直接集成直播或视频会议能力的客户。依托全时云直播后台,单场直播可支持百万级并发。

更多问题可参考官方文档:https://developer.quanshi.com/cn

## 快速集成

### 1. 添加模块依赖

ohpm install livesdk

### 2. 导入 SDK

```typescript
import { QSLiveSDK, QSLiveReq } from 'livesdk'
```

### 3. 初始化并调用

```typescript
// 应用启动时初始化
QSLiveSDK.init(this.pathStack)

// 加入直播间
const req: QSLiveReq = {
  pcode: "",
  liveCode: "",
  liveUrl: "",
  userName: "张三",
  userId: "",
  conferenceId: "",
  audienceJoinUrl: "https://example.com/live/xxx",
  phone: "",
  email: "user@example.com",
  openId: "",
  countryCode: "86",
  company: "",
  umsToken: "",
  isGuest: "",
  extUserId: ""
}

await QSLiveSDK.joinLive(req, (resultCode: number) => {
  if (resultCode === 0) {
    // 加入成功
  } else {
    // 加入失败,resultCode 为错误码
  }
})

// 退出直播间
await QSLiveSDK.exitLive((resultCode: number) => {
  if (resultCode === 0) {
    // 退出成功
  }
})
```

## API 说明

### QSLiveSDK.init()

初始化 SDK,预留全局配置、日志等扩展能力。当前为空实现,建议在应用启动阶段调用一次。

```typescript
QSLiveSDK.init(): void
```

---

### QSLiveSDK.joinLive()

加入直播间。

```typescript
QSLiveSDK.joinLive(
  req: QSLiveReq,
  callback?: (resultCode: number) => void
): Promise<void>
```

| 参数 | 类型 | 说明 |
|------|------|------|
| `req` | `QSLiveReq` | 入会请求参数 |
| `callback` | `(resultCode: number) => void` | 可选,加入结果回调 |

**resultCode 说明:**

| 值 | 说明 |
|----|------|
| `0` | 加入成功 |
| `-1` | 参数校验失败(如 pcode、观众链接为空) |
| 其他 | 服务端返回的业务错误码 |

---

### QSLiveSDK.exitLive()

退出直播间,释放聊天室、心跳、WebSocket 等资源,并通知直播间页面关闭。

```typescript
QSLiveSDK.exitLive(
  callback?: (resultCode: number) => void
): Promise<void>
```

| 参数 | 类型 | 说明 |
|------|------|------|
| `callback` | `(resultCode: number) => void` | 可选,退出结果回调 |

**resultCode 说明:**

| 值 | 说明 |
|----|------|
| `0` | 退出成功(含当前未在直播间内的幂等场景) |

---

## QSLiveReq 参数说明

| 字段 | 类型 | 说明 |
|------|------|------|
| `pcode` | `string` | 入会密码。主持人为 pcode1,参会人为 pcode2 |
| `liveCode` | `string` | 分享直播码 |
| `liveUrl` | `string` | 链接入会时的直播 URL |
| `userName` | `string` | 用户名 |
| `userId` | `string` | 用户 ID |
| `conferenceId` | `string` | 会议 ID |
| `audienceJoinUrl` | `string` | 观众入会链接(`pcode` 为空时必填) |
| `phone` | `string` | 手机号 |
| `email` | `string` | 邮箱 |
| `openId` | `string` | OpenID |
| `countryCode` | `string` | 手机国家码,不带 `+`,默认 `86` |
| `company` | `string` | 部门 |
| `umsToken` | `string` | UMS Token |
| `isGuest` | `string` | 落地页进入直播间传 `1` |
| `extUserId` | `string` | 外部用户 ID |

> `pcode` 与 `audienceJoinUrl` 至少传一个;通过观众链接入会时,SDK 会自动从链接中解析 `pcode` 和 `ukey`。

## 典型调用流程

```
应用启动
  └── QSLiveSDK.init()
用户点击「进入直播」
  └── QSLiveSDK.joinLive(req, callback)
        └── callback(0) → 进入直播间页面
用户离开 / 点击关闭
  └── QSLiveSDK.exitLive(callback)
        └── 释放资源,关闭直播间
```
