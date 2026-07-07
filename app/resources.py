import os
import sys
from typing import Optional


def _base_dir() -> str:
    """Return the application base directory.

    - In a frozen/executable environment, use the executable location.
    - If running from a bundled internal executable (contains "_internal"),
      prefer the parent directory before "_internal" so resources live in the
      shared `Dados`/assets layout when packaged.
    - Otherwise, return the project root (two levels above this file).
    """
    frozen = getattr(sys, 'frozen', False)
    if frozen:
        executable_path = os.path.abspath(sys.executable)
        base_dir = os.path.dirname(executable_path)
        parts = base_dir.split(os.sep)
        lower = [p.lower() for p in parts]
        if '_internal' in lower:
            idx = lower.index('_internal')
            base_dir = os.sep.join(parts[:idx]) or os.sep
        return base_dir

    # development mode: two levels up from this file (SOFME/app/resources.py -> SOFME)
    return os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))


def get_resource_path(relative_path: str) -> str:
    """Return an absolute path to a resource inside the project layout.

    `relative_path` is a path relative to the project root, for example:
      'app/images/icons/home.ico'
    """
    base = _base_dir()
    return os.path.join(base, relative_path)


def icon_path(icon_name: str) -> str:
    return get_resource_path(os.path.join('app', 'images', 'icons', icon_name))


def style_path(style_relative: str) -> str:
    return get_resource_path(style_relative)


def data_path(filename: Optional[str] = None) -> str:
    """Return the shared data directory (SOFME/Dados) or a file inside it.

    Note: DatabaseManager is authoritative for database file layout; this helper
    only returns a predictable data folder for other assets.
    """
    base = _base_dir()
    data_dir = os.path.join(base, 'Dados')
    if filename:
        return os.path.join(data_dir, filename)
    return data_dir
