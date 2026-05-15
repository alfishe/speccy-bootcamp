[← Home](../../README.md) · [Memory & I/O](README.md)

# Development — Memory Architecture and I/O

Memory maps, I/O port decoding, contention, screen layout, and bank switching. Articles are organized by **model** — each combining the memory map with the I/O ports that control it.

## Model-Specific Memory and I/O

| Article | Description |
|---------|------------|
| [memory_and_io_48k.md](memory_and_io_48k.md) | **16K/48K**: static memory map, ROM regions, screen buffer, system variables + #FE port (border, EAR, keyboard, beeper) |
| [memory_and_io_128k.md](memory_and_io_128k.md) | **128K/+2**: 8 RAM banks, #7FFD paging register, ROM switching, shadow screen, AY ports (#FFFD/#BFFD) |
| [memory_and_io_plus3.md](memory_and_io_plus3.md) | **+2A/+3**: Amstrad gate array, #1FFD extended control, 4 paging modes, true double buffering, +3 FDC ports |
| [memory_and_io_pentagon.md](memory_and_io_pentagon.md) | **Pentagon**: compatible baseline + #EFF7 extended paging (512K/1024K), Beta 128 FDC/TR-DOS, zero contention |
| [memory_and_io_next.md](memory_and_io_next.md) | **ZX Spectrum Next**: 2 MB MMU with 8 KB pages, 8 MMU slots, compatibility modes, Layer 2/sprite/copper/DMA ports |

## Cross-Model References

| Article | Description |
|---------|------------|
| [io_port_decoding.md](io_port_decoding.md) | **I/O port concepts**: partial decoding, decoding masks, port mirrors, conflicts, cross-model port differences |
| [bank_switching_patterns.md](bank_switching_patterns.md) | **Practical patterns**: save/restore bank, cross-bank copy, double buffering, +2A/+3 special modes, Pentagon extended, antipatterns |
| [screen_layout.md](screen_layout.md) | **Pixel framebuffer**: nonlinear three-thirds layout, address calculation, lookup tables, attribute file |
| [contention_model.md](contention_model.md) | **Unified contention**: per-model timing, Ferranti vs gate array delay patterns, I/O contention, cross-platform strategy |
