# 可测试 ID 目录

UI 测试 selector 的字面量来源问题（图标按钮没有文本、bindMenu 触发器是 Image、文案多语言）的根治方案：**让源码主动暴露稳定的 `.id('...')` 锚点**。

本文件定义：哪些组件**必加 id**、哪些**不加**、id 怎么命名、命中后测试侧怎么用。

`step2b-id-injector` agent 严格按本目录扫描并注入 id。`step3-ui-test-agent` 严格按本目录生成 `ON.id(...)` selector。

**扫描范围**：`entry/src/main/ets/pages/` **+ `entry/src/main/ets/components/`** 双根（被 pages/ import 的子组件视为可达）。仅扫 pages/ 会遗漏 BrowserToolbar / SettingScreen / 各种 Dialog 等抽出子组件，导致 spec UI 行为被错标为 IMPL_MISSING。

---

## 一、命名规范（强制）

格式：`<page_short>_<purpose>_<kind>`

- `page_short`：页面短名小写。**生成规则**：
  - 取 spec 文件名 `page_NNNN_<XxxActivity|XxxFragment|XxxPage>.md` 中的业务名（去掉前缀编号、去掉 `Activity`/`Fragment`/`Page` 后缀），**转 snake_case**
  - 例：`page_0002_MainActivity.md` → `main`；`page_0010_SettingsActivity.md` → `settings`；`page_0018_WidgetConfigureActivity.md` → `widget_config`
  - 多词驼峰拆分用 `_`（`ViewPager` → `view_pager`，`PanoramaPhoto` → `panorama_photo`）
  - 同业务名碰撞时（`Photo` vs `PhotoVideo`）保留区分词，不要简化到只剩 `photo`
  - **agent 必须为本项目生成完整映射表写入 manifest 头部**，而不是依赖固定预设
- `purpose`：英文小词，描述用途（`overflow` / `search` / `camera` / `autoplay` / `query` / `save`）。多词用 `_` 连接（`auto_play`）。
- `kind`：组件种类后缀 —— `btn` / `text` / `image` / `grid` / `list` / `swiper` / `toggle` / `input` / `row` / `dialog` / `fab` / `refresh` / `tab` / `root`。

**规则**：
- 全小写 `snake_case`，长度 ≤ 32 字符
- 一个页面内必须**全局唯一**（含 @Builder 内的也算）
- LazyForEach 内动态生成的子项**不加** id（同 id 会冲突）；外层容器加（如 Grid 加 `main_directory_grid`，每个 GridItem 不加）
- 已有 `.id(...)` 的组件**不重复加**，但若现有 id 不符合命名规范（如随机字符串、camelCase），**重命名为合规 id**

**抽出子组件 id 归属**（`entry/src/main/ets/components/**`）：

子组件被 pages/ import 后，id 命名两条路径：

- **被 1 个页面用** → 直接用该页 `page_short` 作前缀（例：BrowserToolbar 仅被 BrowserPage 用 → `browser_toolbar_settings_btn`）
- **被 ≥ 2 个页面用，命名差异大** → 推荐改造子组件接收 `idPrefix: string` prop，父页传 `'settings'` / `'data_list'` 等；子组件内 `.id(this.idPrefix + '_xxx_yyy')`；manifest 同 id 列出多组（每页一行，行内备注"复用自 components/SettingItemRow"）
- **被 ≥ 2 个页面用，但不想改源码** → 兜底用 `<component_short>` 自前缀：`<component_short>_<purpose>_<kind>`（component_short 例：SettingItemRow → `setting_item_row`，过长可缩成 `sir`）；manifest 单行记录，"归属"列填 `ALL_PAGES_REUSED`

跨页面复用时 manifest "归属页"列必须填全部引用页（grep 反查 import）。

---

## 二、必加 id 的组件清单（规则 A）

凡是符合下列任一形态的组件，agent 必须注入 id：

### A1. 顶部 ActionBar / Toolbar 的图标按钮

凡是 `Image($r(...))` / `Button(...)` + `.onClick(...)` 出现在页面顶部 Row/Builder 里的：

**purpose 推导规则**（从图标资源名/accessibilityText/onClick 函数名提取语义关键词）：

- 资源名包含 `more` / `overflow` / 三点 / 四点 → `overflow`
- 资源名包含 `search` → `search`
- 资源名包含 `camera` → `camera`
- 资源名包含 `back` / 左箭头 → `back`
- 资源名包含 `cancel` / `close` / `X` → `cancel` 或 `close`
- 资源名包含 `save` / `done` / `check` → `save`
- 资源名包含 `share` → `share`
- 资源名包含 `delete` / `trash` → `delete`
- 资源名包含 `edit` / `pen` → `edit`
- 资源名包含 `settings` / `gear` → `settings`
- 资源名包含 `add` / `plus` → `add`
- 资源名包含 `filter` → `filter`
- 资源名包含 `sort` → `sort`
- 资源名包含 `refresh` → `refresh`
- 资源名包含 `play` → `play`
- 资源名包含 `pause` → `pause`
- 资源名匹配不到模式 → 用 accessibilityText 翻译为 snake_case；都没有就用图标资源名末段（`ohos_ic_public_xxx` → `xxx`）

kind 统一用 `btn`。例：`main_overflow_btn` / `edit_save_btn` / `view_pager_back_btn`。

### A2. 顶部标题文本

页面顶部最大的 Text（标题/title），加 `<page>_toolbar_title`。SMOKE 测试用它当 landmark 比 Grid/Column 稳。

### A3. 顶层数据容器

| ArkUI 组件 | kind |
|-----------|------|
| `Grid()` | `grid` |
| `List()` | `list` |
| `Swiper()` | `swiper` |
| `Refresh()` | `refresh` |
| `Tabs()` | `tabs` |
| `WaterFlow()` | `waterflow` |

每个页面通常只有一两个，purpose 描述其内容（`directory` / `media` / `photo` / `setting`）。例：`main_directory_grid`、`media_thumbnail_grid`、`settings_list`、`view_pager_swiper`、`photo_image_swiper`。

### A4. 设置项 / 行项

每个设置行（自定义 `TextValueRow` / `OneLinerRow` / `SettingItem` / 任何"标签 + 控件"的 Row），加 `<page>_<setting_name>_row`，其内的 Toggle/Switch/Checkbox 加 `<page>_<setting_name>_toggle`。

`<setting_name>` 优先取该行使用的字符串资源 key（`$r('app.string.xxx')` → `xxx`）；没有资源引用就取行内主标题文本的 snake_case。

例：
- 行：`settings_autoplay_videos_row`
- 开关：`settings_autoplay_videos_toggle`

**下限自检（强制）**：Settings 类页面（spec 含 `## 状态接口` `@Local` 布尔表 或 `## 设置项` 列表），manifest 本页条目必须满足：

**计数口径**（与 Step 3 §E1 严格一致，避免两边不同口径导致死锁）：
- `@Local 布尔行数` = `## 状态接口` 表中**装饰器列=`@Local`（V1 老项目 spec 为 `@State`）且 type 列=`boolean`** 的行数；排除 `@Param` / `@Provider` / `@Consumer`（及 V1 `@Prop` / `@Link` / `@Provide` / `@Consume`）/ `string` / 对象 / 数组
- 若同一 `key` 同时出现在 `## 状态接口` 布尔表和 `## 设置项` 表 → **去重**，只计一次（按 `## 状态接口` 的 key 为准）

硬性约束：
- `<page>_<key>_toggle` 行数 ≥ 去重后的 `@Local` 布尔行数
- `<page>_<key>_row` 行数 ≥ 去重后的 `@Local` 布尔行数 + TextValueRow/OneLinerRow 行数
- manifest 不得出现空串 id、含 `undefined` / `null` 字样的 id、同 id 被多个组件共用

不足或违反任一项 → Step 2b agent 返回 `BLOCKERS: manifest gap — <PageName> id injection incomplete (expected N, got M)` 或 `BLOCKERS: manifest contains invalid id`，主线程补实装（每个 @Builder 调用必须传 `settingKey`，见 step2b agent §4.4）后重跑 Step 2b。Step 3 在下限自检通过前**不得启动**，否则会退回"合并枚举"兜底（违反反模式 11）。

**不可达页例外**：若 spec 明确标注该页需要外部 Intent 启动（Step 3 beforeAll 会 `throw (unreachable)`）→ 本下限自检跳过，manifest 用 `<PageName>: UNREACHABLE_SKIP` 标注。

### A5. FAB / 主操作按钮

底部悬浮按钮、底部主按钮（保存、确定、应用），加 `<page>_<action>_fab` 或 `<page>_<action>_btn`。

### A6. 输入框

`TextInput` / `Search` / `TextArea`，加 `<page>_<purpose>_input`。例：`search_query_input`。

### A7. Dialog 内的确认/取消

`AlertDialog` / 自定义 Dialog，按钮加 `<dialog_name>_confirm_btn` / `<dialog_name>_cancel_btn`。Dialog 根容器加 `<dialog_name>_dialog`。

### A8. 页面根容器

页面 build() 里最外层的 `Navigation` / `Column` / `Stack`，加 `<page>_root`。SMOKE landmark 备选。

### A9. bindMenu / bindContextMenu / bindSheet 触发器

触发器组件（图标或按钮）加 id（已被 A1 覆盖即可）。**菜单弹出层本身的菜单项不加** id（API 不支持，靠 `ON.text(value)` 定位，value 来自 `string.json`）。

---

## 三、不加 id 的组件（规则 C）

| 组件 | 不加原因 | 测试侧定位策略 |
|------|---------|---------------|
| LazyForEach / ForEach 内动态生成的子项 | 重复 id 冲突 | `findComponents(ON.type('GridItem'))[index]` |
| `bindMenu` 弹出的 `MenuElement` | API 不支持 | `ON.text(string.json 的 value)` |
| 装饰性容器（阴影 Column、padding 包裹、空白 Stack） | 无交互 | 不需要 |
| @Builder 私有内部布局（仅做对齐用的 Row/Stack） | 视觉，无语义 | 不需要 |
| 仅显示性的 Image/Text（标签、说明、图标装饰） | 不被点也不被断言 | 不需要 |

---

## 四、待人工裁决的灰色地带（规则 B，agent 标记后请人工 review）

下列情况 agent **不要直接加**，只在 manifest 标 `[NEEDS_REVIEW]`：

- 一个 @Builder 内有 ≥ 5 个 Image 都符合 A1 形态 → 可能不全是工具栏按钮，部分是装饰
- LazyForEach 外层但容器嵌套不明（Stack 套 Stack 套 Grid） → 哪个是真"列表容器"
- 同名重复（一个页面里 spec 写了两个 search button） → 用 `_primary` / `_secondary` 后缀

---

## 五、测试侧使用规范（step3 必读）

selector 优先级（高 → 低）：

1. `ON.id('xxx_xxx_xxx')` —— 本目录定义的 id（**默认**）
2. `ON.text('value')` —— 当目标是 LazyForEach 内动态项 / bindMenu 菜单项时；value 必须来自 `string.json` 的 value 字段（不许翻译、不许猜）
3. `ON.type('Toggle' / 'Swiper' / ...)` —— 不需要区分多个同类时的 SMOKE landmark
4. **禁用** `ON.text` 配合凭空翻译的中英文字面量

测试代码示范：
```typescript
// A1 图标按钮
const overflow = await driver.findComponent(ON.id('main_overflow_btn'))
if (!overflow) throw new Error('main_overflow_btn missing')
await overflow.click()
await driver.delayMs(300)

// 菜单项（bindMenu 弹出，文本来自 string.json:settings = "Settings"）
const settings = await driver.findComponent(ON.text('Settings'))
if (!settings) throw new Error('Settings menu item missing')
await settings.click()

// SMOKE landmark：到达 SettingsPage
await driver.assertComponentExist(ON.id('settings_root'))
```

---

## 六、Manifest 文件（agent 产出 / 测试侧消费）

`step2b-id-injector` agent 写入：`entry/src/main/ets/test/testable-id-manifest.md`

格式：

```markdown
# Testable ID Manifest
> Generated by step2b-id-injector. Do not edit by hand.
> Generated at: <ISO 8601>
> Pages scanned: N | IDs injected: M | IDs renamed: K | Needs review: P

## Page → page_short 映射（本项目）

| Spec 文件 | 源文件 | page_short |
|----------|-------|-----------|
| page_NNNN_XxxActivity.md | entry/src/main/ets/pages/XxxPage.ets | xxx |
| ... | ... | ... |

## P{编号} {PageName} (entry/src/main/ets/pages/XxxPage.ets)

| ID | 行号 | 组件 | 规则 |
|----|------|------|------|
| <page>_root | <line> | Navigation/Column/Stack | A8 |
| <page>_toolbar_title | <line> | Text(title) | A2 |
| <page>_<purpose>_btn | <line> | Image($r(...)) + onClick | A1 |
| <page>_<purpose>_grid/list/swiper | <line> | Grid()/List()/Swiper() | A3 |
| <page>_<setting>_toggle | <line> | Toggle() | A4 |
| <page>_<purpose>_input | <line> | TextInput()/Search() | A6 |
| ... | | | |

## 字符串映射（菜单项 / 对话框文案 / 按钮 label）

> 来源：`entry/src/main/resources/<locale>/element/string.json`
> 当 `<locale>` 不存在该 key 时 fallback 到 base。

| string key | base value | zh_CN value | en_US value | 测试设备实际渲染 |
|-----------|-----------|------------|------------|----------------|
| <key> | "..." | "..." 或 (fallback) | "..." 或 (fallback) | "..." |
| ... | | | | |

## NEEDS_REVIEW 条目（人工裁决）

> 灰色地带：agent 不直接注入，列出建议供人工确认。

| 文件 | 行号 | 组件描述 | 建议 ID | 不直接加的原因 |
|------|------|---------|--------|--------------|
| ... | | | | |
```

step3 agent 必须先读这个 manifest：
- selector 用"ID 表"的 `ID` 列
- `ON.text(...)` 字面量用"字符串映射"的"测试设备实际渲染"列
