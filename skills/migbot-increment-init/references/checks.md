# migbot-increment-init Check Specifications

详细检查规格和失败处理定义。

---

## 检查项汇总

| # | 检查项 | 类型 | 优先级 | 失败处理 | 循环机制 |
|---|-------|------|--------|---------|---------|
| 1 | PROJECT_ROOT 存在性 | BLOCK | P0 | 必须指定新路径 | 直到存在 |
| 2 | 构建工具版本 | BLOCK | P0 | 必须修复安装 | 直到检查通过 |
| 3 | 编译测试 | BLOCK | P0 | 必须修复错误 | 直到编译成功 |
| 4 | TEST_ROOT 检测与确认 | BLOCK | P0 | 必须指定或创建 | 直到目录存在/确认 |
| 5 | 系统环境变量 | INFO | P1 | 询问用户提供 | 记录到配置 |
| 7 | 测试框架可用性 | WARN | P1 | 必须选择后备方案 | 直到确认方案 |

---

## 1. PROJECT_ROOT 存在性检查

### 检查逻辑

```bash
ls -la ./${PROJECT_NAME}-main/
```

### 失败处理（循环直到修复）

→ 参考 SKILL.md Step 2-2

---

## 2. 构建工具版本检查

### 检查命令

| 项目类型 | 检查命令 |
|---------|---------|
| HarmonyOS | `hvigorw --version` |
| Node.js | `node --version && npm --version` |

### 失败处理（循环直到修复）

→ 参考 SKILL.md Step 3-1

---

## 3. 编译测试

### 检查命令

| 项目类型 | 编译命令 | 超时 |
|---------|---------|------|
| HarmonyOS | `hvigorw assembleHap` | 10 分钟 |
| Node.js | `npm run build` | 5 分钟 |

### 失败处理（循环直到修复）

→ 参考 SKILL.md Step 3-2

---

## 4. TEST_ROOT 检测与确认

### 检测逻辑

按优先级检测：

1. `{PROJECT_ROOT}/entry/src/test/` — HarmonyOS 标准
2. `{PROJECT_ROOT}/test/`
3. `{PROJECT_ROOT}/entry/test/`
4. 扫描 `test/`、`tests/`、`__tests__/`、`*test*/`

### 检测到时

```
显示检测结果表格，包含：
| 路径 | 状态 | 文件数 |

目录预览：列出最多 5 个测试文件名
```

### 未检测到时

→ 参考 SKILL.md Step 3-3

---

## 5. 系统环境变量检查

### 检查的变量

| 变量 | 用途 | 检查命令 |
|------|------|---------|
| HARMONYOS_SDK_HOME | SDK 根目录 | `echo $HARMONYOS_SDK_HOME` |
| HARMONY_SDK_ROOT | SDK 根目录 | `echo $HARMONY_SDK_ROOT` |
| OHOS_SDK_ROOT | SDK 根目录 | `echo $OHOS_SDK_ROOT` |
| PATH | 系统路径 | `echo $PATH` |

### 用户提示

```
未检测到 SDK 路径。
请提供 SDK 根目录路径（或直接回车跳过）：
_
```

---

## 6. 重要路径检查

### 检查的路径

| 工具 | 验证方式 |
|------|---------|
| hvigorw | `which hvigorw` 或 `{SDK}/hvigorw --version` |
| SDK | 目录存在性检查 |

### 用户提示

```
| 工具 | 状态 |
|------|------|
| hvigorw | {✅/❌} |
| SDK | {⚠️ 未设置} |

请提供以下路径（如已知）：

SDK 根目录：_
hvigorw 路径：_
```

---

## 7. 测试框架可用性检查

### 检查命令

| 项目类型 | 检查命令 |
|---------|---------|
| HarmonyOS | `hvigorw test@entry --help` |
| Node.js | `jest --version` 或 `npm test -- --help` |

### 失败处理（必须选择后备方案）

→ 参考 SKILL.md Step 3-4

---

## 配置模板

### specs/initialized.flag

```markdown
## SDK Configuration
SDK_HOME: {sdk_path}
hvigorw Path: {hvigorw_path}

## User Provided Paths
SDK: {user_provided_sdk}
hvigorw: {user_provided_hvigorw}
```

### {PROJECT_ROOT}/README.md 配置摘要

```markdown
## Migbot-Increment Configuration

### Environment
| Tool | Path | Version |
|------|------|---------|
| hvigorw | {path} | {version} |
| SDK | {path} | {version} |

### Commands
```bash
hvigorw assembleHap
hvigorw test@entry
```
```
