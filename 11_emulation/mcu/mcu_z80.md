[← Home](../../README.md) · [Emulation](../README.md) · [MCU Emulation](README.md)

# Z80 on a Microcontroller

A growing trend in retro-computing is replacing vintage ICs with modern microcontrollers (MCUs). The Z80 CPU is a prime candidate: original Zilog Z80s and their CMOS descendants (Z84C00) are still available but increasingly expensive, and Russian KR1858VM1 chips pulled from 1980s/1990s hardware have variable reliability. A modern MCU — typically an **RP2040 (Raspberry Pi Pico)**, **ESP32**, or **STM32** — can emulate the Z80 at cycle-exact speed while drawing a fraction of the power, fitting in a smaller footprint, and providing additional features (debugging, tracing, integrated peripherals).

This article covers the design, implementation, and trade-offs of emulating a Z80 CPU on a modern microcontroller, as a drop-in replacement for the original chip. For Z80 emulation in software emulators running on PCs, see [fuse.md](../software/fuse.md) and [zesarux.md](../software/zesarux.md). For FPGA-based Z80 implementation (T80), see [fpga_implementation.md](../fpga/fpga_implementation.md). For replacing the ULA (not the Z80) with an MCU, see [mcu_ula.md](mcu_ula.md).

---

## Why Replace the Z80 with an MCU?

Several motivations drive the MCU-based Z80 approach:

### Component Availability

Original Zilog Z80 chips (Z0840004, Z0840006, Z0840008, Z0840020 — the last digit is the max clock in MHz) are out of production. The Russian KR1858VM1 (CMOS clone) is still produced in small batches but quality varies. CMOS Z84C00 chips from secondary suppliers are available but prices are rising (£5–£15 per chip in 2025).

By contrast, an RP2040 costs around £1, an ESP32 around £3, and an STM32F407 around £5. All are vastly more capable than a Z80 and can be programmed to behave like one.

### Power Consumption

The original NMOS Z80 draws ~150 mA at 5V (0.75W). Modern CMOS versions are better (~20–50 mA). An RP2040 running at 3.5 MHz equivalent draws ~10 mA at 3.3V (0.033W). For battery-powered retro projects or modern recreations with tight power budgets, the MCU wins decisively.

### Reliability

A 40-year-old NMOS Z80 may have degraded (electromigration, gate oxide wear). Modern MCUs have lifetimes measured in decades at typical operating conditions. For a daily-use retro system, an MCU is more reliable.

### Additional Features

An MCU-based Z80 can provide features impossible with the original chip:

- **In-circuit debugging** — halt, single-step, inspect registers, view memory
- **Tracing** — log every instruction executed, with timestamps
- **Bus monitoring** — detect illegal accesses, watch specific addresses
- **Integrated peripherals** — replace the ULA, the AY, the FDC, all on the same MCU
- **Software-upgradable** — fix bugs, add features without replacing the chip

### Compatibility Layer

The MCU presents a Z80 bus interface to the host system: the address bus (`A[15:0]`), data bus (`D[7:0]`), and control signals (`M1_n`, `MREQ_n`, `IORQ_n`, `RD_n`, `WR_n`, `RFSH_n`, `BUSRQ_n`, `BUSACK_n`, `WAIT_n`, `INT_n`, `NMI_n`, `RESET_n`). To the rest of the system, the MCU looks like a real Z80.

---

## Host MCU Choices

### RP2040 (Raspberry Pi Pico)

The RP2040 is the most popular MCU for Z80 emulation, due to several features:

- **Dual-core ARM Cortex-M0+** at 133 MHz (overclockable to ~250 MHz)
- ** PIO (Programmable I/O)** — two blocks of 4 state machines each, capable of cycle-precise hardware I/O independent of the CPU
- **30 GPIO pins** — enough for the Z80's 16+8+12 = 36 signals (with creative multiplexing; some use an external latch)
- **Low cost** — ~£1 for the RP2040 chip, ~£4 for a Raspberry Pi Pico board
- **Abundant documentation** and community

The PIO is the killer feature for Z80 emulation. The Z80 bus requires precise timing relationships (e.g., `MREQ_n` falling edge, then `RD_n` falling edge, then data valid after some delay, then `RD_n` rising, then `MREQ_n` rising). Doing this from CPU code is difficult because interrupt latency and cache misses break timing. PIO state machines run deterministically, cycle-by-cycle, in parallel with the CPU. A typical design uses:

- One PIO block to implement the **bus slave** (drive `A`, `D`, `MREQ_n`, `IORQ_n`, `RD_n`, `WR_n` according to the emulated instruction cycle)
- The other PIO block to implement **memory/peripheral responses** (read RAM, write to ULA ports, etc.)
- Both CPU cores for **instruction emulation** (one core executes Z80 instructions, the other manages the bus cycle state machine)

### ESP32 / ESP32-S3

The ESP32 is a dual-core Xtensa (or RISC-V on ESP32-C3/S3) at 240 MHz, with Wi-Fi and Bluetooth. It has fewer GPIO pins (34) than the RP2040, no PIO equivalent, and its peripherals are less suited to bit-banged bus timing.

However, the ESP32's raw CPU speed (240 MHz vs 133 MHz) makes up for the lack of PIO. ESP32-based Z80 emulators achieve cycle-exact timing by careful interrupt handling and DMA. The ESP32's Wi-Fi makes it attractive for **network-connected Spectrum recreations** (e.g., a Wi-Fi-enabled Speccy that loads software from the internet).

### STM32 Family

ST's STM32 family (Cortex-M0/M3/M4/M7) is widely used in retro-computing projects. The **STM32F407** (Cortex-M4 at 168 MHz) is popular for high-performance Z80 emulation due to:

- Plenty of GPIO (up to 82 pins on the larger packages)
- Hardware FMC (Flexible Memory Controller) that can drive an external bus at deterministic timing
- DMA controllers for memory/peripheral data movement
- Floating-point unit (irrelevant for Z80 but useful for sound synthesis in integrated designs)

The STM32 is more expensive than the RP2040 (£5 vs £1) but provides more deterministic bus timing via the FMC.

### Other Choices

- **Arduino (AVR)** — too slow (16 MHz ATmega328) for full-speed Z80; viable for partial systems or slow peripherals
- **Teensy (Cortex-M7)** — high-performance, more expensive
- **iCE40 FPGA** — strictly not an MCU, but the smallest FPGAs compete in the same price/performance band (see [fpga_implementation.md](../fpga/fpga_implementation.md))

For most hobbyist projects, the RP2040 is the optimal choice — cheap, capable, well-documented.

---
## Bus Interface Design

The Z80's bus interface is well-documented but requires careful attention to signal timing. The key signals:

### Address and Data Buses

- **`A[15:0]`** — 16-bit address bus (output from CPU)
- **`D[7:0]`** — 8-bit bidirectional data bus (with tri-state)

The MCU must drive `A` as an output during all CPU cycles, and either drive `D` (during write cycles) or read `D` (during read cycles). The Z80's bus is tri-state — `D` is high-impedance when no device is driving it.

### Control Signals (Output from CPU)

- **`M1_n`** — active-low, asserted during the M1 (opcode fetch) cycle of each instruction
- **`MREQ_n`** — active-low, asserted during memory access
- **`IORQ_n`** — active-low, asserted during I/O port access
- **`RD_n`** — active-low, asserted during read cycles
- **`WR_n`** — active-low, asserted during write cycles
- **`RFSH_n`** — active-low, asserted during DRAM refresh cycles (after M1)

### Control Signals (Input to CPU)

- **`WAIT_n`** — active-low, asserted by external logic to hold the CPU in the current cycle
- **`INT_n`** — active-low, maskable interrupt request
- **`NMI_n`** — active-low, non-maskable interrupt request
- **`RESET_n`** — active-low, resets the CPU
- **`BUSRQ_n`** — active-low, requests the CPU to release the bus (for DMA)

### Control Signals (Output Acknowledgement)

- **`HALT_n`** — active-low, asserted when the CPU has executed a `HALT` instruction
- **`BUSACK_n`** — active-low, acknowledges `BUSRQ_n`

### Pin Count Problem

The Z80's 40-pin package has 16 + 8 + 13 = 37 signals (plus Vcc/GND). The RP2040 has 30 GPIO pins. This is a problem. Solutions:

- **External latch** — multiplex `A[15:8]` onto `D[7:0]` with a 74HC373 or similar latch, controlled by an extra signal. This is how the original Z80 itself addressed memory in some systems
- **SPI port expander** — shift the high address byte into a 74HC595 via SPI. Slower but pin-efficient
- **External address decoder** — use discrete logic (PAL/GAL/CPLD) for address decoding, freeing MCU pins
- **STM32 with more pins** — the STM32F407 in LQFP100 has 82 GPIOs, enough for the full bus without multiplexing

The PIO-based approach on RP2040 typically uses one PIO block for the high address byte (driving `A[15:8]` via 8 pins), and the other for the data bus + low address byte + control signals. With 30 pins total, the RP2040 can fit:

- 8 pins for `A[15:8]` (or `A[7:0]`)
- 8 pins for `D[7:0]`
- 8 pins for low byte of the other address half (via multiplexing)
- 6 pins for the critical control signals (`M1_n`, `MREQ_n`, `IORQ_n`, `RD_n`, `WR_n`, `RFSH_n`)

This leaves 0 pins for `INT_n`, `NMI_n`, `WAIT_n`, `RESET_n`, `BUSRQ_n`, `BUSACK_n`, `HALT_n` — which means these must be handled by the second PIO block or via shared pins with careful timing.

### Voltage Level Translation

The Z80 bus is 5V TTL. The RP2040, ESP32, and most STM32 (except a few 5V-tolerant variants) are 3.3V CMOS. The signals are not directly compatible:

- **5V → 3.3V input** — the RP2040's inputs are technically 3.3V but tolerate 5V on most pins (with caveats). However, this is not recommended for production designs
- **3.3V → 5V output** — 3.3V is high enough to be read as logic 1 by most 5V TTL inputs (TTL threshold is 2.0V), so direct drive often works
- **Recommended: level shifters** — use a 74HCT245 (TTL-compatible input thresholds, 5V output) for the data bus, and similar buffers for address and control signals

The 74HCT family is critical here: HCT inputs have TTL thresholds (VIH = 2.0V) which accept 3.3V CMOS output correctly, while HC inputs (CMOS thresholds, VIH = 3.5V at 5V Vcc) may not.

---

## Timing Requirements

The Z80's bus timing is specified in the Zilog datasheet with nanosecond-level precision. Key timings at 4 MHz (the original Spectrum's 3.5 MHz is similar):

- **Clock period** — 250 ns (at 4 MHz)
- **Address valid → `MREQ_n` falling** — typically 50–100 ns
- **`MREQ_n` falling → `RD_n` falling** — typically 0 ns (overlap allowed)
- **`RD_n` rising → data sampled** — typically 60 ns before end of cycle
- **Cycle duration** — 3 T-states for opcode fetch (M1), 3 for memory read, 3 for memory write

### Realising Timing on an MCU

To realise these timings on an MCU running at, say, 133 MHz (RP2040), each Z80 T-state (285 ns at 3.5 MHz) corresponds to ~38 MCU clock cycles. That's tight but workable:

- The PIO state machines run at 1 instruction per clock cycle, so a PIO program can hold exact timing
- The CPU cores have ~38 cycles per T-state to perform instruction emulation
- DMA can move data between RAM and GPIO ports with cycle precision

The challenge is **synchronisation**: the PIO drives the bus signals cycle-by-cycle, the CPU runs the Z80 emulator in parallel, and they communicate via interrupt/DMA. The CPU must produce the next bus cycle's data (e.g., the opcode to drive during the next M1) in time for the PIO to use it. If the CPU is too slow, the PIO stalls the bus (WAIT asserted) and timing accuracy degrades.

### Instruction-Stepped vs Cycle-Stepped

There are two fundamental approaches to Z80 emulation on MCU:

**Instruction-stepped**: The CPU runs the entire Z80 instruction, then asserts the bus signals for the appropriate number of cycles. This is simpler but loses timing fidelity — the bus signals are not generated cycle-by-cycle but in a burst at the end of each instruction.

**Cycle-stepped**: The CPU and PIO collaborate to generate bus signals **cycle-by-cycle**, matching the real Z80's bus timing. The CPU computes the next bus state each cycle, and the PIO drives it. This is harder but produces authentic timing.

For cycle-exact Spectrum compatibility (needed for demoscene, copy protection, etc.), cycle-stepped is required. Most high-quality RP2040 Z80 emulators use this approach, with one CPU core dedicated to cycle-step execution and the other handling the higher-level instruction stream.

---
## Z80 Instruction Emulation

The Z80 has a rich instruction set, including undocumented but well-known instructions. A faithful emulator must implement:

### Documented Instructions

- 8-bit load/store (`LD r,r'`, `LD r,n`, `LD r,(HL)`, `LD A,(BC)`, etc.)
- 16-bit load/store (`LD HL,nn`, `LD SP,HL`, `LD (nn),HL`, etc.)
- Exchanges (`EX DE,HL`, `EX AF,AF'`, `EXX`, `EX (SP),HL`)
- Arithmetic (`ADD`, `ADC`, `SUB`, `SBC`, `AND`, `OR`, `XOR`, `CP`)
- Increment/decrement (`INC r`, `DEC r`, `INC BC`, etc.)
- Rotates and shifts (`RLCA`, `RLA`, `RRA`, `RLC r`, `RL r`, `SLA r`, `SRL r`, `SRA r`, `RLD`, `RRD`)
- Bit operations (`BIT b,r`, `SET b,r`, `RES b,r`)
- Jumps (`JP nn`, `JP cc,nn`, `JP (HL)`, `JR e`, `JR cc,e`, `DJNZ e`)
- Calls and returns (`CALL nn`, `RET`, `RET cc`, `RETI`, `RETN`, `RST n`)
- Stack operations (`PUSH`, `POP`)
- I/O (`IN A,(n)`, `IN r,(C)`, `OUT (n),A`, `OUT (C),r`)
- Block operations (`LDI`, `LDIR`, `LDD`, `LDDR`, `CPI`, `CPIR`, `CPD`, `CPDR`, `INI`, `INIR`, `IND`, `INDR`, `OUTI`, `OTIR`, `OUTD`, `OTDR`)
- Interrupts (`DI`, `EI`, `IM 0`, `IM 1`, `IM 2`)
- Misc (`NOP`, `HALT`, `EI`, `DI`, `CCF`, `SCF`, `CPL`, `NEG`, `DAA`, `RLD`, `RRD`, `LD A,I`, `LD A,R`, `LD I,A`, `LD R,A`)

### Undocumented Instructions

The Z80's instruction decoder leaves several "holes" that produce undefined opcodes. Some of these have well-known behaviour that software depends on:

- **`SLL r` / `SLL (HL)`** — shift left logical, bit 0 set to 1 (mnemonic also written as `SLI` or `SL1`); opcodes `0x30–0x37` for the documented register pattern
- **`LD A,I` / `LD A,R` flags** — these copy I or R to A and update the parity/overflow flag to the value of IFF2 (the interrupt enable flip-flop), which software can use to detect interrupt state
- **`LDI/CPI/INI/OUTI` flags** — the N flag is set to 1 (as if subtraction), H is set based on the operation, and P/V is set based on the byte counter (BC); the half-carry behaviour differs between documented and actual hardware
- **`OUT (C),0`** — on NMOS Z80, this writes `0x00`; on CMOS Z80 (Z84C00), this writes `0xFF`. The Spectrum used NMOS Z80s, so the NMOS behaviour must be emulated
- **`BIT n,(HL)`** affects the undocumented `Y` and `X` flags (bits 5 and 3 of F) differently from `BIT n,r` — the value comes from the byte read, not the register

### Cycle Counts

Every instruction has a documented cycle count, but there are subtle variations:

- **`LD A,I` / `LD A,R`** — documented as 9 T-states, but the flag update has an additional latency
- **`LDI/CPI/INI/OUTI`** — the half-carry and parity flags have undocumented behaviours that depend on internal Z80 state
- **Conditional jumps taken vs not taken** — different cycle counts
- **Block instructions in their final iteration** — slightly different cycle count

A faithful cycle-stepped emulator must reproduce all of these cycle counts exactly, including the undocumented ones.

### Implementation Techniques

Three main implementation approaches:

**Direct interpretation**: A big `switch` statement in C, with one case per opcode. Simple but slow — each opcode requires a switch dispatch and then the handler code.

**Threaded code**: Each opcode's handler ends with a jump to the next handler (computed from the next opcode). Avoids the switch dispatch overhead. Common in high-performance interpreters.

**JIT compilation**: Compile Z80 opcodes to native ARM code on the fly. Most complex but fastest. Used by some high-end emulators (e.g., the ZX Spectrum Next's acceleration layer) but rarely on MCU due to code size and complexity.

For an MCU running at 133–240 MHz emulating a 3.5 MHz Z80, direct interpretation is typically fast enough. The cycle-stepped approach uses about 30–50 host cycles per emulated Z80 T-state, well within budget.

---

## Existing Projects

Several open-source MCU-based Z80 emulators exist:

- **PicoROM** — RP2040-based, designed to emulate Z80 peripherals (ROM/RAM/IO). Demonstrates PIO-driven bus interface
- **PicoZ80** — RP2040-based full Z80 + ULA replacement, runs complete Spectrum systems
- **Yazoo's Pico Spectrum** — RP2040-based Spectrum recreation
- **libz80** — C library implementing a Z80 emulator (used in many emulators, portable to MCU with care)
- **z80ex** — Another C library, focused on cycle accuracy
- **emu2149** — Specifically for AY-3-8910/8912 sound chip emulation (relevant for [mcu_psg_ay.md](mcu_psg_ay.md))

These projects demonstrate the techniques discussed here. For a full Z80 + ULA + AY + RAM replacement on a single RP2040, Pico Spectrum projects are the reference.

### Integrating with Real Spectrum Hardware

For drop-in replacement of a real Z80 in an existing Spectrum:

- **Pinout adapter** — a small PCB that maps the RP2040's GPIO pins to the Z80's 40-pin DIP layout
- **Level shifters** — 74HCT245 buffers on the data bus, 74HCT541 on the address and control lines
- **Crystal oscillator** — replace the Spectrum's existing clock or use the RP2040's PLL to synthesise 3.5 MHz
- **Firmware** — RP2040 firmware that emulates the Z80 and presents the correct bus signals

Several vendors sell ready-made "Pico Z80" boards with all the required hardware. For DIY builders, the design is reproducible from open-source schematics.

---

## Trade-offs

### MCU Z80 vs Real Z80

| Aspect | Real Z80 | MCU-based Z80 |
|---|---|---|
| **Cycle-exact timing** | ✅ Native | ✅ With cycle-stepped design |
| **Power consumption** | ~20–50 mA at 5V | ~10 mA at 3.3V |
| **Cost** | £5–£15 (rising) | £1 (RP2040) |
| **Reliability** | Variable (especially old chips) | Excellent |
| **Debugging** | Difficult | Easy (in-circuit) |
| **Tracing** | External logic analyser | Built-in |
| **Additional features** | None | Free (debugger, profiler, etc.) |
| **Bus capacitance** | High (real driver) | Low (MCU drive strength limited) |
| **Authenticity** | Maximum | High but not identical |

### MCU Z80 vs FPGA Z80 (T80)

| Aspect | MCU Z80 | FPGA Z80 (T80) |
|---|---|---|
| **Cycle-exact timing** | ✅ With careful design | ✅ Native |
| **Cost** | £1–£5 | £2–£10 (FPGA chip) |
| **Development ease** | C/C++ in standard toolchain | Verilog/VHDL, FPGA tools |
| **Flexibility** | High (reprogram easily) | Lower (resynthesis required) |
| **Integration** | Easy with peripherals | Harder (peripherals in HDL) |
| **Performance overhead** | Higher (interpretation) | Lower (native hardware) |
| **Power consumption** | Lowest | Low |

The choice between MCU and FPGA approaches depends on the project goals: MCU is easier to develop and more flexible, FPGA is more authentic and lower-overhead. The Harlequin and Sizif-512 use FPGAs; the various "Pico Speccy" projects use MCUs.

---
## FAQ

**Q: Can an RP2040 really emulate a Z80 at cycle-exact speed?**

A: Yes, with careful design. The RP2040's dual-core CPU at 133 MHz and dual PIO blocks provide enough throughput. Each Z80 T-state (285 ns at 3.5 MHz) corresponds to ~38 RP2040 cycles, which is enough time to execute the Z80 emulator and drive the bus signals. Overclocking to 250 MHz provides additional headroom.

**Q: Do I need to emulate undocumented instructions?**

A: If you want maximum software compatibility, yes. Several games and demos use `SLL`, `LD A,I/R` flag effects, or `OUT (C),0`. The libz80 and z80ex libraries have options for these; verify before deploying.

**Q: How do I handle the Z80's interrupt modes (IM 0, IM 1, IM 2)?**

A: IM 0 expects an instruction byte on the data bus when INT_n is asserted; IM 1 ignores the bus and calls `0x0038`; IM 2 uses the I register as the high byte of a vector table address. The Spectrum uses IM 1 for the 50 Hz frame interrupt and IM 2 for some peripheral interrupts. The emulator must implement all three correctly.

**Q: Can I use a 3.3V MCU directly on a 5V Z80 bus?**

A: Direct connection often "works" but is not reliable. 5V TTL outputs can exceed the RP2040's absolute maximum ratings on inputs. 3.3V outputs from the RP2040 are usually high enough for 5V TTL inputs (VIH threshold 2.0V) but noise margin is small. Use 74HCT buffers for production designs.

**Q: Why does my emulator pass ZEXALL but fail some demos?**

A: ZEXALL verifies instruction correctness, not bus timing. A demo that depends on exact contention patterns or floating bus behaviour will reveal timing errors that ZEXALL doesn't catch. Run the FUSE test suite and Sensible tests as well.

**Q: How fast does the MCU need to be?**

A: A rough rule: for cycle-stepped emulation, the MCU clock should be at least 30× the Z80 clock. So 3.5 MHz × 30 = 105 MHz minimum. The RP2040 at 133 MHz (or overclocked to 250 MHz) is comfortable; an ATmega328 at 16 MHz is not.

**Q: Can I integrate the Z80, ULA, AY, and other peripherals on a single RP2040?**

A: Yes — this is what "Pico Spectrum" projects do. The RP2040 has enough CPU power and GPIO pins (with creative use of PIO and external latches) to emulate the entire Spectrum. The trade-off is increased firmware complexity and tighter timing constraints.

**Q: What about bus capacitance and drive strength?**

A: The Z80's bus drivers are quite powerful (designed to drive many TTL loads and a few hundred pF of bus capacitance). MCU GPIO drivers are weaker. For long bus traces or many loads, use external buffers (74HCT245, etc.) to ensure signal integrity.

---

## Summary

Replacing the Z80 with a modern MCU is a viable and increasingly popular approach for retro-computing projects. The RP2040 is the optimal choice for most hobbyists due to its PIO blocks, low cost, and strong community. Achieving cycle-exact timing requires:

1. **Careful pin allocation** — fitting 37 Z80 signals into 30 RP2040 GPIOs requires multiplexing or external latches
2. **PIO-driven bus interface** — the PIO handles cycle-precise bus timing, freeing the CPU for instruction emulation
3. **Cycle-stepped execution** — the CPU produces bus state cycle-by-cycle, not instruction-by-instruction
4. **Correct undocumented behaviour** — `SLL`, `LD A,I/R` flags, `OUT (C),0`, etc.
5. **Level shifting** — 74HCT family buffers between 3.3V MCU and 5V bus

With these in place, an MCU-based Z80 can be indistinguishable from the original chip for most software, while providing debugging, tracing, and additional features impossible with a real Z80.

---

## References

- **Zilog Z84C00 Z80 CPU Product Specification** — official datasheet with pinout, timing, instruction set
- **Z80 Undocumented Instructions** — documented in various community references (Sean Young's "The Undocumented Z80 Documented")
- **Raspberry Pi RP2040 Datasheet** — PIO architecture, GPIO characteristics
- **PicoROM project** — RP2040-based ROM/RAM/IO emulator, open-source
- **libz80** — C Z80 emulator library by Lin Ke-Fong (used in FUSE and others)
- **z80ex** — C Z80 emulator library, cycle-accurate
- **"The ZX Spectrum ULA: How to Design a Microcomputer"** by Chris Smith — background on ULA timing that constrains Z80 emulation
- **Pico Spectrum projects on GitHub** — various open-source implementations
- **74HCT245 / 74HCT541 datasheets** — TTL-compatible buffers for level shifting

## Cross-references

- [ULA on MCU](mcu_ula.md) — replacing the ULA (not the Z80) with an MCU
- [FDC on MCU](mcu_fdc_vg93.md) — replacing the floppy disk controller
- [PSG/AY on MCU](mcu_psg_ay.md) — replacing the sound chip
- [Keyboard on MCU](mcu_keyboard.md) — keyboard controller replacement
- [Video adapter on MCU](mcu_video_adapter.md) — VGA/HDMI output from RP2040
- [SD interface on MCU](mcu_sd_interface.md) — SD-card storage replacement
- [FPGA Implementation](../fpga/fpga_implementation.md) — FPGA-based Z80 (T80) alternative
- [Cycle-exact timing](../fpga/fpga_timing_accuracy.md) — why timing precision matters
- [Fuse](../software/fuse.md) / [ZEsarUX](../software/zesarux.md) — software Z80 emulation on PC
