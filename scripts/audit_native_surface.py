"""Audit maintained instruction entrypoints; separately disclose the intact archive."""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import re

ROOT = Path(__file__).resolve().parents[1]
LEGACY = re.compile(r'android|安卓|kotlin|gradle|(?<![A-Za-z])adb(?![A-Za-z])|Jetpack|AppCompat|'
                    r'Intent\.ACTION_|DialogFragment|setContentView|findViewById|res/layout', re.I)
TEXT = {'.md', '.py', '.js', '.json', '.toml', '.yaml', '.yml', '.ps1', '.sh', ''}
CONTEXT_POLICY = 'policies/native-surface-contexts.json'


def _unique_keys(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('Duplicate reviewed-context policy key: ' + key)
        result[key] = value
    return result


def reviewed_context_policy(root):
    """Load only exact, single-line reviews; no patterns or folder exclusions."""
    raw = (root / CONTEXT_POLICY).read_bytes()
    policy = json.loads(raw.decode('utf-8-sig'), object_pairs_hook=_unique_keys)
    if (not isinstance(policy, dict) or type(policy.get('schema_version')) is not int
            or policy['schema_version'] != 1 or not isinstance(policy.get('contexts'), list)):
        raise ValueError('Expected reviewed-context policy version 1 with contexts array')
    seen_ids, seen_lines = set(), set()
    required = {'id', 'path', 'text', 'line_sha256', 'kind', 'reason'}
    for entry in policy['contexts']:
        if not isinstance(entry, dict) or set(entry) != required:
            raise ValueError('Reviewed context requires exactly id/path/text/line_sha256/kind/reason')
        if any(not isinstance(entry[key], str) or not entry[key].strip() for key in required):
            raise ValueError('Reviewed context fields must be nonempty strings')
        path = entry['path']
        parts = PurePosixPath(path).parts
        if (not parts or parts[0] not in {'skills', 'agents-codex', 'bin'}
                or any(c in path for c in '\\:*?[]') or PurePosixPath(path).is_absolute()
                or any(part in {'.', '..'} for part in parts)
                or PurePosixPath(path).as_posix() != path or PurePosixPath(path).suffix not in TEXT):
            raise ValueError('Reviewed context path must be an exact maintained file path')
        if '\n' in entry['text'] or '\r' in entry['text'] or not LEGACY.search(entry['text']):
            raise ValueError('Reviewed context must contain one complete legacy-bearing line')
        if not re.fullmatch('[0-9a-f]{64}', entry['line_sha256']):
            raise ValueError('Reviewed context requires the original line bytes SHA256')
        if entry['kind'] not in {'comparison', 'prohibition'}:
            raise ValueError('Reviewed context kind must be comparison or prohibition')
        key = (path, entry['text'], entry['line_sha256'])
        if entry['id'] in seen_ids or key in seen_lines:
            raise ValueError('Duplicate reviewed context ID or exact line')
        seen_ids.add(entry['id'])
        seen_lines.add(key)
    return policy['contexts'], hashlib.sha256(raw).hexdigest()


def audit(root=ROOT):
    root = Path(root)
    files, findings, disclosed = [], [], []
    try:
        contexts, policy_sha256 = reviewed_context_policy(root)
    except (OSError, ValueError, UnicodeDecodeError) as exc:
        contexts, policy_sha256 = [], None
        findings.append({'path': CONTEXT_POLICY, 'rule': 'reviewed-context-policy-invalid',
                         'reason': str(exc)})
    exact = {(entry['path'], entry['text'], entry['line_sha256']): entry for entry in contexts}
    matches = {entry['id']: [] for entry in contexts}
    for folder in ('skills', 'agents-codex', 'bin'):
        for path in (root / folder).rglob('*'):
            if not path.is_file() or '__pycache__' in path.parts or path.suffix not in TEXT:
                continue
            try:
                raw = path.read_bytes()
                raw.decode('utf-8-sig')
            except UnicodeDecodeError:
                continue
            files.append(path.relative_to(root).as_posix())
            for i, raw_line in enumerate(raw.splitlines(keepends=True), 1):
                line = raw_line.decode('utf-8-sig').rstrip('\r\n')
                if LEGACY.search(line):
                    entry = exact.get((files[-1], line, hashlib.sha256(raw_line).hexdigest()))
                    if entry:
                        matches[entry['id']].append(i)
                        disclosed.append({**entry, 'line': i})
                    else:
                        findings.append({'path': files[-1], 'line': i, 'text': line[:260],
                                         'rule': 'unreviewed-legacy-surface'})
    for entry in contexts:
        positions = matches[entry['id']]
        if len(positions) != 1:
            findings.append({'path': entry['path'], 'id': entry['id'],
                             'rule': 'reviewed-context-stale' if not positions else 'reviewed-context-ambiguous',
                             'matched_lines': positions,
                             'reason': 'Each reviewed exact line must occur once; re-review changes explicitly'})
    retired = json.loads((root / 'docs/upstream/retired-skills.json').read_text(encoding='utf-8'))
    for name in retired:
        if (root / 'skills' / name / 'SKILL.md').exists():
            findings.append({'path': f'skills/{name}', 'rule': 'retired-source-skill-discoverable'})
    return {'status': 'passed' if not findings else 'failed', 'files_scanned': len(files),
            'findings': findings, 'reviewed_contexts': disclosed,
            'reviewed_context_policy': {'path': CONTEXT_POLICY, 'sha256': policy_sha256,
                                        'binding': 'exact path + complete text + original line bytes SHA256'},
            'scope': 'All maintained skills, references, templates, roles and text entrypoints',
            'archive': 'vendor/hmigbot contains 3516 imported resources (byte equality audited separately), outside active discovery; original platform names are retained there',
            'other_occurrences': 'Historical documentation and negative compatibility tests retain truthful names. This lexical gate does not prove semantic or application equivalence.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    result = audit()
    text = json.dumps(result, ensure_ascii=False, indent=2) + '\n'
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding='utf-8')
    print(text)
    return 0 if result['status'] == 'passed' else 1


if __name__ == '__main__':
    raise SystemExit(main())
