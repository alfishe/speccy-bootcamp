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

### 06 — Sound ✅ COMPLETE

#### Synthesis Techniques

| Article | Description |
|---------|------------|
| [ay_ym_synthesis.md](06_sound/synthesis/ay_ym_synthesis.md) | **Comprehensive AY/YM sound generation**: internal counter model, phase reset, sync-square, PWM, SID-sound, envelope exploitation, sample playback, drum synthesis |
| [ay_ym_techniques.md](06_sound/synthesis/ay_ym_techniques.md) | **AY/YM Synthesis Techniques** — sync-square, PWM, SID-sound, buzzer bass, note-colored noise, drum synthesis, sample playback |
| [ay_vs_ym.md](06_sound/synthesis/ay_vs_ym.md) | **AY vs YM Technical Comparison** — DAC ladder differences, 5-bit envelope on YM, DC offset, SEL pin, per-unit variation, emulator modeling |
| [ay_ym_perception.md](06_sound/synthesis/ay_ym_perception.md) | **The AY Sound: Perception, Emotion, and the Hardware Soul** — ABC vs ACB holy war, AY vs YM differences, why real hardware sounds different, psychoacoustics, nostalgia, recapturing the sound |
| [beeper_synthesis.md](06_sound/synthesis/beeper_synthesis.md) | **1-Bit Beeper Synthesis**: PWM engines, multi-channel tricks, DSP emulation physics |
| [shiru_ear_shaver_analysis.md](06_sound/synthesis/shiru_ear_shaver_analysis.md) | **Case Study:** Reverse engineering Shiru's *Ear Shaver* 1-bit engine |
| [multitrack_multichip.md](06_sound/synthesis/multitrack_multichip.md) | Multi-track and multi-chip synthesis outline: TurboSound, cross-chip effects, synchronization |

#### Sound Hardware

| Article | Description |
|---------|------------|
| [sound_overview.md](06_sound/hardware/sound_overview.md) | **Sound hardware ecosystem overview + decision guide** — navigation hub for the entire subdirectory |
| [ay_3_8912.md](06_sound/hardware/ay_3_8912.md) | AY-3-8912 / YM2149F PSG: pinout, register map, clock domains, DAC characteristics, per-model differences |
| [stereo_audio.md](06_sound/hardware/stereo_audio.md) | Stereo audio modifications: ABC/ACB separation, BytesDelight |
| [turbosound.md](06_sound/hardware/turbosound.md) | TurboSound: dual/triple AY, port decoding, programming model |
| [turbosound_fm.md](06_sound/hardware/turbosound_fm.md) | TurboSound FM: YM2203 (OPN) FM synthesis, 3 FM + 3 SSG channels |
| [saa1099.md](06_sound/hardware/saa1099.md) | SAA1099 PSG: Philips sound chip, 6-channel stereo |
| [covox_sounDrive.md](06_sound/hardware/covox_sounDrive.md) | **Covox & SounDrive**: 8-bit DAC hardware mixing, sample playback, TLC7226CN quad DAC |
| [gs_general_sound.md](06_sound/hardware/gs_general_sound.md) | General Sound: dedicated Z80-based sound card, 4-channel sample mixing |
| [moonsound.md](06_sound/hardware/moonsound.md) | MoonSound (OPL4/YMF278B): 24-channel wavetable + 18-channel FM |
| [zx_next_audio.md](06_sound/hardware/zx_next_audio.md) | ZX Spectrum Next audio: 3× AY + beeper + DMA sample playback |

#### Trackers & Formats

| Article | Description |
|---------|------------|
| [tracker_history.md](06_sound/trackers_and_formats/tracker_history.md) | **30-year history of ZX music editors** — beeper trackers (1985), Pro Tracker lineage (Golden Disk Corp.), VTII / Arkos split, modern cross-platform tools (AT3, VT3) |
| [ay_music_formats.md](06_sound/trackers_and_formats/ay_music_formats.md) | **Master catalogue**: every AY/YM music file format (`.PT3`, `.PSG`, `.YM`, `.AY`, `.AKG`, etc.) — modules, dumps, containers, modern embedded |
| [sound_tracker.md](06_sound/trackers_and_formats/sound_tracker.md) | **Sound Tracker 1.1** (Bzyk, 1990) — the first AY grid editor; established the pattern/sample/ornament paradigm |
| [asc_sound_master.md](06_sound/trackers_and_formats/asc_sound_master.md) | **Asc Sound Master** (Sendetskiy, 1992) — Soviet alternative with envelope-mode-per-tick instrument model |
| [protracker.md](06_sound/trackers_and_formats/protracker.md) | **Pro Tracker 1/2/3** (Golden Disk Corp., 1995–1997) — the format-defining lineage that produced `.PT3` |
| [vortex_tracker.md](06_sound/trackers_and_formats/vortex_tracker.md) | Vortex Tracker II — the de facto PC-based PT3 editor (Bulba, 2000–present) |
| [arkos_tracker.md](06_sound/trackers_and_formats/arkos_tracker.md) | Arkos Tracker 2/3 — modern cross-platform AY tracker (Targhan, 2003–present) |
| [pt3_format.md](06_sound/trackers_and_formats/pt3_format.md) | PT3 module format — byte-level binary specification (header, patterns, samples, ornaments, player operation) |
| [psg_format.md](06_sound/trackers_and_formats/psg_format.md) | PSG register dump format — universal pre-rendered AY register stream |

*See [06_sound/README.md](06_sound/README.md) for the full sound section catalog.*

### 09 — Toolchain

**Survey articles**

| Article | Description |
|---------|-------------|
| [native_toolchain.md](09_toolchain/native_toolchain.md) | **Native Spectrum toolchain** — assemblers and monitors that ran on the Spectrum itself (1982–2000s). Zeus, HiSoft DevPac / GENS-MONS, ALASM+STS, XAS; pre-assembler era; editor workflow evolution; Soviet vs Western toolchain split |
| [cross_platform_toolchain.md](09_toolchain/cross_platform_toolchain.md) | **Modern cross-platform toolchain** — SjASMPlus, z88dk, SDCC, Pasmo, vasm, WLA-DX, zmac, RASM; VS Code + DeZog + Klive IDE; Fuse, ZEsarUX, CSpect, JSSpeccy 3, MAME; build systems, CI/CD, asset pipeline, recommended-setup decision matrix, worked Hello World example |

**Per-tool deep dives**

| Article | Description |
|---------|-------------|
| [sjasmplus.md](09_toolchain/sjasmplus.md) | **SjASMPlus** — the de facto standard Z80 cross-assembler. Three-pass assembly, virtual device mode (14 machines), Lua scripting, ZX Spectrum Next Z80N support, complete output directives (SAVESNA/SAVETAP/SAVETRD/SAVENEX), SLD source-level debugging, comparison matrix against every alternative |
| [z88dk.md](09_toolchain/z88dk.md) | **z88dk** — the complete C development kit for the Z80 family. Two C compilers (sccz80 + patched SDCC), classic + newlib libraries, the `+target` system, the `zcc` front-end, full ZX Spectrum library API, `appmake` output formats, mixing C with assembly, worked example |
| [sdcc.md](09_toolchain/sdcc.md) | **SDCC** — the canonical reference for using the Small Device C Compiler standalone. Z80 port history, complete toolchain, Z80-specific flag reference, the stack-based ABI, custom CRT0, `.cdb` debug format, integration with SjASMPlus, worked bare-metal 48K example, and a comparison vs z88dk-sdcc |
| [asset_tools.md](09_toolchain/asset_tools.md) | **Asset Pipeline** — the three-stage model (authoring → conversion → integration). Screen graphics (`.scr`/`.sch`/`.nic`), software sprites and Next hardware sprites, fonts (8×8 and FZX), AY music (VTII, Arkos) and 1-bit beeper engines (Beepola, BeepFX), compression (ZX0/ZX1/ZX2/ZX7/MegaLZ/RCS), tile maps, worked Makefile-driven pipeline |
| [debugging.md](09_toolchain/debugging.md) | **Debugging** — the three-layer model: native monitor-debuggers (STS, MONS, Zeus Monitor), built-in emulator debuggers (ZEsarUX, Fuse, CSpect, UnrealSpeccy, ZXMAK2, MAME), and source-level / IDE-integrated debuggers (DeZog, z88dk-gdb, mainline GDB Z80 target, SpectNetIDE). Compiler-integration deep dive (SLD / `.lis` / `.map` / DWARF / `.cdb`), comparison matrix across 8 debuggers, three recommended workflows |
| [disassemblers.md](09_toolchain/disassemblers.md) | **Disassemblers** — from raw Z80 bytes to annotated source. Three approaches (linear, smart static, trace-driven). z80dasm, z88dk-dis, z80dismblr / DeZog, z80-smart-disassembler, SkoolKit (with built-in cycle-exact Z80 simulator), IDA Pro, Ghidra (Z80 module caveats), Reko. Comparison matrices, decision tree, Fuse profiler + SkoolKit `trace.py` workflow |
| [boriel_zxbasic.md](09_toolchain/boriel_zxbasic.md) | **Boriel ZX BASIC** — the modern BASIC cross-compiler (`zxbc`) emitting native Z80 machine code. Three-stage pipeline (`zxbpp`/`zxbc`/`zxbasm`), 8-type static type system, `SUB`/`FUNCTION` with `ByVal`/`ByRef`/`FastCall`, structured control flow, first-class inline `ASM`, ROM-binding standard library, full CLI flag reference, all output formats (`.bin`/`.tap`/`.tzx`/`.sna`/`.z80`), worked game-loop example, comparison matrix vs z88dk C and pure assembly, decision tree |
| [vscode_integration.md](09_toolchain/vscode_integration.md) | **VS Code Integration** — the canonical reference for VS Code as the ZX Spectrum IDE. Extension ecosystem (DeZog, Z80 Macro-Assembler, Z80 Assembly Meter, Hex Editor, Klive IDE, SpectNetIDE). DeZog deep dive — four backends (ZEsarUX, CSpect, MAME, internal simulator), reverse debugging via ZEsarUX history. Build tasks and problem matchers for SjASMPlus / z88dk / Boriel ZX BASIC. Complete worked `.vscode/` project setup. Stack comparison (DeZog+SjASMPlus+ZEsarUX vs Klive IDE vs SpectNetIDE), decision tree, best practices, pitfalls |

*See [09_toolchain/README.md](09_toolchain/README.md) for the section index, including planned per-tool deep dives (Pasmo, vasm, WLA-DX, zmac, RASM, Klive IDE, ZXDevStudio, etc.).*

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

22. [Sound Hardware Ecosystem Overview](06_sound/hardware/sound_overview.md) — the decision guide; read this first to know which hardware to target
23. [AY-3-8912 / YM2149F PSG Silicon](06_sound/hardware/ay_3_8912.md) — the foundation chip on every 128K and clone
24. [Stereo Audio Modifications](06_sound/hardware/stereo_audio.md) — ABC/ACB/BytesDelight wiring
25. [1-Bit Beeper Synthesis](06_sound/synthesis/beeper_synthesis.md) — PWM fundamentals, emulation physics, multi-channel tracking
26. [Ear Shaver Case Study](06_sound/synthesis/shiru_ear_shaver_analysis.md) — Extreme 1-bit engine reverse engineering
27. [AY/YM Sound Generation](06_sound/synthesis/ay_ym_synthesis.md) — internal counter model, phase reset, sync-square, envelope exploitation
28. [TurboSound](06_sound/hardware/turbosound.md) — dual/triple AY bank-switching
29. [TurboSound FM](06_sound/hardware/turbosound_fm.md) — YM2203 OPN FM expansion
30. [Covox & SounDrive PCM Playback](06_sound/hardware/covox_sounDrive.md) — resistor ladders, TLC7226CN quad DAC, hardware mixing
31. [General Sound](06_sound/hardware/gs_general_sound.md) — dedicated Z80 coprocessor sound card
32. [MoonSound (OPL4)](06_sound/hardware/moonsound.md) — wavetable + FM synthesis
33. [SAA1099 Philips PSG](06_sound/hardware/saa1099.md) — 6-channel stereo alternative
34. [ZX Spectrum Next Audio](06_sound/hardware/zx_next_audio.md) — 3× FPGA AY + DMA + beeper
35. [Multi-Track and Multi-Chip Synthesis](06_sound/synthesis/multitrack_multichip.md) — TurboSound, cross-chip effects
36. [Tracker History](06_sound/trackers_and_formats/tracker_history.md) — 30 years of ZX music editors: from Sound Tracker (1990) to Arkos Tracker 3
37. [AY Music Formats](06_sound/trackers_and_formats/ay_music_formats.md) — master catalogue: `.PT3`, `.PSG`, `.YM`, `.AY`, `.AKG`, all module/dump/container formats
38. [Sound Tracker 1.1](06_sound/trackers_and_formats/sound_tracker.md) — Bzyk's 1990 first AY grid editor; established the pattern/sample/ornament paradigm
39. [Asc Sound Master](06_sound/trackers_and_formats/asc_sound_master.md) — Sendetskiy's 1992 Soviet alternative with envelope-mode-per-tick instruments
40. [Pro Tracker 1/2/3](06_sound/trackers_and_formats/protracker.md) — Golden Disk Corp.'s 1995–1997 format-defining lineage that produced `.PT3`
41. [Vortex Tracker II](06_sound/trackers_and_formats/vortex_tracker.md) — the de facto PC-based PT3 editor
42. [Arkos Tracker 2/3](06_sound/trackers_and_formats/arkos_tracker.md) — modern cross-platform alternative for new composers in 2025
43. [PT3 Module Format](06_sound/trackers_and_formats/pt3_format.md) — byte-level binary specification of the de facto interchange format
44. [PSG Register Dump Format](06_sound/trackers_and_formats/psg_format.md) — the universal pre-rendered AY dump format

**Toolchain and development environment:**

45. [Native Toolchain](09_toolchain/native_toolchain.md) — assemblers and monitors that ran on the Spectrum (1982–2000s): Zeus, DevPac, ALASM, XAS
46. [Cross-Platform Toolchain](09_toolchain/cross_platform_toolchain.md) — modern development on PC/Mac/Linux: SjASMPlus, z88dk, VS Code, emulators, CI/CD
47. [SjASMPlus](09_toolchain/sjasmplus.md) — the de facto standard Z80 cross-assembler: three-pass assembly, virtual device mode, Lua scripting, Z80N, SLD debugging, every output format
48. [z88dk](09_toolchain/z88dk.md) — the complete C development kit: two compilers (sccz80 + SDCC), classic + newlib, `+target` system, full ZX Spectrum library API, mixing C with assembly
49. [SDCC](09_toolchain/sdcc.md) — Small Device C Compiler standalone: stack-based ABI, custom CRT0, `.cdb` debug format, integration with SjASMPlus, when to choose over z88dk
50. [Asset Tools](09_toolchain/asset_tools.md) — the asset pipeline: screen graphics, software/hardware sprites, fonts (8×8 + FZX), AY/beeper music, ZX0/ZX1/ZX7/MegaLZ compression, tile maps
51. [Debugging](09_toolchain/debugging.md) — three-layer model (native / emulator / source-level), every major debugger, debug-metadata formats, comparison matrix, recommended workflows
52. [Disassemblers](09_toolchain/disassemblers.md) — linear / smart static / trace-driven approaches, z80dasm, z88dk-dis, SkoolKit, IDA Pro, Ghidra, decision tree

**Bridge to advanced optimization:**

36. [Z80 Coding Practices](01_cpu/z80_coding_practices.md)

**Coming from modern platforms:**

37. [Z80 vs Modern](01_cpu/z80_vs_modern.md)

---

See [PLAN.md](PLAN.md) for the full knowledge base catalog and writing priorities.
