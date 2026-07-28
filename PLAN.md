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
│   │   ├── power_supply.md
│   │   ├── rom_contents.md
│   │   ├── keyboard_matrix.md
│   │   └── edge_connector.md
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
│       ├── zx_next_sprites.md
│       ├── zx_next_layer2.md
│       ├── zx_next_tilemap.md
│       ├── zx_next_copper.md
│       ├── zx_next_dma.md
│       ├── sprinter.md
│       ├── zx_evo.md
│       ├── ts_conf.md
│       ├── baseconf.md
│       ├── zx_uno.md
│       ├── karabas_pro.md
│       ├── karabas_128.md
│       └── peridot.md
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
│   │   ├── tape_loading.md
│   │   ├── tape_saving.md
│   │   ├── trdos_programming.md
│   │   ├── trdos_disk_operations.md
│   │   ├── plus3dos_programming.md
│   │   ├── esxdos_programming.md
│   │   ├── nextzxos_programming.md
│   │   ├── file_format_handling.md
│   │   ├── ide_hdd_programming.md
│   │   └── fat_filesystem.md
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
│   ├── protection_techniques.md ✅
│   ├── methodology.md
│   ├── speedlock_alkatraz.md
│   ├── game_reversing.md
│   ├── code_crunching.md
│   ├── tool_setup.md
│   ├── static_analysis.md
│   ├── dynamic_analysis.md
│   ├── snapshot_repair.md
│   └── decompilation.md
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
    │   ├── zesarux.md
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
| `zx_spectrum_128.md` | 128K toastrack: AY-3-8912, RS-232, keypad port, RAM paging (16K banks), ROM switching | Planned |
| `zx_spectrum_plus2.md` | Amstrad +2 (grey): integrated keyboard, built-in tape, AY sound | Planned |
| `zx_spectrum_plus2a_plus3.md` | +2A/+3: Amstrad gate array, +3 DOS, internal floppy, RAM banking differences | Planned |
| `ula_architecture.md` | Ferranti ULA internals: video generation, memory arbitration, contention timing, CPU/ULA cycle interleaving | ✅ |
| `ula_contention.md` | Memory contention deep dive: when CPU is stalled, precise timing diagrams per model, impact on cycle-counted code | Planned |
| `ula_timing.md` | ULA frame timing per model (48K/128K/+2A), memory contention (Ferranti 6-5-4-3-2-1-0-0, Amstrad gate array 1-0-7-6-5-4-3-2), contended I/O, multicolor effects, early/late timing drift, performance budget, screen update timing | ✅ |
| `power_supply.md` | PSU design: 9V unregulated, internal regulation, edge connector power pins | Planned |
| `rom_contents.md` | ROM dissection: channel system, editor, BASIC interpreter, character set | Planned |
| `keyboard_matrix.md` | 8x5 matrix, key codes, keyboard reading routine, BEEP key detection | ✅ |
| `edge_connector.md` | Edge connector pinout, bus signals, expansion bus usage | Planned |

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
| `zx_next.md` | ZX Spectrum Next: layer architecture, 28MHz accelerator, sprites, layer 2, tilemap, copper, DMA, SD, WiFi, RTC, ESP | Planned |
| `zx_next_sprites.md` | Next sprite system: 128 sprites, patterns, rotation, priority, collision | Planned |
| `zx_next_layer2.md` | Layer 2 (256-color) and 256x192x8bpp mode | Planned |
| `zx_next_tilemap.md` | Tilemap engine, hardware scrolling, 40x32 tile grid | Planned |
| `zx_next_copper.md` | Next copper: WAIT + MOVE instructions, synced to raster | Planned |
| `zx_next_dma.md` | DMA controller (derived from Z80 DMA): memory copy, pattern fill, port I/O | Planned |
| `zx_next_joystick.md` | Next joystick / input subsystem | ✅ (off-plan) |
| `sprinter.md` | Peters Plus Sprinter: 20MHz Z80, 1MB RAM, SVGA, IDE, PC-like architecture | Planned |
| `zx_evo.md` | ZX Evolution: Z80-based with CPLD glue logic, PS/2 keyboard/mouse, IDE, SVGA — real hardware, not FPGA core recreation | Planned |
| `ts_conf.md` | TS-Conf: FPGA ZX Spectrum config for ZX Evo — sprites, tiles, 512K VRAM, turbo modes | Planned |
| `baseconf.md` | Baseconf: standard ZX Evo configuration, classic Spectrum compatibility | Planned |
| `zx_uno.md` | ZX-Uno: FPGA-based, ULAplus, Turbo, AY, SPI, WiFi | Planned |
| `karabas_pro.md` | Karabas Pro: modern Z80-based hardware with CPLD, compact design, Peridot-compatible | Planned |
| `karabas_128.md` | Karabas 128: modern compact Spectrum-compatible, real Z80 + CPLD glue | Planned |
| `peridot.md` | Peridot: expandable modern Spectrum platform, Karabas-compatible expansion bus | Planned |

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

#### 05_development/08_dos_tape/ — DOS and Tape Interaction

| File | Topic |
|---|---|
| `README.md` | Index — file I/O from assembly: tape, TR-DOS, +3 DOS, ESXDOS, NextZXOS |
| `tape_loading.md` | Tape loading from assembly: ROM LOAD, custom loaders, turbo loaders, tape format generation |
| `tape_saving.md` | Tape saving: ROM SAVE, header construction, data block writing, baud rate control |
| `trdos_programming.md` | TR-DOS programming: hook codes, file operations (OPEN/CLOSE/READ/WRITE), directory access, direct sector I/O |
| `trdos_disk_operations.md` | TR-DOS disk operations: format, verify, catalog, file management from assembly |
| `plus3dos_programming.md` | +3 DOS programming: file I/O via +3 DOS calls, Resident System Extensions |
| `esxdos_programming.md` | ESXDOS .dot commands and API: file access on DivIDE/DivMMC, FAT filesystem |
| `nextzxos_programming.md` | NextZXOS API: file operations, SD card access from NextBASIC and assembly |
| `file_format_handling.md` | Common file formats in code: parsing TAP/TZX, loading SNA/Z80 snapshots, reading TRD images |
| `ide_hdd_programming.md` | IDE/HDD programming from assembly: ATA register access, sector read/write on DivIDE/SMUC/Nemo IDE, LBA vs CHS |
| `fat_filesystem.md` | FAT filesystem on Spectrum: reading FAT16/32 from assembly, directory traversal, ESXDOS file API |

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
| `methodology.md` | ZX Spectrum RE workflow: disassembly, tracing, patching | ✅ |
| `protection_techniques.md` ✅ | Copy protection: tape loaders (Speedlock, Alkatraz), disk schemes, NMI/snapshot defenses, snapshot devices, memory integrity, code obfuscation, bypass techniques |
| `game_reversing.md` | Game RE: asset extraction, map ripping, cheat codes, save game formats |
| `code_crunching.md` | Compression: MegaLZ, HRUM, Z80 crunchers, unpacking, depacker analysis |
| `tool_setup.md` | Tool setup: ZEsarUX debugger, Fuse, sjasmplus, binary diff tools |
| `static_analysis.md` | Static analysis: identifying game engines, asset formats, code patterns |
| `dynamic_analysis.md` | Dynamic analysis: breakpoints, watchpoints, trace logging |
| `snapshot_repair.md` | Snapshot repair: fixing corrupted .SNA/.Z80, restoring tape data |
| `decompilation.md` | Decompilation: Z80 → C reconstruction, tool-assisted approaches |

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
| `zesarux.md` | ZEsarUX: advanced debugging, reverse debugging, FPGA simulation, Next support |
| `cspect.md` | CSpect: ZX Spectrum Next emulator, development focus |
| `test_suites.md` | ✅ **Test Suites** — test programs used to validate ZX Spectrum emulator accuracy. ZEXALL/ZEXDOC (Z80 instruction exerciser by Frank D. Cringle, 1997), the FUSE test suite (Z80 instructions, contended memory, INT timing, video timing, audio, peripherals — hosted on SourceForge), Pentagon Diag ROM (Russian clone validation). Timing-specific tests: Sensible tests (Andrew Owen), Float Spell multicolour demo, contended memory loop, INT timing tests. Peripheral tests: AY-3-8912 register/envelope/noise, Kempston joystick at `0x1F`, Interface 1/microdrive. Diagnostic ROMs (ZX Diag, Ramtest). How to use for emulator users (download, run, compare) and authors (CI pipeline, multi-hardware configs, real hardware comparison, publish results). Limitations of testing (unknown edge cases, hardware variability, test bugs, analogue behaviour). FAQ, summary, references |

#### 11_emulation/fpga/ — FPGA Cores

| File | Topic |
|---|---|
| `README.md` | Index — FPGA Spectrum ecosystem |
| `mist_mister_core.md` | MiSTer ZX Spectrum core: features, accuracy, supported models |
| `zx_uno_core.md` | ZX-Uno: FPGA-based Spectrum, ULAplus, Turbo, AY, SPI |
| `zxevo.md` | ZX Evolution: Z80-based hardware with CPLD glue logic (not FPGA core recreation), PS/2 keyboard/mouse, IDE, SVGA, real chips + CPLD address decoding |
| `harlequin_sizif.md` | Harlequin / Sizif-512: faithful ULA recreation in FPGA, timing accuracy |
| `fpga_implementation.md` | FPGA implementation guide: ULA timing in HDL, contention state machines, T-state accuracy |
| `fpga_timing_accuracy.md` | Timing accuracy: scanline-precise vs T-state-precise, common pitfalls, verification methods |

#### 11_emulation/mcu/ — MCU Chip Emulation

| File | Topic |
|---|---|
| `README.md` | Index — MCU-based chip emulation: replacing vintage silicon with modern microcontrollers |
| `mcu_z80.md` | Z80 on MCU: cycle-exact Z80 emulation on RP2040/ESP32/STM32, bus interface design |
| `mcu_ula.md` | ULA on MCU: video generation, contention emulation, RP2040 PIO-based approaches |
| `mcu_fdc_vg93.md` | KR1818VG93 / WD1793 FDC on MCU: replacing the floppy controller with STM32, VG93Em-STM32 project |
| `mcu_psg_ay.md` | AY-3-8912 PSG on MCU: sound chip replacement, register-compatible implementations |
| `mcu_keyboard.md` | Keyboard controller on MCU: ZXHIDKeyboard, PS/2 to ZX matrix conversion |
| `mcu_video_adapter.md` | Video adapters: VGA/HDMI output from RP2040 Pico, scanline generation, upscaling |
| `mcu_sd_interface.md` | SD card interfaces on MCU: replacing floppy with SD, TRDOS compatibility |
| `n_go.md` | N-Go: MCU-based Spectrum implementation |
| `mcu_design_patterns.md` | Design patterns: bus interfacing, level shifting, timing-critical I/O, GPIO speed requirements |

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
| 10 References | 5/10 | 📝 z80_opcode_table.md, character_set.md, color_palette.md done; 7 more pending |
| 09 Toolchain | 11/~30 | 📝 Surveys done; per-tool stubs pending |
| 02 Hardware (all 3 streams) | 9/~40 | 📝 Major gap |
| 03_io/networking | 6/6 | ✅ **COMPLETE** (Jul 2026) — zx_net, modems, spectranet, zifi, esp_wifi, zx_next_wifi all done |
| 08 Reverse Engineering | 1/9 | 📝 Major gap |
| 11 Emulation | 4/~20 | 📝 Tier E in progress (cycle_exact_accuracy, emulator_comparison, test_suites, fuse done; 16 more across software/fpga/mcu pending) |
| 05_dev/01_basic, 02_assembly, 06_graphics | 0/30+ | 📝 Empty |

**Active writing tiers** (priority order):

- **Tier A** ✅ **DONE** (Jul 2026): `05_display_and_timing` — all 19 articles complete (48K, 128K, +2A/+3, Pentagon, Scorpion, other Soviet, Next, Sprinter, ZX Evolution, contention_timing, interlace_and_flicker, crt_output, video_frame_comparison)
- **Tier D** ✅ **DONE** (Jul 2026): `10_references/character_set.md`, `10_references/color_palette.md`, `10_references/z80_opcode_table.md` all complete (3 of 10 planned reference articles; remaining 7 are deferred)
- **Tier B** ✅ **DONE** (Jul 2026): `02_hardware/original/zx_spectrum_16k_48k.md` and `02_hardware/clones/pentagon.md` — both foundational hardware articles complete
- **Tier C** ✅ **DONE** (Jul 2026): `08_reverse_engineering/methodology.md`, `09_toolchain/zeus_assembler.md`, `09_toolchain/devpac_gens_mons.md`, `09_toolchain/alasm_sts.md`, `09_toolchain/xas_assembler.md` — all 5 articles complete
- **Tier E** (in progress, Jul 2026): `03_io/networking/` ✅ **DONE** (6/6 — zx_net, modems, spectranet, zifi, esp_wifi, zx_next_wifi), now starting `11_emulation/` (5 software + 6 FPGA + 9 MCU articles = 20)

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
