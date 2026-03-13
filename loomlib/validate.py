from __future__ import annotations

from pathlib import Path
import re

from loomlib.derive import sanitize_theme_name
from loomlib.paths import (
    DUNST_THEME_PATH,
    FZF_THEME_PATH,
    GTK3_SETTINGS_PATH,
    GTK4_SETTINGS_PATH,
    KITTY_THEME_PATH,
    NVIM_THEME_PATH,
    PICOM_THEME_PATH,
    ROFI_THEME_PATH,
    SESSION_THEME_PATH,
    TMUX_THEME_PATH,
    VWM_THEME_PATH,
)
from loomlib.theme import IMAGE_EXTENSIONS, load_theme, list_theme_names

HEX_RE = re.compile(r"^#[0-9a-fA-F]{6}$")


def _check_color(name: str, value: str, errors: list[str], theme_name: str) -> None:
    if not HEX_RE.match(value):
        errors.append(f"{theme_name}: {name} invalid hex color '{value}'")


def _check_parent(path: Path, errors: list[str]) -> None:
    parent = path.parent
    if not parent.exists():
        errors.append(f"{path}: parent directory missing")
    elif not parent.is_dir():
        errors.append(f"{path}: parent is not a directory")


def validate_theme(theme_name: str) -> list[str]:
    errors: list[str] = []

    try:
        theme = load_theme(theme_name)
    except Exception as e:
        return [f"{theme_name}: {e}"]

    if sanitize_theme_name(theme.name) != theme.name:
        errors.append(f"{theme_name}: theme name should already be sanitized")

    if theme_name != theme.name:
        errors.append(f"{theme_name}: directory name and theme name do not match")

    for key in [
        "bg", "bg_alt", "fg", "fg_muted", "accent", "accent_fg",
        "border_active", "border_inactive", "workspace_current",
        "workspace_occupied", "workspace_empty", "selection_bg", "selection_fg",
        "color0", "color1", "color2", "color3", "color4", "color5", "color6", "color7",
        "color8", "color9", "color10", "color11", "color12", "color13", "color14", "color15",
    ]:
        _check_color(key, getattr(theme, key), errors, theme_name)

    if theme.ui_mode not in {"light", "dark"}:
        errors.append(f"{theme_name}: ui_mode must be 'light' or 'dark'")

    if not theme.wallpapers_dir.is_dir():
        errors.append(f"{theme_name}: wallpapers directory missing")

    wallpapers = theme.list_wallpapers()
    if not wallpapers:
        errors.append(f"{theme_name}: no wallpapers found")

    names_seen: set[str] = set()
    for p in wallpapers:
        if p.suffix.lower() not in IMAGE_EXTENSIONS:
            errors.append(f"{theme_name}: unsupported wallpaper extension: {p.name}")

        stem = p.stem.lower()
        if stem in names_seen:
            errors.append(f"{theme_name}: duplicate wallpaper basename detected: {stem}")
        names_seen.add(stem)

    try:
        _ = theme.default_wallpaper_path
    except Exception as e:
        errors.append(f"{theme_name}: default wallpaper invalid: {e}")

    if theme.nvim_scheme == "loom-custom" and theme.custom_palette() is None:
        errors.append(f"{theme_name}: nvim_scheme=loom-custom but custom palette is missing")

    if not (20 <= theme.rofi_width <= 100):
        errors.append(f"{theme_name}: rofi_width must be between 20 and 100")

    if not (0 < theme.terminal_opacity <= 1):
        errors.append(f"{theme_name}: terminal_opacity must be in (0, 1]")

    if not (0 < theme.picom_active_opacity <= 1):
        errors.append(f"{theme_name}: picom_active_opacity must be in (0, 1]")

    if not (0 < theme.picom_inactive_opacity <= 1):
        errors.append(f"{theme_name}: picom_inactive_opacity must be in (0, 1]")

    if theme.picom_corner_radius < 0:
        errors.append(f"{theme_name}: picom_corner_radius must be >= 0")

    if theme.picom_round_borders not in {0, 1}:
        errors.append(f"{theme_name}: picom_round_borders must be 0 or 1")

    if theme.border_width < 0:
        errors.append(f"{theme_name}: border_width must be >= 0")

    if theme.gap_px < 0:
        errors.append(f"{theme_name}: gap_px must be >= 0")

    if theme.bar_height <= 0:
        errors.append(f"{theme_name}: bar_height must be > 0")

    if theme.font_size_ui <= 0 or theme.font_size_term <= 0:
        errors.append(f"{theme_name}: font sizes must be > 0")

    return errors


def validate_outputs() -> list[str]:
    errors: list[str] = []
    for path in [
        VWM_THEME_PATH,
        KITTY_THEME_PATH,
        ROFI_THEME_PATH,
        NVIM_THEME_PATH,
        DUNST_THEME_PATH,
        PICOM_THEME_PATH,
        TMUX_THEME_PATH,
        FZF_THEME_PATH,
        SESSION_THEME_PATH,
        GTK3_SETTINGS_PATH,
        GTK4_SETTINGS_PATH,
    ]:
        _check_parent(path, errors)
    return errors


def validate_all_themes() -> list[str]:
    all_errors: list[str] = []
    names = list_theme_names()

    if len(names) != len(set(names)):
        all_errors.append("duplicate theme directories detected")

    for theme_name in names:
        all_errors.extend(validate_theme(theme_name))

    all_errors.extend(validate_outputs())
    return all_errors
