from __future__ import annotations

import colorsys
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


def _clamp(v: float) -> int:
    return max(0, min(255, int(round(v))))


def _brightness(rgb: tuple[int, int, int]) -> float:
    r, g, b = rgb
    return 0.299 * r + 0.587 * g + 0.114 * b


def _mix(a: tuple[int, int, int], b: tuple[int, int, int], t: float) -> tuple[int, int, int]:
    return (
        _clamp(a[0] + (b[0] - a[0]) * t),
        _clamp(a[1] + (b[1] - a[1]) * t),
        _clamp(a[2] + (b[2] - a[2]) * t),
    )


def _lighten(rgb: tuple[int, int, int], amount: float) -> tuple[int, int, int]:
    return _mix(rgb, (255, 255, 255), amount)


def _darken(rgb: tuple[int, int, int], amount: float) -> tuple[int, int, int]:
    return _mix(rgb, (0, 0, 0), amount)


def _desaturate(rgb: tuple[int, int, int], amount: float) -> tuple[int, int, int]:
    r, g, b = [c / 255.0 for c in rgb]
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    s = max(0.0, min(1.0, s * (1.0 - amount)))
    rr, gg, bb = colorsys.hls_to_rgb(h, l, s)
    return (_clamp(rr * 255), _clamp(gg * 255), _clamp(bb * 255))


def _shift_hue(rgb: tuple[int, int, int], amount: float) -> tuple[int, int, int]:
    r, g, b = [c / 255.0 for c in rgb]
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    h = (h + amount) % 1.0
    rr, gg, bb = colorsys.hls_to_rgb(h, l, s)
    return (_clamp(rr * 255), _clamp(gg * 255), _clamp(bb * 255))


def extract_palette(image_path: Path) -> dict[str, str]:
    img = Image.open(image_path).convert("RGB")
    img = img.resize((240, 240))
    paletted = img.quantize(colors=10, method=Image.Quantize.MEDIANCUT)
    palette = paletted.getpalette()
    counts = sorted(paletted.getcolors(), reverse=True)

    colors: list[tuple[int, int, int]] = []
    for _, idx in counts[:10]:
        base = idx * 3
        rgb = (palette[base], palette[base + 1], palette[base + 2])
        colors.append(rgb)

    if not colors:
        colors = [(24, 24, 28), (120, 150, 220), (210, 220, 235)]

    dominant = colors[0]
    accent = colors[1] if len(colors) > 1 else _lighten(_shift_hue(dominant, 0.08), 0.18)

    light_mode = _brightness(dominant) > 150

    if light_mode:
        bg = _lighten(_desaturate(dominant, 0.55), 0.78)
        bg_alt = _darken(bg, 0.04)
        fg = (52, 66, 78)
        fg_muted = _mix(fg, bg, 0.45)
        accent = _desaturate(_mix(accent, (120, 185, 225), 0.35), 0.25)
        accent_soft = _mix(accent, bg, 0.42)
        border_active = accent
        border_inactive = _mix(accent, bg_alt, 0.65)
        workspace_current = accent
        workspace_occupied = border_inactive
        workspace_empty = _mix(border_inactive, bg, 0.35)
        selection_bg = _mix(accent, bg, 0.55)
        selection_fg = (48, 64, 76)
    else:
        bg = _darken(_desaturate(dominant, 0.42), 0.55)
        bg_alt = _lighten(bg, 0.06)
        fg = _lighten(_desaturate(colors[-1] if len(colors) > 2 else (230, 230, 235), 0.35), 0.08)
        fg_muted = _mix(fg, bg, 0.48)
        accent = _lighten(_desaturate(accent, 0.15), 0.08)
        accent_soft = _mix(accent, bg_alt, 0.42)
        border_active = accent
        border_inactive = _mix(accent, bg, 0.68)
        workspace_current = accent
        workspace_occupied = _mix(fg_muted, accent_soft, 0.35)
        workspace_empty = _mix(border_inactive, bg, 0.28)
        selection_bg = _mix(accent, bg_alt, 0.55)
        selection_fg = (255, 255, 255)

    color0 = _hex(bg_alt)
    color1 = _hex(_mix(accent, (255, 90, 90), 0.55))
    color2 = _hex(_mix(accent, (120, 200, 140), 0.55))
    color3 = _hex(_mix(accent, (240, 190, 90), 0.55))
    color4 = _hex(accent)
    color5 = _hex(_shift_hue(_lighten(accent, 0.08), 0.10))
    color6 = _hex(_shift_hue(_lighten(accent, 0.02), -0.08))
    color7 = _hex(fg_muted)
    color8 = _hex(_lighten(bg_alt, 0.18) if not light_mode else _darken(bg_alt, 0.18))
    color9 = _hex(_lighten((_mix(accent, (255, 90, 90), 0.55)), 0.10))
    color10 = _hex(_lighten((_mix(accent, (120, 200, 140), 0.55)), 0.10))
    color11 = _hex(_lighten((_mix(accent, (240, 190, 90), 0.55)), 0.10))
    color12 = _hex(_lighten(accent, 0.12))
    color13 = _hex(_lighten(_shift_hue(accent, 0.10), 0.10))
    color14 = _hex(_lighten(_shift_hue(accent, -0.08), 0.10))
    color15 = _hex(fg)

    return {
        "ui_mode": "light" if light_mode else "dark",
        "bg": _hex(bg),
        "bg_alt": _hex(bg_alt),
        "fg": _hex(fg),
        "fg_muted": _hex(fg_muted),
        "accent": _hex(accent),
        "accent_soft": _hex(accent_soft),
        "accent_fg": _hex((255, 255, 255) if _brightness(accent) < 150 else (20, 20, 20)),
        "border_active": _hex(border_active),
        "border_inactive": _hex(border_inactive),
        "workspace_current": _hex(workspace_current),
        "workspace_occupied": _hex(workspace_occupied),
        "workspace_empty": _hex(workspace_empty),
        "selection_bg": _hex(selection_bg),
        "selection_fg": _hex(selection_fg),
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
        "custom_palette_base00": _hex(bg),
        "custom_palette_base01": _hex(bg_alt),
        "custom_palette_base02": _hex(_lighten(bg_alt, 0.06) if not light_mode else _darken(bg_alt, 0.06)),
        "custom_palette_base03": _hex(fg_muted),
        "custom_palette_base04": _hex(_mix(fg_muted, fg, 0.35)),
        "custom_palette_base05": _hex(fg),
        "custom_palette_base06": _hex(_lighten(fg, 0.08) if not light_mode else _darken(fg, 0.08)),
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

    content = f"""name = "{theme_name}"
default_wallpaper = "default"
ui_mode = "{palette["ui_mode"]}"

font_ui = "FiraCode Nerd Font"
font_mono = "FiraCode Nerd Font"

font_size_ui = 11
font_size_term = 13

gap_px = {18 if light_mode else 10}
border_width = {0 if light_mode else 2}
default_mfact = 0.5
sync_workspaces = true
terminal_opacity = {0.84 if light_mode else 0.94}

bg = "{palette["bg"]}"
bg_alt = "{palette["bg_alt"]}"
fg = "{palette["fg"]}"
fg_muted = "{palette["fg_muted"]}"
accent = "{palette["accent"]}"
accent_soft = "{palette["accent_soft"]}"
accent_fg = "{palette["accent_fg"]}"
border_active = "{palette["border_active"]}"
border_inactive = "{palette["border_inactive"]}"
workspace_current = "{palette["workspace_current"]}"
workspace_occupied = "{palette["workspace_occupied"]}"
workspace_empty = "{palette["workspace_empty"]}"
selection_bg = "{palette["selection_bg"]}"
selection_fg = "{palette["selection_fg"]}"

vwm_bar_enabled = true
vwm_bar_background = {str(not light_mode).lower()}
vwm_bar_modules = "{'pill' if light_mode else 'flat'}"
vwm_bar_icons = true
vwm_bar_colors = true
vwm_bar_minimal = false
vwm_bar_position = "top"
vwm_bar_height = {28 if light_mode else 24}
vwm_bar_radius = {16 if light_mode else 0}
vwm_bar_margin_x = {18 if light_mode else 0}
vwm_bar_margin_y = {10 if light_mode else 0}
vwm_bar_content_margin_x = {14 if light_mode else 12}
vwm_bar_content_margin_y = {2 if light_mode else 0}
vwm_bar_gap = {18 if light_mode else 10}
vwm_bar_padding_x = {12 if light_mode else 8}
vwm_bar_padding_y = {6 if light_mode else 0}
vwm_bar_volume_bar_enabled = true
vwm_bar_volume_bar_width = {38 if light_mode else 28}
vwm_bar_volume_bar_height = {8 if light_mode else 6}
vwm_bar_volume_bar_radius = {10 if light_mode else 0}

nvim_scheme = "loom-custom"
nvim_variant = "{'latte' if light_mode else 'main'}"
nvim_transparent = true

rofi_width = {44 if light_mode else 40}
rofi_padding = {12 if light_mode else 8}
rofi_border_radius = {14 if light_mode else 6}
rofi_lines = 8
rofi_icon_size = 24
rofi_element_spacing = {8 if light_mode else 4}

dunst_corner_radius = {14 if light_mode else 8}
dunst_width = 380
dunst_height = 130
dunst_offset_x = 24
dunst_offset_y = 24
dunst_frame_width = 2
dunst_timeout = 6

picom_active_opacity = 1.0
picom_inactive_opacity = {0.98 if light_mode else 0.90}
picom_corner_radius = {14 if light_mode else 6}
picom_round_borders = 1
picom_shadow = true
picom_shadow_opacity = {0.18 if light_mode else 0.25}
picom_shadow_offset_x = -10
picom_shadow_offset_y = -10
picom_fade_in_step = 0.05
picom_fade_out_step = 0.05
picom_fade_delta = 4
picom_blur_enabled = true

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
