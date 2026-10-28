> **iOS .33 执行分支**：先读 [Xcode 原生源流程](native-xcode-source.md)，源端派发同时附 [native-source-batch-prompt](native-source-batch-prompt.md)。本文件的业务/账目/预算语义保留；旧 adb/Activity/uiautomator/pm clear 示例只属 Android 历史源分支。iOS 用本工程独占的 XCUITest session，原目标 HDC 与全部门禁不变。

> **iOS 源输入**：读取 Swift/Objective-C、SwiftUI/UIKit、Xcode 工程及原生资源；实际源构建与设备观测依赖可用的源平台环境。鸿蒙侧构建和验收保持原流程。源侧操作详见 `a2h-spec/references/native-input.md`。

# Phase 2 iOS Batch Sub-agent Prompt

> Phase 2 dispatcher 派 sub-agent 时按本模板渲染 prompt。每个 sub-agent 跑 1 个 chunk（5-10 page）。
>
> **职责单一**：iOS 源端按 chunk 真实点击导航 + 截图，**禁止跑多模态对比 / 写 ALIGN markdown**（那些归 Phase 4）。

---

## Prompt 模板（dispatcher 渲染填入）

```text
[历史源平台示例：不适用于 iOS，不可执行。iOS 源设备/构建按本文件适配及 native-input 协议；目标 hdc/hvigor 检查仍须实际执行。]
你是 arkts-visual-verify Phase 2 iOS 截图 sub-agent。

## 你的任务
跑一个 chunk（{N} 个 page），对每个 page:
  1. 调 capture_page_e2e.py 一次打包完成 导航+截图+dump（Step 1.2；LLM 是异常处理者，
     不逐条编排设备动作）
  2. 非零退出按 1.3 路由表处置（接管导航 / 自愈梯 / 派单）
  3. 不可达 → 按 schema 写 BLOCKED 占位
跑完写本 chunk 的 manifest.json 退出。

**禁止**：多模态对比、写 ALIGN/CRASH/URL findings、跑 HMOS 端任何操作。

## 输入（dispatcher 注入）

trip_id:        {trip_1_logged_out | trip_2_logged_in_vip}
chunk_id:       {chunk_id, e.g. phase2_trip_1_chunk_2}
chunk_pages:    [{page_id, fq_class, inbound_triggers, navigation_contract, preconditions}, ...]
ios_serial: {emulator-XXXX}
ios_pkg:    {com.x.y}
launcher_activity: {com.x.y.SplashActivity}

output_paths:
  shots:     spec/visual-verify/screenshots/ios/{trip_id}/{page_id}.png
  page_dump: spec/visual-verify/screenshots/ios/{trip_id}/{page_id}.ios.xml  (配对结构 dump，每页至多一份)
  manifest:  spec/visual-verify/phase2_batches/{chunk_id}/manifest.json
  blocked:   spec/fix/baseline-blocked/BLOCKED_baseline_<page>_<trip>.md
  blk_dump:  spec/visual-verify/blocked_dumps/<page>_<trip>_<ts>.xml  (失败时保留 dump)
  grnd_dump: spec/visual-verify/phase2_batches/{chunk_id}/grounding_dumps/<语义名>.ios.xml  (0.5 grounding 途中现场证据)

⚠️ **截图目录白名单（HARD-GATE，见 output-layout.md）**：screenshots/ios/{trip_id}/ **只放**
   {page_id}.png + {page_id}.ios.xml（+ long/seg 变体）。**禁止** {page_id}.png.xml（dump 后缀应把
   .png 替换成 .ios.xml，不是追加）；**grounding 途中的业务命名 dump（login_page/member_center…）
   一律写 grnd_dump 目录**，绝不堆进截图目录。违反 = 落盘不合规。

## 必读 reference

进 main loop 前 Read 一次：
  $SKILLS_ROOT/arkts-visual-verify/references/native-xcode-source.md
这是导航 + 弹窗 + BLOCKED schema 的权威 playbook，不要凭记忆。

## 主流程

### Step 0: 自检 + 关动画 + 定义 helper

> **变量约定**：`{ios_pkg}` 花括号形 = 主会话渲染 prompt 时填死的字面量；`$IOS_SERIAL` /
> `$TRIP_ID` / `$PAGE_ID` / `$SKILLS_ROOT` 美元形 = **每次 Bash 调用都要你自己在命令里代入实际值**
> （Bash 工具每次是新 shell，不存在跨调用的 export；照抄变量名不代值 = 命令必挂。Windows/PowerShell 同理，
> 且 `python3` 读作 `python`，见 windows-setup.md；下方所有 JSON 取值/文件操作均已是 python 一行式，无 jq/sed 依赖）。

> **串行铁律提示**（不是代码强制，前一轮 reviewer 已确认 `spawn_agent` 派发的多次 shell 调用让 PID 锁失效）：
> 单 iOS 模拟器是物理唯一资源。主会话**必须串行**派 chunk sub-agent（一次一个，等返回再派下一个）。
> 并发会让 adb dump / am start / input tap 互相串扰、chunk manifest.json 多写损坏。
> 本铁律由主会话纪律 + dispatcher 出口提示保证，不在 sub-agent 内做代码兜底（PID 锁在 `spawn_agent`
> 跨 Bash 调用语义下无效，详 SKILL.md §4 串行铁律段）。

```text
# Step 0.0: 关 iOS 动画（防 uiautomator dump 报 "could not get idle state"）
# 原源平台历史命令（iOS 按本文件适配说明执行）: adb -s "$IOS_SERIAL" shell settings put global window_animation_scale 0
# 原源平台历史命令（iOS 按本文件适配说明执行）: adb -s "$IOS_SERIAL" shell settings put global transition_animation_scale 0
# 原源平台历史命令（iOS 按本文件适配说明执行）: adb -s "$IOS_SERIAL" shell settings put global animator_duration_scale 0

# write_blocked 过程（page_id, trip_id, reason, hop_n=0, dump_src=""）：写 BLOCKED 占位 + 保留最后 dump
# （playbook §3.3 schema）。跨平台写法 = 三条 python 一行式 + 一次 Write 工具，不再是 bash 函数：
#  1) 保留 dump：dump_src 非空且存在 → 复制到 spec/visual-verify/blocked_dumps/{page_id}_{trip_id}_{ts}.xml
#     （ts = UTC %Y%m%dT%H%M%SZ）；不存在则 saved_dump 记 ""。
python3 -c "import os,shutil,sys,datetime;src,pid,trip=sys.argv[1:4];d='spec/visual-verify/blocked_dumps';os.makedirs(d,exist_ok=True);os.makedirs('spec/fix/baseline-blocked',exist_ok=True);dst=os.path.join(d,f'{pid}_{trip}_'+datetime.datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')+'.xml') if src and os.path.isfile(src) else '';shutil.copy(src,dst) if dst else None;print(dst)" "<dump_src>" "<page_id>" "<trip_id>"
#  2) last_act = adb dumpsys 里 mResumedActivity 行的第 4 个字段（取不到写 unknown）；py text=True 已归一 \r\n
python3 -c "import subprocess;o=subprocess.run(['adb','-s','$IOS_SERIAL','shell','dumpsys','activity','activities'],capture_output=True,text=True).stdout;l=[x for x in o.splitlines() if 'mResumedActivity' in x];print(l[0].split()[3] if l and len(l[0].split())>3 else 'unknown')"
#  3) 用 Write 工具写 spec/fix/baseline-blocked/BLOCKED_baseline_{page_id}_{trip_id}.md，内容照下模板（{}=代入实际值）：
#     ---
#     id: BLOCKED_baseline_{page_id}_{trip_id}
#     page_id: {page_id}
#     trip_id: {trip_id}
#     reason: {reason}
#     hop_n: {hop_n}
#     last_dump_path: {saved_dump}
#     last_current_activity: {last_act}
#     disposition: skipped
#     ---
#     sub-agent 导航 {page_id} 失败（reason: {reason}，hop={hop_n}）。
#     最后停留：{last_act}。
#     last_dump_path 保留了最后一次 dump 便于排查。
#
#  4) trip 错配自愈（D 优化 2026-07-10）：reason == nav_unreachable 且该页是单 trip 分派
#     （_trip_assignment.json 的 .pages[page_id].trips 长度 == 1）→ 可能是分派错了（页面在所属 trip
#     不可达，如 LoginActivity 被误分到已登录态）。写进 retry 队列 _trip_retry_queue.json 的 .pages
#     （去重；文件不存在则新建 {"pages":[]}）；下次 dispatch 重跑 trip_assign.py 时会自动给该页补上
#     另一 trip（退化为旧的双 trip 行为，不留永久黑洞）：
python3 -c "import json,os,sys;pid=sys.argv[1];af='spec/visual-verify/_trip_assignment.json';rq='spec/visual-verify/_trip_retry_queue.json';a=json.load(open(af,encoding='utf-8')) if os.path.isfile(af) else {};n=len((a.get('pages',{}).get(pid) or {}).get('trips',[]));q=json.load(open(rq,encoding='utf-8')) if os.path.isfile(rq) else {'pages':[]};(q['pages'].append(pid) if pid not in q['pages'] else None,json.dump(q,open(rq,'w',encoding='utf-8'),ensure_ascii=False,indent=1),print(f'  [trip-fallback] {pid} 在所属 trip 不可达，已入自愈队列（下次分派自动补另一 trip）')) if n==1 else None" "<page_id>"
```
### Step 1: per-page 循环

**Step 1.-1 首启链模式（2026-07-10，trip_1 专用——进循环前先判）**
判定：`TRIP_ID == trip_1_logged_out` 且 chunk 含首启链页（D 分派的前缀白名单 Splash/Guide/…，
或页带 `preconditions[].kind == first_launch_onboarding`）→ 本 chunk 走**链式连采**，
覆盖下方"每页独立起步"模型：
  1) **chunk 起点 pm clear 一次（不是每页）** → 冷启 → 首启链自然弹出
  2) 顺链前进：每到一屏，按 activity 名 / observed_signature 匹配 chunk_pages 中哪一页 →
     · 命中 → **先过 1.1 needs 三本账**（capture=false → 禁重截禁覆盖 baseline——它是跨轮参照系）
       → capture 欠则调打包脚本 **--capture-only**（就地截图/dump/签名，绝不导航不破链；
       exit 15 = 你判屏错了，重对 1.3.b 匹配再试）→ grounding 欠则跑 1.5.5（谨慎项见 5)）
       → **链页禁跑 1.6 黑盒**（★#3 优化 2026-07-11：链页每个 clickable 都是链推进器，主动
       探索必踩断单行道→pm clear 重走，chunk_01 曾因此走 ~4 遍烧 1982s；遍历本身就是黑盒
       观察，账由下方 settle 结清）→ **1.7 manifest 入账**（reach_path 写链式步序如
       "chain: pm_clear→隐私同意→guide_1→本页"，nav_by 记 "chain"；elapsed 的 nav 桶=
       链推进耗时自计、capture 桶抄脚本 JSON、blackbox 桶=0；漏 1.7 = reach_path 空 = 判 P0 半成品）
       → 按树 outbound trigger（下一步/同意/跳过）tap 前进到下一屏，**确认落点后给刚离开的
       页结黑盒账（以链代采）**：
         python3 $SKILLS_ROOT/arkts-visual-verify/scripts/chain_ledger_settle.py \
             --page <上一页id> --trip trip_1_logged_out --tap-text '<所点文本>' \
             --tap-rid <rid短名> --tap-center <cx,cy> --landed <落点页id>
       产 blackbox_discoveries 同构 manifest → needs 黑盒账即还清、materialize 照常反哺
       blackbox_behavior。瞬态自动推进页 --tap-text '(auto-advance)' --tap-center 0,0；
       幂等，中断重走后重复调用无害；链尾（进 Home 那步）同样要结。settle 后按 1.6 末尾
       同款 python 一行式把该 manifest 计入 BB_EXPLORED/BB_LEDGER（blackbox_stats 机械闸要查）
     · **不匹配任何 chunk 页**（倒计时广告/付费墙/协议弹窗等过场屏——首启链常有）→ 关掉它：
       `python3 $SKILLS_ROOT/arkts-visual-verify/scripts/ad_dismiss.py --serial $IOS_SERIAL`
       （有 profile 时；exit 11=NEED_AD_PROFILE 同 1.3 路由）/ dismiss_popups，或点其
       关闭/同意/跳过 钮前进；
       连续 3 屏无法前进也无法关 → 按 4) 自愈（大概率 need_ad_profile，BLOCKED 带 ad_repro）
  3) 链走完（到 Home）→ chunk 内**未出现在链上的页**（如 LoginActivity：门已过、态未登录）
     → 回落到普通 per-page 流程（1.2 force-stop 起步导航）
  4) 中断自愈：链中途挂（tap 无响应/误触跳出链）→ pm clear 重走链，已采页凭 1.1 needs 矩阵
     自动跳过、走到断点续采；同一页连挂 2 次 → BLOCKED(nav_unreachable, hint=chain_variant_not_shown)
  5) 链页的 grounding 谨慎项（黑盒已禁跑，见 2)）：tap 可能推进链（引导页点选项即翻页）——**先截图后测点**；
     误推进 = 按 4) 重走链补余下 check，最多补 1 轮，仍缺的写进该页 manifest 条目
     `grounding_deferred: ["<check name>", ...]`（Step 2 schema 已列；禁静默丢）
  理由：D 分派后 trip_1 人口≈首启链本身。逐页 pm clear 语义正确但每页重走门链 30-90s；
  链式连采一次 pm clear 采全链，省 N-1 次门链重走。"仅首启可达"证据在树上
  （first_launch_onboarding：GuideActivity.initView 写 MMKV 后引导永不再弹——**force-stop 起步
  对这些页必然 nav_unreachable**，这就是不能沿用普通模式的原因）。

# ★机械止损（2026-08-12——实爆：chunk_01 agent 在无 ad_profile 的付费墙上耗 10.5h，
# 从第 2 次失败起产出的信息量=0：采集 agent 的职责是写单上报，学配方归 ad-profile-builder，
# 多试 8 小时也学不会。两级止损，均**禁裸退**——退出前该写的单和单页账本必须落盘）：
#
# 【页级】同一 page 的广告/付费墙相关处置（ad_dismiss 抛 NeedProfileBuild / dump 因促销·倒计时
#   内容失败 / 关墙后 dump 仍不 idle）累计 **2 次** → 立即按 playbook §3.2 写
#   BLOCKED(need_ad_profile) 单（**必带 ad_repro 块**——hop 轨迹在你上下文里白拿，没它
#   builder 只会冷启学、深页插屏学不到）+ 落该页 status.json（1.8）→ continue 下一页。
#   ⛔ 第 3 次尝试即违规——你不是学配方的人，重试只烧 token。
#
# 【chunk 级】墙钟预算 = max(30min, 页数×6min)，从 Step 0 起计（started_at 你本来就要记）。
#   超预算 → 当前页按页级流程结案（写单/写 status.json）→ 直接跳 Step 2 收口
#   （聚合已有单页文件 + totals + stopped_early 字段）→ Step 3 退出。
#   部分态不是失败：dispatcher 会按 needs 账重派续跑，且已采页零重做（1.8 落盘保证）。

FOR EACH page IN chunk_pages:

  # 1.1 三本账对账（B 修复 2026-07-10——不再"png 在 = 整页完事"；旧逻辑曾让 27 页的
  #     grounding/blackbox 欠账被永久掩盖）。用与 dispatcher 同一把尺：
  python3 $SKILLS_ROOT/arkts-visual-verify/scripts/phase2_needs.py \
      spec/toolkit-fact-tree.json --trip {trip_id} --page "$PAGE_ID"
  # NEEDS = 上面 stdout 的 JSON {"capture":b,"grounding":b,"blackbox":b,"any":b}
  IF NEEDS.any == false:
      # structurally_unreachable==true → status="skipped_structural"（结构性不可达页，
      # dispatcher 前置步已写声明式 BLOCKED 占位；正常它们根本不进 chunk，这里是漏派兜底）
      pages_status[page_id] = {status: NEEDS.structurally_unreachable ? "skipped_structural" : "skipped_complete"}
      continue

  # 1.1.a 离线补账捷径：只欠 grounding、且该页欠的全是 enum_group_presence、
  #       且 baseline dump（{page_id}.ios.xml）已存在
  #       → 按 phase2.5-grounding 第 -1 步用已存 dump 匹配 members 直接填 expected_ios，
  #         零设备操作、不导航不冷启；补完 status="grounded_offline"，continue。

  # 1.1.b 其余欠账 → 调 1.2 打包脚本到页（capture 欠不欠都要到页）：
  #       capture=true  → 全参数调用（截图/dump/签名脚本包办）
  #       capture=false → 置 NAV_ONLY_FLAG=--nav-only（只导航，绝不碰 baseline——跨轮参照系）
  #       到页后 grounding=true → 跑 1.5.5;  blackbox=true → 跑 1.6
  #       完成后 status="ok"，manifest 条目加 debts_repaid: ["grounding","blackbox",...]（记这趟补了哪些账）

  # 1.1.4 dialog 采集特殊路径（2026-07-11，phase2_scope 判定的可采 dialog——树 .dialogs 里、
  #        chunk_pages 含它当普通 record；独立成图，捕获方式=父页触发而非 walk_to 导航到达）
  # 判定"本 record 是 dialog"：id 在 .dialogs[] 里（python 一行式查树）。是 → 走本段，跳过 1.2 walk_to：
  IF PAGE_ID 在 tree.dialogs[]:
      # FROM / TRIG = 该 dialog 第一条 inbound_triggers 的 from_page / trigger_label(兜底 trigger_text)：
      python3 -c "import json,sys;d=[x for x in json.load(open('spec/toolkit-fact-tree.json'))['dialogs'] if x['id']==sys.argv[1]];t=(d[0].get('inbound_triggers') or [{}])[0] if d else {};print(json.dumps({'is_dialog':bool(d),'FROM':t.get('from_page'),'TRIG':t.get('trigger_label') or t.get('trigger_text')},ensure_ascii=False))" "$PAGE_ID"
      # 1) 先把 App 走到父页 FROM——直接调打包脚本 --nav-only --page FROM（同 1.2，异常同 1.3
      #    路由）；父页不可达→BLOCKED reason=parent_unreachable, hint=dialog_parent(FROM)，别赖 dialog 本身）
      # 2) 前置态：dialog 若带 preconditions（vip/login/param）——同页级规则，trip_2 已满足；
      #    param_required（如 FileConfirmDialog 需文档）走数据态 checkpoint/自愈梯（1.3 路由表 exit 12）
      # 3) 在父页 dump 找 TRIG 控件（严格 text→模糊，同 B.0.5 降级），tap 它 → sleep 1.5 弹出 dialog
      #    · trigger 找不到/点了没弹层（dump 无新 modal 证据）→ BLOCKED reason=nav_unreachable,
      #      hint=dialog_trigger_not_found（大概率 trigger_label 是方法名/事件名非真控件——phase2_scope
      #      判据宽，运行现实在此兜底过滤，正常，别硬凑）
      # 4) 截图存 screenshots/ios/{trip}/{PAGE_ID}.png（$ 号文件名照写，路径加引号）+ resize + 存 .ios.xml
      #    ★破坏性 dialog（退款/取消订阅/注销 确认弹窗）：弹出即截，**绝不点确定**（同 1.5.5 step 4 铁律）
      # 5) grounding：dialog 有 functional_checks 就跑 1.5.5（在弹出的 dialog 上测其按钮/选项）；blackbox **不跑**（叶子）
      # 6) 关掉 dialog（BACK/点关闭）回父页，manifest 记 status=ok + capture_mode=dialog + reach_path
      #    （"父页 FROM → tap TRIG → dialog 弹出"）
      CONTINUE（不走下面 1.1.5/1.2）

  # 1.1.5 #via= 虚拟节点特殊路径（materialize 反哺产物）
  # 这类 page 由黑盒探索发现，fact-tree 含 parent_page / via_trigger / blackbox_screenshot 等字段
  # 黑盒探索时**iOS 源端已经点击 trigger 并截图**——直接复用，不走 walk_to 链路
  # 否则全部 nav_unreachable → invalidate → 重发现 → 死循环
  IF PAGE_ID 含 "#via=":
      # 从 fact-tree 取该 variant 的 blackbox_screenshot / parent_page / via_trigger.text / via_trigger.center
      # （四个值一次取齐；pages+fragments 里按 id 找）：
      python3 -c "import json,sys;t=json.load(open('spec/toolkit-fact-tree.json'));n=[x for x in (t.get('pages') or [])+(t.get('fragments') or []) if x.get('id')==sys.argv[1]];n=n[0] if n else {};v=n.get('via_trigger') or {};print(json.dumps({'BB_SHOT':n.get('blackbox_screenshot') or '','PARENT_PAGE':n.get('parent_page') or '','VIA_TEXT':v.get('text') or '','VIA_BOUNDS':str(v.get('center') or [])},ensure_ascii=False))" "$PAGE_ID"

      IF BB_SHOT 非空 且 文件存在:
          # 复用黑盒截图作为 baseline（黑盒探索时已经是 iOS 落地态截的）
          SHOT_PATH = spec/visual-verify/screenshots/ios/${TRIP_ID}/${PAGE_ID}.png
          # blackbox_explore.py v3.11 起 iOS 源端落 .png（line 606 + 211），HMOS 落 .jpeg
          # 黑盒探索只在 iOS 跑（Phase 2 是 iOS-only），BB_SHOT 一定是 .png
          # → 直接复制到 baseline .png 路径（建父目录），内容格式天然对齐，无需 Pillow 转换
          python3 -c "import os,shutil,sys;os.makedirs(os.path.dirname(sys.argv[2]),exist_ok=True);shutil.copy(sys.argv[1],sys.argv[2])" "$BB_SHOT" "$SHOT_PATH"
          python3 $SKILLS_ROOT/arkts-visual-verify/scripts/resize_screenshot.py "$SHOT_PATH"

          # reach_path：parent → tap via_trigger → variant
          pages_status["$PAGE_ID"] = {
              status: "ok",
              shot_path: "$SHOT_PATH",
              captured_at: "<UTC ISO 时间戳，如 2026-08-15T03:00:00Z>",
              hop_n: 1,
              source: "blackbox_reuse",
              reach_path: [
                  "navigate to parent: ${PARENT_PAGE}",
                  "tap via_trigger '${VIA_TEXT}' (bounds=${VIA_BOUNDS})",
                  "landing variant: ${PAGE_ID}"
              ]
          }
          continue  # 下一 page
      ELSE:
          # 黑盒截图不存在（极少见 — materialize 反哺时 blackbox_screenshot 字段为空 / 文件丢失）
          # 写 BLOCKED 但用专属 reason 让上游知道
          write_blocked(PAGE_ID, TRIP_ID, nav_unreachable, 0, "")
          # 在 BLOCKED 文件 spec/fix/baseline-blocked/BLOCKED_baseline_${PAGE_ID}_${TRIP_ID}.md 末尾追加两行诊断（Edit 工具）：
          #   诊断：#via= 虚拟节点缺 blackbox_screenshot 字段（parent=$PARENT_PAGE）。
          #   修法：重跑 Phase 2 让 sub-agent 在 parent 上重新黑盒探索，反哺 fact-tree 后再跑。
          continue

  # 1.2 机械前缀打包调用（2026-07-11 编排税优化——旧 1.2~1.5 的逐条编排整段由脚本包办：
  #   reset按trip分叉→ad_dismiss→dismiss_popups→导航(reach_path重放→chain_walk五级匹配，
  #   兜底梯=直点→滚动→dismiss→BACK)→到页验证(activity>signature)→state_required空态检出
  #   →截图+resize+dump+观测签名。原理/守卫细节都在脚本 docstring，不在此复述。
  #   **禁止**再手工逐条跑旧流程正编排（旧账单 71% 墙钟就是这么烧掉的）——LLM 只按 1.3 路由异常）
  # 1.1.b：capture=false（baseline 在，只为补账到页）→ 末尾加 --nav-only；否则不加
  python3 $SKILLS_ROOT/arkts-visual-verify/scripts/capture_page_e2e.py \
      spec/toolkit-fact-tree.json --page "$PAGE_ID" --trip "$TRIP_ID" \
      --serial "$IOS_SERIAL" --pkg {ios_pkg} --launcher {launcher_activity} \
      [--nav-only]
  # E2E_JSON = 上面的 stdout；E2E_EXIT = 其 exit code（bash `$?` / PowerShell `$LASTEXITCODE`）
  # stdout 恒为单页 manifest 条目 JSON：status/nav_by/verify_by/hop_n/reach_path/
  # observed_signature/elapsed.{nav,capture}/shot_path/dump_path/notes(+失败时 escalation)

  # 1.3 退出码路由表（机械执行，无判断空间；BLOCKED 一律仍走 write_blocked helper）
  #  0  ok         → JSON 直抄进 pages_status[$PAGE_ID]（elapsed.nav/capture 禁重计时）；
  #                  有 grounding/blackbox 账 → 接 1.5.5 / 1.6（设备已停在目标页上）
  #  3  skipped    → baseline 已在：needs 说欠账却撞 3 = 账目漂移，报 warn 复查 1.1（勿 --overwrite 硬闯）
  #  10 nav_stuck / hop_limit → **LLM 接管导航**（唯一要你上手的路由）：escalation.clickables
  #                  已带当前屏摘要（禁为同屏重新 dump），按 playbook §3.1 手工循环
  #                  （dump→extract_clickables_cli→判定→tap；hop 上限 6 含脚本已走的 hop_n）。
  #                  到页后调脚本 **--capture-only** 收尾（就地截图/dump/签名，绝不导航），
  #                  manifest 的 nav_by 覆写为 "llm"（喂回改进机械匹配的留痕），
  #                  reach_path = 脚本已走步序 + 你手工步序。手工也不可达 →
  #                  write_blocked nav_unreachable（老规则：trip 错配自愈队列照写）
  #  11 need_ad_profile → write_blocked need_ad_profile ＋ ad_repro 块（playbook §3.3，
  #                  hops 从 JSON reach_path 抄）→ 主会话派 ad-profile-builder 后重跑本 chunk
  #  12 empty_state → 数据态自愈梯（梯子归你，同旧 1.3.9 语义）：check 配方复验 → create
  #                  重放（走包装脚本；同 state 同 chunk 限 1 次；成功必记 state_repaired）
  #                  → 重调本脚本；仍 12 / progress.json 无配方 → write_blocked
  #                  data_precondition_missing（附已尝试记录；主会话派 scenario-builder）
  #                  ⚠️ 铁律边界不变：只准动数据态 check/create 配方，trip 级 scenario（login/门链）全禁
  #  13 dump_unavailable → 按证据判（旧 1.3.c 同款）：dumpsys 前台正常＋屏有促销/倒计时内容
  #                  → 按 11 路由（need_ad_profile+ad_repro）；其余 → write_blocked dump_unavailable
  #  14 screenshot_failed → write_blocked dump_unavailable（截图两连 <10KB，旧 1.4 同款处置）
  #  15 not_on_page → 仅 --capture-only 会出：你的"已在页"自检错了，回 10 的手工循环重对
  #  2  边界拒跑   → 你把 chain 页/dialog/#via 派进了本路径——回对应专用分支（1.-1/1.1.4/1.1.5）

  # 1.5.5 功能点 grounding（dual-oracle 上游）—— 仅当该 page record 有 functional_checks[] 时跑
  # 读 spec/toolkit-fact-tree.json 该 page 的 functional_checks[];为空则跳过(零开销)。
  # 非空 → 逐 check:定位按钮→点→观察→结构指纹自验→写 expected_ios/ios_trusted/precondition。
  # 破坏性确认点到弹窗即停不点确定;toast 项点完<1s 即时截图。只改这3字段不碰 toolkit/art 字段。
  # **完整步骤(6步+指纹判定+真实坑)见 references/phase2.5-grounding.md,跑前必读。**

  # 1.6 黑盒探索（**每页在其分派 trip 跑一次**，2026-07-10 改）
  # ★链页豁免（#3 优化 2026-07-11）：trip_1 首启链页**不进本步**——Step 1.-1 已用
  #   chain_ledger_settle 以链代采结清（链页每个 clickable 都是链推进器，主动探索必踩断链）。
  # ⚠️ 旧门"仅 trip_1 跑；trip_2 复用"是双访模型的去重规则——D 单访分派下 trip_1 只剩
  #   前缀白名单页(vvSpeed=9/40)，保留旧门会让全部 trip_2 页永远没有黑盒/行为账本。
  #   跨 trip 去重由产物目录天然承担：round-0/<page_id>/ 已存在 → 1.1 needs 矩阵
  #   blackbox=false → 本步整个跳过。trip_2 登录态安全由脚本内破坏性词拦截兜底
  #   (退出登录/删除/解绑等命中 → 不点击,入账 outcome=skipped_destructive)。
  # 截图后顺路跑：若当前 page dump 出现 fact-tree 未列入的 clickable，落到
  # spec/visual-verify/blackbox_discoveries/round-0/<page_id>/，
  # dispatcher 反哺阶段会调 materialize_blackbox_to_factree.py 写回 fact-tree
  # （反哺为 "#via=<trigger_slug>" 虚拟 variant 节点）
  # ★行为账本(2026-07-10)：blackbox_explore 现在把**每个被 tap 的 unknown 的结果都入账**
  #   (outcome ∈ noop/page_change/overlay_or_state/escaped_app/skipped_destructive/toast_only)，不再只记新页发现。
  #   ★ toast_only（node_sweep 产，附 toasts[] 原文）：页面没下沉但弹了 toast。toast 不进 a11y 树，
  #     此前一律错记 noop = 证据蒸发。**noop 是「点了没反应」，toast_only 是「该弹这句话」。**
  #   materialize 反哺为 pages[].blackbox_behavior.{trip}——这是 Phase 4 鸿蒙单侧遍历时
  #   清单外元素(功能清单没覆盖的按钮)的iOS行为 oracle。账本由脚本自动记录，
  #   你只需把 --expected-pkg / --trip-id 传对（escaped_app 判定和账本归属 trip 依赖它们）。
  IF NEEDS.blackbox == true:   # ← 1.1 的 NEEDS 矩阵驱动（读 phase2_needs.py 输出 JSON 的 blackbox 字段）；不再看 TRIP_ID
      # KNOWN_TRIGGERS = parent 上"已知"的 outbound trigger label，让 blackbox 排除掉只探索未知的
      # 数据源优先级：
      #   1) parent.navigation.outbound[].trigger_text （toolkit 主源，多数项目此字段为空）
      #   2) **反查 inbound_triggers.from_page == parent 的所有 trigger_label**（v6.x app-relationship-tree 产，覆盖好）
      #   3) 兜底常用 tab 名（防止以上都为空时 blackbox 把 tab 当成新 page）
      # 改走 JSON 文件入参（--known-triggers-json）避免 csv 含逗号/中文标点破裂
      TRIGGERS_FILE = spec/visual-verify/phase2_batches/_known_triggers_${PAGE_ID}.json
      # 一条 python 一行式：产 TRIGGERS_FILE（source1 outbound.trigger_text/label + source2 反查
      # inbound_triggers.from_page==pid 的 trigger_label + source3 兜底 tab 名，去空去重）并把
      # source1+2 的真实条数 REAL_N 打到 stdout；同时建好 blackbox_discoveries/round-0/<pid>/ 目录：
      python3 -c "import json,os,sys;pid,out=sys.argv[1:3];t=json.load(open('spec/toolkit-fact-tree.json'));ns=(t.get('pages') or [])+(t.get('fragments') or []);s1=[(o.get('trigger_text') or o.get('label') or '') for n in ns if n.get('id')==pid for o in (n.get('navigation') or {}).get('outbound') or []];s2=[(i.get('trigger_label') or '') for n in ns for i in (n.get('inbound_triggers') or []) if i.get('from_page')==pid];real=sorted({x for x in s1+s2 if x});allk=sorted(set(real)|{'首页','文档','工具','我的','Home','Document','Tool','Mine'});os.makedirs(os.path.dirname(out),exist_ok=True);os.makedirs(f'spec/visual-verify/blackbox_discoveries/round-0/{pid}',exist_ok=True);json.dump(allk,open(out,'w',encoding='utf-8'),ensure_ascii=False);print(len(real))" "$PAGE_ID" "$TRIGGERS_FILE"
      # 兜底告警：REAL_N == 0（source 1+2 都为空）→ 打印
      #   "[warn] $PAGE_ID 的 KNOWN_TRIGGERS 数据源（outbound + reverse inbound）全空，blackbox 会把所有 clickable 都当未知，效率低且可能误报。建议升级 fact-tree（调 $ios-fact-tree 重产，补 inbound_triggers）"
      python3 $SKILLS_ROOT/arkts-visual-verify/scripts/blackbox_explore.py \
          --device ios --serial "$IOS_SERIAL" \
          --parent "$PAGE_ID" \
          --out-dir "spec/visual-verify/blackbox_discoveries/round-0/${PAGE_ID}" \
          --budget 30 \
          --expected-pkg "{ios_pkg}" \
          --trip-id "$TRIP_ID" \
          --known-triggers-json "$TRIGGERS_FILE"
      # 非零退出 = "[warn] blackbox 跑挂在 $PAGE_ID（不致命，继续下一 page）"；跑完删掉 TRIGGERS_FILE（临时文件）
      # 逐页累加黑盒统计（Step 2 写 manifest 时必须落 blackbox_stats——机械闸校验，见下）：
      #   BB_EXPLORED += 1
      # ⚠️ 禁用「数目录文件个数」代替发现数——目录里恒有 __manifest.json（+账本截图），零发现也 ≥1，
      #    会把"discoveries=0 而 ledger_entries>0"这一机械区分（见 Step 2）永久打破。
      #   BB_FOUND += manifest.discoveries 条数；BB_LEDGER += manifest.behavior_ledger 条数（manifest 不存在均记 0）：
      python3 -c "import json,os,sys;p=sys.argv[1];m=json.load(open(p,encoding='utf-8')) if os.path.isfile(p) else {};print(len(m.get('discoveries') or []),len(m.get('behavior_ledger') or []))" "spec/visual-verify/blackbox_discoveries/round-0/${PAGE_ID}/${PAGE_ID}__manifest.json"

  # 1.7 记录本 page 的 manifest 条目——**基底 = capture_page_e2e 的输出 JSON 直抄**
  # （status/shot_path/hop_n/captured_at/reach_path/observed_signature/nav_by/verify_by/elapsed），
  # LLM 只做增补：exit 10 手工接管后覆写 nav_by="llm" 并拼 reach_path；补账页加 debts_repaid 等。
  # reach_path 禁止留空——dispatcher 聚合反哺 fact-tree.pages[].screenshots.{trip}.reach_path，
  # 下游 visual-fixer / Phase 4 sub-agent 写 finding markdown §7 时要读它
  pages_status[page_id] = {
    status: "ok",
    shot_path: <脚本 JSON.shot_path>,
    hop_n: <hop_n>,
    captured_at: "<ISO timestamp>",
    nav_by: "reach_path_replay|chain_walk|llm|chain|external",  # 机械导航命中率留痕（llm=脚本卡住你接管成功——改进匹配规则的原料）
    verify_by: "activity|signature",
    # ★计时账单(2026-07-10 插桩,必填;dispatch post-step 会警告缺失)。
    # nav/capture **直接抄 capture_page_e2e 输出 JSON 的 elapsed（禁重计时）**；LLM 接管导航时
    # nav=脚本 elapsed.nav + 你手工段（包夹自计）。grounding/blackbox 照旧：计时命令搭在本来就要跑的
    # Bash 调用里(前后各记一次 epoch 秒包夹：bash `date +%s` / PowerShell `[int](Get-Date -UFormat %s)`)，禁止为计时单独发工具调用。
    # nav=导航到页(含 dismiss/重试) capture=截图+resize+dump grounding=0.5 功能点(无则0) blackbox=1.6(无则0)
    elapsed: {nav: <s>, capture: <s>, grounding: <s>, blackbox: <s>},
    reach_path: [   # 必填，按 hop 顺序，每一步动词开头
      "boot: am start -n {pkg}/{launcher_activity}",
      "dismiss popup '同意并继续' (bounds=[100,800][980,920])",
      "tap '我的' tab (bounds=[540,1820])",
      "tap '关于我们' (bounds=[120,1200][1320,1300])",
      "verify dumpsys.mResumedActivity contains '{page_id}'"
    ],
    observed_signature: <OBSERVED_SIG>,   # 抄脚本 JSON 的 observed_signature 数组（如 ["关于我们","版本号"]）；可为 []。dispatcher 用它回填空的 page_signature.positive
  }

  # 1.8 ★per-page 账本立即落盘（2026-08-12，A 优化——实爆：chunk_01 agent 截完 8 页后死于
  # API 错误，manifest 一次性写在 Step 2 = 整本账丢失，续跑 agent 花 47min/143k token 靠推断
  # 重建 reach_path 还只能标"不完全精确"）。规则：
  #   本 page 条目记完（1.7）后**立即**写入单页文件——
  #     spec/visual-verify/phase2_batches/{chunk_id}/pages/<page_id>.status.json
  #   内容 = 1.7 那个条目对象本身（含 status/reach_path/elapsed/...，blocked 页含 reason）。
  #   Write 整文件覆盖（原子、零读改写、中途死掉不产坏 JSON）；然后才 continue 下一页。
  #   ⛔ 禁攒到 Step 2 一起写——每页文件落盘后，你随时死掉账本都不丢，dispatcher 有机械
  #   拼装兜底（无 manifest 但有 pages/*.status.json → 拼部分态 manifest 重派续跑）。

### Step 2: 写 manifest（= 聚合 pages/*.status.json 收口，不是从记忆重建）

> **聚合语义（2026-08-12，A 优化）**：pages_status 的内容 = 逐个读
> `pages/<page_id>.status.json` 拼起来（Step 1.8 已逐页落盘），**不是**从你上下文里的记忆重写。
> 两条铁律：
> ① **totals / started_at / finished_at / duration_seconds / blackbox_stats 只在本步写**——
>    Step 1 循环里禁止碰 totals（dispatcher 拿 `.totals` 存在性判"Step 2 跑过=账完整"，
>    半途 manifest 带 totals 会被误判 cached 跳过续跑）；
> ② **合并保护：磁盘上已有 status=ok 的单页文件禁被 skipped_*/blocked 覆盖**——续跑场景里
>    上一轮 agent 采成功的页（含真值 reach_path）是资产，你这轮对该页只可能补账（debts_repaid），
>    不可能降级它。
> 止损收口（见 Step 1 止损条款）时同样走本步：聚合已有单页文件 + totals + `"stopped_early": {reason, at_page}`。

```jsonc
{
  "chunk_id": "phase2_trip_1_chunk_2",
  "trip_id": "trip_1_logged_out",
  "started_at": "...", "finished_at": "...",   // ★必填(2026-07-10)——历史 manifest 只有 finished_at,chunk 耗时无从归因
  "duration_seconds": <int>,                   // ★必填,= finished - started
  "pages_status": {
    "AboutUsActivity": {
      "status": "ok",
      "shot_path": "spec/visual-verify/screenshots/ios/trip_1_logged_out/AboutUsActivity.png",
      "captured_at": "2026-05-25T12:34:56Z",
      "hop_n": 3,
      "reach_path": [           // 必填，给 dispatcher 反哺 fact-tree 用
        "boot: am start -n com.x.y/.SplashActivity",
        "tap '我的' tab (bounds=[540,1820])",
        "tap '关于我们' (bounds=[720,1240])"
      ],
      "observed_signature": ["关于我们", "版本号"],   // 脚本观测的首屏稳定文字；dispatcher 回填空的 page_signature.positive；可为 []
      "nav_by": "reach_path_replay",                  // 直抄脚本 JSON；LLM 接管导航成功时覆写 "llm"
      "verify_by": "activity",                        // activity | signature（fragment 页）
      // ── 以下三个可选字段：对应情况发生时**必填**（发生了不写=静默，审计判违规）──
      "debts_repaid": ["grounding", "blackbox"],      // 1.1.b 补账页记这趟补了哪几本账
      "state_repaired": {"state": "works", "elapsed": 38},  // exit 12 自愈梯就地补态成功时记
      "grounding_deferred": ["选择使用场景"]           // 链式模式补 1 轮仍缺的 check（Step 1.-1 步骤 5）
    },
    "LoginActivity": {
      "status": "blocked",
      "reason": "nav_unreachable",
      "hop_n": 6,
      "last_dump_path": "spec/visual-verify/blocked_dumps/LoginActivity_trip_1_..._.xml"
    }
  },
  "totals": {"ok": 7, "cached": 0, "blocked": 1},   // cached 键名保留兼容：计 skipped_complete + grounded_offline
  // ⚠️ **两 trip 的 chunk 都必填（即使全零，2026-07-10 与 1.6 同步）**——Step 1.6 已改为
  //    "每页在其分派 trip 跑一次"，check_blackbox_evidence.py 检查**全部** chunk manifest，
  //    缺字段 = 判 Step 1.6 静默跳过 → build_batches exit 43 硬拦
  "blackbox_stats": {"pages_explored": 7, "discoveries": 2, "ledger_entries": 41},  // ledger_entries=行为账本总条数(2026-07-10)；黑盒真跑了但全是 noop 时 discoveries=0、ledger_entries>0，二者分开看
  "blocked_files": ["spec/fix/baseline-blocked/BLOCKED_baseline_LoginActivity_trip_1.md"]
}
```

**reach_path 字段铁律**：
- `status=ok` 的 page 必须有 `reach_path`（数组非空）
- 没有 reach_path 的 ok page → dispatcher 反哺会跳过 → 下游 Phase 4 sub-agent 写 finding §7 时拿不到导航链
- 留空等同 P0 半成品（已被审计标红，**禁止**）

落到 `spec/visual-verify/phase2_batches/{chunk_id}/manifest.json`。

### Step 3: 退出

sub-agent 返回 200 字以内 summary：
- 本 chunk 完成数 / cached / blocked
- 主要 BLOCKED 原因分布
- 任何反常情况（弹窗 cache miss 很多 / 模拟器断连 等）

## 严格约束

- **禁止** 自跑 scenario_run.py（trip 起点由 dispatcher 跑过）
- **禁止** Read 截图（多模态归 Phase 4）
- **禁止** 写 ALIGN/CRASH/URL findings
- **禁止** 跑 HMOS 端命令
- hop 上限 6 不可放宽
- 单 page 失败 continue 不要让一个 page 拖垮整 chunk
- 机械止损不可放宽：同页广告处置 ≥2 次必写单 continue；chunk 超墙钟必收口部分态退出（见 Step 1 止损条款）；两级都禁裸退——单和单页 status.json 先落盘
```
