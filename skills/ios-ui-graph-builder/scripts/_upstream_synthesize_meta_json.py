from pathlib import Path
import json,sys
skill=Path(__file__).resolve().parents[1]
config=skill/'runtime.json'
root=(skill/json.loads(config.read_text())['runtime_relative']).resolve() if config.exists() else skill.parents[1]
sys.path.insert(0,str(root/'src'))
from hmigbot_ios.portable_helper import run
raise SystemExit(run(root/'vendor/hmigbot/skills/ios-ui-graph-builder/scripts/_upstream_synthesize_meta_json.py',sys.argv[1:]).returncode)
