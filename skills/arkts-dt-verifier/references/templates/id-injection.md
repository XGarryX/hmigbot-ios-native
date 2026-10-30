# Testable ID 注入模板

可测试 ID 的命名规则、注入位置、每类组件的一个具体示例。完整规则见 `references/testable-id-catalog.md`。

**扫描范围**：`entry/src/main/ets/pages/` **+ `entry/src/main/ets/components/`** 双根（被 pages/ import 的子组件视为可达）。

---

## 命名规范（强制）

格式：`<page_short>_<purpose>_<kind>`

- `page_short`：页面短名 snake_case，从 spec 文件名业务部分生成（去编号、去 Activity/Fragment/Page 后缀）。例：
  - `page_0002_MainActivity.md` → `main`
  - `page_0010_SettingsActivity.md` → `settings`
  - `page_0018_WidgetConfigureActivity.md` → `widget_config`
- `purpose`：英文小词（`overflow` / `search` / `autoplay` / `save`）；多词用 `_` 连接
- `kind`：`btn` / `text` / `image` / `grid` / `list` / `swiper` / `toggle` / `input` / `row` / `dialog` / `fab` / `refresh` / `tab` / `root`

**规则**：
- 全小写 snake_case，长度 ≤ 32 字符
- 页面内**全局唯一**（含 @Builder 展开后也算）
- LazyForEach / ForEach 动态子项**不加**（外层容器加即可）
- 已有 id 合规 → 保留；不合规（随机串、camelCase、无 page_short 前缀）→ **重命名**
- 重复同形态（两个 search btn） → `_primary` / `_secondary` 后缀

---

## 注入位置

`.id('xxx')` 一律加在链式调用的**紧接第一行**（`.width()` 之前）。

```typescript
Image($r('sys.media.ohos_ic_public_more'))
  .id('main_overflow_btn')    // ← 加在这里
  .width(24)
  .height(24)
  .onClick(() => { ... })
```

---

## 每类一个示例

### A1. ActionBar 图标按钮（→ `btn`）

purpose 从资源名/accessibilityText/onClick 函数名提取：`more` → `overflow`；`search`、`back`、`save`、`delete`、`edit`、`settings`、`add`、`filter`、`sort`、`refresh`、`play`、`pause` 等各对应关键词。

```typescript
Image($r('sys.media.ohos_ic_public_more')).id('main_overflow_btn')
```

### A2. 顶部标题文本（→ `toolbar_title`）

```typescript
Text($r('app.string.app_name')).id('main_toolbar_title')
```

### A3. 顶层数据容器（→ `grid/list/swiper/refresh/tabs/waterflow`）

```typescript
Grid() { ... }.id('main_directory_grid')
```

### A4. 设置行 + 其中的开关（→ `row` / `toggle`）

`<setting_name>` 取 `$r('app.string.xxx')` 的 `xxx` key；没有就取主标题 snake_case。

```typescript
TextValueRow({ title: ... }).id('settings_autoplay_videos_row')
Toggle({ isOn: this.autoplayVideos }).id('settings_autoplay_videos_toggle')
```

### A5. FAB / 主操作按钮（→ `fab` / `btn`）

```typescript
Button('保存').id('edit_save_btn')
```

### A6. 输入框（→ `input`）

```typescript
Search({ value: this.query }).id('search_query_input')
```

### A7. Dialog 内的按钮（→ `<dialog>_confirm_btn` / `_cancel_btn` / `_dialog`）

```typescript
AlertDialog({ ... }).id('delete_confirm_dialog')
Button('确定').id('delete_confirm_dialog_confirm_btn')
```

### A8. 页面根容器（→ `root`）

页面 `build()` 里最外层 Navigation/Column/Stack。SMOKE landmark 首选。

```typescript
Navigation() { ... }.id('main_root')
```

### A9. bindMenu / bindContextMenu / bindSheet 触发器

触发器已被 A1 覆盖。**弹出菜单项本身不加 id**（API 不支持），靠 `ON.text(value)` 定位，value 来自 `string.json`。

---

## 不加 id（规则 C 摘要）

| 组件 | 原因 | 测试侧怎么定位 |
|------|------|----------------|
| LazyForEach/ForEach 动态子项 | id 重复冲突 | `findComponents(ON.type('GridItem'))[idx]` |
| bindMenu 弹出的 MenuElement | API 不支持 | `ON.text(string.json value)` |
| 装饰容器 / padding 包裹 / 纯视觉 Row | 无交互 | 不需要 |
| 仅显示性 Image/Text（标签、图标装饰） | 不被点 / 断言 | 不需要 |

---

## 灰色地带（规则 B — 标 `[NEEDS_REVIEW]`，不直接加）

- @Builder 内 ≥ 5 个同形态 Image（可能部分是装饰）
- 嵌套容器不清哪层是"真列表容器"
- 同页重复同名（需 `_primary` / `_secondary` 区分）

---

## 自检 grep（写完 manifest 前跑）

- `find entry/src/main/ets/pages entry/src/main/ets/components -name '*.ets' | xargs grep -c "\.id('"` 双根总数对齐 manifest
- 对每个 components/<Sub>.ets，反查 `grep -lE "from '.*components/<Sub>'" entry/src/main/ets/pages/*.ets`，结果写入 manifest "组件复用图"
- manifest 中**禁止**：空串 id、`undefined`/`null`/`NaN` 字样、同 id 出现 ≥ 2 次
- Settings 类页面：`<page>_<key>_toggle` 条数 ≥ 去重后 @Local 布尔行数（见 `testable-id-catalog.md §A4`）

任一违反 → `BLOCKERS: manifest contains invalid id` 或 `BLOCKERS: manifest gap — <PageName> id injection incomplete`，终止。
