#!/usr/bin/env python3
"""Optional official app-scoped XCUITest capture/replay entrypoint."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from hmigbot_ios.ios_ui_automation import main

if __name__ == '__main__':
    raise SystemExit(main())
