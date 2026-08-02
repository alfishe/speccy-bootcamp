# ZX Spectrum Knowledge Base — Master Plan

> **Status**: Draft for review
> **Scope**: Three parallel tracks — Original Sinclair/Amstrad, Soviet clones, New Gen
> **Audience**: All — original developers, demoscene, Soviet clone community, New Gen, FPGA/emulation, historians
> **Assembly-first**: Z80 assembly is the primary language; SDCC/z88dk C is respected as minority but important alternative

---

## 1. Directory Structure

```
zx/
├── PLAN.md                          # This file — master plan and article catalog
├── AGENTS.md                        # Quality standards for article writing
│
├── 00_overview/
│   ├── history.md
│   ├── hardware_models.md
│   ├── timeline.md
│   └── glossary.md
│
├── 01_cpu/
│   ├── z80_architecture.md
│   ├── z80_addressing.md
│   ├── z80_flags.md
│   ├── z80_instruction_set.md
│   ├── z80_undocumented.md
│   ├── z80_timing.md
│   ├── z80_interrupts.md
│   ├── z80_vs_modern.md
│   ├── z80_coding_practices.md
│
├── 02_hardware/
│   ├── original/
│   │   ├── README.md
│   │   ├── zx_spectrum_16k_48k.md
│   │   ├── zx_spectrum_128.md
│   │   ├── zx_spectrum_plus2.md
│   │   ├── zx_spectrum_plus2a_plus3.md
│   │   ├── ula_architecture.md
│   │   ├── ula_contention.md
│   │   ├── ula_timing.md
│   │   ├── keyboard_matrix.md
│   ├── clones/
│   │   ├── README.md
│   │   ├── pentagon.md
│   │   ├── pentagon_1024.md
│   │   ├── scorpion.md
│   │   ├── kay.md
│   │   ├── atm_turbo.md
│   │   ├── profi.md
│   │   ├── byte.md
│   │   ├── other_clones.md
│   │   ├── clone_timing.md
│   │   ├── ula_replacements.md
│   │   └── sizif_harlequin.md
│   └── newgen/
│       ├── README.md
│       ├── zx_next.md
│       ├── sprinter.md
│       ├── zx_evo.md
│       ├── ts_conf.md
│       ├── baseconf.md
│       ├── zx_uno.md
│       └── karabas.md
│
├── 03_io/
│   ├── snapshots/
│   │   ├── README.md
│   │   ├── sna_format.md
│   │   ├── z80_format.md
│   │   ├── szx_format.md
│   │   └── rzx_format.md
│   ├── storage/
│   │   ├── README.md
│   │   ├── tape_interface.md
│   │   ├── tape_format.md
│   │   ├── tap_format.md
│   │   ├── tzx_format.md
│   │   ├── csw_format.md
│   │   ├── pzx_format.md
│   │   ├── beta_disk_interface.md
│   │   ├── fdc_vg93.md
│   │   ├── plus3_floppy.md
│   │   ├── disk_format_overview.md
│   │   ├── trd_disk_format.md
│   │   ├── plus3_dos_format.md
│   │   ├── cpm_disk_format.md
│   │   ├── opus_discovery_format.md
│   │   ├── trd_scl_formats.md
│   │   ├── dsk_fdi_formats.md
│   │   ├── udi_format.md
│   │   ├── scp_format.md
│   │   ├── mfm_encoding.md
│   │   ├── hdd_overview.md
│   │   ├── ide_interface.md
│   │   ├── divide_divmmc.md
│   │   ├── sd_interface.md
│   │   ├── hdf_mgt_formats.md
│   │   └── hdd_partitioning.md
│   ├── peripherals/
│   │   ├── README.md
│   │   ├── keyboard.md
│   │   ├── joystick.md
│   │   ├── mouse.md
│   │   ├── lightgun.md
│   │   ├── interface1.md
│   │   ├── interface2.md
│   │   ├── multiface.md
│   │   ├── z_controller.md
│   │   ├── mb02.md
│   │   ├── zx_bus.md
│   │   ├── printers.md
│   │   ├── video_output.md
│   │   ├── sound_overview.md
│   │   ├── ay_3_8912.md
│   │   ├── turbosound.md
│   │   ├── turbosound_fm.md
│   │   ├── covox_sounDrive.md
│   │   ├── gs_general_sound.md
│   │   ├── neogs.md
│   │   ├── moonsound.md
│   │   ├── zxm_soundcard.md
│   │   ├── saa1099.md
│   │   ├── zx_next_audio.md
│   │   ├── stereo_audio.md
│   │   └── zx_spectrum_48k_audio_routing.md
│   └── networking/
│       ├── README.md
│       ├── zx_net.md                      # ✅ Done (Jul 2026)
│       ├── modems.md                      # ✅ Done (Jul 2026)
│       ├── spectranet.md                  # ✅ Done (Jul 2026)
│       ├── zifi.md                        # ✅ Done (Jul 2026)
│       ├── esp_wifi.md                    # ✅ Done (Jul 2026)
│       └── zx_next_wifi.md                # ✅ Done (Jul 2026) — section complete
│
├── 04_operating_systems/
│   ├── README.md
│   ├── rom_48k.md
│   ├── rom_128k.md
│   ├── rom_plus2.md
│   ├── trdos.md
│   ├── plus3dos.md
│   ├── is_dos.md
│   ├── nedo_dos.md
│   ├── esxdos.md
│   ├── nextzxos.md
│   ├── evo_os.md
│   ├── cpm.md
│   ├── fuzix.md
│   ├── basic_dialects.md
│   └── rom_versions.md
│
├── 05_development/
│   ├── 01_basic/
│   │   ├── README.md
│   │   ├── basic_intro.md
│   │   ├── basic_graphics.md
│   │   ├── basic_sound.md
│   │   ├── basic_file_io.md
│   │   ├── basic_peek_poke.md
│   │   ├── basic_advanced.md
│   │   ├── basic_128k.md
│   │   └── basic_dialects_comparison.md
│   ├── 02_assembly/
│   │   ├── README.md
│   │   ├── assembly_intro.md
│   │   ├── rom_calls.md
│   │   ├── rom_calls_128k.md
│   │   ├── stack_and_rst.md
│   │   ├── assembly_patterns.md
│   │   ├── assembly_optimization.md
│   │   ├── c_with_z88dk.md
│   │   ├── c_with_sdcc.md
│   │   └── mixed_c_asm.md
│   ├── 03_memory_and_io/
│   │   ├── README.md
│   │   ├── io_port_decoding.md
│   │   ├── memory_and_io_48k.md
│   │   ├── memory_and_io_128k.md
│   │   ├── memory_and_io_plus3.md
│   │   ├── memory_and_io_pentagon.md
│   │   ├── memory_and_io_next.md
│   │   ├── bank_switching_patterns.md
│   │   ├── contention_model.md
│   │   ├── screen_layout.md
│   │   └── assets/                    # Generated SVG diagrams
│   │       ├── 48k_port_decoding.svg
│   │       ├── 128k_port_decoding.svg
│   │       ├── plus3_port_decoding.svg
│   │       └── pentagon_port_decoding.svg
│   ├── 04_interrupts/
│   │   ├── interrupt_overview.md
│   │   ├── im1_programming.md
│   │   ├── im2_programming.md
│   │   ├── isr_patterns.md
│   │   ├── interrupt_timing.md
│   │   ├── race_the_beam.md
│   │   ├── nmi.md
│   │   ├── interrupt_antipatterns.md
│   │   └── interrupt_cookbook.md
│   ├── 05_display_and_timing/
│   │   ├── README.md
│   │   ├── video_frame_overview.md
│   │   ├── video_frame_48k.md
│   │   ├── video_frame_128k.md
│   │   ├── video_frame_plus2a_plus3.md
│   │   ├── video_frame_pentagon.md
│   │   ├── video_frame_scorpion.md
│   │   ├── video_frame_other_soviet.md
│   │   ├── video_frame_next.md
│   │   ├── video_frame_sprinter.md
│   │   ├── video_frame_zxevo.md
│   │   ├── video_frame_comparison.md
│   │   ├── raster_timing.md
│   │   ├── contention_timing.md
│   │   ├── floating_bus.md
│   │   ├── border_effects.md
│   │   ├── clone_video_modes.md
│   │   ├── interlace_and_flicker.md
│   │   ├── color_system.md
│   │   └── crt_output.md
│   ├── 06_graphics/
│   │   ├── README.md
│   │   ├── screen_access.md
│   │   ├── fonts_and_text.md
│   │   ├── monochrome_techniques.md
│   │   ├── color_clash_workarounds.md
│   │   ├── attribute_manipulation.md
│   │   ├── sprites_and_masking.md
│   │   ├── sprite_engines.md
│   │   ├── scrolling.md
│   │   ├── double_buffering.md
│   │   ├── multicolor_overview.md
│   │   ├── multicolor_techniques.md
│   │   ├── multicolor_engines.md
│   │   ├── ula_plus.md
│   │   ├── dual_screen.md
│   │   ├── blit_techniques.md
│   │   ├── clipping_and_regions.md
│   │   ├── 3d_line_wireframe.md
│   │   ├── 3d_filled_sorting.md
│   │   ├── raycasting.md
│   │   ├── isometric.md
│   │   ├── 3d_performance.md
│   │   ├── timex_video_modes.md
│   │   ├── next_layer2_graphics.md
│   │   └── next_tilemap.md
│   ├── 07_audio/                     # MOVED to 06_sound/ — see below
│   ├── 08_dos_tape/
│   │   ├── README.md
│   │   ├── tape_programming.md
│   │   ├── trdos_programming.md
│   │   ├── dos_programming.md
│   │   ├── file_format_handling.md
│   │   └── mass_storage_programming.md
│   ├── 09_gamedev/
│   │   ├── README.md
│   │   ├── game_loop.md
│   │   ├── sprite_engines.md
│   │   ├── collision_detection.md
│   │   ├── level_design.md
│   │   ├── asset_pipeline.md
│   │   ├── input_handling.md
│   │   ├── sound_integration.md
│   │   ├── ai_patterns.md
│   │   └── game_case_studies.md
│   └── 10_demoscene/                  # MOVED to 07_demoscene/ — see below
│
├── 06_sound/                         # ✅ SECTION COMPLETE
│   ├── README.md                      # ✅ Section index
│   ├── synthesis/
│   │   ├── README.md
│   │   ├── ay_ym_synthesis.md         # ✅ Comprehensive AY/YM sound generation
│   │   ├── ay_ym_techniques.md        # ✅ Sync-square, PWM, SID-sound, buzzer bass, samples
│   │   ├── ay_vs_ym.md                # ✅ AY vs YM technical comparison (DAC + emulation)
│   │   ├── ay_ym_perception.md        # ✅ Perception, emotion, hardware soul
│   │   ├── beeper_synthesis.md        # ✅ Done
│   │   ├── shiru_ear_shaver_analysis.md # ✅ Shiru's Ear Shaver engine teardown
│   │   └── multitrack_multichip.md    # ✅ Multi-chip outline
│   ├── hardware/
│   │   ├── README.md
│   │   ├── sound_overview.md          # ✅ Ecosystem overview + decision guide
│   │   ├── ay_3_8912.md               # ✅ AY/YM PSG silicon reference
│   │   ├── turbosound.md              # ✅ Dual/triple AY bank-switching
│   │   ├── turbosound_fm.md           # ✅ YM2203 OPN FM expansion
│   │   ├── covox_sounDrive.md         # ✅ Covox/SounDrive + TLC7226CN quad DAC
│   │   ├── gs_general_sound.md        # ✅ General Sound Z80 coprocessor
│   │   ├── moonsound.md               # ✅ MoonSound (OPL4) wavetable + FM
│   │   ├── saa1099.md                 # ✅ Philips SAA1099 PSG
│   │   ├── zx_next_audio.md           # ✅ ZX Spectrum Next 3×AY + DMA + beeper
│   │   └── stereo_audio.md            # ✅ ABC/ACB/BytesDelight stereo mods
│   └── trackers_and_formats/
│       ├── README.md                  # ✅ Section index (9 articles)
│       ├── tracker_history.md         # ✅ 30-year history (Bzyk/Golden Disk/Bulba/Targhan)
│       ├── ay_music_formats.md        # ✅ Master format catalogue (361 lines)
│       ├── sound_tracker.md           # ✅ Sound Tracker 1.1 (Bzyk 1990) — first AY grid editor
│       ├── asc_sound_master.md        # ✅ Asc Sound Master (Sendetskiy 1992) — Soviet alternative
│       ├── protracker.md              # ✅ Pro Tracker 1/2/3 (Golden Disk Corp. 1995-97)
│       ├── vortex_tracker.md          # ✅ VTII PC-based PT3 editor (Bulba)
│       ├── arkos_tracker.md           # ✅ AT2/3 modern cross-platform AY tracker
│       ├── pt3_format.md              # ✅ PT3 binary format spec (502 lines)
│       └── psg_format.md              # ✅ PSG register dump spec (270 lines)
│   └── players/                       # ✅ 2-article pair: architecture + comparison
│       ├── README.md                  # ✅ Section index
│       ├── ay_player_routines.md      # ✅ Z80 → AY register writes (507 lines)
│       └── player_comparison.md       # ✅ PT3 vs AKG/AKM/AKY benchmarks (262 lines)
│
├── 07_demoscene/                      # ✅ SECTION COMPLETE (11 articles)
│   ├── README.md                      # ✅ Section index
│   ├── demoscene_history.md           # ✅ 671 lines
│   ├── soviet_demo_scene.md           # ✅ 722 lines
│   ├── demoscene_platforms.md         # ✅ 657 lines
│   ├── effects_catalog.md             # ✅ 711 lines
│   ├── multicolor_techniques.md       # ✅ 781 lines
│   ├── precalc_trigonometry.md        # ✅ 783 lines
│   ├── compression_packing.md         # ✅ 1054 lines
│   ├── size_coding.md                 # ✅ 1044 lines
│   ├── demo_frameworks.md             # ✅ 898 lines
│   ├── notable_demos.md               # ✅ 599 lines
│   └── 1bit_music_scene.md            # ✅ 538 lines
│
├── 08_reverse_engineering/
│   ├── README.md ✅                    # Section index
│   ├── methodology.md ✅               # RE workflow hub
│   ├── protection_techniques.md ✅      # Protection catalog
│   ├── analysis_techniques.md ✅       # Static/dynamic analysis
│   ├── protection_cracking.md ✅       # Speedlock/Alkatraz cracking
│   ├── game_reversing.md ✅            # Asset extraction, cheats
│   ├── code_crunching.md ✅            # Packer survey, depacking
│   └── snapshot_repair.md ✅           # SNA/Z80 repair
│
├── 09_toolchain/
│   ├── README.md                       # ✅ Section index
│   ├── native_toolchain.md ✅           # Survey
│   ├── cross_platform_toolchain.md ✅   # Survey
│   ├── sjasmplus.md ✅                  # Per-tool deep dive
│   ├── z88dk.md ✅                       # Per-tool deep dive
│   ├── sdcc.md ✅                        # Per-tool deep dive
│   ├── debugging.md ✅                   # Per-tool deep dive
│   ├── asset_tools.md ✅                 # Per-tool deep dive
│   ├── disassemblers.md ✅               # Per-tool deep dive
│   ├── assembler_overview.md            # Planned
│   ├── zeus_assembler.md                # ✅ Done (Jul 2026)
│   ├── devpac_gens_mons.md              # ✅ Done (Jul 2026)
│   ├── alasm_sts.md                     # ✅ Done (Jul 2026)
│   ├── xas_assembler.md                 # ✅ Done (Jul 2026)
│   ├── tasm_native.md                   # Planned
│   ├── zxasm_native.md                  # Planned
│   ├── pikasm.md                        # Planned
│   ├── laser_genius.md                  # Planned
│   ├── avras.md                         # Planned
│   ├── spectrum_basic_mcode.md          # Planned
│   ├── pasmo.md                         # Planned
│   ├── z88dk_z80asm.md                  # Planned
│   ├── vasm.md                          # Planned
│   ├── wla_dx.md                        # Planned
│   ├── zmac.md                          # Planned
│   ├── zasm_kio.md                      # Planned
│   ├── tniasm.md                        # Planned
│   ├── rasm.md                          # Planned
│   ├── sarcasm.md                       # Planned
│   ├── tasm_cross.md                    # Planned
│   ├── as_macro_assembler.md            # Planned
│   ├── zdevstudio.md                    # Planned
│   ├── vscode_integration.md ✅          # Per-tool deep dive
│   ├── zxdstudio.md                     # Planned
│   ├── zx_spin.md                       # Planned
│   ├── boriel_zxbasic.md ✅              # Per-tool deep dive
│   # ~~testing.md~~ — descoped (generic test automation is not Spectrum-specific; see debugging.md workflows)
│   # ~~makefiles.md~~ — descoped (build system setup is not Spectrum-specific)
│   # ~~zesarux_debug.md~~ / ~~fuse_debug.md~~ — folded into debugging.md
│
├── 10_references/
│   ├── z80_opcode_table.md
│   ├── io_port_map.md
│   ├── memory_maps.md
│   ├── character_set.md
│   ├── basic_token_table.md
│   ├── rom_routines.md
│   ├── color_palette.md
│   ├── error_codes.md
│   ├── timing_reference.md
│   └── pinouts.md
│
└── 11_emulation/
    ├── software/
    │   ├── README.md
    │   ├── emulator_comparison.md              # ✅ Done (Jul 2026)
    │   ├── cycle_exact_accuracy.md
    │   ├── fuse.md                             # ✅ Done (Jul 2026)
    │   ├── zesarux.md                           # ✅ Done (Jul 2026)
    │   ├── cspect.md
    │   └── test_suites.md                       # ✅ Done (Jul 2026)
    ├── fpga/
    │   ├── README.md
    │   ├── mist_mister_core.md
    │   ├── zx_uno_core.md
    │   ├── zxevo.md
    │   ├── harlequin_sizif.md
    │   ├── fpga_implementation.md
    │   └── fpga_timing_accuracy.md
    └── mcu/
        ├── README.md
        ├── mcu_z80.md
        ├── mcu_ula.md
        ├── mcu_fdc_vg93.md
        ├── mcu_psg_ay.md
        ├── mcu_keyboard.md
        ├── mcu_video_adapter.md
        ├── mcu_sd_interface.md
        ├── n_go.md
        └── mcu_design_patterns.md
│
├── tools/                            # SVG diagram generation tools
│   └── svg_gen/
│       ├── gen_svg.py               # Memory map / contention diagram generator
│       ├── gen_schematic.py          # Gate-level schematic generator (74-series + Cyrillic Soviet chips)
│       ├── README.md
│       ├── GUIDE.md
│       └── schematics/               # JSON configs for schematic SVGs
│           ├── schematic_48k_decoding.json
│           ├── schematic_128k_decoding.json
│           ├── schematic_plus3_decoding.json
│           └── schematic_pentagon_decoding.json
```

> **Design principle**: 12 top-level sections (00-11). Subfolders only where genuine structural divergence exists:
> - `02_hardware/` — three physically different hardware streams
> - `03_io/` — three I/O categories (storage/peripherals/networking)
> - `05_development/` — 8-tier learning progression (audio and demoscene content moved to sections 06/07)
> - `06_sound/` — four sound subsystems (synthesis/hardware/trackers/players)
> - `11_emulation/` — three fundamentally different implementation approaches
>
> All other sections are flat. Articles note track-applicability inline.

---

## 2. Research Sources

### Primary (per track)

| Track | Sources |
|---|---|
| **Original** | World of Spectrum (spectrumcomputing.co.uk), Sinclair documentation, Chris Smith "The ZX Spectrum ULA" book, Complete Spectrum ROM Disassembly |
| **Soviet** | **zx-pk.ru** (most concentrated knowledge — schematics, ROMs, mods, discussions), nedoPC, SpeccyWiki (speccy.info), Russian-language books and magazines |
| **New Gen** | ZX Spectrum Next official docs (zxnext.io), TS-Conf documentation, SpeccyWiki, GitHub repos |
| **Cross-cutting** | Z80 User Manual (Zilog UM0080), z80-documented (undocumented instructions), Z80 opcode references |

### Reference Library (local, READONLY)

`/Volumes/WDC14Tb-3/Consoles/ZX Spectrum/` — contains schematics, datasheets, ROM dumps, test suites, tools, books, emulators, documentation. **NOT comprehensive** — does not replace web research. Use as a starting point and verification source.

### Research Rules

- **Port decoding bitmasks**: Do NOT trust simplified tables. Verify against hardware schematics and FPGA core source code. **Primary port references**:
  - World of Spectrum ports reference: `worldofspectrum.org/faq/reference/ports.htm` — classic original-hardware ports with partial decoding bitmasks
  - Black_Cat's ZX Ports Full Table: `github.com/tslabs/zx-evo/blob/master/pentevo/docs/ZX/zx-ports-full-table.txt` — THE definitive per-model port decoding reference covering System Ports, Peripheral Ports, Shadow Ports, SMUC, Beta 128, ATM IDE, and more — shows hex address, binary decoding pattern (A15–A0), and per-model differences (1=48K, 2=128K, 3=+2, 4=+2A, 5=+3, 6=Scorpion, 7=Pentagon, 8=ProfScorp, 9=Kay, A=ATM, B=?, C=Profi, D=Pentagon with EFF7 extensions)
  - **Always cross-reference both sources** — WoS covers original hardware, Black_Cat covers Soviet clones
- **Soviet clone specifics**: Always check zx-pk.ru for clone-specific behavior, modifications, and extensions.
- **Web research is mandatory**: The local library is a supplement, not a substitute.
- **Emulator source code as ground truth**: When documentation is unclear, check emulator sources — they contain the most detailed per-model timing and behavioral data ever assembled:
  - **Unreal Speccy** (`github.com/mkoloberdin/unrealspeccy`): `unreal.ini` presets define exact frame timing per model (FRAME T-states, PAPER offset, LINE T-states, INT frequency, INT length, EvenM1/4TBorder/FloatBus/PortFF flags)
  - **ZXMAK2** (`github.com/zxmak/zxmak2`): 16+ clone models with separate timing/contention profiles (48K, 128K, +3, Pentagon, Scorpion, ATM 4.50, ATM 7.10, PentEvo, Profi, Sprinter, Quorum, Leningrad, Byte, LEC)
  - **ZEsarUX**: most detailed modern emulator, per-model contention tables, floating bus behavior, Next support
  - **Fuse**: reference open-source emulator, well-documented timing engine
  - **Unreal Speccy Portable (USP)** / **Unreal-NG**: portable and Next-gen forks with additional model support

---

## 3. Detailed Article Breakdown

### 00 — Overview

| File | Topic |
|---|---|
| `history.md` | Sinclair lineage: ZX80 → ZX81 → ZX Spectrum (1982–1992), Amstrad acquisition, Soviet clone explosion (1989–2000s), New Gen era (2010s–present) |
| `hardware_models.md` | Per-model specification table — all three tracks in parallel comparison matrices |
| `timeline.md` | Visual timeline: chips, models, software milestones, demoscene firsts |
| `glossary.md` | Platform-specific terminology (ATTR, ULA, contention, RASTER, TR-DOS, ESXDOS, etc.) |

### 01 — Z80 CPU (~UM0080 Structure) ✅ COMPLETE

| File | Topic | Status |
|---|---|---|
| `z80_architecture.md` | ~UM0080 Ch.1+2: CPU block diagram, register file (AF/BC/DE/HL/AF'/BC'/DE'/HL', IX/IY, SP, PC, I, R), ALU, 40-pin description. Brief note on MEMPTR/WZ → see `z80_undocumented.md` | ✅ |
| `z80_addressing.md` | Memory addressing modes: immediate, register, register indirect, indexed (IX/IY±d), relative, extended, bit, implied. I/O port addressing: IN/OUT port space, register B/C selects, port aliasing on ZX Spectrum bus | ✅ |
| `z80_flags.md` | Flag register F: S, Z, H, P/V, N, C — documented behavior per instruction group. Brief note on flag quirks → see `z80_undocumented.md` | ✅ |
| `z80_instruction_set.md` | ~UM0080 Ch.4: complete instruction reference with timing (T-states, M-cycles). Includes block instructions (LDIR/CPIR/OTIR). Brief note on undocumented opcodes → see `z80_undocumented.md` | ✅ |
| `z80_undocumented.md` | **Authoritative deep reference** for all undocumented behavior: IX/IY half-registers (IXH/IXL/IYH/IYL), `OUT (C),0` per-clone behavior, SLI and ghost opcodes, `LD A,I/R` flag corruption, block instruction flag quirks, DD/FD/FD CB/DD CB prefix oddities, MEMPTR/WZ internal register, R increment behavior, per-clone differences | ✅ |
| `z80_timing.md` | ~UM0080 Ch.3: M-cycles, T-states, bus timing diagrams, I/O port timing, WAIT pin mechanism, per-instruction cost tables, prefix byte timing, DRAM refresh, bus control signals | ✅ |
| `z80_interrupts.md` | ~UM0080 Ch.5: IM0/IM1/IM2, NMI, vector tables, interrupt latency, ZX Spectrum INT chain, per-model INT timing (48K/128K/Pentagon/Next) | ✅ |
| `z80_vs_modern.md` | Cross-platform comparison: Z80 vs 6502 vs 6809 vs modern cores (RP2040, ESP32) | ✅ |

### 02 — Hardware (subfoldered by stream) 📝 PARTIAL

#### 02_hardware/original/ — Sinclair/Amstrad 📝 5 of 12 done

| File | Topic | Status |
|---|---|---|
| `README.md` | Index + model comparison table (16K/48K/128/+2/+2A/+3) | Planned |
| `zx_spectrum_16k_48k.md` | Ferranti ULA (5C/6C), 16K/48K RAM layout, ROM content, keyboard matrix, tape interface, EAR/MIC | ✅ |
| `zx_spectrum_128.md` | 128K toastrack: AY-3-8912, RS-232, keypad port, RAM paging (16K banks), ROM switching | ✅ |
| `zx_spectrum_plus2.md` | Amstrad +2 (grey): integrated keyboard, built-in tape, AY sound | ✅ |
| `zx_spectrum_plus2a_plus3.md` | +2A/+3: Amstrad gate array, +3 DOS, internal floppy, RAM banking differences | ✅ |
| `ula_architecture.md` | Ferranti ULA internals: video generation, memory arbitration, contention timing, CPU/ULA cycle interleaving | ✅ |
| `ula_contention.md` | Memory contention deep dive: when CPU is stalled, precise timing diagrams per model, impact on cycle-counted code | ✅ |
| `ula_timing.md` | ULA frame timing per model (48K/128K/+2A), memory contention (Ferranti 6-5-4-3-2-1-0-0, Amstrad gate array 1-0-7-6-5-4-3-2), contended I/O, multicolor effects, early/late timing drift, performance budget, screen update timing | ✅ |
| `rom_contents.md` | (descoped — duplicative of `04_operating_systems/rom_*.md` and `10_references/rom_routines.md`) | n/a |
| `keyboard_matrix.md` | 8x5 matrix, key codes, keyboard reading routine, BEEP key detection | ✅ |

> **Scope of the descope filter**: only **pure-hardware subcomponents** with no programming interface are excluded — `power_supply.md` (PSU and regulators), `edge_connector.md` (raw pinout; programming-relevant I/O decoding is covered in [io_port_decoding.md](../05_development/03_memory_and_io/io_port_decoding.md)), and the `Power Supply` section formerly in `zx_spectrum_16k_48k.md` (duplicates [pinouts.md](../10_references/pinouts.md) connector specs). `rom_contents.md` is duplicative of existing ROM coverage in [04_operating_systems/](../04_operating_systems/) (`rom_48k.md`, `rom_128k.md`, `rom_plus2.md`, `rom_versions.md`) and [10_references/rom_routines.md](../10_references/rom_routines.md).
>
> **Whole-platform hardware articles remain in scope** (F2 clones and F3 New Gen): these document complete computers with their own memory maps, I/O ports, video/timing quirks, and programming models — all directly relevant to software development. Partial overlap with timing/reference articles is intentional (multiple lenses: hardware article = system architecture + ports; timing article = cycle-exact numbers).

#### 02_hardware/clones/ — Soviet Clone Ecosystem 📝 5 of 12 done

| File | Topic | Status |
|---|---|---|
| `README.md` | Index + clone ecosystem overview: why Spectrum became THE post-Soviet computer | Planned |
| `pentagon.md` | Pentagon 48K/128K: most popular clone, Russian ROM, TR-DOS integration, design philosophy | ✅ |
| `pentagon_1024.md` | Pentagon 1024/1024SL: expanded memory, modifications | Planned |
| `scorpion.md` | Scorpion ZS-256: GMX expansion, Turbo modes, Z-controller, expanded memory, ProfROM | ✅ |
| `kay.md` | Kay 1024: professional-oriented, 1024K RAM, multiple ROM banks, IDE interface | Planned |
| `atm_turbo.md` | ATM Turbo: CP/M mode, turbo mode, extended graphics modes | ✅ |
| `profi.md` | Profi: Russian professional clone, ISA-like expansion, VGA output | Planned |
| `byte.md` | Byte: Ukrainian clone, compact design | Planned |
| `other_clones.md` | Dozens more: Hobbit, Leningrad (1/2), Mikrosha, Composite, Quorum (64/256), LEC (48/528), etc. | Planned |
| `clone_timing.md` | Non-ULA clone video timing: Pentagon, Scorpion, Kay, ATM Turbo, FPGA implementations, clone detection techniques, demoscene multi-platform strategies | ✅ |
| `clone_joysticks.md` | Joystick conventions on Soviet clones (cursor types, Kempston variants) | ✅ |
| `ula_replacements.md` | ULA replacement chips: Soviet-made gate arrays (Т34ВГ1, etc.), CMOS implementations, timing differences | Planned |
| `sizif_harlequin.md` | Modern recreations: Sizif-512, Harlequin, Speccy 2010 — faithful hardware clones with modern components (Karabas family covered in newgen/) | Planned |

#### 02_hardware/newgen/ — New Generation 📝 1 of 15 done (plus 1 off-plan)

| File | Topic | Status |
|---|---|---|
| `README.md` | Index + New Gen ecosystem overview | Planned |
| `zx_next.md` | ZX Spectrum Next complete hardware reference: layer architecture, 28MHz accelerator, Layer 2 framebuffer, sprites, tilemap, copper, DMA, joystick system, Z80N extensions, SD, WiFi, RTC, ESP | Planned |
| `sprinter.md` | Peters Plus Sprinter: 21MHz Z84C15, 4MB RAM, Altera PLD-based video, IDE, ISA, PS/2 | Planned |
| `zx_evo.md` | ZX Evolution: Z80-based with Altera FPGA + ATmega MCU, PS/2 keyboard/mouse, IDE, SVGA — real hardware, not FPGA core recreation | Planned |
| `ts_conf.md` | TS-Conf: FPGA ZX Spectrum config for ZX Evo — sprites, tiles, 512K VRAM, turbo modes | Planned |
| `baseconf.md` | Baseconf: standard ZX Evo configuration, classic Spectrum compatibility | Planned |
| `zx_uno.md` | ZX-Uno: FPGA-based, ULAplus, Turbo, AY, SPI, WiFi | Planned |
| `karabas.md` | Karabas family (Karabas 128 / Karabas Pro / Peridot): open-source Z80 + Altera MAX II CPLD clones, three tiers (Sinclair 128K exact, Pentagon 128 + turbo/SD, expandable with WiFi/RTC/GPIO) | Planned |

### 03 — I/O (subfoldered)

#### 03_io/snapshots/ — Machine-state Capture (Snapshots & Replay)

| File | Topic | Status |
|---|---|---|
| `README.md` | Index — machine-state capture formats (state-at-an-instant + replay) | ✅ |
| `sna_format.md` | .SNA snapshot format: 48K and 128K variants, header structure, limitations | ✅ |
| `z80_format.md` | .Z80 snapshot format: v1/v2/v3, compression, extended hardware info | ✅ |
| `szx_format.md` | .SZX snapshot format: ZEsarUX native | ✅ |
| `rzx_format.md` | .RZX replay format: input recording for deterministic replay, embedding, validation | ✅ |

#### 03_io/storage/ — Tape, Floppy, HDD, and SD Card Media Formats

| File | Topic | Status |
|---|---|---|
| `README.md` | Index — storage media formats (Tape ✅ COMPLETE; Floppy ✅ COMPLETE; HDD/SD ✅ COMPLETE) | ✅ |
| **Tape** ✅ COMPLETE | | |
| `tape_interface.md` | EAR/MIC hardware: pilot tone, sync pulses, data encoding, Turbo LOAD speed-ups | ✅ |
| `tape_format.md` | Tape data format: blocks (header + data), checksums, baud rates (1500–3600 baud) | ✅ |
| `tap_format.md` | .TAP file format: pulse-level encoding, block structure | ✅ |
| `tzx_format.md` | .TZX file format: complete specification, all block types, turbo loading, custom loaders | ✅ |
| `csw_format.md` | .CSW (Compressed Square Wave): tape format for preservation | ✅ |
| `pzx_format.md` | .PZX: alternative tape format | ✅ |
| **Floppy Disk** ✅ COMPLETE | | |
| `disk_format_overview.md` | Top-level comparison: IBM 3740 physical layer, 4 logical formats side-by-side, 8 disk image formats, decision tree | ✅ |
| **Physical layer** | | |
| `mfm_encoding.md` | MFM signal layer: IBM 3740 sectors, MFM bit encoding, address/data marks, CRC16, gap structure | ✅ |
| `fdc_vg93.md` | WD1793 / KR1818VG93 FDC deep dive: 4 registers, Type I/II/III/IV commands, status bits, Soviet clone, turbo mods | ✅ |
| **Hardware interfaces** | | |
| `beta_disk_interface.md` | Beta Disk Interface: WD1793 controller, port map, TR-DOS ROM bank switching, cable, variants | ✅ |
| `plus3_floppy.md` | +3 internal floppy hardware: WD1772-PH, port map, 720 KB geometry, cable pinout, modern replacements | ✅ |
| **Logical disk formats** | | |
| `trd_disk_format.md` | TR-DOS logical format (Soviet, 800 KB DSDD-10): 128 entries × 16 bytes, sector allocation, file types | ✅ |
| `plus3_dos_format.md` | +3DOS logical format (UK, 720 KB DSDD-9, CP/M derivative): 32-byte entries, 1 KB blocks, extents, DPB | ✅ |
| `cpm_disk_format.md` | CP/M 2.2 on Spectrum: BIOS/BDOS/CCP/TPA, FCB, DPB, +3/ATM Turbo/Sprinter variants | ✅ |
| `opus_discovery_format.md` | Opus Discovery / MGT format (UK, 800 KB DSDD-10): WD1770, 256-byte entries, sector bitmap, linked-list chaining | ✅ |
| **Disk-image file formats** | | |
| `trd_scl_formats.md` | .TRD / .SCL image formats (TR-DOS containers) | ✅ |
| `dsk_fdi_formats.md` | .DSK / .EDSK / .FDI image formats (CP/M / +3DOS / Opus containers) | ✅ |
| `udi_format.md` | .UDI universal flux-level image format (preserves every magnetic transition) | ✅ |
| `scp_format.md` | .SCP SuperCard Pro flux-level image format (gold-standard preservation) | ✅ |
| **Hard Disk / SD** ✅ COMPLETE | | |
| **Overview** | | |
| `hdd_overview.md` | Top-level overview: three generations (floppy → IDE → SD), why HDD mattered for the Soviet scene, the unifying FAT abstraction | ✅ |
| **Hardware interfaces** | | |
| `ide_interface.md` | IDE / PATA interfaces: 40-pin connector pinout, port maps for DivIDE/SMUC/Nemo/ZC/ATM/KAY, Z80 read loop sketch | ✅ |
| `divide_divmmc.md` | DivIDE / DivMMC hardware: board architecture, NMI boot, conmem/mapram paging, divman/divese TR-DOS image emulation (hardware companion to esxdos.md) | ✅ |
| `sd_interface.md` | SD card interfaces (SD-SPI): SPI command frames, 5-step init handshake, Z80 bit-bang sketch, port maps for DivMMC/ZXMMC/Next/ZC | ✅ |
| **Filesystem and image formats** | | |
| `hdd_partitioning.md` | Partitioning and filesystems: MBR + 4-entry partition table, FAT12/16/32, BPB, directory entries, LFN, cluster allocation, IS-DOS | ✅ |
| `hdf_mgt_formats.md` | Image formats (.HDF / .IMG / .MGT / .VHD): raw vs headered HDF, loopback mounting, sparse/compression, per-OS card creation | ✅ |

#### 03_io/peripherals/ — Input, Output, and Sound Cards

| File | Topic | Status |
|---|---|---|
| `README.md` | Index — peripheral ecosystem across all tracks | ✅ |
| **Input** | | |
| `keyboard.md` | Keyboard reading: 48K (IN), 128K (AY port), +2A/+3 differences, PS/2 on modern hardware | ✅ |
| `joystick.md` | Kempston (#1F), Sinclair 1/2, Fuller, Cursor, TG Entertainment joystick protocols | ✅ |
| `mouse.md` | Mouse interfaces: Kempston mouse, AMX mouse, protocols | ✅ |
| `lightgun.md` | Light gun / gun stick: Magnum Light Phaser | ✅ |
| **Expansion Interfaces** | | |
| `interface1.md` | ZX Interface 1: ZX Net, RS-232, Microdrives | ✅ |
| `interface2.md` | ZX Interface 2: ROM cartridges, joystick, MT62001 decode | ✅ |
| `multiface.md` | Multiface One/128/3: snapshot tool, poke finder, NMI overlay | ✅ |
| `z_controller.md` | Z-Controller: SD card interface for ZX Spectrum | ✅ |
| `mb02.md` | MB02 interface: 256K RAM, disk, clock, printer | ✅ |
| `zx_bus.md` | ZX Bus standard: expansion bus protocols, addressing, electrical specs | ✅ |
| **Output** | | |
| `printers.md` | ZX Printer (spark), RS-232 printers, SM640/SM646 (Soviet) | ✅ |
| `video_output.md` | RF modulator, composite video mod, RGB output (128K/+2/+3), SCART wiring, VGA adapters | ✅ |
| **Sound Cards** | |
| `sound_overview.md` | **Sound card ecosystem overview**: evolution from 1-bit beeper to multi-chip orchestration, decision guide for which card to target |
| `ay_3_8912.md` | AY-3-8912 / YM2149F PSG: 3 channels, envelopes, noise, I/O port, register map, per-model differences |
| `turbosound.md` | TurboSound: dual AY (6 channels), port decoding, programming model |
| `turbosound_fm.md` | TurboSound FM: YM2203 (OPN) FM synthesis chip, 3 FM + 3 SSG channels, programming, Genesis/Sega comparison |
| `covox_sounDrive.md` | Covox (8-bit DAC), SounDrive (4x8-bit DAC), direct sample playback |
| `gs_general_sound.md` | General Sound (GS): dedicated Z80-based sound card, 4-channel sample playback, port interface, programming model |
| `neogs.md` | NeoGS: GS successor with additional capabilities |
| `moonsound.md` | MoonSound (OPL4 / YMF278B): 24-channel wavetable + 18-channel FM (OPL3 compatible), Yamaha YAC513 DAC |
| `zxm_soundcard.md` | ZXM Soundcard: TurboSound FM + SAA1099 combined (TFM + SAA) |
| `saa1099.md` | SAA1099 PSG: Philips sound chip, stereo, 6 channels, noise generator |
| `zx_next_audio.md` | ZX Spectrum Next audio: 3x AY + beeper + sample playback via DMA, ESP audio |
| `stereo_audio.md` | Stereo audio mods: BytesDelight stereo, ABC/ACB stereo separation on AY |
| `zx_spectrum_48k_audio_routing.md` | 48K audio routing: beeper + tape + MIC mixing, internal speaker circuit |

#### 03_io/networking/ — Connectivity

| File | Topic |
|---|---|
| `README.md` | Index — networking from ZX Net to WiFi |
| `zx_net.md` | ✅ **ZX Net** — Sinclair's 1983 classroom LAN for the Spectrum (with ZX Interface 1): up to 64 stations daisy-chained via ribbon cable, polling-based MAC, packet format (dest/src/len/ctrl/payload/checksum), 9600 bit/s signalling, ROM API (`*NET`, `*LOAD name N`, `*SAVE name N`), microdrive file system, software ecosystem, commercial failure vs Econet, modern emulation in Fuse/ZEsarUX |
| `modems.md` | ✅ **Modems** — telephone-line connectivity for the ZX Spectrum (1982–2000s): acoustic couplers (300 bit/s V.21 FSK), direct-connect modems (Prestel 1200/75, V.23, V.22, V.22 bis, V.32, V.34), Spectrum serial interfaces (Interface 1 RS-232, Kempston SIO, +2A/+3, Beta 128), Prism VTX-5000, Russian modems (Analog 14400, Idustria, T-mail FidoNet mailer), Prestel/Micronet 800 videotex services, BBSes (BBStar, Commstar), Russian FidoNet, early Internet access, modern alternatives (Spectranet/ZiFi/ESP WiFi), FAQ, summary, references |
| `spectranet.md` | ✅ **Spectranet** — modern (2007+) Ethernet + TCP/IP interface for the ZX Spectrum, designed by Andrew Owen: ENC28J60 Ethernet controller via SPI, on-board flash ROM with full TCP/IP stack (TCP/UDP/ICMP/DHCP/DNS/HTTP/FTP/telnet/IRC/NTP), hardware compatibility with all Sinclair/clones, ROM API (BASIC extensions + BSD socket API via `RST #08`), software ecosystem (telnet/FTP/HTTP/IRC clients, Spectrum HTTP server, multiplayer games), comparison with ZiFi, IPv4-only, FAQ, references |
| `zifi.md` | ✅ **ZiFi** — WiFi networking interface for the ZX Spectrum built around the Espressif ESP8266 microcontroller (released 2014). The ESP8266 runs the TCP/IP stack in its own firmware, exposing WiFi and TCP/UDP operations via the Hayes AT command set over a UART. ZiFi hardware: ESP-01/ESP-12 modules, level shifting between 3.3V ESP8266 and 5V Spectrum, dedicated 3.3V regulator (ESP8266 peaks 80 mA). Serial interfaces: Interface 1 RS-232, +2A/+3 serial, Kempston SIO, Beta 128 serial. AT command reference (WiFi: `AT+CWMODE`/`AT+CWJAP`; TCP: `AT+CIPSTART`/`AT+CIPSEND`/`AT+CIPCLOSE`; `+IPD` notifications), typical session, throughput 2–8 KB/s, software ecosystem (telnet, FTP, HTTP, IRC, multiplayer), ZiFi vs Spectranet comparison (WiFi vs Ethernet, AT vs BSD sockets, £5–£10 vs ~£60), SSL/TLS support, FAQ, references |
| `esp_wifi.md` | ✅ **ESP WiFi** — broader family of ESP8266/ESP32-based WiFi solutions for the ZX Spectrum (beyond ZiFi specifically). Espressif history (2008 founding, 2014 ESP8266 release, 2016 ESP32, ESP32-C3 RISC-V, ESP32-C6 WiFi 6). Module variants table (ESP-01, ESP-01S, ESP-03, ESP-07, ESP-12, ESP-12E/F, NodeMCU, Wemos D1 Mini). Boot modes (UART bootloader, normal). Connection topologies: serial (standard ZiFi), SPI (Next's high-throughput), parallel/memory-mapped. Firmware choices: stock AT, ESP-NOW (peer-to-peer), custom firmware (Paradise, WiC64), NodeMCU Lua. Spectrum-specific projects: ZX Spectrum Next built-in ESP-12, Paradise commercial WiFi, hobbyist bridges, cross-platform companion projects (WiC64 for C64, WiFi232 for Atari). FAQ, summary, references |
| `zx_next_wifi.md` | ✅ **ZX Spectrum Next WiFi** — the Next's built-in WiFi using an ESP-12 module connected to the FPGA via SPI (not UART as in ZiFi). History: Next project (2012), 2016 Kickstarter, 2017-2018 first units shipped. Hardware: ESP-12 with 4 MB flash and custom Next-team firmware, SPI bus (4-40 MHz), additional control pins (reset, GPIO0 boot mode, interrupt), power from Next's 3.3V rail. Custom firmware: binary SPI-slave protocol, LwIP TCP/IP stack, up to 8 simultaneous TCP/UDP connections, SSL/TLS support. NextOS WiFi driver layer translating Z80N syscalls to SPI transactions. NextBASIC `*WIFI` commands (`*WIFI ON`, `*WIFI CONNECT`, `*WIFI TCP CONNECT`, `*HTTP GET ... TO ...`). Software ecosystem: telnet clients, file browsers fetching from World of Spectrum, multiplayer games, demoscene use, remote display/control. Comparison with ZiFi and Spectranet (Next is fastest, most integrated, free for Next owners). FAQ, summary, references |

### 04 — Operating Systems ✅ COMPLETE

| File | Topic | Status |
|---|---|---|
| `README.md` | Index — OS landscape across all tracks | ✅ |
| `rom_48k.md` | 48K ROM: ROM map, RST vectors, key routines, channel/stream I/O, BASIC interpreter, editor, character set | ✅ |
| `system_variables.md` | ROM-defined system variables: FRAMES, PROG, VARS, CHANS, FLAGS, keyboard state, memory boundaries | ✅ |
| `rom_128k.md` | 128K ROM 0 + ROM 1: dual-ROM architecture, menu system, 128K BASIC extensions, RAM disk, full-screen editor | ✅ |
| `rom_plus2.md` | +2A/+3 ROM internals: 64 KB four-page layout, paging ports `#7FFD`/`#1FFD`, four paging modes, bugs | ✅ |
| `trdos.md` | TR-DOS: the Soviet flat filesystem, 128 file slots, hook codes API, Pentagon/Beta 128 standard | ✅ |
| `plus3dos.md` | +3 DOS: Amstrad's CP/M-compatible DOS, BDOS layer, RSX BASIC integration | ✅ |
| `is_dos.md` | IS-DOS: Russian hierarchical filesystem, MS-DOS-compatible directory entries, jump-table API | ✅ |
| `nedo_dos.md` | NedoDOS: modern DOS for ZX Evolution, FAT16/32 with VFAT LFN, SD/CF/IDE | ✅ |
| `esxdos.md` | ESXDOS: modern DOS for DivIDE/DivMMC, FAT16/32, dot-command overlays, hook codes | ✅ |
| `nextzxos.md` | NextZXOS: ZX Spectrum Next OS, ESXDOS-derived, Next hardware extensions | ✅ |
| `evo_os.md` | ZX Evolution BIOS/OS: three-layer stack (boot ROM, BaseConf FPGA, OS), TS-Conf | ✅ |
| `cpm.md` | CP/M 2.2 on Spectrum: +3 bootable, ATM Turbo, Sprinter, BIOS/BDOS, CCP, FCBs | ✅ |
| `fuzix.md` | FUZIX: Alan Cox's Unix-like Z80 OS, ~24 KB kernel, ~70 Unix V7 syscalls, FCC compiler | ✅ |
| `basic_dialects.md` | Sinclair BASIC variants: 48K, 128K, +2/+2A/+3, QL SuperBASIC, SE/OpenSE, NextBASIC | ✅ |
| `rom_versions.md` | ROM version catalogue: 48K Issues 1-6 CRC32, 128K, +2A/+3, clone ROMs, modern replacements | ✅ |

### 05 — Development (Learning Progression)

#### 05_development/01_basic/ — Sinclair BASIC

| File | Topic |
|---|---|
| `README.md` | Index — BASIC as entry point |
| `basic_intro.md` | Sinclair BASIC: syntax, quirks, one-line programs, token system |
| `basic_graphics.md` | BASIC graphics commands: PLOT, DRAW, CIRCLE, POINT, ATTR |
| `basic_sound.md` | BASIC sound: BEEP command, frequency/duration, music from BASIC |
| `basic_file_io.md` | BASIC file I/O: SAVE, LOAD, VERIFY, MERGE, tape operations |
| `basic_peek_poke.md` | BASIC machine code access: PEEK, POKE, USR, calling machine code from BASIC |
| `basic_advanced.md` | Advanced BASIC: string manipulation, arrays, data structures, optimization |
| `basic_128k.md` | 128K BASIC extensions: RAM disk, BANK commands, extra editor features |
| `basic_dialects_comparison.md` | Comparing BASIC dialects: 48K vs 128K vs TIMEX vs Russian vs NextBASIC |

#### 05_development/02_assembly/ — Z80 Assembly Programming

| File | Topic |
|---|---|
| `README.md` | Index — assembly as the primary development language |
| `assembly_intro.md` | Getting started with Z80 assembly: registers, addressing modes, first program |
| `rom_calls.md` | ROM routine reference: key 48K ROM entry points, parameters, usage examples |
| `rom_calls_128k.md` | 128K ROM routines: additional calls, paging-aware routines |
| `stack_and_rst.md` | Stack management and RST vectors: RST #08–#38, stack frame conventions |
| `assembly_patterns.md` | Common assembly patterns: loops, conditions, lookup tables, state machines |
| `assembly_optimization.md` | Optimization techniques: T-state counting, register allocation, avoiding contention, self-modifying code |
| `c_with_z88dk.md` | C development with z88dk: newlib vs classic, cross-compilation, library usage |
| `c_with_sdcc.md` | C development with SDCC: Z80 backend, comparison with z88dk, when to use |
| `mixed_c_asm.md` | Mixing C and assembly: calling conventions, inline asm, interop patterns |

#### 05_development/03_memory_and_io/ — Memory Architecture and I/O ✅ COMPLETE

| File | Topic | Status |
|---|---|---|
| `io_port_decoding.md` | I/O port concepts: partial decoding, masks, mirrors, conflicts, cross-model differences + **schematic diagrams** (74-series / Cyrillic Soviet chips) + **Verilog behavioral equivalents** per model | ✅ |
| `memory_and_io_48k.md` | 16K/48K: memory map + #FE port (border, EAR, keyboard, beeper) | ✅ |
| `memory_and_io_128k.md` | 128K/+2: 8 banks, #7FFD paging, shadow screen, AY ports | ✅ |
| `memory_and_io_plus3.md` | +2A/+3: #1FFD, 4 paging modes, true double buffering, gate array contention, +3 FDC | ✅ |
| `memory_and_io_pentagon.md` | Pentagon: #EFF7 extended paging, Beta 128 FDC/TR-DOS, zero contention, **port decoding schematic** | ✅ |
| `memory_and_io_next.md` | ZX Spectrum Next: 2MB MMU (8 KB pages), compatibility modes, Layer 2/sprite/copper/DMA ports | ✅ |
| `bank_switching_patterns.md` | Practical 128K+ paging: cross-bank copy, double buffering, +2A/+3 special modes, antipatterns | ✅ |
| `screen_layout.md` | Nonlinear pixel framebuffer: three-thirds structure, address calculation, lookup tables | ✅ |
| `contention_model.md` | Unified contention: Ferranti vs gate array, per-model timing, I/O contention, cross-platform strategy | ✅ |

#### 05_development/04_interrupts/ — Interrupt Programming

| File | Topic | Status |
|---|---|---|
| `interrupt_programming.md` | Practical guide: IM1/IM2 setup, vector tables, ISR patterns, timing, cookbook, antipatterns | Done |
| `race_the_beam.md` | Race-the-beam programming: synchronizing code to raster position for multicolor, border effects, scanline tricks | Planned |
| `nmi.md` | NMI handling: Multiface NMI, NMI button, what's safe in NMI context | Planned |


#### 05_development/05_display_and_timing/ — Video Subsystem ✅ COMPLETE (19 of 19 articles done)

| File | Topic | Status |
|---|---|---|
| `README.md` | Index — video subsystem overview, why frame timing is the single most important thing to understand on Spectrum | |

**Frame Generation — Per Model** | | |
| `video_frame_overview.md` | Video frame generation overview: PAL timing fundamentals (50Hz, 312/313 scanlines, 224 T-states/line), what the ULA does each frame, screen + border + blanking regions | ✅ |
| `video_frame_48k.md` | **48K ULA frame**: exact T-state map per scanline, pixel fetch pattern, contention windows (scanlines 64–255), INT position (scanline 248, T-state 0), floating bus behavior | ✅ |
| `video_frame_128k.md` | **128K / +2 frame**: same ULA core but contention differs, shadow screen bank, INT timing differences | ✅ |
| `video_frame_plus2a_plus3.md` | **+2A/+3 frame**: Amstrad gate array contention model, different timing from 48K/128K | ✅ |
| `video_frame_pentagon.md` | **Pentagon frame**: THE most important Soviet clone timing — different scanline count, different INT position, different contention — code that works on 48K WILL break here | ✅ |
| `video_frame_scorpion.md` | **Scorpion frame**: 312 lines matching 48K macro timing, +9 T horizontal shift, revision-dependent contention, 7 MHz turbo | ✅ |
| `video_frame_other_soviet.md` | Other Soviet clone frames: Kay 1024 (48K-clean), ATM Turbo (7 MHz anomaly: 99,880 T-states), Profi (paper offset T=12,580), Byte, Quorum, Leningrad, LEC | ✅ |
| `video_frame_next.md` | **ZX Spectrum Next frame**: configurable timing modes (48K/128K/+2A/Pentagon), 4 CPU speeds (3.5/7/14/28 MHz), copper coprocessor | ✅ |
| `video_frame_sprinter.md` | **Sprinter frame**: SVGA 70 Hz timing (not PAL 50 Hz), 20 MHz Z80, 5 video modes, music tempo 40% faster | ✅ |
| `video_frame_zxevo.md` | **ZX Evolution frame**: real Z80 + Altera MAX CPLDs, Pentagon base, BaseConf vs TS-Conf configurations | ✅ |
| `video_frame_comparison.md` | **Frame timing comparison matrix**: all models side-by-side — scanline count, T-states/line, INT position, contention, turbo, compatibility matrix, detection decision tree | ✅ |

**Timing-Dependent Effects** | |
| `raster_timing.md` | Precise raster position: calculating beam position from T-state count, HALT-based sync, per-model raster position tables | ✅ |
| `contention_timing.md` | Contention timing deep dive: per-T-state delay tables (Ferranti 6-5-4-3-2-1-0-0, Amstrad 1-0-7-6-5-4-3-2), per-instruction contended cost tables | ✅ |
| `floating_bus.md` | Floating bus: what value appears when reading contended memory during ULA fetch, per-model behavior, use as raster sync trick, emulator differences | ✅ |
| `border_effects.md` | Border color changes: multicolor borders, raster bars, timing requirements per model | ✅ |
| `interlace_and_flicker.md` | Spectrum's non-interlaced output, 50 Hz perception threshold, attribute flicker, GigaScreen flicker math, CRT vs LCD behaviour | ✅ |

**Color System** | |
| `color_system.md` | Attribute-based color, ULA hardware palette, reference palettes (FUSE/Skoolkid/ZEsarUX), attribute clash, ULAplus 64-color, Timex HiColor/HiRes modes | ✅ |
| `clone_video_modes.md` | Clone video modes beyond standard ULA: GigaScreen, ATM Turbo hires, Profi 512×256, Kay CPLD modes, TS-Conf | ✅ |
| `crt_output.md` | Developer view of CRT/LCD output: pixel aspect ratio, overscan, composite artifacts, per-display-type behaviour | ✅ |

#### 05_development/06_graphics/ — Graphics Techniques

| File | Topic |
|---|---|
| `README.md` | Index — graphics technique progression: monochrome → color → multicolor → dual screen → 3D |
| **Foundation** | |
| `screen_access.md` | Fast screen write: lookup tables, stack-based fills, attribute tricks, column-major addressing |
| `fonts_and_text.md` | Custom fonts, proportional text, 64-column modes, UDG |
| **Monochrome** | |
| `monochrome_techniques.md` | Monochrome / hi-res: 1-bit per pixel, dithering patterns, halftone, stipple shading — no attribute limits |
| **Color (and Color Clash)** | |
| `color_system.md` | Attribute-based color: INK/PAPER, BRIGHT, FLASH — 8x8 cells, color clash as fundamental constraint |
| `color_clash_workarounds.md` | Color clash workarounds: careful attribute planning, character-cell-aligned sprites, Paper=Black tricks, attribute-preserving drawing |
| `attribute_manipulation.md` | Attribute manipulation: fast attribute updates, color cycling, FLASH tricks, per-row attribute effects |
| **Sprites** | |
| `sprites_and_masking.md` | Software sprites: pre-shifted, masked, character-cell vs pixel-precise, XOR/OR/AND compositing |
| `sprite_engines.md` | Sprite engine design: pre-shifted table generation, sprite pools, frame budgets, multiplexor patterns |
| **Scrolling** | |
| `scrolling.md` | Pixel scrolling: character scroll, smooth scroll tricks, 128K double-buffer, attribute scroll |
| **Double Buffering** | |
| `double_buffering.md` | Double buffering: 128K bank 5/7 switching, partial screen update, dirty-rectangle, flicker elimination |
| **Timing-Based Multicolor** | |
| `multicolor_overview.md` | Multicolor overview: why interrupt-synchronized color changes are the Spectrum's most impressive trick |
| `multicolor_techniques.md` | Multicolor / attribute interrupt: timing-critical code, 8x1/8x2 pixel color, race the beam |
| `multicolor_engines.md` | Multicolor engines: published engines and frameworks, T-state budgets, line-accurate color changes |
| `ula_plus.md` | ULAplus: 64-color palette, 8x1 attribute mode, hardware-assisted multicolor on FPGA clones |
| **Dual Screen Techniques** | |
| `dual_screen.md` | Dual screen / split screen: upper/lower screen with different attribute schemes, bank-switched display, 128K screen banks |
| **Blit Techniques** | |
| `blit_techniques.md` | Blit techniques: fast block copy, masked blit, LDIR-based transfer, stack-based blit, aligned vs unaligned |
| `clipping_and_regions.md` | Clipping: screen edge clipping, viewport clipping, partial sprite clipping |
| **3D Graphics** | |
| `3d_line_wireframe.md` | Line drawing and wireframe 3D: Bresenham, fast line draw, 3D projection, rotation matrices |
| `3d_filled_sorting.md` | Filled 3D: face sorting (painter's algorithm), back-face culling, fixed-point math, vertex transformation |
| `raycasting.md` | Raycasting: how Spectrum games did pseudo-3D (Legendary, Tomb of Cairo), column-based rendering |
| `isometric.md` | Isometric engines: Knight Lore legacy, projection math, z-sorting, room-based engines |
| `3d_performance.md` | 3D performance: what's achievable at 3.5 MHz, tables vs calculation, integer-only math, frame budgets |
| **Platform-Specific** | |
| `timex_video_modes.md` | Timex Sinclair 2068: 8x1 color, high-res 512x192, dual screen |
| `next_layer2_graphics.md` | ZX Next Layer 2: 256-color mode, direct pixel access, hardware acceleration |
| `next_tilemap.md` | ZX Next tilemap: hardware scrolling, tile-based rendering |

> **MOVED to [06_sound/](06_sound/README.md)** — Audio content has been promoted to its own root-level section. The planned articles below are tracked there.

#### ~~05_development/07_audio/~~ → 06_sound/ — Audio Programming (MOVED)

| File | Topic |
|---|---|
| `README.md` | Index — audio pipeline from 1-bit to multi-chip |
| `beeper.md` | 1-bit beeper: OUT (#FE), PWM, multi-channel tricks, timing constraints |
| `beeper_music_engines.md` | 1-bit music engines: WHAM, Qchan, Special FX, FuzzClick, engine comparison, techniques |
| `ay_programming.md` | AY-3-8912 / YM2149F programming: register map, tone/noise/envelope, effects |
| `ay_music_formats.md` | AY music formats: PT3 (Vortex Tracker), STC (Sound Tracker), ASC, SQT — structure, player routines |
| `turbosound_programming.md` | TurboSound dual-AY programming: bank switching, 6-channel composition |
| `turbosound_fm_programming.md` | TurboSound FM programming: YM2203 FM synthesis, instrument design, Sega Genesis comparison |
| `covox_programming.md` | Covox / SounDrive programming: 8-bit DAC output, sample rate considerations |
| `gs_programming.md` | General Sound programming: port interface, sample upload, 4-channel mixing, command set |
| `moonsound_programming.md` | MoonSound programming: OPL4 wavetable access, instrument banks, mixing |
| `saa1099_programming.md` | SAA1099 programming: register map, stereo panning, noise |
| `ay_effects.md` | AY sound effects: noise bursts, frequency sweeps, SID-like tricks, DPCM |
| `audio_pipeline_comparison.md` | Cross-track audio comparison: Original (beeper→AY) vs Soviet (AY+Covox+GS+TurboSound) vs New Gen (Next audio+DMA) |

#### 05_development/08_dos_tape/ — DOS and Tape Programming ✅ COMPLETE

| File | Topic |
|---|---|
| `README.md` | Index — 5-article series: tape protocols, TR-DOS, Western DOSes, file formats, mass storage |
| `tape_programming.md` | ROM tape routines (SA-BYTES, LD-BLOCK), custom bit-banging loaders, turbo loaders, custom savers, error handling |
| `trdos_programming.md` | TR-DOS hook codes, file operations, catalog reader, WD1793 sector I/O, demoscene streaming |
| `dos_programming.md` | +3 DOS RSX, ESXDOS hook codes, NextZXOS, dot commands, API comparison matrix, portable code |
| `file_format_handling.md` | Parsing .TAP/.TZX/.TRD/.SCL/.DSK/.SNA/.Z80/.SCR: magic bytes, directory traversal, decompression |
| `mass_storage_programming.md` | Direct IDE/CF ATA access, SD card SPI, read-only FAT16/32 reader, performance comparison |

#### 05_development/09_gamedev/ — Game Development

| File | Topic |
|---|---|
| `README.md` | Index — from techniques to shipped games |
| `game_loop.md` | Game loop architecture: frame timing, state machine, input processing |
| `sprite_engines.md` | Sprite engine design: pre-shifted tables, masked blitting, object pools, frame budgets |
| `collision_detection.md` | Collision detection: bounding box, pixel-precise, attribute-based |
| `level_design.md` | Level data: compression, tile maps, room-based engines, scrolling worlds |
| `asset_pipeline.md` | Asset pipeline: converting graphics/sound for Spectrum, tools, workflow |
| `input_handling.md` | Input handling: multi-device support, keyboard + joystick + Kempston, debouncing |
| `sound_integration.md` | Sound integration: AY music players in games, SFX mixing, memory budgets |
| `ai_patterns.md` | Game AI patterns: pathfinding on 8-bit, state machines, simple behavior trees |
| `game_case_studies.md` | Case studies: analysis of notable game engines (Knight Lore, Elite, Head Over Heels, etc.) |

> **MOVED to [07_demoscene/](07_demoscene/README.md)** — Demoscene content has been promoted to its own root-level section. The planned articles below are tracked there.

#### ~~05_development/10_demoscene/~~ → 07_demoscene/ — Peak Techniques (MOVED)

| File | Topic |
|---|---|
| `README.md` | Index — demoscene as the apex of Spectrum programming |
| `demoscene_history.md` | ZX Spectrum demoscene: history, evolution, unique constraints, cultural impact |
| `effects_catalog.md` | Effect catalog: plasma, raycasting, 3D objects, multicolor, music visualization, type-ins |
| `multicolor_techniques.md` | Multicolor / attribute interrupt: timing-critical code, 8x1/8x2 pixel color, race the beam |
| `precalc_trigonometry.md` | Pre-calculated trigonometry: sine tables, fixed-point math, interpolation, compression of tables |
| `compression_packing.md` | Heavy packing: MegaLZ, HRUM, Z80 crunchers, depackers, memory-constrained decompression |
| `size_coding.md` | 1K/4K/16K intro competitions: size optimization, self-modifying code, code-as-data |
| `demo_frameworks.md` | Demo frameworks: effect sequencing, timing, resource management |
| `notable_demos.md` | Notable demos: analysis of landmark demos — techniques used, how they work |
| `soviet_demo_scene.md` | Russian/Ukrainian demo scene: unique effects, cultural impact, notable groups |
| `demoscene_platforms.md` | Cross-platform: Spectrum vs C64 vs Amiga vs Atari ST — constraint comparison |
| `1bit_music_scene.md` | 1-bit music scene: beeper engine evolution from 1982 to present |

### 06 — Sound ✅ COMPLETE

#### 06_sound/synthesis/ — Synthesis Techniques

| File | Topic | Status |
|---|---|---|
| `ay_ym_synthesis.md` | **Comprehensive AY/YM sound generation**: internal counter model, phase reset, sync-square, PWM, SID-sound, envelope exploitation, sample playback, drum synthesis | ✅ |
| `ay_ym_techniques.md` | **AY/YM Synthesis Techniques** — sync-square, PWM, SID-sound, buzzer bass, note-colored noise, drum synthesis, sample playback | ✅ |
| `ay_vs_ym.md` | **AY vs YM Technical Comparison** — DAC ladder differences, 5-bit envelope on YM, DC offset, SEL pin, per-unit variation, emulator modeling | ✅ |
| `ay_ym_perception.md` | **The AY Sound: Perception, Emotion, and the Hardware Soul** — ABC vs ACB holy war, AY vs YM differences, analog signal chain, psychoacoustics, nostalgia, recapturing the sound | ✅ |
| `multitrack_multichip.md` | Multi-track and multi-chip synthesis outline: TurboSound, cross-chip effects, synchronization | ✅ |
| `beeper_synthesis.md` | 1-bit beeper synthesis: PWM engines, multi-channel tricks, timing constraints | ✅ Done |
| `shiru_ear_shaver_analysis.md` | **Case Study**: Shiru's Ear Shaver 1-bit engine teardown | ✅ Done |

#### 06_sound/hardware/ — Sound Card Hardware

| File | Topic | Status |
|---|---|---|
| `sound_overview.md` | Sound hardware ecosystem overview + decision guide (taxonomy, chronology, decision matrix, consolidated comparison) | ✅ Done |
| `ay_3_8912.md` | AY-3-8912 / YM2149F PSG: pinout, register map, clock domains, DAC, per-model differences | ✅ Done |
| `stereo_audio.md` | Stereo audio modifications: ABC/ACB separation, BytesDelight | ✅ Done |
| `turbosound.md` | TurboSound: dual/triple AY, port decoding, programming model | ✅ Done |
| `turbosound_fm.md` | TurboSound FM: YM2203 (OPN) FM synthesis, 3 FM + 3 SSG channels | ✅ Done |
| `saa1099.md` | SAA1099 PSG: Philips sound chip, 6-channel stereo | ✅ Done |
| `covox_sounDrive.md` | Covox (8-bit DAC), SounDrive (4×8-bit DAC + TLC7226CN single-chip implementation): direct sample playback | ✅ Done |
| `gs_general_sound.md` | General Sound: dedicated Z80-based sound card, 4-channel sample mixing | ✅ Done |
| `moonsound.md` | MoonSound (OPL4/YMF278B): 24-channel wavetable + 18-channel FM, OPN-vs-OPL3 comparison | ✅ Done |
| `zx_next_audio.md` | ZX Spectrum Next audio: 3× AY + beeper + DMA sample playback | ✅ Done |

#### 06_sound/trackers_and_formats/ — Trackers, Editors & Formats

| File | Topic | Status |
|---|---|---|
| `tracker_history.md` | 30-year history: beeper trackers (1985), Sound Tracker (1990), Pro Tracker lineage (Golden Disk Corp.), VTII / Arkos split, modern tools (AT3, VT3) | ✅ Done |
| `ay_music_formats.md` | **Master catalogue**: every AY/YM music file format (`.PT3`, `.PSG`, `.YM`, `.AY`, `.AKG`, etc.) — modules, dumps, containers, modern embedded | ✅ Done |
| `sound_tracker.md` | Sound Tracker 1.1 (Bzyk, 1990) — the first AY grid editor; established the pattern/sample/ornament paradigm inherited by every later tracker | ✅ Done |
| `asc_sound_master.md` | Asc Sound Master (Sendetskiy, 1992) — Soviet alternative with envelope-mode-per-tick instrument model; `.ASC` / `.AS0` formats | ✅ Done |
| `protracker.md` | Pro Tracker 1/2/3 (Golden Disk Corp., 1995–1997) — the format-defining lineage that produced `.PT3`; 4 versions in 3 years | ✅ Done |
| `vortex_tracker.md` | Vortex Tracker II: the de facto PC-based PT3 editor (Bulba, 2000–present), universal import, TurboSound support | ✅ Done |
| `arkos_tracker.md` | Arkos Tracker 2/3: modern cross-platform AY/YM tracker (Targhan, 2003–present), AKG/AKM/AKY players | ✅ Done |
| `pt3_format.md` | PT3 module format specification: header, position table, ornaments, samples, patterns, player operation, sub-versions | ✅ Done |
| `psg_format.md` | PSG register dump format: frame structure, skip opcode, variants (`.YM`, `.VTX`), 20-byte playback routine | ✅ Done |

#### 06_sound/players/ — Player Routines ✅ COMPLETE (2-article pair)

| File | Topic | Status |
|---|---|---|
| `README.md` | Section index | ✅ Done |
| `ay_player_routines.md` | **Architecture**: Z80 → AY register writes, ISR integration (IM1/IM2), per-model frame budgets, PT3 + Arkos player structures, memory placement, integration patterns (507 lines) | ✅ Done |
| `player_comparison.md` | **Comparison**: PT3 vs AKG/AKM/AKY head-to-head benchmarks (size, CPU, features), sound-quality differences, Targhan's decision table, 13-use-case recommendation matrix (262 lines) | ✅ Done |

> Originally planned as a 3-article sub-section; the third article (`audio_decision_guide.md`) was deleted as redundant — its content was already covered by the architecture + comparison pair.

### 07 — Demoscene ✅ COMPLETE

All 11 articles are ✅ Complete (CC BY-SA 4.0). Cross-references verified. See [07_demoscene/README.md](07_demoscene/README.md) for the section catalog.

| File | Topic |
|---|---|
| `demoscene_history.md` | ✅ Western origins, Soviet explosion, modern revival, cultural impact (671 lines) |
| `soviet_demo_scene.md` | ✅ Russian/Ukrainian scene: Pentagon-centric, FidoNet era, PT3 ecosystem, notable groups (722 lines) |
| `demoscene_platforms.md` | ✅ Cross-platform comparison: Spectrum vs C64 vs Amiga vs Atari ST vs MSX vs Amstrad CPC (657 lines) |
| `effects_catalog.md` | ✅ Visual effects catalog: plasma, raycasting, 3D, multicolor, zoomers, tunnels, copper bars (711 lines) |
| `multicolor_techniques.md` | ✅ Multicolor/attribute interrupt: 8×1 and 8×2 color resolution, race-the-beam timing (781 lines) |
| `precalc_trigonometry.md` | ✅ Sine tables, fixed-point math, interpolation, lookup table compression (783 lines) |
| `compression_packing.md` | ✅ 25 crunchers across 4 generations: ZX0/ZX1/ZX2/MegaLZ/Pletter/HRUM, depackers, RCS (1054 lines) |
| `size_coding.md` | ✅ 256 B / 1 K / 4 K / 16 K intro competitions: squeeze, reuse, math, compression, ROM routines (1044 lines) |
| `demo_frameworks.md` | ✅ Demo frameworks: effect sequencing, music sync, memory layout, ISR, part transitions (898 lines) |
| `notable_demos.md` | ✅ Analysis of landmark demos across four eras: Crack Intro, Western Golden, Soviet Peak, Modern Revival (599 lines) |
| `1bit_music_scene.md` | ✅ 1-bit beeper music scene: hardware, techniques, engine lineage, composers, community (538 lines) |

### 08 — Reverse Engineering

| File | Topic |
|---|---|
| `methodology.md` ✅ | ZX Spectrum RE workflow: starting points, snapshot-driven analysis, standard workflow, heuristics, patching, tools, pitfalls, ethics |
| `protection_techniques.md` ✅ | Copy protection catalog: tape loaders (Speedlock, Alkatraz), disk schemes, NMI/snapshot defenses, memory integrity, code obfuscation |
| `analysis_techniques.md` ✅ | Static/dynamic analysis: SkoolKit disassembly, code/data separation, ZEsarUX/DeZog debugging, trace logging, reverse debugging, memory diffing |
| `protection_cracking.md` ✅ | Protection cracking: Speedlock/Alkatraz decryption, timing bypass, disk protection defeat, NMI countermeasure defeat, clean snapshot technique |
| `game_reversing.md` ✅ | Game RE: engine identification, sprite/map/music ripping, cheat codes, save game analysis, Z80-to-C reconstruction |
| `code_crunching.md` ✅ | Compression RE: packer survey (MegaLZ, HRUM, Hrust, ZX0), format ID, LZSS fundamentals, depacker template |
| `snapshot_repair.md` ✅ | Snapshot repair: corrupted .SNA/.Z80, header validation, PC/SP repair, format conversion, mid-load crash fixes |

### 09 — Toolchain

#### 09_toolchain/ — Assemblers and Build Tools

| File | Topic |
|---|---|
| `README.md` | Index — toolchain overview, recommended setup per target platform |
| `native_toolchain.md` | ✅ **Native Spectrum toolchain survey** — pre-assembler era, Zeus, HiSoft DevPac / GENS-MONS, ALASM+STS, XAS, minor native tools, editor workflow evolution (line → full-screen → TR-DOS), debugger/monitor traditions (MONS, STS, Zeus integrated), track differences (Western vs Soviet), when to choose native today |
| `cross_platform_toolchain.md` | ✅ **Modern cross-platform toolchain survey** — why cross-platform won, modern pipeline diagram, SjASMPlus (primary recommendation), Pasmo, z88dk-z80asm, vasm, WLA-DX, zmac, RASM, minor alternatives; z88dk C toolkit, SDCC, Boriel ZX BASIC, Turbo Rascal; VS Code extensions (Z80 Macro-Assembler, Z80 Assembly Meter, DeZog, Klive IDE); emulators for development (Fuse, ZEsarUX, CSpect, JSSpeccy 3, MAME); build systems (Make, Deno, npm, CMake); testing and CI/CD; asset tools and binary packers; recommended-setup decision matrix; worked Hello World example; 6 common pitfalls |
| `assembler_overview.md` | **Comprehensive assembler survey**: all known Z80 assemblers — native and cross-platform — with feature comparison matrix (macros, linking, output formats, ZX-specific features, Z80N support, active maintenance) |

**ZX Spectrum Native Assemblers** (run on the Spectrum itself) | |
| `zeus_assembler.md` | ✅ **Zeus Assembler** — 40-year integrated Z80 dev environment (Nascom 2 → Spectrum 1983 → Zeus 4 Next): editor+assembler+monitor+disassembler in one program, version history, source language (labels/macros/conditionals), built-in monitor (RST #38 breakpoints), built-in disassembler, Zeus 4 modern era (Z80N, .nex, NextReg), comparison vs sjasmplus, FAQ, references |
| `devpac_gens_mons.md` | ✅ **HiSoft DevPac** — GENS, MONS, and the workhorse of the UK commercial Spectrum era (1983–1990): two-program design, version history, GENS source language (directives, two-pass, macros, conditionals), MONS monitor (commands, RST #38 breakpoints), GENS-MONS workflow, comparison vs Zeus, +3 DOS integration, why commercial studios standardised on DevPac, FAQ, legacy in modern sjasmplus conventions |
| `alasm_sts.md` | ✅ **ALASM + STS** — dominant Soviet/post-Soviet native assembler (1992–2005): TR-DOS-native design, fast assembly on slow clone hardware, Cyrillic comment support, STS hardware-assisted debugger (full trace, reverse debugging), ALASM source language (MODULE/ENDMOD namespaces, parameterised macros, multi-file INCLUDE), ALASM+STS workflow, comparison vs XAS, Russian demoscene party circuit (CC, diHALT, CAFe), FAQ, legacy in modern Russian-scene archives |
| `xas_assembler.md` | ✅ **XAS Assembler** — Russian scene's code-generation specialist (1993–2000s, versions 7.x–9.x): macros as central abstraction, multi-window IDE-like editor, three-layer macro system (substitution → variadic/conditional → algorithmic code generation via IRP/IRPC/REPT/string manipulation), scene adoption by Elite Group and Progress demoscene crews, comparison with ALASM, FAQ, legacy in modern sjasmplus macro/Lua capabilities |
| `tasm_native.md` | TASM (native Spectrum version): early native assembler, simple macro support |
| `zxasm_native.md` | ZXASM 3.0: native assembler with STS integration |
| `pikasm.md` | PikAsm: native assembler, used alongside VAST in some professional workflows |
| `laser_genius.md` | Laser Genius (Ocean): cartridge-based assembler, early professional tool |
| `avras.md` | AVRA / other minor native assemblers: lesser-known tools from the tape era |
| `spectrum_basic_mcode.md` | Writing machine code from BASIC: POKE-based workflow, BASIC loaders, monitor programs — the original development method before assemblers existed |

**Modern Cross-Platform Assemblers** (run on PC/Mac/Linux, target Z80) | |
| `sjasmplus.md` | **sjasmplus** (PRIMARY recommended assembler): 3-pass cross-assembler, Z80 + Z80N (Next), Lua scripting, SNA/TAP/NEX output, macros, ZX-Spectrum-specific directives, actively maintained — the de facto standard for modern Spectrum development |
| `pasmo.md` | Pasmo: simple, no-frills Z80 cross-assembler, C++, easy to build everywhere, TAP output, good for beginners and quick projects |
| `z88dk_z80asm.md` | z88dk-z80asm: assembler/linker/librarian within z88dk toolchain, sections, BSS management, PHASE/DEPHASE offset assembly, multi-chip support (Z80/Z180/Z80N), designed as C compiler backend but usable standalone |
| `vasm.md` | vasm (sun.hasenbraten.de): portable retargetable macro assembler, multiple CPU backends including Z80, multiple syntax modules (Mototron/Madmac/oldstyle), linkable objects or absolute output — cross-platform retro standard |
| `wla_dx.md` | WLA-DX: highly multiplatform development system (6502/6800/68000/Z80/GB-Z80/SPC700/HUC6280/SuperFX), linker-based, good for multi-architecture projects |
| `zmac.md` | zmac (George Phillips): Z-80 macro cross-assembler, full C source, builds trivially on Linux/macOS, simple and reliable |
| `zasm_kio.md` | zasm (Kio's): command-line Z80 assembler for Linux/macOS, can include C source files (uses SDCC internally), ZX Spectrum output formats |
| `tniasm.md` | tniASM: Z80/R800/GBZ80 cross-assembler (Windows), used in MSX community |
| `rasm.md` | RASM: fast Z80 assembler for DOS/Windows, by Edouard Berge |
| `sarcasm.md` | Sarcasm: Perl-based Z80 assembler, works on any OS with Perl |
| `tasm_cross.md` | TASM (Table Driven Assembler): classic DOS cross-assembler, table-based multi-CPU support, still used in some workflows |
| `as_macro_assembler.md` | AS Universal Macro Cross-Assembler (Alfred Arnold): multi-CPU, powerful macro system, German docs, professional-grade |

**IDEs and Editor Integration** | |
| `zdevstudio.md` | zDevStudio: open-source cross-platform IDE built on Pasmo, GUI for Z80 development |
| `vscode_integration.md` ✅ | **VS Code Integration** — canonical reference for VS Code as the ZX Spectrum IDE. Extension ecosystem (DeZog, Z80 Macro-Assembler, Z80 Assembly Meter, ASM Code Lens, Microsoft Hex Editor, Klive IDE, SpectNetIDE). DeZog deep dive with four backends (ZEsarUX, CSpect, MAME, internal simulator), SLD / `.lis` / `.cdb` symbol files, reverse debugging via ZEsarUX history. Build tasks + problem matchers for SjASMPlus / z88dk / Boriel ZX BASIC with multi-task pipelines. Full `launch.json` / `tasks.json` / `extensions.json` / `settings.json` worked project setup. Stack comparison (DeZog + SjASMPlus + ZEsarUX vs Klive IDE vs SpectNetIDE) with decision-tree mermaid. Best practices (committing `.vscode/`, pinning tool versions, multi-root workspaces) and pitfalls (port conflicts, stale SLD, source-path mismatches) |
| `zxdstudio.md` | ZXDStudio: ZX Spectrum development IDE for Windows |
| `zx_spin.md` | ZX Spin: Windows-based IDE with built-in assembler and emulator |

**C Compilers** (assembly-adjacent) | |
| `z88dk.md` ✅ | **z88dk** — the complete C development kit for the Z80 family: two C compilers (sccz80 + patched SDCC), classic + newlib libraries, the `+target` system (~100 machines), the `zcc` front-end pipeline, sections and calling conventions, full ZX Spectrum library API (`<arch/zx.h>`, `<graphics.h>`, `<games.h>`, `<sound.h>`, `<arch/zxn.h>`), `appmake` output formats, mixing C with assembly, worked example, pitfalls |
| `sdcc.md` ✅ | **SDCC** — canonical standalone reference. Z80 port history (2003→2025), complete toolchain (`sdcc`, `sdasz80`, `sdldz80`, `sdcdb`, `makebin`, `ucsim`), Z80-specific flag reference, stack-based ABI (right-to-left push, caller-cleans, IX frame pointer), custom CRT0, `.cdb` debug format, integration with SjASMPlus, worked bare-metal 48K example, comparison vs z88dk-sdcc |
| `boriel_zxbasic.md` ✅ | **Boriel ZX BASIC** — the modern BASIC cross-compiler (`zxbc`). Three-stage pipeline (`zxbpp`/`zxbc`/`zxbasm`), 8-type static type system, `SUB`/`FUNCTION` with `ByVal`/`ByRef`/`FastCall`, structured control flow, first-class inline `ASM` with named-symbol interop, ROM-binding standard library (`PRINT`/`PLOT`/`DRAW`/`CIRCLE`/`BEEP`), full memory layout (ORG, stack, string heap), complete CLI flag reference, all output formats (`.bin`/`.tap`/`.tzx`/`.sna`/`.z80`), ZX Spectrum Next support (`--arch zxnext`), worked game-loop example, comparison matrix vs z88dk C and pure assembly, decision-tree mermaid, pitfalls (heap exhaustion, ROM routine quirks, signed/unsigned promotion, ISRs hand-written) |

**Build and Debug Tools** | |
| `debugging.md` ✅ | **Debugging** — three-layer model: native monitor-debuggers (STS, MONS, Zeus Monitor), built-in emulator debuggers (ZEsarUX, Fuse, CSpect, UnrealSpeccy, ZXMAK2, MAME), and source-level / IDE-integrated debuggers (DeZog, z88dk-gdb, mainline GDB Z80 target since July 2021, SpectNetIDE, tagged-source Fuse). Compiler integration deep dive (SLD / `.lis` / `.map` / DWARF / `.cdb`). Comparison matrix across 8 debuggers, decision tree, three recommended end-to-end workflows, pitfalls |
| ~~`testing.md`~~ | Descoped — generic test automation is not Spectrum-specific; the [debugging.md](09_toolchain/debugging.md) § Recommended Workflows article covers the end-to-end debug-and-verify loop, and cross-platform CI is documented in [cross_platform_toolchain.md](09_toolchain/cross_platform_toolchain.md) § Build Systems and CI/CD |
| `asset_tools.md` ✅ | **Asset Pipeline** — three-stage model (authoring → conversion → integration). Screen graphics (`.scr`/`.sch`/`.nic`/`.chk`), software sprite layouts (unmasked/pre-shifted/masked/aligned/attribute-aware), ZX Spectrum Next hardware sprites, fonts (8×8 + FZX full spec), AY music (VTII `.pt3`, Arkos `.akg`/`.akm`), 1-bit beeper engines (Beepola, BeepFX), ayFX SFX, compression (ZX0/ZX1/ZX2/ZX7/MegaLZ/LZSA/APLIB/RCS), tile maps (Tiled), worked Makefile-driven pipeline |
| `disassemblers.md` ✅ | **Disassemblers** — three approaches (linear, smart static, trace-driven). Tools: z80dasm (reversible with z80asm), z88dk-dis (multi-CPU + `.map` aware), z80dismblr / DeZog (code-flow-graph), z80-smart-disassembler (Python), SkoolKit (`.skool` format + cycle-exact Z80 simulator with MEMPTR/WZ + 128K banking), IDA Pro (no Hex-Rays for Z80), Ghidra (community Z80 module, undocumented-opcode caveats), Reko (.NET). Comparison matrices, decision tree, Fuse profiler + SkoolKit `trace.py` workflow |
| ~~`zezarux_debug.md`~~ | Folded into `debugging.md` |
| ~~`fuse_debug.md`~~ | Folded into `debugging.md` |
| ~~`makefiles.md`~~ | Descoped — build system setup is not Spectrum-specific |

### 10 — References

| File | Topic |
|---|---|
| `z80_opcode_table.md` | Complete Z80 opcode matrix with T-states and byte counts |
| `io_port_map.md` | **Complete I/O port map** — every port across all models with decoding bitmasks. Sections: System (ULA #FE, 128K #7FFD, +2A/+3 #1FFD), Memory Paging, AY Audio (#BFFD/#FFFD), Disk Controllers (Beta 128 WD1793 #1F-#FF, +3 FDC, D80, JLO), IDE (ATM, SMUC, DivIDE), Joysticks (Kempston #1F, Sinclair #EFFE/#F7FE), Mouse (Kempston), Printers, Shadow Ports (Pentagon #77), SMUC ISA, Peripherals — with per-model decoding differences annotated |
| `memory_maps.md` | Consolidated memory maps: 48K/128K/+2A/+3/Pentagon/Scorpion/Next/Evo |
| `character_set.md` | ZX Spectrum character set: ASCII mapping, token table, UDG |
| `basic_token_table.md` | Sinclair BASIC token table: keyword → token number |
| `rom_routines.md` | ROM routine addresses: key routines in 48K ROM, entry points |
| `color_palette.md` | Color reference: 8 standard colors + brightness, ULAplus 64-color palette, Next 256-color |
| `error_codes.md` | BASIC error codes (0–R) with descriptions |
| `timing_reference.md` | Consolidated timing: T-states per instruction, contention tables, interrupt timing per model |
| `pinouts.md` | Pinout reference: edge connector, AY port, joystick ports, expansion bus |

### 11 — Emulation (subfoldered)

#### 11_emulation/software/ — Software Emulators

| File | Topic |
|---|---|
| `README.md` | Index — software emulation landscape |
| `emulator_comparison.md` | ✅ **Emulator Comparison** — comprehensive comparison of ZX Spectrum emulators (Fuse, ZEsarUX, CSpect, Spectaculator, UnrealSpeccy, Klive, Speccy/fMSX, JSSpeccy). Categories: cross-platform accuracy-focused, Windows-focused, Next-aware, web-based, mobile, retro-platform, embedded. Detailed strengths/weaknesses for each major emulator. Comparison matrices: platform support, hardware coverage (16K/48K/128K/Pentagon/Scorpion/Next/TSConf), accuracy (cycle-exact, contended memory, audio timing), development tools (disassembler, memory viewer, breakpoints, sprite/tile viewer, RMX), licensing. Selection guide by use case (casual gaming, original hardware development, Next development, reverse engineering, demoscene production, hardware research, mobile, web, embedded). FAQ, references |
| `cycle_exact_accuracy.md` | Cycle-exact requirements: frame timing divergence, CRT sync mechanism, host sync strategies (DRC, resampling), AY audio clocks, judder mitigation (5 techniques), emulator comparison (10 entries), worst-case conclusion | ✅ |
| `fuse.md` | ✅ **Fuse** — deep dive on the Free Unix Spectrum Emulator by Philip Kendall (1999+, GPLv2+, SourceForge). Architecture: modular design (emulator core, `libspectrum` LGPL file format library used by other emulators, UI layer, audio, input). Hardware coverage: complete Sinclair models (16K/48K/128K/+2/+2A/+3/+3e), Russian clones (Pentagon/Scorpion), Brazilian/Spanish clones (Inves, TK90X, TK95), peripherals (Interface 1, microdrives, ZX Net, +D, Opus, Multiface, Beta 128, DivIDE/DivMMC, Currah µSpeech, SpecDrum). Debugger: register view, disassembly, memory view, breakpoints (execution/memory/IO), watchpoints, stepping. RMX recording for verified speedruns. Save states (.szx/.z80/.sna/.pzx). Tape/disk loading (TAP/TZX/PZX/WAV/CSW; DSK/IMG/TRD/SCL). Derivative projects: JSSpeccy (WebAssembly browser port), Fuse Android, SpeccySDL (embedded). Performance, FAQ (installation, Next support, accuracy, libspectrum licensing), references |
| `zesarux.md` | ✅ **ZEsarUX** — deep dive on ZX Spectrum Emulator Revised And Universal eXtension by Cesar Hernandez Nuñez (chernandezba), started 2013, GPLv3, GitHub-hosted. Architecture: single-source codebase with platform-specific UIs (GTK+/SDL Linux, Cocoa macOS, Win32 Windows), configuration filesystem. **Broadest hardware coverage** of any emulator: Sinclair (16K/48K/128K/+2/+2A/+3), Spanish/South American clones (Inves, TK90X, TK95), Russian clones (Pentagon 128/512/1024, Scorpion 256/1024, ATM Turbo, Profi), modern hardware (TSConf, BaseConf, Chrome, ZX-Uno, ZX Spectrum Next partial). Peripherals: Interface 1, microdrives, ZX Net, Beta 128, +D, Opus, DivIDE/DivMMC, Multiface, AY-3-8912, Currah µSpeech. **Reverse engineering workstation**: register view, disassembly, memory view, stack view, execution/memory/IO breakpoints, conditional breakpoints, watchpoints, **reverse debugging** (step backwards via state snapshots), **real-time assembly editing** (patch code in-place), hardware visualisations (memory map, video timing, AY registers, copper/logic analyser, layer 2/tilemap view), scripting, memory search. ZX Spectrum Next support: Z80N CPU, layer 2, hardware sprites, tilemap, copper, ESP-12 WiFi partial. Use cases: reverse engineering, demoscene production, hardware research, Next development. FAQ, summary, references |
| `cspect.md` | ✅ **CSpect** — deep dive on CSpect by Mike Dailly (co-founder DMA Design / Rockstar North, started 2017 for the ZX Spectrum Next crowdfunding campaign). **De facto reference emulator for the ZX Spectrum Next**. History: Mike Dailly's industry background (Lemmings, GTA, Body Harvest at DMA Design), origin tied to the 2017 Next crowdfunding need for an emulator before real hardware shipped, frequent updates tracking Next spec. Architecture: closed-source, Windows binaries (Wine for Linux/macOS), free for personal use. Hardware coverage: Z80N CPU with extended instruction set (LDPIR, SWAPNIB, MIRROR, PIXELDAT, NEXTREG access via LD A,NX / LD NX,A, BRLC, extended LD, POP HD / PUSH HD); layer 2 framebuffer (256×192×8bpp, 256-colour palette from 24-bit RGB, priority vs ULA, shadow for double-buffering, clipping, blending); hardware sprites (up to 64 per frame, 256 patterns, 16×16 or 8×8, 4-bit transparency, anchor sprites, mirror/rotate, clipping, over-border); tilemap (40×32 at 8×8 tiles or 80×32 at 4×8, hardware scrolling, 256-colour palette, priority); copper (WAIT/MOVE/STOP per-scanline NEXTREG writes, one instruction per scanline, cycle-level divergences from real hardware); DMA controller (Z80DMA-like); DivMMC storage; 4 MB paged RAM; 128 KB ROM; extended PS/2 keyboard; hardware scrolling; lores (128×96) and hires (512×192 interpixel) modes; 256-entry 8-bit-per-channel RGB palette; ESP-12 WiFi partial (SPI interface + subset of AT commands, no real Internet). Debugger: multi-pane (registers, disassembly, memory, stack, **NEXTREG pane** with live register state + tooltips, Layer 2 live view, Sprites with pattern previews, Tilemap, Palette swatches); execution/memory/IO/NEXTREG-write/conditional breakpoints; real-time resource inspection. Next dev workflow: NEX file loader for the Next's standard executable format (header + load address + entry point + memory pages + register init + NEXTREG init), TCP remote debugging protocol for IDE integration (VS Code), CSpect-vs-real hardware divergence notes. Demoscene use. CSpect vs ZEsarUX comparison for Next work (platform, update cadence, tooling, licensing). FAQ, summary, references, cross-references |
| `test_suites.md` | ✅ **Test Suites** — test programs used to validate ZX Spectrum emulator accuracy. ZEXALL/ZEXDOC (Z80 instruction exerciser by Frank D. Cringle, 1997), the FUSE test suite (Z80 instructions, contended memory, INT timing, video timing, audio, peripherals — hosted on SourceForge), Pentagon Diag ROM (Russian clone validation). Timing-specific tests: Sensible tests (Andrew Owen), Float Spell multicolour demo, contended memory loop, INT timing tests. Peripheral tests: AY-3-8912 register/envelope/noise, Kempston joystick at `0x1F`, Interface 1/microdrive. Diagnostic ROMs (ZX Diag, Ramtest). How to use for emulator users (download, run, compare) and authors (CI pipeline, multi-hardware configs, real hardware comparison, publish results). Limitations of testing (unknown edge cases, hardware variability, test bugs, analogue behaviour). FAQ, summary, references |

#### 11_emulation/fpga/ — FPGA Cores

| File | Topic |
|---|---|
| `README.md` | Index — FPGA Spectrum ecosystem |
| `mist_mister_core.md` | ✅ **MiST / MiSTer ZX Spectrum Cores** — deep dive on FPGA-based Spectrum emulation on the DE10-Nano platform. History: **MiST** (2011, Till Harbaum, Altera Cyclone I, 20K LEs, dozens of cores including early Spectrum) → **MiSTer** (2017, Alexey Melnikov, Terasic DE10-Nano with Intel/Altera Cyclone V SoC 5CSEMA5, 85K LEs, ARM Cortex-A9 HPS running Linux, $130 bare board / $200+ with add-ons, open hardware ecosystem — USB hub, SDRAM, I/O board, analogue video — hundreds of thousands of units in active use worldwide). Why FPGA beats software for authenticity: cycle-exact CPU timing, real video signal generation, exact peripheral behaviour, analogue CRT-compatible output. Hardware coverage: full Sinclair range (16K/48K/128K Spanish/+2 grey/+2A/+3), Russian clones (Pentagon 128/512/1024, Scorpion 256/1024, ATM Turbo), Spanish/Brazilian clones (TK90X/TK95, Inves). Peripherals: AY-3-8912, Beta 128 (TR-DOS .trd/.scl), +3 FDC (.dsk), DivMMC/DivIDE (.img), Interface 1, Currah µSpeech, Multiface 128/3, Kempston/Sinclair joysticks. Architecture: **T80** cycle-exact Z80 in Verilog (Daniel Wallner, with undocumented instructions SLL/LD A,R/LD A,I/RLD/RRD at exact cycle counts), ULA module with memory contention (WAIT during video fetch) and floating bus effect, AY-3-8912 at original 1.7734 MHz clock, modular peripheral Verilog modules (beta128.v, divmmc.v, plus3_fdc.v, if1.v, currah_uspeech.v, kempston.v). Video output: HDMI (DE10-Nano on-board, 720p/1080p scaled), Analogue VGA (15kHz RGB or 31kHz via I/O Board), Composite/S-Video (CRT TV); pixel-perfect timing (4 CPU cycles per pixel in lower 256×192 area); 50Hz/60Hz switchable. Audio output: HDMI embedded + analogue 3.5mm jack; beeper + AY-3-8912 mix at original clocks. OSD menu (F12) for load/machine/peripheral/video/audio/state/reset/joy configuration with persistent `.cfg` files. MiSTer vs real hardware vs software emulators decision matrix (timing accuracy, reliability, cost, CRT, software loading, peripherals, keyboard, portability). When to choose MiSTer / real hardware / software emulator. FAQ (accuracy, old tape collection, Next support, Analogue I/O Board necessity, SDRAM necessity, real Spectrum keyboard via adapters, maintenance, TR-DOS). Summary, references (misterfpga.org, MiSTer Spectrum core GitHub, DE10-Nano docs, MiST legacy, Atari-Forum MiSTer subforum), cross-references |
| `zx_uno_core.md` | ✅ **ZX-Uno** — deep dive on the open-source single-board FPGA Spectrum by **Antonio Villena** (Spanish scene, 2016). Hardware: Cyclone IV EP4CE6 FPGA (6K LEs, sufficient for full Spectrum core + peripherals), EPCQ16 config flash, 512 KB SRAM, microSD, PS/2 keyboard, VGA (8-bit RGB = 256 colours), 3.5mm audio, mini-USB power, JTAG header, expansion header, ~100mm × 60mm PCB. History: Spanish scene's need for modern Spectrum (original ULAs dying, keyboards worn out, power supplies unreliable), 2015–2016 design by Villena, first batches 2016, full open-source release 2017 (hardware schematics + Verilog core under GPL), ZX-Uno 2.0 PCB revisions, community variants, influence on Sizif-512 and Russian FPGA clones. Supported machine types: 48K, 128K Spanish, +2 grey, +2A/+3, Pentagon 128, Scorpion, TK90X/TK95. Architecture: T80 Verilog Z80 (cycle-exact with undocumented instructions), ULA module, modular peripheral modules. **ULAplus** extended palette (designed by Andrew Owen — same engineer as Spectranet): 64 entries of 8-bit RGB (3R/3G/2B) via I/O ports 0xBF (palette index) and 0xFF (palette value); standard 16 Spectrum colours mapped to first 16 entries; extended mode with 256 colours via two attribute bytes per cell. **Turbo modes**: 3.5 MHz standard, 7 MHz (×2), 14 MHz (×4) with video timing unaffected. Peripherals: beeper, AY-3-8912, TurboSound (dual AY), SpecDrum, Covox/Soundrive; DivMMC (SD card as mass storage), DivIDE, Beta 128, +3 FDC, Interface 1; Kempston/Sinclair joysticks, PS/2 keyboard/mouse; Multiface 128/3, Currah µSpeech, SpecMate. `zxuno.cfg` configuration via SD card. ZX-Uno vs MiSTer (Spectrum-only vs multi-platform, €60–80 vs €200+) vs Harlequin (superset vs original-form-factor) vs real Spectrum decision matrix. ULAplus adoption in modern software (post-2010 demos, graphics conversions, homebrew games, ZX Paintbrush/BMP2Spectre tools). FAQ (where to buy — Retroleum UK + Spanish eBay/Spectrum-stores + self-build via JLCPCB; assembly; core updates via JTAG or SD bootloader; Next support — no, FPGA too small; software development via sjasmplus/z88dk/Boriel ZX BASIC; ULAplus compatibility — yes, superset; real Spectrum keyboard via adapters; maintenance on GitHub + Spanish forums). Summary, references (ZX-Uno GitHub, Villena's website, ZX-Uno wiki, zorlac.es / speccy.org Spanish forums, World of Spectrum forums, ULAplus specification by Andrew Owen), cross-references |
| `zxevo.md` | ✅ **ZX Evolution** — deep dive on the modern Russian hybrid Z80 + CPLD + MCU Spectrum clone designed by **Vladimir "vslav" Kladov** (2007–2010), spiritual successor to the Pentagon. History: Pentagon legacy (designed by Dmitry "DimaM" Mikhalkov 1990–1991, dominant Russian clone built from discrete logic since Russia lacked Ferranti ULA access, TR-DOS disk operating system with Beta 128 interface), mid-2000s need for modern Pentagon (discrete chips failing, edge connectors oxidising, Russian DRAM unreliable). Hybrid architecture: **real Z80 CPU** (Zilog Z84C00 NMOS or CMOS, Z84C0020 20 MHz rated, or Russian KR1858VM1) at 3.5/7/14 MHz — advantages: exact instruction timing including undocumented SLL and LD A,I/LD A,R flags, real electrical bus characteristics; **Altera MAX II EPM570 CPLD** (570 macrocells, non-volatile config) for address decoding, Pentagon paged memory banking, I/O port decoding, video address generation, CPU/video memory arbitration (WAIT signal); **Atmel ATmega MCU** (ATmega8515 or ATmega162) for PS/2 keyboard scan code translation, PS/2 mouse Kempston protocol, SD card SPI, real-time clock, in-system CPLD reflashing. Memory: 4 MB paged RAM (16 KB pages), standard Pentagon 128K compatibility, RAM disk, multiple ROMs. Video: standard 256×192 at 50/60/100 Hz, Pentagon 384×304 mode, multicolour modes, 16/256-colour extended, SVGA output (no RF/composite). Storage: IDE (hard disks, CompactFlash via adapter, SD-to-IDE), Beta 128 with VG93/FD1793 FDC, DivMMC emulation, SD card via ATmega SPI. **BaseConf firmware**: exact Pentagon 128 compatibility (memory banking, video timing, I/O port layout, Beta 128 at original ports, AY-3-8912 at Pentagon clock); extensions (turbo mode 7/14 MHz, extended RAM, PS/2 keyboard/mouse, IDE, SVGA, RTC, Gluk socket, SD via SPI); boot menu with multiple ROMs (TR-DOS, 128K BASIC, 48K BASIC, service, custom). TR-DOS software ecosystem (hundreds of Russian games, demoscene productions by Progress/Extreme/SkillCom/Boomerang, system software, ALASM/XAS assemblers + STS debugger). Demoscene adoption: CC Chaos Constructions (St. Petersburg), diHalt (Nizhny Novgorod), CAFe (Kazan), FunTop (Moscow historical), AXAC, ZX-Dev. ZX Evolution vs ZX-Uno (Russian hybrid vs Spanish pure FPGA, ~€150–250 vs €60–80) vs MiSTer vs real Pentagon decision matrix. BaseConf vs TS-Conf firmware (TS-Conf adds features but breaks strict Pentagon compat). FAQ (where to buy via NedoPC/Russian eBay/self-build; open source on GitHub; Sinclair software compatibility via 128K emulation; Next support — no, Pentagon-class; real Spectrum keyboard via adapters; TFT monitor via SVGA; active maintenance). Summary, references (ZX Evolution SVN/GitHub, NedoPC nedopc.org, Kladov's project pages, BaseConf source, ZX-Forum.ru Russian forums, CC/diHalt/CAFe party archives, Pentagon software archives), cross-references |
| `harlequin_sizif.md` | ✅ **Harlequin and Sizif-512** — deep dive on modern FPGA Spectrums in **original form factor** (drop-in replacements for original 48K/+2/+3 PCBs). **Harlequin** (Chris Smith, 2012–2013): Cyclone II EP2C5 FPGA, real socketed Z80 (modern CMOS Z84C00), 32/64 KB modern SRAM replacing notoriously unreliable 4116/4532 DRAMs, EPROM or flash ROM with 16K Spectrum BASIC, modern switching power supply (+5V/-5V/+12V), original-form-factor connectors (edge connector, TV RF output/modulator, EAR/MIC jacks, expansion port), PCB designed to fit original Sinclair rubber-key case. Faithful ULA recreation based on Smith's reverse-engineering book *The ZX Spectrum ULA: How to Design a Microcomputer* (2010) — definitive ULA documentation covering video address generator, shift register, colour encoder, memory arbitration, timing generator, `0xFE` I/O port. Harlequin variants 1/2/3 plus 48K and 128K versions for +2/+3 cases. **Sizif-512** (Victor Trucco et al., Brazilian scene, 2018+): Cyclone IV EP4CE6 (same as ZX-Uno), 512 KB paged static RAM, flash ROM with multiple boot ROMs (48K/128K/+2/+3/service), modern switching regulators, original-form-factor connectors + optional PS/2 keyboard port + optional SD card interface. Supports 48K/128K/Pentagon 128 modes, turbo mode (7/14 MHz), ULAplus 256-colour palette, DivMMC SD card loading, PS/2 keyboard bypass. ULA recreation details: memory contention (WAIT signal during pixel/attribute fetches in upper 16 KB of 48K address space `0x4000–0x7FFF`), floating bus effect (reading port `0xFF` during specific cycles returns ULA-fetched byte), composite PAL video signal generation (horizontal/vertical sync, blanking intervals, PAL colour burst, pixel data shifted at pixel clock), beeper audio timing (updates at specific frame points not continuously). Both pass standard timing tests: FUSE test suite (instructions, contended memory, INT timing, video timing), Sensible tests by Andrew Owen (floating bus, contention patterns), Float Spell multicolour demo (exact video timing), Pentagon Diag ROM. Harlequin vs Sizif-512 comparison (Cyclone II vs Cyclone IV; 48K-only vs 48K/128K/Pentagon; no turbo vs 7/14 MHz; no ULAplus vs yes; no PS/2/SD vs optional). Harlequin/Sizif vs MiSTer/ZX-Uno/ZX Evolution/real Spectrum decision matrix (form factor, real Z80 CPU, ULA authenticity, tape loading, CRT/TV output, best-for use case). Why choose: reviving original hardware, maximum authenticity, RF/composite for CRT TV, Chris Smith's ULA work. FAQ (where to buy — Retroleum UK, Brazilian retailers, project GitHub, self-build; original power supply acceptance; need for real Spectrum case — no but intended; original peripheral compatibility via edge connector; better than real Spectrum — for daily use unambiguously yes; open source — yes, both HW and core; firmware updates via JTAG/USB-Blaster, some Sizif via SD). Summary, references (Smith's book, Harlequin project pages, Sizif-512 GitHub, Retroleum catalogue, World of Spectrum forums, ZX-Uno community/zorlac.es Spanish scene, demoscene timing tests), cross-references |
| `fpga_implementation.md` | ✅ **Spectrum FPGA Implementation** — how cores are designed from specification through HDL, simulation, synthesis, and hardware verification. **Specification phase**: machine models (Sinclair 48K/128K/+2/+2A/+3, Pentagon, Scorpion, ATM Turbo, TK90X/TK95), peripherals (AY-3-8912, Beta 128, +3 FDC, DivMMC/DivIDE, Interface 1, Currah µSpeech, Multiface, joysticks, PS/2), video output modes (composite/RGB/VGA/HDMI, 50/60 Hz), performance targets (CPU speed 3.5/7/14 MHz, memory 48K–4 MB, FPGA resource budget), compatibility targets (cycle-exact timing per FUSE test suite). **Module decomposition** as Verilog hierarchy: `spectrum_top.v` instantiating z80_top, ula (with video_addr_gen, shift_reg, colour_encoder, arbitrer submodules), ram, rom, ay_3_8912, keyboard, joystick, beta128, divmmc, ps2_keyboard, audio_mixer. **T80 Z80 core** by Daniel Wallner: cycle-accurate (matches original Z80 instruction timing cycle-by-cycle including undocumented SLL and LD A,I/LD A,R flags), bus-compatible (A[15:0], D[7:0], M1, MREQ, IORQ, RD, WR, RFSH, BUSACK, WAIT, INT, NMI, RESET), synthesizable (Intel/Altera, Xilinx, Lattice), compact (~2K–2.5K LEs), variants T80n/T80s; used in MiSTer/ZX-Uno/Harlequin cores; Verilog instantiation example with WAIT_n for memory contention. **ULA implementation**: video address generator with the unusual address bit layout (high byte `010 Y7 Y6 Y2 Y1 Y0`, low byte `Y5 Y4 Y3 X4..X0`) matching Spectrum's interleaved video memory; pixel shift register (8-bit, one pixel per video clock); colour encoder (INK/PAPER/BRIGHT/FLASH multiplexer with 1 Hz blink for FLASH cells, BORDER register for non-display areas); memory arbitration (WAIT_n asserted by ULA during video fetches in `0x4000–0x7FFF`, asymmetric pattern per scanline position, documented in Smith's book); floating bus effect (port `0xFF` reads during specific cycles return ULA-fetched byte). **Peripheral modules**: AY-3-8912 (16 registers, 3 tone generators, 5-bit LFSR noise, 16-mode envelope, 3× 4-bit DAC, I/O ports), Beta 128 (VG93/FD1793 FDC, TR-DOS ROM banking, .trd/.scl disk image loading, often 500+ lines of HDL), DivMMC (SPI to SD card, FAT16/32 filesystem, memory banking), keyboard (8×8 matrix scan + PS/2 scan code translation). **Simulation** via Icarus Verilog/Verilator/ModelSim/QuestaSim/GTKWave; Verilog test bench example driving clk/reset/video/audio and loading ROM for behaviour verification. **Test programs** (ZEXALL/ZEXDOC for Z80, FUSE test suite, Sensible tests, Pentagon Diag ROM). **Synthesis toolchain**: Quartus Prime/II for Cyclone FPGAs, Vivado/ISE for Xilinx, Diamond for Lattice, IceStorm open-source for iCE40; 5 steps (synthesis → mapping → place and route → timing analysis → bitstream generation); constraints files (.qsf, .xdc); resource usage table for ZX-uno-class Cyclone IV EP4CE6 (4–5K LEs out of 6,272; 50–100K memory bits out of 276K; 1–2 PLLs out of 2; 30–40 I/O pins). **Timing closure** trivial at 3.5 MHz but real concern at 14 MHz turbo or Next layer 2. **Hardware verification**: real-time test programs, oscilloscope/logic analyser comparison with real Spectrum (HSYNC/VSYNC/WAIT timing), software compatibility testing (commercial games, demoscene productions, system software, peripheral-using software). **Iterative development cycle** mermaid (specify → write HDL → simulate → tests pass? → synthesise → load to FPGA → hardware test → real hw matches? → release). **Open-source cores** for study: MiSTer, ZX-Uno, Harlequin, Sizif-512, T80 on OpenCores/GitHub. FAQ (development time — 2–4 weeks basic, several months full, multi-year MiSTer-quality; deep hardware knowledge needed via Smith's book + Zilog datasheet; VHDL vs Verilog both synthesizable; learning FPGA via iCEstick/Cyclone IV dev boards; contributing via issue tracker pull requests; Next implementation in FPGA — yes but substantially more complex). Summary, references (Smith's book, T80 on OpenCores, Zilog Z80 datasheet, Sinclair service manual, MiSTer/ZX-Uno/Harlequin/Sizif-512 GitHub repos, Quartus/Vivado/Icarus/GTKWave), cross-references |
| `fpga_timing_accuracy.md` | ✅ **Cycle-Exact Timing in Spectrum FPGA Cores** — the defining quality metric for FPGA Spectrum recreations. **Why timing matters**: Spectrum's timing sensitivity (contended memory `0x4000–0x7FFF` causing CPU WAIT during video fetches, floating bus reads of port `0xFF`, INT timing); demoscene effects requiring T-state precision (multicolour 2-pixel-wide attribute changes producing 64 colours per character cell per frame, bobs software sprites, sync-scroller horizontal scrolling, copper bars); copy protection measuring timing patterns (Speedlock, Alkatraz, Latenite). **Timing models**: scanline-precise (gross video timing correct but contention uniform, floating bus approximate, works for 95%+ software, fails on multicolour and copy protection) vs T-state-precise (exact contention pattern per scanline position, exact floating bus cycle-by-cycle, exact INT timing, exact Z80 instruction cycle counts including `LD A,I`/`LD A,R`/`RLD`/`RRD`/`LDI`/`CPI`/`INI`). Modern high-quality cores (MiSTer, ZX-Uno, Harlequin, Sizif-512) are all T-state-precise. **ULA timing internals**: frame timing (CPU clock 3.504690 MHz, 224 T-states/scanline = 64 µs, 311 scanlines/frame = 19.9 ms = 50.08 Hz, 192 active scanlines of 256 pixels, 64+56 border scanlines, 128K has different layout, Pentagon has own); contended memory pattern (ULA fetches pixel+attribute byte pair every 4 T-states during active display, asymmetric arbitration T1/T2 contention + T3/T4 free, pattern depends on address range and 4-cycle character position, documented in Smith's book); contention state machine implementation in Verilog (video position counter, contention window detector, WAIT pattern generator, address range check `A[15]=0 && A[14]=1`); floating bus (returns ULA-fetched byte at specific cycles, `0xFF` otherwise); INT timing (asserted at scanline 64, CPU responds in 4–13 T-states); 128K banking-aware contention (only contended pages like page 5). **Common pitfalls**: PLL jitter (causes INT drift, pixel clock jitter, arbitration races; mitigation: low-jitter PLL or crystal); asynchronous clock domains (metastability; mitigation: two-flop synchronisers or single master clock); bus arbitration races (latch errors, missed WAITs, deadlocks; mitigation: careful WAIT_n setup/hold per T80 spec); banking/memory map errors; undocumented Z80 behaviour (`SLL (HL)`, `LD A,I`/`LD A,R` flags = IFF2, partial decode flags after LDI/CPI/INI, `OUT (C),0` writes 0 on NMOS vs 0xFF on CMOS). **Verification methods**: test programs (FUSE test suite covering instructions/contention/INT/video, Sensible tests by Andrew Owen for floating bus, ZEXALL/ZEXDOC exhaustive Z80, Pentagon Diag ROM, Float Spell multicolour demo as integration test); oscilloscope/logic analyser comparison with real Spectrum (HSYNC/VSYNC/WAIT_n/INT/CPU bus signals); software compatibility testing (commercial games, demoscene productions like BIFTRO/Refresh/_NUMBERS_/Eye of the Lizard, system software, peripheral-using software); frame-accurate visual diffing via frame grabber pixel-by-pixel. **Timing accuracy comparison table** across real Spectrum / MiSTer / ZX-Uno / Harlequin / Sizif-512 / ZX Evolution (Pentagon) / ZX Spectrum Next (approximate) / Fuse / ZEsarUX / CSpect / UnrealSpeccy / older emulators — columns: approach, cycle-exact?, FUSE tests, multicolour demos, copy protection. Key observations: all modern high-quality FPGA cores cycle-exact; high-quality software emulators (Fuse/ZEsarUX/UnrealSpeccy) also cycle-exact via T-state simulation; ZX Spectrum Next intentionally less timing-sensitive due to hardware features; CSpect scanline-precise appropriate for Next but not classic 48K demos. FAQ (FUSE pass but demos glitch due to edge cases not covered by tests; need for real Spectrum — not strictly, Fuse as reference; copy-protected crashes due to contention pattern subtle errors; Pentagon timing different from Sinclair; T80n variant with improvements; 128K banking-aware contention; FPGA device family impact minimal at 3.5 MHz; sim-vs-hardware gap via PLL jitter/clock domains/timing violations, diagnose via STA + SignalTap/ChipScope). Summary (4 requirements: T80 cycle-accurate Z80, ULA recreation per Smith's book, careful clock/jitter/arbitration handling, comprehensive verification; modern cores achieve T-state precision indistinguishable from real hardware). References (Smith's book, T80 on OpenCores, Zilog Z84C00 datasheet, MiSTer/ZX-Uno/Harlequin/Sizif GitHub, FUSE/Sensible test suites, World of Spectrum forums, demoscene timing tests), cross-references |

#### 11_emulation/mcu/ — MCU Chip Emulation

| File | Topic |
|---|---|
| `README.md` | Index — MCU-based chip emulation: replacing vintage silicon with modern microcontrollers |
| `mcu_z80.md` | ✅ **Z80 on a Microcontroller** — replacing the Z80 CPU with a modern MCU. **Why MCU**: component availability (original Zilog Z80 out of production, Russian KR1858VM1 quality variable, CMOS Z84C00 rising £5–£15), power consumption (NMOS Z80 ~150 mA at 5V vs RP2040 ~10 mA at 3.3V), reliability (decades of life vs degraded 40-year-old chips), additional features (in-circuit debugging, tracing, bus monitoring, integrated peripherals, software-upgradable). **Compatibility layer**: MCU presents full Z80 bus interface (A[15:0], D[7:0], M1_n, MREQ_n, IORQ_n, RD_n, WR_n, RFSH_n, BUSRQ_n, BUSACK_n, WAIT_n, INT_n, NMI_n, RESET_n). **Host MCU choices**: RP2040 (Raspberry Pi Pico, dual Cortex-M0+ at 133 MHz overclockable to 250 MHz, **PIO blocks** — two blocks of 4 state machines each for cycle-precise hardware I/O independent of CPU, 30 GPIOs, ~£1 — optimal for most hobbyists), ESP32 (Xtensa/RISC-V at 240 MHz with Wi-Fi/Bluetooth, fewer GPIOs, no PIO equivalent but raw speed compensates), STM32 family (F407 Cortex-M4 at 168 MHz with hardware FMC for deterministic external bus timing, up to 82 GPIOs on LQFP100, ~£5), Arduino AVR (too slow at 16 MHz), Teensy Cortex-M7 (high-performance). **Bus interface design**: pin count problem (37 Z80 signals in 40-pin DIP vs 30 RP2040 GPIOs) solved via external latches (74HC373), SPI port expanders (74HC595), external address decoders (PAL/GAL/CPLD), or larger STM32 packages; PIO-based approach allocates one PIO block for high address byte and other for data + low address + controls. **Voltage level translation**: 5V TTL bus vs 3.3V CMOS MCU — 74HCT245 buffers (HCT has TTL thresholds VIH=2.0V accepting 3.3V CMOS correctly, HC with CMOS thresholds VIH=3.5V does not); HCT family critical. **Timing requirements**: Z80 nanosecond-level bus timing (clock period 250 ns at 4 MHz, address→MREQ 50–100 ns, cycle durations 3 T-states for opcode fetch/memory read/write); realising on 133 MHz MCU = 38 host cycles per Z80 T-state, tight but workable via PIO + DMA + dual-core CPU. **Instruction-stepped vs cycle-stepped** emulation: instruction-stepped (simpler, loses timing fidelity), cycle-stepped (CPU and PIO collaborate cycle-by-cycle, authentic timing, needed for cycle-exact Spectrum compat). **Z80 instruction emulation**: documented instructions (8/16-bit load/store, exchanges, arithmetic, rotates/shifts, bit ops, jumps, calls/returns, stack, I/O, block operations LDIR/CPIR/INIR/OTIR, interrupts IM 0/1/2, misc); undocumented instructions (`SLL`/`SLI` opcodes 0x30–0x37 with bit 0 set to 1, `LD A,I`/`LD A,R` flags copy IFF2 to parity/overflow, `LDI/CPI/INI` N flag and H flag and P/V byte counter, `OUT (C),0` writes 0 on NMOS vs 0xFF on CMOS — Spectrum used NMOS, `BIT n,(HL)` affects X/Y flags bits 5 and 3 from byte read); cycle counts with subtle variations; implementation techniques (direct interpretation switch statement, threaded code avoiding dispatch overhead, JIT compilation rarely on MCU). **Existing projects**: PicoROM (RP2040 ROM/RAM/IO emulator), PicoZ80 (full Z80 + ULA replacement), Yazoo's Pico Spectrum, libz80 by Lin Ke-Fong (used in FUSE), z80ex (cycle-accurate), emu2149 (for AY-3-8912). **Integration with real Spectrum hardware**: pinout adapters mapping RP2040 GPIO to Z80 40-pin DIP, 74HCT245/541 level shifters, crystal oscillator or RP2040 PLL synthesising 3.5 MHz, RP2040 firmware. **MCU Z80 vs Real Z80 decision matrix** (timing, power, cost, reliability, debugging, tracing, additional features, bus capacitance, authenticity). **MCU Z80 vs FPGA T80 decision matrix** (timing, cost, development ease C/C++ vs Verilog, flexibility, integration with peripherals, performance overhead, power). FAQ (RP2040 speed sufficient with 38 cycles/T-state headroom, undocumented instructions needed for max compat, IM 0/1/2 implementation, 3.3V on 5V bus requires 74HCT buffers, ZEXALL passes but demos fail due to timing not instructions, MCU clock ≥30× Z80 clock = 105 MHz minimum, full Spectrum on single RP2040, bus capacitance and drive strength). Summary (5 requirements: pin allocation, PIO-driven bus interface, cycle-stepped execution, correct undocumented behaviour, level shifting). References (Zilog Z84C00 datasheet, Sean Young's undocumented Z80 doc, RP2040 datasheet, PicoROM/libz80/z80ex, Chris Smith's ULA book, 74HCT245/541 datasheets). Cross-references |
| `mcu_ula.md` | ✅ **ULA on a Microcontroller** — replacing the Ferranti ULA (most failure-prone original Spectrum component, no replacements since Ferranti sold to Plessey/scrapped tooling) with an MCU. Why replace: ULA failure symptoms (no video, garbage screen, no keyboard, no sound, random crashes), no original replacements available (NOS rare/expensive), Chris Smith's reverse-engineering book enables modern recreation, RP2040 PIO optimal for cycle-precise video. **ULA functions**: video generation (video address counter walking through display RAM in interleaved pattern, pixel shift register, attribute application via colour encoder with INK/PAPER/BRIGHT/FLASH, composite PAL signal with HSYNC/VSYNC/blanking/colour burst, BORDER mixing); memory arbitration (ULA shares RAM with CPU, asserts WAIT_n during active display producing contended memory timing in `0x4000–0x7FFF`, asymmetric pattern per scanline position); I/O ports (port `0xFE` write for beeper/MIC/EAR/BORDER colour, `0xFE` read for keyboard matrix row via `A[8:15]` and EAR input, `0xFF` floating bus); INT generation at scanline 64 every 20 ms; clock generation (14 MHz master / 4 = 3.5 MHz CPU); beeper (1-bit DAC via port `0xFE` bit 4). **Video generation on RP2040 PIO**: pixel timing (7 MHz pixel clock = one pixel every 143 ns, 448 pixels/scanline × 311 scanlines, 192 active × 256 active); PIO program for composite video (load pixel data into ISR, shift out 8 pixels/byte × 32 bytes/scanline, HSYNC 4 µs low + back porch + front porch, VSYNC sequence per PAL standard with equalisation pulses); composite signal requirements (HSYNC 4.7 µs, VSYNC PAL sequence, 4.43 MHz colour burst 10 cycles after HSYNC for TV colour decoder compat even though Spectrum signal is monochrome, blanking levels); VGA alternative (separate TTL HSYNC/VSYNC, RGB via resistor DAC, no PAL encoding, works with modern monitors at 50 Hz refresh); HDMI via Pico DVI project (bit-banged DVI through PIO). **Contention emulation** via state machine: inputs (current video position scanline + pixel, CPU accessing contended, position within 4-T-state character cycle); outputs WAIT_n decision; pseudocode in C; integration with cycle-stepped Z80 emulator running synchronously. **Floating bus emulation**: track ULA's current video fetch byte (most recent pixel or attribute byte fetched), return on `0xFF` read during contention cycle when ULA would have byte on bus, otherwise return `0xFF`. **I/O port bit tables** for port `0xFE` write (bits 0-2 BORDER colour 0-7, bit 3 EAR output enables MIC input, bit 4 MIC output/beeper, bits 5-7 unused) and read (bits 0-4 keyboard matrix row selected by `A[8:15]`, bit 5 unused, bit 6 EAR input, bit 7 unused). **Complete ULA replacement**: video address counter with bit shuffling (C code example with Y7-Y0 → addr 13 12 7 6 5 10 9 8 4-0 matching Spectrum's interleaved video memory layout); INT generation via timer at appropriate frame point; clock generation via RP2040 PLL; beeper GPIO toggle; **128K/+2/+3 considerations** (memory banking via port `0x7FFD`, AY-3-8912 sound chip integration or separate MCU, different contention scheme with contended page 5, different video timing with longer top border); **integration with other components** on single RP2040 (Z80 emulator, ULA emulator, RAM in 264 KB SRAM, ROM from flash/SD, AY-3-8912 emulator, keyboard controller, SD card storage via SPI — full Spectrum-on-a-chip). Existing projects (Pico Spectrum RP2040 complete, Yazoo's Spectrum, PicoVGA VGA library, Pico DVI HDMI output, SpecHMI original Spectrum integration). **Comparison with FPGA ULA recreation** (Harlequin/Sizif-512): MCU advantages (easier development in C/C++ vs Verilog/VHDL, lower cost £1 RP2040 vs £3-10 FPGA, faster iteration reflash firmware vs resynthesise HDL minutes, integrated peripherals USB/Wi-Fi/SD/debug built-in, larger community); FPGA advantages (native parallelism no scheduling overhead, lower timing jitter deterministic logic no interrupt latency, more authentic bus signals FPGA pins drive TTL natively, established solutions T80 + ULA HDL proven). Trade-off summary table (cycle-exact, cost, dev ease, iteration, bus drive, peripherals, power, community). FAQ (RP2040 generates real PAL composite via PIO + resistor DAC; cycle-exact contention with cycle-stepped design; floating bus implementation track ULA byte; ULA+Z80 on single RP2040 in Pico Spectrum projects; composite vs VGA/HDMI trade-off authentic vs daily use; video memory buffer optional but simplifies timing; contention accuracy gross pattern sufficient for 95% software, exact per-cycle for demoscene per Smith's book; 128K banking-aware contention via tracking banking register). Summary (5 requirements: PIO-driven video gen for cycle-precise pixel/sync timing; contention state machine for authentic memory access timing; floating bus emulation for screen position probing software; I/O port implementation port `0xFE` beeper/BORDER/keyboard and port `0xFF` floating bus; INT generation for 50 Hz frame interrupt). References (Smith's ULA book, RP2040 datasheet, Pico Spectrum/PicoVGA/Pico DVI GitHub projects, PAL composite video spec, Harlequin project for FPGA comparison, Sensible tests by Andrew Owen). Cross-references |
| `mcu_fdc_vg93.md` | ✅ **KR1818VG93 / WD1793 FDC on a Microcontroller** — replacing the Beta 128 disk interface's floppy disk controller with an MCU (typically STM32). **WD1793** (and Russian **KR1818VG93** clone) handles MFM/FM encoding/decoding, track seeking, sector read/write, CRC generation/checking, index pulse detection; presents a 5-register interface (Command, Status, Track, Sector, Data) at Beta 128 I/O ports `0x1F`/`0x3F`/`0x5F`/`0x7F`. **TR-DOS** by Mikhail "Misha" Shumakov (late 1980s): file operations (load, save, catalog, delete, rename), disk formatting, BASIC extension (`CAT`, `LOAD *"file"`, `SAVE *"file"`), binary loader — thin layer over Beta 128 hardware. Why replace: failing original chips (30+ years old — read errors, write failures, seek failures, complete failures), media degradation (magnetic domain decay, physical deterioration, fungal growth, mechanical wear), convenience of SD-card loading, authentic form factor preservation for Pentagon/Scorpion/ATM Turbo owners. **VG93Em-STM32 reference implementation**: STM32F103 Blue Pill or STM32F407, microSD via SPI at 12–25 MHz, 40-pin DIP connector for Beta 128 socket, optional status LEDs + config jumpers; firmware implements VG93 register interface and full command set (restore, seek, step/step-in/step-out, read sector/write sector, read address, read/write track, force interrupt); pseudocode C example showing vg93_state_t struct + command dispatch switch. **Disk image formats**: `.trd` (standard TR-DOS 640 KB = 80 tracks × 16 sectors × 256 bytes for 5.25" DS/DD), `.scl` (sector-based with different header), `.fdi` (full disk image with raw MFM data preserving copy protection), `.imd` (ImageDisk format with raw MFM), `.opd`/`.dsk`. **Seek emulation**: update internal track pointer, load track from SD card, BUSY bit reflects SD access time, settle time delay matching real chip. **Sector read/write**: DRQ bit set, host reads/writes Data register for each byte, 256 bytes per sector, completion via status register. **Status register bits**: 7 Motor On, 6 Write Protect, 5 Spin-Up/Ready, 4 Record Not Found/Seek Error, 3 CRC Error, 2 Track 0, 1 Index Pulse, 0 Busy. **Timing considerations**: real FDC at 300 RPM = 200 ms/revolution = 12.5 ms/sector at 16 sectors/track; DRQ every 31 µs for 256-byte sector; index pulse periodic; too fast = copy protection misbehaves, too slow = host times out. **Alternative implementations**: ESP32 (240 MHz with Wi-Fi for network disk image serving over HTTP, eliminating SD card), RP2040 (PIO for precise FDC interface timing + dual CPU cores for concurrent FDC logic + SD I/O), FPGA (MiSTer/ZX-Uno HDL VG93 with cycle-exact timing), **Gotek floppy emulators** (different approach — replace physical floppy drive with MCU device that presents as floppy to existing FDC, reads `.trd` from USB stick via HxC firmware). Comparison table across implementations (cost £2–130, difficulty, timing accuracy, best-for use case). **Integration with real hardware**: drop-in chip replacement on small PCB with 40-pin DIP + external SD slot cabling, requires pinout adapter + level shifters + SD card slot + configuration interface; alternative external module keeping original VG93 in place. **Copy protection considerations**: non-standard sector sizes (128/1024/2048 bytes), non-standard sector IDs outside 1–16, hidden tracks (81/82), weak/fuzzy bits producing different reads each time, timing-based protection measuring FDC event intervals — `.fdi`/`.imd` formats with raw MFM help but advanced protection difficult; users may need cracked versions. FAQ (STM32 F103 vs F407 choice, TR-DOS software compat at 95%+, image selection via buttons/OLED/config file, write-back support with 100k writes/sector SD endurance, Beta 128 ROM still needed separately, SPI vs SDIO trade-off, timing accuracy within microseconds). Summary (4 elements: drop-in chip replacement, SD-card storage, register-accurate emulation, timing-aware DRQ/status). References (WD1793 datasheet, KR1818VG93 Russian datasheet, VG93Em-STM32 GitHub, TR-DOS documentation, Beta 128 spec, HxC Gotek firmware, disk image format specifications). Cross-references |
| `mcu_psg_ay.md` | ✅ **AY-3-8912 PSG on a Microcontroller** — replacing the AY-3-8910/8912/8913 sound chip (or Yamaha YM2149, Russian KR1518VG94) with an MCU. Chip family (AY-3-8910 40-pin with 2 I/O ports, AY-3-8912 28-pin with 1 I/O port used in Spectrum 128K/+2/+3, AY-3-8913 24-pin no I/O ports, YM2149 Yamaha pin-compatible clone with slightly improved DACs, KR1518VG94 Russian clone — all share register interface). **16 registers**: R0-R5 tone A/B/C period 12-bit, R6 noise period 5-bit, R7 enable tone/noise per channel + I/O port config, R8-R10 channel A/B/C amplitude 5-bit (bit 4 = envelope mode), R11-R12 envelope period 16-bit, R13 envelope shape 4-bit (16 attack/decay/sustain/release combinations), R14-R15 I/O port data. 2-step host protocol (write register number to address latch at port `0xFFFD`, write data to data register at port `0xBFFD`, reads from `0xFFFD` return selected register value). **Sound generation**: square wave per channel (12-bit period, frequency = clock / (16 × period)), noise generator (5-bit period, 17-bit LFSR with feedback from bits 0 and 3), envelope generator (16-bit period, 4-bit shape selecting one of 16 attack/decay/sustain/release patterns), 4-bit logarithmic DAC per channel producing characteristic beepy sound. **PSG clock** varies per host (Spectrum 128K = 1.7734 MHz derived from 3.5469 MHz CPU clock / 2, Pentagon = 1.75 MHz producing subtly different pitch, YM2149 sometimes 1.75 or 2 MHz). Why replace: component failure (missing channels, noise generator failure, envelope failure, I/O port failure affecting Kempston mouse/+2 serial, total failure); audio quality enhancement (higher-resolution DACs 8/16-bit linear vs original 4-bit log, linear interpolation smoothing square waves, stereo output separating channels, digital filtering low-pass/high-pass); stereo output conventions (ABC = A left B centre C right, ACB, MON = original mono); multiple AYs (TurboSound 6-channel via second PSG at ports `0x3FFD`/`0x5FFD`, popular in demoscene). **Implementation**: register emulation in ay_state_t struct, tone generation with counter decrement and toggle (16 PSG cycles per step), noise LFSR with bit 0/3 feedback, envelope generator with 32-step patterns per shape, audio mixer combining 3 channels with amplitude × tone/noise source selection. **Audio output**: sample rate 44.1 kHz (CD quality) or 48 kHz; DAC options (MCU built-in 12-bit, PWM via GPIO + RC low-pass filter, external I2S DAC PCM5102 for 24-bit quality, R-2R resistor ladder). **Stereo output** code example showing ABC panning (sample_a left, sample_c right, sample_b/2 centre). **Multiple AYs** via separate ay_state_t structs with port-based dispatch. **Existing projects** (AY-3-8912 Emulator on STM32 drop-in, emu2149 by Vincent Sanders widely ported, ym2149_emul, Pico AY RP2040 with stereo, Schrödinger's AY). **AY file players** demonstrating audio quality (AY-emul by Mikhail Shcheglov, zxtune multi-platform, ChipSeeR). **Integration with real hardware**: drop-in 28-pin DIP chip replacement + level shifters + audio output routing, or external audio module tapping I/O ports. **Comparison with FPGA PSG** (MCU advantages: easier C/C++ vs Verilog, lower cost £1 RP2040 vs £3-10 FPGA, audio quality flexibility with external DACs, multi-AY trivial, stereo panning options; FPGA advantages: native parallelism tone/noise/envelope in true parallel, lower CPU overhead, established HDL cores). FAQ (YM2149 vs AY differences with envelope divide mode, log 4-bit amplitude scale for authentic beepy sound, 44.1 kHz sufficient for AY bandwidth, AY I/O port emulation for Kempston mouse, PSG clock config per host system, audio effects like reverb/chorus via DSP, AY file players running on modern PCs preserving music archive). Summary (5 benefits: eliminates component failure, improves audio quality, adds stereo output, supports TurboSound, maintains software compatibility). References (GI AY-3-8910/8912 datasheet, Yamaha YM2149 datasheet, emu2149 by Vincent Sanders, AY-emul by Shcheglov, .ay/.ym file format specifications, Spectrum 128K service manual, AY register community documentation). Cross-references |
| `mcu_keyboard.md` | ✅ **Keyboard Controller on a Microcontroller** — replacing the Spectrum's membrane keyboard (40-year-old failed membranes: dead keys, phantom keys, slow response, stuck keys) with a modern PS/2 or USB keyboard via an MCU. **8×8 keyboard matrix** (8 row lines from `A[8:15]`, 5 column inputs at port `0xFE` bits 0-4 — scan by setting bit low in high address byte, read 5 column bits from low byte; address mapping table for all 8 rows with all 40 keys: row 0 CAPS/Z/X/C/V, row 1 A/S/D/F/G, ... row 7 SPACE/SYM SHIFT/M/N/B; extended 128K/+2/+3 keyboard with numeric keypad and cursor keys via additional rows). **Limitations of membrane keyboard** (no N-key rollover without diode isolation causing 3-key ghosting since Spectrum matrix has no isolation diodes, slow membrane response, membrane degradation of conductive traces, poor tactile feedback from rubber domes). Why replace with MCU: membrane failure, ergonomic improvement (proper feedback, N-key rollover, function keys F1-F12, numeric keypad, cursor keys), joystick integration via Kempston/Sinclair 1/Sinclair 2/Fuller/Protek, mouse integration via Kempston mouse. **MCU choices**: RP2040 (Raspberry Pi Pico, dual Cortex-M0+ at 133 MHz overclockable to 250 MHz, **PIO blocks**, 30 GPIOs, USB host via TinyUSB library, ~£1 — optimal), ESP32 (Xtensa/RISC-V at 240 MHz with Wi-Fi/Bluetooth for wireless keyboards, fewer GPIOs, ~£3), STM32 (F103 Blue Pill at 72 MHz or F407 at 168 MHz with hardware USB OTG, 5V-tolerant GPIOs on some models eliminating level shifters, ~£2), Arduino ATmega32U4 (Leonardo/Micro with native USB, 8-bit AVR at 16 MHz, basis for many DIY adapters, ~£3). **Hardware connection to the Spectrum**: membrane connector replacement (invasive — 8 row + 5 column ribbon cables directly driven by MCU, requires opening Spectrum); joystick port connection (non-invasive but joystick-only); expansion port connection (intercepts I/O reads to port `0xFE`, fully non-invasive — the standard commercial approach). **PS/2 keyboard input**: PS/2 protocol (clock + data lines, ~10-17 kHz, 11 bits per byte = start + 8 data LSB first + parity + stop; keyboard sends make code on key press and `0xF0` break code on release; MCU samples data on clock falling edge via interrupt). Scan code to ZX matrix translation via lookup table `ps2_to_zx[256]` indexed by scan code returning (row, col); 64-bit keyboard_state bit per matrix key; handle_make_code/handle_break_code C functions. CAPS SHIFT (row 0 col 0) vs SYMBOL SHIFT (row 7 col 1) handling — PC Shift maps to CAPS SHIFT, PC digits map to SYMBOL SHIFT + corresponding key, arrow keys map to CAPS SHIFT + 5/6/7/8, Backspace to CAPS SHIFT + 0. Layout variations (US QWERTY, UK, German QWERTZ, French AZERTY) — scan codes are positions not characters, translation table must match keyboard layout. **USB keyboard input**: USB host MCUs (RP2040 with TinyUSB library providing HID parser, ESP32 S2/S3 with OHCI controller, STM32 OTG, Arduino + USB Host Shield). USB HID protocol (8-byte reports: byte 0 modifier flags Ctrl/Shift/Alt, byte 1 reserved, bytes 2-7 up to 6 simultaneously-pressed keycodes — gives true N-key rollover); HID keycode translation table similar to PS/2 but separate keycodes. **Joystick emulation**: Kempston (I/O port `0x1F` bits 0-4 = right/left/down/up/fire with C code for update_joystick), Sinclair 1 (keys 6-0 = left/right/down/up/fire via keyboard matrix), Sinclair 2 (keys 1-5), Fuller (port `0x7F` bits 0-3 + bit 6 fire), Protek/AGF (port `0xDF`). Gamepad mapping for modern USB/Bluetooth gamepads (D-pad to direction bits, A to fire, B to up+fire for platformer jump, Start to ENTER, Select to SPACE). **Kempston mouse emulation** (I/O ports `0xFBDF` for X, `0xFFDF` for Y, `0xFADF`/`0xBFDF` for buttons; 8-bit X/Y counters updating from PS/2 or USB mouse deltas; button bits 0/1/2 = right/left/middle; C code for kempston_mouse_t struct and movement/button handlers). **Existing projects**: ZXHIDKeyboard (open-source RP2040 or STM32 in expansion port with USB keyboard, multi-layout, Kempston mouse translation, function key shortcuts F1-F10 for NMI/reset/snapshot/tape), ZXKey (Arduino ATmega32U4 membrane replacement for PS/2 keyboards — sits inside Spectrum), ZXKB (ATmega328P Nano with PS/2 + Kempston port), RetroBrew adapters (RP2040-based community projects), ESP32 custom adapters with Bluetooth keyboard support. Comparison table of approaches (Arduino membrane replacement cheap/easy/PS/2-only; RP2040 expansion port medium/full features; STM32 expansion port medium; ESP32 Bluetooth wireless). **Integration with real hardware**: membrane connector approach (5 steps — open Spectrum, disconnect membrane, wire adapter to membrane connector 8 row + 5 column lines, power from 5V supply, connect PS/2 keyboard); expansion port approach (4 steps — build adapter with edge connector, plug into expansion port, connect USB/PS/2 keyboard, power on — non-invasive preserves original hardware); modern recreation approach (keyboard scan in MCU firmware alongside ULA emulation, no adapter needed). FAQ (PS/2 vs USB trade-off — PS/2 simpler two GPIOs but USB increasingly common; multiple keyboards via OR'd states; F1-F12 mapping to Spectrum actions like NMI/reset/snapshot/tape play; Caps Lock LED added by MCU since Spectrum has none; wireless keyboards via ESP32 Bluetooth or wireless USB receiver; keyboard scan speed 50 Hz with microsecond MCU response; Cyrillic layout for Russian Spectrums Pentagon/Scorpion via configuration). Summary (5 functions: receive input from modern keyboard/joystick/mouse/gamepad, translate to Spectrum matrix, drive matrix or intercept scan, optionally emulate joysticks and mouse, provide additional features like function keys and multi-layout and wireless). References (Chris Smith's *The ZX Spectrum ULA* book for keyboard scan logic, Spectrum 48K Service Manual for matrix schematic and connector pinouts, Adam Chapweske's PS/2 Keyboard Protocol documentation, USB HID Usage Tables official spec, RP2040 datasheet, TinyUSB library for USB host and HID parsing, ZXHIDKeyboard and ZXKey open-source projects, Kempston joystick/mouse interface documentation). Cross-references |
| `mcu_video_adapter.md` | ✅ **Video Adapter on a Microcontroller** — converting the Spectrum's composite PAL (48K) or RGB (128K/+2/+3) video output to modern formats (VGA, HDMI, DVI) via an MCU, with upscaling and optional CRT effects. Why need adapter: modern displays don't like Spectrum signals (composite PAL blurry via TV modulator with poor modern downscaling and comb filter artifacts; RGB on SCART increasingly rare on modern TVs that treat it as composite-only; 50 Hz refresh conflicts with 60 Hz native monitors causing frame skipping or sync refusal; 256×192 active resolution tiny on 1920×1080/4K modern displays; CRT artifacts lost on flat-panels). **Adapter role** (4 functions: receive Spectrum video via signal intercept/video memory read/emulator internal state, convert to VGA/HDMI/DVI, upscale 256×192 or 512×192 multicolour to modern resolution, add optional CRT effects like scanlines/phosphor mask/bloom). **Video output options**: Composite PAL recreated via RP2040 PIO + resistor DAC (authentic but low quality for original CRT TVs, inherits all composite problems); VGA (analog RGB 0–0.7V per channel + TTL HSYNC/VSYNC 5V, accepts wide range of resolutions and refresh rates, RP2040 + 3 resistors per colour for 3-bit/512 colours or ADV7125 triple video DAC for 24-bit/16.7M colours); HDMI/DVI (digital, high data rate 25 MHz pixel clock for 640×480 = 250 Mbps per channel, via bit-banged DVI with RP2040 PIO per **Pico DVI** project by Luke Wren OR external HDMI encoder like **ADV7513** supporting 1080p + audio I2S or **TFP410**); DisplayPort (rare in MCU projects, complex encoding, different connector licensing — most target HDMI). **VGA output on RP2040**: hardware (3-bit colour per channel via 9 resistors total, HSYNC/VSYNC direct GPIO no level shifting, VGA 15-pin DSUB connector; or ADV7125 for 8-bit per channel 24-bit colour); PIO program (pixel loop shifting one pixel/cycle, HSYNC at end of scanline drives low then returns to blanking level, VSYNC at end of frame drives low for 2 lines, pixel data read from frame buffer via DMA); **PicoVGA library** by Miroslav Nemecek (defines standard modes 320×240/640×480/800×600, frame buffer in RP2040 RAM, handles PIO programming + DMA setup, supports 8-bit palettised 256 colours or 4-bit 16 colours, includes primitives for pixels/lines/rectangles/text); VGA timing 640×480 @ 60 Hz (pixel clock 25.175 MHz approximated 25 MHz, HSYNC 96 pixels low 3.8 µs + 16 pixels back porch + 480 pixels active + 16 pixels front porch = 800 total 31.77 µs/scanline, VSYNC 2 lines low + 33 lines back porch + 480 lines active + 10 lines front porch = 525 total, frame rate exactly 59.94 Hz; custom VGA mode for 50 Hz like 800×600 @ 56 Hz or 640×480 @ 50 Hz accepted by most monitors). **HDMI via Pico DVI** by Luke Wren: three TMDS channels for R/G/B + fourth TMDS channel for clock; three PIO state machines shift out 10-bit TMDS symbols at pixel clock rate (25 MHz for 640×480); external circuit three pairs of GPIO pins differential with simple resistor network providing 100-ohm differential impedance; library handles TMDS encoding (each 8-bit pixel mapped to 10-bit symbol minimising transitions). Limitations (max 640×480 or 800×600 @ 60 Hz, 264 KB RP2040 RAM tight for frame buffer + Z80 emulator, no audio since PIO fully occupied). **External HDMI encoder ADV7513** (~£10, supports up to 1920×1080 @ 60 Hz 1080p, audio support via I2S from MCU, HDCP included but not useful for retro, standard HDMI connector; TFP410 is alternative). **Upscaling algorithms**: Nearest neighbour integer scaling (each Spectrum pixel becomes 2×2 or 3×3 or 4×4 block — 256×192 × 3 = 768×576; fast no calculation just memory copy with stride, sharp pixels preserves pixel art, no artefacts, but blocky at high scale and may not fit standard resolutions exactly — most common in retro computing); Bilinear filtering (smooths by blending neighbours, softer less pixelated, but destroys sharp pixel art aesthetic — rarely used for retro adapters); Scanline interpolation (256×384 alternating pixel rows and scanline rows then scaled); Integer scaling with aspect ratio correction (Spectrum pixels wider than tall — 256×192 has 4:3 aspect ratio not 16:9, integer scaling often can't preserve exact 4:3 — options: square pixels at wrong aspect ratio e.g., 3×3=768×576 is 4:3 acceptable, non-integer vertical scaling to maintain aspect, or letterboxing with black bars; most retro adapters use first approach with slight distortion). **Scanline generation**: scanline effect darkens every other row by 50% (C pseudocode for apply_scanlines iterating every other y, halving RGB components), strength configurable 50% strong to 25% subtle; phosphor mask (vertical stripes of colour subpixels mimicking shadow mask, computationally intensive, rarely on MCU); bloom/glow (bright pixels bleed into neighbours via 3×3 box blur, rarely on MCU due to cost). **Receiving Spectrum's video**: intercepting analog video signal via ADC scan converter (samples video at pixel rate, complex, few MCU projects); reading video memory from integrated MCU ULA replacement (video memory already in MCU RAM, simplest — how Pico Spectrum projects work); frame grabber via fast SPI or parallel interface (host sends video memory periodically); software emulator internal state (Z80 + ULA emulator runs on MCU, video memory in emulator RAM). **Existing projects**: PicoVGA library by Miroslav Nemecek (comprehensive VGA driver, basis for many Spectrum-on-Pico projects), Pico DVI by Luke Wren (DVI from RP2040 PIO, combined with Spectrum emulator gives HDMI from £1 MCU), RGB-to-HDMI by Ian Stocks and David Banks (Pi Zero scan converter digitising analog RGB and re-emitting as HDMI, plus RP2040 variant using PIO to sample digital video signal), Retroleum SMARTi (expansion port VGA from 48K), ZX-HD (HDMI output for 48K and 128K), Spectra (RGB and other outputs). Comparison table of output formats (Composite PAL ~£1 medium difficulty low quality; VGA resistor DAC ~£1 easy good quality; VGA ADV7125 DAC ~£5 medium high 24-bit; HDMI Pico DVI ~£2 hard high; HDMI ADV7513 ~£12 medium high with audio; RGB-to-HDMI Pi Zero ~£15 medium very high). **Integration with original hardware**: external adapter (small box taking composite cable/RGB cable/edge connector direct digital, non-invasive works with any Spectrum); integrated adapter (MCU Spectrum like Pico Spectrum/Harlequin generates video directly, video output circuit built into main board — most elegant but requires full Spectrum on MCU). FAQ (minimum resolution 640×480 for 2× scale with letterboxing, 768×576 for pixel-perfect 3× but non-standard mode; audio on HDMI only via ADV7513 not Pico DVI since PIO fully occupied; monitor refusing 50 Hz sync — use European monitor or output 60 Hz with slight speedup or frame interpolation duplicating every 5th frame; attribute clash preserved as authentic property of original hardware not 'fixed'; screenshot capture via SD card as PNG/BMP; video output latency negligible for RP2040 direct, 1-2 frames for external HDMI encoders due to internal buffering). Summary (5 functions: receive Spectrum video, upscale to modern resolution, generate VGA/HDMI/DVI signal, optional CRT effects scanlines/phosphor/bloom, aspect ratio handling 4:3 with letterboxing or slight distortion). References (PicoVGA library by Nemecek GitHub, Pico DVI project by Wren GitHub, RGB-to-HDMI project wiki by Stocks and Banks, ADV7513 and ADV7125 datasheets from Analog Devices, VGA timing documentation e.g., TinyVGA, DVI specification for TMDS encoding, RP2040 datasheet for PIO programming, Retroleum SMARTi and ZX-HD and Spectra commercial adapters, Chris Smith's *The ZX Spectrum ULA* for video timing). Cross-references |
| `mcu_sd_interface.md` | ✅ **SD Card Interface on a Microcontroller** — modern mass storage upgrade for the Spectrum, replacing cassette tape (slow ~1500 baud, unreliable) and floppy disk (Beta 128/TR-DOS requiring 30+ year-old media) with SD cards. Why SD cards: capacity (thousands of Spectrum programs on one card, entire World of Spectrum archive fits in a few GB, 1 GB SD = 1,500 floppies); speed (SD card 10–25 MB/s via SPI vs floppy disk ~62 KB/s = 300 RPM × 16 sectors/track × 256 bytes/sector — a Spectrum program that takes 30s from floppy loads in <1s from SD); reliability (solid-state no moving parts no magnetic media to degrade, write endurance 100k+ writes/sector effectively unlimited for retro use); cost (4-8 GB SD card ~£2-3, microSD cheaper, SD card slot simple PCB connector). **SD card basics**: families (SDSC Standard Capacity up to 2 GB original spec, **SDHC High Capacity 4–32 GB** most common today using FAT32, SDXC Extended Capacity 64 GB–2 TB requiring exFAT, SDUC Ultra Capacity 2 TB+ very new rare — SDHC is sweet spot for Spectrum use); form factors (Standard SD 32×24 mm original, miniSD 21.5×20 mm rare obsolete, **microSD 15×11 mm** most common today used in phones and most retro adapters); protocols (**SPI mode** uses 4 signals CS/SCK/MOSI/MISO simpler slower but supported by virtually all MCUs at 12-25 MHz giving 1.5-3 MB/s — preferred for retro; **SDIO mode** uses 4 or 8 data lines faster but more complex requiring MCU hardware support like STM32/ESP32). **Hardware connection**: SPI mode pinout (DAT2 unused pulled high with 10K, CD/DAT3=CS Chip Select any GPIO, CMD=MOSI Master Out Slave In on SPI MOSI, VDD 3.3V power, CLK=SCK Serial Clock on SPI SCK, VSS Ground, DAT0=MISO Master In Slave Out on SPI MISO, DAT1 unused pulled high with 10K); all signals 3.3V logic level — SD card is **not 5V tolerant**; **level shifting** (5V Arduino needs resistor dividers on MOSI/SCK/CS 5V→3.3V and buffer or direct connection on MISO since 3.3V is high enough for 5V TTL logic; 3.3V MCU like RP2040/ESP32/STM32 connects directly no level shifting needed); power supply 3.3V at up to 100 mA during write operations — most MCU boards have 3.3V regulator that can supply this but check current rating since some cheap Arduino clones have weak 3.3V regulators; card detect (CD) switch mechanical closes when card inserted connected to GPIO for hot-swap detection allowing firmware to remount file system; write protect (WP) switch on full-size SD cards not microSD, ignored by most retro adapters. **SD card SPI protocol** documented in SD Physical Layer Specification: initialization sequence (1. Power up apply 3.3V wait 1 ms; 2. Set slow SPI clock 100-400 kHz; 3. Send 80 dummy clocks with CS high and MOSI high to wake card; 4. Send CMD0 RESET with CS low switches card to SPI mode expecting R1 response byte 0x01 idle state; 5. Send CMD8 SEND_IF_COND checks voltage range SDHC/SDXC respond with voltage window in R7; 6. Send CMD55 + ACMD41 SD_SEND_OP_COND repeatedly with HCS bit 30 set to indicate SDHC support — loops until 0x00 ready response; 7. Send CMD58 READ_OCR reads Operating Conditions Register including CCS bit indicating SDHC block-addressed vs SDSC byte-addressed; 8. Switch to high-speed clock 12-25 MHz). Read/write commands (CMD17 READ_SINGLE_BLOCK reads 512-byte block responds with start token 0xFE + 512 data + 2 CRC; CMD24 WRITE_BLOCK writes 512-byte block host sends start token + 512 data + 2 CRC; CMD18 READ_MULTI_BLOCK reads consecutive blocks until CMD12 STOP_TRANSMISSION; CMD25 WRITE_MULTI_BLOCK writes consecutive blocks; CMD13 SEND_STATUS reads status register). SDHC/SDXC addresses are block numbers, SDSC addresses are byte addresses — CMD58 READ_OCR tells host which scheme. C pseudocode for sd_init() and sd_read_block() with full sequence including CS handling and start token 0xFE polling. **File system support**: FAT16 vs FAT32 vs exFAT (FAT16 for SDSC up to 2 GB, **FAT32 for SDHC 4-32 GB is standard choice for Spectrum use**, exFAT for SDXC 64 GB+ requires Microsoft licensing rarely implemented in MCU projects); FAT implementation includes boot sector parsing read BIOS Parameter Block BPB determining cluster size/FAT location/root directory location, FAT table access following cluster chains to read file data, directory listing reading 8.3 filenames or LFN long filenames, file open/read/write high-level operations. Open-source FAT libraries: **FatFs by Elm-Chan** de facto standard for MCU well-documented portable supports FAT12/16/32 LFN multiple partitions; **Petit FatFs** smaller read-only for MCUs with limited RAM; **Arduino SD library** based on older FatFs simplified API. **Spectrum integration**: **DivMMC** is most popular SD interface standard successor to original DivIDE which used IDE hard drives — plugs into Spectrum expansion port, contains MCU often ATmega or RP2040 + microSD slot, presents memory-mapped interface 16 KB DivMMC ROM paged into Spectrum address space when accessed, ROM contains file browser often **ESXOS** or **DIVI** for user navigation, loads `.tap`/`.tzx`/`.z80`/`.sna`/`.scr` formats — when user selects `.tap` file DivMMC plays it through Spectrum's EAR input at higher speed than real tape; **DivMMC EnJon** is popular commercial implementation small expansion port device with DivMMC + Kempston joystick port + tape input passthrough. **ZXMMC** by Zaxos open-source — Z80 bit-bangs SPI directly via I/O ports no MCU involved, needs small CPLD or GAL for address decoding but no MCU firmware, minimalist design. **ZX Div Future OS** complete operating environment for SD-connected Spectrums with file management/text editor/assembler. **Tape emulation** simplest — MCU plays `.tap`/`.tzx` through Spectrum's EAR input, works with any Spectrum no expansion port needed, no special software, but loads at tape speed ~1500 baud. **Generic mass storage**: for TR-DOS the SD interface maps `.trd` disk image to Beta 128's I/O ports per [FDC emulation](mcu_fdc_vg93.md); for +3 DOS maps `.dsk` image to +3's uPD765 FDC giving full compatibility with disk-based software. **Image file formats**: tape formats (`.tap` simplest raw blocks with sync pulse sequence + header/data flag + data bytes + checksum; `.tzx` more comprehensive supporting all tape loading variations including custom speed loaders and copy protection tricks with detailed header structure different block types for pilot tones/data blocks/pure tones by Tomaz Kac; `.csw` Compressed Square Wave sample-based; `.wav` raw audio played as if from real tape); snapshot formats (`.sna` 48K snapshot with RAM + CPU registers PC/SP/AF/BC/DE/HL/IX/IY restoring exact state; `.z80` more flexible supporting 48K and 128K with hardware state extensions; `.sp`/`.szx`/`.rzx` less common); disk images (`.trd` TR-DOS, `.dsk` generic, `.fdi` raw MFM preserving copy protection); screen formats (`.scr` 6912 bytes = 6144 bytes pixel data + 768 bytes attribute data, loads instantly as still image). **Existing projects**: DivMMC EnJon (commercial microSD + ESXOS firmware + Kempston port + tape passthrough); ZXMMC by Zaxos (open-source direct SPI Z80 bit-bang with CPLD address decoding); ZX-Uno and MiSTer (integrated SD via DivMMC protocol, no separate adapter); simple DIY adapters (Arduino + SD card shield + wires to expansion port or EAR input, RP2040 Pico + SD card breakout + custom firmware, ESP32 with built-in SD card slot on some boards); tape-only emulators (simplest — small device connecting to EAR input, MCU plays `.tap`/`.tzx` from SD, requires no expansion port). Comparison table of approaches (Tape emulator ~£2 Arduino+SD easy all Spectrums simple loading; DivMMC ~£10-20 medium best all-rounder; ZXMMC ~£5 DIY hard minimalist DIY PCB; TR-DOS emulation ~£3 STM32 Pentagon/Scorpion owners; Integrated ~£50-150 for FPGA like ZX-Uno/MiSTer). FAQ (max SD card size 32 GB SDHC since SDXC exFAT rarely supported but 32 GB more than enough; SD card not recognised — wrong format NTFS/exFAT vs FAT32, wrong partition type, card too large, counterfeit card; hot-swap supported via CD pin but risky during write safer to eject via software or power off; loading speed tape emulation at tape speed ~1500 baud ~190 bytes/s or accelerated, DivMMC much faster near-instant for snapshots few seconds for tape via turbo loading, ZXMMC 50-200 KB/s depending on Z80 SPI bit-bang speed; saving supported with 100k writes/sector SD endurance effectively unlimited for retro use; no special ROM needed for DivMMC since ROM provided by adapter paged in when needed, but loader needed for ZXMMC often from small EEPROM or via tape; +3 DOS via uPD765 emulation less common than Beta 128). Summary (5 functions: connect SD card via SPI to MCU or directly to Z80 bit-bang, implement FAT file system typically FAT32 so card can be loaded from any PC, load various image formats tape/snapshot/disk/screen, present storage to Spectrum as file browser or TR-DOS disk or tape via EAR, provide fast loading seconds instead of minutes). References (SD Physical Layer Simplified Specification SD Association free download, FatFs by Elm-Chan elm-chan.org de facto standard, DivMMC documentation community wiki and ESXOS docs, ZXMMC project by Zaxos, TAP file format specification on World of Spectrum archive, TZX file format specification by Tomaz Kac comprehensive, SNA and Z80 file format specifications widely documented, RP2040 SPI examples in SDK, Arduino SD library for simpler projects). Cross-references |
| `n_go.md` | ✅ **N-Go — Complete Spectrum on a Microcontroller** — synthesis of all previous MCU articles (Z80, ULA, FDC, PSG, keyboard, video, SD) into complete Spectrum implementation in firmware. **N-Go** (also called Spectrum-on-a-chip) implements entire machine (CPU, ULA, peripherals, mass storage, video, audio, input) on one or more microcontrollers — distinct from [FPGA recreations](../fpga/) (HDL) and [software emulators](../software/) on PCs. Motivation: component scarcity (original Z80s/ULAs rare and expensive), cost under £10, customisation (firmware modifiable with enhancements like stereo sound/scanline effects/save states), repairability (cheap MCU replacement), educational value (teaches how Spectrum works at fundamental level), portability (small board with HDMI). **Integration challenges**: CPU time budget (Z80 at 3.5 MHz requires ~35-70 MHz host processing at 10-20 MCU cycles per Z80 cycle — RP2040 at 133 MHz overclockable to 250 MHz gives comfortable margin); memory bandwidth (ULA reads video memory at ~7 MHz pixel rate must interleave with Z80 accesses — RP2040 SRAM single-cycle at 133 MHz ample bandwidth); real-time constraints (video output shifts pixels at pixel clock with no margin for delay so must be PIO/DMA-driven, audio PSG must produce samples at 44.1/48 kHz without gaps); peripheral pin multiplexing (all peripherals share 30 RP2040 GPIOs requiring careful pin assignment). **System architectures**: **Single-MCU** (one RP2040 — Core 0 runs Z80+ULA+keyboard, Core 1 runs PSG+SD+file browser+misc, PIO blocks for video/PS2/DMA — most elegant but memory constrained 264 KB SRAM tight for 128K Spectrum, solved with flash XIP for ROM or external PSRAM like Pimoroni Pico DV or limiting to 48K); **Dual-MCU** (RP2040 for Z80+ULA+video + ESP32/STM32 for keyboard/SD/network — more flexible each MCU focuses on tasks, ESP32 adds Wi-Fi for network loading, communicates via SPI/UART but adds inter-MCU protocol complexity); **Multi-MCU** (separate MCUs per component — Z80 MCU + video MCU + audio MCU + I/O MCU — overkill but gives FPGA-like accuracy with dedicated hardware per component). **Memory architecture**: 48K memory map (ROM 16 KB in RP2040 flash via XIP, RAM 48 KB in SRAM, frame buffer in SRAM, stack and heap in SRAM); 128K banking logic via port `0x7FFD` with 8 banks of 16 KB C code for read_mem dispatching between ROM/bank 5/bank 2/paged bank; ROM storage options (flash XIP preferred fast no SRAM waste, SD card loaded at boot allows ROM swapping, embedded in firmware as C array); frame buffer sizing (VGA 640×480 8-bit = 300 KB too large, VGA 320×240 8-bit = 75 KB fits, direct Spectrum 256×192 = 48 KB at 8-bit or 6.9 KB at 1-bit+attributes — larger buffers need external PSRAM, on-the-fly generation from video memory like original ULA is most efficient). **Firmware structure**: main loop pseudocode init hardware SPI/PIO/PS2 + mount SD card via FatFs + init Z80/ULA/PSG emulators, loop runs one frame's worth of ~70,000 Z80 cycles via z80_run_frames, updates PSG/keyboard/frame buffer; multicore setup pseudocode Core 0 Z80+ULA+video via core0_main while loop, Core 1 keyboard+SD+PSG+network via core1_main, launched via multicore_launch_core1; interrupt handling vertical sync INT at 50 Hz via hardware timer asserting Z80 INT input emulator jumps to ISR at 0x0038. **Existing projects**: Pico Spectrum (collective name for RP2040 implementations — Yazoo's Pico Spectrum, PicoZX, community builds using libz80 or z80ex with VGA/HDMI/SD/PSG); **SpecHMI** STM32F407-based popular in Russian community with VGA + PS/2 + SD + beeper + PSG + optional ESP8266 network; ZX Spectrum on ESP32 (240 MHz with Wi-Fi + Bluetooth keyboard + HDMI/VGA). Comparison table MCU vs FPGA (cost £1-10 vs £3-150, C/C++ vs Verilog/VHDL, iteration seconds vs minutes, timing good cycle-stepped vs excellent hardware, bus emulated vs native, flexibility easy vs harder HDL, community large vs smaller specialised); comparison with other approaches (vs original hardware cheaper more reliable but lacks authentic feel; vs FPGA recreations cheaper easier but less accurate timing; vs software emulators on PC closer to real hardware as dedicated device; vs emulators on retro hardware impractical host too slow). FAQ (Arduino too slow 16 MHz + 2 KB RAM; RP2040 single chip can do 128K Spectrum tight at ~200 KB of 264 KB SRAM leaving ~64 KB free; timing accuracy very good with cycle-stepped for most software and demos but edge cases differ — FPGA preferred for demoscene-level accuracy; add features like save states/rewind/turbo mode/cheat codes/stereo sound/scanline effects/debugging; load software via SD card file browser or USB or Wi-Fi; connect original peripherals via level shifters). Summary (8 components: Z80 emulation, ULA emulation, full RAM, beeper+PSG sound, keyboard/joystick/mouse input, SD card mass storage, VGA/HDMI/composite video output, optional peripherals like Beta 128/Kempston). References (RP2040 datasheet and Pico SDK documentation, libz80 by Lin Ke-Fong, z80ex cycle-accurate emulator, PicoVGA library by Nemecek, Pico DVI project by Wren, Pico Spectrum GitHub projects, SpecHMI project documentation, FatFs by Elm-Chan). Cross-references |
| `mcu_design_patterns.md` | ✅ **MCU Design Patterns for Spectrum Integration** — general engineering patterns for connecting a modern MCU to 1980s hardware, independent of any specific component. Covers three core questions: voltage translation (3.3V MCU to 5V TTL bus), timing-critical I/O (nanosecond-level Z80 bus response), and real-time firmware architecture (handling video/audio/input/storage simultaneously). **Bus interfacing techniques**: memory-mapped I/O (MCU appears as region of Spectrum address space, decodes addresses and responds to `MREQ_n`/`RD_n`/`WR_n` — standard for memory expansions, DivMMC ROMs, interface ROMs), port I/O (responds to Z80 `IN`/`OUT` via `IORQ_n` and address low byte — used by ports `0xFE` ULA, `0x1F` Kempston, `0xFFFD`/`0xBFFD` PSG, `0x7FFD` banking, Beta 128 FDC ports, partial decoding common like `A[5]=0`), DMA (MCU asserts `BUSRQ_n` to take over the bus, rarely used due to Z80 disruption and complexity), bus master vs bus slave (most adapters are slaves responding to Z80 cycles; CPU replacements like [PicoZ80](mcu_z80.md) and DMA controllers are masters generating the bus cycles). **Voltage level translation**: 5V TTL (VIH=2.0V, VIL=0.8V, VOH ~2.4V min typically ~3.5V) vs 3.3V CMOS (VIH=0.7×VDD=2.3V, VIL=0.3×VDD=1.0V, VOH ~3.3V) — 3.3V output high exceeds TTL threshold so reading 3.3V MCU into 5V TTL works for high state, and 5V TTL output low within 3.3V CMOS low threshold so low state works; problem: 5V TTL output high can exceed 3.3V MCU absolute max causing ESD diode conduction, clamping to VDD+0.3V, damage over time and latch-up. **Critical 74HCT vs 74HC distinction** (single-letter difference is a common beginner mistake): 74HCT (High-Speed CMOS TTL-compatible inputs VIH=2.0V) accepts 3.3V correctly, outputs 5V CMOS ~5V; 74HC (High-Speed CMOS CMOS inputs VIH=0.7×VDD=3.5V at 5V VDD) does NOT accept 3.3V reliably — signal is below threshold, randomly misreads as low. Common buffer ICs (74HCT245 octal bidirectional transceiver with DIR/OE workhorse for data bus, 74HCT541/244 unidirectional for address bus, 74HCT273 D-flip-flop for latching outputs, 74HCT373/573 transparent latch for address). Directional translation (5V bus→3.3V MCU use 74LVC541/HCS541 powered at 3.3V accepting 5V inputs and outputting 3.3V, or series resistor limiting ESD diode current; 3.3V MCU→5V bus use 74HCT powered at 5V accepting 3.3V via TTL thresholds and outputting 5V). Bidirectional data bus via 74HCT245 with DIR tied to `RD_n` and `OE_n` to decoded address (C code for update_bus_direction checking RD_n/WR_n and setting DIR/OE pins). Resistor dividers cheap simple but slow ~1 MHz max with RC time constant and bus capacitance, unidirectional only, lossy — suitable for PS/2/UART/static GPIO. Dedicated level shifters TXB0108 (8-channel bidirectional auto-sensing 20 MHz push-pull / 1 MHz open-drain I2C), TXS0108E (with integrated pull-ups for I2C/SPI), SN74LVC1T45 (single-channel with DIR up to 100 MHz) — convenient for peripherals but rarely needed for Z80 bus where 74HCT buffers preferred for higher drive. Power sequencing (apply 5V first, then 3.3V via LDO, MCU pins high-Z during reset default, MCP100 POR supervisor ensures MCU in reset until VDD stable — backpowering if MCU pins driven high before VDD stable causes erratic startup and latch-up). 5V-tolerant MCUs (STM32 FT pins accept 5V directly no buffer for reading, ATmega328P runs at 5V natively, but output still 3.3V so buffers needed for CMOS-destination chips). **Timing-critical I/O**: Z80 clock period 286 ns at 3.5 MHz, bus cycles 3-4 T-states ~860-1140 ns, setup/hold windows 30-50 ns for address/data/control signals; RP2040 at 133 MHz has 7.5 ns cycle = ~38 cycles per Z80 T-state, enough for software response but only barely — direct GPIO manipulation in software rarely fast enough. Cycle-stepped vs instruction-stepped Z80 emulation (instruction-stepped simpler loses per-cycle fidelity used by libz80 by Lin Ke-Fong; cycle-stepped accurate per-T-state preserving contention/interrupt response/floating bus used by z80ex and serious emulators; cycle-stepping essential for bus master but not needed for bus slave where real Z80 generates timing). **RP2040 PIO** as game changer — each PIO block has 4 state machines executing 1-cycle instructions independently of CPU with deterministic jumps, direct GPIO access in single cycle, 4-word TX/RX FIFOs per state machine decoupling PIO from CPU, ISR/OSR shift registers for serial protocols; typical Z80 bus response sequence (WAIT 0 gpio IORQ 1 cycle → IN PINS 8 read address 1 cycle → JMP PIN compare 1 cycle → OUT PINS 8 drive data 2 cycles → WAIT 1 gpio IORQ 1 cycle → SET PINS high_z 1 cycle) = 5-7 cycles = ~37-52 ns well within Z80 budget; CPU free to refill FIFOs asynchronously. DMA patterns (memory→PIO TX FIFO for video pixels/audio samples at PIO's own rate with DMA refilling FIFO as needed, PIO RX FIFO→memory for captured bus data snooped by PIO, memory→memory for frame buffer updates/image scaling triggered by CPU, DMA chaining for complex pipelines without CPU intervention — RP2040 has 12 DMA channels). Interrupt latency (ARM Cortex-M0+ 12 cycles ~90 ns at 133 MHz, Cortex-M4 12 cycles ~71 ns at 168 MHz, Xtensa LX6 variable 200-500 ns depending on cache — too slow for direct Z80 bus response so PIO/glue logic required; interrupts appropriate for SD card data ready / audio buffer low / frame vertical sync; RP2040 NVIC supports priorities allowing high-priority audio to preempt low-priority SD). Jitter sources (flash cache misses on RP2040 XIP with variable latency cache hit ~1 cycle miss ~50+ cycles solve with `__not_in_flash_func` running timing-critical code from SRAM; memory contention multiple bus masters competing for SRAM assign critical data to dedicated SRAM banks via RP2040's 4 ARM bus ports; interrupt preemption disable interrupts via `critical_section` around tight loops; DMA stealing cycles configure DMA priorities). **GPIO drive strength and slew rate**: RP2040 configurable drive strength 2/4/8/12 mA — use 12 mA for Z80 bus via `gpio_set_drive_strength(pin, GPIO_DRIVE_STRENGTH_12MA)`; slew rate control slow (default limits edge rate reduces EMI for low-speed signals) or fast (full-edge rate for high-speed signals) via `gpio_set_slew_rate(pin, GPIO_SLEW_RATE_FAST)`. STM32 GPIO speeds low ~2 MHz / medium ~12.5 / high ~50 / very high ~100 MHz — high sufficient for Z80, very high adds EMI without benefit. Toggle rate calculations (RP2040 direct software `gpio_put()` ~6 cycles per toggle ~22 MHz; PIO-driven one instruction per toggle ~66 MHz at 133 MHz; DMA-driven via SIO similar to PIO; Z80's fastest signal is clock 3.5 MHz or 7 MHz on 128K/+2/+3 — even software GPIO fast enough for Z80 clock but response time signal-in→signal-out is what matters for bus cycles not toggle rate). Bus capacitance (long bus trace ribbon cable from expansion port to external MCU board adds 10-30 pF per signal + destination pin capacitance ~50 pF total; weak GPIO drive causes slow edges with RC time constant stretching transitions causing setup/hold violations, fast edges on long traces reflect back causing ringing and overshoot dampened with 22-33Ω series termination resistor at source; for long buses use 74HCT245 buffers near MCU to provide strong drive feeding the long bus). **Software design patterns**: state machines per subsystem (kb_state_t enum like IDLE/WAIT_START/READ_DATA/CHECK_PARITY/PROCESS_SCANCODE + step function called periodically processing inputs/outputs/state transitions — avoids blocking each call returns quickly allowing scheduler to run other state machines, scales to dozens of subsystems). Cooperative scheduler (task_t struct with fn/ctx/period_us/last_run_us, scheduler_run loops checking elapsed time calling each task when due — works when tasks complete quickly, long-running tasks like SD card read broken into state machines that yield after few microseconds). Ring buffers for producer-consumer patterns (keyboard scan codes produced by interrupt consumed by main loop) — power-of-2 size allowing `& (SIZE-1)` instead of `% SIZE` faster, head index written by producer ISR, tail index read by consumer main loop, `volatile` qualifiers preventing compiler optimisation, overflow drops byte or increments counter — C code for ring_push/ring_pop. Lock-free SPSC queues (single producer single consumer most common case no mutex needed since single-word reads/writes are atomic on ARM 32-bit aligned, `volatile` prevents stale caching, memory barriers `__dmb()` on ARM ensure visibility across cores for multicore — for multi-producer or multi-consumer use mutex). Double buffering for frame buffers avoiding tearing (front buffer currently displayed, back buffer currently being drawn, swap at vsync atomic pointer assignment, costs 2× memory — alternatives: single buffer with vsync-aware updates tracking CRT beam position updating only part not currently scanned out, triple buffering with one buffer scanned out one finished one being drawn allowing CPU to start next frame without waiting for vsync). Multicore FIFO on RP2040 SIO hardware provides 8-word FIFO per direction faster than shared memory+locks, C code for core1_send_cmd/core0_fifo_isr — 8-word depth shallow so use for commands/acknowledgements not bulk data, bulk data via shared SRAM with lock-free SPSC ring. Interrupt-driven vs polling (video output PIO/DMA never polled real-time; audio output DMA-driven with low-water-mark interrupt for refills; keyboard PS/2 interrupt-driven on clock falling edge; keyboard matrix scan polled every 1 ms; SD card polled in main loop with DMA for transfers; Z80 bus PIO-driven never polled real-time — rule: if missing event causes visible glitch like video tearing or audio gap use interrupts or PIO/DMA, if missing just delays processing by a frame polling is fine). Priority inversion when using multiple interrupts of different priorities (low-priority ISR holding lock needed by high-priority ISR blocking it — ARM Cortex-M BASEPRI register masks low-priority interrupts while allowing high-priority ones, use `critical_section` from SDK which respects BASEPRI; simplest defence avoid locks in ISRs push to ring buffer set flag exit all heavy processing in main loop). **Pin multiplexing strategies**: RP2040 has 30 GPIOs but full Spectrum needs ~50 pins (16 address + 8 data + 8 Z80 controls MREQ_n/IORQ_n/RD_n/WR_n/M1_n/RFSH_n/INT_n/BUSRQ_n-BUSACK_n + 9-12 video VGA 3-bit RGB + HSYNC + VSYNC or DVI 8 TMDS pairs + 1-2 audio PWM/I2S + 2 PS/2 clock+data + 4 SD SPI CS/SCK/MOSI/MISO + optional UART/LEDs/ADC). Strategies (PIO for video freeing CPU pins; external 74HC373 high address latch reduces address bus from 16 to 9 pins saving 8; SPI port expanders 74HC595 output/74HC165 input via SPI few pins add many with latency only for slow signals; small CPLD or GAL like ATF1504/XC9536 decoding addresses and multiplexing signals offloading glue logic; bigger MCU like STM32 F407 LQFP100 with 82 GPIOs enough for everything directly). Pin assignment constraints from RP2040 alternate function table (SPI fixed pin choices SPI0 GP0-3/GP4-7/GP16-19/GP20-23, UART fixed, I2C fixed, PWM slice/channel pairs more flexible, PIO any pin so video/audio flexible, ADC only GP26-GP29 4 pins). Workflow (assign ADC inputs first most constrained, then SPI/UART/I2C next most constrained, then PIO-driven signals video/audio/PS2 most flexible, then bit-banged GPIOs last). Pin multiplexing trade-offs (time multiplexing share pin between functions at different times tricky error-prone; external multiplexer 74HC4051 analog/74HC151 digital switch pin between functions adds propagation delay; function merging combine signals like one status LED blinking different patterns for different events; simplest solution use bigger MCU or add external latches/shift registers). **Power supply considerations**: voltage rails (5V supplied by host Spectrum +5V rail used for 5V TTL bus; 3.3V derived from 5V via LDO regulator AMS1117/MCP1700/AP2112K used for MCU and peripherals; 1.2V internal to some MCUs RP2040 core regulator generates from 3.3V). Current budget (RP2040 ~30 mA active at 133 MHz; external flash ~10 mA during reads; SD card up to 100 mA during writes peak; 74HCT buffers ~5 mA each; PS/2 keyboard ~100 mA powered from host; HDMI/DVI negligible digital low current; VGA ~50 mA per colour channel at peak white 1V into 75Ω — total ~200-300 mA typical; Spectrum +5V rail supplies ~700 mA issue 2 to ~1.5 A issue 6+ has headroom). Decoupling (100 nF ceramic per VDD pin for high-frequency noise; 10 µF tantalum/electrolytic per board section for bulk smoothing; 1 µF ceramic paired with 100 nF for medium-frequency — without proper decoupling fast switching causes voltage droops resetting/hanging MCU). LDO selection (handle current 300 mA minimum 500 mA-1A safer; low dropout input 5V output 3.3V dropout 1.7V most LDOs handle easily; stable with load capacitance check datasheet for recommended output cap ESR range; AMS1117-3.3 cheap ubiquitous ~1A, MCP1700-3302 low quiescent 250 mA, AP2112K-3.3 SOT-23 600 mA). Backpowering common pitfall (MCU's GPIOs driven high while MCU unpowered during power-up sequencing causes current through ESD diodes into VDD backpowering MCU and potentially entire 3.3V rail — effects erratic startup undefined state, latch-up parasitic thyristors conducting shorting VDD to ground, damage if sustained; defences sequence power supplies apply 3.3V before GPIO can be driven, series resistors limit current into driven pins, bus switches 74CB3Q3257 disconnect pins during power-up). **Common pitfalls and how to avoid them** (1. Using 74HC instead of 74HCT — HC requires VIH=3.5V at 5V VDD but 3.3V MCU outputs only 3.3V below threshold randomly reads as low, always use 74HCT for 3.3V→5V translation; 2. Forgetting pull-ups on open-drain signals `INT_n`/`BUSRQ_n`/`NMI_n`/`WAIT_n` quasi-bidirectional on original Z80 without pull-ups ~10K to VDD they float at undefined levels; 3. Driving data bus during write cycle causing bus contention both devices fight high currents voltage glitches potential damage — only drive data bus when `RD_n` low and address matches decode, use 74HCT245 with `OE_n` tied to `IORQ_n OR RD_n OR address_decode`; 4. Missing wait states — some MCUs too slow to respond within Z80 bus cycle, Z80's `WAIT_n` input extends cycle but excessive >~10 cycles confuses some software, use PIO/DMA for cycle-precise response avoiding WAIT_n; 5. Power sequencing issues powering 5V bus before MCU ready causes backpowering, powering MCU before 5V bus stable causes garbage reads, use MCP100 POR supervisor holding MCU in reset until both supplies stable; 6. Inadequate ground return high-speed signals need low-inductance ground return path long thin ground wire single ground pin in ribbon cable creates voltage drop appearing as noise on signals — use multiple ground pins every 8th pin of ribbon cable or solid ground plane on PCB; 7. Floating inputs unconnected input floats at undefined voltage causing input buffer to consume excess current and oscillate — configure all unused GPIOs as outputs driven low or inputs with pull-ups/pull-downs never leave inputs floating). FAQ (level shifter for entire Z80 bus at once — no bidirectional TXB0108 too slow for nanosecond bus timing use dedicated 74HCT245 per bus group one for data two for address; 12 mA drive strength really needed for short traces <5 cm 4 mA sufficient for longer buses ribbon cables expansion port to external board 12 mA plus series termination safer; debug timing issues with logic analyser Saleae/Sigrok-compatible sample bus at 50+ MHz check setup/hold against Z80 datasheet plus oscilloscope for analog characteristics overshoot/ringing that logic analyser misses; adapter works with some Spectrums not others due to issue versions 2/3/4/5/6 having different bus timings buffer strengths pull-up values test on multiple Spectrums common issue is bus timing margin insufficient on faster issue 6 boards; single 74HCT245 for both read and write data bus yes standard design tie `OE_n` to `address_decode AND (RD_n OR WR_n)` and `DIR` to `RD_n` when neither read nor write buffer high-impedance; handle Z80 refresh cycles during `RFSH_n` active every opcode fetch Z80 refreshing dynamic RAM MCU should ignore bus activity `IORQ_n`/`MREQ_n` may pulse but not real accesses add `RFSH_n` to address decode logic; adapter fails when Spectrum reset due to bus undefined for several milliseconds MCU tries responding to garbage addresses add 100 ms reset timeout before enabling bus interface; software bit-banging instead of PIO for Z80 bus probably not software bit-bang on 133 MHz RP2040 ~6 cycles per GPIO operation 4-6 operations per bus response ~30-40 cycles ~250 ns close to Z80 budget PIO faster deterministic). Summary (8 patterns: bus interfacing choose memory-mapped/port/DMA/slave-or-master based on application; level shifting 74HCT not 74HC buffers with proper power sequencing; timing-critical I/O via PIO/DMA with jitter management flash cache/SRAM banks/interrupts/DMA priorities; GPIO configuration 12 mA drive fast slew rate pull-ups on open-drain; software architecture state machines/cooperative scheduler/ring buffers/double buffering/lock-free SPSC queues/multicore FIFO; pin multiplexing external latches/shift registers/CPLD or bigger MCU; power supply multiple rails/adequate current/decoupling/sequenced power-on; avoid pitfalls HCT-not-HC pull-ups bus contention wait states reset timeout ground return floating inputs). References (Zilog Z84C00 Z80 CPU datasheet for bus timing specifications and setup/hold times and output drive capabilities, RP2040 datasheet for PIO architecture/GPIO drive strength/slew rate/DMA channels/SIO multicore FIFO, Pico C/C++ SDK for gpio_set_drive_strength/critical_section/multicore_fifo functions/__not_in_flash_func, 74HCT245/541/244/273/373 datasheets from Texas Instruments/Nexperia/ST for TTL-compatible thresholds and bidirectional transceivers, TXB0108/TXS0108E/SN74LVC1T45 datasheets from TI for dedicated level translators for serial buses, ARM Cortex-M0+ Generic User Guide for interrupt latency/BASEPRI/NVIC priorities, Jack Ganssle's A Guide to Debouncing for practical input handling, Eli Hughes's embedded systems talks for patterns for real-time firmware on ARM Cortex-M, Chris Smith's The ZX Spectrum ULA for bus timing details/contention pattern/refresh cycles, Retro-computing community wikis SpecNext/ZX-Uno/MiSTer/Harlequin all apply these patterns, SparkFun and Adafruit level shifting tutorials for beginner-friendly 3.3V/5V interfacing explanations). Cross-references |

---

## 4. Writing Priority

Articles are written in priority order. README.md is synthesized AFTER articles exist.

**Section completion summary** (Jul 2026):

| Section | Articles done | Status |
|---|---|---|
| 01 CPU | 10/10 | ✅ Complete |
| 03_io/snapshots | 5/5 | ✅ Complete |
| 03_io/storage | 22/22 | ✅ Complete (tape + floppy + HDD/SD) |
| 03_io/peripherals | ~20/20 | ✅ Complete (input + expansion + output + sound cards) |
| 04 OS | 16/16 | ✅ Complete |
| 05_dev/03_memory_and_io | 9/9 | ✅ Complete |
| 06 Sound (synthesis/hardware/trackers/players) | 33+2 | ✅ Complete |
| 07 Demoscene | 11/11 | ✅ Complete |
| 05_dev/05_display_and_timing | **19/19** | ✅ **Complete** (Tier A finished Jul 2026) |
| 11 Emulation | **20/20** | ✅ **COMPLETE** (Jul 2026) — 6 software + 6 FPGA + 9 MCU; AGENTS.md compliance pass committed `6f324b8` |
| 03_io/networking | 6/6 | ✅ **COMPLETE** (Jul 2026) — zx_net, modems, spectranet, zifi, esp_wifi, zx_next_wifi all done |
| 09 Toolchain | **27/27** | ✅ **Complete** (Jul 2026) — 8 surveys/overviews + 19 per-tool deep dives (native + cross-platform + IDEs). All planned articles done across F4 batches 1–4; `zxdstudio.md` descoped (actually ZX Disk Studio Russian disk utility, not an IDE). |
| 08 Reverse Engineering | **7/7** | ✅ **F5 COMPLETE** — consolidated from 10 planned into **7 comprehensive articles** (3,256 lines total): methodology.md (528), protection_techniques.md (492) [both pre-existing], analysis_techniques.md (597), protection_cracking.md (367), game_reversing.md (384), code_crunching.md (432), snapshot_repair.md (456). Merges: static_analysis+dynamic_analysis+tool_setup → analysis_techniques; speedlock_alkatraz → protection_cracking; decompilation → game_reversing |
| 10 References | **10/10** | ✅ **COMPLETE** (Jul 2026) — z80_opcode_table, io_port_map, character_set, color_palette, memory_maps, basic_token_table, error_codes, timing_reference, pinouts, rom_routines |
| 02 Hardware (all 3 streams) | 26/~28 | ✅ **F1/F2/F3 Largely DONE** — original 8/8 (16K/48K, 128K, +2, +2A/+3, ULA architecture/timing/contention, keyboard), clones 11/11 (Pentagon, Scorpion, ATM Turbo, Kay, Profi, Byte, Sizif/Harlequin, + others), newgen 7/8 (Next, Sprinter, Evo, TS-Conf, BaseConf, ZX Uno, Karabas). Descoped: power_supply, edge_connector, rom_contents (pure hardware, duplicative) |
| 05_dev/04_interrupts | 1/~7 | 📝 interrupt_programming done; 6 more pending (im1_programming, im2_programming, isr_patterns, interrupt_timing, race_the_beam, nmi, interrupt_antipatterns, interrupt_cookbook) |
| 05_dev/01_basic | 2/2 | ✅ F7 COMPLETE — consolidated to 2 comprehensive articles: basic_48k.md (1019 lines, merges intro/graphics/sound/peek_poke) + basic_128k.md (496 lines, PLAY/AY-3-8912/+2A+3 DOS). User feedback: "one for 48K comprehensive, one addon for 128K" |
| 05_dev/02_assembly | 6/6 | ✅ **F7 COMPLETE** — consolidated from 10 planned articles into **6 comprehensive articles** (5,762 lines total): assembly_intro.md (705), rom_calls.md (1056), stack_and_rst.md (808), assembly_patterns.md (1016), assembly_optimization.md (860), c_interop.md (1311). Merges: rom_calls_128k → rom_calls; c_with_z88dk + c_with_sdcc + mixed_c_asm → c_interop. User feedback: "Good article should have 500+ lines, combine thin ones" |
| 05_dev/06_graphics | 0/~26 | 📝 Empty (only README) |
| 05_dev/08_dos_tape | 5/5 | ✅ **F8 COMPLETE** — consolidated from 11 planned into **5 comprehensive articles** (4,147 lines total): tape_programming.md (704), trdos_programming.md (817), dos_programming.md (700), file_format_handling.md (1107), mass_storage_programming.md (819). User feedback: "combine thin ones" applied consistently |
| 05_dev/09_gamedev | 0/9 | 📝 Empty (only README) |
| 00 Overview | 0/4 | 📝 Empty (only README) — history, hardware_models, timeline, glossary |

**Active writing tiers** (priority order):

- **Tier A** ✅ **DONE** (Jul 2026): `05_display_and_timing` — all 19 articles complete
- **Tier B** ✅ **DONE** (Jul 2026): `02_hardware/original/zx_spectrum_16k_48k.md` and `02_hardware/clones/pentagon.md`
- **Tier C** ✅ **DONE** (Jul 2026): `08_reverse_engineering/methodology.md`, `09_toolchain/zeus_assembler.md`, `09_toolchain/devpac_gens_mons.md`, `09_toolchain/alasm_sts.md`, `09_toolchain/xas_assembler.md`
- **Tier D** ✅ **DONE** (Jul 2026): `10_references/character_set.md`, `10_references/color_palette.md`, `10_references/z80_opcode_table.md`, `10_references/io_port_map.md` (4 of 10 reference articles done)
- **Tier E** ✅ **DONE** (Jul 2026): `03_io/networking/` (6/6) + `11_emulation/` (20/20 — 6 software + 6 FPGA + 9 MCU). AGENTS.md compliance pass landed in commit `6f324b8` (American English, `#FE` hex prose convention, broken xrefs fixed, README indexes updated)
- **Tier F** (in progress → F4 + F6 ✅ DONE, Jul 2026): user selected F4 (References) as primary, F6 (Toolchain) as second. **F4 ✅ DONE** — all 6 remaining reference articles written in small incremental chunks. **F6 ✅ DONE** — all 19 per-tool deep dives + 8 survey articles written across batches 1–4 (commit `fe874f8`). `zxdstudio.md` descoped after research showed it is the Russian ZX Disk Studio disk-image utility, not a development IDE.

**Tier F candidate bundles** (each scoped to ~6–12 articles, similar effort to Tier E):

- **F1 — 02 Hardware Original (4 articles)**: `zx_spectrum_128.md`, `zx_spectrum_plus2.md`, `zx_spectrum_plus2a_plus3.md`, `ula_contention.md`. Closes out the Original Sinclair/Amstrad hardware story from 16K/48K through +3, focused on architecture/software-development-relevant content. `power_supply.md`, `edge_connector.md`, and `rom_contents.md` originally planned but descoped (pure hardware or duplicative of existing ROM coverage).
- **F2 — 02 Hardware Clones (7 articles)**: `pentagon_1024.md`, `kay.md`, `profi.md`, `byte.md`, `other_clones.md`, `ula_replacements.md`, `sizif_harlequin.md`. Closes out the Soviet clone track. Pentagon + Scorpion + ATM Turbo already done.
- **F3 — 02 Hardware New Gen (7 articles)**: the entire modern-hardware track. `zx_next.md` (merged with sprites/layer2/tilemap/copper/dma/joystick subsystem articles), `sprinter.md`, `zx_evo.md`, `ts_conf.md`, `baseconf.md`, `zx_uno.md`, `karabas.md` (merged with Karabas 128 + Peridot). Largest bundle — modern scene relevance.
- **F4 — 10 References (6 articles)**: `memory_maps.md`, `basic_token_table.md`, `rom_routines.md`, `error_codes.md`, `timing_reference.md`, `pinouts.md`. Quick wins — lookup-table format, referenced everywhere. Closes out the References section.
- **F5 — 08 Reverse Engineering (7 articles)**: `speedlock_alkatraz.md`, `game_reversing.md`, `code_crunching.md`, `tool_setup.md`, `static_analysis.md`, `dynamic_analysis.md`, `snapshot_repair.md` (optionally `decompilation.md`). Closes out the RE section.
- **F6 — 09 Toolchain gap fill** ✅ **DONE** (Jul 2026): 19 per-tool deep dives delivered in 4 batches (batch 1: pasmo, z88dk_z80asm, vasm, wla_dx, zmac, rasm, tniasm; batch 2: tasm_cross, as_macro_assembler, zasm_kio, spectrum_basic_mcode, zx_spin; batch 3: tasm_native, zxasm_native, pikasm, laser_genius, avras, sarcasm; batch 4: zdevstudio). `zxdstudio.md` descoped (Russian ZX Disk Studio disk-image utility, not an IDE — documented in [09_toolchain/README.md](09_toolchain/README.md)).
- **Tier F7 — Sinclair BASIC series** ✅ **COMPLETE** (Jul 2026): Consolidated from 9 planned articles into **2 comprehensive articles**: `basic_48k.md` (1019 lines — merges intro/graphics/sound/peek_poke into a single reference covering tokens, variables, floating-point, calculator stack, parser, PLOT/DRAW/CIRCLE/POINT/ATTR, BEEP, PEEK/POKE/USR) and `basic_128k.md` (496 lines — full-screen editor, boot menu, PLAY mini-language in depth, AY-3-8912 register access from BASIC, +2A/+3 DOS commands, token table differences, RAM disk). User feedback: "don't need many articles about basic — one for 48K comprehensive, one addon for 128K".
- **Tier F7 — Z80 Assembly series** ✅ **COMPLETE** (Jul 2026): Consolidated from 10 planned articles into **6 comprehensive articles** (5,762 lines total): `assembly_intro.md` (705 — first program, toolchain, memory map, Hello World, building, debugging), `rom_calls.md` (1056 — ROM entry points, save/restore state, cookbook for output/keyboard/screen/math/sound, 128K PLAY, AY-3-8912, macros, when NOT to use ROM), `stack_and_rst.md` (808 — stack mechanics, balanced stack rule, RST vectors, calling conventions, shadow registers, computed calls, ERR_SP try/catch, recursion), `assembly_patterns.md` (1016 — state machines, dispatch tables, table-driven code, function pointer tables, coroutines, SMC, macros, modular files, 128K banking), `assembly_optimization.md` (860 — optimization workflow, T-state budgeting, hot-loop techniques, lookup tables, fast multiply/divide, SMC, contention, 10-recipe cookbook), `c_interop.md` (1311 — sccz80 vs zsdcc, calling conventions in depth, C-calls-asm + asm-calls-C, inline assembly, shared globals, project structure, zcc pipeline, performance patterns, library interop, worked multi-file project). User feedback: "do extensive research, create outlines first, combine thin articles".
- **F7 (long-form, remaining)**: `05_development/06_graphics/screen_access.md` + 25 more (Graphics series). Long arc — next subsection to seed.
- **Tier F8 — DOS and Tape Programming series** ✅ **COMPLETE** (Jul 2026): Consolidated from 11 planned articles into **5 comprehensive articles** (4,147 lines total): `tape_programming.md` (704 — ROM SA-BYTES/LD-BLOCK/SAVE/LOAD, custom bit-banging loaders via port #FE, turbo loaders 3000+ baud, custom savers, border effects), `trdos_programming.md` (817 — TR-DOS ROM banking via port #FF, 9 hook codes at #3D13, file operations, catalog reader, WD1793 sector I/O, demoscene double-buffered streaming), `dos_programming.md` (700 — +3 DOS RSX, ESXDOS hook codes at #0084, NextZXOS, dot commands at #2000, API comparison matrix, portable code, runtime DOS detection), `file_format_handling.md` (1107 — magic-byte detection, .TAP/.TZX/.TRD/.SCL/.DSK/.SNA/.Z80/.SCR parsing, directory traversal, .Z80 RLE decompression), `mass_storage_programming.md` (819 — IDE/CF ATA register access, SD card SPI bit-banging, read-only FAT16/32 reader, performance vs OS-mediated). Cross-verified against 25 existing storage reference articles and 4 OS reference articles to avoid duplication.
- **Tier F5 — Reverse Engineering series** ✅ **COMPLETE** (Jul 2026): Consolidated from 10 planned articles into **7 comprehensive articles** (3,256 lines total): 2 pre-existing (`methodology.md` 528 — RE workflow hub, `protection_techniques.md` 492 — protection catalog) + 5 new: `analysis_techniques.md` (597 — SkoolKit disassembly, code/data separation, ROM call labeling, ZEsarUX/DeZog debugging, trace logging, reverse debugging, memory diffing), `protection_cracking.md` (367 — Speedlock/Alkatraz decryption analysis, timing check bypass, disk protection defeat, NMI countermeasure defeat, clean snapshot technique), `game_reversing.md` (384 — engine identification, sprite/map/music ripping, cheat codes, save game analysis, Z80-to-C reconstruction), `code_crunching.md` (432 — packer survey MegaLZ/HRUM/Hrust/ZX0, format identification, LZSS fundamentals, generic depacker template, overlap depacking), `snapshot_repair.md` (456 — corrupted .SNA/.Z80 repair, PC/SP fix, .Z80 decompression error handling, format conversion with Python scripts). Consolidation merges: static_analysis+dynamic_analysis+tool_setup → analysis_techniques; speedlock_alkatraz → protection_cracking; decompilation → game_reversing.

After articles exist: README.md (documentation map), TODO.md (gap analysis), section README.md indexes.

---

## 5. Key Platform Characteristics

1. **Three parallel tracks** — Original, Soviet, New Gen — each with dedicated hardware sections
2. **No traditional OS** — 48K has no disk OS; ROM BASIC is the "OS". TR-DOS/+3 DOS are lightweight DOSes, not full operating systems
3. **CPU-driven everything** (original hardware) — no DMA, no blitter, no coprocessors. Every pixel is pushed by the Z80. Makes timing/optimization the central discipline
4. **Massive sound card ecosystem** — from 1-bit beeper to FM synthesis (YM2203/TurboSound FM) to wavetable (MoonSound/OPL4) to dedicated Z80-based sound cards (General Sound)
5. **Soviet clone ecosystem** — Pentagon alone outsold everything; post-Soviet scene is still the most active community
6. **Active New Gen development** — ZX Spectrum Next is living hardware with ongoing software development
7. **Demoscene constraint storytelling** — extreme constraints (3.5 MHz, 8x8 color cells, contended memory) produced extraordinary creative work
8. **MCU chip emulation** — modern trend of replacing vintage silicon with RP2040/ESP32, bridging retro and embedded worlds
9. **Assembly-first development** — C exists (SDCC/z88dk) but is minority; every article must lead with assembly
10. **Port decoding complexity** — partial address decoding varies per model and clone, must be verified against schematics

## 6. Content Policy

- **License**: CC BY-SA 4.0 — covers original writing, not quoted source material
- **No verbatim ROM listings** — articles reference ROM addresses and describe behavior without full dumps. ROM contents are copyrighted (Amstrad/Sinclair). Use address references, disassembly snippets, and behavioral descriptions instead
- **No copyrighted manual excerpts** — describe, don't copy. Link to original sources where possible
