[← Home](../../README.md) · [New Gen Hardware](README.md) · [ZX Spectrum Next](zx_next.md)

# ZX Spectrum Next — Hardware Sprites

The ZX Spectrum Next's **hardware sprite engine** is the platform's first-ever sanctioned use of hardware sprites — every prior "sprite" trick on the Spectrum (pre-shifted software sprites, attribute-color sprites, BEEP-raster interrupts) was a CPU-side workaround for the ULA's lack of sprite hardware. On the Next, sprites are entirely GPU-side: a sprite can move across the screen while the CPU does something else entirely.

This article is the **programmer's reference** for the Next sprite engine: pattern memory layout, the attribute structure, the upload protocol, sprite types (4-bit / 8-bit), priority and collision detection, and the per-scanline visibility limit. For the Next's other layers, see [zx_next.md](zx_next.md) (overview), [zx_next_layer2.md](zx_next_layer2.md), [zx_next_tilemap.md](zx_next_tilemap.md), and [zx_next_copper.md](zx_next_copper.md).

---

## Sprite Engine Capabilities

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

---

## Sprite Pattern Memory Layout

Pattern RAM holds the sprite pixel data, organized as **pattern slots**. Each slot is a 16×16-pixel image, and the slot layout depends on the bit depth:

| Pattern type | Bytes per slot | Pattern slots in 64 KB | Slot numbering |
|---|---|---|---|
| **4-bit** (16 colors) | 128 bytes | 64 patterns (slots 0–63) | `(slot × 128)` |
| **8-bit** (256 colors) | 256 bytes | 32 patterns (slots 0–31, occupying slots 0–63 pairwise) | `(slot × 256)` |

A 4-bit pattern uses one **nibble per pixel**, with the upper nibble first (pixel 0 in upper nibble of byte 0, pixel 1 in lower nibble of byte 0, pixel 2 in upper nibble of byte 1, etc.). An 8-bit pattern uses one byte per pixel, with each byte indexing the active palette.

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

---

## Sprite Attribute Structure

Once patterns are uploaded, you create **sprite instances** by writing **5-byte attribute records** to the sprite attribute pipeline. Each record describes one sprite on screen.

### Attribute Upload Protocol

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

The exact bit layout is critical; the [official Next sprite documentation](https://gitlab.com/thesmog358/tbblue/-/blob/master/docs/NextRegisterReference.md) is the canonical source.

### Example — Place a Sprite at (100, 50) Using Pattern 2

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

The sprite is now visible at (100, 50) showing pattern 2's image, drawn from the 4-bit pattern palette.

---

## Sprite Types — 4-bit vs 8-bit

Each sprite individually selects **4-bit** or **8-bit** rendering via bit 6 of attribute byte 5:

- **4-bit sprites**: each pixel is a nibble, using the lower 16 entries of the palette. Faster to upload, more patterns fit in 64 KB.
- **8-bit sprites**: each pixel is a full byte, using any of the 256 palette entries. Slower to upload (256 bytes vs 128), but full color fidelity.

Mix 4-bit and 8-bit sprites freely on the same frame — the engine handles the depth per-sprite.

---

## Sprite Priority and Compositing

The Next's sprite engine composites sprites in **slot order** — slot 0 is drawn first (at the back), slot 63 last (in front). The Z-order of sprites is therefore fixed by their slot number, not by a per-sprite priority flag.

The sprite layer as a whole sits at a fixed position in the [layer stack](zx_next.md#the-layer-stack) — above Layer 2 and the tilemap, below the border. To make a sprite appear behind Layer 2 (e.g., for a "background sprite" effect), use **sprite-relative clipping** via the copper or simply write transparent pixels (palette index 0) where the sprite should not appear.

### Transparency

Palette index **0 is transparent** by default for both 4-bit and 8-bit sprites. Pixels with value 0 are not drawn — sprites of any shape (not just rectangles) can be made by leaving the corners as palette 0. The `LDIX` / `LDPIR` Z80N instructions also respect palette index 0 when copying, allowing fast transparency-aware pattern upload.

> [!TIP]
> The transparent palette index is configurable via the sprite-related NextRegs. Some games redefine index 0 as visible and use a different index for transparency — useful when you need pure black to be a real color.

---

## Collision Detection

The sprite engine reports **collisions** through NextReg `0x29` (**Sprite Collision**). The hardware sets bits in this register when any two sprite non-transparent pixels overlap during a scanline:

| Bit | Collision type |
|---|---|
| 0 | Any two sprites with non-transparent pixels overlapped |
| 1 | Any sprite with the (optional) backdrop or any "boundary" |

To detect a collision:

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

---

## Per-Scanline Visibility Limit

The Next's sprite engine can render **up to 64 sprites per scanline** without flicker. If more than 64 sprites' X-coordinates put them on the same scanline, sprites beyond the 64th **silently disappear** — they are not drawn, but no error is reported.

For games that may exceed the per-scanline limit, the standard mitigation is:

1. **Cull off-screen sprites** — sprites with Y outside `[0, 191]` or X outside `[-16, 319]` should be marked disabled (bit 7 of attribute byte 5 = 0).
2. **Sort by visual priority** — assign the lowest slot numbers (drawn first) to sprites the player must see, and the highest slot numbers to sprites that can be dropped.
3. **Use the copper** to swap sprite slots mid-frame — see [zx_next_copper.md](zx_next_copper.md) for the technique.

For most software (10–30 sprites per frame, scattered across the screen), the per-scanline limit is not a concern.

---

## Sprite System NextRegs

| Reg | Name | Function |
|---|---|---|
| `0x15` | Layer 2 / sprites / tilemap enable | Bit 2 = enable sprites globally |
| `0x29` | Sprite collision | Read collision flags; write to clear |
| `0x2A` | Sprite sprite-priority / clipping | Sprite clip window Y-start, etc. |
| `0x2B` | Sprite clip window (low) | Clip window X-start |
| `0x2C` | Sprite clip window (high) | Clip window X-end |
| `0x34` | Sprite clip window Y-start | Top of clip window |
| `0x35` | Sprite clip window Y-end | Bottom of clip window |
| `0x50` | Sprite pattern / attribute upload protocol | Used in some firmware revisions |

The sprite clip window lets you restrict sprite drawing to a sub-rectangle of the screen. Sprites outside the clip window are not drawn. This is useful for **status bars** (sprites should not overlap the top 16 lines of HUD) or for **viewport clipping** (sprites should not draw past the right edge of a scrolling playfield).

---

## Typical Sprite Game Loop

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

## Cross-References

- [ZX Spectrum Next](zx_next.md) — platform overview, layer stack, NextReg system
- [Layer 2](zx_next_layer2.md) — background under sprites
- [Tilemap](zx_next_tilemap.md) — alternative background layer
- [Copper](zx_next_copper.md) — for mid-frame sprite slot swapping
- [Next video frame](../../05_development/05_display_and_timing/video_frame_next.md) — sprite timing independence
- [Next memory map and I/O ports](../../05_development/03_memory_and_io/memory_and_io_next.md) — full port decoding
- [TS-Conf sprites](ts_conf.md) — the Russian equivalent (different sprite engine)

---

## References

- **TBBlue I/O Port System — Sprites** ([specnext.com](https://www.specnext.com/tbblue-io-port-system/)) — canonical sprite port and NextReg reference
- **NextRegister Reference** (community-maintained) — full bit layout of every sprite NextReg
- **"ZX Spectrum Next Assembly Programming"** — D. R. M. Gomes, tutorial covering sprite engines in depth
- **sjasmplus examples** ([GitHub](https://github.com/z00m128/sjasmplus)) — sample sprite programs in the `examples/` directory
- **CSpect emulator** ([cspect.org](https://cspect.org)) — sprite engine implementation for development testing
- **NextBASIC sprite commands** — `#SPRITE`, `#SPRITE MOVE`, documented in [NextZXOS](../../04_operating_systems/nextzxos.md)
