# 穿山甲 CSJ / Pangle

**官方索引页：** https://www.csjplatform.com/union/media/union/download/detail?id=206&osType=harmony&locale=zh-CN
**最后核对：** 2026-05
**警示：** 如离最后核对超过 6 个月，先访问官方索引页核对版本与 API 是否变更。

---

## 1. 下载与安装

- HAR 下载页：https://www.csjplatform.com/union/media/union/download/detail?id=206&osType=harmony
- 放置位置：`entry/libs/openadsdk-X.Y.Z.har`（版本以官方最新为准；Fitness 项目曾用 `openadsdk_7.5.3.har`）
- entry/oh-package.json5 引用片段：
  ```json5
  "dependencies": {
    "@csj/openadsdk": "file:libs/openadsdk-X.Y.Z.har"
  }
  ```
- 根目录 oh-package.json5 overrides 配置（adapter HAR 内部声明的远端版本会被 ohpm 错误解析，必须用根级 overrides 重定向到本地 HAR）：
  ```json5
  "overrides": {
    "@csj/openadsdk": "file:entry/libs/openadsdk-X.Y.Z.har"
  }
  ```

## 2. module.json5 权限表

| 权限 | 作用 | 是否必需 | 默认推荐 | 隐私影响 |
|---|---|---|---|---|
| `ohos.permission.INTERNET` | 广告请求 + 物料下载 | ✅ 必需 | ✅ 加 | 无 |
| `ohos.permission.GET_NETWORK_INFO` | 区分 Wi-Fi/移动网络做物料降码率 | ⚠️ 推荐 | ✅ 加 | 低 |
| `ohos.permission.LOCATION` | LBS 定向广告（提升 eCPM） | ❌ 可选 | ❌ 不加 | 高 — 需用户授权 + 写 reason |
| `ohos.permission.READ_DEVICE_ID`（OAID）| 跨 App 设备标识，去重计费 | ❌ 可选 | ⚠️ 看商务要求 | 高 — 隐私协议要写 |

> 详细权限清单与作用以官方文档为准；本表基于公开资料，请以官方 SDK 文档为准。

## 3. Application 初始化（init + start）

CSJ 的初始化分两步：`init` 配置 + `start` 启动。两步都成功才能 load 广告。

### Android (Kotlin) before
```kotlin
// Application.kt
TTAdSdk.init(context, TTAdConfig.Builder()
    .appId(BuildConfig.CSJ_APP_ID)
    .appName(getString(R.string.app_name))
    .useTextureView(true)
    .titleBarTheme(TTAdConstant.TITLE_BAR_THEME_DARK)
    .allowShowNotify(true)
    .debug(BuildConfig.DEBUG)
    .supportMultiProcess(false)
    .build())

TTAdSdk.start(object : TTAdSdk.Callback {
    override fun success() { /* SDK 启动成功 */ }
    override fun fail(code: Int, msg: String?) { /* 降级 no-op */ }
})
```

### HarmonyOS ArkTS (EntryAbility.onCreate) after
```typescript
// services/AdService.ets
import { CSJAdSdk } from '@csj/openadsdk';

class AdService {
  async init(context: Context): Promise<void> {
    if (!privacyService.isAccepted()) return;  // Core Rule 6
    CSJAdSdk.init(context, {
      appId: AdConfig.CSJ_HARMONY_APP_ID,   // 鸿蒙专属 App ID（Core Rule 4）
      appName: AdConfig.APP_NAME,
      debug: false
    });
    await this.start();
  }

  private async start(): Promise<void> {
    return new Promise((resolve) => {
      CSJAdSdk.start({
        success: () => resolve(),
        fail: (code, msg) => {
          console.error(`CSJAdSdk.start failed: ${code} ${msg}`);
          resolve();   // 降级 no-op，业务继续
        }
      });
    });
  }
}
export const adService = new AdService();

// entryability/EntryAbility.ets
import { adService } from '../services/AdService';

export default class EntryAbility extends UIAbility {
  onCreate(want, param) {
    super.onCreate(want, param);
    adService.init(this.context);
  }

  onWindowStageCreate(windowStage: window.WindowStage) {
    adService.bindWindowStage(windowStage);
  }
}
```

> 实际类名 / 方法签名以官方 HAR 为准；本片段为模式示意。

## 4. WindowStage 绑定

需 windowStage 的广告类型：
- 全屏/插屏（`showFullAd` / `showInterstitial`）
- 激励视频（`showRewardVideo`）

绑定代码：
```typescript
class AdService {
  private windowStage?: window.WindowStage;
  bindWindowStage(stage: window.WindowStage): void {
    this.windowStage = stage;
  }
  showFullAd(slotId: string): Promise<void> {
    if (!this.windowStage) throw new Error('WindowStage 未绑定，showFullAd 不可用');
    // 调 SDK 全屏 API，传 windowStage
  }
}
```

## 5. 关键 API 1:1 对照表

| 广告类型 | Android API | HarmonyOS API | 备注 |
|---|---|---|---|
| 开屏 | `TTAdSdk.getAdManager().createAdNative(ctx).loadSplashAd(slot, listener, timeout)` | `CSJAdSdk.getAdManager().createAdNative(ctx).loadSplashAd(...)` | 类名等价；方法签名以官方 HAR 为准 |
| 插屏/全屏 | `loadFullScreenVideoAd(slot, listener)` → `showFullScreenVideoAd(activity)` | `loadFullScreenVideoAd(slot, listener)` → `showFullScreenVideoAd(windowStage)` | activity → windowStage |
| 激励视频 | `loadRewardVideoAd(slot, listener)` → `showRewardVideoAd(activity)` | `loadRewardVideoAd(slot, listener)` → `showRewardVideoAd(windowStage)` | 奖励发放在 `onRewardVerify` 回调 |
| 信息流 | `loadFeedAd(slot, listener)` → 取 List<TTFeedAd> | `loadFeedAd(slot, listener)` → 取 List<CSJFeedAd> | UI 容器走 ArkTS 自定义渲染 |
| Banner | `loadBannerExpressAd(slot, listener)` | `loadBannerExpressAd(slot, listener)` | 失败折叠为零高度 |

> ⚠️ HarmonyOS API 类名以官方 HAR `@csj/openadsdk` 实际导出为准；上表基于 Android API 等价猜测，请以官方文档为准。

## 6. 完整 before/after：开屏广告

### Android Kotlin
```kotlin
class SplashActivity : AppCompatActivity() {
  override fun onCreate(savedInstanceState: Bundle?) {
    super.onCreate(savedInstanceState)
    setContentView(R.layout.activity_splash)
    val container = findViewById<FrameLayout>(R.id.splash_container)

    val slot = AdSlot.Builder()
      .setCodeId(BuildConfig.CSJ_SPLASH_SLOT_ID)
      .setExpressViewAcceptedSize(360f, 640f)
      .build()

    TTAdSdk.getAdManager().createAdNative(this).loadSplashAd(slot, object : TTAdNative.SplashAdListener {
      override fun onSplashLoadSuccess() { /* 物料缓存成功 */ }
      override fun onSplashRenderSuccess(splashAd: CSJSplashAd) {
        splashAd.splashView?.let { container.addView(it) }
        splashAd.setSplashAdListener(object : CSJSplashAd.SplashAdListener {
          override fun onSplashAdShow(...) { /* show */ }
          override fun onSplashAdClick(...) { /* click */ }
          override fun onSplashAdClose(...) { goMain() }
        })
      }
      override fun onSplashLoadFail(error: CSJAdError?) { goMain() }
      override fun onSplashRenderFail(splashAd: CSJSplashAd?, error: CSJAdError?) { goMain() }
    }, 3000)
  }

  private fun goMain() { startActivity(Intent(this, MainActivity::class.java)); finish() }
}
```

### HarmonyOS ArkTS
```typescript
// services/AdService.ets — 增加 loadSplash 方法
class AdService {
  async loadSplash(slotId: string, container: FrameLayoutLike, timeoutMs: number = 3000): Promise<SplashResult> {
    if (!privacyService.isAccepted()) return { ok: false, reason: 'privacy' };
    return new Promise((resolve) => {
      CSJAdSdk.getAdManager().createAdNative(getContext(this)).loadSplashAd(
        { codeId: slotId, expressViewAcceptedSize: { width: 360, height: 640 } },
        {
          onSplashRenderSuccess: (splashAd) => {
            container.addChild(splashAd.splashView);
            splashAd.setSplashAdListener({
              onSplashAdShow: () => { /* track show */ },
              onSplashAdClose: () => resolve({ ok: true })
            });
          },
          onSplashLoadFail: (err) => resolve({ ok: false, reason: 'load_fail' }),
          onSplashRenderFail: (_, err) => resolve({ ok: false, reason: 'render_fail' })
        },
        timeoutMs
      );
    });
  }
}

// pages/SplashPage.ets — UI 调用（V2，API 12+）
@Entry
@ComponentV2
struct SplashPage {
  @Local container?: FrameLayoutLike = undefined;

  aboutToAppear() {
    adService.loadSplash(AdConfig.CSJ_HARMONY_SPLASH_SLOT_ID, this.container!).then((result) => {
      RouterUtil.replace(RouteConst.PAGE_MAIN);
    });
  }

  build() {
    Stack() {
      // splash container 节点
    }.width('100%').height('100%')
  }
}
```

> ⚠️ ArkTS 端类名 / 方法签名 / 回调结构以 `@csj/openadsdk` HAR 实际导出为准；上述代码为模式示意。

## 7. 已知陷阱

- adapter HAR（如 GroMore 适配器、GDT/KS 适配器）声明远端版本的 `@csj/openadsdk`；ohpm 解析时优先远端，必须用根 oh-package.json5 `overrides` 重定向到本地 HAR
- WindowStage 绑定前调 `showFullScreenVideoAd` / `showSplashAd` 会失败
- 复用 Android 广告位 ID 不可用，必须在穿山甲后台为鸿蒙端单独申请 App ID + 广告位 ID
- 隐私同意前调 `init()` / `start()` 违反 Core Rule 6
- 频控规则放在项目 service 层（如 `TabAdController`），不放 SDK 层
- `start()` 失败但 `init()` 成功时，load 回调可能不触发；排查时必须看 SDK 日志中的 start 成功码
- 激励视频在 `onAdShow` 时发奖励是错误的；必须等 `onRewardVerify` / `onRewardArrived` 回调
