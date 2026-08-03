[← Home](../README.md) · [Overview](README.md)

# 00 — Overview

> The navigational entry point to the ZX Spectrum knowledge base: history, hardware model catalog, and platform-specific terminology.

Licensed under [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/).

---

## Articles

| Article | Lines | Description |
|---------|-------|-------------|
| [history.md](history.md) | 364 | **Narrative synthesis of the ZX Spectrum's 40+ year story**: five distinct eras (Pre-Spectrum 1972–1981, Sinclair 1982–1986, Amstrad 1986–1992, Post-Soviet clone 1989–2000s, Modern revival 2010s–present), verified dates from canonical Sinclair Wiki source, embedded Mermaid `timeline` diagram 1976–2022, cultural and economic context for each transition, 5 pitfalls (sales figures contested, Amstrad acquisition date accuracy, 128K vs +2 confusion, Pentagon as reimplementation not copy, Spectrum/Speccy naming) |
| [hardware_models.md](hardware_models.md) | 203 | **Navigational hub for hardware models across three tracks**: Original/Soviet Clones/New Gen taxonomy, three per-track model tables (7 Original, 10 Soviet clones, 8 New Gen), three cross-track comparison matrices (frame timing, memory architecture, sound capability), "How to Choose a Model" decision matrix with 8 use cases, every model row links to per-model deep-dive article |
| [glossary.md](glossary.md) | 318 | **Platform-specific terminology reference**: 100+ terms organized by category (Hardware, Display, Memory, Storage, Software/System, Cultural/Demoscene, Track-Specific), each entry has 2–4 sentence definition with "See X" cross-reference, abbreviations listed both short form (ULA) and full form (Uncommitted Logic Array), 5 pitfalls (Spectrum vs Speccy, Pentagon disambiguation, three meanings of "ROM", Next as separate hardware family, AY vs PSG terminology) |

---

## Reading Order

**First-time readers**: start with [history.md](history.md) for the chronological context, then [hardware_models.md](hardware_models.md) for the cross-track hardware landscape, then use [glossary.md](glossary.md) as a lookup reference when other articles introduce unfamiliar terms.

**Software developers targeting a specific model**: jump directly to [hardware_models.md](hardware_models.md) §6 "How to Choose a Model" for the decision matrix, then follow the cross-reference to the per-model deep-dive article.

**Demoscene and reverse-engineering readers**: read [history.md](history.md) §4 (Post-Soviet clone era) and §5 (Modern revival) for cultural context, then use [glossary.md](glossary.md) §6 (Cultural and demoscene terms) and §7 (Track-specific terms) as lookups.

---

## Cross-References

These overview articles are intentionally **navigational and synthetic** — they orient the reader and link to deeper content. For the deep technical material:

- **Hardware deep dives**: [02_hardware/original/](../02_hardware/original/README.md), [02_hardware/clones/](../02_hardware/clones/README.md), [02_hardware/newgen/](../02_hardware/newgen/README.md)
- **Demoscene history and culture**: [07_demoscene/demoscene_history.md](../07_demoscene/demoscene_history.md)
- **Frame timing and video subsystem**: [05_development/05_display_and_timing/](../05_development/05_display_and_timing/README.md)
- **Canonical reference data**: [10_references/](../10_references/README.md) — port maps, memory maps, opcode tables, palette, ROM routines

---

## Descope Note

The original F14 plan called for **4 articles**: `history.md`, `hardware_models.md`, `timeline.md`, and `glossary.md`. After Phase 1–3 research and Phase 4 delimitation review, the user approved a **3-article consolidation** via AskUserQuestion that merges the visual timeline into `history.md` as an embedded Mermaid `timeline` diagram. The standalone `timeline.md` was descoped because a separate chronological-visualization article duplicated content already covered by `history.md`'s narrative and by the per-model History subsections of the deep-dive articles in `02_hardware/`.
