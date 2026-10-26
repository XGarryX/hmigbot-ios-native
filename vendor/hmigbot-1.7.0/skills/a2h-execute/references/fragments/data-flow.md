# data-flow — 数据层接入闭环

> 来源：830 `agent-prompts/6-step3c-data.md` 与 `5-step3b-vm.md`。

## 四段闭环，缺一段即未完成
```
UI  ←  ViewModel  ←  Repository  ←  API / DB
```
- Repository / Service 按需创建，先复用 infra 已落公共能力（网络客户端、存储封装、模型），不在域内重造；契约里标 `planned` 的模块照签名调用，禁本地重实现。
- ViewModel 只调 Repository，不直接发请求、不直接读库。
- 数据转换与缓存策略在 Repository 内收口。
- 验收口径 = 闭环通：UI 有绑定、VM 有状态、Repository 有真实调用。

## complex 域：三 role 对齐源码（任务书给 `android_source_anchors` / `source-notes` 时）
| role | 必须对齐 |
|---|---|
| `interceptor` | 拦截器链、header 注入、签名/加密算法——逐字对齐；签名错=全链 401 |
| `service` / `repository` | 每条通路独立实现，不合并、不省略分支 |
| `presenter` / `viewmodel` | 状态流转与触发时机 |

## JSON 字段改名
Gson/Moshi/Jackson `@SerializedName` 改名对必须逐条落 ArkTS 显式映射——`JSON.parse as T` 不改字段名，改名字段运行期静默 `undefined`。任务书注入的改名表逐条核对，不凭相似度猜。

## 多子仓：契约优先
有 `spec/baseline/module-dep-graph.json` 时，跨子仓 service/数据模型的签名与语义以 `cross-module-contracts.md`（被依赖子仓为 owner）+ 接口桩为准；契约缺失 → 摘要记 `decision_gaps`，不臆造。

## addenda 精读预算
AC 组带 `impl:` 指针时只精读目标 `§` 节：≤3 节 / ≤150 行，超出记 `deferred_addenda`；禁整目录扫读 addenda。
