"""Native frontend for a bundled HMigBot consumer."""
from pathlib import Path
import json, sys
here = Path(__file__).resolve()
skill = next(p for p in here.parents if (p / 'SKILL.md').is_file())
config = skill / 'runtime.json'
root = (skill / json.loads(config.read_text())['runtime_relative']).resolve() if config.exists() else skill.parents[1]
sys.path.insert(0, str(root / 'src'))
from hmigbot_ios.native_helpers import main
raise SystemExit(main(['feature-inputs', *sys.argv[1:]]))
