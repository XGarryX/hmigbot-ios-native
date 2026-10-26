---
name: arkts-animation-builder
description: 生成 ArkTS/HarmonyOS 动画和交互效果代码（V2 优先，API 12+）。当用户需要实现 animateTo 显式动画、属性动画 animation()、transition 转场、geometryTransition 共享元素转场、Spring 弹簧动画、手势跟随、循环动画、淡入淡出/缩放/位移/旋转等 UI 动效时，务必触发此 skill。即使只说"加个动画""让它动起来"也应触发。从 Android 动画框架迁移（Lottie/ObjectAnimator/帧动画/SVGA 等）的识别与还原决策用 arkts-animation-migrate。
metadata:
  type: domain
  domain: ui
  tags:
  - ui
  - animation
  - arkts-v2
  - gesture
---
# ArkTS Animation Builder — 动画效果生成器（V2 优先）

> **从 Android 项目迁移动画 → see [arkts-animation-migrate](../arkts-animation-migrate/SKILL.md)**
> 含 Lottie / 属性 / 补间 / 帧 / SVGA / Transition / 共享元素 / MotionLayout 全套迁移视角与 Android→ArkTS 映射表。
> 本 skill 提供完整可运行的 ArkTS 动画 demo（被 migrate 内部 see also 引用）。

## API 版本与项目策略

本 skill 的代码模板基于 **API 12+（HarmonyOS 5.0.0+）和 ArkTS V2 装饰器体系**。

> **项目锁 V2**：本项目所有新生成的动画代码使用 V2 装饰器（`@ComponentV2 / @Local / @Param / @Event / @Once / @ObservedV2 / @Trace`）。**动画 API 本身（`animateTo / .animation() / .transition() / geometryTransition / TransitionEffect / curves.springMotion / Curve / PlayMode / PanGesture / TapGesture / LongPressGesture / PinchGesture / GestureGroup / DragEvent`）在 V1/V2 中完全相同**，本次升级只更换持有动画值的状态装饰器。
>
> 如需查阅 V1 兼容写法（老代码维护场景），参阅同名的 V1 历史文档：
> - `references/explicit-animation.md`（V1 legacy）↔ `references/v2-explicit-animation.md`（V2 主参考）
> - `references/transition-patterns.md`（V1 legacy）↔ `references/v2-transition-patterns.md`（V2 主参考）
> - `references/gesture-animation.md`（V1 legacy）↔ `references/v2-gesture-animation.md`（V2 主参考）
> - `references/media-app-animations.md`（V1 legacy）↔ `references/v2-media-app-animations.md`（V2 主参考）

V2 vs V1 关键差异（仅状态装饰器，动画 API 不变）：

| V1 装饰器 | V2 等价 | 备注 |
|---|---|---|
| `@Component` | `@ComponentV2` | struct 装饰器 |
| `@State scaleValue: number = 1` | `@Local scaleValue: number = 1` | 持有动画属性的内部状态 |
| `@Prop`（只读） | `@Param + @Once` | 父传子的只读动画参数 |
| `@Prop`（可改） | `@Param`（不带 `@Once`） | 子可改的本地副本 |
| `@Link`（双向） | `@Param + @Event onValueChange` 回调 | V2 单向数据流 + 事件 |
| `@Observed` | `@ObservedV2` | 被动画观察的类 |
| `@ObjectLink` | **取消** — 直接用 `@Param` 传 `@ObservedV2` 实例 | V2 简化对象引用 |
| `@StorageLink('isPlaying')` | `AppStorageV2.connect(PlaybackModel, 'playback', () => new PlaybackModel())!` | 配合 `@ObservedV2 + @Trace` 类 |
| `@Watch('method')` | `@Monitor('prop') method(m: IMonitor)` | 方法装饰器 |

不变（V1/V2 通用）：

| 类别 | API |
|---|---|
| 显式动画 | `animateTo({...}, () => { ... })` |
| 属性动画 | `.animation({...})` |
| 转场动画 | `.transition(TransitionEffect.OPACITY)` |
| 共享元素转场 | `.geometryTransition('id')` |
| 转场效果 | `TransitionEffect.OPACITY / SLIDE / move / scale / rotate / asymmetric / combine` |
| 曲线 | `Curve.Linear / EaseInOut / EaseIn / EaseOut / FastOutSlowIn / curves.springMotion / curves.interpolatingSpring / curves.cubicBezierCurve` |
| 播放模式 | `PlayMode.Normal / Reverse / Alternate` |
| 手势 | `PanGesture / TapGesture / LongPressGesture / PinchGesture / GestureGroup` |
| 拖拽 | `.draggable() / onDragStart / onDrop / onDragEnd`（**无 `onDragCancel`**，收尾用 `onDragEnd`） |
| 帧动画 | `this.getUIContext().keyframeAnimateTo(param, keyframes)`（API 11+；**是 UIContext 成员方法，无全局 `keyframeAnimateTo`**） |
| `@Builder / @Styles / @Extend / @Entry` | 不变 |

生成代码前，先确认目标 API 版本 ≥ 12。检查方法：读取 `build-profile.json5` 的 `compatibleSdkVersion` 字段。遇到版本兼容性或其他不确定的 ArkTS 知识点（如属性、语法、权限等），参阅 arkts-knowledge-verifier skill。

---

## 编译硬规矩（必读，否则编译不过）

动画 API 里有**一部分是真实模块导出**、必须显式 `import` 才能用；组件 attribute / decorator / 曲线枚举 才是 ambient（裸用）。混淆二者是本类代码最高频的编译失败源。

### 规矩 1：`curves` 与 `AppStorageV2` 是真实模块导出，必须 import（不是 ambient）

用到 `curves.springMotion / curves.interpolatingSpring / curves.cubicBezierCurve` 或 `AppStorageV2.connect(...)` 的**每个 `.ets` 文件**，文件顶部必须有：

```typescript
import { curves } from '@kit.ArkUI';        // 用到 curves.* 时
import { AppStorageV2 } from '@kit.ArkUI';  // 用到 AppStorageV2 时（可与 curves 合并成一行）
```

漏掉会直接编译失败：`Cannot find name 'curves'. Did you mean 'Curve'?` / `Cannot find name 'AppStorageV2'. Did you mean 'AppStorage'?`。
注意区分：`Curve.EaseInOut / Curve.Linear`（枚举）与 `PlayMode.*`、`TransitionEffect.*`、各 `*Gesture`、`animateTo` 本身、`DragEvent` **是 ambient，不用 import**；只有 `curves` 与 `AppStorageV2` 需要。

### 规矩 2：`keyframeAnimateTo` 是 UIContext 成员，无全局函数

分段关键帧动画必须经 `this.getUIContext().keyframeAnimateTo(param, keyframes)` 调用，**不存在**全局 `keyframeAnimateTo(...)`（裸调会 `Cannot find name 'keyframeAnimateTo'`）。签名：`keyframeAnimateTo(param: KeyframeAnimateParam, keyframes: Array<KeyframeState>)`；`param` 放 `delay / iterations / onFinish`，每个 `KeyframeState` 放 `{ duration, curve?, event }`（时长与目标闭包按段独立）。

```typescript
this.getUIContext().keyframeAnimateTo({ iterations: 1 }, [
  { duration: 800, curve: Curve.EaseOut, event: () => { this.dotScale = 1.5 } },
  { duration: 300, curve: Curve.EaseIn,  event: () => { this.dotScale = 1 } }
])
```

### 规矩 3：状态字段名不得撞组件内置 attribute 名

给 `@Local` 动画字段命名时**避开与组件通用属性同名**的词，否则报 `Property 'xxx' in type 'Index' is not assignable to the same property in base type 'CustomComponent'`。已知雷区：`scale`（内置 `.scale()`）、`rotate`、`translate`、`opacity`、`position`、`dragPreview`（内置 `.dragPreview()`）。缩放值用 `scaleValue / breathScale`，不用 `scale`；旋转用 `rotateAngle`；拖拽预览 `@Builder` 用 `previewBuilder` 之类，不用 `dragPreview`。

### 规矩 4：拖拽收尾事件是 `onDragEnd`，无 `onDragCancel`

系统拖拽框架的通用回调是 `.onDragStart` / `.onDrop` / `.onDragEnd(event: DragEvent)`。**不存在 `.onDragCancel`**（裸用报 `Property 'onDragCancel' does not exist on type '...Attribute'`）。需要在拖拽结束/取消时清理状态，用 `onDragEnd`。

---

## 动画类型选择

```
你需要什么动画？
│
├─ 状态驱动的属性变化（点击后变大/变色/移动）
│   └─ animateTo()（显式动画）— 最常用
│       控制哪些属性变化带动画；闭包内的 @Local / @Param / @Trace 字段变化触发动画
│
├─ 组件始终带动画（任何属性变化自动动画）
│   └─ .animation()（属性动画）
│       写在属性链末尾，之前的属性变化自动动画
│
├─ 组件出现/消失时的过渡
│   └─ .transition()（转场动画）
│       配合 if 条件渲染使用
│
├─ 两个页面/组件间的元素衔接
│   └─ geometryTransition（共享元素转场）
│       同一 id 的元素在不同位置间平滑过渡
│
├─ 手指拖动/滑动跟随
│   └─ 手势 + animateTo / translate
│       PanGesture + 实时更新 offset（@Local 持有）
│
├─ 长按触发辅助操作（点击/长按分工）
│   └─ LongPressGesture 单独使用
│       适用：点击做 A，长按做 B（如查看 vs 新增）
│
├─ 列表拖拽排序
│   ├─ 4-A PanGesture 方案 — 自由度高，可自定义旋转/倾斜动画
│   └─ 4-B DragEvent 框架 — 系统级支持，配合 LazyForEach 性能优
│
└─ 循环/永久动画（loading 旋转、呼吸灯）
    └─ animateTo + iterations: -1
        或组合多个 animateTo
```

---

## 动画实现模板（详见 references）

> **MUST**：写动画代码前，按类型先读对应 reference——

> - animateTo 显式动画 / transition 转场 → `references/v2-explicit-animation.md`
> - .animation() 属性动画 → `references/v2-transition-patterns.md`
> - 手势跟随动画（onActionUpdate / onActionEnd）/ 停止动画技巧 → `references/v2-gesture-animation.md`
> - geometryTransition 共享元素转场 / 循环动画 / @ObservedV2 动画状态封装 / 全局动画状态(AppStorageV2) → `references/v2-extra-animation.md`
> - 媒体类动画（播放器/进度） → `references/v2-media-app-animations.md`

---

## 性能注意事项

1. **避免在动画中频繁创建/销毁组件**：transition 动画比重建组件开销小
2. **优先使用 translate/scale/rotate/opacity**：这些属性不触发重新布局，GPU 直接处理
3. **避免动画中修改 width/height**：会触发重新布局，性能差
4. **LazyForEach / Repeat 中谨慎使用复杂动画**：可能导致帧率下降
5. **V2 数组 Proxy 性能**：V2 的 `@Local arr: T[]` 内置 Proxy，`push/splice` 直接触发刷新，避免 V1 时代"必须重新赋值"的样板代码

```typescript
// 不推荐 — 触发布局重计算
animateTo({ ... }, () => {
  this.cardWidth = 300   // width 变化触发布局
  this.cardHeight = 200  // height 变化触发布局
})

// 推荐 — 使用 scale 代替
animateTo({ ... }, () => {
  this.cardScale = 1.5   // scale 不触发布局，性能好
})
```

---

## 常见错误速记（V2）

| # | 错误 | 正确做法 |
|---|---|---|
| 1 | transition 没配合 animateTo | transition 属性变化必须包在 animateTo 中触发 |
| 2 | 循环动画 @Local 初值=目标值 | 初值与目标值不同，否则无动画 |
| 3 | 手势跟随用 animateTo | onActionUpdate 即时赋值；仅 onActionEnd 用 animateTo |
| 4 | V1/V2 装饰器混用 | 全用 V2 |
| 5 | 忘记给 @ObservedV2 属性加 @Trace | 需观察的属性加 @Trace |

> **MUST**：完整「错误 vs 正确」代码见对应 reference。

---

## 生成检查清单

- [ ] 选择了合适的动画类型
- [ ] struct 用 `@ComponentV2`，所有可观察类用 `@ObservedV2`
- [ ] 动画状态变量用 `@Local`（组件内）/ `@Param`（父传子）
- [ ] 类的可观察属性已加 `@Trace`
- [ ] animateTo 的状态修改在闭包内
- [ ] transition 配合 animateTo 触发
- [ ] 循环动画的初始值 ≠ 目标值
- [ ] 手势跟随不用 animateTo
- [ ] 优先使用 translate/scale/rotate/opacity
- [ ] geometryTransition 的 id 在两个位置一致
- [ ] DragEvent 方案使用 `.draggable()` 启用，`onDragStart` 返回预览 builder
- [ ] 全局动画状态用 `AppStorageV2.connect`，不再用 V1 `@StorageLink`
- [ ] 同文件不混用 V1/V2 装饰器

---

## 跨 Skill 协作

动画通常需要配合 UI 组件使用。如果用户需求涉及组件布局，读取 `arkts-component-builder/SKILL.md`。如果是完整业务功能（如带动画的列表详情页），读取 `arkts-pattern-library/SKILL.md`（它有编排协议引导完整流程）。状态管理细节读 `arkts-state-manager/SKILL.md`。完整路由矩阵见 `arkts-knowledge-verifier/references/skill-routing-guide.md`。

---

## References

### V2 主参考（推荐，本项目实际使用）

- `references/v2-explicit-animation.md` — animateTo 各种场景的完整 V2 示例
- `references/v2-transition-patterns.md` — 页面/组件转场动画完整 V2 模板
- `references/v2-gesture-animation.md` — 手势跟随动画完整 V2 实现（卡片滑动、下拉刷新、长按分工、列表拖拽含 PanGesture 与 DragEvent 对比）
- `references/v2-media-app-animations.md` — 媒体应用 V2 动画：下载进度环、播放按钮切换、MiniPlayer 显隐、半圆图表、`AppStorageV2 + @ObservedV2 PlaybackModel` 全局状态

### V1 历史参考（仅老项目兼容查阅）

- `references/explicit-animation.md` — V1 animateTo 示例（`@Component / @State`）
- `references/transition-patterns.md` — V1 转场动画示例
- `references/gesture-animation.md` — V1 手势 + 动画组合
- `references/media-app-animations.md` — V1 媒体动效（含 `@StorageLink('isPlaying')` 模式）

> 遇到版本兼容性或其他不确定的 ArkTS 知识点（如属性、语法、权限等），参阅 **arkts-knowledge-verifier** skill
