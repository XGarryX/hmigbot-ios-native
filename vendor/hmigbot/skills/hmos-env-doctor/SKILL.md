---
name: hmos-env-doctor
description: HarmonyOS 开发环境检测与修复。在迁移、编译、运行 HarmonyOS 项目前自动诊断环境问题。当用户说"编译失败"、"环境有问题"、"hvigorw 找不到"、"签名错误"、"真机运行白屏"、"网络请求失败"、"检查一下环境"、"为什么编译不过"时触发。也适用于项目初始化后的环境健康检查、DevEco Studio CLI 编译配置、以及迁移前的环境预检。即使用户只说"帮我看看哪里有问题"或者"跑不起来"，也应触发。
metadata:
  type: tool
  domain: engineering
---
# HarmonyOS 环境医生

## 1. 定位

开发环境诊断工具。在 HarmonyOS 项目迁移或开发过程中，自动检测 DevEco Studio、SDK、编译工具链、签名配置、权限声明、网络环境等问题，输出诊断报告并提供一键修复方案。

**解决的核心痛点**：HarmonyOS 开发涉及多个工具链（hvigorw、ohpm、Java、Node.js、SDK），任何一个缺失或配置错误都会导致编译失败或运行异常，而错误信息往往不直观。本 skill 将散落的环境知识整合为系统化的检查清单。

---

## 2. 触发时机

- 项目初始化后，首次尝试编译前
- 编译失败且错误信息指向环境问题
- 真机/模拟器运行出现白屏、闪退、网络失败
- Android→HarmonyOS 迁移开始前的环境预检
- 用户主动请求环境检查

---

## 3. 诊断清单（按优先级排序）

### 3.0 先跑机械体检脚本（**必跑，其余小节是它的解释与兜底**）

```bash
python3 $SKILLS_ROOT/hmos-env-doctor/scripts/env_doctor.py --project <鸿蒙工程根> --markdown spec/env-report.md
#   exit 0 = 全 PASS（WARN 不影响）   1 = 有 FAIL   2 = 脚本异常
#   stderr 人类可读表；stdout JSON；--markdown 落 §4 格式报告
```

它一次跑完 §3.1–3.6：DevEco 定位（三平台**固定候选位**，不递归搜盘）、工具链版本（hvigorw/ohpm/java/node，
各 15s 硬超时）、设备在线（hdc/adb，各 10s 硬超时，区分"未找到 / 超时 / 有工具无设备"）、签名路径存在性与
是否指向别的机器、module.json5 权限、Python 版本。**1–2 秒出结果。**

> 为什么先跑它（2026-08-17）：本 skill 此前零脚本，模型对着下面的清单自主执行——Windows 上 `find`/`dir /s`
> 搜盘找 DevEco、`hdc list targets` 无超时挂死、每条命令一次往返，用户实报 20+ 分钟无结果。
> **脚本报 FAIL 的项才需要你按下面各小节的"修复"动手；PASS 的项不要再手动复查一遍。**
> 排障时读 JSON 里对应 check 的 `detail` / `hint`，别自己重新 `which`。


### 3.1 DevEco Studio 定位

DevEco Studio 是 HarmonyOS 开发的核心 IDE，内置了编译、打包、签名所需的全部工具。

**检测步骤**：由 `env_doctor.py` 的 `check_deveco()` 完成——按 env `DEVECO_HOME`/`DEVECO_SDK_HOME` →
平台固定安装位（macOS `/Applications/DevEco-Studio.app/Contents`；Windows `%ProgramFiles%\Huawei\DevEco Studio`
/ `D:\Program Files\Huawei\DevEco Studio` / `%LOCALAPPDATA%\Huawei\Sdk`；Linux `~/command-line-tools` /
`/opt/deveco-studio`）逐个 `isdir`。**不要 `find /` 或 `dir /s` 全盘搜**——那正是 20 分钟的来源；
候选位都没有就让用户设 `DEVECO_HOME`。

**需要从 DevEco Studio 中提取的工具**：
| 工具 | 相对路径 | 用途 |
|------|---------|------|
| hvigorw | tools/hvigor/bin/hvigorw | 项目编译 |
| ohpm | tools/ohpm/bin/ohpm | 包管理 |
| java | jbr/bin/java | Java 运行时（打包需要） |
| node | tools/node/bin/node | Node.js 运行时 |
| SDK | sdk/default/openharmony/ | HarmonyOS SDK |

**环境变量设置模板**：
```bash
export DEVECO_HOME="/path/to/DevEco Studio"
export PATH="$DEVECO_HOME/tools/hvigor/bin:$DEVECO_HOME/tools/ohpm/bin:$DEVECO_HOME/jbr/bin:$PATH"
export DEVECO_SDK_HOME="$DEVECO_HOME/sdk"
export JAVA_HOME="$DEVECO_HOME/jbr"
```

**诊断结果**：
- PASS: DevEco Studio 找到，工具链完整
- FAIL: 未找到 → 提示安装 DevEco Studio
- WARN: 找到但版本过旧 → 提示升级

### 3.2 编译工具链验证

定位到 DevEco Studio 后，验证各工具是否可用：

```bash
hvigorw --version    # 期望: 6.x.x
ohpm --version       # 期望: 有输出
java --version       # 期望: JDK 17+
node --version       # 期望: v18+
```

**常见故障**：
| 错误信息 | 原因 | 修复 |
|---------|------|------|
| `hvigorw: command not found` | PATH 未设置 | 添加 DevEco tools/hvigor/bin 到 PATH |
| `spawn java ENOENT` | Java 不在 PATH | 添加 DevEco jbr/bin 到 PATH |
| `Cannot find module 'xxx'` | node_modules 缺失 | 运行 `ohpm install` |

### 3.3 签名配置检查

签名问题是 HarmonyOS 编译中最常见的环境卡点。

**检测步骤**：
1. 读取 `build-profile.json5` 中的 `signingConfigs`
2. 检查 `storeFile`、`certpath`、`profile` 路径是否在本机存在
3. 如果路径指向其他用户目录（如 `/Users/xxx/`）→ 签名配置来自其他机器

**修复策略（按优先级）**：
1. **方案 A**: 在 DevEco Studio 中重新配置自动签名（File → Project Structure → Signing Configs）
2. **方案 B**: 移除 `signingConfig` 引用，生成 unsigned HAP（开发调试用）
   ```json5
   // build-profile.json5 中移除这一行:
   // "signingConfig": "default",
   ```
3. **方案 C**: 手动创建签名文件（生产发布用）

**判断逻辑**：
- 路径存在 + 文件有效 → PASS
- 路径不存在但为本机路径 → FAIL: 签名文件缺失
- 路径指向其他用户/机器 → FAIL: 签名配置来自其他环境
- 无 signingConfigs 字段 → WARN: 将生成 unsigned HAP

### 3.4 Python 环境（可选工具）

部分迁移脚本（synthesize_view_xml.py 等）需要 Python。

```bash
python3 --version || python --version
```

**缺失时的影响和降级策略**：
- 影响: 无法运行确定性脚本合成 view.xml，页面 confidence 降为 medium
- 降级: LLM 直接分析源码生成 meta.json（精度略低但可用）
- 建议: 安装 Python 3.8+ 可提升 UI 还原精度

### 3.5 项目配置检查

**module.json5 权限声明**：
```bash
grep -q "ohos.permission.INTERNET" entry/src/main/module.json5
```

缺少 INTERNET 权限是真机上网络请求静默失败的最常见原因。

**必须声明的权限**（网络类应用）：
```json5
"requestPermissions": [
  { "name": "ohos.permission.INTERNET" },
  { "name": "ohos.permission.GET_NETWORK_INFO" }
]
```

**app.json5 身份检查**：
- `bundleName` 不应为 `com.example.*`（模板默认值）
- `vendor` 不应为 `example`
- 检查 `versionName` 是否已从 Android 同步

**main_pages.json 入口检查**：
- 检查 `src` 数组第一项是否指向实际的启动页（不是默认的 `pages/Index`）
- 检查 EntryAbility.ets 中 `loadContent` 路径与 main_pages.json 首项一致

### 3.6 真机/模拟器运行时问题

当应用编译通过但运行异常时，检查以下项：

**白屏/内容为空**：
- 原因 1: `aboutToAppear` 中 async 调用失败，状态变量（`@Local` V2 / `@State` V1）保持初始空值
  - 检查: grep "aboutToAppear" 中的 async 调用，是否有同步 fallback
  - 修复: 关键展示数据同步初始化，async 作为增强
- 原因 2: ForEach 未提供 key generator，class 实例 key 冲突
  - 检查: grep "ForEach" 是否有第三个参数（key generator）
  - 修复: 添加 `(item) => item.uniqueId` 作为 key generator
- 原因 3: 网络权限缺失，API 请求静默失败
  - 检查: module.json5 是否有 INTERNET 权限

**闪退**：
- 原因 1: crypto API 在某些设备上不可用
  - 检查: 是否使用了 cryptoFramework 且未 try-catch
  - 修复: crypto 调用必须有 try-catch + fallback
- 原因 2: 未注册的页面路由
  - 检查: main_pages.json 是否包含所有页面
  - 修复: 确保每个 @Entry 页面都在 src 数组中

**网络请求失败**：
- 原因 1: 缺少 INTERNET 权限
- 原因 2: HTTP 明文传输被阻止（需配置 network_security_config）
- 原因 3: API 域名不可达（检查 DNS/代理）

### 3.7 子 Agent 权限（Codex 特有）

使用 a2h-* pipeline 时，子 agent 可能无法访问 Android 源码目录。

**检测**：子 agent 是否能读取 `$ANDROID_SRC` 路径下的文件。

**修复**：
- 方案 A: 在 Codex settings 中添加 allowedDirectories
- 方案 B: 将 Android 源码复制到工作目录下
- 方案 C: 主会话 fallback（效率低但可用）

---

## 4. 诊断报告格式

```markdown
# 环境诊断报告

| 检查项 | 状态 | 详情 |
|--------|------|------|
| DevEco Studio | PASS/FAIL | 路径: xxx, 版本: xxx |
| hvigorw | PASS/FAIL | 版本: xxx |
| Java | PASS/FAIL | 版本: xxx |
| Node.js | PASS/FAIL | 版本: xxx |
| Python | PASS/WARN | 版本: xxx (可选) |
| 签名配置 | PASS/FAIL/WARN | 状态描述 |
| 网络权限 | PASS/FAIL | module.json5 |
| App 身份 | PASS/WARN | bundleName/vendor |
| 入口页面 | PASS/FAIL | main_pages.json + EntryAbility |

## 需要修复的项
1. ...
2. ...

## 修复命令
(自动生成的修复脚本)
```

---

## 5. 自动修复能力

对于可安全自动修复的问题，skill 直接执行修复：

| 问题 | 自动修复 | 操作 |
|------|---------|------|
| PATH 未设置 | YES | 输出 export 命令 |
| 缺少 INTERNET 权限 | YES | 追加到 module.json5 |
| 签名指向其他机器 | YES | 移除 signingConfig 引用 |
| main_pages.json 入口错误 | YES | 更新 src 数组 |
| bundleName 为模板默认值 | ASK | 提示用户输入正确的包名 |
| Python 缺失 | NO | 提示安装命令 |
| DevEco Studio 缺失 | NO | 提示下载链接 |

---

## 6. 使用示例

```
检查一下环境
```
→ 运行完整诊断清单，输出报告

```
编译失败了，spawn java ENOENT
```
→ 定位 Java 问题，输出 PATH 修复命令

```
真机上模版列表是空的
```
→ 检查网络权限 + async fallback + ForEach key

```
开始迁移前先检查一下
```
→ 运行预检清单（DevEco + 签名 + Python + 权限）
