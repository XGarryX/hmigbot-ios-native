"""
main.py
Static ground truth 生成的入口脚本。
用法：python main.py <android_project_root>
"""
import argparse
import json
import re
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

# Progress is printed with arrows (→, ↔) and Chinese-derived text. When stdout is a
# pipe or redirect (subprocess capture, CI, log file) Python encodes it with the
# locale codec — cp936 on a Chinese Windows — which cannot represent those glyphs and
# crashes the whole scan with UnicodeEncodeError. Force UTF-8 on the streams instead.
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass


from extractors import function_graph_extractor, ground_truth_builder, navigation_extractor, source_extractor, xml_extractor, fragment_detector, dynamic_ui_extractor, behavior_chain_extractor
from extractors.dependency_resolver import resolve_dependencies
from generate_specs import generate_all_specs


def _merge_dict(base, extra):
    for k, v in extra.items():
        if k in base and isinstance(base[k], (int, float)):
            base[k] += v
        elif k in base and isinstance(base[k], dict):
            _merge_dict(base[k], v)
        elif k in base and isinstance(base[k], list):
            base[k].extend(v)
        else:
            base[k] = v


def detect_include_builds(project_root):
    paths = []
    root = Path(project_root).resolve()
    for name in ("settings.gradle.kts", "settings.gradle"):
        sf = root / name
        if not sf.exists():
            continue
        content = sf.read_text(encoding="utf-8", errors="ignore")
        for m in re.finditer(r'includeBuild\(["\']([^"\']+)["\']', content):
            dep = (root / m.group(1)).resolve()
            if dep.exists():
                paths.append(str(dep))
    return paths


def _print_spec_report(flat: list, dag: dict) -> None:
    try:
        _print_spec_report_impl(flat, dag)
    except UnicodeEncodeError:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[union-attr]
        _print_spec_report_impl(flat, dag)


def _print_spec_report_impl(flat: list, dag: dict) -> None:
    print("\n" + "=" * 70)
    print("路径报告 (SPEC REPORT — UI Paths)")
    print("=" * 70)

    ag = dag.get("aggregate_stats", {})
    print(f"  可达屏幕(reachable screens)：{ag.get('screens', 0)}")
    print(f"  路径总数(total paths)：{len(flat)}")

    print("\n" + "-" * 70)
    print("路径明细 (PATH DETAILS)")
    print("-" * 70)
    for p in flat:
        if isinstance(p, dict):
            print(f"  {p.get('path_display', p.get('path_id', ''))}")
        else:
            print(f"  {p}")

    print("\n" + "=" * 70)


def main():
    # Support TREE_SITTER_CACHE_DIR env var for offline machines (parser DLLs)
    _cache_dir = __import__("os").environ.get("TREE_SITTER_CACHE_DIR")
    if _cache_dir:
        try:
            from tree_sitter_language_pack import configure, PackConfig
            configure(PackConfig(cache_dir=_cache_dir))
        except Exception:
            pass

    parser = argparse.ArgumentParser(description="Generate static Android facts for harmony-migration-toolkit")
    parser.add_argument("android_project_root", nargs="?", default=".", help="Android project root")
    parser.add_argument(
        "--out",
        type=Path,
        default=None,
        help="Output directory (default: bundled_spec_tools/output)",
    )
    parser.add_argument(
        "--validate",
        action="store_true",
        help="Run verification after extraction and produce verification_report.json",
    )
    args = parser.parse_args()

    project_root = args.android_project_root

    out_dir = (args.out or (Path(__file__).parent / "output")).resolve()
    if out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    dep_roots = resolve_dependencies(project_root)
    print(f"项目(project)：{project_root}")
    if dep_roots:
        print(f"检测到的依赖库(dependencies)，共 {len(dep_roots)} 个：")
        for d in dep_roots:
            print(f"  {d}")
    print("=" * 50)

    # ── 阶段一：静态提取 ──

    # Step 1: XML 静态提取
    print("\n[1/9] 提取界面资源 (XML resources)…")
    xml_result = xml_extractor.run(project_root)
    for dep in dep_roots:
        dep_name = Path(dep).name
        dep_xml = xml_extractor.run(
            dep,
            source_prefix="library_xml_layout",
            menu_prefix="library_xml_menu",
            file_prefix=dep_name,
        )
        xml_result["elements"].extend(dep_xml["elements"])
        for lt_name, lt_tree in dep_xml.get("layout_trees", {}).items():
            xml_result.setdefault("layout_trees", {})[lt_name] = lt_tree
        xml_result["stats"]["total"] += dep_xml["stats"].get("total", 0)
        xml_result["stats"]["interactive"] += dep_xml["stats"].get("interactive", 0)
        xml_result["stats"]["hidden_by_default"] += dep_xml["stats"].get("hidden_by_default", 0)
        dep_strings = dep_xml.get("strings", {})
        xml_result.get("strings", {}).update(dep_strings)
    (out_dir / "static_xml.json").write_text(
        json.dumps(xml_result, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    s = xml_result["stats"]
    print(f"  界面控件总数(原始,含容器/库/重复)：{s['total']}")
    print(f"  └ 带交互标记的控件(标签/属性看似可点)：{s['interactive']}")
    print(f"  默认隐藏的控件(hidden)：{s['hidden_by_default']}")

    # Step 2: Source 静态扫描
    print("\n[2/9] 扫描源代码 (source code)…")
    src_result = source_extractor.run(project_root)
    symbol_payload, call_graph_payload = function_graph_extractor.run(project_root)
    for dep in dep_roots:
        dep_name = Path(dep).name
        dep_src = source_extractor.run(
            dep,
            file_prefix=dep_name,
            scan_events=True,
        )
        dep_symbols, dep_call_graph = function_graph_extractor.run(dep, file_prefix=dep_name)
        _merge_dict(src_result["findings"], dep_src["findings"])
        _merge_dict(src_result["stats"], dep_src["stats"])
        src_result.setdefault("view_ref_id_map", {}).update(dep_src.get("view_ref_id_map", {}))
        symbol_payload["symbols"].extend(dep_symbols.get("symbols") or [])
        call_graph_payload["symbols"].extend(dep_call_graph.get("symbols") or [])
        call_graph_payload["calls"].extend(dep_call_graph.get("calls") or [])
        call_graph_payload["unresolved_calls"].extend(dep_call_graph.get("unresolved_calls") or [])
    (out_dir / "source_findings.json").write_text(
        json.dumps(src_result, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    symbol_payload["symbols"].sort(key=lambda s: (s.get("file", ""), s.get("start_line", 0), s.get("symbol_id", "")))
    symbol_payload["stats"] = {
        "source_files_scanned": src_result["stats"].get("source_files_scanned", 0),
        "symbol_count": len(symbol_payload["symbols"]),
        "ast_symbol_count": sum(1 for s in symbol_payload["symbols"] if s.get("confidence") == "ast"),
    }
    call_graph_payload["symbols"] = symbol_payload["symbols"]
    call_graph_payload["calls"].sort(key=lambda c: (c.get("callsite_file", ""), c.get("callsite_line", 0), c.get("from_symbol_id", "")))
    call_graph_payload["unresolved_calls"].sort(key=lambda c: (c.get("callsite_file", ""), c.get("callsite_line", 0), c.get("from_symbol_id", "")))
    call_graph_payload["stats"] = {
        "symbol_count": len(call_graph_payload["symbols"]),
        "call_count": len(call_graph_payload["calls"]),
        "unresolved_call_count": len(call_graph_payload["unresolved_calls"]),
        "ast_call_count": sum(1 for c in call_graph_payload["calls"] if str(c.get("confidence", "")).startswith("ast")),
    }
    (out_dir / "function_symbols.json").write_text(
        json.dumps(symbol_payload, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    (out_dir / "call_graph.json").write_text(
        json.dumps(call_graph_payload, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    # 源码扫描各项的中文标签（未列出的 key 原样打印）
    _SRC_STAT_LABELS = {
        "id_dispatchers": "id 分发块(switch/when 派发点击)",
        "event_registrations": "事件监听注册(代码中 setOnXxxListener)",
        "visibility_controls": "动态显隐控制",
        "inflates": "布局加载(inflate)",
        "data_driven_ui": "数据驱动界面",
        "source_files_scanned": "已扫描源文件数",
        "findings_with_enclosing_symbol": "成功定位到所属函数的发现数",
    }
    for k, v in src_result["stats"].items():
        print(f"  {_SRC_STAT_LABELS.get(k, k)}：{v}")
    print(f"  函数总数(function symbols)：{symbol_payload['stats']['symbol_count']}")
    print(f"  函数调用关系(call edges)：{call_graph_payload['stats']['call_count']}")

    # Step 3: 合并 → ground truth
    print("\n[3/9] 合并为基准事实 (ground truth)…")
    gt = ground_truth_builder.build(
        xml_result,
        src_result,
        view_ref_id_map=src_result.get("view_ref_id_map"),
    )
    gt_path = out_dir / "ground_truth.json"
    gt_path.write_text(json.dumps(gt, indent=2, ensure_ascii=False), encoding="utf-8")

    s = gt["coverage_stats"]
    print(f"\n  基准事实已保存：{gt_path}")
    print(f"  可绑定控件(有 id、去重后)：{s['xml_elements_total']}")
    print(f"  └ 带交互信号-可点或已绑行为(interactive-or-bound)：{s['xml_interactive_or_bound']}")
    print(f"      ├ ★ 真正可交互-已确认点击行为(behavior-bound)：{s['xml_with_behavior_bound']}")
    print(f"      └ 仅 XML 标记可点、未追到行为：{s['xml_interactive_or_bound'] - s['xml_with_behavior_bound']}")
    print(f"  条件显隐(conditional visibility)：{s['xml_conditional_visibility']}")
    print(f"  动态控件-XML 中没有(dynamic gap)：{s['dynamic_gap_total']}（新增 {s['dynamic_gap_pure_new']}）")
    print(f"  数据驱动界面(data-driven UI)：{s['data_driven_ui']}")
    print(f"  非界面绑定-后台逻辑(non-UI)：{s['non_ui_bindings']}")
    print(f"  未匹配(unmatched)：{s['unmatched']}")

    # ── 阶段二：导航、区块与行为提取 ──

    # Step 4: 导航图提取
    print("\n[4/9] 提取导航图-屏幕跳转关系 (navigation graph)…")
    nav = navigation_extractor.run(project_root, dep_roots=dep_roots)
    nav_path = out_dir / "navigation_graph.json"
    nav_path.write_text(json.dumps(nav, indent=2, ensure_ascii=False), encoding="utf-8")

    from extractors import nav_pipeline as _nav_pipeline

    cand_payload = _nav_pipeline.build_candidates_payload(project_root, dep_roots)
    (out_dir / "navigation_candidates.json").write_text(
        json.dumps(cand_payload, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    ns = nav.get("stats", {})
    total_nodes = ns.get("total_nodes", 0)
    activity_nodes = ns.get("activity_nodes", 0)
    fragment_nodes = ns.get("fragment_nodes", 0)
    dialog_nodes = ns.get("dialog_nodes", 0)
    external_nodes = ns.get("external_nodes", 0)
    total_edges = ns.get("total_edges", 0)
    by_type = ns.get("by_type", {})
    print(f"\n  导航图已保存：{nav_path}")
    print(
        f"  导航线索-初步(candidates L1)：{cand_payload['stats']['total']} "
        f"（分类：{cand_payload['stats'].get('by_kind', {})}）"
    )
    print(f"  推断出的「代码类↔界面文件」对应：{len(nav.get('class_layouts', {}))}")

    # Router-framework pass results (TheRouter/ARouter/WMRouter): persist the route
    # table + unresolved list, and report how many nav edges came from string routes.
    _router = navigation_extractor.get_router_result()
    if _router and _router.get("stats"):
        rs = _router["stats"]
        (out_dir / "route_table.json").write_text(
            json.dumps(_router.get("route_table", {}), indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        if _router.get("unresolved"):
            (out_dir / "router_unresolved.json").write_text(
                json.dumps(_router["unresolved"], indent=2, ensure_ascii=False),
                encoding="utf-8",
            )
        print(
            f"  字符串路由框架(router)：@Route 声明 {rs.get('route_decl_total', 0)} → "
            f"解析路由表 {rs.get('route_table_size', 0)}；"
            f"发起点 {rs.get('call_sites_total', 0)} → 连边 {rs.get('edges_connected', 0)}，"
            f"运行时未定 {rs.get('unresolved', 0)}"
        )
        if rs.get("wrappers_detected"):
            print(f"    识别封装函数(wrapper)：{rs['wrappers_detected']}")

    # Augment class→layout with inflate-site ownership (strongest deterministic
    # signal) — recovers screens that navigation analysis never reaches.
    from extractors.inflate_owner_map import build_inflate_class_layouts, merge_into_nav
    inflate_class_layouts = build_inflate_class_layouts(src_result, call_graph_payload)
    added_mappings = merge_into_nav(nav, inflate_class_layouts)
    # Invert to layout → owning class for spec resolution, keeping only layouts with a
    # single inflating class so the spec's `class`/`screen_type` is filled from real
    # ground truth without guessing on shared/partial layouts (see generate_all_specs).
    _layout_owners: dict[str, set[str]] = {}
    for _cls, _layouts in inflate_class_layouts.items():
        for _ly in _layouts:
            _layout_owners.setdefault(_ly, set()).add(_cls)
    inflate_owner_layouts = {_ly: next(iter(_cs)) for _ly, _cs in _layout_owners.items() if len(_cs) == 1}
    if added_mappings:
        nav_path.write_text(json.dumps(nav, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"  由「谁加载了哪个布局」新补出的对应(inflate-derived)：{added_mappings}")
    print(f"  屏幕节点总数(screens)：{total_nodes} "
          f"（整屏 {activity_nodes} / 区块 {fragment_nodes} / 弹窗 {dialog_nodes} / 外部 {external_nodes}）")
    print(f"  屏幕间跳转总数(edges)：{total_edges}")
    _EDGE_TYPE_LABELS = {
        "activity": "跳到整屏页面",
        "dialog": "打开对话框",
        "commons_dialog": "打开通用弹窗",
        "fragment": "切换区块",
        "external_intent": "跳到外部应用",
    }
    for t, c in by_type.items():
        print(f"    └ {_EDGE_TYPE_LABELS.get(t, t)}：{c}")

    # Step 4b: Fragment 检测
    print("\n[5/9] 检测可复用区块 (fragments)…")
    frag_result = fragment_detector.run(project_root, dep_roots=dep_roots)
    (out_dir / "fragments.json").write_text(
        json.dumps(frag_result, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    fs = frag_result["stats"]
    print(f"  区块挂载点(fragments)：{fs['total']}（按挂载方式：{fs.get('by_attach_method', {})}）")
    cov = fs.get("coverage", {})
    if cov.get("ast_available"):
        nh = cov.get("needs_host_count", cov["declared_fragment_count"])
        base_n = cov.get("base_class_count", 0)
        print(f"  已挂载到界面的区块(attached)：{cov['attached_fragment_count']}/{nh}"
              f"（共声明 {cov['declared_fragment_count']} 个，其中抽象基类 {base_n} 个由子类挂载、不单独计）")
        if cov.get("orphan_classes"):
            print(f"  仍未追到挂载点的区块(orphan)：{len(cov['orphan_classes'])} 个 → {cov['orphan_classes']}")

    # Step 4c: 动态 UI 检测
    print("\n[6/9] 检测动态创建的界面 (dynamic UI)…")
    dyn_result = dynamic_ui_extractor.run(project_root, dep_roots=dep_roots)
    (out_dir / "dynamic_ui.json").write_text(
        json.dumps(dyn_result, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    ds = dyn_result["stats"]
    print(f"  纯代码创建的控件(dynamic elements)：{ds['total_dynamic_elements']} "
          f"（按方式：{ds.get('by_creation_method', {})}）")
    print(f"  长列表每行布局(adapter layouts)：{ds['total_adapter_layouts']}")

    gt = ground_truth_builder.build(
        xml_result,
        src_result,
        view_ref_id_map=src_result.get("view_ref_id_map"),
        nav_result=nav,
        adapter_layouts=dyn_result.get("adapter_layouts", []),
    )
    gt_path.write_text(json.dumps(gt, indent=2, ensure_ascii=False), encoding="utf-8")
    inferred_stats = gt.get("inferred_event_binding_stats", {})
    total = gt["coverage_stats"]["xml_interactive_or_bound"] + gt["coverage_stats"]["dynamic_gap_pure_new"]
    bound = gt["coverage_stats"]["xml_with_behavior_bound"]
    cross_bound = inferred_stats.get("covered", 0)
    uncovered = inferred_stats.get("uncovered", 0)
    _COVER_CAT_LABELS = {
        "value_read_on_confirm": "弹窗内输入(点确认时读值)",
        "dialog_action": "弹窗按钮(取消/关闭)",
        "framework_managed": "框架自动管理",
        "adapter_bindview": "列表项内控件",
    }
    if total > 0:
        pct = (bound + cross_bound) / total * 100
        print(f"\n  行为覆盖率：{bound + cross_bound}/{total} = {pct:.1f}%"
              f"（真正可交互控件 / 应有行为的控件）")
        print(f"    直接绑定(direct)：{bound}")
        if cross_bound:
            print(f"    跨组件推断(cross-component)：{cross_bound}")
            for cat, count in sorted(inferred_stats.get("by_category", {}).items(), key=lambda x: -x[1]):
                if cat != "programmatic":
                    print(f"      └ {_COVER_CAT_LABELS.get(cat, cat)}：{count}")
        if uncovered > 0:
            print(f"    仍未找到行为(uncovered)：{uncovered}")

    # Step 4d: 行为链提取
    print("\n[7/9] 提取行为链-点击到后果 (behavior chains)…")
    all_xml_ids = {e["id"] for e in xml_result["elements"] if e.get("id")}
    bc_result = behavior_chain_extractor.run(src_result, call_graph_payload, project_root,
                                              xml_ids=all_xml_ids)
    (out_dir / "behavior_chains.json").write_text(
        json.dumps(bc_result, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    bcs = bc_result["stats"]
    print(f"  事件绑定(bindings)：{bcs['total_bindings']}，已追出后果链：{bcs['with_effect_chain']}，"
          f"无处理代码：{bcs['without_handler']}")
    by_confidence = bcs.get("by_confidence", {})
    if by_confidence:
        static_count = by_confidence.get("static_analysis", 0)
        inferred_count = sum(
            by_confidence.get(key, 0)
            for key in ("fallback_analysis", "inferred")
        )
        print(f"  链的可信度(confidence)：{by_confidence}")
        print(f"  确定 vs 推断：确定(static){static_count}，推断(inferred){inferred_count}")
    if bcs.get("handler_resolution"):
        hrs = {k: v for k, v in bcs["handler_resolution"].items() if v}
        if hrs:
            print(f"  处理代码写法(handler resolution)：{hrs}")
    if bcs.get("fallback_chain"):
        print(f"  兜底链(fallback chain)：{bcs['fallback_chain']}")
    _STEP_LABELS = {
        "call": "方法调用(中间环节)", "navigate": "页面跳转", "ui_update": "改界面状态",
        "condition": "条件分支", "async": "异步/后台", "ui_feedback": "用户反馈(Toast等)",
    }
    steps_cn = {_STEP_LABELS.get(k, k): v for k, v in bcs.get("by_step_type", {}).items()}
    print(f"  链最深(max depth)：{bcs['max_chain_depth']}，各类步骤：{steps_cn}")

    # Step 5: Gap 合并
    gap_path = out_dir / "gap_analysis.json"
    gap = {"stats": {"total_resolved": 0, "by_gap_type": {}, "merged_into_gt": False}, "resolved": []}
    if gap_path.exists():
        gap = json.loads(gap_path.read_text(encoding="utf-8"))
        print(f"\n[可选] 缺口补充已载入(gap analysis)：{gap['stats']['total_resolved']} 项")
        for k, v in gap["stats"].get("by_gap_type", {}).items():
            print(f"  {k}：{v}")
        # 将 gap 条目合并到 ground_truth 的 dynamic_gap 中
        for item in gap.get("resolved", []):
            gt.setdefault("dynamic_gap", []).append({
                "layout": item.get("resolved_layout", ""),
                "gap_type": item.get("gap_type", ""),
                "source": item.get("file", ""),
                "file": item.get("file", ""),
                "enclosing_fn": item.get("trigger", ""),
                "view_ref": item.get("view_ref", ""),
                "behavior": item.get("behavior", ""),
                "resolved_xml_id": item.get("resolved_xml_id", ""),
            })
        gap["stats"]["merged_into_gt"] = len(gap.get("resolved", []))
        print(f"  已合并 {gap['stats']['merged_into_gt']} 项到基准事实的动态控件中")
    else:
        print("\n[可选] 未找到 gap_analysis.json —— 该补充步骤可选，跳过（正常）。")

    # Step 6: 动态组装 UI DAG — launcher from AndroidManifest MAIN/LAUNCHER
    print("\n[8/9] 组装可达屏幕树 (UI DAG)…")
    from extractors.ui_dag_assembler import assemble, assemble_all_flat_paths, assemble_flat_paths, set_output_dir
    from extractors.app_model_builder import build_and_write
    from extractors.app_model_schema import path_display_report_from_segments
    from extractors.ui_paths_nav_enumerator import enumerate_nav_paths

    # The assembler reads its inputs (nav/ground_truth/static_xml) from disk; point it
    # at the real out_dir so a non-default --out (e.g. the pipeline's
    # intermediate/0_android_facts) is read instead of the stale default output dir.
    set_output_dir(out_dir)

    launcher_class = navigation_extractor.get_launcher_activity_class(project_root)
    launcher_layout = ""
    if launcher_class:
        node = nav.get("nodes", {}).get(launcher_class, {})
        launcher_layout = node.get("layout", "") or nav.get("class_layouts", {}).get(
            launcher_class, ""
        )
        if not launcher_layout:
            for cname, cnode in nav.get("nodes", {}).items():
                if cname.lower() == launcher_class.lower():
                    launcher_layout = cnode.get("layout", "") or nav.get(
                        "class_layouts", {}
                    ).get(cname, "")
                    launcher_class = cname
                    break
    if not launcher_layout or not launcher_class:
        launcher_class = launcher_class or "BrowserActivity"
        launcher_layout = launcher_layout or "browser_activity"
        for cname, cnode in nav.get("nodes", {}).items():
            if cname == launcher_class or cname.lower() == launcher_class.lower():
                launcher_layout = cnode.get("layout", launcher_layout) or launcher_layout
                launcher_class = cname
                break
    print(f"  根屏幕-启动页(launcher)：{launcher_class}（布局 {launcher_layout}）")

    # Link Fragment / bottom-nav hosting into the nav graph so the reachable-screen
    # DAG follows host→fragment and screen→custom-view-host containment, not only
    # Activity startActivity jumps. Done here (after fragments + static_xml are
    # available) and re-persisted so `assemble`, which reads nav from disk, sees it.
    from extractors import containment_linker
    _cl_stats = containment_linker.merge_into_nav(
        nav, frag_result.get("fragments", []), xml_result,
        project_root, dep_roots=dep_roots,
    )
    if _cl_stats["added"]:
        nav_path.write_text(json.dumps(nav, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"  容器边补充(宿主→区块 / 屏幕→自定义View)：+{_cl_stats['added']} 条"
              f"（{_cl_stats['by_via']}）")

    dag = assemble(launcher_layout, max_depth=8)
    (out_dir / "ui_dag.json").write_text(
        json.dumps(dag, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    ag = dag.get("aggregate_stats", {})
    print(f"  从启动页可达的屏幕(reachable)：{ag.get('screens', 0)}")
    print(f"  这些屏幕上的控件总数：{ag.get('elements', 0)}")
    print(f"  └ 可交互：{ag.get('interactive', 0)}")
    print(f"  └ 带行为：{ag.get('with_behavior', 0)}")
    print(f"  └ 带跳转目标：{ag.get('with_navigation', 0)}")

    flat = assemble_flat_paths(launcher_layout, max_depth=8)
    all_flat, coverage_report = assemble_all_flat_paths(include_report=True)
    if all_flat:
        seen_flat = {p.get("path_id", "") for p in flat if isinstance(p, dict)}
        flat.extend(
            p for p in all_flat
            if isinstance(p, dict) and p.get("path_id", "") not in seen_flat
        )
    (out_dir / "ui_paths_coverage_report.json").write_text(
        json.dumps(coverage_report, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    strings_map = xml_result.get("strings") or {}
    for p in flat:
        if isinstance(p, dict) and p.get("segments"):
            p["path_display_report"] = path_display_report_from_segments(p["segments"], strings_map)

    effect_paths = _nav_pipeline.build_ui_effect_paths(
        project_root,
        dep_roots,
        strings_map,
        launcher_class=launcher_class,
    )
    (out_dir / "ui_effect_paths.json").write_text(
        json.dumps(effect_paths, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    (out_dir / "ui_paths.json").write_text(
        json.dumps(flat, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    legacy_strings = [
        p.get("path_display_legacy", p.get("path_display", ""))
        if isinstance(p, dict)
        else str(p)
        for p in flat
    ]
    legacy_strings.extend(
        p.get("path_display_legacy", "")
        for p in effect_paths.get("paths", [])
        if isinstance(p, dict) and p.get("path_display_legacy")
    )
    (out_dir / "ui_paths_legacy.json").write_text(
        json.dumps(legacy_strings, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    report_rows = [
        {
            "path_id": p.get("path_id", ""),
            "path_display_legacy": p.get("path_display_legacy", p.get("path_display", "")),
            "path_display_report": p.get("path_display_report", ""),
        }
        for p in flat
        if isinstance(p, dict)
    ]
    report_rows.extend(
        {
            "path_id": p.get("path_id", ""),
            "path_display_legacy": p.get("path_display_legacy", ""),
            "path_display_report": p.get("path_display_report", ""),
            "effect_kind": p.get("effect_kind", ""),
            "report_only": True,
            "source_file": p.get("source_file", ""),
            "line": p.get("line", 0),
        }
        for p in effect_paths.get("paths", [])
        if isinstance(p, dict)
    )
    (out_dir / "ui_paths_report.json").write_text(
        json.dumps(report_rows, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    # Isolated root nodes (0 inbound nav edges) that hold anonymous dialogs or
    # fragment children.  They are unreachable from the launcher via pure nav-graph
    # traversal, but their outbound edges carry useful trigger→target chains
    # (e.g. HomeActivity → showCampaignDialog → HomeActivity$showCampaignDialog$1).
    def _isolated_roots_with_useful_edges(nav_data: dict) -> list[str]:
        incoming: dict[str, int] = {}
        for e in nav_data.get("edges", []):
            if e.get("from") != e.get("to"):
                incoming[str(e.get("to") or "")] = incoming.get(str(e.get("to") or ""), 0) + 1
        roots = []
        for name in sorted(nav_data.get("nodes", {})):
            if incoming.get(name, 0) == 0 and name != launcher_class:
                # Only include roots that have outbound edges to anonymous children or
                # fragment destinations — pure leaf roots add nothing to enumeration.
                has_useful = False
                for e in nav_data.get("edges", []):
                    if e.get("from") == name and e.get("from") != e.get("to"):
                        if "$" in str(e.get("to", "")) or str(e.get("via", "")) in (
                            "fragment_host", "custom_view_host"
                        ):
                            has_useful = True
                            break
                if has_useful:
                    roots.append(name)
        return roots

    enum_payload = {
        "schema_version": "1.0",
        "start_class": launcher_class,
        "max_depth": 8,
        "max_paths_cap": 800,
        "paths": enumerate_nav_paths(
            nav,
            start_class=launcher_class,
            start_layout=launcher_layout,
            max_depth=8,
            max_paths=800,
            extra_roots=_isolated_roots_with_useful_edges(nav),
        ),
    }
    enum_payload["path_count"] = len(enum_payload["paths"])
    (out_dir / "ui_paths_enumerated.json").write_text(
        json.dumps(enum_payload, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    am_counts = build_and_write(out_dir, project_root, flat, nav, gt, xml_result)
    print(
        f"  界面效果路径(UI effect paths)：{effect_paths.get('path_count', 0)} "
        f"（分类：{effect_paths.get('stats', {}).get('by_effect_kind', {})}）"
    )
    print(f"  App 模型(app model)：{am_counts}")

    # ── 验证（仅在 --validate 时执行） ────────────────
    if args.validate:
        print("\n[V] 运行交叉验证 (verification)…")
        from extractors.ast_index import build_class_hierarchy, _resolve_android_base
        from verification import manifest_verifier, layout_verifier
        from verification.bytecode_verifier import bytecode_verifier as run_bytecode_verifier
        from verification.report import build_verification_report, print_verification_report

        ast_hierarchy = build_class_hierarchy(project_root, dep_roots)

        m_result = manifest_verifier(project_root, ast_hierarchy, _resolve_android_base)
        l_result = layout_verifier(project_root, ast_hierarchy, _resolve_android_base)
        b_result = run_bytecode_verifier(project_root, ast_hierarchy, _resolve_android_base)

        v_report = build_verification_report(m_result, l_result, b_result)
        (out_dir / "verification_report.json").write_text(
            json.dumps(v_report, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        print_verification_report(v_report)

    # ── Spec 报告 ──────────────────────────────────────────────────────────────
    _print_spec_report(flat, dag)

    # ── 阶段三：Spec 生成 ──

    # Step 7: 为导航图中的每个屏幕生成 HarmonyOS 迁移 spec
    print("\n[9/9] 生成每屏的鸿蒙迁移说明书 (specs)…")
    specs_dir = out_dir / "specs"
    specs_dir.mkdir(exist_ok=True)

    spec_stats = generate_all_specs(nav, gt, flat, dag, specs_dir,
                       layout_trees=xml_result.get("layout_trees"),
                       fragments=frag_result.get("fragments"),
                       dynamic_elements=dyn_result.get("dynamic_elements"),
                       behavior_chains=bc_result.get("behavior_chains"),
                       lifecycle_hooks=bc_result.get("lifecycle_hooks"),
                       adapter_layouts=dyn_result.get("adapter_layouts"),
                       inflate_owner_layouts=inflate_owner_layouts,
                       spec_version="2.0")

    generated = len(list(specs_dir.glob("*_spec.json")))
    print(f"  已生成 {generated} 份说明书 → output/specs/")

    if spec_stats and spec_stats["total_chains"] > 0:
        ss = spec_stats
        print(f"\n  行为链归属：{ss['total_chains']} 条"
              f" → 已分配 {ss['assigned']}，无归属 {ss['orphan']}，重复收走 {ss['duplicated']}")
        if ss.get("fallback_claimed"):
            print(f"  兜底认领(handler_class→layout)：{ss['fallback_claimed']}")
        print(f"  合成绑定-无监听控件(synthetic)：{ss['synthetic']}")
        print(f"  说明书中的事件绑定总数：{ss['total_event_bindings']}")

    # Non-UI component model: route orphan behavior-chains (services, app
    # widgets, receivers, listeners, playback infra…) to a component-level home
    # instead of forcing them onto an unrelated screen. Additive — does not
    # affect screen assignment above.
    from extractors.android_project import manifest_components
    from extractors.non_ui_components import build as build_non_ui_components
    from extractors.non_ui_components import inject_screen_backrefs
    all_chains = bc_result.get("behavior_chains") or []
    assigned_ids = set(spec_stats.get("assigned_chain_ids", [])) if spec_stats else set()
    orphan_chains = [c for i, c in enumerate(all_chains) if i not in assigned_ids]
    try:
        from verification.bytecode_verifier import bytecode_hierarchy
        bc_hier, _ = bytecode_hierarchy(project_root)
    except Exception:
        bc_hier = {}
    non_ui = build_non_ui_components(
        orphan_chains, manifest_components(project_root), bc_hier,
        call_graph=call_graph_payload, class_layouts=nav.get("class_layouts"))
    (out_dir / "non_ui_components.json").write_text(
        json.dumps(non_ui, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    # Reverse link: note each component as a non_ui_dependencies entry inside the
    # screen specs that drive it, so a screen-translating agent sees the coupling.
    link = inject_screen_backrefs(non_ui, specs_dir)
    nus = non_ui["stats"]
    print(f"\n  非界面组件(non-UI: 服务/卡片/接收器/监听器等)：{nus['components']} 个，来自 {nus['behaviors']} 条无归属行为链"
          f"（按类型：{nus['by_kind']}；按判定来源：{nus['by_kind_source']}）")
    print(f"  非界面组件 ↔ 屏幕关联：{nus['screen_links']} 条调用边指向屏幕；"
          f"已把依赖写入 {link['screen_specs_linked']} 份说明书"
          f"（{nus['components_with_callers']}/{nus['components']} 个组件有调用者）")
    if nus["excluded_ui_chains"]:
        print(f"  排除的界面类无归属链(留给屏幕路径处理)：{nus['excluded_ui_chains']}")

    # Combined behavior coverage: chains that found a home — claimed by a screen
    # spec OR routed to a non-UI component — over all extracted chains. The
    # remainder is genuinely homeless (UI orphans pending the screen path + chains
    # with no resolvable handler class).
    if spec_stats and spec_stats["total_chains"] > 0:
        total = spec_stats["total_chains"]
        homed = spec_stats["assigned"] + nus["behaviors"]
        pending_ui = sum(nus["excluded_ui_chains"].values())
        no_handler = nus["unclassified_orphan_chains"]
        print(f"\n  行为总覆盖率(屏幕 + 非界面)：{homed}/{total} = {homed / total * 100:.1f}%"
              f"  [屏幕 {spec_stats['assigned']} + 非界面 {nus['behaviors']}]")
        print(f"    仍无归属：{total - homed}（界面类待屏幕路径 {pending_ui} + 无处理代码 {no_handler}）")

    print("\n完成。输出文件：")
    for name in ["static_xml.json", "source_findings.json", "ground_truth.json",
                 "function_symbols.json", "call_graph.json",
                 "navigation_graph.json", "navigation_candidates.json",
                 "route_table.json",
                 "fragments.json",
                 "dynamic_ui.json",
                 "behavior_chains.json",
                 "non_ui_components.json",
                 "gap_analysis.json", "ui_dag.json",
                 "ui_paths.json", "ui_paths_legacy.json", "ui_paths_report.json",
                 "ui_effect_paths.json",
                 "ui_paths_enumerated.json",
                 "verification_report.json"]:
        exists = (out_dir / name).exists()
        marker = "OK" if exists else "MISSING"
        print(f"  [{marker}] output/{name}")
    am_index = out_dir / "app_model" / "index.json"
    print(f"  [{'OK' if am_index.exists() else 'MISSING'}] output/app_model/index.json")


if __name__ == "__main__":
    main()
