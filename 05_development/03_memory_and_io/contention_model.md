[← Home](../../README.md) · [Memory & I/O](README.md)

# Contention Model — Unified Developer Reference

Memory contention is the ZX Spectrum's most important timing constraint. When the ULA (or gate array) reads screen memory to generate the video signal, it **steals bus cycles from the CPU** — making code that accesses shared RAM slower and nondeterministic unless you account for contention explicitly.

Only machines whose video chip and CPU fight for the **same** memory, with the video given priority, have real contention: the Sinclair and Amstrad models, faithful 48K replicas, and (assumed, not yet measured) the Timex SCLD machines. The Next and the ZX-Evo reproduce it on purpose, only in their Sinclair timing modes at 3.5 MHz. The Soviet clones share memory between video and CPU in fixed time slots, so at 3.5 MHz their CPU never waits for screen data — with one twist: the Scorpion ZS-256 delays **opcode fetches from RAM** by one T-state when they would start on an odd T-state ("Even M1").

This article is a **developer-focused reference** that consolidates contention behavior across all models and tracks (Original, Soviet, New Gen). For the Ferranti ULA's fetch cadence in depth, see [ula_timing.md](../../02_hardware/original/ula_timing.md) and [ula_contention.md](../../02_hardware/original/ula_contention.md); for the Z80 bus cycles behind it, see [z80_timing.md](../../01_cpu/z80_timing.md#where-the-cpu-samples-the-bus--fetch-vs-read).

---

## Quick Reference — Per-Model Contention

| Model | Contended range | Contention type | Delay pattern | I/O contended? |
|-------|----------------|-----------------|---------------|----------------|
| **48K** | `#4000`–`#7FFF` (address-based) | Ferranti ULA, clock stretching | 6-5-4-3-2-1-0-0 | Yes (even ports, and any port whose high byte is `#40`–`#7F`) |
| **128K / +2** | Banks 1, 3, 5, 7 (DRAM set B) | Ferranti ULA, clock stretching | 6-5-4-3-2-1-0-0 | Yes (as 48K; high byte checked against the current mapping) |
| **+2A / +3** | Banks 4, 5, 6, 7 (all high) | Amstrad gate array, WAIT | 1-0-7-6-5-4-3-2 | **No** — gate array contends `MREQ` cycles only |
| **Timex TC2048 / TS2068** | `#4000`–`#7FFF` (assumed) | SCLD, assumed ULA-like | 48K-like, own onset — **unverified** | Presumably as 48K |
| **Harlequin** (open 48K replica) | `#4000`–`#7FFF` | Replica of the Ferranti ULA | 6-5-4-3-2-1-0-0 | Yes |
| **Pentagon 128 / 512 / 1024** | **None** | Fixed video/CPU time slots | N/A | No |
| **Scorpion ZS-256** | **None** | Fixed slots; **Even M1**: +0/+1 T on opcode fetches from RAM | N/A | No |
| **Scorpion Turbo+** at 7 MHz | All RAM | Waits for a free slot, more often during the paper | Not measured | No |
| **Profi** | **None** | Discrete slot scheme | N/A | No |
| **ATM Turbo 1 / 2+** | **None** | Discrete interleave | N/A | No (keyboard `IN #FE` waits for the 8031 controller) |
| **Kay-1024** | **None** at 3.5 MHz ("WAIT-free NORMAL mode"); the older Kay-256 had waits | Discrete arbitration | N/A | No; IORQ stretched in turbo |
| **ZX-Evo BaseConf** | None in the Pentagon raster; **emulated** 48K-style contention in the 48K/128K rasters at 3.5 MHz only | FPGA, by rule | 48K pattern | Even ports, same condition |
| **ZX-Evo TS-Conf** | **None** | FPGA DRAM arbiter | N/A | No |
| **ZX Spectrum Next** | **Emulated** in 48K/128K/+3 timing at 3.5 MHz only; off in Pentagon timing and in any turbo | FPGA, by rule | Per emulated model | 48K/128K timing yes; +3 timing no |

> **Key insight for cross-platform code**: If your code works perfectly on a Pentagon but breaks on a 48K, contention is the most likely culprit. If it works on a 48K but breaks on a +2A/+3, the different contention pattern is the cause.

> [!WARNING]
> **Requires contended memory timing.** Every T-state count in this article is the Z80's base cost plus the delay the machine inserts. On the Sinclair/Amstrad models the ULA or gate array stalls the CPU during specific cycles of the paper area; on the Scorpion, opcode fetches from RAM are aligned to even T-states. Naive timing calculations from the Z80 tables alone will be wrong on those machines.

---

## Why Memory Slows the CPU — Shared DRAM Slots and Who Waits

A memory chip serves one reader at a time. Every Spectrum stores the screen in the same DRAM the CPU uses, so every design must decide **who waits when both want the memory**. The answer, not the CPU, is what makes a machine contended or not.

| Design | Who waits | Machines | Result for the CPU |
|---|---|---|---|
| **Video has priority; the video chip stops the CPU clock** | CPU | Ferranti ULA: 16K/48K/128K/+2; Harlequin | Contention. The ULA looks only at the address lines and `MREQ`/`IORQ`, so internal cycles that leave a contended address on the bus stop too, and so do I/O cycles |
| **Video has priority; the video chip pulls WAIT** | CPU | Amstrad gate array: +2A/+3 | Contention of `MREQ` cycles only — no I/O contention, no internal-cycle contention |
| **Fixed time slots** — the memory runs faster than the CPU needs, and a counter hands out alternating video and CPU slots | Nobody, if the CPU's slot is always there when the Z80 latches data | Pentagon, Scorpion, Profi, ATM Turbo, Kay-1024 | No contention at 3.5 MHz. The price is exact phase — which is where the Scorpion's Even M1 comes from |
| **FPGA with bandwidth to spare** | Nobody, unless a rule says so | ZX-Evo, Next, Karabas-Pro | Contention only where deliberately emulated (Sinclair timing modes at 3.5 MHz); waits at high turbo clocks |

### ROM and RAM Are Different Kinds of Memory

**ROM** (an EPROM such as the 27256/27512) is an asynchronous, non-multiplexed chip that only the CPU uses — the video circuit never reads it. The CPU puts out the address and `RD`; after the chip's access time (hundreds of nanoseconds) the data is stable for as long as the address is held. There are no slots, phases or strobes, so any T-state works.

**RAM** in these machines is dynamic (DRAM), and it is shared with the video circuit: the screen lives in the same DRAM chips. On a slot-based clone a counter clocked from 7 MHz (or 14 MHz) divides time into slots: in one phase `RAS`/`CAS` are issued for the CPU, in the other for the video. DRAM data therefore appears only **inside the CPU's slot, at one fixed phase of the clock**.

### Why the Scorpion Delays Only Opcode Fetches

The Z80 latches the data bus at different moments in different cycles (Zilog UM0080 timing diagrams; details in [z80_timing.md](../../01_cpu/z80_timing.md#where-the-cpu-samples-the-bus--fetch-vs-read)):

```
                  T1        T2        T3        T4
CLK               /‾‾‾‾\____/‾‾‾‾\____/‾‾‾‾\____/‾‾‾‾\____

M1 fetch  RD      ‾‾‾‾‾\______________/‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾   opcode latched on T3 rising edge
          MREQ    ‾‾‾‾‾\______________/‾‾‾‾\_________/‾‾‾‾   second low = refresh
          RFSH    ‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾\___________________/

Read      RD,MREQ ‾‾‾‾‾\___________________/‾‾‾‾‾‾‾‾‾‾‾‾‾‾   data latched on T3 falling edge
```

- An ordinary **memory read** holds `MREQ` and `RD` from the falling edge of T1 to the falling edge of T3 and latches the data on the falling edge of T3. That window is long enough to contain the CPU's DRAM slot whatever the parity of the T-state on which the cycle started.
- An **opcode fetch (M1)** is shorter: the opcode is latched on the rising edge of T3, half a clock earlier, and from that edge the CPU already drives the refresh address. The slot covers that window at only one parity.

So the Scorpion's logic checks "M1, RAM selected, wrong phase" and inserts one WAIT. Data reads, writes, I/O, interrupt acknowledge and fetches from ROM never match that condition. The net effect: **every opcode fetch from RAM starts on an even T-state**, at a cost of 0 or 1 T.

> [!NOTE]
> **Confidence.** *Who* waits and who does not is confirmed by the Scorpion's EPLD equations (SC15.1, the 1996 turbo board firmware) and by programmers' experience on real machines — medium-high confidence. *Why exactly M1* is a reading of those equations against the Z80 bus timing, not something any Scorpion document states — low confidence. See [scorpion.md](../../02_hardware/clones/scorpion.md#contention-and-the-even-m1-wait) for the equations and sources.

---

## When Contention Happens

Contention only occurs **during the paper (display) area** — the 192 scanlines where the ULA fetches pixel and attribute bytes. During border lines and vertical blank, the ULA does not access screen RAM and **there is no contention**.

```
Frame layout (48K):

  Top border    64 lines     → No contention (ULA idle)
  Paper area   192 lines     → CONTENTION ACTIVE
  Bottom border 56 lines     → No contention (ULA idle)
  VBlank        included     → No contention (ULA idle)
```

### T-state windows

Within each paper scanline, contention follows a repeating cycle:

**Ferranti ULA (48K, 128K, +2):**

| T-state offset | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 |
|---|---|---|---|---|---|---|---|---|
| Delay | **6** | **5** | **4** | **3** | **2** | **1** | 0 | 0 |

The first 6 T-states of each 8-T-state window have contention; the last 2 are free. The window repeats 16 times per scanline (128T contention window + 96T free).

**Amstrad gate array (+2A, +3):**

| T-state offset | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 |
|---|---|---|---|---|---|---|---|---|
| Delay | 1 | 0 | **7** | **6** | **5** | **4** | **3** | **2** |

The peak delay (7T) is at offset 2 — the pattern is shifted and inverted compared to Ferranti.

---

## What Gets Contended

### Memory Access

| Access type | Contended? | Notes |
|---|---|---|
| Opcode fetch from contended range | **Yes** | The M1 cycle is delayed |
| Memory read from contended range | **Yes** | Any read operation |
| Memory write to contended range | **Yes** | Any write operation |
| Internal cycle (no `MREQ`) with a contended address on the bus | **Ferranti ULA: yes**; gate array: no | E.g. the extra T-states of `INC HL` or `LD A,(IX+d)` are contended "by address" on 48K/128K |
| Access to ROM (`#0000`–`#3FFF`) | No | ROM is not shared |
| Access to uncontended RAM (48K: `#8000`+) | No | Separate physical RAM |

### I/O Port Access

| Port type | Contended? | Notes |
|---|---|---|
| `#FE` (ULA) and any A0=0 port | **Yes** (Ferranti ULA) | Same contention pattern as memory |
| Odd port (A0=1) with high byte `#40`–`#7F` (48K) or in a contended page (128K) | **Yes** (Ferranti ULA) | The address alone triggers the ULA — four 1-T contention points |
| `#FE` (ULA) on +2A/+3 | **No** | Gate array only contends MREQ |
| `#7FFD` (128K paging) | **Yes** (Ferranti ULA) | Port with A0=0 → contended |
| `#BFFD` / `#FFFD` (AY) | **Yes** (Ferranti ULA) | Port with A0=0 → contended |
| Kempston `#1F` | **No** (as `IN A,(#1F)` with A < `#40`) | A0=1; contended only if the high byte falls in the contended range |

> [!IMPORTANT]
> On the Ferranti ULA, **any port with A0=0** (the ULA port `#FE`, plus 32,767 other aliased addresses) triggers contention during the paper area. This includes `#7FFD` and AY ports — paging the RAM bank or writing to the AY during the display area costs extra T-states. The four I/O patterns (N = uncontended T, C = contended T) are:
>
> | High byte in contended range? | A0 = 0 (ULA port)? | Pattern |
> |---|---|---|
> | No | No | N:4 |
> | No | Yes | N:1, C:3 |
> | Yes | No | C:1, C:1, C:1, C:1 |
> | Yes | Yes | C:1, C:3 |
>
> Source: [sinclair.wiki — Contended I/O](https://sinclair.wiki.zxnet.co.uk/wiki/Contended_I/O).

---

## Per-Model Details

### 48K — Address-Based Contention

The simplest model: addresses `#4000`–`#7FFF` are contended. Everything else is not.

```
Contended:    #4000 - #7FFF   (upper 16K — screen + attributes + system vars)
Uncontended:  #0000 - #3FFF   (ROM)
Uncontended:  #8000 - #FFFF   (lower 32K RAM)
```

The contention pattern is 6-5-4-3-2-1-0-0 during the 128T contention window per scanline. **Pattern starts at T=14,335** (the last T-state of top border, with the ULA prefetching the first paper byte) and repeats every **224 T-states** (one scanline). The closely-related value T=14,336 is the first T-state of scanline 64 (paper display proper) — both values appear in the literature depending on whether one is describing the first delayable access or the first paper pixel. See [contention_timing.md](../05_display_and_timing/contention_timing.md#first-paper-scanline--t-state-by-t-state-ferranti) for the per-T-state delay progression table.

### 128K / +2 — Bank-Based Contention

Contention is determined by **which physical DRAM chip set** the address lives in, not the CPU address directly:

```
DRAM set A (uncontended):  Banks 0, 2, 4, 6 (even banks)
DRAM set B (contended):    Banks 1, 3, 5, 7 (odd banks)
```

- RAM at `#4000`–`#7FFF` is **always contended** because bank 5 (set B) is permanently mapped there as the default screen.
- RAM at `#C000`–`#FFFF` is **conditionally contended** — contended if and only if an odd bank (1, 3, 5, or 7) is paged into that range via `#7FFD`. Page in bank 0, 2, 4, or 6 and code at `#C000` runs at full speed even during the paper area.

The delay **pattern** is the same 6-5-4-3-2-1-0-0 as the 48K, but the **timing differs**: pattern starts at **T=14,361** (not T=14,335) and repeats every **228 T-states** (not 224) because the 128K/+2 scanline is 228T long. Source: [WoS 128K FAQ](https://worldofspectrum.org/faq/reference/128kreference.htm).

### +2A / +3 — Gate Array Contention

The Amstrad gate array (ASIC 40084 in the +2A/+3, 40085 in the +2B/+3B) uses a completely different contention model from the Ferranti ULA:

- **Different contended banks**: 4, 5, 6, 7 (not 1, 3, 5, 7 as on the 128K/+2). Banks 0–3 are never contended regardless of where they're paged.
- **Different delay pattern**: 1-0-7-6-5-4-3-2 (shifted and inverted relative to Ferranti 6-5-4-3-2-1-0-0). Peak delay is **7T** (one worse than Ferranti's 6T) at slot offset 2.
- **MREQ gating**: The gate array applies contention **only when the Z80's `MREQ` line is active** (i.e., a real memory access). I/O port accesses activate `IORQ` instead, leaving `MREQ` inactive, so I/O is **never contended** regardless of port address. This is the underlying reason `OUT (#FE),A`, `OUT (#7FFD),A`, and `OUT (#BFFD),A` all run at full speed during the paper area on +2A/+3.
- **No internal-cycle contention**: for the same reason (`MREQ` gating), the internal T-states of instructions such as `INC HL` or `EX (SP),HL` are never delayed, even with a contended address on the bus.
- **129 T window per line**: photos of Rak's Timing Test on a real +3 (2023) and a real +2A (2025) show that the contended window of each line is 129 T, not 128 — one more T at the end than most emulators model (Fuse, MAME, ZXMAK2, Xpeccy reuse the Ferranti ULA's 128 T).
- **No early/late timing**: The gate array is a single stable ASIC and does not exhibit the thermal drift / ULA-revision variance of the Ferranti chips (5C/6C/7C/8C).
- **Pattern starts at T=14,361** (not T=14,335 as on 48K), repeating every 228 T-states (not 224). For the full per-T-state delay progression table, see [contention_timing.md](../05_display_and_timing/contention_timing.md#first-paper-scanline--t-state-by-t-state-amstrad-gate-array).

> [!WARNING]
> Code that relies on the exact Ferranti contention pattern (6-5-4-3-2-1-0-0) for timing will break on the +2A/+3. The peak delay is 7T instead of 6T, and it occurs at a different T-state offset (slot offset 2 vs slot offset 0).

### Pentagon — No Contention

The Pentagon has **zero memory contention**. There is no ULA: the CPU and the video logic read the same DRAM in fixed slots derived from the 14 MHz master clock (CPU at 14/4 MHz), and the CPU's slot is always there when it needs it — no WAIT, no clock stretching, no M1 alignment. The designer-era Pentagon FAQ puts it as "128k of NOT-CONTENDED memory (no slow areas)". A document describing the exact slot order has not been found; the "no contention" part is not in doubt. The Pentagon 512/1024SL add a 7 MHz turbo; no turbo wait is documented.

This means:
- Multicolor effects that depend on contention delays **will not work** without adaptation
- Code in the screen area runs measurably faster than on 48K/128K
- Floating bus behavior is absent or different

### Scorpion ZS-256 — No Contention, but Even M1

The Scorpion shares its DRAM between CPU and video in fixed slots, like the Pentagon, and has **no memory contention and no I/O contention** on any board. What it has instead is a one-T-state WAIT on **opcode fetches (M1) from RAM** that would start on an odd T-state, so that every fetch from RAM starts on an even T-state (see [Why the Scorpion Delays Only Opcode Fetches](#why-the-scorpion-delays-only-opcode-fetches)):

| Access | Waits? |
|---|---|
| Opcode fetch (M1, including `CB`/`DD`/`ED`/`FD` prefixes) from RAM, starting on an odd T | **+1 T** |
| Opcode fetch from RAM starting on an even T | No |
| Opcode fetch from ROM | No |
| RAM mapped at `#0000` (`#1FFD` bit 0) | Counts as RAM — the logic looks at the RAM select, not the address |
| Data read, data write, I/O, interrupt acknowledge | No |
| 7 MHz turbo (Turbo+ / green board) | Per the equations, Even M1 gives way to slot waits: every RAM access waits for a free slot, more often during the paper (medium confidence, no measurement found) |

Because every fetch in RAM starts on an even T-state, the rule for code running in RAM at 3.5 MHz reduces to: **each instruction costs its Pentagon length rounded up to the next even number.** A prefixed instruction does not pay twice: the prefix fetch is 4 T, so the second fetch is already even.

| Instruction (code in RAM) | Pentagon | Scorpion |
|---|--:|--:|
| `NOP` | 4 | 4 |
| `LD A,n` | 7 | 8 |
| `INC HL` | 6 | 6 |
| `LD A,(IX+d)` | 19 | 20 |
| `OUT (n),A` | 11 | 12 |
| `DJNZ e` (taken / not taken) | 13 / 8 | 14 / 8 |
| `LDIR` (per repeated byte / last byte) | 21 / 16 | 22 / 16 |

The same code in ROM — for example a routine in the 48 BASIC ROM — runs at Pentagon speed. Full details, board-by-board status and emulator support: [scorpion.md](../../02_hardware/clones/scorpion.md#contention-and-the-even-m1-wait).

### Other Clones and FPGA Machines

| Machine | CPU delays |
|---|---|
| **Profi** | None known at 3.5 MHz |
| **Karabas-Pro** (FPGA Profi) | Contention only in its optional "classic" screen mode at 3.5 MHz (`#4000`–`#7FFF` and even ports, clock gated); ~400 ns wait on every `MREQ` cycle at 14 MHz |
| **ATM Turbo 2+** | None on memory; `IN A,(#FE)` holds WAIT until the 8031 keyboard controller answers |
| **Kay-1024** | None at 3.5 MHz; in turbo IORQ is stretched and RAM runs at an effective 6.3–7.0 MHz |
| **ZX-Evo BaseConf** | Emulated 48K-style contention in the 48K/128K rasters at 3.5 MHz only; at 14 MHz variable waits per access (M1 and reads, not writes); WAIT on the AVR-serviced ports |
| **ZX-Evo TS-Conf** | None at 3.5/7 MHz unless video + DMA use the whole DRAM bandwidth; at 14 MHz a wait on each cache miss |
| **Sprinter** | At 21 MHz, accesses to the main DRAM wait; none from the 64K fast RAM |
| **ZX Spectrum Next** | Emulated contention in 48K/128K/+3 timing at 3.5 MHz; at 28 MHz one wait on every memory read |

See [clone_timing.md](../../02_hardware/clones/clone_timing.md) for the per-clone details and sources.

---

## Practical Impact on Code

### Instruction Timing Variance

The same instruction can take different amounts of time depending on where it executes and when:

```z80
; LD (HL),A — base cost 7T, but in contended memory during paper area:
; T-state offset 0:  7 + 6 = 13T (worst case)
; T-state offset 6:  7 + 0 =  7T (no contention)
; During border:      7T (never contended)
```

For cycle-exact multicolor effects, you must know your **exact T-state position** within the scanline and account for each instruction's contended cost.

### Worst-Case vs Best-Case Code

```z80
; Code in uncontended RAM (#8000+) accessing contended screen:
LD   HL,#4000       ; HL = contended address
LD   (HL),A         ; 7T base + 0-6T contention on the write cycle
                     ; Opcode fetch is uncontended (PC in #8000+)
                     ; Only the (HL) write is contended

; Code IN contended RAM (#4000+) accessing contended screen:
; BOTH the opcode fetch AND the memory access are contended
; Worst case: 4T fetch + 6T + 3T write + 6T = 19T for LD (HL),A
```

### Contentious Code Pattern — What to Avoid

```z80
; BAD: Tight loop in contended memory during paper area
; Timing is unpredictable due to contention variance
.loop:
    LD   (HL),A       ; 7T + 0-6T contention
    INC  HL            ; 6T + 0-6T contention
    DJNZ .loop         ; 8/13T + 0-6T contention
    ; Total per iteration: 21-31T (47% variance!)
```

### Uncontended Code Pattern — Reliable Timing

```z80
; GOOD: Code in uncontended RAM, data access to contended memory
; Only memory operations are contended — opcode fetch is free
    ; Assume this code is at #8000+ (uncontended)
    LD   HL,#4000       ; 10T — no contention
.wait:
    IN   A,(#FE)        ; 11T base — but I/O IS contended on Ferranti!
    ; Better: use HALT + precise delay for timing
```

### Scorpion — Programming Around Even M1

The Scorpion never slows down because of the screen at 3.5 MHz, so most Pentagon code runs on it unchanged. Code that counts T-states exactly is different:

- **Odd-length instructions in RAM are rounded up.** A loop that takes 17 T on a Pentagon takes 18 T on a Scorpion when it runs from RAM. Cycle-exact multicolor and border engines tuned on a Pentagon drift by one T-state per odd instruction.
- **Exit from `HALT` is always on an even T-state.** introspec, on a Pentagon timing test that failed on a Scorpion: "on a Scorpion the T-state is always even on exit from HALT" ([zx-pk.ru, "Тайминги Pentagon 128", post #25](https://zx-pk.ru/threads/21212-tajmingi-pentagon-128/page3.html)). A `HALT`-synchronized effect that needs an odd starting phase cannot get it.
- **There is no 1-T delay step in RAM.** Timing-test programs that measure code by sliding it through delays of every length — the `CODETIME` engine of Rak's Timing Test, or the unreal-ng emulator's `ctprobe` contention probe built on it — cannot work on a Scorpion, because every odd delay rounds up to the next even one.
- **Code in ROM is not affected.** A fetch from ROM never waits, so ROM routines keep their Pentagon timings.

```z80
; Even M1 on the Scorpion ZS-256: the same code in RAM, timed on two machines.
; Comment columns: T-states on a Pentagon / on a Scorpion
; (code in RAM at 3.5 MHz; in RAM every Scorpion fetch starts on an even T).
; Scorpion rule: an instruction fetched from RAM costs its Pentagon length
; rounded up to the next even number.

        DEVICE ZXSPECTRUM128
        ORG  #8000

; Fill one 32-byte pixel row at #4000 with #FF.
FillRow:
        LD   HL,#4000         ; 10 / 10
        LD   B,32             ;  7 /  8   odd: the next fetch waits 1 T
.loop:
        LD   (HL),#FF         ; 10 / 10
        INC  L                ;  4 /  4
        DJNZ .loop            ; 13 / 14   taken (last pass: 8 / 8)
        RET                   ; 10 / 10
; Total: Pentagon 17 + 31*27 + 22 + 10 = 886 T
;        Scorpion 18 + 31*28 + 22 + 10 = 918 T

; Two padding routines one T-state apart on a Pentagon...
Pad16:
        INC  HL               ;  6 /  6
        RET                   ; 10 / 10   -> 16 / 16
Pad17:
        LD   A,(HL)           ;  7 /  8
        RET                   ; 10 / 10   -> 17 / 18
; ...are two T-states apart on a Scorpion: in RAM there is no 1-T step.
```

> [!WARNING]
> **Requires contended memory timing** — here, the Scorpion's fetch alignment. The Scorpion column assumes the code runs from RAM at 3.5 MHz; at 7 MHz the Turbo+ slot waits apply instead, and the same code placed in ROM runs at the Pentagon column's speed.

When exact T-state counts matter, detect the Scorpion (see [scorpion.md](../../02_hardware/clones/scorpion.md#detection-techniques)) and either use even-length instruction sequences in the timed path or accept a 2-T resolution on that machine.

---

## Cross-Platform Strategy

### Detect the Machine

```z80
; Simplified detection (see clone_timing.md for full method)
DetectMachine:
    LD   BC,#7FFD
    LD   A,#80
    OUT  (C),A           ; Try 128K paging
    IN   A,(#FF)          ; Check if paging worked
    CP   #80
    JR   Z,.is128K

    ; Could be 48K or clone
    ; Check for Pentagon by timing a frame
    HALT
    LD   BC,0
.delay:
    DEC  BC
    LD   A,B
    OR   C
    JR   NZ,.delay
    ; If BC > 0 after one frame → Pentagon (longer frame)
    ; Exact threshold depends on HALT latency
    RET

.is128K:
    ; Further checks for +2A/+3 vs plain 128K
    RET
```

### Contention Guard Macros

```z80
; For cross-platform code, use conditional assembly:

IF CONTESTED_PLATFORM
    ; 48K/128K: account for contention in T-state budgets
    ; Add NOP padding where contention would steal cycles
ELSE
    ; Pentagon/clone: exact timing, no contention compensation
ENDIF
```

---

## Contention Quick-Reference Card

```
┌──────────────────────────────────────────────────────┐
│              IS MY ACCESS CONTENDED?                 │
├──────────────────────────────────────────────────────┤
│                                                      │
│  48K: Address in #4000-#7FFF AND during paper?  YES  │
│  128K: Address in odd bank AND during paper?    YES  │
│  +2A/+3: Address in bank 4-7 AND during paper?  YES  │
│  Pentagon, Profi, ATM, Kay-1024: any access?    NO   │
│  Scorpion: never contended, but an opcode fetch      │
│    from RAM on an odd T waits 1 T (Even M1)          │
│                                                      │
│  During border/VBlank on any model?             NO   │
│  ROM access on any model?                       NO   │
│  I/O on +2A/+3?                                 NO   │
│                                                      │
├──────────────────────────────────────────────────────┤
│  Maximum delay: 6T (Ferranti) or 7T (gate array)     │
│  Pattern repeats every 8T during paper scanlines     │
└──────────────────────────────────────────────────────┘
```

---

## Cross-References

- **ULA timing deep dive** (hardware mechanism, contention patterns): [ula_timing.md](../../02_hardware/original/ula_timing.md)
- **Clone timing** (per-clone contention behavior): [clone_timing.md](../../02_hardware/clones/clone_timing.md)
- **48K memory and ports** (contended address ranges): [memory_and_io_48k.md](memory_and_io_48k.md)
- **128K memory and ports** (bank-based contention): [memory_and_io_128k.md](memory_and_io_128k.md)
- **+2A/+3 memory and ports** (gate array contention): [memory_and_io_plus3.md](memory_and_io_plus3.md)
- **48K video frame** (contention windows per scanline): [video_frame_48k.md](../05_display_and_timing/video_frame_48k.md)
- **Z80 timing** (per-instruction T-state costs, when the CPU latches the bus in fetch and read cycles): [z80_timing.md](../../01_cpu/z80_timing.md)
- **Scorpion ZS-256** (Even M1 equations, boards, emulator support): [scorpion.md](../../02_hardware/clones/scorpion.md#contention-and-the-even-m1-wait)
- **Pentagon** (no contention): [pentagon.md](../../02_hardware/clones/pentagon.md)
- **Complete I/O port map** (which ports are contended per model): [io_port_map.md](../../10_references/io_port_map.md)

---

## References

### External references

- [Chris Smith — *The ZX Spectrum ULA: How to Design a Microcomputer* (2010)](http://www.zxdesign.info/) — the definitive reference for the Ferranti ULA's bus-arbitration mechanism that causes contention on the 48K. Documents the exact T-state windows during which the ULA steals cycles from the CPU for video refresh.
- [Sinclair ZX Specifications (Martin Korth)](http://problemkaputt.de/zxdocs.htm) — canonical hardware reference covering the gate-array variants in the 128K / +2 / +2A / +3 and how their contention patterns differ from the 48K Ferranti ULA.
- [World of Spectrum — Contended Memory FAQ](https://worldofspectrum.org/faq/reference/rampages.htm) — community-verified contention tables and timing diagrams for every Sinclair model.
- [zx-pk.ru — contention and clone timing subforum](https://zx-pk.ru/) — primary source for Soviet-clone timing differences (the Pentagon, Profi, ATM Turbo and Kay-1024 have no contention at 3.5 MHz; the Scorpion has Even M1).
- [zx-pk.ru — "Scorpion ZS-256 turbo (схема)", post #40](https://zx-pk.ru/threads/940-scorpion-zs-256-turbo-(skhema)/page4.html) — the Scorpion's SC15.1 turbo-board EPLD equations (ZS Company, 1996), the primary source for Even M1 and the turbo slot waits.
- [zx-pk.ru — ScorpEvo thread, post #86](https://zx-pk.ru/threads/13345-scorpevo-(scorpion-zs-na-baze-zx-evolution)/page9.html) — an independent reading of the yellow board's schematic: "a RAM access with M1 low gets a one-clock wait".
- [sinclair.wiki — Contended memory](https://sinclair.wiki.zxnet.co.uk/wiki/Contended_memory) and [Contended I/O](https://sinclair.wiki.zxnet.co.uk/wiki/Contended_I/O) — the Ferranti ULA and gate array patterns, including I/O.
- Pentagon FAQ ([zxspectrum.hal.varese.it](http://zxspectrum.hal.varese.it/static/documenti/pentagon.txt)) — "128k of NOT-CONTENDED memory (no slow areas)".
- [Zilog Z80 CPU User Manual (PDF)](https://www.zilog.com/docs/z80/um0080.pdf) — official Z80 timing diagrams; required reading for understanding T-state budgets that contention consumes.
