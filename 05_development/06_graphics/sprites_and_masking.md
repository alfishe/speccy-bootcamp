[← Home](../../README.md) · [Graphics](README.md)

# Software Sprites and Masking

The ZX Spectrum has **no hardware sprites**. Every moving graphic on the screen — the player's ship, the alien swarm, the bouncing ball — is drawn in software by the CPU writing bytes into the same video RAM that the ULA reads 50 times per second. Where the Commodore 64 has a VIC-II chip that handles up to 8 sprites independently of the CPU, the Spectrum gives you a frame buffer and a 3.5 MHz Z80 and wishes you luck.

This single hardware constraint shaped Spectrum game design more than any other. It determined which genres thrived (single-screen platformers with masked sprites: *Manic Miner*, *Jet Set Willy*), which were awkward (smooth horizontal scrollers: *Chase H.Q.*), and which were never attempted (more than 16 simultaneously moving objects at 50 Hz). The techniques in this article — pre-shifted sprites, masked compositing, three-screen buffered drawing, sprite pools — are how 1980s programmers fit a real game into the Spectrum's frame budget.

This article covers the **technique side** of software sprites. Engine surveys (SP1, AGD, BIFROST*, NIRVANA+) appear in [§ Sprite Engine Surveys](#sprite-engine-surveys). Authoring tools for sprite data are covered in [asset_tools.md § Sprites](../../09_toolchain/asset_tools.md#sprites). Multicolor engines (which change attributes per scanline for higher color resolution) are covered in [multicolor_engines.md](multicolor_engines.md).

> [!NOTE]
> This article assumes you have read [screen_access.md](screen_access.md) (the foundation: address tables, stack-push copy, attribute writes) and understand the non-linear pixel layout from [screen_layout.md](../03_memory_and_io/screen_layout.md).

---

## Compositing Modes

A sprite is a rectangular pixel pattern that gets combined with the existing screen contents. There are four ways to combine them, each with different tradeoffs:

### XOR (eXclusive OR)

```z80
        LD   A,(HL)              ; existing screen byte
        XOR  (DE)                ; sprite byte
        LD   (HL),A              ; write back
```

- **Cost**: ~21 T-states per byte (cheapest mode)
- **Transparent regions**: pixels where the sprite byte is `0` — XOR with 0 leaves the screen byte unchanged.
- **Visible region**: any `1` bit in the sprite toggles the corresponding screen bit.
- **Appearance**: a `1` bit shows through as the inverse of whatever was on screen. On a black background, a `1` bit appears as ink. On a colored background, the same `1` bit appears as the inverse color.
- **Drawback**: the sprite's color depends on the background. The same sprite looks different over different attribute cells.

XOR was used by *Asteroids*, *Star Wars*, and many vector-style games. Cheap and visually clean on monochrome playfields.

### OR

```z80
        LD   A,(HL)
        OR   (DE)
        LD   (HL),A
```

- **Cost**: ~21 T-states per byte
- **Transparent regions**: `0` bits in the sprite leave the screen unchanged.
- **Visible region**: any `1` bit in the sprite sets the corresponding screen bit. The result is the sprite "added" to whatever was on screen.
- **Drawback**: drawing the same sprite twice does not erase it — you need a separate clear pass.

OR is used when the background is always black (so OR is equivalent to a direct write).

### LOAD (direct overwrite)

```z80
        LD   A,(DE)
        LD   (HL),A
```

- **Cost**: ~13 T-states per byte (cheapest mode possible)
- **Transparent regions**: none — the sprite overwrites whatever was on screen, even `0` bits.
- **Visible region**: the sprite is a solid rectangle.
- **Drawback**: the sprite has a visible rectangular bounding box. Only suitable for sprites that fill their entire cell (e.g., character-cell-aligned tiles).

LOAD is used for character-based games (like *Centipede*, *Boulder Dash*) and for restoring background tiles when a sprite moves away.

### MASK (AND + OR)

```z80
        LD   A,(HL)
        AND  (DE)                ; mask byte: 0 clears, 1 preserves
        INC  DE
        OR   (DE)                ; sprite byte: sets new bits
        LD   (HL),A
```

- **Cost**: ~32 T-states per byte (most expensive mode)
- **Transparent regions**: defined by a separate **mask** — anywhere the mask is `0`, the screen byte is cleared; anywhere the mask is `1`, the screen byte is preserved.
- **Visible region**: the sprite bits OR-ed into the cleared region.
- **Advantage**: the sprite can be any shape (circle, triangle, irregular outline), not just a rectangle. The mask defines which pixels the sprite occupies, and only those pixels are touched.

MASK is the standard for action games (*Dan Dare*, *Cybernoid*, *Zynaps*). It is the only mode that produces clean, transparent, smooth-moving sprites over an arbitrary background.

---

## Pre-shifted Sprites

A 16×16 sprite is stored as 32 bytes (16 rows × 2 bytes per row). Drawing it at pixel column X requires shifting the bits to align with the byte boundary: X mod 8 = 0 needs no shift, X mod 8 = 1 needs a 1-bit shift, and so on through X mod 8 = 7.

There are two ways to do this:

1. **Shift at runtime**: the sprite drawing routine includes a shift step, computing the shifted version on each draw call. Cost: ~40 T-states per byte — doubling the cost of the draw.
2. **Pre-shift**: store **8 copies of the sprite**, each shifted by a different amount. At draw time, pick the copy matching `X mod 8`. Cost at runtime: zero — the pre-shifted copy is already in memory.

Pre-shifted sprites are the standard for 50 Hz action games. The cost is **8× the memory**: a 16×16 sprite that takes 32 bytes unshifted takes **256 bytes** pre-shifted (32 × 8 shift variants). With mask, that's **512 bytes** per sprite frame. A typical player sprite has 8 frames of animation × 8 shifts × 64 bytes = **4 KB per character**. That fits comfortably in 48K but limits how many distinct characters a game can have.

### Effective sprite dimensions

A 16-pixel-wide sprite pre-shifted is actually stored as **24 pixels wide** — 3 bytes per row. The extra byte on the right is the "shift spill" where bits shifted off the right edge of the original 2-byte pattern land. The same applies to the left edge if the sprite is shifted left.

```
Original 16×16 sprite (2 bytes per row, 32 bytes total):

  byte 0     byte 1
  ┌────────┐ ┌────────┐
  │XXXXXXXX│ │XXXXXXXX│  ← row 0 (16 pixels)
  │XXXXXXXX│ │XXXXXXXX│  ← row 1
  ...                  ...
  └────────┘ └────────┘

Pre-shifted for shift=3 (3 bytes per row, 48 bytes per shift variant):

  byte 0     byte 1     byte 2
  ┌────────┐ ┌────────┐ ┌────────┐
  │   XXXXX│ │XXXXXXXX│ │XXX     │  ← row 0 shifted right 3 pixels
  │   XXXXX│ │XXXXXXXX│ │XXX     │  ← row 1
  ...                                  ...
  └────────┘ └────────┘ └────────┘

Total memory: 8 shift variants × 48 bytes = 384 bytes per sprite frame
```

### Selecting the shift variant

```z80
; C = X pixel coordinate (0..255)
; DE = sprite base address (pointing at shift 0)
; Returns: DE → start of the correct pre-shifted variant
select_shift:
        LD   A,C
        AND  #07              ; A = X mod 8 (the shift index)
        LD   L,A
        LD   H,0
        ADD  HL,HL            ; ×2
        ADD  HL,HL            ; ×4
        ADD  HL,HL            ; ×8 ... not yet, need ×variant_size
        ; For a 16×16 sprite, variant_size = 3 bytes/row × 16 rows = 48 bytes
        ; Multiply shift_index × 48:
        LD   L,A
        LD   H,0
        ADD  HL,HL            ; ×2
        ADD  HL,HL            ; ×4
        ADD  HL,HL            ; ×8
        ADD  HL,HL            ; ×16
        ADD  HL,HL            ; ×32
        LD   C,L              ; save low byte
        LD   B,H              ; BC = shift × 32
        ADD  HL,HL            ; ×64 — close
        ; ... cleaner: precompute a shift_addr_table[8] with the actual offsets
        ADD  HL,DE            ; HL → correct shift variant
        EX   DE,HL
        RET
```

In practice, a small lookup table of 8 16-bit addresses (one per shift) is the cleanest approach — 16 bytes, ~20 T-states to index.

---

## Masked Sprite Layout

The MASK compositing mode requires the sprite data to be paired with a mask. The two common layouts are **interleaved** (mask byte followed by pattern byte, repeated) and **planar** (all mask bytes first, then all pattern bytes).

### Interleaved layout

```
Row 0:  mask[0], pattern[0], mask[1], pattern[1], mask[2], pattern[2]
Row 1:  mask[0], pattern[0], mask[1], pattern[1], mask[2], pattern[2]
...
Row 15: mask[0], pattern[0], mask[1], pattern[1], mask[2], pattern[2]
```

Per row: 6 bytes (3 mask + 3 pattern). Total for a 16×16 masked sprite: **96 bytes**. Across 8 shift variants: **768 bytes**.

The draw loop walks mask and pattern together:

```z80
; HL = screen byte address
; DE = sprite byte address (interleaved mask/pattern)
; B = number of bytes per row (3 for a 24-pixel-wide pre-shifted sprite)
draw_masked_row:
.byte_loop
        LD   A,(DE)            ; mask byte
        AND  (HL)              ; clear the sprite's bits on screen
        INC  DE
        OR   (DE)              ; combine with sprite pattern
        LD   (HL),A
        INC  DE
        INC  HL
        DEC  B
        JR   NZ,.byte_loop
        RET
```

Per byte: `LD A,(DE)` (7T) + `AND (HL)` (7T) + `INC DE` (6T) + `OR (DE)` (7T) + `LD (HL),A` (7T) + `INC DE` (6T) + `INC HL` (6T) + `DEC B` (4T) + `JR NZ` (12/7T) = **~62 T-states per byte**. For 3 bytes per row × 16 rows = 48 bytes, that's **~3,000 T-states per sprite**.

### Planar layout

```
All mask bytes first:      3 × 16 = 48 bytes
All pattern bytes second:  3 × 16 = 48 bytes
Total per frame:           96 bytes (same as interleaved)
```

The draw loop indexes both regions in parallel:

```z80
; HL = screen address
; DE = mask base, IX = pattern base
; B = bytes per row
draw_masked_row_planar:
.byte_loop
        LD   A,(DE)            ; mask byte
        AND  (HL)
        OR   (IX)              ; pattern byte
        LD   (HL),A
        INC  DE
        INC  IX
        INC  HL
        DEC  B
        JR   NZ,.byte_loop
        RET
```

Planar is slightly faster (~7 T per byte saved from avoiding one `INC DE`) but requires the pattern pointer in `IX`, which has slower increment (`INC IX` is 10 T-states vs `INC DE` 6 T). Net result is roughly the same speed.

The interleaved layout is more common in shipping games because it allows the mask and pattern to be packed together by sprite editors (SevenUp, ZX Paintbrush) and the draw loop is simpler.

---

## Three-Screen Buffered Drawing

Drawing a masked sprite directly to the visible screen produces visible flicker: the sprite's old position must be cleared (showing the background again) and the new position must be drawn. If both operations happen while the beam is mid-screen, the player sees a brief flash of background in the old position and then the sprite in the new position — acceptable at 50 Hz if the timing is tight, but jittery if any frame is delayed.

The classic solution, used by *Dan Dare*, *Cybernoid*, and most action games of the late 1980s, is the **three-screen buffered architecture**:

1. **Visible screen**: the actual video RAM at `#4000`–`#57FF`. The ULA reads from here.
2. **Background buffer**: a copy of the static playfield (tiles, walls, obstacles), stored in some other region of RAM.
3. **Drawing buffer**: a working copy where sprites are composited each frame.

The frame loop:

```
BEAM-CRITICAL PHASE (during top border or VBLANK):
  1. Copy drawing buffer → visible screen (using stack-push for speed)
  2. Copy background buffer → drawing buffer at sprite old positions (erase)
  3. Update sprite coordinates (logic)
  4. Draw sprites into drawing buffer at new positions
  5. Wait for next beam-safe window
```

The advantage of this architecture is that the visible screen never shows an intermediate state — it always shows either the previous frame's drawing buffer or the current frame's drawing buffer, never a half-drawn one. The disadvantage is memory: two extra 6 KB buffers in RAM, totaling ~12 KB just for buffering. On a 48K Spectrum this leaves only ~28 KB for code, level data, music, and other assets. Many games split the screen into a smaller "playfield" buffer (e.g., 16 × 16 cells = 4 KB) instead of buffering the full screen.

### Single-buffer flicker elimination

If you cannot afford three buffers, the alternative is to **race the beam**: draw the sprite's old position (erase) and new position (draw) in the brief window after the beam passes those rows but before it wraps to the next frame. This requires careful timing and breaks if anything delays the routine. See [race_the_beam.md](../04_interrupts/race_the_beam.md) for the synchronization strategies.

Most games use one of:

- **Stack-push double buffering**: two screen buffers, copy one to visible RAM during VBLANK.
- **Single-screen with HALT sync**: draw sprites directly to visible RAM, but only during the top border before the beam enters the pixel area.
- **Three-screen buffered**: as above, used when memory permits.

### The eight-phase sprite loop

The canonical sprite loop, as documented by Tero Heikkinen's analysis of *Ghouls 'n' Ghosts* and similar games, runs in eight phases synchronized to the beam:

```
BEFORE THE LOOP:
  - Copy entire background → drawing buffer
  - Draw sprites into drawing buffer; record their positions in an address table

LOOP (one iteration per frame):
  1. HALT (wait for VBLANK)
  2. RED phase:    Copy sprites from drawing buffer → visible screen
  3. BLUE phase:   Restore background at sprites' old positions in drawing buffer
  4. YELLOW phase: Update sprite coordinates (game logic)
  5. BLUE phase:   Record new address table
  6. YELLOW phase: Draw sprites at new positions in drawing buffer
  7. BLACK phase:  Wait until beam is outside pixel area (timing-estimated)
  8. RED phase:    Restore background at sprites' old positions on visible screen
```

The colored phase names refer to the border color changes used for debugging — early Spectrum developers would write a different border color at the start of each phase so they could see on a CRT how much time each phase consumed. A well-tuned loop leaves the border black for most of the frame; a struggling loop shows the colors bleeding into the pixel area.

This loop achieves **8 flicker-free 16×16 masked sprites** on a stock 48K Spectrum. That's roughly the limit of what the machine can do at 50 Hz with a real game behind it.

---

## Sprite Pools and Frame Budgets

Real games don't draw one sprite — they draw the player, multiple enemies, multiple projectiles, multiple pickups, all in the same frame. A **sprite pool** is a fixed-size array of sprite descriptors that the engine walks each frame:

```z80
; Each sprite descriptor is 8 bytes:
;   +0: status byte (0 = inactive, 1 = active, other bits = flags)
;   +1: X pixel coordinate (low byte)
;   +2: X pixel coordinate (high byte — usually 0)
;   +3: Y pixel coordinate
;   +4: sprite frame pointer (2 bytes)
;   +6: animation counter
;   +7: reserved
MAX_SPRITES   EQU 16
sprite_pool:  DEFS MAX_SPRITES * 8
```

The draw loop:

```z80
draw_all_sprites:
        LD   IX,sprite_pool
        LD   B,MAX_SPRITES
.loop   LD   A,(IX+0)
        OR   A
        JR   Z,.skip              ; inactive — skip
        ; Active sprite: draw it
        LD   L,(IX+4)
        LD   H,(IX+5)             ; HL → sprite frame
        LD   C,(IX+1)             ; X low
        LD   B,(IX+3)             ; Y
        CALL draw_sprite_masked
.skip   LD   DE,8
        ADD  IX,DE                ; next descriptor
        DEC  B
        JR   NZ,.loop
        RET
```

### Frame budget breakdown

At 50 Hz with a 48K Spectrum (69,832 T-states/frame, of which ~14,000 are uncontended), a typical action game allocates the frame as follows:

| Phase | T-states | Notes |
|---|---|---|
| Music player (IM2 ISR) | ~3,000 | PT3 or similar |
| Game logic (input, AI, collision) | ~10,000 | Variable |
| Sprite erase (8 sprites) | ~8,000 | Restore background at old positions |
| Sprite draw (8 sprites, 16×16 masked) | ~24,000 | The expensive part |
| Attribute updates (8 sprites × 4 cells) | ~2,000 | Color cells touched |
| Buffer → screen copy | ~10,000 | Stack-push for one playfield row strip |
| **Total** | **~57,000** | Leaves ~13,000 for edge cases |

If a frame's work exceeds 69,832 T-states, the game drops to 25 Hz (every other frame) or 16.7 Hz (every third frame). The player perceives this as "slowdown" — common in shooters when the screen fills with bullets.

---

## Sprite Engine Surveys

The ZX Spectrum community has produced several published sprite engines that handle the layout, compositing, and frame budget details for you. These are the major ones in active use as of 2024.

### SP1 (z88dk Software Sprite Library)

**SP1** is Alvin Albrecht's software sprite library, distributed with z88dk. It is the most widely used sprite engine in modern Spectrum homebrew.

- **Architecture**: character-cell-based. The screen is divided into 8×8 cells, each managed independently. SP1 tracks a "dirty list" of cells that changed during the current frame and only redraws those cells.
- **Compositing**: supports MASK, OR, XOR, LOAD, plus user-defined draw functions per sprite.
- **Plane system**: 256 sprite planes. Plane 0 is on top; plane 255 is just above the background. Overlapping sprites on the same plane have indeterminate draw order.
- **Sprite sizes**: any size, broken into 8×8 character sub-sprites internally. Each sub-sprite can have a different draw type (e.g., outline cells use MASK, interior cells use LOAD for speed).
- **Performance**: flicker-free without raster sync. Differential update means only changed cells are redrawn. Static sprites are essentially free.
- **Limitation**: NOT designed for scrolling. Differential update works when most of the screen is static; scrolling makes every cell dirty, defeating the optimization. Character-cell scrolling (board games, slow vertical scrollers) works; pixel-smooth scrolling does not.
- **Notable games**: *Cannon Bubble*, *Minesweeper*, *Moggy*, *Phantomas Infinity*, plus hundreds of modern homebrew.

The SP1 distribution includes a customization file where you specify the screen area managed, the location of SP1's variables, and the screen size. The library is then compiled into a `.lib` and linked with `-lsp1`.

### AGD / MPAGD (Arcade Game Designer)

**AGD** (later **MPAGD**, Multi-Platform Arcade Game Designer) is Jonathan Cauldwell's game creation tool. It targets the ZX Spectrum, Amstrad CPC, MSX, BBC Micro, and others from a single project.

- **Architecture**: character-cell-aligned sprites. The entire game world is built from 8×8 tiles and 8×8-aligned sprites — no pre-shifting, no smooth movement within a cell.
- **Compositing**: LOAD (direct overwrite) with background restoration on sprite movement.
- **Performance**: very fast — character-cell alignment means every sprite draw is a fixed-cost tile copy. Tradeoff: movement is jerky (one cell per frame minimum).
- **Use case**: best for beginners and for games where smooth movement is not critical (puzzles, board games, arcade adventures).
- **Notable games**: hundreds of modern homebrew titles on Spectrum Computing and itch.io.

### BIFROST* Engine

**BIFROST\*** is Einar Saukas's multicolor 8×1 graphics engine, released in 2012. It is documented in detail in [multicolor_engines.md](multicolor_engines.md); here we note its relevance to sprite work.

- **Architecture**: tile-based engine with 8×1 color resolution (64 times finer than the stock 8×8 attribute cell). The engine handles the raster-synchronized attribute writes; the game logic treats tiles as ordinary 8×8 sprites.
- **Playfield size**: 18 character columns × 18 character rows (about 56% of the screen).
- **Compositing**: LOAD for tiles; background is a fixed tile map maintained by the engine.
- **Performance**: 50 Hz with up to ~50 simultaneously animated tiles.
- **Notable games**: *Knights & Demons DX*, *Pets vs Aliens Prologue*, *Complica DX*, *Pushbot*.

### NIRVANA+ Engine

**NIRVANA+** is Einar Saukas's multicolor 8×2 graphics engine, released in 2015. It is the practical alternative to BIFROST* for games that need a larger playfield.

- **Architecture**: tile-based with 8×2 color resolution (8 times finer than stock).
- **Playfield size**: 32 character columns × 23 character rows (essentially the full screen).
- **Compositing**: LOAD for tiles.
- **Performance**: 50 Hz with up to ~50 simultaneously animated tiles. The 8×2 resolution is a deliberate tradeoff — slightly less color detail than BIFROST*'s 8×1 but dramatically more playable area.
- **Notable games**: *Snake Escape*, *Pietro Bros*, *Gandalf*, plus *Bomberman* (in development).

### Choosing an engine

| Use case | Recommended engine |
|---|---|
| Modern C/C++ homebrew, flicker-free sprites | SP1 (z88dk) |
| Beginner, simple game, multiple platforms | MPAGD |
| Maximum color resolution (8×1), small playfield OK | BIFROST* |
| Larger playfield, 8×2 color resolution acceptable | NIRVANA+ |
| Custom engine, full control, no library dependency | Hand-rolled (this article) |

---

## Color Clash Workarounds

The Spectrum's attribute cell — 8×8 pixels with one INK, one PAPER, one BRIGHT, one FLASH — is the source of the machine's most mocked graphical artifact: **color clash**. When two differently-colored objects share an 8×8 cell, the cell can only display one INK/PAPER pair, and the wrong-colored object "bleeds" into the right-colored one.

Game designers evolved five standard strategies for living with color clash:

### Strategy 1: Character-cell-aligned sprites

Constrain all sprites to move on 8-pixel boundaries. No sprite ever straddles two cells. Each cell's attribute can be set once for the sprite that lives in it. Games using this approach: *Centipede*, *Boulder Dash*, *Chuckie Egg*. Movement feels blocky but the colors are always right.

### Strategy 2: Monochrome playfield with color highlights

Keep the playfield pixels strictly black-and-white. Place color only in cells where the attribute is unambiguous — typically score bars, status displays, or carefully-chosen background cells. Games: *Manic Miner*, *Jet Set Willy*, *Chuckie Egg*. The most iconic Spectrum aesthetic.

### Strategy 3: Accept the clash

Let color clash happen. Design the game so the clash is not game-breaking — typically by using a consistent background color and letting sprites "tint" the cells they overlap. Games: the *Dizzy* series, *Earth Shaker*. The clash becomes part of the Spectrum's distinctive look rather than a defect.

### Strategy 4: Isometric monochrome per room

Use isometric perspective (see [3d_graphics.md § Isometric](3d_graphics.md#isometric-engines)) where the entire playfield is one color per room. The player and objects are all the same INK; the room's PAPER is set once when the room loads. Games: *Knight Lore*, *Alien 8*, *Head Over Heels*, *Batman*. Color appears only in the border or status area.

### Strategy 5: Multicolor engines

Use a multicolor engine (BIFROST*, NIRVANA+, ULAplus) that changes attributes per scanline, achieving 8×1 or 8×2 color resolution. The clash is not gone but is reduced to a much smaller area. See [multicolor_engines.md](multicolor_engines.md) for the full treatment.

---

## Common Pitfalls

### Pre-shifting in the wrong direction

Pre-shifted sprite tables shift **right** by default — shift variant 0 is unshifted, shift variant 1 is shifted 1 pixel right, and so on. If your X coordinate increases left-to-right (the usual convention), the lookup `shift = X % 8` works directly. If you flip the convention, you must reverse the table.

### Forgetting the shift spill byte

A 16-pixel-wide sprite at shift=7 has bits in 3 bytes (bytes 0, 1, 2 of the row). The naive 2-byte-per-row draw loop overwrites only bytes 0 and 1, leaving byte 2 untouched — visible as a missing right edge. Always allocate 3 bytes per row for pre-shifted 16-wide sprites.

### Drawing the same sprite twice

XOR compositing is its own inverse: drawing the same sprite twice at the same position erases it. OR and LOAD are not — drawing twice leaves the sprite permanently on screen. If you use OR or LOAD, you must explicitly erase (typically by copying the background back) before drawing the next frame.

### Mask byte in the wrong position

For interleaved mask/pattern layout, the mask must come **before** the pattern in each pair. Reversing the order produces the visual inverse of the sprite (you AND with the pattern and OR with the mask).

### Stack in video RAM during a sprite draw

If your draw routine uses `PUSH` (for stack-push drawing) and you forget to `DI` first, an interrupt during the draw will land on the screen as visible corruption. See the same warning in [screen_access.md § Block Copy via Stack Push](screen_access.md#block-copy-via-stack-push).

### Attribute cells not updated

When a sprite moves, the cells it occupied should have their attributes restored to the background values. Forgetting this leaves "ghost color" — cells that briefly held the sprite keep the sprite's INK, producing colored halos around the playfield. Track the cells each sprite touched and restore them in the erase phase.

---

## Cross-References

- [screen_access.md](screen_access.md) — the foundation primitives this article builds on: address tables, stack-push copy, attribute writes.
- [scrolling_and_buffering.md](scrolling_and_buffering.md) — applies the same buffered architecture to panning cameras rather than moving sprites.
- [multicolor_engines.md](multicolor_engines.md) — engines that achieve higher color resolution by raster-synchronized attribute writes; the natural next step beyond MASK compositing.
- [race_the_beam.md](../04_interrupts/race_the_beam.md) — synchronization strategies for the single-buffer flicker elimination technique.
- [color_system.md](../05_display_and_timing/color_system.md) — the attribute byte format, the standard palette, and the underlying cause of color clash.
- [contention_timing.md](../05_display_and_timing/contention_timing.md) — why screen writes during the active display cost more T-states.
- [asset_tools.md](../../09_toolchain/asset_tools.md) — authoring tools for sprite data (SevenUp, ZX Paintbrush, ZX PearPixel) and the sprite format table.
- [native_toolchain.md](../../09_toolchain/native_toolchain.md) — 1980s sprite editors and the historical lineage of the techniques here.
- [interrupt_programming.md](../04_interrupts/interrupt_programming.md) — the IM1/IM2 ISR framework that the eight-phase sprite loop depends on.

---

## References

- **Dean Belfield, "Smooth Scrolling on the ZX Spectrum"** ([breakintoprogram.co.uk](http://www.breakintoprogram.co.uk/software_development/smooth-scrolling-on-the-zx-spectrum-intro)) — modern worked examples of masked sprites, racing the beam, and the eight-phase loop.
- **Jonathan Cauldwell, "How to Write ZX Spectrum Games"** — chapter 13 covers the stack-push sprite technique used in commercial 1980s games.
- **Tero Heikkinen, "ZX Sprites"** (Old Machinery blog, April 2014) — three-screen buffered drawing, 16×16 masked sprite layout, eight-phase frame loop. The single best practical reference for sprite engines.
- **Paleotronic Magazine, "Colour Clash"** — historical survey of how 1980s game designers worked around the 8×8 attribute constraint.
- **SP1 documentation** ([z88dk wiki](https://www.z88dk.org/wiki/doku.php?id=library:sprites:sp1)) — Alvin Albrecht's official SP1 library reference.
- **BIFROST* Engine reference** ([Sinclair Wiki](https://sinclair.wiki.zxnet.co.uk/wiki/BIFROST*_Engine)) — Einar Saukas's official engine documentation and game list.
- **NIRVANA+ Engine reference** ([Sinclair Wiki](https://sinclair.wiki.zxnet.co.uk/wiki/NIRVANA%2B_Engine)) — Einar Saukas's official engine documentation and game list.
- **MPAGD home** ([jonathan-cauldwell.itch.io](https://jonathan-cauldwell.itch.io/multi-platform-arcade-game-designer)) — Jonathan Cauldwell's modern game design tool.
- **z88dk SP1 tutorial series** ([jsmolina/z88dk-tutorial-sp1 on GitHub](https://github.com/jsmolina/z88dk-tutorial-sp1)) — community-contributed SP1 learning materials.
- **Using SP1 for Scroller Games** ([ZXjogv blog](https://jogv.es/posts/2023/05/02/sp1_for_scroller_games/)) — practical modern writeup of using SP1's character-cell background for vertical scrollers.
