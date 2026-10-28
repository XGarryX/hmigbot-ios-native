# Public visual entry; native source actions never fall through to ADB.
from pathlib import Path
import hashlib
import json
import sys

_here = Path(__file__).resolve()
_scripts = _here.parent
_marker = _scripts / '.hmigbot-public-scripts.json'
if _marker.is_file():
    _record = json.loads(_marker.read_text(encoding='utf-8'))
    _scripts = Path(_record['scripts']).resolve()
    _original = _scripts / _here.name
    _expected = _record.get('sha256', {}).get(_here.name)
    if (not _expected or not _original.is_file() or
        hashlib.sha256(_here.read_bytes()).hexdigest() != _expected or
        hashlib.sha256(_original.read_bytes()).hexdigest() != _expected):
        raise SystemExit('Compiled visual cache public-entry hash mismatch')

for _parent in _here.parents:
    _runtime = _parent / 'runtime.json'
    if _runtime.is_file():
        _root = (_parent / json.loads(_runtime.read_text(encoding='utf-8'))['runtime_relative']).resolve()
        if (_root / 'src/hmigbot_ios152').is_dir():
            sys.path.insert(0, str(_root / 'src'))
            break
    if (_parent / 'src/hmigbot_ios152').is_dir():
        sys.path.insert(0, str(_parent / 'src'))
        break
else:
    raise SystemExit('HMigBot visual runtime was not found')

from hmigbot_ios152.visual_dispatch import run
raise SystemExit(run(_here.stem, sys.argv[1:], _scripts))
