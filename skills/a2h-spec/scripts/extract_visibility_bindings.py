from pathlib import Path
import sys
_here=Path(__file__).resolve()
for _parent in _here.parents:
    _runtime=_parent/'runtime.json'
    if _runtime.is_file():
        import json
        _root=(_parent/json.loads(_runtime.read_text(encoding='utf-8'))['runtime_relative']).resolve()
        if (_root/'src/hmigbot_ios152').is_dir(): sys.path.insert(0,str(_root/'src')); break
    if (_parent/'src/hmigbot_ios152').is_dir(): sys.path.insert(0,str(_parent/'src')); break
import argparse
from hmigbot_ios152.source import Source
from hmigbot_ios152.ui import visibility,visibility_warnings
import json
p=argparse.ArgumentParser(); p.add_argument('--ios-root',dest='source_root'); p.add_argument('--android-root',dest='source_root',help=argparse.SUPPRESS); p.add_argument('--output',required=True); p.add_argument('--project-root')
a=p.parse_args()
if not a.source_root: p.error('--ios-root is required')
out=Path(a.output); out.parent.mkdir(parents=True,exist_ok=True)
value=visibility(Source(a.source_root,a.project_root))
out.write_text(json.dumps(value,ensure_ascii=False,indent=2),encoding='utf-8')
for warning in visibility_warnings(value): print(warning,file=sys.stderr)
