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
| [atm_turbo.md](02_hardware/clones/atm_turbo.md) | ATM Turbo: CP/M mode, 7 MHz turbo, 4 video modes (320×200 16-color, 640×200, 80×25 text), IDE controller, flexible memory paging, 64-color RGBI palette |
| [scorpion.md](02_hardware/clones/scorpion.md) | Scorpion ZS-256: Serge Zonov / Leningrad lineage, true 48K timing (69,888 T-states), Shadow Service Monitor debugger, port #1FFD turbo+extended paging, #FF floating bus (correct), SMUC ISA bridge, GMX 2 MB / 640×200×16, ProfROM |

#### New Generation

| Article | Description |
|---------|------------|
| [zx_next.md](02_hardware/newgen/zx_next.md) | ZX Spectrum Next complete hardware reference: layer stack, NextReg system, Layer 2 framebuffer, hardware sprites, tilemap, copper, DMA, joystick system, Z80N extensions |

### 04 — Operating Systems ✅ COMPLETE

#### ROM Internals

| Article | Description |
|---------|------------|
| [rom_48k.md](04_operating_systems/rom_48k.md) | 48K ROM: initialisation, RST vectors, command dispatch, calculator instruction set (66 ops), command handler internals, tape format |
| [rom_128k.md](04_operating_systems/rom_128k.md) | 128K ROM 0: dual-ROM architecture, ROM call bridge, ROM swap calling convention, PLAY/SOUND/BANK handlers, AY-3-8912 register map, RAM disk, editor internals |
| [rom_plus2.md](04_operating_systems/rom_plus2.md) | +2A/+3 ROM internals: 64 KB four-page layout, paging ports `#7FFD`/`#1FFD`, four paging modes (128K compat / all-RAM 0-3 / all-RAM 4-7 / Plus 3), CP/M boot, bugs |
| [system_variables.md](04_operating_systems/system_variables.md) | ROM-defined system variables: FRAMES, PROG, VARS, CHANS, keyboard state, memory boundaries — the ROM's API surface |
| [rom_versions.md](04_operating_systems/rom_versions.md) | ROM version catalogue: 48K Issues 1-6 CRC32 values, 128K, +2 grey, +2A/+3 four-page, localised ROMs, clone ROMs (Pentagon, Scorpion, ATM Turbo, ZX Evolution, Timex), modern replacements (SE BASIC, OpenSE, +3E, NextZXOS) |

#### Disk Operating Systems

| Article | Description |
|---------|------------|
| [trdos.md](04_operating_systems/trdos.md) | TR-DOS: the Soviet flat filesystem standard for Pentagon/Beta 128, 128 file slots, hook codes API, why it dominated the Russian scene |
| [plus3dos.md](04_operating_systems/plus3dos.md) | +3 DOS: Amstrad's CP/M-compatible DOS for +2A/+3, BDOS layer, RSX-based BASIC integration (`LOAD "a:..."`, `CAT`, `FORMAT`) |
| [esxdos.md](04_operating_systems/esxdos.md) | ESXDOS: modern Western DOS for DivIDE/DivMMC, FAT16/32, 8 KB dot-command overlays, hook codes API at `#0084` |
| [is_dos.md](04_operating_systems/is_dos.md) | IS-DOS: 1990s Russian hierarchical filesystem alternative, MS-DOS-compatible 32-byte directory entries, subdirectories, attributes, jump-table API |
| [nedo_dos.md](04_operating_systems/nedo_dos.md) | NedoDOS: modern DOS for ZX Evolution/NedoPC, FAT16/32 with VFAT long filenames, SD/CF/IDE, multiple partitions, NedoDOS Commander |
| [nextzxos.md](04_operating_systems/nextzxos.md) | NextZXOS: ZX Spectrum Next OS, ESXDOS-derived API with Next hardware extensions, dot commands, SD card, layer 2 / sprite / tilemap |
| [evo_os.md](04_operating_systems/evo_os.md) | ZX Evolution BIOS/OS: three-layer stack (boot ROM firmware, BaseConf FPGA bitstream, OS), Pentagon 1024 / ATM Turbo / TS-Conf configurations, boot process |

#### Alternative Operating Systems

| Article | Description |
|---------|------------|
| [cpm.md](04_operating_systems/cpm.md) | CP/M 2.2 on Spectrum: +3 bootable CP/M, ATM Turbo, Sprinter, BIOS/BDOS layer, file control blocks, CCP, the CP/M software library |
| [fuzix.md](04_operating_systems/fuzix.md) | FUZIX: Alan Cox's Unix-like Z80 OS — ~24 KB kernel, ~70 Unix V7 syscalls, pre-emptive multitasking at 50 Hz VBLANK, FCC C compiler, targets 128K/+2A/+3/Pentagon/ATM/Sprinter/Evolution/Next |

#### BASIC Dialects

| Article | Description |
|---------|------------|
| [basic_dialects.md](04_operating_systems/basic_dialects.md) | Sinclair BASIC variants: 48K (1982), 128K (1986), +2/+2A/+3 (1987), TR-DOS ext, QL SuperBASIC (1984), SE BASIC / OpenSE (2002-2023), NextBASIC (2017). 17-feature comparison matrix |

### 05 — Development

#### Sinclair BASIC

| Article | Description |
|---------|------------|
| [basic_48k.md](05_development/01_basic/basic_48k.md) | **Sinclair BASIC 48K — comprehensive reference**: what BASIC is (vs Microsoft BASIC), three ROM versions, memory layout, token system with abbreviations, variable types, 5-byte floating-point format, calculator stack (44 operations), parser pipeline, **graphics commands** (`PLOT`, `DRAW`, `CIRCLE`, `POINT`, `ATTR`), **sound** (`BEEP` with frequency formula), **machine-code bridge** (`PEEK`, `POKE`, `USR`), notable quirks (no ELSE, mandatory LET, single-line editor). Worked examples: Mandelbrot, Ode to Joy |
| [basic_128k.md](05_development/01_basic/basic_128k.md) | **Sinclair BASIC 128K extensions**: new full-screen editor, boot menu, the **`PLAY` command** mini-language in depth (notes c-b/C-B, sharps/flats, octave O0–O8, volume V0–V15, envelope W0–W7, tempo, channel mode, repeats, three-voice harmony), direct AY-3-8912 register access via `OUT`/`IN`, +2A/+3 disk commands (`CAT`, `FORMAT`, `ERASE`), token table differences, memory paging, RAM disk |

#### Assembly

| Article | Description |
|---------|------------|
| [assembly_intro.md](05_development/02_assembly/assembly_intro.md) | **Getting started with Z80 assembly**: toolchain setup (SjASMPlus + Fuse + VSCode/DeZog), source file structure, 48K memory map, annotated Hello World walkthrough, building pipeline (.asm to .tap/.sna), output formats (SNA/TAP/TZX/TRD/NEX), first debugging session, when to use asm vs C vs BASIC |
| [rom_calls.md](05_development/02_assembly/rom_calls.md) | **Calling the ROM from assembly**: entry-point landscape, save/restore state (IY = #5C3A, ERR_SP), cookbook for character output, keyboard, screen, BEEP, math via FP calculator, 128K routines (PLAY), AY-3-8912 direct access, ROM-call wrapper macros, when NOT to use ROM |
| [stack_and_rst.md](05_development/02_assembly/stack_and_rst.md) | **Stack, RST vectors, calling conventions**: stack mechanics (T-state table), balanced stack rule, eight RST vectors, five calling conventions, shadow registers (EXX/EX AF,AF'), stack as temp storage, computed calls (JP (HL)), stack frames for locals, ERR_SP try/catch, recursion |
| [assembly_patterns.md](05_development/02_assembly/assembly_patterns.md) | **Assembly design patterns**: state machines (Moore/Mealy), dispatch tables, table-driven code, function pointer tables (plugin architecture), coroutines via stack swapping, self-modifying code patterns, macro systems, modular file organization, 128K memory banking patterns |
| [assembly_optimization.md](05_development/02_assembly/assembly_optimization.md) | **Performance optimization**: optimization workflow, T-state budgeting (69,888T/frame), hot-loop techniques (loop invariants, LDIR, DJNZ, unrolling), lookup tables (sine, multiply), fast multiply/divide algorithms, SMC in hot loops, contended vs uncontended memory, 10-recipe performance cookbook |
| [c_interop.md](05_development/02_assembly/c_interop.md) | **Mixed C and assembly**: sccz80 vs zsdcc, calling conventions in depth (__FASTCALL__, __sdcccall), C-calls-asm + asm-calls-C, inline assembly, shared globals (PUBLIC/EXTERN), project structure (multi-file, Makefile), zcc build pipeline, performance patterns (which C ops are slow on Z80), z88dk newlib interop, complete worked project |

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

#### Interrupt Programming ✅ COMPLETE

| Article | Description |
|---------|------------|
| [interrupt_programming.md](05_development/04_interrupts/interrupt_programming.md) | **Foundational guide**: IM1/IM2 setup, 257-byte vector table, ISR patterns, T-state budgets, contention, cookbook, antipatterns |
| [race_the_beam.md](05_development/04_interrupts/race_the_beam.md) | **Raster-synchronized multicolor**: 8×8 constraint reframed, T-state budget per scanline, 5 sync strategies (HALT, floating bus, port-#FF, line interrupt, copper), BIFROST* engine deep dive |
| [nmi.md](05_development/04_interrupts/nmi.md) | **NMI and the Multiface**: 74LS74 flip-flop hardware, NMI vs INT comparison, 4 NMI-safe code rules, NMI during common operations table, DivIDE/ESXDOS magic button |
| [im2_effects.md](05_development/04_interrupts/im2_effects.md) | **Demoscene IM2 effects**: vector table placement rules, 15-game disassembly survey (256 vs 257-byte tables), 3 manager patterns (direct / JP trampoline / Hudson Hawk bank-switching), 5 ISR effect catalog, demo framework sequencer |
| [im2_disk_music.md](05_development/04_interrupts/im2_disk_music.md) | **Disk load with AY music**: WD1793 byte budget, Ivan Roshchin concurrency math (Pentagon 48.83 Hz, 9.77 interrupts/rev, 138-byte drift), 3 workaround patterns (music-after-sector / stop-motor resync / custom WD1793 driver), Western DOS comparison |
| [im2_advanced.md](05_development/04_interrupts/im2_advanced.md) | **Advanced IM2 platforms**: ZX Spectrum Next hardware IM2 mode (core 3.02+, 8 prioritized sources, RETI mandatory), TS-Conf separate frame/line/DMA vectors, copper vs ISR decision matrix, Hudson Hawk 128K bank-switching ISR deep dive, sample-rate ISRs (AY/Covox/beeper PWM) |

*See [04_interrupts/README.md](05_development/04_interrupts/README.md) for the section index. All 6 articles complete.*

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
| [video_frame_scorpion.md](05_development/05_display_and_timing/video_frame_scorpion.md) | Scorpion ZS-256 frame: 312 lines matching 48K macro timing, +9 T horizontal shift, revision-dependent contention, 7 MHz turbo |
| [video_frame_other_soviet.md](05_development/05_display_and_timing/video_frame_other_soviet.md) | Long-tail Soviet clones: Kay 1024 (48K-clean), ATM Turbo 7 MHz anomaly (99,880 T-states), Profi paper offset, Byte, Quorum, Leningrad, LEC |
| [video_frame_next.md](05_development/05_display_and_timing/video_frame_next.md) | ZX Spectrum Next: configurable timing modes (48K/128K/+2A/Pentagon), 4 CPU speeds (3.5/7/14/28 MHz), copper coprocessor |
| [video_frame_sprinter.md](05_development/05_display_and_timing/video_frame_sprinter.md) | Sprinter: SVGA 70 Hz frame (not PAL 50 Hz), 20 MHz Z80, 5 video modes, music tempo 40% faster |
| [video_frame_zxevo.md](05_development/05_display_and_timing/video_frame_zxevo.md) | ZX Evolution (PentEvo): real Z80 + Altera MAX CPLDs, Pentagon-compatible base, BaseConf vs TS-Conf configurations |
| [contention_timing.md](05_development/05_display_and_timing/contention_timing.md) | Per-T-state delay tables (Ferranti 6-5-4-3-2-1-0-0, Amstrad 1-0-7-6-5-4-3-2), per-instruction contended cost tables |
| [interlace_and_flicker.md](05_development/05_display_and_timing/interlace_and_flicker.md) | Non-interlaced output, 50 Hz perception threshold, attribute flicker, GigaScreen flicker math, CRT vs LCD |
| [crt_output.md](05_development/05_display_and_timing/crt_output.md) | Developer view of CRT/LCD output: pixel aspect ratio, overscan, composite artifacts, per-display-type behaviour |
| [video_frame_comparison.md](05_development/05_display_and_timing/video_frame_comparison.md) | Synthesis: all models side-by-side — T-states/frame, contention, turbo, compatibility matrix, detection decision tree |

#### DOS & Tape

| Article | Description |
|---------|------------|
| [tape_programming.md](05_development/08_dos_tape/tape_programming.md) | **Tape loading and saving from assembly**: ROM routines (SA-BYTES, LD-BLOCK, SAVE, LOAD), custom bit-banging loaders via port #FE, turbo loaders (3000+ baud), custom savers, border effects, error handling, decision matrix |
| [trdos_programming.md](05_development/08_dos_tape/trdos_programming.md) | **TR-DOS programming**: ROM banking via port #FF, 9 standard hook codes dispatched at #3D13, file operations (LOAD/SAVE/ERASE/CAT), direct WD1793 sector I/O, catalog reader, demoscene double-buffered streaming from disk |
| [dos_programming.md](05_development/08_dos_tape/dos_programming.md) | **Western DOS programming**: +3 DOS RSX calls, ESXDOS hook codes at #0084, NextZXOS extensions, dot command development (8 KB overlays at #2000), API comparison matrix, portable code strategy, runtime DOS detection |
| [file_format_handling.md](05_development/08_dos_tape/file_format_handling.md) | **File format parsing**: magic-byte detection, .TAP/.TZX/.TRD/.SCL/.DSK/.SNA/.Z80/.SCR formats, directory traversal from disk images, .Z80 RLE decompression, common pitfalls (byte order, compression flags, sector IDs) |
| [mass_storage_programming.md](05_development/08_dos_tape/mass_storage_programming.md) | **Direct mass storage access**: IDE/CompactFlash register-level access (ATA commands), SD card SPI bit-banging, read-only FAT16/32 reader (boot sector parsing, cluster chain following), performance comparison vs OS-mediated |

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

#### Player Routines

| Article | Description |
|---------|------------|
| [ay_player_routines.md](06_sound/players/ay_player_routines.md) | Player architecture: ISR integration, register writes, timing |
| [player_comparison.md](06_sound/players/player_comparison.md) | PT3 vs Arkos (AKG/AKM/AKY): speed, size, features, decision table |

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

### 03 — I/O — Peripherals ✅ COMPLETE

| Article | Description |
|---------|-------------|
| [interface1.md](03_io/peripherals/interface1.md) | **ZX Interface 1** (Sinclair, 1983) — triple-function expansion: Microdrive controller + RS-232 + ZX Net LAN. 8 KB shadow ROM paging via `M1` fetch at `#0008`, hook codes `#1B`–`#32`, ZX Microdrive sector format (254 × 543 bytes, bespoke non-CRC checksum), bit-bang RS-232, single-wire token bus for 64 Spectrums |
| [interface2.md](03_io/peripherals/interface2.md) | **ZX Interface 2** (Sinclair, 1983) — twin-joystick + ROM-cartridge expansion. MT62001 joystick decode IC, 28-pin cartridge socket mirroring 27128 EPROM pinout, `/ROMCS` pull-up disables internal ROM at `#0000-#3FFF`, the 10 released cartridges, +2A/+3 incompatibility (two-diode fix), homebrew cartridge ecosystem |
| [multiface.md](03_io/peripherals/multiface.md) | **Multiface (One / 128 / 3)** (Romantic Robot, 1986–1988) — hardware overlay peripheral: 8 KB ROM + 8 KB RAM paged in via NMI vector fetch at `#0066`, three model variants with distinct port maps (`#9F`/`#1F` for MF1, `#BF`/`#3F` for MF128, `#3F`/`#BF` for MF3), `+3` paging-port back doors (`#7F3F`/`#1F3F`), stealth mode, dump-file format (precursor to `.z80`), Genie disassembler and Lifeguard poke-finder ecosystem, cultural impact on cheat codes and snapshots |
| [keyboard.md](03_io/peripherals/keyboard.md) | **Keyboard Reading** — software-side companion to `keyboard_matrix.md`. Half-row scan idiom, 40-key scan, ghosting and the QAOP/CS consensus, per-model differences (48K ULA, 128K AY port B, +2A/+3 multi-stage, PS/2 via Next/DivMMC/Harlequin), debounce/auto-repeat/redefine patterns, 10 pitfalls |
| [mouse.md](03_io/peripherals/mouse.md) | **Mouse Interfaces** — Kempston Mouse (8-bit absolute counters at `#FBDF`/`#FFDF`/`#FADF`, quadrature decode in hardware) vs AMX Mouse (1-bit relative polling at `#1F`/`#3F`/`#DF`, conflict with Kempston joystick), Kempston Mouse Turbo PS/2, K-MOUSE Turbo, Next PS/2 mouse, PS/2 protocol primer, 10 pitfalls |
| [joystick.md](03_io/peripherals/joystick.md) | Joystick interfaces: Kempston #1F, Sinclair/Interface 2, Cursor/Protek/AGF, Fuller, Timex, clone built-ins, unified multi-standard reader |
| [printers.md](03_io/peripherals/printers.md) | **Printers** — ZX Printer (1981, spark / electro-erosion, port `#FB` with `A2=0` decode, paper-start latch bit 7, next-pixel latch bit 0, +9V power removed on +2A/+3), Alphacom 32 thermal alternative, Centronics adapters (Kempston/DK'Tronics data `#0F` / status `#1F` / hardware-strobe on write), Soviet SM640 (IEEE 488/IEC 625) and SM646 (Centronics, GOST 19768-74 Cyrillic), Retro-Printer modern emulation, 10 pitfalls |
| [zx_bus.md](03_io/peripherals/zx_bus.md) | **ZX Bus** — the 56-pin (28+28) expansion edge connector: full pinout, signal groups (address / data / control / interrupts / power), per-model differences (16K/48K vs 128K/+2 vs +2A/+3 — `+9V`/`/ROMCS` removal, `/ROM1OE`+`/ROM2OE` replacement), `/ROMCS` overlay trick, no `/RAMCS`, `M1`-triggered overlays, DMA via `/BUSRQ`/`/BUSACK`, peripheral stacking order, 12 pitfalls |
| [mb02.md](03_io/peripherals/mb02.md) | **MB-02 / MB-02+** — Czech all-in-one disk/DMA/memory/RTC/IDE expansion (8BC group, ~1996; ~90 units made): WD2797 FDC with HD floppies (1.4-1.8 MB), Z80-DMA (RFT U858D required due to BS-DOS init-order bug), 128K-512K SRAM, RTC-72421, full port map, BS-DOS, Hood's NMI menu, MB03+ Ultimate FPGA successor |
| [video_output.md](03_io/peripherals/video_output.md) | **Video Output** — physical video output stage of every Spectrum model. 48K RF-only path (ULA Y/U/V → LM1889 → RF modulator on UHF ch.35/36) vs 128K/+2 TEA2000-based RGB+composite path vs +2A/+3 Amstrad 40077 gate-array path with RGB only; 8-pin DIN 45326 monitor socket pinouts for all three variants (128K TTL RGB vs +2 configurable via LK1-LK8 jumpers vs +2A/+3 with `+12V` on pins 1/5 and audio on 3); composite video vs composite sync distinction; SCART cable wiring tables (128K needs diode Bright mixing; +2 internal mixing; +2A/+3 requires 330 Ω series R for proper levels); 48K composite mod (LM1889 tap + 2N3904 buffer); S-Video alternative (Redhawk PCB); VGA/HDMI adapters (GBS-8200 with gbscontrol, OSSC, RGB-to-HDMI, ZX-VGA-JOY); Soviet clone composite outputs; 12 pitfalls |
| [z_controller.md](03_io/peripherals/z_controller.md) | **Z-Controller** — Russian multi-I/O peripheral designed by Alexey Zhabin (KingOfEvil) in 2007. Combines PS/2 keyboard, PS/2 mouse (Kempston Mouse emulation), Nemo IDE-compatible CompactFlash/hard disk, and SPI-mode SD card on a single ZX Bus board. Two-chip architecture: Altera EPM7128 CPLD (port decode + IDE latch + mouse registers) + KR1878VE1 MCU (PS/2 scan codes). Not bootable from SD; software support is Russian-scene-specific (Wild Disk Copier v1.21+, iS-DOS); functionality carried forward into MB03+ Ultimate FPGA and ZX Spectrum Neo |
| [lightgun.md](03_io/peripherals/lightgun.md) | **Magnum Light Phaser** — Amstrad's 1987 light gun, last first-party ZX Spectrum peripheral. Photo-diode + lens + trigger microswitch; CRT raster-beam detection. Three interface variants: +2/+2A/+3 AUX port (8-pin), 48K/128K Toastrack ZX Bus edge connector + MIC socket box, C64 user port + control port (uses VIC-II hardware light-pen input `$D013`/`$D014`). ZX Spectrum ULA has **no light-pen register** — detection is entirely software-driven (sensor pulse → ULA `/INT` → software T-state count → per-model calibration table for 48K/128K/+2/+2A/+3). ~15 known Spectrum titles (6 bundled, 9 separately-sold); rebranded variants: Trojan Phazer (white), Cheetah Defender, MARPES — all interchangeable; Stack Light Rifle is **incompatible** (emulates Kempston joystick). **CRT-only — does not work on LCD/plasma/OLED**; Sinden/GUN4IR are modern IR-LED-bar alternatives. 12 pitfalls |

*See [03_io/peripherals/README.md](03_io/peripherals/README.md) for the section index. All 12 peripheral articles complete.*

### 07 — Demoscene ✅ COMPLETE

#### History & Culture

| Article | Description |
|---------|-------------|
| [demoscene_history.md](07_demoscene/demoscene_history.md) | ZX Spectrum demoscene: Western origins, Soviet explosion, modern revival, cultural impact |
| [soviet_demo_scene.md](07_demoscene/soviet_demo_scene.md) | Russian/Ukrainian scene: Pentagon-centric development, FidoNet era, notable groups |
| [demoscene_platforms.md](07_demoscene/demoscene_platforms.md) | Cross-platform comparison: Spectrum vs C64 vs Amiga vs Atari ST vs MSX vs Amstrad CPC |

#### Techniques

| Article | Description |
|---------|-------------|
| [effects_catalog.md](07_demoscene/effects_catalog.md) | Visual effects catalog: plasma, raycasting, 3D objects, multicolor, zoomers, tunnel effects, copper bars |
| [multicolor_techniques.md](07_demoscene/multicolor_techniques.md) | Multicolor / attribute interrupt: 8×1 and 8×2 color resolution, race-the-beam timing, per-model differences |
| [precalc_trigonometry.md](07_demoscene/precalc_trigonometry.md) | Sine tables, fixed-point math, interpolation, compression of lookup tables |
| [compression_packing.md](07_demoscene/compression_packing.md) | 25 crunchers across 4 generations: ZX0/ZX1/ZX2/MegaLZ/Pletter/HRUM, depackers, RCS |
| [size_coding.md](07_demoscene/size_coding.md) | 256 B / 1 K / 4 K / 16 K intro competitions: squeeze, reuse, math tricks, compression, ROM routines |

#### Frameworks & Notable Works

| Article | Description |
|---------|-------------|
| [demo_frameworks.md](07_demoscene/demo_frameworks.md) | Demo frameworks: effect sequencing, music synchronisation, memory layout, ISR architecture, part transitions |
| [notable_demos.md](07_demoscene/notable_demos.md) | Analysis of landmark demos across four eras: Crack Intro (1986–89), Western Golden (1990–96), Soviet Peak (1996–2005), Modern Revival (2010–present) |
| [1bit_music_scene.md](07_demoscene/1bit_music_scene.md) | 1-bit beeper music scene: hardware, techniques, engine lineage, composers, community |

*See [07_demoscene/README.md](07_demoscene/README.md) for the section index.*

### 00 — Overview · 03 — I/O · 08 — RE · 09 — Toolchain · 10 — References · 11 — Emulation

**Section 03 — I/O (Snapshots / Storage / Peripherals / Networking)**

*Snapshots & Replay sub-section: ✅ COMPLETE (4/4). Tape sub-section: ✅ COMPLETE (6/6). Floppy sub-section: ✅ COMPLETE (13/13). Hard Disk / SD sub-section: ✅ COMPLETE (6/6). Peripherals sub-section: ✅ COMPLETE (1/1). Networking sub-section: ✅ COMPLETE (6/6).*

**Snapshots & Replay** — machine-state capture formats ([sub-section README](03_io/snapshots/README.md))

| Article | Description |
|---------|-------------|
| [sna_format.md](03_io/snapshots/sna_format.md) | **.SNA snapshot format** — the original 1992 format (JPP emulator), 48K and 128K variants, 27-byte header, PC-on-the-stack trick, limitations |
| [z80_format.md](03_io/snapshots/z80_format.md) | **.Z80 snapshot format** — the 1994 "rich" format by Glen Lleston, three versions (v1 48K, v2 128K, v3 clones+AY), hardware IDs, RLE compression |
| [szx_format.md](03_io/snapshots/szx_format.md) | **.SZX snapshot format** — the modern ZEsarUX chunk-based (IFF-like) format, standard chunks (Z80R, RAM, AY16, CFGR), extensibility via skip-unknown |
| [rzx_format.md](03_io/snapshots/rzx_format.md) | **.RZX replay format** — 2001 input-recording format for the RZX Archive, block-based, cryptographic signing, cycle-accurate replay |

**Storage Media Formats** — tape, floppy, HDD, SD ([sub-section README](03_io/storage/README.md))

| Article | Description |
|---------|-------------|
| [tape_interface.md](03_io/storage/tape_interface.md) | **Tape interface hardware** — EAR/MIC circuits, ULA, port `#FE` bit layout, ROM routines (SA-BYTES, LD-BYTES), pilot/sync pulses, bit encoding, turbo loaders |
| [tape_format.md](03_io/storage/tape_format.md) | **Tape data format** — 17-byte header structure, four block types (Program/Array/Code), XOR checksum, multi-block files |
| [tap_format.md](03_io/storage/tap_format.md) | **.TAP file format** — Thomas Schreiber's 1996 minimal format, just blocks with 2-byte length prefixes |
| [tzx_format.md](03_io/storage/tzx_format.md) | **.TZX file format** — Tomaz Kac's 1996 comprehensive format, 30+ block types, turbo loader support, format of choice for preservation |
| [csw_format.md](03_io/storage/csw_format.md) | **.CSW Compressed Square Wave** — Simon Owen's 2001 pulse-level preservation format, RLE compression, for analog protections |
| [pzx_format.md](03_io/storage/pzx_format.md) | **.PZX format** — Fredrik Öhrström's 2010 chunk-based pulse format, T-state pulse widths, cycle-exact by design |

**Floppy Disk** — physical layer, hardware interfaces, 4 logical formats, 8 image formats ([sub-section README](03_io/storage/README.md))

| Article | Description |
|---------|-------------|
| [mfm_encoding.md](03_io/storage/mfm_encoding.md) | **MFM signal layer** — IBM 3740 sector format, MFM bit encoding, address/data marks, CRC16, gap structure, 250 kbit/s data rate |
| [fdc_vg93.md](03_io/storage/fdc_vg93.md) | **WD1793 / KR1818VG93 FDC chip** — 4-register file, Type I/II/III/IV commands, status bits, Soviet clone, turbo mods |
| [beta_disk_interface.md](03_io/storage/beta_disk_interface.md) | **Beta Disk Interface** (Soviet standard) — WD1793, port map, TR-DOS ROM bank switching, cable, variants |
| [plus3_floppy.md](03_io/storage/plus3_floppy.md) | **+3 floppy hardware** — WD1772-PH, port map, 720 KB geometry, cable pinout, modern replacements |
| [trd_disk_format.md](03_io/storage/trd_disk_format.md) | **TR-DOS logical format** (Soviet, 800 KB DSDD-10) — 128 entries × 16 bytes, sector allocation, file types |
| [plus3_dos_format.md](03_io/storage/plus3_dos_format.md) | **+3DOS logical format** (CP/M derivative, 720 KB DSDD-9) — 32-byte entries, 1 KB blocks, extents, DPB |
| [cpm_disk_format.md](03_io/storage/cpm_disk_format.md) | **CP/M 2.2 disk format** — BIOS/BDOS/CCP/TPA, FCB, DPB, +3/ATM Turbo/Sprinter variants |
| [opus_discovery_format.md](03_io/storage/opus_discovery_format.md) | **Opus Discovery / MGT format** (UK, 800 KB DSDD-10) — WD1770, 256-byte entries, sector bitmap, linked-list chaining |
| [trd_scl_formats.md](03_io/storage/trd_scl_formats.md) | **.TRD / .SCL image formats** — TR-DOS containers (raw sector dump vs file-level backup) |
| [dsk_fdi_formats.md](03_io/storage/dsk_fdi_formats.md) | **.DSK / .EDSK / .FDI image formats** — CP/M / +3DOS / Opus containers |
| [udi_format.md](03_io/storage/udi_format.md) | **.UDI universal flux-level image** — preserves every magnetic transition |
| [scp_format.md](03_io/storage/scp_format.md) | **.SCP SuperCard Pro flux-level image** — gold-standard preservation format |
| [disk_format_overview.md](03_io/storage/disk_format_overview.md) | **Top-level comparison** — IBM 3740 physical layer, 4 logical formats, 8 image formats, decision tree |

**Hard Disk / SD** — IDE / SD interfaces, FAT filesystem, image formats ([sub-section README](03_io/storage/README.md))

| Article | Description |
|---------|-------------|
| [hdd_overview.md](03_io/storage/hdd_overview.md) | **Top-level overview** — three generations (floppy → IDE → SD), why HDD mattered for the Soviet scene, the unifying FAT abstraction |
| [ide_interface.md](03_io/storage/ide_interface.md) | **IDE / PATA interfaces** — 40-pin connector, port maps for DivIDE/SMUC/Nemo/ZC/ATM/KAY, Z80 read loop sketch |
| [divide_divmmc.md](03_io/storage/divide_divmmc.md) | **DivIDE / DivMMC hardware** — board architecture, NMI boot, conmem/mapram paging, divman/divese TR-DOS image emulation (hardware companion to esxdos.md) |
| [sd_interface.md](03_io/storage/sd_interface.md) | **SD card interfaces (SD-SPI)** — SPI command frames, 5-step init handshake, Z80 bit-bang sketch, port maps for DivMMC/ZXMMC/Next/ZC |
| [hdd_partitioning.md](03_io/storage/hdd_partitioning.md) | **Partitioning & filesystems** — MBR + 4-entry partition table, FAT12/16/32, BPB, directory entries, LFN, cluster allocation, IS-DOS |
| [hdf_mgt_formats.md](03_io/storage/hdf_mgt_formats.md) | **Image formats** (.HDF / .IMG / .MGT / .VHD) — raw vs headered HDF, four-names-for-same-thing, loopback mounting, sparse/compression |
| [joystick.md](03_io/peripherals/joystick.md) | Joystick interfaces: Kempston #1F, Sinclair/Interface 2, Cursor/Protek/AGF, Fuller, Timex, clone built-ins, unified multi-standard reader |

**Networking** — ZX Net, modems, modern WiFi/Ethernet ([sub-section README](03_io/networking/README.md))

| Article | Description |
|---------|-------------|
| [zx_net.md](03_io/networking/zx_net.md) | **ZX Net (1983)** — Sinclair's classroom LAN via Interface 1, 64-station daisy-chain, polling MAC, `*NET` / `*LOAD name N` ROM API, comparison with Econet |
| [modems.md](03_io/networking/modems.md) | **Telephone modems** — acoustic couplers (V.21), direct-connect (V.23/V.22/V.32/V.34), Interface 1 RS-232, Prism VTX-5000, Prestel/Micronet 800, Russian FidoNet, BBS software |
| [spectranet.md](03_io/networking/spectranet.md) | **Spectranet (2007+)** — Andrew Owen's Ethernet + TCP/IP interface, ENC28J60 SPI, BSD-style socket API via `RST #08`, software ecosystem (telnet/FTP/HTTP/IRC) |
| [zifi.md](03_io/networking/zifi.md) | **ZiFi (2014)** — ESP8266 WiFi module + Hayes AT command set over UART, 3.3V/5V level shifting, ESP-01/ESP-12 modules, comparison with Spectranet |
| [esp_wifi.md](03_io/networking/esp_wifi.md) | **ESP8266/ESP32 family** — broader WiFi solution landscape, boot modes, topologies (serial/SPI/parallel), firmware choices (AT/ESP-NOW/custom), cross-platform companion projects (WiC64, WiFi232) |
| [zx_next_wifi.md](03_io/networking/zx_next_wifi.md) | **ZX Spectrum Next WiFi** — built-in ESP-12 on SPI (not UART), custom Next-team firmware, LwIP TCP/IP stack, NextBASIC `*WIFI` commands, up to 8 TCP/UDP connections with SSL/TLS |

---

### 08 — Reverse Engineering ✅ COMPLETE (7 articles)

**Section 08 — Reverse Engineering** — RE methodology, protection cracking, game reversing, code compression analysis, snapshot repair ([section README](08_reverse_engineering/README.md))

| Article | Description |
|---------|------------|
| [methodology.md](08_reverse_engineering/methodology.md) | **RE methodology hub**: starting points (tape/disk/snapshot formats), snapshot-driven analysis, standard workflow, heuristics, patching, tools, pitfalls, ethics |
| [protection_techniques.md](08_reverse_engineering/protection_techniques.md) | **Protection catalog**: tape loaders (Speedlock, Alkatraz), disk schemes (weak bits, non-standard sectors), NMI/snapshot defenses, memory integrity, code obfuscation, bypass techniques |
| [analysis_techniques.md](08_reverse_engineering/analysis_techniques.md) | **Static/dynamic analysis**: SkoolKit disassembly workflow, code/data separation, ROM call labeling, ZEsarUX/DeZog debugging, trace logging, reverse debugging, memory diffing |
| [protection_cracking.md](08_reverse_engineering/protection_cracking.md) | **Protection cracking**: Speedlock/Alkatraz decryption analysis, timing check bypass, disk protection defeat, NMI countermeasure defeat, clean snapshot technique |
| [game_reversing.md](08_reverse_engineering/game_reversing.md) | **Game reversing**: engine identification (Ultimate, Ocean, Graftgold, Hewson), sprite/map/music ripping, cheat code creation, save game analysis, Z80-to-C reconstruction |
| [code_crunching.md](08_reverse_engineering/code_crunching.md) | **Code compression RE**: packer survey (MegaLZ, HRUM, Hrust, ZX0), format identification, LZSS fundamentals, generic depacker template, overlap depacking |
| [snapshot_repair.md](08_reverse_engineering/snapshot_repair.md) | **Snapshot repair**: fixing corrupted .SNA/.Z80, header validation, PC/SP repair, decompression error handling, format conversion, fixing mid-load crashes |

### 11 — Emulation ✅ COMPLETE (20 articles)

**Section 11 — Emulation** — software emulators, FPGA cores, MCU-based chip replacements

**Software Emulators** — host-side Spectrum emulation ([sub-section README](11_emulation/software/README.md))

| Article | Description |
|---------|-------------|
| [fuse.md](11_emulation/software/fuse.md) | **Fuse** — Free Unix Spectrum Emulator, the canonical cross-platform accurate emulator, GTK/Qt/SDL frontends, debuggers |
| [zesarux.md](11_emulation/software/zesarux.md) | **ZEsarUX** — Second-cycle-exact emulator with TS-Conf, ZXEvolution, Pentagon support, comprehensive debugger, retro rendering options |
| [cspect.md](11_emulation/software/cspect.md) | **CSpect** — Windows-based accurate emulator with NextReg/layer-2/sprite support, popular for ZX Spectrum Next development |
| [emulator_comparison.md](11_emulation/software/emulator_comparison.md) | **Emulator comparison** — Fuse vs ZEsarUX vs CSpect vs UnrealSpeccy vs Spectaculator, accuracy, debugging, features matrix |
| [cycle_exact_accuracy.md](11_emulation/software/cycle_exact_accuracy.md) | **Cycle-exact accuracy** — frame timing divergence, CRT vs LCD, host sync strategies, AY audio clocks, judder mitigation, worst-case Pentagon@60Hz conclusion |
| [test_suites.md](11_emulation/software/test_suites.md) | **Test suites** — ZEXALL, FUSE test suite, Sensible Software tests, Yamagraph, application-specific test ROMs |

**FPGA Cores** — synthesised hardware re-implementations ([sub-section README](11_emulation/fpga/README.md))

| Article | Description |
|---------|-------------|
| [fpga_implementation.md](11_emulation/fpga/fpga_implementation.md) | **FPGA Spectrum implementations** — why FPGA differs from software emulation, gate-level reconstruction, vendor families, development workflow |
| [fpga_timing_accuracy.md](11_emulation/fpga/fpga_timing_accuracy.md) | **Timing accuracy in FPGA cores** — sub-ns cycle-true reconstruction, ULA contention replication, video timing, audio clock matching |
| [harlequin_sizif.md](11_emulation/fpga/harlequin_sizif.md) | **Harlequin & SIZIF** — Maxim Sichkov's gate-level ULA replacements for original Spectrum motherboards, repair-and-upgrade boards |
| [zxevo.md](11_emulation/fpga/zxevo.md) | **ZX Evolution** — TS-Conf/Baseconf, ATM Turbo spiritual successor, Pentagon-compatible, configurable video modes, IDE/SD |
| [zx_uno_core.md](11_emulation/fpga/zx_uno_core.md) | **ZX-Uno** — compact FPGA board, all-Spectrum-on-one-board, multi-core (Pentagon/Scorpion/48K/128K), WiFi and SD built-in |
| [mist_mister_core.md](11_emulation/fpga/mist_mister_core.md) | **MiST & MiSTer cores** — Spectrum core on the MiSTer FPGA platform, alongside dozens of other retro computers, accurate and extensible |

**MCU Chip Replacement** — replacing vintage silicon with microcontrollers ([sub-section README](11_emulation/mcu/README.md))

| Article | Description |
|---------|-------------|
| [mcu_z80.md](11_emulation/mcu/mcu_z80.md) | **Z80 on MCU** — bit-banged and PIO-driven cycle-true Z80 emulation in firmware, libz80/z80ex cycle engines, drop-in chip replacement |
| [mcu_ula.md](11_emulation/mcu/mcu_ula.md) | **ULA on MCU** — RP2040 PIO reconstruction of the Ferranti ULA, contention timing, video pipeline, floating bus behavior |
| [mcu_fdc_vg93.md](11_emulation/mcu/mcu_fdc_vg93.md) | **WD1793/VG93 on MCU** — bit-banged floppy controller replacement, MFM decoding in firmware, SD-card image backing |
| [mcu_psg_ay.md](11_emulation/mcu/mcu_psg_ay.md) | **AY-3-8910/YM2149 on MCU** — software PSG synthesis, RP2040 PWM/DMA audio, drop-in pin-compatible replacements |
| [mcu_keyboard.md](11_emulation/mcu/mcu_keyboard.md) | **Keyboard on MCU** — PS/2 keyboard matrix scanning, scan-code translation, 8×5 Spectrum matrix emulation, debounce |
| [mcu_video_adapter.md](11_emulation/mcu/mcu_video_adapter.md) | **Video adapter on MCU** — RGB/HDMI output from RP2040 PIO, scanline generation, multicolor effects, layer-2 style overlays |
| [mcu_sd_interface.md](11_emulation/mcu/mcu_sd_interface.md) | **SD card interface on MCU** — SPI/SDIO from MCU, file-backed disk images, DivMMC/DivIDE emulation on a single MCU |
| [n_go.md](11_emulation/mcu/n_go.md) | **N-Go — complete Spectrum on MCU** — synthesis article, RP2040 multicore architecture (Z80 core + ULA + PSG + SD), firmware structure |
| [mcu_design_patterns.md](11_emulation/mcu/mcu_design_patterns.md) | **MCU design patterns** — bus interfacing (memory-mapped/port/IO/DMA), 74HCT vs 74HC level shifting, RP2040 PIO timing-critical I/O, GPIO drive, ring buffers, lock-free SPSC queues, common pitfalls |

### 10 — References ✅ COMPLETE (10 articles)

**Section 10 — References** — lookup tables and pin/byte/timing references ([section README](10_references/README.md))

| Article | Description |
|---------|-------------|
| [z80_opcode_table.md](10_references/z80_opcode_table.md) | One-page Z80 opcode lookup: every documented instruction by group with byte count, T-states, and flag effects |
| [io_port_map.md](10_references/io_port_map.md) | Complete I/O port reference: every port across all models, Black_Cat table with annotations, decoding bitmasks, per-model differences |
| [character_set.md](10_references/character_set.md) | ZX Spectrum character set: code ranges, ROM font layout, UDG system, CHARS redirection |
| [color_palette.md](10_references/color_palette.md) | Standard 15-colour palette (FUSE/Skoolkid/ZEsarUX variants), ULAplus 64-colour, ZX Spectrum Next 256-colour |
| [memory_maps.md](10_references/memory_maps.md) | Consolidated memory maps for every model (16K/48K, 128K/+2, +2A/+3, Pentagon, Scorpion, ATM Turbo, Next) — contended regions, banking registers, RAMTOP defaults, compatibility cheat sheet |
| [basic_token_table.md](10_references/basic_token_table.md) | Sinclair BASIC token table: byte values and tokenisation rules for 48K/128K/+2/+2A/+3 ROMs — control codes, function tokens, UDGs, block graphics |
| [error_codes.md](10_references/error_codes.md) | All BASIC/DOS error codes — 10 Sinclair BASIC, +3 DOS (12), TR-DOS (Russian), ESXDOS (POSIX-style), IS-DOS, NextZXOS — recovery patterns |
| [timing_reference.md](10_references/timing_reference.md) | Cycle-exact timing tables — CPU clocks per model, video frame timings (48K/128K/Pentagon), contention delay tables, INT/NMI timing, common instruction T-state counts |
| [pinouts.md](10_references/pinouts.md) | Pin-by-pin reference — 48K/128K/+2 expansion edge connector (A and B side), Z80 40-pin DIP, AY-3-8912 28-pin DIP, joystick ports, Kempston mouse, EAR/MIC jacks, power connectors |
| [rom_routines.md](10_references/rom_routines.md) | ROM entry points — restart vectors, character output, keyboard, tape, math/calculator, 128K-specific routines, calling conventions with examples |

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
53. [Software Protection Techniques](08_reverse_engineering/protection_techniques.md) — tape loaders (Speedlock, Alkatraz), disk schemes, NMI/snapshot defenses (anti-debugging countermeasures table, hardware vs software debugger comparison), snapshot devices (Multiface, MAGIC button, Shadow Monitor), memory integrity, code obfuscation, bypass techniques

**Bridge to advanced optimization:**

36. [Z80 Coding Practices](01_cpu/z80_coding_practices.md)

**Coming from modern platforms:**

37. [Z80 vs Modern](01_cpu/z80_vs_modern.md)

---

See [PLAN.md](PLAN.md) for the full knowledge base catalog and writing priorities.
