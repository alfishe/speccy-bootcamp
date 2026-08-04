[← Plan](../PLAN.md) · [Reverse Engineering](README.md)

# Code Crunching — Spectrum Packers, Depackers, and Compression Analysis

Every non-trivial ZX Spectrum program is compressed. A 48K game that fills all of RAM cannot fit on a standard tape block without compression. A demo that streams effects from disk needs compression to fit more content per sector. A bootloader must fit in a few hundred bytes. The Spectrum demoscene drove the development of increasingly sophisticated data compression algorithms — many of them unique to the platform, optimized for the Z80's instruction set and memory model.

This article covers Spectrum data compression from the reverse engineer's perspective: how to identify the packer, how to write a depacker, and how to handle compressed executables. It does **not** duplicate [compression_packing.md](../07_demoscene/compression_packing.md) (when it exists) — that article will cover compression from the demoscene author's perspective. This article is the RE view: you have a compressed binary, and you need to get the original data out.

> [!NOTE]
> This article assumes you have read [analysis_techniques.md](analysis_techniques.md) and can produce a disassembly and navigate an emulator debugger.

---

## Why Everything Is Compressed

| Scenario | Uncompressed size | Compressed size | Packer used |
|---|---|---|---|
| 48K game on tape | ~40 KB | ~20-25 KB | MegaLZ, HRUM, Z80 cruncher |
| Demo part on disk | 32-64 KB | 10-20 KB | Laser Compact, Hrust |
| Bootloader | N/A | < 256 bytes | Custom (hand-optimized) |
| Music module (PT3) | ~10-20 KB | ~5-15 KB | PT3 built-in compression |
| Screen image | 6,912 bytes | ~1-3 KB | ZX0, MegaLZ, Laser Compact |

The Spectrum has 16K-128K of RAM. Tape blocks at standard baud rate take ~3 minutes for 48K. Disk sectors are 256 bytes each. Every byte saved means faster loading, more content, or better games. Compression is not optional — it is universal.

---

## Packer Survey

The Spectrum community developed dozens of compression tools over the platform's lifetime. Here are the most important ones:

### The Major Packers

| Packer | Year | Algorithm | Compression ratio | Depacker size | Notes |
|---|---|---|---|---|---|
| **Z80 Cruncher** | 1980s | RLE + LZSS variant | ~40-50% | ~30 bytes | Simple, early, common on tape games |
| **KSA** | 1990s | LZSS | ~45-55% | ~40 bytes | "KSA" = Krisztian's Simple Archiver |
| **MegaLZ** | 2000s | LZ77 variant | ~50-60% | ~60 bytes | Most popular in modern demoscene |
| **HRUM** | 1990s | LZ77 + Huffman | ~50-60% | ~100 bytes | Popular on Russian Spectrum |
| **Hrust** | 1990s | LZ77 + arithmetic | ~55-65% | ~120 bytes | Higher ratio, larger depacker |
| **Laser Compact** | 1990s | LZ77 variant | ~50-60% | ~50 bytes | Used by Russian demoscene |
| **ZX0** | 2019 | LZ77 variant | ~50-60% | ~70 bytes | Modern, optimized by Einar Saukas |
| **ZX1** | 2019 | LZ77 variant | ~50-60% | ~60 bytes | Faster decompression than ZX0 |
| **ZX2** | 2019 | LZSS | ~45-55% | ~40 bytes | Simplest of the ZX family |
| **RLE** | Various | Run-length encoding | ~20-30% | ~15 bytes | Simple, fast, low ratio |

### Compression Ratio Comparison

Typical compression ratios for a 40 KB game binary (ratios vary widely by data type):

```
Uncompressed:   40,960 bytes
RLE:            32,768 bytes  (80% — poor for code, OK for graphics)
Z80 Cruncher:   22,528 bytes  (55%)
KSA:            20,480 bytes  (50%)
MegaLZ:         18,432 bytes  (45%)
HRUM:           17,408 bytes  (42%)
Hrust:          16,384 bytes  (40%)
ZX0:            18,000 bytes  (44%)
```

### Tradeoffs

| Priority | Best choice | Why |
|---|---|---|
| Maximum compression | Hrust | Best ratio, but largest depacker |
| Best ratio-to-depacker-size | MegaLZ, ZX0 | Good ratio with small depacker |
| Fastest decompression | RLE, ZX2 | Minimal CPU time |
| Smallest depacker | RLE (~15 bytes) | Fits in tight bootloaders |
| Modern standard | ZX0/ZX1/ZX2 | Einar Saukas family, actively maintained |
| Historical authenticity | HRUM, Hrust | What Russian Spectrum actually used |

---

## Format Identification

When you encounter a compressed file, the first task is identifying which packer was used. Spectrum packers do not always have a magic byte — the compressed data may start directly with encoded content.

### Identification Heuristics

**Method 1: Look for a depacker stub**

Most compressed executables include a small depacker at the start. The depacker's code is recognizable:

```z80
; MegaLZ depacker signature (simplified):
        LD   HL, CompressedData
        LD   DE, DestinationAddr
        CALL DepackRoutine
        JP   DestinationAddr      ; jump to decompressed code

DepackRoutine:
        ; ... typical MegaLZ bit-stream reading pattern ...
        LD   A, (HL)              ; read byte from compressed stream
        ; ... bit manipulation ...
```

Each packer has a characteristic depacker entry sequence. With experience, you can identify the packer by examining the first 50-100 bytes of the binary.

**Method 2: Check the file extension / wrapper**

On TR-DOS disks, packed files sometimes have extensions that hint at the packer:

| Extension / hint | Likely packer |
|---|---|
| `.C` with small size | Any packer (generic code file) |
| `.HRM` | HRUM |
| `.HRS` | Hrust |
| `.MLZ` | MegaLZ |
| `.Z80` | Z80 Cruncher (not the snapshot format!) |

**Method 3: Try known depackers**

If you cannot identify the packer by inspection, try decompressing with each known depacker. Write a small test program that applies the depacker to the data and checks if the result looks like valid Z80 code:

```bash
# MegaLZ depack test (using z88dk or sjasmplus)
# Write a small wrapper that loads the compressed data, calls the depacker,
# and saves the result to a new file.
# If the output contains valid Z80 opcodes (LD, CALL, RET sequences), the
# depacker matched.
```

**Method 4: Runtime observation**

Load the compressed program in ZEsarUX and observe the decompression:

1. Set a breakpoint at the start of RAM (`#8000`).
2. Let the depacker run.
3. The memory fills with decompressed code.
4. Take a snapshot after decompression completes.

This sidesteps the identification problem entirely — you get the decompressed data regardless of which packer was used.

---

## LZSS and LZ77 Fundamentals

Most Spectrum packers are variants of LZ77/LZSS compression. Understanding the algorithm makes it much easier to analyze and write depackers.

### How LZ77 Works

LZ77 replaces repeated byte sequences with references to earlier occurrences. The compressed stream is a sequence of either:

- **Literal bytes** (copied directly to output)
- **Match references** (copy N bytes from a position M bytes back in the output)

The encoder scans forward through the data. For each position, it searches backward for the longest matching sequence. If it finds a match of length >= 3 (minimum match length), it emits a match reference. Otherwise, it emits a literal.

### How LZSS Differs

LZSS (Lempel-Ziv-Storer-Szymanski) is a variant of LZ77 that uses a bit flag to distinguish literals from matches:

```
Bit stream: 0 = literal, 1 = match
  Literal: [0] [8 bits of literal byte]
  Match:   [1] [offset bits] [length bits]
```

This is more efficient than LZ77's fixed-size tokens. Most Spectrum packers use LZSS-style bit-stream encoding, with variations in how the offset and length are encoded.

### Typical Spectrum LZSS Variant

```z80
; Simplified LZSS depacker (common pattern across Spectrum packers):
;
; The compressed data is a bit-stream. Read one bit at a time:
;   bit = 0: copy one literal byte from compressed stream to output
;   bit = 1: read a match (offset + length), copy from earlier output

DepackLZSS:
        LD   A, #80              ; bit mask (start with bit 7)
.next_byte:
        ; Read one bit from the bit-stream
        RL   A                   ; rotate mask left
        JR   NC, .have_bit       ; mask still has bits
        LD   A, (HL)             ; read next control byte
        INC  HL
        RLA                     ; rotate in new byte, carry = first bit
        LD   (BitBuffer), A      ; save updated mask
.have_bit:
        JR   C, .is_match        ; carry set = match reference

        ; Literal: copy one byte
        LDI                     ; copy (HL) to (DE), HL++, DE++, BC--
        JR   .next_byte

.is_match:
        ; Match: read offset and length from the bit-stream
        ; (Each packer encodes these differently — simplified here)
        CALL ReadBits            ; read offset bits
        LD   C, A                ; C = offset low
        CALL ReadBits            ; read length bits
        LD   B, A                ; B = length

        ; Copy B bytes from (DE - offset) to (DE)
        PUSH HL
        LD   H, D
        LD   L, E
        OR   A
        SBC  HL, BC              ; HL = DE - offset (source)
        POP  HL                  ; HL = compressed stream ptr (restored)
        ; ... copy B bytes from source to DE ...
        JR   .next_byte
```

Each packer optimizes the offset and length encoding differently. MegaLZ uses a gamma-coded length with a variable-length offset. ZX0 uses a specific bit-packing scheme. HRUM adds Huffman coding on top. But the core LZSS pattern — literal vs. match, backward reference — is universal.

---

## Writing a Generic Depacker

If you cannot find the specific depacker for a format, you can write a generic one. The key insight: all LZSS variants share the same structure. You only need to adapt the bit-reading and offset/length encoding.

### Template Depacker

```z80
; ============================================================
; Generic LZSS depacker template
;
; Entry: HL = compressed data source
;        DE = destination address
;        BC = destination length (for LDI counter)
; ============================================================

GenericDepack:
        LD   A, #80              ; initial bit mask

.main_loop:
        ; Check if we are done (BC == 0)
        LD   A, B
        OR   C
        RET  Z

        ; Read control bit
        CALL GetBit
        JR   C, .match

        ; Literal byte
        LD   A, (HL)
        INC  HL
        LD   (DE), A
        INC  DE
        DEC  BC
        JR   .main_loop

.match:
        ; Read offset (usually 8-16 bits)
        CALL GetByte             ; or GetBits for variable-length
        LD   C, A                ; offset low
        CALL GetByte
        LD   B, A                ; offset high (if > 256)

        ; Read length (usually gamma-coded or fixed)
        CALL GetByte
        ; A = match length (minimum 2, typically)

        ; Now copy 'length' bytes from (DE - offset) to (DE)
        PUSH HL
        PUSH BC                  ; save main counter
        LD   B, 0
        LD   C, A                ; BC = copy length
        PUSH DE
        EX   DE, HL              ; HL = dest
        OR   A
        SBC  HL, BC              ; HL = dest - offset = source
        EX   DE, HL              ; DE = source, HL = dest
        POP  HL                  ; HL = dest (restored)
        PUSH HL
        LD   H, D                ; HL = source
        LD   L, E
        POP  DE                  ; DE = dest
.copy_loop:
        LD   A, (HL)
        LD   (DE), A
        INC  HL
        INC  DE
        DEC  BC
        LD   A, B
        OR   C
        JR   NZ, .copy_loop
        POP  BC                  ; restore main counter
        POP  HL                  ; restore compressed stream ptr
        JR   .main_loop

; ============================================================
; GetBit — read one bit from the bit-stream
;
; Entry: A = current bit mask (MSB first)
; Exit:  carry = bit value, A = updated mask
; ============================================================

GetBit:
        RL   A                   ; rotate mask
        RET  NZ                  ; still have bits
        LD   A, (HL)             ; read next control byte
        INC  HL
        RRA                     ; carry = MSB of new byte
        RET

; ============================================================
; GetByte — read 8 bits from the bit-stream
;
; Exit: A = byte value
; ============================================================

GetByte:
        PUSH BC
        LD   B, 8
.byte_loop:
        CALL GetBit
        RL   C                   ; build byte in C
        DJNZ .byte_loop
        LD   A, C
        POP  BC
        RET
```

This template works for basic LZSS. For packers with variable-length offsets (gamma coding, Elias coding), you need to adapt the offset/length reading. For packers with Huffman coding (HRUM), you need a Huffman table reader.

---

## Compressed Executable Format

Most Spectrum software distributes as a **compressed executable**: a small depacker followed by compressed data. When loaded, the depacker runs first, decompresses the payload, then jumps to the entry point.

### Structure

```
Compressed executable:
  +-------------------+
  | Depacker code     |  ~30-120 bytes (packer-specific)
  +-------------------+
  | Compressed data   |  variable length
  +-------------------+

Execution flow:
  1. Loader places the entire block at a fixed address (e.g., #8000)
  2. Execution starts at the depacker
  3. Depacker reads compressed data, writes decompressed code to destination
  4. Depacker jumps to decompressed entry point
```

### Extracting the Payload

To reverse engineer a compressed executable, you need the decompressed code. Two approaches:

**Approach 1: Runtime extraction (easiest)**

1. Load the executable in ZEsarUX.
2. Set a breakpoint on the `JP nn` at the end of the depacker (the jump to decompressed code).
3. Let it run. The breakpoint triggers with all code decompressed.
4. Save the snapshot. The decompressed code is in RAM.

**Approach 2: Standalone depacking**

1. Identify the packer format.
2. Use a matching depacker tool (command-line) to decompress the data.
3. This gives you the raw decompressed binary without running it in an emulator.

```bash
# MegaLZ depack (if you have the megalz tool)
megalz depack input.bin output.bin

# ZX0 depack (using a Python implementation)
python3 zx0.py depack input.zx0 output.bin

# For HRUM/Hrust, use the specific depacker from the Spectrum toolchain
```

---

## Memory-Constrained Depacking

A unique Spectrum challenge: the compressed data and the decompressed data both need to be in RAM simultaneously. If the compressed file is 20 KB and decompresses to 40 KB, both must fit in the 48K RAM (minus screen and system variables).

### Overlap Depacking (Depainting in Place)

The solution: if the depacker is careful about the order of operations, the decompressed data can **overwrite the compressed data** as it goes. This works because the compressed data is read linearly (from low to high address) while the decompressed data is also written linearly. If the decompressed data grows faster than the compressed data is consumed, the write pointer catches up to the read pointer.

```
Memory during overlap depacking:

  Compressed data:  [CCCCCCCCCCCCCCCCCCC.....]  (read pointer moves right)
  Decompressed data:     [DDDDDDDDDDDDDDDDDDDDDD]  (write pointer, faster)

  As depacking progresses, the write pointer overwrites compressed
  data that has already been read. This is safe because the read
  pointer has already passed those bytes.
```

This technique is called **depainting in place** (from Russian "raspisaniye na meste") and is used by virtually all Spectrum packers. The packer ensures that the compressed data is structured so that overlap depacking never corrupts unread data.

---

## Common Pitfalls

### 1. Wrong Depacker for the Format

Using the wrong depacker produces garbage. Always verify the output looks like valid Z80 code (sensible opcodes, proper function boundaries). If the output is garbage, try a different packer.

### 2. Depacking into the Wrong Address

The depacker writes decompressed data to a specific destination address. If you get the address wrong, the code is at the wrong location and will not run. Always check the destination address encoded in the depacker stub.

### 3. Overlapping Compression with Code

If you are depacking into RAM that also contains the depacker itself, the depacker may overwrite its own code before it finishes. Most packers avoid this by placing the depacker before the compressed data and decompressing forward, but check the specific packer's design.

### 4. 128K Banked Compression

Some games store compressed data in multiple RAM banks. The depacker switches banks as it decompresses. When extracting, make sure you handle all banks — a single 48K snapshot may miss data in other banks.

### 5. Self-Modifying Depackers

Some packers use self-modifying code in the depacker stub (e.g., modifying the destination address during depacking). Static disassembly may not show the actual runtime behavior. Always verify with dynamic analysis.

---

## Cross-References

| Topic | Reference |
|---|---|
| RE methodology overview | [methodology.md](methodology.md) |
| Analysis techniques | [analysis_techniques.md](analysis_techniques.md) |
| Protection cracking | [protection_cracking.md](protection_cracking.md) |
| Game reversing | [game_reversing.md](game_reversing.md) |
| Snapshot repair | [snapshot_repair.md](snapshot_repair.md) |
| Demoscene compression (planned) | [compression_packing.md](../07_demoscene/compression_packing.md) |
| File format parsing | [file_format_handling.md](../05_development/08_dos_tape/file_format_handling.md) |
| Memory and I/O (48K) | [memory_and_io_48k.md](../05_development/03_memory_and_io/memory_and_io_48k.md) |
| Assembly patterns | [assembly_patterns.md](../05_development/02_assembly/assembly_patterns.md) |

## References

### External references

- **`zx7` documentation** (Antonio Villena) — the canonical modern packer; documents the exhaustive-search algorithm that achieves better compression than the classic ZX-series crunchers at the cost of slower packing.
- **`lz4` and `aplib` format references** — generic LZ formats that some modern Spectrum releases use for cross-platform compatibility; the decompressor is more complex but compression is tighter.
- **`MegaLZ` documentation** (Bulba / Maxim) — the LZ-based packer widely used in the late 1990s Russian demoscene; documents the bit-stream encoding and the asymmetric packing constraint (decompresses to any address, packs on a different machine).
- **`zx-pk.ru` packer benchmark threads** — Russian-language community benchmarks comparing compression ratios of `zx7` / `MegaLZ` / `HRUM` / `LZ4` / `aplib` on standard test corpora (game binaries, demo code, graphics).
- **`z88dk-appmake` documentation** — the z88dk-side reference for packing Spectrum binaries; includes worked examples of the `--combine` and `--app-type` flags for producing packed `.tap` / `.tzx` images.
