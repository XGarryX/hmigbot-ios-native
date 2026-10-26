# 分层产出骨架示例（layered skeleton）

> **Schema 版本**：v1.2（platform 参数化 + project_profile + 三段式 contract）
> **形态**：分层（`api-inventory.md` 总览索引 + `common.md` 公共约定 + `apis/<模块>.md` 模块明细）
> **代表场景**：Retrofit + 多模块 + ≥ 2 套签名链路 + 多家第三方 SDK

---

## 文件清单

```
example-layered/
├─ README.md             ← 本文件（定位说明）
├─ api-inventory.json    机器可读骨架（v1.2 三段式 contract，含 project_profile）
├─ api-inventory.md      分层总览索引骨架（章节齐全，每章内容裁剪到示意）
├─ common.md             公共约定骨架（通道 / 签名 / 公参 / 信封 / 业务码 / 共享 Bean）
└─ apis/
   └─ user.md            代表性模块骨架（端点速览表 + 2 个 endpoint 完整展开，含 mismatch 演示）
```

真实产出还会有 `apis/<其他模块>.md` 等其余模块文件 + `raw_apis.json`，此处只裁到 `apis/user.md` 一个模块作代表，避免重复。

## 为什么是骨架而非完整产出

完整产出 ~170KB（md 集合 ~1100 行 + json ~4000 行），如果全量保留有两个问题：

1. **阅读成本高** —— 模型下次跑时不需要把全量内容读进上下文
2. **会诱导模仿** —— 模型可能潜意识照搬具体的 Feature ID 映射、中文措辞、第三方分组 ——
   违背「项目定制」的本意

所以这里只保留：

- 完整的**分层结构**（让你知道分层下文件该长什么样）
- 完整的**章节骨架**（每章保留，但内容裁剪到示意）
- 1 个完整代表模块（[apis/user.md](apis/user.md)），展示统一 endpoint 模板 + runtime mismatch 写法
- JSON 1 service / 3 endpoints + 1 provider 完整数据（含 initUser 的 runtime/reconciled 已回填演示）

如需看真实完整产出，跑 skill 自己生成；裁剪示例不是用来直接拷贝的。

## 代表的项目画像

来自 JSON 的 `project_profile` 字段（v1.2 新增）：

```json
{
  "http_stack": "Retrofit+OkHttp",
  "architecture": "多模块（多个 Gradle module，按业务域拆分）",
  "primary_auth": "多套并存（自有 Token + 自定义签名 ss/tt / 第三方 A AWS-style HMAC / 第三方 B Bearer Token）",
  "notes": "RxJava2 与 Kotlin coroutines 混用；中型项目结构（端点 ~100、Service ~17、多家第三方 SDK）"
}
```

- **规模**：示例数据假设 17 Service / 97 endpoints / 5 个第三方 provider → 端点 > 15，按 SKILL.md §3.2 **强制走分层形态**
- **关键迁移点**：≥ 2 套签名链路 hex 大小写不同 / 双层响应信封 / 客户端方法名 ≠ 服务端 path（pitfall D2 典型症状）

## 适合参考这个骨架的项目类型

- ✅ Retrofit + 多模块 + 多家第三方 SDK（中型 AI / 工具 / 内容类应用都适用）
- ✅ 端点数 > 15、按业务域分模块的项目

不适合直接套用的场景：

- ❌ 端点 ≤ 15 / 单 Service → 用 **单文件** `api-inventory.md`（章节顺序也不同，见 SKILL.md §3.2）
- ❌ SDK 黑盒主导 → 章节按 SDK 暴露的接口重新组织，见 `references/output_schema.md` 场景说明
- ❌ 离线 / 无外部 API → 单文件 + 系统级依赖列表
- ❌ React Native / Flutter 壳 → 本 skill 不适用，需在 JS / Dart 层重跑

## 阅读顺序建议

1. 先看 [api-inventory.md](api-inventory.md) —— **分层总览索引**长什么样
2. 再看 [common.md](common.md) —— **公共约定怎么合并一类**
3. 再看 [apis/user.md](apis/user.md) —— **模块文件怎么用统一 endpoint 模板**，含 mismatch 写法
4. 看 [api-inventory.json](api-inventory.json) —— **三段式 contract** 数据骨架，对照 `static` / `runtime` / `reconciled` 三段
5. 对照 [../output_schema.md](../output_schema.md) —— **字段定义与职责划分**的权威文档（含 changelog）

## v1.2 新增点速查

对比 v1.1，本骨架新增：

| 新增点 | 体现位置 |
|--------|---------|
| `platform` 字段 | `api-inventory.json` 顶层 `"platform": "android"` |
| `project_profile` 段 | `api-inventory.json` 顶层（本示例已填充）|
| HMOS scanner | 本示例是 `platform: android`；schema 一致，仅 scanner 不同 |
| Phase 2.5 HMOS 等价物提示 | 本示例未触发（要求 `hmos_references_file` 输入）；触发时会在 `api-inventory.md` 末尾追加段 |

## 关于「分层 vs 单文件」的判定

按 SKILL.md §3.2：

| 项目规模 | 形态 | 文件 |
|---------|------|------|
| 端点 ≤ ~15，或单 service | **单文件** | 只产 `api-inventory.md`（内部含 endpoint 统一模板 + 一个「公共约定」段）|
| 端点 > ~15，或多 service | **分层**（本示例）| `api-inventory.md` + `common.md` + `apis/*.md` |
| 离线 / 无外部 API | **单文件** | 说明无外部 API + 列系统级依赖即可 |

`api-inventory.json` 在三种形态下都产出，是机器可读唯一事实源。
