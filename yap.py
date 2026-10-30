import re

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

