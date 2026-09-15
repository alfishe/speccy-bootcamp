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
| 0 | **a4b** — "attribute per byte" hardware multicolor | Attributes read from `#6000`-`#77FF` instead of `#5800`-`#5AFF`, giving each 8×1 pixel stripe its own ink/paper. 1 = enabled. See [multicolor_engines.md](../../05_development/06_graphics/multicolor_engines.md). |
| 1 | **512×192** monochrome mode | Doubles horizontal resolution; pixel data split between `#4000` and `#6000` areas (documented in Deja Vu #6). 1 = enabled. |
| 2 | **Extended memory gate** | 0 = RAM above 128K present, 1 = disabled (see above). |
| 3 | Unused (proposal: read-only cache control) | 0 = writable, 1 = write-protected — never widely adopted. |
| 4 | **GigaScreen** — hardware screen interleaving | Alternates screen 0/1 every raster line (see below). Rarely implemented; the game *Homer Simpson in Russia* drives it via `#FFFC` instead of `#EFF7`. |
| 5-6 | Reserved for ROM-disk (proposals only) | Alone Coder suggested repurposing: bit 5 = Sound Blaster enable, bit 6 = 384×304 mode (per ZX-Guide 2). |
| 7 | **Gluk CMOS** — real-time clock enable | 1 = CMOS ports active (schematic in Deja Vu #8 — which also prints the port as `#FFFC`). 1 = enabled. |

### Factory Standard (Pentagon-1024SL v2.2, official documentation 2006)

| Bit | Function | Notes |
|---|---|---|
| 0 | **16 colour** mode | Every pixel gets its own color from a 16-color palette — four screen areas compose one 256×192 image. 0 = off, 1 = on. |
| 1 | Unused | — |
| 2 | **128K mode** | 1 = block memory above 128K; `#7FFD` bit 5 becomes the 48K lock. |
| 3 | **ROM disable** | 1 = RAM page 0 projected at `#0000`-`#3FFF` instead of ROM. |
| 4 | **TURBO control** — *inverted* | 0 = 7 MHz turbo ON, 1 = 3.5 MHz normal. |
| 5 | Unused | — |
| 6 | **384×304** mode | Full-screen image without border. 0 = off, 1 = on. |
| 7 | Unused on SL v2.2 | (CMOS enable on other variants; see hand-built bit 7.) |

The official documentation adds that all other I/O ports (Kempston, ZX LPRINT III, border, AY, Beta 128 FDC) keep their standard ZX Spectrum configuration.

> [!WARNING]
> **The two layouts are not compatible.** Hand-built machines put multicolor at bit 0 and 512×192 at bit 1; the SL v2.x puts 16-colour at bit 0 and turbo at bit 4. Video-mode software must target the specific generation or probe. Modern recreations pick either layout — the Pentagon-4096 follows the SL convention (with bit 5 = multicolor), emulators generally implement the paging bits (2 and 3) only.

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
- **[Pentagon-1024SL official project site (NedoPC)](http://pentagon.nedopc.com/)** — version history (SL 1.4 → 2.2 → 2.666), board files, ROMs
- **[Pentagon-1024SL v2.2 official documentation (ver22.pdf, 2006)](https://github.com/koe1234/pentagon_2.2/blob/main/ver22.pdf)** — factory `#7FFD` / `#EFF7` register tables, schematic, BOM
- [ZEsarUX emulator source (`mem128.c`)](https://github.com/chernandezba/zesarux) — reference implementation of `#7FFD` bits 5-7 paging and the `#EFF7` gate, quoting the zx-pk.ru Pentagon 1024 port layout
- [Pentagon-4096 (GitHub)](https://github.com/AleksandrDneprCity/Pentagon-4096) — modern multi-standard recreation documenting Pentagon/Profi/Kay paging variants
- [zx-pk.ru](https://zx-pk.ru) forum — *Пентагон 1024* subforum: hardware variants, repair threads, reproduction PCBs
- [SpeccyWiki](https://speccy.info) — Pentagon 1024SL articles, *Порт EFF7* page
- [Black_Cat — Guide to the ZX Spectrum ports (BC Info Guide #4)](https://github.com/tslabs/zx-evo/blob/master/pentevo/docs/ZX/zx-ports-full-table.txt) — `#EFF7` decode masks (`PagVidTrbReg`); English translation in [zx_ports_full_table.md](../../10_references/zx_ports_full_table.md)
