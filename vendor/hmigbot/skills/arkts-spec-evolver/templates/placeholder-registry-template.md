# 占位符注册表

## 统计
- 总数: 0
- registered: 0
- pending: 0
- due: 0
- fired: 0
- resolved: 0
- deferred: 0

## Schema 说明

每个占位符 6 个字段：前 4 个为核心字段（既有读取方按列名 / 前 4 列向后兼容），后 2 个为「延迟 / 待接工作分类法」新增列，**追加在表末尾**。

| 字段 | 必填 | 说明 |
|------|------|------|
| `P-ID` | 是 | 占位编号。格式：`P-S{SliceN}-{序号}`（来自 Slice）或 `P-B{BaseN}-{序号}`（来自 Base 层）。例：`P-S3-001`、`P-B6-002`。 |
| `location` | 是 | 占位代码落地位置。**必须**是文件路径（可附行号或锚定符）。例：`entry/src/main/ets/pages/PartFivePage.ets:128`、`entry/src/main/ets/repositories/PaymentRepository.ets#processPayment`。 |
| `trigger_condition` | 是 | **可机器校验的**唤起条件（见下方白/黑名单）。 |
| `status` | 是 | 状态枚举：`registered` / `pending` / `due` / `fired` / `resolved` / `deferred`。 |
| `kind` | 是 | 占位类别：`thirdparty-sdk`（三方 SDK 无鸿蒙等价物，需外部依赖入仓）或 `forward-ref`（前向引用——早阶段挖坑、指定后续 Slice 填的代码桩，含 converter UI 钩子 / Base signature 桩 / 跨切片 handler 桩）。 |
| `resolve_by` | forward-ref 必填 | 前向引用的归属 Slice / Step，格式 `Slice {N} Step {3c\|3d}`。`kind=thirdparty-sdk` 时留空（用 `trigger_condition` 表达 SDK 入仓条件）。 |

### status 状态机

```
registered → pending → due → fired → resolved
                    ↘
                      deferred（用户显式延期，需附理由）
```

- `registered`：plan 阶段直写（a2h-plan Step 4.1）或执行期铸号登记，代码尚未落地
- `pending`：代码已落地占位，trigger_condition 未满足，等待唤起
- `due`：trigger_condition 自动检测命中，需要回填真实实现
- `fired`：已通知 owner（或日志告警已抛出），等待回填
- `resolved`：真实代码已回填且编译/验证通过
- `deferred`：经过用户审批延期到下一里程碑（必须含 `defer_until` + 理由）

### trigger_condition 白名单（合法格式）

trigger_condition 必须能被脚本机器解析。支持以下 6 类格式：

| 格式 | 语义 | 检测方式 |
|------|------|---------|
| `D-{N} chosen` | Decision Card 已选定 | `grep "D-{N}.*chosen" spec/migration-decisions.md` |
| `<path> 实现 <symbol>` | 指定文件实现指定符号 | `grep -n "<symbol>" {path}` |
| `<skill-name> 入仓` | 指定 skill 已合入 skills 目录 | `test -d arkts-skills/skills/<skill-name>` |
| `<api-endpoint> 上线` | API 路由已加入网络层 | `grep "<api-endpoint>" entry/src/main/ets/network/` |
| `<resource-id> 就绪` | 资源已就绪 | `grep "<resource-id>" entry/src/main/resources/` |
| `Slice {N} Step {3c\|3d}` | 前向引用待接线工作的归属 Slice/Step（`kind=forward-ref` 专用——让「earlier 阶段挖坑、later Slice 填」的接线延迟可被正规登记） | `location` 文件无 `// FWD-REF:` marker 且真实实现存在 → `resolved` |

### trigger_condition 黑名单（**禁止**使用）

以下模糊措辞**一律禁止**作为 trigger_condition，converter / hard-gate 将直接 FAIL：

- `等真机接入` / `等设备就绪` / `真机联调时`
- `等 SDK 决策` / `SDK 接入后` / `待 SDK 到位`
- `联调时补` / `联调后再说` / `联调阶段处理`
- `上线前补` / `上线前再确认` / `上线时补`
- `后续` / `稍后` / `暂时` / `先这样` / `回头再说`

判定脚本（伪代码）：
```python
BLOCKLIST = ["真机", "SDK", "联调", "上线前", "后续", "稍后", "暂时", "先这样", "回头"]
if any(kw in trigger_condition for kw in BLOCKLIST):
    return FAIL("trigger_condition 含模糊延期措辞，必须改为可机器校验的具体条件")
```

## 注册表

> `kind` / `resolve_by` 为新增列，追加在表末尾；既有读取方（如 a2h-verify CHECK-3）按列名 / 前 4 列读取，向后兼容。

| P-ID | location | trigger_condition | status | kind | resolve_by |
|------|----------|-------------------|--------|------|------------|

## 延期记录（仅 status=deferred 时填写）

| P-ID | defer_until | reason | approved_by |
|------|-------------|--------|-------------|
