import os
from typing import Any
from . import init
def do(command: str, config: dict, args: Any):
    """Execute the given command

    :param command: Name of the command
    :param config: program configuration
    """
    match command:
        case 'init':
            init.init(config)
