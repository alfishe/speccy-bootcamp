[← Home](../../README.md) · [Graphics](README.md)

# Multicolor Engines — Game-Programmer Perspective

This article is the **direct continuation of [race_the_beam.md](../04_interrupts/race_the_beam.md)** from the F11 Interrupt Programming series. That article covered the *foundations*: T-state budgets, ISR synchronization strategies, and the five race-the-beam patterns used in commercial 1980s games. This article covers what came next: **published multicolor engines** that game programmers can drop into their own code, plus the modern hardware-assisted extensions (ULAplus, Timex HiColor) that lift the constraint without requiring cycle-exact code.

The boundary between articles is sharp: raster timing theory lives in [race_the_beam.md](../04_interrupts/race_the_beam.md) and [07_demoscene/multicolor_techniques.md](../../07_demoscene/multicolor_techniques.md); here we focus on the **engines themselves** — what they offer, how to use them, which games shipped with them.

> [!NOTE]
> If you are writing a game and want higher color resolution than the stock 8×8 attribute cell provides, this article tells you what your options are. If you want to understand *why* 8×1 multicolor is hard, read [race_the_beam.md](../04_interrupts/race_the_beam.md) first.

---

## The Engine Survey

Four published engines dominate modern multicolor game development on the ZX Spectrum. Each makes a different tradeoff between color resolution, playable area, and ease of use.

| Engine | Resolution | Playable area | Year | Author | Use case |
|---|---|---|---|---|---|
| **BIFROST\\*** | 8×1 | 18 cols × 18 rows (~56% screen) | 2012 | Einar Saukas | Maximum color detail, small playfield |
| **NIRVANA+** | 8×2 | 32 cols × 23 rows (~full screen) | 2015 | Einar Saukas | Larger playfield, accepts 8×2 tradeoff |
| **ZXodus** | 8×1 | configurable | 2011 | Andrew Owen | Pre-BIFROST* alternative, scanline palette |
| **ULAplus** | hardware | hardware (no CPU cost) | 2008 | Andrew Owen | Modern FPGA clones only — palette extension |

The choice is dictated by hardware: BIFROST* and NIRVANA+ work on **any stock Spectrum** (48K, 128K, +2, +2A, +3) using CPU-driven raster-synchronized attribute writes. ULAplus requires a **FPGA-based clone or emulator** that implements the extended palette register — it does not work on original Sinclair hardware.

---

## BIFROST* Engine

**BIFROST\*** is Einar Saukas's multicolor 8×1 graphics engine, first released in 2012. It is open source and royalty-free, including for commercial use.

### Specifications

- **Color resolution**: 8×1 (each scanline within an 8×8 cell can have its own INK/PAPER pair)
- **Playable area**: 18 character columns × 18 character rows = 144 cells (about 56% of the screen)
- **Frame rate**: 50 Hz on PAL models
- **Hardware support**: any stock Spectrum (48K, 128K, +2, +2A, +2B, +3)
- **Tile size**: 8×8 pixels, with each tile carrying 9 attribute bytes (one per scanline)
- **Tile count**: up to 256 tiles per frame
- **Animated tile count**: typically 30-50 simultaneously animated tiles
- **Memory cost**: ~2 KB for the engine code + ~16 KB for tile data (256 tiles × 64 bytes each)

### Architecture

BIFROST* installs an IM2 interrupt handler that, every scanline during the playfield region, writes a fresh set of attribute bytes to the screen. The engine handles all raster timing internally; the game programmer treats tiles as ordinary 8×8 sprites.

Each tile is stored as **9 bytes of attribute data** (one per scanline of the tile, with the 9th byte unused or used as a flag) plus **8 bytes of pixel data** (the standard Spectrum font-style format). The engine reads the tile index, looks up the tile's address, and writes the per-scanline attributes to the screen at the correct time.

### Game programming interface

The programmer-facing API is small:

```z80
; Initialize the engine at game start
        CALL BIFROSTstart

; Set a tile at position (X, Y) in the playfield
; A = tile index (0..255)
; B = X cell (0..17)
; C = Y cell (0..17)
        LD   A,tile_index
        LD   B,x_cell
        LD   C,y_cell
        CALL BIFROSTsetTile

; The engine draws the tile automatically during its IM2 ISR
```

The tile indices reference a tile table that the programmer populates at game load time. The engine draws tiles every frame; if a tile's index changes (animation), the engine picks up the new tile automatically.

### Games shipped with BIFROST*

- *Knights & Demons DX* (Baron Ashler, Einar Saukas, Craig Stevenson) — puzzle game, two-player
- *Pets vs Aliens Prologue* (Einar Saukas, Jarrod Bentley, Yerzmyey)
- *Complica DX* (Einar Saukas, Dave "R-Tape" Hughes, Yerzmyey)
- *Pushbot* (Dave "R-Tape" Hughes)
- *Midnight Riders Fanclub* (Einar Saukas, in development)

The engine's reference distribution includes these games' tile sets as worked examples.

### Limitations

- **Small playfield** (18×18 = 56% of screen). The engine's ISR timing budget only covers 18 columns of attribute writes per scanline; expanding the area would require dropping below 50 Hz.
- **No sprite overlay** in the multicolor region. Tiles are loaded directly into the playfield; moving sprites over them would require the engine to also draw masked sprites per scanline, which exceeds the frame budget.
- **Tile-based, not freeform pixels**. Each 8×8 cell has one tile; you cannot draw arbitrary shapes within a cell.

For larger playfields or sprite overlays, NIRVANA+ is the typical alternative.

---

## NIRVANA+ Engine

**NIRVANA+** is Einar Saukas's multicolor 8×2 graphics engine, released in 2015. It addresses BIFROST*'s main limitation (small playfield) by accepting a lower color resolution.

### Specifications

- **Color resolution**: 8×2 (each pair of scanlines within an 8×8 cell has its own INK/PAPER pair)
- **Playable area**: 32 character columns × 23 character rows = 736 cells (essentially the full screen)
- **Frame rate**: 50 Hz on PAL models
- **Hardware support**: any stock Spectrum (48K, 128K, +2, +2A, +2B, +3)
- **Tile size**: 8×8 pixels, with each tile carrying 4 attribute bytes (one per 2-scanline pair)
- **Tile count**: up to 256 tiles per frame
- **Animated tile count**: typically 30-50 simultaneously animated tiles

### Why 8×2 instead of 8×1?

The 8×2 resolution is a deliberate tradeoff: it halves the per-scanline attribute write count (16 writes per scanline instead of 32), freeing CPU time to cover a larger playfield. The result is essentially the full screen available for multicolor graphics, at the cost of half the vertical color resolution.

The visual difference is small. In 8×1, each scanline of an 8×8 cell can have its own colors; in 8×2, each *pair* of scanlines shares colors. For most game art (sprites, tiles, backgrounds) the difference is invisible. It matters for fine gradient effects and per-pixel detail work, which is why BIFROST* still exists.

### Architecture

NIRVANA+'s ISR is based on a multicolor render routine originally developed by Alone Coder and Einar Saukas (the engine documentation credits this lineage). The routine uses self-modifying code to walk the playfield's attribute cells and write fresh attribute bytes at the correct scanline T-states.

Each NIRVANA+ tile stores **4 attribute bytes** (one per 2-scanline pair) plus **8 bytes of pixel data**. The engine reads the tile index, looks up the address, and writes the 4 attribute bytes during the appropriate 2-scanline windows.

### Games shipped with NIRVANA+

- *Snake Escape* (Einar Saukas)
- *Pietro Bros* (Cristian Gonzalez) — *Super Mario Bros*-style platformer
- *Gandalf* (Cristian Gonzalez, Alvin Albrecht, January 2018) — *Lord of the Rings*-themed action game
- *Bomberman* (Cristian Gonzalez, in development)

The engine is the de facto choice for modern multicolor game development. The Spectrum community considers *Pietro Bros* and *Gandalf* showpiece titles for what the technique can achieve.

### Relationship to BIFROST*

NIRVANA+ is not a replacement for BIFROST* — both engines coexist because they optimize for different things. BIFROST* is the choice when the playfield can be small but the color detail must be maximum (puzzle games, single-screen arcade games). NIRVANA+ is the choice when the playfield must be large (platformers, action-adventure). For most new games, NIRVANA+ is the safer default.

---

## ZXodus Engine

**ZXodus** is Andrew Owen's earlier (2011) multicolor engine, predating BIFROST* by about a year. It is less widely used than BIFROST* or NIRVANA+ but historically important: it was one of the first published, reusable 8×1 multicolor engines for the Spectrum, and it pioneered the API shape that BIFROST* later refined.

### Specifications

- **Color resolution**: 8×1 (same as BIFROST*)
- **Playable area**: configurable, typically 16-22 columns wide
- **Frame rate**: 50 Hz on PAL models
- **Hardware support**: any stock Spectrum
- **Tile size**: 8×8 pixels with 8 attribute bytes (one per scanline)
- **Memory cost**: similar to BIFROST* (~2 KB engine + tile data)

### Architecture

ZXodus uses the same general approach as BIFROST*: an IM2 interrupt handler writes per-scanline attribute bytes during the playfield region. The engine's main difference from BIFROST* is its **scanline palette model**: instead of storing per-tile attribute data, ZXodus lets the programmer define a palette of attribute values that change at fixed scanline boundaries. This is closer to the demoscene copper-bar technique than to BIFROST*'s tile-based model.

The tradeoff: ZXodus is more flexible for free-form effects (gradients, plasma-style color cycling) but less convenient for tile-based games where each 8×8 cell has its own colors. BIFROST*'s tile API maps cleanly to game art; ZXodus's palette API maps cleanly to demoscene effects.

### Relationship to ULAplus

ZXodus and ULAplus are both Andrew Owen projects, and they reflect the same design goal: extend the Spectrum's color capabilities without requiring new hardware. ZXodus is the **CPU-driven** answer (works on stock hardware, costs frame time); ULAplus is the **hardware-driven** answer (requires FPGA hardware, costs no frame time). The two projects are complementary rather than competing.

### Games shipped with ZXodus

ZXodus has a smaller shipped-games catalog than BIFROST* or NIRVANA+. The engine is primarily of historical interest today — for new game development, BIFROST* or NIRVANA+ are the standard recommendations. ZXodus remains useful as a reference implementation of the scanline-palette approach.

---

## ULAplus: 64-Color Hardware Palette

**ULAplus** is Andrew Owen's 2008 hardware specification for extending the Spectrum's palette from 15 colors (8 ink + 8 paper, with black shared) to **64 colors** via a register-programmable palette. It is not a CPU-driven technique — it requires the ULA (or FPGA replacement of the ULA) to implement the extended palette register.

> [!IMPORTANT]
> ULAplus does **not** work on original Sinclair hardware. It requires either:
> - A modern FPGA-based Spectrum clone (ZXUno, Spectrum Next, harlequin, etc.)
> - An emulator that implements the ULAplus register interface (Fuse, Spectaculator, ZEsarUX)
>
> Original 48K/128K/+2/+2A/+3 machines ignore ULAplus writes; the palette remains the stock 15-color set.

### Programming interface

ULAplus exposes a 64-entry palette through two I/O ports:

- **`#BF3B`** — register select. Write the palette index (0-63) here.
- **`#FF3B`** — data. Write the color value here.

The 64 palette entries are organized as **4 groups of 16 colors**. Group 0 (entries 0-15) replaces the standard Spectrum attribute colors. Groups 1-3 (entries 16-63) are additional palettes that can be swapped in via the mode register.

```z80
; Set palette entry 5 to a custom color
set_palette_entry:
        LD   BC,#BF3B
        LD   A,5                 ; palette index 5
        OUT  (C),A
        LD   BC,#FF3B
        LD   A,#3F               ; G3R3B2 color (white, max intensity)
        OUT  (C),A
        RET
```

### G3R3B2 color encoding

Each palette entry is an 8-bit value in **G3R3B2** format — 3 bits green, 3 bits red, 2 bits blue:

```
Bit:   7  6  5  4  3  2  1  0
       G2 G1 G0 R2 R1 R0 B1 B0
```

The asymmetry (3-3-2 instead of 2-2-2 or 3-3-3) reflects the human eye's greater sensitivity to green. The encoding gives 8 levels each of green and red, and 4 levels of blue — 8 × 8 × 4 = 256 possible values, mapped into the 64 palette entries.

A helper macro to convert (R, G, B) to G3R3B2:

```
; Given R in [0,7], G in [0,7], B in [0,3]
; Result in A
g3r3b2_from_rgb:
        ; A = (G << 5) | (R << 2) | B
        LD   A,G
        SLA  A : SLA  A : SLA  A : SLA  A : SLA  A    ; G << 5
        LD   C,A
        LD   A,R
        SLA  A : SLA  A                                  ; R << 2
        OR   C
        OR   B
        RET
```

In practice, palette values are usually precomputed at assembly time and stored in a `DEFB` table.

### Palette groups and mode register

ULAplus defines a **mode register** (accessed via the same `#BF3B`/`#FF3B` port pair, with bit 7 of the register-select value set) that controls which palette group is active. Writing the mode register lets the programmer instantly swap the entire 16-color attribute palette — useful for fade effects, day/night transitions, or scene-specific color themes.

```z80
; Switch to palette group 1
switch_palette_group_1:
        LD   BC,#BF3B
        LD   A,#40              ; mode register (bit 7 set, group 1)
        OUT  (C),A
        LD   BC,#FF3B
        LD   A,%00000001        ; select group 1
        OUT  (C),A
        RET
```

### Detecting ULAplus at runtime

A game targeting both stock and ULAplus-capable hardware should detect ULAplus at startup and only write palette values if it is present. The detection test exploits the fact that ULAplus responds to writes at `#BF3B`/`#FF3B` while the stock ULA does not:

```z80
; Returns: Z flag set if ULAplus detected
detect_ulaplus:
        LD   BC,#BF3B
        LD   A,#55               ; register index 0x55 (in group 2, normally unused)
        OUT  (C),A
        LD   BC,#FF3B
        IN   A,(C)               ; read back (ULAplus latches the value)
        CP   #55                 ; ULAplus returns last-written register index
        RET
```

If the test fails (no ULAplus), the game falls back to the stock 15-color palette and continues normally. If it succeeds, the game can write its custom palette and use ULAplus-aware attribute values.

### ULAplus in game design

ULAplus changes the *palette* but not the *attribute resolution*. Each 8×8 cell still has one INK and one PAPER value. The improvement is that those values can now be any of 64 colors instead of 8 — eliminating the harsh cyan/magenta/yellow look of the stock palette and allowing softer greens, browns, and skin tones.

ULAplus does **not** eliminate color clash. Two sprites with different colors overlapping within an 8×8 cell still produce a clash — the only difference is that the clash is between two of 64 colors instead of two of 8. To eliminate clash entirely, you need BIFROST* or NIRVANA+ (per-scanline attribute writes), which is why the two techniques are often combined: a multicolor engine for color resolution, plus ULAplus for palette depth.

### Emulator and hardware support

- **Emulators**: Fuse, Spectaculator, ZEsarUX, Klive, qaop — all major modern emulators support ULAplus.
- **FPGA hardware**: ZXUno (full support), Spectrum Next (full support, also has its own Layer 2 — see [next_graphics.md](next_graphics.md)), harlequin (partial support depending on revision).
- **Original Sinclair hardware**: not supported. Some hardware modifications (ULAplus boards, Chloe 140KS) add ULAplus to original-issue machines, but these are enthusiast projects, not stock configurations.

---

## Timex HiColor and HiRes Modes

The **Timex Sinclair 2068** (TS2068, the US-market successor to the TS1000) and its UK cousin the **Timex Computer 2048** (TC2048) include two extended display modes that the Sinclair ZX Spectrum lacks. These modes are accessible from stock Timex hardware and from any emulator that supports the TC2048/TS2068. They are also implemented on the Spectrum Next as legacy-compatible modes.

### Timex HiColor mode (6×1 attributes)

- **Pixel buffer**: 256×192, same as standard
- **Attribute resolution**: **8×1** (one attribute byte per scanline per 8-pixel column)
- **Memory cost**: 6 KB pixel buffer + **6 KB attribute file** (vs 768 bytes on the standard Spectrum)
- **Port**: write `DECIMAL` to port `#FF` (also known as the TIMEX mode port) to select HiColor mode

In HiColor mode, the attribute file expands to match the pixel layout: instead of 32×24 attribute cells, the file holds 32×192 attribute cells (one per scanline per column). This eliminates color clash at the cost of doubling video memory. The CPU writes attribute bytes exactly the same way as pixel bytes — there is no per-scanline ISR synchronization required, no cycle-exact timing.

HiColor mode is the **hardware equivalent** of what BIFROST* and NIRVANA+ achieve in software. The tradeoff is hardware availability: HiColor exists only on Timex-branded machines and modern clones (TC2048, TS2068, Spectrum Next, divMMC, etc.). Pure Sinclair-branded Spectrums cannot display HiColor.

### Timex HiRes mode (512×192 monochrome)

- **Pixel buffer**: **512×192** (twice the horizontal resolution)
- **Attributes**: none — pixels are pure black/white
- **Memory cost**: 6 KB pixel buffer, no attribute file
- **Port**: write to port `#FF` to select HiRes mode

HiRes mode doubles the pixel clock, giving 512 horizontal pixels (each pixel is half the width of a standard Spectrum pixel). The result is sharp, high-detail monochrome graphics — useful for wireframe 3D, detailed character art, and dense text. The lack of color makes it unsuitable for general game use, but several Timex-era games and demos exploit it for technical showpieces.

### Selecting Timex modes

```z80
; Switch to HiColor mode (Timex extended mode 1)
select_hicolor:
        LD   BC,#00FF           ; Timex mode port
        IN   A,(C)              ; read current mode register
        OR   %00000110          ; set bits 1 (extended mode) and 2 (HiColor)
        AND  %11110111          ; clear bit 3 (don't mix HiRes)
        OUT  (C),A
        RET

; Switch to HiRes mode (Timex extended mode 2)
select_hires:
        LD   BC,#00FF
        IN   A,(C)
        OR   %00001010          ; set bits 1 (extended) and 3 (HiRes)
        OUT  (C),A
        RET

; Switch back to standard Spectrum mode
select_standard:
        LD   BC,#00FF
        IN   A,(C)
        AND  %11111101          ; clear bit 1 (back to standard mode)
        OUT  (C),A
        RET
```

### Compatibility notes

Timex modes are supported by: Fuse (TC2048 / TS2068 emulation), ZEsarUX, Spectaculator, Klive, and the Spectrum Next (as legacy modes via the `TIMEX` port). They are **not** supported on stock Sinclair 48K/128K/+2/+2A/+3 hardware.

The Spectrum Next implements HiColor and HiRes in its legacy ULA layer for backward compatibility with TC2048 software. For new Spectrum Next code, the Layer 2 256-color mode (see [next_graphics.md](next_graphics.md)) is generally preferred over the Timex modes — Layer 2 offers both higher resolution and higher color depth without the legacy attribute model.

---

## Choosing an Engine

The decision of which multicolor technique to use depends on three factors: **target hardware**, **playable area size**, and **color resolution requirements**.

### Decision matrix

| Your game needs... | Use this |
|---|---|
| Stock 48K/128K Spectrum, small playfield (puzzle/arcade), max color detail | **BIFROST\*** (8×1) |
| Stock 48K/128K Spectrum, full-screen playfield (platformer/adventure) | **NIRVANA+** (8×2) |
| FPGA clone or modern emulator, want softer palette without clash elimination | **ULAplus** alone (palette extension) |
| FPGA clone or modern emulator, want to combine palette depth and clash elimination | **NIRVANA+ or BIFROST\*** with **ULAplus** for palette |
| Timex TC2048 / TS2068 / Spectrum Next, want 8×1 without CPU cost | **Timex HiColor** (hardware mode) |
| Timex TC2048 / TS2068 / Spectrum Next, want sharp monochrome detail | **Timex HiRes** (512×192 mono) |
| Spectrum Next, want maximum color depth and resolution | **Layer 2** (256×192, 256 colors — see [next_graphics.md](next_graphics.md)) |
| Stock 48K/128K Spectrum, demoscene-style freeform color effects | **ZXodus** (scanline palette model) |

### When to *not* use a multicolor engine

Multicolor engines come with costs: BIFROST* and NIRVANA+ consume roughly 30-50% of the frame budget for their ISR work, and they constrain the playable area or animation budget. For games that do not strictly need higher-than-8×8 color resolution, the standard attribute model plus careful art direction is often better. The classic Spectrum look — *Manic Miner*, *Jet Set Willy*, *Chuckie Egg*, *Cybernoid* — was achieved without any multicolor engine, and remains visually effective.

Common cases where the standard model is fine:
- Single-character games where the player sprite rarely shares an attribute cell with another colored object
- Static or slow-moving puzzle games where each tile has its own dedicated attribute cell
- Monochrome games (INK 7 / PAPER 0) where color clash is invisible
- Games targeting 16 KB or heavily banked memory layouts where the engine's 2 KB code overhead matters

---

## Common Pitfalls

### 1. Forgetting that BIFROST* and NIRVANA+ disable interrupts during their ISR

Both engines install an IM2 handler that runs with interrupts disabled for the duration of the playfield scan. Any code that depends on the Spectrum's 50 Hz IM1 interrupt (music players, keyboard polling, IM1-based frame counters) must either:

- Be called from outside the playfield region (top/bottom border time), or
- Be integrated into the engine's own ISR chain.

Forgetting this produces a game that plays music at the wrong rate, drops keypresses, or freezes after a few seconds.

### 2. Writing to the playfield while the engine is mid-render

The engines read tile indices and attribute bytes from RAM during their ISR. If the game writes a new tile index while the engine is mid-scanline, the result is a torn frame — the top of the tile shows the old colors, the bottom shows the new. Always update the tile table during the border time (top border: ~14,000 T-states available; bottom border: ~14,000 T-states available), not during the playfield scan.

### 3. Mixing ULAplus palette writes with raster-synchronized code

Writing to port `#FF3B` (ULAplus data) takes ~11 T-states, the same as any other `OUT (C),A`. But the ULAplus palette register is *not* double-buffered: a write takes effect immediately. If you write a new palette value mid-scanline, the ULA applies the new color to whatever pixel it is currently displaying — producing a visible seam. ULAplus palette writes should happen during VBLANK (top or bottom border), not during the active display.

### 4. Assuming ULAplus exists on the target machine

Many Spectrum players still use original hardware or emulators configured as stock 48K/128K. If your game requires ULAplus to look right, players without ULAplus support will see the default palette, which may make the art look wrong (intended soft greens become harsh cyan, etc.). Always:

1. Detect ULAplus at startup (see [§ Detecting ULAplus at runtime](#detecting-ulaplus-at-runtime))
2. Design the default (non-ULAplus) palette to look acceptable on its own
3. Treat ULAplus as an enhancement, not a requirement

### 5. Using BIFROST* playfield outside its supported region

BIFROST* supports 18×18 cells (columns 0-17, rows 0-17). Attempting to draw a tile at column 18 or row 18 produces undefined behavior — the engine's timing assumes the playfield ends at those bounds. NIRVANA+ has the same constraint at 32×23. Always clip your tile coordinates to the supported range before calling the engine's `setTile` API.

### 6. Forgetting that Timex HiColor doubles attribute file size

A game that works on the standard Spectrum assumes 768 bytes of attribute file. When porting to Timex HiColor, the attribute file expands to 6 KB. Any code that calculates attribute addresses (e.g., `attr_addr = #5800 + row * 32 + col`) must be rewritten: the formula becomes `attr_addr = #5800 + row * 32 + col`, but `row` now ranges 0-191 instead of 0-23. Code that iterates over attribute cells assuming 24 rows will only update the top portion of the screen.

---

## Cross-References

- [race_the_beam.md](../04_interrupts/race_the_beam.md) — the foundations of raster-synchronized attribute writes (the prerequisite article)
- [multicolor_techniques.md](../../07_demoscene/multicolor_techniques.md) — demoscene-side coverage of the same technique (effects-driven, not game-driven)
- [color_system.md](../05_display_and_timing/color_system.md) — attribute byte format, INK/PAPER encoding, color tables
- [screen_layout.md](../03_memory_and_io/screen_layout.md) — non-linear pixel and attribute address math
- [sprites_and_masking.md](sprites_and_masking.md) — sprite compositing modes that pair with these engines
- [next_graphics.md](next_graphics.md) — the Spectrum Next's Layer 2 and hardware sprites (the modern alternative)

---

## References

- Einar Saukas, *BIFROST\* Engine* — reference distribution and documentation, [World of Spectrum forum thread](https://worldofspectrum.org/forums/discussion/52615/)
- Einar Saukas, *NIRVANA+ Engine* — reference distribution, [GitHub](https://github.com/einar-saukas/NIRVANA-Plus)
- Andrew Owen, *ULAplus specification* — original 2008 document and reference implementation, [ULAplus homepage](https://www.imaginescape.co.uk/)
- Andrew Owen, *ZXodus Engine* (2011)
- Timex Computer 2048 / TS2068 hardware reference manuals — HiColor and HiRes mode documentation
- Cristina Gonzalez's *Pietro Bros* and *Gandalf* — worked examples of NIRVANA+ in shipping games
- *Knights & Demons DX* — worked example of BIFROST* in a shipping game
- *World of Spectrum* forums — community-maintained discussions on multicolor engine tradeoffs
