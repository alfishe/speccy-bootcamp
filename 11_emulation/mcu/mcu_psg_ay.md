[← Home](../../README.md) · [Emulation](../README.md) · [MCU Emulation](README.md)

# AY-3-8912 PSG on a Microcontroller

The **AY-3-8912** (and its siblings AY-3-8910, AY-3-8913, YM2149, and the Russian KR1518VG94) is the sound chip used in the Spectrum 128K, +2, +2A, +3, and all Russian clones (Pentagon, Scorpion, ATM Turbo, ZX Evolution). It is a 3-voice **Programmable Sound Generator (PSG)** that produces tones, noise, and envelopes. Original chips are still available but increasingly scarce and prone to failure after 35+ years. Replacing the PSG with a modern MCU is a popular upgrade — both to repair failed sound chips and to enhance audio (e.g., adding stereo output or higher-quality DACs).

This article covers the AY-3-8912's register interface, the implementation of MCU-based replacements, audio output techniques, and existing projects. For the broader context of MCU-based chip replacement, see [mcu_z80.md](mcu_z80.md) and [mcu_ula.md](mcu_ula.md).

---

## The AY-3-8912 PSG

### Chip Family

The **AY-3-8910/8912/8913** family was designed by **General Instrument (GI)** in the late 1970s. The chips differ only in package:

- **AY-3-8910** — 40-pin DIP, with two 8-bit I/O ports (port A and port B)
- **AY-3-8912** — 28-pin DIP, with one 8-bit I/O port (port A only) — the version used in the Spectrum 128K and later
- **AY-3-8913** — 24-pin DIP, with no I/O ports

The **YM2149** (Yamaha) is a pin-compatible clone with slightly improved audio quality (better DACs). The **KR1518VG94** is the Russian clone.

All variants share the same register interface and produce the same set of sounds. Software written for one runs on all of them.

### Registers

The PSG has 16 registers, each 8 bits:

| Register | Function | Bits |
|---|---|---|
| R0 | Tone A period (fine) | 8 |
| R1 | Tone A period (coarse) | 4 |
| R2 | Tone B period (fine) | 8 |
| R3 | Tone B period (coarse) | 4 |
| R4 | Tone C period (fine) | 8 |
| R5 | Tone C period (coarse) | 4 |
| R6 | Noise period | 5 |
| R7 | Enable: tone/noise per channel + I/O | 8 |
| R8 | Channel A amplitude | 5 (M0–M4) |
| R9 | Channel B amplitude | 5 |
| R10 | Channel C amplitude | 5 |
| R11 | Envelope period (fine) | 8 |
| R12 | Envelope period (coarse) | 8 |
| R13 | Envelope shape/cycle | 4 |
| R14 | I/O port A data | 8 |
| R15 | I/O port B data (8910 only) | 8 |

The host writes to these registers via a 2-step protocol:

1. Write the register number to the **address latch** (via a specific I/O port)
2. Write the data byte to the **data register** (via another I/O port)

On the Spectrum 128K, the address port is `#FFFD` and the data port is `#BFFD`. Reads from `#FFFD` return the currently-selected register's value.

### Sound Generation

Each channel (A, B, C) produces sound by combining:

- A **square wave** at a frequency determined by the channel's tone period register (12-bit period, with frequency = clock / (16 × period))
- The **noise generator** output if enabled (5-bit period, based on an LFSR)
- An **amplitude** controlled either directly (5-bit) or via the **envelope generator**

The envelope generator produces a time-varying amplitude based on:

- The envelope period register (16-bit)
- The envelope shape register (4 bits, selecting one of 16 envelope shapes — attack, decay, sustain, release combinations)

The output of each channel is mixed and sent to a single audio output (or, on the Spectrum 128K, three separate outputs that are combined externally).

### Clock Frequency

The PSG is clocked at a specific frequency that determines the tone frequencies. On the Spectrum 128K, the clock is derived from the CPU clock divided by 2 — giving approximately **1.7734 MHz** (3.5469 MHz / 2). The YM2149 in some clones runs at a slightly different clock (1.75 MHz or 2 MHz), producing subtly different pitch.

On the Pentagon and other Russian clones, the PSG clock is often **1.75 MHz** (using a different divider chain), which gives a slightly different pitch for the same register values — software written for the Spectrum 128K plays slightly out of tune on a Pentagon.

---

## Why Replace the PSG with an MCU?

### Component Failure

The AY-3-8912 has several common failure modes:

- **Missing channels** — one or more tone generators stop working
- **Noise generator failure** — noise becomes silent or distorted
- **Envelope failure** — envelope shape doesn't work, leaving constant amplitude
- **I/O port failure** — Kempston mouse or serial port (which use the AY's I/O ports) stops working
- **Total failure** — no sound at all

A modern MCU replacement eliminates these issues.

### Audio Quality Enhancement

Original AY-3-8912 chips use a **logarithmic 4-bit DAC** per channel — giving 16 volume levels in a non-linear progression. This produces the characteristic "beepy" sound of the Spectrum. An MCU replacement can use:

- **Higher-resolution DACs** — 8-bit or 16-bit linear DACs for smoother volume
- **Linear interpolation** — smoothing the tone square waves to reduce high-frequency aliasing
- **Stereo output** — separating channels A/B/C into stereo, which the original mono output didn't do
- **Digital filtering** — applying low-pass, high-pass, or other filters to shape the sound

### Stereo Output

The original Spectrum combines the three PSG channels into a single mono output. Modern recreations often provide **stereo** output, separating the channels:

- **ABC stereo** — A on left, B in center, C on right (the most common convention)
- **ACB stereo** — A on left, C in center, B on right
- **MONO** — all channels on both left and right (original behavior)

Stereo output is a significant enhancement for music software — many AY music files (`.ay`, `.ym` files) sound substantially better in stereo.

### Multiple AYs (TurboSound)

Some Spectrum software uses **two PSGs** ("TurboSound") for 6-channel music. An MCU can emulate multiple PSGs trivially — no additional hardware needed.

---

## Implementation on MCU

### Register Emulation

The MCU maintains the 16 PSG registers in memory:

```c
typedef struct {
    uint8_t registers[16];
    int selected_register;
    // Internal state
    int tone_counter[3];      // A, B, C
    int tone_output[3];       // Current square wave output
    int noise_counter;
    int noise_lfsr;           // 17-bit LFSR for noise generation
    int envelope_counter;
    int envelope_output;
    int envelope_phase;       // Attack, decay, etc.
} ay_state_t;

// Handle a write to the address port
void ay_write_address(ay_state_t *state, uint8_t addr) {
    state->selected_register = addr & 0x0F;
}

// Handle a write to the data port
void ay_write_data(ay_state_t *state, uint8_t data) {
    state->registers[state->selected_register] = data;
}

// Handle a read from the data port
uint8_t ay_read_data(ay_state_t *state) {
    return state->registers[state->selected_register];
}
```

### Tone Generation

Each of the three tone generators produces a square wave:

```c
// Update tone generator for one channel
void ay_update_tone(ay_state_t *state, int channel, int cycles) {
    int period = (state->registers[channel*2 + 1] << 8) | 
                 state->registers[channel*2];
    period &= 0x0FFF;  // 12-bit period
    if (period == 0) period = 1;
    
    for (int i = 0; i < cycles; i++) {
        state->tone_counter[channel]--;
        if (state->tone_counter[channel] <= 0) {
            state->tone_counter[channel] = period;
            state->tone_output[channel] ^= 1;  // Toggle square wave
        }
    }
}
```

The tone generator's clock is the PSG clock (1.7734 MHz) divided by 16, so each tone cycle takes 16 PSG clock cycles per step.

### Noise Generator

The noise generator uses a 17-bit LFSR (Linear Feedback Shift Register) to produce pseudo-random noise:

```c
void ay_update_noise(ay_state_t *state, int cycles) {
    int period = state->registers[6] & 0x1F;  // 5-bit period
    if (period == 0) period = 1;
    
    for (int i = 0; i < cycles; i++) {
        state->noise_counter--;
        if (state->noise_counter <= 0) {
            state->noise_counter = period;
            // 17-bit LFSR with feedback from bits 0 and 3
            int feedback = (state->noise_lfsr ^ (state->noise_lfsr >> 3)) & 1;
            state->noise_lfsr = (state->noise_lfsr >> 1) | (feedback << 16);
        }
    }
}

int ay_get_noise(ay_state_t *state) {
    return state->noise_lfsr & 1;
}
```

### Envelope Generator

The envelope generator produces a time-varying amplitude according to the envelope shape:

- **Attack** — amplitude rises from 0 to 15
- **Decay** — amplitude falls from 15 to 0
- **Sustain** — amplitude holds at a level
- **Release** — amplitude falls from sustain to 0

The 4-bit envelope shape register selects one of 16 combinations of these phases:

```c
// Envelope shape patterns (selected by register R13 bits 0-3)
const int envelope_shapes[16][32] = {
    // Each shape is a 32-step pattern of amplitudes 0-15
    // ... (detailed patterns for each shape)
};

void ay_update_envelope(ay_state_t *state, int cycles) {
    int period = (state->registers[12] << 8) | state->registers[11];
    if (period == 0) period = 1;
    
    for (int i = 0; i < cycles; i++) {
        state->envelope_counter--;
        if (state->envelope_counter <= 0) {
            state->envelope_counter = period;
            state->envelope_phase++;
            if (state->envelope_phase >= 32) state->envelope_phase = 0;
            int shape = state->registers[13] & 0x0F;
            state->envelope_output = envelope_shapes[shape][state->envelope_phase];
        }
    }
}
```

### Audio Output

The three channels' amplitudes are computed each audio sample, mixed, and output:

```c
// Generate one audio sample
int16_t ay_get_sample(ay_state_t *state) {
    int sample = 0;
    for (int ch = 0; ch < 3; ch++) {
        // Determine channel amplitude (envelope or fixed)
        int amplitude;
        if (state->registers[8 + ch] & 0x10) {
            // Envelope mode
            amplitude = state->envelope_output;
        } else {
            // Fixed amplitude
            amplitude = state->registers[8 + ch] & 0x0F;
        }
        
        // Mix tone and noise according to R7 enable bits
        int tone_enabled = (state->registers[7] >> ch) & 1;
        int noise_enabled = (state->registers[7] >> (ch + 3)) & 1;
        int source = (tone_enabled ? state->tone_output[ch] : 1) &
                     (noise_enabled ? ay_get_noise(state) : 1);
        
        sample += source * amplitude;
    }
    return sample * 256;  // Scale to 16-bit range
}
```

The output sample rate is typically **44.1 kHz** (CD quality) or **48 kHz**, much higher than the original PSG's effective resolution.

### DAC Options

Several DAC options exist for outputting the audio:

- **MCU's built-in DAC** — if available (e.g., some STM32s have 12-bit DACs)
- **PWM via a GPIO pin** — a 1-bit PWM signal at high frequency, filtered via an RC low-pass filter, produces analog audio
- **External I2S DAC** — e.g., the PCM5102, providing high-quality 24-bit audio
- **Multiple resistor DAC** — a simple R-2R ladder connected to multiple GPIO pins

For high-quality audio, an external I2S DAC is preferred.

---
## Stereo Output

### Channel Separation

To produce stereo output, the three PSG channels are panned across the left/right speakers:

```c
// Generate stereo sample
void ay_get_stereo_sample(ay_state_t *state, int16_t *left, int16_t *right) {
    int sample_a = compute_channel(state, 0);
    int sample_b = compute_channel(state, 1);
    int sample_c = compute_channel(state, 2);
    
    // ABC stereo: A left, B centre, C right
    *left = sample_a + (sample_b / 2);
    *right = sample_c + (sample_b / 2);
}
```

Other panning conventions (ACB, MONO) are implemented similarly.

### AY Music Files

Many AY music files (`.ay`, `.ym` formats) include stereo metadata indicating which panning convention the composer intended. A high-quality MCU-based PSG can read this metadata and apply the correct panning.

## Multiple AYs (TurboSound)

Some Spectrum software, particularly demoscene productions, use **two PSGs** for 6-channel music:

- The first PSG responds to ports `#FFFD` / `#BFFD`
- The second PSG responds to ports `#3FFD` / `#5FFD` (or `#7FFD` on some clones)

An MCU can emulate multiple PSGs trivially — just allocate additional `ay_state_t` structures:

```c
ay_state_t ay1, ay2;  // Two PSGs for TurboSound

// Decode which PSG based on the I/O port
void ay_write(int port, uint8_t data) {
    if (port == 0xFFFD || port == 0xBFFD) {
        ay_write_port(&ay1, port, data);
    } else if (port == 0x3FFD || port == 0x5FFD) {
        ay_write_port(&ay2, port, data);
    }
}
```

The audio mixer combines all 6 channels, with stereo panning applied per PSG.

---

## Existing Projects

Several open-source PSG-on-MCU projects exist:

- **AY-3-8912 Emulator on STM32** — direct drop-in replacement
- **emu2149** — Vincent Sanders' C library, widely ported
- **ym2149_emul** — Yamaha YM2149 emulator
- **Pico AY** — RP2040-based AY replacement with stereo output
- **Schrödinger's AY** — FPGA/MCU hybrid with extensive features

These projects serve as references for new implementations. The emu2149 library in particular is well-documented and easy to port to MCUs.

### AY File Players

Beyond hardware replacements, the same PSG emulation code is used in **standalone AY music players**:

- **AY-emul** (Mikhail Shcheglov) — Windows-based AY music player
- **zxtune** — Multi-platform chiptune player, includes AY/YM support
- **ChipSeeR** — Open-source AY player

These demonstrate the audio quality achievable with high-resolution DACs and careful emulation.

---

## Integration with Real Hardware

### Drop-in Chip Replacement

The MCU is mounted on a small PCB with the same pinout as the AY-3-8912 (28-pin DIP) or YM2149 (40-pin DIP). The PCB plugs into the original PSG socket.

Requirements:

- **Pinout adapter** — mapping MCU GPIO to the AY's pinout
- **Level shifters** — 5V host system, 3.3V MCU
- **Audio output** — at minimum, a 3.5mm jack with mono or stereo audio; for authentic installations, routing back to the host's audio circuitry
- **Optional I/O port handling** — if the host uses the AY's I/O port (e.g., for Kempston mouse), the MCU must emulate this too

### External Audio Module

Alternatively, the MCU can be an external module that taps into the host's I/O port signals and provides audio output independently. This allows the original PSG to remain (for visual authenticity) while the MCU provides higher-quality audio.

### Software Transparency

A well-implemented PSG replacement is transparent to the host software. All Spectrum 128K / +2 / +3 / Pentagon / Scorpion / etc. software should work unchanged. The only difference is potentially improved audio quality (with stereo output, higher-resolution DACs, etc.).

---

## Comparison with FPGA PSG

The ZX-Uno, MiSTer, and other FPGA Spectrum recreations include PSG emulation in HDL. How does the MCU approach compare?

### Advantages of MCU

- **Easier development** — C/C++ vs Verilog
- **Lower cost** — RP2040 (~£1) vs FPGA (~£3–£10)
- **Audio quality** — easier to add high-resolution DACs, filters, and effects
- **Multiple AYs trivial** — just allocate more state structures
- **Stereo output flexibility** — easy panning options

### Advantages of FPGA

- **Native parallelism** — the tone/noise/envelope generators all run in true parallel
- **Lower CPU overhead** — no instruction interpretation
- **Established HDL implementations** — proven AY HDL cores exist

For most hobbyist PSG replacements, the MCU approach is preferable due to flexibility and ease of development.

---

## FAQ

**Q: What's the difference between AY-3-8912 and YM2149?**

A: The YM2149 is the Yamaha clone, pin-compatible but with slightly better DACs (cleaner audio). Software written for one runs identically on the other. The YM2149 also supports an "envelope divide" mode that the AY doesn't, but this is rarely used.

**Q: Can an MCU match the AY's distinctive "beepy" sound?**

A: Yes — by using the same logarithmic 4-bit amplitude scale (rather than linear), the MCU can reproduce the exact AY sound. Many MCU implementations also offer a "linear amplitude" mode that sounds subtly different but is preferred by some users.

**Q: What sample rate should I use?**

A: 44.1 kHz is standard and sufficient for the AY's audio bandwidth. Some audiophile implementations use 48 kHz or 96 kHz, but the improvement is minimal for AY audio (which has limited high-frequency content).

**Q: How do I handle the AY's I/O port?**

A: The AY-3-8912 has one 8-bit I/O port (port A), used on the Spectrum for the +2 serial port and for Kempston mouse. The MCU must emulate these reads/writes — usually by maintaining the port value in a register and returning it on read.

**Q: Does the MCU need to know the exact PSG clock?**

A: Yes — the tone frequencies depend on the clock. The Spectrum 128K uses 1.7734 MHz, the Pentagon uses 1.75 MHz, and other clones vary. The MCU should be configurable for the host system's PSG clock, or autodetect it.

**Q: Can I add effects like reverb or chorus?**

A: Yes — the MCU's CPU can apply digital signal processing to the audio output. Reverb, chorus, and equalisation are common. However, some enthusiasts prefer "pure" unmodified AY sound for authenticity.

**Q: Is it possible to play AY files without a real Spectrum?**

A: Yes — AY file players run on modern PCs (and on MCUs) by emulating the PSG and reading the AY/YM file format. This is how the AY music archive (thousands of compositions) is preserved and enjoyed.

---

## Summary

Replacing the AY-3-8912 PSG with a modern MCU is a practical upgrade that:

1. **Eliminates component failure** — no more missing channels or failed envelope generators
2. **Improves audio quality** — with high-resolution DACs and digital filtering
3. **Adds stereo output** — separating the three channels for richer sound
4. **Supports TurboSound** — multiple AYs trivially emulated
5. **Maintains software compatibility** — the host software sees no difference

The RP2040, ESP32, and STM32 are all viable hosts. Implementation involves register emulation, tone/noise/envelope generation, audio mixing, and DAC output. Existing open-source projects (emu2149, ym2149_emul, Pico AY) provide reference implementations.

---

## References

- **General Instrument AY-3-8910/8912 datasheet** — register interface, electrical characteristics
- **Yamaha YM2149 datasheet** — Yamaha clone with technical differences
- **emu2149** by Vincent Sanders — open-source AY emulation library
- **AY-emul** by Mikhail Shcheglov — AY music player with detailed emulation
- **`.ay` file format specification** — AY music archive format
- **`.ym` file format specification** — YM music format
- **Spectrum 128K service manual** — PSG connection and audio circuitry
- [AY-3-8912 register documentation](http://www.worldofspectrum.org/) — community-maintained reference

## Cross-references

- [Z80 on MCU](mcu_z80.md) — companion article on CPU replacement
- [ULA on MCU](mcu_ula.md) — companion article on ULA replacement (which also handles beeper)
- [FDC on MCU](mcu_fdc_vg93.md) — floppy disk controller replacement
- [Keyboard on MCU](mcu_keyboard.md) — keyboard controller
- [SD interface on MCU](mcu_sd_interface.md) — SD-card storage for AY files
- [MiSTer](../fpga/mist_mister_core.md) / [ZX-Uno](../fpga/zx_uno_core.md) — FPGA alternatives with built-in PSG emulation
- [MCU design patterns](mcu_design_patterns.md) — general bus interfacing techniques
