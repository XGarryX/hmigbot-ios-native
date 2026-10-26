# §M1 Final-state 优先 + commit 辅助 模式 — 详细执行手册

主 SKILL.md §M1 卡片的详细执行手册。**当用户能给出 Android 端 git 信息（分支名 / commit 范围 / GitHub URL）时使用本模式。**

## 核心方法论

以用户指定分支的 **final state** 为主信源（直接读源码提取行为轨迹），commit history 作辅助校准证据（提供边界 case 暗示 + scope 划分 + revert 警告）。两者矛盾时以 final state 为准。

天然兼容所有 merge 形态（fast-forward / `--no-ff` / squash / rebase）——主路径直接读 final state，不依赖 commit 序列结构。squash 只是辅助信号变弱（commit messages 数量少），不会让主路径崩塌。

## M1.1 探测目标 final state 与辅助 commit 范围

需要确认**两件事**：
1. **Final state**（行为同步的事实底线，必须）：当前分支 HEAD / 远端分支 tip / 包含未提交改动的工作区
2. **辅助 commit 范围**（WHY + 边界 case 暗示的补充证据，**可选**）：最近 N commit / 当前分支领先 main 的 commits / LAST_SYNC..HEAD

把候选结果贴给用户确认。**不得自己决定**这两件事的任何一项。用户回答"辅助 commit = 无"也合法，本 skill 仍能仅靠 final state 工作。

兜底：非 git 仓库或没有有用 history → `find -mtime -14` 查近期文件 mtime。

> 📖 完整探测命令（含 GitHub CLI 备选）→ **references/m1-detection-commands.md**

## M1.2 读取 diff（辅助证据，不是主路径）

diff 是 §M1.3 Step 2 "辅助校准" 的输入，不是主路径——主路径是直接读 final state 源码（§M1.3 Step 1）。

**绝对原则**：以 final state 的实际代码为同步目标。commit history（含 diff / messages）仅作辅助。一个功能在 RANGE 内被加了又删（净效果 = 在 final state 不存在），**禁止**进差异清单。

> 📖 完整 diff 命令 → **references/m1-detection-commands.md**

## M1.2.5 Final-state 残留物校验（轻量，所有场景必跑）

风险：**final state 上存在但实际无用的残留物**。例如 commit 链里 C1 添加大功能、C2 把入口删了但函数体没删、HEAD 上函数仍存在但已无引用。这种残留代码会被 §M1.3 的源码阅读"看见"并误识别为活功能。

**校验流程（轻量）**：

```bash
# 对 §M1.3 Step 1 提取出的每条行为轨迹，反查 final state 中行为入口的活引用
git -C "$ANDROID" grep -l "uploadItem" -- "*.kt" "*.java" "*.xml"
```

**判定**：
- 入口在 final state 仍可被用户触达（XML 里有对应 view + onClick 绑定 + 函数体非空）→ ✅ 活功能，进 §S2 清单
- 入口被删但函数体残留（grep 只命中函数定义自身、无任何调用方）→ 🟡 标 `RESIDUAL_INTERNAL_ONLY`，**默认 skip 不进 §S2**，仅作透明度记录
- 入口和函数都在但被 §2.6 死代码标记（注释 / `@Deprecated` / `if(false)`）→ 已被 §2.6 过滤，无需重复处理

## M1.3 行为提取（**本模式核心**，两步：final state 主路径 + commit 辅助校准）

> ⚠ 死代码过滤（必跑）：final state 源码里纯注释 / `@Deprecated` / `if(false)` 死分支等**不**计入行为变化。详见 references/dead-code-filter.md

### Step 1 — 主路径：直接读 final state 源码（事实底线）

按 §M2.2 LLM 源码并排阅读模式（同一套方法论），针对 final state 上的关键页面 / Service：读 layout XML + Fragment/Activity → 追交互入口的 `setOnClickListener` → handler → store/service → 形成行为轨迹 `{控件} → {触发} → {数据调用} → {UI 反馈}`。

**关键**：Step 1 **完全不读** commit history。产出必须能在 final state 源码里找到对应锚点，commit 不能推翻代码事实。

### Step 2 — 辅助校准：commit history 补 metadata（仅校准，不替换）

收集辅助 commit（`git log --no-merges $RANGE`），按 commit message 前缀分类：

| 前缀 | 校准动作 |
|------|----------|
| `feat:` | 帮助做 **scope 单元划分** |
| `fix:` | 给轨迹打 **边界 case 标签**（揭示 edge case，进 §S2 时附"已处理边界"）|
| `revert:` | 警告 "X 曾出现但已撤销"；触发 §M1.2.5 残留物校验 |
| `refactor:` / `chore:` | 通常无行为变化 |
| 无前缀 / 写得烂 | 跳过 |

**按需读层**：LLM 看到"防御代码不懂在防什么"时去对应 commit 找 context（`git log -S "uri == null" --no-merges $RANGE`）。

### Step 3 — 冲突仲裁

| 情景 | 仲裁 |
|------|------|
| Step 1 ✓ Step 2 ✓ | ✅ 双重佐证 |
| Step 1 ✓ Step 2 没提 | ✅ 以 Step 1 为准 |
| Step 1 没识别 Step 2 描述了 | ⚠ 进 §M1.2.5 残留物校验（可能已撤销，可能 Step 1 漏抓）|
| Step 1 识别 Step 2 含 `revert:` | 🟡 §M1.2.5：final state 有活引用 → Step 1 正确；仅函数体残留 → 标 RESIDUAL 不进 §S2 |

**绝对原则**：commit history 不能推翻 final state 的代码事实。

**反例**（错误做法）：仅按 commit 标题逐条提取，看到 `feat: add batch upload` + `revert: remove batch` 就纠结"最终行为是什么"——应直接读 final state 源码确认是否有 FAB。

> 📖 详细操作（Step 1 完整阅读流程 / Step 2 必读+按需读两层规则 / 完整冲突仲裁表 / 正反例输出）→ **references/m1-behavior-extraction.md**

## M1.4 查 HMOS 等价路径（**§M 通用收尾**，不 grep 类名）

按**行为入口 / 数据路径 / 状态交互**三维搜索：

```bash
HMOS={hmos_project}
# 行为入口：按文案 / Resource key
grep -rn "上传作品\|uploadItem\|works_upload" $HMOS/entry/src/main/ets/
# 数据路径：新接口
grep -rn "/api/items/batch-upload\|batchUpload" $HMOS/entry/src/main/ets/services/
# 状态/交互
grep -rn "picker\.PhotoViewPicker\|MIMETypes\.IMAGE" $HMOS/entry/src/main/ets/
```

读对应页面 `.ets` 的 `build()` + onClick 链路，判断行为是否闭环。

**必须补一步**：对每条候选差异跑 §3.5 的 HMOS Spec 双重验证。

## M1.5 分桶（**§M 通用收尾**）

| 桶 | 定义 | 处理 |
|---|---|---|
| ✅ HMOS 已覆盖 | 有等价行为路径 | 清单移除，列在透明度证据里 |
| 🟠 部分覆盖 | 有 UI 但缺步骤（例：没接新接口）| 进 S3，标注缺失环节 |
| 🔴 未覆盖 | 无等价路径 | 进 S3，标优先级 |

## M1.6 资源层（**§M 通用收尾**，符号差集在此处生效）

diff 中的 `res/drawable/*`、`res/mipmap/*`、`res/values/strings.xml`、`AndroidManifest.xml` 直接按名字同步，见 §A 资源迁移附录。

→ 进 §S2 用户对齐。
