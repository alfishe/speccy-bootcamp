[← Home](../../README.md) · [Memory & I/O](README.md)

# Development — Memory Architecture

Memory maps, I/O ports, contention, screen layout, system variables, and bank switching.

| Article | Description |
|---------|------------|
| [memory_map_48k.md](memory_map_48k.md) | 16K/48K memory map: ROM, screen pixel buffer, attribute file, system variables, RAM regions, reserving memory for machine code |
| [memory_map_128k.md](memory_map_128k.md) | 128K/+2 paging: 8 RAM banks, #7FFD register, ROM switching, shadow screen (double buffering), contended vs uncontended banks |
| [io_ports.md](io_ports.md) | I/O port architecture: partial decoding, #FE deep dive (border/EAR/keyboard), #7FFD paging, AY ports, Kempston, per-model differences |
| [screen_layout.md](screen_layout.md) | Nonlinear pixel framebuffer: three-thirds structure, address calculation, lookup tables, attribute file, column-major access |
