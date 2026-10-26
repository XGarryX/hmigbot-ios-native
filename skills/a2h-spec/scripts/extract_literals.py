"""Read real iOS source literals; never report an empty spec scan as source coverage."""
from pathlib import Path
import argparse
import json
import sys
here = Path(__file__).resolve()
skill = next(p for p in here.parents if (p / 'SKILL.md').is_file())
runtime = skill / 'runtime.json'
root = (skill / json.loads(runtime.read_text())['runtime_relative']).resolve() if runtime.exists() else skill.parents[1]
sys.path.insert(0, str(root / 'src'))
from hmigbot_ios.ios_literals import run
from hmigbot_ios.core import MigrationError
parser = argparse.ArgumentParser()
parser.add_argument('--spec-dir', type=Path, required=True)
parser.add_argument('--out', type=Path, required=True)
args = parser.parse_args()
try:
    project = args.spec_dir.resolve().parent.parent
    result = run(project, args.out)
    print(json.dumps(result, ensure_ascii=False, indent=2))
except (MigrationError, OSError, ValueError) as exc:
    print(json.dumps({'status': 'FAIL', 'error': str(exc)}))
    raise SystemExit(2)
