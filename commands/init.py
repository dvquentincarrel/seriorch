"""Initializes a project"""

import os
import subprocess
from typing import Any

def init(config: Any) -> None:
    """
    - creates a git repo and its gitignore
    - pastes in the skeleton template
    - creates the symlink location
    """
    with open('skeleton.yaml', 'w') as file:
        config['yaml_dump'](config['skeleton_template'], file)

    os.symlink(os.path.expanduser(config['default_destination']), 'location')
    subprocess.run(['git','init'])
    with open('.gitignore', 'w') as file:
        file.write(f"{config['build_name']}\nruff.toml\nlocation")

    with open('ruff.toml', 'w') as file:
        file.write(f"builtins = {config.get('builtins')}\n")

    subprocess.run(['git','add', '.'])
    subprocess.run(['git','commit', '-m', 'init'])
