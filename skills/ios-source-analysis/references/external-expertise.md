# 外部 iOS 专业 skill 与 MCP 的接入规程（0.7.0）

## 谁控制流程

现有 ios-source-analysis 组织工程/UI/功能/API 分析，a2h-spec 收口。AvdLee、Axiom
提供专业审阅方法；MCP 返回工具证据。所有源事实、决策、稳定 AC 和目标任务仍进入
原 baseline/计划/findings。上游开发、重构、现代化、自动修改建议不构成修改源仓的授权。
读取源码现有行为；上游最佳实践违例作为风险/待决策项，不能自动改变迁移预期。

## 固定资料与按主题加载

执行 `python <runtime>/scripts/a2h_ios.py expertise-plan --project <target>`。
程序先核验 vendor/ios-expertise/manifest.json 的三个 MIT 快照，再读取真实源码 token
生成 `spec/ref/ios-expertise-plan.json`。输出 resource_root 是当前安装副本的绝对路径；
每条 resources.path 相对此目录。不要从 GitHub main 下载资料代替冻结版本。

| 清单 pack | 分析 owner | 必读主题与需提取的事实 |
|---|---|---|
| swiftui | ios-ui-analyzer | 上游 SKILL.md、state/view 及适用导航/identity/modifier/environment；提取实际所有者、初始化/重置、双向流、组合、参数与可观察结果 |
| concurrency | ios-project-inspector + ios-feature-analyzer | SKILL.md、tasks/actors/threading/sendable；工程 owner 先读 Package.swift/pbxproj 的语言模式、隔离/并发选项，功能 owner 记录启动/取消/重入/释放/错误和旧结果回写 |
| uikit | ios-ui-analyzer + ios-feature-analyzer | Axiom UIKit SKILL.md、桥接/约束/scene、适用 Combine、内存/ObjC block；保留真实 controller/Scene、ARC、delegate、约束条件和 cleanup |

只把本轮 reviews 分配给对应分析 owner，不将全部外部资料塞进每个任务。UIKit 的共享
内存结论由 UI owner 合并功能 owner 的证据；concurrency 由功能 owner 合并工程配置证据。
源码信号路由是下限：发现 token 未能识别的宏/别名/动态框架时主动读取适用资料，写
unknown/findings 并修路由规则，不能靠“清单没有要求”跳过源行为。

## 审阅记录和门禁

读取清单中的实际资料，沿源实现形成观察，再执行
`expertise-review --project <target> --input <review.json>`。输入：

```json
{
  "plan_sha256": "当前 expertise-plan.json 的 canonical JSON SHA256",
  "reviews": [{
    "id": "expertise-swiftui",
    "resources": [{"path": "从本轮清单复制", "sha256": "从本轮清单复制"}],
    "status": "reviewed",
    "reviewer": "实际审阅者",
    "observations": [{
      "source": {"path": "源快照内真实文件", "line": 3},
      "interpretation": "该行及追踪的实现表明什么行为，与哪些语义/AC相关",
      "unknowns": ["未能确认的配置、接收者或运行结果；确无未知时用空数组"]
    }]
  }]
}
```

resources 必须完整匹配该 review 的清单；每个 source_paths 文件都需要真实行号和
具体观察。可按 review 分次提交，由工具合并；提交空壳、“已处理”不能代替分析。
plan_sha256 使用 `core.digest(core.json_bytes(plan))`，与 CLI 的规范化 JSON 一致。
语义继续写 ios-semantics.json，义务继续映射 ios-coverage.json，审阅记录不能替代它们。

harness-init/import-legacy 默认启用此门禁。0.6.0 既有项目先运行 expertise-plan 采用
新协议并补审阅；保持 page/F/AC ID。source-check --harness 校验资料摘要、清单新鲜度、
必需审阅和源范围。检查证明记录合同有效，不证明模型已正确理解；高风险行为仍需独立复核。
domains 计划冻结该清单、审阅和 MCP 证据，执行中不得改写。源码变化后重提 facts、
重跑 expertise-plan、重审受影响项；旧清单/记录归档，旧 PASS 不继承。

## MCP 的实际查询

本版实现 stdio 源查询客户端；MCP 服务需由实际环境安装并固定版本。当前发行没有
安装 Serena/Xcode/Apple SDK，没有 Mac 实测。服务器配置由用户项目保存；远端 Mac
可用显式 SSH stdio 桥，远端源码一致性和构建上下文仍需独立核验。HTTP transport 未实现。

`mcp-query --project <target> --server <server.json> --request <query.json>`
执行 initialize → initialized → tools/list（分页）→ tools/call → 关闭进程。
不调用改写、rename、构建、安装或任意命令工具。只有固定源读工具白名单可调用。
失败/超时写 failure.json 和 transcript/stderr，绝不写成功索引。真实服务缺工具时保留
unavailable/unknown，继续不依赖此证据的分析；不能更换成假服务凑通过。

server.json：schema 示例见 [MCP 配置](../assets/mcp-server.example.json)。command 为
已安装固定版本服务的 argv 数组，不是 shell 字符串；cwd 自动设为实际 iOS 源根。
Serena 服务须在启动时选定源项目，因为 activate_project 不在只读查询白名单。
MCP args 必须按实际 tools/list 的 inputSchema 填写，不凭本文假设每个版本都有同名工具。
源快照排除 `.serena/` 工具缓存；应用源码、工程配置和资源变化仍使证据过期。

query.json 必填 source_sha256、graph_sha256、fact_ids、tool、arguments；摘要来自本轮
ios-facts.json，fact_ids 是该查询要澄清的真实事实。示例见 [查询输入](../assets/mcp-query.example.json)。
query 返回的 MCP-ID 可写到对应 ios-semantics known claim 的 tool_evidence_ids；保留原
fact_ids/source evidence。门禁核对实际采集文件和 transcript 摘要、源新鲜度及事实关联。

证据保存在 spec/ref/mcp-runs/MCP-ID/{artifact.json,transcript.json,stderr.log}，索引为
spec/ref/ios-mcp-index.json。返回位置/类型/引用需与本轮源码和构建配置复核；本版标记
resolution=tool_response、build_context=unverified，不自动升级为 compiler_binding/runtime，
不修改机器 facts/obligations，不把文档或上游建议当成 App 行为真值。

构建/设备工具（MobileBuildMCP 等）在已有授权范围通过宿主能力或真实 CLI 运行，按
原 capture/behavior/设备协议保存命令、退出码、源/目标摘要和观察。它们不走此源只读白名单。
