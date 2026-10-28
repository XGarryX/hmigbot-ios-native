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
import argparse, json
from hmigbot_ios152.source import Source
from hmigbot_ios152.native_context import describe
p = argparse.ArgumentParser(description='Native selected-source UI entry declarations')
p.add_argument('src'); p.add_argument('--json', action='store_true'); p.add_argument('--project-root')
a = p.parse_args()
print(json.dumps(describe(Source(a.src, a.project_root)), ensure_ascii=False, indent=2))
