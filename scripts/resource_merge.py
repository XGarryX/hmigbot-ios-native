#!/usr/bin/env python3
"""Submit task-owned resource deltas and run the single indexed-stage merge."""
from pathlib import Path
import sys

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from hmigbot_ios.resource_merge import main

if __name__=='__main__':
    raise SystemExit(main())
