"""Read-only official ETS facts supplementing the original target route engine.

Only statically evidenced tab, overlay and optional-push spellings are added
inside the original engine's default source scope. These are never a device/reachability
verdict.  The caller retains the original compiled-engine artifact separately.
"""
from __future__ import annotations

import copy
from collections import Counter
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import uuid

from hmigbot_ios.core import MigrationError
from .target_route_oracle import engine_files, engine_scripts, optional_delta


class TargetRouteError(MigrationError):
    """Incomplete/stale target analysis; never an empty successful supplement."""


EXCLUDED = {'.git', '.agents', '.codex', '.claude', '.hmigbot-ios', '.migbot',
            'node_modules', 'oh_modules', 'build', '.hvigor', '.preview', '.cxx',
            '__pycache__', 'spec', 'plans', 'design', 'docs'}


def digest(value):
    return hashlib.sha256(value if isinstance(value, bytes) else value.encode('utf-8')).hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode('utf-8')


def _file(path):
    path = Path(path)
    return digest(path.read_bytes()) if path.is_file() else None


def target_inputs(root):
    """Inventory the same application tree, excluding generated/managed data.

    All ETS/TS and application JSON/JSON5 (including route maps) are bound. SPEC
    and migration runtime data are deliberately not target routing evidence.
    """
    root = Path(root).resolve()
    values = {}
    for parent, dirs, names in os.walk(root, followlinks=False):
        dirs[:] = sorted(d for d in dirs if d not in EXCLUDED)
        for name in sorted(names):
            path = Path(parent) / name
            if path.suffix not in {'.ets', '.ts', '.json', '.json5'} and path.relative_to(root).as_posix() != 'local.properties':
                continue
            resolved = path.resolve()
            if not resolved.is_relative_to(root):
                raise TargetRouteError('Target route input escapes project: ' + str(path))
            values[path.relative_to(root).as_posix()] = _file(path)
    return values


def sdk_runtime(project):
    """Resolve the project's selected official SDK without a sibling skill.

    Selection follows the existing SDK proof policy: explicit parser, or one
    project/environment SDK matching compileSdkVersion; no arbitrary fallback.
    """
    project = Path(project)
    parser_override = os.environ.get('HMIGBOT_ETS_PARSER')
    node_override = os.environ.get('HMIGBOT_NODE')
    apps = []
    for home in (Path('/Applications'), Path.home() / 'Applications'):
        if home.is_dir():
            apps.extend(sorted(home.glob('*DevEco*.app')))
    nodes = [Path(node_override)] if node_override else [app / 'Contents/tools/node/bin/node' for app in apps]
    node = next((p.resolve() for p in nodes if p.is_file() and os.access(p, os.X_OK)), None)
    if node is None:
        raise TargetRouteError('Selected official DevEco Node runtime is unavailable')
    sdk_roots = [Path(os.environ[k]) for k in ('DEVECO_SDK_HOME', 'OHOS_SDK_HOME', 'HOS_SDK_HOME') if os.environ.get(k)]
    properties = project / 'local.properties'
    if properties.is_file():
        for line in properties.read_text(encoding='utf-8').splitlines():
            match = re.match(r'\s*(?:sdk\.dir|hwsdk\.dir|ohos\.sdk\.dir)\s*=\s*(.*?)\s*$', line)
            if match:
                sdk_roots.append(Path(match[1].replace('\\:', ':').replace('\\ ', ' ')))
    if not parser_override and not sdk_roots:
        raise TargetRouteError('Project SDK is not configured; select the exact official ETS SDK parser')
    suffixes = ('openharmony/ets/build-tools/ets-loader/node_modules/typescript',
                'ets/build-tools/ets-loader/node_modules/typescript')
    parsers = [Path(parser_override)] if parser_override else []
    if not parser_override:
        for root in sdk_roots:
            for base in (root, root / 'default', *sorted(root.glob('*'))):
                parsers.extend(base / suffix for suffix in suffixes)
    candidates = []
    for parser in parsers:
        if not ((parser / 'package.json').is_file() or parser.is_file()):
            continue
        parser = parser.resolve()
        loader = next((p for p in (parser, *parser.parents) if p.name == 'ets-loader'), None)
        if loader is None:
            continue
        package = loader.parent.parent / 'oh-uni-package.json'
        if package.is_file() and not any(row[0] == parser for row in candidates):
            candidates.append((parser, package, json.loads(package.read_text(encoding='utf-8'))))
    profile = project / 'build-profile.json5'
    configured = []
    if profile.is_file() and candidates:
        loader = next(p for p in (candidates[0][0], *candidates[0][0].parents) if p.name == 'ets-loader')
        program = "const fs=require('fs'),j=require(process.argv[1]);const d=j.parse(fs.readFileSync(process.argv[2],'utf8'));const a=[];function w(o){if(!o||typeof o!=='object')return;for(const[k,v]of Object.entries(o)){if(k==='compileSdkVersion')a.push(String(v));else w(v)}}w(d);process.stdout.write(JSON.stringify(a));"
        parsed = subprocess.run([str(node), '-e', program, str(loader / 'node_modules/json5'), str(profile)], capture_output=True, text=True, timeout=30)
        if parsed.returncode:
            raise TargetRouteError('Cannot read selected project SDK configuration: ' + parsed.stderr[-1000:])
        configured = json.loads(parsed.stdout)
    def matches(metadata, version):
        api = re.search(r'\((\d+)\)\s*$', version)
        return (api[1] if api else version) in (str(metadata.get('apiVersion')), str(metadata.get('platformVersion')))
    if configured:
        candidates = [row for row in candidates if all(matches(row[2], version) for version in configured)]
    if len(candidates) != 1:
        raise TargetRouteError('Selected official ETS parser is missing or ambiguous')
    parser, package, metadata = candidates[0]
    return node, parser, {'package': str(package), 'packageSha256': _file(package), 'metadata': metadata,
                          'configuredCompileSdk': configured, 'configuredSdkRoots': list(map(str, sdk_roots)),
                          'explicitParser': bool(parser_override)}


def _tool_files():
    here = Path(__file__).resolve()
    return {str(path): _file(path) for path in (here, here.with_name('target_routes_sdk.cjs'),
            here.with_name('ets_components.cjs'), here.with_name('target_route_bindings.cjs'),
            here.with_name('route_engine.py'), here.with_name('route_target_entry.py'),
            here.with_name('target_route_oracle.py'))}


def source_scope(root, inputs):
    """Match the measured original engine's entry/src/main/ets host scope.

    Imports remain parser context. Aliased hosts retain the original engine's
    rows but do not acquire new, potentially misattributed supplement rows.
    """
    root = Path(root).resolve()
    scope = root / 'entry/src/main/ets'
    record = {'selected_ets_root': str(scope), 'selected_files': {}, 'scope_exclusions': [],
              'scope_policy': 'original-engine-measured:entry/src/main/ets/**',
              'scope_evidence': 'evaluations/test_target_scope_counterfacts.py',
              'scope_status': 'present' if scope.is_dir() else 'default_scope_absent'}
    parents = [root.joinpath(*scope.relative_to(root).parts[:i]) for i in range(1, 5)]
    if any(path.is_symlink() for path in parents):
        record['scope_exclusions'].append({'file': 'entry/src/main/ets',
            'reason': 'aliased default scope; original rows retained, no supplementary hosts',
            'resolved': str(scope.resolve())})
        return record
    if not scope.is_dir():
        return record
    paths = sorted(scope.rglob('*'))
    for path in paths:
        if path.is_symlink():
            record['scope_exclusions'].append({'file': path.relative_to(root).as_posix(),
                'reason': 'aliased host path not used to generate supplementary rows',
                'resolved': str(path.resolve())})
    resolved = set()
    for path in paths:
        if path.suffix != '.ets' or not path.is_file():
            continue
        real = path.resolve()
        if path.is_symlink() or not real.is_relative_to(scope) or real in resolved:
            continue
        resolved.add(real)
        record['selected_files'][path.relative_to(root).as_posix()] = _file(path)
    return record


def _snapshot(root, node, parser, selection):
    entry = parser / 'lib/typescript.js' if parser.is_dir() else parser
    loader = next(p for p in (parser, *parser.parents) if p.name == 'ets-loader')
    inputs = target_inputs(root)
    return {'target_files': inputs, 'source_scope': source_scope(root, inputs), 'tool_files': _tool_files(),
            'runtime_files': {str(p): _file(p) for p in (node, entry, loader / 'tsconfig.json', Path(selection['package']))},
            'sdk_selection': selection, 'node': str(node), 'parser_module': str(parser)}


def validate_target_snapshot(root, receipt, actual=None):
    """Raise on changed/new/deleted target input, runtime, helper or output.

    The wrapper calls this before every downstream consumer. It is intentionally
    independent of file mtimes and binds all actual SDK context inputs as well.
    """
    if receipt.get('status') != 'complete' or receipt.get('schema') != 1:
        raise TargetRouteError('Target route supplement receipt is missing/incomplete')
    node, parser, selection = sdk_runtime(Path(root))
    current = _snapshot(Path(root), node, parser, selection)
    old = receipt.get('snapshot', {})
    for key in current:
        if current[key] != old.get(key):
            raise TargetRouteError('Target route supplement is stale (' + key + '); rerun hmos_extract')
    for name, value in {**old.get('context_files', {}), **old.get('engine_files', {})}.items():
        if _file(name) != value:
            raise TargetRouteError('Target route SDK/context input changed: ' + name + '; rerun hmos_extract')
    if receipt.get('snapshot_sha256') != digest(canonical(old)):
        raise TargetRouteError('Target route supplement receipt identity is invalid')
    if actual is not None and receipt.get('derived_sha256') != digest(canonical(actual)):
        raise TargetRouteError('Target route artifact changed after supplementation; rerun hmos_extract')
    return True


def validate_receipt(root, receipt):
    """Public downstream freshness check (the wrapper binds output file SHA)."""
    return validate_target_snapshot(root, receipt)


def _add_tab_stats(actual, added):
    stats = actual.setdefault('stats', {})
    for key in ('total_edges', 'page_nav', 'tab_edges', 'via_indirect_method'):
        stats[key] = stats.get(key, 0) + len(added)
    for key, value in (('by_via', 'tab'), ('by_target_type', 'page')):
        group = stats.setdefault(key, {})
        group[value] = group.get(value, 0) + len(added)
    stats['distinct_target_pages'] = sorted(set(stats.get('distinct_target_pages', [])) | {edge['target'] for edge in added})


def supplement_target(root, original, *, scripts=None, original_bytes=None, engine_argv=()):
    """Return (derived original-wire graph, evidence receipt), without writes."""
    root = Path(root).resolve()
    node, parser, selection = sdk_runtime(root)
    before = _snapshot(root, node, parser, selection)
    scope = before['source_scope']
    files = [str(root / name) for name in scope['selected_files']]
    run_id = uuid.uuid4().hex
    request = {'runId': run_id, 'project': str(root), 'files': files,
               'parserModule': str(parser), 'sdkSelection': selection}
    try:
        result = subprocess.run([str(node), str(Path(__file__).with_name('target_routes_sdk.cjs'))],
                                input=json.dumps(request, ensure_ascii=False), capture_output=True,
                                text=True, encoding='utf-8', timeout=120, cwd=root)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise TargetRouteError('Official target route proof failed to run: ' + str(exc)) from exc
    try:
        proof = json.loads(result.stdout)
    except ValueError as exc:
        raise TargetRouteError('Official target route proof did not return JSON: ' + result.stderr[-1000:]) from exc
    if result.returncode or proof.get('runId') != run_id or proof.get('valid') is not True:
        raise TargetRouteError('Official target route proof incomplete: ' + str(proof.get('error') or result.stderr[-1000:]))
    if _snapshot(root, node, parser, selection) != before:
        raise TargetRouteError('Target/runtime input changed while extracting; rerun hmos_extract')
    context = {row['file']: row['sha256'] for row in proof.get('contextFiles', [])}
    if any(_file(path) != value for path, value in context.items()):
        raise TargetRouteError('Official target parser context changed during extraction')
    before['context_files'] = context
    scripts = Path(scripts or engine_scripts(root))
    before['engine_files'] = engine_files(scripts)
    actual = copy.deepcopy(original)
    added, groups_added, conflicts = [], [], []
    original_groups = copy.deepcopy(actual.setdefault('tab_groups', []))
    groups = actual['tab_groups']
    remaining_groups = Counter(canonical(group) for group in original_groups)
    edges = actual.setdefault('edges', [])
    remaining_tab_edges = Counter((edge.get('source'), edge.get('source_file'), edge.get('target'))
                                  for edge in edges if edge.get('via') == 'tab')
    new_tab_sites = set()
    for record in proof.get('tabGroups', []):
        wire = record['wire']
        group_key = canonical(wire)
        if remaining_groups[group_key]:
            remaining_groups[group_key] -= 1
            continue
        same_host = [group for group in original_groups if group.get('host') == wire['host'] and group.get('file') == wire['file']]
        if same_host:
            conflicts.append({'reason': 'original_group_differs_same_host', 'candidate': record, 'original_groups': copy.deepcopy(same_host)})
            continue
        groups.append(copy.deepcopy(wire))
        groups_added.append(record)
        for member in record['members']:
            target = member['target']
            # Original tab wire has no source position (line=0). A pre-existing
            # same host/member tab is the same declaration relation, not a new
            # onclick. Keep its exact original row and preserve the AST span in
            # the supplement receipt even when no new row is needed.
            relation = wire['host'], wire['file'], target
            if remaining_tab_edges[relation]:
                remaining_tab_edges[relation] -= 1
                continue
            site = member['tab_content']
            source_site = (*relation, site['file'], site['start_utf16'], site['end_utf16'])
            if source_site in new_tab_sites:
                continue
            new_tab_sites.add(source_site)
            edge = {'source': wire['host'], 'source_file': wire['file'], 'control_type': 'TabBar',
                    'control_text': None, 'control_media': None, 'target': target, 'target_type': 'page',
                    'via': 'tab', 'chain': 'tabbar', 'guard': None, 'registered': True, 'bound': True, 'line': 0,
                    'supplement': 'ets_ast', 'native_provenance': member}
            edges.append(edge)
            added.append(edge)
    if added:
        _add_tab_stats(actual, added)
    overlays_added = []
    for record in proof.get('overlayBindings', []):
        matches = [i for i, edge in enumerate(edges) if edge.get('source') == record['source'] and
                   edge.get('source_file') == record['source_file'] and edge.get('line') == record['line'] and
                   edge.get('via') == record['api'] and edge.get('target_type') == 'dialog']
        if len(matches) != 1:
            conflicts.append({'reason': 'overlay_original_call_site_missing_or_ambiguous', 'candidate': record, 'matching_rows': len(matches)})
            continue
        index = matches[0]
        if edges[index].get('target') == record['target']:
            continue
        if edges[index].get('target') is not None:
            conflicts.append({'reason': 'overlay_original_target_conflicts', 'candidate': record, 'original_engine_row': copy.deepcopy(edges[index])})
            continue
        original_row = copy.deepcopy(edges[index])
        edges[index] = {**original_row, 'target': record['target'], 'supplement': 'ets_ast',
                        'original_engine_row': original_row, 'native_provenance': record}
        overlays_added.append(edges[index])
    actual, pushes_added, optional_measurement, optional_conflicts = optional_delta(
        root, original, actual, proof.get('optionalPushes', []), before['target_files'],
        scripts=scripts, original_bytes=original_bytes, engine_argv=engine_argv)
    conflicts.extend(optional_conflicts)
    fresh = _snapshot(root, node, parser, selection)
    if any(fresh[key] != before[key] for key in fresh) or any(
            _file(path) != value for path, value in {**context, **before['engine_files']}.items()):
        raise TargetRouteError('Target/runtime input changed during original measurement; rerun hmos_extract')
    receipt = {'schema': 1, 'status': 'complete', **scope,
               'scope': 'official ETS static declaration supplement; no device or entry reachability verdict',
               'snapshot': before, 'snapshot_sha256': digest(canonical(before)),
               'original_sha256': digest(canonical(original)), 'derived_sha256': digest(canonical(actual)),
               'facts': proof, 'added_groups': groups_added, 'added_edges': [*added, *overlays_added, *pushes_added],
               'added_tab_edges': added, 'resolved_overlay_rows': overlays_added, 'added_optional_pushes': pushes_added,
               'optional_measurement': optional_measurement, 'event_bindings': proof.get('eventBindings', []),
               'merge_unknowns': conflicts, 'unknowns': proof.get('unknowns', []), 'dead_builders': proof.get('deadBuilders', [])}
    return actual, receipt
