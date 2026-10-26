# API Inventory 输出格式参考

本文档定义 `api-inventory.json` 和 `api-inventory.md` 的**推荐**字段和结构，两个平台（`android` / `harmony`）共用同一套 schema。

**重要**：这是参考，不是模板。模型应根据项目实际情况调整结构——例如离线项目不需要 `services`、SDK 主导项目需要额外的 `sdk_providers` 字段。字段命名和结构应当服务于该项目的文档表达，不要为了贴合 schema 而遗漏或编造信息。

**当前版本 v1.3**。Changelog：
- **v1.3**：新增三个顶层段 `auth_model`（鉴权链路结构化，登录打通的直接抓手）/ `data_flows`（endpoint→调用方→存储/UI 副作用的链路视图）/ `uncertainties[]`（②③类不确定项结构化清单，grill #2 C17 与 arkts-network-troubleshoot 销账的输入）；endpoint `static` 段新增 `static_headers` / `path_is_dynamic` / `callers`（可选）；Android scanner 泛化（Java Retrofit / @Url 动态端点 / @Headers / Android 侧 interceptors / body 组装点 / gradle 构建期注入 / 调用点回溯）
- **v1.2**：平台参数化（`platform: android | harmony`）+ 新增 HMOS scanner（`@kit.NetworkKit` / `ApiService` URL 常量 / `HttpInterceptor` / ArkTS Bean）+ Phase 2.5 HarmonyOS 等价物预标注（消费 `hmos_references_file`，仅追加 markdown 段、不动 JSON schema）
- **v1.1**：每个 endpoint 升级为三段式 API contract（`static` / `runtime` / `reconciled`，详见下文）

**三段式 contract**：本 skill 只写 `static`，`runtime` / `reconciled` 一律置 `null`，由 `arkts-network-troubleshoot` 抓包 + DIFF 回填。

**v1.3 顶层段所有权**：`auth_model` / `data_flows` 由本 skill 写（Phase 2.75）；`uncertainties[]` 由本 skill 创建（Phase 3），但其 `status` / `resolution` / `resolved_by` 字段由下游更新——a2h-plan grill #2（C17 拷问后写 `answered` / `needs_capture`）与 `arkts-network-troubleshoot`（抓包/DIFF 实证后写 `resolved`）。这三段与 endpoint 三段式平级，不占用 `static` / `runtime` / `reconciled` 的所有权约定。

---

## api-inventory.json 推荐结构

```json
{
  "project": "项目名 (如 'meizhaoAI (AIImage)')",
  "platform": "android | harmony",
  "scan_time": "ISO 8601 时间戳",
  "source_root": "源码根路径（Android 工程根 或 HarmonyOS 工程根）",

  "project_profile": {
    "http_stack": "Retrofit+OkHttp | 裸OkHttp | Ktor | @kit.NetworkKit(http) | SDK主导 | 离线",
    "architecture": "多模块 | 单模块 | RN壳 | HSP分包",
    "primary_auth": "Token | AWS-style签名 | 自定义签名(ss/tt) | Bearer | 多套并存",
    "notes": "该项目的关键技术特征，影响文档组织方式"
  },

  "summary": {
    "total_services": 17,
    "total_endpoints": 97,
    "total_third_party_apis": 5,
    "total_params": 200,
    "modules": ["network", "pay", "..."]
  },

  "base_urls": [
    {
      "name": "常量/描述名",
      "url": "URL 值或动态配置来源",
      "environment": "production | debug | staging | unknown",
      "source_file": "相对路径:行号"
    }
  ],

  "services": [
    {
      "name": "Service 类名",
      "module": "所属模块",
      "file_path": "相对路径",
      "package": "Java/Kotlin 包名",
      "base_path": "公共路径前缀（推断）",
      "auth_type": "Token | Custom | None | ...",
      "auth_detail": "认证机制详细说明",
      "endpoints": [
        {
          "endpoint": "POST /user/initUser",
          "static": {
            "method_name": "Kotlin/Java/ArkTS 方法名",
            "http_method": "GET | POST | PUT | DELETE | PATCH",
            "path": "解析后的实际路径",
            "protocol": "REST | SSE | WebSocket | gRPC",
            "description": "中文功能说明（模型根据上下文推断）",
            "is_suspend": true,
            "is_multipart": false,
            "path_is_dynamic": false,
            "static_headers": ["Content-Type: application/json"],
            "callers": ["UserRepository.login (app/.../UserRepository.kt:8)"],
            "line_number": 16,
            "feature_ids": ["F002"],
            "request": {
              "content_type": "application/json",
              "params": [
                {
                  "name": "参数名",
                  "type": "数据类型",
                  "annotation": "Field | Body | Query | Path | Part | Header",
                  "serialized_name": "JSON 序列化名（ArkTS 无 @SerializedName 时即字段名）",
                  "required": true,
                  "description": "参数含义（模型推断）"
                }
              ]
            },
            "response": {
              "type": "返回类型声明",
              "model_class": "响应 Bean 类名（强制；读不到时填 unknown + 原因）",
              "fields": [
                {
                  "json": "JSON 字段名",
                  "name": "Bean 字段名（Android 来自 @SerializedName；ArkTS 即 json 名）",
                  "type": "类型",
                  "description": "含义"
                }
              ]
            }
          },
          "runtime": null,
          "reconciled": null
        }
      ]
    }
  ],

  "third_party_apis": [
    {
      "provider": "第三方服务商中文名",
      "domain": "域名",
      "protocol": "REST | SSE | WebSocket | gRPC",
      "auth_type": "AWS-style | Bearer | API-Key | OAuth | Custom",
      "auth_detail": "认证算法细节、Header 要求",
      "endpoints": [
        {
          "description": "接口用途",
          "http_method": "POST",
          "full_url": "完整 URL（含参数化部分）",
          "feature_ids": ["F003"]
        }
      ]
    }
  ],

  "url_constants": [
    {
      "constant_ref": "如 UserUrl.initUser",
      "resolved_value": "/user/initUser",
      "file_path": "定义位置",
      "line_number": 15
    }
  ],

  "coverage": {
    "_mode": "audit | incremental | candidate",
    "spec_documented": 36,
    "inventory_found": 72,
    "gaps": [
      {
        "type": "missing_in_spec | missing_in_scan | pending_in_spec",
        "endpoint": "路径或标识",
        "detail": "说明",
        "suggestion": "补录建议（可选）"
      }
    ],
    "feature_candidates": [
      "// ONLY present when _mode == 'candidate' (spec 尚未生成)",
      "// 此时 gaps 数组通常为空，coverage 的主要价值是提供 feature 聚类建议",
      {
        "suggested_id": "F-user",
        "suggested_name": "用户认证与账号",
        "path_prefixes": ["/user/", "/app/sendSmsCode"],
        "endpoint_count": 12,
        "third_party_deps": ["WeChat OAuth"],
        "migration_concerns": ["多家三方账号绑定认证流程各异"]
      }
    ]
  }
}
```

### endpoint 三段式 API contract（v1.1）

每个 endpoint 是一份可验证的 API 契约，三段、字段所有权清晰（两个 skill 不抢写同一段）：

| 段 | 写入者 | 时机 | 内容 |
|----|--------|------|------|
| `static` | 本 skill（`android-api-inventory`） | Phase 3 | 源码静态推断的契约形状（即上文 `endpoints[].static` 全部字段） |
| `runtime` | `arkts-network-troubleshoot` | 其 Phase 0.3 抓包后 | 抓真包得到的运行期实况；未抓则保持 `null` |
| `reconciled` | `arkts-network-troubleshoot` | 其 Phase 1.7 DIFF | `static` ↔ `runtime` 比对结果 |

`endpoint` 字段是 join key，取 `"<HTTP方法> <path>"`（如 `"POST /user/initUser"`），下游按它定位回填。本 skill 产出时 `runtime` / `reconciled` 一律为 `null`。

**`runtime` 段结构**（由 network-troubleshoot 回填）：

```json
"runtime": {
  "captured_at": "ISO 8601 时间戳",
  "source": "method-A-logcat | method-C-proxy",
  "response_wrapper": "{code,msg,data} | {status,toastMsg,data} | flat",
  "business_code": { "field": "status", "success_value": 0 },
  "field_types": [
    { "json": "userId", "observed_type": "int", "sample": 12345, "default": -1 }
  ],
  "headers": [
    { "name": "ss", "note": "签名头，hex 大写，32 字符" }
  ]
}
```

**`reconciled` 段结构**（由 network-troubleshoot 的 DIFF 回填）：

```json
"reconciled": {
  "status": "verified | mismatch | static-only",
  "diffed_at": "ISO 8601 时间戳",
  "discrepancies": [
    {
      "dimension": "response-wrapper | field-name | field-type | business-code | auth-header",
      "static": "源码侧的值",
      "runtime": "抓包侧的值",
      "impact": "对实现的影响 / 该按哪边为准"
    }
  ]
}
```

- `status` 三态：`verified`（runtime 已抓且与 static 一致）/ `mismatch`（已抓且有差异，差异入 `discrepancies`）/ `static-only`（runtime 仍为 `null`，未抓、无法验证）。
- 大量 endpoint 会停在 `static-only` —— 闭环天生**部分闭合**（runtime 需设备 + 能触发该 endpoint），这是设计内的状态，不是缺陷。

### v1.3 顶层段一：auth_model（鉴权链路结构化）

**为什么需要**：login.md 复盘证明，登录打不通的缺口不在接口清单，而在机制层——token 从哪来、存哪、谁注入、什么码判失效、失效做什么、身份模型是什么。这些藏在拦截器和基类里，v1.3 把它们抽成一等公民段。**每个字段读不到就显式填 `unknown` + 建 uncertainty，不许省略字段。**

```json
"auth_model": {
  "identity_model": "device-bound | account-only | none | unknown",
  "identity_notes": "业务语义说明（如：游客登录=用设备身份登录而非新建游客；设备首绑手机号后不可回游客态）",
  "axis_a_guest_token_role": "persistent-baseline | one-shot-antifraud | none | unknown",
  "axis_b_device_role": ["identity-basis | request-trust-component | irrelevant | unknown"],
  "axis_c_login_methods": ["sms", "onekey", "thirdparty", "password"],
  "token_acquisition": [
    { "endpoint": "POST /user/initUser", "grants": "guest token", "trigger": "冷启动" },
    { "endpoint": "POST /user/loginBySmsCode", "grants": "bound token", "trigger": "用户登录" }
  ],
  "token_storage": { "keys": ["token", "userData"], "layer": "MMKV | SharedPreferences | 内存", "source": "文件:行号" },
  "token_injection": { "via": "拦截器类名", "position": "header | body", "names": ["token", "ss", "tt"], "source": "文件:行号" },
  "token_expiry": { "codes": [-1001], "scope_rule": "失效码的适用范围（如 guest 态 -1001 不清 token）", "action": "清 token / 跳登录 / 广播", "source": "文件:行号" },
  "token_clearing": [ { "trigger": "退出登录 | 注销 | 被踢", "clears": ["token"], "keeps": ["deviceNo"] } ],
  "irreversibles": ["一旦发生即永久的单向边（如设备首绑手机号后不可回游客态）"],
  "uncertainty_refs": ["U-003"]
}
```

- 素材来源：raw_apis.json 的 `interceptors`（evidence 标签指路）+ `api_related_constants[code]`（失效码）+ `endpoints[].callers`（token 写入点）+ 模型读拦截器/Repository 源码。
- `identity_model`：`device-bound` = 设备身份永久绑定（游客登录拿回原身份）；`account-only` = 纯账号态；判不出填 `unknown` 并建 uncertainty（tag ②，需真机验证或问后端）。
- **轴 A/B/C（变化轴分类，Phase 2.8 数据链路契约的分支依据）**——它们把已隐含的机制显式化，供 `chain-auth` 投影与完备性核对：
  - `axis_a_guest_token_role`：游客/设备 token 角色。`persistent-baseline`=进 Header、是所有业务请求默认身份；`one-shot-antifraud`=仅发码/注册防刷、用完即弃；`none`=无游客 token（游客=本地跳转）。
  - `axis_b_device_role`：设备身份对登录的作用（**数组、可同时占前两个**，如 deviceNo 既是身份又进签名）。`identity-basis`=换游客/设备 token；`request-trust-component`=进签名或防重放头；`irrelevant`=与登录无关。
  - `axis_c_login_methods`：登录方式子集（`sms`/`onekey`/`thirdparty`/`password`…）。
  - 三者**读不到填 `unknown` 并建 uncertainty**（同 identity_model 约定）；对不上任何已知分支 → 建 uncertainty 冒泡（novelty 逃逸口，勿硬套）。
- 落 `common.md` §鉴权链路（人类可读投影）；轴分类同时供 Phase 2.8 生成 `data-chains/chain-auth.md`。

### v1.3 顶层段二：data_flows（数据链路视图）

endpoint 级 contract 回答"接口长什么样"，`data_flows` 回答"数据怎么流"。**`chain: "auth"` 必产**；其他链路按 `feature_candidates` 的重要度可选产出（建议覆盖支付、启动配置）。

```json
"data_flows": [
  {
    "chain": "auth",
    "endpoints": ["POST /user/initUser", "POST /user/loginBySmsCode"],
    "narrative": "LoginViewModel → UserRepository.login → UserService.loginBySmsCode → TokenStore.save → EventBus USER_DATA_UPDATE → 「我的」Tab 刷新",
    "storage_effects": [
      { "key": "token", "layer": "MMKV", "written_by": "UserRepository.login", "cleared_by": "UserRepository.forceLogout" }
    ],
    "ui_effects": ["登录态组件刷新（@StorageProp userData）"],
    "source_evidence": ["app/.../UserRepository.kt:8"]
  }
]
```

- 素材来源：raw_apis.json 的 `endpoints[].callers`（调用点回溯）+ `body_assembly_sites`（请求组装位置）+ 模型顺调用链读源码。
- `endpoints` 用三段式 contract 的 join key（`"<HTTP方法> <path>"`）关联。

### v1.3 顶层段三：uncertainties[]（不确定项清单 —— grill 与销账的输入）

**分级铁律**（沿用 `arkts-network-troubleshoot` 决策清单的 ①②③ 标签体系）：
- `①源码可定` —— **不入清单**。模型自答直接写进 `static` / `auth_model`。
- `②需真包` —— 源码推不准、需抓包或后端证据（响应壳形状、字段真实类型、业务码语义、header 大小写……）。
- `③策略待确认` —— 无唯一正确答案、涉策略/后端协调（包标识发哪个包名、联调期加密开关、多网关取舍……）。

```json
"uncertainties": [
  {
    "id": "U-001",
    "tag": "②需真包 | ③策略待确认",
    "chain": "auth",
    "scope": "endpoint | auth_model | data_flow | common | chain-owner",
    "endpoint": "POST /user/loginBySmsCode",
    "question": "响应壳是 {code,msg,data} 还是 {status,toastMsg,data}？",
    "why": "Bean 是扁平的，但 ResponseInterceptor 有 body 改写迹象",
    "candidates": ["{code,msg,data}", "{status,toastMsg,data}"],
    "impact": "HttpClient.unwrap 方向 + isResponseSuccess 判定",
    "status": "open",
    "resolution": null,
    "resolved_by": null
  }
]
```

**status 状态机与写入者**：

| 状态 | 含义 | 写入者 |
|------|------|--------|
| `open` | 初始，未有答案 | 本 skill（Phase 3 创建；若 `backend_facts_file` 已能回答则直接建为 `answered`） |
| `answered` | 用户/文档给出答案（`resolution` 填答案，`resolved_by` 填来源） | a2h-plan grill #2 C17（或本 skill 消费 backend_facts 预销账） |
| `needs_capture` | ② 类无证据可答，待真机抓包 | a2h-plan grill #2 C17 |
| `resolved` | 抓包/DIFF 实证闭环（`resolved_by` 填 `runtime <endpoint> @日期`） | `arkts-network-troubleshoot` Phase 0.3 / 1.7 |

- `chain` 字段用于 grill 按链路打包呈现（auth 链最优先）；取值 `auth` 或 `feature_candidates` 的 `suggested_id`。
- `endpoint` 为 join key（`scope: endpoint` 时必填），供 troubleshoot 抓包销账时定位。
- `scope: chain-owner` = Phase 2.8 `chain-auth` 交叉核出的**非 API 层 owner 缺失**（如 feature-index 无 feature owns L1 隐私门控 / L0 应用身份）——auth_model 不覆盖的层，由数据链路契约冒泡；grill 兜底问。
- 人类可读投影落 `api-inventory.md` 的「## 不确定项清单（grill 输入）」段：`id | tag | 链路 | 问题 | 状态` 表。

### coverage 的三种模式说明

- **`audit`**（分支 A）：spec 完整，做审计对比。`gaps` 填 `missing_in_spec` / `missing_in_scan`；`feature_candidates` 省略。
- **`incremental`**（分支 B）：spec 生成中。`gaps` 可含 `pending_in_spec`（feature-index 列了但文件还没生成的）；两个字段都可以有内容。
- **`candidate`**（分支 C）：spec 尚未生成，本 skill 作为 spec 生成的输入源。`gaps` 通常为空，主要填 `feature_candidates`。

### 可选扩展字段（根据项目需要添加）

- `websockets`: WebSocket 连接清单（url、消息协议、用途）
- `sse_streams`: SSE 流式接口清单
- `sdk_providers`: SDK 封装的对外接口（如 twitch4j 暴露的方法）
- `graphql_queries`: GraphQL query/mutation 列表
- `local_system_apis`: 离线项目的系统 API 依赖（ContentResolver 等）

---

## api-inventory 文档结构（分层）

人类可读文档按项目规模分层产出。拆分判定见 SKILL.md §3.2，本节给出**结构清单**与**每个 endpoint 的统一模板**。

### 拆分判定

| 规模 | 形态 |
|------|------|
| 端点 ≤ ~15 或单 service | 单文件 `api-inventory.md`（内部含 endpoint 模板 + 一个「公共约定」段） |
| 端点 > ~15 或多 service | 分层：`api-inventory.md` + `common.md` + `apis/*.md` |
| 离线 / 无外部 API | 单文件 `api-inventory.md`，说明无外部 API + 列系统级依赖 |

### 分层形态的文件结构

```
spec/baseline/api-inventory/
├─ api-inventory.json   机器可读（三段式 contract，唯一事实源）
├─ api-inventory.md     总览索引
├─ common.md            公共约定
├─ apis/
│  ├─ <模块1>.md         每个 service/功能域一文件
│  └─ <模块2>.md
└─ raw_apis.json        原始扫描
```

`api-inventory.md`（总览索引）章节：

```
# API Inventory - <项目名>
## 概览                  技术栈 + 数据总览（service 数 / 端点数 / 第三方数 / runtime 覆盖）
## 文档导航              表格：链接到 common.md 与各 apis/*.md，标端点数 + runtime 已抓数
## Base URL              环境、第三方独立 URL
## 网络层架构摘要         拦截器 / 客户端 / 签名概述（细节在 common.md）
## 第三方 API            按 provider 分组
## Feature 候选 / 覆盖度  分支 C 填候选；分支 A/B 填覆盖度分析
## 不确定项清单（grill 输入）  v1.3：uncertainties[] 的人类可读投影（id | tag | 链路 | 问题 | 状态），auth 链路置顶
```

`common.md`（公共约定）章节（注释里标出每节的 raw_apis.json 数据来源）：

```
# 公共约定（common）
## 通道与 BaseURL                ← raw_apis.json: base_urls（含 build-config 动态来源）+ gradle_config + 模型推断
## 签名头 / 鉴权头                ← raw_apis.json: interceptors（两平台均有）+ api_related_constants[header]
## 鉴权链路（auth_model 投影）     ← api-inventory.json: auth_model（token 获取/存储/注入/失效/清除 + 身份模型）
## App 凭证 / 第三方 AppKey       ← raw_apis.json: api_related_constants[app_secret]
##                                  ⚠ 含 secret 类按敏感级别决定是否仅留名 + 不落值
## 公共请求参数（platformInfo 等） ← raw_apis.json: api_related_constants[param] + body_assembly_sites + 模型推断
## 响应信封                       ← 模型推断 + reconciled.runtime.response_wrapper（回填后刷）
## 业务状态码                     ← raw_apis.json: api_related_constants[code]
## 共享响应体（多端点复用 Bean）   ← raw_apis.json: bean_classes（HMOS）+ 模型读 Bean（Android）
## 抓包状态标记说明                verified / mismatch / static-only
```

### raw_apis.json 字段 → 文档落点（Phase 3 写 md 时按此分流）

脚本产出的每个 raw_apis.json 字段都有明确的文档落点。下表是**规范约定**，不是建议；模型在 Phase 3 写 md 时按这张表分流，不靠直觉。

| raw_apis.json 字段（脚本产出） | 主要落点 | 备注 |
|---|---|---|
| `services[].endpoints[]` | `api-inventory.json`（包成三段式 `{endpoint, static, runtime:null, reconciled:null}`）+ `apis/<模块>.md`（按下方 endpoint 统一模板展开）| 主体 |
| `base_urls` | `api-inventory.md` §Base URL + `common.md` §通道与 BaseURL | 双向写 |
| `url_constants` | **不直出文档**；仅作为 endpoint path 的 `resolved_path` 解析依据 | 内部 |
| `hardcoded_urls` / `third_party_domains` | `api-inventory.md` §第三方 API（按 provider 聚合）| 模型命名 provider |
| `api_related_constants[header]` | `common.md` §签名头 / 鉴权头 | 写 `header 名 \| 含义 \| 何时出现` 表 |
| `api_related_constants[app_secret]` | `common.md` §App 凭证 / 第三方 AppKey | ⚠ 仅落**名**，**不落值**（避免凭证进 spec 仓）|
| `api_related_constants[code]` | `common.md` §业务状态码 | 写 `code \| 名 \| 含义 \| 处理建议` 表 |
| `api_related_constants[param]` | 多端点复用 → `common.md` §公共请求参数；仅单端点引用 → 留 `apis/<模块>.md` 端点请求表 | 按引用频次分流 |
| `api_related_constants[other]` | 按文件路径与上下文判 —— 落 `common.md` 末尾「其它常量」节，或舍弃（无下游消费意义时）| 分类兜底桶 |
| `interceptors`（v1.3 起两平台均有）| `common.md` §签名头 / 鉴权头 + **Phase 2.75 `auth_model` 的首要素材**（evidence 标签指路：token_injection / signing / logout_kick / body_rewrite）| Android 侧 v1.3 新增 |
| `bean_classes`（HMOS scanner 专有）| 跨端点共享 → `common.md` §共享响应体；单端点专用 → `apis/<模块>.md` 该端点 response 表 | 按引用频次分流 |
| `body_assembly_sites`（v1.3，Android）| 对应 endpoint 的请求参数表补全（Retrofit 接口外组装的字段，如 `"source" to 1` 常量字段）+ 多端点复用的 → `common.md` §公共请求参数 | 防 D3 漏抽 |
| `gradle_config`（v1.3，Android）| `common.md` §通道与 BaseURL（buildConfigField 域名）+ `api-inventory.md` 概览（flavor/applicationId 提示）| 构建期注入 |
| `endpoints[].callers`（v1.3，Android）| Phase 2.75 `data_flows` 的链路素材 + endpoint 模板「调用位置」行 | 调用点回溯 |
| `endpoints[].static_headers`（v1.3）| endpoint 的 `static.static_headers` + 多端点复用的 → `common.md` §签名头 / 鉴权头 | @Headers 注解 |

**分流的判定标尺（重要）**：

- **公共 vs 专属** = 相同 `name` 在 raw_apis.json 中跨 ≥ 2 个 endpoint 引用 → 公共；< 2 → 专属。
- **app_secret 落值** = 默认**只写名**；若 secret 长度短、是公开常量（如 weixinAppId）且本仓可公开，可写值并标注；含 token/secret 关键字默认不落值。
- **other 兜底** = 不强求每条都落地；分类兜底桶意味着「模型不确定时先收进来，写文档时按上下文取舍」，可以整体舍弃。
- **单文件形态时** = 所有上述「→ common.md」的内容并到单 `api-inventory.md` 内的「公共约定」段；表头与字段表照上方约定。

`apis/<模块>.md`（每模块详细文档）结构：

```
# <模块名> 接口（<ServiceClass>）
> 模块 / 文件 / 端点数 / 通道；公共约定见 ../common.md
## 端点速览              表格：方法 | 路径 | 接口名 | runtime 状态
## <endpoint 1>          按下方「endpoint 模板」展开
## <endpoint 2>
...
```

### 每个 endpoint 的统一模板（强制）

```markdown
## {序号}. {method_name} — {description}

- **方法**：`{HTTP方法} {path}`（+ 协议 REST/SSE/WebSocket）
- **Service**：`{ServiceClass}.{method}`（{file}:{line}）
- **认证**：{摘要} → 见 [common.md](../common.md)
- **runtime**：⬜ static-only / ✅ verified / ⚠️ mismatch
- **特殊标注**：suspend / multipart / 分页 / 轮询（按需）

**请求参数**

| 参数 | 类型 | 必需 | 说明 |
|------|------|:--:|------|
| {业务字段} | {类型} | 是/否 | {含义} |
| _(公共)_ | — | — | + {公参对象} → 见 common.md |

**响应参数**：`{model_class}`

| 字段 | 类型 | 说明 |
|------|------|------|
| {字段} | {类型} | {含义} |
```

模板要点：

- **响应强制表格化**：每个 endpoint 的响应必须是 `字段 | 类型 | 说明` 表格；嵌套 Bean 逐层展开为子表；读不到 Bean 时 `model_class` 标 `unknown` + 原因，**不省略响应段**。
- **共享响应体**（如 `UserData`，被多端点复用）写「→ 见 common.md」引用，不在各处重复字段表。
- **请求公参**（如 `platformInfo`）只在 `common.md` 写字段表，endpoint 表里用一行 `_(公共)_` 引用。

### 「合并一类」与 runtime 标记

- **合并一类**：重复出现的请求公参、共享响应体、信封 / 签名 —— 只在 `common.md` 写一次，`apis/*.md` 链接引用。这是分层的核心收益。
- **runtime 标记**：本 skill（`android-api-inventory`）产出时所有 endpoint 标 `⬜ static-only`；`arkts-network-troubleshoot` 抓包回填 `api-inventory.json` 的 `runtime`/`reconciled` 后，**同步刷新** `apis/*.md` 的标记为 `✅ verified` / `⚠️ mismatch`，差异处就近标注并链到其 `api-contract-diff.md`。
- 人类可读文档（md 集）是 `api-inventory.json` 的**投影**；json 变更后 md 应随之刷新。

### 单文件形态（小项目）

端点少时不分层，单 `api-inventory.md` 即可，章节：概览 → Base URL → 公共约定（信封/签名/公参/共享 Bean）→ 按 service 分组的 endpoint（用上述统一模板）→ 第三方 API → Feature 候选 / 覆盖度。离线项目则说明无外部 API + 列系统级依赖。

---

## 字段填写职责划分

| 字段 | 填写者 | 说明 |
|------|--------|------|
| `platform` | 脚本 | 本次扫描平台（android \| harmony） |
| `services[].name/file_path/module/package` | 脚本 | 从 raw_apis.json 直接取 |
| `services[].endpoints[].endpoint`（join key） | 脚本 | `"<HTTP方法> <path>"` |
| `services[].endpoints[].static.method_name/http_method/path` | 脚本 | 含 resolved_path |
| `services[].endpoints[].static.request.params[].name/type/annotation` | 脚本 | 从注解 / 调用点提取 |
| `url_constants` | 脚本 | 已自动解析 |
| `hardcoded_urls`（在 raw_apis.json） | 脚本 | 供 模型识别第三方 |
| **`project_profile`** | 模型 | 从项目整体理解 |
| **`services[].auth_type/auth_detail`** | 模型 | 读 Interceptor 源码推断 |
| **`services[].base_path`** | 模型 | 从端点路径归纳 |
| **`services[].endpoints[].static.description`** | 模型 | 根据方法名+参数+调用上下文 |
| **`services[].endpoints[].static.protocol`** | 模型 | 识别 SSE/WebSocket 等 |
| **`services[].endpoints[].static.feature_ids`** | 模型 | 读 feature specs 关联 |
| **`services[].endpoints[].static.request.params[].required/description`** | 模型 | 从源码注释或业务推断 |
| **`services[].endpoints[].static.response`** | 模型 | **强制**：读 Bean 展开 `model_class` + 字段表；读不到填 `unknown` + 原因 |
| **`third_party_apis`** | 模型 | 按 provider 聚合分组 |
| **`coverage`** | 模型 | 集合差集+业务判断 |
| **`auth_model`**（v1.3） | 模型（Phase 2.75） | 读 interceptors + callers + 常量码推断；读不到的字段填 `unknown` + 建 uncertainty |
| **`data_flows`**（v1.3） | 模型（Phase 2.75） | 基于 callers / body_assembly_sites 顺链读源码；`chain: auth` 必产 |
| **`uncertainties[]`**（v1.3） | 模型（Phase 3 创建） | 仅 ②③ 类入清单；`status`/`resolution` 由 grill #2 与 arkts-network-troubleshoot 更新 |
| `services[].endpoints[].runtime` | — | 本 skill **置 `null`**；由 `arkts-network-troubleshoot` 抓包回填 |
| `services[].endpoints[].reconciled` | — | 本 skill **置 `null`**；由 `arkts-network-troubleshoot` DIFF 回填 |

---

## 质量检查清单

生成完文档后，模型应自检：

- [ ] `platform` 字段是否填写（android | harmony）？
- [ ] `project_profile.http_stack` 与实际情况是否匹配？
- [ ] 每个 endpoint 是否为三段式（`static` / `runtime: null` / `reconciled: null`），`endpoint` join key 是否为 `"<方法> <path>"`？
- [ ] `runtime` / `reconciled` 是否都置 `null`（本 skill 不代下游 skill 填）？
- [ ] **`api_related_constants` 五桶**是否按落点表分流到 `common.md`（`header` → §签名头 / 鉴权头；`app_secret` → §App 凭证（含 secret 字样的**仅落名**）；`code` → §业务状态码；`param` 多端点复用的 → §公共请求参数；`other` → §其它常量或舍弃）？
- [ ] 每个 endpoint 是否有中文 description（即使是简短一句）？
- [ ] **每个 endpoint 的 `static.response` 是否填写**（`model_class` + 字段表；读不到的填 `unknown` + 原因，不能整段省略）？
- [ ] 所有第三方域名是否都聚合到 `third_party_apis` 里，并识别了 provider？
- [ ] auth_type 是否填写？有多套并存时是否分别标注？
- [ ] SSE / WebSocket / 特殊协议是否单独标注？（迁移难点）
- [ ] URL 常量里出现的 `${xxx}` 模板变量，是否在文档里解释了含义？
- [ ] coverage.gaps 是否真的有实际意义（不是路径拼写差异导致的假差异）？
- [ ] **`auth_model` 是否产出**（platform: android 时必产；每个字段读不到填 `unknown` + 建 uncertainty，不许省略字段）？
- [ ] **`auth_model` 的轴 A/B/C 是否产出**（`axis_a_guest_token_role` / `axis_b_device_role` / `axis_c_login_methods`；读不到填 `unknown` + 建 uncertainty；对不上已知分支即 novelty 冒泡）？
- [ ] **`data_flows` 是否至少含 `chain: auth`**（登录/鉴权链路是打通目标，不可选）？
- [ ] **`uncertainties[]` 是否只收 ②③ 类**（① 源码可定的应模型自答写进 static/auth_model，不许甩给用户）？每条是否有 `chain` 归属与 `impact` 说明？
- [ ] `backend_facts_file` 提供时，能直接回答的 uncertainty 是否已建为 `answered`（预销账，不留给 grill 重复问）？
- [ ] 文档结构是否贴合项目特点，而不是生硬套模板？
