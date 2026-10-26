<!-- when: a2h-execute 入口页 Navigation 外壳 / main_pages.json / EntryAbility loadContent / Hello World 模板剔除 相关问题时加载 -->
<!-- topics: 入口页, 宿主, Navigation 外壳, main_pages.json, EntryAbility loadContent, DevEco Hello World 剔除, host_page.py, @Provider navPathStack -->

# 宿主入口页：host_page.py 单写

> 宿主入口页**只由脚本写**：`python3 $SKILLS/a2h-execute/scripts/host_page.py --project . [--blueprint spec/blueprint] [--module entry] --json`。
> A 阶段同期清单第 3 项跑一次；execute infra 波尾 `reduce:host-page` 幂等再跑；domains 及之后各波尾 `reduce:pagemap`（sync_pagemap）
> 写模式先调它机械修一遍再对账。**主会话与代理禁手写宿主**——AIPPT_930_token2（2026-09-21）主会话手拼外壳漏了
> `@Provider('navPathStack')`，59 个页面 `@Consumer('navPathStack') navPathStack = new NavPathStack()` 各自拿到私有空栈，
> 全部导航静默失效，而静态接线闸报 38/38 全接通。

## 背景

页面导航采用 `Navigation + NavPathStack`（API 12+ 标准，`@ohos.router` 已废弃）。`main_pages.json` 只注册**宿主**一项；其余页面是
`NavDestination` 子页面，由 `PageMapGen.ets` 的 `AppPageMap` 路由表分发（`sync_pagemap.py` 生成），**不进** `main_pages.json`。

## 脚本做什么（机械，幂等）

1. **宿主解析**：`<module>/src/main/resources/base/profile/main_pages.json` `src[0]`（如 `pages/MainPage` → `pages/MainPage.ets`）；
   缺失/空 → `pages/Index` 并回写 main_pages.json。DevEco 骨架的入口页名不定（Index / MainPage），一律以 main_pages.json 为准。
2. **启动路由**：`spec/journeys.json#start[0]`（回退 `spec/toolkit-fact-tree.json#app.launcher_short`）经 `spec/blueprint/page-names.json`
   （所有 domains + overrides）映射成鸿蒙页名；路由名就是页名（sync_pagemap 按 `<页名>Builder` 登记）。
3. **宿主三态**：
   - 缺失 / DevEco 模板（无 `Navigation(`；`Hello World` / `@State message` / `@Component`）→ **整文件生成**：`@Entry @ComponentV2 struct <宿主名>`、
     `@Provider('navPathStack') navPathStack: NavPathStack = new NavPathStack()`、`@Builder pageMap` 占位、
     `Navigation(this.navPathStack){…}.navDestination(AppPageMap).hideTitleBar(true).mode(NavigationMode.Stack)`、
     `onAppear` 里栈空则 `pushPathByName('<启动页>', <参数>)`；
   - 业务宿主（已有 `Navigation(`）→ 只做机械修补：Navigation 绑定的栈字段补 `@Provider('navPathStack')`（已有 Provider 字段而 Navigation 绑别的字段 → 改绑）；
     缺 `.navDestination(` → 追加 `.navDestination(AppPageMap)` + import；全文件无入栈 → 追加/插入 `onAppear` 启动入栈块；标记块外一行不动。
4. **启动入栈参数**：启动页 builder 首参类型是工程内零参可构造的 `export class` → `new X()`（自动 import）；builder 尚不存在（infra 期）→ `undefined`，
   domains 波尾 sync_pagemap 重刷；首参是 interface / 必填参 class → `undefined` 并记 violation（页面 owner 须让 builder 接受 undefined）。
5. **装机面对齐**：`EntryAbility.loadContent('pages/<宿主>')` 机械改写；`main_pages.json` 里无对应文件/模板残留的条目机械移除，
   业务页多项**报不删**（violation）；非宿主的 `pages/Index.ets` Hello World 模板残留直接删除；`PageMapGen.ets` 缺失时写空 `AppPageMap`（宿主先能编译）。
6. **报告** `spec/reports/host-page.json`：`{ok, host, host_state, launch_route, launch_param, written, removed, notes, violations}`；
   `--check-only` 只校不写（render_static_gate 走这条：凡写模式能机械修的在 check-only 下记 violation 指回 host_page.py）。

标记块 `// <host_page:imports:begin/end>`、`// <host_page:launch:begin/end>` 归脚本维护；块外可按业务扩展（如 `aboutToAppear` 绑 UIContext）。

## 只剩下这些要人/代理处理（无安全机械变换）

- `launch_route: null`：journeys.json#start 缺或 page-names.json 无映射——补齐 spec 后重跑；宿主先带 TODO 块落地。
- 启动页 builder 首参不可零参构造——页面 owner 改 builder 签名或让页面接受 undefined。
- 业务宿主没有 `Navigation(` 外壳——脚本不覆盖业务文件；把内容迁到 NavDestination 页后删除再跑。
- `main_pages.json` 里登记了业务页——把该页改成 NavDestination（同文件导出 `<页名>Builder`）后从 src 移除。

## 校验面

- `sync_pagemap.py`（各实现波尾）：`@Provider/@Consumer` 对账——`navPathStack` 必须由宿主 Provider、其它 key 有 Consumer 零 Provider → `provider-missing` 判 FAIL；
  宿主启动入栈路由必须已注册；`shadow_nav_providers` 列出页面内自建的 `@Provider('navPathStack')`（遮蔽宿主栈，只报）。
- `render_static_gate.py`（closeout，`device_smoke=off`）：`host_page --check-only` + `sync_pagemap --check-only` + `static_runtime_lint`。
