[← Game Dev](README.md) · [Level Data and Worlds](level_data_and_worlds.md)

# Level Data and World Architectures — From Single Screens to Streaming Worlds

> **Scope**: This article covers how ZX Spectrum games store, structure, and render their worlds. It is the bridge between the **authoring tool** (Tiled, ZX Paintbrush, SevenUp — see [asset_tools.md](../../09_toolchain/asset_tools.md)) and the **game engine** (see [game_loop.md](game_loop.md), [entities_collision_ai.md](entities_collision_ai.md)).

For *which tools produce level data*, see [asset_tools.md](../../09_toolchain/asset_tools.md). For *how the engine resolves tile collisions against that data*, see [entities_collision_ai.md](entities_collision_ai.md) §4. This article covers what sits in between: the **world-model architecture** — single screen, scrolling, isometric, stage-based — and the **storage formats** each one implies.

---

## Article Roadmap

- §1 — The four canonical world models
- §2 — Single-screen rooms: the *Manic Miner* 1024-byte format as canonical example
- §3 — Multi-room games: *Jet Set Willy*'s persistent-room model
- §4 — Scrolling worlds: 1-direction, 2-direction, and the camera problem
- §5 — Tile-map storage and rendering pipeline
- §6 — Compression strategies for level data
- §7 — Room/screen transitions

---

## 1. The Four Canonical World Models

Almost every ZX Spectrum game fits one of these architectural templates:

| Model | Example | Room storage | Camera | Scrolling |
|---|---|---|---|---|
| **Single screen, single room** | *Manic Miner* (1983), *Chuckie Egg* (1983) | 1 KB per room | Fixed | None |
| **Single screen, multi-room** | *Jet Set Willy* (1984), *Knight Lore* (1984) | 1–2 KB per room, persistent state | Fixed | None (rooms connected by portals) |
| **Side-scrolling** | *Green Beret*, *Combat School*, *Dizzy* series | Tile map per stage, often compressed | Follows player | 1-direction (horizontal) |
| **Top-down / isometric** | *Head Over Heels*, *Batman*, *Alien 8* | Object-list per room | Fixed or per-room | None |

The world model determines **everything else** about the engine: how entities are stored, how collision works, how the renderer is structured. *Manic Miner* and *Green Beret* are entirely different engines despite both being platformers, because their world models differ.

The choice of world model is forced primarily by **memory**: a single-screen room fits comfortably in 1 KB, so a 48K game can hold 20 rooms in 20 KB and still have 4 KB for the engine. A scrolling world requires a tile map of the entire stage, which is much larger — typically 4–32 KB per stage, forcing either 128K banking or per-stage disk loading.

---

## 2. Single-Screen Rooms — The Matthew Smith Format

The most-copied level format in ZX Spectrum history is the one Matthew Smith designed for *Manic Miner* (1983). It is 1024 bytes per room, broken into fixed sub-regions:

### The 1024-byte room layout

| Offset | Size | Contents |
|---|---|---|
| 0–511 | 512 bytes | Screen-layout: 16 rows × 32 columns of attribute bytes (one byte per 8×8 cell) |
| 512–543 | 32 bytes | Room name (ASCII, padded with spaces) |
| 544–615 | 72 bytes | Block-graphics: 9 tiles × 8 bytes each (8×8 pixel patterns) |
| 616–622 | 7 bytes | Miner Willy start position and animation state |
| 623–626 | 4 bytes | Conveyor direction and animation position |
| 627 | 1 byte | Border color |
| 628–654 | 27 bytes | Items: 5 items × 5 bytes each + sentinel |
| 655–691 | 37 bytes | Portal (exit) definition and animation |
| 692–699 | 8 bytes | Item graphic (8×8 sprite) |
| 700–701 | 2 bytes | Air supply (oxygen countdown) |
| 702–732 | 31 bytes | Horizontal guardians: up to 4 × 7 bytes + sentinel |
| 733–760 | 28 bytes | Vertical guardians: up to 4 × 7 bytes + sentinel |
| 736–767 | 32 bytes | Special graphic (Eugene, Sky-Bird, etc.) — overlaps with vertical guardians in rooms that have them |
| 768–1023 | 256 bytes | Guardian-graphics: 16 sprites × 16 bytes each |

Total: 1024 bytes per room, packed into 20 KB for the full game's 20 rooms.

### Why the format is brilliant

The genius of Matthew Smith's design is **the screen layout IS the collision data**. Each byte in offsets 0–511 is the attribute byte of an 8×8 cell on the visible screen. The engine reads the cell at the player's current position to determine collision: certain ink colors mean solid wall, others mean floor, others mean deadly hazard, others mean conveyor.

```z80
; Check if cell at (B=x/8, C=y/8) is a wall
is_wall:
        ; Compute address in screen layout
        LD    A,C
        RRCA / RRCA / RRCA           ; Y * 32 (multiply by 32 via shifts)
        AND  #60                      ; Mask to char-row bits
        OR    B                       ; Add column
        LD    L,A
        LD    H,room_data / 256       ; High byte of current room's data
        LD    A,(HL)                  ; Read attribute byte
        ; Compare against wall color(s)
        CP    ATTR_WALL
        RET
```

No separate tile map. No separate collision layer. The screen layout is one data structure that does triple duty: it determines **what the player sees** (the rendered background), **what the player can stand on** (the collision data), and **what colors each cell has** (the attribute file).

### The trade-off

The trade-off is **everything is at 8×8 granularity**. The player cannot stand on a 4-pixel-wide ledge. The player's collision box is at least 8 pixels wide. The player's horizontal position snaps to 8-pixel increments for some purposes (such as entering a portal) even though the rendered position can be any pixel.

This trade-off is acceptable for *Manic Miner*'s blocky, grid-based design. It is not acceptable for *Knight Lore*, which uses a completely different world model (see Section 4 of [game_case_studies.md](game_case_studies.md)).

### How the format was copied

*Jet Set Willy* (1984) extends the format to 2048 bytes per room (adds a second screen-layout for the persistent-room-state tracking, plus more guardian slots). *Chuckie Egg*, *Pyjamarama*, *Everyone's a Wally*, and dozens of other 1983–1986 platformers use variants of the same idea. By the late 1980s, the format is the de facto standard for single-room Spectrum games.

---

## 3. Multi-Room Games and Persistent State

*Manic Miner* has 20 rooms but each is independent: when the player exits a room and re-enters, the room resets to its initial state (items reappear, guardians return to their starting positions). This is the simplest possible model.

*Jet Set Willy* introduces **persistent room state**: when the player exits a room, the room's current state (which items have been collected, which guardians have moved where, which tiles have changed) is preserved. Re-entering the room restores that state.

### The implementation trick

Each room has two data blocks: an **immutable template** (the 1024-byte Matthew Smith format) and a **mutable state block** (~256 bytes holding only the things that change). When the player enters a room, the engine copies the template into a working buffer, then applies the state-block patches. When the player leaves, the working buffer's mutable parts are saved back into the state block.

```z80
; Enter room N
enter_room:
        ; Copy template to working buffer
        LD    HL,room_templates
        LD    DE,room_buffer
        LD    BC,1024
        LDIR                           ; Copy 1024 bytes
        ; Apply state patches (items collected, etc.)
        LD    A,(current_room)
        CALL  apply_state_patches      ; Overwrite parts of room_buffer
        ; Now render the room from room_buffer
        CALL  render_room
        RET
```

The state block holds:
- A bitmap of collected items (1 bit per item, so 5 items = 1 byte)
- Modified tile attributes (e.g., a wall that the player has destroyed)
- Modified guardian positions (rare — usually guardians reset to initial positions)

This pattern is what *Head Over Heels*, *Alien 8*, *Batman*, and every persistent-room Spectrum game uses, with variations.

---

## 4. Scrolling Worlds — The Camera Problem

A scrolling world is fundamentally different from a single-screen game: the world is larger than the visible area, and a **camera** selects which portion to render. The camera's position changes per frame as the player moves.

### Direction-constrained scrolling

The simplest scrolling model is **horizontal-only**: the camera tracks the player's X position but the Y position is fixed. *Green Beret*, *Hypaball*, *Combat School*, and most run-and-gun Spectrum games use this. The camera follows the player with a small deadzone (the player can move freely within the center ~64 pixels of the screen without scrolling); when the player exits the deadzone, the camera scrolls to catch up.

```z80
update_camera:
        ; Read player X
        LD    A,(player_x)
        ; Camera target = player_x - 128 (keep player in center)
        SUB   128
        ; Clamp to world bounds
        JR    NC,.x_ok
        XOR   A                        ; Player near left edge: camera = 0
.x_ok:
        LD    B,A
        LD    A,(world_width)
        SUB   255                      ; world_width - 255 (last visible camera position)
        CP    B
        JR    C,.x_clamp_right
        LD    A,B
        JR   .x_done
.x_clamp_right:
        LD    A,(world_width)
        SUB   255
.x_done:
        LD    (camera_x),A
        RET
```

Rendering then translates every entity's world position to a screen position by subtracting `camera_x`. Entities with `world_x < camera_x` or `world_x > camera_x + 255` are off-screen and skipped.

### Bidirectional scrolling

Bidirectional scrolling (camera tracks both X and Y) is rarer on the Spectrum because it requires either a much larger screen buffer or constant repainting of the visible area. *Starquake*, *Fred*, and *Daley Thompson's Super-Test* use it. The cost is roughly 2× that of single-direction scrolling.

### The single-pixel scroll problem

The ZX Spectrum's screen is organized as 8×8 attribute cells. Scrolling by 8 pixels at a time (one cell) is cheap: just shift which cells are visible. Scrolling by 1 pixel at a time requires rewriting the **pixel buffer** (`#4000`–`#57FF`) every frame, which is expensive. See [scrolling_and_buffering.md](../06_graphics/scrolling_and_buffering.md) for the techniques.

The standard solution is **scrolling in raster sync**: during the visible frame, the engine reads the next column of pixels from the world map and writes them into the screen buffer at the column that is about to become visible. This must complete before the raster reaches that column — typically giving a budget of ~224 T-states per scanline × 192 scanlines = ~43,000 T-states total for the scroll, leaving ~26,000 for everything else.

For more on this, see [scrolling_and_buffering.md](../06_graphics/scrolling_and_buffering.md). This article only covers the **data structures** that scrolling requires.

### Tile-map format for scrolling games

A scrolling world needs a tile map covering the entire stage. The format is typically:

```
stage_1_map:
        DB  stage_width / 8             ; Width in tiles (e.g., 64 for 512-pixel wide stage)
        DB  stage_height / 8            ; Height in tiles (e.g., 24 for 192-pixel tall)
        ; Tile indices, row-major:
        DB  1,1,1,1,1,1,1,1,...         ; First row of tiles
        DB  0,0,0,0,2,2,0,0,...         ; Second row
        ; ... etc ...
```

Each byte is a tile index (0–255), selecting which 8×8 pixel pattern to draw at that position. The tile patterns themselves live in a separate `tile_patterns` table (256 entries × 8 bytes = 2 KB for a full tile set).

For a 512×192 stage, the map is 64 × 24 = 1,536 bytes. For a 1024×192 stage, 3,072 bytes. Stages larger than ~4 KB are typically compressed (see Section 6).

---

## 5. Tile-Map Storage and Rendering Pipeline

The tile map describes *what* to draw; the rendering pipeline turns that into pixels on screen. The pipeline has three stages, each with its own cost profile.

### Stage A — Background generation (per-room or per-stage)

For a single-screen room game, this happens once when the player enters a room: the engine reads the room's screen-layout (the 512-byte attribute table from Section 2) and writes the corresponding tile patterns into the screen buffer. Cost: ~30,000 T-states for a full screen of 192 8×8 tiles. Done in one frame, then never touched again while the player is in the room.

For a scrolling game, this happens continuously: each frame, the engine must draw the new column or row that has scrolled into view. Cost: ~224 T-states per scanline × 192 scanlines = ~43,000 T-states total for a full screen redraw, but in practice only a small portion of the screen changes per frame.

### Stage B — Attribute file generation

The Spectrum's attribute file at `#5800`–`#5AFF` carries the ink/paper colors. For a tile-based game, this is generated from the tile map at the same time as the pixel buffer:

```z80
; For each visible tile (col, row):
generate_attr:
        LD    A,(tile_attr_table)     ; Pre-computed: ink/paper per tile index
        LD    (HL),A                  ; HL = attribute file address
        RET
```

The `tile_attr_table` is a 256-byte lookup table indexed by tile index: each entry is the attribute byte for that tile. Cost: ~10 T-states per tile, ~5,000 T-states per screen.

### Stage C — Sprite overlay

After the background is drawn, entities are drawn on top. This is the software-sprite pass, covered in [sprites_and_masking.md](../06_graphics/sprites_and_masking.md). The cost depends on sprite count and size, but typically 15,000–25,000 T-states for a busy screen.

### Total per-frame render budget

| Component | Single-screen room | Scrolling game |
|---|---|---|
| Background redraw | 0 (only on room enter) | ~20,000 T-states (partial) |
| Attribute update | 0 (only on room enter) | ~3,000 T-states |
| Sprite erase | ~8,000 T-states | ~8,000 T-states |
| Sprite draw | ~15,000 T-states | ~15,000 T-states |
| **Total** | **~23,000 T-states** | **~46,000 T-states** |

A scrolling game has roughly **2× the render cost** of a single-screen game. This is why scrolling games on the 48K Spectrum are visually simpler than single-screen games — the budget for sprites, AI, and effects is squeezed by the constant background work.

---

## 6. Compression Strategies for Level Data

Level data is the single largest memory consumer in most ZX Spectrum games. *Manic Miner* uses 20 KB of its 24 KB code/data budget for levels. Compression is essential for any game with more than ~10 rooms or a stage longer than ~3 KB.

### Strategy 1 — Run-length encoding (RLE)

The simplest compression for level data. Each run of identical tile indices is encoded as (count, tile_index):

```
Raw tile data:    1,1,1,1,1,1,1,1,2,2,2,2,3,3,3,3,3,3,3,3   (20 bytes)
RLE-encoded:      8,1, 4,2, 8,3                                  (6 bytes)
```

Compression ratio: 70% for typical level data with long horizontal runs of the same tile. Depacker cost: ~10 T-states per output byte.

### Strategy 2 — Column-major traversal + LZ

The Spectrum's screen has a non-linear layout: bytes that are vertically adjacent in a tile (one pixel apart) are 256 bytes apart in memory. Level data for the screen-layout format inherits this property if it is stored as a flat 512-byte array. A general-purpose LZ packer (ZX0, MegaLZ) compresses this poorly because it cannot see the spatial locality.

The fix: **reorder the data column-major before packing**. The [RCS tool](https://github.com/einar-saukas/rcs) (Reorder Code System) by Einar Saukas does this for screen data; the same idea works for level data. See [compression_packing.md](../../07_demoscene/compression_packing.md) §11 for the technique.

### Strategy 3 — Tile-attribute separation

Instead of storing the full attribute byte for each cell, split the data into two streams:

1. **Tile indices** (one byte per cell, 256 tile types possible)
2. **Attribute deltas** (only where the default attribute for a tile is overridden)

For most rooms, 90%+ of cells use the default attribute for their tile type. The deltas are stored as a small list of (cell_index, attribute_byte) pairs, typically 5–20 entries per room. Total cost: tile_indices (256 bytes) + deltas (~30 bytes) = ~286 bytes per room vs. 512 bytes uncompressed.

### Strategy 4 — Per-stage packing with disk loading

On 128K machines with disk, the standard pattern is to **pack each stage with ZX0** and load it on demand:

```z80
; Player entered stage 3: load and depack stage 3 data
load_stage_3:
        ; Page in bank 6 at #C000
        LD    A,6 | %00010000
        LD    BC,#7FFD
        OUT   (C),A
        ; Load packed data from disk into bank 6
        LD    HL,filename_stage3
        CALL  trdos_load_file
        ; Depack into the level buffer
        LD    HL,#C000                ; Source: packed data in bank 6
        LD    DE,level_buffer         ; Destination: work buffer
        CALL  dzx0_standard
        ; Page out bank 6
        LD    A,(saved_bank)
        OUT   (C),A
        RET
```

This allows arbitrarily large games. The cost is a 1–2 second loading pause when the player transitions between stages, masked by a loading screen.

For the packer and depacker implementations, see [compression_packing.md](../../07_demoscene/compression_packing.md). This article does not duplicate that content.

---

## 7. Room and Screen Transitions

The transition between rooms (in single-screen games) or stages (in scrolling games) is its own architectural concern. The transition must:

1. Save the current room's mutable state (if persistent)
2. Load the new room's data (from RAM or disk)
3. Generate the new room's background (write tile patterns to the screen buffer)
4. Reset the entity pool (despawn all entities from the old room, spawn entities for the new room)
5. Position the player at the entry point
6. Optionally play a transition animation (fade, wipe, scroll)

### The instant transition (most common)

The simplest transition: the screen goes black for one frame while the new room is built, then appears fully rendered. Cost: one frame of "black" (the screen buffer is being rewritten), then the new room is visible. *Manic Miner*, *Chuckie Egg*, and most early platformers use this.

```z80
transition_to_room:
        ; Call with A = new room number
        LD    (current_room),A
        ; Save current room state
        CALL  save_room_state
        ; Load new room template
        LD    HL,room_table
        ; ... compute address of room A's template ...
        ; Copy 1024 bytes into working buffer
        LD    DE,room_buffer
        LD    BC,1024
        LDIR
        ; Apply state patches (collected items, etc.)
        CALL  apply_room_state
        ; Render the room
        CALL  render_room_background
        ; Reset entity pool
        CALL  clear_entity_pool
        CALL  spawn_room_entities
        ; Position player
        LD    A,(room_buffer + PLAYER_START_X_OFFSET)
        LD    (player_x),A
        LD    A,(room_buffer + PLAYER_START_Y_OFFSET)
        LD    (player_y),A
        RET
```

The transition completes within a single frame. The next frame's main loop continues normally with the new room visible.

### The animated transition (rarer)

Some games animate the transition with a fade or wipe, taking 8–32 frames (~160–640 ms) before the new room is fully visible. *Knight Lore* rotates the room into view; *Head Over Heels* uses a short fade. The animation is purely cosmetic — the data loading and entity spawning happen in the first frame; the fade just hides the jarring "pop" of the new room.

### Stage transitions in scrolling games

For scrolling games, "transitions" are continuous: as the player moves right, the camera follows, and new tiles scroll in from the right edge. There is no discrete "room transition" moment — but there is often a discrete "stage transition" when the player reaches the end of a stage and moves to the next. This is handled like a single-screen room transition (above), but with the additional cost of resetting the camera position to the start of the new stage.

---

## 8. Cross-References

- [game_loop.md](game_loop.md) — The transition between rooms is implemented as a state change in the game loop's top-level FSM.
- [entities_collision_ai.md](entities_collision_ai.md) §4 — How the engine uses tile-attribute data for collision. The level data described here is what the collision routines read.
- [sprites_and_masking.md](../06_graphics/sprites_and_masking.md) — Sprite drawing. Entities live on top of the level data.
- [scrolling_and_buffering.md](../06_graphics/scrolling_and_buffering.md) — The single-pixel scroll technique, double-buffering, dirty rectangles. This article covers what data is being scrolled; that article covers how.
- [asset_tools.md](../../09_toolchain/asset_tools.md) — The tools that produce tile maps (Tiled), sprite patterns (SevenUp, ZX Paintbrush), and tile-pattern editors. This article assumes the assets are already produced.
- [compression_packing.md](../../07_demoscene/compression_packing.md) — The ZX0, MegaLZ, and RCS packers used for level data compression (Section 6 of this article).
- [game_case_studies.md](game_case_studies.md) — How *Manic Miner*, *Jet Set Willy*, *Knight Lore*, and *Head Over Heels* implement the world models described here.
- [beta_disk_interface.md](../../03_io/storage/beta_disk_interface.md) — Disk loading via TR-DOS, used in per-stage disk loading (Section 6.4).

---

## 9. Common Pitfalls

### Pitfall 1 — Room data larger than the engine budget

A common mistake in early development: designing rooms with so much unique graphics data that the engine cannot fit 20 rooms in 24 KB. Always budget the room format before designing rooms. *Manic Miner* fits 20 rooms in 20 KB because each room has at most 9 unique tiles, 5 items, 8 guardians, and 256 bytes of sprite data. If you need more unique content per room, you need a different world model (probably multi-load or 128K banking).

### Pitfall 2 — Persistent state not properly saved

If the player exits a room without the state being saved, re-entering the room shows the initial state (items respawned, guardians reset). This breaks the player's expectation: they remember collecting the item, but it is back. Always call `save_room_state` in the transition function.

### Pitfall 3 — Scroll edge cases

When the camera is at the world's left edge (camera_x = 0) and the player moves further left, the camera must not scroll past 0. Conversely, when the camera reaches `world_width - 255`, it must stop. Forgetting the clamp produces a camera that pans past the world boundary, showing garbage memory as if it were level data.

### Pitfall 4 — Tile-attribute mismatch

If the tile map says cell (10, 5) is tile type 3, but the `tile_attr_table` says tile type 3 has INK=BLUE while the actual pixel pattern for tile type 3 is RED, the screen shows a red tile with a blue border (the attribute file's INK value overrides the pixel pattern's color). Always verify that the tile attribute table matches the pixel patterns, or build the table at runtime from the patterns.

### Pitfall 5 — Compression ratios measured on the wrong data

Compression ratios vary dramatically by data type. A level made of long horizontal runs (a wall-heavy platformer) compresses 60% with RLE; a level with random noise (a maze with mixed tiles) compresses only 15%. Always measure on real level data, not on a synthetic test pattern. See [compression_packing.md](../../07_demoscene/compression_packing.md) §9 for benchmarking methodology.

### Pitfall 6 — Loading screen blocks the music

On 128K, if the loading-screen animation halts the main loop (for example, by holding DI during a disk read), the music player (typically in the ISR) is also blocked. The player hears a one-second silence during every stage transition. Solution: keep EI on during loading, design the loading animation around the disk's blocking periods, and verify in an emulator that music plays continuously through the transition.

---

## 10. References

- **Andrew Broad**, [*Manic Miner Room-Format*](https://www.icemark.com/dataformats/manic/mmformat.htm) — The canonical reference for the 1024-byte Matthew Smith format. Used as the primary source for Section 2 of this article.
- **John Elliott**, [*Jet Set Willy: The Disassembly*](https://www.icemark.com/dataformats/jsw/) — Includes the JSW room-format specification (2048 bytes per room, persistent state).
- **Richard Dymond (SkoolKit)**, [*Manic Miner* RAM disassembly](https://skoolkit.ca/disassemblies/manic_miner/) — Engine-level view of how the room data is interpreted.
- **Einar Saukas**, [*RCS — Reorder Code System*](https://github.com/einar-saukas/rcs) — The tool that linearizes screen-format data for better LZ compression.
- **Einar Saukas**, [*ZX0*](https://github.com/einar-saukas/zx0) — The optimal LZ packer; standard for level data compression in modern Spectrum development.
- **Jonathan Cauldwell**, *How to Write ZX Spectrum Games* (2008) — Practical guidance on room and stage design from a working developer.
- **World of Spectrum archives** — [Level data format references](https://worldofspectrum.org/faq/references/index.htm) for many commercial games; useful for reverse-engineering specific titles.

---

## License

This article is released under **Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0)**. You are free to share and adapt the material, provided you credit the original source and license derivative works under the same terms.
