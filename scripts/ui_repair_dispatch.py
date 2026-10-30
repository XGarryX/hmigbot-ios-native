"""Project-scoped repair, root-cause triage and affected recheck entrypoint."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from hmigbot_ios.ui_repair_dispatch import main
raise SystemExit(main())
