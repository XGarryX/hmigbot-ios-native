# Mac bundle-layout adapter: forward to the same package's canonical entry.
import sys
if sys.path and sys.path[0].rstrip('/').endswith('/_entry.dist'):
    sys.path.pop(0)
import os
_target = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../../../../a2h-execute/scripts/hit_test_gate.py'))
if not os.path.isfile(_target):
    sys.stderr.write('Bundled canonical entry missing: ' + _target + '\n')
    raise SystemExit(2)
os.execv(sys.executable, [sys.executable, _target, *sys.argv[1:]])
