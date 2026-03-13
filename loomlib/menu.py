from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

from loomlib.theme import Theme, list_theme_names


def _run_rofi(lines: list[str], prompt: str) -> str | None:
    if shutil.which("rofi") is None:
        raise RuntimeError("rofi is not installed or not in PATH")

    cmd = ["rofi", "-dmenu", "-i", "-p", prompt]

    proc = subprocess.run(
        cmd,
        input="\n".join(lines),
        text=True,
        capture_output=True,
        check=False,
    )

    if proc.returncode != 0:
        return None

    selection = proc.stdout.strip()
    return selection or None


def choose_theme() -> str | None:
    return _run_rofi(list_theme_names(), "Theme")


def choose_wallpaper(theme: Theme) -> Path | None:
    wallpapers = theme.list_wallpapers()
    if not wallpapers:
        return None

    lines = [f"{p.name}\x00icon\x1f{p}" for p in wallpapers]

    if shutil.which("rofi") is None:
        raise RuntimeError("rofi is not installed or not in PATH")

    cmd = ["rofi", "-dmenu", "-i", "-show-icons", "-p", f"{theme.name} wallpaper"]

    proc = subprocess.run(
        cmd,
        input="\n".join(lines),
        text=True,
        capture_output=True,
        check=False,
    )

    if proc.returncode != 0:
        return None

    selection = proc.stdout.strip()
    if not selection:
        return None

    for path in wallpapers:
        if path.name == selection:
            return path

    return None


def choose_main_action() -> str | None:
    return _run_rofi(
        ["Apply Theme", "Change Wallpaper", "Reapply Current Theme"],
        "Loom",
    )
