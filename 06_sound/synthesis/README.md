[← Home](../../README.md) · [Sound](../README.md) · [Synthesis](README.md)

# Synthesis Techniques

> How to make sound chips produce the sounds you want — from basic tone generation to advanced phase manipulation, PWM, and sample playback. Theory and practice for the AY-3-8912, YM2149, and 1-bit beeper.

---

## Quick Reference

| If you want... | Read this |
|----------------|-----------|
| Understand AY/YM internals | [ay_ym_synthesis.md](ay_ym_synthesis.md) |
| Learn specific techniques | [ay_ym_techniques.md](ay_ym_techniques.md) |
| AY vs YM chip differences | [ay_vs_ym.md](ay_vs_ym.md) |
| 1-bit beeper music | [beeper_synthesis.md](beeper_synthesis.md) |
| Multi-chip (TurboSound) | [multitrack_multichip.md](multitrack_multichip.md) |

---

## Articles

### AY/YM PSG Synthesis

| Article | Description |
|---------|-------------|
| [ay_ym_synthesis.md](ay_ym_synthesis.md) | **AY/YM PSG Hardware Reference** — internal architecture, register set, clock domains, counter model, envelope/noise generator internals, phase reset |
| [ay_ym_techniques.md](ay_ym_techniques.md) | **AY/YM Synthesis Techniques** — sync-square, PWM, SID-sound, buzzer bass, envelope-driven bass oscillation, note-colored noise, drum synthesis, sample playback |
| [ay_vs_ym.md](ay_vs_ym.md) | **AY vs YM Technical Comparison** — DAC ladder differences, YM's 5-bit envelope, DC offset, SEL pin, per-unit silicon variation, emulator modeling |
| [ay_ym_perception.md](ay_ym_perception.md) | **The AY Sound: Perception, Emotion, and the Hardware Soul** — ABC vs ACB, AY vs YM subjective differences, analog signal chain, psychoacoustics, nostalgia |
| [multitrack_multichip.md](multitrack_multichip.md) | **Multi-Track and Multi-Chip** — TurboSound programming, interleaved channels, cross-chip effects, synchronization strategies |

### Beeper Synthesis

| Article | Description |
|---------|-------------|
| [beeper_synthesis.md](beeper_synthesis.md) | **1-Bit Beeper Synthesis** — PWM fundamentals, Tim Follin engines, Shiru's Tritone/QChan/Squat, utz's Octode/Fluidcore, drum synthesis, sample playback |
| [shiru_ear_shaver_analysis.md](shiru_ear_shaver_analysis.md) | **Case Study: Shiru's *Ear Shaver* Engine** — forensic teardown of all 7 synthesis modes, DDS phase accumulators, PWM via IX half-registers, self-modifying code |

---

## Technique Quick Reference

### AY/YM Techniques

| Technique | Purpose | Complexity | Article Section |
|-----------|---------|------------|-----------------|
| **Sync-square** | Sawtooth-like timbre | Low | [ay_ym_techniques.md](ay_ym_techniques.md#sync-square) |
| **PWM (Pulse Width Modulation)** | Variable duty cycle, rich harmonics | Medium | [ay_ym_techniques.md](ay_ym_techniques.md#pwm) |
| **SID-sound** | C64-style "digidrum" | Medium | [ay_ym_techniques.md](ay_ym_techniques.md#sid-sound) |
| **Buzzer bass** | Envelope-driven sub-bass | Low | [ay_ym_techniques.md](ay_ym_techniques.md#buzzer-bass) |
| **Note-colored noise** | Pitched percussion | Low | [ay_ym_techniques.md](ay_ym_techniques.md#note-colored-noise) |
| **Sample playback** | Digitized audio via volume register | High | [ay_ym_techniques.md](ay_ym_techniques.md#sample-playback) |

### Beeper Techniques

| Technique | Channels | CPU Cost | Article Section |
|-----------|----------|----------|-----------------|
| **Simple square** | 1 | Minimal | [beeper_synthesis.md](beeper_synthesis.md#simple-square) |
| **PWM (Phaser)** | 1 | Moderate | [beeper_synthesis.md](beeper_synthesis.md#pwm) |
| **Tritone/QChan** | 3–4 | High | [beeper_synthesis.md](beeper_synthesis.md#tritone) |
| **Octode/Fluidcore** | 8+ | Very high | [beeper_synthesis.md](beeper_synthesis.md#octode) |

---

## Cross-References

### Related Sound Topics

- [Sound Hardware](../hardware/README.md) — Hardware specs for AY, TurboSound, etc.
- [Trackers & Formats](../trackers_and_formats/README.md) — Music editors that use these techniques
- [Player Routines](../players/README.md) — Integrating synthesis into games/demos

### Development Context

- [128K Memory and I/O](../../05_development/03_memory_and_io/memory_and_io_128k.md) — AY port decoding (#FFFD/#BFFD)
- [Interrupt Timing](../../05_development/05_display_and_timing/) — Frame timing for music playback
- [I/O Port Map](../../10_references/io_port_map.md) — Complete port addresses
