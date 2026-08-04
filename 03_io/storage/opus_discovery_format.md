[← Home](../../README.md) · [I/O](../) · [Storage](README.md)

# Opus Discovery Disk Format

**Scope:** The **Opus Discovery** disk interface and its associated disk format — a Western (UK-developed) alternative to TR-DOS and +3DOS, popular in the mid-to-late 1980s among UK Spectrum users. The Opus Discovery used the **WD1770** floppy controller and the **MGT** logical disk format (also used by the +D and Disciple interfaces, and later by the SAM Coupé). This article covers both the **physical** disk format (sectors, MFM encoding) and the **logical** file system (directory layout, file entries).

**Audience:** Emulator authors who need to read or write Opus Discovery disks, archival tool authors, and demoscene coders working with MGT-format disk images. The article assumes you already understand the MFM signal layer (see [mfm_encoding.md](mfm_encoding.md)) and the basics of floppy-disk geometry (see [plus3_floppy.md](plus3_floppy.md) or [beta_disk_interface.md](beta_disk_interface.md)).

**Prerequisites:** A working understanding of the IBM 3740-style sector format (gap structure, address marks, data marks) — see [mfm_encoding.md](mfm_encoding.md). Familiarity with TR-DOS (see [trd_disk_format.md](trd_disk_format.md)) helps for comparison, since the Opus Discovery is roughly contemporaneous with TR-DOS but uses a different file-system layout.

**Depth:** Deep. Byte-level layout of the Opus Discovery hardware ports, the WD1770 controller interface, the MGT-format directory structure, file entry format, and the `.MGT` disk-image file format. Worked examples for a typical MGT disk.

---

## §1. What the Opus Discovery Is

### 1.1 Why a separate format?

In 1982–1983, when the ZX Spectrum was at the height of its popularity, the only floppy-disk interface widely available in the West was the Sinclair ZX Microdrive (a stringy-floppy tape-loop system, see the World of Spectrum archive for details). The Microdrive was slow, unreliable, and limited in capacity — it was not a true floppy-disk system.

This gap in the market led several UK companies to develop true floppy-disk interfaces for the Spectrum:

- **Opus Supplies Ltd** — released the **Opus Discovery** in 1984, an integrated disk drive + interface with a built-in DOS ROM.
- **Miles Gordon Technology (MGT)** — released the **Disciple** in 1985 and the **+D** in 1987 (a stripped-down Disciple for the +2A / +3 rear-edge connector).
- **Romantic Robot** — released the **Multiface One** (not a disk interface per se, but a RAM-based backup device) and the **MB-02** (a disk interface).
- **Sinclair Research** — released the **ZX Interface 1 + Microdrive** (1983) and considered, but never released, an official 3" floppy interface.

The Opus Discovery was the first of these — and the one that defined the **MGT logical disk format**, which was subsequently adopted by the Disciple, the +D, and (with extensions) by MGT's own SAM Coupé computer in 1989.

### 1.2 The Opus Discovery vs TR-DOS vs +3DOS

| Property | TR-DOS 5.x | +3DOS | Opus Discovery |
|---|---|---|---|
| **Origin** | USSR (~1985) | UK / Amstrad (1987) | UK / Opus (1984) |
| **Based on** | Custom | CP/M 2.2 | MGT format |
| **Floppy controller** | KR1818VG93 (WD1793 clone) | WD1772-PH | WD1770 |
| **Disk size** | 800 KB DSDD | 720 KB DSDD | 400 KB SSDD or 800 KB DSDD |
| **Sectors per track** | 10 × 512 B | 9 × 512 B | 10 × 512 B |
| **Filesystem** | Custom | CP/M (FCB + extents) | MGT (file entries + sector allocation) |
| **Filename length** | 8 + 1-char ext | 8 + 3-char ext | 8 + 1-char ext (with "type" byte) |
| **File attributes** | None | RO, SYS, ARCH | None |
| **Adoption** | USSR + later Russian clones | +3, +2A | UK + SAM Coupé |

The Opus Discovery and TR-DOS share the same physical geometry (80-track, 10-sector, 512-byte sectors = 800 KB DSDD) but use **completely different logical formats** — an Opus disk cannot be read by a TR-DOS machine, and vice versa.

### 1.3 A short history

The Opus Discovery was launched in 1984 by **Opus Supplies Ltd** (London, UK) as a complete disk subsystem: an Opus-branded 3" drive, a built-in interface that plugged into the Spectrum 48K's rear edge connector, and a built-in DOS ROM (8 KB). The system was aimed at home users who wanted more reliable storage than the Microdrive, and at small businesses that wanted to use the Spectrum as a budget business machine.

In 1985, MGT released the **Disciple** — a more flexible (but more expensive) interface that supported two floppy drives, a printer, a network port, and a passthrough edge connector. MGT used essentially the same logical disk format as the Opus Discovery, which is why the format is generally called **MGT** (after Miles Gordon Technology, not Opus).

In 1987, MGT released the **+D** — a simplified Disciple for the new Spectrum +2A and +3, which used the +2A/+3's rear-edge connector. The +D also used the MGT format.

In 1989, MGT released the **SAM Coupé**, a Spectrum-compatible computer. The SAM Coupé used an extended MGT format (with longer filenames and larger disks), but the basic structure remained the same.

Opus Supplies Ltd went out of business in the late 1980s, but the Opus Discovery remained in use throughout the Spectrum's commercial lifetime. Today, the Opus Discovery is rare in physical form, but the MGT format (in the form of `.MGT` disk images) is widely used by Spectrum emulators.

### 1.4 Scope

This article covers the Opus Discovery's **hardware** (the WD1770 controller and port map) and **disk format** (the MGT logical layout). The related **TR-DOS** format is covered in [trd_disk_format.md](trd_disk_format.md); the **+3DOS** format is covered in [plus3_dos_format.md](plus3_dos_format.md); the **CP/M** format is covered in [cpm_disk_format.md](cpm_disk_format.md); a high-level comparison of all Spectrum disk formats is in [disk_format_overview.md](disk_format_overview.md).


## §2. The Hardware

### 2.1 The major components

The Opus Discovery is an **external subsystem**: it plugs into the Spectrum 48K's rear edge connector and provides a complete disk controller plus (typically) a single 3" Hitachi-compatible drive in the same case. The major components are:

| Component | Purpose | Notes |
|---|---|---|
| **WD1770-PH FDC** | The floppy controller chip | 28-pin DIP. Pin- and register-compatible with the WD1772-PH used in the +3, and a near-sibling of the WD1793 used in the Beta Disk Interface. See §2.4 for differences. |
| **Address-decode logic** (74LS-series TTL) | Decodes two I/O ports for the WD1770 and generates `/CS`, `A0`, `A1` | A small board of discrete logic chips — no PAL/GAL on early revisions. |
| **Control latch** (74LS273 octal D-type) | Holds drive-select, motor, side-select, and density bits | One write-only port; the WD1770 itself does not control drive select or motor. |
| **8 KB DOS ROM** | The Opus Discovery's DOS firmware | Paged into the Spectrum's `#0000–#1FFF` window when active. See §2.3. |
| **Edge-connector passthrough** | Allows other peripherals to be daisy-chained behind the Opus | Notch-detect and `/BUSREQ` logic for shared bus. |
| **3" drive unit** | One or two single-sided 40-track drives (Hitachi HFD-305S or equivalent) | Same drive as the +3 — single-sided, 40-track, caddy-loaded. |
| **Clock oscillator** | 8 MHz crystal | Drives the WD1770's CLK pin. 8 MHz → 250 kbit/s MFM data rate. |

Unlike the +3, where the WD1772-PH is soldered to the motherboard, the Opus Discovery's controller lives in the external box with the drive. The Spectrum sees only an extension of its I/O port space and a paged ROM.

### 2.2 Signal flow

```
              ┌─────────────────────────────────────┐
              │           ZX Spectrum 48K           │
              │   Z80 @ 3.5 MHz                     │
              │                                     │
              │   /IORQ, A0..A7, D0..D7, /M1, /ROMCS│
              └────────┬────────────────────────────┘
                       │  rear edge connector (48-way)
                       ▼
       ┌────────────────────────────────────┐
       │  Opus Discovery PCB                │
       │                                    │
       │  ┌──────────────────────────────┐  │
       │  │ Address-decode TTL           │  │
       │  │ ports #E3, #E7 → WD1770      │  │
       │  │ port #1F → control latch     │  │
       │  └──────┬───────────────────────┘  │
       │         │ /CS, A0, A1              │
       │         ▼                          │
       │  ┌──────────────────┐              │
       │  │ WD1770-PH FDC    │              │
       │  └──────┬───────────┘              │
       │         │ /STEP,/DIR,/WD,/WG,/RD   │
       │         ▼                          │
       │  ┌──────────────────┐              │
       │  │ 34-pin Shugart   │              │
       │  │ cable → drive    │              │
       │  └──────────────────┘              │
       └────────────────────────────────────┘
```

The most important contrast with the +3's block diagram ([plus3_floppy.md §2.2](plus3_floppy.md)) is that **drive-select and motor control go through a separate 74LS273 latch**, not through the Spectrum's `#7FFD` port. The Opus Discovery predates the +3 by three years and has no access to the +3's configuration latch — it must provide its own.

### 2.3 The I/O port map

The Opus Discovery uses three I/O ports:

| Port | Read (`IN`) | Write (`OUT`) | Action |
|---|---|---|---|
| `#E3` | Status register | Command register | WD1770 register 0 (A0=0, A1=0). |
| `#E7` | Track/Sector/Data | Track/Sector/Data | WD1770 registers 1/2/3 (decoded by `A0`, `A1`). |
| `#1F` | (floating) | Control latch | Drive-select, motor-on, side-select, density. |

The port-decoding is the inverse of the +3's pattern: where the +3 decodes `A5,A6 = 0,1`, the Opus decodes `A5,A6,A7 = 1,1,1` (i.e. ports in the `#E0–#FF` range). The control latch at `#1F` is a separate decode that intentionally collides with the Spectrum's `#1F` Kempston joystick port — but since the Opus latches only on `OUT`, the read-side collision is harmless.

The control-latch bit layout is:

| Bit | Function |
|---|---|
| 0 | Drive 0 select (active low) |
| 1 | Drive 1 select (active low) |
| 2 | Side select (0 = side 0, 1 = side 1) |
| 3 | Motor on (0 = on, 1 = off) |
| 4 | Density (0 = FM/single, 1 = MFM/double) |
| 5–7 | Unused (tied to 0) |

### 2.4 The WD1770 vs the WD1772 and WD1793

The Opus's WD1770 is the **immediate predecessor** of the +3's WD1772-PH. The two chips are register-compatible (Status/Cmd, Track, Sector, Data) and use the same Type I/II/III/IV command structure (see [fdc_vg93.md §4](fdc_vg93.md) for the command family). The differences are minor:

- **Step rate.** The WD1770 supports 6/12/20/30 ms step rates; the WD1772-PH adds a 2 ms "turbo" rate. Opus Discovery drives are usually 20 ms (single-sided 40-track).
- **Internal PLL.** Both chips have an internal data separator, unlike the older WD1793 used in the Beta Disk Interface. The Opus Discovery therefore has no external data-separator circuitry.
- **Pinout.** The WD1770 and WD1772-PH share a 28-pin DIP footprint but differ in pin assignment — they are **not** drop-in interchangeable.

Compared to the Beta Disk Interface's WD1793 ([fdc_vg93.md §3](fdc_vg93.md)), the WD1770 is a newer, simpler design with internal PLL and single 5 V supply (no separate +12 V / −5 V needed).

---

## §3. The Physical Disk Format

### 3.1 Geometry

The Opus Discovery's standard physical geometry is **identical** to that of the TR-DOS Beta Disk Interface: 80-track DSDD or 40-track SSDD, with 10 sectors per track and 512 bytes per sector.

| Parameter | SSDD (single-sided) | DSDD (double-sided) |
|---|---|---|
| **Cylinders (tracks per side)** | 40 | 80 |
| **Sides (heads)** | 1 | 2 |
| **Sectors per track** | 10 | 10 |
| **Sector size** | 512 bytes | 512 bytes |
| **Total formatted capacity** | 40 × 1 × 10 × 512 = **200 KB** | 80 × 2 × 10 × 512 = **800 KB** |
| **Encoding** | MFM | MFM |
| **Bit rate** | 250 kbps | 250 kbps |
| **Rotation speed** | 300 RPM | 300 RPM |

The 800 KB DSDD figure matches TR-DOS exactly (see [trd_disk_format.md §2](trd_disk_format.md)). The 200 KB SSDD figure is the original Opus Discovery format (1984, when double-sided drives were rare and expensive). Most surviving disks and disk images are 800 KB DSDD.

### 3.2 Sector IDs

Every sector on an Opus disk has the standard IBM 3740-style 4-byte **address field** (CHN — Cylinder, Head, Sector, size-code) plus the 512-byte **data field**. See [mfm_encoding.md](mfm_encoding.md) for the full gap/address-mark/data-mark structure.

The 4-byte address field on a standard Opus disk is:

| Byte | Field | Typical value |
|---|---|---|
| 0 | Cylinder (C) | 0–79 |
| 1 | Head (H) | 0 or 1 |
| 2 | Sector (N) | 1–10 |
| 3 | Size code | `0x02` (= 512 bytes) |

Sector numbering is **1-based** (sector 1 is the first sector in the track). This is the same convention as TR-DOS and the opposite of the +3DOS / CP/M convention (which also uses 1-based numbering, but with 9 sectors per track instead of 10).

### 3.3 MFM encoding

The Opus Discovery uses standard **MFM** (Modified Frequency Modulation) at 250 kbit/s, exactly as described in [mfm_encoding.md](mfm_encoding.md). The WD1770 handles the bit-level encoding and decoding in hardware; the CPU sees only 512-byte sector buffers.

There is no proprietary flux-level encoding, no copy-protection trickery, and no "long sectors" — every Opus disk ever made is a standard IBM 3740 MFM disk. This is one reason why the `.MGT` disk-image format (§5) is so simple.

### 3.4 Track layout

A standard Opus track (10 sectors, 512 bytes each, MFM) is laid out as:

```
┌─────────┬─────────┬──────┬───────┬───────┬─────────┬─────┬───────┬───────┐
│ GAP4a   │ INDEX   │ GAP1 │ SECT1 │ GAP2 │ SECT2   │ ... │ SECT10│ GAP4b │
│ 80 bytes│ AM      │ 50 B │ 622 B │ 22 B │ 622 B   │     │ 622 B │ ??    │
└─────────┴─────────┴──────┴───────┴───────┴─────────┴─────┴───────┴───────┘
```

Each sector (`SECTn`) is 622 bytes total = 12-byte preamble + sync + AM + 4-byte CHN + 2-byte CRC + 22-byte GAP + sync + DM + 512-byte data + 2-byte CRC + 22-byte GAP. Total track size ≈ 6250 bytes — the same as a TR-DOS track.

### 3.5 Single-sided vs double-sided switching

The Opus Discovery control-latch **side-select bit** (bit 2 of port `#1F`) toggles which head is active. Unlike the +3's "reverse side" trick ([plus3_dos_format.md §2.2](plus3_dos_format.md)), the Opus Discovery reads both sides in **normal cylinder order**:

- Sectors 0–199 (SSDD) or 0–399 (DSDD): side 0, cylinder 0 (sectors 1–10), cylinder 1 (sectors 1–10), ..., cylinder 39 (or 79).
- Sectors 200–399 (SSDD) or 400–799 (DSDD): side 1, cylinder 0 (sectors 1–10), cylinder 1 (sectors 1–10), ..., cylinder 39 (or 79).

This is **interleaved ordering** (cylinder 0 side 0, cylinder 0 side 1, cylinder 1 side 0, cylinder 1 side 1, ...), which is the simplest possible mapping and is also what most non-CP/M formats use.

---

## §4. The Logical Disk Format (MGT)

### 4.1 Overview: a completely different design from CP/M and TR-DOS

The MGT logical format is **neither CP/M-like nor TR-DOS-like**. It combines features of both:

- From TR-DOS: **sector-based allocation** (no 1 KB block abstraction like CP/M).
- From CP/M: **per-file metadata in a directory** (no flat sector list like TR-DOS).
- Unique to MGT: **256-byte directory entries** with a per-file **sector bitmap**.
- Unique to MGT: **linked-list sector chaining** — the last 2 bytes of every file sector point to the next sector.

The result is a format that supports files up to 800 KB on a single disk (large enough to fill the entire disk with one file), with random-access capability (via the bitmap) and resilient sequential access (via the linked list).

### 4.2 The side-encoded-in-track trick

The most unusual feature of MGT sector addressing is the **side bit encoded in the track number**:

- Tracks **0–79** refer to side 0, cylinders 0–79.
- Tracks **128–207** refer to side 1, cylinders 0–79.

This means a single byte (`0x00`–`0xCF`) can address any track on either side of the disk, with `0x80` (128) being the "side 1" flag. Sectors are then addressed as `(track, sector)`, where `sector` is 1–10.

For example:
- `(track=0, sector=1)` → side 0, cylinder 0, sector 1 (first sector on the disk).
- `(track=4, sector=1)` → side 0, cylinder 4, sector 1 (first sector after the directory).
- `(track=128, sector=1)` → side 1, cylinder 0, sector 1 (first sector on side 1).
- `(track=207, sector=10)` → side 1, cylinder 79, sector 10 (last sector on the disk).

This trick is used everywhere in MGT — directory entries, sector maps, and the linked-list pointers all use it. It is also the reason why the Opus Discovery can support up to 80 tracks per side with a single-byte track number.

### 4.3 The directory tracks

The MGT directory occupies the **first four tracks on side 0** (tracks 0–3):

- Track 0: 10 sectors × 512 bytes = 5120 bytes
- Tracks 0–3 total: **20 480 bytes** = 40 sectors

Since each directory entry is 256 bytes (§4.4), 20 480 / 256 = **80 directory entries** — the standard MGT directory size.

MasterDOS (a later SAM Coupé DOS) allows the directory to extend by up to 35 additional tracks (track 4 onwards), giving up to 780 entries — but the original Opus Discovery / GDOS / G+DOS formats are limited to 80.

### 4.4 The 256-byte directory entry

Each MGT directory entry is **256 bytes** — eight times the size of a TR-DOS or CP/M entry. The bulk of the entry is a **per-file sector bitmap** (195 bytes), which lets the DOS know which sectors are allocated to that specific file.

| Offset | Length | Field |
|---|---|---|
| 0 | 1 | **Type byte.** Bits 0–4 = file type (see §4.5), bit 6 = protected, bit 7 = hidden. |
| 1 | 10 | **Filename.** 10 ASCII characters, space-padded. First byte = `0x00` marks an empty/erased entry. |
| 11 | 2 | **Sector count.** Number of 512-byte sectors used by the file. **Big-endian** (MSB first — unusual). |
| 13 | 1 | **First sector track.** Track number of the file's first data sector (uses the side-encoded convention, §4.2). |
| 14 | 1 | **First sector number.** Sector number within that track (1–10). |
| 15 | 195 | **Sector bitmap.** One bit per sector, starting from track 4 sector 1. Set bit = sector allocated to this file. |
| 210 | 10 | **DISCiPLE / +D file info** (see §4.6). |
| 220 | 12 | **SAM Coupé file info** (mostly unused on the Spectrum). |
| 232 | 4 | Spare bytes (set to `0xFF` under SAMDOS). |
| 236 | 9 | **SAM start/length info** (mostly unused on the Spectrum). |
| 245 | 5 | **MasterDOS timestamp** (day/month/year/hour/minute) — set to `0xFF` under the original DOSes. |
| 250 | 6 | Reserved for UNI-DOS / MasterDOS extensions. |

### 4.5 File types

The low 5 bits of the type byte encode the file type. The most common types on Spectrum disks are:

| Type | Meaning |
|---|---|
| 0 | Erased / empty entry |
| 1 | ZX BASIC program |
| 2 | ZX numeric array |
| 3 | ZX string array |
| 4 | ZX code (binary) |
| 5 | ZX 48K snapshot |
| 6 | ZX Microdrive image |
| 7 | ZX screen (`SCREEN$`) |
| 8 | Special |
| 9 | ZX 128K snapshot |

The SAM Coupé later extended this list with types 16–31 (SAM BASIC, SAM code, MasterDOS subdirectory, etc.). Type 0 is the "eraser" marker — when a file is deleted, only the type byte is set to 0; the rest of the entry is left intact until reused.

### 4.6 The 9-byte Spectrum header

Most Spectrum file types (BASIC, arrays, code) carry a **9-byte file header** at the start of the file's first data sector. This header is identical to the TAP-format header (see [tap_format.md](tap_format.md)) and contains:

| Offset | Length | Field |
|---|---|---|
| 0 | 1 | File type (0=BASIC, 1=number array, 2=char array, 3=code) |
| 1 | 2 | Data length (LE) |
| 3 | 2 | Parameter 1 (autostart line / start address) (LE) |
| 5 | 2 | Parameter 2 (LE) |
| 7 | 2 | Reserved |

A snapshot file (type 5) uses bytes 210–241 of the directory entry to store a **register dump** (IY, IX, DE', BC', HL', AF', DE, BC, HL, junk, I, SP, F, R, AF, PC) instead of a 9-byte header in the data.

### 4.7 Linked-list sector chaining

In addition to the per-file sector bitmap, MGT uses a **linked-list scheme**: the **last 2 bytes of every file sector** contain the track and sector number of the next sector in the file. For the last sector, both bytes are `0x00`.

```
┌────────────────────────────────────────────────────────────┐
│ Sector (track=4, sector=1) — first sector of file         │
│   bytes 0–509: 510 bytes of file data                      │
│   byte 510: next track   = 4                               │
│   byte 511: next sector  = 2                               │
└────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌────────────────────────────────────────────────────────────┐
│ Sector (track=4, sector=2)                                 │
│   bytes 0–509: 510 bytes of file data                      │
│   byte 510: next track   = 4                               │
│   byte 511: next sector  = 3                               │
└────────────────────────────────────────────────────────────┘
                          │
                          ▼
                       ... etc ...
                          │
                          ▼
┌────────────────────────────────────────────────────────────┐
│ Sector (track=128, sector=10) — last sector                │
│   bytes 0–509: 510 bytes of file data                      │
│   byte 510: next track   = 0   ← end-of-file marker        │
│   byte 511: next sector  = 0                               │
└────────────────────────────────────────────────────────────┘
```

This means a file sector holds only **510 bytes of file data** (not 512), with 2 bytes sacrificed for the pointer. The trade-off is robustness: even if the directory's bitmap is corrupted, files can still be recovered by following the sector chain.

---

## §5. The `.MGT` Disk Image Format

### 5.1 A simple sector dump

The `.MGT` disk-image file format is one of the simplest in existence: it is a **raw sector dump** of the disk, in track/sector order, with **no header and no metadata**.

For a standard 800 KB DSDD disk:

- File size: **819 200 bytes** (= 80 × 2 × 10 × 512).
- Byte 0 = first byte of track 0, side 0, sector 1.
- Bytes 0–5119 = track 0, side 0 (sectors 1–10).
- Bytes 5120–10 239 = track 0, side 1 (sectors 1–10).
- Bytes 10 240–15 359 = track 1, side 0 (sectors 1–10).
- ...and so on, alternating side 0 / side 1 for 80 tracks.
- Bytes 814 080–819 199 = track 79, side 1 (sectors 1–10).

This is the **interleaved-side ordering** (cylinder 0 side 0, cylinder 0 side 1, cylinder 1 side 0, ...) — matching the physical read order, not the logical "side-encoded" sector addressing.

### 5.2 No magic number, no header

A `.MGT` file has no magic number, no version field, and no embedded geometry. The reader must **assume** the standard geometry (800 KB DSDD, 80 × 2 × 10 × 512). If the file is a different size — for example, a 200 KB SSDD disk — it is up to the consumer to detect this from the file size alone.

Common `.MGT` file sizes:

| File size | Disk geometry |
|---|---|
| 204 800 bytes | 40-track SSDD (40 × 1 × 10 × 512) — original Opus Discovery |
| 409 600 bytes | 80-track SSDD (80 × 1 × 10 × 512) |
| 409 600 bytes | 40-track DSDD (40 × 2 × 10 × 512) — most SAM Coupé disks |
| 819 200 bytes | 80-track DSDD (80 × 2 × 10 × 512) — standard MGT |

### 5.3 Reading a file from a `.MGT` image

To read a file at directory slot N from a `.MGT` image:

1. Locate the directory entry: bytes `N × 256` to `N × 256 + 255` in the file (slots 0–79).
2. Read the type byte (offset 0). If it is 0, the entry is empty — skip.
3. Read the filename (offsets 1–10) and the file info (offsets 210–219).
4. Read the **first-sector track** (offset 13) and **first-sector number** (offset 14).
5. Compute the physical byte offset of that sector in the `.MGT` file:
   ```python
   def sector_offset(track, sector):
       side = 1 if (track & 0x80) else 0
       cylinder = track & 0x7F
       # Interleaved ordering: side 0 of cylinder N is at offset N*10240,
       # side 1 of cylinder N is at offset N*10240 + 5120.
       return (cylinder * 2 + side) * 5120 + (sector - 1) * 512
   ```
6. Read 512 bytes at that offset — the first 510 bytes are file data, bytes 510–511 are the next-sector pointer.
7. If both pointer bytes are 0, stop. Otherwise, decode the next `(track, sector)` and repeat.

### 5.4 Variants: `.DCK`, `.DSQ`, `.IMG`

Some emulators use slightly different file extensions for MGT-format images:

- **`.MGT`** — the standard, original extension.
- **`.IMG`** — used by some Spectrum emulators (Fuse, Spectaculator) as a generic "raw sector dump" extension.
- **`.DSQ`** — used for SAM Coupé disks that include a 32-byte header with geometry info.
- **`.DCK`** — used for "disc-pack" multi-disk archives (rare).

The actual byte content is identical to `.MGT` for `.IMG` files. `.DSQ` and `.DCK` are extension-specific and not interchangeable with `.MGT`.

---

## §6. Variants — the Disciple, the +D, and the SAM Coupé MGT derivatives

### 6.1 The DISCiPLE (MGT, 1985)

The **MGT DISCiPLE** (released 1985) is essentially a more capable Opus Discovery. It uses the same WD1770 floppy controller, the same 800 KB DSDD geometry, and the same MGT logical format. The differences are:

- **Two floppy-drive support** (the Opus Discovery was single-drive).
- **Edge-connector passthrough** for daisy-chaining other peripherals.
- **Network port** for connecting two Spectrums (a primitive LAN).
- **Printer port** (Centronics parallel).
- **16 KB ROM** (vs the Opus's 8 KB) — includes a more sophisticated DOS ("GDOS").

A DISCiPLE disk can be read by an Opus Discovery and vice versa, as long as the file system is MGT (which it almost always is).

### 6.2 The +D (MGT, 1987)

The **+D** (1987) is a stripped-down DISCiPLE for the Spectrum +2A / +3 rear-edge connector. It removes the network port and the edge-connector passthrough but keeps:

- The WD1770 controller.
- The 800 KB DSDD MGT format.
- The floppy drive and Centronics ports.

The +D's DOS is called **G+DOS**. It is binary-compatible with GDOS at the disk-format level.

### 6.3 The SAM Coupé (MGT, 1989)

In 1989, MGT released the **SAM Coupé**, a Spectrum-compatible computer with improved hardware (256-color palette, 4-channel sound, 32 KB ROM with built-in DOS). The SAM Coupé uses an extended MGT format called **SAMDOS 2**:

- Same physical geometry (80 × 2 × 10 × 512 = 800 KB).
- Same 256-byte directory entry layout.
- **Extended file types** (16–31: SAM BASIC, SAM code, SAM screen, MasterDOS subdirectory).
- **Boot sector** at the first sector of track 4 (offset `0x100` = "BOOT" magic string).
- Later DOSes (MasterDOS, B-DOS) extended the directory up to 35 additional tracks (up to 780 entries).

A SAM Coupé disk can be read by an Opus Discovery / DISCiPLE / +D as long as the file types used are within the 1–9 Spectrum range. SAM-specific file types (16+) will appear as garbage on a Spectrum DOS.

### 6.4 Compatibility matrix

| Reader → | Opus | DISCiPLE/+D | SAM Coupé |
|---|---|---|---|
| **Opus disk** | ✓ | ✓ | ✓ (mostly) |
| **DISCiPLE/+D disk** | ✓ | ✓ | ✓ (mostly) |
| **SAM Coupé disk** | partial | partial | ✓ |
| **TR-DOS disk** | ✗ | ✗ | ✗ |
| **+3DOS / CP/M disk** | ✗ | ✗ | ✗ |

The MGT family is mutually compatible at the disk-format level. TR-DOS and +3DOS use **completely different** formats and cannot read MGT disks without conversion utilities.

---

## §7. Tools and Editors

### 7.1 Emulators with MGT support

Almost every modern Spectrum emulator supports `.MGT` disk images natively:

| Emulator | Platform | MGT support | Notes |
|---|---|---|---|
| **Fuse** | Windows, Linux, macOS | ✓ | Reads `.MGT`, `.IMG`. Supports Opus Discovery, +D, DISCiPLE, SAM Coupé. |
| **Spectaculator** | Windows | ✓ | Commercial emulator; full MGT support. |
| **ZX Spin** | Windows | ✓ | Popular demoscene emulator. |
| **UnrealSpeccy / UnrealSpeccy Portable** | Windows / Linux | ✓ | Russian emulator with strong Pentagon/Scorpion support; also reads MGT. |
| **SAM Coupé emulators** (SimCoupé) | Multi-platform | ✓ | Native SAM format; reads SAM-flavoured MGT disks. |

### 7.2 Conversion utilities

- **`samdisk`** — a modern multi-format converter by Owen Dunn. Reads and writes `.MGT`, `.DSK`, `.EDSK`, `.HFE`, `.SCP`. Recommended for archival use.
- **`diskimage.py`** — a Python library for manipulating `.MGT`, `.TRD`, `.DSK` images. Useful for batch conversion.
- **`zxmgt`** — a small command-line utility to extract files from `.MGT` images to host filesystem.

### 7.3 Python parser for `.MGT` directories

```python
def parse_mgt_directory(img):
    """Parse the 80-entry directory of a .MGT disk image (bytes)."""
    assert len(img) == 819200, f"Expected 800 KB MGT image, got {len(img)} bytes"
    files = []
    for slot in range(80):
        entry = img[slot * 256 : (slot + 1) * 256]
        type_byte = entry[0]
        if type_byte & 0x1F == 0:
            continue  # erased / empty entry
        name      = entry[1:11].decode("ascii", "replace").rstrip()
        nsec_hi   = entry[11]
        nsec_lo   = entry[12]
        nsec      = (nsec_hi << 8) | nsec_lo  # big-endian!
        first_trk = entry[13]
        first_sec = entry[14]
        first_side = 1 if (first_trk & 0x80) else 0
        first_cyl  = first_trk & 0x7F
        protected  = bool(type_byte & 0x40)
        hidden     = bool(type_byte & 0x80)
        ftype      = type_byte & 0x1F
        files.append({
            "slot":     slot,
            "name":     name,
            "type":     ftype,
            "sectors":  nsec,
            "first":    (first_cyl, first_side, first_sec),
            "ro":       protected,
            "hidden":   hidden,
        })
    return files

def read_mgt_file(img, entry):
    """Read a file's data by following the linked-list chain."""
    track, sector = entry["first"][0] | (entry["first"][1] << 7), entry["first"][2]
    data = b""
    while True:
        side = 1 if (track & 0x80) else 0
        cyl  = track & 0x7F
        off  = (cyl * 2 + side) * 5120 + (sector - 1) * 512
        raw  = img[off : off + 512]
        data += raw[:510]            # 510 bytes of file data
        next_track, next_sector = raw[510], raw[511]
        if next_track == 0 and next_sector == 0:
            break                    # end-of-file marker
        track, sector = next_track, next_sector
    return data
```

This reads a file by following the linked-list sector chain (§4.7) without consulting the bitmap — the most robust recovery path.

### 7.4 Gotchas

- **Big-endian sector counts.** MGT stores the sector count (bytes 11–12 of the directory entry) in **big-endian** order, unlike every other Spectrum disk format (which is little-endian). This is the single most common bug in MGT parsers.
- **The "side bit" in the track number.** Many naive parsers assume track numbers 0–159 are sequential, missing the side-encoded convention (0–79 for side 0, 128–207 for side 1).
- **The 2-byte pointer sacrifice.** A file sector holds only **510 bytes of data**, not 512. Code that reads sector-by-sector without accounting for the pointer will silently corrupt every file.
- **File type 0 does not mean "BASIC"** — it means "erased". This is the opposite of TR-DOS, where type 0 is BASIC.

---

## §8. Cross-references and License

### 8.1 Related articles in this Knowledge base

- [mfm_encoding.md](mfm_encoding.md) — the **MFM signal layer** that physically encodes every Opus disk's data.
- [fdc_vg93.md](fdc_vg93.md) — the **WD1793 / KR1818VG93 floppy controller** used by the Beta Disk Interface. The Opus's WD1770 is a near-sibling; this article covers the shared Type I/II/III/IV command structure.
- [beta_disk_interface.md](beta_disk_interface.md) — the **Beta Disk Interface** hardware (the Soviet alternative to the Opus Discovery).
- [plus3_floppy.md](plus3_floppy.md) — the **Spectrum +3's floppy hardware** (uses the WD1772-PH, a successor to the WD1770).
- [trd_disk_format.md](trd_disk_format.md) — the **TR-DOS logical disk format** (the Soviet alternative to MGT).
- [plus3_dos_format.md](plus3_dos_format.md) — the **+3DOS logical disk format** (the CP/M-derived UK alternative to MGT).
- [cpm_disk_format.md](cpm_disk_format.md) — the **CP/M 2.2 disk format** on the Spectrum family.
- [dsk_fdi_formats.md](dsk_fdi_formats.md) — the **`.DSK` / `.EDSK` / `.FDI` disk-image formats**, which can hold Opus disks at the sector level (alternative to `.MGT`).
- [scp_format.md](scp_format.md) — the **`.SCP` flux-level image format**, for capturing Opus disks at the magnetic-transition level.
- [udi_format.md](udi_format.md) — the **`.UDI` format**, another flux-level alternative.
- [disk_format_overview.md](disk_format_overview.md) — a **high-level comparison** of all Spectrum floppy formats.

### 8.2 External references

- **The RAMSOFT DISCiPLE / +D Technical Guide** — the canonical reference for the MGT format on the Spectrum, including detailed byte-level layout of directory entries.
- **John Garner's +D Information** — practical guide to the +D's hardware and DOS.
- [SAM Coupé Technical Manual](https://www.worldofspectrum.org/) — the SAM-specific extensions to MGT (SAMDOS 2, MasterDOS).
- [The Sinclair Wiki MGT filesystem page](https://sinclair.wiki.zxnet.co.uk/wiki/MGT_filesystem) — the most authoritative online source for the MGT format; this article draws heavily on it.
- [World of Spectrum](https://worldofspectrum.org/) — Spectrum software archive; many `.MGT` images available for download.

### 8.3 License

This article is licensed under the **Creative Commons Attribution-ShareAlike 4.0 International License (CC BY-SA 4.0)** — see `https://creativecommons.org/licenses/by-sa/4.0/`.

You are free to:

- **Share** — copy and redistribute the material in any medium or format.
- **Adapt** — remix, transform, and build upon the material for any purpose, even commercially.

Under the following terms:

- **Attribution** — You must give appropriate credit (attribution to the Knowledge base project), provide a link to the license, and indicate if changes were made.
- **ShareAlike** — If you remix, transform, or build upon the material, you must distribute your contributions under the same license as the original.

The full legal text is available at the link above.

The trademarks **ZX Spectrum**, **ZX Spectrum +3**, **ZX Spectrum +2A**, **Opus Discovery**, **Opus Supplies Ltd**, **Miles Gordon Technology**, **MGT**, **DISCiPLE**, **+D**, **SAM Coupé**, **SAMDOS**, **GDOS**, **G+DOS**, **MasterDOS**, **B-DOS**, **UNI-DOS**, **Beta DOS**, **WD1770**, **WD1772**, **WD1772-PH**, **WD1793**, **Hitachi HFD-305S**, **Western Digital**, **Shugart**, **Gotek**, **FlashFloppy**, **HxC**, and others mentioned in this document are the property of their respective owners and are used here for identification and educational purposes only. No endorsement by, or affiliation with, any of these trademark holders is implied.
