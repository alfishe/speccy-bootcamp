[← Home](../../README.md) · [Sound](../README.md) · [Synthesis](README.md)

# Synthesis Techniques

> How to make sound chips produce the sounds you want — from basic tone generation to advanced phase manipulation and sample playback.

---

## Articles

| Article | Description |
|---------|-------------|
| [ay_ym_synthesis.md](ay_ym_synthesis.md) | **AY/YM PSG Hardware Reference** — architecture, registers, clock domains, counter model, envelope/noise generator internals |
| [ay_ym_techniques.md](ay_ym_techniques.md) | **AY/YM Synthesis Techniques** — sync-square, PWM, SID-sound, buzzer bass, envelope-driven bass oscillation, note-colored noise, drum synthesis, sample playback |
| [ay_vs_ym.md](ay_vs_ym.md) *(planned)* | **AY vs YM Technical Comparison** — envelope resolution, DC offset, SEL pin, volume tables, detection, emulator behavior |
| [ay_ym_perception.md](ay_ym_perception.md) | **The AY Sound: Perception, Emotion, and the Hardware Soul** — ABC vs ACB holy war, AY vs YM differences, analog signal chain, psychoacoustics, nostalgia, recapturing the sound |
| [multitrack_multichip.md](multitrack_multichip.md) | Multi-track and multi-chip synthesis outline: TurboSound, interleaved channels, cross-chip effects, synchronization |
| [beeper_synthesis.md](beeper_synthesis.md) | **1-Bit Beeper Synthesis** — from ROM beep to multi-channel polyphony: PWM fundamentals, Tim Follin engines, Shiru's Tritone/QChan/Squat/1tracker, utz's Octode/Fluidcore, Earshaver, drum synthesis, sample playback, competition scene |
| [shiru_ear_shaver_analysis.md](shiru_ear_shaver_analysis.md) | **Case Study: Shiru's *Ear Shaver* Engine** — forensic teardown of all 7 synthesis modes, DDS phase accumulators, branchless PWM via IX half-registers, time-division multiplexing, self-modifying code, stream compression, memory map, cross-platform portability |

---

## Cross-References

- [Sound Section Index](../README.md) — full sound catalog including hardware and formats
- [128K Memory and I/O](../../05_development/03_memory_and_io/memory_and_io_128k.md) — AY port decoding
