"""Copied into each skill. Resolves either plugin or workspace installation layout."""
import json
from pathlib import Path
import runpy
import sys

skill = Path(__file__).resolve().parents[1]
config = skill / 'runtime.json'
if config.exists():
    root = (skill / json.loads(config.read_text(encoding='utf-8'))['runtime_relative']).resolve()
else:
    root = Path(__file__).resolve().parents[3]
if not (root / '.codex-plugin/plugin.json').is_file():
    raise SystemExit('Complete hmigbot-ios runtime is missing; rerun the workspace installer')
if sys.argv[1:] == ['--runtime-root']:
    print(root)
else:
    runpy.run_path(str(root / 'scripts/a2h_ios.py'), run_name='__main__')
