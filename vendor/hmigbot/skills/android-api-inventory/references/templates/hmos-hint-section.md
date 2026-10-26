# Phase 2.5：HarmonyOS 等价物提示段 模板

> SKILL.md Phase 2.5 的 markdown 输出示例。触发条件 / 设计原则 / 降级路径在主文件，**具体追加什么样的 markdown** 在本文件。
>
> 此段仅追加到 `api-inventory.md` 总览索引文件（**不下沉到 `apis/*.md`**）。

---

## 追加位置

`api-inventory.md` 末尾 —— 在「Feature 候选 / 覆盖度分析」之后；若该段不存在，直接接在文档末尾。

## 段标题与前言

```markdown
## HarmonyOS 等价物提示

> 来源两类：①框架 API 命中 —— 本 skill 静态映射表 references/framework-kit-mapping.md（2.5a，无条件）；
> ②三方 SDK 命中 —— 用户在 spec Step 3.0c 提供的 spec/ref/hmos-references.md（2.5b，有该文件才有）。
> 下游 a2h-plan grill #2 Step 0 应优先读本段（或直接读上述两个来源文件），避免对已有信息重复问用户。
> **本提示不是 contract** —— `api-inventory.json` 各 entry 未因此新增字段，提示仅在 markdown 中存在。
```

## 三个子段（标准结构）

### 子段 1：已命中

匹配上 hmos-references.md 条目的扫描项：

```markdown
### 已命中（框架映射 + 用户已提供等价物信息）

| 扫描识别 | HarmonyOS 提示 | 来源 |
|---------|---------------|------|
| Retrofit + OkHttp Interceptor ×3 | rcp 会话+拦截器（`@kit.RemoteCommunicationKit`，API 12+）或 NetworkKit http | framework-kit-mapping.md §1 |
| HMAC-SHA256 签名拦截器 (javax.crypto.Mac) | `cryptoFramework.createMac`（`@kit.CryptoArchitectureKit`） | framework-kit-mapping.md §3 |
| Gson @SerializedName ×47 字段 | 无等价 —— 字段镜像必须显式做（迁移关注点） | framework-kit-mapping.md §2 |
| 微信 Open SDK (com.tencent.mm.opensdk) | alpha 鸿蒙包，链接 [...] | hmos-references.md §2 厂商迁移指南 |
| 支付宝 (com.alipay.sdk:msp) | 官方未发布，使用 H5 收银台 | hmos-references.md §2 厂商迁移指南 |
| 私有镜像中的 X SDK | 已有内部鸿蒙适配，路径 [...] | hmos-references.md §3 内部资源 |
```

匹配规则：

- **框架栈（2.5a，先做）**：网络客户端 / 拦截器 / WebSocket·SSE / javax.crypto / SharedPreferences·Room / 设备标识 → 查 `framework-kit-mapping.md`，来源列填该文件 + 小节号；「无等价」条目也写入（即 migration_concerns 素材）
- `services` 中各 Service 类与 `third_party_apis` 的 `provider` → 优先匹配「厂商迁移指南」段的 SDK 名
- `third_party_domains`（按域名聚合）→ 匹配厂商迁移指南的域名（如 `weixin.qq.com` 对应微信条目）
- 认证拦截器 / 网络层基础设施（如自定义签名）→ 算法本体查 framework-kit-mapping.md §3；厂商专有签名方案匹配「总索引」段
- 完全无法对应的扫描项 → 跳过，不强行猜测

### 子段 2：未命中

```markdown
### 未命中（hmos-references.md 中无对应记录，后续 plan grill #2 阶段二补问）

- 个推推送 SDK
- 阿里一键登录 SDK
- 火山引擎埋点（用户标注暂无鸿蒙版，已计入"已命中"段）
- ...
```

来源：扫描结果有，但 hmos-references.md 没对应记录的条目。

### 子段 3：参考未触及

```markdown
### hmos-references.md 中存在但本次扫描未触及的条目

- 华为账号 (Account Kit) —— 项目未引入此依赖，参考留存备查
```

来源：hmos-references.md 列了，但项目实际未引入对应依赖。备查用。

---

## 完整示例（拼装）

```markdown
## HarmonyOS 等价物提示

> 来源两类：①框架 API（framework-kit-mapping.md，2.5a）②三方 SDK（hmos-references.md，2.5b）。
> 下游 a2h-plan grill #2 Step 0 应优先读本段，避免对已有信息重复问用户。
> **本提示不是 contract** —— `api-inventory.json` 各 entry 未因此新增字段，提示仅在 markdown 中存在。

### 已命中（框架映射 + 用户已提供等价物信息）

| 扫描识别 | HarmonyOS 提示 | 来源 |
|---------|---------------|------|
| Retrofit + OkHttp Interceptor ×3 | rcp 会话+拦截器（@kit.RemoteCommunicationKit，API 12+） | framework-kit-mapping.md §1 |
| Gson @SerializedName ×47 字段 | 无等价 —— 字段镜像必须显式做 | framework-kit-mapping.md §2 |
| 微信 Open SDK (com.tencent.mm.opensdk) | alpha 鸿蒙包，链接 [...] | hmos-references.md §2 厂商迁移指南 |
| 支付宝 (com.alipay.sdk:msp) | 官方未发布，使用 H5 收银台 | hmos-references.md §2 厂商迁移指南 |
| 自定义签名拦截器 | 参考 HarmonyOS Developer Docs §加密 | hmos-references.md §1 总索引 |

### 未命中（hmos-references.md 中无对应记录，后续 plan grill #2 阶段二补问）

- 个推推送 SDK
- 阿里一键登录 SDK

### hmos-references.md 中存在但本次扫描未触及的条目

- 华为账号 (Account Kit) —— 项目未引入此依赖，参考留存备查
```

---

## 降级写法

| 情况 | 处置 |
|------|------|
| `hmos_references_file` 不存在或为空 | 跳过 2.5b；**2.5a 框架命中非空时仍写本段**（已命中表只含 framework-kit-mapping 来源行 + 三方全列「未命中」）|
| 文件存在但与扫描结果零交集 | 仍写本段：框架命中照常，三方部分只列「未命中」与「未触及」两个子段 |
| 框架命中与三方命中都为零（极少：离线项目） | 整段跳过，**不**写本段 |
