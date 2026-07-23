# +3 Internal Floppy Drive Hardware

**Scope:** The hardware of the ZX Spectrum +3's built-in floppy subsystem — the WD1772-PH controller chip, its port map, drive geometry, cable, and maintenance. The logical disk format used by the +3's DOS (the +3DOS directory structure, file extents, attribute bytes, and +3DOS-vs-CP/M differences) is covered in the sibling article [plus3_dos_format.md](plus3_dos_format.md). The general MFM signal layer is covered in [mfm_encoding.md](mfm_encoding.md).

**Audience:** Emulator authors, +3 hardware restorers, modern Spectrum-clone designers, and demoscene coders who need to drive the +3's onboard floppy directly (bypassing +3DOS).

**Prerequisites:** A working knowledge of the Z80, the ZX Spectrum memory map (especially the `#7FFD` configuration port), and floppy controllers in general. Strongly recommended to read [fdc_vg93.md](fdc_vg93.md) first, since the WD1772-PH is a derivative of the WD1793 with a near-identical command set and register file.

**Depth:** Deep. Pin-level, port-level, and command-level detail, including the WD1772-PH's timing differences vs. the WD1793, the +3's idiosyncratic motor-control scheme (which is different from both the original Beta Disk Interface and the IBM PC), and the well-known 3" drive-belt replacement procedure.

---

## §1. What the +3 Floppy Subsystem Is

### 1.1 A short history

The ZX Spectrum +3 was launched in December 1987 by Amstrad (which had purchased Sinclair Research's computer division in 1986). It was the first Spectrum with a built-in floppy disk drive. The decision to include a floppy drive was driven by Amstrad's prior success with the CPC range (1984+), which used a similar 3" floppy drive manufactured by Hitachi, Matsushita, and Canon.

The +3's floppy hardware consists of three pieces:

1. A single built-in **3-inch single-sided 40-track** floppy drive (Hitachi HFD-305S or equivalent), accessible via a flip-up lid on the right side of the case.
2. An onboard **WD1772-PH** floppy controller chip, soldered to the +3 motherboard. The "-PH" suffix denotes a plastic DIP package; functionally it is identical to the WD1772 used in many Atari ST and Amstrad CPC machines.
3. A small piece of glue logic that decodes the WD1772's ports from the Z80's I/O space and integrates the drive-motor control into the +3's `#7FFD` configuration port.

The +3's floppy system is **not compatible** with the Beta Disk Interface at the hardware level: it uses different ports, a different controller chip, and a different drive. The +3 ships with its own disk operating system, **+3DOS**, which is a 16 KB ROM that occupies a separate window in the +3's memory map and provides DOS-like file operations through hooks at `#0008` and elsewhere. See [plus3_dos_format.md](plus3_dos_format.md) for the logical format details.

### 1.2 Why the +3 is "different"

Amstrad made several hardware-design choices for the +3 that differ from the dominant Beta Disk Interface standard:

- **Different controller chip (WD1772-PH instead of WD1793).** The WD1772 is a single-density-or-double-density FDC with built-in motor control and PLL; the WD1793 is single-density-only with external motor control. The two are register-compatible at the command level (a Type II READ SECTOR command byte sequence is identical on both chips), but the WD1772 has a simpler, more integrated host interface.
- **Different drive type (3" instead of 5.25" or 3.5").** The 3" drive is a compact, caddy-loaded unit; the media are enclosed in a rigid plastic shell that survives handling much better than a bare 3.5" or 5.25" disk. The 3" format was Amstrad's preferred choice for the CPC and PCW ranges.
- **Different host port map.** The +3 uses ports `#1F`, `#2F`, and `#3F` for the floppy controller, plus the `#7FFD` configuration port for motor control and disk-side selection. The Beta Disk Interface uses ports `#1F`, `#3F`, `#5F`, `#7F`, and `#FF` (see [beta_disk_interface.md](beta_disk_interface.md)). Software written for one will not run on the other without translation.
- **Different operating system (+3DOS instead of TR-DOS).** +3DOS is CP/M-derived and uses a file-control-block (FCB) API; TR-DOS is its own design with BASIC-style LOAD/SAVE commands. See [plus3_dos_format.md](plus3_dos_format.md) and [cpm_disk_format.md](cpm_disk_format.md).

These differences mean that the +3 and Beta Disk Interface are **completely incompatible at every layer** from hardware to OS to disk format, despite both being "Spectrum floppy systems". Software written for TR-DOS will not run on a +3, and vice versa, without porting.

### 1.3 Significance

The +3 sold reasonably well in Western Europe (particularly the UK and Spain) between 1987 and 1990, and was the platform of choice for many British software houses that had grown tired of cassette distribution. However, it failed to dislodge TR-DOS in the Soviet bloc, and its 3" drive format was made obsolete by 3.5" within a few years.

Today, the +3 is mainly of interest to:

- **Emulator authors**, who must implement the WD1772-PH's command set and the +3's idiosyncratic port map to run +3 disk software.
- **Hardware restorers**, who must replace failing 3" drive belts and find rare 3" media (or replace the 3" drive with a 3.5" or Gotek adapter).
- **Demoscene coders**, who occasionally use the +3's floppy for media-distribution demos, though it is much less common than TR-DOS.

### 1.4 Scope of this article

This article covers the +3's floppy **hardware**: the WD1772-PH chip, the port map, the cable, and the drive itself. The +3's logical disk format (+3DOS) is covered in [plus3_dos_format.md](plus3_dos_format.md); the CP/M disk format that the +3 also supports is covered in [cpm_disk_format.md](cpm_disk_format.md).

---

## §2. Hardware Block Diagram

### 2.1 The major components

The +3's floppy subsystem consists of the following components on the +3 motherboard:

| Component | Purpose | Notes |
|---|---|---|
| **WD1772-PH FDC** | The floppy controller chip | 28-pin DIP, soldered directly to the motherboard (no socket on most revisions). Pin- and register-compatible with the WD1770 / WD1773 family. |
| **PAL / GAL address decoder** | Decodes ports `#1F`, `#2F`, `#3F` for the WD1772 and generates `/CS`, `A0`, `A1` for the chip | A small programmable logic chip; the exact logic equation varies by motherboard revision (Issue 1 vs. Issue 2/3). |
| **`#7FFD` configuration latch** | The +3's general-purpose configuration port | Bits 0–2 select RAM bank, bit 3 selects screen RAM, bit 4 selects ROM (48K BASIC vs. +3DOS), bits 5+6 select disk side and motor. **Not specific to floppy**, but used for floppy motor control. |
| **34-pin edge connector** | Connects to the internal 3" drive | A standard Shugart-style edge connector, but with a non-standard pin assignment (see §6). |
| **3" Hitachi HFD-305S drive (or similar)** | The internal floppy drive | Single-sided, 40-track, caddy-loaded. Spindle motor uses a rubber belt that perishes over decades. |
| **Data separator (internal to WD1772)** | The PLL that recovers the MFM data stream from the raw read signal | Unlike the WD1793, the WD1772 has an internal PLL — no external data-separator circuit is needed. |
| **Clock oscillator** | 8 MHz crystal | Drives the WD1772's CLK pin. 8 MHz → 6/12/20/30 ms step rates, 250 kbit/s MFM data rate (single density). |
| **Motor driver transistor** | Switches the +12 V to the floppy drive's spindle motor | Controlled by bit 5 of port `#7FFD`. |

### 2.2 Signal flow

```
              ┌─────────────────────────────────────┐
              │           ZX Spectrum +3            │
              │   Z80 @ 3.5 MHz                     │
              │                                     │
              │   /M1, /IORQ, /MREQ, A0..A15, D0..D7│
              └────────┬────────────────────────────┘
                       │
                       ▼
       ┌────────────────────────────────────┐
       │   #7FFD configuration latch        │
       │   (write-only, 8-bit)              │
       │   bit 5 = MOTOR ON                 │
       │   bit 6 = SIDE SELECT              │
       └──────┬─────────────────────────────┘
              │ /MOTOR, /SIDE
              ▼
       ┌────────────────────────────────────┐
       │  Address decoder (PAL)             │
       │  ports #1F, #2F, #3F → /CS, A0, A1 │
       │  port #FF (DOS-paging)             │
       └──────┬─────────────────────────────┘
              │ /CS, A0, A1, /RE, /WE
              ▼
       ┌────────────────────────────────────┐
       │  WD1772-PH FDC                     │
       │  (registers: Status/Cmd, Track,    │
       │   Sector, Data)                    │
       └──────┬─────────────────────────────┘
              │ /STEP, /DIR, /WD, /WG,
              │ /RD, /TRK00, /WP, /INDEX
              ▼
       ┌────────────────────────────────────┐
       │  34-pin edge connector             │
       │  → internal 3" drive               │
       │  (Hitachi HFD-305S)                │
       └────────────────────────────────────┘
```

The key difference from the Beta Disk Interface block diagram ([beta_disk_interface.md §2.2](beta_disk_interface.md)) is that **the +3 has no separate control latch**: drive-select, motor, and side are all controlled by bits in the general-purpose `#7FFD` configuration port (and only one drive is supported, so drive select is implicit). The WD1772-PH chip itself handles step/dir/read/write like the WD1793, but motor control is **not** integrated into the chip — it goes through `#7FFD`.

### 2.3 What's on the +3's motherboard vs. the drive

The +3 motherboard contains the WD1772-PH, the PAL address decoder, the `#7FFD` latch, the clock crystal, and the 34-pin edge connector. Everything else (spindle motor, stepper motor, read/write head, head-amplifier, write-protect sensor, track-0 sensor) is **inside the 3" drive unit**.

This is in contrast to the Beta Disk Interface, where the FDC chip is in the cartridge and the drive is purely mechanical. In the +3, the boundary between "controller" and "drive" is the 34-pin cable; beyond that cable, everything is in the drive.

### 2.4 Why the +3 has no WAIT-state generator

The WD1772-PH is a faster chip than the WD1793 — it does not need a WAIT state for read/write access at the Z80's 3.5 MHz clock. The WD1772's `/CS`, `A0`, `A1` inputs need only 50 ns of address-setup time, and the chip's output drivers are strong enough to drive the +3 motherboard's short traces without external buffering.

This is one reason why the +3 can do floppy I/O more efficiently than the Beta Disk Interface: every `IN` / `OUT` cycle on the +3 takes 4 T-states (~1.14 µs), vs. the Beta Disk Interface's 5–6 µs (with WAIT state). This is a 5× speedup at the register-access level.

The trade-off is that the +3's floppy hardware is **less tolerant of fast polling loops** than the Beta Disk Interface: code that polls the WD1772-PH's status register too quickly can read stale data because the chip has not finished updating the status bits from the previous operation. TR-DOS software ported to the +3 needs to add a few `NOP`s to its status-polling loops.

---

## §3. Port Map

### 3.1 The +3's floppy ports

The +3 uses three I/O ports for the WD1772-PH, plus one bit of the general-purpose `#7FFD` configuration port for motor control:

| Port | Read (`IN`) | Write (`OUT`) | Action |
|---|---|---|---|
| `#1F` | Status register | Command register | WD1772 register 0 (A0=0, A1=0). |
| `#3F` | Track register | Track register | WD1772 register 1 (A0=1, A1=0). |
| `#5F` | Sector register | Sector register | WD1772 register 2 (A0=0, A1=1). |
| `#7F` | Data register | Data register | WD1772 register 3 (A0=1, A1=1). |
| `#FF` | (floating) | +3DOS ROM page control | Writing to `#FF` pages +3DOS in/out (see §3.3). |
| `#7FFD` | (floating) | Configuration latch | Motor (bit 5), side select (bit 6), plus RAM/ROM config (see §3.4). |

Wait — that's **four** WD1772 ports (`#1F`, `#3F`, `#5F`, `#7F`), exactly the same pattern as the Beta Disk Interface! The +3's port-decoding logic recognises the **low 5 bits** of the port address (`A0..A4`) for the WD1772 and ignores bits 5–7. So actually:

- `#1F`, `#3F`, `#5F`, `#7F` all access the WD1772 (just like on the Beta Disk Interface).
- Port `#FF` is a separate decode that controls +3DOS ROM paging.
- Port `#7FFD` is a separate decode that handles the +3's general configuration (motor, side, RAM, ROM).

The first four ports are decoded identically to the Beta Disk Interface — bits 5 and 6 are `01` for FDC access. The difference is that the +3 has **no port `#FF` control latch for drives**: that latch is replaced by bits in `#7FFD`.

### 3.2 The WD1772 ports `#1F`, `#3F`, `#5F`, `#7F`

These four ports are decoded with the same `bits 5,6 = 01` pattern as on the Beta Disk Interface. The address decoder asserts `/CS` on the WD1772-PH and routes `A0` and `A1` to the chip's register-select inputs:

```
| Port | A1 | A0 | Read        | Write         |
| #1F  | 0  | 0  | Status      | Command       |
| #3F  | 0  | 1  | Track       | Track         |
| #5F  | 1  | 0  | Sector      | Sector        |
| #7F  | 1  | 1  | Data        | Data          |
```

This is **identical** to the Beta Disk Interface. Any code that does raw WD1772 register access on the Beta Disk Interface will work unchanged on the +3 (assuming the same WD1772 command set — see §4 for differences).

### 3.3 Port `#FF` — +3DOS ROM paging

Port `#FF` on the +3 controls the paging of the **+3DOS ROM**, the 16 KB CP/M-derived disk operating system that occupies the `#0000–#3FFF` window when active. This is the +3's equivalent of the Beta Disk Interface's `#3D00–#3DFF` page-in mechanism, but uses a single I/O port instead of a memory-mapped write.

The paging mechanism is more sophisticated than the Beta Disk Interface's flip-flop: the +3 has **multiple ROMs** (the 48K BASIC ROM, the +3 128K BASIC ROM, the +3DOS ROM, and optionally a CP/M ROM), and the page-in/page-out logic interacts with bits 4 of `#7FFD` to select which ROM is active.

The full details of +3DOS ROM paging are beyond the scope of this hardware article — see [plus3_dos_format.md](plus3_dos_format.md) for the +3DOS software architecture.

### 3.4 Port `#7FFD` — the configuration latch

Port `#7FFD` is the +3's general-purpose 8-bit configuration latch. Writing a byte to `#7FFD` latches it and affects multiple subsystems:

| Bit | Function |
|---|---|
| 0–2 | RAM bank paged into `#C000–#FFFF` (0–7) |
| 3 | Screen RAM select (0 = bank 5, 1 = bank 7) |
| 4 | ROM select (0 = 128K BASIC / +3DOS, 1 = 48K BASIC) |
| 5 | **Disk motor on/off** (1 = motor on) |
| 6 | **Disk side select** (1 = side 1) |
| 7 | Lock bit (when set, further writes to `#7FFD` are ignored until reset) |

The floppy-specific bits are 5 and 6. **Motor control** is direct: setting bit 5 turns on the spindle motor via a transistor driver on the +3 motherboard; clearing it turns the motor off. **Side selection** is also direct: setting bit 6 selects the upper head; clearing it selects the lower head. Neither bit has any automatic timing — software must manage spin-up delays explicitly.

This is fundamentally different from the Beta Disk Interface, where motor control is implicit (via the WD1793's head-load mechanism) and side selection is via the `s` bit in the Type II command byte. On the +3, both motor and side are explicit, software-controlled signals.

### 3.5 Important: `#7FFD` is shared

Because `#7FFD` is shared with non-floppy functions (RAM banking, ROM selection, screen bank), code that manipulates the motor or side must **read-modify-write** the latch, preserving the other bits. Standard practice on the +3:

```asm
; Turn on the disk motor
LD  BC, #7FFD
IN  A, (C)        ; wait — port #7FFD is WRITE-ONLY!
; Actually you cannot read #7FFD. Software must track its value in RAM.
```

Port `#7FFD` is **write-only**. Code that wants to flip the motor bit must keep a copy of the last value written in a RAM variable, modify that copy, and write it back. The +3's ROM and +3DOS ROM maintain such a variable at a known address (typically `#5B5C`); user code that needs to flip the motor bit should follow the same pattern.

This is a common source of bugs in +3 software: a program flips the motor bit without preserving the other bits, and inadvertently changes the RAM bank or ROM selection, causing a crash.

### 3.6 No `#FF`-style drive-select latch

Because the +3 supports only **one** internal drive (drive A), there is no need for a drive-select latch. The internal drive is permanently selected via the 34-pin cable — its `/DS0` line is hard-wired to ground inside the +3. External drives connected via the +3's expansion port (rare, but possible via an adapter) would need a separate drive-select mechanism; the +3 does not provide one.

This is another difference from the Beta Disk Interface, which supports up to four drives. The +3 is a single-drive system by design.

### 3.7 Comparison with the +2A

The ZX Spectrum +2A (the "black +2", released 1987, essentially a +3 without the floppy drive) has the **same motherboard logic** as the +3, including the WD1772-PH FDC, the PAL address decoder, and the `#7FFD` motor/side bits. The +2A's motherboard even has the 34-pin edge connector for the internal drive, but it is unpopulated — there is no drive installed.

Some +2A owners have added a floppy drive by soldering a 34-pin header to the unpopulated connector position and installing a 3" drive (or a 3.5" drive via an adapter). The +2A's ROM is identical to the +3's ROM, so the +2A runs +3DOS disk software perfectly once a drive is installed.

The earlier **grey +2** (Toastrack-derived, 1986) does **not** have an onboard FDC; it uses a different motherboard design without the WD1772 or its address decoder. A grey +2 cannot run +3 disk software without an external floppy interface (typically a Beta Disk Interface).

---

## §4. WD1772-PH Specifics

### 4.1 WD1772 vs WD1793 — what's the same

The WD1772-PH is a member of the same Western Digital floppy-controller family as the WD1793. It shares:

- **The same register file** — Status/Command, Track, Sector, Data — at the same addresses (`A0,A1 = 00, 01, 10, 11`).
- **The same command set** — Type I (RESTORE, SEEK, STEP, STEP-IN, STEP-OUT), Type II (READ SECTOR, WRITE SECTOR), Type III (READ ADDRESS, READ TRACK, WRITE TRACK), Type IV (FORCE INTERRUPT). Command byte format is identical.
- **The same status register layout** — the same bit meanings for the same command types.
- **The same step-rate encoding** — bits 1–0 of the Type I command byte select 6/12/20/30 ms step rates at 8 MHz clock.
- **The same Type II flags** — `m` (multi-sector), `s` (side select via /SIDE pin), `e` (head settle), `a` (deleted data AM).
- **The same MFM/FM encoding scheme** — single-density FM at 125 kbit/s, double-density MFM at 250 kbit/s. (The +3 uses MFM exclusively.)

In short: **any software that drives the WD1793 via its command bytes will work on the WD1772-PH with no changes**, as long as the motor and side-control conventions are translated (see §3.4 above).

### 4.2 WD1772 vs WD1793 — what's different

The WD1772-PH differs from the WD1793 in several important ways:

| Feature | WD1793 | WD1772-PH |
|---|---|---|
| **Internal PLL / data separator** | No — needs external PLL circuitry | Yes — integrated |
| **Pin count** | 40-pin DIP | 28-pin DIP |
| **5 V / 12 V power** | 5 V only (TTL) | 5 V only (TTL) |
| **Maximum data rate** | 250 kbit/s MFM (single density) | 500 kbit/s MFM (double density — "DD") |
| **External data separator needed** | Yes (WD1691 or similar) | No |
| **Motor control** | Internal `/HDLD` pin, drives external motor via glue logic | None — motor is controlled externally (on the +3, via `#7FFD` bit 5) |
| **Spin-up timer** | Yes (6 index pulses before Type II) | No — software must delay explicitly |
| **Side-select output** | `/SIDE` pin driven by the Type II `s` bit | `/SIDE` pin driven by the Type II `s` bit, but the +3 also drives side via `#7FFD` bit 6 |
| **Wait-state tolerance** | Needs external WAIT-state generator at Z80's 3.5 MHz | None needed — fast enough |

The two most important practical differences are:

1. **The WD1772 has no built-in spin-up timer.** Software must turn on the motor (via `#7FFD` bit 5), wait at least 0.5 seconds (preferably 1 second for safety) for the drive to reach operating speed, and only then issue Type II or Type III commands. The +3DOS ROM handles this automatically; user code that bypasses +3DOS must do it manually.

2. **The WD1772 has no built-in motor control.** On the +3, software must turn the motor on and off explicitly via `#7FFD` bit 5. There is no "the motor stays on for 15 index pulses after the last command" behaviour — if software forgets to turn the motor off, it stays on forever (wearing out the drive belt and wasting power).

### 4.3 The double-density capability

The WD1772-PH can do **double-density MFM** at 500 kbit/s (vs. the WD1793's 250 kbit/s single-density MFM). However, the +3's floppy controller is wired to run at single density (250 kbit/s), because:

1. The 3" Hitachi drive is rated for 250 kbit/s only.
2. The +3DOS ROM uses single-density mode exclusively.
3. Double-density would require a higher-grade data cable and more careful PCB layout.

The 8 MHz clock on the +3 motherboard sets the WD1772 to its **250 kbit/s MFM** mode. Driving the WD1772 with a 16 MHz clock would enable 500 kbit/s MFM, but this requires hardware modification (replacing the crystal) and software that knows how to handle the higher data rate. Few +3 software titles use double-density.

### 4.4 Command byte compatibility summary

Software written for the WD1793 (e.g., TR-DOS code) will run on the WD1772-PH with the following adjustments:

| Operation | WD1793 (Beta Disk) | WD1772 (+3) |
|---|---|---|
| **Status/command access** | `IN A,(#1F)` / `OUT (#1F),A` | Same — no change |
| **Track / sector / data access** | `IN A,(#3F/#5F/#7F)` / `OUT (#xx),A` | Same |
| **Select drive A** | `OUT (#FF),#01` | Not needed — single drive only |
| **Start motor** | Issue Type I with `h=1` | Set bit 5 of `#7FFD` |
| **Stop motor** | (Automatic — wait 15 index pulses) | Clear bit 5 of `#7FFD` |
| **Spin-up delay** | (Automatic — 6 index pulses) | Software must `HALT` ~1 second |
| **Select side 0/1** | Type II `s=0` / `s=1` | Clear / set bit 6 of `#7FFD` (or use Type II `s`) |
| **Status polling loop** | Need 5–6 µs per iteration (WAIT state) | Need 1–2 µs per iteration (no WAIT state) but add `NOP`s |

These differences are why TR-DOS software does not run on a +3 without porting.

---

## §5. Drive Geometry

### 5.1 The stock 3" Hitachi HFD-305S

The +3's stock drive is a **Hitachi HFD-305S** (or equivalent, such as the Matsushita JU-455). Its physical and logical geometry:

| Parameter | Value |
|---|---|
| **Media form factor** | 3 inch (compact floppy) |
| **Media coating** | Double-sided coating (only side 0 is used) |
| **Drive heads** | 1 (single-sided) |
| **Tracks per side** | 40 |
| **Track pitch** | 1/96 inch (~0.265 mm) |
| **Sectors per track** | 9 (or 10 on some non-standard formats) |
| **Bytes per sector** | 512 |
| **Total capacity** | 40 × 9 × 512 = 180 KB (or 40 × 10 × 512 = 200 KB non-standard) |
| **Rotation speed** | 300 RPM |
| **Bit density** | 250 kbit/s MFM (single density equivalent in terms of bit rate; MFM at 250 kbit/s = 500 kbit/s FM equivalent) |
| **Transfer rate** | ~31.25 KB/s (theoretical) |
| **Encoding** | MFM |
| **Index pulse rate** | 5 Hz (300 RPM) |
| **Step rate** | 6 ms (typical — the +3DOS ROM uses 6 ms; the WD1772 supports 6/12/20/30 ms) |
| **Head load time** | 35 ms (typical) |
| **Spindle motor** | Belt-driven from a DC motor |
| **Loading mechanism** | Caddy-loaded (the disk is inserted into a metal/plastic caddy, which is then inserted into the drive) |

The 3" disk media itself is a rigid plastic shell approximately 90 mm × 94 mm × 3.5 mm, with a sliding metal shutter protecting the read/write window (similar to a 3.5" disk). The write-protect is a small switch on the corner of the disk.

### 5.2 Comparison with TR-DOS geometry

For reference, the standard TR-DOS geometry (used on the Beta Disk Interface with an 80-track 5.25" or 3.5" drive):

| Parameter | TR-DOS 80-track | +3 stock 3" |
|---|---|---|
| Tracks | 80 | 40 |
| Heads | 2 | 1 |
| Sectors/track | 10 | 9 |
| Bytes/sector | 512 | 512 |
| Total capacity | 819 KB | 180 KB |
| Disk rotation | 300 RPM | 300 RPM |
| Step rate | 6 ms (or 12 ms for compatibility) | 6 ms |

The +3's stock 3" drive has roughly **1/5 the capacity** of a TR-DOS disk. This is why +3 software typically came on multiple disks (one disk per major game level, or one disk per application + data), whereas TR-DOS software could often fit multiple programs on a single disk.

### 5.3 The 3.5" drive retrofit

Many +3 owners replace the stock 3" drive with a standard **3.5" PC floppy drive** (typically a Teac, Sony, or Samsung model). The 3.5" drive has the following advantages:

- **Larger capacity**: 80 tracks × 2 sides × 18 sectors/track × 512 bytes = 1.44 MB (with double-density), or 720 KB (with single-density, matching the +3's 250 kbit/s data rate).
- **Readily available media**: 3.5" DS/HD disks are still sold; 3" disks are rare and expensive.
- **No belt to perish**: 3.5" drives use a direct-drive spindle motor, eliminating the most common failure mode of the 3" drive.
- **Higher reliability**: 3.5" drive heads survive longer and require less cleaning.

The 3.5" retrofit requires:

1. **A cable adapter** that translates the +3's 34-pin edge connector to the 3.5" drive's 34-pin header (the pinout is the same, but the connectors are physically different — edge vs. header).
2. **Power supply wiring**: 3.5" drives require +5 V and +12 V (or +5 V only on direct-drive models); the +3's internal power supply provides both.
3. **Physical mounting**: the 3.5" drive is smaller than the 3" drive, so an adapter bracket is needed to fit the 3.5" drive in the +3's drive bay.
4. **Software configuration**: the +3DOS ROM treats the drive as a 40-track single-sided drive by default. To use 80-track or double-sided disks, software must issue standard WD1772 commands with the appropriate track and sector numbers — this works fine on a 3.5" drive.

The +3 can read and write both 3" and 3.5" media with the appropriate drive installed. The +3DOS disk format is media-agnostic (it uses the same MFM sector layout on both).

### 5.4 Geometry-detection software

Software that uses the +3's floppy directly (bypassing +3DOS) typically assumes the stock 3" geometry: 40 tracks × 1 side × 9 sectors × 512 bytes. Software that wants to support 3.5" retrofits typically probes the drive by issuing a SEEK to track 79 and checking the status; if the seek succeeds, the drive has 80 tracks, otherwise it's a 40-track drive.

Similarly, software can probe the number of sides by issuing a Type II READ SECTOR with `s=1` and checking for `RECORD NOT FOUND`. If the read succeeds, the drive is double-sided.

+3DOS itself does not auto-detect drive geometry; the geometry is fixed in the ROM at boot time based on the assumption of a stock 3" drive. User software that wants to use a different geometry must bypass +3DOS and issue raw WD1772 commands.

---

## §6. Cable Pinout and the +3's Special Wiring

### 6.1 The 34-pin internal connector

The +3's internal floppy connector is a **34-pin card-edge connector** on the motherboard, mating with a 34-conductor flat cable that runs to the internal 3" drive. The pinout is **Shugart-compatible** with a few Amstrad-specific twists.

The pinout of the +3's motherboard edge connector:

| Pin | Signal | Direction | Notes |
|---|---|---|---|
| 1, 3, 5, ..., 33 (odd) | GND | — | Ground; all odd pins are tied to ground. |
| 2  | (unused) | — | |
| 4  | (unused) | — | |
| 6  | `/DS3` | out | Hard-wired high (no drive D). |
| 8  | `/INDEX` | in | From the drive. |
| 10 | `/DS0` | out | Hard-wired low (drive A is always selected). |
| 12 | `/DS1` | out | Hard-wired high (no drive B). |
| 14 | `/DS2` | out | Hard-wired high (no drive C). |
| 16 | `/MOTOR ON` | out | From the +3's `#7FFD` bit 5 (via a transistor driver). |
| 18 | `/DIR` | out | From the WD1772. |
| 20 | `/STEP` | out | From the WD1772. |
| 22 | `/WDATE` | out | From the WD1772. |
| 24 | `/WGATE` | out | From the WD1772. |
| 26 | `/TRK00` | in | To the WD1772. |
| 28 | `/WPT` | in | To the WD1772. |
| 30 | `/RDATE` | in | To the WD1772. |
| 32 | `/SIDE1` | out | From the +3's `#7FFD` bit 6. (Note: not from the WD1772's `/SIDE` pin — see §6.3.) |
| 34 | `/READY` | in | Often unused. |

### 6.2 The "always-selected" drive A

Because the +3 supports only one drive, `/DS0` is hard-wired to ground on the motherboard. The drive thinks it is permanently selected and responds to all step/dir/read/write signals regardless of the state of `/DS0`–`/DS3`. This simplifies the cable and the WD1772 command sequences (software never needs to "select the drive").

The downside: a +3 cannot support an external drive B without external hardware. Some +3 expansion peripherals (rare) provide a second floppy connector wired to `/DS1`, but this is non-standard and requires special software.

### 6.3 Side-select routing

A subtle point: the +3 routes **side select via `#7FFD` bit 6**, not via the WD1772's internal `/SIDE` pin. The WD1772's `/SIDE` pin (pin 26 on the 28-pin DIP) is left unconnected on the +3 motherboard; the floppy cable's pin 32 (`/SIDE1`) is driven directly by a flip-flop on the +3's motherboard that is set/cleared by writes to `#7FFD`.

This means:

- The Type II `s` bit in the WD1772 command byte is **ignored** by the +3 hardware — setting `s=1` does NOT switch to side 1.
- To select side 1, software MUST set bit 6 of `#7FFD` (preserving the other bits — see §3.5).
- Software written for the Beta Disk Interface that uses the `s` bit for side selection will not work correctly on the +3.

This was an Amstrad design choice that simplified the +3's motherboard logic (one flip-flop for side, one for motor) at the cost of incompatibility with the Beta Disk Interface's command-set-driven side selection.

### 6.4 Motor-control routing

Motor control is similarly routed through `#7FFD` bit 5, not through the WD1772. The WD1772's `/HDLD` pin (which on the Beta Disk Interface controls the motor via external glue) is left unconnected on the +3. The floppy cable's pin 16 (`/MOTOR ON`) is driven by a transistor on the +3 motherboard, which in turn is controlled by bit 5 of `#7FFD`.

This means:

- The Type I `h` bit (head-load) in the WD1772 command byte is **ignored** by the +3 hardware.
- To turn on the motor, software MUST set bit 5 of `#7FFD`.
- There is no automatic "15 index pulse" motor-off timer — software must explicitly clear bit 5 to turn the motor off.

Again, this was an Amstrad design choice for motherboard simplicity.

### 6.5 Cable length and termination

The +3's internal cable is short (~20 cm), going from the motherboard to the drive inside the same case. This short cable does not need termination resistors — the +3's drive has no termination resistor pack installed (unlike a typical Shugart-bus drive). The WD1772's outputs are strong enough to drive the short unterminated cable reliably.

If you retrofit a 3.5" drive, the cable length is similar (~20 cm), so termination is still not required. Long cables (>50 cm) for external drive mounting would require termination, but this is rarely done on a +3.

### 6.6 Power supply to the drive

The +3 provides +5 V and +12 V to the drive via a separate 4-pin Molex connector (the standard "large" floppy-drive power connector). The +12 V is for the spindle motor; the +5 V is for the drive's logic. The +3's power supply is rated for ~1.5 A on +12 V, which is enough for one 3" drive but may be insufficient for two drives or for a power-hungry 5.25" drive.

When retrofitting a 3.5" drive, the same 4-pin Molex connector provides power. Modern 3.5" drives draw less current than the original 3" drive, so power supply is rarely a problem.

---

## §7. Variants and Compatible Drives

### 7.1 The 3" drive family

The +3's stock drive is a Hitachi HFD-305S, but Amstrad used several interchangeable 3" drives across the CPC, PCW, and +3 ranges. All of these drives are mechanically interchangeable and electrically compatible with the +3:

| Drive model | Manufacturer | Used in | Notes |
|---|---|---|---|
| HFD-305S | Hitachi | +3, CPC 664, CPC 6128 | The most common +3 drive. |
| JU-455 | Matsushita (Panasonic) | +3, CPC 664 | Equivalent to the HFD-305S. |
| EME-150 | Canon | CPC 6128, some +3s | Slightly different spindle motor mounting but compatible. |
| FD-3A | Various / no-name | Some +3 clones | Generic 3" SS drive. |

All of these drives have a 34-pin Shugart-compatible edge connector, single-sided heads, 40 tracks, and a belt-driven spindle motor. Replacement belts are still available from specialty suppliers (the standard size is roughly 75 mm square-section belt, but exact dimensions vary by drive model — measure before ordering).

### 7.2 The 3.5" retrofit options

A standard PC 3.5" floppy drive (Teac, Sony, Samsung, YE Data, etc.) can be retrofitted to the +3. The most common retrofit options:

- **Direct cable adapter** — a small PCB or cable that converts the +3's 34-pin edge connector to a 34-pin header for the 3.5" drive. The simplest possible adapter, since the pinout is identical (only the connector type differs). Available from various Spectrum suppliers.
- **3.5"-in-3"-case retrofit** — physically replacing the 3" drive's internals with a 3.5" drive mounted in a 3D-printed bracket that fits the +3's drive bay. This is the most cosmetically appealing option; the +3 looks stock from the outside.
- **External 3.5" drive** — mounting a 3.5" drive in an external enclosure and running a cable out of the +3's drive-bay cutout. Less elegant, but does not require modifying the +3's case.

Any of these retrofits work fine with the +3DOS ROM. Software sees the new drive as a regular floppy drive; the only difference is the geometry (which software can probe — see §5.4).

### 7.3 Drive variants from Amstrad

Amstrad shipped a small number of variants of the +3 itself:

- **ZX Spectrum +3 (UK)** — the standard UK model, with Hitachi HFD-305S drive, UK power supply, and English ROMs.
- **ZX Spectrum +3 (Spanish)** — same hardware, Spanish ROMs (the +3 was popular in Spain, where it sold well into the early 1990s).
- **ZX Spectrum +3 (German/French/Italian)** — same hardware, localized ROMs.
- **ZX Spectrum +2A** — same motherboard as the +3, but without the floppy drive or the 34-pin connector populated (see §3.7). Software-identical to the +3 once a drive is installed.

### 7.4 Compatible clones

No Spectrum clone (Pentagon, Scorpion, etc.) cloned the +3's floppy subsystem — they all used the Beta Disk Interface port map instead. This is because the +3 was a relatively late Western product (1987), and the Soviet clones had already standardised on the Beta Disk Interface / TR-DOS model by 1989.

The ZX Spectrum Next, ZX Evolution, and other modern FPGA clones typically include **both** a Beta Disk-compatible FDC and an optional +3-compatible FDC, so they can run either TR-DOS or +3DOS software. The +3 mode is usually selected via a configuration register.

### 7.5 Disk-media compatibility

The 3" disk media used by the +3 are interchangeable with the media used by the Amstrad CPC and PCW — they are the same physical format. Disks from a CPC 6128 will read fine in a +3 (assuming the data was written with the same encoding, which it usually is — both use MFM at 250 kbit/s).

3" disks are not interchangeable with 3.5" or 5.25" media — they are physically different sizes. To transfer data between a +3 and another platform, you must use either:

- A 3" drive on both sides (rare today).
- An emulator that can read .DSK images (the standard +3 / CPC disk-image format — see [dsk_fdi_formats.md](dsk_fdi_formats.md)).
- A Gotek floppy emulator with FlashFloppy firmware on the +3 side.

### 7.6 Gotek on the +3

A Gotek floppy emulator can be retrofitted to the +3 just like a 3.5" drive. The Gotek emulates a standard Shugart-bus drive, and the +3 sees it as a regular floppy drive. With FlashFloppy firmware, the Gotek can read .DSK, .EDSK, and other +3 disk-image formats directly from a USB stick.

The Gotek retrofit is the most practical option today: it eliminates the need for rare 3" media, eliminates the belt-failure problem, and provides near-instantaneous disk access (much faster than a real floppy). The only downside is that the +3 no longer has an "authentic" floppy experience — for demoscene and historical-accuracy purposes, real hardware is preferred.

---

## §8. Common Issues and Maintenance

### 8.1 The 3" drive belt: the most common failure

By far the most common hardware failure on a +3 is **perishing of the spindle-motor drive belt**. The Hitachi HFD-305S uses a small rubber belt (~75 mm length, square cross-section) to transmit torque from the spindle motor to the disk spindle. Over 30+ years, this belt:

- **Stretches** and no longer grips the pulleys — the disk rotates slower than 300 RPM, causing read errors.
- **Turns into sticky goo** and jams the spindle — the motor runs but the disk does not turn, often accompanied by a grinding noise.
- **Snaps** outright — the motor runs freely but the disk does not turn at all.

The replacement procedure (well-documented on Spectrum community sites):

1. Open the +3 case (six screws on the bottom).
2. Remove the 3" drive from the drive bay (two screws and a ribbon cable).
3. Open the 3" drive's metal cover (four small screws).
4. Lift out the old belt (or scrape off the goo if it has turned sticky — use isopropyl alcohol and Q-tips).
5. Clean the motor pulley and the spindle pulley thoroughly with isopropyl alcohol.
6. Stretch the new belt over both pulleys. The new belt will be slightly tighter than the old one — this is normal; it will stretch to the correct tension after a few hours of use.
7. Reassemble in reverse order.

The whole procedure takes about 30 minutes. Replacement belts are still available from specialty suppliers (e.g., SellMyRetro, ByteShop, eBay) for a few pounds.

### 8.2 Head cleaning

The read/write head on the 3" drive accumulates magnetic-oxide dust from the disk media over time. Symptoms include read errors on specific tracks (often the outer tracks, which see more disk activity) and a general degradation in read reliability.

The standard fix is a **cleaning disk** — a special 3" disk with a non-abrasive cleaning fabric instead of magnetic media. Insert the cleaning disk, run a `LOAD "x"` (which will fail with read errors), and the disk's fabric wipes the head clean. Cleaning disks are rare today; an alternative is to open the drive and clean the head manually with isopropyl alcohol and a foam swab (do not use a cotton swab — cotton fibers can snag on the head).

Head cleaning should be done every few months on a regularly-used +3, or once before attempting to read old disks that have been in storage for years.

### 8.3 Read/write head alignment

After years of use, the read/write head can drift out of alignment. Symptoms: a disk formatted and written on the +3 reads fine on the same +3, but fails to read on a different +3 (or vice versa). The standard fix is to write a known-good disk on another +3 (or use a known-good disk image on a Gotek), then adjust the head-positioner stepper motor on the misaligned drive until the disk reads correctly.

This is delicate work — the stepper-motor position is adjusted by loosening a small set screw, rotating the motor by a fraction of a degree, and tightening the screw. The adjustment needs to be precise to within ~0.1°. Most +3 owners prefer to replace the drive rather than attempt this repair.

### 8.4 WD1772-PH chip failure

The WD1772-PH chip itself occasionally fails after decades of use. Symptoms include:

- The +3 reports "Drive not ready" or "Missing disk" on every disk operation.
- `IN A,(#1F)` returns a constant value (e.g., `#00` or `#FF`) regardless of what the drive is doing.
- The +3DOS ROM hangs at startup (waiting for the WD1772 to respond).

Replacement WD1772-PH chips are still available from specialty suppliers (they were also used in the Atari ST, which means there is a steady supply from ST repairs). The chip is socketed on some +3 motherboard revisions; on others, it is soldered directly and must be desoldered for replacement.

### 8.5 +2A-specific issues

The +2A has the same motherboard logic as the +3 but no drive installed. Issues specific to the +2A:

- **Unpopulated 34-pin connector**: if you want to add a floppy drive, you need to solder a 34-pin edge connector to the unpopulated footprint on the +2A motherboard. This requires through-hole soldering skills but is otherwise straightforward.
- **No drive-bay cutout**: the +2A's case does not have a cutout for a floppy drive. Owners who add a drive must either cut a hole in the case or run the drive externally via a cable.
- **Identical ROM**: the +2A's ROM is identical to the +3's, including the +3DOS code. Once a drive is installed and the connector populated, the +2A runs +3DOS software without any modifications.

### 8.6 Power supply issues

The +3's internal power supply provides +5 V at 2 A and +12 V at 1.5 A. The +12 V is shared between the floppy drive's spindle motor and the +3's analog video circuitry. A weak or aged power supply can cause:

- The +3 crashes when the floppy drive spins up (the +12 V sags, taking the video circuitry with it).
- The floppy drive spins too slowly (the +12 V is too low for the spindle motor).
- The picture wobbles or distorts during disk access (the +12 V sags and affects video sync).

The standard fix is to recap the power supply (replace the electrolytic capacitors) or replace the entire power supply with a modern switched-mode unit. Several aftermarket replacements are available.

---

## §9. Modern Replacements

### 9.1 Gotek / HxC on the +3

The most popular modern replacement for the +3's floppy drive is the **Gotek** floppy emulator (with FlashFloppy or HxC firmware). The Gotek is a small device that emulates a standard Shugart-bus floppy drive but reads disk images from a USB stick.

On the +3, the Gotek is connected exactly like a real 3.5" drive: a cable adapter from the +3's 34-pin edge connector to the Gotek's 34-pin header, plus a Molex power connector. From the +3DOS software's point of view, the Gotek is indistinguishable from a real floppy drive — but it is much faster, more reliable, and reads .DSK, .EDSK, .HFE, and other disk image formats directly.

The FlashFloppy firmware supports:

- **.DSK / .EDSK** — the standard Amstrad / Spectrum +3 disk-image formats (see [dsk_fdi_formats.md](dsk_fdi_formats.md)).
- **.HFE** — the HxC floppy-emulator format.
- **.SCP** — the SuperCard Pro flux-level format (see [scp_format.md](scp_format.md)).
- Various CPC and PCW disk formats, which are byte-compatible with the +3.

A Gotek with FlashFloppy turns the +3 into a usable modern computer: disk access is nearly instantaneous (compared to several seconds for a real floppy), and the USB stick can hold thousands of disk images.

### 9.2 Hardware add-ons: the DivMMC and divIDEfuture

The **DivMMC** and **divIDEfuture** peripherals provide SD-card storage to the +3 via the expansion port. They use modern mass-storage formats (FAT/FAT32) and bypass the +3DOS disk system entirely. Software that supports these peripherals loads from the SD card, not from the floppy drive.

The DivMMC and divIDEfuture are not floppy replacements per se — they are mass-storage peripherals that happen to obsolete the floppy drive for most uses. The +3's floppy subsystem remains functional alongside the SD card, so the user can still read original +3 disks when needed.

See [divide_divmmc.md](divide_divmmc.md) and [hdd_overview.md](hdd_overview.md) for details on these peripherals.

### 9.3 FPGA clones with onboard +3 FDC

Modern FPGA-based Spectrum clones (ZX Spectrum Next, ZX Evolution, etc.) typically include a **+3-compatible FDC** as one of their emulation modes. The Next, for example, implements the WD1772-PH in its FPGA and routes motor and side control through a `#7FFD`-style configuration register, exactly as the original +3 does. Software written for the +3 runs on the Next without modification.

The advantage of the FPGA approach is that no real floppy drive is needed — disk images are loaded from the Next's SD card and presented to the +3DOS ROM as if they were real floppy disks. The +3's floppy subsystem is essentially a software emulation running on the FPGA.

### 9.4 Cycle-exact emulation

For emulator authors, the +3's floppy subsystem presents some challenges:

- The WD1772-PH's command state machine is similar but not identical to the WD1793's (see §4.2). Emulator code that handles the WD1793 needs to be adjusted for the WD1772's different motor-control and side-select conventions.
- The `#7FFD` configuration latch must be emulated as a shared register (motor and side bits affect the floppy, but other bits affect RAM banking and ROM selection). Emulator code that handles the floppy subsystem must coordinate with the memory-management subsystem.
- The +3DOS ROM paging mechanism (port `#FF`) interacts with the `#7FFD` ROM-select bit. Emulator code must handle the interaction correctly.

Modern emulators (FUSE, ZEsarUX, SpecEmu, etc.) implement approximately cycle-exact +3 floppy emulation. The .DSK and .EDSK formats are the standard disk-image formats for +3 software preservation.

---

## 10. Cross-references

### 10.1 Within the storage section

- [fdc_vg93.md](fdc_vg93.md) — the WD1793 chip used by the Beta Disk Interface. The WD1772-PH is a near-clone of the WD1793 at the command level; reading this article first will give you the background needed to understand the WD1772.
- [beta_disk_interface.md](beta_disk_interface.md) — the alternative Spectrum floppy interface, using the WD1793 and TR-DOS. Worth reading for comparison, since the +3 and Beta Disk Interface are the two competing standards for Spectrum floppy disk.
- [plus3_dos_format.md](plus3_dos_format.md) — the +3's logical disk format: +3DOS directory structure, file extents, attribute bytes, and the +3DOS-vs-CP/M differences. This article covers the hardware; that article covers the software layer.
- [cpm_disk_format.md](cpm_disk_format.md) — CP/M 2.2 disk format on the +3 and other Spectrum platforms. +3DOS is heavily derived from CP/M, and CP/M disks can be read on a +3 with the appropriate loader.
- [disk_format_overview.md](disk_format_overview.md) — the IBM 3740 physical sector layout shared by +3 DOS, TR-DOS, CP/M, and Opus.
- [mfm_encoding.md](mfm_encoding.md) — the signal layer recorded on the +3's floppy disks.
- [dsk_fdi_formats.md](dsk_fdi_formats.md) — the .DSK and .EDSK disk-image formats used to preserve +3 disks.
- [scp_format.md](scp_format.md) — the .SCP flux-level preservation format for +3 disks.
- [divide_divmmc.md](divide_divmmc.md), [hdd_overview.md](hdd_overview.md) — the SD-card mass-storage peripherals that displaced the +3's floppy subsystem.

### 10.2 Adjacent hardware references

- [02_hardware/](../../02_hardware/) — for the +3 motherboard schematic and other hardware documentation.
- The Amstrad CPC 6128 and PCW ranges use essentially the same floppy hardware as the +3 (WD1772-PH, 3" drive, similar cable). Documentation for those machines is widely available and applies directly to the +3.

### 10.3 Reverse engineering and demoscene angles

- For +3 disk-based protection schemes: see [05_reversing/](../../05_reversing/).
- For cycle-exact +3 floppy emulation: see [11_emulation/](../../11_emulation/).
- +3-specific demoscene productions are rare; the dominant platform for Spectrum disk-based demos is the Beta Disk Interface / Pentagon / TR-DOS combination. However, the +3 is the platform of choice for some Spanish and British demoscene productions.

### 10.4 External references

- **The Amstrad +3 Service Manual** — full schematics of the +3 motherboard, including the WD1772-PH wiring, the PAL address-decoder equations, and the power-supply circuitry.
- **The WD1772-PH data sheet** (Western Digital, 1985) — full pin-out, command set, and timing specifications. The Atari ST and Amstrad CPC communities have extensively documented this chip.
- **The comp.sys.sinclair FAQ** — historical context on the +3 and its competitors.
- **The World of Spectrum +3 archive** — +3 disk images, software compatibility lists, and user-maintained documentation.
- **The FlashFloppy documentation** — details on the Gotek firmware that supports .DSK and .EDSK images on the +3.

---

## License

This article is licensed under [Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0)](https://creativecommons.org/licenses/by-sa/4.0/).

You are free to:

- **Share** — copy and redistribute the material in any medium or format.
- **Adapt** — remix, transform, and build upon the material for any purpose, even commercially.

Under the following terms:

- **Attribution** — you must give appropriate credit (a link to this article is sufficient), indicate if changes were made, and indicate the license under which the original is released.
- **ShareAlike** — if you remix, transform, or build upon the material, you must distribute your contributions under the same license as the original.

The full legal text is available at the link above.

The trademarks **ZX Spectrum**, **ZX Spectrum +2**, **ZX Spectrum +2A**, **ZX Spectrum +3**, **+3DOS**, **Amstrad**, **Sinclair**, **WD1772**, **WD1772-PH**, **WD1770**, **WD1793**, **Hitachi HFD-305S**, **Matsushita JU-455**, **Canon EME-150**, **Atari ST**, **Gotek**, **FlashFloppy**, **HxC**, **DivMMC**, **divIDEfuture**, **ZX Spectrum Next**, **ZX Evolution**, **Shugart**, **Western Digital**, **Molex**, and others mentioned in this document are the property of their respective owners and are used here for identification and educational purposes only. No endorsement by, or affiliation with, any of these trademark holders is implied.
