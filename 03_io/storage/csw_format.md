[← Home](../../README.md) · [I/O](../) · [Storage](README.md)

# The .CSW File Format (Compressed Square Wave)

The [.TAP](tap_format.md) and [.TZX](tzx_format.md) formats represent Spectrum tapes at the **block level**: each block is a logical unit (a header, a data block, a silence period, etc.) with its own structure and semantics. But some tapes cannot be faithfully represented at the block level — they use analog protections, non-standard encodings, or signal patterns that defy block-based description.

The **.CSW format** (Compressed Square Wave) takes a different approach: it represents the tape signal at the **pulse level**, as a sequence of pulse widths. Each entry in a .CSW file describes how long the EAR signal stayed at a particular level before the next transition. This is the lowest-level representation of a tape signal that is still practical to store — below this level, you would need to store raw audio samples.

Created in 2001 by **Simon Owen** (the author of the **Disk Image Manager** tools), .CSW was designed for **maximum fidelity preservation** of tapes that cannot be represented by .TZX. It uses a simple but effective run-length encoding scheme to keep file sizes manageable.

This article covers the .CSW format: its history, the file structure, the compression scheme, how to read and write .CSW files, and how it compares to .TZX and .TAP. For the higher-level tape formats, see [tap_format.md](tap_format.md) and [tzx_format.md](tzx_format.md). For the hardware layer, see [tape_interface.md](tape_interface.md).

---

## §1. What the .CSW Format Is

### 1.1 Origins

The .CSW format was created in 2001 by **Simon Owen**, a Spectrum enthusiast and the author of the **Disk Image Manager** (Disk2Disk, DiskImg) tools. Owen needed a format that could represent tape signals at the pulse level, for two reasons:

1. **Analog protections**: some Spectrum tapes (notably those from **Ocean** and **Gremlin**) used analog protection schemes that could not be represented by .TZX's block structure. The protection relied on specific signal patterns (e.g., unusual pulse widths, deliberate noise) that defied block-based description.
2. **Cycle-exact preservation**: for historical accuracy, Owen wanted a format that could capture the tape signal exactly as it appeared on the original tape, without any interpretation or simplification.

The .CSW format was designed to meet both needs. It represents the tape signal as a sequence of pulse widths, with a simple run-length encoding scheme to keep file sizes manageable.

The format has gone through two versions:

- **v1 (2001)**: the original format, with a small fixed-size header and a simple RLE compression scheme.
- **v2 (2004)**: an extended format with a 32-byte header (allowing metadata) and a more flexible compression scheme.

Most modern emulators support both versions.

### 1.2 Design philosophy

The .CSW format's design philosophy is **"the signal, the whole signal, and nothing but the signal"**:

- **The signal**: .CSW represents the tape signal directly, as a sequence of pulse widths. There is no block structure, no logical interpretation, no metadata about the program.
- **The whole signal**: every pulse is represented, including the pilot tone, sync pulses, data pulses, gaps, and any noise or protection signals.
- **Nothing but the signal**: .CSW does not attempt to interpret the signal. It just records the pulse widths and lets the emulator (or the Spectrum's loader code) do the interpretation.

This makes .CSW the most faithful representation of a tape signal, short of storing raw audio samples. The trade-off is that .CSW files are larger than equivalent .TZX files (because they store every pulse, not just the logical blocks), and they are harder to inspect or modify (because there is no block structure to work with).

### 1.3 Scope

A .CSW file contains:

- A **header** identifying the format, version, sample rate, and other parameters.
- A stream of **pulse width samples**, compressed via run-length encoding.

Each sample represents the duration of one pulse (one period of constant signal level, between two transitions). The sequence of samples, when played back at the sample rate, reproduces the original tape signal.

The .CSW file does **not** contain:

- Block structure (no headers, no data blocks, no logical interpretation).
- Metadata about the program (no filename, no publisher, no year) — at least not in v1.
- Pilot tone, sync pulse, or bit timing information (these are implicit in the pulse widths).

### 1.4 Why .CSW matters

The .CSW format matters because:

- **It can represent any tape signal**, including analog protections and non-standard encodings that .TZX cannot.
- **It is the format of last resort** for preservation: when no other format can faithfully represent a tape, .CSW can.
- **It is the basis for some emulator features** like "record to tape" (where the emulator records the EAR signal to a .CSW file).
- **It is simpler than raw audio**: .CSW is much smaller than raw audio (because it stores pulse widths, not samples), and it is easier to process (because the pulses are already synchronized to the signal).

---

## §2. The File Structure

A .CSW file consists of a header followed by a stream of compressed pulse widths.

### 2.1 The v1 header

The v1 header (introduced in 2001) is a small, fixed-size header that identifies the file and provides the minimum information needed to interpret the pulse data. It contains three pieces of information:

1. **A magic string** — a short ASCII identifier (a truncated form of "Compressed Square Wave") that allows loaders to recognize the file as a .CSW file.
2. **A sample rate** — a 16-bit little-endian value giving the sample rate in Hz (typically 44100). All pulse widths in the file are measured in samples at this rate.
3. **A polarity flag** — a single byte indicating whether the first pulse is high or low (most loaders default to positive-first, where the first pulse is a rising edge).

The v1 header is followed immediately by the compressed pulse data stream (see §3). There is no metadata beyond these three fields: no filename, no publisher, no year, no compression-scheme selector. This was one of the main limitations that motivated the v2 revision.

> **Note**: The exact byte offsets of the v1 header fields vary slightly between implementations and are not fully standardized in the original specification. The v2 header (below) is the recommended format for new .CSW files because it defines a precise, documented layout.

### 2.2 The v2 header (32 bytes)

The v2 header (introduced in 2004) is larger and more structured. Its layout is:

| Offset | Size | Field | Notes |
|---|---|---|---|
| 0 | 16 | Magic | "Compressed Squar" (a truncated form of "Compressed Square Wave", no null terminator) |
| 16 | 1 | Major version | Always 2 for v2 files |
| 17 | 1 | Minor version | Currently 0 |
| 18 | 4 | Sample rate (little-endian, Hz) | Typically 44100 |
| 22 | 1 | Polarity flag | Bit 0: first pulse polarity (0 = positive-first, 1 = negative-first) |
| 23 | 1 | Compression flag | 0 = RLE (the standard scheme); other values reserved |
| 24 | 4 | Header extension length | Bytes of additional metadata following the 32-byte fixed header (often 0) |
| 28 | 4 | Reserved | Reserved for future use (typically 0) |

After the 32-byte fixed header, an optional extension block of `header extension length` bytes may follow (containing free-form metadata). Then the compressed pulse data stream begins.

The v2 header is the recommended format for new .CSW files. Its explicit length field and version numbers make it easier to parse and extend than the v1 header.

### 2.3 The data stream

After the header (and any header extension), the .CSW file contains the pulse data as a stream of compressed pulse widths. Each entry in the stream describes one pulse (one period of constant signal level between two transitions).

The compression scheme is **run-length encoding**: short pulses are encoded as a single byte (the width in samples), while long runs of identical pulses are encoded as a marker byte followed by a count and a width. The next section (§3) covers the compression scheme in detail.

For now, the key point is that the data stream represents a sequence of pulse widths, where each pulse alternates between high and low (or low and high, depending on the polarity flag in the header).

---

## §3. The Compression Scheme

The .CSW format uses a simple but effective run-length encoding scheme to compress the pulse data. This section covers the scheme in detail.

### 3.1 The basic idea

A tape signal consists of a sequence of pulses, where each pulse is a period of constant signal level (either high or low) followed by a transition to the opposite level. The duration of each pulse varies: pilot pulses are long (~2168 T-states), data pulses are shorter (~855 or ~1710 T-states), and silence is very long (millions of T-states).

If we stored each pulse's duration as a 16-bit value, a typical tape would require about 100 KB of storage (there are roughly 50000 pulses in a 48K program, each taking 2 bytes). That is manageable, but it can be reduced.

The .CSW compression scheme exploits the fact that many pulses have the same width. For example, the pilot tone consists of 8063 identical pulses of 2168 T-states each. Instead of storing 8063 separate width values, .CSW stores a single run-length entry: "8063 pulses of 2168 T-states each".

### 3.2 The encoding

The .CSW encoding distinguishes between short pulses and long runs:

- **Short pulses** (width 1–255 samples): stored as a single byte, the width in samples.
- **Long runs** (many pulses of the same width, or pulses wider than 255 samples): stored as a marker byte (#00), followed by a count (2 bytes), followed by a width (2 bytes).

The encoding rules are:

**v1 encoding (the standard RLE scheme):**
- The data is a sequence of bytes.
- A byte value of 1–255 represents a single pulse of that many samples.
- A byte value of #00 is a special marker: the next 2 bytes are a count (little-endian), and the following 2 bytes are a width (little-endian, in samples). This represents "count" consecutive pulses of "width" samples each.

So for a single pulse of 100 samples, the encoding is just `0x64` (one byte).

For 8063 consecutive pulses of 55 samples each (the pilot tone at 44100 Hz sample rate), the encoding is `0x00 0x7F 0x1F 0x37 0x00` (5 bytes: marker, count low, count high, width low, width high).

### 3.3 The sample rate

The pulse widths in .CSW are stored in **samples**, not in T-states. To convert between samples and T-states, you need the sample rate:

```
T-states = samples × 3500000 / sample_rate
```

For a sample rate of 44100 Hz:

```
T-states per sample = 3500000 / 44100 ≈ 79.36
```

This non-integer conversion factor introduces rounding errors when the emulator converts sample-based pulse widths to T-states. For high-fidelity playback, the emulator should round to the nearest T-state, accepting that the playback timing will differ slightly from the original.

An alternative is to use a sample rate that divides evenly into the Z80 clock. For example, a sample rate of 35000 Hz gives exactly 100 T-states per sample:

```
T-states per sample = 3500000 / 35000 = 100
```

Many .CSW files use 44100 Hz (the standard audio CD sample rate) because they are derived from audio captures, but this introduces a small amount of timing error on playback. Files generated from .TZX conversion may use 35000 Hz (or another "clean" rate) for exact T-state conversion.

### 3.4 The polarity flag

The polarity flag in the header determines whether the first pulse is high or low:

- **Polarity 0 (positive-first)**: the first pulse is high.
- **Polarity 1 (negative-first)**: the first pulse is low.

The polarity typically doesn't matter for loading (the Schmitt trigger on the EAR input handles either polarity), but it is recorded for fidelity.

### 3.5 End-of-data

The .CSW file ends when there are no more bytes to read. There is no explicit end-of-data marker — the file just ends.

Some .CSW files have a trailing #00 marker (with count 0 and width 0) to indicate the end, but this is not standard. The standard way to detect end-of-data is to check for EOF.

### 3.6 Compression ratio

The .CSW compression scheme is very effective for typical Spectrum tapes:

- **Pilot tones** (8063 pulses of the same width) compress from 16126 bytes (2 bytes per pulse) to 5 bytes (a single run-length entry). That's a 3000:1 compression ratio for the pilot tone.
- **Data** (varying pulse widths) compresses less well, but still achieves about 2:1 compression on average.
- **Silence** (very long pulses) compresses extremely well — a 1-second silence is a single run-length entry.

Overall, a typical .CSW file for a 48K program is about 20–50 KB, compared to about 100 KB uncompressed (2 bytes per pulse). This is comparable to .TZX and larger than .TAP.

---

## §4. Writing a .CSW File

This section shows how to generate a .CSW file from a sequence of pulse widths.

### 4.1 Generating the header

```c
void csw_write_header(FILE *f, uint32_t sample_rate, int polarity) {
    // Magic: first 16 chars of "Compressed Square Wave"
    const char *magic = "Compressed Squar";
    fwrite(magic, 1, 16, f);

    // Sample rate (little-endian, 2 bytes)
    fputc(sample_rate & 0xFF, f);
    fputc((sample_rate >> 8) & 0xFF, f);

    // Polarity flag
    fputc(polarity ? 1 : 0, f);

    // ... additional header fields for v2 ...
}
```

### 4.2 Generating the pulse data

To generate the compressed pulse data:

```c
void csw_write_pulses(FILE *f, const uint16_t *pulses, int count) {
    int i = 0;
    while (i < count) {
        // Look ahead for a run of identical pulses
        uint16_t width = pulses[i];
        int run_length = 1;
        while (i + run_length < count &&
               pulses[i + run_length] == width &&
               run_length < 65535) {
            run_length++;
        }

        if (width > 0 && width <= 255 && run_length == 1) {
            // Single short pulse: one byte
            fputc(width, f);
        } else {
            // Run-length entry: 0x00 + count (2 bytes) + width (2 bytes)
            fputc(0x00, f);
            fputc(run_length & 0xFF, f);
            fputc((run_length >> 8) & 0xFF, f);
            fputc(width & 0xFF, f);
            fputc((width >> 8) & 0xFF, f);
        }

        i += run_length;
    }
}
```

### 4.3 A complete .CSW generator

```c
void csw_generate(const char *filename, uint32_t sample_rate,
                  const uint16_t *pulses, int count) {
    FILE *f = fopen(filename, "wb");
    csw_write_header(f, sample_rate, 0);  // Polarity 0 = positive-first
    csw_write_pulses(f, pulses, count);
    fclose(f);
}
```

### 4.4 Converting from .TZX to .CSW

Converting a .TZX file to .CSW is straightforward: play back the .TZX file in an emulator-like loop, recording each pulse's width, then write the widths to a .CSW file.

```c
void csw_convert_from_tzx(const char *tzx_filename, const char *csw_filename,
                           uint32_t sample_rate) {
    // Open the .TZX file
    FILE *tzx = fopen(tzx_filename, "rb");

    // Play back the .TZX, recording pulse widths
    uint16_t pulses[MAX_PULSES];
    int n_pulses = 0;

    // ... (play back the .TZX, calling record_pulse() for each pulse) ...

    // Write the .CSW file
    csw_generate(csw_filename, sample_rate, pulses, n_pulses);

    fclose(tzx);
}
```

This produces a .CSW file that faithfully represents the same tape signal as the .TZX file.

---

## §5. Reading a .CSW File (Emulator Playback)

This section covers how an emulator plays back a .CSW file.

### 5.1 The playback loop

```c
void csw_play(SpectrumState *state, FILE *f) {
    // Read the header
    CswHeader header;
    csw_read_header(f, &header);

    int level = (header.polarity == 0) ? 1 : 0;  // Initial level

    // Read and play each pulse
    int byte;
    while ((byte = fgetc(f)) != EOF) {
        uint16_t width;
        int count;

        if (byte == 0x00) {
            // Run-length entry: read count and width
            int cl = fgetc(f); int ch = fgetc(f);
            int wl = fgetc(f); int wh = fgetc(f);
            count = cl | (ch << 8);
            width = wl | (wh << 8);
        } else {
            // Single pulse
            count = 1;
            width = byte;
        }

        // Convert width from samples to T-states
        int t_states = width * 3500000 / header.sample_rate;

        // Play 'count' pulses of 't_states' T-states each
        for (int i = 0; i < count; i++) {
            tape_generate_pulse(state, t_states, level);
            level = !level;  // Toggle level for the next pulse
        }
    }
}
```

### 5.2 Cycle-exactness

Like .TZX, .CSW playback requires cycle-exact Z80 emulation for accurate loading. The pulse widths are specified in samples (which must be converted to T-states), and the conversion may introduce rounding errors. For high-fidelity playback, the emulator should use a sample rate that divides evenly into the Z80 clock (e.g., 35000 Hz, which gives exactly 100 T-states per sample).

### 5.3 Performance considerations

.CSW playback is typically slower than .TZX playback, because the emulator must process every pulse individually (rather than generating blocks of pulses with known structure). For long tapes, .CSW playback can be significantly slower, which is why most emulators prefer .TZX when possible.

---

## §6. Use Cases

The .CSW format is used for several specific purposes where .TZX is insufficient.

### 6.1 Analog protections

Some Spectrum tapes (notably from Ocean and Gremlin in the late 1980s) used **analog protections** that relied on specific signal patterns. For example:

- **Deliberate noise**: the tape would include bursts of noise that the loader code would detect and use as a decryption key.
- **Unusual pulse widths**: the tape would use pulse widths that did not fit the standard encoding, requiring the loader to measure timings very precisely.
- **Multiple signal layers**: the tape would carry multiple overlapping signals (e.g., a standard loader plus a hidden protection signal).

These protections cannot be represented by .TZX's block structure, because they are not block-based. .CSW can represent them, because it captures every pulse individually.

### 6.2 Raw tape captures

For preservation purposes, archivists sometimes capture tapes directly from the original hardware, using a sound card or a dedicated tape interface. The resulting raw captures are essentially audio waveforms, which can be converted to .CSW by detecting the pulse widths.

This is the most faithful way to preserve a tape, because it captures the signal exactly as it appeared on the original hardware (including any analog quirks, noise, or distortion).

### 6.3 Non-standard loaders

Some custom loaders use encodings that .TZX cannot represent (e.g., three-level encodings, variable-length pulses, phase-encoded data). .CSW can represent these, because it does not interpret the signal — it just records the pulse widths.

### 6.4 Emulator "record to tape" feature

Some emulators have a "record to tape" feature: the user can connect a real tape recorder to the computer's audio input, and the emulator records the signal to a file. The natural file format for this is .CSW, because it can capture any signal from the tape recorder.

---

## §7. Compatibility and Quirks

### 7.1 Emulator support

| Emulator | .CSW support | Notes |
|---|---|---|
| **Fuse** | ✅ Full | Supports v1 and v2 |
| **ZEsarUX** | ✅ Full | Supports v1 and v2 |
| **SpecEmu** | ✅ Full | Cycle-exact playback |
| **EightyOne** | ⚠️ Partial | v1 only |
| **SPIN** | ⚠️ Partial | v1 only |
| **Qaop** | ❌ | Not supported |

Most modern emulators support .CSW, but it is less widely supported than .TAP or .TZX. For maximum compatibility, .TAP or .TZX is preferred when possible.

### 7.2 Version differences

The main differences between v1 and v2:

- **v1 (2001)**: small fixed header, simple RLE compression, no metadata.
- **v2 (2004)**: 32-byte structured header (with metadata extension), more flexible compression (including zlib compression in some implementations), support for non-Spectrum machines.

Most .CSW files on the internet are v1. v2 is used mainly by modern archiving tools that want to include metadata.

### 7.3 The sample rate issue

The .CSW format stores pulse widths in samples, not in T-states. The sample rate is specified in the header, but it may not divide evenly into the Z80 clock (3.5 MHz). For example, a sample rate of 44100 Hz gives 79.36 T-states per sample — a non-integer value that forces the emulator to round.

For high-fidelity playback, the emulator should use a sample rate that divides evenly into the Z80 clock (e.g., 35000 Hz, 17500 Hz, etc.). But many .CSW files use 44100 Hz (the audio CD standard), which introduces a small amount of timing error.

### 7.4 The polarity issue

The polarity flag in the header determines whether the first pulse is high or low. Some .CSW files have the wrong polarity flag (due to capture errors or format conversion), which can cause loading failures on polarity-sensitive loaders.

Most emulators handle this by trying both polarities and using whichever works, but some loaders are polarity-sensitive and require the correct polarity.

---

## §8. Comparison with .TZX and .TAP

| Feature | .CSW | .TZX | .TAP |
|---|---|---|---|
| **Representation level** | Pulse | Block | Block |
| **Standard ROM blocks** | ✅ (as pulses) | ✅ | ✅ |
| **Turbo loaders** | ✅ | ✅ | ❌ |
| **Analog protections** | ✅ | ⚠️ (limited) | ❌ |
| **Non-standard encodings** | ✅ | ✅ | ❌ |
| **Metadata** | v2 only | ✅ | ❌ |
| **File size (typical)** | 20–50 KB | 20–50 KB | 49 KB |
| **Parser complexity** | Simple | Complex | Simple |
| **Emulator support** | Wide | Wide | Universal |

### 8.1 When to use .CSW

Use .CSW when:

- The tape uses **analog protections** that .TZX cannot represent.
- You are capturing a tape from **raw audio** and want maximum fidelity.
- You need to represent a **non-standard encoding** that .TZX cannot handle.
- You are implementing an emulator's **"record to tape"** feature.

### 8.2 When to use .TZX instead

Use .TZX instead of .CSW when:

- The tape uses **standard or turbo blocks** (the vast majority of cases).
- You want **metadata** (publisher, year, author) without using v2.
- You want the **smallest file size** for typical tapes.
- You want the **widest emulator support** (.TZX is more widely supported than .CSW).

### 8.3 The relationship between .CSW and .TZX

Every .TZX file can be converted to .CSW (by playing back the .TZX and recording the pulses). Most .CSW files can be converted to .TZX (by detecting block boundaries and timings), but some .CSW files (with analog protections) cannot be converted to .TZX without losing information.

For preservation, the best practice is to keep both: .TZX for distribution (since it is more widely supported) and .CSW for archival (since it is more faithful).

---

## §9. Worked Example: A Small .CSW

This section walks through a small .CSW file representing a single pilot pulse.

### 9.1 The pulse

Suppose we want to represent a single pilot pulse of 2168 T-states at a sample rate of 44100 Hz. The pulse width in samples is:

```
samples = 2168 × 44100 / 3500000 ≈ 27.32 samples
```

Rounding, the pulse is 27 samples wide.

### 9.2 The .CSW encoding

For a single pulse of 27 samples, the .CSW encoding is:

```
0x1B    <- Single byte: width = 27 samples
```

(#1B = 27 in decimal.)

### 9.3 A run of pulses

For 8063 consecutive pilot pulses of 27 samples each, the .CSW encoding is:

```
0x00                    <- Run-length marker
0x7F 0x1F               <- Count: 0x1F7F = 8063 (little-endian)
0x1B 0x00               <- Width: 27 samples (little-endian)
```

This 5-byte sequence represents 8063 pulses — a compression ratio of over 3000:1 compared to storing each pulse separately.

### 9.4 The full pilot tone

A complete pilot tone (8063 pulses) followed by the two sync pulses would be:

```
0x00 0x7F 0x1F 0x1B 0x00    <- 8063 pilot pulses of 27 samples
0x00 0x01 0x00 0x08 0x00    <- 1 sync pulse 1 of 8 samples
0x00 0x01 0x00 0x09 0x00    <- 1 sync pulse 2 of 9 samples
```

(The sample widths are approximate; the actual values would be 667 × 44100 / 3500000 ≈ 8.4 samples and 735 × 44100 / 3500000 ≈ 9.26 samples.)

### 9.5 File size

For a complete 48K program, the .CSW file would contain roughly:

- 1 pilot tone (8063 pulses) + 2 sync pulses + 49152 × 8 × 2 data pulses = about 800000 pulses.
- Compressed (with run-length encoding for the pilot and repeated data), the file is typically 20–50 KB.

This is comparable to .TZX and larger than .TAP (which is about 49 KB for the same program).

---

## §10. Cross-References

### 10.1 The rest of the tape series

- [tape_interface.md](tape_interface.md) — the hardware layer: EAR/MIC circuits, ULA, port `#FE`, bit-banging.
- [tape_format.md](tape_format.md) — the logical data format: blocks, headers, block types, checksums.
- [tap_format.md](tap_format.md) — the simplest tape file format.
- [tzx_format.md](tzx_format.md) — the most comprehensive block-based tape file format.
- [pzx_format.md](pzx_format.md) — an alternative pulse-based format, similar in spirit to .CSW.

### 10.2 The snapshot formats

These live in the sibling [../snapshots/](../snapshots/README.md) directory.

- [sna_format.md](../snapshots/sna_format.md), [z80_format.md](../snapshots/z80_format.md), [szx_format.md](../snapshots/szx_format.md), [rzx_format.md](../snapshots/rzx_format.md) — snapshot and replay formats.

### 10.3 Related topics

- [Reverse engineering](../../08_reverse_engineering/) — .CSW files are used for analog protection analysis.
- [Demoscene](../../07_demoscene/) — demos that use non-standard loaders may be preserved only in .CSW form.

### 10.4 External resources

- **The .CSW specification** — the canonical document for the .CSW format.
- **Disk Image Manager** — Simon Owen's tools, including .CSW support.
- **World of Spectrum** — has a small number of .CSW files for tapes with analog protections.

### 10.5 Where to go next

After understanding .CSW, the natural next step is [.PZX](pzx_format.md), an alternative pulse-based format that takes a different approach to the same problem. .PZX is newer than .CSW and uses a more structured representation of pulse sequences.

If you are interested in tape preservation, .CSW is the format of last resort — the format to use when no other format can faithfully represent the tape. For most purposes, .TZX is preferred (because it is more widely supported and includes metadata), but .CSW is essential for analog protections and raw captures.

---

## License

This article is licensed under the **Creative Commons Attribution-ShareAlike 4.0 International License** (CC BY-SA 4.0). You are free to share and adapt this material, provided you credit the original source and license your contributions under the same terms.

For the canonical text of the license, see https://creativecommons.org/licenses/by-sa/4.0/.
