[← Home](../../README.md) · [Display & Timing](README.md)

# Floating Bus — Per-Model Behavior and Raster Sync

The **floating bus** is an unintended feature of the ZX Spectrum's hardware design: when the CPU reads from contended memory during the paper display area, the data bus may contain **the byte the ULA just fetched** for screen generation rather than the actual memory contents. Demoscene programmers turned this quirk into a raster synchronization tool.

---

## Why the Floating Bus Exists

During the paper area (192 display scanlines), the ULA reads screen memory in a repeating pattern:

```
Every 8 T-states, the ULA performs 2 memory reads:
  T-states 0-3:  Read one pixel byte
  T-states 4-7:  Read one attribute byte
```

The ULA drives the DRAM address bus and reads the data into its internal shift register for video output. When the CPU also tries to read from the same DRAM chip set during this window, the CPU may latch the **data the ULA just placed on the bus** rather than initiating its own separate read cycle.

The result: `LD A,(HL)` where HL points to contended memory may return a pixel or attribute byte from the screen being generated — not the actual memory value at that address.

---

## 48K Floating Bus — The Reference Behavior

The 48K is the best-documented and most predictable floating bus implementation.

### Which Addresses Return Floating Data

The floating bus effect occurs when the CPU reads **any address in `#4000`–`#7FFF`** during the paper area. The specific address doesn't matter — it's the DRAM chip set that matters, and on the 48K, `#4000`–`#7FFF` is the entire contended range.

### What Value You Get

```
During each 8-T-state ULA fetch cycle within a paper scanline:

  T-state offset 0-3:   ULA reads a PIXEL byte
    → CPU reads return the pixel byte the ULA just fetched

  T-state offset 4-7:   ULA reads an ATTRIBUTE byte
    → CPU reads return the attribute byte the ULA just fetched
```

The pixel and attribute bytes correspond to the **current column position** on the current scanline being generated:

```
Column 0:  T-states 0-7   (pixel byte 0, then attribute byte 0)
Column 1:  T-states 8-15  (pixel byte 1, then attribute byte 1)
...
Column 31: T-states 248-255 (pixel byte 31, attribute byte 31)
After column 31: No ULA fetches → returns previous bus value (unreliable)
```

### Reading via IN — Port #FF

You can also read the floating bus via `IN A,(#FF)` (or any even port with A0=0). This is the common technique because it avoids needing to set up HL:

```z80
; Read the floating bus value
    IN   A,(#FF)         ; Returns current ULA fetch data
    ; A = pixel or attribute byte depending on exact T-state
```

> [!NOTE]
> Port `#FF` is not a real I/O device — it's just a convenient way to trigger a read cycle that picks up whatever is on the data bus. Any `IN A,(port)` where bit 0 of the port address is 0 will work (because these all alias the ULA's I/O decoding).

---

## Using the Floating Bus for Raster Sync

The floating bus lets you **detect which scanline the ULA is currently generating** without any port access or timing-critical delays.

### Principle

Each scanline has a unique sequence of pixel and attribute bytes. By reading the floating bus in a tight loop and looking for a specific pattern, you can synchronize your code to a particular scanline position.

### Wait for a Specific Attribute Value

```z80
; Wait until the ULA is fetching a specific attribute byte
; This synchronizes to the scanline containing that attribute
WaitForAttr:
    IN   A,(#FF)         ; Read floating bus
    CP   #47             ; White ink on red paper, bright
    JR   NZ,WaitForAttr  ; Not yet — keep polling
    ; Now the raster is at the position where this attribute appears
    ; You have ~4 T-states before the next fetch changes the value
    RET
```

### Wait for Paper Area Entry

```z80
; Detect transition from border (no ULA fetches) to paper area
; During border: floating bus returns #FF (or random stale data)
; During paper: returns actual pixel/attribute bytes
WaitForPaperStart:
    IN   A,(#FF)
    CP   #FF             ; #FF = border area (no fetch)
    JR   Z,WaitForPaperStart
    ; Just entered paper area — raster is at scanline 64 (first paper line)
    ; First non-FF value is pixel byte 0 of the top-left character cell
    RET
```

### Scanline Counter Using Floating Bus

```z80
; Count scanlines by watching the floating bus pattern
; Each scanline = 32 pixel bytes + 32 attribute bytes in sequence
; Look for a repeating byte to detect scanline boundaries
CountScanlines:
    LD   B,0             ; Counter
    LD   C,#FF           ; Previous value
.scan:
    IN   A,(#FF)
    CP   C               ; Same as last time?
    JR   Z,.scan         ; Yes — still in same fetch window
    LD   C,A             ; Update previous
    ; Check if this looks like a scanline boundary
    ; (attribute byte 31 → pixel byte 0 of next line)
    ; Simplified: count transitions
    INC  B
    JR   NZ,.scan
    ; B = number of unique values seen
    RET
```

---

## Per-Model Floating Bus Differences

### 48K — Reliable

The floating bus is well-defined and consistent across all 48K machines with the Ferranti ULA. The pattern is predictable and reproducible.

### 128K / +2 — Mostly Compatible

The 128K uses the same Ferranti ULA, so floating bus behavior is **similar to the 48K**. However:

- Minor timing differences (228T per scanline vs 224T) shift the alignment slightly
- Some 128K revisions return slightly different values during certain T-states
- The shadow screen affects what bytes the ULA fetches — if displaying Bank 7, the floating bus returns Bank 7's pixel/attribute data

Most floating-bus-based raster sync code works on the 128K without modification.

### +2A / +3 — Unreliable

The Amstrad gate array has **significantly different** floating bus behavior:

- Some T-states return `#FF` (no useful data)
- The pattern does not follow the clean pixel/attribute alternation of the Ferranti ULA
- **Floating bus is NOT reliable for raster sync on +2A/+3**

Programs targeting the +2A/+3 should use interrupt-based or HALT-based synchronization instead.

### Pentagon — No Floating Bus

The Pentagon has no ULA and no bus contention mechanism. There is **no floating bus effect**. Reading `IN A,(#FF)` returns `#FF` or stale bus data — no screen content.

```z80
; Pentagon-safe raster sync — use HALT + delay instead
PentagonRasterSync:
    HALT                ; Wait for INT
    ; Calculate delay to desired scanline
    LD   BC,TARGET_DELAY
.wait:
    DEC  BC
    LD   A,B
    OR   C
    JR   NZ,.wait
    RET
```

### ZX Spectrum Next — Configurable

The Next can emulate 48K floating bus behavior in compatible modes, but it is **not enabled by default**. Programs relying on the floating bus should check the machine type.

---

## Floating Bus Summary Table

| Model | Floating bus? | Pattern | Reliable for raster sync? |
|-------|--------------|---------|--------------------------|
| 48K | **Yes** | Clean pixel/attr alternation | **Yes** |
| 128K / +2 | **Yes** | Similar to 48K, minor shifts | **Mostly** |
| +2A / +3 | **Partial** | Irregular, many #FF gaps | **No** |
| Pentagon | **No** | Returns #FF / stale data | **No** |
| Scorpion | **Varies** | Revision-dependent | **Uncertain** |
| ZX Spectrum Next | **Configurable** | 48K emulation mode only | **In compatible mode** |

---

## Cross-References

- **48K video frame** (floating bus position in frame): [video_frame_48k.md](video_frame_48k.md)
- **128K video frame** (floating bus differences): [video_frame_128k.md](video_frame_128k.md)
- **Raster timing** (HALT-based sync, beam position): [raster_timing.md](raster_timing.md)
- **Contention model** (when memory access is delayed): [contention_model.md](../03_memory_and_io/contention_model.md)
- **ULA timing** (hardware mechanism of ULA fetch): [ula_timing.md](../../02_hardware/original/ula_timing.md)
