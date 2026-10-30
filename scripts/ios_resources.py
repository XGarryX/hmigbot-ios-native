"""Source resource operations; merge outputs through the original execute stage."""
from pathlib import Path
import argparse, json, sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from hmigbot_ios.atoms import run_atom
from hmigbot_ios.core import MigrationError
p=argparse.ArgumentParser(); p.add_argument('operation',choices=['asset-inventory','asset-convert','localization-inventory','localization-convert'])
p.add_argument('--src',type=Path,required=True); p.add_argument('--out',type=Path,required=True); p.add_argument('--default-locale')
a=p.parse_args()
try:
    value=run_atom(a.operation,a.src,a.out,default_locale=a.default_locale)
    print(json.dumps({'status':value['status'],'issues':value['issues'],'output':str(a.out)},ensure_ascii=False)); raise SystemExit(0)
except (MigrationError,OSError,ValueError) as exc: print(str(exc),file=sys.stderr); raise SystemExit(3)
