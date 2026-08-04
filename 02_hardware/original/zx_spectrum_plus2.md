[← Home](../../README.md) · [Original Hardware](README.md)

# ZX Spectrum +2 — Amstrad's "Grey" Reinvention

The **ZX Spectrum +2** (popularly known as the **"+2 grey"** or **"Amstrad grey"** to distinguish it from the later black +2A) was launched by **Amstrad Consumer Electronics plc** on **14 August 1986** at the **Personal Computer World Show** in London, priced at **£149.99**. It was the **first Spectrum released after Amstrad's acquisition** of the Sinclair computer brand in April 1986, and the first Spectrum to feature a **built-in full-travel typewriter-style keyboard** — replacing the rubber-key layout of the 48K and the cramped chiclet keyboard of the 128K.

The +2 is, from a programmer's perspective, **almost identical to the 128K**. It uses the same bank-switched memory layout, the same `#7FFD` paging register, the same AY-3-8912 sound chip at the same I/O ports, the same 32 KB dual-bank ROM, the same 228-T-state scanline, and the same per-bank contention model. The differences are almost entirely cosmetic and industrial: a new case, a new keyboard, the removal of the RS-232/MIDI ports and the keypad, and minor firmware revisions to support the new keyboard layout.

The +2 was Amstrad's commercial strategy for revitalising the Spectrum brand: take the 128K's electronics (already designed, tested, and in production), repackage them in a more attractive and durable case with a proper keyboard, drop the price, and ship in volume. The strategy worked — the +2 sold over a million units across Europe between 1986 and 1990, and became the **best-selling Spectrum model of all time**.

> [!NOTE]
> This article focuses on the +2's **physical, industrial, and commercial differences** from the 128K. For the underlying architecture (memory banking, contention, ports, AY chip, ROM layout), see [zx_spectrum_128.md](zx_spectrum_128.md) — those sections are not duplicated here. For the +2's successor with the Amstrad ASIC redesign, see [zx_spectrum_plus2a_plus3.md](zx_spectrum_plus2a_plus3.md).

---

## History

### The Amstrad Acquisition (April 1986)

In April 1986, **Clive Sinclair sold the Sinclair Research computer business to Amstrad for £5 million**. The sale included:

- All rights to the ZX Spectrum 16K, 48K, 128K, and Spectrum+ designs
- The "Sinclair" brand name and logo (in the computer market only)
- All existing inventory, tooling, and PCB designs
- The rights to the unreleased "Darwin II" project (which eventually became the +3)

Amstrad's motivation was straightforward: the Spectrum had an enormous installed base (over 3 million units in the UK alone by 1986), an enormous software library (over 6,000 commercial titles), and enormous brand recognition — but Sinclair Research was losing money and unable to capitalize on these assets. Amstrad, led by **Alan Sugar** (later Lord Sugar), saw an opportunity to monetize the Spectrum brand by aggressive cost-reduction and packaging improvements.

### Design Goals for the +2

Amstrad's product brief for the +2 was:

1. **Use the existing 128K electronics unchanged** — Sinclair's gate array, RAM, ROM, and AY chip were already proven designs. Re-engineering them would delay the launch and risk compatibility bugs.
2. **Replace the case with a BBC-Micro-style slab** — a serious-looking typewriter-keyboard machine that looked more like a competitor to the Acorn BBC Micro or Amstrad CPC than to the rubber-key 48K.
3. **Replace the rubber keyboard with a full-travel keyboard** — addressing the most common complaint about the 48K.
4. **Drop the RS-232/MIDI ports and the numeric keypad** — these had been Spanish-market requirements on the 128K but were unused by UK consumers and added cost.
5. **Hit the £149.99 price point** — £30 less than the 128K's launch price, undercutting the Commodore 64 and Atari 800XL.

The +2 launched on 14 August 1986 to positive reviews. The keyboard quality was praised, the price was competitive, and compatibility with the 128K's software library was immediate — every 128K game worked on the +2 without modification.

### Commercial Reception

The +2 was Amstrad's biggest commercial success in the home computer market. Sales figures (variously reported):

- **1986 (Aug–Dec)**: ~250,000 units in the UK
- **1987**: ~450,000 units across Europe
- **1988**: ~350,000 units (alongside the new +2A)
- **1989**: ~150,000 units (final year of grey +2 production, before being fully replaced by the +2A)

Total grey +2 production is estimated at over **1.5 million units** across UK, Spain, and other European markets. This makes the +2 the best-selling Spectrum of all time, and the second-best-selling 8-bit computer in Europe after the Commodore 64.

---

## Board and Internal Design

The +2's PCB (issue 1 through issue 6) is **functionally identical to the 128K issue 3 board**. It uses the same components:

- **Z8400AB1** Z80A CPU
- **Sinclair 8K5 / 7K0 gate array** (the same custom chip as the 128K)
- **AY-3-8912** sound chip
- **32 KB mask ROM** (the 128K/+2 firmware)
- **16 × 8464 DRAM** chips (128 KB total)
- Standard 74LS-series TTL for address decoding and glue

The differences from the 128K board are:

- **No RS-232 / MIDI interface circuitry** — the MC1488/MC1489 line drivers are omitted
- **No keypad interface** — the AY's I/O port is still present but not connected to anything external
- **Different keyboard connector** — the +2 uses a 13-way ribbon cable to a matrix PCB under the typewriter keyboard, vs the 128K's two separate connectors for the main keyboard and the keypad
- **Different power supply circuitry** — the +2 includes a small audio amplifier on the PCB (the 128K's amplifier was on a separate daughter board)
- **Different firmware in ROM** — minor changes for the new keyboard layout, plus support for the +2's tape-loading sound cues

### The Gate Array (Same as 128K)

The +2 uses the **same Sinclair 8K5 / 7K0 gate array** as the 128K. This is the source of the +2's most important compatibility property: **the +2 has the exact same contention model as the 128K** (per-bank contention, banks 1/3/5/7 contended, 228-T-state scanline). Any 128K software that depends on cycle-precise timing — including all the multicolor demoscene effects — works identically on the +2.

This is **not true** of the +2A/+3, which replaced the Sinclair gate array with a new Amstrad ASIC that uses a different contention model (see [zx_spectrum_plus2a_plus3.md](zx_spectrum_plus2a_plus3.md) for details). The +2 is therefore the **last Spectrum with the original Sinclair contention model**.

### Heat Dissipation

The +2 runs slightly cooler than the 128K despite having the same internal electronics — Amstrad's case design provides better airflow, and the larger case acts as a more effective passive heatsink. The external heatsink is replaced by an **internal heatsink bolted to the 7805 regulator**, with the case's vent slots providing convection cooling. The +2 is still warm to the touch after extended use, but not as uncomfortable as the 128K.

---

## Keyboard

The +2's most distinctive feature is its **64-key full-travel keyboard**. The keys are single-piece keycaps with a smooth action — significantly better than the 48K's rubber mat and the 128K's flat chiclet keys, though not up to the standards of the BBC Micro or the IBM PC AT.

### Layout

The keyboard is laid out in a **compressed QWERTY arrangement** with the cursor keys embedded in the main grid:

- Top row: digits 1–0, with symbols accessible via SYMBOL SHIFT
- Function area: CAPS SHIFT, SYMBOL SHIFT, SPACE (enlarged)
- **Cursor keys** embedded in the right side of the main grid: caps 5/6/7/8 doubled as cursor left/right/down/up when used with CAPS SHIFT
- **EDIT, DELETE, GRAPH, TRUE VIDEO, INV VIDEO** keys on the right side, dedicated keys for these functions (previously SYMBOL SHIFT combinations on the 48K)
- **BREAK** is a dedicated key (previously CAPS SHIFT + SPACE on the 48K)
- **Keypad emulation**: the +2 has no separate numeric keypad, but provides keypad functionality via SYMBOL SHIFT + digits — this is how 128K software that expects keypad input (such as the 128K editor ROM's spreadsheet-like features) is operated on the +2

### Keyboard Matrix

The +2's keyboard matrix is **different from the 48K's 8×5 matrix**. It uses an **8×8 matrix** (8 row lines from the address bus, 8 column reads instead of 5), which allows for the additional keys. The matrix is scanned via the same `#FE` port, but with slightly different decoding for the extra column bits.

The keypad scan via the AY's I/O port (register 14) is **still present** on the +2 — the firmware retains the keypad-reading code from the 128K — but with no physical keypad attached, the reads always return #FF (no keys pressed). Software that explicitly reads the AY keypad port will work but will never see any input.

For the matrix layout details, see [keyboard_matrix.md](keyboard_matrix.md).

### Keyboard Quality

The +2 keyboard's main weakness is the **membrane underneath the keycaps**. The membrane is essentially the same technology as the 48K's — a flexible printed circuit with carbon contacts — and degrades over time. After 30+ years, many +2 keyboards have keys that fail to register or register phantom presses. Replacement membranes are available from retro-computing suppliers.

---

## Differences from the 128K

### Removed Features

| Feature | 128K | +2 |
|---|---|---|
| **Numeric keypad** | 20-key dedicated keypad on the right side | Removed (emulated via SYMBOL SHIFT + digits) |
| **RS-232 port** | Built-in, MC1488/MC1489 line drivers | Removed (no equivalent) |
| **MIDI port** | Built-in, shared with RS-232 circuitry | Removed (no equivalent) |
| **External heatsink** | Bolted to the rear of the case | Internal heatsink with vent slots |
| **Sinclair "toastrack" case** | Rick Dickinson design | New Amstrad BBC-Micro-style case |

### Added Features

| Feature | 128K | +2 |
|---|---|---|
| **Full-travel keyboard** | 65-key chiclet + 20-key keypad | 64-key full-travel typewriter keyboard |
| **Larger case** | 325 × 175 × 32 mm | 410 × 220 × 55 mm |
| **Tape-loading sound cue** | None | ROM plays a tone when tape loading starts/succeeds (firmware feature) |
| **Integrated speaker** | Internal speaker (small) | Larger internal speaker (better audio quality) |

### Unchanged Internals

These are **identical** between the 128K and the +2 — software that depends on these features works the same on both:

- CPU clock (3.504690 MHz)
- Frame timing (228 T-states/scanline × 311 lines = 70,932 T-states = 49.89 Hz)
- Memory banking via `#7FFD` (bank layout, ROM select, shadow screen, paging disable bit)
- Memory contention model (per-bank, banks 1/3/5/7 contended, delay pattern `(6,5,4,3,2,1,0,0)` — same pattern as 48K)
- AY-3-8912 sound chip at ports `#FFFD`/`#BFFD`, PSG clock 1.7734 MHz
- Beeper at port `#FE` bit 4
- Keyboard matrix port `#FE` (same decoding as 128K, despite the extra physical keys)
- Floating bus behavior (same as 128K)
- ROM contents (the same 32 KB dual-bank ROM image, with minor firmware revisions for the new keyboard layout)
- Edge connector pinout (same as 48K/128K)
- Power supply input (9V DC, though the +2's required current is slightly lower than the 128K's due to the removed RS-232 circuitry)

---

## Case and Connectors

The +2 case is a **two-tone grey slab** measuring approximately 410 mm × 220 mm × 55 mm. The bottom half is dark grey, the top half (with the keyboard) is light grey. The styling is distinctly different from any Sinclair-designed Spectrum — it looks more like Amstrad's CPC 464 or the BBC Master, with a flat top suitable for placing a small CRT monitor on.

### Rear Panel Connectors

The +2's rear panel has the following connectors (left to right):

1. **Power input** — 9V DC, 2.1 mm barrel jack (center-positive)
2. **TV RF output** — UHF PAL, channel 36
3. **RGB video output** — 8-pin DIN (different pinout from the 128K's RGB)
4. **Monochrome video output** — phono (RCA) jack
5. **EAR input** — 3.5 mm jack (tape input)
6. **MIC output** — 3.5 mm jack (tape output, also used for the AY audio)
7. **RS-232** — **not fitted** (the case has a blanking plate where the connector would go; the PCB has the pads but no components)
8. **MIDI** — **not fitted** (same as RS-232)
9. **Keypad** — **not fitted** (the case has a blanking plate)
10. **Expansion edge connector** — 2×28-way PCB edge connector (same as 48K/128K)
11. **Joystick port** — 9-pin D-sub (Kempston-compatible if an appropriate interface is connected; the +2 does not have a built-in joystick port, but the case has a cutout that was sometimes populated with a Kempston interface daughter-board)

> [!WARNING]
> The +2's **RGB pinout is different from the 128K's RGB pinout**. The 128K's 8-pin DIN carries composite sync on pin 1; the +2's 8-pin DIN carries separate HSYNC on pin 1 and VSYNC on pin 2. Using a 128K monitor cable on a +2 will not work without an adapter. See [pinouts.md](../../10_references/pinouts.md) for both pinouts.

### Reset Button

The +2 has a **reset button on the left side of the case**, recessed to prevent accidental presses. Pressing reset is equivalent to power-cycling the machine — it reinitialises the CPU, the paging register, and the ROM. The reset button is useful for software that does not provide a clean exit, and is essential when working with hardware that disables the paging register (bit 7 of `#7FFD`).

---

## Video Output

The +2's video outputs are the same as the 128K in capability (RGB, composite, RF), but with the different RGB connector pinout noted above. The composite video quality is slightly better than the 128K's due to improved video amplifier circuitry on the +2's PCB.

### Frame Timing

The +2's video frame is **identical to the 128K's**: 311 scanlines × 228 T-states = 70,932 T-states at 3.504690 MHz = 49.89 Hz. Software written for 128K timing works without modification on the +2.

For the full frame timing reference, see [video_frame_128k.md](../../05_development/05_display_and_timing/video_frame_128k.md) — the +2's timing matches the 128K exactly.

---

## Comparison Across Spectrum Models

| Feature | 48K | 128K | **+2 (grey)** | +2A / +3 |
|---|---|---|---|---|
| **Manufacturer** | Sinclair | Sinclair | **Amstrad** | Amstrad |
| **Launch** | April 1982 | Sept 1985 | **Aug 1986** | December 1987 |
| **Price at launch** | £175 | £179.95 | **£149.99** | £149.99 (+2A) / £199.99 (+3) |
| **RAM** | 48 KB | 128 KB | **128 KB** | 128 KB |
| **Sound** | Beeper | AY + Beeper | **AY + Beeper** | AY + Beeper |
| **Keyboard** | 40-key rubber | 65-key + 20-key keypad | **64-key full-travel** | 64-key full-travel |
| **Numeric keypad** | No | Yes (dedicated) | **No (emulated via SYMBOL+digit)** | No (emulated) |
| **RS-232 / MIDI** | No | Yes | **No** | No |
| **Disk drive** | No | No | **No** | +3: built-in 3" floppy; +2A: optional |
| **Paging register** | — | `#7FFD` | **`#7FFD`** | `#7FFD` + `#1FFD` |
| **Contention model** | per-address, 8-cycle | per-bank (1/3/5/7), 7-cycle | **per-bank (1/3/5/7), 7-cycle (same as 128K)** | per-bank (4/5/6/7), MREQ-gated |
| **Gate array** | Ferranti ULA | Sinclair 8K5/7K0 | **Sinclair 8K5/7K0 (same as 128K)** | Amstrad 40084/40085 |
| **Scanline** | 224 T-states | 228 T-states | **228 T-states** | 228 T-states |
| **External case color** | Beige | Beige | **Grey** | Black (+2A) / Black with disk drive (+3) |
| **Total production** | ~5 million | ~250,000 | **~1.5 million** | ~750,000 (+2A) + ~125,000 (+3) |

The +2 is the **pivotal model** in the Spectrum lineage — it is the bridge between the Sinclair-designed hardware (16K/48K/128K) and the Amstrad-ASIC hardware (+2A/+3). Software targeting the +2 runs on every later Spectrum (and most Russian clones), but software targeting the +2A/+3 does not always work on earlier machines due to the different contention model.

---

## Common Issues and Repairs

### Failed DRAM

Same as the 128K: the 16 DRAM chips (41464-family) run hot and have a high failure rate after 30+ years. Symptoms: random crashes, garbage on screen, failure to boot.

### Keyboard Membrane Failure

The +2's keyboard membrane is the **most common point of failure** on the +2 today. Symptoms: keys that fail to register, keys that register phantom presses, or complete keyboard failure. Replacement membranes are widely available.

### Failed Electrolytic Capacitors

The +2's PCB contains about a dozen electrolytic capacitors that dry out over 30+ years. Symptoms: instability, audio hum, video artefacts, or failure to boot. A full capacitor replacement ("recap") is recommended for any +2 that has not been serviced.

### Internal Speaker Failure

The +2's internal speaker is a small mylar-cone speaker driven by the audio amplifier. After decades, the mylar can tear or the amplifier IC can fail. Replacement speakers are available from retro-computing suppliers.

### Keyboard Ghosting

The +2's keyboard matrix does not have isolation diodes, so pressing three keys simultaneously can produce a "phantom" fourth key. This is the same limitation as the 48K's keyboard. For software that requires multiple simultaneous key presses (rare in Spectrum software, but common in flight simulators), a joystick is the standard workaround.

---

## Cross-References

- [zx_spectrum_128.md](zx_spectrum_128.md) — the predecessor: architecture, banking, contention, AY chip, keypad. The +2 is functionally identical to the 128K in all those respects.
- [zx_spectrum_plus2a_plus3.md](zx_spectrum_plus2a_plus3.md) — the successor with the new Amstrad ASIC, different contention model, and +3 disk drive
- [zx_spectrum_16k_48k.md](zx_spectrum_16k_48k.md) — the original 16K/48K architecture
- [ula_architecture.md](ula_architecture.md) — the Sinclair 8K5/7K0 gate array (used in both 128K and +2)
- [ula_timing.md](ula_timing.md) — frame timing and contention
- [keyboard_matrix.md](keyboard_matrix.md) — the +2's 8×8 keyboard matrix
- [memory_and_io_128k.md](../../05_development/03_memory_and_io/memory_and_io_128k.md) — the +2 uses the same memory map and ports as the 128K
- [contention_model.md](../../05_development/03_memory_and_io/contention_model.md) — contention model (the +2 uses the same per-bank model as the 128K)
- [video_frame_128k.md](../../05_development/05_display_and_timing/video_frame_128k.md) — the +2's video frame (same as the 128K's)
- [ay_ym_synthesis.md](../../06_sound/synthesis/ay_ym_synthesis.md) — the AY sound chip
- [rom_plus2.md](../../04_operating_systems/rom_plus2.md) — the +2's ROM internals (essentially the 128K's ROM with minor revisions)
- [rom_versions.md](../../04_operating_systems/rom_versions.md) — catalog of all Spectrum ROM versions and variants
- [pinouts.md](../../10_references/pinouts.md) — the +2's RGB connector pinout (different from the 128K's)

---

## References

- [Amstrad Consumer Electronics plc](https://www.worldofspectrum.org/hardware.html) — *ZX Spectrum +2 User Manual* (1986)
- **Amstrad PLC** — ZX Spectrum +2 launch press release (14 August 1986)
- [Crash magazine, Issue 33](https://archive.org/details/crash-magazine) — launch review of the +2
- [Your Sinclair magazine, Issue 13](https://archive.org/details/yoursinclair-magazine) — +2 review and benchmark
- [Sinclair User magazine, Issue 56](https://archive.org/details/sinclair-user-magazine) — +2 launch coverage
- **Alan Sugar** — *What You See Is What You Get* (autobiography, 2010) — accounts of the Amstrad acquisition of Sinclair and the +2 product strategy
- [World of Spectrum](https://worldofspectrum.org/) — hardware reference photos for the +2 grey
- **The Centre for Computing History** — +2 technical documentation
- [ZX Spectrum Service Manual](https://www.worldofspectrum.org/hardware.html)

---
