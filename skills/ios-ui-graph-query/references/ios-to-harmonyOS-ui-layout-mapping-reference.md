# iOS → HarmonyOS UI layout mapping

Read the selected target/Release source through Source and retain its source anchors. This table gives candidates, not automatic equivalence. See the graph builder schema for normalized fields; neither graph slots nor static outline bounds are native runtime properties.

| Native source | Target candidate | Evidence to preserve |
|---|---|---|
| SwiftUI VStack / HStack; UIStackView axis | Column / Row | Spacing, alignment, distribution, intrinsic sizing, priorities; do not invent equal weights |
| SwiftUI ZStack / overlay / background; layered UIView hierarchy | Stack | Draw order, clipping, actual layout size and hit testing independently |
| SwiftUI Grid / LazyVGrid / LazyHGrid; UICollectionView layout | Grid / WaterFlow / composed layout | Column definitions, item identity, pagination, reuse and scrolling; not a blind class rename |
| SwiftUI List / ScrollView / LazyVStack; UITableView / UIScrollView | List / Scroll | Stable IDs, sections, refresh, selection, load/error/empty states, viewport sizing |
| SwiftUI TabView; UITabBarController | Tabs or composed tab shell | Selected binding, per-tab navigation stack, restoration and whether the tab bar survives pushed pages |
| NavigationStack / NavigationLink; UINavigationController | Navigation / NavPathStack / NavDestination | Parameters, pop/results, path mutation, re-entry and deep links; use arkts-navigation-builder |
| sheet / fullScreenCover; present / UIPresentationController | bindSheet / bindContentCover / dialog candidate | Dismissal, cancellation, parent ownership, detents and lifecycle; keep distinct from pushed pages |
| NSLayoutConstraint / anchors; SwiftUI custom Layout / alignmentGuide | RelativeContainer or composed/custom layout | Actual equations, priorities, coordinate spaces and measurement behavior; there is no general one-to-one conversion |

## Layout and appearance

SwiftUI modifier order affects the result. Preserve frame constraints, padding, background/overlay ordering, clipping, alignment, layoutPriority and fixedSize in source evidence. UIKit intrinsic size and content hugging/compression resistance are not generic layout weights. Points and image pixels are different; use explicit source dimensions or actual asset scale metadata, never an assumed global divisor.

Source safeAreaInsets / safeAreaLayoutGuide / ignoresSafeArea / safeAreaInset describe different edges and owners. Apply the target four-layer contract in [arkts-immersive-safearea](../../arkts-immersive-safearea/SKILL.md). Do not duplicate window setup on each page. Preserve source trait/color variants, dynamic type and RTL behavior.

## Target rules retained

- Stack positioning and content alignment are different. Use the target layout reference for relative positioning; a child align modifier alone is not proof of the expected sibling geometry.
- Geometry and touch interception are independent. Follow P-17 in ui-migration-pitfalls.md; an interactive subtree must not be disabled by an unconditional blocking ancestor.
- A percentage child under an unconstrained parent is not proof it matches the parent's content size. Retain the original checks for unbounded scrolling and percentage backgrounds.
- Use source-defined size/ratio for Image. Dynamic/unknown geometry remains an explicit implementation question.
- Original ArkTS component/state/navigation/build rules stay in their domain skills. Validate the actual target SDK API before using it.
