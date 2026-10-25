"""Check or restore bundled Mac runtime execution bits after packaging."""
import argparse
import hashlib
import json
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--fix', action='store_true', help='Restore only execution bits; engine bytes are never changed')
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    records = json.loads((root / 'docs/macos-runtime-modes.json').read_text())['files']
    changed = []
    for name, record in records.items():
        path = root / name
        with path.open('rb') as stream:
            actual = hashlib.file_digest(stream, 'sha256').hexdigest()
        if actual != record['sha256']:
            raise ValueError('Runtime content differs from permission manifest: ' + name)
        if bool(path.stat().st_mode & 0o111) != record['executable']:
            changed.append(name)
    if args.fix:
        for name in changed:
            path = root / name
            mode = path.stat().st_mode & ~0o111
            path.chmod(mode | (0o111 if records[name]['executable'] else 0))
    print(json.dumps({'checked': len(records), 'execution_bit_differences': changed,
                      'fixed': len(changed) if args.fix else 0}, indent=2))
    return 0 if args.fix or not changed else 1


if __name__ == '__main__':
    raise SystemExit(main())
