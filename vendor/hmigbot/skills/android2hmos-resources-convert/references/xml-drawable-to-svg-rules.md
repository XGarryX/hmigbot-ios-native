# Android XML Drawable to SVG Conversion Rules

This document provides complete rules for converting Android XML drawable resources to SVG format for HarmonyOS. HarmonyOS natively supports SVG in `media/` directories, making SVG the ideal target format for XML drawables that would otherwise be lost in migration.

## Table of Contents
1. [General Principles](#general-principles)
2. [VectorDrawable Conversion](#vectordrawable-conversion)
3. [ShapeDrawable Conversion](#shapedrawable-conversion)
4. [LayerList Conversion](#layerlist-conversion)
5. [Selector / StateList Conversion](#selector--statelist-conversion)
6. [Gradient Conversion](#gradient-conversion)
7. [Common Attribute Mapping](#common-attribute-mapping)
8. [Unconvertible Types](#unconvertible-types)

---

## General Principles

- Output files use the original Android filename with `.svg` extension (e.g., `ic_arrow.xml` → `ic_arrow.svg`)
- All SVG output should use the SVG 1.1 namespace: `xmlns="http://www.w3.org/2000/svg"`
- Android uses `dp` units for dimensions; convert to unitless numbers in SVG (1dp = 1 SVG user unit)
- Android colors use `#AARRGGBB` or `#RRGGBB`; SVG uses `#RRGGBB` with a separate `opacity` or `fill-opacity` attribute for alpha
- When a drawable XML references another resource (`@drawable/other`, `@color/primary`), resolve the reference if possible. If not resolvable, use a reasonable default and log it in the report.

### Color Conversion (Android → SVG)

| Android Format | SVG Fill/Stroke | SVG Opacity |
|---|---|---|
| `#RRGGBB` | `#RRGGBB` | (none, fully opaque) |
| `#AARRGGBB` | `#RRGGBB` | `opacity="AA/255"` as decimal (e.g., `#80FF0000` → `fill="#FF0000" fill-opacity="0.502"`) |
| `#RGB` | Expand to `#RRGGBB` | (none) |
| `#ARGB` | Expand to `#RRGGBB` | Extract alpha as decimal |

### Dimension Conversion

- `24dp` → `24` (strip `dp` suffix, use as unitless SVG user units)
- `@dimen/ref` → resolve from dimens.xml if available, otherwise use a default and log

---

## VectorDrawable Conversion

Android VectorDrawable (`<vector>`) is structurally very similar to SVG. This is the most straightforward conversion.

### Android VectorDrawable Example

```xml
<vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:width="24dp"
    android:height="24dp"
    android:viewportWidth="24"
    android:viewportHeight="24"
    android:tint="#FF000000"
    android:alpha="0.8">
    <group
        android:name="arrow_group"
        android:rotation="90"
        android:pivotX="12"
        android:pivotY="12"
        android:scaleX="1.5"
        android:scaleY="1.5"
        android:translateX="2"
        android:translateY="0">
        <path
            android:name="arrow"
            android:pathData="M12,2L4.5,20.29l0.71,0.71L12,18l6.79,3 0.71,-0.71z"
            android:fillColor="#FF4081"
            android:fillAlpha="0.8"
            android:strokeColor="#000000"
            android:strokeWidth="1"
            android:strokeAlpha="1"
            android:strokeLineCap="round"
            android:strokeLineJoin="round"
            android:fillType="evenOdd"
            android:trimPathStart="0"
            android:trimPathEnd="1" />
        <clip-path
            android:name="clip"
            android:pathData="M0,0h24v24H0z" />
    </group>
</vector>
```

### Converted SVG Output

```svg
<svg xmlns="http://www.w3.org/2000/svg"
     width="24" height="24"
     viewBox="0 0 24 24"
     opacity="0.8">
  <g transform="translate(2,0) scale(1.5,1.5) rotate(90,12,12)">
    <defs>
      <clipPath id="clip">
        <path d="M0,0h24v24H0z"/>
      </clipPath>
    </defs>
    <path d="M12,2L4.5,20.29l0.71,0.71L12,18l6.79,3 0.71,-0.71z"
          fill="#FF4081" fill-opacity="0.8"
          stroke="#000000" stroke-width="1"
          stroke-linecap="round" stroke-linejoin="round"
          fill-rule="evenodd"
          clip-path="url(#clip)"/>
  </g>
</svg>
```

### Element Mapping: `<vector>` → `<svg>`

| Android Attribute | SVG Equivalent |
|---|---|
| `android:width` | `width` (strip `dp`) |
| `android:height` | `height` (strip `dp`) |
| `android:viewportWidth` | Part of `viewBox="0 0 W H"` |
| `android:viewportHeight` | Part of `viewBox="0 0 W H"` |
| `android:alpha` | `opacity` on root `<svg>` |
| `android:tint` | Apply as a filter or ignore (SVG has no direct tint; log in report) |

### Element Mapping: `<path>` → `<path>`

| Android Attribute | SVG Attribute |
|---|---|
| `android:pathData` | `d` (path data syntax is identical) |
| `android:fillColor` | `fill` (convert color format) |
| `android:fillAlpha` | `fill-opacity` |
| `android:strokeColor` | `stroke` (convert color format) |
| `android:strokeWidth` | `stroke-width` |
| `android:strokeAlpha` | `stroke-opacity` |
| `android:strokeLineCap` | `stroke-linecap` (`butt`, `round`, `square`) |
| `android:strokeLineJoin` | `stroke-linejoin` (`miter`, `round`, `bevel`) |
| `android:strokeMiterLimit` | `stroke-miterlimit` |
| `android:fillType` | `fill-rule` (`nonZero` → `nonzero`, `evenOdd` → `evenodd`) |
| `android:trimPathStart` | No direct SVG equivalent; if != 0, use `stroke-dasharray` + `stroke-dashoffset` to approximate, or log |
| `android:trimPathEnd` | Same as above |
| `android:trimPathOffset` | Same as above |

### Element Mapping: `<group>` → `<g>`

Build the SVG `transform` attribute from the group's transformation properties. Apply in this order:
1. `translate(translateX, translateY)`
2. `scale(scaleX, scaleY)`
3. `rotate(rotation, pivotX, pivotY)`

Combined: `transform="translate(tX,tY) scale(sX,sY) rotate(r,pX,pY)"`

Only include transform components that differ from defaults (translate 0,0; scale 1,1; rotation 0).

### Element Mapping: `<clip-path>` → `<clipPath>` + `<path>`

```xml
<!-- Android -->
<clip-path android:pathData="M0,0h24v24H0z"/>

<!-- SVG -->
<defs>
  <clipPath id="generated_clip_id">
    <path d="M0,0h24v24H0z"/>
  </clipPath>
</defs>
<!-- Apply via clip-path="url(#generated_clip_id)" on sibling paths -->
```

Generate unique IDs for clip paths (e.g., `clip_1`, `clip_2`, or derive from `android:name`).

---

## ShapeDrawable Conversion

Android `<shape>` drawables define geometric shapes with fill, stroke, gradients, corners, and sizing.

### Shape Types

#### Rectangle (default)

```xml
<!-- Android -->
<shape xmlns:android="http://schemas.android.com/apk/res/android"
    android:shape="rectangle">
    <solid android:color="#FF4081"/>
    <stroke android:width="2dp" android:color="#000000"
            android:dashWidth="4dp" android:dashGap="2dp"/>
    <corners android:radius="8dp"/>
    <size android:width="100dp" android:height="50dp"/>
    <padding android:left="10dp" android:top="5dp"
             android:right="10dp" android:bottom="5dp"/>
</shape>
```

```svg
<!-- SVG -->
<svg xmlns="http://www.w3.org/2000/svg" width="100" height="50" viewBox="0 0 100 50">
  <rect x="0" y="0" width="100" height="50" rx="8" ry="8"
        fill="#FF4081"
        stroke="#000000" stroke-width="2"
        stroke-dasharray="4,2"/>
</svg>
```

**Corner radius variants:**
- `android:radius` → `rx` and `ry` (same value)
- `android:topLeftRadius`, `android:topRightRadius`, `android:bottomRightRadius`, `android:bottomLeftRadius` → When different per corner, use a `<path>` with rounded corner arcs instead of `<rect>`

**Per-corner radius SVG path formula:**
```
M {tlr},0
H {w-trr}
Q {w},0 {w},{trr}
V {h-brr}
Q {w},{h} {w-brr},{h}
H {blr}
Q 0,{h} 0,{h-blr}
V {tlr}
Q 0,0 {tlr},0
Z
```
Where `tlr`=topLeftRadius, `trr`=topRightRadius, `brr`=bottomRightRadius, `blr`=bottomLeftRadius, `w`=width, `h`=height.

#### Oval

```xml
<!-- Android -->
<shape android:shape="oval">
    <solid android:color="#2196F3"/>
    <size android:width="60dp" android:height="60dp"/>
</shape>
```

```svg
<!-- SVG -->
<svg xmlns="http://www.w3.org/2000/svg" width="60" height="60" viewBox="0 0 60 60">
  <ellipse cx="30" cy="30" rx="30" ry="30" fill="#2196F3"/>
</svg>
```

- If width == height, use `<circle>` instead: `<circle cx="30" cy="30" r="30"/>`

#### Line

```xml
<!-- Android -->
<shape android:shape="line">
    <stroke android:width="2dp" android:color="#000000"/>
    <size android:height="2dp" android:width="100dp"/>
</shape>
```

```svg
<!-- SVG -->
<svg xmlns="http://www.w3.org/2000/svg" width="100" height="2" viewBox="0 0 100 2">
  <line x1="0" y1="1" x2="100" y2="1" stroke="#000000" stroke-width="2"/>
</svg>
```

#### Ring

```xml
<!-- Android -->
<shape android:shape="ring"
    android:innerRadius="20dp"
    android:thickness="5dp">
    <solid android:color="#4CAF50"/>
    <size android:width="50dp" android:height="50dp"/>
</shape>
```

```svg
<!-- SVG -->
<svg xmlns="http://www.w3.org/2000/svg" width="50" height="50" viewBox="0 0 50 50">
  <circle cx="25" cy="25" r="22.5"
          fill="none" stroke="#4CAF50" stroke-width="5"/>
</svg>
```

- Ring center radius = `innerRadius + thickness/2`
- SVG stroke-width = `thickness`
- If `android:innerRadiusRatio` is used instead of `android:innerRadius`: `innerRadius = width / (2 * innerRadiusRatio)`
- If `android:thicknessRatio` is used: `thickness = width / (2 * thicknessRatio)`

### Shape Size Handling

If `<size>` is not specified, use a sensible default (e.g., `24x24`) and note in the report that the original had no explicit size. The SVG `viewBox` should match the dimensions.

---

## Gradient Conversion

Android shapes and vector drawables can use gradients for fill or stroke colors.

### Linear Gradient

```xml
<!-- Android (in shape) -->
<gradient
    android:type="linear"
    android:startColor="#FF0000"
    android:centerColor="#00FF00"
    android:endColor="#0000FF"
    android:angle="45"/>
```

```svg
<!-- SVG -->
<defs>
  <linearGradient id="grad_1" x1="0%" y1="100%" x2="100%" y2="0%">
    <stop offset="0%" stop-color="#FF0000"/>
    <stop offset="50%" stop-color="#00FF00"/>
    <stop offset="100%" stop-color="#0000FF"/>
  </linearGradient>
</defs>
<rect ... fill="url(#grad_1)"/>
```

**Angle to coordinates mapping:**

| Android `angle` | SVG `x1,y1 → x2,y2` |
|---|---|
| 0 (left→right) | `0%,0% → 100%,0%` |
| 45 (bottom-left→top-right) | `0%,100% → 100%,0%` |
| 90 (bottom→top) | `0%,100% → 0%,0%` |
| 135 (bottom-right→top-left) | `100%,100% → 0%,0%` |
| 180 (right→left) | `100%,0% → 0%,0%` |
| 225 (top-right→bottom-left) | `100%,0% → 0%,100%` |
| 270 (top→bottom) | `0%,0% → 0%,100%` |
| 315 (top-left→bottom-right) | `0%,0% → 100%,100%` |

Android `angle` must be a multiple of 45. For other values, calculate:
- `x1 = 50 + 50*cos(angle+180)`, `y1 = 50 - 50*sin(angle+180)`
- `x2 = 50 + 50*cos(angle)`, `y2 = 50 - 50*sin(angle)`

### Radial Gradient

```xml
<!-- Android -->
<gradient
    android:type="radial"
    android:centerX="0.5"
    android:centerY="0.5"
    android:gradientRadius="50%p"
    android:startColor="#FFFFFF"
    android:endColor="#000000"/>
```

```svg
<!-- SVG -->
<defs>
  <radialGradient id="grad_2" cx="50%" cy="50%" r="50%">
    <stop offset="0%" stop-color="#FFFFFF"/>
    <stop offset="100%" stop-color="#000000"/>
  </radialGradient>
</defs>
```

- `centerX`/`centerY` are fractions (0.0–1.0) → convert to percentages
- `gradientRadius` with `%p` suffix → percentage of parent dimension

### Sweep Gradient

```xml
<!-- Android -->
<gradient
    android:type="sweep"
    android:centerX="0.5"
    android:centerY="0.5"
    android:startColor="#FF0000"
    android:endColor="#0000FF"/>
```

SVG doesn't have a native sweep/conic gradient in SVG 1.1. Options:
1. Use CSS `conic-gradient` if targeting modern renderers (but not SVG 1.1 compliant)
2. Approximate with a series of `<path>` segments in a radial pattern
3. Log as partially converted and note that sweep gradient was approximated

Recommended: convert to a `<linearGradient>` as an approximation and log in the report that the original was a sweep gradient.

### Gradient in VectorDrawable Paths

Android API 24+ supports `<aapt:attr>` inline gradient in vector drawables:

```xml
<path android:pathData="...">
    <aapt:attr name="android:fillColor">
        <gradient android:type="linear" .../>
    </aapt:attr>
</path>
```

Convert the gradient to an SVG `<linearGradient>` in `<defs>` and reference via `fill="url(#grad_id)"`.

---

## LayerList Conversion

`<layer-list>` stacks multiple drawable items. Each `<item>` can contain a `<shape>`, a `<bitmap>`, or reference another drawable.

```xml
<!-- Android -->
<layer-list xmlns:android="http://schemas.android.com/apk/res/android">
    <item>
        <shape android:shape="rectangle">
            <solid android:color="#CCCCCC"/>
            <corners android:radius="4dp"/>
        </shape>
    </item>
    <item android:left="2dp" android:top="2dp"
          android:right="2dp" android:bottom="2dp">
        <shape android:shape="rectangle">
            <solid android:color="#FFFFFF"/>
            <corners android:radius="2dp"/>
        </shape>
    </item>
</layer-list>
```

```svg
<!-- SVG -->
<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100" viewBox="0 0 100 100">
  <!-- Layer 0: background -->
  <rect x="0" y="0" width="100" height="100" rx="4" ry="4" fill="#CCCCCC"/>
  <!-- Layer 1: foreground with insets -->
  <rect x="2" y="2" width="96" height="96" rx="2" ry="2" fill="#FFFFFF"/>
</svg>
```

### Rules

- Items are rendered in document order (first item = bottom layer)
- `android:left/top/right/bottom` on `<item>` → inset the element's position and reduce its size accordingly
- `android:width/height` on `<item>` → explicit size override
- `android:gravity` on `<item>` → position within the layer bounds
- If an `<item>` references another drawable via `android:drawable="@drawable/other"`, try to resolve and inline it; if not resolvable, log in report
- For layer-lists without explicit `<size>`, use a default canvas of `100x100` and note in report

---

## Selector / StateList Conversion

`<selector>` defines different drawables for different UI states (pressed, focused, disabled, etc.). SVG is static, so we extract the most useful representation.

```xml
<!-- Android -->
<selector xmlns:android="http://schemas.android.com/apk/res/android">
    <item android:state_pressed="true">
        <shape android:shape="rectangle">
            <solid android:color="#E0E0E0"/>
            <corners android:radius="4dp"/>
        </shape>
    </item>
    <item android:state_focused="true">
        <shape android:shape="rectangle">
            <solid android:color="#F0F0F0"/>
            <corners android:radius="4dp"/>
        </shape>
    </item>
    <item>
        <shape android:shape="rectangle">
            <solid android:color="#FFFFFF"/>
            <corners android:radius="4dp"/>
        </shape>
    </item>
</selector>
```

### Conversion Strategy

1. Find the **default item** — the `<item>` with no `android:state_*` attributes (or the last item, which serves as the default in Android)
2. Convert that single item to SVG using the appropriate rules (shape → SVG, vector → SVG, etc.)
3. In the conversion report, list all the state variants that were dropped:
   - `state_pressed`, `state_focused`, `state_selected`, `state_checked`, `state_enabled`, `state_activated`, `state_hovered`
4. Note that HarmonyOS state handling should be done in ArkUI component code, not in resource files

---

## Common Attribute Mapping

### Android `android:` namespace to SVG

| Android Attribute | SVG Equivalent | Notes |
|---|---|---|
| `android:fillColor` | `fill` | Convert color format |
| `android:strokeColor` | `stroke` | Convert color format |
| `android:strokeWidth` | `stroke-width` | Strip `dp` |
| `android:alpha` | `opacity` | 0.0-1.0 range |
| `android:fillAlpha` | `fill-opacity` | 0.0-1.0 range |
| `android:strokeAlpha` | `stroke-opacity` | 0.0-1.0 range |
| `android:rotation` | `transform="rotate(deg)"` | In `<group>` |
| `android:scaleX/Y` | `transform="scale(x,y)"` | In `<group>` |
| `android:translateX/Y` | `transform="translate(x,y)"` | In `<group>` |

### Default Values

If an Android drawable doesn't specify certain attributes, use these defaults:
- `fillColor`: `#000000` (black) for paths in `<vector>`, transparent for shapes without `<solid>`
- `strokeWidth`: `0` (no stroke)
- `alpha`: `1.0`
- `fillType`: `nonZero`

---

## Unconvertible Types

These XML drawable types cannot be meaningfully converted to SVG and should be logged as unmappable in the conversion report:

| Type | Root Element | Reason |
|---|---|---|
| Ripple | `<ripple>` | Runtime touch feedback animation |
| Animated Vector | `<animated-vector>` | Requires animation timing/interpolation |
| Animated Selector | `<animated-selector>` | State transitions with animations |
| Transition Drawable | `<transition>` | Cross-fade between two drawables |
| Inset Drawable | `<inset>` | Simple wrapper; if inner drawable is convertible, convert that instead |
| Scale Drawable | `<scale>` | Runtime scaling behavior |
| Rotate Drawable | `<rotate>` | Runtime rotation; could be converted as static rotation if angle is fixed |
| Level List | `<level-list>` | Runtime level-based selection |

For `<inset>` and `<rotate>` with fixed values, attempt conversion by applying the inset/rotation statically and convert the inner drawable. Log in the report either way.
