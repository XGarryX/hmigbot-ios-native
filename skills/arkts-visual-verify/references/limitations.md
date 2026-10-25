# 局限性

> 从 SKILL.md §10 拆出。仅在用户问"为什么这种情况不处理"时 Read。

| 局限 | 说明 |
|------|------|
| 登录墙 | 通过 arkts-scenario-runner 的 `login` 场景自动达到已登录态后再截图。首次需人工跑一次 `scenario_run.py --scenario login` 录入手机号+万能码建档；之后 visual-verify 全程无交互 |
| 数据依赖 | 可在 `spec/visual-verify/page_scenarios.json` 里为该页声明前置场景（如 `upload_image`），runner 先把 App 带到目标状态。**未声明场景的 data_dependent 不再 silent skip**——会写一份 `CRASH_P*_scenario_required_*.md` 记录缺口，让人工介入补 scenario 或评审豁免 |
| 静态页面为主 | 截图的是页面默认状态，无法覆盖交互中状态（如播放中、展开菜单） |
| 长页面分段拼接 | 合法长页（详情/设置/Feed）走 Step 4.1.3 自动分段截图 + OpenCV 模板匹配拼接 + 锚点切块对比；无限流 / 纯色长背景 / 两端长度差 > 30% 时降级为单帧 + 报告标注，不强拼错位长图 |
| 纯色/无锚点长页 | 模板匹配置信度 < 0.7 时放弃长图流程，只对比首屏（`capture_mode: single_fallback`） |
| H5/WebView 页面 | Step 4.1.4 走三段式：URL 一致性断言（origin+path+业务 query，忽略 ts/nonce 等）+ 原生外壳 diff（WebView 视口覆盖为黑色不纳入对比）+ 可选加载态覆盖；URL/Bounds 都抓不到时降级为纯源码 url 表达式对比 |
| 需要模拟器 | 两端模拟器必须已运行且应用已安装 |
| 多模态依赖 | 需要多模态模型能力，纯文本模型无法执行 |
| 动态内容差异 | 默认仍是 bug；多模态可在 description 里标注疑似动态，但**必须**满足 §1.1.1 三条证据之一才能在 markdown frontmatter 设 `disposition: manual_review` |
| 平台设计差异 | 同上——本 skill 不自动判 design_difference，必须用户对话明确豁免；豁免后写入 markdown 的 disposition 字段 |
| 不修代码 | 本 skill 只产出 `spec/fix/round-N/ui/*.md`，不动 .ets。修复由 visual-fixer 离线读 markdown 完成；修不修得动由 visual-fixer 判断，轮次上限由本 skill `round_budget.py` 机械把关，预算耗尽后是否续跑由调用方（用户或 a2h-verify）决定 |
| 导航链路依赖 | 采用导航链路模式，深层嵌套页面可能导航路径较长，耗时增加 |
