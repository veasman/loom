from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

from loomlib.state import write_current_wallpaper
from loomlib.theme import Theme


def set_wallpaper(path: Path) -> None:
    if not path.is_file():
        raise FileNotFoundError(f"wallpaper not found: {path}")

    if shutil.which("xwallpaper") is None:
        raise RuntimeError("xwallpaper is not installed or not in PATH")

    subprocess.run(["xwallpaper", "--zoom", str(path)], check=True)
    write_current_wallpaper(path)


def set_default_wallpaper(theme: Theme) -> Path:
    wallpaper = theme.default_wallpaper_path
    set_wallpaper(wallpaper)
    return wallpaper


def wallpaper_entries(theme: Theme) -> list[tuple[str, Path]]:
    entries: list[tuple[str, Path]] = []
    for path in theme.list_wallpapers():
        entries.append((path.name, path))
    return entries
