<!-- when: Stage 1 批收口后 / Stage 3 组收口后的域巡检点派发时加载 -->
<!-- topics: 域巡检波, 巡检路由表, 后台句柄, findings 单, 墙钟预算 -->

# 域巡检波（Domain Patrol Wave）——按域无条件巡检本批产物

> **为什么存在**（2026-08-24 四组对照实验实证）：知识注入与自愿菜单都救不了
> 「自信错」类缺陷（模型不觉得自己不会，全 app 57 处 .align 误用实录）；域 agent
> 裸审会假 PASS；唯一双验证有效的组合 = **结构性触发（无条件必巡，不留任何
> "谁想到要调"的判断缝）+ 巡检 agent 出厂强制必读本域陷阱文档**。
> 巡检发现的新缺陷类由 retrospect 蒸馏成机械闸（免疫循环）。

## 路由表（文件域 → 巡检 agent，闭集）

| 本批文件落在 | 巡检 agent | 备注 |
|---|---|---|
| pages/ components/ dialogs/ views/ | `arkts-ui-build` | 布局/对齐/层叠语义 |
| resources/ 沉浸式/多设备适配相关 | `arkts-ui-adapt` | 巡检前置段待补（本表先登记） |
| services/ network/ repositories/ database/ preferences/ | `arkts-data-network` | 网络/数据层语义 |
| 权限/通知/窗口/系统能力调用 | `arkts-system-component` | 巡检前置段待补 |
| 三方 SDK 适配（支付/登录/推送渠道） | `arkts-thirdparty-component` | 巡检前置段待补 |

（arkts-audit / arkts-verify / arkts-android-analysis / arkts-project-setup 非产物域，不参与巡检。）

## 执行协议（主会话执行，全并行零墙钟设计）

1. **触发（无条件）**：批/组 closer 返回、`apply_writeback` 成功后**立即**派巡检——
   与后续批次施工**并行**（巡检只读，与任何写者零竞态；批 N 巡检 ∥ 批 N+1 转换）。
2. **考卷（闭集）**：writeback manifest 的本批文件清单（只巡增量）+ 各页
   `layout_sources` / slice `spec_refs` / `spec/baseline/resolved-theme.json`（安卓真值锚点——窗口装饰级结构如自绘标题栏/状态栏条不在 layout XML 里，其真值以 resolved-theme 的 decor 条目为锚，**不得以 layout XML 缺席为由判其越权**）+ 输出契约（见下）。
3. **派发**：按上表路由（一批可命中多域→并行多个巡检 agent）；task_name
   `patrol_<域>_<批号>` 唯一化；派发参数模板 **MUST 加载**
   [agent-prompts/9-patrol.md](./agent-prompts/9-patrol.md)。
4. **收口**：标准 join 协议句柄（后台 T1/T4）；expected-set 契约 = findings 文件
   `spec/fix/round-<R>/patrol/<域>-<批号>.md`（无缺陷也要落"空单"作收货凭证）。
   **join 硬点 = 本批页面 converted→verified 翻转之前**——巡检未收口/未通过的批，
   verified 悬置。
5. **修复**：findings>0 → 派 repair worker **1 轮**（复用原 worker 上下文 +
   findings 修法；fixer_layer 按域路由同 structural-closure §3.5）→ 机械闸
   （binding_gate 等）复验本批 → 清零才翻 verified；1 轮未清 → fix 单转 FV
   审计段（记债不静默，不再重试）。
6. **墙钟**：全程与施工并行（巡检只读，批 N 巡检 ∥ 批 N+1 转换），暴露在总
   墙钟上的只有末批尾巴（巡检+1 轮修复 ≈ 3-6 分钟），不设单次时限。巡检句柄
   悬挂/迟迟不归时按 **join 协议条款②** 走活性检查（连续超时→list_agents 核对→
   死句柄断点重派/记债），不另立超时机制；极端情况下该批 verified 悬置转 FV
   审计段，流水线照常推进。

## findings 单格式

复用 `spec/fix/` 单 schema（与 visual-verify ui/feat 单同构）：每条 = 文件:行号 +
现象 + ArkUI 语义依据 + 修法 + `fixer_layer`。frontmatter 加 `source: patrol` 与
`patrol_domain: <域>`。空单 = frontmatter + `findings: 0`（收货凭证）。
