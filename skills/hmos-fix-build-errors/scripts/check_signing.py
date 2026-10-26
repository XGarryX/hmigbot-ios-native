"""Invoke the bundled helper; reject its known contradictory missing-file result."""
from pathlib import Path
import json, subprocess, sys


def main():
    here = Path(__file__).resolve()
    skill = next(p for p in here.parents if (p / 'SKILL.md').is_file())
    runtime = skill / 'runtime.json'
    root = (skill / json.loads(runtime.read_text())['runtime_relative']).resolve() if runtime.exists() else skill.parents[1]
    helper = root / 'vendor/hmigbot' / 'skills/hmos-fix-build-errors/scripts/check_signing.py'
    if not helper.is_file():
        raise SystemExit('Bundled helper missing; reinstall the complete plugin')
    result = subprocess.run([sys.executable, str(helper), *sys.argv[1:]], shell=False, capture_output=True)
    contradictory = False
    if result.returncode == 0 and len(sys.argv) > 1:
        try:
            value = json.loads(result.stdout)
            contradictory = (isinstance(value, dict) and value.get('verdict') == 'unsigned'
                and value.get('reason') == 'unsigned(build-profile.json5 not found)'
                and (Path(sys.argv[1]) / 'build-profile.json5').is_file())
        except (ValueError, OSError):
            pass  # Unparseable output or unproven existence retains the original result.
    if contradictory:
        # Existence is the only local observation: no config/material parsing,
        # no invented configured/product_ref/expired or signed/unsigned result.
        output = {'status': 'unavailable', 'verdict': 'unverified',
                  'reason': 'signing probe unavailable: helper reported a missing profile that exists'}
        sys.stdout.buffer.write((json.dumps(output) + '\n').encode('utf-8'))
    else:
        sys.stdout.buffer.write(result.stdout)
    sys.stderr.buffer.write(result.stderr)
    return 3 if contradictory else result.returncode


if __name__ == '__main__':
    raise SystemExit(main())
