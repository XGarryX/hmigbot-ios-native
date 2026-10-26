<!-- when: 域巡检波派发时加载（patrol-routing.md 执行协议第 3 步） -->
<!-- topics: 巡检派发参数, 考卷结构, 只读纪律, findings 契约 -->

# 域巡检派发参数模板

```
用 spawn_agent 派发（agent_type=<路由表命中的域 agent>，task_name=patrol_<域>_<批号>）：

任务：巡检以下迁移产物是否忠实实现安卓侧行为。你是发现问题的巡检员，不是修复者。

【考卷·文件闭集】（writeback manifest 原样列出，一个不多一个不少）
<本批文件清单>

【安卓真值锚点】
<每页 layout_sources / slice spec_refs 路径清单>

【硬性纪律】
1. 你的出厂定义里的「巡检前置」必读文档，读完才准下结论。
2. 按 ArkUI 真实渲染语义判断（修饰符/容器的实际效果），禁止按属性名与安卓
   概念的字面相似性放行（实录教训：.align(CenterEnd) 字面像 end|center，
   实际不定位 Stack 子项）。
3. 只读巡检：禁止修改任何文件。
4. 逐文件核对考卷闭集，不许抽样跳过；核对不了的条目明确标 UNVERIFIABLE+原因。
5. 时间自律：这是限时巡检，优先核对位置/显隐/接线类高危项。

【输出契约】最终消息尾部附 ```json 围栏：
{"findings": [{"file": "...", "line": N, "issue": "...", "semantic_basis": "...",
  "fix": "...", "fixer_layer": "ui|feat"}], "unverifiable": [...], "files_covered": N}
```
