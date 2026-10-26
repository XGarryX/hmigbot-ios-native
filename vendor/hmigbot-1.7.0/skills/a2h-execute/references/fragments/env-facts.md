# env-facts — 环境事实（Windows + DevEco 目标机）

## 构建命令（唯一无头形态）
- 必须在**工程根目录**执行：
  `hvigorw.bat assembleHap --mode module -p product=default -p buildMode=debug --no-daemon`
- 构建锁：hvigor 不可并发——同一工程同一时刻只准一个构建进程（含 IDE 内构建）；并发即抢锁失败。派多个修复代理时编译统一由主循环/收口者发起。

## 环境变量
- `DEVECO_SDK_HOME`、`JAVA_HOME` 必须写入工程 `.codex/config.toml` 的 `env` 段（子代理 Bash 不继承 IDE 环境，缺了 hvigor 直接起不来）。
- PATH 前置垫入 DevEco `jbr/bin`（java）与 `tools/node`（node，hvigor 依赖）。

## 编码纪律
- 用户机 Windows Python 默认 cp1252：所有脚本 `open(..., encoding="utf-8")`，stdout 输出前 `sys.stdout.reconfigure(encoding="utf-8", errors="replace")`。
- 生成的一切文本产物一律 UTF-8（无 BOM）；路径用 pathlib，不手拼分隔符。

<!-- source: docs/skills_optimization_818/design/6_rollout.md Step 1 + 1_architecture.md §1.4 -->
