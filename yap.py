#!/usr/bin/env python3

import argparse
import re
import shlex
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

HOME_DIR        = Path.home()
VENV_NAME       = ".venv"
REQUIREMENTS    = "requirements.txt"

KIND_PYTHON     = "python"
KIND_WEB        = "web"

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

INDEX_HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>__NAME__</title>
    <link rel="icon" type="image/svg+xml" href="assets/favicon.svg">
    <link rel="stylesheet" href="css/style.css">
    <script src="js/main.js" defer></script>
</head>
<body>
    <h1>__NAME__</h1>
    <p>This page was made with yap</p>
</body>
</html>
"""

STYLE_CSS_TEMPLATE = """*,
*::before,
*::after {
    box-sizing: border-box;
}

body {
    margin: 0;
    padding: 2rem;
    font-family: system-ui, sans-serif;
    color: #1f2933;
}
"""

MAIN_JS_TEMPLATE = """console.log("__NAME__ is ready");
"""

FAVICON_SVG_TEMPLATE = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32">
    <circle cx="16" cy="16" r="14" fill="#3b82f6" />
</svg>
"""

WEB_README_TEMPLATE = README_TEMPLATE

WEB_GITIGNORE_TEMPLATE = """.DS_Store
node_modules/
.env
*.log
"""


@dataclass
class ProjectConfig:
    kind: str
    name: str
    parent: Path
    packages: list[str]


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="yap")
    sub = parser.add_subparsers(dest="kind", required=True)

    p_py = sub.add_parser(KIND_PYTHON)
    p_web = sub.add_parser(KIND_WEB)

    for p in (p_py, p_web):
        p.add_argument("name")
        p.add_argument("--path")
    p_py.add_argument("--add", nargs="+", default=[])

    return parser.parse_args(argv)


def validate_name(name: str) -> None:
    if NAME_PATTERN.fullmatch(name) is None:
        message = f"Name is not valid: '{name}' (use letters, numbers, _ or -)"
        print(message, file=sys.stderr)
        sys.exit(EXIT_USAGE)


def resolve_parent(path_arg: str | None) -> Path:
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


def web_files(config: ProjectConfig) -> dict[str, str]:
    files = {
        "index.html": INDEX_HTML_TEMPLATE,
        "css/style.css": STYLE_CSS_TEMPLATE,
        "js/main.js": MAIN_JS_TEMPLATE,
        "assets/favicon.svg": FAVICON_SVG_TEMPLATE,
        "assets/images/.gitkeep": "",
        "README.md": WEB_README_TEMPLATE,
        ".gitignore": WEB_GITIGNORE_TEMPLATE,
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
        check=False,  # the caller inspects the exit code
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


def venv_python(target: Path) -> Path:
    return target / VENV_NAME / "bin" / "python"


def install_packages(target: Path, packages: list[str]) -> None:
    # Calling the venv interpreter directly installs into that venv;
    # no "activate" step is needed.
    print(f"Installing: {' '.join(packages)}...")

    code, _, error = run_command(
        [str(venv_python(target)), "-m", "pip", "install", *packages],
        target,
    )
    if code != EXIT_OK:
        print(f"pip install failed:\n{error}", file=sys.stderr)
        sys.exit(EXIT_FAIL)

    code, output, error = run_command(
        [str(venv_python(target)), "-m", "pip", "freeze"],
        target,
    )
    if code != EXIT_OK:
        print(f"pip freeze failed: {error}", file=sys.stderr)
        sys.exit(EXIT_FAIL)

    (target / REQUIREMENTS).write_text(output, encoding="utf-8")


def show_next_steps(config: ProjectConfig, target: Path) -> None:
    # Quote the absolute path so copy-paste still works when it contains spaces.
    quoted = shlex.quote(str(target))

    print()
    print("and yet another project... To continue type:")
    if config.kind == KIND_PYTHON:
        print(f"cd {quoted} && source {VENV_NAME}/bin/activate")
    else:
        print(f"cd {quoted} && python -m http.server")
        print("Then open http://localhost:8000 in your browser")
    print("Happy Coding!")


def main() -> None:
    try:
        args = parse_args(sys.argv[1:])
        validate_name(args.name)
        config = ProjectConfig(
            kind=args.kind,
            name=args.name,
            parent=resolve_parent(args.path),
            packages=getattr(args, "add", []),
        )

        target = ensure_target(config)
        print(f"Creating {config.kind} project '{config.name}' in {target}...")

        if config.kind == KIND_PYTHON:
            files = python_files(config)
        else:
            files = web_files(config)

        write_files(target, files)
        init_git(target)

        if config.kind == KIND_PYTHON:
            create_venv(target)
            if config.packages:
                install_packages(target, config.packages)

        show_next_steps(config, target)
        sys.exit(EXIT_OK)
    except KeyboardInterrupt:
        print("Cancelled.", file=sys.stderr)
        sys.exit(EXIT_FAIL)


if __name__ == "__main__":
    main()
