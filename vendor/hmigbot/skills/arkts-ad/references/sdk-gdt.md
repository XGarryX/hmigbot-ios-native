# 优量汇 GDT (Tencent Ads)

**官方索引页：** https://e.qq.com/dev/help_detail.html?cid=2367
**最后核对：** 2026-05
**警示：** 如离最后核对超过 6 个月，先访问官方索引页核对版本与 API 是否变更。

---

## 1. 下载与安装

- HAR 下载页：https://e.qq.com/dev/help_detail.html?cid=2367 → 找"鸿蒙 SDK"或"HarmonyOS"分类
- 放置位置（两个 HAR）：
  - `entry/libs/gdt-union-sdk-X.Y.Z.har`（GDT 主 SDK）
  - `entry/libs/adapter_gdt-X.Y.Z.har`（在 GroMore 聚合场景下需要）
- entry/oh-package.json5 引用片段：
  ```json5
  "dependencies": {
    "@gdt/gdt-union-sdk": "file:libs/gdt-union-sdk-X.Y.Z.har",
    "@csj/adapter_gdt": "file:libs/adapter_gdt-X.Y.Z.har"
  }
  ```
- 根目录 oh-package.json5 overrides（adapter 内部可能引远端 GDT，需重定向）：
  ```json5
  "overrides": {
    "@gdt/gdt-union-sdk": "file:entry/libs/gdt-union-sdk-X.Y.Z.har"
  }
  ```

## 2. module.json5 权限表

| 权限 | 作用 | 是否必需 | 默认推荐 | 隐私影响 |
|---|---|---|---|---|
| `ohos.permission.INTERNET` | 广告请求 + 物料下载 | ✅ 必需 | ✅ 加 | 无 |
| `ohos.permission.GET_NETWORK_INFO` | 区分 Wi-Fi/移动网络 | ⚠️ 推荐 | ✅ 加 | 低 |
| `ohos.permission.LOCATION` | LBS 定向广告 | ❌ 可选 | ❌ 不加 | 高 |
| `ohos.permission.READ_DEVICE_ID`（OAID）| 跨 App 设备标识 | ❌ 可选 | ⚠️ 看商务要求 | 高 |

> 详细权限以官方文档为准。

## 3. Application 初始化

GDT 通常单步 init（无独立 start）。

### Android (Kotlin) before
```kotlin
GDTAdSdk.init(context, BuildConfig.GDT_APP_ID)
GlobalSetting.setEnableMediationTool(true)
```

### HarmonyOS ArkTS (EntryAbility.onCreate) after
```typescript
import { GDTAdSdk } from '@gdt/gdt-union-sdk';

class AdService {
  async init(context: Context): Promise<void> {
    if (!privacyService.isAccepted()) return;
    GDTAdSdk.init(context, AdConfig.GDT_HARMONY_APP_ID);
  }
}
```

> 实际类名 / 方法签名以官方 HAR 为准。

## 4. WindowStage 绑定

需 windowStage 的广告类型：插屏（`UnifiedInterstitialAD`）、激励视频（`RewardVideoAD`）。

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
| 开屏 | `SplashAD(activity, slot, listener)` → `fetchAndShowIn(container)` | `SplashAD(context, slot, listener)` → `fetchAndShowIn(stack)` | activity → context；container → ArkTS Stack |
| 插屏 | `UnifiedInterstitialAD(activity, slot, listener)` → `loadAD()` → `show()` | `UnifiedInterstitialAD(windowStage, slot, listener)` → `loadAD()` → `show()` | activity → windowStage |
| 激励视频 | `RewardVideoAD(activity, slot, listener)` → `loadAD()` → `showAD(activity)` | `RewardVideoAD(context, slot, listener)` → `loadAD()` → `showAD(windowStage)` | 奖励发放在 `onReward` |
| 信息流 | `NativeExpressAD(activity, size, slot, listener)` → `loadAD(count)` | `NativeExpressAD(context, size, slot, listener)` → `loadAD(count)` | UI 走 ArkTS 自定义渲染 |
| Banner | `UnifiedBannerView(activity, slot, listener)` | `UnifiedBannerView(stack, slot, listener)` | 失败折叠 |

> ⚠️ HarmonyOS API 类名以官方 HAR 实际导出为准；上表基于 Android API 等价猜测，请以官方文档为准。

## 6. 完整 before/after：开屏广告

### Android Kotlin
```kotlin
class SplashActivity : AppCompatActivity() {
  override fun onCreate(b: Bundle?) {
    super.onCreate(b)
    val container = findViewById<FrameLayout>(R.id.splash_container)
    SplashAD(this, BuildConfig.GDT_SPLASH_SLOT_ID, object : SplashADListener {
      override fun onADLoaded(expireTime: Long) { }
      override fun onADPresent() { /* show */ }
      override fun onADClicked() { }
      override fun onADDismissed() { goMain() }
      override fun onADExposure() { }
      override fun onADTick(remain: Long) { }
      override fun onNoAD(error: AdError?) { goMain() }
    }).fetchAndShowIn(container)
  }
}
```

### HarmonyOS ArkTS
```typescript
// services/AdService.ets — 增加 loadGdtSplash 方法
class AdService {
  async loadGdtSplash(slotId: string, container: StackLike): Promise<SplashResult> {
    if (!privacyService.isAccepted()) return { ok: false, reason: 'privacy' };
    return new Promise((resolve) => {
      const ad = new SplashAD(getContext(this), slotId, {
        onADPresent: () => { /* show track */ },
        onADDismissed: () => resolve({ ok: true }),
        onNoAD: (err) => resolve({ ok: false, reason: 'no_ad' })
      });
      ad.fetchAndShowIn(container);
    });
  }
}
```

> ⚠️ ArkTS 端代码为模式示意；以官方 HAR 实际导出为准。

## 7. 已知陷阱

- 在 GroMore 聚合场景下，GDT 通过 `@csj/adapter_gdt` 适配器被 CSJ 调用；adapter 版本必须与 CSJ 版本配对
- adapter HAR 声明远端 GDT 版本，必须用根 oh-package.json5 overrides 重定向
- GDT 没有独立 `start()` 步骤；如代码仍调 `start()` 是粘错的 CSJ 模式
- 复用 Android 广告位 ID 不可用，必须在优量汇后台为鸿蒙端单独申请
- 隐私同意前调 `init()` 违反 Core Rule 6
- 信息流广告物料尺寸不当导致渲染失败：必须按文档约定的几个标准尺寸
