"""Mechanical iOS source helpers for HMigBot's original a2h pipeline."""
from pathlib import Path
import json
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from hmigbot_ios.host import require_supported_host
from hmigbot_ios.core import MigrationError


def main(argv=None):
    try:
        require_supported_host()
    except MigrationError as exc:
        print(json.dumps({'status': 'unsupported', 'error': str(exc),
                          'release_profile': 'macos-arm64',
                          'recovery': 'Run this release on macOS Apple Silicon; see PLATFORM-ROADMAP.md'}),
              file=sys.stderr)
        return 2
    from hmigbot_ios.native_pipeline import main as run_pipeline
    return run_pipeline(argv)

if __name__ == '__main__':
    raise SystemExit(main())
