---
name: a2h-incremental-migration
description: Android→HarmonyOS 增量同步。触发词："增量迁移 / 同步安卓新功能 / 再检查有没有要迁移的 / 对比一下两边 / 把 XX 功能搬过来"。**核心方法论是"行为同步"而非"源码差集"**——比对用户可感知的行为，不比类名/id/字面量。**本 skill 只负责"产出差异清单并交用户确认"**；spec 生成 + 计划 + 实施 + 验收全流程委托给 `arkts-spec-evolver`（`create+plan+execute+verify` 模式，自带两道 HARD-GATE 审批）。三种并列模式：§M1 Diff（有 commit 记录）/ §M2 Source-compare（只有两份代码）/ §M3 Targeted（用户指定功能锚点）。
metadata:
  type: pipeline
  domain: migration
  tags:
  - pipeline
  - migration
  - incremental
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

# a2h-incremental-migration

## ⛔ HARD CONSTRAINT — 生成范本统一 v2（最高优先级，不可省略）

凡本 skill 产出的差异清单 / 行为对齐说明 / spec 草稿 / 对照表 / 代码示例，**所有 HMOS 端范本必须 v2**，下游 `arkts-spec-evolver` 拿到的描述也必须 v2，禁向其传递任何 v1 范本。

| 场景 | 必须用（v2 + 客户私仓） | 禁用（v1 / 通用 ArkTS） |
|---|---|---|
| 组件装饰器 | `@ComponentV2` / `@ObservedV2` | `@Component` / `@Entry` / `@Observed` |
| 字段装饰器 | `@Local` / `@Param` / `@Event` / `@Provider` / `@Consumer` / `@Trace` / `@Computed` | `@State` / `@Prop` / `@Link` / `@Provide` / `@Consume` / `@ObjectLink` / `@StorageLink` / `@StorageProp` |
| 列表渲染 | `Repeat<T>(arr).each((obj: RepeatItem<T>) => {...}).key(...).virtualScroll()` | `LazyForEach` / `LazyDataSource` / `BasicDataSource` |
| 路由 | `RouterUtils.pushPathByName(RouterMap.X, params)`（lib_common）+ route_map.json 注册 | `router.pushUrl/replaceUrl/back/clear` / `NavPathStack.pushPath` 裸字符串 |
| 生命周期 | NavDestination 链 `.onShown/.onHidden/.onBackPressed` | page 内 `onPageShow/onPageHide/onBackPress` |
| 标题栏 | `NavHeaderBar`（lib_widget） | 手写 Row+Image+Text 标题栏 |
| 网络 | `RequestUtil` / `ExternalReqUtil`（lib_network） | `axios` / `http.createHttp` |
| KV 持久化 | `PreferenceUtil`（lib_common；UIAbility 显式传 ctx） | `@ohos.data.preferences` / `@kit.ArkData` |
| 关系型存储 | `@ohos/dataorm` Entity + DAO insertOrReplace | `@ohos.data.relationalStore` 裸用 |
| VM 基类 | 业务 page `extends BaseViewModel`（lib_common） | 自实现单例 ViewModel |
| 用户态 | `UserData.getInstance().isBinding()/.isVip()` | 手写 `userInfoModel.isLogin` / `vipLevel > 0` |
| 安全区 | `this.vm.windowModel.windowTopPadding/.windowBottomPadding` | 硬编码 `padding({ top: 36 })` |
| 多端列数 | `.lanes(GridRowColSetting.getWindowColumn(this.vm.breakPointModel.currentBreakpoint))`（注 P 大写） | `.lanes(2)` / `BreakpointModel.gridColumns`（字段不存在） |

**例外**：扫描既有 v1 老代码（grep 识别现状）允许命中 v1 符号；但**写出的范本 / 推荐做法 / spec 描述 / 给下游的对照表必须 v2**。若上游 Android 端无对应 v2 私仓概念，标 `// v2 待补私仓 API`，**不得回退 v1**。

## 📖 References 索引（详细操作手册）

主文聚焦"流程骨架 + 决策门 + 核心规则 + 三模式卡片"。**详细执行 / 命令 / 模板 / 示例** 全在 `references/`，**按需 Read**。

### 三模式详细执行（按 §3 决策门命中后 Read 对应一个，无需全载入）

| 模式 | 何时用 | 详细 references |
|------|--------|----------------|
| §M1 Final-state 优先 + commit 辅助 | 用户能给 git 信息 | `references/mode-m1.md`（M1.1-M1.6 完整执行）|
| §M2 Source-compare | 只有两份代码 | `references/mode-m2.md`（M2.1-M2.4 完整执行）|
| §M3 Targeted | 用户指定功能锚点 | `references/mode-m3.md`（M3.1-M3.4 + §M3.2.5 完整执行）|

### 共享规则与子流程的详细 references

| 主文章节 | 详细 references | 内容 |
|---------|----------------|------|
| §2.6 死代码过滤 | `references/dead-code-filter.md` | 5 类死代码完整定义 + 三模式过滤命令 + Python 剥离注释脚本 |
| §3.5 HMOS Spec 双重验证 | `references/spec-cross-check.md` | spec 目录扫描 / Step A+B 比对 / 反向扫描关键词提取规则 / 三源汇总 |
| §M1.1 + §M1.2 探测/diff | `references/m1-detection-commands.md` | final state + 辅助 commit 探测命令 / 本地 git + GitHub CLI |
| §M1.3 行为提取 | `references/m1-behavior-extraction.md` | Step 1/2/3 完整流程 / commit 前缀分类表 / 正反例 |
| §M2.2 LLM 源码并排阅读 | `references/m2-source-reading.md` | 5 字段证据要求 / 子代理 yaml 样例 / 主代理复核流程 |
| §M2.4 资源差集 | `references/resource-diff-commands.md` | 完整 grep/sed/comm 命令（图片/strings/endpoint/权限）|
| §M3.2.5 回归范围派生 | `references/regression-scope-derivation.md` | 7 维 grep 完整命令 / `## 回归范围` 栏目模板 / opt-out 格式 / LLM 语义补全 prompt / 漏报模式知识库 |
| §S2.5 Pre-Edit 机械核查 | `references/pre-edit-checklist.md` | 四步完整执行规则 / 越界报告模板 / 同义词复跑细则 |
| §S3.6 运行时回归 | `references/runtime-regression.md` | A/B/C 三类具体步骤 / runtime-regression-log.md 执行模板 / 真实漏检反例 |
| §4 架构映射表 | `references/arch-mapping.md` | 架构工具 13 项 + UI 控件 12 项 + 权限映射 7 项 + 每项反例 |
| §A 资源迁移附录 | `references/resource-migration.md` | 图片格式转换详表 + XML vector → SVG 字段映射 + GitHub 下载二进制命令 |

---

## 1. 定位与方法论

已完成初始迁移的鸿蒙项目，当 Android 端有新变更时，用本 skill 把变更同步过来。

### 1.1 核心原则：行为同步 ≠ 源码差集（**务必理解**）

A→H 跨越两种 UI 范式：命令式（Activity/Fragment/Adapter/ViewModel+LiveData/DialogFragment/RecyclerView）vs 声明式 v2（`@ComponentV2 struct` + `NavDestination` / `Tabs+TabContent+@Builder` / `*PageVM extends BaseViewModel + @Trace + emitter` / `@CustomDialog` / `List + Repeat.virtualScroll`）。**生成范本统一 v2，禁出现 `@Entry/@Component/@State/LazyForEach` 等 v1 形态**（见顶部 HARD CONSTRAINT 表）。

**同一用户感知功能，在两端会产生完全不同的源码符号**：

- ❌ **错误**：比对两端类名 / id / 字面量 / Retrofit endpoint 的集合差集。80%+ 是架构范式差异造成的假阳性，同时漏掉真正的业务变化（算法参数、分支条件、状态机步骤不在符号差集里）。
- ✅ **正确**：
  1. 从 Android **指定分支/commit 的 final state 源码阅读** 提取"用户可感知的行为变化"，commit history 仅作辅助校准证据
  2. 对每条行为变化，在 HMOS 代码里找**等价路径**（onClick → store → service → UI 渲染），不看类名
  3. 只把"HMOS 无等价行为路径"的条目放入差异清单

> 符号差集**仅适合资源层**（图片/string key/endpoint 等 name-as-identity 场景），不适合业务功能判断。

> **已覆盖基线**：判断「HMOS 有无等价行为路径」时，把 baseline 的 `spec/baseline/source-coverage-report.md`（多子仓另含 `module-dep-graph.json` / `cross-module-contracts.md`）作为「已认领能力」参照——已被某 baseline feature 锚定的源码行为视为「已覆盖」，不再列入差异清单，避免把上轮已迁移的行为当成新变更重复同步。

#### 1.1.1 Final state 是行为同步的真目标（**所有模式共享**）

用户感知到的行为 = **当前 final state 的运行时行为**。他打开 App 看到的是 HEAD 那个版本，不是 commit 链中间某个状态。所以：

- **主信源**：用户指定分支的 final state（HEAD 或某个具体 commit 的快照）。这是事实底线，任何分析最终必须能在 final state 源码里找到对应锚点。
- **辅助信源**：commit history（messages + 关键 patches）。提供 WHY（开发意图）+ HOW evolved（演进路径）+ 边界 case 暗示（fix 类 commit 揭示开发者考虑过的 edge case）。
- **冲突仲裁**：两者矛盾时**一律以 final state 为准**——commit 历史不能推翻代码事实（中间被加了又删的功能在 final state 里不存在 = 不该同步）。

这条原则统一了 §M1/§M2/§M3 三种模式的方法论：三者都是"final state → 行为轨迹"，差异只在辅助证据来源不同（§M1 用 commit history / §M2 用全量源码并排阅读 / §M3 用关键词锚点定位）。

### 1.2 三模块流程 + Evolver 委托

本 skill **只做差异识别和用户对齐**；spec / plan / execute / verify 全部委托 `arkts-spec-evolver`。

```
              用户请求
                 │
                 ▼
      ┌──────────────────────┐
      │  §3 决策门（必跑）     │
      │  问三个问题选模式       │
      └──────────┬───────────┘
                 │
        ┌────────┼────────┐
        ▼        ▼        ▼
      §M1      §M2      §M3
    Diff 模式  Source   Targeted
   (commit-   -compare  (功能
    driven)  (两份代码)   锚点)
        │        │        │
        └────────┼────────┘
                 ▼
         §S2 用户对齐关卡
         （差异清单确认，本 skill 独有）
            ├─ §S2.4 override 模式规则
            │   （跳对话 ≠ 跳机械核查）
            ▼
         §S2.5 Pre-Edit 机械核查
         （动代码前，每条差异必跑：
          目标文件完整读 + spec 反查 +
          同义词扫描 + 改后 git diff 自审）
                 ▼
         §S3 委托 arkts-spec-evolver
         create+plan+execute+verify
                 │
                 ├─ create   → spec/features/F-xxx.md
                 │              ★ Gate 1: spec 摘要审批
                 ├─ plan     → 单功能实现计划
                 │              ★ Gate 2: plan 摘要审批
                 ├─ execute  → 写代码
                 └─ verify   → 按验收标准验证
                 ▼
          §S4 完成摘要
```

**三道审批关卡的分工**：
- §S2（本 skill）："差异清单对不对？" — 我找到的东西是不是用户想同步的
- Gate 1（evolver）："spec 写得对不对？" — 功能定义、验收标准是否准确
- Gate 2（evolver）："计划合理吗？" — 改动范围、步骤顺序是否合适

---

## 2. 收集输入

| 参数 | 说明 |
|------|------|
| Android 代码目录 / 仓库 URL | 本地 git 仓库优先；GitHub URL 作为备选 |
| commit / 范围 / 时间窗口 | 有则进 §M1；无则 §3 决策门判断 §M2/§M3 |
| 鸿蒙项目路径 | 本地绝对路径 |
| 功能锚点（可选） | §M3 所需：中文文案 / 类名 / id |

---

## 2.5 硬性禁令（MUST NOT）

1. ❌ **不得**仅凭对话记忆判断"没有要迁移的"。只有**本轮**提取结果才是证据。
2. ❌ **不得**把"BUILD SUCCESSFUL"当作功能对齐证据。Android 新增功能若 HMOS 没实现，**不会触发编译错误**。
3. ❌ **不得**跳过 §3 决策门直接输出"已完成"。
4. ❌ **不得**用源码符号差集（类名/id/字面量）作为 UI/业务层的主扫描方法——只能用于资源层（§M2.3）。
5. ❌ **不得**在 §S2 用户对齐前直接动代码。
6. ❌ **不得**信任子代理返回的"Assumed / Estimated / likely"这类估算词。
7. ❌ **不得**仅凭"用 Android 符号名（类名/方法名/id/res 名）grep HMOS 源码返回空结果"作为某条功能进入 🔴 的唯一证据。HMOS 侧命名规范（驼峰/中文文案/@Builder/路由 url 字符串）与 Android 不一致，关键词空命中常见假阳性。必须同时附带 "HMOS 目标页面已完整阅读" + "≥3 个同义关键词（中文文案/动词同义词/图标或资源 id）全部空命中" 才可判 🔴。
8. ❌ **不得**把 override 模式理解为"跳过一切验证"。见 §S2.4：override 仅免除对话式 yes/no 确认，**机械核查（§M2.2 证据字段 + §3.5 spec 校验 + §S2.5 Pre-Edit）一项都不能省**。
9. ❌ **不得**以"截图通过 + 编译通过 + grep 通过"作为回归无退化结论。`feature_acs / page_acs / shared_files` 必须按 §S3.6 真机走完整链路验证；缺任一类的运行时证据，spec status 不许升级 done。
10. ❌ **不得**因为"该状态需要 picker 交互 / 需要前置数据 / 需要登录"等理由把 affected_visual_pages 中的任何 state_label 推给"人工验证"。先调 arkts-scenario-runner 写场景，scenario 反复 ≥3 次失败才能升级用户裁定（§S3.6.2）。
11. ❌ **不得**把视觉对比中的迁移 bug 自动归类为 "design_difference / platform_difference / dynamic_content"。归类必须满足 arkts-visual-verify §1.1.1 的三种证据之一（用户对话豁免 / OS 系统级无 API 干预 / Android 端本就动态随机），且证据必须落到 progress.json。
12. ❌ **不得**在 §M1 模式下用 commit history 推翻 final state 的代码事实。同步目标永远是用户指定 final state 的实际行为；commit 链中被后续 commit 推翻的中间态在 final state 上必然不存在，**绝对禁止**因为 commit 标题描述了它而把它放进 §S2 差异清单。final state 是事实底线，commit 仅作辅助校准（详见 §1.1.1 + §M1.3 Step 3 冲突仲裁）。
13. ❌ **不得**把 Android 端的"死代码"作为活功能进同步清单。详见 §2.6 死代码过滤原则（注释代码 / `@Deprecated` 已废弃 / `if(false)` 永不进入分支 / feature flag 关闭的代码 / `kotlin -e Always false` 编译期消除的代码均视为死代码，**不得**生成对应 HMOS spec）。

## 2.6 死代码过滤（所有扫描模式共享，必跑）

Android 项目里常有"看起来在那里但运行时不会执行"的代码。直接迁移这些 = 让 evolver 在 HMOS 端真造永不被感知的功能 = 浪费 + 污染 baseline。

**5 类死代码**（**绝对禁止**进 A_CLOSURE / 行为轨迹清单 / §S2 差异清单）：

| 类型 | 识别特征 |
|------|---------|
| 注释代码 | `//` 或 `/* */` 包裹 |
| 已废弃 | `@Deprecated` 注解或 KDoc `@deprecated` |
| 死分支 | `if (false)` / `when { false -> ... }` |
| Feature flag 关闭 | 配置中 flag 为 `false` |
| TODO 占位 | `TODO()` / `throw NotImplementedError()` / 空函数 + `// TODO` |

**HARD-GATE**：
- §M3 模式：grep 命中后**必须**剥离注释再判，**只命中注释 → A_CLOSURE 等价于空 → 走 §M3.1.1 硬闸门**
- §M1 模式：diff 中纯注释 `+/-` 行不计入"新增/下线"行为
- §M2 模式：LLM 阅读 prompt 必须显式声明忽略 5 类死代码

**边界 case**（最近 1-2 commit 被注释 + commit message 含"temporarily disable/WIP"）→ §S2 清单标 `⚠ Android 端暂时禁用，迁移待定`，由用户决定。

> 📖 详细操作（5 类完整定义 + 例 / 三模式过滤命令 / Python 剥离注释脚本 / 边界 case 判断） → **references/dead-code-filter.md**

## 3. 硬性决策门（每次启动必跑）

**只问三个问题**，按顺序命中即锁定模式：

```
问题 A：Android 端能拿到 commit 记录吗（本地 git 或 GitHub）？
  ├─ 是 → 进入 §M1 Diff 模式
  └─ 否 → 问题 B

问题 B：用户给了具体功能锚点吗（功能名 / 类名 / id / "只迁移 XX"）？
  ├─ 是 → 进入 §M3 Targeted 模式
  └─ 否 → 问题 C

问题 C：用户只提供了两份代码，让我自己找差异？
  ├─ 是 → 进入 §M2 Source-compare 模式
  └─ 否 → 主动向用户澄清：Diff / Source-compare / Targeted 哪种？
```

**输出要求**：把命中结论显式写出一行，例：
> 「决策：用户说『再检查下还有什么要迁移』→ 无 commit 无锚点 → 进入 §M2 Source-compare 模式」

没有这句话 = 视为跳过决策门 = skill 失败。

---

## 3.5 HMOS Spec 双重验证（所有模式共享）

**目的**：所有 §M1/§M2/§M3 产出"行为变化候选"时，必须做三源校验，避免误改已实现功能 + 防假阳性。

**三源**：
1. **Android 源码**（行为存在且有轨迹）→ 产出 `android_trace`
2. **HMOS spec**（功能是否已签收 / 现有 spec 是否受影响）→ 产出 `hmos_spec_status` + `existing_spec_refs`
3. **HMOS 源码反向扫描**（代码层是否已实现，防假 🔴）→ 产出 `hmos_reverse_scan`

**HARD-GATE**：三项齐全才允许进 🔴。任一缺失 → 自动降级 `confidence: low`，进"待验证桶"。

**§S2 清单每条必带字段**：
- `HMOS Spec:` ❌（未提及）/ ✅（已签收）/ ⚠（部分定义或不一致）
- `hmos_reverse_scan:` 含 ≥3 个同义关键词的命中结果（必须含中文文案 + 同义动词）

> 📖 详细操作（spec 目录扫描命令 / Step A+B 比对 / 反向扫描关键词提取规则 / 完整示例 / 三源汇总表） → **references/spec-cross-check.md**

## 4. 架构映射表（噪声过滤器，所有模式共享）

防止"误报缺失"的关键防线。**看到 Android 侧有、HMOS 侧找不到同名类时，先查映射表，不是直接报缺失**。

**三类映射**：
- **4.1 架构工具层**：Activity/Fragment/RecyclerView/ViewModel/EventBus 等 Android 独有概念在 HMOS 的 v2 等价形式（如 `@ComponentV2 struct + NavDestination` / `List + Repeat.virtualScroll` / `*PageVM extends BaseViewModel + @Trace + emitter`）
- **4.2 UI 控件层**：TextView / Button / EditText / FAB 等控件的语义同名词典
- **4.3 权限映射**：Android 权限 → OHOS 权限（**非 1:1**；加权限前必须 grep HMOS 代码确认 API 被使用，否则 ACL 卡签名）

> 📖 完整映射表（架构工具 13 项 / UI 控件 12 项 / 权限 7 项 + 每项不该做什么的反例）→ **references/arch-mapping.md**

## §M1 Final-state 优先 + commit 辅助 模式（有 git 历史）

**何时用**：用户能给出 Android 端的 git 信息（分支名 / commit 范围 / GitHub URL）。

**核心方法论**：以用户指定分支的 **final state** 为主信源（直接读源码提行为轨迹），commit history 作辅助校准证据（边界 case 暗示 + scope 划分 + revert 警告）。冲突时以 final state 为准。兼容所有 merge 形态（fast-forward / `--no-ff` / squash / rebase）。

**步骤骨架**：
1. **M1.1** 探测目标 final state（必须）+ 辅助 commit 范围（可选）
2. **M1.2** 读取 diff（辅助证据，不是主路径）
3. **M1.2.5** Final-state 残留物校验：HEAD 存在但无活引用的代码不进 §S2
4. **M1.3** 行为提取：Step 1 final state 主路径 → Step 2 commit 辅助校准 → Step 3 冲突仲裁
5. **M1.4** 查 HMOS 等价路径（§M 通用收尾）
6. **M1.5** 分桶 🔴/🟠/✅（§M 通用收尾）
7. **M1.6** 资源层差集（§M 通用收尾，见 §A 资源附录）
→ 进 §S2 用户对齐

**绝对原则**：commit history 不能推翻 final state 的代码事实——final state 是事实底线。

> 📖 详细执行（M1.1-M1.6 完整步骤 / 探测命令 / 行为提取 3 步 / 残留物校验流程 / HMOS 等价路径搜索）→ **references/mode-m1.md**

## §M2 Source-compare 模式（只有两份代码）

**何时用**：用户只给出 Android 项目 + HMOS 项目，无 commit 信息也无功能锚点；让本 skill 主动找差异。

**核心方法论**：三层并行——LLM 读源码还原 UI/行为（主扫描）+ 符号差集扫资源层 + LLM 对比数据/逻辑层。UI 层跨范式**不能用符号差集**（80% 假阳性），必须并排阅读源码以"行为轨迹"维度对齐；资源层 name-as-identity 才能符号扫描。

**步骤骨架**：
1. **M2.1** 建立页面配对（Android Activity/Fragment ↔ HMOS .ets，用 §4 架构映射表）
2. **M2.2** UI + 行为层：LLM 源码并排阅读（**主扫描**）；每条差异必带 5 证据字段（android_trace / hmos_read / hmos_synonyms / hmos_spec_status / confidence）
3. **M2.3** 数据/逻辑层：LLM 读 Repository/Store/Service 对比输入/输出/副作用
4. **M2.4** 资源层符号差集（图片 / strings.xml key / Retrofit endpoint / 权限）— **本模式唯一允许的符号扫描**
→ 进 §S2 用户对齐

**绝对原则**：UI/业务层禁止用符号差集；每条 🔴 必须含 5 证据字段，缺任一字段自动降级 `confidence: low`。

> 📖 详细执行（页面配对命令 / 三步并排阅读 / 5 字段完整定义 + yaml 样例 / 数据/逻辑对比方法 / 资源差集完整 grep）→ **references/mode-m2.md**

## §M3 Targeted 模式（用户指定功能锚点）

**何时用**：用户给出具体功能锚点（功能名 / 类名 / id / "只迁移 XX"）。

**核心方法论**：锚点 → A_CLOSURE（Android 端命中文件 + 依赖闭包）→ H_TARGETS（HMOS 端目标改动文件清单 = scope lock）→ scope-locked 实施。

**主流程分支**：
```
§M3.1 grep 关键词 → A_CLOSURE 是否为空？
  ├─ 非空 → §M3.2 H_TARGETS → §M3.3 scope-lock 实施 → §M3.4 改动审计 → §S2
  │        （回归范围派生由通用 §SR 处理，不在 §M3 内）
  └─ 空   → §M3.1.1 硬闸门，向用户三选一：
            (a) 换关键词重试 §M3.1（≤3 轮）
            (b) Android 无实现 → 委托 spec-evolver 走 V2 新功能（payload android_behavior_trace=null）
            (c) 取消同步
```

**步骤骨架**：
1. **M3.1** grep 功能定位 + A_CLOSURE 构建（含 §M3.1.1 硬闸门）
2. **M3.2** A_CLOSURE → H_TARGETS 映射（scope lock 边界）
3. **M3.3** scope-lock 实施：禁改 H_TARGETS 外文件，越界请示
4. **M3.4** 改动审计：`git diff --name-only` 对比 H_TARGETS 清单
→ 进 §S2 用户对齐 → §SR 回归范围派生 → §S2.5 Pre-Edit → §S3 委托 evolver

**绝对原则**：
- A_CLOSURE 空时**绝对不得**让 LLM 凭描述脑补 Android 实现
- H_TARGETS 是 scope lock，越界必须请示

> 📖 详细执行（grep 命令 / A_CLOSURE 输出格式 / §M3.1.1 完整硬闸门 / H_TARGETS 映射表）→ **references/mode-m3.md**

## §S2 共享：用户对齐关卡（**实施前必跑**）

三模式产出的差异清单都必须经此关卡。

### S2.1 清单格式

```
本轮同步差异清单：

【🔴 HMOS 未覆盖 / 需新建】
  1. 作品页上传 FAB + 相册多选 + 批量上传
     Android：ItemsFragment FAB → picker → POST /api/items/batch-upload
     HMOS：MainPage.Items 无上传入口
     预计改动：MainPage.ets / UserItemsStore.ets（新建）

【🟠 部分覆盖 / 需补步骤】
  2. Campaign 弹窗倒计时
     Android：新增"剩余 N 分钟"
     HMOS：已有弹窗但无倒计时
     预计改动：CampaignDialog.ets 加 timer

【✅ 已覆盖（透明度）】
  3. 退款理由弹窗 → RefundReasonDialog 已存在
  4. Works 批量删除 → isManageMode 已实现

请确认：
  (a) 全做 / 只做 🔴 / 只做 [1][2]
  (b) 有没有漏的（你改过但上面没列出）
  (c) 有没有 🔴/🟠 里其实 HMOS 已实现
```

### S2.2 用户回复前**不得开工**

- "全做" → §S3（逐条委托 evolver）
- "只做 X" → 剔除其余后进 §S3
- "漏了 Y" → 回对应模式补提取
- "HMOS 其实有 Z" → 验证位置后剔除

**禁止**自行推断"用户应该选全部"。

### S2.3 告知用户后续流程

在清单末尾附加说明，让用户理解 §S2 只是第一关：

```
📌 说明：本关卡确认"我找到的差异对不对"。确认后，每条差异会委托 arkts-spec-evolver
   走 create→plan→execute→verify 全流程，在 Gate 1（spec 审批）和 Gate 2（plan 审批）
   两处还会再次暂停等你确认，方便你逐条监督。
```

### S2.4 Override 模式（用户显式授权"跳过确认"时的规则）

当用户说"跳过所有确认 / 一直跑到底 / 不要问我 / override" 等授权语时：

| 可以跳过 | **不能跳过** |
|---|---|
| §S2.1 的 yes/no 对话式确认 | §M2.2.x 五个证据字段完整性（缺字段 → 仍然不能进 🔴） |
| evolver Gate 1 / Gate 2 的用户审批 | §3.5 三源校验（spec A+B 步 + §3.5.5 代码反向扫描） |
| 多条差异的分组/合并决策对话 | §S2.5 Pre-Edit 机械核查（见下） |
| §S2.2 的"有没有漏的 / 其实已实现的"补充问询 | 改动后的 `git diff` 自审（防越界误改） |

**硬性要求**：
- override 模式下主代理必须在 §S2 清单末尾显式声明：
  > "已收到 override 授权，跳过对话式确认；§M2.2.x 证据字段 + §3.5 三源校验 + §S2.5 Pre-Edit 机械核查仍会逐条跑。"
- 缺此声明 = 视为跳过了本应保留的机械核查 = skill 失败
- 执行期间若 §S2.5 对某条差异判"待人工复核"，override 不能将该条强行进入实施 —— 该条必须回 §S2 清单并暂停等用户单独裁定

---

## §SR 原有功能回归保护（**所有模式共享，必跑**）

§S2 确认 + §S2.5 Pre-Edit 之前，对**每一条**要实施的差异跑回归范围派生。**三模式（§M1/§M2/§M3）共用本节**，不再嵌在任何单一模式里。

### SR.0 三层防护时点

```
改前左移              改中自动              改后兜底
SR.1 派生清单 A        evolver Step 11a/11b   §S3.6 真机回归
expected_files 7 维    dt-verifier filter    feature_acs 主链路
grep + LLM 补全        + 采样 + visual       page_acs / shared_files
   ↓                       ↓                     happy path
SR.2 改完审查清单 B
实际 diff 7 维 grep
   ↓
SR.3 R = A ∪ B  → 写入 spec `## 回归范围`，作为 evolver Step 11 + §S3.6 的回归依据
```

### SR.1 改前派生：清单 A（左移）

**输入**：差异条目的 `expected_files`（§M1/§M2/§M3 都有该字段；§M3 即 H_TARGETS 等价）。

**四步骨架**：
1. **7 维 grep 派生**：(a) 文件 / (b) struct / (c) 共享方法 / (d) AC ID 提取 / (e) 事件层（EventBus/emitter）/ (f) 状态层（v1+v2 并集：`@(Provide\|Consume\|Provider\|Consumer\|StorageLink\|StorageProp)` + `AppStorage(V2)?` key）/ (g) 路由层（`RouterUtils.(push\|replace)PathByName\|pushPath\|pushUrl`，前者 v2 主线，后两者识别 legacy）
2. **LLM 语义补全**（必跑，零人工兜底盲区）：读 baseline AC 全集 + 改动 diff + `spec/features/regression-miss-patterns.md` 漏报模式知识库，补 grep 没命中但描述匹配的 AC
3. **爆炸阈值校验**（>10 触发）：向用户三选一 (a) 全量回归 / (b) 拆分 spec / (c) opt-out 手挑
4. **清单 A** 含 feature_acs / page_acs / shared_files / affected_visual_pages / rationale 五字段

### SR.2 改后审查：清单 B（事实校准）

**触发时机**：evolver execute 阶段写完代码后、verify 之前。incremental-migration 重新介入。

**输入**：实际改动文件 + 实际改动 diff
```bash
cd {hmos_project}
git diff --name-only > /tmp/actual_files.txt
git diff > /tmp/actual_diff.patch
```

**做什么**：用清单 A 同样的 4 步规则**重跑一遍**（7 维 grep + LLM 语义补全 + 爆炸阈值），但输入换成"实际改动文件 + 实际 diff"。

**为什么需要**：清单 A 是**预测**（基于 expected_files），实际写代码时可能：
- 多碰了 expected_files 之外的共享方法（即使 §S2.5 自审通过，但跨方法调用链有可能仍引入新依赖）
- 实际改了某个 EventBus 事件或 @Provider/@Consumer key（§SR.1 派生时这些事件/key 还没存在，无从 grep）
- LLM 实际生成的代码命中了 §SR.1 没预见的 baseline AC

**清单 B** 是基于事实的回归范围，含与 A 同样五字段。

### SR.3 取并集：最终回归清单 R = A ∪ B

```
R.feature_acs = A.feature_acs ∪ B.feature_acs
R.page_acs = A.page_acs ∪ B.page_acs
R.shared_files = A.shared_files ∪ B.shared_files
R.affected_visual_pages = A.affected_visual_pages ∪ B.affected_visual_pages
R.explosion = A.explosion OR B.explosion
R.derivation_provenance = {A_count, B_count, only_in_A_count, only_in_B_count, A∩B_count}
```

**`only_in_B_count > 0` 是关键信号**——说明改前预测有遗漏。本次仍跑（取并集兜住），同时把"漏报模式"自动追加到 `spec/features/regression-miss-patterns.md`，下次 §SR.1 LLM 语义补全读到时能避免同类漏。

**写入 spec 的 `## 回归范围`**：用 R 覆盖 §SR.1 写过的 A 版本，并在 rationale 里标注 "B 覆盖了 only_in_B={...} 条，已写入 regression-miss-patterns.md 漏报模式 #N"。

### SR.4 传 R 给 evolver Step 11 + §S3.6（已有）

更新后的 `## 回归范围` 栏目作为 evolver Step 11a/11b 自动回归的输入，并作为 §S3.6 真机兜底回归的依据。

### HARD-GATE

- 任一模式（§M1/§M2/§M3）跳过 §SR = skill 失败
- §SR.2 改后审查未跑（仅靠 §SR.1 预测就委托 evolver Step 11）= skill 失败
- `regression_scope.derivation_provenance` 字段缺失 = skill 失败（用户无法审计 A/B 各贡献多少）
- `only_in_B_count > 0` 时未追加漏报模式到知识库 = skill 失败

> 📖 详细操作（7 维 grep 完整命令 / LLM 语义补全 prompt / `## 回归范围` 栏目模板 / opt-out 格式 / 漏报模式知识库）→ **references/regression-scope-derivation.md**

---

## §S2.5 Pre-Edit 机械核查关卡（动代码前必跑）

§S2 用户确认差异清单后、任何 `Edit/Write` 动作前，对**每一条**实施差异跑四步机械核查。**任一步失败 → 该条不得实施**，降级为"待人工复核"回 §S2 清单末尾。

**四步**：
1. **目标文件完整阅读**（主代理亲自用 `Read`，禁止 grep 代替）
2. **Spec 反查**（执行期复用 §3.5 Step B，`existing_spec_refs` 非空时主代理读对应 spec 判断不破坏已签收条目）
3. **同义词扫描**（复跑 §M2.2.x 的 `hmos_synonyms` 关键词，全 0 命中才允许继续）
4. **改动后 git diff 自审**（实际改动必须是 `expected_files` 子集；越界立即停下报告）

**执行期日志**：每条差异完成后写一行到 `spec/incremental-migration-{date}/exec-log.md`：
```
[{timestamp}] diff #{n} "{title}"
  target_files_read: [...]  existing_spec_refs: [...]  reverse_scan_hits: 0
  scope_audit: PASS | EXTRA: [...]  result: IMPLEMENTED | DEFERRED(reason) | ROLLED_BACK(reason)
```

§S4 完成摘要必须汇总本 log，让用户能逐条看到每条差异的机械核查轨迹。

> 📖 详细操作（四步完整执行规则 / 越界报告模板 / 同义词复跑细则） → **references/pre-edit-checklist.md**

## §S3 委托 arkts-spec-evolver 执行全流程

§S2 用户确认差异清单后，**本 skill 不自己实施**。逐条差异委托给 `arkts-spec-evolver` 的 `create+plan+execute+verify` 模式，由其接管 spec 生成 → 计划 → 写代码 → 验证，并在 Gate 1 / Gate 2 两处自动暂停等待用户审批。

### S3.1 差异条目 → evolver 输入格式

本 skill 要把 §S2 里确认的每条差异整理成 evolver 能直接消费的 payload。每条包含：

| 字段 | 来源 | 说明 |
|------|------|------|
| `title` | 差异条目标题 | 例："作品页批量上传" |
| `android_behavior_trace` | §M1.3 / §M2.2 提取的行为轨迹 | "FAB.click → PhotoViewPicker → POST /api/items/batch-upload → 列表刷新" |
| `hmos_current_state` | §M1.4 / §M2.2 查路径结论 | "MainPage.Items 无上传入口，services/ 无对应接口" |
| `expected_files` | §M1 / §M3 映射结果 | `MainPage.ets` / `UserItemsStore.ets`（新建） |
| `resources` | §M1.6 / §M2.4 资源差集 | 新增图片/string key/权限清单 |
| `acceptance_criteria` | LLM 从行为轨迹反推 | "点 FAB 弹相册 → 多选 → 上传进度 → 列表出现新项" |
| `android_source_refs` | 原始文件路径 + 行号 | `ItemsFragment.kt:L120-L180` |
| `hmos_source_refs` | HMOS 侧锚点文件 | `MainPage.ets` / `UserItemsStore.ets` |
| `hmos_spec_status` | §3.5 交叉比对结论 | ❌ 未提及 / ✅ 已签收 / ⚠ 部分定义 / ⚠ spec 与代码不一致 |
| `existing_spec_refs` | §3.5 Step B 反查结果 | `spec/baseline/features/F-works-list.md` 等将与改动共存的 spec，供 evolver Gate 1 审批时防误改 |
| `regression_scope` | §SR 派生（清单 R = A ∪ B）| `{feature_acs:[...], page_acs:[...], shared_files:[...], affected_visual_pages:[...], explosion, opt_out_reason, derivation_provenance: {A_count, B_count, only_in_A_count, only_in_B_count}}` — evolver Verify Step 11 直接消费，**不可省略**。§S3 第一次委托时只含 A（execute 前）；evolver execute 完成后回到本 skill 跑 §SR.2 重派生 B，更新 spec `## 回归范围` 为 R，evolver Step 11 用 R 跑 |

### S3.2 委托调用

**每条差异独立调用一次**（不要把多个差异打包成一个 evolver 任务；evolver 的 Gate 审批以 spec 为单位，单功能粒度才能让用户精细审查）：

```
调用 Skill: arkts-spec-evolver
模式: create+plan+execute+verify
输入:
  title: {S3.1 的 title}
  context: |
    本任务由 a2h-incremental-migration 委托，来源：
      - 迁移模式：§M1 Diff / §M2 Source-compare / §M3 Targeted
      - 差异清单条目：{编号}
    Android 行为轨迹：{android_behavior_trace}
    HMOS 现状：{hmos_current_state}
    预期改动文件：{expected_files}
    资源依赖：{resources}
    验收标准：{acceptance_criteria}
    Android 源锚点：{android_source_refs}
    HMOS 源锚点：{hmos_source_refs}
    回归范围 (§SR 派生)：
      **首次委托时仅含清单 A**（改前预测）：
        feature_acs / page_acs / shared_files / affected_visual_pages / explosion / opt_out_reason
        derivation_provenance: { A_count: N, B_count: 0 }   # 此时 B 还没产出
```

**关键交互**：evolver execute 完成后必须**回到本 skill** 跑 §SR.2 改后审查产出清单 B，更新 spec 的 `## 回归范围` 为 R = A ∪ B，再让 evolver 继续 Step 11。委托时必须显式约定该 callback 点，不能让 evolver 在 execute 完了直接进 Step 11（那只回归 A，漏掉 only_in_B）。

### S3.3 Gate 审批流转

evolver 进入以下节点时会暂停，用户审批后继续：

```
create 阶段 → 生成 spec/features/F-xxx-{title}.md
  │
  ▼
★ Gate 1：展示 spec 摘要 → 等待用户确认
  - "确认" → 进入 plan
  - "修改 XX" → evolver 按要求改 spec，再次 Gate 1
  - "终止" → 保留 spec，停止流程
  │
  ▼
plan 阶段 → 生成实现计划
  │
  ▼
★ Gate 2：展示 plan 摘要 → 等待用户确认
  - "确认" → 进入 execute
  - "修改 XX" → evolver 调整 plan，再次 Gate 2
  - "终止" → 保留 plan，停止流程
  │
  ▼
execute → 写代码（evolver 按需调用 arkts-component-builder / arkts-data-layer /
         arkts-navigation-builder / arkts-system-capabilities / android2hmos-resources-convert 等 domain skill）
  │
  ▼
verify → 按 spec 验收标准验证 + 编译闭环
```

**本 skill 在 evolver 执行期间不得介入**。Gate 审批由用户与 evolver 直接交互；本 skill 只在所有差异条目走完后汇总。

### S3.4 多条差异的调度策略

§S2 确认清单里通常有 N 条差异（🔴 + 🟠）。调度建议：

- **顺序执行**：一条走完 create→plan→execute→verify 再起下一条。优点是用户注意力集中在一个功能上，审批质量高；缺点是慢。默认选此方案。
- **按依赖分组**：若两条差异共享基础类（例："批量上传"和"批量删除"都依赖 UserItemsStore 的新建），把它们合并为一条 spec，减少 Gate 重复。合并与否由本 skill 在 §S3.1 汇总 payload 时提议给用户决定。
- **禁止**：把所有差异打包一次性委托给 evolver——会让 Gate 审批粒度失控。

### S3.5 资源/权限的特殊处理

纯资源层变更（新增图片 / string key / 权限）若独立存在且不伴随业务逻辑，evolver 的 create→plan→execute→verify 会显得过重。本 skill 可**直接处理**后，在 evolver 的 spec 里仅作为"前置资源"声明，不走完整 4 步：

- 图片文件：按 §A 资源迁移附录直接落地到 `resources/base/media/`
- string key：直接写入 `resources/base/element/string.json`
- 权限：查 §4.3 映射后写入 `module.json5`

但如果资源变更是某个业务功能的一部分（例：批量上传功能附带的 `icon_upload_work.png`），**不要单独处理**，并入对应业务差异的 evolver 调用。

---

## §S3.6 运行时回归（evolver verify 通过后必跑，不可绕过）

**核心立场**：evolver Verify 三层验证（编译只看语法 + dt-verifier 只看断言 + 视觉只看 UI 截面）**不等于完整回归**。下游真实业务流必须由本 skill 在 evolver 收尾后再跑一道。

**必跑三类回归**（针对每条 evolver 已 done 的 spec）：
- **A. feature_acs 主链路烟雾** — 读 baseline 找用户操作步骤，真机走完整链路，关键节点截图存档
- **B. page_acs UI 交互回归** — 真机点到入口 + 截图前后两态 + multimodal 对比副作用（toast/nav/数据更新）
- **C. shared_files 被改函数 happy path** — 每个修改过的方法（不只是新增）找真实调用方驱动一次

**证据落盘**：所有命令 stdout / 截图 / hilog 写到 `spec/incremental-migration-{date}/runtime-regression-log.md`。

**升级 done 的 HARD-GATE**（同时满足）：
- 编译 PASS（hmos-fix-build-errors stdout）
- 静态 grep AC 全部命中
- feature_acs / page_acs / shared_files / affected_visual_pages 各自全部 PASS 或 user_waived
- 任一缺失 → 维持 `verifying(*-pending)`，**禁止**升级 done

**§S4 完成摘要必带字段**：`runtime_regression_log` 路径 + 上述四类的 pass/fail/pending 数量统计；任一 fail/pending 非 0 → 摘要顶部 ⚠️ 醒目标记。

> 📖 详细操作（A/B/C 三类的具体步骤 / runtime-regression-log.md 执行模板 / visual-verify 完整覆盖规则 / 真实漏检反例） → **references/runtime-regression.md**

## §S4 完成摘要

所有差异条目走完 evolver 流程后汇总：

```
✅ 增量同步完成

识别阶段：
  模式：§M1 Diff / §M2 Source-compare / §M3 Targeted
  范围：{commit 范围 / 页面清单 / 功能锚点}
  §S2 用户确认的差异条目数：N

委托 arkts-spec-evolver 执行：
  [1] {title-1}
      - spec：spec/features/F-xxx-{title-1}.md
      - Gate 1 审批：{通过 / 迭代 N 次后通过}
      - Gate 2 审批：{通过 / 迭代 N 次后通过}
      - verify：✅ 通过 / ❌ 失败（{原因}）
  [2] {title-2}
      - ...
  ...

独立处理的资源变更（§S3.5）：N 个
  - 图片：{列表}
  - 字符串 key：{列表}
  - 权限：{列表}

整体状态（§S3.6 强制必填，缺字段视为偷懒）：
  - 编译：✅ 通过（evolver verify 阶段已做编译闭环）
  - 运行时回归 log：spec/incremental-migration-{date}/runtime-regression-log.md
  - feature_acs runtime: pass=X, fail=Y, pending=Z
  - page_acs runtime: pass=X, fail=Y, pending=Z
  - shared_files happy path: pass=X, fail=Y, pending=Z
  - visual-verify state_labels: pass=X, fail=Y, waived=Z（waived 必须附用户原话引文）
  - spec 留档：spec/features/F-xxx-*.md 共 N 份，可供后续审计/回溯
  - 未完成条目：N（原因：用户在 Gate 处终止 / verify 失败 / runtime regression 失败 / ...）

⚠️ 任一 fail / pending 非 0 → 摘要顶部必须放显眼警告块，列出每条的具体阻塞点 + 下一步动作；
   禁止用"整体已完成，仅 X 条待补"等模糊措辞掩盖未通过项。

后续建议：
  - 若有未完成条目，列出每条的下一步动作
  - 可调 a2h-retrospect 做本轮回顾
```

---

## §A 资源迁移附录

资源层（图片 / 字符串 / 字体 / 权限）的迁移规则：

- **图片**：PNG/JPG/WebP 直接复制到 `resources/base/media/`；`.9.png` 去 `.9`；XML vector → SVG；Lottie/字体放 `resources/base/rawfile/`
- **字符串**：`res/values/strings.xml` → `resources/base/element/string.json`；`values-zh/` → `resources/zh_CN/element/`
- **命名**：保持 Android 原名去密度后缀；HMOS 已有不同名引用同一图标 → 以 HMOS 侧命名为准

**子代理输出约束**（委托 Explore / general-purpose 时）：每条命令 stdout 原文必须 code fence；看到 `Assumed/Estimated/likely` 等估算词 → 打回；真跑失败必须 `SKIPPED(原因)` 不能编数字；返回 >500 行可落盘 /tmp/，但主代理必须亲自 Read 关键章节验证。

> 📖 完整规则（图片格式转换详表 + XML vector → SVG 字段映射 + GitHub 下载二进制命令）→ **references/resource-migration.md**
