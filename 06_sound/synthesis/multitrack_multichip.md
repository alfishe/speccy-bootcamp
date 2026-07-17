[← Home](../../README.md) · [Sound](../README.md) · [Synthesis](README.md)

# Multi-Track and Multi-Chip Synthesis — TurboSound, Cross-Chip Effects, Synchronization

> **Applies to**: Soviet clones (TurboSound dual/triple AY), New Gen (ZX Spectrum Next 3× AY), expanded Original hardware (Melodik + TurboSound). Also relevant to Amstrad CPC (PlayCity dual AY) and MSX (multiple PSG configurations).

---

## Overview

A single AY/YM provides three tone channels — enough for melody, bass, and a simple rhythm, but constraining for ambitious compositions. The ZX Spectrum community solved this by stacking multiple AY chips. **TurboSound** (invented in the Soviet clone scene) adds a second AY for six channels. TurboSound FM adds a YM2203 FM chip alongside. The ZX Spectrum Next has three AY chips plus DMA-driven sample playback. This article outlines the techniques for writing music that exploits multiple sound chips simultaneously.

> [!NOTE]
> This article is currently an **outline** — it defines the scope and planned content for a future comprehensive article. Each section below describes what will be covered when the article is fully written.

---

## Planned Content

### 1. TurboSound Architecture

- **Hardware**: Two AY-3-8912/YM2149 chips on a single interface, accessed via a bank-switching port
- **Port decoding**: How the second AY is selected (typically `#FFFD`/`#BFFD` for chip 0, with a bank-select bit for chip 1)
- **Per-clone differences**: Pentagon TurboSound vs Scorpion TurboSound vs ATM Turbo sound expansion
- **Triple AY (TurboSound Next)**: ZX Spectrum Next's three-chip configuration, 9 total channels

### 2. Inter-Chip Synchronization

- **Phase alignment**: The two AY chips run from the same clock, but their internal counters are independent
- **Sync-square across chips**: Extending sync-square techniques to synchronize phase between chips
- **Envelope sharing**: Each chip has its own envelope generator — for the first time, you get **two independent envelopes**
- **Timing requirements**: Per-frame register write budget (14 registers × 2 chips = 28 OUT pairs per frame)

### 3. Channel Allocation Strategies

| Strategy | Chip 0 (AY 1) | Chip 1 (AY 2) | Use Case |
|----------|---------------|---------------|----------|
| **Lead+Accompaniment** | 3 melodic channels | Bass + drums + pads | Traditional arrangement |
| **Dual Stereo** | Left channel L/R/M | Right channel L/R/M | ABC stereo with 6 channels |
| **Dense Arrangement** | Lead + harmony + bass | Counter-melody + drums + effects | Demoscene music |
| **Sample + PSG** | Tone/noise channels | Sample playback (volume modulation) | Digital drums + melodic PSG |

### 4. Cross-Chip Effects

- **Phase interference**: Setting two chips to nearly-identical frequencies for beating/chorus effects
- **Stereo panning tricks**: Using chip-to-chip volume differences to simulate panning
- **Shared noise**: Routing noise from one chip to modulate tones on another (requires hardware modification)
- **Envelope polyphony**: Two independent envelopes enable complex amplitude modulation patterns impossible on a single chip

### 5. Player Routine Architecture for Multi-Chip

- **Register write sequencing**: Optimal order for writing 28+ registers per frame within the ISR time budget
- **Bank switching overhead**: The TurboSound bank-select adds extra OUT instructions — minimizing this cost
- **TurboSound container format (.TS)**: How multi-chip modules are stored
- **Arkos Tracker multi-PSG**: How AT2/AT3 handles unlimited PSG count in the player

### 6. Beyond AY — Mixed-Chip Systems

- **TurboSound FM (YM2203)**: 3 FM channels + 3 SSG channels alongside a standard AY
- **General Sound**: Dedicated Z80 sound card with independent sample mixing
- **MoonSound (OPL4)**: Wavetable synthesis alongside PSG
- **SAA1099 (ZXM Soundcard)**: Philips PSG as an additional sound source
- **ZX Spectrum Next DMA audio**: Hardware sample playback independent of AY channels

### 7. Timing Budget Analysis

```
Per-frame budget at 50 Hz:
  Total T-states/frame:    69,888 (48K) or 71,680 (Pentagon)
  Minus ISR overhead:      ~500 T-states (register save/restore)
  Minus display effect:    ~20,000-40,000 (if doing multicolor)
  
  Available for music:     ~30,000-50,000 T-states
  
  Single AY (14 registers, 2 OUTs each = 28 OUTs):
    28 × 21 T-states = 588 T-states → plenty of headroom
    
  TurboSound (28 registers, 4 OUTs each = 56 OUTs + bank selects):
    56 × 21 + ~10 bank selects × 21 = ~1,400 T-states → still fine
    
  Triple TurboSound (42 registers):
    ~2,100 T-states → acceptable
```

---

## Cross-References

- [AY/YM Sound Generation](ay_ym_synthesis.md) — Single-chip synthesis techniques (prerequisite reading)
- [Sound Section Index](../README.md) — Sound hardware catalog including TurboSound
- [128K Memory and I/O](../../05_development/03_memory_and_io/memory_and_io_128k.md) — AY port decoding
- [I/O Port Map](../../10_references/io_port_map.md) — TurboSound port addresses

---

## References

- [TurboSound documentation](https://velesoft.speccy.cz/turbosound-cz.htm) — Velesoft
- [Arkos Tracker — unlimited PSG](https://www.julien-nevo.com/arkostracker/) — multi-chip composition tool
- [ZX Spectrum Next audio](https://specnext.dev/) — 3× AY + DMA configuration
