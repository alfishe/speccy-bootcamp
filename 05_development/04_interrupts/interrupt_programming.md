[← Home](../../README.md) · [Interrupts](README.md)

# Interrupt Programming — Practical Guide for the ZX Spectrum

The ZX Spectrum has a single interrupt source: the ULA asserts the INT line once per video frame (50 Hz on all Sinclair models). This 50 Hz heartbeat drives everything smooth — animation, music, raster effects, keyboard scanning. Programs that ignore interrupts are limited to BASIC-speed interactions; programs that master them unlock the machine's full potential.

This article covers **how to write interrupt handlers on real Spectrum hardware** — IM1 and IM2 setup, ISR design patterns, timing constraints, and cookbook examples. For the CPU-level interrupt architecture (IFF1/IFF2, bus cycles, acknowledge timing), see [z80_interrupts.md](../../01_cpu/z80_interrupts.md).

---

## Interrupt Sources on the Spectrum

### ULA Frame Interrupt (All Models)

The Ferranti ULA generates a **single maskable interrupt per video frame**. On the 48K Spectrum, the timing is:

| Parameter | 48K | 128K / +2 | +2A / +3 | Pentagon |
|-----------|-----|-----------|----------|----------|
| Frame rate | ~50.08 Hz | ~50.01 Hz | ~50.01 Hz | ~48.83 Hz |
| INT asserted at | T-state 0 | T-state 0 | T-state 0 | T-state 67,968 (line 304) |
| INT duration | 32 T-states | 32 T-states | ~36 T-states | 32 T-states |
| Total T-states/frame | 69,888 | 70,908 | 70,908 | 71,680 |

The interrupt fires at the **start of the top border** on all Sinclair/Amstrad models — not at the start of the paper area. On 48K, there are 64 uncontended scanlines (14,336 T-states) between INT and the first visible pixel row. This is the programmer's primary time window for ISR setup work.

> [!NOTE]
> The **Pentagon** is different: INT fires near the **end** of the frame (T-state 67,968, line 304 of 320), not at the start. This means the ISR runs during the bottom border, and the "safe time" before paper is only 48 scanlines (10,752 T-states) at the start of the *next* frame. Code that assumes `HALT` returns at the top of the frame will need adjustment. However, this late-INT position is actually **advantageous** for game and demo developers: by the time the ISR fires, the current frame's paper area (lines 48–239) has already been fully rendered, so ISR work never competes with active display rendering. Combined with the Pentagon's **zero contention**, the developer has a generous and predictable time window — ISR code runs at full speed regardless of what memory it accesses. See [clone_timing.md](../../02_hardware/clones/clone_timing.md) for details.

### AY-3-8912 (128K Models)

The 128K / +2 machines include an AY-3-8912 programmable sound generator. The 128K ROM uses it for `PLAY` commands and `BEEP` (which outputs through the AY on 128K rather than the beeper), but this is done **synchronously** — the ROM writes tone parameters to the AY registers directly and busy-waits for note duration. The AY chip has an interrupt output pin, but the standard ROMs **never enable it**. Custom software can configure the AY to generate interrupts (e.g., for sample-rate audio playback or high-precision timing), but this requires IM2 and direct AY register programming. For the full 128K ROM feature set, see [rom_128k.md](../../04_operating_systems/rom_128k.md).

### Peripheral and Extended Hardware Interrupts

The original 48K Spectrum has only one interrupt source (the ULA frame interrupt). Add-on hardware and later clone machines add more:

#### Classic Add-ons

- **Interface 1**: Can generate interrupts for RS232 data reception. Rarely used by commercial software.
- **Multiface 128 / Multiface 3**: Uses **NMI** (non-maskable), not INT — see below.
- **MB02+, DivIDE, DivMMC**: Disk interfaces may assert INT for disk I/O completion or NMI for the "magic button" trap.
- **General Sound / NeoGS**: A sound coprocessor card with its own Z80 CPU. The host sends commands via a shared queue; the card can assert **INT on completion** or when its output buffer needs refilling. This lets the host sleep in `HALT` and wake only when the card needs attention — far cheaper than polling. The card's Z80 handles all audio mixing; the host CPU is free for game logic.

#### ZX Spectrum Next (TBBlue / FPGA)

The Next extends the interrupt system significantly beyond the standard ULA frame interrupt:

- **Line interrupt**: Programmable scanline-based interrupt via NextReg `$22`. Fires at a specific raster line, enabling per-scanline effects without CPU timing loops. Can be positioned anywhere in the frame. The ISR typically updates palette, scrolling, or copper instructions for the next line.
- **Copper coprocessor**: A tiny programmable state machine (32 instructions, `WAIT` + `MOVE`) that writes to hardware registers at precisely defined raster positions. Not an interrupt source itself, but eliminates the need for many interrupt-driven timing techniques — where you'd normally write a line-interrupt ISR to change a register mid-frame, the copper does it autonomously with zero CPU cost.
- **Hardware IM2 mode** (core 3.02+): Multiple prioritized interrupt sources, each with a guaranteed IM2 vector:
  - ULA frame interrupt (VBI)
  - Line interrupt (VBL)
  - ESP UART transmit/receive
  - Raspberry Pi UART transmit/receive
  - CTC timer channels (2 programmable timers)
  Higher-priority interrupts can preempt lower-priority handlers. All returns must use `RETI` so hardware tracks the chain state.
- **Sprite and tile hardware**: Up to 85 sprites per line, tilemaps, and hardware scrolling. These do not generate interrupts — they are autonomous rendering engines. However, sprite initialization and dynamic updates must still be synchronized with the frame via the ULA or line interrupt. A common pattern: ISR fires at frame start → reload sprite position/attribute tables for the next frame.

#### TS-Conf (ZX Evolution)

The TS-Configuration for ZX Evolution provides:

- **Programmable interrupt position**: The INT line can be configured to fire at any scanline via the `INTLine` register, not just at frame start. This replaces the fixed ULA INT position.
- **Separate IM2 vectors**: Different interrupt sources (frame, line, DMA) each get their own IM2 vector, so the ISR can dispatch without polling.
- **DMA controller**: DRAM-to-DRAM, DRAM-to-device, and device-to-DRAM transfers operate autonomously. The DMA controller generates an **interrupt on completion** — the ISR can chain the next transfer or signal the main loop.
- **Hardware sprites and tiles**: Up to 85 sprites per line, multiple sprite/tile planes. These do not generate interrupts, but sprite descriptor writes must be synchronized with line interrupts to avoid tearing. Typical pattern: line-interrupt ISR reloads the sprite table for the next frame region.

#### Other FPGA Platforms

- **ZX-Uno**: Configurable Spectrum-on-FPGA. Supports ULAplus, Timex modes, and configurable contention. Interrupt sources depend on the loaded core.
- **Sizif-512**: A standalone CPLD-based (Altera EPM1270) ZX Spectrum clone that fits in a 48K rubber case. Supports four machine modes — **Pentagon 128**, **Spectrum 128**, **Spectrum 48**, and **Spectrum +3e** — selectable at runtime. Includes 512K RAM, real AY-3-8910, ULAplus, and integrated DivMMC. The interrupt behavior follows whichever machine mode is active (Pentagon timing in Pentagon mode, standard ULA timing in 128/48 modes).

> [!NOTE]
> These extended interrupt sources are only available on their specific hardware. Software that targets them must detect the hardware first (via identification registers) and provide fallback code paths for standard Spectrum models.

---

## IM1 — The Default Mode

IM1 is the only interrupt mode the standard ROM uses. When the ULA asserts INT, the Z80 unconditionally calls `RST #38` — execution jumps to address `#0038`. The 48K ROM places its interrupt service routine (ISR) here, which updates the frame counter and scans the keyboard.

### The ROM Handler at #0038

The 48K ROM ISR does two things every frame:

1. **Increments `FRAMES`** (3-byte counter at `#5C78`–`#5C7A`) — the 24-bit uptime counter used by `PAUSE` and tape loading
2. **Scans the keyboard** — reads all 8 half-rows and updates `KSTATE` (`#5C00`–`#5C07`) and `LAST_K` (`#5C08`)

> [!NOTE]
> The FLASH attribute (bit 7 of each attribute byte) is **not** handled by the ROM ISR. It is implemented entirely in hardware by the ULA, which has an internal counter that toggles ink and paper for all flashing cells every 16 frames (~320 ms at 50 Hz). No CPU intervention is required.

The ROM handler costs approximately **700 T-states** per frame — about 1% of the 69,888 T-state budget on 48K.

### Hooking the ROM Handler

Since `#0038` is in ROM, you cannot directly overwrite it on a standard Spectrum. There are three strategies for installing a custom IM1 handler:

#### Strategy 1: Patch the RST #38 Vector (48K only)

On the 48K Spectrum, `#0038` is in ROM and cannot be patched. However, `RST #38` is an unconditional call — it always jumps to `#0038`. The only way to redirect it is to replace the ROM with RAM (rare hardware mod) or use IM2 instead.

On machines with RAM shadowed at `#0000` (some clones, or after `NEW` on 128K in RAM page 0), you can write a `JP` instruction:

```z80
; Only works if #0000-#3FFF is RAM (not ROM)
    LD   A,#C3           ; JP opcode
    LD   (#0038),A
    LD   HL,my_isr
    LD   (#0039),HL
    EI
```

#### Strategy 2: Use the ROM's Own Hook Point

The 128K ROMs have hook points designed for this purpose. The 128K ROM 0 handler at `#0038` reads a vector from system variable space and calls through it. This is the **recommended** approach for 128K/+2/+2A/+3 software:

```z80
; 128K ROM 0 uses a vector at a known location
; Check the specific ROM version for the exact hook address
; ROM 0 typically calls through a vector that can be redirected
```

#### Strategy 3: Replace ROM with RAM (128K paging)

The 128K machines can page any RAM bank into slot 0 (`#0000`–`#3FFF`). This lets you place your own handler at `#0038`:

```z80
; Page RAM bank into slot 0, install handler, page ROM back
    DI
    LD   BC,#7FFD
    LD   A,#10 + bank    ; Bit 4 = 1 selects RAM in slot 0
    OUT  (C),A            ; Bank is now in #0000-#3FFF
    LD   A,#C3
    LD   (#0038),A
    LD   HL,my_isr
    LD   (#0039),HL
    LD   A,#10 + 0        ; ROM 0 back in slot 0 (or appropriate ROM)
    OUT  (C),A
    EI
```

> [!WARNING]
> After paging ROM out, you lose all ROM routines — `RST #10`, `PRINT`, tape loading, etc. Make sure your code doesn't depend on them, or that you restore ROM before calling any ROM routine.

### Minimal IM1 Handler

If you control address `#0038` (via RAM paging or a clone with writable low memory), the minimal useful handler is:

```z80
my_isr:
    PUSH AF              ; 11T — must save at minimum AF
    LD   HL,(#5C78)     ; 16T — read FRAMES
    INC  HL              ; 6T
    LD   (#5C78),HL     ; 16T — update FRAMES
    PUSH HL
    LD   A,H
    OR   L
    JR   nz,.no_carry   ; 12/7T
    LD   HL,#5C7A
    INC  (HL)            ; 11T — increment high byte
.no_carry:
    POP  HL
    POP  AF
    EI                   ; 4T — re-enable before return
    RET                  ; 10T
```

This preserves the FRAMES counter (needed by tape loading and `PAUSE`) while keeping overhead low. If you don't need ROM compatibility at all, you can skip the FRAMES update.

---

## IM2 — Vectored Interrupts

IM2 is the preferred mode for custom interrupt handlers on the Spectrum. Instead of hardwiring to `#0038`, the Z80 uses a **vector table** to look up the handler address. This gives you full control without needing to patch ROM or page RAM into slot 0.

### The Floating Bus Problem

In IM2, the Z80 expects the interrupting device to place a **vector byte** on the data bus during the interrupt acknowledge cycle. The Z80 then forms a 16-bit table address from `I × 256 + vector_byte` and reads two bytes from that address to find the handler.

On the ZX Spectrum, **no device drives the data bus during interrupt acknowledge**. The ULA asserts the INT line but has no mechanism to place a vector byte on the bus. The byte the Z80 reads is whatever residual charge was left on the bus from the previous memory or I/O cycle.

In practice, this value is **usually `#FF`** due to passive pull-up resistors on the data bus. However, this is not guaranteed:

- After a `LD A,(HL)` that read `#3E` from address `#FFFF`, the bus may still hold `#3E` when the interrupt fires a few T-states later
- After an `OUT (#FE),A` that wrote border color `#02`, the bus may hold `#02`
- After a refresh cycle or certain instruction sequences, the value can be nearly anything

On **real hardware**, the floating bus value tends to correlate with the last byte that was on the data bus before the interrupt acknowledge. Emulators that hardcode `#FF` may mask bugs that would crash on real machines.

**Conclusion**: the vector byte is **unreliable** — your vector table must handle **all 256 possible values** (`#00`–`#FF`).

### Why 257 Bytes — Not 256

The Z80 reads a **pair of consecutive bytes** from the vector table to form the handler address: the byte at `I × 256 + V` is the low byte, and the byte at `I × 256 + V + 1` is the high byte.

When `V = #FF`, the second read goes to `I × 256 + #FF + 1 = (I + 1) × #00` — it **crosses into the next 256-byte page**.

```
With I = #FE:
  V = #00 → read #FE00 (lo), #FE01 (hi)
  V = #01 → read #FE01 (lo), #FE02 (hi)
  ...
  V = #FE → read #FEFE (lo), #FEFF (hi)
  V = #FF → read #FEFF (lo), #FF00 (hi)  ← crosses page!
```

A 256-byte table at `#FE00`–`#FEFF` would leave the `V = #FF` case reading an **undefined byte** at `#FF00`. The table must be **257 bytes**: `#FE00`–`#FF00` (inclusive).

### The Correct Table Fill — One Value, 257 Bytes

The standard solution: fill all 257 bytes with the **same value**. If every byte in the table is `#FD`, then for any vector byte `V`:

```
  Lo byte at table[V]   = #FD
  Hi byte at table[V+1] = #FD
  Handler address       = #FDFD
```

Walkthrough for three specific cases:

```
Case 1: V = #FF (most common — pull-up resistors)
  Address = #FE × 256 + #FF = #FEFF
  Lo = byte at #FEFF = #FD
  Hi = byte at #FF00 = #FD  (257th byte!)
  → Jump to #FDFD ✓

Case 2: V = #7E (after reading attribute byte #7E)
  Address = #FE × 256 + #7E = #FE7E
  Lo = byte at #FE7E = #FD
  Hi = byte at #FE7F = #FD
  → Jump to #FDFD ✓

Case 3: V = #00 (after ROM NOP cycles)
  Address = #FE × 256 + #00 = #FE00
  Lo = byte at #FE00 = #FD
  Hi = byte at #FE01 = #FD
  → Jump to #FDFD ✓
```

### Why the Alternating-Pattern Trick Is Wrong

A common misconception: fill the table with alternating bytes `#00, #FD, #00, #FD, ...` to create a handler at `#FD00`. This **only works for even vector bytes**:

```
Table: #FE00=#00, #FE01=#FD, #FE02=#00, #FE03=#FD, ...

V = #00 → reads #FE00(#00), #FE01(#FD) → handler #FD00 ✓
V = #01 → reads #FE01(#FD), #FE02(#00) → handler #00FD ✗ CRASH
V = #02 → reads #FE02(#00), #FE03(#FD) → handler #FD00 ✓
V = #03 → reads #FE03(#FD), #FE04(#00) → handler #00FD ✗ CRASH
```

Odd vector bytes jump to `#00FD` — which is in ROM and will crash or behave unpredictably. This bug is invisible in emulators that always return `#FF` (an even value), but **will crash on real hardware** when the floating bus returns an odd value.

### IM2 Setup

```z80
; Set up IM2 — handler at #FDFD, vector table at #FE00 (257 bytes)
IM2_Init:
    DI                   ; Disable interrupts during setup
    LD   A,#FE           ; I register → table at #FE00
    LD   I,A
    
    ; Fill 257 bytes (#FE00-#FF00) with #FD
    ; All vectors → handler at #FDFD
    LD   HL,#FE00
    LD   (HL),#FD        ; First byte
    LD   DE,#FE01        ; Destination = next byte
    LD   BC,#0100        ; 256 more bytes (257 total)
    LDIR                 ; Fill #FE01-#FF00 with #FD
    
    IM   2               ; Switch to IM2
    EI                   ; Re-enable interrupts
    RET
```

The handler is placed at `#FDFD`:

```z80
    ORG  #FDFD
im2_handler:
    PUSH AF              ; 11T
    PUSH BC              ; 11T
    PUSH DE              ; 11T
    PUSH HL              ; 11T
    ; ... your code here ...
    POP  HL              ; 10T
    POP  DE              ; 10T
    POP  BC              ; 10T
    POP  AF              ; 10T
    EI                   ; 4T — re-enable
    RETI                 ; 14T — RETI signals Z80 peripherals (optional
                         ;        on Spectrum, RET works too)
```

### IM2 Overhead

| Operation | T-states |
|-----------|----------|
| Interrupt acknowledge (IM2) | 19 |
| Vector table read (2 bytes) | 15 |
| `PUSH AF/BC/DE/HL` | 44 |
| `POP HL/DE/BC/AF` | 40 |
| `EI` | 4 |
| `RETI` | 14 |
| **Total overhead** | **136** |

IM2 costs **65 more T-states** than a minimal IM1 handler (136 vs 71) due to the vector table lookup. For most purposes this is negligible — 136 T-states is 0.2% of the frame budget.

### Table Placement Trade-offs

The handler address is fixed by the fill byte. If you fill with `#FD`, the handler goes at `#FDFD`. Different fill bytes give different handler addresses:

| Fill byte | Handler address | Contended on 48K? | Notes |
|-----------|----------------|-------------------|-------|
| `#FD` | `#FDFD` | Yes (`#4000`–`#7FFF`) | Handler runs slower during paper display |
| `#80` | `#8080` | No (`#8000`–`#FFFF`) | Preferred — full speed in uncontended RAM |
| `#90` | `#9090` | No | Same, different address |
| Any `#xx` | `#xxxx` | Depends on address | `#8000`–`#FFFF` = uncontended |

To place the handler in uncontended RAM, fill the table with a value `>= #80`:

```z80
; Handler in uncontended RAM at #9090
    LD   A,#FE
    LD   I,A
    LD   HL,#FE00
    LD   (HL),#90        ; All vectors → #9090
    LD   DE,#FE01
    LD   BC,#0100        ; 257 bytes total
    LDIR
    IM   2
    EI
    RET
    
    ORG  #9090
im2_handler:
    ; ... runs at full speed even during paper display ...
```

The table itself always occupies `#FE00`–`#FF00` (257 bytes) when `I = #FE`. This area is typically free — the UDG area starts at `#FF58`, leaving `#FE00`–`#FF57` unused by BASIC. The single byte at `#FF00` is the 257th byte that handles the `V = #FF` case.

> [!NOTE]
> On the Pentagon and some clones, the floating bus value is deterministic (always `#FF`). In theory you only need one vector table entry. However, for portability, always fill all 257 bytes — it costs only 257 bytes of RAM and guarantees correct behavior on all hardware.

---

## ISR Design Patterns

### The Minimal Handler (Shadow Registers)

The fastest possible handler uses shadow registers instead of `PUSH`/`POP`, saving 40 T-states of overhead:

```z80
fast_isr:
    EX   AF,AF'          ; 4T — save AF
    EXX                   ; 4T — save BC, DE, HL
    ; ... minimal work using shadow set ...
    LD   HL,(frame_cnt)
    INC  HL
    LD   (frame_cnt),HL
    EXX                   ; 4T — restore BC, DE, HL
    EX   AF,AF'          ; 4T — restore AF
    EI                    ; 4T
    RET                   ; 10T
; Total overhead: 30T (vs 71T with PUSH/POP AF/BC/DE/HL)
```

This is ideal for music players and frame counters. The limitation: you cannot use `EXX` or `EX AF,AF'` in your main code, since the ISR will corrupt them.

### The Full Handler (All Registers)

When the ISR needs index registers or shadow registers for its own work:

```z80
full_isr:
    PUSH AF               ; 11T
    PUSH BC               ; 11T
    PUSH DE               ; 11T
    PUSH HL               ; 11T
    PUSH IX               ; 15T
    PUSH IY               ; 15T
    EX   AF,AF'           ;  4T
    EXX                   ;  4T
    PUSH AF               ; 11T
    PUSH BC               ; 11T
    PUSH DE               ; 11T
    PUSH HL               ; 11T
    ; ... ISR has full use of all registers ...
    POP  HL               ; 10T
    POP  DE               ; 10T
    POP  BC               ; 10T
    POP  AF               ; 10T
    EXX                   ;  4T
    EX   AF,AF'           ;  4T
    POP  IY               ; 14T
    POP  IX               ; 14T
    POP  HL               ; 10T
    POP  DE               ; 10T
    POP  BC               ; 10T
    POP  AF               ; 10T
    EI                     ;  4T
    RET                    ; 10T
; Total overhead: 252T
```

This is expensive — 252 T-states before any actual work. Only use it when the ISR genuinely needs all registers. Most handlers can get away with saving only `AF`, `BC`, `DE`, `HL` (71T overhead).

### Deferred Processing

Instead of doing all work in the ISR, set a flag and let the main loop handle it:

```z80
isr_flag:  DB  0

minimal_isr:
    PUSH AF
    LD   A,1
    LD   (isr_flag),A     ; Signal: frame has occurred
    POP  AF
    EI
    RET

; --- Main program loop ---
main_loop:
    HALT                   ; Wait for next frame
    LD   A,(isr_flag)
    OR   A
    JR   Z,main_loop       ; No flag? (shouldn't happen after HALT)
    XOR  A
    LD   (isr_flag),A      ; Clear flag
    ; ... do all frame processing here, with full register access ...
    JR   main_loop
```

This pattern is the most common in games — the ISR does almost nothing (just a flag), and the main loop does all the work with full register access and no timing pressure.

### Multi-Effect Handler

A single ISR can drive multiple independent systems by maintaining separate counters:

```z80
frame_cnt:  DW  0          ; 16-bit frame counter
music_ptr:  DW  music_data  ; Current music position
effect_tog: DB  0          ; Toggle for alternating effects

multi_isr:
    PUSH AF
    PUSH HL
    
    ; 1. Frame counter (always)
    LD   HL,(frame_cnt)
    INC  HL
    LD   (frame_cnt),HL
    
    ; 2. Music player (always, every frame)
    ; CALL play_note       ; Call your music routine
    
    ; 3. Alternating effects (every other frame)
    LD   A,(effect_tog)
    XOR  1
    LD   (effect_tog),A
    JR   Z,.even_frame
    ; Odd frame: update sprites
    JR   .done
.even_frame:
    ; Even frame: update attributes
.done:
    POP  HL
    POP  AF
    EI
    RET
```

---

## Timing Considerations

### Jitter and Alignment

The interrupt fires at a fixed point in the frame (T-state 0 on 48K), but your handler doesn't start executing instantly. The latency from INT assertion to the first instruction of your handler depends on:

1. **Interrupt acknowledge**: 13T (IM1) or 19T (IM2)
2. **Current instruction completion**: The Z80 finishes the current instruction before servicing INT. Worst case: `LDIR` at 21T/block, or `INIR/OTIR` at 21T
3. **Contention**: If the current instruction or the stack write is in contended memory, additional wait states are added

Typical jitter is **±10–20 T-states** depending on where in the main loop the interrupt catches the CPU. For multicolor effects that need single-scanline precision, you must synchronize after entering the ISR:

```z80
; Precise raster sync after entering ISR
precise_isr:
    PUSH AF
    ; We entered ISR at approximately T-state 13-33 (IM1)
    ; To hit a specific scanline, wait for it:
    LD   BC,#7FFD        ; Any port that doesn't harm
.sync:
    DEC  B                ; 4T
    JP   nz,.sync        ; 10T = 14T per iteration
    ; Now we're aligned — execute timing-critical code
    POP  AF
    EI
    RET
```

### Contention in the ISR

The ISR runs in whatever T-state window the interrupt fires — on 48K, this is the top border (T-states 0–14,335), which is **uncontended**. This means your ISR code runs at full speed during top border.

However, if your ISR is long enough to run into the paper area (T-state 14,336+), any access to `#4000`–`#7FFF` (screen memory and system variables) will be contended. Code executing from contended ROM (`#0000`–`#3FFF`) is also affected.

```z80
; Safe: ISR runs during top border — no contention
; All of #4000-#FFFF is freely accessible at full speed

; Dangerous: ISR runs past top border into paper area
; Accesses to #4000-#7FFF now have contention delays
; LDIR copying to screen RAM will be 20-50% slower
```

### The HALT Instruction

`HALT` puts the CPU to sleep executing `NOP` cycles until an interrupt fires. It's the simplest way to synchronize with the frame:

```z80
; Wait for next frame
    HALT              ; CPU sleeps until INT
    ; First instruction executes 4T after INT wakes the CPU
```

`HALT` is position-independent — it doesn't matter where in the frame you are when you execute it. The CPU simply waits for the next INT. Note that during `HALT`, the CPU still generates refresh cycles and the bus is active — contention still applies to the NOP cycles if the HALT instruction itself is in contended memory.

### Per-Model Timing Differences

| Concern | 48K | 128K / +2 | +2A / +3 | Pentagon |
|---------|-----|-----------|----------|----------|
| Frame T-states | 69,888 | 70,908 | 70,908 | 71,680 |
| Contention model | Standard ULA | Same as 48K | +2A specific | None |
| INT duration | 32T | 32T | ~36T | 32T |
| Bank switching in ISR | N/A | Must preserve BANK_M | Same as 128K | N/A (no banking) |

The 128K machines add a critical concern: **bank switching in the ISR**. If your ISR needs to access data in a specific RAM bank, you must save and restore the current bank configuration:

```z80
; 128K: bank-switching ISR
bank_isr:
    PUSH AF
    PUSH BC
    ; Save current bank
    LD   BC,#7FFD
    IN   A,(C)            ; Read current banking (not always reliable)
    LD   (saved_bank),A
    ; Switch to needed bank
    LD   A,#07            ; Bank 7 paged into #C000
    OUT  (C),A
    ; ... work with banked data ...
    ; Restore bank
    LD   A,(saved_bank)
    OUT  (C),A
    POP  BC
    POP  AF
    EI
    RET
```

> [!WARNING]
> On the 128K machines, `IN A,(#7FFD)` does **not** reliably read back the current bank register — the 7FFD port is write-only. You must track the bank state in software.

---

## Cookbook

### Frame Counter

A simple 16-bit counter incremented every frame — useful for animation timing, delays, and throttling:

```z80
frame_count: DW  0

frame_counter_isr:
    EX   AF,AF'
    LD   HL,(frame_count)
    INC  HL
    LD   (frame_count),HL
    EX   AF,AF'
    EI
    RET

; --- Usage: wait 50 frames (1 second) ---
    LD   HL,(frame_count)
    LD   DE,50
    ADD  HL,DE
    PUSH HL
.wait:
    LD   HL,(frame_count)
    POP  DE
    PUSH DE
    AND  A               ; Clear carry
    SBC  HL,DE
    JR   c,.wait
    POP  HL              ; Clean stack
```

### Border Raster Bar

Change border color at fixed scanline intervals to produce horizontal color bars:

```z80
; Simple 3-color border bar effect
raster_isr:
    PUSH AF
    ; ISR fires at top border start — immediate border changes are safe
    LD   A,#02           ; Red
    OUT  (#FE),A
    
    ; Wait for first scanline change point (~224T per scanline)
    LD   B,40            ; Delay for ~40 scanlines
.d1: NOP : NOP : NOP : NOP
    DJNZ .d1
    
    LD   A,#06           ; Yellow
    OUT  (#FE),A
    
    LD   B,40
.d2: NOP : NOP : NOP : NOP
    DJNZ .d2
    
    LD   A,#04           ; Green
    OUT  (#FE),A
    
    ; Let the rest of the frame run normally
    POP  AF
    EI
    RET
```

> [!NOTE]
> Timing loops using `DJNZ` are approximate and affected by contention. For precise raster bars, use `HALT` + exact T-state counting. See [race_the_beam.md](race_the_beam.md) (planned) for details.

### Music Player ISR

Play a note every frame using the AY-3-8912 on 128K machines:

```z80
music_data: DB  #01,#02,#03,#00   ; Note pattern (channel A tone periods)
            DB  #FF               ; End marker
music_pos:  DW  music_data

ay_isr:
    PUSH AF
    PUSH BC
    PUSH HL
    
    LD   HL,(music_pos)
    LD   A,(HL)
    CP   #FF               ; End of data?
    JR   z,.restart
    
    ; Write tone period to AY register 0 (channel A fine tune)
    LD   BC,#FFFD
    OUT  (C),A              ; Register select: channel A fine tune
    LD   B,#BF
    INC  HL
    LD   A,(HL)             ; Coarse tune value
    OUT  (C),A              ; Write data
    
    INC  HL
    LD   (music_pos),HL
    JR   .done
    
.restart:
    LD   HL,music_data
    LD   (music_pos),HL
    JR   ay_isr + 2         ; Restart from beginning
    
.done:
    POP  HL
    POP  BC
    POP  AF
    EI
    RET
```

### Keyboard Scan ISR

Read a specific key every frame without using the ROM's keyboard scanner:

```z80
key_pressed: DB  0
KEY_ROW     EQU  #FEFE    ; Port for row: SHIFT-Z-X-C-V
KEY_MASK    EQU  #01      ; Bit 0 = SHIFT key

key_isr:
    PUSH AF
    PUSH BC
    
    LD   BC,KEY_ROW
    IN   A,(C)             ; Read keyboard row
    AND  KEY_MASK          ; Test specific key
    JR   z,.is_pressed     ; Bit 0 = 0 means pressed
    LD   A,0
    LD   (key_pressed),A
    JR   .done
.is_pressed:
    LD   A,1
    LD   (key_pressed),A
.done:
    POP  BC
    POP  AF
    EI
    RET
```

---

## Antipatterns

### The Missing EI

The most common interrupt bug — forgetting to re-enable interrupts before returning:

```z80
; BAD: Machine freezes after the first interrupt
broken_isr:
    PUSH AF
    ; ... do work ...
    POP  AF
    RET                ; Interrupts stay disabled forever!
```

```z80
; GOOD: Always EI before RET
correct_isr:
    PUSH AF
    ; ... do work ...
    POP  AF
    EI                 ; Re-enable interrupts
    RET                ; Return — next instruction executes, then INT can fire
```

The Z80 has a one-instruction delay after `EI` — the `RET` completes before the next interrupt can be serviced. This is by design: it guarantees the stack is cleaned up before re-entry.

### The Slow ISR

Doing too much work in the ISR steals CPU time from the main program. If the ISR takes 30,000 T-states, the main program only gets ~27,000 T-states per frame — barely enough for a game loop:

```z80
; BAD: ISR does heavy computation
slow_isr:
    PUSH AF : PUSH BC : PUSH DE : PUSH HL
    CALL render_screen     ; 20,000T — this belongs in the main loop!
    CALL play_music        ; 5,000T — acceptable for ISR
    CALL update_ai         ; 8,000T — this belongs in the main loop!
    POP  HL : POP DE : POP BC : POP AF
    EI : RET
```

Use the deferred processing pattern instead — the ISR sets a flag, the main loop does the heavy lifting.

### The Contended ISR

Code executing from ROM (`#0000`–`#3FFF`) during the paper area is subject to contention. On 48K, the ROM ISR at `#0038` is already in this region. If you place your ISR code in contended memory and it runs during the paper display, it will be slower than expected:

```z80
; BAD: ISR code at #5000 — contended during paper display
    ORG  #5000
my_isr:                     ; Runs slower during paper display!
```

Place ISR code in uncontended memory (`#8000`–`#FFFF` on 48K) or accept the timing variability.

### The Unprotected Bank Switch

On 128K machines, switching banks in the ISR without restoring the previous state corrupts the main program's memory view:

```z80
; BAD: Bank switched but never restored
leaky_isr:
    LD   BC,#7FFD
    LD   A,#07            ; Bank 7 at #C000
    OUT  (C),A             ; Main program's bank is gone!
    ; ... read data from bank 7 ...
    EI
    RET                    ; Bank 7 still paged — main program sees wrong data!
```

Always save and restore the bank register. Since `#7FFD` is write-only, track the state in a RAM variable.

---

## Cross-References

- **Z80 interrupt architecture** (IFF1/IFF2, bus cycles, timing): [z80_interrupts.md](../../01_cpu/z80_interrupts.md)
- **Video frame timing** (T-state budget, contention windows): [video_frame_overview.md](../05_display_and_timing/video_frame_overview.md)
- **ULA timing and contention** (per-scanline contention model): [ula_timing.md](../../02_hardware/original/ula_timing.md)
- **System variables** (FRAMES at #5C78, keyboard state): [system_variables.md](../../04_operating_systems/system_variables.md)
- **Bank switching** (128K paging, ISR considerations): [bank_switching_patterns.md](../03_memory_and_io/bank_switching_patterns.md)
- **I/O ports** (#FE border, #FFFD AY register): [io_ports.md](../03_memory_and_io/io_ports.md)
- **Clone timing** (per-model frame differences): [clone_timing.md](../../02_hardware/clones/clone_timing.md)
