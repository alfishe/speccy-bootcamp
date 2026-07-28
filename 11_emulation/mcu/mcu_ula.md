[← Home](../../README.md) · [Emulation](../README.md) · [MCU Emulation](README.md)

# ULA on a Microcontroller

The Spectrum's ULA (Uncommitted Logic Array) is the most complex and most failure-prone component of the original hardware. Original Ferranti ULAs in 48K Spectrums are now 40+ years old and frequently fail — and there are no direct replacements, since Ferranti's ULA business was sold to Plessey in the late 1980s and the tooling was scrapped. A modern recreation of the ULA using a microcontroller (MCU) is therefore one of the most valuable projects in retro-computing preservation.

Replacing the ULA with an MCU requires emulating not just the video generation (the most visible function) but also the memory arbitration (contention), the I/O ports, the INT signal generation, and the various timing signals. This is substantially more complex than [Z80 emulation on MCU](mcu_z80.md) because the ULA's behaviour is tightly coupled to the video beam position and to the CPU's bus cycle.

This article covers the design of ULA-on-MCU implementations, including video generation via RP2040 PIO, contention state machines, floating bus emulation, and composite video output. For background on the ULA itself, see Chris Smith's *The ZX Spectrum ULA: How to Design a Microcomputer*. For FPGA-based ULA recreation (as used in the Harlequin), see [harlequin_sizif.md](../fpga/harlequin_sizif.md).

---

## Why Replace the ULA with an MCU?

### ULA Failure

The Ferranti ULA in the 48K Spectrum (and the equivalent custom ICs in later models) is the single most common point of failure in original hardware. Symptoms include:

- **No video output** — the ULA's video generation fails entirely
- **Garbage screen** — video is generated but pixels/attributes are corrupted
- **No keyboard input** — the ULA's keyboard scanning fails
- **No sound** — the beeper driver fails
- **Random crashes** — memory arbitration fails, causing the CPU to read/write incorrect data

A failed ULA cannot be repaired — the chip must be replaced. Since original Ferranti ULAs are not available, the only options are NOS (new old stock, increasingly rare and expensive) or a modern recreation.

### ULA Knowledge

Chris Smith's reverse-engineering work, documented in *The ZX Spectrum ULA: How to Design a Microcomputer* (2010), provides the definitive specification of the ULA's behaviour. With this knowledge, recreating the ULA in modern hardware is a tractable engineering problem.

### MCU Choice for ULA

The ULA's functions are well-suited to an MCU with hardware I/O capabilities:

- **Video generation** — pixel-precise timing, best implemented with PIO (on RP2040) or hardware timers and DMA (on STM32)
- **Memory arbitration** — state machine, easily implemented in firmware
- **I/O ports** — simple register reads/writes
- **INT generation** — timer-driven interrupt

The RP2040 is again the optimal choice, due to its PIO blocks which can generate video signals with cycle precision while the CPU handles the rest of the ULA's logic.

---

## ULA Functions

The ULA performs several distinct functions, each of which must be emulated:

### Video Generation

The ULA generates the Spectrum's video signal. Specifically:

- It maintains the **video address counter** that walks through display RAM, fetching pixel bytes and attribute bytes in the correct order
- It shifts pixel bytes through the **pixel shift register**, producing one pixel per video clock cycle
- It applies the **attribute byte** (INK, PAPER, BRIGHT, FLASH) to each pixel via the colour encoder
- It generates the **composite video signal** — horizontal sync, vertical sync, blanking, colour burst, and pixel data — for output to a TV
- It mixes in the **BORDER colour** (from port `0xFE`) for the screen border area

The video signal is generated at a fixed pixel clock (approximately 7 MHz on the 48K Spectrum, with the composite signal at PAL standard timing).

### Memory Arbitration

The ULA shares RAM with the CPU. During the active display area, the ULA needs to fetch bytes from RAM for video generation. To prevent bus contention, the ULA asserts `WAIT_n` on the CPU during specific cycles, holding it off while the video fetcher has the bus.

This produces the characteristic **contended memory** timing of the Spectrum — accesses to addresses `0x4000`–`0x7FFF` (the upper 16 KB of the 48K address space) are slowed down during the active display area, with a specific asymmetric pattern of WAIT assertions.

### I/O Ports

The ULA implements several I/O ports:

- **Port `0xFE`** (the most important) — write: beeper, MIC output, EAR input, BORDER colour; read: keyboard matrix row (selected by `A[8:15]`), EAR input
- **Port `0xFF`** (floating bus) — read: returns the byte the ULA is currently fetching from video memory; write: no effect
- **Memory bank switching** (on 128K / +2 / +3) — handled by additional logic

### INT Generation

The ULA asserts INT every 20 ms (50 Hz) at a specific scanline (line 64 of the 48K frame). This is the vertical sync interrupt that software uses for frame timing.

### Clock Generation

The ULA generates the CPU clock by dividing down its master clock. In the 48K Spectrum, the master clock is 14 MHz (used directly for video), divided by 4 to produce the 3.5 MHz CPU clock.

### Beeper

The ULA includes a 1-bit DAC (essentially a flip-flop) for the beeper audio. Software toggles this via port `0xFE` bit 4 to produce square wave audio at any frequency the CPU can manage.

---
## Video Generation on RP2040 PIO

The video generation is the most demanding ULA function — it requires producing a pixel every ~143 ns (at 7 MHz pixel clock), with precise sync timing for the composite signal.

### Pixel Timing

The 48K Spectrum's video timing:

- **Pixel clock** — 7 MHz (one pixel every 143 ns)
- **Scanline** — 448 pixels wide (224 CPU T-states × 2 pixels/T-state), of which 256 are active display
- **Frame** — 311 scanlines, of which 192 are active display
- **Sync pulses** — HSYNC at end of each scanline, VSYNC at end of frame

Generating this on an MCU requires precise cycle timing. The RP2040's PIO is ideal:

- A PIO state machine can shift out pixels at one per clock cycle
- The PIO clock can be set to 7 MHz (divided down from the 125 MHz system clock)
- Sync pulses can be generated by the same state machine, with precise cycle counts

### PIO Program for Composite Video

A typical PIO program for Spectrum composite video:

1. **Initialise** — load the first scanline's pixel data into the PIO's ISR (input shift register)
2. **Pixel loop** — shift out 8 pixels per byte (with attribute applied), 32 bytes per scanline
3. **HSYNC** — at end of scanline, drive the HSYNC pulse (4 µs low, then back porch, then front porch)
4. **VSYNC** — at end of frame, drive the VSYNC pulses (a sequence of half-scanline sync pulses per PAL standard)
5. **Repeat** — for the next scanline

The PIO runs autonomously, reading pixel data from a buffer prepared by the CPU. The CPU's job is to:

- Maintain the video address counter
- Fetch pixel and attribute bytes from RAM (or from a video memory buffer in the RP2040)
- Apply the attribute (INK/PAPER/BRIGHT/FLASH) to produce the final pixel stream
- Load the pixel stream into the PIO's buffer via DMA

This separation of concerns — PIO for cycle-precise signal generation, CPU for higher-level logic — is the key to the RP2040's effectiveness as a ULA replacement.

### Composite Signal Generation

Generating a true PAL composite signal requires more than just pixels — the signal must include:

- **Horizontal sync** — 4.7 µs low pulse at the end of each scanline
- **Vertical sync** — a sequence of pulses at the end of each frame (PAL uses a complex sequence of equalisation pulses, sync pulses, and more equalisation pulses)
- **Colour burst** — a 10-cycle 4.43 MHz reference signal after HSYNC, used by the TV's colour decoder (the Spectrum's signal is monochrome, but a colour burst is still included for compatibility)
- **Blanking levels** — the signal is at the "black" level during blanking intervals

Some RP2040 ULA implementations generate **true composite** by combining the pixel data with sync pulses via a resistor DAC. Others generate **VGA** instead — driving separate HSYNC/VSYNC/pixel signals at TTL levels, which is simpler and works with modern monitors.

### VGA Output

VGA is simpler than composite PAL:

- Separate HSYNC and VSYNC signals (TTL digital)
- RGB pixel data (analog, via resistor DAC)
- No colour burst, no blanking levels, no PAL encoding

An RP2040 driving a VGA monitor at 50 Hz refresh, 256×192 resolution upscaled to ~640×480 or 720×576, is straightforward. The PIO generates HSYNC and VSYNC; the CPU (via DMA) feeds pixel data.

### HDMI Output

HDMI output from RP2040 requires an external HDMI encoder IC (e.g., the ADV7513) or bit-banged DVI via the PIO (the RP2040's PIO is fast enough to generate DVI signals at low resolutions). The Pico DVI project demonstrates this approach.

---

## Contention Emulation

The memory contention pattern is one of the ULA's most subtle behaviours. Software depends on the exact pattern of WAIT assertions, so it must be reproduced faithfully.

### The Contention State Machine

The contention logic is essentially a state machine that, given:

- The current video position (scanline, pixel position)
- Whether the CPU is accessing contended memory
- The position within the current 4-T-state character cycle

...decides whether to assert `WAIT_n` on the CPU.

On an MCU, this is implemented in firmware:

```c
// Pseudocode for the contention state machine
bool should_assert_wait(int scanline, int pixel_pos, 
                        bool cpu_accessing_contended, 
                        int cycle_in_char) {
    if (!cpu_accessing_contended) return false;
    if (scanline < 64 || scanline >= 256) return false;  // Border
    
    // Within the active display, the contention pattern is:
    // - Cycles 1-2: WAIT asserted (ULA fetching)
    // - Cycles 3-4: WAIT released (CPU free)
    if (cycle_in_char <= 2) return true;
    return false;
}
```

The actual pattern is more nuanced — Chris Smith's book documents the exact per-cycle WAIT pattern, which the MCU must reproduce.

### Integration with the CPU

The contention logic runs in the same MCU as the Z80 emulator (or in a separate MCU, with WAIT_n driven across). The state machine updates every CPU cycle, deciding whether to assert WAIT_n.

For cycle-stepped Z80 emulation (see [mcu_z80.md](mcu_z80.md)), the contention state machine runs synchronously with the Z80 emulator, advancing the video position counter as the Z80 advances through T-states.

---

## Floating Bus Emulation

The floating bus effect — port `0xFF` reads returning the byte the ULA is currently fetching — is implemented by routing the ULA's video fetch data onto the CPU data bus at the right cycles.

In an MCU-based implementation, this requires:

- The ULA emulator to keep track of the current video fetch byte (the pixel or attribute byte currently being read from video memory)
- When the CPU reads port `0xFF`, return this byte if the read is happening during a contention cycle (when the ULA would have the byte on the bus)
- Otherwise return `0xFF` (the value the bus would have if nothing is driving it)

This is straightforward to implement but must be timed correctly — software probes the floating bus at specific cycles and expects specific values.

---

## I/O Port Emulation

The ULA's I/O ports are implemented as register reads/writes in the MCU:

### Port 0xFE Write

| Bit | Function |
|---|---|
| 0–2 | BORDER colour (0–7) |
| 3 | EAR output (also enables MIC input) |
| 4 | MIC output / beeper |
| 5–7 | Unused |

Writing to port `0xFE` updates the corresponding registers in the MCU, which affect video (BORDER colour) and audio (beeper) generation.

### Port 0xFE Read

| Bit | Function |
|---|---|
| 0–4 | Keyboard matrix row (selected by `A[8:15]`) |
| 5 | Unused |
| 6 | EAR input |
| 7 | Unused |

Reading port `0xFE` returns the keyboard state (managed by a separate [keyboard controller](mcu_keyboard.md)) and the EAR input bit.

### Port 0xFF (Floating Bus)

Reads return the byte currently on the ULA's video fetch data path, as described above. Writes have no effect.

---
## Complete ULA Replacement

A complete ULA replacement must handle all the ULA's functions, not just video and contention. The full set includes:

### Video Address Counter

The video address counter walks through display RAM in the Spectrum's unusual interleaved pattern (see [fpga_implementation.md](../fpga/fpga_implementation.md)). On an MCU, this is a simple counter with bit shuffling:

```c
// Spectrum video address calculation
uint16_t video_addr(int x, int y) {
    uint16_t addr = 0x4000;  // Display RAM base
    addr |= ((y & 0xC0) << 5);   // Y7 Y6 -> addr 13 12 (shifted)
    addr |= ((y & 0x38) << 2);   // Y5 Y4 Y3 -> addr 7 6 5
    addr |= ((y & 0x07) << 8);   // Y2 Y1 Y0 -> addr 10 9 8
    addr |= (x >> 3);             // X7..X3 -> addr 4..0
    return addr;
}
```

For each scanline, the MCU fetches the 32 pixel bytes and 32 attribute bytes (256 pixels / 8 per byte) and builds the pixel stream.

### INT Generation

The INT pulse is asserted at scanline 64 (the start of the top of the active display) and held for 32 T-states. The MCU generates this via a timer that fires at the appropriate point in the frame.

### Clock Generation

If the MCU is generating the CPU clock (as in some integrated designs), it divides its master clock to produce 3.5 MHz. The RP2040's clock generator can produce this directly.

### Beeper

The beeper is a 1-bit signal driven by port `0xFE` bit 4. The MCU toggles a GPIO pin in response to writes, and the resulting square wave is filtered and amplified for the speaker.

### 128K / +2 / +3 Considerations

For the later Spectrum models, the ULA replacement must also handle:

- **Memory banking** — the 128K's paged RAM, controlled by port `0x7FFD`
- **AY-3-8912 sound chip** — integrated into the ULA replacement or handled separately (see [mcu_psg_ay.md](mcu_psg_ay.md))
- **Different contention scheme** — the 128K has different contended pages and patterns
- **Different video timing** — the 128K has a longer top border and slightly different frame layout

### Integration with Other Components

A complete Spectrum-on-MCU typically integrates:

- **Z80 emulator** (see [mcu_z80.md](mcu_z80.md))
- **ULA emulator** (this article)
- **RAM** — typically emulated in the MCU's own SRAM (the RP2040 has 264 KB, enough for the 48K Spectrum's 16 KB ROM + 48 KB RAM)
- **ROM** — loaded from flash or SD card
- **AY-3-8912 emulator** (see [mcu_psg_ay.md](mcu_psg_ay.md))
- **Keyboard controller** (see [mcu_keyboard.md](mcu_keyboard.md))
- **Storage** — SD card via SPI (see [mcu_sd_interface.md](mcu_sd_interface.md))

All of these can fit in a single RP2040, producing a complete Spectrum-on-a-chip.

---

## Existing Projects

Several open-source ULA-on-MCU projects exist:

- **Pico Spectrum** — RP2040-based complete Spectrum, demonstrates PIO video generation
- **Yazoo's Spectrum** — RP2040-based, includes ULA emulation
- **PicoVGA** — RP2040 VGA library, used as a building block for ULA video output
- **Pico DVI** — RP2040 DVI/HDMI output via PIO
- **SpecHMI** — RP2040-based, designed for original Spectrum integration

These projects demonstrate the techniques described here. The combination of PIO-driven video generation and cycle-stepped Z80 emulation produces a Spectrum-on-MCU that runs essentially all software.

---

## Comparison with FPGA ULA Recreation

The Harlequin and Sizif-512 use FPGAs to recreate the ULA (see [harlequin_sizif.md](../fpga/harlequin_sizif.md)). How does the MCU approach compare?

### Advantages of MCU

- **Easier development** — C/C++ in standard toolchain vs Verilog/VHDL with FPGA tools
- **Lower cost** — RP2040 (~£1) vs Cyclone II/IV (~£3–£10)
- **Faster iteration** — reflash firmware vs resynthesise HDL (which can take minutes)
- **Integrated peripherals** — USB, Wi-Fi (on ESP32), SD card, debugging all built-in
- **Stronger community** — more MCU developers than FPGA developers

### Advantages of FPGA

- **Native parallelism** — multiple modules run truly in parallel, no scheduling overhead
- **Lower timing jitter** — all logic is deterministic, no interrupt latency
- **More authentic bus signals** — FPGA pins drive the bus at TTL levels natively (with appropriate banks)
- **Established solutions** — T80 + ULA HDL is well-tested and proven

### Practical Choice

For most hobbyist projects, the MCU approach is more accessible. For production-quality recreations targeting maximum authenticity (e.g., the Harlequin), the FPGA approach is preferred. Both achieve cycle-exact timing when carefully implemented.

---

## Trade-offs Summary

| Aspect | FPGA (Harlequin) | MCU (Pico Spectrum) |
|---|---|---|
| **Cycle-exact timing** | ✅ Native | ✅ With careful design |
| **Cost** | £3–£10 FPGA | £1 RP2040 |
| **Development ease** | Verilog/VHDL | C/C++ |
| **Iteration speed** | Slow (synthesis) | Fast (reflash) |
| **Bus drive strength** | Excellent (5V TTL native) | Limited (3.3V CMOS, needs buffers) |
| **Integrated peripherals** | Limited (custom HDL) | Rich (USB, Wi-Fi, SD, debug) |
| **Power consumption** | Low | Lowest |
| **Community size** | Smaller | Larger |

---

## FAQ

**Q: Can an RP2040 generate a real PAL composite video signal?**

A: Yes. The PIO can generate the precise pixel clock and sync timing required. The composite signal is produced via a simple resistor DAC (3-bit or 4-bit is sufficient for the Spectrum's 8 colours + bright variants). Several open-source projects demonstrate this.

**Q: Does the MCU approach achieve cycle-exact contention?**

A: Yes, if the implementation is cycle-stepped. The contention state machine runs in lockstep with the Z80 emulator, advancing the video position counter as the Z80 advances through T-states. The result is contention indistinguishable from real hardware.

**Q: How do I handle the floating bus?**

A: Keep track of the byte currently on the ULA's video fetch path (the most recent pixel or attribute byte fetched). When the CPU reads port `0xFF` during a contention cycle, return that byte. Otherwise return `0xFF`. The timing of when to return the byte vs `0xFF` is documented in Chris Smith's book.

**Q: Can I integrate the ULA and Z80 on a single RP2040?**

A: Yes — this is what "Pico Spectrum" projects do. The RP2040 has enough CPU power and GPIO to handle both. The Z80 emulator runs on one CPU core, the ULA logic on the other, with PIO handling the video signal generation.

**Q: Why use composite output instead of VGA/HDMI?**

A: Composite output is authentic — it works with CRT TVs and produces the "Spectrum look" (slight blur, colour bleed, scanlines). VGA/HDMI is sharper but lacks the nostalgia factor. For authenticity, composite; for daily use, VGA/HDMI.

**Q: Do I need a separate video memory buffer in the MCU?**

A: Not necessarily. The ULA emulator can read directly from the emulated Spectrum RAM (in the MCU's SRAM) at the right times. However, having a dedicated video buffer (a "shadow display RAM" that's updated lazily) can simplify the timing — the video generator reads from the buffer, while the Z80 emulator updates it on writes.

**Q: How accurate does the contention pattern need to be?**

A: For 95%+ of software, the gross pattern (uniform delay during active display) is sufficient. For demoscene productions (multicolour, sync-scroller) and copy-protected software, the exact per-cycle pattern is required. The latter requires careful study of Chris Smith's book.

**Q: Can I emulate the 128K's different contention on the same MCU?**

A: Yes — the contention state machine is parameterised by the machine model. The MCU tracks the current banking register and applies the appropriate contention pattern (page 5 contended on 128K, etc.).

---

## Summary

Replacing the ULA with an MCU is one of the most valuable projects in retro-computing preservation. The RP2040 is the optimal choice due to its PIO blocks, which can generate video signals with cycle precision while the CPU handles the rest of the ULA's logic. Key requirements:

1. **PIO-driven video generation** — for cycle-precise pixel and sync timing
2. **Contention state machine** — for authentic memory access timing
3. **Floating bus emulation** — for software that probes screen position
4. **I/O port implementation** — port `0xFE` for beeper/BORDER/keyboard, port `0xFF` for floating bus
5. **INT generation** — for the 50 Hz frame interrupt

With these implemented, an MCU-based ULA can be indistinguishable from the original Ferranti chip for most software, and can additionally provide modern conveniences (debugging, alternate video outputs, integrated peripherals).

---

## References

- **Chris Smith**, *The ZX Spectrum ULA: How to Design a Microcomputer* (2010) — the definitive ULA reference
- **Raspberry Pi RP2040 Datasheet** — PIO architecture, DMA, GPIO characteristics
- **Pico Spectrum projects on GitHub** — various open-source ULA-on-MCU implementations
- **PicoVGA** — RP2040 VGA generation library
- **Pico DVI** — RP2040 DVI/HDMI generation via PIO
- **PAL composite video specification** — for sync and colour burst timing
- **Harlequin project** — FPGA ULA recreation for comparison (see [harlequin_sizif.md](../fpga/harlequin_sizif.md))
- **Sensible tests by Andrew Owen** — for floating bus and contention verification

## Cross-references

- [Z80 on MCU](mcu_z80.md) — companion article on Z80 emulation
- [PSG/AY on MCU](mcu_psg_ay.md) — sound chip replacement
- [Keyboard on MCU](mcu_keyboard.md) — keyboard controller
- [Video adapter on MCU](mcu_video_adapter.md) — VGA/HDMI output details
- [Harlequin / Sizif](../fpga/harlequin_sizif.md) — FPGA-based ULA recreation
- [FPGA implementation](../fpga/fpga_implementation.md) — broader FPGA approach
- [Cycle-exact timing](../fpga/fpga_timing_accuracy.md) — why timing precision matters
