[← Home](../../README.md) · [New Gen Hardware](README.md) · [ZX Spectrum Next](zx_next.md)

# ZX Spectrum Next — DMA Controller

The ZX Spectrum Next's **DMA controller** is a hardware data mover that performs memory-to-memory, memory-to-I/O, and I/O-to-I/O transfers without CPU intervention. Derived from the **Zilog Z80 DMA** (the Z8410 chip used in CP/M-era systems and the Amstrad CPC), the Next's DMA is the platform's solution to "do this 16 KB block copy / pattern fill / sample load while I'm computing something else" — replacing thousands of `LDIR` cycles with a single register write that fires off the transfer and returns immediately.

This article is the **programmer's reference**: the DMA register set, the transfer modes, the burst vs byte modes, pattern fills, and the typical programming sequence. For the platform overview, see [zx_next.md](zx_next.md). For sibling features, see [Layer 2](zx_next_layer2.md), [sprites](zx_next_sprites.md), [tilemap](zx_next_tilemap.md), and [copper](zx_next_copper.md).

---

## What DMA Does — and Does Not

The DMA controller moves bytes between **a source and a destination**, both of which can be either a memory address or an I/O port. The CPU writes a small configuration block to the DMA's register file, then issues a "load" command — the DMA takes over the bus and performs the transfer at the Z80's full bus speed (or faster, in turbo mode).

| Property | Value |
|---|---|
| **Source types** | Memory address, I/O port |
| **Destination types** | Memory address, I/O port |
| **Transfer modes** | Byte (one byte per bus cycle), Burst (continuous until source/dest not ready), Continuous (entire transfer in one bus lock) |
| **Transfer length** | Up to 64 KB per command (16-bit counter) |
| **Address increment** | Source/destination can each be incremented, decremented, or held fixed |
| **Pattern matching** | Yes — transfer can stop when a specific byte is read (search mode) |
| **Interrupt on completion** | Yes (optional) |
| **CPU involvement** | **Zero** during the transfer — CPU is paused (bus arbitration) until the DMA completes |
| **Throughput at 28 MHz** | ~28 MB/s (memory-to-memory, byte mode) — vs ~3.5 MB/s for `LDIR` at 3.5 MHz |

The DMA is **not** magic — it steals bus cycles from the CPU, so during a DMA transfer the CPU is halted (or slowed). The advantage over `LDIR` is:

1. **No instruction fetch overhead** — DMA reads source and writes destination in dedicated cycles.
2. **No register pressure** — DMA uses its own internal registers; CPU registers are preserved.
3. **Pattern matching** — DMA can stop mid-transfer on a byte match, useful for string operations.
4. **I/O ports** — DMA can drive an I/O port (e.g., the sprite upload port) directly, useful for streaming data.

---

## The DMA Register Set

The DMA is programmed through a **command register file** accessed via two ports:

| Port | Function |
|---|---|
| `#6B` | **Register select / command write** — write a register number or command byte here |
| `#7B` | **Register data** — write/read the selected register's value |

The DMA's register file follows the **Z80 DMA convention** — there are a set of "_WR0" through "_WR6" command registers, each controlling a different aspect of the transfer. The Z80 DMA's programming model is notoriously baroque (a single `#6B` write can encode multiple settings via bit fields); the Next's DMA is a faithful clone of this behavior.

### The Command Bytes

The DMA is configured by writing a sequence of command bytes to `#6B`. Each command byte has a 3-bit "register class" in the upper bits and parameters in the lower bits. The most important commands:

| Command | Class | Function |
|---|---|---|
| `0x7D` | Reset | Reset the DMA to its initial state |
| `0xC3` | Load + Enable | Load the source/dest/length from the WR registers, then start the transfer |
| `0xCF` | Reset + Load | Combined reset + load (common initialization) |
| `0xAB` | Enable interrupt on completion | DMA will fire INT when transfer completes |
| `0xAF` | Disable interrupt | (default) |
| `0x83` | Disable DMA | Stop the DMA, release the bus |
| `0x87` | Enable DMA | Start the DMA (after loading) |
| `0xB3` | Read status | Read the DMA's status byte from `#7B` |

The WR0–WR6 registers hold the actual source address, destination address, transfer length, and operating mode. They are written via additional command bytes after the initial class byte — see the [Z80 DMA datasheet](https://www.zilog.com/docs/z80/ps0179.pdf) for the full bit layout.

---

## A Minimal DMA Memory-to-Memory Transfer

The simplest DMA use case: copy N bytes from one RAM region to another. The configuration sequence:

```z80
; =====================================================================
; dma_copy: Copy BC bytes from HL to DE using the Next DMA
; Input: HL = source, DE = destination, BC = byte count
; =====================================================================
dma_copy:
        ; 1. Reset the DMA
        ld  a, #C3              ; RESET command (bit 7 = 1)
        ; (Simplified — actual sequence writes to #6B)
        ; 2. Configure WR0: source address + length + transfer direction
        ; 3. Configure WR1: source is memory, incrementing
        ; 4. Configure WR2: destination is memory, incrementing
        ; 5. Configure WR4: destination address
        ; 6. Load + enable: transfer starts
        ret
```

The actual sequence is verbose — typically 12–20 byte writes to `#6B` for a one-shot transfer. To avoid this verbosity, the Next community provides two helpers:

### NextBASIC `#DMA` Command

```basic
#DMA SOURCE 16384
#DMA DEST 49152
#DMA LEN 16384
#DMA RUN
```

This configures and starts the transfer in 4 lines of BASIC. The CPU is free to run other code immediately after `#DMA RUN` — the DMA performs the copy in parallel.

### Assembly Helper Library

Most assembly programs define a `dma_setup` subroutine that takes source, dest, length in registers and writes the full command sequence. The `z88dk` and `sjasmplus` standard libraries include such helpers — see [z88dk DMA examples](https://github.com/z88dk/z88dk) for reference code.

---

## Transfer Modes

The DMA has three operating modes, selected via the WR0 command bits:

### Byte Mode

The DMA transfers **one byte per bus cycle**, interleaving with the CPU. The CPU continues executing (slowly — every cycle is a DMA cycle, then a CPU cycle, then DMA, etc.). Byte mode is useful for transferring data while keeping the CPU responsive (e.g., during a game's main loop).

### Burst Mode

The DMA transfers bytes **as fast as the source/dest can accept them** — typically continuously until either side signals "not ready" (via WAIT). The CPU is mostly halted. Burst mode is the default for memory-to-memory transfers.

### Continuous Mode

The DMA **locks the bus** for the entire transfer — the CPU is fully halted from the start of the transfer to the end. This is the fastest mode but blocks all CPU work, including interrupt handling. Use only for short transfers where latency is acceptable.

> [!WARNING]
> Continuous-mode DMA blocks CPU interrupts. If an INT is pending (e.g., the frame interrupt), it will be delayed until the DMA completes. For long transfers (>1 ms), this can cause the program to miss a frame — use burst mode instead, which allows interrupts between bursts.

---

## Pattern Matching — Search Mode

The DMA can be configured to **stop on a byte match** rather than transferring a fixed count. In search mode:

1. The DMA reads each source byte but does **not** write it.
2. After each read, it compares the byte to a match value.
3. When the byte matches, the DMA stops and (optionally) fires an interrupt.

This is useful for:

- **String search** — find the first occurrence of a byte in a buffer (e.g., locate a null terminator)
- **Pattern detection** — scan video memory for a specific pixel value
- **Streaming protocols** — read from a port until a sentinel byte arrives

The match mask and match value are configured via WR5/WR6 commands.

---

## Memory-to-I/O and I/O-to-I/O

The DMA's source and destination types are independent — any combination works:

| Source | Destination | Use case |
|---|---|---|
| Memory | Memory | Block copy, screen clear, snapshot save |
| Memory | I/O port | Upload 16 KB to Layer 2 framebuffer, stream sample data to a DAC |
| I/O port | Memory | Read 512 bytes from IDE controller into RAM |
| I/O port | I/O port | Bridge data from SD card to UART (e.g., file streaming to WiFi) |

The "fixed address" mode (no increment) is essential for I/O port operations — the destination port stays at the same address (e.g., `#55` for sprite upload) while the source memory increments through the pattern data.

### Example — DMA-Driven Sample Playback

A common use case: drive 8-bit PCM samples to a DAC at a fixed rate. The DMA reads from a sample buffer in RAM and writes to the DAC port (`#1F` when Covox/SpecDrum is enabled). The copper or a timer triggers a new DMA burst every scanline (64 μs), giving an ~15.6 kHz sample rate.

```z80
; Per-scanline DMA burst: send 320 bytes of sample to DAC
play_sample_burst:
        ; Configure DMA: source = sample buffer, dest = #1F, count = 320, fixed dest
        ; (DMA setup is one-time at startup; this just retriggers)
        ld  a, #C3              ; LOAD + ENABLE
        ld  bc, #6B
        out (c), a
        ret
```

The copper fires this routine every scanline. The result: 320 samples per scanline × 311 scanlines per frame × 50 Hz = ~15.6 kHz sample rate — better than telephone-quality audio, with zero ongoing CPU cost beyond the per-scanline retrigger.

---

## DMA NextRegs and Ports Summary

| Reg / Port | Name | Function |
|---|---|---|
| Port `#6B` | DMA command | Write command bytes (reset, load, enable, etc.) |
| Port `#7B` | DMA data | Write/read register values |
| NextReg `0x0B` | DMA enable | Bit 0 = enable DMA peripheral globally |
| NextReg (varies) | DMA configuration | Some firmware revisions expose DMA via NextRegs |

---

## DMA vs LDIR vs Copper

| Criterion | `LDIR` (CPU) | DMA | Copper |
|---|---|---|---|
| **Source/dest** | Memory only | Memory + I/O | NextRegs only |
| **Transfer length** | Up to 64 KB | Up to 64 KB | Single byte per instruction |
| **CPU cost** | 100% (21 T/byte) | ~0% (DMA steals cycles but no instruction fetch) | 0% |
| **Pattern match** | No | Yes | No |
| **Interrupt on completion** | No | Yes | No |
| **I/O port destination** | Yes (via `OUTI` etc.) | Yes (more efficiently) | Yes (NextReg writes only) |

**Guideline**: Use `LDIR` for short transfers (<256 bytes) where DMA setup overhead exceeds the transfer cost. Use **DMA** for bulk data movement (16 KB+), pattern fills, and I/O streaming. Use **copper** for raster-synchronized register writes.

---

## Cross-References

- [ZX Spectrum Next](zx_next.md) — platform overview, layer stack
- [Layer 2](zx_next_layer2.md) — DMA is the fastest way to fill Layer 2 framebuffer
- [Sprites](zx_next_sprites.md) — DMA can stream sprite pattern data
- [Tilemap](zx_next_tilemap.md) — DMA can upload tilemap data in bulk
- [Copper](zx_next_copper.md) — alternative data mover, raster-synchronized
- [Next memory map and I/O ports](../../05_development/03_memory_and_io/memory_and_io_next.md) — full port decoding
- [Z80 DMA datasheet](https://www.zilog.com/docs/z80/ps0179.pdf) — the original Zilog reference (the Next DMA is a clone)

---

## References

- **Zilog Z80 DMA Technical Manual** (Zilog, 1984) — the canonical Z80 DMA reference, applicable to the Next's DMA clone
- **TBBlue I/O Port System — DMA** ([specnext.com](https://www.specnext.com/tbblue-io-port-system/)) — Next-specific DMA port and NextReg reference
- **NextBASIC `#DMA` commands** — documented in [NextZXOS](../../04_operating_systems/nextzxos.md)
- **sjasmplus DMA examples** ([GitHub](https://github.com/z00m128/sjasmplus)) — sample DMA programs in the `examples/dma_*.asm` files
- **z88dk DMA library** ([GitHub](https://github.com/z88dk/z88dk)) — C-callable DMA helpers for the Next
- **CSpect emulator** — DMA implementation, for development testing
- **"ZX Spectrum Next DMA Programming"** (community tutorials) — practical DMA usage patterns
