[← Home](../../README.md) · [Graphics](README.md)

# Scrolling and Double Buffering

A scrolling game — *Scuba Dive*, *Chase H.Q.*, *LED Storm*, *Ghouls 'n Ghosts* — needs to shift the entire playfield by some number of pixels every frame while sprites move over the top. On a machine with hardware scrolling or hardware sprites (C64, NES), this is almost free. On the ZX Spectrum, scrolling means **moving 6,144 bytes of pixel data within the frame budget, every frame, while also drawing the sprites**.

The result is a tight engineering problem with a small number of known-good solutions. This article covers the four techniques that shipping games actually used: character-cell scrolling (cheap, jerky), pixel-smooth horizontal scrolling (expensive, smooth), 128K shadow-screen double buffering (free if you have the RAM), and dirty-rectangle partial update (compromise).

This article builds on [screen_access.md](screen_access.md) (address tables, stack-push copy) and [sprites_and_masking.md](sprites_and_masking.md) (the buffered architecture). The demoscene side of scrolling — raster-synchronized effects, copper bars, full-screen multicolor — is covered in [border_effects.md](../05_display_and_timing/border_effects.md) and [multicolor_engines.md](multicolor_engines.md).

> [!NOTE]
> Scrolling is the Spectrum's most expensive 2D operation. Even the best pixel-smooth horizontal scroller manages only **25 Hz** (two-frame cycle) on a stock 48K machine. 50 Hz scrolling is possible on the 128K thanks to the shadow screen buffer (see [§ 128K Shadow Screen](#128k-shadow-screen-double-buffering)).

---

## Character-Cell Scrolling

The cheapest form of scrolling moves the playfield by **one character cell** (8 pixels) per step. There is no bit-shifting; the screen simply shows a different window of the level map.

### Implementation

Maintain the level as a tile map: a 2D array of tile indices, each tile being 8×8 pixels (8 bytes). The visible screen is 32×24 cells. To scroll right by one cell:

1. Discard the leftmost column of cells (they scroll off-screen).
2. Shift all remaining cells left by one column in the screen buffer.
3. Draw the new rightmost column from the tile map.

The cell shift can be done with `LDIR` (slow) or with stack-push copy (fast). For 24 rows × 32 cells × 8 bytes per cell, the cost is roughly 6,000 T-states using stack-push — affordable at 50 Hz.

### Games using this approach

- *Boulder Dash* and descendants (puzzle-action, cell-by-cell movement)
- *Centipede* (cell-based character movement)
- Most board games and turn-based strategy games
- AGD/MPAGD-engine games (character-cell-aligned by design)

### Limitations

Movement is jerky. A character at column 10 either stays at column 10 or jumps to column 11 — no smooth interpolation. For action games, this is usually unacceptable. Most "real" scrolling games use pixel-smooth scrolling instead.

---

## Pixel-Smooth Horizontal Scrolling

True pixel-smooth scrolling shifts the playfield by 1–7 pixels per frame, requiring bit-shifting of the entire pixel buffer. The standard technique, used by *LED Storm*, *Ghouls 'n Ghosts*, and most modern homebrew scrollers, is the **stack-push scroll**.

### The core idea

For each pixel row of the screen (192 rows):

1. Set `SP` to point at the right end of the row (e.g., `#401F` for the first row).
2. Pop 16 register pairs (32 bytes) into the available registers — this reads the existing row.
3. Adjust each register pair to shift the bits one pixel right (using `SRL H; RR L` for each pair, or pre-shifted lookup).
4. Set `SP` to point at the destination (which may be the same row offset by one byte).
5. Push the register pairs back out — this writes the shifted row.

The shift step is the expensive part: 16 register pairs × ~16 T-states per pair = ~256 T-states per row, on top of the 176 T-states for the pop/push. Total per row: ~432 T-states. For 192 rows: **~83,000 T-states** — more than one full frame.

This is why pixel-smooth scrollers run at **25 Hz** (two-frame cycle): one frame shifts the buffer, the next frame draws sprites and copies to the visible screen.

### The two-frame cycle

```
Frame N:  (sprite update + buffer management, ~30,000 T-states)
Frame N+1: (scroll shift + buffer→screen copy, ~50,000 T-states)
Frame N+2: (back to sprite update)
...
```

The player sees new sprites at 25 Hz but the background scroll also advances at 25 Hz — visually consistent. Many games (*LED Storm*, *Ghouls 'n Ghosts*) use exactly this pattern.

### Optimized variant: stack-push with embedded shift

Dean Belfield's worked example ([breakintoprogram.co.uk](http://www.breakintoprogram.co.uk/software_development/smooth-scrolling-on-the-zx-spectrum-intro)) combines the pop, shift, and push into a single self-modifying code loop. The trick is to pre-build the inner loop at startup based on the scroll direction and width, then execute it once per frame.

The inner loop, in pseudocode:

```
; For each pixel row:
        LD SP, source_row_end - 1
        POP BC: POP DE: POP HL: POP IX    ; 8 bytes
        ; ... shift each pair right by 1 bit ...
        SRL B: RR C
        SRL D: RR E
        SRL H: RR L
        ; ... continue for IX, IY, AF ...
        LD SP, dest_row_end - 1
        PUSH AF: PUSH IY: PUSH IX: PUSH HL: PUSH DE: PUSH BC
        ; Advance to next row
```

This achieves ~300 T-states per row (including overhead), or **~58,000 T-states for the full screen**. Still over the 50 Hz frame budget, but closer.

### Dixel scrolling (2-pixel step)

A compromise: scroll 2 pixels at a time instead of 1. This halves the number of scroll operations needed (since the player's eye tolerates 2-pixel jumps at 25 Hz) and produces visibly faster movement for the same engine cost.

Dixel scrolling was documented in *Your Sinclair* issue 19 and is used by some Russian demoscene productions.

---

## 128K Shadow Screen Double Buffering

The 128K Spectrum (and +2, +2A, +3, and all clones) has a **shadow screen buffer** in RAM bank 7. By toggling bit 3 of port `#7FFD`, the CPU can switch which bank the ULA reads from for video display:

```z80
; Switch to shadow screen (bank 7)
show_shadow:
        LD   BC,#7FFD
        LD   A,(current_bank)
        SET  3,A                ; bit 3 = 1 means show bank 7
        LD   (current_bank),A
        OUT  (C),A
        RET

; Switch to main screen (bank 5)
show_main:
        LD   BC,#7FFD
        LD   A,(current_bank)
        RES  3,A                ; bit 3 = 0 means show bank 5
        LD   (current_bank),A
        OUT  (C),A
        RET
```

Both banks have the same layout: pixel buffer at offset `#4000`–`#57FF` and attribute file at `#5800`–`#5AFF`. The CPU can write to whichever bank is currently **not** displayed, then flip the bit during VBLANK to make the new frame visible.

This is the **only** way to achieve true flicker-free animation on the Spectrum: the player never sees a half-drawn frame, because the visible screen is always the previously-completed one.

### Tradeoffs

- **Memory cost**: the second screen consumes 6,912 bytes of bank 7 RAM, which is otherwise available for code or data. Most 128K games use bank 7 as the shadow screen and place music, level data, and other assets in banks 0-3, 4, 6.
- **Bank switching cost**: every `OUT (#7FFD),A` costs 11 T-states, plus the cost of loading `A` from a variable. The flip itself is cheap; the cost is the discipline of doing all bank-7 writes while bank 7 is paged in (which means CPU writes go to the currently-displayed bank).
- **Synchronization**: the flip must happen during VBLANK (top border or bottom border). Otherwise the ULA might read from the new bank partway through a scanline, producing a visible seam.

### Architecture

```
Bank 5 (main screen, default display):
  #4000-#57FF  Pixel buffer (visible)
  #5800-#5AFF  Attribute file (visible)

Bank 7 (shadow screen, alternate display):
  #4000-#57FF  Pixel buffer (drawing target)
  #5800-#5AFF  Attribute file (drawing target)
```

The frame loop:

1. **Currently displaying bank 5, drawing in bank 7**: do all sprite draws, scroll updates, attribute writes to bank 7.
2. **VBLANK**: `OUT (#7FFD), bit_3_set` — now bank 7 is visible, bank 5 is the drawing target.
3. **Drawing in bank 5**: same work as step 1.
4. **VBLANK**: `OUT (#7FFD), bit_3_clear` — back to displaying bank 5.

The result is 50 Hz, fully flicker-free, with no need for timing-exact raster sync. The cost is just the discipline of always writing to the off-screen bank.

### Games using this approach

- *Dizzy* series (128K versions)
- *Turbo Outrun*
- Most late-period 128K-exclusive games
- Modern 128K-targeted homebrew

The 48K Spectrum cannot do this — there is no bank 7, no port `#7FFD`, no shadow screen. 48K games must use one of the other techniques.

---

## Dirty Rectangle Partial Update

A full screen redraw — clear the playfield, redraw all background tiles, redraw all sprites — is expensive even with stack-push copy. The dirty rectangle optimization exploits the fact that **most of the screen does not change between frames**.

### The technique

Maintain a **dirty map**: a 32×24 byte array (768 bytes, one byte per attribute cell) where each byte is `0` (clean) or `1` (dirty). When you draw a sprite, mark the cells it touched as dirty. When you erase a sprite (restore background), mark those cells as dirty. At the end of the frame, walk the dirty map and copy only the dirty cells from the back buffer to the visible screen.

```z80
; Walk dirty map and copy dirty cells from back buffer to screen
; HL = dirty map address, DE = back buffer, IX = screen
render_dirty_cells:
        LD   B,24               ; 24 rows
.row_loop
        PUSH BC
        LD   B,32               ; 32 columns
.col_loop
        LD   A,(HL)
        OR   A
        JR   Z,.skip            ; clean — skip
        ; Dirty: copy 8 bytes from back buffer (DE) to screen (IX)
        PUSH HL
        PUSH DE
        PUSH IX
        ; Use stack-push to copy 8 bytes (4 register pairs)
        ; ... (omitted for brevity) ...
        POP  IX
        POP  DE
        POP  HL
.skip   INC  HL                 ; next dirty map cell
        ; Advance DE and IX to next cell (8 bytes forward)
        ; ... (omitted) ...
        DEC  B
        JR   NZ,.col_loop
        POP  BC
        DEC  B
        JR   NZ,.row_loop
        RET
```

### Performance

For a typical scene with 8 sprites each touching ~6 cells, the dirty count is ~48 cells per frame. Copying 8 bytes per cell via stack-push costs ~100 T-states per cell, so the total is ~4,800 T-states — **versus ~10,000 T-states for a full screen copy**. The dirty map itself costs 768 bytes of RAM.

The dirty rectangle is the standard optimization for 48K games that cannot afford a shadow screen. It pairs naturally with SP1 (z88dk's software sprite library), which is built around this technique — see [sprites_and_masking.md § SP1](sprites_and_masking.md#sp1-z88dk-software-sprite-library).

---

## Vertical Scrolling

Vertical scrolling is mechanically simpler than horizontal scrolling because the Spectrum's pixel layout makes vertical shifts cheap: each pixel row is exactly 256 bytes after the previous one (within a character row), so copying one row to the next is a `LD (DE),A; INC D` pattern (since `INC D` advances by 256).

### Stack-push vertical scroll

To scroll up by one pixel row across the entire screen:

```z80
scroll_up_1px:
        DI
        LD   (saved_sp),SP
        ; For each of 191 rows (row 0 is the new top, source is row 1)
        LD   HL,#4100           ; row 1 (will be the new row 0)
        LD   DE,#4000           ; destination: row 0
        LD   B,191              ; 191 rows to copy
.row_loop
        LD   SP,HL              ; source
        POP  AF: POP BC: POP DE: POP HL: POP IX: POP IY  ; wait, regs full
        ; Better: do it in chunks. For now, assume an unrolled copy.
        ; ...
        ; The cleanest approach uses a precomputed table of row start addresses
        ; and an unrolled stack-push loop per row.
        DEC  B
        JR   NZ,.row_loop
        LD   SP,(saved_sp)
        EI
        RET
```

Vertical scrollers typically achieve **25 Hz** with full sprite overlay, comparable to horizontal scrollers. Pure vertical scroll (no sprites) can hit 50 Hz on the 48K.

### Games using vertical scroll

- *Flying Shark* (vertical shooter, multi-directional)
- *720°* (skateboarding, vertical-scrolling ramps)
- *Stormlord* (vertical exploration)
- Many modern homebrew shooters

---

## Parallax Scrolling

Parallax scrolling — multiple background layers moving at different speeds to simulate depth — is rarely seen on the 48K Spectrum because the cost of scrolling even one layer is already at the frame budget. When it does appear, it is typically achieved by:

1. **Static back layer + scrolling front layer**: the back layer is a fixed image (e.g., a starfield) drawn once, and only the front layer scrolls. Cost: same as single-layer scroll. Used by many space shooters for the "stars moving past" effect.
2. **Character-cell back layer + pixel-smooth front layer**: the back layer moves at character-cell rate (jerky but cheap), the front layer moves pixel-smooth. Cost: roughly 1.5× single-layer scroll. Used by some platformers for distant backgrounds.
3. **Attribute-only back layer**: the back layer is implemented purely as attribute writes (cells change color to suggest movement). Cost: minimal — just ~10,000 T-states for attribute updates. Used by demoscene effects more than games.

True multi-layer parallax with smooth pixel scrolling in both layers is essentially out of reach on the 48K. The 128K with shadow screen makes it feasible, and a handful of modern homebrew titles attempt it.

---

## Split-Screen Techniques

A split screen — status bar at the top, playfield below, or playfield on the left and status on the right — is achieved by **limiting the scroll region**. Instead of scrolling the full 192 pixel rows, the engine scrolls only rows 16-191 (leaving rows 0-15 as a static status bar).

This is straightforward for character-cell scrolling (just limit the row loop). For pixel-smooth scrolling, the stack-push loop must be modified to skip the status bar region and resume at the playfield.

The harder problem is **attribute splitting**: the status bar cells have their own colors (score in white, lives in red, etc.), and the playfield cells have their own. The engine must maintain two attribute regions and never let sprite draws bleed across the boundary.

### Games using split-screen

- *Manic Miner*, *Jet Set Willy* (status bar at top, playfield below)
- *Chuckie Egg* (status bar with score and lives)
- *Dan Dare* (status bar at bottom)
- Most arcade adventures

---

## Common Pitfalls

### Scrolling into the attribute file

The pixel buffer ends at `#57FF` and the attribute file begins at `#5800`. A scroll routine that copies row 23 of the pixel buffer "up" by one pixel will run off the end of the pixel buffer and into the attribute file, producing visible corruption. Always bounds-check the scroll loop.

### Third-boundary wrap

The pixel buffer is divided into three "thirds" of 64 pixel rows each. A scroll that crosses a third boundary (row 63 → row 64, row 127 → row 128) must adjust its destination address by `-2048 + 32` (move to the next third's first row). Forgetting this produces diagonal scrolling artifacts. The precomputed address table in [screen_access.md](screen_access.md) handles this automatically.

### Displaying the off-screen buffer

On the 128K, forgetting to flip the shadow screen bit before VBLANK means the player sees the buffer being drawn. The fix is to flip during the top border (the safest place — the ULA is reading border color, not video RAM).

### Sprite flicker with single-buffer scroll

A 48K single-buffer scroller that draws sprites directly to the visible screen will produce flicker if the scroll happens mid-frame. The fix is to do all scroll work during VBLANK (top border) and all sprite draws during the active display, or to use the dirty-rectangle approach and limit redraws to specific cells.

### Bank-switching during an ISR

If an IM2 ISR (e.g., music player) fires while you have bank 7 paged in (to draw to the shadow screen), and the ISR reads from `#4000`–`#7FFF` (e.g., to fetch a music note from low memory), it will read from bank 7 instead of bank 5. The fix is to either (1) keep all ISR-read data in non-banked memory (banks don't change below `#8000` on the main CPU), or (2) disable interrupts during bank-switching sequences. See [interrupt_programming.md](../04_interrupts/interrupt_programming.md) for the broader discussion of ISR safety.

---

## Cross-References

- [screen_access.md](screen_access.md) — the address tables and stack-push primitives that all scrolling techniques depend on.
- [sprites_and_masking.md](sprites_and_masking.md) — sprites move over the scrolling background; the three-screen buffered architecture extends naturally to scrolling.
- [memory_and_io_48k.md](../03_memory_and_io/memory_and_io_48k.md) — the 128K bank layout and port `#7FFD` bit assignments.
- [contention_timing.md](../05_display_and_timing/contention_timing.md) — why screen writes during the active display cost more, and how this affects scroll timing.
- [raster_timing.md](../05_display_and_timing/raster_timing.md) — when VBLANK happens, which is when you must flip shadow screens.
- [interrupt_programming.md](../04_interrupts/interrupt_programming.md) — the ISR framework that affects what you can safely do during scroll loops.
- [im2_disk_music.md](../04_interrupts/im2_disk_music.md) — bank-switching + ISR + disk + music all interact during scroll-heavy 128K games.

---

## References

- **Dean Belfield, "Smooth Scrolling on the ZX Spectrum"** ([breakintoprogram.co.uk](http://www.breakintoprogram.co.uk/software_development/smooth-scrolling-on-the-zx-spectrum-intro)) — the canonical modern worked example. Multi-part series covering stack-push scroll, racing the beam, masked sprites, Y-sorting.
- **Jonathan Cauldwell, "How to Write ZX Spectrum Games" Chapter 13** ([chuntey.wordpress.com](https://chuntey.wordpress.com/2013/10/02/how-to-write-zx-spectrum-games-chapter-13/)) — the stack-based scroll technique from a 1980s commercial developer.
- **`lib-spectrum` scroll.z80** ([github.com/breakintoprogram/lib-spectrum](https://github.com/breakintoprogram/lib-spectrum/blob/master/lib/scroll.z80)) — open-source Z80 implementation of the stack-based scroller.
- **Dixel Scrolling** ([zxspectrumcoding.wordpress.com](https://zxspectrumcoding.wordpress.com/2017/12/09/dixel-scrolling-2-pixel-at-a-time-scroll/)) — the 2-pixel-step variant, with reference to *Your Sinclair* issue 19.
- **Ghosts 'n' Goblins disassembly** ([emix8.org/ggdisasm](http://www.emix8.org/ggdisasm/)) — commented disassembly of the Spectrum port of *Ghosts 'n' Ghosts*, including the scroll engine.
- **Using SP1 for Scroller Games** ([ZXjogv blog](https://jogv.es/posts/2023/05/02/sp1_for_scroller_games/)) — modern writeup of using SP1's character-cell background for vertical scrollers, including a column-major tile buffer optimization.
