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
from hmigbot_ios152.cli import main
p=argparse.ArgumentParser(); p.add_argument('--source-dir',required=True); p.add_argument('--output-dir',default='spec/baseline/api-inventory'); p.add_argument('--project-root')
a=p.parse_args(); argv=['api','--src',a.source_dir,'--out',str(Path(a.output_dir)/'raw_apis.json')]
if a.project_root: argv+=['--project-root',a.project_root]
raise SystemExit(main(argv))
