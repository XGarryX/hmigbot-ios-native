"""Selected Mac ARM writeback chain, adapted from Garry ios.32; no implicit xattr."""
from pathlib import Path
import sys
here=Path(__file__).resolve()
root=next(parent for parent in here.parents if (parent/'src/hmigbot_ios/native_writeback.py').is_file())
sys.path.insert(0,str(root/'src'))
from hmigbot_ios.native_writeback import chain_main
from hmigbot_ios.core import MigrationError
try:
    raise SystemExit(chain_main(here,sys.argv[1:]))
except (MigrationError,OSError,ValueError,TypeError) as exc:
    print('Selected writeback chain rejected: '+str(exc),file=sys.stderr)
    raise SystemExit(2)
