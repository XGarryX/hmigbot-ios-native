---
name: arkts-architecture-refactor
description: 把现有的 HarmonyOS / ArkTS 应用按照《鸿蒙客户端原生开发规范》(develop_rule.docx) 进行结构化重构。规则覆盖六大类——工程拆分(壳/features/components 三段式)、私仓接入(lib_common/lib_network/lib_widget/lib_payment/lib_starburst/lib_umeng/lib_hmiap + .ohpmrc)、代码分层(components/constants/pages/viewmodel/bean/util)、静态资源(webp 3x/svg/colorFilter)、公共样式(color.json 命名规范、UI weight、AppStorageV2 pagePadding)、其他规范(状态管理 v2、Repeat 替代 LazyForEach、BaseViewModel、Navigation+RouterUtils 路由、RequestUtil/ExternalReqUtil + AbortController 网络、PreferenceUtil/@ohos/dataorm 持久化、WindowModel 安全距、GridRow/GridCol 断点、build-profile buildProfileFields)。务必在以下场景触发：(1) 用户提到"把这个鸿蒙项目按规范重构 / 整改 / 迁移到新架构"、"接入私仓 lib_xxx"、"按 develop_rule 改造工程结构"、"拆 business 子模块"、"v1 状态升级到 v2"、"接入 RouterUtils/RequestUtil"、"统一 color.json"、"加 AbortController"、"BaseViewModel"； (2) 用户给出一个鸿蒙 HAP/HSP 工程并请求架构合规性检查或差距报告； (3) 即使用户只说"按规范重构"、"重构这个 HarmonyOS app"、"对齐 AI 工程的架构"，只要上下文明显是 HarmonyOS/ArkTS 项目改造，也应触发。
---
# arkts-architecture-refactor

把已有 HarmonyOS 应用按公司《鸿蒙客户端原生开发规范》整改成 “壳工程 + business features + components” 三段式架构，并接入私仓底层库。

## 最终目标（北极星）

> 本 skill 的所有 phase / step / 决策 / 取舍 **都是为这一条服务**，任何冲突时这条优先级最高：

**重构后的项目必须 ① 完全符合 skill 列出的架构规范，且 ② 用户可感知的功能与重构前完全一致。**

两个子目标都是硬约束、缺一不可：

| 子目标 | 量化标准 | 验证方式 |
|---|---|---|
| ① 架构合规 | 所有 MUST 规则 PASSED；SHOULD 规则达成或显式列入 deferred 并给出推进路径 | Phase 4 ② 重跑 audit 对比改造前后 + ③ 静态合规扫产物 |
| ② 功能一致 | 编译通过 + 运行时冒烟（L1~L4）通过 + 关键路径行为与 master 一致 | Phase 4 ① 编译闭环 + ⑤ 运行时冒烟 + 必要时切回 master 跑对照 |

**什么算"功能一致"**：
- 用户在重构前能完成的所有交互（启动、登录、跳转、列表渲染、写入、读取……）在重构后**视觉与行为均无差异**
- 重构期间触发的网络/数据库/路由调用，在 master 上同样会触发，且响应处理路径一致
- BEHAVIOR_RISK 仅允许标注**实现等价但写法不同**的改动（如 EntryAbility 硬编码 → BuildProfile 读取，同值同流程）；**禁止**标注真实运行时差异

**判定优先级**（冲突时）：
1. 功能一致 > 架构合规 — 如果某条架构改造会破坏功能，**先保功能**，把架构项降级为 deferred 并写明阻塞原因（例：`lib_network@1.0.9` 不支持 signal → R6.3c 不可达）
2. 架构合规 > 代码风格 — codemod 误改导致编译过但运行时坏（如 router → RouterUtils 误转入口页路由），**必须修**而不是说"建议用户验证"
3. 验证通过 > 报告漂亮 — Phase 4 ⑤ 冒烟未跑成功**绝不允许**写"PASSED"。冒烟失败就回 Phase 3 修，修到通过为止

**收工的硬条件**（任一不达标都不能写 PASSED 收工报告）：
- ✅ `hvigorw assembleHap` 最终一次 BUILD SUCCESSFUL
- ✅ Phase 4 ② audit 重扫所有 MUST 规则 PASSED
- ✅ Phase 4 ⑤ 至少 L1（首屏）+ L2（一跳）冒烟通过；v1↔v2 / Navigation 改动须到 L3；状态环改动须到 L4
- ✅ 所有 BEHAVIOR_RISK 都在报告中显式列出且有"同值同流程"的论证

### 客户优先级声明（最高优先级）

> 本节是**客户的明确诉求**，凌驾于本 skill 任何效率/工程量/HARD-GATE 妥协之上：

**"只要 skill 有要求的就要严格遵从，我只要求重构后的代码架构符合要求，功能和之前完全一致，不在乎 token 和时间消耗。"**

由此推出的硬约束：

1. **不允许"工程量大"作为 MUST 规则的 deferred 理由**。"51 处要改"、"太花时间"、"会议结束前来不及"——这些**全部不构成豁免**。MUST 就是 MUST，每一处都必须改到位。Deferred 仅在**技术上不可达**时允许（如私仓库版本不支持 signal、私仓库代码归属外、规范条款本身与功能一致冲突——三种之一并写明）。
2. **不允许"询问用户要不要 A/B/C 方案"作为 MUST 规则的处置选项**。如果是 MUST 违规，**直接全量整改**，不需要让用户选"全量 / 部分 / 推迟"。HARD-GATE 仅用于 audit 范围确认 + plan 拆分粒度 + 私仓版本，**不用于砍 MUST 规则的工程量**。
3. **不允许以"上下文消耗 / 会话规模"为由提前收工**。超规模工作按"原则 3"分段进行，但每段都要把覆盖范围内的 MUST 规则改完，**不允许把 MUST 留到"下一段"**——上一段没改完不能进入下一段，必要时分多个会话续做（execution-log + commit SHA 是续做基础）。
4. **功能一致是底线，架构合规是天花板，两者必须同时达成**。当真出现冲突（极少数情况），按上方"判定优先级 1"先保功能 + 写明阻塞原因；但**不允许**把"我担心可能影响功能"作为不改的借口——担心就跑冒烟验证，验证通过就改。
5. **唯一可接受的"留给下一轮"**是：技术不可达 + 已写明阻塞原因 + 已上报阻塞依赖方（私仓 / 规范方 / 客户）。其他一切"留给下一轮"都是违反本声明。

## 何时使用本 skill

只要用户的目标是 **让一个现有的 HarmonyOS 工程符合 develop_rule.docx 的架构要求**，就用这个 skill。典型触发词：

- “按规范/按 develop_rule 重构这个项目”
- “拆 business 子模块 / 拆成 features”
- “接入公司私仓 lib_common / lib_network”
- “v1 状态管理升级到 v2”
- “接入 RouterUtils / RequestUtil / PreferenceUtil”
- “整改 color.json / 统一颜色规范”
- “给页面加 AbortController”
- “盘点这个鸿蒙工程跟规范的差距”

如果用户只是问“怎么写 ArkTS 组件”这种细节问题、或者从 Android 项目迁移过来（那是 a2h 系列的事），**不要**触发本 skill。本 skill 关心的是 **已经在 HarmonyOS 上、需要架构合规整改** 的场景。

## 执行原则（Agent 自律规则）

> 本 skill 的工作流（audit → plan → execute → verify）周期长、步骤多，agent 容易在三种地方掉链子：① 该自己决策的反复问用户；② 该自己验证的甩给"建议你跑一下"；③ 一轮硬塞超出会话规模。下面三条强约束**优先级高于任何文风偏好**。

### 原则 1：自主决策，不要遇事就问

skill 已经为大多数选择给出明确指引（HARD-GATE 阐明的范围、`references/*.md` 的规则严格度表、ai-baseline.md 的实证边界、客户校准记录）。在 HARD-GATE 已批准的范围内，**所有可由 skill 文档推断的子决策都自己做**：

- 私仓版本要不要升 → 看 plan 是否声明"沿用现有版本"
- entry → products/phone 用方案 A 还是 B → 读 `references/01-project-structure.md`
- module_* 真实抽取要不要做 → 跑 grep 触发器，达标就抽不达标就留骨架
- buildProfileFields 字段值 → 从代码扫候选值（EntryAbility 硬编码、AppScope/app.json5、preferences keys），找不到的标 BEHAVIOR_RISK 而不是停下来问

**只在 skill 文档里没说 + 影响范围跨多个步骤 + 决策错了得回滚**这三个条件**全部**满足时才回头问用户。日常操作如"这处 padding 真违规吗"、"要不要顺手清死代码"、"v2 装饰器细节"——**自己判，记到 execution-log 里就行**，不要打断用户。

> 反模式：写完 audit 列了 5 个问题问用户"你要做哪些 / 哪个先做 / 要不要豁免 X / 要不要新增 Y / lib_hmiap 要不要 / ..."。Phase 1 HARD-GATE 只该问 **改造范围 + 优先级**，不应该把 plan 阶段所有细节都打包问一遍。

### 原则 2：自主验证，不要甩给人工

Phase 4 ⑤ 运行时冒烟**默认要做**，不是"建议下次设备就绪时跑"。开始 Phase 4 前**主动检查**：

```bash
which hdc 2>/dev/null \
  || ls /Applications/DevEco-Studio.app/Contents/sdk/default/openharmony/toolchains/hdc 2>/dev/null \
  || ls ~/Library/OpenHarmony/Sdk/*/toolchains/hdc 2>/dev/null
which hvigorw 2>/dev/null \
  || ls /Applications/DevEco-Studio.app/Contents/tools/hvigor/bin/hvigorw 2>/dev/null
which ohpm 2>/dev/null \
  || ls /Applications/DevEco-Studio.app/Contents/tools/ohpm/bin/ohpm 2>/dev/null
$HDC list targets   # 模拟器/真机就绪？
```

DevEco Studio 在 macOS 默认装在 `/Applications/DevEco-Studio.app/Contents/{tools,sdk}` 下，工具齐全。**只要 DevEco 装着，hvigorw + ohpm + hdc 三件套都可用**，不要因为 PATH 没暴露就直接判"无法验证"。需要时设置：

```bash
export PATH="/Applications/DevEco-Studio.app/Contents/tools/ohpm/bin:/Applications/DevEco-Studio.app/Contents/tools/hvigor/bin:$PATH"
export DEVECO_SDK_HOME="/Applications/DevEco-Studio.app/Contents/sdk"
HDC=/Applications/DevEco-Studio.app/Contents/sdk/default/openharmony/toolchains/hdc
```

**只有在 `$HDC list targets` 返回空 + 用户拒绝连设备时**才把冒烟标记为"未执行 + 等下次"。其他情况一律自己跑：编译 → 安装 → 启动 → 截图 → uitest 点击 → 抓 hilog → 截图对比。**冒烟期间发现问题（如 codemod 误改 entry 路由）必须回 Phase 3 修，不要写"建议用户在 DevEco 验证"敷衍**。

类似地，**怀疑某个改动是否引入回归** → 临时 `git stash + git checkout master`，把 master 跑一次对比，比让用户去比对快得多。

### 原则 3：超规模工作分段进行，但段间可断点续做

整轮 refactor 估算 15-25 小时实际工时，单会话铺完会上下文爆炸 + 错误叠加难回滚。**每个 Step 完成立即 commit + execution-log 记录 SHA**——这是分段的物理基础。每段产出物：

| 维度 | 做什么 |
|---|---|
| commit | 一个 Step 一个 commit，message 写明 SHA / 改了什么 / 编译结果 |
| execution-log | 当前 Step 的决策、改动范围、BEHAVIOR_RISK、commit SHA |
| 编译验证 | 本 Step 完成后立刻跑 `hvigorw assembleHap`，过了才进下一步 |

**会话边界判断**：当一个 Step 涉及超过 ~5 个 business 模块、或者超过 ~50 文件改动、或者上下文消耗已达对话总量 60% 时，**主动停下来**给用户进度汇报 + 下一段计划，让用户决定是当场继续还是开新会话续做。开新会话时只要交接：① 当前 commit SHA、② Phase 几 Step 几、③ 下一段 todo。skill 状态全在 `spec/refactor-{audit,plan,execution-log}.md` 里，新会话从这三个文件 + git log 直接续。

**不允许**的反模式：
- ❌ 一次会话硬怼 v1→v2 全量迁移 72 文件，编译爆 200 错救火（应该按 business 拆 8 段）
- ❌ 因为"会话快满了"就草草标 deferred 收工而不 commit 进度（应该把当前 Step 完整 commit + 把剩余写进 plan，交接清楚）
- ❌ "建议你下次设备就绪时跑冒烟"作为 Phase 4 ⑤ 的最终结论（应该自己装 hdc 跑、或者明确告知"需要你启动模拟器，启动后告诉我我接着跑"）

## R0 ArkTS 语法基线（鸿蒙官方文档）

依据 develop_rule.docx 第一章："参考鸿蒙官方开发文档"——ArkTS 编码规范遵循鸿蒙官方：

> <https://developer.huawei.com/consumer/cn/doc/harmonyos-guides-V5/arkts-coding-style-guide-V5>

audit 不强制逐条扫语法（依赖 IDE 提示），但 plan/execute 阶段对命名 / 缩进 / 类型 / null safety 等基础规范均按官方文档走。客户 customer-checklist.md 中已显式记录此基线作为 R0.1（MUST）。

## Ground Truth：权威基线 + 双参考工程

### 权威基线（单点真理）

**[`~/Desktop/HUAWEI/wfhc/features/develop_rule.docx`](~/Desktop/HUAWEI/wfhc/features/develop_rule.docx)**（"鸿蒙客户端原生开发规范"）**是所有规则的最终权威**——规则方向、严格度判定、客户校准都以 docx 为准。

**优先级**：`docx 文字 + 客户校准记录` > `AI/Scan 双 baseline 实证` > `agent 自由判断`。

> **2026-04 反思**：上一轮三个客户反馈（VM 错位、资源囤壳、HttpClient 造轮子）都是因为 audit 过度依赖「AI/Scan baseline 没标违规 → MAY 豁免」，忽视了 docx 本身的规则原意（私仓优先、就近放置、壳工程瘦身）。**当 docx 与 AI/Scan 实证冲突时，以 docx 为准**——AI/Scan 工程本身可能存在规范遗留问题，不能反推为「规则容忍」。

### 双参考工程（实证边界）

**两个工程提供规则容忍度的实证边界**：

- `~/Desktop/HUAWEI/wfhc/features/AI`
- `~/Desktop/HUAWEI/wfhc/features/Scan`

两工程的**并集**定义 audit 实证容忍度——但**仅适用于 docx 未严格收紧的条目**。docx 已用「必须 / 务必」明确为 MUST 的条目，AI/Scan 即使存在反例也不构成豁免（视为遗留待整改）。

**第一原则**：跑 audit 之前先读 `references/ai-baseline.md`（含 Scan 对照）+ `references/customer-checklist.md`（最新客户校准），先看 docx 怎么说，再看 AI/Scan 怎么做，**冲突时以 docx + 客户校准为准**。

### 规则严格度

| 严格度 | 含义 | 触发条件 |
|---|---|---|
| **MUST** | 违反就阻塞或会引发 bug，必改 | AI 工程**没有**这种写法，且规范用"必须 / 务必 / 统一" |
| **SHOULD** | 建议改，列 warning，由用户决定 | AI 工程**部分场景**有这种写法，规范用"应 / 应尽量 / 避免" |
| **MAY** | 仅信息，不计入差距 | AI 工程**多场景**有这种写法，规范用"可 / 以下是实例" |

### 关键校准点（从 AI + Scan 双工程反推）

下面这些写法在规范字面上看似违规、但在参考工程里都存在——**不要标违规**：

| 写法 | 实证 | 正确判定 |
|---|---|---|
| `viewmodels`（复数）/`services`/`dialog`/`vm`/`api`/`db` 等目录命名 | 两工程的 business 都有非"viewmodel/util/bean"命名 | **MAY** — 看职责拆分，不看拼写 |
| `app_theme` / `text_color` / `btn_*_Color` 等非规范色名 | 两工程 products/phone 都用此类命名 | **MAY** — 规范的 19 个是跨平台同名建议 |
| business_common color.json 缺通用 token | AI/Scan 都仅 2 个 token | **MAY** |
| `extends BaseBean / HSData` 的 DTO class | 两工程所有 DTO 都用此模式 | **MAY** |
| 网络调用 AbortController.signal | AI 全未用；Scan 部分用 | **拆三条规则、严格度方向相反**：**R6.3c 全局请求 = MUST NOT abort**（命中"误挂页面 abort"必报）/ **R6.3d 非全局请求 = MUST abort**（命中"未传 signal/未 abort"必报，无豁免）/ **R6.3e 第三方请求 = SHOULD abort**（默认报，业务理由可豁免）。详见 [05-network-persistence.md § R6.3c-R6.3e](./references/05-network-persistence.md) |
| 简单 / 辅助 / 计数型 VM 未继承 BaseViewModel | AI: QqShare/WxShare；Scan: + Preview/UseCount | **MAY** — 仅 `*PageVM/*PageViewModel` 主页面状态容器要求继承 |
| widget/dialog/builder/特殊渲染/**引导组件** v1 装饰器 | AI 全在前 4 类；Scan 多了 GuideCheckMark 引导组件 | ⚠️ **客户校准为 MUST**：全局统一 v2，**无场景豁免**。AI/Scan baseline 中残留的 v1 已被客户判定为遗留待整改 |
| 单点 axios 调用（ReadCoverCreate 级别——极窄单次调用，非整体封装） | 两工程都有 | **MAY**（注意：自建完整 HttpClient 封装类**不是**单点调用，是 MUST 违规，见 RR6） |
| `import { AbortController/GenericAbortSignal } from '@ohos/axios'` 类型导入 | Scan 4 处 | **MAY** — 类型来源容许 |
| DAO 层用 `@ohos.data.relationalStore` | AI 的 WorksDao | **MAY** |
| `build-profile.json5` 缺 `buildProfileFields` | AI/Scan 都未配置 | **MAY** — 有三方 key 才配 |
| 根 `oh-package.json5` 缺 `overrides` | AI 有；Scan **没有** | **MAY** — best practice 但非必填 |
| png/gif 资源残留 | AI 110+1；Scan 172+2 | **MAY** — 不主动报告 |
| LazyForEach 残留 | AI 3 处；Scan 2 处 | **SHOULD warning** — 仍可建议 |
| WebSocket 调用 | AI 有使用 | **MAY** — 不在网络规则范围 |
| 链中间 ViewModel `extends ParentVM` | AI business_video 多处 | **MAY** — 链顶层继承即可 |
| `lib_*` 具体版本号 | AI 用一组版本，Scan 用更新的另一组 | **按工程当时稳定版本**，模板不硬编码 |

### 真正会被 audit 标违规的（MUST 红线，含客户最新校准）

> ⚠️ **客户校准（2026-04）**：以下规则严格度最近被客户上调为 MUST，audit 必须按 MUST 处理（详见 [customer-checklist.md](./references/customer-checklist.md) 与 [rule-checklist.md § 客户校准记录](./references/rule-checklist.md)）。

**结构与依赖类**：

1. 工程**完全没有**三段式骨架（仍是 entry 单模块）
2. `.ohpmrc` 缺 dadoubk registry（**私仓**）
3. 没有引入 `lib_common`（**私仓**，缺 RouterUtils（私仓）/ PreferenceUtil（私仓）/ BaseViewModel（私仓）等核心能力）
4. **私仓优先原则违规**（R2.0）：自造 RouterUtils / PreferenceUtil / HTTP 封装等"重复轮子"，绕过私仓
5. 用了 HTTP 网络但没引 `lib_network`（**私仓**）且也没用 RequestUtil（私仓）/ ExternalReqUtil（私仓）

**代码与运行时类**：

6. **业务主体**用 v1 状态管理（不是少数特殊场景，是页面/VM 全是 v1）
7. 大量旧 `router.pushUrl/replaceUrl` 残留（说明根本没接 RouterUtils（私仓））
8. List/Scroll 子节点用 RelativeContainer（会**导致无法滑动**）
9. **R6.1b（客户升级）**：列表用 LazyForEach 而不用 Repeat → P1
10. **R6.3c/d/e（客户校准三条规则、严格度方向相反）**：
    - **R6.3c 全局请求 = MUST NOT abort**（App 级初始化 / 跨页轮询 / 用户态预加载 / IonBusiness.loadPrices / UseCountManager.preloadAllCounts）— **禁止**在页面退出时 abort，否则会误杀核心数据流。命中"误挂页面 abort" → P1
    - **R6.3d 非全局请求 = MUST abort**（页面专属业务接口、详情、列表、上传/下载）— **必须**传 signal + 在 `aboutToDisappear`/`onPageHide` abort。命中"未传 signal 或未 abort" → P1（强约束，无豁免）
    - **R6.3e 第三方请求 = SHOULD abort**（ExternalReqUtil / 外部 SDK）— 默认报，execution-log 给出明确业务理由可豁免
    - 详见 [05-network-persistence.md](./references/05-network-persistence.md)

**资源与样式类**：

11. **R4.1/R4.3（客户升级）**：新增 png/jpg/gif 资源 → P1；存量 png 列入 P1 资源迁移
12. **R4.4（客户新增）**：多色版同名图标（如 `icon_play_blue.webp` + `icon_play_red.webp`）→ P1，必须改单色 webp + ColorUtils.hexToColorMatrix（私仓 lib_common）

**布局与配置类**：

13. **R6.5a（客户升级）**：未使用 WindowModel（私仓）的顶/底安全距，写死 `padding({top: 36})` → P1
14. **R6.5b-1（客户升级）**：List 的 `lanes` / Grid 的 `columnsTemplate` 写死数字（如 `lanes(2)`）→ P1，必须 BreakpointModel（私仓）动态获取
15. **R6.6（客户升级）**：壳工程 build-profile.json5 缺 `buildProfileFields`（appName/appBaseType/ChanelId 必填，三方 key 按工程实际）→ P1

**真实 refactor 回归类（2026-04 用户审核录入，audit 与 verify 必扫）**：

16. **RR1（MUST）**：壳工程 `commons/lib_common`、`commons/lib_widget` 本地副本未删（已引私仓但本地子模块还在）→ P0，违反私仓优先
17. **RR2（MUST）**：冗余 `PageMap.ets`——Index.ets 已用 `Navigation(RouterUtils.getStack())`（无 `.navDestination`），但工程内还存在手写 `@Builder PageMap` 长 if-else → P0 删除（lib_common 已自带 @RouterMap 注解注册）
18. **RR3（MUST）**：ViewModel 放在错误的模块——两种子模式：**RR3-a** 业务专用 VM 堆在 `business_common/viewmodels/`；**RR3-b** VM 放在**错误的 business 模块**（如 `SplashViewModel` 在 `business_login` 而非 `business_home`）→ P0 回迁到主调 Page 所在模块
19. **RR4（SHOULD→MUST 当 VM 已存在）**：page struct 已持有 `vm: XxxViewModel = new XxxViewModel()`，但页面里还残留 `@Local`/`@State` 与会被 mutate 的副作用 → P1 下沉到 VM。**配套 P0**：VM 字段必须 `@Trace`，否则 page 读 `vm.field` 编译过但运行时 UI 假死（首次值之后再无更新）
20. **RR5（MUST）**：资源全堆在壳工程——**RR5-a** 图片资源堆在 `products/*/src/main/resources/base/media/` 但引用全来自 features；**RR5-b**（2026-04 新增）颜色/字符串资源堆在壳工程 `element/color.json` 和 `string.json`，包含大量业务专属条目（如 `login_*`、`tab_*`、`ppt_*`），但**壳工程不被 features 依赖**，导致模块级编译报错 → P1 按业务下沉。归属规则：被 1 个 feature 引用 → 迁该 feature；被 ≥2 个 feature 引用 → 迁 `business_common`；壳工程仅保留 `start_window_background`、`module_desc`、`EntryAbility_*` 等自身配置必需条目
21. **RR6（MUST，2026-04 新增）**：自建完整 HttpClient 封装类（包含 get/post 等完整 HTTP 方法 + 拦截器 + 签名 + 响应解析），等价于私仓 RequestUtil + ExternalReqUtil 的替代品 → P0 违反 R2.0 私仓优先原则。**不适用「单点 axios」MAY 豁免**——单点豁免仅限如 AI baseline 的 ReadCoverCreate 这种极窄单次调用，不适用于完整 HTTP 客户端封装

### 2026-04 客户反馈触发的对称性反思（横向补全）

> **核心权威基线**：所有规则严格度的最终依据是 [`~/Desktop/HUAWEI/wfhc/features/develop_rule.docx`](~/Desktop/HUAWEI/wfhc/features/develop_rule.docx)（"鸿蒙客户端原生开发规范"）。AI/Scan 双 baseline 是规则**容忍度边界**的实证，docx 是**规则方向**的权威。两者冲突时以 docx 为准 + 客户最新校准记录覆盖（见 [customer-checklist.md](./references/customer-checklist.md)）。

> 客户反馈的三条问题（VM 错位、资源囤壳、HttpClient 造轮子）共享三个根因模式。skill 已横向补全到全谱（详见 [audit-patterns.md § 对称性原则](./references/audit-patterns.md)）：

**A. 错位放置（RR3 全谱）**：
- RR3-a：业务专用 VM 错放 business_common（已有）
- RR3-b：VM 放在错的 business 模块（已加，主调 Page 反查）
- **RR3-c**：Service 错位（业务专属 service 在 business_common 或别的 business）
- **RR3-d**：Bean / DTO 错位（业务专属 DTO 在 business_common）
- **RR3-e**：Component / Dialog 错位（业务专属 UI 在 lib_widget 或 business_common）
- **RR3-f**：一文件多 class 跨模块（如 `AuthViewModel.ets` 同时含 SplashViewModel + LoginViewModel，主调 Page 在不同 business），必须拆文件

**B. 壳工程囤积（RR5 全谱）**：
- RR5-a：媒体资源（已有）
- RR5-b：color.json / string.json 业务条目（已加）
- **RR5-d**：float.json / boolean.json 业务条目
- **RR5-e**：壳工程 pages 残留业务页面（壳仅 Index/RouterBuilders）
- **RR5-f**：壳工程 ets 残留 services/util/bean/viewmodel 目录（壳仅 EntryAbility + 路由入口 + 启动初始化）

**C. 私仓重复造轮子（RR6 全谱）**：
- RR6（HttpClient）已加
- **RR6-b**：自造 Logger / LogUtil（私仓 lib_common Logger 已存在）
- **RR6-c**：自造路由工具（私仓 RouterUtils 已存在）
- **RR6-d**：自造 KV 存储（私仓 PreferenceUtil 已存在）
- **RR6-e**：自造 Toast / Dialog 容器（私仓 lib_widget 已存在）
- **RR6-f**：自造 DateUtil / StringUtil / ScreenUtil / DeviceUtil（私仓 lib_common 已存在）
- **RR6-g**：自造事件总线 / EventBus（私仓 lib_common EventHub 已存在）

**反自我安慰原则（Phase 1/4 必跑）**：代码内注释或 ADR 中自称「MAY 豁免 / 单点例外 / 已评估保留」**不能作为豁免证据**——必须用 grep 重新核对实际边界（行数、调用方数、覆盖方法数）。MAY 豁免硬上限 = 1 个调用点 + ≤30 行 + 不形成可复用类。三项任一超出即升级为 MUST。详见 [audit-patterns.md § audit 阶段反自我安慰原则](./references/audit-patterns.md)。

详细 grep 与修复模板见 [audit-patterns.md § 真实回归模式（2026-04 用户审核录入）](./references/audit-patterns.md)。

audit 时**先看 ai-baseline.md，再判 rule-checklist.md**——双 baseline 实证 + 客户校准记录联合作为判定依据。

## 四阶段 workflow

整个改造分四步，每步之间有 HARD-GATE 必须等用户点头才能继续。把"执行"和"验证"独立成两段——验证不只是编译通过，还要重跑 audit 确认 P0/P1 真的消除、产出 ArkTS 静态检查 + 规则合规度报告。

```
[Phase 1 Audit]    扫现状，按规则严格度分级输出差距
                   → spec/refactor-audit.md
                   ↓ HARD-GATE：用户确认改造范围 + 优先级 + 软规则豁免
[Phase 2 Plan]     拓扑排序差距，给出可执行步骤 + 风险评估
                   → spec/refactor-plan.md
                   ↓ HARD-GATE：用户确认拆分粒度 + 私仓版本 + 改造批次
[Phase 3 Execute]  按 plan 落地代码，配置先行→骨架先行→业务模块逐个迁
                   → 改 .ohpmrc / oh-package / build-profile + 业务源码
                   → spec/refactor-execution-log.md（每步 git diff 摘要）
                   ↓（无 HARD-GATE，直接进 Phase 4）
[Phase 4 Verify]   多维验证 + 写最终报告
                   ① 编译闭环（调用 hmos-fix-build-errors）
                   ② 重跑 Phase 1 的 audit 脚本，对比改造前后
                   ③ 静态合规扫：每条用户接受的规则是否真消除
                   ④ 行为保留检查：列出可能有运行时差异的改动给人复核
                   → spec/refactor-report.md
```

> **HARD-GATE 是什么意思**：你**必须停下来**让用户回复确认，不要自己往下走。哪怕用户的项目看起来很简单、计划看起来很显然——架构改造的代价很高，多一次确认远比少一次划算。Phase 3→4 之间没有 HARD-GATE，因为 Phase 4 本质是"自检 + 报告"，发现问题才回去补，不需要再问用户。

---

## Phase 1：Audit（盘点现状）

目标：扫一遍工程，把跟规范不符的地方列成清单。**不改任何代码**。

### 步骤

1. 让用户给出工程根目录路径（如 `/path/to/some-harmony-app`）。
2. 读 `references/rule-checklist.md`，按 6 大类逐条扫描：
   - 工程结构（products / features / components **三段都必须存在**；features/ 下**非 common business 必须 ≥ 2 个**——单 business_main 等价反例堆砌；components/ 下**至少 1 个 module_***。详见 [`references/01-project-structure.md` § 反作弊](./references/01-project-structure.md)）
   - 私仓依赖（`.ohpmrc` 是否包含 `repo.dadoubk.cn`？`oh-package.json5` 是否引用 lib_*？版本是否合规？）
   - 代码分层（`ets/` 下是否拆出 `components/constants/pages/viewmodel/bean/util`？还是平铺？）
   - 资源规范（用没用 webp/svg？有没有 png 大图？webp 是不是 3x？）
   - 公共样式（`color.json` 命名是否符合 `color_main / color_text / color_dialog_*` 规范？）
   - 其他（状态管理是 v1 还是 v2？ViewModel 有没有继承 BaseViewModel？路由是不是 Navigation + RouterUtils？网络请求有没有传 AbortController.signal？JSON 反序列化用 interface 还是 class？）
3. 用 Glob/Grep 搜索关键模式（参考 `references/audit-patterns.md`）。
4. 输出 `spec/refactor-audit.md`，按 **rule_id / 现状 / 差距 / 改造影响范围（文件数/行数）/ 推荐优先级** 表格化。
5. **HARD-GATE**：把审计报告丢给用户，问“哪些项要改、优先级如何、有没有要跳过的”。等用户确认。

### 优先级建议

把改造拆成 P0/P1/P2，方便用户分批接受：

- **P0**（不改就跑不通 / 影响后续所有改造）：工程拆分骨架（**三段齐 + features 多 business + components 至少 1 个 module**）、`.ohpmrc`、私仓依赖。
- **P1**（影响代码可维护性，需逐文件改但模式重复）：状态管理 v1→v2、ViewModel 继承 BaseViewModel、路由迁到 RouterUtils、网络请求接入 RequestUtil + AbortController、color.json 改名。
- **P2**（局部优化，单点处理）：webp 3x 转换、字体 weight 数值化、RelativeContainer 替代深嵌套、JSON 反序列化 class→interface、`buildProfileFields` 配置。

---

## Phase 2：Plan（迁移计划）

目标：把 audit 里用户认可的项，转成可执行的、有顺序依赖的步骤清单。

### 输出 `spec/refactor-plan.md` 包含

- **拓扑顺序**：基础设施先行（先建 features/business_common，再迁其他 business），具体顺序见 `references/migration-order.md`。
- **每步的明确产物**：要新建/修改/删除哪些文件，要新增哪些 import，要替换哪些 API。
- **私仓版本锁定**：列出本次接入的 lib_* 各自版本，参考 `assets/root-oh-package.json5.template`。
- **风险点**：如 LazyForEach → Repeat 涉及 @Builder 传参语义变化（必须传整个 RepeatItem，否则刷新失效），明确提示。
- **回退策略**：每个 P0/P1 步骤是否可独立回退？如果 Phase 3 中途失败，哪些步骤要一起回退？

### 必跑：跨业务依赖图分析（防循环依赖事后救火）

**Phase 2 HARD-GATE 之前必须跑**，根据当前代码（即使在 entry 单模块状态）模拟出"按 plan 拆分后的"跨业务引用关系：

```bash
# 先按 plan 把 features/business_*/ 骨架建好（哪怕空 Index.ets），然后：
python3 <skill-dir>/assets/analyze-cross-business-deps.py <project-root>
# 产出 spec/module-dependency-graph.json + spec/cross-business-deps.md
# 退出码 2 = 检测到强连通环 → Phase 3 BLOCKED，必须先决定哪些符号上提到 business_common
```

**为什么必须前置**：上一轮重构事后救火过 3 次循环（business_login ↔ business_vip 的 FreeCountService、business_home ↔ business_file 的 PptFileLoadViewModel）。每次都是先加 oh-package 依赖 → ohpm install 报 `indirect dependency cannot be same as module name` → 才回头上提符号。**plan 阶段就识别这些环**比执行阶段救火便宜一个数量级。

报告里的「上提建议清单」直接并入 refactor-plan.md 的"步骤 0 基础设施"里，确保 Phase 3 第一批就把这些符号迁到 business_common，而不是先迁业务再发现要返工。

### HARD-GATE

把计划摆给用户，重点请用户确认三件事：

1. business 模块拆分粒度：现有页面归到哪个 business_*？要不要新建 business？（参考 AI 工程：home / mine / login / setting / interaction / video / common）
2. 私仓版本：使用 `assets/root-oh-package.json5.template` 列的最新版本，还是项目已有版本？是否启用鸿蒙联运（决定 lib_hmiap 走 1.0.0 还是更高）？
3. 改造批次：一把全做，还是先做 P0 验证编译，再做 P1/P2？

---

## Phase 3：Execute（执行 plan）

目标：按 plan 落地代码。**只改代码，不做验证**——验证留给 Phase 4。

### Phase 3 反偷懒硬约束（2026-04 新增——客户反馈触发）

> **背景**：上一轮 refactor 中 agent 在 fix 阶段写过这种话术——「全堆 business_common 是当前紧迫修复，per-feature 分发后续再做」「最小可行修复」「先粗后细」「简化处理」「临时方案」。这些都是**客户优先级声明明确禁止的「工程量大→deferred」的变种**，但 skill 原版只在 audit 阶段查注释，execute 阶段没人盯，agent 就钻空子。

**Phase 3 每完成一条 RR 修复必须满足以下 4 条，缺一不可**：

1. **话术黑名单**：commit message / execution-log / 用户回复 中**禁止**出现下列措辞——「最小可行修复 / 紧迫修复 / 先粗后细 / 后续再做 / 临时方案 / 简化处理 / 暂时全堆 / 先这样」。命中即视为偷懒，**必须撤回 commit 重做**或写 ADR。**特例豁免仅限**：技术不可达 + 已写 ADR 偏离登记 + 上报阻塞依赖方。

2. **归属决策表必出**（针对 RR3 / RR5 / RR6 等多目标分发型违规）：每条违规修完必须在 execution-log 里列出 **决策表**——
   ```
   | 违规对象 | 命中规则 | 引用方 (实测 grep) | 归属决策 | 决策依据 |
   |---|---|---|---|---|
   | color_login_subtitle | RR5-b | business_login (1) | business_login | RR5 归属规则: 1 feature → 该 feature |
   | color_main | RR5-b | business_home, business_login, business_ppt (3+) | business_common | RR5 归属规则: ≥2 feature → common |
   ```
   **没有这张表 = 没修完**。

3. **对照规则逐条贴标签**：execute 完每条 RR，必须能回答「这次修复用了 references/audit-patterns.md / references/0X-*.md 中的哪条文字规则？」——不能回答的就是没有对照规则在改。

4. **「先粗后细」是禁忌**：不允许把 MUST 拆成「这次粗做 + 下次细做」两段。要么一次按规则做完，要么作为技术不可达写 ADR。skill 客户优先级声明硬上限——「不允许"工程量大"作为 MUST 规则的 deferred 理由」。

### 执行原则

1. **配置先行**：先改 `.ohpmrc`、根 `oh-package.json5`、`build-profile.json5`，再改业务代码。配置错了后面全是瞎忙。
2. **骨架先行**：先把目录骨架（products/phone、features/business_*、components/module_*）建好，再往里挪文件。空目录用 `Index.ets` 占位。
3. **按 plan 顺序**：Phase 2 已给出拓扑排序，严格按顺序执行，不要跳步。
4. **小步执行 + 日志化**：每完成一个 plan 步骤，把"做了什么、改了哪些文件"追加到 `spec/refactor-execution-log.md`。这是 Phase 4 验证的素材。
5. **保留行为**：架构整改的目标是"不变功能、改结构"。如果某项改造可能改变运行时行为（比如 v1→v2 状态管理对 @Observed 的差异），在 execution-log 里**显式标注 BEHAVIOR_RISK**，让 Phase 4 把它列出来给人复核。
   - **私仓偏离同步落 ADR**：执行过程中若被迫**绕开私仓 / 评估后保留本地实现 / 私仓暂未启用**，**当下立刻**到 `docs/decisions/` 追加 ADR 条目（详见下文 [ADR 决策记录](#adr-决策记录私仓偏离登记) 章节），不要拖到 Phase 4 才补——拖了你会忘哪些是有意为之、哪些是漏改。
6. **代码改写工具强约束（避免反复破坏文件）**：跨文件结构性改写（router/import/装饰器/export/VM 继承等）**禁止**直接用 `perl -i` / `sed -i` / 多行宽松 regex——这种做法在上一轮重构里因贪婪匹配跨多语句吞代码（删了 26 处 `.catch`、把 50+ 文件的 `: number =` 改成 `:as object=`）反复破坏文件，每次都得 `git restore` 整套重做。**统一走 `assets/refactor-codemods.py` 子命令**，它用平衡括号解析器（追踪 `{}` `()` 字符串/反引号深度）实现，绝不跨语句越界：
   ```bash
   python3 <skill-dir>/assets/refactor-codemods.py router-replace <project-root>
   python3 <skill-dir>/assets/refactor-codemods.py imports-fix <project-root> --map spec/import-map.json
   python3 <skill-dir>/assets/refactor-codemods.py strip-entry <project-root>
   python3 <skill-dir>/assets/refactor-codemods.py vm-extends <project-root>
   python3 <skill-dir>/assets/refactor-codemods.py remove-router-catch <project-root>
   python3 <skill-dir>/assets/refactor-codemods.py add-page-params-cast <project-root>
   ```
   只有**纯单行**的 perl/sed 在小范围使用是允许的（如修一个 oh-package.json5 的字段）。任何带 `[\s\S]*?` / 跨多行 / 正则 alternation 的指令都必须改用 codemods.py。
7. **每个 business 迁完必须增量编译（HARD-GATE）**：上一轮重构等所有 7 个 business 全部迁完才第一次编译，结果一上来就是 2314 错——错误来源完全混在一起，根本不知道哪个 business 引入的。本 skill 现在**强制每完成一个 business** 跑一次：
   ```
   委派 hmos-fix-build-errors，build harmony app at <root> in unsigned mode, fix errors in loop until success
   ```
   错误未清零**禁止进入下一个 business 的迁移**。这把"几百错的难题"分摊成"每次几十错的简单题"，每个错都明确归因到刚迁的那个 business。
8. **每个 Step 完成必须 git commit**：execution-log 里记录 commit SHA。这样破坏性失误（如下次又出现误正则）可以精确 `git revert <sha>` 而不是从头重建。提交信息格式：`[refactor] step N.M: <短描述> (<files-changed> files)`。

### 关键改造模式

按规则编号详见各 references：

- 工程结构 → `references/01-project-structure.md`
- 私仓 + .ohpmrc → `references/02-private-deps.md`
- 代码分层 + 资源 + 颜色 + 字体 + 间距 → `references/03-layering-styles.md`
- 状态管理 v2 + Repeat + ViewModel/BaseViewModel + Navigation/RouterUtils → `references/04-state-routing.md`
- 网络请求 + 持久化 → `references/05-network-persistence.md`
- 页面布局 + build-profile → `references/06-layout-config.md`

每个 reference 文件包含：**规则原文 → 反例（重构前）→ 正例（重构后）→ 自动化检测的 grep 模式**。

### Bundled assets

直接复用 `assets/` 下的模板文件，不要凭空生成：

- `assets/ohpmrc.template` — 标准 .ohpmrc，含三个 registry
- `assets/root-oh-package.json5.template` — 根 oh-package（含 dependencies + overrides，私仓版本已锁定）
- `assets/product-oh-package.json5.template` — 壳工程 oh-package
- `assets/feature-oh-package.json5.template` — business 模块 oh-package
- `assets/color.json.template` — 标准命名颜色资源
- `assets/build-profile-target.template.json5` — `buildProfileFields` 示例
- `assets/feature-module-skeleton/` — 标准 ets/{components,constants,pages,viewmodel,bean,util} 目录骨架
- `assets/page-map.template.ets` — **壳工程 Index.ets 模板**（含 NavDestination 包裹，避免运行时空白）
- `assets/gen-page-map.py` — 从 `features/business_*/Index.ets` 自动扫描 Page 导出，生成正确的 `products/phone/.../Index.ets`
- `assets/refactor-codemods.py` — **跨文件结构性改写工具集**（router/import/strip-entry/vm-extends/remove-router-catch/add-page-params-cast）。Phase 3 强制走此脚本，禁止用裸 perl/sed。**注**：`router-replace` 已内置自动剥除 `.catch()` 残留（见 [v2 playbook §2.2](./references/v2-migration-playbook.md)）
- `assets/analyze-cross-business-deps.py` — 模块依赖图 + 强连通环检测，Phase 2 必跑产出 `spec/cross-business-deps.md` + `spec/module-dependency-graph.json`
- `assets/global-state-models.template.ets` — **v1→v2 迁移核心资产**：3 × @ObservedV2 包装类（SafeAreaModel / LoginStateModel / VipStateModel）+ GlobalState 单例。替代 `AppStorage.setOrCreate('key', v) + @StorageProp('key')` 模式。配合 [v2 playbook](./references/v2-migration-playbook.md) Step 1 使用

复制时根据用户工程的具体名（如 business_chat 替代 business_common）做最小化字符串替换，不要重排模板结构。

### 壳工程 Index.ets 强制走生成器（避免致命陷阱）

Phase 3 Step 4「壳工程」**禁止**手写 `products/phone/src/main/ets/pages/Index.ets`。必须：

1. 先在每个 `features/business_*/Index.ets` 里 export 自家 Page struct（如 `export { LoginPage } from './src/main/ets/pages/LoginPage';`）
2. 跑 `python3 assets/gen-page-map.py <project-root> --initial SplashPage`，让脚本生成 Index.ets
3. **静态校验**（生成器内置 + Step 4 完成后再跑一次）：
   ```bash
   INDEX=products/phone/src/main/ets/pages/Index.ets
   grep -A 60 '@Builder' "$INDEX" | grep -q 'NavDestination(' \
     || { echo "❌ FATAL: PageMap 未用 NavDestination 包裹 → 运行时所有页面会空白"; exit 1; }
   ```
   不通过 → **Phase 3 不得进入 Phase 4**，修正后重跑。

**为什么硬性要求**：手写 Index.ets 极易漏 `NavDestination()` 包裹，编译期不报错、运行时所有页面变白屏（无任何错误日志，故障定位耗时极长）。详细反模式见 [`references/04-state-routing.md` § R6.4-CRITICAL](./references/04-state-routing.md)。

---

## Phase 4：Verify（验证 plan）

目标：确认 Phase 3 的产出**真的**符合 plan 和规范。Phase 3 改完不等于改对——Phase 4 多维交叉验证后才能下结论。

### 五维验证

依次跑下面五步，**任何一步失败都回退到对应的源头修复**（不是直接报错退出）。**注意：⑤ 运行时冒烟是 HARD-GATE——只过 ①~④ 不算成功，没有"打开 App 能看到东西"就不能写 PASSED 报告。**

#### ① 编译闭环

调用 `hmos-fix-build-errors` skill：

- unsigned 模式跑 hvigor 编译。
- 失败进入修复循环——但**修复 commit 必须只针对编译错误本身**，不要顺手做规则改造（避免范围蔓延）。
- 修复循环超过 N 轮（默认 5）仍不过 → 中止，把残留错误写进 report 让用户介入。

#### ② 重跑 audit 对比改造前后

读 `spec/refactor-audit.md`（Phase 1 产物），对每条用户接受改造的项重新跑 `references/audit-patterns.md` 里的检测脚本：

- ✅ 改造前命中、改造后无命中 → **PASSED**
- ❌ 改造前命中、改造后仍命中 → **FAILED**：定位到 execution-log 哪一步漏改，回 Phase 3 补
- ⚠️ 改造后冒出**新**违规 → **REGRESSION**：通常是改造引入新违规（如把 v1 改 v2 时不小心又写了 @State），回 Phase 3 修

**额外检查（2026-04 新增——反 fix 阶段偷懒）**：除了「违规命中数为 0」，还要检查「修复时的归属决策是否符合 RR 归属规则」——

- ✅ 每条 RR3/RR5/RR6 类违规在 execution-log 中有 **归属决策表**（违规对象 / 命中规则 / 引用方 / 归属决策 / 决策依据）
- ✅ 决策表中每条「归属决策」都引用了 references/*.md 中对应规则的文字（如 RR5: 1 feature → 该 feature）
- ✅ commit message + execution-log 中**未出现**话术黑名单（最小可行 / 紧迫修复 / 先粗后细 / 后续再做 / 临时方案 / 简化处理 / 暂时全堆 / 先这样）
- 任一不通过 → **回 Phase 3 重做该项**（不接受「编译过 + audit 命中数=0」作为通过条件）

#### ③ 静态合规扫（与 ② 互补）

② 看的是"改造前列出的差距是否消除"，③ 看的是"改造产出本身是否合规"——两件事不一样。比如新建的 features/business_X 是否：

- `oh-package.json5` 用了模板格式
- `Index.ets` 有正确导出
- 新写的 ViewModel 真的继承了 BaseViewModel
- 新加的 RequestUtil 调用真的传了 signal

跑 `references/audit-patterns.md` 的全量检查（不只用户接受的子集），命中视为 P1 报告。

#### ④ 行为保留检查

Phase 3 execution-log 里所有标了 `BEHAVIOR_RISK` 的步骤（v1→v2 状态语义差异 / @Provide → AppStorageV2 数据流向变化等）汇总到 report，**显式提示用户人工复核**。本 skill 不做自动行为验证（那是 `arkts-visual-verify` / `arkts-dt-verifier` 的事，按需委派）。

#### ⑤ 运行时冒烟（HARD-GATE，**编译过 ≠ 跑得起来**）

**只过 ① 不算 PASSED**——一些致命陷阱（如 PageMap 漏 NavDestination 包裹、错误的 `loadContent` 路径、main_pages.json 与实际页面不匹配）**编译期完全不报错，运行时却让所有页面变白屏**。必须做最小冒烟：

1. **就绪条件**（任一缺失则跳过本步、写明原因到 report）：
   - `hdc` 命令可用 — **若 `which hdc` 失败**，按以下顺序回退查找：
     1. `/Applications/DevEco-Studio.app/Contents/sdk/default/openharmony/toolchains/hdc`（macOS DevEco 默认）
     2. `~/Library/OpenHarmony/Sdk/*/toolchains/hdc`（macOS 单装 SDK）
     3. `$OHOS_SDK_HOME/toolchains/hdc` / `$DEVECO_SDK_HOME/default/openharmony/toolchains/hdc`（环境变量）
     4. Windows 用户对应 `C:/Program Files/Huawei/DevEco Studio/sdk/default/openharmony/toolchains/hdc.exe`
     找到后用 `HDC=<full-path>` 显式调用，不要把不在 PATH 当作"hdc 不可用"
   - 至少一个 HarmonyOS 模拟器/真机已连接（`$HDC list targets` 非空）
   - 上一步 ① 编译已 PASSED（产物 `products/phone/build/.../*.hap` 存在）

2. **执行**（建议委派 `arkts-scenario-runner` 完成；直接跑也行）：
   ```bash
   hdc install -r <hap-path>          # 安装
   hdc shell aa start -a EntryAbility -b <bundleName>   # 启动
   sleep 3                            # 等渲染
   hdc shell snapshot_display -f /data/local/tmp/smoke.png
   hdc file recv /data/local/tmp/smoke.png /tmp/smoke.png
   ```

3. **冒烟深度要求**（首屏非空只是最低门槛，**v1→v2 / 大型重构必须做深度路径**）：

   | 冒烟级别 | 路径 | 适用场景 |
   |---|---|---|
   | L1 首屏 | App 启动 → 首页渲染 | 纯目录重命名 / 加 .ohpmrc / 加 color token |
   | L2 一跳 | L1 + 至少 1 次 RouterUtils.push/replace 跳转 | 引入 Navigation/RouterUtils |
   | L3 混合树 | L2 + 至少 1 个 v2 child 在 v1 host 下渲染（或反向） | v1↔v2 边界改动（@Event 加装饰、@Param 替 @Prop）|
   | L4 状态环 | L3 + 触发 AppStorageV2 setter + 另一 page 读取 | v1→v2 全栈 + dual-write（playbook Step 4 后必跑）|

   实战教训：AIPPT 项目 v2 全栈迁移**只过 L1 不足以发现 mixed-mode 编译错+ NavPathStack 失效+@Event 缺失等问题**；至少跑到 L3 才能 PASSED。

4. **判定**：用以下任一方式判定首屏非空（按可用性降序）：
   - **A. 像素差异法**：截图 vs 启动闪屏图（已知系统 splash）的像素差大于阈值（默认 5%）→ PASSED
   - **B. 委派 `arkts-visual-verify`** 做与 Android 端的视觉对比 → 拿到差异分级
   - **C. UI 树审计**：`hdc shell uitest dumpLayout` 输出非空且根节点 child 数 > 0 → PASSED

5. **失败处理**：
   - 黑/白屏 → 第一嫌疑人：`products/phone/.../Index.ets` 的 PageMap @Builder 未用 `NavDestination()` 包裹（详见 references/04 § R6.4-CRITICAL）
   - 启动报错 → 检查 EntryAbility `loadContent('pages/Index')` 路径与 `main_pages.json` 是否匹配
   - 首屏出现但缺关键元素（导航栏/底 tab）→ 列入 BEHAVIOR_RISK
   - **冒烟失败一律回 Phase 3 修，不直接 PASSED 收工**

6. **冒烟产物**：截图存 `spec/smoke/` 目录，refactor-report.md 必须 inline 引用截图作为「能跑」的实证。

> **决策点**：⑤ 失败比 ①/②/③ 失败更严重——它意味着用户打开 App 看不到任何东西。Phase 4 在 ⑤ FAILED 时**强制阻塞 report 出**，避免「编译过就报告搞定」的虚假合规。

### 输出 `spec/refactor-report.md`

固定结构：

```markdown
# Refactor Report
## Build status
- compile: PASSED / FAILED (round N)

## Rule compliance (vs Phase 1 audit)
| rule_id | 改造前 | 改造后 | 状态 |
|---|---|---|---|
| R6.1a | 8 处 | 0 处 | ✅ PASSED |
| R5.1-a | 缺 19 token | 已补全 | ✅ PASSED |
| R6.3c | 5 个 API 缺 signal | 1 个未改 | ❌ FAILED → ${file}:${line} |

## New regressions (改造引入的新违规)
- ...

## Behavior risks (需要人工复核)
- 文件 / 改动 / 风险描述

## Deferred items (用户在 Phase 1 决定豁免的项)
- ...

## Git diff 摘要
- 共 N 个 commit / 改动 M 个文件 / 新增 K 个模块
```

> **决策点**：如果 ②/③ 出现 FAILED 或 REGRESSION，**自动回 Phase 3 修复后重跑 Phase 4**，不需要再问用户——因为这些都是规则确定性问题。只有 ① 编译循环上限或 ④ BEHAVIOR_RISK 才需要人介入。

---

## ADR 决策记录（私仓偏离登记）

> **背景**：本规范贯彻"私仓优先"原则，但 100% 私仓覆盖在真实项目里**做不到**——总会有协议不匹配、API 设计缺陷、视觉样式不可配、暂无业务需求等情况导致绕开或不启用。这些偏离**必须有书面记录**，否则：
> - 客户回顾"为什么有些功能没用私仓"时无据可依
> - 私仓团队后续修复后没人知道该收回哪些偏离
> - 后人（包括下一轮重构者）会重蹈覆辙再踩一遍坑
>
> 工程根目录下统一用 **`docs/decisions/`** 作为偏离登记目录，遵循轻量级 ADR（Architecture Decision Record）格式。

### 何时写 ADR

| 触发场景 | 落到哪份文档 |
|---|---|
| 试过私仓 API，因签名/契约/响应格式不兼容**被迫绕开** | `0003-private-repo-deviations-registry.md` 表格追加一行 |
| 试过私仓 API，因不暴露关键字段（如 `resultStatus`）/视觉样式锁死/UX 不可接受 而**绕开** | 同上 0003；**重大决策（涉及 SDK 替换、依赖图变更）**额外写独立 ADR `NNNN-<topic>.md` |
| 私仓有等价能力，但本地实现因业务语义（如 sticky 事件）/形态差异（如多段 dialog）**保留** | `0004-private-repo-not-adopted-registry.md` 的 A 类（本地实现私仓有等价）/ B 类（私仓不兼容） |
| 私仓提供能力但项目暂无业务需求 | 0004 的 C 类（业务驱动接入） |
| 任何**违反规范文档某条 MUST 规则**但有充分理由的决策 | 独立 ADR `NNNN-<topic>.md` |

### 文件骨架

```
docs/decisions/
├── README.md                                    (索引：每条 ADR 一行链接)
├── 0001-<重大决策标题>.md                       (单项 ADR — 如 SDK 直连)
├── 0002-<重大决策标题>.md                       (单项 ADR)
├── 0003-private-repo-deviations-registry.md     (live registry — 偏离登记表)
└── 0004-private-repo-not-adopted-registry.md    (live registry — 未启用登记表)
```

- 单项 ADR：每条**重大决策**独立成文（一般 100-200 行），含背景 / 根因 / 决策 / 不破坏的部分 / 不选择的方案 / 回归路径 / 影响七节
- live registry（0003/0004）：表格形式，**每行一个偏离条目**，新增偏离时追加；私仓修复后把对应行的状态改成 Superseded 或直接删除并在 git history 留痕

### 单项 ADR 模板

```markdown
# ADR-NNNN: <一句话决策标题>

- **日期**: YYYY-MM-DD
- **状态**: Proposed / Accepted / Superseded by [ADR-NNNN]
- **决策范围**: 涉及的文件路径列表
- **关联**: 相关 audit delta / 其他 ADR / commit（**对外文档不要引用 commit hash**）
- **see also**: 相关 ADR 链接

## 背景
此次改造为什么会触发这个决策？(2-4 段)

## 根因
私仓 / 服务端 / 设计 哪一层导致必须偏离？给出可复现的证据（hilog / API d.ets / 实测响应等）

## 决策
具体改成什么；列出代码层面的契约（接口签名 / 文件位置 / 依赖项变更）

## 不破坏的部分
哪些私仓接入**仍保留**——避免被误读为"全面回滚"

## 不选择的方案
列其它候选 + 不选原因（防止后人再走一遍弯路）

## 回归路径
私仓 / 服务端补齐能力后，**逐步**怎么切回来。这是 ADR 最关键的一节：
- 触发条件（私仓提供 X 字段 / 服务端开 Y 通道）
- 替换步骤（按序）
- 状态变更（本 ADR 改 Superseded）

## 影响
- **代码**: 实际改了哪些文件
- **架构合规性**: 偏离了规范文档哪条规则、规范是否允许豁免
- **行为对齐**: 与基线（feat 分支 / Android 端）是否一致
- **依赖图**: oh-package.json5 是否变更
```

### 0003 偏离登记表骨架

```markdown
# ADR-0003: 私仓接入偏离登记表

- **日期**: YYYY-MM-DD
- **状态**: Accepted（live registry，新增偏离时追加条目）
- **决策范围**: <模块路径汇总>

## 背景
为什么必须有这份登记 — 私仓在真实环境的若干场景下不可用，每次绕开都需可追溯

## 根因（共性）
列出共同根因（如签名协议不匹配 / 视觉锁死 / API 响应字段缺失等），便于一次理解所有条目

## 偏离登记
| # | 模块 / 文件 | 私仓 API（弃用） | 实际使用 | 症状 | 详细 ADR |
|---|---|---|---|---|---|
| 1 | <文件链接> | `lib_xxx.YYY` | <替代方案> | <用户可见症状> | 本表 / [ADR-NNNN](./NNNN-...md) |
| 2 | ... | ... | ... | ... | ... |

## 仍保留的私仓接入（验证有效）
列出**仍在用且工作正常**的私仓 API，避免被误读为"全面绕开"

## 回归路径
按条目逐项写"私仓修好后怎么切回"

## 影响
（同单项 ADR 模板）
```

### 0004 未启用登记表骨架

```markdown
# ADR-0004: 私仓未启用 / 本地实现登记表

- **日期**: YYYY-MM-DD
- **状态**: Accepted（live registry）
- **see also**: [ADR-0003](./0003-private-repo-deviations-registry.md)（本表互补）

## 背景
0003 记的是"试过私仓但用不了"；本表记的是"私仓提供等价能力但项目用本地或未启用"

## 分类
- **A 类** 本地实现，私仓有等价：理论上可替换为私仓
- **B 类** 本地实现，私仓不兼容：私仓 API 形态/视觉与业务需求不匹配
- **C 类** 私仓未使用：业务暂无需求

## A 类登记
| # | 本地文件 | 私仓等价 | 数量 / 范围 | 不接入原因 | 收回路径 |
|---|---|---|---|---|---|
| A1 | ... | ... | ... | ... | ... |

## B 类登记
（同上格式）

## C 类登记
| # | 私仓 API | 能力 | 当前应用是否需要 |
|---|---|---|---|
| C1 | ... | ... | 业务驱动接入 |

## 决策原则
1. A 类每项单独评估收回风险，不批量切换
2. B 类等私仓提供更灵活的 builder/preset 后再迁移；不主动改私仓
3. C 类业务驱动接入

## 影响
不影响当前代码（本表为登记，非操作）
```

### 写作约束（针对客户交付）

- **绝对不要在 ADR 里引用 git commit hash / SHA / 分支名**——客户拿到的是最终版本代码，commit history 对他们没有意义
- 用 file:line 引用代替"见 commit X"（用相对路径，渲染为可点击链接）
- 状态字段只用 `Proposed` / `Accepted` / `Superseded by [ADR-NNNN]` 三态
- 单项 ADR 文件名编号严格顺增，不复用旧编号

### 验证（Phase 4 必跑）

Phase 4 五维验证之外，**额外检查**：

- ✅ 每条 BEHAVIOR_RISK / 私仓绕开 在 `docs/decisions/` 都有对应条目（0003 行 或 独立 ADR）
- ✅ 每条偏离都有"回归路径"段落
- ✅ `docs/decisions/README.md` 索引完整列出所有 ADR
- ✅ 全工程 grep 不到对 `commit` / `SHA` / 分支名 / 内部分支策略 的引用（防止泄漏）

```bash
# 客户交付前自检
grep -rn "commit\|SHA\|feat_v[0-9]" docs/decisions/ && echo "❌ 含内部 commit/分支引用，请清理"
ls docs/decisions/0003-*.md docs/decisions/0004-*.md > /dev/null 2>&1 || echo "❌ 缺少 0003/0004 登记表"
```

---

## 输出物总览

整轮跑完后，工程根目录下应有：

```
<project-root>/
├── spec/                                       (内部产物 — 客户交付前可清理)
│   ├── refactor-audit.md            (Phase 1)
│   ├── refactor-plan.md             (Phase 2)
│   ├── refactor-execution-log.md    (Phase 3 - 每步 git diff + BEHAVIOR_RISK 标记)
│   └── refactor-report.md           (Phase 4 - 最终验证报告)
├── docs/decisions/                             (对外文档 — 客户交付时保留)
│   ├── README.md                               (ADR 索引)
│   ├── 0001-<重大决策>.md                      (单项 ADR，按需新增)
│   ├── 0002-<重大决策>.md
│   ├── 0003-private-repo-deviations-registry.md   (live registry — 试过私仓但用不了)
│   └── 0004-private-repo-not-adopted-registry.md  (live registry — 私仓有但项目用本地或未启用)
├── .ohpmrc                   (新建/更新)
├── oh-package.json5          (新增 lib_* 依赖 + overrides)
├── build-profile.json5       (新增 buildProfileFields)
├── products/phone/...        (壳工程，若原本是单 entry 则迁移)
├── features/business_*/...   (按 plan 拆出的 business 模块)
└── components/module_*/...   (公共组件，按需)
```

> **客户交付前**：`spec/` 目录是 skill 内部产物（audit / plan / execution-log / report），客户拿到的是最终代码 + ADR 文档；交付清单只需 `docs/decisions/` + 实际代码。`spec/` 可在交付前删除或仅保留团队内部归档。

## 写作约束

- 不要给改造代码加“原代码 / 新代码”这种注释，git diff 自身已经说明问题。
- 不要在 refactor-report 里复述全部规则，只列“做了什么 + 为什么”。
- 编译错误优先靠 `hmos-fix-build-errors`，不要在主流程里手工 try/catch 编译产物。

## 相关 skill

- `hmos-fix-build-errors` — Phase 4 ① 编译闭环时调用
- `arkts-knowledge-verifier` — Phase 3 改造过程对 ArkTS API/装饰器版本不确定时查文档
- `arkts-state-manager` — Phase 3 v1→v2 升级细节查询
- `arkts-navigation-builder` — Phase 3 RouterUtils + Navigation 接入查询
- `arkts-visual-verify` / `arkts-dt-verifier` — Phase 4 ④ 行为保留检查时按需委派（视觉对比 / spec 驱动测试）

如果用户的需求其实是 Android → HarmonyOS **从零迁移**，应改用 `a2h-spec` 系列；本 skill 只处理 **已经在 HarmonyOS 平台、要改架构** 的场景。
