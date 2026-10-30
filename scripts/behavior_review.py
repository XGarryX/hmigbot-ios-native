"""Read-only replay of the selected settings/click effect review."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from hmigbot_ios.behavior_review import main
raise SystemExit(main())
