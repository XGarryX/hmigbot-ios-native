# 快手 KS (Kuaishou Ads)

**官方索引页：** https://u.kuaishou.com/portal/adNetwork/sdkDownload
**最后核对：** 2026-05
**警示：** 如离最后核对超过 6 个月，先访问官方索引页核对版本与 API 是否变更。

---

## 1. 下载与安装

- HAR 下载页：https://u.kuaishou.com/portal/adNetwork/sdkDownload → 找"鸿蒙"或"HarmonyOS"
- 放置位置（两个 HAR）：
  - `entry/libs/KSAdSDK-X.Y.Z.har`
  - `entry/libs/adapter_ks-X.Y.Z.har`（GroMore 聚合场景需要）
- entry/oh-package.json5 引用片段：
  ```json5
  "dependencies": {
    "ksadsdk": "file:libs/KSAdSDK-X.Y.Z.har",
    "@csj/adapter_ks": "file:libs/adapter_ks-X.Y.Z.har"
  }
  ```
- 根目录 oh-package.json5 overrides：
  ```json5
  "overrides": {
    "ksadsdk": "file:entry/libs/KSAdSDK-X.Y.Z.har"
  }
  ```

## 2. module.json5 权限表

| 权限 | 作用 | 是否必需 | 默认推荐 | 隐私影响 |
|---|---|---|---|---|
| `ohos.permission.INTERNET` | 广告请求 + 物料下载 | ✅ 必需 | ✅ 加 | 无 |
| `ohos.permission.GET_NETWORK_INFO` | 区分网络类型 | ⚠️ 推荐 | ✅ 加 | 低 |
| `ohos.permission.LOCATION` | LBS 定向广告 | ❌ 可选 | ❌ 不加 | 高 |
| `ohos.permission.READ_DEVICE_ID`（OAID）| 设备标识 | ❌ 可选 | ⚠️ 看商务要求 | 高 |

> 详细权限以官方文档为准。

## 3. Application 初始化

### Android (Kotlin) before
```kotlin
KsAdSDK.init(context, SdkConfig.Builder()
    .appId(BuildConfig.KS_APP_ID)
    .appName(getString(R.string.app_name))
    .showNotification(true)
    .debug(BuildConfig.DEBUG)
    .build())
```

### HarmonyOS ArkTS (EntryAbility.onCreate) after
```typescript
import { KsAdSDK } from 'ksadsdk';

class AdService {
  async init(context: Context): Promise<void> {
    if (!privacyService.isAccepted()) return;
    KsAdSDK.init(context, {
      appId: AdConfig.KS_HARMONY_APP_ID,
      appName: AdConfig.APP_NAME,
      debug: false
    });
  }
}
```

> 实际类名 / 方法签名以官方 HAR 为准。

## 4. WindowStage 绑定

需 windowStage 的广告类型：插屏（`KsInterstitialAd`）、激励视频（`KsRewardVideoAd`）。

```typescript
class AdService {
  bindWindowStage(stage: window.WindowStage): void {
    this.windowStage = stage;
  }
}
```

## 5. 关键 API 1:1 对照表

| 广告类型 | Android API | HarmonyOS API | 备注 |
|---|---|---|---|
| 开屏 | `KsAdSDK.getLoadManager().loadSplashScreenAd(slot, listener)` → `getView()` | `KsAdSDK.getLoadManager().loadSplashScreenAd(slot, listener)` → `getView()` | View → ArkTS 容器节点 |
| 插屏 | `loadInterstitialAd(slot, listener)` → `showInterstitialAd(activity)` | `loadInterstitialAd(slot, listener)` → `showInterstitialAd(windowStage)` | activity → windowStage |
| 激励视频 | `loadRewardVideoAd(slot, listener)` → `showRewardVideoAd(activity)` | `loadRewardVideoAd(slot, listener)` → `showRewardVideoAd(windowStage)` | 奖励在 `onRewardVerify` |
| 信息流 | `loadFeedAd(slot, listener)` → 取 List<KsFeedAd> | `loadFeedAd(slot, listener)` → 取 List<KsFeedAd> | UI 走 ArkTS 自定义渲染 |
| Banner | `loadBannerAd(slot, listener)` | `loadBannerAd(slot, listener)` | 失败折叠 |

> ⚠️ HarmonyOS API 类名以官方 HAR 实际导出为准。

## 6. 完整 before/after：开屏广告

### Android Kotlin
```kotlin
class SplashActivity : AppCompatActivity() {
  override fun onCreate(b: Bundle?) {
    super.onCreate(b)
    val container = findViewById<FrameLayout>(R.id.splash_container)
    KsAdSDK.getLoadManager().loadSplashScreenAd(
      KsScene.Builder(BuildConfig.KS_SPLASH_SLOT_ID).build(),
      object : KsLoadManager.SplashScreenAdListener {
        override fun onSplashScreenAdLoad(splashAd: KsSplashScreenAd) {
          val view = splashAd.getView(this@SplashActivity, object : KsSplashScreenAd.SplashScreenAdInteractionListener {
            override fun onAdClicked() { }
            override fun onAdShowError(code: Int, msg: String?) { goMain() }
            override fun onAdShowEnd() { goMain() }
            override fun onSkippedAd() { goMain() }
            override fun onAdShowStart() { }
            override fun onDownloadTipsDialogShow() { }
            override fun onDownloadTipsDialogDismiss() { }
            override fun onDownloadTipsDialogCancel() { }
          })
          container.addView(view)
        }
        override fun onError(code: Int, msg: String?) { goMain() }
        override fun onRequestResult(adNumber: Int) { }
      }
    )
  }
}
```

### HarmonyOS ArkTS
```typescript
// services/AdService.ets — 增加 loadKsSplash 方法
class AdService {
  async loadKsSplash(slotId: string, container: StackLike): Promise<SplashResult> {
    if (!privacyService.isAccepted()) return { ok: false, reason: 'privacy' };
    return new Promise((resolve) => {
      KsAdSDK.getLoadManager().loadSplashScreenAd({ posId: slotId }, {
        onSplashScreenAdLoad: (splashAd) => {
          const view = splashAd.getView(getContext(this), {
            onAdShowEnd: () => resolve({ ok: true }),
            onAdShowError: (code, msg) => resolve({ ok: false, reason: `show_err:${code}` }),
            onSkippedAd: () => resolve({ ok: true })
          });
          container.addChild(view);
        },
        onError: (code, msg) => resolve({ ok: false, reason: `load_err:${code}` })
      });
    });
  }
}
```

> ⚠️ ArkTS 端代码为模式示意；以官方 HAR 实际导出为准。

## 7. 已知陷阱

- 在 GroMore 聚合场景下，KS 通过 `@csj/adapter_ks` 适配器被 CSJ 调用；adapter 版本必须与 CSJ 版本配对
- adapter HAR 声明远端 KS 版本，必须用根 oh-package.json5 overrides 重定向到本地 HAR
- 复用 Android 广告位 ID 不可用，必须在快手广告后台为鸿蒙端单独申请
- 隐私同意前调 `init()` 违反 Core Rule 6
- 激励视频奖励必须等 `onRewardVerify`，不能在 load/show 时发奖
- KS 信息流物料是视频时，需要在容器节点上预留视频播放控件位置
