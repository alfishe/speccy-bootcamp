[← Home](../../README.md) · [Clone Hardware](README.md)

# Profi 5.03 / 5.04 / 1024 — The Russian Professional Spectrum with VGA and ISA

The **Profi** (Russian: **Профи**, meaning "Professional") is the Soviet Spectrum's **workstation-class clone** — a machine built for professional users who needed PC-like expansion capabilities. Designed and produced in **Moscow, Russia (then Russian SFSR)** beginning in **late spring 1991** by the firm **"Kramis" / "Profi" / "Condor"**, the Profi went further than any other Soviet Spectrum clone of its era: it added an **ISA-compatible expansion bus**, **VGA-compatible video output**, **CP/M support**, an **AY-3-8910/12 sound chip** (making it one of the first mass-produced Soviet clones to include this sound chip), a **turbo mode** that could run at 5 MHz or 7 MHz, and 256–512 KB of RAM expandable to 1 MB.

The Profi's most distinctive programmer-facing feature is its **extended screen**: 512×240 pixels with one attribute byte per 8-pixel strip — hardware multicolor, eight times the vertical color resolution of the stock attribute cell — plus a 16-from-256 palette on Profi 5 boards. Timing code faces a second surprise: the **paper offset quirk** — the visible area starts at T-state ≈12,580 instead of the standard 14,335, so raster code assuming 48K paper timing will **race the beam** and corrupt the display. And paging runs through a second control register, **CMR1** at `#DFFD`, alongside the 128K-standard CMR0 at `#7FFD` — the Pentagon's `#EFF7` plays a different role, and the Kay reuses the same `#DFFD` address with different extra-bit semantics.

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
| **Turbo 5** | 5.0 MHz | Hardware switch | Some timing-sensitive code still works |
| **Turbo 7** | 7.0 MHz | Hardware switch | Full speed — requires cycle-exact code review |

> [!NOTE]
> Clock selection is **hardware only** — a button/switch on the case. Neither CMR0 (`#7FFD`) nor CMR1 (`#DFFD`) carries a turbo bit, so software can neither set nor clear the clock; programs must simply tolerate running at any of the three speeds.

The Profi's turbo is a **clean clock switch**. Like the other discrete Soviet clones, the Profi has **no memory contention** at 3.5 MHz — video and CPU get their own memory slots — and no turbo wait is documented. This is the consensus of emulators (ZXMAK2's `UlaProfi3XX` and others run the Profi uncontended); no analysis of the original schematic has been published. The FPGA re-creation [Karabas-Pro](../newgen/karabas.md) adds its own delays — optional Sinclair-style contention in its "classic" screen mode and waits at 14 MHz — which the original board does not have. See [contention_model.md](../../05_development/03_memory_and_io/contention_model.md) for the cross-model picture.

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

The Profi keeps the 128K control register — **CMR0** (Control Memory Register 0) at `#7FFD` — and adds a second one: **CMR1** at `#DFFD`, write-only, decoded in every peripheral addressing mode. Together they drive extended paging, window placement, ROM bypass, CP/M port semantics, and the extended screen.

### Memory Map

```
Address range    Contents               Control
──────────────────────────────────────────────────────────
#0000 - #3FFF   ROM 0 / ROM 1 / TR-DOS  #7FFD bit 4 + Beta port
                RAM page 0 (NOROM)      #DFFD bit 4
#4000 - #7FFF   Bank 5 (fixed)         Always Bank 5 (ZX 128 model)
#8000 - #BFFF   Bank 2 (fixed)         Always Bank 2
#C000 - #FFFF   Banks 0-7 (standard)   #7FFD bits 0–2
                Banks 8-63 (extended)  #DFFD bits 0–2 (high bits)
──────────────────────────────────────────────────────────
```

### Ports #7FFD and #DFFD — the CMR0 / CMR1 Pair

| Port     | Decoding    | R/W | Description |
|----------|-------------|-----|-------------|
| `#7FFD`  | A15=0, A1=1 | W   | CMR0 — 128K-compatible paging: page low bits, screen, ROM, lock |
| `#DFFD`  | A13=1, A1=1 | W   | CMR1 — Profi extension: page high bits, windows, NOROM, CP/M, extended screen |

> [!NOTE]
> Bit assignments below are those of the hardware documentation (TAE/Chertkov) cross-checked against the ZXMAK2 emulator implementation (`MemoryProfi1024`), the cleanest public reference model. CMR1 stays writable regardless of the CMR0 bit-5 lock; the high-page mask is `RAM pages / 8 − 1`, so a 512 KB Profi masks bit 2 and reaches only pages 0-31.

```
Port #DFFD — CMR1 (write-only, all peripheral modes):

  Bit 7: DS80  — extended screen enable (512×240 video + palette access)
  Bit 6: SCR   — page at window #8000 (0 = page 2, 1 = page 6)
  Bit 5: CPM   — CP/M port-map modifier (with CMR0 bit 4, see below)
  Bit 4: NOROM — RAM page 0 at #0000 (ROM disconnected; releases the lock)
  Bit 3: SCO   — projection window position (0 = #C000, 1 = #4000)
  Bit 0: Extended bank bit 0  ┐
  Bit 1: Extended bank bit 1  ├─ High bits of RAM page number
  Bit 2: Extended bank bit 2  ┘   (page = CMR1 bits 0-2 << 3 + CMR0 bits 0-2)
```

CMR1 bit 4 (**NOROM**) maps RAM page 0 over the ROM at `#0000`–`#3FFF`. That is the entry ticket for CP/M, which needs RAM in low memory — and it also simply hands Spectrum-mode programs another 16 KB.

CMR0 keeps its 128K layout with two Profi-specific footnotes:

- **Bit 5 — paging lock.** Once set, further writes to `#7FFD` are ignored until NOROM maps RAM over the ROM and clears the lock. (The designers originally intended this bit to gate palette-register access in CP/M mode; the hardware authors note that palette writes work with or without it — the gating never actually functioned.)
- **Bit 4 — ROM select / CP/M port modifier.** In Spectrum mode it picks the ROM page as on any 128K. In CP/M mode, `ROM14=1` combined with CMR1 bit 5 (`CPM=1`) switches the peripheral map: with `ROM14=0` the I/O space is addressed as in **PROFI+ V3.2**; with the modifier active roughly **30 additional ports** become available.

The machine has a single 16 KB **projection window** that can show any RAM page, and CMR1 bit 3 chooses where it sits — producing two memory models:

| Window position (`SCO`) | `#0000` | `#4000` | `#8000` | `#C000` |
|---|---|---|---|---|
| `SCO=0` (ZX 128 model) | ROM (or page 0 via NOROM) | page 5 (fixed) | page 2 or 6 (`SCR`) | **projection window** |
| `SCO=1` (Profi/CP-M model) | ROM (or page 0 via NOROM) | **projection window** | page 2 or 6 (`SCR`) | page 7 (fixed) |

The shadow-copy pattern survives intact — it just needs two registers now:

```z80
; Select extended RAM page N (0-63) in the projection window
; (ZX 128 model, SCO=0)
PageIn:
    LD   A,(PAGE_SHADOW)         ; shadow copy of CMR0
    AND  #F8                     ; keep screen/ROM/lock bits
    OR   N_LOW                   ; N & 7
    LD   (PAGE_SHADOW),A
    LD   BC,#7FFD
    OUT  (C),A
    LD   A,(PAGE_SHADOW1)        ; shadow copy of CMR1
    AND  #F8                     ; keep DS80/SCR/CPM/NOROM/SCO
    OR   N_HIGH                  ; N >> 3
    LD   (PAGE_SHADOW1),A
    LD   BC,#DFFD
    OUT  (C),A
    RET
```

### Comparison with Pentagon and Kay Paging

| Clone | Extended port | Bank bits | Turbo bit | Extra control bits |
|---|---|---|---|---|
| **Pentagon 1024** | `#EFF7` | Bits 0-2 (full page) | No | RAM gate, video, turbo |
| **Kay 1024** | `#DFFD` | Bits 0-2 | No | Video (2006 NB: bits 4-5) |
| **Profi 1024** | `#DFFD` | Bits 0-2 | No (hardware button) | Bits 3-7 (windows, NOROM, CP/M, extended screen) |

The Pentagon 1024 packs the whole page number into `#EFF7` bits 0-2 and needs no low bits, while the Kay and Profi split it between `#7FFD` bits 0-2 (low) and their extended port bits 0-2 (high): `bank = (extended & #07) × 8 + (#7FFD & #07)`, giving 64 banks (1024 KB). The non-banking bits differ completely — software targeting one clone will not work on the others without adjustment.

---

## The Extended Screen — 512×240 Hardware Multicolor

Setting CMR1 bit 7 (**DS80** — "extended video") does more than page memory: it switches the video subsystem to a second display format. The screen becomes **512×240 pixels** — 64×30 text cells — and every 8-pixel byte gets **its own attribute byte**. TAE and Vadim Chertkov, who documented the mode for the *Абзац* newspaper in 2003, called it "аппаратный мультиколор" — hardware multicolor — and the name is exact. It is the same value proposition as Timex HiColor: attribute resolution of 8×1 pixels across the whole screen with zero CPU cost, except the Profi's version runs at double width, adds 48 lines, and eats twice the memory.

In modern terms it is a cell-quantized framebuffer — like arcade display hardware that pairs a bitmap with per-tile palette indices, except the Profi's "tile" is 8×1 pixels. Color detail is bought with memory, not CPU cycles.

| Property | Value |
|---|---|
| Resolution | 512×240 pixels — 64×30 text cells at 8×8 |
| Screen memory | 30,720 bytes = 15,360 pixel bytes + 15,360 attribute bytes |
| Attribute granularity | 1 byte per 8×1 pixel strip ("hardware multicolor") |
| Colors | Variant-dependent: B/W → 8+2 brightness → 16 → 16 from 256 (Profi 5) |
| Frame | 59,904 T-states (312 lines × 192 T/line) vs 69,888 in ZX mode |
| Enable | `LD BC,#DFFD / LD A,%10000000 / OUT (C),A` (DS80) |

The color story has an honest footnote: 8×1 attribute resolution is eight times the *vertical* color detail of the stock 8×8 cell, but attribute data now claims **half the screen memory** — 15 KB against the standard screen's 6,912 bytes. The developers' own orientation was CP/M, where 64-column text and dense color UI matter more than memory economy.

### Hardware Variants

Extended-screen Profi boards shipped in four video grades (per the TAE/Chertkov history):

| Variant | Colors | Attribute byte meaning |
|---|---|---|
| Early B/W | 1 | Ignored — no color circuit on the board |
| 8-color + 2 brightness | 8×2 | Standard ink/paper; FLASH dead |
| 16-color | 16 | FLASH bit repurposed as second bright bit |
| Profi 5 palette | 16 from 256 | Attribute = two 4-bit palette indices |

The B/W and 8-color variants behave like a taller ZX Spectrum screen and are effectively extinct; the surviving 16-color and palette machines share one programming model, which is what this section documents.

### Two Screens and the Simultaneous-Access Trick

As on the ZX Spectrum 128, there are **two equivalent extended screens**; each occupies two RAM pages — one for pixels, one for attributes — and CMR0 bit 3 selects which is displayed:

| Screen | CMR0 bit 3 | Pixel page | Attribute page |
|---|---|---|---|
| Screen 0 | 0 | `#04` | `#38` (decimal 56) |
| Screen 1 | 1 | `#06` | `#3A` (decimal 58) |

Two update strategies exist:

1. **Sequential** — works on both screens. Page the pixel page into the projection window, write, then page the attribute page in and write again.
2. **Simultaneous** — screen 1 only. With CMR1 bit 6 (`SCR=1`), pixel page `#06` is hard-mapped at `#8000`–`#BFFF` while attribute page `#3A` sits in the projection window (`#4000` or `#C000`, depending on `SCO`). Pixels and attributes become writable at the same time.

The simultaneous trick is why CP/M uses **screen 1 as the primary display** and screen 0 as the auxiliary buffer. Inside the opened pair, the pixel↔attribute address translation is a single XOR — the attribute area sits `#4000` below the pixel area:

```z80
; DE = pixel address → DE = attribute address of the same cell
    LD   A,#C0
    XOR  D
    LD   D,A
```

### Screen Structure — Two Interleaved Half-Screens

Each 15,360-byte area — pixels and attributes alike — is stored **non-linearly**. It splits into two half-screens of 32 columns: the first part holds the odd-numbered columns (1st, 3rd, 5th, … counting from 1), the second part the even ones. The video circuit fetches one byte from each half alternately, so a pixel row reads: column 1 from the first part, column 2 from the second, column 3 from the first again.

Each half-screen keeps the classic ZX-Spectrum screen structure — except the thirds become **quarters** (four of them; the last is short at 48 lines = 6 character rows of 8), and each holds 32 columns instead of the full 64.

With the pixel page opened at `#8000`, the top-left cells land at:

```
Column 1 (first cell):  #A000 = 1010 0000 0000 0000
Column 2 (second cell): #8000 = 1000 0000 0000 0000
Column 3 (third cell):  #A001 = 1010 0000 0000 0001
```

**Address bit 13 (bit 5 of the high byte) is the part selector**: set for odd-column cells (`#A000…`), clear for even-column cells (`#8000…`). That single bit turns horizontal movement into trivial register surgery:

```z80
; HL = address of the current character cell (pixel page at #8000)
; Step to the cell on the right:
    RES  5,H        ; odd→even column: first part → second part
    SET  5,H        ; even→odd column: back to the first part...
    INC  L          ; ...one column-pair to the right
```

The efficient loop processes a column *pair* per iteration — one `RES 5,H` between the halves, then `SET 5,H / INC L` to advance. Column 31 overflows into the line bits, so a full row wrap needs the address recomputed (or a precomputed table).

The full cell address decomposes like this — cross-checked against the ZXMAK2 renderer's fetch arithmetic (`2048·(Y>>6) + 256·(Y&7) + 32·((Y>>3)&7) + (X>>1)`, plus `#2000` for the odd-column part):

```
High byte:  1 0 P Q Q S S S
              │ │ └─┴─┴── character row within the half-screen: Y>>3 (0-29)
              │ │         (top 2 bits = quarter, low 3 = row-in-quarter)
              │ └──────── P = part select = X bit 0 (1 = odd columns)
              └────────── bit 6 always 0; bit 7 always 1 (screen area)
Low byte:   L L L C C C C C
              │ └─┴─┴─┴─┴── column within the half-screen: X>>1 (0-31)
              └────────── pixel line within the character row: Y&7
```

The published address-calculation routine takes `D = X (0..63)`, `E = Y (0..239)`:

```z80
; In: D = X (0..63), E = Y (0..239). Out: DE = cell address.
Calc_ADDR:
    XOR  A
    SRL  D                 ; low bit of X into carry
    CCF
    RRA                    ; → bit 7 of A
    SCF
    RRA
    SCF
    RRA                    ; A = 10X?????  (part bit staged at bit 5)
    XOR  E
    AND  %11100111
    XOR  E                 ; merge Y bits into the high byte
    PUSH AF
    LD   A,E
    RRCA
    RRCA
    RRCA
    XOR  D
    AND  %11100000
    XOR  D
    LD   E,A
    POP  AF
    LD   D,A
    RET
```

> [!WARNING]
> This listing is transcribed from the 2003 magazine article (republished on Habr in 2024). The scan-derived transcription is lossy: as printed, the `SRL/CCF/RRA` sequence yields `11X` rather than the `10X` its own comment promises, and the merge masks leave part of the Y bits unplaced. Treat the decomposition above as ground truth; a verified reconstruction is:

```z80
; Verified equivalent. In: D = X (0..63), E = Y (0..239)
; Out: HL = cell address; D clobbered (= X>>1); F clobbered. ≈120 T-states.
; H bit 5 = part: 1 → odd columns (#A000-side), 0 → even (#8000-side)
CalcCell:
    LD   A,D
    AND  #01
    RRCA
    RRCA
    RRCA                   ; (X & 1) << 5 — part bit staged
    LD   H,A
    LD   A,E
    SRL  A
    SRL  A
    SRL  A                 ; Y >> 3 — quarter + character row (0..29)
    OR   H
    OR   #80               ; high byte = 1 0 P Q Q S S S
    LD   H,A
    LD   A,E
    AND  #07
    RRCA
    RRCA
    RRCA                   ; (Y & 7) << 5 — pixel line within the row
    LD   L,A
    SRL  D                 ; X >> 1 — column within the half-screen
    LD   A,D
    OR   L                 ; low byte = L L L C C C C C
    LD   L,A
    RET
```

### The 16-Color Attribute Byte

In the 16-color variants the FLASH bit is gone — repurposed as a second brightness bit, giving ink and paper **independent brightness**:

```
Bit:      7    6    5    4    3    2    1    0
          p3   i3   p2   p1   p0   i2   i1   i0
          │    │    └──┴──┴── paper base color ─┘  └──┴── ink base color
          │    └─ ink bright (index bit 3) — the old BRIGHT position
          └─ paper bright (index bit 3) — the old FLASH position
```

Each color field is a 4-bit **palette index**: the base color sits in the same bit positions as the ZX Spectrum attribute, with the extra high bit at bit 6 (ink) / bit 7 (paper). That yields 16 ink × 16 paper combinations — in practice 15 distinct colors, since black has no brightness variant. The emulator reference decodes it exactly this way: `ink = palette[(attr & 7) | ((attr >> 3) & 8)]`, `paper = palette[((attr >> 3) & 7) | ((attr >> 4) & 8)]`.

On pre-palette 16-color machines the index selects directly among the hardware colors; on Profi 5 boards it indexes the palette RAM below.

### The Profi 5 Palette — 16 from 256

The Profi 5 video board adds **16 bytes of static palette RAM**: the attribute color fields stop being colors and become pointers. Each palette cell holds one RGB byte in the `Gg0Rr0Bb` layout — two bits per gun at fixed positions, with bits 5 and 2 hardwired to 0 (the missing LSBs, which keep the 4-level scale linear):

```
Palette cell:  G  g  0  R  r  0  B  b
               │  │     │  │     │  └─ blue low bit
               │  │     │  │     └─ blue high bit (blue = 2 bits + implicit 0 LSB)
               │  │     └──┴─ red  = 2 bits
               └──┴─ green = 2 bits
```

Four intensity levels per gun. White is `%11011011` (`#DB`): every gun at `%11`, zeros in the reserved slots. From the factory the palette reproduces the ZX Spectrum colors exactly, so pre-palette software renders unchanged:

| Index | Color | Byte | Index | Color | Byte |
|---|---|---|---|---|---|
| 0 | black | `#00` | 8 | black (bright) | `#00` |
| 1 | blue | `#02` | 9 | blue (bright) | `#03` |
| 2 | red | `#10` | 10 | red (bright) | `#18` |
| 3 | magenta | `#12` | 11 | magenta (bright) | `#1B` |
| 4 | green | `#80` | 12 | green (bright) | `#C0` |
| 5 | cyan | `#82` | 13 | cyan (bright) | `#C3` |
| 6 | yellow | `#90` | 14 | yellow (bright) | `#D8` |
| 7 | white | `#92` | 15 | white (bright) | `#DB` |

These bytes are identical in the TAE/Chertkov article's `Palette.Std` table and in the ZXMAK2 emulator's startup palette — a byte-for-byte match across two independent sources.

### Programming the Palette

Palette access piggybacks on the ULA port class and only works while **DS80 is set** — with extended video off, palette writes are ignored. The protocol inverts everything twice:

| Step | Port | Value | Decoding | Effect |
|---|---|---|---|---|
| Select entry | `#FE` | entry number | A0=0 | index latched — the hardware stores `value XOR #0F` |
| Write RGB | `#7E` | inverted RGB in B | A0=0, A7=0 | palette cell = `NOT B` |

Entry selection rides on any write to the ULA register (the index latch simply captures the last value written to the `A0=0` port class), which is why the canonical routine writes the index through `OUT (#FE),A`. The data path needs a port decoding `A0=0` **and** `A7=0` — `#7E` is the canonical choice; with `OUT (C),r` the palette data is sampled from register **B**.

Two side effects matter:

- Every data write also asserts the ULA register itself (it decodes plain `A0=0`), so the border and beeper bits receive the palette byte. Program palettes when a border flicker is harmless, or restore the border color afterwards.
- Every ordinary `OUT (#FE),A` border write updates the index latch. Change the border between entry writes and the next entry lands in the wrong cell.

The published loader (clobbers `AF, HL, DE, BC`; entry points `SetPal` = install table at HL or standard if `HL=0`, `SetPal.StPal` = force standard, `SetPal.9` = table pre-arranged):

```z80
; HL = 16-byte palette table, or 0 for the standard palette
; Requires DS80 = 1. Clobbers AF, HL, DE, BC.
SetPal:
    LD   A,H
    OR   L
    JR   NZ,.Go
.StPal:
    LD   HL,Palette.Std     ; 0 → standard palette
.Go:
    EI
    HALT                    ; sync with the ISR: it clobbers HL/AF
    DI                      ; (CP/M stacks sit where the ROM pages in)
.9:
    LD   C,#7E
    LD   D,16
.Loop:
    LD   A,(HL)
    CPL                     ; palette data inverted
    LD   B,A                ; data goes out in B
    DEC  D                  ; 15,14,…,0 — the latch inverts to 0,1,…,15
    LD   A,D
    OUT  (#FE),A            ; select entry
    OUT  (C),B              ; write the cell (data = NOT B)
    INC  HL
    JR   NZ,.Loop           ; Z only when D wrapped through 0
    RET

Palette.Std:
    DB   #00, #02, #10, #12, #80, #82, #90, #92
    DB   #00, #03, #18, #1B, #C0, #C3, #D8, #DB
```

> [!NOTE]
> The magazine transcription prints `OUT (C),D` at the data step — contradicting its own comment ("data from B") and the hardware data path, which samples the palette byte from register B. The listing above corrects that single instruction; everything else follows the publication.

### A Complete Example

The demo installs the standard palette, wipes pixel page `#06`, fills attribute page `#3A` with an interleave-visualizing pattern, and leaves the machine displaying screen 1 with the simultaneous-access pair mapped. It runs from fixed page 5 (`#4000`–`#7FFF`), so no window game ever pulls the code out from under the program counter.

```z80
; ============================================================
; Profi extended screen bring-up demo — sjasmplus syntax
; Runs in the ZX-128 memory model (SCO=0) from fixed page 5.
; Append the SetPal routine and Palette.Std from the
; "Programming the Palette" section above to assemble.
; ============================================================
CMR0            EQU #7FFD       ; 128K paging: page low bits, screen, ROM
CMR1            EQU #DFFD       ; Profi control register
DS80            EQU %10000000   ; CMR1.7 — extended video on
SCR_PAGE6       EQU %01000000   ; CMR1.6 — page #06 hard-mapped at #8000
SHOW_SCR1       EQU %00001000   ; CMR0.3 — display screen 1

                DEVICE ZXSPECTRUM128
                ORG  #6000

Start:
        DI
        LD   SP,#6FFF            ; stack inside fixed page 5

; --- 1. DS80 on, install the standard palette --------------
        LD   BC,CMR1
        LD   A,DS80
        OUT  (C),A               ; DS80=1, everything else 0
        LD   HL,0                ; 0 → standard palette
        CALL SetPal

; --- 2. wipe pixel page #06 via the projection window ------
        LD   BC,CMR1             ; page #06 = %000110: CMR1 bits 0-2 = 0
        LD   A,DS80
        OUT  (C),A
        LD   BC,CMR0
        LD   A,SHOW_SCR1|%00000110   ; window #C000 ← page #06
        OUT  (C),A
        LD   HL,#C000
        LD   DE,#C001
        LD   BC,#3C00            ; 15,360 bytes
        LD   (HL),0
        LDIR

; --- 3. fill attribute page #3A with an interleave pattern --
        LD   BC,CMR1             ; page #3A = %111010: CMR1 bits 0-2 = 7
        LD   A,DS80|%00000111
        OUT  (C),A
        LD   BC,CMR0
        LD   A,SHOW_SCR1|%00000010   ; ...CMR0 bits 0-2 = 2 → page 58 = #3A
        OUT  (C),A
        LD   HL,#C000
        LD   BC,#3C00
.Attr:
        LD   A,H
        XOR  L
        AND  #07                 ; ink cycles through the base colors
        OR   #08                 ; never black-on-black
        LD   (HL),A              ; paper = black (0)
        INC  HL
        DEC  BC
        LD   A,B
        OR   C
        JR   NZ,.Attr            ; H bit 5 flips between paired columns:
                                 ; the fill alternates between half-screens,
                                 ; showing the interleave as 8-px stripes

; --- 4. final map: screen 1 with simultaneous access -------
        LD   BC,CMR1
        LD   A,DS80|SCR_PAGE6|%00000011  ; attrs #3A (high bits 3) +
        OUT  (C),A                       ; SCR: pixels #06 at #8000
        LD   BC,CMR0
        LD   A,SHOW_SCR1|%00000010        ; window #C000 ← page #3A
        OUT  (C),A
.Done:
        JR   .Done               ; freeze — pattern is on screen
```

From here, writes to `#8000` hit the pixel page and writes to `#C000` hit the attribute page — both for the displayed screen, no paging between them.

### Choosing a Soviet Hardware Multicolor Mode

| Criterion | Profi extended screen | Pentagon 16c | ATM 320×200×16 |
|---|---|---|---|
| Resolution | 512×240 | 248–256×192 | 320×200 |
| Color granularity | 8×1 (per pixel byte) | per pixel | per pixel |
| Palette | 16 (Profi 5: from 256) | 15 fixed | 16 from 64 RGBI |
| CPU cost | zero | zero | zero |
| Memory overhead | 50% of screen | none (true bitmap) | none |
| Text fit | 64×30 native | awkward | 40×25 / 80×25 text modes |
| Details | this article | [pentagon_1024.md](pentagon_1024.md) | [atm_turbo.md](atm_turbo.md) |

The full game-programmer decision matrix — including Timex HiColor and the software engines — lives in [multicolor_engines.md](../../05_development/06_graphics/multicolor_engines.md).

### Historical Context

The Profi and the ATM Turbo both appeared in 1991 with the same CP/M ambition and took opposite roads to color. ATM replicated IBM EGA conventions — a true per-pixel bitmap with dedicated video RAM. The Profi stayed inside the Sinclair design: the video circuit still reads a bitmap byte plus an attribute byte, just twice as often horizontally and 25% taller, with the attribute byte feeding a 16-cell SRAM palette lookup instead of a fixed RGB encoder. That is why the extended screen costs two pages per screen — like any 128K screen — while ATM's 320×200×16 needs its own VRAM bank, and why Profi extended-screen code looks like ordinary screen pokes once the half-screen interleave is internalized.

| Concept | ZX-era hardware | Modern equivalent |
|---|---|---|
| Attribute per 8×1 byte | Profi extended screen, Timex HiColor | per-run palette indices in tile/planar display hardware |
| 16-entry writable palette | Profi 5, ULAplus | indexed-color VGA DAC lookup table |
| Dual screens, one hard-mapped pair | Profi screens 0/1 + SCR | double-buffered framebuffer with a live scanout region |

### Pitfalls

1. **The Palette Latch Corruptor.** Under DS80, `OUT (#FE),A` does not just set the border — it re-arms the palette index latch, and the next `OUT (C),B` to an `A0=0, A7=0` port then programs the wrong entry.

   ```z80
   ; BAD — border write between entries re-aims the index latch
   LD   A,4
   OUT  (#FE),A             ; border green — AND index latch ← 4
   ...
   CALL WriteOneEntry       ; lands in entry 4 XOR #0F = #0B, not the one intended

   ; GOOD — keep border writes away from palette sequences,
   ; or rewrite the whole 16-entry table after border churn
   ```

2. **The Linear-Screen Assumption.** Treating the extended screen as 64 linear columns scrambles the picture: odd and even columns live in separate `#2000`-offset halves.

   ```z80
   ; BAD — consecutive HL steps walk down one half-screen, not across the row
   INC  HL                  ; next byte is 32 columns away, vertically

   ; GOOD — step in column pairs with the part bit
   RES  5,H
   SET  5,H
   INC  L
   ```

3. **Code in the Window.** Executing from the projection window while repaging pulls the floor out from under the PC. Fixed pages are safe: page 5 at `#4000` (ZX 128 model) or page 7 at `#C000` (Profi/CP-M model). The demo above runs from page 5 for exactly this reason.

4. **Forgetting SCR.** CMR1 bit 6 reroutes `#8000` to page `#06` — permanently, in every mode, DS80 or not. 128K-standard software that assumes page 2 at `#8000` crashes until SCR is cleared. Restore `CMR1 = 0` before dropping back into 128K-compatible code.

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

Enabling DS80 changes the numbers again — the extended screen runs its own clock plan:

| Parameter | ZX mode | Extended (DS80) mode |
|---|---|---|
| Frame length | 69,888 T | 59,904 T |
| Line length | 224 T | 192 T |
| Total lines | 312 | 312 |
| Paper offset (from INT) | ≈12,583 T (line 56, tact 39) | ≈13,829 T (line 72, tact 24) |
| Active video | 256×192 | 512×240 (64+512+64 px × 240 lines) |

The values are the ZXMAK2 Profi 3.2 model (`UlaProfi3XX` / `ProfiRenderer`); the emulator's own comments flag some border and INT parameters as unverified against real 3.x boards, and Unreal Speccy's presets carry the 12,580 figure for ZX mode — the sources agree to within a few T-states. The practical consequence for raster work: mode-switching software needs **two timing tables**, and the extended frame is ~14% shorter, so interrupt-driven effects have less headroom in DS80 mode.

See [video_frame_other_soviet.md](../../05_development/05_display_and_timing/video_frame_other_soviet.md) for detection code and detailed timing analysis.

---

## Cross-References

- [Pentagon 128K](pentagon.md) — the dominant Soviet clone (different timing, `#EFF7` paging)
- [Pentagon 1024](pentagon_1024.md) — Pentagon's 1 MB variant
- [Kay 1024](kay.md) — alternative professional clone with Nemo bus
- [Scorpion](scorpion.md) — high-end clone with SMUC ISA bridge
- [ATM Turbo](atm_turbo.md) — CP/M-capable clone with extended graphics (the extended screen's contemporary rival)
- [Multicolor engines](../../05_development/06_graphics/multicolor_engines.md) — where the extended screen sits among Pentagon 16c, ATM, and Timex options
- [Clone video modes](../../05_development/05_display_and_timing/clone_video_modes.md) — cross-clone video mode survey
- [Profi video frame](../../05_development/05_display_and_timing/video_frame_other_soviet.md) — paper offset quirk and detailed timing
- [Clone timing](clone_timing.md) — cross-clone timing comparison
- [IDE interface](../../03_io/storage/ide_interface.md) — general IDE programming (Profi uses ISA IDE cards)
- [TR-DOS](../../04_operating_systems/trdos.md) — disk operating system
- [Beta 128 FDC](../../03_io/storage/beta_disk_interface.md) — disk interface

---

## References

- **[TAE (Aleksey Tarasow) & Vadim Chertkov — "Расширенный экран «Profi»" (Habr, 2024)](https://habr.com/ru/articles/836836/)** — the primary source for this article's extended-screen section: screen structure, attribute format, palette protocol, CMR0/CMR1 semantics, and the CP/M memory model. First published in *Абзац* #16 (2003), reworked for *ЗаRulem Печатное Слово* #25 (2019)
- **[zx-pk.ru — Profi subforum](https://zx-pk.ru/forums/102-profi.html)** — the active Profi community: schematics, ROM sets, CP/M builds, hardware variants
- [vk.com/profi1024](https://vk.com/profi1024) and [t.me/Profi1024](https://t.me/Profi1024) — maintainer groups where current Profi software and tools are published
- **[ZXMAK2 emulator source](https://github.com/zxmak/zxmak2)** (`src/ZXMAK2.Hardware/Profi/`) — reference implementation (`MemoryProfi1024`, `UlaProfi3XX`/`UlaProfi5XX`, `ProfiRenderer`); cross-verified for this article's register tables, palette bytes, and screen fetch arithmetic
- [ACNews #65](https://zxpress.ru/) — reconstruction of the Kramis/Profi/Condor commercial history from *Radio* magazine ads and business registrations
- ***Turbo2+* book** (MicroART) — confirms Profi's release date as late spring 1991
- [ZX-Review magazine](https://zxpress.ru/library/) — Profi construction articles, modification guides, and ISA bus programming tutorials
- [SpeccyWiki](https://speccy.info) — Profi 5.03/5.04 articles with schematic scans and PCB layouts
- **[chibiakumas.com](https://chibiakumas.com)** — English translations of Profi hardware articles and ISA programming guides
