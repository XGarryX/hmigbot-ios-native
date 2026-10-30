<!-- when: §3c / §5e 调脚本前需理解 taxonomy / 严重度规则时加载 -->
<!-- topics: 骨架审计, 15 子类 taxonomy, 严重度规则, FWD-REF 反查, escape-hatch -->

# 骨架审计 — 设计与子类参考

> **执行细节已脚本化**：`scripts/audit_skeletons.py`（CLI）+ `scripts/skeleton_lib/`（lib）实现全部检测逻辑。本文件仅保留概念解释 + 子类目录，供 LLM 阅读 JSON 输出时对照。

---

## 1. 15 子类 taxonomy

| 等级 | 子类 | 触发样例 | 默认严重度 |
|---|---|---|---|
| **L1 合法占位** | `forward-ref` | 配套 `// FWD-REF: P-xxx resolve_by=Slice N Step 3X` 且 registry 已登记 | PASS |
| **L1** | `thirdparty-sdk` | 配套 `// PLACEHOLDER: P-xxx trigger=<whitelist>` 且 registry kind=thirdparty-sdk | PASS |
| **L1** | `intentional-default` | `$r('app.media.ic_default_*')` 在 resource-mapping.md `kind=intentional-default` 段登记 | PASS |
| **L1** | `forward-ref-uncertain` | 已登记 `// TODO:` 且 registry kind=forward-ref-uncertain（按 `file:line` 反查命中） | PASS |
| **L1** | `resource-pending-asset` | fallback 资产引用且 registry kind=resource-pending-asset | PASS |
| **L1** | `resource-pending-translation` | 资源 JSON `[TODO: translate]` 且 registry kind=resource-pending-translation（按 `<path>:<key>` 反查命中） | PASS |
| **L2 可疑骨架** | `empty-body` | `aboutToAppear() {}` / `@Builder X() {}` / `onClick: () => {}` / Column 仅含 `Text('占位')` | scope=slice → FAIL；其他 scope → WARN |
| **L3 确定骨架** | `fake-content` | `console.info('TODO:..')` / `console.info('navigate to..')` / `Text('占位')` / `Text('Loading...')` 静态写死 | FAIL |
| **L3** | `naked-TODO` | `// TODO: implement` / `// TODO[Slice 3]` / `// 待实现` / `// 待接入` | FAIL |
| **L3** | `throw-stub` | `throw 'Slice 5'` / `throw Error('not implemented')` 且未登记 | FAIL |
| **L4 架构骨架** | `orphan-vm` | VM/Repo 文件有 export 但无任何 page/component import + 实例化（引用图检测） | FAIL |
| **L4** | `dangling-fwd-ref` | `// FWD-REF: P-xxx` 在代码中存在但 registry 中 status=resolved | FAIL |
| **L4** | `dead-route` | `pageMap` 注册的页无 `pushPathByName` 调用方 | WARN |
| **L5 资源占位** | `resource-pending-unregistered` | 资源 JSON value 含 `[TODO: translate]` / 括号 `[TODO:...]` 但无对应 registry 条目 | FAIL |
| **L5** | `resource-fallback-unregistered` | fallback 资产引用但无 registry `P-RES-ASSET-*` 登记 | FAIL |

> Nav 单子组件 / NavDestination 嵌套违例**不在 audit 范畴**——由 ArkUI 编译器在运行时报错兜底。

## 2. 严重度规则（硬编码在 `skeleton_lib/taxonomy.py`）

```
L1                    → PASS 永远
L2 + scope=slice      → FAIL
L2 + scope=stage|all  → WARN
L3                    → FAIL 永远
L4 (非 dead-route)   → FAIL 永远
L4 dead-route         → WARN 永远
L5                    → FAIL 永远（资源层未登记占位）
```

scope 由调用方参数 `--scope stage|slice|all` 决定。

## 3. 合法性裁定流程（`skeleton_lib/classifier.py` + `registry_resolver.py`）

对每个候选 finding（按序执行，任一步升 L1.PASS 即返回）：

```
1. 命中 SKELETON_PATTERNS 任一 regex → 临时归入 L2/L3 子类
2. 上下 3 行内查找 `// FWD-REF: P-xxx` marker:
   - 命中且 P-ID 在 registry 的 kind=forward-ref 段 → 升 L1.forward-ref, PASS
   - 命中但 P-ID 未登记 → 维持原级，evidence 标"FWD-REF P-ID 未登记"
3. 上下 3 行内查找 `// PLACEHOLDER: P-xxx trigger=...` marker:
   - 命中且 P-ID 在 registry 的 kind=thirdparty-sdk 段 → 升 L1.thirdparty-sdk, PASS
4. registry **location 反查**（无邻接 marker 的已登记占位，如 forward-ref-uncertain 的 `// TODO` / component-builder L3 自登记的 console.info）:
   - 按 `<file>:<line>`（退而 `<file>`）反查 registry，命中条目 status≠resolved 且
     kind ∈ {forward-ref, forward-ref-uncertain, resource-pending-asset, resource-pending-translation, thirdparty-sdk} → 升 L1.<kind>, PASS
5. 资源 JSON（`resources/<locale>/element/*.json`）扫到 `[TODO: translate]` / 括号 TODO:
   - 按 `<path>:<key>` 反查 registry，命中 kind=resource-pending-translation / resource-pending-asset → 升 L1.<kind>, PASS
   - 否则 → L5 FAIL（未登记资源占位）
6. 计算 severity_at_scope（按 §2 规则）
```

## 4. Escape-hatch 措辞扫描（brief 文件）

```python
ESCAPE_HATCH_PHRASES = [
    "由 fixer",
    "后续接通",
    "a2h-fixer 完成",
    "后续 fixer",
    "已知不完整",
    "verify 阶段补齐",
    "fixer 补齐",
]
```

brief prose 命中任一即视为"prose defer"违规，立即 FAIL（执行「禁止 prose defer」规则）。

## 5. 输出 JSON schema

参考 `scripts/audit_skeletons.py --output-json` 输出。关键字段：

- `summary` — 各等级计数 + FAIL/WARN 总数 + brief_escape_hatches 数
- `findings[]` — 每条含 `level / subtype / file / line / match / suggested_action / severity_at_scope / p_id? / resolve_by? / legitimate / legitimacy_evidence`
- `brief_escape_hatches[]` — brief 中扫到的逃生舱命中

## 6. FAIL 时的处置（由 §3c SKILL 段描述）

脚本本身只返回退出码 + JSON；处置策略（3 轮 in-stage retry → BLOCKED → brief escalation）由 SKILL.md §3c 与 §5e 协调。

## 7. 升级路径

- Phase 4：`empty-body` 检测从 regex 切换到 tree-sitter AST（提升对带注释/带 console.log 的伪空体识别精度）
- Phase 4：`dead-route` 检测加 nav_graph_lib 路由图分析
