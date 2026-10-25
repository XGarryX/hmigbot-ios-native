> **iOS 源输入**：读取 Swift/Objective-C、SwiftUI/UIKit、Xcode 工程及原生资源；实际源构建与设备观测依赖可用的源平台环境。鸿蒙侧构建和验收保持原流程。源侧操作详见 `a2h-spec/references/native-input.md`。

# 100% 对齐铁律（HARD-GATE，全 skill 通用）

**目标**：HMOS 端必须与 iOS 源端 **100% 视觉一致**。"差不多 / 看起来够用了 / 鸿蒙不支持就这样吧"全部不接受。

## 1. 禁止把"HMOS 端实现缺失"误判为"scenario 失败 / unreachable"

**事故根因**：sub-agent 遇到「iOS 源端有页面但 HMOS 端没有」时懒得做 differential test，直接判 `CRASH(scenario_failed)` 或 `CRASH(unreachable_unauthenticated)`，把**真实迁移 bug** 当作 scenario 阻塞处理，掩盖 P0 finding。

**规则**：任何"page 不可达"判断都必须先做 **differential test**：

| 状态 | 含义 | 正确归类 | fixer_layer |
|---|---|---|---|
| iOS 能到达 + HMOS 不能（同样的导航/scenario）| HMOS 端缺失实现 | `ALIGNMENT_DIFF` 或 `CRASH(category=page_missing_hmos)` | `ui` 或 `feat` |
| iOS 不能 + HMOS 不能，两端因同样前置态缺失 | scenario 共同失败 | `CRASH(scenario_failed)` | `feat`（scenario yaml 修复）|
| iOS 到 X / HMOS 到 Y（不同页）| HMOS 端导航链断裂 | `ALIGNMENT_DIFF(category=nav_chain_broken_hmos)` | `ui` |
| 两端都到达但视觉不一致 | 常规视觉差异 | `ALIGNMENT_DIFF` | `ui` |

**Differential test 强制步骤**（sub-agent 在判定 unreachable 前必须执行）：

1. 主路径正常：scenario 准备 + 导航 + 截图两端
2. **iOS 截到，HMOS 截不到** → **不准**写 `unreachable_unauthenticated` / `scenario_failed`！必须写：
   - `ALIGN_P{page_id}_page_missing_hmos.md` (kind=ALIGNMENT_DIFF, severity=P0, fixer_layer=ui/feat)
   - Section 3 实际：贴 iOS 截图证据 + HMOS 实际跳转到的页（或崩溃 log）
   - Section 5 修复建议：查 `features/business_*/src/main/ets/pages/` 是否有对应 ets，若有则查 router_map.json / RouterUtils.pushPathByName 注册链
3. **HMOS 截到，iOS 截不到**（典型：iOS 有营销弹窗 / 引导层 / 系统拦截）→ **不准**写 `scenario_failed_login`！必须：
   - (a) **先查 carry-forward**：扫 `spec/fix/round-(N-1)/ui/*.md` 找 disposition=`skipped/manual_review` 且描述匹配当前阻塞物的，有 → frontmatter 写 `related: [round-(N-1) 相对路径]` + status 升 `partial`
   - (b) **单端截图保留证据**：HMOS 端的截图存到 `screenshots/harmony/round-{N}/{trip_id}/<name>.jpeg`
   - 写一份 `ALIGN_P{page_id}_ios_baseline_blocked_{反例物}.md`：kind=ALIGNMENT_DIFF, severity=P1, fixer_layer=ui, category_pattern=`dialog_extra_on_ios` 或 `ios_promo_blocks_baseline`
4. **两端都截不到** → scenario 真坏了，写 `CRASH(scenario_failed)` 合法
5. Sub-agent 必须在 manifest.findings 里标 `category_pattern`

**新增 category_pattern**：
- `page_missing_hmos` — iOS 可达 + HMOS 不可达
- `nav_chain_broken_hmos` — 两端到达不同页
- `launch_flow_skipped` — HMOS 跳过启动前置页
- `ios_promo_blocks_baseline` — HMOS 可达 + iOS 被营销/引导/拦截弹窗挡住
- `dialog_extra_on_ios` — iOS 源端多了 HMOS 端不存在的弹窗（差异本身就是 finding）

**Sub-agent 自检追加**：退出前 grep 自己写的 `CRASH(scenario_failed)` markdown，若某 page 在 ets 源码能找到（`find features/ -iname '<name>Page.ets'`）但本轮没单独验证过 HMOS 实际行为 → markdown Section 3 加："本轮未实测 HMOS 端是否真有该路由；scenario 修复后续跑须 differential test 确认"。

## 2. 禁止"自作主张归类为设计差异"

`design_difference` / `platform_difference` / `dynamic_content` 三类**降级标签不得本 skill 自动判定**。任何视觉差异默认 **bug，severity=high**，直到三种证据之一打掉：

1. **用户对话显式确认**："这条算平台差异，不修"。主代理先把差异完整描述+截图+影响列给用户，得到明确豁免才能改类
2. **HMOS 系统级 UI**（状态栏字号 / 导航条 / 时钟字体 / 输入法）——OS 控制 App 无 API 干预。主代理需给出"已 grep / 已读 OS API 文档" 证据 link
3. **iOS 源端本身就是动态/随机内容**（list 顺序随机、时间戳、用户 token）——主代理给出 iOS 源码片段证明运行时随机

任一未满足 → 视为 bug，必须修。

## 3. 升级用户的场景

本 skill **不再**升级"修不动"（那是 visual-fixer 的职责；预算耗尽后是否继续由调用方——用户或 a2h-verify——决定）。本 skill 只在以下场景升级用户：

- 模拟器自动启动失败 / adb / hdc 不可用
- arkts-scenario-runner 跑挂导致页面进不去（≥3 种 scenario 写法仍失败）
- 多模态服务不可用 / 接连 3 次返回非法 JSON
- `spec/fix/round-N/` 自检无法通过且非业务可修

升级格式：

```
⚠️ visual-verify 卡死请示

阶段: {scenario_run | capture | multimodal | schema_self_check}
页面: {page_id 或 N/A}
失败现象: {具体描述}
已尝试: {≥3 种规避手段，每条带原因}
建议: (a) 用户介入排查环境 / (b) 标 page status=blocked 跳过本页继续 / (c) 终止本轮 visual-verify
```

> 视觉差异本身的"修不动"不在本 skill 升级范围内——按 schema 写成 markdown 即可，visual-fixer 修不动会自己升级用户。
