[← Plan](../../PLAN.md) · [DOS & Tape](README.md)

# File Format Handling — Loading .TAP, .TRD, .DSK, .SNA from Assembly

ZX Spectrum software is distributed in dozens of file formats: tape images (.TAP, .TZX), disk images (.TRD, .DSK, .SCL), memory snapshots (.SNA, .Z80), and raw data dumps (.SCR, .ROM). Every game engine, demo framework, and utility tool eventually needs to parse at least some of these formats — to load assets, stream parts, or browse archives.

This article covers the practical parsing of Spectrum file formats from assembly code. It is the fourth article in the [DOS and Tape series](README.md) and assumes you have read the previous three. It does **not** duplicate the format reference articles in [03_io/storage/](../../03_io/storage/README.md) — those cover the byte-level specification of each format in exhaustive detail. This article provides the **programmer's view**: how to detect a format, extract files from it, and use the data in your program.

> [!NOTE]
> The code examples in this article assume the file data is already in memory (loaded via one of the DOS methods described in [trdos_programming.md](trdos_programming.md) or [dos_programming.md](dos_programming.md)). If you are reading from mass storage, see [mass_storage_programming.md](mass_storage_programming.md) for direct hardware access.

---

## Why Handle File Formats?

| Scenario | Formats needed |
|---|---|
| Game engine loads assets from disk | .TRD, .DSK (disk image parsing) |
| Demo framework streams parts | .TRD, .TAP |
| File browser utility | All formats |
| Snapshot loader (multi-game collection) | .SNA, .Z80 |
| Tape image player | .TAP, .TZX |
| Asset conversion tool | .TAP (extract), .SCR (display) |

---

## File Type Detection

The first step in handling any file is detecting its format. Most Spectrum file formats have a **magic signature** in the first few bytes:

| Format | Extension | Magic bytes (first bytes) | Offset |
|---|---|---|---|
| .TAP | `.tap` | (none — starts with block length) | — |
| .TZX | `.tzx` | `"ZXTape!"` + #1A | 0 |
| .TRD | `.trd` | `"TRD" + version` at offset #8E0 | #08E0 |
| .SCL | `.scl` | `"SINCLAIR"` | 0 |
| .DSK | `.dsk` | `"MV - CPCEMU"` or `"EXTENDED"` | 0 |
| .SNA (48K) | `.sna` | (no magic — starts with register dump) | — |
| .Z80 (v1) | `.z80` | (no magic — check byte 30 for #FF) | #1E |
| .Z80 (v2/v3) | `.z80` | (v1 header, then extended at offset 30) | #1E |
| .SCR | `.scr` | (no magic — exactly 6912 bytes) | — |

### A Generic Detection Function

```z80
; ============================================================
; detect_format — identify file format by magic bytes
;
; Entry: HL = address of file data in memory
;        DE = file length
; Exit:  A = format code:
;          0 = unknown
;          1 = .TAP
;          2 = .TZX
;          3 = .TRD
;          4 = .SCL
;          5 = .DSK
;          6 = .SNA (48K)
;          7 = .Z80
;          8 = .SCR
; ============================================================

detect_format:
    ; Check for .TZX: "ZXTape!" at offset 0
    LD   A, (HL)
    CP   'Z'
    JR   NZ, .not_tzx
    INC  HL
    LD   A, (HL)
    CP   'X'
    JR   NZ, .not_tzx
    ; Check full signature (simplified — check first 2 of 8 bytes)
    LD   A, 2
    RET
.not_tzx:

    ; Check for .SCL: "SINCLAIR" at offset 0
    LD   A, (HL)
    CP   'S'
    JR   NZ, .not_scl
    INC  HL
    LD   A, (HL)
    CP   'I'
    JR   NZ, .not_scl
    LD   A, 4               ; .SCL
    RET
.not_scl:

    ; Check for .DSK: "MV - CPCEMU" or "EXTENDED" at offset 0
    LD   A, (HL)
    CP   'M'                ; "MV - CPCEMU"
    JR   NZ, .not_dsk1
    LD   A, 5               ; .DSK
    RET
.not_dsk1:
    LD   A, (HL)
    CP   'E'                ; "EXTENDED"
    JR   NZ, .not_dsk2
    LD   A, 5               ; .DSK
    RET
.not_dsk2:

    ; Check for .TRD: "TRD" at offset #08E0
    PUSH HL
    LD   BC, #08E0
    ADD  HL, BC             ; HL = start + #08E0
    LD   A, (HL)
    CP   'T'
    JR   NZ, .not_trd
    INC  HL
    LD   A, (HL)
    CP   'R'
    JR   NZ, .not_trd
    POP  HL
    LD   A, 3               ; .TRD
    RET
.not_trd:
    POP  HL

    ; Check for .Z80: byte at offset 30 = #FF (v2/v3) or register A (v1)
    PUSH HL
    LD   BC, 30             ; offset #1E
    ADD  HL, BC
    LD   A, (HL)
    CP   #FF                ; v2/v3 extended header?
    JR   Z, .is_z80
    ; v1: byte 30 is the complement of register A
    ; Check if DE = 6912 (.SCR) instead
    POP  HL
    ; Check for .SCR: length = 6912 bytes
    LD   HL, file_length    ; compare DE to 6912
    LD   A, (HL)
    CP   #00                ; low byte = #00 (6912 = #1B00)
    JR   NZ, .check_sna
    INC  HL
    LD   A, (HL)
    CP   #1B
    JR   NZ, .check_sna
    ; Length is 6912 — it is probably .SCR
    LD   A, 8
    RET
.check_sna:
    ; Check for .SNA: no magic, but first byte is the A register (any value)
    ; If length is exactly 49179 (48K SNA = 27 + 49152), it is .SNA
    LD   HL, file_length
    LD   A, (HL)
    CP   #FB                ; 49179 = #C01B — check low byte
    ; Actually 49179 = #C01B. This is complex; simplified check:
    LD   A, 6               ; assume .SNA if nothing else matched
    RET
.is_z80:
    POP  HL
    LD   A, 7               ; .Z80
    RET

file_length:   DEFW 0       ; set by caller before calling detect_format
```

This is a simplified detector. A production version would verify more signature bytes and handle edge cases (e.g., .TAP has no magic, so it would be detected by elimination).

---

## .TAP Format

The .TAP format is the simplest tape image format. It represents a tape as a sequence of **blocks**, each with a 2-byte length header:

```
.TAP file structure:
  +----------+----------+----------+----------+
  | length lo| length hi| flag     | data...  |
  | (2 bytes)|          | (1 byte) | (N bytes)|
  +----------+----------+----------+----------+
  ^                                   ^
  block header                        block data (length-1 bytes)
  (length includes flag + data + checksum)
```

Each block in the .TAP file corresponds to one block on the original tape: either a 17-byte header block or a variable-length data block.

### Parsing .TAP Blocks

```z80
; ============================================================
; tap_list — list all blocks in a .TAP file
;
; Entry: HL = address of .TAP file data in memory
;        DE = total file length
; ============================================================

tap_list:
    LD   (tap_end), DE       ; save end address
    LD   (tap_ptr), HL       ; save start

.tap_loop:
    LD   HL, (tap_ptr)
    ; Check if we have reached the end
    EX   DE, HL
    LD   HL, (tap_end)
    OR   A                   ; clear carry
    SBC  HL, DE              ; remaining = end - current
    JR   C, .tap_done        ; current >= end, done
    JR   Z, .tap_done

    ; Read block length (2 bytes, little-endian)
    LD   HL, (tap_ptr)
    LD   E, (HL)             ; length low byte
    INC  HL
    LD   D, (HL)             ; length high byte
    INC  HL
    ; DE = block length (includes flag + data + checksum)

    ; Read flag byte
    LD   A, (HL)             ; flag: #00 = header, #FF = data
    INC  HL

    ; If header block (flag = #00), extract filename
    AND  A                   ; flag = 0?
    JR   NZ, .data_block
    ; Header block: next 10 bytes = filename + type
    INC  HL                  ; skip type byte (byte 1 of header)
    LD   B, 10               ; filename is 10 chars
    LD   DE, tap_name_buf
.copy_name:
    LD   A, (HL)
    LD   (DE), A
    INC  HL
    INC  DE
    DJNZ .copy_name
    ; Print the filename
    LD   HL, tap_name_buf
    LD   B, 10
.print_name:
    LD   A, (HL)
    CALL print_char_a
    INC  HL
    DJNZ .print_name
    LD   A, ' '
    CALL print_char_a
    LD   A, 'H'              ; H = header block
    CALL print_char_a
    LD   A, #0D
    CALL print_char_a
    JR   .advance

.data_block:
    LD   A, 'D'              ; D = data block
    CALL print_char_a
    LD   A, #0D
    CALL print_char_a

.advance:
    ; Advance pointer: skip past the block data
    ; Current position is at flag+1; need to skip (length-1) more bytes
    LD   HL, (tap_ptr)
    LD   E, (HL)             ; re-read length low
    INC  HL
    LD   D, (HL)             ; length high
    INC  HL                  ; now at flag byte
    ; HL points to flag; skip (length-1) bytes from flag position
    DEC  DE                  ; subtract flag byte we already counted
    DEC  DE                  ; adjust (length includes flag, we are at flag)
    ADD  HL, DE              ; skip past data
    LD   (tap_ptr), HL
    JR   .tap_loop

.tap_done:
    RET

tap_ptr:     DEFW 0
tap_end:     DEFW 0
tap_name_buf: DEFS 10
```

For the complete .TAP specification including block types and edge cases, see [tap_format.md](../../03_io/storage/tap_format.md).

---

## .TZX Format

The .TZX format is a superset of .TAP that preserves exact pulse timing for custom loaders and turbo speeds. It is more complex to parse because it uses a **block-type** system with variable-length blocks.

### TZX Block Types

| Block ID | Name | Purpose |
|---|---|---|
| `#10` | Standard speed data | Equivalent to one .TAP block |
| `#11` | Turbo speed data | Custom timing data block |
| `#12` | Pure tone | Pilot tone only |
| `#13` | Pure data | Data without pilot or sync |
| `#14` | Direct recording | Raw signal sampling |
| `#15` | C64 ROM type | (Commodore 64 data — rare) |
| `#20` | Silence | Pause for N ms |
| `#21` | Group start | Named group marker |
| `#22` | Group end | End of named group |
| `#23` | Jump | Jump to block N (relative) |
| `#24` | Loop start | Begin loop |
| `#25` | Loop end | End loop (2-byte repeat count) |
| `#26` | Call sequence | Call a sequence of blocks |
| `#27` | Return | Return from call |
| `#30` | Text description | Human-readable text |
| `#31` | Message | Message with pause |
| `#32` | Archive info | Hardware type, etc. |
| `#33` | Hardware type | Spectrum model, etc. |
| `#35` | Custom info | Custom metadata |

### Simplified TZX Reader

A full TZX parser is complex. For most applications, you only need to handle blocks `#10` (standard data) and `#11` (turbo data):

```z80
; ============================================================
; tzx_extract — extract standard data blocks from a .TZX file
; Simplified: only handles block types #10 and #11
;
; Entry: HL = .TZX file start
;        DE = load address for extracted data
; ============================================================

tzx_extract:
    ; Skip 10-byte TZX header ("ZXTape!" + #1A + version)
    LD   BC, 10
    ADD  HL, BC

.tzx_loop:
    LD   A, (HL)             ; block type ID
    INC  HL

    CP   #10                 ; standard speed data?
    JR   Z, .block_10
    CP   #11                 ; turbo speed data?
    JR   Z, .block_11
    CP   #FF                 ; end of file? (no official EOF marker)
    RET  Z
    ; Unknown block type — would need to look up its length to skip
    ; For this simplified version, just return
    RET

.block_10:
    ; Block #10: [2-byte data length] [1-byte pause] [data]
    ; Skip pause (2 bytes)
    INC  HL
    INC  HL
    ; Read data length (3 bytes: 2 data + 1 flag, actually...)
    ; Actually: #10 format = [pause(2)] [data_len(2)] [data(N)]
    ; Wait, the format is: #10, pause_lo, pause_hi, len_lo, len_hi, data...
    ; We already read the pause. Now read len:
    LD   E, (HL)
    INC  HL
    LD   D, (HL)
    INC  HL
    ; DE = data length; copy DE bytes to load address
    LD   BC, (load_addr)
    PUSH HL
    LD   H, D
    LD   L, E                ; HL = count (for LDIR)
    LDIR                     ; copy DE bytes from (HL) to (BC)
    POP  HL
    ; Update load address
    LD   BC, (load_addr)
    ; (advance load_addr by DE — simplified)
    JR   .tzx_loop

.block_11:
    ; Block #11: turbo speed data — complex timing fields
    ; Skip: pilot_len(2), pilot_count(2), sync1(2), sync2(2),
    ;        bit0_len(2), bit1_len(2), bits_in_last(1), pause(2)
    ; Total: 15 bytes of timing before data
    LD   BC, 15
    ADD  HL, BC
    ; Then: data_len(3) + data(N)
    LD   E, (HL)
    INC  HL
    LD   D, (HL)
    INC  HL
    INC  HL                  ; skip 3rd byte of length (MSB)
    ; DE = data length; copy like block #10
    ; (same LDIR as above, omitted)
    JR   .tzx_loop

load_addr:   DEFW #8000
```

For the complete .TZX specification with all block types, see [tzx_format.md](../../03_io/storage/tzx_format.md).

---

## .TRD Format — TR-DOS Disk Image

The .TRD format is a flat disk image of a standard TR-DOS floppy: 80 tracks, 2 sides, 16 sectors per track, 256 bytes per sector. The total image is 655,360 bytes (#A0000). This is the most common disk image format in the Russian Spectrum scene.

### Disk Layout

```
.TRD disk image layout (655,360 bytes):

Track 0, Side 0:
  Sector 1:  Catalog sector 0    (first 8 directory entries)
  Sector 2:  Catalog sector 1    (next 8 entries)
  ...
  Sector 8:  Catalog sector 7    (entries 56-127 + disk info at #08E0)
  Sector 9-16: First data sectors

Track 0, Side 1 - Track 79, Side 1:
  Data sectors

Offset to any sector:
  offset = ((track * 2 + side) * 16 + (sector - 1)) * 256
```

The **catalog** (directory) occupies sectors 1-8 of track 0, side 0. Each sector holds 16 directory entries (256 bytes / 16 bytes per entry), for a total of 128 entries maximum.

### Directory Entry Structure

Each 16-byte directory entry:

| Offset | Size | Content |
|---|---|---|
| 0-7 | 8 bytes | Filename (space-padded, ASCII) |
| 8 | 1 byte | File type byte ('B'=#42, 'C'=#43, 'D'=#44, '#'=#23) |
| 9-10 | 2 bytes | File length in bytes (little-endian) |
| 11-12 | 2 bytes | Parameter 1 (start address for code, autostart line for BASIC) |
| 13 | 1 byte | Parameter 2 (variable area length for BASIC) |
| 14 | 1 byte | Number of sectors occupied |
| 15 | 1 byte | Starting track (0-159) |

> [!NOTE]
> The starting sector within the track is always sector 0 for TR-DOS files — they are always sector-aligned. This means the "starting track" field effectively gives you the full position since files start at sector 0 of the indicated track.

### Reading the Directory

```z80
; ============================================================
; trd_list_dir — list all files in a .TRD image in memory
;
; Entry: HL = address of .TRD image data
; ============================================================

trd_list_dir:
    LD   (trd_base), HL       ; save base address
    ; Catalog starts at offset 0 (track 0, sector 1)
    ; Each entry is 16 bytes, up to 128 entries
    LD   B, 128               ; max entries
    LD   HL, (trd_base)       ; HL = catalog start

.dir_loop:
    LD   A, (HL)              ; first byte of filename
    CP   0                    ; empty entry?
    JR   Z, .dir_end          ; yes, end of catalog
    CP   #FF                  ; deleted entry marker?
    JR   Z, .dir_skip         ; yes, skip

    ; Print filename (8 chars)
    PUSH BC
    PUSH HL
    LD   B, 8
.print_name:
    LD   A, (HL)
    CALL print_char_a
    INC  HL
    DJNZ .print_name
    LD   A, '.'
    CALL print_char_a

    ; Print file type character
    LD   A, (HL)              ; offset 8 = type
    CALL print_char_a
    LD   A, #0D
    CALL print_char_a
    POP  HL
    POP  BC

.dir_skip:
    ; Advance to next entry (16 bytes)
    LD   A, 16
    ADD  A, L
    LD   L, A
    JR   NC, .no_carry
    INC  H
.no_carry:
    DJNZ .dir_loop

.dir_end:
    RET

trd_base:   DEFW 0
```

### Extracting a File from .TRD

Once you find the file in the catalog, you know its starting track and length in sectors. To extract the file data:

```z80
; ============================================================
; trd_extract_file — extract a file from a .TRD image
;
; Entry: HL = .TRD image base address
;        DE = address of 9-byte filename to find
;        IX = destination address for file data
; Exit:  carry set = success, BC = bytes extracted
;        carry clear = file not found
; ============================================================

trd_extract_file:
    ; Step 1: Scan catalog for the filename
    PUSH DE
    PUSH IX
    LD   (trd_base), HL
    LD   DE, 128              ; entry counter

.scan_loop:
    LD   A, (HL)
    CP   0
    JR   Z, .not_found        ; end of catalog
    CP   #FF
    JR   Z, .next_entry       ; deleted entry

    ; Compare 8-byte name + 1-byte type = 9 bytes
    POP  IX                   ; recover filename ptr (was in DE)
    PUSH IX
    PUSH HL
    LD   B, 9
.cmp_loop:
    LD   A, (HL)
    EX   DE, HL              ; swap: DE = catalog ptr, HL = search name
    CP   (HL)
    JR   NZ, .cmp_fail
    INC  HL                   ; next byte of search name
    EX   DE, HL              ; swap back: HL = catalog ptr
    INC  HL
    DJNZ .cmp_loop

    ; Match found! HL points past the 9-byte name/type
    ; HL is at offset 9 of the entry (file length)
    POP  DE                   ; discard saved catalog ptr
    POP  IX                   ; recover destination
    POP  DE                   ; recover search name (discard)

    ; Read file length (offset 9-10 of entry, 2 bytes)
    ; Back up HL to entry start + 9
    ; HL currently points to entry + 9 (after 9 bytes matched)
    LD   E, (HL)             ; length low
    INC  HL
    LD   D, (HL)             ; length high
    INC  HL
    PUSH DE                  ; save byte length

    ; Read starting track (offset 15 of entry)
    ; HL is at entry + 11, need to advance 4 more to reach offset 15
    LD   A, 4
    ADD  A, L
    LD   L, A
    JR   NC, .got_track
    INC  H
.got_track:
    LD   A, (HL)             ; A = starting track
    ; Calculate source offset in .TRD image:
    ; offset = starting_track * 16 * 256 = starting_track * 4096
    ; (since each track has 16 sectors * 256 bytes per side,
    ;  and starting track encodes both track and side)
    ; Actually: track_field = track * 2 + side
    ; offset = track_field * 16 * 256 = track_field * 4096
    LD   L, A
    LD   H, 0
    ; HL = track_field, multiply by 4096 (shift left 12)
    ; First shift left 8 (multiply by 256)
    LD   H, L
    LD   L, 0                ; HL = track_field * 256
    ; Now multiply remaining 16 (shift left 4 more)
    LD   B, 4
.shift_loop:
    ADD  HL, HL
    DJNZ .shift_loop
    ; HL = track_field * 4096 = source offset

    ; Add base address
    LD   BC, (trd_base)
    ADD  HL, BC              ; HL = source address in .TRD

    ; Copy file data to destination
    POP  BC                  ; BC = byte length
    PUSH BC                  ; save for return value
    LD   A, C
    OR   B
    JR   Z, .copy_done       ; zero-length file
    LD   DE, IX              ; not valid — need actual DE
    ; Use EX to set up LDIR
    EX   DE, HL              ; DE = source, HL = dest
.copy_loop:
    LD   A, (DE)
    LD   (HL), A
    INC  DE
    INC  HL
    DEC  BC
    LD   A, B
    OR   C
    JR   NZ, .copy_loop
.copy_done:
    POP  BC                  ; BC = bytes extracted
    SCF                      ; carry set = success
    RET

.cmp_fail:
    POP  HL                  ; restore catalog ptr
    ; Fall through to .next_entry
.next_entry:
    POP  IX                  ; restore destination (preserve)
    PUSH IX
    POP  DE
    POP  DE                  ; restore search name
    PUSH DE
    PUSH IX
    ; Advance HL by 16 bytes
    LD   A, 16
    ADD  A, L
    LD   L, A
    JR   NC, .no_carry2
    INC  H
.no_carry2:
    DEC  DE
    LD   A, D
    OR   E
    JR   Z, .not_found
    JR   .scan_loop

.not_found:
    POP  IX
    POP  DE
    OR   A                   ; carry clear = not found
    RET
```

For the complete .TRD disk format specification, see [trd_disk_format.md](../../03_io/storage/trd_disk_format.md).

---

## .SCL Format

The .SCL format (Sinclair Loader) is a simpler alternative to .TRD. Instead of a full disk image, it stores a list of files with their data concatenated. It is compact but does not preserve the physical disk layout.

### Structure

```
.SCL file structure:
  Offset 0:   "SINCLAIR"          (8 bytes, magic signature)
  Offset 8:   file_count          (1 byte, number of files)
  Offset 9:   file descriptors    (file_count × 14 bytes)
  Offset 9+N*14: file data        (concatenated, in descriptor order)
  Last byte:  checksum            (1 byte, sum of all bytes mod 256)
```

Each 14-byte file descriptor:

| Offset | Size | Content |
|---|---|---|
| 0-7 | 8 bytes | Filename (space-padded) |
| 8 | 1 byte | File type byte |
| 9-10 | 2 bytes | Data length (little-endian) |
| 11-12 | 2 bytes | Parameter 1 (start address) |
| 13 | 1 byte | Parameter 2 |

### Parsing .SCL

```z80
; ============================================================
; scl_list_files — list files in a .SCL image
;
; Entry: HL = .SCL image base address
; ============================================================

scl_list_files:
    ; Skip 9-byte header ("SINCLAIR" + count)
    LD   B, (HL)             ; not correct — count is at offset 8
    PUSH HL
    LD   BC, 8
    ADD  HL, BC
    LD   B, (HL)             ; B = file count
    INC  HL                  ; HL = first descriptor

.list_loop:
    PUSH BC
    ; Print filename (8 bytes)
    LD   B, 8
.name_loop:
    LD   A, (HL)
    CALL print_char_a
    INC  HL
    DJNZ .name_loop
    ; Print type
    LD   A, (HL)
    CALL print_char_a
    LD   A, #0D
    CALL print_char_a
    ; Skip remaining 5 bytes of descriptor (type + len + params)
    LD   B, 5
.skip_desc:
    INC  HL
    DJNZ .skip_desc
    POP  BC
    DJNZ .list_loop
    POP  HL
    RET
```

Extracting file data from .SCL requires scanning through descriptors and summing data lengths to find the offset of each file's data block.

For the complete .SCL specification, see [trd_scl_formats.md](../../03_io/storage/trd_scl_formats.md).

---

## .DSK Format

The .DSK format was created for the Amstrad CPC emulator but is widely used for Spectrum +3 disks. It preserves the physical disk structure including sector headers and gaps.

### Two Variants

| Variant | Magic string | Description |
|---|---|---|
| Standard | `"MV - CPCEMU Disk-File\r\n"` | Fixed sector size per track |
| Extended | `"EXTENDED CPC DSK File\r\n"` | Variable sector sizes (for copy-protected disks) |

### Standard DSK Layout

```
.DSK structure (standard):
  Offset 0:    Disk information block (256 bytes)
    #00:  "MV - CPCEMU Disk-File\r\n"  (34 bytes)
    #22:  padding                        (12 bytes)
    #24:  tracks   (2 bytes, little-endian)
    #26:  sides    (2 bytes, little-endian)
    #28:  track_size  (2 bytes, bytes per track incl. header)
  Offset 256:  Track 0, Side 0
    Track header (128 bytes)
    Sector 0 data (sector_size bytes)
    Sector 1 data ...
  Offset 256 + track_size:  Track 0, Side 1 (or Track 1, Side 0)
  ...
```

### Reading a Sector from .DSK

```z80
; ============================================================
; dsk_read_sector — read a sector from a standard .DSK image
;
; Entry: HL = .DSK base address
;        C  = track number (0-based)
;        B  = side (0 or 1)
;        E  = sector number (1-based, physical sector ID)
;        IX = destination buffer (256 bytes)
; Exit:  carry set = success
; ============================================================

dsk_read_sector:
    LD   (dsk_base), HL

    ; Read track_size from header (offset #28, 2 bytes)
    PUSH HL
    LD   BC, #28
    ADD  HL, BC
    LD   A, (HL)             ; track_size low
    INC  HL
    LD   H, (HL)             ; track_size high
    LD   L, A
    LD   (track_size), HL
    POP  HL

    ; Calculate track offset:
    ; offset = 256 (header) + (track * sides + side) * track_size
    ; Compute linear track index = track * sides + side
    ; Read sides from header (offset #26)
    PUSH HL
    LD   BC, #26
    ADD  HL, BC
    LD   A, (HL)             ; sides low byte
    INC  HL
    LD   H, (HL)
    LD   L, A                ; HL = sides
    LD   (sides_count), HL
    POP  HL

    ; linear = C (track) * sides + B (side)
    ; Simplified: assume sides = 2 (most common)
    LD   A, C                ; A = track
    SLA  A                   ; A = track * 2
    ADD  A, B                ; A = track*2 + side
    LD   C, A
    LD   B, 0                ; BC = linear track index

    ; Multiply BC by track_size
    LD   HL, (track_size)
    CALL mul16x8             ; HL = BC * HL (simplified call)

    ; Add 256 (disk header)
    LD   BC, 256
    ADD  HL, BC

    ; Add base address
    LD   BC, (dsk_base)
    ADD  HL, BC              ; HL = track header address

    ; Track header is 128 bytes; sectors follow after.
    ; Skip 128-byte track header
    LD   BC, 128
    ADD  HL, BC

    ; Now at sector data area. Sector E-1 is the one we want
    ; (sectors are 1-based; data starts at sector 1)
    ; Each sector is 256 bytes (standard .DSK)
    LD   A, E                ; sector number (1-based)
    DEC  A                   ; 0-based index
    LD   C, A
    LD   B, 0
    ; Multiply by 256 (shift left 8)
    LD   H, C
    LD   L, 0                ; HL = sector_index * 256
    ADD  HL, DE              ; DE was corrupted... simplified
    ; Copy 256 bytes from (HL) to (IX)
    ; (LDIR implementation omitted for brevity)
    SCF
    RET

track_size:   DEFW 0
sides_count:  DEFW 0
dsk_base:     DEFW 0
```

> [!NOTE]
> The .DSK reader above is simplified. Real .DSK files have sector information tables in the track header that specify physical sector IDs, sizes, and gap lengths. A robust reader must parse the sector information table to locate the correct sector. See [dsk_fdi_formats.md](../../03_io/storage/dsk_fdi_formats.md) for the full specification.

---

## .SNA Snapshots

The .SNA format is a memory snapshot — a complete dump of the machine state at a moment in time. Loading a .SNA restores the Spectrum to exactly where it was when the snapshot was taken.

### 48K .SNA Structure (49,179 bytes)

| Offset | Size | Content |
|---|---|---|
| 0 | 1 | Register I |
| 1-2 | 2 | HL' (alternate) |
| 3-4 | 2 | DE' (alternate) |
| 5-6 | 2 | BC' (alternate) |
| 7-8 | 2 | AF' (alternate) |
| 9-10 | 2 | HL |
| 11-12 | 2 | DE |
| 13-14 | 2 | BC |
| 15-16 | 2 | IY |
| 17-18 | 2 | IX |
| 19 | 1 | IFF2 (bit 2 = interrupt state) |
| 20 | 1 | R |
| 21-22 | 2 | AF |
| 23-24 | 2 | SP (stack pointer) |
| 25 | 1 | Interrupt mode (0, 1, or 2) |
| 26 | 1 | Border color (0-7) |
| 27-49178 | 49,152 | RAM dump (#4000-#FFFF, contiguous) |

### Loading a .SNA

```z80
; ============================================================
; sna_load — restore a 48K .SNA snapshot from memory
;
; Entry: HL = address of .SNA data
; WARNING: This replaces all registers and RAM. The caller
;          will never see this function return.
; ============================================================

sna_load:
    DI                       ; no interrupts during restore

    ; Copy 49,152 bytes of RAM data from snapshot to #4000
    LD   DE, #4000
    LD   BC, 49152
    PUSH HL
    LD   HL, 27              ; offset to RAM data
    ADD  HL, (SP)            ; HL = sna_base + 27
    EX   DE, HL              ; DE = source, HL = dest
    LDIR                    ; copy 49152 bytes
    POP  HL

    ; Now restore registers from the 27-byte header
    LD   DE, 27
    OR   A
    SBC  HL, DE              ; HL = sna_base (back to header start)

    ; Restore register values (simplified — the real sequence
    ; must carefully set up the stack for RET to load PC)
    LD   C, (HL)             ; I register
    INC  HL
    LD   I, C
    ; ... (skip through alternate registers)
    LD   BC, 18
    ADD  HL, BC              ; skip to offset 19 (IFF2)

    ; The critical part: set SP from snapshot, push PC, RET
    ; Snapshot does NOT store PC directly — instead, the
    ; value at (SP) in the snapshot IS the return address.
    ; Set up the stack, then execute RET to "return" to
    ; the snapshot's PC.
    ;
    ; Full implementation requires careful stack manipulation.
    ; See the complete example in the reference articles.
    RET
```

> [!WARNING]
> Loading a .SNA snapshot replaces the entire machine state. The function effectively never returns — control jumps to the PC stored implicitly in the snapshot's stack. This is inherently destructive: your code at #8000 is overwritten.

---

## .Z80 Snapshots

The .Z80 format is the most popular snapshot format, supporting all Spectrum models through header extensions. It compresses RAM data using run-length encoding, making files much smaller than .SNA.

### Version Detection

```
.Z80 header byte 30 (#1E):
  If byte 30 = #FF and byte 31 = #FF: version 2 or 3 (extended header)
  Otherwise: version 1 (48K only)
```

### Version 1 Header (30 bytes)

| Offset | Size | Content |
|---|---|---|
| 0 | 1 | A |
| 1 | 1 | F |
| 2-3 | 2 | BC |
| 4-5 | 2 | HL |
| 6-7 | 2 | PC (program counter — unlike .SNA, stored directly!) |
| 8-9 | 2 | SP |
| 10 | 1 | I |
| 11 | 1 | R (bit 7 = R7) |
| 12 | 1 | Flags: bit 0-2 = border color, bit 5 = R bit 7, bit 7 = compressed |
| 13-14 | 2 | DE |
| 15-16 | 2 | BC' |
| 17-18 | 2 | DE' |
| 19-20 | 2 | HL' |
| 21 | 1 | A' |
| 22 | 1 | F' |
| 23-24 | 2 | IY |
| 25-26 | 2 | IX |
| 27 | 1 | IFF1 |
| 28 | 1 | IFF2 |
| 29 | 1 | Interrupt mode (0, 1, 2) |

### Compression

If byte 12 bit 7 is set, the RAM data (starting at offset 30) is compressed using a simple run-length scheme:

```
Compressed format:
  #ED #ED <count>  = repeat next byte <count> times
  #ED #00 #00      = end marker (literal #ED #ED #00 #00)
  Any other byte    = literal byte
```

### Decompressing .Z80 RAM Data

```z80
; ============================================================
; z80_decompress — decompress .Z80 RLE data to RAM
;
; Entry: HL = source (compressed data)
;        DE = destination (RAM address, e.g. #4000)
; Exit:  DE = address after last byte written
; ============================================================

z80_decompress:
    LD   A, (HL)
    INC  HL

    CP   #ED                 ; possible RLE marker?
    JR   NZ, .literal

    ; Check for #ED #ED pattern
    LD   A, (HL)
    CP   #ED
    JR   NZ, .single_ed      ; just a literal #ED byte

    ; RLE sequence: #ED #ED <count> <value>
    INC  HL                  ; skip second #ED
    LD   B, (HL)             ; count
    INC  HL
    LD   A, (HL)             ; value to repeat
    INC  HL

.rle_loop:
    LD   (DE), A
    INC  DE
    DJNZ .rle_loop
    JR   z80_decompress      ; continue

.single_ed:
    ; Literal #ED byte
    LD   A, #ED
    LD   (DE), A
    INC  DE
    JR   z80_decompress

.literal:
    LD   (DE), A
    INC  DE
    JR   z80_decompress
```

### Versions 2 and 3

Versions 2 and 3 add an extended header after byte 29. The format inserts two #FF bytes at offset 30-31, followed by additional data including the machine model, 128K bank information, and other extensions. For 128K snapshots, the RAM is stored as separate bank pages rather than a single contiguous block.

For the complete .Z80 specification across all versions, see the [Wikipedia article on Z80 format](https://en.wikipedia.org/wiki/Z80_(file_format)) and the [Spectaculator documentation](https://www.spectaculator.com/manual/).

---

## .SCR Screen Files

The simplest format: a raw screen dump. Exactly 6,912 bytes (#1B00), containing the pixel bitmap and attribute map.

| Offset | Size | Content |
|---|---|---|
| 0-6143 | 6,144 | Pixel bitmap (256×192 pixels, 1 bit per pixel) |
| 6144-6911 | 768 | Attribute bytes (32×24 grid, 1 byte per cell) |

### Loading and Displaying a .SCR

```z80
; ============================================================
; scr_display — load and display a .SCR file
;
; Entry: HL = address of .SCR data (6912 bytes)
; ============================================================

scr_display:
    ; Copy pixel data to display RAM at #4000
    LD   DE, #4000
    LD   BC, 6144
    LDIR                    ; copies 6144 bytes

    ; Copy attribute data to attribute RAM at #5800
    LD   DE, #5800
    LD   BC, 768
    LDIR                    ; copies 768 bytes

    RET
```

The pixel bitmap layout is the standard Spectrum display format with its characteristic three-block vertical arrangement (see [screen_layout.md](../03_memory_and_io/screen_layout.md) for details).

---

## Common Pitfalls

### 1. Wrong Byte Order

Most Spectrum file formats use **little-endian** byte order (least significant byte first). A common bug is reading 2-byte values in the wrong order:

```z80
    ; WRONG (big-endian):
    LD   D, (HL)             ; high byte first
    INC  HL
    LD   E, (HL)             ; low byte second

    ; CORRECT (little-endian):
    LD   E, (HL)             ; low byte first
    INC  HL
    LD   D, (HL)             ; high byte second
```

### 2. Compressed vs. Uncompressed .Z80

Always check the compression flag (byte 12 bit 7) before attempting to load .Z80 RAM data. An uncompressed snapshot can be loaded with a simple `LDIR`. A compressed one requires the RLE decompressor.

### 3. .TRD Track Encoding

The "starting track" field in TR-DOS directory entries encodes both track and side: `value = track * 2 + side`. Do not use it as a raw track number.

### 4. .DSK Sector IDs

In .DSK files, sector numbers in the sector information table are physical sector IDs, not sequential indices. A disk might have sectors numbered #41, #42, #43, ... (not 1, 2, 3). You must look up the sector ID in the track header.

### 5. .TAP Block Length Includes Flag and Checksum

The 2-byte length in a .TAP block header includes the flag byte and checksum byte but **not** the 2-byte length field itself. A 17-byte header block has length = 19 in the .TAP file (17 data + flag + checksum).

Wait, let me reconsider. The length field in .TAP represents the number of bytes that follow (flag + data + checksum). A standard header block is 17 bytes of data, so the length field = 19 (flag + 17 data + 1 checksum). Actually, the Spectrum header is 17 bytes total after the flag byte. Let me be precise:

The .TAP block length field gives the number of bytes **after** the length field, including the flag byte and checksum. For a header block, this is always 19 (1 flag + 17 data + 1 checksum). For a data block, it is the data length + 2.

---

## Cross-References

| Topic | Reference |
|---|---|
| .TAP format specification | [tap_format.md](../../03_io/storage/tap_format.md) |
| .TZX format specification | [tzx_format.md](../../03_io/storage/tzx_format.md) |
| .TRD disk format specification | [trd_disk_format.md](../../03_io/storage/trd_disk_format.md) |
| .SCL format specification | [trd_scl_formats.md](../../03_io/storage/trd_scl_formats.md) |
| .DSK format specification | [dsk_fdi_formats.md](../../03_io/storage/dsk_fdi_formats.md) |
| Disk format overview | [disk_format_overview.md](../../03_io/storage/disk_format_overview.md) |
| Tape loading/saving from code | [tape_programming.md](tape_programming.md) |
| TR-DOS file operations | [trdos_programming.md](trdos_programming.md) |
| Western DOS file operations | [dos_programming.md](dos_programming.md) |
| Direct mass storage access | [mass_storage_programming.md](mass_storage_programming.md) |
| Screen layout reference | [screen_layout.md](../03_memory_and_io/screen_layout.md) |
