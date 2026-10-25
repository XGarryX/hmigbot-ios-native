> **iOS 源输入**：读取 Swift/Objective-C、SwiftUI/UIKit、Xcode 工程及原生资源；实际源构建与设备观测依赖可用的源平台环境。鸿蒙侧构建和验收保持原流程。源侧操作详见 `a2h-spec/references/native-input.md`。

# iOS 真实点击导航 Playbook（公共 include）

> Phase 2 sub-agent 和未来其它需要 LLM-driven 真实点击导航的 prompt **必须 include 本文档**。
> 抽自 v2 SKILL.md Step 4.0 + 2.0.a + 2.0.5，是经过实战验证的稳定模式（< 10% 失败率）。
>
> **核心原理**：fact-tree.reach_path 多为 `[self]` 不可用；非 exported Activity am-start 直跳报 SecurityException。
> 唯一可行路径 = 从 launcher 起步，LLM 看 dumpsys/uiautomator dump 现场决定 tap 哪里，一步步走到目标。

---

## 1. 启动 + 弹窗速关（每个 page 进入前必跑）

```text
# 1.1 force-stop + cold launch launcher
# 原源平台历史命令（iOS 按本文件适配说明执行）: adb -s {ios_serial} shell am force-stop {ios_pkg}
sleep 1
# 原源平台历史命令（iOS 按本文件适配说明执行）: adb -s {ios_serial} shell am start -n "{ios_pkg}/{launcher_activity}" -W
sleep 5   # 等 Splash + 初始化

# 1.2 关启动弹窗（见 §2 dismiss cache 复用）
python3 $SKILLS_ROOT/arkts-visual-verify/scripts/dismiss_popups.py \
  --device {ios_serial} --platform ios \
  --catalog spec/visual-verify/dialog_id_catalog.json \
  --wait-modal 4 --max-iter 8
# ↑ 脚本只认 --catalog（不是 --target-activity）。catalog 由 Phase 1 extract_dialog_ids.py 产；
#   退出码要 check：0=已清 / 2=仍有 modal / 3=catalog 缺失 / 4=dump 失败。
#   --wait-modal 4：启动弹窗(隐私/促销)常慢半拍，首轮 CLEAN 会再轮询等它出现再关，防漏关
#   （2026-07-11 从 10 缩到 4——固定税瘦身；导航中弹窗另有 dismiss 救场兜底）。
```

**trip_1**（无登录态，2026-07-10 改链式）：首启链页走 **链式连采**（batch-prompt Step 1.-1：
chunk 起点一次 `pm clear`、顺链采全，**不逐页 pm clear**——省 N-1 次门链重走）；非链页（如 Login）
链后按本节 force-stop 起步。注："重弹"是首启页可达的**前提**不是副作用（first_launch_onboarding
页 force-stop 起步必然 nav_unreachable）。
**trip_2**（登录态）：用 `am force-stop`（不清数据）保留登录态——已由调用方在 trip 起点跑过 login scenario。

---

## 2. 启动弹窗速关 cache（dismiss_popups.py 内部）

> 冷启动后常弹广告 / 协议 / 更新等。把"点哪个坐标能关掉"记在
> `spec/visual-verify/cache/dismissals.json`，下次遇到同款直接复用。

### 文件格式

```jsonc
{
  "entries": [
    {
      "signature": "<dHash 或 dump 文本 hash>",
      "click_x": 990, "click_y": 480,
      "success_count": 3,
      "platform": "ios"
    }
  ]
}
```

### dismiss 循环

```
冷启动 → 循环最多 5 次：
  1. 截图 / dump 顶层 → 算 signature
  2. 已在目标 activity → exit 0
  3. 查 dismissals.json：
     ├─ 命中 → 点 (click_x, click_y), success_count++ 落盘
     └─ miss → 在当前 UI 找候选按钮（id/text 含
                close / skip / cancel / exit / agree / 同意 / 跳过 / 暂不 / 我知道了 / 稍后）
                按优先级点：close > skip > later > cancel > confirm/agree
                点完顶层变了 → (signature, x, y) 写回 dismissals.json
                点完没变化 / 无候选 → BACK 兜底
  
5 次仍未到达 → exit 2 → 调用方按规则升级
```

### signature 算法

- 优先：截图缩到 64×64，灰度差分 hash（dHash），输出 16 位 hex
- 兜底：取 dumpLayout 前 3 行可见 text 拼接后 sha1[:16]

---

## 3. 从 launcher 真实点击导航到目标 page

### 3.1 LLM 决策流程

```text
[历史源平台示例：不适用于 iOS，不可执行。iOS 源设备/构建按本文件适配及 native-input 协议；目标 hdc/hvigor 检查仍须实际执行。]
loop hop_n = 1..6 (硬上限):
  3.1.a  adb shell dumpsys window windows   → 取输出里 mCurrentFocus 行
         或 adb shell dumpsys activity activities → 取 mResumedActivity 行
         （过滤用 grep / Select-String / python 一行式均可）→ 拿当前 activity 名
  
  3.1.b  IF current_activity matches target_activity:
         break (success)

  ⚠️ Compose 单 Activity 例外（Activity 名判页失效）:
     若 App 是 Jetpack Compose 单 Activity（所有页同一个 Activity，mResumedActivity
     恒不变）→ 3.1.a/3.1.b 的 Activity 名主键**恒退化**，必须短路，改用**内容签名判页**:
       python3 $SKILLS_ROOT/swiftui-fact-tree/scripts/resolve_current_page.py \
                 --tree spec/toolkit-fact-tree.json --serial $SERIAL --json
       page_id = 上面 stdout JSON 的 .page_id 字段
       IF page_id == target_page: break (success)
     判页主键分层 + 签名机制 + 抗滚动/弹窗/动态文本的完整方案见
     $SKILLS_ROOT/swiftui-fact-tree/references/page-identity.md（已真机 6/6 验证）。
     检测"是否单 Activity Compose"：fact-tree 多个 page 的 fq_class 同名 / type=="Composable"，
     或 `adb shell dumpsys package <pkg>` 输出里含 Activity 的行数约等于 1。
  
  3.1.c  adb shell uiautomator dump /sdcard/dump.xml
         # 原源平台历史命令（iOS 按本文件适配说明执行）: adb pull /sdcard/dump.xml <TEMP>/dump.xml        # <TEMP>=/tmp 或 %TEMP%
         ★F 优化(2026-07-10 实测焊入):**同一条 shell 调用里紧接着跑抽取器,LLM 只读它的摘要,禁 cat/Read 全 XML**:
           python3 $SKILLS_ROOT/arkts-visual-verify/scripts/extract_clickables_cli.py <TEMP>/dump.xml
         输出每行 `CLICK|文本|resource-id|centerX,centerY`(SCROLL 行同理),十几行替代 ~4000 token 的原始 XML。
         A/B 实测(同5页同设备串行,两口径如实):**页面循环内** 183s→131s(-28%,锚失配诊断页 -52%);
         **agent 端到端** 279s→256s(仅-8%,被每 agent ~100s 固定开销稀释——chunk 页数越多越接近循环内值);
         **token -61%**(111,979→43,898,harness 客观数,F 最硬的收益=上下文余量+成本)。摘要 35+5 份真实
         dump 零 clickable 丢失。⚠️ 引用 sub-agent 自报计时必须与 harness duration_ms 对账,勿单引循环内口径。
         **唯一例外(兜底)**:抽取器 exit 2(<3 个 clickable,WebView/纯图页)→ 才准 cat 完整 XML(实测 0 触发,但必须保留此退路)。
  
  3.1.d  LLM 决策：
         结合 fact-tree.pages[target].inbound_triggers
           （含 from_page / trigger_label / trigger_view_id / evidence_file/line）
         + 3.1.c 的 CLICK/SCROLL 摘要
         → 决定下一步点哪个按钮（直接用摘要给的 center 坐标）
         
         决策优先级：
         (1) inbound_triggers.trigger_view_id 在当前 dump 命中 → 点它
         (2) inbound_triggers.trigger_label 文本严格匹配 → 点它
         (3) inbound_triggers.trigger_label 模糊匹配（substring）→ 点它
         (4) inbound_triggers 链上一级（如 MineFragment）的 trigger → 先点它去 parent
         (5) 都不命中 → 看 fact-tree.flow_graph 找间接路径
  
  3.1.e  adb shell input tap {x} {y}
         sleep 1.5 (动画 + 异步加载)
         loop continue
```
### 3.2 失败终止条件 + BLOCKED reason 枚举

写 `spec/fix/baseline-blocked/BLOCKED_baseline_<page>_<trip>.md` 时 `reason` 必须是以下枚举之一（另有 `structurally_unreachable`——dispatch 前置步声明式写入，sub-agent 不产；全集与机器路由的单一事实源 = `scripts/blocked_reason_routes.json`，改枚举三处同改）：

| reason | 触发条件 | 后续怎么修 |
|---|---|---|
| `nav_unreachable` | 6 hop 内没到达 target_activity | 检查 fact-tree.inbound_triggers 是否正确；可能要补 reach_path 多 hop chain |
| `dump_unavailable` | `uiautomator dump` 连续 3 次失败（动画太久 / 系统 dialog 拦截）**且已排除广告**（见下行）| 关动画 `settings put global window_animation_scale 0`；或加 sleep |
| `need_ad_profile` | dump 持续失败 + 屏幕有促销/倒计时内容（**倒计时广告挡 idle**，最常见根因）且无 ad_profile 或 profile 失效 | **主会话派 `ad-profile-builder` agent** 学/刷 profile → 重跑本 chunk。有 profile 时 batch prompt 1.2.a/1.3.c 会自动用 ad_dismiss.py 清，不该走到这。★BLOCKED 单**必带 `ad_repro` 块**（见 §3.3）——你刚亲手走完这条路，hop 轨迹在你上下文里白拿；没有它 builder 只会冷启学，深页插屏学不到（乒乓循环） |
| `data_precondition_missing` | 目标 page 需要某数据态（如收藏列表非空），sub-agent 不在 Phase 2 现场造 | **主会话派 `scenario-builder` agent**：读 fact-tree 该页（或其父页）`state_required` 的 `data_hint` 学 check/create 双配方并建 fixture → 删该页 baseline png 后重跑 Phase 2 补图。builder 报 NEED_HUMAN_FIXTURE 才轮到用户手工。（v2026-07-10c：无独立预检环节，本 reason 就是数据态的**正常 at-need 主路径**——撞到才学，不是异常） |
| `hop_limit_exceeded` | 已经走到合理 parent 但 trigger 不响应（onClick 未接 / 跳错 / 截被弹窗拦了 dismiss 都不掉）| 看保存的 last_dump_path 查实际 dump 内容 |

### 3.3 BLOCKED 文件 schema

```markdown
---
id: BLOCKED_baseline_<page_id>_<trip_id>
page_id: <page_id>
trip_id: <trip_id>
reason: nav_unreachable | dump_unavailable | need_ad_profile | data_precondition_missing | hop_limit_exceeded
hop_n: <最后一 hop 序号>
last_dump_path: spec/visual-verify/blocked_dumps/<page_id>_<trip_id>_<timestamp>.xml
last_current_activity: <实际停留的 activity 名>
# ★仅 reason=need_ad_profile 必填(2026-07-10)：深页广告复现块。喂给 ad-profile-builder 让它机械回放
#   到广告现场学（builder 自己只会冷启，学不到深导航才弹的插屏）。hops = 你本次实际走过的轨迹
#   （每跳点了什么，从你自己的导航记录直接抄，不是 fact-tree 静态 reach_path——那个多为 [self]）。
ad_repro:
  entry_page: <撞广告时正要去的目标 page_id>
  trip_id: <trip_1|trip_2>                      # builder 需知道要不要登录态
  hops:
    - {tap_text: "<该跳点击的文本>", coords: [x, y]}
  ad_activity: <撞广告时 mResumedActivity>
disposition: skipped
---
sub-agent 导航 <page_id> 失败（reason: <reason>，hop=<hop_n>）。
最后停留：<last_current_activity>。
last_dump_path 保留了最后一次 dump，便于排查 trigger 不响应 / 文案不一致 / 异常弹窗。

后续修复：
- 若 reason=nav_unreachable → 检查 fact-tree.pages[<page_id>].inbound_triggers
- 若 reason=data_precondition_missing → 主会话派 scenario-builder（读 state_required.data_hint 建 fixture）后删该页 baseline png 重跑 Phase 2 补图
- 若 reason=hop_limit_exceeded → grep 实际 dump 排查 trigger 真实文案
```

---

## 4. 截图（到达 target page 后）

```text
SHOT_PATH="spec/visual-verify/screenshots/ios/{trip_id}/{page_id}.png"
# 原源平台历史命令（iOS 按本文件适配说明执行）: adb -s {ios_serial} shell screencap -p /sdcard/_p0.png
# 原源平台历史命令（iOS 按本文件适配说明执行）: adb -s {ios_serial} pull /sdcard/_p0.png "$SHOT_PATH"
# 原源平台历史命令（iOS 按本文件适配说明执行）: adb -s {ios_serial} shell rm /sdcard/_p0.png

# 必跑 resize（多模态 API 2000px 上限，留 200px 余量到 1800）
python3 $SKILLS_ROOT/arkts-visual-verify/scripts/resize_screenshot.py "$SHOT_PATH"
```

**截图完整性自检**：
- 文件大小 > 10KB（小于即可能是黑屏 / 系统 UI）
- max_dim ≤ 1800px（resize 已保证）
- 不通过 → retry 1 次，仍失败按 `reason=dump_unavailable` BLOCKED

---

## 5. 返回上一页（page 间继续遍历）

每个 page 截完图后回 launcher 起点，方便下一 page 从头开始（避免链式状态残留）：

```text
# 简单粗暴：force-stop + 重启 launcher（同 §1.1）
# 不依赖 back 键，因为 back 行为本身可能就是 bug
# 原源平台历史命令（iOS 按本文件适配说明执行）: adb -s {ios_serial} shell am force-stop {ios_pkg}
```

trip_2 状态保留：`am force-stop` 不清数据，登录态 / preferences 都在。
（trip_1 首启链模式例外：链式连采**不逐页回起点**，顺链前进到底，见 batch-prompt Step 1.-1。）

---

## 6. 关键铁律

1. **禁止** 用 am-start 直跳内部 Activity（非 exported 必失败，且即使成功也跳过了路径验证）
2. **必须** 每个 page 从 launcher 起步导航（哪怕慢一点）
3. **hop 上限 6**：超过即 BLOCKED，避免无限循环 + 给用户清晰信号
4. **dump 失败 retry 3 次**，仍失败 BLOCKED `reason=dump_unavailable`
5. **resize 不可省**——多模态 API 2000px 上限，截图后立即 resize
6. **failed page 不连累其它 page**：本 page 写 BLOCKED continue，下一个 page 从 §1 干净起步
