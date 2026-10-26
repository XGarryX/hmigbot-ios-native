# Schema Reference — iOS UI Graph (v2.0)

Keep the four original graph files, canonical IDs, required fields and relationship checks. These are static analysis records, not a device hierarchy. Unknown facts remain `"unknown"`, absent explicit identity is `"none"`, empty collections are `{}` / `[]`. Do not infer runtime bounds or SDK availability from a graph.

## 1. Screen Node → Screen.json

The root is an array of objects. Preserve every required field below.

| Field | Type | Native source meaning |
|---|---|---|
| `id` | string | `screen:{module.Type}`; stable across the four files |
| `type` | string | `App`, `Scene`, `UIViewController`, `SwiftUIView`, `Dialog`, `Sheet`, or `PopupWindow` (normalized presentation category) |
| `name` | string | Actual declared type or evidence-backed presentation name |
| `package` | string | Swift module / product namespace; not a guessed bundle identifier |
| `layout_ref` | string | Actual Storyboard/XIB reference or source file / symbol; `unknown` if not available |
| `source_file` | string | Relative selected-target source path |
| `language` | string | `Swift` / `Objective-C`; unknown if unresolved |
| `theme` | string | Evidence-backed theme symbol, asset name, trait or `unknown` |
| `parent_activity` | string | Historical host-screen association key: containing Screen ID, or `none`; not a native API |
| `menu_ref` | string | SwiftUI Menu / UIKit UIMenu source anchor, or `unknown` |
| `has_options_menu` | boolean | Normalized slot: source defines a menu; do not invent a lifecycle callback |
| `has_toolbar` | boolean | Source contains toolbar / navigation bar content |
| `orientation_config` | string | `portrait` / `landscape` / `unspecified` / `unknown`, supported by plist or controller configuration |
| `config_changes` | string | Trait/size/scene response source anchor or `unknown`; not a manifest property |
| `lifecycle_callbacks` | array | Actual observed declarations/modifiers, e.g. `onAppear`, `task`, `viewDidLoad`, `scenePhase` |
| `metadata` | object | Native evidence and normalized optional slots, described below |

`metadata` may contain `native_framework`, `scene_role`, `source_anchors`, `presentation`, `launch_mode`, `exported`, `intent_filters`, `soft_input_mode`, `window_flags`, `task_affinity`. Historical optional slots have no automatic native equivalent: leave `unknown` / empty when unsupported. URL types, universal links and scene restoration must be recorded using their actual evidence; they are not interchangeable with these slots. Distinguish plist declaration, source inference and runtime observation.

## 2. Component Node → Component.json

The root is an array. A component belongs to a screen through containment edges, not its filename.

| Field | Type | Native source meaning |
|---|---|---|
| `id` | string | Canonical analysis ID; see identity rules |
| `ios_id` | string | Exact explicitly evidenced native identity value, or `none` / `unknown` |
| `class` | string | Actual qualified type, e.g. `SwiftUI.Button`, `UIKit.UIButton`; analytical groups use `analysis:semantic_region`, never a fabricated framework type |
| `class_short` | string | Actual short type name; analytical group may use `semantic_region` |
| `is_viewgroup` | boolean | Normalized slot: has a container role |
| `is_custom_view` | boolean | Source declares a custom component |
| `source_layout` | string | Relative Swift/Objective-C/Storyboard/XIB path, not a guessed resource |
| `depth` | integer | Evidenced containment depth, root 0; static depth is not runtime view depth |
| `layout_attrs` | object | Normalized layout observations, §2.1 |
| `style_attrs` | object | Normalized appearance observations, §2.2 |
| `behavior_attrs` | object | Normalized interaction observations, §2.3 |
| `accessibility_attrs` | object | Normalized accessibility observations, §2.4 |
| `resource_refs` | array | Actual resource references, §2.5 |
| `custom_attrs` | object | Native identity kind, source line, modifier order, state, constraints and analytical role |

### Identity and analysis-node rules

- Explicit identity: `comp:{source_scope}:{identity_value}`. Without it: `comp:{source_scope}:{class_short}#{stable_counter_from_1}`. Canonical analysis IDs do not assert native runtime identity.
- `ios_id` carries a string only when the source supplies that string. Record its **kind and anchor** in `custom_attrs.native_identity`: `swiftui_explicit_id`, `foreach_key`, `accessibility_identifier`, `restoration_identifier`, `ib_object_id`. Multiple identities belong in a typed `native_identities` array; state which one supplied the lookup value. Their lifetimes and semantics differ. Never treat an accessibility identifier as SwiftUI structural identity.
- Computed IDs whose runtime values are unavailable stay `unknown`; retain the source expression and state dependency separately. No explicit ID is `none`.
- Analytical grouping: `class="analysis:semantic_region"`, `custom_attrs.analysis_role`, `source_anchors`, `not_runtime_bounds=true`. It must not be named as a SwiftUI/UIKit SDK type. Regions are evidence grouping, not proof of a complete control tree.
- The formal graph contains **only `ios_id`**. The launcher adapts its field name in a disposable view for the original read-only engine. Never add a second compatibility identity key to the formal graph.

### 2.1 layout_attrs

Use relevant normalized slots only. Keep values as evidence strings; unsupported values remain unknown. Shared slots include `layout_width`, `layout_height`, `layout_margin`, `layout_padding`, `layout_gravity`, `layout_weight`, `min_width`, `min_height`, `max_width`, `max_height`, `orientation`, `gravity`, `layout_column`, `layout_column_span`, `layout_row`, `layout_row_span`, `constraints`.

These are **analysis slot names**, not claimed native property names. SwiftUI frame/min/ideal/max sizing, layoutPriority, alignment guides, safeAreaInset/ignoresSafeArea and modifier order must retain their original expressions and order under `custom_attrs`. UIKit intrinsicContentSize, hugging/compression resistance and NSLayoutConstraint equations/priority/active state belong in native constraint evidence. Do not translate one to another by name alone. Do not invent absent dimensions or use image pixels as points.

### 2.2 style_attrs

Shared normalized slots include `text`, `textColor`, `textSize`, `fontFamily`, `textStyle`, `textAlignment`, `maxLines`, `ellipsize`, `hint`, `background`, `foreground`, `alpha`, `rotation`, `scaleX`, `scaleY`, `src`, `tint`, `cornerRadius`, `strokeColor`, `strokeWidth`. Preserve native units, dynamic type, locale, color-scheme / trait variants, rendering mode and modifier order in evidence. Strings, asset names and SF Symbols are not automatically resource paths. No unsupported field is filled just to look complete.

### 2.3 behavior_attrs

Slots include `clickable`, `longClickable`, `focusable`, `enabled`, `selected`, `visibility`, `editable`, `checked`, `onClick`, `onLongClick`, `onTouch`, `onFocusChange`. They describe observed source behavior, not native APIs. Keep action/gesture/target-selector/delegate anchors, conditions, Binding/state ownership, cancellation and ForEach identity under `custom_attrs`. `hidden`, conditional absence and zero opacity differ; do not collapse them without retaining the distinction.

### 2.4 accessibility_attrs

Keep the shared keys `contentDescription`, `importantForAccessibility`, `accessibilityLiveRegion`, `accessibilityHeading`, `accessibilityTraversalBefore`, `accessibilityTraversalAfter`, `labelFor`. Use actual accessibility label/value/hint/traits/grouping/order evidence; unknown is valid. A spoken label is not an identity. Any equivalence between an announcement and live-region behavior requires explicit analysis.

### 2.5 resource_refs

Array of `{ "attr": "source_usage", "ref": "actual resource name/path", "type": "image|color|string|font|symbol|animation|other" }`. Use Asset Catalog entries, localized string keys/catalogs, bundle resources and actual font files. Preserve scales, appearances, localization and rendering metadata; do not manufacture resource namespaces.

## 3. Navigation Edge → Navigation_Edge.json

| Required field | Type | Meaning |
|---|---|---|
| `from`, `to` | string | Existing Screen IDs |
| `trigger` | string | Observable action/lifecycle condition and source anchor |
| `mechanism` | string | Actual mechanism: `NavigationStack`, `NavigationLink`, `sheet`, `fullScreenCover`, `TabView`, `pushViewController`, `present`, `segue`, `openURL`, `Other`; keep exact evidence in metadata when needed |
| `direction` | string | `forward` / `back` / `replace` / `unknown` |
| `source_component` | string | Existing Component ID or `unknown` |
| `extras` | object | Passed parameter names/types; retain optionality/ownership separately |
| `transition_anim` | string | Native transition/animation evidence or `unknown` |
| `flags` | string | Navigation-state/options evidence or `unknown`; no invented platform constants |
| `condition` | string | Evidence-backed condition or `none` |

A source declaration is not proof the edge is currently reachable. Distinguish unreachable code, a conditional presentation and a dynamic unresolved destination. Preserve return results, dismissal, cancellation, path mutation and re-entry behavior.

## 4. Containment Edge → Containment_Edge.json

Required fields: `parent` (Screen or Component ID), `child` (Component ID), `order` (0-based sibling index), `source` (normalized `direct`, `include`, `merge`, `viewstub`, `fragment_tag`, `dynamic`), `include_layout` (actual included source or `none`). Historical enum labels are wire categories only: record actual SwiftUI composition, UIKit child containment or IB relationship in native evidence. Do not invent containment for an App/Scene just to suppress an orphan warning.

## 5. Original read-only consumer boundary

`validate_graph.py GRAPH_DIR` and `query_graph.py GRAPH_DIR COMMAND [LOOKUP]` retain original checks, queries and exit codes. Each invocation stores unchanged original stdout/stderr, native display, adapter identity and formal/wire SHA-256 hashes in a sibling `_graph-adapter-evidence` directory (or `HMIGBOT_GRAPH_EVIDENCE_ROOT`, which must be outside the graph). A temporary four-file view is removed after use; the formal graph is never rewritten. Malformed input reaches the original checks. Non-native or dual identity keys are rejected rather than silently preferred. Query JSON returns `ios_id`; values and canonical IDs remain unchanged. A successful graph check is not approval of UI specifications or runtime behavior.
