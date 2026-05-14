[← Home](../../README.md) · [Display & Timing](README.md)

# Color System — Attributes, Palette, and ULAplus

The ZX Spectrum's color system is one of its most distinctive — and constraining — features. Color is assigned per 8×8 character cell, not per pixel, producing the famous "attribute clash." This article covers the attribute system, the standard palette, and hardware extensions (ULAplus) that lift some restrictions.

---

## Attribute Byte Format

Each 8×8 pixel cell has one attribute byte:

```
  Bit:  7       6       5  4  3       2  1  0
      ┌───────┬───────┬──────────┬───────────┐
      │ FLASH │ BRIGHT│  PAPER   │    INK    │
      └───────┴───────┴──────────┴───────────┘
```

| Bits | Mask | Field | Values |
|------|------|-------|--------|
| 0–2 | `#07` | INK | Foreground color (0–7) |
| 3–5 | `#38` | PAPER | Background color (0–7) |
| 6 | `#40` | BRIGHT | 0 = normal intensity, 1 = bright |
| 7 | `#80` | FLASH | 0 = steady, 1 = ink/paper swap every 16 frames |

### Encoding and Decoding

```z80
; Build attribute byte from components
; A = ink (0-7), B = paper (0-7), C = bright (0/1), D = flash (0/1)
BuildAttr:
    AND  #07             ; Mask ink
    LD   E,A
    LD   A,B
    RLCA : RLCA : RLCA   ; Paper to bits 3-5
    AND  #38
    OR   E               ; Merge ink + paper
    BIT  0,C
    JR   Z,.noBright
    SET  6,A
.noBright:
    BIT  0,D
    JR   Z,.noFlash
    SET  7,A
.noFlash:
    RET
```

```z80
; Decode attribute byte
; A = attribute, returns ink in B, paper in C, bright in D
DecodeAttr:
    LD   B,A
    AND  #07             ; Ink
    LD   B,A             ; B = ink
    LD   A,B
    RRCA : RRCA : RRCA   ; Paper to bits 0-2
    AND  #07
    LD   C,A             ; C = paper
    LD   A,B
    AND  #40
    RLCA
    RLCA                 ; Bright to bit 0
    LD   D,A             ; D = bright (0 or 1)
    RET
```

---

## Standard Color Palette

The ZX Spectrum has 8 colors, each available in normal and bright variants (15 unique colors — bright black is the same as black).

### Color Table

| Code | Normal (BRIGHT=0) | Bright (BRIGHT=1) | Binary |
|------|-------------------|-------------------|--------|
| 0 | Black | Black | 000 |
| 1 | Blue | Bright Blue | 001 |
| 2 | Red | Bright Red | 010 |
| 3 | Magenta (Purple) | Bright Magenta | 011 |
| 4 | Green | Bright Green | 100 |
| 5 | Cyan (Turquoise) | Bright Cyan | 101 |
| 6 | Yellow | Bright Yellow | 110 |
| 7 | White (Off-White) | Bright White | 111 |

### Visual Palette

The Spectrum's 15 unique colors (8 normal + 8 bright, where bright black = normal black):

| Code | Normal (BRIGHT=0) | | | Bright (BRIGHT=1) | | |
|------|-------|-----------|--|-------|-----------|--|
| 0 | ![Black](data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSI0OCIgaGVpZ2h0PSIxNiI+PHJlY3Qgd2lkdGg9IjQ4IiBoZWlnaHQ9IjE2IiBmaWxsPSIjMDAwMDAwIi8+PC9zdmc+) | `#000000` Black | | ![Black](data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSI0OCIgaGVpZ2h0PSIxNiI+PHJlY3Qgd2lkdGg9IjQ4IiBoZWlnaHQ9IjE2IiBmaWxsPSIjMDAwMDAwIi8+PC9zdmc+) | `#000000` Black (same) | |
| 1 | ![Blue](data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSI0OCIgaGVpZ2h0PSIxNiI+PHJlY3Qgd2lkdGg9IjQ4IiBoZWlnaHQ9IjE2IiBmaWxsPSIjMDAwMENDIi8+PC9zdmc+) | `#0000CC` Blue | | ![Bright Blue](data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSI0OCIgaGVpZ2h0PSIxNiI+PHJlY3Qgd2lkdGg9IjQ4IiBoZWlnaHQ9IjE2IiBmaWxsPSIjMzMzM0ZGIi8+PC9zdmc+) | `#3333FF` Bright Blue | |
| 2 | ![Red](data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSI0OCIgaGVpZ2h0PSIxNiI+PHJlY3Qgd2lkdGg9IjQ4IiBoZWlnaHQ9IjE2IiBmaWxsPSIjQ0MwMDAwIi8+PC9zdmc+) | `#CC0000` Red | | ![Bright Red](data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSI0OCIgaGVpZ2h0PSIxNiI+PHJlY3Qgd2lkdGg9IjQ4IiBoZWlnaHQ9IjE2IiBmaWxsPSIjRkYzMzMzIi8+PC9zdmc+) | `#FF3333` Bright Red | |
| 3 | ![Magenta](data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSI0OCIgaGVpZ2h0PSIxNiI+PHJlY3Qgd2lkdGg9IjQ4IiBoZWlnaHQ9IjE2IiBmaWxsPSIjQ0MwMENDIi8+PC9zdmc+) | `#CC00CC` Magenta | | ![Bright Magenta](data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSI0OCIgaGVpZ2h0PSIxNiI+PHJlY3Qgd2lkdGg9IjQ4IiBoZWlnaHQ9IjE2IiBmaWxsPSIjRkYzM0ZGIi8+PC9zdmc+) | `#FF33FF` Bright Magenta | |
| 4 | ![Green](data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSI0OCIgaGVpZ2h0PSIxNiI+PHJlY3Qgd2lkdGg9IjQ4IiBoZWlnaHQ9IjE2IiBmaWxsPSIjMDBDQzAwIi8+PC9zdmc+) | `#00CC00` Green | | ![Bright Green](data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSI0OCIgaGVpZ2h0PSIxNiI+PHJlY3Qgd2lkdGg9IjQ4IiBoZWlnaHQ9IjE2IiBmaWxsPSIjMzNGRjMzIi8+PC9zdmc+) | `#33FF33` Bright Green | |
| 5 | ![Cyan](data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSI0OCIgaGVpZ2h0PSIxNiI+PHJlY3Qgd2lkdGg9IjQ4IiBoZWlnaHQ9IjE2IiBmaWxsPSIjMDBDQ0NDIi8+PC9zdmc+) | `#00CCCC` Cyan | | ![Bright Cyan](data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSI0OCIgaGVpZ2h0PSIxNiI+PHJlY3Qgd2lkdGg9IjQ4IiBoZWlnaHQ9IjE2IiBmaWxsPSIjMzNGRkZGIi8+PC9zdmc+) | `#33FFFF` Bright Cyan | |
| 6 | ![Yellow](data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSI0OCIgaGVpZ2h0PSIxNiI+PHJlY3Qgd2lkdGg9IjQ4IiBoZWlnaHQ9IjE2IiBmaWxsPSIjQ0NDQzAwIi8+PC9zdmc+) | `#CCCC00` Yellow | | ![Bright Yellow](data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSI0OCIgaGVpZ2h0PSIxNiI+PHJlY3Qgd2lkdGg9IjQ4IiBoZWlnaHQ9IjE2IiBmaWxsPSIjRkZGRjMzIi8+PC9zdmc+) | `#FFFF33` Bright Yellow | |
| 7 | ![White](data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSI0OCIgaGVpZ2h0PSIxNiI+PHJlY3Qgd2lkdGg9IjQ4IiBoZWlnaHQ9IjE2IiBmaWxsPSIjQ0NDQ0NDIi8+PC9zdmc+) | `#CCCCCC` White | | ![Bright White](data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSI0OCIgaGVpZ2h0PSIxNiI+PHJlY3Qgd2lkdGg9IjQ4IiBoZWlnaHQ9IjE2IiBmaWxsPSIjRkZGRkZGIi8+PC9zdmc+) | `#FFFFFF` Bright White | |

### Reference Palette Comparison

There is no single authoritative palette — the Spectrum outputs analog RF/composite video, and CRT phosphors, modulator quality, and ULA revision all affect the result. Below are the three most commonly used reference palettes (normal variants):

<!-- base64 prefix shared by all: PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSI0OCIgaGVpZ2h0PSIxNiI+PHJlY3Qgd2lkdGg9IjQ4IiBoZWlnaHQ9IjE2IiBmaWxsPSIj -->
<!-- suffix: Ii8+PC9zdmc+ -->

| Code | Color | FUSE (canonical) | | Skoolkid (CRT-corrected) | | ZEsarUX (warm CRT) | |
|------|-------|-------------------|--|--------------------------|--|---------------------|--|
| 0 | Black | ![FUSE](data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSI0OCIgaGVpZ2h0PSIxNiI+PHJlY3Qgd2lkdGg9IjQ4IiBoZWlnaHQ9IjE2IiBmaWxsPSIjMDAwMDAwIi8+PC9zdmc+) `#000000` | | ![Skoolkid](data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSI0OCIgaGVpZ2h0PSIxNiI+PHJlY3Qgd2lkdGg9IjQ4IiBoZWlnaHQ9IjE2IiBmaWxsPSIjMDAwMDAwIi8+PC9zdmc+) `#000000` | | ![ZEsarUX](data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSI0OCIgaGVpZ2h0PSIxNiI+PHJlY3Qgd2lkdGg9IjQ4IiBoZWlnaHQ9IjE2IiBmaWxsPSIjMDAwMDAwIi8+PC9zdmc+) `#000000` | |
| 1 | Blue | ![FUSE](data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSI0OCIgaGVpZ2h0PSIxNiI+PHJlY3Qgd2lkdGg9IjQ4IiBoZWlnaHQ9IjE2IiBmaWxsPSIjMDAwMENDIi8+PC9zdmc+) `#0000CC` | | ![Skoolkid](data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSI0OCIgaGVpZ2h0PSIxNiI+PHJlY3Qgd2lkdGg9IjQ4IiBoZWlnaHQ9IjE2IiBmaWxsPSIjMDAyNENDIi8+PC9zdmc+) `#0024CC` | | ![ZEsarUX](data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSI0OCIgaGVpZ2h0PSIxNiI+PHJlY3Qgd2lkdGg9IjQ4IiBoZWlnaHQ9IjE2IiBmaWxsPSIjMTQxNEM4Ii8+PC9zdmc+) `#1414C8` | |
| 2 | Red | ![FUSE](data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSI0OCIgaGVpZ2h0PSIxNiI+PHJlY3Qgd2lkdGg9IjQ4IiBoZWlnaHQ9IjE2IiBmaWxsPSIjQ0MwMDAwIi8+PC9zdmc+) `#CC0000` | | ![Skoolkid](data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSI0OCIgaGVpZ2h0PSIxNiI+PHJlY3Qgd2lkdGg9IjQ4IiBoZWlnaHQ9IjE2IiBmaWxsPSIjQ0MwMDAwIi8+PC9zdmc+) `#CC0000` | | ![ZEsarUX](data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSI0OCIgaGVpZ2h0PSIxNiI+PHJlY3Qgd2lkdGg9IjQ4IiBoZWlnaHQ9IjE2IiBmaWxsPSIjQzgxNDE0Ii8+PC9zdmc+) `#C81414` | |
| 3 | Magenta | ![FUSE](data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSI0OCIgaGVpZ2h0PSIxNiI+PHJlY3Qgd2lkdGg9IjQ4IiBoZWlnaHQ9IjE2IiBmaWxsPSIjQ0MwMENDIi8+PC9zdmc+) `#CC00CC` | | ![Skoolkid](data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSI0OCIgaGVpZ2h0PSIxNiI+PHJlY3Qgd2lkdGg9IjQ4IiBoZWlnaHQ9IjE2IiBmaWxsPSIjQ0MyNENDIi8+PC9zdmc+) `#CC24CC` | | ![ZEsarUX](data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSI0OCIgaGVpZ2h0PSIxNiI+PHJlY3Qgd2lkdGg9IjQ4IiBoZWlnaHQ9IjE2IiBmaWxsPSIjQzgxNEM4Ii8+PC9zdmc+) `#C814C8` | |
| 4 | Green | ![FUSE](data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSI0OCIgaGVpZ2h0PSIxNiI+PHJlY3Qgd2lkdGg9IjQ4IiBoZWlnaHQ9IjE2IiBmaWxsPSIjMDBDQzAwIi8+PC9zdmc+) `#00CC00` | | ![Skoolkid](data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSI0OCIgaGVpZ2h0PSIxNiI+PHJlY3Qgd2lkdGg9IjQ4IiBoZWlnaHQ9IjE2IiBmaWxsPSIjMDBDQzI0Ii8+PC9zdmc+) `#00CC24` | | ![ZEsarUX](data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSI0OCIgaGVpZ2h0PSIxNiI+PHJlY3Qgd2lkdGg9IjQ4IiBoZWlnaHQ9IjE2IiBmaWxsPSIjMTRDODE0Ii8+PC9zdmc+) `#14C814` | |
| 5 | Cyan | ![FUSE](data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSI0OCIgaGVpZ2h0PSIxNiI+PHJlY3Qgd2lkdGg9IjQ4IiBoZWlnaHQ9IjE2IiBmaWxsPSIjMDBDQ0NDIi8+PC9zdmc+) `#00CCCC` | | ![Skoolkid](data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSI0OCIgaGVpZ2h0PSIxNiI+PHJlY3Qgd2lkdGg9IjQ4IiBoZWlnaHQ9IjE2IiBmaWxsPSIjMDBDQ0NDIi8+PC9zdmc+) `#00CCCC` | | ![ZEsarUX](data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSI0OCIgaGVpZ2h0PSIxNiI+PHJlY3Qgd2lkdGg9IjQ4IiBoZWlnaHQ9IjE2IiBmaWxsPSIjMTRDOEM4Ii8+PC9zdmc+) `#14C8C8` | |
| 6 | Yellow | ![FUSE](data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSI0OCIgaGVpZ2h0PSIxNiI+PHJlY3Qgd2lkdGg9IjQ4IiBoZWlnaHQ9IjE2IiBmaWxsPSIjQ0NDQzAwIi8+PC9zdmc+) `#CCCC00` | | ![Skoolkid](data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSI0OCIgaGVpZ2h0PSIxNiI+PHJlY3Qgd2lkdGg9IjQ4IiBoZWlnaHQ9IjE2IiBmaWxsPSIjQ0NDQzI0Ii8+PC9zdmc+) `#CCCC24` | | ![ZEsarUX](data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSI0OCIgaGVpZ2h0PSIxNiI+PHJlY3Qgd2lkdGg9IjQ4IiBoZWlnaHQ9IjE2IiBmaWxsPSIjQzhDODE0Ii8+PC9zdmc+) `#C8C814` | |
| 7 | White | ![FUSE](data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSI0OCIgaGVpZ2h0PSIxNiI+PHJlY3Qgd2lkdGg9IjQ4IiBoZWlnaHQ9IjE2IiBmaWxsPSIjQ0NDQ0NDIi8+PC9zdmc+) `#CCCCCC` | | ![Skoolkid](data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSI0OCIgaGVpZ2h0PSIxNiI+PHJlY3Qgd2lkdGg9IjQ4IiBoZWlnaHQ9IjE2IiBmaWxsPSIjQ0NDQ0NDIi8+PC9zdmc+) `#CCCCCC` | | ![ZEsarUX](data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSI0OCIgaGVpZ2h0PSIxNiI+PHJlY3Qgd2lkdGg9IjQ4IiBoZWlnaHQ9IjE2IiBmaWxsPSIjQzhDOEM4Ii8+PC9zdmc+) `#C8C8C8` | |

> [!NOTE]
> For emulator development, **FUSE** palette is the de-facto standard. For hardware-accurate visual reproduction on modern displays, the "CRT-corrected" variants account for phosphor decay and RF signal degradation — real Spectrum output was never as clean as the FUSE hex values suggest.

### Color Bit Encoding

The three color bits map directly to RGB signal lines from the ULA:

```
  Bit 2 = R (Red)
  Bit 1 = G (Green)
  Bit 0 = B (Blue)

  0=Black, 1=Blue, 2=Red, 3=Magenta, 4=Green, 5=Cyan, 6=Yellow, 7=White
```

### ULA Color Generation Hardware

The Ferranti ULA generates color from a simple resistor-ladder DAC. The 3-bit color value plus the BRIGHT flag drive eight output levels through weighted resistors into the RF modulator:

```
BRIGHT=0:  Each RGB channel ≈ 0% or ≈ 33% of maximum
BRIGHT=1:  Each RGB channel ≈ 0% or ≈ 100% of maximum

  Black:       0, 0, 0   (both)
  Blue:       0, 0, 33% →  0, 0, 100%
  Red:       33%, 0, 0  → 100%, 0, 0
  ...
  White:      33% all   → 100% all
```

BRIGHT black is identical to normal black because there is no brightness channel — only the RGB levels change. The "dark" palette (BRIGHT=0) sits at roughly one-third intensity, which is why standard Spectrum colors appear dim on CRT.

> [!NOTE]
> The exact analog levels depend on ULA revision (5C, 6C, 7C), resistor tolerances in the specific machine, and RF modulator quality. No two real Spectrums produce identical colors.

---

## Attribute Clash — The Fundamental Constraint

The attribute system assigns **one ink + one paper color per 8×8 cell**. Within that cell:
- Pixels set to 1 are drawn in INK color
- Pixels set to 0 are drawn in PAPER color

There is no way to have three or more colors in a single 8×8 cell (without BRIGHT providing two palettes). When two objects of different colors overlap within the same cell, one must compromise.

### Clash Example

```
  Cell with green sprite on blue background:
  ┌────────┐
  │..GGGG..│  INK = Green (4)
  │.G..G...│  PAPER = Blue (1)
  │.GGGG...│  → White area must be either blue or green
  │.G...G..│  → Can't have both colors AND a third (e.g., yellow)
  └────────┘
  The best you can do: INK=4, PAPER=1 → green on blue
```

### Workaround Strategies

1. **Character-cell-aligned sprites**: Keep all sprites aligned to 8×8 boundaries so they never share a cell with a differently-colored element
2. **Attribute-preserving drawing**: Read the existing attribute before drawing, modify only what you need
3. **Ditherting**: Use alternating pixel patterns to simulate intermediate colors
4. **Multicolor effects**: Change attributes mid-scanline using timing-precise code (see [multicolor_overview.md](../06_graphics/multicolor_overview.md))
5. **ULAplus**: Hardware extension providing 64 colors and 8×1 attribute resolution on FPGA clones

---

## Border Color

The border surrounds the 256×192 pixel display area. It is a **single solid color** set by port `#FE`:

```z80
; Set border color (0-7)
    LD   A,color         ; Bits 1-3 = border color
    RLCA                 ; Shift to bits 1-3 position
    RLCA
    AND  #38             ; Mask border bits
    ; Merge with other #FE port bits (EAR, MIC) if needed
    OUT  (#FE),A
```

The border color is not part of the attribute system — it's set directly via the ULA port. It cannot have BRIGHT=1 through the port (only 8 colors, not 15). However, some hardware modifications and clones support bright border colors.

See [border_effects.md](border_effects.md) for multicolor border techniques.

---

## ULAplus — 64-Color Palette Extension

ULAplus is a hardware extension implemented in FPGA clones (ZX-Uno, MiSTer, Sizif-512, Harlequin) and some emulators. It adds two major features:

### Feature 1: 64-Color Palette

Instead of the fixed 8-color palette, ULAplus provides a programmable 64-color palette using 2 bits per RGB channel:

```
ULAplus palette entry (6 bits per color):
  Bits 5-4: Red   (0-3)
  Bits 3-2: Green (0-3)
  Bits 1-0: Blue  (0-3)

Total: 64 colors (4 levels × 3 channels)
```

The palette has 64 entries, indexed by the 8 standard colors × 2 brightness levels × ... actually the mapping is:

- 16 palette groups (one per attribute value pattern)
- Each group maps to a specific palette entry
- Total: 64 palette entries for 64 unique RGB combinations

### Programming the ULAplus Palette

```
Port #BF3B (write): Palette register select
  Bits 5-0: Palette entry number (0-63)

Port #FF3B (write): Palette data
  Bits 5-4: Red level (0-3)
  Bits 3-2: Green level (0-3)
  Bits 1-0: Blue level (0-3)

Port #BF3B with bit 7 set: Mode register
  Value 0: Standard ZX Spectrum mode (8 colors + bright)
  Value 1: ULAplus 64-color mode (palette lookup)
```

```z80
; Enable ULAplus mode
    LD   BC,#BF3B
    LD   A,#80           ; Bit 7 set = mode register
    OUT  (C),A
    LD   BC,#FF3B
    LD   A,#01           ; Mode 1 = ULAplus enabled
    OUT  (C),A

; Set palette entry 0 to a custom color (e.g., dark teal)
    LD   BC,#BF3B
    XOR  A               ; Entry 0
    OUT  (C),A
    LD   BC,#FF3B
    LD   A,%001001       ; R=0, G=2, B=1 → dark teal
    OUT  (C),A
```

### Feature 2: 8×1 Attribute Mode

ULAplus can switch from the standard 8×8 attribute grid to an **8×1** grid, giving each pixel row its own attribute byte. This requires 192×32 = 6,144 attribute bytes (same size as the pixel buffer) instead of the standard 768.

```
Standard:    32×24 attributes  =   768 bytes, 8×8 pixel resolution
ULAplus 8×1: 32×192 attributes = 6,144 bytes, 8×1 pixel resolution
```

This eliminates attribute clash almost entirely — each 8-pixel-wide, 1-pixel-tall strip can have its own ink and paper.

> [!NOTE]
> ULAplus is **not available on original Sinclair/Amstrad hardware**. It requires an FPGA-based machine or emulator support. Programs using ULAplus should detect its presence before enabling it.

### Detecting ULAplus

```z80
; Check if ULAplus is present
DetectULAplus:
    LD   BC,#BF3B
    LD   A,#43           ; Write a known pattern
    OUT  (C),A
    LD   BC,#FF3B
    LD   A,#55           ; Test value
    OUT  (C),A
    ; Read back — if ULAplus is present, the register was written
    IN   A,(C)            ; Try to read (may not work — ULAplus is write-only on some implementations)
    ; Alternative: check if mode register accepts value
    LD   BC,#BF3B
    LD   A,#C3           ; Mode select + entry
    OUT  (C),A
    ; If machine doesn't crash, ULAplus is likely present
    ; (This is not a perfect detection — see ULAplus specification)
    RET
```

---

## Timex TS/TC 2068 Extended Modes

The Timex Sinclair 2068 (US) and Timex Computer 2048 (Poland) share hardware with the ZX Spectrum but include an enhanced video chip that adds two extra display modes. These machines are not clones — they are **contemporary Sinclair-licensed designs** with official extended hardware.

### Mode Map

| Mode | Resolution | Attributes | Memory | Notes |
|------|-----------|-------------|--------|-------|
| Standard | 256×192 | 8×8 (standard) | 6.75 KB | Identical to ZX Spectrum |
| HiColor | 256×192 | **8×1** (per pixel row) | 12.25 KB | 6144 extra attribute bytes |
| HiRes | **512×192** | None (2-color per 8×1) | 12.25 KB | Monochrome at double horizontal resolution |

### HiColor Mode (8×1 Attributes)

HiColor assigns a separate attribute byte to each **pixel row** within a character cell, giving 8×1 color resolution instead of 8×8. This eliminates attribute clash within a single cell's vertical span.

```
Standard:   1 attribute per 8×8 cell   =   768 attributes total
HiColor:    8 attributes per 8×8 cell   = 6,144 attributes total
```

The attribute format is identical to the standard Spectrum (INK bits 0-2, PAPER bits 3-5, BRIGHT bit 6, FLASH bit 7), but each of the 192 scanlines has its own 32-byte attribute row.

The display file is reorganized: pixel data remains at `#4000`–`#5AFF` (6,144 bytes, unchanged), but attributes expand from `#5800`–`#5AFF` to a second 6,144-byte block. On the TC2048 this second block is banked into `#6000`–`#77FF`.

### HiRes Mode (512×192)

HiRes doubles the horizontal pixel clock, producing 512 pixels per scanline. There are no attribute bytes — instead, each 8-pixel-wide strip has exactly **two colors**: the foreground (pixel=1) and background (pixel=0) colors are defined by the attribute byte of a secondary display file.

```
Pixel data:   8,192 bytes (512 × 192 / 8)
Color data:   6,144 bytes (one attribute byte per 8×1 strip)
Total:       14,336 bytes
```

This mode is useful for 64-column text and detailed monochrome graphics, but with only 2 colors per 8-pixel strip, it trades the Spectrum's attribute clash for a different constraint.

### Dual Screen

The Timex video chip can hold two complete display files. Port `#FF` controls which screen is active:

```z80
; Port #FF — Timex video mode register
; Bit 0:    Screen select (0 = primary, 1 = secondary)
; Bit 1:    Reserved (must be 0 on TC2048)
; Bits 2-3: Video mode
;   00 = Standard ZX Spectrum
;   01 = Standard with extended attributes
;   10 = HiColor (8×1 attributes)
;   11 = HiRes (512×192)
```

The dual screen enables instant page-flipping: render into the off-screen buffer, then switch with a single port write. No contended-memory tearing since the switch is atomic from the video chip's perspective.

> [!NOTE]
> The TC2048 (Poland) supports all three modes. The TS2068 (US) is nearly identical but with a different ROM. Both machines use the same hardware video chip. Emulators typically support Timex modes via a model selection option.

### Programming Example

```z80
; Switch to HiColor mode on TC2048/TS2068
    LD   BC,#00FF          ; Timex video port
    LD   A,%00001000       ; Bit 3=1, Bit 2=0 → HiColor mode
    OUT  (C),A

; Switch back to standard mode
    LD   A,%00000000
    OUT  (C),A
```

---

## Cross-References

- **Screen layout** (pixel/attribute addressing): [screen_layout.md](../03_memory_and_io/screen_layout.md)
- **48K memory map** (attribute file at #5800): [memory_map_48k.md](../03_memory_and_io/memory_map_48k.md)
- **Border effects** (multicolor borders, raster bars): [border_effects.md](border_effects.md)
- **Multicolor overview** (timing-based attribute changes): [multicolor_overview.md](../06_graphics/multicolor_overview.md)
- **I/O ports** (#FE border register): [io_ports.md](../03_memory_and_io/io_ports.md)
- **Clone video modes** (GigaScreen, ATM hires, TS-Conf): [clone_video_modes.md](clone_video_modes.md)
- **Clone timing** (per-model video timing): [clone_timing.md](../../02_hardware/clones/clone_timing.md)
