[← Home](../../README.md) · [I/O](../README.md) · [Snapshots](README.md)

# The .Z80 Snapshot Format

The .SNA format (see [sna_format.md](sna_format.md)) is the simplest snapshot format, but its limitations — no AY state, no support for 128K clones, no metadata — became a problem as emulators grew more sophisticated. The **.Z80 format** was created in 1994 by **Glen Lleston** (also known as "Grendel") for the **Z80** emulator — a DOS-based Spectrum emulator that was widely popular in the late 1990s. The .Z80 format addressed the major limitations of .SNA and quickly became the second de facto snapshot standard.

The .Z80 format has evolved through three versions: v1 (the original, 48K only), v2 (added 128K support), and v3 (added support for Russian clones, AY state, +3 paging, and more). Each version is backward-compatible with the previous — a v1 file can be loaded by a v3-aware loader — but each version also adds new fields and capabilities.

Today, .Z80 is the most widely-supported "rich" snapshot format. Every major emulator supports it, and most online software archives offer .Z80 alongside .SNA. For most use cases beyond simple 48K games, .Z80 is the preferred format.

This article covers the .Z80 format in detail: its history, the byte-level layout of all three versions, the compression scheme, the hardware identification system, what state is captured, how to write a loader, and the gotchas. For the simpler .SNA format, see [sna_format.md](sna_format.md). For the even-more-capable .SZX format, see [szx_format.md](szx_format.md).

---

## Roadmap

1. **What the .Z80 format is** — history, scope, why it was created
2. **The v1 .Z80 format** — original 30-byte header, 48K only
3. **The v2 .Z80 format** — 128K support, extended header
4. **The v3 .Z80 format** — full hardware identification, AY state, peripherals
5. **The compression scheme** — run-length encoding via the 0xED 0xED marker
6. **Hardware identification** — the hardware ID byte and its values
7. **Writing a .Z80 loader** — reference loader implementation
8. **Compatibility and quirks** — emulator-specific behaviours
9. **Comparison with .SNA and .SZX** — when to use which
10. **Cross-references** — where to go next

---

## §1. What the .Z80 Format Is

### 1.1 Origins

The .Z80 format was created in 1994 by **Glen Lleston** for his **Z80** emulator (sometimes called "Z80 by Grendel"), a popular DOS-based Spectrum emulator. Lleston wanted a snapshot format that could capture more state than .SNA — particularly the AY sound chip state, which .SNA lacked — and that could support the 128K Spectrum, which .SNA's original 48K-only format did not.

The .Z80 emulator went through several major versions (Z80 v0.1, v0.2, ..., through to Z80 v4.0 in 2000), and the snapshot format evolved with it:

- **v1 (1994)**: 48K only. 30-byte header. Optionally compressed RAM.
- **v2 (1996)**: 128K support. Extended header (additional 23 bytes for a total of 53 bytes). Stores all 8 RAM banks.
- **v3 (2000)**: Full hardware identification. Extended header again. Added AY state, +3 paging port, IF1 state, Multiface state, keyboard state, and support for many clone machines.

Each version is **backward compatible** with the previous: a v1-aware loader can load v1 files; a v2-aware loader can load v1 and v2 files; a v3-aware loader can load all three.

### 1.2 Scope

A .Z80 file contains:

- A **header** (30 bytes for v1, 55 bytes for v2/v3) with all Z80 register values, hardware identification, and additional state.
- The **RAM contents**, optionally compressed via a simple run-length encoding scheme.
- Optional **additional blocks** (v3 only) for AY state, peripheral state, etc.

Unlike .SNA, .Z80 captures:

- The **AY-3-8910 / YM2149 sound chip state** (all 14 register values, plus the currently-selected register).
- The **+2A/+3 paging port** value (`#1FFD`).
- The **hardware identification** — which machine the snapshot is from (48K, 128K, +3, Pentagon, etc.).
- Various **peripheral states** — Interface 1, Multiface, Kempston mouse, etc.
- The **program counter** explicitly (not relying on the stack-based trick used by .SNA).

This makes .Z80 substantially more capable than .SNA, at the cost of more complexity in the loader.

### 1.3 Why .Z80 matters

.Z80 matters because it is the **most widely-supported rich snapshot format**. Every emulator supports it (just as every emulator supports .SNA), and unlike .SNA, it captures enough state to faithfully resume the vast majority of Spectrum software — including 128K software, AY-using software, and even Russian clone software.

The format is also the **canonical format for archiving** Spectrum software. Sites like World of Spectrum prefer .Z80 for distribution because it preserves more information.

### 1.4 Why .Z80 has three versions

The .Z80 format's three versions reflect the evolution of Spectrum emulation:

- **1994 (v1)**: Spectrum emulation was dominated by 48K. A simple format was sufficient.
- **1996 (v2)**: 128K emulation became common. The format needed to capture the additional 80 KB of RAM and the paging port state.
- **2000 (v3)**: Russian clone support, AY state preservation, and peripheral state all became important. The format was extended again.

A future v4 has been discussed (to capture the state of even more peripherals, such as the +3 FDC, in full detail), but the .SZX format has largely taken over this niche.

---

## §2. The v1 .Z80 Format

The v1 format is the original .Z80 format, designed for 48K snapshots. The file consists of a 30-byte header followed by optionally-compressed 48 KB of RAM.

### 2.1 Header layout (30 bytes)

The v1 .Z80 header is 30 bytes long. All multi-byte register values are stored **little-endian** (low byte first, then high byte) — the same convention as .SNA.

| Offset | Size | Field | Notes |
|---|---|---|---|
| 0 | 1 | A | Main accumulator |
| 1 | 1 | F | Main flags register |
| 2 | 2 | BC | Main BC pair (C low, B high) |
| 4 | 2 | HL | Main HL pair (L low, H high) |
| 6 | 2 | PC | **Program counter**. If 0x0000, this is a v2/v3 file — see §2.3 |
| 8 | 2 | SP | Stack pointer |
| 10 | 2 | IY | IY pair |
| 12 | 2 | IX | IX pair |
| 14 | 1 | IFF1 | Interrupt flip-flop 1 (bit 0 = enabled) |
| 15 | 1 | IFF2 | Interrupt flip-flop 2 (bit 0 = set) |
| 16 | 1 | R | Refresh register. Bit 7 = manual R7 bit; bits 0–6 = auto-incremented value |
| 17 | 2 | AF' | Alternate AF pair (F' low, A' high) |
| 19 | 2 | BC' | Alternate BC pair (C' low, B' high) |
| 21 | 2 | HL' | Alternate HL pair (L' low, H' high) |
| 23 | 2 | DE' | Alternate DE pair (E' low, D' high) |
| 25 | 2 | DE | Main DE pair (E low, D high) |
| 27 | 1 | Border colour | Bits 0–2: border colour (0–7). Other bits reserved |
| 28 | 1 | Flags byte | Bit 0: AY in use; Bit 1: (v2+) mod_128 rom paged; Bit 3: 48K ROM modified flag; Bit 4: compressed RAM flag; Bit 5: 128K paging locked; Bit 6: (v3) later; Bit 7: output to video splitter port |
| 29 | 1 | Sound mode byte | Bits 0–1: sound mode (0=none, 1=beeper, 2=AY, 3=both). Bit 2: full ROM mod info follows. Bits 3–7: reserved |

**Field ordering convention**: Note that the alternate register pairs are stored **before** the main DE pair. This is a quirk of the v1 layout, preserved in all later versions for compatibility.

### 2.2 PC field — explicit, not stack-based

Unlike .SNA, the .Z80 format stores PC **explicitly** in the header (at offset 6). This avoids the .SNA format's reliance on PC being on the stack, which can be fragile (see [sna_format.md](sna_format.md) §7.1). The loader simply sets `z80.PC = header.PC` after loading — no `RET` trick is needed.

The exception to this rule is when PC is **0x0000**, which is used as a sentinel to indicate a v2 or v3 file (see §2.3 below). A real PC value is never 0x0000 because address 0x0000 is ROM.

### 2.3 The PC=0 trick for v2/v3 detection

The most important rule of the .Z80 format is: **if bytes 6 and 7 (the PC field) are both zero, the file is v2 or v3, not v1**.

Why? Because a real PC of 0x0000 is essentially impossible — no Spectrum program executes code at address 0x0000 (which is ROM). The Z80 emulator's authors used this "impossible" value as a sentinel to indicate that more header data follows.

When a loader sees PC=0x0000, it should:

1. Treat the file as v2 or v3.
2. Look at the next 2 bytes (bytes 30–31) for the **additional header length** (typically 23 for v2, 54 or 55 for v3, plus variable-length extensions).
3. Read the additional header and apply it.

This is the key mechanism for backward compatibility: a v1-only loader will see PC=0, attempt to resume at 0x0000, and either crash or do something obviously wrong — but it will not silently corrupt data.

### 2.4 RAM data follows the header

After the 30-byte header (v1) or the extended header (v2/v3), the RAM data follows. In v1, this is exactly 48 KB (49152 bytes) of RAM, optionally compressed (see §5).

The RAM data covers addresses `#4000`–`#FFFF` — the same 48 KB as .SNA. The ROM contents are not stored (the standard 48K ROM is assumed).
---

## §3. The v2 .Z80 Format

The v2 format extends v1 to support the 128K Spectrum and its Russian clones. The header is extended with a 23-byte additional block, and the RAM dump includes all 8 RAM banks.

### 3.1 Detection: PC=0x0000 + extended header length

A v2 file is detected by:

1. The v1 PC field (offsets 6–7) is `0x0000`.
2. The 2 bytes following the 30-byte v1 header (offsets 30–31) give the **additional header length**: a 16-bit little-endian value. For v2, this is typically **23** (0x17 0x00).

When the loader sees PC=0x0000, it reads the next 2 bytes, then reads that many more bytes as the v2 extension header.

### 3.2 v2 extension header layout (23 bytes)

The v2 extension header sits at offsets 30–52 of the file (after the 30-byte v1 header). It is 23 bytes long:

| Offset (from file start) | Size | Field | Notes |
|---|---|---|---|
| 30 | 2 | Extension header length | For v2, this is 0x0017 (23). For v3, it's 0x0036 (54) or 0x0037 (55) |
| 32 | 2 | PC | **The real program counter** (replaces the v1 sentinel at offset 6) |
| 34 | 1 | Hardware ID | 0=48K, 1=48K+IF1, 2=48K+MGT, 3=128K, 4=128K+IF1, 5=128K+MGT, 6=+3 (v3 extended this) |
| 35 | 1 | Extended hardware flags (v2) | Bits 0–6: IF1 ROM paged; Bits 7: issue 2 emulation |
| 36 | 1 | Modified ROM flag | 0x00=standard, 0xFF=modified (or use Interface 1 / custom ROM) |
| 37 | 1 | AY-3-8910 current register | The currently-selected AY register (0–15) |
| 38 | 16 | AY-3-8910 register values | All 16 AY register values (only 14 are defined; bits in unused registers are ignored) |
| 54 | 1 | (Final byte) | Often 0x00. Used as a padding/version marker |

The extension header provides all the information needed to resume a 128K machine: PC, hardware identification, AY state, and (in the additional RAM data following) all 8 RAM banks.

### 3.3 v2 RAM layout and per-page header

After the 53-byte header (30-byte v1 + 23-byte extension), the RAM data follows. For 128K snapshots, this is **16384 bytes for each of 8 banks**.

For a 128K Spectrum snapshot, the 8 banks are stored in this order:

| Bank | Address | Notes |
|---|---|---|
| 5 | `#4000`–`#7FFF` | The screen bank |
| 2 | `#8000`–`#BFFF` | The work-area bank |
| 0 (paged at `#C000`) | `#C000`–`#FFFF` | The currently-paged bank |
| 1, 3, 4, 6, 7 | (not in address space) | The remaining banks |

**Important difference from .SNA**: in .SNA, the 8 banks are stored as a fixed sequence (5, 2, 0, 1, 3, 4, 6, 7) without per-bank metadata. In .Z80 v2/v3, the banks are stored as **one or more "pages"**, each preceded by a 3-byte header that explicitly identifies the bank number and length. This paged-storage scheme is much more flexible — see the per-page header structure below.

#### Per-page header (3 bytes, preceding each page)

| Offset | Size | Field |
|---|---|---|
| 0 | 1 | Bank number (5, 2, 0, 1, 3, 4, 6, 7 for the 8 banks; or other values for clones with extended memory) |
| 1 | 2 | Page length (little-endian). If 0xFFFF, the page is uncompressed 16384 bytes. Otherwise, the page is compressed and this gives the compressed length |

After each page header, the page data follows (either 16384 bytes uncompressed, or the compressed length).

This paged-storage scheme is much more flexible than .SNA's fixed-layout scheme. It allows:

- **Compression per-page**: each bank can be compressed or uncompressed independently.
- **Skipped banks**: a snapshot can omit banks that are not in use (though this is rare).
- **Extended memory**: snapshots of clones with more than 128K (e.g., the Pentagon 1024, the Scorpion 256, the +2A/+3's special modes) can store the additional banks.

For a standard 128K snapshot, all 8 banks are stored, typically in the order 5, 2, 0, 1, 3, 4, 6, 7.

### 3.4 What v2 adds over v1

The v2 extension adds:

- **PC field**: now properly captured (the v1 sentinel is replaced).
- **Hardware ID**: identifies the source machine (48K, 128K, +3, etc.).
- **AY-3-8910 state**: all 16 register values plus the currently-selected register.
- **Modified ROM flag**: indicates if the snapshot's source machine used a non-standard ROM.
- **IF1 / IF2 state**: brief indication of Interface 1 presence and state.

This is enough to faithfully resume most 128K Spectrum software, including AY-using software.

---

## §4. The v3 .Z80 Format

The v3 format extends v2 to support Russian clones, the +3's special paging modes, Multiface state, and more peripheral state. The extension header grows to 54 (or 55) bytes.

### 4.1 Detection: longer extension header

A v3 file is detected by:

1. The v1 PC field is `0x0000`.
2. The extension header length (offsets 30–31) is **0x0036 (54)** or **0x0037 (55)**.

### 4.2 v3 extension header layout

The v3 extension header is 54 bytes long (some sources say 55 — there's a 1-byte padding ambiguity in early v3 files). It extends the v2 layout:

| Offset (from file start) | Size | Field | Notes |
|---|---|---|---|
| 30 | 2 | Extension header length | 54 (0x0036) or 55 (0x0037) |
| 32 | 2 | PC | The real program counter |
| 34 | 1 | Hardware ID | Extended list: 0–6 same as v2; 7=Spectrum +3E; 8=+3 Spanish; 9=Pentagon 128; 10=Scorpion 256; 11=Profi 512; 12=Kay 1024; 13=ZS Scorpion 256; ... up to about 20+ |
| 35 | 1 | Extended hardware flags | Bits 0–6: IF1 ROM paged; Bit 7: issue 2 emulation |
| 36 | 1 | Modified ROM flag | |
| 37 | 1 | AY-3-8910 current register | |
| 38 | 16 | AY-3-8910 register values | |
| 54 | 1 | Low byte of `#7FFD` paging port value | The 128K paging state |
| 55 | 1 | (v3+) High byte — usually 0xFF if `#7FFD` was last set, or 0x00 if `#1FFD` modifier | |
| 56 | 1 | `#1FFD` paging port value (for +2A/+3 and clones) | Captures the +3's special paging mode |
| 57 | 1 | ROM paged flag (IF1, IF2, etc.) | Which ROM is at `#0000`–`#3FFF` |
| 58–59 | 2 | AY-3-8910 register (low 8 bits of the selected register, plus chip select for TurboSound) | |
| 60–61 | 2 | Low T-state counter | The current T-state within the frame (0–69887 for 48K, 0–70908 for 128K, etc.) |
| 62–63 | 2 | High T-state counter | (For emulators that use a 32-bit counter) |
| 64 | 1 | Spectator flag | If non-zero, the snapshot was taken in "spectator mode" (some emulators use this) |
| 65 | 1 | MEMPTR / W register low byte | The undocumented Z80 W register (low 8 bits) |
| 66 | 1 | MEMPTR / W register high byte | The undocumented Z80 W register (high 8 bits) |
| 67–68 | 2 | (Flags / unused) | |
| 69–70 | 2 | Last OUT to `#FF` (Pentagon / Russian clones) | |
| 71 | 1 | Joystick type | 0=none, 1=Kempston, 2=Sinclair 1, 3=Sinclair 2, etc. |
| 72 | 1 | Joystick modifications | |
| 73–83 | 11 | (Reserved / extended ROM info / CHAN interface) | Various fields whose interpretation varies by emulator |

The v3 header is rich enough to capture the state of nearly any Spectrum clone, including the +3's special paging modes, the Pentagon's extended memory, and even the undocumented Z80 MEMPTR register.

### 4.3 What v3 adds over v2

The v3 extension adds:

- **Hardware ID extensions**: Russian clones (Pentagon, Scorpion, Profi, Kay) and +3E.
- **`#7FFD` and `#1FFD` paging state**: full capture of the +3's four paging modes.
- **MEMPTR/W register**: the undocumented Z80 register, important for some demos and copy protection.
- **T-state counter**: the current position within the video frame, allowing cycle-exact resumption.
- **`#FF` port state**: the Pentagon/Russian-clone extended paging port.
- **Joystick type and modifications**: which joystick interface is connected and any emulator-specific joystick patches.

With v3, the .Z80 format can faithfully resume essentially any Spectrum software on any Spectrum clone.

---

## §5. The Compression Scheme

The .Z80 format supports optional compression of the RAM data, using a simple **run-length encoding (RLE) scheme**. The compression is applied independently to each RAM page (in v2/v3) or to the entire RAM block (in v1).

### 5.1 The 0xED 0xED marker

The compression scheme is based on the byte sequence **0xED 0xED** as a marker. The choice of marker is not arbitrary: `0xED 0xED` is the prefix for two consecutive `ED` opcode prefixes in the Z80 instruction set, which is a "redundant" sequence that almost never appears in real Z80 code (real code uses at most one `ED` prefix). This makes it a safe choice for a marker.

### 5.2 Encoding

The compression works as follows. The encoder scans the RAM data byte-by-byte:

- **For a run of 1–4 identical bytes**: store them verbatim (no compression).
- **For a run of 5+ identical bytes**: emit `0xED 0xED` followed by the count byte (1 byte) followed by the value byte (1 byte). The count is the number of repetitions minus 1.
- **For a literal `0xED 0xED` sequence in the data**: emit `0xED 0xED 0x00 0xED`. The count byte `0x00` is interpreted as "1 repetition of 0xED" — which, when decoded, produces a single 0xED. The decoder will then re-emit the second 0xED verbatim.

The maximum run that can be encoded in a single marker is 256 bytes (count byte 0xFF = 255 repetitions of one value).

### 5.3 When compression is used

In v1, the entire 48 KB RAM is compressed as a single block. The flags byte at offset 28, bit 4 indicates whether compression is in use.

In v2/v3, each RAM page can be compressed independently. The page's "length" field in the page header is:

- `0xFFFF` (65535): page is uncompressed, 16384 bytes follow.
- Any other value: page is compressed, that many bytes follow.

Most emulators compress by default when saving .Z80 files, since Spectrum RAM often contains large runs of zero bytes (especially in the upper memory banks, which are usually unused). Compression typically reduces a 48K snapshot from 49179 bytes to about 10–30 KB.

### 5.4 Decoder pseudocode

```c
void decompress_z80_page(uint8_t *in, size_t in_len, uint8_t *out, size_t out_len) {
    size_t in_pos = 0, out_pos = 0;
    while (in_pos < in_len && out_pos < out_len) {
        if (in_pos + 1 < in_len && in[in_pos] == 0xED && in[in_pos+1] == 0xED) {
            // Compressed run
            uint8_t count = in[in_pos + 2];
            uint8_t value = in[in_pos + 3];
            for (int i = 0; i <= count; i++) {  // <= because count is "reps - 1"
                if (out_pos >= out_len) break;
                out[out_pos++] = value;
            }
            in_pos += 4;
        } else {
            // Literal byte
            out[out_pos++] = in[in_pos++];
        }
    }
}
```

Note the `i <= count` in the loop — this is because the count byte stores "repetitions minus 1" (so a single byte is encoded with count=0).

### 5.5 Encoder pseudocode

```c
void compress_z80_page(uint8_t *in, size_t in_len, uint8_t *out, size_t *out_len) {
    size_t in_pos = 0, out_pos = 0;
    while (in_pos < in_len) {
        // Count the run length starting at in_pos
        size_t run = 1;
        while (in_pos + run < in_len && in[in_pos + run] == in[in_pos] && run < 256) {
            run++;
        }
        if (run >= 5) {
            // Emit compressed marker
            out[out_pos++] = 0xED;
            out[out_pos++] = 0xED;
            out[out_pos++] = run - 1;
            out[out_pos++] = in[in_pos];
            in_pos += run;
        } else if (in[in_pos] == 0xED && in_pos + 1 < in_len && in[in_pos + 1] == 0xED) {
            // Special case: literal 0xED 0xED in the source
            out[out_pos++] = 0xED;
            out[out_pos++] = 0xED;
            out[out_pos++] = 0;     // count = 0 means 1 repetition
            out[out_pos++] = 0xED;
            in_pos++;  // only advance one; the next iteration handles the second 0xED
        } else {
            // Emit literal byte
            out[out_pos++] = in[in_pos++];
        }
    }
    *out_len = out_pos;
}
```

The encoder's special case for literal `0xED 0xED` sequences is important: without it, the decoder would interpret the literal sequence as a compression marker, corrupting the data. This case is rare in real Spectrum RAM (it only occurs in code that uses consecutive `ED` opcodes), but it must be handled.
---

## §6. Hardware Identification

The v2/v3 hardware ID byte (offset 34) is one of the most important fields in the .Z80 format. It tells the loader which machine the snapshot was taken on, which determines:

- The ROM to use (48K ROM, 128K ROM, +3 ROM, Pentagon ROM, etc.).
- The memory layout (number of RAM banks, paging ports).
- The video timing (number of T-states per frame, contention pattern).
- The sound chip variant (AY-3-8910 vs YM2149, sound chip frequency).

### 6.1 The standard hardware IDs (v2)

The original v2 hardware IDs:

| ID | Hardware | Notes |
|---|---|---|
| 0 | 48K Spectrum | The original Sinclair 48K |
| 1 | 48K Spectrum + Interface 1 | With the Microdrive / ZX Net ROM |
| 2 | 48K Spectrum + MGT | With the MGT (Plus D / Discovery) disk interface |
| 3 | 128K Spectrum | The "toastrack" |
| 4 | 128K Spectrum + Interface 1 | |
| 5 | 128K Spectrum + MGT | |
| 6 | +3 Spectrum | With the +3 DOS ROM |

### 6.2 Extended hardware IDs (v3)

The v3 format extends the hardware ID list to include Russian clones and Amstrad variants:

| ID | Hardware | Notes |
|---|---|---|
| 7 | Spectrum +3E | The community-developed +3E ROM upgrade |
| 8 | Spectrum +3 (Spanish) | Spanish-language +3 |
| 9 | Pentagon 128 | The standard Russian clone |
| 10 | Scorpion 256 | Russian clone with extended memory |
| 11 | Scorpion 1024 | |
| 12 | Profi 512 | |
| 13 | Kay 1024 | |
| 14 | Pentagon 512 | |
| 15 | Pentagon 1024 | |
| 16 | Sprinter | Russian FPGA-based Spectrum |
| 17 | ATM Turbo 2 | Russian clone with extended video modes |
| 18 | ATM Turbo 3 | |
| 19 | ZX Evolution | The modern Russian FPGA-Spectrum |
| 20 | TS-Conf | The TS-Conf extended graphics configuration |

Any hardware ID > 20 is reserved for future expansion. Loaders should treat unknown IDs as "48K" with a warning, or refuse to load.

### 6.3 The hardware ID's role in loading

When the loader reads the hardware ID, it:

1. Configures the emulator for the corresponding machine (set the ROM, memory model, timing, etc.).
2. Reads the paging port values (`#7FFD`, `#1FFD`, `#EFF7`, `#FF` — whichever are relevant for the machine).
3. Loads the RAM pages into the corresponding banks.

If the loader does not support the specified hardware, it should refuse to load rather than silently misinterpret the snapshot.

---

## §7. Writing a .Z80 Loader

This is a reference loader in C-like pseudocode. It handles all three versions.

### 7.1 Main loader function

```c
typedef struct {
    // ... (Z80 registers, AY registers, etc.)
} SpectrumState;

int load_z80(const char *filename, SpectrumState *state) {
    FILE *f = fopen(filename, "rb");
    if (!f) return -1;

    // Read the 30-byte v1 header
    uint8_t v1_header[30];
    fread(v1_header, 1, 30, f);

    // Check the PC sentinel
    uint16_t pc = v1_header[6] | (v1_header[7] << 8);

    if (pc != 0) {
        // v1 file: 48K, no extension header
        return load_v1_z80(f, v1_header, state);
    }

    // v2 or v3: read the extension header length
    uint8_t ext_len_bytes[2];
    fread(ext_len_bytes, 1, 2, f);
    uint16_t ext_len = ext_len_bytes[0] | (ext_len_bytes[1] << 8);

    // Read the extension header
    uint8_t ext_header[55];  // up to 55 bytes
    fread(ext_header, 1, ext_len, f);

    if (ext_len == 23) {
        // v2 file
        return load_v2_z80(f, v1_header, ext_header, state);
    } else if (ext_len >= 54) {
        // v3 file
        return load_v3_z80(f, v1_header, ext_header, ext_len, state);
    } else {
        // Unknown version
        fclose(f);
        return -1;
    }
}
```

### 7.2 v1 loader

```c
int load_v1_z80(FILE *f, uint8_t *hdr, SpectrumState *state) {
    // Apply the v1 header
    state->A      = hdr[0];
    state->F      = hdr[1];
    state->BC     = hdr[2] | (hdr[3] << 8);
    state->HL     = hdr[4] | (hdr[5] << 8);
    state->PC     = hdr[6] | (hdr[7] << 8);
    state->SP     = hdr[8] | (hdr[9] << 8);
    state->IY     = hdr[10] | (hdr[11] << 8);
    state->IX     = hdr[12] | (hdr[13] << 8);
    state->IFF1   = hdr[14] & 1;
    state->IFF2   = hdr[15] & 1;
    state->R      = hdr[16] & 0x7F;
    state->R7     = (hdr[16] >> 7) & 1;
    state->AF_alt = (hdr[17]) | (hdr[18] << 8);
    state->BC_alt = hdr[19] | (hdr[20] << 8);
    state->HL_alt = hdr[21] | (hdr[22] << 8);
    state->DE_alt = hdr[23] | (hdr[24] << 8);
    state->DE     = hdr[25] | (hdr[26] << 8);
    state->border = hdr[27] & 7;
    int compressed = (hdr[28] >> 4) & 1;
    int ay_in_use = hdr[28] & 1;

    // Set up the 48K hardware
    configure_48k(state);

    // Read the RAM (optionally compressed)
    uint8_t ram_buf[49152];
    if (compressed) {
        // Decompress from file
        decompress_z80_stream(f, ram_buf, 49152);
    } else {
        fread(ram_buf, 1, 49152, f);
    }

    // Copy RAM into the Spectrum's address space
    memcpy(state->ram_48k, ram_buf, 49152);

    fclose(f);
    return 0;
}
```

### 7.3 v3 loader (v2 is similar but without some fields)

```c
int load_v3_z80(FILE *f, uint8_t *v1_hdr, uint8_t *ext, uint16_t ext_len, SpectrumState *state) {
    // Apply the v1 header (same as v1 loader)
    apply_v1_header(state, v1_hdr);

    // Apply the v2/v3 extension header
    uint16_t real_pc = ext[2] | (ext[3] << 8);
    state->PC = real_pc;

    uint8_t hw_id = ext[4];
    configure_hardware(state, hw_id);

    // AY state
    state->ay_selected_register = ext[7];
    for (int i = 0; i < 16; i++) {
        state->ay_registers[i] = ext[8 + i];
    }

    // +3 / 128K paging ports
    if (ext_len >= 54) {
        uint8_t port_7FFD = ext[24];
        uint8_t port_1FFD = ext[26];
        apply_paging_ports(state, port_7FFD, port_1FFD);
    }

    // MEMPTR (undocumented Z80 register)
    if (ext_len >= 55) {
        uint16_t memptr = ext[35] | (ext[36] << 8);
        state->MEMPTR = memptr;
    }

    // Read the RAM pages (each is preceded by a 3-byte header)
    while (!feof(f)) {
        uint8_t page_hdr[3];
        if (fread(page_hdr, 1, 3, f) != 3) break;

        uint8_t bank_num = page_hdr[0];
        uint16_t page_len = page_hdr[1] | (page_hdr[2] << 8);

        uint8_t bank_data[16384];
        if (page_len == 0xFFFF) {
            // Uncompressed page
            fread(bank_data, 1, 16384, f);
        } else {
            // Compressed page
            uint8_t compressed_buf[16384];
            fread(compressed_buf, 1, page_len, f);
            decompress_z80_page(compressed_buf, page_len, bank_data, 16384);
        }

        set_ram_bank(state, bank_num, bank_data);
    }

    fclose(f);
    return 0;
}
```

### 7.4 Validation

A robust loader should validate the file before applying it:

- **File size**: at least 30 bytes for the v1 header.
- **Hardware ID**: must be a known value (0–20).
- **Page lengths**: must be either `0xFFFF` (uncompressed) or a reasonable compressed length (< 16384).
- **Bank numbers**: must be valid for the specified hardware (0–7 for 128K, 0–63 for clones with extended memory).

If validation fails, the loader should refuse to apply the snapshot.

---

## §8. Compatibility and Quirks

The .Z80 format has been around for 30+ years and has accumulated several quirks and emulator-specific behaviours.

### 8.1 The 54 vs 55 byte ambiguity

Some early v3 emulators wrote a 54-byte extension header; others wrote 55 bytes. The 55th byte (when present) is usually padding or contains the high byte of the MEMPTR register. A robust loader should accept both lengths and treat any bytes between the expected end of the v3 header and the start of the first page as padding.

### 8.2 The MEMPTR field

The MEMPTR field (also called W or WZ) is the undocumented Z80 register that some instructions (`BIT n,(HL)`, `LD (NN),A`, `LD A,(NN)`, `OUT (N),A`, `IN A,(N)`) modify. The .Z80 v3 format captures this, but many older loaders ignore it. For most software this doesn't matter, but for demos and copy-protection code that relies on MEMPTR's behaviour, ignoring it can cause incorrect execution.

### 8.3 The T-state counter

The T-state counter field (v3 offsets 60–63) is the position within the current video frame when the snapshot was taken. This is important for cycle-exact resumption but is ignored by many emulators (which simply resume at the start of a frame).

### 8.4 The `0xED 0xED 0x00 0xED` edge case

The literal `0xED 0xED` encoding (`0xED 0xED 0x00 0xED`) is a known edge case. Some buggy decoders treat the count byte 0 as "0 repetitions" (producing no output) instead of "1 repetition" (producing one 0xED byte). This corrupts snapshots that contain literal `0xED 0xED` sequences.

If you write a .Z80 decoder, double-check this edge case.

### 8.5 Per-emulator quirks

Different emulators have slightly different interpretations of some fields:

- **Fuse** is generally the reference implementation for .Z80 loading.
- **ZEsarUX** extends the format with custom fields for its own use (and prefers .SZX).
- **Spectaculator** is the reference for v3-specific fields.
- **UnrealSpeccy** is the reference for Russian-clone-specific fields.

When in doubt, test your .Z80 file against multiple emulators.

---

## §9. Comparison with .SNA and .SZX

| Aspect | .SNA | .Z80 | .SZX |
|---|---|---|---|
| Origin | 1992 (JPP emulator) | 1994 (Z80 emulator) | 2005+ (ZEsarUX) |
| Versions | 1 (48K) + 1 extension (128K) | v1, v2, v3 | Single, with extensions |
| Max header size | 27 bytes (48K) / 31 bytes (128K) | 30 bytes (v1) / 55 bytes (v3) | Variable (chunked) |
| AY state | ❌ | ✅ (v2+) | ✅ |
| Clone hardware | ❌ | ✅ (v3) | ✅ |
| +2A/+3 paging | ❌ | ✅ (v3) | ✅ |
| MEMPTR | ❌ | ✅ (v3) | ✅ |
| Per-page compression | ❌ | ✅ (v2/v3) | ✅ |
| Extensible design | ❌ | Limited (v3) | Highly extensible (chunks) |
| Backward compatibility | N/A | ✅ (v3 reads v1/v2) | Independent |

**When to use which**:

- **.SNA**: Maximum compatibility. Use for simple 48K snapshots where any limitation must be loadable.
- **.Z80**: General-purpose. The recommended format for most snapshots.
- **.SZX**: For complex state (peripherals, T-state-exact timing) that .Z80 cannot represent. See [szx_format.md](szx_format.md).

---

## §10. Cross-References

### 10.1 Within the snapshots section

- **[sna_format.md](sna_format.md)** — The simpler .SNA format. Read this first if you're new to snapshots.
- **[szx_format.md](szx_format.md)** — The .SZX format, ZEsarUX's chunk-based format for capturing even more state.
- **[rzx_format.md](rzx_format.md)** — The .RZX input recording format, for replay rather than static snapshots.

### 10.2 Outside the snapshots section

- **[../../04_operating_systems/rom_plus2.md](../../04_operating_systems/rom_plus2.md)** — The +2A/+3 ROM internals, including the `#1FFD` paging port captured by .Z80 v3.
- **[../../04_operating_systems/rom_versions.md](../../04_operating_systems/rom_versions.md)** — ROM versions, for identifying which ROM is appropriate for a given hardware ID.

### 10.3 External resources

- **World of Spectrum** (worldofspectrum.org) — The format documentation by Martijn van der Heide.
- **The Fuse emulator source code** — A clean reference implementation of the .Z80 loader.

---

## License

This document is licensed under **Creative Commons Attribution-ShareAlike 4.0 International** (CC BY-SA 4.0). You are free to share and adapt this material, provided you give appropriate credit, indicate changes, and distribute derivative works under the same licence.
