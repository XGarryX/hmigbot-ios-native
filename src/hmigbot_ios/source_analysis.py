"""One source-context planner and executor; source facts and authors retain their owners."""
from pathlib import Path
import time
import uuid

from .core import source_snapshot
from .core import MigrationError, digest, json_bytes, read_json, safe_child, snapshot, write_json

INPUTS = 'spec/ref/ios-source-analysis-inputs.json'


def frozen_inputs(project):
    path = project / INPUTS
    if not path.is_file():
        return {}
    value = read_json(path)
    if value.get('schema_version') != 1 or not isinstance(value.get('files'), dict):
        raise MigrationError('Unsupported source analysis input closure')
    result = {INPUTS: digest(path.read_bytes())}
    for relative, sha in value['files'].items():
        item = safe_child(project, relative)
        if not relative.startswith('spec/ref/') or not item.is_file() or digest(item.read_bytes()) != sha:
            raise MigrationError('Source analysis input changed: ' + relative)
        result[relative] = sha
    return result


def _replay_variant(project, source, plan, cfg):
    from .conditional_evidence import validate as validate_condition
    evidence = plan['evidence']
    bundle = Path(evidence['path'])
    variant = {'scope': 'selected-build', 'source_files': evidence['source_files'], 'evidence_path': str(bundle)}
    from .analysis_strategy import resolve_path
    declared = cfg.get('evidence', {}).get('conditional')
    candidates = [resolve_path(project, declared)] if declared else []
    if not declared:
        parent = project / 'spec/ref/ios-conditional-evidence'
        candidates = [p.parent for p in sorted(parent.glob('*/manifest.json'))] if parent.exists() else []
    rejected = []
    for candidate in candidates:
        try:
            condition = validate_condition(source, candidate, project=project)
            condition_manifest = read_json(candidate / 'manifest.json')
            if any(name.endswith('.swift') for name in evidence['source_files']) and condition_manifest.get('kind') != 'compiler_source_views':
                raise MigrationError('Selected Swift inputs require composed Swift/Clang compiler views')
            expected = condition['expected_build']
            selection = evidence['selection']
            if (any(selection.get(k) != expected[k] for k in ('scheme', 'configuration', 'sdk'))
                    or expected['target'] not in selection['targets'] or expected['architecture'] not in selection['architectures']):
                raise MigrationError('Conditional context differs from selected compiler membership')
            if evidence.get('projects') and expected['project'] not in evidence['projects']:
                raise MigrationError('Conditional project differs from selected compiler membership')
            conditional_build = Path(condition_manifest['build_evidence'])
            compiled = read_json(bundle / 'artifacts/source-files.json')
            build_log_sha = compiled.get('evidence', {}).get('captured_build_log', {}).get('sha256')
            conditional_log = conditional_build / 'artifacts/device-build.stdout.log'
            if not build_log_sha or not conditional_log.is_file() or digest(conditional_log.read_bytes()) != build_log_sha:
                raise MigrationError('Conditional and compiler membership evidence must bind the same captured build')
            return {'scope': 'selected-build', 'source_files': condition['members'],
                    'evidence_path': str(conditional_build), 'conditional_evidence': str(candidate),
                    'expected_build': expected, 'compilation_evidence_path': str(bundle)}, rejected
        except (MigrationError, OSError, ValueError, KeyError) as exc:
            if declared:
                raise MigrationError('Requested conditional replay rejected: ' + str(exc)) from exc
            rejected.append({'path': str(candidate), 'reason': str(exc)})
    # Repository inventory also includes tests and other unselected products.
    # Only an actual selected Swift compiler member can require its configured
    # source view; never trigger product recapture from an unrelated #if.
    selected_swift_conditionals = set(evidence['source_files']).intersection(
        plan.get('inventory', {}).get('swift_conditionals') or [])
    if selected_swift_conditionals:
        raise MigrationError('Selected Swift conditional source lacks a validated compiler view; '
                             'capture the current Xcode build context or select a matching existing view: '
                             + ', '.join(sorted(selected_swift_conditionals)))
    return variant, rejected


def run(project, *, variant=None, providers=None, manifest_evidence=None, apply_scaffold=False,
        analysis_config=None, plan_only=False, progress=None, mcp=None, source_ui=None):
    from .native_pipeline import context, index_source
    from .ios_harness import initialize
    from .ios_facts import refresh, obligations
    from .ios_literals import run as literal_index
    from .native_scaffold import scaffold, apply_scaffold as apply_candidate
    from .host import detect_host_profile
    from .provider_plan import preflight
    from .analysis_strategy import configuration, plan, resolve_path
    from .apple_capabilities import export_skills, discover_mcp, query_mcp, publish_guidance

    source, project = context(Path(project))
    if ((project / 'spec/state/state.json').exists()
            or any((project / 'spec/waves').glob('plan-*.json'))):
        raise MigrationError('Source analysis cannot mutate a planned project; use reviewed source-refresh/replan')
    current = source_snapshot(source)
    index_path = project / 'spec/baseline/ios-source-index.json'
    if index_path.exists():
        index = read_json(index_path)
        if index.get('source_sha256') != current['sha256'] or index.get('files') != current['files']:
            raise MigrationError('Source index is stale; preserve it and use reviewed source-refresh before analysis')
    cfg, config_ref = configuration(project, analysis_config)
    host_profile = detect_host_profile()
    from .xcode_mcp import resolve_choice, choice_card
    choice, origin = resolve_choice(project, mcp if mcp is not None else cfg.get('mcp'),
                                   configured_server=bool(cfg.get('mcp_server')))
    cfg = {**cfg, 'mcp': choice}
    choices = [choice_card({'choice': choice, 'choice_origin': origin},
        applicable=host_profile['host']['os'] == 'macos' and cfg.get('mode') not in {'static', 'replay'})]
    from .source_ui_capture import settings as ui_settings, choice_card as ui_choice
    cfg={**cfg,'ui_capture':ui_settings(project,cfg,source_ui)}
    choices.append(ui_choice(project,source,cfg))
    execution = plan(source, project, cfg, host_profile, explicit_providers=providers, variant=variant)
    execution['capability_choices'] = choices
    execution['user_action_required'] = any(c['requires_user_choice'] for c in choices)
    if plan_only:
        return {key: value for key, value in execution.items() if key != 'inventory'}
    run_dir = project / 'spec/ref/analysis-runs' / ('AR-' + uuid.uuid4().hex)
    run_dir.mkdir(parents=True)
    write_json(run_dir / 'plan.json', execution)
    write_json(run_dir / 'analysis-config.json', cfg)
    report_path = project / 'spec/reports/derived/source-analysis.json'
    steps = (['provider-plan-preflight'] if providers is not None else []) + ['harness', 'source-index'] + execution['steps']
    if manifest_evidence is not None or cfg.get('evidence', {}).get('manifest'):
        steps = [name for name in steps if name != 'manifest-evaluation']
    if apply_scaffold:
        steps += ['apply-scaffold', 'spec-authoring']
    report = {'schema_version': 2, 'status': 'running', 'source_sha256': current['sha256'],
              'spec_complete': False, 'behavior_verified': False, 'build': 'not_run',
              'host_profile': host_profile,
              'source_provider_selection': {**host_profile['source'], 'discovery_only': False,
                  'execution': 'automatic_context_plan' if providers is None else 'explicit_plan_override',
                  'selected_backend': execution['backend'], 'compiler_binding': 'unresolved',
                  'provider_plan_supplied': providers is not None},
              'execution_plan': str(run_dir / 'plan.json'), 'decisions': execution['decisions'],
              'capability_choices': choices,
              'user_action_required': any(c['requires_user_choice'] for c in choices),
              'stages': [], 'artifacts': {}, 'counts': {}, 'degraded': [],
              'progress': {'total': len(steps), 'completed': 0, 'failed': 0, 'blocked': 0, 'current': None}}
    started = time.monotonic()
    generated = []

    def save():
        report['elapsed_seconds'] = time.monotonic() - started
        write_json(report_path, report)
        write_json(run_dir / 'progress.json', report)
        if progress is not None:
            progress({'stage': 'spec/source-analysis', 'status': report['status'], **report['progress']})

    def artifact(path):
        body = path.read_bytes()
        report['artifacts'][path.relative_to(project).as_posix()] = {'sha256': digest(body), 'bytes': len(body)}

    def stage(name, action, *, optional=False):
        if source_snapshot(source)['sha256'] != current['sha256']:
            raise MigrationError('Source changed during automatic orchestration')
        stamp = time.monotonic()
        entry = {'name': name, 'status': 'running', 'step': len(report['stages']) + 1}
        report['stages'].append(entry)
        report['progress']['current'] = name
        save()
        try:
            result = action()
        except (MigrationError, OSError, ValueError, KeyError, TypeError) as exc:
            if not optional:
                entry.update(status='failed', error=str(exc))
                report['progress']['failed'] += 1
                save()
                raise
            result = {'status': 'unavailable', 'error': str(exc)}
        state = result.get('status') if isinstance(result, dict) else None
        if state in {'unavailable', 'capture_failed'}:
            entry.update(status='unavailable', reason=result.get('error', result.get('reason')))
            report['degraded'].append({'stage': name, 'detail': result})
        else:
            entry['status'] = 'completed'
        entry['elapsed_seconds'] = time.monotonic() - stamp
        report['progress']['completed'] += 1
        save()
        return result

    if progress is not None:
        progress({'stage': 'spec/source-analysis', 'status': report['status'],
                  **report['progress'], 'capability_choices': choices})
    save()
    try:
        if providers is not None:
            stage('provider-plan-preflight', lambda: preflight(providers))
        if execution['needs_input']:
            report.update(status='needs_input', needs_input=execution['needs_input'])
            report['progress']['blocked'] = report['progress']['total'] - report['progress']['completed']
            save()
            return {**report, 'report': str(report_path)}
        stage('harness', lambda: initialize(project))
        stage('source-index', lambda: {'status': 'reused'} if index_path.exists() else index_source(project))
        artifact(index_path)
        available = host_profile['source']['provider'] == 'macos_xcode'
        skills = stage('official-skills', lambda: export_skills(source, project, run_dir, execution['inventory'],
                       enabled=cfg.get('official_skills', True) and cfg.get('mode') != 'static', available=available), optional=True)
        discovery = stage('official-mcp-discovery', lambda: discover_mcp(source, project, run_dir, cfg, available=available), optional=True)
        effective_variant = variant
        native = None
        if execution['backend'] == 'native':
            from .native_source_capture import selection, capture
            selected = stage('native-selection', lambda: selection(source, execution['selection'], run_dir / 'native-selection'))
            native = stage('native-source-capture', lambda: capture(source, project, selected, run_dir / 'native',
                           need_conditionals=bool(execution['inventory']['c_conditionals'] or execution['inventory'].get('swift_conditionals')),
                           timeout=cfg.get('timeout_seconds', 600)))
            write_json(run_dir / 'native-capture-result.json', native)
            effective_variant = native['variant']
            generated.append({'operation': 'build-settings', 'input': native['compilation']})
            if native['clang_config']:
                generated.append({'operation': 'clang-ast', 'config': native['clang_config']})
            report['build'] = 'source_build_captured'
        elif execution['backend'] == 'replay':
            def replay():
                value, rejected = _replay_variant(project, source, execution, cfg)
                report['rejected_conditional_evidence'] = rejected
                return value
            effective_variant = stage('replay-evidence', replay)
            generated.append({'operation': 'build-settings', 'input': execution['evidence']['path']})
            frozen_clang = Path(execution['evidence']['path']) / 'artifacts/clang-provider.json'
            if available and cfg.get('mode') != 'static' and frozen_clang.is_file():
                generated.append({'operation': 'clang-ast', 'config': str(frozen_clang)})
            report['build'] = 'source_build_evidence_replayed'
        if 'swift-syntax-provider' in steps:
            from .native_source_capture import swift_provider
            built = stage('swift-syntax-provider', lambda: {'config': str(swift_provider(source, run_dir / 'swift-provider'))}, optional=True)
            if built.get('config'):
                generated.append({'operation': 'swift-syntax', 'config': built['config']})
        if 'manifest-evaluation' in steps:
            from .manifest_evidence import capture as evaluate
            manifests = [f['path'] for f in current['files'] if Path(f['path']).name == 'Package.swift']
            conf = run_dir / 'manifest-config.json'
            write_json(conf, {'schema_version': 1, 'manifests': [{'path': p,
                'command': ['swift', 'package', '--package-path', '{package_dir}', 'dump-package'],
                'version_command': ['swift', '--version']} for p in manifests]})
            output = project / 'spec/ref/ios-manifest-evidence' / run_dir.name
            result = stage('manifest-evaluation', lambda: evaluate(source, conf, output), optional=True)
            if result.get('status') != 'capture_failed' and (output / 'manifest.json').is_file():
                manifest_evidence = output
        elif cfg.get('evidence', {}).get('manifest') and manifest_evidence is None:
            manifest_evidence = resolve_path(project, cfg['evidence']['manifest'])
        # Add inventory providers only when the source contains their actual input.
        paths = [f['path'] for f in current['files']]
        for operation, applies in [('interface-builder', any(Path(p).suffix in {'.xib', '.storyboard'} for p in paths)),
                ('asset-inventory', any('.xcassets/' in p for p in paths)),
                ('localization-inventory', any(Path(p).suffix in {'.strings', '.stringsdict', '.xcstrings'} for p in paths))]:
            if applies:
                generated.append({'operation': operation})
        if providers is None and generated:
            providers = run_dir / 'provider-plan.json'
            write_json(providers, {'schema_version': 2, 'providers': generated})
            preflight(providers)
        graph = stage('facts', lambda: refresh(project, source, effective_variant, providers, manifest_evidence))
        for name in ('ios-facts.json', 'ios-obligations.json'):
            artifact(project / 'spec/baseline' / name)
        literals = stage('literals', lambda: literal_index(project))
        artifact(project / 'spec/baseline/literal-ledger.json')
        mcp = stage('official-mcp-evidence', lambda: query_mcp(project, source, graph, run_dir, execution['inventory'], discovery), optional=True)
        guidance = publish_guidance(project, graph, skills, mcp)
        if cfg.get('require_official') and not guidance['official_resources']:
            raise MigrationError('Required official guidance unavailable; inspect actual Apple skill/MCP diagnostics')
        from .expertise import prepare
        stage('expertise-plan', lambda: prepare(project), optional=True)
        from .source_ui_capture import execute as capture_ui, INDEX as UI_INDEX
        ui=stage('source-ui',lambda:capture_ui(project,source,run_dir,cfg))
        report['source_ui']=ui
        artifact(project/UI_INDEX)
        if ui['required'] and ui['status']!='captured':
            report.update(status='needs_ui_evidence')
            report['progress']['blocked']=max(0,report['progress']['total']-report['progress']['completed'])
            report['next']=['Resolve the explicitly selected source UI scope/build/device/evidence and rerun before authoring; independent source facts are retained']
            save()
            return {**report,'report':str(report_path)}
        if cfg.get('mode') == 'static':
            # Explicit file-only scope may not launch a compiler. The removed
            # Python declaration parser is not restored to manufacture pages.
            candidate = stage('spec-scaffold', lambda: {
                'schema_version': 2, 'kind': 'spec-scaffold-candidate', 'status': 'unavailable',
                'reason': 'Explicit static scope has no official AST; provide native/replayed SwiftSyntax evidence before scaffolding',
                'source_sha256': current['sha256'], 'spec_complete': False, 'behavior_verified': False,
                'enterable_plan': False, 'candidates': [], 'files': {},
                'summary': {'total_candidates': 0, 'pages': 0, 'features': 0}})
        else:
            candidate = stage('spec-scaffold', lambda: scaffold(project, source_sha256=current['sha256']))
        candidate_path = project / 'spec/reports/derived/spec-scaffold.json'
        write_json(candidate_path, candidate)
        artifact(candidate_path)
        if apply_scaffold:
            if candidate.get('status') == 'unavailable':
                raise MigrationError(candidate['reason'])
            applied = stage('apply-scaffold', lambda: apply_candidate(project, candidate))
            if applied.get('refused'):
                raise MigrationError('Scaffold apply refused candidate files; inspect retained candidate')
            from .native_authoring import prepare as author
            authoring = stage('spec-authoring', lambda: author(project))
            path = project / 'spec/reports/derived/spec-authoring.json'
            write_json(path, authoring)
            artifact(path)
            report['applied'] = applied
        if source_snapshot(source)['sha256'] != current['sha256'] or graph['source_sha256'] != current['sha256'] or literals['source_sha256'] != current['sha256']:
            raise MigrationError('Source changed during analysis; fresh capture and review required')
        if config_ref and digest(Path(config_ref['path']).read_bytes()) != config_ref['sha256']:
            raise MigrationError('Analysis configuration changed during execution')
        closure = {}
        for path in run_dir.rglob('*'):
            if path.is_file() and 'DerivedData' not in path.parts and path.name != 'progress.json':
                closure[path.relative_to(project).as_posix()] = digest(path.read_bytes())
        for name in ('spec/ref/ios-official-analysis.json', 'spec/ref/ios-apple-skills.json'):
            path = project / name
            if path.is_file():
                closure[name] = digest(path.read_bytes())
        from .source_ui_capture import frozen_inputs as ui_inputs
        closure.update(ui_inputs(project,source))
        write_json(project / INPUTS, {'schema_version': 1, 'source_sha256': current['sha256'], 'files': closure})
        report['counts'] = {'source_files': len(current['files']), 'facts': len(graph['facts']),
                            'obligations': len(obligations(graph)['obligations']),
                            'extraction_issues': len(graph['issues']), 'candidates': candidate['summary']}
        from .apple_capabilities import topics
        needed = set(topics(execution['inventory']['tokens']))
        supplied_topics = set(guidance['official_resources'])
        report['official_capabilities'] = {'apple_skills': skills['status'], 'xcode_mcp': mcp['status'],
            'official_topics': sorted(supplied_topics), 'fallback_topics': sorted(needed - supplied_topics),
            'primary_guidance': ('Apple' if needed and needed <= supplied_topics else 'mixed_with_declared_fallback'
                                 if supplied_topics else 'declared_third_party_or_static_fallback')}
        report['official_execution'] = {
            'swift_fact_input': graph.get('syntax_consumption', {}).get('swift', 'python_static_fallback'),
            'swift_literal_input': literals.get('syntax_consumption', {}).get('swift', 'python_static_fallback'),
            'string_decoding': literals.get('syntax_consumption', {}).get('string_decoding', 'limited_python_fallback'),
            'compiler_binding': 'unresolved',
            'runtime': 'source_ui_observed' if ui['status']=='captured' else 'not_run',
            'source_ui_execution': 'actual_capture_now' if ui.get('actual_native_ui_run') else 'reused_current_capture' if ui.get('reused') else ui['status'],
            'skill_guidance_loaded': bool(skills.get('loaded')),
            'skill_semantic_review': 'required',
            'mcp_successful_calls': len(mcp.get('captures', []))}
        report['status'] = 'needs_review'
        report['progress']['current'] = None
        report['next'] = ['Read the selected official guidance and current source evidence',
                          'Read the selected native source UI observations and original images in spec-authoring; captures are scoped observations, not default values',
                          'Review candidates, unknowns, semantics, responsibility and ACs',
                          'Run spec-check and source-check --harness before plan-ir']
        save()
        return {**report, 'report': str(report_path)}
    except (MigrationError, OSError, ValueError, KeyError, TypeError) as exc:
        report.update(status='failed', error=str(exc))
        report['progress']['blocked'] = max(0, report['progress']['total'] - report['progress']['completed'] - report['progress']['failed'])
        save()
        raise MigrationError(str(exc) + '; retained analysis receipt: ' + str(report_path)) from exc
