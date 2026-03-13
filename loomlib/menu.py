from __future__ import annotations

import os
import shlex
import shutil
import subprocess
import tempfile
from pathlib import Path

from loomlib.state import read_current_theme
from loomlib.theme import Theme, list_theme_names


def _run_rofi(lines: list[str], prompt: str, show_icons: bool = False) -> str | None:
    if shutil.which("rofi") is None:
        raise RuntimeError("rofi is not installed or not in PATH")

    cmd = ["rofi", "-dmenu", "-i", "-p", prompt]
    if show_icons:
        cmd.append("-show-icons")

    proc = subprocess.run(
        cmd,
        input="\n".join(lines),
        text=True,
        capture_output=True,
        check=False,
    )

    if proc.returncode != 0:
        return None

    value = proc.stdout.strip()
    return value or None


def _run_terminal_script(script_text: str, title: str = "loom") -> tuple[int, str]:
    with tempfile.TemporaryDirectory(prefix="loom-ui-") as td:
        td_path = Path(td)
        script_file = td_path / "run.sh"
        out_file = td_path / "out.txt"

        script_file.write_text(script_text, encoding="utf-8")
        script_file.chmod(0o755)

        env = os.environ.copy()
        env["LOOM_OUT_FILE"] = str(out_file)

        if env.get("TMUX"):
            proc = subprocess.run(
                [
                    "tmux",
                    "display-popup",
                    "-E",
                    "-w",
                    "92%",
                    "-h",
                    "92%",
                    str(script_file),
                ],
                env=env,
                check=False,
            )
        elif shutil.which("kitty") is not None:
            proc = subprocess.run(
                [
                    "kitty",
                    "--class",
                    "loom-ui",
                    "--title",
                    title,
                    "bash",
                    str(script_file),
                ],
                env=env,
                check=False,
            )
        elif shutil.which("xterm") is not None:
            proc = subprocess.run(
                [
                    "xterm",
                    "-T",
                    title,
                    "-e",
                    "bash",
                    str(script_file),
                ],
                env=env,
                check=False,
            )
        else:
            proc = subprocess.run(
                ["bash", str(script_file)],
                env=env,
                check=False,
            )

        output = ""
        if out_file.is_file():
            output = out_file.read_text(encoding="utf-8").strip()

        return proc.returncode, output


def choose_theme() -> str | None:
    return _run_rofi(list_theme_names(), "Theme")


def choose_main_action() -> str | None:
    current = read_current_theme() or "none"
    return _run_rofi(
        [
            "Apply Theme",
            "Change Wallpaper",
            "Preview Theme",
            "Revert Preview",
            "Derive Theme From Image",
            "Validate Themes",
            "Reapply Current Theme",
        ],
        f"Loom [{current}]",
    )


def prompt_text(prompt: str, placeholder: str = "") -> str | None:
    if shutil.which("rofi") is None:
        return None

    proc = subprocess.run(
        ["rofi", "-dmenu", "-p", prompt],
        input=placeholder,
        text=True,
        capture_output=True,
        check=False,
    )
    if proc.returncode != 0:
        return None

    value = proc.stdout.strip()
    return value or None


def choose_image_file() -> str | None:
    roots = [
        Path.home() / "Pictures",
        Path.home() / ".local/share/wallpapers",
        Path.home() / ".dotfiles/.local/share/wallpapers",
        Path.home() / "repos/loom/themes",
    ]

    existing_roots = [p for p in roots if p.exists()]
    if not existing_roots:
        existing_roots = [Path.home()]

    root_args = " ".join(shlex.quote(str(p)) for p in existing_roots)

    original_wallpaper = None
    current_wallpaper_file = Path.home() / ".local" / "state" / "loom" / "current_wallpaper"
    if current_wallpaper_file.is_file():
        value = current_wallpaper_file.read_text(encoding="utf-8").strip()
        if value:
            p = Path(value)
            if p.is_file():
                original_wallpaper = p

    restore_cmd = ":"
    if original_wallpaper is not None:
        restore_cmd = f'xwallpaper --zoom {shlex.quote(str(original_wallpaper))} >/dev/null 2>&1'

    script = f"""#!/usr/bin/env bash
set -euo pipefail

cleanup() {{
    {restore_cmd}
}}

trap cleanup INT TERM

find {root_args} -type f \\( \\
    -iname '*.png' -o -iname '*.jpg' -o -iname '*.jpeg' -o -iname '*.webp' -o \\
    -iname '*.gif' -o -iname '*.bmp' -o -iname '*.tiff' -o -iname '*.tif' -o -iname '*.avif' \\
\\) 2>/dev/null | sort | fzf \\
    --cycle \\
    --prompt='image> ' \\
    --delimiter='/' \\
    --with-nth=-1 \\
    --preview='
        file="{{}}";
        if command -v chafa >/dev/null 2>&1; then
            chafa -f symbols -s 80x24 "$file" 2>/dev/null || true;
            printf "\\n";
        fi;
        printf "%s\\n\\n" "$file";
        stat --printf="size: %s bytes\\nmodified: %y\\n" "$file" 2>/dev/null || true
    ' \\
    --preview-window='right:55%' \\
    --bind='focus:execute-silent(xwallpaper --zoom {{}} >/dev/null 2>&1)' \\
    --bind='esc:abort' > "$LOOM_OUT_FILE" || true
"""
    _, output = _run_terminal_script(script, title="Loom Image Picker")
    return output or None


def choose_wallpaper(theme: Theme, original_wallpaper: Path | None = None) -> Path | None:
    wallpapers = theme.list_wallpapers()
    if not wallpapers:
        return None

    restore_cmd = ""
    if original_wallpaper is not None and original_wallpaper.is_file():
        restore_cmd = f'xwallpaper --zoom {shlex.quote(str(original_wallpaper))} >/dev/null 2>&1'

    list_file_lines = "\n".join(str(p) for p in wallpapers)

    script = f"""#!/usr/bin/env bash
set -euo pipefail

cleanup() {{
    {"eval " + shlex.quote(restore_cmd) if restore_cmd else ":"}
}}

trap cleanup INT TERM

cat <<'EOF' | fzf \\
    --cycle \\
    --prompt={shlex.quote(theme.name + " wallpaper> ")} \\
    --delimiter='/' \\
    --with-nth=-1 \\
    --preview-window=hidden \\
    --bind='focus:execute-silent(xwallpaper --zoom {{}} >/dev/null 2>&1)' \\
    --bind='esc:abort' > "$LOOM_OUT_FILE" || true
{list_file_lines}
EOF
"""
    _, output = _run_terminal_script(script, title=f"Loom Wallpaper [{theme.name}]")
    if not output:
        return None

    p = Path(output)
    return p if p.is_file() else None


def show_text_report(title: str, text: str) -> None:
    text = text.rstrip() + "\\n"

    script = f"""#!/usr/bin/env bash
set -euo pipefail
cat <<'EOF' | ${{PAGER:-less}} -R
{text}EOF
"""
    _run_terminal_script(script, title=title)
