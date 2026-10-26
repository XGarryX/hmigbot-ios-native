# _redlines — 全 wave 公共红线（prompt header，逐字注入）

## 防污染（HARD CONSTRAINT）
安卓源码根：`{{android_src}}`——任务书里所有安卓相对路径（如 `app/src/main/java/...`）都相对它；只读这一份源码，不要到它的上级目录里另找同名或名字相近的工程。

本任务是纯净迁移。禁止读取（NEVER read）：
- `{{android_src}}/spec/`、`{{android_src}}/AGENTS.md`、`{{android_src}}/AGENTS.md`、`{{android_src}}/.gitnexus`
- 任何其他已迁移工程 / HarmonyOS 工程
- {{pollution_blocklist}}

只准读任务书列出的原始 Android 源码/资源（可顺藤读同仓其它 Android source/resource 文件）。

## 输出纪律
- 最终消息**只回结构化摘要**（旗舰档 StructuredOutput；保守档为消息尾部围栏 JSON，schema 相同）——细节一律由落盘文件承载，禁把 spec/代码/日志长文贴进最终消息。
- 产物写任务书指定路径；返回字段与 schema 逐字段对齐，禁自由发挥字段。

## 文件所有权边界（声明模板）
- 你只准创建/编辑 YOUR FILES 白名单内的文件；共享文件（registry / 契约 JSON / 路由表 / 资源索引等）禁碰。
- 白名单外的必要改动**不实现**：在返回值 `skipped[]` 登记 `{file, reason, required_owner}` 上报，由主循环转交 owner。
- 缺失依赖不越界补写：按占位分类法登记申报（见 placeholder-taxonomy 片段）。

<!-- GAP(已解决): 槽位 {{android_src}}/{{pollution_blocklist}} 由 assemble_prompt.py section_redlines 渲染（android_src ← workflow-params.project.android_src；blocklist 行展开为逐条 `- <entry>`，空名单剔行）；本片段内 HTML 注释不注入 prompt。 -->
<!-- source: docs/skills_optimization_818/design/corpus/prompt_P1_reader_member-pay.txt:L3,L15 + 3_execute-workflows.md §3.2/§3.3 -->
