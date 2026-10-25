---
name: commit
description: ArkTS 迁移/修复工作的 git commit 生成器，强制 7 字段结构化 commit message（大类/问题分类/Skill/工具/Spec参考/修复方式/Summary）。即使用户只说"提交"、"commit"、"帮我记录下这次修改"，也应触发。
metadata:
  type: tool
  domain: engineering
  tags:
  - tool
  - git
  - commit
  - migration
---
# a2h-commit

## 1. 定位

ArkTS 迁移与 TDD 修复流水线的**变更记录层**。每次 commit 都按固定 schema 记录关键元数据，让 `git log` 可被 a2h-retrospect 机器解析。

**核心原则**：信息从当前会话上下文中提取，不要追问用户；用户只需确认/调整，不需从零填写。

---

## 2. 触发场景

- 用户说"commit"、"提交"、"记录这次修改"、"保存这次改动"
- ArkTS 转译/修复工作完成一个阶段后（编译通过、DT 测试转绿、功能新增完成）
- a2h-execute / arkts-dt-autofix / a2h-verify 执行完毕后用户要求存档

---

## 3. Commit Message Schema（7 字段）

```
<大类>: <Summary>

Category: <新加功能|bug fix|verify|DT测试|编译错误>
Issue-Type: <功能|UI/UX|业务逻辑|数据状态一致性|API/SDK/集成|N/A>
Skill: <使用的 skill 名，多个用逗号>
Tools: <Read, Edit, Agent, Bash, ...>
Spec-Ref: <spec 文件路径#锚点，例如 feature-slice-003.md#AC-2；无则填 N/A>
Fix-Approach: <一句话说明修复/实现方式>
```

### 字段取值规范

| 字段 | 枚举/格式 | 说明 |
|------|----------|------|
| **大类** (Category) | `新加功能` / `bug fix` / `verify` / `DT测试` / `编译错误` | 必填，枚举五选一 |
| **问题分类** (Issue-Type) | `功能` / `UI/UX` / `业务逻辑` / `数据状态一致性` / `API/SDK/集成` / `N/A` | `新加功能`/`verify` 类可为 `N/A` |
| **Skill** | skill 名字符串 | 本次工作实际使用的 skill；多个用 `, ` 分隔；无则 `N/A` |
| **Tools** | 工具名字符串 | Read/Edit/Write/Bash/Grep/Glob/Agent 等；多个用 `, ` 分隔 |
| **Spec-Ref** | `<file>#<anchor>` | 精确到锚点（AC-ID、section）；无 spec 参考填 `N/A` |
| **Fix-Approach** | 单行，≤ 80 字 | 根因+做法一句话；避免"修复了一个 bug"这种空话 |
| **Summary** | 首行标题，≤ 60 字 | 遵循 `<大类>: <动作+对象>` 格式 |

### Summary 首行格式

```
<大类>: <精炼标题>
```

示例：
- `bug fix: 修正 LoginPage 状态未持久化问题`
- `新加功能: 实现健身计划详情页数据绑定`
- `DT测试: FEAT-003 从 RED 转 GREEN`
- `编译错误: 修复 HomePage.ets 类型推断失败`

---

## 4. 执行流程

```
用户请求提交
  │
  ├─ 1. 从会话上下文提取信息
  │     ├─ 大类：看最近工作性质（写新代码 / 修已有代码 / 跑测试 / 修编译 / verify）
  │     ├─ 问题分类：看修改内容域
  │     ├─ Skill：看本轮用过哪些 skill
  │     ├─ Tools：看实际用过的工具
  │     ├─ Spec-Ref：看 Read 过哪些 spec 文件和锚点
  │     └─ Fix-Approach：看修改的实质内容
  │
  ├─ 2. 跑 git status + git diff 核对变更
  │
  ├─ 3. 生成 commit message 草稿，展示给用户确认
  │     （展示格式要清晰，字段一目了然）
  │
  ├─ 4. 用户确认/调整
  │
  └─ 5. git add + git commit（HEREDOC 传 message）
```

---

## 5. 信息提取策略

### 大类判定优先级

1. 如果会话中主要在跑 `arkts-dt-verifier` → `DT测试` 或 `verify`
2. 如果主要在跑 `arkts-dt-autofix` 或修 RED→GREEN → `bug fix`
3. 如果主要在修编译报错 → `编译错误`
4. 如果 `a2h-execute` 新建页面/feature slice → `新加功能`
5. 如果 `a2h-verify` → `verify`
6. 否则看 git diff 性质：新文件为主 → `新加功能`；改已有 → `bug fix`

### 问题分类判定

看改动落点：
- 改了 `.ets` 的 UI 组件/样式/布局 → `UI/UX`
- 改了 state/store/数据流 → `数据状态一致性`
- 改了 API 调用/网络/SDK wrapper → `API/SDK/集成`
- 改了功能逻辑/算法/规则 → `业务逻辑`
- 新功能整体交付 → `功能`
- `编译错误`/`verify` 大类下若纯技术性修复 → `N/A`

### Skill / Tools 提取

- Skill：扫会话中实际 `Skill` 工具调用或被委托的 a2h-*/arkts-* skill
- Tools：列出本轮 commit 对应工作中真正调用过的工具名

### Spec-Ref 提取

扫会话中 `Read` 过的 `spec/` 目录文件；优先记录最相关的一个（如 feature-slice、ui-manifest）。锚点从当时读取的 section/AC-ID 推断，读不出具体锚点时至少记录文件名。

---

## 6. 输出模板

展示给用户确认时用以下格式：

```
即将创建 commit：
─────────────────────────
bug fix: 修正 HomePage 数据未刷新问题

Category: bug fix
Issue-Type: 数据状态一致性
Skill: arkts-dt-autofix
Tools: Read, Edit, Bash
Spec-Ref: spec/features/feature-slice-002.md#AC-3
Fix-Approach: @Local 状态装饰器（V2，等价 V1 @State）标注遗漏导致视图不订阅；补齐后手动 triggerRefresh
─────────────────────────
变更文件（git status --short）：
 M entry/src/main/ets/pages/HomePage.ets
 M entry/src/main/ets/viewmodel/HomeVM.ets

确认提交？(y/n/edit)
```

---

## 7. Commit 执行

用户确认后：

```bash
git add <具体文件>   # 不要用 git add -A
git commit -m "$(cat <<'EOF'
<大类>: <Summary>

Category: <...>
Issue-Type: <...>
Skill: <...>
Tools: <...>
Spec-Ref: <...>
Fix-Approach: <...>
EOF
)"
```

**不要**附加 `Co-Authored-By` 或 `Generated with Codex` 等尾注（这个项目的 commit 历史不带这类标记）。

---

## 8. 边界与错误处理

- 工作区无变更 → 告知用户"没有变更可提交"，不创建空 commit
- 变更含敏感文件（`.env`、`credentials.*`）→ 警告并让用户确认
- 用户回 `edit` → 展示 schema 允许用户逐字段修改，改完再提交
- 一次 commit 跨多个大类 → 建议拆分多个 commit，如用户坚持合并，大类字段取最主要的一项

---

## 9. 与 a2h-retrospect 的契约

a2h-retrospect 会用以下命令回捞：

```bash
git log --format="%H%n%s%n%b%n---" --grep="^Category:"
```

因此本 skill 生成的每个 commit 必须包含 `Category:` 行（首字段），否则 retrospect 扫不到。
