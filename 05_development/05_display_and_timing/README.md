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
