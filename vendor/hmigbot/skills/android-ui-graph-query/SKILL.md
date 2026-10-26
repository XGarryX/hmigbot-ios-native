---
name: android-ui-graph-query
description: Query an Android UI graph (produced by android-ui-graph-builder) to retrieve migration context for Android→HarmonyOS UI work. Given a screen, returns its full component tree, attributes, navigation edges, and resource inventory; given a component, returns its children, parent chain, siblings, and attributes — all sourced from the four JSON graph files (Screen.json, Component.json, Navigation_Edge.json, Containment_Edge.json). Use whenever the user asks to query, look up, inspect, or retrieve information from an Android UI graph for migration ("迁移上下文", "查询界面/组件", "what does this screen contain", "what navigates to this screen"). This is the retrieval counterpart to android-ui-graph-builder — run the builder first to create the graph; this skill only queries an existing one.
metadata:
  type: domain
  domain: migration
  tags:
  - migration
  - android
  - ui-graph
  - query
---
# Android UI Graph Query — Migration Context Retrieval

This skill queries the Android UI graph (four JSON files) to extract complete context
for migrating Android UI code to HarmonyOS ArkUI. It provides two primary entry points:

1. **Screen-level**: "I need to migrate LoginActivity" → retrieves everything about that screen
2. **Component-level**: "I need to migrate this RecyclerView" → retrieves everything about that component

The core value: instead of the LLM reading raw JSON files and risk missing relationships,
this skill uses a Python query engine with pre-built indexes to guarantee complete and
accurate context extraction.

> **ArkTS 装饰器策略（V2 优先 + V1 兼容查找）**：本 skill 输出的迁移上下文用于生成 ArkTS 代码。**新代码默认 ArkTS V2 装饰器**（`@ComponentV2 / @Local / @Param + @Once / @Event / @Provider() / @Consumer() / @ObservedV2 + @Trace / @Monitor / AppStorageV2.connect / PersistenceV2.globalConnect`（页面子树共享用 `@Provider`/`@Consumer`，无 LocalStorageV2；API 12+ 推荐））；老项目按需用 V1 等价（`@Component / @State / @Prop / @Link / @Provide / @Consume / @Observed + @ObjectLink / @Watch / @StorageLink / PersistentStorage.persistProp`）。当 grep 检测下游 ArkTS 代码或解析迁移结果时，建议用 **V1+V2 兼容模式**，例如：`grep -E '@Component(V2)?\b'`、`grep -E '@State|@Local'`、`grep -E '@Prop|@Param'`、`grep -E '@StorageLink|AppStorageV2'`。详细映射查 `arkts-state-manager/SKILL.md` 与 `arkts-state-manager/references/v2-decorators.md`。

---

## Prerequisites

The four graph JSON files must exist (produced by `android-ui-graph-builder`):
- `Screen.json`
- `Component.json`
- `Navigation_Edge.json`
- `Containment_Edge.json`

These can be in any directory. The user will specify or the LLM will locate them.

---

## When to use

Use this skill whenever the user:
- Asks to migrate a specific Android screen or component to HarmonyOS
- Wants to see the component tree / hierarchy of a screen
- Asks "what components does XxxActivity contain?"
- Asks "what navigates to/from this screen?"
- Asks "what are the attributes of this component?"
- Asks "show me the full context for migrating screen X"
- Wants to understand relationships between screens and components before writing ArkUI code

---

## Quick reference: available query commands

| Command | Input | What it returns |
|---------|-------|-----------------|
| `migration_context` | Screen name or ID | **COMPLETE** migration context: screen metadata, full component tree with all attributes, navigation in/out, resource inventory, layout summary, host/child screen info |
| `migration_component` | Component ID or android_id | **COMPLETE** component context: all attributes, children subtree, parent chain, siblings, resources, triggered navigations |
| `screen` | Screen name or ID | Screen metadata + root components + navigation summary |
| `component` | Component ID or android_id | Component attributes + direct children + parent chain + siblings |
| `screen_list` | (none) | All screens with type, layout, nav counts |
| `component_list` | Screen name or ID | Flat list of all components in a screen |
| `tree` | Screen name or ID | Visual indented component tree |
| `navigation` | Screen name or ID | All navigation edges from/to a screen |
| `search` | Keyword | Search across all nodes by name, class, ID |

---

## Workflow

### Step 1: Read references

Before querying, read the mapping reference to understand how Android concepts map to HarmonyOS:

```bash
view <skill_directory>/references/android-to-harmonyOS-ui-layout-mapping-reference.md
view <skill_directory>/references/android-to-harmonyOS-ui-atomic-component-mapping-reference.md
view <skill_directory>/references/android-to-harmonyOS-ui-interaction-mapping-reference.md
view <skill_directory>/references/ui-migration-pitfalls.md
```

These files contain the Android→HarmonyOS mapping for layouts, widgets, interactions, and known migration pitfalls —
essential for interpreting query results in a migration context.

### Step 2: Locate the graph files

Find where the four JSON files are stored:

```bash
# Common locations
ls /mnt/user-data/outputs/Screen.json 2>/dev/null
ls /mnt/user-data/uploads/Screen.json 2>/dev/null
# Or ask the user for the directory
```

Set `GRAPH_DIR` to the directory containing all four files.

### Step 3: Get the big picture

Start with an overview of the entire project:

```bash
python3 <skill_directory>/scripts/query_graph.py $GRAPH_DIR screen_list
```

This returns all screens with their types, layout references, component counts, and
navigation edge counts. Use this to understand the project scope and help the user
choose what to migrate.

### Step 4: Query based on user intent

#### 4A: Screen-level migration (most common)

When the user says "migrate LoginActivity" or "转换登录界面":

```bash
python3 <skill_directory>/scripts/query_graph.py $GRAPH_DIR migration_context LoginActivity
```

This returns a comprehensive JSON containing:

- **`screen`**: Full screen metadata (type, theme, lifecycle, manifest config, etc.)
- **`layout_summary`**: Root container type, max depth, component counts by type,
  whether ConstraintLayout/RecyclerView/include/fragment/dynamic content is used
- **`component_tree`**: EVERY component with ALL attributes (layout, style, behavior,
  accessibility), plus tree structure info (parent, order, depth, containment source)
- **`resource_inventory`**: All unique resources (drawables, colors, strings, dimens)
  used by this screen, with which components reference each resource
- **`navigation.outgoing`**: Where this screen can navigate to (with trigger descriptions)
- **`navigation.incoming`**: Where users come from to reach this screen
- **`host_activity`**: If this is a Fragment/Dialog, which Activity hosts it
- **`child_screens`**: If this is an Activity, which Fragments/Dialogs it hosts

**How to use this for migration:**

1. Look at `layout_summary.root_container` → decide the top-level ArkUI container
   (e.g., ConstraintLayout → RelativeContainer or Column/Row composition)
2. Walk `component_tree` in order → translate each component using the mapping reference
3. Preserve the `_tree_info.parent_id` and `_tree_info.order` to maintain hierarchy
4. Use `resource_inventory` to know which resources need to be migrated
5. Use `navigation.outgoing` to write the equivalent `router.pushUrl()` calls
6. Check `screen.lifecycle_callbacks` for lifecycle-specific logic to migrate

#### 4B: Component-level migration

When the user says "migrate this RecyclerView" or "转换这个列表组件":

```bash
python3 <skill_directory>/scripts/query_graph.py $GRAPH_DIR migration_component rv_list
```

(accepts component ID, android_id, or partial match)

This returns:

- **`component`**: Full component attributes
- **`children_tree`**: All descendant components with their attributes
- **`parent_context`**: The chain from this component up to the screen root,
  with each parent's layout attributes (critical for understanding how this
  component is positioned)
- **`sibling_context`**: Other components at the same level (important for
  understanding the visual context — what's next to this component)
- **`resource_inventory`**: Resources used by this component and its descendants
- **`triggered_navigations`**: Any navigation edges triggered by clicking this component

**How to use this for migration:**

1. Look at `component.class_short` → find the ArkUI equivalent in the mapping reference
2. Translate `component.layout_attrs` → ArkUI modifiers (.width, .height, .margin, etc.)
3. Translate `component.style_attrs` → ArkUI visual modifiers (.backgroundColor, .fontSize, etc.)
4. Look at `parent_context` → understand layout constraints from parent containers
5. If the component is a container, walk `children_tree` to translate children
6. Check `triggered_navigations` for any navigation logic to migrate

#### 4C: Visual tree inspection

To quickly understand a screen's structure:

```bash
python3 <skill_directory>/scripts/query_graph.py $GRAPH_DIR tree HomeActivity
```

This prints an indented tree to stderr (human-readable) like:
```
📱 HomeActivity (Activity)
  └── CoordinatorLayout #root
      ├── AppBarLayout #appbar
      │   └── MaterialToolbar #toolbar
      ├── FrameLayout #content
      │   └── RecyclerView #rv_list
      └── FloatingActionButton #fab
```

Use this to quickly grasp the layout structure before diving into detailed attributes.

#### 4D: Navigation flow analysis

To understand all navigation around a screen:

```bash
python3 <skill_directory>/scripts/query_graph.py $GRAPH_DIR navigation HomeActivity
```

Returns incoming and outgoing edges with trigger descriptions, mechanisms, extras, and conditions.

#### 4E: Search

To find components or screens by keyword:

```bash
python3 <skill_directory>/scripts/query_graph.py $GRAPH_DIR search RecyclerView
python3 <skill_directory>/scripts/query_graph.py $GRAPH_DIR search btn_login
python3 <skill_directory>/scripts/query_graph.py $GRAPH_DIR search activity_home
```

### Step 5: Present context to user or feed to migration

After querying, present the results in one of two ways:

**For human review**: Summarize the key findings in natural language, highlighting:
- Screen type and its HarmonyOS equivalent
- Root container and recommended ArkUI layout approach
- Key components that need special migration attention (RecyclerView, custom views, etc.)
- Navigation logic that needs router setup
- Resources that need to be migrated

**For code generation**: Feed the full JSON result into the code generation context.
The `migration_context` output is designed to be self-contained — it has everything
needed to write the HarmonyOS ArkUI equivalent without going back to the original source.

---

## Multiple screens migration

When migrating an entire project or module:

1. Run `screen_list` to get all screens
2. Identify migration order: start with screens that have no incoming navigation (entry points)
3. For each screen, run `migration_context`
4. Migrate screens in dependency order (migrate screens that are navigated TO before
   screens that navigate TO them, so router targets exist first)

```bash
# Get all screens sorted by dependency
python3 <skill_directory>/scripts/query_graph.py $GRAPH_DIR screen_list
```

---

## Interpreting "unknown" values

When query results contain `"unknown"` for an attribute:
- It means the attribute was not explicitly set in the Android XML
- For migration: this typically means the Android system default applies
- In HarmonyOS: you can usually omit the corresponding modifier (ArkUI defaults will apply)
- Exception: if the component looks wrong without explicit values, check the Android default
  for that component type and set it explicitly in ArkUI

---

## Tips for effective querying

1. **Start with `tree`** to get a visual overview before diving into details
2. **Use `migration_context` for full screens** — it's the most comprehensive query
3. **Use `migration_component` for complex widgets** like RecyclerView, custom views
4. **The `resource_inventory`** tells you exactly which drawables/colors/strings to migrate
5. **Check `layout_summary.constraint_layout_used`** — ConstraintLayout→ArkUI conversion
   is the most complex mapping and may need manual layout restructuring
6. **Parent context matters**: a Button inside a LinearLayout (→ Row/Column child) behaves
   differently from a Button inside a ConstraintLayout (→ RelativeContainer anchor)


---

## See Also

- [android-ui-graph-builder](../android-ui-graph-builder/SKILL.md) — 同 graph 三件套（builder 建图，本 skill 查图）
- [arkts-ui-coverage-auditor](../arkts-ui-coverage-auditor/SKILL.md) — 同 graph 三件套（用 builder 产物做对账）
