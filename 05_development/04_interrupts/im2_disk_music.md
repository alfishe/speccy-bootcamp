[← Home](../../README.md) · [Interrupts](README.md)

# Disk Load with AY Music — The Concurrency Math

One of the most famous demoscene effects on the Pentagon and other disk-equipped Spectrum clones is the "load a sector while playing music" trick. To an observer it looks like the disk is loading and the music is playing at the same time. In reality the situation is more subtle: the WD1793 FDC's strict byte-timing requirements conflict with the frame-interrupt's loose 50 Hz heartbeat, and the math shows that true concurrency is **practically impossible** on stock hardware. What demos actually do is a set of carefully-engineered approximations.

This article explains the math (derived from Ivan Roshchin's classic Adventurer #9 article), the workarounds real demos use, and the practical code patterns for playing music while reading sectors.

> [!NOTE]
> This article assumes you understand TR-DOS programming from [trdos_programming.md](../08_dos_tape/trdos_programming.md) and ISR integration from [interrupt_programming.md](interrupt_programming.md).

---

## Why This Is Hard

### The WD1793 Byte Budget

The WD1793 (Russian clone: VG93 / KR1818VG93) is a simple FDC. When reading a sector, it asserts `DRQ` (Data Request) each time a byte is ready in its 1-byte data register. The CPU has approximately **32 T-states** to read the byte before the next one overwrites it.

```text
Disk data rate: 250 kbit/s = 31,250 bytes/s
T-states per byte at 3.5 MHz: 3,500,000 / 31,250 = 112 T-states/byte nominal

But the FDC has a 1-byte buffer with no FIFO. The CPU must read within
half the bit-cell window before the next byte shifts in. Effective
deadline: ~32 T-states per byte on average, less in worst case.
```

### The Interrupt Conflict

A maskable interrupt firing during a sector read causes the CPU to:
1. Acknowledge the interrupt (~19 T-states for IM2)
2. Jump to the ISR
3. Execute the ISR body
4. Return with `EI; RETI` (~18 T-states)

Even an **empty** ISR consumes ~40 T-states. A real music player ISR (Arkos AKG, PT3) takes 1,500-3,000 T-states. The FDC's 32-T-state byte budget is blown by orders of magnitude.

The result: if an interrupt fires during a `READ SECTOR` command, the FDC loses bytes, sets the Lost Data bit in the status register, and the entire sector read fails with a CRC error.

---

## Ivan Roshchin's Math

The canonical analysis comes from Ivan Roshchin's article *TR-DOS: the disk included with the interrupt* in Adventurer #9 (Russian disk magazine, zxpress.ru). The full derivation:

### Frame Rate vs Disk Rotation

| Parameter | Value |
|---|---|
| Pentagon clock | 3.5 MHz |
| Pentagon T-states per frame | 71,680 |
| **Pentagon frame rate** | **48.83 Hz** (not 50) |
| Disk rotation | 300 RPM = 5 revolutions/sec |
| Interrupts per revolution | 48.83 × 60 / 300 = **9.77** (not integer) |

The frame rate is not exactly 50 Hz, and the disk does not rotate an integer number of interrupt periods per revolution. The two clocks drift relative to each other.

### Byte-Position Drift

| Parameter | Value |
|---|---|
| Track data capacity | 6,250 bytes (at 250 kbit/s for one revolution) |
| Bytes between interrupts | 6,250 / 9.77 = **~640 bytes** |
| Per-revolution drift | 640 × 0.77 = **~150 bytes** (Roshchin's theoretical value) |
| Empirical drift on Roshchin's Pentagon | **~138 bytes** (slightly slower rotation: 299.4 RPM) |

### Sector Read Outcomes by Sector Size

A standard TR-DOS sector is 256 bytes. Consider the worst-case scenario: the interrupt fires at offset 0 within the sector on revolution 1.

| Revolution | Interrupt offset (within sector) | Sector read? |
|---|---|---|
| 1 | 0 | **FAIL** (interrupt mid-read) |
| 2 | 138 | **FAIL** (interrupt mid-read) |
| 3 | 276 (wraps to 276-256=20) | **SUCCESS** (interrupt falls in gap between sectors) |

**Worst case: 3 revolutions per sector.** For an entire TR-DOS disk (160 tracks × 16 sectors = 2,560 sectors), reading with interrupts enabled at this worst-case rate:

```text
Normal read: 32 seconds (1 rev/sector × 2560 sectors / 5 rev/sec / 16 sectors-per-rev)
With interrupts: 32 × 3 = 96 seconds
```

A 3× slowdown. Tolerable for a demo loader, painful for a game.

### MS-DOS Sectors (512 bytes)

Larger sectors make the problem worse. For MS-DOS-formatted disks (512-byte sectors):

| Revolution | Offset | Outcome |
|---|---|---|
| 1 | 0 | FAIL |
| 2 | 138 | FAIL |
| 3 | 276 | FAIL |
| 4 | 414 | FAIL |
| 5 | 552 (wraps to 40) | SUCCESS (sometimes) |
| ... or 9 revolutions worst case | | |

Empirically, MS-DOS track reads with interrupts enabled average 5-9 revolutions per sector. A 1024-byte sector is **completely impossible** — the sector is so long that two or more interrupts always fall within it.

### Why Format Commands Are Impossible

Track formatting requires writing the index pulse, sector headers, and data fields in one continuous revolution. Any interrupt during format corrupts the entire track structure. **Never attempt format with interrupts enabled.**

---

## Real-World Workaround Patterns

Three patterns appear in demoscene loaders that need to combine disk reads with music.

### Pattern A — Music After Sector (POWER UP EYE ACHE 2)

The simplest pattern, used by demos where seamless music is more important than fast loading. The main loop alternates between reading one sector and running one frame of music:

```text
Loop:
  1. Read one sector from disk (interrupts disabled)
  2. Enable interrupts
  3. Call music player (synchronized to current CPU time, not to vblank)
  4. Disable interrupts
  5. Advance to next sector
  6. Go to Loop
```

The music plays at roughly the right tempo because the sector-read time is approximately one frame. But the music is **not synchronized to vblank** — it drifts relative to the video frame. This produces audible jitter in fast tempos. Ivan Roshchin describes the symptom: "read errors are accompanied by unpleasant howling."

```z80
; Simplified POWER UP pattern
load_with_music:
    DI
    LD   HL,(sector_ptr)
    LD   DE,(buf_ptr)
    CALL read_one_sector   ; ~10000 T-states with interrupts OFF
    ; Sector loaded
    EI                     ; Allow interrupt to fire
    HALT                   ; Wait for it (synchronizes music)
    CALL play_music        ; Music advances
    DI                     ; Back to disk work
    LD   HL,(sector_ptr)
    INC  HL                ; Next sector
    LD   (sector_ptr),HL
    LD   A,(sectors_left)
    DEC  A
    LD   (sectors_left),A
    JR   NZ,load_with_music
    RET
```

**Pros**: simple, robust, no data loss.
**Cons**: slow (3× slowdown from worst-case interrupts during retry, plus HALT overhead), music not perfectly synced.

### Pattern B — Stop-Motor Resync

A more complex pattern that enables true music-vblank synchronization. The trick: stop the drive motor between sectors, restart it aligned to a vblank edge, then read the next sector with interrupts disabled.

```text
Loop:
  1. Wait for vblank (HALT)
  2. Run music player
  3. Stop drive motor
  4. Restart drive motor (will be aligned to next sector pulse)
  5. Wait for motor to reach full speed (300 ms)
  6. Disable interrupts
  7. Read one sector (interrupts off, no data loss)
  8. Enable interrupts
  9. Go to Loop
```

The 300 ms motor spin-up time per sector is catastrophic for throughput. A 2560-sector disk read would take **13 minutes**. This pattern is only used for very small amounts of data (e.g. loading a single high-resolution screen, ~7 KB / 28 sectors = 8 seconds).

```z80
motor_resync_loader:
    HALT                   ; Wait for vblank
    CALL play_music        ; Music in sync
    CALL stop_motor        ; OUT (#FF),motor_off
    LD   B,200             ; ~30 ms delay
.spinup_wait:
    HALT                   ; ~20 ms per frame
    DJNZ .spinup_wait
    CALL start_motor      ; OUT (#FF),motor_on
    DI
    CALL read_one_sector   ; Interrupts off, no retry
    EI
    JR   motor_resync_loader
```

**Pros**: perfect music sync, no data loss.
**Cons**: extremely slow due to motor spin-up.

### Pattern C — Custom WD1793 Driver

Bypass TR-DOS hook codes entirely. Manage the WD1793 directly, polling `DRQ` and `INTRQ` in a tight loop. Interrupts can be enabled during seek operations (long, no byte-level timing pressure) and disabled only during the actual byte-stream read.

```z80
custom_read_sector:
    ; --- Seek phase: interrupts OK ---
    EI
    LD   A,(target_track)
    CALL wd_seek_track     ; ~50 ms with interrupts on
    DI                     ; From here, no interrupts

    ; --- Issue READ SECTOR command ---
    LD   A,(target_sector)
    OUT  (#F7),A           ; Sector register
    LD   A,#20             ; READ SECTOR command (assuming #F7 is cmd port)
    OUT  (#F7),A

    ; --- Byte-by-byte read loop ---
    LD   HL,(buf_ptr)
    LD   B,0               ; 256 bytes
.read_loop:
    IN   A,(#F7)           ; Status
    AND  #02               ; DRQ bit
    JR   Z,.read_loop      ; Wait for DRQ
    IN   A,(#F6)           ; Data register
    LD   (HL),A
    INC  HL
    DJNZ .read_loop

    EI                     ; Safe to enable interrupts now
    RET
```

This is the fastest pattern: sector reads happen at full speed with no retries, music plays during seek operations. Requires writing your own seek, format-detect, and error-recovery code — typically 500-1000 lines of assembler.

**Pros**: maximum speed, music plays during seeks.
**Cons**: significant code complexity, must reimplement WD1793 driver logic.

---

## Western DOS Behavior

### +3DOS (the +2A/+3 DOS)

The +2A/+3 use a UPD765 FDC (not the WD1793), which has a deeper 16-byte FIFO. Sector reads can tolerate interrupts up to ~16 × 32 = 512 T-states before data loss — much more forgiving than the WD1793's single-byte buffer.

The +3DOS API exposes `DOS_READ` as an RSX (Resident System Extension) hook. It internally disables interrupts during the byte-critical section but re-enables them during seek operations. Calling `DOS_READ` from main code with interrupts enabled is **safe** on the +3.

```z80
; +3DOS read with interrupts enabled
    EI
    LD   C,#07             ; DOS_READ RSX hook code
    LD   DE,file_handle
    LD   HL,buffer
    LD   BC,256            ; Bytes to read
    CALL #DOS_READ         ; Internally manages interrupt state
```

### ESXDOS (DivIDE / DivMMC)

ESXDOS uses IDE/SD storage which is block-buffered at the hardware level. A 512-byte sector arrives as a complete block; the API call returns it to a memory buffer. Interrupts during the API call are harmless because the hardware holds the data stable in its own buffer until the CPU reads it.

```z80
; ESXDOS sector read with interrupts enabled
    EI
    LD   B,1               ; 1 sector
    LD   C,#40             ; ESA_READ sector opcode
    LD   HL,buffer
    LD   DE,sector_number_low
    RST   #08              ; ESXDOS hook
    DB   #A0              ; ESA_READ sector opcode
```

Because ESXDOS uses block-buffered hardware, the Ivan Roshchin math does not apply. You can play music through the entire load with no data loss risk.

### Comparison Table

| DOS / Hardware | FDC | Interrupt tolerance | Music during load |
|---|---|---|---|
| TR-DOS (Beta 128) | WD1793 / VG93 | **Intolerant** — 1-byte buffer | Only via patterns A/B/C above |
| +3DOS (+2A/+3) | UPD765 | Tolerant — 16-byte FIFO | Yes, via RSX calls |
| ESXDOS (DivIDE) | IDE / SD | Fully tolerant — block buffered | Yes, seamless |
| NextZXOS (Next) | SD via DMA | Fully tolerant — DMA does the work | Yes, seamless |

---

## Worked Example — Minimal TR-DOS Music Loader

A complete, working pattern combining Pattern A (music-after-sector) with a simple AY player. The music tempo will drift slightly but no data is lost.

```z80
    ORG  #8000
start:
    ; --- Install IM2 ISR for music ---
    DI
    LD   A,#FE
    LD   I,A
    LD   HL,#FE00
    LD   (HL),#90
    LD   DE,#FE01
    LD   BC,#0100
    LDIR
    LD   HL,#9090
    LD   (HL),#C3           ; JP opcode
    INC  HL
    LD   HL,music_isr
    LD   (#9091),HL         ; JP music_isr
    IM   2

    ; --- Init music ---
    LD   HL,music_data
    CALL PLY_AKG_INIT

    ; --- Set up loader state ---
    LD   HL,0
    LD   (sector_counter),HL
    LD   HL,#C000
    LD   (buf_ptr),HL
    LD   A,32               ; Load 32 sectors (~8KB)
    LD   (sectors_left),A

    EI

load_loop:
    ; --- Disable interrupts, read one sector ---
    DI

    ; TR-DOS READ-SECTOR call
    LD   A,(current_track)
    LD   (#5CF6),A
    LD   A,(current_sector)
    LD   (#5CF7),A
    LD   HL,(buf_ptr)
    LD   DE,#3D13           ; TR-DOS hook
    LD   A,#02              ; READ-FILE hook code
    ; ... actually set up #5CF6 system variables per TR-DOS API ...

    ; For demonstration, assume hook code #02 loads 256 bytes to (buf_ptr)

    ; --- Re-enable interrupts ---
    EI
    HALT                    ; Synchronize to vblank
    CALL PLY_AKG_PLAY       ; Advance music one frame

    ; --- Advance buffer and sector counters ---
    LD   HL,(buf_ptr)
    LD   DE,256
    ADD  HL,DE
    LD   (buf_ptr),HL

    LD   A,(current_sector)
    INC  A
    CP   17                 ; Sector 16 is last on a track
    JR   NZ,.same_track
    LD   A,1
    LD   (current_sector),A
    LD   A,(current_track)
    INC  A
    LD   (current_track),A
    JR   .next
.same_track:
    LD   (current_sector),A
.next:
    LD   A,(sectors_left)
    DEC  A
    LD   (sectors_left),A
    JR   NZ,load_loop

    ; --- Done ---
    RET

music_isr:
    PUSH AF : PUSH BC : PUSH DE : PUSH HL
    PUSH IX : PUSH IY
    EX   AF,AF'
    EXX
    PUSH AF : PUSH BC : PUSH DE : PUSH HL

    CALL PLY_AKG_PLAY

    POP  HL : POP  DE : POP  BC : POP  AF
    EXX
    EX   AF,AF'
    POP  IY : POP  IX
    POP  HL : POP  DE : POP  BC : POP  AF
    EI
    RETI

; --- Variables ---
sector_counter:  DW  0
buf_ptr:         DW  #C000
sectors_left:    DB  32
current_track:   DB  0
current_sector:  DB  1
```

**Caveat**: this code calls the music player from the ISR **and** from the main loop after each sector. That is a bug — the player would advance twice per frame. Pick one location. In real loaders, the main loop calls the player and the ISR only sets a "frame happened" flag. The version above is simplified for clarity.

---

## Antipatterns

### Calling TR-DOS Hook Codes with Interrupts Enabled

The TR-DOS hook codes at `#3D13` internally use the WD1793 with no interrupt protection beyond their own critical sections. Calling them with interrupts enabled can corrupt sector reads silently.

```z80
; BAD: TR-DOS call with interrupts on
    EI
    LD   A,#02             ; READ hook code
    CALL #3D13             ; Sector read may fail
```

**Fix**: always wrap TR-DOS hook calls in `DI`/`EI`:

```z80
    DI
    LD   A,#02
    CALL #3D13
    EI
```

### Bank Switching Without Saving State

On 128K machines, the ISR must save and restore the `#7FFD` bank state. The Hudson Hawk pattern (see [im2_effects.md](im2_effects.md)) is the canonical solution.

### Format with Interrupts

```z80
; BAD: formatting a track with interrupts on
    EI
    LD   A,#04             ; FORMAT TRACK command
    CALL #3D13
```

Formatting requires one continuous revolution of writing. Any interrupt corrupts the entire track. **Always `DI` before format.**

### Trying 1024-byte Sectors

As shown in the math section, 1024-byte sectors cannot be read with interrupts enabled — the sector is so long that at least one interrupt always falls inside it. If your disk image uses 1024-byte sectors, you must either disable interrupts entirely during the read or convert the disk image to use 256-byte or 512-byte sectors.

### Calling the Music Player from Both ISR and Main Loop

A common bug in loader code. The music player is not re-entrant; calling it twice per frame advances the music twice, producing a chipmunk effect.

```z80
; BAD: player called twice
music_isr:
    CALL PLY_AKG_PLAY       ; Once here, in ISR
    ; ...

main_loop:
    CALL load_sector
    CALL PLY_AKG_PLAY       ; And again here
```

**Fix**: call the player from exactly one location. The ISR is the standard choice because it gives consistent timing regardless of main-loop work.

---

## Cross-References

- **[trdos_programming.md](../08_dos_tape/trdos_programming.md)** — TR-DOS hook codes, sector read API, IY preservation rules
- **[dos_programming.md](../08_dos_tape/dos_programming.md)** — +3DOS RSX, ESXDOS, NextZXOS APIs (all interrupt-tolerant)
- **[fdc_vg93.md](../../03_io/storage/fdc_vg93.md)** — WD1793 register reference, DRQ/INTRQ timing
- **[ay_player_routines.md](../../06_sound/players/ay_player_routines.md)** — Music player ISR integration patterns
- **[interrupt_programming.md](interrupt_programming.md)** — Foundational IM2 mechanics
- **[im2_effects.md](im2_effects.md)** — Demoscene ISR patterns including the Hudson Hawk bank-switching trick
- **[nmi.md](nmi.md)** — Why NMI is catastrophic during disk I/O

## Sources

- Ivan Roshchin, *TR-DOS: the disk included with the interrupt* (Adventurer #9, zxpress.ru) — canonical derivation of disk-interrupt math, empirical Pentagon drift measurements
- Gasman, *Compatibility: An open letter to the Russian scene* (Subliminal Extacy #3, zxpress.ru) — context on why some demos fail on original Spectrums
- *Beta Disk Interface Manual V4* — Technology Research official TR-DOS documentation
- *ESXDOS manual* — DivIDE/DivMMC API reference
- *+3DOS Technical Reference* — UPD765 FDC behavior and RSX hook list
---
