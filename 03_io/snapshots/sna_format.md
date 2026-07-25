[← Home](../../README.md) · [I/O](../../README.md) · [Snapshots](README.md)

# The .SNA Snapshot Format

A **snapshot** is a complete dump of the Spectrum's machine state at a single instant — every Z80 register, the entire RAM contents, and enough hardware state to allow execution to resume exactly where it left off. Snapshots are how Spectrum software is distributed today: instead of dealing with tape images or loader programs, you load a snapshot into an emulator and you are instantly inside the program.

The **.SNA format** is the simplest, oldest, and most widely-supported snapshot format. It was created by **Arnt Gulbrandsen** in 1992 for the **JPP emulator** (one of the earliest Spectrum emulators for Unix) and was rapidly adopted by virtually every other emulator. Its age and simplicity have made it a de facto standard — every emulator that loads snapshots can load .SNA files — but its limitations have led to the development of more capable formats like .Z80 and .SZX.

This article covers the .SNA format in full: its history, its on-disk byte layout for both 48K and 128K variants, what hardware state it captures (and what it doesn't), how to write a loader, the gotchas, and how it compares to .Z80 and .SZX. For the other snapshot formats, see [z80_format.md](z80_format.md), [szx_format.md](szx_format.md), and for the input-recording counterpart, see [rzx_format.md](rzx_format.md).

---

## Roadmap

1. **What the .SNA format is** — history, scope, why it exists
2. **The 48K .SNA format** — byte-by-byte header layout, RAM dump
3. **The 128K .SNA format** — extension, additional banks, bank order
4. **Hardware state captured** — what's saved, what isn't, why it matters
5. **Writing a .SNA loader** — full reference loader implementation
6. **Compatibility across emulators** — which emulators support which variants
7. **Limitations and gotchas** — what to watch out for
8. **Comparison with .Z80** — when to use which
9. **Modern status** — the .SNA format in 2024
10. **Cross-references** — where to go next

---

## §1. What the .SNA Format Is

### 1.1 Origins

The .SNA format was created in 1992 by **Arnt Gulbrandsen**, a Norwegian computer scientist, for his **JPP** Spectrum emulator (a precursor to the more widely-known **xzx** emulator). At the time, Spectrum emulators were proliferating, but each used its own proprietary snapshot format — making it impossible to share snapshots between emulators. Gulbrandsen designed .SNA as a simple, open format that anyone could implement.

The original .SNA format targeted only the 48K Spectrum, since that was what JPP emulated. The 128K extension came later, added by the authors of other emulators when 128K support became common.

The name "**SNA**" is short for "**snapshot**". The ".sna" file extension is universal — there is no alternative extension in use.

### 1.2 Scope

A .SNA file contains:

- A small **header** (27 bytes for 48K, larger for 128K) holding the Z80 register values and some hardware state.
- A **full dump of the RAM contents** at the moment the snapshot was taken — 48 KB for a 48K snapshot, 128 KB for a 128K snapshot.

That's it. The .SNA format is fundamentally a "registers + RAM dump" format. It does **not** include:

- The ROM contents (because ROM is constant for a given Spectrum model).
- The CPU's internal state beyond what's in the Z80 registers (no MEMPTR, no Q register, no internal ALU latches).
- Detailed hardware state (no AY register values, no FDC state, no peripheral state).
- Tape or disk state.
- Any embedded metadata (no emulator name, no timestamp, no description).

The format's design is "minimum viable snapshot" — enough to resume a typical Spectrum program, but nothing more. This simplicity is its strength: any emulator can implement .SNA support in an afternoon.

### 1.3 Why .SNA matters

.SNA matters because it is the **lingua franca** of Spectrum snapshots. Even though more capable formats exist, .SNA is universally supported. If you want to share a snapshot and you want the maximum number of emulators to be able to load it, .SNA is the safest choice.

The format is also the **foundation** of other formats. The .Z80 format, for example, uses a header structure inspired by .SNA, and many emulators that load .Z80 internally convert it to a .SNA-like representation before applying it to the emulated machine.

### 1.4 Why .SNA's limitations led to other formats

The .SNA format was designed in 1992 for 48K emulation. By the late 1990s, emulators were supporting:

- The 128K, +2, +2A, +3 hardware.
- The AY-3-8910 / YM2149 sound chip (whose current register values are part of the audio state).
- Multiple memory configurations (Pentagon, Scorpion, etc.).
- Detailed peripheral state (Beta 128 disk interface, +3 FDC, etc.).
- Various custom ROMs and patches.

The .SNA format could not represent most of this. The 128K extension was a partial fix, but it still did not capture AY state, did not support Russian clones, and had no way to identify the source hardware.

The .Z80 format (created by Glen Lleston for the Z80 emulator, also in the early 1990s) addressed some of these limitations. The .SZX format (created by César Hernández Bauset for ZEsarUX in the 2000s) addressed the rest. See §8 for the comparison.

Despite these limitations, .SNA remains popular because for 95% of use cases — running a 48K game — it works perfectly.
---

## §2. The 48K .SNA Format

The 48K .SNA format is the original and most common. The file is exactly **49179 bytes** long: a 27-byte header followed by 48 KB (49152 bytes) of RAM.

### 2.1 Header layout (27 bytes)

The header occupies bytes 0–26 of the file. All multi-byte values are **little-endian** (low byte first, as is the Z80 convention).

| Offset | Size | Field | Notes |
|---|---|---|---|
| 0 | 1 | I | The Z80 I register (interrupt vector base) |
| 1 | 2 | HL' | Alternate HL register pair (L first, then H) |
| 3 | 2 | DE' | Alternate DE register pair |
| 5 | 2 | BC' | Alternate BC register pair |
| 7 | 2 | AF' | Alternate AF register pair (F first, then A) |
| 9 | 2 | HL | Main HL register pair |
| 11 | 2 | DE | Main DE register pair |
| 13 | 2 | BC | Main BC register pair |
| 15 | 2 | IY | IY register pair |
| 17 | 2 | IX | IX register pair |
| 19 | 1 | IFF1 | Interrupt flip-flop 1 (bit 0 set = interrupts enabled) |
| 20 | 1 | IFF2 | Interrupt flip-flop 2 (bit 0 set = IFF2 set) |
| 21 | 1 | R | The Z80 R register (refresh counter) |
| 22 | 2 | AF | Main AF register pair (F first, then A) |
| 24 | 2 | SP | The Z80 stack pointer |
| 26 | 1 | Interrupt mode | 0, 1, or 2 (encoded in bits 0–1) |
| 27 | — | RAM dump begins | 49152 bytes of RAM follow |

**Note**: The header contains **25 bytes of registers + 2 bytes of PC-cleverness = 27 bytes**. The "interrupt mode" byte at offset 26 actually packs two things (see §2.3 below).

### 2.2 The PC trick

Look at the header layout again. There is no `PC` (program counter) field! This is not an omission — it's a deliberate trick.

When the snapshot was taken, the program counter had just been pushed onto the stack (by the snapshot-saving code). The Z80's SP register points to the top-of-stack, which is where PC sits. To resume execution, the loader:

1. Restores all registers from the header.
2. Restores SP from the header (SP now points at the saved PC).
3. Executes a `RET` instruction — which pops the saved PC off the stack and jumps to it.

This is why the header has no PC field: PC is stored in RAM (on the stack), and the loader retrieves it via the normal `RET` mechanism.

This trick means that a .SNA file is **self-restoring**: loading it does not require any special emulator support, just a `RET`. Some bare-bones emulators literally just load the header and RAM and then execute a `RET`.

### 2.3 The byte at offset 26

The byte at offset 26 (the 27th byte) encodes:

- **Bits 0–1**: The Z80 interrupt mode (0, 1, or 2). Mode 0 is rarely used; mode 1 is the standard Spectrum interrupt mode; mode 2 is used by some games for vector interrupts.
- **Bit 2**: If set, the screen is currently showing the "border colour" effect. (Some emulators interpret this; most ignore it.)
- **Bits 3–7**: Reserved. Should be 0.

In practice, most .SNA files have this byte set to `0x01` (interrupt mode 1, no border effect) — which is what the standard Spectrum uses.

### 2.4 The RAM dump

Bytes 27–49178 (49152 bytes) are the entire 48 KB of Spectrum RAM:

- `#4000`–`#5AFF` (6.75 KB): The display file (bitmap + attributes).
- `#4000`–`#FFFF` (48 KB): All of RAM.

The RAM dump is stored in **logical address order**, not banked order. Byte 27 of the .SNA file corresponds to RAM address `#4000`, byte 28 to `#4001`, and so on up to `#FFFF` at byte 49178.

Note that the .SNA file does **not** include the contents of the ROM (`#0000`–`#3FFF`). The ROM is assumed to be the standard 48K ROM. If the snapshot was taken with a different ROM in the address space (e.g., a custom ROM), that information is lost.

### 2.5 Total file size

A 48K .SNA file is exactly **49179 bytes** (27 + 49152). This makes it trivial to validate: if the file size is not 49179, it's either corrupt or a different format. (See §3 for the 128K variant, which has a different size.)

### 2.6 Hex byte map

A visual map of the first 27 bytes of a typical .SNA file:

```
Offset 0x00:  3F 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
Offset 0x10:  5A 00 00 00 01 00 00 00 00 00 00 00 01 00 00 00
Offset 0x1B:                                                01
```

- Byte 0: I = `0x3F` (the standard 48K value, pointing to the ROM's interrupt vector table).
- Bytes 1–18: alternate and main registers (all zero in this example, indicating a snapshot taken early in execution).
- Byte 19: IFF1 = `0x00` (interrupts disabled).
- Byte 20: IFF2 = `0x00`.
- Byte 21: R = `0x01`.
- Bytes 22–23: AF = `0x0000`.
- Bytes 24–25: SP = `0x0000` (will be set by the loader).
- Byte 26: Interrupt mode = `0x01`.

---

## §3. The 128K .SNA Format

The 128K .SNA format is an extension of the 48K format. It uses the same 27-byte header layout but adds an **extension block** between the header and the RAM dump, allowing it to capture the state of all 128 KB of RAM.

### 3.1 File structure

A 128K .SNA file consists of three parts:

1. **Header** (27 bytes): same layout as the 48K header.
2. **RAM banks 5, 2, 0** (3 × 16384 = 49152 bytes): the three banks currently mapped into the Spectrum's address space (this is the same data the 48K format would store).
3. **Extension header** (4 bytes): identifies this as a 128K snapshot.
4. **RAM banks 1, 3, 4, 6, 7** (5 × 16384 = 81920 bytes): the remaining banks.

Total file size: 27 + 49152 + 4 + 81920 = **131103 bytes**.

(Note: The PC is still stored on the stack in this variant, just like in the 48K case.)

### 3.2 The extension header (4 bytes)

The extension header sits at byte offset 27 + 49152 = 49179 in the file. It is 4 bytes long:

| Offset (within file) | Size | Field |
|---|---|---|
| 49179 | 1 | PC low byte |
| 49180 | 1 | PC high byte |
| 49181 | 1 | `#7FFD` value (the 128K paging port) |
| 49182 | 1 | TR-DOS paged flag (see §3.4) |

**The PC field**: Unlike the 48K format (which relies on PC being on the stack), the 128K format explicitly stores PC here. This is because the 128K's paged memory model makes the stack-based PC trick less reliable — the SP might point to a bank that's been paged out.

**The `#7FFD` value**: This is the value last written to the 128K paging port. It determines which ROM is in the address space (48K or 128K) and which RAM bank is paged at `#C000`–`#FFFF`. Without this, the loader would not know which bank was active when the snapshot was taken.

**The TR-DOS paged flag**: If this byte is non-zero, the Beta 128 disk interface ROM was paged in at `#0000`–`#3FFF` instead of the Spectrum ROM. This is critical for snapshots of TR-DOS-using software.

### 3.3 The remaining banks

After the extension header, the remaining five RAM banks (1, 3, 4, 6, 7) are stored in numerical order:

- Bytes 49183–65566: bank 1
- Bytes 65567–81950: bank 3
- Bytes 81951–98334: bank 4
- Bytes 98335–114718: bank 6
- Bytes 114719–131102: bank 7

The banks are always stored in this fixed order, regardless of which bank is currently paged at `#C000`–`#FFFF`. The paging information is captured in the `#7FFD` extension byte.

### 3.4 Bank ordering: why 5, 2, 0?

The first three banks stored (5, 2, 0) are the banks **currently mapped** into the Spectrum's address space:

- Bank 5 is at `#4000`–`#7FFF` (always — this is the screen bank).
- Bank 2 is at `#8000`–`#BFFF` (always — this is the work-area bank).
- Bank 0 is at `#C000`–`#FFFF` by default (the first page of banked memory).

This corresponds exactly to the layout captured by a 48K snapshot, which is why the 128K format stores these three banks first — it allows a 48K-only emulator to load the first 49152 bytes and ignore the rest.

### 3.5 The TR-DOS paged flag

The TR-DOS paged flag (byte 49182) deserves special attention. When the Beta 128 disk interface ROM is paged in (by an `OUT (#FD),...` operation on the disk port), it replaces the Spectrum ROM at `#0000`–`#3FFF`. A snapshot taken in this state must record that the Beta ROM is active, or the loader will incorrectly assume the Spectrum ROM is in place.

The flag is interpreted as follows:

- `0x00`: Spectrum ROM (or 128K ROM) is at `#0000`–`#3FFF`. Standard.
- `0xFF`: Beta 128 TR-DOS ROM is at `#0000`–`#3FFF`. The loader must page in the Beta ROM before resuming.

Some emulators also use intermediate values to indicate other ROM states (e.g., the +3 DOS ROM, or custom ROMs), but the standard interpretation is just `0x00` or `0xFF`.

### 3.6 128K variant: +2A/+3 paging port (`#1FFD`)

The 128K .SNA format does **not** capture the value of the +2A/+3 paging port (`#1FFD`). This means .SNA files cannot fully represent +2A/+3 states — the four paging modes (see [../../04_operating_systems/rom_plus2.md](../../04_operating_systems/rom_plus2.md) §6) are lost. For +2A/+3 software, .Z80 or .SZX is preferred.

### 3.7 Other clone hardware

The .SNA format has no support for Russian clones (Pentagon, Scorpion, ATM Turbo, etc.). If a snapshot is taken on such hardware, the .SNA file loses the clone-specific state. For Russian clone snapshots, .Z80 or .SZX is required.
---

## §4. Hardware State Captured

The .SNA format captures a **partial** snapshot of the Spectrum's state. This section enumerates exactly what is and isn't saved.

### 4.1 What .SNA captures

The .SNA format preserves:

- **All Z80 general-purpose registers**: A, F, B, C, D, E, H, L (and their alternates A', F', B', C', D', E', H', L').
- **The index registers**: IX, IY.
- **The special registers**: I (interrupt vector base), R (refresh counter).
- **The interrupt state**: IFF1, IFF2, and the interrupt mode (0, 1, or 2).
- **The stack pointer**: SP.
- **The program counter**: PC (via the stack in 48K, explicitly in 128K).
- **The entire RAM contents**: 48 KB for 48K, 128 KB for 128K.
- **The 128K paging port value**: `#7FFD` (128K variant only).
- **The TR-DOS paging flag**: whether the Beta 128 ROM was active (128K variant only).

This is enough to resume execution for the vast majority of Spectrum software.

### 4.2 What .SNA does not capture

The .SNA format does **not** preserve:

- **The ROM contents**: The ROM is assumed to be the standard 48K ROM (for 48K .SNA) or the 128K ROM (for 128K .SNA). Custom ROMs are lost.
- **The AY-3-8910 / YM2149 sound chip state**: All AY register values are lost. On resume, the AY is silent (or in an undefined state). For music-playing software, this means a noticeable glitch.
- **The beeper state**: The current value of the beeper port (`#FE` bit 4) is not preserved. (Though it is reproduced by the next OUT to `#FE` after resume.)
- **The floating bus state**: The internal ULA latch used to generate the floating bus pattern is not preserved.
- **The contention timing state**: The current T-state counter (used for contention emulation) is not preserved.
- **The `#1FFD` paging port** (+2A/+3): Critical for +2A/+3 software.
- **The +3 FDC state**: Floppy controller registers, motor state, etc.
- **The Beta 128 disk controller state**: FDC registers, disk position, motor state.
- **The Kempston joystick / mouse port state**: Not preserved.
- **The Z80 internal state beyond the registers**: MEMPTR (the undocumented W/Z register), Q (the undocumented flag used by some instructions), the internal ALU latches. These are lost — important for some demos and copy-protection schemes that rely on undocumented Z80 behaviour.
- **The interrupt pending state**: Whether an interrupt is "queued" (e.g., from the INT line being held low during the last instruction).

### 4.3 Practical consequences of missing state

The missing state has several practical consequences:

- **AY music glitches**: When loading a .SNA of a game with AY music, the music often glitches for a moment as the player re-initialises the AY registers. Most games recover quickly, but some do not.
- **+2A/+3 software may not work**: Software that uses the +2A/+3 paging modes (Modes 1, 2, or 3 — see [../../04_operating_systems/rom_plus2.md](../../04_operating_systems/rom_plus2.md) §6) cannot be reliably snapshotted as .SNA.
- **TR-DOS software may not resume correctly**: Some TR-DOS-using software relies on the Beta 128 FDC's internal state (e.g., the current track, the motor state). These are not preserved by .SNA.
- **Undocumented Z80 features are lost**: Software that uses MEMPTR (e.g., demos that use `BIT n,(HL)` followed by reading the undocumented `W` register) will not resume correctly.
- **Tape loaders and disk operations in progress**: A .SNA taken mid-load or mid-disk-operation will not resume the I/O.

For most use cases (loading a game that has finished its tape/disk loading and is running normally), .SNA works perfectly. For pathological cases, you need .Z80 or .SZX.

---

## §5. Writing a .SNA Loader

A reference loader for the 48K .SNA format is small enough to reproduce here. This is C-like pseudocode; the same logic applies to any language.

### 5.1 The 48K loader

```c
typedef struct {
    uint8_t  I;
    uint16_t HL_alt, DE_alt, BC_alt, AF_alt;
    uint16_t HL,     DE,     BC,     IY, IX;
    uint8_t  IFF1, IFF2, R;
    uint16_t AF;
    uint16_t SP;
    uint8_t  interrupt_mode;
} SNAHeader;

int load_48k_sna(const char *filename) {
    FILE *f = fopen(filename, "rb");
    if (!f) return -1;

    // Read the 27-byte header
    SNAHeader hdr;
    fread(&hdr, 1, 27, f);

    // Read 48 KB of RAM
    uint8_t ram[49152];
    fread(ram, 1, 49152, f);
    fclose(f);

    // Apply the state to the emulated Spectrum
    z80.I      = hdr.I;
    z80.HL_alt = hdr.HL_alt; z80.DE_alt = hdr.DE_alt;
    z80.BC_alt = hdr.BC_alt; z80.AF_alt = hdr.AF_alt;
    z80.HL     = hdr.HL;     z80.DE     = hdr.DE;
    z80.BC     = hdr.BC;     z80.IY     = hdr.IY;
    z80.IX     = hdr.IX;
    z80.IFF1   = hdr.IFF1 & 1; z80.IFF2 = hdr.IFF2 & 1;
    z80.R      = hdr.R;
    z80.A      = hdr.AF >> 8; z80.F = hdr.AF & 0xFF;
    z80.SP     = hdr.SP;
    z80.IM     = hdr.interrupt_mode & 3;

    // Copy RAM into the Spectrum's address space (#4000-#FFFF)
    memcpy(spectrum_ram + 0x4000, ram, 49152);

    // The PC is on the stack — pop it via a RET
    uint16_t pc = read_word(z80.SP);
    z80.SP += 2;
    z80.PC = pc;

    return 0;
}
```

The "pop PC via RET" trick is what makes this work without an explicit PC field.

### 5.2 The 128K loader

```c
int load_128k_sna(const char *filename) {
    FILE *f = fopen(filename, "rb");
    if (!f) return -1;

    // 27-byte header
    SNAHeader hdr;
    fread(&hdr, 1, 27, f);

    // First 3 banks (5, 2, 0): 49152 bytes
    uint8_t banks_5_2_0[49152];
    fread(banks_5_2_0, 1, 49152, f);

    // 4-byte extension header
    uint8_t ext[4];
    fread(ext, 1, 4, f);
    uint16_t pc        = ext[0] | (ext[1] << 8);
    uint8_t  port_7FFD = ext[2];
    uint8_t  trdos_paged = ext[3];

    // Remaining 5 banks (1, 3, 4, 6, 7): 81920 bytes
    uint8_t banks_other[81920];
    fread(banks_other, 1, 81920, f);
    fclose(f);

    // Apply header (same as 48K)
    apply_header_to_z80(&hdr);

    // Apply the bank data to the 128K memory model
    set_ram_bank(5, banks_5_2_0 + 0*16384);
    set_ram_bank(2, banks_5_2_0 + 1*16384);
    set_ram_bank(0, banks_5_2_0 + 2*16384);
    set_ram_bank(1, banks_other + 0*16384);
    set_ram_bank(3, banks_other + 1*16384);
    set_ram_bank(4, banks_other + 2*16384);
    set_ram_bank(6, banks_other + 3*16384);
    set_ram_bank(7, banks_other + 4*16384);

    // Apply the paging state
    write_port(0x7FFD, port_7FFD);

    // Apply TR-DOS state
    if (trdos_paged) {
        page_in_beta_rom();
    }

    // Set PC directly (128K variant stores PC explicitly)
    z80.PC = pc;

    return 0;
}
```

Note that the 128K loader does **not** pop PC from the stack — it uses the explicit PC field from the extension header.

### 5.3 Validation

A robust loader should validate the file before applying it:

- **File size**: must be exactly 49179 (48K) or 131103 (128K) bytes.
- **Interrupt mode**: bits 0–1 of byte 26 must be 0, 1, or 2.
- **IFF1/IFF2**: bits other than bit 0 should be ignored (treat as 0).
- **Reserved bits**: should be 0 but should not cause a load failure.

If validation fails, the loader should refuse to apply the snapshot. Applying a corrupt snapshot can leave the emulator in an inconsistent state.

---

## §6. Compatibility Across Emulators

Every major Spectrum emulator supports the .SNA format. Here is a summary of compatibility:

| Emulator | 48K .SNA load | 128K .SNA load | 48K .SNA save | 128K .SNA save | Notes |
|---|---|---|---|---|---|
| Fuse | ✅ | ✅ | ✅ | ✅ | Reference implementation |
| ZEsarUX | ✅ | ✅ | ✅ | ✅ | Also supports .SZX (its native format) |
| Spectaculator | ✅ | ✅ | ✅ | ✅ | |
| X128 | ✅ | ✅ | ✅ | ✅ | |
| SPX (SpecEmu) | ✅ | ✅ | ✅ | ✅ | |
| EightyOne | ✅ | ✅ | ✅ | ✅ | |
| UnrealSpeccy | ✅ | ✅ | ✅ | ✅ | Russian emulator; primary on Russian scene |
| ZXMAK2 | ✅ | ✅ | ✅ | ✅ | |
| CSpect | ✅ | ✅ | ✅ | ✅ | ZX Spectrum Next support |
| Klive | ✅ | ✅ | ✅ | ✅ | |
| z81 (ZX81) | n/a | n/a | n/a | n/a | ZX81 emulator — uses .P format instead |

In practice, you can assume that any Spectrum emulator written after 1995 supports .SNA. The 128K variant is supported by all emulators written after about 1999.

### 6.1 Compatibility quirks

A few quirks to be aware of:

- **Older emulators may not save the 128K variant correctly**. Some early emulators (late 1990s) saved 128K snapshots as 48K snapshots, losing the additional banks. If you find an old .SNA file from this era, it may be a 48K snapshot even though the source was a 128K machine.
- **The TR-DOS flag is interpreted differently** by some emulators. The standard is `0x00` / `0xFF`, but a few emulators use `0x00` / non-zero. Test against multiple emulators if you rely on this flag.
- **The interrupt mode byte's bits 2–7** are sometimes used by emulators to store extra state (e.g., the border colour from `OUT (#FE),...`). This is non-standard; ignore these bits when loading.

---

## §7. Limitations and Gotchas

The .SNA format has several limitations and gotchas that users should be aware of.

### 7.1 The PC-on-the-stack trick is fragile

The 48K format's reliance on PC being on the stack is fragile:

- If the snapshot was taken with SP pointing to a non-RAM address (e.g., a ROM address), the loader will read garbage as PC.
- If the snapshot was taken with SP pointing to an invalid address (e.g., `#0000`), the loader may crash.
- If the snapshot was taken immediately after a `PUSH` of something other than PC, the loader will retrieve the wrong value.

The 128K format's explicit PC field avoids these issues, but the 48K format is stuck with the trick for backwards compatibility.

### 7.2 No AY state means audio glitches

As mentioned in §4.3, loading a .SNA of AY-using software typically produces a brief audio glitch while the AY is re-initialised. For most software this is momentary, but for software that uses the AY for timing-critical effects (e.g., sample playback via the AY's envelope generator), the glitch can be more pronounced.

### 7.3 The R register is only 7 bits

The Z80's R register is 7 bits wide (bit 7 is set manually and does not increment). Some emulators save R as a full 8-bit value with bit 7 set, while others save it with bit 7 cleared. This can cause subtle differences in software that relies on R for timing (e.g., some demos that use R as a random number seed).

### 7.4 Russian clone state is lost

The .SNA format has no support for Russian clone state. A snapshot of, say, Pentagon software loaded into a Pentagon emulator via .SNA will work for the basics, but Pentagon-specific features (the extended memory banks, the Beta 128 disk interface state, the additional Turbo modes) will be in their default state, not the state at the time of the snapshot.

### 7.5 No metadata

The .SNA format has no metadata fields — no emulator name, no timestamp, no description, no author. If you need to annotate a snapshot, you must do so externally (e.g., via the filename or a sidecar file).

### 7.6 The +3 disk system is incompatible

Software that uses the +3's built-in disk system cannot be reliably snapshotted in .SNA. The +3 FDC state, the disk in the drive, and the current motor state are all lost.

---

## §8. Comparison with .Z80

The .Z80 format (see [z80_format.md](z80_format.md) for full details) is the other widely-used snapshot format. Here's how it compares to .SNA:

| Aspect | .SNA | .Z80 |
|---|---|---|
| Origin | 1992 (Arnt Gulbrandsen, JPP) | 1994 (Glen Lleston, Z80 emulator) |
| 48K support | ✅ | ✅ |
| 128K support | ✅ (extension) | ✅ (v2/v3) |
| Header size | 27 bytes | 30+ bytes (variable) |
| AY state | ❌ | ✅ (v2+) |
| +2A/+3 paging port | ❌ | ✅ (v3) |
| Clone hardware support | ❌ | ✅ (v3) |
| File compression | ❌ | ✅ (v2/v3, optional) |
| Metadata | ❌ | ✅ (v3) |
| Adoption | Universal | Universal |

In short, .Z80 is more capable but more complex; .SNA is simpler but more limited. Most emulators support both, and most users use whichever is more convenient for their workflow.

**Rule of thumb**: Use .SNA for simple 48K software. Use .Z80 (or .SZX) for 128K software, software with custom ROMs, or software that uses non-standard hardware.

---

## §9. Modern Status (2024)

Despite its age and limitations, the .SNA format remains **the most widely-supported** snapshot format in 2024. Every emulator supports it. Most online Spectrum software archives (World of Spectrum, InfoSeek, etc.) offer .SNA files for download.

However, .SNA is rarely the **preferred** format for new snapshots in 2024. Most modern emulators default to .Z80 or .SZX, which capture more state. The .SNA format is primarily used for:

- **Sharing snapshots with maximum compatibility** (since every emulator can load .SNA).
- **Distributing 48K games** (where the .SNA limitations don't matter).
- **Snapshot format conversion** (as a common intermediate format between emulators).

For new snapshots, .Z80 or .SZX is recommended. But the .SNA format is not going away — it remains the lowest-common-denominator snapshot format, and that role is unlikely to change.

---

## §10. Cross-References

### 10.1 Within the snapshots section

- **[z80_format.md](z80_format.md)** — The .Z80 snapshot format, the more capable alternative. Read this if .SNA's limitations are a problem for your use case.
- **[szx_format.md](szx_format.md)** — The .SZX snapshot format (ZEsarUX's native format), which captures even more state than .Z80.
- **[rzx_format.md](rzx_format.md)** — The .RZX input recording format, used for deterministic replay rather than static snapshots.

### 10.2 Outside the snapshots section

- **[../../04_operating_systems/rom_plus2.md](../../04_operating_systems/rom_plus2.md)** — The +2A/+3 ROM internals, including the four paging modes that .SNA cannot represent.
- **[../../04_operating_systems/rom_48k.md](../../04_operating_systems/rom_48k.md)** — The 48K ROM that is assumed by every 48K .SNA file.
- **[beta_disk_interface.md](../storage/beta_disk_interface.md)** — The Beta 128 disk interface, whose paged state is captured by the TR-DOS flag in 128K .SNA files.
- **[tape_format.md](../storage/tape_format.md)** — The on-tape data format, the alternative to snapshots for distributing Spectrum software.

### 10.3 External resources

- **World of Spectrum** (worldofspectrum.org) — The largest archive of .SNA files.
- **The .SNA format specification** — Various community-documented versions; the canonical reference is the format documentation included with the Fuse emulator source.

---

## License

This document is licensed under **Creative Commons Attribution-ShareAlike 4.0 International** (CC BY-SA 4.0). You are free to share and adapt this material, provided you give appropriate credit, indicate changes, and distribute derivative works under the same licence.
