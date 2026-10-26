# `spec/verify/ut/unimplemented/` 未实现功能点清单 JSON 模版 / Schema

第一步「测试用例设计」及 fixer 必要更新时的**非阻断诊断产物**。按 Spec 确定范围与 AC，核对 Android 实际行为或明确批准的平台差异后，若**高/中置信**判定某个
功能点在鸿蒙源码里**没实现 / 占位 / 假数据源 / 部分缺分支 / 与已核实契约冲突**，就把它记到 `spec/verify/ut/unimplemented/` 下一份 JSON——
**注明出自 Spec 的哪个 Feature、Android 依据或批准差异、功能点是什么，有鸿蒙源码就附上源码**。不能仅凭 Spec 概述诊断 Android 没有的新业务。

> 📍 **位置**：`spec/verify/ut/unimplemented/`（skill 流水线私有根 `spec/verify/ut/` 下，与 `ut-design/`、`android-oracle/` 同级）。
> 与设计、oracle、轮次产物并排，统一收在本 skill 自己的目录树里。

> **仅诊断，不阻断流程**：
> - 测试设计**照常盘点**（`spec/verify/ut/ut-design/F*.md` 有有效证据的行写满已核实契约，不预测红绿、不因「没实现」就弱化断言；缺 Android 行为/预期证据的行标 `needs_review`、未验证）。
> - 主线程汇总清单并继续 step2 测试生成、step3 编译和执行；不因文件存在或 `points` 非空暂停，不等待用户补全或要求清单清空。后续修复仍按 `MODE` 和真实执行结果决定。
> - 「是否真没实现」是**源码阅读后的高/中置信初判**；只记明显情形，模糊的不记（留给后续核验），不能直接据此判定用例 RED/GREEN。

## 一、目录布局

```
spec/
├── baseline/features/F012_collage_export.md         ← 输入：功能 Spec
└── verify/ut/                                       ← skill 流水线私有根（设计/生成/执行/修复都在这）
    ├── ut-design/F012_collage_export.md             ← 测试设计照常生成（每 Feature 一份）
    └── unimplemented/                               ← 本产物根（仅诊断，与 ut-design/ 同级）
        ├── F012_collage_export.json                 ← 每有命中项的 Feature 一份
        └── F031_share_sheet.json
```

- **每个 Feature 一份 JSON**：`spec/verify/ut/unimplemented/F{编号}_{英文名}.json`，与该 Feature 的设计文件同名、扩展名 `.json`。
- **没有命中项的 Feature 不写文件**（不产生空 JSON）；目录不存在就创建。
- 设计 agent 按 `FEATURE_SCOPE` 并发，各写各 Feature 的 JSON；fixer 仅在主线程分配的文件所有权内更新受影响点，禁止同一 JSON 并发写入。
- 主线程仅读取本轮 `FEATURE_SCOPE` 内的诊断文件，按 Feature 汇总 Spec / Android / ArkTS 源码溯源与关联用例；文件存在性和未实现项数量都不作为流程控制信号。
- 已有诊断文件中的额外控制字段不参与流程判断；格式警告也不转为测试生成的 `BLOCKERS`。

## 二、文件 Schema（复制后填写）

```json
{
  "feature_id": "F012",
  "feature_name": "collage_export",
  "spec_file": "spec/baseline/features/F012_collage_export.md",
  "detected_by": "arkts-ut-test-designer",
  "detected_at_stage": "design",
  "points": [
    {
      "point_id": "F012_AC03_grid_layout",
      "trace_ac": "AC3 + §Service layer",
      "feature_point": "composeCollageBitmap 须支持 1/2/4/9 格网格布局；当前源码仅实现 strip 横排分支",
      "spec_ref": "spec/baseline/features/F012_collage_export.md §验收标准 AC3 / §Service layer",
      "behavior_ref": "Android:<实际源码路径>:<行号> → composeCollageBitmap 的 1/2/4/9 格分支；须按项目实际证据填写",
      "status": "partial",
      "confidence": "high",
      "evidence": "源码 composeCollageBitmap 只有 strip 分支，无 grid 分支（无 1/2/4/9 格处理）",
      "source": {
        "file": "entry/src/main/ets/services/CollageService.ets",
        "symbol": "composeCollageBitmap",
        "lines": "42-70",
        "snippet": "composeCollageBitmap(items: PixelMap[]): PixelMap {\n  // 仅横向拼接，未按格数布局\n  return this.stripJoin(items)\n}"
      },
      "design_case_ids": ["F012_AC03_grid_2", "F012_AC03_grid_4", "F012_AC03_grid_9"]
    }
  ]
}
```

### 顶层字段

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `feature_id` | string | ✅ | Feature 编号，如 `F012`（出自 `spec/baseline/features/` 文件名）。 |
| `feature_name` | string | ✅ | Feature 英文名（与设计文件名一致）。 |
| `spec_file` | string | ✅ | 该 Feature 的 spec 文件仓内相对路径。 |
| `detected_by` | enum | ✅ | `arkts-ut-test-designer` 或 `arkts-ut-fixer`，对应本次核对并更新正文的角色。 |
| `detected_at_stage` | enum | ✅ | `design` 或 `fix`；始终是源码诊断快照，非实跑判决。 |
| `points` | list[object] | ✅ | 命中的未实现功能点，≥ 1 条（否则不写文件）。 |

### `points[]` 字段

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `point_id` | string | ✅ | 功能点标识，**与设计表的用例ID对齐**（如 `F012_AC03_grid_layout`），便于和 `ut-design/` 对照。 |
| `trace_ac` | string | ✅ | 出自 spec `## 验收标准` 的哪条 AC；若来自 `## Service layer`/`## Data flow` 分支补出，写 `AC + §Service layer`。 |
| `feature_point` | string | ✅ | **功能点是什么**：一句话说清范围内 Android 已核实行为或批准差异 + 鸿蒙缺口（"须支持 X，当前仅 Y"）。 |
| `spec_ref` | string | ✅ | spec 中的精确出处（文件 + 节 + AC 号），让人能回到原文。 |
| `behavior_ref` | string | ✅ | 行为依据：Android 实际源码 `path:line` / 已核验 oracle 条目，或明确批准平台差异的依据、范围；旧诊断缺此字段时先复核补齐，不照抄 Spec 推测。 |
| `status` | enum | ✅ | 缺口类型，见 §三。 |
| `confidence` | enum | ✅ | `high` \| `medium`——只记这两档；模糊/拿不准的**不记**，留给用户/后续实跑。 |
| `evidence` | string | ✅ | 凭什么判没实现：引源码现状一句话（如「方法体只有 `throw new Error('Not implemented')`」「返回写死常量」「焦点符号 grep 不到」）。 |
| `source` | object \| null | ✅ | **有源码就附上**；焦点符号在源码中完全不存在时填 `null`。结构见下。 |
| `design_case_ids` | list[string] | ✅ | 本功能点在 `ut-design/F*.md` 里对应的稳定用例 ID；有入口、环境与有效预期依据的行生成执行，其余逐 ID 保留缺口，结果以实跑为准。 |

### `source` 对象（有源码时填，否则 `null`）

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `file` | string | ✅ | 焦点源文件仓内相对路径，如 `entry/src/main/ets/services/CollageService.ets`。 |
| `symbol` | string | ✅ | 焦点方法/函数/类名。 |
| `lines` | string | ✅ | 行号范围，如 `42-70`；拿不准写 `unknown`。 |
| `snippet` | string | ✅ | 关键源码片段（**≤ 20 行**，截到能看出缺口即可；保留换行用 `\n`）。 |

## 三、`status` 枚举

| 取值 | 含义 | 典型源码形态 |
|---|---|---|
| `missing` | 已核实的迁移行为缺少实际生产入口 | 按 Android 行为搜索并排除鸿蒙等价入口，不能只因 Spec 建议的类名不存在而判缺失；无对应源码时 `source` 填 `null` |
| `placeholder` | **占位** | 空方法体 / `throw new Error('Not implemented')` / 仅 `console.*` / `// TODO` |
| `fake_data_source` | **假数据源** | 返回写死常量 / `PH-*` 占位 / 写死列表 / 仅 `emit` 不发请求 / `return false` |
| `partial` | **部分实现，缺分支/模式或必要生产接线** | 范围内 Android 实际行为或批准差异中的某些分支缺失；或逻辑已存在，但本功能所需应用调用、状态消费或生命周期尚未接通 |
| `spec_conflict` | 实装存在但**与已核实行为契约明显冲突**（保留字段名兼容） | 鸿蒙行为偏离 Android 实际行为或明确批准的平台差异；未核实的 Spec↔Android 分歧不据此判实现错误 |

> `missing` / `placeholder` / `fake_data_source` 对应 `test-design-template.md`「识别假数据源」表的三类；
> `partial` / `spec_conflict` 是设计期额外能看出的两类缺口。

## 四、判定边界（记什么、不记什么）

为保证诊断可信，**只记高/中置信的明显未实现**；不把源码初判当作实跑结果。

**记**：

- 已核实 Android 迁移行为对应的入口不存在，且已排除鸿蒙等价入口（`missing`）。
- 方法体是占位（空体 / `Not implemented` / 仅日志 / `// TODO`）（`placeholder`）。
- 返回写死常量 / 假数据源（`fake_data_source`）。
- 范围内 Android 源码/已核验 oracle 或批准差异确认了 N 个分支/模式，鸿蒙源码只实现其中一部分（`partial`）。
- 已有逻辑入口，但范围内功能所需实际调用、结果消费或生命周期仍缺失（`partial`）；附准确未接通位置，不把直接调用方法的 UT 通过视为整条功能已实现。
- 鸿蒙行为与已核实契约明显相反（`spec_conflict`，同时在设计文件备注里标注 Android/批准差异与鸿蒙的具体差异）。

**不记**：

- Android 行为本身就是固定值、空列表或返回 false，不能仅因这种代码形态判占位/假数据源。
- 逻辑看起来对、只是拿不准边界/异常分支是否齐全——交给实跑测。
- 隔离够不到或 Android 行为/预期证据不足的点（按 `test-design-template.md` 的 `no_entry/needs_review` 保留缺口；不得猜预期或弱化断言）。
- 纯 UI 层 AC（本 skill 不管）。

## 五、自检

> **谁核对**：设计 agent 或获得该文件所有权的 fixer 写完后，用 `Read` 回读 JSON，逐字段对照 §二核对（合法 JSON + 顶层/每点必填齐 + 角色/阶段合法 + `behavior_ref` 有效 + `status`∈枚举 + `confidence`∈{high,medium} + `source` 要么 null 要么四字段齐）。设计 agent 无 Bash，不运行下方脚本。
> **可执行校验由主线程在单个 Feature 设计或诊断更新完成时跑**：把准确诊断文件交给下面脚本；不合格文件交对应所有者修正。仍不合格则记诊断警告、不纳入可信计数，但不阻断其它有效测试生成或要求用户补全功能。

```bash
# 将本片段作为脚本运行，参数为本轮已确认的 JSON 文件路径；无文件时不传参数。
for f in "$@"; do
  if python3 - "$f" <<'PY'
import json,sys
d=json.load(open(sys.argv[1]))
for k in ("feature_id","feature_name","spec_file","detected_by","detected_at_stage","points"):
    assert k in d, f"缺顶层字段 {k}"
assert d["points"], "points 为空却写了文件"
assert d["detected_by"] in ("arkts-ut-test-designer", "arkts-ut-fixer"), d["detected_by"]
assert d["detected_at_stage"] in ("design", "fix"), d["detected_at_stage"]
for p in d["points"]:
    for k in ("point_id","trace_ac","feature_point","spec_ref","behavior_ref","status","confidence","evidence","source","design_case_ids"):
        assert k in p, f"{p.get('point_id')} 缺字段 {k}"
    assert p["status"] in ("missing","placeholder","fake_data_source","partial","spec_conflict"), p["status"]
    assert p["confidence"] in ("high","medium"), p["confidence"]
    if p["source"] is not None:
        for k in ("file","symbol","lines","snippet"):
            assert k in p["source"], f"source 缺 {k}"
print("ok", sys.argv[1])
PY
  then
    :
  else
    echo "[warning] $f: 诊断格式待修正，不阻断测试生成"
  fi
done
```

## 六、诊断生命周期（主线程视角，详见 SKILL.md）

1. 主线程解析本轮 `FEATURE_SCOPE`，仅清理这些 Feature 对应的已确认旧诊断文件，保留范围外文件。
2. step1 并发设计，各 Feature 如有命中项就写自己的 `spec/verify/ut/unimplemented/F*.json`；无命中项不写文件。
3. 每个 Feature 设计完成即校验并汇总该 Feature 诊断，同时进入生成就绪队列；格式问题修正或记警告，不等待所有设计返回。
4. step2 根据设计的可执行类型生成真实 UT，并记录未生成项；step3 编译、执行并产出真实报告，不等待补全通知或诊断清单清空。
5. 后续按 `MODE` 和运行结果执行 fix-loop。fixer 补齐入口、生产接线或必要更新/新增测试时，在分配的文件所有权内同步更新受影响设计行、generation 与本诊断：移除已消除的点，必要接线仍缺时保留 `partial` 及准确缺口，保留其余有效点；清空后删除对应诊断文件，不追加历史记录。无需因此重设计整个 Feature，已核验仍适用的 Android 证据可复用。
6. 诊断更新不代表通过；测试仍交独立 executor 编译、执行和审查。清单不替代运行报告，也不直接作为 fixer 派发依据；测试质量与更新边界见 [fixer 测试更新策略](fixer-test-policy.md)。
