"""Source-derived UI delivery CLI; same API as the public pipeline router."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from hmigbot_ios.ios_ui_delivery import main
raise SystemExit(main())
