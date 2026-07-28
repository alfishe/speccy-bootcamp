[← Home](../README.md) · [Emulation](README.md)

# Emulation

This section covers ZX Spectrum emulation in all its forms: software emulators, FPGA implementations, and MCU-based hardware replacements.

---

## Subdirectories

| Directory | Topic | Status |
|-----------|-------|--------|
| [software/](software/) | Software emulators — Fuse, ZEsarUX, cycle-exact accuracy, test suites | Active |
| [fpga/](fpga/) | FPGA cores — MiSTer, ZX-Uno, Harlequin/Sizif, implementation guides | Placeholder |
| [mcu/](mcu/) | MCU emulation — Z80 on MCU, ULA on MCU, FDC, video adapters | Placeholder |

## Articles

### Software Emulators

| # | Article | Description |
|---|---------|------------|
| 1 | [emulator_comparison.md](software/emulator_comparison.md) | Comprehensive comparison of ZX Spectrum emulators (Fuse, ZEsarUX, CSpect, Spectaculator, UnrealSpeccy, Klive, Speccy/fMSX, JSSpeccy). Categories, detailed strengths/weaknesses, comparison matrices (platform, hardware, accuracy, dev tools, licensing), selection guide by use case, FAQ, references |
| 2 | [test_suites.md](software/test_suites.md) | Test suites for validating emulator accuracy: ZEXALL/ZEXDOC, FUSE test suite, Pentagon Diag ROM, timing-specific tests, peripheral tests, diagnostic ROMs. How to use, limitations |
| 3 | [fuse.md](software/fuse.md) | Deep dive on Fuse (Free Unix Spectrum Emulator) by Philip Kendall (1999+): modular architecture, libspectrum, full Sinclair + Russian/Brazilian/Spanish clones, debugger, RMX recording, derivative projects (JSSpeccy, Android, SDL) |
| 4 | [cycle_exact_accuracy.md](software/cycle_exact_accuracy.md) | Frame timing divergence, CRT sync mechanism, host sync strategies (DRC, resampling), AY-3-8912 audio clocks, judder mitigation (5 techniques with compute costs), emulator comparison (10 entries), worst-case Pentagon@60Hz conclusion |

See [PLAN.md](../PLAN.md) for the full article catalog.
