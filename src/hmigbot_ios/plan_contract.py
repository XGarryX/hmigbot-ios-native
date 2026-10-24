"""Read-only correspondence between indexed Markdown plans and typed requests.

Markdown remains the reviewed plan. Its bounded JSON projection is checked against
the prose/table item and the spec; a request is only a scheduling allocation of
those items. This module never writes the upstream control ledgers.
"""
from __future__ import annotations

import json
import re
from collections import defaultdict
from pathlib import Path

from .core import MigrationError, digest, json_bytes, read_json, safe_child

PROGRESS_VALUES = {'pending', 'converted', 'implemented', 'verified', 'generated', 'blocked',
                   'not_run', 'running', 'passed', 'failed', 'stale', 'PASS', 'FAIL'}
VERIFICATION = {'generated', 'compile', 'behavior', 'visual'}
VERIFICATION_RANK = {'generated': 0, 'compile': 1, 'behavior': 2, 'visual': 3}
AC = re.compile(r'^- \[[ xX]\]\s+(F\d+-AC\d+)\b', re.M)


def profile(project):
    from .artifact_contract import contract_version
    return contract_version(Path(project))


def contract_revision(project):
    from .artifact_contract import revision
    root = Path(__file__).resolve().parents[2]
    paths = [root / 'schemas/ios-harness-v2.schema.json', Path(__file__).resolve(),
             root / 'src/hmigbot_ios/source_responsibility.py',
             root / 'src/hmigbot_ios/macos_permissions.py', root / 'src/hmigbot_ios/portable_helper.py',
             root / 'src/hmigbot_ios/native_pipeline_runtime.py', root / 'src/hmigbot_ios/upgrade_cleanup.py',
             root / 'src/hmigbot_ios/conditional_evidence.py',
             root / 'src/hmigbot_ios/native_semantics.py', root / 'src/hmigbot_ios/native_authoring.py',
             root / 'src/hmigbot_ios/native_pipeline.py', root / 'src/hmigbot_ios/quality_views.py',
             root / 'src/hmigbot_ios/artifact_contract.py', root / 'src/hmigbot_ios/spec_contract.py',
             root / 'src/hmigbot_ios/source_scope.py', root / 'src/hmigbot_ios/ios_harness.py',
             root / 'src/hmigbot_ios/ios_scheduler.py', root / 'src/hmigbot_ios/replan_recovery.py', root / 'src/hmigbot_ios/harness_schema.py',
             root / 'src/hmigbot_ios/capability_contract.py',
             root / 'src/hmigbot_ios/capability_manifest.py', root / 'src/hmigbot_ios/capability_runtime.py',
             root / 'src/hmigbot_ios/behavior.py',
             root / 'src/hmigbot_ios/ios_facts.py', root / 'src/hmigbot_ios/objc_state.py',
             root / 'src/hmigbot_ios/native_pipeline_semantics.py',
             root / 'skills/arkts-structural-closure/scripts/gen_capability_manifest.py',
             root / 'skills/arkts-structural-closure/scripts/capability_ledger_gate.py',
             root / 'skills/arkts-structural-closure/SKILL.md',
             root / 'skills/a2h-plan/references/plan-delivery-contract.md']
    paths += [root / 'src/hmigbot_ios' / name for name in ('swiftui.py', 'computed_properties.py', 'spec_discovery.py', 'spec_helpers.py', 'finding_identity.py', 'provider_plan.py', 'provider_runs.py', 'providers.py', 'gate_artifacts.py', 'native_scaffold.py', 'init_environment.py', 'source_candidates.py', 'artifact_commit.py', 'verification_scope.py', 'source_build_membership.py')]
    paths += [root / 'runtime-entrypoints.json', root / 'schemas/source-build-membership.schema.json']
    # All maintained readers/routers and schema adapters participate in the freeze,
    # including old modules whose policy changed through a shared service.
    paths += sorted((root / 'src/hmigbot_ios').glob('*.py'))
    paths += sorted((root / 'src/hmigbot_ios').glob('*.json'))
    paths += sorted((root / 'schemas').glob('*.json'))
    scheduler_payload = root / 'vendor/hmigbot-1.7.0/skills/a2h-execute/scripts'
    paths += sorted(scheduler_payload.glob('*.py'))
    paths += sorted(scheduler_payload.glob('bin/*/_entry.dist/_entry.bin'))
    paths += sorted(scheduler_payload.glob('bin/*/_entry.dist/_entry.exe'))
    paths += sorted((root / 'skills/a2h-plan/templates').glob('*.md'))
    from .source_responsibility import parser_fingerprints
    return digest(json_bytes({'artifacts': revision(Path(project)),
                              'source_responsibility_parsers': parser_fingerprints(),
                              'plan_rules': {p.relative_to(root).as_posix(): digest(p.read_bytes()) for p in paths if p.is_file()}}))


def assert_pinned(project, contract):
    """A config/CLI downgrade cannot turn a frozen v2 run into a legacy run."""
    pinned = contract.get('spec_contract_version', 1)
    if profile(project) != pinned:
        raise MigrationError('Frozen spec contract profile changed; restore it before reviewed replan')
    responsibility_enabled = contract.get('responsibility_enabled') is True or (Path(project) / 'spec/baseline/ios-responsibility.json').is_file()
    if (pinned >= 2 or responsibility_enabled) and contract.get('contract_revision') != contract_revision(project):
        raise MigrationError('Frozen tool contract revision changed; review and explicitly replan')


def _core_index_tables(text, artifact):
    """Select the catalog index table, not other tables reusing its IDs."""
    from .artifact_contract import canonical_headers, catalog, markdown_sections, markdown_tables
    declarations = [section for entry in catalog()['spec'] if entry.get('path') == artifact
                    for section in entry.get('sections', []) if section.get('progress')]
    headings, tables = markdown_sections(text), markdown_tables(text)
    selected = []
    for section in declarations:
        matches = []
        for table in tables:
            prior = [heading for heading in headings if heading['line'] < table['line']]
            headers = canonical_headers(section, table['headers'])
            if (headers is not None and prior
                    and prior[-1]['title'] == section['title']):
                matches.append({**table, 'authored_headers': table['headers'], 'headers': headers})
        if len(matches) > 1:
            raise MigrationError('Core index progress table must be unique: ' + str(artifact))
        if matches:
            selected.append((section, matches[0]))
    return selected


def structural_digest(text, *, artifact=None):
    """Project only the catalog's core index progress cells, never business state.

    The artifact identity, exact heading/header and stable row ID are all needed
    before a cell can be mutable. Other tables retain their original lines,
    including adjacent tables and business tables which happen to use status.
    """
    begin, end = '<!-- hmigbot-progress:begin -->', '<!-- hmigbot-progress:end -->'
    if text.count(begin) != text.count(end) or text.count(begin) > 1:
        raise MigrationError('Malformed managed progress block')
    if begin in text:
        if text.index(begin) > text.index(end):
            raise MigrationError('Malformed managed progress block order')
        content = text[text.index(begin) + len(begin):text.index(end)]
        for entry in content.splitlines():
            entry = re.sub(r'^\s*(?:-\s+)?', '', entry).strip()
            count = r'(?:\d+ of \d+|(?:generation|acceptance|features|pages|registered|resolved):\s*\d+(?:/\d+)?)'
            state = r'(?:generation|compilation|behavior|visual):\s*(?:pending|not_run|running|passed|failed|stale|blocked|generated|unverified)'
            if entry and not re.fullmatch('(?:' + count + '|' + state + ')', entry):
                raise MigrationError('Managed progress only permits defined count/axis state lines')
        text = text[:text.index(begin)] + begin + '\n' + end + text[text.index(end) + len(end):]
    lines = text.splitlines()
    for section, table in _core_index_tables(text, artifact):
        progress = section['progress']
        id_column = table['headers'].index(progress['id_column'])
        columns = [table['headers'].index(name) for name in progress['columns']]
        identities = [row[id_column].strip('` ') for row in table['rows']
                      if len(row) == len(table['headers'])]
        for row, number, spans in zip(table['rows'], table['row_lines'], table['row_cell_spans']):
            if len(row) != len(table['headers']):
                continue
            ident = row[id_column].strip('` ')
            if not re.fullmatch(progress['id_pattern'], ident) or identities.count(ident) != 1:
                continue
            line, segments, cursor = lines[number - 1], [], 0
            for column in sorted(columns):
                if row[column] in PROGRESS_VALUES:
                    start, end = spans[column]
                    segments.extend([line[cursor:start], {'managed_progress': True}])
                    cursor = end
            # Replace just the permitted cell span; even whitespace, escaping
            # and inline code in another core column remain frozen as authored.
            # A typed marker cannot collide with text authored in an invalid
            # state cell, unlike a reserved string embedded in the Markdown.
            if segments:
                lines[number - 1] = {'progress_projection': segments + [line[cursor:]]}
    return digest(json_bytes(lines))


def _sections(text):
    from .artifact_contract import markdown_sections
    return markdown_sections(text)


def _tables(text):
    from .artifact_contract import markdown_tables
    return markdown_tables(text)


def _plain(text):
    return re.sub(r'^\s*(`{3,}|~{3,})[^\n]*\n.*?^\s*\1\s*$', '', text, flags=re.M | re.S)


def _strings(value, subject):
    if not isinstance(value, list) or any(not isinstance(v, str) or not v.strip() for v in value) or len(set(value)) != len(value):
        raise MigrationError('Expected unique nonempty strings: ' + subject)
    return set(value)


def _projection(project, path):
    from .harness_schema import validate
    text = path.read_text(encoding='utf-8-sig')
    candidates = []
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise MigrationError('Duplicate plan projection field: ' + key)
            result[key] = value
        return result
    for block in re.findall(r'^\s*```json\s*\n(.*?)^\s*```\s*$', text, re.M | re.S):
        try:
            value = json.loads(block, object_pairs_hook=unique)
        except ValueError as exc:
            if 'plan_items_version' in block:
                raise MigrationError('Malformed plan projection: ' + str(path)) from exc
            continue
        if isinstance(value, dict) and 'plan_items_version' in value:
            candidates.append(value)
    if len(candidates) != 1:
        raise MigrationError('Each plan needs one version 2 plan_items projection: ' + str(path))
    rows = validate(candidates[0], 'planItems')['items']
    body = _plain(text)
    relative = path.relative_to(project).as_posix()
    declarations, headings = {}, _sections(body)
    for table in _tables(body):
        if table['headers'] != ['字段', '值']:
            continue
        declaration = {}
        for row in table['rows']:
            if len(row) != 2 or row[0] in declaration:
                raise MigrationError('Responsibility table needs unique field/value rows: ' + relative)
            try:
                declaration[row[0]] = json.loads(row[1], object_pairs_hook=unique)
            except ValueError as exc:
                raise MigrationError('Responsibility table values must be JSON literals: ' + relative) from exc
        validate(declaration, 'planItem')
        ident = declaration['item_id']
        prior = [heading for heading in headings if heading['line'] < table['line']]
        if not prior or ident not in prior[-1]['title']:
            raise MigrationError('Responsibility table needs its own full item_id heading: ' + ident)
        heading = prior[-1]['title']
        if ident in declarations or sum(section['title'] == heading for section in headings) != 1:
            raise MigrationError('Responsibility item or exact heading is duplicated: ' + ident)
        declarations[ident] = (declaration, heading)
    if set(declarations) != {item['item_id'] for item in rows}:
        raise MigrationError('Markdown responsibility tables and aggregate projection have different item sets: ' + relative)
    items = []
    for item in rows:
        ident = item['item_id']
        declaration, heading = declarations[ident]
        if declaration != item:
            raise MigrationError('Markdown responsibility fields differ from aggregate plan projection: ' + ident)
        for output in item['ownership']:
            safe_child(project, output)
            if any(ch in output for ch in '*?['):
                raise MigrationError('Plan ownership needs exact paths: ' + ident)
        if ident.startswith('UI:') and item['page_ids'] != ['page_' + ident.rsplit('-', 1)[1]]:
            raise MigrationError('UI item identity and page_ids differ: ' + ident)
        if ident.startswith('SLICE:') and any(not ac.startswith(ident.split(':')[1] + '-AC') for ac in item['ac_ids']):
            raise MigrationError('Slice item AC ownership differs from its F-ID: ' + ident)
        if ident.startswith('SLICE:'):
            file_fid = re.search(r'-(F\d+)\.md$', path.name, re.I)
            if not file_fid or file_fid[1].upper() != ident.split(':')[1]:
                raise MigrationError('Slice item F-ID differs from its indexed file: ' + ident)
        metadata = {}
        if ident.startswith('UI:'):
            matches = []
            for table in _tables(body):
                if 'item_id' not in table['headers']:
                    continue
                for row in table['rows']:
                    values = dict(zip(table['headers'], row))
                    if values.get('item_id') in {ident, ident.split(':', 1)[1]}:
                        matches.append(values)
            if len(matches) != 1:
                raise MigrationError('UI responsibility item needs one overview table row: ' + ident)
            overview = matches[0]
            targets = [value for key, value in overview.items() if key in {'目标文件', 'ownership', 'owned_files'}]
            try:
                overview_ac = json.loads(overview['ac_ids'])
            except (KeyError, ValueError) as exc:
                raise MigrationError('UI overview ac_ids must be a JSON array: ' + ident) from exc
            if targets != item['ownership'] or overview_ac != item['ac_ids']:
                raise MigrationError('UI overview target/AC differs from its responsibility table: ' + ident)
            metadata['owning_slice'] = overview.get('owning_slice', '')
        items.append({**item, **metadata, 'path': relative, 'heading': heading, 'sha256': digest(path.read_bytes())})
    return items


def _inventory(project):
    from .spec_contract import acceptance
    base = project / 'spec/baseline'
    features, pages = {}, {}
    for path in sorted((base / 'features').glob('F*.md')):
        for ac, _ in acceptance(path.read_text(encoding='utf-8-sig')):
            if ac in features:
                raise MigrationError('Duplicate AC: ' + ac)
            features[ac] = path
    for path in sorted((base / 'ui').glob('page_*.md')):
        match = re.match(r'(page_\d{4})(?:_|\.|$)', path.name)
        if match:
            if match[1] in pages:
                raise MigrationError('Duplicate page spec: ' + match[1])
            pages[match[1]] = path
    from .ios_harness import responsibility
    projection = responsibility(project)
    if projection is not None:
        features = {ident: path for ident, path in features.items() if ident in projection.target_acceptance_ids}
    return features, pages


def _table_rows(path, *, artifact):
    rows = []
    tables = _core_index_tables(path.read_text(encoding='utf-8-sig'), artifact)
    if len(tables) != 1:
        raise MigrationError('Missing catalog core index table: ' + artifact)
    for _, table in tables:
        for row in table['rows']:
            if len(row) != len(table['headers']):
                raise MigrationError('Malformed catalog core index row: ' + artifact)
            rows.append(dict(zip(table['headers'], row)))
    return rows


def _feature_rows(project):
    result = {}
    artifact = 'spec/baseline/feature-index.md'
    for row in _table_rows(project / artifact, artifact=artifact):
        ident = row.get('ID', row.get('id', '')).strip('` ')
        if re.fullmatch(r'F\d+', ident) and row.get('状态', row.get('status', '')) not in {'skipped', 'excluded'}:
            if ident in result:
                raise MigrationError('Duplicate active feature-index row: ' + ident)
            result[ident] = row
    return result


def _manifest_target(project, row, page):
    """The catalog cell is one .ets path, optionally followed by / Component."""
    cell = row['ArkTS 目标文件/组件'].replace('`', '').strip()
    match = re.fullmatch(r'(.+?\.ets)(?:[ \t]+/[ \t]+([A-Za-z_$][\w$]*))?', cell)
    if not match or match[1].count('.ets') != 1:
        raise MigrationError('UI manifest needs one unambiguous target file/component: ' + page)
    path = match[1]
    safe_child(project, path)
    return path


def _contract_dependencies(project, row):
    """Read the actual index protocol: exact path#heading, with F-ID compatibility."""
    from .spec_contract import references
    raw = row.get('契约依赖', '').strip()
    if not raw or re.match(r'^(?:none|无|N/A|not_applicable|不适用)(?:$|\s*[:：])', raw, re.I):
        return set(), []
    if raw.startswith('['):
        try:
            entries = json.loads(raw)
        except ValueError as exc:
            raise MigrationError('Index contract dependency array must be JSON strings') from exc
        _strings(entries, 'feature-index:契约依赖')
    else:
        entries = [value.strip('` ') for value in re.split(r'<br\s*/?>|[;；\n]|,\s*(?=`?(?:spec/|F\d+))', raw)]
    fids, refs = set(), []
    for entry in entries:
        if re.fullmatch(r'F\d+', entry):
            fids.add(entry)
        else:
            refs.append(entry)
    resolved = references(project, project / 'spec/baseline/feature-index.md', 'contract_refs: ' + json.dumps(refs))
    return fids, resolved


def indexed_contract_inputs(project):
    """Freeze index-only exact contracts even when no feature repeats the link."""
    from .spec_contract import references
    project = Path(project).resolve()
    pending = [target for row in _feature_rows(project).values() for target, _, _ in _contract_dependencies(project, row)[1]]
    seen, hashes = set(), {}
    while pending:
        path = pending.pop()
        if path in seen:
            continue
        seen.add(path)
        hashes[path.relative_to(project).as_posix()] = digest(path.read_bytes())
        pending.extend(target for target, _, _ in references(project, path, path.read_text(encoding='utf-8-sig')))
    return hashes


def _indexed_links(project, index, detail_paths):
    text = _plain(index.read_text(encoding='utf-8-sig'))
    links = re.findall(r'^\s*(?:-\s*)?detail:\s*`?([^`\s]+)`?\s*$', text, re.M)
    normalized = []
    for link in links:
        relative = link if link.startswith('spec/baseline/') else 'spec/baseline/' + link
        target = safe_child(project, relative)
        if not target.is_file():
            raise MigrationError('Indexed plan detail points to a missing file: ' + link)
        normalized.append(relative.casefold())
    expected = {p.relative_to(project).as_posix().casefold() for p in detail_paths}
    if len(set(normalized)) != len(normalized) or set(normalized) != expected:
        raise MigrationError('Indexed plan detail pointers and Base/Slice files must correspond one to one')


def task_inputs(project, task, items=None):
    """Exact headings + file hashes, transitively from owned ACs/pages/contracts."""
    from .spec_contract import references
    project = Path(project).resolve()
    features, pages = _inventory(project)
    seeds = {features[ac] for ac in task.get('ac_ids', []) if ac in features}
    # Contract dependencies require reading, not serialization. Follow their
    # feature contracts transitively without inventing task parents.
    index = _feature_rows(project)
    pending_features = [ac.split('-AC', 1)[0] for ac in task.get('ac_ids', [])]
    read_features, explicit_contracts = set(), []
    while pending_features:
        fid = pending_features.pop()
        if fid in read_features:
            continue
        read_features.add(fid)
        dependencies, shared = _contract_dependencies(project, index.get(fid, {}))
        explicit_contracts.extend((target, heading) for target, heading, _ in shared)
        for dependency in dependencies:
            seeds.update(path for ac, path in features.items() if ac.startswith(dependency + '-AC'))
        pending_features.extend(dependencies - read_features)
    seeds.update(path for path in (project / 'spec/baseline/feature-base.md', project / 'spec/baseline/skip-list.md',
                                   project / 'spec/decision-ledger.md') if path.is_file())
    plan_seeds = []
    for item in items or []:
        plan_seeds.append((safe_child(project, item['path']), item['heading']))
        seeds.update(pages[page] for page in item['page_ids'] if page in pages)
    # Also discover consuming pages when an AC-bearing task maps no UI item.
    for path in pages.values():
        text = path.read_text(encoding='utf-8-sig')
        if set(re.findall(r'F\d+-AC\d+', text)) & set(task.get('ac_ids', [])):
            seeds.add(path)
    pending = [(path, None) for path in seeds] + plan_seeds + explicit_contracts
    seen, consumed = set(), {}
    while pending:
        path, exact = pending.pop()
        text = path.read_text(encoding='utf-8-sig')
        relative = path.relative_to(project).as_posix()
        headings = [exact] if exact else [s['title'] for s in _sections(text)]
        if not headings:
            raise MigrationError('Consumed Markdown needs an exact heading: ' + relative)
        for heading in headings:
            consumed[(relative, heading)] = {'path': relative, 'heading': heading, 'sha256': digest(path.read_bytes())}
        if path in seen:
            continue
        seen.add(path)
        for target, heading, _ in references(project, path, text):
            pending.append((target, heading))
    return [consumed[key] for key in sorted(consumed)]


def plan_units(project):
    """Load the same bounded indexed responsibility authority used by validate_plan."""
    project = Path(project).resolve()
    from .artifact_contract import catalog
    projections = {}
    for artifact in catalog()['plan']['artifacts']:
        if artifact.get('check') != 'correspondence':
            continue
        matches = ([safe_child(project, artifact['path'])] if 'path' in artifact
                   else sorted(project.glob(artifact['glob'])))
        matches = [path for path in matches if path.is_file()]
        if artifact.get('required') and not matches:
            raise MigrationError('Missing required plan artifact: ' + artifact.get('path', artifact.get('glob', '')))
        for path in matches:
            if path in projections:
                raise MigrationError('Plan artifact has multiple projection definitions: ' + str(path))
            projections[path] = artifact['projection'] + ':'
    indexes = [path for path, prefix in projections.items() if prefix == 'FV:']
    if len(indexes) != 1:
        raise MigrationError('Catalog must identify one indexed feature plan')
    index = indexes[0]
    if not re.search(r'plan_format:\s*indexed-v1\b', index.read_text(encoding='utf-8-sig')):
        raise MigrationError('feature-plan must retain indexed-v1 layout')
    _indexed_links(project, index, [path for path, prefix in projections.items() if prefix in {'BASE:', 'SLICE:'}])
    units = {}
    for path, expected in projections.items():
        for item in _projection(project, path):
            ident = item['item_id']
            if not ident.startswith(expected) or ident in units:
                raise MigrationError('Duplicate or misplaced plan item: ' + ident)
            units[ident] = item
    return projections, units


def validate_plan(project, request):
    """Return a read-only PASS report or raise MigrationError before state writes."""
    project = Path(project).resolve()
    from .harness_schema import validate
    validate(request, 'planRequest')
    version = profile(project)
    result = {'status': 'PASS', 'spec_contract_version': version, 'task_inputs': {}, 'behavior_verified': False}
    if version < 2 or request.get('wave') != 'domains':
        return result
    projections, units = plan_units(project)
    active = {ident: item for ident, item in units.items() if item['scope'] == 'product'}
    for ident in ('FV:FV-1', 'FV:FV-2'):
        if ident not in active or active[ident]['verification'] != 'compile' or active[ident]['ownership']:
            raise MigrationError('Final structural check and final compilation require read-only compile obligations: ' + ident)
    if 'FV:FV-1' not in active['FV:FV-2']['parents']:
        raise MigrationError('Final compilation must follow the final structural check')
    features, pages = _inventory(project)
    for ident, item in active.items():
        if set(item['ac_ids']) - features.keys() or set(item['page_ids']) - pages.keys():
            raise MigrationError('Plan references unknown or excluded AC/page: ' + ident)
        if set(item['parents']) - active.keys():
            raise MigrationError('Plan dependency references unknown/excluded item: ' + ident)
        if ident.startswith(('UI:', 'SLICE:')) and not item['ac_ids']:
            raise MigrationError('Product UI/Slice items must bind acceptance criteria: ' + ident)
    artifact = 'spec/baseline/ui-manifest.md'
    manifest = _table_rows(project / artifact, artifact=artifact)
    manifest_pages = set()
    for row in manifest:
        page = row.get('page_id', '').strip('` ')
        if not re.fullmatch(r'page_\d{4}', page):
            continue
        excluded = row.get('状态', row.get('status', '')) in {'skipped', 'excluded'}
        matches = [item for ident, item in active.items() if ident.startswith('UI:') and page in item['page_ids']]
        if excluded and matches or not excluded and len(matches) != 1:
            raise MigrationError('UI plan and manifest page scope/owner differ: ' + page)
        if not excluded:
            manifest_pages.add(page)
            if _manifest_target(project, row, page) not in matches[0]['ownership']:
                raise MigrationError('UI plan ownership differs from manifest target: ' + page)
    ui_pages = {page for ident, item in active.items() if ident.startswith('UI:') for page in item['page_ids']}
    if ui_pages != manifest_pages:
        raise MigrationError('UI plan page set differs from manifest')
    feature_rows = _feature_rows(project)
    if {ident.split(':')[1] for ident in active if ident.startswith('SLICE:')} != set(feature_rows):
        raise MigrationError('Slice plan feature set differs from feature-index active scope')
    creators = defaultdict(set)
    for fid, row in feature_rows.items():
        for page in re.findall(r'page_\d{4}', row.get('创建页面', '')):
            creators[page].add(fid)
        contract_fids, _ = _contract_dependencies(project, row)
        if (set(re.findall(r'F\d+', row.get('排序依赖', ''))) | contract_fids) - feature_rows.keys():
            raise MigrationError('Feature index dependency references unknown/excluded feature: ' + fid)
        associated = row.get('关联页面', row.get('关联页面（不声明创建）', ''))
        expected_pages = set() if re.match(r'^(?:N/A|not_applicable|不适用)(?:$|\s*[:：])', associated, re.I) else set(re.findall(r'page_\d{4}', associated))
        slice_pages = {page for ident, item in active.items() if ident.startswith('SLICE:' + fid + ':') for page in item['page_ids']}
        if slice_pages != expected_pages or expected_pages - manifest_pages:
            raise MigrationError('Slice page_ids differ from feature-index associated pages: ' + fid)
    for ident, item in active.items():
        if ident.startswith('UI:'):
            page = item['page_ids'][0]
            if len(creators[page]) != 1 or item['owning_slice'] not in creators[page]:
                raise MigrationError('UI owning_slice differs from the unique feature-index page creator: ' + page)
    unit_ancestors = {}
    def unit_parents(ident, visiting=()):
        if ident in visiting:
            raise MigrationError('Markdown plan dependency cycle')
        if ident not in unit_ancestors:
            unit_ancestors[ident] = set(active[ident]['parents'])
            for parent in active[ident]['parents']:
                unit_ancestors[ident].update(unit_parents(parent, (*visiting, ident)))
        return unit_ancestors[ident]
    for ident in active:
        unit_parents(ident)
    for fid, row in feature_rows.items():
        prerequisites = set(re.findall(r'F\d+', row.get('排序依赖', '')))
        needed = {ident for ident in active if ident.startswith('SLICE:') and ident.split(':')[1] in prerequisites}
        if re.search(r'\bbase\b', row.get('排序依赖', ''), re.I):
            needed.update(ident for ident in active if ident.startswith('BASE:'))
        for ident in active:
            if ident.startswith('SLICE:' + fid + ':') and needed - unit_ancestors[ident]:
                raise MigrationError('Slice plan dropped feature-index ordering dependency: ' + ident)
    tasks = request.get('tasks', [])
    by_task = {task['id']: task for task in tasks}
    if len(by_task) != len(tasks):
        raise MigrationError('Duplicate task IDs')
    mapped, refs_by_task = defaultdict(list), {}
    owned_files = set()
    for task in tasks:
        ident = task['id']
        refs = _strings(task.get('plan_item_refs'), ident + ':plan_item_refs')
        if not refs or refs - active.keys():
            raise MigrationError('Task maps missing/excluded Markdown plan items: ' + ident)
        if 'parents' not in task or set(_strings(task['parents'], ident + ':parents')) - by_task.keys():
            raise MigrationError('Task parents must be explicit and known: ' + ident)
        refs_by_task[ident] = refs
        for ref in refs:
            mapped[ref].append(task)
        expected_ac = {a for ref in refs for a in active[ref]['ac_ids']}
        expected_own = {p for ref in refs for p in active[ref]['ownership']}
        if _strings(task['ac_ids'], ident + ':ac_ids') - expected_ac or _strings(task['ownership'], ident + ':ownership') - expected_own:
            raise MigrationError('Task AC/ownership exceeds mapped Markdown plan: ' + ident)
        highest = max((active[ref]['verification'] for ref in refs), key=VERIFICATION_RANK.get)
        if task.get('verification') != highest:
            raise MigrationError('Task verification obligation differs from Markdown plan: ' + ident)
        if not task['ownership'] and highest == 'generated':
            raise MigrationError('Generation task needs actual owned outputs: ' + ident)
        for output in task['ownership']:
            if output.casefold() in owned_files:
                raise MigrationError('Tasks cannot share lifetime file ownership: ' + output)
            owned_files.add(output.casefold())
    if active.keys() - mapped.keys():
        raise MigrationError('Unmapped Markdown plan items: ' + ','.join(sorted(active.keys() - mapped.keys())))
    for ref, owners in mapped.items():
        item = active[ref]
        if {a for task in owners for a in task['ac_ids'] if a in item['ac_ids']} != set(item['ac_ids']):
            raise MigrationError('Split/merge omitted item acceptance: ' + ref)
        if {p for task in owners for p in task['ownership'] if p in item['ownership']} != set(item['ownership']):
            raise MigrationError('Split/merge omitted item ownership: ' + ref)
        if len(owners) > 1 or any(len(refs_by_task[task['id']]) > 1 for task in owners):
            if any(not isinstance(task.get('mapping_reason'), str) or not task['mapping_reason'].strip() for task in owners):
                raise MigrationError('Split/merge needs a concrete mapping_reason: ' + ref)
    ancestors = {}
    def parents(ident, visiting=()):
        if ident in visiting:
            raise MigrationError('Task dependency cycle')
        if ident not in ancestors:
            ancestors[ident] = set(by_task[ident]['parents'])
            for parent in by_task[ident]['parents']:
                ancestors[ident].update(parents(parent, (*visiting, ident)))
        return ancestors[ident]
    for ident, refs in refs_by_task.items():
        prior = parents(ident)
        for ref in refs:
            for dependency in active[ref]['parents']:
                if any(owner['id'] != ident and owner['id'] not in prior for owner in mapped[dependency]):
                    raise MigrationError('Typed task dropped Markdown dependency: ' + ident + ':' + dependency)
        if any(ref.startswith('FV:') for ref in refs):
            needed = {task['id'] for ref, owners in mapped.items() if not ref.startswith('FV:') for task in owners}
            if needed - prior - {ident}:
                raise MigrationError('Final verification must follow all product tasks: ' + ident)
        result['task_inputs'][ident] = task_inputs(project, by_task[ident], [active[ref] for ref in sorted(refs)])
    if {ac for item in active.values() for ac in item['ac_ids']} != set(features):
        raise MigrationError('Markdown plan omitted or added acceptance criteria')
    from .capability_contract import validate_declarations
    capabilities = validate_declarations(project, projections, units)
    if capabilities is not None:
        result['capability_declarations'] = capabilities
    result.update(contract_revision=contract_revision(project), plan_items=len(active), tasks=len(tasks))
    return result
