from __future__ import annotations

from pathlib import Path


HOME = Path.home()

REPO_ROOT = Path(__file__).resolve().parent.parent
THEMES_DIR = REPO_ROOT / "themes"

XDG_CONFIG_HOME = HOME / ".config"
XDG_STATE_HOME = HOME / ".local" / "state"

LOOM_STATE_DIR = XDG_STATE_HOME / "loom"
LOOM_GENERATED_DIR = LOOM_STATE_DIR / "generated"

CURRENT_THEME_FILE = LOOM_STATE_DIR / "current_theme"
CURRENT_WALLPAPER_FILE = LOOM_STATE_DIR / "current_wallpaper"

VWM_THEME_PATH = LOOM_GENERATED_DIR / "vwm-theme.conf"
KITTY_THEME_PATH = LOOM_GENERATED_DIR / "kitty-theme.conf"
ROFI_THEME_PATH = LOOM_GENERATED_DIR / "rofi-theme.rasi"
NVIM_THEME_PATH = LOOM_GENERATED_DIR / "nvim-theme.lua"
DUNST_THEME_PATH = HOME / ".config" / "dunst" / "dunstrc"
PICOM_THEME_PATH = HOME / ".config" / "picom" / "picom.conf"
TMUX_THEME_PATH = LOOM_GENERATED_DIR / "tmux-theme.conf"
FZF_THEME_PATH = LOOM_GENERATED_DIR / "fzf-theme.sh"


def ensure_runtime_dirs() -> None:
    LOOM_STATE_DIR.mkdir(parents=True, exist_ok=True)
    LOOM_GENERATED_DIR.mkdir(parents=True, exist_ok=True)
    DUNST_THEME_PATH.parent.mkdir(parents=True, exist_ok=True)
    PICOM_THEME_PATH.parent.mkdir(parents=True, exist_ok=True)
