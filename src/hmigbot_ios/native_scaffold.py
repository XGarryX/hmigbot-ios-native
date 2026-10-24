"""Compatibility candidate adapter to the sole native gate content producer."""
from pathlib import Path
import os,re
from .core import MigrationError,digest,json_bytes,read_json,safe_child,snapshot
from .native_pipeline import context
from .source_candidates import discover_candidates, classify_type, _top_level_types

def _reviewed_snapshot(source, project, expected_sha256=None):
    index_path = project / 'spec/baseline/ios-source-index.json'
    if not index_path.is_file():
        raise MigrationError('Source index missing: run source-index/refresh and review before scaffolding')
    index = read_json(index_path)
    current = snapshot(source)
    if index.get('source_sha256') != current['sha256'] or index.get('files') != current['files']:
        raise MigrationError('Source changed or source index files disagree; re-review the source baseline before scaffolding')
    if expected_sha256 is not None and expected_sha256 != current['sha256']:
        raise MigrationError('Provided source_sha256 does not match current source')
    return index, current

def scaffold(project, *, source_sha256=None):
    from .gate_artifacts import render_spec_inputs
    source, project = context(project)
    index, current = _reviewed_snapshot(source, project, source_sha256)
    candidates = discover_candidates(source, index)
    if not any(c['is_ui'] for c in candidates):
        raise MigrationError('Scaffold found no UI surface candidate; author features/pages manually rather than fabricating them')
    rendered = render_spec_inputs(project)
    files = {path: text for path, text in sorted(rendered['files'].items(), key=lambda row: (0 if '/features/' in row[0] else 1 if '/ui/' in row[0] else 2, row[0])) if _allowed_path(path)}
    _reviewed_snapshot(source, project, current['sha256'])
    for item in candidates:
        anchor = item['anchor']
        page = next((p for p in rendered['pages'] if p['source']==anchor['path'] and p['name']==item['name']), None)
        item.update(page_id=page['page_id'] if page else None, feature_id='F001' if page else None,
                    stable_key=digest(json_bytes([item['decl_kind'], item['name'], anchor['path'], anchor['line']]))[:16],
                    enterable_plan=False)
    return {'schema_version': 2, 'kind': 'spec-scaffold-candidate', 'source_platform': 'ios',
            'source_sha256': current['sha256'], 'candidate': True, 'needs_review': True,
            'spec_complete': False, 'behavior_verified': False, 'enterable_plan': False,
            'source_change_detected': False, 'candidates': candidates,
            'summary': {'total_candidates': len(candidates), 'pages': len(rendered['pages']),
                        'features': int(bool(rendered['pages'])),
                        'components': sum(c['candidate_type']=='component' for c in candidates),
                        'bridges': sum(c['is_bridge'] for c in candidates),
                        'extensions': sum(c['is_extension'] for c in candidates),
                        'unknown_templates': sum(c['unknown_template'] for c in candidates)},
            'files': {path: {'kind': 'page' if '/ui/' in path else 'feature' if '/features/' in path else 'index'} for path in files},
            'file_contents': files,
            'inventory_diff': {'new_pages': [p['page_id'] for p in rendered['pages']],
                               'new_features': ['F001'] if rendered['pages'] else [],
                               'unknown_templates': [c['name'] for c in candidates if c['unknown_template']],
                               'extensions': [c['name'] for c in candidates if c['is_extension']]}}


def _allowed_path(path):
    return bool(re.fullmatch(r'spec/baseline/(?:feature-index\.md|ui-manifest\.md|feature-base\.md|api-inventory\.md)', path)
                or re.fullmatch(r'spec/baseline/features/F\d+-.+\.md', path)
                or re.fullmatch(r'spec/baseline/ui/page_\d+(?:_.+)?\.md', path))


def _fid_conflict(base, path):
    match = re.match(r'(F\d+|page_\d+)', Path(path).stem)
    if match is None:
        return None
    folder = base / ('features' if match[1].startswith('F') else 'ui')
    if any(existing.name != Path(path).name for existing in folder.glob(match[1]+'*.md')):
        return match[1]
    return None


def apply_scaffold(project, candidate):
    """Materialize only missing scaffold files, never trusting the supplied candidate.

    Security / integrity contract (per in-scope review):

    * The supplied ``candidate`` is verified, never executed. The canonical candidate
      is re-derived from the current reviewed source and compared against it.
    * Any path outside the four allowed scaffold outputs (e.g. ``ios-semantics.json``
      or other pseudo-approved artifacts) is rejected outright.
    * Identity (``stable_key`` set), source hash and file content must match the
      re-derived candidate exactly; a drift, hand-inserted baseline, stale index or
      tampered content is refused.
    * All paths and conflicts are pre-checked. Exclusive creation cannot overwrite
      another author; failure rolls back only our still-unchanged creations.
    * Existing documents are never overwritten; only same-content idempotent fills are
      permitted.
    """
    source, project = context(project)
    if not isinstance(candidate, dict) or candidate.get('kind') != 'spec-scaffold-candidate':
        raise MigrationError('apply requires a spec-scaffold-candidate produced by native_scaffold.scaffold')
    if candidate.get('schema_version') != 2:
        raise MigrationError('Old candidate schema; regenerate with spec-scaffold before applying')
    # 1. reject foreign / pseudo-approved artifacts up front
    for path in candidate.get('file_contents', {}):
        if not _allowed_path(path):
            raise MigrationError('Candidate carries non-scaffold artifact (possible pseudo-approved baseline): ' + path)
    baseline = (project / 'spec/baseline').resolve()
    for path in candidate.get('file_contents', {}):
        conflict = _fid_conflict(baseline, path)
        if conflict:
            raise MigrationError('Conflicting main document for ' + conflict)
    conflict = _fid_conflict(baseline, 'spec/baseline/features/F001-ios-source.md')
    if conflict:
        raise MigrationError('Conflicting main document for ' + conflict)
    # 2. re-derive canonical candidate from current reviewed source
    rederived = scaffold(project)
    # 3. consistency: supplied candidate must match the derived identity/hash/content
    if candidate.get('source_sha256') != rederived['source_sha256']:
        raise MigrationError('Provided candidate source_sha256 does not match currently derived source')
    if {c['stable_key'] for c in candidate.get('candidates', [])} != {c['stable_key'] for c in rederived['candidates']}:
        raise MigrationError('Candidate identity drift vs derived source candidates; refuse apply')
    expected = dict(rederived['file_contents'])
    provided = candidate.get('file_contents', {})
    if set(provided.keys()) != set(expected.keys()):
        raise MigrationError('Candidate file set differs from derived source files; refuse apply')
    for path, content in expected.items():
        if provided.get(path) != content:
            raise MigrationError('Candidate content differs from derived source content: ' + path)
    # 4. pre-check every path / conflict, then write only missing (idempotent)
    baseline = (project / 'spec/baseline').resolve()
    plan, skipped = [], []
    for path, content in expected.items():
        target = safe_child(project, path)
        if not target.is_relative_to(baseline):
            raise MigrationError('Scaffold path escapes spec/baseline: ' + path)
        fid = _fid_conflict(baseline, path)
        if fid is not None:
            raise MigrationError('Conflicting main document for ' + fid + '; refuse to create duplicate ID')
        if target.exists():
            if target.read_text(encoding='utf-8-sig') != content:
                raise MigrationError('Existing document conflicts with candidate (would overwrite): ' + path)
            skipped.append(path)
            continue
        plan.append((path, target, content.encode('utf-8')))
    from .artifact_commit import create_missing
    def check():
        _reviewed_snapshot(source, project, rederived['source_sha256'])
        for path in expected:
            if _fid_conflict(baseline, path) is not None:
                raise MigrationError('Conflicting main document; refuse to create duplicate ID')
    return create_missing(project, expected, before_commit=check, strict_existing=True)
