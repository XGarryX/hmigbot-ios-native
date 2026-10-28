> **iOS .39 准备数据**：源码引用回填继续调用原匹配器，在私有输入镜像映射文件级 source_anchors，输出规范 ios_source_refs；保留原未匹配项。Step 1.1.6 对 iOS 使用：`python3 "$SKILLS_ROOT/arkts-visual-verify/scripts/extract_dialog_ids.py" --ios-root "$IOS_SOURCE_ROOT" --package "$IOS_BUNDLE_ID" --project-root "$PROJECT_ROOT" --out "$PROJECT_ROOT/spec/visual-verify/native_dialog_catalog.json"`。此文件是静态声明目录，`partial_unknowns` 必须传给行走者补查，不代表动作或验收通过；旧 dialog_id_catalog.json 留存但 iOS 分支不读。下文旧 Android catalog 命令仅属历史分支。

> **iOS .33 执行分支**：先读 [Xcode 原生源流程](native-xcode-source.md)，源端派发同时附 [native-source-batch-prompt](native-source-batch-prompt.md)。本文件的业务/账目/预算语义保留；旧 adb/Activity/uiautomator/pm clear 示例只属 Android 历史源分支。iOS 用本工程独占的 XCUITest session，原目标 HDC 与全部门禁不变。

> **iOS 源输入**：读取 Swift/Objective-C、SwiftUI/UIKit、Xcode 工程及原生资源；实际源构建与设备观测依赖可用的源平台环境。鸿蒙侧构建和验收保持原流程。源侧操作详见 `a2h-spec/references/native-input.md`。

# Phase 1 — 准备

> 从 SKILL.md §4 Phase 1 抽出。Phase 1 真正进入时 Read。
> 包含 Step 1.0 / 1.1 / 1.2 / 1.2.5 / 1.3 全部执行细则。

---

## Step 1.0: 确保 toolkit-fact-tree.json 完备（**委托统一调度器**，禁止分支化跳过）

> **历史事故根因**：之前 Step 1.0 是 `IF NOT exists(spec/toolkit-fact-tree.json)` 纯存在检查。半成品 tree（文件存在但 reach_paths=0%）被当成"OK"放过，visual-verify 深层页全够不着。
>
> **为何委托调度器（v6.6 重构）**：第一版门控 FAIL 时写死调 `toolkit-fact-indexer → app-relationship-tree`——这是**纯 XML/传统链**，对 **Compose / 混合架构应用会产空树**（toolkit 啃不动 Compose）。现已有统一调度器 `ios-fact-tree`：它**确定性判架构**（XML/Compose/混合）→ 分发到对应生成器 → 自带产出闸。所以 visual-verify 不再自己挑生成器，**gate FAIL → 统一调 `$ios-fact-tree`**，怎么产树（含三态路由）全交给它。这既简化又让 Compose/混合应用自动可用。

### 步骤（写死，不允许变形）

```
1. 跑 gate 脚本（zero LLM，秒级）；**--source 必带**：
   python3 $SKILLS_ROOT/arkts-visual-verify/scripts/check_prereq_freshness.py \
        spec/toolkit-fact-tree.json --source <ios_source_root>
   记下 exit code（bash `$?` / PowerShell `$LASTEXITCODE`）
   # ⚠️ --source 不是可选：gate 的 PASS/FAIL 判定本身依架构而变——compose/混合树合法 purpose=null，
   #    缺 --source 会被默认按 traditional 查 purpose≥70% → 合法 compose 树被误判 NEED、永远过不了。
   #    （NEED 后缀仍不用来分支——remediation 永远是调度器；但 --source 决定 PASS/FAIL 本身。）
   #    <ios_source_root> = 本次迁移的iOS工程根（a2h-spec/app-relationship-tree 同一输入）。

2. IF stdout == "PASS" (exit 0):
     2.0-fn  ★功能维度门控（补结构闸盲区，2026-06）：结构闸 PASS 不代表功能维度就绪——
             check_prereq_freshness **不看 functional_checks**，结构完整但功能空的树会静默漏测。
             跑：python3 $SKILLS_ROOT/arkts-visual-verify/scripts/check_functional_dimension.py \
                     spec/toolkit-fact-tree.json <hmos_project>
             - exit 0 (OK) → 功能维度就绪 或 合法无功能点 → 进 2.0
             - exit 2 (NEED:functional-*) → **走下方 2.a 同款**：$ios-fact-tree 指向iOS源
               （它 §3.5 自产 registry→注入→机械闸；XML/Compose 自动分流）→ 再跑本闸确认 OK → 进 2.0
             > 防无限重触发：本闸用 registry 文件存在性当"已尝试"标记——纯 UI/无功能点项目产空 registry 后恒 OK，不每轮重跑。
     2.0  跑 enrich 步（见下方 Step 1.0.5），完成后进 Step 1.1

   IF stdout 包含 "NEED:" (exit 2):
     # 不看 NEED 后面是什么、不自己挑生成器——统一委托调度器
     2.a  $ios-fact-tree  ← 指向 <ios_source_root>
          → 它跑 dispatch.py plan 确定性判架构（XML/Compose/混合）
          → 分发到对应生成器（写死链路，各自带内部质量门 + 自愈）：
              传统 = toolkit-fact-indexer → app-relationship-tree
              Compose = swiftui-fact-tree（Phase 2–7）
              混合 = XML 半边 + Compose 补充叠加 + 跨架构缝合
          → 跑 dispatch.py gate 自检（产出契约闸 + 混合连通闸）
     2.b  再跑一次本 gate 脚本确认 PASS
          - PASS → 跑 enrich 步（见 Step 1.0.5），完成后进 Step 1.1
          - 仍 FAIL → 升级用户（不在 visual-verify 内死循环）

   IF exit == 3:
     升级用户（python3/依赖缺失等环境问题）
```

### Step 1.0.5: 反哺 a2h-spec 的 source_anchors 到 fact-tree（**必跑**）

```
python3 $SKILLS_ROOT/arkts-visual-verify/scripts/enrich_factree_anchors.py
       --fact-tree spec/toolkit-fact-tree.json
       --page-spec-dir spec/baseline/ui
```

**为什么必跑**：
- a2h-spec 把每个页面的 iOS 源（Kotlin / layout XML / ViewModel / 基类）路径写在 `spec/baseline/ui/page_*.md` 头部 YAML 的 `source_anchors`
- 但 toolkit-fact-indexer 不读 page_*.md，所以 fact-tree.pages[].ios_source_refs **永远是 null**
- 下游 `inject_factree_refs.py` 拿不到 refs → 工单 §1 "Spec 引用" 一直写 "iOS 源参考缺失"
- visual-fixer 看不到 iOS 源 → **凭眼测改色**（实测 41% attempts 是这种情况）
- 本脚本就是这座缺失的桥：page_*.md → fact-tree.ios_source_refs

**幂等**：脚本每次 overwrite ios_source_refs，跑 N 次和跑 1 次一样。

**失败处理**：
- a2h-spec 没产 page_*.md → 脚本 warn，fact-tree 不改（ios_source_refs 还是 null），inject 依然写"参考缺失"。**不报错**（visual-verify 还能跑，只是 fixer 会眼测）
- YAML 解析失败 → 脚本带容错（缺空格 `KEY:"VALUE"` 自动补），跑不通的 warn 单个 page 跳过，不影响其它

**期望产出（跑完看 stdout）**：
```
✓ spec/toolkit-fact-tree.json
  enriched=29/62 (matched page_spec=24)
✓ spec/.cache/fact-tree/draft.json
  enriched=28/57 (matched page_spec=22)
```

`enriched > 0` = 至少有些 page 有 iOS 源路径了。若 `enriched=0`，去查：(a) spec/baseline/ui/page_*.md 文件存不存在；(b) page_*.md YAML 头里有没有 `source_anchors:` 段。

### Step 1.0.6: 构建 spec 验收旁路 `spec_oracle.json`（feat 单注入用，**非致命**）

```
python3 $SKILLS_ROOT/arkts-visual-verify/scripts/build_spec_oracle.py \
       spec/baseline  spec/visual-verify/spec_oracle.json
```

**作用**：把 `spec/baseline/features/F*.md` 的 `## 验收标准` 段切成 snapshot，连同 locator + `page→feature`/`域→feature` 映射（取自 `feature-index.md` 功能清单"涉及页面"列）落到旁路 JSON。**出单时**由 B.4.5 第 5 步的 `inject_spec_oracle.py` 按 `page_id`（兜底 `feature_path` 域）O(1) 查表，把验收契约注进 **feat 单 §2 期望**。

**为什么这样设计（与 ios_source_refs 注入对称、但只补 feat 单）**：
- feat 单（IMPL_MISSING）修复缺"行为契约"——`expected_ios` 只是一句话实测态；`## 验收标准`（几档/默认/持久化/边界）才是 fixer 端到端实装的真参考。ui 单真值是截图（自足），**不注入**。
- **不塞 fact-tree**（树不胖：只在出单时按键查旁路）；**不每单重读 spec**（snapshot 已切好，emit 是 dict 查）；**解析失败显式 `UNRESOLVED`**（旁路里非静默兜底，fixer 知道去手读 spec，不静默遗漏）。
- join 命门：`logical_feature_id` 是源文件派生 slug（接不上 F-id），唯一可用信号 = feature-index"涉及页面"列的模糊匹配；匹配失败在**本 build 步**一次性暴露（stderr 覆盖率 + 缺验收段警告），不漏到 emit。

**失败处理（非致命，跟 1.0.5 同档）**：
- 没有 `spec/baseline/features/` → 脚本仍产空壳旁路，出单时全 `UNRESOLVED`（fixer 退回手读源码，与现状无异，不阻断 visual-verify）。
- 某 F 缺 `## 验收标准` 段 / 某页 join 不到 feature → stderr 警告 + emit 期该单写 UNRESOLVED；属 spec 数据质量缺口，记下反馈 a2h-spec，不阻断本轮。

**幂等**：每次 overwrite 旁路 JSON，跑 N 次 = 跑 1 次。

### 铁律（违反一条算事故）

1. **必须先跑 gate 脚本**——不允许 `ls spec/toolkit-fact-tree.json` 或心算"上次跑过了应该 OK"。
2. **gate FAIL → 统一调 `$ios-fact-tree`**（指向 iOS 源根），**不允许自己挑生成器、不允许按 NEED 后缀手动只调一个**。架构判定 + 三态路由 + 自检全是调度器的职责；visual-verify 自己心算"这是 XML 应该调 toolkit"= 给模型留跳过/判错口子（且对 Compose 会产空树）。
3. **必须用 Skill 工具调起 `ios-fact-tree`**——不允许 subprocess 直接调 dispatch.py/生成器脚本绕过。调度器 + 各生成器自己有质量门 / 重试 / 自愈循环，subprocess 会丢这些。
4. **第二次 gate 仍 FAIL → 升级用户**，不允许"差不多就行了"继续，也不允许在 visual-verify 这层第三次 retry——前置 skill 各自有自己的内部循环，那才是该解决的地方。
5. **不允许人工修改 fact-tree.json 来糊弄 gate**——阈值是实测校准的最小可用值，低于就深层页到不了。

### 阈值依据

| 检查项 | 阈值 | 字段（兼容多套版本） | 不达标的现象 |
|---|---|---|---|
| pages 数组长度 > 0 | 任意 | `.pages` | 整树空 |
| 顶层 8 字段齐 | schema 契约 | top-level | 下游脚本崩 |
| `purpose` 非 null 占比 ≥ 70% | LLM 已读源码 | `.purpose` | sub-agent 不知道每页是干啥的 → scenario 准备凭经验猜 |
| reach 路径非空占比 ≥ 50% | 多源 BFS | `.reach_paths`（toolkit 复数）OR `.reach_path`（v6.3 单数）| 没有"点 A 再点 B 再点 C"指令链 → 深层页全够不着 |
| 导航网非空占比 ≥ 80% | LLM 补了"怎么到达"结构化数据 | `.navigation_contract.trigger_actions` 非空 OR `.inbound_triggers` 非空 OR `.navigation.inbound` 非空 | sub-agent 不知道从哪点进 |
| `contract_uncertain` 占比 ≤ 30% | v6.4 LLM 推断未通过源码验证的不能太多 | `.navigation_contract.contract_uncertain == true` | 太多不确定项 → 遍历器（walk_exec）卡 |

> **阈值依据**：
> - `navigation_contract` 是 v6.4 起 visual-verify Phase Alpha 的主消费字段，应接近 100%；门槛 80% 已经放宽。
> - 同时兼容 v6.2 字段 `inbound_triggers` 和 toolkit 原生 `navigation.inbound`——任一非空即算"导航网这条 record 上有"。这样老 fact-tree 也能通过。

任一不达标的实例：本仓在引入 gate 脚本前，fact-tree exists 但 reach_paths=0%（脚本一跑就抓出），visual-verify 实测只能截 9 个 HomePage tile，深层 FileScanContent / ScanPage / ImageCutting / Content / CardScanContent 等 10 个页全部 0 覆盖。

---

## Step 1.1: 验证前置条件（含自动启动模拟器）

逐项检查 SKILL.md §2 中的条件。**模拟器未运行时先自动尝试启动，失败才升级给用户。**

```text
[历史源平台示例：不适用于 iOS，不可执行。iOS 源设备/构建按本文件适配及 native-input 协议；目标 hdc/hvigor 检查仍须实际执行。]
# ── 1.1.a 检查 adb / hdc 可用性（不可自动修复，直接升级用户）──
# 跨平台定位：python3 $SKILLS_ROOT/arkts-visual-verify/scripts/lib_tools.py 打印 {"adb":..,"hdc":..}
#   （env ADB/HDC > PATH > 平台候选：macOS ~/Library/iOS/sdk、/Applications/DevEco-Studio.app；
#    Windows %LOCALAPPDATA%\iOS\Sdk、C:\Program Files\Huawei\DevEco Studio；见 windows-setup.md）
IF lib_tools 输出的 "adb" 是裸名（未定位到真实路径）:
  升级用户: "请安装 iOS SDK 并确保 adb 在 PATH 中（或设 env ADB）"
IF lib_tools 输出的 "hdc" 是裸名:
  升级用户: "请安装 HarmonyOS SDK 并确保 hdc 在 PATH 中（或设 env HDC）"

# ── 1.1.b 自动启动 iOS 模拟器 ──
IOS_ONLINE = `adb devices` 输出里（表头 List 行之外）存在状态为 device 的行
IF !IOS_ONLINE:
  打印: "⚠️ iOS 模拟器未运行，尝试自动启动..."
  # 探测可用 AVD
  AVD_LIST = `emulator -list-avds`
  IF AVD_LIST 为空:
    升级用户: "未找到任何 iOS AVD，请先在 iOS Studio 中创建模拟器"
    ABORT
  AVD_NAME = AVD_LIST 第一行（默认取首个 AVD）
  # 后台启动（-no-window 可选，CI 场景下加；本地开发不加）
  后台启动 `emulator -avd {AVD_NAME}`（bash: 末尾加 `&`；PowerShell: `Start-Process emulator -ArgumentList "-avd","{AVD_NAME}"`）
  # 轮询等待上线，最多 120 秒
  FOR i IN 1..24:
    sleep 5
    IF `adb devices` 输出里存在状态为 device 的行:
      # 再等 boot 完成
      `adb wait-for-device shell getprop sys.boot_completed` == "1"
      打印: "✅ iOS 模拟器 {AVD_NAME} 已启动"
      BREAK
  IF 仍未上线:
    升级用户: "iOS 模拟器启动超时（120s），请手动启动后重试"
    ABORT

# ── 1.1.c 自动启动 HarmonyOS 模拟器 ──
HMOS_ONLINE = `hdc list targets` 有非空输出且不含 "Empty"
IF !HMOS_ONLINE:
  打印: "⚠️ HarmonyOS 模拟器未运行，尝试自动启动..."
  # 探测 DevEco 模拟器可执行文件
  DEVECO_EMU = 在 DevEco 安装目录（macOS /Applications/DevEco-Studio.app；Windows $env:DEVECO_HOME）
               下递归找名为 devicemanager 或 emulator 的可执行文件，取第一个
               （python3 -c "import pathlib,sys;r=pathlib.Path(sys.argv[1]);print(next((p for p in r.rglob('*') if p.name in ('devicemanager','emulator','emulator.exe')),''))" <DevEco目录>）
  IF DEVECO_EMU 为空:
    # 回退：尝试命令行直接拉起（PATH 里的 deveco-emulator）
    DEVECO_EMU = `deveco-emulator` 若在 PATH 中（bash: which / PowerShell: Get-Command）
  IF DEVECO_EMU 为空:
    升级用户: "未找到 HarmonyOS 模拟器可执行文件，请手动从 DevEco Studio → Tools → Device Manager 启动模拟器"
    ABORT
  # 后台启动
  后台启动 `{DEVECO_EMU}`（bash: 末尾加 `&`；PowerShell: `Start-Process`）
  # 轮询等待 hdc 可连接，最多 120 秒
  FOR i IN 1..24:
    sleep 5
    # 远程模拟器可能需要 tconn
    `hdc tconn 127.0.0.1:5557`（忽略报错）
    IF `hdc list targets` 有非空输出且不含 "Empty":
      打印: "✅ HarmonyOS 模拟器已启动"
      BREAK
  IF 仍未上线:
    升级用户: "HarmonyOS 模拟器启动超时（120s），请手动从 DevEco Studio 启动后重试"
    ABORT

# ── 1.1.d 保证设备包新鲜（构建锚点②：遍历开始前，**每轮无条件跑本检查**）──
# ★ 历史（2026-08-11，血泪）：
#   visual-fixer 改完 .ets 是「落盘即退，不重编、不复测」。更旧的版本这里写的是
#   `IF !APK_INSTALLED OR !HAP_INSTALLED` 才装、且装的是现成产物——于是第二轮起
#   整个分支被跳过，截的还是上一轮那个**旧二进制**。修改永远上不了设备 →
#   similarity 永远 < 0.95 → disposition 永远到不了 fixed → 无限轮次且"修复效果不佳"。
#   （再旧的设计把重编委托给 a2h-verify，单独调用时整条断掉。）
# ★ 构建点重排（2026-08-12，用户拍板 O(batch)→O(1)）：
#   「每轮无条件」的对象是**新鲜检查**，不再是重编本身——Phase 6.8（fix 后置构建）
#   出包+装机成功会打新鲜戳，本步 --skip-if-fresh 见戳秒过（同一批改动只编一次）；
#   无戳（首个 round / 上个构建点没成功 / 会话中断过）才真正重编。
#   语义不变：开始截图时设备上的包 ≡ 当前源码。重复劳动砍掉。
#   iOS 源侧不重建——它是固定对照基线，不该随迁移代码变化。
打印: "🔨 校验设备包新鲜度（无戳则重编）..."
python3 $SKILLS_ROOT/arkts-visual-verify/scripts/auto_install_artifacts.py \
  --ios-root {ios_project_root} --package {package} \
  --hmos-root    {hmos_project_root}    --bundle  {bundleName} \
  --rebuild --skip-if-fresh
CASE 脚本 exit:
  0 → 继续
  3 → 构建失败 → 自动调 $hmos-fix-build-errors（指向 {hmos_project_root}，
      其内部自带构建→修错→再构建循环）：
        修好 → 复跑本脚本 --rebuild（不带 --skip-if-fresh，确保装上修复后的包）→ 继续
        它也修不动 → 升级用户: "HAP 构建失败且自动修复未果，已停止（禁止拿旧包截图）"
                     ABORT
      ★ 本构建点最多自动修一次；与 Phase 6.8 是同一路由（见 phase6-summary.md §6.8）
  * → 升级用户: "auto_install_artifacts.py 装机失败，请检查设备与产物"
      ABORT

# ── 1.1.e 其他前置条件 ──
# 多模态模型可用性等，按原逻辑检查

# ── 1.1.f 三级前置探针：UNIT fail-fast + OPTIONAL 降级告知（standalone 体验核心）──
# 前置分三级：REQUIRED（fact-tree/设备/HAP，Step 1.0 与上面 1.1.a-d 已把守）、
# UNIT（自闭环单元成员：scenario_run.py + visual-fixer/reviewer agent，缺一个循环转不起来）、
# OPTIONAL（a2h-spec 等上游增益产物，缺失合法但相关维度降级）。
# 单独调用 visual-verify 时没有 a2h-spec 产物完全正常——但要在第一屏告知降级边界，
# 不许等到 Phase 4 用户才发现"feat 单为 0 / fixer 只能眼测"。
python3 $SKILLS_ROOT/arkts-visual-verify/scripts/check_dimension_prereqs.py \
  --project-root {hmos_project_root}
CASE 脚本 exit:
  0 → 把打印的「维度启用/降级表」原样转述给用户（首屏），继续
  2 → 升级用户: "自闭环单元成员缺失（scenario-runner 脚本或 visual-fixer/reviewer agent），
      按脚本提示安装后重跑" → ABORT
  3 → a2h-spec 产物整体缺失（从没跑过）→ **自动调 `$a2h-spec`**（指向
      <ios_source_root>，与 Step 1.0 传给 gate 的 --source 同一个）→ 跑完复跑本探针：
        exit 0 → 转述维度表，继续
        仍 exit 3 → **只自动调这一次**，按全降级继续（表已打印），并告知用户
                    "a2h-spec 自动补齐未产出 baseline，本轮按降级模式跑"
```
> **exit 3 的三条纪律**（与 Step 1.0 fact-tree 同模板）：
> 1. 必须用 **Skill 工具**调 a2h-spec，不许 subprocess 绕过——它内部的质量门/审批点是产物可信的前提。
> 2. a2h-spec 若在其内部审批门停下等用户，属它自身流程，正常交互即可；**不许为了"全自动"替用户批**。
> 3. 只在"整体缺失"（page_*.md 与 feature spec 双缺）时触发；部分缺失走降级——已跑过的 spec
>    整重跑代价不成比例，且会覆盖用户可能已审过的 baseline。

> **启动策略说明**：
> - iOS 源端使用 `emulator -list-avds` 探测 + `emulator -avd` 启动，这是 iOS SDK 标准 CLI，无需 iOS Studio GUI。
> - HarmonyOS 端优先探测 DevEco Studio 内置的模拟器管理工具；路径不固定，用 `find` 动态定位。
> - 两端都给 120 秒超时（每 5 秒轮询一次，共 24 次），覆盖冷启动场景。
> - 启动成功后继续原流程；超时或找不到可执行文件则**升级给用户并 ABORT**，不做静默跳过。

### Step 1.1.5: 禁用 iOS 全局动画（**建议默认设 0，对静态页无影响**）

```text
# 关 3 个 animation scale，让 uiautomator dump 不再被 splash/transition 动画卡死在等 idle
# 原源平台历史命令（iOS 按本文件适配说明执行）: adb -s {device} shell settings put global window_animation_scale 0
# 原源平台历史命令（iOS 按本文件适配说明执行）: adb -s {device} shell settings put global transition_animation_scale 0
# 原源平台历史命令（iOS 按本文件适配说明执行）: adb -s {device} shell settings put global animator_duration_scale 0

# 自检（部分 iOS 版本返回 "0.0"，部分返回 "0"；兼容两种）——跨平台 python 一行式，
# 由 py 的 text=True 归一 \r\n，无需 tr -d '\r'
python3 -c "import subprocess,re,sys;v=subprocess.run(['adb','-s','{device}','shell','settings','get','global','window_animation_scale'],capture_output=True,text=True).stdout.strip();sys.exit(0 if re.fullmatch(r'0(\.0+)?',v) else print('❌ 动画关闭失败（实际值=%s）'%v) or 1)"
```

**为什么默认设 0**：
- `uiautomator dump` 实现里"等 idle"才返回 XML
- **有持续动画的页**（Splash logo / MemberCenter lottie / 长 loading）→ idle 永远不来 → dump 报 `ERROR: could not get idle state` → 所有依赖 dump 的脚本（dismiss_popups.py / click_and_verify_edge.py / blackbox_explore.py）全跪
- **静态页**（HomePage / Settings 等无持续动画）→ idle 自然达成，dump 正常，关不关动画都无所谓
- 由于"无法预知本轮要测哪些页是动画密集型"，**默认设 0 是最安全的零代价默认**

**什么时候不该关动画**：
- 显式要验"按钮按下动效"等动画行为时（极少；目前 visual-verify 不做这类验证）
- 此时把这步标 SKIP 并在 progress.json 记理由，避免下游脚本误以为环境异常

**恢复（可选）**：测试结束后主会话可选还原：
```text
# 原源平台历史命令（iOS 按本文件适配说明执行）: adb shell settings put global window_animation_scale 1
# 原源平台历史命令（iOS 按本文件适配说明执行）: adb shell settings put global transition_animation_scale 1
# 原源平台历史命令（iOS 按本文件适配说明执行）: adb shell settings put global animator_duration_scale 1
```

### Step 1.1.6: 生成 dialog_id_catalog.json（弹窗关闭路由表）

```text
# 从 iOS 源码扫所有 res/layout/dialog_*.xml，提取按钮 resource-id 到 catalog
# 后续 dismiss_popups.py / sub-agent 关弹窗时按 catalog 找 close/confirm 按钮，不靠像素坐标
python3 $SKILLS_ROOT/arkts-visual-verify/scripts/extract_dialog_ids.py \
  --ios-root {ios_project_dir} \
  --package {applicationId} \
  --out spec/visual-verify/dialog_id_catalog.json
```

**输出**：每个 dialog 列 `close_ids` + `confirm_ids` + `all_ids` 三组 resource-id（全限定，含包名前缀）。catalog 永久生效（除非 iOS 源码改了 dialog 布局，正常迁移期不会改）。

### Step 1.1.7: 冷启广告探针（无 ad_profile 时才跑；2026-08-12 新增）

> 实爆 2026-08-11：项目无 `script_test/config/ad_profile.json`，chunk 内撞上冷启付费墙 →
> "chunk 投降写单(47m) → 派 builder(68m) → 重派补采(3h+)" 三段全新上下文往返，只为关一个弹窗。
> ad_profile 是**每项目学一次**的资产，天然属于准备阶段——最常见的冷启墙在这里就能撞出来。

```text
# 只在项目无 profile 时探一次（有 profile 直接跳过本步）
# IF script_test/config/ad_profile.json 不存在（bash: [ ! -f ... ]；PowerShell: !(Test-Path ...)）:
# 原源平台历史命令（iOS 按本文件适配说明执行）: adb -s <IOS_SERIAL> shell am start -n {ios_pkg}/{launcher_activity}
# 等 8 秒让 splash 落地（后续 chunk 起点自己会 pm clear，本次冷启不毒害 trip_1 首启链——
#   MMKV 首启标记随 pm clear 重置，引导链必然重弹）
# 原源平台历史命令（iOS 按本文件适配说明执行）: adb -s <IOS_SERIAL> shell uiautomator dump /sdcard/probe.xml
# 原源平台历史命令（iOS 按本文件适配说明执行）: adb -s <IOS_SERIAL> pull /sdcard/probe.xml <TEMP>/probe.xml     # <TEMP>=系统临时目录（/tmp 或 %TEMP%）
```

**触发判据（两个条件缺一不派，防假阳性白烧 builder）**：
1. dump 失败报 `could not get idle state`（或 dump 成功但内容为广告全屏层）；
2. **且**屏上有促销证据——dump/截图含 促销·倒计时·会员·限时·优惠·¥ 类词，或 resumed activity 是
   Member/Vip/Promo 类名。**长 splash 动画同样报 could not get idle**（ad_dismiss.py 为此专设
   `dump_empty_unsafe`），只凭条件 1 就派 builder = 无广告 app 白烧一小时。

两条都命中 → **当场派 ad-profile-builder agent**（产 `script_test/config/ad_profile.json`），
学完再进 Phase 2。两条没齐 → 照常进 Phase 2。

⚠️ **本探针绿灯≠不会撞墙**：深页插屏/登录后弹层探不到（builder 自述"深页插屏学不到"）——
chunk 内 `need_ad_profile` 的 at-need 路由（batch prompt 1.3 exit 11 + 机械止损 §页级）**原样保留**，
本步只是把最常见的冷启墙从"chunk 现场三段往返"前移成"准备期一次学会"。

---

## Step 1.2: 构建**全树页面索引** page_queue.json（不是采集集）

> ⚠️ **SKILL.md §0 Context Discipline 铁律重申**：禁止 Read `spec/toolkit-fact-tree.json` —— 走脚本生成紧凑 `page_queue.json` 再 Read 它。

```text
# 由本 skill 用 Bash 工具调用，输出紧凑队列：
python3 $SKILLS_ROOT/arkts-visual-verify/scripts/build_page_queue.py \
    --tree spec/toolkit-fact-tree.json \
    --out  spec/visual-verify/page_queue.json
```

脚本行为（实现细节见脚本 docstring）：
1. 合并 `tree.pages[] + tree.fragments[] + tree.dialogs[]` 进统一队列（fragments / dialogs 是独立测试目标，每个 Dialog/DialogFragment 单独触发）
2. 按 `dependency_graph.layers` 拓扑排序: Foundation → Auth → Monetize → Core AI → Extended → Shell
3. 每层内按 `(priority asc, name asc)`：P0 在前 P2 在后
4. 输出 entries 只包含 `{name, file, priority, kind, feature_ids, layer}` —— 紧凑，可放心 Read

铁律：
- priority（P0/P1/P2）仅用于**排序**，不作为过滤——**本队列内**不许按优先级挑着测
- ⚠️ **page_queue.json ≠ 鸿蒙采集集**（2026-07-25）：本队列是**全树清单**，用于排序/索引/查找；
  真正的鸿蒙采集集由 Phase 3.5 `build_batches.py` 从**iOS Phase 2 覆盖集**产出（见 SKILL.md §1.1
  第 4 条「鸿蒙采集集 ≡ iOS覆盖集」）。iOS没覆盖的页**没有 GT**，进队列只会产生假 PASS 或噪音。
  两者数量不等是**正常**（实测 80 vs 31），不是漏测——差额由债账（`_baseline_debt.json` /
  `_hmos_queue_excluded.json`）承载，`assert_run_success.py` cond 6 机械核对。
- 如需某页的 navigation/sub_components 详情，用 python 一行式按需取片段：`python3 -c "import json;print([p for p in json.load(open('spec/toolkit-fact-tree.json'))['pages'] if p['name']=='X'])"`；**禁整文件 Read**

> **铁律（2026-07-25 修订）**：visual-verify 单 run 必须测**采集集内的所有页面**（含 fragments /
> dialogs），priority 只决定先后顺序，不决定测不测。"P0 队列"是历史误用措辞。
> **采集集 = iOS覆盖集**，不是全树——旧表述"必须测所有页面（全量页面队列）"是**单侧化之前**的
> 遗留，与 SKILL.md §1.1 第 4 条直接冲突，已作废。iOS没覆盖的页无 GT，**不测是对的**；
> 但"iOS没覆盖"必须二分：真不可达=合法出界，漏采=**债**（须补采，不许当成"不用测"）。

---

## Step 1.2.5: 页面可达性预分类（保留，但作用已收窄）

> **作用范围（2026-07-25 澄清）**：本步产 `progress.json.reachability`，全仓**唯一实际消费者**是
> [phase4-scenario.md](phase4-scenario.md) 的 `login_walled → 默认 login scenario` 兜底。
> 它**不决定测不测**——采集集由 Phase 3.5 从iOS覆盖集定（SKILL.md §1.1 第 4 条），
> 且采集集内的页多半iOS侧已跑通建态。所以本步是**给建态选配方的提示**，不是覆盖闸。
> 分类信号建议取 `fact-tree.preconditions[]`（`preconditions_enhancer` 产，带 `evidence_file:line`
> 源码证据，可审计），比下方散文里的 grep .ets 更准。

对队列中每个页面，判断可达性并分类：

```
FOR EACH page IN queue:
  1. grep 页面代码是否包含 login/token 检查:
     grep -l "LoginPage\|isLogin\|checkLogin\|token" {page}.ets
  2. 检查 toolkit-fact-tree.json 中的依赖关系:
     - 依赖 F002(Auth) 的功能所属页面 → login_walled
  3. 检查页面是否需要前序参数:
     grep "RouterUtils.getParamByName\|context.pathInfo.param" {page}.ets
     - 有参数依赖且无默认值 → data_dependent
  4. 分类结果:
     - public: 无需登录、无需参数，可直接导航到达
     - login_walled: 需要登录才能访问
     - data_dependent: 需要前序页面传参（detail 页、result 页等）

处理策略（**已改为场景驱动 + 缺口必报告**，禁止 silent skip）:
  - public 页面: 执行完整 Phase 4（截图 → 对比 → 写 round-N markdown）
  - login_walled 页面: 先调 arkts-scenario-runner 跑 `login` 场景把 App 开到已登录态，然后执行完整 Phase 4
  - data_dependent 页面: 在 `page_scenarios.json` 里声明该页的前置场景（如 `upload_image`），runner 先把 App 带到目标状态，再执行 Phase 4
  - **若对应场景不存在 OR scenario-runner 无法实现**（如需要支付/NFC/真实短信等人工不可绕开） →
      status = "blocked"
      写一份 `CRASH_P{page_id}_scenario_required_{scenario}.md` 到 round-N/ui/
      → **不允许 silent skip**——必须有 markdown 产出，让人工看到缺口
```

> **铁律：采集集内的页一个都不许静默跳过**——`status: "skip"` 已废弃。**采集集内**任何无法实际截图的页面都必须**写一份 CRASH markdown 记录缺口**，否则下游消费者会以为该页"已对齐"。详见 alignment-rules.md §3 升级用户和 [fix-file-schema.md §六 CRASH(scenario_required)](fix-file-schema.md)。
>
> ⚠️ **区分两类"没截图"（2026-07-25）**：
> - **采集集内没截到** → 真缺口，**写 CRASH md**（本铁律管的就是这类）
> - **本就不在采集集**（iOS无 GT）→ **不写 CRASH md**（写了是噪音，会把"无需测"伪装成"测失败"），
>   改由债账 `_hmos_queue_excluded.json` 承载：`blocked`=债须补采 / `skipped_structural`=合法出界。

**页面到场景的映射**（`spec/visual-verify/page_scenarios.json`）：
```json
{
  "defaults": {
    "login_walled": "login"
  },
  "pages": {
    "ContentDetailPage": ["login", "upload_image"],
    "VideoDetailsPage": ["login", "goto_video_list"]
  }
}
```
没有该文件时，login_walled 统一用 `login` scenario，data_dependent 走 Step 1.2.5 / Step 4.-1 的 **scenario_required CRASH 路径**（写 markdown 记录缺口，不 silent skip）。

---

## Step 1.3: 创建输出目录与进度文件

```text
# 按 trip_id 分目录（双态页 logged_out/logged_in_vip UI 不同，必须分开存）
# ROUND = python3 $SKILLS_ROOT/arkts-visual-verify/scripts/lib_resolve_round.py 打印的 round 号（读 _state.yaml.current_round）
# 对 TRIP_ID ∈ {trip_1_logged_out, trip_2_logged_in_vip} 各建三个目录（跨平台一行式）：
python3 -c "import os,sys;R=sys.argv[1];[os.makedirs(d,exist_ok=True) for t in ('trip_1_logged_out','trip_2_logged_in_vip') for d in (f'spec/visual-verify/screenshots/ios/{t}',f'spec/visual-verify/screenshots/harmony/round-{R}/{t}',f'spec/visual-verify/screenshots/sbs/round-{R}/{t}')]" <ROUND>
```

初始化或恢复进度文件 `spec/visual-verify/progress.json`：

- **首次某全局轮**（spec/fix/_state.yaml.current_round 与 progress.json.current_round 不同）：把所有页面（pages + fragments + dialogs）重新入队，全量重测，看上轮 fixer 改动有没有引入回归
- **断点续跑某全局轮**（current_round 一致）：跳过 `pages` 中 `status` 已为 `pass`/`fail`/`blocked` 的页面，仅处理 `queue_remaining` 中的
- **⚠️ 保留未知顶层键（2026-07-10）**：初始化/重置 queue 只改本节列出的键，**禁止整文件重写**——progress.json 还承载 `scenario_attempts`（run_scenario_with_verify 失败计数器）和 `states_provisioned`（数据态 checkpoint 配方注册表，SKILL 步骤 2.5 / phase4-dispatch 0.b 写入），整写会抹掉它们 → 计数器归零绕过自修上限、数据态被重复造（烧消耗型配方）

```json
{
  "last_updated": "<ISO8601>",
  "project": "<bundleName>",
  "current_round": 2,                  // 与 spec/fix/_state.yaml.current_round 同步；不一致 → 重置 queue
  "pages": {},                         // 见下方 Step 4.5 的 page 结构
  "queue_remaining": ["Index", "HomePage", ...],
  "reachability": {
    "public": ["Index", "HomePage", "MineSettingPage", ...],
    "login_walled": ["CreditsPage", "MembershipPage", ...],
    "data_dependent": ["VideoDetailsPage", "ContentDetailPage", ...]
  }
}
```

> **断点续跑规则**：同一全局轮内的本 skill 单 run，已有结论的页面直接跳过；进入新一轮则重置 queue 全跑（这是多轮修复循环的自身要求——每轮要观察 fixer 改动是否引发其它页回归，不论轮次由谁触发）。visual-fixer 的修复历史在 `docs/autofix-log/round-N/`，本 skill 不读不写。

源端局部子任务的返回不代表整轮 visual skill 退出。round_budget 的 begin/next/end 和轮次生命周期由主会话统一执行；源树/准备/行走子任务只回传本段结果，不调用这些控制入口，也不自行标记阶段完成。
