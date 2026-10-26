# Schema Reference — Android UI Graph (v2.0)

Global convention: all required fields must appear; undetermined values → `"unknown"` (string), `{}` (object), `[]` (array).

---

## 1. Screen Node (→ Screen.json)

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | `screen:{full.qualified.ClassName}` |
| `type` | enum | `Activity` / `Fragment` / `DialogFragment` / `Dialog` / `BottomSheetDialogFragment` / `PopupWindow` |
| `name` | string | Simple class name |
| `package` | string | Package path |
| `layout_ref` | string | e.g. `R.layout.activity_home` or `"unknown"` |
| `source_file` | string | Relative path from project root |
| `language` | enum | `Java` / `Kotlin` |
| `theme` | string | e.g. `@style/Theme.App` or `"unknown"` |
| `parent_activity` | string | Screen ID of host Activity; Activity itself → `"none"` |
| `menu_ref` | string | e.g. `R.menu.menu_home` or `"unknown"` |
| `has_options_menu` | boolean | Whether `onCreateOptionsMenu` is overridden |
| `has_toolbar` | boolean | Whether layout contains Toolbar / MaterialToolbar |
| `orientation_config` | enum | `portrait` / `landscape` / `unspecified` / `unknown` |
| `config_changes` | string | Manifest `configChanges` value or `"unknown"` |
| `lifecycle_callbacks` | array | e.g. `["onCreate","onResume","onDestroy"]` |
| `metadata` | object | See below |

**metadata:**
```json
{
  "launch_mode": "standard | singleTop | singleTask | singleInstance | unknown",
  "exported": true | false,
  "intent_filters": [ { "action": "...", "category": "..." } ],
  "soft_input_mode": "adjustResize | adjustPan | unknown",
  "window_flags": "unknown",
  "task_affinity": "unknown"
}
```

---

## 2. Component Node (→ Component.json)

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | See ID rules below |
| `android_id` | string | XML `android:id` value, or `"none"` |
| `class` | string | Full class name, e.g. `android.widget.Button` |
| `class_short` | string | Short name, e.g. `Button` |
| `is_viewgroup` | boolean | Container or leaf |
| `is_custom_view` | boolean | Project-defined custom View |
| `source_layout` | string | e.g. `layout/activity_home.xml` |
| `depth` | int | Tree depth (root = 0) |
| `layout_attrs` | object | See §2.1 |
| `style_attrs` | object | See §2.2 |
| `behavior_attrs` | object | See §2.3 |
| `accessibility_attrs` | object | See §2.4 |
| `resource_refs` | array | See §2.5 |
| `custom_attrs` | object | `app:xxx` non-constraint attrs, or `{}` |

**ID rules:**
- Has `android:id` → `comp:{layout_name}:{id_value}` (e.g. `comp:activity_home:btn_login`)
- No `android:id` → `comp:{layout_name}:{class_short}#{counter_from_1}` (e.g. `comp:activity_home:LinearLayout#2`)

### 2.1 layout_attrs

Include only fields relevant to the component's parent container type. Irrelevant fields are omitted (not filled with "unknown"). `constraints` sub-object only when parent is ConstraintLayout / MotionLayout.

```json
{
  "layout_width":          "match_parent | wrap_content | value | unknown",
  "layout_height":         "match_parent | wrap_content | value | unknown",
  "layout_margin":         { "start": "", "end": "", "top": "", "bottom": "" },
  "layout_padding":        { "start": "", "end": "", "top": "", "bottom": "" },
  "layout_gravity":        "unknown",
  "layout_weight":         "unknown",
  "min_width":             "unknown",
  "min_height":            "unknown",
  "max_width":             "unknown",
  "max_height":            "unknown",
  "orientation":           "horizontal | vertical | unknown  [LinearLayout containers only]",
  "gravity":               "unknown  [containers only, child alignment]",
  "layout_column":         "unknown  [GridLayout children]",
  "layout_column_span":    "unknown  [GridLayout children]",
  "layout_row":            "unknown  [GridLayout children]",
  "layout_row_span":       "unknown  [GridLayout children]",
  "layout_span":           "unknown  [TableRow children]",
  "layout_anchor":         "unknown  [CoordinatorLayout children]",
  "layout_anchor_gravity": "unknown  [CoordinatorLayout children]",
  "layout_behavior":       "unknown  [CoordinatorLayout children]",
  "layout_collapse_mode":  "unknown  [CollapsingToolbarLayout children]",
  "layout_scroll_flags":   "unknown  [AppBarLayout children]",
  "constraints": {
    "topToTopOf":       "unknown", "topToBottomOf":    "unknown",
    "bottomToTopOf":    "unknown", "bottomToBottomOf": "unknown",
    "startToStartOf":   "unknown", "startToEndOf":     "unknown",
    "endToStartOf":     "unknown", "endToEndOf":       "unknown",
    "baseline_to_baseline_of": "unknown",
    "horizontal_bias":  "unknown", "vertical_bias": "unknown",
    "width_default":    "spread | wrap | percent | unknown",
    "width_percent":    "unknown",
    "height_default":   "spread | wrap | percent | unknown",
    "height_percent":   "unknown",
    "dimension_ratio":  "unknown",
    "chain_style_horizontal": "spread | spread_inside | packed | unknown",
    "chain_style_vertical":   "spread | spread_inside | packed | unknown",
    "constraint_set":   "unknown  [MotionLayout]"
  }
}
```

### 2.2 style_attrs

Include only fields relevant to the component's type. `[scope]` tags indicate applicable component types — omit fields outside that scope entirely.

```json
{
  "style":              "@style/... | unknown",
  "background":         "unknown",
  "backgroundTint":     "unknown",
  "foreground":         "unknown",
  "elevation":          "unknown",
  "translationZ":       "unknown",
  "alpha":              "unknown",
  "rotation":           "unknown",
  "rotationX":          "unknown",
  "rotationY":          "unknown",
  "scaleX":             "unknown",
  "scaleY":             "unknown",
  "transformPivotX":    "unknown",
  "transformPivotY":    "unknown",
  "clipToOutline":      "unknown",
  "clipChildren":       "unknown  [ViewGroup only]",
  "clipToPadding":      "unknown  [ViewGroup only]",

  "text":               "unknown  [TextView+]",
  "textColor":          "unknown  [TextView+]",
  "textColorHint":      "unknown  [TextView+]",
  "textSize":           "unknown  [TextView+]",
  "textStyle":          "normal | bold | italic | bold|italic | unknown  [TextView+]",
  "textAlignment":      "unknown  [TextView+]",
  "textAllCaps":        "unknown  [TextView+]",
  "fontFamily":         "unknown  [TextView+]",
  "typeface":           "unknown  [TextView+]",
  "letterSpacing":      "unknown  [TextView+]",
  "lineSpacingExtra":   "unknown  [TextView+]",
  "lineSpacingMultiplier": "unknown  [TextView+]",
  "maxLines":           "unknown  [TextView+]",
  "minLines":           "unknown  [TextView+]",
  "ellipsize":          "start | middle | end | marquee | unknown  [TextView+]",
  "hint":               "unknown  [TextView+]",
  "drawableStart":      "unknown  [TextView+]",
  "drawableEnd":        "unknown  [TextView+]",
  "drawableTop":        "unknown  [TextView+]",
  "drawableBottom":     "unknown  [TextView+]",
  "drawablePadding":    "unknown  [TextView+]",

  "src":                "unknown  [ImageView+]",
  "scaleType":          "unknown  [ImageView+]",
  "adjustViewBounds":   "unknown  [ImageView+]",
  "tint":               "unknown  [ImageView+]",
  "tintMode":           "unknown  [ImageView+]",

  "progress":           "unknown  [ProgressBar/SeekBar]",
  "max":                "unknown  [ProgressBar/SeekBar]",
  "min":                "unknown  [ProgressBar/SeekBar]",
  "indeterminate":      "unknown  [ProgressBar/SeekBar]",
  "progressDrawable":   "unknown  [ProgressBar/SeekBar]",
  "progressTint":       "unknown  [ProgressBar/SeekBar]",
  "thumbTint":          "unknown  [SeekBar]",

  "layoutManager":      "unknown  [RecyclerView]",
  "spanCount":          "unknown  [RecyclerView]",
  "hasFixedSize":       "unknown  [RecyclerView]",
  "overScrollMode":     "unknown  [RecyclerView]",

  "cornerRadius":       "unknown  [Material]",
  "strokeColor":        "unknown  [Material]",
  "strokeWidth":        "unknown  [Material]",
  "rippleColor":        "unknown  [Material]",
  "iconGravity":        "unknown  [Material]",
  "icon":               "unknown  [Material]",
  "iconTint":           "unknown  [Material]",
  "iconSize":           "unknown  [Material]",
  "shapeAppearance":    "unknown  [Material]",
  "boxBackgroundMode":  "unknown  [TextInputLayout]",
  "boxStrokeColor":     "unknown  [TextInputLayout]",
  "boxCornerRadius":    "unknown  [TextInputLayout]",
  "errorEnabled":       "unknown  [TextInputLayout]",
  "helperTextEnabled":  "unknown  [TextInputLayout]",
  "counterEnabled":     "unknown  [TextInputLayout]",
  "counterMaxLength":   "unknown  [TextInputLayout]",
  "tabIndicatorColor":  "unknown  [TabLayout]",
  "tabMode":            "unknown  [TabLayout]",
  "tabGravity":         "unknown  [TabLayout]"
}
```

### 2.3 behavior_attrs

Include only fields relevant to the component's type.

```json
{
  "clickable":            "true | false | unknown",
  "longClickable":        "true | false | unknown",
  "focusable":            "true | false | unknown",
  "focusableInTouchMode": "true | false | unknown",
  "enabled":              "true | false | unknown",
  "selected":             "true | false | unknown",
  "activated":            "true | false | unknown",
  "visibility":           "visible | invisible | gone | unknown",
  "scrollbars":           "horizontal | vertical | none | unknown",
  "nestedScrollingEnabled": "true | false | unknown",
  "overScrollMode":       "always | ifContentScrolls | never | unknown",
  "tag":                  "unknown",
  "transitionName":       "unknown",

  "inputType":            "unknown  [EditText+]",
  "imeOptions":           "unknown  [EditText+]",
  "editable":             "true | false | unknown  [EditText+]",
  "digits":               "unknown  [EditText+]",
  "maxLength":            "unknown  [EditText+]",
  "selectAllOnFocus":     "true | false | unknown  [EditText+]",
  "textIsSelectable":     "true | false | unknown  [TextView+]",

  "checked":              "true | false | unknown  [CheckBox/Switch/RadioButton]",
  "checkable":            "true | false | unknown  [CheckBox/Switch/RadioButton]",
  "button":               "unknown  [CheckBox/RadioButton]",
  "switchMinWidth":       "unknown  [Switch]",
  "thumbDrawable":        "unknown  [Switch]",
  "trackDrawable":        "unknown  [Switch]",

  "onClick":              "method_name | unknown",
  "onLongClick":          "method_name | unknown",
  "onTouch":              "method_name | unknown",
  "onFocusChange":        "method_name | unknown"
}
```

### 2.4 accessibility_attrs

All components include these fields.

```json
{
  "contentDescription":             "unknown",
  "importantForAccessibility":      "auto | yes | no | noHideDescendants | unknown",
  "accessibilityLiveRegion":        "none | polite | assertive | unknown",
  "accessibilityHeading":           "true | false | unknown",
  "accessibilityTraversalBefore":   "unknown",
  "accessibilityTraversalAfter":    "unknown",
  "labelFor":                       "unknown"
}
```

### 2.5 resource_refs

Array of all `@xxx/yyy` references found on the component.

```json
[
  {
    "attr": "attribute_name",
    "ref":  "@type/name",
    "type": "drawable | color | string | dimen | style | font | anim | array | integer | bool | menu | raw | mipmap"
  }
]
```

---

## 3. Navigation Edge (→ Navigation_Edge.json)

| Field | Type | Description |
|-------|------|-------------|
| `from` | string | Source Screen ID |
| `to` | string | Target Screen ID |
| `trigger` | string | Natural-language description (Chinese) of what triggers the navigation |
| `mechanism` | enum | `Intent` / `NavController` / `FragmentTransaction` / `DialogShow` / `PopupShow` / `StartActivityForResult` / `DeepLink` / `Other` |
| `direction` | enum | `forward` / `back` / `replace` / `unknown` |
| `source_component` | string | Component ID that triggers navigation, or `"unknown"` |
| `extras` | object | Passed parameters as `{ key: type }`, or `{}` |
| `transition_anim` | string | e.g. `@anim/slide_in_right` or `"unknown"` |
| `flags` | string | e.g. `FLAG_ACTIVITY_CLEAR_TOP` or `"unknown"` |
| `condition` | string | Natural-language pre-condition, or `"none"` |

---

## 4. Containment Edge (→ Containment_Edge.json)

| Field | Type | Description |
|-------|------|-------------|
| `parent` | string | Parent node ID (Screen or Component) |
| `child` | string | Child Component ID |
| `order` | int | 0-based sibling index |
| `source` | enum | `direct` / `include` / `merge` / `viewstub` / `fragment_tag` / `dynamic` |
| `include_layout` | string | Included layout file name if `source=include`, otherwise `"none"` |
