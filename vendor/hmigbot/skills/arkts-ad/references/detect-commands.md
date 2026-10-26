# Android 广告 SDK 识别命令清单

> Stage 0 用此文件中的 grep 命令在 Android 项目根目录扫描，输出"使用的 SDK 清单"。
> 命中后查 sdk-catalog.md 对应行决定后续走向。

## 前置变量

```bash
ANDROID_ROOT=/path/to/android/project   # 由 skill 主流程从用户处获取
```

## 1. Gradle 依赖扫描（最权威）

扫所有 build.gradle / build.gradle.kts：

```bash
rg -n "com\.bytedance\.sdk:openadsdk|com\.pangle\.global|com\.qq\.e\.|com\.qq\.e\.union|com\.kwad\.sdk|com\.huawei\.hms:ads|com\.baidu\.mobads|com\.bytedance\.sdk:gromore" \
   "$ANDROID_ROOT" --glob "build.gradle*" --glob "*.gradle.kts" --glob "settings.gradle*"
```

**命中含义**：
- `com.bytedance.sdk:openadsdk` → 穿山甲 CSJ → 查 sdk-catalog.md → sdk-csj.md
- `com.pangle.global:` → 穿山甲 Pangle 国际版 → sdk-csj.md
- `com.qq.e.` / `com.qq.e.union` → 优量汇 GDT → sdk-gdt.md
- `com.kwad.sdk` → 快手 KS → sdk-ks.md
- `com.huawei.hms:ads` → 华为 HMS Ads → sdk-hms-ads.md
- `com.baidu.mobads` → 百度联盟 → sdk-baidu.md（⚠️ 待核实）
- `com.bytedance.sdk:gromore` → GroMore 聚合 → sdk-gromore.md

## 2. SDK init 调用扫描（佐证）

```bash
rg -n "TTAdSdk\.init|TTAdManagerHolder|GDTAdSdk\.init|KsAdSDK\.init|HwAds\.init|BaiduAds\.init|MediationConfigUserInfoForSegment" \
   "$ANDROID_ROOT" --type kt --type java
```

**命中含义**：
- `TTAdSdk.init` / `TTAdManagerHolder` → 穿山甲已初始化
- `GDTAdSdk.init` → 优量汇已初始化
- `KsAdSDK.init` → 快手已初始化
- `HwAds.init` → 华为 HMS Ads 已初始化
- `BaiduAds.init` → 百度联盟已初始化
- `MediationConfigUserInfoForSegment` → GroMore 聚合代码特征

如 init 调用与 Gradle 依赖结果不一致（例如有 init 但 Gradle 没找到 dep），可能是模块拆分或动态加载，需要扩大扫描范围。

## 3. Manifest 权限佐证（弱信号）

```bash
rg -n "android\.permission\.(INTERNET|ACCESS_FINE_LOCATION|ACCESS_COARSE_LOCATION|READ_PHONE_STATE|ACCESS_WIFI_STATE)" \
   "$ANDROID_ROOT" --glob "AndroidManifest.xml"
```

**说明**：广告 SDK 通常会要求这些权限，但反向不成立（有这些权限不一定有广告 SDK）。仅作为佐证。

## 4. ProGuard/R8 keep 规则佐证（弱信号）

```bash
rg -n "-keep .*com\.(bytedance|qq\.e|kwad|huawei|baidu|pangle)" \
   "$ANDROID_ROOT" --glob "proguard*.pro" --glob "*proguard-rules*"
```

## Stage 0 输出格式

按以下格式整理结果：

| Android dep | 命中位置 | 对应 catalog 行 | 状态 |
|---|---|---|---|
| `com.bytedance.sdk:openadsdk:5.7.0.5` | `app/build.gradle:123` | sdk-csj.md ✅ 有 HAR | 需走 Stage 2/3 |
| `com.qq.e.union:union:4.460.1370` | `app/build.gradle:124` | sdk-gdt.md ✅ 有 HAR | 需走 Stage 2/3 |
| ... | ... | ... | ... |

未命中任何上述 SDK：直接输出"未识别到广告 SDK 使用，跳过迁移"，结束 skill。
