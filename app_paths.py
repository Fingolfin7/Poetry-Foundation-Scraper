"""App path helpers.

Keeps file locations stable when running:
- from source (python gui_app.py)
- from a PyInstaller one-file executable

Contract:
- `get_runtime_dir()` returns the folder that contains the running program.
- `resource_path(rel)` finds packaged resources (icon, etc.) in both modes.
"""

from __future__ import annotations

import os
import sys


def get_runtime_dir() -> str:
    """Folder containing the running entry point (exe folder in frozen mode)."""
    if getattr(sys, "frozen", False):
        # In PyInstaller, sys.executable is the path to the exe.
        return os.path.dirname(os.path.abspath(sys.executable))
    # In source mode, use current working directory (more intuitive than __file__).
    return os.path.abspath(os.getcwd())


def resource_path(relative_path: str) -> str:
    """Resolve a relative resource path in both dev and PyInstaller modes."""
    base = getattr(sys, "_MEIPASS", None)
    if base:
        return os.path.join(base, relative_path)

    # Dev mode: paths are relative to repo root (this file lives at repo root)
    repo_root = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(repo_root, relative_path)

