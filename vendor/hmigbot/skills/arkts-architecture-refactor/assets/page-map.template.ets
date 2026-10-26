/**
 * products/phone/src/main/ets/pages/Index.ets — 壳工程 Navigation 路由根页
 *
 * ⚠️ 致命陷阱（编译期不报错、运行时所有页面空白）：
 *   PageMap @Builder 内**必须** NavDestination() {...} 包裹一层。
 *   直接 `if (name === 'X') { XPage() }` 而无 NavDestination 包裹 → 框架默默忽略 → 全黑屏。
 *
 * 占位规则（生成时由 gen-page-map.py 替换）：
 *   __ROUTE_IMPORTS__         — 从 features/business_*/Index.ets 收集 Page struct 的 import
 *   __INITIAL_PAGE__          — 入口页路由名（默认 SplashPage；项目无 splash 时用首业务 page）
 *   __ROUTE_BRANCHES__        — `if/else if` 分支链
 *
 * 与本模板配套的工具：
 *   - references/04-state-routing.md §R6.4-CRITICAL（反模式说明）
 *   - assets/gen-page-map.py（自动从 business_*/Index.ets 生成）
 *   - SKILL.md Phase 4 ⑤ 运行时冒烟（首屏非空校验）
 */

import { RouterUtils, StackEnum } from 'lib_common';
__ROUTE_IMPORTS__

@Entry
@ComponentV2
struct Index {
  @Local pageStack: NavPathStack = RouterUtils.createStack(StackEnum.Main, true);

  aboutToAppear(): void {
    // 入口页推入；如该路由名不在 PageMap 注册列表，跳转后会黑屏
    this.pageStack.pushPathByName('__INITIAL_PAGE__', null);
  }

  build() {
    Navigation(this.pageStack)
      .navDestination(this.PageMap)
      .hideTitleBar(true)
      .hideToolBar(true)
      .mode(NavigationMode.Stack)
  }

  /**
   * 路由表 — name → page struct 映射。
   *
   * ⚠️ 必须用 NavDestination() {...} 包一层！
   * 直接 `XPage()` 不带 NavDestination 包裹 = 框架不渲染 = 运行时空白页。
   */
  @Builder
  PageMap(name: string) {
    NavDestination() {
__ROUTE_BRANCHES__
    }
    .hideTitleBar(true)
    .hideToolBar(true)
    .mode(NavDestinationMode.STANDARD)
  }
}
