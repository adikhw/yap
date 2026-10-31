import re
import argparse
import sys

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


def validate_name(name):
    if NAME_PATTERN.fullmatch(name) is None:
        print(f"Name is not valid: '{name}' (use letters, numbers, _ or -)", file=sys.stderr)
        sys.exit(EXIT_USAGE)


def resolve_parent(path_arg):
    if not path_arg:
        return HOME_DIR
    path = Path(path_arg).expanduser()

    if not path.is_absolute():
        path = HOME_DIR / path
    return path.resolve()


def target_dir(config: ProjectConfig) -> Path:
    return config.parent / config.name


def ensure_target(config: ProjectConfig) -> Path:
    target = target_dir(config)

    if target.exists() or target.is_symlink():
        print(f"Folder already exists: {target}", file=sys.stderr)
        sys.exit(EXIT_FAIL)

    try:
        target.mkdir(parents=True, exist_ok=False)
    except OSError as e:
        print(f"Cannot create: {target}: {e}", file=sys.stderr)
        sys.exit(EXIT_FAIL)

    return target
