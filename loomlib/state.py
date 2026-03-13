from __future__ import annotations

from pathlib import Path

from loomlib.paths import (
    CURRENT_THEME_FILE,
    CURRENT_WALLPAPER_FILE,
    PREVIEW_ACTIVE_FILE,
    PREVIEW_ORIGINAL_THEME_FILE,
    PREVIEW_ORIGINAL_WALLPAPER_FILE,
    THEME_STATE_DIR,
    ensure_runtime_dirs,
)


def _theme_state_dir(theme_name: str) -> Path:
    return THEME_STATE_DIR / theme_name


def _theme_wallpaper_file(theme_name: str) -> Path:
    return _theme_state_dir(theme_name) / "current_wallpaper"


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
    p = Path(value)
    return p if p.is_file() else None


def write_theme_wallpaper(theme_name: str, wallpaper_path: Path) -> None:
    ensure_runtime_dirs()
    d = _theme_state_dir(theme_name)
    d.mkdir(parents=True, exist_ok=True)
    _theme_wallpaper_file(theme_name).write_text(str(wallpaper_path) + "\n", encoding="utf-8")


def read_theme_wallpaper(theme_name: str) -> Path | None:
    path = _theme_wallpaper_file(theme_name)
    if not path.is_file():
        return None
    value = path.read_text(encoding="utf-8").strip()
    if not value:
        return None
    p = Path(value)
    return p if p.is_file() else None


def begin_preview_state(theme_name: str | None, wallpaper: Path | None) -> None:
    ensure_runtime_dirs()

    if not PREVIEW_ACTIVE_FILE.exists():
        PREVIEW_ACTIVE_FILE.write_text("1\n", encoding="utf-8")

        if theme_name is not None:
            PREVIEW_ORIGINAL_THEME_FILE.write_text(theme_name + "\n", encoding="utf-8")

        if wallpaper is not None:
            PREVIEW_ORIGINAL_WALLPAPER_FILE.write_text(str(wallpaper) + "\n", encoding="utf-8")


def preview_is_active() -> bool:
    return PREVIEW_ACTIVE_FILE.exists()


def read_preview_theme() -> str | None:
    if not PREVIEW_ORIGINAL_THEME_FILE.is_file():
        return None
    value = PREVIEW_ORIGINAL_THEME_FILE.read_text(encoding="utf-8").strip()
    return value or None


def read_preview_wallpaper() -> Path | None:
    if not PREVIEW_ORIGINAL_WALLPAPER_FILE.is_file():
        return None
    value = PREVIEW_ORIGINAL_WALLPAPER_FILE.read_text(encoding="utf-8").strip()
    if not value:
        return None
    p = Path(value)
    return p if p.is_file() else None


def clear_preview_state() -> None:
    PREVIEW_ACTIVE_FILE.unlink(missing_ok=True)
    PREVIEW_ORIGINAL_THEME_FILE.unlink(missing_ok=True)
    PREVIEW_ORIGINAL_WALLPAPER_FILE.unlink(missing_ok=True)
