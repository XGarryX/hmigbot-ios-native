---
name: hmos-sdk-docs
description: 鸿蒙三方 SDK（伙伴 SDK）离线文档知识库。收录华为生态市场 SDK 分类全量 347 个 SDK 的集成文档（概览/使用指南/接口文档，2026-07 快照），含极光推送、环信/融云 IM、声网 RTC、友盟全家桶、支付宝支付、穿山甲/Taku 广告、高德地图等。当需要某个具体三方 SDK 的集成事实——初始化代码、API 签名、权限配置、ohpm 包名与版本、混淆配置——或问"鸿蒙上做推送/IM/广告的 SDK 有哪些"时触发。不要用于：三方库选型决策、Android 库找替代（用 arkts-library-migration）；HarmonyOS 官方 Kit API 事实（用 harmony-docs / harmony-docs-cli）。
metadata:
  type: domain
  domain: migration
  tags:
  - migration
  - third-party-sdk
  - ohpm
  - knowledge-base
---
# hmos-sdk-docs — 鸿蒙三方 SDK 离线文档库

## 库里有什么

快照 2026-07-17 ｜ **347 个 SDK**（华为生态市场 SDK 分类全量 + 62 个 ohpm README 补采 + 29 页厂商官方文档抓取）｜ ~11MB Markdown ｜ 文档厚度：厚 45 / 中 177 / 薄 125 ｜ 示例代码覆盖：**有示例 265（76%）/ 仅安装配置 42（12%）/ 纯文字 40（11%）**——后两档编码前必走 online-lookup，它们的市场页只是"目录入口"，真文档在厂商站。

分类分布（个）：安全风控 93 · 媒体 42 · 人工智能 28 · 认证 27 · 设备通信 20 · 统计 18 · 平台服务 16 · 广告 14 · 第三方登录 12 · 网络 12 · 社交 11 · 性能监控 11 · 系统工具 9 · 客服 7 · 地图 7 · 推送 7 · 游戏 6 · 框架 5 · 支付 2。

## 查询协议（按序执行）

1. **Grep 索引定位**：`Grep references/l0-index.md`，按 SDK 名、分类关键词或 ohpm 包名任一匹配。
   按能力找（"做推送的有哪些"）→ Grep 分类列（如 `推送 >`），逐行读出候选。
2. **Read 文档**：进入索引"数据目录"列指向的 `references/sdks/<分类>/<目录>/`（按 19 个一级分类分层；目录名 = 市场 productId 前 8 位 + SDK 名，前缀用于防重名与溯源，完整详情页 URL 在 overview.md 首行）：
   - `overview.md` — 市场详情页链接、约束与限制、版本、提供商、厂商外站链接（先读这个判断够不够用）
   - `manual.md` — 集成步骤（安装/权限/初始化/混淆）
   - `api.md` — 接口文档（存在且与 manual 不同份时才有）
   - `readme-ohpm.md` — ohpm 中央仓 README 补采（62 个市场文档缺代码的 SDK 有此文件；T1 信源，版本常比市场快照新，文件头标注了 ohpm 实际包名——**大厂的实际包名常与索引里的市场登记名不同**，如腾讯云 `LiteAVSDK`→`@tencentcloud/liteavsdk_*`、高德→`@amap/amap_lbs_*`）
   - `vendor-doc-N.md` — 厂商官方文档页快照（T2 信源，文件头有来源 URL；单页抓取，深层页面按 online-lookup 现场取）
3. **走线上**：索引"示例代码"列 = 纯文字或仅安装、"厚度"列 = 薄、SDK 未收录、或需要最新版本时，按 `references/online-lookup.md` 执行（ohpm 中央仓优先，一次 HTTP 拿原生 md README）。

Android SDK 找鸿蒙对应 → 先查 `references/android-mapping.md`（同厂优先，无同厂给能力对等项）。

## 事实与坑

- 索引"版本"列是**市场快照版本**，ohpm 上通常更新（实测过市场 1.8.0 vs ohpm 2.0.0）。编码引用版本号前，用 online-lookup 第一步核对最新版。
- 文档由厂商 PDF 机器转换而来。绝大多数干净，但个别文件残留字序错乱或重影段落——遇到明显混乱的段落，按 online-lookup 交叉验证后再用，可疑代码不直接照抄。
- 11 个 SDK 的 PDF 是图片型（离线只有骨架信息，索引中均为"薄"），必须走 online-lookup。
- `references/vendor-domains.json` 是 200 家厂商的官方域名白名单（从华为审核过的市场元数据推导），线上搜厂商文档时用它做 `site:` 限定，白名单外的结果标"非官方"。

## 边界

- 选型/找替代（"用什么替代 Glide"）→ **arkts-library-migration**（它做决策，本 skill 供它查证候选的集成事实）
- HarmonyOS 官方 Kit / ArkTS 语言 API → **harmony-docs**（MCP）/ **harmony-docs-cli**（subagent）
- 知识库刷新（月度）→ `scripts/sdk_kb/README.md` 三段式流水线

**Remember**：快照优先——先 Grep `references/l0-index.md` 再 Read 对应目录；厚度=薄或版本敏感场景必走 `references/online-lookup.md`；在线结果必须标注来源级别（T0-T4）与抓取日期。
