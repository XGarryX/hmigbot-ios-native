# bundled_spec_tools 架构文档

## 1. 项目定位

`bundled_spec_tools` 是一个**纯静态分析工具**，输入一个 Android 项目的源码目录，输出结构化 JSON，描述该 App 的全部 UI 结构、导航关系、控件行为和生命周期。这些 JSON 文件（统称 **facts**，其中每屏幕一份的迁移描述称为 **spec**）供下游 stage 消费，最终目标是把 Android App 自动翻译为 HarmonyOS（鸿蒙）应用。

**不做的事**：不编译 Android 代码、不运行 App、不生成 HarmonyOS 代码。它只负责"理解"Android App 的 UI 层并把理解结果写成确定性事实。

**在大流水线中的位置**：本工具是 `pipeline.py` 的 **Stage 0**（`stages/stage0_run_spec_tools.py` 调 `bundled_spec_tools/main.py`），产物落在 `<out>/intermediate/0_android_facts/`。后续 stage（1 规范化、2 框架映射、3 鸿蒙架构、5 feature tree、4 脚手架、7 agent bundle）都建立在 Stage 0 的 facts 之上。本文档只覆盖 Stage 0。

---

## 2. 设计原则

这些原则贯穿全部模块，是阅读后续章节的前提：

1. **确定性优先，推断兜底**。任何能从静态 AST / 调用图 / XML 确定推出的关系，绝不用启发式猜测。只有在确定性手段全部失败、且缺失会显著拉低覆盖率时，才生成带 `confidence: inferred` 标记的低置信度结果，并永远可与确定性结果区分。
2. **泛化，不针对单一仓**。所有正则与模式都基于 Android/Kotlin/Java 的**语言与框架通用写法**，不为某个具体 App 硬编码 id 名、类名或路径。
3. **复用既有产物，不重复扫描**。模块间通过已提取的中间 JSON（`source_findings`、`call_graph`、`static_xml` 等）传递事实；新分析尽量是对既有事实的纯函数 join，而非重新读源码。
4. **产物可审计**。每个中间 JSON 独立可读，字段语义稳定，便于调试与人工核对。
5. **tree-sitter 可选**。所有依赖 AST 的模块在 tree-sitter 不可用时回退到正则，保证离线/受限环境可运行。

---

## 3. 运行方式

```bash
# 直接运行 Stage 0
python bundled_spec_tools/main.py <android_project_root> [--out <dir>] [--validate]

# 或经由大流水线（Stage 0 是其中一环）
python pipeline.py --android-root <android_project_root> --out <dir>
```

- `<android_project_root>`：Android 工程根目录（含 `src/main/`、`AndroidManifest.xml`）
- `--out`：输出目录，默认 `bundled_spec_tools/output/`
- `--validate`：额外执行字节码 / Manifest / Layout 交叉验证

运行时间取决于项目规模，AntennaPod（534 个源文件）约 8-10 分钟，主要耗时在 tree-sitter AST 解析。

---

## 4. 流水线架构

`main.py` 按 7 个阶段依次执行，每个阶段输出独立 JSON：

```
[1/9] XML 静态提取          → static_xml.json
[2/9] 源码扫描 + 函数图谱    → source_findings.json, function_symbols.json, call_graph.json
[3/9] Ground Truth 合并      → ground_truth.json
[4/9] 导航图提取            → navigation_graph.json, navigation_candidates.json
                              + inflate 派生 class→layout 并入 navigation_graph
[5/9] Fragment 检测         → fragments.json
[6/9] 动态 UI 检测          → dynamic_ui.json
[7/9] 行为链提取            → behavior_chains.json
[可选] Gap 合并             → gap_analysis.json
[8/9] UI DAG 组装           → ui_dag.json, ui_paths.json, ui_effect_paths.json, ...
[9/9] Spec 生成             → specs/*.json, screen_index.json, app_model/
```

> 注：导航图(4)、Fragment(5)、动态 UI(6)、行为链(7)是**各自独立**的事实提取器，无从属关系；终端按连续顶层编号 `[1/9]…[9/9]` 呈现，避免把后三者读成"导航图的子步骤"。

### 依赖关系图

```
xml_extractor ─────┐
                   ├─→ ground_truth_builder ─┐
source_extractor ──┤                         │
                   │                         │
function_graph ────┼─→ inflate_owner_map ────┤   (join inflates × call_graph symbols)
                   │        │                 │
                   │        ↓ merge           │
                   ├─→ navigation_extractor ──┤
                   │                         │
                   ├─→ fragment_detector ─────┤
                   │                         ├─→ generate_specs ─→ specs/*.json
                   ├─→ dynamic_ui_extractor ──┤                    screen_index.json
                   │                         │
                   └─→ behavior_chain_extractor ─┘
                                             │
                      containment_linker (fragment_detector × static_xml → 容器边并入 nav)
                                             │
                                  ui_dag_assembler ─→ ui_paths
                                             │
                                  app_model_builder ─→ app_model/
```

---

## 5. 模块详解

### 5.1 XML 静态提取 — `extractors/xml_extractor.py`

**输入**：`res/layout/*.xml`, `res/menu/*.xml`, `res/navigation/*.xml`
**输出**：`static_xml.json`

- 解析所有 XML 布局，提取每个控件的 `id`、`tag`（类型名）、`text`、`hint`、`contentDescription`
- 判断控件是否可交互（Button/EditText/SeekBar 等天然可交互；TextView/ImageView 仅在有 `clickable=true` 或 `onClick` 时才算）
- 检测 `visibility="gone"/"invisible"` 的初始隐藏控件
- 提取 `onClick` XML 属性绑定
- **构建 `layout_trees`**：每个布局文件的完整控件树（保留嵌套层级），供 spec 的 `ui.tree` 使用
- 合并字符串资源 `res/values/strings.xml` 到 `strings`

```json
{
  "elements": [
    {"id": "btnSave", "tag": "Button", "layout": "activity_main", "text": "Save",
     "is_interactive": true, "source": "xml_layout"}
  ],
  "layout_trees": {"activity_main": {"tag": "LinearLayout", "id": "", "children": [...]}},
  "strings": {"app_name": "MyApp"},
  "stats": {"total": 736, "interactive": 252, "hidden_by_default": 67}
}
```

### 5.2 源码扫描 — `extractors/source_extractor.py`

**输入**：`src/main/**/*.java`, `*.kt`
**输出**：`source_findings.json`

5 个核心语义模式：

1. **R.id 分发块**（`id_dispatchers`）：when/switch 中 `R.id.xxx → handler` 的映射。
2. **事件注册**（`event_registrations`）：三种检测模式覆盖主流写法：
   - `binding.xxx.setOnClickListener(` — ViewBinding 直接引用
   - `findViewById(R.id.xxx).setOnClickListener(` — 链式调用（锚定 `R.id.` 编译期常量）
   - `var = yyy.findViewById(R.id.xxx)` → `var.setOnClickListener(` — 局部变量追踪
   提取 `view_ref`、`event_type`、`method`、`enclosing_fn`，以及 **callback metadata**（`callback_kind`、`callback_ref`、`registration_snippet`，供行为链恢复 handler 复用）。过滤 `remove*`、`(null)`、PendingIntent（标记 `is_pending_intent`）。
3. **可见性控制**（`visibility_controls`）：`setVisibility(View.GONE)`、`isVisible = false` 等。
4. **布局膨胀**（`inflates`）：`inflate(R.layout.xxx)` 和 `XxxBinding.inflate()`，携带 `enclosing_symbol_id`。
5. **数据驱动 UI**（`data_driven_ui`）：构建选项列表后传入弹窗/列表的静态文本。

`_enrich_findings_with_symbols()` 用 AST 为每条 finding 补 `enclosing_symbol_id` / `function_name` / `function_range`，这是行为链与 inflate 所有权追踪的关键锚点。

误报抑制：PascalCase `view_ref` 视为类型名过滤；`decorView`/`contentResolver` 等系统对象排除；第三方库目录不扫事件注册。同时生成 `view_ref_id_map`（per-file `{变量 → R.id.xxx}`）。

### 5.3 函数图谱 — `extractors/function_graph_extractor.py`

**输出**：`function_symbols.json`, `call_graph.json`

- 提取所有函数符号（`symbol_id` = `fn:package.Class.method/arity`），含 `class_name`、`file`、`start_line`、`end_line`
- 构建调用图（caller → callee），供行为链追踪与 inflate 所有权解析
- 优先 tree-sitter AST，回退正则

```json
// call_graph.json
{
  "symbols": [{"symbol_id": "fn:...", "function_name": "onClick", "class_name": "MainActivity", ...}],
  "calls": [{"from_symbol_id": "fn:A.onClick/1", "callee_name": "navigate", ...}],
  "unresolved_calls": [...]
}
```

### 5.4 AST 索引 — `extractors/ast_index.py`

tree-sitter Kotlin/Java 统一入口（依赖 `tree_sitter_language_pack`，缺失时各模块回退正则）：
- `parse_file(src_path)` — **共享解析缓存**：按 (路径, mtime, size) 缓存 `(source, root_node)`，一次 run 内同一文件只解析一次。`build_class_hierarchy`、`build_project_index`、fragment_detector、dynamic_ui_extractor、source_extractor 全部复用，消除跨模块的重复全量解析（否则同一批源文件一次 run 内会被重复解析 6–9 遍）。
- `build_class_hierarchy(project_root)` — 继承链映射（按 `(project_root, dep_roots, file_prefix)` 记忆化）
- `lookup_class(name)` / `_resolve_android_base(class_name)` — 判定 Activity/Fragment/Dialog/Service
- `find_enclosing_symbol(file, line)` — 行号 → 所属函数符号
- 低级遍历工具 `_walk` / `_node_text` / `_line` / `_source_files`

被 fragment_detector、navigation_extractor、source_extractor、function_graph_extractor、dynamic_ui_extractor 共享。

### 5.5 Ground Truth 合并 — `extractors/ground_truth_builder.py`

**输入**：`static_xml.json` + `source_findings.json`（+ nav + adapter_layouts）
**输出**：`ground_truth.json`

把 XML 控件与源码行为绑定：

1. `event_registrations` 的 `view_ref` 对齐 XML `id`（ViewBinding camelCase→snake_case）
2. `id_dispatchers` 直接对齐 XML `id`
3. `visibility_controls` 标记 `conditional_visibility`
4. 未在 XML 出现的 `inflates` → `dynamic_gap`
5. `data_driven_ui` → 数据驱动 gap
6. **未绑定 interactive 控件推断**（见 5.10）→ `inferred_event_bindings`

关键统计（AntennaPod）：525 XML 元素，246 绑定行为，271 interactive-or-bound，97 条件可见，dynamic_gap 80，unmatched 44。

### 5.6 导航图提取 — `extractors/navigation_extractor.py`

**输出**：`navigation_graph.json`, `navigation_candidates.json`

检测模式：`startActivity(Intent(this, XxxActivity::class.java))`（Kotlin）/ `startActivity(new Intent(this, XxxActivity.class))`（Java）、`XxxDialog().show()`、`intent-filter`、`finish()`/`onBackPressed()`、隐式 Intent、Adapter→Host 绑定、Fragment 导航。

```json
{
  "nodes": {"MainActivity": {"type": "activity", "layout": "main"}},
  "edges": [{"from": "MainActivity", "to": "SettingsDialog", "trigger": "menu settings", "type": "dialog"}],
  "class_layouts": {"MainActivity": "main"}
}
```

辅助 `nav_pipeline.py` 三层增强：L1 candidates（原始事实）、L2 通用模式提边（createIntent 工厂、本地 Intent 变量）、L3 可选 per-repo overlay。

本地 Intent 变量解析由共享 helper `_resolve_local_intent_target(var, window)` 完成（L1 candidates 与 L2 提边同源）：在 `startActivity(var)` 调用上方的回溯窗口内，找最近一处把 `var` 绑定到显式 Activity 类literal 的赋值，**同时支持 Kotlin `Intent(ctx, X::class.java)` 与 Java `new Intent(ctx, X.class)`，含无 `val`/`var`/类型声明的重赋值**（如 `intent = new Intent(this, X.class)`）。过程内、纯确定性——找不到显式类literal 时不推断：隐式 Intent（`ACTION_VIEW`/url/浏览器）、工厂构造（`X.createIntent(...)`）、透传 `getIntent()` 一律保持 unresolved，因为没有 app 内目标可链。

### 5.7 inflate 派生所有权 — `extractors/inflate_owner_map.py`

**为何需要**：导航分析只能发现「显式 Intent/transaction 目标」的屏幕。从不被显式跳转的辅助 Fragment、RecyclerView Adapter、子 Dialog 的 layout 没有任何 owning class，导致其 behavior chain 变成 orphan、spec 的 `screen_type=unknown`。

**核心洞察**：「**哪个类 inflate 了某 layout**」是最强的确定性所有权信号——比任何命名启发式都可靠。

- `build_inflate_class_layouts(source_findings, call_graph)`：把 `source_findings.inflates`（携带 `enclosing_symbol_id`）与 call_graph 符号表（解析 `class_name`）join，得到 `{class → [layout]}`。纯函数复用既有产物，**不重新扫描源码**。
- `merge_into_nav(nav, mapping)`：仅填充导航**未映射**的类（导航所有权优先），作为 **1:1 主映射**并入 `class_layouts`，自动流入 `layout_to_classes` / `class_to_layout_set` / screen_type 推断。

刻意用 1:1 主映射而非多映射：一个类可能 inflate 多个 layout（如某 Fragment 既加载主布局又展示子 dialog），若全量多映射会把同一 chain 重复塞进多个 spec。经 A/B 实测，多映射使 duplicated 105→176（+71 噪声）却不增加真正认领量，故弃用。

覆盖率（AntennaPod）：新增 18 条 class→layout，orphan chain 53→45，unknown screen_type 60→50。

### 5.8 Fragment 检测 — `extractors/fragment_detector.py`

**输出**：`fragments.json`

13 种挂载模式：FragmentTransaction.replace/add（正则）、ktx 泛型事务 `add<T>()`/`replace<T>()`（类作为类型参数，含 `commit { add<T>(...) }` 内的无接收者裸调用）、ViewPager Adapter、XML `<fragment>` 标签 + `FragmentContainerView android:name=`（静态挂载，等价于 `<fragment>`；排除 `NavHostFragment`）、Navigation Component 导航图 `res/navigation/*.xml` 的 `<fragment>`/`<dialog>` 目的地、全屏对话框内容绑定 `FullScreenDialogFragment.Builder.setContent(X::class.java / X.class, …)`（类字面量即被托管的 Fragment）、AST 类声明、AST FragmentTransaction、AST loadFragment/showFragment、AST `.show()`（DialogFragment，接收者容忍 `X\n  .newInstance(..)\n  .show(fm)` 跨行链式）、AST switch-case 工厂、Fragment 实例化上下文（含 `when` 箭头工厂 `-> XFragment()` / `-> X.newInstance()`、以及赋值/return/传参位置的 `X.newInstance(...)`）。

`_resolve_fragment_arg()` 追踪数据流确定实际 Fragment 类：直接类名 → `new Xxx()` → `Xxx.newInstance()` → 变量赋值 → 方法返回值。变量赋值优先读**显式类型标注**：`val f: XFragment = newInstance(...)` 的 RHS 常是静态导入的裸 `newInstance(...)`（无类前缀）追不到，但标注 `: XFragment` 直接确定类，无需推断。

**类名门槛 `_is_fragment_name()`**：正则模式（如 `.show()` 接收者、`X.newInstance()`）以子串 `Fragment in name` 兜底放行候选类，但这会误纳两类「含 Fragment 却非 Fragment」的名字——框架基础设施（`getSupportFragmentManager()` → `SupportFragmentManager`、`FragmentStateAdapter` 子类 → `*FragmentAdapter`、`*FragmentTransaction`/`*FragmentActivity`）与小写工厂方法名（`createDetailFragmentForNote`）。两条确定性收紧滤除它们：(1) 首字母必须大写（类名约定，排除方法名）；(2) 排除 `FragmentManager`/`FragmentTransaction`/`FragmentActivity`/`*FragmentAdapter` 等基础设施后缀。这些是 Android 命名约定，不针对单一仓库。误报不影响 `attached/needs_host` 覆盖率（它们本就不在 AST 声明集合里），但会虚增挂载点计数并生成指向不存在节点的 containment 边——收紧后这些假边消失。

**宿主覆盖口径**：抽象基类（作为另一 Fragment 的父类、自身未被直接挂载）通过子类挂载，不需要自己的宿主，从 orphan 分母中剔除（`coverage.base_class_count`）。覆盖率 = `attached_fragment_count / needs_host_count`，`needs_host = 声明总数 − 抽象基类`。

覆盖率（AntennaPod）：84 个声明 Fragment 中 79 个找到宿主（94%）。
覆盖率（WordPress）：声明 187，抽象基类 13，需宿主 174，已挂载 168（97%）；剩余 6 个 orphan 为自定义挂载 helper（`replaceFragment(X())` / `slideInFragment(new X())`，事务在 helper 体内、与类名解耦）、`showFragment(TAG){ X.newInstance() }` 工厂 lambda、`else X()` 裸构造工厂、以及只声明 `newInstance()` 工厂而 app 侧无静态挂载点（由外层容器/库内自管，如 `EditPostPublishSettingsFragment`、`LinkDialogFragment`）。前几类需自动发现自定义 helper（跨过程），后两类属语义上正确的 orphan，强挂即造边。

### 5.8b 容器边链接 — `extractors/containment_linker.py`

**作用**：把 Fragment / 底部导航的"宿主→区块"挂载关系作为**容器边**并入导航图，让"从启动页可达"的 DAG 不再只跟随 Activity `startActivity` 跳转。

**背景**：导航图只建模 startActivity 发现的屏幕跳转。主导航靠 Fragment / 底部导航的 App（宿主用 Fragment 替换切 tab、从不调 startActivity），其枢纽 Activity 几乎没有出边，BFS 走到枢纽即断（WordPress 从启动页只可达 5 屏）。被托管的屏幕全都提取到了（在 fragments.json / app_model 里），只是没**连**到宿主。

两条确定性容器边，每条都有具体源码/布局依据，绝不推断：
- **(a) host → fragment**（来自 fragments.json）：host 类经**内部类→最外层类**解析，使适配器/内部 helper（如 `NavAdapter`）归到真正声明它的屏幕/View（`WPMainNavigationView`）。
- **(b) screen → custom-view**：当一个**托管了 Fragment 的自定义 View** 作为标签出现在某屏幕的布局里（取自 static_xml 的 `tag@layout`），加 屏幕→该 View 边，桥接 `Activity → 自定义底部导航 View → 其 tab`。仅链接确实托管 Fragment 的自定义 View，无关 View 不会变成伪屏幕节点。

边 schema 与导航边一致（`from/to/to_layout/type/via/trigger/line`），`via=fragment_host`/`custom_view_host` 以区分容器与真实导航。在 [8/9] 调 `assemble` 前由 `merge_into_nav` 并入并重写 `navigation_graph.json`（assemble 从盘读 nav）。

覆盖率（WordPress）：从启动页可达屏幕 **5 → 26**。其中容器边链接贡献 5→24（+86 host→区块、+2 屏幕→自定义View）；本地 Intent 变量解析（§5.6，Kotlin+Java 双形态）把 `unresolved_start_activity` 109→32、`local_intent_var` 30→107、导航边 215→292（新增 77 条全是 Activity 整屏目标），可达再升至 26。剩余 32 条 unresolved 是隐式 Intent（`ACTION_VIEW`/url/浏览器，13 条）、工厂构造与无类literal 的透传 intent（19 条）——过程内无显式 app 内目标可链，留白是诚实结果，不推断。

### 5.9 动态 UI 检测 — `extractors/dynamic_ui_extractor.py`

**输出**：`dynamic_ui.json`

3 种动态创建模式：`addView`（程序化创建控件）、`inflate + addView`（动态插入布局片段）、`setAdapter`（RecyclerView/ListView 的 Adapter 关联，追踪 item 布局）。

```json
{
  "dynamic_elements": [...],
  "adapter_layouts": [{"adapter_class": "QueueRecyclerAdapter", "item_layout": "feeditemlist_item",
                       "host_class": "QueueFragment", "host_id": "recyclerView"}]
}
```

> spec 的 `ui.inflated_layouts`（来自 ground_truth 的 inflate gap）与此处的 `dynamic_elements`（addView 模式）是**互补**关系。

### 5.10 共享未绑定控件推断 — `extractors/unbound_control_inference.py`

为无 listener 的 interactive 控件生成低置信度 `inferred_event_bindings`，被 ground_truth 与 spec 复用：

- `build_layout_contexts(nav, adapter_layouts)`：一次构建 layout → owner/dialog/adapter 上下文
- `classify_unbound_control(tag, layout, ctx)`：按场景分类
  - `framework_managed` — TabLayout/ViewPager/RecyclerView/ScrollView 等框架托管
  - `value_read_on_confirm` — dialog 内的值输入控件（值在确认按钮 handler 读取）
  - `dialog_action` — dialog 内 Button（取消/关闭）
  - `adapter_bindview` — item 布局控件（handler 在 adapter.onBindViewHolder）
  - `programmatic` — 兜底，handler 存在但静态无法定位
- 每条推断 binding 带 `claim_hints`（owner_classes / screen_types / adapter_classes），给 spec orphan claiming 直接复用，统一标 `confidence: inferred`

### 5.11 行为链提取 — `extractors/behavior_chain_extractor.py`

**输入**：`source_findings` + `call_graph` + XML id 集合
**输出**：`behavior_chains.json`

三层架构：

**Layer 1 — Step Pipeline**（纯函数，无 Android 假设）：
- `classify_call(method_name)` → `navigate` / `ui_feedback` / `ui_update` / `async` / `call`
- `build_step_for_call(...)` → 递归构建步骤，沿 call_graph 展开（max_depth=3）
- `extract_braced_block(text, pos)` → 大括号匹配

**Layer 2 — Body Parser**（文本处理，无 call_graph 依赖）：
- `extract_handler_body(source_lines, reg_line)` → 提取方法体：花括号块、箭头 lambda（`v -> expr()`）、方法引用回退
- `_extract_calls_from_body(body, include_members)` → 提取方法调用名。**直接 handler body** 用 `include_members=True` 捕获成员调用（`view.setText(...)`、`launcher.launch(...)`）；调用图深层递归保持非限定调用，避免外部库叶子调用淹没链路
- `_extract_property_mutations(body)` → 检测 Kotlin/Android 属性式 UI 变更（`view.isVisible = false`、`label.text = ...`），映射为对应 `ui_update` step
- `_prune_effectless_calls(steps)` → 深度感知剪枝：剪掉递归展开中走到死胡同（无下游效果）的深层 `call` 噪声，保留 handler 自身语句、效果与控制流（见 §9.2）
- `split_body_by_conditions(body)` → 递归切分 if/when/else 分支为结构化 segment

**Layer 3 — Specialized Extractors**：
- `extract_event_chains(...)` → 为每个事件注册构建 event → handler → effect 链
- `extract_lifecycle_hooks(symbols)` → 提取生命周期方法的直接调用（callee 去重）

**handler body 恢复分层策略**（按 `callback_kind` 选路）：inline lambda → method reference（`this::onClick`）→ callback variable（追变量赋值）→ anonymous listener（`object : Listener {}`）→ fallback chain（基于 enclosing symbol 直接调用图，低置信度）。

**element_id 解析**（ViewBinding 支持）：`findViewById` 显式映射 > camelCase→snake_case + XML id 验证 > 直接匹配。

```json
{
  "element_id": "butSave",
  "view_ref": "butSave",
  "event_type": "click",
  "handler": {"method": "onCreate", "class": "MainActivity", "file": "...", "line": 42},
  "effect_chain": [
    {"step": "navigate", "target": "finish"},
    {"step": "ui_update", "action": "setVisibility", "value": "gone"},
    {"step": "condition", "expr": "isValid()", "then": [...], "else": [...]}
  ],
  "chain_depth": 3,
  "confidence": "static_analysis",
  "claim_hints": {"owner_classes": ["MainActivity"]}
}
```

`confidence` 区分来源：`static_analysis`（确定链）/ `fallback_analysis`（enclosing 调用图兜底）/ `pending_intent`（跨进程）/ `no_chain`（body 提取成功但无迁移相关效果，见 §8）。`stats.by_confidence` 聚合各级数量，终端 `[4d]` 据此输出。

步骤类型：

| step | 含义 | 关键字段 |
|------|------|---------|
| `navigate` | 页面跳转/返回 | `target`, `destination` |
| `ui_feedback` | 用户反馈 | `action`（Toast/Snackbar/dismiss） |
| `ui_update` | UI 状态更新 | `action`, `value`, `text` |
| `async` | 异步操作 | `target`（launch/enqueue） |
| `call` | 普通方法调用 | `target`, `symbol_id`, `nested` |
| `condition` | 条件分支 | `expr`, `then`, `else` |

覆盖率（AntennaPod）：386 bindings，with chain 360，no_chain 13，static_analysis 331。

### 5.12 view_ref 解析工具 — `extractors/view_ref_utils.py`

被 ground_truth_builder 与 behavior_chain_extractor 共享：
- `camel_to_snake(name)` — `drawerLayout` → `drawer_layout`（含字母↔数字边界）
- `clean_view_ref(ref)` — 去 `binding.`/`viewBinding.` 前缀
- `resolve_view_id(raw_ref, known_ids, file_ref_map)` — 多策略解析

### 5.13 其它基础模块

- `extractors/android_project.py` — `source_files` / `res_dirs` / `manifests` / `_is_ignored`
- `extractors/dependency_resolver.py` — 解析 `libs.versions.toml` JitPack 依赖与 `includeBuild`，下载到 `~/.cache/harmony-migration/deps/`
- `extractors/bytecode_navigation.py` + `class_parser.py` — 从 `.class` 常量池补充导航（需已编译）
- `extractors/ui_dag_assembler.py` — 从 launcher Activity 递归展开 UI DAG（max_depth=8），生成 `ui_dag.json` + `ui_paths.json`
- `extractors/ui_paths_nav_enumerator.py` — 枚举可读导航链（上限 800）→ `ui_paths_enumerated.json`
- `extractors/app_model_builder.py` — 分层 App 模型 `app_model/`（index / screens / features / paths / references）

### 5.14 验证模块 — `verification/`（`--validate`）

- `manifest_verifier.py` — 提取的 Activity 是否在 AndroidManifest 声明
- `layout_verifier.py` — XML 引用的 Fragment 是否有对应类
- `bytecode_verifier.py` — 从字节码继承链验证 Fragment/Activity 分类
- `report.py` — 汇总 `verification_report.json`

**字节码类目录扫描（`_class_dirs`）**：编译产物布局随 AGP/Kotlin 版本变化。`_CLASS_DIR_PATTERNS` 同时扫 `build/intermediates/javac`（Java）、`build/intermediates/built_in_kotlinc`（新版 AGP 内建 Kotlin 编译）、`build/tmp/kotlin-classes`（旧版 Kotlin）、`build/intermediates/classes`（按 variant 合并的 Java+Kotlin 全集），`bytecode_hierarchy()` 用短名 `seen` 集跨目录去重。只扫旧两项（javac + kotlin-classes）会在新版 AGP 下漏掉全部 Kotlin 类——WordPress 实测 Kotlin fragment 几乎全在 `built_in_kotlinc`/`classes`，补全后字节码可用类从 ~5791 升到 9909。

**基类清单**：`_ANDROID_FRAGMENT_BASES_SHORT` 含 `PreferenceFragment` 与 `PreferenceFragmentCompat`（两者都是真实 Fragment 基类，旧清单只有后者，导致 Preference 系 fragment 被误判 unknown）。

**Hilt 合成基类分流**：Dagger-Hilt 在 `@AndroidEntryPoint` 的源类与框架父类之间生成中间基类 `Hilt_<原名>`，只存在于字节码、源码无对应，否则会在 `bytecode_only` 里表现为上百个假“AST 漏报”。`_is_synthetic_generated()` 按固定前缀 `Hilt_`（跨项目通用约定）识别，diff 时移入独立 `synthetic_excluded` 桶并计数，不直接丢弃以保审计可见、不掩盖真实漏报。WordPress 实测分流 fragment 62 + activity 87。

**验证基线（WordPress，jetpackDebug，已编译）**：字节码类 9909；Fragment matched 186/187（99.5%），Activity matched 136/138（98.6%）。剩余分歧均已定位且非 verifier 缺陷：5 个 manifest activity 为第三方库（Zendesk / UCrop）仅在 Manifest 声明、源码不在仓库；3 个 ast_only 源码存在但未编译进当前 variant；1 个 bytecode_only（`LoginPrologueRevampedFragment`）源码在 flavor 源集真实存在但 AST hierarchy 未解析到——AST flavor 源集覆盖的真实信号，待单独跟进。

### 5.15 非 UI 组件归类 — `extractors/non_ui_components.py`

**为何需要**：迁移目标是把 Android app 翻成鸿蒙 app，不是硬把行为挂到屏幕上提覆盖率。orphan chain（§8.2）里大多数 handler 类**本就不是屏幕**——后台 `<service>`、桌面 widget `<receiver>`、传感器/滚动监听器、播放基础设施。它们是真实功能、需要迁移，但不属于任何 screen spec。本模块把这些 orphan 行为按 owning class 聚合成「非 UI 组件」，并给出鸿蒙能力映射提示，作为它们的归处。

**组件类型判定**（确定性，按优先级，记录 `kind_source` 供审计）：
1. **AndroidManifest 声明**（权威，无需编译）：`<service>`→`service`；`<provider>`→`provider`；带 appwidget meta/action 的 `<receiver>`→`appwidget_provider`；普通 `<receiver>`→`broadcast_receiver`。来源 `extractors/android_project.py:manifest_components()`。
2. **字节码继承链**（已编译时）：沿 `.class` super 链匹配 `*Service`/`AppWidgetProvider`/`BroadcastReceiver`/`*Listener`/`View*`，复用 `verification/bytecode_verifier.py:bytecode_hierarchy()`。
3. **类名后缀启发式**（兜底，标 `kind_source: name_heuristic`）。

**UI 类排除**：经判定为 `activity`/`fragment`/`adapter` 的 orphan 是 UI（如 `PagedToolbarFragment`、`EpisodeItemListAdapter`），**不进**本产物，计入 `stats.excluded_ui_chains`，留给屏幕/item_layout 路径。

**鸿蒙映射提示**：`service`→ServiceExtensionAbility(+AVSession)；`appwidget_provider`→FormExtensionAbility(服务卡片)；`broadcast_receiver`→CommonEvent/后台任务；`provider`→DataShareExtensionAbility；`listener`→宿主侧事件/传感器 API。

**与 app 其余部分的联系（双向）**：组件不是孤立的映射目标。利用 `call_graph.json`（对被调方做精确类名匹配）为每个组件补 `used_by`——构造或调用它的调用者类，并标出其中哪些是屏幕（在 navigation `class_layouts` 中），空 `used_by` 是诚实信号（无静态调用者，如框架回调驱动的 widget updater），不臆造。反向由 `inject_screen_backrefs()` 把组件作为一条 `non_ui_dependencies` 写回受影响的屏幕 spec，让翻译某屏幕的 agent 也看到它驱动了哪些非 UI 组件。反向解析以 spec 自身的 `class` 字段为权威键（不是 layout 名，因 `audio_player_fragment` 与 spec 的 `audioplayer_fragment` 可能不一致）——匹配不上即不写反链，不做模糊猜测，故正向 `screen_links` 可多于反向 `screen_specs_linked`。

orphan 集合由 `generate_all_specs` 返回的 `assigned_chain_ids` 推导（chain 不在其中即 orphan），不重复实现认领判定。产物 `non_ui_components.json`，由 `main.py` 在 spec 生成后装配（先 `build()`，再 `inject_screen_backrefs()` 回写 spec）。覆盖率（AntennaPod）：42 个 orphan 中 35 条归入 10 个非 UI 组件，6 条 UI（adapter 5 + fragment 1）排除，1 条无 handler 类；其中约 28 条 caller→screen 边写入 22 个屏幕 spec 的 `non_ui_dependencies`。

---

## 6. Spec 生成 — `generate_specs.py`

### 6.1 核心逻辑

为每个布局生成 `{layout}_spec.json`：按 layout 分组 static_elements → 反查 layout↔class → 收集导航出入边 → 合并 fragments / programmatic_views / behavior_chains / lifecycle_hooks / adapter_layouts → 附加 inferred bindings → 按渐进式披露顺序写出。

`_dedupe_layout_variants()` 处理 snake_case 转换差异（`media3_video` vs `media3video`）。

### 6.2 Spec Schema（v2.2，字段按渐进式披露排序）

**`brief` 排在最前**，LLM 读一屏即可决定是否深入；`event_bindings` 内 `effect_summary` 排在 `effect_chain` 之前（先看压缩标签，再看完整树）。

```json
{
  // ── 摘要（LLM 最优先读取，最前） ──
  "brief": {
    "interactive_controls": [{"id": "btnSave", "type": "Button", "label": "Save",
                              "actions": ["navigate:finish", "ui_feedback:Toast"]}],
    "nav_in": ["SplashActivity (activity)"],
    "nav_out": ["→ SettingsActivity (menu settings)"],
    "has_fragments": true, "has_adapters": false,
    "lifecycle_methods": ["onCreate", "onResume"]
  },

  // ── 身份 ──
  "screen_type": "activity|fragment|dialog|adapter_item|unknown",
  "class": "MainActivity",
  "layout": "activity_main",
  "source": "project|library",

  // ── 导航 ──
  "navigation": {
    "entry_points": [{"from": "SplashActivity", "trigger": "fn: onCreate", "type": "activity"}],
    "exit_points": [{"trigger": "menu settings", "destination": "SettingsActivity",
                     "destination_layout": "settings_activity", "type": "activity", "via": "startActivity"}]
  },

  // ── UI（元素 + 布局树 + 动态加载） ──
  "ui": {
    "elements": [{"id": "btnSave", "type": "Button", "label": "Save",
                  "visibility": "always|conditional", "condition": "", "is_interactive": true}],
    "tree": {"tag": "LinearLayout", "id": "", "children": [...]},
    "inflated_layouts": [{"source": "inflate_layout", "layout": "activity_main", "enclosing_fn": "...", "file": "..."}],
    "programmatic_views": [{"view_type": "TextView", "creation_method": "addView", "container_id": "..."}]
  },

  // ── 行为（事件 + 生命周期 + fragment + adapter） ──
  "behavior": {
    "event_bindings": [{
      "element_id": "btnSave", "event_type": "click", "handler_method": "onCreate",
      "effect_summary": ["navigate:finish", "ui_feedback:Toast"],
      "effect_chain": [{"step": "navigate", "target": "finish"}, {"step": "ui_feedback", "action": "Toast"}],
      "chain_depth": 2
    }],
    "lifecycle_hooks": {"onCreate": ["initView"], "onResume": ["refreshData"]},
    "fragments": [{"class": "SettingsFragment", "container_id": "fragment_container", "attach_method": "FragmentTransaction.replace"}],
    "adapter_bindings": [{"container_id": "recyclerView", "adapter_class": "MyAdapter", "item_layout": "item_row"}]
  },

  "stats": {"conditional_visibility": 2, "inflated_layouts": 1, "nav_out": 3, "nav_in": 2,
            "fragments": 1, "programmatic_views": 0, "event_bindings": 12, "event_bindings_with_chain": 5}
}
```

**合成 event_binding**：interactive 控件无 listener 时按 §5.10 分类自动生成（`value_read:on_dialog_confirm` / `ui_feedback:dismiss_dialog` / `adapter_bindview:{Adapter}.onBindViewHolder` / `framework:TabLayout.setupWithViewPager` / `programmatic:handler_in_code`）。

### 6.3 effect_summary

`_summarize_effects()` 把嵌套 `effect_chain` 树扁平化为翻译相关标签 `["navigate:finish", "ui_feedback:Toast", "ui_update:setVisibility"]`。只取 `navigate`/`ui_feedback`/`ui_update`/`async`，跳过通用 `call`/`condition`。

### 6.4 Behavior chain 分配到 spec

`generate_specs` 将全局 behavior_chains 分配到各 screen spec，匹配条件（OR，优先确定性）：

1. `element_id ∈ layout_ids` — chain 目标控件在当前 layout 的 XML 元素集
2. `claim_hints.owner_classes ∩ owner_classes` — handler 所在类（含内部类→外部类 `Foo$1`→`Foo`）属于当前 spec owner 集
3. `handler_class ∈ layout_to_classes[layout]` — 当前 spec 无 class，但 handler_class 的 layout 映射到当前 layout
4. `layout ∈ class_to_layout_set[owner_class]` — owner_class 反查匹配（含 adapter_class→item_layout、**inflate 派生映射**）

`class_to_layout_set` 的确定性数据源：`class_layouts`（已并入 inflate 派生映射）、nav nodes、`adapter_layouts`。

终端输出（[7/7]）：
```
Binding assignment: 385 chains → 340 assigned, 45 orphan, 105 duplicated
Fallback claimed: 5 (handler_class→layout)
Synthetic: 24 (cross-component)
Total event_bindings in specs: 469
```
- **orphan**：分配不到任何 spec 的 chain（见 §8.2）
- **duplicated**：被多个 spec 收走（element_id 在多 layout 存在，如 include 复用）
- **synthetic**：无 listener 控件合成的 binding（不来自 behavior_chains）
- **fallback_claimed**：通过 handler_class→layout 反查兜底认领

### 6.5 screen_index.json — 全局索引

`generate_specs` 完成后生成，LLM 读此一个文件即可了解 App 全貌：

```json
{"total_screens": 177,
 "screens": [{"layout": "activity_main", "class": "MainActivity", "type": "activity",
              "controls": 15, "interactive": 8, "event_bindings": 12,
              "nav_in": [...], "nav_out": [...], "tags": ["navigate:startActivity"],
              "spec_file": "activity_main_spec.json"}]}
```

### 6.6 渐进式披露工作流

```
LLM 翻译工作流：
  1. 读 screen_index.json   → App 全貌，规划 feature 分组
  2. 读 spec.brief           → 单页概览：控件 + 行为标签 + 导航
  3. 读 spec.ui / behavior   → 翻译时取完整 ui.tree、effect_chain、fragments
```

### 6.7 字段顺序在流水线中的保持

Stage 0 把 spec 写入临时目录后，`stages/stage0_run_spec_tools.py::_normalize_dir_facts_dir` 会做一次**路径归一化**（把绝对路径替换为相对 posix 路径）。该步**必须保持各文件的原始 key 顺序**——它只重写路径字符串，不重排 key。早期实现误用 `sort_keys=True` 把所有 facts JSON 按字母排序（`behavior` 排到 `brief` 前），破坏了渐进式披露顺序；现已改为顺序保持序列化。产物仍确定（同一次扫描 → 同一 dict 顺序 → 同一字节）。

---

## 7. 输出文件清单

| 文件 | 大小（AntennaPod） | 用途 |
|------|-------------------|------|
| `static_xml.json` | ~740KB | XML 控件原始数据 |
| `source_findings.json` | ~680KB | 源码扫描的语义模式 |
| `function_symbols.json` | ~2.5MB | 函数符号表 |
| `call_graph.json` | ~13MB | 调用图（最大文件） |
| `ground_truth.json` | ~550KB | XML + 源码合并事实 + 推断 binding |
| `navigation_graph.json` | ~110KB | 屏幕导航图（含 inflate 派生 class_layouts） |
| `navigation_candidates.json` | ~19KB | L1 导航候选 |
| `fragments.json` | ~78KB | Fragment 检测结果 |
| `dynamic_ui.json` | ~3KB | 动态 UI + Adapter |
| `behavior_chains.json` | ~1.9MB | 事件→效果链 |
| `non_ui_components.json` | ~小 | orphan 行为按非 UI 组件聚合（service/widget/receiver/listener）+ 鸿蒙能力提示 + `used_by` 调用者/屏幕（§5.15） |
| `ui_dag.json` / `ui_paths*.json` | — | UI 导航树与路径 |
| `specs/*.json` | ~177 个 | 每屏幕迁移 spec（被组件驱动的屏幕含 `non_ui_dependencies` 反链，§5.15） |
| `screen_index.json` | ~50KB | 全局屏幕索引（LLM 概览） |
| `app_model/` | ~1MB | 分层 App 模型 |
| `verification_report.json` | — | 交叉验证（--validate） |

> 经 `pipeline.py` 运行时（非仅 Stage 0），产物根目录另带一份 `PIPELINE_OUTPUTS.md` 索引（"什么产物在哪"的目录级地图）。其末尾的**数量统计 (Counts)** 小节由 `_build_counts_section()` 在产物生成后从各阶段产物（navigation_graph / fragments / behavior_chains / ui_dag / app_model / framework_map / harmony_arch / feature_tree）现读现算，随每次运行刷新；每处读取都有兜底，缺失的阶段自动省略，故部分 stage 跑也不报错。计数字段都取各产物 schema 稳定的现成统计，泛化不针对单一仓。

---

## 8. 覆盖率边界与未能分析的原因

静态分析存在不可消除的边界。本节基于 AntennaPod 实测数据，逐一说明**剩余未覆盖项的根因**，并区分「**应当留空**」（语义上本就无可迁移信息）与「**静态原理受限**」（需运行时/数据流分析才能解，超出纯静态范围）。**这些都不应通过针对性正则强行提高覆盖率**——那只会制造虚假事实，误导下游翻译。

### 8.1 无法提取 effect chain 的事件绑定（`no_chain`，AntennaPod 13 个）

这些 handler 的 body **成功提取**了，但展开后没有任何迁移相关的 step。分三类，**全部应当留空**：

| 类别 | 数量 | 典型 body | 为何留空 |
|------|------|-----------|---------|
| 返回字面量 | 3 | `return false` / `true` | OnLongClick/OnTouch 仅消费事件返回布尔，无副作用 |
| 纯状态赋值 | 5 | `longPressedItem = item;` | 只改成员字段，无 UI/导航效果；字段如何被消费属运行时数据流 |
| 其它非效果 | 5 | `toolbar.setNavigationIcon(null)` | 调用被 classify 为通用 `call`，且无下游可追踪效果 |

**根因**：`classify_call` 只把明确的 navigate/ui_feedback/ui_update/async 计为效果。纯赋值不是调用，事件消费型返回值不产生 UI 变化。这类 handler 在鸿蒙侧通常也无对应可迁移行为，强行编造 step 反而有害。

> 已修复的**假性** no_chain：早期版本因调用提取正则丢弃成员调用（`view.setText(...)`），把 80 个**本应有链**的 handler 误判为空。现捕获成员调用 + Kotlin 属性式变更后降到 13 个真·空链。

### 8.2 分配不到任何 spec 的 chain（`orphan`，AntennaPod 45 个）

chain 提取成功，但其 owning class 不映射到任何带 layout 的屏幕。按 handler 类性质分（实测 43 个可定位类）：

| 类别 | 数量 | 代表类 | 性质 |
|------|------|--------|------|
| 服务/控制器/辅助类 | 37 | `WidgetUpdater` `LocalPSMP` `PlaybackController` `ExoPlayerWrapper` `ShakeListener` `Media3PlaybackService` `EmptyViewHandler` `LiftOnScrollListener` | **非屏幕**：后台播放、widget 更新、传感器监听、滚动行为。它们注册的 listener 不绑定到某个可见 layout，**本就不该进任何 screen spec** |
| Adapter 内 listener | 5 | `EpisodeItemListAdapter` `PlaybackStatisticsListAdapter` | item 内控件 listener。若该 adapter 的 `item_layout` 关联缺失（dynamic_ui 未检出），则无法定位 item 布局 |
| 真·屏幕但无 layout | 1 | `PagedToolbarFragment` | 抽象/基类 Fragment，自身不 inflate 具体布局（由子类提供），故无 class→layout 映射 |

**根因**：
- 服务类 orphan 是**正确行为**——它们是 App 的非 UI 逻辑，不属于任何屏幕。把它们塞进某个 spec 才是错误。
- Adapter orphan 受限于 `dynamic_ui` 的 `setAdapter` 检测：当 adapter 实例化与 `setAdapter` 调用跨方法/跨文件，或经工厂构造时，host↔item_layout 关联断裂。补全需要**跨过程数据流分析**，超出当前单文件正则+调用图的范围。
- 抽象基类 Fragment 无自有布局，是 Android **运行时多态**结构，静态无法在基类侧确定具体 layout。

> **去向**：这些 orphan 不再只是「认领不到」的悬空行为。非 UI 类（service/widget/receiver/listener/辅助类）由 `non_ui_components.py`（§5.15）按组件归类、附鸿蒙能力提示，写入 `non_ui_components.json`；UI 类（adapter/抽象 Fragment）则计入 `excluded_ui_chains`，留给屏幕/item_layout 路径后续处理。即「不硬挂屏幕，也不丢功能」。组件还经 `call_graph` 反查出 `used_by`（谁在驱动它）并把屏幕调用者反链回对应 spec 的 `non_ui_dependencies`，避免成为脱离上下文的孤立映射目标。

### 8.3 完全没有找到行为绑定的控件（unbound interactive，AntennaPod 24 个，7 个未覆盖）

interactive 控件在 XML 中存在，但源码无对应 `setOnXxxListener`。`unbound_control_inference` 按场景推断了 17 个（dialog_action 5 / value_read_on_confirm 10 / framework_managed 2），剩 **7 个 `programmatic`** 兜底类未能确定 handler。

**根因**（programmatic 类未覆盖）：
- handler 通过**数据绑定（DataBinding `@{...}` 表达式）**或 **Compose/运行时反射**关联，静态正则不可见
- listener 在**基类/Mixin**中统一注册，子类布局的控件经继承获得行为——需跨类继承链的数据流
- 控件实际由**库内部**消费（自定义 View 自带交互），项目源码层面无注册点

这类控件已标 `confidence: inferred` + `inference_category: programmatic` + `effect_summary: ["programmatic:handler_in_code"]`，**明确告知下游"有交互但 handler 不可静态定位"**，而非伪造一个 effect。

### 8.4 screen_type=unknown 的 layout（AntennaPod ~50 个）

这些 layout 有控件但无 class→layout 映射，分两类：

- **include 片段 / 子组件布局**：`feeditemlist_header`、`feeditemlist_item`、`empty_view_layout`、`audio_controls`、`feed_statistics_card` 等。它们经 `<include>` 或作为 item/子 View 复用，**没有独立宿主类**——这是 Android 布局复用机制的固有特征，本就不对应单一屏幕。
- **库内/抽象布局**：由库或基类持有，项目侧无 inflate 点可锚定。

§5.7 的 inflate 派生映射已把能确定 owner 的（如 `fragment_online_search`→`DiscoveryFragment`）补全（unknown 60→50）；剩余的确实没有确定性所有权信号。

### 8.5 边界总结

| 现象 | 应当留空（语义无信息） | 静态原理受限（需运行时/数据流） |
|------|----------------------|-------------------------------|
| no_chain | ✅ 返回字面量、纯状态赋值 | — |
| orphan | ✅ 服务/控制器/辅助类 | Adapter 跨过程 host 关联、抽象基类多态布局 |
| unbound control | — | ✅ DataBinding/继承/库内消费 |
| unknown screen_type | ✅ include 片段/子组件布局 | 库内/抽象布局所有权 |

**结论**：剩余未覆盖项中，相当一部分是**语义上本就不该有可迁移信息**的（强行覆盖即制造噪声）；另一部分需要跨过程数据流或运行时信息，已用 `confidence`/`inference_category`/orphan 统计**显式标注边界**，把"不确定"如实传递给下游，而非用脆弱正则掩盖。

---

## 9. 关键算法与设计决策

### 9.1 ViewBinding camelCase → snake_case 解析

Android ViewBinding 将 XML `id` 转为 camelCase 属性名（`drawer_layout` → `binding.drawerLayout`）。`camel_to_snake()` 反向转换：小写→大写边界、字母→数字边界插入下划线。匹配优先级：`findViewById` 显式映射 > snake_case 转换 + XML id 验证 > 直接匹配。

### 9.2 Handler body 提取捕获成员调用 + 深层 call 噪声剪枝

`_extract_calls_from_body(body, include_members=True)` 对直接 handler body 捕获 `obj.foo(` 形式的成员调用，恢复了大量"全是成员调用"的 handler（`view.setText`/`launcher.launch`/`recyclerView.post`）。深层调用图递归保持非限定调用，避免外部库叶子调用淹没链路。配合 `_extract_property_mutations` 处理 Kotlin 属性式 UI 变更。

但成员调用若解析到项目方法会继续沿调用图递归展开（max_depth=3），大量展开会在 2-3 层深处终止于无法分类的通用 `call` 叶子（AntennaPod 约 4500 个）。这些叶子不被 `effect_summary`/`brief` 收录，只撑大原始链。`_prune_effectless_calls` **深度感知**地剪枝：depth-0（handler 自身语句，如 `openSettings()`）一律保留；depth≥1 的 `call` 仅当其子树仍能到达 navigate/ui_update/ui_feedback/async 时保留；效果与 condition（控制流）各层全保留。

实测（AntennaPod）：剪枝前后 with_chain 360 / no_chain 13 不变（零信号损失），394 个迁移效果全留，但 `call` 步骤 2354→1375、`behavior_chains.json` 1.9MB→720KB（低于改动前的 972KB）。

### 9.3 inflate 派生 class→layout 的确定性

「类 inflate 布局」是比命名启发式强得多的所有权信号。`inflate_owner_map` 用已提取的 `enclosing_symbol_id` join 符号表，纯函数、无重复扫描，仅填导航未覆盖的类，作 1:1 主映射避免 chain 重复认领（详见 §5.7）。

### 9.4 Spec 防膨胀

当 `class_name == ""` 时，所有 `"".find("")==0` / `""==""` 条件恒真会把全部 chain/fragment 塞入 spec。修复：所有匹配条件前加 `class_name and` 守卫，产物从 32MB 降至 1.5MB。

### 9.5 字段顺序的端到端保持

spec 在 generate_specs 按渐进式披露顺序构建，且 Stage 0 路径归一化改为顺序保持序列化（§6.7），保证 LLM 看到的最终产物 `brief` 在最前。

---

## 10. 开发约定

- **小步提交**：每个功能点单独 commit，附覆盖率前后对比
- **复用优先**：共享逻辑提取到 `view_ref_utils.py` / `unbound_control_inference.py` / `inflate_owner_map.py` 等公共模块
- **确定性优先**：见 §2，推断结果永远带 `confidence` 标记并可与确定结果区分
- **泛化**：禁止针对单一仓硬编码 id/类名；覆盖率提升须来自通用语言/框架模式
- **边界透明**：无法分析的项用 orphan/uncovered/inferred 统计如实暴露，不用脆弱正则掩盖（见 §8）
- **v2 唯一 schema**：v1 冗余字段已删除
- **同步更新本文档**：每次代码改动一并更新 ARCHITECTURE.md
