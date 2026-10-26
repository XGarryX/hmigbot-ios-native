# 网易云信 NIM `@nimsdk/*` HarmonyOS SDK 接入指南

> 资料来源:网易云信官方文档(doc.yunxin.163.com/messaging2)、官方 Demo(github.com/netease-im/nim-harmony-demo)、context7 索引。
> SDK 截至 2026-05 已迭代到 v10.7.0+,要求 DevEco Studio NEXT Developer Beta1 (5.0.3.300+) 与 HarmonyOS API 12+。

## 1. 模块拆分(@nimsdk/*)

云信 NIM 把能力拆成 ~10 个独立 har 模块,**按需引入**。这是和七鱼/腾讯 IM 最大的区别 —— 它不强制把所有功能都打进同一个包。

### 必备模块(任何场景都要)

| 模块 | 作用 |
|------|------|
| `@nimsdk/nim` | SDK 主入口(NIMSdk 类、注册自定义 service)|
| `@nimsdk/base` | 基础类型(NIMInitializeOptions / NIMServiceOptions / V2NIMProvidedServiceType / NIMInterface)|

### 业务模块(按需选)

| 模块 | 作用 | 备注 |
|------|------|------|
| `@nimsdk/conversation` | 云端会话列表 | 与 localconversation **互斥** |
| `@nimsdk/conversationgroup` | 会话分组 | 需要先开通会话分组功能 |
| `@nimsdk/localconversation` | 本地会话 | 与 conversation 互斥;离线优先场景 |
| `@nimsdk/message` | 消息收发(文本/图片/视频/自定义) | 高频使用 |
| `@nimsdk/team` | 群组管理 | 群成员、禁言、权限 |
| `@nimsdk/user` | 用户资料 | 自己/他人 profile |
| `@nimsdk/friend` | 好友关系 | 加好友、黑名单 |
| `@nimsdk/notification` | 自定义通知 | 不走消息通道的轻量通知 |
| `@nimsdk/setting` | 设置管理 | 免打扰、消息提醒 |
| `@nimsdk/signalling` | 信令 | 1v1 / 多人通话信令 |
| `@nimsdk/chatroom` | 聊天室 | 万人直播间 |
| `@nimsdk/search` | 本地全文检索 | 与 localconversation 配合 |

### 元服务(Atomic Service)专用

如果是鸿蒙元服务(快应用)而非完整 App,只需依赖 `@nimsdk/atomic`,并在 `build-profile.json5` 设置 `strictMode.useNormalizedOHMUrl: true`。

## 2. 依赖配置

### 方式一:本地 har 包(主流)

云信 SDK 大多通过 har 包分发,放在 `libs/` 目录下:

```json5
// entry/oh-package.json5
{
  "dependencies": {
    "@nimsdk/nim": "file:../../libs/nim.har",
    "@nimsdk/base": "file:../../libs/base.har",
    "@nimsdk/conversation": "file:../../libs/conversation.har",
    "@nimsdk/message": "file:../../libs/message.har",
    "@nimsdk/team": "file:../../libs/team.har",
    "@nimsdk/user": "file:../../libs/user.har",
    "@nimsdk/friend": "file:../../libs/friend.har",
    "@nimsdk/signalling": "file:../../libs/signalling.har"
  }
}
```

### 方式二:ohpm 远程拉取(部分模块支持)

```bash
ohpm install @nimsdk/nim
ohpm install @nimsdk/base
# ... 按需安装
```

如果 ohpm 找不到包,以官方 har 包下载页 https://yunxin.163.com/im-sdk-demo 为准。

### module.json5 权限

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

## 3. 完整接入示例

### 3.1 注册自定义 Service(在 EntryAbility / 静态初始化处)

云信 SDK 用**注册式架构**:必须先告诉 SDK 你要用哪些 Service,SDK 才会拉起对应模块。

```ts
import { NIMInitializeOptions, NIMServiceOptions, V2NIMProvidedServiceType, NIMInterface } from '@nimsdk/base';
import { NIMSdk } from '@nimsdk/nim';
import { V2NIMTeamServiceImpl } from '@nimsdk/team';
import { V2NIMConversationServiceImpl } from '@nimsdk/conversation';
import { V2NIMUserServiceImpl } from '@nimsdk/user';
import { V2NIMFriendServiceImpl } from '@nimsdk/friend';
import { V2NIMClientAntispamUtil, V2NIMMessageServiceImpl } from '@nimsdk/message';
import { V2NIMNotificationServiceImpl } from '@nimsdk/notification';
import { V2NIMSettingServiceImpl } from '@nimsdk/setting';
import { V2NIMSignallingServiceImpl } from '@nimsdk/signalling';

// 团队
NIMSdk.registerCustomServices(
  V2NIMProvidedServiceType.V2NIM_PROVIDED_SERVICE_TEAM,
  (core, serviceName, serviceConfig) => new V2NIMTeamServiceImpl(core, serviceName, serviceConfig),
);

// 反垃圾
NIMSdk.registerCustomServices(
  V2NIMProvidedServiceType.V2NIM_PROVIDED_SERVICE_CLIENT_ANTISPAM_UTIL,
  (core, serviceName, serviceConfig) => new V2NIMClientAntispamUtil(core, serviceName, serviceConfig),
);

// 云端会话(与 localconversation 二选一)
NIMSdk.registerCustomServices(
  V2NIMProvidedServiceType.V2NIM_PROVIDED_SERVICE_CONVERSATION,
  (core, serviceName, serviceConfig) => new V2NIMConversationServiceImpl(core, serviceName, serviceConfig),
);

// 消息
NIMSdk.registerCustomServices(
  V2NIMProvidedServiceType.V2NIM_PROVIDED_SERVICE_MESSAGE,
  (core, serviceName, serviceConfig) => new V2NIMMessageServiceImpl(core, serviceName, serviceConfig),
);

// ... 其他模块同样注册
```

### 3.2 初始化 SDK

```ts
const initializeOptions: NIMInitializeOptions = {
  appkey: 'your-yunxin-appkey',                    // 云信控制台 → 应用信息
  logLevel: LogLevel.Debug,                         // Error / Warn / Info / Debug
  isOpenConsoleLog: true,                           // 是否输出到 hilog
};

const serviceOptions: NIMServiceOptions = {
  // 离线推送(可选)
  pushServiceConfig: {
    // ⚠ 必须与控制台上传的鸿蒙推送证书名称完全一致;> 32 字符登录会报 500
    harmonyCertificateName: 'PROD_HMOS_PUSH_xxx',
  },
  // 自定义服务器地址(自有部署 / 测试环境时用)
  // loginServiceConfig: {
  //   lbsUrls: ['https://lbs.netease.im/lbs/webconf'],
  //   linkUrl: 'weblink-harmony.netease.im:443',
  // },
};

const nim: NIMInterface = NIMSdk.newInstance(context, initializeOptions, serviceOptions);
// 全局保存 nim 实例(单例),后续业务调用都从这里取
```

`context` 是 `common.UIAbilityContext`,在 EntryAbility.onCreate 拿到。

### 3.3 登录与状态监听

```ts
// 监听登录状态变化(掉线、被踢、token 过期等)
nim.loginService.on('onLoginStatus', (loginStatus) => {
  console.info(`[NIM] loginStatus = ${loginStatus}`);
  // 1: LOGGED   2: LOGGING   3: UNLOGINED   4: LOGOUT
});

// 监听 token 过期(需要业务侧重新换 token)
nim.loginService.on('onLoginFailed', (error) => {
  console.warn(`[NIM] loginFailed: ${JSON.stringify(error)}`);
});

// 登录(token 由业务后端签发,每个用户独立)
try {
  await nim.loginService.login('YOUR_ACCOUNT_ID', 'YOUR_TOKEN');
  console.info('[NIM] login success');
} catch (e) {
  console.warn(`[NIM] login failed: ${JSON.stringify(e)}`);
}
```

### 3.4 发送消息

```ts
// 文本消息
const message = nim.messageCreator.createTextMessage('hello');
await nim.messageService?.sendMessage(message, 'YOUR_ACCOUNT|1|RECEIVER_ACCOUNT');
// 会话 ID 格式: 发送方账号|会话类型|接收方账号
// 会话类型: 1=P2P单聊  2=群聊  3=超大群

// 图片消息
const imgMessage = nim.messageCreator.createImageMessage('/data/storage/.../photo.jpg');
await nim.messageService?.sendMessage(imgMessage, conversationId);

// 自定义消息(客服业务常用 —— 透传业务字段)
const customMessage = nim.messageCreator.createCustomMessage(JSON.stringify({
  type: 'order_card',
  orderId: 'TRY-2026-001',
  status: 'refunded',
}));
await nim.messageService?.sendMessage(customMessage, conversationId);
```

### 3.5 接收消息

```ts
nim.messageService?.on('onReceiveMessages', (messages) => {
  for (const msg of messages) {
    console.info(`[NIM] received from=${msg.senderId} type=${msg.messageType} text=${msg.text}`);
    // 业务侧追加到聊天 UI 数据源
  }
});

// 撤回 / 修改回调(可选)
nim.messageService?.on('onReceiveMessagesModified', (messages) => { /* ... */ });
nim.messageService?.on('onMessageRevokeNotifications', (notifications) => { /* ... */ });
```

### 3.6 会话列表

```ts
// 拉取会话列表(分页)
const result = await nim.conversationService?.getConversationList(0, 100);
// result.conversationList: V2NIMConversation[]

// 监听会话变更(新消息进来 / 未读数变化)
nim.conversationService?.on('onConversationChanged', (conversations) => {
  // 用 EventBus 广播给 UI 层刷新红点
});
```

### 3.7 用户资料(客服场景必透)

```ts
// 自己设置资料
await nim.userService?.updateSelfUserProfile({
  name: currentUser.nickName,
  mobile: currentUser.mobile,
  avatar: currentUser.avatar,
  ext: JSON.stringify({
    // 业务自定义透传字段,客服后台可见
    appName: '<your-app-name>',
    userId: currentUser.id,
    regChannel: '<register-channel>',
    versionName: '<app-version>',
  }),
});

// 拉取他人资料(客服面板要看用户卡片)
const profiles = await nim.userService?.getUserList(['ACCOUNT_ID_1']);
```

### 3.8 登出

```ts
try {
  await nim.loginService.logout();
} catch (e) {
  console.warn(`[NIM] logout failed: ${JSON.stringify(e)}`);
}
```

## 4. 配置项详解

云信 SDK 接收两个配置对象:`NIMInitializeOptions`(基础初始化)和 `NIMServiceOptions`(可选服务配置)。下表列出全部字段。

### 4.1 `NIMInitializeOptions`(必传)

```ts
import { NIMInitializeOptions, LogLevel } from '@nimsdk/base';

const initializeOptions: NIMInitializeOptions = {
  appkey: 'your-yunxin-appkey',
  logLevel: LogLevel.Info,
  isOpenConsoleLog: true,
};
```

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `appkey` | `string` | ✅ | — | 云信控制台 → 应用信息中获取的 AppKey,业务侧多端使用同一个 |
| `logLevel` | `LogLevel` | ❌ | `Info` | 日志级别枚举:`LogLevel.Error` / `Warn` / `Info` / `Debug`,生产环境用 `Warn` 或更高 |
| `isOpenConsoleLog` | `boolean` | ❌ | `false` | 是否把 SDK 日志同步输出到 hilog/console;调试期开,上线关 |
| `cacheLimit` | `number` | ❌ | SDK 自定 | 本地缓存上限(MB),≤0 表示使用默认 |
| `enableForeground` | `boolean` | ❌ | `true` | 是否启用前台保活 |

### 4.2 `NIMServiceOptions`(可选)

```ts
const serviceOptions: NIMServiceOptions = {
  loginServiceConfig: {
    lbsUrls: ['https://lbs.netease.im/lbs/webconf'],
    linkUrl: 'weblink-harmony.netease.im:443',
  },
  pushServiceConfig: {
    harmonyCertificateName: 'PROD_HMOS_PUSH_xxx',
  },
};
```

#### 4.2.1 `loginServiceConfig`(自定义登录服务地址)

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `lbsUrls` | `string[]` | ❌ | LBS(负载均衡)接入点列表,公有云默认即可,**自有部署 / 测试环境**才需要覆盖 |
| `linkUrl` | `string` | ❌ | WebLink 长连接地址,与 `lbsUrls` 一起改 |
| `dnsResolveTimeout` | `number` | ❌ | DNS 解析超时(ms) |

公有云用户**不需要**配置这一段,SDK 内置默认地址。

#### 4.2.2 `pushServiceConfig`(鸿蒙离线推送)

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `harmonyCertificateName` | `string` | 启用推送时必填 | 与云信控制台上传的鸿蒙推送证书名称**完全一致**,⚠ 上限 32 字符,超出会让 `loginService.login` 报 500 错误 |
| `pushOnNotification` | `boolean` | ❌ | 是否在通知栏弹通知,默认 `true`;App 内自定义 UI 时可关 |

不需要鸿蒙离线推送时,整个 `pushServiceConfig` 字段可省略。

### 4.3 单条消息推送配置 `V2NIMMessagePushConfig`

发送消息时可以挂载 `pushConfig`,精细控制单条消息的离线推送行为:

```ts
const message = nim.messageCreator.createTextMessage('hello');
message.pushConfig = {
  pushEnabled: true,
  pushTitle: '客服消息',
  pushContent: '您有新的客服回复',
  pushPayload: JSON.stringify({ type: 'reply', orderId: 'TRY-001' }),
  category: 'IM',
  forcePush: false,
};
await nim.messageService?.sendMessage(message, conversationId);
```

| 字段 | 类型 | 默认 | 说明 |
|------|------|------|------|
| `pushEnabled` | `boolean` | `true` | 该条消息是否走离线推送 |
| `pushTitle` | `string` | 业务昵称 | 通知栏标题(≤50 字符) |
| `pushContent` | `string` | 消息文本预览 | 通知栏正文(≤200 字符) |
| `pushPayload` | `string` | — | 业务自定义透传字段(stringify 的 JSON) |
| `category` | `string` | `'IM'` | 鸿蒙推送分类:`IM` / `SOCIAL_COMMUNICATION` / `VOIP` / `SUBSCRIPTION` 等,**鸿蒙强制要求**,不传可能被系统限流 |
| `forcePush` | `boolean` | `false` | 是否强制推送(忽略接收方免打扰设置),通常仅运营公告用 |

### 4.4 `LogLevel` 枚举

```ts
import { LogLevel } from '@nimsdk/base';

LogLevel.Error    // 仅错误
LogLevel.Warn     // 错误 + 警告
LogLevel.Info     // 默认,业务关键动作
LogLevel.Debug    // 全部,调试期用
```

### 4.5 工程级配置(build-profile.json5)

V1.3.0+ 字节码 HAR 包要求工程级开启 `useNormalizedOHMUrl`:

```json5
{
  "app": {
    "products": [{
      "buildOption": {
        "strictMode": {
          "useNormalizedOHMUrl": true
        }
      }
    }]
  }
}
```

不开会导致模块解析失败;**所有云信 NIM 项目都要配**。

### 4.6 module.json5 推送相关配置(可选)

如启用鸿蒙离线推送,需在 `entry/src/main/module.json5` 添加 metadata 与权限:

```json5
{
  "module": {
    "requestPermissions": [
      { "name": "ohos.permission.INTERNET" },
      { "name": "ohos.permission.GET_NETWORK_INFO" }
    ],
    "metadata": [
      {
        "name": "client_id",
        "value": "<华为推送服务的 Client ID>"
      }
    ]
  }
}
```

`client_id` 在华为开发者平台 → 推送服务 → 应用配置中获取。

## 5. 推荐封装层模板

云信 SDK 直接调用方式 API 散件较多,实战中建议在业务侧封装一个 Service 类,对外暴露 `init / login / logout / sendText` 等高层方法,把 SDK 内部 service 注册、事件订阅、错误吞咽逻辑藏起来:

```ts
// services/NimService.ets
import { NIMSdk } from '@nimsdk/nim';
import { NIMInterface, NIMInitializeOptions, NIMServiceOptions, LogLevel } from '@nimsdk/base';
import { common } from '@kit.AbilityKit';

export interface NimInitConfig {
  appKey: string;
  /** 鸿蒙离线推送证书名称(与控制台一致,≤32 字符);不需要推送可不填 */
  harmonyCertificateName?: string;
}

export interface NimUserProfile {
  nickName?: string;
  mobile?: string;
  avatar?: string;
  /** 业务自定义透传字段(stringify 后写入 ext) */
  extras?: Record<string, string>;
}

export class NimService {
  private static initialized: boolean = false;
  private static nim: NIMInterface | undefined = undefined;

  static isReady(): boolean {
    return NimService.initialized && NimService.nim !== undefined;
  }

  static async init(context: common.UIAbilityContext, config: NimInitConfig): Promise<void> {
    if (NimService.initialized) return;
    try {
      // 1. 注册业务 service(见 §4.1,按需挑选)
      NimService.registerServices();

      // 2. 创建实例
      const initOpts: NIMInitializeOptions = {
        appkey: config.appKey,
        logLevel: LogLevel.Info,
        isOpenConsoleLog: true,
      };
      const svcOpts: NIMServiceOptions = {};
      if (config.harmonyCertificateName !== undefined) {
        svcOpts.pushServiceConfig = { harmonyCertificateName: config.harmonyCertificateName };
      }
      NimService.nim = NIMSdk.newInstance(context, initOpts, svcOpts);

      // 3. 监听全局事件,转发给业务侧的事件总线 / 状态管理
      NimService.nim.loginService.on('onLoginStatus', (status) => {
        console.info(`[NimService] loginStatus=${status}`);
        // 推荐: EventBus.post('nim_login_status', { status });
      });
      NimService.nim.messageService?.on('onReceiveMessages', (msgs) => {
        // 推荐: EventBus.post('nim_new_message', { messages: msgs });
      });

      NimService.initialized = true;
    } catch (e) {
      console.warn(`[NimService] init failed: ${JSON.stringify(e)}`);
    }
  }

  /** registerServices 见 §4.1,按业务需要选择模块 */
  private static registerServices(): void { /* ... */ }

  static async login(accountId: string, token: string, profile?: NimUserProfile): Promise<void> {
    if (!NimService.isReady()) throw new Error('NIM not ready');
    await NimService.nim!.loginService.login(accountId, token);
    if (profile !== undefined) {
      await NimService.nim!.userService?.updateSelfUserProfile({
        name: profile.nickName,
        mobile: profile.mobile,
        avatar: profile.avatar,
        ext: profile.extras !== undefined ? JSON.stringify(profile.extras) : undefined,
      });
    }
  }

  static async logout(): Promise<void> {
    if (!NimService.isReady()) return;
    try {
      await NimService.nim!.loginService.logout();
    } catch (e) {
      console.warn(`[NimService] logout failed: ${JSON.stringify(e)}`);
    }
  }

  static async sendText(conversationId: string, text: string): Promise<void> {
    if (!NimService.isReady()) throw new Error('NIM not ready');
    const msg = NimService.nim!.messageCreator.createTextMessage(text);
    await NimService.nim!.messageService?.sendMessage(msg, conversationId);
  }
}
```

## 6. 离线推送(鸿蒙独有配置)

云信鸿蒙离线推送依赖**鸿蒙推送服务**,需要:

1. 华为开发者平台为该 bundleId 启用推送服务,创建服务账号凭证
2. 下载凭证 JSON,上传到云信控制台 → 应用 → 即时通讯 → 功能配置 → 消息推送 → 证书管理 → 鸿蒙
3. `module.json5` 添加推送 metadata + `client_id`
4. 业务代码 `serviceOptions.pushServiceConfig.harmonyCertificateName` 与控制台证书名一致

```ts
// SDK 自动上报 pushToken;手动开关:
nim.pushService?.enable(true);   // 开启鸿蒙推送
nim.pushService?.enable(false);  // 关闭

// 单条消息控制是否推送
const message = nim.messageCreator.createTextMessage('hello');
message.pushConfig = {
  pushEnabled: true,
  pushTitle: '客服消息',
  pushContent: '您有新的客服回复',
  category: 'IM',           // 鸿蒙推送分类(必填,否则可能被系统限流)
};
await nim.messageService?.sendMessage(message, conversationId);
```

**鸿蒙推送特殊规则**:
- 通知必须在 `notificationManager.requestEnableNotification()` 已授权前提下才能触达
- `category` 字段是鸿蒙强制要求的(IM / SOCIAL_COMMUNICATION 等),否则可能被强制限流
- 证书名称 ≤ 32 字符

## 7. 跨端 API 一致性

云信 NIM HarmonyOS SDK 的 V2NIM 系列 API 与 Android / iOS V2NIM 高度对齐:

| Android | HarmonyOS | 备注 |
|---------|-----------|------|
| `NIMClient.init(context, account, options, sdkOptions)` | `NIMSdk.newInstance(context, initializeOptions, serviceOptions)` | 入参更细粒度 |
| `AuthService.login(loginInfo)` | `nim.loginService.login(accountId, token)` | Promise 风格 |
| `MsgService.sendMessage(...)` | `nim.messageService.sendMessage(message, conversationId)` | 同名 |
| `Observer<List<IMMessage>>` | `on('onReceiveMessages', (msgs) => {})` | 事件订阅 |
| `MessageBuilder.createTextMessage(...)` | `nim.messageCreator.createTextMessage(...)` | 通过实例属性 |

迁移成本:Android 已有 NIM 接入的项目,业务代码 60-70% 可以按字面替换,主要差别在异步风格(callback → Promise)和 service 注册式架构。

## 8. 常见踩坑

### 8.1 互斥模块同时引入

`@nimsdk/conversation` 与 `@nimsdk/localconversation` **不能同时引入**,否则 SDK 启动时报"两个 service 同时注册"。规则:

- 在线优先 / 多端同步 → 用 `conversation`(云端)
- 离线优先 / 弱网 → 用 `localconversation`(本地)

### 8.2 推送证书名称超长

`harmonyCertificateName` 上限 32 字符。超过会让 `loginService.login` 抛 500 错误,但日志不直接说明原因。如果登录莫名失败,**先检查这个字段长度**。

### 8.3 字节码 HAR 配置遗漏

SDK V1.3.0+ 采用官方推荐的字节码构建,需要在工程级 `build-profile.json5` 配置:

```json5
{
  "app": {
    "products": [{
      "buildOption": {
        "strictMode": {
          "useNormalizedOHMUrl": true   // 必须 true
        }
      }
    }]
  }
}
```

不开会报 module 解析失败。

### 8.4 isConnected ≠ isLogged

V1.3.0+ 新增 `ChatClient#isConnected` 方法,**自动登录场景下登录态变 LOGGED 不等于已连上服务端**。如果发消息失败,先用 `isConnected` 判断 socket 状态,而不是只看 loginStatus。

### 8.5 登出后必须再次注册 service 吗?

不需要。`NIMSdk.registerCustomServices` 是进程级,只调用一次;`logout` / `login` 不重置注册表。

## 9. 关键文档链接

- 集成指南:https://doc.yunxin.163.com/messaging2/guide/DMzMTMxMjM
- 初始化:https://doc.yunxin.163.com/messaging2/guide/TY4MTAxNzE
- 离线推送:https://doc.yunxin.163.com/messaging2/guide/TMzMzE5Mjc
- 鸿蒙推送证书:https://doc.yunxin.163.com/messaging2/guide/TkyNTI3OTg
- TypeDoc API:https://doc.yunxin.163.com/messaging2/references/harmony/typedoc/Latest/zh/index.html
- 官方 Demo:https://github.com/netease-im/nim-harmony-demo
- SDK 下载:https://yunxin.163.com/im-sdk-demo
