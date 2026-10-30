"""Offline UI evidence pairing, conservative reuse and measured run accounting.

Consumes app-scoped captures; never captures a screen or changes device settings.
The explicit configuration subcommand reads the selected Simulator via Apple CLI.
Image/structure observations are review aids, not proof of business equivalence.
The original capture artifacts remain authoritative and are never modified.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
from datetime import datetime
import hashlib
import math
from pathlib import Path, PurePosixPath
import re
import struct
import subprocess
import tempfile
import time

from .core import MigrationError, digest, json_bytes, read_json, write_json, snapshot, source_snapshot
from .cli_output import emit_json

SCHEMA = 'hmigbot-ui-evidence/1'
HASH = re.compile(r'[0-9a-f]{64}')
CONFIG_KEYS = ('language', 'locale', 'theme', 'content_size')
PAIR_REPORT = 'spec/reports/ios-ui-pair.json'
PREFLIGHT_REPORT = 'spec/reports/ios-ui-preflight.json'


def build_identity(path):
    """Shared capture/current identity for an actual .app directory or HAP file."""
    path = Path(path).resolve()
    _require(path.is_dir() or path.is_file(), 'Current build artifact is unavailable')
    return snapshot(path)['sha256'] if path.is_dir() else _file_sha(path)


def source_identity(platform, root):
    """Harmony evidence/progress cannot become its own product source input."""
    root = Path(root).resolve()
    _require(root.is_dir(), 'Current UI source root is unavailable')
    if platform == 'harmonyos':
        from .quality_views import target_inputs
        return digest(json_bytes(target_inputs(root)))
    _require(platform in {'ios', 'preview'}, 'Unknown UI source platform')
    return source_snapshot(root)['sha256']


def _require(test, message):
    if not test:
        raise MigrationError(message)


def _hash(value, name):
    _require(isinstance(value, str) and HASH.fullmatch(value), 'Invalid SHA256: ' + name)
    return value


def _relative(value):
    _require(isinstance(value, str) and value and '\\' not in value and ':' not in value,
             'UI artifact path must be a portable relative path')
    path = PurePosixPath(value)
    _require(not path.is_absolute() and '..' not in path.parts and path.as_posix() == value
             and value not in {'.', ''}, 'Unsafe UI artifact path: ' + value)
    return path


def _artifact(root, relative):
    relative = _relative(relative)
    current = root
    for part in relative.parts:
        current = current / part
        _require(not current.is_symlink(), 'UI artifact cannot follow a symlink: ' + str(relative))
    _require(current.resolve().is_relative_to(root) and current.is_file(),
             'UI artifact missing or outside bundle: ' + str(relative))
    return current


def _file_sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def identity(value):
    """The current identity must come from the caller's selected build/config."""
    _require(isinstance(value, dict), 'UI identity must be an object')
    for key in ('bundle_id', 'platform'):
        _require(isinstance(value.get(key), str) and value[key], 'Missing UI identity: ' + key)
    device, build, scenario, configuration = (value.get(k) for k in
                                               ('device', 'build', 'scenario', 'configuration'))
    _require(all(isinstance(v, dict) for v in (device, build, scenario, configuration)),
             'UI identity needs device, build, scenario and configuration objects')
    _require(all(isinstance(device.get(k), str) and device[k] for k in ('id', 'kind')),
             'UI identity needs an explicit device id and kind')
    _require(isinstance(scenario.get('id'), str) and scenario['id'], 'UI scenario id is missing')
    _require(all(isinstance(configuration.get(k), str) and configuration[k] for k in CONFIG_KEYS),
             'UI identity needs explicit language, locale, theme and content_size')
    return {'platform': value['platform'], 'bundle_id': value['bundle_id'],
            'device': {k: device[k] for k in ('id', 'kind')},
            'build': {'sha256': _hash(build.get('sha256'), 'build')},
            'source_sha256': _hash(value.get('source_sha256'), 'source'),
            'scenario': {'id': scenario['id'], 'sha256': _hash(scenario.get('sha256'), 'scenario')},
            'configuration': {k: configuration[k] for k in CONFIG_KEYS}}


def _load(path, expected=None):
    path = Path(path)
    _require(not path.is_symlink(), 'UI manifest cannot be a symlink')
    path = path / 'manifest.json' if path.is_dir() else path
    _require(path.is_file() and not path.is_symlink(), 'UI manifest is missing')
    root = path.parent.resolve()
    manifest = read_json(path)
    _require(isinstance(manifest, dict) and manifest.get('schema_version') == SCHEMA,
             'Unsupported UI evidence schema')
    _require(manifest.get('platform') in {'ios', 'harmonyos', 'preview'}, 'Unsupported UI evidence platform')
    _require(isinstance(manifest.get('run_id'), str) and manifest['run_id'], 'UI evidence run_id is missing')
    bound = identity(manifest)
    artifacts = manifest.get('artifacts')
    _require(isinstance(artifacts, dict) and artifacts, 'UI artifacts must be a nonempty hash map')
    for name, sha in artifacts.items():
        item = _artifact(root, name)
        _require(item.resolve() != path.resolve(), 'UI manifest cannot list itself as an artifact')
        _require(_file_sha(item) == _hash(sha, name), 'UI artifact hash changed: ' + name)
    checkpoints = manifest.get('checkpoints')
    _require(isinstance(checkpoints, list) and checkpoints, 'UI evidence needs explicit checkpoints')
    seen = set()
    for checkpoint in checkpoints:
        _require(isinstance(checkpoint, dict), 'UI checkpoint must be an object')
        key = checkpoint.get('id')
        _require(isinstance(key, str) and key and key not in seen, 'Missing or duplicate UI checkpoint id')
        seen.add(key)
        _require(checkpoint.get('status') in {'passed', 'failed', 'blocked', 'not_run'},
                 'Unknown checkpoint status: ' + key)
        for field in ('screenshot', 'hierarchy'):
            ref = checkpoint.get(field)
            if ref is None and checkpoint['status'] != 'passed':
                continue
            _require(isinstance(ref, dict) and ref.get('path') in artifacts,
                     key + ' needs a listed ' + field + ' artifact')
            _require(ref.get('sha256') == artifacts[ref['path']], key + ' capture reference hash differs')
    issues = []
    if expected is not None:
        wanted = identity(expected)
        for key in wanted:
            if bound[key] != wanted[key]:
                issues.append({'rule': 'current_identity_mismatch', 'field': key,
                               'expected': wanted[key], 'captured': bound[key]})
    return path.resolve(), manifest, bound, issues


def validate_bundle(path, expected=None):
    manifest_path, manifest, bound, issues = _load(path, expected)
    physical = verify_current(expected) if expected is not None else []
    issues += physical
    return {'status': 'needs_current_binding' if any(i['rule']=='current_binding_missing' for i in issues)
            else 'stale_evidence' if issues else 'current_bound' if expected is not None else 'integrity_valid',
            'manifest': str(manifest_path), 'manifest_sha256': _file_sha(manifest_path),
            'identity': bound, 'artifacts_checked': len(manifest['artifacts']),
            'checkpoint_ids': [c['id'] for c in manifest['checkpoints']], 'issues': issues,
            'freshness': 'not_bound' if any(i['rule']=='current_binding_missing' for i in issues)
                         else 'mismatch' if issues else 'current_identity_bound' if expected is not None else 'not_bound',
            'execution_authenticity': 'artifact_integrity_does_not_authenticate_capture',
            'behavior_verified': False, 'preview_only': manifest['platform'] == 'preview'}


def verify_current(value):
    """Verify physical selected build/source and an actual configuration receipt.

    The independent observation receipt is supplied by the platform adapter. Its
    hashes establish integrity/binding, not cryptographic capture authenticity.
    """
    bound = identity(value)
    verification = value.get('verification')
    if not isinstance(verification, dict) or not all(k in verification for k in
            ('build_path', 'source_root')):
        return [{'rule':'current_binding_missing','platform':bound['platform'],
                 'required':['verification.build_path','verification.source_root','verification.configuration_receipt']}]
    issues = []
    if build_identity(verification['build_path']) != bound['build']['sha256']:
        issues.append({'rule':'current_build_bytes_changed','platform':bound['platform']})
    if source_identity(bound['platform'], verification['source_root']) != bound['source_sha256']:
        issues.append({'rule':'current_product_source_changed','platform':bound['platform']})
    reference = verification.get('configuration_receipt')
    if reference is None:
        return issues+[{'rule':'current_configuration_observation_missing','platform':bound['platform']}]
    _require(isinstance(reference,dict) and isinstance(reference.get('path'),str),
             'Current configuration observation receipt is missing')
    path = Path(reference['path']).resolve()
    _require(path.is_file() and _file_sha(path)==_hash(reference.get('sha256'),'current configuration receipt'),
             'Current configuration observation receipt changed')
    receipt = read_json(path)
    _require(isinstance(receipt,dict) and receipt.get('schema_version')=='hmigbot-ui-current/1',
             'Unsupported current UI configuration observation schema')
    calls = receipt.get('calls',[])
    if (receipt.get('observations_actual') is not True or not isinstance(calls,list)
            or not any(isinstance(c,dict) and c.get('actual_call_now') is True
                       and type(c.get('exit_code')) is int and c.get('exit_code')==0 and not c.get('timed_out')
                       and c.get('kind') in {'app_ui_test','configuration_observation'} for c in calls)):
        issues.append({'rule':'current_configuration_not_actually_observed','platform':bound['platform']})
    expected = {'platform':bound['platform'],'bundle_id':bound['bundle_id'],
                'device':bound['device'],'build_sha256':bound['build']['sha256'],
                'observed_configuration':bound['configuration']}
    for key,wanted in expected.items():
        if receipt.get(key)!=wanted:
            issues.append({'rule':'current_configuration_observation_mismatch','field':key,'platform':bound['platform']})
    return issues


def _png_dimensions(path):
    with path.open('rb') as stream:
        header = stream.read(24)
    _require(len(header) == 24 and header[:8] == b'\x89PNG\r\n\x1a\n' and header[12:16] == b'IHDR',
             'Current image metrics support captured PNG images only')
    width, height = struct.unpack('>II', header[16:24])
    _require(width > 0 and height > 0, 'Invalid PNG dimensions')
    return width, height


def _bmp_pixels(raw):
    _require(raw[:2] == b'BM' and len(raw) >= 54, 'Apple image conversion did not produce a BMP')
    offset = struct.unpack_from('<I', raw, 10)[0]
    width, height = struct.unpack_from('<ii', raw, 18)
    bpp = struct.unpack_from('<H', raw, 28)[0]
    compression = struct.unpack_from('<I', raw, 30)[0]
    _require(width == 8 and abs(height) == 8 and bpp in (24, 32) and compression in (0, 3),
             'Unsupported Apple BMP metric format')
    stride = ((width * bpp + 31) // 32) * 4
    _require(offset + stride * abs(height) <= len(raw), 'Truncated Apple BMP metric')
    pixels = []
    for y in range(8):
        row = y if height < 0 else 7 - y
        for x in range(8):
            pos = offset + row * stride + x * (bpp // 8)
            b, g, r = raw[pos:pos + 3]
            pixels.append((r, g, b))
    return pixels


def image_metrics(path):
    """Read an existing capture with Apple's sips; never acquire a new image."""
    path = Path(path).resolve()
    width, height = _png_dimensions(path)
    binary = Path('/usr/bin/sips')
    if not binary.is_file():
        return {'status': 'unavailable', 'reason': 'Apple sips is unavailable', 'width': width, 'height': height}
    started = time.monotonic()
    with tempfile.TemporaryDirectory(prefix='hmigbot-image-metric-') as temporary:
        output = Path(temporary) / 'sample.bmp'
        command = [str(binary), '-z', '8', '8', '-s', 'format', 'bmp', str(path), '--out', str(output)]
        try:
            run = subprocess.run(command, capture_output=True, timeout=20, shell=False)
        except (OSError, subprocess.TimeoutExpired) as exc:
            return {'status': 'unavailable', 'reason': str(exc), 'width': width, 'height': height}
        call = {'provider': 'Apple sips', 'actual_call_now': True, 'exit_code': run.returncode,
                'elapsed_seconds': time.monotonic() - started}
        if run.returncode != 0 or not output.is_file():
            return {'status': 'unavailable', 'reason': run.stderr.decode('utf-8', errors='replace')[:1000],
                    'width': width, 'height': height, 'call': call}
        pixels = _bmp_pixels(output.read_bytes())
    levels = [(299 * r + 587 * g + 114 * b) / 1000 for r, g, b in pixels]
    mean = sum(levels) / len(levels)
    bits = ''.join('1' if level >= mean else '0' for level in levels)
    return {'status': 'measured', 'width': width, 'height': height,
            'average_hash': format(int(bits, 2), '016x'), 'sample_rgb': pixels,
            'measurement': '8x8 resampled observation; not a full-resolution pixel comparison', 'call': call}


def _nodes(document):
    result = defaultdict(list)
    def visit(item):
        if isinstance(item, list):
            for child in item:
                visit(child)
        elif isinstance(item, dict):
            key = item.get('identifier', item.get('accessibilityIdentifier', item.get('id')))
            if isinstance(key, str) and key:
                result[key].append(item)
            for key in ('nodes', 'elements', 'children'):
                if key in item:
                    visit(item[key])
    visit(document)
    return result


def _structure(source, target, rules):
    left, right = _nodes(source), _nodes(target)
    mapping = rules.get('control_map', {})
    fields = rules.get('compare_fields', ['label', 'value', 'enabled'])
    _require(isinstance(mapping, dict) and all(isinstance(k, str) and isinstance(v, str) for k, v in mapping.items()),
             'control_map must map stable source ids to target ids')
    _require(len(set(mapping.values())) == len(mapping), 'control_map target ids must be unique')
    _require(isinstance(fields, list) and fields and len(set(fields)) == len(fields)
             and set(fields) <= {'label', 'value', 'enabled', 'selected'},
             'Only explicitly comparable control observations may be selected')
    differences, unknown = [], []
    for key, candidates in sorted(left.items()):
        target_id = mapping.get(key, key)
        matches = right.get(target_id, [])
        if len(candidates) != 1 or len(matches) != 1:
            unknown.append({'control': key, 'target_control': target_id,
                            'reason': 'missing_or_ambiguous_stable_identifier',
                            'source_matches': len(candidates), 'target_matches': len(matches)})
            continue
        for field in fields:
            if field not in candidates[0] or field not in matches[0] or candidates[0][field] is None or matches[0][field] is None:
                unknown.append({'control': key, 'field': field, 'reason': 'observation_not_exposed_on_both_sides'})
            elif candidates[0][field] != matches[0][field]:
                differences.append({'control': key, 'field': field, 'source': candidates[0][field],
                                    'target': matches[0][field]})
    if not left:
        unknown.append({'reason': 'no_stable_source_control_ids; raw UI tree is retained for review'})
    mapped = {mapping.get(key, key) for key in left}
    for key in sorted(set(right) - mapped):
        unknown.append({'target_control': key, 'reason': 'additional_unmapped_target_control'})
    return {'status': 'differences_observed' if differences else 'review_required' if unknown else 'equal_observations',
            'differences': differences, 'unknown': unknown, 'source_stable_ids': len(left),
            'target_stable_ids': len(right),
            'scope': 'Exposed accessible controls only; no full SwiftUI/UIKit internal tree claim'}


def _receipt_key(source, target, rules, selected, current, observations_only, business_scenario):
    return digest(json_bytes({'source_identity': identity(source), 'target_identity': identity(target),
                             'source_artifacts': source['artifacts'], 'target_artifacts': target['artifacts'],
                             'source_checkpoints': source['checkpoints'], 'target_checkpoints': target['checkpoints'],
                             'rules': rules, 'selected': selected,
                             'observations_only':observations_only,
                             'business_scenario':business_scenario,
                             'current_observation_sha256':{platform:(current[platform].get('verification',{}).get('configuration_receipt') or {}).get('sha256')
                                                            for platform in ('ios','harmonyos')},
                             'implementation_sha256': _file_sha(Path(__file__))}))


def _valid_previous(previous, key, selected):
    if (not isinstance(previous, dict) or previous.get('schema_version') != 1
            or previous.get('reuse_key') != key or previous.get('status') not in {'compared','compared_with_configuration_gap'}
            or previous.get('behavior_verified') is not False):
        return False
    pairs = previous.get('pairs')
    if not isinstance(pairs,list) or len(pairs)!=len(selected):
        return False
    if any(not isinstance(p,dict) or not isinstance(p.get('id'),str) or p.get('status')!='compared' or p.get('behavior_verified') is not False
           or not isinstance(p.get('image'),dict) or p['image'].get('status')!='measured'
           or not isinstance(p.get('assessment'),dict) or not isinstance(p.get('cross_platform'),dict)
           or not isinstance(p.get('structure'),dict) or p['structure'].get('status') not in
               {'differences_observed','review_required','equal_observations'} for p in pairs):
        return False
    if sorted(p.get('id','') for p in pairs)!=selected:
        return False
    value = {k: v for k, v in previous.items() if k != 'receipt_sha256'}
    return previous.get('receipt_sha256') == digest(json_bytes(value))


def _cross_exceptions(value, source_file, source, target_file, target, current):
    """Verify explicit reviewed per-difference exceptions, not inferred waivers."""
    if value is None:
        return {}
    _require(isinstance(value,dict) and value.get('schema_version') == 'hmigbot-ui-exceptions/1',
             'Unsupported UI exception rules')
    _require(value.get('source_manifest_sha256') == _file_sha(source_file)
             and value.get('target_manifest_sha256') == _file_sha(target_file),
             'UI exceptions belong to different capture manifests')
    decisions=value.get('decisions')
    _require(isinstance(decisions,list),'UI exceptions need explicit decisions')
    grouped,seen={},set()
    for item in decisions:
        _require(isinstance(item,dict) and item.get('reviewed') is True,
                 'UI exception requires a caller-reviewed decision')
        checkpoint=item.get('checkpoint_id')
        _require(isinstance(checkpoint,str) and checkpoint in {c['id'] for c in source['checkpoints']}
                 and checkpoint in {c['id'] for c in target['checkpoints']}, 'Unknown UI exception checkpoint')
        pair=(checkpoint,item.get('difference_id'))
        _require(pair not in seen,'Duplicate UI exception for one difference')
        seen.add(pair)
        evidence=item.get('evidence')
        _require(isinstance(evidence,dict) and evidence.get('platform') in {'ios','harmonyos'},
                 'Exception needs selected source/capture evidence')
        platform=evidence['platform']
        if evidence.get('kind')=='source':
            root=Path(current[platform]['verification']['source_root']).resolve()
            path=_artifact(root,evidence.get('path'))
            _require(_file_sha(path)==_hash(evidence.get('sha256'),'exception source'), 'Exception source changed')
            lines=path.read_text().splitlines(); line=evidence.get('line')
            _require(type(line)is int and 1<=line<=len(lines) and evidence.get('quote')==lines[line-1],
                     'Exception source line/quote changed')
        else:
            _require(evidence.get('kind')=='capture' and item.get('category')=='design_difference',
                     'Dynamic/config exclusions need source evidence; design decisions may reference captures')
            manifest,root=(source,source_file.parent) if platform=='ios' else (target,target_file.parent)
            path=_artifact(root,evidence.get('path'))
            _require(manifest['artifacts'].get(evidence['path'])==evidence.get('sha256')==_file_sha(path),
                     'Exception capture is not a bound artifact')
        decision={k:item.get(k) for k in ('difference_id','observation_sha256','category','reason')}
        decision['evidence']={**evidence,'validated_for_current_comparison':True,
                              'authority':'caller_reviewed_decision; hashes_establish_binding_not_human_authentication'}
        grouped.setdefault(checkpoint,[]).append(decision)
    return grouped


def _visual_observations(value, source_file, source, target_file, target):
    if value is None:
        return {}
    _require(isinstance(value,dict) and value.get('schema_version')=='hmigbot-ui-visual-review/1'
             and value.get('source_manifest_sha256')==_file_sha(source_file)
             and value.get('target_manifest_sha256')==_file_sha(target_file),
             'Visual review must bind the exact source/target capture manifests')
    _require(value.get('reviewer_kind') in {'human','agent'} and isinstance(value.get('observations'),list),
             'Visual review needs an attributed reviewer and observations')
    grouped={}
    for item in value['observations']:
        _require(isinstance(item,dict),'Malformed visual observation')
        key=item.get('checkpoint_id')
        for platform,manifest in [('ios',source),('harmonyos',target)]:
            found=[c for c in manifest['checkpoints'] if c['id']==key and c['status']=='passed']
            _require(len(found)==1 and item.get(platform+'_screenshot_sha256')==found[0]['screenshot']['sha256'],
                     'Visual review belongs to another screenshot/checkpoint')
        grouped.setdefault(key,[]).append({**item,'reviewer_kind':value['reviewer_kind'],
            'provenance':'external visual observation; not an offline pixel detector or native runtime conclusion'})
    return grouped


def pair_evidence(source_path, target_path, *, current=None, phase='initial', checkpoints=None,
                  rules=None, previous=None, observations_only=False, business_recipe=None, control_mapping=None,
                  exceptions=None, visual_observations=None):
    """Pair iOS/Harmony captures against explicit current app/build identities."""
    _require(phase in {'initial', 'intermediate', 'final'}, 'Unknown UI comparison phase')
    _require(type(observations_only)is bool,'observations_only must be explicitly boolean')
    report = {'schema_version': 1, 'status': 'incomplete', 'phase': phase, 'pairs': [],
              'behavior_verified': False, 'application_acceptance': 'not_established',
              'actual_capture_invoked': False, 'issues': [],'configuration_gaps':[],
              'mode':'observations_only' if observations_only else 'strict_binding'}
    if source_path is None or target_path is None:
        report['issues'].append({'rule': 'both_platform_evidence_required'})
        return report
    if not isinstance(current, dict) or not {'ios', 'harmonyos'} <= current.keys():
        report.update(status='needs_current_binding')
        report['issues'].append({'rule': 'explicit_current_ios_and_harmonyos_identities_required'})
        return report
    source_file, source, source_identity, source_issues = _load(source_path, current['ios'])
    target_file, target, target_identity, target_issues = _load(target_path, current['harmonyos'])
    _require(source['platform'] == 'ios' and target['platform'] == 'harmonyos',
             'App pairing requires iOS and HarmonyOS; Preview cannot stand in for app execution')
    report['issues'] += source_issues + target_issues + verify_current(current['ios']) + verify_current(current['harmonyos'])
    if observations_only:
        for issue in list(report['issues']):
            configuration_gap=(issue['rule'] in {'current_configuration_not_actually_observed','current_configuration_observation_missing'}
                or issue['rule']=='current_configuration_observation_mismatch' and issue.get('field')=='observed_configuration'
                or issue['rule']=='current_identity_mismatch' and issue.get('field')=='configuration')
            if configuration_gap:
                report['configuration_gaps'].append(issue)
                report['issues'].remove(issue)
    if report['issues']:
        report['status'] = ('needs_current_binding' if any(i['rule']=='current_binding_missing' for i in report['issues'])
                            else 'stale_evidence')
        return report
    if business_recipe is None:
        _require(source['scenario'] == target['scenario'], 'Source/target scenario identity differs')
        business_scenario=source['scenario']
    else:
        _require(isinstance(business_recipe,dict) and isinstance(business_recipe.get('id'),str)
                 and business_recipe['id'],'Explicit shared business recipe needs an id')
        recipe_checkpoints=business_recipe.get('checkpoints')
        _require(isinstance(recipe_checkpoints,list) and recipe_checkpoints
                 and all(isinstance(v,str) and v for v in recipe_checkpoints)
                 and len(set(recipe_checkpoints))==len(recipe_checkpoints),'Invalid shared business recipe checkpoints')
        business_scenario={'id':business_recipe['id'],'sha256':digest(json_bytes(business_recipe))}
        _require(source['scenario']['sha256']==target['scenario']['sha256']==business_scenario['sha256'],
                 'Source/target scenario identity differs from explicit shared business recipe')
        _require(all(set(recipe_checkpoints)=={c['id'] for c in value['checkpoints']} for value in (source,target)),
                 'Shared business recipe checkpoint scope differs from captured evidence')
    report.update(business_scenario=business_scenario,
                  platform_scenarios={'ios':source['scenario'],'harmonyos':target['scenario']})
    if source_identity['configuration'] != target_identity['configuration']:
        _require(observations_only,'Source/target UI configuration differs')
        report['configuration_gaps'].append({'rule':'source_target_configuration_mismatch',
            'source':source_identity['configuration'],'target':target_identity['configuration']})
    left = {c['id']: c for c in source['checkpoints']}
    right = {c['id']: c for c in target['checkpoints']}
    all_ids = sorted(set(left) | set(right))
    if checkpoints is not None:
        _require(phase == 'intermediate', 'Initial and final UI comparisons must use the full checkpoint scope')
        _require(isinstance(checkpoints, list) and checkpoints and len(set(checkpoints)) == len(checkpoints)
                 and set(checkpoints) <= set(all_ids), 'Invalid selected UI checkpoint scope')
    selected = all_ids if checkpoints is None else sorted(checkpoints)
    rules = {} if rules is None else rules
    _require(isinstance(rules, dict) and not (set(rules) - {'control_map', 'compare_fields'}),
             'Unsupported UI comparison rule fields')
    from .ui_configuration import compare_contexts
    from .ui_cross_platform import match_controls, assess_controls, validate_mapping
    if control_mapping is not None:
        validate_mapping(control_mapping,current)
    reviewed_exceptions = _cross_exceptions(exceptions,source_file,source,target_file,target,current)
    reviewed_visual = _visual_observations(visual_observations,source_file,source,target_file,target)
    configuration = compare_contexts(*[read_json(Path(current[p]['verification']['configuration_receipt']['path']))
                         if current[p]['verification'].get('configuration_receipt') else {}
                         for p in ('ios','harmonyos')])
    report['configuration_context'] = configuration
    # Bind all cross-platform policy/code inputs to the existing reuse receipt.
    report['control_mapping_sha256'] = digest(json_bytes(control_mapping)) if control_mapping is not None else None
    cross_inputs = {name:_file_sha(Path(__file__).with_name(name))
                    for name in ('ui_cross_platform.py','ui_configuration.py')}
    key = _receipt_key(source, target, rules, selected,current,observations_only,business_scenario)
    key = digest(json_bytes({'base':key,'control_mapping':control_mapping,'exceptions':exceptions,
                            'visual_observations':visual_observations,'cross_implementation':cross_inputs}))
    report.update(status='compared', reuse_key=key, source_manifest_sha256=_file_sha(source_file),
                  target_manifest_sha256=_file_sha(target_file), selected_checkpoint_ids=selected,
                  not_evaluated_checkpoint_ids=sorted(set(all_ids) - set(selected)), full_scope=selected == all_ids,
                  rules_sha256=digest(json_bytes(rules)), execution_authenticity='not_authenticated_by_hashes')
    if phase == 'intermediate' and _valid_previous(previous, key, selected):
        import copy
        report['pairs'] = copy.deepcopy(previous['pairs'])
        for pair in report['pairs']:
            for call in pair['image'].get('actual_measurement_calls',[]):
                call.update(actual_call_now=False,reused_from_receipt=previous['receipt_sha256'])
        report['measurement_reuse'] = {'reused': True, 'actual_measurement_now': False,
                                     'original_receipt_sha256': previous['receipt_sha256']}
    else:
        report['measurement_reuse'] = {'reused': False, 'actual_measurement_now': True,
                                     'reason': 'first_or_final_full_check' if phase != 'intermediate' else 'no_exact_current_receipt'}
        measured = {}
        for key_id in selected:
            a, b = left.get(key_id), right.get(key_id)
            pair = {'id': key_id, 'status': 'incomplete', 'behavior_verified': False}
            if a is None or b is None:
                pair['reason'] = 'checkpoint_missing_on_one_platform'
            elif a['status'] != 'passed' or b['status'] != 'passed':
                pair.update(reason='capture_or_scenario_assertion_not_passed',
                            source_status=a['status'], target_status=b['status'])
            else:
                pair['status'] = 'compared'
                source_image, target_image = (_artifact(source_file.parent, a['screenshot']['path']),
                                               _artifact(target_file.parent, b['screenshot']['path']))
                for ref, path in ((a['screenshot'], source_image), (b['screenshot'], target_image)):
                    if ref['sha256'] not in measured:
                        measured[ref['sha256']] = image_metrics(path)
                am, bm = measured[a['screenshot']['sha256']], measured[b['screenshot']['sha256']]
                image = {'status': 'unavailable', 'source_dimensions': [am['width'], am['height']],
                         'target_dimensions': [bm['width'], bm['height']],
                         'capture_bytes_equal': a['screenshot']['sha256'] == b['screenshot']['sha256']}
                if am['status'] == bm['status'] == 'measured':
                    image.update(status='measured',
                        average_hash_distance=(int(am['average_hash'], 16) ^ int(bm['average_hash'], 16)).bit_count(),
                        low_resolution_rgb_mae=sum(abs(x-y) for ap,bp in zip(am['sample_rgb'],bm['sample_rgb'])
                                                   for x,y in zip(ap,bp))/(64*3*255),
                        scope='8x8 screening metrics; not full-resolution visual acceptance',
                        actual_measurement_calls=[am['call']] + ([] if am is bm else [bm['call']]))
                else:
                    image['reasons'] = [m.get('reason') for m in (am, bm) if m['status'] != 'measured']
                pair['image'] = image
                pair['structure'] = _structure(read_json(_artifact(source_file.parent, a['hierarchy']['path'])),
                                               read_json(_artifact(target_file.parent, b['hierarchy']['path'])), rules)
                cross = match_controls(read_json(_artifact(source_file.parent,a['hierarchy']['path'])),
                                       read_json(_artifact(target_file.parent,b['hierarchy']['path'])),
                                       control_mapping,key_id,control_map=rules.get('control_map'))
                pair['cross_platform'] = cross
                pair['assessment'] = assess_controls(cross,configuration,rules.get('compare_fields'),reviewed_exceptions.get(key_id))
                from .ui_cross_platform import include_visual_observations
                include_visual_observations(pair['assessment'],reviewed_visual.get(key_id,[]))
                pair['review_required'] = (not image['capture_bytes_equal'] or image['status'] != 'measured'
                                           or pair['structure']['status'] != 'equal_observations'
                                           or not pair['assessment']['aligned_observations'])
            report['pairs'].append(pair)
        if any(p['status'] != 'compared' for p in report['pairs']):
            report['status'] = 'incomplete'
    if report['status']=='compared' and report['configuration_gaps']:
        report['status']='compared_with_configuration_gap'
    report['current_binding_verified']=not report['issues'] and not report['configuration_gaps']
    report['ui_assessment'] = {
        'status':'differences_observed' if any(p.get('assessment',{}).get('differences') for p in report['pairs'])
                 else 'incomplete' if any(not p.get('assessment',{}).get('evidence_complete') for p in report['pairs'])
                 else 'equal_control_observations',
        'automatic_page_closure':False,'application_acceptance':'not_established',
        'reason':'See per-checkpoint matching, configuration, classified differences and closure_blockers; control observations do not prove full visual/business acceptance'}
    report['receipt_sha256'] = digest(json_bytes(report))
    return report


def impact_plan(checkpoints, changed_files, ownership=None, *, phase='intermediate'):
    """Select a reviewed scope; missing ownership widens recheck instead of blocking."""
    _require(phase in {'initial', 'intermediate', 'final'}, 'Unknown UI recheck phase')
    _require(isinstance(checkpoints, list) and checkpoints and len(set(checkpoints)) == len(checkpoints)
             and all(isinstance(c, str) and c for c in checkpoints), 'Expected unique checkpoint ids')
    _require(isinstance(changed_files, list), 'Expected a changed-file list')
    changed = {_relative(p).as_posix() for p in changed_files}
    ownership = ownership if isinstance(ownership, dict) else {}
    records = ownership.get('checkpoints', {})
    components = ownership.get('components', {})
    _require(isinstance(records, dict) and isinstance(components, dict), 'Invalid UI ownership map')
    files, covered = {}, set()
    for key in checkpoints:
        record = records.get(key, {})
        _require(isinstance(record, dict), 'Checkpoint ownership must be an object')
        declared = record.get('files', [])
        _require(isinstance(declared, list), 'Checkpoint files must be a list')
        files[key] = {_relative(p).as_posix() for p in declared}
        covered.update(files[key])
    for record in components.values():
        _require(isinstance(record, dict) and isinstance(record.get('files', []), list)
                 and isinstance(record.get('checkpoints', []), list), 'Invalid shared component ownership')
        component_files = {_relative(p).as_posix() for p in record.get('files', [])}
        component_checkpoints = set(record.get('checkpoints', []))
        _require(component_checkpoints <= set(checkpoints), 'Shared component refers to an unknown checkpoint')
        covered.update(component_files)
        for checkpoint in component_checkpoints:
            files[checkpoint].update(component_files)
    unknown = changed - covered
    missing_ownership = sorted(key for key in checkpoints if not files[key])
    full = phase in {'initial', 'final'} or not ownership or bool(unknown) or bool(missing_ownership)
    selected = sorted(checkpoints if full else [key for key in checkpoints if files[key] & changed])
    groups = []
    for key in selected:
        matching = [g for g in groups if g['write_set'] & files[key]]
        group = {'checkpoints': {key}, 'write_set': set(files[key])}
        for prior in matching:
            group['checkpoints'].update(prior['checkpoints'])
            group['write_set'].update(prior['write_set'])
            groups.remove(prior)
        groups.append(group)
    unlocated = sorted(c for g in groups if not g['write_set'] for c in g['checkpoints'])
    located = [{'checkpoints': sorted(g['checkpoints']), 'write_set': sorted(g['write_set'])}
               for g in groups if g['write_set']]
    return {'status': 'planned', 'phase': phase, 'full_scope': full,
            'selected_checkpoint_ids': selected, 'not_selected_checkpoint_ids': sorted(set(checkpoints)-set(selected)),
            'unmapped_changed_files': sorted(unknown), 'disjoint_fix_groups': located,
            'checkpoints_without_file_ownership':missing_ownership,
            'unlocated_checkpoints_serial_last': unlocated,
            'reason': 'first_or_final_full_scope' if phase != 'intermediate' else
                      'ownership_unavailable_full_scope' if not ownership else
                      'partial_ownership_full_scope' if missing_ownership else
                      'unmapped_change_full_scope' if unknown else 'reviewed_impact_scope',
            'evidence_reuse': 'Requires exact current build, scenario, configuration, rules and artifact hashes separately'}


def measured_run(value):
    """Count supplied actual call receipts; no estimated speedup or fabricated work."""
    _require(isinstance(value, dict) and isinstance(value.get('scope'), dict), 'Benchmark needs an explicit scope')
    scope=value['scope']
    scope_identified=(isinstance(scope.get('application_id'),str) and bool(scope['application_id'])
        and isinstance(scope.get('checkpoint_ids'),list) and bool(scope['checkpoint_ids'])
        and all(isinstance(c,str) and c for c in scope['checkpoint_ids'])
        and len(set(scope['checkpoint_ids']))==len(scope['checkpoint_ids'])
        and isinstance(scope.get('source_build_sha256'),str) and bool(HASH.fullmatch(scope['source_build_sha256']))
        and isinstance(scope.get('configuration'),dict)
        and all(isinstance(scope['configuration'].get(k),str) and scope['configuration'][k] for k in CONFIG_KEYS))
    calls = value.get('calls')
    _require(isinstance(calls, list), 'Benchmark needs actual call receipts')
    start, end = (datetime.fromisoformat(value[key]) for key in ('started_at', 'finished_at'))
    _require(start.tzinfo is not None and end.tzinfo is not None and end >= start,
             'Benchmark timestamps must include timezone and monotonic order')
    actual, cached, durations = [], [], defaultdict(float)
    for call in calls:
        _require(isinstance(call, dict) and isinstance(call.get('actual_call_now'), bool), 'Call receipt lacks actual_call_now')
        if not call['actual_call_now']:
            cached.append(call)
            continue
        duration = call.get('elapsed_seconds')
        _require(isinstance(duration, (int,float)) and not isinstance(duration,bool)
                 and math.isfinite(duration) and duration >= 0, 'Invalid measured call duration')
        actual.append(call)
        durations[str(call.get('kind', 'unspecified'))] += duration
    manual = value.get('manual_seconds')
    _require(manual is None or isinstance(manual, (int,float)) and not isinstance(manual,bool)
             and math.isfinite(manual) and manual >= 0, 'Invalid manual duration')
    return {'status': 'measured', 'scope_sha256': digest(json_bytes(value['scope'])),
            'scope_identified':scope_identified,
            'scope_complete': value.get('scope_complete') is True,
            'quality_protocol_sha256': _hash(value.get('quality_protocol_sha256'), 'benchmark quality protocol'),
            'wall_seconds': (end-start).total_seconds(), 'actual_calls': len(actual),
            'reused_receipts': len(cached), 'summed_call_seconds_by_kind': dict(durations),
            'manual_seconds': manual, 'manual_measurement_source': value.get('manual_measurement_source') if manual is not None else None,
            'retry_calls': sum(c.get('attempt', 1) > 1 for c in actual),
            'note': 'Overlapping call durations are summed separately from elapsed wall time'}


def benchmark(current, baseline=None):
    result = {'status': 'current_measured', 'current': measured_run(current), 'comparison_available': False}
    if baseline is None:
        result['reason'] = 'No measured baseline supplied; no speedup claimed'
        return result
    prior = measured_run(baseline)
    result['baseline'] = prior
    now = result['current']
    comparable = (now['scope_sha256'] == prior['scope_sha256'] and now['scope_identified'] and prior['scope_identified']
                  and now['actual_calls']>0 and prior['actual_calls']>0 and now['scope_complete']
                  and prior['scope_complete'] and now['quality_protocol_sha256'] == prior['quality_protocol_sha256']
                  and prior['wall_seconds'] > 0)
    if comparable:
        result.update(status='measured_comparison', comparison_available=True,
                      wall_time_reduction_percent=100 * (prior['wall_seconds']-now['wall_seconds'])/prior['wall_seconds'])
    else:
        result['reason'] = 'Comparable full scope and quality protocol are not established'
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    validate = commands.add_parser('validate')
    validate.add_argument('--bundle', type=Path, required=True)
    validate.add_argument('--current', type=Path)
    pair = commands.add_parser('pair')
    pair.add_argument('--source', type=Path, required=True)
    pair.add_argument('--target', type=Path, required=True)
    pair.add_argument('--current', type=Path, required=True)
    pair.add_argument('--phase', choices=['initial','intermediate','final'], default='initial')
    pair.add_argument('--checkpoint', action='append')
    pair.add_argument('--rules', type=Path)
    pair.add_argument('--previous', type=Path)
    pair.add_argument('--business-recipe',type=Path,help='Explicit shared recipe JSON bound by both scenario hashes; preserves platform-local scenario labels')
    pair.add_argument('--control-mapping',type=Path,help='Optional source-anchored correspondence bound to current source/target bytes')
    pair.add_argument('--exceptions',type=Path,help='Explicit reviewed per-difference exceptions with current source/artifact evidence')
    pair.add_argument('--visual-observations',type=Path,help='Human/agent visual review bound to both original screenshot hashes; no invented pixel detection')
    pair.add_argument('--observations-only',action='store_true',help='Measure images/controls with explicit configuration gaps; never grants UI acceptance')
    impact = commands.add_parser('impact')
    impact.add_argument('--input', type=Path, required=True)
    measure = commands.add_parser('benchmark')
    measure.add_argument('--input', type=Path, required=True)
    measure.add_argument('--baseline', type=Path)
    mapping = commands.add_parser('bind-mapping',help='Bind caller-supplied control correspondence to source lines/hashes; no code mutation')
    mapping.add_argument('--input',type=Path,required=True)
    mapping.add_argument('--source-root',type=Path,required=True)
    mapping.add_argument('--target-root',type=Path,required=True)
    configuration = commands.add_parser('configuration',help='Read official settings of one explicit iOS simulator; supplementary device evidence')
    configuration.add_argument('--device-id',required=True)
    configuration.add_argument('--bundle-id',required=True)
    configuration.add_argument('--directory',type=Path,required=True)
    for command in (validate, pair, impact, measure, mapping, configuration):
        command.add_argument('--output', type=Path)
        command.add_argument('--project',type=Path,help='Explicit target for an optional in-project progress note; never inferred')
    args = parser.parse_args(argv)
    from .project_progress import ProjectProgress
    from argparse import Namespace
    progress=ProjectProgress(Namespace(command='ui-pair',project=args.project if args.command=='pair' and args.output else None))
    progress.record('running')
    try:
        if args.command == 'validate':
            result = validate_bundle(args.bundle, read_json(args.current) if args.current else None)
        elif args.command == 'pair':
            result = pair_evidence(args.source, args.target, current=read_json(args.current), phase=args.phase,
                checkpoints=args.checkpoint, rules=read_json(args.rules) if args.rules else None,
                previous=read_json(args.previous) if args.previous else None,observations_only=args.observations_only,
                business_recipe=read_json(args.business_recipe) if args.business_recipe else None,
                control_mapping=read_json(args.control_mapping) if args.control_mapping else None,
                exceptions=read_json(args.exceptions) if args.exceptions else None,
                visual_observations=read_json(args.visual_observations) if args.visual_observations else None)
        elif args.command == 'bind-mapping':
            from .ui_cross_platform import bind_mapping
            result = bind_mapping(read_json(args.input),args.source_root,args.target_root)
            result = {'status':'mapping_bound',**result}
            # The integrity digest covers the canonical mapping document only.
            result['mapping_sha256'] = digest(json_bytes({k:v for k,v in result.items() if k != 'mapping_sha256'}))
        elif args.command == 'configuration':
            from .ui_configuration import collect_simulator_context
            runtime = Path(__file__).resolve().parents[2]
            _require(not args.directory.resolve().is_relative_to(runtime),'Configuration output must be outside tool runtime')
            result = {'status':'observed_with_gaps',**collect_simulator_context(args.device_id,args.bundle_id,args.directory)}
        elif args.command == 'impact':
            value = read_json(args.input)
            result = impact_plan(value['checkpoints'], value['changed_files'], value.get('ownership'), phase=value.get('phase','intermediate'))
        else:
            result = benchmark(read_json(args.input), read_json(args.baseline) if args.baseline else None)
        if args.output:
            runtime = Path(__file__).resolve().parents[2]
            output = args.output.resolve()
            _require(not output.is_relative_to(runtime), 'UI measurement output must be outside the tool runtime')
            write_json(output, result)
        code=3 if result['status'] in {'stale_evidence','incomplete','needs_current_binding'} else 0
        progress.record(result['status'],result,exit_code=code)
        emit_json(result)
        return code
    except (MigrationError, OSError, ValueError, KeyError, TypeError) as exc:
        result={'status':'error','error':str(exc)}
        progress.record('error',result,exit_code=2)
        emit_json(result)
        return 2
