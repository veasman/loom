from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

from loomlib.paths import CURRENT_WALLPAPER_LINK
from loomlib.state import write_current_wallpaper, write_theme_wallpaper
from loomlib.theme import Theme


def set_wallpaper(path: Path) -> None:
    if not path.is_file():
        raise FileNotFoundError(f"wallpaper not found: {path}")

    if shutil.which("xwallpaper") is None:
        raise RuntimeError("xwallpaper is not installed or not in PATH")

    CURRENT_WALLPAPER_LINK.unlink(missing_ok=True)
    CURRENT_WALLPAPER_LINK.symlink_to(path)

    subprocess.run(["xwallpaper", "--zoom", str(path)], check=True)
    write_current_wallpaper(path)


def set_default_wallpaper(theme: Theme) -> Path:
    wallpaper = theme.default_wallpaper_path
    set_wallpaper(wallpaper)
    write_theme_wallpaper(theme.name, wallpaper)
    return wallpaper


def set_theme_wallpaper(theme: Theme, wallpaper: Path) -> None:
    set_wallpaper(wallpaper)
    write_theme_wallpaper(theme.name, wallpaper)


def wallpaper_entries(theme: Theme) -> list[tuple[str, Path]]:
    entries: list[tuple[str, Path]] = []
    for path in theme.list_wallpapers():
        entries.append((path.name, path))
    return entries
