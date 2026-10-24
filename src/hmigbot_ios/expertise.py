"""Pinned source expertise, topic routing and source-backed review receipts."""
from pathlib import Path

from .core import MigrationError, digest, json_bytes, read_json, safe_child, write_json
from .swiftui import tokenize

ROOT = Path(__file__).resolve().parents[2]
BUNDLE = ROOT / 'vendor/ios-expertise'
PLAN = 'spec/ref/ios-expertise-plan.json'
REVIEWS = 'spec/ref/ios-expertise-reviews.json'
SKILL_ROOTS = {
    'swiftui': 'swiftui/skills/swiftui-expert-skill',
    'concurrency': 'concurrency/skills/swift-concurrency',
    'uikit': 'uikit/axiom-codex/skills/axiom-uikit',
}


def audit():
    manifest = read_json(BUNDLE / 'manifest.json')
    if manifest.get('schema_version') != 1 or {p['id'] for p in manifest['packs']} != set(SKILL_ROOTS):
        raise MigrationError('Invalid external skill manifest')
    files = {}
    for pack in manifest['packs']:
        if pack['license'] != 'MIT' or len(pack['commit']) != 40:
            raise MigrationError('Unreviewed skill license or revision')
        for item in pack['files']:
            path = safe_child(BUNDLE, item['path'])
            if item['path'] in files or digest(path.read_bytes()) != item['sha256']:
                raise MigrationError('Pinned skill changed: ' + item['path'])
            files[item['path']] = item['sha256']
    for root in SKILL_ROOTS.values():
        if root + '/SKILL.md' not in files:
            raise MigrationError('Upstream entrypoint missing')
    return manifest, files


def make_plan(source, graph, *, project=None):
    manifest, files = audit()
    groups = {'swiftui': [], 'concurrency': [], 'uikit': []}
    tokens_by_path = {}
    for item in graph['facts']:
        tokens_by_path.setdefault(item['anchor']['path'], set())
    # Framework detection reads actual tokens, not comments or string literals.
    from .core import snapshot
    for item in snapshot(source)['files']:
        path = item['path']
        if Path(path).suffix in {'.swift', '.m', '.mm', '.h'}:
            tokens = {t.value for t in tokenize((source / path).read_text(encoding='utf-8-sig'), skip_pragma_marks=Path(path).suffix != '.swift') if t.kind != 'string'}
            tokens_by_path[path] = tokens
            if 'SwiftUI' in tokens or 'View' in tokens and 'body' in tokens:
                groups['swiftui'].append(path)
            if tokens & {'Task', 'task', 'async', 'await', 'actor', 'MainActor', 'Sendable', 'AsyncStream'}:
                groups['concurrency'].append(path)
            if tokens & {'UIKit', 'UIViewController', 'UIView', 'UIHostingController', 'UIViewRepresentable', 'UIViewControllerRepresentable'}:
                groups['uikit'].append(path)
        elif Path(path).suffix in {'.xib', '.storyboard'}:
            groups['uikit'].append(path)
    reviews = []
    for pack, paths in groups.items():
        if not paths:
            continue
        facts = [f for f in graph['facts'] if f['anchor']['path'] in paths]
        kinds = {f['kind'] for f in facts}
        refs = []
        if pack == 'swiftui':
            refs = ['view-structure.md', 'state-management.md']
            for kind, name in {'binding': 'state-management.md', 'identity': 'list-patterns.md',
                               'modifier': 'modifier-patterns.md', 'navigation': 'sheet-navigation-patterns.md',
                               'environment': 'environment-patterns.md', 'constraint': 'layout-best-practices.md'}.items():
                if kind in kinds:
                    refs.append(name)
            resources = [SKILL_ROOTS[pack] + '/references/' + v for v in dict.fromkeys(refs)]
            scope = 'ui'
        elif pack == 'concurrency':
            resources = [SKILL_ROOTS[pack] + '/references/' + v for v in ['tasks.md', 'actors.md', 'threading.md', 'sendable.md']]
            scope = 'feature'
        else:
            resources = [SKILL_ROOTS[pack] + '/skills/' + v for v in ['uikit-bridging.md', 'auto-layout-debugging.md', 'uikit-modernization.md']]
            if any('Combine' in tokens_by_path.get(p, set()) for p in paths):
                resources.append(SKILL_ROOTS[pack] + '/skills/combine-patterns.md')
            resources += ['uikit/axiom-codex/skills/axiom-performance/skills/' + v for v in ['memory-debugging.md', 'objc-block-retain-cycles.md']]
            scope = 'ui'
        resources.insert(0, SKILL_ROOTS[pack] + '/SKILL.md')
        reviews.append({'id': 'expertise-' + pack, 'pack': pack, 'scope': scope,
                        'source_paths': sorted(paths), 'fact_ids': [f['id'] for f in facts],
                        'resources': [{'path': p, 'sha256': files[p]} for p in resources],
                        'mode': 'read_only_source_analysis'})
    official_sha = None
    if project is not None:
        from .apple_capabilities import preferred_reviews, GUIDANCE
        # App Intents has an official export but no bundled third-party pack.
        # Include it in the required read contract when that actual resource exists.
        guidance = read_json(project / GUIDANCE) if (project / GUIDANCE).is_file() else {}
        intent_paths = sorted(path for path, tokens in tokens_by_path.items()
                              if tokens & {'AppIntents', 'AppIntent', 'AppEntity', 'IntentResult'})
        if intent_paths and guidance.get('official_resources', {}).get('app_intents'):
            reviews.append({'id': 'expertise-app_intents', 'pack': 'app_intents', 'scope': 'api',
                            'source_paths': intent_paths,
                            'fact_ids': [f['id'] for f in graph['facts'] if f['anchor']['path'] in intent_paths],
                            'resources': [], 'mode': 'read_only_source_analysis'})
        reviews, official_sha = preferred_reviews(project, source, graph, reviews)
    result = {'schema_version': 1, 'source_sha256': graph['source_sha256'],
            'graph_sha256': digest(json_bytes(graph)), 'bundle_sha256': digest(json_bytes(manifest)),
            'reviews': reviews, 'behavior_verified': False}
    if official_sha is not None:
        result['official_guidance_sha256'] = official_sha
    return result


def prepare(project):
    from .native_pipeline import context
    from .ios_facts import validate_graph
    source, project = context(project)
    graph, _ = validate_graph(source, project)
    plan = make_plan(source, graph, project=project)
    path = project / PLAN
    if path.exists() and read_json(path) != plan:
        old = read_json(path)
        archive = project / 'spec/.a2h/history/expertise' / digest(json_bytes(old))
        write_json(archive / 'plan.json', old)
        if (project / REVIEWS).exists():
            write_json(archive / 'reviews.json', read_json(project / REVIEWS))
            (project / REVIEWS).unlink()
    write_json(path, plan)
    cfg = read_json(project / '.migbot/config.json')
    cfg['ios_expertise'] = {'version': 1, 'required': True}
    write_json(project / '.migbot/config.json', cfg)
    return {**plan, 'plan': str(path), 'resource_root': str(BUNDLE),
            'review_status': 'required' if plan['reviews'] else 'not_applicable'}


def validate_reviews(source, project, graph, *, require=True):
    expected = make_plan(source, graph, project=project)
    return _validate_reviews(source, project, expected, require=require)


def _validate_reviews(source, project, expected, *, require=True):
    if read_json(project / PLAN) != expected:
        raise MigrationError('Expertise plan is stale or edited; regenerate and re-review')
    if not expected['reviews']:
        return {'status': 'not_applicable', 'review_count': 0}
    receipt = read_json(project / REVIEWS)
    if receipt.get('plan_sha256') != digest(json_bytes(expected)) or not isinstance(receipt.get('reviews'), list):
        raise MigrationError('Expertise receipt does not pin the current plan')
    required = {r['id']: r for r in expected['reviews']}
    seen = set()
    for review in receipt['reviews']:
        ident = review.get('id')
        if ident not in required or ident in seen:
            raise MigrationError('Unexpected or duplicate expertise review')
        seen.add(ident)
        item = required[ident]
        if review.get('resources') != item['resources'] or review.get('status') != 'reviewed':
            raise MigrationError('Review must acknowledge all pinned skill resources')
        if not isinstance(review.get('reviewer'), str) or not review['reviewer'].strip():
            raise MigrationError('Expertise reviewer missing')
        observations = review.get('observations')
        if not isinstance(observations, list) or not observations:
            raise MigrationError('Expertise source observations missing')
        covered = set()
        for obs in observations:
            anchor = obs.get('source', {})
            path, line = anchor.get('path'), anchor.get('line')
            if path not in item['source_paths'] or not isinstance(line, int) or isinstance(line, bool):
                raise MigrationError('Expertise observation outside assigned source')
            lines = safe_child(source, path).read_text(encoding='utf-8-sig').splitlines()
            if not 1 <= line <= len(lines) or not isinstance(obs.get('interpretation'), str) or not obs['interpretation'].strip():
                raise MigrationError('Expertise observation needs a real source line and interpretation')
            if not isinstance(obs.get('unknowns'), list):
                raise MigrationError('Expertise observation must explicitly list unknowns')
            covered.add(path)
        if covered != set(item['source_paths']):
            raise MigrationError('Expertise review omitted assigned source files')
    if require and seen != set(required):
        raise MigrationError('Required expertise reviews are missing')
    return {'status': 'reviewed', 'review_count': len(seen), 'behavior_verified': False,
            'scope': 'Resource integrity and source-backed review contract; model judgment is not mechanically proven'}


def record(project, input_path):
    from .native_pipeline import context
    from .ios_facts import validate_graph
    source, project = context(project)
    graph, _ = validate_graph(source, project)
    plan = make_plan(source, graph, project=project)
    if read_json(project / PLAN) != plan:
        raise MigrationError('Prepare current expertise plan first')
    candidate = read_json(input_path)
    if candidate.get('plan_sha256') != digest(json_bytes(plan)):
        raise MigrationError('Review input must pin current expertise plan')
    # Validate a submitted receipt in isolation before replacing any prior receipt.
    import tempfile
    with tempfile.TemporaryDirectory(prefix='ios-expertise-review-') as tmp:
        staging = Path(tmp)
        write_json(staging / PLAN, plan)
        write_json(staging / REVIEWS, candidate)
        _validate_reviews(source, staging, plan, require=False)
    old = read_json(project / REVIEWS) if (project / REVIEWS).exists() else {'reviews': []}
    retained = {r['id']: r for r in old['reviews']} if old.get('plan_sha256') == candidate['plan_sha256'] else {}
    retained.update({r['id']: r for r in candidate['reviews']})
    receipt = {'schema_version': 1, 'plan_sha256': candidate['plan_sha256'], 'reviews': list(retained.values())}
    write_json(project / REVIEWS, receipt)
    provenance_path = project / 'spec/ref/ios-analysis-provenance.json'
    provenance = read_json(provenance_path) if provenance_path.exists() else {'schema_version': 1}
    provenance['external_expertise'] = {'status': 'review_declared', 'bundle_sha256': plan['bundle_sha256'],
                                        'plan_sha256': receipt['plan_sha256'],
                                        'reviews': [{'id': r['id'], 'reviewer': r['reviewer'], 'resources': r['resources']} for r in receipt['reviews']]}
    write_json(provenance_path, provenance)
    return {'status': 'recorded', 'review_count': len(retained), 'behavior_verified': False}


def check(project, source, graph):
    cfg = read_json(project / '.migbot/config.json')
    if cfg.get('ios_expertise') != {'version': 1, 'required': True}:
        raise MigrationError('0.7.0 source gate requires expertise-plan and reviewed pinned resources; adopt before continuing legacy plans')
    return validate_reviews(source, project, graph)
