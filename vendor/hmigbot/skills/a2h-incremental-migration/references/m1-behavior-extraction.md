# §M1.3 行为提取（references 详细版）

主 SKILL.md §M1.3 的详细执行手册。**§M1 模式的核心**，两步：final state 主路径 + commit 辅助校准。

## Step 1 — 主路径：直接读 final state 源码提取行为轨迹（事实底线）

按 §M2.2 LLM 源码并排阅读模式（同一套方法论），针对用户指定 final state 上的关键页面/Service：

1. 读 layout XML + 对应 Fragment/Activity → 提取"用户可触及的交互入口"（按钮 / 菜单项 / Tab / 列表项点击 / 下拉刷新 / 长按等）
2. 对每个入口追 `setOnClickListener` / `onMenuItemClick` → handler 方法 → 调用到的 store/service
3. 形成行为轨迹清单：`{控件} → {触发} → {数据调用} → {UI 反馈}`

**关键**：这一步**完全不读** commit history。Step 1 的产出必须能完全在 final state 源码里找到对应锚点，commit 不能推翻代码事实。

### 正确示例（基于 final state 阅读）

```
ItemsFragment final state 行为轨迹：
  1. FAB tv_upload_item.click → openImagePicker() → 相册多选 → POST /api/items/batch-upload → 刷新列表
  2. list item 长按 → 进入 isManageMode → 底部 Toolbar 显示"删除"
  3. Toolbar 删除 → 确认对话框 → POST /api/items/batch-delete → 移除项
```

## Step 2 — 辅助校准：用 commit history 给行为轨迹补 metadata（仅校准，不替换）

收集辅助 commit 范围内所有非 merge commit（`git log --no-merges $RANGE`），分两层喂给 LLM。

### 必读层（commit messages 标题）

```bash
git -C "$ANDROID" log --no-merges --format="%h %s" $RANGE
```

按前缀分类信号：

| 标题前缀 | 校准动作 |
|----------|----------|
| `feat:` / `feature:` | 帮助 Step 1 做 **scope 单元划分**（这 commit 引入独立功能单元）|
| `fix:` / `bugfix:` | 给对应轨迹打 **边界 case 标签**（揭示开发者考虑过的 edge case，进 §S2 时附"已处理边界"）|
| `revert:` / `rollback:` | 警告 "X 行为曾出现但已撤销"。Step 1 没识别出 X → 一致；Step 1 识别到 X → 触发 §M1.2.5 残留物校验 |
| `refactor:` / `chore:` | 通常无行为变化，记录"该 scope 经历过重构" |
| 无前缀 / 团队 message 写得烂 | 不强制读，跳过 |

### 按需读层（完整 commit body + patch）

LLM 在 Step 1 final state 阅读中遇到"看不懂这段防御代码在防什么"时，去对应 commit 找 context：

```bash
# 例：final state 里看到 if (uri == null) return Toast.LENGTH_SHORT
# 反查 git log 找哪个 commit 加了这条 null 检查
git -C "$ANDROID" log -S "uri == null" --no-merges $RANGE
```

## Step 3 — 冲突仲裁

| 情景 | 仲裁 |
|------|------|
| Step 1 识别行为 X，Step 2 commits 也描述 X | ✅ 双重佐证，轨迹 + 强信心 |
| Step 1 识别行为 X，Step 2 commits 没提 | ✅ 以 Step 1 为准（可能 squash 或 commit message 写得烂）|
| Step 1 没识别行为 Y，Step 2 commits 描述 Y | ⚠ 进 §M1.2.5 残留物校验：Y 可能是已撤销功能（不该同步），也可能是 Step 1 漏抓（要补）|
| Step 1 识别 Y，Step 2 commits 含 `revert: Y` | 🟡 优先 §M1.2.5 残留物校验。final state 仍有 Y 活引用 → Step 1 正确；final state 仅函数体残留 → 标 RESIDUAL 不进 §S2 |

**绝对原则**：commit history 不能推翻 final state 的代码事实——final state 是事实底线。

## 错误示例（不接受）

```
（仅按 commit 标题逐 commit 提取，不读 final state）
Commit abc1234: feat: add batch upload  → 行为：FAB 上传
Commit def5678: revert: remove batch     → 行为：撤销
最终行为：???
```

这种做法忽略了"final state 才是真相"，应直接读源码确认 final state 是否有 FAB 即可。
