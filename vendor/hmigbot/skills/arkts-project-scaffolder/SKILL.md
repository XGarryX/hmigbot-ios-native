---
name: arkts-project-scaffolder
description: 生成 ArkTS/HarmonyOS 项目结构和配置文件（V2 装饰器优先，API 12+）。当用户需要创建新项目、设计多模块架构（commons/features/products）、编写 module.json5 / build-profile.json5 / oh-package.json5 / app.json5、创建 EntryAbility（含 AppStorageV2 / PersistenceV2 全局状态预热）、配置权限、或搭建任何 HarmonyOS 项目骨架时，务必触发此 skill；说"从零搭建完整应用"时也优先触发，它会引导调用其他 skill。即使只说"新建个项目""项目怎么搭建"也应触发。不适用于状态管理深度用法（见 arkts-state-manager）。
metadata:
  type: domain
  domain: engineering
  tags:
  - scaffolding
  - project-structure
  - config
---
# ArkTS Project Scaffolder — 项目脚手架（V2 优先）

## API 版本与项目策略

本 skill 的配置与代码模板基于 **API 12+（HarmonyOS 5.0.0+）和 ArkTS V2 装饰器体系**。

> **项目锁 V2**：本 skill 生成的所有页面 / 组件 / EntryAbility 模板使用 V2 装饰器（`@ComponentV2 / @Local / @Param / @Once / @Event / @ObservedV2 / @Trace / @Provider / @Consumer / @Monitor / @Computed / AppStorageV2 / PersistenceV2`）。HarmonyOS 项目结构本身（`build-profile.json5 / module.json5 / app.json5 / oh-package.json5 / EntryAbility.ets`）在 V1/V2 下完全相同，无需变化；变化的是页面/组件代码内的状态装饰器。
>
> 阅读老 V1 项目（`@Component / @State / @Prop / @Link / @StorageLink` 等）时，参阅 `arkts-state-manager/references/state-decorators.md`（V1 历史文档）。

项目配置中的版本字段：

- `build-profile.json5` 中的 `compileSdkVersion` 和 `compatibleSdkVersion`：编译和兼容的 API 级别
  - 数字格式：`12`（推荐）
  - 字符串格式：`"5.0.0(12)"`（部分 DevEco Studio 版本使用，括号内为 API 级别）
- `app.json5` 中的 `minAPIVersion` 和 `targetAPIVersion`：与 `compatibleSdkVersion` / `compileSdkVersion` 对应
- 所有模板使用 `@kit.*` 导入（不要用 `@ohos.*`）
- EntryAbility 使用 `import { ... } from '@kit.AbilityKit'`
- V2 装饰器（`@ComponentV2 / AppStorageV2 / PersistenceV2 / ...`）要求 **API 12+**；低于 12 时回落 V1 写法或先升 SDK

生成配置文件时，根据用户的目标版本设置正确的 SDK 版本号。遇到版本兼容性或其他不确定的 ArkTS 知识点（如属性、语法、权限等），参阅 arkts-knowledge-verifier skill；状态装饰器选择见 arkts-state-manager skill。

---

## 项目复杂度决策

```
你的项目有多复杂？
│
├─ 简单应用（<5 页面，单人开发）
│   └─ 单模块项目
│       一个 entry 模块搞定一切
│
├─ 中等应用（5-15 页面，小团队）
│   └─ 单模块 + 功能目录划分
│       entry 模块内按 features/ 组织
│
└─ 大型应用（>15 页面，多团队协作）
    └─ 多模块项目
        commons/ + features/ + products/
        每个模块独立编译、独立测试
```

---

## 单模块项目结构

适合绝大多数场景，从这里开始：

```
MyApp/
├── AppScope/
│   ├── app.json5                # 应用级配置
│   └── resources/               # 应用级资源
├── entry/                       # 主模块
│   ├── src/main/
│   │   ├── ets/
│   │   │   ├── entryability/
│   │   │   │   └── EntryAbility.ets    # 应用入口
│   │   │   ├── pages/
│   │   │   │   ├── Index.ets           # 首页（@Entry）
│   │   │   │   ├── DetailPage.ets
│   │   │   │   └── SettingsPage.ets
│   │   │   ├── components/             # 公共组件
│   │   │   │   ├── CommonHeader.ets
│   │   │   │   └── LoadingView.ets
│   │   │   ├── model/                  # 数据模型
│   │   │   │   └── ArticleModel.ets
│   │   │   ├── service/                # 网络服务
│   │   │   │   └── ApiService.ets
│   │   │   ├── common/                 # 工具/常量
│   │   │   │   ├── Constants.ets
│   │   │   │   └── PreferencesUtil.ets
│   │   │   └── viewmodel/             # 视图模型（可选）
│   │   ├── resources/
│   │   │   ├── base/
│   │   │   │   ├── element/
│   │   │   │   │   ├── string.json
│   │   │   │   │   └── color.json
│   │   │   │   ├── media/              # 图片资源
│   │   │   │   └── profile/
│   │   │   │       ├── main_pages.json # 页面路由注册
│   │   │   │       └── backup_rules.json
│   │   │   ├── en_US/                  # 英文资源
│   │   │   └── zh_CN/                  # 中文资源
│   │   └── module.json5               # 模块配置
│   ├── oh-package.json5               # 依赖管理
│   └── hvigorfile.ts                  # 构建脚本
├── build-profile.json5                # 构建配置
├── oh-package.json5                   # 项目级依赖
└── hvigorfile.ts                      # 项目级构建脚本
```

---

## 配置文件模板 & EntryAbility（详见 references）

> **MUST**：生成配置/入口前先读对应 reference——

> - module.json5 / build-profile.json5 / oh-package.json5 / app.json5 完整模板 → `references/config-reference.md`
> - 单模块项目骨架 + EntryAbility.ets（含 AppStorageV2 / PersistenceV2 预热）→ `references/single-module-template.md`
> - 多模块项目骨架 → `references/multi-module-template.md`

---

## 多模块项目结构

当项目达到一定规模时，拆分模块有助于团队协作和编译效率：

```
MyApp/
├── AppScope/
│   └── app.json5
├── commons/                     # 公共模块（工具、基础组件）
│   ├── common/                  # 通用工具
│   │   ├── src/main/ets/
│   │   │   ├── utils/
│   │   │   ├── constants/
│   │   │   └── Index.ets       # barrel export
│   │   ├── oh-package.json5
│   │   └── module.json5        # type: "har"
│   └── uicomponents/           # UI 组件库
│       ├── src/main/ets/
│       │   ├── components/
│       │   └── Index.ets
│       └── module.json5        # type: "har"
├── features/                    # 功能模块
│   ├── discover/
│   │   ├── src/main/ets/
│   │   │   ├── views/
│   │   │   ├── model/
│   │   │   ├── service/
│   │   │   └── Index.ets
│   │   └── module.json5        # type: "har"
│   ├── mine/
│   └── settings/
├── products/                    # 产品模块（entry）
│   └── phone/
│       ├── src/main/ets/
│       │   ├── entryability/
│       │   └── pages/
│       └── module.json5        # type: "entry"
└── build-profile.json5         # 注册所有模块
```

### Index.ets barrel export 模式

每个模块的 `Index.ets` 统一导出公共接口：

```typescript
// features/discover/Index.ets
export { DiscoverView } from './views/DiscoverView'
export { DiscoverModel } from './model/DiscoverModel'
export { ArticleModel } from './model/ArticleModel'
```

### 模块间引用

```json5
// products/phone/oh-package.json5
{
  "dependencies": {
    "@commons/common": "file:../../commons/common",
    "@features/discover": "file:../../features/discover"
  }
}
```

```typescript
// products/phone/src/main/ets/pages/Index.ets
import { DiscoverView } from '@features/discover'
import { Constants } from '@commons/common'
```

---

## HAR 模块配置

功能模块使用 HAR（Harmony Archive）类型：

```json5
// features/discover/module.json5
{
  "module": {
    "name": "discover",
    "type": "har",           // HAR 类型，不是 entry
    "deviceTypes": ["phone", "tablet"]
  }
}
```

---

## 常见错误 vs 正确写法

### 错误 1：把所有页面塞进 main_pages.json（旧 router 写法）

```json
// 错误 — router 时代写法：逐页登记到 main_pages.json
{ "src": ["pages/Index", "pages/DetailPage", "pages/SettingsPage"] }

// 正确 — Navigation 模型：main_pages.json 只放入口页
{ "src": ["pages/Index"] }
// DetailPage / SettingsPage 等是 NavDestination 子页面，不进 main_pages.json：
// 单模块可用入口页 @Builder pageMap；跨模块/动态/推荐用系统路由表
// （module.json5 "routerMap":"$profile:route_map" + route_map.json，见 arkts-navigation-builder）
```

### 错误 2：bundleName 格式不规范

```json5
// 错误
"bundleName": "myapp"              // 太短，不符合规范

// 正确 — 反向域名格式
"bundleName": "com.example.myapp"
```

### 错误 3：多模块依赖路径错误

```json5
// 错误 — 路径不对
"dependencies": {
  "@commons/common": "file:../commons/common"  // 少了一级
}

// 正确 — 相对路径从当前 oh-package.json5 出发
"dependencies": {
  "@commons/common": "file:../../commons/common"
}
```

---

## 生成检查清单

- [ ] app.json5 有正确的 bundleName（反向域名格式）
- [ ] module.json5 type 正确（entry / feature / har / shared(HSP)，见 references/config-reference.md §模块类型选型）
- [ ] main_pages.json 只放入口页；NavDestination 子页面用入口页 pageMap（单模块）或系统路由表 route_map（跨模块/推荐，见 arkts-navigation-builder）
- [ ] 所需权限配置在 requestPermissions
- [ ] EntryAbility 加载了正确的页面
- [ ] V2 全局状态在 EntryAbility.onCreate 中通过 `AppStorageV2.connect(Cls, key, () => new Cls())` 预热（V1 老项目用 `AppStorage.setOrCreate`）
- [ ] 所有页面/组件 struct 用 `@ComponentV2`，状态用 `@Local / @Param / @Event`，类用 `@ObservedV2 + @Trace`，不混用 V1 装饰器
- [ ] 多模块项目的 build-profile.json5 注册了所有模块
- [ ] 模块间 oh-package.json5 依赖路径正确

---

## 完整项目编排指南

当用户要求"从零搭建完整应用"时，本 skill 不仅生成项目骨架，还应引导按以下 6 步序列，读取其他 skill 的内容来生成完整项目代码。

### 6 步生成序列

| 步骤 | 内容 | 读取来源 |
|------|------|---------|
| **Step 1: 项目结构** | 配置文件骨架、EntryAbility、模块结构 | 本 skill 自身模板 |
| **Step 2: 数据层** | Model 类 + Service 网络请求 + BasicDataSource | 读取 `arkts-data-layer/SKILL.md`"数据模型"和"网络请求"节 |
| **Step 3: 状态管理** | 全局状态设计（`AppStorageV2.connect` + `@ObservedV2` 模型类、key 常量；老项目可读 V1 `AppStorage.setOrCreate / @StorageLink` 章节） | 读取 `arkts-state-manager/SKILL.md`"AppStorageV2 / @ObservedV2"节 |
| **Step 4: 导航框架** | Navigation + Tabs 主框架、页面路由映射 | 读取 `arkts-navigation-builder/SKILL.md`"Tabs + Navigation 组合模式"节 |
| **Step 5: 业务页面** | 各功能页面 UI（列表、详情、搜索等） | 读取 `arkts-pattern-library/SKILL.md` 选择对应模式 + `arkts-component-builder/SKILL.md` UI 组件 |
| **Step 6: 动画润色** | 转场动画、交互反馈（可选） | 读取 `arkts-animation-builder/SKILL.md`"animateTo"和"transition"节 |

### 输出格式

按文件分块输出，每个文件标注路径：`// === 文件路径 ===`。按依赖顺序排列（配置 → Model → Service → State → Navigation → Page）。

> 完整路由矩阵见 `arkts-knowledge-verifier/references/skill-routing-guide.md`

---

## References

- `references/single-module-template.md` — 最小可运行项目的所有文件完整内容
- `references/multi-module-template.md` — 多模块架构的完整文件和配置
- `references/config-reference.md` — 所有配置文件的字段详细说明（含 SDK 版本格式）
- `references/audio-app-scaffold.md` — 音频应用脚手架：module.json5 模板、GlobalState 清单、层依赖、96 文件清单
- 遇到版本兼容性或其他不确定的 ArkTS 知识点（如属性、语法、权限等），参阅 **arkts-knowledge-verifier** skill
