#!/usr/bin/env python3
"""
ZX Spectrum Knowledge Base — Schematic SVG Generator

Renders gate-level logic diagrams (74-series / Soviet equivalents) as
Catppuccin Mocha SVG for embedding in Markdown via <img> tags.

Usage:
    python3 tools/svg_gen/gen_schematic.py tools/svg_gen/schematic_48k_decoding.json \
        -o 05_development/03_memory_and_io/assets/48k_port_decoding.svg
"""

import sys
import json
import argparse
from pathlib import Path

# ═══════════════════════════════════════════════════════════════════════
# DESIGN SYSTEM — Catppuccin Mocha (shared with gen_svg.py)
# ═══════════════════════════════════════════════════════════════════════

PALETTE = {
    "base":       "#1e1e2e",
    "mantle":     "#181825",
    "crust":      "#11111b",
    "surface0":   "#313244",
    "surface1":   "#45475a",
    "surface2":   "#585b70",
    "overlay0":   "#6c7086",
    "overlay1":   "#7f849c",
    "overlay2":   "#9399b2",
    "subtext0":   "#a6adc8",
    "subtext1":   "#bac2de",
    "text":       "#cdd6f4",
    "lavender":   "#b4befe",
    "blue":       "#89b4fa",
    "sapphire":   "#74c7ec",
    "sky":        "#89dceb",
    "teal":       "#94e2d5",
    "green":      "#a6e3a1",
    "yellow":     "#f9e2af",
    "peach":      "#fab387",
    "maroon":     "#eba0ac",
    "red":        "#f38ba8",
    "mauve":      "#cba6f7",
    "pink":       "#f5c2e7",
    "flamingo":   "#f2cdcd",
    "rosewater":  "#f5e0dc",
}

FONT = "'Menlo','Consolas','Courier New',monospace"

# ═══════════════════════════════════════════════════════════════════════
# SVG BUILDER
# ═══════════════════════════════════════════════════════════════════════

class SchematicSVG:
    """SVG builder for schematic diagrams with Catppuccin styling."""

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
            self.text(width // 2, 28, title, size=14, color="text",
                      bold=True, anchor="middle")

    # ── Color resolution ─────────────────────────────────────────────

    @staticmethod
    def _color(name):
        return PALETTE.get(name, name)

    # ── Primitives ────────────────────────────────────────────────────

    def rect(self, x, y, w, h, *, fill="surface1", stroke="overlay0",
             stroke_width=1, rx=3, fill_opacity=None, dash=None):
        fill = self._color(fill)
        stroke = self._color(stroke)
        attrs = [f'x="{x}"', f'y="{y}"', f'width="{w}"', f'height="{h}"',
                 f'fill="{fill}"', f'stroke="{stroke}"',
                 f'stroke-width="{stroke_width}"', f'rx="{rx}"']
        if fill_opacity is not None:
            attrs.append(f'fill-opacity="{fill_opacity}"')
        if dash:
            if isinstance(dash, bool):
                attrs.append('stroke-dasharray="4,3"')
            else:
                attrs.append(f'stroke-dasharray="{dash}"')
        self.parts.append(f'  <rect {" ".join(attrs)}/>')

    def text(self, x, y, content, *, size=10, color="overlay2",
             bold=False, anchor="middle", text_decoration=None):
        color = self._color(color)
        weight = ' font-weight="bold"' if bold else ''
        deco = f' text-decoration="{text_decoration}"' if text_decoration else ''
        content = (content.replace("&", "&amp;").replace("<", "&lt;")
                          .replace(">", "&gt;"))
        self.parts.append(
            f'  <text x="{x}" y="{y}" text-anchor="{anchor}" '
            f'fill="{color}" font-size="{size}"{weight}{deco}>'
            f'{content}</text>')

    def line(self, x1, y1, x2, y2, *, stroke="overlay2", stroke_width=1.5,
             dash=None):
        stroke = self._color(stroke)
        attrs = [f'x1="{x1}"', f'y1="{y1}"', f'x2="{x2}"', f'y2="{y2}"',
                 f'stroke="{stroke}"', f'stroke-width="{stroke_width}"']
        if dash:
            attrs.append(f'stroke-dasharray="{dash}"')
        self.parts.append(f'  <line {" ".join(attrs)}/>')

    def polyline(self, points, *, stroke="overlay2", stroke_width=1.5,
                 fill="none", dash=None):
        stroke = self._color(stroke)
        fill = self._color(fill) if fill != "none" else "none"
        pts = " ".join(f"{x},{y}" for x, y in points)
        attrs = [f'points="{pts}"', f'stroke="{stroke}"',
                 f'stroke-width="{stroke_width}"', f'fill="{fill}"']
        if dash:
            attrs.append(f'stroke-dasharray="{dash}"')
        self.parts.append(f'  <polyline {" ".join(attrs)}/>')

    def path(self, d, *, stroke="overlay2", stroke_width=1.5,
             fill="none", dash=None):
        stroke = self._color(stroke)
        fill = self._color(fill) if fill != "none" else "none"
        attrs = [f'd="{d}"', f'stroke="{stroke}"',
                 f'stroke-width="{stroke_width}"', f'fill="{fill}"']
        if dash:
            attrs.append(f'stroke-dasharray="{dash}"')
        self.parts.append(f'  <path {" ".join(attrs)}/>')

    def circle(self, cx, cy, r, *, fill="base", stroke="overlay2",
               stroke_width=1.5):
        fill = self._color(fill)
        stroke = self._color(stroke)
        self.parts.append(
            f'  <circle cx="{cx}" cy="{cy}" r="{r}" '
            f'fill="{fill}" stroke="{stroke}" '
            f'stroke-width="{stroke_width}"/>')

    def comment(self, text):
        self.parts.append(f'  <!-- {text} -->')

    def section_comment(self, text):
        self.parts.append(f'')
        self.parts.append(f'  <!-- {"=" * 5} {text} {"=" * 5} -->')

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
# GATE RENDERERS — IEEE/ANSI logic symbols
# ═══════════════════════════════════════════════════════════════════════

# Gate dimensions (constants)
GATE_W = 44          # gate body width
NOT_LEN = 36          # NOT triangle length
NOT_BASE = 24        # NOT triangle base height
BUBBLE_R = 4         # inversion bubble radius
PIN_SPACING = 14     # vertical spacing between input pins
CHIP_PAD = 8         # padding inside MSI chip boxes
STUB_LEN = 18        # pin stub length (line from body to connection point)

class GateRenderer:
    """Renders IEEE/ANSI logic gate symbols onto a SchematicSVG."""

    def __init__(self, svg: SchematicSVG):
        self.svg = svg
        # Track pin positions: { (comp_id, pin_name): (x, y) }
        self.pins = {}

    def _register_pin(self, comp_id, pin_name, x, y):
        self.pins[(comp_id, pin_name)] = (x, y)

    def get_pin(self, comp_id, pin_name):
        return self.pins.get((comp_id, pin_name))

    # ── NOT / Buffer ──────────────────────────────────────────────────

    def draw_not(self, comp_id, x, y, *, label="", inputs=1):
        """
        Draw a NOT gate (inverter) or buffer.

        For a NOT gate: triangle pointing right with a bubble on output.
        For a buffer (if used as type 'buffer'): triangle without bubble.

        Layout (NOT, single input):
            input pin ──►|>o── output pin

        Pin positions registered:
            (id, "in0")   — left center
            (id, "out")    — right center (after bubble)
        """
        svg = self.svg
        is_inverter = True  # NOT gates always invert

        # Triangle body
        tri_len = NOT_LEN
        tri_half = NOT_BASE // 2

        # Triangle points: left-center, right-top, right-bottom
        svg.path(
            f"M {x} {y} L {x + tri_len} {y - tri_half} "
            f"L {x + tri_len} {y + tri_half} Z",
            stroke="overlay2", fill="base", stroke_width=1.5
        )

        # Input stub (line extending left from triangle apex)
        svg.line(x - STUB_LEN, y, x, y, stroke="overlay2", stroke_width=1.5)
        self._register_pin(comp_id, "in0", x - STUB_LEN, y)

        if is_inverter:
            # Bubble on output
            bx = x + tri_len + BUBBLE_R
            svg.circle(bx, y, BUBBLE_R, fill="base", stroke="overlay2")
            out_body = bx + BUBBLE_R
        else:
            out_body = x + tri_len

        # Output stub (line extending right from bubble/tip)
        svg.line(out_body, y, out_body + STUB_LEN, y, stroke="overlay2",
                 stroke_width=1.5)
        self._register_pin(comp_id, "out", out_body + STUB_LEN, y)

        # Label above or below
        if label:
            svg.text(x + tri_len // 2, y - tri_half - 6, label,
                     size=7, color="subtext0", anchor="middle")

    # ── AND / NAND ────────────────────────────────────────────────────

    def draw_and(self, comp_id, x, y, *, label="", inputs=2, nand=False):
        """
        Draw an AND or NAND gate with configurable inputs (2-8).

        AND:  flat left side, curved (D-shape) right side.
        NAND: same shape with a bubble on output.

        Layout (2-input AND):
            in0 ──╮
                  │)D── out
            in1 ──╯

        Pin positions registered:
            (id, "in0")..(id, "inN")  — left side, evenly spaced
            (id, "out")               — right center
        """
        svg = self.svg
        n = max(2, min(inputs, 8))
        h = (n - 1) * PIN_SPACING + 20  # total gate height
        half_h = h / 2
        w = GATE_W

        # Build D-shape path: flat left, curved right
        # Left side goes from (x, y-half_h) to (x, y+half_h)
        # Right side is a semicircular arc bulging right to (x+w, y)
        top = y - half_h
        bot = y + half_h
        right = x + w

        # D-shape: flat left edge, curved right edge
        # The arc starts at (x, top) going right, curves to (x, bot)
        # Control: the rightmost point should be at approximately x+w
        arc_rx = w * 0.55  # horizontal radius of the arc
        d_path = (
            f"M {x} {top} "
            f"L {right - arc_rx} {top} "  # horizontal to where arc starts
            f"A {arc_rx} {half_h} 0 0 1 {right - arc_rx} {bot} "  # arc to bottom
            f"L {x} {bot} Z"  # flat bottom back to left
        )
        svg.path(d_path, stroke="overlay2", fill="base", stroke_width=1.5)

        # Input stubs (lines extending left from flat left side)
        for i in range(n):
            if n == 1:
                py = y
            else:
                py = top + 10 + i * PIN_SPACING
            svg.line(x - STUB_LEN, py, x, py, stroke="overlay2", stroke_width=1.5)
            self._register_pin(comp_id, f"in{i}", x - STUB_LEN, py)

        # Output: at the rightmost point of the arc (x + w, y)
        out_tip_x = right
        # NAND bubble on output (if applicable)
        if nand:
            svg.circle(out_tip_x, y, BUBBLE_R, fill="base", stroke="overlay2")
            out_body = out_tip_x + BUBBLE_R
        else:
            out_body = out_tip_x

        # Output stub (line extending right from arc tip or bubble)
        svg.line(out_body, y, out_body + STUB_LEN, y, stroke="overlay2",
                 stroke_width=1.5)
        self._register_pin(comp_id, "out", out_body + STUB_LEN, y)

        # Label
        if label:
            svg.text(x + w * 0.3, y - half_h - 6, label,
                     size=7, color="subtext0", anchor="middle")

    # ── OR / NOR / XOR ────────────────────────────────────────────────

    def draw_or(self, comp_id, x, y, *, label="", inputs=2, nor=False,
                xor=False):
        """
        Draw an OR / NOR / XOR gate with configurable inputs (2-8).

        OR:  curved shield shape (curved left input side, pointed right).
        NOR: same with bubble on output.
        XOR: extra curved line on left side.

        Layout (2-input OR):
            in0 ──╮
                  │)── out
            in1 ──╯

        Pin positions registered:
            (id, "in0")..(id, "inN")  — left side, along input curve
            (id, "out")               — right tip
        """
        svg = self.svg
        n = max(2, min(inputs, 8))
        h = (n - 1) * PIN_SPACING + 20
        half_h = h / 2
        w = GATE_W

        top = y - half_h
        bot = y + half_h

        # OR shield shape: curved left, pointed right
        # Left curve (input side): concave arc from top to bottom
        # Top edge: slight curve from left-top to right tip
        # Bottom edge: slight curve from right tip to left-bottom
        # Right: comes to a point at (x+w, y)

        # Control points for the left (input) curve
        cx1 = x + w * 0.15  # how much the left side bows inward

        # Top curve: from (x, top) to (x+w, y)
        # Bottom curve: from (x+w, y) to (x, bot)
        # Left curve: from (x, bot) back to (x, top) bowing right
        or_path = (
            f"M {x} {top} "
            f"Q {x + w * 0.7} {top} {x + w} {y} "   # top curve to tip
            f"Q {x + w * 0.7} {bot} {x} {bot} "      # bottom curve from tip
            f"Q {cx1} {y} {x} {top} Z"              # left curve (input side)
        )
        svg.path(or_path, stroke="overlay2", fill="base", stroke_width=1.5)

        # XOR extra curve (parallel to left side, slightly offset)
        if xor:
            offset = 6
            svg.path(
                f"M {x + offset} {top + 2} Q {cx1 + offset} {y} {x + offset} {bot - 2}",
                stroke="overlay2", fill="none", stroke_width=1.5
            )

        # Input stubs along the left curve
        for i in range(n):
            if n == 1:
                py = y
            else:
                py = top + 10 + i * PIN_SPACING
            # Offset x slightly to account for the curve
            t = (py - top) / h if h > 0 else 0.5
            curve_offset = 4 * (1 - abs(2 * t - 1))  # parabolic
            body_x = x - curve_offset
            stub_x = body_x - STUB_LEN
            svg.line(stub_x, py, body_x, py, stroke="overlay2", stroke_width=1.5)
            self._register_pin(comp_id, f"in{i}", stub_x, py)

        # Output: right tip
        out_body = x + w
        if nor:
            svg.circle(out_body + BUBBLE_R, y, BUBBLE_R, fill="base",
                       stroke="overlay2")
            out_body = out_body + BUBBLE_R * 2
        # Output stub (line extending right from tip or bubble)
        svg.line(out_body, y, out_body + STUB_LEN, y, stroke="overlay2",
                 stroke_width=1.5)
        self._register_pin(comp_id, "out", out_body + STUB_LEN, y)

        # Label
        if label:
            svg.text(x + w * 0.4, y - half_h - 6, label,
                     size=7, color="subtext0", anchor="middle")

    # ── MSI Chip (IC package box) ────────────────────────────────────

    def draw_chip(self, comp_id, x, y, *, chip_type="74138", label="",
                  left_pins=None, right_pins=None, width=90):
        """
        Draw an MSI chip as a rectangular IC package with labeled pins.

        chip_type: determines default pin layout if pins not specified.
            "74138" — 3-to-8 decoder (A,B,C inputs left, Y0-Y7 outputs right,
                       G1,/G2A,/G2B enables left)
            "74688" — 8-bit comparator (P0-P7, Q0-Q7 left, enable, output right)
            "7474"  — Dual D-type flip-flop (D, CLK, /CLR, /PRE left, Q, /Q right)

        Custom pins can override defaults:
            left_pins:  [("pin_name", ...)]  — pins on left side, top to bottom
            right_pins: [("pin_name", ...)]  — pins on right side, top to bottom

        Pin positions registered:
            (id, pin_name) for each pin — on the edge of the box
        """
        svg = self.svg

        # Default pin layouts per chip type
        if left_pins is None or right_pins is None:
            defaults = {
                "74138": {
                    "left": ["A", "B", "C", "G1", "/G2A", "/G2B"],
                    "right": ["Y7", "Y6", "Y5", "Y4", "Y3", "Y2", "Y1", "Y0"],
                },
                "74688": {
                    "left": ["P0", "P1", "P2", "P3", "P4", "P5", "P6", "P7"],
                    "right": ["Q0", "Q1", "Q2", "Q3", "Q4", "Q5", "Q6", "Q7", "/G", "/P=Q"],
                },
                "7474": {
                    "left": ["1D", "1CLK", "/1CLR", "/1PRE", "2D", "2CLK", "/2CLR", "/2PRE"],
                    "right": ["1Q", "/1Q", "2Q", "/2Q"],
                },
            }
            pin_def = defaults.get(chip_type, {"left": [], "right": []})
            if left_pins is None:
                left_pins = pin_def["left"]
            if right_pins is None:
                right_pins = pin_def["right"]

        n_pins = max(len(left_pins), len(right_pins))
        chip_h = n_pins * PIN_SPACING + 2 * CHIP_PAD
        chip_w = width

        top = y - chip_h / 2
        bot = y + chip_h / 2

        # Draw chip body
        svg.rect(x, top, chip_w, chip_h, fill="surface0",
                 stroke="overlay2", stroke_width=1.5, rx=2)

        # Chip label (type designation) centered in body
        chip_label = label or chip_type
        # Split label on " / " to show western and soviet names on separate lines
        label_parts = chip_label.split(" / ")
        if len(label_parts) == 2:
            svg.text(x + chip_w // 2, y - 8, label_parts[0], size=9,
                     color="text", bold=True, anchor="middle")
            svg.text(x + chip_w // 2, y + 6, label_parts[1], size=8,
                     color="overlay2", anchor="middle")
        else:
            svg.text(x + chip_w // 2, y - 4, chip_label, size=9,
                     color="text", bold=True, anchor="middle")
            # Sub-label (function)
            if label and chip_type != label:
                svg.text(x + chip_w // 2, y + 10, chip_type, size=7,
                         color="overlay2", anchor="middle")

        # Draw left pins: stub line extends left from body, label outside
        for i, pin_name in enumerate(left_pins):
            py = top + CHIP_PAD + i * PIN_SPACING + 4
            # Stub line from body edge extending left
            svg.line(x - STUB_LEN, py, x, py, stroke="overlay2", stroke_width=1.5)
            # Pin label inside chip body (near left edge)
            svg.text(x + 4, py + 3, pin_name, size=7, color="overlay2",
                     anchor="start")
            # Register pin position at end of stub
            self._register_pin(comp_id, pin_name, x - STUB_LEN, py)

        # Draw right pins: stub line extends right from body, label outside
        for i, pin_name in enumerate(right_pins):
            py = top + CHIP_PAD + i * PIN_SPACING + 4
            # Stub line from body edge extending right
            svg.line(x + chip_w, py, x + chip_w + STUB_LEN, py,
                     stroke="overlay2", stroke_width=1.5)
            # Pin label inside chip body (near right edge)
            svg.text(x + chip_w - 4, py + 3, pin_name, size=7,
                     color="overlay2", anchor="end")
            # Register pin position at end of stub
            self._register_pin(comp_id, pin_name, x + chip_w + STUB_LEN, py)

        return chip_h

    # ── Wire drawing helpers ──────────────────────────────────────────

    def draw_wire(self, x1, y1, x2, y2, *, label="", color="overlay2",
                  bus_bits=0, dash=None, active_low=False):
        """
        Draw a wire (line or bus) between two points.

        bus_bits > 0: draw as a bus with a slash and bit count.
        active_low: draw label with overbar.
        """
        svg = self.svg
        stroke_w = 2.0 if bus_bits > 0 else 1.5
        svg.line(x1, y1, x2, y2, stroke=color, stroke_width=stroke_w,
                 dash=dash)

        if bus_bits > 0:
            # Bus slash notation at midpoint
            mx = (x1 + x2) / 2
            my = (y1 + y2) / 2
            # Small slash line
            svg.line(mx - 3, my + 5, mx + 3, my - 5, stroke=color,
                     stroke_width=1)
            svg.text(mx + 6, my + 3, str(bus_bits), size=7, color=color,
                     anchor="start")

        if label:
            mx = (x1 + x2) / 2
            my = (y1 + y2) / 2
            offset = -8 if not active_low else -10
            deco = "overline" if active_low else None
            svg.text(mx, my + offset, label, size=7, color=color,
                     anchor="middle", text_decoration=deco)

    def draw_junction(self, x, y, *, color="overlay2"):
        """Draw a junction dot (where wires connect)."""
        self.svg.circle(x, y, 3, fill=color, stroke=color, stroke_width=0)

    def draw_port_label(self, x, y, label, *, direction="in", color="text",
                        active_low=False):
        """
        Draw an external port label (input or output arrow + text).
        direction: "in" (arrow pointing right) or "out" (arrow pointing right).
        """
        svg = self.svg
        deco = "overline" if active_low else None
        if direction == "in":
            svg.text(x - 4, y + 3, label, size=8, color=color,
                     anchor="end", text_decoration=deco)
        else:
            svg.text(x + 4, y + 3, label, size=8, color=color,
                     anchor="start", text_decoration=deco)

    def draw_annotation(self, x, y, text, *, color="overlay2", size=8):
        """Draw an annotation note (italic-style comment)."""
        self.svg.text(x, y, text, size=size, color=color, anchor="start")

    # ── Dispatch component draw by type ─────────────────────────────

    def draw_component(self, comp):
        """Draw a component based on its config dict. Returns the renderer."""
        cid = comp["id"]
        ctype = comp["type"]
        x = comp["x"]
        y = comp["y"]
        label = comp.get("label", "")

        if ctype == "not":
            self.draw_not(cid, x, y, label=label)
        elif ctype == "buffer":
            self.draw_not(cid, x, y, label=label)
        elif ctype == "and":
            self.draw_and(cid, x, y, label=label,
                          inputs=comp.get("inputs", 2))
        elif ctype == "nand":
            self.draw_and(cid, x, y, label=label,
                          inputs=comp.get("inputs", 2), nand=True)
        elif ctype == "or":
            self.draw_or(cid, x, y, label=label,
                         inputs=comp.get("inputs", 2))
        elif ctype == "nor":
            self.draw_or(cid, x, y, label=label,
                         inputs=comp.get("inputs", 2), nor=True)
        elif ctype == "xor":
            self.draw_or(cid, x, y, label=label,
                         inputs=comp.get("inputs", 2), xor=True)
        elif ctype in ("74138", "74688", "7474"):
            self.draw_chip(cid, x, y, chip_type=ctype, label=label,
                           left_pins=comp.get("left_pins"),
                           right_pins=comp.get("right_pins"),
                           width=comp.get("width", 90))
        else:
            print(f"Warning: unknown component type '{ctype}'", file=sys.stderr)

# ═══════════════════════════════════════════════════════════════════════
# SCHEMATIC GENERATOR
# ═══════════════════════════════════════════════════════════════════════

def _parse_pin_ref(ref, renderer):
    """Parse a pin reference like 'comp_id.pin_name' into (x, y)."""
    if "." in ref:
        comp_id, pin_name = ref.split(".", 1)
        pos = renderer.get_pin(comp_id, pin_name)
        if pos:
            return pos
    print(f"Warning: pin '{ref}' not found", file=sys.stderr)
    return (0, 0)


def gen_schematic(config, output_path):
    """
    Generate a schematic diagram from config dict.

    Config structure:
    {
        "title": "48K ULA Port #FE Decoding",
        "width": 500,
        "height": 300,
        "components": [ ... ],   // Gates and chips
        "wires": [ ... ],        // Connections
        "ports": [ ... ],        // External I/O labels
        "annotations": [ ... ]   // Text notes
    }
    """
    w = config.get("width", 600)
    h = config.get("height", 400)
    svg = SchematicSVG(w, h, config.get("title", ""))
    renderer = GateRenderer(svg)

    # ── Phase 0: Register port positions as pins (so wires can reference them) ─
    for port in config.get("ports", []):
        renderer._register_pin("port", port["id"], port["x"], port["y"])

    # ── Phase 1: Draw all components (registers pin positions) ───────
    for comp in config.get("components", []):
        svg.section_comment(f"Component: {comp['id']}")
        renderer.draw_component(comp)

    # ── Phase 2: Draw wires ──────────────────────────────────────────
    for wire in config.get("wires", []):
        svg.section_comment(f"Wire")

        if "from" in wire and "to" in wire:
            # Pin-to-pin wire
            x1, y1 = _parse_pin_ref(wire["from"], renderer)
            x2, y2 = _parse_pin_ref(wire["to"], renderer)

            # Route: horizontal first, then vertical, then horizontal
            # (Manhattan routing)
            mid_x = wire.get("mid_x", (x1 + x2) / 2)
            points = [(x1, y1), (mid_x, y1), (mid_x, y2), (x2, y2)]

            color = wire.get("color", "overlay2")
            for i in range(len(points) - 1):
                px1, py1 = points[i]
                px2, py2 = points[i + 1]
                if px1 != px2 or py1 != py2:
                    svg.line(px1, py1, px2, py2, stroke=color,
                             stroke_width=2.0 if wire.get("bus_bits", 0) > 0 else 1.5)

            # Bus slash notation
            bus_bits = wire.get("bus_bits", 0)
            if bus_bits > 0:
                mx = mid_x
                my = (y1 + y2) / 2
                svg.line(mx - 3, my + 5, mx + 3, my - 5, stroke=color,
                         stroke_width=1)
                svg.text(mx + 6, my + 3, str(bus_bits), size=7,
                         color=color, anchor="start")

            # Wire label
            label = wire.get("label", "")
            if label:
                lx = mid_x
                ly = min(y1, y2) - 8
                deco = "overline" if wire.get("active_low") else None
                svg.text(lx, ly, label, size=7, color=color,
                         anchor="middle", text_decoration=deco)

        elif "points" in wire:
            # Explicit polyline wire
            pts = wire["points"]
            color = wire.get("color", "overlay2")
            svg.polyline(pts, stroke=color, stroke_width=1.5,
                         dash=wire.get("dash"))

    # ── Phase 3: Draw junction dots ──────────────────────────────────
    for junc in config.get("junctions", []):
        renderer.draw_junction(junc["x"], junc["y"],
                               color=junc.get("color", "overlay2"))

    # ── Phase 4: Draw external port labels ───────────────────────────
    for port in config.get("ports", []):
        renderer.draw_port_label(
            port["x"], port["y"], port["label"],
            direction=port.get("direction", "in"),
            color=port.get("color", "text"),
            active_low=port.get("active_low", False))

    # ── Phase 5: Draw annotations ────────────────────────────────────
    for ann in config.get("annotations", []):
        renderer.draw_annotation(
            ann["x"], ann["y"], ann["text"],
            color=ann.get("color", "overlay2"),
            size=ann.get("size", 8))

    svg.write(output_path)


def main():
    parser = argparse.ArgumentParser(
        description="Generate ZX Spectrum schematic SVG diagrams")
    parser.add_argument("config", help="Path to JSON config file")
    parser.add_argument("--output", "-o",
                        help="Output SVG path (default: same stem as config)")
    args = parser.parse_args()

    config_path = Path(args.config)
    if not config_path.exists():
        print(f"Error: {config_path} not found", file=sys.stderr)
        sys.exit(1)

    config = json.loads(config_path.read_text())
    output = args.output or str(config_path.with_suffix(".svg"))

    gen_schematic(config, output)


if __name__ == "__main__":
    main()
