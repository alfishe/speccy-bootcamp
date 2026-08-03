[← Home](../README.md) · [References](README.md)

# ZX Spectrum Color Palette — Reference Tables

Quick-reference color tables for all ZX Spectrum palette systems: the standard 15-color attribute palette, the ULAplus 64-color extension, and the ZX Spectrum Next 256-color Layer 2 palette. For the conceptual model (attribute bytes, attribute clash, BRIGHT/FLASH semantics, ULA hardware color generation), see [color_system.md](../05_development/05_display_and_timing/color_system.md).

---

## Standard 15-Colour Palette

The ZX Spectrum's attribute byte encodes **INK (3 bits) + PAPER (3 bits) + BRIGHT (1 bit) + FLASH (1 bit)**. The 3-bit color code selects one of 8 base colors; the BRIGHT flag toggles between the dim and bright variants, giving **15 unique colors** (bright black = normal black):

| Code | Binary | Normal (BRIGHT=0) | Bright (BRIGHT=1) |
|---|---|---|---|
| 0 | `000` | Black | Black (same as normal) |
| 1 | `001` | Blue | Bright Blue |
| 2 | `010` | Red | Bright Red |
| 3 | `011` | Magenta | Bright Magenta |
| 4 | `100` | Green | Bright Green |
| 5 | `101` | Cyan | Bright Cyan |
| 6 | `110` | Yellow | Bright Yellow |
| 7 | `111` | White | Bright White |

The 3 bits map directly to RGB signal lines from the Ferranti ULA: **bit 2 = R, bit 1 = G, bit 0 = B**.

---

## Reference Hex Values

There is no single canonical palette — real Spectrum output is analog RF/composite and varies by ULA revision (5C/6C/7C/8C), resistor tolerance, modulator quality, and CRT phosphor decay. Three emulator reference palettes are in common use:

| Code | Colour | FUSE (canonical) | Skoolkid (CRT-corrected) | ZEsarUX (warm CRT) |
|---|---|---|---|---|
| 0 (Black) | normal | `#000000` | `#000000` | `#000000` |
| 0 (Black) | bright | `#000000` | `#000000` | `#000000` |
| 1 (Blue) | normal | `#0000CC` | `#0024CC` | `#1414C8` |
| 1 (Blue) | bright | `#3333FF` | `#2D2DFF` | `#3838D8` |
| 2 (Red) | normal | `#CC0000` | `#CC0000` | `#C81414` |
| 2 (Red) | bright | `#FF3333` | `#FF2D2D` | `#D83838` |
| 3 (Magenta) | normal | `#CC00CC` | `#CC24CC` | `#C814C8` |
| 3 (Magenta) | bright | `#FF33FF` | `#FF2DFF` | `#D838D8` |
| 4 (Green) | normal | `#00CC00` | `#00CC24` | `#14C814` |
| 4 (Green) | bright | `#33FF33` | `#2DFF2D` | `#38D838` |
| 5 (Cyan) | normal | `#00CCCC` | `#00CCCC` | `#14C8C8` |
| 5 (Cyan) | bright | `#33FFFF` | `#2DFFFF` | `#38D8D8` |
| 6 (Yellow) | normal | `#CCCC00` | `#CCCC24` | `#C8C814` |
| 6 (Yellow) | bright | `#FFFF33` | `#FFFF2D` | `#D8D838` |
| 7 (White) | normal | `#CCCCCC` | `#CCCCCC` | `#C8C8C8` |
| 7 (White) | bright | `#FFFFFF` | `#FFFFFF` | `#D8D8D8` |

> [!NOTE]
> **FUSE** is the de-facto standard for emulator development. **Skoolkid** values account for CRT phosphor decay and RF signal degradation, producing more historically-accurate visuals on modern displays. **ZEsarUX** values use a slightly warmer tint. Pick one and apply consistently across the project.

### Hex Values for the Three-Bit Bright Palette (FUSE)

For convenience, here are the 8-bit values often used in source code and palette files (`.act`, `.gpl`):

```
# Standard 8-colour palette (BRIGHT=0) — FUSE values
00 00 00    ; 0 Black
00 00 CC    ; 1 Blue
CC 00 00    ; 2 Red
CC 00 CC    ; 3 Magenta
00 CC 00    ; 4 Green
00 CC CC    ; 5 Cyan
CC CC 00    ; 6 Yellow
CC CC CC    ; 7 White

# Bright variants (BRIGHT=1) — FUSE values
00 00 00    ; 0 Black (same as normal)
00 00 FF    ; 1 Bright Blue   (#0000CC → bright uses #3333FF, often simplified to #0000FF)
FF 00 00    ; 2 Bright Red
FF 00 FF    ; 3 Bright Magenta
00 FF 00    ; 4 Bright Green
00 FF FF    ; 5 Bright Cyan
FF FF 00    ; 6 Bright Yellow
FF FF FF    ; 7 Bright White
```

> [!TIP]
> The simplified `#0000CC`/`#0000FF` form (no `#33` mix) is widely used in modern Spectrum-adjacent code because it lines up with web/HTML conventions. Use the FUSE values from the table above when matching emulator output exactly.

---

## Border Colour (8 colors)

The border color is set via port `#FE` bits 3-5 (the same encoding as PAPER). It supports only the **8 base colors**, not the bright variants — there is no BRIGHT bit for the border on original Sinclair/Amstrad hardware.

```z80
; Set border to colour N (0-7)
    LD   A,N
    RLCA : RLCA : RLCA     ; Shift colour into bits 3-5
    AND  #38
    OUT  (#FE),A
```

Some clones (Pentagon, ATM Turbo) and FPGA implementations (ZX-Uno, Harlequin) extend port `#FE` decoding to accept a BRIGHT bit for the border, but this is not portable.

---

## ULAplus 64-Colour Palette

ULAplus is a hardware extension implemented in FPGA clones (ZX-Uno, MiSTer, Harlequin, Sizif-512) and several emulators. It adds a **programmable 64-color palette** with 2 bits per RGB channel:

```
ULAplus palette entry format (6 bits):
  Bits 5-4: Red   (0-3)
  Bits 3-2: Green (0-3)
  Bits 1-0: Blue  (0-3)

64 entries × 6 bits = 384 bits of palette storage
```

Each of the 2-bit channel values maps to an output intensity (not strictly linear — see ULAplus spec):

| 2-bit value | Intensity | Hex level (typical) |
|---|---|---|
| `00` | Off | `#00` |
| `01` | Low | `#55` |
| `10` | Medium | `#AA` |
| `11` | Full | `#FF` |

So ULAplus entry `%10 01 10` (R=2, G=1, B=2) = `#AA #55 #AA` = a medium-violet color.

### Palette Mapping to Attribute Bytes

The 16 standard attribute values (8 colors × 2 brightness) are remapped to **16 of the 64 palette entries** in ULAplus mode. The mapping is:

| Attribute byte | ULAplus entry |
|---|---|
| INK=0, BRIGHT=0 | Entry 0 |
| INK=1, BRIGHT=0 | Entry 1 |
| ... | ... |
| INK=7, BRIGHT=0 | Entry 7 |
| INK=0, BRIGHT=1 | Entry 8 |
| ... | ... |
| INK=7, BRIGHT=1 | Entry 15 |

Entries 16-63 are **unused by attribute lookup** but can be programmed and accessed via direct ULAplus port writes (e.g., for static screens, images, demos).

### Programming the ULAplus Palette

```z80
; Enable ULAplus mode
    LD   BC,#BF3B
    LD   A,#80               ; Bit 7 = mode register
    OUT  (C),A
    LD   BC,#FF3B
    LD   A,#01               ; Mode 1 = ULAplus
    OUT  (C),A

; Set palette entry 5 (BRIGHT=0, INK=5 cyan) to a custom teal
    LD   BC,#BF3B
    LD   A,#05               ; Entry 5
    OUT  (C),A
    LD   BC,#FF3B
    LD   A,%00_10_01_10      ; R=0, G=2, B=1 → teal
    OUT  (C),A
```

For ULAplus detection, attribute clash workarounds, and 8×1 attribute mode, see [color_system.md](../05_development/05_display_and_timing/color_system.md).

---

## ZX Spectrum Next 256-Colour Palette

The ZX Spectrum Next (2017–2020) provides a **256-color indexed palette** for its Layer 2 (256×192, 8-bpp) and enhanced attribute modes. Each palette entry is a **24-bit RGB888** value stored in three NextReg writes.

### Layer 2 Palette Encoding

The 256 palette entries are indexed by an 8-bit value (0-255). Each entry is 24-bit RGB with 8 bits per channel. The default palette provides a smooth gradient plus the standard 15 Spectrum colors.

| Index range | Default contents |
|---|---|
| 0–15 | Standard Spectrum colors (matches FUSE palette above) |
| 16–127 | Smooth gradients across the RGB cube |
| 128–255 | Reserved / additional gradients |

### Programming the Next Palette

The Next palette is programmed via the `NextReg` mechanism (ports `#243B` select, `#253B` data):

```z80
; Set NextReg $40 (palette index 0, first entry) to pure red #FF0000
    LD   BC,#243B            ; NextReg select port
    LD   A,#40               ; NextReg $40 = palette index 0 register
    OUT  (C),A
    LD   BC,#253B            ; NextReg data port
    LD   A,#FF               ; R = 255 (first write = red)
    OUT  (C),A
    ; Next two writes are G and B (auto-incrementing register pointer)
    LD   A,#00               ; G = 0
    OUT  (C),A
    LD   A,#00               ; B = 0
    OUT  (C),A
```

The palette index auto-increments after each 3-byte write, allowing fast bulk palette uploads.

### Layer 2 vs Layer 1 (ULA) Palette Independence

On the Next, Layer 2 has its own **separate 256-entry palette** that does not affect the ULA (Layer 1) display. The Next can display both layers simultaneously with different palettes, enabling full-color sprites over attribute-constrained backgrounds.

### Per-Scanline Palette via Copper

The Next's **copper coprocessor** can rewrite palette entries at specific scanlines, enabling per-scanline color cycling (e.g., copper-bar effects, horizon gradients). See [video_frame_next.md](../05_development/05_display_and_timing/video_frame_next.md) for the copper instruction set and timing.

For complete Next hardware details (Layer 2, sprites, tilemap, copper, DMA), see [memory_and_io_next.md](../05_development/03_memory_and_io/memory_and_io_next.md).

---

## Timex TS/TC 2068 Extended Modes

The Timex Sinclair 2068 (US) and Timex Computer 2048 (Poland) use the **same 15-color palette** as the standard Spectrum but with two extended display modes that change **how** attributes are arranged (not the colors themselves):

| Mode | Attributes | Notes |
|---|---|---|
| Standard | 8×8 cells | Same as ZX Spectrum |
| HiColor | 8×1 cells | 6,144 attribute bytes, eliminates vertical attribute clash |
| HiRes | 2 colors per 8×1 strip | 512×192 pixel resolution, no separate attribute bytes |

The color values and palette are identical — only the addressing changes. See [color_system.md](../05_development/05_display_and_timing/color_system.md) for details.

---

## Cross-References

- **Conceptual color model** (attribute byte format, attribute clash, BRIGHT/FLASH semantics, ULA hardware generation): [color_system.md](../05_development/05_display_and_timing/color_system.md)
- **Border effects** (multicolor border code, raster bars, sync techniques): [border_effects.md](../05_development/05_display_and_timing/border_effects.md)
- **Screen layout** (pixel/attribute byte addressing): [screen_layout.md](../05_development/03_memory_and_io/screen_layout.md)
- **I/O port map** (#FE border register, ULAplus #BF3B/#FF3B, Next #243B/#253B): [io_port_map.md](io_port_map.md)
- **ZX Spectrum Next memory map** (Layer 2, sprites, copper): [memory_and_io_next.md](../05_development/03_memory_and_io/memory_and_io_next.md)
- **ZX Spectrum Next video frame** (copper, configurable timing): [video_frame_next.md](../05_development/05_display_and_timing/video_frame_next.md)
