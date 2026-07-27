[← Home](../../README.md) · [Display & Timing](README.md)

# Development — Video Subsystem

Video frame generation, per-model timing, raster synchronization, contention, floating bus, and color systems.

| Article | Description |
|---------|------------|
| [video_frame_overview.md](video_frame_overview.md) | PAL timing fundamentals, ULA frame cycle, contentious vs non-contentious time, T-state budget per frame |
| [video_frame_48k.md](video_frame_48k.md) | 48K frame: complete T-state map, contention pattern (6-5-4-3-2-1-0-0), floating bus, performance budget |
| [video_frame_128k.md](video_frame_128k.md) | 128K/+2 frame: odd-bank contention, shadow screen timing, floating bus differences, 48K vs 128K comparison |
| [video_frame_pentagon.md](video_frame_pentagon.md) | Pentagon frame: 320 scanlines, binary counter, zero contention, 48.83 Hz frame rate, runtime detection |
| [video_frame_plus2a_plus3.md](video_frame_plus2a_plus3.md) | +2A/+3 frame: Amstrad gate array contention (1-0-7-6-5-4-3-2), different contended banks, no I/O contention, porting checklist |
| [floating_bus.md](floating_bus.md) | Floating bus per-model behavior: 48K reference pattern, 128K compatibility, +2A/+3 unreliable, Pentagon absent, raster sync usage |
| [raster_timing.md](raster_timing.md) | Beam position calculation, HALT-based sync, scanline-precise delays, per-model raster maps, cross-platform sync strategy |
| [color_system.md](color_system.md) | Attribute byte format, 8-color palette (normal/bright), ULA hardware color generation, reference palettes, attribute clash, ULAplus 64-color extension, Timex HiColor/HiRes modes |
| [border_effects.md](border_effects.md) | Border color via #FE, raster bars, rainbow borders, per-model timing, safe border writes, gradient effects |
| [clone_video_modes.md](clone_video_modes.md) | Clone-specific video modes beyond standard ULA: GigaScreen, ATM Turbo hires, Profi 512×256, Kay CPLD modes, TS-Conf |
| [video_frame_scorpion.md](video_frame_scorpion.md) | Scorpion ZS-256 frame: 312 lines matching 48K macro timing, +9 T horizontal shift, revision-dependent contention, 7 MHz turbo |
| [video_frame_other_soviet.md](video_frame_other_soviet.md) | Long-tail Soviet clones: Kay 1024 (48K-clean), ATM Turbo (7 MHz anomaly: 99,880 T-states), Profi (paper offset T=12,580), Byte, Quorum, Leningrad, LEC |
| [video_frame_next.md](video_frame_next.md) | ZX Spectrum Next: configurable timing modes (48K/128K/+2A/Pentagon), 4 CPU speeds (3.5/7/14/28 MHz), copper coprocessor (WAIT/MOVE/STOP) |
| [video_frame_sprinter.md](video_frame_sprinter.md) | Peters Plus Sprinter: SVGA 70 Hz frame (not PAL 50 Hz), 20 MHz Z80, 5 video modes, music tempo 40% faster |
| [video_frame_zxevo.md](video_frame_zxevo.md) | ZX Evolution (PentEvo): real Z80 + Altera MAX CPLDs, Pentagon-compatible base timing, BaseConf vs TS-Conf configurations |
| [contention_timing.md](contention_timing.md) | Per-T-state delay tables (Ferranti 6-5-4-3-2-1-0-0, Amstrad 1-0-7-6-5-4-3-2), per-instruction contended cost tables, I/O contention |
| [interlace_and_flicker.md](interlace_and_flicker.md) | Spectrum's non-interlaced output, 50 Hz perception threshold, attribute flicker, GigaScreen flicker math, CRT vs LCD behaviour |
| [crt_output.md](crt_output.md) | Software developer's view of CRT/LCD output: pixel aspect ratio, overscan, composite artifacts, per-display-type behaviour |
| [video_frame_comparison.md](video_frame_comparison.md) | Synthesis: all models side-by-side — T-states/frame, scanlines, contention pattern, turbo, compatibility matrix, detection decision tree |
