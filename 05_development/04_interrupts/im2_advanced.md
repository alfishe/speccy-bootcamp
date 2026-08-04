[← Home](../../README.md) · [Interrupts](README.md)

# Advanced IM2 — Next, TS-Conf, Bank Switching, Sample-Rate ISRs

The classic Z80 IM2 model — one maskable interrupt source, a 257-byte vector table, one ISR per frame — is everything the stock Spectrum offers. Modern FPGA-based platforms (ZX Spectrum Next, TS-Conf on the ZX Evolution) extend this with **multiple prioritized interrupt sources** and per-source guaranteed vectors. This article covers the advanced patterns: Next hardware IM2 mode, TS-Conf's separate vectors, the copper-vs-ISR tradeoff, the canonical 128K bank-switching ISR pattern (Hudson Hawk, deep dive), and sample-rate ISRs driven by AY, Covox, or beeper PWM.

> [!NOTE]
> This article assumes you understand classic IM2 from [interrupt_programming.md](interrupt_programming.md) and the demoscene patterns in [im2_effects.md](im2_effects.md). The Next-specific content requires core 3.02 or later for the hardware IM2 mode.

---

## ZX Spectrum Next Hardware IM2 Mode

The Next's classic IM2 mode (when NextReg `#C0` bit 0 is clear) behaves like a standard Spectrum: one INT per frame, vector byte from the floating bus, 257-byte table recommended. With NextReg `#C0` bit 0 **set** (core 3.02+), the Next enters **hardware IM2 mode**, which is a different beast entirely.

### Enabling Hardware IM2 Mode

```z80
    LD   BC,#243B           ; NextReg select port
    LD   A,#C0              ; NextReg #C0 = interrupt control
    OUT  (C),A
    LD   B,#25              ; NextReg data port
    LD   A,#01              ; Bit 0 = enable hardware IM2 mode
    OUT  (C),A
```

Once enabled, each interrupt source has a **fixed, well-known vector byte**. The vector byte is no longer read from the floating bus. This means:
- A 256-byte vector table is sufficient (the `V = #FF` case never happens randomly)
- Different sources dispatch to different ISRs without polling
- The hardware tracks priority and pending state

### Interrupt Sources and Vectors

| Source | Vector byte (low nibble) | Default priority | Notes |
|---|---|---|---|
| ULA VBI (vertical blank) | `#01` | Highest | Equivalent to classic frame interrupt |
| Line interrupt | `#02` | High | Fires at scanline programmed in NextReg `#22` |
| ESP UART Tx | `#03` | Medium | Data sent to ESP32 coprocessor |
| ESP UART Rx | `#04` | Medium | Data received from ESP32 |
| Pi UART Tx | `#05` | Low | Raspberry Pi Zero send |
| Pi UART Rx | `#06` | Low | Raspberry Pi Zero receive |
| CTC timer 7 | `#07` | Variable | Programmable timer |
| CTC timer 8 | `#08` | Variable | Programmable timer |

The vector byte is OR'd with `(I × 256)` to form the table lookup address. So a VBI ISR with `I = #F0` would dispatch through table entry at `#F001`, while the line interrupt uses `#F002`, etc.

### Priority and Preemption

Higher-priority interrupts can **preempt** lower-priority ISRs. If the line-interrupt ISR is running and the ULA VBI fires, the VBI ISR runs inside the line-interrupt ISR. This is true hardware nested interrupt handling — impossible on classic Spectrum hardware.

The hardware tracks the chain state via the `RETI` instruction. **All returns in hardware IM2 mode must use `RETI`**, never plain `RET`. If you use `RET`, the hardware loses track of the priority chain and subsequent interrupts may not fire or may fire at wrong priority.

```z80
; Correct Next hardware IM2 ISR
vbi_isr:
    PUSH AF
    ; ... work ...
    POP  AF
    EI
    RETI                   ; MUST be RETI, not RET
```

### Comparison: Classic vs Hardware IM2

| Property | Classic IM2 | Next Hardware IM2 |
|---|---|---|
| Interrupt sources | 1 (ULA) | 8+ |
| Vector byte source | Floating bus (random) | Hardware (deterministic per source) |
| Vector table size | 257 bytes recommended | 256 bytes sufficient |
| Priority | None (single source) | Fixed, with preemption |
| Return instruction | `RET` works (RETI recommended) | `RETI` mandatory |
| Core version | Any | 3.02+ |
| Compatibility | All Spectrums | Next only |

### Worked Example — VBI + Line Interrupt

A common Next pattern: VBI runs the music player, line interrupt changes palette per scanline.

```z80
; --- Vector table setup ---
    DI
    LD   A,#F0
    LD   I,A
    ; Fill 256 bytes at #F000 with #01 for VBI default
    LD   HL,#F000
    LD   (HL),#01
    LD   DE,#F001
    LD   BC,#00FF
    LDIR
    ; Line interrupt entry at #F002 → ISR address
    LD   HL,#F002
    LD   (HL),line_isr_lo
    INC  HL
    LD   (HL),line_isr_hi
    ; VBI entry at #F001 → ISR address
    LD   HL,#F001
    LD   (HL),vbi_isr_lo
    INC  HL
    LD   (HL),vbi_isr_hi
    IM   2
    EI

; --- Enable line interrupt at scanline 64 ---
    LD   BC,#243B
    LD   A,#22             ; NextReg #22 = line interrupt line
    OUT  (C),A
    LD   B,#25
    LD   A,64
    OUT  (C),A

; --- VBI ISR (priority high) ---
vbi_isr:
    PUSH AF : PUSH BC : PUSH DE : PUSH HL
    PUSH IX : PUSH IY
    CALL music_player      ; ~1500 T-states
    POP  IY : POP  IX
    POP  HL : POP  DE : POP  BC : POP  AF
    EI
    RETI

; --- Line ISR (priority lower) ---
line_isr:
    PUSH AF
    LD   A,(palette_index)
    INC  A
    AND  #0F
    LD   (palette_index),A
    LD   BC,#243B
    OUT  (C),A
    LD   B,#25
    LD   A,(current_palette_value)
    OUT  (C),A
    POP  AF
    EI
    RETI
```

This pattern is impossible on classic Spectrums — you would have to manually check the frame counter inside the ISR to decide whether it is "VBI time" or "line time".

---

## TS-Conf Interrupt Vectors

The TS-Configuration (TS-Conf) is a configuration bitstream for the ZX Evolution board (Pentagon-based FPGA clone). It provides a similar multi-source IM2 model to the Next hardware IM2 mode, but with different register layout.

### TS-Conf Interrupt Sources

| Source | Register | Trigger |
|---|---|---|
| Frame interrupt | `INTLine` configured for last scanline | End of frame |
| Line interrupt | `INTLine` configured for any scanline | Beam reaches configured scanline |
| DMA completion | DMA controller status | Block transfer completes |

Each source has its own IM2 vector byte, so the ISR can dispatch without polling. The `INTLine` register also configures the **frame** interrupt position — unlike the standard Spectrum where the frame interrupt is fixed.

### TS-Conf ISR Pattern

```z80
; TS-Conf vector table (I = #F1)
; Frame:    #F1xx + vector byte from hardware
; Line:     #F1yy + different vector byte
; DMA done: #F1zz + yet another vector byte

    DI
    LD   A,#F1
    LD   I,A
    LD   HL,#F100
    LD   (HL),#40          ; Frame ISR low byte
    INC  HL
    LD   (HL),#F1          ; Frame ISR high byte (#F140 assumed)
    ; ... similar for line and DMA ...
    IM   2
    EI

frame_isr:
    PUSH AF
    CALL music_player
    POP  AF
    EI
    RETI

line_isr:
    ; ... per-scanline work ...
    EI
    RETI

dma_isr:
    ; ... chain next DMA transfer ...
    EI
    RETI
```

### DMA + ISR Pattern

The TS-Conf DMA controller can transfer RAM-to-RAM, RAM-to-device, or device-to-RAM autonomously. The DMA fires an interrupt on completion. A common pattern is double-buffered streaming:

```text
1. Frame ISR fires at frame end
2. Frame ISR starts DMA: copy bank 6 → screen bank
3. Main loop runs game logic, modifies bank 7
4. DMA completes → DMA ISR fires
5. DMA ISR starts next DMA: copy bank 7 → bank 6
6. Next frame: loop repeats
```

This pattern delivers "zero CPU cost" memory-to-screen transfers — impossible on classic Spectrums where every byte must be moved by the Z80 itself.

---

## Copper Coprocessor vs ISR

The Next's copper coprocessor is a tiny 32-instruction programmable state machine that can write to hardware registers at specific beam positions with **zero CPU cost**. Where you would normally write an ISR to change a palette entry mid-frame, you program the copper instead.

### Copper Capabilities

The copper has exactly two instructions:

- `WAIT x,y` — wait until beam reaches column `x`, scanline `y`
- `MOVE reg,val` — write `val` to hardware register `reg`

That is the entire ISA. No arithmetic, no branches, no memory access. But this is enough for an enormous range of effects.

### Decision Matrix — Copper vs ISR

| Effect | Copper | ISR | Winner |
|---|---|---|---|
| Per-scanline palette change | Yes, 32 instructions per scanline | Yes, but costs T-states | **Copper** |
| Per-scanline Layer 2 bank switch | Yes | Yes, but T-state cost | **Copper** |
| Per-scanline attribute write | No (attribute RAM not copper-writable) | Yes | **ISR** |
| Sprite table update | No (sprite RAM not copper-writable) | Yes | **ISR** |
| Music player | No (no code execution) | Yes | **ISR** |
| Game logic | No | Yes | **ISR** |
| Layer 2 priority change | Yes | Yes | **Copper** (zero CPU) |

The copper is strictly better for **hardware register writes** timed to beam positions. The ISR is strictly better for **RAM writes** and any code execution.

### Worked Example — Copper Palette Cycle

```text
; Copper program: cycle palette entry 0 through 4 colors per scanline
WAIT 0,64        ; Beam at top of paper
MOVE palreg[0],#03
WAIT 0,72
MOVE palreg[0],#07
WAIT 0,80
MOVE palreg[0],#0E
WAIT 0,88
MOVE palreg[0],#0C
; ... repeat for each scanline ...
```

This program changes palette entry 0 every 8 scanlines throughout the paper area, with zero CPU cost. The CPU is completely free for music, game logic, or anything else.

The equivalent ISR code would be:

```z80
; Without copper — ISR does the work
frame_isr:
    PUSH AF
    PUSH BC
    LD   B,24              ; 24 character rows
.row:
    CALL sync_to_next_scanline    ; ~200 T-states
    LD   A,(pal_index)
    INC  A
    LD   (pal_index),A
    LD   BC,#243B
    OUT  (C),A
    LD   B,#25
    LD   A,(pal_value)
    OUT  (C),A
    DJNZ .row              ; Total: ~5000 T-states
    POP  BC
    POP  AF
    EI
    RETI
```

The ISR version costs 5,000 T-states per frame and requires per-scanline synchronization. The copper version costs zero T-states and is hardware-precise.

---

## 128K Bank-Switching ISR — The Hudson Hawk Pattern Deep Dive

The Hudson Hawk pattern (introduced in [im2_effects.md](im2_effects.md)) is the canonical solution for ISRs that need to access data in a different RAM bank than the main program. This section covers it in full detail.

### The Problem

On 128K Spectrums, port `#7FFD` selects which 16 KB RAM bank is paged at `#C000`–`#FFFF`. The main program might have bank 0 paged for game-state work, while the music player lives in bank 3. The ISR has no way to know which bank is currently paged.

Worse: `#7FFD` is **write-only**. There is no `IN A,(#7FFD)` to read back the current state. The ISR must track the bank in software.

### The Shadow Variable Solution

Maintain a RAM variable (the "shadow") that always contains the next value to be written to `#7FFD`. Update this variable **before** the actual `OUT`:

```z80
; Banking shadow variable
bank_shadow:    DB  #10

; Switch bank routine
switch_bank:
    ; A = new bank number (0-7)
    LD   (desired_bank),A
    LD   A,(bank_shadow)   ; Current value
    AND  #38              ; Preserve other bits (screen, ROM select)
    OR   (desired_bank)   ; Combine with new bank
    OR   #10              ; Bit 4 = use ROM 0
    LD   (bank_shadow),A  ; *** Update shadow FIRST ***
    LD   BC,#7FFD
    OUT  (C),A            ; Then actually switch
    RET

desired_bank:  DB  0
```

The critical ordering: shadow write **before** `OUT`. This guarantees that if an interrupt fires between the shadow write and the `OUT`, the ISR will read the correct desired bank state from the shadow.

### The ISR Bank Save/Restore

```z80
im2_isr:
    ; --- Prologue ---
    PUSH AF : PUSH BC : PUSH DE : PUSH HL
    PUSH IX : PUSH IY

    ; Save current bank
    LD   A,(bank_shadow)
    PUSH AF               ; Save current shadow value

    ; Switch to ISR's working bank (e.g. bank 3 for music)
    LD   A,(bank_shadow)
    AND  #F8              ; Clear bank bits
    OR   #03              ; Set bank 3
    LD   (bank_shadow),A
    LD   BC,#7FFD
    OUT  (C),A

    ; --- ISR body ---
    CALL music_player     ; Music lives in bank 3
    ; ... other ISR work ...

    ; --- Epilogue ---
    POP  AF               ; Restore saved shadow value
    LD   (bank_shadow),A
    LD   BC,#7FFD
    OUT  (C),A            ; Switch back to main program's bank

    POP  IY : POP  IX
    POP  HL : POP  DE : POP  BC : POP  AF
    EI
    RETI
```

### Why You Cannot Read Back #7FFD

The `#7FFD` port is wired to a 74LS273 latch on the 128K motherboard. The latch takes input from the data bus on a write cycle but does not drive the data bus on a read cycle. Attempting to `IN A,(#7FFD)` returns whatever happens to be on the data bus — typically stale data from the previous memory cycle.

The +2A/+3's `#1FFD` port has the same limitation. The Hudson Hawk shadow-variable technique is the only way to track banking state across interrupts.

---

## Sample-Rate ISRs

The standard Spectrum frame rate is 50 Hz. For digital audio playback, this is too slow — most sample playback needs 8-20 kHz. The technique for high-rate ISRs is to drive the interrupt from a faster source than the ULA.

### AY Interrupt as Sample-Rate Trigger

The AY-3-8912 sound chip has a 5-cycle envelope generator that can be configured to assert its IRQ output at programmable intervals. The 128K machines wire this IRQ to the maskable interrupt line.

By setting the AY envelope period to a short value and enabling the IRQ output, you can get interrupts at 100 Hz, 200 Hz, or higher — independent of the video frame rate.

```z80
; --- Configure AY for 200 Hz interrupt ---
    LD   BC,#FFFD          ; AY register select port
    LD   A,#0B             ; Register 11 = envelope period fine
    OUT  (C),A
    LD   B,#BF
    LD   A,Expression      ; Period for 200 Hz
    OUT  (C),A
    LD   B,#FF
    LD   A,#0C             ; Register 12 = envelope period coarse
    OUT  (C),A
    LD   B,#BF
    LD   A,#00
    OUT  (C),A
    LD   B,#FF
    LD   A,#0D             ; Register 13 = envelope shape
    OUT  (C),A
    LD   B,#BF
    LD   A,#0A             ; Continue shape (cycles IRQ)
    OUT  (C),A
    LD   B,#FF
    LD   A,#0E             ; Register 14 = I/O port A (unused)
    OUT  (C),A
    LD   B,#BF
    LD   A,#FF
    OUT  (C),A
```

This produces an interrupt at ~200 Hz instead of 50 Hz. The ISR then writes one byte per interrupt to a Covox DAC or to the AY's amplitude register, producing sample playback.

### Covox / SounDrive DAC Output

The Covox is a simple 8-bit DAC attached to a parallel port. Writing a byte to the DAC port produces an instantaneous voltage. Sample playback is just `LD A,(sample); OUT (port),A` inside the ISR.

```z80
; 200 Hz Covox sample playback
covox_isr:
    PUSH AF
    PUSH HL
    LD   HL,(sample_ptr)
    LD   A,(HL)
    OUT  (#FB),A           ; Covox port (varies by interface)
    INC  HL
    LD   (sample_ptr),HL
    POP  HL
    POP  AF
    EI
    RETI

sample_ptr:  DW sample_data
```

The ISR costs ~50 T-states. At 200 Hz, that is 10,000 T-states per second — about 0.3% of the CPU.

### 1-bit Beeper PWM

On the 48K Spectrum (no AY, no Covox), the only audio output is the 1-bit beeper at port `#FE`. Sample playback requires **pulse-width modulation**: rapidly toggling the beeper bit at a rate much faster than the sample rate, with the duty cycle proportional to the sample value.

PWM ISRs run at 10-30 kHz — far faster than the 50 Hz frame rate. They require a custom timer source (CTC on the Next, or cycle-counted main-loop polling on stock hardware). This is the domain of beeper music engines like WHAM, Qchan, and Special FX.

The ISR cost is significant: a 20 kHz PWM ISR with 8-bit resolution needs 8 toggles per sample, each costing ~20 T-states. That is 160 T-states per sample × 20,000 samples/sec = 3,200,000 T-states/sec — **91% of the CPU**. Beeper engines are the most timing-critical code on the platform.

---

## Multi-ISR Chaining on Stock Hardware

A frequently asked question: can you have **two** maskable ISRs on a classic Spectrum — one for music, one for raster effects?

The answer is **no, not without hardware support**. The Z80 has exactly one maskable interrupt input. The standard ULA drives it once per frame. There is no way to insert a second interrupt at a different point in the frame.

The workaround is to chain effects inside a single ISR:

```z80
im2_isr:
    PUSH AF
    ; ... music player ...
    ; ... check frame counter, do effect A on even frames, B on odd frames ...
    POP  AF
    EI
    RETI
```

This is what every commercial IM2 game does. The Next's hardware IM2 mode (see above) is the only way to get true multi-ISR on a Spectrum.

---

## Cross-References

- **[interrupt_programming.md](interrupt_programming.md)** — Foundational IM2 mechanics
- **[im2_effects.md](im2_effects.md)** — Demoscene ISR patterns including the basic Hudson Hawk bank-switching intro
- **[race_the_beam.md](race_the_beam.md)** — Cycle-counted raster effects (the line-interrupt alternative)
- **[nmi.md](nmi.md)** — NMI handling, which follows the same register-preservation rules
- **[video_frame_next.md](../05_display_and_timing/video_frame_next.md)** — Next-specific timing, line interrupt configuration
- **[memory_and_io_next.md](../03_memory_and_io/memory_and_io_next.md)** — Next's full memory and I/O map including NextReg ports
- **[ay_3_8912.md](../../06_sound/hardware/ay_3_8912.md)** — AY register access, envelope period configuration
- **[bank_switching_patterns.md](../03_memory_and_io/bank_switching_patterns.md)** — 128K paging patterns (the foundation for the Hudson Hawk technique)

## Sources

- *Interrupts - SpecNext Wiki* (wiki.specnext.dev) — authoritative reference for Next hardware IM2 mode, core version requirements, and per-source vectors
- *[ZX Spectrum Next Regs Reference* (gitlab.com/SpectrumNext) — NextReg `#22` and `#C0` documentation](https://specnext.dev/)
- *[TS-Conf](https://zxevo.ru/) documentation* (zxevo.org) — TS-Conf interrupt and DMA registers
- *Hudson Hawk disassembly* (via zxspectrumcoding.wordpress.com) — Jim Bagley's bank-switching ISR pattern
- *AY-3-8910/8912 Data Manual* (Microchip) — envelope period calculation for sample-rate interrupts
- *[Arkos Tracker](https://www.julien-nevo.com/arkostracker/) documentation* (julien-nevo.com) — patterns for high-rate music ISRs
