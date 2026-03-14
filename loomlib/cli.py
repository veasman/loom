from __future__ import annotations

import argparse
import glob
import subprocess
import shlex
from pathlib import Path

from loomlib.menu import (
    choose_main_action,
    choose_theme,
    choose_wallpaper,
    choose_image_file,
    prompt_text,
    show_text_report,
)
from loomlib.derive import write_derived_theme
from loomlib.validate import validate_all_themes
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
    ensure_runtime_dirs,
)
from loomlib.renderers import (
    render_dunst_theme,
    render_fzf_theme,
    render_gtk_settings,
    render_kitty_theme,
    render_nvim_theme,
    render_picom_theme,
    render_rofi_theme,
    render_session_theme,
    render_tmux_theme,
    render_vwm_theme,
)
from loomlib.state import (
    begin_preview_state,
    clear_preview_state,
    preview_is_active,
    read_current_theme,
    read_current_wallpaper,
    read_preview_theme,
    read_preview_wallpaper,
    read_theme_wallpaper,
    write_current_theme,
)
from loomlib.theme import Theme, list_theme_names, load_theme
from loomlib.wallpaper import set_default_wallpaper, set_theme_wallpaper, set_wallpaper


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
    SESSION_THEME_PATH.write_text(render_session_theme(theme), encoding="utf-8")
    gtk_settings = render_gtk_settings(theme)
    GTK3_SETTINGS_PATH.write_text(gtk_settings, encoding="utf-8")
    GTK4_SETTINGS_PATH.write_text(gtk_settings, encoding="utf-8")

def notify_theme_applied(message: str) -> None:
    subprocess.run(
        [
            "bash",
            "-lc",
            f'command -v notify-send >/dev/null 2>&1 && notify-send "Loom" {shlex.quote(message)} || true',
        ],
        check=False,
    )


def validate_themes() -> int:
    errors = validate_all_themes()
    if not errors:
        print("all themes valid")
        return 0

    for err in errors:
        print(err)
    return 1


def derive_theme(image_path: str, theme_name: str) -> int:
    root = write_derived_theme(Path(image_path).expanduser().resolve(), theme_name)
    print(f"derived theme created: {root}")
    return 0


def preview_theme(theme_name: str) -> int:
    begin_preview_state(read_current_theme(), read_current_wallpaper())
    return apply_theme(theme_name)


def revert_preview() -> int:
    prev_theme = read_preview_theme()
    prev_wallpaper = read_preview_wallpaper()

    if not prev_theme:
        print("no preview state saved")
        return 1

    result = apply_theme(prev_theme, wallpaper=prev_wallpaper)
    clear_preview_state()
    return result

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
        try:
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
                timeout=1.5,
            )
        except subprocess.TimeoutExpired:
            try:
                Path(socket).unlink(missing_ok=True)
            except OSError:
                pass
            continue

        if probe.returncode != 0:
            try:
                Path(socket).unlink(missing_ok=True)
            except OSError:
                pass
            continue

        try:
            subprocess.run(
                [
                    "nvim",
                    "--server",
                    socket,
                    "--remote-send",
                    "<Esc>:silent! LoomReloadTheme<CR>",
                ],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=False,
                timeout=1.5,
            )
        except subprocess.TimeoutExpired:
            continue


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


def resolve_theme_wallpaper(theme: Theme) -> Path:
    saved = read_theme_wallpaper(theme.name)
    if saved is not None and saved.is_file():
        return saved
    return theme.default_wallpaper_path


def apply_theme(theme_name: str, wallpaper: Path | None = None) -> int:
    theme = load_theme(theme_name)

    write_generated_files(theme)
    write_current_theme(theme.name)

    if wallpaper is not None:
        set_theme_wallpaper(theme, wallpaper)
    else:
        set_theme_wallpaper(theme, resolve_theme_wallpaper(theme))

    apply_runtime_reloads()
    notify_theme_applied(f"Applied theme: {theme.name}")

    print(f"applied theme: {theme.name}")
    return 0


def apply_theme_with_picker(theme_name: str) -> int:
    theme = load_theme(theme_name)

    write_generated_files(theme)
    write_current_theme(theme.name)

    # Apply theme first so wallpaper choice happens in the real final theme context.
    apply_runtime_reloads()

    chosen = choose_wallpaper(theme, original_wallpaper=read_current_wallpaper())
    if chosen is not None:
        set_theme_wallpaper(theme, chosen)
    else:
        set_theme_wallpaper(theme, resolve_theme_wallpaper(theme))

    notify_theme_applied(f"Applied theme: {theme.name}")
    print(f"applied theme: {theme.name}")
    return 0


def change_wallpaper_for_theme(theme_name: str) -> int:
    theme = load_theme(theme_name)
    original_wallpaper = read_current_wallpaper()

    chosen = choose_wallpaper(theme, original_wallpaper=original_wallpaper)
    if chosen is None:
        if original_wallpaper is not None and original_wallpaper.is_file():
            set_wallpaper(original_wallpaper)
        return 1

    set_theme_wallpaper(theme, chosen)
    notify_theme_applied(f"Applied wallpaper for {theme.name}: {chosen.name}")
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

    if action == "Preview Theme":
        theme_name = choose_theme()
        if theme_name is None:
            return 1
        return preview_theme(theme_name)

    if action == "Revert Preview":
        return revert_preview()

    if action == "Derive Theme From Image":
        image_path = choose_image_file()
        if image_path is None:
            return 1

        theme_name = prompt_text("Theme Name", "custom")
        if theme_name is None:
            return 1

        result = derive_theme(image_path, theme_name)
        if result != 0:
            return result

        return apply_theme_with_picker(theme_name)

    if action == "Validate Themes":
        errors = validate_all_themes()
        if not errors:
            show_text_report("Loom Validate", "all themes valid")
            return 0

        show_text_report("Loom Validate", "\n".join(errors))
        return 1

    if action == "Reapply Current Theme":
        return reapply_current_theme()

    return 1


def status() -> int:
    current = read_current_theme()
    wallpaper = read_current_wallpaper()
    preview = preview_is_active()

    print(f"theme: {current or 'none'}")
    print(f"wallpaper: {wallpaper if wallpaper else 'none'}")
    print(f"preview_active: {'yes' if preview else 'no'}")
    return 0


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

    p_preview = sub.add_parser("preview")
    p_preview.add_argument("theme")

    sub.add_parser("revert")
    sub.add_parser("validate")

    p_derive = sub.add_parser("derive")
    p_derive.add_argument("image")
    p_derive.add_argument("--name", required=True)

    args = parser.parse_args()

    if args.command == "list":
        for name in list_theme_names():
            print(name)
        return 0

    if args.command == "menu":
        return open_menu()

    if args.command == "status":
        return status()

    if args.command == "reapply":
        return reapply_current_theme()

    if args.command == "apply":
        return apply_theme(args.theme)

    if args.command == "wallpaper":
        return change_wallpaper_for_theme(args.theme)

    if args.command == "preview":
        return preview_theme(args.theme)

    if args.command == "revert":
        return revert_preview()

    if args.command == "validate":
        return validate_themes()

    if args.command == "derive":
        return derive_theme(args.image, args.name)

    return 1
