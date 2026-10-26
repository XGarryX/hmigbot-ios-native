# GroMore 聚合广告 (字节跳动)

**官方索引页：** https://www.csjplatform.com/union/media/union/download/detail?id=206&osType=harmony
**最后核对：** 2026-05
**警示：** 如离最后核对超过 6 个月，先访问官方索引页核对版本与 API 是否变更。

> GroMore 是字节跳动的聚合广告平台。鸿蒙端 SDK 与 CSJ 主 SDK（@csj/openadsdk）共用一个 HAR；接入第三方广告源（GDT / KS / 百度等）需要对应的 adapter HAR。

---

## 1. 下载与安装

需要 1 个主 SDK + 每个接入第三方源对应的 1 个 adapter HAR：

- 主 SDK：`@csj/openadsdk` (file:libs/openadsdk-X.Y.Z.har) — 与 sdk-csj.md §1 同
- adapter HAR（按需引入接入的第三方源）：
  - `@csj/adapter_gdt` — 优量汇 adapter（详见 sdk-gdt.md §1）
  - `@csj/adapter_ks` — 快手 adapter（详见 sdk-ks.md §1）
  - 其它（百度等）的 adapter 状态待官方索引页核对

entry/oh-package.json5 引用片段（典型 3 家聚合）：

```json5
"dependencies": {
  "@csj/openadsdk": "file:libs/openadsdk-X.Y.Z.har",
  "@csj/adapter_gdt": "file:libs/adapter_gdt-X.Y.Z.har",
  "@csj/adapter_ks": "file:libs/adapter_ks-X.Y.Z.har",
  "@gdt/gdt-union-sdk": "file:libs/gdt-union-sdk-X.Y.Z.har",
  "ksadsdk": "file:libs/KSAdSDK-X.Y.Z.har"
}
```

根目录 oh-package.json5 overrides（关键，必须重定向所有第三方源到本地 HAR）：

```json5
"overrides": {
  "@csj/openadsdk": "file:entry/libs/openadsdk-X.Y.Z.har",
  "@gdt/gdt-union-sdk": "file:entry/libs/gdt-union-sdk-X.Y.Z.har",
  "ksadsdk": "file:entry/libs/KSAdSDK-X.Y.Z.har"
}
```

⚠️ 漏写 overrides 是 GroMore 集成最常见的失败模式：adapter HAR 内部声明远端版本，ohpm 优先解析远端导致版本不匹配。

## 2. module.json5 权限表

聚合广告权限 = 主 SDK 权限 + 各 adapter 权限的并集。

| 权限 | 作用 | 是否必需 | 默认推荐 | 隐私影响 | 来源 |
|---|---|---|---|---|---|
| `ohos.permission.INTERNET` | 广告请求 | ✅ 必需 | ✅ 加 | 无 | CSJ + 全部 adapter |
| `ohos.permission.GET_NETWORK_INFO` | 网络类型识别 | ⚠️ 推荐 | ✅ 加 | 低 | CSJ + 全部 adapter |
| `ohos.permission.LOCATION` | LBS 定向 | ❌ 可选 | ❌ 不加 | 高 | 各家可选 |
| `ohos.permission.READ_DEVICE_ID`（OAID）| 设备标识 | ❌ 可选 | ⚠️ 看商务要求 | 高 | 各家可选 |

## 3. Application 初始化

GroMore 入口走 CSJ 主 SDK；各 adapter 通常无独立 init（由 CSJ 在加载具体广告时按 wateifall 自动调用）。

### Android (Kotlin) before
```kotlin
TTAdSdk.init(context, TTAdConfig.Builder()
    .appId(BuildConfig.GROMORE_APP_ID)   // 注意：GroMore App ID 与单源 CSJ 不同
    .appName(getString(R.string.app_name))
    .useTextureView(true)
    .titleBarTheme(TTAdConstant.TITLE_BAR_THEME_DARK)
    .build())

TTAdSdk.start(object : TTAdSdk.Callback {
    override fun success() { /* GroMore 启动成功 */ }
    override fun fail(code: Int, msg: String?) { /* 降级 */ }
})
```

### HarmonyOS ArkTS (EntryAbility.onCreate) after
```typescript
import { CSJAdSdk } from '@csj/openadsdk';

class AdService {
  async init(context: Context): Promise<void> {
    if (!privacyService.isAccepted()) return;
    CSJAdSdk.init(context, {
      appId: AdConfig.GROMORE_HARMONY_APP_ID,   // 鸿蒙端 GroMore App ID
      appName: AdConfig.APP_NAME
    });
    await this.start();
  }
}
```

> 实际类名 / 方法签名以官方 HAR 为准。

## 4. WindowStage 绑定

需 windowStage 的广告类型与各 adapter 一致：插屏 / 激励视频 / 全屏。绑定方式与 sdk-csj.md §4 同。

## 5. 关键 API 1:1 对照表

GroMore 的 load/show API 与 CSJ 主 SDK **同接口**，区别在 slotId 是 GroMore 后台配置的"聚合广告位 ID"，由 SDK 内部按 waterfall / bidding 决定实际请求哪个第三方源。

| 广告类型 | Android API | HarmonyOS API | 备注 |
|---|---|---|---|
| 开屏 | `loadSplashAd(slot, listener, timeout)` | `loadSplashAd(slot, listener, timeout)` | slotId = GroMore 聚合位 ID |
| 插屏/全屏 | `loadFullScreenVideoAd(slot, listener)` | `loadFullScreenVideoAd(slot, listener)` | slotId = GroMore 聚合位 ID |
| 激励视频 | `loadRewardVideoAd(slot, listener)` | `loadRewardVideoAd(slot, listener)` | 奖励在 `onRewardVerify` |
| 信息流 | `loadFeedAd(slot, listener)` | `loadFeedAd(slot, listener)` | UI 走 ArkTS 自定义渲染 |
| Banner | `loadBannerExpressAd(slot, listener)` | `loadBannerExpressAd(slot, listener)` | 失败折叠 |

> ⚠️ HarmonyOS API 类名以官方 HAR 实际导出为准。

## 6. 完整 before/after：开屏广告

代码与 sdk-csj.md §6 一致（GroMore 与 CSJ 共用主 SDK API），唯一差异是 `slotId` 取自 AdConfig.GROMORE_HARMONY_SPLASH_SLOT_ID（GroMore 聚合位 ID 而非单源 CSJ 位 ID）。

参考 `sdk-csj.md` §6。

## 7. 已知陷阱

- **overrides 必须覆盖所有第三方源 HAR**（GDT / KS / 百度等），否则 ohpm 解析远端版本失败 — 这是 GroMore 最常见失败模式
- adapter HAR 版本必须与主 SDK 版本配对（不同主 SDK 版本对应不同 adapter 版本）
- 复用单源 SDK 的 App ID 不可用：GroMore 后台为聚合场景单独签发 App ID
- 单源 slotId 不可用：必须在 GroMore 后台创建"聚合广告位"得到聚合 slotId
- 如某个第三方源（如 GDT）adapter 缺失，对应 waterfall 节点会跳过；不影响其它源
- waterfall 顺序由 GroMore 后台配置决定，本地代码不可控
- 失败回调可能是聚合层失败也可能是底层源失败；排障时看 SDK 日志中的 wateifall 路径
- WindowStage 绑定前调 show 与单源 CSJ 一致（违反报错）
