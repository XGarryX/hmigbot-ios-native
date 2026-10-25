# AC 索引文件格式说明

## 文件位置

```
entry/src/ohosTest/ets/test/tdd-ac-index.md
```

由 `arkts-dt-verifier` 第一步（解析 Spec）自动生成，后续步骤和跨对话恢复时直接读取，无需重新解析 Spec。

---

## 完整格式

```markdown
# TDD AC 索引
> 由 arkts-dt-verifier 第一步自动生成，勿手动修改
> 生成时间：YYYY-MM-DD

## F001 媒体扫描
涉及页面：MainPage, MediaPage
服务层：MediaFetcherService, MediaRepository

| AC | 描述 | 类型 | 实现状态 | 运行结果 | 源码位置 |
|----|------|------|---------|---------|---------|
| AC1 | 启动时扫描所有目录 | unit | todo | — | MediaFetcherService.scanDirectories() |
| AC2 | 目录显示媒体数量角标 | ui | — | — | MainPage GridItem |
| AC3 | 点击目录进入 MediaPage | ui | — | — | MainPage → MediaPage 导航 |
| AC4 | 下拉刷新重新扫描 | ui | — | — | MediaPage Refresh 组件 |
| AC5 | 支持过滤：图片/视频/全部 | unit | pure_function | — | Medium.isImage / isVideo |

## F002 媒体查看器
涉及页面：ViewPagerPage
服务层：FavoritesRepository, MediaRepository

| AC | 描述 | 类型 | 实现状态 | 运行结果 | 源码位置 |
|----|------|------|---------|---------|---------|
| AC1 | 左右滑动切换媒体 | ui | — | — | ViewPagerPage Swiper |
| AC2 | 点击切换工具栏显隐 | ui | — | — | ViewPagerPage 沉浸式状态 |
| AC3 | 获取相邻索引边界处理 | unit | pure_function | — | ViewerViewModel.getAdjacentIndex() |
| AC4 | 收藏状态内存切换 | unit | pure_function | — | ViewerViewModel.toggleFavorite() |
| AC5 | 收藏状态持久化 | unit | todo | — | FavoritesRepository.add() |
| AC6 | 删除后自动切换到下一项 | ui | — | — | ViewPagerPage 删除回调 |

## F003 …
…

---

## 来源：页面 Spec（P00xx）
> 由 Step 3 UI 测试 Agent 追加，覆盖 `spec/baseline/ui/page_*.md` 全部页面
> 表头与 Feature 主表对齐，`实现状态` 固定填 `—`（UI 类不适用），`运行结果` 由 Step 5 写入

| AC ID | 页面 | 类型 | 实现状态 | 运行结果 | it() 名 |
|-------|------|------|---------|---------|---------|
| P0002_UI_SMOKE | MainPage | smoke | — | — | P0002_UI_SMOKE_page_renders |
| P0002_UI_COMP_Grid | MainPage | comp | — | — | P0002_UI_COMP_Grid_exists |
| P0002_UI_NAV_to_MediaPage | MainPage | nav | — | — | P0002_UI_NAV_to_MediaPage |
| P0002_UI_INTERACT_long_press_item_shows_cab | MainPage | interact | — | — | P0002_UI_INTERACT_long_press_item_shows_cab |
| F001_UI_AC03_click_directory_navigates | MainPage | feature_derived | — | — | F001_UI_AC03_click_directory_navigates |
| P0002_UI_INTERACT_cab_select_all_triggers_select_all_IMPL_MISSING | MainPage | impl_missing | — | — | P0002_UI_INTERACT_cab_select_all_triggers_select_all_IMPL_MISSING |
| P0006_UI_UNREACHABLE_page_renders | WidgetConfigurePage | unreachable | — | — | P0006_UI_UNREACHABLE_page_renders |
| … | | | | | |
```

---

## 字段说明

| 字段 | 取值 | 说明 |
|------|------|------|
| `AC` | AC1, AC2 … | 对应 Spec `## 验收标准` 的第 N 条 `- [ ]` |
| `描述` | 简短中文描述 | 直接从 Spec 摘录 |
| `类型` | Feature 主表：`unit` / `ui`；Page 来源节：`smoke` / `comp` / `nav` / `interact` / `feature_derived` / `impl_missing` / `unreachable` | Feature 主表按 `spec-parsing-guide.md` 决策树分类；Page 来源节细分 Step 3 产出的各类 UI 用例（`impl_missing` = R1 占位；`unreachable` = R2 占位） |
| `实现状态` | `pure_function` / `mockkit` / `todo` / `deferred` / `—` | **静态分类标签，仅 Step 1 写入**，用于指导测试模板选择；生成后不再修改 |
| `运行结果` | `GREEN` / `RED` / `ERROR` / `skipped-compile` / `—` | **动态运行结果，仅 Step 5 写入**；Step 1 初始填 `—`，第五步跑完后覆盖 |
| `源码位置` | 方法全名或页面组件 | 便于第二步快速定位，ui 类填组件名 |

### 实现状态取值（Step 1 写入，之后不再改）

- `pure_function`：方法无外部依赖，可直接构造输入断言输出
- `mockkit`：方法依赖 DB / fileIo / photoAccessHelper 等，需 MockKit 隔离
- `todo`：方法体只有 `console.info` 或为空，功能未实现，测试预期 RED
- `deferred`：MockKit 策略选 B，已暂挂；不生成测试、不计入分母
- `—`：UI 类 AC，不适用

### 运行结果取值（Step 5 写入）

- `GREEN`：断言通过，功能已实现
- `RED`：断言失败，功能未实现；在"RED 清单"中附失败摘要
- `ERROR`：运行时报错（非断言失败），需排查环境/代码异常
- `skipped-compile`：因为编译失败被注释掉注册，不计入分母
- `—`：第五步未跑（例如策略选 B 的 deferred，或该 AC 本身标 deferred）

---

## 使用规则

- **第一步结束时必须生成此文件**，即使还未写测试代码
- **第二步**（测试数据预制）读取此文件，从 `涉及页面` 字段提取需要预制数据的页面列表
- **第三步**（UI 测试）读取此文件，筛选 `类型 = ui` 的条目，按 `涉及页面` 分组生成页面测试文件
- **跨对话恢复**：新对话开始时先读此文件，确认 AC 列表完整后再继续生成测试
- 若文件不存在，必须先执行第一步重新生成
