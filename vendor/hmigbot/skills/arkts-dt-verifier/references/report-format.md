# 实现率报告格式

> **⚠️ v2 重要变更（已应用）**：
> - 移除 `_systemic/SYSTEMIC_*.md` 子目录与 SYSTEMIC kind 枚举
> - 每个失败 it() / 视觉差异 = 一个独立文件，**不再做 systemic 聚类**
> - 移除回滚机制（REGRESSED 仅记录，不触发 git reset）
> 下面文档若仍含 SYSTEMIC 或 `_systemic/` 字样，按 v2 schema 生成时**忽略它们**

第五步跑完测试后，主线程产出**两类输出**：

```
docs/
└── dt-verification-report.md            ← 人类阅读版（单文件，本文档定义）

spec/fix/round-{N}/
├── _index.md                            ← 本轮所有问题清单
├── _summary.md                          ← 本轮统计 + 维度分布
├── _delta.md                            ← 与 round-{N-1} 对比（round-1+）
├── feat/
│   └── <id>.md                          ← 单问题文件（schema 见 fix-file-schema.md）
└── ui/
    └── <id>.md
```

| 文件 | 用途 | 读者 | Schema |
|------|------|------|--------|
| `docs/dt-verification-report.md` | **人类阅读版** — 汇总率、维度分布、Top 10 问题 | review 会议、迁移验收方 | 本文档 |
| `spec/fix/round-{N}/{feat,ui}/<id>.md` | **单问题文件** — fixer 修代码用 | a2h-fixer agent、人工开发 | `fix-file-schema.md` |
| `spec/fix/round-{N}/_index.md` | **问题清单速览** | 人类速看 | `fix-file-schema.md §八` |
| `spec/fix/round-{N}/_summary.md` | **本轮统计** | 人类 | 同上 |
| `spec/fix/round-{N}/_delta.md` | **vs 上轮对比** | autofix 收敛判定 | `reconcile-rules.md §四` |

> **与旧版对比**：旧版产出 `docs/dt-fix/feature.md` + `docs/dt-fix/ui.md` 两个大 markdown，全部 RED/ERROR 都展开在同一文件里。新版每个 RED/ERROR/DIFF/SYSTEMIC 都是一个独立 markdown 文件，便于 fixer 按文件粒度分批修复 + autofix 通过目录差异跨轮对比。**不再产出旧 feature.md / ui.md**。

---

## 数据来源

- 用例层：`entry/src/ohosTest/ets/test/tdd-ac-index.md` 的两组表格（Feature 主表 + Page 来源节），`运行结果` 列由第五步写入
- 运行层：`aa test` 的 stdout（汇总行 + 逐用例行），必须 "runtime verified on device"
- Spec 原文：`spec/baseline/features/F*.md` + `spec/baseline/ui/page_*.md`
- 源码定位：对 RED/ERROR/DIFF 条目读 `entry/src/main/ets/` 对应实现文件，抽出缺口所在文件/行号（用于单问题文件 §4 源码缺口）
- 上轮快照（round ≥ 1）：`spec/fix/round-{N-1}/` 全部文件 frontmatter（用于 carry forward）

---

## 一、人类阅读版 `docs/dt-verification-report.md`

**风格**：高密度信息 + 一屏可读。**不展开逐条 it()**（避免过长）—— 逐条清单去 `spec/fix/round-{N}/{feat,ui}/<id>.md`。

### 模板

```markdown
# Spec 功能验证报告

> runtime verified on device
> 生成时间：YYYY-MM-DDTHH:mm:ss+08:00
> 设备：<device_id>  Bundle：<bundle_name>
> MockKit 策略：full | weak | deferred
> 当前轮次：round-{N}
> 配套问题清单：`spec/fix/round-{N}/_index.md`（速览）+ `spec/fix/round-{N}/{feat,ui}/<id>.md`（逐问题）

## 1. 执行概要（≤ 5 行）

- 构建：主 HAP + 测试 HAP 编译通过（轮数：{N}）
- 安装：`hdc install` 成功
- `aa test` 原始汇总：`Tests run: N, Failures: F, Errors: E, Skipped: S`
- 本轮耗时：约 {mm} 分钟

## 2. 实现质量两个维度（区分通过率 vs 覆盖率）

### 2.1 Spec 功能覆盖率（结构维度 — 测试是否触达 spec 行为）

| 维度 | 已实装 | 未实装 | 不可达 | Spec AC 总数 | Spec 覆盖率 |
|------|-------|-------|--------|--------------|------------|
| 逻辑层（unit） | {uimpl} | {umiss} | 0 | {utotal} | {ucov}% |
| UI 层（ui）    | {iimpl} | {imiss} | {iunr} | {itotal} | {icov}% |
| 总体           | {timpl} | {tmiss} | {tunr} | {ttotal} | {tcov}% |

> "已实装" = AC 索引中状态 = pure_function / mockkit / manifest_id / type / manifest_string / type_fallback
> "未实装" = AC 索引中状态 = todo (unit) / impl_missing (ui)
> "不可达" = depends_on_intent / external_intent / external_picker / platform_limit
> **Spec 覆盖率 = 已实装 / (已实装 + 未实装)**，不可达不计入分母

### 2.2 通过率（运行维度 — 已触达的测试是否通过）

| 维度 | GREEN | 真实运行总数 | 通过率 | RED | ERROR | 变化 vs 上轮 |
|------|-------|------------|--------|-----|-------|-------------|
| 逻辑层（unit） | {ug} | {ureal} | {ur}% | {urd} | {uer} | {±x%} |
| UI 层（ui）    | {ig} | {ireal} | {ir}% | {ird} | {ier} | {±x%} |
| 总体           | {tg} | {treal} | {tr}% | {trd} | {ter} | {±x%} |

> "真实运行总数" = 全部 it() − IMPL_MISSING 占位 − UNREACHABLE 占位 − skipped-compile − deferred
> "通过率 = GREEN / 真实运行总数"
> "变化 vs 上轮"：从 `spec/fix/_state.yaml` 找上轮 round 号，读上轮报告 §2.2 对比

### 2.3 实现率演进（跨轮快照，feat 与 UI 分开）

> 设计要点：合并展示掩盖层间分化（如 feat 卡 75% / UI 涨到 88%），各层数据必须独立列。

**feat 层（{feat_total} 个 it()）**：

| 轮次 | feat PASS | feat 失败 | feat 通过率 | 本轮变化 |
|---|---|---|---|---|
| round-0 (baseline) | x | y | x/total% | - |
| round-1 | x | y | x/total% | +N（一句话归因，如"修了 7 个 ERROR：DB init / setSpeed 等"）|
| ... | | | | |
| **round-{当前}** | x | y | x/total% | ±N |

**UI 层（{ui_total} 个 it()）**：

| 轮次 | UI PASS | UI 失败 | UI 通过率 | 本轮变化 |
|---|---|---|---|---|
| round-0 (baseline) | x | y | x/total% | - |
| ... | | | | |

**总计（{total} 个 it()）**：

| 轮次 | 总 PASS | 总失败 | 总通过率 | RESOLVED 本轮 | NEWLY_OPEN | REGRESSED |
|---|---|---|---|---|---|---|
| ... | | | | | | |

**端到端改进（round-0 → 当前）**：

| 维度 | round-0 | round-{当前} | 增量 |
|---|---|---|---|
| feat PASS | x / total | x / total | +N pp |
| UI PASS | x / total | x / total | +N pp |
| 总 PASS | x / total | x / total | +N pp |

**写表规则（必读）**：
- 分子分母用所在层总数（feat=spec unit AC 总数，UI=spec ui AC 总数），别用合计 it() 数除两边
- 通过率小数 1 位（如 75.3%），增量小数 1 位 + `pp` 单位（如 +7.3pp）
- "本轮变化"列必须给一句话归因，不只列数字（"+22"❌ vs "+22（路由补全 / bindMenu value / toolbar 标题等）"✅）

### 2.4 阅读约定（防误读）

- 例：spec 100 条 AC，写了 50 条有效测试 + 30 条 IMPL_MISSING 占位 + 20 条 UNREACHABLE → Spec 覆盖率 = 50/(50+30) = 62.5%；不可达 20 不计入
- 50 条有效测试中 40 条 GREEN → 通过率 = 40/50 = 80%
- **绝不要把 80% 误读为 "spec 实现 80%"** —— 真实 spec 实现 = 覆盖率 × 通过率 = 62.5% × 80% = **50%**
- 只有"覆盖率高 + 通过率高"两个数都高才能宣告 spec 实现良好

## 3. Feature 维度表（一行一 Feature）

| Feature | 逻辑 G/T | UI G/T | 实现率 | 状态 |
|---------|---------|--------|--------|------|
| F001 media-scan | 4/5 | 3/4 | 77.8% | 🟡 |
| F004 favorites | 0/7 | 0/3 | 0% | 🔴 |

状态判定：实现率 ≥ 80% → 🟢；40%–80% → 🟡；< 40% → 🔴

## 4. 页面维度表（一行一 Page）

| Page | SMOKE | COMP | NAV | INTERACT | FEATURE_DERIVED | 总 G/T | 状态 |
|------|-------|------|-----|----------|-----------------|--------|------|
| P0002 MainPage | 1/1 | 3/4 | 2/2 | 1/3 | 1/2 | 8/12 | 🟡 |

## 5. Top 10 问题（按修复收益排序）

按"阻塞 Feature/页面数 × 关联失败用例数"排序。每行一条，简述 + 指向单问题文件：

1. [SYSTEMIC db-init Context 缺失](../spec/fix/round-{N}/feat/_systemic/SYSTEMIC_db-init-context-failure.md) — 阻塞 12 条 unit AC
2. [P0010 Toggle 全部 RED](../spec/fix/round-{N}/ui/_systemic/SYSTEMIC_settings-toggle-no-onchange.md) — 影响 45 条 INTERACT
3. ... (共 10 条)

## 6. 分类小结

- **逻辑层 RED 热点**：{1 行描述 + Feature 编号}（详见 `spec/fix/round-{N}/feat/`）
- **UI 层 RED/ERROR 热点**：{1 行描述 + Page 编号}（详见 `spec/fix/round-{N}/ui/`）
- **视觉对齐差异**：{N} 条 ALIGN_*.md（来自 visual-verify）
- **Deferred / weak**：{N} 条（策略 = {policy}）
- **不可达页**：{N} 个（P{list}） — 均为外部 Intent / Tab 子页 / Dialog-only

## 7. 证据片段（raw）

```
Tests run: 195, Failures: 82, Errors: 45, Skipped: 0
[FAIL] F004_AC03_toggle_persists_to_db — expected add called, got 0 calls
[ERROR] P0010_UI_INTERACT_toggle_autoplay_flips_checked — expect true, actualValue is false
… (最多 20 行)
```

## 8. 抽查校验

- GREEN 抽 10 条 → 读源码确认逻辑确实实现：{通过数}/10
- RED 抽 10 条 → 读单问题文件 §3 实际 + 源码确认确实未实装：{通过数}/10
- 两轮准确率 ≥ 90% → 报告置信度达标
```

### 硬性要求

1. 头部必标 `runtime verified on device` + 设备 ID + bundle + 时间戳 + `aa test` 原始汇总行 + `当前轮次：round-{N}`
2. **§2.1 覆盖率 + §2.2 通过率**两张表都要有
3. Feature 维度表 + 页面维度表都要有
4. Top 10 问题**按修复收益排序**，每条必带单问题文件链接（`spec/fix/round-{N}/...`）
5. **禁止**把逐条 it() 的完整清单塞进来（那是单问题文件的职责）
6. **禁止**只写聚合百分比而不出 Top 10 问题
7. **禁止**把 IMPL_MISSING 占位的 PASS 算入"已实装"或"通过率分子"

---

## 二、单问题文件 schema

详见 [`fix-file-schema.md`](./fix-file-schema.md) 与 [`fix-file-template.md`](./fix-file-template.md)。

要点：
- 一个 it() 失败（或一个视觉差异）= 一个 markdown 文件
- 文件名 = ID + .md（ID 推导规则见 `fix-file-schema.md §二`）
- 文件路径 = `spec/fix/round-{N}/<layer>/<id>.md`，systemic 在 `_systemic/` 子目录
- frontmatter + 6 个 section 正文，所有 verifier 共用同一 schema
- 跨轮的 disposition / related 由 carry forward 算法保留（`reconcile-rules.md §三`）；不维护历史尝试表（跨轮历史靠 round 目录序列承载）

---

## 三、`_index.md` / `_summary.md` / `_delta.md`

`_index.md` 与 `_summary.md` 模板见 [`fix-file-schema.md §八`](./fix-file-schema.md#八_indexmd-与-_summarymd-与-_deltamd)。

`_delta.md` 模板见 [`reconcile-rules.md §四`](./reconcile-rules.md#四_deltamd-生成算法)。

---

## 四、写文件流水线（Step 5 主线程执行顺序）

```
1. 跑完 aa test，回写 tdd-ac-index.md 的 运行结果 列
2. 解析 runtime_results: { id → GREEN | RED | ERROR | ALIGNMENT_DIFF }
3. 读 spec/fix/_state.yaml，取 current_round 作为 N
   （若 baseline 首跑 → N = 0；若 autofix 调度 → N 由调用方传入）
4. 创建 spec/fix/round-{N}/{feat,ui}/{,_systemic/}/ 目录骨架
5. 对每个 RED/ERROR/DIFF/SYSTEMIC 的 ID:
   a. 算出 layer + path
   b. 读 round-{N-1}/<layer>/<id>.md（若存在）→ 准备 carry forward
   c. 用本轮 runtime data + spec 原文 + 源码定位 拼出新 frontmatter + 6 sections
   d. carry forward disposition / related（不维护历史尝试表）
   e. Write spec/fix/round-{N}/<layer>/<id>.md
6. 生成本轮 _index.md / _summary.md
7. 若 N ≥ 1 → 计算 vs round-{N-1} 的 delta，写 _delta.md
8. 更新 spec/fix/_state.yaml （current_round = N）
9. 写 docs/dt-verification-report.md（人类阅读版）
10. 跑自检（fix-file-schema §十 + reconcile-rules §七）
```

---

## 五、自检（写完所有文件后必跑）

```bash
N=$(awk '/^current_round:/{print $2; exit}' spec/fix/_state.yaml)
ROUND_DIR="spec/fix/round-$N"

# 1. 人类版 + 三个汇总文件齐全
test -f docs/dt-verification-report.md || echo "❌ 缺人类版报告"
test -f $ROUND_DIR/_index.md || echo "❌ 缺 _index.md"
test -f $ROUND_DIR/_summary.md || echo "❌ 缺 _summary.md"
[[ $N -ge 1 ]] && { test -f $ROUND_DIR/_delta.md || echo "❌ 缺 _delta.md"; }

# 2. 人类版不含逐 it() 明细（除证据片段外）
inline_its=$(grep -cE '^\| `[FP][0-9]+_' docs/dt-verification-report.md)
[[ $inline_its -gt 5 ]] && echo "⚠️ 人类版疑似展开了逐条 it()"

# 3. 单问题文件数 ≈ AC 索引 RED + ERROR + 视觉差异条目数
problem_files=$(find $ROUND_DIR/feat $ROUND_DIR/ui -name '*.md' -not -name '_*.md' | wc -l)
expected=$(grep -cE '\| (RED|ERROR) \|' entry/src/ohosTest/ets/test/tdd-ac-index.md)
echo "本轮问题文件数: $problem_files；AC 索引 RED+ERROR 数: $expected"

# 4. Top 10 锚点必须指向 spec/fix/round-{N}/
toplinks=$(awk '/^## 5\. Top 10/,/^## 6\./' docs/dt-verification-report.md | grep -cE 'spec/fix/round-')
[[ $toplinks -lt 5 ]] && echo "⚠️ Top 10 链接过少"

# 5. 单问题文件 schema 校验（fix-file-schema §十）
# ... 执行 fix-file-schema 自检脚本
```

不达标的报告必须返工补全后再交付。
