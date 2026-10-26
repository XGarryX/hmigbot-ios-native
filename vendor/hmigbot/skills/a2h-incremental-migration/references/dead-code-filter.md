# §2.6 死代码过滤（references 详细版）

主 SKILL.md §2.6 的详细执行手册。所有扫描模式共享，**必跑**。

## 1. 为什么必跑

Android 项目里常有"看起来在那里但运行时不会执行"的代码。直接迁移这些 = 让 evolver 在 HMOS 端真造一个永远不会被用户感知的功能 = 浪费 + 污染 baseline。

**死代码污染 vs 漏报 的代价对比**：
- 漏报：用户在 §S2 看到"漏了 X"会主动补充（轻）
- 误报死代码：evolver 走完完整 create→plan→execute→verify 才发现 HMOS 实现的是永远跑不到的功能，浪费 ≥30 分钟 + 污染 spec/features/ 目录（重）

## 2. 死代码定义（5 种）

**绝对禁止**进入 A_CLOSURE / 行为轨迹清单 / §S2 差异清单：

| 类型 | 识别特征 | 例 |
|------|---------|----|
| 注释代码 | `//` 或 `/* */` 包裹 | `// fun uploadWork() { picker.show() }` |
| 已废弃 | `@Deprecated` / `@deprecated` 注解，或 KDoc / Javadoc 含 `@deprecated` | `@Deprecated("use uploadWorkV2") fun uploadWork()` |
| 死分支 | `if (false) { ... }` / `if (BuildConfig.DEBUG && false) { ... }` / `when { false -> ... }` | `if (false) { showOldDialog() }` |
| Feature flag 关闭 | 常量级 flag 在配置中为 `false`（编译期可推出永不进入）| `if (FeatureFlags.UPLOAD_ENABLED) { ... }` 而 `UPLOAD_ENABLED = false` |
| TODO 占位 | 函数体只有 `TODO("not implemented")` / `throw NotImplementedError()` / 空函数体 + `// TODO 实现` | `fun uploadWork() { TODO() }` |

## 3. 三模式过滤要求

### §M1 Final-state 优先 + commit 辅助 模式

- final state 阅读时（§M1.3 Step 1）：直接忽略上述 5 类
- commit 辅助校准时（§M1.3 Step 2）：diff 中 `+` 行如果是纯注释（`+ // ...` / `+ /* */`），不计入"新增行为"
- diff 中删除注释代码（`- // ...`）**绝对不算**功能下线（注释代码本来就不是活功能）
- 命令层面：`git diff` 结果用 `grep -v -E '^\+\s*(//|/\*|\*)'` 过滤注释行后再做行为归并

### §M2 Source-compare 模式

- LLM 并排阅读源码时，prompt 必须显式声明：
  > 「忽略所有 `//` `/* */` 注释、`@Deprecated` 函数、`if(false)` 死分支、feature flag 关闭的代码块——这些不构成用户可感知行为」
- 资源层符号差集（§M2.4）：strings.xml 的 `<!-- -->` 注释 key 必须先剔除再做差集

### §M3 Targeted 模式（**最易踩坑**）

```bash
# ❌ 旧错法：grep 命中注释行也会进 A_CLOSURE
grep -rlE "$KW" {android_dir}/app/src/main/

# ✅ 必须：剥离注释后再判命中
grep -rlE "$KW" {android_dir}/app/src/main/ | while read -r f; do
  python3 -c "
import re, sys
src = open(sys.argv[1]).read()
src = re.sub(r'//.*', '', src)                              # 剥离单行注释
src = re.sub(r'/\*.*?\*/', '', src, flags=re.DOTALL)        # 剥离多行注释
if re.search(sys.argv[2], src):
  print(sys.argv[1])
" "$f" "$KW"
done > /tmp/a_files_filtered.txt
```

A_CLOSURE 必须基于过滤后的命中文件构建。如果关键词**只**命中注释 → A_CLOSURE 等价于空 → 直接走 §M3.1.1 硬闸门"Android 无对应实现"路径。

## 4. 边界 case：被注释但马上要恢复的代码

如果 Android 端有一段代码刚被注释掉（开发者明确表示"暂时禁用，下版本恢复"），**不应**当死代码处理。

**判断方法**：
- 看 git blame：注释化提交是否是最近 1-2 个 commit
- 看 commit message：是否含 "temporarily disable / 暂时屏蔽 / WIP" 等暗示

满足条件 → 在 §S2 差异清单标注 `⚠ Android 端暂时禁用，迁移待定`，**不**自动入 🔴/🟠 桶，由用户决定是否同步。
