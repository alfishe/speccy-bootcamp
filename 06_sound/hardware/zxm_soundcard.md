# ZXM-SoundCard — The All-in-One Sound Expansion

> **Applies to**: **Soviet** — ZXM-SoundCard expansion cards (Mick Laboratory, 2000s–present) for Nemo-Bus and ZX-Bus machines (ZXM-Phoenix, KAY-256/1024, Pentagon, Scorpion). This is a hardware integration article covering the combined card; for deep dives on individual sound engines, see the linked component articles.

## Overview

The **ZXM-SoundCard** is a multi-function sound expansion board designed by Mick Laboratory (`micklab.ru`) that combines three distinct sound subsystems on a single PCB:

| Subsystem | Chip | Channels | Type | Article |
|-----------|------|----------|------|---------|
| **TurboSound FM (TSFM)** | 2 × YM2203 OPN | 2 × (3 FM + 3 SSG) = 12 total | FM synthesis + PSG | [TurboSound FM](turbosound_fm.md) |
| **SAA1099** | Philips SAA1099 | 6 tone + 2 noise | Stereo PSG | [SAA1099](saa1099.md) |
| **SounDrive** | TLC7226CN | 4 DAC outputs | 8-bit PCM | [Covox & SounDrive](covox_sounDrive.md) |

The card exists in multiple revisions:

| Revision | TSFM | SAA1099 | SounDrive | Notes |
|----------|------|---------|-----------|-------|
| **00–01** | Yes | Yes | No | Early revisions, TSFM + SAA only |
| **02** | Yes | Yes | Yes | First revision with all three subsystems |
| **Middle** | Yes | Yes | Yes | Refined layout |
| **Extreme** | Yes | Yes | Yes | Final production revision |

The ZXM-SoundCard is notable for being **fully open-source** — Mick Laboratory publishes complete schematics, CPLD firmware source (for the EPM7128 or EPM7032 glue logic), and bills of materials for every revision. This makes it the best-documented reference implementation for combining these sound chips on the ZX platform.

### Naming Convention

| Term | Meaning |
|------|---------|
| **ZXM-SoundCard** | The combined multi-function card covered in this article |
| **TSFM** | TurboSound FM — the 2 × YM2203 subsystem |
| **SounDrive** | The 4-channel DAC subsystem (TLC7226CN) |
| **SAA1099** | The Philips 6-channel stereo PSG |
| **Nemo-Bus** | The expansion bus used by KAY-256/1024 and ZXM-Phoenix |
| **ZX-Bus** | Standard ZX Spectrum expansion bus (Pentagon, Scorpion) |

## Hardware Architecture

The ZXM-SoundCard connects to the host machine via either the **Nemo-Bus** (KAY/Phoenix) or the standard **ZX-Bus** (Pentagon/Scorpion). The card's CPLD handles address decoding, bus arbitration, and the bank-select logic that allows all three subsystems to coexist without port conflicts.

```
┌─────────────────────────────────────────────────────────────────┐
│                       ZXM-SoundCard                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │
│  │  YM2203 #0  │  │  YM2203 #1  │  │   SAA1099   │              │
│  │  (OPN chip) │  │  (OPN chip) │  │  (Philips)  │              │
│  │  3 FM + 3AY │  │  3 FM + 3AY │  │  6ch stereo │              │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘              │
│         │                │                │                      │
│         └───────┬────────┴────────┬───────┘                      │
│                 │                 │                              │
│          ┌──────┴──────┐   ┌──────┴──────┐                       │
│          │   CPLD      │   │  TLC7226CN  │                       │
│          │ (EPM7128)   │   │ (Quad DAC)  │                       │
│          │ Bank-select │   │  SounDrive  │                       │
│          │ + decode    │   │  4 channels │                       │
│          └──────┬──────┘   └──────┬──────┘                       │
│                 │                 │                              │
│                 └────────┬────────┘                              │
│                          │                                       │
│                    ┌─────┴─────┐                                 │
│                    │ Audio Mix │──► Line Out (stereo)            │
│                    └───────────┘                                 │
└──────────────────────┬───────────────────────────────────────────┘
                       │
                  Nemo-Bus / ZX-Bus
```

### Audio Mixing

All three subsystems feed into a passive or active mixing stage on the card. The stereo output sums:

- **Left channel**: YM2203 #0 + YM2203 #1 (mixed) + SAA1099 left + SounDrive LA + SounDrive LB
- **Right channel**: YM2203 #0 + YM2203 #1 (mixed) + SAA1099 right + SounDrive RA + SounDrive RB

The YM2203 outputs are mono; stereo separation comes from the SAA1099 (per-channel panning) and SounDrive (dedicated L/R DACs).

## Port Map

The ZXM-SoundCard decodes three independent port ranges. The CPLD firmware implements bank-selection to multiplex the YM2203 chips and SAA1099 through overlapping address space.

### TSFM Ports (TurboSound FM)

Standard TurboSound FM port protocol extended for two YM2203 chips:

| Port | Decoding (A15–A0) | Read | Write | Notes |
|------|-------------------|------|-------|-------|
| `#FFFD` | `11111111111111x1` | Status / AY reg | Register select | A0=0 for YM2203 |
| `#BFFD` | `10111111111111x1` | — | Register data | A0=1 for YM2203 |
| `#FF` | `xxxxxxxx11111111` | — | Bank select | Controls which chip receives writes |

**Bank-select register (`#FF`):**

| Bits | Value | Effect |
|------|-------|--------|
| `[1:0]` | `00` | Select AY chip 0 (SSG of YM2203 #0) |
| `[1:0]` | `01` | Select AY chip 1 (SSG of YM2203 #1) |
| `[1:0]` | `10` | Select YM2203 FM mode (chip 0 or 1 via bit 2) |
| `[1:0]` | `11` | Reserved |

See [TurboSound FM](turbosound_fm.md) for the full YM2203 register map and programming model.

### SAA1099 Ports

| Port | Decoding (A15–A0) | Read | Write | Notes |
|------|-------------------|------|-------|-------|
| `#FF` (255) | `xxxxxxxx11111111` | — | SAA data | Write register value |
| `#1FF` (511) | `xxxxxx0111111111` | — | SAA address | Select register |

The SAA1099 shares the `#FF` port with the TSFM bank-select. The CPLD distinguishes writes by:
- **Low byte only** (`A8=0`): routed to TSFM bank-select or SAA data
- **High byte set** (`A8=1`): routed to SAA address register

**SAA1099 clock control via `#FFFD`:**

The SAA1099 lacks a hardware reset pin. The ZXM-SoundCard gates the SAA1099's master clock through a control bit in the AY-compatible register space:

| `#FFFD` bit | Function |
|-------------|----------|
| Bit 3 | SAA1099 clock enable: `1` = clock running, `0` = clock stopped (silence) |

Write `#F6` to `#FFFD` to enable the SAA1099 clock; write `#FE` to disable it. This provides a soft-reset mechanism.

See [SAA1099](saa1099.md) for the full register map and programming model.

### SounDrive Ports (TLC7226CN)

Four independent 8-bit DAC channels for stereo PCM output:

| Port | Decoding (A15–A0) | Read | Write | Channel |
|------|-------------------|------|-------|---------|
| `#0F` (15) | `xxxxxxxx00001111` | — | DAC value | Left A |
| `#1F` (31) | `xxxxxxxx00011111` | — | DAC value | Left B |
| `#4F` (79) | `xxxxxxxx01001111` | — | DAC value | Right A |
| `#5F` (95) | `xxxxxxxx01011111` | — | DAC value | Right B |

Each write immediately updates the corresponding DAC output. There is no buffering — values appear on the analog output within nanoseconds.

See [Covox & SounDrive](covox_sounDrive.md) for mixing strategies, sample playback code, and CPU timing considerations.

## Programming Considerations

### Subsystem Independence

The three subsystems are electrically and logically independent. You can:
- Play TSFM music while streaming samples through SounDrive
- Use SAA1099 for sound effects while TSFM handles the soundtrack
- Mix all three simultaneously (subject to CPU bandwidth)

The only coupling is the `#FFFD` control byte, which affects both TSFM bank-select and SAA1099 clock gating. Software must coordinate writes to this port.

### Initialization Sequence

A clean initialization touches all three subsystems:

```z80
ZXM_Init:
    ; 1. Stop SAA1099 clock (soft-reset)
    LD   BC,#FFFD
    LD   A,#FE           ; SAA clock disable
    OUT  (C),A
    
    ; 2. Initialize TSFM: select AY chip 0, silence all channels
    LD   A,#00
    OUT  (#FF),A         ; bank-select = AY chip 0
    
    LD   BC,#FFFD
    LD   A,7             ; AY mixer register
    OUT  (C),A
    LD   B,#BF
    LD   A,#3F           ; all channels off
    OUT  (C),A
    
    ; 3. Initialize SounDrive: silence all DACs
    XOR  A
    OUT  (#0F),A         ; Left A
    OUT  (#1F),A         ; Left B
    OUT  (#4F),A         ; Right A
    OUT  (#5F),A         ; Right B
    
    ; 4. Re-enable SAA1099 clock
    LD   BC,#FFFD
    LD   A,#F6           ; SAA clock enable
    OUT  (C),A
    
    ; 5. Silence SAA1099 (write 0 to all volume registers)
    LD   HL,SAA_SilenceTable
    LD   B,12            ; 6 left + 6 right volume regs
.saa_loop:
    LD   A,(HL)
    INC  HL
    LD   BC,#01FF        ; SAA address port
    OUT  (C),A
    LD   A,(HL)
    INC  HL
    LD   BC,#00FF        ; SAA data port
    OUT  (C),A
    DJNZ .saa_loop
    RET

SAA_SilenceTable:
    DB   #00,#00, #01,#00, #02,#00, #03,#00, #04,#00, #05,#00  ; left vols
    DB   #10,#00, #11,#00, #12,#00, #13,#00, #14,#00, #15,#00  ; right vols
```

### Detection

Detecting a ZXM-SoundCard involves probing for each subsystem:

1. **TSFM detection**: Read status from `#FFFD` after selecting the TSFM bank; a real YM2203 returns bits 6–7 with timer flags, not floating bus.
2. **SAA1099 detection**: Gate on host machine type (ZXM-Phoenix, KAY with known ZXM-SoundCard). Port reads are unreliable.
3. **SounDrive detection**: Write a test pattern to `#0F` and listen for audible output, or rely on host machine identification.

For software targeting the ZXM-SoundCard specifically, the simplest approach is to assume all subsystems are present if the host machine is known to be ZXM-equipped.

### CPU Budget

Each subsystem consumes CPU time differently:

| Subsystem | Writes/frame (typical) | T-states/frame | Notes |
|-----------|------------------------|----------------|-------|
| TSFM (SSG only) | ~10–20 | ~600–1200 | Standard AY playback |
| TSFM (FM + SSG) | ~50–100 | ~3000–6000 | FM voice updates are register-heavy |
| SAA1099 | ~10–30 | ~600–1800 | Fewer registers than FM |
| SounDrive (8 kHz) | ~160 | ~9600 | T-state cost dominated by sample fetch |
| SounDrive (16 kHz) | ~320 | ~19200 | May require unrolled loops |

Running all three at high update rates is feasible on a 7 MHz machine but leaves little CPU for gameplay. Most productions use TSFM for music and reserve SounDrive for occasional sampled speech or sound effects.

## Comparison with Other Sound Hardware

| Criterion | ZXM-SoundCard | TurboSound (2×AY) | General Sound | MoonSound |
|-----------|---------------|-------------------|---------------|-----------|
| **Channels (total)** | 12 FM + 6 SSG + 6 SAA + 4 DAC = 28 | 6 | 4 (sample) | 18 FM + 24 wavetable |
| **FM synthesis** | Yes (YM2203 OPN) | No | No | Yes (OPL4) |
| **Sample playback** | Yes (SounDrive DAC) | No | Yes (coprocessor) | Yes (wavetable RAM) |
| **CPU cost** | Low–Medium | Very Low | Very Low | Low |
| **Availability** | Rare (DIY/Mick Lab) | Common (Soviet clones) | Rare | Very Rare |

The ZXM-SoundCard is the most feature-rich ZX sound expansion in terms of raw channel count and synthesis variety. Its main limitation is availability — it was produced in small numbers for the enthusiast market, and most ZX software assumes only AY or TurboSound.

## Revisions and Variants

| Revision | Year | Key Changes |
|----------|------|-------------|
| **00** | ~2004 | Initial design, TSFM + SAA1099 only |
| **01** | ~2005 | Minor fixes, improved CPLD firmware |
| **02** | ~2006 | Added SounDrive (TLC7226CN) |
| **Middle** | ~2008 | Revised PCB layout, better audio section |
| **Extreme** | ~2010 | Final production revision, all features |

All revisions use the same port addresses and are software-compatible. Hardware differences are in the mixing stage quality and PCB manufacturing.

## Software Support

### Trackers and Players

- **Vortex Tracker II**: Supports TSFM export (experimental FM instrument editor)
- **E-Tunes series**: Mick Laboratory's SAA1099 music compilations (SAM Coupé E-Tracker ports)
- **Custom demos**: Several ZXM-SoundCard-specific demos from the Mick Laboratory archive

### Emulators

| Emulator | TSFM | SAA1099 | SounDrive |
|----------|------|---------|-----------|
| **Unreal Speccy** | Yes | Yes | Yes |
| **ZEsarUX** | Yes | Yes | Yes |
| **Fuse** | No | No | Yes (via Covox) |

## References and Further Reading

- [Mick Laboratory: ZXM-SoundCard](http://micklab.ru/My%20Soundcard/ZXMSoundCard.htm) *(in Russian)* — Full schematics, CPLD firmware source, and bills of materials for every revision.
- [TurboSound FM](turbosound_fm.md) — Deep dive on the YM2203 OPN chips and FM programming.
- [SAA1099](saa1099.md) — Philips PSG architecture and register map.
- [Covox & SounDrive](covox_sounDrive.md) — DAC subsystem details and sample playback techniques.
- [Sound Hardware Ecosystem Overview](sound_overview.md) — How the ZXM-SoundCard fits into the broader ZX sound landscape.
