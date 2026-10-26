# 网易七鱼 `@ysf/sdk` 客服 SDK 接入指南

> 资料来源:网易七鱼鸿蒙端访客 SDK 官方包(ohpm: `@ysf/sdk`)、Android 端 `com.qiyukf.unicorn.api` 对照、社区实战经验。
> SDK 版本:≥ `1.0.10` 才支持 `setAvoidArea`,推荐用 `1.1.5+`。

## 1. 安装

```json5
// entry/oh-package.json5
{
  "dependencies": {
    "@ysf/sdk": "^1.0.10"   // ≥ 1.0.10 才支持 setAvoidArea
  }
}
```

无新增权限 —— 全部走 `INTERNET / GET_NETWORK_INFO`,onClickUrl 拉浏览器 / 拨号盘走系统 want action(dial / browsable)免权限。

## 2. 核心 API(HOS ↔ Android Unicorn 对齐)

| Android `com.qiyukf.unicorn.api` | HOS `@ysf/sdk` | 备注 |
|----------------------------------|----------------|------|
| `Unicorn.initSdk()` | `await initYsf()` | HOS 必须 await |
| `config(...).appKey = ...` | `configAppKey(key)` | 单独 setter |
| —(manifest 写死) | `configBundleId(name)` | HOS 端必须显式设置 |
| `ConsultSource.groupTmpId = <gid>` | `configGroupId(groupId)` | 全局默认 |
| `config(...).copyText` | `configAutoCopy(1)` | 链接复制行为 |
| `setUserInfo(YSFUserInfo, RequestCallback)` | `setUserInfo({userId, data[]})` | **HOS 同步无回调** |
| `ConsultSource(sourceUrl, sourceTitle, custom)` | `setCustomConfig({fromTitle, referrer, ...})` | 拆成独立 setter |
| `openServiceActivity(ctx, title, source)` | `open(uiContext)` | 入参是 `getUIContext()` |
| `addUnreadCountChangeListener(l, true)` | `onUnread((res) => ...)` | 单回调,反复调覆盖 |
| `setOnClickUrlListener` | `onClickUrl((res) => ...)` | 同上 |
| `Unicorn.logout()` | `logout()` | 同名同语义 |
| —(Android 用沉浸式适配) | `setAvoidArea({top, bottom})` | HOS 独有 |

## 3. 推荐封装层模板

七鱼 SDK 散件 API 多,实战中建议在业务侧封装一个 Service 类,对外暴露 `init / openChat / logout / isReady` 四个方法,内部把所有 SDK 细节藏起来。

```ts
// services/QiyuService.ets
import { initYsf, configAppKey, configBundleId, configGroupId, configAutoCopy,
         setAvoidArea, open, setUserInfo, setCustomConfig, logout as ysfLogout,
         onUnread, onClickUrl } from '@ysf/sdk';
import { common, Want } from '@kit.AbilityKit';
import { BusinessError } from '@kit.BasicServicesKit';
import { window } from '@kit.ArkUI';

interface YsfDataItem {
  key: string;
  value: string;
  label?: string;
  hidden?: boolean;
  isCustomField?: boolean;
}

export interface OpenChatOptions {
  /** 当前登录用户 id;空字符串 / undefined 视同游客 */
  userId?: string;
  /** 用户资料(将装配进 YSFUserInfo.data,显示在客服后台) */
  userData?: YsfDataItem[];
  /** 联系电话(常用于反馈表单透传) */
  phone?: string;
  /** 退款 / 咨询原因(常用于反馈表单透传) */
  reason?: string;
  /** 指定客服组,未传走 init 时配置的默认组 */
  serviceGroup?: number;
  /** 来源标题(对齐 Android ConsultSource.sourceTitle) */
  fromTitle?: string;
  /** 来源 URL(对齐 Android ConsultSource.sourceUrl) */
  referrer?: string;
}

export class QiyuService {
  private static initialized: boolean = false;
  private static abilityContext: common.UIAbilityContext | undefined = undefined;
  private static defaultGroupId: number = 0;

  static isReady(): boolean { return QiyuService.initialized; }

  /** 全局初始化。幂等 —— EntryAbility.onCreate 调一次即可。*/
  static async init(
    context: common.UIAbilityContext,
    config: { appKey: string; bundleId: string; defaultGroupId: number },
  ): Promise<void> {
    if (QiyuService.initialized) return;
    QiyuService.abilityContext = context;
    QiyuService.defaultGroupId = config.defaultGroupId;
    try {
      await initYsf();
      configAppKey(config.appKey);
      configBundleId(config.bundleId);
      configGroupId(config.defaultGroupId);
      configAutoCopy(1);
      QiyuService.applyAvoidAreaFromWindow(context);

      onUnread((res: Record<string, Object>): void => {
        const total: number = typeof res.total === 'number' ? (res.total as number) : 0;
        // 业务侧可在此广播事件,驱动红点显示
        console.info(`[QiyuService] onUnread total=${total}`);
      });

      onClickUrl((res: Record<string, string>): void => {
        const raw: string = (res && res.url) ? res.url : '';
        if (raw.length === 0) return;
        if (raw.startsWith('tel:')) QiyuService.startDialer(raw);
        else QiyuService.startBrowsable(raw);
      });

      QiyuService.initialized = true;
    } catch (e) {
      console.warn(`[QiyuService] init failed: ${JSON.stringify(e)}`);
    }
  }

  /** 拉起聊天页 */
  static openChat(uiContext: UIContext, opts?: OpenChatOptions): void {
    if (!QiyuService.initialized) return;
    try {
      // 1) 注入用户资料(空 userId 视同游客,跳过)
      if (opts?.userId !== undefined && opts.userId.length > 0 && opts.userData !== undefined) {
        setUserInfo({ userId: opts.userId, data: opts.userData });
      }
      // 2) 来源页 + 标题栏样式
      setCustomConfig({
        fromTitle: opts?.fromTitle ?? '联系客服',
        referrer: opts?.referrer ?? '',
        navigationBarTitleText: '在线客服',
        navigationBarBackgroundColor: '#FFFFFF',
        navigationBarTextStyle: 'black',
      });
      // 3) 客服组(只在与默认组不同时才覆盖,避免重复调用)
      const groupId: number | undefined = opts?.serviceGroup;
      if (groupId !== undefined && groupId !== QiyuService.defaultGroupId) {
        configGroupId(groupId);
      }
      // 4) 拉起
      open(uiContext);
    } catch (e) {
      console.warn(`[QiyuService] openChat failed: ${JSON.stringify(e)}`);
    }
  }

  /** 清七鱼本地会话 / 用户绑定 */
  static logout(): void {
    if (!QiyuService.initialized) return;
    try {
      ysfLogout();
    } catch (e) {
      console.warn(`[QiyuService] logout failed: ${JSON.stringify(e)}`);
    }
  }

  // 私有方法 setAvoidArea / startBrowsable / startDialer 见下文章节
}
```

## 4. YSFUserInfo 字段约定

七鱼 SDK 把传给客服后台的用户资料拆成"系统字段 + 自定义字段"两类,用 `YsfDataItem[]` 表达:

| 类别 | 必填字段 | 字段定式 |
|------|---------|---------|
| 系统字段(SDK 识别) | `real_name`、`mobile_phone`、`avatar`、`email`、`sex`、`age`、`vip_level` 等 | `{ key, value, hidden? }`,**不带** `label` 和 `isCustomField` |
| 自定义字段(后台展示) | 任意 key,如 `APP名称`、`用户id`、`注册时间`、`版本号`、`归因渠道`、`联系电话`等 | `{ key, value, label, isCustomField: true }` |

**典型映射示例**(参考 Android `ContactServiceExt.getUserData` 11 字段拼装顺序):

```ts
function buildUserData(user: { id: string; nickName: string; mobile: string; avatar: string;
                              regShowDate: string; },
                      meta: { appName: string; versionName: string; channel: string;
                              memberStartTime?: string; },
                      phone: string, reason: string): YsfDataItem[] {
  return [
    // 系统字段
    { key: 'real_name', value: user.nickName },
    { key: 'mobile_phone', value: user.mobile, hidden: false },
    { key: 'avatar', value: user.avatar },
    // 自定义字段
    { key: 'APP名称',     label: 'APP名称',     value: meta.appName,                  isCustomField: true },
    { key: '用户id',      label: '用户id',      value: user.id,                       isCustomField: true },
    { key: '注册时间',    label: '注册时间',    value: user.regShowDate,              isCustomField: true },
    { key: '会员开始时间', label: '会员开始时间', value: meta.memberStartTime ?? '',    isCustomField: true },
    { key: '版本号',      label: '版本号',      value: meta.versionName,              isCustomField: true },
    { key: '归因渠道',    label: '归因渠道',    value: meta.channel,                  isCustomField: true },
    { key: '退款原因',    label: '退款原因',    value: reason,                        isCustomField: true },
    { key: '联系电话',    label: '联系电话',    value: phone,                         isCustomField: true },
  ];
}
```

**关键差异**:HOS 用 `YsfDataItem[]` 强类型数组,SDK 内部序列化;Android 是手拼 JSON 字符串。差异不影响 SDK 接收。

**注意:`hidden:false` 的语义**:对于敏感字段如 `mobile_phone`,显式声明 `hidden: false` 表示让客服后台可见(不显式声明时 SDK 行为可能与控制台默认配置相关,显式更稳)。

## 5. 业务接入点

### 5.1 入口按钮(常见场景:个人中心 / 帮助页"联系客服"按钮)

```ts
private onContactServiceClick(): void {
  if (QiyuService.isReady()) {
    QiyuService.openChat(this.getUIContext(), {
      userId: this.userInfo?.id,
      userData: buildUserData(this.userInfo, AppMeta, '', ''),
    });
  } else {
    // 降级 fallback:跳转本地 echo 壳页面 / 或 H5 客服页
    router.pushUrl({ url: 'pages/LocalChatFallback' });
  }
}
```

### 5.2 反馈表单提交后转客服

业务场景:用户在反馈页填写联系电话和退款原因,提交后跳转到客服会话延续:

```ts
private onSubmitFeedbackSuccess(bean: { userMobile?: string; refundReason?: string; gid?: string }): void {
  // gid:可能是 string,转 number,NaN 时降级到默认组
  let groupId: number | undefined = undefined;
  if (bean.gid !== undefined && bean.gid.length > 0) {
    const parsed = parseInt(bean.gid, 10);
    if (!Number.isNaN(parsed)) groupId = parsed;
  }
  QiyuService.openChat(this.getUIContext(), {
    userId: this.currentUser?.id,
    userData: buildUserData(this.currentUser, AppMeta, bean.userMobile ?? '', bean.refundReason ?? ''),
    phone: bean.userMobile ?? '',
    reason: bean.refundReason ?? '',
    serviceGroup: groupId,
  });
  router.back();
}
```

### 5.3 登出联动

```ts
// 用户登出的统一入口里调
QiyuService.logout();
```

避免登出后下次 `openChat` 仍以旧身份建会话。

## 6. 标题栏视觉对齐(盲传字段)

```ts
setCustomConfig({
  fromTitle: '联系客服',
  referrer: '',
  navigationBarTitleText: '在线客服',
  navigationBarBackgroundColor: '#FFFFFF',
  navigationBarTextStyle: 'black',  // 'black' | 'white'
});
```

`navigationBar*` 三字段是 Taro PageMeta 标准命名,**未在 SDK 1.1.5 的 `Index.d.ets` 公开签名**,但 SDK 二进制内有引用 —— 属于盲传:

- SDK 接住 → 标题文字 / 背景 / 文字色与项目自有 TitleBar 视觉对齐
- SDK 不接住 → 字段被忽略,零副作用

字号 / 字重 / 返回箭头资源仍由 SDK 自渲染,无法严格统一。完全统一需要"自包 NavDestination + QiyuPage Component"路线,需评估 SDK 是否提供嵌入容器 API。

## 7. onClickUrl 路由(聊天内链接处理)

```ts
private static startBrowsable(url: string): void {
  const ctx = QiyuService.abilityContext;
  if (!ctx) return;
  const want: Want = {
    action: 'ohos.want.action.viewData',
    entities: ['entity.system.browsable'],
    uri: url,
  };
  ctx.startAbility(want).catch((err: BusinessError): void => {
    console.warn(`[QiyuService] browsable failed code=${err.code}`);
  });
}

private static startDialer(telUri: string): void {
  const ctx = QiyuService.abilityContext;
  if (!ctx) return;
  // 用 dial 不用 call.makeCall —— 免 ohos.permission.PLACE_CALL 敏感权限,
  // 仅打开拨号盘由用户手动按键,无权限要求。
  const want: Want = { action: 'ohos.want.action.dial', uri: telUri };
  ctx.startAbility(want).catch((err: BusinessError): void => {
    console.warn(`[QiyuService] dial failed code=${err.code}`);
  });
}
```

`abilityContext` 在 `init` 时缓存,给 `startAbility` 用。

## 8. 未读消息事件

```ts
onUnread((res: Record<string, Object>): void => {
  const total: number = typeof res.total === 'number' ? (res.total as number) : 0;
  // 推荐:广播全局事件,由订阅方(如导航 Tab、个人中心入口)展示红点
  // EventBus.post('qiyu_unread', { total });
  console.info(`[QiyuService] unread total=${total}`);
});
```

回调是**单例覆盖**式 —— 多次调用 `onUnread` 后只有最后一次生效,所以建议在 `init` 里只注册一次,业务侧通过事件总线消费。

## 9. 常见踩坑

### 9.1 Bundle ID 必须运营侧绑定

七鱼控制台 → 在线系统 → App → **必须为 HOS 应用的 bundleName 单独绑定 HOS App**。未绑定时 init 不报错但消息无法下发,用户表现为"打开聊天页但收不到接待"。

不要伪装为 Android 老包名复用现有白名单 —— 与后端 header `package` 字段会冲突,且违反七鱼侧的统计/路由规则,应该在控制台单独绑定鸿蒙 bundleName。

### 9.2 init 不要 await

`EntryAbility.onCreate` 内 fire-and-forget:

```ts
QiyuService.init(this.context, { appKey, bundleId, defaultGroupId }).catch((err: Error): void => {
  hilog.warn(DOMAIN, 'tag', '[Qiyu] init failed: %{public}s', JSON.stringify(err));
});
```

`initYsf` 内部可能 hang(网络握手 / 包名校验),await 拖慢 onCreate 影响首屏。失败时 `isReady() = false`,业务降级到本地 echo 壳。

### 9.3 setUserInfo 同步无回调

HOS SDK `setUserInfo` 不像 Android 有 `RequestCallback`,**失败处理只能靠外层 try-catch**。建议策略:try-catch warn 不抛,让 openChat 继续走(即使资料没透成功,也好过按钮哑)。

### 9.4 群组 ID 重设要做差异判断

```ts
// openChat 内
if (groupId !== undefined && groupId !== defaultGroupId) {
  configGroupId(groupId);
}
```

否则每次 openChat 都重新调 `configGroupId`,SDK 内部可能有不必要的状态重建。

### 9.5 H5 反馈页 gid 类型转换

H5 里的 `gid` 通常是 string,而 `OpenChatOptions.serviceGroup` 是 number,需要安全转换:

```ts
let groupId: number | undefined = undefined;
if (bean.gid && bean.gid.length > 0) {
  const parsed = parseInt(bean.gid, 10);
  if (!Number.isNaN(parsed)) groupId = parsed;
}
```

NaN 时降级到默认组,而不是直接传 NaN 给 SDK。

### 9.6 字号 / 字重 SDK 自渲染无法统一

`navigationBar*` 三字段只能控制文字内容、背景色、文字色,**字号 / 字重 / 返回箭头资源**由 SDK 自渲染,与项目 TitleBar 视觉无法严格统一。如果设计师强烈要求像素级一致,只能走"自包 NavDestination + QiyuPage Component"方案,但 SDK 是否提供嵌入容器 API 需向七鱼商务确认。

## 10. 真机回归清单

落地后必须在真机上验证:

- [ ] 冷启动 `[QiyuService] init done` 日志可见
- [ ] 客服入口按钮可拉起聊天页(未登录态 / 已登录态都跑一次)
- [ ] 聊天页顶部留白合理(`safeArea + TOP_EXTRA_PADDING_VP`)
- [ ] 聊天页底部不被手势条压住(`bottom = NAVIGATION_INDICATOR inset`)
- [ ] YSFUserInfo 字段在客服后台能看到(重点系统字段 + 自定义字段)
- [ ] 客服主动发消息 → `onUnread` 回调触发
- [ ] 聊天内 `tel:` 链接 → 拉拨号盘(不弹权限)
- [ ] 聊天内 `https:` 链接 → 拉浏览器
- [ ] 登出后再次 openChat 走匿名通道(不带 userId)
- [ ] H5 反馈页提交 → openChat(带 phone/reason/gid)→ 反馈页关闭
- [ ] bundleId 绑定生效(让运营在控制台收到 HOS 客户端发起的会话)

## 11. 跟运营 / 后端的常见约定

| 项 | 责任方 | 说明 |
|---|------|----------|
| 七鱼控制台为 HOS bundleName 绑定 App | 运营 | 未绑定聊天页能开但收不到接待 |
| 客服组(groupId) HOS / Android 是否单独路由 | 运营决策 | 不单独路由时同队列,工单标签可借自定义字段区分 |
| 鸿蒙推送证书上传 | 运营 + 后端 | 离线推送依赖 |
| 用户 `memberStartTime` 等扩展字段 | 后端 | 业务模型里需要保留对应字段才能透给 SDK |
