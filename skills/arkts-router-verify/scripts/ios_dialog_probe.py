# Native source input dispatch; all legacy arguments/target engines retain their launcher.
from pathlib import Path as _Path
import sys as _sys
_here = _Path(__file__).resolve()
for _parent in _here.parents:
    _runtime = _parent / 'runtime.json'
    if _runtime.is_file():
        import json as _json
        _root = (_parent / _json.loads(_runtime.read_text(encoding='utf-8'))['runtime_relative']).resolve()
        if (_root / 'src/hmigbot_ios152').is_dir():
            _sys.path.insert(0, str(_root / 'src')); break
    if (_parent / 'src/hmigbot_ios152').is_dir():
        _sys.path.insert(0, str(_parent / 'src')); break
from hmigbot_ios152.native_routes_entry import dispatch_if_native as _native_dispatch
_native_code = _native_dispatch('ios_dialog_probe', _here.parent)
if _native_code is not None:
    raise SystemExit(_native_code)

raise SystemExit('ios_dialog_probe requires native iOS source input')
