#!/bin/bash
# Review existing, scoped CLI startup evidence. No device or UI operations.
# Usage: cold_start_probe.sh <bundle> --pid N --started-at ISO --ended-at ISO \
#          --process-evidence process.json --log startup.log [--network-scenario NAME]
set -eu
SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
exec "${PYTHON:-python3}" - "$SCRIPT_DIR" "$@" <<'PY'
import json
from pathlib import Path
import sys
skill = Path(sys.argv[1]).resolve().parent
config = skill / 'runtime.json'
runtime = (skill / json.loads(config.read_text())['runtime_relative']).resolve() if config.is_file() else skill.parents[1]
sys.path.insert(0, str(runtime / 'src'))
from hmigbot_ios.cold_start_evidence import main
raise SystemExit(main(sys.argv[2:]))
PY
