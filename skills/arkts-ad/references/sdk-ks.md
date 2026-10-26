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

### 原生源调用取证
源侧按锁定版本的真实 Swift/Objective-C SDK 调用取证：初始化/隐私、广告位、加载/渲染/展示/关闭、失败/超时/取消、奖励回调与生命周期；不使用其他源语法的示例推导接口。

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

## 5. 原生 API 与目标候选

逐项读取实际依赖、源调用和目标 HAR 导出，建立初始化/开屏/插屏/激励/信息流等行为映射。没有通用 1:1 类名或签名等价承诺。源 UIViewController/展示容器不等于目标 windowStage；奖励必须对应真实有效回调，失败与取消不得发奖。下文目标代码是候选示例，实际版本 API 需核验。

## 6. 完整 before/after：开屏广告

### iOS 原生源证据
源侧按锁定版本的真实 Swift/Objective-C SDK 调用取证：初始化/隐私、广告位、加载/渲染/展示/关闭、失败/超时/取消、奖励回调与生命周期；不使用其他源语法的示例推导接口。

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
- 复用 iOS 广告位 ID 不可用，必须在快手广告后台为鸿蒙端单独申请
- 隐私同意前调 `init()` 违反 Core Rule 6
- 激励视频奖励必须等 `onRewardVerify`，不能在 load/show 时发奖
- KS 信息流物料是视频时，需要在容器节点上预留视频播放控件位置
