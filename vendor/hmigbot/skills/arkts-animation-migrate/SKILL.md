---
name: arkts-animation-migrate
description: Android → HarmonyOS 动画框架迁移的系统化定位与还原（V2 优先，兼容 V1）。覆盖 8 大类动画：Lottie（@airbnb/lottie-android）、属性动画（ObjectAnimator/ValueAnimator/ViewPropertyAnimator）、补间动画（Tween/View Animation）、帧动画（AnimationDrawable）、SVGA、Transition Framework、共享元素转场（SharedElementTransition）、物理动画（DynamicAnimation/Spring）+ Activity/Fragment 转场。触发条件：用户描述"原版安卓是个动图，现在鸿蒙是静态图 / 这个 Lottie 用不了吗 / 选中态没有动画 / 卡片切换没有过渡 / 一镜到底 / 共享元素 / 转场没生效 / 帧动画 / 序列帧 / SVGA 礼物动画 / 安卓有 ObjectAnimator/animate().translation / 这个动画在鸿蒙怎么写"，或在 a2h-execute 还原 Android 页面时发现 XML 里出现 lottie_*/objectAnimator/<set>/<animation-list>/transitionSet/sharedElementEnterTransition 等属性，即使用户没明说"做动画"也要触发。内容：源框架识别决策树、按动画大类的 ArkTS 等价方案速查（详细模板在 references/）、@ohos/lottie 接入与 LottieView 复用范式、资源迁移路径（assets→rawfile）、调试与验证回环。不处理：纯 UI 静态样式（用 arkts-text-truncation/arkts-large-font/arkts-dark-mode 等专项 skill）、纯 router 跳转无视觉过渡（不算动画）、Web/H5 内嵌动画（非 ArkTS 域）。
metadata:
  type: domain
  domain: ui
  tags:
  - domain
  - ui
  - animation
  - migration
  - lottie
  - transition
  - sharedelement
---
# arkts-animation-migrate

> **ArkTS 动画 API 写法细节统一在 [arkts-animation-builder](../arkts-animation-builder/SKILL.md)。**
>
> 本 skill 专注于"Android 框架识别 + 标签映射 + 资源迁移 + 平台特有 API 接入说明 + 迁移陷阱"，**完整可运行的 ArkTS demo 组件请走 builder**（避免双源同步）。

## 1. 定位

ArkTS / HarmonyOS 迁移项目里，**动画几乎不会自然冒出来**——Android XML 里的 `lottie_fileName` / `<objectAnimator>` / `<animation-list>` / `app:layout_constraintXxx` 等动画属性，绝大多数迁移工具会丢掉或忽略，剩下的就是"静态图占位 + 动画消失"的样子。本 skill 是一套**识别 → 选型 → 还原 → 验证**的流水线。

**核心原则**：

1. **先确认能不能复用，再考虑降级**——用户第一反应往往是"鸿蒙没有这个吧"。事实是 Lottie / 属性动画 / 转场动画 / 共享元素 ArkTS 几乎都有原生或官方三方等价物，**不要急着降级到序列帧或拆图静态化**。
2. **资源是动画的一半**——JSON 模板 + 图集 + 序列帧 PNG 都要从 Android `assets/` / `res/raw/` / `res/drawable/` 完整搬到 HarmonyOS `entry/src/main/resources/rawfile/`。少一张 `img_X.png` 就是看不到 + 静默 fallback。
3. **坐标系不一致**——Android 的 dp/px、`marginStart` / `constraintXxx` 跟 ArkTS 的 vp、`position()` 不能直接 1:1，必须对照容器尺寸算 % 或绝对 vp，否则视觉上是"动画在播但歪了"。

---

## 2. 触发场景

### 用户语言信号

- 视觉对比类："**原版安卓是个动图，现在鸿蒙只有静态字 / 静图**" "动画没了" "选中态没动画" "卡片切换硬切" "硬跳没过渡"
- 直接询问类："**Lottie 用不了吗**" "鸿蒙怎么做共享元素" "这个动画在 ArkTS 怎么写" "ObjectAnimator 等价是啥"
- 资源信号："JSON 动画" "序列帧" "SVGA" "帧动画" "礼物动画" "一镜到底"
- 转场类："Activity 切换没动画" "页面进出特效" "返回时图片应该飞回原位"

### 代码信号（在读 Android 源码时）

任意一项命中即触发：

| 信号 | 出处 | Android 框架 |
|---|---|---|
| `app:lottie_fileName="..."` `app:lottie_imageAssetsFolder="..."` | XML 布局 | Lottie |
| `<set xmlns="...">` 含 `<alpha>/<scale>/<rotate>/<translate>` | `res/anim/*.xml` | 补间动画 |
| `<objectAnimator>` `<animator>` `<set ordering=...>` | `res/animator/*.xml` | 属性动画 |
| `<animation-list>` `<item drawable=... duration=...>` | `res/drawable/*.xml` | 帧动画 |
| `ObjectAnimator.ofFloat(...)` `view.animate().X(...)` | `.kt`/`.java` | 属性动画 |
| `TransitionManager.beginDelayedTransition(...)` `Scene.getSceneForLayout(...)` | `.kt`/`.java` | Transition Framework |
| `ActivityOptions.makeSceneTransitionAnimation(...)` `transitionName=` | `.kt`/`.java`/XML | 共享元素转场 |
| `SVGAImageView` `SVGAParser` `.svga` 文件 | `.kt`/资源 | SVGA |
| `SpringAnimation(...)` `FlingAnimation` `DynamicAnimation` | `.kt`/`.java` | 物理动画 |
| `overridePendingTransition(...)` `<style>...windowAnimationStyle</style>` | `.kt`/主题 | Activity 转场 |
| `ConstraintSet` `MotionScene` `<Transition>` | `res/xml/*.xml` | MotionLayout |

---

## 3. 识别决策树

```
迁移目标页面/组件存在视觉变化
    │
    ▼
是否有 .json 动画文件 + 配套图集？
    │
    ├─ 有 → ① Lottie (90% 走 @ohos/lottie)
    │         JSON 头部含 "v":"x.x.x", "fr":xx, "layers":[...] = bodymovin 导出特征
    │         → 详见 references/lottie.md
    │
    └─ 否
       │
       ▼
    是否有 .svga 文件？
       │
       ├─ 有 → ⑥ SVGA (鸿蒙无官方等价)
       │         首选：转 Lottie；兜底：拆帧
       │         → 详见 references/frame-and-svga.md §2
       │
       └─ 否
          │
          ▼
       res/anim/*.xml 含 <alpha>/<scale>/<rotate>/<translate>？
          │
          ├─ 有 → ② 补间动画 (.animation() + transform)
          │         → 详见 references/property-and-tween.md §1
          │
          └─ 否
             │
             ▼
          代码含 ObjectAnimator/ValueAnimator/.animate().X？
             │
             ├─ 有 → ③ 属性动画 (animateTo / .animation())
             │         → 详见 references/property-and-tween.md §2
             │
             └─ 否
                │
                ▼
             res/drawable/*.xml 含 <animation-list>？
                │
                ├─ 有 → ④ 帧动画 (ImageAnimator)
                │         → 详见 references/frame-and-svga.md §1
                │
                └─ 否
                   │
                   ▼
                代码含 TransitionManager / Scene？
                   │
                   ├─ 有 → ⑤ Transition Framework (.transition() 修饰符)
                   │         → 详见 references/transitions.md §1
                   │
                   └─ 否
                      │
                      ▼
                   含 makeSceneTransitionAnimation / transitionName？
                      │
                      ├─ 有 → ⑦ 共享元素转场 (geometryTransition / sharedTransition)
                      │         → 详见 references/transitions.md §2-§4
                      │
                      └─ 否
                         │
                         ▼
                      含 SpringAnimation / DynamicAnimation？
                         │
                         ├─ 有 → ⑧ 物理动画 (curves.springMotion)
                         │         → 详见 references/property-and-tween.md §3
                         │
                         └─ 否
                            │
                            ▼
                         含 overridePendingTransition / windowAnimationStyle？
                            │
                            └─ 有 → ⑨ Activity 转场 (pageTransition() / customNavContentTransition)
                                      → 详见 references/transitions.md §5
```

---

## 4. 速查表（按动画类型路由到 references/）

| # | Android 框架 | ArkTS 等价 | 详细模板 |
|---|---|---|---|
| ① | Lottie (`@airbnb/lottie-android`) | `@ohos/lottie` + 自建 `LottieView` 组件 | [references/lottie.md](./references/lottie.md) |
| ② | 补间动画 (`<set>/<alpha>/<scale>/<rotate>/<translate>`) | `.animation()` 修饰符 + `transform` | [references/property-and-tween.md](./references/property-and-tween.md) §1 |
| ③ | 属性动画 (`ObjectAnimator` / `ValueAnimator` / `ViewPropertyAnimator`) | `.animation()` 隐式 + `animateTo()` 显式 + `keyframeAnimateTo` | [references/property-and-tween.md](./references/property-and-tween.md) §2 |
| ④ | 帧动画 (`AnimationDrawable`) | `ImageAnimator` | [references/frame-and-svga.md](./references/frame-and-svga.md) §1 |
| ⑤ | Transition Framework (`TransitionManager`) | `.transition()` 修饰符 + `if/else` + `animateTo` | [references/transitions.md](./references/transitions.md) §1 |
| ⑥ | SVGA (`SVGAImageView`) | **无官方等价**——首选转 Lottie，兜底拆帧 | [references/frame-and-svga.md](./references/frame-and-svga.md) §2 |
| ⑦ | 共享元素转场 (`makeSceneTransitionAnimation`) | `geometryTransition`（同页）/ `sharedTransition`（Router）/ `customNavContentTransition`（Navigation） | [references/transitions.md](./references/transitions.md) §2-§4 |
| ⑧ | 物理动画 (`SpringAnimation` / `DynamicAnimation`) | `curves.springMotion()` / `curves.springCurve()` | [references/property-and-tween.md](./references/property-and-tween.md) §3 |
| ⑨ | Activity 转场 (`overridePendingTransition`) | `pageTransition()` / `customNavContentTransition()` | [references/transitions.md](./references/transitions.md) §5 |

**索引规则**：决策树定位到类型后，**直接打开对应 reference**——里面有完整代码模板、对照表、常见坑、调用示例。SKILL.md 不再重复这些细节。

---

## 5. 资源迁移总览

```
Android 项目                                        HarmonyOS 项目
─────────────────────────────────────             ─────────────────────────────
lib-xxx/src/main/assets/                           entry/src/main/resources/rawfile/
  ├── fit_part_1.json           (Lottie JSON) →     ├── fit_part_1.json
  ├── part_one_pre/             (Lottie 图集) →     ├── part_one_pre/
  │   ├── img_0.png                                 │   ├── img_0.png
  │   └── ...                                       │   └── ...
  └── gift.svga                 (SVGA)        →     └── (重导 Lottie 或拆帧)

res/drawable/loading_anim.xml   (帧动画)       →   ImageAnimator() 组件 + entry/src/main/resources/base/media/
res/anim/fade_in.xml            (Tween)        →   .animation() + opacity
res/animator/scale.xml          (属性动画)     →   .animation() + scale
res/transition/explode.xml      (Transition)   →   .transition() 修饰符
```

**资源命名规则**：HarmonyOS 设备文件系统大小写敏感。**复制后立刻 `ls` 一遍**确认大小写——macOS 的 `cp` 不会报警。

---

## 6. 工作流程（给 模型的执行顺序）

用户提出动画相关需求/问题后按顺序：

1. **识别源框架**（§3 决策树）——读 Android XML / Kotlin / 资源目录，定位是哪类
2. **打开对应 reference**（§4 速查表）——按 reference 文件里的模板和对照表执行
3. **检查鸿蒙工程现状**——已经有对应 ArkTS 代码？是补动画还是从零写？
4. **执行迁移**：
   - Lottie：先看 `oh-package.json5` 是否已装 `@ohos/lottie`，再看是否已有 `LottieView` 通用组件；多页 / 可滚动列表里的 Lottie 别全量 `autoPlay` 同播，要按可见性只播当前项（lottie.md §6.1）
   - 其他类型：按 reference 模板抄
5. **资源拷贝**——按 §5 路径表搬，**立刻 ls 验证大小写**
6. **编译 + 跑设备**——动画类问题**只看代码不算数**，必须真机或模拟器看一眼
7. **走 §7 验证回环**

---

## 7. 验证回环

修改后必须走完：

1. **编译过**：
   ```bash
   export PATH="/Applications/DevEco-Studio.app/Contents/tools/node/bin:$PATH"
   export DEVECO_SDK_HOME="/Applications/DevEco-Studio.app/Contents/sdk"
   hvigorw assembleHap --mode module -p product=default --no-daemon
   ```
2. **装到设备**：`hdc install -r entry/build/.../entry-default-signed.hap`
3. **进入对应页面眼看**：
   - Lottie：JSON 在播（不是静止帧） + 图集完整（缺图会显示空白方框） + 位置对（不偏不歪）
   - 属性动画：状态切换有过渡（不瞬间跳变） + 时长接近 Android（误差 ≤ 50ms 可接受）
   - 帧动画：连续播 + 循环正常
   - 转场：进入/退出都有 + 共享元素位置对齐
4. **横竖屏 / 折叠屏切换不崩**——动画组件 reuse 时常见 destroy 不彻底
5. **抓 hilog 看错误**：
   ```bash
   $HDC shell hilog -x | grep -E "lottie|animation|transition"
   ```
6. **小步提交**——按 a2h-commit 规范走（参见本工程 [`fc2a348`](#) 是这一类 commit 的范本）

---

## 8. 与其他 a2h-* skill 的关系

- **a2h-execute**：在还原 Android 页面时如果遇到动画属性/资源 → 触发本 skill 做动画那部分
- **a2h-commit**：动画类 commit 的 `Issue-Type` 通常是 `UI/UX`，`Skill` 字段填 `a2h-animation-migrate`
- **a2h-api-triage**：动画看不到时，**先排除是不是数据没来**（无数据 → 列表空 → 没渲染 → 看上去没动画）。这种情况走 a2h-api-triage，不是动画 skill 的问题
- **arkts-multi-device**：折叠屏展开/收起触发 reuse，Lottie 容易 destroy 异常 → 同时用两个 skill
- **arkts-large-font**：Lottie 字体层不受 fontSizeScale 影响（JSON 内嵌字号），但周围文本会变 → 二者无冲突，独立处理

---

## 9. 历史参考（本工程已落地的迁移案例）

| Commit | 范例类别 | 关键点 |
|---|---|---|
| [`fc2a348`](#) `接入 @ohos/lottie + 4 个 PrePage Lottie 还原` | ① Lottie 首次接入 | LottieView 组件诞生 + 4 套 fit_part_*.json + 图集迁移 |
| [`bd6ee25`](#) `PartFour SPORTS 步补齐机器人 Lottie` | ① Lottie 复用 | 复用 LottieView + 新增 gy_jqr_eye_up_down.json + jqr_eye/img_0..3.png |
| [`5d3ed1f`](#) `PartFive NICE Lottie 缺失资源` | ① Lottie 资源补漏 | gy_complete_data.json + imagesComplete*/ 图集补齐，典型"动画在播但部分空白"症状 |
| [`7e15191`](#) `PartFour Swiper 翻页动画` | 转场 | viewPager.setCurrentItem 平滑切换 → ArkTS Swiper |
| [`5c80f76`](#) `首页智能课表双层 Swiper 切换` | 转场 | 双层联动动画对齐 |

读这些 commit 的 diff 是最快理解本 skill 实战形态的方式。

---

## 10. 边界与不处理的事

**不处理**：
- 纯静态样式（颜色/字号/圆角对不齐）→ 用 arkts-text-truncation / arkts-large-font / arkts-dark-mode 等专项
- 纯 router 跳转无视觉过渡需求 → 那是路由问题，不是动画
- WebView / H5 内嵌动画 → 在 Web 域，本 skill 不覆盖
- Native 渲染层（XComponent + GLES）的自绘动画 → 高级场景，独立专项

**处理**：
- 任何"原版有动画现在没有 / 动画歪 / 动画卡"的视觉差异修复
- Lottie / SVGA / 帧动画 / 属性动画 / 转场 / 共享元素 / 物理动画 / 页面进出 的从零接入与还原
