"""Opens configuration file"""

import subprocess

def config(editor: str, config: dict) -> None:
    subprocess.run([editor, config['config_file']])
