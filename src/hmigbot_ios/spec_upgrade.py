"""Read-only profile diagnostics and explicitly selected, evidence-bound edits.

This is an upgrade aid, not a gate or a new workflow. It can relocate existing
metadata and qualify an AC target from an already explicit target declaration;
it cannot author missing behavior, approve scope or carry a previous PASS.
"""
from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import re
import shutil
import tempfile

from .core import source_snapshot
from .core import MigrationError, atomic_write, digest, json_bytes, read_json, safe_child, snapshot, source_files, write_json

SCHEMA_VERSION = 1
SCHEMA_PATH = Path(__file__).resolve().parents[2] / 'schemas/spec-upgrade.schema.json'
KNOWN_META_EXTENSIONS = {'presentation_evidence', 'non_product_ranges', 'limitations'}
HANDOFF = [
    'Complete unresolved behavior and source evidence with the original author.',
    'Obtain independent source/content review; proposals establish format only.',
    'Explicitly choose the project profile and run the formal source/spec/harness gates.',
    'Replan explicitly before execution; no previous PASS or receipt is inherited.',
]


def validate_report(value):
    """Enforce the shipped report envelope without an optional package."""
    schema = read_json(SCHEMA_PATH)
    supported = {'$ref', 'type', 'required', 'properties', 'additionalProperties',
                 'const', 'enum', 'minLength', 'pattern', 'minItems', 'uniqueItems', 'items'}
    types = {'object': lambda v: isinstance(v, dict), 'array': lambda v: isinstance(v, list),
             'string': lambda v: isinstance(v, str), 'integer': lambda v: type(v) is int,
             'boolean': lambda v: type(v) is bool}

    def walk(item, rule, location):
        if set(rule) - supported:
            raise MigrationError('Unsupported upgrade schema keyword at ' + location)
        if '$ref' in rule:
            ref = rule['$ref']
            if not ref.startswith('#/$defs/') or ref[8:] not in schema.get('$defs', {}):
                raise MigrationError('Unsupported upgrade schema reference')
            return walk(item, schema['$defs'][ref[8:]], location)
        if 'type' in rule and (rule['type'] not in types or not types[rule['type']](item)):
            raise MigrationError(location + ': wrong type')
        if 'const' in rule and (type(item) is not type(rule['const']) or item != rule['const']):
            raise MigrationError(location + ': wrong constant')
        if 'enum' in rule and not any(type(item) is type(option) and item == option for option in rule['enum']):
            raise MigrationError(location + ': unsupported value')
        if isinstance(item, str):
            if len(item.strip()) < rule.get('minLength', 0) or ('pattern' in rule and not re.search(rule['pattern'], item)):
                raise MigrationError(location + ': invalid string')
        if isinstance(item, list):
            if len(item) < rule.get('minItems', 0) or (rule.get('uniqueItems') and len({json_bytes(i) for i in item}) != len(item)):
                raise MigrationError(location + ': insufficient or duplicate items')
            for index, child in enumerate(item):
                walk(child, rule.get('items', {}), f'{location}[{index}]')
        if isinstance(item, dict):
            if set(rule.get('required', [])) - set(item):
                raise MigrationError(location + ': missing required fields')
            props, additional = rule.get('properties', {}), rule.get('additionalProperties')
            for key, child in item.items():
                if key not in props and additional is False:
                    raise MigrationError(location + ': unknown field ' + key)
                child_rule = props.get(key, additional)
                if isinstance(child_rule, dict):
                    walk(child, child_rule, location + '.' + key)
    walk(value, {key: rule for key, rule in schema.items() if key not in {'$schema', '$id', '$defs'}}, 'spec-upgrade')
    return value


def _inputs(project):
    selected = {}
    for path in source_files(project):
        relative = path.relative_to(project).as_posix()
        if (relative == '.migbot/config.json' or relative == 'spec/decision-ledger.md'
                or relative.startswith(('spec/baseline/', 'spec/ref/'))):
            selected[relative] = digest(path.read_bytes())
    return selected


def _retained_ids(project):
    values = {'features': set(), 'pages': set(), 'acceptance': set()}
    for path in source_files(project):
        if not path.relative_to(project).as_posix().startswith('spec/baseline/') or path.suffix not in {'.md', '.json'}:
            continue
        text = path.read_text(encoding='utf-8-sig')
        values['features'].update(re.findall(r'\bF\d+\b', text))
        values['pages'].update(re.findall(r'\bpage_\d+\b', text))
        values['acceptance'].update(re.findall(r'\bF\d+-AC\d+\b', text))
    return {key: sorted(ids) for key, ids in values.items()}


def _copy_tree(root, destination):
    """Materialize the entire non-generated tree; links fail before copying."""
    files = source_files(root)
    destination.mkdir(parents=True, exist_ok=True)
    for path in files:
        target = safe_child(destination, path.relative_to(root).as_posix())
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(path, target)


def _profile_diagnostics(project, source):
    from .spec_contract import check
    result = {}
    with tempfile.TemporaryDirectory(prefix='hmigbot-spec-upgrade-') as temporary:
        root = Path(temporary)
        virtual_project, virtual_source = root / 'project', root / 'source'
        _copy_tree(source, virtual_source)
        _copy_tree(project, virtual_project)
        config_path = virtual_project / '.migbot/config.json'
        config = read_json(config_path)
        config['ios'] = str(virtual_source)
        config['harmonyos'] = str(virtual_project)
        for profile in (1, 2):
            virtual_config = deepcopy(config)
            virtual_config.setdefault('ios_harness', {})['spec_contract_version'] = profile
            write_json(config_path, virtual_config)
            try:
                report, code = check(virtual_project)
            except (MigrationError, OSError, UnicodeError, KeyError, TypeError) as exc:
                report, code = {'status': 'FAIL', 'findings': [{'rule': 'UPGRADE.PROFILE_ERROR',
                    'subject': 'spec/baseline', 'detail': str(exc)}]}, 2
            # Temporary directory names must not leak into a reusable diagnosis.
            findings = []
            for finding in report['findings']:
                item = {key: finding.get(key, '') for key in ('rule', 'subject', 'detail')}
                for key in ('subject', 'detail'):
                    item[key] = item[key].replace(str(virtual_project), '<project>').replace(str(virtual_source), '<source>')
                findings.append(item)
            result[str(profile)] = {'status': report['status'], 'exit_code': code, 'findings': findings}
    return result


def _classified_findings(profiles):
    grouped = {}
    for number in (1, 2):
        for finding in profiles[str(number)]['findings']:
            missing = finding['rule'].endswith(('DOCUMENT_MISSING', 'ARTIFACT_MISSING'))
            key = ('missing', finding['subject']) if missing else (finding['rule'], finding['subject'], finding['detail'])
            item = grouped.setdefault(key, {'category': 'missing' if missing else 'v2_added',
                'subject': finding['subject'], 'profiles': [], 'rules': [], 'origins': []})
            if number not in item['profiles']:
                item['profiles'].append(number)
            if finding['rule'] not in item['rules']:
                item['rules'].append(finding['rule'])
            origin = {'profile': number, **finding}
            if origin not in item['origins']:
                item['origins'].append(origin)
            if number == 1 and not missing:
                item['category'] = 'legacy'
    return list(grouped.values())


def _manual(path, rule, detail, **extra):
    return {'rule': 'UPGRADE.' + rule, 'subject': path, 'detail': detail, 'blocking': True, **extra}


def _patch(project, path, content, operations):
    before = path.read_bytes()
    after = content.encode('utf-8')
    relative = path.relative_to(project).as_posix()
    identity = {'path': relative, 'before_sha256': digest(before), 'after_sha256': digest(after), 'operations': operations}
    return {'patch_id': 'UP-' + digest(json_bytes(identity))[:20], **identity, 'content': content}


def _meta_candidate(project, source, path):
    from .artifact_contract import SCHEMA_PATH
    relative = path.relative_to(project).as_posix()
    try:
        old = read_json(path)
        if not isinstance(old, dict):
            raise MigrationError('Metadata must be an object')
        known_fields = set(read_json(SCHEMA_PATH)['$defs']['page_meta']['properties'])
        unknown = set(old) - known_fields - KNOWN_META_EXTENSIONS
        if unknown:
            raise MigrationError('Unknown metadata fields need an author decision: ' + ', '.join(sorted(unknown)))
        value, operations = deepcopy(old), []
        extensions = value.get('extensions', {})
        if not isinstance(extensions, dict):
            raise MigrationError('Existing extensions must be an object')
        for key in sorted(KNOWN_META_EXTENSIONS & set(value)):
            if key in extensions and extensions[key] != value[key]:
                raise MigrationError('Conflicting extensions value: ' + key)
            extensions[key] = value.pop(key)
            operations.append({'kind': 'relocate_meta_extension', 'field': key})
        refs = value.get('source_refs')
        if isinstance(refs, list) and any(isinstance(ref, dict) for ref in refs):
            anchors = value.get('source_anchors')
            if not isinstance(anchors, list) or not anchors or any(not isinstance(a, dict) for a in anchors):
                raise MigrationError('Object source_refs require existing matching structured anchors')
            converted, ranges = [], []
            retained_objects = False
            for ref in refs:
                if isinstance(ref, str):
                    match = re.fullmatch(r'(.+):(\d+)(?:-(\d+))?', ref)
                    if not match:
                        raise MigrationError('Mixed source_refs contain an unsupported source range')
                    name, line, end = match[1], int(match[2]), int(match[3] or match[2])
                    converted.append(ref)
                elif isinstance(ref, dict):
                    if set(ref) - {'path', 'line', 'end_line', 'symbol', 'role', 'sha256'}:
                        raise MigrationError('Object source_refs contain unknown fields')
                    name, line, end = ref.get('path'), ref.get('line'), ref.get('end_line', ref.get('line'))
                    if not isinstance(name, str) or type(line) is not int or type(end) is not int:
                        raise MigrationError('Object source_refs need a literal path and integer line/range')
                    matches = [a for a in anchors if a.get('path') == name and a.get('line') == line
                               and all(a.get(k) == ref[k] for k in ('symbol', 'role') if k in ref)]
                    if not matches:
                        raise MigrationError('source_refs and source_anchors disagree; do not infer a new anchor')
                    converted.append(f'{name}:{line}' + (f'-{end}' if end != line else ''))
                    retained_objects |= bool(set(ref) - {'path', 'line', 'end_line'})
                    if 'sha256' in ref and ref['sha256'] != digest(safe_child(source, name).read_bytes()):
                        raise MigrationError('Object source_refs file hash is stale')
                else:
                    raise MigrationError('source_refs must contain strings or supported objects')
                source_file = safe_child(source, name)
                if not source_file.is_file() or not 1 <= line <= end <= len(source_file.read_text(encoding='utf-8-sig').splitlines()):
                    raise MigrationError('source_refs range is outside current source')
                ranges.append((name, line, end))
            if ({r[0] for r in ranges} != {a.get('path') for a in anchors}
                    or any(type(a.get('line')) is not int or not any(n == a.get('path') and start <= a['line'] <= stop
                            for n, start, stop in ranges) for a in anchors)):
                raise MigrationError('source_refs and source_anchors must cover the same existing evidence')
            if retained_objects:
                if 'legacy_source_refs' in extensions and extensions['legacy_source_refs'] != refs:
                    raise MigrationError('Conflicting extensions.legacy_source_refs')
                extensions['legacy_source_refs'] = refs
            value['source_refs'] = converted
            operations.append({'kind': 'normalize_source_refs', 'anchors_unchanged': True})
        if operations:
            if extensions or 'extensions' in value:
                value['extensions'] = extensions
            return _patch(project, path, json_bytes(value).decode('utf-8'), operations), []
        return None, []
    except (MigrationError, OSError, UnicodeError, KeyError, TypeError) as exc:
        return None, [_manual(relative, 'META_MANUAL', str(exc))]


def _feature_candidate(project, path):
    from .spec_contract import AC, declared_symbols, references, sections
    from .artifact_contract import _visible_lines
    # A target token edit must not rewrite a user's BOM or line endings.
    text = path.read_bytes().decode('utf-8')
    relative = path.relative_to(project).as_posix()
    manual, operations, substitutions = [], [], []
    try:
        symbols = declared_symbols(sections(text))
        pending, visited = [path], set()
        while pending:
            current = pending.pop()
            if current in visited:
                continue
            visited.add(current)
            for target, heading, body in references(project, current, current.read_text(encoding='utf-8-sig')):
                symbols.update(declared_symbols({heading: body}))
                pending.append(target)
        visible_lines = {number for number, _ in _visible_lines(text)}
        for assertion in AC.finditer(text):
            # AC examples inside a code block are source text to preserve,
            # never authored acceptance criteria to upgrade.
            if text.count('\n', 0, assertion.start()) + 1 not in visible_lines:
                continue
            ident, body = assertion[1], assertion[2]
            slots = []
            for inline in re.finditer(r'`([^`\r\n]+)`', body):
                # This is the documented source -> target contract slot. A
                # marker in an expected result or ordinary prose is content,
                # not a target that this formatter is allowed to rewrite.
                marker = re.match(r'^\s*源:[^`\r\n]+?(?:→|->)\s*标:\s*'
                                  r'([A-Za-z_]\w*(?:\.[A-Za-z_]\w*)*)(?=\s*(?:\(|$))', inline[1])
                if marker:
                    slots.append((inline.start(1) + marker.start(1), inline.start(1) + marker.end(1), marker[1]))
            if len(slots) != 1:
                if slots or re.search(r'标:\s*[A-Za-z_]\w*(?=[`\s(,;]|$)', body):
                    manual.append(_manual(relative, 'TARGET_MANUAL',
                        'An automatic target edit requires one explicit inline source -> target contract slot.', ac_id=ident))
                continue
            start, stop, short = slots[0]
            if '.' in short:
                continue
            candidates = sorted(symbol for symbol in symbols if symbol.rsplit('.', 1)[-1] == short)
            if len(candidates) != 1:
                manual.append(_manual(relative, 'TARGET_MANUAL',
                    'Unqualified AC target needs one existing explicit owner.symbol declaration; no owner is inferred.',
                    ac_id=ident, target=short, candidates=candidates))
                continue
            substitutions.append((assertion.start(2) + start, assertion.start(2) + stop, candidates[0]))
            operations.append({'kind': 'qualify_ac_target', 'ac_id': ident, 'from': short, 'to': candidates[0]})
    except (MigrationError, OSError, UnicodeError, KeyError, TypeError) as exc:
        manual.append(_manual(relative, 'TARGET_MANUAL', str(exc)))
        return None, manual
    if not substitutions:
        return None, manual
    for start, stop, value in reversed(substitutions):
        text = text[:start] + value + text[stop:]
    return _patch(project, path, text, operations), manual


def inspect(project):
    """Compare both profiles in a disposable materialized copy, writing nothing."""
    from .native_pipeline import context
    from .artifact_contract import contract_version, revision
    source, project = context(Path(project))
    if source == project or source.is_relative_to(project) or project.is_relative_to(source):
        raise MigrationError('Upgrade inspection requires separate source and target trees')
    inputs, source_digest = _inputs(project), source_snapshot(source)['sha256']
    profile = contract_version(project)
    diagnostics = _profile_diagnostics(project, source)
    patches, manual = [], []
    for path in sorted((project / 'spec/baseline/ui-snapshots').glob('*/meta.json')):
        patch, notes = _meta_candidate(project, source, path)
        patches.extend([patch] if patch else []); manual.extend(notes)
    for path in sorted((project / 'spec/baseline/features').glob('F*.md')):
        if re.match(r'F\d+[-_].+\..+\.md$', path.name):
            continue
        patch, notes = _feature_candidate(project, path)
        patches.extend([patch] if patch else []); manual.extend(notes)
    if inputs != _inputs(project) or source_digest != source_snapshot(source)['sha256']:
        raise MigrationError('Source or Spec inputs changed during inspection; retry against stable inputs')
    return validate_report({'schema_version': SCHEMA_VERSION, 'kind': 'hmigbot-ios/spec-upgrade',
        'status': 'diagnostic_requires_review', 'project_root': str(project), 'source_root': str(source),
        'source_sha256': source_digest, 'input_hashes': inputs, 'spec_contract_version': profile,
        'artifact_contract_revision': revision(project), 'retained_ids': _retained_ids(project),
        'profile_diagnostics': diagnostics, 'findings': _classified_findings(diagnostics),
        'patches': patches, 'manual': manual, 'behavior_verified': False, 'handoff': HANDOFF.copy()})


def _allowed_patch_path(project, relative):
    path = safe_child(project, relative)
    if not (re.fullmatch(r'spec/baseline/features/F\d+[^/]*\.md', relative)
            or re.fullmatch(r'spec/baseline/ui-snapshots/page_\d+/meta\.json', relative)):
        raise MigrationError('Upgrade patches may edit only feature Markdown or page metadata in baseline')
    return path


def apply(project, report, *, patch_ids=None):
    """Apply exactly selected proposals after recomputing their safe equivalent.

    No implicit all mode: CLI callers must expand an explicit --all-candidates.
    Every selected edit is preflighted before the first write. Original ledgers,
    project profile, AC checkbox state and stable IDs remain untouched.
    """
    if not isinstance(patch_ids, list) or not patch_ids or any(not isinstance(i, str) for i in patch_ids) or len(set(patch_ids)) != len(patch_ids):
        raise MigrationError('Explicit unique patch_ids are required to apply upgrade candidates')
    validate_report(report)
    project = Path(project).resolve()
    for patch in report.get('patches', []):
        if not isinstance(patch, dict) or not isinstance(patch.get('path'), str):
            raise MigrationError('Malformed upgrade candidate')
        _allowed_patch_path(project, patch['path'])
    current = inspect(project)
    for field in ('project_root', 'source_root', 'source_sha256', 'input_hashes',
                  'spec_contract_version', 'artifact_contract_revision', 'retained_ids'):
        if report.get(field) != current[field]:
            raise MigrationError('Stale upgrade diagnosis: ' + field)
    proposed = report.get('patches')
    if not isinstance(proposed, list) or any(not isinstance(p.get('patch_id'), str) for p in proposed):
        raise MigrationError('Upgrade candidates must be an identified list')
    by_id = {p['patch_id']: p for p in proposed}
    canonical = {p['patch_id']: p for p in current['patches']}
    if len(by_id) != len(proposed):
        raise MigrationError('Duplicate upgrade candidate IDs')
    writes = []
    for ident in patch_ids:
        if ident not in canonical or by_id.get(ident) != canonical[ident]:
            raise MigrationError('Upgrade candidate is unknown or differs from a current safe proposal: ' + ident)
        patch = canonical[ident]
        path = _allowed_patch_path(project, patch['path'])
        if digest(path.read_bytes()) != patch['before_sha256']:
            raise MigrationError('Upgrade target changed: ' + patch['path'])
        writes.append((path, patch['content'].encode('utf-8')))
    # Recheck input bindings immediately before the write set, including additions.
    from .native_pipeline import context
    source, _ = context(project)
    if _inputs(project) != current['input_hashes'] or source_snapshot(source)['sha256'] != current['source_sha256']:
        raise MigrationError('Source or Spec inputs changed during apply preflight')
    for path, data in writes:
        atomic_write(path, data)
    return {'schema_version': SCHEMA_VERSION, 'status': 'applied_requires_review',
        'applied_patch_ids': patch_ids.copy(), 'behavior_verified': False,
        'spec_contract_version': current['spec_contract_version'], 'retained_ids': current['retained_ids'],
        'handoff': HANDOFF.copy()}
