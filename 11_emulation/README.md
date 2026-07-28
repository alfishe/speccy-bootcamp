[← Home](../README.md) · [Emulation](README.md)

# Emulation ✅ COMPLETE (20 articles)

This section covers ZX Spectrum emulation in all its forms: software emulators (6), FPGA cores (6), and MCU-based hardware replacements (9). All subsections are complete.

---

## Subdirectories

| Directory | Topic | Status |
|-----------|-------|--------|
| [software/](software/) | Software emulators — Fuse, ZEsarUX, CSpect, cycle-exact accuracy, test suites, emulator comparison | ✅ COMPLETE (6/6) |
| [fpga/](fpga/) | FPGA cores — MiST/MiSTer, ZX-Uno, Harlequin/Sizif, ZX Evolution, FPGA implementation and timing | ✅ COMPLETE (6/6) |
| [mcu/](mcu/) | MCU chip replacement — Z80, ULA, FDC, PSG, keyboard, video, SD on MCU; N-Go synthesis; design patterns | ✅ COMPLETE (9/9) |

## Articles

### Software Emulators

| # | Article | Description |
|---|---------|------------|
| 1 | [emulator_comparison.md](software/emulator_comparison.md) | Comprehensive comparison of ZX Spectrum emulators (Fuse, ZEsarUX, CSpect, Spectaculator, UnrealSpeccy, Klive, Speccy/fMSX, JSSpeccy). Categories, detailed strengths/weaknesses, comparison matrices (platform, hardware, accuracy, dev tools, licensing), selection guide by use case, FAQ, references |
| 2 | [test_suites.md](software/test_suites.md) | Test suites for validating emulator accuracy: ZEXALL/ZEXDOC, FUSE test suite, Pentagon Diag ROM, timing-specific tests, peripheral tests, diagnostic ROMs. How to use, limitations |
| 3 | [fuse.md](software/fuse.md) | Deep dive on Fuse (Free Unix Spectrum Emulator) by Philip Kendall (1999+): modular architecture, libspectrum, full Sinclair + Russian/Brazilian/Spanish clones, debugger, RMX recording, derivative projects (JSSpeccy, Android, SDL) |
| 4 | [zesarux.md](software/zesarux.md) | Deep dive on ZEsarUX by Cesar Hernandez Nuñez (2013+): broadest hardware coverage (Sinclair + Spanish/Russian/modern clones), reverse engineering workstation (reverse debugging, real-time assembly editing, conditional breakpoints), ZX Spectrum Next support |
| 5 | [cspect.md](software/cspect.md) | Deep dive on CSpect by Mike Dailly (2017+): de facto reference emulator for the ZX Spectrum Next, comprehensive Next hardware coverage (Z80N, layer 2, hardware sprites, tilemap, copper, DMA, DivMMC, 4 MB RAM, ESP-12 partial), multi-pane debugger with NEXTREG inspection and live Layer 2/Sprites/Tilemap views, `.nex` file loader, TCP remote debugging protocol |
| 6 | [cycle_exact_accuracy.md](software/cycle_exact_accuracy.md) | Frame timing divergence, CRT sync mechanism, host sync strategies (DRC, resampling), AY-3-8912 audio clocks, judder mitigation (5 techniques with compute costs), emulator comparison (10 entries), worst-case Pentagon@60Hz conclusion |

### FPGA Cores

| # | Article | Description |
|---|---------|------------|
| 1 | [fpga_implementation.md](fpga/fpga_implementation.md) | Why FPGA differs from software emulation, gate-level reconstruction, vendor families (Altera/Intel, Xilinx, Lattice, Gowin), FPGA design flow, when FPGA is the right choice |
| 2 | [fpga_timing_accuracy.md](fpga/fpga_timing_accuracy.md) | Cycle-true timing in FPGA cores: ULA contention replication, video frame timing, audio clock matching, sub-ns precision, testing methodology |
| 3 | [harlequin_sizif.md](fpga/harlequin_sizif.md) | Maxim Sichkov's Harlequin (2007+) and SIZIF series — gate-level ULA replacements for original Spectrum motherboards, repair-and-upgrade boards, multiple revisions |
| 4 | [zxevo.md](fpga/zxevo.md) | ZX Evolution — TS-Conf/Baseconf FPGA platform, ATM Turbo spiritual successor, Pentagon-compatible, configurable video modes, IDE/SD |
| 5 | [zx_uno_core.md](fpga/zx_uno_core.md) | ZX-Uno — compact FPGA board, all-Spectrum-on-one-board, multi-core (Pentagon/Scorpion/48K/128K), WiFi and SD built-in, community-developed |
| 6 | [mist_mister_core.md](fpga/mist_mister_core.md) | MiST & MiSTer Spectrum cores — accurate and extensible, alongside dozens of other retro computers on the MiSTer FPGA platform |

### MCU Chip Replacement

| # | Article | Description |
|---|---------|------------|
| 1 | [mcu_z80.md](mcu/mcu_z80.md) | Z80 on MCU — bit-banged and PIO-driven cycle-true Z80 emulation in firmware, libz80/z80ex cycle engines, drop-in chip replacement |
| 2 | [mcu_ula.md](mcu/mcu_ula.md) | ULA on MCU — RP2040 PIO reconstruction of the Ferranti ULA, contention timing, video pipeline, floating bus behavior |
| 3 | [mcu_fdc_vg93.md](mcu/mcu_fdc_vg93.md) | WD1793/VG93 on MCU — bit-banged floppy controller replacement, MFM decoding in firmware, SD-card image backing |
| 4 | [mcu_psg_ay.md](mcu/mcu_psg_ay.md) | AY-3-8910/YM2149 on MCU — software PSG synthesis, RP2040 PWM/DMA audio, drop-in pin-compatible replacements |
| 5 | [mcu_keyboard.md](mcu/mcu_keyboard.md) | Keyboard on MCU — PS/2 keyboard matrix scanning, scan-code translation, 8×5 Spectrum matrix emulation, debounce |
| 6 | [mcu_video_adapter.md](mcu/mcu_video_adapter.md) | Video adapter on MCU — RGB/HDMI output from RP2040 PIO, scanline generation, multicolor effects, layer-2 style overlays |
| 7 | [mcu_sd_interface.md](mcu/mcu_sd_interface.md) | SD card interface on MCU — SPI/SDIO from MCU, file-backed disk images, DivMMC/DivIDE emulation on a single MCU |
| 8 | [n_go.md](mcu/n_go.md) | N-Go — complete Spectrum on MCU — synthesis article, RP2040 multicore architecture (Z80 core + ULA + PSG + SD), firmware structure |
| 9 | [mcu_design_patterns.md](mcu/mcu_design_patterns.md) | MCU design patterns — bus interfacing (memory-mapped/port/IO/DMA), 74HCT vs 74HC level shifting, RP2040 PIO timing-critical I/O, GPIO drive, ring buffers, lock-free SPSC queues, common pitfalls |

See [PLAN.md](../PLAN.md) for the full article catalog.
