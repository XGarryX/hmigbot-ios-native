<!-- when: $MULTI_MODULE=true（settings.gradle ≥2 模块 / 用户给多子仓路径 / 总 LOC ≥500k），执行 Phase 0 跨模块依赖桥接时加载 -->
<!-- topics: 多子仓, 跨模块依赖, module-dep-graph.json, cross-module-contracts.md, seam 接口签名, 分片生成, 子仓拓扑序, 成环退化, extract_module_deps.py -->

# Phase 0：多子仓 / 跨模块依赖桥接（仅 `$MULTI_MODULE=true` 触发）

**为什么需要**：超大仓**单次**生成会因上下文饱和而"产出收缩"（feature 数不随 LOC 扩张、主文件 500 行硬上限截断），导致严重欠规约；而单纯**按子仓分片**又会丢失跨子仓依赖（A 调 B 的接口、共享数据模型/序列化、事件/DI 绑定），译成错误逻辑。Phase 0 把**依赖发现**与**详情生成**解耦：依赖是结构化、稀疏的（签名、不是方法体），用脚本对全仓做一次"信号级"骨架提取（体量极小、可入上下文、且**穷尽**——静态分析无注意力预算，比 LLM 通读 1M LOC 更完整），再把该骨架注入每个子仓的分片生成。此模式复用本 skill 既有的"确定性脚本骨架 + LLM 语义补充"范式（同 Phase A 的 `synthesize_*.py`），只是换到"模块依赖"这一维度。

## Step P0.1 — 确定性脚本提取依赖骨架（脚本，非 LLM）

```bash
python3 .agents/skills/a2h-spec/scripts/extract_module_deps.py \
  --src $ANDROID_SRC \
  --out spec/baseline/module-dep-graph.json
# 若 settings.gradle 无法表达模块边界，可显式给子仓根：--modules path/a,path/b,path/c
```

脚本穷尽提取：
- **模块 DAG**：从 `settings.gradle` + 各模块 `build.gradle` 的 `implementation/api project(...)` 解析"允许依赖"有向图；
- **跨模块引用边**：跨模块 `import` + 类型引用（A 文件 import B 模块的类）→ 调用边 `caller_module → callee_module : Symbol`；
- **共享数据模型 / 序列化**：被 ≥2 模块引用的 `data class` / Protobuf / `@Serializable` / Parcelable 定义（跨模块若 spec 各写一套 → 反序列化错位，是"错误逻辑"高发区）；
- **seam 接口签名**：每条跨模块边被引用符号的公开签名（`class/interface + 方法签名 + 类型`，**仅签名不取方法体** → 紧凑可入上下文）。

## Step P0.2 — LLM 语义补充（在骨架上，不读原始 1M LOC）

读 `module-dep-graph.json`（紧凑），仅补静态分析看不到的耦合：事件/广播、DI / service-locator 绑定（A 经注入拿 B 实现，无直接 import）、intent / AIDL、反射；以及每条边的**语义契约**（前置/后置/可空/线程/副作用约束）。产出 `spec/baseline/cross-module-contracts.md`。

## Step P0.3 — 生成全局 feature-base + 全局 feature-index（跨子仓）

- 全局 `feature-base.md`：把**跨模块共享契约/模型/事件只规约一次**（seam owner 一侧权威），各子仓引用而非各写一套 → 从根上消除"两侧逻辑分叉"。
- 全局 `feature-index.md` 增加 `## 跨模块依赖图`（子仓级 DAG）+ `## 子仓执行顺序（拓扑排序）`：被依赖的子仓（叶/底座）先生成，其 seam 契约先就位。

## Step P0.4 — 分片生成（按拓扑序，注入依赖骨架）

对每个子仓按拓扑序跑 Phase A→C（详情完整、单子仓可入上下文），但向每个分片**注入**：
1. `module-dep-graph.json` 中**触及本子仓的边**；
2. 本子仓**依赖的其它子仓的 seam 接口桩**（仅签名，来自 P0.1）；
3. 全局 `feature-base.md` 的共享契约。

这样子仓 A 的 spec 能正确写出 `A.FooService → B.BarRepo.getX()` 的依赖与契约，而 A 的生成**无需通读 B 的内部实现**——既不丢依赖，又不撑爆上下文。

> **子仓依赖成环时**（实测多子仓常见：子仓间互相依赖，非 DAG）：拓扑序退化为"尽力而为"（脚本自动回退到稳定输入序），但**不阻断流程**——因为 P0.1 已用脚本把**所有**子仓的 seam 签名提前抽出（不依赖任何 spec），这些桩即"环的破点"：每个分片无论生成先后，都能拿到其依赖方的接口契约。故环上子仓正常分片生成，仅在 C4.6d 对环上 seam 重点核对两侧一致性。

## Step P0.5 — seam 一致性审计

每条跨模块边在两侧 spec 中契约一致（调用方假设 == 被调方暴露契约），详见 a2h-spec **Step C4.6d**（[c4-coverage-and-seam-audits.md](./c4-coverage-and-seam-audits.md)）。

---

**输出新增**：`spec/baseline/module-dep-graph.json`（P0.1 脚本）、`spec/baseline/cross-module-contracts.md`（P0.2）。单仓（`$MULTI_MODULE=false`）跳过整个 Phase 0。
