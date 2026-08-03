[← Home](../../README.md) · [BASIC](README.md)

# Development — Sinclair BASIC

This directory covers **Sinclair BASIC programming** on the ZX Spectrum — the language built into the ROM, used as the entry point by every Spectrum programmer. The two articles below are deliberately comprehensive: one for the 48K dialect (which is also the foundation everyone must learn first), and one for the 128K-specific extensions that build on top of it.

---

## Articles

| # | Article | Description |
|---|---|---|
| 1 | [basic_48k.md](basic_48k.md) | **Sinclair BASIC 48K — comprehensive reference**: what BASIC is (vs Microsoft BASIC), three ROM versions, memory layout (PROG, VARS, FRAMES, RAMTOP), program storage format, token system with abbreviations, variable types (numeric/string/array with quirks), 5-byte floating-point format, calculator stack (44 operations), parser pipeline, **graphics commands** (`PLOT`, `DRAW`, `CIRCLE`, `POINT`, `ATTR`), **sound** (`BEEP` with frequency formula and pitch table), **machine-code bridge** (`PEEK`, `POKE`, `USR` with calling conventions and parameter passing), notable quirks (no ELSE, mandatory LET, single-line editor, GO TO vs GOTO), when to use BASIC vs machine code. Worked examples: guess-the-number, Mandelbrot set, Ode to Joy. |
| 2 | [basic_128k.md](basic_128k.md) | **Sinclair BASIC 128K extensions**: the new full-screen editor with 4-line edit buffer, the boot menu (128 BASIC / 48 BASIC / Tape Loader / Calculator / Tape Tester), the **`PLAY` command** mini-language in depth (notes c-b/C-B, sharps/flats, octave O0–O8, volume V0–V15, envelope effects W0–W7/U/X, tempo T60–T240, channel mode M0–M63, repeats, comments, three-voice harmony), direct AY-3-8912 register access from BASIC via `OUT`/`IN`, +2A/+3 disk commands (`CAT`, `FORMAT`, `ERASE`, `MOVE`, `OPEN #`), token table differences, memory paging, RAM disk, common pitfalls (shared envelope/noise generators, interrupt dependency). Worked example: background music with foreground animation. |

---

## Related Articles (Elsewhere)

- [basic_dialects.md](../../04_operating_systems/basic_dialects.md) — comparison of all BASIC dialects: 48K, 128K, +2/+2A/+3, QL SuperBASIC, SE BASIC, NextBASIC
- [basic_token_table.md](../../10_references/basic_token_table.md) — byte-level token values for every keyword across all ROM versions
- [rom_48k.md](../../04_operating_systems/rom_48k.md), [rom_128k.md](../../04_operating_systems/rom_128k.md), [rom_plus2.md](../../04_operating_systems/rom_plus2.md) — ROM internals for the three families
- [ay_3_8912.md](../../06_sound/hardware/ay_3_8912.md) — AY-3-8912 PSG complete reference (assembly-level)
- [beeper_synthesis.md](../../06_sound/synthesis/beeper_synthesis.md) — the 1-bit beeper hardware

---

See [PLAN.md](../../PLAN.md) for the full article catalog.
