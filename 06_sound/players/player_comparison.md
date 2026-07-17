[← Home](../../README.md) · [Sound](../README.md) · [Players](README.md)

# Player Comparison — PT3 vs Arkos (AKG/AKM/AKY)

> **Status**: Stub — article not yet written

A detailed comparison of the major AY player routines: PT3 player, Arkos AKG, Arkos AKM, and Arkos AKY. Covers code size, CPU usage, feature set, and practical recommendations.

---

## Planned Content

- PT3 player: size, speed, features (samples, ornaments, envelopes)
- Arkos AKG: general-purpose player, size/speed tradeoffs
- Arkos AKM: minimal player (for 1K/4K intros), extreme size optimization
- Arkos AKY: sound effect player, one-shot sample playback
- Benchmark table: code size, T-states per frame, RAM usage
- Feature comparison: which player supports what (pitch bends, arpeggios, noise, etc.)
- Quality comparison: does the player alter the sound? (exact vs approximated)
- Recommendation matrix: which player for games vs demos vs intros

---

## Cross-References

- [AY Player Routines](ay_player_routines.md) — general architecture (prerequisite)
- [Audio Decision Guide](audio_decision_guide.md) — choosing hardware + format + player
- [Vortex Tracker II](../trackers_and_formats/vortex_tracker.md) — PT3 ecosystem
- [Arkos Tracker](../trackers_and_formats/arkos_tracker.md) — AKG/AKM/AKY ecosystem
