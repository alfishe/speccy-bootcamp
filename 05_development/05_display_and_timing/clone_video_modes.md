[← Home](../../README.md) · [Display & Timing](README.md)

# Clone Video Modes — Beyond Standard ULA

The ZX Spectrum's Ferranti ULA produces a single video mode: 256×192 pixels with 8×8 attributes. Soviet and post-Soviet clone manufacturers extended this with hires, high-color, and dual-screen modes using additional CPLDs, FPGA overlays, and discrete logic. This article covers the clone-specific video modes that are not present on any original Sinclair/Amstrad machine.

For Timex TS/TC 2068 extended modes (HiColor, HiRes), see [color_system.md](color_system.md#timex-tstc-2068-extended-modes). For ZX Spectrum Next Layer 2 / tilemap, see the Next hardware documentation.

---

## Mode Overview

| Mode | Machines | Resolution | Colors | Attribute Size | Memory |
|------|----------|-----------|--------|---------------|--------|
| GigaScreen | Pentagon, Kay, ZX Evo | 256×192 | 1024 (temporal mix) | 8×1 (temporal) | 2 × 768 attr |
| ATM Turbo hires | ATM Turbo | 640×200 | 2 (mono) | N/A | 16,000 bytes |
| ATM Turbo text | ATM Turbo | varies | configurable | per-char | varies |
| Profi hires | Profi | 512×256 | 2 (mono) | N/A | 16,384 bytes |
| Kay 512×192 | Kay 2006 NB | 512×192 | 2 (mono) | N/A | 12,288 bytes |
| Kay multicolor | Kay 2006 NB | 256×192 | standard | 8×1 (per scanline) | 6,144 extra |
| TS-Conf | ZX Evolution | up to 360×288 | 256 (8-bit) | per-pixel | up to 512 KB VRAM |

> [!NOTE]
> These modes are mutually incompatible across machines. Code that uses ATM Turbo hires mode will not work on a Pentagon, and vice versa. Cross-platform software must detect the machine before activating extended modes.

---

## GigaScreen — Temporal Attribute Mixing

GigaScreen is the most widespread clone video extension. It alternates between **two attribute sets** on even and odd frames, exploiting the persistence of CRT phosphor (or LCD frame blending) to produce a visual mix of both. The result is an effective 8×1 attribute resolution with up to 1,024 visually distinct color combinations per cell.

### How It Works

```
Frame N (even):   Display pixel data + attribute set A
Frame N+1 (odd):  Display pixel data + attribute set B
Frame N+2 (even): Display pixel data + attribute set A
...

CRT phosphor persistence blends the two frames,
producing intermediate colors the eye perceives as simultaneous.
```

The pixel bitmap is shared — only the attribute data alternates. This means the shape of objects remains stable while their colors appear to blend.

### Attribute Layout

```
Standard:       #5800–#5AFF  (768 bytes)  — 32×24 attributes
GigaScreen A:   #5800–#5AFF  (768 bytes)  — even frame attributes
GigaScreen B:   alternate bank             — odd frame attributes
```

On Pentagon-based machines, the second attribute set is typically stored in the shadow screen bank (bank 7 on 128K Pentagon) or a dedicated memory page. The exact location depends on the implementation.

### Activating GigaScreen

GigaScreen activation varies by machine:

| Machine | Port | Activation |
|---------|------|------------|
| Pentagon 1024 + GigaScreen CPLD | `#EFF7` bit ? | Machine-specific CPLD register |
| Kay 2006 NB | Built into Altera CPLD | Automatic when second attr bank is populated |
| ZX Evolution (Baseconf) | Config register | TS-Conf or Baseconf firmware controls |
| Emulators (FUSE, ZEsarUX) | Menu option | Runtime toggle, no port access |

### Visual Trade-offs

- **Flicker**: On 50 Hz display, the 25 Hz alternation of each attribute set produces visible flicker, especially with high-contrast color pairs (e.g., red/cyan). Dark-on-dark combinations flicker less.
- **LCD displays**: Frame blending is less effective on LCD panels with fast pixel response. Emulators often provide a "GigaScreen blend" filter to simulate CRT persistence.
- **Brightness halving**: Each color is displayed only half the time, so the perceived brightness drops. Compensate by using bright variants.

### Practical Use

GigaScreen is popular in the demoscene for static artwork and title screens. It is rarely used for in-game graphics because the flicker is distracting during gameplay.

```z80
; Simplified GigaScreen frame handler (Pentagon 128K)
; Assumes shadow attributes are in bank 7 at #D800 (shadow screen attrs)
GigaFrame:
    LD   A,(FrameCount)
    XOR  1                ; Toggle even/odd
    LD   (FrameCount),A
    JR   Z,.showB

.showA:
    ; Page in bank 5 (main screen attributes at #5800)
    LD   BC,#7FFD
    LD   A,#10            ; Bank 5, no shadow screen
    OUT  (C),A
    RET

.showB:
    ; Page in bank 7 (shadow attributes at #D800 → mapped to #5800)
    LD   BC,#7FFD
    LD   A,#17            ; Bank 7 + shadow screen bit
    OUT  (C),A
    RET
```

---

## ATM Turbo — Hires and Text Modes

The ATM Turbo was designed as a dual-purpose machine: ZX Spectrum compatible and CP/M capable. Its extended video modes serve the CP/M use case (80-column text) while remaining accessible to Spectrum software.

### Video Modes

| Mode | Resolution | Colors | Pixel Clock | Use Case |
|------|-----------|--------|-------------|----------|
| ZX Spectrum | 256×192 | 15 (standard) | 7 MHz (same as ULA) | Standard software |
| 640×200 mono | 640×200 | 2 (foreground + background) | 14 MHz | CP/M 80-column text |
| Text mode | configurable | configurable | varies | CP/M terminal |

### 640×200 Monochrome Mode

The hires mode runs the pixel clock at double frequency, producing 640 pixels across a standard PAL active area. Each pixel row is 80 bytes (640/8).

```
Memory: 640 × 200 / 8 = 16,000 bytes (no attribute file)
Address: Typically mapped into a dedicated VRAM page
```

There are no attribute bytes — the display is strictly 1-bit per pixel with a single foreground and background color, set via a dedicated port.

### Mode Switching

ATM Turbo modes are controlled through its custom I/O port mapping. The exact port addresses vary between ATM Turbo v1 and v2 revisions:

```
ATM Turbo video control (simplified):
  Port #FF (some revisions) or dedicated ATM port
  Selects between ZX Spectrum mode and hires/text modes
```

> [!WARNING]
> ATM Turbo mode switching details are revision-specific. Consult the ATM Turbo hardware documentation for your specific board revision.

### CP/M Interoperability

The 640×200 mode makes the ATM Turbo one of the few ZX Spectrum clones that can run CP/M with a readable 80-column display. Standard CP/M software (WordStar, dBase II, Turbo Pascal) becomes usable, albeit in monochrome.

---

## Profi — 512×256 Hires Mode

The Profi is a Russian ZX Spectrum clone with a unique 512×256 hires mode — the only common clone to extend the vertical resolution beyond 192 lines. This produces a more square pixel aspect ratio and denser text display.

### Video Mode

| Mode | Resolution | Colors | Memory |
|------|-----------|--------|--------|
| ZX Spectrum | 256×192 | 15 (standard) | Standard layout |
| Profi hires | 512×256 | 2 (mono) | 16,384 bytes |

The hires mode is strictly monochrome — no attribute bytes. The pixel buffer occupies a full 16 KB bank:

```
512 × 256 / 8 = 16,384 bytes
```

### Frame Timing

The Profi's hires mode has different timing from the standard ZX Spectrum mode. The paper display area starts at a different T-state offset (approximately T=12,580 on some Profi revisions vs T=14,335 on the 48K). Software relying on precise raster timing must account for this when switching modes.

### Use Case

The 512×256 mode supports 64-column text with comfortable line spacing. Combined with the Profi's 512K memory and CP/M support, it serves as a serious productivity machine — unusual for the ZX Spectrum ecosystem.

---

## Kay 2006 NB — CPLD-Enhanced Video

The Kay 1024 was a standard Pentagon-compatible clone with no contention. The later Kay 2006 NB revision added an **Altera EPM7064 CPLD** that provides three enhanced video modes without changing the base frame timing (69,888 T-states, 312 lines, 50 Hz).

### Available Modes

| Mode | Resolution | Attributes | Description |
|------|-----------|-------------|-------------|
| Standard | 256×192 | 8×8 | Pentagon-compatible base mode |
| Multicolor | 256×192 | 8×1 (per scanline) | Per-scanline attribute changes, no contention |
| GigaScreen | 256×192 | 8×1 (temporal) | Alternating two attribute sets on even/odd frames |
| 512×192 | 512×192 | None (2-color) | Double horizontal resolution, monochrome |

### Multicolor Mode

The Kay's multicolor mode provides per-scanline attribute changes through hardware — no timing-precise code required. The CPLD reads a secondary attribute table that contains one attribute byte per scanline per character column (192 × 32 = 6,144 bytes).

This is conceptually identical to the Timex HiColor mode but implemented differently in hardware. The key advantage on the Kay is the **absence of contention** — since the Pentagon-derived hardware has no ULA bus arbitration, the CPU can update the multicolor attributes at any time without stalling.

### 512×192 Mode

Double horizontal resolution at 512 pixels, monochrome only. Each scanline is 64 bytes (512/8). The total pixel buffer is 12,288 bytes. This mode is useful for 64-column text editors and detailed line-art graphics.

---

## TS-Conf — ZX Evolution FPGA Video

TS-Conf is an FPGA-based video controller for the ZX Evolution (PentEvo). It replaces the standard ZX Spectrum video circuit with a fully programmable VGA-compatible display engine. TS-Conf is not a simple hires mode — it is a fundamentally different video architecture coexisting with the Z80.

### Capabilities

| Feature | Specification |
|---------|--------------|
| Max resolution | 360×288 (non-standard VGA timing) |
| Color depth | 256 colors (8-bit per pixel) from 18-bit palette |
| VRAM | Up to 512 KB dedicated video RAM |
| Tiles | 8×8 or 16×16 hardware tiles with 256-color attributes |
| Sprites | Up to 85 hardware sprites per frame, per-pixel transparency |
| Scrolling | Hardware pixel-scroll registers for smooth scroll |
| Output | VGA (RGB), 50–60 Hz selectable |

### Architecture

TS-Conf uses a separate VRAM address space that the Z80 accesses through a window in the memory map (banked into the standard 64K address space). The video controller reads VRAM independently of the CPU, similar to how modern GPUs work — no contention, no ULA stalling.

### Relation to Baseconf

The ZX Evolution ships with two firmware options:
- **Baseconf**: Pentagon-compatible base with GigaScreen support, standard ZX Spectrum timings
- **TS-Conf**: Full FPGA video with tiles, sprites, 256-color palette, VGA output

Switching between them requires a firmware change (reconfiguring the CPLD). They are mutually exclusive at runtime.

> [!NOTE]
> TS-Conf is a separate platform from the ZX Spectrum for practical purposes. Software written for TS-Conf will not run on any other clone. See the TS-Conf documentation for programming details.

---

## Detection Strategies

Before activating any clone video mode, software must identify the host machine. Common detection techniques:

```z80
; Simple machine detection (simplified)
DetectMachine:
    ; 1. Check for Pentagon (no contention + 320 lines)
    ;    Read port #FF — if no floating bus, likely Pentagon or Scorpion

    ; 2. Check for 128K banking
    LD   BC,#7FFD
    LD   A,#10            ; Try to page bank 5
    OUT  (C),A            ; If this works, it's a 128K+ machine

    ; 3. Check for ZX Evolution / TS-Conf
    ;    Attempt to read TS-Conf config port

    ; 4. Check for ATM Turbo
    ;    Attempt to switch video mode and read back

    ; Machine-specific detection is complex and often unreliable.
    ; Many programs use the user's manual selection instead.
    RET
```

For production software, the most reliable approach is to provide a **configuration menu** where the user selects their machine type. Automatic detection is fragile due to the variety of clone revisions and CPLD configurations.

---

## Cross-References

- **Color system** (standard palette, attribute format, ULAplus): [color_system.md](color_system.md)
- **Clone timing** (per-model frame timing, contention): [clone_timing.md](../../02_hardware/clones/clone_timing.md)
- **Bank switching** (memory paging for video banks): [bank_switching_patterns.md](../03_memory_and_io/bank_switching_patterns.md)
- **Border effects** (multicolor borders, raster bars): [border_effects.md](border_effects.md)
- **Screen layout** (standard pixel/attribute addressing): [screen_layout.md](../03_memory_and_io/screen_layout.md)
- **ZX Evolution hardware**: [clone_timing.md#zx-evolution](../../02_hardware/clones/clone_timing.md)

## References

### External references

- **TS-Conf documentation** (`zxevo.ru` wiki) — the canonical reference for the ZX Evolution's FPGA-based video subsystem, including 640x200 / 320x200 / 256x192 modes, hardware tiles, and the layer sprite engine.
- **ATM Turbo documentation** (`atmturbo.com`, archived) — the original HIRES and TEXT mode specifications for the ATM Turbo 1/2, the first widely deployed Soviet-clone video extensions.
- **Kay 2006 NB CPLD documentation** (`zxpress.ru` article archive) — the CPLD-based video subsystem that brought 16-color mode and programmable palettes to the late Kay lineage.
- **Profi 512x256 hires reference** — community-maintained documentation for the Profi's non-standard hires mode; rarely used in production software but historically important.
- [GigaScreen documentation](https://zx-pk.ru) — the temporal-mixing technique that pairs two screens at 50 Hz to simulate 8x8 attribute resolution; documented extensively in the Brainwave/Eternity Industry demo archives.