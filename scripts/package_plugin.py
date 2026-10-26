"""Build directly from this source checkout, retaining its layout and metadata."""
import argparse
import json
from pathlib import Path
from package_tree import build_package


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    try:
        report = build_package(Path(__file__).resolve().parents[1], args.output)
    except (OSError, ValueError) as exc:
        parser.error(str(exc))
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
