[← Home](../../README.md) · [New Gen Hardware](README.md) · [ZX Spectrum Next](zx_next.md)

# ZX Spectrum Next — Hardware Tilemap

The ZX Spectrum Next's **hardware tilemap** is a tile-based display layer — a 40×32 (or 80×32) grid of 8×8 pixel tiles, each independently selectable from a 256-entry pattern table, with its own per-tile attributes (palette offset, mirror, priority over Layer 2). For games with large scrolling backgrounds (platformers, RPGs, shooters), the tilemap is the most efficient way to fill the screen with detail at zero CPU cost — replacing both the ULA screen (whose 8×8 attribute blocks are too coarse) and Layer 2 (whose per-pixel cost is high for backgrounds).

This article is the **programmer's reference**: the tile/attribute layout in RAM, the pattern table, the scroll offset NextRegs, and the tile modes (40×32 with attributes vs 80×32 without). For the platform overview, see [zx_next.md](zx_next.md). For sibling layers, see [sprites](zx_next_sprites.md), [Layer 2](zx_next_layer2.md), and [copper](zx_next_copper.md).

---

## Tilemap Specifications

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

The tilemap pattern table is **separate** from main RAM — it occupies its own FPGA RAM region, accessed via NextRegs rather than directly addressable.

---

## Two Modes — 40×32 vs 80×32

The tilemap has two resolution modes, selected via NextReg `0x6E` (**Tilemap mode**):

| Mode | Resolution | Tile bytes | Per-tile attributes | Use case |
|---|---|---|---|---|
| **40×32** | 320×256 pixels | 2 bytes per tile (number + attr) | Yes (palette offset, mirror, priority) | Standard tile-based games |
| **80×32** | 640×256 pixels | 1 byte per tile (number only) | No | Text modes, ASCII art, double-width maps |

The 40×32 mode is the typical choice for games — it provides per-tile control over palette and orientation while remaining a comfortable resolution for 8×8 pixel art. The 80×32 mode is suited for text-heavy applications (terminals, editors, debug overlays) where each tile is one character cell.

> [!NOTE]
> In 80×32 mode, the pattern table is **still 256 entries of 8×8 pixels** — only the tilemap grid resolution doubles. A pattern depicting an `A` glyph in 80×32 mode renders as 8×8 pixels, giving 80 columns of 8-pixel-wide text across 640 pixels.

---

## Memory Layout — Tilemap RAM

The tilemap grid is stored in **dedicated RAM** inside the FPGA. Unlike Layer 2, you do not page this RAM into the Z80 address space — you write to it via a **two-port protocol** that auto-increments through addresses.

### Tilemap Write Ports

| Port | Function |
|---|---|
| NextReg `0x6E` | Mode select (40×32 with attrs vs 80×32 no attrs) — also enables 8-bit patterns |
| `#6B` | **Tilemap address select** (low byte) — write the address low byte here |
| NextReg `0x6F` | **Tilemap address select** (high byte) — write the address high byte |
| `#7B` (or `#40`-`#43` in some firmware) | **Tilemap data** — sequential writes go to consecutive tile addresses |

After setting the address via `#6B` and `0x6F`, sequential writes to `#7B` fill the tilemap. The internal pointer auto-increments after each byte. The tilemap is 2560 bytes (40×32×2 in 40×32 mode, or 80×32×1 in 80×32 mode), starting at address 0.

### Tilemap Address Space Layout

| Address range | Contents (40×32 mode) | Contents (80×32 mode) |
|---|---|---|
| `0x0000 – 0x04FF` (1280 bytes) | **Tilemap byte 0** for each tile (tile pattern number, 0–255) | **Tile numbers only** (80 columns × 32 rows = 2560 bytes — fills entire address space) |
| `0x0500 – 0x09FF` (1280 bytes) | **Tilemap byte 1** for each tile (attribute byte) | (not used — only tile numbers) |

The tilemap is **interleaved** in 40×32 mode — each tile occupies 2 bytes, the first being the pattern number and the second being the attribute. To write tile (x, y) with pattern P and attribute A:

```
address = (y * 40 + x) * 2
write P at address
write A at address + 1
```

Or in 80×32 mode:

```
address = y * 80 + x
write P at address
```

---

## The Pattern Table

The pattern table holds **256 tile images**, each 8×8 pixels. Each tile is 32 bytes (4-bit color: 32 pixels per tile, 4 bits per pixel) or 64 bytes (8-bit color: 64 pixels per tile, 8 bits per pixel). The pattern table size is therefore:

| Color depth | Bytes per tile | Total pattern table size |
|---|---|---|
| 4-bit (16 colors) | 32 bytes | 8 KB |
| 8-bit (256 colors) | 64 bytes | 16 KB |

The pattern table is uploaded via the same two-port protocol as the tilemap, but at a different address range (see the NextReg `0x6E` bit 2 for the address-select mode).

### Pattern Byte Layout

A 4-bit tile's 32 bytes are organized as 8 rows × 4 bytes-per-row (each row = 8 pixels × 4 bits = 32 bits = 4 bytes). The first 4 bytes are the top row of the tile, the next 4 bytes are the second row, etc.

```
Pattern layout (4-bit tile, 32 bytes):
  Bytes 0-3   → Row 0 (8 pixels, upper nibble = pixel 0, lower = pixel 1, etc.)
  Bytes 4-7   → Row 1
  Bytes 8-11  → Row 2
  ...
  Bytes 28-31 → Row 7
```

An 8-bit tile is the same layout but 8 bytes per row (one byte per pixel), giving 64 bytes per tile.

---

## Tile Attributes (40×32 Mode Only)

In 40×32 mode, each tile has an **attribute byte** alongside its pattern number. The attribute byte format:

| Bit | Function |
|---|---|
| 0–3 | **Palette offset** (0–15) — added to the pattern's palette index |
| 4 | Reserved |
| 5 | **X mirror** (flip the tile horizontally) |
| 6 | **Y mirror** (flip the tile vertically) |
| 7 | **Priority over Layer 2** — if set, the tile is drawn above Layer 2 instead of below |

The palette offset lets a single tile pattern render in **16 different color schemes** — useful for status icons, repeated floor tiles with seasonal variations, etc.

The X/Y mirror bits are essential for **pattern compression** — a single "tree" tile can render as itself, mirror-X (mirror of the tree), mirror-Y (upside-down tree), or both (rotated 180°). This is the standard tileset-compression technique used in NES / SNES / GBA games, and the Next provides it for free.

The priority bit (7) is the most powerful — it lets the tilemap have **holes** that show Layer 2 through them. Use this for "background + foreground" splits: most tiles are background (priority 0), but a few foreground tiles (priority 1) appear in front of Layer 2 sprites.

---

## Scrolling — X and Y Offsets

The tilemap's **scroll position** is set via NextRegs `0x30`–`0x33`:

| Reg | Name | Range |
|---|---|---|
| `0x30` | Tilemap offset X (low byte) | 0–255 |
| `0x31` | Tilemap offset X (high byte, only bits 0–0) | Extends X to 0–511 |
| `0x32` | Tilemap offset Y | 0–255 |
| `0x33` | Tilemap vertical offset (high byte) | (rarely used) |

The tilemap is **scrolled in hardware** — writing a new X or Y offset shifts the entire tilemap on the next frame, with zero CPU cost. The scroll position is in **pixels**, not tiles — so an X offset of 1 moves the tilemap right by 1 pixel, revealing 1 new pixel column from the next tile.

### Scrolling Strategy — The 40-Column Wrap

The tilemap grid is 40 columns wide, but the screen shows 40 columns only at offset 0. As you scroll right, the leftmost column scrolls off-screen and a new column would scroll on from the right — but the tilemap grid is only 40 columns wide. There is no "infinite" tilemap.

The standard solution is **wraparound scrolling**: when the X offset reaches 8 (one full tile), shift the tilemap contents in RAM and reset the offset to 0. This way the tilemap grid is always "refilled" with new content as the player moves:

```z80
; Horizontal scroll right by 1 pixel, with tile refill on tile boundary
scroll_right:
        ; 1. Increment the pixel offset
        ld      bc, #243B
        ld      a, #30
        out     (c), a
        ld      b, >#253B
        in      a, (c)
        inc     a
        out     (c), a
        cp      8
        ret     nz                    ; not at tile boundary yet — done
        
        ; 2. At tile boundary — refill the leftmost column with new content
        call    refill_leftmost_column
        
        ; 3. Reset X offset to 0 (or subtract 8) and shift tilemap RAM
        ld      bc, #243B
        ld      a, #30
        out     (c), a
        ld      b, >#253B
        xor     a
        out     (c), a
        call    shift_tilemap_left
        ret
```

Alternatively, the **copper** can be used to swap between two pre-built tilemaps mid-frame — useful for parallax scrolling (a foreground tilemap moves fast, a background tilemap moves slow).

---

## Tilemap NextRegs Summary

| Reg | Name | Function |
|---|---|---|
| `0x15` bit 1 | Tilemap enable | 0 = disable, 1 = enable |
| `0x6E` | Tilemap mode | Bit 0: 40×32 (0) vs 80×32 (1); bit 1: 8-bit patterns (vs 4-bit); bit 2: tilemap RAM location select |
| `0x6F` | Tilemap address high byte | Used with port `#6B` (low byte) to set write address |
| `0x30` | Tilemap offset X (low byte) | 0–255 |
| `0x31` | Tilemap offset X (high byte) | Bit 0 = X bit 8 |
| `0x32` | Tilemap offset Y | 0–255 |
| `0x33` | Tilemap clip window control | Reserved / clip window |
| `0x18`, `0x19` | Clip window | Restrict tilemap drawing area |

---

## Tilemap vs Layer 2 — When to Use Which

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

## Putting It Together — A Tile-Based Game

```z80
; =====================================================================
; tilemap_game_init: Initialize the tilemap for a platformer level
; =====================================================================
tilemap_game_init:
        ; 1. Enable tilemap (and disable Layer 2 for now)
        ld      bc, #243B
        ld      a, #15
        out     (c), a
        ld      b, >#253B
        ld      a, %00000010           ; enable tilemap only (bit 1)
        out     (c), a
        
        ; 2. Set 40×32 mode, 4-bit patterns
        ld      bc, #243B
        ld      a, #6E
        out     (c), a
        ld      b, >#253B
        xor     a                       ; 40×32, 4-bit patterns
        out     (c), a
        
        ; 3. Upload tile patterns to pattern table
        ld      hl, tile_patterns
        call    upload_tile_patterns    ; upload 256 patterns
        
        ; 4. Fill the tilemap grid with the level data
        ld      hl, level_data
        call    upload_tilemap          ; upload 40×32×2 bytes
        
        ; 5. Reset scroll to (0, 0)
        ld      bc, #243B
        ld      a, #30
        out     (c), a
        ld      b, >#253B
        xor     a
        out     (c), a                  ; X offset = 0
        ld      bc, #243B
        ld      a, #32
        out     (c), a
        ld      b, >#253B
        xor     a
        out     (c), a                  ; Y offset = 0
        ret
```

The tilemap is now visible, with the player free to use sprites on top via [zx_next_sprites.md](zx_next_sprites.md).

---

## Cross-References

- [ZX Spectrum Next](zx_next.md) — platform overview, layer stack
- [Layer 2](zx_next_layer2.md) — alternative background layer, free-form artwork
- [Sprites](zx_next_sprites.md) — drawn on top of the tilemap
- [Copper](zx_next_copper.md) — mid-frame palette swaps, parallax via tilemap swap
- [Next memory map and I/O ports](../../05_development/03_memory_and_io/memory_and_io_next.md) — full port decoding
- [TS-Conf](ts_conf.md) — the Russian equivalent tile/sprite engine
- [Next video frame](../../05_development/05_display_and_timing/video_frame_next.md) — tilemap timing independence

---

## References

- **TBBlue I/O Port System — Tilemap** ([specnext.com](https://www.specnext.com/tbblue-io-port-system/)) — canonical tilemap port and NextReg reference
- **NextRegister Reference** — full bit layout of `0x6E`/`0x6F`/`0x30`–`0x33`
- **sjasmplus tilemap examples** ([GitHub](https://github.com/z00m128/sjasmplus)) — sample programs in the `examples/tilemap*.asm` files
- **CSpect emulator** — tilemap engine implementation, for development testing
- **"ZX Spectrum Next Assembly Programming"** — tilemap tutorial with full game-loop example
- **NextBASIC tilemap commands** — `#TMAP`, documented in [NextZXOS](../../04_operating_systems/nextzxos.md)
