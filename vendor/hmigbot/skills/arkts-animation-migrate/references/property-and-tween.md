# 属性动画 / 补间动画 / 物理动画 迁移参考

**适用判定**：Android 端命中以下任意一项：
- `<set>/<alpha>/<scale>/<rotate>/<translate>` 在 `res/anim/*.xml` → **补间动画 (Tween/View Animation)**
- `<objectAnimator>/<animator>` 在 `res/animator/*.xml` → **属性动画 (Property Animation)**
- 代码 `ObjectAnimator.ofFloat(...)` / `ValueAnimator.ofXxx(...)` / `view.animate().translationX(...)` → **属性动画**
- `SpringAnimation(...)` / `FlingAnimation(...)` / `DynamicAnimation` → **物理动画**

ArkTS 端三类共享同一套 API 体系：`.animation()` 隐式 + `animateTo()` 显式 + `curves.*` 曲线。

---

## 1. 补间动画 (Tween) → `.animation()` + transform

### 标签对照表

| Android XML 标签 | ArkTS 等价 |
|---|---|
| `<alpha android:fromAlpha="0" toAlpha="1" duration="300"/>` | `.opacity(this.show ? 1 : 0).animation({ duration: 300, curve: Curve.Linear })` |
| `<scale fromXScale="0" toXScale="1" pivotX="50%"/>` | `.scale({ x: this.show ? 1 : 0, y: this.show ? 1 : 0, centerX: '50%' }).animation({...})` |
| `<rotate fromDegrees="0" toDegrees="360"/>` | `.rotate({ angle: this.angle }).animation({...})` |
| `<translate fromXDelta="-100%" toXDelta="0"/>` | `.translate({ x: this.x }).animation({...})` |
| `<set>` 嵌套（默认并行） | 一个 `.animation()` 修饰符 + 多属性同时改即并行 |
| `<set ordering="sequentially">` | 用 `animateTo` + `onFinish` 嵌套（见 §2.3） |

### 完整示例

Android：
```xml
<!-- res/anim/fade_scale_in.xml -->
<set xmlns:android="http://schemas.android.com/apk/res/android"
     android:duration="300"
     android:interpolator="@android:interpolator/decelerate_quad">
  <alpha android:fromAlpha="0" android:toAlpha="1"/>
  <scale android:fromXScale="0.8" android:toXScale="1"
         android:fromYScale="0.8" android:toYScale="1"
         android:pivotX="50%" android:pivotY="50%"/>
</set>
```

ArkTS：
```typescript
SomeView()
  .opacity(this.show ? 1 : 0)
  .scale({
    x: this.show ? 1 : 0.8,
    y: this.show ? 1 : 0.8,
    centerX: '50%',
    centerY: '50%'
  })
  .animation({ duration: 300, curve: Curve.EaseOut })
```

---

## 2. 属性动画 (Property Animation)

### 2.1 ObjectAnimator / ViewPropertyAnimator → `.animation()` 隐式

**适用**：简单单属性、纯 UI 状态切换。

**Android → ArkTS API 映射**：
- `view.animate().translationY(100f).setDuration(300).start()`
- → ArkTS（V2）：`@Local translateY`（V1 项目则 `@State translateY`）+ `.translate({ y }).animation({ duration: 300 })` + 改 state 触发

**完整 ArkTS 代码示例**（BounceButton / ExpandableCard 等）：see [arkts-animation-builder/references/explicit-animation.md §1](../../arkts-animation-builder/references/explicit-animation.md)。

### 2.2 ValueAnimator with Listener → `animateTo` 显式

**适用**：动画过程中精确控制中间值、执行回调、组合多属性。

**Android → ArkTS API 映射**：
- `ValueAnimator.ofFloat(...) + addUpdateListener + addListener(onAnimationEnd)`
- → ArkTS（V2）：`animateTo({ duration, curve, onFinish }, () => { 改多个 @Local })`（V1 项目用 `@State`）

**完整 ArkTS 代码示例**（多属性同时动画 + onFinish 回调）：see [arkts-animation-builder/references/explicit-animation.md §6](../../arkts-animation-builder/references/explicit-animation.md)。

### 2.3 AnimatorSet 串行/并行

**Android → ArkTS 编排映射**：

| Android | ArkTS |
|---|---|
| `AnimatorSet().playTogether(animA, animB)` | 一个 `animateTo` 内改多个 `@Local`（V1 用 `@State`）（自动并行） |
| `AnimatorSet().playSequentially(animA, animB)` | `animateTo({ onFinish: ... }, ...)` 嵌套（2 步） |
| 3 步以上串行编排 | 改用 `keyframeAnimateTo({ iterations }, [{ duration, event }, ...])` |

**完整 ArkTS 串行 demo**（链式 animateTo + 4 步序列动画）：see [arkts-animation-builder/references/explicit-animation.md §7](../../arkts-animation-builder/references/explicit-animation.md)。

---

## 3. 物理动画 / Spring → `curves.springMotion` / `springCurve`

**Android → ArkTS API 映射**：
- `SpringAnimation(view, ...).apply { spring = SpringForce(...).setStiffness(...).setDampingRatio(...) }.start()`
- → ArkTS 简化参数：`animateTo({ curve: curves.springMotion(response, dampingFraction) }, () => {...})`
- → ArkTS 完整参数：`animateTo({ curve: curves.springCurve(velocity, mass, stiffness, damping) }, () => {...})`

**完整 ArkTS Spring 示例**（4 种弹簧参数对比 + 触发动画 demo）：see [arkts-animation-builder/references/explicit-animation.md §8](../../arkts-animation-builder/references/explicit-animation.md)。

### Android SpringForce 参数 → ArkTS 折算（迁移独有）

| Android | ArkTS `springCurve` 参数 |
|---|---|
| `setStiffness(STIFFNESS_LOW)` (200) | stiffness ≈ 200 |
| `setStiffness(STIFFNESS_MEDIUM)` (1500) | stiffness ≈ 1500 |
| `setStiffness(STIFFNESS_HIGH)` (10000) | stiffness ≈ 10000 |
| `setDampingRatio(DAMPING_RATIO_LOW_BOUNCY)` (0.3) | damping ≈ stiffness × 0.3 |
| `setDampingRatio(DAMPING_RATIO_MEDIUM_BOUNCY)` (0.5) | damping ≈ stiffness × 0.5 |
| `setDampingRatio(DAMPING_RATIO_NO_BOUNCY)` (1.0) | damping ≈ stiffness × 1.0 |

---

## 4. 插值器 (Interpolator) 映射

| Android | ArkTS Curve |
|---|---|
| `linear_interpolator` | `Curve.Linear` |
| `accelerate_interpolator` | `Curve.EaseIn` |
| `decelerate_interpolator` | `Curve.EaseOut` |
| `accelerate_decelerate_interpolator` | `Curve.EaseInOut` |
| `bounce_interpolator` | `curves.springMotion()` 或 `curves.cubicBezierCurve(0.34, 1.56, 0.64, 1)` |
| `overshoot_interpolator` | `curves.cubicBezierCurve(0.34, 1.56, 0.64, 1)` |
| `anticipate_interpolator` | `curves.cubicBezierCurve(0.36, 0, 0.66, -0.56)` |
| 自定义 PathInterpolator | `curves.cubicBezierCurve(x1, y1, x2, y2)` |

---

## 5. 常见坑

### 5.1 直接改 `@Local`（V1 项目 `@State`）值不包 `animateTo` → 瞬间跳变没过渡

```typescript
// 错
this.x = 200;  // 瞬间跳到 200，没动画

// 对（方式 A：组件加 .animation() 修饰符）
SomeView().translate({ x: this.x }).animation({ duration: 300 })
this.x = 200;   // 此时会动画

// 对（方式 B：包 animateTo）
animateTo({ duration: 300 }, () => { this.x = 200; })
```

### 5.2 `.animation()` 修饰符放错位置 → 只对**它之前**的属性生效

```typescript
// 错：.animation() 在 .opacity 之前 → opacity 不会动画
SomeView()
  .animation({ duration: 300 })
  .opacity(this.show ? 1 : 0)

// 对：.animation() 写在被动画属性之后
SomeView()
  .opacity(this.show ? 1 : 0)
  .animation({ duration: 300 })
```

ArkUI 的 `.animation()` 修饰符是**对它之前的所有可动画属性生效**，类似栅栏。多个 `.animation()` 可以叠加，分段控制不同属性的曲线和时长。

### 5.3 持续型动画用 `setInterval` 改 state → 性能差

错：
```typescript
setInterval(() => {
  this.angle = (this.angle + 5) % 360;
}, 16);
```

对：
- 单纯循环旋转：用 `keyframeAnimateTo({ iterations: -1 }, [...])`
- 复杂动画：用 Lottie

### 5.4 `animateTo` 内部嵌套异步操作

```typescript
// 错：await 之后的 state 改动已经不在 animateTo 上下文，不会动画
animateTo({ duration: 300 }, async () => {
  const data = await loadData();
  this.x = data.x;   // 瞬间跳变
})

// 对：先 await，拿到值再开 animateTo
const data = await loadData();
animateTo({ duration: 300 }, () => {
  this.x = data.x;
})
```

### 5.5 Android `dp` 直接当 ArkTS `vp`

大部分场景可以 1:1，但密度差异大的设备（折叠屏外屏 / 平板）会偏。**建议**：
- 简单场景 1:1 写
- 翻译过程中发现偏，再按 `actualScreenDensity / referenceDensity` 缩放
- 涉及绝对位置的（比如 `position.x = 67`），优先改用百分比或 `Constraint`
