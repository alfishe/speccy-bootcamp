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

### SounDrive v1.05 Port Map

SounDrive uses incomplete address decoding, checking only the low byte (`A7–A0`).

| Channel | Port | Decoding | Pan | Notes |
|---------|------|----------|-----|-------|
| **A** | `#0F` | `xxxxxxxx00001111` | Left | |
| **B** | `#1F` | `xxxxxxxx00011111` | Right | *Conflicts with Kempston Joystick!* |
| **C** | `#4F` | `xxxxxxxx01001111` | Right | |
| **D** | `#5F` | `xxxxxxxx01011111` | Left | |

> [!WARNING]
> **The Kempston Collision:** Port `#1F` is the canonical address for the Kempston Joystick. If a user has a cheap Kempston interface with poor address decoding plugged in alongside a SounDrive, writing a sample to channel B will cause a bus collision.

### Why This Changed Everything

With SounDrive, the Z80 no longer has to do any math. It just fetches a byte for Channel A and throws it at `#0F`. It fetches a byte for Channel B and throws it at `#1F`. The analog circuitry handles the addition instantly. This removed the software mixing bottleneck, allowing developers to write incredibly tight, unrolled playback loops that pushed the ZX Spectrum's sample rate into the 15–20 kHz range—rivaling the Amiga.

![Software vs Hardware Mixing](assets/soundrive_mixing_comparison.svg)

---

## 4. Practical Implementation

To get high-quality audio, the sample output loop must be as tight as physically possible. Every wasted T-state drops the sample rate and muddies the treble frequencies.

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

If you are developing a modern game or demo and want to play digital samples, you have four main options:

| Target Hardware | Output Method | CPU Load | Quality / Polyphony |
|---|---|---|---|
| **Original 48K** | [1-Bit Beeper (PWM)](../synthesis/beeper_synthesis.md) | **100%** (halts game) | 1-4 channels, heavily distorted, gritty. |
| **Original 128K** | [AY Volume Registers](../synthesis/ay_ym_techniques.md) | **100%** (halts game) | 3 channels. 4-bit logarithmic. Quiet and muddy. |
| **Pentagon / Clones** | **Covox / SounDrive** | **95%** (leaves tiny slice for logic) | 4 channels. 8-bit linear stereo. Clear, punchy Amiga-like audio. |
| **High-End Clones** | **[General Sound (GS)](gs_general_sound.md)** | **0%** (Fire and forget) | 4 channels, 8-bit. Handled entirely by the GS card's dedicated Z80! |

---

## 7. Use Cases in the Scene

SounDrive transformed the Soviet demoscene. Trackers like **FlashTracker** and **Digital Studio** allowed musicians to compose traditional 4-channel MOD files directly on the Spectrum. Demos like *Satisfaction* and *Illusion* used SounDrive to blast high-fidelity techno tracks while pushing minimal graphics to the screen, proving that the Spectrum could punch far above its weight class when the CPU was freed from audio math.

---

## References & Further Reading

- [I/O Port Map](../../10_references/io_port_map.md) — Complete port decoding for all clones, including SounDrive and Kempston conflicts.
- [AY/YM Hardware Synthesis](../synthesis/ay_ym_synthesis.md) — Why the AY chip is bad at playing samples.
- [General Sound (GS)](gs_general_sound.md) — The ultimate solution: putting a second Z80 entirely in charge of the audio.
