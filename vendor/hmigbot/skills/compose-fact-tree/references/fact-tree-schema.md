# `toolkit-fact-tree.json` Schema v1

本文档是 `spec/toolkit-fact-tree.json` 的**唯一事实来源（SSOT）**。所有写入方（`toolkit-fact-indexer` skill）和读取方（a2h-spec、app-relationship-tree、人工）都按本 schema 解析。

---

## 一、定位

把 [harmony-migration-toolkit](https://github.com/Junkang123456/harmony-migration-toolkit) 的产物加工成一份「Android 端事实树」：

- 每个 Page / Fragment / Dialog 包含哪些 Component（flat list + parent_id 邻接表）
- 每个 Component 是什么类型、用途是什么、点了去哪
- 完整的页面流转图（flow_graph）+ toolkit 自动生成的 17 个 feature 分组

```
toolkit bundle ─→ [toolkit-fact-indexer] ─→ spec/toolkit-fact-tree.json
                  Python 脚本 + LLM 补 purpose       │
                                                    ├─→ a2h-spec Phase 0.5
                                                    └─→ app-relationship-tree Phase 4D
                                                        （二者 schema 1:1 兼容）
```

**v1 schema 设计原则**：
- Schema 必须 1:1 兼容 app-relationship-tree Phase 4D 的现有读取契约（不让下游改逻辑）
- 组件保持 **flat list** + 用 `parent_id` 表示父子关系（不递归 tree — 否则下游 4D 字段映射会崩）
- 顶层保留 `flow_graph` 与 `features`（4D 用 flow_graph 找强连通子图聚类）
- **`purpose` 字段（page-level 和 component-level）全部为 null**——v1.1 起 LLM 补 purpose 移交 app-relationship-tree，本 schema 的 fact-indexer 责任范围只覆盖结构事实

---

## 二、文件位置

- **最终产物**: `spec/toolkit-fact-tree.json`
- **中间产物**（脚本写、LLM 读）:
  - `spec/.cache/fact-tree/draft.json`（脚本初产，purpose 全 null）
  - `spec/.cache/fact-tree/source-index.json`（每个 component 的源锚点）

---

## 三、顶层结构

```jsonc
{
  "$schema_version": 1,
  "source":     { ... },             // 数据溯源 + toolkit_refs 外链
  "app":        { ... },             // 应用元信息
  "features":   [ ... ],             // toolkit 自动生成的 17 个 feature 分组
  "pages":      [ ... ],             // Activity 级
  "fragments":  [ ... ],             // Fragment / 嵌套 UI 容器（含 toolkit 漏的兜底）
  "dialogs":    [ ... ],             // Dialog / DialogFragment / BottomSheet
  "flow_graph": { ... },             // 完整页面流转图（顶层聚合）
  "dependency_graph": { ... } | null,  // 架构层级映射（由 app-relationship-tree 补；fact-indexer 不产）
  "stats":      { ... }              // 自检统计
}
```

`$schema_version` 当前为 `1`（与 app-relationship-tree Phase 4D 的 `assert fact["$schema_version"] == 1` 兼容）。schema 不向后兼容地变更时递增。

---

## 四、`source` — 数据溯源 + 外链

```jsonc
{
  "toolkit": "harmony-migration-toolkit",
  "toolkit_bundle_path": "/abs/path/to/harmony_migration_out/agent_bundle.v1.json",
  "toolkit_schema_version": "1.0",
  "generated_at": "2026-05-14T15:23:11Z",
  "android_root": "/abs/path/to/android/project",
  "generator": {
    "skill": "toolkit-fact-indexer",
    "script_version": "1.0.0"
  },
  "toolkit_refs": {
    "feature_tree":         "intermediate/5_feature_tree/feature_tree.v1.json",
    "navigation_graph":     "intermediate/0_android_facts/navigation_graph.json",
    "ui_paths":             "intermediate/0_android_facts/ui_paths.json",
    "ui_paths_enumerated":  "intermediate/0_android_facts/ui_paths_enumerated.json",
    "specs_dir":            "intermediate/0_android_facts/specs/",
    "harmony_arch":         "intermediate/3_harmony_arch/harmony_arch.v1.json",
    "android_facts":        "intermediate/1_android_facts/android_facts.v1.json"
  }
}
```

`toolkit_refs.*` 是相对 `toolkit_bundle_path` 父目录的相对路径。下游想要详细数据（如 156 条 ui_paths）直接读这些文件，不要让 fact-tree 复制内容。

---

## 五、`app` — 应用元信息

```jsonc
{
  "package": "com.example.app",
  "label": "DemoApp",
  "launcher_activity": "com.example.app.MainActivity",
  "launcher_short": "MainActivity",
  "min_sdk": 21,
  "target_sdk": 33,
  "version_name": "1.2.3"
}
```

> ⚠️ toolkit 当前 manifest 解析只给 launcher，其余可能为空。

---

## 六、`features[i]` — toolkit 自动生成的功能分组

```jsonc
{
  "id": "generated.mine.about",
  "label": "Mine About App",
  "screens": ["AboutUsActivity", "MineActivity", "MineFragment"],
  "top_tokens": ["mine", "about", "app"],
  "strategy": "deterministic_token_graph_clustering"
}
```

**注意**：这些是 toolkit 按命名 token 聚类的，**不是业务功能**。app-relationship-tree 4D Step 4D.4 把 features 当成"初始聚类提示"再 LLM 二次重命名为业务功能。

---

## 七、`pages[i]` / `fragments[i]` / `dialogs[i]` — 三类节点共享 schema

```jsonc
{
  // ── 标识 ──
  "id": "MainActivity",
  "type": "Activity",
  "fq_class": "com.example.app.MainActivity",
  "package": "com.example.app",

  // ── 描述 ──
  "label": "首页",
  "purpose": "应用主入口，承载底部导航和 Feed 信息流",   // LLM 必填一句中文
  "uncertain": false,

  // ── 文件锚点 ──
  "android_file": "app/src/main/java/com/example/app/MainActivity.kt",
  "layout_file": "app/src/main/res/layout/activity_main.xml",
  "harmony_target": "pages/mainactivity/Index",
  "logical_feature_id": "generated.home.foo",

  // ── 嵌套与触发关系 ──
  "contains": ["HomeFragment", "FeedFragment"],
  "shows_dialogs": ["LogoutConfirmDialog"],

  // ── 组件清单（flat list + parent_id 邻接表）──
  "components": [ <Component>, ... ],

  // ── 页面级导航 ──
  "navigation": {
    "inbound":  [ <NavEntry>, ... ],
    "outbound": [ <NavEntry>, ... ]
  },

  // ── reach_paths（来自 toolkit ui_paths / ui_paths_enumerated，不重新 BFS）──
  "reach_paths": [
    {
      "display": "Splash > Runtime Entry > Home",   // 人类可读链路
      "depth": 1,                                    // 链路长度（segments 数 - 1）
      "source": "ui_paths_enumerated.json",         // ui_paths.json | ui_paths_enumerated.json
      "ref": null                                    // 如来自 ui_paths.json，则为 path_id（可回查完整 segments）
    },
    {
      "display": "App > Runtime Entry > Home > Limitcampaign",
      "depth": 3,
      "source": "ui_paths.json",
      "ref": "path:ea8c4d11b9bab9300001"
    }
  ],

  // ── 人工备注（fact-indexer 不写；用户/下游 LLM 填）──
  "notes": null
}
```

### `Component`

```jsonc
{
  // ── 标识 ──
  "id": "btn_login",
  "type": "Button",
  "parent_id": "ll_root",                // 父组件 id；null 表示页面根
  "uncertain": false,

  // ── 静态属性 ──
  "text": "登录",
  "hint": null,                          // EditText placeholder（android:hint）
  "image_resource": null,                // android:src / drawableStart
  "content_desc": null,                  // android:contentDescription
  "on_click_attr": null,                 // android:onClick="xxx"（XML 静态）
  "is_interactive": true,
  "visibility": "visible",               // visible | invisible | gone | always

  // ── 触发形式聚合 ──
  "triggers": ["click", "long_press"],   // 聚合自 behaviors[].event/method + navigation.trigger

  // ── LLM 必填 ──
  "purpose": "触发登录流程，弹出登录页",

  // ── 行为 ──
  "action": null,
  "navigation": {
    "to_page": "LoginActivity",
    "trigger": "click",
    "params": { "from": "main" },
    "is_dynamic": false
  },

  // ── 条件可见性 ──
  "visible_when": null,

  // ── 列表 / 容器子项 ──
  "items": null,                         // RecyclerView/ListView/Grid/Swiper 子项；待 adapter 源码扫

  // ── 行为锚点 ──
  "behaviors": [
    { "event": "click", "method": "setOnClickListener",
      "file": "...kt", "line": 91, "enclosing_fn": "override fun initListener()" }
  ],

  // ── 源码锚点（脚本填，LLM 不可改）──
  "source_anchor": {
    "file": "app/src/main/res/layout/activity_main.xml",
    "line": 42
  },

  // ── 人工备注（fact-indexer 不写；记录 toolkit 解不出 / 易踩坑的 trigger 等）──
  "notes": null
}
```

### `NavEntry`（pages[].navigation.inbound / outbound 元素）

```jsonc
{
  "from": "SplashActivity",              // outbound 此字段为 to
  "via_component": "btn_login",
  "trigger": "click",
  "params": { ... },
  "is_dynamic": false
}
```

---

## 八、`flow_graph` — 完整流转图（顶层聚合）

```jsonc
{
  "nodes": [
    { "id": "MainActivity", "type": "Activity", "label": "首页" }
  ],
  "edges": [
    {
      "from": "MainActivity",
      "to": "LoginActivity",
      "via_component": "btn_login",
      "trigger": "click",
      "is_dynamic": false
    }
  ]
}
```

`edges` 必须与所有 `pages/fragments/dialogs[].navigation.outbound` 总和一一对应（数量相等）。

---

## 九、`dependency_graph` — 架构层级映射（由 app-relationship-tree 补）

fact-indexer 产出时此字段为 `null` 或缺失。`app-relationship-tree` Phase 4 跑完后会用 LLM 推断 toolkit 17 个 feature 各自属于哪个架构层，写到这里：

```jsonc
"dependency_graph": {
  "layers": [
    { "layer": 0, "name": "Foundation", "features": ["generated.splash.app", "generated.launch.agreement"] },
    { "layer": 1, "name": "Auth",       "features": ["generated.app.src"] },
    { "layer": 2, "name": "Monetize",   "features": ["generated.member.center", "generated.home.renew"] },
    { "layer": 3, "name": "Core AI",    "features": ["generated.choice.ppttemplate", "generated.works.app"] },
    { "layer": 4, "name": "Extended",   "features": ["generated.video.play", "generated.web.app"] },
    { "layer": 5, "name": "Shell",      "features": ["generated.mine.about"] }
  ]
}
```

**约束**：
- 每个 `features[*].id` 必须出现在某 `layers[*].features` 里（覆盖完整）
- 同一 feature 不能在两层（互斥）
- layer 编号严格递增 0-5，name 字段固定为 6 个值之一

下游用途：
- visual-verify 排序：先 Foundation 层 page 验证 → 再 Shell；Foundation 失败不浪费时间往后跑
- a2h-spec / a2h-plan 用于排执行批次

---

## 十、`stats`

```jsonc
{
  "total_pages": 25,
  "total_fragments": 7,
  "total_dialogs": 4,
  "total_components": 380,
  "total_navigation_edges": 56,
  "total_features": 17,
  "llm_filled_purposes": 380,
  "uncertain_items": 3,
  "dynamic_targets": 2,
  "fragments_promoted_from_specs": 13,
  "components_with_parent": 230
}
```

---

## 十一、字段填写责任划分

| 字段 | 脚本 | LLM | 说明 |
|---|---|---|---|
| `source.*` 含 `toolkit_refs` | ✅ | — | 完全确定性 |
| `app.*` | ✅ | 🟡 label 缺失兜底 | manifest 直取 |
| `features[]` | ✅ | — | toolkit feature_tree 抄 |
| `pages/fragments/dialogs[].id / type / fq_class / package` | ✅ | — | toolkit 直给 |
| `pages[].label` | 🟡 | LLM 兜底 | 都没有则 null |
| `pages[].purpose` | — | ⏭️ **由 app-relationship-tree 补**（fact-indexer 范围内为 null）| 移交下游 |
| `pages[].android_file / layout_file / harmony_target` | ✅ | — | toolkit |
| `pages[].contains / shows_dialogs` | ✅ | — | 直给 |
| `components[]` 骨架 | ✅ | — | spec / XML |
| `components[].id / type / parent_id / source_anchor` | ✅ | — | 完全确定性 |
| `components[].text / image_resource / content_desc / visibility` | ✅ | — | XML / spec |
| `components[].hint` | ✅ | — | XML `android:hint`（EditText placeholder） |
| `components[].on_click_attr` | ✅ | — | XML `android:onClick=""` 静态属性 |
| `components[].triggers[]` | ✅ | — | **聚合**自 behaviors event/method + navigation.trigger，如 `["click", "long_press"]` |
| `components[].purpose` | — | ⏭️ **由 app-relationship-tree 补**（fact-indexer 范围内为 null）| 移交下游 |
| `components[].navigation.*` | ✅ | — | nav_graph |
| `components[].action` | 🟡 | ✅ 增强 | 缺则 null |
| `components[].visible_when` | 🟡 | 🟡 | 否则 null |
| `components[].items[]` | 🟡 | — | 多数 null |
| `components[].behaviors[]` | ✅ | — | spec / source_findings |
| `pages[].navigation.inbound/outbound` | ✅ | — | 聚合 |
| `pages[].reach_paths[]` | ✅ | — | **从 toolkit ui_paths.json + ui_paths_enumerated.json 反查（不自己 BFS）** |
| `dependency_graph.layers` | — | ⏭️ **由 app-relationship-tree Phase 4 补**（fact-indexer 范围内为 null）| LLM 把 features 归到 6 个架构层 |
| `pages[].notes` / `components[].notes` | — | 🟡 用户/下游 LLM 写 | fact-indexer 初始化为 null，**不读不写** |
| `flow_graph` | ✅ | — | 聚合 |
| `stats` | ✅ | — | 脚本自动 |

**v1.1 起的铁律**：
- 本 schema 由 **toolkit-fact-indexer 纯确定性脚本**填充结构性字段
- `purpose` / `label` / `action` / `visible_when` / `items[].purpose` 字段全部为 null（**不是 fact-indexer 的责任**）
- 这些字段由 **app-relationship-tree Phase 4.5.B** 一次性 LLM 读源码 + page_spec 补
- fact-indexer 写完即终止；不要把任何 LLM 调用嵌进 fact-indexer

---

## 十二、自检脚本（结构性事实层 7 项，必跑且不可放宽）

v1.1 起 fact-indexer 的自检**只查结构性事实**——purpose / description 字段不在自检范围（那是 app-relationship-tree 自己自检的事）。但**结构性事实层每一项都必须 HARD-PASS，不接受任何放宽**。

```bash
F="spec/toolkit-fact-tree.json"

# 1. schema_version
jq -e '."$schema_version" == 1' "$F" >/dev/null || echo "❌ schema_version 不为 1"

# 2. 必填顶层字段（8 项）
for k in source app features pages fragments dialogs flow_graph stats; do
  jq -e "has(\"$k\")" "$F" >/dev/null || echo "❌ 缺顶层字段 $k"
done

# 3. pages/fragments/dialogs id 唯一
jq -r '(.pages + .fragments + .dialogs)[].id' "$F" | sort | uniq -d \
  | while read dup; do echo "❌ id 冲突: $dup"; done

# 4. 所有 navigation.to_page 必须可达（或 is_dynamic=true）
ALL_IDS=$(jq -r '(.pages + .fragments + .dialogs)[].id' "$F" | sort -u)
jq -r '(.pages + .fragments + .dialogs)[].components[] | select(.navigation != null and .navigation.is_dynamic == false) | .navigation.to_page' "$F" \
  | while read t; do
      grep -qFx "$t" <<< "$ALL_IDS" || echo "❌ 未知 navigation target: $t"
    done

# 5. component.parent_id 闭合（指向同 page 内存在的 id 或 null）
python3 -c "
import json, sys
data = json.load(open('$F'))
errors = []
for r in (data.get('pages', []) + data.get('fragments', []) + data.get('dialogs', [])):
    comp_ids = {c['id'] for c in r.get('components', [])}
    for c in r.get('components', []):
        pid = c.get('parent_id')
        if pid is not None and pid not in comp_ids:
            errors.append(f\"❌ {r['id']}.{c['id']}.parent_id={pid} 不存在\")
for e in errors[:10]: print(e)
"

# 6. flow_graph.edges 数量 == 所有 outbound 总和
EXPECT=$(jq '[(.pages + .fragments + .dialogs)[].navigation.outbound | length] | add' "$F")
ACTUAL=$(jq '.flow_graph.edges | length' "$F")
[[ "$EXPECT" == "$ACTUAL" ]] || echo "❌ flow_graph.edges 数量不匹配 ($ACTUAL vs $EXPECT)"

# 7. stats 一致
jq -e '.stats.total_pages == (.pages | length)' "$F" >/dev/null || echo "❌ stats.total_pages 不一致"
jq -e '.stats.total_fragments == (.fragments | length)' "$F" >/dev/null || echo "❌ stats.total_fragments 不一致"
jq -e '.stats.total_dialogs == (.dialogs | length)' "$F" >/dev/null || echo "❌ stats.total_dialogs 不一致"
jq -e '.stats.total_features == (.features | length)' "$F" >/dev/null || echo "❌ stats.total_features 不一致"

# 8. reach_paths 必须是 list（可空数组，但字段必须存在；toolkit 未覆盖时 []）
jq -e '[(.pages + .fragments + .dialogs)[] | select(.reach_paths == null)] | length == 0' "$F" >/dev/null \
  || echo "❌ 有 record.reach_paths == null（应是空数组 [] 而非 null）"
```

任一 ❌ → fact-tree 视为不合格，必须修正后才能交给下游。**结构性事实不允许残缺**。

> **不在 fact-indexer 自检范围**（由 app-relationship-tree 自检）：
> - 所有 page/fragment/dialog 的 `purpose` 是否填齐
> - 所有 components 的 `purpose` 是否填齐
> - sub_components 的 `description` 是否填齐
>
> 这些项在 fact-indexer 输出时**预期全为 null**。app-relationship-tree Phase 4.5.B 跑完后会在自己的自检里检查。

---

## 十三、`uncertain` 字段约定

| toolkit 来源 | 在 fact-tree 表现 |
|---|---|
| `framework_map.gap_items[]` 命中该 screen | `pages[i].uncertain: true` |
| 动态 navigation 无法解析 | `components[i].navigation.is_dynamic: true` + `uncertain: true` |
| 多模态扫不到的资源 / 缺失 layout 文件 | `pages[i].uncertain: true` + `layout_file: null` |
| Fragment 兜底但 grep 找不到 class | `fragments[i].fq_class: null` + `uncertain: true` |

下游消费时 `uncertain: true` 字段**仅作参考**，必要时回查 toolkit 原产物。

---

## 十四、与 app-relationship-tree Phase 4D 的契约（必读）

```python
sc = {
    "name":        fc["id"],
    "type":        _map_android_to_arkui_type(fc["type"]),
    "description": fc["purpose"],     # 必须非 null（schema §十一 检查 4 保证）
}
if fc.get("navigation"):
    sc["trigger"] = fc["navigation"]["trigger"]
    sc["target"]  = fc["navigation"]["to_page"]
    if fc["navigation"].get("is_dynamic"):
        sc["target"] = f"dynamic({fc['navigation']['to_page']})"
elif fc.get("action"):
    sc["action"] = fc["action"]
if fc.get("visible_when"):
    sc["visible_when"] = fc["visible_when"]
if fc.get("items"):
    sc["items"] = [...]
```

4D Step 4D.4 用 `fact.flow_graph` 找强连通子图做 feature 聚类——所以 `flow_graph` 是顶层必备。

**v1 起的设计约束**：任何破坏性 schema 变更必须先开 issue 通知 a2h-spec / app-relationship-tree 两个下游 skill 维护者。
