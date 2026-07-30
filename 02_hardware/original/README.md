[← Home](../../README.md) · [Original Hardware](README.md)

# Hardware — Original Sinclair/Amstrad

This directory covers original ZX Spectrum hardware models (16K, 48K, 128K, +2, +2A, +3), ULA architecture, and peripherals.

---

## Articles

| # | Article | Description |
|---|---------|------------|
| 1 | [zx_spectrum_16k_48k.md](zx_spectrum_16k_48k.md) | The canonical Sinclair: history, system architecture, bill of materials (4116 lower RAM, 4532/4164 upper RAM, LM1889 modulator), memory map, ULA revisions, board issues, video/audio/tape/power/edge connector, 16K→48K upgrade path |
| 2 | [ula_timing.md](ula_timing.md) | ULA frame timing per model, memory contention, **snow effect** (RFSH/RAS collision), multicolor effects, early/late timing, performance budget |
| 3 | [ula_architecture.md](ula_architecture.md) | Inside the Ferranti ULA: video pipeline, memory arbitration, #FE register, keyboard matrix, tape/sound cells, revisions, Amstrad gate arrays, clone and modern replacements |
| 4 | [keyboard_matrix.md](keyboard_matrix.md) | The 8×5 keyboard matrix: membrane hardware, half-row scanning, ghosting mechanics, Interface 2/Sinclair/Cursor joystick mappings, game keyset conventions by genre and region, redefinable game input |
| 5 | [zx_spectrum_128.md](zx_spectrum_128.md) | The 128K "Toast Rack": Sinclair's last Spectrum — Spanish origin, board variants, `#7FFD` banking, AY-3-8912, keypad, RS-232/MIDI, per-bank contention, comparison across models |
| 6 | [zx_spectrum_plus2.md](zx_spectrum_plus2.md) | Amstrad +2 "Grey": functionally identical to the 128K (same gate array, same contention) — physical/industrial/keyboard differences, unchanged internals list |
| 7 | [zx_spectrum_plus2a_plus3.md](zx_spectrum_plus2a_plus3.md) | +2A/+3: Amstrad ASIC redesign (40084/40085), MREQ-gated contention on banks 4-7, `#1FFD` paging register, special paging mode, +3 disk subsystem, four-bank ROM |
| 8 | [ula_contention.md](ula_contention.md) | Hardware-perspective on memory contention: DRAM electrical foundation (RAS/CAS, paged mode), why the `(6,5,4,3,2,1,0,0)` pattern exists, per-model comparison (48K/128K/+2/+2A/+3), MREQ gating, emulator/FPGA implications |

> This directory is being populated. The 4-article F1 batch is complete: `zx_spectrum_128.md`, `zx_spectrum_plus2.md`, `zx_spectrum_plus2a_plus3.md`, `ula_contention.md`. (`power_supply.md`, `edge_connector.md`, and `rom_contents.md` were originally planned but descoped — pure hardware or duplicative of existing ROM coverage in [04_operating_systems/](../../04_operating_systems/).) See [PLAN.md](../../PLAN.md) for details.
