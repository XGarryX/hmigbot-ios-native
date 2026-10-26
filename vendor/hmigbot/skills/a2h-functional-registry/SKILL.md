---
name: a2h-functional-registry
description: 从 Android 源码 + a2h-spec 产物，开放透明地生成 A2H Stage1 的两份契约产物——`functional_registry.json`（控件级功能点枚举 + 锚点）与 `test_intents.json`（含"预期结果"判据），落到契约路径 `<hmos_project>/spec/a2h/`，让 arkts-visual-verify / a2h-functional-merge **零改消费**。流程对齐 A2H（LLM 读完整源码做主提取 + 确定性脚本做兜底），完全不依赖 A2H 的封装二进制。⚠️ 触发场景：用户说"自产/重写 functional_registry"、"不用 A2H 工具生成功能点"、"脱钩 A2H 黑盒"、"生成 test_intents 给 visual-verify"、"产功能点契约"、"functional registry skill"时使用。即使只说"自己生成功能清单接 visual-verify"，只要上下文是替代 A2H Stage1，也应触发。本 skill 只产这两份 JSON，绝不跑设备测试、绝不改 fact-tree（注入 fact-tree 是 a2h-functional-merge 的事）。
metadata:
  title: 自产功能点契约（registry + test_intents，脱钩 A2H 黑盒）
---

> **Codex subagent dispatch convention.** This skill dispatches subagents. In Codex, spawn them with the `spawn_agent` tool and pass `agent_type` = the role name **exactly as written in this skill** — the roles registered under `.codex/agents/*.toml` use the same hyphenated names, so no translation step is involved: `a2h-activity-converter`, `a2h-android-analyzer`, `a2h-closer`, `a2h-fixer`, `a2h-migration-worker`, `ad-profile-builder`, `compose-fact-analyzer`, `hmos-builder`, `scenario-builder`, `visual-fixer`, `visual-fixer-reviewer`. The built-in `general-purpose` agent_type is unchanged. (Claude's `subagent_type` field is written `agent_type` for Codex; `Agent(...)` dispatch calls are `spawn_agent(...)`; there is no `Task` tool in Codex.)
>
> **Join 协议（收口五条款）。** Codex 子代理完成后**不会**唤醒主会话——结果必须由派发方主动收口，违者=静默卡死（实测事故）。
> ① **循环 wait**：每个 `spawn_agent` 句柄用循环调用 `wait_agent` 收口；单次超时只代表"还在跑"，继续再调；**禁止以"等待子代理"为由结束回合**。醒后必调 `list_agents` 确认是谁完成——**完成的唯一合法信号 = `agent_status` 为 `{"completed": …}`，绝不是产物文件的存在/条数**（文件会中途落盘，读半截=实测事故）；completed 态会在数轮后从 list 中消失，所以每次醒来都要及时查。正文所有"等待完成 / join / 到点即收"表述一律指此循环。
> ② **死句柄与验收**：连续 3 次超时后调 `list_agents` 核对，可配 `wait_for_artifact.py` 探产物活性；已 completed 且 summary 可读 → 直接消费；句柄消失且从未观测到 completed → 按断点重派（带原 prompt + 已落盘产物，上限 2 次），禁止继续等待。**completed ≠ 验收通过**：join 点跑 `python3 .agents/skills/a2h-join/scripts/join_gate.py --project .` 验产物完整性，FAIL 视同未取回、按本条重派。
> ③ **收口锚点**：本 skill 最终完成报告前必须收口全部句柄（join_gate exit 0）；正文写明的显式 join 点优先按正文执行。发用户门（Gate）时允许句柄跨 Gate 存活，但 Gate 摘要必须列明未收口句柄清单 + 各自的指定 join 点。
> ④ **放行 ≠ 遗弃**：正文"非阻塞放行/到点即收/降级继续"只推迟收口时机，不豁免收口义务。
> ⑤ **fire-and-forget**：仅正文显式声明"结果丢弃/不 gate"的派发（如 a2h-execute 的 env-prewarm）免收口；审计只认 join_gate 内静态 allowlist，正文声明只是文档层。
> **派发纪律**：`task_name` 必须唯一（带 page-id/slice-id/round-N 后缀）；并行派发前把预期产物清单写 `spec/a2h/_work/expected_<join点>.json`（join_gate 对账用，契约只认派发方、不认子代理自报）；**谁派谁收**——sub-agent 内部需要"等齐 N 片再合并"时禁止嵌套外派后自行退出，要么同步自做、要么把分片清单回报主会话代派（sub-agent 一停止，收口能力即丢）。**契约产物必须出自承担任务的子代理**：重派上限后仍产不出 → 如实报缺并停在未完成态；禁止派发方代写占位产物让 gate 转绿（声明过也不行——绿账必须对应真产物）。

## 编排定位

A2H 测试工具是第三方、脚本封装为黑盒、不可控。但我们确认过：**`functional_registry.json` 的内容 100% 是 LLM 读源码推理产物，A2H 的脚本只做机械预处理/合并/校验。** 本 skill 把这套能力搬成自己的——预处理脚本自己实现（脱钩封装二进制），提取方法论自己持有（[`references/extraction-methodology.md`](references/extraction-methodology.md)，源自并改进 A2H 开放方法论），产物逐字段对齐契约，下游零改消费。

### ⚠️ 流程铁律（对齐 A2H，纠正早期颠倒）
- **LLM 读完整源码（.java/.kt + xml）= 主提取器** —— 决定有哪些功能点。这是 A2H 的 `extract-deep-features`。
- **control_census（XML + 代码扫描）= 确定性地板 + 省 token 素材** —— **不是上限**。XML 控件给真 resource-id；代码交互(dialog/context_menu/bottom_sheet/code_click...)给候选种子，LLM 在其上展开 dialog 选项 / 长按各项 / 枚举值。
- 早期错误版本把 census 当主干、LLM 当贴标签的 → 系统性漏掉 ~26% 代码级交互。**本版禁止再这样**。

### ⚠️ a2h-spec 产物的角色：交叉校验器 + expected 增量（**不是脚手架、不替代源码**）
设计拍板：**源码 + census = 真值与完备性来源（主推导）**；**a2h-spec = 独立第二来源**，只做两件事，绝不替代源码定义功能点：
1. **expected 增量**：`features/F*.md` 验收标准 + `ui/page_*.md` 导航关系 → `expected` 升级源（比 A2H test_intents 静态种子更准）。
2. **双向交叉校验**（S5b）：源码主推导出 registry 后，用 spec 当独立第二来源对账，暴露分歧（spec 有/源码无 = 候选漏项；源码有/spec 无 = 候选 spec 漏项或过提取）。脚本**只产候选、不裁决**；**裁决者 = 运行本 skill 的 LLM**（回源码为真值），人默认不在回路、仅在 LLM 拿不准时升级。详见 S5b。
> 不当脚手架替代的原因：spec 本身也是 LLM 产的、有盲区（实证某项目 a2h-spec 漏 7 个 domain）。让源码当主、spec 当独立校验，两推导互相挑错；一旦用 spec 定 feature_path/枚举就继承它的盲区且再发现不了。
> `android_source_anchors` 只当 S3 读源码的**起点提示**，**不限定只读 anchors**——census 全覆盖照跑。

### 做什么 / 不做什么
| ✅ 做 | ❌ 不做 |
|------|--------|
| LLM 读全源码 + census 兜底，产 registry + test_intents | 跑安卓/鸿蒙设备测试 |
| 全 20 类 source_section + 真 resource-id + 预期判据 | 改 `spec/toolkit-fact-tree.json`（那是 a2h-functional-merge 的事） |
| 落契约路径 `<hmos_project>/spec/a2h/` | 依赖 A2H 任何封装二进制 |
| 自建透明的完备性 + join 校验 | 产 feature_tree / UI 清单（那是 a2h-spec） |

---

## 输出契约（⚠️ 路径固定）

`a2h-functional-merge` **只认契约路径** `<hmos_project>/spec/a2h/`：

| 产物 | 路径 |
|------|------|
| 功能点枚举 | `<hmos_project>/spec/a2h/functional_registry.json` |
| 测试意图 | `<hmos_project>/spec/a2h/test_intents.json` |
| 中间产物 | `<hmos_project>/spec/a2h/_work/`（census/oracle/index/points/report，留审计） |

**三条 join / 定位命门（脚本强保证）**：① `registry.name` == `intent.feature_path` 叶名（merge 主键）；② `intent.steps` 含 `预期结果：`（merge `split_expected` 切 expected_llm）；③ XML 控件 `raw_identifier` = 真 resource-id（grounding `uiautomator dump` 定位）。

---

## 脚本
目录 `.agents/skills/a2h-functional-registry/scripts/`（按安装位置改绝对路径）。变量：`$SRC`=安卓源码根，`$HM`=鸿蒙工程根，`$BASE`=`$HM/spec/baseline`，`$WORK`=`$HM/spec/a2h/_work`，`$PKG`=包名。

| 脚本 | 角色 | 替代 A2H 的 |
|------|------|------------|
| `source_index.py` | 源码结构索引（定向读取地图） | source_index_generator（二进制） |
| `strings_catalog.py` | strings.xml → 语义名查找表 | strings_resource_parser（二进制） |
| `arrays_catalog.py` | arrays → 枚举选项查找表 | arrays_resource_parser（二进制） |
| `control_census.py` | XML 控件 + 代码交互候选(C5 兜底/代码种子) | controls census 子命令 |
| `deterministic_floor.py` | **无遗漏叶子地板**(menu+pref+enum展开+Java枚举,召回79%) | (A2H 无独立此层,本 skill 强项) |
| `reconcile.py` | 地板 ⊕ LLM 双向对账(并集 90%) | A2H 的 verifier(单向)→ 升双向 |
| `project_registry.py` | points → functional_registry.json | merge_domain_fragments + 投影 |
| `build_intents.py` | points → test_intents.json | （A2H 的 Stage2，我们合并到一处） |
| `spec_oracle.py` | 从 spec/baseline 收割 expected 判据 + 供交叉校验 | （A2H 无此能力，本 skill 增量） |
| `validate_contract.py` | 契约 + 完备性 + join 自检 | validate_registry_format + verifier |
| `spec_crosscheck.py` | 源码产物 × spec 双向交叉校验（候选分歧） | （A2H 无此能力，本 skill 增量） |

---

## 执行流程

### 执行主体图例（每步开头都标，运行时严格照做）
- **⚙️ 脚本步**：跑指定 `python3` 命令即可，**零决策**。脚本不读语义、不改内容。
- **🤖 LLM 步**：由**运行本 skill 的 agent（你）**亲自读源码/判断/写文件。判断需要时**回源码当真值**，不靠记忆/不靠 spec 拍板。

### 全局不变量（贯穿所有步，违反即运行出错）
1. **唯一可被 LLM 手写/手改的文件 = `$WORK/functional_points.json`**（S3 产物）。
2. **`functional_registry.json` 与 `test_intents.json` 永远是 `functional_points.json` 的确定性投影**——只能由 S4 脚本生成，**禁止 LLM 直接手改这两份**。
3. **"改产物" 的唯一合法路径 = 改 `functional_points.json` → 重跑 S4（project_registry + build_intents）→ 重跑 S5 校验**。
4. **裁决者 = 运行本 skill 的 LLM**（同一个跑 S3 的 agent）；脚本只列候选，从不裁决。人默认不在回路，仅在 LLM 明确拿不准时升级给用户。
5. **冲突一律以源码为真值**：spec / census / 任何派生物与实际源码冲突时，回源码确认后以源码为准。

### 端到端总览（主体切换一目了然）
```
S0 🤖 确认输入($SRC/$HM/$PKG/$BASE)
S1 ⚙️ source_index + strings_catalog + arrays_catalog + control_census + ★deterministic_floor → 预处理 + 无遗漏地板
S2 ⚙️ spec_oracle                                                        → spec_oracle.json(expected 源, 可选)
S3 🤖 ★地板喂 LLM 深读(补语义 + 补代码层 + 枚举收口) ── 唯一手写文件 ──   → $WORK/functional_points.json
S3b ⚙️ reconcile(地板⊕LLM)→ 对账; 🤖 核 floor_only(LLM漏?)/llm_only(代码级) → 真漏补回 → 回 S4
S4 ⚙️ project_registry + build_intents (确定性投影)                       → spec/a2h/{functional_registry,test_intents}.json
S5a ⚙️ validate_contract → 报告; 🤖 若 C1/C3 硬失败或 C2/C4/C5 告警 → 改 points 回 S4
S5b ⚙️ spec_crosscheck → 候选; 🤖 逐条裁决(回源码) → 真漏补/真多删/spec漏记 → 改过则回 S4+S5a
S6 🤖 确认 ok=true + 候选已处理 → 交下游(android-fact-tree → functional-merge → visual-verify)
```
**回路只有一条**：任何修改都落在 `functional_points.json`，再经 S4 重投影；registry/intents 永不手改。

### S0. 〔🤖 LLM〕确认输入
- `$SRC`：安卓源码根（含 AndroidManifest.xml / build.gradle）。
- `$HM`：鸿蒙工程根，产物落 `$HM/spec/a2h/`。`mkdir -p $WORK`。
- `$PKG`：从 `source_index.py` 产的 `package`（manifest/gradle namespace）取，或用户给定。
- `$BASE`：`$HM/spec/baseline/features/` 存在 → 启用 expected 升级；否则 expected 走源码推断。

### S1. 〔⚙️ 脚本〕确定性预处理 + 无遗漏地板（自有脚本，脱钩 A2H 封装）
```bash
python3 .../scripts/source_index.py        "$SRC" "$WORK"
python3 .../scripts/strings_catalog.py     "$SRC" "$WORK"
python3 .../scripts/arrays_catalog.py      "$SRC" "$WORK"
python3 .../scripts/control_census.py      "$SRC" "$WORK"
python3 .../scripts/deterministic_floor.py "$SRC" "$WORK"   # ★ 无遗漏叶子地板
```
产 `source_index/strings_catalog/arrays_catalog/control_census.json` + **`det_floor.json`**。
- **`det_floor.json` = 确定性叶子地板**：menu + preference(后缀匹配自定义类) + ListPreference 枚举展开 + **Java 枚举类**(UI 向) → 真 resource-id / enum 常量，**实测召回 A2H 79%、无随机漏**。带 feature_path 空(待 S3 填)。
- census 含 XML 控件 + 代码交互候选(dialog/context_menu/code_click...)，供 S3 啃代码层。

> **结合方案的依据(实测)**：纯确定性地板召回 79% + LLM 深读召回 75% → **并集 90%**。互补：地板救 LLM 的随机漏(资源项)，LLM 救地板的代码盲区(dialog/custom/手势)。所以 S3 = 地板喂 LLM 深读，S3b 双向对账。

### S2. 〔⚙️ 脚本〕预期判据收割（expected 升级源，可选，非致命）
```bash
python3 .../scripts/spec_oracle.py "$BASE" "$WORK"
```
产 `spec_oracle.json`（features 验收标准 + page 导航关系）。`available=false` 时 expected 全走源码推断。

### S3. 〔🤖 LLM〕★核心：**地板喂 LLM 深读**产 functional_points.json
**关键:LLM 不是从零读源码,而是被 `det_floor.json` 喂着——采用地板已枚举的资源项(直接用其 id/section,不重数),只做三件 LLM 才能做的事。严格按 [`references/extraction-methodology.md`](references/extraction-methodology.md)。产物只写 `$WORK/functional_points.json`(全局不变量①)。**

> ⚠️ **不要"独立跑 LLM 再和地板 merge"**——两者 source_file/id 约定不一致会导致同一条被拆开。正确做法是 LLM **扩写地板**:地板的条目原样保留(id/section/source_file 不动),LLM 在其上补语义,并**额外新增**地板够不到的代码层。这样 id 约定统一,S3b 对账才干净。

LLM 在地板基础上做三件事:
1. **给地板每条补语义**:feature_path(以域名开头,反映导航层级,溢出经"更多")+ 中文 name + action + expected + group + precondition + domain。地板的 `raw_identifier`/`source_section`/`source_file` **原样不动**。
2. **补代码层**(地板够不到的,读 census 的 code_* 候选 + 源码):dialog 按钮/选项、custom_view 手势、setOnClickListener、BottomSheet 内操作 等 —— 实测这是 LLM 独有贡献(占召回的 +11%)。
   **★WebView 桥接点必入册（2026-07-11，治"H5 壳桥接盲区"）**：grep 全源码
   `@JavascriptInterface` / `onShowFileChooser` / `setDownloadListener` / `shouldOverrideUrlLoading`
   （自定义 scheme 拦截），**每个桥方法一条功能点**——anchor=桥方法（source_file+方法名），
   name=桥的业务语义（如"H5 一键退款桥"），expected=**原生侧反应**（弹原生确认弹窗/系统相册/拨号盘/
   下载器——这是可机械观察的判据），挂到注册该桥的 WebView 容器页。
   实证教训：AIPPT 的 WebAppInterface 6 个 @JavascriptInterface（callRefund/unsubscribe/callPhone/
   contactService/showToast/onCloseEvent）全部漏册——这些是如假包换的迁移物（鸿蒙 Web 组件要重实现
   同名桥），坏了的表现="H5 首屏正常、一点就死"，入口 landing 验证完全失明。桥接 check 的验证深度
   与防偏差规则见 arkts-visual-verify 的 phase0.5-grounding.md 2c / sub-agent-batch-prompt B.4.5。
3. **枚举 per-dialog 收口**:地板把 Java 枚举全量列了(如 SortOrder 17 档),但某弹窗只暴露子集(队列排序 6 档)——LLM 读对话框代码,把地板里**该弹窗不暴露的枚举档删掉**(这是地板做不到的精度收口)。

- **按 L1 域 / 页面分批**(地板的 source_file 天然聚类)。控件多时派 `general-purpose` sub-agent 分域并行,每 agent 拿到**它那域的地板切片** + 源码,回收合并为 `$WORK/functional_points.json`。
  > ⚠️ **收口铁律(谁派谁收,别嵌套下放)**:「等齐 N 个分域 agent → 合并成 functional_points.json」这一步是**收口协调**,**必须由派发这些 agent 的那一层持有**——sub-agent 一 stop 收口能力即丢。
  > - **本 skill 被当 sub-agent 调起时(如 android-fact-tree fork 腿B)**:**禁止**自己再派后台分域 agent 然后 return —— 那样收口落在你(sub-agent)手里,你一停就丢(实测事故:7 个 census 分片抽取 agent 派完即停,functional_points 从未合并)。此时二选一:**(a)** 分域抽取**自己同步做**(不外派,读每个分片就地抽,慢但收口稳);**(b)** 若上层是主会话,把「分域清单 + 地板切片」**回报给主会话**,由**主会话**派分域 agent 并收口(推荐——并行不丢、收口在不会停的主会话)。
  > - **本 skill 由主会话直接调起时**:可放心派分域 agent 并行,主会话**等齐所有完成通知**(只认 task=completed,不看文件条数——分片会中途落盘)再合并。判据同 §android-fact-tree §2A.2:**"需等齐再合并"的收口留主线,"产独立分片文件"的抽取可下放**;抽取 agent 只写自己的分片 JSON、绝不合并。
- 输入:`det_floor.json`(地板,主)+ `control_census.json`(代码候选)+ `strings_catalog`/`arrays_catalog`/`source_index` + `spec_oracle`(expected)+ 源码。

### S3b. 〔⚙️ 脚本产对账 → 🤖 LLM 核〕地板 ⊕ LLM 双向交叉校验
```bash
python3 .../scripts/reconcile.py "$WORK/det_floor.json" "$WORK/functional_points.json" "$WORK/reconciled_points.json" "$WORK/reconcile_report.json"
```
对账报告三类(实测互补):
- **both**:地板与 LLM 都有 → 已合并(干净 id + LLM 语义)。
- **floor_only**:地板有、LLM 没采纳 → **候选「LLM 漏了资源项」**(地板救 LLM 随机漏)。🤖 LLM 逐条核:真功能→补进 points;地板过量产(如该弹窗不暴露的枚举)→ 确认丢弃。
- **llm_only**:LLM 有、地板没有 → 代码级真功能(LLM 救地板盲区)→ 保留。
> 若 floor_only 有真漏 → 补进 `functional_points.json` → 回 S4 重投影。这就是"地板 verifier" + "LLM 补码"双向兜底。

每条 point（schema 见 `references/extraction-methodology.md`）：
```jsonc
{"name","depth","feature_path","source_file","source_section","raw_identifier",
 "action","expected","expected_source":"spec_acceptance|spec_nav|inferred",
 "group":"independent|setup|dependent|blocked","precondition","domain"}
```
**expected 优先级**：`spec_acceptance`（命中 features 验收标准）> `spec_nav`（命中 page 导航关系 target）> `inferred`（读源码 handler 推断）。
**★inferred 时 handler 下钻（2026-07-16，AIPPT 实证猜错）**：读源码推断 expected 时，若 handler
（onClick 分支）调的是一个**中转函数/扩展函数/ViewModel 方法**而非直接落点 → **不要按函数名字面猜**，
必须进那个函数体看它真正干什么，有分支就每支都记。真实事故：`mineSettingCustomerService` 的 handler
是 `showService(false)`，registry 按函数名猜成"弹窗/拨号"，但 `showService`（SaleCenterViewModel.kt）
主分支实为 `CustomerServiceWebActivity.openWebPage`（跳 H5 客服网页），只有 `contactUsUrl` 空时才拨号/
弹窗 → expected 写错，下游把"该跳 H5"的功能点当"弹窗"验。**与 app-relationship-tree Phase 2.5 的
"间接跳转下钻"是同一盲区的两面**（ART 漏边、registry 猜错 expected），两处都须下钻。落点是 WebView
页时 expected 记「打开 H5 网页（url=…）」并标可交 §2c oracle，别记成弹窗/原生。
**raw_identifier**：XML 控件抄 census 真 id；代码交互用 census 代码锚点。
**覆盖铁律**：census 每个控件都要有对应 point（除非纯装饰/重复）；code_* 候选不得整类跳过。

### S4. 〔⚙️ 脚本〕投影为两份契约产物（确定性，同源 → join 天然对齐）
```bash
python3 .../scripts/project_registry.py "$WORK/functional_points.json" "$HM/spec/a2h"
python3 .../scripts/build_intents.py   "$WORK/functional_points.json" "$HM/spec/a2h" "$PKG"
```

### S5a. 〔⚙️ 脚本 → 🤖 LLM 修〕契约 + 完备性自检（脱钩 A2H 后的透明兜底）
```bash
python3 .../scripts/validate_contract.py "$HM/spec/a2h" "$WORK/control_census.json"
```
C1 registry schema / C2 raw_identifier 填充率 / C3 intents schema + 预期结果标记 / C4 join 对齐率 / C5 census 覆盖率（含代码交互）。报告 `contract_report.json`。
- **C1/C3 硬失败** → 修 points 回 S4。
- **C2<80%** → 回 S3 补真 id。 **C4<95%** → 查 S3 命名一致性。
- **C5<85%**（漏控件）→ 读 `uncovered_controls.json`，回 S3 补；尤其检查 code_* 候选是不是整类漏了。最多 2 轮。

### S5b. 〔⚙️ 脚本产候选 → 🤖 LLM 裁决并修〕spec 双向交叉校验（独立第二来源对账）
> ⚠️ 前提：**仅在 S3 已产出完整 registry 后跑**（部分切片会因"切片 registry vs 全量 spec"产生大量假未匹配，无意义）。`$BASE`/spec/baseline 不存在则脚本自动跳过（非致命）。

**第 1 步〔⚙️ 脚本〕生成候选**（脚本只对账、不裁决）：
```bash
python3 .../scripts/spec_crosscheck.py "$HM/spec/a2h" "$WORK"
```
产 `spec_crosscheck_report.json`，三类**候选分歧**：
- **A nav_trigger_unmatched**：spec 导航关系记了某交互、registry 无 → 候选「源码提取漏了」。
- **B criteria_unmatched**：spec 验收标准断言了某行为、registry 无明显对应 → 候选「漏功能 / 或 AC 是非控件级行为」。
- **C registry_unreferenced**：registry 有、spec 全文没提 → 候选「spec 漏了(我对) / 或我过提取」。

**第 2 步〔🤖 LLM 裁决〕**（裁决者 = 运行本 skill 的 LLM，全局不变量④）：脚本是确定性候选生成器、**不是终判**（字面匹配会因"spec 行为级散文 vs registry 控件级短名"误报）。**逐条**打开候选，读 `report` 指向的 spec 原文 **+ 回 `source_file` 实际源码**，判定四选一：
| 裁决 | 含义 | 动作 |
|------|------|------|
| **真漏**（A/B：源码确有此控件/交互，registry 没收） | 源码为真，我漏了 | **改 functional_points.json：补这条 point** |
| **真多**（C：源码里根本没有此控件） | 我过提取 | **改 functional_points.json：删这条 point** |
| **spec 漏**（C：源码确有，spec 没写） | 我对，spec 缺 | **保留 point**，把该项记入 `$WORK/spec_gaps.md` 供反馈 a2h-spec |
| **仅措辞不同**（A/B/C：同一功能两边叫法不同） | 无分歧 | **不动** |

**第 3 步〔⚙️ 脚本〕**：若第 2 步改过 functional_points.json → **重跑 S4（project_registry + build_intents）+ S5a（validate_contract）**，使两份契约与裁决后的 points 重新对齐。
- **铁律**：裁决冲突一律**以源码为真值**（全局不变量⑤）；spec 分歧只作线索，不作判决。**禁止**为了"对齐 spec"而手改 registry/intents（全局不变量②）。

### S6. 〔🤖 LLM〕完成
两份契约落 `$HM/spec/a2h/`，`contract_report.json` 的 `ok=true`（且 S5b 候选已逐条裁决处理）。
**下游**：跑 `android-fact-tree`（出口契约 §3.5 检测到 `spec/a2h/functional_registry.json` → 自动接 `a2h-functional-merge` 注入 `functional_checks[]`），再跑 `arkts-visual-verify`。本 skill **不自己调 merge / 不改 fact-tree**。

---

## 相对 A2H 的改进（见 `references/extraction-methodology.md` §7）
1. 每个功能点都配 expected（A2H 仅 75% registry 能 join 到 intent）。
2. expected 升级源：features 验收标准 + page 导航关系 > test_intents 静态种子。
3. raw_identifier 更稳：XML 控件给真 resource-id（A2H 常给代码路径），grounding 定位更准。
4. 完备性兜底自实现（census + 地板召回），脱钩 A2H 黑盒工具。
5. census 给"应覆盖控件数"，C5 量化覆盖率 + 列 uncovered，漏没漏一目了然。
6. **spec 双向交叉校验**（S5b）：源码与 a2h-spec 两个独立推导互相挑错，暴露双向漏项——A2H 单源生成、无此自我校验回路。

## ⚠️ 架构适用范围：本 skill 的 S0-S6 主流程是 **XML/View 架构专用**
S1 的 `control_census`/`deterministic_floor` 扫 layout/menu/preference XML 拿 **resource-id**——纯 Compose 无这些（无 XML 布局、无 resource-id、testTag 实测 0 用），主流程会塌成近空。

**纯 Compose 走旁路脚本**（`scripts/compose_registry_from_tree.py`，由 android-fact-tree §3.5 按架构调）：
- compose-fact-tree 已把交互组件抽进 `fact-tree.pages[].components`（含 text/navigation/behaviors[file:line]），**宿主页天然已知（join 已完成）**。
- 脚本直接投影成 registry，**锚点 = 文案(text)**，并产 `compose_host_map.json` 供 `compose_merge_into_facttree.py` 精确映射。
- 纯确定性、无 LLM（组件已是 compose-fact-tree 的提取产物）。下游产物 schema 与 XML 路径一致，visual-verify 零改消费（check 带 `tap_by=text`）。
- 实测 habicat（154 @Composable）：76 交互组件 → 76 entries → merge 100% 映射 → 树挂 76 functional_checks。

## 与既有 skill 的边界
- **a2h-spec**：产 `spec/baseline/`；本 skill **消费**其 features/ui 当 expected 升级源，不替代。
- **a2h-functional-merge**：消费本 skill 两份产物注入 fact-tree；本 skill 是其上游生产者（替代 A2H Stage1）。
- **android-fact-tree**：产结构树，与本 skill 并行，在 merge 处汇合。

## 兜底
1. `$BASE` 不存在 → spec_oracle 空壳，expected 全 `inferred`。
2. layout/strings XML 解析失败 → census/strings_catalog 自动 regex 兜底。
3. 某交互找不到源码 handler → expected 标 `inferred` 备注，不跳过控件。
