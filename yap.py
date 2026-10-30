import re
import argparse

from pathlib import Path
from dataclasses import dataclass

HOME_DIR        = Path.home()
VENV_NAME       = ".venv"
NAME_PATTERN    = re.compile(r"[A-Za-z0-9][A-Za-z0-9_-]*")
NAME_MARKER     = "__NAME__"
EXIT_OK         = 0
EXIT_FAIL       = 1
EXIT_USAGE      = 2

@dataclass
class ProjectConfig:
    kind: str
    name: str
    parent: Path
    packages: list[str]

def parse_args(argv):
    parser = argparse.ArgumentParser(prog="yap")
    sub = parser.add_subparsers(dest="kind", required=True)

    p_py = sub.add_parser("python")
    p_web = sub.add_parser("web")

    for p in (p_py, p_web):
        p.add_argument("name")
        p.add_argument("--path")
    p_py.add_argument("--add", nargs="+", default=[])

    return parser.parse_args(argv)

