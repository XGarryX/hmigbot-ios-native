# §M1.1 + §M1.2 探测与 diff 读取命令（references 详细版）

## §M1.1 探测目标 final state 与辅助 commit 范围

需要确认**两件事**：
1. **Final state**：行为同步的事实底线（必须）
2. **辅助 commit 范围**：WHY + 边界 case 暗示的补充证据（可选）

### 探测命令

```bash
ANDROID={android_dir}

# === 探测 final state 候选 ===
# (a) 当前分支 + HEAD（最常见的 final state）
git -C "$ANDROID" branch --show-current
git -C "$ANDROID" log -1 --format="%h %s" HEAD

# (b) 远端分支列表（用户可能想以某个远端 tip 为 final state）
git -C "$ANDROID" branch -r | head -10

# (c) 工作区有未提交改动？这才是真正的 final state
git -C "$ANDROID" status --short | head -40
git -C "$ANDROID" diff --stat | head -40

# === 探测辅助 commit 范围 ===
# (d) 最近 N 个 commit
git -C "$ANDROID" log --oneline -20

# (e) 当前分支领先 main 的 commits（feature 分支场景）
git -C "$ANDROID" log --oneline main..HEAD

# (f) 自上次同步点以来的 commits
# git -C "$ANDROID" log --oneline LAST_SYNC..HEAD --no-merges

# === 兜底（非 git 仓库或没有有用 history 时）===
# (g) 过去 14 天 mtime 文件
find "$ANDROID" \( -name "*.kt" -o -name "*.java" -o -name "*.xml" \) \
  -not -path "*/build/*" -mtime -14 -type f | head -40
```

把结果贴给用户确认两件事。**不得自己决定**这两个的任何一项。

## §M1.2 读取 diff（辅助证据，不是主路径）

### 本地 git（推荐）

```bash
RANGE={base}..{head}   # 或单个 {sha}
git -C "$ANDROID" diff --name-status $RANGE
git -C "$ANDROID" diff $RANGE -- "*.java" "*.kt" "*.xml"
git -C "$ANDROID" log --format="%h %s%n%b" $RANGE
git -C "$ANDROID" diff HEAD   # 未提交
```

### GitHub CLI（仅有 GitHub URL）

```bash
gh api repos/{owner}/{repo}/commits/{sha} \
  --jq '.files[] | {filename, status, patch}'
gh api repos/{owner}/{repo}/compare/{base}...{head} \
  --jq '.files[] | {filename, status, patch}'
```

### 读 diff 的定位

- diff 是**辅助证据**，提供 §M1.3 Step 2 "辅助校准" 的输入
- diff **不是**主路径——主路径是直接读 final state 源码（§M1.3 Step 1）
- diff 用于补充 commit messages 里没说清楚的 patch 细节（如 fix 类 commit 的具体修复点）

**绝对原则**：以 final state 的实际代码为同步目标。commit history（含 diff / messages）仅作辅助。一个功能在 RANGE 内被加了又删（净效果 = 在 final state 不存在），**禁止**进差异清单。
