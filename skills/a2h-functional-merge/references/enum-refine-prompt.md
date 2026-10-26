# Phase 3 枚举入口精修 — sub-agent prompt 模板

保留原限定：只精修传入 confidence=low 的枚举功能点，不全量重写，也不改其他映射。输入为 name/raw_identifier、合法 fact-tree record ID 集合和选定 Source。

## 方法

1. 在本轮 target/Release 的 Source 中定位实际枚举/事件的引用，排除注释与不生效分支；关键词众数只作候选。
2. 从真实 Button/action、UIKit target-action 或事件处理追踪 switch/if、路由和中转函数，直到实际 SwiftUI 目的页或 UIKit push/present/segue/容器落点。
3. 区分点击后第一个承载页与后续结果/详情/成功页/弹窗。源代码实际选定通用承载页时保留其真实类型和 discriminator，不为每个枚举虚构页面。
4. 下线或不在本轮可达路径的分支按真实来源记录原因；不能把 DEBUG 片段作为 Release 行为。mapped_record 必须在输入合法集合；不匹配时明确 not_in_facttree/低置信，不能编 ID。

## 输出

原 JSON 形状与文件 enum_refine_overrides.json 保持：

```jsonc
{
  "<本轮真实raw_identifier>": {
    "mapped_record": "<本轮合法原生record_id>",
    "impl_file": "<选定Source中的真实.swift/.m/.mm路径>",
    "confidence": "high",
    "evidence": "<实际文件/符号/调用链与行号>",
    "notes": "<实际通用承载参数或差异>"
  }
}
```

只有反查证明后才能标 high；示例不是本项目事实。主流程仍通过原 --enum-refine 消费并执行原合并与自检，不把未验证的自动源解析器当已移植。
