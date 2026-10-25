> **iOS 源输入**：读取 Swift/Objective-C、SwiftUI/UIKit、Xcode 工程及原生资源；实际源构建与设备观测依赖可用的源平台环境。鸿蒙侧构建和验收保持原流程。源侧操作详见 `a2h-spec/references/native-input.md`。

# iOS → ArkTS 目录映射与迁移骨架

> 从 iOS 项目迁移到 ArkTS 时的标准目录映射表和骨架搭建 checklist。
>
> **ArkTS V2 lock**：本文档代码示例与映射表使用 V2 装饰器（`@ComponentV2 / @Local / @Param / @ObservedV2 / @Trace / AppStorageV2`）。V1 老项目（`@Component / @State / @Prop / @Link / @StorageLink`）兼容查阅请见 `arkts-state-manager/references/state-decorators.md`。

---

## 目录映射表

```
iOS                              →  ArkTS
实际 Swift/ObjC model 源文件      →  entry/src/main/ets/models/
实际 Core Data/SwiftData/SQLite 源文件   →  entry/src/main/ets/database/
实际持久层协议/实现  →  entry/src/main/ets/database/  (DAO 合并)
实际可导航原生页面  →  entry/src/main/ets/pages/
实际嵌入原生子页   →  entry/src/main/ets/components/
实际列表 data source / View 组合    →  entry/src/main/ets/components/ (合并到组件)
实际共享工具     →  entry/src/main/ets/helpers/
实际服务与后台任务    →  entry/src/main/ets/playback/ 或 workers/
实际 Asset Catalog/Bundle/本地化资源                    →  entry/src/main/resources/
(新增)                                →  entry/src/main/ets/viewmodels/
(新增)                                →  entry/src/main/ets/datasource/
(新增)                                →  entry/src/main/ets/common/
```

### 映射规则说明

| iOS 概念 | ArkTS 概念（V2，本项目默认） | 映射说明 |
|-------------|-----------|---------|
| UIViewController / 路由 SwiftUIView | `@Entry @ComponentV2` struct（Page） | 每个独立导航页 → 一个 Page 文件（V1 老项目用 `@Entry @Component`） |
| 嵌入 SwiftUIView / child controller | `@ComponentV2` struct | 可复用组件（V1 老项目用 `@Component`） |
| UITableView/UICollectionView data source 与 View | Repeat / ForEach / LazyForEach + @Builder | Adapter 逻辑合并到组件中（V2 推荐 `Repeat`） |
| ViewModel | `@ObservedV2` class + `@Trace` 字段 + `@Local` 持有 | ArkTS 无 ViewModel 感知生命周期；V2 用 `@ObservedV2 + @Trace` 暴露可观察字段 |
| Core Data/SwiftData/SQLite 模型 | 手写 class + CREATE TABLE SQL | 无 ORM |
| 原生 repository / 查询封装 | 手写 DAO class + querySql() | 无注解 |
| UserDefaults | Preferences from @kit.ArkData | 异步 API |
| 真实导航与传参 | NavPathStack.pushPathByName(name, param) | 参数在 onReady 获取 |
| Info.plist / entitlements / App/Scene | module.json5 | 权限、Ability 声明 |
| project.pbxproj / Package.swift / 锁定依赖 | oh-package.json5 + build-profile.json5 | 依赖和构建配置 |
| SwiftUI/UIKit/IB 源 UI | build() 声明式 UI | 无 xml 布局 |

---

## 迁移骨架搭建 Checklist

### Phase 2 骨架搭建（按顺序执行）

- [ ] DevEco Studio 新建空项目
- [ ] 按映射表创建所有子目录
- [ ] 配置 `module.json5`（权限、backgroundModes）
- [ ] 配置 `oh-package.json5`（三方库依赖）
- [ ] 创建 `common/GlobalState.ets`（单例初始化）
- [ ] 创建 `common/AppRouter.ets`（路由名常量）
- [ ] 创建 `common/EventBus.ets`（事件总线）
- [ ] 创建 `entryability/EntryAbility.ets`（应用入口）
- [ ] 创建 AGENTS.md（项目规则）
- [ ] `hvigor build` 编译通过

### 基础设施文件清单

| 文件 | 用途 | 依赖 |
|------|------|------|
| `common/GlobalState.ets` | 单例，初始化 Config/Database，同步 AppStorage | Config, Database |
| `common/AppRouter.ets` | 路由名常量 + 页面参数类型定义 | — |
| `common/EventBus.ets` | 发布-订阅事件总线 | — |
| `common/Constants.ets` | 全局常量定义 | — |
| `helpers/Logger.ets` | hilog 封装 | — |
| `helpers/PermissionHelper.ets` | 权限请求封装 | — |
| `helpers/FileUtils.ets` | 文件操作封装 | — |
| `network/HttpClient.ets` | HTTP 请求封装 | — |

---

## GlobalState 初始化模式（V2）

```typescript
import { AppStorageV2 } from '@kit.ArkUI'

@ObservedV2
export class AppConfigModel {
  @Trace viewType: string = 'list'
  @Trace sortOrder: string = 'asc'
}

export class GlobalState {
  private static initialized: boolean = false

  static async init(context: Context): Promise<void> {
    if (GlobalState.initialized) return
    const config = Config.getInstance()
    await config.init(context)
    const db = AppDatabase.getInstance()
    await db.init(context)
    // 把 Config 的快照写入共享 @ObservedV2 实例（一次写入，所有 connect 该 key 的页面同步刷新）
    const cfg = AppStorageV2.connect(AppConfigModel, 'appConfig', () => new AppConfigModel())!
    cfg.viewType = config.viewType
    cfg.sortOrder = config.sortOrder
    GlobalState.initialized = true
  }
}
```

**关键**：`GlobalState.init()` 必须在任何 Page 创建前执行。在 `Index.ets` 的 `aboutToAppear()` 中调用，并用 `@Local isInitialized` 控制 UI 显示（V1 老项目用 `@State isInitialized`）。
