"""Lints xml and python files"""

import subprocess

def lint(*args, **kwargs) -> None:
    """Lints the xml and python files"""
    subprocess.run('ruff check *.py', shell=True)
    subprocess.run('xmllint --noout *.xml', shell=True)
