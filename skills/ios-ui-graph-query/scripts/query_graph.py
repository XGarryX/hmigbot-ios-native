from pathlib import Path
import json,sys
skill=Path(__file__).resolve().parents[1]
config=skill/'runtime.json'
root=(skill/json.loads(config.read_text())['runtime_relative']).resolve() if config.exists() else skill.parents[1]
sys.path.insert(0,str(root/'src'))
from hmigbot_ios.portable_helper import command as original_command
from hmigbot_ios.graph_wire import run
helper=root/'vendor/hmigbot/skills/ios-ui-graph-query/scripts/query_graph.py'
with original_command(helper,sys.argv[1:]) as (argv,env):
    raise SystemExit(run(argv[0],"query_graph",sys.argv[1:],helper.parent))
