# gen_svg.py — SVG Diagram Generator

Generates dark-themed technical diagrams (Catppuccin Mocha palette) for embedding in Markdown via `<img>` tags. Produces SVG files that render consistently in VS Code preview and on GitHub.

For design principles and when to use SVG vs Mermaid, see [GUIDE.md](GUIDE.md).

## Quick Start

```bash
# From project root
python3 tools/svg_gen/gen_svg.py tools/svg_gen/ram_bridge_config.json -o 04_operating_systems/assets/diagram.svg

# From the tool directory
cd tools/svg_gen
python3 gen_svg.py ram_bridge_config.json -o ../../04_operating_systems/assets/diagram.svg
```

## CLI Reference

```
python3 gen_svg.py <config.json> [--output path.svg] [--type diagram_type]
```

| Argument | Default | Description |
|----------|---------|-------------|
| `config` | (required) | Path to JSON config file |
| `--output, -o` | Same stem as config + `.svg` | Output SVG file path |
| `--type, -t` | `memory_map` | Diagram type to generate |

## Supported Diagram Types

### `memory_map` (default)

Vertical proportional memory layout with columns, sections, arrows, and callout panels.

## Config Format — `memory_map`

The config is a JSON file describing the diagram structure. All color values use Catppuccin Mocha palette names (see below).

### Top-Level Fields

```json
{
    "title": "Diagram title (centered, 14px bold)",
    "subtitle": "Optional subtitle (9px dim)",
    "width": 820,
    "height": 860,
    "columns": [ ... ],
    "arrows": [ ... ],
    "callout": { ... },
    "legend": [ ... ]
}
```

### Columns

Each column represents a memory page or address range:

```json
{
    "label": "Page 0: ROM 0",
    "label_color": "blue",
    "address_top": "#0000",
    "address_bottom": "#3FFF",
    "address_side": "left",
    "total_bytes": 16384,
    "column_height": 620,
    "x_offset": 60,
    "width": 250,
    "y_start": 80,
    "scale_note": "Optional note below column",
    "sections": [ ... ]
}
```

| Field | Type | Description |
|-------|------|-------------|
| `label` | string | Column header text |
| `label_color` | string | Palette name for header (`blue`, `green`, `sky`, `mauve`) |
| `address_top` | string | Top address label (e.g., `"#0000"`) |
| `address_bottom` | string | Bottom address label (e.g., `"#3FFF"`) |
| `address_side` | `"left"` or `"right"` | Which side of the column gets address labels |
| `total_bytes` | int | Total byte count for proportional height calculation |
| `column_height` | int | Pixel height of the column panel |
| `x_offset` | int | X position of the column |
| `width` | int | Column width in pixels |
| `y_start` | int | Y position of the column top |
| `scale_note` | string | Optional annotation below the column |
| `sections` | array | Ordered list of content blocks (top to bottom) |

### Sections

Each section is a block within a column. Heights are computed proportionally from `bytes` / `total_bytes`, with a `min_height` floor:

```json
{
    "name": "bridge_source",
    "bytes": 82,
    "min_height": 10,
    "title": "Bridge source (~82 bytes)",
    "lines": ["Optional", "body lines"],
    "fill": "surface1",
    "highlight": "yellow",
    "dash": false
}
```

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | **Unique identifier** within the column. Used as arrow target |
| `bytes` | int | Byte count for proportional height |
| `min_height` | int | Minimum pixel height (prevents tiny regions from vanishing) |
| `title` | string | Block title text |
| `lines` | string[] | Optional body text lines below the title |
| `fill` | string | Palette name for block fill (default: `surface1`) |
| `highlight` | string? | Palette name for highlight border. If set, uses fill_opacity=0.25 and 2px border |
| `dash` | bool | If true, draws dashed border (for inactive/switchable regions) |

### Arrows

Curved or straight arrows between sections in different columns:

```json
{
    "from_col": 0,
    "from_section": "bridge_source",
    "to_col": 1,
    "to_section": "bridge_dest",
    "label": "LDIR ~82 bytes",
    "color": "red",
    "curved": true,
    "dash": "6,3"
}
```

| Field | Type | Description |
|-------|------|-------------|
| `from_col` | int | Source column index (0-based) |
| `from_section` | string | Source section `name` |
| `to_col` | int | Target column index |
| `to_section` | string | Target section `name` |
| `label` | string | Text label on the arrow |
| `color` | string | Palette name for arrow color |
| `curved` | bool | Use cubic bezier (true) or straight line (false) |
| `dash` | string | Dash pattern (e.g., `"6,3"`) or null for solid |

### Callout (Optional)

A magnified detail panel below the main diagram:

```json
{
    "title": "Magnified View: Detail Area",
    "x": 110,
    "y": 730,
    "width": 600,
    "height": 110,
    "items": [
        {"title": "SWAP", "width": 100, "height": 30, "highlight": "green"},
        {"title": "STOO", "width": 80, "height": 30, "highlight": "green"}
    ]
}
```

### Legend (Optional)

Color swatches at the bottom of the diagram:

```json
[
    {"color": "yellow", "label": "Source (in ROM)"},
    {"color": "green", "label": "Destination (in RAM)"}
]
```

## Palette Reference

All color fields accept these palette names:

| Name | Hex | Typical use |
|------|-----|-------------|
| `base` | `#1e1e2e` | Background |
| `surface0` | `#313244` | Column panels |
| `surface1` | `#45475a` | Block fill |
| `surface2` | `#585b70` | Column borders |
| `overlay0` | `#6c7086` | Dim text, ghost borders |
| `overlay2` | `#9399b2` | Body text |
| `subtext0` | `#a6adc8` | Block titles |
| `text` | `#cdd6f4` | Bright text, titles |
| `blue` | `#89b4fa` | Page 0 / ROM headers |
| `green` | `#a6e3a1` | Page 1 / RAM / destination |
| `sky` | `#89dceb` | Page 2 headers |
| `mauve` | `#cba6f7` | Page 3 / switchable headers |
| `yellow` | `#f9e2af` | Source / origin highlight |
| `red` | `#f38ba8` | Critical / arrows / BANK_M |
| `peach` | `#fab387` | Warnings |
| `teal` | `#94e2d5` | Data / registers |
| `lavender` | `#b4befe` | Accents |

## Files

```
tools/svg_gen/
├── README.md                   # This file
├── GUIDE.md                    # Design principles guide
├── gen_svg.py                  # Generator script (Python 3, no dependencies)
└── ram_bridge_config.json      # Template: memory map with source→destination
```
