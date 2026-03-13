from __future__ import annotations

import argparse
import glob
import subprocess
from pathlib import Path

from loomlib.menu import choose_main_action, choose_theme, choose_wallpaper
from loomlib.paths import (
    DUNST_THEME_PATH,
    FZF_THEME_PATH,
    KITTY_THEME_PATH,
    NVIM_THEME_PATH,
    PICOM_THEME_PATH,
    ROFI_THEME_PATH,
    TMUX_THEME_PATH,
    VWM_THEME_PATH,
    ensure_runtime_dirs,
)
from loomlib.renderers import (
    render_dunst_theme,
    render_fzf_theme,
    render_kitty_theme,
    render_nvim_theme,
    render_picom_theme,
    render_rofi_theme,
    render_tmux_theme,
    render_vwm_theme,
)
from loomlib.state import (
    read_current_theme,
    read_current_wallpaper,
    write_current_theme,
)
from loomlib.theme import Theme, list_theme_names, load_theme
from loomlib.wallpaper import set_default_wallpaper, set_wallpaper


def write_generated_files(theme: Theme) -> None:
    ensure_runtime_dirs()

    VWM_THEME_PATH.write_text(render_vwm_theme(theme), encoding="utf-8")
    KITTY_THEME_PATH.write_text(render_kitty_theme(theme), encoding="utf-8")
    ROFI_THEME_PATH.write_text(render_rofi_theme(theme), encoding="utf-8")
    NVIM_THEME_PATH.write_text(render_nvim_theme(theme), encoding="utf-8")
    DUNST_THEME_PATH.write_text(render_dunst_theme(theme), encoding="utf-8")
    PICOM_THEME_PATH.write_text(render_picom_theme(theme), encoding="utf-8")
    TMUX_THEME_PATH.write_text(render_tmux_theme(theme), encoding="utf-8")
    FZF_THEME_PATH.write_text(render_fzf_theme(theme), encoding="utf-8")


def reload_vwm() -> None:
    subprocess.run(
        ["bash", "-lc", 'pidof vwm >/dev/null && kill -HUP "$(pidof vwm)"'],
        check=False,
    )


def reload_kitty() -> None:
    subprocess.run(
        ["bash", "-lc", 'pidof kitty >/dev/null 2>&1 && pkill -USR1 -x kitty || true'],
        check=False,
    )


def reload_nvim_sessions() -> None:
    sockets = sorted(glob.glob("/tmp/nvim-loom-*.sock"))
    if not sockets:
        return

    for socket in sockets:
        probe = subprocess.run(
            [
                "nvim",
                "--server",
                socket,
                "--remote-expr",
                "1",
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
        )

        if probe.returncode != 0:
            try:
                Path(socket).unlink(missing_ok=True)
            except OSError:
                pass
            continue

        subprocess.run(
            [
                "nvim",
                "--server",
                socket,
                "--remote-send",
                "<Esc>:LoomReloadTheme<CR>",
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
        )


def reload_dunst() -> None:
    subprocess.run(
        ["bash", "-lc", 'pidof dunst >/dev/null 2>&1 && pkill -HUP -x dunst || true'],
        check=False,
    )


def reload_picom() -> None:
    subprocess.run(
        ["bash", "-lc", 'pidof picom >/dev/null 2>&1 && pkill -USR1 -x picom || true'],
        check=False,
    )

def reload_tmux() -> None:
    subprocess.run(
        [
            "bash",
            "-lc",
            'tmux source-file ~/.local/state/loom/generated/tmux-theme.conf >/dev/null 2>&1 || true',
        ],
        check=False,
    )

def apply_runtime_reloads() -> None:
    reload_vwm()
    reload_kitty()
    reload_dunst()
    reload_picom()
    reload_tmux()
    reload_nvim_sessions()


def apply_theme(theme_name: str, wallpaper: Path | None = None) -> int:
    theme = load_theme(theme_name)

    write_generated_files(theme)
    write_current_theme(theme.name)

    if wallpaper is not None:
        set_wallpaper(wallpaper)
    else:
        set_default_wallpaper(theme)

    apply_runtime_reloads()

    print(f"applied theme: {theme.name}")
    return 0


def apply_theme_with_picker(theme_name: str) -> int:
    theme = load_theme(theme_name)

    write_generated_files(theme)
    write_current_theme(theme.name)

    chosen = choose_wallpaper(theme)
    if chosen is not None:
        set_wallpaper(chosen)
    else:
        set_default_wallpaper(theme)

    apply_runtime_reloads()

    print(f"applied theme: {theme.name}")
    return 0


def change_wallpaper_for_theme(theme_name: str) -> int:
    theme = load_theme(theme_name)
    chosen = choose_wallpaper(theme)
    if chosen is None:
        return 1

    set_wallpaper(chosen)
    print(f"set wallpaper: {chosen}")
    return 0


def reapply_current_theme() -> int:
    current = read_current_theme()
    if not current:
        print("no current theme set")
        return 1

    wallpaper = read_current_wallpaper()
    return apply_theme(current, wallpaper=wallpaper)


def open_menu() -> int:
    action = choose_main_action()
    if action is None:
        return 1

    if action == "Apply Theme":
        theme_name = choose_theme()
        if theme_name is None:
            return 1
        return apply_theme_with_picker(theme_name)

    if action == "Change Wallpaper":
        current = read_current_theme()
        if not current:
            theme_name = choose_theme()
            if theme_name is None:
                return 1
        else:
            theme_name = current
        return change_wallpaper_for_theme(theme_name)

    if action == "Reapply Current Theme":
        return reapply_current_theme()

    return 1


def main() -> int:
    parser = argparse.ArgumentParser(prog="loom")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("list")
    sub.add_parser("menu")
    sub.add_parser("status")
    sub.add_parser("reapply")

    p_apply = sub.add_parser("apply")
    p_apply.add_argument("theme")

    p_wallpaper = sub.add_parser("wallpaper")
    p_wallpaper.add_argument("theme")

    args = parser.parse_args()

    if args.command == "list":
        for name in list_theme_names():
            print(name)
        return 0

    if args.command == "menu":
        return open_menu()

    if args.command == "status":
        current = read_current_theme()
        print(current if current else "no theme set")
        return 0

    if args.command == "reapply":
        return reapply_current_theme()

    if args.command == "apply":
        return apply_theme(args.theme)

    if args.command == "wallpaper":
        return change_wallpaper_for_theme(args.theme)

    return 1
