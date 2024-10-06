#!/bin/sh
serior_path=$(readlink -f "$0" | xargs dirname)
. "$serior_path/venv/bin/activate"
python "$serior_path/main.py" "$@"
