# ID 注入设计文件格式（ID Inject Design）

第一步「测试用例设计」**与测试设计文件并行产出**的 ID 注入设计，**每页一份**，写到 `spec/test/ui-test/id-inject/P{编号}_{PageName}.md`。

> 与 `spec/test/ui-test/design/P{编号}_{PageName}.md`（测试设计 §A/§B/§C/§D/§F）**一一对应**；§E 在原模板里曾合并写在设计文件，现在独立成本文件，下游第二步只读这一份。

## 谁读谁写

- **写**：第一步 `step1-design-agent`（与测试设计同批产出，同一 agent 同一实例顺手写两份）
- **读**：第二步 `step2-id-inject-agent`（**唯一驱动输入**）
- 第三步 `step3-generate-agent` **不读本文件**，只读 manifest 取已注入的 id

## 输出格式（严格按顺序）

```markdown
# P{编号} ID 注入设计：{PageName}

> 配套测试设计：spec/test/ui-test/design/P{编号}_{PageName}.md
> 相关源码：entry/src/main/ets/pages/{PageName}.ets, components/{Sub}.ets …
> page_short：{main / settings / widget_config / …}   ← `<page_short>` 命名规则见 test-case-template.md §4
> Mount Strategy：NAVIGATION_DIRECT_MOUNT | ROUTER_LOAD_CONTENT

## 1. ID 注入表

| 目标 ID | 注入位置（文件:行号） | 规则 | 用例引用 | 备注 |
|---------|-------------------|------|---------|------|
| main_root | pages/MainPage.ets:42 (Navigation 最外层) | A8 | P0002_UI_SMOKE_page_renders | 必有 |
| main_directory_grid | pages/MainPage.ets:58 (Grid()) | A3 | P0002_UI_COMP_directory_grid_exists | |
| main_empty_placeholder | pages/MainPage.ets:71 (空态 Text) | A2 变体 | F005_UI_AC02_empty_shows_placeholder | |
| browser_toolbar_settings_btn | components/BrowserToolbar.ets:23 (Image(settings)) | A1 + 跨页面策略 | P0002_UI_NAV_to_SettingPage | 见 §2 |

- **规则列**填 A1-A9（见 `test-case-template.md §4`）
- **行号**用 grep 实测得出，禁瞎填
- **用例引用**写第二步生成测试时哪些 it 会用到本 id（来自 design §C 用例 ID）
- **备注**用于标"必有 landmark / 跨页面 / 同名重复 _primary/_secondary / 灰色地带" 等

## 2. 跨页面复用子组件命名策略

| Component | 引用的 page 列表（grep import 反查） | 命名策略 | 落地形式 |
|-----------|--------------------------------|----------|---------|
| BrowserToolbar | MainPage, MediaPage, AlbumPage | **主用户前缀** = 'main' | 加 `@Prop idPrefix: string = ''`，父页 MainPage 传 `idPrefix: 'main'`，其他页传具体前缀 |
| EmptyPlaceholder | MainPage, SearchPage | **idPrefix prop** | 父页各自传 `idPrefix: 'main' / 'search'` |
| SettingSection | SettingPage | **page_short 自前缀** | 仅 1 页引用，无需 idPrefix，直接用 `settings_*` 命名 |

> 三种策略选一，必须明确「主用户」（首要业务父页）+ 「其他引用页是否也加 idPrefix」。漏一页 → 那一页的 component 内 id 为空字符串。

## 3. NEEDS_REVIEW 灰色地带

第一步无法决断、需要用户确认后才决定怎么注入的条目（**第二步不会注入这些**，只在源码加 `// NEEDS_REVIEW: ...` 注释、并在 manifest 登记）。

| 建议 ID | 位置 | 类型/形态 | 原因 | 待用户确认动作 |
|---------|------|----------|------|--------------|
| ?_overflow_item_btn_{1..N} | components/OverflowMenu.ets @Builder 内 ≥5 个 Image | A1 同形态批量 | 不确定哪个是哪个语义 | 用户给每个 Image 标语义 → 派单页 step2 重跑 |
| settings_section_{a/b}_row | pages/SettingPage.ets 嵌套 Column | 容器层级模糊 | 哪一层是真"设置行" | 用户确认行组件归属 |

## 4. 未注入清单（实装缺失 / UNREACHABLE）

源码里**根本没有这个组件** / 整页 unreachable 的 id（第二步 **不注入、不创造源码**，留给第三步用 `_IMPL_MISSING` 模式断言不存在让 RED 暴露 gap）。

| 目标 ID | 用例引用 | 原因 |
|---------|---------|------|
| main_directory_grid | P0002_UI_COMP_directory_grid_exists | 源码 MainPage 当前只有空 Column，无 Grid 容器 |
| settings_autoplay_toggle | settings_autoplay_toggle_flips_state | 源码 SettingPage 未加 Toggle 组件 |
| widget_config_root | P0099_UI_SMOKE_page_renders | 整页 unreachable（FormExtension，测试 context 不可达） |

## 5. page_short → PageName 映射

| page_short | 对应文件 | 说明 |
|-----------|---------|------|
| main | pages/MainPage.ets | 主页 |
| settings | pages/SettingPage.ets | 设置 |
| widget_config | pages/WidgetConfigureActivity.ets | 卡片配置（含旧命名后缀，剥后用 `widget_config`） |

## 6. ID ↔ persistence key 映射（状态层断言必填）

涉及"双重断言-状态层"的 UI id 必须在此表显式登记 persistence key 原值（grep 业务源码 `*Keys` 常量、`preferences.put*` 调用、`AppStorage.setOrCreate` 写入处实测）。**禁止 step3 用 strip(uiId) 推导**。

| UI id | persistence key | 来源 | 备注 |
|---|---|---|---|
| settings_show_hidden_items_toggle | `showHiddenItems` | SettingsKeys.SHOW_HIDDEN_ITEMS @ viewmodels/SettingsViewModel.ets:13 | snake↔camel 不一致，必须显式映射 |
| settings_use_english_language_toggle | (none) | onChange 是 TODO，不持久化 | ⚠️ spec gap → 用例标 _IMPL_MISSING，不写状态层断言 |
| included_folders_item_remove_btn_{i} | (none) | 纯列表 UI，无单 key | 仅意图层 |

`(none)` 两种含义：① onChange TODO/spec gap → `_IMPL_MISSING` RED；② 纯 UI 无状态 → "仅意图层 + 原因"。
```

## 注入规则（命名 + A1-A9）的单一来源

具体规则**不在本文件**重复，全部见 `test-case-template.md §4`（命名 + 9 类组件 + Settings 类页下限 + 灰色地带处理）。本文件只列**本页 ID 表 + 跨页面策略 + NEEDS_REVIEW + 未注入清单 + page_short 映射**。

## 字段速查

| 字段 | 填法 |
|------|------|
| **目标 ID** | `<page_short>_<purpose>_<kind>`，全小写 snake_case，≤32 字符，页面内唯一 |
| **注入位置** | `pages/<File>.ets:<行号>` 或 `components/<Sub>.ets:<行号>`，行号 grep 实测，标控件形态（如 `Grid()` / `Navigation 最外层` / `空态 Text`） |
| **规则** | A1-A9（test-case-template.md §4） |
| **用例引用** | design §C 表里的 用例 ID（一个 id 可被多个用例引用） |
| **命名策略** | 主用户前缀 / idPrefix prop / page_short 自前缀（仅复用 component 填） |

## 边界（写本文件时的约束）

- ❌ 不写 `.id()` 注入动作 / 不改源码（那是第二步）
- ❌ 不重复 design §C 的用例详细（只引用 用例 ID）
- ❌ 不写注入规则定义（指向 test-case-template.md §4）
- ✅ 必须填 NEEDS_REVIEW 表（即使为空，写 `(无)`）
- ✅ 必须填未注入清单（即使为空，写 `(无)` 表示源码与设计 §C 完全对齐）
- ✅ 必须填 §6 ID↔persistence key 映射（即使为空，写 `(无)` 表示本页无状态层断言）；任何 design §C 用例标"状态层 = AppStorage.get / @State" 的 → §6 必须有对应行
