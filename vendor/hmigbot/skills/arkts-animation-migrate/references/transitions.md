# 转场 / 共享元素 / 页面进出动画 迁移参考

**适用判定**：Android 端命中以下任意一项：
- `TransitionManager.beginDelayedTransition(...)` / `Scene.getSceneForLayout(...)` → **Transition Framework**
- `ActivityOptions.makeSceneTransitionAnimation(activity, pair)` / `setEnterSharedElementCallback` / `transitionName=` → **共享元素转场**
- `overridePendingTransition(R.anim.in, R.anim.out)` / 主题 `windowAnimationStyle` → **Activity 转场**
- `Fragment` 的 `setEnterTransition` / `setSharedElementEnterTransition` → 同上
- `ConstraintSet` + `MotionScene` + `<Transition>` + `<KeyFrameSet>` → **MotionLayout**

ArkTS 端工具箱：
- `.transition()` 修饰符 — 组件出现/消失时的过渡
- `geometryTransition(id)` — 同页面内组件 → 组件的"一镜到底"
- `sharedTransition(id, opts)` — 跨 Router 页面的共享元素
- `customNavContentTransition(...)` — Navigation 子页面的自定义转场
- `pageTransition()` — Router 页面的整页进出动画

---

## 1. Transition Framework → `.transition()` 修饰符

**Android → ArkTS API 映射**：
- `TransitionManager.beginDelayedTransition(container)` 在容器内监听子布局变化
- → ArkTS：`.transition({ type: Insert/Delete, opacity, scale, ... })` 修饰符 + `if/else` 切换 + 外层 `animateTo` 包状态变更

**关键认知**：`.transition()` 只描述"目标态"（如 `opacity: 0` 表示"出现时 0→1，消失时 1→0"）；时长由外层 `animateTo` 或父容器 `.animation()` 控制。

**完整 ArkTS 代码示例**（淡入淡出 / 滑入 / 缩放 / 非对称转场 等 8+ 模式）：see [arkts-animation-builder/references/transition-patterns.md §1-3](../../arkts-animation-builder/references/transition-patterns.md)。

### Transition 标签对照

| Android Transition 类 | ArkTS `.transition({...})` 配置 |
|---|---|
| `Fade` | `opacity: 0` |
| `Slide(Gravity.LEFT)` | `translate: { x: '-100%' }` |
| `Slide(Gravity.RIGHT)` | `translate: { x: '100%' }` |
| `Explode` | `scale: { x: 1.5, y: 1.5 }` + `opacity: 0` |
| `ChangeBounds` | 用 `geometryTransition(id)`（见 §2） |

---

## 2. 共享元素转场（同页面内） → `geometryTransition`

Android 端通常用 `TransitionManager.beginDelayedTransition` + `ChangeBounds`，或 `MotionLayout` 的 ConstraintSet 切换。ArkTS 等价（V2 推荐）：

```typescript
@ComponentV2
struct HeroExpander {
  @Local expanded: boolean = false;

  build() {
    Stack() {
      if (!this.expanded) {
        Image($r('app.media.cover'))
          .geometryTransition('hero')   // ← 同 id 绑定 in/out
          .width(100)
          .height(100)
      } else {
        Image($r('app.media.cover'))
          .geometryTransition('hero')   // ← 同 id
          .width('100%')
          .height(300)
      }
    }
    .onClick(() => {
      animateTo({ duration: 350, curve: Curve.EaseInOut }, () => {
        this.expanded = !this.expanded;
      })
    })
  }
}
```

**关键**：
1. **必须配合 `if/else` 或 `Visibility` 切换**——同时挂着两个组件不会触发
2. **必须用 `animateTo` 包状态变更**——直接改 state 不会触发过渡
3. **同 id**——拼写错就静默无效果

---

## 3. 共享元素转场（跨 Router 页面） → `sharedTransition`

Android `ActivityOptions.makeSceneTransitionAnimation(this, Pair(view, "name"))` + `transitionName="name"`：

```kotlin
// Android
val options = ActivityOptions.makeSceneTransitionAnimation(
    this,
    Pair(coverImageView, "hero")
)
startActivity(intent, options.toBundle())
```

ArkTS：

```typescript
// 源页面
Image($r('app.media.cover'))
  .sharedTransition('hero', {
    duration: 350,
    curve: Curve.EaseInOut,
    type: SharedTransitionEffectType.Exchange
  })
  .onClick(() => router.pushUrl({ url: 'pages/DetailPage' }))

// 目标页面（同 id 即可自动 pair）
Image($r('app.media.cover'))
  .sharedTransition('hero', {
    duration: 350,
    type: SharedTransitionEffectType.Exchange
  })
```

### `SharedTransitionEffectType` 选型

| 类型 | 行为 | 对应 Android 场景 |
|---|---|---|
| `Exchange` | 源元素飞向目标位置，平滑形变 | `ChangeBounds` + 共享元素的标准走法 |
| `Static` | 源元素淡出，目标元素淡入（不形变） | 仅做"标记同元素"但不要动效 |

---

## 4. Navigation 子页面 → `customNavContentTransition`

如果用的是 `Navigation` + `NavDestination`（鸿蒙官方推荐的页面栈方案），转场要用 `customNavContentTransition()` 注册到 `NavPathStack`，**不能走 router 的 `sharedTransition`**——两套机制。

```typescript
this.pathStack.disableAnimation(false);
this.pathStack.setInterception({
  willShow: (from: NavDestinationContext, to: NavDestinationContext, op: NavigationOperation, isAnim: boolean) => {
    // 自定义转场动画
  }
});
```

**何时用 router、何时用 Navigation**：
- 已有项目用 router 历史长 → 继续 router + sharedTransition
- 新项目 / 鸿蒙原生写法 → 用 Navigation + customNavContentTransition

---

## 5. Activity 转场 / 页面进出 → `pageTransition()`

Android `overridePendingTransition(R.anim.slide_in_right, R.anim.slide_out_left)` 或主题 `windowAnimationStyle`。

### Router 模式

在被跳入的页面 `@Entry struct` 内：

```typescript
@Entry
@ComponentV2
struct DetailPage {
  build() {
    // ...
  }

  pageTransition() {
    PageTransitionEnter({ duration: 250, curve: Curve.EaseOut })
      .slide(SlideEffect.Right)
    PageTransitionExit({ duration: 250, curve: Curve.EaseIn })
      .slide(SlideEffect.Left)
  }
}
```

### `SlideEffect` 对照

| `SlideEffect` | 行为 | 对应 Android |
|---|---|---|
| `Right` | 从右滑入 / 向右滑出 | `slide_in_right` / `slide_out_right` |
| `Left` | 从左滑入 / 向左滑出 | |
| `Top` | 从上滑入 | |
| `Bottom` | 从下滑入 | |

### 复杂转场 — 用 `opacity / scale / translate / rotate` 组合

```typescript
pageTransition() {
  PageTransitionEnter({ duration: 300 })
    .opacity(0)
    .scale({ x: 0.8, y: 0.8 })
    .translate({ x: 100 })

  PageTransitionExit({ duration: 300 })
    .opacity(0)
    .scale({ x: 1.2, y: 1.2 })
}
```

---

## 6. MotionLayout → `geometryTransition` + `ConstraintSet` 思想

Android `MotionLayout` 是 `ConstraintLayout` 子类，靠 `MotionScene` XML 描述两个 `ConstraintSet` 之间的过渡。ArkTS 没有直接对标——拆成：

1. **状态切换**：用 `@Local`（V1 项目用 `@State`）+ `if/else` 表达两个 layout 状态
2. **平滑过渡**：用 `geometryTransition` 把两个状态下的同一组件连起来
3. **关键帧**：用 `keyframeAnimateTo` 表达 MotionScene 的 `<KeyFrameSet>`

```typescript
@ComponentV2
struct MotionDemo {
  @Local state: 'collapsed' | 'expanded' = 'collapsed';

  build() {
    Stack() {
      if (this.state === 'collapsed') {
        Image($r('app.media.cover'))
          .geometryTransition('hero')
          .width(100).height(100)
          .position({ x: 0, y: 0 })
      } else {
        Image($r('app.media.cover'))
          .geometryTransition('hero')
          .width('100%').height(300)
          .position({ x: 0, y: 0 })
      }
    }
    .onClick(() => {
      animateTo({ duration: 400, curve: Curve.EaseInOut }, () => {
        this.state = this.state === 'collapsed' ? 'expanded' : 'collapsed';
      })
    })
  }
}
```

复杂多关键帧（5+ 状态）用 keyframe：

```typescript
keyframeAnimateTo({ iterations: 1 }, [
  { duration: 200, event: () => { this.x = 50; } },
  { duration: 300, event: () => { this.x = 100; this.y = 100; } },
  { duration: 200, event: () => { this.scale = 1.2; } },
])
```

---

## 7. 常见坑

### 7.1 in/out 组件 id 不同 / 拼写错 → 静默无过渡，不报错

```typescript
// 错
if (this.show) {
  ImageA().geometryTransition('hero')
} else {
  ImageB().geometryTransition('Hero')   // ← H 大写，不匹配
}

// 对：完全相同的字符串
.geometryTransition('hero')   // 两边一致
```

### 7.2 直接改 state 而不包 animateTo → 共享元素也不生效

```typescript
// 错
this.expanded = true;

// 对
animateTo({ duration: 350 }, () => { this.expanded = true; })
```

### 7.3 跨页面 sharedTransition 但用了 Navigation

Navigation 不走 router 的 sharedTransition——必须改 `customNavContentTransition`。两套机制不互通。

### 7.4 `pageTransition` 写在错误的位置

`pageTransition()` 是 `@Entry struct` 的成员函数，**写在 `build()` 同级**，不是写在某个组件里。

```typescript
@Entry
@ComponentV2
struct DetailPage {
  build() { /* ... */ }

  pageTransition() {     // ← 这里，与 build 同级
    PageTransitionEnter({...}).slide(SlideEffect.Right)
    PageTransitionExit({...}).slide(SlideEffect.Left)
  }
}
```

### 7.5 `.transition()` 修饰符没生效

3 个常见原因：
1. 组件没在 `if/else` 控制下挂载/卸载——`.transition()` 只在 insert/delete 时生效
2. 状态变更没包 animateTo
3. 父容器 `clip(true)` 了，过渡的 translate/scale 出界被裁掉

### 7.6 共享元素位置闪一下

源页面尺寸和目标页面初始尺寸差太大时会闪。**对策**：
- 检查目标页面源元素的初始尺寸是不是 0（懒加载导致）→ 用占位
- 调长 `duration` 让眼睛跟得上
- `type: SharedTransitionEffectType.Exchange` 而不是 `Static`

### 7.7 性能问题：`transition` 列表里大量项目

每个 `if` 都自带 `.transition` 时，列表滚动会大量触发 insert/delete 计算。**列表场景慎用**——优先用属性动画（modify state）而不是结构动画（add/remove components）。

---

## 8. 决策速查

```
需要在 UI 状态切换时有过渡
  │
  ├─ 同页面内、同一个组件改尺寸/位置
  │   └─ geometryTransition + animateTo
  │
  ├─ 同页面内、组件出现/消失
  │   └─ .transition({...}) 修饰符 + if/else + animateTo
  │
  ├─ 跨页面（Router）、共享同元素
  │   └─ sharedTransition('id', {...})
  │
  ├─ 跨页面（Navigation）
  │   └─ customNavContentTransition（不能用 sharedTransition）
  │
  └─ 单纯整页进出动画（无共享元素）
      └─ pageTransition() 在 @Entry struct 内
```
