# loom

`loom` is a desktop theme manager for my X11 environment.

It provides a single source of truth for visual styling across the entire desktop and applies themes consistently to multiple tools.

Themes control:

* window manager colors
* terminal palette
* UI accent colors
* wallpaper
* transparency
* GTK light/dark mode
* notification styling
* launcher styling
* compositor effects

A theme change updates everything at once.

---

# What loom manages

Loom generates theme configuration for:

* **vwm**
* **kitty**
* **rofi**
* **dunst**
* **picom**
* **tmux**
* **neovim**
* **fzf**
* **GTK light/dark mode**
* **wallpaper**

Themes live inside the repository and are the **source of truth**.

Runtime state and generated configuration live under:

```
~/.local/state/loom
```

---

# Install

```
./install.sh
```

This installs the `loom` launcher to:

```
~/.local/bin/loom
```

Make sure `~/.local/bin` is in your `$PATH`.

Example:

```
export PATH="$HOME/.local/bin:$PATH"
```

---

# Uninstall

Safe uninstall:

```
./uninstall.sh
```

This removes the launcher and runtime-generated files but keeps theme state.

Full purge:

```
./uninstall.sh --purge
```

This removes all Loom state:

```
~/.local/state/loom
```

---

# Basic usage

Open the interactive menu:

```
loom menu
```

Apply a theme:

```
loom apply <theme>
```

Example:

```
loom apply pink
```

---

# Preview a theme

Preview applies a theme temporarily.

```
loom preview <theme>
```

Example:

```
loom preview noir
```

Revert preview:

```
loom revert
```

---

# Change wallpaper

```
loom wallpaper <theme>
```

Example:

```
loom wallpaper pink
```

Wallpaper selection includes **live desktop preview while browsing**.

---

# Derive a theme from an image

You can generate a new theme automatically from a wallpaper.

```
loom derive <image> --name <theme>
```

Example:

```
loom derive ~/Pictures/wallpaper.png --name sakura
```

This will:

1. extract a palette from the image
2. generate a theme
3. copy the image into the theme’s wallpaper directory

The new theme appears under:

```
themes/<name>
```

---

# Validate themes

Check for errors across all themes:

```
loom validate
```

This verifies:

* color format
* theme structure
* wallpaper validity
* configuration ranges
* output paths

---

# Show current state

```
loom status
```

Example output:

```
theme: pink
wallpaper: /home/user/repos/loom/themes/pink/wallpapers/default.png
preview_active: no
```

---

# Theme structure

Each theme lives in:

```
themes/<theme-name>/
```

Example:

```
themes/pink/
    theme.toml
    wallpapers/
        default.png
        other.png
```

---

# Theme file

Themes are defined in `theme.toml`.

Example fields:

```
name = "pink"
ui_mode = "light"

bg = "#fdf0f5"
fg = "#4a3a3f"

accent = "#ff8fb1"

terminal_opacity = 0.8

gap_px = 18
border_width = 0
bar_height = 28

picom_corner_radius = 22
picom_shadow = true
```

Themes control both **color palette** and **layout parameters**.

---

# Wallpaper behavior

Each theme has a wallpaper directory:

```
themes/<theme>/wallpapers
```

Example:

```
themes/pink/wallpapers/default.png
```

Loom stores the currently selected wallpaper in:

```
~/.local/state/loom/current_wallpaper
```

Your session startup (for example `.xprofile`) can read this to restore the wallpaper automatically.

---

# Generated files

Loom writes generated theme configuration to:

```
~/.local/state/loom/generated
```

These files are used by:

* vwm
* kitty
* rofi
* tmux
* neovim
* fzf
* dunst
* picom
* GTK

These files are **not meant to be edited manually**.

---

# Menu interface

The menu provides:

```
Apply Theme
Change Wallpaper
Preview Theme
Revert Preview
Derive Theme From Image
Validate Themes
Reapply Current Theme
```

The menu uses:

* rofi
* fzf
* tmux popup or floating terminal

depending on the context.

---

# Dependencies

Required:

```
python3
rofi
fzf
xwallpaper
picom
kitty
```

Recommended:

```
chafa
```

`chafa` enables image previews inside terminal pickers.

---

# Design goals

Loom focuses on:

* fast theme switching
* consistent styling across tools
* reproducible desktop setups
* theme generation from images
* minimal manual configuration

Themes are version-controlled and portable across machines.

---

# Notes

* Themes inside the repo are the **source of truth**
* Runtime files live in `~/.local/state/loom`
* Generated files should not be edited manually
* Loom is designed for **X11 environments**

---

If you want, next we can also add a **small GIF demo section** to the README showing:

* theme switching
* wallpaper preview
* derive from image

which makes the project feel far more polished.

__

# License

MIT
