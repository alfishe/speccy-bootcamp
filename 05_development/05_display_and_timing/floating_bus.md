[← Home](../../README.md) · [Display & Timing](README.md)

# Floating Bus — Per-Model Behavior and Raster Sync

The **floating bus** is an unintended feature of the ZX Spectrum's hardware design: when the CPU reads an I/O port that no device decodes, nothing drives the data bus, and the CPU samples the state of the ULA's bus instead — during the paper area, **the screen byte the ULA is transferring to its video circuits**; when the ULA is idle, `#FF`. Demoscene programmers and commercial game authors turned this quirk into a raster synchronization tool.

---

## Why the Floating Bus Exists

The ULA owns the lower 16K DRAM and its data path, and during the paper area the screen bytes it fetches transit the ULA bus. If the CPU performs a read cycle that **no device answers** — an undecoded I/O port — nothing actively drives the data bus, so the CPU samples whatever is on it: a display byte mid-transfer, or `#FF` while the ULA is idle. The ULA's bus state, not memory contents, decides the value — hence "floating".

> [!WARNING]
> **Memory reads are not the floating bus.** A `LD A,(HL)` from contended memory returns the **correct** byte — the access is merely delayed by contention (see [contention_model.md](../03_memory_and_io/contention_model.md)). The floating bus is observed only through reads that put no real device on the bus: undecoded I/O ports, and memory regions where no RAM is fitted (e.g. `#8000`+ on a 16K machine).

During roughly **60% of the frame** — the paper area — reads return a mix of display bytes and `#FF` (idle slots); the remaining ~40% — border and vertical retrace — returns `#FF` deterministically. The ratio and mechanism are documented in the [World of Spectrum 16K/48K Reference](https://fizyka.umk.pl/~jacek/zx/faq/reference/48kreference.htm).

---

## 48K Floating Bus — The Reference Behavior

The 48K is the best-documented and most predictable floating bus implementation.

### Which Reads Observe the Floating Bus

| Read type | Floating bus? | Why |
|---|---|---|
| Undecoded odd port (`IN A,(#FF)`) | **Yes** | No port hardware answers; bus undriven |
| Port `#FE` / any even port | No | ULA decodes A0=0 and supplies keyboard/EAR data |
| `#FFFD` / `#BFFD` on 128K/+2/+2A/+3 | No | AY chip decodes the port and drives the bus |
| Contended memory (`#4000`–`#7FFF`) | No | Real RAM access — delayed by contention, correct data |
| Unattached memory (e.g. `#8000`+ on 16K) | **Yes** | No RAM fitted; nothing drives the bus |

On a bare 48K, every odd port is undecoded — `IN A,(#FF)` is simply the conventional choice.

### What Value You Get

Each paper scanline's fetch activity consists of **16 slots of 8 T-states** (128 T-states total; the remaining 96 T-states of the 224 T-state line are idle). Each slot fetches **two character cells** — four bytes back to back, then four idle cycles ([Sinclair Wiki — Floating bus](https://sinclair.wiki.zxnet.co.uk/wiki/Floating_bus)):

```
Per 8 T-state slot (cells n and n+1):
  T+0:  bitmap byte of cell n        → readable on the floating bus
  T+1:  attribute byte of cell n     → readable
  T+2:  bitmap byte of cell n+1      → readable
  T+3:  attribute byte of cell n+1   → readable
  T+4..T+7: idle                     → #FF
```

The Z80 **samples the data bus during the final T-state of the I/O machine cycle** ([Sinclair Wiki — Floating bus](https://sinclair.wiki.zxnet.co.uk/wiki/Floating_bus)) — the value an `IN` returns corresponds to one specific T-state, not an average or a latched level. This is why per-T-state tables are the authoritative reference, and why poll-loop timing must be calibrated against the polling instruction's T-state footprint.

First slot of the first paper scanline, relative to the INT assertion:

| Model | First fetch T-state |
|---|---|
| 48K early timing | 14338 |
| 48K late timing | 14339 (+1) |
| 128K / +2 | 14364 |

The attribute byte of a cell is fetched on **every scanline of its 8-line character row** — the same value eight lines running. An attribute-value match therefore pins the beam to a **character row**, not to a single scanline (see the sync examples below).

### Reading via IN — Port #FF

You can also read the floating bus via `IN A,(#FF)` — or any **odd** port (A0=1). This is the common technique because it avoids needing to set up HL:

```z80
; Read the floating bus value
    IN   A,(#FF)         ; Returns current ULA fetch data
    ; A = pixel or attribute byte depending on exact T-state
```

> [!NOTE]
> Port `#FF` is not a real I/O device — on the 48K, no hardware decodes it. The ULA's port requires A0=0 (and returns keyboard/EAR data), so an odd-port read leaves the data bus **undriven** and the CPU simply samples whatever is on it: passive pull-up resistors pull an idle bus toward `#FF`, and during the paper area the ULA's screen fetches are the last thing on the bus. This is the same undriven bus that makes the IM2 interrupt vector read `#FF` — see [interrupt_programming.md](../04_interrupts/interrupt_programming.md). Do not confuse this with TR-DOS's port `#FF`, which is the FDC status register while the TR-DOS ROM is paged in — see [beta_disk_interface.md](../../03_io/storage/beta_disk_interface.md).

---

## Using the Floating Bus for Raster Sync

The floating bus lets you **detect which scanline the ULA is currently generating** with nothing but a port read in a tight loop — no dedicated timing hardware required.

### Principle

Bitmap bytes are unique to a scanline, and attribute bytes repeat for the 8 scanlines of a character row. By reading the floating bus in a tight loop and looking for a specific byte or pattern, you can synchronize your code to a particular scanline or character-row position.

### Wait for a Specific Attribute Value

```z80
; Wait until the ULA is fetching a specific attribute byte
; This synchronizes to the character row containing that attribute
WaitForAttr:
    IN   A,(#FF)         ; Read floating bus
    CP   #47             ; White ink on red paper, bright
    JR   NZ,WaitForAttr  ; Not yet — keep polling
    ; Now the raster is on a scanline of the character row holding
    ; that attribute — the value changes on the next fetch cycle
    ; (attributes repeat for all 8 scanlines of the row)
    RET
```

### Wait for Paper Area Entry

```z80
; Detect transition from border (no ULA fetches) to paper area
; During border and idle slots: floating bus returns #FF (deterministic)
; During paper fetch slots: returns the bitmap/attribute bytes
WaitForPaperStart:
    IN   A,(#FF)
    CP   #FF             ; #FF = border area (no fetch)
    JR   Z,WaitForPaperStart
    ; Just entered paper area — raster is at scanline 64 on 48K
    ; (63 on 128K/+2); first non-FF value is bitmap byte 0 of the
    ; top-left character cell
    RET
```

### Synchronize to a Specific Character Row

The commercial pattern: preload one attribute row with a marker value that appears nowhere else in display or attribute data, then wait for the ULA to fetch it:

```z80
; Attribute row at #5B00 preloaded with a unique marker (e.g. #C7,
; chosen so no bitmap or attribute byte anywhere on screen equals it)
WaitForRow:
    IN   A,(#FF)         ; Read floating bus (11T)
    CP   #C7             ; Unique marker (7T)
    JR   NZ,WaitForRow   ; (12/7T) — 30T steady-state poll period
    ; The ULA just fetched the marker: beam is in that character row
    RET
```

A marker collision elsewhere on screen causes a premature match — choose the value with the whole display in mind. From this row anchor, calibrated delays reach a specific scanline; see [race_the_beam.md](../04_interrupts/race_the_beam.md) for the full precision ladder.

### Commercial Users

Several commercial games shipped floating-bus sync, generally to synchronize drawing with the display and avoid flicker ([Sinclair Wiki — Floating bus](https://sinclair.wiki.zxnet.co.uk/wiki/Floating_bus)):

- **Arkanoid** and **Cobra** — original releases only; the later Hit Squad budget re-releases dropped the technique
- **Sidewize** and **Short Circuit**

### Pitfalls

1. **`IN A,(#FF)` self-contention.** For `IN A,(n)` the Z80 emits the current `A` as the **high byte** of the port address — and a port whose high byte lies in `#40`–`#7F` is treated by the ULA as a contended access during the paper area ([World of Spectrum 16K/48K Reference](https://fizyka.umk.pl/~jacek/zx/faq/reference/48kreference.htm)). A poll loop whose `A` holds a freshly read byte in that range silently slows and skews its timing. Keep `A` out of `#40`–`#7F`, or recalibrate for the contended period.
2. **Attribute matches repeat for 8 scanlines.** The same attribute byte is re-fetched on every line of a character row — a value match alone cannot tell scanline 0 of the row from scanline 7. Add per-line timing or distinct marker values per row.
3. **`#FF` is ambiguous.** Idle slots, border, and vertical retrace all read `#FF`. A non-`#FF` value proves the ULA is fetching paper data; `#FF` alone proves nothing about position.

---

## Per-Model Floating Bus Differences

### 48K — Reliable

The floating bus is well-defined and consistent across all 48K machines with the Ferranti ULA. The pattern is predictable and reproducible.

### 16K — Same Behavior, Plus Floating Memory

The 16K machines use the same Ferranti ULA as the 48K, so undecoded-port reads float identically. They add one extra case: with no RAM fitted above `#8000`, reads of that unattached region also observe the floating bus — the same "no device answers" rule applied to memory ([Sinclair Wiki — Floating bus](https://sinclair.wiki.zxnet.co.uk/wiki/Floating_bus)).

### 128K / +2 — Same Pattern, Shifted

The grey 128K and +2 keep ULA-style fetch behavior, so the slot pattern is **identical to the 48K's** — only the frame geometry differs:

- **228 T-states per scanline** (vs 224 T) and 311 lines per frame
- The first paper fetch arrives at **T 14364** instead of 14338 (see the table above)
- The ULA fetches from whichever screen bank is displayed — with the shadow screen (Bank 7) selected via `#7FFD` bit 3, the floating bus carries **Bank 7's** bitmap and attribute bytes

Byte-pattern polling (marker values, paper-entry detection) works unmodified; only code calibrated in absolute T-states must be redone for the 228 T line.

### +2A / +3 — Unreliable

The Amstrad gate array has **significantly different** floating bus behavior:

- Some T-states return `#FF` (no useful data)
- The pattern does not follow the clean pixel/attribute alternation of the Ferranti ULA
- **Floating bus is NOT reliable for raster sync on +2A/+3**

Programs targeting the +2A/+3 should use interrupt-based or HALT-based synchronization instead.

### Pentagon — No Floating Bus

The Pentagon rebuilds the Spectrum in TTL logic — no ULA chip, no contention, and **no floating bus**. `IN A,(#FF)` never returns screen bytes (typically `#FF`), so pattern-based raster sync is impossible; only `HALT` plus a calibrated delay works:

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

The Next core implements the floating bus, and its pattern follows the **machine timing profile** selected in nextreg 3 bits 6-4 (`000`/`001` = 48K, `010` = 128K/+2, `100` = Pentagon) — [SpecNext — TBBlue I/O port system](https://www.specnext.com/tbblue-io-port-system/). Two nextreg 8 bits can break floating-bus code:

- **Bit 6 = 1 disables RAM contention** (0 after a hard reset) — the ULA-arbitration delays that accompany the real fetch pattern are then gone
- **Bit 2 = 1 enables Timex modes** (0 after a hard reset) — port `#FF` is then handled by hardware instead of floating, and `IN A,(#FF)` stops observing the bus

With the default settings (contention on, Timex modes off) under a 48K or 128K timing profile, `IN A,(#FF)` behaves as on the corresponding original machine.

---

## Floating Bus Summary Table

| Model | Floating bus? | Pattern | Reliable for raster sync? |
|-------|--------------|---------|--------------------------|
| 48K | **Yes** | 16 slots × 8 T: two cells, then idle `#FF` | **Yes** |
| 16K | **Yes** | Same ULA; `#8000`+ memory reads also float | **Yes** |
| 128K / +2 | **Yes** | Identical pattern; 228 T lines; first fetch T 14364 | **Mostly** |
| +2A / +3 | **Partial** | Irregular, many #FF gaps | **No** |
| Pentagon | **No** | Returns #FF / stale data | **No** |
| Scorpion | **Varies** | Revision-dependent | **Uncertain** |
| ZX Spectrum Next | **Yes** | Follows the nextreg 3 timing profile | **Yes** (with default nextreg 8 settings) |

---

## Cross-References

- **48K video frame** (floating bus position in frame): [video_frame_48k.md](video_frame_48k.md)
- **128K video frame** (floating bus differences): [video_frame_128k.md](video_frame_128k.md)
- **Raster timing** (HALT-based sync, beam position): [raster_timing.md](raster_timing.md)
- **Contention model** (when memory access is delayed): [contention_model.md](../03_memory_and_io/contention_model.md)
- **ULA timing** (hardware mechanism of ULA fetch): [ula_timing.md](../../02_hardware/original/ula_timing.md)
- **IM2 interrupt vector `#FF`** (same undriven data bus, pull-up resistors): [interrupt_programming.md](../04_interrupts/interrupt_programming.md)

---

## References

### External references

- [Chris Smith — *The ZX Spectrum ULA: How to Design a Microcomputer* (2010)](http://www.zxdesign.info/) — the definitive reference for the floating bus phenomenon; documents the exact T-states during which the ULA reads screen bytes, leaving the stale data on the bus that the CPU can sample via `IN A, (#FF)`.
- [Sinclair ZX Specifications (Martin Korth)](http://problemkaputt.de/zxdocs.htm) — canonical hardware reference covering the 48K ULA's address-decode logic and the bus-keeper circuitry that produces the floating bus signature; documents the gate-array differences that change the floating bus behavior on 128K / +2 / +2A / +3.
- [World of Spectrum — 16K/48K Reference](https://fizyka.umk.pl/~jacek/zx/faq/reference/48kreference.htm) — community-verified reference for the floating bus values returned at each T-state of the 48K video frame, the port-decode rules (odd ports float; the ULA decodes A0=0), and the `IN A,(n)` self-contention pitfall for high bytes in `#40`–`#7F`.
- [Sinclair Wiki — Floating bus](https://sinclair.wiki.zxnet.co.uk/wiki/Floating_bus) — the canonical per-slot fetch model (16 × 8 T slots, two cells per slot, `#FF` idle cycles), the 48K/128K first-fetch T-states, the final-T-state sampling rule, and the list of commercial games using the effect.
- [ZEsarUX — Floating Bus Implementation (GitHub)](https://github.com/chernandezba/zesarux) — emulator reference implementation of the 48K / 128K / +2A / +3 / Pentagon floating bus behavior, including the irregular `#FF` gaps that make the +2A/+3 unreliable for raster sync.
- [zx-pk.ru — floating bus and raster sync subforum](https://zx-pk.ru/) — primary Russian-language community archive for per-clone floating bus findings (Pentagon returns `#FF`, Scorpion varies by revision, ATM Turbo implements a clean emulation of the 48K pattern).
