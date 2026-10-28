#!/usr/bin/env python3
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from hmigbot_ios152.native_visual import main
raise SystemExit(main())
