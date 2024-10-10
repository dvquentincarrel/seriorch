import argparse
import commands
from colors import *

parser = argparse.ArgumentParser(
    formatter_class=argparse.RawDescriptionHelpFormatter,
    description="Découpe et assemble des fichiers de data pour les web scanners"
)
parser.add_argument('-v', '--version', action='version', version='seriorch 1.0')
subparsers = parser.add_subparsers(dest="command", title="Commandes", help="commandes")

init_parser = subparsers.add_parser('init', help="Initialise un projet")
config_parser = subparsers.add_parser('config', help="Ouvre le fichier de config")
build_parser = subparsers.add_parser('build', help="Compose un fichier de data à partir de ses composants")
inject_parser = subparsers.add_parser('inject', help="Injecte les composants dans la base de données")

unravel_parser = subparsers.add_parser('unravel', help="Décompose un fichier de data en ses composants")
unravel_parser.add_argument('fichier', help="Fichier de data à décomposer")

update_parser = subparsers.add_parser('update', help=B(BRD("NIY: Met à jour un fichier de data avec les composants")))
update_parser.add_argument('fichier', help="Fichier de data à mettre à jour")

def parse_args(config: dict) -> argparse.Namespace:
    args = parser.parse_args()
    if 'fichier' in args:
        args.file = args.fichier
    commands.do(args.command, config, args)
    return args
