[← Home](../../README.md) · [I/O](../) · [Storage](README.md)

# The .TZX File Format

The [.TAP format](tap_format.md) is simple and universal, but it has a fundamental limitation: it can only represent standard ROM blocks. Any tape that uses a turbo loader, custom timings, or non-standard encoding cannot be faithfully stored in a .TAP file. For most commercial Spectrum software — which used turbo loaders throughout the late 1980s — this means .TAP is insufficient.

The **.TZX format** was created in 1996 by **Tomaz Kac** (under the handle "Tomazy") to solve this problem. .TZX is a **comprehensive tape file format** that can represent any Spectrum tape, including turbo loaders, custom encodings, and even non-Spectrum tapes (the format has been extended to support the C64, Amstrad CPC, and other machines). It is the format of choice for **tape preservation**: archives like World of Spectrum use .TZX for their highest-fidelity tape images.

This article covers the .TZX format in detail: its history, the file header, the block structure, the standard block types (including the all-important turbo loader blocks), how to read and write .TZX files, and how it relates to the simpler .TAP format. For the logical data format that .TZX blocks represent, see [tape_format.md](tape_format.md). For the hardware layer, see [tape_interface.md](tape_interface.md).

---

## Roadmap

1. **What the .TZX format is** — history, scope, design philosophy
2. **The file header** — the 10-byte "ZXTape!" header
3. **The block structure** — block ID + length + data
4. **The standard block types** — normal speed, turbo speed, pure tone, pulse sequence, etc.
5. **Turbo loader support** — how .TZX represents turbo loaders
6. **Writing a .TZX file** — generating a .TZX from a program
7. **Reading a .TZX file** — loading a .TZX into an emulator
8. **Compatibility and quirks** — emulator support, version differences
9. **Comparison with .TAP** — when to use which
10. **Cross-references** — where to go next

---

## §1. What the .TZX Format Is

### 1.1 Origins

The .TZX format was created in 1996 by **Tomaz Kac** ("Tomazy"), a Slovenian Spectrum enthusiast. Kac was involved in the **Centerfold Disk Magazine** and the **TR-DOS** preservation scene, and he needed a file format that could faithfully represent the turbo-loaded tapes that were common in the Russian and Eastern European Spectrum scenes.

The existing .TAP format was insufficient: it could not represent the non-standard timings used by Speedlock, Alcatraz, and other turbo loaders. Kac designed .TZX as an extensible, block-based format that could represent any tape signal, down to the individual pulse level.

The format was first documented in the **.TZX Specification v1.0** (1996), which defined a small set of block types covering the most common tape patterns. The specification has been extended several times:

- **v1.0 (1996)**: Initial release. Standard speed block, turbo speed block, pure tone, pulse sequence, pure data, silence, group start/end, text description, message, archive info, hardware type.
- **v1.1 (1997)**: Added the "glue" block (for concatenating .TZX files).
- **v1.2 (1998)**: Added custom info block, and refined the turbo speed block.
- **v1.3 (1999)**: Added the "direct recording" block (for raw signal capture).
- **v1.4–1.8 (2000–2003)**: Minor extensions and clarifications.
- **v1.10–1.13 (2004–2008)**: Added support for non-Spectrum machines (C64, Amstrad CPC, etc.), the "cycle-based" block, and other extensions.

The current version is **v1.13**, although most emulators support v1.10 or later.

### 1.2 Design philosophy

The .TZX format's design philosophy is **"any tape, anywhere, anytime"**:

- **Any tape**: .TZX can represent any Spectrum tape signal, including standard ROM blocks, turbo loaders, custom encodings, and even raw analog captures.
- **Anywhere**: .TZX is machine-independent. The same format can represent Spectrum tapes, C64 tapes, Amstrad CPC tapes, and other machines (via the "hardware type" block).
- **Anytime**: .TZX is extensible. New block types can be added without breaking older loaders (which simply skip unknown blocks).

This philosophy makes .TZX the most capable tape format. The trade-off is complexity: .TZX files are harder to generate and parse than .TAP files, and the specification is much longer.

### 1.3 Scope

A .TZX file contains:

- A **10-byte file header** (magic + version).
- An arbitrary number of **blocks**, each with a block ID, length, and data.

Each block represents a piece of the tape signal: a standard speed block, a turbo speed block, a silence period, a group start, a text description, etc. The player (emulator) reads the blocks in order and generates the corresponding tape signal.

The .TZX format does **not** impose a fixed block ordering. Blocks can appear in any order, although in practice they follow the natural sequence of the tape (pilot, sync, data, gap, pilot, sync, data, ...).

### 1.4 Why .TZX matters

The .TZX format matters because:

- **It is the format of choice for tape preservation**. Archives like World of Spectrum use .TZX for their highest-fidelity tape images.
- **It can represent turbo loaders**, which .TAP cannot. Most commercial Spectrum software from the late 1980s uses turbo loaders, and .TZX is the only way to faithfully preserve these tapes.
- **It is extensible**, allowing new block types to be added without breaking older loaders.
- **It is machine-independent**, allowing it to represent tapes from multiple machines (Spectrum, C64, Amstrad CPC, etc.).
- **It is widely supported** by modern emulators (Fuse, ZEsarUX, SpecEmu, etc.).

---

## §2. The File Header

Every .TZX file begins with a 10-byte header that identifies the format and version.

### 2.1 The header layout

| Offset | Size | Field | Notes |
|---|---|---|---|
| 0 | 7 | Magic | "ZXTape!" (0x5A 0x58 0x54 0x61 0x70 0x65 0x21) — identifies this as a .TZX file |
| 7 | 1 | Major version (binary) | Typically 1 |
| 8 | 1 | Minor version (binary) | Typically 13 (for v1.13) |
| 9 | 1 | File integrity byte | (Deprecated; typically 0) |

If the first 7 bytes are not "ZXTape!", the file is not a .TZX file. Loaders should reject it.

The version fields allow the loader to detect which version of the .TZX specification the file uses. Most modern loaders support v1.10+; some support earlier versions.

### 2.2 Hex view of the header

```
Offset 0x00: 5A 58 54 61 70 65 21 01 0D 00    <- "ZXTape!" + v1.13 + integrity byte
```

The bytes decode as:

- `5A 58 54 61 70 65 21` = "ZXTape!" (ASCII).
- `01` = major version 1.
- `0D` = minor version 13 (hexadecimal 0x0D = decimal 13).
- `00` = integrity byte (deprecated).

### 2.3 Version handling

The loader should check the major and minor version fields:

- If the major version is higher than the loader supports, the file uses a newer .TZX specification with unknown block types. The loader may still attempt to load the file, skipping unknown block types.
- If the minor version is higher than the loader supports, the file may use extensions that the loader does not understand. Again, the loader should skip unknown block types.

The .TZX specification is designed to be forward-compatible: a loader that supports v1.10 can load a v1.13 file, skipping any v1.11+ block types it does not understand.

---

## §3. The Block Structure

After the 10-byte file header, the file consists of a sequence of blocks. Each block has a block ID, length, and data.

### 3.1 The block layout

| Offset (within block) | Size | Field |
|---|---|---|
| 0 | 1 | Block ID |
| 1 | varies | Block data (length and structure depend on the block ID) |

Unlike .TAP (which has a uniform 2-byte length field for every block), .TZX block lengths are determined by the block type. Each block type has a specific structure, and the length is either:

- **Implicit** (fixed-size blocks, where the length is determined by the block type).
- **Explicit** (variable-size blocks, where the length is stored in a field within the block).

This makes .TZX harder to parse than .TAP: the parser must know the structure of each block type to determine where the next block begins.

### 3.2 Reading a block

The C code to read a single .TZX block:

```c
typedef struct {
    uint8_t id;
    void *data;  // Pointer to block-type-specific data
} TzxBlock;

int tzx_read_block(FILE *f, TzxBlock *block) {
    // Read the 1-byte block ID
    if (fread(&block->id, 1, 1, f) != 1) {
        return 0;  // EOF
    }

    // Dispatch based on block ID
    switch (block->id) {
        case 0x10: return tzx_read_block_10(f, block);
        case 0x11: return tzx_read_block_11(f, block);
        case 0x12: return tzx_read_block_12(f, block);
        case 0x13: return tzx_read_block_13(f, block);
        case 0x14: return tzx_read_block_14(f, block);
        case 0x15: return tzx_read_block_15(f, block);
        case 0x20: return tzx_read_block_20(f, block);
        case 0x21: return tzx_read_block_21(f, block);
        case 0x30: return tzx_read_block_30(f, block);
        // ... and so on for each block type ...
        default:
            fprintf(stderr, "Unknown block ID 0x%02X — skipping\n", block->id);
            return tzx_skip_unknown_block(f, block->id);
    }
}
```

### 3.3 Skipping unknown blocks

A key feature of .TZX is that unknown block types can be skipped without aborting the load. This is what makes the format forward-compatible.

However, skipping an unknown block requires knowing its length. The .TZX specification defines a convention for this:

- **Block IDs 0x00–0x7F** (well-known blocks): the length is determined by the block type. If the loader does not recognise the block ID, it cannot determine the length and must abort.
- **Block IDs 0x80–0xFF** (extension blocks): the first 4 bytes after the block ID are a 32-bit length, giving the total size of the block data (not including the 5-byte block header). This allows loaders to skip unknown extension blocks.

In practice, most modern loaders support all well-known block IDs (0x00–0x7F), so the abort case is rare.

### 3.4 The block ID registry

The standard block IDs defined by the .TZX specification:

| Block ID | Name | Description |
|---|---|---|
| `0x10` | Standard speed | A standard ROM block (pilot + sync + data + final pulse) |
| `0x11` | Turbo speed | A turbo loader block with custom timings |
| `0x12` | Pure tone | A sequence of pulses at a fixed frequency |
| `0x13` | Pulse sequence | A sequence of pulses with arbitrary durations |
| `0x14` | Pure data | Raw data with custom bit timings (no pilot/sync) |
| `0x15` | Direct recording | Raw signal sample (every byte = 8 T-states) |
| `0x16` | C64 ROM type | (For C64 tapes) |
| `0x17` | C64 turbo type | (For C64 tapes) |
| `0x20` | Silence | A period of silence |
| `0x21` | Group start | Marks the start of a named group of blocks |
| `0x22` | Group end | Marks the end of a group |
| `0x23` | Jump | Jumps to a specific block index (for loops) |
| `0x24` | Loop | Repeats the following blocks N times |
| `0x25` | Pulse sequence (32-bit) | Like 0x13 but with 32-bit pulse counts |
| `0x26` | BNC data | (Rare) |
| `0x27` | BNC program | (Rare) |
| `0x30` | Text description | A free-text description of the tape |
| `0x31` | Message block | A text message displayed to the user |
| `0x32` | Archive info | Metadata about the archive (publisher, year, etc.) |
| `0x33` | Hardware type | Specifies the machine and ROM type |
| `0x34` | Emulation info | Specifies the emulator that created the file |
| `0x35` | Custom info | Arbitrary key-value metadata |
| `0x40` | Snapshot | An embedded snapshot (rare in .TZX) |
| `0x5A` | Glue block | Used for concatenating .TZX files |
| `0x80+` | Extension blocks | Custom blocks with explicit length (see §3.3) |

The most important block types for Spectrum tapes are:

- **0x10** (standard speed): used for ROM-loaded blocks.
- **0x11** (turbo speed): used for turbo-loaded blocks.
- **0x20** (silence): used for gaps between blocks.
- **0x30** (text description): used for metadata.
- **0x32** (archive info): used for publisher/year information.

### 3.5 A typical .TZX file

A typical .TZX file for a turbo-loaded game might look like:

```
[File header: "ZXTape!" v1.13]
[Block 0x30: Text description — "Game Title by Publisher, 1987"]
[Block 0x32: Archive info — publisher, year, etc.]
[Block 0x10: Standard speed — the loader header block (loaded by the ROM)]
[Block 0x10: Standard speed — the loader data block (loaded by the ROM)]
[Block 0x20: Silence — 1 second gap]
[Block 0x11: Turbo speed — the first game block (loaded by the turbo loader)]
[Block 0x20: Silence — 0.5 second gap]
[Block 0x11: Turbo speed — the second game block]
[Block 0x20: Silence — 0.5 second gap]
...
```

The loader (loaded by the ROM via the two 0x10 blocks) takes over and reads the subsequent 0x11 blocks at turbo speed.

---

## §4. The Standard Block Types

This section covers the most important .TZX block types in detail, with their byte-level structure.

### 4.1 Block 0x10: Standard speed data block

This is the .TZX equivalent of a .TAP block. It represents a standard ROM block (pilot + sync + data + final pulse) with the standard timings.

| Offset (within block) | Size | Field |
|---|---|---|
| 0 | 1 | Block ID (`0x10`) |
| 1 | 2 | Data length (little-endian) — the number of data bytes that follow |
| 3 | 2 | Pause after block (ms) — typically 1000 ms (1 second) for the standard gap |
| 5 | varies | Data — the block's payload (flag byte + data + checksum) |

The data field is identical to the payload of a .TAP block: flag byte + data + checksum. The emulator generates the standard pilot tone, sync pulses, bit timings, and final pulse based on the flag byte (exactly as described in [tap_format.md](tap_format.md) §6).

The `pause after block` field is the length of the gap after the block, in milliseconds. This corresponds to the silence between blocks on a real tape.

### 4.2 Block 0x11: Turbo speed data block

This is the key innovation of .TZX: a turbo loader block with **fully customisable timings**. Every timing parameter can be set independently, allowing .TZX to represent any turbo loader.

| Offset (within block) | Size | Field |
|---|---|---|
| 0 | 1 | Block ID (`0x11`) |
| 1 | 2 | Pilot pulse length (T-states) |
| 3 | 2 | First sync pulse length (T-states) |
| 5 | 2 | Second sync pulse length (T-states) |
| 7 | 2 | Zero bit pulse length (T-states) |
| 9 | 2 | One bit pulse length (T-states) |
| 11 | 2 | Pilot pulse count (for headers, typically 8063; for data, 3223) |
| 13 | 1 | Used bits in last byte (1–8; other bits are ignored) |
| 14 | 2 | Data length (little-endian) — the number of data bytes that follow |
| 16 | 2 | Pause after block (ms) |
| 18 | varies | Data — the block's payload |

The data field is the same as for block 0x10: flag byte + data + checksum (though the flag byte may have a non-standard value, and the checksum may be a custom checksum).

### 4.3 Block 0x11 timing parameters

The timing parameters in block 0x11 allow the .TZX file to represent any turbo loader. For example:

- **Speedlock v1**: pilot 2168, sync 667/735, zero 600, one 1200, pilot count 10000+.
- **Alcatraz**: pilot 2168, sync 667/735, zero 400, one 800, pilot count 5000+.
- **Custom loader**: pilot 2000, sync 600/700, zero 500, one 1000, pilot count 8000.

The standard ROM timings can also be represented with block 0x11: pilot 2168, sync 667/735, zero 855, one 1710, pilot count 8063 (header) or 3223 (data). This is equivalent to block 0x10, just with explicit timings.

### 4.4 Block 0x12: Pure tone block

A pure tone block represents a sequence of pulses at a fixed frequency. It is used for the pilot tone when the data block that follows uses a different encoding (and therefore a separate data block).

| Offset (within block) | Size | Field |
|---|---|---|
| 0 | 1 | Block ID (`0x12`) |
| 1 | 2 | Pulse length (T-states) |
| 3 | 2 | Number of pulses |

The pure tone block does not include any data — it just generates the specified number of pulses at the specified length.

### 4.5 Block 0x13: Pulse sequence block

A pulse sequence block represents an arbitrary sequence of pulses. It is used for sync pulses, custom marker pulses, and any other case where a fixed sequence of pulses is needed.

| Offset (within block) | Size | Field |
|---|---|---|
| 0 | 1 | Block ID (`0x13`) |
| 1 | 1 | Number of pulses |
| 2 | varies | Pulse lengths (each 2 bytes, little-endian) |

For example, the standard sync pulses (667 and 735 T-states) can be represented as:

```
13                  <- Block ID
02                  <- 2 pulses
9B 02               <- 0x029B = 667 T-states
DF 02               <- 0x02DF = 735 T-states
```

### 4.6 Block 0x14: Pure data block

A pure data block represents raw data with custom bit timings, without a pilot tone or sync pulses. It is used after a pure tone block (0x12) and a pulse sequence block (0x13) to complete the block structure.

| Offset (within block) | Size | Field |
|---|---|---|
| 0 | 1 | Block ID (`0x14`) |
| 1 | 2 | Zero bit pulse length (T-states) |
| 3 | 2 | One bit pulse length (T-states) |
| 5 | 1 | Used bits in last byte |
| 6 | 2 | Pause after block (ms) |
| 8 | 3 | Data length (little-endian, 24-bit) — allows blocks larger than 64 KB |
| 11 | varies | Data |

The pure data block allows data lengths up to 16 MB (24-bit length), compared to the 64 KB limit of blocks 0x10 and 0x11. This is useful for very large turbo-loaded blocks.

### 4.7 Block 0x15: Direct recording block

A direct recording block represents the raw tape signal, sampled at a fixed rate. Each byte represents 8 T-states of the EAR signal (bit 7 = first T-state, bit 6 = second T-state, ..., bit 0 = eighth T-state).

| Offset (within block) | Size | Field |
|---|---|---|
| 0 | 1 | Block ID (`0x15`) |
| 1 | 2 | T-states per sample (little-endian) — typically 1 or 8 |
| 3 | 2 | Pause after block (ms) |
| 5 | 1 | Used bits in last byte |
| 6 | 3 | Data length (24-bit) |
| 9 | varies | Data |

The direct recording block is the most faithful representation of a tape signal: it captures the exact EAR level at every T-state. It is used for tapes that cannot be represented by any other block type (e.g., analog protections, non-standard encodings).

The downside is size: a direct recording block at 8 T-states per sample requires about 400 KB per second of tape (8 T-states per byte × 4.4 MB/sec Z80 clock ÷ 8 = 437500 bytes/sec). This is much larger than the equivalent 0x10 or 0x11 block, so direct recording is rarely used for whole tapes.

### 4.8 Block 0x20: Silence block

A silence block represents a period of silence (no signal) on the tape.

| Offset (within block) | Size | Field |
|---|---|---|
| 0 | 1 | Block ID (`0x20`) |
| 1 | 2 | Silence duration (ms) |

The silence block is used for gaps between blocks. Typically, a 1000 ms silence block separates each data block, matching the standard ROM behaviour.

### 4.9 Block 0x21 / 0x22: Group start / end

These blocks mark the start and end of a named group of blocks. They are used to organise the .TZX file into logical sections (e.g., "Loader", "Title screen", "Level 1").

| Block ID | Field |
|---|---|
| `0x21` (group start) | Group name length (1 byte) + group name (ASCII) |
| `0x22` (group end) | (no data) |

Group start/end blocks are purely informational — they do not affect the tape signal. Emulators can use them to display the current loading stage to the user.

### 4.10 Block 0x23: Jump block

A jump block instructs the player to jump to a specific block index, allowing loops and conditionals.

| Offset (within block) | Size | Field |
|---|---|---|
| 0 | 1 | Block ID (`0x23`) |
| 1 | 2 | Block index to jump to (signed, little-endian) |

The jump block is used for multi-load games that need to re-read a block (e.g., when the player dies and the game reloads the level). The block index is relative to the current block (positive = forward, negative = backward).

### 4.11 Block 0x24: Loop block

A loop block instructs the player to repeat the following blocks N times.

| Offset (within block) | Size | Field |
|---|---|---|
| 0 | 1 | Block ID (`0x24`) |
| 1 | 2 | Number of repetitions |

The loop block is paired with an "end loop" marker (block 0x25 or just the implicit end of the loop region). It is used for tapes that have repetitive sections (e.g., the same pilot tone repeated 10 times).

### 4.12 Block 0x30: Text description block

A text description block contains a free-text description of the tape.

| Offset (within block) | Size | Field |
|---|---|---|
| 0 | 1 | Block ID (`0x30`) |
| 1 | 1 | Text length |
| 2 | varies | Text (ASCII) |

The text is typically the game title, the publisher, and the year (e.g., "Manic Miner by Bug-Byte, 1983"). Emulators display this text when the .TZX file is loaded.

### 4.13 Block 0x31: Message block

A message block contains a text message that is displayed to the user during playback (typically at a specific point in the loading process).

| Offset (within block) | Size | Field |
|---|---|---|
| 0 | 1 | Block ID (`0x31`) |
| 1 | 1 | Time (seconds) — how long to display the message |
| 2 | 1 | Text length |
| 3 | varies | Text (ASCII) |

The message block is used for instructions like "Press PLAY on your tape recorder" or "Side A complete — insert Side B".

### 4.14 Block 0x32: Archive info block

An archive info block contains structured metadata about the tape.

| Offset (within block) | Size | Field |
|---|---|---|
| 0 | 1 | Block ID (`0x32`) |
| 1 | 2 | Block length (little-endian) |
| 3 | 1 | Number of info strings |
| 4 | varies | Info strings (each: type ID + length + text) |

The info string type IDs include:

- `0x00`: Full title
- `0x01`: Software house / publisher
- `0x02`: Author
- `0x03`: Year of publication
- `0x04`: Language
- `0x05`: Game/utility type
- `0x06`: Price
- `0x07`: Protection scheme / loader
- `0x08`: Origin

The archive info block is used by archives like World of Spectrum to record the provenance of each tape.

### 4.15 Block 0x33: Hardware type block

A hardware type block specifies the machine that the tape was designed for.

| Offset (within block) | Size | Field |
|---|---|---|
| 0 | 1 | Block ID (`0x33`) |
| 1 | 1 | Number of hardware records |
| 2 | varies | Hardware records (each: hardware type + hardware ID + ROM type) |

The hardware type IDs include:

- `0x00`: ZX Spectrum 16K / 48K
- `0x01`: ZX Spectrum 48K (Issue 1)
- `0x02`: ZX Spectrum 128K (Sinclair)
- `0x03`: ZX Spectrum +2 (grey)
- `0x04`: ZX Spectrum +2A / +3
- `0x05`: Pentagon 128K
- `0x06`: Scorpion 256K
- `0x07`: Amstrad CPC 464
- `0x08`: Commodore 64
- ...

The hardware type block tells the emulator which machine to emulate when playing back the tape.

### 4.16 Block 0x5A: Glue block

The glue block is used to concatenate .TZX files. It marks the boundary between two concatenated files.

| Offset (within block) | Size | Field |
|---|---|---|
| 0 | 1 | Block ID (`0x5A`) |
| 1 | 4 | Magic value (`0x1A 0x5A 0x54 0x5A` = "Z-Tape") |
| 5 | 4 | (Reserved) |

When a loader encounters a glue block, it knows that the following blocks come from a different .TZX file. This is useful for assembling multi-tape collections into a single file.

---

## §5. Turbo Loader Support

Turbo loader support is the **primary reason** .TZX exists. This section explains how .TZX represents turbo loaders in detail.

### 5.1 The challenge of turbo loaders

A turbo loader is a custom load routine that uses non-standard timings to load faster than the ROM. The timings vary between loaders:

- **Speedlock v1**: ~3000 baud (zero pulse 600, one pulse 1200).
- **Speedlock v2**: ~3500 baud (zero pulse 550, one pulse 1100).
- **Alcatraz**: ~4000 baud (zero pulse 400, one pulse 800).
- **Custom loaders**: any timings the developer chose.

The .TAP format cannot represent these timings — it assumes standard ROM timings for every block. A .TAP file of a Speedlock-loaded game would have to either:

- Omit the turbo-loaded blocks (losing the game data), or
- Approximate them as standard blocks (which would not load correctly).

Neither option is acceptable for preservation.

### 5.2 How .TZX solves the problem

The .TZX format solves the problem with the **turbo speed block** (0x11), which allows every timing parameter to be specified explicitly:

- Pilot pulse length
- Sync pulse lengths (two pulses)
- Zero bit pulse length
- One bit pulse length
- Pilot pulse count
- Pause after block

This allows the .TZX file to represent any turbo loader, with any combination of timings. The emulator plays back the block with the specified timings, producing exactly the same signal that the original turbo loader would have seen.

### 5.3 The typical structure of a turbo-loaded .TZX

A typical .TZX file for a Speedlock-loaded game has the following structure:

```
[File header: "ZXTape!" v1.13]
[Block 0x30: Text description — "Game Title by Publisher, 1987"]
[Block 0x10: Standard speed — the loader header (loaded by the ROM)]
[Block 0x10: Standard speed — the loader data (loaded by the ROM)]
[Block 0x20: Silence — 1 second gap]
[Block 0x11: Turbo speed — the game header (loaded by the turbo loader)]
[Block 0x11: Turbo speed — the game data block 1]
[Block 0x20: Silence — 0.5 second gap]
[Block 0x11: Turbo speed — the game data block 2]
...
```

The first two blocks (0x10) are loaded by the ROM's `LOAD ""` command. These blocks contain the turbo loader itself — a small machine code program that takes over and reads the subsequent blocks at turbo speed.

The subsequent blocks (0x11) contain the actual game data, encoded at the turbo loader's timings. The turbo loader (running on the emulated Spectrum) reads these blocks via the EAR input, exactly as it would on a real Spectrum.

### 5.4 How the emulator plays back turbo blocks

When the emulator plays back a turbo speed block (0x11), it:

1. Reads the timing parameters (pilot, sync, zero, one, count).
2. Generates the pilot tone (count pulses of pilot length).
3. Generates the two sync pulses.
4. For each byte of data, for each bit (MSB first), generates two pulses at the zero or one length.
5. Generates the pause after block.

The emulated Spectrum's CPU runs in parallel, executing the turbo loader's load routine. The turbo loader's `IN A, (#FE)` instructions read the EAR input that the emulator is generating. The timings match exactly, so the turbo loader reads the data correctly.

### 5.5 The "cycle-exact" challenge

For maximum fidelity, the emulator must generate the turbo block's pulses at exactly the right T-state counts. If the emulator's timing is off by even one T-state per pulse, the turbo loader's timing-sensitive code may fail to lock on, and the load will fail.

This is why cycle-exact Z80 emulation is important for accurate .TZX playback. Emulators that are not cycle-exact (e.g., that use approximate instruction timings) may fail to play back turbo-loaded .TZX files correctly.

The .TZX format itself does not encode cycle-exact information — it just specifies the pulse lengths. But the emulator's playback must be cycle-exact for the timings to be reproduced correctly.

### 5.6 Custom encodings

Some turbo loaders use non-standard bit encodings — for example, three pulse durations (instead of two) to encode ternary data, or variable-length pulses to encode run-length-compressed data.

The .TZX format can represent these via the **pure tone** (0x12), **pulse sequence** (0x13), and **pure data** (0x14) blocks, which allow arbitrary sequences of pulses with arbitrary lengths. By combining these blocks, any encoding can be represented.

For truly unusual encodings (e.g., analog protections that rely on the Schmitt trigger's exact threshold), the **direct recording** block (0x15) can be used to capture the raw signal. This is the most faithful representation, but also the largest (in file size).

### 5.7 The Speedlock pilot tone quirk

Some turbo loaders (notably Speedlock) use a **non-standard pilot tone** that is shorter than the standard 8063 pulses. For example, Speedlock v3 uses a pilot tone of about 100 pulses, which the loader uses to detect the start of the block.

The .TZX format represents this by setting the `pilot pulse count` field in the turbo speed block (0x11) to the actual count (e.g., 100). The emulator generates only the specified number of pilot pulses, matching the original tape.

This level of detail is what makes .TZX the format of choice for preservation — it captures the exact timings and counts of the original tape, allowing perfect reproduction.

---

## §6. Writing a .TZX File

This section shows how to generate a .TZX file from a program, using C-style pseudocode.

### 6.1 Writing the file header

Every .TZX file begins with the 10-byte header:

```c
void tzx_write_header(FILE *f) {
    uint8_t header[10] = {
        'Z', 'X', 'T', 'a', 'p', 'e', '!',  // Magic: "ZXTape!"
        1,                                     // Major version
        13,                                    // Minor version
        0                                      // Integrity byte (deprecated)
    };
    fwrite(header, 1, 10, f);
}
```

### 6.2 Writing a standard speed block (0x10)

```c
void tzx_write_standard_block(FILE *f, const uint8_t *data,
                              uint16_t length, uint16_t pause_ms) {
    uint8_t prefix[5];
    prefix[0] = 0x10;                          // Block ID
    prefix[1] = length & 0xFF;                 // Data length low byte
    prefix[2] = (length >> 8) & 0xFF;          // Data length high byte
    prefix[3] = pause_ms & 0xFF;               // Pause low byte
    prefix[4] = (pause_ms >> 8) & 0xFF;        // Pause high byte
    fwrite(prefix, 1, 5, f);
    fwrite(data, 1, length, f);
}
```

### 6.3 Writing a turbo speed block (0x11)

```c
typedef struct {
    uint16_t pilot_pulse;
    uint16_t sync1_pulse;
    uint16_t sync2_pulse;
    uint16_t zero_pulse;
    uint16_t one_pulse;
    uint16_t pilot_count;
    uint8_t  used_bits_last;
    uint16_t pause_ms;
} TurboTimings;

void tzx_write_turbo_block(FILE *f, const uint8_t *data, uint16_t length,
                           const TurboTimings *t) {
    uint8_t prefix[18];
    prefix[0]  = 0x11;                         // Block ID
    prefix[1]  = t->pilot_pulse & 0xFF;
    prefix[2]  = (t->pilot_pulse >> 8) & 0xFF;
    prefix[3]  = t->sync1_pulse & 0xFF;
    prefix[4]  = (t->sync1_pulse >> 8) & 0xFF;
    prefix[5]  = t->sync2_pulse & 0xFF;
    prefix[6]  = (t->sync2_pulse >> 8) & 0xFF;
    prefix[7]  = t->zero_pulse & 0xFF;
    prefix[8]  = (t->zero_pulse >> 8) & 0xFF;
    prefix[9]  = t->one_pulse & 0xFF;
    prefix[10] = (t->one_pulse >> 8) & 0xFF;
    prefix[11] = t->pilot_count & 0xFF;
    prefix[12] = (t->pilot_count >> 8) & 0xFF;
    prefix[13] = t->used_bits_last;
    prefix[14] = length & 0xFF;
    prefix[15] = (length >> 8) & 0xFF;
    prefix[16] = t->pause_ms & 0xFF;
    prefix[17] = (t->pause_ms >> 8) & 0xFF;
    fwrite(prefix, 1, 18, f);
    fwrite(data, 1, length, f);
}
```

### 6.4 Writing a silence block (0x20)

```c
void tzx_write_silence(FILE *f, uint16_t duration_ms) {
    uint8_t block[3];
    block[0] = 0x20;
    block[1] = duration_ms & 0xFF;
    block[2] = (duration_ms >> 8) & 0xFF;
    fwrite(block, 1, 3, f);
}
```

### 6.5 Writing a text description block (0x30)

```c
void tzx_write_text_description(FILE *f, const char *text) {
    uint8_t length = strlen(text);
    fputc(0x30, f);
    fputc(length, f);
    fwrite(text, 1, length, f);
}
```

### 6.6 A complete .TZX generator

To generate a .TZX file for a turbo-loaded game:

```c
void tzx_generate_turbo_game(const char *filename,
                             const char *title,
                             const uint8_t *loader_data, uint16_t loader_length,
                             const uint8_t *game_data, uint16_t game_length,
                             const TurboTimings *turbo_timings) {
    FILE *f = fopen(filename, "wb");

    // File header
    tzx_write_header(f);

    // Text description
    tzx_write_text_description(f, title);

    // Standard speed blocks for the loader (loaded by ROM)
    uint8_t loader_header[19];
    build_loader_header(loader_header, loader_length);  // (omitted for brevity)
    tzx_write_standard_block(f, loader_header, 19, 1000);
    tzx_write_standard_block(f, loader_data, loader_length, 1000);

    // Silence gap
    tzx_write_silence(f, 1000);

    // Turbo speed block for the game data
    tzx_write_turbo_block(f, game_data, game_length, turbo_timings);

    fclose(f);
}
```

### 6.7 Converting from .TAP to .TZX

Converting a .TAP file to a .TZX file is straightforward:

1. Write the .TZX file header.
2. For each block in the .TAP file, write a corresponding standard speed block (0x10).
3. (Optionally) insert silence blocks (0x20) between blocks.

The resulting .TZX file represents the same tape as the .TAP file, but in the more capable .TZX format. It can be played back by any .TZX-aware emulator.

```c
void tzx_convert_from_tap(const char *tap_filename, const char *tzx_filename) {
    FILE *tap = fopen(tap_filename, "rb");
    FILE *tzx = fopen(tzx_filename, "wb");

    // Write the .TZX file header
    tzx_write_header(tzx);

    // Convert each .TAP block to a .TZX standard speed block
    TapBlock block;
    while (tap_read_block(tap, &block) > 0) {
        tzx_write_standard_block(tzx, block.data, block.length, 1000);
        free(block.data);
    }

    fclose(tap);
    fclose(tzx);
}
```

---

## §7. Reading a .TZX File (Emulator Playback)

This section covers how an emulator plays back a .TZX file.

### 7.1 The playback loop

The emulator's .TZX playback works as follows:

1. Read and verify the file header.
2. Read the next block.
3. Dispatch on the block ID:
   - 0x10: play a standard speed block.
   - 0x11: play a turbo speed block.
   - 0x12: play a pure tone.
   - 0x13: play a pulse sequence.
   - 0x14: play pure data.
   - 0x15: play direct recording data.
   - 0x20: generate silence.
   - 0x21 / 0x22: group start/end (no playback action).
   - 0x23: jump to a different block.
   - 0x24: loop the following blocks.
   - 0x30 / 0x31 / 0x32 / 0x33: metadata (display to user, no playback action).
   - Unknown: skip.
4. Repeat from step 2 until EOF or a jump/loop changes the position.

### 7.2 Playing a standard speed block (0x10)

To play a standard speed block:

```c
void tzx_play_standard_block(SpectrumState *state, const TzxStandardBlock *block) {
    int is_header = (block->data[0] == 0x00);
    int pilot_count = is_header ? 8063 : 3223;

    // Pilot tone (2168 T-states per pulse)
    for (int i = 0; i < pilot_count; i++) {
        tape_generate_pulse(state, 2168, 1);
        tape_generate_pulse(state, 2168, 0);
    }

    // Sync pulses
    tape_generate_pulse(state, 667, 1);
    tape_generate_pulse(state, 735, 0);

    // Data (MSB first, 855 for 0, 1710 for 1)
    for (int i = 0; i < block->length; i++) {
        tape_generate_byte_standard(state, block->data[i]);
    }

    // Final pulse
    tape_generate_pulse(state, 955, 1);

    // Pause after block (silence)
    tape_generate_silence(state, block->pause_ms * 3500);  // ms to T-states
}
```

### 7.3 Playing a turbo speed block (0x11)

To play a turbo speed block:

```c
void tzx_play_turbo_block(SpectrumState *state, const TzxTurboBlock *block) {
    // Pilot tone
    for (int i = 0; i < block->pilot_count; i++) {
        tape_generate_pulse(state, block->pilot_pulse, 1);
        tape_generate_pulse(state, block->pilot_pulse, 0);
    }

    // Sync pulses
    tape_generate_pulse(state, block->sync1_pulse, 1);
    tape_generate_pulse(state, block->sync2_pulse, 0);

    // Data (MSB first)
    for (int i = 0; i < block->length; i++) {
        for (int bit = 7; bit >= 0; bit--) {
            int b = (block->data[i] >> bit) & 1;
            int len = b ? block->one_pulse : block->zero_pulse;
            tape_generate_pulse(state, len, 1);
            tape_generate_pulse(state, len, 0);
        }
    }

    // Pause after block
    tape_generate_silence(state, block->pause_ms * 3500);
}
```

### 7.4 The cycle-exactness requirement

For turbo speed blocks, the emulator's pulse generation must be **cycle-exact**. This means the `tape_generate_pulse` function must run the Z80 for exactly the specified number of T-states — no more, no less.

If the emulator's Z80 core is not cycle-exact (e.g., it rounds instruction timings to the nearest cycle), the pulse lengths will be slightly off, and the turbo loader's timing-sensitive code may fail.

This is why cycle-exact Z80 emulation is so important for accurate .TZX playback. Modern emulators (Fuse, ZEsarUX, SpecEmu, Klive) are all cycle-exact, and they can play back .TZX files with high fidelity.

### 7.5 Handling jumps and loops

The jump (0x23) and loop (0x24) blocks require the emulator to maintain a block index and to seek backward or forward in the file.

```c
void tzx_play_with_jumps(SpectrumState *state, FILE *f) {
    long *block_offsets = build_block_offset_index(f);
    int n_blocks = count_blocks(f);
    int current = 0;

    while (current < n_blocks) {
        fseek(f, block_offsets[current], SEEK_SET);
        TzxBlock block;
        tzx_read_block(f, &block);

        switch (block.id) {
            case 0x23:  // Jump
                current += block.jump.offset;
                break;
            case 0x24:  // Loop start
                loop_count = block.loop.count;
                loop_start = current + 1;
                break;
            // ... other block types ...
            default:
                tzx_play_block(state, &block);
                current++;
        }
    }
}
```

This is more complex than the linear playback of .TAP files, but it allows .TZX to represent multi-load games with complex loading patterns.

### 7.6 Warp playback for .TZX

Like .TAP, .TZX supports warp playback (instant loading) for standard blocks (0x10). For turbo blocks (0x11), warp playback is more difficult: the emulator must understand the turbo loader's encoding to load the data directly.

Some emulators implement "smart warp" for .TZX: they identify the turbo loader (e.g., by matching the timings against known loaders) and use a loader-specific fast-load routine. This achieves near-instant loading for common turbo loaders.

For unknown turbo loaders, the emulator must fall back to real-time playback, which is why cycle-exact emulation is still important.

---

## §8. Compatibility and Quirks

### 8.1 Emulator support

| Emulator | .TZX support | Notes |
|---|---|---|
| **Fuse** | ✅ Full | Reference implementation; supports all standard block types |
| **ZEsarUX** | ✅ Full | Full support, including direct recording blocks |
| **SpecEmu** | ✅ Full | Cycle-exact playback for turbo loaders |
| **Klive** | ✅ Full | Modern emulator with strong .TZX support |
| **EightyOne** | ✅ Most | Supports standard and turbo blocks; some extension blocks unsupported |
| **SPIN** | ✅ Most | Older but widely used; some v1.10+ blocks unsupported |
| **Qaop** | ⚠️ Partial | Browser-based; supports standard blocks but not all turbo blocks |
| **X128** | ✅ Full | The original .TZX-aware emulator (Thomas Schreiber) |

Most modern emulators support .TZX v1.10 or later. The current specification is v1.13, but few emulators support the v1.11–v1.13 extensions (which are mostly for non-Spectrum machines).

### 8.2 Version differences

The .TZX specification has evolved through 13 minor versions. The most important differences:

- **v1.0 (1996)**: Standard speed, turbo speed, pure tone, pulse sequence, pure data, silence, group, text, message, archive info, hardware type.
- **v1.1 (1997)**: Added the glue block (0x5A) for concatenating .TZX files.
- **v1.3 (1999)**: Added direct recording (0x15) for raw signal capture.
- **v1.4 (2000)**: Refined the turbo speed block; added the 24-bit length for pure data (0x14).
- **v1.8 (2003)**: Added the C64 ROM type (0x16) and C64 turbo type (0x17).
- **v1.10 (2004)**: Added the "generalised data" block (0x18) for very complex encodings.
- **v1.13 (2008)**: Current version; minor clarifications and bug fixes.

Most .TZX files on the internet are v1.10 or later. Files from the late 1990s may be v1.0–v1.3, but these are rare.

### 8.3 Conversion to .TAP

Converting a .TZX file to a .TAP file is possible only if the .TZX file contains **only standard speed blocks** (0x10). If the .TZX file contains turbo blocks (0x11) or any other non-standard blocks, the conversion will lose information.

Conversion tools typically warn the user if the .TZX file cannot be losslessly converted to .TAP. Some tools offer a "best effort" conversion that replaces turbo blocks with standard blocks (which will not load correctly on a real Spectrum), but this is rarely useful.

For most modern use cases, .TZX files are kept as .TZX (since every modern emulator supports .TZX), and conversion to .TAP is only done when targeting a .TAP-only emulator.

### 8.4 The "PAUSE" bug

Some early .TZX files have a bug where the `pause after block` field in standard speed blocks (0x10) is set to 0, which can cause some emulators to skip the block entirely (because they interpret 0 as "no pause, immediately start the next block"). This was fixed in the .TZX specification v1.4 by clarifying that 0 means "no pause" (the next block starts immediately), not "skip this block".

Modern emulators handle this correctly, but some older emulators may not.

### 8.5 The hardware type block

The hardware type block (0x33) specifies the machine that the tape was designed for. For Spectrum tapes, the hardware type is typically:

- `0x00` (ZX Spectrum 16K / 48K): for tapes that work on all 48K Spectrums.
- `0x02` (ZX Spectrum 128K): for tapes that require the 128K.
- `0x04` (ZX Spectrum +2A / +3): for tapes that require the +2A or +3.
- `0x05` (Pentagon 128K): for Russian tapes that require the Pentagon.

The emulator uses this block to decide which machine to emulate when playing back the tape. If the hardware type block is absent, the emulator uses the default machine (typically the 48K).

### 8.6 Custom block types

The .TZX specification reserves block IDs 0x80–0xFF for extension blocks. These blocks have a 4-byte length field after the block ID, allowing loaders to skip them.

Some emulator authors have defined custom extension blocks for their emulators. For example, an emulator might define a custom block to store its own metadata (e.g., save states, debugger info). These custom blocks are skipped by other emulators, which is the whole point of the extension mechanism.

### 8.7 The .TZX preservation project

The .TZX format is the basis of the **.TZX Preservation Project**, an ongoing effort to create faithful .TZX images of every Spectrum tape ever produced. The project is maintained by volunteers and hosted on sites like World of Spectrum.

The project's goal is to preserve the original tape timings, including turbo loaders, custom encodings, and analog protections. This is essential for historical accuracy: future generations should be able to load any Spectrum tape exactly as it was originally experienced.

The .TZX format's extensibility is what makes this project possible: new block types can be added to represent new tape patterns as they are discovered, without breaking existing .TZX files.

---

## §9. Comparison with .TAP

This section compares .TZX and .TAP in detail, to help you choose the right format.

### 9.1 Feature comparison

| Feature | .TAP | .TZX |
|---|---|---|
| **File header** | None | 10-byte header ("ZXTape!" + version) |
| **Block structure** | Uniform (2-byte length + data) | Per-block-type structure |
| **Standard speed blocks** | ✅ | ✅ (block 0x10) |
| **Turbo speed blocks** | ❌ | ✅ (block 0x11) |
| **Custom timings** | ❌ | ✅ |
| **Custom encodings** | ❌ | ✅ (blocks 0x12, 0x13, 0x14, 0x15) |
| **Silence / gaps** | Implicit (between blocks) | Explicit (block 0x20) |
| **Grouping** | ❌ | ✅ (blocks 0x21, 0x22) |
| **Jumps / loops** | ❌ | ✅ (blocks 0x23, 0x24) |
| **Metadata** | ❌ | ✅ (blocks 0x30, 0x31, 0x32, 0x33) |
| **File size (typical)** | Smaller | Larger (overhead for block headers) |
| **Parser complexity** | Simple | Complex (per-block-type dispatch) |
| **Forward compatibility** | N/A | ✅ (unknown blocks skipped) |
| **Emulator support** | Universal | Wide (all modern emulators) |

### 9.2 When to use .TAP

Use .TAP when:

- The software uses the **standard ROM loader** (no turbo loader, no custom timings).
- You want **maximum compatibility** (every emulator supports .TAP).
- You want the **smallest possible file size**.
- You are distributing **BASIC programs**, **simple machine code programs**, or **modern homebrew**.

### 9.3 When to use .TZX

Use .TZX when:

- The software uses a **turbo loader** (Speedlock, Alcatraz, Bleepload, etc.).
- The software uses **custom timings** or **custom encodings**.
- You are **preserving** a tape for archival purposes.
- You need to include **metadata** (publisher, year, author).
- The tape has a **complex loading pattern** (loops, jumps, multi-stage loading).

### 9.4 File size comparison

For a standard Spectrum program (no turbo loader), the .TAP and .TZX files are roughly the same size:

- .TAP: each block is 2 + 19 = 21 bytes (header) or 2 + N + 2 bytes (data).
- .TZX: 10-byte file header + each block is 5 + 19 = 24 bytes (header) or 5 + N bytes (data).

For a typical 48K program, the .TAP file is about 49 KB, and the .TZX file is about 49 KB (the overhead is small).

For turbo-loaded software, only .TZX can represent the tape. The .TZX file is typically about the same size as the equivalent .TAP file would be (if it could exist), because the turbo loader uses a more efficient encoding.

### 9.5 Conversion

Converting .TAP → .TZX is straightforward (see §6.7). The resulting .TZX file uses only standard speed blocks (0x10) and can be played by any .TZX-aware emulator.

Converting .TZX → .TAP is possible only if the .TZX file contains only standard speed blocks. If the .TZX file contains turbo blocks (0x11) or other non-standard blocks, the conversion cannot be done losslessly.

### 9.6 The modern recommendation

For modern Spectrum development and distribution:

- **Use .TAP for standard software**. It is smaller, simpler, and universally supported.
- **Use .TZX for turbo-loaded software** and for archival preservation.
- **Provide both** when in doubt. Many archives provide both formats.

The World of Spectrum archive uses .TZX as its primary format (for maximum fidelity) and provides .TAP as a convenience for users who want smaller files or whose emulators only support .TAP.

### 9.7 The future of tape formats

The .TZX format is mature and unlikely to see major changes. The current version (v1.13) has been stable for over a decade, and the format covers essentially all known Spectrum tape patterns.

A successor format (**.TZX2**) has been discussed, with goals like:

- Better support for cycle-exact timing.
- Built-in compression.
- A cleaner block structure (e.g., a uniform 4-byte length for all block types).
- Better metadata support (e.g., Dublin Core fields).

However, .TZX2 has not been formally specified or widely adopted, and .TZX remains the de facto standard for tape preservation.

For the foreseeable future, .TZX (for preservation) and .TAP (for distribution) will continue to be the two main tape file formats for the Spectrum.

---

## §10. Cross-References

### 10.1 The rest of the tape series

- [tape_interface.md](tape_interface.md) — the hardware layer: EAR/MIC circuits, ULA, port `#FE`, bit-banging, pilot tone, sync pulses, bit timings.
- [tape_format.md](tape_format.md) — the logical data format: blocks, headers, block types, checksums.
- [tap_format.md](tap_format.md) — the simplest tape file format. The .TZX format extends .TAP with support for non-standard blocks and timings.
- [csw_format.md](csw_format.md) — the Compressed Square Wave format. A lower-level representation that captures the raw signal (below the block structure).
- [pzx_format.md](pzx_format.md) — an alternative pulse-based format.

### 10.2 The snapshot formats

These live in the sibling [../snapshots/](../snapshots/README.md) directory.

- [sna_format.md](../snapshots/sna_format.md) — the .SNA snapshot format. Snapshots capture the machine state at a single instant; .TZX files capture the loading process.
- [z80_format.md](../snapshots/z80_format.md) — the .Z80 snapshot format.
- [szx_format.md](../snapshots/szx_format.md) — the .SZX snapshot format.
- [rzx_format.md](../snapshots/rzx_format.md) — the .RZX replay format.

### 10.3 Related topics

- [Reverse engineering](../../08_reverse_engineering/) — .TZX files are often analysed during reverse engineering to extract the turbo loader and the protected code.
- [Demoscene](../../07_demoscene/) — demos often use custom loaders that push the boundaries of the .TZX format.
- [BASIC interpreter internals](../../04_operating_systems/) — the BASIC interpreter handles the `LOAD`, `SAVE`, `MERGE`, `VERIFY` commands.

### 10.4 External resources

- **The .TZX specification** — the canonical document for the .TZX format, maintained by the Spectrum community.
- **World of Spectrum** — the largest archive of .TZX files.
- **The .TZX Preservation Project** — an ongoing effort to create faithful .TZX images of every Spectrum tape.
- **TZX Tools** — a command-line toolkit for converting between tape formats.
- **Fuse emulator** — a reference implementation that can read, write, and play back .TZX files.

### 10.5 Where to go next

After understanding the .TZX format, the natural next steps are:

- **For preservation**: read about the .TZX Preservation Project and consider contributing .TZX images of tapes that have not yet been preserved.
- **For emulator development**: implement .TZX playback in your emulator. Start with standard speed blocks (0x10), then add turbo speed blocks (0x11), then the other block types.
- **For reverse engineering**: study the turbo loader block timings in a .TZX file to understand how the original turbo loader worked. The timings reveal the loader's encoding, which is the first step to extracting the protected code.
- **For the lower-level signal representation**: read about [csw_format.md](csw_format.md) (Compressed Square Wave), which captures the tape signal below the block structure. This is useful for tapes that cannot be represented by any .TZX block type.

---

## License

This article is licensed under the **Creative Commons Attribution-ShareAlike 4.0 International License** (CC BY-SA 4.0). You are free to share and adapt this material, provided you credit the original source and license your contributions under the same terms.

For the canonical text of the license, see https://creativecommons.org/licenses/by-sa/4.0/.
