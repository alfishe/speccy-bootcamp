[← Home](../README.md) · [Demoscene](README.md)

# Multicolor Techniques — 8x1 and 8x2 Color Resolution

> **Status**: Stub — article not yet written

The ZX Spectrum's attribute system limits color to 8×8 pixel blocks. "Multicolor" (also called "attribute interrupt" or "race the beam") exploits cycle-exact timing to change attributes mid-scanline, achieving 8×1 or 8×2 color resolution.

---

## Planned Content

- The constraint: 8×8 attribute cells, why they exist, color clash
- 8×2 multicolor: changing INK/PAPER every 2 scanlines within a character row
- 8×1 multicolor (ULApixel / "chrominance"): changing attributes every scanline
- Timing math: exact T-state count per attribute change, contention window
- Per-model differences: 48K ULA timing, 128K timing, Pentagon timing
- Practical implementation: ISR setup, timing loop, attribute write sequence
- The "floating bus" technique: using IN A,(#FF) for raster synchronization
- Multicolor engines: managing double buffering, bank switching, timing tables
- Performance budget: how much CPU time is consumed per multicolor frame
- Limitations: not possible on +2A/+3 (different contention model)
- ULAplus: hardware 64-color palette as modern alternative

---

## Cross-References

- [ULA Timing](../02_hardware/original/ula_timing.md) — contention windows (prerequisite)
- [Video Frame 48K](../05_development/05_display_and_timing/video_frame_48k.md) — scanline timing
- [Contention Model](../05_development/03_memory_and_io/contention_model.md) — per-model differences
- [Race the Beam](../05_development/04_interrupts/race_the_beam.md) — timing fundamentals
- [Floating Bus](../05_development/05_display_and_timing/floating_bus.md) — raster sync technique
