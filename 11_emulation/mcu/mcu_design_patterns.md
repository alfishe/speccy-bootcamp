[← Home](../../README.md) · [Emulation](../README.md) · [MCU Emulation](README.md)

# MCU Design Patterns for Spectrum Integration

The previous articles in this MCU section covered individual components — replacing the [Z80](mcu_z80.md), the [ULA](mcu_ula.md), the [FDC](mcu_fdc_vg93.md), the [PSG](mcu_psg_ay.md), the [keyboard](mcu_keyboard.md), the [video output](mcu_video_adapter.md), and the [SD storage](mcu_sd_interface.md), and [bringing them together](n_go.md) into a complete Spectrum. This final article steps back and covers the **general engineering patterns** that recur across all of those projects — the techniques that make a modern microcontroller reliably interface with 1980s hardware.

These patterns are independent of any specific component. They concern three questions:

1. **How does a 3.3V MCU talk to a 5V TTL bus safely?** — voltage level translation
2. **How does a 133 MHz MCU keep up with nanosecond-level Z80 bus timing?** — timing-critical I/O
3. **How do you organize firmware to handle video/audio/input/storage simultaneously without missing deadlines?** — software design patterns

This article covers bus interfacing techniques, level shifting (with the critical 74HCT vs 74HC threshold distinction), timing-critical I/O via PIO and DMA, GPIO drive strength and slew rate, common software patterns for real-time retro-computing firmware (state machines, ring buffers, double buffering, lock-free queues), pin multiplexing strategies, and power supply considerations. The patterns apply to any retro-computing MCU project — Spectrum, C64, Amiga, Atari ST, MSX, CPC, BBC Micro — not just the Spectrum.

---

## Bus Interfacing Techniques

When an MCU needs to communicate with the Spectrum's bus (or any classic CPU bus), three interface styles are common:

### Memory-Mapped I/O

The simplest interface — the MCU appears as a region of memory in the Spectrum's address space. The Spectrum reads/writes the MCU by executing `LD` instructions against those addresses, and the MCU's firmware responds.

In hardware terms, this means the MCU must:

1. **Decode addresses** — watch the address bus, and only respond when the address falls within its assigned range (e.g., `#0000-#3FFF` for a ROM, or `#1FFD`/`#3FFD` for an I/O device)
2. **Observe bus controls** — `MREQ_n` (memory request), `RD_n` (read), `WR_n` (write), `IORQ_n` (I/O request) — and respond accordingly
3. **Drive the data bus** — during a read, the MCU must place the requested byte on `D[7:0]` within the bus timing window

This is the standard interface for **memory expansions** (e.g., paged RAM at `#0000-#3FFF`), **DivMMC** (16 KB ROM paged into address space), and **interface ROMs**.

### Port I/O

For smaller devices that don't need to occupy a memory region, **port I/O** uses the Z80's `IN`/`OUT` instructions. The Z80 executes `OUT (n),A` to write to an I/O port, or `IN A,(n)` to read from one. The MCU responds to `IORQ_n` going low with the matching port number on the address bus.

The Spectrum uses port I/O for many peripherals:

- Port `#FE` — ULA (BORDER color, beeper, EAR/MIC, keyboard matrix)
- Port `#1F` — Kempston joystick
- Port `#FFFD`/`#BFFD` — AY-3-8912 PSG (128K)
- Port `#7FFD` — Memory banking (128K)
- Port `#1FFD` — +2A/+3 secondary banking
- Ports `#1F`/`#3F`/`#5F`/`#7F` — Beta 128 FDC

The MCU monitors `IORQ_n` and the low byte of the address bus (`A[7:0]`), and responds with the matching peripheral behavior. Since the Z80's I/O space is 256 ports (`A[7:0]`), partial decoding is common — the Kempston port at `#1F` is sometimes decoded as just `A[5]=0`.

### DMA (Direct Memory Access)

For high-throughput transfers (e.g., loading a screen from SD card into video memory), the MCU can use **DMA** — bypassing the Z80 entirely and writing directly to the Spectrum's RAM. This requires:

1. The MCU asserts `BUSRQ_n` (bus request)
2. The Z80 responds by tri-stating its bus pins and asserting `BUSACK_n` (bus acknowledge)
3. The MCU now drives the address, data, and control lines, reading/writing RAM directly
4. When done, the MCU releases `BUSRQ_n`, and the Z80 resumes

DMA is rarely used in retro adapters because (a) it pauses the Z80, disrupting timing, (b) implementing the full bus master is complex, and (c) most peripherals don't need the throughput — even loading a screen takes only milliseconds of CPU time.

### Bus Master vs Bus Slave

Most MCU retro adapters act as **bus slaves** — they respond to the Spectrum's read/write cycles but never initiate them. The Spectrum is the master.

The exceptions are:

- **DMA controllers** (above) — the MCU is briefly the master
- **MCU-based CPU replacements** (e.g., [PicoZ80](mcu_z80.md)) — the MCU *is* the master, generating the bus cycles
- **Test equipment / logic analysers** — the MCU snoops the bus without driving it

For slave operation, the MCU must obey the Z80's bus timing — it has a fixed window (typically a few hundred nanoseconds) to respond to a read/write cycle. For master operation, the MCU must generate that timing — driving `MREQ_n`, `RD_n`, `WR_n` with the correct durations and setup/hold times.


---

## Voltage Level Translation

The Spectrum (and most 1980s computers) uses **5V TTL logic**. Modern MCUs (RP2040, ESP32, STM32 — except some 5V-tolerant STM32 variants) use **3.3V CMOS logic**. These are **not directly compatible**, even though both will read a logic 1 from a 3.3V source. Understanding why is critical.

### The Two Voltage Domains

- **5V TTL** (Spectrum, Z80, ULA, 74LS, 74ALS, original 74S): Logic high (`VIH`) is **2.0V minimum**, logic low (`VIL`) is **0.8V maximum**. Output high (`VOH`) is typically 2.4V minimum (often ~3.5V on a lightly loaded bus). Output low (`VOL`) is 0.5V maximum.
- **3.3V CMOS** (RP2040, ESP32, most STM32, 74HC, 74AHC): Logic high (`VIH`) is **0.7 × VDD = 2.3V** minimum, logic low (`VIL`) is **0.3 × VDD = 1.0V** maximum. Output high (`VOH`) is close to VDD (3.3V). Output low (`VOL`) is close to 0V.

The good news: **3.3V CMOS output high (3.3V) exceeds the 5V TTL input threshold (2.0V)**. So a 3.3V MCU driving a 5V TTL input "works" for the high state. And 5V TTL output low (0.5V) is within the 3.3V CMOS input low threshold (1.0V), so the low state works too.

The problem: **5V TTL output high can exceed the 3.3V MCU's absolute maximum voltage**. A 5V TTL device outputting high can swing to nearly 5V (especially 74HC parts at 5V, or a lightly loaded Z80 `RD_n` line). The MCU's ESD protection diodes will conduct, clamping the voltage to VDD + 0.3V, but this can damage the MCU over time or cause latch-up.

### The Solution: 74HCT Buffers

The standard solution is to insert **74HCT** family buffers between the 5V bus and the 3.3V MCU. The key:

- **74HCT** (High-Speed CMOS, **TTL-compatible inputs**) — `VIH` is **2.0V** (TTL threshold), `VIL` is **0.8V** (TTL threshold). Powered at 5V, but accepts 3.3V logic correctly. Outputs are 5V CMOS levels (~5V high).
- **74HC** (High-Speed CMOS, **CMOS inputs**) — `VIH` is **0.7 × VDD = 3.5V** at 5V VDD. **Does NOT accept 3.3V logic reliably** — the 3.3V signal is below the 3.5V threshold. **Do not use 74HC for translating 3.3V → 5V**.

The single-letter difference (HCT vs HC) is critical and a common beginner mistake. A 74HC245 will randomly misread a 3.3V signal as low. A 74HCT245 will read it correctly.

Common buffer ICs:

- **74HCT245** — octal bidirectional transceiver with direction pin and enable. The workhorse for translating the 8-bit data bus. Set `DIR` based on `RD_n`/`WR_n`.
- **74HCT541** — octal unidirectional buffer/driver. For read-only buses (e.g., address bus from Z80 to MCU).
- **74HCT244** — octal unidirectional buffer, similar to '541 but different pinout.
- **74HCT273** — octal D-type flip-flop. For latching the MCU's output onto the bus.
- **74HCT373/573** — octal transparent latch. For latching the address bus.

### Directional Translation

For unidirectional signals (e.g., `A[15:0]` from Z80 to MCU), there are two distinct cases depending on direction:

1. **5V bus → 3.3V MCU** (reading address bus, control signals): A 74LVC541 or 74HCS541 powered at 3.3V will accept 5V inputs (modern LVC/HCS logic is 5V tolerant when VDD is 3.3V — check the datasheet) and output 3.3V. Alternatively, a simple **series resistor** (e.g., 1K) limits current through the MCU's ESD diode to a safe level — useful for prototype work but not production.
2. **3.3V MCU → 5V bus** (driving data bus during read response, driving control signals): Use **74HCT** (TTL thresholds) powered at 5V. The MCU's 3.3V outputs drive the HCT inputs (which accept 2.0V as high), and the HCT outputs swing to 5V — satisfying both 5V TTL and 5V CMOS destinations.

### Bidirectional Translation

For the **data bus** (bidirectional), use a **74HCT245** with the `DIR` pin controlled by `RD_n`/`WR_n`:

```c
// Direction control for 74HCT245 on data bus
// When RD_n = 0 (Spectrum reads), MCU drives bus: DIR = A-to-B
// When WR_n = 0 (Spectrum writes), Spectrum drives bus: DIR = B-to-A
// When neither, bus is high-impedance: OE_n = 1

void update_bus_direction(int rd_n, int wr_n) {
    if (rd_n == 0) {
        gpio_put(DIR_PIN, 1);  // A (MCU) to B (Spectrum bus)
        gpio_put(OE_PIN, 0);   // Enable outputs
    } else if (wr_n == 0) {
        gpio_put(DIR_PIN, 0);  // B (Spectrum bus) to A (MCU)
        gpio_put(OE_PIN, 0);   // Enable outputs
    } else {
        gpio_put(OE_PIN, 1);   // High-impedance
    }
}
```

### Resistor Dividers (Cheap but Slow)

For low-speed signals (e.g., PS/2 keyboard at ~15 kHz, or static control lines), a simple **resistor divider** (e.g., 2.2K series + 3.3K to ground, giving 5V → 3.0V) is sufficient. Cheap, simple, no active components. But:

- **Slow** — the RC time constant with bus capacitance limits speed to ~1 MHz
- **Unidirectional** — only works for 5V → 3.3V
- **Lossy** — wastes power, weak drive

Resistor dividers are common for UART, PS/2, slow GPIO inputs. Don't use them for the high-speed Z80 bus.

### Dedicated Level Shifter ICs

For mixed-voltage interfaces (SPI, I2C, UART), dedicated level shifter ICs exist:

- **TXB0108** — 8-channel bidirectional voltage translator, auto-direction sensing, up to 20 MHz (push-pull) or 1 MHz (open-drain I2C)
- **TXS0108E** — similar with integrated pull-ups, good for I2C/SPI
- **SN74LVC1T45** — single-channel bidirectional translator with DIR pin, up to 100 MHz

These are convenient for peripheral connections (SD card at 3.3V from a 5V MCU, I2C sensors, etc.) but rarely needed for the Z80 bus itself, where 74HCT buffers are more appropriate due to higher drive strength.

### Power Sequencing

When mixing voltage domains, **power sequencing matters**:

1. Apply **5V first** (the Spectrum's supply) — this powers the 74HCT buffers and the original chips
2. Apply **3.3V** (the MCU's supply, derived from 5V via a regulator) — the MCU starts up
3. The MCU's pins must be **high-impedance during reset** — most MCUs do this by default, but check
4. If the MCU drives a pin high before its VDD is stable, it can back-power the regulator, causing erratic startup

A **power-on reset (POR)** circuit (e.g., a reset supervisor like the MCP100) ensures the MCU stays in reset until VDD is stable.

### What About 5V-Tolerant MCUs?

Some MCUs have **5V-tolerant inputs** — the input protection diodes are designed to handle 5V without damage. The STM32 family (most variants) is 5V-tolerant on many pins (marked as `FT` in the datasheet). The Arduino ATmega328P runs entirely at 5V.

For 5V-tolerant inputs, you can connect 5V signals directly — no buffer needed for reading. **Output is still 3.3V**, so for driving 5V TTL inputs you still need buffers if the destination needs more than 2.0V (which it usually doesn't for TTL — the HCT-vs-HC issue only matters for chips with CMOS thresholds).


---

## Timing-Critical I/O

The Z80's bus operates at nanosecond-level timing. A 3.5 MHz Z80 has a clock period of **286 ns**. Each bus cycle is 3-4 clock periods (~860-1140 ns), with critical setup/hold windows of **30-50 ns** for address, data, and control signals.

A 133 MHz RP2040 has a clock period of **7.5 ns** — so one Z80 T-state spans ~38 RP2040 cycles. That's enough for software to respond, but only barely. **Direct GPIO manipulation in software is rarely fast enough** for the Z80 bus.

### Cycle-Stepped vs Instruction-Stepped

For Z80 emulation on an MCU, two approaches to timing:

- **Instruction-stepped** — emulate one Z80 instruction at a time, advancing the host clock by the instruction's cycle count. Simpler, but loses per-cycle timing fidelity (e.g., when the ULA checks for contention mid-instruction). Used by simple emulators like Lin Ke-Fong's `libz80`.
- **Cycle-stepped** — emulate one Z80 T-state at a time, advancing the host clock by exactly 286 ns. More accurate, preserves per-cycle behavior (contention, interrupt response, floating bus). Used by `z80ex` and serious emulators.

For a **bus slave** (responding to a real Z80), cycle-stepping isn't needed — the real Z80 generates the timing, and the MCU just responds. But for a **bus master** (MCU emulating the Z80 and driving the bus), cycle-stepping is essential for authentic timing.

### RP2040 PIO — The Game Changer

The RP2040's **PIO (Programmable I/O)** is what makes it uniquely suited for retro-computing. Each PIO block contains 4 state machines that execute simple programs independently of the CPU, with cycle-precise timing. Key features:

- **Cycle-precise** — each PIO instruction takes exactly 1 cycle (7.5 ns at 133 MHz), with deterministic jumps
- **No CPU overhead** — once started, a PIO state machine runs without CPU intervention
- **Direct GPIO access** — each instruction can set/clear/read GPIOs in a single cycle
- **FIFOs for data** — 4-word TX/RX FIFOs per state machine, decoupling PIO from CPU
- **ISR/OSR shift registers** — shift bits in/out at one bit per cycle, ideal for serial protocols

For the Z80 bus, a PIO state machine can:

1. **Wait for `IORQ_n` falling edge** — `WAIT 0 gpio IORQ` (1 cycle)
2. **Read address bus** — `IN PINS, 8` (1 cycle, reads 8 GPIOs into ISR)
3. **Compare to expected port** — `JMP PIN x_not_match skip` (1 cycle)
4. **Drive data bus** — `OUT PINS, 8` followed by `SET PINS drive` (2 cycles)
5. **Wait for `IORQ_n` rising edge** — `WAIT 1 gpio IORQ` (1 cycle)
6. **Release bus** — `SET PINS high_z` (1 cycle)

Total response: ~5-7 cycles = ~37-52 ns. Well within the Z80's timing budget.

The CPU is free to update the PIO's FIFOs with the data to be returned, with the PIO handling all timing-critical work autonomously.

### DMA for High-Throughput Transfers

For moving bulk data (e.g., video frame buffer to a VGA PIO, audio samples to a PWM DAC), **DMA** is essential. The RP2040 has 12 DMA channels that can transfer data between any memory-mapped locations without CPU intervention.

Typical DMA patterns:

- **Memory → PIO TX FIFO** — video pixels, audio samples. The PIO consumes data at its own rate, with the DMA refilling the FIFO as needed.
- **PIO RX FIFO → Memory** — captured bus data (e.g., Z80 read transactions snooped by the PIO)
- **Memory → Memory** — frame buffer updates, image scaling. Triggered by the CPU.

DMA chaining (one channel triggers another) allows complex pipelines without CPU intervention.

### Interrupt Priorities and Latency

When the MCU must respond to an asynchronous event (e.g., a Z80 `INT_n` that needs immediate attention), **interrupts** are used. But interrupt latency is the enemy of real-time:

- **ARM Cortex-M0+** (RP2040): Interrupt latency is **12 cycles** (~90 ns at 133 MHz) — the time from interrupt assert to the first instruction of the ISR executing.
- **ARM Cortex-M4** (STM32F4): Latency is **12 cycles** (~71 ns at 168 MHz).
- **Xtensa LX6** (ESP32 dual-core): Latency is variable, ~200-500 ns depending on cache hits.

For the Z80 bus, 90 ns is too slow for direct response — by the time the ISR runs, the Z80 has already moved on. **PIO or GPIO-glue-logic** is required for cycle-precise bus responses.

But for less time-critical events (e.g., SD card data ready, audio buffer low, frame vertical sync), interrupts are appropriate. The RP2040's NVIC (Nested Vectored Interrupt Controller) supports priorities, allowing high-priority interrupts (e.g., audio) to preempt low-priority ones (e.g., SD card).

### Jitter Sources

Even with deterministic code, several sources of **timing jitter** exist:

- **Flash cache misses** — on RP2040, fetching code from external flash via XIP has variable latency (cache hit ~1 cycle, miss ~50+ cycles). **Run timing-critical code from SRAM** (`__not_in_flash_func`).
- **Memory contention** — multiple bus masters competing for SRAM. The RP2040 has 4 ARM bus ports; assign critical data to dedicated SRAM banks.
- **Interrupt preemption** — a high-priority interrupt arriving during timing-critical code can disrupt it. **Disable interrupts** (`critical_section`) around tight loops.
- **DMA stealing cycles** — DMA transfers can block CPU access to memory. Configure DMA priorities.

---

## GPIO Drive Strength and Slew Rate

Driving the Z80 bus (especially the data bus during read response) requires **strong, fast** GPIO outputs. The Z80's `D[7:0]` pins have input capacitance (~10 pF each), and the bus traces add more. With 8 pins + trace capacitance of ~50 pF, the GPIO must source/sink significant current to change the voltage quickly.

### RP2040 GPIO Drive Strength

The RP2040's GPIOs have configurable drive strength:

- **2 mA** — default, lowest power, slowest edges
- **4 mA** — moderate
- **8 mA** — strong, faster edges
- **12 mA** — maximum, fastest edges

For the Z80 bus, **12 mA drive strength** is recommended. Configure with `gpio_set_drive_strength(pin, GPIO_DRIVE_STRENGTH_12MA)`.

### Slew Rate Control

The RP2040 also has **slew rate control**:

- **Slow** (default) — limits the edge rate to reduce EMI. Suitable for low-speed signals.
- **Fast** — full-edge rate, suitable for high-speed signals.

For the Z80 bus, **fast slew rate** is recommended (`gpio_set_slew_rate(pin, GPIO_SLEW_RATE_FAST)`).

### STM32 GPIO Speeds

STM32 MCUs have similar configurable speeds, typically:

- **Low speed** — ~2 MHz, suitable for static signals
- **Medium speed** — ~12.5 MHz
- **High speed** — ~50 MHz
- **Very high speed** — ~100 MHz

For the Z80 bus, **high speed** is sufficient. The "very high" setting adds EMI without benefit at Z80 rates.

### Toggle Rate Calculations

A GPIO's toggle rate determines how fast it can change state. For an RP2040 at 133 MHz:

- Direct GPIO toggle (software `gpio_put()`): ~6 cycles per toggle = ~22 MHz toggle rate
- PIO-driven toggle (one instruction = one toggle): 133 MHz / 2 = ~66 MHz toggle rate
- DMA-driven via SIO: similar to PIO

For comparison, the Z80's fastest signal is the clock at **3.5 MHz** (or 7 MHz on a 128K/+2/+3). Even software-driven GPIO is fast enough for the Z80 clock, but the **response time** (signal-in → signal-out) is what matters for bus cycles, not the toggle rate.

### Bus Capacitance

A long bus trace (e.g., a ribbon cable from an expansion port to an external MCU board) adds significant capacitance — **10-30 pF per signal**, plus the destination pin capacitance. With weak GPIO drive, this can cause:

- **Slow edges** — the RC time constant stretches transitions, causing setup/hold violations
- **Reflections** — fast edges on long traces reflect back, causing ringing and overshoot. A **series termination resistor** (~22-33Ω) at the source damps reflections.

For long buses, use **buffer ICs** (74HCT245) near the MCU to provide strong drive, with the buffer's outputs feeding the long bus.


---

## Software Design Patterns

Real-time retro-computing firmware must juggle multiple time-sensitive tasks — Z80 emulation, video output, audio generation, keyboard scanning, SD card access — without missing deadlines. Several software patterns make this manageable.

### State Machines

The most fundamental pattern. Each subsystem (keyboard scanner, PSG emulator, SD card driver, file browser) is implemented as a **state machine** — a function called periodically that processes inputs, updates internal state, and produces outputs.

```c
typedef enum {
    KB_STATE_IDLE,
    KB_STATE_WAIT_START,
    KB_STATE_READ_DATA,
    KB_STATE_CHECK_PARITY,
    KB_STATE_PROCESS_SCANCODE,
} kb_state_t;

typedef struct {
    kb_state_t state;
    uint8_t shift_reg;
    int bit_count;
    uint64_t key_state;
} keyboard_t;

// Called on PS/2 clock falling edge (via PIO interrupt)
void keyboard_step(keyboard_t *kb, int data_bit) {
    switch (kb->state) {
        case KB_STATE_IDLE:
            if (data_bit == 0) kb->state = KB_STATE_WAIT_START;  // start bit
            break;
        case KB_STATE_WAIT_START:
            kb->shift_reg = (kb->shift_reg >> 1) | (data_bit << 7);
            if (++kb->bit_count == 8) kb->state = KB_STATE_CHECK_PARITY;
            break;
        // ... etc
    }
}
```

State machines avoid blocking — each call returns quickly, allowing the scheduler to run other state machines. The pattern scales to dozens of subsystems.

### Cooperative Scheduler

A simple **cooperative scheduler** runs each state machine in turn:

```c
typedef void (*task_fn)(void *);

typedef struct {
    task_fn fn;
    void *ctx;
    uint32_t period_us;     // target period in microseconds
    uint32_t last_run_us;
} task_t;

task_t tasks[] = {
    { z80_step,      &z80,    1,        0 },  // every 1 µs
    { psg_step,      &psg,    20,       0 },  // every 20 µs (50 kHz)
    { keyboard_scan, &kb,     1000,     0 },  // every 1 ms
    { sd_poll,       &sd,     10000,    0 },  // every 10 ms
};

void scheduler_run(void) {
    while (1) {
        uint32_t now = time_us_32();
        for (int i = 0; i < ARRAY_SIZE(tasks); i++) {
            if (now - tasks[i].last_run_us >= tasks[i].period_us) {
                tasks[i].fn(tasks[i].ctx);
                tasks[i].last_run_us = now;
            }
        }
    }
}
```

This works well when each task completes quickly. For long-running tasks (e.g., SD card read), break them into state machines that yield after a few microseconds.

### Ring Buffers

For producer-consumer patterns (e.g., keyboard scan codes produced by interrupt, consumed by main loop), a **ring buffer** (FIFO) is standard:

```c
#define RING_SIZE 64  // must be power of 2

typedef struct {
    uint8_t buf[RING_SIZE];
    volatile uint32_t head;  // written by producer (ISR)
    volatile uint32_t tail;  // read by consumer (main loop)
} ring_t;

// Called from ISR
void ring_push(ring_t *r, uint8_t byte) {
    uint32_t next = (r->head + 1) & (RING_SIZE - 1);
    if (next != r->tail) {  // not full
        r->buf[r->head] = byte;
        r->head = next;
    }
    // else: overflow, drop byte (or increment a counter for diagnostics)
}

// Called from main loop
int ring_pop(ring_t *r, uint8_t *byte) {
    if (r->head == r->tail) return -1;  // empty
    *byte = r->buf[r->tail];
    r->tail = (r->tail + 1) & (RING_SIZE - 1);
    return 0;
}
```

The power-of-2 size allows the `& (SIZE-1)` trick instead of `% SIZE`, which is faster. The `volatile` qualifiers ensure the compiler doesn't optimize away the reads.

### Lock-Free SPSC Queues

For **single-producer single-consumer** (SPSC) — the most common case — the ring buffer above is **lock-free**: no mutex needed, because only one writer and one reader exist. The writer advances `head`, the reader advances `tail`, and they read each other's variables (but never write them).

This works because:

- Single-word reads/writes are atomic on ARM (32-bit aligned)
- The `volatile` keyword prevents the compiler from caching stale values
- Memory barriers (`__dmb()` on ARM) ensure visibility across cores (for multicore systems)

For multi-producer or multi-consumer queues, a mutex is required. But SPSC covers most retro-computing use cases.

### Double Buffering

For frame buffers, **double buffering** avoids tearing — the display reads one buffer while the CPU writes the other, then they swap:

```c
typedef struct {
    uint8_t *front;  // currently displayed
    uint8_t *back;   // currently being drawn
} doublebuf_t;

// Called at vertical sync (display has finished reading front buffer)
void doublebuf_swap(doublebuf_t *db) {
    uint8_t *tmp = db->front;
    db->front = db->back;
    db->back = tmp;
}
```

The swap is atomic (just pointer assignment), so no tearing. The cost is doubled memory — two frame buffers instead of one.

On the RP2040 with limited SRAM, double buffering may be infeasible. Alternatives:

- **Single buffer with vsync-aware updates** — only update the part of the frame not currently being scanned out (track the CRT beam position)
- **Triple buffering** — one buffer being scanned out, one finished, one being drawn. Allows the CPU to start drawing the next frame without waiting for vsync.

### Multicore FIFO

On the RP2040's dual cores, the **SIO hardware** provides a 8-word FIFO per direction for inter-core communication. This is faster than shared memory with locks:

```c
// Core 1 sends a command to Core 0
void core1_send_cmd(uint32_t cmd) {
    while (!multicore_fifo_wready()) ;  // wait if FIFO full
    multicore_fifo_push_blocking(cmd);
}

// Core 0 receives the command (in interrupt)
void core0_fifo_isr(void) {
    while (multicore_fifo_rvalid()) {
        uint32_t cmd = multicore_fifo_pop_blocking();
        process_cmd(cmd);
    }
}
```

The 8-word depth is shallow, so use it for commands/acknowledgements, not bulk data. For bulk data, use shared SRAM with the lock-free SPSC ring pattern.

### Interrupt-Driven vs Polling

Two ways for a subsystem to learn about events:

- **Polling** — check a status flag periodically in the main loop. Simple, no ISR overhead. Used for low-frequency events.
- **Interrupt-driven** — register an ISR that fires on the event. Responsive, but ISR overhead and concurrency concerns. Used for high-frequency or urgent events.

For a retro-computing MCU:

- **Video output** — PIO/DMA-driven, never polled (real-time)
- **Audio output** — DMA-driven, with low-water-mark interrupt for refills
- **Keyboard (PS/2)** — interrupt-driven (clock falling edge)
- **Keyboard (matrix scan)** — polled (every 1 ms)
- **SD card** — polled in main loop, with DMA for transfers
- **Z80 bus** — PIO-driven, never polled (real-time)

As a rule of thumb: if missing an event would cause a visible glitch (video tearing, audio gap), use interrupts or PIO/DMA. If missing an event just delays processing by a frame, polling is fine.

### Avoiding Priority Inversion

When using multiple interrupts of different priorities, **priority inversion** can occur: a low-priority ISR holds a lock needed by a high-priority ISR, blocking it. On ARM Cortex-M, the **BASEPRI** register allows masking low-priority interrupts while allowing high-priority ones — use `critical_section` from the SDK which respects BASEPRI.

The simplest defense: **avoid locks in ISRs**. ISRs should be short, fast, and lock-free — push to a ring buffer, set a flag, exit. All heavy processing happens in the main loop.


---

## Pin Multiplexing Strategies

The RP2040 has 30 GPIOs — many for a typical MCU, but tight for a full Spectrum integration. A typical full Spectrum needs:

- **Address bus** (16 pins): `A[15:0]`
- **Data bus** (8 pins): `D[7:0]`
- **Z80 controls** (8 pins): `MREQ_n`, `IORQ_n`, `RD_n`, `WR_n`, `M1_n`, `RFSH_n`, `INT_n`, `BUSRQ_n`/`BUSACK_n`
- **Video output** (VGA: 9 pins for 3-bit RGB + HSYNC + VSYNC, or DVI: 8 pins for TMDS pairs)
- **Audio output** (1-2 pins for PWM/I2S)
- **PS/2 keyboard** (2 pins: clock + data)
- **SD card SPI** (4 pins: CS, SCK, MOSI, MISO)
- **Optional**: UART for debugging, GPIO for status LEDs, ADC for analog inputs

Total: ~50 pins needed. The RP2040 has only 30 — there's a shortfall.

### Strategies for Multiplexing

1. **PIO for video, free up CPU pins** — video output via PIO uses ~8-12 pins but doesn't need CPU attention
2. **External address latch** — use a 74HC373 to latch the high address byte (`A[15:8]`), requiring only 9 pins for the address bus (8 data + 1 latch enable). Saves 8 pins.
3. **SPI port expanders** — use 74HC595 shift registers (output) or 74HC165 (input) via SPI. Costs a few pins but adds many. Adds latency, so only for slow signals.
4. **CPLD or GAL** — a small programmable logic device (like the ATF1504 or XC9536) can decode addresses and multiplex signals, offloading glue logic from the MCU
5. **Use a bigger MCU** — STM32 F407 in LQFP100 has 82 GPIOs, enough for everything directly

### Pin Assignment Constraints

The RP2040's alternate function table constrains which pins can do what:

- **SPI** — fixed pin choices (e.g., SPI0 on GP0-GP3 or GP4-GP7 or GP16-GP19 or GP20-GP23)
- **UART** — fixed pin choices
- **I2C** — fixed pin choices
- **PWM** — slice/channel pairs, more flexible but still constrained
- **PIO** — can access any pin, so video/audio on any free GPIO
- **ADC** — only GP26-GP29 (4 pins)

The recommended workflow:

1. Assign **ADC inputs** first (most constrained)
2. Assign **SPI/UART/I2C** (next most constrained)
3. Assign **PIO-driven signals** (video, audio, PS/2) — most flexible
4. Assign **bit-banged GPIOs** last (anything left over)

### Pin Multiplexing Trade-offs

- **Time multiplexing** — share a pin between two functions at different times (e.g., during boot vs runtime). Tricky, error-prone.
- **External multiplexer** (e.g., 74HC4051 analog mux or 74HC151 digital mux) — switch a pin between functions. Adds propagation delay.
- **Function merging** — combine signals where possible (e.g., one status LED that blinks different patterns for different events)

For most projects, the simplest solution is **use a bigger MCU** or **add external latches/shift registers**.

---

## Power Supply Considerations

### Voltage Rails

A typical retro-computing MCU project has multiple voltage rails:

- **5V** — supplied by the host (Spectrum's +5V rail), used for the 5V TTL bus
- **3.3V** — derived from 5V via an LDO regulator (e.g., AMS1117, MCP1700), used for the MCU and most peripherals
- **1.2V** — internal to some MCUs (RP2040's core regulator generates this from 3.3V)

### Current Budget

Add up the current consumption of all components:

- **RP2040** — ~30 mA active at 133 MHz
- **External flash** — ~10 mA during reads
- **SD card** — up to 100 mA during writes (peak)
- **74HCT buffers** — ~5 mA each
- **PS/2 keyboard** — ~100 mA (powered from host)
- **HDMI/DVI output** — negligible (digital, low current)
- **VGA output** — ~50 mA per color channel at peak white (1V into 75Ω)

Total: ~200-300 mA typical. The Spectrum's +5V rail can supply ~700 mA (issue 2) to ~1.5 A (issue 6+), so there's headroom.

### Decoupling

Each IC needs **decoupling capacitors** close to its power pins:

- **100 nF ceramic** — for high-frequency noise, one per VDD pin
- **10 µF tantalum or electrolytic** — for bulk supply smoothing, one per board section
- **1 µF ceramic** — for medium-frequency noise, often paired with the 100 nF

Without proper decoupling, fast switching (GPIO toggles, DMA activity) can cause voltage droops that reset or hang the MCU.

### LDO Regulator Selection

The LDO that converts 5V → 3.3V must:

- **Handle the current** — a 300 mA regulator is the minimum; 500 mA or 1A is safer
- **Have low dropout** — the input is 5V, output 3.3V, so dropout is 1.7V — most LDOs handle this easily
- **Be stable with the load capacitance** — check the datasheet for recommended output cap ESR range

Common choices: **AMS1117-3.3** (cheap, ubiquitous, ~1A), **MCP1700-3302** (low quiescent current, 250 mA), **AP2112K-3.3** (SOT-23, 600 mA).

### Backpowering

A common pitfall: if the MCU's GPIOs are driven high while the MCU is unpowered (e.g., during power-up sequencing), current flows through the ESD diodes into the MCU's VDD, **backpowering** the MCU and potentially the entire 3.3V rail. This can cause:

- **Erratic startup** — the MCU starts up in an undefined state
- **Latch-up** — parasitic thyristors conduct, shorting VDD to ground
- **Damage** — if sustained

Defences:

- **Sequence power supplies** — apply 3.3V before any GPIO can be driven
- **Series resistors** — limit current into driven pins
- **Bus switches** (e.g., 74CB3Q3257) — disconnect pins during power-up

---

## Common Pitfalls and How to Avoid Them

### 1. Using 74HC instead of 74HCT

The classic mistake. **74HC requires VIH = 0.7 × VDD = 3.5V at 5V VDD**, but a 3.3V MCU outputs only 3.3V — below the threshold. The HC will randomly read 3.3V signals as low. **Always use 74HCT** when translating 3.3V → 5V.

### 2. Forgetting Pull-Ups on Open-Drain Signals

`INT_n`, `BUSRQ_n`, `NMI_n`, `WAIT_n` are open-drain (or quasi-bidirectional on the original Z80). Without pull-up resistors (~10K to VDD), they float at undefined levels. **Always add pull-ups** to open-drain inputs.

### 3. Driving the Data Bus at the Wrong Time

If the MCU drives `D[7:0]` while the Z80 is also driving it (during a write cycle, or when `RD_n` is high), **bus contention** occurs — both devices fight each other, causing high currents, voltage glitches, and potential damage.

**Solution**: Only drive the data bus when `RD_n` is low and the address matches your decode. Use a 74HCT245 with `OE_n` tied to `IORQ_n OR RD_n OR address_decode`.

### 4. Missing Wait States

Some MCUs are too slow to respond within the Z80's bus cycle. The Z80's `WAIT_n` input extends the cycle — assert it to give yourself more time. But excessive `WAIT_n` (more than ~10 cycles) can confuse some software.

**Solution**: Use PIO or DMA for cycle-precise response, avoiding the need for `WAIT_n`.

### 5. Power Sequencing Issues

Powering the 5V bus before the MCU is ready can cause backpowering (above). Powering the MCU before the 5V bus is stable can cause the MCU to read garbage.

**Solution**: Use a power-on reset supervisor (e.g., MCP100) to hold the MCU in reset until both supplies are stable.

### 6. Inadequate Ground Return

High-speed signals need a low-inductance ground return path. A long, thin ground wire (e.g., a single ground pin in a ribbon cable) creates a voltage drop that appears as noise on the signals.

**Solution**: Use multiple ground pins in the connector (e.g., every 8th pin of a ribbon cable), or a solid ground plane on the PCB.

### 7. Floating Inputs

An unconnected input (e.g., a spare GPIO not configured) floats at an undefined voltage, causing the input buffer to consume excess current and potentially oscillate.

**Solution**: Configure all unused GPIOs as either outputs (driven low) or inputs with pull-ups/pull-downs. Never leave inputs floating.

---

## FAQ

**Q: Can I use a level shifter for the entire Z80 bus at once?**

A: No. Bidirectional level shifters like the TXB0108 work for slow signals (SPI, I2C) but can't keep up with the Z80's nanosecond bus timing. Use dedicated 74HCT245 buffers per bus group (one for data, two for address).

**Q: Do I really need 12 mA drive strength?**

A: For short traces (< 5 cm), 4 mA is sufficient. For longer buses (ribbon cables, expansion port to external board), 12 mA plus a series termination resistor is safer.

**Q: How do I debug timing issues?**

A: A **logic analyser** (Saleae, Sigrok-compatible) is essential. Sample the bus at 50+ MHz and check setup/hold times against the Z80 datasheet. An **oscilloscope** shows analog characteristics (overshoot, ringing) that a logic analyser misses.

**Q: My adapter works with some Spectrums but not others. Why?**

A: Spectrum issue versions (2, 3, 4, 5, 6) have slightly different bus timings, buffer strengths, and pull-up values. Test on multiple Spectrums. The most common issue is bus timing margin being insufficient on faster issue 6 boards.

**Q: Can I use a single 74HCT245 for both reading and writing the data bus?**

A: Yes — that's the standard design. Tie `OE_n` to `address_decode AND (RD_n OR WR_n)`, and `DIR` to `RD_n`. When neither read nor write is active, the buffer is high-impedance. When reading, the buffer drives the bus from MCU to Z80. When writing, it drives from Z80 to MCU.

**Q: How do I handle the Z80's refresh cycles?**

A: During `RFSH_n` active (every opcode fetch), the Z80 is refreshing dynamic RAM. The MCU should ignore bus activity during refresh — `IORQ_n` and `MREQ_n` may pulse, but they're not real accesses. Add `RFSH_n` to your address decode logic.

**Q: Why does my adapter fail when the Spectrum is reset?**

A: During reset, the bus is in an undefined state for several milliseconds. The MCU may try to respond to garbage addresses. Add a long enough reset timeout (~100 ms) before enabling your bus interface.

**Q: Can I use software bit-banging instead of PIO for the Z80 bus?**

A: Probably not. Software bit-banging on a 133 MHz RP2040 takes ~6 cycles per GPIO operation, and a bus response requires 4-6 operations — that's ~30-40 cycles, or ~250 ns, close to the Z80's cycle budget. PIO is faster and deterministic.

---

## Summary

The key design patterns for MCU integration with retro hardware:

1. **Bus interfacing** — choose memory-mapped I/O, port I/O, or DMA based on the application; usually a bus slave responding to Z80 cycles
2. **Level shifting** — use 74HCT (not 74HC!) buffers for 3.3V → 5V translation; 74LVC or series resistors for 5V → 3.3V; manage power sequencing to avoid backpowering
3. **Timing-critical I/O** — use PIO (RP2040) or hardware timers (STM32) for cycle-precise bus responses; reserve interrupts for less time-critical events; understand jitter sources
4. **GPIO configuration** — set drive strength (12 mA for buses), slew rate (fast), and proper pull-ups for open-drain signals
5. **Software architecture** — state machines for subsystems, cooperative scheduler, ring buffers for producer-consumer, double buffering for displays, lock-free SPSC queues for inter-core communication
6. **Pin multiplexing** — start with constrained peripherals (ADC, SPI), assign PIO-driven signals next, use external latches/shift registers when pins run out
7. **Power supply** — multiple rails (5V, 3.3V), adequate current budget (~300 mA), proper decoupling (100 nF per IC), sequenced power-on to avoid backpowering
8. **Avoid pitfalls** — 74HCT not 74HC, pull-ups on open-drain, drive bus only when safe, handle refresh cycles, don't leave inputs floating

These patterns appear repeatedly in the [Z80](mcu_z80.md), [ULA](mcu_ula.md), [FDC](mcu_fdc_vg93.md), [PSG](mcu_psg_ay.md), [keyboard](mcu_keyboard.md), [video adapter](mcu_video_adapter.md), [SD interface](mcu_sd_interface.md), and [complete Spectrum](n_go.md) articles — they are the foundation of all MCU retro-computing projects.

---

## References

- **Zilog Z84C00 (Z80 CPU) Datasheet** — bus timing specifications, setup/hold times, output drive capabilities
- **Raspberry Pi RP2040 Datasheet** — PIO architecture, GPIO drive strength and slew rate, DMA channels, SIO multicore FIFO
- **Raspberry Pi Pico C/C++ SDK** — `gpio_set_drive_strength()`, `critical_section`, `multicore_fifo_*`, `__not_in_flash_func`
- **74HCT245 / 74HCT541 datasheets** (Texas Instruments, Nexperia, ST) — TTL-compatible thresholds, bidirectional transceivers
- **TXB0108 / TXS0108E datasheets** (Texas Instruments) — dedicated level translators for serial buses
- **ARM Cortex-M0+ Generic User Guide** — interrupt latency, BASEPRI, NVIC priorities
- **Jack Ganssle's "A Guide to Debouncing"** — practical input handling
- **Eli Hughes's embedded systems talks** — patterns for real-time firmware on ARM Cortex-M
- [Chris Smith's The ZX Spectrum ULA](http://www.zxdesign.info/) — bus timing details, contention pattern, refresh cycles
- **Retro-computing community wikis** — SpecNext, ZX-Uno, MiSTer, Harlequin, all apply these patterns
- **SparkFun and Adafruit level shifting tutorials** — beginner-friendly explanations of 3.3V/5V interfacing

## Cross-References

- [Z80 on MCU](mcu_z80.md) — MCU as bus master, cycle-stepped emulation, undocumented instructions
- [ULA on MCU](mcu_ula.md) — PIO-driven video generation, contended memory timing, floating bus
- [FDC (VG93) on MCU](mcu_fdc_vg93.md) — register interface, DRQ timing, SD card backend
- [PSG on MCU](mcu_psg_ay.md) — sample-rate audio generation, stereo output, multi-PSG
- [Keyboard on MCU](mcu_keyboard.md) — PS/2 protocol, matrix scanning, lock-free ring buffers
- [Video Adapter on MCU](mcu_video_adapter.md) — VGA/DVI/HDMI output via PIO and DMA, double buffering
- [SD Card Interface on MCU](mcu_sd_interface.md) — SPI protocol, FatFs, DivMMC memory-mapped interface
- [N-Go — Complete Spectrum on MCU](n_go.md) — bringing all the above together, multicore firmware architecture
- [FPGA Implementation](../fpga/fpga_implementation.md) — alternative approach using programmable logic instead of MCU
- [FPGA Timing Accuracy](../fpga/fpga_timing_accuracy.md) — timing considerations for FPGA recreations, comparison with MCU approaches
