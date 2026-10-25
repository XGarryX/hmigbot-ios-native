> **iOS 源输入**：读取 Swift/Objective-C、SwiftUI/UIKit、Xcode 工程及原生资源；实际源构建与设备观测依赖可用的源平台环境。鸿蒙侧构建和验收保持原流程。源侧操作详见 `a2h-spec/references/native-input.md`。

# Step 4.1 / 2.1.2 — 截图主流程 + capture_mode 判定

> 从 SKILL.md §4 Step 4.1 / 2.1.2 抽出。sub-agent 实际截图前 Read。

---

## Step 4.1 总览

**核心优化**：iOS 源端在跨 round 的多轮 verify-fix 循环里**是不变的参照系**——只有 HarmonyOS 代码在被 visual-fixer 改。所以 iOS 基线由 Phase 2 一次性产出到 `screenshots/ios/{trip_id}/{page_id}.png`，Phase 4 里**该 png 已存在即直接复用**（跳过重截 + 跳过 iOS 源端的 scenario 准备）。HarmonyOS 端必须每轮重截。

---

## 快捷方式（推荐）

下方步骤逻辑已封装成 `scripts/capture_or_reuse.py`（纯 python，三平台同一份），可直接调用：

```text
python3 $SKILLS_ROOT/arkts-visual-verify/scripts/capture_or_reuse.py \
  ios emulator-5556 {page_id} {trip_id} "{scenario_chain}" {app_version}

python3 $SKILLS_ROOT/arkts-visual-verify/scripts/capture_or_reuse.py \
  harmony 127.0.0.1:5555 {page_id} {trip_id}
```

退出码：`0`=新截 / `1`=baseline 复用 / `2`=已有图更好跳过(HMOS) / `3`=错误 / `9`=HMOS gate 拦截。

下方手写步骤是脚本内部逻辑的说明，sub-agent 直接调脚本即可，不必复刻。

---

## 2.1-a iOS 源端：baseline 已存在即复用，缺失才截

```text
# OUT = spec/visual-verify/screenshots/ios/{trip_id}/{page_id}.png
# IF OUT 文件存在（bash [ -f ] / PowerShell Test-Path / python os.path.isfile）:
  # baseline 已存在（Phase 2 产出）：直接复用
  打印 "↻ ios {page_id} baseline exists, reuse"
# ELSE:
  # ★单侧化 2026-07-12：缺失**不在 Phase 4 现场补截**（旧 adb 补截废止——现场截绕过 Phase 2
  # 的 needs/grounding/行为账本管道，会造出"有图无账"的半吊子基线，且 Phase 4 常规流程不驱动
  # iOS设备）。缺失 = Phase 2 漏截或合法 BLOCKED：
  #   有 BLOCKED_baseline_{page_id}_{trip}.md → 本页按 SKIPPED 占位引用之（合法不可达）
  #   无 BLOCKED 单 → 写 SKIPPED(reason=baseline_missing) + manifest 记 fatal 项，
  #     主会话收尾后重跑 Phase 2 该页（dispatch 会按 needs 自动补）再重测本页
  打印 "✗ ios {page_id} baseline missing → SKIPPED, 路由回 Phase 2"
```

**关键约束**：

- ✅ **baseline 存在时跳过 Step 4.-1 的 iOS 源端 scenario**（让 scenario_run.py 支持 `--device harmonyos` 单端模式；HarmonyOS 端仍要跑）
- ✅ 多模态读的就是 `screenshots/ios/{trip_id}/{page_id}.png` 这个 baseline 本体

---

## 2.1-b HarmonyOS 端：永远重截（代码在改）

```text
# HarmonyOS 必须用 .jpeg（snapshot_display 不支持 png）
hdc shell snapshot_display -f "/data/local/tmp/vv_{page_id}.jpeg"
hdc file recv "/data/local/tmp/vv_{page_id}.jpeg" \
  "spec/visual-verify/screenshots/harmony/round-{N}/{trip_id}/{page_id}.jpeg"
hdc shell rm "/data/local/tmp/vv_{page_id}.jpeg"
python3 $SKILLS_ROOT/arkts-visual-verify/scripts/resize_screenshot.py \
  "spec/visual-verify/screenshots/harmony/round-{N}/{trip_id}/{page_id}.jpeg"
```

### 2.1-b.2 取 HMOS UI dump（结构 oracle 用，P0-B）

截图后**紧接着**在同一落地态取 HMOS 组件树（dump 不受 1800px 限制，是 JSON 不是图，无需 resize、可放心 recv）：

```text
# uitest dumpLayout 落 /data/local/tmp/layout_*.json，命令 stdout 给出确切路径
hdc shell uitest dumpLayout
# HMOS_LAYOUT = 上面 stdout 里 "saved to:" 之后的路径（无需 tr -d '\r'：py text=True 已归一 \r\n；
#   跨平台一行式：python3 -c "import subprocess,re;o=subprocess.run(['hdc','shell','uitest','dumpLayout'],capture_output=True,text=True).stdout;m=re.search(r'saved to:\s*(\S+)',o);print(m.group(1) if m else '')"）
# IF HMOS_LAYOUT 非空:
hdc file recv "<HMOS_LAYOUT>" \
  "spec/visual-verify/screenshots/harmony/round-{N}/{trip_id}/{page_id}.hmos.json"
hdc shell rm "<HMOS_LAYOUT>"
# dump 失败（个别 ROM / 动画未停）不阻断截图主流程；Step 4.2-pre 取不到时自动跳过结构 oracle。
```

> 与 iOS dump（Phase 2 已存 `screenshots/ios/{trip_id}/{page_id}.ios.xml`）配对，喂给 Step 4.2-pre 的 `structural_diff.py`。

---

## 2.1-c baseline 失效条件（什么时候要重截 iOS）

| 触发器 | 要重截？ | 怎么做 |
|---|---|---|
| iOS APK 改了（重新安装新版本） | ✅ | `run_phase2_ios_survey.py --invalidate-ios-cache` 全清后重跑 Phase 2 |
| scenario YAML 改了（登录流程变了，影响 trip_2 落地态） | ✅ | 同上（或只删受影响 trip 目录） |
| iOS 模拟器换了（不同设备/不同镜像，分辨率可能差） | ✅ | 同上 |
| 仅 HarmonyOS 代码改了（visual-fixer 改 .ets） | ❌ 不该重截 | 这正是 baseline 复用的价值——HMOS 改不影响 iOS |

---

## 2.1-d 用户显式控制（主代理识别意图触发）

| 用户说 | 主代理动作 |
|---|---|
| "重新截一遍 iOS" | `run_phase2_ios_survey.py --invalidate-ios-cache`（清空 screenshots/ios 后重跑 Phase 2） |
| "只刷新 MainPage 这一页的 iOS" | 删 `screenshots/ios/{trip_id}/MainPage.png`（+配对 .ios.xml）后重跑 Phase 2 补图 |

---

## 🚨 BLOCKER 级强制约束：截图必须下采样到 ≤1800px 再读取

<HARD-GATE>

Anthropic 多模态 API 对单图最长边有 2000px 上限。现代模拟器截图（1320×2856 / 1440×3120 等）全部超限，**直接用 Read 工具读原图会抛 `API Error: An image in the conversation exceeds the dimension limit for many-image requests (2000px)`，触发后无法恢复，整轮对话必须从头开始**。

上限设为 1800px（而非 1920px）是为了留 200px 安全余量，防止 sbs 拼图、JPEG 元数据膨胀、多图模式等边界情况下刚好超限。

**规则（MUST 级，零容忍，任何一条违反都会导致不可恢复的 API 错误）**：

1. 每次 `screencap` / `snapshot_display` / `file recv` / `adb pull` **完成后立即**调用 `scripts/resize_screenshot.py` 把图片最长边压到 1800px；无论单页截图、rapid capture、中间 peek 图、debug 图，**一律走 resize**。**任何绕过 resize 直接读图的行为等同于 P0 bug**。
2. Read 工具 / 多模态对比只能读 **resize 之后** 的文件。严禁读原始 `screencap` 输出、严禁读 `/tmp/` 或 `/sdcard/` 未 resize 的拉取产物。**违反此条 = 触发 API 2000px 限制 = 整轮对话作废**。
3. rapid capture 循环（每秒多帧抓过渡页）也必须在每帧拉取完立即 resize，**不能**留到循环结束批量 resize — 中途读 peek 图就会触发超限。
4. 发现任何脚本、辅助工具产出未 resize 的图片，**停止一切操作**，先补 resize 再读，并回写修复到对应脚本。
5. **resize 脚本失败（exit code != 0）时，禁止继续读图**。必须先修复 resize 环境（安装 Pillow / ImageMagick），确认 resize 成功后才能继续。

```text
# 正确范式（iOS）——★单侧化注（2026-07-12）：本范式仅 Phase 2 采集侧适用；
# Phase 4 不驱动iOS（基线复用 Phase 2 产物），sub-agent 禁在 batch 内执行本段
# 原源平台历史命令（iOS 按本文件适配说明执行）: adb -s {device} shell screencap -p "/sdcard/vv.png"
# 原源平台历史命令（iOS 按本文件适配说明执行）: adb -s {device} pull "/sdcard/vv.png" "spec/visual-verify/screenshots/ios/{trip_id}/{page_id}.png"
python3 $SKILLS_ROOT/arkts-visual-verify/scripts/resize_screenshot.py \
  "spec/visual-verify/screenshots/ios/{trip_id}/{page_id}.png"   # ← 必选，不可省

# 正确范式（HarmonyOS）
hdc shell snapshot_display -f "/data/local/tmp/vv.jpeg"
hdc file recv "/data/local/tmp/vv.jpeg" "spec/visual-verify/screenshots/harmony/round-{N}/{trip_id}/{page_id}.jpeg"
python3 $SKILLS_ROOT/arkts-visual-verify/scripts/resize_screenshot.py \
  "spec/visual-verify/screenshots/harmony/round-{N}/{trip_id}/{page_id}.jpeg"  # ← 必选，不可省
```

`capture_or_reuse.py` 已内置 resize（双端分支均在落盘前调 resize_screenshot.py）；写 rapid capture / 自定义脚本时也要同样内置，不要依赖人工记忆。

</HARD-GATE>

---

## 截图完整性验证

```
ios_ok = exists AND size > 10KB AND max_dim <= 1800
harmony_ok = exists AND size > 10KB AND max_dim <= 1800
如两端任一缺失或尺寸超限 → retry once（含 resize），仍失败则 status="blocked"，写 `CRASH_P{page_id}_app_crash_on_screenshot.md` 记录原因
```

---

## Step 4.1.2: capture_mode 判定（分流总开关）

首屏截完后、进入 2.1.3/2.1.4 之前，按以下优先级决定本页的 `capture_mode`，写入 `progress.json`，**单页闭环内锁定**避免轮次抖动：

| 优先级 | 判定信号 | capture_mode | 下一步 |
|--------|---------|-------------|-------|
| **0** | **page_queue 行 / fact-tree 节点已带 `capture_mode: "web"`**（产树期 `annotate_capture_mode.py` 确定性标注，带源码行号证据）——**直接采信**；本页现场 grep 仅做兜底校验，树标了但两端源码都 grep 不到 → manifest 记 `capture_mode_conflict` 警告（不改判） | `web` | [Step 4.1.4 H5/WebView](phase4-webview.md) |
| 1 | （树无标注时兜底）HMOS 页面 ets 文件里检测到 `Web({` + `controller:` / 路径匹配 `*webview*.ets` / iOS 对应 `WebView` + `loadUrl`（⚠️ grep 词边界坑：`WebViewActivity`/中文注释 `WebView是否` 都匹配不上 `\bWebView\b`，认小写 `webview` binding token 更稳） | `web` | [Step 4.1.4 H5/WebView](phase4-webview.md) |
| 2 | 首屏 content_bottom > viewport（[2.1.3-a 规则](phase4-long-page.md#213-a-触发判定)） | `long` | [Step 4.1.3 长页](phase4-long-page.md) |
| 3 | 以上都不命中 | `single` | Step 4.1.5 崩溃检测（详本文档末尾） |

> **检测命令示例**（web 判定，在 arkts 源码里 grep）：
> ```
> grep -rEn "Web\s*\(\s*\{[^}]*src\s*:|new\s+WebviewController" entry/src/main/ets/pages/{page_file}
> # 命中 → capture_mode=web；同时提取 src 表达式与 query 组装代码位置
> ```

---

## Step 4.1.5 — 崩溃检测（每次截图后必须执行）

```text
# HarmonyOS：取 aa dump 里第一条 "mission name" 行，不含 {bundleName} 即崩溃（跨平台一行式；
#   也可直接跑 `hdc shell aa dump -a` 人眼看第一条 mission name）
python3 -c "import subprocess,sys;o=subprocess.run(['hdc','shell','aa','dump','-a'],capture_output=True,text=True).stdout;l=[x for x in o.splitlines() if 'mission name' in x];sys.exit(0 if l and '{bundleName}' in l[0] else print('CRASH on page: {page_id}') or 1)"
# 非零 → 拉起 App 并等 9 秒：hdc shell aa start -a EntryAbility -b {bundleName}
#   status=blocked, reason=app_crash, 跳过当前页

# iOS——★单侧化注（2026-07-12）：Phase 4 不驱动iOS，本段仅历史参考/Phase 2 侧适用
python3 -c "import subprocess,sys;o=subprocess.run(['adb','-s','{device}','shell','dumpsys','activity','top'],capture_output=True,text=True).stdout;l=[x for x in o.splitlines() if 'mResumedActivity' in x];sys.exit(0 if l and '{package}' in l[0] else print('CRASH on iOS page: {page_id}') or 1)"
```

崩溃后写 `CRASH_P{page_id}_app_crash_on_{phase}.md`，schema 见 [`fix-file-schema.md`](fix-file-schema.md) §六 CRASH 段。
