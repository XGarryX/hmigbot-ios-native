# SVG Display Issue Fix Patterns

Common display abnormalities and fixes when migrating SVG/Vector Drawables from Android projects or manually creating SVGs.

---

## Issue 1: viewBox Does Not Match Path Coordinates

### Symptoms
Icon does not display at all, or only shows a blank area.

### Cause
The coordinate range defined by `viewBox` does not match the coordinate data in the `d` attribute of `<path>`.

For example: path data is based on a 512×512 coordinate system (coordinate values range from 85 to 448), but `viewBox` is set to `0 0 24 24`, causing all paths to exceed the visible area.

### Fix

**Option A: Adjust viewBox to Match Path Coordinates (Recommended for Simple Cases)**
```xml
<!-- Wrong: viewBox too small -->
<svg viewBox="0 0 24 24">
  <path d="M101.51,411.23 Q85.21,395.05 ..." />  <!-- coordinates far exceed 24 -->
</svg>

<!-- Fixed: viewBox matches coordinate system, use width/height to control render size -->
<svg width="24" height="24" viewBox="0 0 512 512">
  <path d="M101.51,411.23 Q85.21,395.05 ..." />
</svg>
```

> Note: `viewBox` defines the path coordinate space, while `width`/`height` define the render size. They are independent.

**Option B: Scale Path Coordinates Proportionally (Recommended for Standardization)**

Scale all values in the path proportionally to the target coordinate system. For example, scaling from 512 to 24:

```python
import re

scale = 24.0 / 512.0  # 0.046875

def scale_number(match):
    num = float(match.group(0))
    scaled = round(num * scale, 2)
    return '{:.2f}'.format(scaled).rstrip('0').rstrip('.')

path_data = "M101.51,411.23Q85.21,395.05 85.22,371.75..."
result = re.sub(r'[0-9]+\.?[0-9]*', scale_number, path_data)
```

After scaling, you can use the standard `viewBox="0 0 24 24"`, consistent with other Material Design icons.

---

## Issue 2: Android Vector Drawable Syntax Remnants

### Symptoms
The SVG file contains Android-specific XML attributes that standard SVG renderers cannot parse.

### Common Remnant Syntax

| Android Syntax | Standard SVG Equivalent |
|---------------|----------------------|
| `<group android:translateX="24" android:rotation="90">` | `<g transform="translate(24,0) rotate(90)">` |
| `android:fillColor="#FF000000"` | `fill="#000000"` |
| `android:pathData="..."` | `d="..."` |
| `android:viewportWidth="24"` | Part of `viewBox="0 0 24 24"` |
| `<vector>` root element | `<svg>` root element |
| `<clip-path android:pathData="..."/>` | `<defs><clipPath id="..."><path d="..."/></clipPath></defs>` |

### Fix

Fully convert Android `<group>` transform attributes to SVG `transform`:

```xml
<!-- Android Vector Drawable -->
<group
    android:translateX="24"
    android:translateY="0"
    android:rotation="90"
    android:pivotX="12"
    android:pivotY="12"
    android:scaleX="1.5"
    android:scaleY="1.5">
  <path android:pathData="M18,12l4,-4..." android:fillColor="#FFFFFF"/>
</group>

<!-- Converted to Standard SVG -->
<g transform="translate(24,0) rotate(90,12,12) scale(1.5,1.5)">
  <path d="M18,12l4,-4..." fill="#FFFFFF"/>
</g>
```

Transform order: `translate` → `rotate` (with pivot point) → `scale`

---

## Issue 3: Fill Color is White Causing Invisible Icon

### Symptoms
SVG file exists and path is correct, but icon does not display (invisible on white background).

### Cause
The original Android drawable's `fillColor` is `#FFFFFF` (white), which is invisible on a white background. Common for icons designed to appear on dark ActionBars.

### Fix

Change `fill="#FFFFFF"` to `fill="#000000"` (black), or choose a suitable color based on UI needs:

```xml
<!-- Before fix: white fill invisible on white background -->
<path fill="#FFFFFF" d="M18,12l4,-4..."/>

<!-- After fix -->
<path fill="#000000" d="M18,12l4,-4..."/>
```

---

## Issue 4: Google Material Symbols Coordinate System

### Description
Material Symbols SVGs downloaded from Google Fonts use a special coordinate system:

```xml
<svg xmlns="http://www.w3.org/2000/svg" height="24px" viewBox="0 -960 960 960" width="24px" fill="#000000">
  <path d="M200-120q-33 0-56.5-23.5T120-200v-560..."/>
</svg>
```

- `viewBox="0 -960 960 960"` — Y-axis starts at -960 (positive is upward)
- Many negative values in path coordinates are normal
- This format renders correctly in HarmonyOS, **no additional conversion needed**

---

## Issue 5: HarmonyOS media Directory Does Not Support Subdirectories

### Symptoms
Compilation error: `CompileResource` error "invalid path, not a file"

### Cause
Created subdirectories under `resources/base/media/` (e.g., `media/icons/`, `media/md/`).

### Fix

Move all files from subdirectories to the `media/` root directory, using file name prefixes to distinguish sources:

```bash
# Wrong: using subdirectories
media/
  md/
    share.svg
    home.svg

# Correct: flat storage with prefixes
media/
  md_share.svg
  md_home.svg
  ic_custom_icon.svg
```

---

## Quick Diagnosis Checklist

When SVG icon does not display, check in order:

1. **File exists?** — Confirm the file exists under `entry/src/main/resources/base/media/`
2. **Reference correct?** — `$r('app.media.filename_without_extension')`, filename is case-sensitive
3. **viewBox matches?** — `viewBox` coordinate range must cover path data coordinate values
4. **Syntax standard?** — No `android:` namespace attributes, root element is `<svg>` not `<vector>`
5. **Fill color visible?** — `fill` is not `#FFFFFF` (invisible on white background)
6. **No subdirectories?** — SVG files are directly under `media/` root directory
