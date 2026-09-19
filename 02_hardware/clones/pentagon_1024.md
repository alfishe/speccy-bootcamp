[← Home](../../README.md) · [Clone Hardware](README.md)

# Pentagon 1024 / 1024SL — The Maximum Pentagon: 1 MB of RAM

The **Pentagon 1024** is the maximum configuration of the Pentagon family — a 1024 KB (1 MB) RAM expansion of the base Pentagon 128K. Where the base Pentagon 128K was the *default* Russian Spectrum of the early 1990s, the Pentagon 1024 became the **demoscene and power-user machine** of the late 1990s and 2000s — the platform that ran the most ambitious Russian productions, hosted the most advanced trackers (Pro Tracker 3.x), and stored the largest software collections on a single machine.

Surprisingly for a machine this influential, **the Pentagon 1024 was never factory-produced**. As Alone Coder wrote in *Born Dead* #10 (1999): every single unit was **assembled by hand**, mostly as an upgrade of an existing Pentagon 128 — so no two machines were identically configured, and it is remarkable that any de-facto standard emerged at all. That standard exists thanks to a handful of enthusiasts — **V.M.G., Ivan Mak, Mr.Gluk & Co.** — whose combined modifications converged on a common port layout that later emulators and the factory-built Pentagon-1024SL formalized.

Technically, the Pentagon 1024 is **not a different computer** from the Pentagon 128K — it is the same discrete-TTL design with additional DRAM, extra latch bits, and an `#EFF7` decode circuit added. The engineering elegance of the upgrade is that **all six bank-select bits end up in the single `#7FFD` port**: one `OUT` instruction pages any of the 64 banks. This article covers the paging model, the `#EFF7` control register, the video extensions, the service-ROM ecosystem, the 1024SL factory consolidation, and the programming model.

> [!NOTE]
> This article covers the **hardware platform** — the physical machine, its expansions, and its variants. For the base Pentagon 128K history and architecture, see [pentagon.md](pentagon.md). For the frame timing (320 scanlines, 48.83 Hz, zero contention), see [video_frame_pentagon.md](../../05_development/05_display_and_timing/video_frame_pentagon.md).

---

## Why 1024 KB?

The base Pentagon 128K has 8 banks of 16 KB — enough for the standard 128K memory map plus the screen buffer and TR-DOS workspace. But by 1993–1995, Russian software had outgrown 128 KB:

| Use case | RAM needed | Why |
|---|---|---|
| **TR-DOS disk caching** | 256–512 KB | Loading demos/games from disk was slow (5.25" drives at 300 KB/disk). Caching the entire disk in RAM eliminated reloads. |
| **Pro Tracker 3.x samples** | 256–1024 KB | PT3 modules with high-quality digitized samples could exceed 128 KB per song. The 1024K machine could hold an entire album in RAM. |
| **Multicolor double-buffering** | 256 KB | Two full-screen multicolor buffers (one being displayed, one being rendered) require 2 × 6912 bytes per bank — easily exceeding 128 KB with code and data. |
| **Russian RPGs and adventures** | 256–512 KB | Games like *Black Raven* (Черный Ворон) used banked data sets far larger than 128 KB. |
| **Demo megablocks** | 512–1024 KB | Multi-part demos loaded all parts into RAM at startup and switched between them via paging, avoiding disk access during the demo. |

---

## Hardware Architecture — The 1024K Upgrade

The 1024K upgrade is a **minimal hardware change** to the base Pentagon 128K. The modification consists of three additions.

### 1. Additional DRAM

The base Pentagon uses `К565РУ5` (4164-equivalent, 64 Kbit × 1) DRAM for the fixed banks. The upgrade populates the expansion RAM area with higher-density chips:

| Configuration | RAM chips | Total banks | Total RAM |
|---|---|---|---|
| Pentagon 48K | 16 × 4164 (64 Kbit × 1) | 3 | 48 KB |
| Pentagon 128K | 16 × 4164 + expansion | 8 | 128 KB |
| Pentagon 256K | + bank bit in `#7FFD` | 16 | 256 KB |
| Pentagon 512K | + two bank bits in `#7FFD` | 32 | 512 KB |
| Pentagon 1024K | + three bank bits in `#7FFD` | 64 | 1024 KB |

The `К565РУ6` (256 Kbit × 1, equivalent to 41256) was the workhorse DRAM for Pentagon expansions; a full 1024K machine needs 32 of these for the paged banks alone. Because every machine was hand-built, chip choices varied — `4464` (64 Kbit × 4) arrays and salvaged SIMM modules appear on later boards.

### 2. Extension Latch Bits in #7FFD

The critical design decision: **the extension bits live in the unused high bits of the standard `#7FFD` paging register**, not in a separate port. The full 1024K paging model:

```
#7FFD (write-only) on a Pentagon 1024:

  Bit  0-2:  RAM bank at #C000, bits 0-2        (standard 128K, banks 0-7)
  Bit  3:    Screen select (0 = Bank 5, 1 = Bank 7)
  Bit  4:    ROM select (0 = ROM 0, 1 = ROM 1)
  Bit  5:    Bank bit 5  (banks 32-63)  — ONLY while extended RAM is enabled
             otherwise: standard 48K lock (see below)
  Bit  6:    Bank bit 3  (banks 8-15, 256 KB step)
  Bit  7:    Bank bit 4  (banks 16-31, 512 KB step)

  Effective bank = (#7FFD & #07)
                 | (#7FFD & #40) >> 3      ; bit 6 -> bank bit 3
                 | (#7FFD & #80) >> 3      ; bit 7 -> bank bit 4
                 | (#7FFD & #20)           ; bit 5 -> bank bit 5 (if enabled)
                 = 0..63
```

One `OUT (#7FFD), A` therefore selects **any of the 64 banks** — a deliberate convenience. Alone Coder notes that paging through the single `#7FFD` port is *faster* than the two-port schemes used by Profi-style software (which must write `#7FFD` for the low bits and `#DFFD` for the high bits).

> [!WARNING]
> The **weights of bits 6 and 7 vary between hand-built machines**. The convention documented on zx-pk.ru and implemented by every major emulator (ZEsarUX, UnrealSpeccy, ZXMAK2) is bit 6 = bank bit 3, bit 7 = bank bit 4 — the order used throughout this article. Some builders wired the pair in reverse (bit 7 = bank bit 3). Software that only uses banks 8-15 or 16-31 monotonically is unaffected; bank-number-sensitive code should verify the mapping on real hardware.

### 3. The #EFF7 Gate and Control Port

The second added port, `#EFF7`, does **not** carry bank bits. It is a **control register** — Black_Cat's port guide calls it `PagVidTrbReg` (paging/video/turbo register). Its most important bit is the **extended-memory gate**:

```
#EFF7 bit 2  —  memory above 128 KB:
                 0 = extended RAM present (bits 5-7 of #7FFD = bank bits)
                 1 = extended RAM disabled (machine acts as plain 128K,
                     #7FFD bit 5 reverts to the standard 48K lock)
```

This gate is what makes the 1024K machine **software-compatible with everything below it**. Toggle one bit and the machine is electronically a Pentagon 128: the extra DRAM disappears from the address space, `#7FFD` bit 5 locks paging the Sinclair way, and 128K-era software (including titles that write lock values to `#7FFD`) behaves exactly as on the base machine. The Gluk Reset Service ROM (see below) flips this bit among its housekeeping duties — which is exactly why software must not assume `#EFF7` state at startup.

For the complete `#EFF7` bit layout — video modes, GigaScreen, CMOS clock — see [The #EFF7 Control Register](#the-eff7-control-register) below.

### 4. The #DFFD Parallel Wiring (Profi Compatibility)

For compatibility with software written for the Profi 1024 (see [profi.md](profi.md)), the extension latch bits are **wired in parallel** to `#DFFD` bits 0-2:

```
  #DFFD bit 0  ≡  #7FFD bit 7   (bank bit 3)
  #DFFD bit 1  ≡  #7FFD bit 6   (bank bit 4)
  #DFFD bit 2  ≡  #7FFD bit 5   (bank bit 5, when enabled)
```

Either port drives the same latch lines, so Profi-targeted software works unmodified. The Kay 1024 uses the same port for its own extension — see [kay.md](kay.md) for the differences.

### Port Decoding

| Port | Decoding (A15…A0) | Lines checked | Mirrors | Function |
|---|---|---|---|---|
| `#7FFD` | `0xxxxxxxxxxxxx0x` (Pentagon 128) | 2 (A15=0, A1=0) | 16K-wide | Paging latch |
| `#7FFD` | `01xxxxxxxxxxxx0x` (Pentagon 1024 / 1024SL; official v2.2 doc, zx-pk, emulators) | 3 (+A14=1) | 8K-wide | Paging latch |
| `#EFF7` | `1110xxxxxxxx0xxx` (1024SL v2.x, emulators) | 5 (A15-A12=`1110`, A3=0) | 2048 | Control register |
| `#EFF7` | A3=0, A12=0 minimum (Born Dead hand-builts) | 2 | ~16K | Control register |

Note that `#EFF7` decoding is **partial** on every real implementation — a direct consequence of the port being added to existing boards with a minimum of glue logic (minimum decode: A3, A12, and IOWR, reset by RESET). The two decoded lines were chosen so that the heavily-mirrored `#7FFD` writes (A3=1 and A12=1 in the canonical address) can never accidentally strobe the `#EFF7` latch.

> [!NOTE]
> The `#EFF7` port is **write-only on all original hardware** — there is no readback. Software must shadow the register in RAM (see [memory_and_io_pentagon.md](../../05_development/03_memory_and_io/memory_and_io_pentagon.md) for the standard pattern).

---

## The #EFF7 Control Register

The `#EFF7` layout evolved through two generations — the hand-built standard documented by Alone Coder in *Born Dead* #10, and the factory Pentagon-1024SL v2.x layout from the official 2006 documentation. Both are given here because both exist in the wild and in emulators.

### Hand-Built Standard (Born Dead #10, 1999)

| Bit | Function | Notes |
|---|---|---|
| 0 | **a4b** — "attribute per byte" hardware multicolor | Attributes read from `#6000`-`#77FF` instead of `#5800`-`#5AFF`, giving each 8×1 pixel stripe its own ink/paper. 1 = enabled. See [multicolor_engines.md](../../05_development/06_graphics/multicolor_engines.md). Superseded on this bit in late 2005 by the 16-colour mode — see [The 16-Colour Video Mode (16c)](#the-16-colour-video-mode-16c--every-pixel-its-own-color). |
| 1 | **512×192** monochrome mode | Doubles horizontal resolution; pixel data split between `#4000` and `#6000` areas (documented in Deja Vu #6). 1 = enabled. |
| 2 | **Extended memory gate** | 0 = RAM above 128K present, 1 = disabled (see above). |
| 3 | Unused (proposal: read-only cache control) | 0 = writable, 1 = write-protected — never widely adopted. |
| 4 | **GigaScreen** — hardware screen interleaving | Alternates screen 0/1 every raster line (see below). Rarely implemented; the game *Homer Simpson in Russia* drives it via `#FFFC` instead of `#EFF7`. |
| 5-6 | Reserved for ROM-disk (proposals only) | Alone Coder suggested repurposing: bit 5 = Sound Blaster enable, bit 6 = 384×304 mode (per ZX-Guide 2). |
| 7 | **Gluk CMOS** — real-time clock enable | 1 = CMOS ports active (schematic in Deja Vu #8 — which also prints the port as `#FFFC`). 1 = enabled. |

### Factory Standard (Pentagon-1024SL v2.2, official documentation 2006)

| Bit | Function | Notes |
|---|---|---|
| 0 | **16 colour** mode | Every pixel gets its own color (standard 15-color ULA palette with BRIGHT) — four 6 KB screen areas compose one 256×192 image. Direct factory adoption of Alone Coder's v1.1 schematic; see [The 16-Colour Video Mode (16c)](#the-16-colour-video-mode-16c--every-pixel-its-own-color). 0 = off, 1 = on. |
| 1 | Unused | — |
| 2 | **128K mode** | 1 = block memory above 128K; `#7FFD` bit 5 becomes the 48K lock. |
| 3 | **ROM disable** | 1 = RAM page 0 projected at `#0000`-`#3FFF` instead of ROM. |
| 4 | **TURBO control** — *inverted* | 0 = 7 MHz turbo ON, 1 = 3.5 MHz normal. |
| 5 | Unused | — |
| 6 | **384×304** mode | Full-screen image without border. 0 = off, 1 = on. |
| 7 | Unused on SL v2.2 | (CMOS enable on other variants; see hand-built bit 7.) |

The official documentation adds that all other I/O ports (Kempston, ZX LPRINT III, border, AY, Beta 128 FDC) keep their standard ZX Spectrum configuration.

> [!WARNING]
> **The two layouts are not compatible.** Hand-built machines put multicolor at bit 0 and 512×192 at bit 1; the SL v2.x puts 16-colour at bit 0 and turbo at bit 4. The bit-0 story has a third wrinkle: on hand-builts, bit 0 itself *changed meaning* in late 2005 — from a4b multicolor to the 16-colour mode (per Info Guide #8; the a4b-only *Hexagonal Filler* moved to bit 5 in its second release). Video-mode software must target the specific generation or probe. Modern recreations pick either layout — the Pentagon-4096 follows the SL convention (with bit 5 = multicolor), emulators generally implement the paging bits (2 and 3) only.

### GigaScreen — Hardware Screen Interleaving

The `#EFF7` bit 4 feature (hand-built standard) interleaves the two screen banks line by line: the screen-select signal C35 (normally `#7FFD` bit 3) is XORed with an 8 kHz square wave:

```
  C35 = (bit4 & 8kHz) XOR C35
```

Odd scanlines show screen 0, even scanlines show screen 1 (or vice versa) — at 48.83 Hz field rate the eye merges both images, effectively doubling brightness and enabling mixed-color dithering without software line-switching. The same idea later became a standard feature on the Kay 2006, ZX Evolution and TS-Conf. On a 384×304-capable machine the combination yields "X-Color" effects with reduced flicker.

### Video Controller Internals — A13V and C35 Priority

For builders, Alone Coder documented the order in which the video extensions must capture the video controller's address lines: **A13V** (address line 13 of the video address multiplexer, normally grounded) and **C35** (the screen-page select bit, normally `#7FFD` bit 3):

```
  A13V capture order:  a4b forms → SounDrive sums → 512x192 switches → 384x304 switches
  C35 capture order:   384x304 switches and mixes → GigaScreen XORs
```

If 384×304 is built on a multiplexer (`КП11`/`КП12`), `#EFF7` bit 6 must route either the existing A13V (bit = 1) or ground (bit = 0), and the resulting signal OR-ed into C35 — combining bit 6 with the 512×192 mode then yields **768×304**.

---

## The 16-Colour Video Mode (16c) — Every Pixel Its Own Color

In October 2005, Alone Coder published a schematic that gave the Pentagon something Sinclair never built: **a full-screen video mode where every pixel has its own color**. The 16-colour mode (**16c**, Russian *16-цветный режим*; SpeccyWiki entry "16col") reinterprets the four standard screen areas as one 24 KB, 4-bit-per-pixel bitmap — 256×192 pixels, each selecting from the standard ULA palette with BRIGHT (15 distinct colors; the article's "16" counts bright black). It costs **zero per-frame CPU time** — no raster interrupts, no attribute races, no BIFROST-style playfield limits. The whole mode is switched by a single bit, `#EFF7` bit 0 — the exact bit the factory Pentagon-1024SL v2.x adopted as its "16 colour" control in 2006.

> [!NOTE]
> Sources: Alone Coder, *"16-цветный режим v1.1"* — worked out in the ZX.SPECTRUM echo conference (23 and 30 October 2005), published in **Info Guide #8** (30.10.2005; v1.1 corrects an error in v1.0's defect-fix schematic), with a video-viewing addendum in **Info Guide #9**. Software census and mode description: [SpeccyWiki, "16col"](https://speccy.info/16col).

### History — How Bit 0 Changed Meaning

The mode descends directly from the **hardware multicolor** modification (a4b — attribute per byte), documented in the hand-built `#EFF7` standard above: attributes are fetched from `#6000`-`#77FF` instead of `#5800`-`#5AFF`, so every 8×1 pixel stripe gets its own ink/paper pair. Alone Coder's v1.1 article states the 16c mode "is based on hardware multicolor — all 3 standard circuits are used, plus the optional separate-BRIGHT circuit." Nothing from the a4b schematic is thrown away; the 16c mode only adds video-controller address lines that turn the *attribute* read path into a second *pixel* read path.

As a software platform, a4b went nowhere — SpeccyWiki records exactly **one** program supporting it, *Hexagonal Filler* (whose second release moved a4b to bit 5). The 16c mode replaced a4b on bit 0 in late 2005 and became the mode people actually used: within four years it had games, demos, visual novels, a video player, and an operating system (see [Software for 16c](#software-for-16c)). When Alexey Zhabin froze the factory standard in the Pentagon-1024SL v2.x (2006), bit 0 kept the 16c function — which is why the SL documentation and this article's factory table both read "bit 0 = 16 colour."

> [!WARNING]
> Early-1990s hand-builts (per Born Dead #10) expose **a4b** on `#EFF7` bit 0; post-2005 machines expose **16c**. Writing bit 0 without knowing which generation the board is produces a very different screen. See the compatibility warning in [The #EFF7 Control Register](#the-eff7-control-register).

### Screen Organization — Four Areas, One 4-Bit Bitmap

One 16c screen is four standard 6,144-byte screen areas, two DRAM banks deep:

| Area | Address range | DRAM bank | Stripe bytes covered |
|---|---|---|---|
| 1 | `#C000`-`#D7FF` | bank 4 (paged at `#C000`) | pixels 0-1 of each 8-pixel stripe |
| 2 | `#4000`-`#57FF` | bank 5 (standard) | pixels 2-3 |
| 3 | `#E000`-`#F7FF` | bank 4 | pixels 4-5 |
| 4 | `#6000`-`#77FF` | bank 5 | pixels 6-7 |

The **second screen** (shadow) mirrors this exactly in banks 7 (`#4000`/`#6000`) and 6 (`#C000`/`#E000`) — so both Pentagon screens exist in 16c, and the standard `#7FFD` bit 3 selects between them as usual.

Key properties:

- **4 bits per pixel** — every byte holds **two horizontally adjacent pixels**, each `BRIGHT`+RGB.
- **Standard Spectrum addressing** — the offset inside each 6 KB area is the ordinary interleaved screen layout (thirds of 64 lines, 8-pixel sub-rows); unlike the ATM Turbo's linear layout, no address translation is needed.
- **One line of a character cell = four bytes at the same offset in four different areas** — in stripe order `#C000`, `#4000`, `#E000`, `#6000`.
- Total: 4 × 6,144 = **24,576 bytes per screen** — 12 KB used of each 16 KB bank (each bank's `#5800`-`#5FFF` attribute window and last 2 KB are unused).

#### The Addressing, Byte by Byte

The v1.1 article's address map for screen 0 (one 8×8 cell boxed; each row is one scanline, column offsets `#00`-`#1F`):

```
#c000 #4000 #e000 #6000 ┃ #c001 ... #601f
#c100 #4100 #e100 #6100 ┃ #c101 ... #611f
........................┃...............
#c700 #4700 #e700 #6700 ┃ #c701 ... #671f
────────────────────────┘
#c020 #4020 #e020 #6020   #c021 ... #603f
........................................
........................................
#d7e0 #57e0 #f7e0 #77e0   #d7e1 ... #77ff
```

One byte = two pixels, packed in the same field order the **ATM Turbo uses for its EGA-style 320×200×16 mode** — which is exactly why one source can compile a game for both machines (see [atm_turbo.md](atm_turbo.md) and the [Software for 16c](#software-for-16c) section):

| Bit | Field | Pixel | Meaning |
|---|---|---|---|
| D7 | `Yr` | right | BRIGHT |
| D6 | `Yl` | left | BRIGHT |
| D5 | `Gr` | right | Green |
| D4 | `Rr` | right | Red |
| D3 | `Br` | right | Blue |
| D2 | `Gl` | left | Green |
| D1 | `Rl` | left | Red |
| D0 | `Bl` | left | Blue |

The Info Guide notation for the same byte is `%IiGRBgrb`, where `IGRB` (intensity+RGB) is the *right* pixel. Each pixel selects one of 8 colors, times 2 for BRIGHT — 15 distinct colors, because bright black is still black.

Since pixels come in pairs, a single odd pixel cannot be set in isolation — write both halves, or read-modify-write preserving the neighbor.

#### Enabling the Mode and Writing a Stripe

```z80
; --- Enable 16c, paint one 8-pixel stripe (screen 0, line 0, cell 0) ---
; Stripe byte order: #C000 (px 0-1), #4000 (px 2-3), #E000 (px 4-5), #6000 (px 6-7)
; Left pixel = bright red (Y=1,R=1,G=0,B=0), right pixel = blue (Y=0,R=0,G=0,B=1)

        LD   A,%00000001        ; bit 0 only — keep other #EFF7 bits as they were!
        LD   BC,#EFF7
        OUT  (C),A              ; 16c ON

        LD   A,#04              ; ROM 0, screen 0, low bank bits = 4
        LD   BC,#7FFD
        OUT  (C),A              ; bank 4 at #C000-#FFFF (bank 5 already at #4000)

        LD   L,#00              ; offset 0 = line 0, cell 0 (standard screen addr)
        LD   H,#C0
        LD   (HL),#4A           ; %01001010: px 0-1 = bright red | blue
        LD   H,#40
        LD   (HL),#4A           ; px 2-3
        LD   H,#E0
        LD   (HL),#4A           ; px 4-5
        LD   H,#60
        LD   (HL),#4A           ; px 6-7  — one full 8-pixel stripe painted

        XOR  A                 ; restore: 16c OFF, bank 0 at #C000
        LD   BC,#EFF7
        OUT  (C),A
        LD   BC,#7FFD
        OUT  (C),A
```

> [!WARNING]
> Half of every stripe lives in bank 4 (or 6 for the shadow screen). Code that assumes the whole 256×192 bitmap sits in one 16 KB bank will silently paint only the even stripes. Page the bank once at init and leave it — but note bank 4 at `#C000` is also where disk cache and demo parts often live; plan your bank allocation (see [Bank Allocation Strategy](#bank-allocation-strategy)).

Note what is *gone* in this mode: the attribute file. The ULA's attribute fetch path now delivers pixel data (see the FLASH-mask circuit below), so `ATTR`-address math, FLASH and the ink/paper split have no meaning while bit 0 is set.

### The Seven Circuits

The v1.1 article specifies seven modifications to the Pentagon video section. Signal names are the standard Pentagon schematic designators (D10 — ТМ2 flip-flop, D17 — video address multiplexers, D3 — pixel-clock counter, КП11/КП12 multiplexers):

| # | Signal | Formation | Purpose |
|---|---|---|---|
| 1 | `/BUSRQ` (CPU pin) | wired-OR of `D10/8` and `/eff7b0` | the mode joins the a4b bus-request line, letting the video controller run its doubled fetch pattern |
| 2 | `A13V` (D17/11) | wired-AND of `eff7b0` and the 7/8 MHz tap (D3/2) | video-mux address line 13 — selects the `#4000` vs `#6000` half within the bank |
| 3 | `A14V` aka `P0V` (D17/14) | wired-OR of `/eff7b0` and the 7/4 MHz tap (D3/3) | video-mux address line 14 — the *odd-page* select (bank 4 vs 5, 6 vs 7) |
| 4 | FLASH mask (D6/11) | КП11 switches in 3.5 MHz (D1/8) | the FLASH mask becomes a constant phase — its old bit position now carries pixel data |
| 5 | second BRIGHT (D47/11) | КП11 switches attribute bit 7 (D7/12) | the separate-BRIGHT circuit inherited from the multicolor scheme |
| 6 | attribute read strobes | primary buffer D37/11 ← 3.5 MHz (D45/2); secondary buffer D40/11 ← 3.5 MHz delayed 90° (D1/9) | phases the two screen-buffer reads |
| 7 | ATTR/MASK addressing select | unchanged from the a4b schematic (c29 → D8/3, c30 → D14/1, via `eff7b0` muxes) | routes the address latches between attribute and mask fetches |

Build notes from the article:

- Only **one new chip** is required — a **КР1533КП11** (74ALS157/74LS157-equivalent quad 2:1 multiplexer), which commutates circuits 4, 5 and 6. Everything else reuses the a4b ("attribute per byte") wiring — "nothing from the a4b schematic is thrown away."
- If a **384×304** modification is fitted, circuits 2 and 3 must attach **upstream** of it — the 384×304 scheme already mixes in the old A13V, and circuit 3 must precede its C35 mixing.
- The signals exist in similar form on many other ZX models, but the article documents Pentagon only.

> [!WARNING]
> The table above is a summary, not a build sheet. The gate-level wiring in v1.0's defect-fix schematic contained an error — **build from the v1.1 text only** (link in [References](#references)).

### Known Defects and the v1.1 Fix

On a Pentagon built to v1.0, two border-zone defects were observed:

1. The **rightmost 8 pixels** of each line are fetched from start-of-line + 8 bytes (the doubled fetch wraps).
2. The **leftmost 4 pixels** are affected by CPU activity (the bus is not yet quiet when the first fetch fires).

The v1.1 fix is a small retime circuit: an additional **ТМ2** (7474-type) flip-flop — clocked by the border address signal (pin 12), D input gated with `eff7b0` — whose output feeds circuit 1 in place of `D10/8`. The bus request is then asserted at a defined point in the border window instead of racing the CPU. The cost of the fix is blanking: **3 pixels on the left and 5 on the right become invisible**, leaving a defect-free **248×192** working area — still more usable area than most multicolor-engine playfields, at zero CPU cost.

> [!WARNING]
> Requires bus-request timing awareness. While 16c is active, the doubled video fetch pattern runs through `/BUSRQ`, so the classic Pentagon property of *zero CPU stalls during screen fetch* no longer holds during the 192 visible lines. Naive T-state budgets computed for the unmodified machine will be optimistic in this mode (the v1.1 article does not quantify the loss; measure on target hardware or in UnrealSpeccy).

### Software for 16c

Despite a four-year run, the mode accumulated a real software library — games, Transman's visual-novel ports, and an entire video-player toolchain:

| Title | Year | Author | Notes |
|---|---|---|---|
| **Pang 16C** | 2005 | Alone Coder | The demo piece: compiles from **one source** for Pentagon 16c *and* ATM Turbo 2's 16-colour mode (keys or auto-detect) |
| **Time Gal** | 2006 | Alone Coder | Digitized-animation game port |
| **Ball Quest** | 2006 | Alone Coder | — |
| **Big L** (demo version) | — | Alone Coder | — |
| **Season of the Sakura** | 2007 | Transman | Visual novel port |
| **Book of the Dead: Lost Souls** (Книга мёртвых: Потерянные души) | 2009 | Transman | Visual novel port |
| **Three Sisters' Story** | 2010 | Transman | Visual novel port |

Demos and intros: *16Cbiver* (30.10.2005, Alone Coder — the mode's first release companion), *Borntro 2008* and *vD16F* (breeze, 2008), *NedoDemo* (27.06.2008, Alone Coder), *ASCiI'2008 Demoparty Invitation* (22.10.2008, breeze), *The Link* (28.08.2009, Alone Coder), *ART* (2009, DDp — with DDp-palette support).

System software and tools:

| Tool | Date | Author | Purpose |
|---|---|---|---|
| **view102** | 11.2005 (*Info Guide* #8) | Alone Coder | Viewer for 102-colour images using a palette computed by Diver; loads an unpacked 256-colour indexed BMP sharing the viewer's file name — many picture+viewer pairs fit on one TRD |
| **16CCON** | 2005 | — | Screen converter for *Pang 16C* |
| **SOUL** | 01.2006 (*Info Guide* #9) | Alone Coder | Video player — the reason *Info Guide* #9 carried a video-viewing addendum to the schematic |
| **DNA OS** | 2007 | ZET-9 | Operating system using the mode |
| **Little Viewer** | 2007 | SAM Style | Picture viewer |

The portability trick is worth restating: the 16c byte layout is **field-identical to ATM Turbo's** 16-colour mode — the v1.1 article states the intra-byte bit order is the same (`%IiGRBgrb`) and calls the four-area addressing "analogous to ATM's" (`#C000+`, `#4000+`, `#E000+`, `#6000+`). The line ordering differs: ATM keeps rows linear, while the Pentagon version deliberately keeps the standard Spectrum row interleave — "standard linework, as in the ordinary Spectrum mode." A converter, compile-time keys, or runtime auto-detection bridges the two — which is exactly how *Pang 16C* shipped for both machines from one source.

### Platform Support and Disposition

| Implementation | 16c support |
|---|---|
| **Pentagon-1024SL v2.x** (factory, 2006) | `#EFF7` bit 0, documented in ver22 — the factory standard frozen by this machine |
| Post-2005 hand-builts | Bit 0 per Info Guide #8 v1.1 |
| Emulators | **UnrealSpeccy**, **Speccy**, **ZEmu** (per SpeccyWiki) |
| Pentagon-4096 | Follows the SL register convention (see warning in [#EFF7 Control Register](#the-eff7-control-register)) |

The mode is **historically closed**: hardware development stopped, and the surviving software was reworked for the ATM Turbo 2, whose own 16-colour mode (plus 320×200 resolution and hardware scroll) absorbed the niche. For new Soviet-track work targeting per-pixel color, ATM Turbo 2+ is the living target; 16c matters today for preservation, emulation accuracy, and running the existing library.

### When to Use / When NOT to Use

| Criterion | Pentagon 16c | ATM Turbo 320×200×16 | Software engines (BIFROST\*/NIRVANA+) | ULAplus |
|---|---|---|---|---|
| When to use | Pentagon 1024/1024SL target, full-screen per-pixel color, no CPU budget | ATM 2/2+ target; want 320×200 + scroll | Any stock Spectrum; active cross-platform tooling | Modern FPGA/emulator; palette depth on the stock attribute model |
| Resolution / colors | 256×192, 15 colors per pixel | 320×200, 16 of 64 RGBI | 8×1 or 8×2 cells, 15 colors | 8×8 cells, 64 colors |
| CPU cost | ~0 (hardware fetches; bus-shared) | ~0 | 30-50% of frame | ~0 |
| Availability today | Legacy; emulated (UnrealSpeccy/Speccy/ZEmu) | Active Soviet-track standard | Active, mainstream | Active on modern hardware |

**Modern analogies.** The 16c screen is a **4-bit packed framebuffer with 2-pixel granularity** — the same nibble-packing trick as PC VGA's mode 13h (which packed two 4-bit pixels per byte in Mode X variants) rather than EGA's four-bitplanes model. The four-area bank interleave is a banked-framebuffer layout; the two full 16c screens in banks 4-7 are effectively **hardware double buffering**, something the stock Spectrum never offered.

### Pitfalls

1. **The Wrong Generation** — writing `#EFF7` bit 0 on a pre-2005 hand-built switches *a4b multicolor*, not 16c; on the SL v2.x it switches 16c *and nothing else matches the hand-built bit map*. Detect the machine generation or target one explicitly.
2. **The Half-Painted Screen** — drawing only through `#4000`/`#6000` and wondering why every other stripe pair is black: bank 4 (shadow: bank 6) must be paged at `#C000` first.
3. **The Lone Pixel Write** — a byte always colors two adjacent pixels; preserving an odd pixel requires read-modify-write, and reads hit the same four-area interleave.
4. **The Safe-Area Ignorer** — without the v1.1 fix circuit, the right 8 and left 4 pixel columns are corrupt; with it, 3+5 columns are blanked. Center the composition in 248×192 on hardware.
5. **The Attribute Ghost** — ROM/BIOS attribute routines (ATTR-address math, FLASH toggling) corrupt the bitmap while bit 0 is set.

---

## ROM and Service Software

Hand-built 1024K machines standardized on a two-ROM software stack, both documented in Born Dead #10.

### TR-DOS v5.13Fm with RAM-Disk

The disk OS is a normal TR-DOS 5.13 with **accelerated track positioning** — a seek optimization that unfortunately breaks *Monster Commander*. Its signature feature: **drive D: is a RAM-disk** living in the extended banks. A program that uses the `#3D13` file-entry hook can be copied to `D:` and then runs at RAM speed — a popular trick on 1024K machines. See [trdos.md](../../04_operating_systems/trdos.md) and [beta_disk_interface.md](../../03_io/storage/beta_disk_interface.md).

### Gluk Reset Service v5.3K

A resident service OS (by Renat Mamedov, `2:5026/5.46@Fidonet`) burned into an unused page of the 27512 ROM — usually page 0 — which the machine enters on RESET:

- **Hot reset combos**: `RESET`+`1` → exit to STS (the STS debugger — see [debugging tools](../../09_toolchain/debugging.md)); `RESET`+`Space` → TR-DOS. Invaluable when a program under development hangs.
- **Screen salvage**: can view the display of the interrupted program and save it to disk (the 5.3K version has a bug affecting screen 0).
- **Disk catalog rescue**: saves and restores the disk catalog on track 161.
- **Boot + Perfect Commander 1.52** built in.
- Controls the `#EFF7` extended-memory gate among its housekeeping — one more reason software must not assume the gate state.

---

## The 32K LPRINT III Cache

Many 1024K machines carry a 32 KB **SRAM cache** for the `#0000`-`#3FFF` ROM area, built to the ZX LPRINT III schematic — usually a Western `11C256` (32K × 8). In turbo mode, code executing from this area incurs **no WAIT states**, which is what makes 7 MHz upgrades practical for ROM-heavy software.

```
  IN A,(251)   ; enable cache
  IN A,(123)   ; disable cache
```

The upper address line of the SRAM is switched by the **DOSEN** signal (ROM pin 15), selecting which 16 KB half of the cache shadows the currently active ROM context (BASIC vs TR-DOS). The Pentagon-1024SL v2.x integrated the LPRINT III port and cache onto the motherboard.

> [!WARNING]
> Some programs that use the **General Sound** card conflict with the LPRINT III decode. Born Dead's advice to software authors: detect the LPRINT III device *first* (it was widespread), and only then probe for GS. See [gs_general_sound.md](../../06_sound/hardware/gs_general_sound.md).

---

## Standard Peripheral Set

### Kempston Mouse

By the late 1990s the Kempston mouse was considered standard equipment on a serious Pentagon 1024 — the SL v1.x even integrated the controller on-board. The interface exposes three read ports:

| Port | Function | Notes |
|---|---|---|
| `#FBDF` | X coordinate | 8-bit counter, wraps at 0/255 |
| `#FFDF` | Y coordinate | **counts bottom-up** (inverted vs screen coordinates) |
| `#FADF` | Buttons | 0 = pressed, 1 = released; left = D0, right = D1, middle = D2 (CREATE SOFT order) |

The button-order convention is credited to CREATE SOFT; the mirrored layout was devised by Zonov (see [mouse.md](../../03_io/peripherals/mouse.md) for the full protocol and wiring, published in ZX Format #5).

**Detecting the mouse** (per Born Dead #10): the mouse is considered present when the three port reads are **not all equal** — an undriven bus returns the same idle value everywhere, while counters and buttons decorrelate quickly. Failure probability 1/65536:

```z80
; Kempston mouse presence test (algorithm from Born Dead #10)
; Returns: A = 1 if mouse present, A = 0 if not
; Destroys: AF, BC, E

DetectMouse:
        HALT                    ; wait for a quiet, stable bus period
        LD   BC,#FADF
        IN   A,(C)              ; A = buttons
        LD   E,A                ; E = sample 1
        LD   B,#FF
        IN   A,(C)              ; B=#FF, C=#DF -> port #FFDF = Y
        CP   E
        JR   NZ,.present        ; Y != buttons -> bus is being driven
        LD   B,#FB
        IN   A,(C)              ; port #FBDF = X
        CP   E
        JR   NZ,.present
        XOR  A                  ; all three equal -> nothing there
        RET
.present:
        LD   A,1
        RET
```

### Sound

- **AY-3-8910/12 or YM2149F** — the standard music chip (all Pentagon boards).
- **COVOX** — considered mandatory; a bare 8-bit DAC on the printer-port decode.
- **SounDrive v1.51** — four-channel DAC expansion with COVOX emulation (schematic in Deja Vu #1); see [covox_sounDrive.md](../../06_sound/hardware/covox_sounDrive.md).
- **General Sound** — theoretically attachable (and standard on later NemoBus machines); see [gs_general_sound.md](../../06_sound/hardware/gs_general_sound.md).
- **DMA UltraSound Card** — predicted to work; no confirmed reports at the time.

### Modem, Drives, and Storage

- **Modem**: Hayes-compatible per Kondratiev's schematic (Oberon #4) at 14400-57600 baud.
- **Disk**: Beta 128 interface + TR-DOS, 5.25" and 3" drives. Born Dead's drive rankings: **Robotron** recommended, **Teac** tolerable but slow and short-lived, **Mitsumi 1M** the best observed.
- **HDD**: *no standard hard-disk interface existed* for the platform at the time — the standard workaround was copying floppy images into extended RAM (the Amiga-style RAM-disk approach). Standard controllers (Z-Controller, NemoIDE) arrived with the SL/NemoBus era; see [ide_interface.md](../../03_io/storage/ide_interface.md) and [sd_interface.md](../../03_io/storage/sd_interface.md).

---

## Pentagon 1024SL — the Factory Consolidation

The **Pentagon-1024SL** is the lineage that turned the hand-built 1024K standard into a manufactured product, designed by **Alexey Zhabin** and supported by the NedoPC project (full schematics, PCB files and CPLD firmware are published at [pentagon.nedopc.com](http://pentagon.nedopc.com/)):

| Version | Year | Highlights |
|---|---|---|
| **SL v1.x** | 2004-2005 | 1024 KB RAM, 3.5 MHz only, integrated Kempston **mouse** controller, 2× ZX-BUS slots; P-CAD 2001 board files published |
| **SL v2.x** | 2006 | 3.5/**7 MHz** turbo (`#EFF7` bit 4), 16-colour and 384×304 video modes, integrated ZX LPRINT III port + cache, YM2149F, Beta 128 FDC on КР1818ВГ93, RGB SYNC 75Ω + PAL/NTSC coder (MC1377P), EPM7128/EPM3032 CPLDs with open firmware |
| **2.666 / LE / FE** | 2007-2023 | Modern successors: Cyclone II FPGA + 512K-2M SRAM (2.666LE, 2009), Cyclone III + 8 MB SDRAM + ARM service MCU (2.666FE, 2023); VGA/HDMI, PS/2, SD, Ethernet |

The SL v2.x is the machine that froze the factory `#7FFD`/`#EFF7` layout documented above, and it is the model that "Pentagon 1024" emulator presets implement.

### Programming the SL v2.x

| Feature | Port | Notes |
|---|---|---|
| Extended RAM gate / 128K mode | `#EFF7` bit 2 | 0 = 1 MB enabled, 1 = plain 128K |
| RAM page 0 at `#0000` | `#EFF7` bit 3 | 1 = RAM replaces ROM — useful for RAM-resident systems and debuggers |
| Turbo 7 MHz | `#EFF7` bit 4 | **0 = turbo ON, 1 = OFF** (inverted — easy to get wrong) |
| 16-colour video | `#EFF7` bit 0 | 0 = off, 1 = on |
| 384×304 borderless video | `#EFF7` bit 6 | 0 = off, 1 = on |

> [!WARNING]
> Writing `#7FFD` bit 5 while extended RAM is **disabled** (`#EFF7` bit 2 = 1) engages the 48K lock — on the SL v2.x the lock blocks the port and *all* of its functions until a hardware RESET. Enable the extended RAM gate before any bit-5 banking, and treat `#EFF7` state as unknown at program start.

---

## Programming Model

### Detecting RAM Above 128K — Pentagon 512 vs 1024

There is no ROM routine to query RAM size. The canonical method is **write-and-verify** across candidate banks — but on the Pentagon there is a subtlety that makes the test safe. Per Born Dead #10: the 48K lock (`#7FFD` bit 5) only engages **when memory above 128K is disabled** (`#EFF7` bit 2 = 1). Clear the gate first, and bit 5 becomes an ordinary bank bit that can be toggled freely. The test ladder below only ever writes bit 5 *after* bits 6/7 have proven that extended-memory hardware exists, so a plain 128K machine never gets locked:

```z80
; DetectPentagonRAM — RAM size on a Pentagon-family machine
; Prereq: machine confirmed as Pentagon via timing (see clone_timing.md)!
; Returns: A = 1, 2, 4 or 8  (RAM size in 128K units)
; Destroys: AF, BC, HL; moves SP temporarily (restored on exit — the temp
;           stack at #6000 clobbers a few attribute bytes at #5FFA-#5FFF)
; Note: 1/256 false positive per step from garbage matching the signature;
;       write a second signature byte for 1/65536 if that matters.

BANK_M  EQU #5CC5               ; ROM shadow copy of #7FFD
SAVSP   DEFW 0
SAV7F   DEFB 0

DetectPentagonRAM:
        DI
        LD   (SAVSP),SP
        LD   SP,#6000            ; temp stack in fixed bank 5 (#4000-#7FFF)

        XOR  A
        LD   BC,#EFF7
        OUT  (C),A               ; extended RAM ON; bit 5 of #7FFD = bank bit

        LD   A,(BANK_M)
        AND  #1F                 ; keep bank/screen/ROM bits, drop lock
        LD   (SAV7F),A

        LD   HL,0                ; result = 1 x 128K so far
        LD   A,#80               ; test #7FFD bit 7 (bank bit 3, 256K)
        CALL .TryBit
        JR   NC,.done            ; NC = bit responded
        ADD  HL,HL               ; 1 -> 2
        LD   A,#40               ; test bit 6 (bank bit 4, 512K)
        CALL .TryBit
        JR   NC,.done
        ADD  HL,HL               ; 2 -> 4
        LD   A,#20               ; test bit 5 (bank bit 5, 1024K)
        CALL .TryBit
        JR   NC,.done
        ADD  HL,HL               ; 4 -> 8
.done:  ; fall through with result in L (units of 128K)

        LD   A,(SAV7F)           ; restore #7FFD (bank 0 context)
        LD   BC,#7FFD
        OUT  (C),A
        LD   (BANK_M),A
        LD   SP,(SAVSP)
        LD   A,L                 ; A = size in 128K units
        EI
        RET

; --- TryBit: test one extension bit (A = #80, #40 or #20) ---
; Returns CY set = bank responded, NC = no RAM behind this bit
.TryBit:
        PUSH HL
        PUSH AF
        LD   B,#7F
        LD   C,#FD
        OUT  (C),A               ; page candidate bank (ROM 0 / screen 5 forced)
        LD   HL,#C000
        LD   (HL),#A5            ; signature into candidate bank
        XOR  A
        OUT  (C),A               ; page bank 0 back in
        LD   A,(HL)
        CP   #A5
        JR   Z,.fail             ; same bank as 0 -> extension not implemented
        POP  AF                  ; A = candidate bit again
        PUSH AF
        OUT  (C),A               ; page the candidate bank back in
        LD   A,(HL)
        CP   #A5
        JR   NZ,.fail            ; signature lost -> no real RAM behind the bit
        POP  AF                  ; carry must be set AFTER the POPs to survive
        POP  HL
        SCF                      ; CY = 1: bit responded
        RET
.fail:  POP  AF
        POP  HL
        AND  A                   ; CY = 0: no response
        RET
```

> [!WARNING]
> This routine assumes Pentagon-style extended paging. On non-Pentagon machines `#EFF7` may be decoded differently or not at all, and the `#7FFD` extension bits mean other things (Scorpion: nothing; Profi: uses `#DFFD`). Always run a broader machine-detection routine first — see [clone_timing.md](clone_timing.md). Also note: on early-1990s 256/512K boards built *without* the `#EFF7` gate circuit, the final bit-5 probe can engage the 48K lock (the size result stays correct, but a RESET is then needed). All post-2000 implementations — 1024SL, FPGA cores, emulators — gate bit 5, making the probe safe.

### Bank Allocation Strategy

The 64 banks are typically allocated as follows by demoscene and game code:

```
Banks 0-7    -> Standard 128K bank space (via #7FFD bits 0-2 alone)
                Bank 0,1,3,4,6: general code/data
                Bank 2: fixed at #8000 (ROM-compatible)
                Bank 5: fixed at #4000 (screen bank)
                Bank 7: shadow screen
Banks 8-31   -> Extended data (samples, graphics, level data)
Banks 32-63  -> Disk cache / RAM-disk / reserved
```

Because all six bank bits live in `#7FFD`, sequential access to extended data costs **exactly one `OUT` per bank switch** — no `#EFF7`/`#DFFD` writes are needed once the extended-memory gate is clear. Set the gate once at init, then treat `#7FFD` as a plain 6-bit bank register.

### Pitfall: Mixed Full and Partial #FD Addressing

Born Dead #10 documents a classic compatibility bug: some programs switch banks quickly using **partial addressing** (any port of the form `xxFD`, one `OUT (n), A` with the bank number patched into A0-A2... and often bit 6 set "so it works on Scorpion"), but **fill** those banks using **full** `#7FFD` addressing. The two phases then select *different* banks — on a 512K/1024K machine the loader writes one bank while the player reads another, and the program corrupts itself. Pentagon 512-1024 owners had to disable the upper memory (set the `#EFF7` gate) while running such software.

**The rule**: if you use partial `xxFD` addressing anywhere, use it *everywhere* — never mix addressing widths for the same latch.

### The #EFF7 Readback Proposal (Historical Note)

Alone Coder proposed making `#EFF7` readable: unimplemented bits (no device behind them) should read as 1, implemented bits should return their written state — making the whole feature set software-detectable, with manual configuration as the fallback where readback does not exist. Original hardware never adopted this; on real machines reading `#EFF7` returns an undefined bus value. Modern machines (e.g., Pentagon-4096) solve detection through their own BIOS registers instead.

---

## Pentagon 1024 vs Other Large-RAM Clones

| Clone | Max RAM | Extended paging | Notes |
|---|---|---|---|
| **Pentagon 1024 / 1024SL** | 1024 KB | `#7FFD` bits 5-7 (single-port) + `#DFFD` parallel; `#EFF7` = gate/features | Most popular 1 MB clone; de-facto Russian demoscene standard |
| **Kay 1024** | 1024 KB | `#7FFD` bits 0-2 + `#DFFD` bits 0-2 | Nemo-bus expansion; see [kay.md](kay.md) |
| **Scorpion ZS-1024** | 1024 KB | `#1FFD` + ProfROM | GMX expansion adds 2 MB; see [scorpion.md](scorpion.md) |
| **ATM Turbo 2+** | 1024 KB | `#7FFD` + `#FDFD` | Own paging model for CP/M modes; see [atm_turbo.md](atm_turbo.md) |
| **Profi 1024** | 1024 KB | `#7FFD` + `#DFFD` bits 0-2 | The Pentagon's parallel `#DFFD` wiring exists precisely for this software; see [profi.md](profi.md) |

The Pentagon's single-port paging is the most widely supported extended scheme in the Russian software ecosystem — software targeting "Pentagon 1024" typically also runs on Kay and Profi (both share `#DFFD` bits 0-2 semantics).

---

## Modern Recreations

The original Pentagon 1024 hand-builts are aging, but the platform is one of the best-documented Soviet clones — every major emulator and FPGA platform supports it:

| Project | Type | Pentagon 1024 support |
|---|---|---|
| **Pentagon 2.666 LE / FE** | Real Z80 + FPGA glue (NedoPC, 2009-2023) | Full — the direct factory successor line; open schematics and firmware |
| **ZX Evolution (TS-Conf)** | Real Z80 + CPLD | Full — Pentagon-compatible with extensions; see [zx_evo.md](../newgen/zx_evo.md) and [ts_conf.md](../newgen/ts_conf.md) |
| **MiST / MiSTer (Pentagon core)** | FPGA | Full — cycle-accurate Pentagon 1024 core; see [mist_mister_core.md](../../11_emulation/fpga/mist_mister_core.md) |
| **Unreal Speccy / ZXMAK2 / ZEsarUX** | Software emulator | Full — implement `#7FFD` bits 5-7 with the `#EFF7` gate (ZEsarUX documents the zx-pk layout in `mem128.c`) |
| **ZX-Uno** | FPGA (Cyclone IV) | Full — Pentagon 1024 core included; see [zx_uno.md](../newgen/zx_uno.md) |
| **Pentagon LEO 1024K** | Discrete TTL recreation (2024-2025) | Full — modern hand-buildable board, open files on GitHub |
| **Pentagon-4096** | Discrete TTL + AVR (2020s) | Multi-standard — switchable Pentagon/Profi/Kay paging schemes up to 4 MB |

For software development, code that runs on one Pentagon 1024 implementation runs on all of them — provided it sticks to the single-port `#7FFD` model and the emulator-standard bit 6/7 weighting.

---

## Cross-References

- [Pentagon 128K (base)](pentagon.md) — the original 1989 design, history, architecture, video timing
- [Pentagon memory & I/O ports](../../05_development/03_memory_and_io/memory_and_io_pentagon.md) — register-level `#7FFD` / `#EFF7` reference, code examples
- [Pentagon video frame](../../05_development/05_display_and_timing/video_frame_pentagon.md) — 320-line frame, 48.83 Hz, zero contention
- [Clone timing](clone_timing.md) — cross-clone timing comparison and machine detection
- [Multicolor graphics engines](../../05_development/06_graphics/multicolor_engines.md) — the software counterpart of the a4b hardware mode
- [ATM Turbo](atm_turbo.md) — its EGA-style 320×200×16 mode shares the 16c byte layout, which is what made single-source Pentagon/ATM builds possible
- [Kempston mouse](../../03_io/peripherals/mouse.md) — full protocol, wiring, and modern PS/2 descendants
- [Kay 1024](kay.md) — alternative 1 MB clone with Nemo bus
- [Profi](profi.md) — Ukrainian professional clone; source of the `#DFFD` convention
- [ATM Turbo](atm_turbo.md) — CP/M-capable clone with extended graphics
- [Scorpion](scorpion.md) — true-48K-timing alternative with GMX expansion
- [ZX Evolution](../newgen/zx_evo.md) — modern FPGA-based Pentagon successor
- [TR-DOS](../../04_operating_systems/trdos.md) — the disk OS standard on Pentagon 1024
- [Beta 128 FDC](../../03_io/storage/beta_disk_interface.md) — disk interface integrated into Pentagon 1024SL
- [COVOX / SounDrive](../../06_sound/hardware/covox_sounDrive.md), [General Sound](../../06_sound/hardware/gs_general_sound.md) — the standard sound expansions
- [Pro Tracker 3](../../06_sound/trackers_and_formats/pt3_format.md) — AY music format that benefits from 1024K RAM
- [Soviet demoscene](../../07_demoscene/soviet_demo_scene.md) — cultural context for Pentagon 1024's dominance

---

## References

- **[Alone Coder — "IRON MADE IN", Born Dead #10 (1999)](https://zxpress.ru/ru/ezines/born-dead/10/tehnicheskie-podrobnosti-kompyuterov-semeystva-pentagon-osobennosti-pentagon-1024-upravlenie)** — the primary source for the hand-built Pentagon 1024 standard: `#EFF7` bit layout, `#DFFD` parallel wiring, lock nuance, cache, mouse detection, Gluk Reset Service
- **[Alone Coder — "16-цветный режим v1.1 для пентагона" (Info Guide #08, 30.10.2005)](https://zxpress.ru/ru/ezines/info-guide/08/shema-16-cvetnogo-videorezhima-v1-1-dlya-pentagon-apparatnaya-realizaciya-multikolora-s-podderzhkoy)** — the primary source for the 16c mode: seven-circuit schematic, address map, `%IiGRBgrb` byte layout, the v1.1 defect-fix circuit, *Pang 16C* and the view102 workflow (video-viewing addendum in *Info Guide* #9)
- **[SpeccyWiki — "16col"](https://speccy.info/16col)** — mode description and `YrYlGrRrBrGlRlBl` byte format, the games/demos/tools census, emulator support list, and the a4b-on-bit-0 history (*Hexagonal Filler*)
- **[Pentagon-1024SL official project site (NedoPC)](http://pentagon.nedopc.com/)** — version history (SL 1.4 → 2.2 → 2.666), board files, ROMs
- **[Pentagon-1024SL v2.2 official documentation (ver22.pdf, 2006)](https://github.com/koe1234/pentagon_2.2/blob/main/ver22.pdf)** — factory `#7FFD` / `#EFF7` register tables, schematic, BOM
- [ZEsarUX emulator source (`mem128.c`)](https://github.com/chernandezba/zesarux) — reference implementation of `#7FFD` bits 5-7 paging and the `#EFF7` gate, quoting the zx-pk.ru Pentagon 1024 port layout
- [Pentagon-4096 (GitHub)](https://github.com/AleksandrDneprCity/Pentagon-4096) — modern multi-standard recreation documenting Pentagon/Profi/Kay paging variants
- [zx-pk.ru](https://zx-pk.ru) forum — *Пентагон 1024* subforum: hardware variants, repair threads, reproduction PCBs
- [SpeccyWiki](https://speccy.info) — Pentagon 1024SL articles, *Порт EFF7* page
- [Black_Cat — Guide to the ZX Spectrum ports (BC Info Guide #4)](https://github.com/tslabs/zx-evo/blob/master/pentevo/docs/ZX/zx-ports-full-table.txt) — `#EFF7` decode masks (`PagVidTrbReg`); English translation in [zx_ports_full_table.md](../../10_references/zx_ports_full_table.md)
