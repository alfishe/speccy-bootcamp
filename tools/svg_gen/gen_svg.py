#!/usr/bin/env python3
"""
ZX Spectrum Knowledge Base — SVG Diagram Generator

Generates dark-themed technical diagrams (Catppuccin Mocha palette) for
embedding in Markdown via <img> tags. Produces SVG files that render
consistently in VS Code preview and on GitHub.

Usage:
    python3 tools/svg_gen/gen_svg.py tools/svg_gen/ram_bridge_config.json -o 04_operating_systems/assets/ram_bridge_memory_layout.svg
    # Or from the tool directory:
    python3 gen_svg.py ram_bridge_config.json -o ../../04_operating_systems/assets/diagram.svg

Config format: JSON files in tools/svg_gen/. Output paths are relative to project root.
Templates: ram_bridge_config.json — memory map with source/destination columns and arrows.
"""

import sys
import json
import argparse
from pathlib import Path

# ═══════════════════════════════════════════════════════════════════════
# DESIGN SYSTEM — Catppuccin Mocha
# ═══════════════════════════════════════════════════════════════════════

PALETTE = {
    "base":       "#1e1e2e",   # background
    "mantle":     "#181825",   # darker background
    "crust":      "#11111b",   # darkest
    "surface0":   "#313244",   # column bg, panels
    "surface1":   "#45475a",   # block fill
    "surface2":   "#585b70",   # borders
    "overlay0":   "#6c7086",   # dim text, inactive borders
    "overlay1":   "#7f849c",   # secondary dim
    "overlay2":   "#9399b2",   # body text
    "subtext0":   "#a6adc8",   # block titles
    "subtext1":   "#bac2de",   # labels
    "text":       "#cdd6f4",   # bright text
    "lavender":   "#b4befe",   # accents
    "blue":       "#89b4fa",   # ROM / section 0 headers
    "sapphire":   "#74c7ec",   # secondary headers
    "sky":        "#89dceb",   # section 2 headers
    "teal":       "#94e2d5",   # data
    "green":      "#a6e3a1",   # RAM / destination / success
    "yellow":     "#f9e2af",   # source / highlight
    "peach":      "#fab387",   # warnings
    "maroon":     "#eba0ac",   # errors (soft)
    "red":        "#f38ba8",   # critical arrows, BANK_M
    "mauve":      "#cba6f7",   # section 3 headers
    "pink":       "#f5c2e7",   # special
    "flamingo":   "#f2cdcd",   # deprecated
    "rosewater":  "#f5e0dc",   # warm accents
}

FONT = "'Menlo','Consolas','Courier New',monospace"

# ═══════════════════════════════════════════════════════════════════════
# SVG BUILDER HELPERS
# ═══════════════════════════════════════════════════════════════════════

class SVG:
    """Minimal SVG builder with Catppuccin styling defaults."""

    def __init__(self, width, height, title=""):
        self.parts = []
        self.width = width
        self.height = height
        self.parts.append(
            f'<svg xmlns="http://www.w3.org/2000/svg" '
            f'viewBox="0 0 {width} {height}" font-family="{FONT}">'
        )
        # Background
        self.rect(0, 0, width, height, fill="base", rx=6)
        if title:
            self.text(width // 2, 28, title, size=14, color="text", bold=True, anchor="middle")

    # ── Primitives ────────────────────────────────────────────────────

    def rect(self, x, y, w, h, *, fill="surface1", stroke="overlay0",
             stroke_width=1, rx=3, fill_opacity=None, dash=None, comment=None):
        if fill in PALETTE:
            fill = PALETTE[fill]
        if stroke in PALETTE:
            stroke = PALETTE[stroke]
        attrs = [f'x="{x}"', f'y="{y}"', f'width="{w}"', f'height="{h}"',
                 f'fill="{fill}"', f'stroke="{stroke}"', f'stroke-width="{stroke_width}"',
                 f'rx="{rx}"']
        if fill_opacity is not None:
            attrs.append(f'fill-opacity="{fill_opacity}"')
        if dash:
            if isinstance(dash, bool):
                attrs.append('stroke-dasharray="4,3"')
            else:
                attrs.append(f'stroke-dasharray="{dash}"')
        line = f'  <rect {" ".join(attrs)}/>'
        if comment:
            line = f'  <!-- {comment} -->\n{line}'
        self.parts.append(line)

    def text(self, x, y, content, *, size=10, color="overlay2", bold=False,
             anchor="middle", comment=None):
        if color in PALETTE:
            color = PALETTE[color]
        weight = ' font-weight="bold"' if bold else ''
        # Escape XML entities
        content = content.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        line = f'  <text x="{x}" y="{y}" text-anchor="{anchor}" fill="{color}" font-size="{size}"{weight}>{content}</text>'
        if comment:
            line = f'  <!-- {comment} -->\n{line}'
        self.parts.append(line)

    def line(self, x1, y1, x2, y2, *, stroke="overlay0", stroke_width=1, dash=None):
        if stroke in PALETTE:
            stroke = PALETTE[stroke]
        attrs = [f'x1="{x1}"', f'y1="{y1}"', f'x2="{x2}"', f'y2="{y2}"',
                 f'stroke="{stroke}"', f'stroke-width="{stroke_width}"']
        if dash:
            attrs.append(f'stroke-dasharray="{dash}"')
        self.parts.append(f'  <line {" ".join(attrs)}/>')

    def arrow(self, x1, y1, x2, y2, *, stroke="red", stroke_width=2.5,
              dash=None, curved=False, label="", label_size=8):
        """Draw an arrow with optional label. Uses a cubic bezier if curved=True."""
        if stroke in PALETTE:
            stroke_color = PALETTE[stroke]
        else:
            stroke_color = stroke

        marker_id = f"arr_{len(self.parts)}"
        self.parts.append(f'  <defs>')
        self.parts.append(
            f'    <marker id="{marker_id}" markerWidth="10" markerHeight="7" '
            f'refX="10" refY="3.5" orient="auto">'
        )
        self.parts.append(f'      <polygon points="0 0, 10 3.5, 0 7" fill="{stroke_color}"/>')
        self.parts.append(f'    </marker>')
        self.parts.append(f'  </defs>')

        attrs = [f'fill="none"', f'stroke="{stroke_color}"',
                 f'stroke-width="{stroke_width}"', f'marker-end="url(#{marker_id})"']
        if dash:
            attrs.append(f'stroke-dasharray="{dash}"')

        if curved:
            # Auto-generate a smooth cubic bezier from left to right
            cx = (x1 + x2) // 2
            self.parts.append(
                f'  <path d="M {x1} {y1} C {cx} {y1}, {cx} {y2}, {x2} {y2}" {" ".join(attrs)}/>'
            )
        else:
            self.parts.append(f'  <line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" {" ".join(attrs)}/>')

        if label:
            mx = (x1 + x2) // 2
            my = (y1 + y2) // 2 - 4
            self.text(mx, my, label, size=label_size, color=stroke, bold=True)

    def section_comment(self, text):
        self.parts.append(f'')
        self.parts.append(f'  <!-- {"=" * 5} {text} {"=" * 5} -->')

    # ── High-level building blocks ────────────────────────────────────

    def title_bar(self, y, title, subtitle="", color="text"):
        """Centered title + optional subtitle."""
        self.text(self.width // 2, y, title, size=14, color=color, bold=True, anchor="middle")
        if subtitle:
            self.text(self.width // 2, y + 16, subtitle, size=9, color="overlay2", anchor="middle")

    def column(self, x, y, w, h, *, label="", label_color="blue", comment=""):
        """Draw a column panel (e.g., a memory page). Returns inner offset (x+pad, y+pad)."""
        self.section_comment(comment or label)
        self.rect(x, y, w, h, fill="surface0", stroke="surface2", rx=4, comment=label)
        if label:
            self.text(x + w // 2, y - 12, label, size=11, color=label_color, bold=True)
        pad = 10
        return x + pad, y + pad

    def block(self, x, y, w, h, *, title="", lines=None, fill="surface1",
              stroke="overlay0", highlight=None, dash=None, comment=""):
        """
        Draw a content block with optional title and body lines.
        highlight: color name for highlighted blocks (sets fill_opacity=0.25, thicker stroke).
        Returns the y position below the block.
        """
        fill_opacity = None
        stroke_width = 1
        hl_color = None
        if highlight:
            hl_color = highlight
            fill = highlight
            fill_opacity = 0.25
            stroke = highlight
            stroke_width = 2

        self.rect(x, y, w, h, fill=fill, stroke=stroke, stroke_width=stroke_width,
                  fill_opacity=fill_opacity, dash=dash, comment=comment or title)

        cx = x + w // 2
        ty = y + h // 2
        if title and not lines:
            # Single centered title
            color = hl_color if hl_color else "subtext0"
            sz = 8 if h < 15 else (9 if h < 20 else 10)
            self.text(cx, ty + 4, title, size=sz, color=color, bold=bool(hl_color))
        elif title and lines:
            color = hl_color if hl_color else "subtext0"
            body_color = "overlay2"
            sz_title = 10 if h > 40 else 8
            sz_body = 8 if h > 40 else 7
            self.text(cx, y + 18, title, size=sz_title, color=color, bold=True)
            for i, line_text in enumerate(lines):
                self.text(cx, y + 32 + i * 14, line_text, size=sz_body, color=body_color)
        elif lines:
            for i, line_text in enumerate(lines):
                self.text(cx, y + 12 + i * 13, line_text, size=8, color="overlay2")

        return y + h

    def address_label(self, x, y, addr, *, side="left", color="overlay0"):
        """Draw an address label beside a column."""
        anchor = "end" if side == "left" else "start"
        self.text(x, y, addr, size=8, color=color, anchor=anchor)

    def legend_item(self, x, y, fill_color, label, *, size=7):
        """Draw a legend swatch + label."""
        self.rect(x, y, 10, 10, fill=fill_color, stroke=fill_color, stroke_width=1.5, rx=2, fill_opacity=0.25)
        self.text(x + 15, y + 9, label, size=size, color="text")

    # ── Output ────────────────────────────────────────────────────────

    def render(self):
        self.parts.append('</svg>')
        return '\n'.join(self.parts)

    def write(self, path):
        svg = self.render()
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        Path(path).write_text(svg + '\n')
        print(f"Wrote {path} ({len(svg)} bytes)")


# ═══════════════════════════════════════════════════════════════════════
# MEMORY MAP DIAGRAM — Vertical proportional layout
# ═══════════════════════════════════════════════════════════════════════

def gen_memory_map(config, output_path):
    """
    Generate a vertical memory map diagram from config dict.
    
    Config structure:
    {
        "title": "Diagram Title",
        "subtitle": "Optional subtitle",
        "width": 820,
        "height": 860,
        "columns": [
            {
                "label": "Page 0: ROM 0",
                "label_color": "blue",
                "address_top": "#0000",
                "address_bottom": "#3FFF",
                "total_bytes": 16384,
                "column_height": 620,
                "x_offset": 60,
                "width": 250,
                "y_start": 80,
                "sections": [
                    {
                        "name": "Main ROM body",
                        "bytes": 12288,
                        "title": "ROM 0",
                        "lines": ["RST vectors", "Editor", "BASIC ext"],
                        "fill": "surface1",
                        "highlight": null
                    },
                    {
                        "name": "Bridge source",
                        "bytes": 82,
                        "min_height": 10,
                        "title": "Bridge source (~82 bytes)",
                        "highlight": "yellow"
                    }
                ]
            },
            ...
        ],
        "arrows": [
            {
                "from_col": 0, "from_section": "Bridge source",
                "to_col": 1, "to_section": "Bridge destination",
                "label": "LDIR ~82 bytes",
                "curved": true
            }
        ],
        "callout": {
            "title": "Magnified View",
            "y": 730,
            "items": [
                {"title": "SWAP", "subtitle": "#5B00 (16 bytes)", "highlight": "green"},
                ...
            ]
        },
        "legend": [
            {"color": "yellow", "label": "Source (in ROM)"},
            {"color": "green", "label": "Destination (in RAM)"},
        ]
    }
    """
    w = config.get("width", 820)
    h = config.get("height", 860)
    svg = SVG(w, h)
    
    svg.title_bar(28, config.get("title", "Memory Map"),
                  config.get("subtitle", ""), "text")
    
    # Track section positions for arrows
    section_positions = {}  # (col_idx, section_name) -> (cx, cy)
    
    for ci, col in enumerate(config.get("columns", [])):
        cx, cy_start = svg.column(
            col["x_offset"], col.get("y_start", 80),
            col["width"], col["column_height"],
            label=col.get("label", ""),
            label_color=col.get("label_color", "blue"),
            comment=col.get("label", "")
        )
        
        # Address labels
        addr_side = col.get("address_side", "left")
        addr_x = col["x_offset"] - 5 if addr_side == "left" else col["x_offset"] + col["width"] + 5
        svg.address_label(addr_x, cy_start + 8, col.get("address_top", ""), side=addr_side)
        svg.address_label(addr_x, cy_start + col["column_height"] - 4,
                         col.get("address_bottom", ""), side=addr_side)
        
        # Compute proportional heights
        total_bytes = col.get("total_bytes", 16384)
        available_h = col["column_height"] - 20  # padding
        sections = col.get("sections", [])
        
        # First pass: compute raw proportional heights
        heights = []
        for sec in sections:
            raw = sec["bytes"] / total_bytes * available_h
            min_h = sec.get("min_height", 6)
            heights.append(max(raw, min_h))
        
        # Scale if total exceeds available
        total_h = sum(heights)
        if total_h > available_h:
            scale = available_h / total_h
            heights = [h * scale for h in heights]
        
        # Draw sections
        y = cy_start
        inner_w = col["width"] - 20
        for si, sec in enumerate(sections):
            sh = int(heights[si])
            highlight = sec.get("highlight")
            
            new_y = svg.block(
                cx, y, inner_w, sh,
                title=sec.get("title", ""),
                lines=sec.get("lines"),
                fill=sec.get("fill", "surface1"),
                highlight=highlight,
                dash=sec.get("dash"),
                comment=sec.get("name", "")
            )
            
            # Store center position for arrow targeting
            section_positions[(ci, sec.get("name", f"sec_{si}"))] = (cx + inner_w // 2, y + sh // 2)
            # Store edge positions too
            section_positions[(ci, sec.get("name", "") + "_right")] = (cx + inner_w, y + sh // 2)
            section_positions[(ci, sec.get("name", "") + "_left")] = (cx, y + sh // 2)
            
            y = new_y + 2  # 2px gap
        
        # Scale note
        if col.get("scale_note"):
            svg.text(col["x_offset"] + col["width"] // 2,
                    cy_start + col["column_height"] + 10,
                    col["scale_note"], size=7, color="overlay0")
    
    # Draw arrows
    for arrow in config.get("arrows", []):
        from_key = (arrow["from_col"], arrow["from_section"])
        to_key = (arrow["to_col"], arrow["to_section"])
        
        # Use edge positions if available, otherwise center
        from_right = section_positions.get((arrow["from_col"], arrow["from_section"] + "_right"))
        to_left = section_positions.get((arrow["to_col"], arrow["to_section"] + "_left"))
        
        if from_right and to_left:
            fx, fy = from_right
            tx, ty = to_left
        else:
            fx, fy = section_positions.get(from_key, (0, 0))
            tx, ty = section_positions.get(to_key, (0, 0))
        
        svg.arrow(fx, fy, tx, ty,
                  stroke=arrow.get("color", "red"),
                  stroke_width=arrow.get("stroke_width", 2.5),
                  dash=arrow.get("dash", "6,3"),
                  curved=arrow.get("curved", True),
                  label=arrow.get("label", ""),
                  label_size=arrow.get("label_size", 8))
    
    # Draw callout (magnified view)
    callout = config.get("callout")
    if callout:
        cy = callout["y"]
        cw = callout.get("width", 600)
        cx = callout.get("x", (w - cw) // 2)
        ch = callout.get("height", 110)
        svg.rect(cx, cy, cw, ch, fill="base", stroke="surface2", rx=4)
        svg.text(cx + cw // 2, cy + 18, callout.get("title", "Detail"),
                size=10, color="text", bold=True)
        
        # Items in the callout
        items = callout.get("items", [])
        ix = cx + 10
        for item in items:
            iw = item.get("width", 100)
            ih = item.get("height", 30)
            svg.block(ix, cy + 30, iw, ih,
                     title=item.get("title", ""),
                     lines=item.get("lines"),
                     highlight=item.get("highlight"))
            ix += iw + 6
    
    # Draw legend
    legend = config.get("legend", [])
    if legend:
        ly = h - 30
        lx = 120
        for item in legend:
            svg.legend_item(lx, ly, item["color"], item["label"])
            lx += 250
    
    svg.write(output_path)


# ═══════════════════════════════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(description="Generate ZX Spectrum knowledge base SVG diagrams")
    parser.add_argument("config", help="Path to JSON config file")
    parser.add_argument("--output", "-o", help="Output SVG path (default: same name as config with .svg)")
    parser.add_argument("--type", "-t", choices=["memory_map"], default="memory_map",
                       help="Diagram type (default: memory_map)")
    args = parser.parse_args()
    
    config_path = Path(args.config)
    if not config_path.exists():
        print(f"Error: {config_path} not found", file=sys.stderr)
        sys.exit(1)
    
    config = json.loads(config_path.read_text())
    
    output = args.output
    if not output:
        output = str(config_path.with_suffix(".svg"))
    
    if args.type == "memory_map":
        gen_memory_map(config, output)


if __name__ == "__main__":
    main()
