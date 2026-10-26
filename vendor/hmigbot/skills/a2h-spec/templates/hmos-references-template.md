# HarmonyOS 参考文档 — {项目名}

> 用户预提供的 HarmonyOS 知识参考。由 a2h-spec Step 3.0c 在源码路径确认后收集，落到 `spec/ref/hmos-references.md`。
> 后续 `android-api-inventory` 子 agent 与 a2h-plan grill #2 Step 0 共享消费此文件作为 HarmonyOS 等价物预标注 / 用户预知收集的输入源之一。
> **本文件可在项目全周期手工追加 / 修改**；每次 api-inventory 或 grill 跑时会重新读，无需重新生成。

---

## 1. API / SDK 总索引（通用层面）

> 不针对具体 API，而是 HarmonyOS API 全集文档入口、ArkTS 语法手册等总目录类资源。模型在做"未知 API 是否有鸿蒙等价物"判断时优先查这些索引。

- [ ] HarmonyOS Developer Docs（官方）: __
- [ ] ArkTS / ArkUI API Reference: __
- [ ] 公司内部 Wiki / 知识库: __
- [ ] 其他总索引: __

---

## 2. 厂商迁移指南（按 SDK 名）

> 针对具体三方 SDK / Kit 的官方或合作方提供的迁移文档。每个 SDK 一行，放链接 + 简短备注（如版本、域限制、已知不支持点）。

| SDK / API 名 | 文档链接 | 备注 |
|--------------|---------|------|
| __ | __ | __ |

**典型条目示例（删除后再用）**：
- 微信 (Open SDK) | https://... | alpha 鸿蒙包，仅支付 / 登录二接口
- 支付宝 | https://... | 官方未发布，使用 H5 收银台
- 华为账号 (Account Kit) | https://... | 需 entitlement 配置
- 火山引擎埋点 | __ | 暂无鸿蒙版

---

## 3. 内部资源 / 私有镜像

> 公司内部已经迁移过的方案 / 私有镜像地址 / 合作方提前给的鸿蒙 alpha 包等仅团队可见的资源。
> 模型查公开渠道找不到的信息，应优先从这里找。

- [ ] __

---

## 使用约定（给下游 skill 消费方）

- 本文件**完全可选**：未提供时下游降级到 `harmonyos-development` skill / `grill-with-docs` / Web 文档查询链
- 子 agent / grill 跑时，对每个 Android API / 三方 SDK / 系统能力：**优先匹配本文件中的条目**；命中即可作为 user-provided 等价物提示
- 用户可在项目跑到一半时手工追加新发现的链接；下次 api-inventory 或 grill 跑会自动消费新内容
