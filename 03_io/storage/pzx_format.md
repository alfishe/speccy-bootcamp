[← Home](../../README.md) · [I/O](../) · [Storage](README.md)

# The .PZX File Format (Pulse-based Tape Representation)

The [.TAP](tap_format.md) and [.TZX](tzx_format.md) formats are block-based: they represent a tape as a sequence of logical blocks (headers, data blocks, silences, etc.). The [.CSW format](csw_format.md) is pulse-based but unstructured: it represents the tape as a flat stream of pulse widths. The **.PZX format** takes a middle path: it is **pulse-based but chunked**, combining the fidelity of .CSW with the structure of .TZX/.SZX.

Created in 2010 by **Fredrik Öhrström** (a Spectrum enthusiast and emulator author), .PZX was designed to address the limitations of both .TZX (which struggles with some non-standard encodings) and .CSW (which lacks structure and metadata). The format uses an **IFF-like chunk structure** (similar to [.SZX](../snapshots/szx_format.md)) to organize the tape data into named, length-prefixed chunks, while preserving the pulse-level fidelity needed for accurate preservation.

This article covers the .PZX format: its history, the chunk-based file structure, the pulse data representation, how to read and write .PZX files, and how it compares to .CSW and .TZX. For the higher-level tape formats, see [tap_format.md](tap_format.md) and [tzx_format.md](tzx_format.md). For the lower-level .CSW format, see [csw_format.md](csw_format.md).

---

## §1. What the .PZX Format Is

### 1.1 Origins

The .PZX format was created in 2010 by **Fredrik Öhrström**, the author of the **Unreal Speccy** emulator (a portable Spectrum emulator for Linux and other platforms). Öhrström was dissatisfied with the existing tape formats:

- **.TAP** was too limited (no turbo loaders, no custom timings).
- **.TZX** was complex and had some representation gaps (particularly for very fast or very irregular encodings).
- **.CSW** lacked structure and metadata, making it hard to inspect or modify.

Öhrström designed .PZX as a **modern, clean, pulse-based format** that would combine the best features of .TZX and .CSW:

- **Chunk-based structure** (like .TZX and .SZX): each piece of data is in a named chunk, making the format easy to parse and extend.
- **Pulse-level fidelity** (like .CSW): the actual tape signal is preserved, without simplification.
- **Metadata support** (like .TZX): publisher, year, author, and other information can be included.
- **Simple and clean design**: the format avoids the historical cruft of .TZX (which has 13 minor versions and many rarely-used block types).

The format has not been formally standardized (there is no specification document comparable to the .TZX specification), but it is documented in the Unreal Speccy source code and has been adopted by several other emulators.

### 1.2 Design philosophy

The .PZX format's design philosophy is **"structured fidelity"**:

- **Structured**: the format uses named chunks (similar to IFF/RIFF/PNG/SZX), making it easy to parse, inspect, and extend.
- **Fidelity**: the format preserves the tape signal at the pulse level, without simplification or interpretation.
- **Clean**: the format avoids historical cruft and rarely-used features, keeping the specification short and the implementation simple.
- **Extensible**: new chunk types can be added without breaking older loaders (which simply skip unknown chunks).

This makes .PZX a good choice for modern tape preservation and emulator development, where both fidelity and maintainability are important.

### 1.3 Scope

A .PZX file contains:

- A **file header** (8 bytes) identifying the format and version.
- An arbitrary number of **chunks**, each containing a piece of the tape data or metadata.

Each chunk has:

- A **4-character ASCII ID** (e.g., "PULS" for pulse data, "TEXT" for text description, "INFO" for archive info).
- A **4-byte length** (the size of the chunk's data, in bytes, little-endian).
- The chunk **data** itself.

The loader reads chunks one at a time. If it doesn't recognize a chunk ID, it skips that chunk (using the length field) and continues.

This is the same design as [.SZX](../snapshots/szx_format.md) (the snapshot format), and it has the same benefits: extensibility, robustness, and ease of parsing.

### 1.4 Why .PZX matters

The .PZX format matters because:

- **It offers a clean, modern alternative** to .TZX and .CSW. For new emulator projects, .PZX is often easier to implement than .TZX (which has a complex block structure) and more structured than .CSW (which is a flat stream).
- **It supports metadata**, which .CSW lacks.
- **It is pulse-based**, which means it can represent any tape signal (like .CSW) — there are no representation gaps.
- **It is used by Unreal Speccy**, a popular emulator, giving it a user base.

The main drawback of .PZX is that it is **less widely supported** than .TZX. Most major emulators support .TZX, but only some support .PZX. For maximum compatibility, .TZX remains the format of choice for tape distribution.

---

## §2. The File Structure

A .PZX file uses an IFF-like chunk structure, similar to .SZX.

### 2.1 The file header (8 bytes)

Every .PZX file begins with an 8-byte header:

| Offset | Size | Field | Notes |
|---|---|---|---|
| 0 | 4 | Magic | "PZXT" (#50 #5A #58 #54) — identifies this as a .PZX file |
| 4 | 4 | Version (little-endian) | The .PZX format version. Currently 1 |

If the first 4 bytes are not "PZXT", the file is not a .PZX file. Loaders should reject it.

### 2.2 The chunks

After the 8-byte header, the file consists of a sequence of chunks. Each chunk has the following structure:

| Offset (within chunk) | Size | Field |
|---|---|---|
| 0 | 4 | Chunk ID (4 ASCII characters) |
| 4 | 4 | Chunk data length (little-endian) |
| 8 | (length) | Chunk data |

The chunk ID identifies what type of data the chunk contains. The chunk data length gives the size of the chunk's data (not including the 8-byte chunk header). The chunk data follows immediately.

After the chunk data, the next chunk begins (or EOF if there are no more chunks).

### 2.3 The standard chunk types

The standard .PZX chunk IDs:

| Chunk ID | Name | Content |
|---|---|---|
| `PULS` | Pulse data | A sequence of pulse widths (the actual tape signal) |
| `TEXT` | Text description | A free-text description of the tape |
| `INFO` | Archive info | Structured metadata (publisher, year, author, etc.) |
| `TIME` | Timing info | Sample rate, polarity, and other timing parameters |
| `STOP` | Stop marker | Marks the end of the tape (optional) |
| `PAUS` | Pause | A period of silence |

The most important chunk type is **PULS** (pulse data), which contains the actual tape signal. The other chunk types are for metadata and control.

### 2.4 Chunk ordering

Chunks can appear in any order, but the natural sequence for a typical tape is:

1. `TEXT` — the tape description.
2. `INFO` — the archive metadata.
3. `TIME` — the timing parameters.
4. `PULS` — the first block's pulses.
5. `PAUS` — the gap between blocks.
6. `PULS` — the second block's pulses.
7. `PAUS` — another gap.
8. ...

Multiple `PULS` and `PAUS` chunks can appear in sequence, representing the blocks and gaps of the tape.

### 2.5 Skipping unknown chunks

As with .SZX, the most important rule of .PZX loading is: **if you encounter a chunk ID you don't recognize, skip it using the chunk data length and continue with the next chunk**. Do not abort the load.

This rule is what makes .PZX extensible. A loader that aborts on unknown chunks would be unable to load .PZX files written by newer tools.

### 2.6 Hex view

A small .PZX file might look like this in hex:

```
Offset 0x00: 50 5A 58 54 01 00 00 00    <- File header: "PZXT" + version 1
Offset 0x08: 54 45 58 54 0E 00 00 00    <- Chunk: ID="TEXT", length=14
Offset 0x10: 4D 61 6E 69 63 20 4D 69    <- Chunk data: "Manic Mi"
Offset 0x18: 6E 65 72 20 31 39 38 33    <- "ner 1983"
Offset 0x20: 50 55 4C 53 00 40 00 00    <- Chunk: ID="PULS", length=16384
Offset 0x28: ...                         <- Chunk data: 16384 bytes of pulse widths
```

This layout — file header followed by heterogeneous chunks — is typical of IFF-derived formats.

---

## §3. The Pulse Data Representation

The `PULS` chunk contains the actual tape signal as a sequence of pulse widths. This section covers the pulse data format in detail.

### 3.1 The PULS chunk structure

The `PULS` chunk contains a sequence of pulse widths, stored as 16-bit little-endian values (2 bytes per pulse). Each value represents the duration of one pulse, in T-states.

| Offset (within chunk data) | Size | Field |
|---|---|---|
| 0 | 2 | First pulse width (T-states, little-endian) |
| 2 | 2 | Second pulse width |
| 4 | 2 | Third pulse width |
| ... | ... | ... |

The pulse widths alternate between high and low levels (or low and high, depending on the polarity specified in the `TIME` chunk). The first pulse is high (by convention), the second is low, the third is high, and so on.

### 3.2 Why T-states?

Unlike .CSW (which uses samples at a configurable sample rate), .PZX uses **T-states directly**. This avoids the sample-rate conversion issue that plagues .CSW (where the sample rate may not divide evenly into the Z80 clock).

By using T-states, .PZX achieves cycle-exact representation of the tape signal. The emulator does not need to convert between samples and T-states — it just plays back the specified number of T-states for each pulse.

### 3.3 The maximum pulse width

Each pulse width is stored as a 16-bit value, so the maximum pulse width is **65535 T-states** (about 18.7 ms at 3.5 MHz). Pulses longer than this (e.g., long silences) must be split into multiple pulses.

For silence periods, the `PAUS` chunk is used instead of `PULS`. The `PAUS` chunk specifies the silence duration in milliseconds (up to about 65 seconds), which is much longer than a single `PULS` chunk could represent.

### 3.4 Compression

The basic .PZX format does not include compression: each pulse width is stored as a 2-byte value. For a typical 48K program, this results in a .PZX file of about 100 KB (twice the size of the equivalent .TZX file).

Some implementations of .PZX support an optional compression scheme (using zlib or a simple RLE), but this is not part of the core format. For most use cases, the uncompressed size is acceptable.

### 3.5 The polarity convention

The first pulse in a `PULS` chunk is assumed to be **high** (signal level 1), and subsequent pulses alternate. If the tape signal starts with a low pulse, the loader should insert a zero-width high pulse at the beginning.

This convention simplifies the playback code: the emulator just toggles the EAR level for each pulse, starting from high.

### 3.6 Relationship to the TIME chunk

The `TIME` chunk (if present) specifies additional timing parameters:

- The sample rate (for compatibility with .CSW-style captures).
- The polarity (whether the first pulse is high or low).
- The T-states per frame (for cycle-exact frame timing).

If the `TIME` chunk is absent, the loader assumes the default values (T-states directly, polarity high-first, standard frame timing).

---

## §4. Writing a .PZX File

This section shows how to generate a .PZX file from a sequence of pulse widths.

### 4.1 Writing the file header

```c
void pzx_write_header(FILE *f) {
    uint8_t header[8] = {
        'P', 'Z', 'X', 'T',  // Magic: "PZXT"
        1, 0, 0, 0           // Version 1
    };
    fwrite(header, 1, 8, f);
}
```

### 4.2 Writing a TEXT chunk

```c
void pzx_write_text_chunk(FILE *f, const char *text) {
    uint32_t length = strlen(text);
    fwrite("TEXT", 1, 4, f);
    fwrite(&length, 4, 1, f);  // Little-endian length
    fwrite(text, 1, length, f);
}
```

### 4.3 Writing a PULS chunk

```c
void pzx_write_puls_chunk(FILE *f, const uint16_t *pulses, int count) {
    uint32_t length = count * 2;  // 2 bytes per pulse
    fwrite("PULS", 1, 4, f);
    fwrite(&length, 4, 1, f);
    for (int i = 0; i < count; i++) {
        fputc(pulses[i] & 0xFF, f);           // Low byte
        fputc((pulses[i] >> 8) & 0xFF, f);    // High byte
    }
}
```

### 4.4 Writing a PAUS chunk

```c
void pzx_write_paus_chunk(FILE *f, uint32_t duration_ms) {
    uint32_t length = 4;  // 4 bytes for the duration
    fwrite("PAUS", 1, 4, f);
    fwrite(&length, 4, 1, f);
    fwrite(&duration_ms, 4, 1, f);  // Little-endian duration in ms
}
```

### 4.5 A complete .PZX generator

```c
void pzx_generate(const char *filename, const char *text,
                  const uint16_t *pulses, int count) {
    FILE *f = fopen(filename, "wb");

    pzx_write_header(f);
    if (text) pzx_write_text_chunk(f, text);
    pzx_write_puls_chunk(f, pulses, count);

    fclose(f);
}
```

### 4.6 Converting from .TZX or .CSW

Converting a .TZX or .CSW file to .PZX is straightforward: play back the source file, recording each pulse width, then write the widths to a .PZX `PULS` chunk.

```c
void pzx_convert_from_tzx(const char *tzx_filename, const char *pzx_filename) {
    FILE *tzx = fopen(tzx_filename, "rb");
    FILE *pzx = fopen(pzx_filename, "wb");

    pzx_write_header(pzx);

    uint16_t pulses[MAX_PULSES];
    int n_pulses = 0;

    // Play back the .TZX, recording pulse widths
    // ... (similar to the .CSW conversion code) ...

    // Write the pulses as a single PULS chunk
    pzx_write_puls_chunk(pzx, pulses, n_pulses);

    fclose(tzx);
    fclose(pzx);
}
```

The resulting .PZX file faithfully represents the same tape signal as the source file.

---

## §5. Reading a .PZX File (Emulator Playback)

This section covers how an emulator plays back a .PZX file.

### 5.1 The playback loop

```c
void pzx_play(SpectrumState *state, FILE *f) {
    // Read the file header
    uint8_t header[8];
    fread(header, 1, 8, f);
    if (memcmp(header, "PZXT", 4) != 0) {
        fprintf(stderr, "Not a .PZX file\n");
        return;
    }

    // Read and play each chunk
    while (!feof(f)) {
        char chunk_id[5] = {0};
        uint32_t length;

        if (fread(chunk_id, 1, 4, f) != 4) break;
        if (fread(&length, 4, 1, f) != 1) break;

        if (memcmp(chunk_id, "PULS", 4) == 0) {
            pzx_play_puls_chunk(state, f, length);
        } else if (memcmp(chunk_id, "PAUS", 4) == 0) {
            pzx_play_paus_chunk(state, f, length);
        } else if (memcmp(chunk_id, "TEXT", 4) == 0) {
            // Display the text to the user (optional)
            fseek(f, length, SEEK_CUR);
        } else {
            // Unknown chunk: skip
            fseek(f, length, SEEK_CUR);
        }
    }
}
```

### 5.2 Playing a PULS chunk

```c
void pzx_play_puls_chunk(SpectrumState *state, FILE *f, uint32_t length) {
    int n_pulses = length / 2;
    int level = 1;  // First pulse is high

    for (int i = 0; i < n_pulses; i++) {
        uint8_t lo = fgetc(f);
        uint8_t hi = fgetc(f);
        uint16_t width = lo | (hi << 8);

        tape_generate_pulse(state, width, level);
        level = !level;  // Toggle level for the next pulse
    }
}
```

### 5.3 Playing a PAUS chunk

```c
void pzx_play_paus_chunk(SpectrumState *state, FILE *f, uint32_t length) {
    uint32_t duration_ms;
    fread(&duration_ms, 4, 1, f);

    // Convert ms to T-states (at 3.5 MHz, 1 ms = 3500 T-states)
    int t_states = duration_ms * 3500;
    tape_generate_silence(state, t_states);
}
```

### 5.4 Cycle-exactness

Because .PZX stores pulse widths directly in T-states, playback is inherently cycle-exact. The emulator does not need to convert between samples and T-states (as it does for .CSW). This is one of .PZX's main advantages over .CSW.

---

## §6. Comparison with .CSW and .TZX

| Feature | .PZX | .CSW | .TZX |
|---|---|---|---|
| **Representation level** | Pulse (T-states) | Pulse (samples) | Block |
| **File structure** | IFF-like chunks | Flat stream | Block-based |
| **Standard ROM blocks** | ✅ | ✅ | ✅ |
| **Turbo loaders** | ✅ | ✅ | ✅ |
| **Analog protections** | ✅ | ✅ | ⚠️ (limited) |
| **Metadata** | ✅ (TEXT, INFO) | v2 only | ✅ |
| **Cycle-exact** | ✅ (T-states) | ⚠️ (sample conversion) | ✅ |
| **File size (typical)** | 100 KB | 20–50 KB | 20–50 KB |
| **Parser complexity** | Simple (chunks) | Simple | Complex |
| **Emulator support** | Moderate | Wide | Wide |

### 6.1 .PZX vs .CSW

.PZX and .CSW are both pulse-based formats, but .PZX has several advantages:

- **T-states instead of samples**: .PZX stores pulse widths in T-states, avoiding the sample-rate conversion issue of .CSW.
- **Chunk structure**: .PZX uses named chunks, making it easy to parse and extend. .CSW uses a flat stream, which is harder to inspect.
- **Metadata**: .PZX includes TEXT and INFO chunks for metadata. .CSW (v1) has no metadata.

The main disadvantage of .PZX vs .CSW is **file size**: .PZX is typically larger (because it doesn't use the run-length compression that .CSW uses by default). However, .PZX could be extended with compression without changing the format.

### 6.2 .PZX vs .TZX

.PZX and .TZX are both structured formats, but they take different approaches:

- **.TZX is block-based**: each block represents a logical unit (a header, a data block, a silence). This makes it efficient for typical tapes, but limits its ability to represent non-standard signals.
- **.PZX is pulse-based**: each chunk represents a sequence of pulses. This makes it less efficient for typical tapes (larger files), but more flexible for non-standard signals.

For most Spectrum tapes, .TZX is the better choice (smaller files, wider support). For tapes with analog protections or non-standard encodings, .PZX (or .CSW) is needed.

---

## §7. Use Cases

The .PZX format is used for several specific purposes.

### 7.1 Modern tape preservation

For modern tape preservation projects, .PZX offers a clean, cycle-exact representation that avoids the historical cruft of .TZX. Some preservation projects use .PZX as their working format, converting to .TZX or .TAP for distribution.

### 7.2 Emulator development

For emulator developers, .PZX is often easier to implement than .TZX (because the chunk structure is simpler) and more accurate than .CSW (because it uses T-states directly). New emulator projects may choose .PZX as their primary tape format.

### 7.3 Analog protection analysis

For reverse engineers analysing analog protections, .PZX provides a faithful, cycle-exact representation of the tape signal. The pulse-level data can be analyzed to understand the protection scheme.

### 7.4 Custom loader development

For developers writing custom loaders, .PZX provides a convenient way to test the loader against a known tape signal. The developer can generate a .PZX file with specific pulse widths and test the loader's response.

---

## §8. Compatibility and Quirks

### 8.1 Emulator support

| Emulator | .PZX support | Notes |
|---|---|---|
| **Unreal Speccy** | ✅ Full | Reference implementation (Fredrik Öhrström) |
| **Fuse** | ⚠️ Partial | Read support in recent versions |
| **ZEsarUX** | ⚠️ Partial | Read support |
| **SpecEmu** | ❌ | Not supported |
| **EightyOne** | ❌ | Not supported |

.PZX is less widely supported than .TZX or .CSW. For maximum compatibility, .TZX is preferred.

### 8.2 The version issue

The .PZX format has not been formally versioned (beyond the version field in the header, which is always 1). Some implementations may use non-standard chunks or interpretations, which could cause compatibility issues.

### 8.3 The file size issue

Because .PZX does not include compression by default, .PZX files are typically larger than equivalent .TZX files (about 100 KB vs 50 KB for a 48K program). This makes .PZX less suitable for distribution, where file size matters.

Some implementations support optional compression (e.g., gzip-compressed .PZX files), but this is not part of the core format.

### 8.4 The documentation issue

Unlike .TZX (which has a formal specification document), .PZX is documented only in the Unreal Speccy source code. This makes it harder for third-party developers to implement .PZX support, and it increases the risk of incompatible implementations.

---

## §9. Worked Example: A Small .PZX

This section walks through a small .PZX file representing a single pilot pulse.

### 9.1 The pulse

Suppose we want to represent a single pilot pulse of 2168 T-states.

### 9.2 The PULS chunk

The `PULS` chunk for a single pulse of 2168 T-states:

```
50 55 4C 53             <- Chunk ID: "PULS"
02 00 00 00             <- Chunk data length: 2 bytes
68 08                   <- Pulse width: 0x0868 = 2168 (little-endian)
```

(#0868 = 2168 in decimal.)

### 9.3 A complete .PZX file

A complete .PZX file with just the header and one PULS chunk:

```
Offset 0x00: 50 5A 58 54 01 00 00 00    <- File header: "PZXT" + version 1
Offset 0x08: 50 55 4C 53 02 00 00 00    <- Chunk: ID="PULS", length=2
Offset 0x10: 68 08                       <- Pulse width: 2168 T-states
```

Total file size: 18 bytes.

### 9.4 A run of pulses

For 8063 consecutive pilot pulses of 2168 T-states each, the PULS chunk contains 8063 × 2 = 16126 bytes of pulse data. There is no run-length compression in the basic .PZX format, so each pulse is stored as a separate 2-byte value.

This is the main disadvantage of .PZX: for long runs of identical pulses (like the pilot tone), the file size is larger than it needs to be.

### 9.5 A more realistic example

A complete pilot tone (8063 pulses) + sync pulses + a small data block might be:

```
[File header: "PZXT" v1]
[PULS chunk: 8063 pilot pulses of 2168 T-states + 2 sync pulses + data pulses]
[PAUS chunk: 1000 ms silence]
[PULS chunk: more data pulses]
```

The total file size for a 48K program is typically about 100 KB.

---

## §10. Cross-References

### 10.1 The rest of the tape series

- [tape_interface.md](tape_interface.md) — the hardware layer: EAR/MIC circuits, ULA, port `#FE`, bit-banging.
- [tape_format.md](tape_format.md) — the logical data format: blocks, headers, block types, checksums.
- [tap_format.md](tap_format.md) — the simplest tape file format.
- [tzx_format.md](tzx_format.md) — the most comprehensive block-based tape file format.
- [csw_format.md](csw_format.md) — the Compressed Square Wave format, a flat pulse-based format.

### 10.2 The snapshot formats

These live in the sibling [../snapshots/](../snapshots/README.md) directory.

- [sna_format.md](../snapshots/sna_format.md), [z80_format.md](../snapshots/z80_format.md), [szx_format.md](../snapshots/szx_format.md), [rzx_format.md](../snapshots/rzx_format.md) — snapshot and replay formats. .PZX's chunk structure is inspired by .SZX.

### 10.3 Related topics

- [Reverse engineering](../../08_reverse_engineering/) — .PZX files are used for analog protection analysis.
- [Demoscene](../../07_demoscene/) — demos that use non-standard loaders may be preserved in .PZX form.

### 10.4 External resources

- [Unreal Speccy](https://sdkcad.free.fr/) — the reference implementation of .PZX (Fredrik Öhrström).
- [The .PZX documentation](https://sdkcad.free.fr/) — documented in the Unreal Speccy source code.

### 10.5 Where to go next

After understanding .PZX, you have completed the tour of the major Spectrum tape formats:

1. [.TAP](tap_format.md) — the simplest, most widely supported format.
2. [.TZX](tzx_format.md) — the most comprehensive block-based format.
3. [.CSW](csw_format.md) — the flat pulse-based format for maximum fidelity.
4. .PZX — the structured pulse-based format, combining fidelity with clean design.

Each format has its strengths and weaknesses. For most purposes, .TAP (for standard software) or .TZX (for turbo-loaded software) is the right choice. .CSW and .PZX are reserved for special cases where maximum fidelity is required.

If you are interested in tape preservation, the best practice is to keep tapes in multiple formats: .TZX for distribution, .CSW or .PZX for archival. This ensures that the tapes can be loaded by any emulator, while also preserving the maximum amount of information for future generations.

---

## License

This article is licensed under the **Creative Commons Attribution-ShareAlike 4.0 International License** (CC BY-SA 4.0). You are free to share and adapt this material, provided you credit the original source and license your contributions under the same terms.

For the canonical text of the license, see https://creativecommons.org/licenses/by-sa/4.0/.
