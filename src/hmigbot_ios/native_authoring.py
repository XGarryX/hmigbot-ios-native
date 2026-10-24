"""Source-bound authoring forms and validated candidates for the existing Spec phase.

No baseline, source, findings or scheduler ledger is changed. The model supplies
reviewed meaning; this renderer supplies identities, field shape and truth tokens.
Candidates still require the existing source, harness and independent review gates.
"""
from copy import deepcopy
from pathlib import Path
import re

from .artifact_contract import markdown_tables, validate_json
from .core import MigrationError, digest, json_bytes, read_json, safe_child, snapshot
from .native_contract import source_truth, validate_literal_exclusion
from .native_semantics import COMMON, PAGE, FEATURE, SWIFTUI, UIKIT, SWIFT, OBJC, required_facts, validate_native_payload
from .source_scope import source_anchor_info


def _inventory(project):
    from .native_pipeline import context, source_paths, CODE
    from .spec_contract import acceptance
    source, project = context(Path(project))
    base = project / 'spec/baseline'
    index = read_json(base / 'ios-source-index.json')
    current = snapshot(source)
    if index.get('source_sha256') != current['sha256'] or index.get('files') != current['files']:
        raise MigrationError('Authoring needs a current reviewed source index; use facts/source-refresh and re-review, never delete the index')
    known = {f['path']: f for f in current['files']}
    documents, acs, inputs, owned, addenda = {}, [], {}, set(), []

    def collect_acceptance(text, ident, path, sources):
        for ac_id, body in acceptance(text):
            if any(a['ac_id'] == ac_id for a in acs):
                raise MigrationError('Duplicate authoring acceptance: ' + ac_id)
            external = re.search(r'真:(?:test|trace|device|decision):[^`\s]+', body)
            acs.append({'ac_id': ac_id, 'feature_id': ident, 'spec': path,
                        'requires_source_truth': not bool(external) or '真:src:' in body,
                        'allowed_sources': sources})
    for folder, pattern, kind in (('features', 'F*.md', 'feature'), ('ui', 'page_*.md', 'page')):
        for file in sorted((base / folder).glob(pattern)):
            if kind == 'feature' and re.match(r'F\d+[-_].+\..+\.md$', file.name):
                addenda.append(file)
                continue
            match = re.match(r'^(F\d+|page_\d+)', file.stem)
            if not match:
                continue
            ident = match[1]
            if ident in documents:
                raise MigrationError('Duplicate authoring document: ' + ident)
            text = file.read_text(encoding='utf-8-sig')
            path = file.relative_to(project).as_posix()
            inputs[path] = digest(file.read_bytes())
            anchors = source_paths(text)
            if not anchors:
                raise MigrationError('Authoring document needs real source_anchors: ' + ident)
            sources = []
            for anchor in anchors:
                actual = safe_child(source, anchor)
                if anchor not in known or not actual.is_file():
                    raise MigrationError('Authoring source anchor is outside the index: ' + anchor)
                sources.append({'path': anchor, 'sha256': known[anchor]['sha256'],
                                **source_anchor_info(actual)})
                owned.add(anchor)
            documents[ident] = {'id': ident, 'kind': kind, 'spec': path, 'source_anchors': sources,
                               'required_common_facts': sorted(COMMON | (PAGE if kind == 'page' else FEATURE))}
            if kind == 'feature':
                collect_acceptance(text, ident, path, sources)
    for file in addenda:
        ident = re.match(r'^(F\d+)', file.stem)[1]
        if ident not in documents:
            raise MigrationError('Feature addendum has no main document: ' + file.name)
        path = file.relative_to(project).as_posix()
        inputs[path] = digest(file.read_bytes())
        collect_acceptance(file.read_text(encoding='utf-8-sig'), ident, path, documents[ident]['source_anchors'])
    for name, column, pattern in (('feature-index.md', 'ID', r'F\d+'), ('ui-manifest.md', 'page_id', r'page_\d+')):
        path = base / name
        if not path.exists():
            continue  # The formal spec gate still requires its complete index contract.
        inputs[path.relative_to(project).as_posix()] = digest(path.read_bytes())
        for table in markdown_tables(path.read_text(encoding='utf-8-sig')):
            if column not in table['headers']:
                continue
            pos = table['headers'].index(column)
            for row in table['rows']:
                ident = row[pos].strip('` ') if len(row) > pos else ''
                if re.fullmatch(pattern, ident) and ident not in documents:
                    raise MigrationError('Indexed authoring document is missing: ' + ident)
    if not documents or not any(d['kind'] == 'feature' for d in documents.values()):
        raise MigrationError('Write the page/feature inventory before preparing authoring')
    inputs['.migbot/config.json'] = digest((project / '.migbot/config.json').read_bytes())
    inputs['spec/baseline/ios-source-index.json'] = digest((base / 'ios-source-index.json').read_bytes())
    for name in ('ios-facts.json', 'ios-obligations.json', 'ios-responsibility.json'):
        path = base / name
        if path.is_file():
            inputs[path.relative_to(project).as_posix()] = digest(path.read_bytes())
    if (base / 'ios-responsibility.json').exists():
        from .ios_harness import responsibility
        inputs.update(responsibility(project, source=source).frozen_inputs())
    inventory = {'source_sha256': current['sha256'], 'inputs': inputs,
                 'documents': list(documents.values()), 'acceptance': acs,
                 'unaccounted_sources': sorted(p for p in known if Path(p).suffix.lower() in CODE and p not in owned),
                 'conditional_dimensions': {'swift': sorted(SWIFT), 'objc/objcxx': sorted(OBJC),
                                            'swiftui_page': sorted(SWIFTUI), 'uikit/ib_page': sorted(UIKIT)}}
    return source, project, known, inventory


def prepare(project):
    source, project, known, inventory = _inventory(project)
    template = {'schema_version': 1, 'source_sha256': inventory['source_sha256'],
                'inventory_sha256': digest(json_bytes(inventory)), 'documents': [],
                'dispositions': [], 'truth_anchors': []}
    for doc in inventory['documents']:
        template['documents'].append({'id': doc['id'], 'kind': doc['kind'], 'languages': [], 'frameworks': [],
            'facts': {dimension: {'status': 'unknown', 'reason': f'Source review required for {doc["id"]}:{dimension}'}
                      for dimension in doc['required_common_facts']}})
    return {'schema_version': 1, 'status': 'needs_authoring', **inventory, 'input_template': template,
            'disposition_contract': {'schema': 'schemas/spec-artifacts.schema.json#/$defs/source_disposition',
                                     'required_entry_fields': ['path', 'disposition', 'reason', 'line', 'end_line', 'source_sha256'],
                                     'entry_example': {'path': '<source-relative indexed file>', 'disposition': 'test',
                                                       'reason': '<independent reviewed reason>', 'line': 1,
                                                       'end_line': '<inclusive last reviewed line>',
                                                       'source_sha256': '<sha256 of this file current bytes>'},
                                     'source_sha256_levels': 'top level binds the whole-source snapshot; each entry binds its own file bytes',
                                     'evidence': 'line/end_line and the per-file hash are checked against the current source before planning',
                                     'owner_mapping_destination': 'page/feature source_anchors; never disposition.files'},
            'spec_complete': False, 'behavior_verified': False}


def render(project, request):
    source, project, known, inventory = _inventory(project)
    if not isinstance(request, dict) or request.get('schema_version') != 1:
        raise MigrationError('Authoring input requires schema_version=1')
    if (request.get('inventory_sha256') != digest(json_bytes(inventory))
            or request.get('source_sha256') != inventory['source_sha256']):
        raise MigrationError('Authoring inventory/source changed; prepare again and re-review')
    expected = {d['id']: d for d in inventory['documents']}
    records = request.get('documents')
    if (not isinstance(records, list) or any(not isinstance(d, dict) or not isinstance(d.get('id'), str) for d in records)
            or len(records) != len(expected) or {d['id'] for d in records} != set(expected)):
        raise MigrationError('Native documents must cover every page/feature exactly once; no missing, extra or duplicate documents')
    semantics = {'schema_version': 2, 'source_platform': 'ios', 'documents': deepcopy(records)}
    from .ios_facts import validate_graph
    from .ios_harness import responsibility
    graph, obs = validate_graph(source, project)
    candidate = request.get('responsibility')
    if 'responsibility' in request and not isinstance(candidate, dict):
        raise MigrationError('Responsibility candidate must be an explicit object')
    projection = responsibility(project, source=source, graph=graph, obligations=obs,
                                semantics=semantics, candidate=candidate)
    for doc in records:
        if doc.get('kind') != expected[doc['id']]['kind']:
            raise MigrationError('Native document kind differs from its spec: ' + doc['id'])
        if (not isinstance(doc.get('languages'), list) or not doc['languages']
                or not isinstance(doc.get('frameworks'), list) or not doc['frameworks']
                or any(not isinstance(v, str) for v in doc['languages'] + doc['frameworks'])):
            raise MigrationError('Choose actual source languages/frameworks before rendering: ' + doc['id'])
        required = required_facts(doc['kind'], set(doc['languages']), set(doc['frameworks']))
        facts = doc.get('facts')
        if not isinstance(facts, dict) or required - facts.keys():
            missing = required - facts.keys() if isinstance(facts, dict) else required
            raise MigrationError('Missing native dimensions for ' + doc['id'] + ': ' + ', '.join(sorted(missing)))
        for dimension, claim in facts.items():
            if not isinstance(claim, dict):
                raise MigrationError('Native source review is incomplete: ' + doc['id'] + ':' + dimension)
            if claim.get('status') == 'unknown' and (projection is None or
                    projection.semantic_requirement(doc['id'], dimension, claim)['target_required']):
                raise MigrationError('Native source review is incomplete: ' + doc['id'] + ':' + dimension)
            if claim.get('status') == 'known' and (not isinstance(claim.get('value'), dict) or not claim['value']
                    or not isinstance(claim.get('fact_ids'), list) or not claim['fact_ids']
                    or any(not isinstance(f, str) for f in claim['fact_ids'])):
                raise MigrationError('Known native claim requires typed value and current fact_ids: ' + doc['id'] + ':' + dimension)
    dispositions = request.get('dispositions')
    if not isinstance(dispositions, list):
        raise MigrationError('Authoring dispositions must be a list of reviewed exclusions')
    seen = set()
    for item in dispositions:
        validate_literal_exclusion(source, known, item)
        if item['path'] in seen:
            raise MigrationError('Duplicate source disposition: ' + item['path'])
        seen.add(item['path'])
    validate_json({'source_sha256': inventory['source_sha256'], 'files': dispositions}, 'source_disposition')
    unaccounted = set(inventory['unaccounted_sources']) - seen
    if unaccounted:
        raise MigrationError('Source files still need reviewed ownership/disposition: ' + ', '.join(sorted(unaccounted)))
    semantics = {'schema_version': 2, 'source_platform': 'ios', 'documents': deepcopy(records)}
    native_issues = []
    validate_native_payload(source, project,
        {ident: (d['kind'], [a['path'] for a in d['source_anchors']]) for ident, d in expected.items()},
        set(known), lambda *issue: native_issues.append(issue), semantics, projection=projection)
    if native_issues:
        raise MigrationError('Native authoring rejected: ' + '; '.join(': '.join(i) for i in native_issues))
    from .ios_facts import validate_graph
    graph, _ = validate_graph(source, project)
    from .ios_harness import validate_native_claims
    validate_native_claims(project, graph, semantics, lambda *issue: native_issues.append(issue), projection=projection)
    if native_issues:
        raise MigrationError('Native authoring rejected: ' + '; '.join(': '.join(i) for i in native_issues))
    truths = request.get('truth_anchors')
    expected_truths = {a['ac_id']: a for a in inventory['acceptance'] if a['requires_source_truth']}
    if (not isinstance(truths, list) or any(not isinstance(t, dict) or not isinstance(t.get('ac_id'), str) for t in truths)
            or len(truths) != len(expected_truths) or {t['ac_id'] for t in truths} != set(expected_truths)):
        raise MigrationError('Supply one exact source truth for every source-based AC; no duplicates or unowned truths')
    files = {'spec/baseline/ios-semantics.json': semantics,
             'spec/baseline/ios-source-disposition.json': {'source_sha256': inventory['source_sha256'], 'files': deepcopy(dispositions)}}
    if candidate is not None:
        files['spec/baseline/ios-responsibility.json'] = deepcopy(candidate)
    for truth in truths:
        ac = expected_truths[truth['ac_id']]
        token = source_truth(source, [a['path'] for a in ac['allowed_sources']], truth.get('path'), truth.get('line'))
        path = ac['spec']
        text = files.get(path, safe_child(project, path).read_text(encoding='utf-8-sig'))
        lines = text.splitlines(keepends=True)
        matches = [n for n, line in enumerate(lines) if re.match(r'^- \[[ xX]\]\s+' + re.escape(truth['ac_id']) + r'\s', line)]
        if len(matches) != 1:
            raise MigrationError('Ambiguous authoring acceptance line: ' + truth['ac_id'])
        n = matches[0]
        if len(re.findall('真:', lines[n])) > 1:
            raise MigrationError('Multiple truth declarations need source review: ' + truth['ac_id'])
        if '真:src:' in lines[n]:
            lines[n], count = re.subn(r'真:src:[^`\r\n|]+',
                lambda match: token + re.search(r'\s*$', match[0])[0], lines[n])
            if count != 1:
                raise MigrationError('Cannot render source truth: ' + truth['ac_id'])
        else:
            lines[n] = lines[n].rstrip('\r\n') + ' `' + token + '`\n'
        files[path] = ''.join(lines)
    input_hashes = dict(inventory['inputs'])
    candidate_hashes = {'native_semantics': digest(json_bytes(semantics))}
    if projection is not None:
        projection.validate_frozen_inputs(project)
        input_hashes.update(projection.frozen_inputs())
        # A truth edit must not silently invalidate the independent review and
        # original supersedes/emits closure that authorized this projection.
        for relative, value in files.items():
            if isinstance(value, str) and relative in projection.frozen_inputs():
                if digest(value.encode('utf-8')) != projection.frozen_inputs()[relative]:
                    raise MigrationError('Responsibility-bound source contract changed; re-review the proof before rendering: ' + relative)
        if candidate is not None:
            candidate_hashes['responsibility'] = digest(json_bytes(candidate))
    for relative, expected_hash in input_hashes.items():
        if digest(safe_child(project, relative).read_bytes()) != expected_hash:
            raise MigrationError('Authoring input changed during rendering: ' + relative)
    if snapshot(source)['sha256'] != inventory['source_sha256']:
        raise MigrationError('Authoring source changed during rendering')
    return {'schema_version': 1, 'status': 'candidate', 'inventory_sha256': request['inventory_sha256'],
            'source_sha256': inventory['source_sha256'], 'files': files,
            'input_hashes': input_hashes, 'candidate_hashes': candidate_hashes,
            'responsibility_candidate': candidate is not None,
            'required_checks': ['independent source/content review', 'spec-check', 'source-check --harness'],
            'spec_complete': False, 'behavior_verified': False}
