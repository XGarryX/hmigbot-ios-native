#!/usr/bin/env python3
"""Optional UI source adapters; writes only caller-project derived artifacts."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from hmigbot_ios.ui_wire_cli import main

if __name__ == '__main__':
    raise SystemExit(main())
