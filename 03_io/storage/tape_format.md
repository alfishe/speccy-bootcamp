[← Home](../../README.md) · [I/O](../) · [Storage](README.md)

# The Tape Data Format (Blocks, Headers, Checksums)

The [tape interface hardware](tape_interface.md) defines how individual bits are transmitted over the EAR/MIC jacks — the pilot tone, sync pulses, and bit-level encoding. But the hardware layer doesn't answer the questions: what does a complete "program" look like on tape? How does the loader know whether it's loading a BASIC program, an array, or a screen dump? How is the filename stored? How does the loader know when the data is complete and correct?

The answers are at the **logical data format** layer — the layer above the bits. The Spectrum's tape format defines a small set of **block types**, each with a specific structure: a **header block** (carrying the filename and metadata) followed by one or more **data blocks** (carrying the actual bytes). Every block ends with a checksum. Together, these conventions form the protocol that the ROM's `LOAD` and `SAVE` commands understand.

This article covers the logical data format: the block structure, the header types, the data blocks, the checksum, the multi-block file conventions, and the quirks. For the hardware layer (how bits become bytes), see [tape_interface.md](tape_interface.md). For the modern file formats that represent tapes (.TAP, .TZX, .CSW, .PZX), see the subsequent articles in this section.

---

## §1. What the Tape Data Format Is

### 1.1 The two-layer model

The Spectrum's tape system has two layers:

| Layer | Concerned with | Article |
|---|---|---|
| **Hardware / physical** | How bits become pulses on the EAR/MIC lines | [tape_interface.md](tape_interface.md) |
| **Logical / data format** | What the bytes mean: filenames, block types, parameters, checksums | This article |

The hardware layer says: "a 0 bit is two pulses of 855 T-states each; a 1 bit is two pulses of 1710 T-states each". The logical layer says: "the first byte of every block is a flag byte (0x00 for headers, 0xFF for data); the next 17 bytes of a header are the filename and parameters; the last byte is a checksum".

A loader (or saver) must implement both layers. The ROM does. Turbo loaders typically implement the hardware layer differently (faster timings) but keep the logical layer unchanged — this is why a turbo-loaded BASIC program still appears in the LOAD "" menu with its correct filename.

### 1.2 History

The logical data format was designed by Sinclair Research for the ZX Spectrum's ROM in 1982. It is essentially unchanged from the ZX81's format, with the addition of a "Code" block type (for arbitrary memory ranges) and the "Screen$" convention (for loading a screen dump directly into display memory).

The format was designed to be:

- **Simple**: the ROM loader is only a few hundred bytes of code; the format had to be decodable with minimal CPU resources.
- **Robust**: the checksum catches most corruption; the pilot tone and sync pulses handle tape stretch and speed variation.
- **Extensible**: the "block type" byte allows for new block types without changing the core format (though in practice, only four types were ever defined).

Commercial software houses extended the format in unofficial ways — turbo loaders, custom block types, compression schemes, multi-load formats. These extensions are not part of the standard format but are preserved by the .TZX file format (see [tzx_format.md](tzx_format.md)).

### 1.3 Scope

The standard tape data format defines:

- **Block**: the atomic unit of tape data. Each block is independent: it has its own pilot tone, sync pulses, data, and checksum. A typical file consists of two blocks (a header and a data block).
- **Flag byte**: the first byte of every block, indicating whether it's a header (`#00`) or a data block (`#FF`).
- **Header block**: a fixed-size (17-byte) block containing the filename, block type, and parameters.
- **Data block**: a variable-size block containing the actual bytes of the program, array, or memory range.
- **Checksum**: the XOR of all bytes in the block (including the flag byte), appended as the final byte.
- **Multi-block files**: sequences of header + data pairs, used for multi-load games and demos.

### 1.4 Why this matters

The logical data format matters because:

- **It is the protocol** that the ROM's `LOAD` and `SAVE` commands understand. Every piece of standard Spectrum software uses this format.
- **It is the basis for the .TAP file format** (see [tap_format.md](tap_format.md)). A .TAP file is essentially a sequence of logical blocks, with the hardware-layer timing stripped out.
- **It defines what the user sees** when they type `LOAD ""` — the filename, the block type, the parameters. This is the user-facing side of the tape system.
- **It is the foundation for custom loaders**. Turbo loaders may change the timing, but they almost always keep the logical format intact, so that the user experience (filenames, block types) is unchanged.

---

## §2. Block Structure

Every block on a standard Spectrum tape has the same top-level structure: a pilot tone, sync pulses, a flag byte, the block data, a checksum byte, and a final pulse. This section covers the block structure at the logical layer.

### 2.1 The anatomy of a block

A complete block consists of:

```
[Pilot tone] [Sync pulses] [Flag byte] [Block data] [Checksum byte] [Final pulse]
                            ←─────── payload ───────→
```

The **payload** (flag byte + block data + checksum byte) is what the loader actually decodes. The pilot tone, sync pulses, and final pulse are at the hardware layer (see [tape_interface.md](tape_interface.md) §4 and §5).

The payload for a header block is **19 bytes**:
- 1 byte: flag byte (`#00`)
- 17 bytes: header data (block type, filename, parameters)
- 1 byte: checksum

The payload for a data block is **variable size**:
- 1 byte: flag byte (`#FF`)
- N bytes: data
- 1 byte: checksum

Where N can range from 0 (an empty data block, rare but valid) to 65535 (the maximum the ROM can handle in a single block; in practice, blocks are typically a few KB).

### 2.2 The flag byte

The first byte of every block is the **flag byte**. It identifies the block type:

| Flag byte value | Block type |
|---|---|
| `#00` | Header block |
| `#FF` | Data block |

The loader reads the flag byte first, then decides how to interpret the rest of the block. For a header block, the next 17 bytes are parsed as a header structure. For a data block, the next N bytes (where N is determined by the preceding header or by the caller) are read as raw data.

The flag byte is included in the checksum, so any corruption of the flag byte will be detected by the checksum verification.

Some custom loaders use other flag byte values to indicate custom block types. For example, a turbo loader might use `#01` for a custom header or `#FE` for a custom data block. The standard ROM loader will reject these blocks (the loader checks for `#00` and `#FF` specifically), but the custom loader can interpret them.

### 2.3 The checksum byte

The last byte of every block is the **checksum**. It is the XOR of all bytes in the payload (flag byte + block data):

```
checksum = flag_byte XOR data[0] XOR data[1] XOR ... XOR data[N-1]
```

The loader computes the same XOR as it reads the block, then compares its computed checksum to the transmitted checksum byte. If they match, the block is accepted; if not, the loader returns "R Tape loading error".

The XOR checksum is simple but effective. It detects:

- **Single-bit flips**: always detected (a single bit flip changes the XOR).
- **Any odd number of bit flips**: always detected.
- **Two bit flips in the same bit position**: not detected (the flips cancel out in the XOR).

For tape loading, where the dominant error source is dropout (missing pulses, which typically corrupt a whole byte), the XOR checksum is sufficient. More sophisticated checksums (CRC) would catch more errors, but the ROM's simple XOR was considered adequate.

### 2.4 The block transfer

When the ROM's `LD-BYTES` routine loads a block, the sequence is:

1. Wait for the pilot tone (a long sequence of ~2168 T-state pulses).
2. Wait for the two sync pulses (667 and 735 T-states).
3. Read the flag byte (8 bits, MSB first).
4. Read the block data (N bytes, where N is specified by the caller).
5. Read the checksum byte.
6. Compute the XOR of all bytes (including the flag byte).
7. Compare the computed XOR to the transmitted checksum.
8. Return success (carry set) or failure (carry clear).

The caller (typically the BASIC interpreter, responding to `LOAD ""`) decides how many data bytes to read, based on the header that preceded the data block. If no header was read (or the header specified a different length), the data block may be truncated or extended, causing a checksum mismatch.

### 2.5 The block as seen by the user

When the user types `LOAD ""` and presses PLAY on the recorder, the sequence is:

1. The ROM loader waits for the pilot tone of the first block (the header).
2. The header's filename is displayed in the lower-left corner of the screen as it is read: e.g., "ManicMiner" (with the program's filename).
3. The loader waits for the pilot tone of the second block (the data).
4. The data is loaded into memory (typically at the program's load address).
5. The checksum is verified.
6. If the load is successful, the program starts (for `LOAD "" CODE` or `LOAD "" SCREEN$`) or the BASIC prompt returns with the program loaded (for `LOAD ""`).

The user-visible parts of this sequence — the loading stripes, the filename display, the start of the program — are all consequences of the block structure described in this article.

---

## §3. Header Blocks

A header block is a fixed-size block (17 bytes of header data, plus the flag byte and checksum) that precedes a data block. It carries the filename, the block type, and the parameters that the loader needs to know in order to load the data block correctly.

### 3.1 The 17-byte header structure

The header data (after the flag byte, before the checksum) is exactly 17 bytes:

| Offset (within header) | Size | Field | Notes |
|---|---|---|---|
| 0 | 1 | Block type | 0=Program, 1=Number Array, 2=Character Array, 3=Code |
| 1 | 10 | Filename | 10 characters, padded with spaces (`#20`). No null terminator |
| 11 | 2 | Data length | Length of the following data block, in bytes (little-endian) |
| 13 | 2 | Parameter 1 | Interpretation depends on block type — see §4 |
| 15 | 2 | Parameter 2 | Interpretation depends on block type — see §4 |

So the full payload of a header block is **19 bytes**:

| Offset (within payload) | Size | Field |
|---|---|---|
| 0 | 1 | Flag byte (`#00`) |
| 1 | 1 | Block type |
| 2 | 10 | Filename |
| 12 | 2 | Data length |
| 14 | 2 | Parameter 1 |
| 16 | 2 | Parameter 2 |
| 18 | 1 | Checksum |

All multi-byte fields are **little-endian** (low byte first, then high byte), the standard Z80 convention.

### 3.2 The filename

The filename is **10 characters**, padded with spaces (`#20`). For example, the filename "ManicMiner" is stored as the 10 bytes `M`, `a`, `n`, `i`, `c`, `M`, `i`, `n`, `e`, `r`. The filename "Jetpac" is stored as `J`, `e`, `t`, `p`, `a`, `c`, ` `, ` `, ` `, ` ` (6 characters + 4 spaces).

There is **no null terminator**. The loader always reads exactly 10 bytes for the filename. A filename longer than 10 characters cannot be represented (the ROM truncates to 10 when saving).

When the user types `LOAD "name"`, the BASIC interpreter matches the requested name against the filename in the header. The match is case-sensitive. The wildcard `""` (empty string) matches any filename — this is the famous `LOAD ""` command that loads the next block regardless of filename.

Filenames can contain any character except the quote character (`"`) and some control characters. In practice, most filenames are alphanumeric.

### 3.3 The data length field

The **data length** field (bytes 11–12 of the header) gives the length of the following data block, in bytes. This is the number of bytes the loader should read after the data block's flag byte.

For example, if the data length is `#00 0x40` (little-endian for 16384 = 0x4000), the data block's payload is 16384 bytes of data + 1 flag byte + 1 checksum byte = 16386 bytes total.

The data length is a 16-bit value, so the maximum block size is 65535 bytes. In practice, blocks are typically a few KB; the ROM itself loads data in 256-byte chunks for its own purposes, but the data block can be any size.

### 3.4 Parameter 1 and Parameter 2

The interpretation of **Parameter 1** (bytes 13–14) and **Parameter 2** (bytes 15–16) depends on the block type:

| Block type | Parameter 1 | Parameter 2 |
|---|---|---|
| Program (0) | Auto-run line number. If `≥ #8000`, the program does not auto-run; the BASIC prompt returns after loading. Otherwise, the program auto-runs from this line number. | Length of the BASIC program area (in bytes). The variables are stored after the program and occupy `data_length - parameter_2` bytes. |
| Number Array (1) | (Unused — typically `#00 0x00` or the variable name with high bit set, e.g., `#61 0x80` for array `a`) | (Unused) |
| Character Array (2) | (Unused — typically `#00 0x00` or the variable name with high bit set, e.g., `#61 0x80` for array `a$`) | (Unused) |
| Code (3) | Start address (the address in memory where the data should be loaded) | `#80 0x00` (`#8000`) — a sentinel value indicating "no parameter 2". Often just `#00 0x00` in practice. |

For the **Program** block type, the auto-run line number is checked against the value `#8000` (32768). If the parameter is less than `#8000`, the program auto-runs from that line. If the parameter is `#8000` or greater, the program does not auto-run; the BASIC prompt returns after loading.

The convention of "auto-run line number ≥ #8000 means no auto-run" is a hack: real BASIC line numbers are never that high (the maximum is 9999), so the range `#8000`–`#FFFF` can be used as a sentinel.

### 3.5 The header in hex

A complete header block for a program named "Test" (auto-run from line 10) with a data length of 100 bytes (where 80 bytes are the BASIC program and 20 bytes are variables) would be:

```
Flag byte:        00
Block type:       00                         (Program)
Filename:         54 65 73 74 20 20 20 20 20 20   ("Test" + 6 spaces)
Data length:      64 00                       (100 bytes, little-endian)
Parameter 1:      0A 00                       (line 10, auto-run)
Parameter 2:      50 00                       (80 bytes of BASIC program)
Checksum:         ??                          (XOR of all the above)
```

The checksum is the XOR of all 18 bytes before it (flag + 17 header bytes). The exact value depends on the XOR of the filename and parameters.

### 3.6 Reading the header

The ROM's `LOAD ""` command reads the first block as a header (it expects 17 bytes after the flag byte). It then displays the filename in the bottom-left corner of the screen — this is the famous "Program: Test" line that appears during loading.

After reading the header, the ROM decides what to do next based on the block type:

- **Program**: prepare to load the data block into the BASIC program area (at `PROG`, typically around `#5CB3` after a NEW command).
- **Number Array / Character Array**: prepare to load the data block into the variables area.
- **Code**: prepare to load the data block into the address specified by Parameter 1.

The ROM then reads the next block (the data block) and loads it into the prepared location.

---

## §4. Block Types

The header's **block type** byte (offset 0 of the header data) determines what kind of data the block contains. The standard format defines four block types.

### 4.1 Block type 0: Program

A **Program** block contains a BASIC program (with or without variables). When loaded, the program is placed in the BASIC program area (starting at `PROG`, which is typically `#5CB3` after a NEW command).

The data block's contents are:

1. The **BASIC program** (a sequence of program lines, each with a line number, length, and tokenised statement).
2. (Optionally) The **variables area** (a sequence of variables, each with a name and value).

Parameter 2 in the header specifies the length of the BASIC program (so the loader knows where the program ends and the variables begin).

After loading, if Parameter 1 (auto-run line number) is less than `#8000`, the program auto-runs from that line. Otherwise, the BASIC prompt returns.

The `SAVE "name" LINE n` command produces a Program block with auto-run line `n`. The `SAVE "name"` command (without `LINE`) produces a Program block with auto-run line `#8000` (no auto-run).

### 4.2 Block type 1: Number Array

A **Number Array** block contains a numeric array variable (e.g., `DIM a(10)`). When loaded, the array is placed in the variables area.

The data block's contents are the array's numeric values, stored in the Spectrum's 5-byte floating-point format. The array name is encoded in the header's Parameter 1 (with the high bit of the first byte set — e.g., `#E1` for array `a`).

Number Array blocks are typically produced by `SAVE "name" DATA a()`. They are rarely used in practice (most software uses Code blocks for data), but the format supports them for completeness.

### 4.3 Block type 2: Character Array

A **Character Array** block contains a string array variable (e.g., `DIM a$(10)`). When loaded, the array is placed in the variables area.

The data block's contents are the array's string values, stored as sequences of characters. The array name is encoded in the header's Parameter 1 (with the high bit of the first byte set, plus bit 5 set for string arrays — e.g., `#E1` for `a$`).

Character Array blocks are produced by `SAVE "name" DATA a$()`. Like Number Array blocks, they are rarely used in commercial software.

### 4.4 Block type 3: Code

A **Code** block contains an arbitrary sequence of bytes to be loaded at a specified memory address. When loaded, the bytes are placed at the address specified by Parameter 1 (the start address).

The data block's contents are the raw bytes — no interpretation, no framing. The loader simply copies the bytes from the tape to the specified memory range.

Code blocks are the most common block type for machine code programs, screen dumps, and binary data. They are produced by:

- `SAVE "name" CODE start, length` — saves `length` bytes starting at address `start`.
- `SAVE "name" SCREEN$` — saves the screen memory (6912 bytes at `#4000`–`#5AFF`). This is equivalent to `SAVE "name" CODE 16384, 6912`.

The `LOAD "" CODE` command loads a Code block into the address specified by Parameter 1. The `LOAD "" CODE addr` command loads a Code block into the specified address (overriding the header's Parameter 1). The `LOAD "" SCREEN$` command loads a Code block directly into screen memory (regardless of the header's Parameter 1).

### 4.5 Comparison of block types

| Block type | What it contains | Typical use | Produced by |
|---|---|---|---|
| Program (0) | BASIC program + variables | BASIC programs | `SAVE "name"`, `SAVE "name" LINE n` |
| Number Array (1) | Numeric array | Numeric data | `SAVE "name" DATA a()` |
| Character Array (2) | String array | String data | `SAVE "name" DATA a$()` |
| Code (3) | Raw bytes | Machine code, screen dumps, binary data | `SAVE "name" CODE start, length`, `SAVE "name" SCREEN$` |

For commercial software, **Code blocks** are by far the most common. Almost every machine code program is distributed as a Code block (often with the start address pointing to `#5CB3` or another location where the program then takes over). BASIC programs are typically distributed as Program blocks.

### 4.6 Non-standard block types

Some custom loaders use non-standard block types (e.g., 4, 5, or values above 3). These are not part of the standard format and will be rejected by the ROM's `LOAD` command. However, the .TZX file format (see [tzx_format.md](tzx_format.md)) preserves the original block type byte, so emulators can recognise and document these non-standard blocks even if they don't interpret them.

For example, the Speedlock turbo loader uses a custom block type to identify its custom-encoded data blocks. The block type is preserved in the .TZX file, even though the ROM would reject it.

---

## §5. Data Blocks

A **data block** contains the actual bytes of a program, array, or memory range. It follows a header block (which specifies the data length and other parameters).

### 5.1 The data block structure

A data block's payload is:

| Offset (within payload) | Size | Field |
|---|---|---|
| 0 | 1 | Flag byte (`#FF`) |
| 1 | N | Data bytes |
| N+1 | 1 | Checksum |

Where N is the data length specified in the preceding header block.

The loader reads the flag byte (`#FF`), then reads N data bytes (where N is determined by the preceding header's data length field), then reads the checksum byte and verifies it.

### 5.2 The data length

The data length is specified in the preceding header block (bytes 11–12 of the header data). The loader uses this value to know how many bytes to read.

For a Code block, the data length is the number of bytes to load into memory. For a Program block, the data length is the total size of the BASIC program plus the variables. For an array block, the data length is the size of the array data.

### 5.3 Loading the data

After reading the header and determining the data length and destination address, the loader reads the data block byte by byte and stores each byte at the destination address:

```
address = destination_from_header
for i in 0 .. data_length-1:
    byte = read_byte_from_tape()
    memory[address + i] = byte
    checksum ^= byte
transmitted_checksum = read_byte_from_tape()
if checksum != transmitted_checksum:
    error()
```

The destination address depends on the block type:

- **Program**: `PROG` (the start of the BASIC program area, typically `#5CB3` after NEW).
- **Number Array / Character Array**: the end of the variables area.
- **Code**: the address specified by Parameter 1 in the header.

### 5.4 Empty data blocks

An empty data block (data length 0) is technically valid. It consists of just the flag byte (`#FF`) and the checksum (which equals `#FF` since the flag byte is the only byte in the checksum). Empty data blocks are rare but can be used as markers or sentinels in multi-block files.

### 5.5 Large data blocks

The maximum data length is 65535 bytes (the maximum value of a 16-bit field). In practice, data blocks are typically a few KB. The ROM has no problem loading large blocks, but the longer the block, the more likely a tape error will occur somewhere within it.

For very large programs (e.g., a 48K snapshot), the data is typically split into multiple blocks (see §6) rather than loaded as a single 49152-byte block. This reduces the impact of tape errors — a single block failure only requires re-loading that block, not the entire program.

### 5.6 The Screen$ convention

A common use of Code blocks is to load a screen dump directly into display memory. The screen memory occupies addresses `#4000`–`#5AFF` (6912 bytes: 6144 bytes of pixel data + 768 bytes of attribute data). A Code block with start address `#4000` and data length 6912 will load the screen.

The BASIC `SAVE "name" SCREEN$` command produces exactly this: a Code block with start `#4000` and length 6912. The `LOAD "" SCREEN$` command loads such a block into screen memory.

Many games use this convention to display a loading screen while the rest of the program loads. The sequence is:

1. Load a Code block containing the loading screen (into `#4000`–`#5AFF`).
2. Load a Code block containing the game itself.

The loading screen appears instantly after the first block, giving the user visual feedback while the rest of the program loads.

---

## §6. Multi-Block Files

A standard file consists of two blocks: a header followed by a data block. But many files have more than two blocks — they are **multi-block files**. This section covers the multi-block conventions.

### 6.1 The standard 2-block file

The simplest file is the **2-block file**: a header block followed by a data block. This is the format produced by `SAVE "name"`, `SAVE "name" LINE n`, `SAVE "name" CODE start, length`, and similar commands.

On tape, the two blocks are separated by a **short gap** of silence (typically about 1 second). This gap gives the loader time to process the header and prepare for the data block. The gap is not encoded in any way — it is simply a period of silence on the tape.

```
[Header block] [~1 second gap] [Data block]
```

The ROM loader handles this automatically: after reading the header, it returns to its caller (the BASIC interpreter), which then issues a second call to load the data block. The loader waits for the next pilot tone (which comes after the gap).

### 6.2 Multi-block files

A file can have more than one header+data pair. For example, a file containing a BASIC program and a separate screen dump might consist of:

```
[Program header] [gap] [Program data] [gap] [Code header] [gap] [Code data]
```

The ROM's `LOAD ""` command loads only the first program it encounters. To load subsequent blocks, the program (or the user) must issue additional `LOAD` commands. For example:

```basic
LOAD ""              : REM Loads the BASIC program
LOAD "" CODE         : REM Loads the screen dump
```

Each `LOAD ""` command waits for the next block on the tape and loads it. The user must press PLAY on the recorder before each `LOAD` (or keep PLAY pressed throughout, and the loader will skip past the intermediate blocks until it finds one of the requested type).

### 6.3 Multi-load games

Many games, especially later ones, use a **multi-load** format: the initial load brings in a small loader program, which then loads additional data (levels, graphics, music) on demand as the player progresses through the game.

The typical sequence:

1. The user types `LOAD ""` (or presses a key on the loader screen).
2. The ROM loads the first block: a short machine code loader.
3. The loader takes over and displays a title screen.
4. When the user starts the game, the loader loads the first level's data from tape.
5. As the player completes levels, the loader loads subsequent level data.

This requires the user to keep the tape running (or to manually advance it to the correct position when prompted). Some multi-load games display messages like "Rewind to start of side B" or "Press PLAY when prompted".

The multi-load format is supported by the standard block structure — each level is just another Code block, loaded on demand by the loader program. The .TAP and .TZX file formats preserve multi-load files as sequences of blocks.

### 6.4 The 128K multi-load pattern

The 128K Spectrum, with its banked memory, enabled a different multi-load pattern: **load all data into the various RAM banks at the start, then switch between banks during gameplay**. This eliminated the need to load data during gameplay (which interrupted the experience with loading screens).

The typical 128K pattern:

1. The loader loads data into multiple RAM banks (e.g., graphics into bank 5, music into bank 6, level data into bank 7).
2. During gameplay, the program switches banks as needed (via port `#7FFD`), accessing the pre-loaded data.

This pattern required more careful programming (the loader had to manage the bank switching), but it gave a much better user experience (no in-game loading pauses). It was used by many late-era 128K games.

### 6.5 Gaps between blocks

The gap between blocks is not strictly standardised. The ROM produces a gap of about 1 second when saving, but commercial tape duplication equipment might produce shorter or longer gaps. As long as the gap is at least ~0.5 seconds (enough for the loader to reset and start looking for the next pilot tone), the loader will work.

Some turbo loaders use very short gaps (~0.1 seconds) to speed up loading. This requires the loader to be very fast at resetting after each block, but it can shave seconds off the total load time.

Conversely, some commercial tapes have very long gaps (10+ seconds) between the loader program and the main game data, to give the user time to read the loading instructions or to ensure the tape is positioned correctly.

### 6.6 Tape side structure

A typical commercial cassette has:

- **Side A**: The loader program (a short block) followed by the main game data (a larger block or blocks).
- **Side B**: Often a duplicate of side A (for reliability — if one side fails to load, try the other), or a different version (e.g., 48K vs 128K versions of the game).

The .TAP and .TZX file formats do not explicitly represent tape sides — each file represents one continuous tape (typically one side). To represent a full cassette, two files are used (one per side).

---

## §7. The Checksum

The checksum is the **XOR of all bytes in the block** (including the flag byte, excluding the checksum byte itself). This section covers the checksum in detail.

### 7.1 Why XOR?

The XOR checksum was chosen for several reasons:

1. **Simplicity**: XOR is a single Z80 instruction (`XOR B` or `XOR (HL)`). Computing the checksum is extremely cheap.
2. **Symmetry**: The same operation computes and verifies the checksum. The loader XORs each incoming byte into a running total; if the final total matches the transmitted checksum, the block is valid.
3. **Order independence**: XOR is commutative and associative — the order of the bytes does not matter. This means the loader does not need to keep track of byte positions.
4. **Sufficient error detection**: For the dominant error source on tape (dropout, which typically corrupts one or more bytes), the XOR checksum catches most errors.

### 7.2 Mathematical properties

The XOR checksum has the following properties:

- It detects any **single-byte corruption** (any number of bit flips within one byte).
- It detects any corruption where the total number of flipped bits across all bytes is **odd**.
- It does NOT detect corruption where the total number of flipped bits across all bytes is **even** (e.g., flipping one bit in byte 0 and the same bit in byte 5).

For random multi-byte corruption, the XOR checksum detects about 99.6% of errors (1 in 256 false negatives). This is adequate for tape loading, where the dominant error mode is single-byte dropout.

### 7.3 Limitations

The XOR checksum has known limitations:

- **No error correction**: the checksum detects errors but cannot correct them. If the checksum fails, the loader must re-load the entire block (or report an error).
- **No positional information**: the checksum does not tell the loader which byte is corrupt. Even if the loader knew which byte was bad, it could not reconstruct it from the checksum.
- **Vulnerable to swap errors**: if two bytes are swapped, the XOR checksum is unchanged.

More sophisticated checksums (CRC-8, CRC-16) address these limitations but were not used by the ROM (they require more code and more CPU time). Some turbo loaders use CRC-16 for better error detection; the .TZX format (see [tzx_format.md](tzx_format.md)) can represent both XOR and CRC checksums.

### 7.4 The checksum byte in practice

When the ROM loads a block, it:

1. Initialises a checksum accumulator to 0.
2. XORs each incoming byte (including the flag byte) into the accumulator.
3. Reads the final checksum byte.
4. Compares the accumulator to the checksum byte.
5. If they match, the block is valid; if not, "R Tape loading error".

The comparison is done with `CP (HL)` (or similar), which sets the Z flag if the values are equal. The loader returns success (carry set) or failure (carry clear) based on this comparison.

### 7.5 The "verify" mode

The ROM's `VERIFY` command (as in `VERIFY "name"`) works like `LOAD`, but instead of storing the incoming bytes in memory, it compares them to the bytes already in memory. This is used to check that a tape was saved correctly: after `SAVE "name"`, the user can `VERIFY "name"` to confirm that the tape data matches the memory data.

The verify mode uses the same block structure and checksum as the load mode. The only difference is that the loader compares each incoming byte to the corresponding byte in memory, instead of overwriting the memory byte.

---

## §8. Compatibility and Quirks

### 8.1 Non-standard blocks

The standard format defines only two flag byte values (`#00` for header, `#FF` for data) and only four block types (Program, Number Array, Character Array, Code). Commercial software, especially turbo loaders, often deviates from this standard:

- **Custom flag bytes**: Some loaders use `#01`, `#FE`, or other values for their blocks. The ROM rejects these; the custom loader interprets them.
- **Custom block types**: Some loaders use block type values above 3 for custom block categories.
- **Headerless blocks**: Some loaders skip the header block entirely, loading only data blocks. The loader program knows the data length and destination address from its own code, not from a header.
- **Custom data lengths**: Some loaders use 24-bit or 32-bit data lengths (the standard is 16-bit).

These non-standard blocks cannot be loaded by the ROM's `LOAD` command. They are typically loaded by a custom loader program (which is itself loaded as a standard Code block first).

The .TAP file format (see [tap_format.md](tap_format.md)) can represent non-standard blocks by storing them as raw data without a header. The .TZX file format (see [tzx_format.md](tzx_format.md)) can represent non-standard blocks more faithfully, preserving the custom timings and encodings.

### 8.2 Mismatched lengths

If the header's data length field does not match the actual data block length, the loader will produce a checksum error (because it will read either too few or too many bytes, and the XOR will not match).

This can happen if:

- The tape is truncated (the data block is cut short).
- The tape has extra data appended (the data block is longer than the header specifies).
- A custom loader uses a non-standard data length encoding.

The ROM's loader cannot recover from a mismatched length — it will fail with "R Tape loading error". A custom loader with more sophisticated error recovery might be able to re-read the block or skip to the next one.

### 8.3 Filename matching

The ROM's `LOAD "name"` command matches the requested filename against the header's filename byte by byte. The match is case-sensitive and exact (the filenames must be the same length, since both are padded to 10 characters).

The `LOAD ""` command uses the empty string as a wildcard: it matches any filename. The loader reads the first block on the tape regardless of its filename.

Some users discovered that `LOAD "x"` (where `x` is any single character) would load the next block if its filename started with `x`. This is because the ROM's filename matching is actually a prefix match when the requested name is shorter than 10 characters. This is not a documented feature, but it works.

### 8.4 The auto-run line sentinel

The Program block's auto-run line number (Parameter 1 in the header) uses a sentinel value to indicate "no auto-run": any value `≥ #8000` means "do not auto-run". This works because real BASIC line numbers are in the range 1–9999, well below `#8000` (32768).

The `SAVE "name" LINE n` command sets the auto-run line to `n` (which must be a valid line number, 1 ≤ n ≤ 9999). The `SAVE "name"` command (without `LINE`) sets the auto-run line to `#8000` (no auto-run).

Some programs exploit the sentinel value: by setting the auto-run line to `#FFFF` (65535), they can signal to a custom loader that the block should be treated specially (e.g., not auto-run even after a `LOAD "" LINE 0` command).

### 8.5 The `MERGE` command

The `MERGE "name"` command works like `LOAD "name"`, but instead of replacing the existing BASIC program, it merges the loaded program lines into the existing program. If a loaded line has the same line number as an existing line, the loaded line replaces the existing line.

`MERGE` is implemented at the BASIC interpreter level (not at the tape format level). The tape format for a `MERGE` is identical to the tape format for a `LOAD` — the difference is purely in how the loaded data is processed.

### 8.6 Header-only loads

Some software does not need the full data block — only the header. For example, a directory-listing program might read all the headers on a tape without reading the data blocks, displaying a list of filenames.

The ROM does not directly support header-only loads, but a custom loader can easily implement it: just call the `LD-BYTES` routine for the header, then skip past the data block (by waiting for the next pilot tone).

### 8.7 The "Stop the tape" prompt

After loading a multi-block file, the ROM displays a message like "Start tape, then press any key" or "Stop the tape" to prompt the user. This is handled by the BASIC interpreter (not the tape format itself), but it affects how multi-block files are structured on tape: there must be a gap between blocks long enough for the user to respond.

For automated loading (e.g., from an emulator or a modern tape interface), this prompt is often skipped or auto-confirmed. The .TAP and .TZX file formats do not encode the prompt — it is purely a runtime behaviour.

### 8.8 Custom checksums

Some turbo loaders use a **CRC-16** checksum instead of (or in addition to) the XOR checksum. CRC-16 catches more errors than XOR, including some swap errors. The CRC is computed over the data bytes (typically not including the flag byte) and stored as two bytes at the end of the block.

The ROM loader does not understand CRC-16 — it will reject blocks that use it. Custom loaders, of course, understand their own CRCs. The .TZX format can represent blocks with custom checksums.

---

## §9. Comparison with Other Formats

The Spectrum's logical data format (header + data blocks with an XOR checksum) is one of several formats used by 1980s home computers. This section compares it to its contemporaries.

### 9.1 Commodore 64 (PRG / T64)

The Commodore 64 used a different tape format, designed for the Commodore 1530 Datasette. The format consists of:

- A **header** (192 bytes) containing the program type, the start address, the end address, and the filename.
- A **data block** containing the program bytes.

The C64 format uses a **CRC checksum** (more sophisticated than XOR) and a more elaborate block structure that supports multiple programs on a single tape.

The C64's `PRG` file format (used on disk) is even simpler: a 2-byte start address followed by the program bytes, with no header block, no filename, and no checksum (the disk's own filesystem provides integrity checking).

The `T64` file format (used by emulators to represent C64 tapes) wraps the C64 tape format in a modern file container, similar to how .TAP wraps the Spectrum tape format.

### 9.2 Amstrad CPC

The Amstrad CPC's tape format is very similar to the Spectrum's: a header block followed by a data block, with an XOR checksum. The CPC format uses a slightly different header structure (24 bytes instead of 17), supporting longer filenames and additional metadata.

The CPC format also supports multiple blocks per file (like the Spectrum's multi-block format), and the AMSDOS operating system provides built-in commands for loading and saving.

### 9.3 MSX

The MSX standard uses the **Kansas City Standard** (KCS) tape format, which is more sophisticated than the Spectrum's format. KCS uses a different physical encoding (1200 Hz for a 0, 2400 Hz for a 1) and a more elaborate block structure with a header, a data block, and a CRC checksum.

KCS was designed for interoperability: any KCS-compliant computer can load tapes from any other KCS-compliant computer. In practice, this interoperability was rarely used (different computers used different file formats on top of KCS), but the standard existed.

### 9.4 BBC Micro

The BBC Micro's tape format uses the **Acorn Cassette Filing System** (CFS), which is more sophisticated than the Spectrum's format. CFS uses:

- A **header block** (256 bytes) with the filename, load address, execution address, and a CRC checksum.
- A **data block** (up to 256 bytes per block) with the data and a CRC checksum.
- **Inter-block gaps** for the filing system to process each block.

CFS supports filenames up to 10 characters, multiple files per tape, and random access (the filing system can seek to a specific file on the tape). It is closer to a tape-based filesystem than the Spectrum's simple block format.

### 9.5 Comparison table

| Feature | Spectrum | C64 | Amstrad CPC | MSX | BBC Micro |
|---|---|---|---|---|---|
| Header block | 17 bytes | 192 bytes | 24 bytes | varies | 256 bytes |
| Data block size | Variable (up to 64K) | Variable | Variable | Variable | 256 bytes per block |
| Checksum | XOR | CRC | XOR | CRC | CRC |
| Multi-file tapes | Yes (multi-block) | Yes (native) | Yes (native) | Yes (native) | Yes (native, with directory) |
| Random access | No | No | No | No | Yes |
| Filename length | 10 chars | 16 chars | 12 chars | 6–8 chars | 10 chars |

The Spectrum's format is among the simplest of the major home computer formats. Its simplicity made it easy to implement in the ROM (only a few hundred bytes of code) and easy to extend with custom loaders. But it lacks the sophistication of the C64, BBC Micro, or MSX formats — no random access, no native multi-file support, and a weaker checksum.

### 9.6 Why the Spectrum's format won (for Spectrum software)

Despite its simplicity, the Spectrum's format was sufficient for the vast majority of Spectrum software. The reasons:

- **Tape was sequential anyway**: random access was not particularly useful for loading a single program.
- **Custom loaders filled the gaps**: where the standard format was insufficient (e.g., for multi-load games), software houses developed custom loaders that met their needs.
- **The .TAP and .TZX file formats** (see [tap_format.md](tap_format.md) and [tzx_format.md](tzx_format.md)) preserved the format faithfully for emulation and archival.

Today, the Spectrum's tape format is one of the best-preserved of the 1980s home computer formats, thanks to the .TZX specification's comprehensive coverage of standard and non-standard blocks.

---

## §10. Cross-References

### 10.1 The rest of the tape series

- [tape_interface.md](tape_interface.md) — the hardware layer: EAR/MIC circuits, ULA, port `#FE`, bit-banging, pilot tone, sync pulses, bit timings. The companion to this logical-format article.
- [tap_format.md](tap_format.md) — the simplest tape file format. Represents a tape as a sequence of logical blocks (the format described in this article).
- [tzx_format.md](tzx_format.md) — the most comprehensive tape file format. Preserves non-standard blocks, turbo loaders, and custom timings. The format of choice for preservation.
- [csw_format.md](csw_format.md) — the Compressed Square Wave format. A lower-level representation that captures the raw signal (below the block structure).
- [pzx_format.md](pzx_format.md) — an alternative pulse-based format.

### 10.2 The snapshot formats

These live in the sibling [../snapshots/](../snapshots/README.md) directory.

- [sna_format.md](../snapshots/sna_format.md) — the .SNA snapshot format. Snapshots capture the machine state at a single instant; tape files capture the loading process. The two are complementary.
- [z80_format.md](../snapshots/z80_format.md) — the .Z80 snapshot format.
- [szx_format.md](../snapshots/szx_format.md) — the .SZX snapshot format.
- [rzx_format.md](../snapshots/rzx_format.md) — the .RZX replay format.

### 10.3 Related topics

- [BASIC interpreter internals](../../04_operating_systems/) — the BASIC interpreter handles the `LOAD`, `SAVE`, `MERGE`, `VERIFY` commands that use the tape format described here.
- [Reverse engineering](../../08_reverse_engineering/) — many Spectrum reverse engineering projects begin with analysing a custom tape loader to extract the protected code.
- [Demoscene](../../07_demoscene/) — demos often include custom loaders that push the boundaries of the tape format.

### 10.4 External resources

- **The Spectrum ROM disassembly** — the canonical commented disassembly, including the `LD-BYTES`, `SA-BYTES`, `LD-BLOCK`, and related routines.
- **World of Spectrum** — the largest archive of Spectrum tape images.
- **The .TAP specification** — the canonical document for the .TAP file format, which is based on the logical format described here.
- **The .TZX specification** — the canonical document for the .TZX file format, which extends .TAP with support for non-standard blocks and timings.

### 10.5 Where to go next

After understanding the logical data format, the natural next step is the **file formats** that represent tapes for modern emulators. The simplest is [.TAP](tap_format.md), which is essentially a sequence of logical blocks. The most comprehensive is [.TZX](tzx_format.md), which can represent any tape, including non-standard turbo loaders.

If you are interested in writing your own loader or saver, study the ROM disassembly of `LD-BYTES` (load) at `#0556` and `SA-BYTES` (save) at `#04C6`. These routines implement the format described in this article in a few hundred bytes of Z80 code.

If you are interested in tape preservation, start with [tzx_format.md](tzx_format.md), which is the format used by the major Spectrum archives for faithful preservation of original tapes.

---

## License

This article is licensed under the **Creative Commons Attribution-ShareAlike 4.0 International License** (CC BY-SA 4.0). You are free to share and adapt this material, provided you credit the original source and license your contributions under the same terms.

For the canonical text of the license, see https://creativecommons.org/licenses/by-sa/4.0/.
