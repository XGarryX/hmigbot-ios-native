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
from hmigbot_ios152.source import ios_source
p=argparse.ArgumentParser(); p.add_argument('--ios-project',dest='source_project'); p.add_argument('--android-project',dest='source_project',help=argparse.SUPPRESS); p.add_argument('--out',required=True)
a=p.parse_args()
if not a.source_project: p.error('--ios-project is required')
if ios_source(a.source_project):
    print('iOS 样式读取 Asset Catalog、UIKit appearance 与 SwiftUI environment；无层叠 XML 主题，按原规程继续样式分析。'); raise SystemExit(2)
import subprocess
raise SystemExit(subprocess.run([sys.executable,str(_here.with_name('_upstream_resolve_theme.py')),*sys.argv[1:]]).returncode)
