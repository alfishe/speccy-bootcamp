[← Home](../../README.md) · [New Gen Hardware](README.md) · [ZX Spectrum Next](zx_next.md)

# ZX Spectrum Next — Layer 2 Framebuffer

The **Layer 2** framebuffer is the ZX Spectrum Next's most-impactful graphics upgrade. Where every prior Spectrum (including the original 48K, all clones, and even the Russian TS-Conf machines) was bound to the **attribute model** — 8×8 pixel cells with two colors per cell — Layer 2 gives the programmer a **true 256-color 8-bpp framebuffer**, addressable pixel-by-pixel with no attribute constraint at all.

For game developers, Layer 2 is what makes the Next feel like a 16-bit console: full-color backgrounds, pre-rendered title screens, digitized images, and even software 3D — all at 50 Hz, with no raster tricks and no CPU contention from the video circuit. This article is the **programmer's reference**: the bank-switching protocol, the palette, the resolution modes, the shadow layer, and the typical draw-loop pattern.

For the platform overview, see [zx_next.md](zx_next.md). For sibling layers, see [sprites](zx_next_sprites.md), [tilemap](zx_next_tilemap.md), and [copper](zx_next_copper.md).

---

## Layer 2 Specifications

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

---

## Bank Switching — The Three-Window Model

The 48 KB framebuffer for the standard 256×192 mode is divided into **three 16 KB windows**:

| Window | Lines covered | NextReg `0x12/0x13` (offsets) |
|---|---|---|
| **Window 0** | Lines 0–63 | Y offset 0–63 |
| **Window 1** | Lines 64–127 | Y offset 0–63 |
| **Window 2** | Lines 128–191 | Y offset 0–63 |

To write a pixel, you select the appropriate window by writing the window number to NextReg `0x12` (X offset, normally 0) and NextReg `0x13` (Y offset, the window's start line). Once the window is selected, the 16 KB at `#0000–#3FFF` becomes a linear bitmap of that 64-line region — pixel `(x, y)` within the window is at byte `y × 256 + x` (since each line is 256 bytes wide).

### The Banking Port — `#123B`

The simpler bank-switching mechanism is port `#123B`. Writing a value 0, 1, or 2 to `#123B` selects which **third** of the framebuffer is paged at `#0000–#3FFF`:

```z80
        ; Write the value 1 to port #123B to page framebuffer window 1
        ld  bc, #123B
        ld  a, 1
        out (c), a
        ; Now #0000-#3FFF is framebuffer lines 64-127
```

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
; plot_pixel: Set Layer 2 pixel at (D=E=x, L=y) to color A
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
        ; HL = (line * 256) + X — but line is in H already since H*256
        ; Actually H = line, L = X, so HL = line*256 + X. Perfect.
        
        ; 4. Write the pixel
        ld      a, (current_color)
        ld      (hl), a             ; store the 8-bit color index
        
        ; 5. Restore banking (optional — re-enable ROM/RAM at #0000)
        ; Not strictly required if you immediately set another pixel.
        ret
```

For high-speed drawing (e.g., filling the screen), keep banking active and iterate; for one-shot pixel access, restore banking to 3 (ROM) before returning.

---

## The 256-Color Palette

Layer 2 pixels are **palette indices** — each byte in the framebuffer is an index 0–255 into a 256-entry palette. The palette entries themselves are 24-bit RGB (8 bits red, 8 bits green, 8 bits blue) on the Next, but are commonly configured as **9-bit RGB** (3 bits per channel) for compatibility with the Next's other layers.

### Palette Programming

The palette is programmed through a **3-port protocol**:

| Port | Function |
|---|---|
| `#40` | Write the **palette index** to select (0–255) |
| `#41` | Write the **palette value** (the format depends on NextReg `0x4A` mode) |
| NextReg `0x4A` | Select palette write mode: `0` = 8-bit paletted, `1` = 9-bit RGB (3 writes), `2` = 16-bit RGB565 (2 writes), `3` = 24-bit RGB (3 writes) |

In **8-bit paletted mode** (NextReg `0x4A = 0`), each value written to `#41` is itself an index into a 256-entry fixed palette (this is the original 1980s-like mode, useful for fast gradient setup). In **9-bit RGB mode**, three writes to `#41` set the R, G, B channels (each 0–7).

Example — set palette entry 5 to bright red in 9-bit RGB mode:

```z80
        ; 1. Set palette mode to 9-bit RGB
        ld  bc, #243B
        ld  a, #4A
        out (c), a
        ld  b, >#253B
        ld  a, 1                   ; mode 1 = 9-bit RGB
        out (c), a
        
        ; 2. Select palette entry 5
        ld  bc, #40
        ld  a, 5
        out (c), a
        
        ; 3. Write R=7, G=0, B=0
        ld  bc, #41
        ld  a, 7                   ; R = max
        out (c), a
        xor a                      ; G = 0
        out (c), a
        xor a                      ; B = 0
        out (c), a
```

### Layer-Specific Palettes

Layer 2 shares its palette with the ULA, sprites, and tilemap by default. To give Layer 2 its own palette, you can use the **palette offset** feature (via the layer-priority NextReg) — Layer 2 can use palette entries 0–63 while sprites use 64–127, etc. This is detailed in the [NextReg reference](https://www.specnext.com/tbblue-io-port-system/).

---

## Extended Resolution — 320×256

The Next's **extended Layer 2 mode** increases the resolution from 256×192 to **320×256** — a 30% wider and 33% taller image. This mode is enabled via NextReg `0x16` (Layer 2 resolution):

| NextReg `0x16` value | Mode |
|---|---|
| `0` | Standard 256×192 |
| `1` | Extended 320×256 |

In 320×256 mode, the framebuffer grows from 48 KB to **80 KB**, requiring more bank switching. The `#123B` port still pages 16 KB chunks, but now there are 5 windows (80 KB ÷ 16 KB) instead of 3. The pixel address within each window changes from `(y * 256 + x)` to `(y * 320 + x)` since lines are now 320 bytes wide.

> [!TIP]
> 320×256 mode is excellent for **ports of Amiga/Atari ST games** that were originally designed for 320×200 — the 40 extra columns make text and HUDs fit naturally. The standard 256×192 mode is best for software that needs to remain visually compatible with the original Spectrum screen.

---

## The Shadow Layer 2 — Double Buffering

Layer 2 supports a **shadow framebuffer** — a hidden second 48 KB buffer that can be drawn to without being visible. This enables proper **double-buffering**: write to the shadow buffer during one frame, then swap visible/shadow at vblank to display the new frame with no tearing.

The shadow is controlled via NextReg `0x15` bit 4 — toggling this bit swaps the visible and shadow buffers. The `#123B` port selects which buffer is being **written to**; NextReg `0x15` selects which is being **displayed**.

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

For most games, double-buffering is overkill — Layer 2 has no raster-synchronized attribute fetch, so screen tearing is rare. But for animations that produce lots of redraw, double-buffering produces visibly smoother motion.

---

## Layer 2 NextRegs Summary

| Reg | Name | Function |
|---|---|---|
| `0x12` | Layer 2 offset X | Horizontal scroll offset (0–255) |
| `0x13` | Layer 2 offset Y | Vertical scroll offset (0–255) |
| `0x15` | Layer 2 enable / shadow | Bit 0 = enable, bit 4 = shadow toggle |
| `0x16` | Layer 2 resolution | 0 = 256×192, 1 = 320×256 |
| `0x1A` | Layer 2 RAM page | Direct select of which 16 KB bank to page (alternative to `#123B`) |
| `0x4A` | Palette write mode | 0/1/2/3 paletted/9-bit/16-bit/24-bit |

---

## LoRes and HiRes Modes

Beyond Layer 2's standard and extended resolutions, the Next has two additional modes that affect the framebuffer:

- **LoRes mode** (`NextReg 0x15` bit 3): A 320×192 mode with **8×8 attribute blocks** at double resolution — like the standard Spectrum display but at 4× the resolution. Useful for high-resolution ULA-style graphics.
- **HiRes mode** (`NextReg 0x08` bit 4): A 512×192 mode with **2 colors per 8×1 cell** — the Timex HiColor mode, original to the Sinclair TC2048 / Timex Sinclair 2068.

These are independent of Layer 2 — they affect how the ULA layer is rendered, not the Layer 2 framebuffer.

---

## Layer 2 vs Original Spectrum — What You Gain

| Capability | Original 48K | Next Layer 2 |
|---|---|---|
| **Colors per pixel** | 2 (per 8×8 cell) | **256** |
| **Frame buffer size** | 6.75 KB (6144 pixels + 768 attrs) | 48 KB (256×192×8 bpp) |
| **Pixel address** | Complex (line / 8 + (line % 8) × 32 + col) | **Linear** (window: line × 256 + col) |
| **CPU contention** | Yes (ULA steals cycles) | **None** (separate RAM) |
| **Attribute clash** | Yes (8×8 cells limit color placement) | **None** (every pixel has its own color) |
| **Scrolling** | Painful (re-render every shifted pixel) | **Easy** (write Y offset NextReg, hardware scrolls) |
| **Double buffering** | Impossible (only one screen RAM) | **Built-in** (shadow framebuffer) |
| **Pre-rendered art** | Limited (digitized images reduce to attribute-blocky) | **Lossless** (PNG-quality images at 256 colors) |

For game developers moving from classic Spectrum to the Next, Layer 2 is the single most impactful change — it eliminates the attribute clash problem that defined Spectrum graphics for 30 years.

---

## Typical Layer 2 Drawing Patterns

### Fast Full-Screen Fill

```z80
; Fill the entire Layer 2 with color A
fill_layer2:
        ld      b, 3                  ; 3 windows
        ld      c, 0                  ; start with window 0
.fill_window:
        push    bc
        ; Page the window
        ld      b, >#123B
        out     (c), c
        ; Fill 16384 bytes at #0000-#3FFF with A
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
        ; Restore ROM at low memory
        ld      bc, #123B
        ld      a, 3
        out     (c), a
        ret
```

At 28 MHz, this fills the entire 48 KB framebuffer in under 1 ms — fast enough to do multiple times per frame.

### Software Horizontal Scrolling

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

For pixel-perfect scroll that wraps around (e.g., a horizontally-scrolling shooter), maintain a virtual "world X" and use `(worldX mod 256)` for the offset. New pixel columns are written into the framebuffer at the position the offset will move out of next frame, achieving seamless wrap.

---

## Cross-References

- [ZX Spectrum Next](zx_next.md) — platform overview, layer stack
- [Sprites](zx_next_sprites.md) — drawn on top of Layer 2
- [Tilemap](zx_next_tilemap.md) — alternative/companion to Layer 2 for tiled backgrounds
- [Copper](zx_next_copper.md) — palette changes per scanline, mid-frame mode switches
- [DMA](zx_next_dma.md) — fast memory-to-framebuffer transfers
- [Next memory map and I/O ports](../../05_development/03_memory_and_io/memory_and_io_next.md) — full port decoding
- [Next video frame](../../05_development/05_display_and_timing/video_frame_next.md) — Layer 2 timing independence

---

## References

- **TBBlue I/O Port System — Layer 2** ([specnext.com](https://www.specnext.com/tbblue-io-port-system/)) — canonical Layer 2 port and NextReg reference
- **NextRegister Reference** — full bit layout of `0x12`/`0x13`/`0x15`/`0x16`
- **"ZX Spectrum Next Assembly Programming"** — Layer 2 tutorial with full code
- **sjasmplus Layer 2 examples** ([GitHub](https://github.com/z00m128/sjasmplus)) — sample programs in the `examples/l2_*.asm` files
- **CSpect emulator** — Layer 2 implementation, for development testing
- **NextBASIC Layer 2 commands** — `#L2`, `#L2 COPY`, documented in [NextZXOS](../../04_operating_systems/nextzxos.md)
