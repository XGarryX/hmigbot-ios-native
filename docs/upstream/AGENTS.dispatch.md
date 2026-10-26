<!-- arkts-domain-agents:begin (generated with codex/; do not edit inside) -->
## ArkTS / 鸿蒙迁移请求的派发规则
- 本工程安装了领域 agent（.codex/agents/arkts-*.toml）。收到 ArkTS/鸿蒙相关请求时，对照各 agent 的 description：匹配到哪个领域就用 spawn_agent 派发该 agent 处理（请求横跨多个领域时并行派发多个，汇总后回复）。
- 不要在主会话里自己凭通用知识回答这些领域问题，也不要要求用户提供 agent 或 skill 名。
- agent 回复末尾必须有 `loaded_skills:` 行；缺失、或领域内问题却报 none 时，视为未按规执行——点名应使用的 skill 重派一次；汇总回复中保留该行。
- 统一规则：**有单直调，无单走 agent**。
  - SKILL 正文写死的固定步骤（结构闸/编译/资源等）→ 直接调用对应 skill；
  - 迁移流水线阶段 skill（a2h-spec / a2h-plan / a2h-execute / a2h-verify、arkts-visual-verify、hmos-fix-build-errors 等）及 plan 产物里绑定的 `suggested_skills` → 按流水线自己的派发协议照单直调（绑定单即"写死"，不经领域 agent 重新匹配）；
  - **没有任何单子覆盖的领域需求** → 匹配领域 agent：流水线外的用户请求如此；流水线内撞到计划外领域难题（plan 未绑定、worker 协议未覆盖）时同样派对应领域 agent——但此时 agent 只输出分析与方案，改码仍由流水线的 worker / fixer 按写契约执行。
- 与 ArkTS/鸿蒙无关的通用问题直接回答，不派发。

## 设备截图/dump 落点纪律（2026-08-26）
任何 `hdc snapshot_display` / `uitest dumpLayout` / `hdc file recv` 的本地目标一律落
`spec/visual-verify/screenshots/adhoc/<page>__<tag>_<HHMMSS>.jpeg`（dump 配套同名 `.json`），
**禁止 recv 到项目根目录**。排查结束把有留存价值的移入对应 round 目录，其余删除；
收口时 `check_scratch_pollution.sh` 会对项目根做卫生检查。

<!-- arkts-domain-agents:end -->
