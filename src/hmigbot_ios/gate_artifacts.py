"""Deterministic iOS migration gate artifacts.

The Android migration produced a set of human-readable gate files.  The iOS
pipeline keeps the same review points, but derives their initial contents from
the native source index/facts and leaves all semantic decisions pending until a
human authors the contracts.  Generated files are marked and are safe to
recreate; authored files are never replaced.
"""
from __future__ import annotations

import re
import json
from pathlib import Path

from .core import MigrationError, atomic_write, digest, json_bytes, read_json, safe_child, snapshot, write_json

MARKER = "<!-- hmigbot-derived-gate:1 -->"


def _rel(path: Path, project: Path) -> str:
    return path.resolve().relative_to(project.resolve()).as_posix()


def _write_scaffold(path: Path, text: str) -> str:
    """Create missing authoring inputs. Never replace even marked user edits."""
    if path.exists():
        return "preserved"
    atomic_write(path, text.encode("utf-8"))
    return "written"


def _emit_scaffold(project, outputs, path, text):
    if outputs is None:
        return _write_scaffold(path, text)
    outputs[_rel(path, project)] = text
    return 'candidate'


def render_spec_inputs(project):
    """Pure main content renderer. Consumers select explicit commit scopes."""
    from .native_pipeline import context
    from .ios_facts import extract
    project = Path(project).resolve()
    source, _ = context(project)
    index = read_json(project / 'spec/baseline/ios-source-index.json')
    current = snapshot(source)
    if index.get('source_sha256') != current['sha256'] or index.get('files') != current['files']:
        raise MigrationError('Source index is stale; refresh and review')
    graph_path = project / 'spec/baseline/ios-facts.json'
    graph = read_json(graph_path) if graph_path.is_file() else extract(source)
    if graph['source_sha256'] != current['sha256']:
        raise MigrationError('Source facts are stale; refresh and review')
    outputs = {}
    pages = _scaffold_contracts(project, index, graph, current['files'], outputs=outputs)
    _emit_scaffold(project, outputs, project / 'spec/baseline/ui-manifest.md', _manifest_text(index, pages))
    _emit_scaffold(project, outputs, project / 'spec/baseline/feature-index.md', _feature_index_text(index, pages))
    if snapshot(source)['sha256'] != current['sha256']:
        raise MigrationError('Source changed during candidate rendering')
    return {'files': outputs, 'pages': pages, 'source_sha256': current['sha256']}


def _write_report(path: Path, text: str) -> None:
    atomic_write(path, text.encode("utf-8"))


def _source_data(project: Path):
    index_path = project / "spec/baseline/ios-source-index.json"
    facts_path = project / "spec/baseline/ios-facts.json"
    if not index_path.is_file() or not facts_path.is_file():
        raise MigrationError("Generate the iOS source index and facts before gate artifacts")
    index, facts = read_json(index_path), read_json(facts_path)
    if not isinstance(index, dict) or not isinstance(facts, dict):
        raise MigrationError("Malformed iOS source index or facts")
    files = index.get("files", [])
    if not isinstance(files, list):
        raise MigrationError("iOS source index files must be a list")
    from .native_pipeline import context
    source, _ = context(project)
    current = snapshot(source)
    if (index.get('source_sha256') != facts.get('source_sha256')
            or index.get('source_sha256') != current['sha256'] or files != current['files']):
        raise MigrationError('Source index/facts are stale; refresh and review before generating gates')
    return index, facts, files


def _code_files(files):
    suffixes = {".swift", ".m", ".mm", ".h", ".c", ".cpp"}
    return [f for f in files if isinstance(f, dict) and Path(str(f.get("path", ""))).suffix.lower() in suffixes]


def _page_candidates(project: Path, files):
    from .native_pipeline import context
    from .source_candidates import discover_candidates
    source, _ = context(project)
    candidates = discover_candidates(source, {'files': files})
    result = []
    for item in candidates:
        if not item['is_ui']:
            continue
        name, anchor = item['name'], item['anchor']
        kind = ('overlay' if 'HUD' in name else 'nested'
                if item['candidate_type'] == 'component' or name.endswith('Cell') else 'page')
        result.append({'name': name, 'path': anchor['path'], 'line': anchor['line'],
                       'framework': 'SwiftUI' if item['framework'] == 'swiftui' else 'UIKit',
                       'kind': kind, 'sha256': anchor['sha256']})
    if not result:
        for item in files:
            if Path(item['path']).suffix in {'.storyboard', '.xib'}:
                result.append({'name': Path(item['path']).stem, 'path': item['path'], 'line': 1,
                               'framework': 'InterfaceBuilder', 'kind': 'page', 'sha256': item['sha256']})
    return result


def _anchors(items):
    return "\n".join(f'  - path: "{item["path"]}"\n    line: {item.get("line", 1)}' for item in items)


def _feature_anchors(files):
    suffixes = {".swift", ".m", ".mm", ".h", ".c", ".cpp", ".storyboard", ".xib"}
    return [{"path": f["path"], "line": 1} for f in files
            if isinstance(f, dict) and isinstance(f.get("path"), str)
            and Path(f["path"]).suffix.lower() in suffixes]


def _source_anchor_refs(text):
    """Read exact list/map anchor identities without executing YAML.

    Display strings and bare filenames cannot register a
    declaration. Unsupported/duplicate scalar fields fail closed for the item.
    This is deliberately the same block boundary convention as source_paths.
    """
    refs, item, active = set(), {}, False

    def finish():
        if set(item) >= {'path', 'symbol', 'line'} and item.get('valid', True):
            line = item['line']
            if re.fullmatch(r'[1-9]\d*', line):
                refs.add((item['path'], item['symbol'], int(line)))

    for line in text.splitlines():
        if re.match(r'^\s*source_anchors:\s*(?:#.*)?$', line):
            finish()
            item, active = {}, True
            continue
        if not active:
            continue
        if line.startswith('```') or (line and not line[0].isspace()):
            finish()
            item, active = {}, False
            continue
        match = re.fullmatch(r'\s+(?P<new>-\s+)?(?P<key>[\w.-]+):\s*(?:"(?P<double>[^"\n]*)"|\'(?P<single>[^\'\n]*)\'|(?P<plain>[^#]*?))\s*(?:#.*)?', line)
        if not match:
            if line.strip() and not line.lstrip().startswith('#'):
                item['valid'] = False
            continue
        if match['new']:
            finish()
            item = {}
        key = match['key']
        if key not in {'path', 'symbol', 'line'}:
            continue
        if key in item:
            item['valid'] = False
        item[key] = next(value.strip() for value in (match['double'], match['single'], match['plain'])
                         if value is not None)
    finish()
    return refs


def _candidate_identity(item):
    return (item.get('path', item.get('source', '')), item.get('name', ''), item.get('line', 1))


def _scaffold_contracts(project: Path, index: dict, facts: dict, files: list, *, outputs=None):
    base = project / "spec/baseline"
    ui_dir, feature_dir = base / "ui", base / "features"
    source_sha = index.get("source_sha256", "")
    candidates = _page_candidates(project, files)
    # Stable IDs are reserved by existing documents, including removed pages.
    # Do not recycle an ID when a new declaration sorts before an old one.
    identities, reserved = {}, set()
    for existing in sorted(ui_dir.glob('page_*.md')):
        old = existing.read_text(encoding='utf-8-sig')
        match = re.match(r'(page_\d+)', existing.stem)
        if match:
            reserved.add(match[1])
            for relative, symbol, _ in _source_anchor_refs(old):
                identities.setdefault((relative, symbol), set()).add(match[1])
    pages = []
    for item in candidates:
        # Source lines can move; path + symbol retain a stable ID while the
        # unchanged old anchor stays stale until its owner reviews it.
        owners = identities.get(_candidate_identity(item)[:2], set())
        # Multiple authored claims stay visible as a source/spec issue. Never
        # silently choose an owner by a global class name across modules.
        page_id = next(iter(owners)) if len(owners) == 1 else None
        if page_id is None:
            number = max([int(p.split('_')[1]) for p in reserved] or [0]) + 1
            page_id = f'page_{number:04d}'
            reserved.add(page_id)
        target = f"entry/src/main/ets/pages/{item['name']}Page.ets"
        pages.append({"page_id": page_id, "name": item["name"], "source": item["path"],
                      "line": item["line"], "kind": item["kind"], "framework": item["framework"],
                      "target": target, "feature": "F001", "priority": "P0" if item["kind"] == "page" else "P1",
                      "confidence": "medium"})
        content = f"""# {page_id} — {item['name']}\n{MARKER}\nsource_platform: ios\nspec_contract_version: 2\nsource_sha256: {source_sha}\npage_id: {page_id}\nstatus: pending_authoring\ntarget: {target}\nios_frameworks: [{item['framework'].lower()}]\n\n## 页面与范围\n入口候选 `{item['name']}`，所属功能 F001，目标页面 `{target}`。机器扫描尚未证明可见入口完整性。\n\n## iOS 原生语义\n待依据 ios-semantics.json 与源码生命周期、委托、动作和状态事实补充；当前只记录源锚点。\n\n## 页面结构与视觉\n待审阅真实节点、条件分支、布局约束、动态字体、安全区和资源变体。\n\n## 组件层级\n| 节点ID | 父节点 | 源控件/条件 | ArkUI组件 | 内容/事件 | 源证据 |\n|---|---|---|---|---|---|\n| root | - | {item['name']} | pending | pending | `{item['path']}:{item['line']}` |\n\n## 布局约束\n| 节点ID | 尺寸/布局/安全区 | 条件/优先级 | 资源引用 | 源证据 |\n|---|---|---|---|---|\n| root | unknown（需源/运行证据） | pending | pending | `{item['path']}:{item['line']}` |\n\n## 状态接口\n| 源状态与类型 | 初值/所有者/生命周期 | 读写者 | UI 影响 | 目标 Owner.state 与类型 |\n|---|---|---|---|---|\n| unknown | pending | pending | pending | pending |\n\n## 交互与导航\n| 前置态 | 事件/入口 | 状态与副作用 | 导航值/返回行为 | 源证据 | owning_feature |\n|---|---|---|---|---|---|\n| unknown | pending | pending | pending | `{item['path']}:{item['line']}` | F001 |\n\n## ArkUI 映射决策\n| 源机制 | 目标实现 | 约束/差异 | 源证据 |\n|---|---|---|---|\n| {item['framework']} | pending | 待审阅 | `{item['path']}:{item['line']}` |\n\n## 资源引用\n| 资源ID | 类型 | 目标引用 | 源证据 |\n|---|---|---|---|\n| pending | pending | pending | `{item['path']}:{item['line']}` |\n\n## 资源与运行证据\n截图/录像：not_run；资源变体和设备观察待补。\n\n## 验收与接线\n待补充稳定 F001-ACxx、真实 handler→ViewModel/Service 接线及独立判断；本脚手架不声明通过。\n\nsource_anchors:\n  - role: view\n    path: "{item['path']}"\n    symbol: "{item['name']}"\n    line: {item['line']}\n"""
        if outputs is not None or not any(ui_dir.glob(page_id + '*.md')):
            _emit_scaffold(project, outputs, ui_dir / f"{page_id}.md", content)
    all_anchor_text = _anchors(_feature_anchors(files))
    feature = f"""# F001: iOS source behavior\n{MARKER}\ncomplexity: complex\ntier: core\ndepth: full\nsource_platform: ios\nspec_contract_version: 2\nsource_sha256: {source_sha}\naction_contracts: required\n\n## 范围\n机器事实覆盖当前 iOS 源索引中的代码；需按用户可感知能力拆分并补充入口、页面和 feature-base 依赖。\n\n## iOS 源语义\n待依据 ios-semantics.json 保留 Swift/Objective-C 行为、Optional、委托、错误、取消和资源生命周期事实。\n\n## 数据流\n待依据 source facts、服务调用和持久化证据补充输入→校验/转换→服务→副作用→UI。\n\n## 源行为表\n| 前态/输入 | 事件 | 条件/运算 | 后态/结果 | 错误/取消 | 源文件:行 |\n|---|---|---|---|---|---|\n| unknown | pending | pending | pending | pending | 待审阅 |\n\n## 动作合同\n待确认是否存在跨层异步、取消或共享副作用；确认后在此定义 action_id 或引用 feature-base。\n\n## 服务层（ArkTS 目标接口）\n| 目标接口 | 输入/输出/值域 | 错误/取消 | 状态/线程/生命周期 |\n|---|---|---|---|\n| pending | pending | pending | pending |\n\n## API 接口\n待绑定真实 api-inventory 端点；不从依赖名推断网络契约。\n\n## 实现映射（Source→ArkTS）\n| 源机制 | 目标实现 | 数据/生命周期契约及依据 | 迁移分类 | 决策 |\n|---|---|---|---|---|\n| pending | pending | 待审阅 | pending | pending |\n\n## 状态管理\n待补充状态持有者、更新方向、共享范围、恢复和清理。\n\n## 对接点（与 UI 页面的接口）\n待绑定 page.handler ← ViewModel/Service、参数、状态投影和完成边界。\n\n## 验收标准\n待由 iOS 行为证据补充稳定 F001-ACxx；此脚手架不声明验收通过。\n\nsource_anchors:\n{all_anchor_text}\n"""
    if not list(feature_dir.glob('F*.md')) or outputs is not None and (feature_dir / 'F001-ios-source.md').is_file():
        _emit_scaffold(project, outputs, feature_dir / "F001-ios-source.md", feature)
    _emit_scaffold(project, outputs, base / "feature-base.md", f"""# 公共基础设施合同\n{MARKER}\nspec_contract_version: 2\nsource_platform: ios\nsource_sha256: {source_sha}\n\n## 数据模型\n机器事实尚未确认公共数据模型；unknown，补证步骤：审阅源状态/服务/持久化事实。\n\n## 数据库与文件恢复\n机器事实尚未确认公共恢复合同；unknown，补证步骤：审阅真实存储调用。\n\n## 网络与外部合同\n机器事实尚未确认公共 API；unknown，补证步骤：审阅 API 清单和请求证据。\n\n## 事件系统\n机器事实尚未确认公共事件总线；unknown，补证步骤：审阅委托、通知和回调。\n\n## 偏好设置\n机器事实尚未确认公共偏好键；unknown，补证步骤：审阅 UserDefaults/AppStorage 等调用。\n\n## 权限声明\n机器事实尚未确认权限调用；unknown，补证步骤：审阅 usage description、entitlement 和运行时请求。\n\n## 公共服务与状态\n| 目标接口 | 输入/输出/错误 | 所有者/线程 | 初始化/释放 | 定义方/消费方 |\n|---|---|---|---|---|\n| pending | pending | pending | pending | F001 |\n\n## 公共组件与资源\n机器事实尚未确认公共组件合同；unknown，补证步骤：审阅页面嵌入和资源变体。\n\n## 跨栈映射基线\n| 源机制 | 目标实现 | 行为/值域/生命周期 | 核验依据 | 决策 |\n|---|---|---|---|---|\n| pending | pending | pending | source facts | pending |\n""")
    decision_text = f"""# Decision ledger\n{MARKER}\nsource_platform: ios\nsource_sha256: {source_sha}\n\n## 待决策\n机器生成脚手架不做语义决策；请记录每项平台差异与证据。\n"""
    _emit_scaffold(project, outputs, project / "spec/decision-ledger.md", decision_text)
    _emit_scaffold(project, outputs, project / "spec/decision-ledger.md", decision_text)
    _emit_scaffold(project, outputs, base / "skip-list.md", f"""# 范围排除\n{MARKER}\nspec_contract_version: 2\nsource_platform: ios\nsource_sha256: {source_sha}\n\n## 排除项\n| ID | 源路径/入口 | 排除原因 | 源证据 | 决策引用 |\n|---|---|---|---|---|\n| none | none | 当前没有自动排除项 | 当前源快照 `{source_sha}` | none |\n\n## Preview\n当前没有自动 Preview 排除；如发现精确区间，须保留义务并补 source_review。\n""")
    _emit_scaffold(project, outputs, base / "source-coverage-report.md", f"""# 源范围与覆盖报告\n{MARKER}\nspec_contract_version: 2\nsource_platform: ios\nsource_sha256: {source_sha}\n\n## 源归属\n| 源路径 | feature | page_id | 范围处置 | 源证据 |\n|---|---|---|---|---|\n| 见 ios-source-index.json | F001 | page inventory | pending_review | `{source_sha}` |\n\n## 覆盖口径与限制\n源快照、全仓 repository 变体和 token facts 已生成；有效构建、义务→AC、目标生成、编译和设备观察仍未完成。\n\n## 未决与回流\n源语义、AC、目标接口和运行证据由 spec/plan/verify 阶段补齐；unknown 不计入已覆盖分子。\n""")
    _write_ios_baselines(project, index, facts, pages, files, outputs=outputs)
    return pages


def _write_ios_baselines(project: Path, index: dict, facts: dict, pages: list, files: list, *, outputs=None):
    from .native_pipeline import source_paths
    from .native_semantics import required_facts
    base = project / "spec/baseline"
    source_sha = index.get("source_sha256", "")
    graph_sha = digest(json_bytes(facts))
    docs = []
    suffixes = {'.swift': 'swift', '.m': 'objc', '.mm': 'objcxx', '.c': 'c', '.cpp': 'cpp'}
    for folder, kind in (('features', 'feature'), ('ui', 'page')):
        documents = {path: path.read_text(encoding='utf-8-sig') for path in (base / folder).glob('*.md')}
        documents.update({project / rel: text for rel, text in (outputs or {}).items()
                          if Path(rel).parent == Path('spec/baseline') / folder and rel.endswith('.md')})
        for path, text in sorted(documents.items()):
            match = re.match(r'^(F\d+|page_\d+)', path.stem)
            if not match or kind == 'feature' and re.match(r'F\d+[-_].+\..+', path.stem):
                continue
            anchors = source_paths(text)
            languages = {suffixes[Path(p).suffix] for p in anchors if Path(p).suffix in suffixes}
            if not languages:
                languages = {'objc'} if any(p.endswith('.h') for p in anchors) else {'swift'}
            frameworks = ({'swiftui'} if 'ios_frameworks: [swiftui]' in text else
                          {'ib'} if any(Path(p).suffix in {'.storyboard', '.xib'} for p in anchors) else
                          {'uikit'} if kind == 'page' else {'nonvisual'})
            dimensions = required_facts(kind, languages, frameworks)
            docs.append({'id': match[1], 'kind': kind, 'languages': sorted(languages),
                         'frameworks': sorted(frameworks),
                         'facts': {field: {'status': 'unknown',
                                          'reason': f"{match[1]} 的 {field} 尚需沿源锚点审阅输入、处理和可观察结果。"}
                                   for field in sorted(dimensions)}})
    semantics = {"schema_version": 2, "source_platform": "ios", "source_sha256": source_sha,
                 "graph_sha256": graph_sha, "documents": docs,
                 "scope": "Generated review scaffold; claims remain unknown until authored."}
    sem_path = base / "ios-semantics.json"
    if not sem_path.exists():
        _emit_scaffold(project, outputs, sem_path, json_bytes(semantics).decode("utf-8"))
    obligations_path = project / "spec/baseline/ios-obligations.json"
    obligations_doc = read_json(obligations_path) if obligations_path.is_file() else {}
    obligations = obligations_doc.get("obligations", []) if isinstance(obligations_doc, dict) else []
    mappings = [{"obligation_id": o.get("id"), "ac_ids": [], "disposition": "pending",
                 "source_review": {"status": "pending", "input": "", "processing": "",
                                    "observable": "", "reviewer": ""}}
                for o in obligations if isinstance(o, dict) and o.get("id")]
    coverage = {"schema_version": 2, "source_platform": "ios", "source_sha256": source_sha,
                "graph_sha256": graph_sha, "mappings": mappings,
                "scope": "Generated pending mappings; no obligation is treated as covered."}
    cov_path = base / "ios-coverage.json"
    if not cov_path.exists():
        # JSON has no comment channel; a scope field explicitly marks it as a
        # generated review scaffold and prevents it being mistaken for proof.
        _emit_scaffold(project, outputs, cov_path, json_bytes(coverage).decode("utf-8"))
    disposition = {"schema_version": 2, "source_platform": "ios", "source_sha256": source_sha,
                   "files": [], "scope": "Generated empty disposition; review every unowned file."}
    disp_path = base / "ios-source-disposition.json"
    if not disp_path.exists():
        _emit_scaffold(project, outputs, disp_path, json_bytes(disposition).decode("utf-8"))


def _manifest_text(index: dict, pages: list):
    rows = ["# UI Manifest", MARKER, "source_platform: ios", "spec_contract_version: 2",
            f"source_sha256: {index.get('source_sha256', '')}", "",
            "## 全局约定", "目标导航、状态所有权、主题、安全区、资源和组件以页面/功能规格为准；机器候选不构成完成。", "",
            "## 页面与覆盖层", "| 序号 | 源文件/入口/框架 | 类型 | ArkTS 目标文件/组件 | 功能归属 | 优先级 | confidence | 状态 | spec |",
            "|---|---|---|---|---|---|---|---|---|"]
    for p in pages:
        rows.append(f"| {p['page_id']} | `{p['source']}:{p['line']}` / {p['name']} / {p['framework']} | {p['kind']} | `{p['target']}` | F001 | {p['priority']} | {p['confidence']} | pending | `spec/baseline/ui/{p['page_id']}.md` |")
    if not pages:
        rows.append("| — | 未发现可判定页面候选 | — | — | F001 | P0 | low | blocked | — |")
    rows.extend(["", "## 页面内部显示态", "| 页面 | 前态/条件 | 显示结果 | 事件/转移 | 源依据 |", "|---|---|---|---|---|", "| pending | unknown | pending | pending | ios-facts.json |", "", "## 页面状态生命周期", "pending→converted→verified；verified 需要独立证据，不能由机器扫描赋予。", "", "## 共享组件与嵌入（子组件表）", "| 定义方 | 组件/目标接口 | 父页面/slot | 输入/事件 | feature |", "|---|---|---|---|---|", "| pending | pending | pending | pending | F001 |", "", "## 范围与证据", "机器候选来自 iOS 源码声明；截图/录像为 runtime=not_run，状态和视觉事实必须经过规格审阅。"])
    return "\n".join(rows) + "\n"


def _feature_index_text(index: dict, pages: list):
    rows = ["# Feature Index", MARKER, "source_platform: ios", "spec_contract_version: 2",
            f"source_sha256: {index.get('source_sha256', '')}", "",
            "## 领域模型概览", "公共模型待依据真实 iOS 状态/服务/持久化事实补充；完整字段见 feature-base。", "",
            "## 功能清单", "| ID | 功能 | 优先级 | 排序依赖 | 契约依赖 | 关联页面 | 创建页面 | complexity | tier | depth | 状态 | spec |",
            "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    page_ids = ", ".join(p["page_id"] for p in pages) or "—"
    rows.append(f"| F001 | iOS source behavior（待按用户行为拆分） | P0 | none | `spec/baseline/feature-base.md#数据模型` | {page_ids} | none | complex | core | full | pending | `spec/baseline/features/F001-ios-source.md` |")
    rows.extend(["", "## 依赖图", "feature-base → F001", "", "## 执行顺序（拓扑排序）", "1. feature-base", "2. F001", "", "## 生成边界", "机器登记不构成稳定功能边界；请保留源语义、入口、状态、事件和副作用证据。"])
    return "\n".join(rows) + "\n"


def generate_spec_gates(project: Path):
    """Generate source-derived spec inputs/reports after the facts stage."""
    project = Path(project).resolve()
    index, facts, files = _source_data(project)
    frozen = (project / 'spec/blueprint/contracts.json').exists()
    if frozen:
        pages = _page_candidates(project, files)
    else:
        rendered = render_spec_inputs(project)
        from .artifact_commit import create_missing
        create_missing(project, rendered['files'], before_commit=lambda: _source_data(project))
        pages = rendered['pages']
    base = project / "spec/baseline"
    if not frozen:
        _write_scaffold(base / "ui-manifest.md", _manifest_text(index, pages))
        _write_scaffold(base / "feature-index.md", _feature_index_text(index, pages))
    report = _coverage_report(project, index, _manifest_pages(project), candidates=pages)
    _write_report(project / "spec/ui-coverage-report.md", report)
    return {"status": "generated", "stage": "spec", "pages": len(pages),
            "feature_count": len(list((base / 'features').glob('F*.md'))),
            "ui_coverage": "PASS" if 'gate_status: PASS' in report else "BLOCKED"}


def _manifest_pages(project):
    from .artifact_contract import markdown_tables
    path = project / 'spec/baseline/ui-manifest.md'
    if not path.is_file():
        return []
    pages = []
    for table in markdown_tables(path.read_text(encoding='utf-8-sig')):
        headers = table['headers']
        if not headers or headers[0] not in {'page_id', '序号'} or 'spec' not in headers:
            continue
        for row in table['rows']:
            cells = dict(zip(headers, [cell.strip(' `') for cell in row]))
            ident = cells.get('page_id', cells.get('序号', ''))
            if not re.fullmatch(r'page_\d+', ident):
                continue
            pages.append({'page_id': ident, 'source': cells.get('源文件/入口/框架', ''),
                          'kind': cells.get('类型', 'page'),
                          'target': cells.get('ArkTS 目标文件/组件', ''),
                          'feature': cells.get('功能归属', ''), 'spec': cells['spec'],
                          'priority': cells.get('优先级', 'P1'), 'status': cells.get('状态', '')})
    return pages


def refresh_spec_reports(project: Path, gate=None):
    project = Path(project).resolve()
    index, _, files = _source_data(project)
    candidates = _page_candidates(project, files)
    text = _coverage_report(project, index, _manifest_pages(project), candidates=candidates, gate=gate)
    _write_report(project / 'spec/ui-coverage-report.md', text)
    return {'status': 'generated', 'report': 'spec/ui-coverage-report.md',
            'gate_status': 'PASS' if 'gate_status: PASS' in text else 'BLOCKED'}


def _coverage_report(project: Path, index: dict, pages: list, *, candidates=(), gate=None):
    from .ios_harness import check
    from .native_pipeline import context
    if gate is None:
        gate, _ = check(project, report_only=True)
    source, _ = context(project)
    known = {item['path']: item.get('sha256') for item in index.get('files', [])
             if isinstance(item, dict) and isinstance(item.get('path'), str)}
    # Exact identities preserve same-named classes in distinct modules/slices.
    # A candidate is trusted only while its source bytes match the inventory.
    available = {}
    for candidate in candidates:
        identity = _candidate_identity(candidate)
        try:
            file = safe_child(source, identity[0])
            if known.get(identity[0]) and digest(file.read_bytes()) == known[identity[0]] == candidate.get('sha256'):
                available[identity] = candidate
        except (MigrationError, OSError):
            continue
    authored, bindings = set(), {}
    for page in pages:
        path = safe_child(project, page['spec'])
        if path.is_file() and path.suffix == '.md' and path.is_relative_to(project / 'spec/baseline/ui'):
            text = path.read_text(encoding='utf-8-sig')
            for identity in _source_anchor_refs(text) & available.keys():
                bindings.setdefault(identity, set()).add(page['page_id'])
            if 'pending_authoring' not in text:
                authored.add(page['page_id'])
    unmapped = [item for item in candidates if _candidate_identity(item) not in bindings]
    status = 'PASS' if pages and len(authored) == len(pages) and not unmapped and gate.get('status') == 'PASS' else 'BLOCKED'
    rows = ["# iOS UI Coverage Report", MARKER, "source_platform: ios",
            f"source_sha256: {index.get('source_sha256', '')}", f"gate_status: {status}", "",
            "## 覆盖汇总", "| 类型原值 | 索引项 | 已有规格（非语义验收） | 结果 |", "|---|---:|---:|---|"]
    # Compound/source/target classifications stay intact. Names such as unused
    # do not approve an exclusion or remove anything from this inventory.
    kinds = list(dict.fromkeys(["page", "nested", "overlay"] + [p.get('kind') or 'unknown' for p in pages]))
    for kind in kinds:
        group = [p for p in pages if (p.get('kind') or 'unknown') == kind]
        rows.append(f"| {_cell(kind)} | {len(group)} | {sum(p['page_id'] in authored for p in group)} | {'PASS' if group and status == 'PASS' else ('未发现候选' if not group else 'PENDING')} |")
    rows.extend(["", "## 精确源身份登记", "| 源声明 | symbol | page_id |", "|---|---|---|"])
    for identity in sorted(bindings):
        relative, name, line = identity
        rows.append(f"| `{_cell(relative)}:{line}` | {_cell(name)} | {', '.join(sorted(bindings[identity]))} |")
    rows.extend(["", "## 阻断项"])
    missing = [p["page_id"] for p in pages if p["page_id"] not in authored]
    rows.append("- " + ("、".join(missing) + " 尚未绑定页面规格；需补充结构、状态、导航和验收。" if missing else "页面规格已存在，但仍需源门禁审阅状态和可观察验收。"))
    rows += [f"- 源规格门禁：{gate.get('status', 'NOT_RUN')}；发现 {len(gate.get('findings', []))} 项。"]
    rows += [f"- 未进入索引的源候选：`{_cell(p.get('path', p.get('source', '')))}:{p.get('line', 1)}` / {_cell(p.get('name', ''))}" for p in unmapped]
    rows.extend(["", "## 范围与未审项",
                 "按 manifest 保留类型原值；unused、non_product、system_owned 等标签不构成范围排除、实现完成或可达性证明。",
                 "本报告仅登记真实 source_anchors 的 path + symbol + line；不按同名类、缩写路径或同文件的其他 symbol 合并。",
                 "产品范围、条件分支、选定构建、库声明/死符号与未知实现由当前源门禁及其责任投影审阅；本报告未审这些语义，不将未审范围计为已验证。",
                 "", "## 结论", "机器覆盖只证明候选入口已登记，不能证明页面实现、视觉一致或运行时行为。"])
    return "\n".join(rows) + "\n"


def generate_plan_gates(project: Path, plan_input: Path | None = None):
    """Project actual plan responsibilities without changing frozen MD inputs.

    Canonical indexed plans remain the authoring input to plan-ir. These
    reports are a readable task projection and never an alternate scheduler.
    """
    from .ios_harness import check
    project = Path(project).resolve()
    index, _, _ = _source_data(project)
    gate, _ = check(project, report_only=True)
    pages = _manifest_pages(project)
    request = read_json(plan_input) if plan_input else {}
    tasks = request.get('tasks', [])
    gate_status = 'PROJECTED' if tasks and gate['status'] == 'PASS' else 'BLOCKED_BY_SPEC'
    header = [MARKER, 'source_platform: ios', 'spec_contract_version: 2',
              f"source_sha256: {index['source_sha256']}", f'gate_status: {gate_status}', '',
              '这是原生计划的只读投影。正式执行仍消费 indexed-v1、七字段局部责任表及 plan-ir 冻结合同。',
              '已存在的 canonical 计划已保留原文；本投影不会刷新旧草稿的责任或执行状态。规格更新后需原计划负责人审阅并重新生成正式计划。']
    ui_rows = ['# iOS UI Plan 责任投影', *header, '', '## 页面清单',
               '| page_id | iOS 来源 | 目标文件 | 功能归属 |', '|---|---|---|---|']
    for p in pages:
        ui_rows.append(f"| {p['page_id']} | {p['source']} | `{p['target']}` | {p['feature']} |")
    feature_rows = ['# iOS Feature Plan 责任投影', *header, '', '## 任务与依赖',
                    '| task_id | role | goal | parents | AC | ownership |', '|---|---|---|---|---|---|']
    for task in tasks:
        values = [task.get(k, '') for k in ('id', 'role', 'goal', 'parents', 'ac_ids', 'ownership')]
        feature_rows.append('| ' + ' | '.join(_cell(value) for value in values) + ' |')
    if not tasks:
        feature_rows += ['', '尚无通过 plan-ir 的 typed tasks；不自动猜测 Base/Slice/FV 所有权或 AC。']
    if not (project / 'spec/blueprint/contracts.json').exists():
        for name, title, projection in (
            ('ui-plan.md', 'UI Conversion Plan', 'ui-plan.md'),
            ('feature-plan.md', 'Feature Execution Plan', 'feature-plan.md'),
        ):
            draft = [f'# {title} — 等待正式计划', MARKER, 'spec_contract_version: 2',
                     'gate_status: BLOCKED_BY_PLAN_AUTHORING', '', '## Context',
                     '本文件为门禁初稿。源规格和稳定 AC 过门后，按原生 indexed 计划模板生成正式责任合同。',
                     '', '## 阻断与恢复',
                     'UI 需 Batch/owning_slice；功能需 Base/Slice/组收尾/FV-1/FV-2。',
                     '七字段局部责任表、Plan items JSON 与 typed tasks 必须逐字段一致，经 plan-ir 校验后冻结。',
                     '当前无可执行任务；不得据文件存在进入 execute。', '', '## 责任预览',
                     f'见 [只读投影](../../reports/derived/{projection})。']
            if name == 'feature-plan.md':
                draft.insert(3, 'plan_format: indexed-v1')
            _write_scaffold(project / 'spec/baseline/plans' / name, '\n'.join(draft) + '\n')
    plans = project / 'spec/reports/derived'
    _write_report(plans / 'ui-plan.md', '\n'.join(ui_rows) + '\n')
    _write_report(plans / 'feature-plan.md', '\n'.join(feature_rows) + '\n')
    return {'status': 'generated', 'stage': 'plan', 'gate_status': gate_status,
            'ui_plan': _rel(plans / 'ui-plan.md', project),
            'feature_plan': _rel(plans / 'feature-plan.md', project)}


def _cell(value):
    value = json.dumps(value, ensure_ascii=False) if not isinstance(value, str) else value
    return value.replace('|', '&#124;').replace('\n', '<br>')


def generate_verify_report(project: Path, *, build_evidence=None, write=True, scope=None):
    """Bind the native four-check report to current inputs and evidence bytes.

    A verifier may supply spec/verification/verify-results.json (version 1).
    Status text in an old report or a random build filename is never proof.
    """
    from .native_pipeline import context
    from .quality_views import summary, spec_inputs, target_inputs
    from .ios_harness import check
    source, project = context(Path(project))
    from .verification_scope import resolve as resolve_scope
    selected_scope = resolve_scope(scope) if scope is not None else None
    source_sha = snapshot(source)['sha256']
    gate, _ = check(project, report_only=True)
    summary_error = None
    try:
        view = summary(project, build_evidence=build_evidence, include_behavior=selected_scope is None or selected_scope['behavior']=='selected')
        spec_hashes, target_hashes = spec_inputs(project), target_inputs(project)
    except (MigrationError, OSError, ValueError) as exc:
        summary_error = str(exc)
        view = {'axes': {axis: {'status': 'unverified'} for axis in ('generation', 'compilation', 'behavior', 'visual')}}
        spec_hashes = target_hashes = None
    result_path = project / 'spec/verification/verify-results.json'
    results = read_json(result_path) if result_path.is_file() else {}
    bound = (summary_error is None and isinstance(results, dict) and results.get('schema_version') == 1
             and results.get('source_sha256') == source_sha
             and results.get('spec_input_hashes') == spec_hashes
             and results.get('target_input_hashes') == target_hashes)
    checks, seen = {}, set()
    entries = results.get('checks', []) if isinstance(results, dict) else []
    if not isinstance(entries, list):
        raise MigrationError('Verifier checks must be a list')
    for entry in entries:
        ident = entry.get('id') if isinstance(entry, dict) else None
        if ident not in {'CHECK-1', 'CHECK-2', 'CHECK-3', 'CHECK-4'} or ident in seen:
            raise MigrationError('Unknown or duplicate native verification check: ' + str(ident))
        seen.add(ident)
        state = entry.get('status')
        detail = entry.get('detail', '')
        evidence = entry.get('evidence', [])
        valid = bound and type(entry.get('selected')) is bool
        if state == 'SKIP':
            valid = valid and ident in {'CHECK-3', 'CHECK-4'} and entry['selected'] is False and bool(detail)
        elif state in {'PASS', 'FAIL'}:
            valid = valid and entry.get('selected') is True and isinstance(evidence, list) and bool(evidence)
            valid = valid and type(entry.get('exit_code')) is int and (state != 'PASS' or entry['exit_code'] == 0)
        elif state == 'DEFERRED':
            valid = valid and bool(detail)
        else:
            valid = False
        links = []
        for item in evidence if isinstance(evidence, list) else []:
            try:
                path = safe_child(project, item['path'])
                if (not item['path'].startswith('spec/') or path == result_path
                        or path == project / 'spec/verify-report.md'
                        or digest(path.read_bytes()) != item['sha256']):
                    valid = False
                links.append('`' + item['path'] + '`')
            except (MigrationError, OSError, TypeError, KeyError):
                valid = False
        checks[ident] = (state if valid else 'DEFERRED', detail if valid else '缺少当前输入绑定或证据已过期', ', '.join(links) if valid else '—')
    labels = {'CHECK-1': '静态分析', 'CHECK-2': 'App 身份校验', 'CHECK-3': '视觉对齐', 'CHECK-4': '单元测试'}
    for ident in labels:
        checks.setdefault(ident, ('DEFERRED', '尚未执行/选择；等待真实 verifier 结果', '—'))
    if selected_scope is not None:
        for ident in ('CHECK-3', 'CHECK-4'):
            if ident not in selected_scope['checks']:
                checks[ident] = ('SKIP', '用户未选择本轮检查', '—')
    values = [row[0] for row in checks.values()]
    overall = ('FAIL' if gate['status'] != 'PASS' or 'FAIL' in values else
               'PARTIAL' if 'DEFERRED' in values else 'PASS')
    rows = ['# 迁移验证报告', MARKER, 'source_platform: ios', f'source_sha256: {source_sha}',
            f'gate_status: {overall}', '', '## 四项结果',
            '| 编号 | 检查项 | 状态 | 结果摘要 | 证据 |', '|---|---|---|---|---|']
    rows += ['| ' + ' | '.join(_cell(v) for v in (ident, label, *checks[ident])) + ' |' for ident, label in labels.items()]
    rows += ['', '## 转换门禁与同轮派生证据', f"- 源规格门禁：{gate['status']}；{len(gate.get('findings', []))} 项待处理。",
             '- 当前生成/编译/行为/视觉轴见 `spec/migration-report.md` 与 `spec/reports/spec-summary.json`。',
             '', '| 证据轴 | 当前状态 |', '|---|---|']
    rows += [f"| {axis} | {data['status']} |" for axis, data in view['axes'].items()]
    if summary_error:
        rows += ['', '派生证据生成受阻：' + _cell(summary_error)]
    rows += ['', '## 未验证范围', 'DEFERRED、PARTIAL、not_run、unverified、stale 均不计为通过。SKIP 仅表示用户明确未选择设备项。',
             'Android 参考报告的扩展门禁不替换当前 iOS CHECK-1..4 编号；结构、路由、资源与编译各自保留原工具证据。',
             '', '## 输入绑定', f"input_sha256: {digest(json_bytes({'source': source_sha, 'spec': spec_hashes, 'target': target_hashes, 'results': digest(result_path.read_bytes()) if result_path.is_file() else None, 'axes': view['axes'], 'gate': gate, 'summary_error': summary_error}))}"]
    markdown = '\n'.join(rows) + '\n'
    if write:
        _write_report(project / 'spec/verify-report.md', markdown)
    return {'status': 'generated', 'stage': 'verify', 'gate_status': overall,
            'report': 'spec/verify-report.md', **({'markdown': markdown} if not write else {})}


def generate_execution_gates(project: Path, *, build_evidence=None, write=True):
    """Refresh the existing evidence summary after a landing operation."""
    from .quality_views import summary, render_report
    project = Path(project).resolve()
    path = project / "spec/migration-report.md"
    try:
        report = summary(project, build_evidence=build_evidence)
        markdown = render_report(report)
        state = 'available'
        if write:
            write_json(project / 'spec/reports/spec-summary.json', report)
    except (MigrationError, OSError, ValueError) as exc:
        from .native_pipeline import context
        source, _ = context(project)
        markdown = ('# 迁移证据报告\n' + MARKER + '\ngate_status: BLOCKED\n'
                    + 'source_sha256: ' + snapshot(source)['sha256'] + '\n\n'
                    + '## 证据生成阻断\n' + _cell(str(exc)) + '\n\n'
                    + '## 阶段总览\n| 阶段 | 所需证据 | 当前状态 |\n|---|---|---|\n'
                    + '| Stage 0 资源 | resource-mapping 与真实产物摘要 | unverified |\n'
                    + '| Stage 1 UI | 冻结任务、页面产物、落账与 brief | unverified |\n'
                    + '| Stage 2 Base | 公共合同、目标文件与落账 | unverified |\n'
                    + '| Stage 3 Slice | AC、接线、目标产物与落账 | unverified |\n'
                    + '| FV-1 结构收口 | 原结构工具与 loops JSON | unverified |\n'
                    + '| FV-2 终态编译 | 当前鸿蒙构建报告与 HAP 摘要 | unverified |\n\n'
                    + '生成、编译、行为、视觉状态均为 unverified。修复证据输入后重新生成并检查报告。\n')
        state = 'blocked'
    if write:
        _write_report(path, markdown)
    return {"status": "generated", "stage": "execute", "report": _rel(path, project),
            "summary_status": state, **({'markdown': markdown} if not write else {})}
