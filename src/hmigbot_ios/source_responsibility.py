"""One read-only, fail-closed projection of reviewed source responsibilities.

The original graph and obligation list are never edited. Source-private unknowns
remain unknown. A valid projection describes target obligations; it is neither a
source review generator, an approval authority, nor a runtime verification.
"""
from __future__ import annotations

import copy
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
import re
import tempfile

from .core import source_snapshot
from .core import MigrationError, digest, json_bytes, read_json, safe_child, snapshot

KINDS = ('dependency_internal', 'unused_symbol', 'test_target', 'replaced_source_history')


def _require(condition, detail):
    if not condition:
        raise MigrationError('Source responsibility: ' + detail)


def _shape(value, keys, label, *, optional=''):
    required, allowed = set(keys.split()), set((keys + ' ' + optional).split())
    _require(isinstance(value, dict) and required <= set(value) <= allowed, label + ' has invalid fields')
    return value


def _strings(value, label, *, empty=False):
    _require(isinstance(value, list) and (empty or value) and
             all(isinstance(i, str) and i.strip() for i in value) and len(set(value)) == len(value),
             label + ' must be a unique string list')
    return value


def _file(root, relative):
    _require(isinstance(relative, str) and not any(c in relative for c in '*?[]'), 'exact file path required')
    file = safe_child(root, relative)
    # safe_child resolves containment, while this also rejects in-root symlinks.
    cursor = Path(root)
    for part in Path(relative).parts:
        cursor /= part
        _require(not cursor.is_symlink(), 'symlinks cannot authorize a boundary')
    _require(file.is_file(), 'regular file required: ' + relative)
    return file


def _ref(project, relative, frozen):
    _require(relative.startswith(('spec/baseline/', 'spec/ref/')) or relative == 'spec/decision-ledger.md',
             'evidence must be a pinned project spec/ref or baseline file')
    file = _file(project, relative)
    frozen[relative] = digest(file.read_bytes())
    return file


def _section(project, ref, frozen):
    from .artifact_contract import markdown_sections
    _require(isinstance(ref, str) and '#' in ref, 'reference requires an exact heading')
    relative, heading = ref.split('#', 1)
    file = _ref(project, relative, frozen)
    sections = [s for s in markdown_sections(file.read_text(encoding='utf-8-sig')) if s['title'] == heading]
    _require(len(sections) == 1, 'reference heading must exist exactly once: ' + ref)
    return sections[0]['body']


def _upstream_root():
    return Path(__file__).resolve().parents[2]


def _acceptance_inputs(project):
    paths = sorted((project / 'spec/baseline/features').glob('F*.md'))
    ledger = project / 'spec/decision-ledger.md'
    if ledger.is_file():
        paths.append(ledger)
    return {p.relative_to(project).as_posix(): digest(p.read_bytes()) for p in paths}


@lru_cache(maxsize=32)
def _original_inventory(project_string, fingerprints, helper_fingerprints):
    """Recompute with the original parser, never a parallel supersedes grammar."""
    from .portable_helper import run
    project, root = Path(project_string), _upstream_root()
    scripts = root / 'skills/a2h-spec/scripts'
    with tempfile.TemporaryDirectory(prefix='source-responsibility-index-') as tmp:
        output = Path(tmp) / 'requirements.json'
        for helper, args in [
            ('lint_divergence.py', ['--spec-dir', str(project / 'spec/baseline/features'),
                                    '--ledger', str(project / 'spec/decision-ledger.md'), '--gate']),
            ('build_traceability_index.py', ['--project-root', str(project), '--out', str(output)])]:
            result = run(scripts / helper, args, capture_output=True, text=True, timeout=120, project_root=project)
            _require(result.returncode == 0, 'original traceability closure failed: ' + (result.stdout + result.stderr)[-4000:])
        data = read_json(output)
    rows = data.get('requirements')
    _require(isinstance(rows, list) and rows, 'original traceability produced no criteria')
    ids = [r.get('requirement_id') for r in rows]
    _require(all(isinstance(i, str) for i in ids) and len(set(ids)) == len(ids), 'original traceability has duplicate criteria')
    _require(not data.get('_meta', {}).get('duplicate_ids'), 'original traceability has duplicate criteria')
    result = {'all': {r['requirement_id']: r for r in rows}, 'active_target': {}, 'source_history': {}}
    for row in rows:
        status = row.get('status')
        _require(status in ('active', 'superseded'), 'unsupported original AC status')
        result['active_target' if status == 'active' else 'source_history'][row['requirement_id']] = row
    return result


def acceptance_inventory(project, scope=None):
    """Original freshly content-keyed all/active_target/source_history inventory.

    Only helper output written to a temporary directory is consumed. The existing
    project requirements-index.json, including edited statuses, is never read.
    """
    project = Path(project).resolve()
    helper_hashes = tuple(sorted(parser_fingerprints().items()))
    result = copy.deepcopy(_original_inventory(str(project), tuple(sorted(_acceptance_inputs(project).items())), helper_hashes))
    _require(scope is None or scope in result, 'unknown acceptance inventory scope')
    return result if scope is None else result[scope]


def parser_fingerprints():
    """Actual original parser payloads belong to both cache and tool freeze."""
    root = _upstream_root()
    scripts = root / 'vendor/hmigbot/skills/a2h-spec/scripts'
    return {p.relative_to(root).as_posix(): digest(p.read_bytes()) for p in [*scripts.rglob('*'), *(root / 'skills/a2h-spec/scripts').glob('*.py')]
            if p.is_file() and p.name in ('build_traceability_index.py', 'lint_divergence.py', '_entry.bin', '_entry.exe')}


@dataclass(frozen=True)
class Projection:
    all_obligation_ids: tuple
    product_obligation_ids: tuple
    historical_obligation_ids: tuple
    treatments: dict
    acceptance: dict
    variant: dict
    counts: dict
    _frozen: dict
    _semantic: dict
    behavior_verified: bool = False
    enabled: bool = False
    candidate: bool = False
    historical_action_ids: tuple = ()
    target_action_ids: tuple = ()

    def frozen_inputs(self):
        return copy.deepcopy(self._frozen)

    def validate_frozen_inputs(self, project):
        for relative, expected in self._frozen.items():
            _require(digest(_file(project, relative).read_bytes()) == expected, 'frozen input changed: ' + relative)

    @property
    def target_acceptance_ids(self):
        return tuple(self.acceptance['active_target' if self.enabled else 'all'])

    def validate_target_ownership(self, ac_ids, obligation_ids):
        _require(set(self.target_acceptance_ids) <= set(ac_ids), 'active target acceptance ownership missing')
        _require(set(self.product_obligation_ids) <= set(obligation_ids), 'product obligation ownership missing')

    def semantic_requirement(self, document_id, dimension, claim):
        record = self._semantic.get((document_id, dimension))
        if record is None:
            return {'target_required': True, 'source_status': claim.get('status'),
                    'retained_parts': [], 'requires_ordinary_validation': True}
        _require(digest(json_bytes(claim)) == record['claim_sha256'], 'semantic claim changed after projection')
        return {'target_required': False, 'source_status': 'unknown',
                'retained_parts': copy.deepcopy(record['retained_parts']),
                'requires_ordinary_validation': bool(record['retained_parts']),
                'private_parts': copy.deepcopy(record['private_parts']), 'replacement_id': record['replacement_id']}


def _context(project, source, payload, graph, frozen):
    from .conditional_evidence import _build, validate, frozen_inputs
    ctx = _shape(payload, 'expected_build build_evidence conditional_evidence', 'product_context')
    build = _ref(project, ctx['build_evidence'] + '/manifest.json', frozen).parent
    conditional = _ref(project, ctx['conditional_evidence'] + '/manifest.json', frozen).parent
    _require(ctx['conditional_evidence'].startswith('spec/ref/ios-conditional-evidence/'), 'conditional capture must be pinned')
    original = _build(source, build, ctx['expected_build'])
    observed = validate(source, conditional, project=project)
    _require(original['expected_build'] == observed['expected_build'] == ctx['expected_build'] and
             original['members'] == observed['members'], 'build/conditional identity or membership differs')
    if graph.get('variant', {}).get('scope') == 'selected-build':
        variant = graph['variant']
        _require(variant.get('expected_build') == ctx['expected_build'] and
                 variant.get('source_files') == original['members'] and
                 Path(variant.get('evidence_path', '')).resolve() == build and
                 Path(variant.get('conditional_evidence', '')).resolve() == conditional,
                 'graph variant differs from responsibility build')
    frozen.update(frozen_inputs(project, {'conditional_evidence': observed.get('reference', {'path': str(conditional)})}))
    return set(original['members'])


def _source_span(source, item, indexed):
    _shape(item, 'path line end_line symbol source_sha256', 'source span')
    path = item['path']
    _require(path in indexed, 'span is outside the current source snapshot')
    file = _file(source, path); raw = file.read_bytes()
    _require(digest(raw) == item['source_sha256'], 'source span file hash is stale')
    _require(type(item['line']) is int and type(item['end_line']) is int and
             1 <= item['line'] <= item['end_line'], 'invalid source span range')
    _require(isinstance(item['symbol'], str) and item['symbol'].strip(), 'exact symbol required')
    try:
        lines = raw.decode('utf-8-sig').splitlines()
    except UnicodeError:
        _require(file.suffix == '.plist' and item['symbol'] == '<resource>' and item['line'] == item['end_line'] == 1,
                 'binary boundary requires an exact plist resource anchor')
        import plistlib
        try:
            plistlib.loads(raw)
        except Exception as exc:
            raise MigrationError('Source responsibility: invalid plist boundary') from exc
        return
    _require(item['end_line'] <= len(lines), 'source span exceeds current line range')
    _require(item['symbol'] == '<resource>' or item['symbol'] in '\n'.join(lines[item['line']-1:item['end_line']]),
             'reviewed symbol is absent from its declared span')


def _inside(anchor, span):
    return (anchor['path'] == span['path'] and anchor['file_sha256'] == span['source_sha256'] and
            span['line'] <= anchor['line'] <= anchor['end_line'] <= span['end_line'])


def _review(project, source, payload, graph, indexed, frozen):
    ref = _shape(payload, 'path sha256', 'review reference')
    path = _ref(project, ref['path'], frozen)
    _require(digest(path.read_bytes()) == ref['sha256'], 'independent source review changed')
    review = _shape(read_json(path), 'schema_version mode source_sha256 graph_sha256 reviewer independent_reviewer input processing observable file_roles routes unresolved', 'source review')
    _require(review['schema_version'] == 1 and review['mode'] == 'independent_source_review', 'generated/pending review cannot authorize scope')
    _require(review['source_sha256'] == graph['source_sha256'] and review['graph_sha256'] == digest(json_bytes(graph)), 'review source or graph is stale')
    for key in ('reviewer', 'independent_reviewer', 'input', 'processing', 'observable'):
        _require(isinstance(review[key], str) and review[key].strip(), 'source review requires ' + key)
    _require(review['reviewer'] != review['independent_reviewer'], 'source review requires an independent reviewer')
    _require(review['unresolved'] == [], 'unresolved entry/call/dynamic routes remain blocking')
    roles = {}
    _require(isinstance(review['file_roles'], list), 'file roles must be a list')
    for row in review['file_roles']:
        _shape(row, 'path source_sha256 role package', 'file role')
        _require(row['path'] in indexed and row['path'] not in roles and
                 row['role'] in ('application', 'dependency', 'test', 'resource', 'configuration') and
                 isinstance(row['package'], str) and row['package'].strip(), 'invalid exact file role')
        _require(digest(_file(source, row['path']).read_bytes()) == row['source_sha256'], 'file role hash changed')
        roles[row['path']] = row['role']
    _require(set(roles) == set(indexed), 'review must classify every indexed file explicitly')
    facts = {f['id']: f for f in graph['facts']}
    routes = {}
    _require(isinstance(review['routes'], list), 'reviewed route inventory required')
    for row in review['routes']:
        _shape(row, 'fact_id resolution boundary_ids evidence', 'reviewed route')
        ident = row['fact_id']
        _require(ident in facts and ident not in routes, 'unknown/duplicate route fact')
        _require(row['resolution'] in ('product_entry', 'no_entry', 'dependency_boundary', 'outside_selected_target'), 'unresolved route resolution')
        _strings(row['boundary_ids'], 'route boundary IDs', empty=True)
        _require(isinstance(row['evidence'], list) and row['evidence'] and
                 all(e == facts[ident]['anchor'] for e in row['evidence']), 'route needs the current exact machine source anchor')
        routes[ident] = row
    # Every machine fact is reviewed, including delegates/lifecycle/state, rather
    # than assuming lack of a text match proves no indirect or dynamic entry.
    _require(set(routes) == set(facts), 'entry/call review must account for every current fact')
    return roles, routes, {review['reviewer'], review['independent_reviewer']}



def _has_selector_call(tokens, selectors, *, arity):
    """Conservative call-shape signal; never resolve receiver types or reachability."""
    values = [t.value for t in tokens if t.kind != 'string']
    for index, value in enumerate(values):
        # Swift/member-style source calls; method declarations lack the dot.
        if (value == selectors[0] and index > 0 and values[index-1] == '.' and
                index + 1 < len(values) and values[index+1] == '('):
            return len(selectors) == 1
        if value != '[':
            continue
        depth, end = 1, index + 1
        while end < len(values) and depth:
            depth += (values[end] == '[') - (values[end] == ']')
            end += 1
        if depth:
            continue
        body = values[index+1:end-1]
        if not body:
            continue
        # Recognize simple identifiers/dotted receivers and nested messages.
        cursor = 1
        if body[0] == '[':
            depth = 1
            while cursor < len(body) and depth:
                depth += (body[cursor] == '[') - (body[cursor] == ']')
                cursor += 1
            if depth:
                continue
        elif not re.fullmatch(r'[A-Za-z_]\w*', body[0]):
            continue
        else:
            while cursor + 1 < len(body) and body[cursor] == '.' and re.fullmatch(r'[A-Za-z_]\w*', body[cursor+1]):
                cursor += 2
        if cursor >= len(body) or body[cursor] != selectors[0]:
            continue
        if cursor + 1 == len(body):
            if arity == 0 and len(selectors) == 1:
                return True
            continue
        if body[cursor+1] != ':':
            continue
        if arity == 0:
            continue
        # The leading selector is a real message signal; require the other
        # explicitly named selector pieces to exist at this same message depth.
        labels, depth = [], 0
        for offset in range(cursor, len(body)-1):
            depth += (body[offset] in ('[', '(', '{')) - (body[offset] in (']', ')', '}'))
            if depth == 0 and body[offset+1] == ':' and re.fullmatch(r'[A-Za-z_]\w*', body[offset]):
                labels.append(body[offset])
        if labels == selectors and len(labels) == arity:
            return True
    return False

def _actions(project):
    from .artifact_contract import json_blocks, _json, validate_json
    actions = {}
    for path in sorted((project / 'spec/baseline/features').glob('F*.md')):
        for block in json_blocks(path.read_text(encoding='utf-8-sig')):
            if block['kind'] != 'action-contract':
                continue
            row = _json(block['body']); validate_json(row, 'action_contract')
            _require(row['action_id'] not in actions, 'duplicate action definition')
            actions[row['action_id']] = row
    return actions



def _objc_method_region(source, span, source_anchor, truth_line):
    """Resolve the original parsed AC symbol using the existing closed ObjC parser."""
    from .objc_state import _methods
    from .swiftui import tokenize
    _require(isinstance(source_anchor, str) and '.' in source_anchor, 'historical app AC needs an original Owner.selector source anchor')
    wanted_owner, selector = source_anchor.split('.', 1)
    _require(span['symbol'] in (selector, selector.split(':')[0]), 'application span symbol differs from original historical AC')
    tokens = tokenize(_file(source, span['path']).read_text(encoding='utf-8-sig'), skip_pragma_marks=Path(span['path']).suffix != '.swift')
    owner, implementation, found, i = None, False, [], 0
    while i < len(tokens):
        value = tokens[i].value
        if value == '@' and i + 1 < len(tokens):
            directive = tokens[i+1].value
            if directive in ('implementation', 'interface') and i + 2 < len(tokens):
                owner, implementation = tokens[i+2].value, directive == 'implementation'
            elif directive == 'end':
                owner, implementation = None, False
        if implementation and value in ('-', '+') and i + 1 < len(tokens) and tokens[i+1].value == '(':
            parsed = _methods(tokens, i)
            _require(parsed is not None, 'cannot replay Objective-C source symbol region')
            method_selector, _, body, end = parsed
            if (body is not None and owner == wanted_owner and method_selector == selector and
                    tokens[i].line <= span['line'] <= truth_line <= span['end_line'] <= tokens[end-1].line):
                found.append((tokens[i].line, tokens[end-1].line))
            i = end
            continue
        i += 1
    _require(len(found) == 1, 'application replacement span must belong wholly to the original historical AC method')


def _application_bindings(source, boundary, replacement, facts, roles, reviewers, inventory):
    """Exact original source AC + per-obligation reviewed replacement for app spans."""
    app_spans = [s for s in boundary['sources'] if roles[s['path']] == 'application']
    bindings = boundary.get('source_ac_bindings', [])
    _require(isinstance(bindings, list), 'source_ac_bindings must be a list')
    if not app_spans:
        _require(not bindings, 'app source bindings cannot classify dependency internals')
        return
    _require(bindings, 'replaced application spans require exact original source AC bindings')
    app_facts = {f for f in boundary['fact_ids'] if roles[facts[f]['anchor']['path']] == 'application'}
    app_obligations = {'IO-' + f[3:]: f for f in app_facts}
    seen, used_spans = set(), []
    for binding in bindings:
        _shape(binding, 'source_ac_id source_ac_sha256 source_span obligation_ids source_reviews', 'application source AC binding')
        ident = binding['source_ac_id']
        _require(ident in replacement['superseded_ac_ids'] and ident in inventory['source_history'], 'app binding needs exact superseded source AC')
        original = inventory['source_history'][ident]
        _require(original['superseded_by'] == replacement['decision_id'] and
                 digest(json_bytes(original)) == binding['source_ac_sha256'], 'original historical AC changed or belongs to another decision')
        span = binding['source_span']
        _require(span in app_spans, 'app binding must use an exact declared source span')
        truth = re.fullmatch(r'src:([^:\n]+):(\d+)', original.get('truth_source') or '')
        _require(truth is not None and truth[1] == span['path'] and span['line'] <= int(truth[2]) <= span['end_line'],
                 'original source truth anchor is outside application replacement span')
        _objc_method_region(source, span, original.get('source_anchor'), int(truth[2]))
        used_spans.append(span)
        ids = _strings(binding['obligation_ids'], 'app binding obligation IDs')
        _require(set(ids) <= app_obligations.keys() and not seen.intersection(ids), 'app obligation must have exactly one original AC treatment')
        _require(all(_inside(facts[app_obligations[o]]['anchor'], span) for o in ids), 'app obligation is outside its exact source AC span')
        reviews = binding['source_reviews']
        _require(isinstance(reviews, list) and len(reviews) == len(ids), 'each app obligation needs an explicit source review')
        reviewed = set()
        for review in reviews:
            _shape(review, 'obligation_id fact_sha256 status input processing observable reviewer replacement_ac_ids', 'app obligation source review')
            obligation = review['obligation_id']
            _require(obligation in ids and obligation not in reviewed and review['status'] == 'reviewed' and
                     review['reviewer'] in reviewers, 'app source review must be current and independently attributed')
            _require(digest(json_bytes(facts[app_obligations[obligation]])) == review['fact_sha256'], 'app source review fact changed')
            _require(all(isinstance(review[k], str) and review[k].strip() for k in ('input', 'processing', 'observable')), 'app source review needs input, processing and observable outcome')
            targets = _strings(review['replacement_ac_ids'], 'app replacement responsibility AC IDs')
            _require(set(targets) <= set(replacement['replacement_ac_ids']) and
                     all(t in inventory['active_target'] and inventory['active_target'][t]['decision_ref'] == replacement['decision_id'] for t in targets),
                     'each app obligation needs active same-decision replacement responsibility')
            reviewed.add(obligation)
        _require(reviewed == set(ids), 'app source review is incomplete')
        seen.update(ids)
    _require(seen == set(app_obligations) and all(span in used_spans for span in app_spans),
             'unreviewed or mixed application behavior remains product-required')

def _replace(project, source, rows, graph, semantics, boundaries, facts, roles, reviewers, inventory, frozen):
    from .ios_facts import RULES
    from .artifact_contract import _visible_lines
    from .native_pipeline import source_paths
    actions = _actions(project)
    projections, used_boundaries, ids, projected_actions = {}, set(), set(), set()
    docs = {d['id']: d for d in (semantics or {}).get('documents', [])}
    _require(isinstance(rows, list), 'replacements must be a list')
    for row in rows:
        _shape(row, 'id decision_id decision_ref decision_sha256 boundary_ids superseded_ac_ids replacement_ac_ids historical_action_ids target_action_ids semantic_parts', 'replacement')
        _require(isinstance(row['id'], str) and row['id'] not in ids, 'duplicate replacement ID'); ids.add(row['id'])
        decision = row['decision_id']
        _require(isinstance(decision, str) and decision.strip(), 'decision ID required')
        body = _section(project, row['decision_ref'], frozen)
        path, heading = row['decision_ref'].split('#', 1)
        _require(path == 'spec/decision-ledger.md' and heading.split()[0] == decision and
                 digest((project / path).read_bytes()) == row['decision_sha256'], 'decision identity/hash mismatch')
        # Approval belongs to the existing authored decision, never this payload.
        body = '\n'.join(line for _, line in _visible_lines(body))
        _require(re.search(r'(?im)^\s*-?\s*status\s*[:：]\s*approved(?:\b|[。\s])', body) and
                 re.search(r'(?m)^\s*-?\s*(?:授权|依据|authorization)\s*[:：]\s*\S+', body),
                 'replacement requires existing approved decision and authorization evidence')
        boundary_ids = _strings(row['boundary_ids'], 'replacement boundary IDs')
        _require(set(boundary_ids) <= boundaries.keys() and not used_boundaries.intersection(boundary_ids), 'replacement boundary missing or reused')
        _require(all(boundaries[b]['kind'] == 'replaced_source_history' for b in boundary_ids), 'replacement must use exact replaced-source boundaries')
        used_boundaries.update(boundary_ids)
        old = _strings(row['superseded_ac_ids'], 'superseded AC IDs')
        new = _strings(row['replacement_ac_ids'], 'replacement AC IDs')
        _require(all(a in inventory['source_history'] and inventory['source_history'][a]['superseded_by'] == decision for a in old), 'source AC not superseded by same decision')
        _require(all(a in inventory['active_target'] and inventory['active_target'][a]['decision_ref'] == decision for a in new), 'target AC must be active under same decision')
        for key, valid in [('historical_action_ids', set(old)), ('target_action_ids', set(new))]:
            for ident in _strings(row[key], key):
                _require(ident in actions and set(actions[ident]['ac_ids']), 'action does not belong to exact replacement AC closure')
                action_acs = set(actions[ident]['ac_ids'])
                if key == 'historical_action_ids':
                    _require(action_acs <= valid, 'historical action mixes active and historical acceptance')
                    spans = [s for b in boundary_ids for s in boundaries[b]['sources']]
                    for anchor in actions[ident]['source_anchors']:
                        region = {**anchor, 'end_line': anchor.get('end_line', anchor['line']),
                                  'file_sha256': digest(_file(source, anchor['path']).read_bytes())}
                        containing = [s for s in spans if _inside(region, s)]
                        _require(containing, 'historical action source is outside the exact replacement boundary')
                        matched = False
                        for ac in action_acs:
                            original = inventory['source_history'][ac]
                            truth = re.fullmatch(r'src:([^:\n]+):(\d+)', original.get('truth_source') or '')
                            selector = (original.get('source_anchor') or '').split('.')[-1]
                            if (truth and truth[1] == anchor['path'] and anchor.get('symbol') in (selector, selector.split(':')[0])
                                    and any(s['line'] <= int(truth[2]) <= s['end_line'] for s in containing)):
                                matched = True
                        _require(matched, 'historical action must retain the original source AC symbol and truth boundary')
                    _require(ident not in projected_actions, 'historical action projected twice'); projected_actions.add(ident)
                else:
                    # An application action may retain ordinary app behavior
                    # alongside an approved replacement (e.g. a HUD surrounding
                    # system preview). Those ACs remain active and source-based.
                    _require(action_acs <= inventory['active_target'].keys() and bool(action_acs & valid),
                             'target action requires active acceptance and an explicit replacement emit')
                    _require(all(inventory['active_target'][a].get('decision_ref') is None for a in action_acs - valid),
                             'additional target action ACs must retain ordinary application responsibility')
                    _require(actions[ident]['target'] in {inventory['active_target'][a]['target_anchor'] for a in action_acs & valid}, 'target action symbol differs from original active AC')
        for b in boundary_ids:
            _application_bindings(source, boundaries[b], row, facts, roles, reviewers, inventory)
        # Application history can be replaced, but it never becomes private SDK
        # unknown evidence. Surviving application unknowns still block normally.
        allowed_facts = {f for b in boundary_ids for f in boundaries[b]['fact_ids'] if roles[facts[f]['anchor']['path']] == 'dependency'}
        _require(isinstance(row['semantic_parts'], list), 'semantic_parts must be a list')
        for part in row['semantic_parts']:
            _shape(part, 'document_id dimension claim_sha256 private_part_ids retained_part_ids retained_app_ac_ids', 'semantic treatment')
            docid, dimension = part['document_id'], part['dimension']
            _require((docid, dimension) not in projections and docid in docs, 'semantic document missing or multiply projected')
            doc = docs[docid]; claim = doc['facts'].get(dimension)
            _require(isinstance(claim, dict) and claim.get('status') == 'unknown' and isinstance(claim.get('reason'), str) and claim['reason'].strip(), 'source private claim must remain unknown with original reason')
            _require(digest(json_bytes(claim)) == part['claim_sha256'], 'semantic claim changed since source review')
            components = claim.get('parts')
            _require(isinstance(components, list) and components, 'mixed unknown must be split into explicit source parts')
            partids = [c.get('id') for c in components]
            _require(all(isinstance(i, str) and i for i in partids) and len(set(partids)) == len(partids), 'semantic part IDs must be unique')
            private = _strings(part['private_part_ids'], 'private part IDs')
            retained = _strings(part['retained_part_ids'], 'retained part IDs', empty=True)
            _require(not set(private).intersection(retained) and set(private + retained) == set(partids), 'every semantic part must have exactly one treatment')
            _require(set(_strings(part['retained_app_ac_ids'], 'retained app AC IDs')) <= set(new), 'app contract must retain active replacement ACs')
            anchors = set()
            folder = 'ui' if doc.get('kind') == 'page' else 'features'
            for path in (project / 'spec/baseline' / folder).glob(docid + '*.md'):
                frozen[path.relative_to(project).as_posix()] = digest(path.read_bytes())
                anchors.update(source_paths(path.read_text(encoding='utf-8-sig')))
            relevant = {f['id'] for f in facts.values() if f['anchor']['path'] in anchors and dimension in RULES[f['kind']]['dimensions']}
            covered, seen_refs, retained_parts, private_parts = set(), set(), [], []
            for component in components:
                refs = set(_strings(component.get('fact_ids'), 'semantic part fact IDs'))
                _require(refs <= facts.keys() and not refs.intersection(seen_refs), 'semantic part facts unknown or overlapping')
                seen_refs.update(refs)
                covered.update(refs.intersection(relevant))
                if component['id'] in private:
                    _require(component.get('status') == 'unknown' and isinstance(component.get('reason'), str) and component['reason'].strip() and refs <= allowed_facts and all(facts[f]['anchor']['path'] in anchors for f in refs),
                             'private unknown includes app responsibility or lost source reason')
                    private_parts.append(copy.deepcopy(component))
                else:
                    _require(component.get('status') == 'known' and isinstance(component.get('value'), dict) and component['value'] and
                             isinstance(component.get('evidence'), list) and component['evidence'], 'surviving app parts need ordinary typed known claims')
                    _require(not refs.intersection(allowed_facts) and all(facts[f]['anchor']['path'] in anchors and roles[facts[f]['anchor']['path']] == 'application' for f in refs), 'retained known parts require document-owned app facts; private source cannot be relabeled known by replacement')
                    for e in component['evidence']:
                        _require(any(e.get('path') == facts[f]['anchor']['path'] and type(e.get('line')) is int and facts[f]['anchor']['line'] <= e['line'] <= facts[f]['anchor']['end_line'] for f in refs),
                                 'retained part evidence must intersect linked facts')
                    retained_parts.append(copy.deepcopy(component))
            _require(covered == relevant, 'mixed unknown omits source responsibilities')
            projections[(docid, dimension)] = {'claim_sha256':part['claim_sha256'], 'replacement_id':row['id'],
                                               'private_parts':private_parts, 'retained_parts':retained_parts}
    _require(used_boundaries == {b for b, v in boundaries.items() if v['kind'] == 'replaced_source_history'}, 'replaced boundary has no approved replacement')
    return projections


def load_and_validate(project, source, graph, obligations, *, semantics=None, candidate=None):
    """Validate one current reviewed payload; errors never reduce the denominator.

    Callers must obtain graph/obligations through ios_facts.validate_graph first.
    This function additionally checks snapshot, rule-derived obligations and all
    review bindings, and never writes the baseline, reports or scheduler ledgers.
    Candidate is explicit: a supplied dict replaces, rather than merges with, an
    existing baseline. Candidate-dependent hashes are returned for caller pinning.
    """
    from .ios_facts import obligations as derive_obligations
    project, source = Path(project).resolve(), Path(source).resolve()
    _require(graph.get('source_sha256') == source_snapshot(source)['sha256'], 'source snapshot is stale')
    _require(obligations == derive_obligations(graph), 'obligations are not the original machine-derived denominator')
    ids = [o['id'] for o in obligations['obligations']]
    _require(len(set(ids)) == len(ids), 'duplicate machine obligations')
    frozen = _acceptance_inputs(project)
    for relative in ('spec/baseline/ios-facts.json', 'spec/baseline/ios-obligations.json'):
        if (project / relative).is_file():
            frozen[relative] = digest((project / relative).read_bytes())
    inventory = acceptance_inventory(project)
    semantics_path = project / 'spec/baseline/ios-semantics.json'
    if semantics_path.is_file():
        frozen['spec/baseline/ios-semantics.json'] = digest(semantics_path.read_bytes())
        if semantics is None:
            semantics = read_json(semantics_path)
    path = project / 'spec/baseline/ios-responsibility.json'
    payload = candidate if candidate is not None else (read_json(path) if path.is_file() else None)
    if payload is None:
        return Projection(tuple(ids), tuple(ids), (), {}, inventory, copy.deepcopy(graph.get('variant', {})),
                          {'all':len(ids),'product':len(ids),'historical':0, **{k:0 for k in KINDS}}, frozen, {})
    _shape(payload, 'schema_version source_platform source_sha256 graph_sha256 product_context review boundaries replacements', 'responsibility payload')
    _require(payload['schema_version'] == 1 and payload['source_platform'] == 'ios' and payload['source_sha256'] == graph['source_sha256'] and
             payload['graph_sha256'] == digest(json_bytes(graph)), 'responsibility source/graph/version is stale')
    if candidate is None:
        frozen['spec/baseline/ios-responsibility.json'] = digest(path.read_bytes())
    # Even an unrelated dependency payload cannot silently retire ACs belonging
    # to an unapproved decision elsewhere in the original global inventory.
    from .artifact_contract import markdown_sections, _visible_lines
    ledger = _ref(project, 'spec/decision-ledger.md', frozen).read_text(encoding='utf-8-sig')
    for decision in {r['superseded_by'] for r in inventory['source_history'].values()}:
        sections = [s for s in markdown_sections(ledger) if s['title'].split()[0] == decision]
        _require(len(sections) == 1, 'historical acceptance requires one original decision heading')
        body = '\n'.join(line for _, line in _visible_lines(sections[0]['body']))
        _require(re.search(r'(?im)^\s*-?\s*status\s*[:：]\s*approved(?:\b|[。\s])', body) and
                 re.search(r'(?m)^\s*-?\s*(?:授权|依据|authorization)\s*[:：]\s*\S+', body),
                 'historical acceptance requires approved decision and authorization evidence')
    # Candidate hashes are not file pins. Consumers must persist and revalidate
    # before plan freeze; candidate acceptance cannot authorize dispatch.
    members = _context(project, source, payload['product_context'], graph, frozen)
    indexed = {f['path']:f for f in source_snapshot(source)['files']}
    roles, routes, reviewers = _review(project, source, payload['review'], graph, indexed, frozen)
    facts = {f['id']:f for f in graph['facts']}
    expected = {o['id']:o for o in obligations['obligations']}
    boundaries, treatments = {}, {}
    _require(isinstance(payload['boundaries'], list), 'boundaries must be a list')
    for row in payload['boundaries']:
        _shape(row, 'id kind sources obligation_ids public_contracts skip_ref', 'boundary', optional='source_ac_bindings')
        ident, kind = row['id'], row['kind']
        _require(kind != 'unused_symbol', 'unused-symbol exclusion requires a replayable reachability provider; review text or no-entry labels cannot prove whole-program absence')
        _require(isinstance(ident, str) and re.fullmatch(r'[A-Za-z][A-Za-z0-9_-]*', ident) and ident not in boundaries and kind in KINDS, 'invalid/duplicate boundary ID or kind')
        _require(isinstance(row['sources'], list) and row['sources'], 'boundary requires exact source spans')
        for span in row['sources']:
            _source_span(source, span, indexed)
            if kind == 'dependency_internal':
                _require(roles[span['path']] == 'dependency', 'app/resource effects cannot become dependency internals')
            elif kind == 'replaced_source_history':
                _require(roles[span['path']] in ('dependency', 'application'), 'only reviewed app or dependency history may be replaced')
            if kind == 'test_target':
                _require(roles[span['path']] == 'test' and span['path'] not in members and Path(span['path']).suffix in ('.swift', '.m', '.mm', '.c', '.cpp', '.cc'), 'test exclusion requires original out-of-target evidence')
        skip = _section(project, row['skip_ref'], frozen)
        _require(row['skip_ref'].startswith('spec/baseline/skip-list.md#') and
                 all(s['path'] in skip and s['symbol'] in skip for s in row['sources']), 'skip-list must name exact file/symbol boundary')
        obs = _strings(row['obligation_ids'], 'boundary obligation IDs')
        boundary_facts = []
        for obligation in obs:
            _require(obligation in expected and obligation not in treatments, 'unknown/overlapping obligation treatment')
            fact = facts[expected[obligation]['fact_id']]
            _require(any(_inside(fact['anchor'], s) for s in row['sources']), 'fact is not wholly inside the reviewed span')
            route = routes[fact['id']]
            _require(ident in route['boundary_ids'], 'boundary absent from reviewed entry/call inventory')
            if kind == 'unused_symbol':
                _require(route['resolution'] == 'no_entry', 'unused symbol still has a product/indirect entry')
            elif kind == 'test_target':
                _require(route['resolution'] == 'outside_selected_target', 'test boundary route is not outside selected target')
            elif kind == 'replaced_source_history' and roles[fact['anchor']['path']] == 'application':
                _require(route['resolution'] == 'product_entry', 'application history must retain its reviewed product entry role')
            else:
                _require(route['resolution'] == 'dependency_boundary', 'app route cannot be treated as dependency internal')
            boundary_facts.append(fact['id'])
            treatments[obligation] = {'kind':kind,'boundary_ref':ident,'source_fact_id':fact['id']}
        _require(isinstance(row['public_contracts'], list), 'public_contracts must be a list')
        if kind == 'dependency_internal' or kind == 'replaced_source_history' and any(roles[s['path']] == 'dependency' for s in row['sources']):
            _require(row['public_contracts'], 'used dependencies require active public boundary contracts')
        if 'source_ac_bindings' in row:
            _require(kind == 'replaced_source_history', 'source AC bindings apply only to explicitly replaced history')
        for contract in row['public_contracts']:
            _shape(contract, 'caller_fact_ids ac_ids callee_symbol', 'public boundary contract', optional='caller_sources')
            _require(isinstance(contract['callee_symbol'], str) and contract['callee_symbol'].strip() and
                     any(s['symbol'] in contract['callee_symbol'] for s in row['sources']), 'callee does not identify reviewed dependency symbol')
            callerids = _strings(contract['caller_fact_ids'], 'public caller facts')
            _require(all(f in facts and roles[facts[f]['anchor']['path']] == 'application' and routes[f]['resolution'] == 'product_entry' for f in callerids), 'public boundary needs exact app caller evidence')
            # A public boundary needs a real call-site selector signal, not an
            # arbitrary prose label. Receiver/type dispatch remains independent
            # source review; this lexical check never claims a complete call graph.
            from .swiftui import tokenize
            selector = contract['callee_symbol'].split('.')[-1]
            _require(re.fullmatch(r'[A-Za-z_]\w*(?::(?:[A-Za-z_]\w*:)*?)?', selector), 'callee must retain a complete Objective-C selector')
            selectors = re.findall(r'[A-Za-z_]\w*', selector)
            arity = selector.count(':')
            caller_spans = contract.get('caller_sources')
            if caller_spans is not None:
                _require(isinstance(caller_spans, list) and caller_spans, 'explicit caller_sources must be nonempty')
                for span in caller_spans:
                    _source_span(source, span, indexed)
                    _require(roles[span['path']] == 'application' and any(_inside(facts[f]['anchor'], span) for f in callerids),
                             'caller source span needs its exact reviewed application fact')
                _require(all(any(_inside(facts[f]['anchor'], span) for span in caller_spans) for f in callerids),
                         'every caller fact must be wholly within its explicit call source span')
            else:
                caller_spans = [facts[f]['anchor'] for f in callerids]
            calls = []
            for anchor in caller_spans:
                lines = _file(source, anchor['path']).read_text(encoding='utf-8-sig').splitlines()
                calls.append(bool(selectors) and _has_selector_call(tokenize('\n'.join(lines[anchor['line']-1:anchor['end_line']]), skip_pragma_marks=True), selectors, arity=arity))
            _require(all(calls) if 'caller_sources' in contract else any(calls),
                     'public boundary has no actual complete caller selector call shape')
            _require(set(_strings(contract['ac_ids'], 'public active AC IDs')) <= inventory['active_target'].keys(), 'public dependency contract needs active target ACs')
        boundaries[ident] = {**copy.deepcopy(row), 'fact_ids':boundary_facts}
    _require(all(set(r['boundary_ids']) <= boundaries.keys() for r in routes.values()), 'entry/call inventory references missing boundary')
    semantic = _replace(project, source, payload['replacements'], graph, semantics, boundaries, facts, roles, reviewers, inventory, frozen)
    product = tuple(i for i in ids if i not in treatments)
    historical = tuple(i for i in ids if i in treatments)
    counts = {'all':len(ids),'product':len(product),'historical':len(historical),
              **{k:sum(t['kind']==k for t in treatments.values()) for k in KINDS}}
    projection = Projection(tuple(ids), product, historical, treatments, inventory, copy.deepcopy(graph.get('variant', {})), counts, frozen, semantic,
                            enabled=True, candidate=candidate is not None,
                            historical_action_ids=tuple(a for r in payload['replacements'] for a in r['historical_action_ids']),
                            target_action_ids=tuple(a for r in payload['replacements'] for a in r['target_action_ids']))
    _require(source_snapshot(source)['sha256'] == graph['source_sha256'], 'source changed during responsibility validation')
    projection.validate_frozen_inputs(project)
    return projection
