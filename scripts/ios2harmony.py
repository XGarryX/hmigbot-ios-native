#!/usr/bin/env python3
"""Location-independent entry point; works when the complete plugin is copied."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from hmigbot_ios.cli import main

if __name__ == "__main__":
    raise SystemExit(main())
