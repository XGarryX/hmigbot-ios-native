# 百度联盟 BES (Baidu Mobile Ads) ⚠️ 待核实

**官方索引页：** https://union.baidu.com/bqt/#/login
**最后核对：** 2026-05
**警示：** 写本文档时无法 100% 确认百度联盟在鸿蒙 NEXT / OpenHarmony 是否提供官方 HAR。**用户必须先访问官方索引页核对**：

1. 登录百度联盟开发者后台 → "SDK 下载" / "开发文档"
2. 搜"鸿蒙"或"HarmonyOS"或"OpenHarmony"
3. 确认是否有官方 HAR 下载链接

---

## 0. 鸿蒙端可用性核对

按以下分支处理：

### ✅ 找到官方 HAR
→ 走 `generic-sdk-template.md` 的 §1-§7 通用对接流程，按官方文档填具体类名 / API。**不要用本文档**填补缺失信息（本文档是简化兜底）。

### ⚠️ 未找到 HAR 但社区有 port
→ 用户自评风险；如选择接入，按 `generic-sdk-template.md` 谨慎走，重点关注：
- HAR 来源可信度
- 与官方版本号的对应关系
- 是否有第三方 ohpm 维护

### ❌ 明确无对应
→ 走 `generic-sdk-template.md` §0.E 替代方案：
- HMS Ads 兜底（参考 sdk-hms-ads.md）
- Web H5 落地页
- 移除该广告场景

---

## 1. 下载与安装

待核实。访问官方索引页确认。

## 2. module.json5 权限表

参考其它 SDK 的通用权限模板（INTERNET 必需 + GET_NETWORK_INFO 推荐 + LOCATION/设备标识可选），具体权限清单以百度联盟鸿蒙文档为准。

## 3-6. 详细 API 表与代码

写本文档时无法核实。如官方提供 HarmonyOS HAR，用户应**直接走 `generic-sdk-template.md`** 的通用流程，不复用本文档（避免基于猜测填错的 API）。

## 7. 已知陷阱（通用，不限于百度联盟）

- 复用 Android 广告位 ID 不可用，必须为鸿蒙端单独申请
- 隐私同意前调 SDK 违反 Core Rule 6
- 第三方 SDK 的鸿蒙端 port 版本可能落后于 Android 主线，注意 API / 错误码差异

---

## 维护提示

下次更新本 skill 时（≥ 6 个月或用户报告需求时）：
1. 访问官方索引页确认百度联盟鸿蒙端最新支持状态
2. 如已提供官方 HAR，按 `sdk-csj.md` / `sdk-gdt.md` 模板补完 §1-§7
3. 在 `sdk-catalog.md` 中把状态从 `⚠️ 待核实` 改为 `✅ 有 HAR` 或 `❌ 暂无对应`
