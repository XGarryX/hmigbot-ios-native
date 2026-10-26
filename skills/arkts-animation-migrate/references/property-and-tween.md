# 原生属性、补间与物理动画迁移

源输入为 SwiftUI withAnimation / animation(value:) / transition、UIKit UIView.animate / UIViewPropertyAnimator、Core Animation 的实际调用。先读取时长、delay、curve、重复/反转、起止状态、完成/取消、interruptibility、layer presentation/model state 与生命周期。

## 1. 补间 → 目标属性动画

SwiftUI opacity/scaleEffect/rotationEffect/offset 或 UIView alpha/transform 的状态变化，可选择目标 .animation / animateTo。UIKit duration 常为秒，目标示例通常为毫秒；按实际 API 单位换算。示例不是源项目事实。

## 2. 属性编排

UIViewPropertyAnimator 的暂停/继续/反向/取消，以及 CAAnimationGroup / CAKeyframeAnimation 的 keyTimes、fillMode、removedOnCompletion 与 delegate，不能用一个立即完成的回调替代。目标编排与示例复用 [explicit-animation.md](../../arkts-animation-builder/references/explicit-animation.md)。串行、并行和逐帧值分别保存证据，不凭数组顺序推定时间关系。

## 3. 弹簧

读取 SwiftUI spring 参数、UIKit damping/initial velocity 或 CASpringAnimation 的 mass/stiffness/damping/initialVelocity。目标 spring 曲线需按其 SDK 参数语义核验；没有普适的数值直接照抄公式。保留取消和交互驱动进度，参数不明则记录待验证项。

## 4. 曲线

线性/easeIn/easeOut/easeInOut 或 CAMediaTimingFunction 控制点可作为目标曲线候选。保持延迟、单位和控制点顺序；不能用近似弹簧宣称像素/时序完全一致。

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

### 5.5 源布局单位与目标尺寸

保留源点坐标、坐标空间、布局约束与实际图片 scale；不能把像素直接当目标逻辑尺寸，不能用全局倍率替代逐图/逐布局证据。动画路径、旋转中心和测量时机必须一起核对。
