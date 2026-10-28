# Native source boundary; original functional enumeration/merge remains bundled.
from pathlib import Path
import json
import sys
_here = Path(__file__).resolve()
for _parent in _here.parents:
    _runtime = _parent / 'runtime.json'
    if _runtime.is_file():
        _root = (_parent / json.loads(_runtime.read_text(encoding='utf-8'))['runtime_relative']).resolve()
        if (_root / 'src/hmigbot_ios152').is_dir():
            sys.path.insert(0, str(_root / 'src')); break
    if (_parent / 'src/hmigbot_ios152').is_dir():
        sys.path.insert(0, str(_parent / 'src')); break
else:
    raise SystemExit('HMigBot native functional runtime was not found')
from hmigbot_ios152.native_functional import main
raise SystemExit(main(_here.stem, sys.argv[1:], _here.parent))
