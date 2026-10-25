# @Prop / @State / @Link 命名规则（**V1 历史文档 — Legacy**）

> ⚠️ **本项目锁 ArkTS V2**。本文档为 **V1 历史参考**（`@Prop / @State / @Link` 命名约束），仅用于阅读老代码或迁移老项目时查阅。
>
> **新代码请使用 V2 命名规则**：参阅 [`v2-prop-naming-rules.md`](./v2-prop-naming-rules.md)（V2 主参考，对应 `@Param / @Local / @Event`）。

## 禁用名称列表

以下变量名与 CustomComponent 基类属性冲突，**禁止**用作 @Prop / @State / @Link 的变量名：

```
size, position, value, width, height, type, enabled, opacity, visibility,
direction, offset, border, padding, margin, shadow, translate, scale, rotate,
zIndex, aspectRatio, flexBasis, flexGrow, flexShrink, alignSelf, layoutWeight,
clip, mask, id, key, hitTestBehavior, responseRegion, touchable,
monopolizeEvents, onClick
```

## 替代方案表格

| 禁用名称 | 推荐替代名称 |
|---------|------------|
| size | buttonSize / thumbnailSize |
| position | playPosition / scrollPosition |
| value | sliderValue / inputValue |
| width | cardWidth |
| height | headerHeight |
| type | mediaType / filterType |
| enabled | isPlayEnabled |
| opacity | contentOpacity |
| offset | scrollOffset |

## 校验方法说明

生成 @Prop / @State / @Link 变量时，对照禁用名称列表逐一检查：

1. 若变量名与列表中任一名称完全匹配（区分大小写），必须改用推荐替代名称或加业务前缀。
2. 若业务含义与表格中的对应项一致，优先使用表格中已列出的替代名称。
3. 若业务含义不在表格中，通过加前缀方式区分，如 `item` + `Width` → `itemWidth`，`card` + `Height` → `cardHeight`。
4. 检查完成后，将变量名加入生成检查清单的对应条目进行标注。
