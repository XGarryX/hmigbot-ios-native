---
name: arkts-codebase-locator
description: 针对ArkTS语言的Harmony应用代码仓功能定位类问答技能。专门用于回答"xx功能在哪实现？"、"导出逻辑在哪？"、"增加参数/开关/按钮在哪？"等功能定位类问题，快速定位候选入口和核心文件集合。适用于HarmonyOS应用开发者快速理解和导航大型ArkTS代码库（同时支持 ArkTS V1 装饰器 @Component/@State/@Prop/@Link/@Provide/@Consume/@Observed/@ObjectLink/@StorageLink/@StorageProp/@LocalStorageLink/@LocalStorageProp/@Watch 与 V2 装饰器 @ComponentV2/@Local/@Param/@Once/@Event/@Provider/@Consumer/@ObservedV2/@Trace/@Monitor/@Computed/AppStorageV2/PersistenceV2 两套体系，定位查询时会自动覆盖两种）。使用场景包括：(1) 定位具体功能实现位置，(2) 查找特定逻辑代码，(3) 代码仓结构分析，(4) 快速理解项目架构，(5) 新功能开发时相关代码查找。
metadata:
  type: codebase
  domain: general
---
# HarmonyOS 功能定位问答技能

## 概述

本技能专注于ArkTS语言的Harmony应用代码仓功能定位类问题回答。当开发者询问"xx功能在哪实现？"、"导出逻辑在哪？"、"增加参数/开关/按钮在哪？"等功能定位问题时，本技能能够快速给出候选入口与核心文件集合，帮助开发者高效理解和导航大型ArkTS代码库。

## ArkTS V1 / V2 双版本兼容说明

本项目已锁 V2（API 12+），但代码仓中既可能存在 V1 旧代码也可能存在 V2 新代码。本技能在生成 grep / 关键词搜索时，**默认使用 V1+V2 兼容模式**，即同时匹配两套装饰器名，避免漏检：

| 类别 | V1 装饰器 | V2 装饰器 | 推荐 grep 模式 |
|------|----------|----------|---------------|
| 组件 struct | `@Component` | `@ComponentV2` | `@Component(V2)?\b` |
| 组件内部状态 | `@State` | `@Local` | `@State\|@Local` |
| 父→子单向 | `@Prop` | `@Param`（可加 `@Once`） | `@Prop\|@Param` |
| 父↔子双向 | `@Link` | `@Param + @Event` 回调 | `@Link\|@Event` |
| 跨层级 Provide | `@Provide` | `@Provider()` | `@Provide(r)?` |
| 跨层级 Consume | `@Consume` | `@Consumer()` | `@Consume(r)?` |
| 可观察类 | `@Observed` | `@ObservedV2` | `@Observed(V2)?\b` |
| 类属性级观察 | `@ObjectLink`（V2 取消） | `@Trace` 类属性标记 | `@ObjectLink\|@Trace` |
| 全局存储 | `@StorageLink` / `@StorageProp` | `AppStorageV2.connect(...)` | `@StorageLink\|@StorageProp\|AppStorageV2` |
| 本地存储 | `@LocalStorageLink` / `@LocalStorageProp` | `@Provider()/@Consumer()`（无 LocalStorageV2） | `@LocalStorageLink\|@LocalStorageProp` |
| 持久化 | `PersistentStorage.persistProp` | `PersistenceV2.globalConnect(...)` | `PersistentStorage\|PersistenceV2` |
| 监听变化 | `@Watch` | `@Monitor`（带 `IMonitor`） | `@Watch\|@Monitor` |
| 派生状态（V2 新增） | — | `@Computed` | `@Computed` |

**定位时的两条规则**：

1. 用户问"@State 变量在哪/全局状态在哪"时，**必须同时搜 V1 和 V2 等价**——否则会漏掉一半文件。
2. 报告时**两套写法的命中点都要列出**，并标注是 V1 还是 V2，方便后续判断是否需要按 v1→v2-migration-plan 迁移。

> 项目代码示例（本技能 references 中的代码块）以 V2 为目标风格；V1 装饰器仅在描述定位关键词时出现。

## 功能定位类问题类型

本技能支持以下8大类功能定位问题：

### 1. 页面和导航功能定位
- **问题特征**：询问页面、路由、导航相关功能位置
- **典型问题**："登录页面在哪实现？"、"路由配置在哪？"、"页面跳转逻辑在哪？"
- **定位目标**：页面组件文件、路由配置文件、导航相关代码

### 2. 数据存储和状态管理定位
- **问题特征**：询问数据存储、状态管理、缓存相关功能位置
- **典型问题**："用户数据存储在哪？"、"全局状态管理在哪实现？"、"本地缓存逻辑在哪？"
- **定位目标**：数据存储相关文件、状态管理代码、缓存实现
- **关键装饰器/API（V1+V2 兼容）**：
  - V1：`@State` / `@Prop` / `@Link` / `@Provide` / `@Consume` / `@Observed` / `@ObjectLink` / `@StorageLink` / `@StorageProp` / `@LocalStorageLink` / `@LocalStorageProp` / `@Watch` / `AppStorage.get/set` / `PersistentStorage`
  - V2：`@Local` / `@Param` (`@Once`) / `@Event` / `@Provider()` / `@Consumer()` / `@ObservedV2` / `@Trace` / `AppStorageV2.connect` / `PersistenceV2.globalConnect` / `@Monitor` / `@Computed`
- **推荐 grep 模式**：`@State|@Local|@Prop|@Param|@Link|@Event|@Provide|@Provider|@Consume|@Consumer|@Observed|@ObservedV2|@ObjectLink|@Trace|@StorageLink|@StorageProp|@LocalStorageLink|@LocalStorageProp|AppStorageV2|PersistenceV2|@Watch|@Monitor|@Computed`

### 3. UI组件和交互定位
- **问题特征**：询问组件、交互、样式相关功能位置
- **典型问题**："按钮组件在哪实现？"、"弹窗逻辑在哪？"、"布局文件在哪？"
- **定位目标**：UI组件文件、交互逻辑代码、样式定义文件
- **关键装饰器（V1+V2 兼容）**：V1 `@Component` + `@Entry` / V2 `@ComponentV2` + `@Entry`，配合 `@Builder` / `@Styles` / `@Extend`（V1/V2 通用）
- **推荐 grep 模式**：`@Component(V2)?\b` 或 `@Component|@ComponentV2`

### 4. API和网络请求定位
- **问题特征**：询问API调用、网络请求、接口相关功能位置
- **典型问题**："登录接口在哪调用？"、"网络请求逻辑在哪实现？"、"API接口定义在哪？"
- **定位目标**：API调用代码、网络请求实现、接口定义文件

### 5. 业务逻辑实现定位
- **问题特征**：询问核心逻辑、算法、计算相关功能位置
- **典型问题**："价格计算逻辑在哪？"、"核心算法在哪实现？"、"业务流程在哪定义？"
- **定位目标**：业务逻辑实现代码、算法处理文件、计算相关代码

### 6. 配置和常量定位
- **问题特征**：询问配置、常量、枚举相关功能位置
- **典型问题**："API配置文件在哪？"、"常量定义在哪？"、"枚举值在哪定义？"
- **定位目标**：配置文件、常量定义文件、枚举定义文件

### 7. 事件和生命周期定位
- **问题特征**：询问事件处理、生命周期、初始化相关功能位置
- **典型问题**："点击事件在哪处理？"、"生命周期函数在哪？"、"初始化逻辑在哪实现？"
- **定位目标**：事件处理代码、生命周期相关文件、初始化逻辑

### 8. 权限和安全定位
- **问题特征**：询问权限申请、安全逻辑、验证相关功能位置
- **典型问题**："权限申请在哪实现？"、"身份验证逻辑在哪？"、"安全检查在哪？"
- **定位目标**：权限申请代码、安全相关文件、验证逻辑

## 工作流程

### 步骤1：项目架构学习（repomap分析）

**目标**：利用已生成的repomap信息快速定位问题相关模块

**操作流程**：
1. **加载repomap数据**：
   - 读取项目根目录下的repomap文件（通常为`repomap.json`或`repomap.yml`）
   - 解析repomap中包含的模块说明、组件列表、文件索引等信息
   - 分析repomap提供的项目概览和结构信息

2. **模块识别与分析**：
   - 根据repomap中的模块说明，识别主要功能模块：
     - 页面模块：repomap中的`pages`分类
     - 组件模块：repomap中的`components`分类  
     - 服务模块：repomap中的`services`分类
     - 工具模块：repomap中的`utils`分类
     - 配置模块：repomap中的`config`分类
   - 分析模块间的依赖关系和功能定位
   - 确定问题相关的目标模块范围

3. **关键信息提取**：
   - 从repomap中提取问题相关的核心文件列表
   - 识别关键入口点和配置文件位置
   - 分析组件层次结构和调用关系

**输出**：基于repomap的问题相关模块清单，目标文件集合，关键入口点

### 步骤2：问题类型识别

**目标**：识别用户提问的具体功能定位问题类型

**操作流程**：
1. 分析用户问题的关键词和语义
2. 匹配到8大类问题类型中的一类
3. 确定问题的具体定位方向

**分类标准**：
- 使用关键词匹配（页面、路由、数据、组件、API、逻辑、配置、事件、权限等）
- 分析问题语义（实现位置、定义位置、配置位置等）
- 确定搜索范围和方向

**输出**：问题类型识别结果，搜索关键词集合，定位方向建议

### 步骤3：基于DAG和repomap的精准代码探索

**目标**：基于repomap信息，结合DAG（有向无环图）组合模式系统性地探索代码仓，并提供功能的完整调用链。

**操作流程**：
首先加载repomap数据，然后根据问题类型选择对应的DAG探索路径，在定位核心文件的同时，分析并记录完整的调用链关系。

**优先级策略**：
1. **第一优先级**：使用repomap信息进行精准定位
2. **第二优先级**：当repomap信息不足时，使用命令行工具进行文件召回
3. **第三优先级**：结合关键词搜索和语义分析进行补充探索

**完整调用链分析要求**：
- 在探索过程中，不仅要定位核心文件，还要跟踪函数/方法之间的调用关系
- 分析从UI组件→事件处理→业务逻辑→数据访问→API调用的完整流程
- 记录跨模块、跨层的依赖关系
- 构建可视化的调用链，帮助开发者理解功能实现的完整流程

#### DAG加载与初始化
```
加载repomap数据 → 解析模块信息 → 提取目标文件 → 建立探索索引 → 补充搜索准备 → 调用链分析准备
```

#### 补充搜索方法论

**核心思想**：具体的glob和grep命令由大模型根据问题动态生成，本技能提供关键词和语义抽取的通用方法论。

**搜索工具使用指导**：
- **Glob工具**：用于按文件类型和目录结构进行快速文件定位
- **Grep工具**：用于在文件内容中搜索关键词和模式
- **组合策略**：先用glob召回候选文件集合，再用grep在候选文件中精确定位

#### 关键词与语义抽取统一方法

**1. 关键词抽取三步法**

**步骤1：直接关键词提取**
- 从用户问题中直接提取的显性词汇
- 重点关注名词和动词
- 示例：问题"登录页面在哪实现？"
  - 直接关键词：["登录", "页面", "实现"]

**步骤2：隐含关键词推理**
- 根据问题语境推断的相关词汇
- 分析问题背后的技术含义
- 示例："登录"隐含
  - 隐含关键词：["用户", "认证", "account", "profile"]

**步骤3：技术关键词映射**
- 将自然语言关键词映射到ArkTS技术术语
- 结合HarmonyOS开发规范
- 默认输出 V1+V2 兼容关键词集合（项目锁 V2，但旧代码可能仍用 V1）
- 示例：自然语言 → ArkTS术语（V1 + V2 同时列出）
  - "页面" → ["Page", "@Entry", "@Component", "@ComponentV2"]
  - "按钮" → ["Button", "onClick"]
  - "数据/状态" → ["Data", "interface", "class", "@State|@Local", "@Prop|@Param", "@Link|@Event", "@Observed|@ObservedV2", "@Trace"]
  - "全局/共享数据" → ["AppStorage", "AppStorageV2", "LocalStorage", "PersistentStorage", "PersistenceV2"]
  - "路由" → ["router", "Navigation", "route", "NavPathStack", "NavDestination"]
  - "监听变化" → ["@Watch", "@Monitor", "IMonitor"]

**2. 语义分析四维法**

**维度1：功能维度**
- 分析问题指向的功能类型
- 对应到HarmonyOS应用的不同功能域
- 分类：页面、组件、服务、工具、配置等

**维度2：技术维度**
- 分析问题涉及的技术概念
- 映射到ArkTS的语言特性和API
- 分类：装饰器、组件、方法、接口等

**维度3：位置维度**
- 分析问题询问的位置类型
- 确定是查找实现、定义还是配置
- 分类：文件位置、代码位置、配置位置

**维度4：层级维度**
- 分析问题涉及的架构层次
- 确定是查找页面、服务、工具还是配置层
- 分类：表现层、业务层、数据层、配置层

**3. 搜索关键词生成策略**

**策略A：精确模式**
- 使用直接提取的关键词
- 适用于问题表述清晰明确的情况
- 示例：glob "**/pages/Login*.ets"

**策略B：扩展模式**
- 结合隐含关键词进行扩展
- 适用于需要发现更多相关文件的情况
- 示例：grep -r "UserService\|AuthService\|login"

**策略C：组合模式**
- 将多个关键词组合进行搜索
- 提高搜索的准确性和召回率
- 示例：glob "**/pages/*Login*.ets" AND grep -r "login\|auth"

**策略D：模糊模式**
- 使用正则表达式进行模糊匹配
- 适用于不确定具体关键词的情况
- 示例：grep -r ".*[Ll]ogin.*" --include="*.ets"

**4. 搜索路径选择指导**

**基于问题类型选择搜索路径**：

**页面/导航类问题**：
- Glob优先：查找pages目录下的.ets文件
- Grep补充：搜索 `@Entry`、`@Component(V2)?`、`router`、`Navigation`、`NavPathStack` 关键词

**数据/状态类问题**（V1+V2 兼容）：
- Glob优先：查找stores、models、data、viewmodel目录
- Grep补充：状态装饰器同时搜 V1 与 V2：
  - `@State|@Local`（组件内状态）
  - `@Prop|@Param`（父→子单向）
  - `@Link|@Event`（父↔子双向）
  - `@Observed|@ObservedV2`、`@ObjectLink|@Trace`（可观察对象）
  - `@StorageLink|@StorageProp|AppStorageV2`（全局存储）
  - `@LocalStorageLink|@LocalStorageProp`（本地存储）
  - `PersistentStorage|PersistenceV2`（持久化）
  - `@Watch|@Monitor`（监听）
  - 接口/类：`interface`、`class`

**组件/交互类问题**（V1+V2 兼容）：
- Glob优先：查找components、common目录
- Grep补充：`@Component(V2)?\b`、`onClick`、`@Builder`、事件处理关键词

**API/网络类问题**：
- Glob优先：查找services、api、network目录
- Grep补充：搜索http、fetch、request、接口定义关键词

**业务/逻辑类问题**：
- Glob优先：查找business、logic、algorithm目录
- Grep补充：搜索Service、Manager、calculate、process关键词

**配置/常量类问题**：
- Glob优先：查找config、constants、settings目录
- Grep补充：搜索const、enum、API_BASE、endpoint关键词

**事件/生命周期类问题**：
- Glob优先：查找lifecycle、hooks、events目录
- Grep补充：搜索aboutToAppear、onClick、onCreate关键词

**权限/安全类问题**：
- Glob优先：查找security、permission、auth目录
- Grep补充：搜索requestPermissions、auth、token关键词

#### DAG1：页面导航探索路径
```
repomap[pages] → page_components → routes → navigation → AppStage
```
**Primary搜索（基于repomap）**：
1. **基于repomap筛选**：
    - 从repomap的pages分类中提取页面相关文件
    - 过滤包含`@Entry`、`@Component`/`@ComponentV2` 装饰器的组件文件（V1+V2 兼容）
2. **导航逻辑分析**：
    - 在repomap索引中查找`router.push()`, `router.back()`, `NavPathStack.pushPath` 等调用
    - 定位Navigation组件和相关路由配置文件
3. **页面关联分析**：
    - 基于repomap的组件依赖关系分析页面跳转逻辑
    - 确定页面间的关系和导航路径

**补充搜索（基于关键词和语义分析）**：
根据关键词抽取方法，生成相应的glob和grep命令进行补充搜索：
1. 使用glob查找pages目录下的页面文件
2. 使用grep搜索页面装饰器（V1+V2 兼容模式）：`@Entry`、`@Component(V2)?\b` 或 `@Component|@ComponentV2`
3. 使用grep搜索路由相关调用（router、Navigation、NavPathStack、NavDestination）
4. 结合语义分析搜索页面名称模式

#### DAG2：数据状态探索路径
```
repomap[stores] → models → services → storage → AppStorage
```
**Primary搜索（基于repomap）**：
1. **基于repomap筛选**：
    - 从repomap的stores分类中提取状态管理文件
    - 过滤包含 V1（`@State` / `@Prop` / `@Link` / `@Observed` / `@ObjectLink`）或 V2（`@Local` / `@Param` / `@Event` / `@ObservedV2` / `@Trace`）装饰器的文件
2. **数据存储定位**：
    - 在repomap索引中查找 `Preferences`, `RelationalStore`/`RdbStore` 使用
    - 同时识别 V1 全局存储（`AppStorage` / `@StorageLink` / `PersistentStorage`）与 V2 等价（`AppStorageV2.connect` / `PersistenceV2.globalConnect`）
    - 定位数据模型定义和接口文件
3. **状态管理分析**：
    - 基于repomap的模块依赖分析数据流向
    - 确定状态更新和同步机制（V1 通过 `@Watch`，V2 通过 `@Monitor`/`IMonitor` 与 `@Computed`）

**补充搜索（基于关键词和语义分析）**：
根据关键词抽取方法，生成相应的glob和grep命令进行补充搜索（**V1+V2 兼容模式，强烈建议使用合并正则避免漏检**）：
1. 使用glob查找stores、models、data、viewmodel 目录下的文件
2. 使用grep搜索状态装饰器（V1+V2 一并）：
   - 组件内：`@State|@Local`
   - 父→子单向：`@Prop|@Param`
   - 父↔子双向：`@Link|@Event`
   - 可观察类：`@Observed|@ObservedV2`
   - 类属性级：`@ObjectLink|@Trace`
3. 使用grep搜索存储相关API（V1+V2 一并）：
   - 全局：`@StorageLink|@StorageProp|AppStorageV2`
   - 本地：`@LocalStorageLink|@LocalStorageProp`
   - 持久化：`PersistentStorage|PersistenceV2`
   - 偏好/数据库：`Preferences`、`RdbStore|RelationalStore`
4. 使用grep搜索监听/派生（V1+V2 一并）：`@Watch|@Monitor|@Computed`
5. 结合语义分析搜索数据模型定义（interface、class）

#### DAG3：UI组件探索路径
```
repomap[components] → common_components → pages → build_methods → styles
```
**Primary搜索（基于repomap）**：
1. **基于repomap筛选**：
    - 从repomap的components分类中提取组件文件
    - 过滤 `@Component` / `@ComponentV2` 装饰器定义的组件（V1+V2 兼容）
2. **交互事件分析**：
    - 在repomap索引中查找`onClick`, `onAppear`等事件处理
    - V2 还需关注 `@Event` 回调声明（替代 V1 `@Link` 的双向通信）
    - 定位组件交互逻辑和事件绑定
3. **样式配置定位**：
    - 基于repomap的资源配置查找样式定义
    - 确定组件样式和主题配置文件

**补充搜索（基于关键词和语义分析）**：
根据关键词抽取方法，生成相应的glob和grep命令进行补充搜索：
1. 使用glob查找components、common目录下的组件文件
2. 使用grep搜索组件装饰器（V1+V2 一并）：
   - 组件 struct：`@Component(V2)?\b` 或 `@Component|@ComponentV2`
   - 通用：`@Styles`、`@Extend`、`@Builder`、`@BuilderParam`（V1/V2 通用）
3. 使用grep搜索交互事件：`onClick`、`onAppear`、`onDisappear`、`@Event`（V2 子→父回调声明）
4. 结合语义分析搜索UI组件类型（Button、TextInput、Text、Image等）
5. 使用grep搜索布局组件（Row、Column、Stack、List、Grid 等；V2 推荐 `Repeat` 替代 ForEach/LazyForEach）

#### DAG4：API网络探索路径
```
repomap[services] → api_definitions → network_calls → utils → constants
```
**Primary搜索（基于repomap）**：
1. **基于repomap筛选**：
    - 从repomap的services分类中提取服务文件
    - 过滤包含HTTP请求调用的文件
2. **接口定义定位**：
    - 在repomap索引中查找API接口文件和类型定义
    - 确认网络请求相关的配置文件
3. **调用链分析**：
    - 基于repomap的依赖关系分析API调用链
    - 定位接口封装和数据转换逻辑

**补充搜索（基于关键词和语义分析）**：
根据关键词抽取方法，生成相应的glob和grep命令进行补充搜索：
1. 使用glob查找services、api、network目录下的文件
2. 使用grep搜索HTTP调用（http.createHttp、request方法）
3. 使用grep搜索网络请求方法（GET、POST、PUT、DELETE）
4. 结合语义分析搜索API接口定义（interface、endpoint）
5. 结合语义分析搜索认证相关（auth、token、jwt）

#### DAG5：业务逻辑探索路径
```
repomap[business] → logic_files → rule_definitions → algorithms → utils
```
**Primary搜索（基于repomap）**：
1. **基于repomap筛选**：
    - 从repomap的business分类中提取业务逻辑文件
    - 过滤包含算法和业务规则的文件
2. **核心逻辑定位**：
    - 在repomap索引中查找算法实现和逻辑处理
    - 确定业务规则和约束定义文件
3. **处理流程分析**：
    - 基于repomap的模块关系分析业务处理流程
    - 定位关键计算和数据处理逻辑

**补充搜索（基于关键词和语义分析）**：
根据关键词抽取方法，生成相应的glob和grep命令进行补充搜索：
1. 使用glob查找business、logic、rules、algorithms目录下的文件
2. 使用grep搜索业务相关类（Service、Manager）和方法（calculate、process）
3. 使用grep搜索算法和规则相关关键词（algorithm、rule、validation）
4. 结合语义分析搜索业务逻辑标识（business、domain、entity、value object）

#### DAG6：配置常量探索路径
```
repomap[config] → constants → enums → settings_files
```
**Primary搜索（基于repomap）**：
1. **基于repomap筛选**：
    - 从repomap的config分类中提取配置文件
    - 过滤包含常量定义的文件
2. **配置内容分析**：
    - 在repomap索引中查找应用配置和环境配置
    - 定位全局常量和枚举定义
3. **配置关系分析**：
    - 基于repomap的依赖关系分析配置使用情况
    - 确定配置更新和应用机制

**补充搜索（基于关键词和语义分析）**：
根据关键词抽取方法，生成相应的glob和grep命令进行补充搜索：
1. 使用glob查找config、constants、enums、settings目录下的文件
2. 使用grep搜索常量定义（const、export const、readonly）
3. 使用grep搜索枚举定义（enum）
4. 结合语义分析搜索配置相关模式（config、API_BASE、endpoint）

#### DAG7：事件生命周期探索路径
```
repomap[lifecycle] → lifecycle_methods → event_handlers → initialization
```
**Primary搜索（基于repomap）**：
1. **基于repomap筛选**：
    - 从repomap的lifecycle分类中提取生命周期文件
    - 过滤包含生命周期方法的文件
2. **事件处理定位**：
    - 在repomap索引中查找事件监听和回调函数
    - 定位生命周期事件处理逻辑
3. **初始化分析**：
    - 基于repomap的组件关系分析初始化流程
    - 确定关键初始化逻辑和资源管理

**补充搜索（基于关键词和语义分析）**：
根据关键词抽取方法，生成相应的glob和grep命令进行补充搜索：
1. 使用glob查找lifecycle、hooks、events、init目录下的文件
2. 使用grep搜索生命周期方法（aboutToAppear、aboutToDisappear、onShow、onHide、onCreate、onDestroy）
3. 使用grep搜索事件处理（onClick、onTouch、onLongPress、addEventListener；V2 还含 `@Event` 子→父回调声明）
4. 使用grep搜索状态变化监听（V1+V2 一并）：`@Watch|@Monitor`，V2 还可关注 `@Computed` 派生
5. 结合语义分析搜索初始化相关（init、initialize、bootstrap、setup）

#### DAG8：权限安全探索路径
```
repomap[security] → permissions → authentication → validation
```
**Primary搜索（基于repomap）**：
1. **基于repomap筛选**：
    - 从repomap的security分类中提取安全相关文件
    - 过滤包含权限申请的文件
2. **权限管理定位**：
    - 在repomap索引中查找权限申请和安全检查
    - 定位身份验证和授权逻辑
3. **安全机制分析**：
    - 基于repomap的依赖关系分析安全处理流程
    - 确定加密和安全保护机制

**补充搜索（基于关键词和语义分析）**：
根据关键词抽取方法，生成相应的glob和grep命令进行补充搜索：
1. 使用glob查找security、permissions、auth、validation目录下的文件
2. 使用grep搜索权限相关API（requestPermissions、ohos.permission）
3. 使用grep搜索权限申请模式（CAMERA、LOCATION、STORAGE、INTERNET）
4. 结合语义分析搜索认证相关（auth、login、token、jwt、authenticate、verify）
5. 结合语义分析搜索加密和安全（encrypt、decrypt、hash、cipher）

### 步骤4：回退机制和重试策略

**目标**：在探索失败时提供备选方案，确保回答的可靠性

**回退机制**：
1. **DAG路径回退**：当前DAG步骤探索失败时，返回上一步尝试继续探索，如果失败继续回退直至第一步
2. **降级探索模式1（基于repomap）**：基于repomap的文件列表进行关键词搜索
3. **降级探索模式2（基于命令行工具）**：使用glob和grep进行文件召回和关键词搜索

**命令行工具搜索策略**：
1. **Glob优先文件召回**：
    - 使用glob按文件扩展名和目录结构进行快速文件定位
    - 基于问题类型选择合适的glob模式
    - 结合项目结构使用多层glob模式

2. **Grep关键词搜索**：
    - 使用grep进行文件内容关键词搜索
    - 结合正则表达式进行模式匹配
    - 使用多关键词组合搜索提高精度

3. **混合搜索策略**：
    - 先用glob召回候选文件集合
    - 再用grep在候选文件中精确定位
    - 结合关键词和语义分析优化搜索关键词

**重试策略**：
1. **三次重试机制**：每个步骤最多重试3次
2. **备选探索路径**：当前DAG最多尝试失败后，重试尝试不同的DAG路径
3. **repomap信息增强**：利用repomap重新定位模块
4. **命令行工具备选**：repomap失败时，使用glob和grep进行搜索
5. **人工干预**：仍然失败后，向用户请求更具体的问题描述

**错误处理**：
- 记录每次探索的具体错误信息和repomap使用情况
- 分析repomap数据是否完整或准确
- 记录命令行工具搜索的执行情况和结果
- 提供错误原因分析，建议优化探索方向
- 在repomap信息不足时，建议重新生成或更新repomap
- 在命令行工具搜索失败时，建议用户澄清问题

### 步骤5：回答模板输出

**目标**：提供结构化、功能定位明确的回答，包含完整的调用链分析

**回答模板结构**：

```
# [功能名称] 定位结果

## 🎯 定位总结
[简要说明功能的总体定位位置和核心文件]

## 📁 核心文件清单
- **文件路径**：`完整文件路径`
- **文件类型**：文件类型说明
- **功能描述**：该文件中的具体功能实现
- **关键代码片段**：相关的核心代码示例

## 🔍 探索路径
1. 探索过程的第一步
2. 关键发现点
3. 最终定位方法

## 🔗 完整调用链
[重点强调：提供从UI触发到最终实现的完整调用链]

### 调用链层级结构
```
[UI层] → [事件处理层] → [业务逻辑层] → [数据访问层] → [API/存储层]
```

### 详细调用流程
**步骤1：UI触发**
- **触发源**：用户操作或系统事件
- **入口组件**：具体的UI组件文件和方法
- **事件处理**：事件处理函数名称和位置

**步骤2：事件传递**
- **传递方式**：方法调用、事件冒泡、状态更新
- **中间组件**：经过的中间组件或服务
- **参数传递**：传递的参数和数据

**步骤3：业务逻辑**
- **核心逻辑**：业务逻辑处理的文件和方法
- **算法/规则**：涉及的计算、验证、规则执行
- **状态管理**：状态更新和数据同步机制

**步骤4：数据操作**
- **数据访问**：数据读取、修改、删除等操作
- **存储/缓存**：数据存储、缓存、持久化操作
- **数据模型**：涉及的数据模型和接口定义

**步骤5：外部交互**
- **API调用**：HTTP请求、接口调用、第三方服务
- **权限检查**：权限申请、权限验证、安全检查
- **配置读取**：配置文件读取、环境变量、常量使用

### 跨模块依赖关系
**模块A → 模块B → 模块C**
- 说明模块之间的依赖关系
- 标注关键的接口和调用点
- 分析数据的流向和传递方式

## 💡 关键入口点
- **主要入口**：主要功能入口文件和位置
- **次要入口**：相关的辅助文件和位置
- **配置位置**：相关配置文件位置

## 📋 详细清单
| 文件路径 | 文件类型 | 功能模块 | 关键词 | 在调用链中的位置 |
|---------|---------|---------|--------|-----------------|
| 完整路径 | 文件类型 | 功能模块 | 相关关键词 | [UI/事件/业务/数据/API] |

## ⚠️ 注意事项
[特别说明或需要用户注意的地方]
[特别说明或需要用户注意的地方]
```

### 步骤6：事实核查与保证

**目标**：确保所有回答都基于真实的代码仓内容

**核查原则**：
1. **代码验证**：每个定位结果都必须在代码中实际存在
2. **文件路径验证**：确认提到的文件在项目中的真实路径
3. **代码片段验证**：确保提供的代码片段能够实际找到

**信息不足处理**：
1. **承认未知**：当信息不足时，明确告知用户无法确定的部分
2. **反问澄清**：请求用户提供更多信息以帮助精确定位
3. **避免臆断**：禁止对缺失的细节进行假设

**文档记录**：
- 记录每次探索的过程和结果
- 保存分析过程中的关键发现
- 维护问题-答案映射关系，便于后续优化

## 输出标准

### 忠实性要求
- 一切结果都必须源于真实的代码仓内容
- 禁止臆测和假设
- 信息不足时明确告知

### 准确性要求
- 文件路径必须准确无误
- 代码片段必须真实存在
- 功能描述必须准确匹配

### 完整性要求
- 提供核心文件清单
- 给出探索过程说明
- 标注关键入口点

### 可用性要求
- 提供可直接访问的文件路径
- 给出具体的操作建议
- 提供后续开发指导

## 常见问题处理

### 问题1：项目结构与预期不符
**处理**：重新进行repomap分析，适应项目实际结构

### 问题2：功能分布多个模块
**处理**：提供完整的分布式定位结果，标注各模块间的关系，构建完整的调用链

### 问题3：代码结构不清晰
**处理**：通过多种搜索方式进行交叉验证，确保定位准确性，分析完整的调用流程

### 问题4：新功能开发相关代码
**处理**：基于现有架构模式，推断可能的实现位置，提供调用链的参考模板

## 使用示例

**用户问题**："登录功能在哪实现？"

**技能执行**：
1. **加载repomap数据**：读取项目中的repomap.json文件，解析模块和组件信息
2. **问题类型识别**：识别为"页面和导航功能定位"问题类型
3. **基于repomap的DAG探索**（V1+V2 兼容）：
    - 从repomap.categories.pages获取页面候选文件
    - 筛选包含`@Entry`装饰器的页面组件，并识别属于 V1（`@Component`）还是 V2（`@ComponentV2`）
    - 分析组件的路由配置和依赖关系
    - 查找router相关调用、`NavPathStack`/`NavDestination` 与 Navigation组件使用
    - **分析完整调用链**：从UI点击事件→事件处理函数→认证服务→API调用→数据存储
4. **精准定位**：利用repomap的元数据信息验证和补充探索结果
5. **结构化输出**：基于repomap数据生成完整的定位结果，包含完整调用链

**输出结果**包含：
- 登录页面文件位置（基于repomap.components索引；标注 V1/V2）
- 路由配置信息（基于repomap.routes分析）
- 相关的API调用代码（基于repomap.services追踪）
- 样式和组件定义文件（基于repomap.dependencies关联）
- **完整调用链分析（V2 项目示例）**：
  ```
  用户点击登录按钮（LoginPage.ets:Button.onClick）
    ↓
  调用login方法（LoginPage.ets:login())
      ↓
      调用AuthService.login（services/AuthService.ets:login）
          ↓
          发送HTTP请求到登录API（http.createHttp.request）
              ↓
              接收响应并验证（AuthService.ets:validateResponse）
                  ↓
                  保存用户token到全局存储（stores/UserStore.ets:saveToken；V2 用 AppStorageV2.connect，V1 用 @StorageLink）
                      ↓
                      更新用户状态（V2: @Local isAuthenticated = true / @Trace；V1: @State isAuthenticated = true）
                          ↓
                          路由跳转到首页（router.pushUrl 或 NavPathStack.pushPath）
  ```

## 参考文档

本技能依赖以下参考资料来确保定位的准确性和全面性：

- [项目结构指南](references/project-structure.md) - HarmonyOS标准项目结构解析
- [问题类型分类](references/question-types.md) - 8大类功能定位问题类型详解
- [ArkTS编程模式](references/arkts-patterns.md) - ArkTS语言特征和最佳实践
- [工作流程指导](references/workflows.md) - 标准化的功能定位工作流程
- [repomap使用指南](references/repomap-guide.md) - 基于repomap的功能定位方法

通过这种系统化的方法，结合repomap的元数据信息、DAG探索模式、命令行工具搜索以及关键词和语义分析，开发者能够快速、准确地定位HarmonyOS ArkTS应用中的各种功能实现，显著提高开发效率和代码导航能力。