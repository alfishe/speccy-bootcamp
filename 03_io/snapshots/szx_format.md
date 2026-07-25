[← Home](../../README.md) · [I/O](../../README.md) · [Snapshots](README.md)

# The .SZX Snapshot Format

The .SNA format (1992) and .Z80 format (1994) dominated Spectrum snapshots for over a decade, but both have a fundamental limitation: they use a **fixed-layout header**. Every new feature requires either adding new fields to the header (breaking older loaders) or overloading existing fields (creating ambiguity). The .Z80 format's evolution through v1, v2, and v3 shows the friction of this approach.

The **.SZX format** (created by **César Hernández Bauset** for the **ZEsarUX** emulator around 2005) takes a different approach: it uses a **chunk-based (IFF-like)** file structure, where each piece of state is stored in a separately-identified "chunk". New chunks can be added to capture new state without breaking older loaders — they just ignore chunks they don't recognise. This design makes .SZX the most extensible and future-proof of the major snapshot formats.

.SZX is ZEsarUX's **native** format, but the format specification was published openly, and several other emulators (Fuse, SpectaNet, etc.) support it. Today it is the format of choice for capturing complex Spectrum state — particularly state involving peripherals, custom hardware, or cycle-exact timing.

This article covers the .SZX format: its history, the chunk-based file structure, the standard chunk types, the hardware identification system, what state is captured, how to write a loader, and the gotchas. For the other snapshot formats, see [sna_format.md](sna_format.md) and [z80_format.md](z80_format.md).

---

## Roadmap

1. **What the .SZX format is** — history, scope, design philosophy
2. **The chunk-based file structure** — IFF-like layout, magic header
3. **The standard chunks** — Z80 registers, AY, memory, peripherals
4. **Hardware identification** — the machine ID and configuration
5. **State captured** — what .SZX preserves that .SNA/.Z80 don't
6. **Writing an .SZX loader** — reference loader implementation
7. **Extensibility and custom chunks** — how to add new chunk types
8. **Compatibility across emulators** — who supports what
9. **Comparison with .SNA and .Z80** — when to use which
10. **Cross-references** — where to go next

---

## §1. What the .SZX Format Is

### 1.1 Origins

The .SZX format was created by **César Hernández Bauset** (the author of the ZEsarUX emulator) in the mid-2000s. ZEsarUX was becoming a sophisticated emulator with support for many Spectrum variants and peripherals, and the .SNA / .Z80 formats were proving insufficient to capture all the state ZEsarUX needed to preserve.

Rather than extending .Z80 with yet another version, Hernández Bauset chose a **clean-slate design** based on the well-established IFF (Interchange File Format) pattern used by many other file formats (RIFF for WAV/AVI, AIFF for audio, PNG chunks, etc.). The result is a format that is:

- **Extensible**: new chunk types can be added without breaking older loaders.
- **Modular**: each piece of state is in its own chunk, easy to parse and reason about.
- **Self-describing**: each chunk carries its own length, so loaders can skip chunks they don't understand.
- **Compact**: chunks can be compressed independently.

### 1.2 Design philosophy

The .SZX format's design philosophy is "**capture everything**". Unlike .SNA (which captures only the basics) or .Z80 (which captures a fixed list of fields), .SZX is designed to allow any piece of emulated state to be stored in a chunk. The format defines a set of standard chunks for the most common state, but new chunks can be added by anyone.

This philosophy has made .SZX the format of choice for:

- **ZEsarUX** itself, which uses .SZX for all its native snapshots.
- **Emulator developers** who want to capture complex state (e.g., cycle-exact timing, peripheral state) that other formats cannot represent.
- **Archivists** who want the maximum fidelity snapshot for preservation purposes.

### 1.3 Scope

A .SZX file contains:

- A **file header** (8 bytes) identifying the format and version.
- An **arbitrary number of chunks**, each containing a piece of state.

Each chunk has:

- A **4-character ASCII ID** (e.g., "Z80R" for Z80 registers, "AY16" for AY state, "RAM " for a memory page).
- A **4-byte length** (the size of the chunk's data, in bytes, little-endian).
- The chunk **data** itself.

The loader reads chunks one at a time. If it doesn't recognise a chunk ID, it skips that chunk (using the length field) and continues.

### 1.4 Why .SZX matters

.SZX matters because it represents the **state of the art** in Spectrum snapshot formats. It is the only widely-supported format that can capture essentially any Spectrum state, including:

- Multiple sound chips (TurboSound, TurboSound FM, MoonSound).
- Multiple video modes (Layer 2, hardware sprites, tilemaps on the Next).
- Peripheral state (Beta 128 FDC, +3 FDC, DivIDE, IDE, Multiface, Interface 1, etc.).
- Cycle-exact timing.
- Custom hardware (Russian clones, the ZX Spectrum Next, etc.).

For modern Spectrum development (especially for the ZX Spectrum Next), .SZX is often the only format that can faithfully capture the state of a complex piece of software.

---

## §2. The Chunk-Based File Structure

The .SZX file format uses an IFF-like chunk structure. This section covers the file-level layout.

### 2.1 The file header (8 bytes)

Every .SZX file begins with an 8-byte file header:

| Offset | Size | Field | Notes |
|---|---|---|---|
| 0 | 4 | Magic | "ZXST" (0x5A 0x58 0x53 0x54) — identifies this as an .SZX file |
| 4 | 4 | Version (32-bit, little-endian) | The .SZX format version. Currently 1 (0x01 0x00 0x00 0x00) |

If the first 4 bytes are not "ZXST", the file is not an .SZX file. Loaders should reject it.

The version field allows for future major format changes. Version 1 is the original .SZX format; subsequent versions (if any) would indicate breaking changes.

### 2.2 The chunks

After the 8-byte file header, the file consists of a sequence of chunks. Each chunk has the following structure:

| Offset (within chunk) | Size | Field |
|---|---|---|
| 0 | 4 | Chunk ID (4 ASCII characters) |
| 4 | 4 | Chunk data length (32-bit, little-endian) |
| 8 | (length) | Chunk data |

The chunk ID identifies what type of data the chunk contains. The chunk data length gives the size of the chunk's data (not including the 8-byte chunk header). The chunk data follows immediately.

After the chunk data, the next chunk begins (or EOF if there are no more chunks).

### 2.3 Chunk ordering

Chunks can appear in any order — the loader should not assume a specific ordering. However, as a convention, the **hardware configuration** chunk (which identifies the machine) typically comes first, followed by the Z80 register chunk, then the memory pages, then peripheral chunks.

If multiple chunks of the same type appear (e.g., multiple "RAM " chunks for different memory pages), they are applied in order.

### 2.4 Skipping unknown chunks

The most important rule of .SZX loading: **if you encounter a chunk ID you don't recognise, skip it using the chunk data length and continue with the next chunk**. Do not abort the load.

This rule is what makes .SZX extensible. A loader that aborts on unknown chunks would be unable to load .SZX files written by newer emulators.

### 2.5 Alignment and padding

Chunks are **not padded** to any alignment boundary. The next chunk starts immediately after the previous chunk's data. This keeps the format compact but means loaders must read chunk lengths carefully (off-by-one errors can corrupt the rest of the file).

Some early .SZX implementations padded chunks to 4-byte boundaries, but this is non-standard. Modern implementations do not pad.

### 2.6 Hex view

A visual layout of a small .SZX file:

```
Offset 0x00: 5A 58 53 54 01 00 00 00    <- File header: "ZXST" + version 1
Offset 0x08: 5A 38 30 52 21 00 00 00    <- Chunk: ID="Z80R", length=33
Offset 0x10: 3F 00 00 00 ...             <- Chunk data: Z80 registers
...
Offset 0x29: 41 59 31 36 10 00 00 00    <- Chunk: ID="AY16", length=16
Offset 0x31: 00 0F 00 ...                <- Chunk data: AY registers
...
Offset 0x41: 52 41 4D 20 00 40 00 00    <- Chunk: ID="RAM ", length=16384
Offset 0x49: ...                         <- Chunk data: 16384 bytes of RAM
```

This layout is typical of IFF-derived formats.
---

## §3. The Standard Chunks

The .SZX format defines a set of standard chunk IDs for the most common pieces of Spectrum state. This section covers the most important ones.

### 3.1 The chunk ID registry

| Chunk ID | Name | Content |
|---|---|---|
| `CFGR` | Configuration | Machine type, settings, hardware ID |
| `Z80R` | Z80 registers | All Z80 registers including alternates, IFF1/2, IM, I, R |
| `RAM ` | RAM page | A single 16 KB RAM bank (with bank number) |
| `AY16` | AY-3-8910 state | All 16 AY registers plus the currently-selected register |
| `KEYB` | Keyboard state | Current keyboard matrix state |
| `SCLD` | Specbase / Chroma 81 / Chroma interface | (Rarely used) |
| `ZXRG` | ZX Spectrum Next registers | All NextReg values |
| `AYRX` | AY extension | Extra AY state for TurboSound (multi-chip) |
| `BETA` | Beta 128 FDC state | The Beta 128 disk controller state |
| `PLSB` | +3 / +3E FDC state | The +3's internal floppy controller state |
| `DIVE` | DivIDE / DivMMC state | The DivIDE/DivMMC interface state |
| `IF1 ` | Interface 1 state | Microdrive / serial / ZX Net state |
| `MULF` | Multiface state | Multiface One / 128 / Three state |
| `MOUS` | Mouse state | Kempston / AMX mouse position and buttons |
| `JOYS` | Joystick state | Joystick port state |
| `COPR` | Copper list | The ZX Spectrum Next copper program |
| `DMA ` | DMA state | The ZX Spectrum Next DMA state |
| `CRTC` | CRTC state | (For machines with a CRTC) |
| `RTC ` | Real-time clock state | For machines with an RTC |
| `ESPD` | ESP / WiFi state | For the ZX Spectrum Next's ESP module |
| `USBR` | USB ringbuffer state | For the ZX Spectrum Next's USB |

Many more chunk types are defined; see the ZEsarUX source code for the canonical list.

### 3.2 The CFGR (Configuration) chunk

The `CFGR` chunk is typically the first chunk in the file. It identifies the source machine and provides top-level configuration.

| Offset | Size | Field | Notes |
|---|---|---|---|
| 0 | 1 | Hardware ID | See §4 for the list of hardware IDs |
| 1 | 1 | Flags | Bit 0: issue 2; Bit 1: AY enabled; Bit 2: +3 FDC enabled; etc. |
| 2 | 1 | Video mode | 0=standard, 1=ATM Turbo, 2=text, 3=TS-Conf, etc. |
| 3 | 1 | Extended flags | Bits depend on hardware ID |
| 4+ | varies | (Hardware-specific data) | E.g., NextReg values for the Next, BaseConf settings for the Evo |

The `CFGR` chunk is the most variable in size — its content depends on the hardware ID. Loaders should read only the parts relevant to their supported hardware and skip the rest.

### 3.3 The Z80R (Z80 Registers) chunk

The `Z80R` chunk captures all Z80 register values:

| Offset | Size | Field |
|---|---|---|
| 0 | 2 | AF (F low, A high) |
| 2 | 2 | BC (C low, B high) |
| 4 | 2 | DE (E low, D high) |
| 6 | 2 | HL (L low, H high) |
| 8 | 2 | AF' (F' low, A' high) |
| 10 | 2 | BC' (C' low, B' high) |
| 12 | 2 | DE' (E' low, D' high) |
| 14 | 2 | HL' (L' low, H' high) |
| 16 | 2 | IX |
| 18 | 2 | IY |
| 20 | 2 | SP |
| 22 | 2 | PC |
| 24 | 1 | I |
| 25 | 1 | R (bit 7 = R7) |
| 26 | 1 | IFF1 |
| 27 | 1 | IFF2 |
| 28 | 1 | IM (interrupt mode) |
| 29 | 2 | MEMPTR (the undocumented W register) |
| 31 | 2 | (reserved / extended flags) |

The `Z80R` chunk is 33 bytes (or longer for future extensions). It includes MEMPTR — the undocumented Z80 register that .SNA does not capture and .Z80 only captures in v3.

### 3.4 The RAM (RAM Page) chunk

Each `RAM ` chunk captures a single 16 KB RAM bank:

| Offset | Size | Field |
|---|---|---|
| 0 | 1 | Bank number (0–255 — supports up to 4 MB of RAM) |
| 1 | 1 | Flags | Bit 0: compressed (using the .Z80 RLE scheme); Bits 1–7: reserved |
| 2 | 2 | Page data length | The length of the page data that follows (may be < 16384 if compressed) |
| 4 | (length) | Page data | 16384 bytes uncompressed, or fewer if compressed |

A typical 128K snapshot has 8 `RAM ` chunks (one per bank). A Pentagon 1024 snapshot has 64. The compression scheme is the same as .Z80's (see [z80_format.md](z80_format.md) §5).

### 3.5 The AY16 (AY State) chunk

The `AY16` chunk captures the AY-3-8910 / YM2149 state:

| Offset | Size | Field |
|---|---|---|
| 0 | 1 | Currently-selected register (0–15) |
| 1 | 16 | All 16 register values |

For TurboSound (multiple AY chips), multiple `AY16` chunks appear, each tagged with a chip index (via a chunk extension or a separate `AYRX` chunk).

### 3.6 Peripheral chunks

The peripheral chunks (BETA, PLSB, DIVE, IF1, MULF, MOUS, JOYS) follow similar patterns: a fixed-layout structure capturing the relevant state. Their exact contents depend on the peripheral.

For example, the `BETA` chunk captures the Beta 128 FDC state:

| Offset | Size | Field |
|---|---|---|
| 0 | 1 | WD1793 command register |
| 1 | 1 | WD1793 status register |
| 2 | 1 | WD1793 track register |
| 3 | 1 | WD1793 sector register |
| 4 | 1 | WD1793 data register |
| 5 | 1 | FDC flags (motor on, etc.) |
| 6 | 1 | Currently-selected drive |
| 7 | 1 | Disk side |
| 8+ | ... | (Per-drive state, disk image references) |

This level of detail is what makes .SZX capable of capturing state that .SNA and .Z80 simply cannot.

---

## §4. Hardware Identification

The `CFGR` chunk's hardware ID byte identifies the source machine. The list is extensive and growing.

### 4.1 The standard hardware IDs

| ID | Hardware |
|---|---|
| 0 | 48K Spectrum |
| 1 | 48K Spectrum + Interface 1 |
| 2 | 48K Spectrum + MGT |
| 3 | 128K Spectrum |
| 4 | 128K Spectrum + Interface 1 |
| 5 | +2 (grey) |
| 6 | +2A / +3 |
| 7 | +3E (community upgrade) |
| 8 | Inves 48K+ (Spanish clone) |
| 9 | TK90X (Spanish/Brazilian clone) |
| 10 | TK95 (Spanish/Brazilian clone) |
| 11 | Ts2068 (Timex) |
| 12 | Pentagon 128 |
| 13 | Pentagon 512 |
| 14 | Pentagon 1024 |
| 15 | Scorpion 256 |
| 16 | Scorpion 1024 |
| 17 | Profi 512 |
| 18 | Kay 1024 |
| 19 | ATM Turbo 2 |
| 20 | ATM Turbo 3 |
| 21 | Sprinter |
| 22 | ZX Evolution |
| 23 | Chrome 48K (Chloe 140 SE) |
| 24 | Azurewrath (Spanish clone) |
| 25 | ZX-Uno |
| 26 | ZX Spectrum Next (with various configurations) |
| 27 | TS-Conf |
| 28+ | (Reserved for future hardware) |

A loader should accept any ID and, if it doesn't recognise the hardware, treat it as 48K with a warning (or refuse to load, depending on policy).

### 4.2 Hardware configuration extensions

For some hardware, the `CFGR` chunk includes extended configuration:

- **ZX Spectrum Next**: NextReg values, Layer 2 / sprite / tilemap enable flags, RAM configuration.
- **ZX Evolution**: BaseConf settings, TS-Conf enable, peripheral flags.
- **ATM Turbo**: Video mode, memory configuration.
- **Inves / TK90X / Ts2068**: Localised keyboard, ROM variant.

The exact extensions are documented in the ZEsarUX source code.

### 4.3 Why .SZX is good at hardware ID

The .SZX format's chunk-based design makes it well-suited to hardware identification:

- New hardware IDs can be added without breaking older loaders (they'll see an unknown ID and warn but continue).
- Hardware-specific configuration can be added as additional chunks (e.g., a `ZXRG` chunk for NextRegs) without bloating the main `CFGR` chunk.
- The format scales cleanly to new hardware (e.g., the ZX Spectrum Next, which was added in the late 2010s).

---

## §5. State Captured

This section enumerates exactly what .SZX captures, compared to .SNA and .Z80.

### 5.1 What .SZX captures that .SNA does not

| State | .SNA | .SZX |
|---|---|---|
| Z80 registers | ✅ | ✅ |
| Full RAM (48K) | ✅ | ✅ |
| 128K paging (`#7FFD`) | ✅ | ✅ |
| PC (explicit) | (on stack) | ✅ |
| Border colour | ❌ | ✅ |
| AY-3-8910 state | ❌ | ✅ |
| Hardware identification | ❌ | ✅ |
| MEMPTR (undocumented Z80 register) | ❌ | ✅ |
| +2A/+3 paging (`#1FFD`) | ❌ | ✅ |
| Russian clone state | ❌ | ✅ |
| T-state counter (within frame) | ❌ | ✅ |
| Beta 128 FDC state | ❌ | ✅ |
| +3 FDC state | ❌ | ✅ |
| Interface 1 state | ❌ | ✅ |
| Multiface state | ❌ | ✅ |
| Mouse / joystick state | ❌ | ✅ |

.SZX captures essentially everything that .SNA doesn't.

### 5.2 What .SZX captures that .Z80 v3 does not

| State | .Z80 v3 | .SZX |
|---|---|---|
| Z80 registers | ✅ | ✅ |
| Full RAM (any clone) | ✅ | ✅ |
| AY-3-8910 state | ✅ | ✅ |
| Hardware ID | ✅ | ✅ |
| MEMPTR | ✅ | ✅ |
| +2A/+3 paging | ✅ | ✅ |
| Russian clone state | ✅ | ✅ |
| T-state counter | ✅ | ✅ |
| **Beta 128 FDC internal registers** | ❌ | ✅ |
| **+3 FDC internal registers** | ❌ | ✅ |
| **DivIDE / DivMMC state** | ❌ | ✅ |
| **Interface 1 microdrive state** | ❌ | ✅ |
| **Multiface state** | ❌ | ✅ |
| **ZX Spectrum Next NextRegs** | ❌ | ✅ |
| **ZX Spectrum Next copper list** | ❌ | ✅ |
| **ZX Spectrum Next DMA state** | ❌ | ✅ |
| **TurboSound / TurboSound FM / MoonSound state** | ❌ | ✅ |
| **ESP / WiFi state** | ❌ | ✅ |

For modern emulators (especially ZEsarUX, CSpect for the Next, etc.), .SZX is the only format that can capture the full state.

### 5.3 Why this matters

For most use cases — running a 48K game — the extra state captured by .SZX doesn't matter. The game will run the same in .SNA, .Z80, or .SZX form.

For complex use cases, however, .SZX's extra state is essential:

- **Snapshotting mid-disk-operation**: .SZX captures the FDC state, so a disk operation can resume correctly.
- **Snapshotting Next software**: .SZX captures the NextRegs, copper, and DMA, all of which are essential for resuming Next software.
- **Snapshotting multi-chip sound**: .SZX captures the state of all sound chips in a TurboSound / MoonSound system.
- **Cycle-exact snapshots**: .SZX's T-state counter allows cycle-exact resumption, important for software with timing-sensitive code (e.g., demos with cycle-exact raster effects).
---

## §6. Writing an .SZX Loader

A reference loader in C-like pseudocode. The chunk-based structure makes the loader quite simple compared to .Z80's version-detection logic.

### 6.1 Main loader function

```c
typedef struct {
    // ... (Z80 registers, AY registers, peripheral state, etc.)
} SpectrumState;

int load_szx(const char *filename, SpectrumState *state) {
    FILE *f = fopen(filename, "rb");
    if (!f) return -1;

    // Read and verify the file header
    uint8_t header[8];
    if (fread(header, 1, 8, f) != 8 ||
        memcmp(header, "ZXST", 4) != 0) {
        fclose(f);
        return -1;  // Not an .SZX file
    }
    uint32_t version = header[4] | (header[5] << 8) |
                       (header[6] << 16) | (header[7] << 24);
    if (version != 1) {
        // Unknown version; proceed with caution or reject
    }

    // Read chunks until EOF
    while (!feof(f)) {
        uint8_t chunk_hdr[8];
        if (fread(chunk_hdr, 1, 8, f) != 8) break;

        char chunk_id[5];
        memcpy(chunk_id, chunk_hdr, 4);
        chunk_id[4] = '\0';

        uint32_t chunk_len = chunk_hdr[4] | (chunk_hdr[5] << 8) |
                             (chunk_hdr[6] << 16) | (chunk_hdr[7] << 24);

        // Read the chunk data
        uint8_t *chunk_data = malloc(chunk_len);
        fread(chunk_data, 1, chunk_len, f);

        // Dispatch based on chunk ID
        if (memcmp(chunk_id, "CFGR", 4) == 0) {
            apply_cfgr(state, chunk_data, chunk_len);
        } else if (memcmp(chunk_id, "Z80R", 4) == 0) {
            apply_z80r(state, chunk_data, chunk_len);
        } else if (memcmp(chunk_id, "RAM ", 4) == 0) {
            apply_ram_page(state, chunk_data, chunk_len);
        } else if (memcmp(chunk_id, "AY16", 4) == 0) {
            apply_ay16(state, chunk_data, chunk_len);
        } else if (memcmp(chunk_id, "BETA", 4) == 0) {
            apply_beta(state, chunk_data, chunk_len);
        } else if (memcmp(chunk_id, "ZXRG", 4) == 0) {
            apply_zxrg(state, chunk_data, chunk_len);
        }
        // else: unknown chunk — ignore (already read the data, just free it)

        free(chunk_data);
    }

    fclose(f);
    return 0;
}
```

The key insight is that **unknown chunks are simply skipped**. The loader does not need to know about every chunk type — it only needs to handle the ones it cares about, and the chunk-length field lets it skip the rest.

### 6.2 Applying a chunk

Each chunk-application function (`apply_cfgr`, `apply_z80r`, etc.) takes the chunk data and updates the `SpectrumState`. Here's an example for `Z80R`:

```c
void apply_z80r(SpectrumState *state, uint8_t *data, uint32_t len) {
    if (len < 31) return;  // Truncated chunk — ignore
    state->AF     = data[0]  | (data[1]  << 8);
    state->BC     = data[2]  | (data[3]  << 8);
    state->DE     = data[4]  | (data[5]  << 8);
    state->HL     = data[6]  | (data[7]  << 8);
    state->AF_alt = data[8]  | (data[9]  << 8);
    state->BC_alt = data[10] | (data[11] << 8);
    state->DE_alt = data[12] | (data[13] << 8);
    state->HL_alt = data[14] | (data[15] << 8);
    state->IX     = data[16] | (data[17] << 8);
    state->IY     = data[18] | (data[19] << 8);
    state->SP     = data[20] | (data[21] << 8);
    state->PC     = data[22] | (data[23] << 8);
    state->I      = data[24];
    state->R      = data[25] & 0x7F;
    state->R7     = (data[25] >> 7) & 1;
    state->IFF1   = data[26] & 1;
    state->IFF2   = data[27] & 1;
    state->IM     = data[28] & 3;
    state->MEMPTR = data[29] | (data[30] << 8);
}
```

The length check at the top is important — it allows the loader to gracefully handle truncated or malformed chunks.

### 6.3 Applying a RAM page

```c
void apply_ram_page(SpectrumState *state, uint8_t *data, uint32_t len) {
    if (len < 4) return;  // Truncated
    uint8_t  bank_num = data[0];
    uint8_t  flags    = data[1];
    uint16_t data_len = data[2] | (data[3] << 8);
    uint8_t *page_data = data + 4;

    uint8_t bank_buf[16384];
    if (flags & 1) {
        // Compressed page (using .Z80 RLE scheme)
        decompress_z80_page(page_data, data_len, bank_buf, 16384);
    } else {
        // Uncompressed page
        if (data_len != 16384) return;  // Wrong size
        memcpy(bank_buf, page_data, 16384);
    }

    set_ram_bank(state, bank_num, bank_buf);
}
```

Note that .SZX reuses the .Z80 RLE compression scheme (see [z80_format.md](z80_format.md) §5). This is a deliberate choice — the scheme is well-understood and well-tested, and reusing it avoids the need to define a new compression format.

### 6.4 Robustness considerations

A production-quality .SZX loader should:

- Validate the file header (magic "ZXST", version 1).
- Handle truncated chunks gracefully (don't crash, just skip).
- Handle unknown chunks by skipping them (not aborting).
- Handle the case where the same chunk type appears multiple times (e.g., multiple RAM pages — apply them in order).
- Validate that the hardware ID is known; warn (don't abort) if it isn't.
- Validate that the necessary chunks are present (at minimum: `CFGR`, `Z80R`, and at least one `RAM ` page).

---

## §7. Extensibility and Custom Chunks

One of .SZX's great strengths is its extensibility. This section describes how to add new chunk types.

### 7.1 The "private use" chunk IDs

If you are an emulator author and want to add a new chunk type for your emulator's private state, you have two options:

1. **Register a new standard chunk ID** with the ZEsarUX project. This makes your chunk part of the official .SZX spec.
2. **Use a "private use" chunk ID** (with an `X` prefix, like `XMYE` for "MY Emulator"). Other emulators will skip it, but your emulator will recognise it.

The convention is that chunk IDs starting with `X` are private to a specific emulator. Standard chunk IDs (without the `X` prefix) should be registered to avoid collisions.

### 7.2 Adding a new standard chunk type

To add a new standard chunk type:

1. **Choose a chunk ID**. The ID must be 4 ASCII characters, typically mnemonic (e.g., `BETA` for the Beta 128 disk interface). Avoid IDs that are already in use.
2. **Define the chunk data layout**. Specify the byte-by-byte layout of the chunk's data.
3. **Document the chunk** in the .SZX spec (currently maintained as part of the ZEsarUX documentation).
4. **Implement chunk reading and writing** in your emulator.

Once your chunk type is in use, other emulator authors can choose to support it (or skip it).

### 7.3 Why this matters

The chunk-based extensibility is what makes .SZX future-proof. As new Spectrum hardware is developed (e.g., the ZX Spectrum Next, new Russian clones, new peripherals), new chunk types can be added to capture their state. Older loaders will simply skip the new chunks and continue to load the rest of the snapshot — degraded but functional.

This is in stark contrast to .SNA and .Z80, where new features require new versions of the format, and old loaders either fail outright or silently corrupt the snapshot.

---

## §8. Compatibility Across Emulators

| Emulator | .SZX load | .SZX save | Notes |
|---|---|---|---|
| ZEsarUX | ✅ | ✅ | Native format; full support for all standard chunks |
| Fuse | ✅ | ✅ | Supports the common chunks (CFGR, Z80R, RAM, AY16); may skip exotic ones |
| Spectaculator | ✅ | ❌ | Loads .SZX but does not save as .SZX |
| CSpect | ✅ | ✅ | Especially good for ZX Spectrum Next state (ZXRG, COPR, DMA chunks) |
| UnrealSpeccy | ✅ | ✅ | Russian clone support |
| ZXMAK2 | ✅ | ✅ | Russian clone support |
| EightyOne | ⚠️ | ❌ | Partial support |
| Klive | ⚠️ | ❌ | Partial support (via import filter) |

In practice, .SZX is most useful when both you and your target audience are using modern emulators (ZEsarUX, Fuse, CSpect). For sharing snapshots with users of older or simpler emulators, .Z80 or .SNA remains more compatible.

### 8.1 Compatibility quirks

- **Chunk interpretation differs** between emulators. For example, the `CFGR` chunk's extended configuration bytes are interpreted differently by different emulators for the same hardware. Test your .SZX files across emulators if compatibility matters.
- **Some chunks are emulator-specific**. Chunks starting with `X` (e.g., `XZUE` for ZEsarUX-specific extensions) are not portable between emulators.
- **Compression compatibility**: All emulators support the .Z80 RLE compression scheme used by `RAM ` chunks, but some older emulators do not handle the `0xED 0xED 0x00 0xED` edge case correctly (see [z80_format.md](z80_format.md) §5.4).

---

## §9. Comparison with .SNA and .Z80

| Aspect | .SNA | .Z80 | .SZX |
|---|---|---|---|
| Origin | 1992 (JPP) | 1994 (Z80 emulator) | 2005+ (ZEsarUX) |
| Layout | Fixed header | Fixed header (with version detection) | Chunk-based (IFF-like) |
| Extensibility | None (only via file size) | Limited (v1→v2→v3) | Unlimited (new chunks) |
| State captured | Minimal | Moderate | Comprehensive |
| File size (typical) | 48 KB (48K) | 10–48 KB (compressed) | Variable (depends on chunks) |
| Loader complexity | Very simple | Moderate | Simple (skip unknown chunks) |
| Adoption | Universal | Universal | Modern emulators |
| Best for | Maximum compat | General-purpose | Maximum fidelity |

**When to use .SZX**:

- **Snapshotting complex state** that .SNA/.Z80 cannot capture: FDC state, peripheral state, multi-chip sound, ZX Spectrum Next state.
- **ZEsarUX-native workflows**: When using ZEsarUX, .SZX is the natural format.
- **Cycle-exact timing**: For demos and timing-sensitive software, .SZX's T-state counter allows cycle-exact resumption.
- **Future-proofing**: For archival purposes, .SZX captures the most state and is the most future-proof.

**When to use .SNA or .Z80 instead**:

- **Sharing with maximum compatibility**: Not every emulator supports .SZX.
- **Simple 48K software**: Where the extra state doesn't matter, .SNA is simpler and more universally supported.

---

## §10. Cross-References

### 10.1 Within the snapshots section

- **[sna_format.md](sna_format.md)** — The simplest format. Read this first if you're new to snapshots.
- **[z80_format.md](z80_format.md)** — The most widely-supported rich format. Shares the compression scheme used by .SZX's `RAM ` chunks.
- **[rzx_format.md](rzx_format.md)** — The input recording format, used for replay rather than static snapshots.

### 10.2 Outside the snapshots section

- **[../../04_operating_systems/nextzxos.md](../../04_operating_systems/nextzxos.md)** — The ZX Spectrum Next's OS, captured in detail by .SZX's `ZXRG`, `COPR`, and `DMA` chunks.
- **[../../04_operating_systems/evo_os.md](../../04_operating_systems/evo_os.md)** — The ZX Evolution's BIOS/OS, captured by .SZX's `CFGR` extensions for the Evo hardware.

### 10.3 External resources

- **The ZEsarUX source code** (`zesarux/src`) — The canonical reference for the .SZX format, including all standard chunk types.
- **The Fuse emulator source code** — A clean reference loader for the common .SZX chunks.

---

## License

This document is licensed under **Creative Commons Attribution-ShareAlike 4.0 International** (CC BY-SA 4.0). You are free to share and adapt this material, provided you give appropriate credit, indicate changes, and distribute derivative works under the same licence.
