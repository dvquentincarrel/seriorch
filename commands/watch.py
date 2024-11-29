from time import sleep
from typing import Any
import re
import os
import inotify.adapters

# Some editors recreate an inode for every write. This helps ensure only the correct
# files trigger the command (temporary files are usually not named like regular files)
END_EXT_RE = re.compile('\.(xml|css|py|yaml)$')

def watch(command, config, *args, **kwargs):
    """Watch the dir for file writes. Executes the command on file save

    :param command: Callback to the command to execute
    """
    def wrapper(*args, **kwargs):
        i = inotify.adapters.Inotify()
        i.add_watch('.')


        try:
            for event in i.event_gen(yield_nones=False):
                (_, type_names, path, filename) = event
                if ('IN_CLOSE_WRITE' in type_names 
                    and filename != config['build_name']
                    and END_EXT_RE.search(filename)
                ):
                    # Process' group and and its stdout's group differ if run in brackground
                    if os.getpgrp() == os.tcgetpgrp(1):
                        print(f"{filename} modifié")
                    command(*args, **kwargs)
        except KeyboardInterrupt:
            pass
    return wrapper
