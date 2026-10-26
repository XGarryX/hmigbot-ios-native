# 华为 HMS Ads (鸿蒙 AdsKit)

**官方索引页：** https://developer.huawei.com/consumer/cn/doc/harmonyos-references/js-apis-ads
**最后核对：** 2026-05
**警示：** 如离最后核对超过 6 个月，先访问官方索引页核对 API 是否变更。HMS Ads 在鸿蒙 NEXT 上为**系统能力**（@kit.AdsKit），无需 HAR。

---

## 1. 下载与安装

HMS Ads 在鸿蒙 NEXT 上以系统能力（Kit）形式提供，**无需下载 HAR**。

- 在 ArkTS 文件中直接 import：
  ```typescript
  import { advertising } from '@kit.AdsKit';
  ```
- entry/oh-package.json5 **不需要**增加任何 dependency 项
- 根 oh-package.json5 **不需要** overrides

## 2. module.json5 权限表

| 权限 | 作用 | 是否必需 | 默认推荐 | 隐私影响 |
|---|---|---|---|---|
| `ohos.permission.INTERNET` | 广告请求 + 物料下载 | ✅ 必需 | ✅ 加 | 无 |
| `ohos.permission.GET_NETWORK_INFO` | 区分网络类型 | ⚠️ 推荐 | ✅ 加 | 低 |
| `ohos.permission.APP_TRACKING_CONSENT` | 广告跟踪授权（OAID 等价）| ❌ 可选 | ⚠️ 看隐私合规 | 高 — 必须用户同意后申请 |
| `ohos.permission.LOCATION` | LBS 定向广告 | ❌ 可选 | ❌ 不加 | 高 — 需用户授权 + 写 reason |

> 详细权限以官方 AdsKit 文档为准。

## 3. Application 初始化

HMS Ads 作为系统能力，通常**无需显式 init**（与 CSJ/KS 不同）。某些 API 调用前可能需要登记 App ID 或 placement ID。

### Android (Kotlin) before
```kotlin
HwAds.init(context)
HwAds.setRequestOptions(RequestOptions.Builder()
    .setAdContentClassification(AdContentClassification.AD_CONTENT_CLASSIFICATION_PI)
    .build())
```

### HarmonyOS ArkTS (EntryAbility.onCreate) after
```typescript
import { advertising } from '@kit.AdsKit';

class AdService {
  async init(context: Context): Promise<void> {
    if (!privacyService.isAccepted()) return;
    // HMS AdsKit 通常无需显式 init；具体见官方文档
    // 如需要全局配置（如非个性化广告标志），在此调相应 API
  }
}
```

> 具体 init / 配置 API 以 @kit.AdsKit 文档为准；某些版本可能完全无需 init。

## 4. WindowStage 绑定

鸿蒙原生 AdsKit 部分 API（特别是全屏 / 插屏 / 激励视频）需要 windowStage 或 UIContext。

```typescript
class AdService {
  bindWindowStage(stage: window.WindowStage): void {
    this.windowStage = stage;
  }
}
```

## 5. 关键 API 1:1 对照表

| 广告类型 | Android API（HwAds）| HarmonyOS API（@kit.AdsKit） | 备注 |
|---|---|---|---|
| 开屏 | `SplashAd.preloadAd(...)` → `SplashAd.show(activity)` | `advertising.loadAd(adRequest, listener)` → splash 类型 | 类型由 adRequest 中的 `adType` 字段指定 |
| 插屏 | `InterstitialAd(context, slot)` → `loadAd()` → `show(activity)` | `advertising.loadAd(...)` → interstitial 类型 → `advertising.showAd(ad, displayOptions)` | activity → windowStage / UIContext |
| 激励视频 | `RewardAd(context, slot)` → `loadAd()` → `show(activity, statusListener)` | `advertising.loadAd(...)` → rewarded 类型 → `advertising.showAd(ad, displayOptions)` | 奖励发放逻辑以官方文档为准 |
| 信息流 | `NativeAdLoader(context, slot, ...)` → `loadAd(adParam, listener)` | `advertising.loadAd(...)` → native 类型 | UI 走 ArkTS 自定义渲染 |
| Banner | `BannerView(context, ...)` | `advertising.loadAd(...)` → banner 类型 | 失败折叠 |

> ⚠️ HarmonyOS API 以 `@kit.AdsKit` 实际导出为准；上表基于公开文档关键 API 名整理，请以官方文档为准。

## 6. 完整 before/after：开屏广告

### Android Kotlin
```kotlin
class SplashActivity : AppCompatActivity() {
  override fun onCreate(b: Bundle?) {
    super.onCreate(b)
    val container = findViewById<FrameLayout>(R.id.splash_container)
    val splashAd = SplashAd(this)
    splashAd.adId = BuildConfig.HMS_SPLASH_SLOT_ID
    splashAd.adListener = object : AdListener() {
      override fun onAdLoaded() { /* show */ }
      override fun onAdFailed(code: Int) { goMain() }
      override fun onAdDismissed() { goMain() }
    }
    splashAd.loadAd(AdParam.Builder().build())
  }
}
```

### HarmonyOS ArkTS
```typescript
// services/AdService.ets — 增加 loadHmsSplash 方法
import { advertising } from '@kit.AdsKit';

class AdService {
  async loadHmsSplash(slotId: string, container: StackLike): Promise<SplashResult> {
    if (!privacyService.isAccepted()) return { ok: false, reason: 'privacy' };
    return new Promise((resolve) => {
      const adRequest: advertising.AdRequestParams = {
        adId: slotId,
        adType: advertising.AdType.SPLASH
      };
      advertising.loadAd(adRequest, {
        onAdLoad: (ads: advertising.Advertisement[]) => {
          // 渲染广告物料
          // ...
          resolve({ ok: true });
        },
        onAdFail: (code, msg) => resolve({ ok: false, reason: `load_err:${code}` })
      });
    });
  }
}
```

> ⚠️ 上述 API 名（`advertising.loadAd` / `AdRequestParams` / `AdType.SPLASH`）基于公开 AdsKit 文档结构整理，实际类型与方法签名请以 `@kit.AdsKit` 实际导出为准。

## 7. 已知陷阱

- HMS Ads 是系统能力，无需 HAR；如尝试 `ohpm install` 任何 hms-ads HAR 是错误的
- 鸿蒙 NEXT 的 AdsKit API 与 Android HMS Ads SDK 不是 1:1 对应；类名 / 回调结构有差异，以官方文档为准
- 广告位 ID 必须在华为 AGC 后台为 HarmonyOS 平台单独申请，不能复用 Android HMS Ads 的 ID
- `APP_TRACKING_CONSENT` 权限必须在用户授权后才能调用相关 API；提前调用会被拒绝
- AdContentClassification（年龄分级）等参数在鸿蒙端字段名可能不同
- 隐私同意前调 SDK 违反 Core Rule 6
