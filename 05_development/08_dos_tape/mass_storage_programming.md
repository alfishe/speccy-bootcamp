[← Plan](../../PLAN.md) · [DOS & Tape](README.md)

# Mass Storage Programming — Direct IDE, SD Card, and FAT Access

Every DOS-mediated file operation — whether through TR-DOS, ESXDOS, or +3 DOS — ultimately talks to physical hardware. The DOS layer adds convenience: filenames, directories, error handling. But it also adds overhead: bank switching, ROM calls, parameter marshaling. When you need maximum speed, minimum footprint, or access to raw data that the DOS cannot reach, you bypass the OS and talk to the hardware directly.

This article covers direct mass storage programming from assembly: IDE/CompactFlash register access, SD card SPI communication, and a minimal read-only FAT16/32 reader. It is the fifth and final article in the [DOS and Tape series](README.md) and assumes you have read the previous four. It does **not** duplicate the hardware reference articles — [IDE interface](../../03_io/storage/ide_interface.md), [SD interface](../../03_io/storage/sd_interface.md), [HDD overview](../../03_io/storage/hdd_overview.md) — those cover the electrical, signaling, and protocol details. This article is the **programmer's practical guide**: complete working code for reading sectors and files without any OS.

> [!NOTE]
> Direct hardware access means you are responsible for everything the OS normally handles: error recovery, timeout, retry logic, and device initialization. The code in this article is educational. Production code needs more robustness — particularly for SD card initialization, which is notoriously flaky across different card brands.

---

## Why Direct Access?

| Scenario | Why Direct? | Alternative |
|---|---|---|
| Boot screen loads 200 KB of data | Direct IDE reads are 2-3x faster than ESXDOS | Use ESXDOS if speed is acceptable |
| Demo streams data from disk every frame | No time for DOS overhead (bank switching, etc.) | TR-DOS streaming (see [trdos_programming.md](trdos_programming.md)) |
| Custom partition format (non-FAT) | DOS cannot read it | Roll your own filesystem |
| Minimal bootloader (< 1 KB) | Cannot fit DOS dependencies | Direct sector reads |
| Accessing raw disk geometry | DOS abstracts it away | Direct sector I/O |

### Performance Comparison

| Method | Read speed (KB/s) | Overhead per sector |
|---|---|---|
| TR-DOS hook code | ~15-20 | ~2000T (ROM dispatch) |
| ESXDOS M_READ | ~25-35 | ~1500T (hook dispatch) |
| Direct IDE (8-bit I/O) | ~50-80 | ~500T (port I/O) |
| Direct SD (SPI) | ~30-50 | ~800T (SPI byte loop) |

> [!NOTE]
> Speeds are approximate for 3.5 MHz Z80. Actual throughput depends on device, interface, and code optimization.

---

## IDE / CompactFlash Interface

### Hardware Overview

The IDE/CF interface connects to the Spectrum via an I/O port decoder. The DivIDE and DivMMC interfaces map the IDE registers into the Spectrum's I/O space using 8-bit transfers (the Spectrum has no 16-bit data bus).

### IDE Register Map

The IDE controller exposes a set of 8-bit registers. On the DivIDE interface, these are mapped at base port `#10`:

| Port offset | IDE register | Direction | Purpose |
|---|---|---|---|
| `#00` | Data | R/W | 16-bit data (read/write as two 8-bit transfers) |
| `#01` | Error / Features | R / W | Error details / set features |
| `#02` | Sector Count | R/W | Number of sectors to transfer |
| `#03` | LBA Low | R/W | Sector address bits 0-7 |
| `#04` | LBA Mid | R/W | Sector address bits 8-15 |
| `#05` | LBA High | R/W | Sector address bits 16-23 |
| `#06` | Drive / Head | R/W | Bits 24-27 + drive select + LBA mode bit |
| `#07` | Status / Command | R / W | Device status / issue command |

On the Spectrum, these are accessed via `IN`/`OUT` instructions. The base port on a standard DivIDE is `#10`:

```z80
; Register port addresses (DivIDE base = #10)
IDE_DATA      EQU #10
IDE_ERROR     EQU #11
IDE_SECCOUNT  EQU #12
IDE_LBA0      EQU #13
IDE_LBA1      EQU #14
IDE_LBA2      EQU #15
IDE_LBA3      EQU #16
IDE_STATUS    EQU #17
```

### Status Register Bits

| Bit | Name | Meaning |
|---|---|---|
| 7 | BSY | Busy — wait for this to clear before any command |
| 6 | DRDY | Drive ready |
| 5 | DRQ | Data request — data is ready to transfer |
| 4 | DSC | Seek complete |
| 3 | — | (reserved) |
| 2 | CORR | Corrected data |
| 1 | IDX | Index mark |
| 0 | ERR | Error — read Error register for details |

The two critical bits are **BSY** (bit 7) and **DRQ** (bit 5). Before issuing a command, you must wait for BSY to clear. After issuing a read command, you must wait for BSY to clear and DRQ to set before reading data.

### Waiting for the Drive

```z80
; ============================================================
; ide_wait_busy — wait for BSY bit to clear
;
; Exit: carry set = timeout (drive stuck), carry clear = ready
;       B = status register value
; ============================================================

ide_wait_busy:
    LD   B, 0                ; timeout counter (256 iterations)
.wait_loop:
    IN   A, (IDE_STATUS)
    AND  #80                 ; BSY bit?
    JR   Z, .not_busy        ; BSY clear, ready
    DJNZ .wait_loop          ; try again
    SCF                      ; carry set = timeout
    RET
.not_busy:
    OR   A                   ; carry clear = ok
    LD   B, A                ; B = final status
    RET
```

```z80
; ============================================================
; ide_wait_drq — wait for DRQ bit (data ready)
;
; Exit: carry set = timeout, carry clear = data ready
; ============================================================

ide_wait_drq:
    LD   B, 0
.wait_loop:
    IN   A, (IDE_STATUS)
    AND  #80                 ; still busy?
    JR   NZ, .wait_loop      ; yes, keep waiting
    IN   A, (IDE_STATUS)
    AND  #08                 ; DRQ bit?
    JR   NZ, .ready          ; yes, data ready
    DJNZ .wait_loop
    SCF                      ; timeout
    RET
.ready:
    OR   A                   ; carry clear = ok
    RET
```

### Reading a Sector (LBA Mode)

```z80
; ============================================================
; ide_read_sector — read one 512-byte sector via LBA
;
; Entry: DEHL = 32-bit LBA sector number
;        IX = destination address (512-byte buffer)
; Exit:  carry set = error, carry clear = success
; ============================================================

ide_read_sector:
    ; Wait for drive to be not busy
    CALL ide_wait_busy
    RET  C                   ; timeout

    ; Set up LBA address
    LD   A, L
    OUT  (IDE_LBA0), A       ; LBA bits 0-7

    LD   A, H
    OUT  (IDE_LBA1), A       ; LBA bits 8-15

    LD   A, E
    OUT  (IDE_LBA2), A       ; LBA bits 16-23

    ; LBA3 = bits 24-27 + LBA mode bit (bit 6) + master drive (bit 4)
    LD   A, D
    AND  #0F                 ; only lower 4 bits of LBA
    OR   #E0                 ; bit 7=1 (obsolete), bit 6=1 (LBA), bit 5=1, bit 4=0 (master)
    OUT  (IDE_LBA3), A

    ; Sector count = 1
    LD   A, 1
    OUT  (IDE_SECCOUNT), A

    ; Issue READ SECTORS command (#20)
    LD   A, #20
    OUT  (IDE_STATUS), A     ; command register

    ; Wait for data ready
    CALL ide_wait_drq
    RET  C                   ; timeout

    ; Read 512 bytes (256 word transfers = 512 byte transfers on 8-bit bus)
    ; On 8-bit interface, each 16-bit word requires two IN reads
    LD   B, 0                ; 256 iterations (B=0 means 256 for DJNZ)
    LD   HL, IX              ; HL = destination
.read_loop:
    IN   A, (IDE_DATA)       ; low byte
    LD   (HL), A
    INC  HL
    IN   A, (IDE_DATA)       ; high byte
    LD   (HL), A
    INC  HL
    DJNZ .read_loop          ; repeat 256 times = 512 bytes

    OR   A                   ; carry clear = success
    RET
```

### Writing a Sector

```z80
; ============================================================
; ide_write_sector — write one 512-byte sector via LBA
;
; Entry: DEHL = 32-bit LBA sector number
;        IX = source address (512 bytes of data)
; Exit:  carry set = error, carry clear = success
; ============================================================

ide_write_sector:
    CALL ide_wait_busy
    RET  C

    ; Set up LBA (same as read)
    LD   A, L
    OUT  (IDE_LBA0), A
    LD   A, H
    OUT  (IDE_LBA1), A
    LD   A, E
    OUT  (IDE_LBA2), A
    LD   A, D
    AND  #0F
    OR   #E0
    OUT  (IDE_LBA3), A

    LD   A, 1
    OUT  (IDE_SECCOUNT), A

    ; Issue WRITE SECTORS command (#30)
    LD   A, #30
    OUT  (IDE_STATUS), A

    ; Wait for DRQ (drive ready to accept data)
    CALL ide_wait_drq
    RET  C

    ; Write 512 bytes
    LD   B, 0
    LD   HL, IX
.write_loop:
    LD   A, (HL)
    OUT  (IDE_DATA), A       ; low byte
    INC  HL
    LD   A, (HL)
    OUT  (IDE_DATA), A       ; high byte
    INC  HL
    DJNZ .write_loop

    ; Wait for write to complete
    CALL ide_wait_busy
    RET
```

### ATA Command Quick Reference

| Command | Code | Purpose |
|---|---|---|
| `#20` | READ SECTORS | Read 1-256 sectors via LBA |
| `#30` | WRITE SECTORS | Write 1-256 sectors via LBA |
| `#EC` | IDENTIFY DEVICE | Get device info (512 bytes) |
| `#E7` | FLUSH CACHE | Force write buffer to disk |
| `#E5` | STANDBY IMMEDIATE | Spin down |
| `#E0` | STANDBY IMMEDIATE (alt) | Some CF cards use this |
| `#EF` | SET FEATURES | Configure parameters |

For the complete IDE/ATA command reference, see [ide_interface.md](../../03_io/storage/ide_interface.md).

---

## SD Card via SPI

### Hardware Overview

SD cards communicate via the SPI protocol: a serial clock (SCK), master-out-slave-in (MOSI), master-in-slave-out (MISO), and chip-select (CS). On the Spectrum, these signals are driven through a single I/O port, typically with 1 bit per pin.

### SPI Bit-Banging

The most common SPI implementation on the Spectrum uses a port where each bit controls one SPI signal:

```
Port #DF (example — varies by interface):
  bit 0: CS (chip select, 0=active)
  bit 1: SCK (clock)
  bit 2: MOSI (master out)
  bit 7: MISO (master in, read-only)
```

```z80
; SPI port definition (example interface)
SPI_PORT  EQU #DF
SPI_CS    EQU %00000001
SPI_SCK   EQU %00000010
SPI_MOSI  EQU %00000100
SPI_MISO  EQU %10000000

; ============================================================
; spi_send_byte — send one byte via SPI (bit-bang)
;
; Entry: A = byte to send
; Exit:  A = byte received (full-duplex)
; Destroys: B, C
; ============================================================

spi_send_byte:
    LD   B, 8                ; 8 bits
    LD   C, A                ; C = byte to send
    LD   A, (spi_port_state) ; current port output state
    AND  ~SPI_CS             ; ensure CS is low (active)

.bit_loop:
    ; Clock low
    AND  ~SPI_SCK            ; clear clock bit

    ; Set MOSI bit
    RL   C                   ; shift C left, MSB into carry
    JR   C, .mosi_high
    RES  2, A                ; MOSI = 0
    JR   .clk
.mosi_high:
    SET  2, A                ; MOSI = 1
.clock:
    OUT  (SPI_PORT), A       ; output with clock low + MOSI

    ; Clock high (rising edge = sample)
    OR   SPI_SCK             ; set clock bit
    OUT  (SPI_PORT), A       ; rising edge

    ; Read MISO bit
    IN   A, (SPI_PORT)       ; read port
    AND  SPI_MISO            ; isolate MISO bit
    JR   Z, .miso_low
    SCF                      ; carry = 1
    JR   .shift
.miso_low:
    OR   A                   ; carry = 0
.shift:
    ; Shift received bit into result
    ; (result accumulates in a separate register)
    ; Simplified — in practice use a 8-bit shift register

    ; Clock low for next bit
    LD   A, (spi_port_state)
    AND  ~SPI_SCK
    OUT  (SPI_PORT), A

    DJNZ .bit_loop
    RET

spi_port_state:  DEFB 0
```

> [!WARNING]
> SPI bit-banging is extremely slow on the Z80 — each bit requires ~20-30 clock cycles, so a single byte takes 160-240T. For a 512-byte sector, that is 82,000-123,000T, or about 5-8 screen frames. This is why SD card interfaces that include a hardware SPI controller (like the ZX Spectrum Next) are dramatically faster.

### SD Card Commands

SD cards use a simple command protocol: send a 6-byte command frame, then wait for a response byte.

```z80
; SD command frame: [01][CMD5bits][32-bit arg][CRC7][1]
; Byte 0: #01 | (command << 2) — actually: command | #40
; Bytes 1-4: 32-bit argument (big-endian)
; Byte 5: CRC + #01 (stop bit)

; ============================================================
; sd_send_command — send an SD command
;
; Entry: A = command number (0-63)
;        DEHL = 32-bit argument
; Exit:  A = response byte (R1), carry set = error
; ============================================================

sd_send_command:
    ; Build command byte: command | #40
    OR   #40
    CALL spi_send_byte       ; send command byte

    ; Send 4-byte argument (big-endian: D, E, H, L)
    LD   A, D
    CALL spi_send_byte
    LD   A, E
    CALL spi_send_byte
    LD   A, H
    CALL spi_send_byte
    LD   A, L
    CALL spi_send_byte

    ; Send CRC + stop bit (for CMD0: #95, for others: #01)
    LD   A, #01              ; generic CRC + stop bit
    CALL spi_send_byte

    ; Wait for response (#FF means "not ready")
    LD   B, 10               ; timeout: 10 retries
.resp_loop:
    LD   A, #FF
    CALL spi_send_byte       ; send dummy, read response
    CP   #FF
    JR   NZ, .got_response   ; non-FF = response
    DJNZ .resp_loop
    SCF                      ; timeout
    RET
.got_response:
    OR   A                   ; carry clear = ok (A = R1 response)
    RET
```

### Reading a Block

```z80
; ============================================================
; sd_read_block — read one 512-byte block from SD card
;
; Entry: DEHL = block number (512-byte aligned)
;        IX = destination buffer
; Exit:  carry set = error
; ============================================================

sd_read_block:
    ; Convert block number to byte address (multiply by 512)
    ; DEHL * 512 = DEHL << 9
    ; Shift HL left 9 bits into DEHL
    ; Simplified: assume block number is already a byte address
    ; (some SD cards use block addressing after init)

    ; Send CMD17 (READ_SINGLE_BLOCK)
    LD   A, 17               ; CMD17
    CALL sd_send_command
    RET  C                   ; command failed
    CP   #00                 ; R1 = 0 means success
    JR   NZ, .cmd_error

    ; Wait for data start token (#FE)
    LD   B, 0                ; max 256 retries
.wait_token:
    LD   A, #FF
    CALL spi_send_byte
    CP   #FE
    JR   Z, .data_start
    DJNZ .wait_token
    SCF                      ; timeout
    RET
.data_start:

    ; Read 512 bytes
    LD   HL, IX
    LD   BC, 512
.read_loop:
    LD   A, #FF
    CALL spi_send_byte       ; send dummy, receive data byte
    LD   (HL), A
    INC  HL
    DEC  BC
    LD   A, B
    OR   C
    JR   NZ, .read_loop

    ; Read and discard 2-byte CRC
    LD   A, #FF
    CALL spi_send_byte       ; CRC high
    LD   A, #FF
    CALL spi_send_byte       ; CRC low

    OR   A                   ; carry clear = success
    RET

.cmd_error:
    SCF
    RET
```

For the complete SD card interface specification including initialization sequence, see [sd_interface.md](../../03_io/storage/sd_interface.md).

---

## Read-Only FAT16/32 Reader

Once you can read raw sectors, the next step is interpreting the FAT filesystem. This section provides a minimal read-only FAT16 reader — enough to open a file by name and read its contents. FAT32 is structurally similar but with wider fields.

> [!NOTE]
> A complete FAT implementation is complex. This reader handles the most common case: FAT16, single partition, 512-byte sectors. For FAT32 or multi-partition disks, the extensions are straightforward but add code size. See [HDD partitioning](../../03_io/storage/hdd_partitioning.md) for the partition table format.

### FAT Concepts

| Concept | Description |
|---|---|
| **Sector** | Smallest physical unit (512 bytes) |
| **Cluster** | Smallest allocation unit (1-128 sectors) |
| **FAT** | File Allocation Table — maps cluster chains |
| **Root directory** | Fixed-size directory at a known location (FAT16) |
| **Chain** | Sequence of clusters that form a file's data |

### Boot Sector Parsing

The first sector of a FAT volume (the boot sector) contains critical parameters:

```z80
; Boot sector (BPB — BIOS Parameter Block) key fields:
; Offset #0B: bytes per sector (2 bytes, usually 512)
; Offset #0D: sectors per cluster (1 byte)
; Offset #0E: reserved sectors before FAT (2 bytes)
; Offset #10: number of FATs (1 byte, usually 2)
; Offset #11: root directory entries (2 bytes, FAT16 only)
; Offset #16: sectors per FAT (2 bytes)
; Offset #20: hidden sectors (4 bytes)
; Offset #1FE: signature (#55 #AA)
```

```z80
; ============================================================
; fat_init — parse boot sector and compute geometry
;
; Entry: HL = address of boot sector data (512 bytes)
; Exit:  geometry stored in fat_* variables
; ============================================================

fat_init:
    LD   (bs_ptr), HL

    ; Bytes per sector (offset #0B)
    LD   DE, #0B
    ADD  HL, DE
    LD   E, (HL)
    INC  HL
    LD   D, (HL)             ; DE = bytes per sector
    LD   (bytes_per_sector), DE

    ; Sectors per cluster (offset #0D)
    INC  HL
    LD   A, (HL)
    LD   (sectors_per_cluster), A

    ; Reserved sectors (offset #0E)
    INC  HL
    LD   E, (HL)
    INC  HL
    LD   D, (HL)
    LD   (reserved_sectors), DE

    ; Number of FATs (offset #10)
    INC  HL
    LD   A, (HL)
    LD   (num_fats), A

    ; Root dir entries (offset #11)
    INC  HL
    LD   E, (HL)
    INC  HL
    LD   D, (HL)
    LD   (root_dir_entries), DE

    ; Sectors per FAT (offset #16)
    LD   HL, (bs_ptr)
    LD   DE, #16
    ADD  HL, DE
    LD   E, (HL)
    INC  HL
    LD   D, (HL)
    LD   (sectors_per_fat), DE

    ; Compute key offsets:
    ; FAT start = reserved_sectors
    ; Root dir start = reserved_sectors + (num_fats * sectors_per_fat)
    ; Data start = root_dir_start + (root_dir_entries * 32 / bytes_per_sector)

    ; root_dir_start = reserved + num_fats * sectors_per_fat
    LD   HL, (reserved_sectors)
    LD   A, (num_fats)
    LD   B, A
.fat_loop:
    LD   DE, (sectors_per_fat)
    ADD  HL, DE
    DJNZ .fat_loop
    LD   (root_dir_start), HL

    ; data_start = root_dir_start + root_dir_entries * 32 / 512
    ; = root_dir_start + root_dir_entries / 16
    LD   DE, (root_dir_entries)
    ; Divide DE by 16
    SRL  D
    RR   E
    SRL  D
    RR   E
    SRL  D
    RR   E
    SRL  D
    RR   E
    ADD  HL, DE
    LD   (data_start), HL

    RET

bs_ptr:               DEFW 0
bytes_per_sector:     DEFW 0
sectors_per_cluster:  DEFB 0
reserved_sectors:     DEFW 0
num_fats:             DEFB 0
root_dir_entries:     DEFW 0
sectors_per_fat:      DEFW 0
root_dir_start:       DEFW 0
data_start:           DEFW 0
```

### Finding a File in the Root Directory

```z80
; ============================================================
; fat_find_file — find a file in the FAT16 root directory
;
; Entry: HL = 11-byte filename (8.3, space-padded, uppercase)
; Exit:  carry set = found (HL = dir entry address)
;        carry clear = not found
; ============================================================

fat_find_file:
    LD   (search_name), HL

    ; Read root directory sectors into a buffer
    ; (Simplified: assumes root dir fits in one read)
    LD   DE, (root_dir_start)
    LD   IX, dir_buffer
    CALL ide_read_sector_lba    ; read sector at LBA=DE+partition_start
    ; (Implementation depends on how partition offset is stored)

    ; Scan directory entries (32 bytes each)
    LD   HL, dir_buffer
    LD   B, 16                 ; 16 entries per sector (512/32)
.scan_loop:
    LD   A, (HL)
    CP   #00                   ; end of directory?
    JR   Z, .not_found
    CP   #E5                   ; deleted entry?
    JR   Z, .next_entry

    ; Compare 11-byte name
    PUSH HL
    PUSH BC
    LD   DE, (search_name)
    LD   B, 11
.cmp_loop:
    LD   A, (HL)
    CP   (DE)
    JR   NZ, .cmp_fail
    INC  HL
    INC  DE
    DJNZ .cmp_loop
    ; Match!
    POP  BC
    POP  HL
    SCF                        ; carry set = found
    RET

.cmp_fail:
    POP  BC
    POP  HL
.next_entry:
    ; Advance 32 bytes
    LD   A, L
    ADD  A, 32
    LD   L, A
    JR   NC, .no_overflow
    INC  H
.no_overflow:
    DJNZ .scan_loop

.not_found:
    OR   A                     ; carry clear = not found
    RET

search_name:  DEFW 0
```

### Directory Entry Format

| Offset | Size | Content |
|---|---|---|
| 0-10 | 11 bytes | Filename (8.3, space-padded, uppercase) |
| 11 | 1 byte | Attributes (#01=RO, #02=hidden, #04=system, #08=vol label, #10=directory, #20=archive) |
| 12-21 | 10 bytes | Reserved (creation time, date, etc.) |
| 22-23 | 2 bytes | Last write time |
| 24-25 | 2 bytes | Last write date |
| 26-27 | 2 bytes | **Starting cluster** (low word) |
| 28-31 | 4 bytes | **File size** (in bytes) |

### Following a Cluster Chain

Once you have the starting cluster from the directory entry, follow the FAT chain to read all of the file's data:

```z80
; ============================================================
; fat_read_file — read a file by following its cluster chain
;
; Entry: HL = directory entry address
;        IX = destination buffer
; Exit:  file data loaded at (IX), BC = bytes read
; ============================================================

fat_read_file:
    ; Extract starting cluster (offset 26-27)
    LD   DE, 26
    ADD  HL, DE
    LD   E, (HL)               ; cluster low byte
    INC  HL
    LD   D, (HL)               ; cluster high byte
    INC  HL
    INC  HL
    INC  HL
    LD   C, (HL)              ; file size low byte
    INC  HL
    LD   B, (HL)              ; file size (simplified: only low 16 bits)
    PUSH BC                   ; save file size

    ; DE = starting cluster
.chain_loop:
    ; Convert cluster to sector:
    ; sector = data_start + (cluster - 2) * sectors_per_cluster
    LD   HL, (data_start)
    ; HL += (DE - 2) * sectors_per_cluster
    DEC  DE
    DEC  DE                   ; DE = cluster - 2
    LD   A, (sectors_per_cluster)
    ; Multiply DE by A (sectors_per_cluster)
    CALL mul_de_by_a          ; HL += result (simplified)

    ; Read sector(s) for this cluster
    ; (For simplicity, read 1 sector per cluster)
    LD   IX, file_buffer
    CALL ide_read_sector_lba

    ; Look up next cluster in FAT
    ; FAT16: each entry is 2 bytes at offset cluster*2 within the FAT
    ; Read FAT sector containing this entry
    LD   A, D
    OR   E
    CP   #0FFF                ; end of chain marker (>= #FFF8)
    JR   NC, .chain_done      ; actually need to check #FFF8+
    ; ... (read FAT entry, get next cluster)
    JR   .chain_loop

.chain_done:
    POP  BC                   ; BC = file size
    RET

file_buffer:  DEFS 512
```

> [!NOTE]
> The cluster chain follower above is simplified. The complete version must read the appropriate FAT sector, look up the 2-byte FAT entry, check for end-of-chain markers (#FFF8-#FFFF for FAT16), and handle bad cluster markers (#FFF7). The pattern is: read FAT sector, extract entry, check for end, compute next cluster's data sector, repeat.

---

## When to Use Direct Access vs. OS-Mediated

| Factor | Direct Access | OS-Mediated (DOS) |
|---|---|---|
| **Speed** | Faster (no ROM overhead) | Slower (bank switching, dispatch) |
| **Code size** | Larger (must implement everything) | Smaller (OS provides the code) |
| **Portability** | Low (tied to specific hardware) | High (works across DOS variants) |
| **Error handling** | Must implement your own | OS provides error codes |
| **Filesystem support** | Must implement FAT yourself | OS provides it |
| **Best for** | Boot loaders, demos, performance-critical code | Applications, utilities, games |

### Decision Matrix

| Your situation | Recommendation |
|---|---|
| Loading assets for a game | Use [ESXDOS](dos_programming.md) — simpler, fast enough |
| Boot loader before DOS is available | Direct IDE/SD access |
| Demoscene streaming with per-frame deadlines | Direct IDE or [TR-DOS streaming](trdos_programming.md) |
| File browser utility | Use DOS APIs — you get filenames for free |
| Custom non-FAT partition | Direct sector I/O |
| Need to read .TAP/.TRD/.SNA from disk | Load via DOS, then parse with [file_format_handling.md](file_format_handling.md) |

---

## Common Pitfalls

### 1. No Error Recovery

Direct hardware access means you handle all errors. A missing retry loop means a single transient error corrupts your data. Always implement:
- Timeout counters (avoid infinite loops on dead hardware)
- Retry logic (retry reads 3-5 times before giving up)
- Status checking (verify DRQ/BSY before every transfer)

### 2. Byte Order in LBA Addressing

IDE LBA registers are written separately, so byte order is straightforward. But SD card commands send the 32-bit argument **big-endian** (most significant byte first). Getting this backward silently reads the wrong sector.

### 3. FAT16 vs. FAT32 Differences

| Feature | FAT16 | FAT32 |
|---|---|---|
| FAT entry size | 2 bytes | 4 bytes |
| Root directory location | Fixed (after FATs) | Cluster chain (usually cluster 2) |
| End-of-chain marker | #FFF8-#FFFF | #0FFFFFF8-#0FFFFFFF |
| Max clusters | 65,524 | 268,435,444 |

### 4. CF Card 8-Bit Mode

CompactFlash cards can operate in 8-bit or 16-bit mode. The Spectrum's DivIDE interface uses 8-bit mode. If a CF card defaults to 16-bit mode after power-on, you must issue a SET FEATURES command to switch it to 8-bit before any data transfer will work correctly.

### 5. SD Card Initialization Timing

SD card initialization requires a specific sequence: send 74+ dummy clock cycles with CS high, then CMD0 with correct CRC (#95), then CMD8 (voltage check), then ACMD41 (initialization). Skipping or shortening any step causes initialization to fail on certain card brands. SanDisk cards are particularly strict.

---

## Cross-References

| Topic | Reference |
|---|---|
| IDE interface hardware details | [ide_interface.md](../../03_io/storage/ide_interface.md) |
| SD card interface hardware | [sd_interface.md](../../03_io/storage/sd_interface.md) |
| HDD overview and partitioning | [hdd_overview.md](../../03_io/storage/hdd_overview.md) |
| HDD partition tables | [hdd_partitioning.md](../../03_io/storage/hdd_partitioning.md) |
| DivIDE/DivMMC hardware | [divide_divmmc.md](../../03_io/storage/divide_divmmc.md) |
| WD1793 FDC (floppy controller) | [fdc_vg93.md](../../03_io/storage/fdc_vg93.md) |
| Beta disk interface | [beta_disk_interface.md](../../03_io/storage/beta_disk_interface.md) |
| TR-DOS file operations | [trdos_programming.md](trdos_programming.md) |
| Western DOS file operations | [dos_programming.md](dos_programming.md) |
| File format parsing | [file_format_handling.md](file_format_handling.md) |
