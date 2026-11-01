import re
import argparse
import sys
import shutil
import subprocess

from pathlib import Path
from dataclasses import dataclass

HOME_DIR        = Path.home()
VENV_NAME       = ".venv"

NAME_PATTERN    = re.compile(r"[A-Za-z0-9][A-Za-z0-9_-]*")
NAME_MARKER     = "__NAME__"

EXIT_OK         = 0
EXIT_FAIL       = 1
EXIT_USAGE      = 2

MAIN_TEMPLATE = """def main():
    print("Hello from __NAME__!")


if __name__ == "__main__":
    main()
"""

README_TEMPLATE = """# __NAME__

This README was Made with yap (yet another project)
"""

GITIGNORE_LINES = [
    "__pycache__/",
    "*.pyc",
    ".venv/",
    "venv/",
    ".env",
    "dist/",
    "build/",
    "*.egg-info/",
    ".pytest_cache/",
]

GITIGNORE_TEMPLATE = "\n".join(GITIGNORE_LINES) + "\n"

PYPROJECT_TEMPLATE = """[project]
name = "__NAME__"
version = "0.1.0"
requires-python = ">=3.10"
"""


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


def python_files(config: ProjectConfig) -> dict[str, str]:
    files = {
        "main.py": MAIN_TEMPLATE,
        "README.md": README_TEMPLATE,
        ".gitignore": GITIGNORE_TEMPLATE,
        "pyproject.toml": PYPROJECT_TEMPLATE,
    }
    return {p: t.replace(NAME_MARKER, config.name) for p, t in files.items()}


def write_files(target: Path, files: dict[str, str]) -> None:
    for rel_path, content in files.items():
        path = target / rel_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")


def run_command(args: list[str], cwd: Path) -> tuple[int, str, str]:
    result = subprocess.run(
        args,
        cwd=cwd,
        capture_output=True,
        text=True,
    )
    return result.returncode, result.stdout, result.stderr


def init_git(target: Path) -> None:
    if shutil.which("git") is None:
        print("Warning: git not found, skipping git init", file=sys.stderr)
        return

    code, _, error = run_command(["git", "init"], target)
    if code != EXIT_OK:
        print(f"git init failed: {error}", file=sys.stderr)
        sys.exit(EXIT_FAIL)


def create_venv(target: Path) -> None:
    # Use the interpreter running yap, never a guessed "python" from PATH.
    code, _, error = run_command([sys.executable, "-m", "venv", VENV_NAME], target)
    if code != EXIT_OK:
        print(f"Failed to create venv: {error}", file=sys.stderr)
        sys.exit(EXIT_FAIL)
