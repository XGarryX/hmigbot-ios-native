#!/bin/sh
set -eu
if [ "$#" -ne 1 ]; then printf '%s\n' 'Usage: sh install.sh /absolute/workspace' >&2; exit 2; fi
plugin_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
exec "${PYTHON:-python3}" "$plugin_dir/scripts/manage_install.py" install --workspace "$1"
