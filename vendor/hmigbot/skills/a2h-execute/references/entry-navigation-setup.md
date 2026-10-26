<!-- when: a2h-execute SKILL.md §3a-bis 入口页 Navigation 装配/注册 + Hello World 模板剔除执行时加载 -->
<!-- topics: 入口页, Navigation 外壳, main_pages.json, pageMap 路由表, EntryAbility loadContent, DevEco Hello World 剔除, HARD-GATE -->

# 入口页 Navigation 装配 + 注册 + Hello World 模板剔除

> a2h-execute §3a-bis 的完整执行规范。**触发时机**：Stage 1 **全部 Batch 完成后**（§3d 收口第一步），一次性入口配置（之后不再执行）。
> **HARD-GATE**：第 2 部分（DevEco Hello World 模板剔除）为 HARD-GATE，必须执行；编译验证并入 §3d single-pass，不单独派发。

## 背景

本项目页面导航采用 `Navigation + NavPathStack`（API 12+ 标准，`@ohos.router` 已废弃）。`main_pages.json` 只注册**入口页**一项；其余页面是 `NavDestination` 子页面，由入口页 `pageMap` 路由表分发，**不进** `main_pages.json`。

## 1. 入口页 Navigation 装配 + 注册

Stage 1 全部 Batch 完成后（§3d 收口第一步），建立入口配置：

1. 读取 `entry/src/main/resources/base/profile/main_pages.json`
2. 将 Launcher Activity 对应的 ArkTS 页面（入口页）加入 `"src"` 数组，并**删除 `"pages/Index"` 条目**（DevEco 默认模板，无业务价值；见 §2 配套清理）
3. **`"src"` 数组最终只保留入口页一项**——NavDestination 子页面通过入口页 `pageMap` 路由，**不在 `main_pages.json` 逐页登记**（这是 Navigation 模型与旧 router 模型的关键差异）
4. **同步修改 EntryAbility.ets 的 `loadContent` 调用**：
   - 读取 `entry/src/main/ets/entryability/EntryAbility.ets`
   - 将 `windowStage.loadContent('pages/Index', ...)` 改为 `windowStage.loadContent('pages/{MainPage}', ...)`（`{MainPage}` 为入口页文件名）
   - 必须与 main_pages.json 首项保持一致，否则运行时仍会加载默认 Hello World 页面
5. **入口页 Navigation 外壳装配**：将入口页改造为 `Navigation` 容器形态——加 `@Provider('navPathStack') navPathStack: NavPathStack = new NavPathStack()`，页面内容包进 `Navigation(this.navPathStack){ ... }.navDestination(this.pageMap).mode(NavigationMode.Stack)`，并补 `pageMap` `@Builder` 路由表。完整模板见 [`arkts-navigation-builder`](../../arkts-navigation-builder/SKILL.md) 方案 1「标准入口模板」。
6. **pageMap 路由表生成**：入口页 `pageMap` 的 if-else 路由表**从 `spec/baseline/ui-manifest.md` 全量页面清单自动生成**（规则见 arkts-navigation-builder「pageMap 自动生成规则（迁移项目专用）」），每个“ArkTS 产出”页面一个 if 分支、不遗漏。**定稿时机：Stage 1 全部 Batch 转换完成后**——届时所有 NavDestination 页面 struct 均已存在，`pageMap` 引用不会编译失败。

## 2. DevEco Hello World 模板剔除（HARD-GATE）

§1 入口注册完成后，**强制执行**：

1. 检查 `entry/src/main/ets/pages/Index.ets` 是否存在
2. 若存在 → grep 其内容，命中以下任一特征即视为 **DevEco 默认模板**：
   - 含 `@Component` 装饰器（项目锁 V2 时本应不出现）
   - 含 `@State message: string = 'Hello World'`
   - 文件行数 ≤ 30 且仅含一个 `build()` 块
3. 命中 → 执行**三联清理**：
   - **删除** `entry/src/main/ets/pages/Index.ets`
   - **从** `main_pages.json` 的 `"src"` 数组**移除** `"pages/Index"`（与 §1 步骤 2 配套）
   - **确认** `EntryAbility.ets` 的 `loadContent` 不指向 `'pages/Index'`（应已在 §1 改向新主页面，若未改 → 报错）
4. 未命中（Index.ets 已被改成业务页或已被删）→ 跳过，记录日志 `"Index.ets 已非默认模板，跳过清理"`
5. 清理无破坏由紧随的 §3d single-pass 编译验证（STAGE_HINT=stage-1-close），**不单独派发**

清理后输出日志：删除 `pages/Index.ets` / `main_pages.json` 移除 `"pages/Index"` / EntryAbility 切换到 `pages/{MainPage}`。