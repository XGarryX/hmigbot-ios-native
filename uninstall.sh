#!/usr/bin/env bash
set -eu
python3 "$(dirname "$0")/scripts/manage_install.py" uninstall --workspace "${1:-.}"
