# @Param / @Local / @Event 命名规则（V2）

> 本文档为 ArkTS V2 装饰器（`@Param / @Local / @Event` 等）的变量命名约束，对应 V1 的 `@Prop / @State / @Link` 命名规则。**本项目锁 V2**，本文档为主参考。V1 历史规则查阅请见 [`prop-naming-rules.md`](./prop-naming-rules.md)。

---

## 适用范围（V2 装饰器）

以下 V2 状态装饰器的变量名都受本规则约束：

- `@Param` — 父→子单向传值
- `@Param @Once` — 父→子单向只读
- `@Local` — 组件内部状态
- `@Event` — 子→父事件回调
- `@Provider() / @Consumer()` — 跨层级共享
- `@Param` 持有 `@ObservedV2` 类实例（替代 V1 `@ObjectLink`）
- `AppStorageV2.connect / PersistenceV2.globalConnect` 返回值绑定到 `@Local`（**无 `LocalStorageV2`**；页面子树共享用 `@Provider`/`@Consumer`）

> `@BuilderParam / @Builder / @Computed` 不受此规则约束（不是状态变量）。

---

## 禁用名称列表

以下变量名与 `CustomComponent` 基类（V1/V2 共用基类）属性或框架方法冲突，**禁止**用作 `@Param / @Local / @Event` 的变量名：

```
size, position, value, width, height, type, enabled, opacity, visibility,
direction, offset, border, padding, margin, shadow, translate, scale, rotate,
zIndex, aspectRatio, flexBasis, flexGrow, flexShrink, alignSelf, layoutWeight,
clip, mask, id, key, hitTestBehavior, responseRegion, touchable,
monopolizeEvents, onClick
```

> 与 V1 完全一致：CustomComponent 基类是 V1/V2 共用基础。V2 仅是装饰器层升级，基类未变。

---

## V2 额外保留方法（CustomComponent 生命周期与基础 API）

V2 组件除上面属性外，还需避开以下 CustomComponent 基类方法名（这些是组件生命周期 / 基础能力的标识符）：

```
build, aboutToAppear, aboutToDisappear, onPageShow, onPageHide,
onBackPress, pageTransition, getUIContext, getHostContext, getInspectorChildren,
getInspectorChildren, getDialogController, queryNavDestinationInfo,
queryNavigationInfo, queryRouterPageInfo
```

> 这些是组件实例方法，与变量名同名会编译失败或运行时覆盖。

---

## 替代方案表格

| 禁用名称 | 推荐替代名称（V2） | 装饰器示例 |
|---------|-------------------|----------|
| size | buttonSize / thumbnailSize | `@Param @Once buttonSize: number = 48` |
| position | playPosition / scrollPosition | `@Local playPosition: number = 0` |
| value | sliderValue / inputValue | `@Param sliderValue: number = 0` |
| width | cardWidth | `@Param @Once cardWidth: number = 200` |
| height | headerHeight | `@Param @Once headerHeight: number = 56` |
| type | mediaType / filterType | `@Param @Once mediaType: string = 'audio'` |
| enabled | isPlayEnabled | `@Local isPlayEnabled: boolean = true` |
| opacity | contentOpacity | `@Local contentOpacity: number = 1.0` |
| offset | scrollOffset | `@Local scrollOffset: number = 0` |
| onClick | onPlayClick / onCardClick / onItemTap | `@Event onPlayClick: () => void = () => {}` |
| key | itemKey / sectionKey | `@Param @Once itemKey: string = ''` |
| id | itemId / userId / feedId | `@Param @Once feedId: string = ''` |
| direction | scrollDirection / flowDirection | `@Local scrollDirection: Axis = Axis.Vertical` |

---

## V1 → V2 命名规则对照（重要）

| V1 命名规则 | V2 等价 | 备注 |
|-----------|--------|------|
| `@Prop xxx: T` | `@Param @Once xxx: T = default` 或 `@Param xxx: T = default` | V2 必须有默认值 |
| `@State xxx: T` | `@Local xxx: T = default` | 同样禁用上面列表中的名称 |
| `@Link xxx: T` | `@Param xxx: T = default` + `@Event onXxxChange: (v: T) => void = () => {}` | V2 用事件命名约定 `on<Property>Change` |

**V2 `@Event` 命名约定**：

- 使用 `on<Action>` 或 `on<Property>Change` 前缀
- 示例：`onPlayClick / onItemSelect / onValueChange / onProgressChange / onSubmit / onCancel`
- **不要**直接用 `onClick`（与 CustomComponent 基类的 `.onClick()` 修饰符冲突）

---

## V2 特有命名建议

### `@ObservedV2` 类的 `@Trace` 属性

`@ObservedV2` 类的属性名也建议避开禁用列表（虽然类不是组件，理论上不冲突，但若类实例通过 `@Param` 传给组件，属性访问 `this.user.size` 仍可能产生混淆）：

```typescript
// 推荐
@ObservedV2
class TaskItem {
  id: string = ''
  @Trace title: string = ''     // 不要叫 @Trace value
  @Trace done: boolean = false
  @Trace itemPriority: number = 0   // 不要叫 @Trace priority（虽未列入禁用，但与 zIndex 等概念易混）
}

// 不推荐
@ObservedV2
class TaskItem {
  @Trace value: string = ''     // 易混淆
  @Trace size: number = 0       // 易混淆
}
```

### `AppStorageV2 / PersistenceV2` 的 key 命名

`AppStorageV2.connect(Cls, key, ...)` 的 `key` 字符串建议用常量 + 业务前缀，避免与基类属性同名：

```typescript
// 推荐
export class StorageKeys {
  static readonly USER_PROFILE = 'app_user_profile'
  static readonly PLAYBACK_STATE = 'app_playback_state'
}

@Local user: UserModel = AppStorageV2.connect(UserModel, StorageKeys.USER_PROFILE, () => new UserModel())!

// 不推荐 — 短名称易碰撞
AppStorageV2.connect(UserModel, 'user', () => new UserModel())  // 'user' 太通用
```

---

## 校验方法说明（V2）

生成 `@Param / @Local / @Event / @Provider() / @Consumer()` 变量时，对照禁用名称列表 + V2 额外保留方法逐一检查：

1. 若变量名与列表中任一名称完全匹配（区分大小写），必须改用推荐替代名称或加业务前缀。
2. 若业务含义与表格中的对应项一致，优先使用表格中已列出的替代名称。
3. 若业务含义不在表格中，通过加前缀方式区分，如 `item` + `Width` → `itemWidth`，`card` + `Height` → `cardHeight`。
4. **V2 额外**：`@Event` 不能命名为 `onClick`，应该用 `on<Action>` 或 `on<Property>Change`。
5. **V2 额外**：`@ObservedV2` 类的 `@Trace` 属性也建议避开禁用列表（虽不强制）。
6. 检查完成后，将变量名加入生成检查清单的对应条目进行标注。

---

## 完整 V2 示例

```typescript
@ObservedV2
class TaskModel {
  id: string = ''
  @Trace taskTitle: string = ''       // 不用 title
  @Trace taskDescription: string = '' // 不用 description（虽未列入禁用，业务命名更清晰）
  @Trace isComplete: boolean = false
  @Trace taskPriority: number = 0
}

@ComponentV2
struct TaskItemView {
  // V2 替代 V1 @Prop
  @Param @Once cardWidth: number = 320            // 不用 width
  @Param @Once headerHeight: number = 56          // 不用 height
  @Param task: TaskModel = new TaskModel()        // V2 直接 @Param 持有 @ObservedV2 实例

  // V2 替代 V1 @State
  @Local isExpanded: boolean = false              // 不用 enabled
  @Local contentOpacity: number = 1.0             // 不用 opacity

  // V2 替代 V1 @Link（双向同步）
  @Param isSelected: boolean = false
  @Event onSelectionChange: (v: boolean) => void = () => {}

  // V2 跨层级
  @Consumer() currentTheme: string = 'light'      // 不用 theme（虽未列入禁用，业务命名更清晰）

  build() {
    Column() {
      Text(this.task.taskTitle)
      Toggle({ type: ToggleType.Checkbox, isOn: this.isSelected })
        .onChange((v: boolean) => { this.onSelectionChange(v) })
    }
    .width(this.cardWidth)
    .opacity(this.contentOpacity)
  }
}
```

---

## 跨文档参考

- [`prop-naming-rules.md`](./prop-naming-rules.md) — V1 历史命名规则
- [`v2-common-components.md`](./v2-common-components.md) — V2 常用组件（含变量命名示例）
- `../SKILL.md` — V2 组件骨架与生成检查清单
- `arkts-state-manager/references/v2-decorators.md` — V2 装饰器完整语法参考
