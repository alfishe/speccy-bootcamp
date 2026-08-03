[← Plan](../../PLAN.md) · [Game Dev](README.md)

# Development — Game Development

This section covers ZX Spectrum game engine architecture: the per-frame loop, entity systems, collision, AI, level data, input, audio integration, and case studies of commercial engines.

For the related technique articles that this section builds on, see the [Graphics Techniques series](../06_graphics/README.md) (sprite primitives, scrolling, 3D), the [Interrupt Programming series](../04_interrupts/README.md) (ISR construction, raster sync), and the [Sound section](../../06_sound/README.md) (AY player architecture, SFX synthesis).

## Reading Order

| # | Article | Lines | Topic |
|---|---|---|---|
| 1 | [game_loop.md](game_loop.md) | 502 | Frame-synchronized loop architectures, HALT vs ISR-driven, game state machines, 48K vs 128K memory models, ROM/RAM layouts, load screens, debugging, pitfalls |
| 2 | [entities_collision_ai.md](entities_collision_ai.md) | 729 | Fixed-pool entity storage, update ordering, dual-phase erase/draw, AABB/grid/pixel/attribute collision, tile-world collision, FSMs, waypoint AI, steering, pathfinding |
| 3 | [level_data_and_worlds.md](level_data_and_worlds.md) | 413 | Four world models (single-screen, multi-room, scrolling, isometric), Manic Miner 1024-byte room format, persistent state, scroll camera, tile-map pipeline, compression, transitions |
| 4 | [input_sound_integration.md](input_sound_integration.md) | 435 | Input normalization across devices, edge detection, redefine-keys UI, ISR-driven music, SFX channel priority/stealing, memory budgets for music/SFX |
| 5 | [game_case_studies.md](game_case_studies.md) | 382 | Engine-by-engine analysis: *Manic Miner* (1983), *Jet Set Willy* (1984), *Knight Lore* (1984), *Alien 8* (1985), *Head Over Heels* (1987), *Elite* (1985) |

**Total: 5 articles, 2,461 lines.**

## Cross-Reference Table

| This section | Canonical reference elsewhere |
|---|---|
| game_loop.md §1 | [interrupt_programming.md](../04_interrupts/interrupt_programming.md) — ISR construction |
| game_loop.md §2 | [video_frame_overview.md](../05_display_and_timing/video_frame_overview.md) — frame timing |
| entities_collision_ai.md §6 | [sprites_and_masking.md](../06_graphics/sprites_and_masking.md) — sprite rendering |
| level_data_and_worlds.md §2 | [asset_tools.md](../../09_toolchain/asset_tools.md) — tile-map authoring tools |
| level_data_and_worlds.md §6 | [compression_packing.md](../../07_demoscene/compression_packing.md) — ZX0/MegaLZ/RCS |
| input_sound_integration.md §1 | [joystick.md](../../03_io/peripherals/joystick.md) — joystick hardware |
| input_sound_integration.md §4-5 | [ay_player_routines.md](../../06_sound/players/ay_player_routines.md) — music player internals |
| game_case_studies.md §3-5 | [3d_graphics.md](../06_graphics/3d_graphics.md) — isometric math |
| game_case_studies.md §6 | [3d_graphics.md](../06_graphics/3d_graphics.md) §2-4 — wireframe 3D math |

## Scope Note

This section follows the **F12 consolidation pattern** (one comprehensive article per major topic) rather than the original PLAN.md's 9-article breakdown. The 5 articles here cover all the planned topics with explicit cross-references to canonical treatments elsewhere, avoiding duplication of:
- Sprite rendering primitives (covered in F12 `sprites_and_masking.md`)
- Scrolling and buffering techniques (covered in F12 `scrolling_and_buffering.md`)
- Input device hardware (covered in `03_io/peripherals/joystick.md`)
- Music player internals (covered in `06_sound/players/ay_player_routines.md`)
- Asset authoring tools (covered in `09_toolchain/asset_tools.md`)
- 3D rendering math (covered in F12 `3d_graphics.md`)
