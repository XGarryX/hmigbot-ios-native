"""Read-only binding to standalone HMigBot and source-to-target skill handoff.

Skills are agent procedures, not executable APIs. A prepared packet is never
reported as executed code. Original Android pipeline contracts are not forged.
"""
from __future__ import annotations

import os
from pathlib import Path
import re

from .analyze import analyze
from .core import source_snapshot
from .core import MigrationError, anchor, digest, io_path, json_bytes, read_json, safe_child, snapshot, write_json, write_new_tree

BINDING = 'hmigbot-binding/1'
CONTRACT = 'ios-harmony-contract/1'
# Required fields describe source semantics, not a target implementation guess.
ROUTES = {
    'project': (['arkts-project-scaffolder'], ['identity', 'modules', 'entry', 'sdk']),
    'types': (['arkts-data-layer'], ['fields', 'invariants', 'serialization']),
    'business': (['arkts-codebase-modifier'], ['inputs', 'outputs', 'branches', 'side_effects']),
    'view': (['arkts-component-builder'], ['nodes', 'properties', 'conditional_visibility']),
    'layout': (['arkts-component-builder'], ['constraints', 'adaptation', 'units']),
    'state': (['arkts-state-manager'], ['owners', 'initial_values', 'transitions']),
    'events': (['arkts-component-builder', 'arkts-state-manager'], ['bindings', 'handlers', 'effects']),
    'navigation': (['arkts-navigation-builder'], ['routes', 'parameters', 'back_behavior']),
    'concurrency': (['arkts-data-layer'], ['ordering', 'cancellation', 'error_propagation']),
    'network': (['arkts-data-layer'], ['requests', 'responses', 'errors', 'authentication']),
    'storage': (['arkts-data-layer'], ['schema', 'operations', 'upgrades', 'failure_behavior']),
    'system-service': (['arkts-system-capabilities'], ['source_api', 'behavior', 'permissions', 'replacement_decision']),
    'dependency': (['hmos-sdk-docs', 'arkts-knowledge-verifier'], ['source_library', 'used_surface', 'replacement_decision']),
    'resources': (['arkts-component-builder'], ['source_assets', 'target_mapping', 'variants']),
    'localization': (['arkts-i18n'], ['keys', 'locales', 'format_semantics']),
    'lifecycle': (['arkts-project-scaffolder'], ['callbacks', 'ordering', 'state_restoration']),
    'identity': (['arkts-project-scaffolder'], ['source_identity', 'target_identity', 'permissions']),
    'build': (['hmos-fix-build-errors'], ['sdk', 'deveco_path', 'product', 'module']),
    'tests': ([], ['cases', 'source_oracle', 'target_observation']),
    'accessibility': (['arkts-accessibility'], ['semantics', 'focus_order', 'scenarios']),
}
SUPPORT_SKILLS = ['arkts-knowledge-verifier', 'hmos-sdk-docs', 'hmos-env-doctor']
BLOCKED_ROUTES = {'tests': 'Original arkts-ut-verifier requires Android oracle/spec and registered roles; iOS consumer adaptation is not implemented'}
SKILLS = sorted({s for skills, _ in ROUTES.values() for s in skills} | set(SUPPORT_SKILLS))
SKIP = {'bin', '__pycache__', '.git', 'node_modules'}


def binding_data(root: Path):
    root = io_path(root).resolve()
    manifest = read_json(root / '.codex-plugin/plugin.json')
    if (not isinstance(manifest, dict) or manifest.get('name') != 'migbot' or manifest.get('version') != '1.6.1'
            or 'hmigbot-CodeX' not in manifest.get('repository', '')
            or not (root / 'skills/a2h-run/SKILL.md').is_file()):
        raise MigrationError('Select standalone HMigBot CodeX 1.6.1, not HMigBot Plus or the iOS adapter')
    records = {}
    for name in SKILLS:
        entry = safe_child(root, f'skills/{name}/SKILL.md')
        if not entry.is_file() or not re.search(r'^name:\s*' + re.escape(name) + r'\s*$', entry.read_text(encoding='utf-8-sig'), re.M):
            raise MigrationError('Missing or mismatched HMigBot skill: ' + name)
        records[name] = {'entry': str(entry), 'files': {}}
        for parent, dirs, names in os.walk(entry.parent, followlinks=False):
            dirs[:] = sorted(d for d in dirs if d not in SKIP)
            for child in dirs + names:
                path = io_path(Path(parent) / child)
                if path.is_symlink() or (hasattr(path, 'is_junction') and path.is_junction()):
                    raise MigrationError('HMigBot skill contains a link: ' + str(path))
            for file in sorted(names):
                path = io_path(Path(parent) / file)
                if path.suffix != '.pyc':
                    records[name]['files'][path.relative_to(root).as_posix()] = digest(path.read_bytes())
    return {'schema_version': BINDING, 'root': str(root), 'upstream': manifest,
            'manifest_sha256': digest((root / '.codex-plugin/plugin.json').read_bytes()),
            'skills': records, 'binary_integrity': 'not_checked', 'status': 'bound',
            'execution': 'agent_reads_original_skill_and_references; no migration has run'}


def bind(root: Path, output: Path):
    root, output = root.resolve(), output.resolve()
    if output.exists() or output.is_relative_to(root):
        raise MigrationError('Use a new binding file outside original HMigBot')
    data = binding_data(root)
    write_json(output, data)
    return {'status': 'bound', 'binding': str(output), 'upstream_root': str(root), 'skills': len(data['skills'])}


def check_binding(path: Path):
    prior = read_json(path)
    if not isinstance(prior, dict) or prior.get('schema_version') != BINDING or not isinstance(prior.get('root'), str):
        raise MigrationError('Invalid HMigBot binding')
    current = binding_data(Path(prior['root']))
    if prior != current:
        raise MigrationError('HMigBot binding changed; review the upstream change and bind to a new file')
    return current


def disjoint(*paths):
    roots = [p.resolve() for p in paths]
    if any(a.is_relative_to(b) or b.is_relative_to(a) for i, a in enumerate(roots) for b in roots[i+1:]):
        raise MigrationError('Source, target, packet and original HMigBot paths must not overlap')


def contract_draft(source: Path, output: Path):
    source, output = source.resolve(), output.resolve()
    disjoint(source, output)
    facts = analyze(source)
    units = []
    def add(kind, title, refs, source_facts):
        units.append({'id': f'U{len(units)+1:04d}', 'kind': kind, 'title': title,
            'source_anchors_ref': refs, 'source_facts': source_facts,
            'status': 'needs_analysis', 'disposition': 'migrate', 'depends_on': [],
            'contract': {key: None for key in ROUTES[kind][1]}, 'target_files': [], 'acceptance': []})
    covered = set()
    for page in facts['pages']:
        add('view', page['path'], [anchor(page['path'], page['sha256'])], page)
        covered.add(page['path'])
    for file in facts['source_snapshot']['files']:
        if file['path'] not in covered and Path(file['path']).suffix.lower() in {'.swift', '.m', '.mm', '.c', '.cpp', '.h'}:
            add('business', file['path'], [anchor(file['path'], file['sha256'])],
                {'scope': 'file discovery only; split into actual functions/features before implementation'})
    for fact in facts['facts']:
        kind = {'platform_service': {'network': 'network', 'persistence': 'storage', 'preferences': 'storage'}.get(
            fact['value'].get('category'), 'system-service'), 'asset_catalog': 'resources',
            'localization': 'localization', 'dependency': 'dependency'}.get(fact['kind'])
        if kind:
            add(kind, fact['id'], fact['source_anchors_ref'], fact)
    result = {'schema_version': CONTRACT, 'source_platform': 'ios', 'target_platform': 'harmonyos',
        'source_sha256': facts['source_snapshot']['sha256'], 'target_sdk': None, 'units': units,
        'scope': 'discovered candidates; not a complete feature inventory', 'unresolved': facts['issues']}
    write_new_tree(output, {'contract.json': json_bytes(result), 'facts.json': json_bytes(facts)})
    return {'status': 'needs_analysis', 'contract': str(output / 'contract.json'), 'units': len(units), 'code_generated': False}


def check_anchors(source, files, refs):
    if not isinstance(refs, list) or not refs:
        raise MigrationError('Every unit and acceptance case needs source anchors')
    for ref in refs:
        if not isinstance(ref, dict) or not isinstance(ref.get('path'), str) or ref.get('path') not in files or ref.get('sha256') != files[ref['path']]:
            raise MigrationError('Missing or stale source anchor')
        line = ref.get('line')
        if type(line) is not int or line < 1 or line > max(1, len(safe_child(source, ref['path']).read_bytes().splitlines())):
            raise MigrationError('Source anchor line is outside the file')


def nonempty(value):
    return value is not None and value != '' and value != [] and value != {}


def handoff(source: Path, target: Path, contract_path: Path, binding_path: Path, output: Path, selected=None):
    source, target, output = source.resolve(), target.resolve(), output.resolve()
    binding = check_binding(binding_path)
    disjoint(source, target, output, Path(binding['root']))
    contract = read_json(contract_path)
    current = source_snapshot(source)
    if (not isinstance(contract, dict) or contract.get('schema_version') != CONTRACT or contract.get('source_platform') != 'ios'
            or contract.get('target_platform') != 'harmonyos' or contract.get('source_sha256') != current['sha256']):
        raise MigrationError('Invalid or stale iOS-to-HarmonyOS contract')
    if not isinstance(contract.get('target_sdk'), str) or not contract['target_sdk'].strip():
        raise MigrationError('Specify the actual target SDK before creating implementation tasks')
    units = contract.get('units')
    if not isinstance(units, list) or not units or any(not isinstance(u, dict) for u in units):
        raise MigrationError('Contract needs migration units')
    ids = [u.get('id') for u in units]
    if any(not isinstance(i, str) or not re.fullmatch(r'[A-Za-z0-9_-]+', i) for i in ids) or len(set(ids)) != len(ids):
        raise MigrationError('Unit IDs must be unique portable identifiers')
    selected = list(selected) if selected else ids
    if not set(selected) <= set(ids) or len(set(selected)) != len(selected):
        raise MigrationError('Selected units are missing or duplicated')
    files = {f['path']: f['sha256'] for f in current['files']}
    todo = {u['id']: u for u in units if u['id'] in selected}
    # Require dependency closure. Never imply a skipped dependency was implemented.
    for unit in todo.values():
        deps = unit.get('depends_on')
        if not isinstance(deps, list) or any(not isinstance(d, str) or d not in todo for d in deps):
            raise MigrationError('Select all unit dependencies in the handoff')
    ordered = []
    pending = dict(todo)
    while pending:
        ready = [u for u in pending.values() if set(u['depends_on']) <= set(ordered)]
        if not ready:
            raise MigrationError('Migration unit dependencies contain a cycle')
        for unit in ready:
            ordered.append(unit['id'])
            del pending[unit['id']]
    outputs, packets, owners = {}, [], {}
    for uid in ordered:
        unit = todo[uid]
        kind = unit.get('kind')
        if not isinstance(kind, str) or kind not in ROUTES:
            raise MigrationError('No audited HMigBot route for unit kind: ' + str(kind))
        if kind in BLOCKED_ROUTES:
            raise MigrationError(BLOCKED_ROUTES[kind])
        if unit.get('status') != 'ready' or unit.get('disposition') != 'migrate':
            raise MigrationError('Unit ' + uid + ' still needs source analysis or an explicit disposition')
        check_anchors(source, files, unit.get('source_anchors_ref'))
        semantics = unit.get('contract')
        if not isinstance(semantics, dict) or any(not nonempty(semantics.get(k)) for k in ROUTES[kind][1]):
            raise MigrationError('Missing source semantics for ' + uid + ': ' + ', '.join(ROUTES[kind][1]))
        dests = unit.get('target_files')
        if not isinstance(dests, list) or not dests or any(not isinstance(p, str) for p in dests):
            raise MigrationError('Each unit needs explicit target files')
        for path in dests:
            safe_child(target, path)
            # Shared files have serial writers; output records make this explicit.
            owners.setdefault(path.casefold(), []).append(uid)
        cases = unit.get('acceptance')
        if not isinstance(cases, list) or not cases:
            raise MigrationError('Each unit needs source-based acceptance cases')
        for case in cases:
            if not isinstance(case, dict) or any(not isinstance(case.get(k), str) or not case[k].strip() for k in ('id', 'given', 'when', 'then')):
                raise MigrationError('Acceptance cases need id, given, when and then')
            check_anchors(source, files, case.get('source_anchors_ref'))
        names = list(dict.fromkeys(ROUTES[kind][0] + SUPPORT_SKILLS))
        packet = {'unit': unit, 'source_root': str(source), 'target_root': str(target),
            'target_sdk': contract['target_sdk'], 'source_sha256': current['sha256'],
            'skill_entries': {s: binding['skills'][s]['entry'] for s in names},
            'upstream_root': binding['root'], 'input_mode': 'source_semantic_contract',
            'execution_mode': 'advice_then_adapter_implementation' if kind in {'business', 'dependency'} else 'original_target_skill',
            'status': 'prepared_not_executed', 'code_generated': False}
        outputs[f'tasks/{uid}.json'] = json_bytes(packet)
        text = [f'# {uid}: {unit.get("title", kind)}', '',
            '本任务将 iOS 源码中已提取的功能实现为原生鸿蒙代码。任务包不是转换结果。',
            '读取同名 JSON、其中的源文件锚点，以及以下原 HMigBot 技能和所需 references。', '',
            *[f'- `{s}`: `{binding["skills"][s]["entry"]}`' for s in names], '',
            '按原技能实际编写 target_files 中的代码并接线；不得仅交付描述、空回调或占位。',
            'business: arkts-codebase-modifier 只提供建议；由本适配器依据源契约实际编码，不能称原技能自动转译业务。',
            'dependency: 替代决策由适配器完成；原 SDK 文档只核验已选依赖的集成事实，不执行 Android 库选型流程。',
            '组件技能使用模式 A（描述驱动）；描述来自 contract，不传 android_layout/android_class。',
            '相对 references/scripts 路径按原技能目录解析；跨技能引用按 upstream_root/skills 解析。',
            '目标 API 以本任务 SDK、本机 SDK 和官方文档为准，原技能模板不是版本可用性证明。',
            '涉及其他原技能先读取其真实文件；Android 事实/ADB/Activity 参数不适用，记录适配缺口，不能伪造。',
            '不进入旧 a2h-run/a2h-execute，不设置 .done，不启动遥测。',
            '按 acceptance 逐项验证。分别记录实际改动、构建、行为观察和未完成项；缺少设备观察不算行为通过。', '']
        outputs[f'tasks/{uid}.md'] = '\n'.join(text).encode('utf-8')
        packets.append({'id': uid, 'kind': kind, 'skills': ROUTES[kind][0], 'packet': f'tasks/{uid}.json', 'status': 'prepared_not_executed'})
    report = {'schema_version': 'hmigbot-handoff/1', 'source_sha256': current['sha256'],
        'contract_sha256': digest(json_bytes(contract)), 'binding_sha256': digest(json_bytes(binding)),
        'upstream_root': binding['root'], 'source_root': str(source), 'target_root': str(target),
        'units': packets, 'execution_order': ordered,
        'shared_file_writers': {p: writers for p, writers in owners.items() if len(writers) > 1},
        'unselected_units': [i for i in ids if i not in selected], 'unresolved': contract.get('unresolved', []),
        'status': 'prepared_not_executed', 'migration_complete': False}
    outputs['contract.json'] = json_bytes(contract)
    outputs['binding.json'] = json_bytes(binding)
    report['artifacts'] = {p: digest(data) for p, data in outputs.items()}
    outputs['handoff.json'] = json_bytes(report)
    write_new_tree(output, outputs)
    return report


def check_handoff(source: Path, directory: Path):
    report = read_json(directory / 'handoff.json')
    if not isinstance(report, dict) or report.get('schema_version') != 'hmigbot-handoff/1':
        raise MigrationError('Unsupported handoff schema')
    if str(source.resolve()) != report.get('source_root') or source_snapshot(source.resolve())['sha256'] != report.get('source_sha256'):
        raise MigrationError('Handoff source changed; regenerate from current source semantics')
    artifacts = report.get('artifacts')
    if not isinstance(artifacts, dict) or not {'contract.json', 'binding.json'} <= set(artifacts):
        raise MigrationError('Missing handoff artifacts')
    for path, checksum in artifacts.items():
        item = safe_child(directory, path)
        if not item.is_file() or digest(item.read_bytes()) != checksum:
            raise MigrationError('Handoff artifact changed: ' + path)
    units = report.get('units')
    if not isinstance(units, list) or not units:
        raise MigrationError('Missing handoff units')
    for unit in units:
        if not isinstance(unit, dict) or not isinstance(unit.get('packet'), str) or unit['packet'] not in artifacts:
            raise MigrationError('Missing handoff task packet')
        packet = read_json(safe_child(directory, unit['packet']))
        if (packet.get('source_sha256') != report['source_sha256'] or packet.get('target_root') != report.get('target_root')
                or packet.get('unit', {}).get('id') != unit.get('id')):
            raise MigrationError('Handoff task metadata does not match the report')
    check_binding(directory / 'binding.json')
    return {'status': 'handoff_inputs_valid', 'execution': 'not_verified', 'units': len(report['units'])}
