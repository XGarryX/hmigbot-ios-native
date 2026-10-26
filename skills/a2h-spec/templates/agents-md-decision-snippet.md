<!-- when: a2h-spec Step C4.8b 同步项目根 AGENTS.md（ledger 首次生成后 / 模板规则演进重跑）时加载 -->
<!-- topics: AGENTS.md 同步, decision-ledger, 三道闸·闸3, 标题锚定, idempotent 同步, 条件段, Karpathy 通用准则 -->

# 项目 AGENTS.md 模板（决策触发段 + Karpathy 通用准则）

> 三道闸协同的第 3 闸（项目级行为约束）。
> 由 **a2h-spec Step C4.8b** 在 ledger 首次生成时自动 idempotent 同步到项目根 `AGENTS.md`。
>
> 业界对照：行业共识 AGENTS.md ~80% 可靠（advisory）；100% deterministic 需要 hooks（暂未实现，留作 future enhancement）。

---

## 模板（最多三个标题锚定段，由 a2h-spec 自动同步）

模板包含两段固定内容 + 一段条件内容，各以**固定 H2 标题为锚**（不使用任何 HTML 注释 marker），**独立同步**：

1. **决策触发段**（锚标题《决策来源与禁止交互（HARD-GATE）》，**始终同步**） — 迁移特定规则，HARD-GATE 级
2. **HarmonyOS 知识查询优先级段**（锚标题《HarmonyOS 知识查询优先级》，**条件同步**） — 当 `harmonyos-development` skill 在当前配置中可用时（Glob `**/harmonyos-development/SKILL.md` 命中）才写入；skill 不可用时**不写入**，已存在时**移除**
3. **通用行为准则**（锚标题《通用行为准则》，**始终同步**） — 迁移友好版 Karpathy（删 #1 Think Before Coding + #4 Goal-Driven Execution，保留 #2 Simplicity / #3 Surgical 并加迁移化 caveat）

放在新 AGENTS.md 中的**完整顺序**：决策段在前（项目特定、优先级高） → harmonyos-dev-skill 段（如有） → 通用基线在后。

### 完整模板内容

````markdown
## 决策来源与禁止交互（HARD-GATE）

唯一事实源：@spec/decision-ledger.md。快速定位用其顶部「决策索引」段（D-编号一行结论速查）；**涉及某类目时按类目 / D-编号 grep 取完整决策正文**（背景/候选/依据/影响/运行期验证项），无需通读全文。

凡涉及以下**迁移决策类目（C0–C17）**判断，先 grep ledger 对应类目，再做任何操作：
- 范围取舍（页面/功能要不要做、是否本轮）
- 技术替代方案（平台无对等能力、SDK 留桩/降级/砍）
- UX 行为差异（系统组件 vs 应用内、后台行为、降级兜底）
- 工程配置（签名/entitlement/密钥策略）

执行规则：
- ledger 命中 → 按之执行，不再询问用户
- ledger 未命中 → fail-fast，把缺口写入 @spec/migration-report.md 的「决策缺口」段，
  禁止交互式追问；由下一轮 grill 补齐
- 与其他文档（旧报告 / AGENTS.md 旧描述）冲突时，ledger 优先

> **适用范围**：迁移决策类目 C0–C17。普通代码实现层面的不清晰按下方通用准则处理。

## HarmonyOS 知识查询优先级

迁移过程中遇到任何 **HarmonyOS 知识不确定**（API / SDK / 组件 / 最佳实践 / FAQ）时，**优先以 Skill 工具调用 `harmonyos-development`** 查本地最佳实践 + FAQ 路由：

- **适用域**：相机开发 / 图片处理 / ArkUI 开发（布局 / 组件 / 导航 / 手势 / 动画 / 对话框 / Tabs / 列表 / 文本输入 / 窗口 / UI 故障排查）
- **调用方式**：`$harmonyos-development`
- **降级路径**：skill 未命中或域外问题 → `grill-with-docs` 或 WebFetch / WebSearch 查公开文档
- **生效范围**：spec 阶段类目核验 / plan 阶段技术决策 / execute 阶段代码实现 全程优先

> 本段为**条件段**：仅当 a2h-spec Step C4.8b 检测到 `harmonyos-development` skill 在当前配置中可用时同步；若 skill 后续被移除，下次同步将自动删除本段。

## 通用行为准则

降低常见 LLM 编码错误的行为准则。**取舍**：偏向谨慎而非速度；琐碎任务用判断力。

### 1. 极简优先

**只写解决问题所需的最少代码，不要任何揣测性扩展。**

- 不写超出需求的功能
- 不为单次使用的代码做抽象
- 不引入未被要求的"灵活性"或"可配置性"
- 不为不可能发生的场景做错误处理
- 写了 200 行能用 50 行的，重写

> **迁移场景例外**：与 spec / iOS 源一致优先于代码量；**不主动 simplify 已 spec 出来的内容**。忠实复刻（C12 类目）的决议优先于本原则——iOS 原版 200 行的 8 tab 页面在 spec 里就是 8 tab，不要"优化"成 3 tab。

自检："高级工程师会觉得这过度复杂吗？"——如是，简化。

### 2. 外科手术式改动

**只动你必须动的；只清理你自己造成的混乱。**

编辑已有代码时：
- 不要"顺手优化"相邻代码、注释或格式
- 不要重构没坏的东西
- **优先 match HarmonyOS / ArkTS 最佳实践**，不要 match iOS 风格、也不要 match 偶然的早期 ArkTS 产物风格——pipeline 生成代码以最佳实践为准
- 若发现无关的死代码，提及它，不要删除

当你的改动产生孤儿（orphans）时：
- 移除**你的改动**导致变得未使用的 import / 变量 / 函数
- 不要删除既有的死代码，除非被要求

**自检**：每一行被改的代码都应能直接追溯到 **plan / ledger / spec / 当前 task**——迁移场景下"用户的请求"通常只是"执行"，真正的事实源是 plan + ledger，不要尝试追溯到用户对话中某一句话。

### 3. 暴露矛盾，不取折中

代码库中两种模式相互矛盾时，**选其一**（更新的 / 更经验证的），说明选择理由，把另一个标记待清理。

**不要把矛盾的模式糅在一起取折中**——和稀泥不是解法，等于又造出第三种与前两种都冲突的模式。

### 4. 先读后写

添加代码前，先读：**exports / 直接调用方 / 共享工具**。

"看起来正交"是危险信号——你以为不相关的东西，常常其实有关联。如果不确定代码为何这样组织，**先弄清楚**（查代码 / 读注释 / 看测试）**再动手**。

### 5. 每个关键步骤后设检查点

每完成一个有意义的步骤，**先总结**再继续：做了什么 / 已验证什么 / 还剩什么。

**不要从一个你自己说不清楚的状态继续推进**。如果失去线索，停下来**重新陈述**当前状态，再决定下一步。

### 6. 遵循代码库既有约定

即使你不同意，也要**遵循代码库的约定**。代码库内部的规范性高于个人喜好。

### 7. 失败要响亮（Fail Loud）

- 如果有任何东西被**静默跳过**，标注"已完成"就是**错的**

---

**这套准则在以下指标改善时表明它在起作用**：diff 中无关改动减少、因过度复杂而重写的次数减少、静默跳过的"完成"声明被显式失败取代。

> **适用范围**：通用代码实现层面（编码风格 / 修改纪律 / 矛盾处理 / 状态自检 / 失败暴露）。
> 迁移决策类目（C0–C17，含范围 / SDK 选型 / UX 退化 / 签名密钥 / 忠实度等）由上方决策段优先约束，按 ledger 走、不询问。
> 成功标准（编译 PASS / visual-verify PASS / ledger 合规）由 a2h-execute / a2h-verify skill HARD-GATE 内置，AGENTS.md 不重复。

> 《决策来源与禁止交互（HARD-GATE）》《HarmonyOS 知识查询优先级》（如存在）《通用行为准则》三个标题段由 a2h-spec Step C4.8b 自动同步：**请勿重命名这三个标题、勿手工编辑段内内容**；规则演进请回到 a2h-spec 修改模板后重跑。
````

### 关键设计点

| 设计点 | 说明 |
|--------|------|
| 三个标题锚定段（独立同步） | 决策段 / harmonyos-dev-skill 段 / Karpathy 段可独立更新，互不污染；**锚 = 精确 H2 标题行，AGENTS.md 中无任何机器注释** |
| 决策段在前 | 项目特定、HARD-GATE 级，优先于通用基线 |
| 显式读取指令 | Codex 的 AGENTS.md 无 `@` 前缀 import 自动加载机制，靠**写明「会话开始必须先读取」的动作指令**保证 ledger 被加载（比单纯路径提及可靠性显著提高） |
| 适用范围互斥说明 | 决策段管 C0–C17（"不问"），通用基线管代码量/边界/风格三类，两者职责正交不冲突 |
| 受管标题段之外永不动 | Fitness 项目根 106 行手工 AGENTS.md 完整保留 |

---

## Idempotent 同步算法（a2h-spec Step C4.8b 实现）

```
SECTION 定义（全算法通用）:
  受管段(heading) = 从「该精确 H2 标题行」起，至「下一个 H2/H1 标题行」或 EOF 止（含首尾间全部内容）。
  三个锚标题（常量，逐字匹配）:
    H_DECISION  = "## 决策来源与禁止交互（HARD-GATE）"
    H_HMOSDEV   = "## HarmonyOS 知识查询优先级"
    H_KARPATHY  = "## 通用行为准则"

INPUT:
  - PROJECT_ROOT                      项目根目录（含 spec/decision-ledger.md 的目录）
  - SNIPPET_BODY_DECISION             本文件「模板」节中 H_DECISION 标题段整段（含标题行）
  - SNIPPET_BODY_HARMONYOS_DEV        本文件「模板」节中 H_HMOSDEV 标题段整段（含标题行）
  - SNIPPET_BODY_KARPATHY             本文件「模板」节中 H_KARPATHY 标题段整段（含标题行，含段尾"请勿重命名"提示）

PRE-CHECK:
  HMOS_DEV_SKILL_AVAILABLE = (Glob "**/harmonyos-development/SKILL.md" 命中非空)
  # 即在当前可访问的 skill 路径下能找到 harmonyos-development/SKILL.md
  # 涵盖：project/.agents/skills/、~/.agents/skills/、各 plugin 目录、本仓 arkts-skills/skills/ 等

PROCEDURE:
  CLAUDE_MD = $PROJECT_ROOT/AGENTS.md

  IF !exists(CLAUDE_MD):
    # 项目尚无 AGENTS.md（如 baseline 模式）→ 创建最小骨架
    # 重要：intro 必须全中文；仅路径、项目名、文件名等保留原始字符串
    # **严禁**模型自行用英文描述项目背景（错误示范："iOS→HarmonyOS migration workspace for ..."）
    BODY_HARMONYOS = SNIPPET_BODY_HARMONYOS_DEV if HMOS_DEV_SKILL_AVAILABLE else ""
    write(CLAUDE_MD, f"""
      # {项目名}

      > iOS → HarmonyOS 迁移工作区：{项目名}。
      > 源项目：{source_path_path}{tech_stack_chinese_note}。
      > Spec baseline 在 `spec/baseline/`；项目决策历史在 @spec/decision-ledger.md。

      {SNIPPET_BODY_DECISION}

      {BODY_HARMONYOS}

      {SNIPPET_BODY_KARPATHY}
    """)  # 注意：BODY_HARMONYOS 为空时连同前后空行一并省略，避免连续空行
    RETURN created

  # 占位符填充规则：
  #   {source_path_path}       = a2h-spec Step 3.0 记录的 $SOURCE_ROOT（原始路径，不翻译）
  #   {tech_stack_chinese_note}   = 可选，技术栈中文简述：
  #                                  - "（传统 View 体系，含 XML 布局）"
  #                                  自动探测；无法探测时留空字符串

  content = read(CLAUDE_MD)
  original = content

  # ---- 处理决策段（始终同步）----
  IF content 含标题行 H_DECISION:
    content = replace_section(content, heading=H_DECISION, body=SNIPPET_BODY_DECISION)
  ELSE:
    content = content + "\n\n" + SNIPPET_BODY_DECISION

  # ---- 处理 HarmonyOS 知识查询优先级段（条件同步）----
  IF HMOS_DEV_SKILL_AVAILABLE:
    # skill 可用 → 确保段落存在且为最新
    IF content 含标题行 H_HMOSDEV:
      content = replace_section(content, heading=H_HMOSDEV, body=SNIPPET_BODY_HARMONYOS_DEV)
    ELSE:
      # 段落缺失 → 插入到决策段之后、Karpathy 段之前（保持顺序）
      content = insert_after_section(content, after_heading=H_DECISION,
        body="\n\n" + SNIPPET_BODY_HARMONYOS_DEV)
      # 如果 H_KARPATHY 段还不存在，则上一行的 insert 退化为 append
  ELSE:
    # skill 不可用 → 若段落存在则移除（idempotent 反映当前状态）
    IF content 含标题行 H_HMOSDEV:
      content = remove_section(content, heading=H_HMOSDEV)  # 整段（含标题行）删除
      # 移除后规整连续空行（避免留下 \n\n\n\n）
    # ELSE: 段落不存在 → 不动

  # ---- 处理 Karpathy 段（始终同步）----
  IF content 含标题行 H_KARPATHY:
    content = replace_section(content, heading=H_KARPATHY, body=SNIPPET_BODY_KARPATHY)
  ELSE:
    content = content + "\n\n" + SNIPPET_BODY_KARPATHY

  IF content == original:
    RETURN unchanged

  write(CLAUDE_MD, content)
  RETURN updated（命中至少一个标题段） / appended（全部新追加）
```

### 关键不变式

| 不变式 | 保证 |
|--------|------|
| 不破坏既有 AGENTS.md 三个受管标题段**之外**的内容 | replace_section 仅改各自标题段之间 |
| 多个标题段独立同步 | 决策段 / harmonyos-dev-skill 段 / Karpathy 段三者互不影响 |
| 没有锚标题时只追加，不覆盖 | else 分支只 append |
| 反复跑结果一致 | idempotent：第二次跑命中标题走 replace，content 不变则 unchanged |
| 用户手工编辑受管段之外的项目说明 | 永远不会被覆盖 |
| 用户手工编辑受管标题段**之内** | 下次同步会被覆盖（Karpathy 段尾已明确警告"请勿手工编辑"） |
| skill 状态变化（harmonyos-development 安装 / 卸载） | 下次同步自动追加 / 移除《HarmonyOS 知识查询优先级》段 |

---

## 使用约定

| 时机 | 动作 |
|------|------|
| spec/decision-ledger.md 首次生成（a2h-spec Step C4.8 末尾） | 自动跑同步算法，结果 = created / appended |
| ledger 内容变更（新增 D 编号决策） | **不动 AGENTS.md**（AGENTS.md 装规则不装内容，决策内容只在 ledger） |
| 决策段规则演进（罕见） | 改本文件「模板」节决策段 → 重跑 a2h-spec Step C4.8 → 同步算法走 updated 分支 |
| Karpathy 基线演进（极罕见） | 改本文件「模板」节 Karpathy 段 → 重跑 a2h-spec Step C4.8 → 同步算法走 updated 分支 |

---

## 与 a2h-execute SKILL.md HARD-GATE 的关系

- a2h-execute SKILL.md §1.1 内的 HARD-GATE 是**闸 1**（流程权威，skill 加载即生效）
- 项目 AGENTS.md 的决策段是**闸 3**（项目级 always-on，兜底绕过 pipeline 的入口）
- 两者措辞核心一致，覆盖场景不同：

| 场景 | 闸 1（skill HARD-GATE） | 闸 3（AGENTS.md 决策段） |
|------|------------------------|---------------------|
| 用户跑 a2h-execute | ✓ 生效 | ✓ 生效（冗余但无害） |
| 用户绕过 pipeline 直接喊"把 X 改一下" | ✗ skill 未加载 | ✓ 生效（关键兜底） |
| 长 context 中模型"想不起来查" | 部分（skill 在 context 头） | 部分（AGENTS.md 在 context 头，提醒频次更高） |

业界共识：**两者均为 ~80% advisory**。100% deterministic 需要 hooks（PreToolUse 拦截 AskUserQuestion + grep ledger 校验），属 future enhancement，当前未实现。

---

## 反模式

❌ 把 ledger 决策内容**复制**进 AGENTS.md
- 理由：AGENTS.md / ledger 漂移高发（Fitness 已实证）
- 正确：AGENTS.md 只放规则指针 → ledger，ledger 是唯一内容源

❌ 用 AGENTS.md 提示替代 a2h-execute SKILL.md HARD-GATE
- 理由：AGENTS.md 是软提示，skill HARD-GATE 才是强制规则
- 正确：两层都要有，互为兜底

❌ 在决策段里写"如有疑问请询问用户"
- 理由：直接违背"禁止交互式追问"的核心约束
- 正确：未命中即 fail-fast 写「决策缺口」段，由下一轮 grill 补齐

❌ 重命名三个受管段标题（《决策来源与禁止交互（HARD-GATE）》《HarmonyOS 知识查询优先级》《通用行为准则》）
- 理由：标题是 idempotent 同步的唯一锚点，改名后下次同步识别不到 → 追加重复段
- 正确：标题逐字保留；如需改名，先改本模板锚常量再重跑同步

❌ 在 AGENTS.md 用普通路径写法 `spec/decision-ledger.md`（不带 @）
- 理由：模型只看到路径文本，不会自动加载文件，可靠性降为单纯文本提及
- 正确：用 `@spec/decision-ledger.md`，触发 Codex 渐进披露机制按需加载
