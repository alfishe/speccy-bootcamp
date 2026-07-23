# .SCP (SuperCard Pro) Flux-Level Disk Image Format

**Scope:** The **.SCP** (SuperCard Pro) format — a **flux-level** disk image format that captures the disk at the lowest possible level: the raw timing of magnetic flux transitions on the disk surface. The .SCP format is the modern gold standard for floppy-disk preservation, capable of representing any disk that any FDC could write (and many that no FDC could write — deliberately weak bits, spurious transitions, custom modulation schemes, etc.).

**Audience:** Archival tool authors, copy-protection researchers, demoscene preservationists, and anyone who needs to image floppy disks at the highest possible fidelity. The .SCP format is hardware-specific: producing a .SCP file requires a **SuperCard Pro** hardware device (or a compatible flux-level reader, such as KryoFlux, GreaseWeazle, or the DiskFerret).

**Prerequisites:** A solid understanding of the MFM / FM signal layers (see [mfm_encoding.md](mfm_encoding.md)) and of the simpler sector-level formats (.DSK / .EDSK, .TRD, .SCL — see [dsk_fdi_formats.md](dsk_fdi_formats.md), [trd_scl_formats.md](trd_scl_formats.md)). The .SCP format operates **below** the sector layer, so familiarity with the lower-level floppy format is essential.

**Depth:** Deep. Byte-level layout of the .SCP format, including the header, the track-index table, the per-track flux data, and the conventions for multi-revolution sampling. Worked examples and detailed discussion of the trade-offs versus .EDSK and .UDI.

---

## §1. What .SCP Is

### 1.1 Flux-level preservation

Every other disk-image format discussed in this storage section (.TRD, .SCL, .DSK, .EDSK, .FDI, .UDI) operates at the **sector level** — the format captures the per-sector data, the per-sector IDs, and (sometimes) the per-sector error flags. The sector level is the right level for most use cases (running software, distributing disk images, doing basic archival work).

But the sector level is **insufficient** for true preservation. A real floppy disk does not store sectors — it stores **magnetic flux transitions**, which an FDC (Floppy Disk Controller) chip interprets as MFM- or FM-encoded bits, which in turn are grouped into sectors by the FDC. Anything that the FDC cannot interpret (or interprets inconsistently) is lost at the sector level. This includes:

- **Weak / fuzzy bits** that read as different values on different revolutions.
- **Spurious transitions** that confuse the FDC's PLL.
- **Non-standard modulation schemes** (custom GCR variants, deliberate timing variations).
- **Copy-protection tricks** that depend on specific flux patterns rather than sector contents.
- **Bit cells with non-standard widths** (caused by drive-speed variation or deliberate bit-shifting).
- **Long sync gaps** or other unusual pre-sector formatting.

The **flux level** is the lowest useful level for digital preservation: it captures every magnetic transition on the disk surface, as a sequence of timing intervals between transitions. A flux-level image can be re-interpreted by an emulator (using a virtual FDC) to extract the sector-level data, but it also captures everything that the FDC would have discarded.

The .SCP format is one of several flux-level formats in use today (others include the KryoFlux raw stream format, the GreaseWeazle format, and the older DiskFerret format). The .SCP format is distinguished by being:

- **Open** (the specification is published).
- **Self-contained** (each .SCP file contains all the flux data for the entire disk).
- **Multi-revolution** (each track can be sampled up to 5 times, to characterize weak-bit behaviour).
- **Modulation-agnostic** (the format stores raw flux timings, not MFM-decoded bits).

### 1.2 The SuperCard Pro hardware

The .SCP format was created by **Jim Drew** of **CBM Electronics** as the native format of the **SuperCard Pro** hardware device. The SuperCard Pro is a USB-connected flux-level floppy-disk reader that can image disks from almost any 3.5", 5.25", or 8" floppy drive.

The SuperCard Pro hardware samples the floppy drive's read-amplifier output at 25 MHz, measuring the time between consecutive flux transitions to a resolution of 40 ns. This is sufficient to capture the bit-cell timings of all common floppy-disk formats, including the high-density 1 Mbps formats used by late-1980s computers.

Other flux-level readers in use today:

- **KryoFlux** (by the KryoFlux team, ~2010) — a USB-connected reader with its own raw-stream format. Can convert to .SCP via third-party tools.
- **GreaseWeazle** (by Keir Fraser, 2018) — an open-source USB reader, originally based on a STM32 board. Reads and writes .SCP natively.
- **DiskFerret** (an older format, ~2010) — supports its own format and can convert to / from .SCP.
- **a2floppy** (Apple II-focused) — supports .SCP for cross-platform interchange.

The .SCP format has emerged as the de facto interchange format for flux-level imaging, regardless of which hardware device is used to capture the flux.

### 1.3 .SCP vs. .EDSK / .UDI

| Property | .EDSK | .UDI | .SCP |
|---|---|---|---|
| **Level** | Sector | Sector | Flux |
| **Multi-revolution** | No | No | Yes (up to 5) |
| **Modulation** | MFM only | MFM / FM / GCR / other | Raw flux (modulation-agnostic) |
| **Weak-bit fidelity** | Single representative sample | Single representative sample | Multi-revolution characterisation |
| **Copy-protection preservation** | Partial (per-sector CRC flag) | Partial (per-sector flags) | Full (raw flux pattern) |
| **Typical file size** | 100 KB – 1 MB | 100 KB – 1 MB | 5 MB – 50 MB |
| **Tool support** | Universal | Limited (Russian) | Growing rapidly |
| **Hardware required to produce** | None (any FDC) | None (any FDC) | SuperCard Pro / KryoFlux / GreaseWeazle |

The .SCP format is **strictly more expressive** than .EDSK and .UDI: anything that can be represented in .EDSK or .UDI can be represented in .SCP, but the reverse is not true. The cost is file size (50× larger) and tool support (less universal).

### 1.4 A short history

The SuperCard Pro hardware was launched in 2012 by Jim Drew, originally targeted at the Commodore Amiga preservation community. The .SCP format was standardised by Drew in 2014 (with revisions in subsequent years), and the format specification was published openly to encourage adoption.

By the late 2010s, .SCP had become the dominant interchange format for flux-level floppy-disk imaging, with support from major preservation projects (the Internet Archive's Software Collection, the MAME project, the Amiga Preservation Foundation, the Atari ST preservation project). The Spectrum community adopted .SCP more slowly, since most Spectrum software is on standard TR-DOS disks that .TRD / .SCL can represent perfectly well, but .SCP is now the recommended format for archival imaging of original Spectrum disk media.

### 1.5 Scope

This article covers the byte-level layout of .SCP files. The simpler sector-level formats are covered in [trd_scl_formats.md](trd_scl_formats.md), [dsk_fdi_formats.md](dsk_fdi_formats.md), and [udi_format.md](udi_format.md).


## §2. The .SCP Header and Disk Information Block

### 2.1 Overview

A .SCP file consists of three parts:

1. **A 16-byte file header** containing the magic string, the format version, and the disk's geometry (number of tracks, number of revolutions per track).
2. **A track-offset table** (variable length) containing, for each track, the byte offset in the file where that track's data begins.
3. **The track data blocks** (variable length) containing the raw flux timings for each revolution of each track.

The format is intentionally simple — the header is small, the track-offset table is direct, and the per-track data is self-contained. This makes it possible to read a single track from a .SCP file without parsing the entire file.

### 2.2 The 16-byte file header

| Offset | Length | Field | Notes |
|---|---|---|---|
| 0 | 3 | **Magic** | ASCII: `"SCP"` (`53 43 50`). Identifies the file as .SCP. |
| 3 | 1 | **Version / category** | Bit 7 = disk category (0 = floppy, 1 = hard disk); bits 0–6 = format version (currently 0x00–0x05). |
| 4 | 1 | **Revolutions per track** | The number of flux-capture revolutions stored per track. Values: 0x01 (single revolution), 0x02–0x05 (multi-revolution). 0x00 is reserved. |
| 5 | 1 | **Start track** | The first track in the image (typically 0x00). Non-zero values are used for partial disk images. |
| 6 | 1 | **End track** | The last track in the image (typically 0xA2 = 162 for a 2-sided 80-track disk, since .SCP numbers tracks as `cylinder * 2 + side`). |
| 7 | 1 | **Flags** | Bit 0 = "index mode" (see §3.3); bit 1 = "288 RPM mode" (vs. 300 RPM); bit 2 = "use 25 ns cell width" (vs. the default 40 ns); bit 3 = "flux data is RLE-compressed". |
| 8 | 4 | **Sample rate** (BE, big-endian) | The sampling rate in Hz at which the flux was captured (typically 25,000,000 for SuperCard Pro). Big-endian (unusual; most other fields are LE). |
| 12 | 4 | **Amount of flux data** (BE) | The total size of all track data blocks combined, in bytes. Big-endian. |

After the 16-byte header comes the track-offset table, followed by the track data blocks.

### 2.3 The track-offset table

The track-offset table has one entry per track, from track 0 through track `end_track`. Each entry is a 4-byte little-endian value giving the byte offset in the .SCP file where that track's data begins.

| Offset | Length | Field | Notes |
|---|---|---|---|
| 16 | 4 × (end_track - start_track + 1) | **Track-offset table** | One 4-byte LE offset per track, in order. |

The number of tracks is `end_track - start_track + 1`. For a 2-sided 80-track disk imaged in full, this is `0xA2 - 0x00 + 1 = 163` tracks (80 cylinders × 2 sides + 1 for the entry that marks the end of the data block).

A track offset of `0x00000000` means the track is not present in the image (e.g., a single-sided disk would have all side-1 tracks at offset 0). A reader should handle this case gracefully.

### 2.4 .SCP track numbering

The .SCP format uses **linear track numbering** rather than (cylinder, side) tuples:

```
track = cylinder * 2 + side
```

So for an 80-track 2-sided disk:

- Track 0 = cylinder 0, side 0.
- Track 1 = cylinder 0, side 1.
- Track 2 = cylinder 1, side 0.
- Track 3 = cylinder 1, side 1.
- ...
- Track 159 = cylinder 79, side 1.

This is the same "side-first" ordering used by .TRD (see [trd_scl_formats.md §2.2](trd_scl_formats.md)). The total track count for a standard 2-sided 80-track disk is 160 (tracks 0–159).

### 2.5 Validation

A reader should validate the following:

- The magic string at offset 0 is `"SCP"`.
- The version / category byte at offset 3 indicates a supported version.
- The revolutions-per-track byte at offset 4 is in the range 1–5.
- The start track is ≤ end track.
- Each non-zero entry in the track-offset table points to a valid position within the file (i.e., `offset < file_size`).
- The total flux data size at offset 12 is consistent with the actual file size.

Malformed files should be reported as warnings, since real-world .SCP files in circulation sometimes have minor inconsistencies (especially in the flags byte and the sample rate field).

### 2.6 Example: a standard 80-track 2-sided disk header

For a standard 80-track 2-sided Spectrum disk, imaged at 25 MHz with 5 revolutions per track:

```
00 53 43 50  ; "SCP" magic
03 00        ; category=floppy, version=0
04 05        ; 5 revolutions per track
05 00        ; start track 0
06 A2        ; end track 162 (= 80*2 + 1 extra)
07 00        ; flags: index mode, 40 ns cells, no RLE
08 01 7D 78 40 ; sample rate 25,000,000 Hz (big-endian)
0C 00 00 00 00 ; total flux data size (placeholder; set on write)
```

After this header comes 163 4-byte track-offset entries (= 652 bytes), then the track data.


## §3. The Track Data Block

### 3.1 Per-track header

Each track's data block (located via the track-offset table) begins with a small per-track header, followed by the flux data for each revolution:

| Offset | Length | Field | Notes |
|---|---|---|---|
| 0 | 3 | **Track-header magic** | ASCII: `"TRK"` (`54 52 4B`). Identifies the start of a track's data. |
| 3 | 1 | **Track number** | The .SCP track number (cylinder × 2 + side) for this track. |
| 4 | 12 × N | **Per-revolution descriptors** | N entries (one per revolution), each 12 bytes. See §3.2. |

After the per-revolution descriptors come the actual flux data, one block per revolution, in the same order as the descriptors.

### 3.2 The 12-byte per-revolution descriptor

| Offset | Length | Field | Notes |
|---|---|---|---|
| 0 | 4 | **Index time** (LE) | The time (in nanoseconds, at the sample rate) between the index pulse that started this revolution and the next index pulse. Typically ~20,000,000 ns (20 ms = 50 Hz / 300 RPM). |
| 4 | 4 | **Track data length** (LE) | The size in bytes of this revolution's flux data block. |
| 8 | 4 | **Sample count** (LE) | The number of flux-transition samples in this revolution's data block. |

The per-revolution descriptor tells the reader exactly how much flux data follows, so the reader can quickly skip to the next revolution (or the next track) without parsing the flux data itself.

### 3.3 Flux-transition encoding

Each revolution's flux data block consists of a sequence of **2-byte (16-bit) little-endian values**, each representing the time (in sample clock ticks, not nanoseconds) between consecutive flux transitions. The sample clock is 25 MHz by default, so each tick is 40 ns.

The encoding handles two special cases:

| Value | Meaning |
|---|---|
| `0x0001`–`0xFFFF` (1–65535) | The time between this flux transition and the next one, in sample clock ticks. |
| `0x0000` | **Spacer / overflow**. The previous flux interval is **continued** by adding 65536 to the next interval. This allows intervals longer than 65536 ticks (~2.6 ms) to be encoded, by chaining multiple 0x0000 values together. |

For example, an interval of 80,000 ticks would be encoded as:

```
00 00  ; +65536
80 38  ; 0x3880 = 14,464 ticks (total: 65536 + 14464 = 80,000)
```

This scheme can encode arbitrarily long intervals (at the cost of additional 2-byte spacers), while keeping the common short intervals to a single 2-byte value.

### 3.4 Index mode vs. splice mode

The .SCP header's flags byte has an "index mode" bit that determines how the flux data is delimited:

- **Index mode** (flag set): the flux data starts at one index pulse and ends at the next index pulse. This is the preferred mode for archival work — every revolution is exactly one disk revolution, and the start of the data is well-defined.
- **Splice mode** (flag clear): the flux data may start and end at any point in the revolution. The reader is expected to "splice" the start and end together when reconstructing the track. Splice mode is used by some imaging tools that cannot reliably detect the index pulse.

For archival work, index mode is strongly preferred, since it preserves the exact alignment between flux transitions and the disk's physical index.

### 3.5 Multi-revolution sampling

When the revolutions-per-track byte in the header is greater than 1, each track's data block contains multiple per-revolution descriptors (and corresponding flux data blocks), in order:

1. Revolution 0: 12-byte descriptor + flux data.
2. Revolution 1: 12-byte descriptor + flux data.
3. ... and so on.

A reader can compare the data from multiple revolutions to identify weak-bit regions (where the flux transitions differ between revolutions). For example, if the same physical region on the disk reads as `0xFF` in revolution 0 and `0x00` in revolution 1, that region is a weak bit, and the reader should report it as non-deterministic.

Multi-revolution sampling is the key advantage of .SCP over sector-level formats. The .EDSK and .UDI formats only store a single sample per sector, so they cannot distinguish a stable region from a weak one. The .SCP format, by storing 5 (or however many) full-revolution samples, allows the reader to fully characterise the disk's magnetic behaviour.

### 3.6 RLE compression

The flags byte's bit 3 indicates whether the flux data is **run-length encoded** (RLE). When RLE is enabled, the flux data uses a slightly different encoding that compresses long runs of identical intervals:

- If the high bit of a 2-byte value is set (i.e., the value is in the range `0x8000`–`0xFFFF`), the low 15 bits give a **repeat count**, and the next 2 bytes give the flux interval to repeat that many times.
- If the high bit is clear, the value is a normal flux interval (1–32767 ticks).

RLE typically compresses flux data by 30–60%, since floppy disks have many long runs of identical-length flux intervals (especially in the gap regions between sectors).

A reader should check the RLE flag in the header and decode the flux data accordingly. Most modern tools (HxC, GreaseWeazle, MAME's floptool) support both modes.

### 3.7 Worked example: a single revolution

Consider a single-revolution image of a track with 100,000 flux transitions, each averaging 250 ticks (10 µs) apart:

- Header (16 bytes): `"SCP"`, version=0, revolutions=1, start=0, end=0xA2, flags=0x01 (index mode), sample_rate=25 MHz, total_data_size=200,412 (12-byte descriptor + 200,000 bytes flux data, plus the 4-byte "TRK" header).
- Track-offset table (4 bytes): offset 20 (= start of track 0's data).
- Track data block:
  - Track header: `"TRK"` + track_number 0 + 12-byte per-revolution descriptor:
    - Index time: 20,000,000 ns (= 50 Hz / 300 RPM).
    - Track data length: 200,000 bytes.
    - Sample count: 100,000.
  - Flux data: 100,000 × 2-byte values, each in the range 1–32767, representing the time (in 40-ns ticks) between consecutive flux transitions.

The reader parses the per-revolution descriptor, allocates a buffer of `sample_count` 16-bit values, and reads the flux data. It can then decode the flux into MFM / FM bits using a virtual PLL (see [mfm_encoding.md](mfm_encoding.md) for the decoding details).

### 3.8 Total file size

For a standard 80-track 2-sided Spectrum disk, imaged at 25 MHz with 5 revolutions per track, the typical file size is:

- Each revolution: ~200,000 bytes of flux data + 12-byte descriptor.
- Each track: ~1,000,000 bytes (5 revolutions × 200,000 bytes) + 4-byte "TRK" header + 12-byte descriptor × 5.
- Total: 160 tracks × ~1,000,000 bytes = ~160 MB uncompressed, ~80 MB RLE-compressed.

In practice, Spectrum disks (which have simpler flux patterns than, say, Amiga disks) compress to about 5–15 MB per disk image with RLE.


## §4. Tools and Converters

### 4.1 Hardware

The .SCP format is **produced** by the following hardware devices:

| Device | Manufacturer | Status | Notes |
|---|---|---|---|
| **SuperCard Pro** | CBM Electronics (Jim Drew) | In production (2012–) | The reference hardware. USB-connected, supports 3.5", 5.25", and 8" drives. |
| **GreaseWeazle** | Keir Fraser (open source) | In production (2018–) | Open-source hardware, originally based on STM32. Reads and writes .SCP natively. Cost-effective (~$30). |
| **KryoFlux** | KryoFlux Team | In production (~2010–) | Supports .SCP via third-party conversion tools (the native format is a raw stream, not .SCP). |
| **DiskFerret / DiskFerret Jr.** | David Kuder | Limited production | An earlier flux-level reader; supports .SCP via its own tooling. |

For Spectrum disk imaging, the **GreaseWeazle** is the most cost-effective option (~$30 vs. ~$200 for SuperCard Pro). It connects to any standard PC floppy drive and to a USB port on a modern PC.

### 4.2 Software

The following software tools can read, write, or convert .SCP files:

- **SuperCard Pro software** (Windows) — the official software for the SuperCard Pro hardware. Reads, writes, and analyses .SCP files.
- **HxCFloppyEmulatorTool** (Windows / Linux, by Jean-François DEL NERO) — a multi-format disk-image tool that can convert .SCP to / from .EDSK, .HFE, .IMG, and many other formats. The de facto standard for cross-format conversion.
- **GreaseWeazle tools** (Python, by Keir Fraser) — the official GreaseWeazle software. Reads, writes, and analyses .SCP files.
- **MAME's floptool** — part of the MAME project; can convert .SCP to / from many other formats, and can analyse flux data for sector extraction.
- **cwtool** — a Unix raw flux tool that can produce .SCP files (and other formats) from raw flux captures.
- **a2flux** (Apple II-focused) — converts .SCP to / from the Apple II's WOZ format.

### 4.3 Emulators that read .SCP

Emulator support for .SCP is more limited than for sector-level formats, because emulating a virtual FDC that reads raw flux is much more work than emulating one that reads sector data. The major emulators that support .SCP:

- **HxC firmware for Gotek** — runs .SCP files directly on a Gotek USB-floppy emulator installed in a real Spectrum (or other retro computer). The Gotek synthesises the flux transitions in real time and feeds them to the Spectrum's onboard FDC.
- **MAME** — the multi-system emulator supports .SCP for several floppy-based systems (including the Amiga, Atari ST, and IBM PC). Spectrum support is via the MAME Spectrum driver, which can read .SCP but is slower than reading sector-level formats.
- **WinUAE** (Amiga) — reads .SCP natively; the Amiga community is the primary user of .SCP in emulation.
- **Hatari** (Atari ST) — reads .SCP via a virtual FDC.

The Spectrum emulators FUSE, ZEsarUX, and UnrealSpeccy do **not** currently read .SCP directly — they require conversion to .EDSK or .TRD first. This is changing as flux-level emulation becomes more common.

### 4.4 .SCP → sector-level conversion

The most common use of .SCP files in the Spectrum community is **conversion to a sector-level format** for use in emulators:

- **.SCP → .EDSK**: the .SCP flux data is decoded using a virtual PLL, the MFM (or FM) bits are extracted, the sector IDs and sector data are parsed, and the result is written to .EDSK. This is lossy (the multi-revolution flux data is discarded; only the first revolution is used to extract sectors), but the resulting .EDSK is suitable for emulator use.
- **.SCP → .TRD**: same as above, but the result is written to a .TRD file. Only works for standard TR-DOS disks (80-track, 2-sided, 10 sectors of 512 bytes).
- **.SCP → .SCL**: extract the directory and files from the .SCP flux data, write to .SCL. Same limitations as .TRD.

HxCFloppyEmulatorTool and MAME's floptool can perform all of these conversions. The conversion is usually automatic (the tool detects the disk's format from the flux data), but in some cases manual configuration is needed.

### 4.5 .EDSK / .TRD → .SCP

Converting **from** a sector-level format **to** .SCP is not generally possible, because the sector-level format does not contain enough information to reconstruct the flux transitions. There are tools that **synthesise** a plausible flux pattern from a .EDSK or .TRD file (e.g., for use on a Gotek that has no .SCP support), but the result is not a faithful preservation of any real disk — it is a freshly-generated flux pattern that, when read by an FDC, produces the sectors of the original disk.

### 4.6 When to use .SCP

Use .SCP when:

- You are **archiving original Spectrum disk media** for long-term preservation. The .SCP format captures every magnetic transition on the disk surface, including weak-bit patterns, spurious transitions, and copy-protection tricks. This is the gold standard for preservation.
- You need to **image a copy-protected disk** that no sector-level format can represent. The .SCP format can preserve any flux pattern, regardless of how it would be interpreted by an FDC.
- You need to **reconstruct a disk** on real hardware (via a Gotek with HxC firmware) with byte-level accuracy.

For day-to-day use (running software, distributing disk images, sharing demoscene releases), .TRD / .SCL (for TR-DOS disks) or .EDSK (for +3DOS / CP/M disks) are preferred due to their smaller size and wider tool support.

---

## §5. Cross-references and License

### 5.1 Within the storage section

- [mfm_encoding.md](mfm_encoding.md) — the MFM signal layer that is reconstructed from the .SCP flux data.
- [fdc_vg93.md](fdc_vg93.md) — the WD1793 / KR1818VG93 floppy controller chip that the .SCP format bypasses by operating at the flux level.
- [beta_disk_interface.md](beta_disk_interface.md), [plus3_floppy.md](plus3_floppy.md) — the host-side hardware.
- [trd_disk_format.md](trd_disk_format.md), [trd_scl_formats.md](trd_scl_formats.md) — the simpler formats used for TR-DOS disks.
- [dsk_fdi_formats.md](dsk_fdi_formats.md), [udi_format.md](udi_format.md) — the other sector-level formats that .SCP supersedes in expressive power.

### 5.2 Adjacent format articles

- [plus3_dos_format.md](plus3_dos_format.md), [cpm_disk_format.md](cpm_disk_format.md), [opus_discovery_format.md](opus_discovery_format.md) — the on-disk logical formats that can be extracted from .SCP files.
- [disk_format_overview.md](disk_format_overview.md) — a comparative overview of all Spectrum floppy image formats.

### 5.3 Reverse engineering and demoscene

- (Reverse engineering / preservation) The .SCP format is the gold standard for floppy-disk preservation. See the 05_reversing section for the techniques used to bypass copy protection once the disk has been imaged.
- (Demoscene) Demoscene releases are typically distributed as .TRD / .SCL files (smaller, more compatible), but archival imaging of original demoscene disk media (where available) is done with .SCP.

### 5.4 External references

- **The official SuperCard Pro website** (store.cbm8bit.com) — the canonical reference for the .SCP format and the SuperCard Pro hardware.
- **GreaseWeazle GitHub** (github.com/keirf/Greaseweazle) — the open-source GreaseWeazle firmware and tools.
- **HxCFloppyEmulatorTool** (hxc2001.com) — the de facto cross-format disk-image conversion tool.
- **MAME floptool documentation** — the MAME project's flux-analysis tools and format converters.
- **"Disc Preservation"** (various archival projects) — the Internet Archive, the Software Preservation Society, and the Amiga Preservation Foundation all use .SCP as their primary imaging format.

### 5.5 License

This article is licensed under the **Creative Commons Attribution-ShareAlike 4.0 International License (CC BY-SA 4.0)**. You are free to share and adapt the material, provided you give appropriate credit and distribute derivative works under the same license.

"Spectrum", "ZX Spectrum", "+3", "SuperCard Pro", "GreaseWeazle", "KryoFlux", "Gotek", "HxC", "MAME", and other trademarks are the property of their respective owners and are used here for identification and educational purposes only.
