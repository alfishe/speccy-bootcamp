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
| [ula_architecture.md](02_hardware/original/ula_architecture.md) | Inside the Ferranti ULA: video pipeline, bus arbitration, #FE register, keyboard/tape/sound cells, revisions, gate arrays, replacements |
| [keyboard_matrix.md](02_hardware/original/keyboard_matrix.md) | The 8×5 keyboard matrix: membrane hardware, half-row scanning, ghosting, Interface 2/Sinclair/Cursor joystick mappings, game keyset conventions by genre and region, redefinable input |

#### Soviet Clone Ecosystem

| Article | Description |
|---------|------------|
| [clone_timing.md](02_hardware/clones/clone_timing.md) | Clone video timing — Pentagon, Scorpion, Kay, ATM Turbo, FPGA implementations, detection techniques |
| [clone_joysticks.md](02_hardware/clones/clone_joysticks.md) | Built-in Kempston on clone motherboards, Beta 128 coexistence, two-player conventions, single-standard software culture |

#### New Generation

| Article | Description |
|---------|------------|
| [zx_next_joystick.md](02_hardware/newgen/zx_next_joystick.md) | ZX Next joystick: per-port modes (NextReg 0x05), dual Kempston #1F/#37, Mega Drive pads, Sinclair numbering trap |

### 04 — Operating Systems

| Article | Description |
|---------|------------|
| [system_variables.md](04_operating_systems/system_variables.md) | ROM-defined system variables: FRAMES, PROG, VARS, CHANS, keyboard state, memory boundaries — the ROM's API surface |

### 05 — Development

#### Memory & I/O

| Article | Description |
|---------|------------|
| [io_port_decoding.md](05_development/03_memory_and_io/io_port_decoding.md) | I/O port concepts: partial decoding, masks, mirrors, conflicts |
| [memory_and_io_48k.md](05_development/03_memory_and_io/memory_and_io_48k.md) | 16K/48K: memory map + #FE port (border, EAR, keyboard, beeper) |
| [memory_and_io_128k.md](05_development/03_memory_and_io/memory_and_io_128k.md) | 128K/+2: 8 banks, #7FFD paging, shadow screen, AY ports |
| [memory_and_io_plus3.md](05_development/03_memory_and_io/memory_and_io_plus3.md) | +2A/+3: #1FFD, 4 paging modes, true double buffering, +3 FDC |
| [memory_and_io_pentagon.md](05_development/03_memory_and_io/memory_and_io_pentagon.md) | Pentagon: #EFF7 extended paging, Beta 128 FDC/TR-DOS, zero contention |
| [memory_and_io_next.md](05_development/03_memory_and_io/memory_and_io_next.md) | ZX Spectrum Next: 2MB MMU, 8 KB pages, Layer 2/sprite/copper/DMA ports |
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

### 06 — Sound

#### Synthesis Techniques

| Article | Description |
|---------|------------|
| [ay_ym_synthesis.md](06_sound/synthesis/ay_ym_synthesis.md) | **Comprehensive AY/YM sound generation**: internal counter model, phase reset, sync-square, PWM, SID-sound, envelope exploitation, sample playback, drum synthesis |
| [ay_ym_perception.md](06_sound/synthesis/ay_ym_perception.md) | **The AY Sound: Perception, Emotion, and the Hardware Soul** — ABC vs ACB holy war, AY vs YM differences, why real hardware sounds different, psychoacoustics, nostalgia, recapturing the sound |
| [beeper_synthesis.md](06_sound/synthesis/beeper_synthesis.md) | **1-Bit Beeper Synthesis**: PWM engines, multi-channel tricks, DSP emulation physics |
| [shiru_ear_shaver_analysis.md](06_sound/synthesis/shiru_ear_shaver_analysis.md) | **Case Study:** Reverse engineering Shiru's *Ear Shaver* 1-bit engine |
| [multitrack_multichip.md](06_sound/synthesis/multitrack_multichip.md) | Multi-track and multi-chip synthesis outline: TurboSound, cross-chip effects, synchronization |

#### Sound Hardware

| Article | Description |
|---------|------------|
| [covox_sounDrive.md](06_sound/hardware/covox_sounDrive.md) | **Covox & SounDrive**: 8-bit DAC hardware mixing, sample playback, Z80 bottlenecks, T-state limits |

*See [06_sound/README.md](06_sound/README.md) for the full sound section catalog.*

### 07 — Demoscene

*Section scaffolded — content coming. See [07_demoscene/README.md](07_demoscene/README.md) for the planned article catalog.*

### 00 — Overview · 03 — I/O · 08 — RE · 09 — Toolchain · 10 — References · 11 — Emulation

| Article | Description |
|---------|-------------|
| [joystick.md](03_io/peripherals/joystick.md) | Joystick interfaces: Kempston #1F, Sinclair/Interface 2, Cursor/Protek/AGF, Fuller, Timex, clone built-ins, unified multi-standard reader |
| [io_port_map.md](10_references/io_port_map.md) | Complete I/O port reference: every port across all models, Black_Cat table with annotations, decoding bitmasks, per-model differences |
| [cycle_exact_accuracy.md](11_emulation/software/cycle_exact_accuracy.md) | Frame timing divergence, CRT vs LCD, host sync strategies, AY audio clocks, judder mitigation techniques, emulator comparison, worst-case Pentagon@60Hz conclusion |

*Other sections are placeholders — content coming. See [PLAN.md](PLAN.md) for the full catalog.*

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
10. [Cycle-Exact Emulation Accuracy](11_emulation/software/cycle_exact_accuracy.md)

**Spectrum assembly programmers (memory, I/O, display):**

11. [I/O Port Decoding](05_development/03_memory_and_io/io_port_decoding.md)
12. [48K Memory and I/O](05_development/03_memory_and_io/memory_and_io_48k.md)
13. [128K Memory and I/O](05_development/03_memory_and_io/memory_and_io_128k.md)
14. [+2A/+3 Memory and I/O](05_development/03_memory_and_io/memory_and_io_plus3.md)
15. [Pentagon Memory and I/O](05_development/03_memory_and_io/memory_and_io_pentagon.md)
16. [ZX Spectrum Next Memory and I/O](05_development/03_memory_and_io/memory_and_io_next.md)
17. [Screen Pixel Layout](05_development/03_memory_and_io/screen_layout.md)
18. [Video Frame Overview](05_development/05_display_and_timing/video_frame_overview.md)
19. [48K Video Frame](05_development/05_display_and_timing/video_frame_48k.md)
20. [128K Video Frame](05_development/05_display_and_timing/video_frame_128k.md)
21. [Pentagon Video Frame](05_development/05_display_and_timing/video_frame_pentagon.md)

**Sound and music programmers:**

22. [1-Bit Beeper Synthesis](06_sound/synthesis/beeper_synthesis.md) — PWM fundamentals, emulation physics, multi-channel tracking
23. [Ear Shaver Case Study](06_sound/synthesis/shiru_ear_shaver_analysis.md) — Extreme 1-bit engine reverse engineering
24. [Covox & SounDrive PCM Playback](06_sound/hardware/covox_sounDrive.md) — Resistor ladders and hardware mixing
25. [AY/YM Sound Generation](06_sound/synthesis/ay_ym_synthesis.md) — internal counter model, phase reset, sync-square, envelope exploitation
26. [Multi-Track and Multi-Chip Synthesis](06_sound/synthesis/multitrack_multichip.md) — TurboSound, cross-chip effects

**Bridge to advanced optimization:**

27. [Z80 Coding Practices](01_cpu/z80_coding_practices.md)

**Coming from modern platforms:**

28. [Z80 vs Modern](01_cpu/z80_vs_modern.md)

---

See [PLAN.md](PLAN.md) for the full knowledge base catalog and writing priorities.
