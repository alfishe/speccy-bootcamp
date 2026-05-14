# ZX Spectrum Knowledge Base

> Knowledge about ZX Spectrum, clones, next-gen for software developers, demosceners, retro-enthusiasts.

Licensed under [CC BY-SA 4.0](LICENSE).

---

## Documentation Map

### 01 — Z80 CPU

| Article | Description |
|---------|------------|
| [z80_architecture.md](01_cpu/z80_architecture.md) | Registers, ALU, pinout, bus interface, and internal datapath |
| [z80_addressing.md](01_cpu/z80_addressing.md) | All addressing modes — immediate, register, indirect, indexed, relative |
| [z80_flags.md](01_cpu/z80_flags.md) | S, Z, H, P/V, N, C flags — per-instruction behavior, DAA, BCD arithmetic |
| [z80_instruction_set.md](01_cpu/z80_instruction_set.md) | Complete ISA: 698 instructions, opcode encoding, timing, groups, decision guides |
| [z80_undocumented.md](01_cpu/z80_undocumented.md) | IX/IY halves, SLL, MEMPTR, F3/F5, OUT (C),0, clone detection, R register |
| [z80_timing.md](01_cpu/z80_timing.md) | T-states, M-cycles, bus timing, WAIT pin, per-instruction costs, DRAM refresh |
| [z80_interrupts.md](01_cpu/z80_interrupts.md) | IM0/IM1/IM2, NMI, IFF1/IFF2, vector tables, EI latency, per-model timing |
| [z80_vs_modern.md](01_cpu/z80_vs_modern.md) | Z80 vs x86-64/ARM64 comparison, register mapping, programming mindset shift |
| [z80_coding_practices.md](01_cpu/z80_coding_practices.md) | Register discipline, instruction selection, arithmetic tricks, contention-aware coding, stack blitter |

### 02 — Hardware

#### Original Sinclair/Amstrad

| Article | Description |
|---------|------------|
| [ula_timing.md](02_hardware/original/ula_timing.md) | ULA frame timing per model, memory contention, multicolor effects, early/late timing, performance budget |

#### Soviet Clone Ecosystem

| Article | Description |
|---------|------------|
| [clone_timing.md](02_hardware/clones/clone_timing.md) | Clone video timing — Pentagon, Scorpion, Kay, ATM Turbo, FPGA implementations, detection techniques |

#### New Generation

*Placeholder — content coming.*

### 04 — Operating Systems

| Article | Description |
|---------|------------|
| [system_variables.md](04_operating_systems/system_variables.md) | ROM-defined system variables: FRAMES, PROG, VARS, CHANS, keyboard state, memory boundaries — the ROM's API surface |

### 00 — Overview · 03 — I/O · 06 — RE · 07 — Toolchain · 08 — References

*Placeholders — content coming. See [PLAN.md](PLAN.md) for the full catalog.*

### 05 — Development

#### Memory & I/O

| Article | Description |
|---------|------------|
| [memory_map_48k.md](05_development/03_memory_and_io/memory_map_48k.md) | 16K/48K memory map: ROM, screen, attributes, system variables, RAM regions |
| [memory_map_128k.md](05_development/03_memory_and_io/memory_map_128k.md) | 128K/+2 paging: 8 banks, #7FFD register, shadow screen, contended banks |
| [io_ports.md](05_development/03_memory_and_io/io_ports.md) | I/O ports: partial decoding, #FE deep dive, #7FFD, AY, Kempston, per-model differences |
| [screen_layout.md](05_development/03_memory_and_io/screen_layout.md) | Nonlinear framebuffer: three-thirds structure, address calculation, attribute file |
| [contention_model.md](05_development/03_memory_and_io/contention_model.md) | Unified contention reference: per-model timing, Ferranti vs gate array patterns, I/O contention |
| [bank_switching_patterns.md](05_development/03_memory_and_io/bank_switching_patterns.md) | Practical 128K+ paging: #7FFD, cross-bank access, double buffering, +2A/+3 modes |

#### Display & Timing

| Article | Description |
|---------|------------|
| [video_frame_overview.md](05_development/05_display_and_timing/video_frame_overview.md) | PAL fundamentals, ULA frame cycle, T-state budget, contentious vs non-contentious time |
| [video_frame_48k.md](05_development/05_display_and_timing/video_frame_48k.md) | 48K frame: T-state map, contention pattern, floating bus, performance budget |
| [video_frame_128k.md](05_development/05_display_and_timing/video_frame_128k.md) | 128K frame: odd-bank contention, shadow screen, floating bus differences |
| [video_frame_pentagon.md](05_development/05_display_and_timing/video_frame_pentagon.md) | Pentagon frame: 320 lines, binary counter, zero contention, 48.83 Hz |
| [video_frame_plus2a_plus3.md](05_development/05_display_and_timing/video_frame_plus2a_plus3.md) | +2A/+3 frame: Amstrad gate array contention, different contended banks, no I/O contention |
| [floating_bus.md](05_development/05_display_and_timing/floating_bus.md) | Floating bus: per-model behavior, raster sync via IN A,(#FF), why it fails on +2A/+3 and Pentagon |
| [raster_timing.md](05_development/05_display_and_timing/raster_timing.md) | Beam position calculation, HALT-based sync, per-model raster maps, cross-platform strategy |
| [color_system.md](05_development/05_display_and_timing/color_system.md) | Attribute byte, 8-color palette, attribute clash, ULAplus 64-color, Timex HiColor/HiRes |
| [border_effects.md](05_development/05_display_and_timing/border_effects.md) | Border color via #FE, raster bars, rainbow borders, per-model timing |
| [clone_video_modes.md](05_development/05_display_and_timing/clone_video_modes.md) | Clone video modes: GigaScreen, ATM hires, Profi 512×256, Kay CPLD, TS-Conf |

### 09 — Emulation

| Article | Description |
|---------|-------------|
| [cycle_exact_accuracy.md](09_emulation/software/cycle_exact_accuracy.md) | Frame timing divergence, CRT vs LCD, host sync strategies, AY audio clocks, judder mitigation techniques, emulator comparison, worst-case Pentagon@60Hz conclusion |

---

## Reading Order

**New to Z80 assembly:**

1. [Z80 Architecture](01_cpu/z80_architecture.md)
2. [Z80 Addressing](01_cpu/z80_addressing.md)
3. [Z80 Flags](01_cpu/z80_flags.md)
4. [Z80 Instruction Set](01_cpu/z80_instruction_set.md)

**Emulator authors and demoscene programmers:**

5. [Z80 Undocumented](01_cpu/z80_undocumented.md)
6. [Z80 Timing](01_cpu/z80_timing.md)
7. [ULA Timing](02_hardware/original/ula_timing.md)
8. [Clone Timing](02_hardware/clones/clone_timing.md)
9. [Z80 Interrupts](01_cpu/z80_interrupts.md)
10. [Cycle-Exact Emulation Accuracy](09_emulation/software/cycle_exact_accuracy.md)

**Spectrum assembly programmers (memory, I/O, display):**

11. [48K Memory Map](05_development/03_memory_and_io/memory_map_48k.md)
12. [Screen Pixel Layout](05_development/03_memory_and_io/screen_layout.md)
13. [I/O Ports](05_development/03_memory_and_io/io_ports.md)
14. [128K Memory Map](05_development/03_memory_and_io/memory_map_128k.md)
15. [Video Frame Overview](05_development/05_display_and_timing/video_frame_overview.md)
16. [48K Video Frame](05_development/05_display_and_timing/video_frame_48k.md)
17. [128K Video Frame](05_development/05_display_and_timing/video_frame_128k.md)
18. [Pentagon Video Frame](05_development/05_display_and_timing/video_frame_pentagon.md)

**Bridge to advanced optimization:**

19. [Z80 Coding Practices](01_cpu/z80_coding_practices.md)

**Coming from modern platforms:**

20. [Z80 vs Modern](01_cpu/z80_vs_modern.md)

---

See [PLAN.md](PLAN.md) for the full knowledge base catalog and writing priorities.
