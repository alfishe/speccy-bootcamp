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

### 03 — I/O — Peripherals (in progress)

| Article | Description |
|---------|-------------|
| [interface1.md](03_io/peripherals/interface1.md) | **ZX Interface 1** (Sinclair, 1983) — triple-function expansion: Microdrive controller + RS-232 + ZX Net LAN. 8 KB shadow ROM paging via `M1` fetch at `#0008`, hook codes `#1B`–`#32`, ZX Microdrive sector format (254 × 543 bytes, bespoke non-CRC checksum), bit-bang RS-232, single-wire token bus for 64 Spectrums |
| [joystick.md](03_io/peripherals/joystick.md) | Joystick interfaces: Kempston #1F, Sinclair/Interface 2, Cursor/Protek/AGF, Fuller, Timex, clone built-ins, unified multi-standard reader |

*See [03_io/peripherals/README.md](03_io/peripherals/README.md) for the section index. Planned: keyboard, mouse, lightgun, Interface 2, Multiface, Z-Controller, MB02, ZX Bus, printers, video output.*

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

*Snapshots & Replay sub-section: ✅ COMPLETE (4/4). Tape sub-section: ✅ COMPLETE (6/6). Floppy sub-section: ✅ COMPLETE (13/13). Hard Disk / SD sub-section: ✅ COMPLETE (6/6). Other I/O sub-sections (peripherals, networking) are in progress — see [PLAN.md](PLAN.md).*

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

**Other sections**

| Article | Description |
|---------|-------------|
| [io_port_map.md](10_references/io_port_map.md) | Complete I/O port reference: every port across all models, Black_Cat table with annotations, decoding bitmasks, per-model differences |
| [cycle_exact_accuracy.md](11_emulation/software/cycle_exact_accuracy.md) | Frame timing divergence, CRT vs LCD, host sync strategies, AY audio clocks, judder mitigation techniques, emulator comparison, worst-case Pentagon@60Hz conclusion |

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
