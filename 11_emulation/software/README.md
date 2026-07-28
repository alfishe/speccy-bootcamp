[← Emulation](../README.md) · [Software Emulators](README.md)

# Emulation — Software Emulators

This directory covers software emulators: Fuse, ZEsarUX, CSpect, Spectaculator, Unreal Speccy, cycle-exact accuracy, and test suites.

## Articles

| # | Article | Topic |
|---|---------|-------|
| 1 | [emulator_comparison.md](emulator_comparison.md) | Comprehensive comparison of ZX Spectrum emulators (Fuse, ZEsarUX, CSpect, Spectaculator, UnrealSpeccy, Klive, Speccy/fMSX, JSSpeccy). Categories: cross-platform accuracy-focused, Windows-focused, Next-aware, web-based, mobile, retro-platform, embedded. Detailed strengths/weaknesses for each major emulator. Comparison matrices: platform support, hardware coverage (16K/48K/128K/Pentagon/Scorpion/Next/TSConf), accuracy (cycle-exact, contended memory, audio timing), development tools (disassembler, memory viewer, breakpoints, sprite/tile viewer, RMX), licensing. Selection guide by use case (casual gaming, original hardware development, Next development, reverse engineering, demoscene production, hardware research, mobile, web, embedded). FAQ (best emulator, multiple installs, beating real hardware, free emulators, console bundles, cross-platform). References |
| 2 | [test_suites.md](test_suites.md) | Test suites used to validate ZX Spectrum emulator accuracy: ZEXALL/ZEXDOC (Z80 instruction exerciser by Frank D. Cringle), the FUSE test suite (Z80 instructions, contended memory, INT timing, video timing, audio, peripherals), Pentagon Diag ROM (Russian clone validation), timing-specific tests (Sensible, Float Spell, contended memory loop, INT timing), peripheral tests (AY-3-8912, Kempston, Interface 1 microdrive), diagnostic ROMs (ZX Diag, Ramtest). How to use: for users (download, run, compare) and for emulator authors (CI pipeline, multiple hardware configs, real hardware comparison, publish results). Limitations of testing (unknown edge cases, hardware variability, test bugs, analogue behaviour). FAQ, summary, references |
| 3 | [cycle_exact_accuracy.md](cycle_exact_accuracy.md) | Frame timing divergence, CRT sync mechanism, host sync strategies (DRC, resampling), AY-3-8912 audio clocks, judder mitigation (5 techniques with compute costs), emulator comparison (10 entries), worst-case Pentagon@60Hz conclusion |

See [PLAN.md](../../PLAN.md) for the full article catalog.
