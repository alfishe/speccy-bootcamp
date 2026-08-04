[← Home](../../README.md) · [Original Hardware](README.md)

# ZX Spectrum 128K — The "Toast Rack": Sinclair's Last Spectrum

The **ZX Spectrum 128K** (codenamed *Darwin* during development, popularly known as the **"Toast Rack"** after its rectangular case with a raised rear section housing the heatsink) was launched in **September 1985 in Spain** and **February 1986 in the UK**. It was the **last ZX Spectrum designed by Sinclair Research** before the Amstrad acquisition in April 1986, and the first Spectrum to ship with **bank-switched memory, an AY-3-8912 sound chip, a keypad, and 32 KB of ROM split across two switchable banks**.

The 128K was the result of a joint development effort between Sinclair Research and **Investrónica**, the Spanish distributor of Sinclair products, which had identified the Spanish market's strong demand for a more capable Spectrum — particularly for the educational sector and for the growing Spanish demoscene. The Spanish launch preceded the UK launch by five months because Investrónica had effectively forced Sinclair's hand: the Spanish version was firmware-finalized first, and the UK release had to wait for localisation and the Sinclair/Amstrad transition.

Although superseded within a year by the Amstrad-branded +2, the 128K is **architecturally the bridge** between the original Sinclair design philosophy and the Amstrad era. Its core decisions — the `#7FFD` paging register layout, the bank numbering scheme, the dual-ROM switching, the AY chip at ports `#FFFD`/`#BFFD`, the keypad scanning via the AY's I/O port — were inherited unchanged by every later Spectrum model and by every Soviet/Russian clone. Understanding the 128K is therefore a prerequisite for understanding the +2, +2A, +3, Pentagon, Scorpion, and ATM Turbo.

> [!NOTE]
> This article covers the 128K as a **system**: history, board variants, bill of materials, memory banking, sound, keypad, ports, video timing, and physical packaging. For the **internal architecture of the 8K5/7K0 gate array** (the 128K's ULA replacement), see [ULA Architecture](ula_architecture.md). For **frame timing and contention**, see [contention_timing.md](../../05_development/05_display_and_timing/contention_timing.md). For the **programmer-facing view of memory and ports**, see [128K Memory & I/O](../../05_development/03_memory_and_io/memory_and_io_128k.md).

---

## History

### Spanish Origin and the Investrónica Partnership

In 1984–1985, the Spanish home computer market was the **second-largest in Europe** after the UK, with Investrónica (the electronics division of the Spanish department-store chain El Corte Inglés) holding exclusive distribution rights for Sinclair products. The Spanish Spectrum user base had grown frustrated with the limitations of the 48K — particularly the lack of sound (the beeper was widely considered inadequate for music), the limited RAM for Spanish-localised business software, and the absence of a built-in keypad for data entry.

Investrónica approached Sinclair Research in late 1984 with a proposal: a new Spectrum model with 128 KB of RAM, an AY-3-8912 sound chip, an RS-232 serial port, and an enhanced keyboard. The development was code-named **Darwin** and was largely completed by mid-1985. The Spanish launch as the **ZX Spectrum 128K (versión española)** took place at the **SIMO'85** computer trade show in Madrid (November 1985, with retail availability from late September). The UK launch followed at the **Which Computer? Show** in January 1986, with retail availability from February 1986 at **£179.95**.

### The Amstrad Acquisition (April 1986)

Sinclair Research had been losing money throughout 1985 due to the failure of the Sinclair QL and the Wrist TV/Pocket TV products, accumulated debts, and intense price competition. In **April 1986**, Clive Sinclair sold the rights to all Sinclair computer products and the "Sinclair" brand name in the computer market to **Amstrad** for **£5 million**. The 128K was the last Sinclair product on sale when the sale completed, and Amstrad continued to manufacture and sell it alongside the newly-launched +2 (August 1986) for about a year.

### Why It Matters

The 128K introduced four features that defined the rest of the Spectrum lineage:

| Feature | Significance |
|---|---|
| **128 KB RAM bank-switched via `#7FFD`** | The paging layout (3-bit bank number, ROM select, shadow screen) was inherited by every later Sinclair model and by every clone. Soviet clones copied it verbatim. |
| **AY-3-8912 sound chip** | Standardised Spectrum music. Every later model, every Russian clone, and the modern demoscene's `.pt3`/`.ay` file formats are direct descendants. |
| **32 KB ROM (two switchable 16 KB banks)** | Bank 0: 128K editor + 48K BASIC API; Bank 1: the original 48K ROM. The "48K mode" accessed by `USR 0` and the ROM-disabling bit are 128K inventions. |
| **228 T-states/scanline frame (vs 224 on 48K)** | The +2, +2A, +3, Pentagon, Scorpion, and ATM Turbo all use the 228-T-state scanline. The 4 extra T-states per scanline absorbed the bank-decode logic needed for the bank-switched 128 KB memory map (the 48K's ULA fetches from a fixed bank, the 128K's ULA must look up the active screen bank on each access). |

---

## Board Variants

The 128K was produced in two major **PCB revisions** identifiable by the issue number silkscreened on the board:

| Issue | Region | Notes |
|---|---|---|
| **Issue 1** | Spain (Sept 1985) | First production run, sold in Spain only. Uses a small heatsink on the 7805 regulator. |
| **Issue 1 (UK)** | UK (Feb 1986) | Same PCB, different firmware language default and keypad layout label. |
| **Issue 2** | UK + Spain (mid-1986) | Minor routing fixes; more reliable RAM; larger heatsink. |
| **Issue 3** | UK + Spain (late 1986) | Last Sinclair-designed board before +2 production took over. Rare. |

All issues share the same gate array (ULA), the same AY-3-8912, the same RS-232/MIDI interface circuitry, and the same memory timing. Differences are in PCB routing, component placement, and regulator heat dissipation.

### Regional Variants

- **ZX Spectrum 128K (versión española)** — Spanish firmware default, Spanish keypad labels, distributed by Investrónica
- **ZX Spectrum +128K** — UK firmware default (English), UK keypad labels, distributed by Sinclair Research then Amstrad
- **ZX Spectrum 128** — Heavily rebranded for some continental European markets, with localized firmware

The Spanish firmware has a slightly different 48K BASIC bank (bank 1) — keyword tokens and error messages are localised.

---

## Bill of Materials

A 128K board contains a surprisingly small number of ICs, but the IC count is higher than the 48K because of the extra paging logic, the AY sound chip, and the RS-232/MIDI drivers.

| IC | Function | Quantity | Package | Notes |
|---|---|---|---|---|
| **Z8400AB1** (Zilog Z80A) | CPU | 1 | 40-pin DIP | NMOS, 3.5 MHz, 4 MHz rated |
| **Sinclair 8K5 / 7K0 gate array** | ULA — video, banking, contention, keyboard | 1 | 48-pin QFP | Sinclair custom chip, not Ferranti. Two part numbers exist; both pin-compatible. |
| **AY-3-8912** | Sound chip + I/O port | 1 | 28-pin DIP | GI / Microchip; same chip used in 128K/+2/+2A/+3 |
| **ROM** (32 KB) | Two 16 KB banks, switchable | 1 | 28-pin DIP | Mask ROM, type 23256 or equivalent |
| **8464 / 41464 / HM4864** (DRAM) | 64 Kbit × 4-bit, 4 chips for one 16 KB bank × 8 banks = 128 KB total | 16 | 16-pin DIP | Lower-power than 4164; runs cooler than the 48K's 4532/4116 |
| **74HCT family** (various) | Address decoding, banking latch, glue logic | ~6 | 14- and 16-pin DIP | Common: 74LS00, 74LS02, 74LS04, 74LS08, 74LS32, 74LS139, 74LS273 |
| **MC1488 / MC1489** | RS-232 line drivers / receivers | 2 each | 14-pin DIP | Standard RS-232 level-shift ICs |
| **LM1889** | PAL video modulator | 1 | 16-pin DIP | Same as 48K for RF output to TV |
| **7805** | +5V linear regulator | 1 | TO-3 or TO-220 | Heatsink required; the 128K runs hotter than the 48K due to extra chips |
| **Transistors** | Audio output amplifier, tape interface | ~4 | TO-92 | |
| **Diodes** | Various, including RESET and EAR/MIC clamping | ~6 | DO-35 | |
| **Resonator** | 1.7734 MHz clock source for AY-3-8912 | 1 | 3-pin | Half the CPU clock |

### The Gate Array (Sinclair 8K5 / 7K0)

The 128K's ULA — unlike the 48K's **Ferranti** ULA — was manufactured by **Sinclair Research itself** using a different foundry. The Sinclair 8K5 (in early issues) and 7K0 (in later issues) are pin-compatible gate arrays in a 48-pin QFP package. The chip integrates:

- **Video generation** (pixel/attribute fetch, color encoder, BORDER register, composite sync generator)
- **DRAM arbitration** (bank-specific contention, see [contention model](#memory-contention-on-the-128k) below)
- **The `#FE` output port** (border color, MIC output, EAR output, beeper)
- **The `#FE` input port** (keyboard row scan)
- **The `#7FFD` paging register** (bank number, ROM select, shadow screen select)
- **Memory decoding logic** (which bank is active where in the address space)
- **Tape signal mixing**

For more detail on what the gate array does internally, see [ULA Architecture](ula_architecture.md).

### Heat Dissipation

The 128K runs noticeably hotter than the 48K due to:
- 16 DRAM chips instead of 8 (or 16 on the 48K, but the 128K uses smaller, hotter-running packages)
- The AY-3-8912 sound chip (which dissipates ~500 mW)
- The RS-232 driver ICs (MC1488 alone can dissipate ~1 W when driving a load)
- A more complex gate array

This is why the 128K case has a large external heatsink bolted to the rear of the case — the 7805 regulator and the gate array both dissipate into it. The 128K is the **hottest-running Spectrum of the entire Sinclair/Amstrad lineage**.

---

## Memory Banking (the `#7FFD` Paging Register)

The 128K's defining feature is **bank-switched memory**: 128 KB of RAM is presented to the Z80 in 8 banks of 16 KB each, with one bank at a time visible at the top of the address space (`#C000`–`#FFFF`). The bank selection is controlled by a single write-only port at `#7FFD`:

```
OUT (#7FFD), A — 128K paging register (write-only)

  Bit   7  6  5  4  3  2  1  0
      ┌────┬────┬────┬────┬────┬────┬────┬────┐
      │DIS │ x  │ x  │ROM │SCR │B2  │B1  │B0  │
      └────┴────┴────┴────┴────┴────┴────┴────┘

  Bits 0–2 (B0–B2): RAM bank to page into #C000–#FFFF (0–7)
  Bit  3    (SCR):   Screen select (0 = bank 5, 1 = bank 7 shadow)
  Bit  4    (ROM):   ROM select (0 = 128K editor ROM, 1 = 48K BASIC ROM)
  Bit  5:            Unused
  Bit  6:            Unused
  Bit  7    (DIS):   Disable further writes to #7FFD (see below)
```

The memory map as seen by the CPU is:

```
#0000–#3FFF   ROM bank 0 (128K editor) OR ROM bank 1 (48K BASIC)
#4000–#7FFF   RAM bank 5 (fixed, contains the visible screen)
#8000–#BFFF   RAM bank 2 (fixed, general-purpose RAM)
#C000–#FFFF   RAM bank 0–7 (switchable via bits 0–2 of #7FFD)
```

Banks **5 and 2 are always fixed** in their positions. Only the bank at `#C000` can be switched — but this is enough to give software access to all 128 KB by cycling banks through that 16 KB window.

### The Shadow Screen (Bank 7)

Bit 3 of `#7FFD` selects which bank the ULA fetches pixels from: **0 = bank 5** (the default visible screen at `#4000`–`#7FFF`), **1 = bank 7**. This is independent of where bank 7 is currently paged from the CPU's perspective.

The shadow screen is the 128K's **double-buffering** primitive: software can build the next frame in bank 7 while the ULA is still displaying bank 5, then flip the bit to switch display instantly at the next vertical blank. This eliminates the tearing that plagues 48K software that tries to update the screen in-place during the border period.

### The Paging Disable Bit (Bit 7)

Writing **1 to bit 7 of `#7FFD`** makes the paging register **read-only** until the next machine reset. The intent was to protect 48K software from accidentally corrupting its own memory map — once a 48K program is running, it should not be able to page in the wrong bank and crash the system.

Once bit 7 is set, no further writes to `#7FFD` have any effect. The paging configuration is frozen until power-cycle or reset. This feature is rarely used by 128K-native software (which needs to keep switching banks), but it is essential for running 48K software safely: the 128K's ROM sets bit 7 on entry to 48K mode.

### The ROM Select Bit (Bit 4)

Bit 4 of `#7FFD` switches between the two 16 KB ROM banks:
- **0 = ROM bank 0** (the 128K editor ROM with extended BASIC, the editor with keypad, the calculator with new functions, and the 48K BASIC APIs)
- **1 = ROM bank 1** (the original 48K ROM, byte-for-byte identical to the 16 KB ROM in the 48K Spectrum)

The 128K editor ROM provides the **`USR 0`** entry point that flips to ROM bank 1 and disables paging — this is how 48K mode is entered on the 128K.

---

## Memory Contention on the 128K

The 128K's contention model is **fundamentally different from the 48K's**:

- **48K**: any access to `#4000`–`#7FFF` may be delayed by the ULA's video fetches. The delay pattern is `(6,5,4,3,2,1,0,0)` repeated every 8 T-states.
- **128K**: contention is **per-bank, not per-address**. The ULA contends only the banks that share DRAM with the screen: **banks 1, 3, 5, 7** (the odd-numbered banks). Banks 0, 2, 4, 6 are never contended.

The implication: code running from bank 3 paged at `#C000` is contended, even though `#C000` is outside the screen area. Conversely, code in bank 0 (also at `#C000`) is not contended. This is the **most common source of timing bugs when porting 48K software to the 128K**: a tight loop that runs in `#C000` works fine in 48K mode (which uses the 48K ROM bank 1 and the original contention), but stalls unpredictably when banked into a contended bank on the 128K.

The 128K's contention timing is also different from the 48K's:

| Parameter | 48K | 128K / +2 |
|---|---|---|
| **Scanline length** | 224 T-states | 228 T-states |
| **Contention pattern length** | 8 T-states | 8 T-states (same pattern, different contended banks) |
| **Delay pattern** | `(6,5,4,3,2,1,0,0)` | `(6,5,4,3,2,1,0,0)` (same as 48K) |
| **Pattern starts at T-state** | 14335 | 14361 |
| **Contention scanline range** | 64–255 | 63–254 |
| **Frame length** | 69,888 T-states (312 lines × 224) | 70,932 T-states (311 lines × 228) |
| **Frame rate** | 50.08 Hz | 49.89 Hz |

The 228-T-state scanline (vs the 48K's 224) exists because the 128K's gate array performs **bank-aware addressing** during video fetch — it has to look up the bank number for each fetch, since the visible screen can be in bank 5 or bank 7 (selected by `#7FFD` bit 3). The 4 extra T-states per scanline absorb this extra decoding work. The contention pattern itself (the `(6,5,4,3,2,1,0,0)` delay table) is identical to the 48K's.

For the programmer-facing view of contention with T-state tables, see [contention_model.md](../../05_development/03_memory_and_io/contention_model.md) and [contention_timing.md](../../05_development/05_display_and_timing/contention_timing.md).

---

## The AY-3-8912 Sound Chip

The 128K is the **first Spectrum with a real sound chip** — the General Instrument **AY-3-8912**. This is a 3-voice programmable sound generator (PSG) with:

- **Three tone channels** (A, B, C), each with 12-bit frequency resolution
- **One noise channel** (5-bit resolution, shared across all three channels)
- **One envelope generator** (16-bit period, 4-bit shape selecting from 16 attack/decay/sustain/release patterns)
- **Three 4-bit logarithmic DACs** (one per channel)
- **One 8-bit I/O port** (used on the 128K to scan the auxiliary keypad)

The AY-3-8912 is a 28-pin variant of the AY-3-8910 (40-pin, two I/O ports) and AY-3-8913 (24-pin, no I/O ports). The 8912 was chosen because it offers one I/O port (enough for the keypad) in a smaller package.

### AY I/O Ports

The AY is accessed via two I/O ports on the Z80:

- **`#FFFD`** — Function select (write selects which AY register is active, read returns the value of the currently selected register)
- **`#BFFD`** — Data register (write updates the active register with the written value)

All 16 AY registers are accessed through this two-step protocol: write the register number to `#FFFD`, then write or read data via `#BFFFD`.

### PSG Clock

The AY-3-8912 on the 128K runs at **1.7734 MHz** — half the Z80 clock of 3.5469 MHz. This is the same clock used on the +2, +2A, +3, and (with slight variation) on the Pentagon. The exact PSG clock matters because it determines the tuning of all music written for the platform.

> [!NOTE]
> The Pentagon clone uses a PSG clock of **1.75 MHz** instead of 1.7734 MHz — about 1.3% slower. Music written for the 128K plays very slightly flat on the Pentagon (and vice versa). The modern demoscene's `.pt3` tracker format bakes in a PSG clock assumption, which is why Pentagon-targeted modules sound wrong on real 128K Spectrums unless the player compensates.

### Audio Output Path

The AY's three analog audio outputs are summed together with the Spectrum's traditional **1-bit beeper** (still present at port `#FE` bit 4) and routed to the same audio amplifier that drives the 48K's internal speaker and the EAR/MIC jacks. This means:

- The beeper and the AY can play simultaneously, mixed analog
- The beeper is effectively **deprecated** on the 128K for new software, but kept for 48K backward compatibility
- Connecting headphones or an amplifier to the EAR jack picks up both the beeper and the AY audio

For a deeper look at the AY-3-8912 architecture, register set, and use in Spectrum music, see [ay_ym_synthesis.md](../../06_sound/synthesis/ay_ym_synthesis.md).

---

## The Auxiliary Keypad

The 128K case adds a **20-key numeric keypad** to the right of the main QWERTY keyboard. The keypad contains:

- Digits 0–9
- Four arithmetic operators (+, -, *, /)
- Decimal point (.)
- ENTER
- DELETE
- CAPS SHIFT and SYMBOL SHIFT duplicates
- A blank function key (often labeled EDIT or used as a custom function)

The keypad is **scanned via the AY-3-8912's I/O port** (register 14, the 8912's only bidirectional 8-bit port) rather than via the main keyboard matrix. This is why the keypad does not work on the 48K — the AY chip is not present.

### Reading the Keypad

To read the keypad:

1. Write `14` to `#FFFD` (select AY register 14)
2. Write a row-select pattern to `#BFFD` (sets which keypad row is being scanned, pulls certain columns low)
3. Read from `#FFFD` (returns the column states)

The full keypad scan requires cycling through several row-select patterns and reading the column state each time. The ROM's keyboard-scanning routine handles this automatically — user software rarely needs to access the keypad directly.

### Why a Keypad?

The keypad was a **Spanish-market requirement**. Spanish business and education users were accustomed to numeric keypads on CP/M systems and PC compatibles, and considered the 48K's lack of one a serious usability flaw for spreadsheet-style applications. The keypad's inclusion on the 128K was a direct response to Investrónica's market research.

The keypad did not survive the transition to the +2 — Amstrad removed it to fit the larger typewriter-style keyboard into the +2's BBC-Micro-style case.

---

## RS-232 and MIDI Ports

The 128K is the **only Spectrum to ship with built-in RS-232 and MIDI ports**. These are not separate serial chips — they are driven by the Z80 directly via a small interface circuit:

- **RS-232 output**: the Z80 writes serial data bit-by-bit to a port, with the MC1488 line driver converting TTL levels to ±12V RS-232 levels. The Z80 must time the bit transitions in software (bit-banging).
- **RS-232 input**: an MC1489 receiver converts RS-232 levels to TTL, which the Z80 reads bit-by-bit via a port read.
- **MIDI output**: shares the RS-232 output circuit at a different baud rate (MIDI runs at 31,250 baud, RS-232 typically at 9,600 baud).

The ports are at I/O addresses `#FFFD` (data) and `#FBFD` (control/status), shared with the AY chip's port addressing — the firmware distinguishes them via the address-low-byte decoding.

These ports were **rarely used** in commercial Spectrum software. They exist primarily to qualify the 128K as a "business computer" for the Spanish educational market, which had strict I/O requirements for funding eligibility.

---

## Case and Physical Packaging

The 128K's industrial design is by **Rick Dickinson** (the same designer who did the ZX81, the original 48K Spectrum, and the Spectrum+). The case is a **flat rectangular slab** (approximately 325 mm × 175 mm × 32 mm) with a raised rear section (the "toaster slot" that gives the machine its nickname) housing the **external heatsink** and the regulator circuitry.

Design features:

- **Hard plastic case** in Sinclair's characteristic light-grey/beige color (not the rubber-feel of the 48K)
- **Integrated full-travel keyboard** with 65 keys (a refinement over the 48K rubber keyboard, but still not full typewriter quality)
- **20-key numeric keypad** on the right side, separate from the main keyboard
- **Large external heatsink** bolted to the rear of the case — the most recognisable visual feature
- **All connectors on the rear**: RGB monitor, monochrome monitor, TV RF, EAR, MIC, RS-232, MIDI, expansion edge connector, power input
- **Reset button** on the left side (recessed to prevent accidental presses)

The 128K's case design is often described as **the most elegant of the Sinclair Spectrums**, though its thermal management (with a heatsink literally bolted to the outside) was widely mocked at the time.

### The Heatsink Issue

The 128K runs noticeably hotter than the 48K (see [Heat Dissipation](#heat-dissipation) above). The external heatsink was a **pragmatic engineering decision**: rather than redesign the regulator circuitry to dissipate less heat, Sinclair's engineers chose to bolt the existing 7805 regulator to the case and let the entire rear of the machine act as a heatsink. This works — the 128K is thermally stable — but it makes the case warm to the touch after extended use, and the heatsink fins can be uncomfortable if the machine is on the user's lap.

---

## Video Output

The 128K provides **three video outputs**, all on the rear panel:

| Output | Connector | Signal |
|---|---|---|
| **RGB video** | 8-pin DIN | RGB analog (TTL-level RGBI + composite sync), 50 Hz vertical refresh, intended for the Sinclair TM1620 monitor or any compatible RGB monitor |
| **Monochrome composite** | phono (RCA) jack | Composite video, 50 Hz, suitable for a monochrome monitor or any TV with a composite input |
| **RF (UHF)** | Coaxial | PAL-modulated UHF on channel 36 (UK) or channel 27 (Spain, different RF modulator) |

The RGB output is **the recommended video connection** for the 128K — it provides the sharpest picture and supports color without the artefacts of composite encoding. The +2 and later models kept the same RGB pinout.

> [!WARNING]
> The 128K's RGB pinout is **not the same as the later +2/+2A/+3 pinout**. The 128K uses 8-pin DIN with composite sync on one pin; the +2 uses 8-pin DIN with separate HSYNC/VSYNC. Adapters are needed to use a 128K monitor cable on a +2, or vice versa. See [pinouts.md](../../10_references/pinouts.md) for the exact wiring of both.

### Frame Timing

The 128K's video frame is **311 scanlines × 228 T-states/scanline = 70,932 T-states**, running at the Z80 clock of 3.504690 MHz, which gives a frame rate of **49.89 Hz**. This is slightly slower than the 48K's 50.08 Hz — a difference that is just perceptible to a trained eye in side-by-side comparison but is rarely noticeable in normal use.

The active display area is 256×192 pixels, the same as the 48K, with the same attribute-cell constraint (8×8 pixels per attribute cell, two colors per cell). The 128K does **not** add any new video modes — it uses the same display layout as the 48K, with the only innovation being the bank-7 shadow screen for double-buffering.

For a complete reference of the 128K's frame timing, see [video_frame_128k.md](../../05_development/05_display_and_timing/video_frame_128k.md).

---

## Comparison to Other Models

| Feature | 48K | **128K** | +2 (grey) | +2A / +3 |
|---|---|---|---|---|
| **Manufacturer** | Sinclair | **Sinclair** | Amstrad | Amstrad |
| **Launch** | April 1982 | **Sept 1985 / Feb 1986** | August 1986 | December 1987 |
| **RAM** | 16/48 KB | **128 KB** | 128 KB | 128 KB |
| **ROM** | 16 KB | **32 KB (2 banks)** | 32 KB (2 banks) | 64 KB (2 banks) |
| **Sound** | Beeper | **AY-3-8912 + Beeper** | AY-3-8912 + Beeper | AY-3-8912 + Beeper |
| **Keyboard** | 40-key rubber | **65-key + 20-key keypad** | 64-key full-travel | 64-key full-travel |
| **RS-232 / MIDI** | No | **Yes** | No (removed) | No |
| **Disk support** | No | No (but Beta 128 interface popular) | No | +3 has built-in 3" floppy |
| **Paging port** | — | **`#7FFD`** | `#7FFD` | `#7FFD` + `#1FFD` |
| **Scanline length** | 224 T-states | **228 T-states** | 228 T-states | 228 T-states |
| **Frame rate** | 50.08 Hz | **49.89 Hz** | 49.89 Hz | 49.89 Hz |
| **Contention model** | 8-cycle pattern | **per-bank (1,3,5,7 contended)** | per-bank (1,3,5,7) | per-bank (4,5,6,7), MREQ-gated |
| **Power** | 9V DC @ 1.2A | **9V DC @ 2.0A** | 9V DC @ 2.0A | 9V DC @ 1.5A |
| **Case design** | Rubber-key slab | **"Toast Rack" with heatsink** | Grey BBC-style slab | Black +2A / black +3 with disk drive |

---

## Common Issues and Repairs

### Failed DRAM (Most Common)

The 128K's 16 DRAM chips (41464-family) run hot and have a high failure rate after 30+ years. Symptoms: random crashes, garbage on screen, failure to boot. The DRAM chips can be replaced individually, but identifying the failed chip requires a diagnostic ROM or oscilloscope probing.

### Failed Gate Array

The Sinclair 8K5/7K0 gate array is a custom chip with no modern drop-in replacement. Failures are terminal unless a working donor chip can be found from another 128K. The Harlequin and Sizif-512 FPGA recreations are modern replacements that can fit the original case (covered in the Soviet clone and FPGA articles).

### Failed AY-3-8912

The AY chip is replaceable with a new-old-stock AY-3-8912 or a Yamaha YM2149 (pin-compatible clone with slightly improved DACs). See [ay_vs_ym.md](../../06_sound/synthesis/ay_vs_ym.md) for compatibility notes.

### Heat Damage

The 128K's external heatsink exists because the regulator runs hot. After decades, the heatsink compound between the regulator and the case can dry out, leading to thermal shutdown or damage to nearby capacitors. Replacing the thermal compound and checking the regulator output (should be 5.0V ± 0.1V) is recommended during any service.

### Keyboard Membrane

The 128K's integrated keyboard uses a membrane that degrades over time. Replacement membranes are available from retro-computing suppliers; the membrane is **not compatible** with the 48K or the +2.

---

## Cross-References

- [zx_spectrum_16k_48k.md](zx_spectrum_16k_48k.md) — the predecessor: 16K/48K architecture, ULA, board issues
- [zx_spectrum_plus2.md](zx_spectrum_plus2.md) — the Amstrad successor: same internals, new case, no keypad
- [zx_spectrum_plus2a_plus3.md](zx_spectrum_plus2a_plus3.md) — the Amstrad ASIC redesign with different contention model and disk support
- [ula_architecture.md](ula_architecture.md) — the 8K5/7K0 gate array internals
- [ula_timing.md](ula_timing.md) — frame timing and contention, including the 128K's 228-T-state scanline
- [keyboard_matrix.md](keyboard_matrix.md) — the main 8×5 keyboard matrix (the 128K adds the keypad via AY)
- [memory_and_io_128k.md](../../05_development/03_memory_and_io/memory_and_io_128k.md) — programmer-facing view of memory and ports
- [contention_model.md](../../05_development/03_memory_and_io/contention_model.md) — detailed contention model across all models
- [contention_timing.md](../../05_development/05_display_and_timing/contention_timing.md) — T-state-precise contention tables
- [video_frame_128k.md](../../05_development/05_display_and_timing/video_frame_128k.md) — the 128K's video frame structure
- [floating_bus.md](../../05_development/05_display_and_timing/floating_bus.md) — the floating bus behavior on the 128K
- [ay_ym_synthesis.md](../../06_sound/synthesis/ay_ym_synthesis.md) — the AY sound chip's register-level reference and synthesis techniques
- [ay_vs_ym.md](../../06_sound/synthesis/ay_vs_ym.md) — AY-3-8912 vs Yamaha YM2149 differences and replacement considerations
- [rom_128k.md](../../04_operating_systems/rom_128k.md) — the 128K's two-bank ROM internals
- [rom_versions.md](../../04_operating_systems/rom_versions.md) — catalog of all Spectrum ROM versions and variants
- [pinouts.md](../../10_references/pinouts.md) — connector pinouts for RGB, RS-232, and MIDI
- [pentagon.md](../clones/pentagon.md) — the Soviet clone based on the 128K architecture

---

## References

- [Sinclair Research Ltd.](https://www.worldofspectrum.org/hardware.html) — *ZX Spectrum 128K User Manual* (1986)
- [Investrónica / Sinclair Research](https://www.worldofspectrum.org/hardware.html) — *ZX Spectrum 128K (versión española) Manual* (1985)
- **Andrew Owen** — Sinclair ZX Spectrum 128K Technical Information (Sinclair Wiki)
- [World of Spectrum](https://worldofspectrum.org/) — hardware documentation and reference photos
- [Chris Smith](http://www.zxdesign.info/) — *The ZX Spectrum ULA: How to Design a Microcomputer* (2010) — although focused on the 48K ULA, the 128K gate array differences are documented in appendices
- [ZX Spectrum Service Manual](https://www.worldofspectrum.org/hardware.html) — board schematics for issues 1, 2, and 3
- [Crash magazine, Issue 26](https://archive.org/details/crash-magazine) — launch coverage of the UK 128K release
- **Microhobby magazine** (Spanish, 1985–1986) — extensive coverage of the Spanish launch and software library
- **The History of the ZX Spectrum** — various sources including the Centre for Computing History and the Science Museum archive
- **Amstrad PLC** — acquisition press release (April 1986)

---
