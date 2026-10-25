<!-- when: Phase A 生成 meta.json / view.xml / visibility bindings 时加载 -->
# Phase A 原生脚本调用

所有调用以当前迁移项目为工作目录，传入真实选定 target/Release 的源根；共享 Source 输入器会校验成员和条件视图。脚本产候选骨架，后续语义分析与原阶段门禁仍须执行。

## A2a meta.json 骨架

```text
python .agents/skills/ios-ui-graph-builder/scripts/synthesize_meta_json.py <源根> --activity <真实页面类型> --page-id <page_id> --project-root <项目根> --output spec/baseline/ui-snapshots/<page_id>/meta.json --mode scaffold --package <bundle_id>
```

activity 是保留的数据接口，值为真实 App/Scene、SwiftUI 页面或 UIKit 类型。layout_sources/style_sources 填实际 Swift/ObjC/Storyboard/XIB/资源路径，不填虚构布局文件。脚本的 UNKNOWN/未分析字段须继续读取源码补充。

## A3 静态 view.xml 与语义富化

```text
python .agents/skills/ios-ui-graph-builder/scripts/synthesize_view_xml.py <源根> --layouts <真实源文件逗号分隔> --project-root <项目根> --output spec/baseline/ui-snapshots/<page_id>/view.xml
python .agents/skills/ios-ui-graph-builder/scripts/synthesize_meta_json.py <源根> --activity <真实页面类型> --page-id <page_id> --project-root <项目根> --output spec/baseline/ui-snapshots/<page_id>/meta.json --mode enrich --existing spec/baseline/ui-snapshots/<page_id>/meta.json --view-xml spec/baseline/ui-snapshots/<page_id>/view.xml
```

静态根节点 synthesized=true，bounds 未知；不能当作设备观测。原生词法 outline 只列候选调用，须补真实层级、状态、所有权、条件、交互和导航。成功为 medium；真实设备观测才可据其证据提高评级，缺文件按原 low 规则披露。

## 显隐绑定

```text
python .agents/skills/a2h-spec/scripts/extract_visibility_bindings.py --ios-root <源根> --project-root <项目根> --output spec/baseline/ui/visibility-bindings.json
```

复用官方 SwiftSyntax 扫描渲染条件、动态 opacity 与 UIKit isHidden/alpha，输出原 visibility-bindings.v1 rows；未知渲染上下文列入 unresolved，动态数据流继续原 Phase A 人工语义补充，不把未命中等同于无条件。Objective-C 仍沿用有限候选路径。

提取入口会把 unresolved 候选的位置和表达式显示到 stderr。按原 A2b 读取对应源码，在现有 Phase A 分析报告记录其真实渲染/行为语义及显隐数据来源；不能因 rows 未收录便认定无条件，也不为这些候选另设审批或门禁。
