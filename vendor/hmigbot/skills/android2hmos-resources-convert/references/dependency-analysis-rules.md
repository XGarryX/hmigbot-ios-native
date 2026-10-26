# Android Resource Dependency Analysis Rules

This document defines how to extract, track, and resolve inter-resource dependencies during Android-to-HarmonyOS resource conversion. Dependency analysis runs regardless of resource source — whether from a decompiled APK (complete resource set) or from the project's source `res/` directory (potentially missing library resources). When working from source `res/`, more references will be unresolvable, but the analysis is still essential to identify exactly what's missing and why.

## Table of Contents
1. [Resource Reference Patterns](#resource-reference-patterns)
2. [Building the Resource Value Lookup Table](#building-the-resource-value-lookup-table)
3. [Resolving References to True Values](#resolving-references-to-true-values)
4. [Where to Scan for Dependencies](#where-to-scan-for-dependencies)
5. [Dependency Verification](#dependency-verification)
6. [Handling Missing Library Resources](#handling-missing-library-resources)

---

## Resource Reference Patterns

Android resources reference each other using `@type/name` syntax. Extract these references from XML attribute values and text content.

### Reference Regex Pattern

Use the following pattern to extract resource references from any XML content:

```
@(color|drawable|mipmap|string|dimen|integer|bool|array|style|attr|id|layout|menu|anim|animator|raw|font|xml|plurals)/([a-zA-Z_][a-zA-Z0-9_]*)
```

This captures:
- Group 1: resource type (`color`, `drawable`, etc.)
- Group 2: resource name

### System Resource References

References prefixed with `@android:` (e.g., `@android:color/black`, `@android:drawable/ic_menu_close`) are Android framework resources provided by the OS. These do NOT need to be tracked as dependencies — they have no equivalent that needs to be migrated. Log them as "system resource reference" but do not flag them as unsatisfied.

### Theme Attribute References

References using `?attr/name` or `?android:attr/name` are theme attribute references resolved at runtime. These **cannot** be statically resolved — they depend on which theme is applied at runtime. Log them as "unresolvable theme attribute" and keep the reference as-is in the converted output.

### Reference Locations in XML

Resource references can appear in several places within Android XML files:

**1. XML attribute values:**
```xml
<background android:drawable="@color/md_amber_700" />
<TextView android:text="@string/hello" android:textColor="@color/primary" />
<ImageView android:src="@drawable/icon" />
```

**2. Style/theme item values:**
```xml
<style name="AppTheme">
    <item name="colorPrimary">@color/primary</item>
    <item name="android:windowBackground">@drawable/bg_window</item>
</style>
```

**3. Color state list references:**
```xml
<selector>
    <item android:color="@color/pressed_color" android:state_pressed="true" />
    <item android:color="@color/default_color" />
</selector>
```

**4. Drawable XML references:**
```xml
<layer-list>
    <item android:drawable="@drawable/bg_layer" />
</layer-list>

<adaptive-icon>
    <background android:drawable="@color/ic_bg" />
    <foreground android:drawable="@mipmap/ic_fg" />
</adaptive-icon>
```

**5. Values XML cross-references (these are the primary targets for resolution):**
```xml
<!-- colors.xml -->
<color name="primary_light">@color/primary</color>

<!-- dimens.xml -->
<color name="margin_double">@dimen/margin_base</color>
```

---

## Building the Resource Value Lookup Table

Before resolving references, build a complete lookup table from the resource source directory (either decompiled `res/` or source `res/`). When using the decompiled APK, this table will be comprehensive. When using source `res/`, it will only contain app-defined resources — library resources will be absent, and references to them will be flagged during verification.

### Value Resources

Parse all `values*/*.xml` files and build mappings:

```
colors:
  "primary" → "#FF6200EE"
  "primary_light" → "@color/primary"     # reference chain — will be resolved
  "md_blue_500" → "#2196F3"

dimens:
  "margin_base" → "16dp"
  "margin_double" → "@dimen/margin_base"  # reference chain

strings:
  "app_name" → "My App"
  "greeting" → "Hello, %1$s!"

integers:
  "max_items" → "10"

bools:
  "is_tablet" → "false"
```

Include ALL qualifier variants (e.g., `values/colors.xml`, `values-night/colors.xml`, `values-ar/colors.xml`). Each qualifier variant gets its own entry in the lookup table.

### File Resources

Record all drawable and mipmap files:

```
drawables:
  "icon" → "drawable/icon.png"
  "bg_card" → "drawable/bg_card.xml" (shape)
  "ic_arrow" → "drawable/ic_arrow.xml" (vector)

mipmaps:
  "ic_launcher" → "mipmap-anydpi-v26/ic_launcher.xml" (adaptive-icon)
  "ic_launcher_foreground" → "mipmap-xxxhdpi/ic_launcher_foreground.png"
```

---

## Resolving References to True Values

The key step: walk through all resource values and replace references with actual concrete values.

### Resolution Algorithm

```
function resolve(type, name, qualifier, depth=0):
    if depth > 5: return UNRESOLVABLE  # prevent infinite loops
    value = lookup_table[qualifier][type][name]
    if value is a concrete value (hex color, number, string literal):
        return value
    if value matches @type/other_name:
        return resolve(type, other_name, qualifier, depth+1)
    if value matches ?attr/name:
        return UNRESOLVABLE  # theme attribute, cannot resolve statically
    return value
```

### What Gets Resolved

**Value-to-value references** (primary targets):
- `@color/name` → resolved hex color (e.g., `@color/primary` → `#FF6200EE`)
- `@dimen/name` → resolved dimension value (e.g., `@dimen/margin_base` → `16dp`)
- `@string/name` → resolved string value
- `@integer/name` → resolved integer value
- `@bool/name` → resolved boolean value

**File references** (kept as HarmonyOS references, not resolved to values):
- `@drawable/name` → `$media:name` (the file itself is converted separately)
- `@mipmap/name` → `$media:name`

**Unresolvable references** (logged but kept as-is):
- `?attr/name` — theme attributes depend on runtime theme
- `@android:type/name` — system resources, provided by the platform
- `@style/name` — styles have no HarmonyOS equivalent

### Resolution During Conversion

Resolution happens at conversion time, not as a separate pass. When converting a value from Android XML to HarmonyOS JSON:

1. Parse the XML value
2. If it's a concrete value (hex color, number, string), convert directly using format rules
3. If it's a resource reference (`@type/name`):
   a. Look up in the lookup table
   b. Follow the chain to the concrete value
   c. Convert the concrete value using format rules
   d. Use the resolved concrete value in the HarmonyOS JSON output
4. If the reference can't be resolved, use HarmonyOS reference syntax (`$color:name`, `$float:name`, etc.) and log it

### Example: Full Resolution Chain

Android `values/colors.xml`:
```xml
<color name="app_background">@color/surface_color</color>
<color name="surface_color">@color/md_grey_50</color>
<color name="md_grey_50">#FAFAFA</color>
```

Resolution:
- `app_background` → `@color/surface_color` → `@color/md_grey_50` → `#FAFAFA`

HarmonyOS `color.json` output:
```json
{
  "color": [
    {"name": "app_background", "value": "#ffFAFAFA"},
    {"name": "surface_color", "value": "#ffFAFAFA"},
    {"name": "md_grey_50", "value": "#ffFAFAFA"}
  ]
}
```

All three resolve to the same concrete value. The `#ffFAFAFA` format is after applying the `#RRGGBB` → `#ffRRGGBB` color format conversion.

---

## Where to Scan for Dependencies

Scan ALL resource files from the resource source directory for dependencies, organized by priority:

### High Priority (converted resources — broken dependencies cause direct errors)

| File Type | Typical Location | Why It Matters |
|---|---|---|
| Adaptive icon XML | `mipmap-anydpi-v26/*.xml` | References colors, drawables, mipmaps for icon layers |
| Vector drawables | `drawable/*.xml` (root: `<vector>`) | May reference colors via theme attrs |
| Shape drawables | `drawable/*.xml` (root: `<shape>`) | May reference colors, dimens |
| Layer-list drawables | `drawable/*.xml` (root: `<layer-list>`) | References other drawables |
| Selector drawables | `drawable/*.xml` (root: `<selector>`) | References other drawables for states |
| Color state lists | `color/*.xml` | References other colors |
| Values XML | `values*/*.xml` | Cross-references between value types |

### Required — Layout and Menu (not converted, but dependencies must be verified)

Layout and menu files are **not** converted to HarmonyOS (they use ArkUI instead), but the resources they reference — strings, colors, drawables, dimensions — **must** be present in the converted output so the developer has everything needed when rebuilding the UI.

| File Type | Typical Location | Why It Matters |
|---|---|---|
| Layout XML | `layout*/*.xml` | References strings, colors, drawables, dimens used by every UI component |
| Menu XML | `menu/*.xml` | References strings and drawables for action bar / navigation items |

### Skip (no meaningful dependencies)

- Raw files (`raw/`)
- Font files (`font/`) — unless font XML family definitions reference other fonts
- Image files (PNG, JPG, WEBP, etc.) — binary files, no references

---

## Dependency Verification

After conversion with reference resolution, verify that the output is self-consistent:

### Check by Resource Type

| Dependency Type | Where to Check in HarmonyOS Output |
|---|---|
| `@color/name` | Should be resolved to hex in `*/element/color.json`. If not resolved, check `name` exists. |
| `@drawable/name` | Look for `name.*` (any extension: .png, .svg, .jpg, etc.) in `*/media/` |
| `@mipmap/name` | Same as drawable — mipmaps go to `media/` in HarmonyOS |
| `@string/name` | Should be resolved to literal in `*/element/string.json`. If not resolved, check `name` exists. |
| `@dimen/name` | Should be resolved to value in `*/element/float.json`. If not resolved, check `name` exists. |
| `@integer/name` | Look for `name` in `*/element/integer.json` |
| `@bool/name` | Look for `name` in `*/element/boolean.json` |
| `@array/name` | Look for `name` in `*/element/strarray.json` or `*/element/intarray.json` |
| `@plurals/name` | Look for `name` in `*/element/plural.json` |
| `@style/name` | Mark as "unmappable type" (styles have no HarmonyOS equivalent) |
| `@attr/name` | Mark as "unmappable type" |
| `@layout/name` | Mark as "not applicable" (layouts aren't converted) |
| `@id/name` | Mark as "not applicable" (IDs are code-level concerns) |

### Qualifier Coverage Check

When a dependency is satisfied, also verify qualifier coverage. If the dependent resource exists in multiple qualifier directories (e.g., `base`, `dark`, `ldpi`), the dependency should ideally exist in matching qualifier directories. Flag cases where a dependency exists in `base` but the dependent resource also has `dark` or density-qualified variants — the dependency may need those variants too.

---

## Handling Missing Library Resources

When converting from source `res/` (because the APK build failed or no APK was available), library-provided resources will be absent from the lookup table. This section describes how to handle these gaps gracefully.

### Identifying Library Resources

Many common Android libraries define resources with recognizable naming patterns. Use these heuristics to correlate unsatisfied dependencies with likely library sources:

| Library | Common Resource Prefixes |
|---|---|
| Material Components (`com.google.android.material`) | `material_*`, `design_*`, `mtrl_*`, `Widget.Material*`, `Theme.Material*` |
| AndroidX AppCompat (`androidx.appcompat`) | `abc_*`, `Widget.AppCompat.*` |
| AndroidX Core (`androidx.core`) | `notification_*`, `compat_*` |
| AndroidX ConstraintLayout | `constraint_*` |
| Google Play Services | `common_google_*` |

### Extracting Library Dependencies from build.gradle

Parse `build.gradle` or `build.gradle.kts` to identify declared library dependencies:

```groovy
// build.gradle
dependencies {
    implementation 'com.google.android.material:material:1.9.0'
    implementation 'androidx.appcompat:appcompat:1.6.1'
    implementation 'androidx.core:core-ktx:1.12.0'
}
```

Extract the group:artifact for each dependency. In the conversion report, list these libraries with their likely resource prefixes so the developer knows which libraries contribute which missing resources.

### Resolution Behavior for Missing Resources

When a reference cannot be resolved because the target resource is not in the lookup table:

1. **Keep the HarmonyOS reference syntax** (`$color:name`, `$float:name`, `$media:name`, etc.) in the converted output — this makes the reference visible and searchable
2. **Log it as an unsatisfied dependency** with:
   - The reference (`@color/design_default_color_primary`)
   - The source file where it was found
   - The likely library source (if identifiable from naming patterns)
   - The reason: "Library resource not available in source res/"
3. **Do NOT substitute a default or placeholder value** — keeping the reference intact is more useful because:
   - The developer can see exactly what's missing
   - If the build is later fixed and resources re-converted from the APK, the output will be correct
   - The reference name itself carries meaning for the developer

### Categorizing Unresolved References

In the report, separate unresolved references into categories:

1. **Missing library resources** — references to resources that likely come from declared library dependencies. These are expected when converting from source `res/`.
2. **Theme attributes** (`?attr/name`) — cannot be statically resolved regardless of resource source.
3. **System resources** (`@android:type/name`) — Android framework resources, not migrated.
4. **Truly missing** — references that don't match any known library pattern and aren't in the lookup table. These may indicate a project misconfiguration or an undeclared dependency.
