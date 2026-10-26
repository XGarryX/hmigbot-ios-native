# Android View/XML To ArkUI Mapping

Use this file when translating source Android UI structures into ArkUI components.

## Page And Shell Mapping

| Android source | ArkUI target | Notes |
| --- | --- | --- |
| `Activity` | routed page or app shell page | Use for top-level destinations and window-level state. |
| `Fragment` | reusable `@ComponentV2` (V2, recommended) or `@Component` (V1) struct, or routed page | Promote to page only if it is a top-level destination. |
| `DialogFragment` / dialog class | dialog or sheet component | Keep the dialog separate from the page. Android dialogs are page-scoped; ArkUI dialogs default to window-global (stay on top after route push) — for page-level semantics see arkts-component-builder v2-dialogs-and-sheets §2c. |
| `DrawerLayout` | shell-level navigation container | Build once in the app shell, not per page. |
| `BottomNavigationView` | shell tabs or bottom navigation component | Centralize routing and tab state. |
| `FragmentContainerView` | child component slot | Use parent/child composition instead of recreating Android fragment transactions. |

## Layout Mapping

| Android source | ArkUI target | Notes |
| --- | --- | --- |
| `LinearLayout` vertical | `Column` | Prefer extracted child components over deep nesting. |
| `LinearLayout` horizontal | `Row` | |
| `FrameLayout` | `Stack` | Good for overlay content. |
| `RelativeLayout` | `Stack`, `Row`, `Column` | Restructure instead of trying to mirror each rule mechanically. |
| `ConstraintLayout` | split into smaller ArkUI components | Mechanical translation is usually fragile. |
| `NestedScrollView` / `ScrollView` | `Scroll` | Keep one main scroll owner per page when possible. |
| `SwipeRefreshLayout` | refresh wrapper or placeholder refresh action | If target refresh behavior is unclear, preserve the action path first. |
| `CoordinatorLayout` | page shell + explicit state | Do not try to reproduce Android behavior nesting blindly. |

## Layout Parameter Mapping (width / margin / padding)

The container table above maps *shapes*. It does NOT map layout *parameters*, and these do not translate literally — the box model differs between the two platforms:

- Android `LinearLayout` measures a `match_parent` child **inside** the parent's content area, then subtracts the child's `layout_margin`. Horizontal margin therefore stays *inside* the parent.
- ArkUI treats margin as **part of the component's own size** (docs: 尺寸设置.md, margin — 「在计算位置时外边距视为组件大小的一部分」；「在Row、Column、Flex交叉轴上布局时，子组件交叉轴的大小与margin的和为整体」). So `width('100%')` + horizontal `margin` = `100% + left + right`, which **overflows the parent** (docs: width — 「若子组件的宽大于父组件的宽，则会超出父组件的范围」). The compiler does NOT flag this; it silently renders wrong.

The two platforms are semantically opposite here, so literal translation is a bug. Map by parameter:

| Android layout parameter | Correct ArkUI mapping | Notes |
| --- | --- | --- |
| `layout_width="match_parent"` (no horizontal margin) | `.width('100%')` | Safe only when there is no left/right/start/end margin on the same child. |
| `layout_width="match_parent"` + `layout_marginLeft/Right` (or 四向 `layout_margin` shorthand) | move horizontal spacing onto the **parent's `.padding({ left, right })`**, child stays `.width('100%')` with **no horizontal margin**; OR keep the child's `.width('calc(100% - <ML+MR>vp)')` (API 10+) | Do NOT keep `.width('100%')` and horizontal `.margin(...)` on the same attribute chain. `.margin(N)` (Length shorthand) counts as horizontal too — it applies to all four sides. |
| fixed `layout_width="360dp"` + horizontal `layout_marginLeft/Right` | prefer a relative/adaptive width (`.width('100%')` minus parent padding, or `.constraintSize({ maxWidth: '100%' })`), NOT a hardcoded `.width(360)` + `.margin({ left, right })` | A fixed dp width plus side margin overflows narrow screens (360 + 20 + 20 = 400vp on a ~360vp parent). |
| `layout_marginTop` / `layout_marginBottom` (vertical) | **keep as-is** — `.margin({ top, bottom })` | Vertical margin is along the main axis; it does not overflow the cross axis. NEVER convert vertical margin into padding; keep the vertical spacing exactly. |
| `layout_marginStart` / `layout_marginEnd` (RTL-aware) | `LocalizedMargin` via `LengthMetrics` (needs `import { LengthMetrics } from '@kit.ArkUI'`) | Same overflow rule applies: do not pair with `width('100%')`; sink into parent padding when the child is full-width. |
| parent horizontal `padding` + child horizontal `margin` | combine both into the **parent's `.padding`** (parent 24 + child 8 → parent `.padding({ left: 32, right: 32 })`), child `.width('100%')` with no horizontal margin | The parent padding already narrows the content area; adding child horizontal margin on top of `width('100%')` overflows again. Preserve the vertical stacking (parent top/bottom padding + child marginTop) as-is. |
| nested `match_parent` at every level | apply the rule at **each nesting level** independently | Each level's full-width child must not carry horizontal margin; sink each level's horizontal spacing into that level's parent padding (or calc). The overflow compounds per level if translated literally. |

`calc` syntax (docs: 尺寸设置.md — calc 从 API version 10 起支持，运算符与数值之间需要使用空格隔开): operators MUST be space-separated, e.g. `.width('calc(100% - 32vp)')`. Missing spaces is a runtime/parse error.

### Worked example — match_parent + horizontal margin

Android source:

```xml
<LinearLayout android:orientation="vertical"
    android:layout_width="match_parent" android:layout_height="match_parent">
    <TextView android:layout_width="match_parent" android:layout_height="wrap_content"
        android:layout_marginLeft="16dp" android:layout_marginRight="16dp"
        android:layout_marginTop="12dp" android:text="Account" />
</LinearLayout>
```

WRONG — literal translation (compiles, but the child overflows the parent by 32vp):

```typescript
Column() {
  Text('Account')
    .width('100%')                                  // 100% of parent…
    .margin({ left: 16, right: 16, top: 12 })       // …plus 32vp horizontal → overflow
}
.width('100%').height('100%')
```

CORRECT — sink horizontal spacing into the parent's padding, keep vertical margin:

```typescript
Column() {
  Text('Account')
    .width('100%')                 // now 100% of the padded content area
    .margin({ top: 12 })           // vertical margin preserved as-is
}
.width('100%').height('100%')
.padding({ left: 16, right: 16 })  // horizontal spacing carried by the parent
```

Alternative (equivalent) — keep spacing on the child via `calc`:

```typescript
Text('Account')
  .width('calc(100% - 32vp)')      // 16 + 16 = 32; note the spaces around '-'
  .margin({ top: 12 })
```

Do NOT "fix" overflow by wrapping the child in another `width('100%')` + horizontal-margin container — that reproduces the same box-model math one level up and still overflows.

## Control Mapping

| Android source | ArkUI target | Notes |
| --- | --- | --- |
| `TextView` | `Text` | |
| `ImageView` | `Image` | |
| `Button` / `MaterialButton` | `Button` | Preserve emphasis levels rather than exact class names. |
| `Toolbar` / `MaterialToolbar` | page header component | Convert menu items into explicit actions. |
| `RecyclerView` | `List`, `Grid`, `Scroll`, `ForEach`, or `LazyForEach` | Always extract an item component. |
| `Adapter` + `ViewHolder` | item component + callbacks | The adapter is a structural dependency, not a target artifact. |
| menu XML | header actions or contextual action area | Do not silently drop actions. |
| XML item layout | ArkUI child component | One item layout should map to one reusable component where possible. |

## Resource Mapping

| Android source | ArkUI target | Notes |
| --- | --- | --- |
| `strings.xml` | resources or constants | Keep display text out of page logic where possible. |
| colors, dimens | ArkUI resources or design tokens | Normalize repeated values into tokens first. |
| `dp` | `vp` | Convert size intent, not just raw numbers. |
| `sp` | `fp` | |
| styles and themes | shared tokens and shell-level theme setup | Do not mirror Android style names one-to-one. |
| `tools:*` attributes | **nothing — drop them** | Design-time preview only; they do not exist at runtime. Never turn `tools:srcCompat` / `tools:text` / `tools:visibility` / `tools:listitem` into a runtime initial value. Runtime initial state comes from `android:*` attributes and code assignment; when neither sets one, the widget starts empty and the ArkUI page must start empty too. |

## Migration Rules

- Translate page shell, page content, list items, dialogs, and sections as separate target artifacts.
- If the source page mixes empty state, list state, and loading state, keep those states explicit in ArkUI rather than flattening to one static layout.
- If the source page injects children dynamically, convert that to explicit component composition with clear props.
- If one source XML is reused in multiple contexts, create a shared ArkUI component instead of duplicating it.
- If the source uses view binding or data binding, treat the binding class as a clue for layout dependency discovery.

## Suggested Target Structure

Use a structure close to this when the target project is still empty:

- `entry/src/main/ets/pages/` for routed pages
- `entry/src/main/ets/components/` for reusable page parts, cards, dialogs, and list items
- `entry/src/main/ets/models/` for UI-facing data shapes
- `entry/src/main/ets/viewmodels/` or state helpers for local page state
- `entry/src/main/resources/` for strings, colors, media, and profile config

Keep shell components separate from feature pages.
