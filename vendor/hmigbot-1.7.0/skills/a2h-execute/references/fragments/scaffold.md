# scaffold — 项目结构决策

## 单/多模块决策
- 简单应用（<5 页面，单人）→ 单模块：一个 entry 搞定；
- 中等应用（5-15 页面，小团队）→ 单模块 + entry 内 features/ 目录划分；
- 大型应用（>15 页面，多团队）→ 多模块：`commons/`(har) + `features/`(har) + `products/`(entry)；各模块 `Index.ets` barrel export，跨模块引用走 oh-package.json5 `file:` 相对路径依赖。

## 3 个常见配置错误
1. 禁止把所有页面塞 main_pages.json（旧 router 写法）→ 只放入口页；NavDestination 子页走入口页 pageMap（单模块）或系统路由表 `routerMap: $profile:route_map`（跨模块/动态）；
2. bundleName 必须反向域名格式 `com.example.myapp`，禁止裸短名 `myapp`；
3. 多模块依赖路径必须从当前 oh-package.json5 出发：`"@commons/common": "file:../../commons/common"`（少写一级 `../` 是高频错）。

<!-- source: arkts-project-scaffolder/SKILL.md:L34-54,L203-243 -->
