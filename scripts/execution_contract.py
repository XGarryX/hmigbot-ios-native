"""Public indexed execution handoff, using the one maintained package."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from hmigbot_ios.execution_bridge import main
raise SystemExit(main())
