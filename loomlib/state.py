from __future__ import annotations

from pathlib import Path

from loomlib.paths import CURRENT_THEME_FILE, CURRENT_WALLPAPER_FILE, ensure_runtime_dirs


def write_current_theme(theme_name: str) -> None:
    ensure_runtime_dirs()
    CURRENT_THEME_FILE.write_text(theme_name + "\n", encoding="utf-8")


def read_current_theme() -> str | None:
    if not CURRENT_THEME_FILE.is_file():
        return None
    value = CURRENT_THEME_FILE.read_text(encoding="utf-8").strip()
    return value or None


def write_current_wallpaper(wallpaper_path: Path) -> None:
    ensure_runtime_dirs()
    CURRENT_WALLPAPER_FILE.write_text(str(wallpaper_path) + "\n", encoding="utf-8")


def read_current_wallpaper() -> Path | None:
    if not CURRENT_WALLPAPER_FILE.is_file():
        return None
    value = CURRENT_WALLPAPER_FILE.read_text(encoding="utf-8").strip()
    if not value:
        return None
    return Path(value)
