[← Plan](../PLAN.md) · [Reverse Engineering](README.md)

# Snapshot Repair — Fixing Corrupted .SNA and .Z80 Files

Snapshots are the most common format for distributing ZX Spectrum software today. They are also fragile: a single corrupted byte in the header can make the file unloadable. This article covers the practical repair of .SNA and .Z80 snapshots — identifying corruption types, fixing broken headers, recovering damaged RAM data, and converting between formats.

This article does **not** duplicate [file_format_handling.md](../05_development/08_dos_tape/file_format_handling.md) — that article covers the *parsing* of snapshot formats. This article covers the *repair* perspective: you have a snapshot that does not work, and you need to fix it.

> [!NOTE]
> Snapshot repair requires a hex editor (xxd, hexyl, or a GUI hex editor like Hex Fiend) and an understanding of the .SNA and .Z80 format internals. See [file_format_handling.md](../05_development/08_dos_tape/file_format_handling.md) for the byte-level format specifications.

---

## Common Corruption Types

| Problem | Cause | Fixable? |
|---|---|---|
| Wrong PC (program counter) | Snapshot taken at wrong moment, or header corrupted | Yes — set PC to valid code address |
| Wrong SP (stack pointer) | Stack corrupted before snapshot | Yes — reset SP to sane value |
| Truncated RAM | File transfer error, disk corruption | Partially — missing RAM is unrecoverable |
| Wrong machine model flag | 48K game saved as 128K or vice versa | Yes — fix model byte |
| Bad .Z80 compression | Corrupted RLE stream | Yes — decompress manually |
| Wrong border color | Cosmetic only | Yes — fix border byte |
| Modified I/R registers | Cosmetic, rarely causes crashes | Usually fine |
| RAM bank mismatch (128K) | Wrong bank paged during save | Yes — swap banks |

---

## .SNA Repair

### 48K .SNA Structure

A 48K .SNA is 49,179 bytes: a 27-byte header followed by 49,152 bytes of RAM (`#4000`-`#FFFF`).

```
Header (27 bytes):
  Offset  Size  Content
  0       1     Register I
  1       2     HL' (alternate register pair)
  3       2     DE' (alternate)
  5       2     BC' (alternate)
  7       2     AF' (alternate)
  9       2     HL
  11      2     DE
  13      2     BC
  15      2     IY
  17      2     IX
  19      1     IFF2 (bit 2 = interrupt state)
  20      1     R (refresh register)
  21      2     AF
  23      2     SP (stack pointer)
  25      1     Interrupt mode (0, 1, or 2)
  26      1     Border color (0-7)

RAM data (49,152 bytes):
  Offset  Size   Content
  27      49152  RAM dump (#4000 through #FFFF, contiguous)
```

### Validating the Header

```python
import struct, sys

def validate_sna48(filename):
    with open(filename, "rb") as f:
        data = f.read()

    if len(data) != 49179:
        print(f"WRONG SIZE: {len(data)} bytes (expected 49179)")
        if len(data) < 49179:
            print("  FILE IS TRUNCATED — RAM data is incomplete")
        else:
            print("  FILE HAS EXTRA DATA — may be padded or corrupt")

    # Extract header fields
    i_reg = data[0]
    sp = struct.unpack_from("<H", data, 23)[0]
    pc_is_on_stack = True  # .SNA stores PC on the stack

    # Validate SP: must be in RAM range #4000-#FFFF
    if sp < 0x4000:
        print(f"BAD SP: #{sp:04X} — below RAM start (#4000)")
    elif sp > 0xFFFE:
        print(f"BAD SP: #{sp:04X} — at top of RAM (stack overflow?)")

    # Check interrupt mode
    im = data[25]
    if im not in (0, 1, 2):
        print(f"BAD IM: {im} — must be 0, 1, or 2")

    # Check border color
    border = data[26]
    if border > 7:
        print(f"BAD BORDER: {border} — must be 0-7")

    # The PC is stored at (SP) in the RAM dump
    # RAM offset = SP - #4000 + 27 (header size)
    ram_offset = sp - 0x4000 + 27
    if 0 <= ram_offset < len(data) - 1:
        pc = struct.unpack_from("<H", data, ram_offset)[0]
        print(f"PC: #{pc:04X} (stored at SP=#{sp:04X})")
        # Validate PC: should be in code range
        if pc < 0x5C00:
            print(f"  WARNING: PC below system variables — may be in ROM space")
        if pc > 0xFF00:
            print(f"  WARNING: PC near top of RAM — may be stack corruption")
    else:
        print(f"CANNOT READ PC: SP=#{sp:04X} points outside RAM")

    print(f"I: #{i_reg:02X}, R: #{data[20]:02X}")
    print(f"IM: {im}, Border: {border}")

if __name__ == "__main__":
    validate_sna48(sys.argv[1])
```

### Fixing a Bad PC

The most common .SNA corruption: the PC (stored on the stack at address SP) points to an invalid location. To fix it:

1. Read the SP value from header offset 23-24.
2. Read the PC from RAM at offset `(SP - #4000 + 27)`.
3. Check if the PC points to valid Z80 code (disassemble from PC — do you see sensible instructions?).
4. If not, search for the real entry point. Common candidates:
   - The address that appears most frequently as a JP/CALL target in the code
   - The start of the code block (`#8000` is a common entry point)
   - The address stored in the BASIC system variable `PROG` (`#5C53`) for programs that return to BASIC

```python
def fix_pc(filename, new_pc):
    """Fix the PC in a 48K .SNA by writing it to the stack location."""
    with open(filename, "rb") as f:
        data = bytearray(f.read())

    sp = struct.unpack_from("<H", data, 23)[0]
    ram_offset = sp - 0x4000 + 27

    # Write new PC to the stack location
    struct.pack_into("<H", data, ram_offset, new_pc)

    with open(filename, "wb") as f:
        f.write(data)
    print(f"PC set to #{new_pc:04X} at SP=#{sp:04X}")
```

### Fixing a Bad SP

If the stack pointer itself is corrupted (pointing into ROM or below RAM):

```python
def fix_sp(filename, new_sp=0xFF40):
    """Reset SP to a safe value inside upper RAM."""
    with open(filename, "rb") as f:
        data = bytearray(f.read())

    # Write new SP to header offset 23
    struct.pack_into("<H", data, 23, new_sp)

    # Also write a valid return address at the new SP location
    # (The PC will be read from this location)
    ram_offset = new_sp - 0x4000 + 27
    # Use #8000 as a default entry point
    struct.pack_into("<H", data, ram_offset, 0x8000)

    with open(filename, "wb") as f:
        f.write(data)
    print(f"SP reset to #{new_sp:04X}, PC set to #8000")
```

A safe SP value is typically in upper RAM (`#FF00`-`#FF40`), which most games use as the stack area.

---

## .Z80 Repair

The .Z80 format is more complex than .SNA — it supports multiple machine models, compression, and extended headers. This also means more things can go wrong.

### Version Detection

```
Byte 30 (#1E) of .Z80 header:
  If byte 30 = #FF AND byte 31 = #FF: version 2 or 3 (extended header)
  Otherwise: version 1 (48K only)
```

### Decompressing .Z80 RAM

Version 1 .Z80 files may use RLE compression (byte 12 bit 7 = 1). If the compressed data is corrupted, you need to handle errors during decompression.

```python
def z80_decompress(data, expected_len):
    """Decompress .Z80 RLE data. Returns decompressed bytes."""
    output = bytearray()
    i = 0

    while i < len(data) and len(output) < expected_len:
        byte = data[i]
        i += 1

        if byte == 0xED and i < len(data) and data[i] == 0xED:
            # RLE sequence: #ED #ED <count> <value>
            i += 1  # skip second #ED
            if i >= len(data):
                print("TRUNCATED RLE SEQUENCE")
                break
            count = data[i]
            i += 1
            if count == 0:
                # #ED #ED #00 #00 = literal #ED #ED
                output.extend(b'\xED\xED')
            else:
                if i >= len(data):
                    print("TRUNCATED RLE VALUE")
                    break
                value = data[i]
                i += 1
                output.extend(bytes([value]) * count)
        else:
            output.append(byte)

    if len(output) < expected_len:
        print(f"DECOMPRESSION INCOMPLETE: {len(output)} of {expected_len} bytes")

    # Pad with zeros if short
    output.extend(b'\x00' * (expected_len - len(output)))
    return bytes(output)
```

### Common .Z80 Corruption Issues

**Issue 1: Compressed data truncated**

The compressed RAM data ends before producing the expected 48K/128K. This happens when a file transfer cut off the end. The decompressor fills what it can and pads the rest with zeros. The game may crash when it reaches the zero-filled area.

**Fix**: Find an alternative copy of the file, or accept the corruption. If the missing data is in the upper RAM (above the code region), the game may still work.

**Issue 2: Wrong machine model**

The extended header (v2/v3) at offset 34 stores the hardware model:

| Value | Machine |
|---|---|
| 0 | 48K |
| 1 | 48K + IF1 |
| 2 | SAM Coupe |
| 3 | 128K |
| 4 | 128K + IF1 |
| ... | Various others |

If a 48K game is stored with model = 3 (128K), emulators may page in the wrong ROM and crash. Fix: change the model byte to 0.

**Issue 3: Wrong A register value in version 1**

In version 1 .Z80, byte 12 bit 7 doubles as both the compression flag and R7 (bit 7 of the R register). Some emulators misinterpret this. If the game crashes on startup with a garbled display, try toggling bit 7 of byte 12.

---

## Format Conversion

### .SNA to .Z80

```python
def sna_to_z48(sna_filename, z80_filename):
    """Convert 48K .SNA to .Z80 v1 (uncompressed)."""
    with open(sna_filename, "rb") as f:
        sna = f.read()

    if len(sna) != 49179:
        raise ValueError("Not a valid 48K .SNA")

    # Extract .SNA header fields
    i_reg = sna[0]
    hl_alt = struct.unpack_from("<H", sna, 1)[0]
    de_alt = struct.unpack_from("<H", sna, 3)[0]
    bc_alt = struct.unpack_from("<H", sna, 5)[0]
    af_alt = struct.unpack_from("<H", sna, 7)[0]
    hl = struct.unpack_from("<H", sna, 9)[0]
    de = struct.unpack_from("<H", sna, 11)[0]
    bc = struct.unpack_from("<H", sna, 13)[0]
    iy = struct.unpack_from("<H", sna, 15)[0]
    ix = struct.unpack_from("<H", sna, 17)[0]
    iff2 = sna[19]
    r_reg = sna[20]
    af = struct.unpack_from("<H", sna, 21)[0]
    sp = struct.unpack_from("<H", sna, 23)[0]
    im = sna[25]
    border = sna[26]

    # PC is stored at (SP) in .SNA RAM
    ram_offset = sp - 0x4000 + 27
    pc = struct.unpack_from("<H", sna, ram_offset)[0]

    # Build .Z80 v1 header (30 bytes)
    z80 = bytearray(30)
    z80[0] = af & 0xFF           # A
    z80[1] = af >> 8             # F
    struct.pack_into("<H", z80, 2, bc)
    struct.pack_into("<H", z80, 4, hl)
    struct.pack_into("<H", z80, 6, pc)      # PC stored directly!
    struct.pack_into("<H", z80, 8, sp)
    z80[10] = i_reg
    z80[11] = r_reg & 0x7F
    # Byte 12: bit 0-2 = border, bit 5 = R bit 7, bit 7 = compressed (0=uncompressed)
    z80[12] = (border & 0x07) | ((r_reg & 0x80) >> 2)
    struct.pack_into("<H", z80, 13, de)
    struct.pack_into("<H", z80, 15, bc_alt)
    struct.pack_into("<H", z80, 17, de_alt)
    struct.pack_into("<H", z80, 19, hl_alt)
    z80[21] = af_alt & 0xFF
    z80[22] = af_alt >> 8
    struct.pack_into("<H", z80, 23, iy)
    struct.pack_into("<H", z80, 25, ix)
    z80[27] = iff2 & 0x04       # IFF1
    z80[28] = iff2 & 0x04       # IFF2
    z80[29] = im

    # Append uncompressed RAM (49,152 bytes)
    z80.extend(sna[27:])

    with open(z80_filename, "wb") as f:
        f.write(z80)
    print(f"Converted: {sna_filename} -> {z80_filename}")
    print(f"  PC: #{pc:04X}, SP: #{sp:04X}")
```

### .Z80 to .SNA

Converting .Z80 to .SNA is the reverse: extract PC from the .Z80 header, write it to the stack position in RAM, and build the 27-byte .SNA header. The trick: .SNA stores PC on the stack at (SP), so you must write the PC value to the correct RAM location.

```python
def z80_to_sna48(z80_filename, sna_filename):
    """Convert .Z80 v1 (48K, uncompressed) to .SNA."""
    with open(z80_filename, "rb") as f:
        z80 = f.read()

    # Check: version 1 (byte 30 is register A complement, not #FF)
    if len(z80) < 30:
        raise ValueError("File too short to be valid .Z80")

    # Extract .Z80 header fields
    af = z80[0] | (z80[1] << 8)
    bc = struct.unpack_from("<H", z80, 2)[0]
    hl = struct.unpack_from("<H", z80, 4)[0]
    pc = struct.unpack_from("<H", z80, 6)[0]
    sp = struct.unpack_from("<H", z80, 8)[0]
    i_reg = z80[10]
    r_reg = z80[11] | ((z80[12] & 0x20) << 2)
    border = z80[12] & 0x07
    de = struct.unpack_from("<H", z80, 13)[0]
    bc_alt = struct.unpack_from("<H", z80, 15)[0]
    de_alt = struct.unpack_from("<H", z80, 17)[0]
    hl_alt = struct.unpack_from("<H", z80, 19)[0]
    af_alt = z80[21] | (z80[22] << 8)
    iy = struct.unpack_from("<H", z80, 23)[0]
    ix = struct.unpack_from("<H", z80, 25)[0]
    iff = z80[27] & 0x04
    im = z80[29]

    # Get RAM data (may be compressed)
    compressed = (z80[12] & 0x80) != 0
    if compressed:
        ram = z80_decompress(z80[30:], 49152)
    else:
        ram = z80[30:30 + 49152]
        if len(ram) < 49152:
            ram = ram + b'\x00' * (49152 - len(ram))

    ram = bytearray(ram)

    # Write PC to the stack location (SP) in RAM
    # RAM offset = (SP - #4000)
    stack_offset = sp - 0x4000
    if 0 <= stack_offset < len(ram) - 1:
        struct.pack_into("<H", ram, stack_offset, pc)
    else:
        print(f"WARNING: SP #{sp:04X} out of range, PC not written")

    # Build .SNA header (27 bytes)
    sna = bytearray(27)
    sna[0] = i_reg
    struct.pack_into("<H", sna, 1, hl_alt)
    struct.pack_into("<H", sna, 3, de_alt)
    struct.pack_into("<H", sna, 5, bc_alt)
    struct.pack_into("<H", sna, 7, af_alt)
    struct.pack_into("<H", sna, 9, hl)
    struct.pack_into("<H", sna, 11, de)
    struct.pack_into("<H", sna, 13, bc)
    struct.pack_into("<H", sna, 15, iy)
    struct.pack_into("<H", sna, 17, ix)
    sna[19] = iff
    sna[20] = r_reg
    struct.pack_into("<H", sna, 21, af)
    struct.pack_into("<H", sna, 23, sp)
    sna[25] = im
    sna[26] = border

    # Append RAM
    sna.extend(ram)

    with open(sna_filename, "wb") as f:
        f.write(sna)
    print(f"Converted: {z80_filename} -> {sna_filename}")
    print(f"  PC: #{pc:04X}, SP: #{sp:04X}")
```

---

## Fixing Snapshots Crashed Mid-Load

A common scenario: a tape loader crashes partway through loading, and the emulator saves a snapshot of the crashed state. The snapshot contains partially loaded code.

### Diagnosis

1. Check the PC — does it point to valid code or into a loading routine?
2. Examine RAM `#8000`+ — is it fully populated with code, or is it partially zeros?
3. Check the display RAM (`#4000`-`#57FF`) — does it show a loading screen?

### Repair Options

**Option A: Re-load from tape**

If the original tape image (.TAP/.TZX) is available, simply re-load it in the emulator and take a fresh snapshot. This is usually the best option.

**Option B: Patch the loading routine**

If the crash is in the loader (not the game), disassemble the loader, find the crash point, and patch it:

```z80
; Example: loader crashes at #8500 due to bad timing check
; Original: JR NZ, CrashHandler
; Patch: NOP NOP (skip the timing check)
```

Save the modified snapshot and re-attempt loading.

**Option C: Manual reconstruction**

If only partial code was loaded, you may need to manually reconstruct the missing sections from a disassembly of a working copy (if available) or from the original tape image.

---

## Cross-References

| Topic | Reference |
|---|---|
| File format specifications | [file_format_handling.md](../05_development/08_dos_tape/file_format_handling.md) |
| RE methodology | [methodology.md](methodology.md) |
| Analysis techniques | [analysis_techniques.md](analysis_techniques.md) |
| Protection cracking | [protection_cracking.md](protection_cracking.md) |
| Game reversing | [game_reversing.md](game_reversing.md) |
| Code compression | [code_crunching.md](code_crunching.md) |
| ROM routines | [rom_routines.md](../10_references/rom_routines.md) |
| System variables | [system_variables.md](../04_operating_systems/system_variables.md) |
| Memory and I/O (48K) | [memory_and_io_48k.md](../05_development/03_memory_and_io/memory_and_io_48k.md) |
| Memory and I/O (128K) | [memory_and_io_128k.md](../05_development/03_memory_and_io/memory_and_io_128k.md) |
