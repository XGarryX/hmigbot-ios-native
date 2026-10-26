---
name: android2hmos-resources-convert
description: Convert Android project resources to HarmonyOS project resources. Use this skill when the user wants to migrate, convert, or transfer resource files (strings, colors, dimensions, images, drawables, icons, etc.) from an Android project to a HarmonyOS project. Also trigger when the user mentions Android-to-HarmonyOS migration involving resource files, qualifier directories (like drawable-hdpi, values-zh), or resource format conversion (XML to JSON). Also trigger for Material Design icon download/integration, SVG display issues (blank/invisible/wrong size), or icon mapping from Android source code. Even partial mentions like "icon display broken", "download Material icon", "SVG size wrong", "migrate Android icons" should trigger this skill.
metadata:
  type: domain
  domain: migration
  tags:
  - migration
  - resources
  - android
  - svg
---
# Android to HarmonyOS Resource Converter

This skill converts resource files from an Android project into the resource format used by HarmonyOS projects. It attempts to build the Android APK and decompile it with apktool to get the complete merged resource set (including all library dependencies). If the build fails or no APK is available, it falls back to converting directly from the project's source `res/` directory — which may be missing library-provided resources, but still produces a useful conversion with clear reporting of what's missing and why.

## Reference Guide

| What You Want To Do | Read This |
|---------------------|----------|
| Batch convert Android resource directories to HarmonyOS format | `references/conversion-rules.md` |
| Convert Android XML Drawable to SVG | `references/xml-drawable-to-svg-rules.md` |
| Analyze resource dependencies, resolve missing references | `references/dependency-analysis-rules.md` |
| Download Material Design icons from Google Fonts and integrate | `references/material-design-icons.md` |
| Fix SVG display issues (coordinates/format/Android syntax remnants) | `references/svg-fix-patterns.md` |

## Inputs

1. **Android project path** — root directory of the Android project (contains `build.gradle` or `build.gradle.kts`)
2. **HarmonyOS project output path** — where the new HarmonyOS project will be created

## Workflow

### Step 1: Initialize HarmonyOS Project

**Skip condition**: Before copying, check if the HarmonyOS output path already exists and is non-empty (i.e., it contains files or directories such as `AppScope/`, `entry/`, `build-profile.json5`, etc.). If it does, this is an existing HarmonyOS project — skip template initialization entirely and proceed directly to Step 2. Only copy the template when the output path doesn't exist or is empty.

When initialization is needed, copy the bundled HarmonyOS project template to the output path:

```
Template source: <skill_dir>/template/
```

- Copy the entire template directory to the target path
- Preserve the template's directory structure (AppScope, entry, hvigor, etc.)
- The main resource target directory is: `<output>/entry/src/main/resources/`

### Step 2: Attempt to Build the Android APK

Try to build the Android project to produce an APK containing all merged resources (source + library dependencies + generated resources). The decompiled APK is the ideal source because it contains everything — but building is not always possible.

1. Ask the user which Gradle build variant to use (e.g., `assembleDebug`, `assembleRelease`, `assembleFossDebug`). Default to `assembleDebug` if the user has no preference — debug builds include all resources without optimization.

2. Run the build:
```bash
cd <android_project>
./gradlew <variant>
```

3. **If the build succeeds**: locate the APK in `<android_project>/app/build/outputs/apk/`. If multiple APKs exist, prefer the debug variant. Record `build_status = "success"` and proceed to Step 3 (decompile).

4. **If the build fails**: record the build error output and `build_status = "failed"`. Also check if a previously-built APK already exists at `<android_project>/app/build/outputs/apk/`. If an existing APK is found, use it and record `build_status = "failed_using_cached_apk"`. If no APK exists at all, skip Step 3 entirely and proceed to Step 4 using the source `res/` directory. Set `resource_source = "source_res"`.

The reason we prefer the decompiled APK: it contains all merged resources from source code AND library dependencies (AARs, Maven artifacts). When falling back to source `res/`, library resources are missing, which means some resource references may be unresolvable. The conversion report will clearly flag this.

### Step 3: Decompile the APK with apktool (skip if no APK)

If an APK is available (from a successful build or a cached previous build), decompile it:

```bash
java -jar <skill_dir>/tools/apktool_3.0.1.jar d <apk_path> -o <decompiled_output_path>
```

The skill bundles `apktool_3.0.1.jar` in its `tools/` directory. Java must be available in the system PATH.

The decompiled output at `<decompiled_output_path>/res/` contains the **complete merged resource set**. Set `resource_source = "decompiled_apk"` and use this as the conversion source.

If no APK is available, skip this step. The conversion source will be the project's source `res/` directory (typically `<android_project>/app/src/main/res/`). Set `resource_source = "source_res"`.

### Step 4: Convert Resources

Read the detailed conversion rules from `references/conversion-rules.md` before performing conversions. Convert all resources found in the resource source directory (either decompiled `res/` or source `res/`).

**Determining the source `res/` directory when using source fallback:**
- Check `<android_project>/app/src/main/res/`
- If multi-module, also check other module directories
- If the project uses flavor source sets, include those too (e.g., `app/src/debug/res/`, `app/src/flavor/res/`)

#### 4.1 Resource Type Mapping

| Android Resource Dir | HarmonyOS Target | Notes |
|---|---|---|
| `drawable/` (images: png, jpg, webp, gif) | `base/media/` | Direct file copy |
| `drawable/` (Android vector drawables: `<vector>`) | `base/media/` as `.svg` | Convert VectorDrawable XML to SVG format |
| `drawable/` (shape drawables: `<shape>`) | `base/media/` as `.svg` | Convert shape XML to SVG |
| `drawable/` (layer-list drawables: `<layer-list>`) | `base/media/` as `.svg` | Convert layered drawable to SVG with nested elements |
| `drawable/` (selector/state-list drawables) | `base/media/` (default state as `.svg`) | Extract default state item and convert to SVG; log state variants in report |
| `drawable/` (ripple, animated-vector, transition) | No direct equivalent | Log as unmappable; note in report |
| `mipmap/` (PNG/WEBP images) | `base/media/` | App launcher icons — direct copy |
| `mipmap/` (adaptive-icon XML: `<adaptive-icon>`) | `base/media/` as `xxx_layered_image.json` | Convert to layered-image JSON (see below) |
| `mipmap/` (vector XML: `<vector>`) | `base/media/` as `.svg` | Convert VectorDrawable to SVG |
| `values/strings.xml` | `base/element/string.json` | XML → JSON conversion |
| `values/colors.xml` | `base/element/color.json` | XML → JSON; fix color format |
| `values/dimens.xml` | `base/element/float.json` | XML → JSON; convert units |
| `values/integers.xml` | `base/element/integer.json` | XML → JSON |
| `values/bools.xml` | `base/element/boolean.json` | XML → JSON |
| `values/arrays.xml` (string-array) | `base/element/strarray.json` | XML → JSON |
| `values/arrays.xml` (integer-array) | `base/element/intarray.json` | XML → JSON |
| `values/plurals.xml` | `base/element/plural.json` | XML → JSON |
| `values/styles.xml` | No direct equivalent | Log in report |
| `values/attrs.xml` | No direct equivalent | Log in report |
| `raw/` | `rawfile/` | Direct file copy |
| `font/` | `rawfile/fonts/` | Copy fonts to rawfile |
| `xml/` | `base/profile/` (JSON only) or unmappable | `profile/` accepts **JSON only**; most Android `xml/` (preferences, network-security-config, etc.) is XML with no HarmonyOS equivalent → log as unmappable. Route to `profile/` only for genuine config data, via a real XML→JSON conversion (NOT a `.xml`→`.json` rename) |
| `anim/`, `animator/` | No direct equivalent | Log in report |
| `layout/` | No direct equivalent | ArkUI uses declarative UI; log in report |
| `menu/` | No direct equivalent | Log in report |
| `color/` (color state lists) | No direct equivalent | Log in report |

#### 4.1.1 Adaptive Icon → Layered-Image JSON Conversion

Android adaptive-icon XML files (root element `<adaptive-icon>`, commonly found in `mipmap-anydpi-v26/`) are converted to HarmonyOS layered-image JSON files.

**Conversion rules:**
1. Parse the `<adaptive-icon>` XML and extract the `<background>` and `<foreground>` elements
2. Only `background` and `foreground` are valid keys in the output JSON. Skip `monochrome` (and any other elements) **from the JSON output** — HarmonyOS has no layered-image equivalent. However, the resource *referenced* by `monochrome` (e.g., `@drawable/ic_launcher_monochrome`) is a real asset that should still be converted as a normal drawable.
3. Convert Android resource references to HarmonyOS format:
   - `@drawable/xxx` → `$media:xxx`
   - `@mipmap/xxx` → `$media:xxx`
   - `@color/xxx` → **generate a solid color PNG** (see rule 4 below)
4. **Critical — color background handling**: HarmonyOS `layered-image` only accepts `$media:xxx` references. It does NOT support `$color:xxx`. When the `background` (or `foreground`) references a color (`@color/xxx`):
   a. Look up the **resolved hex value** of `@color/xxx` from the resource source's `res/values*/colors.xml`. Follow reference chains if the color itself references another color — keep resolving until you reach a concrete hex value.
   b. Generate a solid-color PNG filled entirely with that hex color. A minimal valid PNG of any small size (e.g., 1×1 or 108×108 pixels) is sufficient.
   c. Name the PNG `<color_name>_bg.png` (e.g., `brand_color_bg.png`) and place it in `base/media/`.
   d. Reference it as `$media:<color_name>_bg` in the layered-image JSON.
   e. **If the color cannot be resolved** (e.g., it comes from a library and we're using source `res/`), log it as an unsatisfied dependency in the report and use a placeholder reference.
5. Output filename: `<original_name>_layered_image.json` (e.g., `ic_launcher.xml` → `ic_launcher_layered_image.json`)
6. Store in the target `media/` directory (typically `base/media/`)

**Example:**
```xml
<!-- mipmap-anydpi-v26/ic_launcher.xml -->
<adaptive-icon xmlns:android="http://schemas.android.com/apk/res/android">
    <background android:drawable="@color/md_orange_700" />
    <foreground android:drawable="@mipmap/ic_launcher_foreground" />
    <monochrome android:drawable="@drawable/ic_launcher_monochrome" />
</adaptive-icon>
```

Suppose `@color/brand_orange` resolves to `#F57C00`. Generate `base/media/brand_orange_bg.png` (a solid `#F57C00` filled PNG). Then convert to `base/media/ic_launcher_layered_image.json`:
```json
{
  "layered-image": {
    "background": "$media:brand_orange_bg",
    "foreground": "$media:ic_launcher_foreground"
  }
}
```

#### 4.2 Qualifier Directory Mapping

Android uses qualifiers as directory suffixes (e.g., `drawable-hdpi`, `values-ar`). HarmonyOS uses a different qualifier directory naming convention. Convert as follows:

**Screen density mapping** (Android DPI names differ from HarmonyOS):

| Android Qualifier | Android DPI | HarmonyOS Qualifier | HarmonyOS DPI Range |
|---|---|---|---|
| `ldpi` | ~120 | `sdpi` | (0, 120] |
| `mdpi` | ~160 | `mdpi` | (120, 160] |
| `hdpi` | ~240 | `ldpi` | (160, 240] |
| `xhdpi` | ~320 | `xldpi` | (240, 320] |
| `xxhdpi` | ~480 | `xxldpi` | (320, 480] |
| `xxxhdpi` | ~640 | `xxxldpi` | (480, 640] |
| `nodpi` | N/A | `base` | No density qualifier; use base |
| `anydpi` | N/A | `base` | No density qualifier; use base |

**Language/region mapping**:
- `values-ar` → `ar/element/`
- `values-zh-rCN` or `values-zh` → `zh_CN/element/` or `zh/element/`
- `values-en-rUS` → `en_US/element/`
- `drawable-ar` → `ar/media/`

### Multi-language Enforcement Rules

When converting an Android project's string resources, apply these **mandatory** rules:

**Minimum language requirement:**
1. Scan Android `res/` for all `values-*` directories with string resources
2. **Must** generate at least 2 language resource sets:
   - `resources/base/element/string.json` — default language (follow Android's `values/strings.xml`)
   - `resources/en_US/element/string.json` — English (if default is not English)
   - `resources/zh_CN/element/string.json` — Chinese (if default is not Chinese)
3. If the default language is English, generate: `base` (English) + `zh_CN` (Chinese)
4. If the default language is Chinese, generate: `base` (Chinese) + `en_US` (English)

**Scaling rules for additional languages:**
- Android has N language directories:
  - N ≤ 10: Convert ALL languages
  - N > 10: Convert base + en + zh + user-specified languages (ask user which to include)

**Key consistency validation:**
After conversion, verify that ALL language resource files have the **exact same set of string keys**. If a key exists in `base/` but not in `en_US/`, add it to `en_US/` with the English value from Android's `values-en/strings.xml` (or the base value as fallback with a `[TODO: translate]` prefix).

**Translation placeholders (`[TODO: translate]`) + fallback assets**: every remaining placeholder **MUST** be registered in `spec/placeholder-registry.md` (`kind=resource-pending-translation` or `kind=resource-pending-asset`, all 6 fields populated). This skill only emits the placeholder and writes the registry entry; the actual translation workflow is handled by the `arkts-i18n` skill (see its SKILL.md "Auto-translation mode" section). a2h-execute automatically invokes arkts-i18n after Stage 0 completes.

**Report section:**
Add a "Language Resources" section to the conversion report:
```
### Language Resources
- Android languages detected: N (values/, values-en/, values-zh-rCN/, ...)
- HarmonyOS languages generated: M (base/, en_US/, zh_CN/, ...)
- String key count per language: base=X, en_US=X, zh_CN=X
- Key consistency: PASS / FAIL (missing keys listed)
- [TODO: translate] placeholders emitted: K (registered as kind=resource-pending-translation, handed off to arkts-i18n)
- Fallback assets used: M (registered as kind=resource-pending-asset)
```

The pattern: strip the base type prefix (e.g., `values-`, `drawable-`), convert the qualifier to HarmonyOS format, then place resources under the appropriate resource group directory (`element/`, `media/`, or `profile/`).

**Multi-qualifier directories**: Android directories can combine multiple qualifiers with hyphens (e.g., `mipmap-anydpi-v26`, `drawable-night-v21`). Parse ALL qualifiers individually, map each one, strip unsupported ones, and use whatever valid qualifiers remain. Never reject a directory just because one of its qualifiers is unsupported — strip it and keep going. If all qualifiers are stripped, use `base/`.

**Qualifiers to strip** (only these are silently removed):
- API level `v<N>` (e.g., `v26`, `v21`)

**Qualifiers without a HarmonyOS equivalent** (skip entirely):
- Smallest width `sw<N>dp` (e.g., `sw600dp`)
- Available width `w<N>dp` (e.g., `w480dp`)
- Available height `h<N>dp`
- Screen size (`small`, `normal`, `large`, `xlarge`)

These qualifiers have no HarmonyOS mapping. When a directory's only remaining qualifiers (after stripping API level etc.) are from this list, **skip all resources in that directory** and mark them as "unmapped" in the conversion report with reason "Unsupported qualifier: no HarmonyOS equivalent". Do NOT convert them to `base/` or preserve the qualifier as-is — skipping ensures correct conversion output.

**Common example**: `mipmap-anydpi-v26` → qualifiers: `anydpi` (→ `base`) + `v26` (→ strip) → target: `base/media/`. The files inside (typically `<adaptive-icon>` XML) should be processed normally by reading their XML content to determine the type — adaptive-icon XML gets converted to layered-image JSON.

**HarmonyOS qualifier directory naming rules**:
- Language and region are joined by underscore: `zh_CN`, `en_US`
- Multiple qualifier types are separated by hyphens: `zh_CN-dark-ldpi`
- Order: MCC_MNC-language_script_country/region-orientation-device-colormode-density

**Orientation mapping**:
- `land` → `horizontal`
- `port` → `vertical`

**Night mode mapping**:
- `night` → `dark`
- `notnight` → `light`

**Handling values with non-mappable qualifiers** (e.g., `values-sw600dp`, `values-w480dp`, `values-w600dp`):
These directories contain value resources qualified by screen-size constraints that HarmonyOS does not support. **Skip all resources in these directories** and mark them as "unmapped" in the conversion report with reason "Unsupported qualifier: `sw600dp` / `w480dp` / etc. — no HarmonyOS equivalent". Do NOT convert them to `base/element/` or preserve the qualifier as-is.

#### 4.3 Value Format Conversions

When converting `values/*.xml` to HarmonyOS JSON format:

**Colors**:
- Android `#RRGGBB` → HarmonyOS `#ffRRGGBB` (prepend `ff` for full opacity)
- Android `#AARRGGBB` → HarmonyOS `#AARRGGBB` (already in correct format, HarmonyOS uses same order)
- Android `#RGB` → expand to `#ffRRGGBB`
- Android `#ARGB` → expand to `#AARRGGBB`

**Dimensions** (for `dimens.xml` → `float.json`):
- `dp` → `vp` (virtual pixels, similar concept)
- `sp` → `fp` (font pixels)
- `px` → keep as `px`
- Plain numbers → append `vp`

**Strings**:
- XML entities (`&amp;`, `&lt;`, `&gt;`, `&quot;`, `&apos;`) → decoded characters
- `\n`, `\t` → preserved
- CDATA sections → extract text content
- String format placeholders (`%1$s`, `%2$d`) → preserved (HarmonyOS uses same format)

**Booleans**:
- `"true"` / `"false"` → `true` / `false` (as JSON booleans)

**Plurals**:
- Android quantities: `zero`, `one`, `two`, `few`, `many`, `other`
- HarmonyOS quantities: `zero`, `one`, `two`, `few`, `many`, `other` (same set)

### Step 5: Analyze and Resolve Resource Dependencies

Android resources often reference other resources using `@type/name` syntax (e.g., `@color/primary`, `@drawable/icon`). Dependency analysis runs regardless of whether resources came from a decompiled APK or source `res/` — the difference is that source-based conversion may have more unresolvable references because library resources are absent.

Read `references/dependency-analysis-rules.md` for the complete dependency extraction patterns.

#### 5.1 Build a Resource Value Lookup Table

Before resolving references, build a complete lookup table from whichever resource source is being used. This table maps every resource name to its concrete value:

- **Value resources** (`colors.xml`, `dimens.xml`, `strings.xml`, etc.): parse all `values*/*.xml` files and build `type → name → value` mappings across all qualifier directories
- **File resources** (`drawable/`, `mipmap/`): record `type → name → file_path` for each image or XML drawable

When working from source `res/`, this table will be **incomplete** — it won't contain resources defined in library dependencies. That's expected. The dependency analysis in Step 5.3 will identify these gaps.

#### 5.2 Resolve References to True Values

Scan all converted HarmonyOS resource files and replace resource references with their resolved concrete values:

**In element JSON files** (`color.json`, `float.json`, `string.json`, etc.):
- If a value field contains a HarmonyOS reference like `$color:name`, `$float:name`, `$string:name`, etc., look up the referenced resource in the lookup table
- Replace the reference with the actual resolved value
- Follow reference chains (resource A → resource B → concrete value) up to 5 levels deep to handle transitive references
- If a reference cannot be resolved (e.g., it points to a library resource not in source `res/`, or to a theme attribute `?attr/name`), keep the reference as-is and log it in the report

**Example — color reference resolution:**
```json
// Before resolution:
{"name": "primary_light", "value": "$color:primary"}

// After resolution (primary resolves to #ff6200EE):
{"name": "primary_light", "value": "#ff6200EE"}
```

**Example — dimension reference resolution:**
```json
// Before resolution:
{"name": "margin_double", "value": "$float:margin_base"}

// After resolution (margin_base resolves to "16vp"):
{"name": "margin_double", "value": "16vp"}
```

**In SVG files** (converted XML drawables):
- If a fill or stroke color was a resource reference, resolve it to the actual hex color during SVG generation
- If a dimension was a resource reference, resolve it to the actual numeric value

**In layered-image JSON files**:
- `@drawable/xxx` and `@mipmap/xxx` references → keep as `$media:xxx` (these are file references, not value references — the files themselves are converted)
- `@color/xxx` references → resolve to hex and generate solid-color PNG (as described in section 4.1.1)

#### 5.3 Verify All Dependencies Are Satisfied

After resolution, scan all converted resources for any remaining unresolved references:

1. **Converted resource dependencies**: check that every `$media:xxx`, `$color:xxx`, `$float:xxx`, etc. reference in converted files points to an existing resource in the HarmonyOS output
2. **Layout and menu file dependencies**: scan all `layout*/` and `menu/` files from the resource source for `@type/name` references. Even though layouts and menus won't be migrated as-is (ArkUI uses declarative UI), the resources they reference — strings, colors, drawables, dimensions — must exist in the converted output so the developer has everything needed when rebuilding the UI
3. Mark each dependency as **satisfied** or **unsatisfied**
4. **When using source `res/`**: unsatisfied dependencies are expected — they likely come from library resources. Parse `build.gradle` / `build.gradle.kts` to identify declared library dependencies (e.g., AndroidX, Material Components, third-party libraries). In the report, correlate unsatisfied references with likely library sources where possible (e.g., `@color/material_xxx` likely comes from Material Components library)

### Step 6: Verify Completeness

After conversion and dependency resolution, verify the output:

1. Build a list of all resource files found in the resource source directory
2. For each, check if it was converted or marked as unmappable
3. For converted resources, verify the target file exists in the HarmonyOS project
4. For `values/*.xml` entries, verify each individual resource entry (string, color, dimen, etc.) appears in the corresponding JSON file
5. Flag any resources that were missed
6. Verify all dependencies from converted resources are satisfied (all references resolved to true values)
7. Verify all dependencies from layout and menu files are satisfied — any missing resources should appear in the Unsatisfied Dependencies section of the report

### Step 7: Generate Report

Output a conversion report with these sections:

```
# Android to HarmonyOS Resource Conversion Report

## Build Status
- Build attempted: Yes/No
- Build result: Success / Failed / Skipped
- Build error (if failed): <error summary>
- APK source: <"freshly built" / "cached previous build" / "none — using source res/">
- Resource source: <"decompiled APK (complete)" / "source res/ (may be missing library resources)">
- Resource source path: <path>

⚠️ **Note** (if source res/ was used): Resources were converted from the project's source `res/` directory because no APK was available. Library-provided resources (from Maven dependencies, AARs) are NOT included. References to library resources will appear as unsatisfied dependencies below. To get a complete conversion with all library resources, fix the build and re-run.

## Library Dependencies (from build.gradle)
Libraries declared in the project's build.gradle that may provide resources:
| Library | Group:Artifact | Likely Resource Prefixes |
|---|---|---|
| Material Components | com.google.android.material:material | @color/material_*, @dimen/material_*, @style/Widget.Material* |
| AndroidX AppCompat | androidx.appcompat:appcompat | @color/abc_*, @drawable/abc_* |
| ... | ... | ... |

(This section helps identify which unsatisfied dependencies come from which libraries.)

## Summary
- Resource source: <decompiled APK / source res/>
- Total Android resource files found: <count>
- Successfully converted: <count>
- Unmappable (no HarmonyOS equivalent): <count>
- Failed: <count>
- Resource references resolved: <count>
- Unresolved references (library resources missing): <count>
- Unresolved references (other reasons): <count>

## Conversion Details

### Successfully Converted Resources
| Android Source | HarmonyOS Target | Type | Notes |
|---|---|---|---|
| res/values/strings.xml | resources/base/element/string.json | values→element | 25 strings converted |
| res/drawable/icon.png | resources/base/media/icon.png | media copy | Direct copy |
| res/drawable-hdpi/bg.png | resources/ldpi/media/bg.png | qualified media | hdpi→ldpi |
| ... | ... | ... | ... |

### Qualifier Mappings Applied
| Android Qualifier Dir | HarmonyOS Qualifier Dir | Files Converted |
|---|---|---|
| drawable-hdpi | ldpi/media | 5 |
| values-ar | ar/element | 3 |
| ... | ... | ... |

### Resource Reference Resolution
References in converted resources that were resolved to their actual values.

| Resource File | Reference | Resolved Value | Resolution Chain |
|---|---|---|---|
| base/element/color.json → primary_light | $color:primary | #ff6200EE | @color/primary → @color/material_blue_500 → #6200EE |
| base/element/float.json → margin_double | $float:margin_base | 16vp | @dimen/margin_base → 16dp → 16vp |
| ... | ... | ... | ... |

### Layout & Menu Resource Dependencies
Dependencies from layout/menu files (not converted to HarmonyOS, but needed when rebuilding the UI in ArkUI).

| Source File (not converted) | Dependencies | All Satisfied? |
|---|---|---|
| layout/activity_main.xml | @string/app_name ✅, @drawable/bg_header ✅, @color/primary ✅ | Yes |
| layout/fragment_settings.xml | @string/settings_title ✅, @drawable/ic_back ❌ (library) | No |
| menu/main_menu.xml | @string/menu_share ✅, @drawable/ic_share ❌ (library) | No |
| ... | ... | ... |

### Unmappable Resources
| Android Source | Reason |
|---|---|
| res/layout/activity_main.xml | Layout XML has no HarmonyOS equivalent (use ArkUI) |
| res/drawable/ripple_effect.xml | XML drawable not supported |
| ... | ... |

### Unmapped Resources (Unsupported Qualifiers)
| Android Source Dir | Qualifier | Reason |
|---|---|---|
| res/values-sw600dp/ | sw600dp | No HarmonyOS equivalent — skipped |
| res/values-w480dp/ | w480dp | No HarmonyOS equivalent — skipped |
| ... | ... | ... |

### Unresolved References
| Resource File | Reference | Reason | Likely Source |
|---|---|---|---|
| drawable/bg_themed.xml | ?attr/colorSurface | Theme attribute — cannot resolve statically | N/A |
| element/color.json → material_blue | @color/design_default_color_primary | Library resource not in source res/ | com.google.android.material:material |
| ... | ... | ... | ... |

### Failed Conversions
| Android Source | Error |
|---|---|
| ... | ... |

### Verification Results
- All resources accounted for: Yes/No
- Missing resources: <list if any>
- All references resolved: Yes/No
- Unresolved references: <count> (<count> due to missing library resources, <count> other)

### Translation / Asset Placeholders (registered in placeholder-registry; downstream handling delegated to arkts-i18n / build-loop trigger)
- `[TODO: translate]` placeholders (kind=resource-pending-translation): K entries → handed off to `arkts-i18n` skill automatically after a2h-execute Stage 0 completes
- Fallback assets (kind=resource-pending-asset): M entries → closed via the build-loop `<resource-id> ready` trigger
- Full entries listed in `spec/placeholder-registry.md`
```

## Important Notes

- Always read `references/conversion-rules.md` for the complete, detailed conversion rules before starting conversions. The tables above are summaries.
- **Build is best-effort**: The APK build + decompilation is attempted first because the decompiled APK is the most complete resource source (it includes library dependencies). But if the build fails, conversion proceeds from source `res/` — a partial conversion with clear reporting is far more useful than no conversion at all.
- **XML drawable conversion is critical**: Android XML drawables (`<vector>`, `<shape>`, `<layer-list>`, `<selector>`) must be converted to SVG format, not skipped. HarmonyOS supports SVG in `media/`. Read `references/xml-drawable-to-svg-rules.md` for the detailed conversion rules for each drawable type.
- **Dependency analysis always runs**: Read `references/dependency-analysis-rules.md` for the complete dependency extraction patterns and reference formats. Even when converting from source `res/` with missing library resources, dependency analysis is essential — it tells the developer exactly which references are broken and why, so they can address them manually or fix the build.
- **APK decompilation**: The skill bundles `apktool_3.0.1.jar` in the `tools/` directory. Java must be available in the system PATH.
- When parsing Android XML resource files, handle XML namespaces, comments, and attributes correctly.
- For `values/` XML files, each `<resources>` element can contain multiple resource entries — extract ALL of them.
- When multiple Android value files contribute to the same HarmonyOS JSON file (e.g., both `strings.xml` and custom `app_strings.xml` both contain `<string>` entries), merge them into a single JSON file.
- Preserve resource names exactly as they appear in Android (they serve as identifiers).
- If an element JSON file (like `string.json`) already exists from the template, merge new entries into it rather than overwriting — but template defaults can be replaced if they conflict.
