[← Home](../../README.md) · [Development](../../README.md)

# Development — Interrupt Programming

This directory covers ZX Spectrum interrupt programming from a practical standpoint: IM1/IM2 setup, ISR design patterns, timing constraints, and cookbook examples.

## Articles

| Article | Topic |
|---------|-------|
| [interrupt_programming.md](interrupt_programming.md) | Practical guide: IM1/IM2 setup, ISR patterns, timing, cookbook, antipatterns |

## Planned

- `race_the_beam.md` — Raster-synchronized programming for multicolor effects
- `nmi.md` — NMI handling: Multiface, NMI button, safe context

The CPU-level interrupt architecture (IFF1/IFF2, bus cycles, acknowledge timing) is covered in [z80_interrupts.md](../../01_cpu/z80_interrupts.md).
