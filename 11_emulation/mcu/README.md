[← Emulation](../README.md) · [MCU Emulation](README.md)

# Emulation — MCU Chip Emulation

This directory covers replacing vintage silicon with modern microcontrollers: Z80 on MCU, ULA on MCU, FDC, PSG, keyboard, video adapters, SD interfaces, and design patterns. MCU-based chip emulation is a growing trend in retro-computing — modern MCUs (especially the RP2040 with its PIO blocks) can replace ageing Z80s, ULAs, AY chips, and floppy controllers at lower cost, lower power, and with additional features like in-circuit debugging and tracing.

For FPGA-based chip emulation, see the [fpga](../fpga/) directory. For software emulators running on PCs, see the [software](../software/) directory.

## Articles

| # | File | Topic |
|---|---|---|
| 1 | [mcu_z80.md](mcu_z80.md) | **Z80 on a Microcontroller** — replacing the Z80 CPU with an RP2040/ESP32/STM32. Why MCU (component availability, power consumption, reliability, additional features like debugging/tracing/integrated peripherals, compatibility layer presenting the full Z80 bus interface). Host MCU choices: RP2040 (Raspberry Pi Pico, dual Cortex-M0+ at 133 MHz, **PIO blocks** for cycle-precise bus I/O, 30 GPIOs — the optimal choice), ESP32 (Xtensa/RISC-V at 240 MHz with Wi-Fi/Bluetooth), STM32 (F407 with hardware FMC), Arduino AVR (too slow), Teensy (high-performance). **Bus interface design**: address/data/control signal mapping (16+8+13 = 37 signals in 40-pin Z80 package, pin count problem solved with external latches/SPI expanders/CPLDs), voltage level translation (74HCT245 buffers for 3.3V MCU ↔ 5V bus, HCT vs HC thresholds). **Timing requirements**: Z80 nanosecond-level bus timing, realising it on a 133 MHz MCU (38 cycles per T-state), instruction-stepped vs cycle-stepped emulation (cycle-stepped needed for cycle-exact accuracy). **Z80 instruction emulation**: documented + undocumented instructions (`SLL`/`SLI`, `LD A,I`/`LD A,R` flags = IFF2, `OUT (C),0` NMOS writes 0 vs CMOS writes 0xFF, `BIT n,(HL)` X/Y flags), cycle counts, implementation techniques (direct interpretation, threaded code, JIT). Existing projects (PicoROM, PicoZ80, Pico Spectrum, libz80, z80ex). Integration with real Spectrum hardware (pinout adapters, level shifters, crystal oscillator). MCU Z80 vs Real Z80 vs FPGA T80 decision matrix. FAQ (RP2040 speed, undocumented instructions, IM 0/1/2, 3.3V on 5V bus, ZEXALL pass but demos fail, MCU speed requirement ~30× Z80 clock, integration on single RP2040, bus capacitance). Summary, references, cross-references |
| 2 | [mcu_ula.md](mcu_ula.md) | Coming soon: ULA on MCU — video generation, contention emulation, RP2040 PIO-based approaches |
| 3 | [mcu_fdc_vg93.md](mcu_fdc_vg93.md) | Coming soon: KR1818VG93 / WD1793 FDC on MCU — replacing the floppy controller with STM32, VG93Em-STM32 project |
| 4 | [mcu_psg_ay.md](mcu_psg_ay.md) | Coming soon: AY-3-8912 PSG on MCU — sound chip replacement, register-compatible implementations |
| 5 | [mcu_keyboard.md](mcu_keyboard.md) | Coming soon: Keyboard controller on MCU — ZXHIDKeyboard, PS/2 to ZX matrix conversion |
| 6 | [mcu_video_adapter.md](mcu_video_adapter.md) | Coming soon: Video adapters — VGA/HDMI output from RP2040 Pico, scanline generation, upscaling |
| 7 | [mcu_sd_interface.md](mcu_sd_interface.md) | Coming soon: SD card interfaces on MCU — replacing floppy with SD, TRDOS compatibility |
| 8 | [n_go.md](n_go.md) | Coming soon: N-Go — MCU-based Spectrum implementation |
| 9 | [mcu_design_patterns.md](mcu_design_patterns.md) | Coming soon: Design patterns — bus interfacing, level shifting, timing-critical I/O, GPIO speed requirements |

See [PLAN.md](../../PLAN.md) for the full article catalog.
