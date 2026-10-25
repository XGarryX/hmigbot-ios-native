---
name: mod-design
description: 根据需求分析阶段的产出物（proposal.md、delta-spec.md、info.md、task-lessons.md 等），生成 design.md 或 delta-design.md，用于指导后续任务分解和代码实现。当用户说"生成设计文档"、"输出 design"、"完成设计"、"生成 delta-design"时触发。注意：本 skill 是正向设计（根据需求生成设计），而非逆向分析（从代码反推设计）。
---

# MOD Design Skill

根据需求分析产出物，生成符合 ArkTS/HarmonyOS 项目规范的 design.md 或 delta-design.md，用于指导后续任务分解和代码实现。

## 核心定位

根据需求产出设计文档。设计文档应当结构稳定、符号精确、路径可定位，便于后续被检索、引用与交叉校验。

## 使用场景

| 场景 | 判断条件 | 输出路径 |
|------|----------|----------|
| 全新项目设计 | `specs/changes/` 目录不存在 | `{SPECS_FEATURE_ROOT}/design.md` |
| 增量变更设计 | `specs/changes/` 目录已存在 | `{CHANGES_ROOT}/{date}-{type}-{name}/delta-design.md` |

## 输入

按优先级读取以下文件（位于 `specs/changes/{date}-{type}-{name}/` 或 `{SPECS_FEATURE_ROOT}/`）：
1. `info.md` - 代码仓理解（来自 PLANNING）
2. `proposal.md` - 需求提案（来自 PLANNING）
3. `delta-spec.md` 或 `spec.md` - 需求规格说明（来自 PLANNING）
4. `task-lessons.md` - 经验教训（来自 LESSON_LEARNING）

## Step 0: 确定输出类型

检查 `specs/changes/` 目录是否存在：
- 存在 → 输出 `delta-design.md`（增量设计，专注于变更点）
- 不存在 → 输出 `design.md`（完整设计，覆盖全量功能）

## Step 1: 理解需求与现有架构

**1.1 理解需求**
- 核心功能需求：来自 proposal.md / delta-spec.md
- 代码仓现状：来自 info.md（技术栈、模块结构）
- 历史经验教训：来自 task-lessons.md（避免重复犯错）

**1.2 参考现有架构（增量变更时）**
若为增量变更设计，读取现有设计文档作为参考，确保新设计与现有架构一致。

## Step 2: 生成设计文档

按以下章节结构生成文档。

---

## D1: 概述

```markdown
## 1. 概述
### 1.1 应用定位
### 1.2 核心交互
### 1.3 技术栈概览
```

**1.1 应用定位**：从 proposal.md 提炼功能定位

**1.2 核心交互**：描述主要用户交互流程（用户 → 页面 → 功能 → 结果）

**1.3 技术栈概览**：列出技术栈
- 框架：ArkTS、Stage 模型、ArkUI 声明式
- 状态管理：V1（@State/@Prop/@Link）还是 V2（@ObservedV2/@Trace）
- 使用的 Kit 列表
- 是否有 Native C++/Rust 模块
- Hvigor 插件配置

---

## D2: 功能清单

```markdown
## 2. 功能清单
```

| 功能名 | 说明 | 入口 Ability/Page | 优先级 |
|--------|------|-------------------|--------|

- **P0**：核心功能，无则无法使用
- **P1**：重要功能，影响主要流程
- **P2**：辅助功能，增强体验

---

## D3: 实现模型

```markdown
## 3. 实现模型
### 3.1 上下文视图
### 3.2 总体架构
### 3.3 HAP/HAR/HSP 模块划分
### 3.4 设计系统规格
### 3.5 - 3.N 模块实现设计
```

### D3.1: 上下文视图

PlantUML 上下文图：User ↔ App ↔ System Kits / 远端设备 / 云 / 其他应用

### D3.2: 总体架构

PlantUML 分层架构图，体现 ArkTS 声明式 UI 与状态管理的单向数据流：

```
View（页面）→ ViewModel（状态）→ Service（业务）→ Data（数据）→ Platform-Kit（系统能力）
```

### D3.3: 模块划分

基于 build-profile.json5 和各模块 module.json5 确定：
- entry HAP：主入口模块
- feature HAP：功能模块
- HAR：静态共享包
- HSP：动态共享包
- OHPM 依赖：第三方包

### D3.4: 设计系统规格

```markdown
### 3.4 设计系统规格
#### 3.4.1 色彩系统
#### 3.4.2 主题系统
#### 3.4.3 排版系统
#### 3.4.4 间距与尺寸系统
#### 3.4.5 图标与图形资源
#### 3.4.6 动画规格
#### 3.4.7 响应式断点与栅格
```

**3.4.1 色彩系统**：设计应用中使用的色彩体系

| 名称 | Light 模式 | Dark 模式 | 用途 |

**3.4.2 主题系统**：主题切换逻辑、自定义 theme/styles

**3.4.3 排版系统**：字号规格表

| 名称 | 字号 | 用途 |

**3.4.4 间距与尺寸系统**：尺寸值表

| 名称 | 值 | 用途 |

**3.4.5 图标与图形资源**：

| 名称 | 类型 | 尺寸 | 用途 |

**3.4.6 动画规格**：动画时长、曲线、触发条件

**3.4.7 响应式断点与栅格**：sm/md/lg/xl 断点定义

### D3.5 - D3.N: 模块实现设计

```markdown
### 3.X {模块名}模块实现设计
#### 3.X.1 模块介绍
#### 3.X.2 功能描述
#### 3.X.3 目录结构
#### 3.X.4 架构图谱
#### 3.X.5 功能与用例分析
#### 3.X.6 接口设计
#### 3.X.7 状态管理设计
#### 3.X.8 核心算法
#### 3.X.9 错误处理
#### 3.X.10 依赖关系
```

**3.X.1 模块介绍**：模块职责与范围（entry / feature / har / hsp 身份、是否 installationFree）

**3.X.2 功能描述**：主要功能列表

**3.X.3 目录结构**：

```
ets/
├── pages/          # 页面
├── view/           # 自定义组件
├── viewmodel/      # 视图模型
├── service/        # 业务服务
├── model/          # 数据模型
├── common/         # 公共能力
└── cpp/            # Native 模块（如有）
```

**3.X.4 架构图谱**：
- PlantUML 类图
- PlantUML 时序图
- PlantUML ER 图（数据存储模块）
- PlantUML 状态图（Ability 生命周期）

**3.X.5 功能与用例分析**：

```
用例：{用例名}
前置条件：{条件}
步骤：1. ... 2. ... 3. ...
后置条件：{结果}
```

**3.X.6 接口设计**：公开接口的方法签名、参数、返回值、是否 async

**3.X.7 状态管理设计**：
- V1: @State / @Prop / @Link / @Provide / @Consume / @Observed + @ObjectLink
- V2: @ObservedV2 + @Trace / @ComponentV2
- 存储: AppStorage / PersistentStorage / LocalStorage
- 附数据流图

**3.X.8 核心算法**：复杂算法（调度/合并/去重/加解密/编解码）的逻辑和复杂度

**3.X.9 错误处理**：BusinessError 处理、降级策略、重试机制、埋点策略

**3.X.10 依赖关系**：
- 内部依赖：其他模块 / HAR / HSP
- 外部依赖：Kit / OHPM 包 / Native so

**模块优先生成顺序**：
1. 数据存储模块（RDB / Preferences / 分布式数据）
2. 核心业务模块（如播放、内容、支付）
3. 跨端与卡片模块（ServiceExtension / FormExtension / Continuation）
4. 基础平台模块（网络、鉴权、埋点）
5. Native / C++ 模块（若有）

---

## D4: 接口设计

```markdown
## 4. 接口设计
### 4.1 内部数据访问 API
### 4.2 业务抽象接口
### 4.3 后台任务与 ExtensionAbility 接口
### 4.4 Want / Action 协议
### 4.5 URI / Deep Link / AppLinking 协议
### 4.6 IPC 与 RPC 接口
### 4.7 Native（C/C++）接口
### 4.8 文件交换接口
```

**4.1 内部数据访问 API**：relationalStore / preferences 封装类的读写方法签名

**4.2 业务抽象接口**：interface / abstract class（业务接口）

**4.3 后台任务接口**：各类 *ExtensionAbility 的生命周期接口

**4.4 Want/Action 协议**：module.json5.skills.actions

**4.5 URI / Deep Link / AppLinking 协议**：module.json5.skills.uris

**4.6 IPC 与 RPC 接口**：rpc.RemoteObject / MessageSequence

**4.7 Native 接口**：napi_* / .d.ts 声明

**4.8 文件交换接口**：导入/导出格式（JSON Schema / XML / 二进制协议）

---

## D5: 数据模型

```markdown
## 5. 数据模型
### 5.1 关系型数据库模型
### 5.2 领域模型
### 5.3 Preferences 结构
### 5.4 分布式数据对象模型
### 5.5 文件格式 Schema
```

**5.1 RDB 模型**：建表 SQL + PlantUML ER 图

**5.2 领域模型**：

| 字段名 | 类型 | 必填 | 说明 |

**5.3 Preferences 结构**：

| key | 类型 | 默认值 | 说明 |

**5.4 分布式数据对象模型**：DistributedDataObject / 分布式 KV Store 的 Schema

**5.5 文件格式 Schema**：导入/导出格式

---

## D6: UI 设计系统

```markdown
## 6. UI设计系统
### 6.1 色彩系统
### 6.2 主题与暗色模式
### 6.3 排版系统
### 6.4 间距与尺寸规范
### 6.5 图标与图形资源
### 6.6 动画规格
### 6.7 一多响应式规范
```

若 §3.4 已足够详细，此处写"见 §3.4"并补充一多响应式规范要点。

---

## D7: 页面清单与导航

```markdown
## 7. 页面清单与导航
### 7.1 页面清单总表
### 7.2 全局导航图
### 7.3 Deep Link / AppLinking 处理
### 7.4 Want 跳转矩阵
```

**7.1 页面清单总表**：

| 页面名 | 路径 | 入口 Ability | 传参 | 功能摘要 |

**7.2 全局导航图**：PlantUML 导航图

**7.3 Deep Link / AppLinking**：scheme/host/path 配置

**7.4 Want 跳转矩阵**：Action / bundleName / abilityName / parameters

---

## D8: 用户交互规格

```markdown
## 8. 用户交互规格
### 8.1 手势交互目录
### 8.2 弹窗/Sheet/Menu 目录
### 8.3 剪贴板与反馈行为
### 8.4 卡片交互
```

**8.1 手势交互**：onClick、gesture、TapGesture、LongPressGesture、PanGesture、PinchGesture、SwipeGesture、bindContextMenu

**8.2 弹窗目录**：AlertDialog、ActionSheet、CustomDialog、@CustomDialog、promptAction、bindSheet、bindMenu

**8.3 剪贴板与反馈**：PasteBoard、Toast、Dialog

**8.4 卡片交互**：FormExtensionAbility、FormBindingData、widget

---

## D9: 平台集成

```markdown
## 9. 平台集成
### 9.1 构建配置与依赖
### 9.2 权限与运行时请求
### 9.3 系统能力（Kits）清单
### 9.4 后台与 Extension
### 9.5 备份与恢复
### 9.6 分布式与跨端
```

**9.1 构建配置**：oh-package.json5 依赖表 + build-profile.json5 关键配置

**9.2 权限与运行时请求**：

| 权限 | 类型 | reason | usedScene | 降级行为 |

区分 system_grant / user_grant

**9.3 Kits 清单**：

| Kit | 关键 API | 用途 |

**9.4 后台与 Extension**：ExtensionAbility 详情 + 后台模式

**9.5 备份与恢复**：BackupExtension + backupConfig.json

**9.6 分布式与跨端**：流转、组网、跨设备数据、超级终端

---

## D10: 偏好设置目录

```markdown
## 10. 偏好设置目录
### 10.1 - 10.N {按偏好类分组}
```

| key | 类型 | 默认值 | 说明 | 行为影响 |

---

## Step 3: 自验证

设计文档与需求文档交叉校验：

1. **功能一致性**：proposal.md / delta-spec.md 的功能 ↔ design.md §2 功能清单
2. **页面一致性**：proposal.md / delta-spec.md 的页面需求 ↔ design.md §7.1
3. **数据一致性**：proposal.md / delta-spec.md 的数据模型 ↔ design.md §5
4. **权限一致性**：proposal.md / delta-spec.md 的权限需求 ↔ design.md §9.2
5. **Kit 一致性**：proposal.md / delta-spec.md 声明的 Kit ↔ design.md §9.3

**delta-design.md 验证范围**：仅验证变更涉及的章节。

---

## 输出规则

1. **语言**：中文撰写，代码标识符保持英文原样
2. **格式**：严格遵循上述章节编号结构
3. **表格**：结构化数据优先使用 markdown 表格
4. **图表**：架构图、时序图、ER 图、状态图使用 PlantUML（`@startuml ... @enduml`）
5. **增量设计**：delta-design.md 专注于变更点，通过引用已有 design.md 的章节实现（格式：`见 design.md §X.X`）
6. **可追溯**：每个设计决策关联到对应的需求条目（来自 proposal.md / delta-spec.md）
7. **推断标记**：基于设计推断的内容标记 `[推断]`
8. **缺失处理**：某章节在需求中无相关实现 → 写"无相关实现"，保留章节标题不删除
9. **API 版本**：涉及 @ohos.* / @kit.* 时，标注最低 API version
10. **ArkTS 版本**：明确状态管理使用 V1 还是 V2

---

## 输出

- **全新项目**：`{SPECS_FEATURE_ROOT}/design.md`
- **增量变更**：`{CHANGES_ROOT}/{date}-{type}-{name}/delta-design.md`

---

## 文档生成标记

在文档末尾追加：

```markdown
---
> 本文档由 mod-design skill 生成。
> 标记 [推断] 的内容为基于设计推断，非确定性事实。
> 生成时间: {当前时间}
```