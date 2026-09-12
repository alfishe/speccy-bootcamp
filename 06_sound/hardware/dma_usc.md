[← Home](../../README.md) · [Sound](../README.md) · [Hardware](README.md)

# DMA USC — DMA Ultra Sound Controller

The **DMA Ultra Sound Controller** (DMA USC) represents the most ambitious approach to sample playback on Soviet ZX Spectrum clones. While [General Sound](gs_general_sound.md) uses a dedicated Z80 coprocessor and [SounDrive](covox_sounDrive.md) relies on brute-force CPU output, the DMA USC takes a third path: **autonomous DMA transfers** using the Intel 8237 controller. This eliminates CPU overhead entirely — the main Z80 sets up a transfer, then walks away while hardware streams samples to the DAC.

> **Applies to**: **Soviet** — DMA USC expansion boards for Pentagon, Scorpion, and other Soviet clones. Extremely rare hardware, with perhaps fewer than 100 units ever built. Software support is limited to a handful of demos and experimental players.

---

## Overview

The DMA USC borrows heavily from IBM PC sound card architecture. The Intel 8237 DMA controller — the same chip that handles floppy disk and hard drive transfers on PCs — is repurposed here to autonomously read sample data from RAM and output it to a DAC. Two Intel 8253 programmable interval timers provide precise sample rate control and interrupt generation.

### Key Specifications

| Parameter | Value |
|-----------|-------|
| **DMA Controller** | Intel 8237A or equivalent (KR580VT57 Soviet clone) |
| **Timer Chips** | 2 × Intel 8253 or KR580VI53 |
| **DAC Resolution** | 8-bit linear |
| **Sample Rate** | Programmable via 8253, typically 8–44 kHz |
| **Channels** | 4 hardware-mixed (some variants) |
| **CPU Overhead** | Near zero during playback |
| **RAM Source** | Main ZX RAM (DMA steals bus cycles) |

### Why DMA?

The fundamental problem with [Covox](covox_sounDrive.md) is CPU overhead. At 11 kHz mono playback, the Z80 spends ~30% of its time just pushing bytes to the DAC. At 22 kHz stereo (4 channels mixed), the CPU is completely saturated — no game logic, no graphics, just sample output.

DMA solves this by offloading the memory-to-DAC transfer to dedicated hardware:

1. Z80 sets up source address, destination port, and byte count in the 8237
2. Z80 programs the 8253 timer to generate DMA requests at the desired sample rate
3. Z80 enables the DMA channel and returns to other work
4. 8253 fires → 8237 steals one bus cycle → byte goes to DAC
5. Repeat until byte count exhausted, then interrupt the Z80

The CPU cost drops from ~70,000 T-states/frame to ~1,000 T-states/frame (just the setup and interrupt handler).

---

## Hardware Architecture

### Block Diagram

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Z80 CPU   │────▶│ Intel 8237  │────▶│  8-bit DAC  │───▶ Audio Out
│             │◀────│    DMA      │◀────│             │
└─────────────┘     └─────────────┘     └─────────────┘
       │                   │
       │            ┌──────┴──────┐
       │            │             │
       ▼            ▼             ▼
┌─────────────┐ ┌─────────┐ ┌─────────┐
│   ZX RAM    │ │ 8253 #1 │ │ 8253 #2 │
│  (samples)  │ │ (rate)  │ │ (aux)   │
└─────────────┘ └─────────┘ └─────────┘
```

### Intel 8237A DMA Controller

The 8237 provides four independent DMA channels. In the DMA USC, one or more channels are dedicated to audio streaming:

- **Channel 0–3**: Each can transfer from memory to I/O or vice versa
- **Mode**: Single transfer, block transfer, or demand transfer
- **Address**: 16-bit source/destination (with page register for 20-bit on PC, not used here)
- **Count**: 16-bit transfer count (up to 65,536 bytes per setup)

For audio, the 8237 is configured in **single transfer mode** — each DMA request (DREQ) from the 8253 timer causes exactly one byte transfer.

### Intel 8253 Programmable Interval Timer

Two 8253 chips provide timing:

- **8253 #1**: Primary sample rate timer. Generates DREQ pulses to the 8237 at the desired frequency (e.g., 22,050 Hz for CD-quality mono).
- **8253 #2**: Auxiliary functions — envelope timing, channel mixing sync, or secondary rate for multi-rate playback.

Each 8253 has three 16-bit counters. For audio, Counter 0 is typically configured as a rate generator (Mode 2) or square wave generator (Mode 3).

### Multi-Channel Mixing

Some DMA USC variants include hardware mixing for 4 channels, similar to [SounDrive](covox_sounDrive.md). Each channel has its own DMA setup, and an analog summing amplifier combines the outputs:

```
Channel 0 ──▶ DAC ──┐
Channel 1 ──▶ DAC ──┼──▶ Summing Amp ──▶ Audio Out
Channel 2 ──▶ DAC ──┤
Channel 3 ──▶ DAC ──┘
```

The `Channel` register at `#0777`–`#3777` selects which channel subsequent 8237/8253 programming affects.

---

## Port Map

The DMA USC uses a complex port decoding scheme in the `#x777` range:

| Port Range | Address (A15–A0) | Decoding (A15–A0) | Read | Write | Function |
|------------|------------------|-------------------|------|-------|----------|
| `#0777`–`#3777` | `00BA011101110111` | `00BA0x1101110xxx` | — | Channel | Select active channel (0–3) |
| `#0C77`–`#FC77` | `DCBA110001110111` | `DCBAxx0001110xxx` | 8237 | 8237 | DMA controller registers |
| `#3D77`–`#FD77` | `BA11110101110111` | `BAxxxx0101110xxx` | — | 8253-1 | Timer #1 registers |
| `#3E77`–`#FE77` | `BA11111001110111` | `BAxxxx1001110xxx` | — | 8253-2 | Timer #2 registers |
| `#3F77`–`#FF77` | `BA11111101110111` | `BAxx1x1101110xxx` | — | Volume | Master volume control |
| `#F777` | `1111011101110111` | `11xx0x1101110xxx` | — | DMAIntMask | DMA interrupt enable/disable |

### Port Decoding Notes

- Bits A15–A12 (`DCBA`) select 8237 internal registers (address, count, mode, status)
- The `#x777` base with variations in upper bits is typical of Soviet peripheral designs
- Multiple mirrors exist due to incomplete decoding (bits 3, 8–11 often ignored)

### 8237 Register Access

The 8237's internal registers are accessed via the upper address bits:

| A15–A12 | 8237 Register |
|---------|---------------|
| `0000` | Channel 0 Address |
| `0001` | Channel 0 Count |
| `0010` | Channel 1 Address |
| `0011` | Channel 1 Count |
| `0100` | Channel 2 Address |
| `0101` | Channel 2 Count |
| `0110` | Channel 3 Address |
| `0111` | Channel 3 Count |
| `1000` | Status (R) / Command (W) |
| `1001` | Request |
| `1010` | Single Mask |
| `1011` | Mode |
| `1100` | Clear Flip-Flop |
| `1101` | Master Clear (W) / Temp (R) |
| `1110` | Clear Mask |
| `1111` | All Mask |

---

## Programming Model

### Basic Playback Sequence

```z80
; === DMA USC Playback Example ===
; Play 8192 bytes from HL at 11025 Hz

DMAUSC_CHAN     EQU #0777   ; Channel select
DMAUSC_8237     EQU #0C77   ; 8237 base
DMAUSC_8253_1   EQU #3D77   ; Timer 1
DMAUSC_VOLUME   EQU #3F77   ; Volume

; 1. Select channel 0
    LD BC, DMAUSC_CHAN
    LD A, 0
    OUT (C), A

; 2. Reset 8237
    LD BC, DMAUSC_8237 + #D000  ; Master Clear
    OUT (C), A

; 3. Set source address (sample data at HL)
    LD BC, DMAUSC_8237 + #C000  ; Clear flip-flop
    OUT (C), A
    LD BC, DMAUSC_8237          ; Channel 0 Address
    LD A, L
    OUT (C), A                  ; Low byte
    LD A, H
    OUT (C), A                  ; High byte

; 4. Set transfer count (8192 - 1 = 8191)
    LD BC, DMAUSC_8237 + #C000  ; Clear flip-flop
    OUT (C), A
    LD BC, DMAUSC_8237 + #1000  ; Channel 0 Count
    LD A, #FF
    OUT (C), A                  ; Low byte (8191 & 0xFF)
    LD A, #1F
    OUT (C), A                  ; High byte (8191 >> 8)

; 5. Set mode: single transfer, read, auto-init, channel 0
    LD BC, DMAUSC_8237 + #B000  ; Mode register
    LD A, %01011000             ; Single, read, auto-init, ch0
    OUT (C), A

; 6. Program 8253 Timer 1 for 11025 Hz
;    Assuming 1.7734 MHz input: 1773400 / 11025 ≈ 161
    LD BC, DMAUSC_8253_1 + #3000  ; Control word
    LD A, %00110110               ; Counter 0, LSB/MSB, Mode 3
    OUT (C), A
    LD BC, DMAUSC_8253_1          ; Counter 0 data
    LD A, 161                     ; Divisor low
    OUT (C), A
    LD A, 0                       ; Divisor high
    OUT (C), A

; 7. Unmask channel 0 to start DMA
    LD BC, DMAUSC_8237 + #A000  ; Single Mask
    LD A, %00000000             ; Clear mask for channel 0
    OUT (C), A

; DMA now running autonomously!
    RET
```

### Interrupt Handling

When the transfer count reaches zero, the 8237 can generate an interrupt (if enabled via `#F777`). The interrupt handler typically:

1. Acknowledges the interrupt
2. Reloads the next sample buffer address/count (double-buffering)
3. Returns

This allows seamless streaming of samples larger than 64 KB.

---

## Comparison With Other Sound Hardware

| Criterion | Covox / SounDrive | General Sound | DMA USC | ZX Next DMA |
|-----------|-------------------|---------------|---------|-------------|
| **CPU Overhead** | Very high (30–100%) | Very low (~2%) | Near zero | Zero |
| **Sample Source** | Main RAM | GS RAM (separate) | Main RAM | Next RAM |
| **Max Channels** | 4 (SounDrive) | 4 | 4 | 4 |
| **Hardware Mixing** | Yes (SounDrive) | Yes | Yes (some variants) | Yes |
| **Complexity** | Simple | Complex (coprocessor) | Moderate (PC chips) | FPGA-integrated |
| **Availability** | Common | Uncommon | Very rare | Next only |
| **Sample Rate** | CPU-limited | 37.5 kHz max | Timer-limited (~44 kHz) | 27.7 kHz |

### DMA USC vs. General Sound

- **GS advantage**: Self-contained with its own RAM; the main Z80 never stalls waiting for sample data.
- **DMA USC advantage**: No need for a separate sample upload phase; samples play directly from main RAM.
- **GS disadvantage**: Limited to 64–128 KB of sample storage.
- **DMA USC disadvantage**: DMA steals bus cycles from the main Z80 (though individual steals are brief).

### DMA USC vs. ZX Next DMA

The ZX Spectrum Next's FPGA-integrated DMA audio is conceptually similar but far more refined:

- No external chips — everything is in the FPGA
- Tighter integration with the memory system
- Better interrupt handling
- Actually available to buy

---

## Detection

DMA USC detection is straightforward — probe the 8237 status register:

```z80
; Returns A=1 if DMA USC present, A=0 otherwise
DetectDMAUSC:
    LD BC, DMAUSC_8237 + #D000  ; Master Clear
    XOR A
    OUT (C), A
    
    LD BC, DMAUSC_8237 + #8000  ; Status register
    IN A, (C)
    AND %00001111               ; Lower 4 bits = TC flags
    CP %00001111                ; After reset, all TC flags set
    JR NZ, .notfound
    
    LD A, 1
    RET
.notfound:
    XOR A
    RET
```

---

## Historical Context

The DMA USC emerged in the late 1990s as Soviet hardware hackers explored PC-derived audio solutions. By this time, the demoscene had largely moved to trackers requiring 4-channel mixing at reasonable sample rates — something the Z80 simply couldn't do in software while leaving CPU time for visuals.

The approach never gained widespread adoption due to:

1. **Component cost**: 8237 + 2×8253 + support logic was expensive
2. **Timing complexity**: Synchronizing DMA with Z80 memory access required careful design
3. **Competition**: General Sound provided similar capability with a more elegant (if expensive) coprocessor approach
4. **Platform decline**: By the time DMA USC matured, the ZX Spectrum scene was shrinking

Today, DMA USC is primarily of historical interest — a fascinating "what if" from an era when hobbyists tried to drag the Spectrum into the multimedia age.

---

## References and Further Reading

- [SounDrive](covox_sounDrive.md) — The brute-force alternative: hardware-mixed 4-channel DAC without DMA
- [General Sound](gs_general_sound.md) — The coprocessor approach: dedicated Z80 for audio mixing
- [ZX Spectrum Next Audio](zx_next_audio.md) — Modern DMA audio in FPGA
- [Sound Hardware Overview](sound_overview.md) — Comparison of all ZX audio options
- [Intel 8237A DMA Controller Datasheet](https://www.alldatasheet.com/datasheet-pdf/pdf/27483/INTEL/8237A.html) — Original Intel documentation
- [Intel 8253 Timer Datasheet](https://www.alldatasheet.com/datasheet-pdf/pdf/27458/INTEL/8253.html) — Timer programming reference
