#!/bin/bash
# Keep the original CLI; HDC transport status alone is not a remote result.
exec python3 -B "$(dirname "$0")/cold_start_probe.py" "$@"
