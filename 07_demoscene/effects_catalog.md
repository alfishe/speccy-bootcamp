[← Home](../README.md) · [Demoscene](README.md)

# Visual Effects Catalog

> **Status**: Stub — article not yet written

A comprehensive catalog of demoscene visual effects on the ZX Spectrum — from plasma and zoomers to raycasting, 3D objects, tunnel effects, and copper bars — with implementation notes for each.

---

## Planned Content

- **Plasma**: color-cycling attribute effects, trigonometric color interpolation
- **Zoomers / rotazers**: scaling and rotating images, frame timing tricks
- **Raycasting**: pseudo-3D environments, column casting, texturing
- **3D objects**: wireframe, filled polygon sorting, Z-buffer approximation
- **Tunnel effects**: polar coordinate rendering, precomputed distance tables
- **Copper bars / raster bars**: border and screen color timing effects
- **Twisters / rotating objects**: perspective tricks
- **Starfields**: 2D and 3D star projections
- **Vector scrolling**: smooth hardware-impossible scroll via CPU timing
- **Particle systems**: dots, points, fire effects
- **Texture mapping**: floor/ceiling, walls
- Per-effect: technique summary, T-state budget, known limitations

---

## Cross-References

- [Multicolor Techniques](multicolor_techniques.md) — the foundation for many effects
- [Precalc Trigonometry](precalc_trigonometry.md) — math tables used by effects
- [ULA Timing](../02_hardware/original/ula_timing.md) — timing constraints for effects
- [Race the Beam](../05_development/04_interrupts/race_the_beam.md) — cycle-exact timing
