---
name: arkts-pattern-library
description: 生成 ArkTS/HarmonyOS 常见业务功能的完整实现方案（V2 优先，API 12+）。当用户需要实现搜索、列表详情页、登录注册、下拉刷新/加载更多、Tab 内容切换、个人中心、设置页、主题切换、空状态、骨架屏、播放器 UI、下载管理 UI、Feed 详情页，或任何完整业务功能时，务必触发此 skill。即使只说"做个搜索""写个列表页"也应触发。这是综合模式库，与其他 skill 配合使用。仅单个组件或技术点（非完整业务功能）→ arkts-component-builder / arkts-navigation-builder。
metadata:
  type: domain
  domain: ui
  tags:
  - ui
  - pattern
  - arkts-v2
  - business-feature
---
# ArkTS Pattern Library — 综合功能模式库（V2 优先）

## API 版本与项目策略

本 skill 的代码模板基于 **API 12+（HarmonyOS 5.0.0+）和 ArkTS V2 装饰器体系**。

> **项目锁 V2**：本项目所有新生成代码使用 V2 装饰器（`@ComponentV2 / @Local / @Param / @Event / @Once / @Provider / @Consumer / @ObservedV2 / @Trace / @Monitor / @Computed / AppStorageV2 / PersistenceV2`）。如需 V1 兼容写法查阅，参阅 `references/auth-pattern.md`、`references/list-detail-pattern.md`、`references/search-pattern.md`、`references/media-app-pattern.md`、`references/performance-patterns.md` 等 V1 历史文档（已加 legacy 标识）。

V2 vs V1 关键差异（影响本 skill 模式实现）：

| V1 装饰器 | V2 等价 | 备注 |
|---|---|---|
| `@Component` | `@ComponentV2` | struct 装饰器 |
| `@State` | `@Local` | 组件内部状态 |
| `@Prop`（单向只读） | `@Param + @Once` | V2 显式标记不可改 |
| `@Link`（双向） | `@Param + @Event` 回调（V2 无 @Link 等价） | V2 强调单向数据流 + 事件 |
| `@Provide / @Consume` | `@Provider() / @Consumer()` | 必须带括号；`@Consumer` 必须给默认值 |
| `@Observed + @ObjectLink` | `@ObservedV2 + @Trace`，组件直接用 `@Param` 持有实例 | V2 简化对象引用 |
| `@StorageLink('key')` | `@Local x: Cls = AppStorageV2.connect(Cls, 'key', () => new Cls())!` | 配合 `@ObservedV2` 类 |
| `PersistentStorage.persistProp` | `PersistenceV2.globalConnect({type, key, defaultCreator})` | V2 一站式持久化 + UI 响应式 |
| `@Watch('method')` | `@Monitor('prop') method(m: IMonitor)` | V2 是方法装饰器 |
| `@Reusable` | `@ReusableV2` | V2 复用组件 |

使用 `@kit.*` 导入（不要用 `@ohos.*`）。使用 Navigation 导航（不要用 @ohos.router）。`@Param` 必须初始化默认值。遇到版本兼容性或其他不确定的 ArkTS 知识点（如属性、语法、权限等），参阅 arkts-knowledge-verifier skill。

---

## 模式索引

| 模式名称 | 一句话描述 | 涉及技术（V2） |
|---------|----------|---------|
| 列表详情页 | 列表页 → 点击 → 详情页 | Navigation + LazyForEach + NavDestination + @ComponentV2 |
| 搜索功能 | 搜索框 + 历史 + 实时搜索 + 结果列表 | TextInput + Preferences + 防抖 + @Local |
| 下拉刷新加载更多 | 上拉触底加载更多 + 下拉刷新 | Refresh + List.onReachEnd + BasicDataSource + @Local |
| Tab 内容切换 | 顶部/底部标签切换不同内容 | Tabs + TabContent + @Builder |
| 登录状态管理 | 登录/未登录切换显示 | AppStorageV2.connect + @ObservedV2 类 |
| 设置页面 | 开关/选项/版本信息列表 | List + ListItem + Toggle + PersistenceV2 |
| 空状态 & 加载态 | 加载中/空数据/错误状态切换 | if/else + @Local 枚举 |
| 瀑布流 | 不等高卡片网格 | WaterFlow + FlowItem |
| 播放器 UI | MiniPlayer + FullPlayer 双态播放器 | AVPlayer + AppStorageV2 + @ObservedV2 + NavDestination |
| 下载管理 UI | 进度环 + 取消按钮 + 完成状态 | Progress Ring + request.agent + @Local |
| Feed 列表+详情页 | 网格订阅列表 → Feed 详情 → 剧集详情 | List + Grid + NavPathStack |
| 带校验的表单页 | 实时校验 + 提交按钮联动 | TextInput + @Computed + @Local 错误态 |
| 底部 Sheet/模态 | 筛选/分享/评论面板（草稿态隔离） | bindSheet + @Builder + $$ 双向绑定 |

---

## 模式实现（详见 references）

> **MUST**：实现某业务模式前，先读对应 reference 的完整模板——

> - 列表详情页 / 下拉刷新+加载更多 / 父子双向同步 → `references/v2-list-detail-pattern.md`
> - 搜索功能（历史 / 防抖 / 实时 / @Monitor 监听） → `references/v2-search-pattern.md`
> - 登录状态管理 → `references/v2-auth-pattern.md`
> - 设置页 / 主题切换 / 派生状态 @Computed → `references/v2-media-app-pattern.md`
> - 长列表性能 / LazyForEach 优化 / @Computed → `references/v2-performance-patterns.md`
> - 带校验的表单页（实时校验 + 提交联动）/ 底部 Sheet·模态（筛选/分享面板，草稿态隔离） → `references/v2-form-and-sheet-patterns.md`

> 空状态 & 加载态见下方（本 skill 内联，未单列 reference）。

---

## 模式 5：空状态 & 加载态

```typescript
enum PageState { Loading, Success, Empty, Error }

@ComponentV2
struct StatefulPage {
  @Local pageState: PageState = PageState.Loading

  build() {
    Column() {
      if (this.pageState === PageState.Loading) {
        LoadingProgress().width(48).height(48)
      } else if (this.pageState === PageState.Empty) {
        Text('暂无数据')
      } else if (this.pageState === PageState.Error) {
        Button('重试').onClick(() => this.loadData())
      } else {
        List() { /* 数据列表 */ }
      }
    }
  }

  loadData(): void { this.pageState = PageState.Loading }
}
```

**关键点**：用枚举管理页面状态，根据状态条件渲染不同 UI。

---

## 组合说明

这些模式通常需要组合使用：

| 功能 | 需要配合的 skills |
|------|-----------------|
| 列表详情页 | component-builder + navigation-builder + data-layer |
| 搜索功能 | component-builder + data-layer（Preferences） |
| 下拉刷新列表 | component-builder + data-layer（BasicDataSource） |
| 登录状态 | state-manager（AppStorageV2 + @ObservedV2） |
| 设置页面 | state-manager + component-builder（PersistenceV2） |
| 完整应用 | project-scaffolder + 以上全部 |

---

## Multi-Skill 编排协议

本 skill 提供的业务模式通常需要多个 skill 协作完成。当你被触发后，根据用户的具体需求，按以下指引读取其他 skill 的 reference 文件来生成完整方案。

### 执行顺序

生成完整业务功能时，按此顺序生成各层代码：

```
Model（数据模型，含 @ObservedV2）→ DataSource（数据源）→ State（状态管理 / AppStorageV2 / PersistenceV2）→ Navigation（导航）→ UI（@ComponentV2 页面组件）→ Animation（动画，可选）
```

### 场景路由表

| 业务场景 | 需要读取的 reference | 生成内容 |
|---------|---------------------|---------|
| **列表详情页** | ① `arkts-data-layer/SKILL.md`"数据模型"节 ② `arkts-data-layer/references/datasource-patterns.md` ③ `arkts-navigation-builder/SKILL.md`"NavDestination 页面模板"节 | Model + BasicDataSource + Navigation 框架 + 列表页 + 详情页（V2） |
| **搜索功能** | ① `arkts-data-layer/references/network-service.md` | 网络请求 + SearchView + Preferences 持久化（V2） |
| **下拉刷新列表** | ① `arkts-data-layer/references/datasource-patterns.md` ② `arkts-data-layer/references/network-service.md` | BasicDataSource + 分页请求 + Refresh 列表（V2） |
| **登录状态** | ① `arkts-state-manager/references/v2-global-state.md` ② `arkts-data-layer/references/network-service.md` | AppStorageV2 + @ObservedV2 AuthState + 登录接口 + 状态切换 UI |
| **设置页面** | ① `arkts-state-manager/references/v2-global-state.md` ② `arkts-component-builder/references/common-components.md` | PersistenceV2 持久化设置 + Toggle/List 组件 |

### 编排流程

1. **识别场景**：根据用户请求匹配上方场景路由表
2. **读取 reference**：用 Read 工具按表中顺序读取所需的 reference 文件
3. **按顺序生成**：Model → Service → Page，确保依赖关系正确
4. **分文件输出**：每个文件用 `// === 文件路径 ===` 标注，方便用户复制
5. **验证检查**：读取 `arkts-knowledge-verifier/references/arkts-vs-typescript.md` 确认无 ArkTS 幻觉

> 完整的路由矩阵和输出格式规范见 `arkts-knowledge-verifier/references/skill-routing-guide.md`

---

## 生成检查清单

- [ ] 所有 struct 用 `@ComponentV2`（不要 V1 `@Component`）
- [ ] 所有可观察类用 `@ObservedV2` + `@Trace` 属性（不要 V1 `@Observed`）
- [ ] `@Trace` 只加在**驱动 UI 渲染**的可变字段上；VM/model 内部只做记账/控制流的字段（请求计数器、重试次数、非渲染标志等）用**普通字段、不加 @Trace**（自增不触发刷新），且**除非需求明确要展示**否则不渲染到 UI——判定与范例见 `references/v2-performance-patterns.md` §3
- [ ] `@Local` 变量已初始化（不要 V1 `@State`）
- [ ] `@Param` 必须有默认值（V2 强制），只读场景加 `@Once`
- [ ] 父子双向用 `@Param + @Event`（不要试图用 V1 `@Link`）
- [ ] 全局状态用 `AppStorageV2.connect(Cls, key, () => new Cls())!`（不要 V1 `@StorageLink`）
- [ ] 持久化用 `PersistenceV2.globalConnect({type, key, defaultCreator})`（不要 V1 `PersistentStorage.persistProp`）
- [ ] 监听用 `@Monitor('prop') method(m: IMonitor)`（不要 V1 `@Watch`）
- [ ] V2 装饰器与伴随类型（`@Local/@Param/@Monitor/@ObservedV2/@Trace/@Computed/IMonitor`…）**及组件控制器类**（`Scroller`/`TabsController` 等——裸用 `new Scroller()`/`new TabsController()`、`.scrollEdge()`/`.changeIndex()`）都是框架 **ambient 符号、绝不 import**（误写 `import { TabsController } from '@kit.ArkUI'` → `'TabsController' is not exported from Kit '@kit.ArkUI'`；`Scroller` 同理）。但**用作值的真实导出类/对象仍须 import** `from '@kit.ArkUI'`：`AppStorageV2`/`PersistenceV2`（`.connect(...)`）、`LengthMetrics`（`.vp(n)`）、`ComponentContent`（组件控制器不在此列）——漏 import 报 `Cannot find name` 或 `only refers to a type, but is being used as a value`
- [ ] 派生值用 `@Computed` getter（V1 无等价物）
- [ ] 弹窗/Toast 用 **UIContext 实例形** `this.getUIContext().showAlertDialog(...)` / `this.getUIContext().getPromptAction().showToast(...)`（全局 `AlertDialog.show` / `promptAction.showToast` 自 API18 已 deprecated）
- [ ] 长列表项考虑 `@ReusableV2 + @ComponentV2`（不要 V1 `@Reusable`）
- [ ] 同一文件不混用 V1/V2 装饰器
- [ ] **多文件相对 import**：host 入口页（在 ets 根）用 `./Name`（同级）/ `./dir/Name`（子目录）匹配实际文件布局，**绝不 `../`**（host 在 ets 根、`../` 越界 → `Cannot find module`）
- [ ] `@ReusableV2` 的 **`aboutToReuse()` 无入参**：复用时框架自动重置（@Param 用父传入值、@Local 用初始值）——**绝不在 `aboutToReuse` 内给 @Param 赋值**（@Param 只读 → `Cannot assign to read-only property`；V1 旧式 `aboutToReuse(params){ this.x = params.x }` 在 V2 必报错）。要改父态走 @Event 回调

---

## References

### V2 主参考（推荐，本项目实际使用）

- `references/v2-list-detail-pattern.md` — 列表+详情页完整方案（V2，含分页、缓存）
- `references/v2-search-pattern.md` — 搜索功能完整方案（V2，搜索框+历史+结果+持久化）
- `references/v2-auth-pattern.md` — 登录/用户状态管理完整方案（V2 @ObservedV2 AuthState + AppStorageV2）
- `references/v2-performance-patterns.md` — 性能优化模式（V2 LazyForEach + @ReusableV2 + @Computed + cachedCount）
- `references/v2-form-and-sheet-patterns.md` — 带校验表单页 + 底部 Sheet/模态 业务模式
- `references/v2-media-app-pattern.md` — 媒体应用模式（V2 播放器、下载、Feed 链）

### V1 历史参考（仅老项目兼容查阅）

- `references/list-detail-pattern.md` — V1 列表+详情页
- `references/search-pattern.md` — V1 搜索功能
- `references/auth-pattern.md` — V1 登录/用户状态管理（AppStorage + @StorageLink）
- `references/performance-patterns.md` — V1 性能优化（@Reusable + @Observed + @Track）
- `references/media-app-pattern.md` — V1 媒体应用（@StorageLink 驱动 MiniPlayer/FullPlayer）

> 遇到版本兼容性或其他不确定的 ArkTS 知识点（如属性、语法、权限等），参阅 **arkts-knowledge-verifier** skill
