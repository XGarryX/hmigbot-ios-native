# 腾讯云 IM `@tencentcloud/imsdk` HarmonyOS SDK 接入指南

> 资料来源:腾讯云官方文档(cloud.tencent.com/document/product/269)、TIMSDK GitHub(github.com/TencentCloud/TIMSDK)、context7 索引。
> SDK 截至 2026-05 主版本 7.7+,要求 DevEco Studio 5.0+ 与 HarmonyOS API 12+。

## 1. 安装

腾讯云 IM 鸿蒙端走**单包 ohpm 安装**,比云信的多模块更简单。

### 远程拉取(主流)

```bash
ohpm install @tencentcloud/imsdk
# 离线推送(可选)
ohpm install @tencentcloud/timpush
```

### 本地 har 包(版本锁死场景)

```json5
// entry/oh-package.json5
{
  "dependencies": {
    "@tencentcloud/imsdk": "file:./libs/imsdk-ohos-7.7.5294.har"
    // 或锁版本号:  "@tencentcloud/imsdk": "^7.7.5294"
  }
}
```

执行 `ohpm install` 完成依赖拉取。

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

## 2. 完整接入示例

### 2.1 初始化 SDK + 登录

腾讯云 IM 的 ArkTS API 结构:`V2TIMManager` 是顶层入口,业务能力通过 `V2TIMManager.getXxxManager()` 子模块取。所有方法**返回 Promise**,优先用 async-await。

```ts
import { V2TIMManager } from '@tencentcloud/imsdk';
import { BusinessError } from '@kit.BasicServicesKit';

const SDK_APP_ID = 1400000000;     // 你的 SDKAppID(腾讯云控制台 → 即时通信 IM → 应用管理)
const USER_ID = 'try_user_001';     // 业务侧 userId
const USER_SIG = 'xxx';             // 由业务后端用 SDKAppID + Secret 签发

// 1. 添加全局事件监听(连接、Token、被踢)
V2TIMManager.addIMSDKListener({
  onConnecting: () => console.info('[TIM] connecting'),
  onConnectSuccess: () => console.info('[TIM] connected'),
  onConnectFailed: (code, error) => console.warn(`[TIM] connect failed code=${code} ${error}`),
  onKickedOffline: () => {
    // 账号在别处登录被踢,业务侧引导用户重新登录
    console.warn('[TIM] kicked offline');
  },
  onUserSigExpired: () => {
    // userSig 过期,业务侧重新拉 sig 后再次 login
    console.warn('[TIM] userSig expired');
  },
  onSelfInfoUpdated: (info) => { /* 自己的资料卡有更新 */ },
});

// 2. 初始化 SDK
try {
  await V2TIMManager.initSDK(SDK_APP_ID, {
    logLevel: 4,                  // 0=DEBUG 1=INFO 4=WARN 5=ERROR 6=NONE
    initOptions: {
      // 自定义服务器地址(自有部署场景)
      // logFilePath: '...',
    },
  });
  console.info('[TIM] init done');
} catch (err) {
  const e = err as BusinessError;
  console.warn(`[TIM] init failed code=${e.code} msg=${e.message}`);
}

// 3. 登录
try {
  await V2TIMManager.login(USER_ID, USER_SIG);
  console.info('[TIM] login success');
} catch (err) {
  const e = err as BusinessError;
  console.warn(`[TIM] login failed code=${e.code} msg=${e.message}`);
}

// 4. 检查登录状态
const status = await V2TIMManager.getLoginStatus();
// V2TIM_STATUS_LOGINED / V2TIM_STATUS_LOGGING_IN / V2TIM_STATUS_LOGOUT

// 5. 获取当前 user
const userId = await V2TIMManager.getLoginUser();
```

### 2.2 发送消息

```ts
import { V2TIMManager, V2TIMOfflinePushInfo } from '@tencentcloud/imsdk';

// 文本消息
async function sendText(receiver: string, text: string) {
  try {
    const message = V2TIMManager.getMessageManager().createTextMessage(text);
    await V2TIMManager.getMessageManager().sendMessage(message, {
      receiver,                     // 单聊接收方 userId
      // groupID: 'GROUP_001',      // 群聊填这个,与 receiver 互斥
      priority: 1,                  // 0=普通 1=高 2=最高(影响 QoS)
    });
  } catch (err) {
    const e = err as BusinessError;
    console.warn(`[TIM] sendText failed code=${e.code} msg=${e.message}`);
  }
}

// 图片消息
async function sendImage(receiver: string, imagePath: string) {
  const message = V2TIMManager.getMessageManager().createImageMessage(imagePath);
  await V2TIMManager.getMessageManager().sendMessage(message, { receiver });
}

// 自定义消息(客服业务常用 —— 透传业务字段如订单卡片、问卷)
async function sendCustom(receiver: string, payload: object) {
  const data: string = JSON.stringify(payload);
  const message = V2TIMManager.getMessageManager().createCustomMessage(data, 'order_card', '');
  await V2TIMManager.getMessageManager().sendMessage(message, { receiver });
}

// 带离线推送的消息
async function sendWithPush(receiver: string, text: string) {
  const message = V2TIMManager.getMessageManager().createTextMessage(text);
  const pushInfo: V2TIMOfflinePushInfo = {
    title: '客服消息',
    desc: '您有新的客服回复',
    ext: JSON.stringify({ type: 'service_reply' }),    // 业务自定义透传
  };
  await V2TIMManager.getMessageManager().sendMessage(message, {
    receiver,
    offlinePushInfo: pushInfo,
  });
}
```

### 2.3 接收消息

```ts
V2TIMManager.getMessageManager().addAdvancedMsgListener({
  onRecvNewMessage: (message) => {
    console.info(`[TIM] recv from=${message.userID} type=${message.elemType}`);
    if (message.elemType === 1 /* V2TIM_ELEM_TYPE_TEXT */) {
      console.info(`[TIM] text=${message.textElem?.text}`);
    } else if (message.elemType === 2 /* V2TIM_ELEM_TYPE_CUSTOM */) {
      const payload = JSON.parse(message.customElem?.data ?? '{}');
      // 业务侧分发:订单卡片 / 问卷 / 文章
    }
    // 推荐: 通过项目自有事件总线 / 状态管理把消息分发到聊天 UI
    // EventBus.post('tim_new_message', { message });
  },
  onRecvMessageRevoked: (msgID) => { /* 消息被撤回 */ },
  onRecvMessageModified: (message) => { /* 消息被修改 */ },
  onRecvC2CReadReceipt: (receipts) => { /* 已读回执 */ },
  onRecvMessageReadReceipts: (receipts) => { /* 群消息已读回执 */ },
  onSendMessageProgress: (message, progress) => { /* 富媒体上传进度 0-100 */ },
});
```

### 2.4 会话列表

```ts
// 拉取会话列表(分页)
const result = await V2TIMManager.getConversationManager().getConversationList(
  '0',         // nextSeq:首次拉取传 '0',下一页用上次返回的 nextSeq
  100,         // count
);
// result.conversationList: V2TIMConversation[]
// result.nextSeq: string
// result.isFinished: boolean

// 监听会话变更(新消息进来 / 未读数变化 / 总未读数)
V2TIMManager.getConversationManager().addConversationListener({
  onNewConversation: (list) => { /* 有新会话产生 */ },
  onConversationChanged: (list) => { /* 会话信息变化(含未读数) */ },
  onTotalUnreadMessageCountChanged: (totalUnread) => {
    // 推荐: 广播到事件总线驱动红点 UI
    // EventBus.post('tim_unread', { total: totalUnread });
  },
});

// 主动获取总未读数
const total = await V2TIMManager.getConversationManager().getTotalUnreadMessageCount();
```

### 2.5 用户资料(客服场景必透)

```ts
// 设置自己的资料 —— 客服后台通过这些字段看用户卡片
await V2TIMManager.setSelfInfo({
  nickName: currentUser.nickName,
  faceURL: currentUser.avatar,
  selfSignature: '',
  gender: 1,
  birthday: 19900101,
  level: 0,
  role: 0,
  customInfo: {
    // 自定义字段,需要先在腾讯云 IM 控制台配置 schema(以 Tag_Profile_Custom_ 开头)
    'Tag_Profile_Custom_AppName': '<your-app-name>',
    'Tag_Profile_Custom_RegChannel': '<register-channel>',
    'Tag_Profile_Custom_VersionName': '<app-version>',
  },
});

// 获取他人资料
const profiles = await V2TIMManager.getUsersInfo([targetUserId]);
```

### 2.6 登出

```ts
try {
  await V2TIMManager.logout();
  console.info('[TIM] logout success');
} catch (err) {
  const e = err as BusinessError;
  console.warn(`[TIM] logout failed code=${e.code} msg=${e.message}`);
}

// 完全退出(不再使用 SDK)
await V2TIMManager.unInitSDK();
```

## 3. 配置项详解

腾讯云 IM 主要有四类配置入参:`initSDK` 配置 / `addIMSDKListener` 监听器 / `sendMessage` 选项 / `setSelfInfo` 资料字段。下表逐一列出。

### 3.1 `initSDK(sdkAppID, config)` 入参

```ts
await V2TIMManager.initSDK(SDK_APP_ID, {
  logLevel: 4,
  initOptions: {
    logFilePath: '/data/storage/.../tim-logs/',
  },
});
```

| 字段 | 类型 | 必填 | 默认 | 说明 |
|------|------|------|------|------|
| `sdkAppID`(第 1 参) | `number` | ✅ | — | 控制台 → 应用管理获取的 SDKAppID,**必须 number**,传 string 会校验失败 |
| `config.logLevel` | `number` | ❌ | `3` | 日志级别:`0=ALL` / `3=DEBUG` / `4=INFO` / `5=WARN` / `6=ERROR` / `7=NONE`,生产用 5+ |
| `config.initOptions.logFilePath` | `string` | ❌ | SDK 沙箱 | 自定义日志输出目录,排查问题时方便 hdc pull 日志 |
| `config.initOptions.disableLogPrint` | `boolean` | ❌ | `false` | 关闭控制台日志(只写文件) |

### 3.2 `V2TIMSDKListener`(全局监听器)

```ts
V2TIMManager.addIMSDKListener({
  onConnecting: () => {},
  onConnectSuccess: () => {},
  onConnectFailed: (code, error) => {},
  onKickedOffline: () => {},
  onUserSigExpired: () => {},
  onSelfInfoUpdated: (info) => {},
  onUserStatusChanged: (list) => {},
});
```

| 回调 | 触发时机 | 业务侧典型动作 |
|------|---------|----------------|
| `onConnecting` | 正在连接服务器 | 显示"连接中"指示 |
| `onConnectSuccess` | 连接成功 | 隐藏指示,可以发消息了 |
| `onConnectFailed(code, error)` | 连接失败 | 提示用户检查网络;`code` 是腾讯云错误码 |
| `onKickedOffline` | 账号在别处登录被踢 | 引导用户重新登录,**必须实现** |
| `onUserSigExpired` | UserSig 过期(默认 7 天)| 重新拉 sig 后再 login,**必须实现** |
| `onSelfInfoUpdated(info)` | 自己资料卡变化 | 刷新本地缓存的用户信息 |
| `onUserStatusChanged(list)` | 关注的用户在线状态变化 | 列表里更新 online/offline 标识 |

`addIMSDKListener` 可重复调用,所有 listener 都会被调用(不是覆盖),但**通常只注册一次**。

### 3.3 `sendMessage(message, options)` 选项

```ts
await V2TIMManager.getMessageManager().sendMessage(message, {
  receiver: 'target_user_id',
  groupID: '',
  priority: 1,
  onlineUserOnly: false,
  isExcludedFromUnreadCount: false,
  isExcludedFromLastMessage: false,
  needReadReceipt: false,
  offlinePushInfo: { /* V2TIMOfflinePushInfo */ },
  cloudCustomData: '',
  localCustomData: '',
});
```

| 字段 | 类型 | 默认 | 说明 |
|------|------|------|------|
| `receiver` | `string` | — | 单聊接收方 userId,**与 `groupID` 互斥** |
| `groupID` | `string` | — | 群聊 groupID,与 `receiver` 互斥 |
| `priority` | `number` | `0` | 消息优先级:`0=普通` / `1=高` / `2=最高`,影响 QoS,普通文本用 0 即可 |
| `onlineUserOnly` | `boolean` | `false` | 是否仅在线用户接收(类似透传消息);为 `true` 时不存历史 |
| `isExcludedFromUnreadCount` | `boolean` | `false` | 是否不计入未读数(系统提示常用) |
| `isExcludedFromLastMessage` | `boolean` | `false` | 是否不更新会话最后一条消息 |
| `needReadReceipt` | `boolean` | `false` | 是否需要群已读回执(单聊忽略) |
| `offlinePushInfo` | `V2TIMOfflinePushInfo` | — | 离线推送配置(见 3.4) |
| `cloudCustomData` | `string` | — | 云端存储的业务自定义透传字段(stringify JSON) |
| `localCustomData` | `string` | — | 仅本地存储的字段(不上传服务端,用于客户端临时标记) |

### 3.4 `V2TIMOfflinePushInfo`(离线推送配置)

```ts
const pushInfo: V2TIMOfflinePushInfo = {
  title: '客服消息',
  desc: '您有新的客服回复',
  ext: JSON.stringify({ type: 'reply', orderId: 'ORD-001' }),
  disablePush: false,
  ignoreIOSBadge: false,
  androidSound: '',
  iOSSound: 'system',
};
```

| 字段 | 类型 | 默认 | 说明 |
|------|------|------|------|
| `title` | `string` | App 名称 | 通知栏标题(≤ 50 字符) |
| `desc` | `string` | 消息内容预览 | 通知栏正文(≤ 200 字符) |
| `ext` | `string` | — | 业务自定义透传字段,**必须是 stringify 的 JSON 字符串**,接收端再 `JSON.parse` |
| `disablePush` | `boolean` | `false` | 单条消息禁用推送(临时不打扰) |
| `ignoreIOSBadge` | `boolean` | `false` | iOS 是否不修改角标 |
| `androidSound` | `string` | — | Android 自定义提示音资源名 |
| `iOSSound` | `string` | `'system'` | iOS 提示音 |

⚠ HarmonyOS 端推送行为还受 `@tencentcloud/timpush` 配置控制,见 §5。

### 3.5 `setSelfInfo(info)` 字段

```ts
await V2TIMManager.setSelfInfo({
  nickName: '',
  faceURL: '',
  selfSignature: '',
  gender: 0,
  birthday: 0,
  level: 0,
  role: 0,
  allowType: 0,
  customInfo: { /* 自定义字段 */ },
});
```

| 字段 | 类型 | 说明 |
|------|------|------|
| `nickName` | `string` | 昵称(≤ 32 字符) |
| `faceURL` | `string` | 头像 URL |
| `selfSignature` | `string` | 个性签名 |
| `gender` | `number` | `0=未知` / `1=男` / `2=女` |
| `birthday` | `number` | 生日,YYYYMMDD 格式数字(如 19900101) |
| `level` | `number` | 等级(业务自定义) |
| `role` | `number` | 角色(业务自定义) |
| `allowType` | `number` | 加好友验证方式:`0=同意所有` / `1=拒绝所有` / `2=需验证` |
| `customInfo` | `Record<string, string>` | 自定义字段 map,**key 必须以 `Tag_Profile_Custom_` 开头**,且需要先在控制台 → 应用配置 → 用户资料 schema 中声明 |

### 3.6 `V2TIMConversationListener` 回调

会话列表监听器全部回调,按需实现:

| 回调 | 触发时机 |
|------|---------|
| `onSyncServerStart` | 多端同步开始拉取会话(冷启动) |
| `onSyncServerFinish` | 多端同步完成 |
| `onSyncServerFailed` | 多端同步失败 |
| `onNewConversation(list)` | 有新会话产生 |
| `onConversationChanged(list)` | 会话信息变化(含未读数) |
| `onConversationDeleted(idList)` | 会话被删除 |
| `onTotalUnreadMessageCountChanged(total)` | 总未读数变化 |
| `onConversationGroupCreated(groupName)` | 会话分组创建 |
| `onConversationGroupDeleted(groupName)` | 会话分组删除 |

### 3.7 `V2TIMAdvancedMsgListener` 高级消息监听器

详见 §2.3,完整回调清单:`onRecvNewMessage` / `onRecvMessageRevoked` / `onRecvMessageModified` / `onRecvC2CReadReceipt` / `onRecvMessageReadReceipts` / `onSendMessageProgress` / `onRecvMessageExtensions(Changed|Deleted)`(消息扩展)。

### 3.8 `module.json5` 推送配置(用 `@tencentcloud/timpush` 时)

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
        "value": "<华为推送 Client ID>"
      }
    ]
  }
}
```

`client_id` 来自华为开发者平台 → 推送服务 → 应用配置;同时控制台 → IM 应用 → 推送配置 → 鸿蒙 上传服务账号凭证 JSON。

## 4. 推荐封装层模板

V2TIMManager 是顶层入口、子 Manager 散件 API 多,实战中建议在业务侧封装一个 Service 类,对外暴露 `init / login / logout / sendText / isReady / isLoggedIn` 等高层方法,把 SDK 内部事件订阅、错误处理逻辑藏起来:

```ts
// services/TencentImService.ets
import { V2TIMManager } from '@tencentcloud/imsdk';
import { common } from '@kit.AbilityKit';
import { BusinessError } from '@kit.BasicServicesKit';

export interface TimUserProfile {
  nickName?: string;
  avatar?: string;
  /** 自定义字段 key 必须以 Tag_Profile_Custom_ 开头(腾讯云 IM 控制台 schema 约定) */
  customInfo?: Record<string, string>;
}

export class TencentImService {
  private static initialized: boolean = false;
  private static loggedIn: boolean = false;

  static isReady(): boolean { return TencentImService.initialized; }
  static isLoggedIn(): boolean { return TencentImService.loggedIn; }

  static async init(_context: common.UIAbilityContext, sdkAppId: number): Promise<void> {
    if (TencentImService.initialized) return;
    try {
      // 全局事件
      V2TIMManager.addIMSDKListener({
        onConnecting: () => {},
        onConnectSuccess: () => console.info('[TIM] connected'),
        onConnectFailed: (code, err) => console.warn(`[TIM] conn failed code=${code} ${err}`),
        onKickedOffline: () => {
          TencentImService.loggedIn = false;
          // 推荐: 广播事件让业务侧引导用户重新登录
          // EventBus.post('tim_kicked_offline', {});
        },
        onUserSigExpired: () => {
          // 推荐: 广播事件让业务侧重新拉 sig 并重新 login
          // EventBus.post('tim_sig_expired', {});
        },
      });

      // 消息监听
      V2TIMManager.getMessageManager().addAdvancedMsgListener({
        onRecvNewMessage: (msg) => {
          // 推荐: EventBus.post('tim_new_message', { message: msg });
        },
        onRecvMessageRevoked: () => {},
        onRecvMessageModified: () => {},
        onRecvC2CReadReceipt: () => {},
        onRecvMessageReadReceipts: () => {},
        onSendMessageProgress: () => {},
      });

      // 总未读数
      V2TIMManager.getConversationManager().addConversationListener({
        onNewConversation: () => {},
        onConversationChanged: () => {},
        onTotalUnreadMessageCountChanged: (total) => {
          // 推荐: EventBus.post('tim_unread', { total });
        },
      });

      // 初始化
      await V2TIMManager.initSDK(sdkAppId, { logLevel: 4 });
      TencentImService.initialized = true;
    } catch (err) {
      const e = err as BusinessError;
      console.warn(`[TencentImService] init failed code=${e.code} msg=${e.message}`);
    }
  }

  static async login(userId: string, userSig: string, profile?: TimUserProfile): Promise<void> {
    if (!TencentImService.initialized) throw new Error('TIM not ready');
    try {
      await V2TIMManager.login(userId, userSig);
      TencentImService.loggedIn = true;
      if (profile !== undefined) {
        await V2TIMManager.setSelfInfo({
          nickName: profile.nickName,
          faceURL: profile.avatar,
          customInfo: profile.customInfo,
        });
      }
    } catch (err) {
      const e = err as BusinessError;
      console.warn(`[TencentImService] login failed code=${e.code} msg=${e.message}`);
      throw err;
    }
  }

  static async logout(): Promise<void> {
    if (!TencentImService.loggedIn) return;
    try {
      await V2TIMManager.logout();
      TencentImService.loggedIn = false;
    } catch (err) {
      const e = err as BusinessError;
      console.warn(`[TencentImService] logout failed code=${e.code} msg=${e.message}`);
    }
  }

  static async sendText(receiver: string, text: string): Promise<void> {
    const msg = V2TIMManager.getMessageManager().createTextMessage(text);
    await V2TIMManager.getMessageManager().sendMessage(msg, { receiver });
  }
}
```

EntryAbility 接入跟七鱼一样 fire-and-forget:

```ts
TencentImService.init(this.context).catch((err: Error): void => {
  hilog.warn(DOMAIN, 'tag', '[TIM] init failed: %{public}s', JSON.stringify(err));
});
```

## 5. 离线推送(`@tencentcloud/timpush`)

腾讯云 IM 把离线推送拆成单独包,鸿蒙端配置流程:

```bash
ohpm install @tencentcloud/timpush
```

```json5
// entry/oh-package.json5
{
  "dependencies": {
    "@tencentcloud/imsdk": "^7.7",
    "@tencentcloud/timpush": "^7.7"
  }
}
```

控制台配置:
1. 华为开发者平台为 bundleId 启用推送服务,创建服务账号凭证
2. 上传到腾讯云 IM 控制台 → 应用 → 推送配置 → 鸿蒙
3. ArkTS 侧调用 `TIMPush.registerPush(appId, certificateID)` 完成注册

发送消息时通过 `V2TIMOfflinePushInfo` 控制单条消息的推送行为(见 3.2 sendWithPush 示例)。

## 6. 跨端 API 一致性

腾讯云 IM 是市面上跨端心智一致性**最好**的 IM SDK,从 Android 项目迁移 ArkTS 几乎是 1:1:

| Android Java | ArkTS | 备注 |
|--------------|-------|------|
| `V2TIMManager.getInstance().initSDK(ctx, appId, config, listener)` | `V2TIMManager.initSDK(appId, config)` + `addIMSDKListener(listener)` | listener 拆出 |
| `V2TIMManager.getInstance().login(uid, sig, callback)` | `await V2TIMManager.login(uid, sig)` | Promise |
| `V2TIMManager.getInstance().logout(callback)` | `await V2TIMManager.logout()` | Promise |
| `V2TIMManager.getMessageManager().sendMessage(msg, ..., callback)` | `await V2TIMManager.getMessageManager().sendMessage(msg, opts)` | Promise + 选项对象 |
| `V2TIMManager.getMessageManager().addAdvancedMsgListener(l)` | 同名 | 同 |
| `V2TIMManager.getConversationManager().getConversationList(seq, count, cb)` | `await ...getConversationList(seq, count)` | Promise |
| `V2TIMManager.setSelfInfo(info, callback)` | `await V2TIMManager.setSelfInfo(info)` | Promise |

迁移成本:Android 已有 V2TIM 接入的项目,可以**按方法名机械替换**,把 `V2TIMCallback / V2TIMValueCallback<T>` 换成 `await + try/catch`。

## 7. 常见踩坑

### 7.1 SDKAppID 是 number 不是 string

```ts
const SDK_APP_ID = 1400000000;        // ✅ number
const SDK_APP_ID = '1400000000';      // ❌ initSDK 类型校验失败
```

### 7.2 UserSig 必须由后端签发,不要硬编码

UserSig 用 `SDKAppID + UserID + Secret + 过期时间` 在**服务端**签出来。客户端硬编码 Secret 会泄漏 → 任何人都能签出全员的 sig 进而冒充用户。推荐流程:

```ts
// 拉 UserSig 的接口由业务后端实现并暴露给客户端
const sig = await getImUserSigFromBackend();    // 例如: GET /im/usersig
await TencentImService.login(currentUser.id, sig, profile);
```

### 7.3 onUserSigExpired 必须实现

UserSig 默认 7 天过期,过期后 `sendMessage` 等所有调用都会失败。必须在 `addIMSDKListener.onUserSigExpired` 里**主动重新拉 sig 然后重新 login**:

```ts
onUserSigExpired: async () => {
  try {
    const newSig = await getImUserSigFromBackend();
    await V2TIMManager.login(currentUserId, newSig);
  } catch (e) {
    // 业务侧引导用户重新登录
  }
},
```

### 7.4 离线推送 ext 字段是 string 不是 object

```ts
const info: V2TIMOfflinePushInfo = {
  title: '客服消息',
  desc: '您有新的客服回复',
  ext: JSON.stringify({ type: 'reply' }),    // ✅ stringify
  // ext: { type: 'reply' },                  // ❌ 类型校验失败
};
```

接收端解析时再 `JSON.parse`。

### 7.5 customMessage 的 description 字段

```ts
createCustomMessage(data: string, description: string, extension: string)
```

`description` 不是 UI 显示文案,而是**离线推送预览文本**(用户没打开 App 时通知栏看到的内容)。客户端显示要在 `onRecvNewMessage` 里自己根据 `data` 解析渲染。

### 7.6 sendMessage 的 receiver 与 groupID 互斥

单聊填 `receiver`,群聊填 `groupID`,两个都填或都不填会报参数错误。封装层最好分两个方法:`sendC2C(userId, msg)` / `sendGroup(groupId, msg)`。

## 8. 关键文档链接

- HarmonyOS 集成文档:https://cloud.tencent.com/document/product/269/103558
- HarmonyOS 初始化登录 API:https://cloud.tencent.com/document/product/269/103559
- TIMSDK GitHub(明确支持 HarmonyOS):https://github.com/TencentCloud/TIMSDK
- V2TIMManager API 索引:https://im.sdk.qcloud.com/doc/zh-cn/interfaceV2TIMManager.html
- 离线推送配置:https://cloud.tencent.com/document/product/269/108823
- 控制台:https://console.cloud.tencent.com/im
