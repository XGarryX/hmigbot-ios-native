---
name: migbot-increment-init
description: "触发：`$migbot-increment-init` 或自然语言（\"初始化\"/\"init\"/\"环境检查\"）。Migbot-Increment 工作流初始化 skill，在首次使用 migbot-increment-workflow 前执行环境检查和目录配置。 当用户说\"初始化\"、\"init\"、\"环境检查\"或首次使用 migbot-increment-workflow 前触发。 功能：项目路径验证、环境检查（编译/测试）、TEST_ROOT 检测、目录配置确认、Git 状态检查、会话恢复检查。"
---

# migbot-increment-init Skill

## 概述

migbot-increment-init 是 Migbot-Increment 工作流的初始化阶段，确保在开始 PLANNING 之前环境和目录配置就绪。

**执行时机**：首次使用 migbot-increment-workflow 前，或使用 `$migbot-increment-init` 重新初始化。

---

## 入口

```
$migbot-increment-init              # 执行初始化检查
$migbot-increment-init --force      # 强制重新初始化（跳过会话恢复）
```

---

## 执行流程

```
Step 1: 检查初始化状态
    ↓
Step 2: 验证项目路径 (PROJECT_ROOT)
    ↓
Step 3: 检查环境
    ├─ 3-1: 构建工具版本
    ├─ 3-2: 编译测试
    ├─ 3-3: TEST_ROOT 检测与确认
    └─ 3-4: 测试框架检查（含环境变量和路径收集）
    ↓
Step 4: 创建目录结构
    ↓
Step 5: 用户确认目录配置
    ↓
Step 6: Git 状态检查
    ↓
Step 7: 会话恢复检查
    ↓
Step 8: 写入初始化标记 + 写入 README.md 配置摘要
```

---

## Step 1: 检查初始化状态

检查 `specs/initialized.flag` 是否存在：

| 状态 | 处理 |
|------|------|
| 文件存在 | 显示已初始化信息，询问用户选择 |
| 文件不存在 | 继续 Step 2 |

### 已初始化时的提示

```
## 检测到已初始化

最后初始化时间：{date}
项目：{PROJECT_ROOT}

选项：
1. 继续（使用现有配置）→ 执行 Step 6-7 后完成
2. 重新初始化 → 删除现有标记并重新执行
```

---

## Step 2: 验证项目路径

### 2-1: 检测项目类型

检查项目根目录下的构建文件：

| 构建文件 | 项目类型 | 编译命令 | 测试命令 |
|---------|---------|---------|---------|
| `hvigorw` | HarmonyOS | `hvigorw assembleHap` | `hvigorw test@entry` |
| `package.json` | Node/JS/TS | `npm run build` | `npm test` |
| 其他 | 未知类型 | 询问用户 | 询问用户 |

### 2-2: 验证项目路径

1. 检查 `{PROJECT_ROOT}/` 是否存在
2. 检查构建文件是否存在

**失败处理（BLOCK — 必须修复）：**

```
## ❌ 项目路径验证失败

未找到目标项目。请确认项目路径。

检查路径：./{项目名}-main

错误详情：
{error_message}

---

### 修复选项

请选择以下方式之一来修复：

1. **指定正确路径** → 请提供正确的项目路径
2. **创建新项目** → 在当前目录初始化新项目
3. **列出可用目录** → 我来帮你查找当前目录下的项目

请输入选项编号或直接提供项目路径：
_
```

**循环检查机制**：
- 用户提供新路径 → 重新验证
- 验证失败 → 显示错误，继续循环
- 验证成功 → 继续下一步

---

## Step 3: 检查环境

### 3-1: 检查构建工具版本

运行版本检查命令：

| 项目类型 | 检查命令 | 成功标准 |
|---------|---------|---------|
| HarmonyOS | `hvigorw --version` | 输出版本号 |
| Node/JS/TS | `node --version && npm --version` | 输出版本号 |
| 未知 | 询问用户 | 用户提供命令 |

**失败处理（BLOCK — 必须修复，循环检查）：**

```
## ⚠️ 构建工具检查失败

{build_tool} 未安装或不可用。

检查命令：{command}
错误详情：{error_message}

---

### 修复建议

| 平台 | 安装命令 |
|------|---------|
| macOS | {install_command} |
| Linux | {install_command} |
| Windows | {install_command} |

---

### 请选择

1. **我已修复** → 重新检查
2. **需要更多信息** → 询问具体问题
3. **使用其他工具** → 指定替代构建命令

请输入选项编号：
_
```

### 3-2: 编译测试

运行编译命令确认项目可构建：

| 项目类型 | 编译命令 | 成功标准 |
|---------|---------|---------|
| HarmonyOS | `hvigorw assembleHap` | BUILD SUCCESS |
| Node/JS/TS | `npm run build` | 退出码 0 |
| 未知 | 询问用户 | 用户确认 |

**失败处理（BLOCK — 必须修复，循环检查）：**

```
## ⚠️ 编译测试失败

项目无法成功编译。

编译命令：{command}
退出码：{exit_code}

错误摘要：
{error_summary}

---

### 修复建议

| 错误类型 | 解决方案 |
|---------|---------|
| 缺少依赖 | 运行 npm install / ohpm install |
| 语法错误 | 检查错误指向的文件 |
| 路径错误 | 检查 hvigorw 是否在项目根目录 |
| 权限问题 | 检查文件读写权限 |

---

### 请选择

1. **我已修复** → 重新编译
2. **需要帮助分析错误** → 我来详细解释错误原因
3. **环境问题，需要配置** → 指导配置编译环境

请输入选项编号：
_
```

---

### 3-3: TEST_ROOT 检测与确认

#### 自动检测

按以下顺序检测 TEST_ROOT：

1. `{PROJECT_ROOT}/entry/src/test/` — HarmonyOS 标准位置
2. `{PROJECT_ROOT}/test/` — 常见备选位置
3. `{PROJECT_ROOT}/entry/test/` — 备选结构
4. 扫描项目中的测试相关目录

#### 检测结果处理

**检测到时：**
```
## TEST_ROOT 检测

自动检测到以下测试目录：

| 路径 | 状态 | 文件数 |
|------|------|--------|
| {path_1} | 推荐 | {count} |
| {path_2} | 备选 | {count} |

推荐使用：{recommended_path}

目录预览：
{file_list_preview}
```

**请确认：**
1. **确认使用推荐目录**
2. **使用其他检测到的路径** → 请选择
3. **指定其他路径** → 请提供路径

---

**未检测到时（BLOCK — 必须指定）：**
```
## TEST_ROOT 未检测到

在标准位置未找到测试目录。

已检查路径：
- {PROJECT_ROOT}/entry/src/test/
- {PROJECT_ROOT}/test/
- {PROJECT_ROOT}/entry/test/

---

### 请指定测试目录

1. **创建默认测试目录** → 在 {PROJECT_ROOT}/entry/src/test/ 创建
2. **指定现有目录** → 请提供路径
3. **稍后配置** → 跳过，但在 APPLYING 阶段需要重新指定

请输入选项编号或路径：
_
```

**确认新目录时：**
```
## 确认新目录

您选择了：{new_path}

1. **确认** → 使用此目录继续
2. **返回重新选择** → 返回上一步
```

---

### 3-4: 测试框架检查

#### 3-4-1: 检查系统环境变量

检查以下环境变量：

| 变量 | 用途 | 当前值 |
|------|------|--------|
| HARMONYOS_SDK_HOME | SDK 根目录 | {value} |
| HARMONY_SDK_ROOT | SDK 根目录 | {value} |
| OHOS_SDK_ROOT | SDK 根目录 | {value} |
| PATH | 系统路径 | {已记录} |

```
## 系统环境变量检查

| 变量 | 状态 |
|------|------|
| SDK_HOME | {未设置/已设置} |
| JAVA_HOME | {未设置/已设置} |

未检测到 SDK 路径。
请提供 SDK 根目录路径（或直接回车跳过）：
_
```

#### 3-4-2: 检查重要路径

检查以下路径：

| 工具 | 状态 |
|------|------|
| hvigorw | {✅/❌} |
| SDK | {⚠️未设置} |

```
## 重要路径检查

| 工具 | 状态 |
|------|------|
| hvigorw | {✅ 找到 / ❌ 未找到} |
| SDK | {⚠️ 未设置} |

请提供以下路径（如已知）：

SDK 根目录：_
hvigorw 路径：_
```

#### 3-4-3: 验证测试框架

基于确认的路径验证测试框架：

```
## 测试框架验证

正在使用以下路径验证：

SDK: {sdk_path}
hvigorw: {hvigorw_path}

验证中...
```

**成功：**
```
✅ 测试框架验证通过

测试命令: hvigorw test@entry
可用测试: {count} 个
```

**失败：**
```
## ⚠️ 测试框架验证失败

错误: {error_message}

请选择：
1. 加载 harmony-ui-test skill（推荐）
2. 重新配置路径
3. 提供替代测试命令
4. 跳过（确认风险）
```

---

## Step 4: 创建目录结构

自动创建以下目录（如不存在）：

| 目录 | 说明 |
|------|------|
| `specs/changes/` | 变更记录根目录 |
| `specs/guidelines/` | 领域指南 |
| `specs/guidelines/incidents/` | 事件报告 |
| `specs/archives/` | 归档记录 |

---

## Step 5: 用户确认目录配置

### 默认配置

| 目录 | 默认值 | 说明 |
|------|--------|------|
| PROJECT_ROOT | `./{项目名}-main` | 目标项目路径 |
| CHANGES_ROOT | `specs/changes` | 变更记录根目录 |
| SPECS_FEATURE_ROOT | `specs/specs` | 特性规格根目录 |
| TEST_ROOT | 自动检测的值 | 测试文件目录 |

### 确认提示

```
## 目录配置确认

请确认以下路径配置：

| 目录 | 当前值 |
|------|--------|
| PROJECT_ROOT | ./MyApp-main |
| CHANGES_ROOT | specs/changes |
| SPECS_FEATURE_ROOT | specs/specs |
| TEST_ROOT | ./MyApp-main/entry/src/test |

选项：
1. 确认所有路径正确
2. 修改某个路径（请说明要修改哪个目录和新路径）
```

---

## Step 6: Git 状态检查

```bash
git status --short
git branch --show-current
```

### 有未提交变更时

```
## Git 状态

当前分支：{branch}
未提交变更：{count} 个文件

选项：
1. 提交变更 → 询问提交信息
2. 暂存变更 → git stash
3. 忽略（有风险，可能丢失工作）
```

### 无变更时

```
## Git 状态

当前分支：{branch}
状态：干净
```

---

## Step 7: 会话恢复检查

扫描 `specs/changes/*/todo.md` 查找未完成任务：

```
## 发现未完成的会话

| 会话 | 类型 | 阶段 | 上次步骤 |
|------|------|------|---------|
| {session_1} | {type} | {phase} | {step} |

选项：
1. 恢复会话 → 询问选择哪个会话
2. 忽略，开始新会话
3. 取消初始化
```

**如果无未完成任务：** 继续 Step 8

---

## Step 8: 写入初始化标记

### 8-1: 创建 specs/initialized.flag


### 8-2: 写入 {PROJECT_ROOT}/README.md 配置摘要

在项目 README.md 末尾追加：

```markdown
---

## Migbot-Increment Configuration

> Generated by migbot-increment-init. Do not edit manually.

### Project
- **Project Root**: `{PROJECT_ROOT}`
- **Spec Changes**: `{CHANGES_ROOT}`
- **Spec Feature Root**: `{SPECS_FEATURE_ROOT}`
- **Test Root**: `{TEST_ROOT}`

### Environment
| Tool | Path | Version |
|------|------|---------|
| hvigorw | {hvigorw_path} | {version} |
| SDK | {sdk_path} | {sdk_version} |

### SDK
| Variable | Path |
|---------|------|
| SDK_HOME | {sdk_path} |

### Test
- **Command**: `hvigorw test@entry`
- **Skills**: harmony-ui-test

### Commands
```bash
# Build
hvigorw assembleHap

# Test
hvigorw test@entry
```
```

---

## Step 9: 初始化完成

```
## ✅ Initialization Complete

**Project:** {PROJECT_ROOT}
**Build Tool:** {build_tool} {version}
**Test:** {test_available}
**Status:** Ready

**Configuration saved:**
- specs/initialized.flag
- {PROJECT_ROOT}/README.md

---

## Next Steps

### 开始新任务
$migbot-increment-workflow add <feature-name>

### 继续未完成任务
$migbot-increment-workflow continue

### 归档已完成任务
$migbot-increment-archive
```

---

## 防护栏

### 环境检查循环机制

**核心原则**：环境检查失败时，必须修复后才能继续，不能跳过。

```
环境检查失败？
    ↓
显示错误详情和修复建议
    ↓
询问用户将如何修复
    ↓
等待用户修复
    ↓
重新检查 ←──┐
    │      │
    ├──通过─┴──→ 继续下一步
    │
    └──失败 → 显示新错误，继续循环
```

### 强制执行要求

| 检查项 | 级别 | 失败处理 | 循环机制 |
|--------|------|---------|---------|
| PROJECT_ROOT | BLOCK | 必须指定有效路径 | 直到路径存在 |
| 构建工具版本 | BLOCK | 必须修复安装问题 | 直到版本检查通过 |
| 编译测试 | BLOCK | 必须修复编译错误 | 直到编译成功 |
| TEST_ROOT | BLOCK | 必须指定或创建目录 | 直到目录存在/确认 |
| 测试框架 | WARN | 必须选择后备方案 | 直到用户确认方案 |

### 禁止事项

1. **禁止跳过环境检查** — 所有检查项必须执行
2. **禁止跳过修复循环** — BLOCK 类错误必须修复，不能绕过
3. **禁止使用未确认的路径** — 所有路径必须验证存在
4. **禁止修改已存在的 initialized.flag** — 除非用户明确要求重新初始化

---

## 参考文件

- `references/checks.md` — 详细检查规格和失败处理
