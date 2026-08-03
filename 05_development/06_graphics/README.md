[← Plan](../../PLAN.md) · [Graphics](README.md)

# Development — Graphics Techniques

This series covers ZX Spectrum graphics programming from the ground up: the foundational screen access primitives, software sprites and masking, scrolling and double buffering, multicolor engines that break the 8×8 attribute grid, 3D graphics (wireframe, filled-polygon, isometric, raycasting), and the ZX Spectrum Next's hardware-accelerated graphics layers.

The series is organized by **visual problem** rather than by hardware capability. Articles 1–3 cover the techniques that every stock-Spectrum game uses. Article 4 extends those techniques with raster-synchronized multicolor engines. Article 5 covers 3D graphics in all its forms. Article 6 covers the Spectrum Next, where most of the techniques in articles 1–4 become optional.

## Reading Order

| # | Article | Description |
|---|---|---|
| 1 | [screen_access.md](screen_access.md) | Foundational primitives: address lookup tables (pixel + attribute), fast clear via stack push, block copy, custom font rendering, viewport clipping |
| 2 | [sprites_and_masking.md](sprites_and_masking.md) | Software sprites: compositing modes (XOR/OR/LOAD/MASK), pre-shifted sprites, masked sprite layout, three-screen buffered drawing, sprite pools, engine surveys (SP1, AGD/MPAGD) |
| 3 | [scrolling_and_buffering.md](scrolling_and_buffering.md) | Scrolling: character-cell scroll, pixel-smooth horizontal scroll (stack-push, 25 Hz two-frame cycle), 128K shadow screen double buffering, dirty rectangle, parallax, split-screen |
| 4 | [multicolor_engines.md](multicolor_engines.md) | Engines that break the 8×8 attribute constraint: BIFROST* (8×1), NIRVANA+ (8×2), ZXodus, ULAplus (64-color hardware palette), Timex HiColor/HiRes, decision matrix |
| 5 | [3d_graphics.md](3d_graphics.md) | 3D on the Z80: fixed-point math, rotation matrices, Bresenham line drawing, wireframe (*Elite*), filled polygons (*Driller*/Freescape, 3D Construction Kit), isometric (Filmation/*Knight Lore*), raycasting, performance budgets |
| 6 | [next_graphics.md](next_graphics.md) | ZX Spectrum Next: layer stack, Layer 2 (256-color framebuffer), hardware sprites, tilemap, copper coprocessor, mixing-layer architectures, CPU at 28 MHz |

## Cross-Reference Table

| This series | Canonical reference |
|---|---|
| [screen_access.md](screen_access.md) | [screen_layout.md](../03_memory_and_io/screen_layout.md), [color_system.md](../05_display_and_timing/color_system.md) |
| [sprites_and_masking.md](sprites_and_masking.md) | [asset_tools.md](../../09_toolchain/asset_tools.md), [game_reversing.md](../../08_reverse_engineering/game_reversing.md) |
| [scrolling_and_buffering.md](scrolling_and_buffering.md) | [bank_switching_patterns.md](../03_memory_and_io/bank_switching_patterns.md), [ula_timing.md](../../02_hardware/original/ula_timing.md) |
| [multicolor_engines.md](multicolor_engines.md) | [race_the_beam.md](../04_interrupts/race_the_beam.md), [multicolor_techniques.md](../../07_demoscene/multicolor_techniques.md) |
| [3d_graphics.md](3d_graphics.md) | [c_interop.md](../02_assembly/c_interop.md) (fixed-point), [effects_catalog.md](../../07_demoscene/effects_catalog.md) |
| [next_graphics.md](next_graphics.md) | [zx_next.md](../../02_hardware/newgen/zx_next.md), [video_frame_next.md](../05_display_and_timing/video_frame_next.md), [memory_and_io_next.md](../03_memory_and_io/memory_and_io_next.md), [im2_advanced.md](../04_interrupts/im2_advanced.md) |

> **Scope note**: Article 1 is the foundation — every later article assumes its address tables and stack-push primitives. Articles 2 and 3 are the 2D game-programming core. Article 4 is the **direct continuation** of [race_the_beam.md](../04_interrupts/race_the_beam.md) from the Interrupt Programming series — that article covers the raster-timing theory; this one covers the published engines. Article 5 covers 3D across all four visual styles (wireframe, filled, isometric, raycasting). Article 6 covers the Spectrum Next's hardware acceleration, which makes most techniques in articles 1–4 optional. The demoscene side of multicolor (effect-driven, not game-driven) is covered in [multicolor_techniques.md](../../07_demoscene/multicolor_techniques.md); this series focuses on the game-programmer perspective.
