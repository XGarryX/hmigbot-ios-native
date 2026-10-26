---
name: android-ui-graph-builder
description: 'Build a structured graph model (knowledge graph) from an Android project''s UI code. Analyzes XML layouts, Java/Kotlin sources, AndroidManifest, navigation graphs, and menu resources to produce four JSON files: Screen.json, Component.json, Navigation_Edge.json, Containment_Edge.json. Use whenever the user asks to analyze, model, or reverse-engineer the UI layer of an Android project ("界面图谱", "UI 建模", "组件关系", "界面跳转关系", "screen/component/navigation map"), or simply says "analyze this Android project" when it contains XML layouts. This skill creates the graph; to query an existing graph use android-ui-graph-query.'
metadata:
  type: domain
  domain: migration
  tags:
  - migration
  - android
  - ui-graph
  - analysis
---
# Android UI Graph Builder

This skill turns an Android frontend project into a structured graph expressed as four JSON files.
The graph captures every screen (Activity, Fragment, Dialog, etc.), every UI component (View/ViewGroup),
their full attributes, the parent-child containment tree, and all navigation (screen-to-screen) edges.

## Core design: division of labor

A critical insight: LLMs are good at semantic understanding (identifying screens, understanding
navigation intent, describing triggers in natural language) but unreliable at deterministic
bookkeeping (generating unique IDs for hundreds of components, counting XML siblings, maintaining
cross-file ID consistency). This skill addresses this by splitting work:

| Task | Who does it | Why |
|------|-------------|-----|
| Identify screens, extract screen metadata | **LLM** | Requires understanding Java/Kotlin code, Manifest, inheritance |
| Parse XML layouts → Components + Containment | **Python script** | Deterministic, no missed IDs, no counter errors |
| Identify navigation, write trigger descriptions | **LLM** | Requires understanding code logic, click listeners, intent flow |
| Merge, validate, fix ID references | **Python script** | Guarantees cross-file ID consistency |

## Prerequisites

The user should provide access to an Android project. The skill adapts to different project structures:

**Standard single-module:**
```
app/src/main/java/...
app/src/main/res/layout/...
app/src/main/AndroidManifest.xml
```

**Multi-module (Gradle):**
```
app/src/main/...
feature-login/src/main/...
feature-home/src/main/...
lib-common/src/main/...
```

**Build variants:** The skill defaults to the base `layout/` directory. If `layout-land/`, `layout-sw600dp/` etc. exist, note them in summary but process only the base variant unless the user asks otherwise.

At minimum these are needed:
- XML layout files (`res/layout/`)
- Java or Kotlin source files containing screen classes
- `AndroidManifest.xml`

---

## Workflow (7 steps)

```
1. READ the schema           → references/schema_v2.md
2. SCAN the project           → inventory all relevant files
3. EXTRACT screens (LLM)      → produce Screen.json
4. PARSE layouts (SCRIPT)     → produce components_raw.json + containment_raw.json
5. EXTRACT navigation (LLM)   → produce Navigation_Edge.json (using IDs from step 4)
6. MERGE and ENRICH (SCRIPT)  → produce final Component.json + Containment_Edge.json
7. VALIDATE (SCRIPT)          → cross-check all ID references, fix inconsistencies
```

**Before doing anything else**, read `references/schema_v2.md` in this skill's directory to load
the full JSON schema definition.

---

## Step 1: Read the schema

```bash
view <skill_directory>/references/schema_v2.md
```

Key conventions:
- Every required field must appear in the output.
- Undetermined values → `"unknown"` (strings), `{}` (objects), `[]` (arrays).
- Never omit a required field; never invent values not in the source.

---

## Step 2: Scan the project

Adapt all paths to the actual project. For multi-module projects, scan each module.

```bash
# Detect project structure (single vs multi-module)
find <project_root> -name "build.gradle" -o -name "build.gradle.kts" | head -20

# Find all XML layout files across all modules
find <project_root> -path "*/res/layout*" -name "*.xml" | sort

# Find all potential screen classes (broad search)
grep -rl --include="*.java" --include="*.kt" -E \
  "(extends|:)\s*(AppCompat)?Activity\b|(extends|:)\s*(Fragment|DialogFragment|BottomSheetDialogFragment)\b|(extends|:)\s*(Dialog|AlertDialog|PopupWindow)\b" \
  <project_root> | sort

# Also find screens via custom base classes (common in real projects)
# First, identify project base classes:
grep -rl --include="*.java" --include="*.kt" -E \
  "abstract\s+class\s+Base\w*(Activity|Fragment)" <project_root>
# Then find classes extending those base classes too.

# Find AndroidManifest.xml (may be multiple in multi-module)
find <project_root> -name "AndroidManifest.xml" | sort

# Find navigation graphs
find <project_root> -path "*/res/navigation*" -name "*.xml" | sort

# Find menu resources
find <project_root> -path "*/res/menu*" -name "*.xml" | sort
```

Build a complete inventory before proceeding. For multi-module projects, track which module
each file belongs to.

### Identifying screens through inheritance chains

Real projects often use custom base classes. Follow the full chain:

```
BaseActivity extends AppCompatActivity       ← abstract, NOT a screen
  └── HomeActivity extends BaseActivity      ← IS a screen
  └── LoginActivity extends BaseActivity     ← IS a screen

BaseFragment extends Fragment                ← abstract, NOT a screen
  └── HomeFragment extends BaseFragment      ← IS a screen
```

Rules:
- Abstract classes are NOT screens (they have no layout of their own).
- A class is a screen if it (a) transitively extends Activity/Fragment/Dialog/PopupWindow,
  AND (b) is concrete (not abstract), AND (c) has a layout (setContentView or inflate).
- Also check for `PreferenceFragmentCompat`, `ListFragment`, `MapFragment`, and other
  library-provided Fragment subclasses — they are screens if used in the project.

---

## Step 3: Extract Screen nodes → Screen.json (LLM task)

For each identified Screen class, read its source file, layout XML, and AndroidManifest entry,
then produce a Screen node conforming to the schema.

### 二三层 UI 来源清单（必须全部识别，不依赖 LLM 自由发挥）

下游 [arkts-ui-coverage-auditor](../arkts-ui-coverage-auditor/SKILL.md) 依赖本步骤识别完整。漏识别会导致 spec 缺二三层 page、ArkTS 端手工补救火（实证：Fitness 项目 84 page spec 漏 100+ 二三层页）。

按以下 8 类信号穷举搜索：

| # | 信号 | 出现位置 | 层级 |
|---|---|---|---|
| 1 | `ViewPager.adapter` / `ViewPager2.adapter` → `getItem(int)` 返回的 Fragment 列表 | `.kt`/`.java` | 二层 |
| 2 | `TabLayout` + `ViewPager` 的 Tab Fragment 子项 | `.kt`/`.java`/XML | 二层 |
| 3 | Step / Wizard 类 Fragment（命名通常含 Step1/Step2 等数字后缀） | 类名/包名 | 二/三层 |
| 4 | `BottomSheetDialogFragment` / `DialogFragment` / `PreferenceDialogFragmentCompat` | `.kt`/`.java` | 三层 |
| 5 | 三方弹窗库：`XPopup.Builder.asCustom(...)` / Lxj 等 | `.kt`/`.java` | 三层 |
| 6 | `PopupWindow` / `DropDownPopupWindow` 含 layout 引用 | `.kt`/`.java` | 三层 |
| 7 | `FragmentTransaction.replace(...)` / `add(...)` 通过类引用反查 | `.kt`/`.java` | 二/三层 |
| 8 | Compose `composable("route")` 路由名 | `.kt` | 一/二层 |

> 上面任何一条命中 → 必须产生对应的 `Screen` 节点（带正确 `type`：Fragment / DialogFragment / BottomSheetDialogFragment / Dialog / PopupWindow 等）。漏识别 → 下游 auditor 在启动校验段会报警 `BUILDER_INCOMPLETE`。

### Where to find each field

| Field | Source |
|-------|--------|
| `id` | `screen:{full.qualified.ClassName}` |
| `type` | From the superclass chain: Activity / Fragment / DialogFragment / BottomSheetDialogFragment / Dialog / PopupWindow |
| `name` | Simple class name |
| `package` | Package declaration in source file |
| `layout_ref` | `setContentView(R.layout.xxx)` or `inflate(R.layout.xxx, ...)` or derive from ViewBinding class name (`ActivityMainBinding` → `R.layout.activity_main`) |
| `source_file` | Relative path from project root |
| `language` | `.kt` → Kotlin, `.java` → Java |
| `theme` | Manifest `<activity android:theme="...">`, or app-level `<application android:theme="...">` |
| `parent_activity` | For Fragment/Dialog: find which Activity hosts it. Activity itself → `"none"` |
| `menu_ref` | `onCreateOptionsMenu` → `menuInflater.inflate(R.menu.xxx, ...)` |
| `has_options_menu` | Whether `onCreateOptionsMenu` is overridden (Fragment: also check `setHasOptionsMenu(true)`) |
| `has_toolbar` | Layout XML contains `Toolbar`/`MaterialToolbar`, or source calls `setSupportActionBar` |
| `orientation_config` | Manifest `android:screenOrientation="..."` |
| `config_changes` | Manifest `android:configChanges="..."` |
| `lifecycle_callbacks` | All overridden lifecycle methods found in source |
| `metadata.*` | From AndroidManifest `<activity>` attributes |

### Output

Save as `/home/claude/Screen.json` — a JSON array. This file is also the input for Step 4.

---

## Step 4: Parse layouts → Components + Containment (SCRIPT task)

This is the most important step for ID reliability. Use the deterministic parser script.

```bash
python3 <skill_directory>/scripts/parse_layouts.py \
  <project_root> \
  /home/claude/Screen.json \
  /home/claude/raw_output/
```

This produces:
- `/home/claude/raw_output/components_raw.json` — all Component nodes with deterministic IDs
- `/home/claude/raw_output/containment_raw.json` — all parent-child edges with correct IDs

The parser:
- Generates consistent component IDs (no counter drift)
- Handles `<include>`, `<merge>`, `<ViewStub>`, `<fragment>` correctly
- Extracts and classifies all XML attributes
- Recursively follows included layouts
- Connects Screen → root component containment edges

**After the script runs**, review its stderr output for any warnings (missing layouts, parse errors).
If there are issues, investigate and fix the Screen.json `layout_ref` values.

### Enriching component attributes (LLM task, optional)

The script extracts attributes that are directly in the XML. The LLM can enrich components with
information from code that isn't visible in XML:
- Components created dynamically in Java/Kotlin code (add them to Component.json with `source: "dynamic"`)
- Visibility changes done in code (`view.visibility = View.GONE`)
- Click listeners set in code (update `behavior_attrs.onClick`)

If enrichment is needed, save LLM additions as `/home/claude/llm_output/Component.json` alongside
a copy of Screen.json and Navigation_Edge.json. These will be merged in Step 6.

---

## Step 5: Extract Navigation edges → Navigation_Edge.json (LLM task)

**CRITICAL**: When writing `source_component` IDs in navigation edges, you MUST reference the exact
IDs from `/home/claude/raw_output/components_raw.json` (produced in Step 4). Do NOT invent
component IDs from memory. Instead:

1. First read `components_raw.json` and note the available component IDs.
2. For each navigation action found in source code, match the triggering component to an ID
   from that list.
3. If no exact match exists, use `"unknown"`.

### Patterns to detect

| Code pattern | mechanism |
|-------------|-----------|
| `startActivity(Intent(this, Xxx::class.java))` | `"Intent"` |
| `startActivityForResult(...)` / `ActivityResultLauncher.launch(...)` | `"StartActivityForResult"` |
| `findNavController().navigate(R.id.action_xxx)` | `"NavController"` |
| `supportFragmentManager.beginTransaction().replace(...)` | `"FragmentTransaction"` |
| `XxxDialogFragment().show(...)` / `AlertDialog.Builder(...).show()` | `"DialogShow"` |
| `PopupWindow.showAtLocation(...)` / `showAsDropDown(...)` | `"PopupShow"` |
| Deep link in Manifest or NavGraph | `"DeepLink"` |

### For each navigation edge

1. Identify `from` (current screen) and `to` (target screen) — use Screen IDs from Screen.json.
2. Find the triggering component: look for the `setOnClickListener`, `onOptionsItemSelected`,
   or other event handler that contains the navigation code. Map it to a component ID from
   `components_raw.json` by matching `android_id`.
3. Write `trigger` as a Chinese natural-language description.
4. Extract `extras`, `flags`, `transition_anim`, `condition`, `direction`.

### Navigation Graph support

If the project uses Jetpack Navigation (`res/navigation/*.xml`):
1. Parse each `<action>` element; `app:destination` → target.
2. `app:enterAnim`, `app:exitAnim` → `transition_anim`.
3. `<argument>` elements → `extras`.
4. Cross-reference source code to find which component triggers each action.

### Output

Save as `/home/claude/Navigation_Edge.json`.

---

## Step 6: Merge and produce final outputs (SCRIPT task)

If you enriched components in Step 4's optional LLM step, merge them:

```bash
python3 <skill_directory>/scripts/merge_components.py \
  /home/claude/raw_output/ \
  /home/claude/llm_output/ \
  /mnt/user-data/outputs/
```

If no LLM enrichment was done, simply copy the authoritative files:

```bash
cp /home/claude/Screen.json /mnt/user-data/outputs/Screen.json
cp /home/claude/raw_output/components_raw.json /mnt/user-data/outputs/Component.json
cp /home/claude/raw_output/containment_raw.json /mnt/user-data/outputs/Containment_Edge.json
cp /home/claude/Navigation_Edge.json /mnt/user-data/outputs/Navigation_Edge.json
```

---

## Step 7: Validate (SCRIPT task)

Run cross-reference validation with auto-fix:

```bash
python3 <skill_directory>/scripts/validate_graph.py /mnt/user-data/outputs/ --fix
```

This script checks:
1. Screen ID uniqueness
2. Component ID uniqueness
3. Every `from`/`to` in Navigation edges references an existing Screen
4. Every `source_component` in Navigation edges references an existing Component
5. Every `parent`/`child` in Containment edges references an existing node
6. Every Screen has at least one Containment edge
7. All required fields are present
8. Fuzzy-matches mistyped IDs and auto-fixes them when `--fix` is passed

**If errors remain after auto-fix**, read the validation report and manually correct the issues.
Common fixes:
- A `source_component` ID that doesn't match → look up the correct ID in Component.json
- A Screen with no containment edge → check if `layout_ref` is correct

After fixing, re-run validation until it passes clean.

### Present a summary

After validation passes, present to the user:
- Total Screens (by type breakdown)
- Total Components
- Total Containment edges
- Total Navigation edges
- Any notable findings (orphan screens, deeply nested layouts, etc.)

---

## Handling large projects

For projects with >20 screens or >50 layouts:
1. The layout parser script handles any number of files automatically.
2. For Screen extraction (Step 3), process in batches by package/module.
3. For Navigation extraction (Step 5), process one screen at a time, always referencing
   the component ID list from Step 4.
4. If the project is too large for one session, process module by module and merge JSON arrays.

---

## Common pitfalls

- **ViewBinding**: `ActivityMainBinding.inflate(...)` → layout is `activity_main.xml`.
- **Kotlin synthetics** (deprecated): `import kotlinx.android.synthetic.main.activity_main.*` → `activity_main.xml`.
- **Custom base classes**: `LoginActivity extends BaseActivity extends AppCompatActivity` — BaseActivity is NOT a screen; LoginActivity IS.
- **Custom Views**: `<com.app.widget.AvatarView>` → `is_custom_view: true`. Don't expand internal layout.
- **RecyclerView items**: Adapter references `R.layout.item_xxx`. Include in Component.json; containment edge `source: "dynamic"`.
- **Fragments in ViewPager**: Each Fragment page is a separate Screen. Navigation mechanism: `"FragmentTransaction"`.
- **Style expansion**: Do NOT expand style attributes. Only record what is explicitly in the XML plus the style reference.
- **Multi-module R classes**: `com.app.feature.R.layout.xxx` vs `com.app.R.layout.xxx` — the layout name is the same; match by name not by full R path.
- **Abstract fragments**: `abstract class BaseListFragment<T> : Fragment()` is NOT a screen. Only concrete subclasses with layouts are screens.


---

## See Also

- [arkts-ui-coverage-auditor](../arkts-ui-coverage-auditor/SKILL.md) — 用本 skill 产出做对账（本 skill 漏识别二三层会拖累其表现，详见 Step 3 二三层来源清单）
- [android-ui-graph-query](../android-ui-graph-query/SKILL.md) — 同 graph 三件套（本 skill 建图，query 查图）
