[← Home](../../README.md) · [Graphics](README.md)

# ZX Spectrum Next Graphics — Programmer's Perspective

The ZX Spectrum Next (2017–2020) changes the game-programming landscape more fundamentally than any other platform in this section. Every constraint that shaped 1980s Spectrum development — non-linear screen layout, 8×8 attribute clash, no hardware sprites, no hardware scrolling, frame budgets dominated by block copies — is lifted or relaxed by the Next's FPGA hardware. The result is a machine where the techniques in [screen_access.md](screen_access.md), [sprites_and_masking.md](sprites_and_masking.md), [scrolling_and_buffering.md](scrolling_and_buffering.md), and [multicolor_engines.md](multicolor_engines.md) become optional rather than mandatory.

This article is the **game-programmer's introduction** to the Next's graphics hardware. It does not duplicate the hardware reference — for register maps and full specifications, see [zx_next.md](../../02_hardware/newgen/zx_next.md) (hardware), [video_frame_next.md](../05_display_and_timing/video_frame_next.md) (timing), and [memory_and_io_next.md](../03_memory_and_io/memory_and_io_next.md) (memory map). Here, we focus on **what to use when**, with code patterns and decision matrices.

> [!NOTE]
> This article assumes you have read at least [screen_access.md](screen_access.md) and [sprites_and_masking.md](sprites_and_masking.md). The Next's hardware features are best understood as answers to specific problems in those articles — without the problems, the answers do not make sense.

---

## What the Next Changes

The single biggest change is that the Next ships with a **layer stack** — multiple independent video layers, each with its own memory and capabilities, composited by the FPGA in real time with zero CPU cost. The classic Spectrum has one layer (the ULA screen). The Next has six:

| # | Layer | Resolution | Colors | Use case |
|---|---|---|---|---|
| 1 | **ULA screen** | 256×192 | 8×2 attribute | Backward compatibility; legacy games |
| 2 | **LoRes** | 320×192 | 8×8 attribute | Higher horizontal resolution for ULA-style games |
| 3 | **Layer 2** | 256×192 or 320×256 | **256 from 24-bit RGB** | The default target for new games |
| 4 | **Tilemap** | 40×32 or 80×32 tiles | 256 from palette | Hardware scrolling, level maps |
| 5 | **Hardware sprites** | 16×16, up to 64 per scanline | 256 from palette | The replacement for SP1 / pre-shifted sprites |
| 6 | **Border** | Frame border | 256 from palette | Cosmetic |

Each layer can be enabled, disabled, and reordered. A typical Next game enables Layer 2 (background art) + hardware sprites (player, enemies, projectiles) + border (cosmetic), and leaves the others off. A Next port of a classic 128K game might enable only the ULA layer, running the original code unchanged.

### Other Next advantages for graphics

- **CPU at 3.5 / 7 / 14 / 28 MHz** — selectable at runtime. A 28 MHz CPU is 8× faster than the original, making software rendering cheap enough that Layer 2 can be driven entirely in software if needed.
- **Hardware multiply** — the Z80N CPU adds `MUL D,E` (16-bit result in DE), eliminating the table-driven multiply overhead that dominates 3D math on stock Z80s.
- **Copper coprocessor** — a small programmable unit that writes to NextRegs at specific scanlines, eliminating the need for raster-synchronized ISRs (the entire foundation of BIFROST*, NIRVANA+, and demoscene multicolor work).
- **Hardware DMA** — block memory transfers without CPU intervention, ideal for double-buffering Layer 2.
- **2 MB RAM** — eliminates the memory pressure that shaped 1980s game architectures.

The result: a Next game can do at 50 Hz what a 48K game struggled to do at 4 Hz, and the programmer does not need to fight the hardware to achieve it.

---

## Layer 2 Programming

**Layer 2** is the default graphics target for new Next software. It is a 256×192 pixel framebuffer with **256 colors per pixel** (from a 24-bit RGB palette), no attribute grid, no color clash, and a linear memory layout. Writing to Layer 2 is as simple as writing to RAM.

### Memory layout

Layer 2 framebuffer memory is **48 KB** (256 × 192 = 49,152 bytes, rounded to a convenient bank size). It is exposed to the CPU as **three 16 KB banks** paged into the MMU's slot 0–2 (addresses `#0000`–`#BFFF`):

```
MMU slot 0  (#0000-#3FFF)  →  Layer 2 bank 0  (top third of screen, y=0..63)
MMU slot 1  (#4000-#7FFF)  →  Layer 2 bank 1  (middle third, y=64..127)
MMU slot 2  (#8000-#BFFF)  →  Layer 2 bank 2  (bottom third, y=128..191)
```

The active bank is selected via NextReg `#12` (**Layer 2 RAM bank**). Within each 16 KB bank, pixels are stored in a **linear layout**: address `#0000` is pixel (0, 0), `#0001` is pixel (1, 0), ..., `#00FF` is pixel (255, 0), `#0100` is pixel (0, 1), and so on. This is in stark contrast to the ULA's non-linear layout (see [screen_layout.md](../03_memory_and_io/screen_layout.md)).

```z80
; Set Layer 2 bank 0 (top third)
select_layer2_bank_0:
        NEXTREG #12, 8         ; Layer 2 bank 0 is RAM bank 8
        RET

; Write a pixel at (x, y) — both byte-aligned coordinates
; A = color index, D = x (0..255), E = y (0..63 within bank)
put_pixel_layer2:
        ; First select the right bank based on y
        LD   A,E
        CP   64
        JR   C,.bank0
        CP   128
        JR   C,.bank1
.bank2
        NEXTREG #12, 10
        SUB  128               ; y -= 128 within bank
        JR   .write
.bank1
        NEXTREG #12, 9
        SUB  64                ; y -= 64 within bank
        JR   .write
.bank0
        NEXTREG #12, 8
.write
        ; Compute address = y * 256 + x
        LD   L,D
        LD   H,A               ; HL = y * 256 + x (linear layout!)
        LD   (HL),<color>      ; write the color
        RET
```

The **linear layout** is the key win. Filling a rectangle, drawing a line, blitting a sprite — every 2D operation becomes simpler and faster because there is no `(high three bits) << 8 | (mid three bits) << 3 | (low three bits)` address calculation, no attribute file to keep in sync, and no INK/PAPER assignment to worry about.

### Enabling Layer 2

Layer 2 is enabled via NextReg `#15` (layer control):

```z80
enable_layer2_only:
        NEXTREG #15, %00000001  ; bit 0 = enable Layer 2, disable others
        RET
```

Once enabled, Layer 2 overlays the ULA screen. By default, Layer 2 has priority — the ULA screen is hidden behind it. Setting bit 4 of NextReg `#15` flips the priority so the ULA shows over Layer 2, which is useful for status bars (ULA-rendered text over a Layer 2 playfield).

### Palette setup

Layer 2 has its own **256-entry palette**, initialized at boot to a default 256-color RGB set. To customize the palette, write to NextReg `#40` (palette write index) followed by NextReg `#41` (palette data) — three writes per entry (R, G, B):

```z80
; Set palette entry 5 to bright red (255, 0, 0)
set_palette_red:
        NEXTREG #40, 5         ; palette index 5
        NEXTREG #41, 255       ; R
        NEXTREG #41, 0         ; G
        NEXTREG #41, 0         ; B
        RET
```

The palette can also be loaded from a binary file at startup using NextZXOS's `LOAD` command, which is the typical approach for game art.

### Double buffering

Layer 2 supports double buffering via the **shadow Layer 2** mechanism. The Next has RAM banks 8–10 for the visible Layer 2 and **banks 11–13** for a shadow Layer 2 that the CPU can draw to without affecting the visible screen. Once a frame is complete, a single NextReg write flips the two:

```z80
; Frame loop with double buffering
frame_loop:
        ; ... draw to shadow Layer 2 (banks 11-13) ...
        ; Wait for VBLANK
        HALT
        ; Flip shadow and visible
        LD   A,(current_shadow_bit)
        XOR  1
        LD   (current_shadow_bit),A
        NEXTREG #69, A         ; Layer 2 shadow bank select
        JR   frame_loop
```

This eliminates the flicker that haunted 48K Spectrum development. Combined with the linear layout and zero attribute constraints, Layer 2 is roughly **comparable to the Amiga's bitplane graphics** in terms of programmer effort — a profound change from the stock Spectrum.

---

## Hardware Sprites

The Next's hardware sprites are the answer to every problem documented in [sprites_and_masking.md](sprites_and_masking.md). Up to **64 sprites per scanline** (or 80 with limitations), each **16×16 pixels** in 256 colors, composited by the FPGA in real time. No pre-shifting, no masking, no sprite pools, no frame budgets dominated by draw cost.

### Sprite capabilities

- **Size**: 16×16 pixels (configurable to 8×8 or 32×16 with limitations)
- **Colors**: 256 per pixel, from the Layer 2 palette (shared with the background)
- **Transparency**: one selectable palette index acts as transparent (typically index 0)
- **Rotation/scaling**: optional per-sprite, via the sprite clip register
- **Mirroring**: per-sprite horizontal/vertical flip
- **Count**: up to 64 visible per scanline (the 65th and beyond are clipped by scanline by the hardware)
- **Priority**: per-sprite, with later-defined sprites drawing on top

### Sprite data format

Each sprite is stored as **256 bytes** of pixel data (16 × 16 = 256), one byte per pixel, with the byte value being a palette index. Byte 0 is the top-left pixel; byte 1 is the pixel to its right; byte 16 is the first pixel of the second row; and so on. This is much simpler than the masked-interleaved format used by stock Spectrum sprite engines.

Sprite data lives in a dedicated **sprite bank** in the Next's RAM (typically bank 9 or higher). The bank is paged into the CPU's address space for writing at setup time, then the hardware reads from it autonomously during display.

### Programming interface

Sprites are programmed via a small set of I/O ports:

- **`#303B`** — sprite setup port (selects which sprite slot to configure)
- **`#57`** — sprite data port (writes pixel data, one byte per write, 256 writes per sprite)
- **`#55`** — sprite attribute port (writes the per-frame sprite attributes: x, y, palette, mirror, etc.)

The typical sprite setup at game initialization:

```z80
; Upload a 16×16 sprite to slot 5
upload_sprite_5:
        ; Select sprite slot 5 for writing
        LD   BC,#303B
        LD   A,5
        OUT  (C),A
        ; Set the sprite's pattern pointer to our data's RAM address
        ; ... (depends on memory layout) ...
        ; Now write 256 bytes of pixel data to port #57
        LD   HL,sprite_data_5
        LD   B,0
        LD   C,#57
.upload_loop
        OUTI                     ; (C) <- (HL); HL++; B--
        JR   NZ,.upload_loop     ; loop 256 times (B counts from 0 = 256)
        ; ... second half of the 256 bytes ...
        RET
```

And the per-frame sprite attribute update (position, mirror, palette):

```z80
; Position sprite 5 at screen (D, E), no mirror, palette 0
update_sprite_5:
        LD   BC,#303B
        LD   A,5
        OUT  (C),A               ; select sprite slot 5
        ; Write attribute bytes (format: x_lo, x_hi_bits, y, misc)
        LD   BC,#55
        LD   A,D                 ; x low byte
        OUT  (C),A
        LD   A,0                 ; x high bits (and other flags)
        OUT  (C),A
        LD   A,E                 ; y
        OUT  (C),A
        LD   A,%00000000         ; mirror=0, palette=0, etc.
        OUT  (C),A
        RET
```

### What this eliminates

Compared to stock Spectrum sprite engines, hardware sprites eliminate:

- **Pre-shifted sprite storage** (8× memory multiplier) — sprites can be placed at any pixel position without shifting
- **MASK compositing** (the most expensive blend mode) — transparency is handled by the FPGA
- **Three-screen buffered drawing** — sprites composite directly onto the visible Layer 2
- **Sprite pools and frame budgets** — 64 sprites per scanline is a hardware limit, not a CPU one
- **Color clash workarounds** (per-room colors, INK-only sprites, etc.) — irrelevant with 256-color sprites

A Next game with 32 sprites moving freely at 50 Hz takes essentially **zero CPU time for sprite rendering** — only the position-update code (four `OUT` instructions per sprite, ~50 T-states) is needed per frame.

### When to use software sprites instead

Despite hardware sprites being strictly better in capability, software sprites (drawing to Layer 2 from the CPU) remain useful for:

- **Sprites larger than 16×16** — a 32×32 sprite can be composed of 4 hardware sprites, but a software sprite has no size limit
- **Sprites with non-standard effects** — per-pixel palette cycling, soft-edged alpha, palette swaps at scanline boundaries
- **Sprites that need to write to the background** — hardware sprites always composite *over* Layer 2; software sprites can write *into* Layer 2 and be overwritten by later draws

For most games, hardware sprites cover 90% of cases.

---

## Tilemap

The Next's **tilemap** layer is a hardware-accelerated tile grid, similar to the tile engines on the NES, SNES, or C64. It is the natural choice for level-map rendering: side-scrollers, top-down adventures, RPG world maps.

### Capabilities

- **Tile size**: 8×8 pixels or 16×16 pixels (selectable)
- **Tilemap dimensions**: 40×32 tiles (320×256 at 8×8) or 80×32 tiles (640×256 at 8×8, half-resolution)
- **Tile count**: 256 tiles in the default palette-mapped mode, more with extended modes
- **Colors**: 256 per pixel from the palette
- **Hardware scrolling**: per-pixel X/Y offset via two NextReg writes — the entire tilemap shifts without CPU work
- **Tile priority**: per-tile, allowing foreground/background distinction

### Tile data format

Each tile is **64 bytes** (8×8 pixels × 1 byte per pixel). The tilemap itself is a 40×32 array of tile indices (1,280 bytes), one byte per cell. To draw a level map, the programmer fills the tile index array with the appropriate tile numbers; the hardware reads from this array and the tile data autonomously during display.

### Programming the tilemap

```z80
; Enable tilemap (and disable Layer 2 for this example)
enable_tilemap:
        NEXTREG #15, %00000010   ; bit 1 = enable tilemap
        ; Select tilemap mode: 8×8 tiles, 40×32 grid
        NEXTREG #6C, %00000000   ; 8×8 tile, 40-col mode
        ; Set tilemap base address (in 16 KB banks)
        NEXTREG #6E, 12          ; tilemap definitions in bank 12
        NEXTREG #6F, 13          ; tile data in bank 13
        RET
```

Per-frame hardware scrolling:

```z80
; Scroll tilemap to (D, E) pixel offset
scroll_tilemap:
        NEXTREG #30, D           ; X scroll low byte
        NEXTREG #31, 0           ; X scroll high byte (9-bit value)
        NEXTREG #32, E           ; Y scroll byte
        RET
```

That is the entire scrolling implementation. No stack-push copy, no two-frame cycle, no 25 Hz limit — just two register writes per frame, and the playfield scrolls at 50 Hz.

### When to use tilemap vs Layer 2

| Use case | Recommended layer |
|---|---|
| Side-scroller with repeating tile patterns | **Tilemap** (hardware scroll) |
| Side-scroller with unique hand-drawn backgrounds | **Layer 2** (freeform art) |
| Top-down RPG with grid-based map | **Tilemap** |
| Pinball or single-screen puzzle | **Layer 2** |
| Status bar at top of screen | **ULA** or **Layer 2** with priority bit |
| Procedurally-generated map | **Tilemap** (just rewrite the tile index array) |

The tilemap is the right choice when the level can be expressed as a grid of tiles. Layer 2 is the right choice when each screen is a unique composition.

---

## The Copper Coprocessor

The **copper** is a small programmable coprocessor that writes to NextRegs at specific scanlines. It is the Next's answer to raster-synchronized ISRs (the entire category of techniques covered in [race_the_beam.md](../04_interrupts/race_the_beam.md) and [multicolor_engines.md](multicolor_engines.md)).

### Why the copper matters

On stock hardware, changing a graphics register mid-frame requires a cycle-exact ISR — the CPU must enter an IM2 handler at a specific T-state, count cycles until the beam reaches the target scanline, and write the register value at the exact moment. This is what BIFROST*, NIRVANA+, and demoscene multicolor effects do. It costs the CPU heavily.

The copper does the same job with **zero CPU cost**. The programmer writes a small list of `(scanline, register, value)` tuples to a copper buffer; the FPGA walks the list during display and writes each NextReg at the specified scanline. The CPU is free to do game work.

### Copper instructions

The copper has three instructions:

- **`MOVE`** — write a value to a NextReg at the current scanline
- **`WAIT`** — wait until a specific scanline and T-state before continuing
- **`STOP`** — end the copper program

A copper program is a sequence of these instructions stored in a dedicated copper DMA buffer. The instructions are encoded as 16-bit words:

```
MOVE reg, value:    2 words: [reg | flags, value]
WAIT line, tstate:  2 words: [line | flags, tstate]
STOP:               1 word:  0xFFFF
```
### Example: copper-bar effect

The classic copper-bar effect (horizontal stripes of different colors in the border) becomes trivial:

```z80
; Build a copper program that sets border color every 16 scanlines
build_copper_bars:
        LD   HL,copper_buffer
        LD   B,19                ; 19 stripes (312 scanlines / 16)
        LD   C,0                ; starting scanline
.stripe_loop
        ; WAIT until scanline C
        LD   (HL),%10000000     ; WAIT instruction flag
        INC  HL
        LD   (HL),C             ; scanline
        INC  HL
        ; MOVE border color register (#14) to a stripe color
        LD   (HL),%00000000     ; MOVE instruction flag
        INC  HL
        LD   (HL),#14           ; NextReg #14 = border color
        INC  HL
        LD   (HL),stripe_colors-C
        ; ... advance C, B, etc. ...
        DJNZ .stripe_loop
        ; STOP
        LD   (HL),0xFF
        INC  HL
        LD   (HL),0xFF
        RET
```

With this loaded into the copper, the FPGA executes the program every frame, producing the copper-bar effect with **zero ongoing CPU cost**.

### What the copper enables

The copper makes per-scanline effects essentially free:

- **Copper bars** (horizontal stripes in the border)
- **Per-scanline Layer 2 bank switching** (different Layer 2 banks on different scanlines, effectively extending Layer 2 beyond 256 lines)
- **Per-scanline palette changes** (gradient skies, sunsets, plasma effects)
- **Split-screen** (different display modes in the top and bottom halves of the screen)
- **Raster-synchronized sprite counts** (more sprites in the playfield area, fewer in the status bar)

The copper does not eliminate the need for ISRs entirely — it cannot run game logic, only write NextRegs. But it takes over the workload that previously consumed 50% or more of the frame budget on stock hardware.

---

## Mixing Layers: Typical Game Architectures

The Next's flexibility means most games use a **combination** of layers rather than just one. Here are the typical architectures:

### Architecture 1: Layer 2 + hardware sprites

The default for action games. Layer 2 holds the background (drawn by the CPU each frame from a tile map or bitmap). Hardware sprites hold the player, enemies, and projectiles. The status bar is drawn directly into Layer 2 at the top of the screen.

This is the closest analog to a C64 or NES game on the Next.

### Architecture 2: Tilemap + hardware sprites

The default for side-scrollers. Tilemap holds the level map with hardware scrolling. Hardware sprites overlay the action. Layer 2 is unused (or used only for cutscenes).

This gives the smoothest-scrolling gameplay on the Next, because the tilemap scrolling is entirely hardware-driven.

### Architecture 3: Layer 2 only

Used for puzzle games, single-screen adventures, and games with hand-drawn backgrounds. The CPU redraws Layer 2 each frame, possibly using double buffering. No sprites, no tilemap.

This is the simplest architecture and the easiest to develop. The cost is that the CPU must handle every visual update.

### Architecture 4: ULA + Layer 2 status bar

Used for ports of classic Spectrum games that want a Next-enhanced status display. The ULA layer runs the original 48K/128K game code unchanged. Layer 2 (with priority bit set so ULA shows over it) provides a 256-color status bar that the original game did not have.

This is the lowest-effort way to enhance an existing game for the Next.

### Architecture 5: Everything

For showpiece games: Layer 2 background, tilemap foreground objects, hardware sprites for player and enemies, copper for raster effects, ULA for legacy text overlays. The Next's FPGA composites all of them at zero CPU cost — the only cost is the CPU work to draw into each layer's memory.

---

## Performance at Higher Clock Speeds

The Next's CPU can run at 3.5, 7, 14, or 28 MHz. The choice is made via NextReg `#07`:

```z80
set_cpu_28mhz:
        NEXTREG #07, %00000011   ; bits 0-1 = 3 for 28 MHz
        RET
```

At 28 MHz, every T-state is 8× faster than stock. A 50 Hz frame goes from ~71,000 T-states to **~559,000 T-states** of useful work. This is enough to do software rendering of Layer 2 at 50 Hz without hardware sprites, software 3D rasterization at 25 Hz, or any other technique that was out of reach on stock hardware.

The CPU speed can be switched at runtime — for example, run at 28 MHz during the visible part of the frame for rendering, drop to 3.5 MHz during VBLANK to maintain 48K-compatible timing for the music routine. (Music routines written for stock Spectrums assume 3.5 MHz; running them at 28 MHz produces incorrect pitches.)

---

## Common Pitfalls

### 1. Forgetting that Layer 2 requires bank switching

Layer 2 is not contiguous in CPU address space — it is three 16 KB banks. Code that draws across bank boundaries (e.g., a vertical line from y=50 to y=80) must switch banks at the boundary (y=64). Forgetting this produces either a crash (writing to wrong RAM) or visible artifacts (the line wraps to the wrong screen position).

The standard solution is to keep the per-pixel write routine bank-aware, as shown in [put_pixel_layer2](#memory-layout) above.

### 2. Sprite count overflow on scanlines

The Next supports 64 sprites per scanline. If 65+ sprites overlap on the same scanline, the hardware silently drops the extra ones — producing missing-sprite bugs that depend on the player's position. The fix is to either reduce sprite density (fewer simultaneous enemies) or to use sprite priority carefully (let the player sprite take priority over distant background sprites).

### 3. Palette conflicts between layers

Layer 2, tilemap, and hardware sprites all share the **same 256-entry palette**. A palette index that produces red on Layer 2 will also produce red on a hardware sprite using the same index. This means the art for all layers must agree on a single palette — typically designed as a shared asset at game-design time.

The 256-color shared palette is usually more than enough for a single game's art, but it requires discipline during asset creation.

### 4. Mixing CPU speeds with cycle-exact code

Code written for stock Spectrums (3.5 MHz) often uses cycle counts for timing — for example, an ISR that takes exactly 8,000 T-states. Running this code at 28 MHz makes the ISR complete in 1/8 the wall-clock time, breaking any timing assumption.

The fix is to either keep cycle-exact code at 3.5 MHz (using the runtime CPU speed switch), or to rewrite the timing logic to be wall-clock based (using the Next's line interrupt or a timer-based NextReg).

### 5. Assuming the copper can read state

The copper can only write NextRegs — it cannot read them, perform arithmetic, or branch conditionally. A copper program is a fixed sequence of writes; it cannot adapt to game state. Game-logic-driven effects (e.g., "flash the screen red when the player takes damage") must be implemented by the CPU rewriting the copper buffer, not by the copper itself.

### 6. Ignoring the ULA when running Next-native code

Even when a Next game uses only Layer 2 (ULA disabled), the ULA hardware is still reading from bank 5 every scanline. This causes memory contention on bank 5 accesses, slowing the CPU. The fix is to either keep game code out of bank 5, or to use NextReg `#03` to disable the ULA entirely (which also disables legacy 48K compatibility, but gives the CPU full uncontended access to all banks).

---

## Cross-References

- [zx_next.md](../../02_hardware/newgen/zx_next.md) — the complete hardware reference (register maps, layer stack, sprite and tilemap details)
- [video_frame_next.md](../05_display_and_timing/video_frame_next.md) — frame timing, CPU clock switching, contention model
- [memory_and_io_next.md](../03_memory_and_io/memory_and_io_next.md) — the 2 MB MMU and NextReg system
- [im2_advanced.md § ZX Spectrum Next Hardware IM2 Mode](../04_interrupts/im2_advanced.md) — the Next's per-scanline interrupt system
- [screen_access.md](screen_access.md) — the stock Spectrum techniques that Layer 2 replaces
- [sprites_and_masking.md](sprites_and_masking.md) — the stock sprite techniques that hardware sprites replace
- [multicolor_engines.md](multicolor_engines.md) — the stock multicolor techniques that the copper replaces
- [3d_graphics.md](3d_graphics.md) — how the Next's 28 MHz CPU and `MUL` instruction transform Spectrum 3D
- [nextzxos.md](../../04_operating_systems/nextzxos.md) — the Next's operating system and BASIC extensions

---

## References

- *ZX Spectrum Next Hardware Reference* — the official register-level documentation, [GitLab: SpectrumNext/ZX-Spectrum-Next](https://gitlab.com/SpectrumNext/ZX-Spectrum-Next-specs)
- *ZX Spectrum Next Assembly Programming* by D. R. R. S. Rello — community-maintained tutorial series
- *NextBASIC Programming Manual* — Garry Lancaster's official NextZXOS reference
- *specnext.dev* — community wiki with worked examples for Layer 2, sprites, tilemap, and copper
- *The Mojon Twins* game source code — open-source Next games showing typical architectures (Layer 2 + sprites, tilemap + sprites)
- *NextSprT* and *Sprite Editor* tools — community sprite editors producing Next-compatible data
- The [World of Spectrum](https://worldofspectrum.org/) forums — active Next development community
