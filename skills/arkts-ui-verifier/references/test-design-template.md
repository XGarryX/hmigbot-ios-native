# UI 测试用例方案模版（UI Design）

第一步「测试用例设计」的产物格式。**每页一份**，写到 `spec/test/ui-test/design/P{编号}_{PageName}.md`。

> 配套的 **ID 注入设计**也是每页一份，写到 `spec/test/ui-test/id-inject/P{编号}_{PageName}.md`，格式见 `references/id-inject-design-template.md`。本文件不再含 §E ID 注入计划（已独立）。

输入两个：

1. **Spec**：`spec/baseline/ui/page_{编号}_*.md`（该页面规格）+ `spec/baseline/features/F*.md`（含 `类型=ui` 且涉及该页的 AC）
2. **代码**：`entry/src/main/ets/pages/{PageName}.ets` + 该页引用的 `entry/src/main/ets/components/**`

设计阶段**不写测试代码、不注入 `.id()`**，只产出这份设计供第三步实现。

## 目标框架（UiTest 能力边界）

下游用 `@kit.TestKit` 的 `Driver` / `ON` / `findComponent` / `assertComponentExist` 实现。设计时每条用例的「操作 + 预期」必须落在 UiTest 能力内：

- **定位**：`ON.id(...)` (首选) / `ON.text(...)` (来自 `string.json`，禁止凭空翻译) / `ON.type(...)` (SMOKE landmark)
- **操作**：click / longClick / input / swipe / scroll / pressBack
- **断言**：意图层 `assertComponentExist` / `findComponent` 非 null / `getText` / `isChecked` / `isEnabled`；状态层 `AppStorage.get<T>('key')` / `LocalStorage` / 绑定的 `@State` + `expect(...).assertEqual(...)`
- **时序**：显式等待目标控件出现（轮询 landmark），**禁止固定 sleep**

落不到 UiTest（像素级渲染、动画过程、复杂手势真实手感）→ 按**标准 0** 标"转人工"，不硬塞。

## 最高标准（6 条铁律 · 任一违反即设计不合格）

**标准 0 — 可测性判定优先。**
逐个识别 spec 行为，先判定：可见+界面触发+控件可断言 → 纳入 UI 测试；纯逻辑（无 UI 依赖）→ 标 **"转 UT(Hypium)"**，本设计不收；动画/手感/像素/罕见渲染等无法稳定自动断言 → 标 **"转人工/探索性"**。绝不为凑覆盖率写"未崩溃 / 未抛异常"的空用例。

**标准 1 — 以需求覆盖为主轴，产追溯矩阵。**
spec 拆成原子需求（独立可验证的用户可见行为）。每条纳入的原子需求**至少被一条用例覆盖**，矩阵不允许空行。关键需求（核心流程、数据正确性）**必须正向 + 反向**。

**标准 2 — 强制覆盖五个维度（不得只写 happy path）。**
对每界面/组件逐维度检查（不适用就显式写 `N/A + 原因`）：

- **状态**：初始 / 加载中 / 数据正常 / 空数据 / 部分数据 / 错误 / 无网络 / 无权限
- **交互**：每个可交互控件的正常 + 边界（空输入 / 超长输入 / 快速重复点击 / 操作中断）
- **流程**：关键用户路径走通 + 中途退出 / 返回 / 中断后状态正确
- **数据流转**：跨页面 / 跨组件传值、路由参数、返回后状态保持
- **适配**（按 spec 相关性）：屏幕尺寸 / 横竖屏 / 深色模式 / 字体缩放 / 多语言

**标准 3 — 双重断言：意图达成 + 内存状态（缺一在 notes 写原因）。**
不写"应正常显示"。每条用例预期写两行（ArkUI UI 由 State 派生，单断一边都有盲区：单断 UI 漏"状态没存对，下次启动退化"；单断 State 漏"UI 没刷新，用户看不到"）：
- **预期-意图**（UI 用户视角）：`assertComponentExist(ON.id('home_root'))` / `getText() == '我的主页'` / `isEnabled() == false` / Toast 文本 = '账号或密码错误'
- **预期-状态**（声明式应用视角）：`AppStorage.get<User>('currentUser').name == 'alice'` / `AppStorage.get<boolean>('autoplay') == true` / 绑定 `@State` 等于目标值
纯渲染 SMOKE 或无对应状态键 → notes 标 `仅意图层 + 原因`。

**标准 4 — 每条用例可独立运行。**
明确**前置**（从哪页/状态开始、登录态、数据准备）+ **Mock 依赖**（外部接口/系统能力 + 期望返回值）。用例间不共享可变状态、不依赖执行顺序。

**标准 5 — spec 与代码冲突时以 spec 为准并标记。**
代码行为与 spec 不一致 → 按 **spec 预期**写（暴露 bug），并在该用例 notes 标注 `⚠️ spec↔代码冲突：<差异>`。不要把测试写成固化现有 bug。

**标准 6 — 用例集合最小且无冗余 + 标稳定性风险。**
最少用例覆盖最多行为，合并等价输入。每条标**稳定性风险**（是否依赖异步时序/跳转/动画 → flaky）+ **缓解方式**（显式等待 landmark，不固定延时）。

## 输出格式（严格按顺序）

```markdown
# P{编号} 测试设计：{PageName}

> Page Spec：spec/baseline/ui/page_{编号}_{Xxx}.md
> 相关源码：entry/src/main/ets/pages/{PageName}.ets, components/{Sub}.ets …（列出读过的）
> Mount Strategy：NAVIGATION_DIRECT_MOUNT | ROUTER_LOAD_CONTENT  ← 见 test-case-template.md §Mount

## A. 原子需求清单（含可测性判定）

| 需求ID | 来源 | 描述 | 可测性判定 | 处置 |
|--------|------|------|----------|------|
| R1 | page §转换决策 | MainPage 渲染 Grid 容器 | UI 可测 | 纳入 |
| R2 | F005 AC2 | 数据加载完成显示列表 | UI 可测 | 纳入 |
| R3 | page §状态接口 isFavorite | 收藏标记切换 | 纯逻辑（无 UI 触达） | 转 UT |
| R4 | page §转换决策 卡片入场动画 | 卡片动画流畅 | 像素/动画过程 | 转人工 |

## B. 需求-用例追溯矩阵（不允许空行 / 关键需求正反齐全）

| 需求ID | 用例ID | 类型 |
|--------|--------|------|
| R1 | P0002_UI_SMOKE_page_renders | SMOKE |
| R1 | P0002_UI_COMP_directory_grid_exists | COMP |
| R2 | F005_UI_AC02_loaded_shows_3_items | 正向 |
| R2 | F005_UI_AC02_empty_shows_placeholder | 反向 |

## C. 用例详细设计

### P0002_UI_SMOKE_page_renders
- **类型**：SMOKE
- **追溯**：R1
- **前置**：mountPage('MainPage')，TestDataSetup 已注入 2 个 directory
- **操作**：(无)
- **预期-意图**：`assertComponentExist(ON.id('main_root'))`
- **预期-状态**：`AppStorage.get<boolean>('__TEST_MODE__') == true` 且 `AppStorage.get<Array>('__MOCK_DIRECTORIES__').length == 2`（mock 已注入）
- **依赖/Mock**：MainPage 用 DirectoryRepository.list()，需 mock 返回 2 条
- **稳定性**：低风险；landmark 显式等待
- **当前实装**：已实现 → 预期 GREEN（或 未实现 → 预期 RED + 说明）

### F005_UI_AC02_empty_shows_placeholder
- **类型**：反向（空数据）
- **追溯**：R2
- **前置**：TestDataSetup 注入 0 条 directory
- **操作**：(无)
- **预期-意图**：`assertComponentExist(ON.id('main_empty_placeholder'))`，文本含"暂无数据"
- **预期-状态**：`AppStorage.get<Array>('__MOCK_DIRECTORIES__').length == 0`（空 mock 已生效，证空态不是渲染巧合）
- **依赖/Mock**：DirectoryRepository.list() 返回 `[]`
- **稳定性**：低；landmark
- **当前实装**：未实现 → 预期 RED（暴露空态占位缺失）

…

## D. 覆盖缺口与风险

- **未覆盖需求**：(无 / 列出)
- **转 UT 项**：R3（收藏切换逻辑），交 arkts-ut-verifier
- **转人工项**：R4（卡片入场动画），人工探索
- **flaky 风险**：F005_UI_AC02_loaded_shows_3_items 依赖异步加载，已用 landmark 轮询缓解

## E. (已迁出) ID 注入计划

> §E 已独立成 `spec/test/ui-test/id-inject/P{编号}_{PageName}.md`，本文件不再写 §E。
> 格式与字段见 `references/id-inject-design-template.md`。第一步 agent 同实例顺手产两份（design + id-inject）。

## F. 测试数据 setup 计划

- **Mount Strategy**：NAVIGATION_DIRECT_MOUNT（根页 `MainPage.ets` 含 `: NavPathStack` 字段）
- **EntryAbility 桥**：注入 `__test_mode__` + `__target_page__` 检测 → `AppStorage.setOrCreate`
- **根页桥**：`@Watch('targetPage')` → `navPathStack.pushPath({ name: targetPage })`；宿主页特判（消费 token 不 push）
- **TestDataSetup 预置**：
  - `__MOCK_DIRECTORIES__` = `[{ path: 'DCIM/Camera', name: 'Camera' }, { path: 'Pictures/Test', name: 'Test' }]`
  - 空数据用例临时覆盖 `__MOCK_DIRECTORIES__ = []`
- **Service 旁路**：`DirectoryRepository.list()` 首句加 `if (AppStorage.get<boolean>('__TEST_MODE__')) return AppStorage.get('__MOCK_DIRECTORIES__')`
```

## 每页 AC 类型推导（设计阶段就要列齐）

每页**至少**这些类型（合并到 §C 详细设计；不适用就在 §D 写 `N/A + 原因`）：

| 类型 | 派生规则 | 命名 |
|------|---------|------|
| **SMOKE** | 从 Want 启动该页面，断言根容器存在 | `P{id}_UI_SMOKE_page_renders` |
| **COMP** | spec `## 转换决策` 每个顶层组件一条 `assertComponentExist` | `P{id}_UI_COMP_{组件}_exists` |
| **NAV 入** | spec `## 导航关系` 中"由其他页跳入" | `P{id}_UI_NAV_from_{来源}` |
| **NAV 出** | spec `## 导航关系` 中"跳出到其他页" | `P{id}_UI_NAV_to_{目标}` |
| **INTERACT** | 见下方枚举铁律 | `P{id}_UI_INTERACT_{action}_{effect}` |
| **Feature 派生** | `features/F*.md` 中 `类型=ui` 且涉及该页的 AC | `F{编号}_UI_AC{序号}_{行为}` |

### INTERACT 枚举铁律（每项独立 it，禁止合并）

- `## 菜单项` / `## 溢出菜单`：**每一项**一条 `it`（点菜单 → 点该项 → 对应动作）
- `## CAB`：**每条动作**一条（长按进 CAB → 点该动作 → 效果生效）
- `## 设置项` / TextValueRow / OneLinerRow：**每一项**一条（点击 → Dialog 弹出）
- `## 状态接口` `@State boolean`：**每个布尔**一条（点 Toggle → checked 翻转）
- 可滚动页（`Scroll` / `NestedScrollView`）额外 1 条 `scroll_to_bottom_reveals_*`

判据：spec 出现"N 项/N 组/每个/1:1 对应/复用 @Builder/列出" → 硬性展开。**禁止**把 N 项合并成"菜单弹出"或"Toggle_exists"。

## 字段说明速查

| 字段 | 填法 |
|------|------|
| **用例ID** | `P{编号}_UI_{TYPE}_{描述}` 或 `F{编号}_UI_AC{序号}_{行为}`，全局唯一、跨轮稳定 |
| **类型** | SMOKE / COMP / NAV / INTERACT / 正向 / 反向（覆盖标准 2 五维度对应一类） |
| **追溯** | 对应 §A 的需求 ID（保证可回溯，对应标准 1） |
| **前置** | 起始页 + 数据准备 + Mock 状态（对应标准 4） |
| **预期-意图** | UI 用户视角的具体可断言事实（控件 + 特征 + 值，对应标准 3） |
| **预期-状态** | 应用内存视角的状态键 + 值（`AppStorage.get<T>('key')` / `@State`，对应标准 3）；纯渲染无对应状态键 → 在 notes 标"仅意图层 + 原因" |
| **依赖/Mock** | 外部依赖 + 期望返回值（对应标准 4） |
| **稳定性** | 低 / 中 / 高 + 缓解（对应标准 6） |
| **当前实装** | 已实现→GREEN / 未实现→RED / 部分→RED（决定预期；对应 ut 的实装判断同口径） |
