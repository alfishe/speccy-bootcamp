[← Emulation](../README.md) · [FPGA Cores](README.md)

# Emulation — FPGA Cores

This directory covers **FPGA-based** Spectrum implementations — synthesised hardware re-implementations of the ZX Spectrum in programmable logic. Unlike software emulators, FPGA cores reconstruct the original hardware at the gate level, providing cycle-exact timing and authentic video/audio output.

For software emulators, see the [software](../software/) directory. For MCU-based emulation, see the [mcu](../mcu/) directory.

| # | Article | Description |
|---|---------|------------|
| 1 | [mist_mister_core.md](mist_mister_core.md) | Deep dive on the **MiST / MiSTer** ZX Spectrum cores on the DE10-Nano FPGA platform (Cyclone V SoC, 85K LEs, ARM HPS). History: MiST (2011, Till Harbaum, Altera Cyclone I, 20K LEs) → MiSTer (2017, Alexey Melnikov, DE10-Nano). Why FPGA beats software for authenticity. Hardware coverage: full Sinclair range (16K/48K/128K/+2/+2A/+3), Russian clones (Pentagon 128/512/1024, Scorpion 256/1024, ATM Turbo), Spanish/Brazilian clones (TK90X/TK95, Inves). Peripherals: AY-3-8912, Beta 128, +3 FDC, DivMMC, Interface 1, Currah µSpeech, Multiface, Kempston/Sinclair joysticks. Architecture: T80 cycle-exact Z80 in Verilog, ULA module with memory contention and floating bus, AY-3-8912 at original clock rate, modular peripheral modules. Video output: HDMI, Analogue VGA, Composite/S-Video (with pixel-perfect 4-CPU-cycle pixel timing). OSD configuration (F12), machine/peripheral/video/audio settings, save states. MiSTer vs real hardware vs software emulators decision matrix. FAQ, summary, references, cross-references |
| 2 | [zx_uno_core.md](zx_uno_core.md) | Coming soon: ZX-Uno FPGA platform for the Spectrum |
| 3 | [zxevo.md](zxevo.md) | Coming soon: ZX Evolution — Russian FPGA Spectrum based on Pentagons |
| 4 | [harlequin_sizif.md](harlequin_sizif.md) | Coming soon: Harlequin and Sizif — modern FPGA Spectrums in original form factor |
| 5 | [fpga_implementation.md](fpga_implementation.md) | Coming soon: How Spectrum FPGA cores are designed (T80 CPU, ULA module, peripheral modules, test bench) |
| 6 | [fpga_timing_accuracy.md](fpga_timing_accuracy.md) | Coming soon: Cycle-exact timing in FPGA cores, comparison with software emulator accuracy |

See [PLAN.md](../../PLAN.md) for the full article catalog.
