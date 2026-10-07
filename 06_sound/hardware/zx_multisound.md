[← Home](../../README.md) · [Sound Hardware](README.md)

# ZX-MultiSound — Five Sound Engines on One NemoBus Card

> **Applies to**: **Soviet / New Gen** — ZX-MultiSound rev.A/A1/A2 by Eugene Lozovoy (`UzixLS`), a NemoBus/ZX-bus expansion card for Pentagon-class machines and the ZX Evolution. This article is a hardware reference; for the individual engines see the linked component articles.

Most ZX sound cards pick one idea: a second AY ([TurboSound](turbosound.md)), FM synthesis ([TurboSound FM](turbosound_fm.md)), a sample-playing coprocessor ([General Sound](gs_general_sound.md)), or a stereo PSG ([SAA1099](saa1099.md)). The **ZX-MultiSound** puts **all of them plus a MIDI wavetable synthesizer** on one open-source board: two YM2203 (TurboSound FM), a **General Sound clone with the coprocessor at 16 MHz and up to 2 MB RAM**, a SAA1099, a four-channel SounDrive, and a Dream **SAM2695** MIDI synth — with the ZX's 128K MIDI convention (AY register 14) wired straight to the wavetable chip. Every subsystem can be switched off by DIP so a dedicated card can share the bus.

The card is fully open hardware: CPLD Verilog, KiCad schematics and errata are published in [UzixLS/zx-multisound](https://github.com/UzixLS/zx-multisound). The facts below are verified against that repository's RTL and rev.A2 netlist (every pin accounted for), its issue tracker, and RTL simulation measurements — cross-checked against the classic TSFM and GS references.

---

## Board Summary

| Block | Parts | Clock |
|---|---|---|
| **TurboSound FM** | 2 × YM2203 + 2 × YM3014B DACs | 3.5 MHz average — a DDS from the 32 MHz master (32 × 7/64; period alternates 9/10 cycles, jitter inaudible) |
| **General Sound clone** | Z80 (QFP), 27C512 ROM (**GS firmware 1.05b**, [psbhlw/gs-firmware](https://github.com/psbhlw/gs-firmware)), 2 × AS6C4008 (1 MB; **2 MB** with the `rev_A1_2mb` firmware) | **16 MHz** (32/2; classic GS: 12 MHz) |
| **SAA1099** | SAA1099 | 8 MHz (32/4), **gated by control bit 3** |
| **SounDrive** | 4 channels | shares the GS DAC path |
| **MIDI synth** | Dream SAM2695 wavetable | 12 MHz average (32 × 3/8 DDS), no crystal of its own |
| **DACs** | 4 × 1-bit sigma-delta in the CPLD, 6-bit volume PWM | 32 MHz |
| **Mixer** | LM358 inverting summers, MCP602 buffers | — |
| **Power** | +5 V and **+12 V required** (edge pin b29) | — |

One 32 MHz oscillator clocks everything; the odd-looking frequencies (3.5 MHz YM, 12 MHz SAM2695) are DDS-synthesized from it, so the card needs no per-chip crystals.

## Bus Interface

The card sits on the 2×30 NemoBus/ZX-bus edge connector and answers port cycles by driving **IORQGE active high**. Two quirks verified in the RTL matter to programmers:

- **`/IORQ` is ignored.** An I/O cycle is detected as "RD or WR without M1 and without MREQ" (`// iorq_n are useless in zxevo` — the designer's comment). rev.A boards without the MREQ wire misbehaved (errata); rev.A1/A2 fix it.
- **ROM-fetch lock instead of `/DOS`.** Every M1 fetch from `#0000–#3FFF` sets a flag; while it is set, the **SAA and SounDrive ports are ignored**. This keeps TR-DOS (running from ROM, using `#1F/#3F/#5F/#7F/#FF`) from hitting SounDrive channel 1 — but it is coarser than the real `/DOS`: *any* code executing from the ROM area, including 48K BASIC, cannot reach those ports.

## Port Map

| Function | Decode | Example ports | IORQGE | ROM lock | DIP |
|---|---|---|---|---|---|
| YM register/control | A15-14 = `11`, A3-0 = `1101` | `#FFFD`, **`#DFFD`**, `#CFFD`, `#C00D` | only when A13 = 1 (`#FFFD`, `#EFFD`, …) | no | `ym` |
| YM data | A15-14 = `10`, A3-0 = `1101` | `#BFFD`, `#8FFD`, `#800D` | yes | no | `ym` |
| SAA write | low byte `#FF`; A8 = SAA A0 | `#FF` data, `#1FF` address | **no** | **yes** | `saa` |
| GS data | low byte `#B3` | `#xxB3` | yes | no | `gs` |
| GS command/status | low byte `#BB` | `#xxBB` | yes | no | `gs` |
| SounDrive | A7=0, A5=0, A3-0=`#F`; channel = {A6,A4} | `#0F` ch0, `#1F` ch1, `#4F` ch2, `#5F` ch3 (+ mirrors) | **no** | **yes** | `sd` |

Notes verified in RTL co-simulation:

- **There is no GS control port `#33`** (the classic GS has it): software that resets a GS through `#33` gets nothing.
- **`#DFFD` is deliberately shared**: the write reaches the selected YM2203 *and* the machine's own `#DFFD` paging register (IORQGE is not driven) — "required for compatibility with #dffd", per the firmware comment. A `#DFFD` *read* is a genuine bus fight between card and machine.
- IORQGE follows the address regardless of direction or cycle type; `IN #BFFD` asserts it while the card drives nothing — on a well-behaved machine the read returns the floating bus.
- Reads: `#FFFD` returns the selected YM2203's status or register (per control bit 1); `#xxB3`/`#xxBB` the GS output/status; everything else floats.

## The Control Byte — and How It Differs from Classic TSFM

A write to the YM register port with the **top four bits `1111`** is a control byte:

| Bit | Effect | 0 | 1 |
|---|---|---|---|
| 0 | YM chip select | chip 1 (U4) | chip 2 (U10) |
| 1 | `IN #FFFD` mode | status | selected register |
| 2 | FM mute (both chips) | FM on | **muted** |
| 3 | SAA clock | on | **off** (frozen) |

| Behavior | Classic TSFM | ZX-MultiSound |
|---|---|---|
| Control-byte mask | top **five** bits `11111` | top **four** bits `1111` — so `#F0–#F7` are control bytes here, register addresses on TSFM |
| Does the byte reach a YM2203? | **no** (`/WR` held inactive; address latch untouched) | **yes** — the selected chip latches it as an address write; a chip *switch* even lets the newly-selected chip latch it (the 15.6 ns CS overlap is below the YM2203 write pulse, so no data write occurs — but the latched address changes) |
| Plain TS chip-switch (`#FF`/`#FE`) | harmless | has bit 3 = 1 → **stops the SAA**, bit 2 = 1 → **mutes FM**; software wanting FM+SAA writes `#F0–#F3`-style values deliberately |
| Compatibility victim | — | *Ball Quest* writes `#F0–#F7` as YM addresses and clicks (issue [#11](https://github.com/UzixLS/zx-multisound/issues/11)); the unofficial `ctrlMask = classic` option restores five-bit behavior |

**Reset state**: chip 1 selected, `IN #FFFD` returns the selected **register** (not the status), **FM muted**, SAA clock off — a program must write a control byte with bits 2–3 clear before anything is audible. (The classic TSFM also resets FM-muted but defaults to status reads.)

## The Subsystems

### TurboSound FM pair

Two YM2203s, each with 3 FM + 3 SSG (AY-compatible) channels; SSG from both chips is mixed **ABC** (A left, B center, C right). Only one I/O pin of the pair is wired: **chip 1's IOA2 feeds the SAM2695 MIDI input** (the 128K MIDI-out convention, register 14 bit 2) — software bit-bangs 31 250 baud on it (register 7 bit 6 must make port A an output). Measured behavior worth knowing (issue [#6](https://github.com/UzixLS/zx-multisound/issues/6)): **no busy after an address write** — busy appears after *data* writes only.

### General Sound at 16 MHz

A GS-compatible coprocessor with the clock raised 12 → **16 MHz** and RAM to 1–2 MB. Host ports `#B3`/`#BB` (no `#33`); page register = GS port 0 bits 0–6; DAC volumes ports 6–9; DAC sample reads at `#6000–#7FFF` with the channel in A9-A8. Verified specifics:

- The **INT line runs at 12 MHz/321 = 37.383 kHz** (the classic GS divides differently), low for 2.75 µs.
- The ROM is the 32 KB GS 1.05b image doubled into 64 KB.
- **Status-flag quirks** (RTL-exact): the data flag clears on a host `#B3` read *or a GS access to port 2*, sets on a host `#B3` write or GS port 3; the command flag sets on `#BB` write, clears on GS port 5; GS port `#0A` inverts the data flag from page bit 0, port `#0B` sets the command flag from volume-3 bit 5 — and **volume 3 is shared with SounDrive channel 3**, so a SounDrive write to `#5F` at full volume raises the command flag.
- Interrupt-acknowledge reads `#FF` (IM2 vector).

### SounDrive and the shared sigma-delta DACs

Four channels, each fed by **either** the GS (its memory reads) **or** the SounDrive ports — last writer wins, with the RTL's priority deciding only on a same-edge tie (GS sample > SounDrive sample; SounDrive volume > GS volume). A SounDrive write forces volume 63. The transfer function (simulation-exact): each pin is a 1-bit first-order sigma-delta at 32 MHz with a PWM volume gate; mean output = `0.5 + 0.5 × level/128 × gain/64`, where level is the byte's sign-magnitude value (`#00` = −127, `#7F`/`#80` = 0, `#FF` = +127 — full scale never reached) and gain is the volume for 0–62 but **64 for volume 63**.

### MIDI: SAM2695

The wavetable chip's MIDI IN is wired **directly** to YM chip 1 IOA2 — no level shifter (5 V YM into 3.3 V SAM, works in practice). Straps: XDIV high (12 MHz mode, matching the DDS clock), parallel bus unused, reset shared with the YMs.

## Mixer (verified gains)

| Source | L | R | Filter |
|---|---|---|---|
| FM 1 + FM 2 | 0 dB | 0 dB | 2.2 nF hold cap |
| SSG A (both chips) | −7.6 dB | 0 | — |
| SSG B | −13.4 dB | −13.4 dB | — |
| SSG C | 0 | −7.6 dB | — |
| SAA L/R | ×0.833 | ×0.833 | 2-pole RC, −3 dB at **7.0 kHz** |
| MIDI L/R | 0 dB | 0 dB | — |
| DAC 0-1 (GS ch 1-2, SounDrive `#0F`/`#1F`) | −13.6 dB | 0 | 1-pole, 16.25 kHz |
| DAC 2-3 (GS ch 3-4, SounDrive `#4F`/`#5F`) | 0 | −13.6 dB | 1-pole, 16.25 kHz |

SSG is **ABC**; the GS/SounDrive channels are **hard left / hard right** (1-2 left, 3-4 right) — unlike the 50 % cross-feed of a stock GS mix.

## DIP Switch — Polarity Trap

SW1.1–1.4 enable YM/TSFM+MIDI, SAA, GS, SounDrive. Each line has a pull-up and the switch shorts it to ground, while the RTL enables are active high — so **"switch ON" (closed) disables the function**, the opposite of the silkscreen. A disabled function also releases its ports, so a second, dedicated card can occupy the bus.

## Revisions and Firmware

| Item | rev.A | rev.A1 | rev.A2 |
|---|---|---|---|
| MREQ to CPLD | missing (bodge wire) | fixed | fixed |
| MIDI mix resistors | 18 k (−5.1 dB) | 10 k (0 dB) | 10 k |
| DAC mix resistors | 33 k | 47 k | 47 k |
| 3.5 mm jack | L/R swapped | swapped | fixed |
| GS Z80 clock | unbuffered (unstable GS) | same | buffered |

CPLD firmware history: GS 16 MHz (2022-11), 2 MB option (2023-02), NemoIDE compatibility (2023-03), SounDrive + `#FF` removed from IORQGE (2023-12), YM chips swapped (2024-01 — "fixes stellar.scl"). Emulator authors pick rev.A2 with current firmware as the least-buggy variant.

## ZX-MultiSound vs ZXM-SoundCard

The two Russian "everything cards" are easy to confuse:

| | [ZXM-SoundCard](zxm_soundcard.md) (Mick Laboratory) | ZX-MultiSound (UzixLS) |
|---|---|---|
| Engines | 2 × YM2203 + SAA1099 + SounDrive (TLC7226 DACs) | 2 × YM2203 + **GS clone @ 16 MHz** + SAA1099 + SounDrive (sigma-delta DACs) + **SAM2695 MIDI** |
| Sample engine | none | General Sound coprocessor, 1–2 MB |
| MIDI/wavetable | none | SAM2695 via YM IOA2 |
| Open source | yes | yes |

## Emulation Notes

- The YM clock is DDS-jittered on hardware (9/10-cycle alternation) but modeled as exact 3.5 MHz — the jitter is inaudible.
- IORQGE semantics (address-only, direction-blind) mean port-read side effects differ from naive models; `IN #BFFD` must return the floating bus.
- The control-byte reach-into-YM behavior (address latch change on chip switch) is required for accurate *Ball Quest* breakage and for software that relies on re-latching.

---

## Cross-References

- [TurboSound FM](turbosound_fm.md) — the classic control byte this card extends (and deviates from)
- [General Sound / NeoGS](gs_general_sound.md) — the coprocessor this card clones at 16 MHz
- [SAA1099](saa1099.md) · [Covox & SounDrive](covox_sounDrive.md)
- [ZXM-SoundCard](zxm_soundcard.md) — the other all-in-one card
- [Sound hardware overview](sound_overview.md) — where this card sits in the ecosystem
- [AY-3-8912](ay_3_8912.md) — the SSG half of the YM2203, and the register-14 MIDI convention

---

## References

- **[UzixLS/zx-multisound](https://github.com/UzixLS/zx-multisound)** — open hardware: `cpld/rtl/top.v`, KiCad schematics (`pcb/rev.*/`), `ERRATA.txt`, README (verified live, October 2026)
- **Issue tracker** — [#6](https://github.com/UzixLS/zx-multisound/issues/6) (YM busy behavior), [#9](https://github.com/UzixLS/zx-multisound/issues/9) (reset prescaler), [#11](https://github.com/UzixLS/zx-multisound/issues/11) (*Ball Quest* control-byte clash and the `ctrlMask = classic` patch)
- **[psbhlw/gs-firmware](https://github.com/psbhlw/gs-firmware)** — the GS 1.05b ROM the card carries
- **YM2203 / YM3014B / SAA1099 / SAM2695 datasheets** — via the chip articles above
