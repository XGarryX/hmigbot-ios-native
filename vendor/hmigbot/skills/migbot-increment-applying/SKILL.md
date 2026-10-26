---
name: migbot-increment-applying
description: |
  Migbot-Increment APPLYING 阶段 skill，用于代码应用与测试。
  当用户说"执行 migbot-increment-applying"、"应用代码"、"测试xxx"或类似表述时触发。
  本 skill 负责 APPLYING 阶段的所有工作：代码应用、单元测试、lint 检查、产出应用报告。
---

# migbot-increment-applying Skill

## 概述

本 skill 实现 Migbot-Increment APPLYING 阶段，负责将开发完成的代码应用到项目并进行测试验证。

```
APPLYING 阶段流程：
step3-0（环境检查）→ step3-1（确认应用条件）→ step3-2（代码应用）→ step3-3（更新任务状态）→ step3-4（产出应用报告）
```

## 使用方法

```
执行 migbot-increment-applying {类型}-{名称}
应用 {功能名称} 的代码
测试 {功能名称} 功能
```

---

## 前置条件

进入 APPLYING 阶段前，确认以下条件已满足：
1. IMPLEMENTING 阶段已完成
2. 代码已完成开发
3. 所有 tasks.md 中的任务已完成

---

## 全局约束

### 1. TodoWrite 管理

**注意**：TodoWrite 由编排层 migbot-increment-workflow 统一管理，本 skill 不使用 TodoWrite 工具。

### 2. todo.md 文件同步

在每个 step 完成后，同步更新 `{CHANGES_ROOT}/{YYYYMMDD}-{类型}-{名称}/todo.md` 文件，记录当前进度。

### 3. 测试要求

- 单元测试必须通过
- Lint 检查必须通过
- 如有集成测试，也需要通过

### 4. 代码质量

确保代码符合项目规范：
- 遵循导入顺序规范
- 遵循命名规范
- 无安全隐患

---

## step3-0：环境检查

**目的**：确保编译和测试环境就绪，避免在 APPLYING 过程中因环境问题中断。

**原则**：根据项目类型自适应检查，不硬编码特定工具。

### step3-0-1：检测项目类型

检查项目根目录下存在哪些构建文件来确定项目类型：

| 构建文件 | 项目类型 | 编译命令 | 测试命令 |
|---------|---------|---------|---------|
| `hvigorw` | HarmonyOS | `hvigorw assembleHap` | `hvigorw test@entry` |
| `package.json` | Node/JS/TS | `npm run build` | `npm test` |
| `gradlew` | Gradle/Android | `gradlew assembleDebug` | `gradlew test` |
| `pom.xml` / `build.gradle` | Maven/Java/Kotlin | `mvn compile` / `gradle compileJava` | `mvn test` / `gradle test` |
| `Cargo.toml` | Rust | `cargo build` | `cargo test` |
| `Makefile` | C/C++ | `make` | `make test` |
| 其他 | 未知类型 | 询问用户 | 询问用户 |

**操作**：
1. 检查项目根目录下的构建文件
2. 识别项目类型
3. 记录对应的编译和测试命令
4. 如果无法识别，询问用户使用的构建工具

### step3-0-2：检查编译环境

根据检测到的项目类型，运行对应的版本检查命令：

| 项目类型 | 检查命令 | 成功标准 |
|---------|---------|---------|
| HarmonyOS | `hvigorw --version` | 输出版本号 |
| Node/JS/TS | `node --version && npm --version` | 输出版本号 |
| Gradle | `gradlew --version` | 输出版本号 |
| Maven | `mvn --version` | 输出版本号 |
| Rust | `cargo --version` | 输出版本号 |
| C/C++ | `make --version` | 输出版本号 |
| 未知 | 询问用户 | 用户提供命令 |

**检查项**：
- 命令是否可用
- 版本号是否正常显示

### step3-0-3：尝试编译项目

运行编译命令确认项目可构建：

| 项目类型 | 编译命令 | 成功标准 |
|---------|---------|---------|
| HarmonyOS | `hvigorw assembleHap` | BUILD SUCCESS |
| Node/JS/TS | `npm run build` | 退出码 0 |
| Gradle | `gradlew assembleDebug` | BUILD SUCCESSFUL |
| Maven | `mvn compile` | BUILD SUCCESS |
| Rust | `cargo build` | 退出码 0 |
| C/C++ | `make` | 退出码 0 |
| 未知 | 询问用户 | 用户确认 |

**检查项**：
- 项目能否成功编译
- 是否有编译错误

### step3-0-4：检查测试环境

运行测试命令确认测试框架可用：

| 项目类型 | 测试命令 | 成功标准 |
|---------|---------|---------|
| HarmonyOS | `hvigorw test@entry --help` | 输出帮助信息 |
| Node/JS/TS | `npm test -- --help` 或 `jest --version` | 输出版本或帮助 |
| Gradle | `gradlew test --help` | 输出帮助信息 |
| Maven | `mvn test --help` | 输出帮助信息 |
| Rust | `cargo test --help` | 输出帮助信息 |
| C/C++ | `make test` 或检查 Makefile | 目标存在 |
| 未知 | 询问用户 | 用户提供命令 |

**HarmonyOS 特殊说明**：
- CLI 测试在 Linux 环境下不支持，需使用 Windows/macOS
- 如需 UI 测试支持，可使用 `skill('harmonyos-ui-test')`

**检查项**：
- 测试命令是否可用
- Linux 环境下 CLI 测试不支持

### step3-0-5：环境问题处理

如果环境检查失败：

**选项 1：用户可解决**
- 提示用户："编译/测试环境未就绪，请先配置"
- 列出需要解决的问题
- 等待用户确认环境就绪后再继续

**选项 2：环境限制**
- 如果项目在 Linux 环境下且 CLI 测试不可用
- 询问用户："是否在 Windows/macOS 环境下进行测试？"
- 或记录为遗留问题

**选项 3：未知项目类型**
- 询问用户使用的构建工具和测试框架
- 记录用户提供的命令
- 根据用户输入执行检查

**重要**：不要跳过环境检查。进入 step3-2（TDD 代码应用）前必须确保环境就绪。

---

## step3-1：确认应用条件

### step3-1-1：检查代码完成状态

确认以下条件已满足：
1. 代码已完成开发
2. 所有 tasks.md 中的任务已完成
3. 代码已按设计文档实现

### step3-1-2：检查代码质量

在应用前，运行以下检查：
1. 代码 lint 检查
2. 语法检查

如果检查未通过，**必须先修复问题**，然后继续。

---

## step3-2：代码应用

### step3-2-1：按照 tasks.md 执行代码生成/修改（TDD 模式）

**约束**：必须使用 `skill('tdd-enforcer')`

按照 tasks.md 中定义的任务顺序，对每个 task 执行 TDD 循环：

```
对每个 task:
  1. RED：根据验收标准写失败测试
  2. 验证测试失败
  3. GREEN：写最小代码使测试通过
  4. 验证测试通过
  5. REFACTOR：重构，保持测试绿色
  6. 进入下一个 task
```

执行顺序仍遵循：
1. 基础设施代码
2. 核心业务逻辑代码
3. UI 表现层代码

### step3-2-2：运行全量测试

所有 task 完成后，运行全量测试确认无回归：

```bash
cd {项目名}-main
hvigorw test@entry
```

### step3-2-3：执行 lint 检查

执行代码 lint 检查：

```bash
cd {项目名}-main
hvigorw lint
```

### step3-2-4：执行集成测试（如有）

如果有集成测试，执行集成测试验证各模块协作正常。

---

## step3-3：更新任务状态

更新 `{CHANGES_ROOT}/{YYYYMMDD}-{类型}-{名称}/todo.md`：
- 标记所有完成的任务
- 记录测试结果
- 记录 lint 检查结果
- 标记 APPLYING 阶段完成

---

## step3-4：产出应用报告

在 `{CHANGES_ROOT}/{YYYYMMDD}-{类型}-{名称}/apply-report.md` 中输出应用报告：

**参考模板**：`migbot-increment-applying/templates/apply-report-template.md`

### apply-report.md 结构

```markdown
# 应用报告

## 应用信息
- 变更类型：{类型}
- 变更名称：{名称}
- 关联特性：feat-{特性}
- 应用日期：{YYYY-MM-DD}

## 代码完成情况
| 任务 | 状态 | 完成时间 |
|------|------|----------|
| Task 1.1 | ✅ 完成 | {日期} |
| Task 1.2 | ✅ 完成 | {日期} |
| Task 2.1 | ✅ 完成 | {日期} |

## 测试结果
- 单元测试：{通过/未通过}
- 集成测试：{通过/未通过（如有）}
- Lint 检查：{通过/未通过}

## 测试详情
### 单元测试
{测试结果详情}

### Lint 检查
{检查结果详情}

## 下一步
测试通过后，执行归档操作：
执行 migbot-increment-archiving {类型}-{名称}
```

---

## APPLYING 阶段完成

**完成条件**：代码通过单元测试和 lint 检查

**完成动作**：
1. 更新 apply-report.md 测试结果
2. 更新 `{CHANGES_ROOT}/{YYYYMMDD}-{类型}-{名称}/todo.md` 状态（标记 APPLYING 完成）

**用户确认**：

```
## APPLYING 阶段完成

**产出物位置**：`{CHANGES_ROOT}/{YYYYMMDD}-{类型}-{名称}/apply-report.md`

**测试结果**：
- 单元测试：{通过/未通过}
- 集成测试：{通过/未通过（如有）}
- Lint 检查：{通过/未通过}

**代码完成情况**：
- Task 1.1: ✅ 完成
- Task 1.2: ✅ 完成
- Task 2.1: ✅ 完成

**请确认**：
- 代码应用和测试结果是否符合您的预期？
- 是否需要处理问题？

选项：
1. 接受，继续下一阶段
2. 处理问题（请说明需要处理的内容）
```

### 处理用户反馈

如果用户在确认时反馈问题：
1. 暂停继续执行
2. 听取并记录用户反馈的问题
3. 定位并修复问题
4. 重新运行测试验证
5. 更新 apply-report.md
6. 重新展示测试结果
7. 再次等待用户确认
8. 用户接受后继续执行下一阶段

**提示用户**：测试通过，可以进入achieving阶段进行归档


---

## 附录

### Skill 模板文件

模板文件位于 `migbot-increment-applying/templates/` 目录：

| 模板文件 | 用途 |
|----------|------|
| `apply-report-template.md` | 应用报告模板 |
| `todo-template.md` | 任务进度模板 |

### 构建/测试命令

在 `{项目名}-main/` 目录下执行：

```bash
# 构建
hvigorw assembleHap

# 测试
hvigorw test@entry

# Lint 检查
hvigorw lint
```

---

## Git Commit & Push（推荐）

当所有测试通过且 apply-report.md 已生成：

1. 向用户推荐：「建议提交并推送本次变更到远程分支，是否执行？」
2. 用户接受 → 执行：
   ```bash
   git add -A
   git commit -m "feat({name}): apply changes from migbot-increment-workflow"
   git push -u origin $(git branch --show-current)
   ```
3. 用户拒绝 → 跳过

**约束**：
- 仅在 `git_branch_adopted: true`（step1.5 中用户接受了分支推荐）时触发此推荐
- 如果用户在 main 分支上工作，不推荐此步骤
