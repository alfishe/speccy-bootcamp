[← Home](../../README.md) · [Clone Hardware](README.md)

# Other Soviet Clones — Hobbit, Leningrad, Mikrosha, Quorum, LEC, Composite

Beyond the five dominant Soviet clones — [Pentagon](pentagon.md), [Scorpion](scorpion.md), [Kay](kay.md), [ATM Turbo](atm_turbo.md), and [Profi](profi.md) — the post-Soviet Spectrum ecosystem produced **dozens** of additional clones. Most were built in small numbers, served specific regional markets, or were experimental designs that never achieved mass adoption. But collectively, they represent the incredible diversity of the Soviet homebrew hardware scene from 1987 to 1995.

This article covers the **hardware and programming characteristics** of the long tail of Soviet clones. For the frame timing of these machines (which is the most common reason programmers need to know about them), see [video_frame_other_soviet.md](../../05_development/05_display_and_timing/video_frame_other_soviet.md). For the cross-clone timing landscape, see [clone_timing.md](clone_timing.md).

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

## Hobbit — The Educational Clone

The **Hobbit** (Хоббит, designed by **Dmitry Mikhalkov** and team, Leningrad, 1990) is a compact 128K clone aimed at the **educational market**. It was produced in moderate numbers for Soviet schools and was one of the few clones sold with a complete documentation package in Russian.

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

## Quick Reference — Clone Comparison Table

| Clone | Year | Origin | Max RAM | Timing | Contention | Disk | Unique feature |
|---|---|---|---|---|---|---|---|
| **Leningrad 1/2** | 1987 | Leningrad | 48/128K | Approx. 48K | None | Tape | Pentagon precursor |
| **Hobbit** | 1990 | Leningrad | 128K | 48K-exact | None | Optional | Cyrillic ROM, educational |
| **Mikrosha** | 1989 | State factory | 48K | Approx. 48K | None | Tape | Integrated keyboard, non-standard matrix |
| **Quorum 64/128/256** | 1990 | Moscow | 64/128/256K | Approx. 48K | None | Optional | Т34ВГ1 gate array |
| **LEC 48/528** | 1991 | Minsk | 48/528K | 48K-exact | None | Optional | Non-power-of-two 528K |
| **Composite** | 1989 | Various | 128–512K | 48K | None | Some models | All-in-one form factor |
| **Byte** | 1991 | Ukraine | 48/128K | 48K-exact | None | Optional | Minimal IC count (see [byte.md](byte.md)) |

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

- **ZX-Review magazine** (1989–1995) — primary source for clone construction articles and schematics
- **zx-pk.ru forum** — individual subforums for each clone contain schematics, build guides, and repair threads
- **SpeccyWiki (speccy.info)** — comprehensive clone encyclopedia with photos and specifications
- **Zonov, S.** — *"The Scorpion Story"* (ZX-Review, 1994) — Leningrad-to-Scorpion evolution
- **chibiakumas.com** — English translations of Russian clone hardware articles
- **Unreal Speccy emulator** — reference implementations of all clones listed here (see `machines/` directory)
- **ZX Evolution wiki** (zxevo.ru) — clone compatibility database and timing measurements
