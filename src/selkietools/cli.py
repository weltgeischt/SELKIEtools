import os
import sys
import runpy
import argparse
from pathlib import Path
from selkietools.scripts_registry import SCRIPTS

PACKAGE_DIR = Path(__file__).resolve().parent

def main():
    parser = argparse.ArgumentParser(prog='selkie')
    subparsers = parser.add_subparsers(dest='subcommand', required=True)
    for name in SCRIPTS:
        subparsers.add_parser(name, add_help=False)

    args, remaining_args = parser.parse_known_args()

    #script_path = PACKAGE_DIR / SCRIPTS[args.subcommand]
    script_path = PACKAGE_DIR / SCRIPTS[args.subcommand]['path']
    sys.argv = [str(script_path)] + remaining_args
    runpy.run_path(str(script_path), run_name='__main__')

if __name__ == '__main__':
    main()
