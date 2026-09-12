[← Home](../../README.md) · [Sound](../README.md) · [Players](README.md)

# Player Routines

> How music data becomes sound on real hardware — ISR integration, register write sequences, timing budgets, and format comparison. The Z80 code that bridges tracked music to the AY chip.

---

## Quick Reference

| If you want... | Read this |
|----------------|-----------|
| Integrate a player into your code | [ay_player_routines.md](ay_player_routines.md) |
| Compare PT3 vs Arkos players | [player_comparison.md](player_comparison.md) |
| Choose the right player | [player_comparison.md](player_comparison.md#decision-matrix) |

---

## Articles

| Article | Description |
|---------|-------------|
| [ay_player_routines.md](ay_player_routines.md) | **AY Player Routines** — Z80 code that converts music modules into per-frame AY register writes. ISR integration, PT3/Arkos player structures, timing budgets, Init/Play/Mute entry points, 14 common pitfalls |
| [player_comparison.md](player_comparison.md) | **Player Comparison Matrix** — PT3 vs Arkos AKG/AKM/AKY head-to-head: size, speed, sound quality, portability. 13-case recommendation matrix |

---

## Player Quick Reference

| Player | Format | Size | T-states/frame | Best for |
|--------|--------|------|----------------|----------|
| **PT3** (Bulba) | `.PT3` | 400–600 bytes | 3,000–4,000 | Soviet scene, emulators |
| **AKG** (Arkos) | `.AKG` | 1.0–1.5 KB | 1,500–2,500 | Games (balanced) |
| **AKM** (Arkos) | `.AKM` | 400–600 bytes | 800–1,500 | Intros (size) |
| **AKY** (Arkos) | `.AKY` | 600–900 bytes | 600–1,200 | Demos (speed, digidrum) |

---

## Integration Patterns

### Basic ISR Integration

```z80
; IM1 hook at #38 (simplified)
    push af
    push bc
    push de
    push hl
    call MusicPlay      ; ~3000 T-states
    pop  hl
    pop  de
    pop  bc
    pop  af
    ei
    ret
```

### Key Considerations

1. **Frame timing**: 48K = 69,888 T-states/frame @ 50.08 Hz; Pentagon = 71,680 @ 48.83 Hz
2. **Contention**: Place player code in uncontended memory (bank 0 on 128K)
3. **Register preservation**: Save ALL registers including AF' and IX/IY if used
4. **Mute on pause**: Call player's mute routine, not just silence registers

---

## Cross-References

### Related Sound Topics

- [Trackers & Formats](../trackers_and_formats/README.md) — The formats players interpret
- [Synthesis Techniques](../synthesis/README.md) — Underlying sound generation
- [Sound Hardware](../hardware/README.md) — AY register details

### Development Context

- [128K Memory and I/O](../../05_development/03_memory_and_io/memory_and_io_128k.md) — AY port decoding
- [Interrupt Handling](../../05_development/) — ISR setup and timing
