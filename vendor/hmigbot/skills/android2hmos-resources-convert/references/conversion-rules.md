# Android to HarmonyOS Resource Conversion Rules

This document contains the complete, detailed rules for converting Android resources to HarmonyOS format. Read this before performing any conversions.

## Table of Contents
1. [Android Resource Directory Structure](#android-resource-directory-structure)
2. [HarmonyOS Resource Directory Structure](#harmonyos-resource-directory-structure)
3. [Values XML to Element JSON Conversion](#values-xml-to-element-json-conversion)
4. [Media Resource Conversion](#media-resource-conversion)
5. [Qualifier Mapping](#qualifier-mapping)
6. [Special Cases and Edge Cases](#special-cases-and-edge-cases)

---

## Android Resource Directory Structure

Android resources live under `app/src/main/res/`. Common subdirectories:

| Directory | Contents |
|---|---|
| `drawable/` | Images (PNG, JPG, GIF, WEBP, BMP) and XML drawables (shapes, selectors, layer-lists, vector drawables) |
| `drawable-<qualifier>/` | Qualified drawable variants (e.g., `drawable-hdpi`, `drawable-night`) |
| `mipmap/` | Launcher icons (usually at multiple densities) |
| `mipmap-<qualifier>/` | Qualified launcher icon variants |
| `values/` | XML files defining strings, colors, dimensions, styles, themes, arrays, etc. |
| `values-<qualifier>/` | Qualified value variants (e.g., `values-ar`, `values-zh-rCN`, `values-night`) |
| `layout/` | XML layout definitions |
| `anim/` | Tween animation XML |
| `animator/` | Property animation XML |
| `color/` | Color state list XML |
| `menu/` | Menu definition XML |
| `raw/` | Arbitrary files copied as-is |
| `xml/` | Arbitrary XML files (preferences, configs, etc.) |
| `font/` | Font files (TTF, OTF, TTC) |
| `transition/` | Transition animation XML |
| `interpolator/` | Animation interpolator XML |

## HarmonyOS Resource Directory Structure

HarmonyOS resources live under `entry/src/main/resources/`. Structure:

```
resources/
├── base/                    # Default resources
│   ├── element/             # Key-value resources (JSON)
│   │   ├── string.json
│   │   ├── color.json
│   │   ├── float.json
│   │   ├── integer.json
│   │   ├── boolean.json
│   │   ├── plural.json
│   │   ├── strarray.json
│   │   └── intarray.json
│   ├── media/               # Images, audio, video
│   │   ├── icon.png
│   │   └── ...
│   └── profile/             # JSON configuration files
│       └── ...
├── <qualifier>/             # Qualified resources (e.g., zh_CN, dark, ldpi)
│   ├── element/
│   ├── media/
│   └── profile/
├── rawfile/                 # Raw files (accessed by path)
└── resfile/                 # Raw files (decompressed to sandbox)
```

---

## Values XML to Element JSON Conversion

### strings.xml → string.json

**Android format:**
```xml
<resources>
    <string name="app_name">My App</string>
    <string name="greeting">Hello, %1$s! You have %2$d messages.</string>
    <string name="with_apostrophe">It\'s a test</string>
    <string name="with_html"><![CDATA[<b>Bold</b> text]]></string>
</resources>
```

**HarmonyOS format:**
```json
{
  "string": [
    {
      "name": "app_name",
      "value": "My App"
    },
    {
      "name": "greeting",
      "value": "Hello, %1$s! You have %2$d messages."
    },
    {
      "name": "with_apostrophe",
      "value": "It's a test"
    },
    {
      "name": "with_html",
      "value": "<b>Bold</b> text"
    }
  ]
}
```

**Rules:**
- Remove Android escape sequences: `\'` → `'`, `\"` → `"`
- Decode XML entities: `&amp;` → `&`, `&lt;` → `<`, `&gt;` → `>`, `&quot;` → `"`, `&apos;` → `'`
- Extract text from CDATA sections
- Preserve format placeholders (`%1$s`, `%2$d`, etc.) — HarmonyOS uses the same format
  - ⚠️ **DO NOT drop the `$`**: Android positional format is `%1$s` / `%2$d`. A common silent bug is emitting `%1s` / `%2d` (no `$`). HarmonyOS `resourceManager.getStringSync(id, arg)` / `getPluralStringValueSync` only recognize `%s` / `%d` / `%1$s`; `%1s` / `%1d` are **invalid.
  - **Mandatory self-check after writing string.json / plural.json**: `grep -rEn "%[0-9]+[a-z]" <out>/element/*.json` — any hit of `%<digit><letter>` WITHOUT a `$` (e.g. `%1s`, `%2d`) is a malformed placeholder; fix to `%1$s` / `%2$d`.
- If the string value is wrapped in quotes in Android XML (`"some text"`), remove the outer quotes
- Skip `<string>` elements with `translatable="false"` attribute? No — still include them, as they may be used at runtime. But note the translatable status.

### colors.xml → color.json

**Android format:**
```xml
<resources>
    <color name="primary">#FF6200EE</color>
    <color name="background">#FFFFFF</color>
    <color name="semi_transparent">#80000000</color>
    <color name="shorthand">#F00</color>
</resources>
```

**HarmonyOS format:**
```json
{
  "color": [
    {
      "name": "primary",
      "value": "#FF6200EE"
    },
    {
      "name": "background",
      "value": "#ffFFFFFF"
    },
    {
      "name": "semi_transparent",
      "value": "#80000000"
    },
    {
      "name": "shorthand",
      "value": "#ffFF0000"
    }
  ]
}
```

**Rules:**
- `#AARRGGBB` (8 digits) → keep as-is (HarmonyOS uses same format: first 2 = opacity)
- `#RRGGBB` (6 digits) → prepend `ff` → `#ffRRGGBB`
- `#ARGB` (4 digits) → expand each: `#8F00` → `#88FF0000`
- `#RGB` (3 digits) → expand each and add `ff`: `#F00` → `#ffFF0000`
- Color values are case-insensitive in Android; preserve original case or normalize

### dimens.xml → float.json

**Android format:**
```xml
<resources>
    <dimen name="text_size">16sp</dimen>
    <dimen name="margin_large">24dp</dimen>
    <dimen name="border_width">1px</dimen>
    <dimen name="line_height">20dp</dimen>
</resources>
```

**HarmonyOS format:**
```json
{
  "float": [
    {
      "name": "text_size",
      "value": "16fp"
    },
    {
      "name": "margin_large",
      "value": "24vp"
    },
    {
      "name": "border_width",
      "value": "1px"
    },
    {
      "name": "line_height",
      "value": "20vp"
    }
  ]
}
```

**Unit mapping:**
| Android Unit | HarmonyOS Unit | Notes |
|---|---|---|
| `dp` | `vp` | Density-independent pixels → virtual pixels |
| `dip` | `vp` | Same as dp |
| `sp` | `fp` | Scale-independent pixels → font pixels |
| `px` | `px` | Physical pixels (keep as-is) |
| `pt` | `vp` | Points → convert to vp (multiply by 2.22 — 1pt = 1/72 inch = 160/72 dp; same 160dp/inch baseline as `in`/`mm` below) |
| `in` | `vp` | Inches → convert to vp (multiply by 160) |
| `mm` | `vp` | Millimeters → convert to vp (multiply by 6.3) |
| (no unit) | `vp` | Plain number → append `vp` |

### integers.xml → integer.json

**Android format:**
```xml
<resources>
    <integer name="max_items">10</integer>
    <integer name="animation_duration">300</integer>
</resources>
```

**HarmonyOS format:**
```json
{
  "integer": [
    {
      "name": "max_items",
      "value": 10
    },
    {
      "name": "animation_duration",
      "value": 300
    }
  ]
}
```

### bools.xml → boolean.json

**Android format:**
```xml
<resources>
    <bool name="is_tablet">false</bool>
    <bool name="show_ads">true</bool>
</resources>
```

**HarmonyOS format:**
```json
{
  "boolean": [
    {
      "name": "is_tablet",
      "value": false
    },
    {
      "name": "show_ads",
      "value": true
    }
  ]
}
```

### arrays.xml → strarray.json / intarray.json

**Android string-array:**
```xml
<resources>
    <string-array name="colors">
        <item>Red</item>
        <item>Green</item>
        <item>Blue</item>
    </string-array>
</resources>
```

**HarmonyOS strarray.json:**
```json
{
  "strarray": [
    {
      "name": "colors",
      "value": [
        {
          "value": "Red"
        },
        {
          "value": "Green"
        },
        {
          "value": "Blue"
        }
      ]
    }
  ]
}
```

**Android integer-array:**
```xml
<resources>
    <integer-array name="scores">
        <item>100</item>
        <item>200</item>
        <item>300</item>
    </integer-array>
</resources>
```

**HarmonyOS intarray.json:**
```json
{
  "intarray": [
    {
      "name": "scores",
      "value": [
        {
          "value": 100
        },
        {
          "value": 200
        },
        {
          "value": 300
        }
      ]
    }
  ]
}
```

### plurals.xml → plural.json

**Android format:**
```xml
<resources>
    <plurals name="items_count">
        <item quantity="one">%d item</item>
        <item quantity="other">%d items</item>
    </plurals>
</resources>
```

**HarmonyOS format:**
```json
{
  "plural": [
    {
      "name": "items_count",
      "value": [
        {
          "quantity": "one",
          "value": "%d item"
        },
        {
          "quantity": "other",
          "value": "%d items"
        }
      ]
    }
  ]
}
```

**Supported quantities (same for both):** `zero`, `one`, `two`, `few`, `many`, `other`

---

## Media Resource Conversion

### Drawable images → media

Copy image files directly from Android `drawable/` to HarmonyOS `base/media/`:
- Supported formats in HarmonyOS: PNG, JPG, GIF, SVG, WEBP, BMP
- All these are also common Android formats, so direct copy works
- **Do NOT copy XML drawables** (shapes, selectors, vector drawables, layer-lists, ripple effects) — these have no direct HarmonyOS equivalent

### Identifying XML vs image drawables

In `drawable/` directories, files can be either images or XML:
- `.png`, `.jpg`, `.jpeg`, `.gif`, `.webp`, `.bmp`, `.svg` → image files, copy to `media/`
- `.xml` → XML drawable, **convert to SVG** (see `references/xml-drawable-to-svg-rules.md` for detailed rules). HarmonyOS supports SVG natively in `media/`. Output as `<original_name>.svg` in the target `media/` directory.
- `.9.png` → nine-patch image, copy to `media/` (note: HarmonyOS doesn't natively support nine-patch, but the file can still be used)

### XML Drawable → SVG Conversion (Summary)

Android XML drawables should be converted to SVG format for HarmonyOS. The main convertible types are:

1. **VectorDrawable** (`<vector>`) — Most straightforward. Android's `pathData` uses the same syntax as SVG `d` attribute. Convert `<path>`, `<group>`, `<clip-path>` elements to SVG equivalents.

2. **ShapeDrawable** (`<shape>`) — Convert rectangles, ovals, lines, and rings to SVG `<rect>`, `<ellipse>`, `<line>`, or `<circle>` elements with appropriate fill, stroke, and gradient attributes.

3. **LayerListDrawable** (`<layer-list>`) — Each `<item>` becomes a nested SVG element, layered in document order.

4. **StateListDrawable** (`<selector>`) — Extract the default (no-state) `<item>` or the last `<item>` as fallback, and convert it to SVG. Log the state-dependent items in the conversion report as requiring manual handling.

5. **Unconvertible types** — `<ripple>`, `<animated-vector>`, `<animated-selector>`, `<transition>` remain logged as unmappable because they involve runtime behavior that SVG cannot represent.

For the complete, detailed conversion rules with examples, read `references/xml-drawable-to-svg-rules.md`.

### Mipmap → media

Launcher icons from `mipmap/` directories go to `base/media/` (or qualified `media/`):
- Typically named `ic_launcher.png`, `ic_launcher_round.png`, `ic_launcher_foreground.png`, `ic_launcher_background.png`
- PNG/WEBP launcher icons → direct copy to target `media/` directory
- **Adaptive icon XML files** (`<adaptive-icon>` root element, commonly found in `mipmap-anydpi-v26/`) → convert to HarmonyOS layered-image JSON. Parse the XML, extract the `background` and `foreground` layer references, and convert them using the rules below. Output as `<original_name>_layered_image.json` in the target `media/` directory. Only `background` and `foreground` are valid keys under the `"layered-image"` object — skip `monochrome` or any other elements.

**Reference conversion rules for layered-image values:**
- `@drawable/xxx` → `$media:xxx`
- `@mipmap/xxx` → `$media:xxx`
- `@color/xxx` → **must NOT use `$color:xxx`** — `layered-image` only accepts `$media:` references. See color-background handling below.

**Color background handling (critical):**

HarmonyOS `layered-image` does not support `$color:xxx` — only `$media:xxx` is valid for both `background` and `foreground`. When an Android `<background>` (or `<foreground>`) points to a color resource (`@color/xxx`):

1. Resolve the actual hex color value by looking it up in the converted `color.json` or the Android `colors.xml`. If the color itself references another color, follow the chain to get the final hex value.
2. Generate a solid-color PNG image filled entirely with that hex value. Any reasonable dimensions work (e.g., 1×1 px or 108×108 px).
3. Save the PNG as `<color_name>_bg.png` in `base/media/` (e.g., `md_orange_700_bg.png`).
4. Use `$media:<color_name>_bg` in the layered-image JSON.

**Adaptive icon JSON format example:**

For `ic_launcher.xml`:
```xml
<adaptive-icon xmlns:android="http://schemas.android.com/apk/res/android">
    <background android:drawable="@color/md_orange_700" />
    <foreground android:drawable="@mipmap/ic_launcher_foreground" />
    <monochrome android:drawable="@drawable/ic_launcher_monochrome" />
</adaptive-icon>
```

Suppose `@color/md_orange_700` resolves to `#F57C00`. Generate `base/media/md_orange_700_bg.png` (solid `#F57C00`). Converts to `ic_launcher_layered_image.json`:
```json
{
  "layered-image": {
    "background": "$media:md_orange_700_bg",
    "foreground": "$media:ic_launcher_foreground"
  }
}
```

Note: The `monochrome` element has no HarmonyOS `layered-image` equivalent, so omit it from the JSON output. But do not ignore it entirely — the drawable it references (e.g., `@drawable/ic_launcher_monochrome`) is a real resource that should be converted as a normal drawable and included in dependency analysis. If it's missing from the source `res/` directory (i.e., it comes from a library), record it as an unsatisfied dependency and attempt to recover it via APK decompilation in Step 5, just like any other missing resource.
- **VectorDrawable XML files** (if found in mipmap directories with `<vector>` root element) → convert to SVG, same as drawable vectors

**Common pattern**: `mipmap-anydpi-v26/` is extremely common in Android projects. The qualifier `anydpi-v26` should be parsed as `anydpi` (→ `base`) + `v26` (→ strip). The files inside are typically `<adaptive-icon>` XMLs — process them by reading the XML root element to classify the content type, not by rejecting based on the directory qualifier.

### Raw files → rawfile

Copy all files from Android `raw/` to HarmonyOS `rawfile/`:
- Preserve original filenames
- These are accessed by path in both systems

### Font files → rawfile/fonts

Copy font files from Android `font/` to HarmonyOS `rawfile/fonts/`:
- `.ttf`, `.otf`, `.ttc` files → direct copy
- Font XML files (font family definitions) → log as unmappable

---

## Qualifier Mapping

### Density Qualifiers

The naming conventions differ between Android and HarmonyOS because HarmonyOS uses different DPI range labels:

| Android Qualifier | Approx DPI | HarmonyOS Qualifier | HarmonyOS DPI Range |
|---|---|---|---|
| `ldpi` | 120 | `sdpi` | (0, 120] |
| `mdpi` | 160 | `mdpi` | (120, 160] |
| `tvdpi` | 213 | `ldpi` | (160, 240] |
| `hdpi` | 240 | `ldpi` | (160, 240] |
| `xhdpi` | 320 | `xldpi` | (240, 320] |
| `xxhdpi` | 480 | `xxldpi` | (320, 480] |
| `xxxhdpi` | 640 | `xxxldpi` | (480, 640] |
| `nodpi` | N/A | `base` | No density qualifier; use base |
| `anydpi` | N/A | `base` | No density qualifier; use base |

### Language/Region Qualifiers

Android format: `<type>-<language>` or `<type>-<language>-r<REGION>`
HarmonyOS format: `<language>` or `<language>_<REGION>`

**Examples:**
| Android | HarmonyOS |
|---|---|
| `values-ar` | `ar/element/` |
| `values-zh` | `zh/element/` |
| `values-zh-rCN` | `zh_CN/element/` |
| `values-zh-rTW` | `zh_TW/element/` |
| `values-en` | `en/element/` |
| `values-en-rUS` | `en_US/element/` |
| `values-en-rGB` | `en_GB/element/` |
| `values-fr-rFR` | `fr_FR/element/` |
| `values-ja` | `ja/element/` |
| `values-ko` | `ko/element/` |
| `drawable-zh-rCN-hdpi` | `zh_CN-ldpi/media/` |

**Parsing Android language qualifiers:**
- Language code: 2 or 3 lowercase letters (ISO 639)
- Region code: preceded by `r`, 2 uppercase letters (ISO 3166-1) — strip the `r` prefix
- Script code (BCP 47): preceded by `b+`, e.g., `b+sr+Latn` → `sr_Latn`

### Orientation Qualifiers

| Android | HarmonyOS |
|---|---|
| `land` | `horizontal` |
| `port` | `vertical` |

### Night Mode Qualifiers

| Android | HarmonyOS |
|---|---|
| `night` | `dark` |
| `notnight` | `light` |

### Combining Multiple Qualifiers

Android directory names can contain multiple qualifiers separated by hyphens, e.g., `drawable-zh-rCN-night-hdpi` or `mipmap-anydpi-v26`.

**Parsing algorithm for any Android resource directory name:**

1. Split the directory name by `-` to get segments
2. The first segment is the resource type (`drawable`, `mipmap`, `values`, etc.)
3. The remaining segments are qualifiers. Parse them left-to-right, recognizing:
   - Language codes: 2-3 lowercase letters (e.g., `zh`, `ar`, `en`)
   - Region codes: `r` + 2 uppercase letters (e.g., `rCN`, `rUS`) — always follows a language
   - Density: `ldpi`, `mdpi`, `hdpi`, `xhdpi`, `xxhdpi`, `xxxhdpi`, `nodpi`, `anydpi`, `tvdpi`
   - Orientation: `land`, `port`
   - Night mode: `night`, `notnight`
   - API level: `v` followed by digits (e.g., `v26`, `v21`) — **strip, do not reject**
   - Screen size qualifiers: `sw<N>dp`, `w<N>dp`, `h<N>dp`, `small`, `normal`, `large`, `xlarge` — **skip entire directory, mark as unmapped**
   - Other unsupported qualifiers — **strip, do not reject**
4. Map each recognized qualifier to its HarmonyOS equivalent
5. Strip only API-level, layout direction, screen shape, HDR, and aspect qualifiers (see "Unsupported Android Qualifiers" below)
6. If any screen-size qualifiers remain (`sw<N>dp`, `w<N>dp`, `h<N>dp`, `small`/`normal`/`large`/`xlarge`), skip the entire directory — mark all resources as "unmapped" with reason "Unsupported qualifier"
7. If no mappable or preserved qualifiers remain after stripping, use `base/`
8. Reassemble remaining HarmonyOS qualifiers in correct order: MCC_MNC-language_script_country/region-orientation-device-colormode-density (preserved qualifiers go at the end)

**Examples:**
| Android Directory | Type | Qualifiers | HarmonyOS Dir |
|---|---|---|---|
| `drawable-hdpi` | drawable | hdpi→ldpi | `ldpi/media/` |
| `mipmap-anydpi-v26` | mipmap | anydpi→base, v26→stripped | `base/media/` |
| `drawable-zh-rCN-night-hdpi` | drawable | zh-rCN→zh_CN, night→dark, hdpi→ldpi | `zh_CN-dark-ldpi/media/` |
| `values-ko-rKR` | values | ko-rKR→ko_KR | `ko_KR/element/` |
| `drawable-night-v21` | drawable | night→dark, v21→stripped | `dark/media/` |

### Unsupported Android Qualifiers

These Android qualifiers have no HarmonyOS equivalent. When encountered, **strip them** from the qualifier list (do not reject the directory). If stripping leaves no remaining qualifiers, use `base/`. If other valid qualifiers remain, use those.

Unsupported qualifiers to strip:
- API level `v<N>` (e.g., `v26`, `v21`, `v31`)
- Layout direction (`ldrtl`, `ldltr`)
- `round`, `notround` (screen shape)
- `highdr`, `lowdr` (HDR)
- `long`, `notlong` (screen aspect)

**Qualifiers without a HarmonyOS equivalent** (skip entirely, do NOT convert):
- `sw<N>dp` (smallest width, e.g., `sw600dp`)
- `w<N>dp` (available width, e.g., `w480dp`, `w600dp`)
- `h<N>dp` (available height)
- `small`, `normal`, `large`, `xlarge` (screen size)

These qualifiers have no HarmonyOS mapping. When a directory's only remaining qualifiers (after stripping API level etc.) are from this list, **skip all resources in that directory entirely**. Mark them as "unmapped" in the conversion report with reason "Unsupported qualifier: no HarmonyOS equivalent". Do NOT place them in `base/` or preserve the qualifier as-is — skipping avoids incorrect conversions.

**Important: multi-qualifier directory handling.** Android directory names often combine multiple qualifiers with hyphens. When parsing, extract ALL qualifiers, map each one independently, strip any unsupported ones, and then assemble the HarmonyOS qualifier from whatever remains.

**Examples of stripping unsupported qualifiers:**

| Android Directory | Qualifiers Parsed | After Mapping | HarmonyOS Target |
|---|---|---|---|
| `mipmap-anydpi-v26` | `anydpi` + `v26` | `anydpi` → `base`, `v26` → stripped | `base/media/` |
| `drawable-night-v21` | `night` + `v21` | `night` → `dark`, `v21` → stripped | `dark/media/` |
| `values-sw600dp` | `sw600dp` | **skip — unmapped** | N/A (skipped) |
| `values-w480dp` | `w480dp` | **skip — unmapped** | N/A (skipped) |
| `drawable-hdpi-v4` | `hdpi` + `v4` | `hdpi` → `ldpi`, `v4` → stripped | `ldpi/media/` |

The key principle: API-level qualifiers (`v<N>`) and a few others (layout direction, screen shape, HDR, aspect) are **silently stripped**. Screen-size qualifiers (`sw<N>dp`, `w<N>dp`, `h<N>dp`, `small`/`normal`/`large`/`xlarge`) cause the **entire directory to be skipped** — resources are marked as "unmapped" in the report because HarmonyOS has no equivalent qualifier. This avoids incorrect conversions and keeps the output clean.

---

## Special Cases and Edge Cases

### Multiple values files contributing to the same JSON

Android projects often have multiple XML files under `values/` that all contain `<string>` or `<color>` entries. For example:
- `values/strings.xml` — main strings
- `values/strings_feature.xml` — feature-specific strings
- `values/google_strings.xml` — library strings

All `<string>` entries from any file go into a single `string.json`. Similarly for colors, dimens, etc. Collect entries across all files before writing.

### Resource name conflicts

If two files define the same resource name, the last one wins (matching Android's behavior where later entries override earlier ones). Log these conflicts in the report.

### Android resource references

Android values may reference other resources: `@string/other_string`, `@color/primary`, `@dimen/margin`. These references don't have a direct equivalent in HarmonyOS element JSON. Convert them as:
- `@string/name` → `$string:name`
- `@color/name` → `$color:name`
- `@dimen/name` → `$float:name`
- `@integer/name` → `$integer:name`
- `@bool/name` → `$boolean:name`
- `?attr/name` → log as unmappable (theme attribute reference)

### Android system resource references

References like `@android:color/black` or `@android:string/ok` are Android system resources. Map known ones to literal values or HarmonyOS system resources where possible. Unknown ones should be logged in the report.

### Empty or comment-only XML files

Skip these silently — don't create empty JSON files.

### Large resource sets

When an Android project has hundreds of resources, process them systematically:
1. First scan and inventory all resources
2. Group by type and qualifier
3. Convert each group
4. Verify completeness

### XML encoding and BOM

Some Android XML files may have BOM (Byte Order Mark) or non-UTF-8 encoding declarations. Handle these gracefully — read with the declared encoding, output UTF-8 JSON.
