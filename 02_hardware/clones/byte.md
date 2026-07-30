[← Home](../../README.md) · [Clone Hardware](README.md)

# Byte — The Compact Ukrainian Spectrum Clone

The **Byte** (Байт, designed in Ukraine, 1991) is a compact, low-cost Soviet ZX Spectrum clone that prioritized **minimal component count** over expansion capability. Where the Pentagon was a full-featured machine with disk support and the Profi added ISA expansion, the Byte was designed to be the **cheapest possible working Spectrum** — a machine that could be built from the absolute minimum number of ICs and still run the entire Spectrum software library.

The Byte is notable for being one of the **cleanest 48K-compatible clones** from a timing perspective. It uses standard 48K frame timing (69,888 T-states, 312 scanlines, 50.08 Hz) with zero memory contention, making it an excellent target for cross-platform software that must run on both Western and Russian hardware.

> [!NOTE]
> This article covers the **hardware platform**. For the Byte's frame timing, see [video_frame_other_soviet.md](../../05_development/05_display_and_timing/video_frame_other_soviet.md). For the broader clone timing landscape, see [clone_timing.md](clone_timing.md).

---

## History and Context

The Byte was designed in 1991 in Ukraine, at the height of the Soviet clone boom. By this point, the Pentagon had already established itself as the dominant Russian clone, but the Pentagon's relatively high component count (~50 ICs) and requirement for the Beta 128 disk interface made it expensive for home builders. The Byte was an attempt to create a **truly minimal** Spectrum — targeting the same budget-conscious market segment as the Leningrad, but with better 48K compatibility.

The Byte was produced in relatively small numbers compared to the Pentagon and Scorpion, primarily in Ukraine. It never achieved the mass popularity of the Pentagon, but it gained a reputation as a **reliable, no-frills** machine that was easy to build and maintain. Several variants were produced, including 48K and 128K versions.

---

## Hardware Architecture

The Byte's design philosophy is **radical simplification**. Where the Pentagon uses ~50 ICs and the Scorpion uses 100+, the Byte uses **fewer than 30 ICs** total:

### Component Count Comparison

| Component | Pentagon 128K | Byte 128K | Scorpion ZS-256 |
|---|---|---|---|
| **Total IC count** | ~50 | **~28** | ~100+ |
| **CPU** | КР1858ВМ1 (Z80A) | КР1858ВМ1 (Z80A) | КР1858ВМ1 (Z80A) |
| **Lower RAM** | 8 × 4116 (К565РУ5) | 8 × 4164 (К565РУ5) | 8 × 4464 (4-bit × 8K) |
| **Upper RAM** | 8 × 4164 per bank | 2 × 4464 (4-bit × 8K) | 32 × 4464 |
| **ROM** | 27C256 (32 KB) | 27C256 (32 KB) | 27C512 (64 KB) |
| **Glue logic** | 74LS series (discrete) | **CMOS 74HC series** (lower power) | 74ALS + PALs |
| **FDC** | Beta 128 (WD1793) | **None** (tape only on base model) | Beta 128 + SMUC |

### Key Design Decisions

1. **4464 DRAM instead of 4164** — The 4464 (64 Kbit × 4) stores 4 bits per chip, so only 2 chips are needed per 16 KB bank (vs 8 chips with the 4164). This halves the RAM chip count and significantly reduces PCB complexity. The Byte was one of the first Soviet clones to adopt the 4464 widely.

2. **No built-in disk interface** — The base Byte model supports only tape loading, keeping the cost down. A disk interface (Beta 128 compatible) was available as an expansion, but most Byte machines were used with tape.

3. **CMOS logic (74HC) instead of TTL (74LS)** — The Byte uses CMOS logic throughout, which draws significantly less power than the Pentagon's TTL. This allows the Byte to run cooler and from a wider range of power supplies.

4. **Integrated Kempston joystick** — Despite its minimal design, the Byte includes a built-in Kempston joystick port (decoded at `#1F`), reflecting the game-oriented target market.

---

## Memory Architecture

### Byte 48K

The 48K Byte is the simplest configuration — a straightforward 48K Spectrum with the standard memory map:

```
#0000 - #3FFF   ROM (16 KB, 48K BASIC)
#4000 - #7FFF   Lower RAM (16 KB, contended on Sinclair — NOT on Byte)
#8000 - #FFFF   Upper RAM (32 KB, uncontended)
```

### Byte 128K

The 128K Byte adds the standard `#7FFD` paging register, making it software-compatible with the Sinclair 128K:

```
#0000 - #3FFF   ROM 0 / ROM 1          #7FFD bit 4
#4000 - #7FFF   Bank 5 (fixed)         Always Bank 5
#8000 - #BFFF   Bank 2 (fixed)         Always Bank 2
#C000 - #FFFF   Banks 0–7 (switchable) #7FFD bits 0–2
```

The Byte 128K does **not** support extended paging (`#EFF7` or `#DFFD`). There is no 256K or 1024K Byte variant — the design is strictly 48K or 128K. Users who needed more RAM were expected to add a Beta 128 disk interface (which pages its own TR-DOS ROM into the memory map) or migrate to a Pentagon/Kay/Scorpion.

### Port Summary

| Port | Function | Notes |
|---|---|---|
| `#FE` | Border, EAR, MIC, keyboard | Standard — same as all Spectrums |
| `#1F` | Kempston joystick | Built-in (not an expansion) |
| `#7FFD` | 128K paging (128K model only) | Standard — same as Sinclair 128K |
| `#FFFD` | AY register select (128K model) | Standard — AY-3-8912 |
| `#BFFD` | AY register data (128K model) | Standard — AY-3-8912 |

The Byte does **not** decode `#EFF7`, `#DFFD`, or any extended paging port. It also does **not** have the Pentagon's port `#77` shadow port. Software written for the Byte must work within the standard 128K memory model.

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

The Byte's combination of 48K timing and zero contention makes it the **cleanest Soviet clone** for running Western software. Code written for the 48K runs without timing adjustments (beyond removing contention delays). The only behavioral difference is the absence of the floating bus — reading `#FF` during screen display does not return the byte the ULA is fetching (because there is no ULA fetching).

### Floating Bus

Like all discrete-TTL Soviet clones, the Byte does **not** implement the floating bus. Software that reads contended memory during screen display to detect beam position or steal cycles will not work on the Byte. This is the same limitation as the Pentagon — see [floating_bus.md](../../05_development/05_display_and_timing/floating_bus.md) for the impact on multicolor effects.

### Disk Support

The base Byte has no disk interface. Software that requires TR-DOS will not work without a Beta 128 expansion. Most Byte-targeted software was distributed on tape or as snapshot files (`.SNA`, `.Z80`).

---

## Byte vs Other Minimal Clones

| Criterion | Byte 128K | Leningrad 2 | Quorum 128 |
|---|---|---|---|
| **IC count** | ~28 | ~45 | ~35 |
| **Max RAM** | 128 KB | 48 KB | 128 KB |
| **Timing** | 48K-exact | Approximate | 48K-exact |
| **Disk support** | Optional expansion | No | Optional expansion |
| **Joystick** | Built-in Kempston | No | No |
| **Production volume** | Moderate (Ukraine) | High (USSR-wide) | Low (Russia) |

The Byte's main advantage over the Leningrad is **better 48K compatibility** (proper timing, proper INT signal) and the built-in joystick port. Its main advantage over the Quorum is simpler construction and wider Ukrainian availability.

---

## Cross-References

- [Pentagon 128K](pentagon.md) — the dominant Soviet clone (different timing)
- [Other Soviet clones](other_clones.md) — Leningrad, Quorum, LEC, and more
- [Clone timing](clone_timing.md) — Byte vs Pentagon vs 48K timing comparison
- [Byte video frame](../../05_development/05_display_and_timing/video_frame_other_soviet.md) — detailed frame timing
- [Floating bus](../../05_development/05_display_and_timing/floating_bus.md) — why the floating bus doesn't work on TTL clones
- [Clone joysticks](clone_joysticks.md) — Kempston joystick conventions on Soviet clones
- [Contention model](../../05_development/03_memory_and_io/contention_model.md) — why the Byte has no contention

---

## References

- **Byte schematic** (1991, Ukraine) — original design, distributed via Ukrainian electronics magazines
- **zx-pk.ru forum** — *Байт* subforum contains build guides, repair threads, and variant documentation
- **SpeccyWiki (speccy.info)** — Byte 48K/128K articles with component lists and PCB photos
- **Unreal Speccy emulator** — reference implementation of Byte timing (48K-exact mode)
- **ZX-Review magazine** (1991–1993) — Byte construction articles and 4464 RAM usage guides
