"""Compare an exact ZIP to its sidecar manifest and optionally its source checkout."""
import argparse
import json
from pathlib import Path
from package_tree import verify_package


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--package', type=Path, required=True)
    parser.add_argument('--source', type=Path)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    if args.output and args.output.exists():
        parser.error('Report already exists')
    try:
        report = verify_package(args.package, args.source)
    except (OSError, ValueError, KeyError) as exc:
        report = {'status': 'failed', 'error': str(exc)}
    text = json.dumps(report, ensure_ascii=False, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text + '\n', encoding='utf-8')
    print(text)
    return 0 if report['status'] == 'passed' else 1


if __name__ == '__main__':
    raise SystemExit(main())
