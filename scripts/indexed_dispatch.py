"""Public standalone entry for indexed host dispatch cooperation."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from hmigbot_ios.indexed_dispatch import main
raise SystemExit(main())
