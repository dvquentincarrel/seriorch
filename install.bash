#!/bin/bash
if ! [ -d  venv ]; then
    printf '===== \x1b[33mCreating venv\x1b[m =====\n'
    py_exec=$(which python3 python 2>/dev/null | head -n1)
    $py_exec -m venv venv
    . venv/bin/activate
    printf '===== \x1b[33mInstalling pip packages\x1b[m =====\n'
    pip install -r requirements.txt
fi

if ! [ -e  ~/.local/bin/serior ]; then
    printf '===== \x1b[33mInstalling serior\x1b[m =====\n'
    mkdir -p ~/.local/bin
    ln -vs "$PWD"/serior.sh ~/.local/bin/serior
fi

printf ' \n\x1b[32mInstallation done\x1b[m\n'
