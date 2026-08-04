[← Home](../../README.md) · [I/O](../) · [Storage](README.md)

# MFM Encoding: How Bits Are Recorded on Floppy Disk

When you write a byte to a floppy disk, the floppy controller does not write eight bits to the medium. It writes a **modulated signal**: a stream of magnetic transitions whose positions in time encode both the data bits *and* a clock signal that lets the controller recover the bit boundaries on readback. The scheme used for virtually all ZX Spectrum floppy formats (TR-DOS, +3 DOS, CP/M, DivIDE) is **Modified Frequency Modulation (MFM)**.

MFM encoding sits at the very bottom of the floppy stack — below the [TR-DOS logical format](trd_disk_format.md), below the [floppy controller chip](fdc_vg93.md), and below the [disk image file formats](trd_scl_formats.md). Understanding MFM is essential for emulator authors (who must reproduce the FDC's bit-level behavior), for preservationists (who need to know why flux-level formats like [.SCP](scp_format.md) exist), and for anyone reverse engineering non-standard or copy-protected disk formats.

This article covers MFM from the ground up: the bit cell model, the encoding rules, sync marks and address marks, the phase-locked loop (PLL) data separator, write precompensation, and how MFM compares to its predecessors (FM) and successors (RLL, GCR). After reading this, the rest of the floppy stack — FDC registers, sector layouts, image formats — will fall into place.

---

## §1. What MFM Encoding Is

### 1.1 The fundamental problem

A floppy disk stores information as a sequence of **magnetic domains**: tiny regions of the magnetic coating on the disk surface, each magnetised in one of two directions (call them "north-up" and "north-down"). As the disk rotates under the read/write head, the head detects **transitions**: places where consecutive domains have opposite magnetisation. A region of constant magnetisation produces no signal; only the transitions are visible to the head.

So the floppy medium is fundamentally a **transition-based channel**. The writer controls *when* transitions occur (by reversing the write current at chosen times); the reader observes *when* transitions occur (by detecting the voltage pulses from the head). Information must be encoded in the *timing* of transitions, not in the *level* of the signal.

This immediately raises a question: how does the reader know the bit rate? If the writer puts one transition every microsecond, the reader must sample the signal at one-microsecond intervals to decode it. But the disk is spinning at a nominally fixed angular velocity (300 RPM = 5 Hz = 200 ms per revolution for a standard 3.5" drive), and the actual velocity varies by ±2% or so due to motor tolerances. If the reader samples at a fixed rate, it will drift in and out of sync with the writer within a few hundred bits.

The solution is to embed **clock information** in the data stream itself. The reader uses a **phase-locked loop (PLL)** to lock onto the embedded clock and recover the writer's timing. Once locked, the reader can sample at the correct times to extract the data bits.

### 1.2 The history of floppy encoding

Three main encoding schemes have been used for floppy disks:

- **Frequency Modulation (FM)**, also called "single density". Used by the earliest 8" floppies (IBM 23FD, 1970) and by the Sinclair Microdrive (in a modified form). Every **bit cell** contains both a clock transition and a data transition. Simple, but wasteful: half the bandwidth is consumed by clock bits.

- **Modified Frequency Modulation (MFM)**, also called "double density". Introduced by IBM in 1972 for the 8" floppy used in the IBM 3740 system. MFM drops most of the clock transitions — only the *necessary* ones are kept, for clock recovery when the data has long runs of zeros. MFM roughly **doubles** the storage capacity of FM at the same physical density, hence "double density". This is what the ZX Spectrum's floppy systems (Beta Disk Interface, +3, DivIDE, etc.) all use.

- **Run-Length Limited (RLL)** schemes (such as 2,7 RLL used in early hard disks, and the "vertical recording" schemes of modern drives). These achieve higher density than MFM by allowing longer runs of zeros (fewer transitions) while still guaranteeing clock recovery. RLL is rarely used on floppy disk because MFM is already adequate for the relatively low densities of floppy media.

There are also a few niche schemes:

- **Modified MFM (M²FM or MMFM)**: a variant of MFM with slightly fewer clock transitions. Used in some early IBM products but never popular for floppies.
- **Group Coded Recording (GCR)**: maps groups of data bits to longer codewords chosen to avoid long runs of zeros. Used by Apple II, Commodore 1541, and Macintosh 400K/800K floppies. Not used on the ZX Spectrum.

For the ZX Spectrum ecosystem, **MFM is universal**. All standard floppy formats (TR-DOS, +3 DOS, CP/M, Opus Discovery, Kendon, Rotronics Wafadrive) use MFM at 250 kbit/s (double density, 300 RPM).

### 1.3 What MFM is *not*

MFM is **not** a file format. It is a **physical-layer encoding** that sits below the FDC's notion of sectors and tracks. A .TRD or .DSK file contains the logical contents of a disk (sectors in their linear order); converting that to flux transitions on a real disk requires applying MFM encoding, adding sync marks, address marks, CRCs, and inter-sector gaps. An emulator that loads .TRD files does not need to know about MFM at all — it just reads the sectors directly.

MFM is also **not** specific to floppy disk. It was used on early hard disks (ST-506 interface), on some tape drives, and even on the magnetised stripe on the back of a credit card (which uses an FM-like encoding at a much lower bit rate). But for our purposes, MFM is "the encoding used on Spectrum floppies".

### 1.4 Why MFM matters for Spectrum developers

MFM matters because:

- **It is what the FDC chip does**. The [WD1793 / KR1818VG93](fdc_vg93.md) takes a byte from the data bus and serialises it into an MFM bit stream on the write-data pin. Reading is the reverse: the raw read-data pin carries an MFM bit stream that the FDC's internal data separator decodes back into bytes. Understanding MFM is essential for understanding the FDC's behavior.

- **It explains the format parameters**. Why does a standard TR-DOS disk have 10 sectors of 512 bytes per track? Because at 250 kbit/s MFM with the standard sector overhead (sync marks, ID field, data field, gaps), a track holds exactly 10 sectors of 512 bytes in 6250 bytes of raw MFM data. Change the encoding (e.g., to RLL) and you would get more sectors per track.

- **It is the basis of copy protection**. Non-standard protection schemes (such as speeding up the disk slightly to fit an extra sector, or using deliberately malformed MFM that the FDC's PLL locks to in unusual ways) all work by manipulating the MFM layer. To understand Spectrum disk copy protection, you must understand MFM.

- **It is essential for preservation**. The [SuperCard Pro](scp_format.md) format stores the raw flux transitions (the MFM signal itself), allowing perfect preservation of any disk — including non-standard ones. To interpret a .SCP file, you must decode the MFM signal, which requires understanding the encoding.

---

## §2. The Bit Cell and the Window

MFM (and FM) divides time on the track into equal-length **bit cells**. Each cell carries exactly one data bit. The bit rate is determined by the disk's rotational speed and the encoding's clock frequency.

### 2.1 The bit cell on a standard Spectrum floppy

For a standard 3.5" double-density floppy (the format used by virtually all Spectrum floppy systems):

- Rotational speed: 300 RPM (5 revolutions per second, 200 ms per revolution).
- Data rate: **250 kbit/s** (250 000 bits per second).
- Bit cell width: 1 / 250000 = **4 µs**.

So each bit cell is 4 µs wide, and a full revolution (200 ms) contains 200000 / 4 = **50000 bit cells**. That's 50000 bits per track, or 6250 bytes (raw MFM bytes, before accounting for sector overhead).

For a 5.25" disk at 300 RPM (the Beta Disk Interface's original format), the parameters are identical.

### 2.2 The two halves of the cell

Each 4 µs bit cell is divided into two equal **windows**:

- The **clock window** (first 2 µs): where clock transitions can appear.
- The **data window** (second 2 µs): where data transitions can appear.

The two windows are visually:

```
|<------- 4 µs bit cell ------>|
|<-- 2 µs clock -->|<-- 2 µs data -->|
|                  |                  |
```

Each window is, in turn, divided into a narrower "valid transition" zone and two "invalid" guard zones at the edges. The PLL tries to keep its sampling clock aligned with the center of each window, so that transitions in the middle of the window are reliably detected and transitions at the edges (which would indicate drift) are rejected.

### 2.3 FM: clock and data bits in every cell

In **Frequency Modulation (FM)**, every cell has both a clock bit and a data bit:

| Data bit | Clock transition? | Data transition? |
|----------|-------------------|------------------|
| 0        | Yes (always)      | No               |
| 1        | Yes (always)      | Yes              |

So the FM encoding of a byte `0xB5` (10110101) is:

```
Data bits:        1   0   1   1   0   1   0   1
Clock transitions: v   v   v   v   v   v   v   v   <- always
Data transitions:  v   .   v   v   .   v   .   v   <- only for 1 bits

Combined signal:   vv  v.  vv  vv  v.  vv  v.  vv
```

(where `v` = transition, `.` = no transition).

Notice that every cell has at least one transition (the clock bit). This means the PLL sees a steady stream of clock transitions and can lock to them easily. The cost is bandwidth: half of every cell is dedicated to clock bits, leaving only half for data. FM at 250 kbit/s of *transitions* delivers only 125 kbit/s of *data*.

### 2.4 MFM: only the necessary clock transitions

**Modified Frequency Modulation (MFM)** drops most of the clock transitions. The rule is: a clock transition is added **only when both the current data bit and the previous data bit are zero**. (If either is a one, there's already a data transition nearby that the PLL can use for clock recovery.)

| Current data bit | Previous data bit | Clock transition? | Data transition? |
|------------------|-------------------|-------------------|------------------|
| 1                | (any)             | No                | Yes              |
| 0                | 1                 | No                | No               |
| 0                | 0                 | **Yes**           | No               |

So the MFM encoding of `0xB5` (10110101), starting from an assumed previous bit of 0:

```
Prev data:      0
Data bits:      1   0   1   1   0   1   0   1
Clock transitions: .   .   .   .   v   .   .   .   <- only between two 0s
Data transitions:  v   .   v   v   .   v   .   v   <- for 1 bits

Combined signal:   .v  v.  .v  .v  v.  .v  v.  .v
```

Notice how much sparser the MFM signal is. Each cell has at most one transition, and many cells have none. The minimum time between transitions is 2 µs (one window); the maximum is 8 µs (two consecutive all-zero cells, which would be `0v. .v.` and is the case the clock-transition rule was designed to break up).

### 2.5 Density comparison

By dropping unnecessary clock transitions, MFM roughly doubles the data density at the same physical transition rate:

- **FM at 250 kbit/s transitions**: 125 kbit/s data (1 bit per 2 transitions).
- **MFM at 250 kbit/s transitions**: 250 kbit/s data (1 bit per 1 transition, on average).

This is why MFM is called "double density" — at the same physical recording density (transitions per inch of track), MFM stores twice as much data as FM.

In practice, MFM achieves slightly less than 2× density because of the **worst-case run-length constraint**: MFM guarantees that transitions are at most 8 µs (4 cells) apart, so the PLL has a maximum gap to bridge. This is enforced by the clock-transition rule.

---
## §3. The Encoding Rules

The MFM encoding rules can be stated precisely as a small state machine. This section gives the formal rule, then works through several examples by hand.

### 3.1 The MFM rule (formal)

For each data bit `d[i]` in the stream, the writer produces a clock bit `c[i]` and a data bit `data[i]` according to:

```
data[i]  = d[i]                                   (data transition iff data bit is 1)
clock[i] = (NOT d[i]) AND (NOT d[i-1])            (clock transition iff both bits are 0)
```

where `d[i-1]` is the previous data bit (with `d[-1]` taken to be 0 at the start of a byte, or as carried over from the previous byte during continuous streaming).

Each clock and data bit is then mapped to a transition or no-transition:

```
clock window of cell i:   transition iff clock[i] == 1
data  window of cell i:   transition iff data[i]  == 1
```

The combined transition stream is what gets written to the disk.

### 3.2 Worked example: encoding `0x00`

Encoding a single `0x00` byte, assuming previous data bit was `1` (a common case after sync marks):

```
Prev:   ... 1
Data:   0   0   0   0   0   0   0   0
Clock:  .   v   v   v   v   v   v   v   .   <- clock bit is 1 for cells 1..6 (both prev and current are 0)
                                            <- cell 0: prev=1, so no clock
                                            <- cell 7: prev=0, current=0, clock=1
                                            <- next byte's cell 0: prev=0 (this byte's last), so depends on next data
Data:   .   .   .   .   .   .   .   .

Combined: .  v.  v.  v.  v.  v.  v.  v.
```

The minimum spacing between transitions is 2 µs (the gap between clock and data windows within a cell, when only the clock transitions).

### 3.3 Worked example: encoding `0xFF`

Encoding `0xFF` (all ones):

```
Prev:   ... 0
Data:   1   1   1   1   1   1   1   1
Clock:  .   .   .   .   .   .   .   .   <- never any clock (current data bit is always 1)
Data:   v   v   v   v   v   v   v   v

Combined: .v  .v  .v  .v  .v  .v  .v  .v
```

The minimum spacing is again 2 µs (the gap between data windows of adjacent cells, since no cell has a clock transition).

### 3.4 The maximum run-length

The longest run of cells without a transition occurs when the data has a pattern like `1 0 0 0`: the first cell has a data transition (because the bit is 1), the next cell has no transition (bit is 0, previous bit was 1 so no clock), the next cell has a clock transition (bit is 0, previous bit was 0). This produces a gap of **6 µs** between the data transition in cell 0 and the clock transition in cell 2.

The maximum legal gap in MFM is **8 µs**, which arises in a slightly different pattern: where a data transition in cell N is followed by an empty cell N+1 (where prev was 1, current is 0), then cell N+2 has its clock at the *end* (because prev was 0). This is a subtle case and varies by source, but the practical bound is:

> **In MFM, transitions are spaced 2 µs, 4 µs, 6 µs, or 8 µs apart — never less, never more.**

The PLL uses these four valid spacings to discriminate real transitions from noise.

### 3.5 Encoding C code

A simple MFM encoder in C, taking a byte stream and producing a transition bit stream:

```c
// Encode 'data_byte' as MFM, given the previous data bit.
// Returns 16 bits (8 clock + 8 data, interleaved) representing the transitions.
// 'prev_bit' is updated to the last bit of this byte.

uint16_t mfm_encode_byte(uint8_t data_byte, int *prev_bit) {
    uint16_t transitions = 0;
    int prev = *prev_bit;

    for (int i = 7; i >= 0; i--) {
        int data_bit = (data_byte >> i) & 1;
        int clock_bit = (!data_bit) && (!prev);

        // Clock window transition
        transitions = (transitions << 1) | clock_bit;
        // Data window transition
        transitions = (transitions << 1) | data_bit;

        prev = data_bit;
    }

    *prev_bit = prev;
    return transitions;
}
```

The decoder is essentially the reverse, but with a PLL to recover the bit clock first (see §6).

---

## §4. Sync Marks

The MFM encoding scheme described so far has a fundamental problem: **byte synchronisation**. The PLL recovers the bit clock, so the FDC knows where each *bit cell* is. But it doesn't know where each *byte* starts. If it samples the bit stream and reads `10110101`, is that the first byte of a sector header, the middle of a data field, or some random bytes in a gap? The FDC has no way to tell.

The solution is the **sync mark**: a deliberately malformed bit pattern that the FDC can recognize unambiguously, even mid-stream. Once the FDC sees a sync mark, it knows that the *next* byte boundary is the start of a meaningful field.

### 4.1 The missing-clock-bit trick

A sync mark works by violating MFM's encoding rules. Recall that in MFM, the spacing between transitions is 2 µs, 4 µs, 6 µs, or 8 µs — those are the only valid intervals. If the writer deliberately omits a transition that the rules require, the resulting signal has an "impossible" spacing that the FDC can recognize.

The most common sync mark is the **`A1` with missing clock**. The byte `0xA1` (10100001) encodes normally as a specific pattern of clock and data transitions. The sync-mark version of `A1` omits the **clock bit between cell 4 and cell 5** (the one that the MFM rule would insert because cells 4 and 5 are both zero). The resulting transition stream has a **gap longer than 8 µs** — a "hole" that violates MFM's run-length rule. The FDC's data separator detects this hole and recognizes the sync.

### 4.2 The `A1` sync byte

The standard MFM `A1` sync mark is the byte `0xA1` encoded with a missing clock transition. To mark a sync, the disk format writes **three consecutive `A1` sync bytes**, each with the missing-clock-bit violation. Three in a row gives very high confidence that the pattern is a real sync (not a random bit error) and lets the FDC's PLL lock to the byte boundary.

```
Sync sequence: A1* A1* A1* <next byte>
                ^   ^   ^
                |   |   |
                each A1 is the special "missing clock" version
```

After the three sync `A1`s, the FDC is byte-synchronized and can read the next byte as the start of a field (typically an address mark — see §5).

### 4.3 The `C2` sync byte

A second sync pattern, used less commonly, is the **`C2` with missing clock**. This is the byte `0xC2` (11000010) with a specific clock bit dropped. It is used for some niche purposes (such as hard-sectored disk formats or non-standard protection schemes) but is not part of the standard Spectrum floppy formats.

The standard Spectrum floppy formats use only the `A1` sync.

### 4.4 How the FDC uses sync marks

When the FDC is searching for a sector (on a `READ SECTOR` command), it does the following:

1. **Wait for a sync mark.** The FDC's data separator watches the raw read signal for the `A1*` pattern. Until it sees three in a row, it just consumes bits without producing bytes.

2. **Read the next byte as the address mark.** After the sync, the next byte identifies what kind of field follows (header or data — see §5).

3. **Read the rest of the field.** The FDC reads the specified number of bytes (the ID field or data field length), checking the CRC at the end.

4. **If this is the sector we wanted, return it; otherwise, go back to step 1.**

This process continues until either the requested sector is found or the index hole is seen again (indicating a full revolution without finding the sector).

### 4.5 The format gap

Between sectors, the writer fills the track with **gap bytes**: typically `0x4E` (a "neutral" pattern that the FDC's PLL can lock to). These gap bytes serve several purposes:

- They give the FDC time to finish processing the previous sector before the next sync mark arrives.
- They absorb timing variations between the writing drive (which wrote the disk) and the reading drive (which may spin slightly faster or slower).
- They give the writer a "blank" region where it can rewrite a sector without affecting the previous or next sector.

The gap structure is discussed further in §5.6.

---
## §5. Address Marks

The sync marks of §4 establish byte synchronisation. The next thing the FDC needs is **field identification**: knowing whether the bytes following a sync are a sector header, a sector data payload, or something else. This is the role of the **address mark** — a single byte, written immediately after a sync, that identifies the field type.

### 5.1 The four standard address marks

The standard MFM floppy format defines four address marks:

| Mark | Name | Byte value | Purpose |
|------|------|------------|---------|
| **IAM** | Index Address Mark | `0xFC` | Marks the start of the track (written once per revolution, right after the index hole) |
| **IDAM** | ID Address Mark | `0xFE` | Marks the start of a sector header (the ID field) |
| **DAM** | Data Address Mark | `0xFB` | Marks the start of a normal data field |
| **DDAM** | Deleted Data Address Mark | `0xF8` | Marks the start of a *deleted* data field (a sector that has been logically marked as deleted by the OS) |

Each address mark is preceded by three `A1` sync bytes (with missing clock bits). The address mark itself is encoded normally (no missing clock).

### 5.2 The full track layout

A standard MFM track is laid out as follows:

```
[Index hole]
|<--- GAP1 (post-index gap, ~80 bytes of 0x4E) --->|
| IAM sync: 12 bytes of 0x00, then 3 × A1*, then 0xFC |
|<--- GAP2 (post-IAM gap, ~50 bytes of 0x4E) --->|
|
|  +--------- Sector 1 ---------+
|  | ID sync: 12 bytes of 0x00, 3 × A1*, 0xFE |
|  | ID field: track, side, sector, size (4 bytes) |
|  | ID CRC: 2 bytes |
|  |<--- GAP3a (post-ID gap, ~22 bytes of 0x4E) --->|
|  | Data sync: 12 bytes of 0x00, 3 × A1*, 0xFB |
|  | Data field: 512 bytes (or 128, 256, 1024) |
|  | Data CRC: 2 bytes |
|  |<--- GAP3b (post-data gap, ~80 bytes of 0x4E) --->|
|  +------------------------------+
|
|  +--------- Sector 2 ---------+
|  | ... (same layout as Sector 1) |
|  +------------------------------+
|
|  ... (Sectors 3 through N) ...
|
|<--- GAP4 (pre-index gap, fills the rest of the track with 0x4E) --->|
[Next index hole]
```

The exact gap lengths depend on the format. For the standard TR-DOS format (80 tracks × 2 sides × 10 sectors × 512 bytes), the gaps are tuned so that all 10 sectors fit exactly within one revolution.

### 5.3 The ID field

The ID field (sector header) is a 4-byte field that identifies the sector:

| Offset | Size | Field | Notes |
|--------|------|-------|-------|
| 0 | 1 | Track (cylinder) number | 0-based; 0–79 for an 80-track disk |
| 1 | 1 | Side (head) number | 0 or 1 for a double-sided disk |
| 2 | 1 | Sector number | 1-based on TR-DOS disks (sectors 1–10), 0-based on many PC formats |
| 3 | 1 | Sector size code | Encoded as `2^(N+7)` bytes: 0=128, 1=256, 2=512, 3=1024 |

The ID field is followed by a 2-byte **CRC-16** (CCITT polynomial `0x1021`) covering the address mark and the ID field.

The FDC uses the ID field to identify the sector. When you issue a `READ SECTOR` command with a target track/side/sector, the FDC scans the track reading ID fields until it finds the matching one, then reads the following data field.

### 5.4 The data field

The data field contains the sector's payload:

| Component | Size | Notes |
|-----------|------|-------|
| Address mark | 1 byte | `0xFB` (DAM) for normal data, `0xF8` (DDAM) for deleted data |
| Data | `2^(N+7)` bytes | 512 bytes for the standard TR-DOS sector size |
| CRC | 2 bytes | CRC-16 covering the address mark + data |

The FDC verifies the CRC and reports an error if it doesn't match. The data is then delivered to the host computer byte by byte through the FDC's data register.

### 5.5 The deleted-data mark (DDAM)

The `0xF8` deleted-data address mark is a leftover from early IBM mainframe conventions. On the Spectrum, it's used by some operating systems (notably +3 DOS and CP/M) to mark sectors that have been "logically deleted" — the data is still on the disk, but the OS considers it free. The FDC's `READ DELETED SECTOR` command distinguishes between DAM and DDAM sectors.

TR-DOS does not use DDAM. All TR-DOS sectors use DAM.

### 5.6 The gap structure

The various gaps (GAP1, GAP2, GAP3, GAP4) serve mechanical purposes:

- **GAP1** (post-index gap): gives the FDC time to settle after the index pulse before the first sector.
- **GAP2** (post-IAM gap): gives the FDC time to process the IAM before the first IDAM.
- **GAP3a** (post-ID gap): gives the FDC time to process the ID field before the data field arrives. This is critical — without GAP3a, the FDC would have to decide "is this the sector we want?" and start reading the data field with zero latency, which is impossible.
- **GAP3b** (post-data gap): gives the FDC time to process the data field before the next IDAM.
- **GAP4** (pre-index gap): absorbs timing variations. If the writing drive spun slightly slower than 300 RPM, GAP4 will be slightly shorter than nominal. If the reading drive spins slightly faster, GAP4 will be even shorter — but as long as it doesn't disappear entirely, the format still works.

The gap lengths are specified by the format. The FDC uses the GAP length registers (in the [WD1793](fdc_vg93.md)) to know how much gap to expect when writing a sector.

### 5.7 Why the IAM exists

The IAM (Index Address Mark) exists for one reason: to give the FDC a reference point at the start of the track. Without an IAM, the FDC would have to rely on the physical index hole pulse to know where the track starts — but the physical index hole and the logical start of the formatted data are not always perfectly aligned (the drive motor has jitter). The IAM provides a logical "start of track" marker that is independent of the physical index hole.

Some formats (notably non-standard protection schemes) omit the IAM entirely, which can confuse standard FDCs.

---

## §6. Reading MFM

Reading MFM is a two-stage process: first the **PLL** recovers the bit clock from the raw read signal, then the **data separator** extracts bytes from the bit stream and looks for sync marks. This section covers both stages.

### 6.1 The phase-locked loop (PLL)

The PLL is an analog circuit (in older FDCs) or a digital algorithm (in modern implementations and emulators) that recovers the writer's bit clock from the read signal. Its job is to align the FDC's internal sample clock with the centers of the data and clock windows, so that transitions are sampled at the optimal time.

The PLL operates as follows:

1. **Phase detector**: compares the timing of incoming transitions to the FDC's internal sample clock. If a transition arrives before the sample clock fires, the PLL's phase is too slow; if after, too fast.

2. **Loop filter**: averages the phase detector's output over time, smoothing out noise and jitter. The filter's time constant is chosen to balance responsiveness (how fast the PLL locks) against stability (how much it wobbles when locked).

3. **Voltage-controlled oscillator (VCO)**: generates the sample clock at a frequency controlled by the loop filter. The VCO runs at 500 kHz (twice the 250 kHz data rate), producing one clock pulse per window (clock or data).

When locked, the PLL's sample clock is aligned with the centers of the data and clock windows, and the data separator can reliably distinguish "transition in this window" from "no transition in this window".

### 6.2 The digital PLL (for emulators)

For emulator authors, the PLL must be implemented in software. The standard approach is the **digital PLL with a step-adjustment**:

```c
typedef struct {
    int counter;      // Counts down from PERIOD to 0
    int adjustment;   // Current phase adjustment
    int period;       // Nominal counter period (e.g., 16 for 2 µs at 8 MHz sampling)
} PllState;

#define PERIOD 16     // 2 µs at 8 MHz sample rate
#define MIN_PERIOD 12 // 1.5 µs
#define MAX_PERIOD 20 // 2.5 µs

// Called on every flux transition. 'delta' is the time since the last transition.
void pll_on_transition(PllState *pll, int delta) {
    // Where in the current period did the transition fall?
    int center = pll->period / 2;
    int error = (pll->counter + delta / 2) - center;  // Phase error

    // Apply correction (with low-pass filter)
    pll->adjustment = (pll->adjustment * 7 + error) / 8;

    // Adjust the period
    pll->period = PERIOD + pll->adjustment;
    if (pll->period < MIN_PERIOD) pll->period = MIN_PERIOD;
    if (pll->period > MAX_PERIOD) pll->period = MAX_PERIOD;

    pll->counter = 0;  // Reset for next window
}

// Called on every sample tick. Returns 1 if this tick is a window boundary.
int pll_tick(PllState *pll) {
    pll->counter++;
    if (pll->counter >= pll->period) {
        pll->counter = 0;
        return 1;  // Window boundary
    }
    return 0;
}
```

This is a simplified version. Real PLLs have additional logic for distinguishing clock windows from data windows, handling missing transitions, and detecting sync marks.

### 6.3 The data separator

Once the PLL produces a window-aligned sample clock, the **data separator** watches the transitions in each window:

- **Clock window transition?** → this is a clock bit (used to keep the PLL locked, but not delivered to the host).
- **Data window transition?** → this is a data bit (1 if a transition, 0 if no transition).

The data separator accumulates 8 data bits into a byte and passes the byte to the FDC's internal logic. It also watches for the `A1` sync pattern (with the missing clock bit) to establish byte synchronisation.

### 6.4 Window discrimination

A key function of the data separator is **window discrimination**: deciding whether a transition falls in the clock window or the data window. This is straightforward when the PLL is perfectly locked, but tricky when the signal has noise or the PLL has drift.

The standard approach is to use **dead zones** at the window boundaries. Transitions in the center 50% of a window are definitely in that window; transitions in the outer 25% are uncertain and may be rejected as noise. This gives the data separator some immunity to PLL drift and signal noise.

### 6.5 The raw read signal

In a real floppy drive, the read head produces an analog signal: a series of voltage pulses, one per flux transition. The drive's analog electronics condition this signal:

1. **Amplification**: the head signal is very weak (microvolts) and must be amplified.
2. **Filtering**: a band-pass filter removes noise outside the expected frequency range (125 kHz to 500 kHz for MFM at 250 kbit/s).
3. **Differentiation**: the filtered signal is differentiated to produce zero-crossings at the flux transitions.
4. **Comparison**: a comparator converts the zero-crossings to digital pulses (one per transition).

The resulting signal — a stream of digital pulses at the transition times — is the **raw read signal** that the FDC's PLL works with.

For preservation purposes, the [SuperCard Pro](scp_format.md) hardware can capture this raw read signal directly, storing the time between transitions as a sequence of numbers. This is the most faithful representation of the disk surface.

### 6.6 Read clock recovery in practice

In practice, the PLL locks onto the bit clock within a few byte times after encountering a regular pattern of transitions (such as the gap bytes `0x4E` between sectors). Once locked, it stays locked as long as the bit stream has transitions within the legal MFM spacing (2 µs to 8 µs).

The PLL can lose lock in two situations:

1. **Long gaps** (no transitions for more than 8 µs). This should not happen in well-formed MFM, but can happen on damaged disks or with non-standard encodings.
2. **Sudden frequency changes** (e.g., when reading a track written at a different speed). The PLL will eventually re-lock, but during the re-lock period, bytes will be lost.

The format gaps (GAP1, GAP2, GAP3, GAP4) are filled with regular `0x4E` bytes precisely to keep the PLL locked between fields.

---
## §7. Writing MFM

Writing MFM is conceptually simpler than reading: there is no PLL to lock, no sync marks to search for, no window discrimination to perform. The writer controls the timing precisely. But writing has its own subtleties — most notably **write precompensation** — that affect reliability.

### 7.1 The write process

When the FDC's `WRITE SECTOR` (or `WRITE TRACK` for formatting) command is executed:

1. The FDC asserts the **write gate** signal to the drive, which switches the head from read mode to write mode.
2. The FDC sends bytes to its internal serialiser, which encodes each byte as MFM transitions (applying the rules of §3).
3. The serialized MFM signal drives the **write data** pin, which the drive's write amplifier converts to write-current reversals in the head coil.
4. When the field is complete, the FDC de-asserts the write gate, and the drive returns to read mode.

During writing, the head's write current continuously reverses direction at the transition times, magnetising the disk coating in alternating directions. The magnetic domains on the track are thereby "imprinted" with the MFM pattern.

### 7.2 Write precompensation

When a transition is written, the magnetic field on the disk doesn't instantly snap to the new polarity. There is a slight **peak shift**: the magnetic domain that records a transition "spreads" slightly, and neighbouring transitions can pull each other toward or away from their nominal positions. This effect becomes more pronounced at high transition densities (inner tracks of high-capacity disks).

**Write precompensation** is the technique of writing transitions *slightly earlier or later* than their nominal positions, to compensate for the expected peak shift. The FDC's precompensation logic uses a small table (or formula) that maps the local pattern of bits to a time offset:

```c
int precomp_offset(int prev_data, int data, int next_data) {
    // Returns offset in nanoseconds. Positive = later, negative = earlier.
    if (prev_data == 1 && data == 0 && next_data == 1) return -30;  // Pulled apart
    if (prev_data == 1 && data == 1 && next_data == 1) return +20;  // Pushed together
    // ... and so on for other patterns ...
    return 0;  // No precomp
}
```

The [WD1793](fdc_vg93.md) supports precompensation via the `rclk` pin and a configurable precomp value (typically 0 ns, 125 ns, 250 ns, or 375 ns). Modern FDCs and emulators handle precompensation internally.

For standard Spectrum floppy formats, precompensation is not strictly necessary (the densities are low enough that peak shift is minimal), but it is often applied for marginal reliability improvement.

### 7.3 Write current

The **write current** is the amount of current flowing through the head coil during writing. Too little current, and the magnetic domains don't fully magnetise (resulting in weak signals on readback). Too much current, and the magnetic domains "blur" into each other (resulting in peak shift and bit errors).

For inner tracks (which have a smaller circumference, hence higher linear density), the write current must be **reduced** to prevent blurring. Many drives implement **write current reduction** (WCR), which reduces the write current on tracks beyond a certain threshold (typically track 43 or so). The FDC controls this via a `REDUCE WRITE CURRENT` output pin.

For the standard Spectrum floppy formats (80 tracks × 2 sides × 10 sectors), WCR is usually applied on tracks 40–79.

### 7.4 The format write process

Formatting a track is a special write operation that lays down the entire track structure: IAM, then 10 sectors (each with IDAM, ID field, DAM, data field), separated by the standard gaps. The FDC's `FORMAT TRACK` command takes a parameter specifying the sector size, number of sectors, and gap lengths, and writes the whole track in one revolution.

The data field of each sector is filled with a "fill byte" (typically `0xE5` or `0x00`) on a freshly formatted track. The fill byte is overwritten when the sector is later written with actual data.

Formatting requires the FDC to generate the sync marks (with missing clock bits) at the right places. This is one of the few cases where the FDC's MFM encoder produces non-standard output — normally it follows the MFM rules strictly, but during formatting it deliberately violates them to write the sync marks.

### 7.5 Erase

Erasing a track is equivalent to writing all-zeros (no transitions). In practice, formatting a track with a new pattern effectively erases the old pattern — the new write-current reversals overwrite the old magnetic domains.

Some FDCs have a separate `ERASE` command, but for standard MFM this is rarely used. Formatting is the standard way to erase.

---

## §8. Comparison with FM, M²FM, GCR, RLL

MFM is the most common encoding for floppy disks, but it is not the only one. This section compares MFM to its main competitors.

### 8.1 FM (Frequency Modulation)

| Property | FM | MFM |
|----------|----|----|
| Transitions per data bit | 1.5 average (always clock + data for 1 bits) | 0.75 average (only necessary clock + data for 1 bits) |
| Data density at fixed transition rate | 50% | 100% |
| PLL lock time | Fast (clock bit every cell) | Slower (clock bit only when needed) |
| Sync mark complexity | Simple (any unique pattern works) | Complex (requires missing-clock trick) |
| Typical use | Earliest 8" floppies (1970), microdrives | All modern floppy formats |

MFM's density advantage is decisive for floppy disk, so FM is essentially obsolete except for historical interest.

### 8.2 M²FM (Modified MFM)

M²FM is a refinement of MFM that drops even more clock transitions, achieving a slightly higher density. The rule is:

```
MFM clock rule:   clock[i] = !d[i] && !d[i-1]
M²FM clock rule:  clock[i] = !d[i] && !d[i-1] && !clock[i-1]
```

In other words, M²FM only inserts a clock transition if the *previous* cell didn't have one. This reduces the average clock transition rate from "always between two zeros" to "only between long runs of zeros".

M²FM was used in some early IBM products but never became popular for floppy disks. The complexity of the encoder and PLL is slightly higher than MFM, and the density improvement is small (a few percent). MFM was already good enough.

### 8.3 GCR (Group Coded Recording)

GCR takes a completely different approach: instead of adding clock bits to each data bit, it maps **groups of data bits** to longer codewords chosen to avoid long runs of zeros. The most common GCR code is **4/5 GCR**: each 4-bit nibble is mapped to a 5-bit codeword, with the codewords chosen so that no run of zeros is longer than 2 bits.

| Data nibble | 5-bit GCR codeword |
|-------------|--------------------|
| `0000` | `11001` |
| `0001` | `11011` |
| `0010` | `10010` |
| ... | ... |
| `1111` | `11101` |

GCR achieves higher density than MFM (4/5 GCR stores 4 data bits per 5 transition slots, vs. MFM's ~1 data bit per ~1.5 transition slots). The Apple II and Commodore 1541 used GCR at 4/5 ratio; the Macintosh 400K/800K used a variable-rate GCR.

GCR is **not used on the ZX Spectrum**. All Spectrum floppy systems use MFM. (The reasons are historical: the Western FDC chips that the Spectrum ecosystem adopted — WD177x, WD179x — were MFM-only.)

### 8.4 RLL (Run-Length Limited)

RLL generalises both MFM and GCR. An RLL `(d, k)` code guarantees that:

- At least `d` zeros appear between consecutive 1 bits (limiting the maximum transition density).
- At most `k` zeros appear between consecutive 1 bits (guaranteeing clock recovery).

MFM is an RLL `(1, 3)` code (minimum 1 zero, maximum 3 zeros between transitions, equivalent to 2/4/6/8 µs spacings at 250 kbit/s). 2,7 RLL (used on early hard disks) is `(2, 7)`, allowing higher density by allowing longer runs of zeros.

RLL is rarely used on floppy disk because:

- The complexity of the encoder/decoder is higher than MFM.
- At floppy disk densities, MFM is already adequate.
- The improvement (typically 50% more capacity) doesn't justify the complexity.

For hard disks, RLL (and its successors like EPRML) is universal.

### 8.5 Density comparison

At the same physical transition density (transitions per inch of track):

| Encoding | Relative data density |
|----------|-----------------------|
| FM       | 0.5× (1 data bit per 2 transition slots) |
| MFM      | 1.0× (1 data bit per 1 transition slot, average) |
| M²FM     | ~1.05× |
| 4/5 GCR  | ~1.25× |
| 2,7 RLL  | ~1.5× |

For floppy disks, MFM is the sweet spot: simple, reliable, and supported by all standard FDC chips. Higher-density encodings (GCR, RLL) would offer marginal capacity improvements at the cost of much more complex hardware and software, so the floppy industry standardized on MFM.

---

## §9. The Real-World Floppy Signal

This section puts it all together: a complete end-to-end walkthrough of what the magnetic signal on a floppy disk looks like, from the physical medium to the FDC's decoded bytes.

### 9.1 The physical track

A track on a 3.5" double-density floppy is a **circular band** of magnetic domains, magnetised in alternating directions. The track is located at a specific radius (typically 0.5 mm to 1.5 mm from the center of the disk's recording area), and is read/written by the head positioned at that radius.

The track has no physical "start" — it's a continuous circle. The **index hole** (a small physical hole in the disk jacket, detected by an optical sensor in the drive) provides a reference point: each time the index hole passes the sensor, the drive generates an **index pulse** that the FDC uses to know where the track starts.

### 9.2 The flux transitions

As the disk rotates under the head, the head detects each flux transition (each point where the magnetisation reverses) as a small voltage pulse. For a standard 3.5" disk at 300 RPM with MFM at 250 kbit/s, the transition rate is 0 to 250000 transitions per second (depending on the data pattern), giving a maximum transition frequency of 125 kHz (the Nyquist limit for 250 kHz sampling).

The read signal is a series of pulses, one per transition:

```
Read signal:    _   _       _   _   _       _   _
              _| |_| |_____| |_| |_| |_____| |_| |___

Transitions:    .   .       .   .   .       .   .
Time:           0   2  4    6   8   10  12  14  16  (µs)
```

Each pulse is approximately 1 µs wide (a sharp spike), and the spacing between pulses is 2–8 µs depending on the MFM pattern.

### 9.3 From flux to bytes

The conversion from flux transitions to bytes is a multi-stage process:

1. **Analog conditioning**: the head's raw signal is amplified, filtered, and differentiated to produce clean digital pulses (one per transition).

2. **PLL lock**: the digital pulses drive the FDC's PLL, which recovers the bit clock (a 500 kHz square wave, with one rising edge per window center).

3. **Window discrimination**: the FDC samples the digital pulses at the window centers. A pulse in the clock window is a clock bit; a pulse in the data window is a data bit (a "1"). No pulse means a "0".

4. **Byte assembly**: the data bits are assembled MSB-first into bytes.

5. **Sync detection**: the FDC watches for the `A1*` pattern (three `A1` bytes with missing clock bits). When it sees this pattern, it knows the next byte is an address mark.

6. **Field reading**: the FDC reads the address mark, then the field (ID or data) of the appropriate length, then the CRC.

7. **CRC check**: the FDC computes the CRC of the field and compares it to the stored CRC. If they match, the data is delivered to the host; if not, a CRC error is reported.

This entire pipeline runs continuously as the disk rotates, processing 250 kbit/s of flux data in real time.

### 9.4 The complete track in flux form

A complete track on a standard TR-DOS disk contains about 50000 flux transitions (varying with the data pattern). Stored as a flux-level capture (in the [.SCP](scp_format.md) or .VFLX format), this is about 50 KB of data per track — much larger than the 5 KB of logical sector data.

The flux capture contains every detail of the disk's recording: the exact transition timings, the sync marks, the address marks, the data, the gaps, and any non-standard features (protections, errors, marginal signals). This is why flux-level preservation is the gold standard for archival.

### 9.5 Why not skip MFM and store raw bits?

You might wonder: if the FDC ultimately produces bytes, why not just store the bytes (as a .TRD or .DSK file does) and skip the MFM layer?

The answer is: **you can, for standard formats**. A .TRD file is exactly that — the logical sector contents of a TR-DOS disk, without any MFM encoding. Emulators can load .TRD files directly into emulated RAM without ever simulating MFM.

The reasons to keep the MFM layer are:

1. **Real-hardware compatibility**: if you want to write the .TRD back to a real floppy disk (using a real FDC), you need to re-encode the sectors as MFM (with sync marks, gaps, etc.). This is what tools like `fdrawcmd` do.

2. **Non-standard formats**: if the disk uses non-standard sector sizes, non-standard layout, or copy protection, the .TRD format cannot represent it. You need a format that preserves the MFM layer (like .DSK for sector-level, or .SCP for flux-level).

3. **Emulation accuracy**: some Spectrum software (notably copy-protected games and demos with disk-based loaders) is sensitive to exact MFM timing. For these, the emulator must simulate the MFM layer accurately.

For most purposes, however, the logical sector view (as in .TRD) is sufficient, and MFM is hidden behind the FDC's abstraction.

---
## §10. Cross-References

### 10.1 The floppy format series

MFM encoding is the foundation on which the rest of the floppy stack is built. To see how MFM is used in practice, follow the rest of the floppy series:

- [fdc_vg93.md](fdc_vg93.md) — the WD1793 / KR1818VG93 floppy controller chip. This is the chip that produces and consumes the MFM signal. Its registers, commands, and behavior are determined by the MFM layer described in this article.
- [beta_disk_interface.md](beta_disk_interface.md) — the Beta Disk Interface, the most common Spectrum floppy controller, built around the WD1793. Shows how the FDC connects to the Spectrum's bus and how TR-DOS drives it.
- [plus3_floppy.md](plus3_floppy.md) — the +2A/+3 internal floppy controller, built around the WD1772 (a single-chip integrated controller). Uses MFM at the same 250 kbit/s rate.
- [trd_disk_format.md](trd_disk_format.md) — the TR-DOS logical disk format. Defines the directory structure, file types, and disk parameters that sit on top of the MFM-encoded sectors.
- [trd_scl_formats.md](trd_scl_formats.md) — the .TRD and .SCL disk image formats. These store the logical sector contents (without MFM encoding).
- [dsk_fdi_formats.md](dsk_fdi_formats.md) — the .DSK and .FDI disk image formats. These store the logical sector contents with enough metadata to reproduce the MFM layout.
- [udi_format.md](udi_format.md) — the .UDI universal disk image format. Stores both logical and MFM-level information.
- [scp_format.md](scp_format.md) — the .SCP (SuperCard Pro) flux-level preservation format. Stores the raw flux transitions (the MFM signal itself), allowing perfect preservation of any disk.

### 10.2 Tape encoding (comparison)

The tape subsystem uses a completely different encoding scheme, but the underlying problem is the same: how to embed clock information in a transition-based channel.

- [tape_interface.md](tape_interface.md) — the Spectrum's tape encoding: pilot tone, sync pulses, bit cells of 856 / 1710 T-states. Conceptually similar to MFM (clock + data), but implemented in software by the ROM load routine rather than by a dedicated controller chip.
- [csw_format.md](csw_format.md) — the .CSW format, which is essentially the "flux-level" capture of a tape (the equivalent of .SCP for floppy).

### 10.3 Related topics

- [Reverse engineering](../../08_reverse_engineering/) — disk-based copy protection is one of the most common reverse engineering targets on the Spectrum. Understanding MFM is essential for analysing protected disk formats.
- [Demoscene](../../07_demoscene/) — some demos use non-standard disk loaders that push the limits of the MFM format (e.g., fitting 11 sectors per track instead of the standard 10).
- [Cycle-Exact Emulation Accuracy](../../11_emulation/software/cycle_exact_accuracy.md) — accurate FDC emulation requires simulating the MFM layer at the bit level, which is much more expensive than simulating the logical sector view.

### 10.4 External resources

- [The WD1793 datasheet](https://www.worldofspectrum.org/hardware.html) — the canonical reference for the WD1793 / KR1818VG93 FDC. Includes detailed timing diagrams of the MFM signal.
- **The IBM 3740 format specification** — the original definition of the MFM track layout (IAM, IDAM, DAM, gaps). All later formats (including TR-DOS and +3 DOS) are descended from this.
- **The " FluxSync" website** — a community resource on flux-level floppy preservation, with detailed articles on MFM encoding and PLL behavior.
- **The SuperCard Pro documentation** — covers the .SCP flux format and includes tools for visualising MFM signals.

### 10.5 Where to go next

After understanding MFM encoding, the natural next step is the [FDC chip itself](fdc_vg93.md). The WD1793 / KR1818VG93 datasheet will make much more sense now that you understand what the FDC's data separator does (PLL lock + window discrimination) and how the format commands (`READ SECTOR`, `WRITE SECTOR`, `FORMAT TRACK`) produce the MFM track structure described in this article.

If you are an emulator author, the next step is to implement a digital PLL and an MFM encoder/decoder. The code snippets in §3.5 and §6.2 are starting points; full implementations can be found in open-source FDC emulators (such as the one in FUSE or ZEsarUX).

If you are interested in disk preservation, the next step is the [.SCP format](scp_format.md), which stores the raw flux transitions that the MFM signal is made of.

---

## License

This article is licensed under the **Creative Commons Attribution-ShareAlike 4.0 International License** (CC BY-SA 4.0). You are free to share and adapt this material, provided you credit the original source and license your contributions under the same terms.

For the canonical text of the license, see https://creativecommons.org/licenses/by-sa/4.0/.
