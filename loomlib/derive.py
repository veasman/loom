from __future__ import annotations

import re
from pathlib import Path
from shutil import copy2
from PIL import Image

from loomlib.paths import THEMES_DIR


VALID_THEME_RE = re.compile(r"^[a-z0-9][a-z0-9_-]*$")


def sanitize_theme_name(value: str) -> str:
    raw = value.strip().lower()
    raw = raw.replace(" ", "-")
    raw = re.sub(r"[^a-z0-9_-]+", "-", raw)
    raw = re.sub(r"-{2,}", "-", raw)
    raw = raw.strip("-_")
    return raw


def validate_new_theme_name(value: str) -> str:
    name = sanitize_theme_name(value)
    if not name:
        raise ValueError("theme name is empty after sanitization")
    if not VALID_THEME_RE.match(name):
        raise ValueError(f"invalid theme name: {value!r}")
    if (THEMES_DIR / name).exists():
        raise ValueError(f"theme already exists: {name}")
    return name


def _hex(rgb: tuple[int, int, int]) -> str:
    return "#{:02x}{:02x}{:02x}".format(*rgb)


def _clamp(v: int) -> int:
    return max(0, min(255, v))


def _adjust(rgb: tuple[int, int, int], amt: int) -> tuple[int, int, int]:
    return tuple(_clamp(c + amt) for c in rgb)


def _brightness(rgb: tuple[int, int, int]) -> float:
    r, g, b = rgb
    return (0.299 * r + 0.587 * g + 0.114 * b)


def extract_palette(image_path: Path) -> dict[str, str]:
    img = Image.open(image_path).convert("RGB")
    img = img.resize((200, 200))
    paletted = img.quantize(colors=8, method=Image.Quantize.MEDIANCUT)
    palette = paletted.getpalette()
    counts = sorted(paletted.getcolors(), reverse=True)

    colors: list[tuple[int, int, int]] = []
    for count, idx in counts[:8]:
        base = idx * 3
        colors.append((palette[base], palette[base + 1], palette[base + 2]))

    if not colors:
        colors = [(30, 30, 30), (220, 220, 220), (120, 160, 220)]

    bg_rgb = colors[0]
    accent_rgb = colors[1] if len(colors) > 1 else _adjust(bg_rgb, 40)

    light_mode = _brightness(bg_rgb) > 140
    fg_rgb = (40, 40, 40) if light_mode else (230, 230, 230)
    fg_muted_rgb = (100, 100, 100) if light_mode else (150, 150, 150)
    bg_alt_rgb = _adjust(bg_rgb, -12 if light_mode else 12)
    selection_bg_rgb = _adjust(accent_rgb, 18 if light_mode else -18)
    selection_fg_rgb = (20, 20, 20) if _brightness(selection_bg_rgb) > 150 else (255, 255, 255)
    border_inactive_rgb = _adjust(bg_rgb, -24 if light_mode else 24)

    color0 = _hex(bg_alt_rgb)
    color1 = _hex(_adjust(accent_rgb, 20))
    color2 = _hex(_adjust(accent_rgb, -20))
    color3 = _hex(_adjust(accent_rgb, 35))
    color4 = _hex(accent_rgb)
    color5 = _hex(_adjust(accent_rgb, 55))
    color6 = _hex(_adjust(accent_rgb, -35))
    color7 = _hex(fg_muted_rgb)
    color8 = _hex(_adjust(bg_alt_rgb, 20 if light_mode else 30))
    color9 = _hex(_adjust(accent_rgb, 35))
    color10 = _hex(_adjust(accent_rgb, -5))
    color11 = _hex(_adjust(accent_rgb, 50))
    color12 = _hex(_adjust(accent_rgb, 15))
    color13 = _hex(_adjust(accent_rgb, 65))
    color14 = _hex(_adjust(accent_rgb, -15))
    color15 = _hex(fg_rgb)

    return {
        "ui_mode": "light" if light_mode else "dark",
        "bg": _hex(bg_rgb),
        "bg_alt": _hex(bg_alt_rgb),
        "fg": _hex(fg_rgb),
        "fg_muted": _hex(fg_muted_rgb),
        "accent": _hex(accent_rgb),
        "accent_fg": _hex((255, 255, 255) if _brightness(accent_rgb) < 150 else (20, 20, 20)),
        "border_active": _hex(accent_rgb),
        "border_inactive": _hex(border_inactive_rgb),
        "workspace_current": _hex(accent_rgb),
        "workspace_occupied": _hex(fg_muted_rgb),
        "workspace_empty": _hex(border_inactive_rgb),
        "selection_bg": _hex(selection_bg_rgb),
        "selection_fg": _hex(selection_fg_rgb),
        "color0": color0,
        "color1": color1,
        "color2": color2,
        "color3": color3,
        "color4": color4,
        "color5": color5,
        "color6": color6,
        "color7": color7,
        "color8": color8,
        "color9": color9,
        "color10": color10,
        "color11": color11,
        "color12": color12,
        "color13": color13,
        "color14": color14,
        "color15": color15,
        "custom_palette_base00": _hex(bg_rgb),
        "custom_palette_base01": _hex(bg_alt_rgb),
        "custom_palette_base02": _hex(_adjust(bg_alt_rgb, 10 if light_mode else 16)),
        "custom_palette_base03": _hex(fg_muted_rgb),
        "custom_palette_base04": _hex(_adjust(fg_muted_rgb, 20 if light_mode else 25)),
        "custom_palette_base05": _hex(fg_rgb),
        "custom_palette_base06": _hex(_adjust(fg_rgb, 10 if light_mode else -10)),
        "custom_palette_base07": "#ffffff" if light_mode else "#f8f8f8",
        "custom_palette_base08": color1,
        "custom_palette_base09": color9,
        "custom_palette_base0A": color11,
        "custom_palette_base0B": color10,
        "custom_palette_base0C": color14,
        "custom_palette_base0D": color12,
        "custom_palette_base0E": color13,
        "custom_palette_base0F": color8,
    }


def write_derived_theme(image_path: Path, theme_name: str) -> Path:
    if not image_path.is_file():
        raise FileNotFoundError(f"image not found: {image_path}")

    theme_name = validate_new_theme_name(theme_name)
    palette = extract_palette(image_path)

    root = THEMES_DIR / theme_name
    wallpapers = root / "wallpapers"
    root.mkdir(parents=True, exist_ok=True)
    wallpapers.mkdir(parents=True, exist_ok=True)

    ext = image_path.suffix.lower() or ".png"
    dest_image = wallpapers / f"default{ext}"
    copy2(image_path, dest_image)

    light_mode = palette["ui_mode"] == "light"
    nvim_variant = "latte" if light_mode else "mocha"

    content = f"""name = "{theme_name}"
default_wallpaper = "default"
ui_mode = "{palette["ui_mode"]}"

font_ui = "FiraCode Nerd Font"
font_mono = "FiraCode Nerd Font"

font_size_ui = 11
font_size_term = 13

gap_px = {18 if light_mode else 12}
border_width = {0 if light_mode else 2}
default_mfact = 0.5

bar_height = {28 if light_mode else 24}
bar_outer_gap = {10 if light_mode else 4}
sync_workspaces = true

terminal_opacity = {0.80 if light_mode else 0.95}

bg = "{palette["bg"]}"
bg_alt = "{palette["bg_alt"]}"

fg = "{palette["fg"]}"
fg_muted = "{palette["fg_muted"]}"

accent = "{palette["accent"]}"
accent_fg = "{palette["accent_fg"]}"

border_active = "{palette["border_active"]}"
border_inactive = "{palette["border_inactive"]}"

workspace_current = "{palette["workspace_current"]}"
workspace_occupied = "{palette["workspace_occupied"]}"
workspace_empty = "{palette["workspace_empty"]}"

selection_bg = "{palette["selection_bg"]}"
selection_fg = "{palette["selection_fg"]}"

nvim_scheme = "loom-custom"
nvim_variant = "{nvim_variant}"
nvim_transparent = true

rofi_width = {44 if light_mode else 40}
rofi_padding = {12 if light_mode else 8}
rofi_border_radius = {18 if light_mode else 6}
rofi_lines = 8
rofi_icon_size = 24
rofi_element_spacing = {8 if light_mode else 4}

dunst_corner_radius = {18 if light_mode else 10}
dunst_width = 380
dunst_height = 130
dunst_offset_x = 24
dunst_offset_y = 24
dunst_frame_width = 0
dunst_timeout = 6

picom_active_opacity = 1.0
picom_inactive_opacity = {0.95 if light_mode else 0.90}
picom_corner_radius = {22 if light_mode else 12}
picom_round_borders = 1
picom_shadow = true
picom_shadow_opacity = {0.18 if light_mode else 0.25}
picom_shadow_offset_x = -10
picom_shadow_offset_y = -10
picom_fade_in_step = 0.05
picom_fade_out_step = 0.05
picom_fade_delta = 4

color0 = "{palette["color0"]}"
color1 = "{palette["color1"]}"
color2 = "{palette["color2"]}"
color3 = "{palette["color3"]}"
color4 = "{palette["color4"]}"
color5 = "{palette["color5"]}"
color6 = "{palette["color6"]}"
color7 = "{palette["color7"]}"
color8 = "{palette["color8"]}"
color9 = "{palette["color9"]}"
color10 = "{palette["color10"]}"
color11 = "{palette["color11"]}"
color12 = "{palette["color12"]}"
color13 = "{palette["color13"]}"
color14 = "{palette["color14"]}"
color15 = "{palette["color15"]}"

custom_palette_base00 = "{palette["custom_palette_base00"]}"
custom_palette_base01 = "{palette["custom_palette_base01"]}"
custom_palette_base02 = "{palette["custom_palette_base02"]}"
custom_palette_base03 = "{palette["custom_palette_base03"]}"
custom_palette_base04 = "{palette["custom_palette_base04"]}"
custom_palette_base05 = "{palette["custom_palette_base05"]}"
custom_palette_base06 = "{palette["custom_palette_base06"]}"
custom_palette_base07 = "{palette["custom_palette_base07"]}"
custom_palette_base08 = "{palette["custom_palette_base08"]}"
custom_palette_base09 = "{palette["custom_palette_base09"]}"
custom_palette_base0A = "{palette["custom_palette_base0A"]}"
custom_palette_base0B = "{palette["custom_palette_base0B"]}"
custom_palette_base0C = "{palette["custom_palette_base0C"]}"
custom_palette_base0D = "{palette["custom_palette_base0D"]}"
custom_palette_base0E = "{palette["custom_palette_base0E"]}"
custom_palette_base0F = "{palette["custom_palette_base0F"]}"
"""
    (root / "theme.toml").write_text(content, encoding="utf-8")
    return root
