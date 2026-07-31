[← Home](../../README.md) · [Clone Hardware](README.md)

# Other Soviet and Eastern Bloc Clones — Moskva, Leningrad, Hobbit, Mikrosha, Quorum, LEC, Robik, Delta, Sintez, and Beyond

Beyond the five dominant Soviet clones — [Pentagon](pentagon.md), [Scorpion](scorpion.md), [Kay](kay.md), [ATM Turbo](atm_turbo.md), and [Profi](profi.md) — the post-Soviet Spectrum ecosystem produced **dozens** of additional clones. Most were built in small numbers, served specific regional markets, or were experimental designs that never achieved mass adoption. But collectively, they represent the incredible diversity of the Soviet homebrew hardware scene from 1987 to 1995 — and the parallel Eastern Bloc cloning efforts in Poland, Czechoslovakia, Hungary, Romania, and East Germany that started even earlier, in some cases before the Soviet machines.

This article covers the **hardware and programming characteristics** of the long tail of Soviet clones, plus a section on the non-Soviet Eastern Bloc machines that pre-dated or coexisted with them. For the frame timing of these machines (which is the most common reason programmers need to know about them), see [video_frame_other_soviet.md](../../05_development/05_display_and_timing/video_frame_other_soviet.md). For the cross-clone timing landscape, see [clone_timing.md](clone_timing.md).

---

## Moskva 48K / 128K — The First Mass-Produced Russian Clone

The **Moskva 48K** (Москва, Moscow, 1988) holds the distinction of being the **first mass-produced Russian clone of the 48K Spectrum**. Built in Moscow from discrete TTL logic (no ULA), the Moskva 48K established the template that subsequent Soviet clones would refine — a discrete-logic ULA replacement, KR1858VM1 CPU (Soviet Z80A equivalent), and 48 KB of KR565RU6 DRAM.

The follow-up **Moskva 128K** (1989) was a faithful clone of the Sinclair 128K — adding the `#7FFD` paging port, an AY-3-8910/12 sound chip, a printer interface, joystick port, and TV/RGB output. Notably, it shipped **without a disk drive** — Beta 128 was an optional external addition. Software compatibility was high; the Moskva 128K was a serious attempt to clone the +2 hardware rather than the bare 48K.

The Moskva series is historically important because it proved that a Russian factory could ship a working 128K Spectrum clone at scale, and it predated the Pentagon by roughly a year. However, the Pentagon's open schematics and lower cost eventually displaced the Moskva in the hobbyist market.

---

## Leningrad — The Pentagon's Precursor

The **Leningrad** (Ленинград, designed by **Serge Zonov**, Leningrad, 1987) is the most important of the minor clones — not because of its own success, but because it was the **direct ancestor of the Pentagon**. The Leningrad proved that a Spectrum could be built from discrete TTL logic, and the Pentagon's designers explicitly set out to fix the Leningrad's compatibility problems.

### Leningrad 1 (1987)

The original Leningrad was a 48K-only machine with under 50 ICs:

- **TTL reimplementation** of the ULA's video generation and memory arbitration
- **No memory contention** (the Leningrad's video circuit reads independently of the CPU)
- **Approximate 48K timing** — close but not exact (the video counters were not precisely tuned)
- **No disk support** — tape only
- **No joystick** — Kempston was added as an expansion

### Leningrad 2 (1988)

The Leningrad 2 improved on the original with:

- Better INT signal shaping (the Leningrad 1's INT was noisy)
- Proper black-level clamping (the Leningrad 1 had a slightly washed-out picture)
- Optional 128K expansion via a daughterboard

### Known Compatibility Issues

The Leningrad has several quirks that affect software compatibility:

| Issue | Impact | Workaround |
|---|---|---|
| **Floating bus reads `#FF`** | Software expecting the 48K floating bus behavior gets `#FF` (all bits high) instead of the video-fetch byte | None — software must be adapted or the feature disabled |
| **INT timing drift** | The INT signal is not precisely at the 48K's position | Timing-sensitive code may desync — add a detection routine |
| **`#FF` port behavior** | Reading port `#FF` returns `#FF` instead of the 48K's floating value | Software that uses `IN A,(#FF)` for detection will misidentify the machine |

> [!NOTE]
> Serge Zonov later designed the **Scorpion ZS-256** specifically to fix the Leningrad's compatibility problems. The Scorpion became the "correct timing" alternative to the Pentagon. See [scorpion.md](scorpion.md) for the full Scorpion story.

---

## Sintez — The Signal Factory Clone

The **Sintez** (Синтез) is a Russian clone of the 48K Spectrum with an unusual hardware profile. While software-compatible with the 48K, its internals use a **different memory chip arrangement** that eliminates the original Spectrum's memory slowdown when accessing contended regions. The result is faster-than-expected execution for code that runs in the contended region — but software that depends on the original timing (`HALT`-synchronized loops, multicolor effects that read `#4000`–`#7FFF`) will desync.

The Sintez shipped with **two Interface 2 joystick ports** (rather than the more common Kempston port), placing it firmly in the early-48K-software compatibility camp rather than the Russian 128K + Beta 128 + TR-DOS ecosystem. The Sintez was produced in relatively small numbers; the unrelated **Sintez-M** from the **Signal factory (NPO «Сигнал»)** in the Moldovan SSR (1989) is sometimes conflated with the Russian Sintez but is a separate design.

> [!WARNING]
> The Sintez's lack of memory contention means timing loops tuned for the standard 48K will run **too fast**. Detection is tricky — there is no dedicated ID port. The most reliable detection is to measure the contention pattern by writing to `#FE` from within the contended region and checking the resulting cycle count.

---

## Hobbit — The Educational Clone

The **Hobbit** (Хоббит, designed by **Dmitry Mikhalkov** and team, Leningrad, 1990) is a compact 128K clone aimed at the **educational market**. It was produced in moderate numbers for Soviet schools and was one of the few clones sold with a complete documentation package in Russian. The Hobbit also shipped with a **CP/M mode** and either a **Forth mode or LOGO mode** resident in an on-board ROM — features that set it apart from purely game-focused clones and made it attractive for classroom use.

### Key Features

- **128K RAM** with standard `#7FFD` paging
- **48K-compatible timing** (69,888 T-states, 312 scanlines)
- **Zero memory contention**
- **Integrated tape interface** with enhanced signal conditioning
- **Optional Beta 128 disk interface** (expansion port)
- **Russian-language ROM** with Cyrillic font and keyboard mapping

### Programming Model

The Hobbit is largely Sinclair 128K-compatible. Its main distinguishing feature is the **Cyrillic font ROM** — the standard character set includes both Latin and Cyrillic glyphs, accessible via a mode switch. Software that assumes the standard Sinclair character set will work, but Cyrillic text may not display correctly on non-Hobbit machines.

The Hobbit does **not** support extended paging, turbo mode, or any non-standard video modes. It is a straightforward 128K clone.

---

## Mikrosha — The Soviet-Built Spectrum

The **Mikrosha** (Микроша, produced by the **Elektronika** state factory, 1989–1991) is one of the few Soviet clones produced by an **official state factory** rather than a hobbyist collective. It was sold through state electronics stores and was positioned as a "home computer for the family."

### Architecture

The Mikrosha is a 48K clone with a unique design:

- **Single-board construction** with integrated keyboard
- **KR1858VM1** CPU (Soviet Z80A equivalent)
- **4164 DRAM** (48 KB total)
- **No disk interface** (tape only)
- **Integrated RF modulator** for direct TV connection
- **Built-in power supply** (no external adapter needed — mains directly in)

The Mikrosha's most distinctive feature is its **integrated keyboard** — a full-travel keyboard built into the case, unlike the Spectrum's rubber-key membrane. The keyboard uses a non-standard matrix that is **not** Sinclair-compatible, so software that reads the keyboard directly (rather than through the ROM) may not work.

### Programming Considerations

| Feature | Mikrosha | Sinclair 48K |
|---|---|---|
| **Keyboard matrix** | Non-standard (8 × 8) | Standard (8 × 5 half-rows) |
| **ROM** | Custom Russian 48K ROM | Standard Sinclair 48K ROM |
| **Timing** | Approximately 48K | Standard 48K |
| **Contention** | None | `#4000`–`#7FFF` |
| **Disk** | None | None (48K baseline) |

Software that uses the ROM keyboard routine (`#028E` — KEY-SCAN) works on the Mikrosha. Software that reads the keyboard matrix directly via port `#FE` will not work — the Mikrosha's matrix is different.

---

## Robik — The Military-Factory Conversion

The **Robik** (Робик, produced between **1989 and 1994** by **Selto-Rotor** — the "Scientifically-Technical Industrial-Creative Association", a former military factory) is one of the most enduring Soviet clones. Production spanned the dissolution of the USSR, and the Robik was sold both as a bare board for hobbyist assembly and as a complete desktop system with case, keyboard, and integrated power supply. The full-stroke keyboard has 55 keys (vs the 40-key Sinclair membrane), including separate **EDIT** and **three SHIFT** keys — a layout clearly designed for Russian-language typing rather than gaming.

Robik specifications:

- **Z80A at 3.5 MHz** (Soviet KR1858VM1)
- **48 KB RAM** (4164 DRAM)
- **16 KB ROM** (Sinclair BASIC, sometimes with Russian-localized variant)
- **Graphics**: 256×192, 8 colors (standard Spectrum)
- **Composite video output**
- **No disk interface** (tape only — Beta 128 was an expansion)
- **Kempston joystick port** (optional)

From a programming perspective the Robik is a **straightforward 48K** — no extended paging, no turbo, no special video modes. Its main distinguishing characteristic is the **military-grade build quality** (heavy-gauge steel case, robust keyboard) that has helped many units survive in working condition into the 2020s.

---

## Quorum 64 / 256 / 128

The **Quorum** (Кворум, produced in Moscow, 1990–1992) is a family of low-cost clones aimed at the budget market. Three models were produced:

| Model | RAM | Paging | Disk | Notes |
|---|---|---|---|---|
| **Quorum 64** | 64 KB | None | Tape only | Cheapest model — 48K with extra 16K |
| **Quorum 128** | 128 KB | `#7FFD` | Optional | Standard 128K clone |
| **Quorum 256** | 256 KB | `#7FFD` + `#DFFD` | Optional | Extended memory via `#DFFD` |

### Architecture

The Quorum uses a hybrid design — part discrete TTL, part Soviet-made gate array (Т34ВГ1). The Т34ВГ1 is a Soviet-produced ULA replacement that implements the video generation and memory arbitration functions. See [ula_replacements.md](ula_replacements.md) for details on this chip.

The Quorum's timing is **approximately 48K-compatible** — close enough for most software, but with minor INT timing drift that can affect cycle-exact code.

### Programming Considerations

- **48K timing** with minor drift
- **Quorum 256** uses port `#DFFD` for extended paging (different bit layout from Kay and Profi)
- **Т34ВГ1 gate array** has slightly different floating-bus behavior from the Ferranti ULA
- **Integrated Kempston joystick** on all models

---

## Delta, Delta S-128, Delta SA/SB — The Zelenograd Family

The **Delta** family is a set of related clones produced across multiple Soviet cities. The original **Delta** (1991, near **Zelenograd**) is a near-perfect clone of the ZX Spectrum+ — fully software-compatible, with 48 KB RAM, composite video, cassette I/O, two joystick ports (both Kempston and Sinclair), RGB adjustment controls, and a Russian-specific expansion port. The Delta originally sold for around **620 Deutschmarks** (about $380 in 1991), and was a bestseller in the Moscow region for several months.

The **Delta S-128** (1990, **Voronezh and Kazan**) is a more advanced modular design that can run at up to **7 MHz turbo**, includes Kempston and Sinclair joystick ports, both TV and RGB monitor outputs, a printer interface, a sound processor (AY-3-8910/12), and an optional disk controller.

The **Delta SA** and **Delta SB** are variants that were partly manufactured in **Tbilisi, Republic of Georgia**, at the (now abandoned) Military Scientific Plant **"Skhivi"**. No reference to the real Georgian manufacturer was given on the units — all data refer to Zelenograd as the origin. The difference can be identified only by the correction table in the user manual: original manuals had hand-written and rotoscoped corrections, while the Georgian release included a computer-typed correction list.

> [!NOTE]
> There are persistent reports that some Delta units were actually **re-badged unsold ZX Spectrums from the UK** — with various stickers covering up "Made in the UK" hints and Sinclair badging. Whether these are accurate or apocryphal is unclear, but the Delta's near-perfect Spectrum+ compatibility (vs the usually loose timing of other Soviet clones) gives the story some plausibility for at least a subset of units.

---

## LEC 48 / 528

The **LEC** (ЛЭК, produced in Minsk, Belarus, 1991) is another low-cost clone family. The "LEC" name stands for "Лёгкий Электронный Компьютер" (Light Electronic Computer).

| Model | RAM | Notes |
|---|---|---|
| **LEC 48** | 48 KB | Basic 48K clone |
| **LEC 528** | 528 KB | Extended memory via `#DFFD` |

The LEC is notable for its **unusual 528 KB configuration** — 32 banks of 16 KB plus an extra 16 KB fixed bank. This is not a power-of-two size, and the extended paging port (`#DFFD`) has a non-standard bit layout:

```
Port #DFFD (LEC 528 extended paging):
  Bits 0–3: Extended bank bits (4 bits → 16 groups × 8 banks = 128 banks max)
            But only 33 banks are physically populated (528 KB / 16 KB = 33)
```

> [!WARNING]
> Software that targets the LEC 528 must account for the **non-power-of-two bank count**. Writing a bank number beyond 32 will page in undefined memory (typically `#FF` or `#00`).

The LEC uses **standard 48K frame timing** with zero contention. It is one of the cleaner Belarusian clones from a compatibility perspective.

---

## Composite — The Integrated Clone

The **Composite** (Композит, various producers, 1989–1992) is a generic name for a class of Soviet clones that were **integrated into a single case** with monitor, keyboard, and tape deck — similar to the Amstrad CPC 464 or Commodore 64 form factor. Several different manufacturers produced "Composite" machines with varying specifications:

- **Composite-128** — 128K clone with integrated 10-inch monochrome monitor
- **Composite-256** — 256K clone with integrated color monitor
- **Composite-512** — 512K clone with RGB monitor and built-in disk drive

The Composite machines were aimed at the **educational and office markets** — they were sold as complete systems, not as bare boards for home assembly. They were produced in relatively small numbers and are rare today.

From a programming perspective, the Composite machines are **standard 128K clones** with `#7FFD` paging and 48K-compatible timing. The integrated peripherals (monitor, tape) do not affect the programming model.

---

## Peters MC64 / Peters 256 — Sprinter Precursors

The **Peters MC64** (circa 1993) and **Peters 256** are the predecessors to the [Sprinter](../newgen/sprinter.md), produced by **Peters Plus, Ltd.** (St. Petersburg) — the same firm that later designed the Sprinter. The naming reflects the firm's identity ("Peters") and the RAM size (64 KB or 256 KB).

The **Peters MC64** came in two sub-variants:

- **Peters MC64S1** — Service Monitor ROM with fast loader, assembler, video test, and tape copyist
- **Peters MC64S2** — Service Monitor 2 adds Tetris, video test, tape copyist, and text editor; Centronics printer port

The **Peters 256** (Peters MD-256S3) ships with Service Monitor 3, which includes **IS-DOS** — an alternative disk operating system to TR-DOS. This is historically significant: IS-DOS was a uniquely Russian attempt to escape TR-DOS's design constraints, and Peters Plus carried the lessons forward into the Sprinter's Estex OS.

These machines are rare today but are important as the **direct ancestors of the Sprinter** — the Sprinter's design philosophy (Peters Plus, 4 MB RAM, ISA bus, CGA video, IS-DOS lineage) is already visible in the Peters 256's feature set.

---

## GrandRomMax / Grandboard 2+ — Pentagon Derivatives

The **GrandRomMax** (GRM, 1993, Moscow) is a Pentagon-derived clone with one important fix: the **INT signal is reworked to match the original 48K's position** rather than the Pentagon's notorious 320-line timing. There are four or five GRM models with minor differences between them — most notoriously, one variant has a non-standard turbo Beta Disk interface: disks written on that GRM are unreadable on any other machine, and vice versa.

The **Grandboard 2+** (1994, **Frajzino**, Independent Science-Manufacturing Laboratory of Computer Techniques) uses the GRM2+ board as its base and adds:

- **Z80 NEC** at 3.45 MHz
- **128 KB RAM**
- **24×32 text mode** and **256×192 graphics**, both 8 colors
- **BASIC + TR-DOS 5.03 + LPRINT 3**
- **Turbo mode**, cassette and **2× 720 KB FDD**, mouse, **AY-8910m (YM2149F)**, printer

These are Pentagon-family machines and behave like the Pentagon for timing purposes — the GRM's INT fix is the main compatibility concern.

---

## Smaller and Regional Soviet Clones

The Soviet clone ecosystem produced many additional machines, most with very small production runs. A non-exhaustive catalog of notable minor clones:

| Clone | Year | Origin | Notes |
|---|---|---|---|
| **Dubna 48K** | 1989 | **Dubna** (near Moscow) | Soviet Z80 analog, 48K — named after the town |
| **Nafanja** | 1990 | Russia | Portable clone in a case — made for **diplomatic offices and children**; 650 rubles at launch; compatible with Dubna 48K |
| **Santaka 002** | 1990 | **Lithuania** | Spectrum+ clone, Russian keyboard glyphs; produced by ex-military plants as part of a conversion program; reported as reliable |
| **Spektr 48** | 1991 | **Oryol** (Oryol PC factory, former military) | 48K clone with membrane keyboard, Latin + Cyrillic letters, monitor program in ROM |
| **Sever (Nord) 48/002** | 1990 | Russia | 64 KB RAM, 16 KB ROM, 12×8×2½ inch case |
| **Krasnogorsk** | 1991 | Russia | Used the **PZY K573PF2(5)** Soviet IC for TV signal generation |
| **Master** | 1990 | Russia | Ran at **2.5 MHz** (slower than standard!) — likely related to Master K11 |
| **Master K** | 1991 | **Ivanovo** | 48K, 16K ROM, built-in (?) Kempston joystick interface |
| **Baltica** | ~1990 | Russia | Used **K556PT4 + K155PE3** as ULA replacement; CPU ran at **4 MHz** (less compatible) |
| **Best III** | 1993 | **St. Petersburg** | 16.8 × 10 × 2½ inch case; uses Russian Z80 clone CPU |
| **Bi Am ZX-Spectrum 48/64 / 128** | 1992–1994 | Russia | Metal-case clone marked "Made in RF" (Russian Federation) |
| **Moskva 48K / 128K** | 1988 / 1989 | **Moscow** | First mass-produced Russian clone (see above) |
| **Kvorum** (64 / 128 / 128+) | various | Russia | Kvorum 128 had built-in monitor/copyist ROM; 128+ shipped with 3.5" drive |
| **AZX-Monstrum** | ~1993 | Russia (open project) | **Zilog Z380** (32-bit Z80 derivative, 40 MHz), 4 GB linear RAM, DMA, AT-keyboard, own BIOS — only HDD controller was built |
| **ZX-Forum 2** ("ZX Next") | ~1995 | Russia | **Dual Z80** (one as video CPU), RS-232, turbo, IBM keyboard, **10 Mbit/s LAN**, **640×200 CGA**, up to 512 KB RAM |

---

## Eastern Bloc Clones (Non-Soviet)

In parallel with the Soviet cloning scene, every Warsaw Pact country plus Yugoslavia developed its own Spectrum clones — often **before** the Soviet machines appeared. The Eastern Bloc clones were typically produced by state electronics firms (often the local Robotron / Iskra / ICE Felix equivalent) and shipped through state stores.

### Romania — The Earliest and Most Diverse

Romania was the first Eastern Bloc country to clone the Spectrum, and produced the most diverse set of machines:

| Clone | Year | Manufacturer | Notes |
|---|---|---|---|
| **Felix HC 85** | 1985 | **ICE Felix** | First of the HC series — closely resembled the 48K Spectrum, Z80A, 48K RAM; widely used in Romanian schools |
| **Felix HC 88 / 90 / 91** | 1988–1991 | ICE Felix | HC 90/91 added optional CP/M via extension board; HC 91 had a 50-key keyboard |
| **Felix HC 2000** | 1992–1994 | ICE Felix | Built-in **3.5" 720K floppy**, 64 KB RAM; could run as Spectrum (48K mode) or full CP/M (64K mode) |
| **CIP-03** | ~1986 | **Întreprinderea Electronică** | "Calculator pentru Instrucție Personală" (computer for personal teaching); 45 chips on the PCB, mostly 74-family; ROM labeled "BASIC S" instead of Sinclair copyright |
| **Cobra** | ~1986 | Brașov | Romanian clone with limited documentation |
| **TimS** | ~1987 | University of Timișoara | Name from **TIMișoara + Spectrum**; 64 KB RAM; later models added joystick, **192 KB RAM** and **AY-3-8912** |
| **JET** | ~1989 | Romania | Casing was **adapted from a telephone** |

### Poland

- **Elwro 800 Junior** — full-size keyboard with paper holder (the case was originally designed for a small electric organ); later **804 Junior PC** added internal 3.5" floppy. A version of **CP/J** (CP/M derivative) was available.

### Czechoslovakia

- **Didaktik** — series of home computers; later Spectrum-compatible models used the **U880** (East German Z80 clone) or original Zilog Z80
- **Mistrum** — 48K Czech clone; ROM included Latin and Czech-diacritic character sets; design published in *Amatérské Radio* 1/89 — builders made their own cases and keyboards

### Hungary

- **HT 3080C** (1986, **Híradástechnikai Szövetkezet**) — switchable between **TRS-80 mode** and **ZX Spectrum mode**; 32K ROM (HT + Speccy); 64K RAM; AY sound chip; **Commodore serial port** for connecting the 1541 disk drive. Designed for Hungarian school computers that were required to support high-resolution graphics and Hungarian characters.

### East Germany

- **Spectral** — East German clone with built-in joystick interface; sold as a kit by **Hübner Elektronik**; 48K or 128K variants. East Germany also produced the **U880** CPU — a Z80 clone used in many Eastern Bloc machines.

### Other Regions

- **Investronica Inves Spectrum 48k plus** (Spain) — released after Amstrad bought Sinclair; cloned the Spectrum+; had compatibility issues with some games (Bombjack, Commando, Top Gun)
- **Czerweny CZ Spectrum / Spectrum Plus** (Argentina) — produced by the Czerweny company
- **Microdigital TK 90X / TK 95** (Brazil, 1985/1986) — first Brazilian Spectrum clones; TK 95 was a cosmetic evolution of TK 90X

> [!NOTE]
> The Eastern Bloc machines generally predate the Russian clones and represent the **first wave of unofficial Spectrum cloning** — ICE Felix started the HC series in 1985, three years before the Soviet Moskva 48K (1988) and four years before the Pentagon (1989). Many Russian clones drew on Eastern Bloc engineering and reverse-engineering work.

---

## Quick Reference — Clone Comparison Table

| Clone | Year | Origin | Max RAM | Timing | Contention | Disk | Unique feature |
|---|---|---|---|---|---|---|---|
| **Moskva 48K/128K** | 1988 / 1989 | Moscow | 48 / 128K | Approx. 48K | None | None | First mass-produced Russian clone |
| **Leningrad 1/2** | 1987 | Leningrad | 48 / 128K | Approx. 48K | None | Tape | Pentagon precursor (Serge Zonov design) |
| **Sintez** | ~1989 | Russia | 48K | 48K (no contention) | **None** (no slowdown) | Tape | Interface 2 joystick ports |
| **Hobbit** | 1990 | Leningrad | 128K | 48K-exact | None | Optional | Cyrillic ROM, **CP/M + Forth/LOGO modes**, educational |
| **Mikrosha** | 1989 | State factory | 48K | Approx. 48K | None | Tape | Integrated keyboard, non-standard matrix |
| **Robik** | 1989–1994 | Selto-Rotor (former military) | 48K | 48K-exact | None | Tape | 55-key keyboard, military-grade build |
| **Quorum 64/128/256** | 1990 | Moscow | 64/128/256K | Approx. 48K | None | Optional | Т34ВГ1 gate array |
| **Delta / S-128 / SA / SB** | 1990–1991 | Zelenograd / Voronezh / Kazan / Tbilisi | 48–128K | **48K-exact** (turbo on S-128) | None | Optional | Possibly re-badged UK Spectrums; modular |
| **LEC 48/528** | 1991 | Minsk | 48 / 528K | 48K-exact | None | Optional | Non-power-of-two 528K |
| **Composite** | 1989 | Various | 128–512K | 48K | None | Some models | All-in-one form factor |
| **Byte** | 1989 | Brest, Belarus | 48 / 128K | 48K-exact | None | Optional | ~80 ICs on 8-layer PCB (see [byte.md](byte.md)) |
| **Peters MC64 / 256** | 1993 | St. Petersburg (Peters Plus) | 64 / 256K | Approx. 48K | None | Optional | Sprinter precursor; **IS-DOS** on 256 |
| **GrandRomMax / Grandboard 2+** | 1993–1994 | Moscow / Frajzino | 128K | Pentagon (INT fixed) | None | Yes | Pentagon derivative; AY-8910m (YM2149F) |
| **Felix HC 85/90/91/2000** | 1985–1994 | Romania (ICE Felix) | 48–64K | 48K | Standard 48K | HC 2000 built-in | First Eastern Bloc clone (1985) |
| **CIP-03** | ~1986 | Romania | 48K | 48K | Standard 48K | None | 45 chips (mostly 74-family); "BASIC S" ROM |
| **TimS** | ~1987 | Romania (Timișoara) | 64–192K | 48K | Standard 48K | Optional | AY-3-8912 on later models |
| **HT 3080C** | 1986 | Hungary | 64K | 48K | Standard 48K | Commodore 1541 | **TRS-80 + Spectrum** dual-mode |
| **Elwro 800 Junior** | ~1986 | Poland | 64K | 48K | Standard 48K | Optional (804) | Paper holder (organ case); **CP/J** |
| **Didaktik** | various | Czechoslovakia | 48–128K | 48K | Standard 48K | Some models | U880 (East German Z80 clone) |
| **Spectral** | ~1987 | East Germany (Hübner) | 48 / 128K | 48K | Standard 48K | None | Kit form; built-in joystick interface |
| **Inves Spectrum+** | ~1987 | Spain (Investronica) | 48K | 48K | Standard 48K | None | Official-looking Spectrum+ clone |
| **TK 90X / 95** | 1985 / 1986 | Brazil (Microdigital) | 48K | 48K | Standard 48K | None | First Brazilian clones |

---

## Cross-References

- [Pentagon 128K](pentagon.md) — the dominant Soviet clone
- [Pentagon 1024](pentagon_1024.md) — 1 MB variant
- [Scorpion](scorpion.md) — the "correct timing" alternative (Leningrad successor)
- [Kay 1024](kay.md) — professional clone with Nemo bus
- [ATM Turbo](atm_turbo.md) — CP/M-capable clone
- [Profi](profi.md) — Ukrainian professional clone with ISA/VGA
- [Byte](byte.md) — compact Ukrainian clone
- [Clone timing](clone_timing.md) — cross-clone timing comparison and detection
- [ULA replacements](ula_replacements.md) — Soviet-made gate arrays (Т34ВГ1, etc.)
- [Clone video frames](../../05_development/05_display_and_timing/video_frame_other_soviet.md) — detailed timing for all clones
- [Floating bus](../../05_development/05_display_and_timing/floating_bus.md) — why TTL clones lack the floating bus
- [Soviet demoscene](../../07_demoscene/soviet_demo_scene.md) — cultural context

---

## References

- **List of ZX Spectrum clones** (Wikipedia / en-academic.com) — comprehensive list of Soviet, Eastern Bloc, and worldwide clones; primary source for the catalog above
- **ZX-Review magazine** (1989–1995) — primary Russian-language source for clone construction articles, schematics, and reviews
- **zx-pk.ru forum** — individual subforums for each clone contain schematics, build guides, and repair threads (Russian)
- **SpeccyWiki (speccy.info)** — comprehensive clone encyclopedia with photos and specifications
- **Zonov, S.** — *"The Scorpion Story"* (ZX-Review, 1994) — Leningrad-to-Scorpion evolution
- **chibiakumas.com** — English translations of Russian clone hardware articles
- **Unreal Speccy emulator** — reference implementations of all clones listed here (see `machines/` directory)
- **ZX Evolution wiki** (zxevo.ru) — clone compatibility database and timing measurements
- **Planet Sinclair: Clones and Variants** — English-language overview of the international clone ecosystem
- **Soviet ZX Spectrum clones** (Zoe Blade's notebook, notebook.zoeblade.com) — curated English-language index of Soviet clones
- **Alone Coder, *ACNews* series** — Russian-language retrospective articles on minor Soviet clone manufacturers
- **icefelix.ro / hc85.3x.ro** — Romanian Felix HC series documentation (Romanian/English)
- **Didaktik.sk** — Slovak Didaktik clone documentation
