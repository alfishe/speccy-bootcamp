[← Home](../../README.md) · [Clone Hardware](README.md)

# Profi 5.03 / 5.04 / 1024 — The Russian Professional Spectrum with VGA and ISA

The **Profi** (Russian: **Профи**, meaning "Professional") is the Soviet Spectrum's **workstation-class clone** — a machine built for professional users who needed PC-like expansion capabilities. Designed and produced in **Moscow, Russia (then Russian SFSR)** beginning in **late spring 1991** by the firm **"Kramis" / "Profi" / "Condor"**, the Profi went further than any other Soviet Spectrum clone of its era: it added an **ISA-compatible expansion bus**, **VGA-compatible video output**, **CP/M support**, an **AY-3-8910/12 sound chip** (making it one of the first mass-produced Soviet clones to include this sound chip), a **turbo mode** that could run at 5 MHz or 7 MHz, and 256–512 KB of RAM expandable to 1 MB.

The Profi's most distinctive characteristic — from a programmer's perspective — is its **paper offset quirk**: the visible screen area starts at T-state 12,580 instead of the standard 14,335. This 1,755-T-state shift means timing-sensitive code that assumes standard 48K paper timing will **race the beam** and corrupt the visible display. The Profi also uses a **different extended paging port** (`#DFFD`) from both the Pentagon (`#EFF7`) and the Kay (which also uses `#DFFD`, but with different semantics).

> [!NOTE]
> This article covers the **hardware platform**. For the Profi's frame timing and the paper-offset quirk, see [video_frame_other_soviet.md](../../05_development/05_display_and_timing/video_frame_other_soviet.md). For the broader clone timing landscape, see [clone_timing.md](clone_timing.md).

---

## History — The "Kramis" / "Profi" / "Condor" Story

The Profi's commercial history reads like a detective story, reconstructed by Alone Coder in *ACNews #65* (2008) from Radio magazine ads, business registrations, and contemporary interviews.

### The Kramis Joint Venture

The Profi was produced by a firm operating under several related names — the most likely sequence is:

- **JV "Kramis"** — a Russian-Spanish-Lebanese joint venture, named "Kramis". Kramis itself produced **wallpaper and woodwork**, not computers. The Profi project appears to have been a side venture within the joint venture.
- **"Profi"** — an operating department within or subsidiary of JV Kramis that handled the computer business
- **TOO "Condor"** (or "Condor (Kramis)") — the firm's registered name after formal incorporation, with a different Moscow location ("Library for youth #214") and phone number from the earlier Kramis listings

The Profi computer was released in **late spring of 1991** (per the *Turbo2+* book by MicroART; no earlier ads have been found). It was possibly the **first mass-produced Soviet Spectrum clone to ship with the AY-3-8910/12 sound chip** as standard, alongside 256–512 KB of RAM, high-resolution graphics, and a turbo mode.

### The Tadeusz Radjusz Connection

The sole "Condor" with online traces is **TOO "Condor" headed by Tadeusz Radjusz** — a Polish publisher who entered the Soviet computer business around 1990. Radjusz's background is significant:

- **First FidoNet user in Moscow** (around 1990) — the actual node and BBS were operated by his Russian wife Elena Radyush from their home near metro Krasnopresnenskaya, on a 386/25 PC with a 2400 baud modem
- **Soviet-Polish "Computer" magazine** (1990–1991) — Radjusz collaborated on this magazine; Russian articles were transmitted to Poland by mailer, and the assembled issues were downloaded back. The BBS functioned as a supplementary computer magazine
- **Beta 128 Disk Interface import** — there are rumors that Radjusz brought the Beta 128 Disk Interface into the USSR, though the first Russian clone of the Beta 128 was actually produced in early 1988 by Sergey Pacyuk and Vyacheslav Bogomyatov of NTK "Plus", Moscow

Radjusz wrote an article about Betadisk for the Soviet-Polish Computer magazine. The Condor firm eventually shut down; the Moscow address and phone number (now occupied by a political organization) are no longer active.

### The Profi as a Product

The Profi was positioned as a **"serious" alternative to the IBM PC** — aimed at a minority professional customer, not the gaming market that dominated the tape-driven 48K clone scene. The Profi competed directly with ATM-COMPUTER's **ATM-Turbo** (released in 1991 by another Moscow-based firm). Where the Profi distinguished itself:

- **AY-3-8910/12 sound chip** — among the first mass-produced Soviet clones to include this as standard
- **CP/M operating system** — adapted for the Profi (alongside Byte and ATM-Turbo), allowing professional productivity applications
- **Two-board design** — the Profi used a two-board architecture (vs the ATM-Turbo's single board) — the Profi had its own custom case
- **High-resolution graphics** — supported a separate high-resolution mode for CP/M applications and word processing
- **DAC and stereo sound** — an 8-bit Covox-style DAC was included in the printer port, supporting stereo sound at the cost of non-standard printer port addresses

The Profi was sold alongside the "Nadezhda" (Hope) 128K machine — a budget offering from the same firm (Radio magazine, August 1994).

---

## Hardware Architecture

The Profi is built from discrete Soviet TTL logic (КР1533 series, equivalent to 74ALS), with the following key differences from the Pentagon:

### CPU and Clock

The Profi uses a **CMOS Z80** (КР1858ВМ1, equivalent to Z84C0006 — a 6 MHz-rated part) and runs at three selectable clock speeds:

| Mode | Clock | Switching | Notes |
|---|---|---|---|
| **Standard** | 3.5 MHz | Default | Sinclair-compatible speed |
| **Turbo 5** | 5.0 MHz | Hardware switch or port `#DFFD` bit 3 | Some timing-sensitive code still works |
| **Turbo 7** | 7.0 MHz | Hardware switch or port `#DFFD` bit 3 | Full speed — requires cycle-exact code review |

The turbo mode is switched via a hardware button on the case, but can also be controlled from software via port `#DFFD`. The Profi's turbo is a **clean clock switch** — unlike the ATM Turbo, there is no memory bus bottleneck; all RAM is fast enough for 7 MHz access.

### Video Subsystem — VGA Output

The Profi's video subsystem is its most innovative feature. In addition to the standard composite video output (compatible with all Spectrum software), the Profi adds a **VGA output** via a dedicated video DAC and sync generator:

| Output | Resolution | Refresh | Sync |
|---|---|---|---|
| **Composite** | 256×192 (standard) | ~50 Hz | PAL composite |
| **VGA** | 256×192 (scaled) | 50 Hz / 60 Hz | VGA separate H/V sync |

The VGA output runs at the Spectrum's native 50 Hz (or optionally 60 Hz for NTSC monitors). The 256×192 display is scaled up to fill a 640×480 or 720×400 VGA frame using simple line-doubling and pixel-doubling. There is no additional video RAM for the VGA mode — the same screen buffer is used, just output through a different signal path.

> [!NOTE]
> The Profi's VGA output does **not** add higher resolution or more colors. It simply provides a VGA-compatible signal for monitors that cannot accept composite video. Software is unaware of whether the output is composite or VGA — both read from the same screen buffer at `#4000`–`#7AFF`.

### ISA Expansion Bus

The Profi includes a **PC AT ISA bus connector** on the motherboard — the same 16-bit ISA bus used in IBM PC AT clones of the era. This allows connecting PC ISA cards directly to the Profi:

| Card type | Compatibility | Use case |
|---|---|---|
| **VGA cards** | Partial — requires Profi-specific driver | Higher-resolution video modes (640×480, 800×600) |
| **IDE controllers** | Good — 8-bit transfers work | Hard disk storage |
| **Sound cards** | Limited — Adlib/SB require PC BIOS | Rarely used; TurboSound is preferred |
| **Network cards** | Good — NE2000-compatible Ethernet | TCP/IP networking via ZXIP stack |

The ISA bus operates in **8-bit mode** by default — the Profi does not implement the full 16-bit ISA data path. 16-bit ISA cards that require 16-bit transfers will not work. The bus speed is the Z80's clock divided by 4 (approximately 875 kHz at 3.5 MHz, or 1.75 MHz at turbo 7), which is slow enough for most ISA cards.

Programming ISA cards requires mapping their I/O ports into the Z80's I/O space via a programmable address decoder. The Profi's ISA bridge maps the PC's I/O ports `#0100`–`#03FF` (the standard ISA I/O range) to Z80 ports `#0100`–`#03FF` directly — but the data path is 8-bit, so 16-bit ISA registers require two reads/writes.

---

## Memory Architecture and Paging

The Profi uses the standard `#7FFD` port for base 128K paging, and adds port `#DFFD` for extended memory, turbo control, and video mode selection.

### Memory Map

```
Address range    Contents               Control
──────────────────────────────────────────────────────────
#0000 - #3FFF   ROM 0 / ROM 1 / TR-DOS  #7FFD bit 4 + Beta port
#4000 - #7FFF   Bank 5 (fixed)         Always Bank 5
#8000 - #BFFF   Bank 2 (fixed)         Always Bank 2
#C000 - #FFFF   Banks 0-7 (standard)   #7FFD bits 0–2
                Banks 8-63 (extended)  #DFFD bits 0–2 (high bits)
──────────────────────────────────────────────────────────
```

### Port #DFFD — Profi Multi-Function Register

The Profi's `#DFFD` port is **overloaded** — it controls multiple functions:

```
Port #DFFD (Profi multi-function register, write-only):

  Bit 0: Extended bank bit 0  ┐
  Bit 1: Extended bank bit 1  ├─ High bits of bank number
  Bit 2: Extended bank bit 2  ┘
  Bit 3: Turbo mode (0 = 3.5 MHz, 1 = 5 or 7 MHz depending on hardware switch)
  Bit 4: VGA refresh rate (0 = 50 Hz, 1 = 60 Hz)
  Bit 5: Video output select (0 = composite, 1 = VGA)
  Bit 6: ROM bank select (extended ROM banking)
  Bit 7: Unused
```

> [!WARNING]
> Because `#DFFD` is multi-function, software that changes the extended bank must preserve the turbo/video/ROM bits. The standard pattern is:
> ```z80
> LD   A,(PROFI_DFFD_SHADOW)    ; Read shadow copy of #DFFD
> AND  #F8                      ; Clear bank bits (preserve other bits)
> OR   NEW_BANK_HIGH            ; Set new extended bank bits
> LD   BC,#DFFD
> OUT  (C),A
> LD   (PROFI_DFFD_SHADOW),A    ; Update shadow
> ```

### Comparison with Pentagon and Kay Paging

| Clone | Extended port | Bank bits | Turbo bit | Video bits |
|---|---|---|---|---|
| **Pentagon 1024** | `#EFF7` | Bits 0–2 | No | No |
| **Kay 1024** | `#DFFD` | Bits 0–2 | No | Yes (2006 NB: bits 4–5) |
| **Profi 1024** | `#DFFD` | Bits 0–2 | Bit 3 | Bits 4–5 |

All three use the same formula: `bank = (extended & #07) × 8 + (#7FFD & #07)`, giving 64 banks (1024 KB). But the extended port address and the non-banking bits differ — software targeting one clone will not work on the others without adjustment.

---

## The Paper Offset Quirk

The Profi's most notorious programming issue is its **paper offset**: the visible screen area begins at a different point in the frame than on any other Spectrum model.

```
48K frame:    INT → 14,335 T → Paper starts at scanline 64
Profi frame:  INT → 12,580 T → Paper starts at scanline ~56
                                ^^^^^^^^^^^^^^^^^^^^^^^^
                                1,755 T-states EARLIER
                                (~7.8 scanlines)
```

This means the Profi has **12% less time** between the INT signal and the start of the visible display. Interrupt service routines that assume they have 14,336 T-states of free time (the 48K standard) will still be running when the Profi's paper area begins, causing visible corruption.

> [!WARNING]
> Code that uses `HALT` to synchronize with INT and then performs setup work before the paper area must be adjusted for the Profi. Either:
> 1. **Reduce setup time** to under 12,580 T-states (the Profi's paper offset)
> 2. **Skip Profi support** if your effects depend on tight timing
> 3. **Detect the Profi** and use a different timing table

See [video_frame_other_soviet.md](../../05_development/05_display_and_timing/video_frame_other_soviet.md) for detection code and detailed timing analysis.

---

## Cross-References

- [Pentagon 128K](pentagon.md) — the dominant Soviet clone (different timing, `#EFF7` paging)
- [Pentagon 1024](pentagon_1024.md) — Pentagon's 1 MB variant
- [Kay 1024](kay.md) — alternative professional clone with Nemo bus
- [Scorpion](scorpion.md) — high-end clone with SMUC ISA bridge
- [ATM Turbo](atm_turbo.md) — CP/M-capable clone with extended graphics
- [Profi video frame](../../05_development/05_display_and_timing/video_frame_other_soviet.md) — paper offset quirk and detailed timing
- [Clone timing](clone_timing.md) — cross-clone timing comparison
- [IDE interface](../../03_io/storage/ide_interface.md) — general IDE programming (Profi uses ISA IDE cards)
- [TR-DOS](../../04_operating_systems/trdos.md) — disk operating system
- [Beta 128 FDC](../../03_io/storage/beta_disk_interface.md) — disk interface

---

## References

- [Profi 5.03 / 5.04 schematics](https://zxpress.ru/library/) — original design documentation, distributed via *Radio* magazine advertisements and *ZX-Review*
- [ACNews #65](https://zxpress.ru/) — reconstruction of the Kramis/Profi/Condor commercial history from *Radio* magazine ads and business registrations
- ***Turbo2+* book** (MicroART) — confirms Profi's release date as late spring 1991
- [ZX-Review magazine](https://zxpress.ru/library/) — Profi construction articles, modification guides, and ISA bus programming tutorials
- **[zx-pk.ru](https://zx-pk.ru) forum** — *Профі* subforum contains hardware variants, VGA modification threads, and ISA card compatibility reports
- [velesoft.speccy.cz](https://velesoft.speccy.cz) — Solitude Soft's Profi 5.03 technical reference, including `#DFFD` paging tests and CP/M adaptation notes
- **SpeccyWiki (speccy.info)** — Profi 5.03/5.04 articles with schematic scans and PCB layouts
- [Unreal Speccy emulator](https://sdkcad.free.fr/) — reference implementation of Profi `#DFFD` paging and paper-offset timing
- **[chibiakumas.com](https://chibiakumas.com)** — English translations of Profi hardware articles and ISA programming guides
