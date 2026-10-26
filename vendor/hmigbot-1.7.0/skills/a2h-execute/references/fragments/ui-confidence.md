# ui-confidence — UI 参照数据 confidence 分级与三源消费

## 每页三件套（spec/baseline/ui-snapshots/page_NNNN_XxxActivity/）
- `view.xml` — UIAutomator dump；无真机 dump 时为静态合成版（根节点 `<hierarchy synthesized="true">`、bounds 留空）
- `meta.json` — 页面语义（activity 映射 / navigation_targets / click_path / dynamic_menus 等）
- `screenshot.png` — 真机截图（可缺）

## confidence 三级行为契约（写码前先看本页级别：meta.json / ui-manifest）
| 级别 | 数据来源 | 允许的动作 |
|---|---|---|
| `high` | 真机 UIAutomator dump（view.xml 有真实 bounds） | 按 `bounds` 精确布局，允许硬编码尺寸/可见性 |
| `medium` | 源码 layout XML 静态合成（bounds 为空） | 只按层级结构布局；尺寸/visibility 用自适应或状态驱动，禁硬编码 bounds |
| `low` | 部分 layout 缺失/高度动态页 | 缺失处只写显式 TODO 占位（按占位分类法登记 deferred），禁臆测布局 |

## 编译外硬规矩（真机才现形）
1. medium 页把合成 view.xml 的空 bounds 当真值、或照 screenshot 目测像素硬编码 = 必错；尺寸一律 `'100%'`/`layoutWeight`/`constraintSize` 自适应。
2. low 页禁"这里应该有个列表"式脑补；占位走 deferred 申报，散文注释 = FAIL。
3. 级别由数据定，不得把 low 当 medium 用、也不得因截图清晰把 medium 当 high 用。

## 三源分工：结构以 view.xml 为准，样式以源码为准，语义以 meta.json 为准
| 信息 | 权威源 |
|---|---|
| 视图层级 / bounds / 运行时可见性 | view.xml（合成版无 bounds） |
| 颜色/字体/样式/主题继承/drawable/资源名 | 源码 layout + styles.xml + themes.xml（view.xml 一概没有） |
| 导航目标 / 点击路径 / Activity-Fragment 映射 | meta.json |
| 文本内容 | 三者皆有：view.xml=运行时值，源码=默认值/resource ref |

## 五步消费顺序（逐页固定，不跳步）
1. meta.json → 这页是什么、能做什么；2. view.xml → 建精确层级树；3. 源码 layout + styles/themes → 补样式、颜色、资源引用；4. 交叉验证：层级冲突以 view.xml 为准，源码只补样式；5. screenshot.png（如有）→ 最终视觉校验。

<!-- source: a2h-spec/SKILL.md:L217-243 + a2h-spec/references/three-source-and-scale.md:L6-31 -->
