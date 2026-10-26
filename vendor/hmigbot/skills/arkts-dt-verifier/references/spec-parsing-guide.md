# Spec 解析指南

## 目录

- [两类 Spec 文件的定位](#两类-spec-文件的定位)
- [Feature 文件解析](#feature-文件解析)
- [UI Spec 文件解析](#ui-spec-文件解析)
- [AC 分类决策树](#ac-分类决策树)
- [Feature → 页面映射](#feature--页面映射)
- [源码分析：识别实现状态](#源码分析识别实现状态)

---

## 两类 Spec 文件的定位

```
spec/baseline/
├── features/F00x-xxx.md   ← 主 AC 来源：所有测试（单元 + UI）从这里读
└── ui/page_000x_xxx.md    ← UI 辅助：提供组件定位符、导航关系、@Local 状态变量名
```

**测试生成的起点始终是 Feature 文件的 `## 验收标准`**。UI spec 文件不用于生成 AC，而是在你需要写 `ON.text()` / `ON.type()` 定位符时查找具体组件信息。

---

## Feature 文件解析

### 实际格式

```markdown
# F006: 全库搜索

## 范围
涉及页面: SearchPage
依赖: feature-base, F001

## 数据流
...（理解业务逻辑用，不直接生成测试）

## 服务层
```typescript
class SearchService { ... }
```

## 对接点
- SearchPage: SearchMenuBar 的 onSearchTextChanged → 触发 filterMedia
- 结果点击 → ViewPagerPage（图片）/ openPath（视频）

## 验收标准
- [ ] 搜索框自动聚焦
- [ ] 实时过滤（文件名包含搜索词）
- [ ] 精确匹配排在前面
- [ ] 无结果时显示空状态提示
- [ ] 清空搜索词 → 显示全部媒体
```

### 关键字段提取

| 字段 | 用途 |
|------|------|
| `# F00x: 名称` | Feature 编号和名称 |
| `## 范围 → 涉及页面:` | 知道哪些页面需要 UI 测试 |
| `## 服务层` | 找到可 Mock 的 Service/Repository 类名 |
| `## 对接点` | UI 交互触发点（哪个组件触发哪个方法） |
| `## 验收标准` | **全部 AC**，单元测试和 UI 测试都从这里来 |

### 验收标准格式

```
- [ ] <验收描述>
```

- `- [ ]` = 未实现（待验证）
- `- [x]` = 已确认实现（仍应写测试）

每条 `- [ ]` 生成一个 `it()` 测试用例。

---

## UI Spec 文件解析

UI spec 文件在需要写具体 UI 定位符时查阅，不需要全部读完。

### 有用的字段

**`## 转换决策`** — 找 ON.type() 的值

```markdown
| RecyclerView (Grid) | Grid + LazyForEach |
| RecyclerView (List) | List + LazyForEach |
```

→ UI 测试中用 `ON.type('Grid')` 或 `ON.type('List')` 定位

**`## 导航关系`** — 知道哪个 item 点击后跳转到哪里

```markdown
| 触发 | 目标页面 | 类型 |
| 目录 item 点击 | MediaPage | push，传递 path/name |
| 搜索按钮点击 | SearchPage | push |
```

→ UI 测试导航用例的操作序列

**`## 状态接口`** — 了解页面状态变量，判断测试后状态变化

```markdown
| directories | Directory[] | DirectoryRepository |
| isGridView  | boolean     | AppStorage (config) |
```

**查询 UI spec 的时机**：写 UI 测试时，先根据 Feature AC 确定要测什么，再去对应的页面 spec 查找组件类型 / 文本 / ID，而不是一开始就通读所有 UI spec。

---

## 页面级 UI AC 推导（Step 3 专用）

Step 3 Agent 除了消费 Feature 文件的 UI AC，还要**只依据 spec**（`spec/baseline/ui/page_*.md`）为每个页面派生一组 `P{编号}_UI_*` 用例。**不读 `.ets` 源码，不读 Android `view.xml`/`meta.json` snapshot**。

### AC 类型清单（每页至少产出这些）

| 类型 | 生成规则 | 命名 |
|------|---------|------|
| SMOKE | 从 Want 启动该页面，断言不崩溃 | `P{id}_UI_SMOKE_page_renders` |
| COMP | `## 转换决策` 表每个顶层组件一条 `assertComponentExist` | `P{id}_UI_COMP_{组件名}_exists` |
| NAV（入） | `## 导航关系` 中"由其他页面跳入"条目 | `P{id}_UI_NAV_from_{来源页}` |
| NAV（出） | `## 导航关系` 中"跳出到其他页面"条目 | `P{id}_UI_NAV_to_{目标页}` |
| INTERACT | 见下方三源推导 | `P{id}_UI_INTERACT_{action}_{effect}` |

### INTERACT 双源推导规则

**源 A：页面 Spec 的专节**

| Spec 小节 | 交互 | 断言形态 |
|----------|------|---------|
| `## 菜单项` / `## 菜单` / `## 溢出菜单` | **每一项**分别：点菜单 → 点该项 → 对应动作 | 逐项 `it()`：点击后 `dumpLayout` 找到具体项；点击后预期 Dialog / 页面跳转 / 状态变化 |
| `## CAB` | **每条动作**分别：长按进入 CAB → 点该动作 → 效果生效 | 逐条 `it()`：CAB 出现、点具体动作有断言 |
| `## 设置项` / `TextValueRow` / `OneLinerRow` | **每一项**独立 `it()`：点击 → Dialog 弹出 | `dumpLayout` 能找到 Dialog；找不到 → FAIL |
| `## 状态接口` `@Local` 布尔表（Settings/Preferences） | **每一个布尔**独立 `it()`：点对应 Toggle → checked 翻转 | 断言点击前后 `isChecked()` 翻转 |

> ⚠️ **枚举铁律**（v6→v7 教训；详见 `ui-test-antipatterns.md` 反模式 11/12 + `step3-ui-test-agent.md` §E1/E2/E3）
> 上表"每一项/每条/每一个布尔"是硬性展开要求，不是装饰。**禁止**把 N 项合并成一条"菜单弹出"或"Toggle_exists"。枚举信号词：spec 里出现"N 项/N 组/每个/1:1 对应/复用 @Builder/列出"。可滚动页（`Scroll` / `NestedScrollView`）额外需 1 条 `scroll_to_bottom_reveals_*`。

**源 B：`## 转换决策` 组件语义**

| 组件 | 交互 | 断言 |
|------|------|------|
| Toggle / Switch / Checkbox | 点击 → `checked` 翻转 | 前后 `checked` 翻转 |
| Swiper | 左右滑动切换 | `getPageSig` 或当前索引变化 |
| Refresh | 下拉刷新 | `swipeDown` 后不崩、刷新态短暂出现后消失 |
| List / Grid + LazyForEach（若 `## CAB` 存在）| 长按进入多选 | 同源 A CAB |
| bindMenu / bindContextMenu | 长按/点击触发 | 触发后 `dumpLayout` 能找到菜单项 |
| Search / TextInput | 输入文本 | `text` 属性变化 |

### 去重

- COMP 与 INTERACT 不冲突（前者检存在性，后者检行为），都保留
- 若 Feature UI AC 与 INTERACT 语义重合，保留 Feature 派生的（追溯更清晰），丢弃 INTERACT 重复项

### 单一状态原则

多步交互（长按 → CAB 出现 → 点全选 → 全选生效）必须**拆成多条 `it()`**，每条只验单一状态变化。每个 INTERACT 用例开头要确保应用处于该页面。

---

## AC 分类决策树

拿到 `## 验收标准` 的每条 AC，按以下规则分类：

```
AC 描述包含以下特征 → UI 测试（Step 3）
  ✦ 用户行为词：点击、输入、滑动、长按、聚焦、下拉刷新
  ✦ 视觉状态词：显示、出现、消失、可见、高亮、置灰
  ✦ 页面/导航词：跳转、返回、打开、进入、回到主页
  ✦ 空态/占位词：空状态提示、无结果、占位图
  ✦ 跨页面联动：在 A 页操作后 B 页出现变化

AC 描述包含以下特征 → 单元测试（Step 1）
  ✦ 纯逻辑词：计算、格式化、排序、过滤、分组、判断
  ✦ 持久化词：保存、重启后保持、写入 DB、更新记录
  ✦ 方法调用词：调用了 xxx、触发了 yyy（内部调用链）
  ✦ 无 UI 的状态变化：isFavorite 更新、deletedTS 设置
```

### 实例分类（F004 收藏夹）

```
- [ ] 在 ViewPager 中标记收藏后，Favorites 目录出现该媒体   → UI 测试
- [ ] 取消收藏后从 Favorites 目录移除                       → UI 测试
- [ ] App 重启后收藏状态保持                               → 单元测试（MockKit，验证 DB 写入）
- [ ] Favorites 虚拟目录在 MainPage 始终固定显示           → UI 测试
```

### 实例分类（F006 搜索）

```
- [ ] 搜索框自动聚焦                  → UI 测试（页面打开即聚焦）
- [ ] 实时过滤（文件名包含搜索词）    → 单元测试（纯函数 filterMedia）
- [ ] 精确匹配排在前面               → 单元测试（纯函数 sort 逻辑）
- [ ] 无结果时显示空状态提示          → UI 测试（视觉反馈）
- [ ] 清空搜索词 → 显示全部媒体       → 单元测试（纯函数） + UI 测试（页面状态）
```

> **一条 AC 可同时生成两个测试**：逻辑层验证 filter 方法的返回值，UI 层验证空态组件是否出现。这种情况优先写单元测试，UI 测试作为补充。

---

## Feature → 页面映射

读取 Feature 文件的 `## 范围 → 涉及页面` 后，根据页面名称找到对应的 UI spec 文件：

| Feature 文件中的页面名 | 对应 UI spec 文件 |
|----------------------|-----------------|
| MainPage             | ui/page_0002_MainActivity.md |
| MediaPage            | ui/page_0003_MediaActivity.md |
| SearchPage           | ui/page_0004_SearchActivity.md |
| ViewPagerPage        | ui/page_0005_ViewPagerActivity.md |
| VideoPlayerPage      | ui/page_0007_VideoPlayerActivity.md |
| SettingsPage         | ui/page_0010_SettingsActivity.md |

如果页面名没有对应 UI spec，只做单元测试，跳过 UI 测试。

---

## 源码分析：识别实现状态

读取对应源文件，判断每个 AC 相关方法的实现状态：

### 已实现（GREEN 候选）

```typescript
// 有实质性逻辑
get isInRecycleBin(): boolean {
  return this.deletedTimestamp > 0
}
```

```typescript
filterMedia(media: ThumbnailItem[], query: string): ThumbnailItem[] {
  if (!query.trim()) return media
  return media.filter(m => m.filename.toLowerCase().includes(query.toLowerCase()))
}
```

### TODO / 未实现（RED 候选）

```typescript
// 只有 console.info
async moveToRecycleBin(item: Medium): Promise<void> {
  console.info('moveToRecycleBin TODO')
}

// 空方法体
async share(paths: string[]): Promise<void> {}

// throw 占位
async restore(): Promise<void> {
  throw new Error('Not implemented')
}
```

### 部分实现

对部分实现的方法，为已实现部分写 GREEN 测试，为缺失部分写 RED 测试，在注释中注明：

```typescript
// 注释：RED — 内存操作完成但未写 DB，F004_AC03 持久化部分未实现
it('F004_AC03_toggle_persists_to_db', 0, async () => {
  // ...
})
```

---

## 完整解析流程

1. 读 `spec/baseline/features/` 所有文件
2. 提取每个文件的 Feature 编号 + `## 范围 → 涉及页面` + `## 验收标准`
3. 按决策树给每条 AC 打标：`unit` 或 `ui`（或两者都有）
4. 对 `unit` 类：读源码确认实现状态 → 生成测试
5. 对 `ui` 类：读对应页面的 `## 转换决策` 和 `## 导航关系` → 补充组件定位符 → 生成测试
