[← Home](../../README.md) · [Display & Timing](README.md)

# Development — Video Subsystem

Video frame generation, per-model timing, raster synchronization, contention, floating bus, and color systems.

| Article | Description |
|---------|------------|
| [video_frame_overview.md](video_frame_overview.md) | PAL timing fundamentals, ULA frame cycle, contentious vs non-contentious time, T-state budget per frame |
| [video_frame_48k.md](video_frame_48k.md) | 48K frame: complete T-state map, contention pattern (6-5-4-3-2-1-0-0), floating bus, performance budget |
| [video_frame_128k.md](video_frame_128k.md) | 128K/+2 frame: odd-bank contention, shadow screen timing, floating bus differences, 48K vs 128K comparison |
| [video_frame_pentagon.md](video_frame_pentagon.md) | Pentagon frame: 320 scanlines, binary counter, zero contention, 48.83 Hz frame rate, runtime detection |
