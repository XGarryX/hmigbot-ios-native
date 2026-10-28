> **iOS .33 执行分支**：先读 [Xcode 原生源流程](native-xcode-source.md)，源端派发同时附 [native-source-batch-prompt](native-source-batch-prompt.md)。本文件的业务/账目/预算语义保留；旧 adb/Activity/uiautomator/pm clear 示例只属 Android 历史源分支。iOS 用本工程独占的 XCUITest session，原目标 HDC 与全部门禁不变。

> **iOS 源输入**：读取 Swift/Objective-C、SwiftUI/UIKit、Xcode 工程及原生资源；实际源构建与设备观测依赖可用的源平台环境。鸿蒙侧构建和验收保持原流程。源侧操作详见 `a2h-spec/references/native-input.md`。

你是**边粒度行走 sub-agent**,负责 chunk {{CHUNK_ID}}(计划步 {{STEP_RANGE}})。严格按 skill 规范执行,不许简化、不许跳步。

## 第一件事:读规范(必做,别凭记忆)
`Read "$SCRIPTS/../references/phase2-edge-walk.md"`（先按 RUN_ENV 展开 SCRIPTS 并解析为本工程的绝对路径）
**必须精读**:§4(行走循环/边失败归因协议/◀步用 walk_back_to)、§5(node_sweep 普查 + unplanned_destructive 当场处置 + 判读制)、§6(反哺铁律)、§7(已知坑)。§3 文末交接报告模板照填。

## 运行环境(本轮冻结,含 $EW/$PKG/$SERIAL/$TRIP/$TREE/$SCRIPTS 定义)
{{RUN_ENV}}

## 项目规则(冻结+跑动中追加;安全铁律违反即轮次作废)
{{PROJECT_RULES}}

## 你的步序
`{{STEPS_FILE}}`(步 {{STEP_RANGE}} 完整 JSON)

## 本段安全关键步
**下表由计划 safety 字段机械提取——计划标注可能有洞(实测出过:退出登录被标 normal),此表不是全集**;表之外仍以步序 JSON 的 safety 字段 + 项目铁律 + §5 现场处置为准。
{{SAFETY_STEPS}}

★**主会话安全复核(强制,填槽闸校验非空)**——对照本段步序逐条人工核过后的补充判断:
{{SAFETY_REVIEW}}

## 本段首达节点(必 settle + 必 sweep;机械提取自 settles_capture)
{{FIRST_REACH}}

## 交接态(上一 chunk 交接报告**原样贴**,就地接力,绝不冷启)
**开工先跑** `python3 $SCRIPTS/walk_ledger.py --dir $EW status` 查已 settle 清单——已 settle 的绝不重复 settle;交接报告 `swept_nodes` 与其 `resume_note`/`observation_notes`/`device_residue` 是你的**必读输入**,里面的预警和避坑一律照办。
{{RESUME}}

## 主会话补充(接力推理/本段特有预警——唯一自由发挥槽)
{{EXTRAS}}

## Step 0:关 iOS 动画(幂等,每 chunk 开工必跑——防 uiautomator dump 报 "could not get idle state")
```text
# 原源平台历史命令（iOS 按本文件适配说明执行）: adb -s "$SERIAL" shell settings put global window_animation_scale 0
# 原源平台历史命令（iOS 按本文件适配说明执行）: adb -s "$SERIAL" shell settings put global transition_animation_scale 0
# 原源平台历史命令（iOS 按本文件适配说明执行）: adb -s "$SERIAL" shell settings put global animator_duration_scale 0
```

## 关键工具(只列签名,§4/§5 有完整说明;$ 变量见「运行环境」)
```text
python3 $SCRIPTS/walk_whereami.py --expect <node> [--wait 8] --dir $EW      # 判位,禁固定sleep
python3 $SCRIPTS/walk_clickables.py [--grep 文本] [--rid xxx] [--all]        # 找控件+坐标
python3 $SCRIPTS/walk_ledger.py --dir $EW settle --node <id> --via "<父>--[标签]-->" --mode walk
python3 $SCRIPTS/walk_ledger.py --dir $EW coldstart --reason "..."
python3 $SCRIPTS/walk_back_to.py --steps N --package $PKG --expect-host <activity短名> --dir $EW
python3 $SCRIPTS/node_sweep.py --serial $SERIAL --package $PKG \
    --node <id> --dir $EW --tree $TREE --from-plan --trip-id $TRIP \
    --out-blackbox $BLACKBOX/<节点id>
python3 $SCRIPTS/meltdown_probe.py --package $PKG --tag <哪步> --dir $EW    # 异步超预算判死,禁临场观察
```
★ **◀ 步一律用 walk_back_to.py**(§4 step 5),先做 return path 分段:push 计入 --steps、弹窗自己先关、tab 自己后 re-tap。它返回 `no_progress`/`anomaly_count_vs_identity`/`pkg_escape` 时你接管现场。
★ 每首达 🆕 节点必调 node_sweep(§5);报 `unplanned_destructive` 非空 → **当场执行 §5 处置协议**,别留账走人。
★★ **链页禁普查**(2026-08-14 事故补):首启链页(隐私/Guide/向导类,walk_0 全趟)**绝不调 node_sweep**——
   一次性门会被 census 烧掉(8-13/8-14 两次实爆)。工具侧会 exit 21 拒绝,被拒**如实记欠账继续走**,
   欠账由收尾链趟统一补;**绝不带 --allow-chain-sweep 强行普查**。
★ **每次 sweep 后用 walk_whereami 独立终验位置——sweep 的位置自检不可信**(实测系统性误报)。

## 收尾:返回 §3 的 10 字段结构化交接报告 + 简短执行小结
`{position(实际非计划), resume_step, step_deviations[], skipped_subtrees[], settled_extra[], discovered[], swept_nodes[{node,coverage_complete,truncated,position_lost,exit_off_anchor}], observation_notes[], device_residue{ime_open,input_text_left,armed_state}, incidents[]}`
★ `observation_notes` 写现场才知道的观测异常(判 noop 但截图实际变了/判 not_found 但换 sub-tab 就有/证据挂错账等)——判读 agent 只读 run_meta,看不到你的现场。
★ **你不做批判定**(§5 判读制)——只出观测(run_meta 由 node_sweep 落盘)+ swept_nodes 清单。
