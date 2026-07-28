[← Home](../../README.md) · [Emulation](../README.md) · [MCU Emulation](README.md)

# N-Go — Complete Spectrum on a Microcontroller

The previous articles in this MCU section covered replacing individual Spectrum components with microcontrollers — the [Z80](mcu_z80.md), the [ULA](mcu_ula.md), the [FDC](mcu_fdc_vg93.md), the [PSG](mcu_psg_ay.md), the [keyboard](mcu_keyboard.md), the [video output](mcu_video_adapter.md), and the [SD storage](mcu_sd_interface.md). This article brings them all together: building a **complete Spectrum implementation on a microcontroller** — what the retro-computing community sometimes calls a **"Spectrum-on-a-chip"** or **N-Go** style project.

The term **N-Go** broadly refers to MCU-based Spectrum implementations where the entire machine (CPU, ULA, peripherals, mass storage, video, audio, input) is implemented in firmware on one or more microcontrollers. This is distinct from [FPGA recreations](../fpga/) (which implement the Spectrum in hardware description language) and from [software emulators](../software/) running on general-purpose PCs.

This article covers the architecture of complete MCU-based Spectrums, the integration challenges, memory organization, firmware structure, existing projects, and the trade-offs compared to FPGA recreations.

---

## What is a Complete Spectrum on MCU?

A complete Spectrum-on-MCU implements all of the following in firmware:

- **Z80 CPU emulation** — full instruction set, undocumented instructions, interrupts, cycle-accurate timing (see [mcu_z80.md](mcu_z80.md))
- **ULA emulation** — video generation (256×192 display + attributes + border), contended memory timing, floating bus, INT generation (see [mcu_ula.md](mcu_ula.md))
- **Memory** — the full Spectrum RAM (16 KB for 48K, 128 KB for 128K, plus ROM)
- **Sound** — the beeper (1-bit) and the AY-3-8912 PSG (for 128K/+2/+3) (see [mcu_psg_ay.md](mcu_psg_ay.md))
- **Input** — keyboard (PS/2 or USB), joystick, mouse (see [mcu_keyboard.md](mcu_keyboard.md))
- **Mass storage** — SD card for software loading (see [mcu_sd_interface.md](mcu_sd_interface.md))
- **Video output** — VGA, HDMI, or composite PAL for display (see [mcu_video_adapter.md](mcu_video_adapter.md))
- **Optional peripherals** — Beta 128 disk interface (FDC emulation), Kempston joystick port, tape I/O

The result is a single board (or small box) that contains a complete Spectrum, with no original silicon — just an MCU (or multiple MCUs), some passive components, connectors, and an SD card slot.

### Motivation

Building a complete Spectrum on an MCU is motivated by several factors:

- **Component scarcity** — original Z80s and ULAs are increasingly rare and expensive
- **Cost** — a complete MCU Spectrum can be built for under £10
- **Customisation** — firmware can be modified, features added, enhancements enabled (stereo sound, scanline effects, save states)
- **Repairability** — if an MCU fails, it's cheap to replace; if an original ULA fails, it's a major problem
- **Educational value** — building a complete Spectrum teaches how the machine works at a fundamental level
- **Portability** — a small MCU board with HDMI output can be carried anywhere

---

## Integration Challenges

Combining all the components into a single MCU presents several challenges:

### CPU Time Budget

The Z80 in a Spectrum runs at 3.5 MHz. To emulate it cycle-accurately, the host MCU must execute approximately 3.5 million Z80 cycles per second. Each Z80 cycle requires multiple MCU cycles to emulate (instruction decode, register updates, memory access). A rough estimate: 10-20 MCU cycles per Z80 cycle, so the host MCU needs at least 35-70 MHz of effective processing power just for the Z80.

The RP2040 runs at 133 MHz (overclockable to 250 MHz), giving a comfortable margin. But the Z80 is only one of many tasks — the ULA, PSG, keyboard scan, SD card access, and video generation all consume CPU time.

### Memory Bandwidth

The ULA reads video memory at ~7 MHz pixel rate (or ~3.5 MHz byte rate). This memory access must be interleaved with the Z80's accesses and the video output circuit's reads. The MCU's RAM must be fast enough to handle this.

The RP2040's SRAM is single-cycle access at 133 MHz, providing ample bandwidth. But organizing the video memory access pattern (interleaved with Z80 access and contention emulation) requires careful design.

### Real-Time Constraints

Video output is real-time — the PIO shifts out pixels at the pixel clock rate, with no margin for delay. If the MCU misses a deadline, the video frame is corrupted. This means the video output must be interrupt-driven or DMA-driven, with the CPU free to handle other tasks.

Audio is similarly real-time — the PSG must produce samples at the audio sample rate (44.1 kHz or 48 kHz) without gaps.

### Peripheral Pin Multiplexing

All the peripherals — keyboard, joystick, SD card, video output, audio output — share the MCU's GPIO pins. The RP2040 has 30 GPIOs, which is enough but requires careful pin assignment. Some functions (like SPI for SD card, or PIO for video) have fixed pin mappings on the RP2040's alternate function table.

---
## System Architectures

Three approaches are common for building a complete Spectrum on MCU:

### Single-MCU Architecture (RP2040)

The **single-MCU** approach uses one RP2040 to handle everything:

- **Core 0** — Z80 emulation, ULA logic (contention, INT timing), keyboard scan
- **Core 1** — PSG emulation, SD card access, file browser, miscellaneous tasks
- **PIO blocks** — video output (composite, VGA, or DVI), PS/2 keyboard input, optionally tape I/O
- **DMA** — video frame buffer to PIO, audio samples to PWM/I2S DAC

This is the most elegant approach — one chip does everything. The RP2040's dual cores and PIO blocks are well-suited to this task. The challenge is **memory** — the RP2040 has 264 KB of SRAM, which is enough for a 48K Spectrum (16 KB ROM + 48 KB RAM + frame buffer + stack) but tight for a 128K Spectrum (16 KB ROM + 128 KB RAM exceeds available SRAM).

Solutions to the memory constraint:

- **Use flash for ROM** — the Spectrum ROM is read-only and can be executed directly from the RP2040's flash (with XIP — eXecute In Place). This frees up SRAM for RAM
- **External PSRAM** — some RP2040 boards (like the Pimoroni Pico DV) include external PSRAM, providing megabytes of additional memory
- **Limit to 48K** — for the simplest implementation, only emulate the 48K Spectrum

### Dual-MCU Architecture

The **dual-MCU** approach splits the workload across two MCUs:

- **MCU 1 (RP2040)** — Z80 emulation, ULA logic, video output
- **MCU 2 (ESP32 or STM32)** — keyboard, SD card, network, file browser

The MCUs communicate via SPI or UART. This approach is more flexible (each MCU focuses on its tasks) but adds complexity (inter-MCU protocol, two firmware codebases).

The ESP32 as the second MCU adds Wi-Fi capability — the Spectrum can load software over the network.

### Multi-MCU Architecture

For maximum performance or flexibility, multiple MCUs can be used:

- **Z80 emulator MCU** — dedicated Z80 emulation
- **Video MCU** — dedicated video generation
- **Audio MCU** — dedicated PSG emulation
- **I/O MCU** — keyboard, joystick, SD card

This is overkill for most projects but can give very high accuracy (each component is emulated in dedicated hardware, like an FPGA).

---

## Memory Architecture

### Memory Map

A typical Spectrum-on-MCU memory map (single RP2040, 48K Spectrum):

| Address Range | Contents | Location |
|---|---|---|
| `#0000`-`#3FFF` | Spectrum ROM (16 KB) | RP2040 flash (via XIP) |
| `#4000`-`#FFFF` | Spectrum RAM (48 KB) | RP2040 SRAM (or external PSRAM) |
| Frame buffer | VGA/DVI frame buffer | RP2040 SRAM |
| Stack | MCU stack | RP2040 SRAM |
| Heap | MCU heap (file system, etc.) | RP2040 SRAM |

For a 128K Spectrum, the banking logic (port `#7FFD`) must be emulated — the 128 KB of RAM is divided into 8 banks of 16 KB, with one bank paged into the `#C000`-`#FFFF` range at a time.

### ROM Storage

The Spectrum ROM is fixed data — it never changes during operation. It can be stored in:

- **RP2040 flash** — 2 MB of flash on a standard Pico, plenty for the 16 KB or 32 KB Spectrum ROM. Accessed via XIP (eXecute In Place), appearing as memory at a fixed address
- **SD card** — loaded into RAM at boot. Slower startup but allows swapping ROMs (e.g., for different Spectrum models)
- **Embedded in firmware** — compiled into the firmware binary as a C array

The flash approach is preferred — it's fast and doesn't waste SRAM.

### Banking Emulation (128K)

For the 128K Spectrum, the banking logic must be emulated:

```c
// 128K banking: 8 banks of 16 KB
uint8_t ram_banks[8][16384];  // 128 KB total

// Current banking state (from port 0x7FFD)
uint8_t current_ram_bank = 0;  // Bank paged into 0xC000-0xFFFF

// Memory access function
uint8_t read_mem(uint16_t addr) {
    if (addr < 0x4000) {
        // ROM (could be swapped between ROM 0 and ROM 1)
        return rom[rom_bank * 16384 + addr];
    } else if (addr < 0x8000) {
        // Bank 5 (always mapped here)
        return ram_banks[5][addr - 0x4000];
    } else if (addr < 0xC000) {
        // Bank 2 (always mapped here)
        return ram_banks[2][addr - 0x8000];
    } else {
        // Paged bank
        return ram_banks[current_ram_bank][addr - 0xC000];
    }
}
```

### Frame Buffer

The frame buffer holds the upscaled video output:

- **VGA 640×480 at 8-bit color** — 640 × 480 = 307,200 bytes (~300 KB). Too large for the RP2040's SRAM.
- **VGA 320×240 at 8-bit color** — 76,800 bytes (~75 KB). Fits in RP2040 SRAM.
- **Direct Spectrum resolution (256×192)** — 49,152 bytes (~48 KB) at 8-bit, or 6,912 bytes at 1-bit + attributes.

For larger frame buffers, **external PSRAM** is needed. Some projects reduce the frame buffer by generating pixels on-the-fly from the Spectrum's video memory (no full frame buffer at all) — this is what the original ULA did.

---

## Firmware Structure

A typical Spectrum-on-MCU firmware has these components:

### Main Loop

```c
int main() {
    // Initialise hardware
    stdio_init_all();
    spi_init(spi0, 25000000);  // SD card SPI
    pio_video_init();           // Video output PIO
    pio_ps2_init();             // PS/2 keyboard PIO
    
    // Mount SD card
    f_mount(&fs, "", 1);
    
    // Load Spectrum ROM from flash (already in flash via XIP)
    // Or load from SD card
    
    // Initialise Z80 emulator
    z80_init(&z80, rom, ram);
    
    // Initialise ULA emulator
    ula_init(&ula);
    
    // Initialise PSG emulator (for 128K)
    psg_init(&psg);
    
    // Main loop — runs forever
    while (1) {
        // Run one frame's worth of Z80 cycles (~70,000 cycles)
        z80_run_frames(&z80, &ula, 69888);
        
        // Update PSG audio
        psg_run_frame(&psg);
        
        // Update keyboard state
        keyboard_update();
        
        // Update frame buffer for video output
        ula_update_frame_buffer(&ula, frame_buffer);
    }
}
```

### Multicore Setup

On RP2040, the two cores typically split work:

```c
// Core 0 main — Z80 + ULA + video
void core0_main() {
    while (1) {
        z80_run_frames(&z80, &ula, 69888);
        ula_update_frame_buffer(&ula, frame_buffer);
    }
}

// Core 1 main — keyboard + SD + PSG + network
void core1_main() {
    while (1) {
        keyboard_update();
        psg_run_frame(&psg);
        sd_poll();
        if (network_enabled) network_poll();
    }
}

int main() {
    multicore_launch_core1(core1_main);
    core0_main();
}
```

### Interrupts

The vertical sync interrupt (the ULA's INT signal at 50 Hz) is emulated by a hardware timer on the MCU. When the timer fires, the Z80 emulator's INT input is asserted, and the emulator handles the interrupt (jumping to the ISR at address `#0038`).

---
## Existing Projects

### Pico Spectrum

The **Pico Spectrum** is a collective name for various projects that implement a complete Spectrum on an RP2040. These projects combine:

- Z80 emulator (often based on **libz80** by Lin Ke-Fong or **z80ex**)
- ULA emulation including video and contention
- PS/2 or USB keyboard input
- VGA or HDMI video output
- SD card for software loading
- Beeper and (optionally) PSG emulation

Specific named projects include **Yazoo's Pico Spectrum**, **PicoZX**, and various community builds. They are typically open-source, with firmware and PCB designs available on GitHub.

### SpecHMI

**SpecHMI** is an STM32-based complete Spectrum, popular in the Russian retro-computing community. It uses an STM32F407 or similar, providing:

- Full Z80 + ULA emulation
- VGA video output
- PS/2 keyboard input
- SD card via SPI
- Beeper and PSG audio
- Optional network via ESP8266 addon

### ZX Spectrum on ESP32

Several projects implement a Spectrum on ESP32, taking advantage of the ESP32's higher clock speed (240 MHz) and Wi-Fi connectivity. These typically provide:

- Full Z80 + ULA emulation
- HDMI or VGA video output
- Bluetooth keyboard support
- Wi-Fi for loading software over the network
- Beeper and PSG audio

### Comparison with FPGA Spectrum Recreations

The [FPGA recreations](../fpga/) (Harlequin, Sizif-512, ZX-Uno, MiSTer) implement the Spectrum in hardware description language. Compared to MCU-based Spectrums:

| Aspect | MCU Spectrum | FPGA Spectrum |
|---|---|---|
| Cost | £1-10 (RP2040 + components) | £3-150 (FPGA board) |
| Development language | C/C++ | Verilog/VHDL |
| Iteration speed | Seconds (reflash firmware) | Minutes (resynthesise HDL) |
| Timing accuracy | Good (cycle-stepped) but subject to interrupt latency | Excellent (hardware) |
| Bus signals | Emulated in firmware | Native hardware pins |
| Flexibility | Easy to add features (filters, effects) | Harder, requires HDL changes |
| Community | Large (Arduino/RP2040 ecosystem) | Smaller but specialized |

MCU Spectrums are typically cheaper and easier to develop, while FPGA Spectrums have better timing accuracy and more authentic bus behavior.

---

## Comparison with Other Approaches

### vs Original Hardware

A complete MCU Spectrum is much cheaper than original hardware (which is increasingly collectible and expensive). It's also more reliable — no 40-year-old components to fail. But it lacks the "authentic" feel of original hardware, and the timing may not be 100% accurate (though close).

### vs FPGA Recreations

MCU Spectrums are cheaper and easier to develop. FPGA recreations have better timing accuracy and are closer to the original hardware in behavior. For most users, an MCU Spectrum is sufficient; for demoscene-level accuracy, FPGA is preferred.

### vs Software Emulators on PC

A software emulator on a modern PC is the most accurate and flexible option — cycle-exact timing, perfect audio, save states, debuggers. But a PC is not a "Spectrum" — it's a general-purpose computer running an emulator.

An MCU Spectrum is closer to "real hardware" — it's a dedicated device that just runs Spectrum software, with real video output and real input devices.

### vs Software Emulators on Retro Hardware

Some software emulators run on other retro hardware — e.g., a Spectrum emulator on a Commodore 64, or on an MSX. These are curiosities rather than practical solutions — the host hardware is usually too slow for full-speed emulation.

---

## FAQ

### Can I build a complete Spectrum on an Arduino?

Probably not. An Arduino Uno (ATmega328P at 16 MHz) is too slow — a Z80 at 3.5 MHz would require at least 35 MHz of host processing, and the ATmega has only 2 KB of RAM (far too little for 48 KB of Spectrum RAM).

An Arduino with more capable hardware (like the Arduino Portenta with STM32H7) could do it, but at that point you're just using an STM32.

### Can a single RP2040 emulate a 128K Spectrum?

Yes, but it's tight. The RP2040 has 264 KB of SRAM:

- 128 KB of Spectrum RAM (128K model)
- Frame buffer (~50 KB for 256×192 at 8-bit)
- Stack, heap, emulator state (~20 KB)
- Total: ~200 KB, leaving ~64 KB free

This fits, but doesn't leave much room for enhancements. For more comfortable memory headroom, use an RP2040 board with external PSRAM (like the Pimorono Pico DV).

### How accurate is the timing?

With cycle-stepped Z80 emulation and careful contention modeling, timing accuracy is very good — most software works correctly, including most demos. However, some edge cases (precise contention timing, undocumented Z80 flags) may differ from real hardware.

For demoscene-level accuracy, FPGA recreations (Harlequin, Sizif-512) are preferred.

### Can I add features not in the original Spectrum?

Yes — this is one of the main advantages of MCU Spectrums:

- **Save states** — snapshot the entire Spectrum state at any point
- **Rewind** — step backwards through execution
- **Turbo mode** — run the Z80 at 2×, 4×, or 8× speed for fast loading
- **Cheat codes** — POKE memory at startup
- **Stereo sound** — separate PSG channels for stereo output
- **Scanline effects** — add CRT-like scanlines to the video output
- **Debugging** — single-step the Z80, inspect registers and memory

### How do I load software?

Typically via SD card ([mcu_sd_interface.md](mcu_sd_interface.md)). The firmware includes a file browser that lists `.tap`, `.tzx`, `.z80`, `.sna`, `.trd` files on the SD card. The user selects a file, and the firmware loads it.

Some projects also support loading over USB (from a PC) or over Wi-Fi (from a network share).

### Can I connect original Spectrum peripherals?

Yes — the MCU can drive original peripherals via level shifters. For example, an original Kempston joystick can be connected to GPIO inputs (with 5V-to-3.3V level shifting). Original floppy drives can be connected via an FDC emulator (see [mcu_fdc_vg93.md](mcu_fdc_vg93.md)).

---

## Summary

Building a complete Spectrum on a microcontroller is a substantial project that integrates all the components covered in the previous articles:

1. **Z80 emulation** — full instruction set with cycle-accurate timing
2. **ULA emulation** — video generation, contention, floating bus, INT timing
3. **PSG emulation** — AY-3-8912 for 128K models
4. **Keyboard and joystick input** — PS/2, USB, or original peripherals
5. **SD card storage** — for loading software
6. **Video output** — VGA, HDMI, or composite PAL
7. **Audio output** — beeper and PSG via DAC or PWM
8. **Optional features** — network, save states, turbo mode, debugging

The **RP2040** is the optimal MCU for single-chip implementations, thanks to its dual cores, PIO blocks, and low cost. Multi-MCU architectures (RP2040 + ESP32) offer additional flexibility, especially for network connectivity.

The result is a complete Spectrum that costs under £10, fits in the palm of your hand, and runs the entire Spectrum software library — a powerful modern realisation of the 1982 design.

---

## References

- **RP2040 datasheet** — hardware reference for the Raspberry Pi Pico
- **libz80 by Lin Ke-Fong** — Z80 emulator library (used in FUSE)
- **z80ex** — cycle-accurate Z80 emulator
- **Pico Spectrum projects on GitHub** — various open-source implementations
- **SpecHMI project** — STM32-based complete Spectrum (Russian community)
- **Chris Smith's *The ZX Spectrum ULA*** — for the ULA's behavior
- **FatFs by Elm-Chan** — FAT file system library
- **PicoVGA** by Miroslav Nemecek — VGA output library
- **Pico DVI** by Luke Wren — DVI output library

## Cross-References

- [Z80 on MCU](mcu_z80.md) — the CPU core of a complete Spectrum
- [ULA on MCU](mcu_ula.md) — the video and memory arbitration logic
- [PSG on MCU](mcu_psg_ay.md) — sound generation
- [Keyboard on MCU](mcu_keyboard.md) — input handling
- [Video adapter on MCU](mcu_video_adapter.md) — output to modern displays
- [SD interface on MCU](mcu_sd_interface.md) — mass storage
- [FDC on MCU](mcu_fdc_vg93.md) — for disk-based software
- [FPGA implementation](../fpga/fpga_implementation.md) — alternative approach using FPGA
- [Harlequin/Sizif](../fpga/harlequin_sizif.md) — popular FPGA recreations for comparison
- [MCU design patterns](mcu_design_patterns.md) — general techniques for integration
