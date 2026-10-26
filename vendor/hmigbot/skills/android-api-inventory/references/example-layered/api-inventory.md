# API Inventory（分层骨架示例）   ← 这是**分层形态总览索引骨架**，不是完整产出

> 假设项目 17 Service / 97 endpoint，按 SKILL.md §3.2 强制走**分层形态**：
> `api-inventory.md`（本文件，总览索引）+ `common.md`（公共约定）+ `apis/<模块>.md`（每模块一文件）。
>
> 本文件展示**总览索引该长什么样**：保留全部章节骨架，但每章内容裁剪到 1-2 行示意。
> 完整产出 ~1100 行；真实跑会落在工程仓 `spec/baseline/api-inventory/` 下，不是这里。

---

## 概览

| 维度 | 数量 |
|------|------|
| API 服务数 | 17 |
| 接口端点数 | 97 |
| 第三方 API provider | 5 |
| 涉及模块 | common, feature_image, feature_video, network, pay, push, tracking |
| runtime 已抓数 / 总数 | 1 / 97（示例只演示 initUser 一条；真实产出抓 ≥ 5 条核心接口）|

**技术栈**：Retrofit + OkHttp，RxJava2 与 Kotlin coroutines 混用（详见 `project_profile.notes`）

## 文档导航

> 分层形态下，本文件只放索引；endpoint 明细全在 `apis/*.md`，公共约定全在 `common.md`。

| 文档 | 内容 | 端点数 | runtime 已抓 |
|------|------|:--:|:--:|
| [common.md](common.md) | 公共约定（信封 / 签名 / 公参 / 业务码 / 共享 Bean） | — | — |
| [apis/user.md](apis/user.md) | 用户登录、第三方账号绑定、账号管理 | 12 | 1 |
| *apis/pay.md* | 支付、订单、VIP（示例只展开 `apis/user.md`） | 13 | 0 |
| *apis/feature_image.md* | 图像生成 / 编辑业务接口 | 14 | 0 |
| *apis/feature_video.md* | 视频生成 / 动画业务接口 | 10 | 0 |
| *apis/common.md* | 公共配置 / 应用初始化 / 日志上报 | 18 | 0 |
| *apis/push.md* | 推送 ClientID 上报 / 通知 | 6 | 0 |
| *apis/tracking.md* | 埋点 | 5 | 0 |
| *apis/chat_sse.md* | 聊天 SSE 流式接口 | 8 | 0 |
| *apis/basic.md* | 基础设施（应用日志 / 安全检测） | 11 | 0 |

> 真实产出每个 `apis/*.md` 都填齐；本示例只展开 `apis/user.md` 作为代表。

## Base URL

| 名称 | URL | 环境 | 来源文件 |
|------|-----|------|----------|
| 主服务（生产） | `AppConfig.baseUrl（动态配置）` | production | common/.../AppConfig.kt |
| 主服务（开发） | `http://dev-api.example.com` | debug | common/.../AppConfig.kt |
| AI 图像 vendor-A | `https://image-api.vendor-a.com` | production | feature_image/.../ImageService.kt |
| LLM vendor-B | `https://llm-api.vendor-b.com/v3/chat/completions` | production | common/.../LlmClient.kt |
| *（其余 base URL 略）* | | | |

## 网络层架构摘要

- **拦截器栈**（自有业务实例）：`CommonRequestInterceptor` → `RequestInterceptor`（Token 注入 + 自定义签名）→ `ResponseInterceptor`（隐式 unwrap data）→ `HttpLogInterceptor`
- **签名链路 ≥ 2 套并存**：自有业务签名（MD5/SHA1 **大写** hex）+ AI 图像 vendor-A（AWS-style HMAC-SHA256 + 强制 4 个 Header）+ LLM vendor-B（Bearer Token）
- **响应包装**：自有业务为 `{code, msg, data: {status, toastMsg, ...}}` 双层信封；三方厂商各自不同
- **客户端方法名 ≠ 服务端 path**：例 `bindMobile()` → `/user/bindMobileBySmsCode`，必须以服务端真实 path 为准

> 细节全在 [common.md](common.md)。

## 第三方 API

> 5 个 provider，此处只展示 1 个代表性 provider 的索引项；详细 endpoints 见 JSON 或真实产出的 `apis/` 下三方模块文件。

### AI 图像 vendor-A   *（示范性 provider）*

- **域名**：`image-api.vendor-a.com`
- **协议**：REST（Action 参数化）
- **认证**：AWS-style HMAC-SHA256（AccessKeyId + SecretAccessKey），Header: `X-Date / Authorization / X-Content-Sha256 / Host`
- **业务角色**：图像生成主引擎，所有图像 AI 功能通过 Action 参数复用这套 API
- **迁移关注点**：签名算法需用 HMOS 的 `@ohos.security.cryptoFramework` 重写；HMAC algName 用 `'HMAC'` 无后缀（详见 `arkts-network-troubleshoot` pitfalls A2）

*（其余 4 个 provider：LLM vendor-B、TTS vendor-C、分析 vendor-D、OAuth provider —— 真实产出按相同格式列出）*

---

## Feature 候选 / 覆盖度分析

> 本项目 spec 已生成（分支 A），coverage `_mode: audit`，主要填 gaps；
> 若 spec 尚未生成（分支 C），此节改为「Feature 候选建议」。

- Spec 中已记录：**36** 个端点
- 扫描发现：**72** 个端点
- 差异（`missing_in_spec`）：**36** 个（真实产出列出全部并给补录建议；此处略）

代表性 gap 示例（仅 3 条）：

| 端点路径 | 类型 | 说明 |
|---------|------|------|
| `/app/appLog` | missing_in_spec | 应用日志上报 — 基础设施层接口，建议归入对应 feature 补录 |
| `/anti/textCheat` | missing_in_spec | 文本内容安全检测 — 合规接口，spec 未记录 |
| `/push/getuiCid` | missing_in_spec | 推送 ClientID 上报 — 在两个 Service 中重复定义，需确认去重 |

完整 gaps + 补录建议见 `api-inventory.json` 的 `coverage.gaps`。

---

## 如何使用这个示例

1. **结构层面参考**：看分层怎么组织、每个文件放什么；尤其看 [apis/user.md](apis/user.md) 学 endpoint 统一模板
2. **格式层面参考**：看 [common.md](common.md) 怎么写公共约定、`apis/*.md` 怎么写「端点速览表 + 统一展开」
3. **不要参考**：具体的 Feature ID、接口描述措辞、第三方 provider 名 —— 这些都是占位
4. **不要照搬章节顺序**：你的项目若 spec 尚未生成（分支 C），「覆盖度分析」要换成「Feature 候选建议」；若是 SDK 主导项目，章节要重新组织（见 `references/output_schema.md` 场景说明）
5. **判定单/分层**：端点 ≤ 15 时用单文件形态（不创建 `common.md` 与 `apis/`），见 SKILL.md §3.2
