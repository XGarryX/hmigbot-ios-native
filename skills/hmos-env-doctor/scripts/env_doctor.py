"""Read-only target environment diagnostics; no device call by default."""
from pathlib import Path
import json, sys
here = Path(__file__).resolve()
skill = next(p for p in here.parents if (p / 'SKILL.md').is_file())
runtime = skill / 'runtime.json'
root = (skill / json.loads(runtime.read_text())['runtime_relative']).resolve() if runtime.exists() else skill.parents[1]
sys.path.insert(0, str(root / 'src'))
from hmigbot_ios.target_environment import main
raise SystemExit(main())
