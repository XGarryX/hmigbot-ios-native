#!/usr/bin/env python3
"""
analyze-cross-business-deps.py — Phase 2 plan 阶段必跑：扫跨业务 import 形成的依赖图，
                                  提前发现循环依赖，给出"上提到 business_common"的建议。

为什么必须跑：
  上一次重构事后救火过 3 次循环：
    business_login ↔ business_vip （FreeCountService / LOGIN_STATE_VERSION_KEY）
    business_home → business_file → business_home （PptFileLoadViewModel ↔ DBPPTManager）
  每次都是先加 oh-package 依赖 → ohpm install 报 "indirect dependency cannot be same as
  module name" → 才意识到要把符号上提到 business_common，**反复来回浪费时间**。
  在 Phase 2 plan 阶段就应识别这些「双向引用 / 强连通分量」并提示先上提。

输入：features/business_*/src/main/ets/ 下所有 .ets
输出：
  spec/module-dependency-graph.json   { module: [imported_modules] }
  spec/cross-business-deps.md         可读报告（含 SCC + 上提建议）
  退出码：0 OK；2 发现强连通环（必须人工决策上提哪些符号才能进 Phase 3）

用法：
  python3 analyze-cross-business-deps.py <project-root>
"""
from __future__ import annotations
import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path


IMPORT_RE = re.compile(r"""import\s*(?:type\s*)?\{([^}]+)\}\s*from\s*['"](business_\w+|lib_\w+)['"]""")
BUSINESS_RE = re.compile(r"^business_\w+$")


def biz_of(path: Path) -> str | None:
    m = re.search(r"features/(business_\w+)/", str(path))
    return m.group(1) if m else None


def collect(project_root: Path) -> tuple[dict[str, set[str]], dict[tuple[str, str], set[str]]]:
    """返回：
      module → 引用的其他 business 模块集合
      (module_a, module_b) → module_a 从 module_b 导入的符号集合
    """
    graph: dict[str, set[str]] = defaultdict(set)
    sym_edges: dict[tuple[str, str], set[str]] = defaultdict(set)

    features = project_root / "features"
    if not features.is_dir():
        sys.stderr.write(f"✗ no features/ under {project_root}\n")
        sys.exit(1)

    for biz_dir in sorted(features.iterdir()):
        if not biz_dir.is_dir() or not biz_dir.name.startswith("business_"):
            continue
        for p in (biz_dir / "src" / "main" / "ets").rglob("*.ets") if (biz_dir / "src").exists() else []:
            try:
                src = p.read_text(encoding="utf-8")
            except Exception:
                continue
            current = biz_dir.name
            for m in IMPORT_RE.finditer(src):
                syms = m.group(1)
                target = m.group(2)
                # 只关心跨 business（lib_* 不算业务依赖，跳过）
                if not BUSINESS_RE.match(target):
                    continue
                if target == current:
                    continue
                graph[current].add(target)
                for s in syms.split(","):
                    s = s.strip().split(" as ")[0].strip()
                    if s:
                        sym_edges[(current, target)].add(s)
        # 即使没引用别人，也要在图里出现（保证报告完整）
        graph.setdefault(biz_dir.name, set())
    return graph, sym_edges


def find_sccs(graph: dict[str, set[str]]) -> list[list[str]]:
    """Tarjan SCC。返回所有 size>=2 或自环的 SCC。"""
    index_counter = [0]
    stack: list[str] = []
    on_stack: dict[str, bool] = {}
    indices: dict[str, int] = {}
    lowlinks: dict[str, int] = {}
    result: list[list[str]] = []

    def strongconnect(v: str) -> None:
        indices[v] = index_counter[0]
        lowlinks[v] = index_counter[0]
        index_counter[0] += 1
        stack.append(v)
        on_stack[v] = True
        for w in graph.get(v, set()):
            if w not in indices:
                strongconnect(w)
                lowlinks[v] = min(lowlinks[v], lowlinks[w])
            elif on_stack.get(w):
                lowlinks[v] = min(lowlinks[v], indices[w])
        if lowlinks[v] == indices[v]:
            comp: list[str] = []
            while True:
                w = stack.pop()
                on_stack[w] = False
                comp.append(w)
                if w == v:
                    break
            result.append(comp)

    for v in graph:
        if v not in indices:
            strongconnect(v)
    # 仅保留有循环（size>=2 或单点自环）
    return [c for c in result if len(c) > 1 or c[0] in graph.get(c[0], set())]


def build_report(
    graph: dict[str, set[str]],
    sym_edges: dict[tuple[str, str], set[str]],
    sccs: list[list[str]],
) -> str:
    lines: list[str] = ["# Cross-Business Dependency Analysis", ""]
    lines.append("## 模块依赖图")
    lines.append("")
    lines.append("```")
    for mod in sorted(graph):
        deps = sorted(graph[mod])
        lines.append(f"{mod} → {deps if deps else '(no cross-business deps)'}")
    lines.append("```")
    lines.append("")

    if sccs:
        lines.append("## ⚠️ 检测到循环依赖（强连通分量）")
        lines.append("")
        lines.append("**这些环必须在 Phase 3 开始前打破**——否则 ohpm install 会报")
        lines.append("`indirect dependency cannot be same as module name`，反复救火。")
        lines.append("")
        for i, comp in enumerate(sccs, 1):
            lines.append(f"### SCC #{i}: {{ {', '.join(sorted(comp))} }}")
            lines.append("")
            lines.append('环上的跨模块符号清单（按"被多业务引用次数"高到低）：')
            lines.append("")
            # 收集环内所有符号 → 引用方集合
            sym_to_consumers: dict[str, set[str]] = defaultdict(set)
            sym_owner: dict[str, str] = {}
            for a in comp:
                for b in comp:
                    if a == b:
                        continue
                    for s in sym_edges.get((a, b), set()):
                        sym_to_consumers[s].add(a)
                        sym_owner[s] = b
            ranked = sorted(sym_to_consumers.items(), key=lambda kv: (-len(kv[1]), kv[0]))
            lines.append("| 符号 | 当前归属 | 被引用方 | 建议 |")
            lines.append("|---|---|---|---|")
            for sym, consumers in ranked:
                owner = sym_owner.get(sym, "?")
                lines.append(
                    f"| `{sym}` | {owner} | {', '.join(sorted(consumers))} | 上提到 `business_common` |"
                )
            lines.append("")
        lines.append("## 建议的破环顺序")
        lines.append("")
        lines.append("1. 把上表「建议」列的所有符号迁到 `features/business_common/src/main/ets/`")
        lines.append("2. 在 business_common/Index.ets re-export")
        lines.append("3. 各 business 内 `from \"business_<other>\"` 改 `from \"business_common\"`")
        lines.append("4. 移除各 business oh-package.json5 里循环方向的 `business_<other>` 依赖")
        lines.append("5. 重跑本脚本，确认 SCC 清零，**才能进 Phase 3**")
    else:
        lines.append("## ✅ 无循环依赖")
        lines.append("")
        lines.append("可以直接进 Phase 3。")
    return "\n".join(lines) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("project_root", type=Path)
    args = ap.parse_args()

    project = args.project_root.resolve()
    graph, sym_edges = collect(project)
    sccs = find_sccs(graph)

    spec_dir = project / "spec"
    spec_dir.mkdir(exist_ok=True)

    # JSON 产物
    graph_json = {k: sorted(v) for k, v in graph.items()}
    (spec_dir / "module-dependency-graph.json").write_text(
        json.dumps(graph_json, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    # MD 报告
    report = build_report(graph, sym_edges, sccs)
    (spec_dir / "cross-business-deps.md").write_text(report, encoding="utf-8")

    sys.stdout.write(f"✓ wrote spec/module-dependency-graph.json + spec/cross-business-deps.md\n")
    if sccs:
        sys.stderr.write(f"✗ {len(sccs)} cycle(s) found — see spec/cross-business-deps.md\n")
        sys.stderr.write("  Phase 3 BLOCKED until cycles resolved (hoist symbols to business_common).\n")
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
