[← Home](../../README.md) · [New Gen Hardware](README.md)

# ZX Spectrum Next — The Modern FPGA Spectrum

The **ZX Spectrum Next** (2017–2020) is a modern FPGA-based Spectrum-compatible home computer, designed by a UK-Brazilian team led by **Jim Bagley**, **Victor Trucco**, **Henrique Oliviéri**, and **Fabio Belavenuto**, with the ROM/OS work by **Garry Lancaster**. It is the most commercially successful modern Spectrum: a desktop machine in a Spectrum-style case with a real keyboard, FPGA core, and a stack of hardware features — Layer 2 256-color graphics, hardware sprites, tilemap, copper coprocessor, DMA, 28 MHz CPU, 2 MB RAM — none of which existed on any 1980s Spectrum.

For software developers, the Next is **the only Spectrum where a BASIC programmer can write a smooth-scrolling hardware-sprite game without dropping to assembly**. It is also fully binary-compatible with the entire 48K/128K/Pentagon software library: classic software runs without modification, with optional contention emulation so even cycle-exact demos work.

This article is the **complete programmer's hardware reference** for the Next: the platform overview, the layer stack, the NextReg system, and deep dives into each hardware subsystem (Layer 2, sprites, tilemap, copper, DMA, joystick). For the operating system and BASIC, see [NextZXOS](../../04_operating_systems/nextzxos.md). For frame timing and contention, see [Next video frame](../../05_development/05_display_and_timing/video_frame_next.md).

---

## History and Hardware Revisions

The Next was funded via **Kickstarter** in 2016 (campaign by the "SpecNext" team). Two major hardware revisions shipped:

| Revision | Year | FPGA | Notes |
|---|---|---|---|
| **Issue 2 / 2A / 2B** (KS1) | 2017–2019 | **Xilinx Spartan-6** (XC6SLX16) | First backer shipment; the "black case" |
| **Issue 3** (KS2) | 2020 | **Xilinx Spartan-6** (XC6SLX16) | Minor PCB revision; the "white case" |
| **Issue 4 / 4A** (Accelerated) | 2022+ | **Artix-7** (XC7A15T) | Latest; faster FPGA, accommodates core 3.x firmware |

All revisions are **binary-compatible at the software level** — software written for KS1 runs unchanged on KS2/4. The only differences are analog (HDMI output quality) and the firmware version supported. Today (2024), the **Issue 4** is the only revision still in production, available from **Pin Solutions** (UK) and various retro-computing retailers.

---

## Physical Architecture

| Component | Specification |
|---|---|
| **Case** | Spectrum-style desktop case with built-in rubber-key or membrane keyboard (issue-dependent) |
| **CPU** | **Z80N** — an FPGA soft-core with the standard Z80 instruction set **plus** Next-specific extensions (`LDPIR`, `SWAPNIB`, `MIRROR`, `PIXELDAT`, `NEXTREG` access instructions) |
| **CPU clock** | **3.5 / 7 / 14 / 28 MHz** — runtime-switchable via NextReg `0x07` |
| **RAM** | **2 MB** static RAM (vs. 48K–128K on classic Spectrums) |
| **ROM** | **512 KB** flash, holds NextZXOS + 48K/128K editor ROMs + TR-DOS-compatible routines |
| **Video output** | **HDMI** + VGA + composite (all simultaneously) |
| **Storage** | **MicroSD card slot** (SPI-mode, FAT32) |
| **Audio** | **Internal speaker** + AY-3-8912 (two chips, 6 channels) + 8-channel DMA-driven PCM + beeper |
| **Joystick** | **Two DE-9 ports** — individually mode-switchable per port (Kempston ×2, Sinclair, Cursor, Mega Drive) — see [Joystick System](#joystick-system) below |
| **Expansion** | **Raspberry Pi Zero** slot (accelerator), **ESP-12 WiFi** module, **2×20-pin GPIO header** |
| **Accelerator** | **Pi Zero** (optional) — runs a faster Z80 emulator at >100 MHz effective clock |

The case is designed to evoke the original Sinclair 48K rubber-key form factor (Issue 2) or the Spectrum+ membrane-key form factor (Issue 3+). The keyboard matrix is **Sinclair-compatible** so original software reads it correctly.

---

## The Layer Stack

The Next's video hardware presents a **stack of independent layers** that are composited in a fixed priority order:

| # | Layer | Resolution | Colors | Priority |
|---|---|---|---|---|
| 1 | **ULA screen** (standard Spectrum) | 256×192 | 8×2 (attribute-based) | Lowest |
| 2 | **LoRes** (320×192, optional) | 320×192 | 8×8 attribute blocks | Above ULA |
| 3 | **Layer 2** (256-color framebuffer) | 256×192 / 320×256 | 256 from 24-bit RGB palette | Above LoRes |
| 4 | **Tilemap** (hardware tiles) | 40×32 or 80×32 tiles | 256 from palette | Above Layer 2 |
| 5 | **Hardware sprites** (up to 64 per scanline) | 16×16 each | 256 from palette | Above tilemap |
| 6 | **Border** (programmable) | Frame border | 256 from palette | Highest (covers everything) |

Each layer can be **enabled, disabled, and prioritized** via NextReg registers. The compositor runs entirely in the FPGA in parallel with CPU execution — there is **zero CPU cost** for layer compositing (beyond the initial memory writes to set up each layer).

### The Layer-Selection NextReg

The most fundamental video NextReg is `0x15` (**Layer 2 shadow, LoRes, tilemap, sprites, layer priority**). It contains one-bit enable flags for each layer and the priority between Layer 2 and the tilemap:

| Bit | Function |
|---|---|
| 0 | Enable Layer 2 (1 = on) |
| 1 | Enable tilemap (1 = on) |
| 2 | Enable sprites (1 = on) |
| 3 | Select LoRes mode (1 = on) |
| 4 | Layer 2 / tilemap priority bit (1 = tilemap over Layer 2) |
| 5–7 | Reserved |

> [!TIP]
> For a first graphics program, enable **only Layer 2** (`NextReg 0x15 = 0x01`). This gives you a 256-color framebuffer with no attribute constraints and no need to understand sprites or tilemaps. See [Layer 2 Framebuffer](#layer-2-framebuffer) below for the programming guide.

---

## The NextReg System

The Next's hardware features are configured via **NextReg registers** — a flat 256-register address space accessed through a two-port I/O protocol. This is the **single most important programmer interface** on the machine: nearly every hardware feature is enabled, tuned, or queried through a NextReg.

### NextReg Access Ports

| Port | Direction | Function |
|---|---|---|
| `#243B` | Write | **Register select** — write the register number (#00–#FF) here |
| `#253B` | Read/Write | **Register data** — read or write the selected register's value |

Example — write the value `0x01` to NextReg `0x15` (enable Layer 2):

```z80
        ld  bc, #243B
        ld  a, #15          ; NextReg 0x15 = Layer 2 / sprites / tilemap config
        out (c), a
        ld  bc, #253B
        ld  a, #01          ; enable Layer 2, disable others
        out (c), a
```

The Z80N instruction set also has dedicated `NEXTREG` instructions that combine the two-port sequence into a single instruction — see [The Z80N CPU](#the-z80n-cpu) below for the full Z80N extension set.

### Most-Used NextReg Quick Reference

| Reg | Name | Function |
|---|---|---|
| `0x00` | Machine ID | Read-only — returns hardware revision (e.g. `0x0A` = Issue 4) |
| `0x05` | Peripheral 1 | Joystick 1/2 mode, 50/60 Hz, scandoubler — see [Joystick System](#joystick-system) |
| `0x06` | Peripheral 2 | Kempston mouse, Multiface, divMMC, scan doubler |
| `0x07` | Turbo mode | CPU speed: `0` = 3.5 MHz, `1` = 7 MHz, `2` = 14 MHz, `3` = 28 MHz |
| `0x08` | Peripheral 3 | DAC A/B/C/D enables, SpecDrum, Timex modes |
| `0x0A` | Layer 2 RAM page | Selects which 16 KB bank is paged at `#0000–#3FFF` for Layer 2 writes |
| `0x12` | Layer 2 offset X | Layer 2 horizontal scroll offset |
| `0x13` | Layer 2 offset Y | Layer 2 vertical scroll offset |
| `0x15` | Layer 2 / sprites / tilemap enable | See table above |
| `0x16` | Layer 2 resolution | 0 = 256×192, 1 = 320×256 |
| `0x1A` | Layer 2 RAM page (alt) | Direct select of which 16 KB bank to page |
| `0x29` | Sprite collision | Read collision flags; write to clear |
| `0x30`–`0x33` | Tilemap scroll X/Y | Pixel-precise scroll offsets |
| `0x40` | Palette index | Write-only — select palette entry for write |
| `0x41` | Palette value | Write the 8-bit palette value (in palette write mode) |
| `0x42` | Palette value (16-bit, RGB565) | Write the upper 8 bits of a 16-bit palette entry |
| `0x4A` | Palette write mode | 0/1/2/3 = paletted/9-bit/16-bit/24-bit |
| `0x50` | Sprite system | Sprite enable, pattern/attribute upload protocol |
| `0x6E` | Tilemap mode | 40×32 vs 80×32, 4-bit vs 8-bit patterns |
| `0x6F` | Tilemap address high | High byte of tilemap write address |
| `0x6B` | DMA port | Direct DMA register access (legacy; main DMA port is `#6B`/`#7B`) |
| `0x70` | Tilemap base address | High byte of tilemap RAM base |
| `0x71` | Tilemap attribute base | High byte of attribute RAM base |

For the full 256-register list, see the [official Next documentation](https://www.specnext.com/tbblue-io-port-system/) or [io_port_map.md](../../10_references/io_port_map.md).

---

## I/O Port Summary

Beyond the NextReg system, the Next exposes hardware features through traditional I/O ports. The complete port map is in [memory_and_io_next.md](../../05_development/03_memory_and_io/memory_and_io_next.md); the most important ports:

| Port | Function |
|---|---|
| `#FE` | Standard Spectrum ULA port — border, beeper, MIC, keyboard (compatibility) |
| `#1F` / `#37` | Kempston joystick 1 / 2 — see [Joystick System](#joystick-system) |
| `#FFFD` / `#BFFD` | AY-3-8912 register select / data (first AY) |
| `#1FFD` | +2A/+3 paging compatibility port |
| `#7FFD` | 128K paging compatibility port |
| `#123B` | Layer 2 bank select (16 KB bank at `#0000–#3FFF`) — see [Layer 2](#layer-2-framebuffer) |
| `#243B` / `#253B` | NextReg select / data |
| `#303B` / `#55` / `#57` | Sprite pattern/attribute upload — see [Hardware Sprites](#hardware-sprites) |
| `#6B` / `#7B` | DMA register select / data — see [DMA Controller](#dma-controller). Also tilemap address/data. |
| `#60` / `#61` | Copper instruction write (low/high byte) — see [The Copper Coprocessor](#the-copper-coprocessor) |

The Next's port decoding is deliberately **complex** to support all the classic modes — for the precise port decoding logic (full vs partial, address mask conventions), see [memory_and_io_next.md](../../05_development/03_memory_and_io/memory_and_io_next.md).

---

## Layer 2 Framebuffer

The **Layer 2** framebuffer is the Next's most-impactful graphics upgrade. Where every prior Spectrum (including the original 48K, all clones, and even the Russian TS-Conf machines) was bound to the **attribute model** — 8×8 pixel cells with two colors per cell — Layer 2 gives the programmer a **true 256-color 8-bpp framebuffer**, addressable pixel-by-pixel with no attribute constraint at all.

For game developers, Layer 2 is what makes the Next feel like a 16-bit console: full-color backgrounds, pre-rendered title screens, digitized images, and even software 3D — all at 50 Hz, with no raster tricks and no CPU contention from the video circuit.

### Layer 2 Specifications

| Feature | Value |
|---|---|
| **Resolution** | 256×192 (standard) / 320×256 (extended) |
| **Color depth** | **8 bits per pixel** (256 simultaneous colors) |
| **Framebuffer size** | 256×192 = **48 KB** (320×256 = 80 KB) |
| **Palette** | 256 entries, each selectable from a 24-bit RGB (or 9-bit RGB in legacy mode) |
| **Banking** | Framebuffer is paged into the Z80 address space **16 KB at a time** at `#0000–#3FFF` |
| **Shadow layer** | Yes — Layer 2 can have a hidden second framebuffer for double-buffering |
| **Pixel read** | Yes — the Z80N `PIXELDAT` instruction reads a pixel at address DE |
| **Priority** | Above the ULA screen (Layer 1), below sprites (Layer 5) |
| **CPU contention** | **None** — Layer 2 fetches from dedicated RAM, not contended memory |

The framebuffer is **not** in main RAM — it occupies its own dedicated bank of FPGA RAM. You access it through a **bank-switching protocol** that pages 16 KB chunks of it into the lower 16 KB of the Z80 address space (`#0000`–`#3FFF`).

### Bank Switching — The Three-Window Model

The 48 KB framebuffer for the standard 256×192 mode is divided into **three 16 KB windows**:

| Window | Lines covered | NextReg `0x12/0x13` (offsets) |
|---|---|---|
| **Window 0** | Lines 0–63 | Y offset 0–63 |
| **Window 1** | Lines 64–127 | Y offset 0–63 |
| **Window 2** | Lines 128–191 | Y offset 0–63 |

To write a pixel, you select the appropriate window by writing the window number to port `#123B`. Once the window is selected, the 16 KB at `#0000–#3FFF` becomes a linear bitmap of that 64-line region — pixel `(x, y)` within the window is at byte `y × 256 + x` (since each line is 256 bytes wide).

| Value written to `#123B` | Window paged at `#0000–#3FFF` | Lines covered |
|---|---|---|
| `0` | Window 0 | 0–63 |
| `1` | Window 1 | 64–127 |
| `2` | Window 2 | 128–191 |
| `3` | **Disable Layer 2 banking** — restore ROM/RAM at `#0000–#3FFF` |

> [!WARNING]
> While Layer 2 banking is active, **the lower 16 KB of the Z80's address space is the framebuffer, not ROM/RAM**. Code that runs from `#0000–#3FFF` (e.g., RST routines, interrupt handlers in low RAM) will not work — the CPU will fetch framebuffer bytes as instructions. Always disable Layer 2 banking (write 3 to `#123B`) before returning to code that uses the low memory, or move your interrupt handler to high RAM.

### Setting a Pixel — Full Example

```z80
; ============================================================
; plot_pixel: Set Layer 2 pixel at (E=x, L=y) to color A
; Uses: A, B, C, D, E, H, L
; ============================================================
plot_pixel:
        ; 1. Determine which window (0/1/2) the line is in
        ld      a, l                ; A = Y
        and     %11000000           ; isolate top 2 bits of Y
        rrca
        rrca                        ; move to bits 1-0
        ld      c, a                ; C = window number (0/1/2)

        ; 2. Page the appropriate window
        ld      b, >#123B
        out     (c), c              ; OUT (#123B), window number

        ; 3. Compute the in-window address: byte = (Y mod 64) * 256 + X
        ld      a, l
        and     %00111111           ; A = Y mod 64 (line within window)
        ld      h, a                ; H = line
        ld      l, e                ; L = X (passed in E)
        ; HL = (line * 256) + X — H = line, L = X

        ; 4. Write the pixel
        ld      a, (current_color)
        ld      (hl), a             ; store the 8-bit color index
        ret
```

### The 256-Color Palette

Layer 2 pixels are **palette indices** — each byte in the framebuffer is an index 0–255 into a 256-entry palette. The palette entries themselves are 24-bit RGB on the Next, but are commonly configured as **9-bit RGB** (3 bits per channel) for compatibility with the Next's other layers.

The palette is programmed through a **3-port protocol**:

| Port | Function |
|---|---|
| `#40` | Write the **palette index** to select (0–255) |
| `#41` | Write the **palette value** (the format depends on NextReg `0x4A` mode) |
| NextReg `0x4A` | Select palette write mode: `0` = 8-bit paletted, `1` = 9-bit RGB (3 writes), `2` = 16-bit RGB565 (2 writes), `3` = 24-bit RGB (3 writes) |

Layer 2 shares its palette with the ULA, sprites, and tilemap by default. To give Layer 2 its own palette, use the **palette offset** feature — Layer 2 can use palette entries 0–63 while sprites use 64–127, etc.

### Extended Resolution — 320×256

The Next's **extended Layer 2 mode** increases the resolution from 256×192 to **320×256** — a 30% wider and 33% taller image. Enabled via NextReg `0x16`: `0` = standard 256×192, `1` = extended 320×256. In 320×256 mode, the framebuffer grows from 48 KB to **80 KB**, requiring 5 windows instead of 3.

> [!TIP]
> 320×256 mode is excellent for **ports of Amiga/Atari ST games** that were originally designed for 320×200 — the 40 extra columns make text and HUDs fit naturally.

### The Shadow Layer 2 — Double Buffering

Layer 2 supports a **shadow framebuffer** — a hidden second 48 KB buffer that can be drawn to without being visible. This enables proper **double-buffering**: write to the shadow buffer during one frame, then swap visible/shadow at vblank to display the new frame with no tearing.

The shadow is controlled via NextReg `0x15` bit 4 — toggling this bit swaps the visible and shadow buffers.

```z80
; Double-buffered frame flip
flip_layer2:
        ld  bc, #243B
        ld  a, #15
        out (c), a
        ld  b, >#253B
        in  a, (c)                 ; read current value
        xor  %00010000             ; toggle shadow bit (bit 4)
        out (c), a
        ret
```

### Fast Full-Screen Fill

```z80
; Fill the entire Layer 2 with color A
fill_layer2:
        ld      b, 3                  ; 3 windows
        ld      c, 0                  ; start with window 0
.fill_window:
        push    bc
        ld      b, >#123B
        out     (c), c
        ld      hl, #0000
        ld      (hl), a
        ld      d, h
        ld      e, l
        inc     de
        ld      bc, 16383
        ldir                          ; fast block fill
        pop     bc
        inc     c
        djnz    .fill_window
        ld      bc, #123B
        ld      a, 3
        out     (c), a                ; restore ROM at low memory
        ret
```

At 28 MHz, this fills the entire 48 KB framebuffer in under 1 ms — fast enough to do multiple times per frame.

### Hardware Scrolling

Layer 2's hardware X/Y offset NextRegs (`0x12`/`0x13`) provide **free** hardware scrolling — write a new offset and the entire framebuffer shifts. This is the single fastest way to scroll on the Next, with zero CPU cost.

```z80
; Scroll right by 1 pixel
scroll_right:
        ld      bc, #243B
        ld      a, #12                ; Layer 2 X offset
        out     (c), a
        ld      b, >#253B
        in      a, (c)                ; read current X offset
        inc     a                     ; scroll right by 1
        out     (c), a                ; write back
        ret
```

### Layer 2 vs Original Spectrum

| Capability | Original 48K | Next Layer 2 |
|---|---|---|
| **Colors per pixel** | 2 (per 8×8 cell) | **256** |
| **Frame buffer size** | 6.75 KB (6144 pixels + 768 attrs) | 48 KB (256×192×8 bpp) |
| **Pixel address** | Complex (line / 8 + (line % 8) × 32 + col) | **Linear** (window: line × 256 + col) |
| **CPU contention** | Yes (ULA steals cycles) | **None** (separate RAM) |
| **Attribute clash** | Yes (8×8 cells limit color placement) | **None** (every pixel has its own color) |
| **Scrolling** | Painful (re-render every shifted pixel) | **Easy** (write Y offset NextReg, hardware scrolls) |
| **Double buffering** | Impossible (only one screen RAM) | **Built-in** (shadow framebuffer) |

For game developers moving from classic Spectrum to the Next, Layer 2 is the single most impactful change — it eliminates the attribute clash problem that defined Spectrum graphics for 30 years.

---

## Hardware Sprites

The Next's **hardware sprite engine** is the platform's first-ever sanctioned use of hardware sprites — every prior "sprite" trick on the Spectrum (pre-shifted software sprites, attribute-color sprites, BEEP-raster interrupts) was a CPU-side workaround for the ULA's lack of sprite hardware. On the Next, sprites are entirely GPU-side: a sprite can move across the screen while the CPU does something else entirely.

### Sprite Engine Capabilities

| Feature | Value |
|---|---|
| **Sprite pattern memory** | 64 KB (separate from main RAM) |
| **Pattern size** | 16×16 pixels (fixed) — no 8×8 or 32×32 |
| **Color depth** | **4-bit** (16 colors from palette) or **8-bit** (256 colors from palette) — per-sprite selectable |
| **Patterns per engine** | **64** (4-bit) or **32** (8-bit) within the 64 KB pattern RAM |
| **Sprites per frame** | **64** attribute slots |
| **Sprites visible per scanline** | **64** (hardware limit — no flicker, no per-line priority scan) |
| **Per-sprite features** | Mirror X, mirror Y, rotate 90°, 4-/8-bit type, palette offset, relative anchor |
| **Position range** | X: 0–511, Y: 0–255 (with optional 9-bit X via the `X MSB` flag in attribute byte 4) |
| **Collision detection** | Yes — hardware reports when any two sprite patterns overlap (with optional masking) |

The sprite engine reads from a **64 KB pattern RAM** that is **entirely separate** from main RAM and from Layer 2 / tilemap memory. You upload patterns to it through a dedicated port protocol; you do not write patterns directly to memory addresses.

### Sprite Pattern Memory Layout

Pattern RAM holds the sprite pixel data, organized as **pattern slots**. Each slot is a 16×16-pixel image:

| Pattern type | Bytes per slot | Pattern slots in 64 KB | Slot numbering |
|---|---|---|---|
| **4-bit** (16 colors) | 128 bytes | 64 patterns (slots 0–63) | `(slot × 128)` |
| **8-bit** (256 colors) | 256 bytes | 32 patterns (slots 0–31, occupying slots 0–63 pairwise) | `(slot × 256)` |

A 4-bit pattern uses one **nibble per pixel**, with the upper nibble first (pixel 0 in upper nibble of byte 0, pixel 1 in lower nibble of byte 0, etc.). An 8-bit pattern uses one byte per pixel, with each byte indexing the active palette.

### Pattern Upload Protocol

Patterns are written via a **two-port protocol**:

| Port | Function |
|---|---|
| `#303B` | Write the **pattern slot number** (0–63 for 4-bit, 0–31 for 8-bit) |
| `#55` | Write pattern data — the **next byte** goes to the next sequential position in the slot |

After selecting the slot via `#303B`, sequential writes to `#55` fill the pattern RAM. The internal pointer auto-increments after each byte. For a 16×16 4-bit sprite (128 bytes), you issue 128 writes to `#55`; for 8-bit, 256 writes.

Example — upload a 4-bit pattern to slot 5:

```z80
        ; HL = pointer to 128-byte pattern data
        ; Upload to pattern slot 5
        ld  bc, #303B
        ld  a, 5
        out (c), a               ; select slot 5
        ld  b, >#55              ; BC = #0055
        ld  a, 128               ; byte count
.loop:
        outi                     ; OUT (C), (HL); HL++; B--
        jr  nz, .loop
        ret
```

> [!NOTE]
> The `#55` upload port uses the pattern RAM's internal pointer, not the slot base address. If you write 130 bytes after selecting slot 5, the last 2 bytes overwrite the **first 2 bytes of slot 6**. Always write exactly the pattern's full byte count, or re-select the slot before each upload.

### Sprite Attribute Structure

Once patterns are uploaded, you create **sprite instances** by writing **5-byte attribute records** to the sprite attribute pipeline. Each record describes one sprite on screen.

| Port | Function |
|---|---|
| `#303B` | Write the **attribute slot index** (0–63) before writing the record |
| `#57` | Write 5 sequential bytes — they form one attribute record at the previously-selected slot |

After writing the slot index to `#303B`, you write 5 bytes to `#57`. The internal pointer increments through the 5 bytes of the record, then advances the slot index. Writing a new record to slot N+1 does **not** require re-writing the slot index — the pipeline auto-advances.

### The 5-Byte Attribute Record

| Byte | Field | Bits |
|---|---|---|
| **1** | **X coordinate (low 8 bits)** | 0–255 |
| **2** | **Y coordinate** | 0–255 (line 0 = top) |
| **3** | **Pattern number (low 6 bits) + palette offset (bit 7) + X MSB (bit 0)** | Bits 0–5: pattern number; bit 6: palette offset enable; bit 7: X MSB (extending X to 0–511) |
| **4** | **Misc flags** | Bit 4: rotate 90°; bit 6: mirror X; bit 7: mirror Y |
| **5** | **Sprite type** | Bit 7: enable this sprite (1 = visible); bit 6: 8-bit pattern type (vs 4-bit); bits 0–3: palette offset value (0–15, adds to palette index when offset is enabled) |

Example — place a sprite at (100, 50) using pattern 2:

```z80
        ld  bc, #303B
        ld  a, 0                 ; sprite slot 0 (first sprite)
        out (c), a
        ld  b, >#57              ; BC = #0057
        ld  a, 100               ; X = 100
        out (c), a
        ld  a, 50                ; Y = 50
        out (c), a
        ld  a, %00000010         ; pattern 2, no X MSB, no palette offset
        out (c), a
        ld  a, %00000000         ; no rotation/mirror
        out (c), a
        ld  a, %10000000         ; enable sprite, 4-bit type (bit 6 = 0)
        out (c), a
        ret
```

### Sprite Types — 4-bit vs 8-bit

Each sprite individually selects **4-bit** or **8-bit** rendering via bit 6 of attribute byte 5:

- **4-bit sprites**: each pixel is a nibble, using the lower 16 entries of the palette. Faster to upload, more patterns fit in 64 KB.
- **8-bit sprites**: each pixel is a full byte, using any of the 256 palette entries. Slower to upload (256 bytes vs 128), but full color fidelity.

Mix 4-bit and 8-bit sprites freely on the same frame — the engine handles the depth per-sprite.

### Sprite Priority and Transparency

The Next's sprite engine composites sprites in **slot order** — slot 0 is drawn first (at the back), slot 63 last (in front). The Z-order of sprites is therefore fixed by their slot number, not by a per-sprite priority flag.

Palette index **0 is transparent** by default for both 4-bit and 8-bit sprites. Pixels with value 0 are not drawn — sprites of any shape (not just rectangles) can be made by leaving the corners as palette 0. The `LDIX` / `LDPIR` Z80N instructions also respect palette index 0 when copying, allowing fast transparency-aware pattern upload.

### Collision Detection

The sprite engine reports **collisions** through NextReg `0x29` (**Sprite Collision**). The hardware sets bits in this register when any two sprite non-transparent pixels overlap during a scanline:

| Bit | Collision type |
|---|---|
| 0 | Any two sprites with non-transparent pixels overlapped |
| 1 | Any sprite with the (optional) backdrop or any "boundary" |

```z80
        ld  bc, #243B
        ld  a, #29               ; NextReg 0x29 = Sprite Collision
        out (c), a
        ld  b, >#253B            ; BC = #253B
        in  a, (c)               ; read collision flags
        and 1                    ; bit 0 = any-sprite overlap
        jr  nz, .collision
```

The collision flag is **sticky** — once set, it remains until cleared. Clear it by writing any value to NextReg `0x29`, or by reading from it (some firmware revisions auto-clear on read). Re-clear it at the start of each frame.

> [!WARNING]
> The collision register only reports **whether** a collision occurred, not **which** sprites collided. To find out which sprites hit, you must check bounding-box overlap in software. The hardware collision is a fast early-out for "did anything happen this frame"; precise collision is your code's responsibility.

### Per-Scanline Visibility Limit

The Next's sprite engine can render **up to 64 sprites per scanline** without flicker. If more than 64 sprites' X-coordinates put them on the same scanline, sprites beyond the 64th **silently disappear** — they are not drawn, but no error is reported.

For games that may exceed the per-scanline limit:

1. **Cull off-screen sprites** — sprites with Y outside `[0, 191]` or X outside `[-16, 319]` should be marked disabled (bit 7 of attribute byte 5 = 0).
2. **Sort by visual priority** — assign the lowest slot numbers (drawn first) to sprites the player must see, and the highest slot numbers to sprites that can be dropped.
3. **Use the copper** to swap sprite slots mid-frame — see [The Copper Coprocessor](#the-copper-coprocessor) below.

### Typical Sprite Game Loop

```z80
; --- Per-frame sprite update ---
update_sprites:
        ; 1. Update sprite positions based on game logic
        call    move_player
        call    move_enemies

        ; 2. Clear previous collision flag
        ld      bc, #243B
        ld      a, #29
        out     (c), a
        ld      b, >#253B
        xor     a                       ; write 0 to clear
        out     (c), a

        ; 3. Re-upload sprite attributes (positions may have changed)
        ld      hl, sprite_table
        ld      b, 64                   ; 64 sprite slots
        call    upload_sprite_table

        ; 4. Wait for next frame (vblank)
        call    wait_vblank

        ; 5. Read collision register for game logic
        ld      bc, #243B
        ld      a, #29
        out     (c), a
        ld      b, >#253B
        in      a, (c)
        ld      (collision_flags), a
        ret
```

In this pattern, the sprite **patterns** (image data) are uploaded once at startup; the **attributes** (positions, enables) are re-uploaded every frame. This is the standard structure for a Next sprite game.

---

## Hardware Tilemap

The Next's **hardware tilemap** is a tile-based display layer — a 40×32 (or 80×32) grid of 8×8 pixel tiles, each independently selectable from a 256-entry pattern table, with its own per-tile attributes (palette offset, mirror, priority over Layer 2). For games with large scrolling backgrounds (platformers, RPGs, shooters), the tilemap is the most efficient way to fill the screen with detail at zero CPU cost — replacing both the ULA screen (whose 8×8 attribute blocks are too coarse) and Layer 2 (whose per-pixel cost is high for backgrounds).

### Tilemap Specifications

| Feature | Value |
|---|---|
| **Tile grid size** | 40×32 (320×256 pixels) or 80×32 (640×256 pixels) |
| **Tile size** | **8×8 pixels** (fixed) |
| **Pattern table** | 256 entries × 8×8 = 16 KB pattern memory |
| **Color depth** | **4-bit** (16 colors) per pixel OR **8-bit** (256 colors) per pixel — engine-wide selection |
| **Tilemap RAM size** | **40×32 mode**: 40×32×2 = 2560 bytes (tile number + attribute byte); **80×32 mode**: 80×32×1 = 2560 bytes (tile number only, no attributes) |
| **Scroll range** | X: 0–511 (wraps); Y: 0–255 |
| **Per-tile features** | Palette offset (0–15), mirror X, mirror Y, rotate 90°, "priority over Layer 2" flag |
| **CPU contention** | **None** — tilemap RAM is separate from main RAM |

### Two Modes — 40×32 vs 80×32

Selected via NextReg `0x6E` (**Tilemap mode**):

| Mode | Resolution | Tile bytes | Per-tile attributes | Use case |
|---|---|---|---|---|
| **40×32** | 320×256 pixels | 2 bytes per tile (number + attr) | Yes (palette offset, mirror, priority) | Standard tile-based games |
| **80×32** | 640×256 pixels | 1 byte per tile (number only) | No | Text modes, ASCII art, double-width maps |

The 40×32 mode is the typical choice for games — it provides per-tile control over palette and orientation while remaining a comfortable resolution for 8×8 pixel art. The 80×32 mode is suited for text-heavy applications (terminals, editors, debug overlays) where each tile is one character cell.

### Tilemap Write Ports

The tilemap grid is stored in **dedicated RAM** inside the FPGA. Unlike Layer 2, you do not page this RAM into the Z80 address space — you write to it via a **two-port protocol** that auto-increments through addresses.

| Port | Function |
|---|---|
| NextReg `0x6E` | Mode select (40×32 with attrs vs 80×32 no attrs) — also enables 8-bit patterns |
| `#6B` | **Tilemap address select** (low byte) — write the address low byte here |
| NextReg `0x6F` | **Tilemap address select** (high byte) — write the address high byte |
| `#7B` (or `#40`-`#43` in some firmware) | **Tilemap data** — sequential writes go to consecutive tile addresses |

The tilemap is **interleaved** in 40×32 mode — each tile occupies 2 bytes, the first being the pattern number and the second being the attribute. To write tile (x, y) with pattern P and attribute A:

```
address = (y * 40 + x) * 2
write P at address
write A at address + 1
```

### The Pattern Table

The pattern table holds **256 tile images**, each 8×8 pixels:

| Color depth | Bytes per tile | Total pattern table size |
|---|---|---|
| 4-bit (16 colors) | 32 bytes | 8 KB |
| 8-bit (256 colors) | 64 bytes | 16 KB |

A 4-bit tile's 32 bytes are organized as 8 rows × 4 bytes-per-row (each row = 8 pixels × 4 bits = 32 bits = 4 bytes). The first 4 bytes are the top row of the tile, the next 4 bytes are the second row, etc.

### Tile Attributes (40×32 Mode Only)

| Bit | Function |
|---|---|
| 0–3 | **Palette offset** (0–15) — added to the pattern's palette index |
| 4 | Reserved |
| 5 | **X mirror** (flip the tile horizontally) |
| 6 | **Y mirror** (flip the tile vertically) |
| 7 | **Priority over Layer 2** — if set, the tile is drawn above Layer 2 instead of below |

The palette offset lets a single tile pattern render in **16 different color schemes**. The X/Y mirror bits are essential for **pattern compression** — a single "tree" tile can render as itself, mirror-X, mirror-Y, or both (rotated 180°). This is the standard tileset-compression technique used in NES / SNES / GBA games.

The priority bit (7) is the most powerful — it lets the tilemap have **holes** that show Layer 2 through them. Use this for "background + foreground" splits: most tiles are background (priority 0), but a few foreground tiles (priority 1) appear in front of Layer 2 sprites.

### Scrolling — X and Y Offsets

The tilemap's **scroll position** is set via NextRegs `0x30`–`0x33`:

| Reg | Name | Range |
|---|---|---|
| `0x30` | Tilemap offset X (low byte) | 0–255 |
| `0x31` | Tilemap offset X (high byte, only bits 0–0) | Extends X to 0–511 |
| `0x32` | Tilemap offset Y | 0–255 |
| `0x33` | Tilemap vertical offset (high byte) | (rarely used) |

The scroll position is in **pixels**, not tiles — so an X offset of 1 moves the tilemap right by 1 pixel, revealing 1 new pixel column from the next tile.

The standard scrolling technique is **wraparound scrolling**: when the X offset reaches 8 (one full tile), shift the tilemap contents in RAM and reset the offset to 0. Alternatively, the **copper** can swap between two pre-built tilemaps mid-frame for parallax scrolling.

### Tilemap vs Layer 2 — When to Use Which

| Criterion | Layer 2 | Tilemap |
|---|---|---|
| **Best for** | Detailed artwork, pre-rendered images, parallax backgrounds | Game backgrounds with repeating tiles, platformers, RPG maps |
| **Memory cost** | 48 KB (256×192×8 bpp) | 2.5 KB tilemap + 16 KB patterns = ~18 KB |
| **CPU cost to redraw** | High (full framebuffer) | Low (just modified tiles) |
| **Scrolling cost** | Free (hardware X/Y offsets) | Free (hardware X/Y offsets) — but needs tile refill at boundaries |
| **Pattern reuse** | None (every pixel stored) | Excellent (256 patterns reused across grid) |
| **Per-pixel color** | 256 | 16 (4-bit) or 256 (8-bit) |
| **Text rendering** | Manual | Trivial (80×32 mode) |

**Guideline**: Use the tilemap for **structured backgrounds** (grid-based game worlds, text overlays). Use Layer 2 for **free-form artwork** (digitized images, hand-drawn title screens, parallax backdrops). The two can coexist — Layer 2 with the tilemap on top is a common combination.

---

## The Copper Coprocessor

The Next's **copper** is a small programmable coprocessor that runs in parallel with the CPU and writes to NextReg registers at precisely-defined scanline positions. Named by analogy to the Amiga's copper (which performs the same role on the Amiga chipset), the Next's copper is the key to **per-scanline video effects** without cycle-exact CPU code: raster palette changes, mid-frame mode switches (Layer 2 → tilemap, sprites appear at line 100), horizontal splits, and per-scanline scroll offsets.

### What the Copper Is — and Is Not

| Property | Value |
|---|---|
| **Programming model** | A flat list of instructions, executed in order |
| **Instruction set** | 3 opcodes: `WAIT`, `MOVE`, `STOP` (and `DISABLE`) |
| **Operating mode** | Runs in parallel with the CPU — does not block CPU execution |
| **Memory access** | **Cannot read main RAM** — only writes to NextReg registers |
| **Timing reference** | Tied to the video frame — `WAIT line, hpos` waits for a specific scanline + horizontal position |
| **Instruction rate** | One copper instruction per scanline (approximately) |
| **List storage** | Internal FPGA RAM — written via two-port I/O protocol |

The copper is **not** a general-purpose second processor. It cannot read RAM, cannot call subroutines, cannot branch — it is a simple state machine that walks a list of `WAIT` + `MOVE` pairs. What it gives you is **synchronization with the raster beam**, which the CPU alone cannot do reliably without dedicated cycle-counted loops.

### The Three Copper Instructions

**WAIT** — `WAIT line, hpos` pauses the copper until the raster beam reaches scanline `line` (0–255, with bit 8 extending to 0–311) at horizontal position `hpos` (0–223, in units of ~8 pixels).

**MOVE** — `MOVE reg, value` writes `value` (8-bit) to NextReg `reg`. MOVE takes one scanline to complete — you cannot issue two MOVEs in the same scanline.

**STOP / DISABLE** — halts the copper. The end of a copper list is conventionally marked with `STOP`.

### Instruction Encoding

Each copper instruction is encoded as **2 bytes** (a 16-bit word). The two ports that accept copper instructions are:

| Port | Function |
|---|---|
| `#60` | Write the **low byte** of the next copper instruction |
| `#61` | Write the **high byte** of the next copper instruction |

| Opcode | Byte 1 (low) | Byte 2 (high) | Encoding |
|---|---|---|---|
| `WAIT` | `hpos` (0–223) | `0xxxxxxx` + bit 7 = WAIT opcode | High byte bit 7 = 0 marks WAIT; lower bits = line |
| `MOVE` | `value` | `1xxxxxxx` + bits 6–0 = reg number | High byte bit 7 = 1 marks MOVE; lower 7 bits = reg |
| `STOP` | `0x00` (any) | `0xFE` or specific stop marker | (firmware-dependent — check Next docs) |
| `DISABLE` | `0x00` | `0xFF` | (firmware-dependent) |

### Copper Timing Constraints

| Constraint | Value |
|---|---|
| **Instructions per scanline** | **1** (one MOVE per scanline) |
| **WAIT resolution** | 1 scanline (vertical), ~8 pixels (horizontal) |
| **Total list size** | Limited by FPGA RAM (typically ~2 KB = ~1024 instructions) |
| **Wraparound** | At the end of the frame (after line 311), the copper restarts from the top of its list |

The "one MOVE per scanline" rule is the copper's defining limit. To change **N** registers at the same scanline, you must spread the writes across **N consecutive scanlines**. For a palette swap of 256 entries, this means the swap takes 256 scanlines — most of the visible frame.

### Common Copper Effects

**1. Raster bars (copper bars)** — change the border color every scanline:

```
WAIT 0, 0
MOVE 0x14, 1     ; border = blue
WAIT 1, 0
MOVE 0x14, 2     ; border = red
WAIT 2, 0
MOVE 0x14, 3     ; border = magenta
...
```

**2. Mid-frame mode switch** — Layer 2 on top half, tilemap on bottom half:

```
WAIT 0, 0
MOVE 0x15, 0x01     ; enable only Layer 2 (bit 0)
WAIT 192, 0         ; wait until line 192
MOVE 0x15, 0x02     ; enable only tilemap (bit 1)
STOP
```

**3. Per-scanline palette swap** — animate the palette across the frame for a "heat haze" or "water" effect.

**4. Horizontal split (sprite multiplexing)** — swap sprite slots mid-frame to double the effective sprite count:

```
WAIT 0, 0
MOVE 0x50, 0x00     ; config sprites for top half — sprites 0-7 = enemies
WAIT 128, 0         ; wait to middle of screen
MOVE 0x50, 0x01     ; config sprites for bottom half — sprites 0-7 = bullets
STOP
```

This is the standard technique for fitting more than 64 sprites in a single frame.

### Copper vs CPU Raster Effects

| Criterion | CPU multicolor | Copper |
|---|---|---|
| **CPU cost** | 100% during visible lines | **0%** |
| **Effects possible** | Per-pixel attribute changes (8×1 color cells) | Per-scanline register changes |
| **Resolution** | Pixel-exact | ~8-pixel horizontal |
| **Register targets** | Screen RAM, attribute RAM | Any NextReg |
| **Complexity** | High (cycle counting, contention handling) | Low (declarative list) |

The copper and CPU multicolor are **complementary** — use the copper for register writes (palettes, mode switches, scroll offsets) and reserve CPU multicolor for screen-RAM writes (8×1 attribute changes that the copper cannot do).

---

## DMA Controller

The Next's **DMA controller** is a hardware data mover that performs memory-to-memory, memory-to-I/O, and I/O-to-I/O transfers without CPU intervention. Derived from the **Zilog Z80 DMA** (the Z8410 chip used in CP/M-era systems and the Amstrad CPC), the Next's DMA is the platform's solution to "do this 16 KB block copy / pattern fill / sample load while I'm computing something else" — replacing thousands of `LDIR` cycles with a single register write that fires off the transfer and returns immediately.

### What DMA Does

| Property | Value |
|---|---|
| **Source types** | Memory address, I/O port |
| **Destination types** | Memory address, I/O port |
| **Transfer modes** | Byte (one byte per bus cycle), Burst (continuous until source/dest not ready), Continuous (entire transfer in one bus lock) |
| **Transfer length** | Up to 64 KB per command (16-bit counter) |
| **Address increment** | Source/destination can each be incremented, decremented, or held fixed |
| **Pattern matching** | Yes — transfer can stop when a specific byte is read (search mode) |
| **Interrupt on completion** | Yes (optional) |
| **CPU involvement** | **Zero** during the transfer — CPU is paused (bus arbitration) until the DMA completes |
| **Throughput at 28 MHz** | ~28 MB/s (memory-to-memory, byte mode) — vs ~3.5 MB/s for `LDIR` at 3.5 MHz |

### The DMA Register Set

| Port | Function |
|---|---|
| `#6B` | **Register select / command write** — write a register number or command byte here |
| `#7B` | **Register data** — write/read the selected register's value |

The DMA's register file follows the **Z80 DMA convention** — there are a set of "_WR0" through "_WR6" command registers, each controlling a different aspect of the transfer. The most important commands:

| Command | Function |
|---|---|
| `0x7D` | Reset the DMA to its initial state |
| `0xC3` | Load + Enable — load the source/dest/length, then start the transfer |
| `0xCF` | Reset + Load (combined — common initialization) |
| `0xAB` / `0xAF` | Enable / disable interrupt on completion |
| `0x83` / `0x87` | Disable / enable DMA |
| `0xB3` | Read status |

### Transfer Modes

**Byte mode** — The DMA transfers **one byte per bus cycle**, interleaving with the CPU. The CPU continues executing (slowly). Useful for transferring data while keeping the CPU responsive.

**Burst mode** — The DMA transfers bytes **as fast as the source/dest can accept them**. The CPU is mostly halted. Default for memory-to-memory transfers.

**Continuous mode** — The DMA **locks the bus** for the entire transfer — the CPU is fully halted. Fastest mode but blocks all CPU work, including interrupt handling.

> [!WARNING]
> Continuous-mode DMA blocks CPU interrupts. If an INT is pending (e.g., the frame interrupt), it will be delayed until the DMA completes. For long transfers (>1 ms), this can cause the program to miss a frame — use burst mode instead, which allows interrupts between bursts.

### Source/Destination Combinations

| Source | Destination | Use case |
|---|---|---|
| Memory | Memory | Block copy, screen clear, snapshot save |
| Memory | I/O port | Upload 16 KB to Layer 2 framebuffer, stream sample data to a DAC |
| I/O port | Memory | Read 512 bytes from IDE controller into RAM |
| I/O port | I/O port | Bridge data from SD card to UART (e.g., file streaming to WiFi) |

The "fixed address" mode (no increment) is essential for I/O port operations — the destination port stays at the same address (e.g., `#55` for sprite upload) while the source memory increments through the pattern data.

### DMA-Driven Sample Playback

A common use case: drive 8-bit PCM samples to a DAC at a fixed rate. The DMA reads from a sample buffer in RAM and writes to the DAC port (`#1F` when Covox/SpecDrum is enabled). The copper or a timer triggers a new DMA burst every scanline (64 μs), giving an ~15.6 kHz sample rate.

```z80
; Per-scanline DMA burst: send 320 bytes of sample to DAC
play_sample_burst:
        ld  a, #C3              ; LOAD + ENABLE
        ld  bc, #6B
        out (c), a
        ret
```

The copper fires this routine every scanline. Result: 320 samples per scanline × 311 scanlines per frame × 50 Hz = ~15.6 kHz sample rate — better than telephone-quality audio, with zero ongoing CPU cost beyond the per-scanline retrigger.

### DMA vs LDIR vs Copper

| Criterion | `LDIR` (CPU) | DMA | Copper |
|---|---|---|---|
| **Source/dest** | Memory only | Memory + I/O | NextRegs only |
| **Transfer length** | Up to 64 KB | Up to 64 KB | Single byte per instruction |
| **CPU cost** | 100% (21 T/byte) | ~0% (DMA steals cycles but no instruction fetch) | 0% |
| **Pattern match** | No | Yes | No |
| **Interrupt on completion** | No | Yes | No |

**Guideline**: Use `LDIR` for short transfers (<256 bytes) where DMA setup overhead exceeds the transfer cost. Use **DMA** for bulk data movement (16 KB+), pattern fills, and I/O streaming. Use **copper** for raster-synchronized register writes.

---

## Joystick System

The Next ends the joystick standards war by simply implementing **all of it**. Its two DE-9 ports are not wired to any fixed protocol — each port is individually switchable between Sinclair-row, Cursor, Kempston, and Mega Drive modes through a NextReg, and the FPGA presents the stick to software as whichever standard was selected. A 1984 game expecting a Cursor joystick and a 1994 demo expecting Kempston can both work, on the same machine, one port each.

Two further upgrades matter for new software: the Next is one of the few Spectrum-family machines with **two Kempston-style ports** (`#1F` and `#37`), making dual-stick games practical; and its Mega Drive pad support brings **three or six fire buttons** to a platform that spent four decades with one.

### The Two Ports and NextReg #05

Both DB9 connectors use the **Atari-standard pinout**. What each port *is* depends on NextReg `0x05` (Peripheral 1 setting), which holds a 3-bit mode for each joystick:

| NextReg `0x05` bits | Field |
|---|---|
| 7–6 + 3 | Joystick 1 mode (bits 7–6 = low two bits, bit 3 = high bit) |
| 5–4 + 1 | Joystick 2 mode (bits 5–4 = low two bits, bit 1 = high bit) |
| 2 | 50/60 Hz mode — unrelated, preserve on write |
| 0 | Scandoubler enable — unrelated, preserve on write |

**Mode values:**

| Mode | Standard | Read via |
|---|---|---|
| `000` | Sinclair 2 (keys 67890) | keyboard row `#EFFE` |
| `001` | Kempston 1 | port `#1F` |
| `010` | Cursor (keys 56780) | keyboard rows `#F7FE`/`#EFFE` |
| `011` | Sinclair 1 (keys 12345) | keyboard row `#F7FE` |
| `100` | Kempston 2 | port `#37` |
| `101` | MD 1 — Mega Drive pad, 3 or 6 button | port `#1F` |
| `110` | MD 2 — Mega Drive pad, 3 or 6 button | port `#37` |

In the matrix modes the FPGA injects the stick state into the emulated keyboard rows — the game's ordinary keyboard-scan code sees keypresses, exactly like a real Interface 2. In Kempston/MD modes the port returns an active-high byte.

> [!WARNING]
> **The Sinclair numbering trap.** The official Next documentation labels the 67890 mapping "Sinclair 2" and 12345 "Sinclair 1" — the *opposite* of the Interface 2-era convention used by most games and by [Joystick Interfaces](../../03_io/peripherals/joystick.md) (Sinclair 1 = 6–0, Sinclair 2 = 1–5). The numbering was never consistent across the ecosystem; when configuring or documenting, specify the **keys**, not the number.

### Configuring and Reading — Complete Example

```z80
; next_joystick.asm — dual Kempston setup on the ZX Spectrum Next
; sjasmplus. NextReg access: #243B = register select, #253B = data.

NR_SEL      equ #243B
NR_DAT      equ #253B
NR_PERIPH1  equ #05

; --- Configure: joy1 = Kempston 1 (mode 001), joy2 = Kempston 2 (mode 100) ---
setup_joysticks:
        ld      bc, NR_SEL
        ld      a, NR_PERIPH1
        out     (c), a          ; select NextReg 0x05
        ld      b, >NR_DAT      ; BC = #253B
        in      a, (c)          ; read current Peripheral 1 value
        and     %00000101       ; clear joy1 bits (7,6,3) and joy2 bits (5,4,1),
                                ; preserve 50/60Hz (bit 2) and scandoubler (bit 0)
        or      %01000010       ; joy1 mode 001 (bit 6) | joy2 mode 100 (bit 1)
        out     (c), a
        ret

; --- Read both sticks: returns B = player 1, C = player 2 ---
; Format: FUDLR active-high (bit 0=R 1=L 2=D 3=U 4=F)
read_both:
        in      a, (#1F)        ; Kempston joy 1
        and     #1F
        ld      b, a
        in      a, (#37)        ; Kempston joy 2
        and     #1F
        ld      c, a
        ret
```

Notes:

- **Always read-modify-write NextReg `0x05`** — it also carries the 50/60 Hz flag and the scandoubler enable; clobbering them changes the video mode.
- The mask `%00000101` clears the six joystick-mode bits while preserving bits 2 and 0.
- The returned byte is the classic Kempston `000FUDLR` layout — every unified reader already written for 1980s hardware works unchanged.

### Mega Drive Pads — More Than One Fire Button

Modes `101`/`110` decode Sega Mega Drive/Genesis pads (3- and 6-button) through the same `#1F`/`#37` ports: directions and the primary fire button occupy the standard Kempston bits, and **the additional buttons appear on the upper bits (5–7)** of the port byte. For software this is the first sanctioned use of those bits in the platform's history — everywhere else they are undefined.

Recommended practice:

1. Detect the Next first (Machine ID NextReg `0x00`), then check the configured mode — never probe upper bits on unknown hardware.
2. Treat extra buttons as **progressive enhancement**: the game must remain fully playable with fire on bit 4 alone, so the same binary runs on clones and original hardware.
3. Offer the mapping in your redefine menu like any other key.

### Port Conflicts to Know

- **`#1F` is also Multiface 1's disable port and DAC B** — with SpecDrum/Covox enabled (NextReg `0x08` bit 3), writes/reads on `#1F` hit the audio DAC; the Multiface enable/disable ports (`#1F`, `#9F`, `#3F`, `#BF`) share the same low addresses. When the Multiface is disabled (NextReg `0x06` bit 3 = 0) and Covox is off, `#1F` is purely the joystick.
- **Kempston mouse** lives at `#FBDF`/`#FFDF`/`#FADF` — different addresses, no conflict with either joystick port.
- Mode changes are **global, not per-process**: if your program switches modes, restore the user's configuration on exit (read `0x05` at startup, keep it, write it back).

---

## Compatibility Modes

The Next can impersonate four classic machines via the **timing-mode NextReg `0x22`** (and its associated memory-map NextRegs). Switching modes at runtime lets a single binary support multiple Spectrums:

| Mode | Memory map | Contention | Frame |
|---|---|---|---|
| **48K** | ROM + 16K contended + 32K uncontended | Yes (`#4000`–`#7FFF`) | 69,888 T-states, 312 lines, 50.08 Hz |
| **128K / +2** | `#7FFD` paging | Yes (banks 1/3/5/7) | 70,908 T-states, 311 lines, 50.02 Hz |
| **+2A / +3** | `#7FFD` + `#1FFD` paging | Yes (split banks) | 70,908 T-states, 311 lines, 50.02 Hz |
| **Pentagon** | `#7FFD` + `#DFFD`/`#EFF7` paging | **No** | 71,680 T-states, 320 lines, 48.83 Hz |

Classic software that runs on any of these machines will run on the Next. **Contention is emulated** in 48K/128K/+3 modes — even cycle-exact demos work.

> [!WARNING]
> The Pentagon mode is **not binary-compatible** with original Sinclair 128K software that depends on contention timing. Software must be specifically compiled for Pentagon (or written to handle the difference). See [video_frame_next.md](../../05_development/05_display_and_timing/video_frame_next.md) for the full timing comparison.

---

## The Z80N CPU

The Next's CPU is not a standard Z80 — it is a **Z80N**, an FPGA soft-core with the standard Z80 instruction set **plus** Next-specific extensions. The most important extensions:

| Instruction | Mnemonic | Function |
|---|---|---|
| `ED 30 nn` | `NEXTREG nn` | Write accumulator to NextReg `nn` (single instruction, vs 2-port sequence) |
| `ED 31 nn mm` | `NEXTREG nn, mm` | Write immediate `mm` to NextReg `nn` |
| `ED 23` | `SWAPNIB` | Swap high/low nibbles of A |
| `ED 24` | `MIRROR` | Mirror (bit-reverse) the bits of A |
| `ED 8A` | `PIXELDAT` | Read a Layer 2 pixel at DE into A |
| `ED 90` | `LDIX` | Like `LDIR`, but skips bytes equal to A (transparency-aware copy) |
| `ED 91` | `LDWX` | Like `LDIX`, but copies with a byte mask from another register |
| `ED 92` | `LDPIR` | Pixel-aware LDIR for fast block fill with transparency |
| `ED 93` | `JP (C)` | Jump to address held at `(HL)` if C matches — useful for jump tables |

The Z80N extensions are **upward-compatible** — code assembled for a standard Z80 runs on the Next unchanged. The extensions are an opt-in convenience for fast graphics and NextReg access. See [memory_and_io_next.md](../../05_development/03_memory_and_io/memory_and_io_next.md) for the full opcode table and cycle timings.

---

## Software Development Entry Points

The Next offers three primary ways to develop software, in increasing order of capability:

### 1. NextBASIC (high-level, beginner)

NextBASIC is the Next's enhanced BASIC dialect, integrated with NextZXOS. It can drive Layer 2, sprites, tilemap, copper, and DMA directly from BASIC commands. Best for: educational programs, simple games, demos, and prototypes. See [nextzxos.md](../../04_operating_systems/nextzxos.md) for the NextBASIC command reference.

### 2. C with z88dk (medium-level, productivity)

The **z88dk** C compiler targets the Next natively, with library functions wrapping Layer 2, sprites, tilemap, copper, and DMA. Best for: games that need C-level structure, larger projects, cross-platform code. See [z88dk.md](../../09_toolchain/z88dk.md) for the toolchain.

### 3. Assembly with sjasmplus (low-level, performance)

The **sjasmplus** assembler is the canonical Next assembler. It supports the Z80N extension instructions and the Next's memory model directly. Best for: demoscene productions, cycle-exact code, performance-critical games. See the assembler's documentation at [z00m128/sjasmplus on GitHub](https://github.com/z00m128/sjasmplus).

### The Developer's Typical Workflow

1. **Code** in z80 assembly (sjasmplus) or C (z88dk), using the [NextReg access pattern](#the-nextreg-system) for hardware features.
2. **Test** in the [CSpect](../../11_emulation/software/cspect.md) emulator — Mike Dailly's reference emulator, fast iteration.
3. **Verify** on real hardware via SD card — for cycle-exact behavior, floating-bus quirks, and HDMI signal fidelity.
4. **Cross-reference** the official Next documentation at [zxnext.io](https://www.zxnext.io/) and [specnext.com](https://www.specnext.com/tbblue-io-port-system/) for the canonical register reference.

---

## Cross-References

### Programming reference (in 05_development)

- [Next memory map and I/O ports](../../05_development/03_memory_and_io/memory_and_io_next.md) — full MMU, 8 KB paging, port decoding
- [Next video frame](../../05_development/05_display_and_timing/video_frame_next.md) — frame timing, contention modes, copper timing
- [Multicolor techniques](../../07_demoscene/multicolor_techniques.md) — the CPU-side raster technique that copper complements
- [Floating bus](../../05_development/05_display_and_timing/floating_bus.md) — alternative raster-sync method (CPU-side)
- [z88dk toolchain](../../09_toolchain/z88dk.md) — C compiler targeting the Next

### OS and emulator coverage

- [NextZXOS](../../04_operating_systems/nextzxos.md) — operating system, NextBASIC, dot commands, function dispatch
- [CSpect emulator](../../11_emulation/software/cspect.md) — reference emulator for Next development
- [ZEsarUX emulator](../../11_emulation/software/zesarux.md) — alternative emulator with better WiFi simulation

### Hardware context

- [ZX Evolution](zx_evo.md) — the Russian equivalent (Pentagon-compatible FPGA Spectrum)
- [TS-Conf](ts_conf.md) — the Russian enhanced video mode (sprites/tilemap/512K VRAM)
- [BaseConf](baseconf.md) — ZX Evolution's default Pentagon 1024 firmware
- [ZX-Uno](zx_uno.md) — open-source FPGA Spectrum (smaller feature set than Next)
- [Karabas family](karabas.md) — Russian open-source Z80 + CPLD clones
- [Original 48K](../original/zx_spectrum_16k_48k.md) — the Next's binary-compatibility target
- [Joystick Interfaces](../../03_io/peripherals/joystick.md) — the protocols the Next's joystick system emulates
- [Clone Joysticks](../clones/clone_joysticks.md) — the single-standard ecosystem the Next is a superset of

---

## References

- **Official Next documentation** ([specnext.com](https://www.specnext.com/tbblue-io-port-system/)) — canonical NextReg and port reference
- **ZX Spectrum Next community site** ([zxnext.io](https://www.zxnext.io/)) — tutorials, software library, community forums
- [TBBlue I/O Port System documentation](https://specnext.org/) — the NextReg register table maintained by the development team
- **NextRegister Reference** (community-maintained PDF) — full bit layout of every NextReg
- **NextZXOS source** ([GitHub](https://github.com/z00m128/NextZXOS)) — open-source firmware
- **sjasmplus assembler** ([GitHub: z00m128/sjasmplus](https://github.com/z00m128/sjasmplus)) — canonical Next assembler with examples in `examples/l2_*.asm`, `examples/copper_*.asm`, `examples/dma_*.asm`, `examples/tilemap*.asm`
- **"ZX Spectrum Next Assembly Programming"** (D. R. M. Gomes and various community tutorials at speccy.xyz/next) — beginner-friendly programming guides
- [Zilog Z80 DMA Technical Manual](https://www.zilog.com/docs/z80/ps0179.pdf) — the canonical Z80 DMA reference (the Next DMA is a clone)
- **The Amiga Copper Hardware Reference** (Commodore, 1985) — the original inspiration for the Next's copper; useful conceptual background
- **Pin Solutions store** (pinsolutions.co.uk) — current Next hardware vendor (Issue 4)
- **CSpect emulator** ([cspect.org](https://cspect.org)) — reference emulator with debug views for sprites, copper, and DMA
