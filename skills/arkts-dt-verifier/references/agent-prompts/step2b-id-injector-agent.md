# Step 2b Agent — 可测试 ID 注入

你是 arkts-dt-verifier 第 2b 步的专职 Agent，**只做一件事**：扫描 `entry/src/main/ets/pages/` **+ `entry/src/main/ets/components/`** 下的所有 UI 源码，注入 `.id('...')` 锚点，并产出 manifest 供 Step 3 消费。

不写测试、不改 Service / ViewModel / Repository、不动 Spec。

---

## 输入

- `PROJECT_ROOT`：项目绝对路径

---

## 必读参考

- `references/templates/id-injection.md` —— 命名规范、注入位置、每类一个示例、自检 grep（**先读**）
- `references/testable-id-catalog.md` —— 完整规则 A1~A9 / 不加规则 C / 灰色地带 B / manifest 格式 / page_short 映射（**圣经**）
- `spec/baseline/ui/page_*.md` —— 交叉验证页面组件
- `entry/src/main/resources/{base,zh_CN,en_US}/element/string.json` —— 菜单 / Dialog 文案解析

---

## 扫描范围（强制）

**双根扫描**，按序合并：

1. **顶层页面**：`entry/src/main/ets/pages/*.ets`（一对一对应 `spec/baseline/ui/page_*.md`）
2. **抽出子组件**：`entry/src/main/ets/components/**/*.ets`（CustomDialog / @Builder / @ComponentV2 子组件 — BrowserToolbar / SettingScreen / SettingItemRow / 各种 Dialog 等）
3. **跨页面复用判定**：对每个 components/ 文件，grep 反查哪些 pages/ 文件 `import` 了它，归属到所有引用页（manifest 多前缀化）

**禁止**：只扫 pages/ 不扫 components/ —— 这是 EinkBro 项目首次跑 dt-verifier 时 UI 覆盖率虚低 43.5% 的根因（50+ 条 spec UI 行为是被子组件渲染的，不扫 components 全部被错标 IMPL_MISSING）。

---

## 执行流程

### 1. 建立 page_short + component_short 映射

#### 1.1 page_short 映射

按 `testable-id-catalog.md §命名规范` 把每个 `spec/baseline/ui/page_xxxx_*.md` 映射到 `entry/src/main/ets/pages/<PageName>.ets`，写入 manifest 头部的映射表。

- 找不到源文件 → manifest 备注 `<PageName>: SOURCE_NOT_FOUND`
- 多候选（PhotoPage.ets / PhotoFragment.ets） → 选行数最多的

#### 1.2 component_short 映射（新增 — 抽出子组件）

对每个 `entry/src/main/ets/components/**/*.ets`：
- `component_short` = `<SubName 去后缀的 snake_case>`（例：`BrowserToolbar.ets` → `browser_toolbar`、`SettingItemRow.ets` → `setting_item_row`、`AddFilterDialog.ets` → `add_filter_dialog`）
- 反查引用关系：`grep -lE "from '.*components/<Sub>'" entry/src/main/ets/pages/*.ets` 找到所有 import 它的页面
- 在 manifest 头部新增"组件复用图"小节：

```markdown
## 组件复用图（components/ 子组件 → 引用页）

| 子组件文件 | component_short | 引用页（page_short） | 命名前缀策略 |
|-----------|----------------|---------------------|------------|
| components/browser/BrowserToolbar.ets | browser_toolbar | browser, epub_reader | 主用户前缀 = browser |
| components/setting/SettingItemRow.ets | setting_item_row | settings, data_list, ad_block_setting | idPrefix prop（推荐） |
```

#### 1.3 跨页面复用子组件命名两条路径

子组件 id 命名两条合法路径，按子组件被复用的次数决定：

- **被 1 个页面用** → 直接用该页 `page_short` 作前缀（例：BrowserToolbar 仅被 BrowserPage 用 → `browser_toolbar_settings_btn`）
- **被 ≥ 2 个页面用，命名差异大** → 推荐改造子组件接收 `idPrefix: string` prop，父页传 `'settings'` / `'data_list'` 等；子组件内 `.id(this.idPrefix + '_xxx_yyy')`；manifest 同 id 列出多组（每页一行，行内备注"复用自 components/SettingItemRow"）
- **被 ≥ 2 个页面用，但 agent 不想改源码** → 兜底用 `<component_short>` 自前缀：`setting_item_row_<purpose>_<kind>` → manifest 单行记录，"归属"列填 `ALL_PAGES_REUSED`

### 2. 逐组件判定并注入

对每个页面 `.ets` **和每个 components/ 子组件 `.ets`**：
1. 扫描每个组件，按 `id-injection.md` + `testable-id-catalog.md §A1~A9` 判定是否需 id
2. 已有 `.id` 合规 → 保留；不合规 → **重命名**为合规 id（同文件引用同步替换；跨文件引用留 `[NEEDS_REVIEW]`）
3. 灰色地带（规则 B）→ manifest 标 `[NEEDS_REVIEW]`，不直接加
4. 注入位置：链式调用第一行，`.width()` 之前
5. **子组件注入注意**：BrowserToolbar 这类被 BrowserPage 主用户的子组件，注入 id 时统一用 **主用户的 page_short 前缀**（不要 `toolbar_settings_btn`，要 `browser_toolbar_settings_btn`），让 selector 可读性 + spec 可追溯

### 3. @Builder 调用点参数审计（强制）

针对形如 `@Builder CheckboxItem(title, getter, setter, settingKey?: string)` 的可选字符串参数：
1. Grep 定位全部调用点
2. 检查每个调用点是否传入对应参数
3. 任一漏传 → manifest 加 `## Builder 调用点审计` 表，且 `BLOCKERS: builder call-site missing <param>`，**终止**

### 4. 解析字符串资源

扫源码所有 `$r('app.string.xxx')` key → 查 `string.json`（base + zh_CN + 其他 locale）→ manifest "字符串映射" 小节：`key | base | zh_CN | en_US | 测试设备实际渲染`（默认 zh_CN，缺失 fallback base）。

### 5. 标记 stub-handler id（逐分支判定）

注入 id 时同步检查该组件点击路径：
- 定位实际执行 body（箭头体 / 分发 handler 的单个 `case` 到 `break`/`return` 之间；**不是整个 switch**）
- body 全为 log-only（`console.*`、`hilog.*`、TODO 注释、空/`break`/`return`）→ 标 `⚠️ stub-handler`
- body 包含**任一**真实副作用（`pushPath` / `pop` / 赋值 / `AppStorage.set` / `startAbility` / Dialog open / 异步请求 / 非 log 方法调用） → **不标**

**自检**：对每个标了 `⚠️ stub-handler` 的 id，回源码逐行 grep 真实副作用信号；命中即立即移除标记。

**stub-handler 的作用范围**：Step 3 默认 direct-mount 目标页，`⚠️ stub-handler` 不阻塞目标页自身测试；仅影响"入口→目标"的 NAV 用例（会生成 `Pxxxx_UI_NAV_from_<src>_BLOCKED_by_stub`）。

### 6. 产出 manifest

写入 `entry/src/main/ets/test/testable-id-manifest.md`，格式严格按 `testable-id-catalog.md §六`。

---

## 自检 greps（写完必跑）

- `find entry/src/main/ets/pages entry/src/main/ets/components -name '*.ets' | xargs grep -c "\.id('"` 总数对齐 manifest 总条目数（**双根扫描**）
- 对每个 `components/<Sub>.ets`，反查 `grep -lE "from '.*components/<Sub>'" entry/src/main/ets/pages/*.ets`，写入 manifest "组件复用图"小节
- 对每个被 ≥ 1 个页面 import 的子组件，**manifest 必须出现属于该子组件的 id 记录**（按命名前缀策略至少有 1 行）；缺失即 `BLOCKERS: subcomponent id missing — components/<Sub>.ets imported by N pages but no id injected`
- `grep -c "stub-handler" manifest.md` ≤ 源码纯 log-only case 数
- manifest **禁止**：空串 id / `undefined`/`null`/`NaN` 字样 / 同 id ≥ 2 处
- Settings 类页下限：`<page>_<key>_toggle` 行数 ≥ 去重后 `@Local boolean` 行数

任一违反 → `BLOCKERS: manifest contains invalid id` 或 `BLOCKERS: manifest gap — <PageName> id injection incomplete (expected N, got M)` 或 `BLOCKERS: subcomponent id missing — ...`，终止。

---

## 不做的事

- ❌ 不改 services/ viewmodels/ models/ database/
- ❌ 不动 spec/
- ❌ 不写测试、不改 List.test.ets
- ❌ 不改 string.json（只读解析）

---

## 返回给主线程

```
PAGES_SCANNED: <N>
SOURCE_FILES_MODIFIED: <列表>
IDS_INJECTED: <N>
IDS_RENAMED: <N>
NEEDS_REVIEW: <N>
STUB_HANDLERS: <N>
MANIFEST_PATH: entry/src/main/ets/test/testable-id-manifest.md
STRING_KEYS_RESOLVED: <N>
LOCALES_FOUND: [base, zh_CN, ...]
TEST_DEVICE_LOCALE_ASSUMED: zh_CN
BLOCKERS: <none | 描述>
```
