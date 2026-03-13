from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import tomllib

from loomlib.paths import THEMES_DIR


IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp", ".tiff", ".tif", ".avif"}


@dataclass(slots=True)
class Theme:
    name: str
    root: Path
    theme_file: Path
    wallpapers_dir: Path
    default_wallpaper: str
    ui_mode: str

    font_ui: str
    font_mono: str
    font_size_ui: int
    font_size_term: int

    gap_px: int
    border_width: int
    default_mfact: float
    bar_height: int
    bar_outer_gap: int
    sync_workspaces: bool
    terminal_opacity: float

    bg: str
    bg_alt: str
    fg: str
    fg_muted: str
    accent: str
    accent_fg: str
    border_active: str
    border_inactive: str
    workspace_current: str
    workspace_occupied: str
    workspace_empty: str
    selection_bg: str
    selection_fg: str

    nvim_scheme: str
    nvim_variant: str
    nvim_transparent: bool

    rofi_width: int
    rofi_padding: int
    rofi_border_radius: int
    rofi_lines: int
    rofi_icon_size: int
    rofi_element_spacing: int

    dunst_corner_radius: int
    dunst_width: int
    dunst_height: int
    dunst_offset_x: int
    dunst_offset_y: int
    dunst_frame_width: int
    dunst_timeout: int

    picom_active_opacity: float
    picom_inactive_opacity: float
    picom_corner_radius: int
    picom_round_borders: int
    picom_shadow: bool
    picom_shadow_opacity: float
    picom_shadow_offset_x: int
    picom_shadow_offset_y: int
    picom_fade_in_step: float
    picom_fade_out_step: float
    picom_fade_delta: int

    color0: str
    color1: str
    color2: str
    color3: str
    color4: str
    color5: str
    color6: str
    color7: str
    color8: str
    color9: str
    color10: str
    color11: str
    color12: str
    color13: str
    color14: str
    color15: str

    custom_palette_base00: str | None = None
    custom_palette_base01: str | None = None
    custom_palette_base02: str | None = None
    custom_palette_base03: str | None = None
    custom_palette_base04: str | None = None
    custom_palette_base05: str | None = None
    custom_palette_base06: str | None = None
    custom_palette_base07: str | None = None
    custom_palette_base08: str | None = None
    custom_palette_base09: str | None = None
    custom_palette_base0A: str | None = None
    custom_palette_base0B: str | None = None
    custom_palette_base0C: str | None = None
    custom_palette_base0D: str | None = None
    custom_palette_base0E: str | None = None
    custom_palette_base0F: str | None = None

    @property
    def default_wallpaper_path(self) -> Path:
        resolved = resolve_wallpaper_reference(self.wallpapers_dir, self.default_wallpaper)
        if resolved is None:
            raise FileNotFoundError(
                f"default wallpaper not found for theme '{self.name}': {self.default_wallpaper}"
            )
        return resolved

    def list_wallpapers(self) -> list[Path]:
        if not self.wallpapers_dir.is_dir():
            return []
        return [
            p for p in sorted(self.wallpapers_dir.iterdir())
            if p.is_file() and p.suffix.lower() in IMAGE_EXTENSIONS
        ]

    def custom_palette(self) -> dict[str, str] | None:
        keys = [
            "base00", "base01", "base02", "base03", "base04", "base05", "base06", "base07",
            "base08", "base09", "base0A", "base0B", "base0C", "base0D", "base0E", "base0F",
        ]
        values = {
            "base00": self.custom_palette_base00,
            "base01": self.custom_palette_base01,
            "base02": self.custom_palette_base02,
            "base03": self.custom_palette_base03,
            "base04": self.custom_palette_base04,
            "base05": self.custom_palette_base05,
            "base06": self.custom_palette_base06,
            "base07": self.custom_palette_base07,
            "base08": self.custom_palette_base08,
            "base09": self.custom_palette_base09,
            "base0A": self.custom_palette_base0A,
            "base0B": self.custom_palette_base0B,
            "base0C": self.custom_palette_base0C,
            "base0D": self.custom_palette_base0D,
            "base0E": self.custom_palette_base0E,
            "base0F": self.custom_palette_base0F,
        }
        if not any(values.values()):
            return None
        return {k: values[k] for k in keys if values[k] is not None}


REQUIRED_KEYS = {
    "name",
    "default_wallpaper",
    "ui_mode",
    "font_ui",
    "font_mono",
    "font_size_ui",
    "font_size_term",
    "gap_px",
    "border_width",
    "default_mfact",
    "bar_height",
    "bar_outer_gap",
    "sync_workspaces",
    "terminal_opacity",
    "bg",
    "bg_alt",
    "fg",
    "fg_muted",
    "accent",
    "accent_fg",
    "border_active",
    "border_inactive",
    "workspace_current",
    "workspace_occupied",
    "workspace_empty",
    "selection_bg",
    "selection_fg",
    "nvim_scheme",
    "nvim_variant",
    "nvim_transparent",
    "rofi_width",
    "rofi_padding",
    "rofi_border_radius",
    "rofi_lines",
    "rofi_icon_size",
    "rofi_element_spacing",
    "dunst_corner_radius",
    "dunst_width",
    "dunst_height",
    "dunst_offset_x",
    "dunst_offset_y",
    "dunst_frame_width",
    "dunst_timeout",
    "picom_active_opacity",
    "picom_inactive_opacity",
    "picom_corner_radius",
    "picom_round_borders",
    "picom_shadow",
    "picom_shadow_opacity",
    "picom_shadow_offset_x",
    "picom_shadow_offset_y",
    "picom_fade_in_step",
    "picom_fade_out_step",
    "picom_fade_delta",
    "color0",
    "color1",
    "color2",
    "color3",
    "color4",
    "color5",
    "color6",
    "color7",
    "color8",
    "color9",
    "color10",
    "color11",
    "color12",
    "color13",
    "color14",
    "color15",
}


def resolve_wallpaper_reference(wallpapers_dir: Path, value: str) -> Path | None:
    raw = value.strip()
    if not raw:
        return None

    exact = wallpapers_dir / raw
    if exact.is_file():
        return exact

    candidate_path = Path(raw)
    if candidate_path.suffix:
        return None

    matches = []
    for ext in sorted(IMAGE_EXTENSIONS):
        p = wallpapers_dir / f"{raw}{ext}"
        if p.is_file():
            matches.append(p)

    if len(matches) == 1:
        return matches[0]

    if len(matches) > 1:
        raise ValueError(
            f"multiple wallpapers match default '{raw}' in {wallpapers_dir}: "
            + ", ".join(p.name for p in matches)
        )

    return None


def load_theme(theme_name: str) -> Theme:
    root = THEMES_DIR / theme_name
    theme_file = root / "theme.toml"
    wallpapers_dir = root / "wallpapers"

    if not root.is_dir():
        raise FileNotFoundError(f"theme directory not found: {root}")

    if not theme_file.is_file():
        raise FileNotFoundError(f"theme file not found: {theme_file}")

    with theme_file.open("rb") as f:
        data = tomllib.load(f)

    missing = sorted(REQUIRED_KEYS - data.keys())
    if missing:
        raise ValueError(f"missing required theme keys: {', '.join(missing)}")

    theme = Theme(
        name=data["name"],
        root=root,
        theme_file=theme_file,
        wallpapers_dir=wallpapers_dir,
        default_wallpaper=data["default_wallpaper"],
        ui_mode=data["ui_mode"],
        font_ui=data["font_ui"],
        font_mono=data["font_mono"],
        font_size_ui=int(data["font_size_ui"]),
        font_size_term=int(data["font_size_term"]),
        gap_px=int(data["gap_px"]),
        border_width=int(data["border_width"]),
        default_mfact=float(data["default_mfact"]),
        bar_height=int(data["bar_height"]),
        bar_outer_gap=int(data["bar_outer_gap"]),
        sync_workspaces=bool(data["sync_workspaces"]),
        terminal_opacity=float(data["terminal_opacity"]),
        bg=data["bg"],
        bg_alt=data["bg_alt"],
        fg=data["fg"],
        fg_muted=data["fg_muted"],
        accent=data["accent"],
        accent_fg=data["accent_fg"],
        border_active=data["border_active"],
        border_inactive=data["border_inactive"],
        workspace_current=data["workspace_current"],
        workspace_occupied=data["workspace_occupied"],
        workspace_empty=data["workspace_empty"],
        selection_bg=data["selection_bg"],
        selection_fg=data["selection_fg"],
        nvim_scheme=data["nvim_scheme"],
        nvim_variant=data["nvim_variant"],
        nvim_transparent=bool(data["nvim_transparent"]),
        rofi_width=int(data["rofi_width"]),
        rofi_padding=int(data["rofi_padding"]),
        rofi_border_radius=int(data["rofi_border_radius"]),
        rofi_lines=int(data["rofi_lines"]),
        rofi_icon_size=int(data["rofi_icon_size"]),
        rofi_element_spacing=int(data["rofi_element_spacing"]),
        dunst_corner_radius=int(data["dunst_corner_radius"]),
        dunst_width=int(data["dunst_width"]),
        dunst_height=int(data["dunst_height"]),
        dunst_offset_x=int(data["dunst_offset_x"]),
        dunst_offset_y=int(data["dunst_offset_y"]),
        dunst_frame_width=int(data["dunst_frame_width"]),
        dunst_timeout=int(data["dunst_timeout"]),
        picom_active_opacity=float(data["picom_active_opacity"]),
        picom_inactive_opacity=float(data["picom_inactive_opacity"]),
        picom_corner_radius=int(data["picom_corner_radius"]),
        picom_round_borders=int(data["picom_round_borders"]),
        picom_shadow=bool(data["picom_shadow"]),
        picom_shadow_opacity=float(data["picom_shadow_opacity"]),
        picom_shadow_offset_x=int(data["picom_shadow_offset_x"]),
        picom_shadow_offset_y=int(data["picom_shadow_offset_y"]),
        picom_fade_in_step=float(data["picom_fade_in_step"]),
        picom_fade_out_step=float(data["picom_fade_out_step"]),
        picom_fade_delta=int(data["picom_fade_delta"]),
        color0=data["color0"],
        color1=data["color1"],
        color2=data["color2"],
        color3=data["color3"],
        color4=data["color4"],
        color5=data["color5"],
        color6=data["color6"],
        color7=data["color7"],
        color8=data["color8"],
        color9=data["color9"],
        color10=data["color10"],
        color11=data["color11"],
        color12=data["color12"],
        color13=data["color13"],
        color14=data["color14"],
        color15=data["color15"],
        custom_palette_base00=data.get("custom_palette_base00"),
        custom_palette_base01=data.get("custom_palette_base01"),
        custom_palette_base02=data.get("custom_palette_base02"),
        custom_palette_base03=data.get("custom_palette_base03"),
        custom_palette_base04=data.get("custom_palette_base04"),
        custom_palette_base05=data.get("custom_palette_base05"),
        custom_palette_base06=data.get("custom_palette_base06"),
        custom_palette_base07=data.get("custom_palette_base07"),
        custom_palette_base08=data.get("custom_palette_base08"),
        custom_palette_base09=data.get("custom_palette_base09"),
        custom_palette_base0A=data.get("custom_palette_base0A"),
        custom_palette_base0B=data.get("custom_palette_base0B"),
        custom_palette_base0C=data.get("custom_palette_base0C"),
        custom_palette_base0D=data.get("custom_palette_base0D"),
        custom_palette_base0E=data.get("custom_palette_base0E"),
        custom_palette_base0F=data.get("custom_palette_base0F"),
    )

    _ = theme.default_wallpaper_path
    return theme


def list_theme_names() -> list[str]:
    if not THEMES_DIR.is_dir():
        return []
    return sorted(
        p.name for p in THEMES_DIR.iterdir()
        if p.is_dir() and (p / "theme.toml").is_file()
    )


def hex_to_vwm(color: str) -> str:
    color = color.strip()
    if not color.startswith("#") or len(color) != 7:
        raise ValueError(f"invalid color: {color}")
    return "0x" + color[1:].lower()
