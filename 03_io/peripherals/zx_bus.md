# ZX Bus — The Expansion Edge Connector

## Overview

The **ZX Bus** is the name given (retroactively) to the 56-pin card-edge expansion connector on the rear of every ZX Spectrum model. The connector exposes the Z80's address bus, data bus, and most control signals, plus power rails, the CPU clock, and a handful of video/audio signals. Every peripheral in this directory — Interface 1, Interface 2, Multiface, Kempston joystick, ZX Printer, Beta 128, DivMMC, Z-Controller — connects to the Spectrum through this single connector.

The ZX Bus is **not a buffered, arbitrated bus** in the modern sense (PCIe, USB, VME). It is essentially **the bare Z80 CPU brought out to pins**, with the ULA's memory-control signals intermixed. This makes it powerful — peripherals can do anything the CPU can — but also fragile: there is no electrical isolation, no plug-and-play enumeration, and no automatic bus arbitration. Two peripherals claiming the same address line at the same time will short each other out.

This article covers the physical connector, the full signal reference, the **critical differences between the three model families** (16K/48K vs. 128K/+2 vs. +2A/+3), and the conventions that peripheral designers follow to stay compatible. For the canonical port-address reference, see [10_references/io_port_map.md](../../10_references/io_port_map.md). For ULA timing and the source of bus contention, see [02_hardware/original/ula_timing.md](../../02_hardware/original/ula_timing.md).

---

## Physical Connector

The connector is a **double-sided card edge** with 28 fingers on each side (56 total), at **0.1 inch (2.54 mm) pitch**. One finger position is omitted between lower pin 4 and lower pin 6 — this is the **key slot** that ensures correct orientation (lower pin 5 is not present).

Looking at the rear of the Spectrum with the connector pointing at you:

- **Upper row** (component side): pins numbered 1A-28A from right to left
- **Lower row** (solder side): pins numbered 1B-28B from right to left

Most peripherals mate with the connector using a 28+28 way printed-circuit board edge that slides into the Spectrum's slot. A pass-through female connector on the peripheral allows further peripherals to stack behind it, forming the classic "Spectrum sandwich" — a Spectrum with three or four peripherals stacked on its rear edge was a common sight in the late 1980s.

### ZX80/ZX81 compatibility

The Spectrum's edge connector is a **superset** of the earlier ZX80/ZX81 expansion connector. The data bus, low address lines (A0-A7), and a subset of control signals occupy the same positions relative to the key slot. The ZX Printer, designed originally for the ZX81, works on both because it uses only these legacy lines. Most Spectrum-specific peripherals (Interface 1, Multiface, etc.) use signals not present on the ZX81 and are not backward compatible.

### Soviet / Eastern clone variants

Soviet and Czech clones (Pentagon, Scorpion, Leningrad, Didaktik, Quorum) adopted the same logical signals but sometimes used **2.5 mm pitch** instead of 2.54 mm, and occasionally added extra pins for clone-specific features (extra RAM banking, alternate video modes). Soviet peripherals generally do not physically fit a Western Spectrum without an adapter, and the addition of clone-specific pins means a Western peripheral may not work even with a mechanical adapter. See [02_hardware/clones/README.md](../../02_hardware/clones/README.md) for the clone ecosystem.

---

## Full Pinout (Cross-Model Composite)

The table below shows the 56-pin connector with signals that are **consistent across all models** (or where the differences are noted). Pins marked `NC` on a particular model have no connection on that model — they may carry signals on other models (see "Per-Model Differences" below).

| Upper | Signal | Lower | Signal |
|-------|--------|-------|--------|
| 1A | A15 | 1B | A14 |
| 2A | A13 | 2B | A12 |
| 3A | D7 | 3B | +5V |
| 4A | /ROM1OE (only +2A/+3) | 4B | +9V (16K/48K/128K/+2 only) |
| — | **key slot** | — | **key slot** |
| 5A | (slot for key) | 5B | (slot for key) |
| 6A | D0 | 6B | 0V |
| 7A | D1 | 7B | 0V |
| 8A | D2 | 8B | CK (CPU clock) |
| 9A | D6 | 9B | A0 |
| 10A | D5 | 10B | A1 |
| 11A | D3 | 11B | A2 |
| 12A | D4 | 12B | A3 |
| 13A | /INT | 13B | /IORQULA |
| 14A | /NMI | 14B | 0V |
| 15A | /HALT (also /ROM2OE on +2A/+3) | 15B | VIDEO (16K/48K) |
| 16A | /MREQ | 16B | Y (luminance, 16K/48K) |
| 17A | /IORQ | 17B | V (color-diff, 16K/48K) |
| 18A | /RD | 18B | U (color-diff, 16K/48K) |
| 19A | /WR | 19B | /BUSRQ |
| 20A | −5V (16K/48K only) | 20B | /RESET |
| 21A | /WAIT | 21B | A7 |
| 22A | +12V | 22B | A6 |
| 23A | +12V AC (16K/48K only) | 23B | A5 |
| 24A | /M1 | 24B | A4 |
| 25A | /RFSH (not on issue 6A) | 25B | /ROMCS (16K/48K/128K/+2 only) |
| 26A | A8 | 26B | /BUSACK |
| 27A | A10 | 27B | A9 |
| 28A | NC | 28B | A11 |

All `/`-prefixed signals are **active-low**. The CPU control signals follow the standard Z80 convention.
---

## Signal Groups

### Address bus (A0–A15)

The full 16-bit Z80 address bus is exposed (16 pins). During memory cycles, A0–A15 select the byte address; during I/O cycles, A0–A7 contain the port number duplicated across both halves of the bus (so `OUT (#FB),A` drives A0–A15 = #FBFB), and A8–A15 carry the contents of the accumulator-shadow register — useful for "free" extra decode bits.

All 16 address lines are **tri-stated** during a `/BUSACK` cycle, so a DMA peripheral can drive them directly.

### Data bus (D0–D7)

The full 8-bit Z80 data bus (8 pins). Bidirectional, tri-state. Pulled up weakly inside the ULA so that an undriven bus reads as `#FF`. The data bus is shared with the ULA's video memory reads — every 8th CPU cycle during the active display is stolen by the ULA, which is the source of the Spectrum's "contended memory" timing. See [02_hardware/original/ula_timing.md](../../02_hardware/original/ula_timing.md) for the contention pattern.

### Memory / I/O control

| Signal | Active | Function |
|--------|--------|----------|
| `/MREQ` | low | Memory request — address bus holds a valid memory address |
| `/IORQ` | low | I/O request — address bus (low half) holds a valid port number |
| `/RD` | low | Read — CPU is reading from data bus |
| `/WR` | low | Write — CPU is writing to data bus |
| `/M1` | low | Machine cycle 1 — CPU is fetching an opcode (or acknowledging an interrupt) |
| `/RFSH` | low | Refresh — address bus holds a DRAM refresh address (absent on issue 6A boards) |

The `/M1` + `/IORQ` combination is the **interrupt-acknowledge** signal: the CPU is responding to an interrupt and expects a vector byte on the data bus. This is the basis of the Multiface overlay trick (`M1` fetch at `#0066` triggers a flip-flop that pages in the Multiface ROM/RAM).

### CPU state and interrupts

| Signal | Direction | Function |
|--------|-----------|----------|
| `/INT` | into CPU | Maskable interrupt — pulled low by ULA once per video frame (~50 Hz PAL, ~60 Hz TS2068) |
| `/NMI` | into CPU | Non-maskable interrupt — pulled low by Multiface button, some other peripherals |
| `/WAIT` | into CPU | Insert wait states — ULA pulls low during contended memory |
| `/HALT` | from CPU | CPU has executed a HALT instruction and is idle |
| `/RESET` | bidirectional | Reset — power-on reset pulse, can be driven by peripherals to force a reboot |
| `/BUSRQ` | into CPU | Bus request — peripheral asks CPU to release the bus for DMA |
| `/BUSACK` | from CPU | Bus acknowledge — CPU has released the bus (tri-stated A, D, and control) |

The `/INT` line is **open-collector**: multiple peripherals can pull it low simultaneously. The ULA's 50 Hz interrupt is the standard frame interrupt used by games for animation timing. A peripheral can also pull `/INT` for its own purposes (e.g., a mouse-polling ISR), but it must follow the Z80's interrupt-acknowledge protocol — typically IM2 mode with a vector table.

### Special signals

| Signal | Function |
|--------|----------|
| `/ROMCS` | ROM chip-select (active-low). On 16K/48K/128K/+2, pulling this high disables the internal 16K ROM, allowing external ROM or RAM to occupy `#0000-#3FFF`. **Not present on +2A/+3.** |
| `/ROM1OE`, `/ROM2OE` | On +2A/+3 only — output-enable for the two physical ROM chips (32K total split as 2×16K). Replaces `/ROMCS`. A peripheral that wants to overlay ROM must drive both of these. |
| `/IORQULA` | Composite signal: `IORQ & A0=0`. Set low when the CPU is doing an I/O cycle with A0 low — i.e., reading or writing a `#FE`-class port (keyboard, ULA, etc.). Useful for peripherals that want to override ULA port reads. |
| `CK` | CPU clock — nominally 3.5 MHz on the 16K/48K (3.54690 MHz exact), derived from the ULA. **Interrupted during contended memory access** — peripherals that clock themselves from `CK` must tolerate the jitter. (Note: accidentally unconnected on the Spanish 128K.) |

### Video signals (16K/48K only)

The 16K/48K exposes composite video and the three luminance/chrominance signals (`Y`, `U`, `V`) for S-Video-like output. These were removed on later models as the RF modulator was replaced with a built-in composite output and the YUV signals dropped. The +2A/+3 reuses these pins for `/ROM1OE` and `/ROM2OE`.

### Power rails

| Pin | Voltage | Notes |
|-----|---------|-------|
| 3B | +5V | Regulated logic supply — available on all models, up to ~500 mA spare |
| 4B | +9V | Unregulated DC from the external PSU — **removed on +2A/+3**. Powered the ZX Printer's motor. |
| 20A | −5V | Negative bias for the DRAMs — **16K/48K only** |
| 22A | +12V | Positive supply for the DRAMs — available on all models |
| 23A | +12V AC | AC supply (part of the DRAM bias network) — **16K/48K only** |
| 6B, 7B, 14B | 0V | Ground (3 pins) |

The removal of `+9V` on the +2A/+3 is the single most compatibility-breaking change in the ZX Bus history — it broke the ZX Printer and several other peripherals that drew motor power from this line. See [printers.md](printers.md) and [interface2.md](interface2.md) for the affected peripherals.


---

## Per-Model Differences

The three families of Sinclair-manufactured Spectrums expose slightly different signals on the edge connector. A peripheral designed for one family may not work on another.

### 16K / 48K / 48K+ (1982–1984)

The most "complete" edge connector. Provides:

- **`+9V`** on lower pin 4 (powers the ZX Printer)
- **`−5V`** on upper pin 20 and **`+12V AC`** on upper pin 23 (used by the internal DRAM bias network)
- **Composite video** on lower pin 15 (also fed to the RF modulator)
- **Y/U/V video** on lower pins 16/17/18 (luminance + two chrominance difference signals, useful for S-Video mod)
- **`/ROMCS`** on lower pin 25 — drives the chip-select of the internal 16K ROM
- **`/IORQULA`** on lower pin 13 — composite IORQ+A0 signal
- **`CK`** on lower pin 8 — the CPU clock

Some issue 6A motherboards omit the `/RFSH` line (the ULA generates refresh internally).

### 128K / +2 grey (1986–1987)

Largely the same as 16K/48K, with:

- All video signals still present
- `+9V` still present (ZX Printer compatible)
- `/ROMCS` still present
- Composite video moved to a dedicated RCA jack; lower pin 15 still carries video but is no longer the primary output
- The AY-3-8912 sound chip adds stereo audio (one channel left, one right, one to the beeper)
- EAR/MIC consolidated to a single 3.5 mm jack (was two on 16K/48K)
- The Spanish 128K (Investronica) accidentally left `CK` (lower pin 8) unconnected — a known factory bug

### +2A / +2B / +3 / +3B (1987–1990)

Amstrad substantially redesigned the edge connector. This is the most **incompatible** variant:

- **`+9V` REMOVED** from lower pin 4 — breaks ZX Printer, some Disk interfaces, some Multiface variants
- **`−5V` REMOVED** from upper pin 20
- **`+12V AC` REMOVED** from upper pin 23
- **`/ROMCS` REMOVED** from lower pin 25 — replaced by **`/ROM1OE`** (upper pin 4) and **`/ROM2OE`** (upper pin 15, formerly `/HALT`)
- Composite video and Y/U/V signals removed (the +2A/+3 has built-in composite via the AY chip's video output stage and the RF modulator was redesigned)
- Lower pin 15 was composite video on 16K/48K — now `/ROM2OE`. Plugging a 16K/48K peripheral that reads pin 15 into a +2A/+3 will see logic-level signals instead of analog video.

The two new `/ROM1OE` / `/ROM2OE` lines reflect the +2A/+3's two-physical-ROM design: the 32K ROM is split as two 16K chips, each with its own output-enable. A peripheral that wants to overlay ROM must drive **both** lines.

This is why the **ZX Interface 2** (which only drives `/ROMCS`) does not work on the +2A/+3 — its ROM cartridge cannot disable the internal ROMs. The "two-diode fix" wires the Interface 2's `/ROMCS` output to both `/ROM1OE` and `/ROM2OE` through diodes, restoring compatibility. See [interface2.md](interface2.md).

### Pentagon, Scorpion, and other clones

Most Soviet clones follow the 48K connector pinout (with `+9V`, `/ROMCS`, etc.) but with **2.5 mm pitch** instead of 2.54 mm. The Pentagon in particular exposes the full 48K signal set. Scorpion adds extra banking pins for its 256K+ memory. See [02_hardware/clones/README.md](../../02_hardware/clones/README.md).

### TS2068 / TC2048 (Timex)

The Timex TS2068 uses a **different expansion connector** (a 64-pin box header) and adds extra video modes (the "Timex Sinclair" 64×192 dual-pixel mode and the 512×192 hi-res mode). The TC2048 (Portuguese variant) uses the standard Spectrum connector. See [02_hardware/clones/clone_timing.md](../../02_hardware/clones/clone_timing.md) for related discussion.

---

## Memory Access from the Bus

The Spectrum's memory map is `#0000-#3FFF` ROM, `#4000-#FFFF` RAM. The edge connector exposes everything needed to overlay the ROM:

### The `/ROMCS` trick (16K/48K/128K/+2)

Pulling `/ROMCS` (lower pin 25) high disables the internal 16K ROM. The peripheral can then drive the data bus for any memory access to `#0000-#3FFF`. The simplest use of this is **ROM cartridges**: a 16K ROM chip on the cartridge, with its `/OE` gated by `/MREQ`, `/CE` gated by `A14`, and `/OE2` gated by `A15` — exactly the Interface 2 design. See [interface2.md](interface2.md) for the cartridge decode logic.

More sophisticated peripherals use **paged ROM**: the peripheral overlays a 16K region into `#0000-#3FFF` only on demand, typically triggered by an `M1` fetch at a specific address (e.g., `#0008` for Interface 1, `#0066` for Multiface). When the trigger fires, the peripheral pulls `/ROMCS` high and drives its own ROM onto the bus; when the paging condition clears, `/ROMCS` returns low and the internal ROM is back. This is the basis of the shadow-ROM architecture.

### No `/RAMCS` — a deliberate omission

Unlike the ZX81, the Spectrum does **not** expose a `/RAMCS` line. A peripheral cannot disable the internal RAM and overlay its own RAM in `#4000-#FFFF`. The only way to add more than 48K of RAM is via the **banking** approach: page extra RAM into the `#0000-#3FFF` slot (over the disabled ROM) and bank-switch it from there. This is how the 128K and later models implement their extra RAM — see [04_operating_systems/system_variables.md](../../04_operating_systems/system_variables.md) for the paging registers.

The lack of `/RAMCS` also means ROM-cartridge programs are limited to 16K (one bank at `#0000-#3FFF`) — they cannot overlay their own RAM. This is the reason no Spectrum ROM cartridge ever exceeded 16K, and is a key commercial reason the cartridge format failed (the home computer market moved to disk-based distribution).

### I/O access from the bus

Every I/O cycle puts the port number on A0–A7 (and a copy on A8–A15), with `/IORQ` low and either `/RD` or `/WR` low. A peripheral decodes a port by checking some subset of the address lines. The conventions:

- **Single-line decode** (e.g., `A0=0` for ULA at `#FE`) — responds to 32768 port addresses; very simple hardware, but conflicts with anything else using the same line
- **Partial decode** (e.g., `A0=0, A5=0, A7=0`) — Kempston joystick at `#1F` actually uses this style; conflicts are less likely
- **Full decode** (e.g., `A0-A7` all checked) — responds to one specific port only; most flexible but most logic

See [10_references/io_port_map.md](../../10_references/io_port_map.md) for the canonical port assignment list.

### `M1`-triggered overlays

The `M1` fetch is special because it always coincides with `/MREQ` low and lasts longer than a normal memory read. Several peripherals use an `M1` fetch at a specific address as a paging trigger:

- **Interface 1**: `M1` at `#0008` or `#1708` (the RST restart vectors and the error handler) pages in the 8K shadow ROM
- **Multiface**: `M1` at `#0066` (the NMI vector) or `#0067` (with an extra flip-flop) pages in the 8K overlay ROM and 8K overlay RAM
- **DISCiPLE / +D**: similar `M1` trick to page the GDOS ROM

The `M1` trick works because the Z80 always does an `M1` fetch before executing any instruction — so the moment the CPU tries to execute from the trigger address, the peripheral gets control before the internal ROM has a chance to drive the bus.


---

## Bus Mastering (DMA)

The edge connector supports full bus mastering via the Z80's standard `/BUSRQ` and `/BUSACK` signals. The protocol:

1. Peripheral pulls `/BUSRQ` (lower pin 19) low.
2. CPU finishes the current machine cycle, then tri-states the address bus, data bus, and `/MREQ`, `/IORQ`, `/RD`, `/WR`, `/RFSH` signals, and pulls `/BUSACK` (lower pin 26) low.
3. Peripheral sees `/BUSACK` low and takes over: it drives the address bus, data bus, and control signals to do its own memory or I/O accesses.
4. Peripheral releases `/BUSRQ` high when done.
5. CPU releases `/BUSACK` and resumes normal execution.

This is the standard Z80 bus-arbitration handshake. On the Spectrum, **very few peripherals actually used DMA** — the most notable being:

- **Currah μSource** and **Currah μSpeech** — used `/BUSRQ` briefly during speech-synthesis memory access
- **Larken** disk interface — DMA-style disk transfer
- **Rotronics Wafadrive** — internal DMA for the wafer tape loop
- Some Russian disk interfaces — direct memory access for fast disk transfers

Most disk interfaces (Beta 128, Opus Discovery, Interface 1's Microdrive) did **not** use DMA — they used PIO with the CPU as the bus master. This is one reason Spectrum disk I/O is slow compared to contemporary platforms.

### ULA contention

The ULA steals cycles from the CPU during the active display to read video bytes from RAM. During these cycles, the ULA pulls `/WAIT` low, freezing the CPU. The contention pattern is documented in [02_hardware/original/ula_timing.md](../../02_hardware/original/ula_timing.md) and depends on which scanline is being drawn.

For peripherals using DMA: the ULA still does its video reads during a DMA cycle. If the peripheral accesses contended memory (`#4000-#7FFF` on the 48K), the ULA may also be accessing the same memory — there is no arbitration. In practice, DMA peripherals should either avoid contended memory or accept the timing jitter.

---

## Interrupts from Peripherals

### `/INT` (maskable)

Open-collector, shared with the ULA's 50 Hz frame interrupt. A peripheral can pull `/INT` low at any time. The CPU will respond (if interrupts are enabled, `EI`) by acknowledging via `/M1` + `/IORQ`. The CPU expects an 8-bit vector on the data bus (in IM2 mode), which the peripheral must supply.

Standard pattern for a peripheral interrupt in IM2:

```z80
; Peripheral pulls /INT low
; CPU does /M1 + /IORQ
; Peripheral must drive D0-D7 with the low byte of the vector table address
; The vector table address is: I_reg << 8 | vector_byte
; The vector table entry is a 16-bit pointer to the ISR
```

The ULA's frame interrupt does NOT supply a vector — it relies on IM1 mode (default after `RST 08` etc.) and jumps to `#0038`. A peripheral that wants to coexist with the ULA interrupt should use IM2 with its own vector, and chain to the ULA's `#0038` handler if it did not source the interrupt.

### `/NMI` (non-maskable)

`/NMI` is also exposed on the connector (upper pin 14). The CPU jumps to `#0066` on the next instruction boundary. The Multiface uses `/NMI` for its "red button" snapshot feature — pressing the button triggers the Multiface's overlay. See [multiface.md](multiface.md).

Because `/NMI` is not shareable (no vector mechanism), only one NMI-source peripheral can be installed at a time. Most peripherals avoid `/NMI` for this reason.

---

## Peripheral Stacking

The classic Spectrum configuration has multiple peripherals stacked on the rear edge:

```
[Spectrum] ← [Interface 1] ← [Interface 2] ← [Kempston Joystick] ← [ZX Printer]
```

The ordering matters because:

1. **ROM-overlay peripherals** (Interface 1, Multiface) need to be **first in the chain** (closest to the Spectrum) so they can intercept `/ROMCS` and `M1` first. If a non-ROM peripheral is between the Spectrum and an ROM-overlay peripheral, the `/ROMCS` line won't propagate correctly.
2. **Passive peripherals** (Kempston joystick interface, simple parallel port adapters) can go anywhere — they only listen to the bus, they don't drive it back.
3. **Bus-mastering peripherals** should be at the **end of the chain** so they don't have to propagate `/BUSRQ` / `/BUSACK` through downstream devices.
4. **The ZX Printer draws significant current from +9V** — long chains cause voltage drop and the printer may fail.

Most commercially available peripherals include a pass-through female connector for stacking. The cheap "stick" peripherals (Kempston joystick dongle, simple Centronics adapter) often omit the pass-through and must be the last in the chain.

---

## Common Pitfalls

1. **The +2A/+3 dropped `+9V` and `/ROMCS`.** Any peripheral that uses either of these lines will not work on a +2A/+3 without modification. Check the peripheral's documentation. The two-diode fix restores `/ROMCS`-based overlays.

2. **The ZX Bus is the bare CPU bus.** There is no electrical isolation. Plugging two peripherals that drive the same data line simultaneously will short them and may damage both. Always turn off the Spectrum before connecting or disconnecting peripherals (the bus is hot-plug-hostile).

3. **`/INT` is open-collector but `/NMI` is not.** Multiple peripherals can share `/INT` (with pull-up), but only one should drive `/NMI`. The Multiface uses `/NMI` exclusively — don't stack two Multiface variants.

4. **Long chains cause signal degradation.** The address and data buses are unbuffered. After 3-4 peripherals in a chain, the capacitance and the resistance of the edge connectors cause ringing and timing errors. Use a buffered expansion backplane for chains longer than 3 peripherals.

5. **The `CK` signal is interrupted during contended memory.** Peripherals that clock themselves from `CK` must tolerate 1-3 cycle gaps. The issue 6A 48K and the Spanish 128K omit `CK` entirely — peripherals that depend on it won't work.

6. **The issue 6A 48K omits `/RFSH`.** Peripherals that use `/RFSH` to detect refresh cycles (e.g., some DRAM-based add-ons) will not work on issue 6A boards.

7. **`/BUSRQ` halts the CPU but not the ULA.** During `/BUSACK`, the ULA still does video reads from RAM. A DMA peripheral accessing `#4000-#7FFF` will collide with the ULA and produce display corruption.

8. **The data bus is shared with the ULA.** During a video read (every 8th cycle during active display), the ULA drives the address bus and reads the data bus. A peripheral that drives the data bus during a ULA video cycle will corrupt the display.

9. **`/ROMCS` only works for `#0000-#3FFF`.** There is no `/RAMCS`. Don't try to overlay the RAM region — it can't be done from the edge connector.

10. **`/RESET` is bidirectional.** A peripheral can drive `/RESET` low to force a reboot. But this also resets any other peripherals that depend on power-on state. Use `/NMI` for a "soft" reset.

11. **The IORQULA signal is a composite, not a true decode.** It indicates `IORQ & A0=0`, but the ULA may be in the middle of its own I/O cycle. Peripherals that try to override ULA port reads using `/IORQULA` may race.

12. **Soviet clones use 2.5 mm pitch.** A Western peripheral will not fit a Soviet Spectrum clone without an adapter — and the adapter must also translate any clone-specific banking signals. See [02_hardware/clones/README.md](../../02_hardware/clones/README.md).

---

## When to Use the ZX Bus (Today)

| Use case | Recommendation |
|----------|----------------|
| Writing a new peripheral for real hardware | Target the 16K/48K connector — it has the most signals and the widest compatibility. Use only signals present on all models if possible |
| Emulator authors | Implement the full 16K/48K signal set. Emulate `/ROMCS`, `/M1`, `/NMI`, `/INT` accurately — many peripherals depend on subtle timing of these signals |
| Modern Pi-based peripherals (DivMMC, Z-Controller, etc.) | Use the standard 16K/48K pinout. Avoid depending on `+9V` (use `+5V` instead) for compatibility with the +2A/+3 |
| New storage interface | Use the existing DivMMC or Z-Controller conventions — don't reinvent the port decode. See [z_controller.md](z_controller.md) |
| Building a backplane / expansion box | Buffer the address and data buses with 74HCT244/245 chips. Buffer `/MREQ`, `/IORQ`, `/RD`, `/WR`, `/M1`, `/RFSH`, `/RESET`. Don't buffer `/INT`, `/NMI`, `/BUSRQ`, `/BUSACK`, `/WAIT` — they're open-collector / require direct connection |
| Restoring a 1980s peripheral chain | Inspect the edge connector contacts; clean with isopropyl alcohol. Oxidation is the #1 cause of intermittent peripheral failures |

---

## Comparison Matrix

| Feature | 16K/48K | 128K/+2 | +2A/+3 | Pentagon | TS2068 |
|---------|---------|---------|--------|----------|--------|
| Pitch | 2.54 mm | 2.54 mm | 2.54 mm | 2.5 mm | 2.54 mm (different connector) |
| `/ROMCS` available | ✅ | ✅ | ❌ (replaced by `/ROM1OE` + `/ROM2OE`) | ✅ | n/a |
| `+9V` line | ✅ | ✅ | ❌ | ✅ | n/a |
| Composite video pin | ✅ | ✅ | ❌ | ✅ | n/a |
| Y/U/V video pins | ✅ | ✅ | ❌ | ✅ | n/a |
| `/RFSH` | ✅ (except issue 6A) | ✅ | ✅ | ✅ | n/a |
| `CK` (CPU clock) | ✅ | ✅ (except Spanish 128K) | ✅ | ✅ | n/a |
| `/BUSRQ` / `/BUSACK` | ✅ | ✅ | ✅ | ✅ | n/a |
| ZX Printer compatible | ✅ | ✅ | ❌ | ❌ | ❌ |
| Interface 2 ROM cartridges | ✅ | ✅ | ❌ (without mod) | ❌ | ❌ |


---

## Modern Analogies

- **The ZX Bus ≈ the bare Z80 CPU on header pins.** No buffers, no arbitration, no Plug-and-Play. It is what you would get if you took a microcontroller and brought every GPIO pin to a 0.1" header — full freedom, full responsibility.
- **The `/ROMCS` overlay trick ≈ bank-switched boot ROMs on embedded systems.** A watchdog or reset controller swaps the boot ROM based on a hardware trigger, exactly like the Multiface's `M1` overlay.
- **The +2A/+3 signal removals ≈ Apple's frequent connector changes.** Removing `+9V` and `/ROMCS` forced a complete redesign of the peripheral ecosystem, much like Apple's 30-pin → Lightning → USB-C transitions.
- **The lack of `/RAMCS` ≈ modern PC's lock on the lower BIOS region.** Even when you can replace the boot ROM, you can't replace the system RAM from an expansion slot — that's a CPU-internal decision.
- **The unbuffered bus with stacking ≈ SCSI-1 without active termination.** Long chains accumulate reflections and signal integrity problems; only short, well-terminated chains work reliably.
- **The hot-plug hostility ≈ the original IBM PC ISA bus.** Both assumed the user would turn off power before changing hardware; both would happily let users destroy their machines by ignoring that.
- **The peripheral-stack-on-edge ≈ a USB hub daisy-chain.** Both let you add multiple peripherals to a single host port, both have signal-integrity limits on chain length, both eventually require a powered external hub/backplane.
- **The `/IORQULA` composite signal ≈ a dedicated "chip select" line derived from address decode.** The ULA saved a TTL chip by combining two signals into one, at the cost of flexibility.

---

## Cross-References

- [10_references/io_port_map.md](../../10_references/io_port_map.md) — Canonical I/O port assignment reference
- [02_hardware/original/ula_timing.md](../../02_hardware/original/ula_timing.md) — ULA timing, contended memory, CPU clock jitter
- [02_hardware/original/ula_architecture.md](../../02_hardware/original/ula_architecture.md) — ULA design, video memory access
- [02_hardware/clones/README.md](../../02_hardware/clones/README.md) — Soviet/Czech clone variants of the ZX Bus (2.5 mm pitch, extra banking pins)
- [02_hardware/clones/clone_timing.md](../../02_hardware/clones/clone_timing.md) — Per-clone timing and bus differences
- [interface1.md](interface1.md) — Interface 1's shadow-ROM trick using `M1` at `#0008`
- [interface2.md](interface2.md) — Interface 2 cartridge decode via `/ROMCS` + A14/A15 + `/MREQ`
- [multiface.md](multiface.md) — Multiface overlay using `/NMI` and `M1` at `#0066`
- [printers.md](printers.md) — ZX Printer depends on +9V line (removed on +2A/+3)
- [z_controller.md](z_controller.md) — Modern SD-card peripheral using the bus
- [05_development/04_interrupts/interrupt_programming.md](../../05_development/04_interrupts/interrupt_programming.md) — Z80 IM2 interrupt handling on the Spectrum
- [05_development/02_assembly/README.md](../../05_development/02_assembly/README.md) — Z80 assembly language reference for the Spectrum

---

## Primary Sources

1. **Sinclair Wiki — ZX Spectrum edge connector** — `sinclair.wiki.zxnet.co.uk/wiki/ZX_Spectrum_edge_connector`. Cross-model composite pinout, model differences, ZX80/ZX81 compatibility notes.
2. **Sinclair Wiki — ZX Spectrum 16K/48K edge connector** — `sinclair.wiki.zxnet.co.uk/wiki/ZX_Spectrum_16K/48K_edge_connector`. Detailed notes on power, video, clock, and `/IORQULA`.
3. **ZX Interface 2 Circuitry (fruitcake.plus.com)** — `fruitcake.plus.com/Sinclair/Interface2/Interface/Interface2_Circuitry.htm`. Documents the +2A/+3 signal changes including `/ROM1OE` / `/ROM2OE`.
4. **The ZX Spectrum ROM Disassembly** — Logan & O'Hara, 1983. Documents the `M1`-triggered shadow ROM mechanism for Interface 1.
5. **Z80 CPU Product Specification** — Zilog, 1976 (and later revisions). The definitive reference for `/BUSRQ`, `/BUSACK`, `/M1`, `/RFSH`, `/INT`, `/NMI`, `/WAIT`, `/HALT`.
6. **World of Spectrum — Peripherals FAQ** — `worldofspectrum.org/faq/reference/peripherals.htm`. Survey of commercial peripherals and their bus usage.
7. **The Hardware Book — ZX Spectrum Expansion Port** — `hardwarebook.info/`. Compact pinout reference.
8. **SpeccyWiki (Polish)** — `speccy.wiki.pirmipl.pl`. Additional photos of clone variants and their edge-connector deviations.
