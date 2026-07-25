[← Home](../../README.md) · [Sound](../README.md) · [Players](README.md)

# Player Routines

> How music data becomes sound on real hardware — ISR integration, register write sequences, timing budgets, and player format comparison.

---

## Articles

| Article | Description |
|---------|-------------|
| [ay_player_routines.md](ay_player_routines.md) | **AY Player Routines** — Z80 code that converts a music module into per-frame AY register writes. AY two-port idiom (`#FFFD` address latch + `#BFFD` data write; the `LD C,#FD` + B-toggle optimisation). Per-model frame budgets (48K 69,888 T-states at 50.08 Hz vs Pentagon 71,680 at 48.83 Hz). ISR integration patterns (IM1 patching vs IM2 vector table with 257-byte table). PT3 player structure (~400–600 bytes, 3,000–4,000 T-states/frame). Arkos AKG/AKM/AKY player structures (AKG balanced for games, AKM size-optimised for intros, AKY fast/digidrum-capable for demos). RAM-vs-ROM player variants (self-modifying code vs buffer). Contended vs uncontended memory placement (bank 0 uncontended for player code). Music + game / demo / music-disk integration patterns. Init/Play/Mute entry points. 14 pitfalls (most common: forgetting to preserve all registers in the ISR) |
| [player_comparison.md](player_comparison.md) | **Player Comparison** — head-to-head benchmarks of PT3 (Bulba/Soviet lineage, ~400–600 bytes, 3,000–4,000 T-states/frame) vs Arkos AKG (balanced, ~1.0–1.5 KB, 1,500–2,500 T-states), AKM (smallest, ~400–600 bytes, 800–1,500 T-states, ROM-only, single-PSG), AKY (fastest, ~600–900 bytes, 600–1,200 T-states, digidrum/sample support). Sound-quality differences (AKM envelope-retrigger click, skip-unchanged drift, volume-update timing). Per-platform PSG-clock behaviour (AKG/AKM portable, AKY tied to one clock, PT3 follows composer's clock). Targhan's official decision table. 13 use-case recommendation matrix (games/demos/intros/music-disk/cartridge/Next/archival). 10 pitfalls (most common: AKY cross-clock pitch error; AKM envelope click; forgetting ROM variant) |
| [audio_decision_guide.md](audio_decision_guide.md) | **Audio Decision Guide** — top-level decision tree covering hardware → chip → format → player. Step 1: target hardware table (9 machines from 48K to Next with built-in + external sound options). Step 2: chip trade-offs (beeper/AY/TurboSound/SAA1099/MoonSound/DMA/Covox) with sensible-default rule. Step 3: format catalogue (PT3, AKG/AKM/AKY, PSG, ASM, SAP, DSQ, YM, MOD, beeper formats). Step 4: player choice (Bulba / AKG / AKM / AKY). Mermaid flowchart of the full decision tree. Compatibility matrix (9 targets × 6 chips; 6 chips × 7 formats). 15 common scenarios with full hardware+chip+format+player recommendations. 5 trade-off axes (size/quality, CPU/visuals, compatibility/modernity, ease/sophistication, audience/ambition). 5 sensible defaults (128K game / 48K game / Pentagon demo / archival / no-idea). 10 pitfalls (most common: format mismatch; wrong PSG clock; TurboSound player mismatch) |

---

## Cross-References

- [Trackers & Formats](../trackers_and_formats/README.md) — the formats players interpret
- [Synthesis Techniques](../synthesis/README.md) — the underlying sound generation
- [Sound Section Index](../README.md) — full sound catalog
