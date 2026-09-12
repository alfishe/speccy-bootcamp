[← Home](../../README.md) · [Sound](../README.md) · [Hardware](README.md)

# Covox & SounDrive — Brute-Force PCM Playback

By the early 1990s, the demoscene and game developers were desperate for digitized sound. Trackers on the Commodore Amiga were pumping out incredible 4-channel sampled music (MOD files), making the ZX Spectrum's AY-3-8910 chip sound decidedly anachronistic. 

Developers tried to force the AY chip to play PCM samples by rapidly changing its volume registers (see [SID-sound and Sample Playback](../synthesis/ay_ym_techniques.md)). But the AY's volume DAC is only 4-bit, non-linear (logarithmic), and requires massive CPU overhead to convert linear 8-bit samples into 4-bit logarithmic equivalents via lookup tables. The results were gritty, quiet, and consumed nearly 100% of the Z80's CPU time.

The solution didn't come from a complex new sound chip. It came from a crude hack invented for IBM PCs in 1987: the **Covox Speech Thing**. It was literally just a handful of resistors plugged into a parallel printer port. Soviet hardware hackers brought this exact concept to the ZX Spectrum, evolving it from a single-channel curiosity into **SounDrive** — a massive 4-channel hardware mixer that bypassed the Z80's mathematical bottlenecks and brought Amiga-quality MOD playback to the Speccy.

---

## 1. Hardware Architecture: The Resistor Ladder

A Covox is nothing more than an **R-2R resistor ladder DAC** (Digital-to-Analog Converter). It uses a network of resistors with only two values ($R$ and $2R$) to convert an 8-bit digital value into an analog voltage.

```mermaid
flowchart LR
    subgraph Z80 ["Z80 CPU / Data Bus"]
        D7 --> R7["2R"]
        D6 --> R6["2R"]
        D5 --> R5["2R"]
        D4 --> R4["2R"]
        D3 --> R3["2R"]
        D2 --> R2["2R"]
        D1 --> R1["2R"]
        D0 --> R0["2R"]
    end
    
    subgraph Ladder ["R-2R Ladder"]
        R0 --> N1(( ))
        N1 -->|R| N2(( ))
        R1 --> N2
        N2 -->|R| N3(( ))
        R2 --> N3
        N3 -->|R| N4(( ))
        R3 --> N4
        N4 -->|R| N5(( ))
        R4 --> N5
        N5 -->|R| N6(( ))
        R5 --> N6
        N6 -->|R| N7(( ))
        R6 --> N7
        N7 -->|R| N8(( ))
        R7 --> N8
    end
    
    N8 --> Out["Analog Output (Audio)"]
```

For the Z80, the brilliance of Covox lies in its sheer simplicity. There are no registers to select. There is no status flag to poll. There is no initialization sequence. **Playing a sample is just a single `OUT` instruction.**

```z80
    LD A, (HL)    ; 7 T-states : Fetch sample from memory
    OUT (C), A    ; 12 T-states: Output directly to speaker voltage!
```

![DAC Resolution Comparison](assets/covox_dac_resolution.svg)

---

## 2. The Single Channel Era: Covox

Initially, clone builders wired a single Covox DAC to a spare I/O port (often hijacking a parallel printer port). If you wrote an 8-bit value to the port, the speaker cone moved to that exact position.

| Clone / Interface | Covox Port | Decoding Mask | R/W | Notes |
|-------------------|------------|---------------|-----|-------|
| **Profi** | `#DF` | `xxxxxxxx11011111` | W | Official Covox port on Profi boards |
| **ATM Turbo** | `#FB` | `xxxxxxxx11111011` | W | Built-in DAC on ATM |
| **Pentagon** | `#FB` | `xxxxxxxx11111011` | W | Often wired to the LPT port |

### The T-State Mixing Problem

A single Covox channel is great for playing a single sound effect (like a gunshot). But to play music, you need multiple instruments simultaneously. 

Because there is only one hardware DAC, the Z80 has to act as a **software mixer**. To play four channels, the Z80 must fetch four samples, add them together, divide by four (to prevent overflow), and then output the final byte. 

The Z80 has no hardware multiply or divide instructions. Addition (`ADD A, B`) is fast, but doing it four times per sample, plus boundary checking, consumes dozens of T-states per output cycle. A 3.5 MHz Z80 simply cannot mix 4 channels in software fast enough to achieve a decent sample rate.

---

## 3. The SounDrive Revolution

In 1995, a Russian demoscene group called **Flash Inc.** realized that if software mixing was too slow, they should mix in *hardware*. 

They designed the **SounDrive** interface. Instead of one Covox, SounDrive put **four independent Covox DACs** on a single expansion board. Each DAC was wired to a different I/O port. The outputs of these four DACs were then sent into an analog op-amp mixer (two for the left ear, two for the right).

### SounDrive Version History

Two major SounDrive revisions exist, with slightly different port mappings. Software targeting broad compatibility should detect which version is present (typically by probing for the card's presence via a simple read-back test or configuration register).

### SounDrive v1.02 Port Map

The original Flash Inc. design uses six ports — four DAC channels plus two control ports.

| Channel | Port | Address (A15–A0) | Decoding (A15–A0) | Mirrors | R/W | Stereo Pan |
|---------|------|------------------|-------------------|---------|-----|------------|
| **A** | `#0F` (15) | `xxxxxxxx00001111` | `xxxxxxxxx0001111` | 512 | W | Left |
| **B** | `#1F` (31) | `xxxxxxxx00011111` | `xxxxxxxxx0011111` | 512 | W | Right |
| **Control** | `#3F` (63) | `xxxxxxxx00111111` | `xxxxxxxxx0111111` | 512 | W | — |
| **C** | `#4F` (79) | `xxxxxxxx01001111` | `xxxxxxxxx1001111` | 512 | W | Right |
| **D** | `#5F` (95) | `xxxxxxxx01011111` | `xxxxxxxxx1011111` | 512 | W | Left |
| **Control 2** | `#7F` (127) | `xxxxxxxx01111111` | `xxxxxxxxx1111111` | 512 | W | — |

### SounDrive v1.05 Port Map (Covox Compatible)

Version 1.05 simplifies to four DAC ports with different decoding and adds an alternative high-byte port range for Covox compatibility:

**Primary Ports (Low Range):**

| Channel | Port | Address (A15–A0) | Decoding (A15–A0) | R/W | Stereo Pan |
|---------|------|------------------|-------------------|-----|------------|
| **Left A** | `#0F` (15) | `xxxxxxxx00001111` | `xxxxxxxxxB0Axxx1` | W | Left |
| **Left B** | `#1F` (31) | `xxxxxxxx00011111` | `xxxxxxxxxB0Axxx1` | W | Left |
| **Right A** | `#4F` (79) | `xxxxxxxx01001111` | `xxxxxxxxxB0Axxx1` | W | Right |
| **Right B** | `#5F` (95) | `xxxxxxxx01011111` | `xxxxxxxxxB0Axxx1` | W | Right |

**Alternative Ports (High Range — Covox Compatible):**

| Channel | Port | Address (A15–A0) | Decoding (A15–A0) | R/W | Stereo Pan |
|---------|------|------------------|-------------------|-----|------------|
| **Left A** | `#F1` (241) | `xxxxxxxx11110001` | `xxxxxxxxxxB0A1` | W | Left |
| **Left B** | `#F3` (243) | `xxxxxxxx11110011` | `xxxxxxxxxxB0A1` | W | Left |
| **Right A** | `#F9` (249) | `xxxxxxxx11111001` | `xxxxxxxxxxB0A1` | W | Right |
| **Right B** | `#FB` (251) | `xxxxxxxx11111011` | `xxxxxxxxxxB0A1` | W | Right |

The high-range ports (`#F1`–`#FB`) provide compatibility with existing Covox software that used the `#FB` port on ATM Turbo and Pentagon machines.

### Stereo Channel Layout

Both versions use the same stereo mixing topology — two channels summed to each ear:

```
Left Ear:   Channel A (#0F) + Channel D (#5F)  →  Left DAC  →  Left Speaker
Right Ear:  Channel B (#1F) + Channel C (#4F)  →  Right DAC →  Right Speaker
```

This arrangement allows for several stereo effects. See [Stereo Audio Techniques](stereo_audio.md) for detailed panning strategies.

> [!WARNING]
> **The Kempston Collision:** Port `#1F` is the canonical address for the Kempston Joystick. If a user has a cheap Kempston interface with poor address decoding plugged in alongside a SounDrive, writing a sample to channel B will cause a bus collision. Modern SounDrive implementations (like ZXM-SoundCard) include a configuration bit to disable the `#1F` channel when a Kempston is detected.

### Why This Changed Everything

With SounDrive, the Z80 no longer has to do any math. It just fetches a byte for Channel A and throws it at `#0F`. It fetches a byte for Channel B and throws it at `#1F`. The analog circuitry handles the addition instantly. This removed the software mixing bottleneck, allowing developers to write incredibly tight, unrolled playback loops that pushed the ZX Spectrum's sample rate into the 15–20 kHz range—rivaling the Amiga.

![Software vs Hardware Mixing](assets/soundrive_mixing_comparison.svg)

### The TLC7226CN — Single-Chip Quad DAC

The original 1995 SounDrive built its four channels from discrete TTL: four octal latches (typically `74HC273`), four R-2R resistor networks (eight resistors each — thirty-two total), and four op-amp buffers (a quad LM324 or similar). That is roughly forty discrete parts dedicated to mixing. It works, but it consumes board space, requires close-tolerance resistors for linearity, and the resistor mismatch between channels causes audible stereo imbalance.

Modern SounDrive implementations replace that entire parts pile with a single 20-pin IC: the **Texas Instruments TLC7226CN** — a monolithic **quad 8-bit digital-to-analog converter** with per-channel input latches, on-chip output buffer amplifiers, and a microprocessor-compatible bus interface. Four DACs, four latches, four op-amps, one chip.

| Parameter | Value |
|---|---|
| **Resolution** | 8 bits (256 levels) per channel |
| **Channels** | 4 (A, B, C, D) — independent latches |
| **Package** | 20-pin DIP (also available in PLCC/SOIC) |
| **Output type** | Voltage-mode with buffered amplifier, ~5 mA source/sink |
| **Reference** | Single `Vref` pin shared by all 4 DACs (2 V to `VDD`−4 V) |
| **Supplies** | `VDD` +5 V, `VSS` −5 V (or 0 V for single-supply) |
| **Bus interface** | 8-bit data (`DB0..DB7`) + `A0`/`A1` register select + `/WR` strobe + `/CS` (tied low in SounDrive use) |
| **Settling time** | ~6 µs typical (1 LSB accuracy) |

### TLC7226CN Pinout (20-pin DIP)

The pin layout deliberately separates analog (pins 1–6 and 19–20) from digital (pins 7–18) to minimize crosstalk. In typical SounDrive use the chip is strapped for single-supply operation (`VSS` = 0 V = `AGND`), `/CS` is tied low so the chip responds whenever `/WR` falls, and the four `OUTA..OUTD` pins route directly to the stereo op-amp mixer.

```
              ┌────────────┐
        OUTB ─┤1         20├── OUTC
        OUTA ─┤2         19├── OUTD
         VSS ─┤3         18├── VDD
         REF ─┤4         17├── A0
        AGND ─┤5         16├── A1
        DGND ─┤6         15├── /WR
         DB7 ─┤7         14├── DB0
         DB6 ─┤8         13├── DB1
         DB5 ─┤9         12├── DB2
         DB4 ─┤10        11├── DB3
              └────────────┘
```

> [!NOTE]
> The `A0`/`A1` inputs form a 2-bit register-select that picks which of the four DAC latches captures `DB0..DB7` on the rising edge of `/WR`. The four combinations map cleanly to SounDrive channels A/B/C/D, so the chip is functionally four SounDrive ports in one package.

### Single-Chip vs. Discrete SounDrive

The table below compares the two SounDrive hardware families. Both produce the same output to software — four bytes written to four I/O ports, four analog outputs summed into stereo — but the engineering trade-offs differ significantly.

| Aspect | Original SounDrive (Flash Inc. 1995) | TLC7226CN SounDrive (e.g., Mick Lab ZXM-SoundCard) |
|---|---|---|
| **DAC core** | Discrete R-2R ladder (8 resistors/channel) | Monolithic thin-film R-2R on TLC7226 die |
| **Input latches** | 4 × `74HC273` (or similar) octal latches | 4 on-chip latches included in TLC7226 |
| **Output buffers** | 4 × op-amp (LM324 / LM358 quad) | 4 on-chip buffer amplifiers included in TLC7226 |
| **Total parts for 4 channels** | ~40 components | 1 IC + 4 mixing resistors |
| **Linearity** | ±1–2 LSB best-case; varies with resistor tolerance | ±1 LSB guaranteed by datasheet |
| **Channel-to-channel match** | Limited by resistor matching (1% recommended) | Tight, all on same die |
| **Settling time** | ~1 µs (limited by op-amp slew) | ~6 µs (slower — on-chip buffered output) |
| **Cost (modern)** | Cheap jellybean parts | TLC7226CN now hard to find; often ~$5–10 NOS |
| **Software compatibility** | Identical — both respond to ports `#0F`/`#1F`/`#4F`/`#5F` |

The practical takeaway: for software, both families look identical. For hardware builders, the TLC7226 reduces board area and component count dramatically, but the original discrete design is easier to source parts for and faster in terms of analog settling time.

### TLC7226 Bus Interface and Legacy Port Compatibility

The TLC7226 exposes four register slots through `A0`/`A1`: `00`=DAC A, `01`=DAC B, `10`=DAC C, `11`=DAC D. In the simplest decoding scheme the four channels would occupy four consecutive ports (`#FB`, `#FC`, `#FD`, `#FE`). But Soviet SounDrive software expects the original Flash Inc. port map (`#0F`, `#1F`, `#4F`, `#5F`). A TLC7226-based SounDrive must therefore include a small programmable logic device (CPLD or PAL) that decodes the legacy port addresses and translates them into the correct `A0`/`A1` combination for the TLC7226.

```mermaid
flowchart LR
    Z80["Z80 bus<br/>A0..A7, /IORQ, /WR"] --> CPLD["Address decode<br/>CPLD / PAL"]
    CPLD -->|A0_sel, A1_sel| DAC["A0/A1 register select"]
    CPLD -->|/WR strobe| DAC2["/WR strobe"]
    Z80 -->|D0..D7| DAC3["TLC7226<br/>DB0..DB7"]
    DAC3 --> OUTA[OUTA]
    DAC3 --> OUTB[OUTB]
    DAC3 --> OUTC[OUTC]
    DAC3 --> OUTD[OUTD]
```

The decoding logic also handles the Kempston collision (`#1F`) by either routing that address to the joystick port exclusively or by gating SounDrive writes on a configuration bit set by the user.

### Real-World Example: Mick Lab ZXM-SoundCard

The **ZXM-SoundCard** series by Mick Laboratory (`micklab.ru`) is a documented real-world TLC7226-based SounDrive implementation. It is a multi-function sound card for ZX-Bus / Nemo-Bus machines (ZXM-Phoenix, KAY-256/1024) that combines:

- **TSFM part** — two YM2203 OPN chips (ports `#BFFD` / `#FFFD`, NedoPC-compatible)
- **SAA1099 part** — Philips PSG chip (ports `#FF` / `#1FF` write, `#04FF` / `#05FF` in later revisions)
- **SounDrive part** — single TLC7226CN providing four 8-bit DAC channels

The SounDrive part appears only in the **Middle** and **Extreme** board revisions; earlier revisions (00–03, Light) omit it. The card uses a CPLD for address decoding: an Altera **EPM7032STC44** in the Light/Middle revisions and an **EPM7064STC100** in the Extreme revision. The Extreme revision also adds software-selectable clock sources for the YM2203 chips (standard / Amstrad CPC / Atari ST frequencies) via a `#FFFC` configuration port.

> [!NOTE]
> The ZXM-SoundCard is interesting not because it is unique — there are several TLC7226-based SounDrive implementations in the Soviet clone ecosystem — but because the Mick Lab documentation includes full schematics, CPLD firmware source, and bill of materials for every revision. It is the best-documented reference for how a TLC7226 SounDrive is actually wired.

---

## 4. Practical Implementation

To get high-quality audio, the sample output loop must be as tight as physically possible. Every wasted T-state drops the sample rate and muddies the treble frequencies.

### Single-Channel Covox Output

The simplest case: playing a sample through a single Covox port. This is the foundation of all PCM playback on the Spectrum.

```z80
; Single-channel Covox playback (ATM/Pentagon port #FB)
; Input: HL = sample data address, DE = sample length
; Destroys: A, BC, DE, HL

PlaySampleCovox:
    ld c, #FB           ; Covox port
.loop:
    ld a, (hl)          ; 7 T: fetch sample byte
    out (c), a          ; 12 T: output to DAC
    inc hl              ; 6 T: next sample
    
    ; Timing padding — adjust NOPs for target sample rate
    ; At 3.5 MHz: 25 T/sample = 140 kHz (way too fast)
    ; We need ~180 T/sample for 19.4 kHz
    
    ; Simple delay loop (coarse timing)
    ld b, 8             ; 7 T
.delay:
    djnz .delay         ; 13 T × 8 = 104 T (first 7 are 13T, last is 8T)
                        ; Actually: 13×7 + 8 = 99 T
    
    dec de              ; 6 T
    ld a, d             ; 4 T
    or e                ; 4 T
    jr nz, .loop        ; 12 T (taken) / 7 T (not taken)
    ret
```

For a more precise sample rate, use a lookup table of delay values or unroll the loop entirely with calculated padding.

### Profi Covox Output

The Profi uses port `#DF` instead of `#FB`:

```z80
; Profi Covox — same as above but different port
PlaySampleProfi:
    ld c, #DF           ; Profi Covox port
    ; ... rest identical to PlaySampleCovox
```

### SounDrive 4-Channel Playback

Here is a highly optimized 4-channel SounDrive playback loop. Note that we don't use `OUT (C), A`. We use the `OUTI` (Output, Increment, and Decrement) instruction, which is heavily abused here to fetch from `(HL)`, write to port `(C)`, and increment `HL` all in a single 16-T-state sweep.

```z80
; SounDrive 4-Channel Playback Kernel
; Requires Contended Memory Timing awareness! 
; If this runs in contended RAM, the sample rate will jitter wildly.

PlayFrame:
    ; Set up BC for Channel A (Port #0F)
    LD BC, #000F        ; C = Port #0F, B = 0 (we don't care about B here)
    LD HL, (ChanAPtr)   ; HL = Pointer to Channel A sample data
    OUTI                ; 16 T: Read (HL), write to port C, HL++, B--

    ; Set up BC for Channel B (Port #1F)
    LD C, #1F           ; 7 T: Just change the port (C)
    LD HL, (ChanBPtr)   
    OUTI                ; 16 T: Output Channel B

    ; Set up BC for Channel C (Port #4F)
    LD C, #4F           
    LD HL, (ChanCPtr)   
    OUTI                ; 16 T: Output Channel C

    ; Set up BC for Channel D (Port #5F)
    LD C, #5F           
    LD HL, (ChanDPtr)   
    OUTI                ; 16 T: Output Channel D

    ; ... (Save pointers, calculate next pitch step, etc) ...
```

### Performance Reality Check

At 3.5 MHz, the Z80 executes 3,500,000 T-states per second.
If our 4-channel loop (fetching, outputting, advancing pointers, and checking loop bounds) takes **180 T-states** per iteration:

$$ 3,500,000 \div 180 = 19,444 \text{ Hz} $$

A 19.4 kHz sample rate is excellent for 8-bit audio, producing crisp drums and clear vocals. (For comparison, the Amiga's Paula chip typically maxed out around 28 kHz for most MODs).

### Stereo Panning Techniques

SounDrive's dual-channel-per-ear design enables several stereo effects. These techniques are also covered in detail in [Stereo Audio Techniques](stereo_audio.md).

#### Hard Panning (MOD-Style)

Traditional Amiga MOD files hard-pan channels: 1 and 4 to the left, 2 and 3 to the right. SounDrive maps naturally to this:

```z80
; Hard-panned 4-channel playback (MOD channel order)
; Channel 1 (Left):  port #0F
; Channel 2 (Right): port #1F  
; Channel 3 (Right): port #4F
; Channel 4 (Left):  port #5F

HardPanFrame:
    ld hl, (Chan1Ptr)   ; MOD channel 1 → Left
    ld c, #0F
    outi
    
    ld hl, (Chan2Ptr)   ; MOD channel 2 → Right
    ld c, #1F
    outi
    
    ld hl, (Chan3Ptr)   ; MOD channel 3 → Right
    ld c, #4F
    outi
    
    ld hl, (Chan4Ptr)   ; MOD channel 4 → Left
    ld c, #5F
    outi
    ret
```

#### Center Panning (Mono Mix)

To place a sound in the center, output the same sample to both a left and right channel:

```z80
; Center-panned voice using channels A (left) and B (right)
CenterPan:
    ld a, (hl)          ; fetch sample
    ld c, #0F           ; Left channel A
    out (c), a
    ld c, #1F           ; Right channel B
    out (c), a          ; same sample to both ears = center
    inc hl
    ret
```

This "wastes" a channel but creates a solid center image. For full 4-channel MOD playback with center-panned bass, software-mix the bass into channels A and B before output.

#### Dynamic Stereo Width

By varying the balance between left and right outputs, you can create a sense of stereo width:

```z80
; Pseudo-stereo: same sample, different volumes for left/right
; Input: A = sample, B = pan position (0=left, 128=center, 255=right)
DynamicPan:
    push af
    
    ; Calculate left volume: sample × (255 - pan) / 256
    ld c, a             ; C = sample
    ld a, 255
    sub b               ; A = 255 - pan
    call MultiplyCA     ; A = C × A / 256 (needs mul routine)
    ld e, a             ; E = left sample
    
    pop af
    ; Calculate right volume: sample × pan / 256
    ld c, a             ; C = sample
    ld a, b             ; A = pan
    call MultiplyCA     ; A = C × A / 256
    ld d, a             ; D = right sample
    
    ; Output
    ld a, e
    out (#0F), a        ; Left
    ld a, d
    out (#1F), a        ; Right
    ret
```

This requires a fast 8×8→8 multiply routine, which consumes significant CPU. For production code, use a pre-calculated panning table.

---

## 5. Antipatterns & Pitfalls

### Antipattern 1: The `IM2` Jitter Trap

A common mistake for beginners is trying to play PCM samples inside the standard 50Hz Vblank interrupt (`IM2`). 

**Why it fails:** The interrupt only fires 50 times a second. If you play a chunk of samples inside the interrupt, the timing between chunks will vary depending on what the main loop was doing when the interrupt hit. Furthermore, standard Z80 interrupts have a variable latency of up to ~23 T-states depending on which instruction was interrupted. This creates brutal, audible clicking and phase jitter.

**The Fix:** Disable interrupts (`DI`). PCM playback must own the entire CPU. If you need to sync with the screen, use the [Floating Bus port `#FF`](../../10_references/io_port_map.md) to poll for the electron beam.

### Antipattern 2: The `LDIR` Myth

You might think: *"If `LDIR` is the fastest way to move memory, I should use `OUTI` in a block repeat (`OTIR`) to blast a sample to the Covox!"*

**Why it fails:** `OTIR` executes in 21 T-states per byte. At 3.5 MHz, that's an output rate of **166 kHz**. The human ear can't hear that, and standard tape-loaded samples are encoded at 8–16 kHz. `OTIR` will finish playing a 1-second sample in a fraction of a tenth of a second, resulting in a microscopic high-pitched "blip."

**The Fix:** You must artificially delay the output to match the sample's target frequency. The playback loop *is* the clock.

---

## 6. Decision Matrix: Choosing a DAC

If you are developing a modern game or demo and want to play digital samples, you have four main options. These are **output method choices**, not platform choices — most methods span multiple hardware tracks. The deciding factor is not what machine the user has, but what sound hardware is fitted to it.

| Output Method | Typical Hardware | CPU Load | Quality / Polyphony |
|---|---|---|---|
| **1-Bit Beeper (PWM)** | Any 48K/128K (built-in speaker port) | **100%** (halts game) | 1–4 channels, heavily distorted, gritty. |
| **AY Volume Registers** | Any AY-equipped machine | **100%** (halts game) | 3 channels. 4-bit logarithmic. Quiet and muddy. |
| **Covox / SounDrive** | Any machine with the expansion fitted | **100%** (halts game) | 4 channels. 8-bit linear stereo. Clear, punchy Amiga-like audio. |
| **[General Sound (GS)](gs_general_sound.md)** | Soviet clones with expansion slot | **0%** (fire and forget) | 4 channels, 8-bit. Handled entirely by the GS card's dedicated Z80. |

> [!IMPORTANT]
> These methods are **not exclusive to the platforms listed in column two** — those are simply where each method is most commonly encountered. The AY chip is built into every Pentagon; Covox works fine on an original 128K with a suitable expansion; a 48K without any sound add-on can still do beeper PWM. Choose the method first, then state your hardware requirement honestly to the user.

> [!WARNING]
> **The CPU load column is not a sliding scale.** Beeper, AY-sample, and Covox/SounDrive are all software-driven playback — the CPU is the playback clock. At a 19 kHz sample rate (see [Performance Reality Check](#performance-reality-check) below), a 4-channel SounDrive loop consumes the **entire** ~70,000-T-state frame budget. There is no leftover for any other activities during audible playback exceot brief keyboard polling. The advantage of Covox over AY-sample playback is **audio quality** (8-bit linear vs 4-bit logarithmic, plus true stereo), not CPU savings. Only the GS card actually offloads the CPU.

---

## 7. Use Cases in the Scene

SounDrive transformed the Soviet demoscene. Trackers like **FlashTracker** and **Digital Studio** allowed musicians to compose traditional 4-channel MOD files directly on the Spectrum. Demos like *Satisfaction* and *Illusion* used SounDrive to blast high-fidelity techno tracks while pushing minimal graphics to the screen, proving that the Spectrum could punch far above its weight class when the CPU was freed from audio math.

---

## 8. Comparison With Other PCM Solutions

How does Covox/SounDrive compare to other sample playback options on the ZX Spectrum?

| Feature | Covox (Single) | SounDrive (4-ch) | [General Sound](gs_general_sound.md) | [ZX Next DMA](zx_next_audio.md) |
|---------|----------------|------------------|--------------------------------------|----------------------------------|
| **Channels** | 1 | 4 | 4 | 1 (DMA) + 3×AY |
| **Resolution** | 8-bit | 8-bit | 8-bit | 8-bit |
| **Max Sample Rate** | ~22 kHz | ~19 kHz | 22 kHz | 27.7 kHz |
| **CPU Load** | 100% | 100% | **0%** | **0%** |
| **Stereo** | Mono | True stereo | True stereo | True stereo |
| **Hardware Mixing** | No | Yes | Yes | Yes |
| **Availability** | Common | Soviet clones | Soviet clones | Next only |
| **Year Introduced** | 1987 | 1995 | 1994 | 2017 |

Key observations:

1. **CPU load is the critical differentiator.** Covox and SounDrive require the CPU to be dedicated to playback. General Sound and ZX Next DMA free the CPU entirely.

2. **SounDrive's advantage over single Covox is hardware mixing**, not CPU savings. The Z80 still runs a tight loop, but it doesn't need to do any arithmetic — just fetch-and-output.

3. **General Sound is the "best" Soviet-era solution** if available, but SounDrive is far more common and works on any clone with a spare I/O port.

4. **ZX Next DMA supersedes all of the above** for Next-exclusive projects. See [ZX Spectrum Next Audio](zx_next_audio.md).

---

## 9. Detection and Runtime Probing

Unlike chips with readable status registers, DAC ports are write-only. Detection typically relies on:

1. **Configuration assumptions** — The user tells the software which hardware is present via a setup menu.
2. **Read-back test** — Some SounDrive implementations include a shadow latch that can be read back. Write a known value, read it back, verify.
3. **Probing side effects** — Writing to a non-existent port may cause bus noise or floating values. Not reliable.

For production software, **option 1 (user configuration)** is recommended. The scene convention is a setup utility that stores hardware flags to disk or NVRAM.

```z80
; Simple SounDrive presence check (unreliable — for reference only)
; Many SounDrive implementations don't support read-back
DetectSounDrive:
    ld a, #AA           ; test pattern
    out (#0F), a        ; write to channel A
    in a, (#0F)         ; attempt read-back (may return garbage)
    cp #AA              ; did we get it back?
    ret z               ; Z = probably present
    ; Note: This WILL give false negatives on most implementations
    ret
```

---

## References & Further Reading

### Related Articles in This Knowledge Base

- [Sound Hardware Ecosystem Overview](sound_overview.md) — Decision matrix for choosing between beeper, AY, Covox, SounDrive, General Sound, and Next DMA.
- [General Sound (GS)](gs_general_sound.md) — The coprocessor approach: a dedicated Z80 handles all mixing, freeing the main CPU.
- [ZX Spectrum Next Audio](zx_next_audio.md) — DMA-driven sample playback on the Next — the modern successor to SounDrive.
- [Stereo Audio Techniques](stereo_audio.md) — Panning, stereo width, and mixing strategies applicable to SounDrive.
- [AY/YM Synthesis Techniques](../synthesis/ay_ym_techniques.md) — Why the AY chip is bad at playing samples (and the hacks people tried).
- [I/O Port Map](../../10_references/io_port_map.md) — Complete port decoding for all clones, including SounDrive and Kempston conflicts.

### External References

- [Texas Instruments TLC7226 Datasheet (PDF)](https://www.ti.com/lit/gpn/TLC7226) — Official datasheet for the TLC7226 quad 8-bit DAC used in modern single-chip SounDrive implementations.
- [Mick Laboratory: ZXM-SoundCard](http://micklab.ru/My%20Soundcard/ZXMSoundCard.htm) *(in Russian)* — The best-documented TLC7226-based SounDrive reference. Full schematics, CPLD firmware source, and bill of materials for every board revision (00 through Extreme). The SounDrive part appears in the Middle and Extreme revisions alongside TSFM and SAA1099 sections.
- [Flash Inc. — Original SounDrive Authors](http://flash-inc.net/) *(archived)* — The Russian demoscene group that invented the SounDrive in 1995.
