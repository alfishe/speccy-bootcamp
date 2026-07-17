[← Home](../../README.md) · [Sound](../README.md) · [Synthesis](README.md)

# The AY Sound — Perception, Emotion, and the Hardware Soul

> **Applies to**: AY-3-8910/8912 and YM2149 on all platforms — ZX Spectrum, Atari ST, Amstrad CPC, MSX. This article bridges the gap between the technical architecture (covered in [AY/YM Sound Generation](ay_ym_synthesis.md)) and the human experience of the sound.

---

## Why This Article Exists

You can write a bit-perfect AY emulator. You can sample every register write at the exact clock rate. You can model the logarithmic DAC with 16-bit precision. And it will still sound *wrong* — not technically wrong, but emotionally wrong. The sound will lack something that the original hardware had. A sharpness. A presence. A *soul*.

This article is about that gap. It covers the holy wars (ABC vs ACB, AY vs YM), the psychoacoustics of square waves, the analog circuitry that colors the sound, and the deep nostalgia that makes grown adults argue passionately about a 1978 sound chip. It is written for:

- **Emulator authors** who want to understand why their output sounds "cold" compared to hardware
- **Musicians** who want to choose the right routing and chip variant for their aesthetic goals
- **Hardware enthusiasts** trying to recapture the exact sound of their childhood
- **Anyone curious** why a primitive square-wave chip produces an emotional response that a modern synthesizer cannot

---

## The ABC vs ACB Holy War

### What Is ABC and ACB?

The AY has three output channels: A, B, and C. On original hardware, these are mixed to a single mono output. But stereo modifications — present on many Soviet clones and all modern hardware (ZX Spectrum Next, DivMMC, etc.) — route the channels to separate left/right speakers. The question is: **which channel goes where?**

| Routing | Left | Center (both) | Right | Origin |
|---------|------|---------------|-------|--------|
| **ABC** | Channel A | Channel B | Channel C | Western Europe (Amstrad, MSX tradition) |
| **ACB** | Channel A | Channel C | Channel B | Eastern Europe (Pentagon, Soviet clone tradition) |

In ABC routing, channel B sits in the center. In ACB, channel B sits on the right, and C is centered. This seemingly trivial swap completely changes how music *feels*.

### Why It Matters

The AY has exactly three channels. Most AY music follows a convention:

- **Channel A** — Lead melody (panned left in both systems)
- **Channel B** — Bass line or accompaniment
- **Channel C** — Rhythm, counter-melody, or arpeggio continuation

In **ABC**, the bass (channel B) is centered. This feels natural — bass anchors the center of the stereo field, like a kick drum or bass guitar in a modern mix. The lead is on the left, rhythm on the right. This is the "Western" approach: balanced, conventional, warm.

In **ACB**, the rhythm/counter-melody (channel C) is centered, and the bass (channel B) is on the right. This sounds more aggressive — the bass moves to one side, creating an asymmetric energy. The center is occupied by fast arpeggios or rhythmic elements, giving the sound a driving, hypnotic quality. This is the "Soviet" approach: intense, driving, slightly unbalanced in a way that grabs attention.

### Why the Holy War

The debate is intense because **both sides are right**:

- **Western composers** (primarily using the ZX Spectrum 128K, Amstrad CPC, MSX) wrote music *hearing* ABC routing. Their bass was meant to be centered. Playing their music in ACB pushes the bass to the right and sounds "wrong" — unbalanced, distracting.

- **Soviet composers** (primarily on Pentagon clones with stereo modifications) wrote music *hearing* ACB routing. Their arpeggios were meant to be centered, driving the energy. Playing their music in ABC pushes the arpeggios to the right and sounds "flat" — missing the hypnotic central pulse that defines the Soviet chiptune aesthetic.

The ZX Spectrum Next recognized this by making the routing **software-selectable** (TBBlue register `#08`, bit 5). This is the pragmatic solution: let the music itself declare which routing it was composed for.

### The Mono Purist Position

A third faction argues that **both stereo routings are wrong** — the original ZX Spectrum 128K had mono output, and all AY music was composed for mono. The stereo modifications are a post-hoc addition that the composers never intended. This is technically correct for original Western music, but ignores the Soviet reality where stereo mods were ubiquitous by the mid-1990s and composers actively exploited them.

> [!TIP]
> **For emulator authors**: Always provide a mono option. Many AY music files (.AY, .PSG) are mono captures. If you force stereo routing on mono content, you create an artificial soundstage that the original composer never intended. Conversely, if you provide stereo, always let the user choose ABC or ACB.

---

## AY vs YM — More Than a Name

The General Instrument AY-3-8910 (1978) and the Yamaha YM2149 (early 1980s) are often described as "the same chip." They are pin-compatible, register-compatible, and most software runs identically on both. But they are not the same chip. The differences are subtle, measurable, and — to the trained ear — audible.

### The Envelope Resolution Difference

The most significant documented difference is the **envelope generator resolution**:

| Feature | AY-3-8910/8912 | YM2149 |
|---------|----------------|--------|
| Envelope steps | **16** (4-bit) | **32** (5-bit) |
| Volume table | 16 logarithmic levels | 32 logarithmic levels |
| Envelope shape smoothness | Stepped, grainy | Smoother transitions |

The YM2149's 32-step envelope produces noticeably smoother volume sweeps. This matters most for **buzzer bass** and other techniques that use the envelope as an audio-rate oscillator (see [AY/YM Sound Generation](ay_ym_synthesis.md) §5). On the AY-3-8912, these techniques sound more grainy and quantized. On the YM2149, the same code produces a rounder, warmer tone.

The ZX Spectrum uses the **AY-3-8912** (16-step envelope). The Atari ST uses the **YM2149F** (32-step). This is one reason why Atari ST chiptunes often sound "smoother" than ZX Spectrum chiptunes, even though the synthesis techniques are identical.

### The DC Offset

This is the difference that emulator authors cannot agree on:

- **YM2149**: The output includes a **2V DC offset**. Every channel sits at +2V when silent. This DC component is present in the analog output at all times.
- **AY-3-8910**: When a channel's fixed volume is set to 0 (envelope disabled), the output is **0V** — the channel is truly off. When the envelope is active, a small DC offset (~0.2V) appears.

This sounds trivial, but it has real consequences:

1. **Channel interaction**: When three channels are summed in an analog mixer, their DC offsets interact. On the YM2149, all three channels contribute +2V, creating a +6V baseline that the mixing circuit must handle. This pushes the analog stage into a different part of its operating range, subtly changing the harmonic content.

2. **Highpass filter effect**: The DC blocking capacitor in the output circuit acts as a **highpass filter** at ~15-20 Hz. On the YM2149, the constant DC offset means the filter is always "engaged" — low frequencies below 20 Hz are attenuated. On the AY-3-8910, with channels turning fully off, the DC level fluctuates, creating a subtle "breathing" effect as the filter responds to changes.

3. **Emulation headaches**: Most emulators ignore the DC offset entirely. The MAME AY driver, for example, models the YM2149's 2V DC offset but treats the AY-3-8910 differently based on whether the envelope is active. No two emulator implementations agree on the exact values. This is why the same .PSG file sounds different in different players.

### The SEL Pin (YM2149 Only)

The YM2149 has an extra pin (pin 26, `SEL`) that the AY-3-8910 lacks. When pulled low, this pin **halves the envelope generator clock rate**. On the Atari ST, this pin is wired to allow software selection of envelope speed. The AY-3-8910 has no such capability — its envelope always runs at the standard rate.

This means that Atari ST music using the SEL feature will play with the wrong envelope timing on a ZX Spectrum, and vice versa. Most .YM and .PSG files encode the clock frequency but do not specify the SEL state, creating another source of cross-platform incompatibility.

### The Volume Table Chaos

Every AY/YM emulator uses a slightly different volume table. This is not laziness — it reflects genuine hardware variation:

```
Emulator/Source     Volume table basis
─────────────────────────────────────────
MAME (measured)     Hardware oscilloscope measurements
MAME (formula)      exp(i/2 - 7.5) — mathematical approximation
ZEsarUX             Own measured values
Fuse                Based on MAME tables
AYEmul              Sergey Bulba's measurements
Vortex Tracker      Bulba's measurements (different from AYEmul)
Furnace             Configurable: AY-3-8910 or YM2149 modes
```

The truth is that **no two AY chips have identical volume tables**. The logarithmic DAC is implemented as a physical resistor ladder on silicon. Manufacturing tolerances in the resistor values mean that every chip has slightly different amplitude steps. This is not a defect — it is the nature of analog hardware. The variation is small (a few percent between steps) but audible to trained ears.

> [!NOTE]
> **Why this matters emotionally**: The volume table determines the *character* of the sound — the exact harmonic balance of each note, the way notes blend in a chord, the perceived "warmth" of the timbre. When an emulator uses a mathematical approximation instead of real hardware measurements, the character changes subtly. The sound becomes *correct* but loses its *identity*.

### Summary: Which Chip for Which Aesthetic?

| Goal | Chip | Why |
|------|------|-----|
| Authentic ZX Spectrum sound | AY-3-8912 | 16-step envelope, ZX-specific volume table, correct DC behavior |
| Authentic Atari ST sound | YM2149F | 32-step envelope, 2V DC offset, SEL envelope control |
| Soviet clone authenticity | AY-3-8912 or YM2149F | Both were used; check the specific clone's schematic |
| "Smoothest" chiptune | YM2149F emulation | 32-step envelope creates the silkiest volume sweeps |
| "Grittiest" chiptune | AY-3-8912 emulation | 16-step grain adds raw character |

---

<!-- Continued: Section 3 -->

## The Analog Soul — Why Real Hardware Sounds Different

If you take a bit-perfect register dump (.PSG file) and play it through a modern emulator, then play the same dump on real hardware through a CRT television, the difference is immediately obvious. The hardware sounds warmer, punchier, more "alive." The emulator sounds cleaner, thinner, more "digital." This is not imagination — it is physics. Between the AY chip's digital register values and your ear, the signal passes through an **analog signal chain** that fundamentally transforms the sound.

### Stage 1: The Internal DAC

The AY/YM converts digital volume levels to analog voltage using an internal **resistor-ladder DAC**. This is not a modern precision DAC — it is a set of polysilicon resistors on the chip die, with manufacturing tolerances of ±5-20%. The result:

- **Non-uniform step sizes**: The logarithmic spacing between volume levels is approximate. Some steps are wider, some narrower, creating an irregular harmonic signature unique to each chip.
- **Glitch energy**: When the DAC switches between levels, brief transient spikes (glitches) appear in the output. These are not modeled by any emulator. They add a subtle "fizz" to envelope transitions — the sound of electricity moving through imperfect silicon.
- **Temperature drift**: As the chip warms up, resistor values change slightly. A cold AY chip sounds marginally different from one that has been running for an hour. This is completely absent from emulation.

### Stage 2: The Output Coupling Circuit

The AY's analog output does not go directly to a speaker. On the ZX Spectrum 128K, it passes through:

```
AY output → coupling capacitor → RC lowpass filter → mixing resistor → amplifier → speaker/TV
```

Each component colors the sound:

- **Coupling capacitor** (typically 1-10 µF): Blocks DC, acts as a **highpass filter** at ~15-50 Hz. This removes sub-bass rumble but also removes the bottom octave of buzzer-bass lines. The exact cutoff depends on the capacitor value and condition — and capacitors drift with age. A 30-year-old electrolytic capacitor in a Spectrum 128K has different characteristics than when it was new.

- **RC lowpass filter** (typically 1-10 kΩ + 1-10 nF): Smooths the harsh edges of the square wave, creating a **cutoff around 15-30 kHz**. This seems irrelevant (above human hearing) but matters because it **removes aliasing artifacts** that the ear can perceive as harshness. Real hardware cannot produce frequencies above its analog bandwidth. Emulators sampling at 44.1 kHz can produce ultrasonic artifacts that, when played through modern equipment, create an uncomfortable "digital" harshness.

- **Mixing resistor network**: On mono hardware, the three channels are summed through resistors. This is not a perfect mathematical sum — the resistors have tolerances, and the finite output impedance of the AY means channels interact. When channel A outputs a high level, it slightly loads the power rail, momentarily affecting channels B and C. This **interchannel crosstalk** is subtle but adds a "glue" — the channels sound connected, like musicians playing in the same room. Digital summing (as in emulators) produces perfectly isolated channels that sound sterile by comparison.

### Stage 3: The Amplifier and Speaker

On a real ZX Spectrum connected to a CRT television, the audio goes through:

- The Spectrum's internal 1-watt amplifier (a simple LM386 or transistor circuit)
- The TV's audio input stage
- The TV's speaker (typically a 2-3 inch full-range driver with limited bass response and prominent midrange coloration)

This stage adds enormous character:

- **Speaker distortion**: Small TV speakers produce harmonic distortion at higher volumes. A square wave at 440 Hz produces distortion products at 880 Hz, 1320 Hz, 2200 Hz — the speaker *adds* harmonics that were not in the original signal. These harmonics are perceived as "warmth" and "presence."
- **Cabinet resonance**: The TV cabinet resonates at certain frequencies, boosting specific notes and creating a formant character. This is why a Spectrum sounds different through a Philips TV than through a Sony TV.
- **Volume-dependent response**: At low volume, the speaker is nearly linear. At high volume, bass and treble are compressed, making the midrange more prominent. Most childhood memories involve the volume turned up — which means the "Spectrum sound" in your memory includes speaker compression.

### Stage 4: The Room

The final stage is the acoustic environment. A CRT television in a 1980s bedroom produces reflections, absorptions, and resonances that color the sound. This is the most personal factor — your childhood room is literally part of the sound you remember. No emulator can reproduce this.

### Why Emulation Sounds "Cold"

Putting it all together, here is what a typical emulator misses:

| Stage | Real Hardware | Typical Emulator |
|-------|---------------|------------------|
| DAC nonlinearity | Chip-specific irregular steps | Mathematical `exp()` curve |
| DAC glitch energy | Transient spikes on transitions | None |
| Temperature drift | Subtle parameter change over time | Static |
| DC blocking capacitor | Highpass at 15-50 Hz, age-drifted | Usually 0 Hz (flat) or crude approximation |
| RC lowpass filter | Gentle 15-30 kHz rolloff | None, or brick-wall at Nyquist |
| Channel crosstalk | Resistive summing, rail loading | Perfect digital sum, zero interaction |
| Speaker distortion | Harmonic enrichment at volume | None |
| Speaker coloration | Midrange prominence, bass rolloff | Flat response |
| Room acoustics | Personal, irreplaceable | None |

The result is that a **perfect emulator** produces a signal that is mathematically correct but perceptually impoverished. The analog stages that emulators skip are the exact stages that give the AY its *character* — the grit, the warmth, the "soul."

---

<!-- Continued: Section 4 -->

## Psychoacoustics of the Square Wave

Why does a primitive square wave from a 1978 chip trigger a stronger emotional response than a pristine 24-bit recording of a real instrument? The answer lies in how the human auditory system processes sound.

### The Harmonic Series of a Square Wave

A perfect square wave at frequency *f* contains only **odd harmonics**: *f*, 3*f*, 5*f*, 7*f*, 9*f*, ... with amplitudes decreasing as 1/n:

```
Amplitude of nth harmonic = 1/n (for odd n only)

Example: 440 Hz square wave
  Fundamental:     440 Hz  (1.0)
  3rd harmonic:   1320 Hz  (0.33)
  5th harmonic:   2200 Hz  (0.20)
  7th harmonic:   3080 Hz  (0.14)
  9th harmonic:   3960 Hz  (0.11)
  ...
```

This is an incredibly rich spectrum. A sine wave at 440 Hz contains only the fundamental — it sounds pure, clean, and emotionally neutral. A square wave at 440 Hz contains dozens of audible harmonics, creating a sound that is bright, buzzy, and full of energy. The harmonic richness is what makes the AY sound "alive" — every note is a complex chord of frequencies, not a single tone.

The human ear evolved to analyze harmonic series. Real-world sounds — vocal cords, violin strings, brass tubes — all produce harmonic series. The brain uses harmonics to identify timbre, estimate distance, and extract emotional content. A square wave's harmonic series is *simpler* than any acoustic instrument (only odd harmonics, perfectly spaced), which makes it easy for the brain to process. This is why chiptune is often described as "clear" or "pure" despite being technically distorted.

### The Missing Fundamental Effect

When the AY plays a low note (say, 55 Hz for buzzer bass), the small TV speaker cannot reproduce 55 Hz — it is below the speaker's resonance frequency. But the harmonics at 165 Hz, 275 Hz, 385 Hz *are* reproduced. The brain **reconstructs the missing fundamental** from the harmonic spacing. You "hear" 55 Hz even though the speaker never produces it.

This psychoacoustic effect means that the AY's bass is largely a **brain-generated phantom**. The chip and speaker provide the harmonics; your auditory cortex fills in the fundamental. This is why AY bass sounds different on different speakers — and why headphones produce weaker bass than a CRT TV (headphones reproduce more of the actual low frequencies, paradoxically making the phantom fundamental weaker because the brain doesn't need to reconstruct it).

### Volume Quantization and "Chiptune Character"

The AY's 16 logarithmic volume levels create a distinctive **staircase envelope**. Each step is a 3 dB jump (roughly). The human ear perceives this quantization as a **flutter** or **tremolo** effect — a rapid amplitude modulation that adds a metallic, electronic character.

This is not a defect. It is the defining aesthetic of chiptune. Modern synthesizers with 16-bit volume resolution produce smooth, continuous envelopes that sound "professional" but lack the chiptune *edge*. The quantization is the point — it is the sonic fingerprint of the hardware.

The YM2149's 32-step envelope is still quantized, but the steps are ~1.5 dB apart — fine enough that the flutter is less prominent. This is one reason why YM2149 chiptunes sound "smoother" — the quantization flutter is below the perceptual threshold for most listeners.

### The Logarithmic Volume Illusion

The AY's volume levels are **logarithmic**, not linear. This means equal register steps correspond to equal *perceived* volume increments, not equal amplitude increments. This is actually correct for human perception (which is logarithmic) and means that volume fades sound natural and musical.

But the logarithmic spacing has a side effect: the **signal-to-noise ratio** changes with volume. At volume 15 (maximum), the signal-to-noise ratio is at its best. At volume 1, the signal is so quiet that analog noise (hiss from the amplifier, hum from the power supply) becomes prominent relative to the signal.

This means quiet AY notes are **noisier** than loud ones. This is completely natural — acoustic instruments behave the same way (a softly played violin has more bow noise relative to tone than a loudly played one). Emulators with a flat noise floor cannot reproduce this effect. The result: emulated quiet passages sound "too clean" compared to hardware.

### Why Two Identical Square Waves Sound Different

A square wave at 440 Hz from the AY, from a SID, from a NES, and from a modern synthesizer all contain the same harmonic series. Yet they sound completely different. Why?

1. **DAC characteristics**: Each chip's DAC has different nonlinearity, creating different harmonic *amplitudes* — the 3rd harmonic might be slightly louder on an AY than on a SID.

2. **Clock precision**: The AY's clock is derived from a crystal oscillator. Crystal oscillators have phase noise and micro-jitter that creates a **chorusing** effect — the frequency is not perfectly stable. This is absent from emulators using perfectly stable numerical oscillators.

3. **Channel interaction**: On the AY, playing a note on channel A slightly affects the power rail, which slightly affects channels B and C. This creates a form of **amplitude modulation** between channels — a organic, constantly-changing interplay that a digital mixer cannot reproduce.

4. **Bandwidth**: Each chip's analog output stage has a different bandwidth. The AY's simple RC filter rolls off above ~20 kHz. The SID's filter is programmable. The NES has a more complex output stage. These differences create different **high-frequency content**, which the ear perceives as "brightness" or "harshness."

### The Appeal of Constraint

Psychoacoustics explains *how* we hear the AY, but not *why* we like it. Part of the answer is **constraint aesthetics** — the appeal of art created under extreme limitation.

The AY gives you three channels, 16 volume levels, one envelope, and a noise generator. Every musical decision is a compromise. The composer must choose: will the envelope go to the bass or the lead? Will channel C carry noise for a hi-hat, or arpeggios for a counter-melody? These constraints force creative solutions that would never emerge with unlimited resources.

The listener perceives this struggle. The brain recognizes that the music is working *hard* — that every note is precious because there are so few of them. This creates a form of **aesthetic respect** that enhances the emotional impact. A modern synthesizer with 128-voice polyphony and 24-bit effects cannot trigger this response — the listener knows the resources are unlimited, so the music feels less precious.

This is why chiptune continues to thrive as a genre long after the hardware became obsolete. The limitation *is* the art.

---

<!-- Continued: Section 5 -->

## Nostalgia and Emotional Resonance

The technical explanations above describe *what* is different between hardware and emulation. But they do not fully explain *why it matters*. The AY sound is not just a set of frequencies — it is a **memory trigger** of extraordinary power.

### The Proust Effect

Marcel Proust described how the taste of a madeleine cake dipped in tea unleashed a flood of childhood memories. Sound is the most powerful sense for triggering involuntary memory — more than sight or smell. The AY's specific tonal palette, its specific distortion, its specific frequency response, is permanently encoded in the memory of everyone who grew up with a ZX Spectrum.

This is why a "perfect" emulation fails emotionally even when it succeeds technically. The brain is not comparing the emulation to a reference recording — it is comparing it to a **memory**. And memories are not recordings — they are reconstructions, amplified by emotion, colored by nostalgia. The remembered sound is always louder, brighter, more exciting than the original ever was. No reproduction can match a memory, because the memory is not a copy — it is a *feeling*.

### Generational Identity

For the generation that grew up in the Soviet Union and post-Soviet states in the 1990s, the ZX Spectrum (specifically, the Pentagon clone) was *the* computer. Its sound is the soundtrack of a generation. The AY's buzz is not just a sound — it is a cultural identifier, a badge of belonging. This is why the ABC vs ACB debate is so fierce among Russian-speaking enthusiasts: it is not just about channel routing, it is about *whose childhood was real*.

Similarly, for Western European children of the 1980s, the ZX Spectrum 128K's AY sound (often through a small mono TV speaker) defines a specific era and social class. The Sinclair sound is different from the Commodore sound, the Amstrad sound, the Atari sound. Each chip sound is a key to a specific world.

### The Loneliness of the Chiptune

There is a quality to AY music that is hard to describe but universally recognized by those who grew up with it: a kind of **noble loneliness**. Three square-wave channels, playing alone in a bedroom, through a small speaker, late at night. The music was not background music — it was the *only* sound in the room. It demanded attention because it was the sole occupant of the auditory space.

Modern music comes through headphones that block the world, or through surround-sound systems that fill the room. The AY came through a mono TV speaker that was *part of the room*. The music and the environment were fused. This is a quality that no listening setup can fully reproduce today — the room is different, the time is different, *you* are different.

---

## Recapturing the Sound — A Practical Guide

You cannot go back to 1988. But you can get closer to the original AY experience. Here are practical recommendations, from most to least authentic.

### Tier 1: Real Hardware (Most Authentic)

The only way to hear the true AY sound is through the actual chip:

1. **Real ZX Spectrum 128K / +2** with a CRT television. The AY-3-8912, the original analog circuit, the TV speaker — this is the reference. Mono. No stereo mods. This is what the music was composed for.

2. **Real Pentagon** (or other Soviet clone) with stereo modification. If your goal is the Soviet chiptune experience, this is the authentic path. ACB routing. The Pentagon's specific analog circuit (often hand-soldered, with Soviet-era components) has its own coloration.

3. **ZX Spectrum Next** with correct configuration: select the right AY chip, set ABC or ACB per the music's origin, use the analog audio output (not HDMI). The Next's FPGA-implemented AY is cycle-accurate but the analog output stage is different from original hardware.

### Tier 2: Emulation with Analog Modeling (Good Balance)

If real hardware is impractical, configure your emulator to approximate the analog chain:

1. **Choose the right chip model**: Set the emulator to AY-3-8912 for ZX Spectrum music, YM2149F for Atari ST music. This matters — the envelope resolution and DC behavior are different.

2. **Set the correct clock frequency**: 1.7734 MHz for ZX Spectrum 128K, 1.75 MHz for Pentagon, 2.0 MHz for Atari ST. Getting this wrong changes every note's pitch and the envelope speed.

3. **Enable highpass filtering**: Set a DC blocking filter at ~20 Hz. This mimics the coupling capacitor. Without this, the sound has an unnatural DC offset that colors the low end.

4. **Enable lowpass filtering**: Set a gentle rolloff at ~15-18 kHz. This mimics the RC filter and removes ultrasonic aliasing artifacts. A simple one-pole filter is sufficient — do not use a brick-wall filter, as the gradual rolloff is part of the character.

5. **Select the correct stereo routing**: ABC for Western music, ACB for Soviet music. If unsure, use mono — it is always safe.

6. **Add subtle noise**: A small amount of white noise (~-60 dB) mimics the analog noise floor. This sounds crazy, but it works — the noise gives the digital signal an analog "bed" that the brain interprets as authenticity.

### Tier 3: Post-Processing (If Your Emulator Lacks Analog Modeling)

If you are stuck with a basic emulator, you can approximate the hardware sound with post-processing:

- **EQ**: Roll off below 50 Hz (highpass), roll off above 16 kHz (lowpass). Boost slightly around 2-4 kHz to mimic TV speaker midrange prominence.
- **Saturation**: A subtle tube or tape saturation plugin adds harmonic content that mimics amplifier and speaker distortion. Keep it subtle — you want warmth, not crunch.
- **Stereo width**: If the music was composed for mono, do not widen it. If it was composed for stereo, do not collapse it. The original spatial presentation is part of the composition.
- **Reverb**: A tiny amount of room reverb (very short decay, ~100 ms) mimics the acoustic of a small room with a TV. This is the most controversial suggestion — purists will object — but it helps bridge the gap between headphones and the room experience.

### Tier 4: Speaker Choice (The Cheat Code)

The single biggest improvement you can make to emulated AY sound is to **change your speakers**:

- **CRT TV speaker**: If you still have a CRT TV with audio input, connect your computer's audio output to it. The TV's speaker and amplifier will do more to recreate the original sound than any software processing.

- **Small full-range speaker**: A single small (2-3 inch) full-range driver, driven by a basic amplifier, approximates the TV speaker experience. The limited frequency response and inherent distortion are features, not bugs.

- **Avoid high-fidelity headphones**: Premium headphones reproduce the AY's harmonics *too accurately*, exposing the digital harshness that the TV speaker would have masked. Cheap earbuds, paradoxically, often sound more "authentic" for chiptune than audiophile headphones.

### Quick Reference: Getting It Right

| Setting | ZX Spectrum 128K | Pentagon | Atari ST |
|---------|-----------------|----------|----------|
| Chip | AY-3-8912 | AY-3-8912 or YM2149F | YM2149F |
| Clock | 1.7734 MHz | 1.75 MHz | 2.0 MHz |
| Stereo routing | Mono (or ABC) | ACB | Mono (or ABC) |
| Highpass | ~20 Hz | ~20 Hz | ~20 Hz |
| Lowpass | ~16 kHz | ~16 kHz | ~18 kHz |
| Noise floor | -55 to -60 dB | -55 to -60 dB | -50 to -55 dB |

---

## Cross-References

- [AY/YM Sound Generation](ay_ym_synthesis.md) — the technical companion: counter model, register mechanics, synthesis techniques
- [Stereo Audio Modifications](../hardware/stereo_audio.md) — ABC vs ACB hardware wiring
- [AY/YM PSG Hardware](../hardware/ay_3_8912.md) — chip variants, pinouts, electrical characteristics
- [Sound Hardware Overview](../hardware/sound_overview.md) — the full hardware ecosystem
- [Cycle-Exact Emulation Accuracy](../../11_emulation/software/cycle_exact_accuracy.md) — AY clock accuracy in emulation

---

## References

- MAME AY8910 driver source code — documents the DC offset difference and volume table measurements
- nesdev.org AY-3-8910 / YM2149 emulation thread — detailed technical discussion of envelope and DAC differences
- ZX Spectrum Next TurboSound Next documentation — ABC/ACB selection via TBBlue register
- vgmrips.net forum — AY vs YM envelope resolution discussion
- Sergey Bulba's AYEmul — measured volume tables from real hardware
- Furnace tracker documentation — configurable AY-3-8910 / YM2149 emulation modes

---

> *"It's not the notes that make the music — it's the silence between them. And it's not the chip that makes the sound — it's the room, the speaker, and the memory."*
