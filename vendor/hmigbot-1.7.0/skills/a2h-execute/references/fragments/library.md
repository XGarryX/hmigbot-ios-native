# library — 三方库替代决策

## 五层查找（逐级下探，禁跳层直判"没有"）
1. **L1 ohpm 三方库**：ohpm.openharmony.cn／gitee openharmony-tpc／HarmonyOS-tpc，命中直接 `ohpm install`；
2. **L2 原生 @kit.\***：ImageKit／ArkData／MediaLibraryKit／CoreFileKit／NetworkKit + ArkUI 内置 Video/Image/Canvas/Web；
3. **L3 NAPI 桥接 C/C++**：FFmpeg／OpenCV／libjpeg-turbo（交叉编译 .so，成本高）；
4. **L4 WebView + JS 库**：Three.js／Fabric.js（性能有损）；
5. **L5 自研简化版／功能降级／标记 Skip**（最后手段）。

决策树：ohpm/tpc 有直接替代→L1｜@kit.* 能覆盖→L2｜有 C/C++ 开源核心→L3｜JS/Web 有等价库→L4｜否→L5。

## 3 个常见错误
1. 禁直接 import npm 包（如 axios）→ 用 `@kit.NetworkKit` 的 http，或 `ohpm install @ohos/axios`；
2. 禁假设同名鸿蒙版存在（`ohpm install glide` 不存在）→ 先查对照表再走决策树：Glide→`@ohos/imageknife`（L1）；
3. 闭源 SDK 禁直接标 Skip → 先查厂商适配状态（华为 C 类：联系厂商拿鸿蒙版），过渡方案 ArkWeb + JS-Bridge。

<!-- source: arkts-library-migration/SKILL.md:L17-72,L162-199 -->
