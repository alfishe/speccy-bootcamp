[← Home](../../README.md) · [I/O](../) · [Storage](README.md)

# The WD1793 / KR1818VG93 Floppy Disk Controller

Every Spectrum floppy system — the [Beta Disk Interface](beta_disk_interface.md), the original TR-DOS cartridge, the +3's internal controller (a close cousin), and dozens of Soviet-era clones — is built around a single chip: the **Western Digital WD179x series** of floppy disk controllers. In the Soviet Sphere, this chip was cloned as the **KR1818VG93** (КР1818ВГ93), functionally identical and pin-compatible with the WD1793.

The WD1793 is the chip that takes commands like "read sector 5 of track 12 on side 0" from the host computer and produces the [MFM signal](mfm_encoding.md) on the disk drive cable. It contains a phase-locked loop (PLL) for clock recovery, an MFM encoder/decoder, a CRC generator, a sector-search state machine, and a register file for command/status/data exchange with the host. Understanding the WD1793 is the prerequisite for understanding every Spectrum floppy interface, every disk format, and every disk-based protection scheme.

This article covers the WD1793 in depth: its pinout, its five internal registers, its full command set (Type I/II/III/IV), its status register bits, timing characteristics, undocumented quirks, the KR1818VG93 clone's differences, and the various "turbo" modifications used to speed up Spectrum floppy systems.

---

## §1. What the WD1793 Is

### 1.1 History

The WD179x series was introduced by **Western Digital Corporation** in 1977 as the successor to the earlier FD1771 (the first single-chip floppy controller). The WD179x brought several improvements:

- **MFM support** in addition to FM (the FD1771 was FM-only).
- **Double-density recording** at up to 500 kbit/s (the FD1771 was limited to single-density FM).
- **Simplified host interface** with a smaller register file.
- **Built-in write precompensation** and PLL data separator (the FD1771 required external circuitry).

The WD179x series consists of several variants. The key differences are in **data-bus polarity** (true vs inverted) and **density support** (FM+MFM vs FM-only). All members with the same density support share the same data separator (internal monolithic PLL on the -3/-4/-5/-7, identical to the -1/-2 except for the bus polarity):

| Part | Data bus | Density | Used in |
|------|----------|---------|---------|
| **WD1791** | Inverted (`/DAL`) | FM + MFM | Rare; requires external data separator on some boards. |
| **WD1792** | Inverted (`/DAL`) | FM only (single density) | Rare; FD1771-compatible. |
| **WD1793** | **True (non-inverted DAL)** | FM + MFM | **The standard for Spectrum floppy systems.** |
| **WD1794** | True | FM only (single density) | Not used on Spectrum. |
| **WD1795 / WD1797** | True | FM + MFM, with side-select output | Not used on Spectrum; differs in pinout to expose SSO. |

Per the WD1793 datasheet (reproduced on MSX Info Pages): "The 1793 is identical to the 1791 except the Data Access Lines are TRUE (for systems that utilize true data buses). The 1792 and 1794 are 'single density only' versions of the 1791 and 1793 respectively. The 1795/7 has a side select output for controlling double sided drives."

The WD1793 is the variant used in the Spectrum ecosystem because it has an internal PLL (no external data separator required) and supports both FM and MFM. The Beta Disk Interface, the original TR-DOS cartridge, the Kay interface, the Scorpion interface, the Pentagon's onboard FDC, and many Soviet clones all use the WD1793 (or its KR1818VG93 clone).

A closely related chip, the **WD1772**, is used in the Amstrad +2A/+3 internal floppy controller. The WD1772 is functionally similar to the WD1793 but integrates additional logic for the +3's specific bus interface. It is described briefly in §10.

### 1.2 The role of the FDC in the floppy stack

The FDC sits between the host computer (the Spectrum) and the floppy drive. To the host, the FDC presents a simple register interface: write a command, wait for completion, read or write data through a single data register. To the drive, the FDC presents the standard Shugart floppy interface: step/direction signals for the head stepper motor, write data / write gate for writing, raw read data for reading, and various status inputs (track 0, index, write protect).

```
            Host interface                Drive interface
+----------+               +-------------+               +-------+
| Spectrum | <-- data -->  | WD1793 FDC  | <-- signals-->| Floppy|
|  Z80     | <-- status--> |             |               | drive |
+----------+               +-------------+               +-------+
                            ^             ^
                            |             |
                            v             v
                        5 host        10 drive
                        registers     signals
```

The FDC is responsible for:

- **Encoding/decoding MFM**: turning bytes from the host into MFM flux transitions on write, and turning flux transitions back into bytes on read.
- **Clock recovery (PLL)**: locking onto the embedded clock signal in the MFM stream.
- **Sync mark detection**: finding the `A1*` sync bytes to establish byte synchronisation.
- **Sector searching**: comparing the ID field of each sector to the desired track/side/sector.
- **CRC generation/checking**: computing the CRC-16 of fields and flagging errors.
- **Head positioning**: issuing step/direction pulses to the drive's stepper motor to move the head to the desired track.

All this complexity is hidden behind five host-visible registers and a small command set.

### 1.3 Why the WD1793 matters for Spectrum developers

The WD1793 matters because:

- **It is universal**. Every Spectrum floppy system uses the WD1793 (or a close relative). Understanding this chip is the key to understanding every floppy-related Spectrum program.
- **It defines the programming model**. The TR-DOS ROM, the +3 DOS ROM, the Beta Disk Interface BIOS, all Soviet disk loaders, and all disk-based demos and games use the WD1793's register interface. There is no abstraction layer between your code and the FDC.
- **It is essential for emulator authors**. A WD1793 emulator must reproduce all the chip's behaviour, including its quirks and undocumented features. Many Spectrum disk programs depend on specific FDC timing or specific quirks, and an inaccurate FDC emulator will fail to run them.
- **It is the basis of copy protection**. Most Spectrum disk protection schemes rely on exploiting specific WD1793 behaviour (such as the "side-select trick" or the "read track" command's raw data capture).

### 1.4 What the WD1793 is *not*

The WD1793 is **not** a complete floppy interface. It is just the controller chip. The complete interface requires additional logic for:

- **Address decoding**: mapping the WD1793's registers into the Spectrum's I/O space.
- **Drive selection**: choosing which of up to four drives is active.
- **Side selection**: choosing which side of a double-sided disk is active (the WD1793 has a side-select output, but the actual head switching is done by the drive).
- **DMA / interrupt handling**: passing data between the FDC's data register and the Spectrum's RAM. (The WD1793 has DRQ and IRQ outputs for this; the Spectrum typically polls DRQ rather than using DMA.)
- **Bus buffering**: the WD1793's bus drivers are not strong enough to drive the Spectrum's full bus; buffer chips (74LS244, 74LS245) are required.

These functions are provided by the surrounding interface circuitry, which differs between the Beta Disk Interface, the +3 controller, and other implementations.

---

## §2. Pinout and Hardware Interface

The WD1793 is a 40-pin DIP (Dual Inline Package) chip. This section covers its pinout and how it connects to the host and drive.

### 2.1 Pinout

```
                  +-----+--+-----+
        RESET --->|1  +-+--+   40|<--- VCC (+5V)
          RTN --->|2           39|<--- /WE
          /MR --->|3           38|<--- /RE
         /ENP --->|4   WD1793  37|<--- A0
         /IW --->|5            36|<--- A1
          /CS --->|6           35|<--- /DAL7
          INTRQ ->|7           34|<-> DAL6
       /CLK488 -->|8           33|<-> DAL5
          DIR --->|9           32|<-> DAL4
          STEP -->|10          31|<-> DAL3
        /WDATA -->|11          30|<-> DAL2
         /WGATE -->|12         29|<-> DAL1
       /TRK00 <---|13          28|<-> DAL0
         /IP <----|14          27|---> /MR
         WPRT <---|15          26|---> /ENP
         /DD <----|16          25|---> RCLK
         /DS0 --->|17          24|---> VFOC
         /DS1 --->|18          23|---> TG43
         HLD --->|19           22|---> READY
         HLT <---|20           21|---> GND
                 +---------------+
```

(Schematic representation. Pin assignments may vary slightly between manufacturers; the above is the canonical WD1793 layout.)

### 2.2 Host interface signals

The WD1793 connects to the host via these signals:

| Pin(s) | Signal | Direction | Purpose |
|--------|--------|-----------|---------|
| 26–33 | DAL0–DAL7 | bidirectional | 8-bit data/address bus. Used to read/write registers. |
| 35, 36 | A0, A1 | input | Register select. Together with /RE and /WE, selects which register is accessed. |
| 36 (note) | /CS | input | Chip select. The FDC responds only when /CS is asserted. |
| 38 | /WE | input | Write enable. When asserted with /CS, the FDC latches data from DAL into the selected register. |
| 37 | /RE | input | Read enable. When asserted with /CS, the FDC drives the selected register onto DAL. |
| 7 | INTRQ | output | Interrupt request. Asserted when a command completes (or when a forced interrupt is triggered). |
| 1 | /RESET | input | Reset. When asserted, the FDC enters the idle state and clears its internal logic. |
| 3 | /MR | input | Master reset (alternate function on some variants). |

### 2.3 Drive interface signals

The WD1793 connects to the floppy drive via these signals:

| Pin | Signal | Direction | Purpose |
|-----|--------|-----------|---------|
| 9 | DIR | output | Direction for the next STEP pulse. 0 = inward (towards higher tracks), 1 = outward (towards track 0). |
| 10 | STEP | output | Step pulse. One pulse moves the head one track in the direction set by DIR. |
| 13 | /TRK00 | input | Track 0 sensor. Asserted by the drive when the head is at track 0. |
| 14 | /IP | input | Index pulse. Asserted by the drive once per revolution (when the index hole passes the sensor). |
| 15 | WPRT | input | Write protect. Asserted by the drive when the disk is write-protected. |
| 16 | /DD | input | Double density select. 0 = MFM (double density), 1 = FM (single density). |
| 24 | RCLK | output | Raw read clock. The PLL's recovered clock signal. (Sometimes used as an output to external PLL circuitry.) |
| 11 | /WDATA | output | Write data. The MFM-encoded bit stream to be written. |
| 12 | /WGATE | output | Write gate. Asserted when the FDC is actively writing. |
| 22 | READY | input | Drive ready. Asserted by the drive when a disk is inserted and the motor is up to speed. |
| 23 | TG43 | output | Track greater than 43. Asserted when the head is on a track > 43, indicating that write current reduction should be applied. |
| 25 | VFOC | output | VFO control. A signal for external PLL circuitry (not used in the WD1793's internal PLL). |
| 17, 18 | /DS0, /DS1 | output | Drive select. Indicates which of up to 4 drives is selected (in combination with /DS0 and /DS1). |
| 19 | HLD | output | Head load. Asserted to engage the read/write head against the disk. |
| 20 | HLT | input | Head load timing. Asserted by the drive when the head is fully loaded. |

### 2.4 The Shugart bus

The drive interface follows the **Shugart Associates Systems Interface (SASI)**, which later evolved into the SCSI standard for hard disks. For floppy disks, the relevant subset is the **Shugart floppy bus**, which uses a 34-pin ribbon cable (for PC-style drives) or a 26-pin ribbon cable (for older Shugart-style drives).

The WD1793's drive signals are buffered through open-collector drivers on the interface card and connected to the drive through this cable. The interface card also includes pull-up resistors and termination networks to ensure signal integrity.

### 2.5 The clock input

The WD1793 requires an external **clock** signal, typically at **8 MHz** (for 4" and 5.25" drives) or **16 MHz** (for 3.5" drives at 500 kbit/s). The internal logic divides this clock down to produce the various timing signals used by the FDC (the 250 kHz data rate, the 500 kHz PLL frequency, the step rate, etc.).

Some WD1793 variants (and most KR1818VG93 clones) have a built-in clock oscillator, but the original WD1793 requires an external clock.

---

## §3. The Register File

The WD1793 exposes **five 8-bit registers** to the host. All host interaction with the FDC — issuing commands, checking status, transferring data, positioning the head — goes through these five registers. There is no other interface.

### 3.1 The five registers

| # | Register | Read (/RE + /CS) | Write (/WE + /CS) | Purpose |
|---|----------|------------------|-------------------|---------|
| 0 | **Status** | Current command status (7 bits, see §6) | (write goes to Command register) | Read: poll command progress. Write: issue a command. |
| 1 | **Command** | (read returns Status register) | Command byte (top 3 bits = type, see §4) | Write-only in practice; reads decode to Status. |
| 2 | **Track** | Current track number (0–255) | Set the track register | Tracks the head's *logical* position. Updated by Type I commands. |
| 3 | **Sector** | Target sector number (1–255) | Set the sector register | Holds the sector number for the next Type II/III command. |
| 4 | **Data** | Read a byte from the FDC (sector data, ID field, etc.) | Write a byte to the FDC (sector data, format fields) | The data path for all read/write transfers. |

The Status and Command registers share register-select address `A0=0, A1=0`: a read returns Status, a write goes to Command. The other three registers (Track, Sector, Data) are bidirectional — read and write access the same underlying storage.

### 3.2 The register-select matrix

The host selects which register to access using **A0, A1, /RE, /WE** (with /CS asserted). The four combinations of A0/A1 select the register group; /RE vs /WE then determines read vs write within that group.

| /CS=0 | A1 | A0 | /RE=0 | /WE=0 |
|-------|----|----|-------|-------|
| | 0  | 0  | Read **Status** | Write **Command** |
| | 0  | 1  | Read **Track** | Write **Track** |
| | 1  | 0  | Read **Sector** | Write **Sector** |
| | 1  | 1  | Read **Data** | Write **Data** |

This means the WD1793 occupies **four I/O port addresses** in the host's I/O space (one for each A0/A1 combination). The exact port addresses differ between interfaces: the Beta Disk Interface uses `#1F`–`#3F`, the +3 internal controller uses `#1F`–`#3F` (with different paging), and so on. The interface hardware decodes the host's I/O address bus down to A0 and A1 plus /CS.

### 3.3 Read and write timing

A register read or write is a single I/O cycle:

- **Read**: The host asserts /CS, A0, A1, and /RE. After a short access time (typically 350 ns on the WD1793), the FDC drives the selected register's contents onto DAL0–DAL7. The host reads the byte and deasserts /CS and /RE.
- **Write**: The host asserts /CS, A0, A1, drives the byte onto DAL0–DAL7, and asserts /WE. The FDC latches the byte into the selected register on the rising edge of /WE (or /CS — the exact edge differs between WD1793 variants).

These are standard Z80 I/O cycles. From the Z80's perspective, accessing the FDC is the same as accessing any other I/O device: an `IN A,(#1F)` reads the Status register; an `OUT (#1F),A` writes the Command register.

### 3.4 The Status register (overview)

The Status register is the primary way the host monitors the FDC. The meaning of each bit is **context-dependent** — it depends on which command type (I, II, III, or idle) is currently executing. The overview below uses the Type I assignment; the full per-type table is in §6.

| Bit | Type I name | Type II/III name | Source (hardware signal) |
|-----|-------------|------------------|--------------------------|
| 7 | NOT READY | NOT READY | Inverted `/READY` input, ORed with `/MR` (reset state) |
| 6 | WRITE PROTECT | WRITE PROTECT (writes only) | Inverted `/WPRT` input |
| 5 | HEAD LOADED | RECORD TYPE (read) / WRITE FAULT (write) | Type I: AND of HLD and HLT. Type II read: data address mark (`#FB`=0, `#F8`=1). Type II/III write: write-fault input. |
| 4 | SEEK ERROR | RECORD NOT FOUND (RNF) | Type I: target track not verified. Type II/III: target sector ID not found. |
| 3 | CRC ERROR | CRC ERROR | CRC mismatch in ID field (Type I verify, READ ADDRESS) or data field (READ SECTOR) |
| 2 | TRACK 00 | LOST DATA | Type I: inverted `/TRK00` input. Type II/III: host failed to service DRQ within one byte window. |
| 1 | INDEX | DRQ | Type I: inverted `/IP` input (pulses once per revolution). Type II/III: copy of internal DRQ signal. |
| 0 | BUSY | BUSY | Command in progress (1) or complete (0) |

Bit 0 (**BUSY**) is the most important: the host polls this bit to know when a command has finished. Most programming patterns look like:

```
loop:
    IN A,(#1F)      ; read Status register
    AND 1           ; isolate BUSY
    JR NZ, loop     ; wait until command completes
```

The Status register's bit meanings depend on which command is currently executing — bit 6 means "write protect" during Type I commands but "lost data" during Type II commands. The full per-command bit table is in §6.

### 3.5 The Command register

The Command register is **write-only**: the host writes a command byte to it, and the FDC begins executing that command. The command byte has a fixed structure:

- **Bits 7–5**: command **type** (0 = Type I positioning, 1 = Type II read/write sector, 2 = Type III format/raw, 3 = Type IV force interrupt).
- **Bits 4–0**: command-specific **flags** (step rate, head load, density, multi-sector, etc.).

Writing a new command to the Command register while another command is executing forces the old command to terminate (the FDC does not queue commands). The full command set is documented in §4.

### 3.6 The Track and Sector registers

The **Track register** holds the *logical* track number that the FDC thinks the head is currently on. It is updated automatically by Type I commands (RESTORE sets it to 0, SEEK sets it to the data register's value, STEP increments/decrements it). The host can also write it directly — this is sometimes done to "fool" the FDC about its position, for example when implementing copy protection schemes that read a sector from a different track than the FDC believes.

The **Sector register** holds the *desired* sector number for the next Type II or Type III command. Before issuing a READ SECTOR or WRITE SECTOR command, the host must set the Sector register to the target sector (1, 2, 3, ... up to the number of sectors per track). The FDC then searches the track for a sector whose ID field matches this value (combined with the Track register's value for the track number and a separate side-select input for the head).

The Track and Sector registers are *not* automatically reset on command completion. They persist between commands, which lets the host issue a sequence of operations on the same track/sector without rewriting them each time.

### 3.7 The Data register

The **Data register** is the host's window into the FDC's data path. It is used for three distinct purposes, depending on the command:

1. **Track number for SEEK**: Before issuing a SEEK command, the host writes the desired track number into the Data register. The FDC compares this with the Track register and steps the head the appropriate number of tracks.
2. **Sector bytes for READ SECTOR / WRITE SECTOR**: During the execution phase of a Type II command, the FDC transfers one byte per sector-data byte through the Data register. On READ SECTOR, each `IN A,(#3F)` returns the next byte; on WRITE SECTOR, each `OUT (#3F),A` provides the next byte.
3. **Format fields for WRITE TRACK**: During a WRITE TRACK command (used to format a track), the host streams a sequence of bytes through the Data register that defines the track's physical layout — gaps, sync marks, ID fields, data fields. See §4.4.

Each byte transferred through the Data register is synchronised to the FDC's internal processing. The host must read or write the next byte within a fixed time window (typically 27 µs at 250 kbit/s for MFM, less for higher data rates); otherwise a **lost data** error is flagged in the Status register. The host knows when the next byte is ready by polling the **DRQ** (Data Request) status bit or by sampling the DRQ pin (which some interfaces expose via a separate status port).

---

## §4. The Command Set

The WD1793 has **11 commands**, divided into four types by their function. The top three bits of the command byte select the type; the remaining five bits select the specific command and its options.

| Type | Commands | Purpose |
|------|----------|---------|
| **I** | RESTORE, SEEK, STEP, STEP-IN, STEP-OUT | Move the head (positioning). No data transfer. |
| **II** | READ SECTOR, WRITE SECTOR | Transfer one or more sectors between disk and host. |
| **III** | READ ADDRESS, READ TRACK, WRITE TRACK | Read/write the raw track layout (formatting, low-level access). |
| **IV** | FORCE INTERRUPT | Terminate the current command immediately. |

The host issues a command by writing the command byte to the Command register (port `A0=0, A1=0`, /WE). The FDC begins executing on the rising edge of /WE. Most commands set the BUSY bit (Status bit 0) for the duration of execution and assert INTRQ when they complete.

This section covers each command in detail. Sub-sections 4.1–4.4 cover Types I–IV respectively.

### 4.1 Type I commands — head positioning

Type I commands move the read/write head to a specific track. They are the only commands that produce STEP and DIR output signals to the drive's stepper motor. Type I commands do not transfer data; they only update the Track register and physically move the head.

#### Command byte format

All Type I commands share this byte layout:

```
Bit:    7  6  5  4  3  2  1  0
        ---type---  T  h  V  r1 r0
        =000       |  |  |  |-- step rate (see table below)
                    |  |  |-- V: verify (1 = read first ID field and check track number against Track register)
                    |  |-- h: head load (1 = assert HLD after stepping)
                    |-- T: update Track register (STEP / STEP-IN / STEP-OUT only; ignored on RESTORE/SEEK)
```

The five Type I commands are distinguished by bits 7–4 (with bit 4 being the update flag for the three STEP variants):

| Command   | Bit pattern `7 6 5 4` |
|-----------|------------------------|
| RESTORE   | `0 0 0 0` |
| SEEK      | `0 0 0 1` |
| STEP      | `0 0 1 T` (T = update Track register) |
| STEP-IN   | `0 1 0 T` |
| STEP-OUT  | `0 1 1 T` |

The **step rate** field (bits 1–0) selects how fast the stepper motor pulses are issued. The rates below are for the standard 8 MHz / 2 MHz WD1793 clock; see §8.4 for how they scale with non-standard clocks:

| Bits 1–0 | Step rate | Typical use |
|----------|-----------|-------------|
| 00 | 6 ms | Old 5.25" drives (Miniberk, early Beta Disk) |
| 01 | 12 ms | Standard 5.25" and 3.5" drives |
| 10 | 20 ms | Conservative, for worn drives |
| 11 | 30 ms | Very conservative; rarely used |

Most Spectrum software uses 6 ms (00) or 12 ms (01). The 6 ms rate is safe for almost all 3.5" drives; the 12 ms rate is safer for older 5.25" mechanisms. The FDC cannot step faster than the drive's mechanism allows — too-fast stepping causes the head to "overshoot" or fail to settle, leading to read errors on the next sector access.

#### RESTORE (command byte `#0x` = `0000xxxx`)

**RESTORE** (`#00`, `#08`, `#10`, `#18`, etc.) moves the head to **track 0**. It is typically the first command issued after a reset.

Mechanism:
1. The FDC sets DIR = outward (towards track 0).
2. It pulses STEP until /TRK00 is asserted by the drive.
3. The Track register is set to 0.

If /TRK00 is already asserted (head is already at track 0), the command completes immediately. If /TRK00 never asserts (e.g., the drive is not connected or the sensor is broken), the FDC steps up to 255 times before giving up — at that point the Track register is undefined and the BUSY bit clears with an error.

RESTORE is essential after power-up because the FDC has no way to know where the head is. Most TR-DOS and +3 DOS routines begin with a RESTORE on the first access after reset.

#### SEEK (command byte `#1x` = `0001xxxx`)

**SEEK** (`#10`, `#18`, etc.) moves the head to an arbitrary track specified by the **Data register**. Before issuing SEEK, the host writes the desired track number to the Data register (port `A0=1, A1=1`):

```
LD   A, desired_track
OUT  (#3F), A          ; write Data register
LD   A, #1F            ; SEEK command (with flags)
OUT  (#1F), A          ; issue SEEK
```

The FDC compares the Data register with the Track register:
- If Data > Track: DIR = inward, step (Data − Track) times.
- If Data < Track: DIR = outward, step (Track − Data) times.
- If equal: do nothing.

After SEEK, the Track register equals the Data register (assuming the drive stepped correctly). The host does **not** verify the head's physical position by default — the FDC trusts the step count. To verify, set the **verify bit** (bit 2) in the command byte; the FDC then reads the first sector's ID field after stepping and checks that its track number matches the Track register.

#### STEP, STEP-IN, STEP-OUT

These three commands step the head **one track** in a specific direction:

| Command | Byte (with flags) | Direction | Updates Track register? |
|---------|-------------------|-----------|-------------------------|
| STEP    | `#2x` (0010xxxx)  | Same as last STEP | If bit 4 (T) = 1 |
| STEP-IN  | `#4x` (0100xxxx)  | Inward (higher tracks) | If bit 4 (T) = 1 |
| STEP-OUT | `#6x` (0110xxxx)  | Outward (lower tracks) | If bit 4 (T) = 1 |

The **update bit** (bit 4, T) controls whether the Track register is updated. With `T=1`, the Track register is incremented (STEP-IN) or decremented (STEP-OUT) by 1. With `T=0`, the Track register is unchanged — useful when deliberately desynchronising the FDC's notion of position from the physical head position (a common trick in copy protection).

STEP (without -IN or -OUT) repeats the direction of the previous STEP command. This is rarely used in practice; most code uses STEP-IN and STEP-OUT explicitly.

These single-step commands are typically used only in low-level drivers (e.g., the +3 ROM's seek routine). Application code calls higher-level routines like `seek_to_track` that issue SEEK directly.

#### Head load and head load timing

Type I commands have two flags related to the head load solenoid:

- **h** (bit 3): Head load. If 1, the FDC asserts HLD to engage the read/write head against the disk after stepping.
- **V** (bit 2): Verify. If 1, the FDC reads the first sector's ID field after stepping and checks that its track number matches the Track register. Sets SEEK ERROR (Status bit 4) on mismatch or ID-field CRC error.
- The **head settle delay** (15 ms after HLD) is implicit — the FDC always waits 15 ms after asserting HLD before completing the command. There is no separate command-bit control for this on the WD1793. The HLT input is sampled after the 15 ms delay and gates the HEAD LOADED status bit (Status bit 5).

The HLT input is driven by the drive (typically via a 555 timer or a Hall-effect sensor) and indicates that the head has physically settled against the disk after the solenoid engages. The HEAD LOADED status bit is the logical AND of HLD and HLT — so if HLT is never asserted (as on most Spectrum interfaces that do not wire HLT to the controller), HEAD LOADED reads 0 even after HLD is asserted.

Most Spectrum software uses `h=1, V=0` (load head, do not verify) because verification requires a readable sector ID and adds a revolution of latency. RESTORE with `V=1` is typically used only during drive-detection or alignment checks.

---

### 4.2 Type II commands — sector read/write

Type II commands transfer data between a sector on the disk and the host. There are two: **READ SECTOR** and **WRITE SECTOR**. Both share the same command byte layout and use the Track, Sector, and Data registers.

#### Command byte format

```
Bit:    7  6  5  4  3  2  1  0
        --type--  m  S  E  C  a  0
        =10        |  |  |  |  |  0 (reserved)
                   |  |  |  |-- a0: Data Address Mark (WRITE SECTOR only; 0 = `#FB`, 1 = `#F8` deleted DAM)
                   |  |  |-- C: Side Compare Enable (0 = disable side compare, 1 = enable)
                   |  |-- E: 15 ms head-settling delay when stepping is needed (0 = no delay, 1 = wait 15 ms)
                   |-- S: Side Compare Value (0 = compare for side 0, 1 = compare for side 1)
                   |-- m: Multiple Record (0 = single sector, 1 = multi-sector)
```

The flags most relevant to driver authors:

- **m** (bit 4): **Multi-record**. If 1, the FDC reads/writes multiple consecutive sectors in a single command. After each sector, the Sector register is incremented and the FDC continues to the next sector. If 0, only the sector in the Sector register is transferred.
- **C** (bit 2): **Side compare enable**. If 0, the FDC does not compare the side byte in the sector ID field at all — any side value matches. If 1, the FDC compares the sector ID's side byte against the **S** bit (bit 3) and only matches sectors where they are equal.
- **S** (bit 3): **Side compare value**. When C=1, sectors with side byte = S are matched. S also drives the SSO (Side Select Output) pin directly during Type II/III commands; this is independent of the C bit's compare behaviour.
- **a0** (bit 1, WRITE SECTOR only): Selects the Data Address Mark. 0 = `#FB` (normal), 1 = `#F8` (deleted). READ SECTOR reads either mark and reports it via RECORD TYPE (Status bit 5).

The **E** bit (bit 2 of Type III commands, or bit 2 with different meaning on Type II commands that include head load) adds a 15 ms head-settling delay when stepping is needed. This is rarely needed in practice because Type I commands typically load the head first.

Note: many Spectrum interfaces (including the Beta Disk Interface) route side selection through a separate system control port (`#FF` bit 4) that drives the drive's `/SIDE1` input directly, bypassing the FDC's SSO pin. On these interfaces the FDC's S/C bits are still relevant for ID-field matching but do not affect which physical head is active.

#### READ SECTOR (command byte `#8x` = `1000xxxx`)

**READ SECTOR** reads the contents of a single sector (or multiple sectors, with `m=1`) from the disk into the host's memory via the Data register.

Before issuing READ SECTOR:
1. SEEK to the desired track (Type I command).
2. Write the sector number to the Sector register.
3. Write the READ SECTOR command byte to the Command register.

The FDC then:
1. Waits for the index pulse (start of track).
2. Searches the track for a sector whose ID field matches: Track = Track register, Sector = Sector register, side = s bit.
3. When the sector is found, reads the data field, checking the CRC.
4. For each byte of the data field, asserts DRQ (Data Request) and presents the byte in the Data register.
5. The host reads each byte by executing `IN A,(#3F)` (or equivalent) before the next DRQ.
6. When the sector is complete, sets the Status register and asserts INTRQ.

If the sector is not found (e.g., wrong track number, or sector doesn't exist), the FDC sets RECORD NOT FOUND (bit 4) and CRC ERROR (bit 3) in the Status register after one full revolution.

If the host fails to read the Data register within the byte window (~27 µs at 250 kbit/s MFM), the FDC sets LOST DATA (bit 6) in the Status register and the byte is lost. Reading continues with the next byte, but the data is corrupted.

The DRQ bit appears in the Status register at bit 1 **during Type II execution** (it appears at bit 7 only on some variants). Most polling loops look like:

```
wait_drq:
    IN  A,(#1F)          ; read Status
    AND #02              ; isolate DRQ
    JR  Z, wait_drq      ; wait for DRQ
    IN  A,(#3F)          ; read data byte
    LD  (HL), A          ; store in memory
    INC HL
    ; ...repeat for sector length...
```

#### WRITE SECTOR (command byte `#Ax` = `1010xxxx`)

**WRITE SECTOR** writes the contents of the host's memory to a sector on the disk.

Before issuing WRITE SECTOR:
1. SEEK to the desired track.
2. Write the sector number to the Sector register.
3. Write the WRITE SECTOR command byte to the Command register.

The FDC then:
1. Waits for the index pulse.
2. Searches the track for the target sector.
3. When the sector is found, asserts DRQ and waits for the host to provide the first byte.
4. The host writes each byte via `OUT (#3F), A`. The FDC latches it and asserts DRQ for the next.
5. The FDC writes the data field, computing the CRC as it goes.
6. After the data field, writes the CRC bytes and the gap, then asserts INTRQ.

If the disk is write-protected, the FDC terminates immediately with WRITE PROTECT (bit 6) in the Status register. No data is written.

If the host fails to provide a byte within the window, LOST DATA is set and the FDC writes `#00` in place of the missing byte (corrupting the data field but maintaining sector structure).

WRITE SECTOR also supports the **deleted data address mark** via the **a0** bit (bit 1) of the command byte. If `a0=1`, the FDC writes a DDAM (`#F8`) instead of a DAM (`#FB`) before the data. This is used to mark sectors as "deleted" or "special" — some copy protection schemes use this to flag hidden or intentionally damaged sectors. READ SECTOR reads either mark transparently; the type is reported in Status bit 5 (RECORD TYPE: 1 = deleted DAM, 0 = normal DAM).

#### Multi-sector operations

With `m=1`, READ SECTOR and WRITE SECTOR operate on multiple sectors in one command. The FDC starts at the Sector register's value and continues until either:

- The Sector register reaches `#FF` (the maximum), or
- A READ SECTOR encounters RECORD NOT FOUND (e.g., the track has fewer sectors than requested), or
- The host issues FORCE INTERRUPT.

Multi-sector reads are useful for loading entire tracks in one command (e.g., loading a 5120-byte TR-DOS track as 10 × 512-byte sectors). The host still has to handle DRQ for every byte — there is no DMA on the basic WD1793 setup.

Most TR-DOS and +3 DOS routines use single-sector operations in a loop, because this gives finer control over error recovery (a bad sector can be skipped without aborting the whole multi-sector read).

---

### 4.3 Type III commands — raw track access

Type III commands bypass the sector-level abstraction and operate on the **raw track layout**. They are used for two purposes: **formatting** a track (writing the gaps, sync marks, ID fields, and empty data fields that define the sector structure) and **low-level inspection** (reading the raw ID fields or the raw bit stream for copy protection analysis).

There are three Type III commands: READ ADDRESS, READ TRACK, and WRITE TRACK. They share the same command byte prefix (top 3 bits = `110`).

#### READ ADDRESS (command byte `#Cx` = `1100xxxx`)

**READ ADDRESS** reads the **ID field** of the *next* sector that passes under the head. It does not search for a specific sector — it just waits for the next sync mark, reads the following ID field, and returns it.

The ID field consists of 6 bytes:

| Byte | Meaning |
|------|---------|
| 0 | Track number (from the disk's ID field) |
| 1 | Side number (0 or 1) |
| 2 | Sector number |
| 3 | Sector length code (see table below) |
| 4 | CRC byte 1 |
| 5 | CRC byte 2 |

The **sector length code** (byte 3 of the ID field) selects the data-field length for that sector. The code is the upper 2 bits of a 1-byte field; the lower 6 bits are reserved:

| Code (bits 7–6 of byte 3) | Sector length | Used in |
|----------------------------|---------------|---------|
| `00` | 128 bytes | Rare on Spectrum; some CP/M formats |
| `01` | 256 bytes | **Standard for TR-DOS / Beta Disk** |
| `10` | 512 bytes | Standard for +3 DOS, Opus Discovery, IBM-PC |
| `11` | 1024 bytes | Rare; some CP/M and server-grade formats |

The encoding follows the formula `length = 128 << code`, so the same field can describe any of the four sizes. The unreal-ng FDC implementation confirms this: `_sectorSize = 128 << (idAddressMark->sector_size & 0x03)`.

The 6 ID-field bytes are returned through the Data register (one DRQ per byte). The host reads them by polling DRQ and reading the Data register six times. The Sector register is also updated with byte 2 (the sector number) — this is a side effect that can confuse drivers that don't expect it.

If no ID field is encountered within a disk revolution (i.e., the track is unformatted), READ ADDRESS does **not** set RNF — instead it keeps spinning. Per the unreal-ng implementation the search times out after 5 revolutions (about 1 second at 300 RPM) and the command completes with whatever partial data was collected.

READ ADDRESS is useful for:
- Enumerating the sectors on a track (call it repeatedly while the disk rotates, collecting every sector ID).
- Detecting non-standard sector sizes or sector orderings (e.g., copy protection).
- Verifying that a track was formatted correctly.

#### READ TRACK (command byte `#Ex` = `1110xxxx`)

**READ TRACK** reads the **entire raw contents of one track revolution** — every byte from index pulse to index pulse, including gaps, sync marks, address marks, ID fields, data fields, and CRCs. This is the lowest-level read the FDC supports.

The host reads the bytes through the Data register, just like READ SECTOR, but instead of a single sector it receives the entire track (~6250 bytes for a standard MFM track). The FDC synchronises to the index pulse and starts reading at that point.

READ TRACK has important caveats:
- **Sync marks are not preserved**. The `A1*` patterns with missing clock bits cannot be represented in the byte stream — the FDC substitutes normal `#A1` bytes. So the raw track image is not bit-exact.
- **Per the WD1793 datasheet**: "The ID Address Mark, ID field, ID CRC bytes, DAM, Data and Data CRC bytes for each sector will be correct. The gap bytes may be read incorrectly during write-splice time because of synchronization." In other words, the structural bytes (address marks, ID fields, data fields, CRCs) are reliably reproduced; only the gap fill bytes (the long runs of `#4E`) may differ between reads.
- **Bit slip may occur** if the PLL loses lock during gap regions (long runs of `#4E` bytes). The FDC's PLL is designed to recover from this, but READ TRACK can produce slightly different byte counts between reads.
- **The total byte count is approximately 6250** for a standard MFM track at 250 kbit/s / 300 RPM, but the actual count varies by ±50 bytes depending on motor speed (±2%) and exact index-hole position.

READ TRACK is used almost exclusively for copy protection analysis — to inspect the raw track layout and detect non-standard patterns. It is rarely used in normal software.

#### WRITE TRACK (command byte `#Fx` = `1111xxxx`)

**WRITE TRACK** formats an entire track. The host streams a sequence of bytes through the Data register that defines the track's physical layout. This is how a blank disk is formatted with sectors.

The format stream uses a special control-byte encoding:

| Byte | Meaning |
|------|---------|
| `#FE` | ID Address Mark — start of an ID field |
| `#FB` | Data Address Mark — start of a normal data field |
| `#F8` | Deleted Data Address Mark — start of a deleted data field |
| `#F5` | Write `A1*` (sync mark with missing clock) — MFM only |
| `#F6` | Write `C2*` (alternate sync mark with missing clock) — rarely used |
| `#FC` | Index Address Mark |
| `#F7` | Generate 2 CRC bytes (the FDC computes and writes the CRC) |
| `#4E` | Gap fill byte (most common) |
| `#00` | Sync byte (used in the pre-sync run-in) |
| Any other byte | Written literally as MFM data |

To format a track with N sectors, the host writes a stream that looks roughly like:

```
<80 bytes of #4E>            ; GAP1 (post-index)
for each sector 1..N:
    <12 bytes of #00>        ; sync run-in
    <3 bytes of #F5>         ; three A1* sync marks
    <#FE>                    ; IDAM
    <track, side, sector, size_code>  ; 4 ID bytes
    <#F7>                    ; generate CRC (2 bytes)
    <22 bytes of #4E>        ; GAP2 (post-ID)
    <12 bytes of #00>        ; sync run-in
    <3 bytes of #F5>         ; three A1* sync marks
    <#FB>                    ; DAM
    <sector_length bytes of #E5>  ; data (typically initialised to #E5)
    <#F7>                    ; generate CRC (2 bytes)
    <80 bytes of #4E>        ; GAP3 (post-data)
<remaining bytes of #4E>     ; GAP4 (pre-index fill)
```

The host streams this entire sequence through the Data register in lockstep with the FDC's writing. Missing a byte within the window corrupts the track structure (gaps shift, sync marks appear at wrong positions) — usually requiring the track to be re-formatted.

Most TR-DOS and +3 DOS "FORMAT" commands are wrappers around WRITE TRACK that build the format stream in a RAM buffer, then stream it to the FDC during a single revolution.

WRITE TRACK requires the disk to be **not write-protected**. If it is, the FDC terminates immediately with WRITE PROTECT in the Status register.

### 4.4 Type IV command — FORCE INTERRUPT

**FORCE INTERRUPT** (command byte `#Dx` = `1101xxxx`) is the only Type IV command. It can be written at any time — even when another command is BUSY (it is the only command with this property). If a command is executing, it is terminated immediately and the BUSY bit is cleared. If no command is executing, FORCE INTERRUPT simply updates the Status register to reflect Type I semantics and asserts INTRQ (subject to the condition bits).

The low 4 bits select when INTRQ is asserted:

| Bits 3–0 | Mnemonic | Condition |
|----------|----------|----------|
| `0000`   | —        | No interrupt is generated (command terminates silently, BUSY clears, no INTRQ). |
| `0001`   | i0       | On the next **not-ready → ready** transition of the `/READY` input (disk inserted / drive spun up). |
| `0010`   | i1       | On the next **ready → not-ready** transition of the `/READY` input (disk removed / drive stopped). |
| `0100`   | i2       | On the next **index pulse** (`/IP` assertion). |
| `1000`   | i3       | **Immediate** interrupt. INTRQ asserts right away. Per the WD datasheet, this condition "requires a reset" — the FDC will not accept further commands until the Status register is read or the Command register is written again. |

Multiple condition bits can be set simultaneously (e.g. `#0F` = any of the four conditions). If no condition bit is set (`#D0`), the command just terminates the current operation without generating an INTRQ.

Typical uses:
- **Aborting a stuck READ SECTOR**. If a read is taking too long (e.g., the disk is not spinning or the sector is corrupt), `#D0` lets the host regain control immediately.
- **Implementing a timeout**. The host issues a READ SECTOR, sets a timer, and if the timer expires before INTRQ, it issues `#D0` to abort.
- **Waiting for the index pulse without a command**. `#D4` (i2 set) arms an interrupt that fires on the next index pulse; useful for measuring revolution time or synchronising to the disk.
- **Waiting for disk insertion**. `#D1` (i0 set) arms an interrupt that fires when `/READY` goes high — useful for change-detection in DOS shells.

Writing a Type I/II/III command implicitly aborts the current command (the FDC does not queue commands), but FORCE INTERRUPT is the **clean** way to abort because it does not start a new command's execution phase.

---

## §5. Command Execution Phases

Every WD1793 command (except FORCE INTERRUPT) goes through up to three phases. Understanding these phases is essential for driver authors, because the host has different responsibilities in each phase.

### 5.1 The three phases

| Phase | Duration | What the FDC does | What the host does |
|-------|----------|-------------------|---------------------|
| **Command** | 1 I/O write cycle (~3 µs) | Latches the command byte, decodes it, starts internal state machine | Writes the command byte to the Command register |
| **Execution** | Variable (ms to seconds) | Performs the actual work (stepping, reading, writing) | Either waits (Type I/III raw) or transfers data (Type II) via the Data register |
| **Result** | 0 cycles (no explicit result phase) | Asserts INTRQ, updates Status register, returns to idle | Polls Status / services INTRQ, reads result bits |

The Command phase is instantaneous from the host's perspective. The Execution phase is where the time is spent. The Result phase is implicit — there is no separate result register to read; the host just reads the Status register after INTRQ.

### 5.2 Phase-by-phase walkthrough: READ SECTOR

A READ SECTOR command goes through these steps:

**Command phase** (host-initiated):
```
LD   A, track_number
OUT  (#3F), A          ; Data register = target track
LD   A, #1F            ; SEEK command
OUT  (#1F), A          ; issue SEEK (Command register)
; ...wait for INTRQ after SEEK completes...
LD   A, sector_number
OUT  (#2F), A          ; Sector register = target sector
LD   A, #80            ; READ SECTOR command (single-sector, side 0)
OUT  (#1F), A          ; issue READ SECTOR (Command register)
```

The act of writing `#80` to the Command register ends the Command phase and starts Execution.

**Execution phase** (FDC-driven):
1. FDC sets BUSY=1.
2. FDC waits for the index pulse.
3. FDC scans sectors: reads ID fields, looking for Track=Track_reg AND Sector=Sector_reg.
4. When the matching sector is found, FDC reads the data field.
5. For each byte of the data field, FDC sets DRQ=1 and presents the byte in the Data register.
6. Host polls DRQ, then reads the byte:
   ```
   wait_drq:
       IN  A,(#1F)      ; Status
       BIT 1, A         ; DRQ?
       JR  Z, wait_drq
       IN  A,(#3F)      ; Data
       LD  (HL), A      ; store
       INC HL
   ```
7. After 512 bytes (for a standard sector), the FDC verifies the CRC.

**Result phase**:
1. FDC clears BUSY=0.
2. FDC asserts INTRQ.
3. Host reads Status register to check for CRC errors, lost data, etc.
4. FDC returns to idle.

### 5.3 Phase-by-phase walkthrough: WRITE SECTOR

WRITE SECTOR is similar, but the data flow direction is reversed, and the host must provide each byte within the window:

**Execution phase** (FDC-driven, host-provided data):
1. FDC finds the target sector's ID field.
2. After the ID field's CRC, FDC writes the gap (GAP2), then the sync run-in.
3. FDC writes the Data Address Mark.
4. FDC asserts DRQ — host must provide byte 0.
5. FDC writes byte 0 to the disk, then asserts DRQ for byte 1.
6. ... continues for 512 bytes.
7. FDC computes CRC and writes 2 CRC bytes.
8. FDC writes GAP3 (post-data gap).

If the host fails to provide a byte within the window (about 27 µs at 250 kbit/s MFM), FDC writes `#00` in its place and sets LOST DATA. This corrupts the sector but maintains track structure — subsequent sectors are still readable.

### 5.4 The idle phase

When no command is executing, the FDC is in the **idle phase**. In idle, the FDC continuously polls the drive interface for the index pulse (to support FORCE INTERRUPT with the i2 / index-pulse condition) and the `/TRK00` sensor.

There is **no internal motor-on timer on the WD1793**. The Status bit 7 (NOT READY) is a direct combinational copy of the inverted `/READY` input (ORed with the `/MR` reset state). Motor control is purely external: the host (or the interface logic) turns the spindle motor on or off via drive-select lines, and the drive asserts `/READY` only when a disk is inserted and spinning at the correct speed. Software that needs to wait for motor spin-up must poll NOT READY until it clears (or wait a fixed ~1 second at 300 RPM after switching the motor on).

### 5.5 Polling during execution: DRQ vs INTRQ

There are two distinct signals the host can poll:

- **DRQ (Data Request)**: Asserted by the FDC when the Data register is ready for the next byte transfer. Set during the execution phase of Type II/III commands. The host must service DRQ within the byte window (32 µs at 250 kbit/s MFM, 64 µs at 125 kbit/s FM — 114 or 228 Z80 T-states at 3.5 MHz) or lose data.
- **INTRQ (Interrupt Request)**: Asserted by the FDC when a command completes (or when a FORCE INTERRUPT condition fires). Stays asserted until the host reads the Status register **or** writes a new command byte to the Command register — whichever happens first. This reset-on-Status-read / reset-on-Command-write semantics is common to all command types.

The WD1793 exposes DRQ on a separate pin from the host bus. Some interfaces (e.g., Beta Disk Interface) make DRQ visible as bit 6 of a separate "system" port (port `#FF`). Other interfaces only expose DRQ through the Status register (bit 1 during Type II/III execution). The exact wiring is interface-specific.

Servicing DRQ fast enough is **the** critical performance problem on the WD1793. At 250 kbit/s MFM, the byte window is only 32 µs. In Z80 cycles at 3.5 MHz, that's about 114 T-states — tight enough that polling loops must be hand-optimised, and any memory contention (on the 48K Spectrum, contended memory accesses during the loading delay the loop) can cause lost data.

### 5.6 INTRQ handling: polling vs interrupts

The simplest INTRQ handling is **polling**: the host sits in a tight loop reading the Status register, waiting for BUSY to clear. This wastes CPU time but is universally compatible.

A more sophisticated approach uses the Z80's **interrupt mechanism**: the interface's INTRQ pin is wired to the Z80's `/INT` pin, and the host's interrupt handler is invoked when INTRQ asserts. This is more efficient (the host can do other work while the FDC runs) but requires the interface hardware to provide a clean interrupt vector and the host software to set up an interrupt table.

Most TR-DOS routines use polling, because:
- The FDC operations are short enough that the polling overhead is acceptable.
- Polling avoids the complexity of interrupt-safe code.
- The original Beta Disk Interface did not wire INTRQ to the Z80's interrupt controller.

The +3 DOS ROM does use interrupts for some operations, taking advantage of the +3's more integrated hardware design.

**Important INTRQ semantics** (per the WD1793 datasheet, verified in the unreal-ng implementation):
- INTRQ is asserted at the end of **every** command's result phase, including commands that terminate due to an error or due to FORCE INTERRUPT.
- INTRQ is reset by either (a) reading the Status register or (b) writing a new command byte to the Command register. Writing a new command without first reading the Status register is legal and clears the pending INTRQ.
- If FORCE INTERRUPT is issued with all four condition bits clear (`#D0`), the command terminates but INTRQ is **not** asserted. With any of i0–i3 set, INTRQ is asserted either immediately (i3) or when the condition fires (i0/i1/i2).

---

## §6. Status Register Bit Reference

The Status register's bit meanings are **context-dependent**: bit 6 means one thing during a Type I command and a different thing during a Type II command. This is a common source of bugs in FDC drivers. This section gives the full per-command bit table.

### 6.1 Status bits during Type I commands

Type I commands (RESTORE, SEEK, STEP, STEP-IN, STEP-OUT) update the Status register as follows:

| Bit | Name | Meaning |
|-----|------|---------|
| 7 | NOT READY | Inverted copy of the `/READY` input, ORed with the reset state (`/MR`). 1 = drive not ready (no disk, or motor not up to speed); 0 = drive ready. Type I commands execute regardless of `/READY`. |
| 6 | WRITE PROTECT | Inverted copy of the `/WPRT` input. 1 = disk in the selected drive is write-protected. |
| 5 | HEAD LOADED | Logical AND of the internally-driven HLD signal and the externally-sampled HLT input. 1 = head solenoid is energised **and** the drive confirms head contact. On Spectrum interfaces that leave HLT disconnected (the common case), this bit reads 0 even when HLD is asserted. |
| 4 | SEEK ERROR | 1 = verify failed: the track number read from the first ID field did not match the Track register, or the ID field had a CRC error. Only meaningful when the V bit was set in the command. Cleared to 0 when the Status register is read. |
| 3 | CRC ERROR | 1 = CRC mismatch in the ID field (only set if verify was requested, V=1). Cleared when the Status register is read. |
| 2 | TRACK 00 | Inverted copy of the `/TRK00` input. 1 = head is currently at track 0. |
| 1 | INDEX | Inverted copy of the `/IP` input. Pulses 1 for the duration of the index pulse (~4 ms at 300 RPM, ~3.3 ms at 360 RPM) once per disk revolution. |
| 0 | BUSY | 1 = command in progress; 0 = command complete. |

Bit 5 (HEAD LOADED) is the most useful for knowing whether the drive's read/write head is actually engaged with the media. Because the original WD1793 datasheet specifies that HEAD LOADED = HLD AND HLT, and most Spectrum interfaces leave HLT floating or tied to a fixed level, drivers cannot rely on this bit alone — they typically infer head-loaded state from whether a Type I command with `h=1` has been issued recently.

Bit 1 (INDEX) is also useful: it pulses once per revolution. Drivers that need to time a full revolution (e.g., to detect a "missing" sector for copy protection, or to measure RPM) poll this bit.

### 6.2 Status bits during Type II commands

Type II commands (READ SECTOR, WRITE SECTOR) use a different bit layout from Type I:

| Bit | Name | Meaning |
|-----|------|---------|
| 7 | NOT READY | Inverted copy of the `/READY` input, ORed with the reset state. 1 = drive not ready. Type II commands do **not** execute when `/READY` is low; the command terminates immediately with INTRQ and no data transfer. |
| 6 | WRITE PROTECT (writes) / 0 (reads) | WRITE SECTOR only: inverted copy of the `/WPRT` input. Always reads 0 on READ SECTOR. Cleared when the Status register is read. |
| 5 | RECORD TYPE (reads) / WRITE FAULT (writes) | READ SECTOR: reflects the data-field address mark — 1 = `#F8` (Deleted Data Address Mark), 0 = `#FB` (normal Data Address Mark). WRITE SECTOR: inverted copy of the write-fault input from the drive; on most Spectrum interfaces this input is hardwired inactive and the bit always reads 0. |
| 4 | RECORD NOT FOUND (RNF) | 1 = no sector on the track had an ID field matching Track register + Sector register + (if C=1) S bit. Also set when the ID field had a CRC error. Cleared when the Status register is read. |
| 3 | CRC ERROR | 1 = CRC mismatch. If RNF (bit 4) is also set, the error was in the ID field; otherwise it was in the data field. Cleared when the Status register is read. |
| 2 | LOST DATA | 1 = the host failed to service DRQ within one byte window (32 µs at 250 kbit/s MFM, 64 µs at 125 kbit/s FM). Cleared when the Status register is read. |
| 1 | DRQ | Copy of the internal DRQ signal. 1 = the Data register contains a byte that needs reading (read) or is ready for the next byte (write). Cleared when the Data register is serviced. |
| 0 | BUSY | 1 = command in progress; 0 = command complete. |

The key bits for error handling are:
- Bit 7 (NOT READY): no disk in the drive, or drive not spun up. The command does not execute at all.
- Bit 4 (RECORD NOT FOUND): the sector wasn't there. Most likely the track number or sector number in the registers is wrong, or the ID-field CRC failed so the FDC could not confirm the match.
- Bit 3 (CRC ERROR): the data on the disk is corrupted. The host should retry, and if the error persists, mark the sector as bad. If RNF is also set, the corruption was in the ID field rather than the data field.
- Bit 6 (WRITE PROTECT on writes): the disk is write-protected; no data was written.
- Bit 2 (LOST DATA): the host failed to keep up with the FDC's data rate. The transfer continued with the lost byte replaced by `#00` on writes, or skipped on reads.

**INTRQ reset behaviour**: INTRQ is asserted at command completion and stays asserted until the host reads the Status register **or** writes a new command byte to the Command register. This is true for all command types.

### 6.3 Status bits during Type III commands

Type III commands (READ ADDRESS, READ TRACK, WRITE TRACK) use yet another layout:

| Bit | Name | Meaning |
|-----|------|---------|
| 7 | NOT READY | Inverted `/READY` input, ORed with reset state. As with Type II, Type III commands do not execute when `/READY` is low. |
| 6 | WRITE PROTECT | WRITE TRACK only: inverted copy of the `/WPRT` input. Always 0 on READ ADDRESS / READ TRACK. |
| 5 | WRITE FAULT (writes) / 0 (reads) | WRITE TRACK only: inverted copy of the write-fault input. Always 0 on reads. |
| 4 | 0 | Always 0 (no RNF condition for Type III — READ ADDRESS reads the next ID field regardless of match, READ TRACK reads the entire revolution, WRITE TRACK writes the entire revolution). |
| 3 | CRC ERROR | READ ADDRESS only: 1 = CRC mismatch in the ID field that was just read. Always 0 on READ TRACK / WRITE TRACK. |
| 2 | LOST DATA | 1 = host failed to service DRQ in time (32 µs MFM / 64 µs FM). |
| 1 | DRQ | Copy of internal DRQ signal. |
| 0 | BUSY | 1 = command in progress. |

For WRITE TRACK, bit 6 (WRITE PROTECT) is checked at the start of the command. If set, the command terminates immediately without writing anything. For READ ADDRESS, the CRC ERROR bit reflects the validity of the most recent ID field read.

### 6.4 Status bits during idle (no command executing)

When no command is executing, the Status register reflects the Type I bit layout (the FDC's reset / idle state uses Type I semantics):

| Bit | Name | Meaning |
|-----|------|---------|
| 7 | NOT READY | Inverted `/READY`, ORed with `/MR` (reset). |
| 6 | WRITE PROTECT | Inverted `/WPRT`. |
| 5 | HEAD LOADED | AND of HLD and HLT. After reset, HLD is deasserted so this reads 0. |
| 4 | SEEK ERROR | Reads 0 (no verify has been run since reset). |
| 3 | CRC ERROR | Reads 0 (no ID-field check has been run since reset). |
| 2 | TRACK 00 | Inverted `/TRK00`. |
| 1 | INDEX | Inverted `/IP` (pulses once per revolution). |
| 0 | BUSY | Always 0 in idle. |

Note that bits 4, 3, 5 (SEEK ERROR, CRC ERROR, HEAD LOADED) are **sticky** in some implementations — once set, they remain until the next Status-register read clears them. The WD1793 datasheet specifies this reset-on-read behaviour for SEEK ERROR and CRC ERROR; HEAD LOADED follows the live HLD AND HLT state. Emulator authors should verify the exact reset behaviour against the specific FDC variant they are modelling.

### 6.5 Common status-reading patterns

Most FDC drivers use one of these patterns:

**Wait for command completion (Type I or III)**:
```
wait_busy:
    IN  A,(#1F)      ; read Status
    BIT 0, A         ; BUSY?
    JR  NZ, wait_busy ; keep waiting
; Status now contains the result bits
```

**Wait for DRQ during Type II read**:
```
wait_drq:
    IN  A,(#1F)
    BIT 1, A         ; DRQ?
    JR  Z, wait_drq
    IN  A,(#3F)      ; read Data
    LD  (HL), A
    INC HL
```

**Combined: wait for DRQ or INTRQ (whichever first)**:
```
wait_drq_or_done:
    IN  A,(#1F)
    BIT 0, A         ; BUSY cleared (command done)?
    JR  Z, done
    BIT 1, A         ; DRQ?
    JR  Z, wait_drq_or_done
    IN  A,(#3F)      ; read Data
    LD  (HL), A
    INC HL
    JR  wait_drq_or_done
done:
; ...check for errors...
```

The third pattern is the most robust — it handles the case where the command completes (e.g., the last byte has been read) before the host polls again.

### 6.6 The DRQ bit timing

The DRQ bit in the Status register is set the moment a byte is ready in the Data register. It stays set until the host reads (or writes) the Data register, at which point DRQ clears. If the next byte becomes ready before DRQ has been serviced, the FDC sets LOST DATA and overwrites the Data register with the new byte.

The byte window at 250 kbit/s MFM is about 32 µs. The host has 32 µs from DRQ being set to read/write the Data register. In Z80 cycles at 3.5 MHz, that's about 112 T-states. The polling loop above (`IN`, `BIT`, `JR Z`) takes about 24 T-states, leaving 88 T-states for the actual `IN A,(#3F)` and `LD (HL),A; INC HL` (about 25 T-states). So roughly 60% of the window is available as polling overhead — usually enough, but tight.

On contended memory (e.g., the 48K Spectrum's lower 16 KB), each memory access is delayed by the ULA, eating into this window. This is why TR-DOS drivers typically run from uncontended RAM (the upper 32 KB on the 48K, or any RAM bank on the 128K).

---

## §7. The KR1818VG93 Soviet Clone

Every Soviet and Russian Spectrum clone with a floppy interface uses the **KR1818VG93** (Russian: **КР1818ВГ93**), a Soviet-produced clone of the WD1793. The clone is pin-compatible with the WD1793-02 (the second revision of the WD1793) and functionally identical for all documented features. The KR1818VG93 was produced at the **Angstrem** plant (Zelenograd, near Moscow) starting in the late 1980s, as part of the Soviet programme to clone Western integrated circuits.

### 7.1 The cloning programme

The Soviet Union's microelectronics industry operated on a "copy first, improve later" principle. When a Western chip became important for Soviet industry (military, industrial, consumer), it was reverse-engineered and produced domestically under a Soviet part number. The KR1818VG93 was part of the **KR1818** series, a family of clones of Western Digital's floppy controller line:

| Soviet part | Western original |
|-------------|------------------|
| KR1818VG91  | WD1691 (FDC support / write precompensation) |
| KR1818VG93  | WD1793-02 (the main FDC) |
| KR1818VG97  | WD1797 (extended FDC with separate input/output shift registers) |

The KR1818VG93 is the part most commonly encountered on Soviet Spectrum clones (Pentagon, Scorpion, Kay, ATM Turbo, Leningrad, etc.), where it serves exactly the same role as the WD1793 in the Western Beta Disk Interface.

### 7.2 Physical differences

The KR1818VG93 is a 40-pin DIP, identical in pinout to the WD1793. There are a few physical differences:

- **Package material**: WD1793 is plastic DIP; KR1818VG93 is typically ceramic DIP (more robust, but more expensive to produce).
- **Marking**: Soviet chips use Cyrillic markings (КР1818ВГ93) and a date code in the format "WW YY" (week and year). The plant logo (Angstrem's stylised "A") is also present.
- **Operating temperature range**: KR1818VG93 is rated for the military-grade temperature range (−40°C to +85°C), reflecting its origins in Soviet military-industrial production. The WD1793 consumer part is rated 0°C to +70°C.

These physical differences do not affect the chip's behaviour in a Spectrum clone. The KR1818VG93 is a drop-in replacement for the WD1793 in any Spectrum floppy interface.

### 7.3 Functional differences

The KR1818VG93 was reverse-engineered from the WD1793-02 die mask, so its behaviour matches the WD1793-02 for all documented features. The differences observed on real hardware are in undocumented behaviour and analog characteristics, not in the documented command set:

- **Step rate accuracy**: The KR1818VG93's step rate generator is less precise than the WD1793's. The 6 ms setting is typically 6.0 ms on the WD1793 but can be 6.2–6.5 ms on the KR1818VG93. This is rarely a problem because most drives tolerate ±10% step rate variation.
- **PLL lock time**: The internal PLL on the KR1818VG93 takes slightly longer to lock to the MFM bit clock than the WD1793's PLL. On marginal disks (with weak signals or off-speed motors), the KR1818VG93 may produce more read errors.
- **NOT READY bit latency**: Status bit 7 (NOT READY) is documented as a combinational copy of the inverted `/READY` input. On some KR1818VG93 lots, the bit's response to a `/READY` transition can be delayed by a few hundred nanoseconds relative to the WD1793-02. This is invisible to polling software but matters for cycle-exact emulator implementation.

None of these differences cause incompatibility with normal software. They become relevant only when emulating the FDC precisely (e.g., for cycle-exact emulator implementation) or when running software that depends on specific undocumented timing.

### 7.4 Why the KR1818VG93 matters for the Spectrum ecosystem

The KR1818VG93 is the standard FDC for the entire Soviet/Russian Spectrum clone ecosystem. Every Pentagon, Scorpion, Kay, ATM Turbo, Profi, and Leningrad with a floppy interface uses one. The Western WD1793 is rare in this ecosystem — most Soviet clones were built entirely from Soviet-made parts, with the KR1818VG93 as the floppy controller.

This means that for emulator authors targeting the Russian Spectrum scene (Unreal Speccy, Spectaculator, ZEsarUX's Pentagon mode, etc.), the FDC model must be the KR1818VG93, not the WD1793. The differences are small but can affect software that pushes the FDC to its limits — particularly copy-protected disk loaders, which often depend on specific FDC timing.

For modern hardware projects (Karabas, Peridot, etc.) that use Soviet-style interfaces, the KR1818VG93 is still the chip of choice when an authentic FDC is desired. New-old-stock KR1818VG93 chips are readily available from Russian electronics suppliers as of 2025.

---

## §8. Undocumented Features and Quirks

The WD1793 has a number of undocumented behaviours that real software (especially copy protection schemes) relies on. These quirks are not in the official datasheet but have been reverse-engineered from chip behaviour and are essential for emulator authors to reproduce.

### 8.1 The "side-select" trick

The WD1793's **s** bit (bit 3 of Type II commands) is documented as selecting the disk side (0 or 1). However, the actual behaviour is more nuanced: the FDC compares the **side byte** in the sector's ID field against the **s** bit, and only matches the sector if they are equal.

This means a disk can be formatted with **sectors that claim to be on side 1 even though they are physically on side 0**. The FDC will only read those sectors when the host issues a READ SECTOR with `s=1`. A normal read with `s=0` will skip them.

Copy protection schemes exploit this by:
1. Formatting a track on side 0 with normal sectors (side byte = 0).
2. Adding extra sectors to the same physical track with side byte = 1.
3. The normal DOS (which reads with `s=0`) sees only the normal sectors.
4. The protection check reads with `s=1` and finds the hidden sectors.

This trick is used by several Spectrum disk protections, including the **Alkatraz** protection system and various Pentagon-era games.

### 8.2 Reading with deliberately wrong track number

If the host sets the Track register to a value that doesn't match the disk's actual track number, the FDC will still try to read sectors — it just won't find any (because the ID field's track byte won't match). But if the disk is formatted with **non-standard track numbers** (e.g., a "track 5" that's physically located at track 0), the FDC will happily read it.

Some protection schemes format a disk with shifted track numbers: what the DOS calls "track 0" is actually at physical track 5, etc. The driver looks up tracks via a translation table; without the table, the disk appears unformatted.

### 8.3 The 125 µs INTRQ-after-Command window

After a command completes, INTRQ asserts and stays asserted until the host reads the Status register (or writes a new command). But there is a brief window — about 125 µs after the command byte is written — during which INTRQ is asserted for the *previous* command. If the host writes a new command in this window, the previous INTRQ is "stuck" and the new command's INTRQ assertion may be missed.

This is rarely a problem in practice (the host usually reads the Status register between commands), but it can confuse interrupt-driven drivers that do not perform this read.

### 8.4 Multiple-step rates from a single bit combination

The official step rates are 6, 12, 20, and 30 ms (for bit combinations 00, 01, 10, 11). However, the actual step rate depends on the FDC's master clock frequency. On interfaces that clock the FDC at a non-standard rate (e.g., 7 MHz instead of 8 MHz), the step rates scale proportionally:

| Clock | Step rate for `00` | Step rate for `01` |
|-------|---------------------|---------------------|
| 8 MHz (standard) | 6 ms | 12 ms |
| 7 MHz | ~6.86 ms | ~13.7 ms |
| 16 MHz | 3 ms | 6 ms |

The 16 MHz case is the basis of the "turbo" floppy modification (see §9): by clocking the FDC faster, both the data rate and the step rate double, halving access time.

### 8.5 The READ TRACK byte count

The byte count returned by READ TRACK is not exactly 6250 (the nominal track length). It varies by:
- **Motor speed**: ±2% motor speed = ±125 bytes per revolution.
- **Index hole position**: the index sensor's physical position determines where the read starts and ends; small variations here add or remove bytes at the start/end of the read.
- **PLL slip**: in long gaps, the PLL may lose and regain sync, occasionally inserting or dropping a byte.

Most software that uses READ TRACK (mainly copy programs and protection analyzers) accounts for this by reading 6500 bytes and discarding the extras, or by aligning the read to a known sync mark.

### 8.6 DRQ during Type III commands

Type III commands also assert DRQ, but the timing differs from Type II. During WRITE TRACK, DRQ is asserted continuously — the host must provide bytes as fast as the FDC writes them, which is one byte per 32 µs at 250 kbit/s MFM. Missing a byte corrupts the track structure.

During READ TRACK, DRQ is similarly continuous, but the FDC will silently skip bytes if the host doesn't read fast enough (no LOST DATA error is flagged for Type III reads on some variants — the FDC just keeps streaming).

### 8.7 The /MR (Master Reset) pin behaviour

The /MR pin (pin 3, also called /MR or "Master Reset" on some variants) is documented as a hardware reset. But the actual behaviour depends on the variant:

- **WD1793 original**: /MR resets the FDC's internal logic but does NOT clear the Track, Sector, or Data registers.
- **WD1793-02**: /MR clears all registers and restores the chip to a known state.
- **KR1818VG93**: /MR behaves like the WD1793-02 (clears all registers).

Software that uses /MR must account for this: on the original WD1793, the Track register retains its value across /MR, so the host must issue a RESTORE after reset. On the -02 and KR1818VG93, the Track register is undefined and must be initialised.

---

## §9. Turbo Mods and Speed Improvements

The standard WD1793 setup on the Spectrum (8 MHz clock, 250 kbit/s MFM, single-density sectors) is reliable but slow. A standard TR-DOS disk holds about 80 KB of data per side and takes about 4 seconds to load fully. As the Spectrum clone scene matured in the 1990s, various "turbo" modifications emerged to push the FDC faster.

### 9.1 The clock-doubling mod

The simplest and most common turbo mod is to **double the FDC's master clock** from 8 MHz to 16 MHz. As described in §8.4, this halves the step rate and doubles the data rate:

| Parameter | 8 MHz clock (standard) | 16 MHz clock (turbo) |
|-----------|------------------------|----------------------|
| Data rate | 250 kbit/s MFM | 500 kbit/s MFM |
| Bit cell | 4 µs | 2 µs |
| Byte window | 32 µs | 16 µs |
| Step rate (00) | 6 ms | 3 ms |
| Bytes per track | ~6250 | ~12500 |

A 16 MHz clock lets the FDC read and write at "high density" (HD) rates — the same rate used by PC 5.25" HD and 3.5" HD floppies. With HD-capable disks and drives, a Spectrum can store ~160 KB per side (twice the standard density).

The mod is purely a hardware change: replace the 8 MHz crystal on the FDC interface with a 16 MHz crystal. No software change is required for the FDC itself, though software that depends on specific timing (e.g., copy protection) will need updates. Most modern TR-DOS versions (e.g., TR-DOS 6.10+ for the Pentagon) detect the clock speed automatically and adjust their timing loops accordingly.

The downside: HD floppies are physically different from DD floppies (different magnetic coating, different coercivity). Writing HD data to a DD floppy produces unreliable results. The mod requires HD disks (marked "2D" or "HD") and an HD drive.

### 9.2 The custom PLL mod

The WD1793's internal PLL is adequate for standard MFM at 250 kbit/s but limits performance at higher densities. Some clone manufacturers (notably Scorpion with the Scorpion ZS 256 Turbo) replaced the WD1793's internal PLL with an external, higher-performance PLL connected to a WD1791 (which has no internal PLL).

The external PLL can lock to weaker signals and tolerate more motor speed variation, allowing reliable reads of marginal disks. The downside is complexity: the external PLL is several extra chips, and the WD1791 has slightly different register behaviour than the WD1793 (the side-select bit is in a different place, for example).

### 9.3 Software turbo loaders

Without modifying hardware, software can achieve modest speed-ups by:

- **Skipping the NOT READY poll**: standard drivers wait for Status bit 7 (NOT READY) to clear before each access. Turbo loaders skip this wait on the assumption that the motor is already up to speed and `/READY` is asserted.
- **Using multi-sector reads**: instead of issuing READ SECTOR for each sector, issue one READ SECTOR with `m=1` to read the entire track in one command. This avoids the per-sector index-pulse wait.
- **Overlapping seeks and reads**: issue a SEEK, then start a READ SECTOR on the new track before the head has fully settled. Risky, but works on most drives.
- **Reading from uncontended memory**: on the 48K Spectrum, contended memory accesses delay the polling loop, causing lost data. Turbo loaders copy their inner DRQ-polling loop to upper RAM (uncontended) before reading.

Combined, these software techniques can roughly halve load times without any hardware changes. They are used by most "turbo" versions of TR-DOS and by many game loaders.

### 9.4 Modern replacements: emulator-only FDCs and HD/FPGA FDCs

For modern Spectrum hardware (ZX Evolution, ZX Next, Karabas, etc.), the original WD1793 / KR1818VG93 is often replaced by:

- **FPGA-implemented FDC**: an FPGA (Cyclone, MAX II, etc.) implements the WD1793 register interface but runs at any clock speed the FPGA supports. The FPGA can also add features the original chip lacked, like DMA, dual-buffer DRQ, or non-standard data rates.
- **Microcontroller-based FDC**: a small microcontroller (AVR, STM32) emulates the WD1793's register interface and handles the floppy drive via GPIO. This approach is used by some modern floppy emulators (e.g., HxC, Gotek with FlashFloppy firmware).
- **Cycle-exact WD1793 emulator in software**: for FPGA-based Spectrum clones (Next, Uno, Evolution), the FDC is just a piece of HDL running on the same FPGA as the Z80 core. This allows perfect WD1793 emulation with the option of "turbo" modes that don't correspond to any real hardware.

The ZX Spectrum Next, for example, implements a cycle-exact WD1793 model in its FPGA, with an optional "turbo" mode that doubles the data rate (effectively the 16 MHz mod). Software can detect this mode via a NextReg port and enable it for faster disk access.

### 9.5 The Nemo IDE / SMUC alternative

The most common "turbo" approach in the modern scene is to bypass floppy entirely and use IDE or SD card storage via interfaces like the Nemo IDE, SMUC, or DivIDE/DivMMC. These interfaces are an order of magnitude faster than any floppy system (a few milliseconds to read a sector vs. hundreds of milliseconds for floppy), and they use modern mass-storage formats (FAT16, FAT32).

See [divide_divmmc.md](divide_divmmc.md) and [ide_interface.md](ide_interface.md) for the IDE/SD alternatives. Floppy remains relevant for authenticity (running original disk-based games and demos) and for cycle-exact emulation work, but it is rarely used for primary storage on modern hardware.

---

## 10. Cross-references

### 10.1 Within the storage section

- [mfm_encoding.md](mfm_encoding.md) — the signal layer this chip produces and decodes. Read this first to understand the bit-stream view (sync marks, address marks, CRC) that the FDC manipulates through its Data register.
- [beta_disk_interface.md](beta_disk_interface.md) — the host glue that connects this FDC to the Spectrum's Z80: address decoder, port map (#1F–#3F), /ROMCS disk-rotate, TR-DOS ROM bank switching, and the WAIT-state logic that hides the FDC's slow register access from the CPU.
- [plus3_floppy.md](plus3_floppy.md) — the +3's on-board WD1772-PH controller, a single-density variant of the WD1793 with a simpler port map and integrated motor control. Useful as a point of comparison for command timing and register layout.
- [disk_format_overview.md](disk_format_overview.md) — the IBM 3740 physical sector layout that all Spectrum formats (TR-DOS, +3 DOS, CP/M, Opus) build on. The ID field, data field, gap layout, and CRC scheme described here are exactly what the WD1793's READ TRACK and WRITE TRACK commands operate on.
- [trd_disk_format.md](trd_disk_format.md), [plus3_dos_format.md](plus3_dos_format.md), [cpm_disk_format.md](cpm_disk_format.md), [opus_discovery_format.md](opus_discovery_format.md) — the logical disk formats layered on top of the physical sectors this controller reads and writes.
- [trd_scl_formats.md](trd_scl_formats.md), [dsk_fdi_formats.md](dsk_fdi_formats.md), [udi_format.md](udi_format.md), [scp_format.md](scp_format.md) — the image formats used to preserve and emulate the disks this controller accesses. The .SCP format in particular captures the raw flux transitions that the FDC's PLL sees on the read side.
- [hdd_overview.md](hdd_overview.md), [ide_interface.md](ide_interface.md), [divide_divmmc.md](divide_divmmc.md) — the IDE/SD storage interfaces that displaced floppy (and the WD1793) on modern hardware.

### 10.2 Adjacent hardware and system references

- [beta_disk_interface.md](beta_disk_interface.md) (also above) — the most common host for a WD1793 on the Spectrum.
- For the +3's controller: see [plus3_floppy.md](plus3_floppy.md). The WD1772-PH is register-compatible with the WD1793 but uses a fixed step rate and a different motor-control scheme.
- For the original WD1772 data sheet and the KR1818VG93 pinout: see the [14_references/](../../14_references/) directory.

### 10.3 Reverse engineering and demoscene angles

- For protection schemes that exploit FDC quirks (wrong track number, custom address marks, side-select trick): see the [05_reversing/](../../05_reversing/) section, in particular articles on [custom_loaders_and_drm.md](../../05_reversing/custom_loaders_and_drm.md) and [unpacking_and_decrunching.md](../../05_reversing/unpacking_and_decrunching.md).
- For turbo loaders used in demos and games: see [tape_interface.md](tape_interface.md) (the tape equivalent). Disk-based turbo loaders use the techniques described in §9.3 above.
- For cycle-exact emulation of the WD1793: see the [11_emulation/](../../11_emulation/) section.

### 10.4 External references

- **Western Digital FD179X-02 datasheet** — the original primary source. Reproduced electronically at <https://www.retrotechnology.com/herbs_stuff/WD179X.PDF> and <http://info-coach.fr/atari/documents/general/fd/WD177x-00.pdf>. Covers all four Type I–IV commands, the full per-command status bit table, electrical characteristics, and timing diagrams.
- **WD1793 on MSX Info Pages (Hans Otten)** — faithful electronic reproduction of the WD1793 datasheet with the IBM 34 format layout and the Type III data-pattern encoding table. <https://hansotten.file-hunter.com/technical-info/wd1793/>.
- **KR1818VG93 data sheet (Russian)** — the Soviet clone's official documentation. Differs from the WD data sheet in a few minor timing parameters (see §7).
- **app.note 17 "Floppy Disk Controller Design" (Western Digital)** — design notes for using the WD179X family, including recommended PLL circuits and write-precompensation values.
- **The "WD179X" entry in the sparetimegizmos.com FPGA FDC project** — an open-source HDL implementation of the WD1793, useful for understanding the chip's state machine.
- **The FDC directory at zxevo.ru** — Russian-language community documentation on Beta Disk Interface clones and turbo modifications.
- **unreal-ng emulator source** (`alfishe/unreal-ng` on GitHub) — a modern re-engineering of Unreal Speccy with a full C++ WD1793 model. The relevant files live in `core/src/emulator/io/fdc/`: `wd1793.cpp`, `wd1793.h`, `wd1793state.h`, `mfm_parser.h`. The `WD_STATUS` enum in `wd1793.h` defines all status bit constants; `WD93Counters` in `wd1793state.h` documents the byte-transfer windows (32 µs MFM / 64 µs FM) and the 5-revolution RNF timeout. Used as a primary reference for the FDC state machine in this article.

---

## License

This article is licensed under [Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0)](https://creativecommons.org/licenses/by-sa/4.0/).

You are free to:

- **Share** — copy and redistribute the material in any medium or format.
- **Adapt** — remix, transform, and build upon the material for any purpose, even commercially.

Under the following terms:

- **Attribution** — you must give appropriate credit (a link to this article is sufficient), indicate if changes were made, and indicate the license under which the original is released. You may do so in any reasonable manner, but not in a way that suggests the licensor endorses you or your use.
- **ShareAlike** — if you remix, transform, or build upon the material, you must distribute your contributions under the same license as the original.

The full legal text is available at the link above. A summary is available at <https://creativecommons.org/licenses/by-sa/4.0/>.

The trademarks **WD1793**, **WD1772**, **WD1771**, **WD179X**, **KR1818VG93**, **Beta Disk Interface**, **TR-DOS**, **+3 DOS**, **CP/M**, **ZX Spectrum**, **ZX Spectrum Next**, **ZX Evolution**, **Karabas**, **Peridot**, **DivIDE**, **DivMMC**, **Nemo IDE**, **SMUC**, **HxC**, **Gotek**, **FlashFloppy**, **SuperCard Pro**, **Western Digital**, and others mentioned in this document are the property of their respective owners and are used here for identification and educational purposes only. No endorsement by, or affiliation with, any of these trademark holders is implied.
