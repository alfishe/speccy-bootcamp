[← Home](../../README.md) · [New Gen Hardware](README.md) · [ZX Spectrum Next](zx_next.md)

# ZX Spectrum Next — The Copper Coprocessor

The ZX Spectrum Next's **copper** is a small programmable coprocessor that runs in parallel with the CPU and writes to NextReg registers at precisely-defined scanline positions. Named by analogy to the Amiga's copper (which performs the same role on the Amiga chipset), the Next's copper is the key to **per-scanline video effects** without cycle-exact CPU code: raster palette changes, mid-frame mode switches (Layer 2 → tilemap, sprites appear at line 100), horizontal splits, and per-scanline scroll offsets.

This article is the **programmer's reference**: the copper instruction set, the upload protocol, the timing constraints, and typical effect patterns. For the platform overview, see [zx_next.md](zx_next.md). For related effects-driven features, see [Layer 2](zx_next_layer2.md), [tilemap](zx_next_tilemap.md), and [sprites](zx_next_sprites.md).

---

## What the Copper Is — and Is Not

The copper is a **write-only register coprocessor**:

| Property | Value |
|---|---|
| **Programming model** | A flat list of instructions, executed in order |
| **Instruction set** | 3 opcodes: `WAIT`, `MOVE`, `STOP` (and `DISABLE`) |
| **Operating mode** | Runs in parallel with the CPU — does not block CPU execution |
| **Memory access** | **Cannot read main RAM** — only writes to NextReg registers |
| **Timing reference** | Tied to the video frame — `WAIT line, hpos` waits for a specific scanline + horizontal position |
| **Instruction rate** | One copper instruction per scanline (approximately — see timing notes below) |
| **List storage** | Internal FPGA RAM — written via two-port I/O protocol |

The copper is **not** a general-purpose second processor. It cannot read RAM, cannot call subroutines, cannot branch — it is a simple state machine that walks a list of `WAIT` + `MOVE` pairs. What it gives you is **synchronization with the raster beam**, which the CPU alone cannot do reliably without dedicated cycle-counted loops.

---

## The Three Copper Instructions

### WAIT — Wait for Scanline Position

```
WAIT line, hpos
```

Pauses the copper until the raster beam reaches scanline `line` (0–255, with bit 8 extending to 0–311) at horizontal position `hpos` (0–223, in units of ~8 pixels). After the WAIT completes, the next MOVE executes.

`WAIT` is the synchronization primitive — it lets the copper time its writes relative to the visible screen. A typical pattern is `WAIT 100, 0` followed by `MOVE` to a palette register, achieving "change palette starting at line 100".

### MOVE — Write to a NextReg

```
MOVE reg, value
```

Writes `value` (8-bit) to NextReg `reg`. After the MOVE, the copper advances to the next instruction. MOVE takes one scanline to complete — you cannot issue two MOVEs in the same scanline.

### STOP / DISABLE — End of List

```
STOP
```

Halts the copper. No further instructions execute until the copper is restarted. `DISABLE` is similar but also turns off the copper (until re-enabled via NextReg). The end of a copper list is conventionally marked with `STOP`.

### Instruction Encoding

Each copper instruction is encoded as **2 bytes** (a 16-bit word). The two ports that accept copper instructions are:

| Port | Function |
|---|---|
| `#60` | Write the **low byte** of the next copper instruction |
| `#61` | Write the **high byte** of the next copper instruction |

After the high byte is written, the copper appends the 2-byte instruction to its internal list. The list is built sequentially; you cannot write to an arbitrary offset without first resetting the list (via NextReg `0x60`/`0x61`).

The instruction encodings:

| Opcode | Byte 1 (low) | Byte 2 (high) | Encoding |
|---|---|---|---|
| `WAIT` | `hpos` (0–223) | `0xxxxxxx` + bit 7 = WAIT opcode | High byte bit 7 = 0 marks WAIT; lower bits = line |
| `MOVE` | `value` | `1xxxxxxx` + bits 6–0 = reg number | High byte bit 7 = 1 marks MOVE; lower 7 bits = reg |
| `STOP` | `0x00` (any) | `0xFE` or specific stop marker | (firmware-dependent — check Next docs) |
| `DISABLE` | `0x00` | `0xFF` | (firmware-dependent) |

The exact encoding has minor variations across firmware revisions; the [official TBBlue copper reference](https://www.specnext.com/tbblue-io-port-system/) is the canonical source.

---

## Uploading a Copper List

A copper list is built by writing pairs of bytes to ports `#60` and `#61`:

```z80
; =====================================================================
; upload_copper_list: Copy a copper list to the copper's internal RAM
; Input: HL = pointer to copper list, B = byte count (must be even)
; =====================================================================
upload_copper_list:
        ; 1. Reset the copper's write pointer
        ld      bc, #243B
        ld      a, #61                ; NextReg 0x61 = Copper reset (in some firmware)
        out     (c), a
        ld      b, >#253B
        xor     a                     ; value 0 = reset
        out     (c), a
        
        ; 2. Write the list, alternating low/high bytes
.loop:
        ld      a, b
        or      a
        ret     z                     ; done when B = 0
        
        ; Write low byte to #60
        ld      c, >#60               ; BC = #xx60
        ld      a, (hl)
        out     (c), a
        inc     hl
        ; Write high byte to #61
        ld      c, >#61
        ld      a, (hl)
        out     (c), a
        inc     hl
        
        dec     b
        dec     b
        jr      .loop
```

Once the list is uploaded, you start the copper with a write to NextReg `0x61` bit 0 (or similar — exact bit depends on firmware).

---

## Copper Timing Constraints

The copper's instruction rate is the most important constraint:

| Constraint | Value |
|---|---|
| **Instructions per scanline** | **1** (one MOVE per scanline) |
| **WAIT resolution** | 1 scanline (vertical), ~8 pixels (horizontal) |
| **Total list size** | Limited by FPGA RAM (typically ~2 KB = ~1024 instructions) |
| **Wraparound** | At the end of the frame (after line 311), the copper restarts from the top of its list |

The "one MOVE per scanline" rule is the copper's defining limit. To change **N** registers at the same scanline, you must spread the writes across **N consecutive scanlines**. For a palette swap of 256 entries, this means the swap takes 256 scanlines — most of the visible frame.

> [!TIP]
> The horizontal `WAIT` position lets you fit **two** MOVEs per scanline if they target different NextRegs and are spaced at different hpos values. This is rarely used in practice — most copper effects use vertical-only timing.

---

## Common Copper Effects

### 1. Raster Bars (Copper Bars)

The classic Amiga demo effect: change the border color every scanline to produce horizontal color bars.

```
WAIT 0, 0      ; wait for line 0
MOVE 0x14, 1   ; border color = 1 (blue)
WAIT 1, 0
MOVE 0x14, 2   ; line 1: border = 2 (red)
WAIT 2, 0
MOVE 0x14, 3   ; line 2: border = 3 (magenta)
WAIT 3, 0
MOVE 0x14, 5   ; line 3: border = 5 (cyan)
...
```

This produces 4 colored horizontal stripes. A full-frame raster bar typically has ~192 WAIT/MOVE pairs (one per visible scanline).

### 2. Mid-Frame Mode Switch

Switch from Layer 2 to tilemap (or vice versa) at a specific scanline — useful for a high-resolution status bar above a Layer 2 playfield.

```
WAIT 0, 0
MOVE 0x15, 0x01    ; enable only Layer 2 (bit 0)
WAIT 192, 0        ; wait until line 192 (just past Layer 2 area)
MOVE 0x15, 0x02    ; enable only tilemap (bit 1)
STOP
```

After this copper list runs, lines 0–191 display Layer 2, and lines 192+ display the tilemap. The CPU does nothing — the copper handles the switch in parallel.

### 3. Per-Scanline Palette Swap

Animate the palette across the frame for a "heat haze" or "water" effect:

```
WAIT 0, 0
MOVE 0x40, 16     ; select palette entry 16
MOVE 0x41, 200    ; set entry 16 to value 200
WAIT 1, 0
MOVE 0x40, 16
MOVE 0x41, 201    ; entry 16 = 201 on line 1
...
```

(Each palette change requires 2 MOVEs — select index, then write value — so it takes 2 scanlines per palette entry. For larger palette animations, use the copper to drive only the **most visible** entries and let the rest stay static.)

### 4. Horizontal Split (Sprite Multiplexing)

Use the copper to swap sprite slots mid-frame, doubling the effective sprite count by re-using the same slots for different objects on different screen halves:

```
WAIT 0, 0
MOVE 0x50, 0x00    ; (config sprites for top half — sprites 0-7 = enemies)
WAIT 128, 0        ; wait to middle of screen
MOVE 0x50, 0x01    ; (config sprites for bottom half — sprites 0-7 = bullets)
STOP
```

This is the standard technique for fitting more than 64 sprites in a single frame.

---

## Copper NextRegs Summary

| Reg | Name | Function |
|---|---|---|
| `0x60` | Copper control | Bit 0: run/stop; bit 1: reset list pointer; bit 2: copper enable |
| `0x61` | Copper list pointer high | Used in some firmware revisions |
| `0x62` | Copper list pointer low | Used in some firmware revisions |
| Ports `#60`/`#61` | Copper data write | Sequential writes build the copper list |

---

## Copper vs CPU Raster Effects

On the original 48K, per-scanline effects required **cycle-counted CPU loops** — the programmer wrote an `OUT (c), r` instruction, then carefully inserted `NOP`s to consume exactly the right number of T-states, then another `OUT`, and so on. This is the classic [multicolor technique](../../07_demoscene/multicolor_techniques.md), and it produces beautiful results — but it consumes the entire CPU for the duration of the visible frame.

| Criterion | CPU multicolor | Copper |
|---|---|---|
| **CPU cost** | 100% during visible lines | **0%** |
| **Effects possible** | Per-pixel attribute changes (8×1 color cells) | Per-scanline register changes |
| **Resolution** | Pixel-exact | ~8-pixel horizontal |
| **Register targets** | Screen RAM, attribute RAM | Any NextReg |
| **Complexity** | High (cycle counting, contention handling) | Low (declarative list) |
| **Combinability** | Yes — can run alongside copper | Yes — runs alongside CPU |

The copper and CPU multicolor are **complementary** — use the copper for register writes (palettes, mode switches, scroll offsets) and reserve CPU multicolor for screen-RAM writes (8×1 attribute changes that the copper cannot do).

---

## Putting It Together — Animated Copper Bars

```z80
; =====================================================================
; copper_bars.asm — Animated raster bars via copper
; =====================================================================
        ; 1. Build a copper list with 192 WAIT/MOVE pairs
        ld      hl, copper_list
        ld      de, copper_list_target
        ld      bc, 192 * 4           ; 192 entries × 4 bytes (WAIT + MOVE)
        ldir
        
        ; 2. Upload the list to the copper
        ld      hl, copper_list_target
        ld      b, 192 * 4
        call    upload_copper_list
        
        ; 3. Start the copper
        ld      bc, #243B
        ld      a, #60
        out     (c), a
        ld      b, >#253B
        ld      a, %00000011          ; run + enable
        out     (c), a
        
        ; 4. Main loop: animate the bar colors each frame
.animate:
        call    wait_vblank
        call    update_bar_colors     ; modify palette values in copper list
        call    upload_copper_list    ; re-upload the modified list
        jr      .animate

copper_list:
        ; 192 WAIT/MOVE pairs, each 4 bytes:
        ;   WAIT line, 0
        ;   MOVE 0x14, color
        ; Generated programmatically at startup
        defs 192 * 4
```

This produces a set of horizontal color bars that animate over time — all driven by the copper, with the CPU only modifying the bar colors at vblank.

---

## Cross-References

- [ZX Spectrum Next](zx_next.md) — platform overview, layer stack
- [Layer 2](zx_next_layer2.md) — copper can swap Layer 2 banks mid-frame
- [Sprites](zx_next_sprites.md) — copper enables sprite multiplexing (more than 64 sprites/frame)
- [Tilemap](zx_next_tilemap.md) — copper can swap tilemap content mid-frame for parallax
- [DMA](zx_next_dma.md) — alternative high-speed data mover (memory-to-memory)
- [Next video frame](../../05_development/05_display_and_timing/video_frame_next.md) — copper timing relative to the raster
- [Multicolor techniques](../../07_demoscene/multicolor_techniques.md) — the CPU-side technique that copper complements
- [Floating bus](../../05_development/05_display_and_timing/floating_bus.md) — alternative raster-sync method (CPU-side)

---

## References

- **TBBlue I/O Port System — Copper** ([specnext.com](https://www.specnext.com/tbblue-io-port-system/)) — canonical copper port and NextReg reference
- **The Amiga Copper Hardware Reference** (Commodore, 1985) — the original inspiration for the Next's copper; useful conceptual background
- **sjasmplus copper examples** ([GitHub](https://github.com/z00m128/sjasmplus)) — sample copper programs in the `examples/copper_*.asm` files
- **CSpect emulator** — copper implementation, with debug views for inspecting the running list
- **"ZX Spectrum Next Assembly Programming"** — copper tutorial with full raster-bar example
- **Demo scene copper tutorials** (specnext.com forums) — community-authored advanced copper techniques
