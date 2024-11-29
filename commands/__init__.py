import os
from typing import Any
from . import init
from . import build
from . import config as cfg
from . import inject
from . import unravel
from . import watch
from . import lint
def do(command: str, config: dict, args: Any):
    """Execute the given command

    :param command: Name of the command
    :param config: program configuration
    :param args: arguments the script wath invoked with
    """
    if args.watch or config.get('watch'):
        wrapper = watch.watch
    else:
        wrapper = lambda cb, *x: cb

    match command:
        case 'init':
            init.init(config)
        case 'unravel':
            unravel.unravel(args.file, config)
        case 'config':
            cfg.config(os.environ['EDITOR'], config)
        case 'build':
            wrapper(build.build, config)(config)
        case 'inject':
            wrapper(inject.inject, config)(config)
        case 'lint':
            lint.lint()
        case 'update':
            raise NotImplementedError
