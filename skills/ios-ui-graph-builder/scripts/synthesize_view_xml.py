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
from hmigbot_ios152.cli import main
if __name__=="__main__": raise SystemExit(main(["view",*sys.argv[1:]]))
