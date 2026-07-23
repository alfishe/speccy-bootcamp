[← Home](../../README.md) · [I/O](../) · [Storage](README.md)

# The .TAP File Format

The [tape data format](tape_format.md) describes the logical structure of blocks on a Spectrum tape: a header block followed by data blocks, each with a flag byte and checksum. But this is the format of the **tape signal** — the sequence of pulses on the EAR/MIC lines. When you want to store a "tape" on a modern computer, as a single file that an emulator can load, you need a **file format** that represents this sequence of blocks.

The **.TAP file format** is the simplest such format. Created in the mid-1990s by the authors of early Spectrum emulators (notably **X128** by Thomas Schreiber), .TAP represents a tape as a sequence of logical blocks. Each block is just a 2-byte length followed by the block's payload — no timing information, no pilot tone, no compression. The .TAP format is the **de facto standard** for distributing Spectrum software in tape form, and every major emulator supports it.

This article covers the .TAP file format: its history, its simple file structure, how to read and write .TAP files, its limitations (especially around turbo loaders), and how it relates to the more capable .TZX format. For the logical data format that .TAP blocks represent, see [tape_format.md](tape_format.md). For the hardware layer (pilot tones, sync pulses, bit timings), see [tape_interface.md](tape_interface.md).

---

## §1. What the .TAP Format Is

### 1.1 Origins

The .TAP format was created in the mid-1990s by **Thomas Schreiber**, the author of the **X128** emulator (one of the earliest Spectrum emulators for DOS). Schreiber needed a file format that could represent Spectrum tapes — the input to `LOAD ""` — in a form that an emulator could read.

His design was deliberately minimal: a .TAP file is just a sequence of blocks, where each block is a 2-byte length followed by the block's payload. The payload is exactly the data that would be transmitted on the tape (flag byte + data + checksum — see [tape_format.md](tape_format.md) §2). No timing information, no pilot tone, no metadata about the emulator or the source tape.

The simplicity was intentional: the format is trivial to parse (read 2 bytes, read that many bytes, repeat until EOF) and trivial to generate. It captures the logical structure of a Spectrum tape without any extraneous detail.

### 1.2 Design philosophy

The .TAP format's design philosophy is **"just the data"**:

- **No file header**: the file begins immediately with the first block. There is no magic number, no version number, no metadata.
- **No timing information**: each block is just a payload. The emulator is expected to generate the standard pilot tone, sync pulses, and bit timings when playing back the block.
- **No compression**: blocks are stored raw. If you want to compress a .TAP file, you compress the whole file (e.g., with gzip), not individual blocks.
- **No metadata**: there is no place to record the source tape, the emulator that created the .TAP, or any other provenance information.

This minimalism is the format's greatest strength and its greatest weakness:

- **Strength**: the format is universally supported. Every Spectrum emulator can read and write .TAP files. The format is so simple that adding .TAP support to an emulator takes only a few dozen lines of code.
- **Weakness**: the format cannot represent non-standard blocks (turbo loaders, custom encodings, compressed data). For tapes that use such blocks, .TZX is needed (see [tzx_format.md](tzx_format.md)).

### 1.3 Scope

A .TAP file contains:

- A sequence of **blocks**, where each block is:
  - A 2-byte **length** (little-endian).
  - A payload of **length** bytes, which is exactly the data that would be transmitted on the tape: flag byte + data + checksum.

The .TAP file does **not** contain:

- A file header (no magic, no version, no metadata).
- Timing information (the emulator uses standard ROM timings).
- Pilot tone, sync pulses, or bit timings (the emulator generates these from the block type).
- Compression (blocks are stored raw).
- Custom loader information (the format cannot represent non-standard blocks).

### 1.4 Why .TAP matters

The .TAP format matters because:

- **It is the simplest tape format**, and therefore the most widely supported. Every emulator can read .TAP files.
- **It is the most common distribution format** for Spectrum software on tape. Sites like World of Spectrum offer .TAP files for the vast majority of standard (non-turbo) Spectrum software.
- **It is easy to generate and inspect**. A .TAP file can be created with a few lines of code, and its contents can be inspected with a hex editor.
- **It is the basis for more sophisticated formats**. The .TZX format (see [tzx_format.md](tzx_format.md)) extends the .TAP concept with support for non-standard blocks and timings, but a .TAP file is essentially a .TZX file with only standard blocks.

---

## §2. The File Structure

A .TAP file is a sequence of blocks. There is no file header, no magic number, and no end-of-file marker — the file simply ends when there are no more blocks.

### 2.1 The file layout

```
┌────────────────────────────────────────────────────────────┐
│  Block 1: length (2 bytes) + data (length bytes)           │
├────────────────────────────────────────────────────────────┤
│  Block 2: length (2 bytes) + data (length bytes)           │
├────────────────────────────────────────────────────────────┤
│  Block 3: length (2 bytes) + data (length bytes)           │
├────────────────────────────────────────────────────────────┤
│  ...                                                        │
├────────────────────────────────────────────────────────────┤
│  Block N: length (2 bytes) + data (length bytes)           │
└────────────────────────────────────────────────────────────┘
```

A loader reads blocks until the end of the file. There is no explicit block count — the file just ends.

### 2.2 Detecting the end of the file

The standard way to detect the end of a .TAP file is to try to read the next block's length:

- If `fread(&length, 2, 1, f)` returns 0 (or fewer than 2 bytes read), the file is over.
- If `fread(&length, 2, 1, f)` returns 1 (2 bytes successfully read), then read `length` more bytes as the block data.

There is no end-of-file marker, no block count, and no checksum at the file level. The only integrity check is the per-block checksum inside each block's payload (see [tape_format.md](tape_format.md) §2.3).

### 2.3 The block sequence

A typical .TAP file for a single Spectrum program contains two blocks:

1. **Header block** (19 bytes): flag byte (`#00`) + 17 bytes of header data + checksum.
2. **Data block** (variable size): flag byte (`#FF`) + data bytes + checksum.

For a multi-block file (e.g., a multi-load game), the .TAP file contains more blocks, in the order they appear on the tape.

### 2.4 A hex view

A small .TAP file (a header block + a small data block) might look like this in hex:

```
Offset 0x00: 13 00                       <- Block 1 length: 0x0013 = 19 bytes
Offset 0x02: 00 00 54 65 73 74 20 20     <- Flag byte (#00) + block type (00=Program) + "Test  "
Offset 0x0A: 20 20 20 20 64 00 0A 00     <- "    " + data length (#0064=100) + param 1 (#000A=10)
Offset 0x12: 50 00 ??                    <- param 2 (#0050=80) + checksum
Offset 0x15: 65 00                       <- Block 2 length: 0x0065 = 101 bytes
Offset 0x17: FF ?? ?? ?? ...             <- Flag byte (#FF) + 100 data bytes + checksum
```

The first block is 19 bytes (the standard header block size). The second block is 101 bytes (1 flag byte + 100 data bytes + 1 checksum byte). The total file size is 2 + 19 + 2 + 101 = 124 bytes.

### 2.5 No alignment, no padding

Blocks are **not padded** to any alignment boundary. The next block starts immediately after the previous block's data. This keeps the format compact but means loaders must read lengths carefully (an off-by-one error can corrupt the rest of the file).

### 2.6 Big-endian vs little-endian

The block length is stored **little-endian** (low byte first, then high byte), matching the Z80's convention. So a block of length 0x0013 (19) is stored as the two bytes `13 00` (not `00 13`).

This is consistent with the rest of the Spectrum's tape format (where all multi-byte values are little-endian) and with the Z80's native byte order.

---

## §3. The Block Format

Each block in a .TAP file consists of a 2-byte length followed by the block's data. The data is exactly what would be transmitted on the tape: the flag byte, the block data (header or payload), and the checksum.

### 3.1 The block header

Each block is preceded by a 2-byte header:

| Offset (within block) | Size | Field |
|---|---|---|
| 0 | 2 | Data length (little-endian) |

The data length gives the number of bytes that follow (the block's payload, including the flag byte and checksum).

### 3.2 The block data

The block data is `data_length` bytes, structured as follows:

| Offset (within block data) | Size | Field | Notes |
|---|---|---|---|
| 0 | 1 | Flag byte | `#00` for a header block, `#FF` for a data block |
| 1 | varies | Block payload | For a header: 17 bytes of header data. For a data block: the raw data bytes |
| data_length - 1 | 1 | Checksum | XOR of all bytes (including the flag byte) |

For a **header block**, the data length is always **19** (1 flag byte + 17 header bytes + 1 checksum).

For a **data block**, the data length is `1 + N + 1`, where `N` is the number of data bytes specified in the preceding header's data length field.

### 3.3 Reading a block

The C code to read a single block from a .TAP file:

```c
typedef struct {
    uint16_t length;
    uint8_t *data;
} TapBlock;

int tap_read_block(FILE *f, TapBlock *block) {
    // Read the 2-byte length
    uint8_t len_bytes[2];
    if (fread(len_bytes, 1, 2, f) != 2) {
        return 0;  // EOF
    }
    block->length = len_bytes[0] | (len_bytes[1] << 8);

    // Allocate and read the data
    block->data = malloc(block->length);
    if (fread(block->data, 1, block->length, f) != block->length) {
        free(block->data);
        return -1;  // Truncated file
    }

    return 1;  // Success
}
```

### 3.4 Writing a block

The C code to write a single block to a .TAP file:

```c
int tap_write_block(FILE *f, const TapBlock *block) {
    // Write the 2-byte length (little-endian)
    uint8_t len_bytes[2] = {
        block->length & 0xFF,
        (block->length >> 8) & 0xFF
    };
    if (fwrite(len_bytes, 1, 2, f) != 2) return -1;

    // Write the data
    if (fwrite(block->data, 1, block->length, f) != block->length) return -1;

    return 0;  // Success
}
```

### 3.5 Verifying the checksum

After reading a block, the loader can verify its checksum by XORing all bytes (including the flag byte and the checksum byte itself). If the result is `#00`, the block is valid:

```c
int tap_verify_block(const TapBlock *block) {
    uint8_t xor = 0;
    for (int i = 0; i < block->length; i++) {
        xor ^= block->data[i];
    }
    return (xor == 0);  // Valid if XOR of all bytes (including checksum) is 0
}
```

This works because the checksum byte is the XOR of all the preceding bytes. XORing all bytes (data + checksum) produces `data_checksum XOR checksum_byte = data_checksum XOR data_checksum = #00`.

### 3.6 The maximum block size

The block length is a 16-bit value, so the maximum block size is **65535 bytes**. This is the same limit as the underlying tape format (the header's data length field is also 16-bit).

In practice, blocks are typically a few KB. The 48K Spectrum's RAM is only 48 KB, so a single block cannot load more than that. Multi-block files can load more data in total, but each individual block is limited to 65535 bytes.

---

## §4. Standard Block Types in .TAP

The .TAP format inherits the standard block types from the tape data format. This section summarises how the standard blocks appear in .TAP files.

### 4.1 Header blocks (flag byte `#00`)

A header block in a .TAP file has:

- **Data length**: 19 bytes (always).
- **Flag byte**: `#00` (offset 0 of the block data).
- **Header data**: 17 bytes (offsets 1–17 of the block data), structured as described in [tape_format.md](tape_format.md) §3.
- **Checksum**: 1 byte (offset 18 of the block data).

The header data contains:

| Offset (within block data) | Size | Field |
|---|---|---|
| 1 | 1 | Block type (0=Program, 1=Number Array, 2=Character Array, 3=Code) |
| 2 | 10 | Filename (10 characters, space-padded) |
| 12 | 2 | Data length of the following data block (little-endian) |
| 14 | 2 | Parameter 1 (interpretation depends on block type) |
| 16 | 2 | Parameter 2 (interpretation depends on block type) |
| 18 | 1 | Checksum |

The .TAP format does not add any metadata to the header — it stores the header exactly as it would appear on the tape.

### 4.2 Data blocks (flag byte `#FF`)

A data block in a .TAP file has:

- **Data length**: `1 + N + 1`, where N is the data length specified in the preceding header.
- **Flag byte**: `#FF` (offset 0 of the block data).
- **Data**: N bytes (offsets 1 to N of the block data).
- **Checksum**: 1 byte (offset N+1 of the block data).

The data is stored raw — no compression, no encoding. The bytes are exactly the bytes that would be loaded into memory.

### 4.3 The standard 2-block sequence

A typical .TAP file for a single Spectrum program contains two blocks:

```
[Header block (19 bytes)] [Data block (variable size)]
```

The header block specifies the program's filename, block type, data length, and parameters. The data block contains the program's bytes.

This 2-block structure is what the ROM's `LOAD ""` command expects: it reads the first block as a header, then reads the second block as data.

### 4.4 Multi-block sequences

A .TAP file can contain more than two blocks. For a multi-load game, the sequence might be:

```
[Loader header] [Loader data] [Level 1 header] [Level 1 data] [Level 2 header] [Level 2 data] ...
```

Each header+data pair is loaded separately, either by the ROM (for the first pair) or by the loader program (for subsequent pairs).

### 4.5 Non-standard blocks

The .TAP format does not have a way to represent non-standard blocks (e.g., turbo loader blocks with custom timings). If a tape contains such blocks, a .TAP file cannot faithfully represent it — the non-standard blocks must either be omitted or approximated as standard blocks.

For tapes with non-standard blocks, the .TZX format (see [tzx_format.md](tzx_format.md)) is required. .TZX can represent any block, including turbo loader blocks with custom timings.

In practice, most commercial Spectrum software (which uses turbo loaders) is distributed in .TZX form. The .TAP format is used primarily for:

- **Standard (ROM-loaded) software**: programs that load via the ROM's standard `LOAD ""` command.
- **Homebrew and modern software**: programs that do not use custom loaders.
- **BASIC programs**: which always use the standard load mechanism.

### 4.6 Empty .TAP files

An empty .TAP file (zero bytes) is technically valid — it represents a tape with no blocks. Loading such a file into an emulator does nothing (the emulator waits for a block that never arrives).

Some emulators use empty .TAP files as placeholders or as the initial state for a "record to tape" feature (where the emulator starts with an empty tape and records the user's `SAVE` commands into it).

---

## §5. Writing a .TAP File

This section shows how to generate a .TAP file from a program, using C-style pseudocode.

### 5.1 Generating a header block

To generate a header block for a Code block (the most common case):

```c
void tap_write_code_header(FILE *f, const char *filename,
                           uint16_t start_addr, uint16_t data_length) {
    uint8_t header[19];
    uint8_t checksum = 0;

    // Flag byte
    header[0] = 0x00;  // Header block
    checksum ^= header[0];

    // Block type: Code (3)
    header[1] = 0x03;
    checksum ^= header[1];

    // Filename (10 chars, space-padded)
    memset(&header[2], ' ', 10);
    int name_len = strlen(filename);
    if (name_len > 10) name_len = 10;
    memcpy(&header[2], filename, name_len);
    for (int i = 0; i < 10; i++) checksum ^= header[2 + i];

    // Data length (little-endian)
    header[12] = data_length & 0xFF;
    header[13] = (data_length >> 8) & 0xFF;
    checksum ^= header[12];
    checksum ^= header[13];

    // Parameter 1: start address (for Code blocks)
    header[14] = start_addr & 0xFF;
    header[15] = (start_addr >> 8) & 0xFF;
    checksum ^= header[14];
    checksum ^= header[15];

    // Parameter 2: 0x8000 (unused for Code)
    header[16] = 0x00;
    header[17] = 0x80;
    checksum ^= header[16];
    checksum ^= header[17];

    // Checksum
    header[18] = checksum;

    // Write the 2-byte length, then the 19 bytes
    uint8_t len[2] = { 19, 0 };
    fwrite(len, 1, 2, f);
    fwrite(header, 1, 19, f);
}
```

### 5.2 Generating a data block

To generate a data block from raw bytes:

```c
void tap_write_data_block(FILE *f, const uint8_t *data, uint16_t length) {
    // Allocate a buffer for flag + data + checksum
    int total = 1 + length + 1;
    uint8_t *block = malloc(total);

    // Flag byte
    block[0] = 0xFF;

    // Data
    memcpy(&block[1], data, length);

    // Checksum (XOR of all preceding bytes)
    uint8_t checksum = 0;
    for (int i = 0; i < total - 1; i++) {
        checksum ^= block[i];
    }
    block[total - 1] = checksum;

    // Write the 2-byte length, then the block
    uint8_t len[2] = { total & 0xFF, (total >> 8) & 0xFF };
    fwrite(len, 1, 2, f);
    fwrite(block, 1, total, f);

    free(block);
}
```

### 5.3 Putting it together: a complete .TAP generator

To generate a .TAP file for a Code block:

```c
void tap_generate_code(const char *filename, const char *tap_filename,
                       uint16_t start_addr, const uint8_t *data, uint16_t length) {
    FILE *f = fopen(tap_filename, "wb");
    tap_write_code_header(f, filename, start_addr, length);
    tap_write_data_block(f, data, length);
    fclose(f);
}
```

This produces a 2-block .TAP file (header + data) that the ROM's `LOAD "" CODE` command can load.

### 5.4 Generating a Program block

For a BASIC program, the header is similar but uses block type 0 (Program) and different parameter semantics:

```c
void tap_write_program_header(FILE *f, const char *filename,
                              uint16_t data_length, uint16_t auto_run_line,
                              uint16_t program_length) {
    uint8_t header[19];
    uint8_t checksum = 0;

    header[0] = 0x00;  // Header block
    header[1] = 0x00;  // Block type: Program
    // ... fill in filename, data_length, auto_run_line, program_length ...
    // ... compute checksum ...
    // ... write 2-byte length (19) + 19 bytes of header ...
}
```

The data block contains the tokenised BASIC program followed by the variables area.

### 5.5 Generating a SCREEN$ block

A SCREEN$ block is just a Code block with start address `#4000` and data length 6912:

```c
void tap_generate_screen(const char *tap_filename, const uint8_t *screen_data) {
    FILE *f = fopen(tap_filename, "wb");
    tap_write_code_header(f, "", 0x4000, 6912);
    tap_write_data_block(f, screen_data, 6912);
    fclose(f);
}
```

The resulting .TAP file can be loaded with `LOAD "" SCREEN$`.

---

## §6. Reading a .TAP File (Emulator Playback)

This section covers how an emulator plays back a .TAP file — translating the block data into the audio signal that the Spectrum's EAR input would see.

### 6.1 The playback loop

The emulator's .TAP playback works as follows:

1. Read the first block from the .TAP file.
2. Generate the pilot tone (a sequence of ~2168 T-state pulses, 8063 for a header or 3223 for data — determined by the flag byte).
3. Generate the two sync pulses (667 and 735 T-states).
4. Generate the data pulses: for each byte, for each bit (MSB first), generate two pulses of 855 T-states (for a 0) or 1710 T-states (for a 1).
5. Generate the final pulse (955 T-states).
6. If there are more blocks, generate a gap (typically about 1 second of silence) and go to step 1.

The emulator's "tape player" is essentially a state machine that generates these pulses on the EAR input line.

### 6.2 The pulse generator

The core of the playback is the **pulse generator**: a function that drives the EAR input high or low for a specified number of T-states. In an emulator, this is typically implemented as part of the main CPU loop:

```c
void tape_generate_pulse(SpectrumState *state, int t_states, int level) {
    // Drive the EAR input to 'level' for 't_states' T-states
    state->ear_level = level;
    advance_cpu(state, t_states);
}
```

The `advance_cpu` function runs the Z80 for the specified number of T-states, during which the Z80's `IN A, (#FE)` instructions read the current `ear_level`.

### 6.3 Generating a bit

To generate a single bit (two pulses):

```c
void tape_generate_bit(SpectrumState *state, int bit) {
    int pulse_length = bit ? 1710 : 855;  // 1: 1710, 0: 855
    tape_generate_pulse(state, pulse_length, 1);  // High
    tape_generate_pulse(state, pulse_length, 0);  // Low
}
```

### 6.4 Generating a byte

To generate a byte (MSB first):

```c
void tape_generate_byte(SpectrumState *state, uint8_t byte) {
    for (int i = 7; i >= 0; i--) {
        int bit = (byte >> i) & 1;
        tape_generate_bit(state, bit);
    }
}
```

### 6.5 Generating a block

To generate a complete block (pilot + sync + data + final pulse):

```c
void tape_play_block(SpectrumState *state, const TapBlock *block) {
    int is_header = (block->data[0] == 0x00);
    int pilot_count = is_header ? 8063 : 3223;

    // Pilot tone
    for (int i = 0; i < pilot_count; i++) {
        tape_generate_pulse(state, 2168, 1);
        tape_generate_pulse(state, 2168, 0);
    }

    // Sync pulses
    tape_generate_pulse(state, 667, 1);  // First sync pulse (high)
    tape_generate_pulse(state, 735, 0);  // Second sync pulse (low)

    // Data
    for (int i = 0; i < block->length; i++) {
        tape_generate_byte(state, block->data[i]);
    }

    // Final pulse
    tape_generate_pulse(state, 955, 1);
}
```

### 6.6 Playing a complete .TAP file

To play an entire .TAP file:

```c
void tape_play_tap(SpectrumState *state, const char *filename) {
    FILE *f = fopen(filename, "rb");
    TapBlock block;

    while (tap_read_block(f, &block) > 0) {
        tape_play_block(state, &block);
        free(block.data);

        // Inter-block gap (about 1 second of silence)
        tape_generate_silence(state, 69888);  // 1 frame = 69888 T-states
    }

    fclose(f);
}
```

### 6.7 The "warp" playback mode

Many emulators offer a **warp playback** mode (also called "instant load" or "fast load"). In warp mode, the emulator does not generate the full pilot tone, sync pulses, and bit timings. Instead, it directly loads the block data into the Spectrum's memory, bypassing the ROM loader entirely.

Warp playback is much faster than real-time playback (typically instant), but it requires the emulator to understand the block structure:

- For a header block, the emulator reads the block type, filename, and parameters.
- For a data block, the emulator writes the data directly to the address specified by the preceding header.

This is how emulators achieve sub-second load times for .TAP files, even though the original tape would have taken minutes.

Warp playback does not work for non-standard blocks (turbo loaders), because the emulator does not know how to interpret them. For non-standard blocks, the emulator must fall back to real-time playback, which is why .TZX files (which preserve the timings) are needed for turbo-loaded software.

---

## §7. Limitations

The .TAP format's simplicity is both its strength and its weakness. This section covers the format's limitations.

### 7.1 No custom timings

The biggest limitation: .TAP files **cannot represent non-standard timings**. Every block is assumed to use the standard ROM timings:

- Pilot tone: 2168 T-states per pulse, 8063 pulses (header) or 3223 (data).
- Sync pulses: 667 and 735 T-states.
- Bit pulses: 855 T-states (for 0) and 1710 T-states (for 1).
- Final pulse: 955 T-states.

If a tape uses different timings (e.g., a turbo loader with shorter pulses), a .TAP file cannot represent it. The .TAP file would either omit the non-standard block or approximate it as a standard block (which would not load correctly on a real Spectrum).

For tapes with non-standard timings, the .TZX format (see [tzx_format.md](tzx_format.md)) is required. .TZX can represent any timing, including turbo loader timings.

### 7.2 No turbo loaders

Because of the timing limitation, .TAP files **cannot represent turbo loaders**. A turbo-loaded game cannot be faithfully stored in a .TAP file.

Some emulators work around this by providing a "standard speed" version of the turbo loader in the .TAP file (i.e., the loader is rewritten to use standard timings). This produces a .TAP file that loads correctly, but it is not the original turbo loader — it is a modified version.

For faithful preservation of turbo-loaded software, .TZX is required.

### 7.3 No custom encodings

Some custom loaders use non-standard bit encodings (e.g., three pulse durations instead of two, or run-length-encoded data). The .TAP format cannot represent these, because it assumes the standard 2-pulse-per-bit encoding.

Again, .TZX can represent custom encodings via its "pure tone", "pulse sequence", and "pure data" block types.

### 7.4 No metadata

The .TAP format has **no place for metadata**:

- No emulator identifier (which emulator created the .TAP).
- No source tape identifier (which tape the .TAP was made from).
- No creation date or timestamp.
- No author or copyright information.
- No comments.

The only "metadata" is the filename in each header block (which is part of the Spectrum's standard format, not the .TAP container).

For archival purposes, this means that .TAP files must be accompanied by external metadata (in a sidecar file, a database, or a web page). The .TZX format includes optional metadata blocks, which is one reason it is preferred for archival.

### 7.5 No compression

The .TAP format does not support compression. Blocks are stored raw, so a .TAP file for a 48K program is about 49 KB.

Some users compress .TAP files with external tools (gzip, zip), producing `.tap.gz` or `.zip` files. Emulators typically decompress these on the fly. But the .TAP format itself has no compression.

The .TZX format supports a "compressed data" extension, but it is rarely used.

### 7.6 No custom block types

The .TAP format recognises only two flag byte values: `#00` (header) and `#FF` (data). Blocks with other flag byte values (used by some custom loaders) are stored in the .TAP file but are interpreted as standard blocks (with unpredictable results when played back).

The .TZX format can represent arbitrary block types via its "custom info" and "glue" block types.

### 7.7 Limitations summary

| Feature | .TAP | .TZX |
|---|---|---|
| Standard ROM blocks | ✅ | ✅ |
| Turbo loader blocks | ❌ | ✅ |
| Custom timings | ❌ | ✅ |
| Custom encodings | ❌ | ✅ |
| Metadata | ❌ | ✅ |
| Compression | ❌ | (Rare) |
| Custom block types | ❌ | ✅ |
| Simplicity | ✅ | ❌ |

The trade-off is clear: .TAP is simple but limited; .TZX is complex but capable. For most purposes (distributing standard Spectrum software), .TAP is sufficient. For preservation (especially of turbo-loaded software), .TZX is required.

---

## §8. Comparison with .TZX

This section compares .TAP and .TZX in more detail, to help you choose the right format for a given use case.

### 8.1 When to use .TAP

Use .TAP when:

- The software uses the **standard ROM loader** (no turbo loader, no custom timings).
- You want **maximum compatibility** (every emulator supports .TAP).
- You want **small files** (.TAP files are typically smaller than equivalent .TZX files, because they omit timing information).
- You are distributing **BASIC programs** or **simple machine code programs** that do not need a custom loader.

### 8.2 When to use .TZX

Use .TZX when:

- The software uses a **turbo loader** (Speedlock, Alcatraz, Bleepload, etc.).
- The software uses **custom timings** or **custom encodings**.
- You are **preserving** a tape for archival purposes and want the highest fidelity.
- The software has **multiple loading stages** with different timings.

### 8.3 File size comparison

For a standard Spectrum program, the .TAP and .TZX files are roughly the same size:

- .TAP: each block is 2 + 19 = 21 bytes (header) or 2 + N + 2 bytes (data).
- .TZX: each block is 19 + N bytes (header) or 19 + N bytes (data), plus a small file header.

For a typical 48K program, the .TAP file is about 49 KB, and the .TZX file is about 49 KB (the overhead is negligible).

For turbo-loaded software, only .TZX can represent the tape. There is no .TAP equivalent.

### 8.4 Conversion

Converting from .TAP to .TZX is straightforward:

- A .TAP file is essentially a .TZX file with only "standard speed" blocks.
- The conversion tool reads each .TAP block and emits a corresponding .TZX "standard speed" block.

Converting from .TZX to .TAP is possible only if the .TZX file contains only standard blocks:

- If the .TZX file contains turbo loader blocks, custom timings, or other non-standard blocks, the conversion will lose information (or fail).
- Conversion tools typically warn the user if the .TZX file cannot be losslessly converted to .TAP.

Several tools exist for .TAP ↔ .TZX conversion, including:

- **TZX Tools** (by Tomasz K.): a command-line toolkit for converting between tape formats.
- **tzx2tap** and **tap2tzx**: simple converters included with many emulator distributions.
- **ZEsarUX** (the emulator): can load .TZX files and export them as .TAP (with warnings about non-convertible blocks).

### 8.5 The .TAP-only emulators

Some emulators support only .TAP files, not .TZX. These are typically very simple emulators (often early or minimal ones) that focus on standard software. Modern full-featured emulators (Fuse, ZEsarUX, SpecEmu, etc.) support both formats.

If you are targeting a .TAP-only emulator, you must use .TAP — which means you cannot faithfully represent turbo-loaded software.

### 8.6 The modern recommendation

For modern Spectrum development and distribution, the recommendation is:

- **Use .TAP for standard software**. It is smaller, simpler, and universally supported.
- **Use .TZX for turbo-loaded software** and for archival preservation.
- **Provide both** when in doubt. Many archives (including World of Spectrum) provide both .TAP and .TZX for software that uses turbo loaders.

---

## §9. Worked Example: A Small .TAP in Hex

This section walks through a complete (small) .TAP file byte by byte, to illustrate the format.

### 9.1 The program

Suppose we have a tiny Z80 program that turns the border red:

```z80
        ORG  #8000
Start:  LD   A, 0x02      ; Border colour 2 (red)
        OUT  (#FE), A     ; Output to port #FE
Loop:   JR   Loop         ; Infinite loop
```

The program assembles to 6 bytes: `3E 02 D3 FE 18 FE`. We want to save it as a Code block with start address `#8000` and filename "RedBordr".

### 9.2 The header block

The header block payload is 19 bytes:

| Offset | Byte | Meaning |
|---|---|---|
| 0 | `#00` | Flag byte (header) |
| 1 | `#03` | Block type (Code) |
| 2 | `#52` | 'R' |
| 3 | `#65` | 'e' |
| 4 | `#64` | 'd' |
| 5 | `#42` | 'B' |
| 6 | `#6F` | 'o' |
| 7 | `#72` | 'r' |
| 8 | `#64` | 'd' |
| 9 | `#72` | 'r' |
| 10 | `#20` | ' ' (space padding) |
| 11 | `#20` | ' ' (space padding) |
| 12 | `#06` | Data length low byte (6) |
| 13 | `#00` | Data length high byte (0) |
| 14 | `#00` | Parameter 1 low byte (start address `#8000` → low byte `#00`) |
| 15 | `#80` | Parameter 1 high byte (`#80`) |
| 16 | `#00` | Parameter 2 low byte (`#8000` → `#00`) |
| 17 | `#80` | Parameter 2 high byte (`#80`) |
| 18 | `#??` | Checksum (XOR of bytes 0–17) |

Let's compute the checksum step by step:

```
#00 XOR #03 = #03
#03 XOR #52 = #51
#51 XOR #65 = #34
#34 XOR #64 = #50
#50 XOR #42 = #12
#12 XOR #6F = #7D
#7D XOR #72 = #0F
#0F XOR #64 = #6B
#6B XOR #72 = #19
#19 XOR #20 = #39
#39 XOR #20 = #19
#19 XOR #06 = #1F
#1F XOR #00 = #1F
#1F XOR #00 = #1F
#1F XOR #80 = #9F
#9F XOR #00 = #9F
#9F XOR #80 = #1F
```

So the header checksum is `#1F`.

### 9.3 The data block

The data block payload is 8 bytes: 1 flag byte + 6 program bytes + 1 checksum byte.

| Offset | Byte | Meaning |
|---|---|---|
| 0 | `#FF` | Flag byte (data) |
| 1 | `#3E` | First program byte (`LD A, n` opcode) |
| 2 | `#02` | Second program byte (immediate value `#02`) |
| 3 | `#D3` | Third program byte (`OUT (n), A` opcode) |
| 4 | `#FE` | Fourth program byte (port `#FE`) |
| 5 | `#18` | Fifth program byte (`JR n` opcode) |
| 6 | `#FE` | Sixth program byte (displacement `-2`, encoding `JR Loop`) |
| 7 | `#??` | Checksum (XOR of bytes 0–6) |

The checksum is `#FF XOR #3E XOR #02 XOR #D3 XOR #FE XOR #18 XOR #FE`, computed step by step:

```
#FF XOR #3E = #C1
#C1 XOR #02 = #C3
#C3 XOR #D3 = #10
#10 XOR #FE = #EE
#EE XOR #18 = #F6
#F6 XOR #FE = #08
```

So the data block checksum is `#08`.

### 9.4 The complete .TAP file

The complete .TAP file is:

```
Offset 0x00: 13 00                              <- Block 1 length: 0x0013 = 19 bytes
Offset 0x02: 00 03 52 65 64 42 6F 72 64 72     <- Flag + block type + "RedBordr"
Offset 0x0C: 20 20 06 00 00 80 00 80 1F         <- "  " + data len 6 + start addr + params + checksum
Offset 0x15: 08 00                              <- Block 2 length: 0x0008 = 8 bytes
Offset 0x17: FF 3E 02 D3 FE 18 FE 08            <- Flag + 6 program bytes + checksum
```

Total file size: 2 + 19 + 2 + 8 = 31 bytes.

This 31-byte .TAP file can be loaded by any Spectrum emulator with `LOAD "" CODE`. The emulator will load the 6-byte program into memory at `#8000`, then return to the BASIC prompt. The user can then run the program with `RANDOMIZE USR 32768` (which is `#8000` in decimal) to see the border turn red.

### 9.5 Verifying the file

You can verify the checksums yourself:

- **Block 1**: XOR of all 19 bytes in the block (flag + 17 header bytes + checksum) should be `#00`.
- **Block 2**: XOR of all 8 bytes in the block (flag + 6 data bytes + checksum) should be `#00`.

For block 1: `#00 XOR ... XOR #1F` (all header bytes including the `#1F` checksum) `= #1F XOR #1F = #00`. ✓
For block 2: `#FF XOR ... XOR #08` (all data bytes including the `#08` checksum) `= #08 XOR #08 = #00`. ✓

Both checksums verify correctly, confirming that the .TAP file is well-formed.

---

## §10. Cross-References

### 10.1 The rest of the tape series

- [tape_interface.md](tape_interface.md) — the hardware layer: EAR/MIC circuits, ULA, port `#FE`, bit-banging, pilot tone, sync pulses, bit timings.
- [tape_format.md](tape_format.md) — the logical data format: blocks, headers, block types, checksums. The .TAP format is a direct representation of this format.
- [tzx_format.md](tzx_format.md) — the more capable tape file format. Preserves non-standard blocks, turbo loaders, and custom timings. The format of choice for preservation.
- [csw_format.md](csw_format.md) — the Compressed Square Wave format. A lower-level representation that captures the raw signal.
- [pzx_format.md](pzx_format.md) — an alternative pulse-based format.

### 10.2 The snapshot formats

These live in the sibling [../snapshots/](../snapshots/README.md) directory.

- [sna_format.md](../snapshots/sna_format.md) — the .SNA snapshot format. Snapshots capture the machine state at a single instant; .TAP files capture the loading process.
- [z80_format.md](../snapshots/z80_format.md) — the .Z80 snapshot format.
- [szx_format.md](../snapshots/szx_format.md) — the .SZX snapshot format.
- [rzx_format.md](../snapshots/rzx_format.md) — the .RZX replay format.

### 10.3 Related topics

- [Reverse engineering](../../08_reverse_engineering/) — many Spectrum reverse engineering projects begin with analysing a .TAP file to extract the loader and the protected code.
- [Demoscene](../../07_demoscene/) — demos often use custom loaders that push the boundaries of the .TAP format.
- [BASIC interpreter internals](../../04_operating_systems/) — the BASIC interpreter handles the `LOAD`, `SAVE`, `MERGE`, `VERIFY` commands that read and write .TAP-compatible blocks.

### 10.4 External resources

- **World of Spectrum** — the largest archive of .TAP files for Spectrum software.
- **The .TAP specification** — the canonical document for the .TAP format (very short, given the format's simplicity).
- **TZX Tools** — a command-line toolkit for converting between tape formats, including .TAP and .TZX.
- **Fuse emulator** — a reference implementation that can read, write, and play back .TAP files.

### 10.5 Where to go next

After understanding the .TAP format, the natural next step is the more capable **.TZX format** (see [tzx_format.md](tzx_format.md)). .TZX extends .TAP with support for non-standard blocks, turbo loaders, and custom timings, making it the format of choice for preservation.

If you are interested in writing your own .TAP-related tools (generators, players, converters), the format is simple enough to implement in a few hours. Start with the `tap_read_block` and `tap_write_block` functions in §3, and extend from there.

If you are interested in how emulators achieve instant load times, study the "warp playback" mechanism in §6.7 — this is how modern emulators make .TAP files load in milliseconds rather than minutes.

---

## License

This article is licensed under the **Creative Commons Attribution-ShareAlike 4.0 International License** (CC BY-SA 4.0). You are free to share and adapt this material, provided you credit the original source and license your contributions under the same terms.

For the canonical text of the license, see https://creativecommons.org/licenses/by-sa/4.0/.
