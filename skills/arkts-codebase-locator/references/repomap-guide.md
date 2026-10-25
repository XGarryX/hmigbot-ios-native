# 基于 Repomap 的功能定位方法

## 概述

Repomap 是对代码库结构的元数据摘要，包含文件路径、类名、函数签名等信息。本文档说明如何利用 repomap 快速定位 HarmonyOS ArkTS 应用中的功能实现。

## Repomap 结构

典型 repomap.md 包含：
- 模块列表（HAP/HSP）
- 每个模块的关键文件路径
- 导出的类、组件、函数摘要
- 跨模块依赖关系

## 使用方法

### 步骤一：读取 Repomap

```
读取项目根目录下的 repomap.md（或 .repomap）
```

### 步骤二：关键词匹配

在 repomap 中搜索与用户问题相关的：
- 类名（如 `LoginPage`、`UserService`）
- 文件名（如 `login.ets`、`user.ets`）
- 模块名（如 `feature_user`、`common`）

### 步骤三：路径提取

从匹配结果提取完整文件路径，优先选择：
1. 命名最精确匹配的文件
2. 层级最浅的文件（避免深层嵌套的工具类）
3. 非测试文件（排除 `test/`、`mock/` 路径）

### 步骤四：验证与精化

- 必要时打开文件确认内容
- 定位到具体函数或组件
- 结合 question-types.md 确认问题类型匹配

## 常见模式（V1+V2 兼容）

| 用户意图 | Repomap 搜索关键词 | 典型路径 |
|---------|------------------|---------|
| 登录功能 | Login、Auth、login | pages/LoginPage.ets |
| 列表展示 | List、Feed、Item、Repeat | pages/FeedPage.ets |
| 数据存储 | DAO、RDB、Store、RdbStore | model/dao/ |
| 网络请求 | Service、Api、Http | services/ |
| 全局状态 | AppStorage、AppStorageV2、State、Local、Observed、ObservedV2 | viewmodel/ 或 stores/ |
| 持久化 | PersistentStorage、PersistenceV2 | model/persist/ 或 viewmodel/ |
| 跨层级注入 | Provide、Provider、Consume、Consumer | viewmodel/ |
| 状态监听 | Watch、Monitor、Computed | viewmodel/ |

## 注意事项

- Repomap 可能不包含所有文件，缺失时需人工目录浏览
- 大型项目 repomap 较长，优先搜索模块级入口
- 组件类文件通常以 `Component` 或 `View` 结尾
- **V1+V2 兼容**：搜状态/存储相关时同时覆盖 V1 与 V2 装饰器名（如 `@State|@Local`、`@StorageLink|AppStorageV2`），避免漏检

## V1 → V2 装饰器速查（搜索时同时考虑两边）

| V1 | V2 |
|---|---|
| `@Component` | `@ComponentV2` |
| `@State` | `@Local` |
| `@Prop` | `@Param`（只读加 `@Once`） |
| `@Link` | `@Param + @Event` 回调 |
| `@Provide` / `@Consume` | `@Provider()` / `@Consumer()` |
| `@Observed` + `@ObjectLink` | `@ObservedV2` + 类属性 `@Trace`（无 `@ObjectLink`） |
| `@StorageLink` / `@StorageProp` | `AppStorageV2.connect(...)` |
| `@LocalStorageLink` / `@LocalStorageProp` | `@Provider()/@Consumer()`（无 LocalStorageV2） |
| `PersistentStorage.persistProp` | `PersistenceV2.globalConnect(...)` |
| `@Watch` | `@Monitor` + `IMonitor` |
