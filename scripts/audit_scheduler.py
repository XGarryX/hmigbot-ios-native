"""Validate the selected 1.7.0 scheduler payload against the original archive manifest."""
from pathlib import Path
import hashlib
import json
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from hmigbot_ios.payload_layout import exclusion, release_profile

ROOT = Path(__file__).resolve().parents[1]

def audit(root=ROOT):
    from pathlib import PurePosixPath
    root = Path(root)
    manifest_path = root / 'docs/upstream/scheduler-1.7.0-manifest.json'
    raw = manifest_path.read_bytes()
    manifest = json.loads(raw.decode('utf-8'))
    adaptation_path = root / 'docs/upstream/runtime-adaptations.json'
    adaptations = json.loads(adaptation_path.read_text()).get('changes', []) if adaptation_path.is_file() else []
    reviewed = {item['path']: item for item in adaptations}
    if len(reviewed) != len(adaptations):
        raise ValueError('Duplicate reviewed runtime adaptation')
    failures, excluded, selected, applied = [], [], [], []
    for file in manifest['files']:
        relative = file['path']
        path = PurePosixPath(relative)
        if (path.is_absolute() or '..' in path.parts or '\\' in relative or ':' in relative or
                not path.parts or path.as_posix() != relative):
            raise ValueError('Unsafe scheduler source manifest path')
        reason = exclusion('vendor/hmigbot-1.7.0/' + relative)
        if reason:
            excluded.append({'path': relative, 'reason': reason})
            continue
        selected.append(relative)
        path = root / 'vendor/hmigbot-1.7.0' / relative
        actual = hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None
        change = reviewed.get('vendor/hmigbot-1.7.0/' + relative, {})
        approved = (path.suffix == '.py' and change.get('kind') == 'python_rule_adaptation'
                    and change.get('source_manifest') == 'docs/upstream/scheduler-1.7.0-manifest.json'
                    and change.get('source_sha256') == file['sha256']
                    and change.get('sha256') == actual and bool(change.get('reason')))
        if actual != file['sha256'] and not approved:
            failures.append(relative)
        elif actual != file['sha256']:
            applied.append(relative)
    return {'version': manifest['version'], 'source_files': len(manifest['files']),
            'source_manifest_sha256': hashlib.sha256(raw).hexdigest(),
            'release_profile': release_profile(), 'files': len(selected),
            'excluded_source_files': excluded,
            'reviewed_python_adaptations': applied,
            'status': 'failed' if failures else 'passed', 'failures': failures,
            'scope': 'Every selected scheduler runtime input is checked against the complete original source manifest; excluded tests/platforms are not required.'}


if __name__ == '__main__':
    result = audit()
    print(json.dumps(result, ensure_ascii=False))
    raise SystemExit(1 if result['status'] != 'passed' else 0)
