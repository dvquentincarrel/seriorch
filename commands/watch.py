from time import sleep
from typing import Any
import inotify.adapters

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
                if 'IN_CLOSE_WRITE' in type_names and filename != config['build_name']:
                    print(f"{filename} modifié")
                    sleep(0.1) # Certains éditeurs recréent un inode à chaque écriture. Permet d'attendre que le fichier soit recréé
                    command(*args, **kwargs)
        except KeyboardInterrupt:
            pass
    return wrapper
