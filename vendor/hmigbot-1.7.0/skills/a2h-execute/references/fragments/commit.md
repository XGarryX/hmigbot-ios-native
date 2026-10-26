# commit — 7 字段结构化提交格式

```
<大类>: <Summary（≤60 字，动作+对象）>

Category: <新加功能|bug fix|verify|DT测试|编译错误>
Issue-Type: <功能|UI/UX|业务逻辑|数据状态一致性|API/SDK/集成|N/A>
Skill: <本次实际使用的 skill，逗号分隔；无则 N/A>
Tools: <Read, Edit, Bash, Agent, ...>
Spec-Ref: <file#anchor，如 feature-slice-003.md#AC-2；无则 N/A>
Fix-Approach: <根因+做法一句话，≤80 字，禁"修复了一个 bug"式空话>
```

规则：
- `Category:` 行必在且是正文首字段——a2h-retrospect 用 `git log --grep="^Category:"` 回捞，缺了扫不到。
- 信息从会话上下文提取，不追问用户；提交前 `git status` + `git diff` 核对。
- `git add <具体文件>`，禁 `git add -A`；message 用 HEREDOC 传。
- 禁附加 Co-Authored-By / Generated with 等尾注。
- 一次改动跨多个大类 → 拆多个 commit。

<!-- source: commit/SKILL.md:L29-63,L152-167,L180-188 -->
