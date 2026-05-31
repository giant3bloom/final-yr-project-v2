"""Project bootstrap — ensure imports work for `python -m` entry points."""
from __future__ import annotations

import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def bootstrap() -> Path:
    """Add project root to sys.path and set cwd. Returns project root."""
    root = str(PROJECT_ROOT)
    if root not in sys.path:
        sys.path.insert(0, root)
    os.chdir(PROJECT_ROOT)
    return PROJECT_ROOT
