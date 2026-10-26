# animation-id — 源动画框架识别

## 识别决策树（按序，命中即定型）
1. `.json` 动画+图集（JSON 头含 `"v"/"fr"/"layers"` = bodymovin）→ **Lottie** → `@ohos/lottie` + LottieView；
2. `.svga` → **SVGA**（无官方等价）：首选转 Lottie，兜底拆帧；
3. `res/anim/*.xml` 含 `<alpha>/<scale>/<rotate>/<translate>` → **补间动画** → `.animation()` + transform；
4. `ObjectAnimator/ValueAnimator/.animate().X` → **属性动画** → `animateTo()`／`.animation()`／`keyframeAnimateTo`；
5. `res/drawable/*.xml` 含 `<animation-list>` → **帧动画** → `ImageAnimator`；
6. `TransitionManager/Scene` → **Transition Framework** → `.transition()` + `animateTo`；
7. `makeSceneTransitionAnimation/transitionName` → **共享元素转场** → `geometryTransition`(同页)／`sharedTransition`(Router)／`customNavContentTransition`(Navigation)；
8. `SpringAnimation/DynamicAnimation` → **物理动画** → `curves.springMotion()`；
9. `overridePendingTransition/windowAnimationStyle` → **Activity 转场** → `pageTransition()`／`customNavContentTransition()`。

## 铁律
- Lottie／属性／转场／共享元素在 ArkTS 均有等价物：先确认可复用再降级，禁急降级为序列帧/静态图。
- 资源整搬：`assets/`、`res/raw/` → `entry/src/main/resources/rawfile/`，少一张 img_X.png = 静默 fallback；复制后 `ls` 验证大小写（设备文件系统大小写敏感）。

## 编译硬规矩
1. `curves.*` 与 `AppStorageV2` 是真实模块导出：每个用到的 .ets 顶部 `import { curves, AppStorageV2 } from '@kit.ArkUI'`（漏了报 `Cannot find name 'curves'`）；`Curve.*`/`PlayMode.*`/`TransitionEffect.*`/各 `*Gesture`/`animateTo`/`DragEvent` 是 ambient，禁 import。
2. `keyframeAnimateTo` 只有 `this.getUIContext().keyframeAnimateTo(param, keyframes)`，无全局函数；param 放 delay/iterations/onFinish，KeyframeState = `{duration, curve?, event}`。
3. `@Local` 动画字段名禁 `scale/rotate/translate/opacity/position/dragPreview`（撞 CustomComponent 基类，报 not assignable to base type）→ `scaleValue`/`rotateAngle`/`previewBuilder`。
4. 拖拽收尾只有 `.onDragEnd(event: DragEvent)`，无 `.onDragCancel`；取消清理也走 onDragEnd。

<!-- source: arkts-animation-migrate/SKILL.md:L59-133; arkts-animation-builder/SKILL.md:L62-98 -->
