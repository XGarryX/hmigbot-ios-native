# 广告 SDK 鸿蒙端可用性目录

> Stage 1 单点查表：detect 命中的 Android Gradle dep → 鸿蒙端可用性 + 对应详情文档。
> 严选 6 个国内市场主流广告 SDK；未列入的走 generic-sdk-template.md 兜底。

## 严选索引表

| Android Gradle dep（关键字） | 名称 | 鸿蒙端状态 | 鸿蒙 HAR / ohpm 包 | 官方索引页 | 最后核对 | 详情 |
|---|---|---|---|---|---|---|
| `com.huawei.hms:ads-lite` / `com.huawei.hms:ads-base` | 华为 HMS Ads | ✅ 原生 | `@kit.AdsKit` 系统能力（无需 HAR） | https://developer.huawei.com/consumer/cn/doc/harmonyos-references/js-apis-ads | 2026-05 | sdk-hms-ads.md |
| `com.bytedance.sdk:openadsdk` / `com.pangle.global:` | 穿山甲 CSJ / Pangle | ✅ 有 HAR | `@csj/openadsdk` (file:libs/openadsdk-X.Y.Z.har) | https://www.csjplatform.com/union/media/union/download/detail?id=206&osType=harmony | 2026-05 | sdk-csj.md |
| `com.qq.e:gdt-sdk` / `com.qq.e.union` | 优量汇 GDT | ✅ 有 HAR (adapter) | `@gdt/gdt-union-sdk` + `@csj/adapter_gdt` | https://e.qq.com/dev/help_detail.html?cid=2367 | 2026-05 | sdk-gdt.md |
| `com.kwad.sdk:*` | 快手 KS | ✅ 有 HAR (adapter) | `ksadsdk` + `@csj/adapter_ks` | https://u.kuaishou.com/portal/adNetwork/sdkDownload | 2026-05 | sdk-ks.md |
| `com.baidu.mobads:*` | 百度联盟 BES | ⚠️ 待核实 | （需访问官方索引页核对） | https://union.baidu.com/bqt/#/login | 2026-05 | sdk-baidu.md |
| `com.bytedance.sdk:gromore` | GroMore 聚合 | ✅ 有 HAR | `@csj/openadsdk` 内嵌 + 各家 adapter HARs | https://www.csjplatform.com/union/media/union/download/detail?id=206&osType=harmony | 2026-05 | sdk-gromore.md |

## 字段语义

- **鸿蒙端状态**：
  - `✅ 原生` — 鸿蒙系统自带 API（如 @kit.AdsKit），无需引入第三方 HAR
  - `✅ 有 HAR` — 官方提供 HarmonyOS 适配 HAR，按 sdk-*.md 集成
  - `⚠️ 待核实` — 写本目录时无法 100% 确认；用户必须访问官方索引页核对
  - `❌ 暂无对应` — 鸿蒙端确认无可用版本；走替代方案（HMS Ads 兜底 / Web H5 落地页 / 移除场景）
- **最后核对**：写本目录时的年月。Stage 1 主流程会显式提示用户：如离最后核对超过 6 个月，先访问官方索引页核对。

## 未列入 SDK 兜底

如 detect 命中的 Android dep 不在上表中（如 Mintegral / TopOn / Unity Ads / AdMob / Facebook Audience 等），按以下顺序处理：

1. 访问 SDK 官方文档查"HarmonyOS"或"鸿蒙"关键字，确认是否有 HAR
2. 有 HAR → 按 `generic-sdk-template.md` 的抽象 6 步走
3. 无 HAR → 鸿蒙端无对应；提示替代：HMS Ads 兜底 / Web H5 落地页 / 移除该广告场景
