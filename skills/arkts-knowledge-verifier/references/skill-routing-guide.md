# Skill 路由与编排指南

> 本文件是多 Skill 协作的完整路由参考。任何 skill 都可以读取此文件来获取跨 skill 编排信息。
>
> **装饰器版本**：本项目锁 ArkTS V2，下文 §输出格式示例使用 V2 装饰器（`@ComponentV2 / @Local / @Param / @ObservedV2 / @Trace`）。

---

## 请求分类矩阵

| 用户请求特征 | 入口 Skill | 配合 Skills | 生成顺序 |
|---|---|---|---|
| 完整业务功能（列表详情页、搜索、登录、设置等） | **pattern-library** | data-layer + navigation-builder + component-builder + state-manager | Model → DataSource → State → Navigation → UI → Animation |
| 从零搭建完整应用 | **project-scaffolder** | data-layer + state-manager + navigation-builder + pattern-library + component-builder + animation-builder | 项目结构 → 数据层 → 状态管理 → 导航框架 → 业务页面 → 动画润色 |
| 单个 UI 组件/布局 | **component-builder** | （通常独立） | 直接生成 |
| 单个技术点（装饰器、动画、导航） | 对应专项 skill | （通常独立） | 直接生成 |
| 三方库替代方案查找 | **library-migration** | （通常独立） | 查对照表 → 走决策树 → 输出替换方案 |
| 系统能力（媒体/权限/文件/后台） | **system-capabilities** | （通常独立） | 直接生成 |
| 知识验证/语法检查 | **knowledge-verifier** | （按需读取其他 skill 的 reference） | 查找 → 验证 → 回答 |

---

## 场景路由表

### 列表详情页
- **入口**：pattern-library（模式 1）
- **需要读取**：
  1. `arkts-data-layer/SKILL.md`"数据模型"节 → 生成 Model 类
  2. `arkts-data-layer/references/datasource-patterns.md` → 生成 BasicDataSource
  3. `arkts-navigation-builder/SKILL.md`"NavDestination 页面模板"节 → 生成导航框架
  4. pattern-library 自身的列表详情模板 → 组装完整页面
  5. `arkts-knowledge-verifier/references/arkts-vs-typescript.md` → 验证无幻觉

### 搜索功能
- **入口**：pattern-library（模式 2）
- **需要读取**：
  1. `arkts-data-layer/references/network-service.md` → 网络请求封装
  2. pattern-library 自身的搜索模板 → 组装 SearchView
  3. `arkts-state-manager/SKILL.md` → Preferences 持久化搜索历史

### 下拉刷新加载更多
- **入口**：pattern-library（模式 3）
- **需要读取**：
  1. `arkts-data-layer/references/datasource-patterns.md` → BasicDataSource
  2. `arkts-data-layer/references/network-service.md` → 分页请求
  3. pattern-library 自身的刷新模板

### 登录/用户状态
- **入口**：pattern-library（模式 4）
- **需要读取**：
  1. `arkts-state-manager/references/v2-global-state.md` → AppStorageV2 全局状态（V1 项目可参考 `global-state.md`）
  2. `arkts-data-layer/references/network-service.md` → 登录接口
  3. pattern-library 自身的登录模板

### 设置页面
- **入口**：pattern-library（模式 6）
- **需要读取**：
  1. `arkts-state-manager/references/v2-global-state.md` → PersistenceV2 持久化设置（V1 项目可参考 `global-state.md`）
  2. `arkts-component-builder/references/common-components.md` → Toggle 等组件

### 完整应用搭建
- **入口**：project-scaffolder
- **6 步生成序列**：
  1. project-scaffolder 自身 → 项目结构 + 配置文件
  2. `arkts-data-layer/SKILL.md` → Model + Service + BasicDataSource
  3. `arkts-state-manager/SKILL.md` → 全局状态设计
  4. `arkts-navigation-builder/SKILL.md` → Navigation + Tabs 框架
  5. `arkts-pattern-library/SKILL.md` + `arkts-component-builder/SKILL.md` → 业务页面 UI
  6. `arkts-animation-builder/SKILL.md` → 动画润色（可选）

---

## 判断规则（优先级从高到低）

1. **"从零搭建/新建项目/完整应用"** → project-scaffolder
2. **"完整业务功能"**（列表详情页、搜索、登录、设置等复合需求） → pattern-library
3. **"单个技术点"**（单组件、单动画、单导航、单状态管理） → 对应专项 skill
4. **"验证/检查/这个对不对"** → knowledge-verifier
5. **无法判断** → knowledge-verifier（它的路由决策树会进一步引导）

---

## 输出合并协议

当一次请求涉及多个 skill 的知识时，输出应：

1. **按文件分块标注**：每个生成的文件用 `// === 文件路径 ===` 标注
2. **按依赖顺序排列**：Model → Service → State → Navigation → Page → Animation
3. **必要的导入说明**：每个文件开头标注需要的 import
4. **跨文件引用说明**：标注文件间的引用关系

### 输出格式示例

```
// === model/ArticleModel.ets ===
// 数据模型（参考 arkts-data-layer）
@ObservedV2
export class ArticleModel {
  @Trace title: string = ''
  @Trace summary: string = ''
}

// === service/ArticleService.ets ===
// 网络请求（参考 arkts-data-layer）
export class ArticleService { ... }

// === pages/ListPage.ets ===
// 列表页面（参考 arkts-pattern-library + arkts-navigation-builder）
// 引用：ArticleModel, ArticleService
@Entry
@ComponentV2
struct ListPage {
  @Local articles: ArticleModel[] = []
  // ...
}

// === pages/DetailPage.ets ===
// 详情页面（参考 arkts-navigation-builder）
// 引用：ArticleModel
@ComponentV2
struct DetailPage {
  @Param article: ArticleModel = new ArticleModel()
  // ...
}
```

---

## 注意事项

- 读取其他 skill 的 reference 时，使用 Read 工具读取对应文件路径
- 所有 skill 的文件都在 `arkts-skills/` 目录下
- 每个 skill 的 SKILL.md 是入口，references/ 目录下是详细参考
- 生成代码后，始终用 knowledge-verifier 的检查清单验证
