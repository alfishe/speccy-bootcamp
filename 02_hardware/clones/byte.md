[← Home](../../README.md) · [Clone Hardware](README.md)

# Byte — The Belarusian Factory-Built Spectrum

The **Byte** (Russian: **Байт**, also transliterated **Bajt**) is a Soviet ZX Spectrum clone designed and manufactured by the **Brest Electromechanical Plant (BEMZ)** in Brest, Byelorussian SSR (now Belarus), beginning in **December 1989**. It is one of the few Soviet Spectrum clones produced by an **official state-owned factory** — part of the Brest Production Association of Computing Equipment (BPO SVT) — rather than a hobbyist collective or cooperative. The Byte was produced in substantial volumes (estimated **60,000+ units** by the mid-1990s) and played a major role in bringing affordable personal computing to Soviet schools, Pioneer clubs, and homes during the perestroika era and the early post-Soviet period.

From a programmer's perspective, the Byte is a **broadly 48K-compatible Soviet clone** built from discrete TTL logic. It runs the entire 48K Spectrum software library, uses standard 48K frame timing (69,888 T-states, 312 scanlines, 50.08 Hz), and has zero memory contention. Unlike most homebrew Soviet clones, the Byte shipped in a **monoblock plastic case** with an integrated full-stroke keyboard, external power supply, and SECAM RF output — designed to look and feel like a finished consumer product rather than a bare board.

> [!NOTE]
> This article covers the **hardware platform**. For the Byte's frame timing, see [video_frame_other_soviet.md](../../05_development/05_display_and_timing/video_frame_other_soviet.md). For the broader clone timing landscape, see [clone_timing.md](clone_timing.md).

---

## History and Context

### The Brest Factory Story

The Byte was developed at the **Brest Electromechanical Plant (BEMZ)** in Brest, a city in the Byelorussian SSR on the Soviet-Polish border. The factory was part of the **Brest Production Association of Computing Equipment (BPO SVT)**, a state-owned enterprise tasked with producing computing equipment for the Soviet domestic market. The Byte project was launched in the late 1980s, motivated by the Soviet government's push for "a million school computers by 1990" — a national goal driven by Mikhail Gorbachev's perestroika reforms.

Because original Zilog Z80 CPUs and Ferranti ULA chips were unobtainable inside the Soviet Union (and forbidden by COCOM export controls), the BEMZ engineers reverse-engineered the ZX Spectrum using **Soviet-made TTL logic** and Soviet clones of the Z80. The result is a fully discrete-logic Spectrum reimplementation — no ULA, no custom chips.

The first working prototypes were completed in **December 1989** and immediately put on sale at around **1,000 Soviet rubles** (roughly half a year's average salary at the time). Mass production began in 1990, with refinement continuing into 1991. The BEMZ plant remained the primary manufacturer until production wound down around 1994, with remaining stock still being sold through 1996.

### Production Volumes

Unlike most homebrew Soviet clones, the Byte has well-documented factory production statistics:

| Year | Avg. units / month | Notes |
|---|---|---|
| **1990** | 479 | Initial mass production; first retail sales at ~960 rubles |
| **1991** | 1,176 | Ramp-up; Soviet Union dissolves in December |
| **1992** | 1,705 (peak) | Peak production year |
| **1993** | ~1,000 | Decline begins as cheap Asian PCs flood market |
| **1994** | ~500 | Official BEMZ production winds down |
| **1995** | 234 | Clearance sales; final new-old stock |

Total estimated production: **over 60,000 units** — making the Byte one of the most-produced Soviet Spectrum clones by a single factory, second only to the aggregate of Pentagon-compatible machines across all manufacturers.

---

## Hardware Architecture

The Byte is built around a **discrete-logic reimplementation** of the ZX Spectrum 48K, using approximately **80 integrated circuits** on a dense, **8-layer military-grade PCB**. The multilayer board was a BEMZ signature — most other Soviet clones used simpler 2-layer boards, but Brest's defense-plant heritage gave them access to higher-quality PCB fabrication.

### Component Summary

| Subsystem | Byte implementation |
|---|---|
| **CPU** | **KR1858VM1** (Soviet Z80A clone, ~3.5 MHz) — East German U880 in some later units |
| **Lower RAM** | **KR565RU6** DRAM (Soviet 4116-equivalent, 16 Kbit × 1) — 8 chips for the contended bank |
| **Upper RAM** | KR565RU7 / KR565RU8 DRAM (Soviet 4164-equivalent) |
| **ROM** | **K573RF6A** EPROM (Soviet Intel 2764 equivalent, 8 KB × 2 = 16 KB) |
| **Glue logic** | Discrete **KR1533-series TTL** (Soviet 74ALS-equivalent) |
| **Video** | Discrete TTL video generator (no ULA) — composite RF, SECAM |
| **Keyboard** | 66-key full-stroke, integrated, RUS/LAT toggle |
| **Power** | External transformer unit: +5 V @ 2.5 A, +12 V @ 0.5–1 A |

> [!IMPORTANT]
> The Byte uses the older **KR565RU6 (4116-equivalent) DRAM** for the lower 16 KB contended bank — the same chip family as the original Sinclair 48K. This is **not** the modernized single-rail 4464 DRAM used in some later Soviet clones. The 4116's triple-rail requirement (+5 V / −5 V / +12 V) is why the Byte's power supply delivers all three voltages.

### Design Philosophy

The Byte's design choices reflect its **factory origin**:

1. **Military-grade PCB** — 8-layer board with plated through-holes, vastly more reliable than the 2-layer homebrew boards used in Pentagon kits. This is a direct consequence of BEMZ being a converted defense plant with high-end PCB fabrication equipment.

2. **Integrated monoblock case** — Unlike bare-board clones (Pentagon, Scorpion) that required the user to source a separate case, keyboard, and power supply, the Byte shipped as a finished product. The plastic case houses the mainboard, keyboard, and a small built-in speaker.

3. **Dual-language ROM** — The 16 KB ROM contains **two switchable character sets**: Latin (for original ZX Spectrum compatibility) and Cyrillic (for Russian-language software). A physical RUS/LAT key on the keyboard toggles between them, and a separate "СОВМЕСТ" (compatibility) button near the reset switch selects between the original Sinclair ROM and a localized Russian ROM with translated system messages.

4. **SECAM RF output** — Composite RF modulator producing a SECAM signal compatible with Soviet TVs. An RGB output via DIN connector is also available for monitors.

5. **Tape storage** — Built-in cassette interface at 1,500 baud, standard for ZX Spectrum-compatible systems.

---

## Variants

### Byte (Base Model, 1990)

The standard Byte is a 48K Spectrum-compatible machine. Memory can be expanded externally to 80 KB (some configurations) or to a full 128 KB via add-on modules such as the **BC-1**, **B-1**, or **C-1** daughterboards, which connect via the expansion port and implement the standard Sinclair 128K `#7FFD` paging register.

### Byte-01 (1991+)

The **Byte-01** is the improved variant, produced in smaller numbers. Key differences from the base Byte:

- **Optional 128 KB RAM** on the mainboard (no expansion daughterboard required)
- **CP/M compatibility** via an additional 8 KB ROM (TRS-DOS 5.01 and CP/M boot support)
- **512×192 monochrome graphics mode** — a non-standard high-resolution mode for CP/M applications and word processors
- **Tower-style 5.25" floppy drive support** — connects via the Byte-01's expansion interface
- **Refined circuit revisions** for greater reliability
- **Optional printer support** — the Elektronika MS6313 dot-matrix printer was bundled with some Byte-01 units

The Byte-01 is the variant most commonly referenced in Western retrospectives about "Spectrum clones with high-resolution graphics and CP/M," though it is much rarer than the base model.

### Moldovan Byte (Elektronika VI-201 / Parus / VI-202)

A **distinct Moldovan clone** was sold under the Byte name, produced at the **Dniester plant** in Bender, Moldavian SSR, beginning around 1991. This is **not** the same hardware as the Brest Byte:

| Variant | Producer | Distinct features |
|---|---|---|
| **Elektronika VI-201 (Parus)** | Dniester plant, Bender | More reliable power supply, KR1013RE1-020 ROM with Didaktik Skalica firmware |
| **Elektronika VI-202** | Dniester plant, Bender | East German **U880 CPU**, **Angstrem T34VG1 ULA** (Soviet gate array), plastic keys, integrated joystick port |

The VI-202 is particularly notable for being one of the few Soviet Spectrums to use the **T34VG1 ULA** — a Soviet-designed gate array that reimplements the Ferranti ULA's functionality in a single chip. (A dedicated `ula_replacements.md` article is planned; see the [section README](README.md) for now.)

> [!WARNING]
> When a Soviet software product refers to running on the "Byte," it almost always means the **Brest (Belarusian) Byte** — the Moldovan variant was produced in much smaller numbers and was largely confined to the Moldavian and Ukrainian markets.

---

## Memory Architecture

### Byte 48K (Standard Configuration)

The 48K Byte uses the standard Sinclair 48K memory map:

```
#0000 - #3FFF   ROM (16 KB, modified Sinclair 48K BASIC with Russian support)
#4000 - #7FFF   Lower RAM (16 KB, "contended" on Sinclair — but NO contention on Byte)
#8000 - #FFFF   Upper RAM (32 KB, uncontended)
```

### Byte 128K (with Expansion)

When a 128 KB expansion module is fitted, the Byte implements the standard Sinclair 128K paging scheme via port `#7FFD`:

```
#0000 - #3FFF   ROM 0 / ROM 1          #7FFD bit 4
#4000 - #7FFF   Bank 5 (fixed)         Always Bank 5
#8000 - #BFFF   Bank 2 (fixed)         Always Bank 2
#C000 - #FFFF   Banks 0–7 (switchable) #7FFD bits 0–2
```

The Byte 128K does **not** support extended paging ports (`#EFF7` or `#DFFD`). There is no official 256K or 1024K Byte variant from BEMZ, though hobbyist expansions using SIMM modules have been built to push the architecture up to 1 MB.

### Port Summary

| Port | Function | Notes |
|---|---|---|
| `#FE` | Border, EAR, MIC, keyboard | Standard — same as all Spectrums |
| `#1F` | Kempston joystick | Built-in (not an expansion) — some configurations only |
| `#7FFD` | 128K paging (128K model only) | Standard — same as Sinclair 128K |
| `#FFFD` | AY register select (128K model) | Standard — AY-3-8910/12 |
| `#BFFD` | AY register data (128K model) | Standard — AY-3-8910/12 |
| `#FF` | Attribute read (some variants) | Returns the attribute byte currently being displayed |

The Byte does **not** decode the Pentagon's `#EFF7`, Scorpion's `#1FFD`, or any extended paging port. Software written for the Byte must work within the standard 48K or 128K memory model.

---

## Programming Considerations

### Timing

The Byte uses **standard 48K frame timing** — this is its main advantage over the Pentagon:

| Parameter | Byte 128K | Pentagon 128K | Sinclair 48K |
|---|---|---|---|
| T-states/frame | 69,888 | 71,680 | 69,888 |
| Scanlines | 312 | 320 | 312 |
| Frame rate | 50.08 Hz | 48.83 Hz | 50.08 Hz |
| Memory contention | **None** | None | `#4000`–`#7FFF` |

The Byte's combination of 48K timing and zero contention makes it one of the **cleanst Soviet clones** for running Western software. Code written for the 48K runs without timing adjustments. The only behavioral difference is the absence of the floating bus — reading `#FF` during screen display does not return the byte the video circuit is fetching.

### Floating Bus

Like all discrete-TTL Soviet clones, the Byte does **not** implement the floating bus. Software that reads contended memory during screen display to detect beam position or steal cycles will not work. This is the same limitation as the Pentagon — see [floating_bus.md](../../05_development/05_display_and_timing/floating_bus.md) for the impact on multicolor effects.

### Disk Support

The base Byte has no disk interface. Software that requires TR-DOS will not work without a Beta 128 expansion or the Byte-01 variant with its CP/M-compatible floppy controller. Most Byte-targeted software was distributed on tape or as snapshot files (`.SNA`, `.Z80`).

### Cyrillic ROM Behavior

The Byte's dual-ROM architecture has a subtle compatibility implication: software that reads character glyphs directly from ROM at `#0000`–`#1FFF` (the character bitmap area in the Sinclair ROM) may see **Cyrillic glyphs** instead of the expected Latin ones, depending on the RUS/LAT toggle state. Software that draws text by calling the standard ROM `RST `#10` (PRINT-V) routine works correctly in either mode.

---

## Software Ecosystem

### Built-in Software

The Byte's ROM contains a **modified Sinclair BASIC interpreter** adapted for the dual Russian/English keyboard layout. The ROM includes:

- **Two switchable character sets** — Latin and Cyrillic, toggled via the RUS/LAT key
- **Two ROM variants** — the original Sinclair 48K ROM and a localized Russian version with translated system messages, selectable via the "СОВМЕСТ" button
- **Standard BASIC commands** for text output (32×24 character mode) and graphics (256×192 pixels)
- **Tape loader** — compatible with standard ZX Spectrum tape formats

The ROM does **not** include any pre-loaded games, applications, or utilities beyond the BASIC interpreter.

### Tape and Disk Software

The Byte software library was dominated by **ZX Spectrum tape software** — games and educational programs loaded from cassette at 1500 baud. Major categories:

- **Ported Western titles** — Dizzy series (with unofficial Russian sequels like *Dizzy X* / *Dizzy X-2*), *Jet Set Willy* variants, *Chuckie Egg*, and hundreds of others
- **Original Soviet games** — *Viking Quest 3* (bilingual text adventure), *Vera*, *Star Inheritance*, *Kolobok Zoom 1-2*, *Spectris* (Tetris variant)
- **Educational software** — BASIC tutorials, math drills, language learning programs developed for Soviet schools
- **Demo scene releases** — Soviet demoscene productions from CC (Chaos Constructions), diHalt, and other parties

Floppy-based software (TR-DOS) became common after the Byte-01's release, distributed via informal tape-trading clubs and regional marketplaces in Moscow, Saint Petersburg, Minsk, and other cities between 1993 and 1997.

### Modern Emulation

The Byte is supported by the **ZXMak2** emulator (Windows), which models the Brest Byte's specific ROM, RAM, and timing behavior. An active collector community maintains documentation, repair guides, and software archives at **zxbyte.ru**. Surviving Byte units in working condition are increasingly rare and have been listed on eBay for around **$150** (as of 2024).

---

## Byte vs Other Factory-Built Clones

| Criterion | Byte (Brest) | Mikrosha (Elektronika) | Robik (Cherkasy) | Raton-9003 (Gomel) |
|---|---|---|---|---|
| **Year** | 1989 | 1989 | 1989 | ~1990 |
| **Origin** | Brest, Belarus (BEMZ) | Soviet state factory | Cherkasy, Ukraine | Gomel, Belarus |
| **Total production** | **60,000+** | Low (state allocation) | Low (regional) | Low (regional) |
| **Max RAM** | 48 KB → 128 KB (expansion) | 48 KB | 48 KB + 16 KB shadow | 48 KB |
| **IC count** | ~80 (8-layer PCB) | ~50 | ~53 | **~19** (minimal) |
| **Timing** | 48K-exact | Approximate 48K | Approximate 48K | Approximate 48K |
| **Disk support** | Optional (Byte-01) | None | None | None |
| **Joystick** | Built-in Kempston | None | None | None |
| **Form factor** | Monoblock case | Single-board | Single-board | Single-board |
| **Cyrillic ROM** | Yes (dual ROM) | Custom Russian | Yes | Yes |

The Byte's main distinction is being the **only mass-produced Soviet Spectrum clone from a state factory in such volumes** — the Mikrosha was produced by a state factory but in much smaller numbers and aimed at a different market segment (consumer home computer, not school deployment).

---

## Cross-References

- [Pentagon 128K](pentagon.md) — the dominant Soviet clone (different timing, different production model)
- [Other Soviet clones](other_clones.md) — Mikrosha, Robik, Raton, LEC, and more
- [Clone timing](clone_timing.md) — Byte vs Pentagon vs 48K timing comparison
- [Byte video frame](../../05_development/05_display_and_timing/video_frame_other_soviet.md) — detailed frame timing
- [Floating bus](../../05_development/05_display_and_timing/floating_bus.md) — why the floating bus doesn't work on TTL clones
- [Clone joysticks](clone_joysticks.md) — Kempston joystick conventions on Soviet clones
- [Contention model](../../05_development/03_memory_and_io/contention_model.md) — why the Byte has no contention
- [Section README](README.md) — notes on the T34VG1 gate array used in the Moldovan VI-202 variant (dedicated `ula_replacements.md` article is planned)

---

## References

- **Brest Electromechanical Plant (BEMZ) archives** — original factory production records, monthly unit counts (1990–1995)
- **Old Computer Museum** (old-computers.com) — Byte hardware reference with component photographs
- **MCbx Old Computer Collection** — Bajt variant documentation with PCB scans and schematic analysis
- **zxbyte.ru** — active collector community forum with repair guides, ROM dumps, and software archives
- [Spectrumpedia III](https://speccy.wiki/) — English-language reference covering Byte variants and Moldovan clones
- **ZXMak2 emulator** — reference implementation of Byte timing and ROM behavior
- **[zx-pk.ru](https://zx-pk.ru) forum** — *Байт* subforum contains build guides, repair threads, and variant documentation
- **VC.ru** ("С паяльником и напильником") — Belarusian DIY computing history, includes Byte factory context
