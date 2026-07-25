[← Home](../../README.md) · [Sound](../README.md) · [Players](README.md)

# Player Routines

> How music data becomes sound on real hardware — ISR integration, register write sequences, timing budgets, and player format comparison.

---

## Articles

| Article | Description |
|---------|-------------|
| [ay_player_routines.md](ay_player_routines.md) | **AY Player Routines** — Z80 code that converts a music module into per-frame AY register writes. AY two-port idiom (`#FFFD` address latch + `#BFFD` data write; the `LD C,#FD` + B-toggle optimisation). Per-model frame budgets (48K 69,888 T-states at 50.08 Hz vs Pentagon 71,680 at 48.83 Hz). ISR integration patterns (IM1 patching vs IM2 vector table with 257-byte table). PT3 player structure (~400–600 bytes, 3,000–4,000 T-states/frame). Arkos AKG/AKM/AKY player structures (AKG balanced for games, AKM size-optimised for intros, AKY fast/digidrum-capable for demos). RAM-vs-ROM player variants (self-modifying code vs buffer). Contended vs uncontended memory placement (bank 0 uncontended for player code). Music + game / demo / music-disk integration patterns. Init/Play/Mute entry points. 14 pitfalls (most common: forgetting to preserve all registers in the ISR) |
| [player_comparison.md](player_comparison.md) | PT3 vs Arkos (AKG/AKM/AKY): speed, size, features |
| [audio_decision_guide.md](audio_decision_guide.md) | Which hardware + format + player to target |

---

## Cross-References

- [Trackers & Formats](../trackers_and_formats/README.md) — the formats players interpret
- [Synthesis Techniques](../synthesis/README.md) — the underlying sound generation
- [Sound Section Index](../README.md) — full sound catalog
