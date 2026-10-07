[← Home](../../README.md) · [Display & Timing](README.md)

# Clone Video Modes — Beyond Standard ULA

The ZX Spectrum's Ferranti ULA produces a single video mode: 256×192 pixels with 8×8 attributes. Soviet and post-Soviet clone manufacturers extended this with hires, high-color, and dual-screen modes using additional CPLDs, FPGA overlays, and discrete logic. This article covers the clone-specific video modes that are not present on any original Sinclair/Amstrad machine.

For Timex TS/TC 2068 extended modes (HiColor, HiRes), see [color_system.md](color_system.md#timex-tstc-2068-extended-modes). For ZX Spectrum Next Layer 2 / tilemap, see the Next hardware documentation.

---

## Mode Overview

| Mode | Machines | Resolution | Colors | Attribute Size | Memory |
|------|----------|-----------|--------|---------------|--------|
| GigaScreen | Pentagon, Kay, ZX Evo | 256×192 | 1024 (temporal mix) | 8×1 (temporal) | 2 × 768 attr |
| ATM Turbo hires | ATM Turbo 2/2+ | 640×200 | 2 per 8×1 strip | 8×1 | 32,000 bytes (bitmap page 5 + attrs page 1) |
| ATM Turbo EGA | ATM Turbo 2/2+ | 320×200 | 16 per pixel | per pixel | 32,000 bytes (pages 1+5, interleaved) |
| ATM Turbo text | ATM Turbo 2/2+ | 80×25 chars | 16 per char | per-char | 4,000 bytes + font |
| Profi extended screen | Profi 3.2/5.x | 512×240 | 16 (Profi 5: from 256) | 8×1 (per pixel byte) | 30,720 bytes |
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

### Rendering GigaScreen correctly — what the modern "ZXDLSS" work established

Rendering a GigaScreen demo on modern hardware is its own problem: naive per-pixel frame averaging smears everything that *moves*, and ghosting looks worse than the flicker it replaces. The verified principles from recent scanline-analysis work ("never worse than the raw frame"):

1. **Separate detection from mixing.** First decide *which* pixels belong to an intentional temporal mix (stable content alternating between two palettes across frames) and which are ordinary motion; then a mixer combines only the detected samples. When the detector is unsure, the pixel is shown exactly as rendered.
2. **Mix in the right light domain.** A plain sRGB average is the weakest model; converting to **linear light** before averaging (the eye integrates emitted light) is the sane default, and a CRT-calibrated variant (gamma 2.4–2.8 with black level) tracks real tubes closer still. Perceptual-space (OKLab) averaging keeps hue steadiest for wildly different color pairs.
3. **Historical references are calibrated pair tables.** Unreal Speccy's hand-tuned mixed levels for attribute pairs (the ZZ/ZN/NN/NB/BB/ZB six) and its windowed-sinc temporal filter (12/8 Hz cutoffs) remain the classic CRT-calibrated baselines to compare against; Spectaculator/Xpeccy plugin blends are the other lineage.
4. **Run per emulated frame, before the framebuffer latch** — the host display rate must not influence the mix; phosphor-decay models add age-dependent, per-channel weights (P22 green decays slowest).

Because every sample is one of 16 palette colors, mixer results are table-precomputable — even exotic user formulas cost nothing per frame.
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

| RG code | Mode | Resolution | Colors | Framebuffer | Use Case |
|---|---|-----------|--------|-------------|----------|
| 3 | ZX Spectrum | 256×192 | 15 (standard) | page 5 + attrs page 1 | Standard software |
| 2 | 640×200 hires | 640×200 | 2 per 8×1 strip | bitmap page 5 + attrs page 1 | CP/M 80-column display |
| 0 | EGA | 320×200 | 16 per pixel | pages 1 + 5 (interleaved) | PC game ports, graphics |
| 6 | Text | 80×25 chars | 16 per char | pages 1 + 5 + font RAM | CP/M terminal |

### 640×200 Monochrome Mode

The hires mode runs the pixel clock at double frequency, producing 640 pixels across a standard PAL active area. Each pixel row is 80 bytes; the bitmap lives in **RAM page 5** and the attributes in **RAM page 1** (or pages 7/3 while `#7FFD` bit 3 = 1), each split into two 8 KB half-planes scanned alternately every 8 pixels:

```
Memory:   16,000 bytes bitmap (page 5) + 16,000 bytes attributes (page 1)
Address:  page + (x & 8 ? #2000 : #0000) + (x >> 4) + Y × 40
          pixel bit 7-(x & 7); attr = ZX ink/paper byte per 8×1 strip
```

The attribute byte per 8×1 strip gives every 8-pixel run its own foreground/background pair from the 16-entry palette — effectively a hardware-multicolor hires mode.

### 320×200 EGA Mode (16 Colors Per Pixel)

The signature ATM Turbo mode: **16 colors per pixel with no attribute clash**, sized to match the IBM PC EGA 320×200 mode for direct game ports (*Prince of Persia*, *Color Lines*, *Gobliiins*). The framebuffer occupies **two fixed physical RAM pages — 1 and 5** (3 and 7 while `#7FFD` bit 3 = 1), 16,000 bytes each, scanned linearly with pixel pairs interleaved across the two pages and their 8 KB half-planes. The byte format is a ZX-attribute look-alike (`%RLRRRLLL`): the left pixel takes D0-2 + D6, the right pixel D3-5 + D7. Complete addressing math, the CPU mapping recipe and plot code: [atm_turbo.md](../../02_hardware/clones/atm_turbo.md).

### Mode Switching

On the ATM Turbo 2/2+ (v6.40–7.10) the video mode lives in **bits 0-2 of the `#FF77` system register** (any port with low byte `#77`; the address bits A8/A9/A14 of the write additionally control the PEN/CPM/PEN2 flags). On the Turbo 1 the mode is selected by address bits A5/A6 of the `#FE` port write instead.

```z80
LD A,#20 \ OUT (#FF77),A   ; RG=0: 320×200 EGA mode (bit 5 = Z_I kept set)
LD A,#23 \ OUT (#FF77),A   ; RG=3: back to standard ZX mode
```

The `#xx77`/`#xxF7` ports are gated by the DOS latch (active under TR-DOS/CP/M). Full decode tables, the EGA framebuffer interleave, the palette protocol and worked examples: [atm_turbo.md](../../02_hardware/clones/atm_turbo.md).

### CP/M Interoperability

The 640×200 mode makes the ATM Turbo one of the few ZX Spectrum clones that can run CP/M with a readable 80-column display. Standard CP/M software (WordStar, dBase II, Turbo Pascal) becomes usable, albeit in monochrome.

---

## Profi — 512×240 Extended Screen (Hardware Multicolor)

The Profi is a Moscow-built ZX Spectrum 128 descendant with CP/M ambitions. Its extended screen, enabled by the DS80 bit (bit 7) of the Profi control register `#DFFD`, doubles the horizontal resolution, adds 48 scanlines — and, unlike every other extended mode in this article, keeps color: one attribute byte per 8-pixel byte.

### Video Mode

| Mode | Resolution | Colors | Memory |
|------|-----------|--------|--------|
| ZX Spectrum | 256×192 | 15 (standard) | Standard layout |
| Extended (DS80) | 512×240 | 16 (Profi 5: from a 256-color palette) | 15,360 pixels + 15,360 attributes |

The screen consists of two 15,360-byte areas — pixels and attributes — one per RAM page (screen 0: pages `#04`/`#38`; screen 1: pages `#06`/`#3A`). Attribute granularity is 8×1 pixels: **hardware multicolor** with zero CPU cost, eight times the vertical color resolution of the stock attribute cell. Screen 1 additionally supports simultaneous pixel+attribute access (pixels hard-mapped at `#8000`, attributes in the projection window), which is why CP/M uses it as the primary display.

The image is stored as two interleaved half-screens of 32 columns (odd columns in the first part, even in the second, switched by bit 13 of the address); within each half-screen the layout is ZX-Spectrum-like with four quarters of 64 lines, the last short at 48. Text resolution is 64×30 — the Profi's CP/M selling point. Full addressing math, the 16-color attribute byte, palette programming protocol, and a worked demo: [profi.md](../../02_hardware/clones/profi.md).

### Frame Timing

Extended mode changes the frame itself: 59,904 T-states (312 lines × 192 T) instead of the ZX-mode 69,888 T, with the paper area starting at a different offset. Software relying on raster timing must keep separate tables per mode — see the timing section of [profi.md](../../02_hardware/clones/profi.md) and [video_frame_other_soviet.md](video_frame_other_soviet.md).

### Use Case

64×30 text and hardware multicolor made the extended screen the centerpiece of the Profi's CP/M productivity pitch — word processing and programming tools, not games. Early boards shipped without the color circuit at all (a B/W variant), and 8-color + 2-brightness variants existed; the surviving 16-color and 16-of-256-palette (Profi 5) machines share one programming model.

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
- **ATM Turbo hardware** (mode register decode, EGA framebuffer, palette): [atm_turbo.md](../../02_hardware/clones/atm_turbo.md)

## References

### External references

- [TS-Conf documentation](https://zxevo.ru) — the canonical reference for the ZX Evolution's FPGA-based video subsystem, including 640x200 / 320x200 / 256x192 modes, hardware tiles, and the layer sprite engine.
- **ATM Turbo documentation** (`atmturbo.com`, archived) — the original HIRES and TEXT mode specifications for the ATM Turbo 1/2, the first widely deployed Soviet-clone video extensions.
- [Kay 2006 NB CPLD documentation](https://zxpress.ru) — the CPLD-based video subsystem that brought 16-color mode and programmable palettes to the late Kay lineage.
- **[TAE & Vadim Chertkov — "Расширенный экран «Profi»" (Абзац #16 2003 / ЗаRulem #25 2019, on Habr)](https://habr.com/ru/articles/836836/)** — the extended-screen reference: half-screen structure, 16-color attribute byte, palette programming protocol
- [GigaScreen documentation](https://zx-pk.ru) — the temporal-mixing technique that pairs two screens at 50 Hz to simulate 8x8 attribute resolution; documented extensively in the Brainwave/Eternity Industry demo archives.