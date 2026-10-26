<!-- when: 派发 Stage 1 converter（a2h-activity-converter）时加载本段 + _common.md -->
<!-- topics: Stage 1 converter prompt, 占位规则, forward-ref, stub 处理, 三源数据 -->

# §1. Stage 1 converter prompt（a2h-activity-converter）

> 公共占位规则 §2.1 见 [`_common.md`](./_common.md)，派发时一并 Read。

派发 Codex 子代理 `a2h-activity-converter`（定义于 `.codex/agents/a2h-activity-converter.toml`），任务提示词：

```
将 {activity_name} 从 Android 迁移到 ArkTS。

  参数:
  - activity_name: {activity_name}
  - ui_info: {ui_snapshots_path}
  - harmony_project_dir: {harmony_project_dir}
  - references_dir: {references_dir}
  - android_source_dir: {android_source_dir}
  - android_source_anchors: {来自 spec/baseline/ui/page_{page_id}.md 顶部 anchor 字段}
  - registered_placeholders: {按本页 owning_slice 前缀 grep spec/placeholder-registry.md 所得已登记占位（若无则空）}
  - wiring_ownership_map: {来自 coverage-matrix.md `Wiring Ownership Map` 段，本页相关的 (文件,handler)→owning_slice 子集}

  额外上下文:
  - 页面 Spec: spec/baseline/ui/page_{page_id}.md
  - 公共组件库路径: entry/src/main/ets/components/common/（如 Stage 2 已完成，请引用这些组件作为样式锚点）
  - **设计令牌（必读，不得跳过）**: `spec/baseline/ui-manifest.md` 的 `## 全局约定` 节整节读取
    （`sed -n '/^## 全局约定/,/^## /p' spec/baseline/ui-manifest.md`；本节是 grep-first 纪律的白名单例外，见 _common.md）
    * 该节记载的主色 / 主题 / 排版 / 图标方案是 Android 侧真值，**样式一律以此为准**（三源原则：结构看 view.xml、样式看令牌与 Android 主题、语义看 meta.json）
    * **主题层规格（机械注入，禁止转述/摘要）**：派发本 prompt 前，**派发方**（Stage 1 直派时=主线程；
      Step 3a 二级派发时=worker）**必须**运行
      `python3 <a2h-execute skill 根>/scripts/theme_brief.py --project <鸿蒙工程根> --activity {activity_name}`
      并把 stdout **原文**粘贴到下方占位块。输出自带 `<<<THEME-BRIEF v2 BEGIN/END>>>` 哨兵，
      粘贴后自检：prompt 内必须有成对哨兵、不得残留 `{THEME_BRIEF_STDOUT` 字样
      （教训：规格块经过任何一次模型转述就会丢失，两次实测子代理零命中）：

      {THEME_BRIEF_STDOUT — 派发前用 theme_brief.py 输出原文替换本行，禁止留空或改写}

    * **主题回执（收口对账凭证，per-page 分片）**：完成转换后写
      `spec/execution/theme-receipts/{page_id}.json`（每页一个分片文件，并发安全；
      **禁止写共享单文件**），形如
      `{"action_bar": "entry/src/main/ets/pages/MainPage.ets:54", "status_bar": "...:50", "button_shape": "...:86"}`，
      行号指向对应绑定真实所在行（仅写规格块里存在的条目；NoActionBar 主题无 action_bar 键；
      规格块声明"无强制条目"时不写回执）。
      收口时 `theme_gate.py` 按**必填闭集**机械对账（必填键由 resolved-theme 推导）：
      色值未绑定、硬编码 hex、形状未修正、必填键缺失、回执悬空 → 一律 FAIL 打回
    * Android 侧靠主题隐式继承的着色（Material 的 Button / Toolbar / TabLayout / FAB 等控件在 layout XML 里"裸"写、颜色来自 `themes.xml` 的 colorPrimary 系列）**必须在 ArkUI 侧显式绑定**为对应令牌资源（`$r('app.color.*')`），不得落回系统默认色
    * **禁止自创平行令牌体系**：转换期不得新建 `DesignTokens.ets` 之类的裸数字/裸色值常量文件，也不得在组件里硬编码色值与尺寸；令牌一律走 `$r('app.color.*')` / `$r('app.float.*')` 资源引用
      （边界说明：`arkts-design-tokens-extractor` 规约自述含"Stage 1 每页生成后 converter 内部固定挂钩"——**该挂钩在 a2h 管线内停用**：其 `DesignTokens.ets` 归并产物与本管线"一律 `$r` 资源引用"的纪律互斥，且会被 theme_gate 判 UNBOUND。extractor 仅作为用户显式调用的独立重构工具使用，且在本管线工程上应以 `--apply` 只落 `float.json/color.json` 路线。转换期不得以"稍后由 extractor 归并"为由留下裸值）
    * 令牌节缺失或与页面所需不匹配 → 报告 `design_tokens_missing`，禁止自行发明后静默继续
    * **界面文案逐字纪律**：Toast/按钮/弹窗等用户可见文案一律**逐字**取自 spec 或 Android
      strings 资源，禁止"用自己的话重写"（「您的退款已经返回到您的账号，请注意查收」→
      '退款成功' 即违纪实录）；业务常量（时长/上限/次数）逐值取自 spec，禁止发明近似值。
      收口时 literal_gate.py 按 spec 字面量清单机械对账，改写/缺失会被逐条点名
  - meta.json 关键字段
    * `needs_immersive_safearea`: true/false

  沉浸式 + 安全区 契约:
  仅当 meta.json `needs_immersive_safearea: true` 时调用 arkts-immersive-safearea 实施四层架构；false时跳过本契约。
  报告必填：needs=true → `immersive_safearea_implemented:[{layer,file,line}]×4`；needs=false → `immersive_safearea_skipped:<page_type>`

  stub 处理规则（严格）:
  1. 遇到 spec 中 stub: ComponentX(...) → 读取 android_source_anchors[ComponentX] 指向的源文件
  2. 找到源文件 → 按其 Kotlin/Java 实现生成 ArkTS 对等代码
  3. anchor 缺失 / 读取失败 / 文件路径不存在 → **必须 FAIL 返回报告，禁止 placeholder 占位**

  占位规则：converter 阶段可生成的 4 类合法占位的 marker 形态与 kind 类型:
  - `forward-ref`：未实装 handler / 跨切片 ViewModel 等代码桩，marker `// FWD-REF: <P-ID> resolve_by=Slice {N} Step 3d`
  - `thirdparty-sdk`：仅当 registry 已登记（plan 期直写）时允许，marker `// PLACEHOLDER: <P-ID> trigger=...`
  - `resource-pending-asset`：fallback 资产引用，marker `// FWD-REF: P-RES-ASSET-{seq} kind=resource-pending-asset trigger=<resource-id> 就绪`
  - `forward-ref-uncertain`：转换期自判的不确定区域（常见于 ui-manifest confidence=medium/low 页面的动态值/几何近似），marker `// TODO: <reason>` + **必须同步登记 placeholder-registry**（P-S{N}-UNC-{seq} + kind=forward-ref-uncertain + resolve_by=Slice {N} Step 3a）

  Phase 4 局部语法自检失败可留 `// TODO:` 标注 + 同步登记 registry，留待 a2h-execute Batch-level build 收敛。
  其余形式（**未登记的** `// TODO` / 空回调 / 空 try-catch / 资源 value 含未登记 `[TODO:...]`）一律 FAIL。

  返回报告（结构化）必须含:
  - failed_stubs: []                # spec stub 无法展开清单（anchor 缺失/读取失败），与编译无关
  - generated_placeholders: []      # 每项 6 字段（P-ID + location + trigger_condition + kind + resolve_by + status）
  - illegal_placeholder_attempts: []  # 被规则拒绝的尝试（未登记 TODO / 占位禁令命中等）
  - low_confidence_uncertain_regions: []  # 仅 confidence != high 时列出 forward-ref-uncertain P-ID 及原因

  再次强调：failed_stubs（stub 无法展开）必须为空、且无非法占位尝试，本页才 PASS。
  ⚠️ 禁止任何编译/构建（hvigorw / hmos-builder / hmos-fix-build-errors）——编译由 §3b Batch 收尾统一跑一次，并发 hvigor 锁会拖垮整批。
  完成后返回转换报告。
```

**五参数说明**：

| 参数 | 含义 | 来源 |
|------|------|------|
| `activity_name` | 目标 Android Activity 类名 | ui-plan.md 的 Android 来源列 |
| `ui_info` | UIAutomator 快照目录路径（含 view.xml + meta.json） | 项目中的 ui-snapshots 目录 |
| `harmony_project_dir` | HarmonyOS 工程根目录 | 当前项目路径 |
| `references_dir` | 领域知识和映射参考文件目录 | `$SKILLS_ROOT/android-ui-graph-query/references/`（skill 安装根常见为 `.agents/skills/`） |
| `android_source_dir` | Android 源码根目录 | 用户提供的 $ANDROID_SRC |

**三源数据**：converter agent 消费三种数据源：
1. `view.xml` — UIAutomator dump 的视图层次
2. `meta.json` — 页面元数据（可交互元素、导航路径等）
3. 源码 layout XML — Android 原始布局文件（通过 `android_source_dir` + Activity 源码中的 `setContentView` 定位）
