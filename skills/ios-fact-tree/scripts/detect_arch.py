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
import argparse,json,re
from hmigbot_ios152.source import Source,entrypoints
p=argparse.ArgumentParser(); p.add_argument('src'); p.add_argument('--json',action='store_true'); a=p.parse_args()
source=Source(a.src); swift=[]; uikit=[]
for name in sorted(source.files):
    code=source.code(name)
    if re.search(r'\bimport\s+SwiftUI\b|\bNavigationStack\b|:\s*View\b',code): swift.append(name)
    if re.search(r'\b(?:UIKit|UIViewController|UIHostingController|UIViewRepresentable|UIViewControllerRepresentable)\b',code): uikit.append(name)
arch='hybrid' if swift and uikit else 'pure_compose' if swift else 'pure_traditional'
entries=entrypoints(source)
print(json.dumps({'arch':arch,'architecture':arch,'source_platform':'ios','frameworks':{'SwiftUI':swift,'UIKit':uikit},
 'launcher_short':entries[0]['short'] if entries else None,'launcher_arch':'compose' if swift else 'xml',
 'compose_screen_ratio':1 if swift and not uikit else 0 if not swift else .5,
 'wire_labels':{'pure_compose':'SwiftUI','pure_traditional':'UIKit/IB','hybrid':'mixed native UI'}},ensure_ascii=False,indent=2))
