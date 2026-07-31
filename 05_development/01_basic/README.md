[← Home](../../README.md) · [BASIC](README.md)

# Development — Sinclair BASIC

This directory covers **Sinclair BASIC programming** on the ZX Spectrum — the language built into the ROM, used as the entry point by every Spectrum programmer. Articles here cover syntax, graphics, sound, and the bridge to machine code via `PEEK`/`POKE`/`USR`.

---

## Articles

| # | Article | Description |
|---|---|---|
| 1 | [basic_intro.md](basic_intro.md) | **Sinclair BASIC foundation**: tokens, syntax, variable types (numeric/string/array), 5-byte floating-point format, the calculator stack, ROM parser, line-entry quirks, GO TO vs GOTO, no ELSE, mandatory LET, single-line editor |
| 2 | [basic_graphics.md](basic_graphics.md) | **Graphics commands**: coordinate system (origin bottom-left), `PLOT`, `DRAW` (line + arc), `CIRCLE`, `POINT`, `ATTR`, INK/PAPER/INVERSE/OVER modifiers, performance timings, worked examples |
| 3 | [basic_sound.md](basic_sound.md) | **`BEEP` command**: pitch in semitones from middle C, duration in seconds, frequency formula (261.63 × 2^(pitch/12)), note lookup table, DATA-driven melodies, sound effects (laser/explosion/warble), 128K `PLAY` overview, performance notes |
| 4 | [basic_peek_poke.md](basic_peek_poke.md) | **BASIC-to-machine-code bridge**: `PEEK` (read byte), `POKE` (write byte), `USR` (call routine, return value in BC), calling conventions, parameter passing, loading machine code (`LOAD "" CODE`), `RANDOMIZE USR addr` idiom, common pitfalls |

### Planned

| # | Article | Topic |
|---|---|---|
| 5 | `basic_file_io.md` | `SAVE`, `LOAD`, `VERIFY`, `MERGE`, tape operations |
| 6 | `basic_128k.md` | 128K BASIC extensions: `PLAY`, `SPECTRUM`, `SOUND`, RAM disk, BANK commands, full-screen editor |
| 7 | `basic_advanced.md` | String manipulation, arrays, data structures, optimization |
| 8 | `basic_dialects_comparison.md` | Comparing BASIC dialects: 48K vs 128K vs TIMEX vs Russian vs NextBASIC |

---

See [PLAN.md](../../PLAN.md) for the full article catalog.
