# 标准化功能定位工作流程

## 概述

本文档描述 arkts-codebase-locator 技能在响应功能定位请求时的标准化工作流程。

## 主流程

### 阶段一：问题分析

1. 识别问题类型（参见 question-types.md）
2. 提取关键词和语义意图
3. 确定目标：组件、服务、数据层还是配置

### 阶段二：Repomap 初步探索

1. 读取 repomap.md 获取项目整体结构
2. 通过模块列表缩小候选范围
3. 识别相关 HAP/HSP 模块

### 阶段三：目录级导航

1. 按项目结构规范（参见 project-structure.md）定位目录
2. 优先检查约定路径：
   - 页面：`src/main/ets/pages/`
   - 组件：`src/main/ets/components/`
   - 服务：`src/main/ets/services/`
   - 模型：`src/main/ets/model/`

### 阶段四：文件级精确定位

1. 根据文件命名规范匹配目标文件
2. 必要时读取文件确认内容
3. 返回精确路径和关键代码位置

## 决策树

```
用户问题
  ├─ 是否涉及 UI/页面？ → pages/ 或 components/（找 @Component 或 @ComponentV2）
  ├─ 是否涉及数据/状态？ → model/ 或 viewmodel/
  │     V1 找 @State/@Prop/@Link/@Observed/@StorageLink；
  │     V2 找 @Local/@Param/@Event/@ObservedV2/@Trace/AppStorageV2/PersistenceV2
  ├─ 是否涉及网络/IO？ → services/ 或 data/
  ├─ 是否涉及配置？ → 项目根或 resources/
  └─ 是否涉及导航？ → router 配置或 NavDestination
```

## V1+V2 兼容 grep 速查

| 关注点 | V1+V2 兼容 grep 模式 |
|---|---|
| struct 定义 | `@Component(V2)?\b` |
| 组件内状态 | `@State\|@Local` |
| 父→子单向 | `@Prop\|@Param` |
| 父↔子双向 | `@Link\|@Event` |
| 跨层级 | `@Provide(r)?\|@Consume(r)?` |
| 可观察类 | `@Observed(V2)?\b` |
| 类属性级 | `@ObjectLink\|@Trace` |
| 全局存储 | `@StorageLink\|@StorageProp\|AppStorageV2` |
| 本地存储 | `@LocalStorageLink\|@LocalStorageProp` |
| 持久化 | `PersistentStorage\|PersistenceV2` |
| 监听变化 | `@Watch\|@Monitor` |
| 派生（V2 新增） | `@Computed` |

## 输出规范

定位结果需包含：
- 文件相对路径（相对于项目根）
- 关键类名或函数名
- 装饰器版本标签（V1 / V2 / mixed）便于下游判断是否需要按 v1→v2 迁移
- 简短说明（1-2 句）
