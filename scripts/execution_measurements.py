"""Project-local full-flow measurement entry point."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from hmigbot_ios.execution_measurements import main
raise SystemExit(main())
