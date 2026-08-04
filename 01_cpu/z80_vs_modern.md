[← Plan](../PLAN.md) · [Z80 CPU](README.md)

# Z80 vs. Modern CPUs — Architecture, Programming Model, and Mindset Differences

The Z80 is a **microcoded, single-issue, in-order, deterministic** processor from 1976. Modern CPUs (x86-64, ARM Cortex, RISC-V) are **superscalar, out-of-order, speculative, pipelined** machines with caches, branch predictors, and multi-gigahertz clock speeds. The gap between them is not just one of speed — it is a fundamental difference in **programming model**. On the Z80, every instruction takes a known number of clock cycles, every memory access is visible, and the programmer is the scheduler. On a modern CPU, hardware decides what runs when, memory accesses are cached and reordered, and timing is statistical.

This article is the bridge for developers coming from modern platforms. It maps Z80 concepts to their modern equivalents, highlights what's **gone**, what's **new**, and what's **surprisingly similar**. Understanding these differences is essential for writing correct Z80 code and for building accurate emulators.

> [!NOTE]
> This article synthesizes concepts from the other seven CPU articles. References link to the relevant deep-dive articles throughout.

---

## The Big Picture

### Z80 in One Table

| Property | Z80 | Modern CPU (x86-64 / ARM) | Scale |
|----------|-----|---------------------------|-------|
| Year introduced | 1976 | 2003 (AMD64) / 2011 (ARMv8) | 27–35 years later |
| Process technology | 3–4 µm NMOS | 7–3 nm FinFET | ~500–1,000× smaller features |
| Transistors | ~8,500 | ~4–50 billion | ~500,000–6,000,000× |
| Clock speed | 3.5 MHz (ZX Spectrum) | 2–6 GHz | ~570–1,700× |
| Data bus | 8-bit | 64-bit | 8× wider |
| Address bus | 16-bit | 48–64 bit (virtual: 57 bit on x86-64) | 3–4× wider (physical) |
| Addressable memory | 64 KB | 256 TB (x86-64 virtual) | ~4 billion× |
| General registers | 6 (8-bit) + shadow set | 16 (64-bit GPRs on x86-64), 31 (ARM64) | ~3–5× count, 8× width |
| Cache | None | L1: 32–64 KB, L2: 256 KB–1 MB, L3: 4–64 MB | 0 → megabytes |
| Pipeline | None (single instruction at a time) | 14–19 stages, superscalar | 0 → 19 stages |
| Instruction parallelism | None (single-issue) | 4–8 µops/cycle | 0 → 8× |
| Branch prediction | None | 95%+ accuracy, deep predictors | 0 → near-perfect |
| Virtual memory | None | 4–5 level page tables | 0 → multi-level |
| Memory protection | None | Rings, PLs, MPUs | 0 → multi-ring |
| Interrupt latency | Deterministic (11–19 T-states) | Variable (100+ cycles) | ~10× more cycles, non-deterministic |
| Power consumption | ~0.5W | 15–250W | 30–500× |
| Peak MIPS (estimated) | ~0.875 MIPS | ~50,000 MIPS | ~57,000× |
| Memory bandwidth | 1.75 MB/s (LDIR 21T/byte) | ~50 GB/s (DDR5) | ~28,000× |
| Dhrystone 2.1 | ~0.03 DMIPS | ~15,000–50,000 DMIPS | ~500,000–1,600,000× |

### Speed Comparison

| Metric | Z80 at 3.5 MHz | Modern CPU at 3.5 GHz |
|--------|---------------|----------------------|
| Clock ratio | 1× | **1,000×** |
| `NOP` throughput | 0.875 MIPS | ~4,000 MIPS (superscalar) |
| Memory copy throughput | 166 KB/s (LDIR) | ~50 GB/s (L3 cache) |
| Integer multiply (8×8) | ~100 µs (software loop) | ~0.3 ns (1 cycle hardware multiply) |
| Interrupt response | ~3.1 µs | ~0.03 µs (but less deterministic) |
| Addressable RAM | 64 KB | 128+ TB |

The Z80 is **1,000× slower** by clock, but the effective gap is larger because modern CPUs execute multiple instructions per cycle, have hardware multiply/divide, SIMD units, and caches. A rough estimate: modern CPUs are **10,000–100,000× faster** in real-world throughput.

---

## Architecture Comparison

### Register File

| Z80 | Modern Equivalent | Key Difference |
|-----|-------------------|----------------|
| A (accumulator) | RAX (x86-64) / X0 (ARM64) | Z80: ALU always operates on A; Modern: any GPR |
| BC, DE, HL | RBX, RDX, RSI, etc. | Z80: 3 pairs, HL is "special"; Modern: all GPRs equal |
| IX, IY | Base+displacement addressing via SIB byte | Z80: 2 dedicated index regs; Modern: any register as base |
| SP | RSP (x86-64) / SP (ARM64) | Similar function — stack pointer |
| PC | RIP (x86-64) / PC (ARM64) | Similar — program counter |
| AF' / BC' / DE' / HL' | No equivalent | Z80: instant register swap; Modern: renamed in hardware |
| I, R | No equivalent | Z80: interrupt vector + refresh counter |
| F (flags) | RFLAGS (x86-64) / CPSR (ARM64) | Z80: 6 bits; Modern: many more status bits |

**The shadow register set** (`EX AF,AF'` / `EXX`) is a unique Z80 feature with no modern equivalent. In modern CPUs, register renaming provides vastly more physical registers transparently. On the Z80, the programmer explicitly swaps between two complete register sets — useful for fast interrupt handling (4T vs. 42T for PUSH/POP of four register pairs).

### Memory Model

| Aspect | Z80 | Modern CPU |
|--------|-----|------------|
| Address space | Single flat 64 KB | Separate virtual/physical, multi-level paging |
| Memory protection | None | Rings (x86), privilege levels (ARM), memory protection units |
| Cache | None | Multi-level (L1/L2/L3), cache coherence protocols |
| DMA | No built-in DMA | Built-in DMA engines, IOMMU |
| Bus width | 8-bit data, 16-bit address | 64-bit data, 48+ bit address |
| Byte order | Little-endian | Little-endian (x86, most ARM) |

On the Z80, **every memory access goes directly to RAM** (or ROM) with no cache. The programmer sees the exact latency of every load and store. On a modern CPU, L1 cache has a 4-cycle latency, L2 is ~12 cycles, and main memory is ~200 cycles — but the programmer cannot predict which level will be hit without careful profiling.

### I/O Model

| Aspect | Z80 | Modern CPU |
|--------|-----|------------|
| I/O space | Separate 256-port address space (or 64K with `IN r,(C)`) | Memory-mapped I/O (x86: also port I/O via `IN`/`OUT`) |
| I/O instructions | `IN`, `OUT`, block I/O | Memory loads/stores to MMIO addresses |
| DMA | External only | Integrated DMA controllers |
| Interrupt signaling | Pin-based (INT, NMI) | MSI (Message Signaled Interrupts), APIC |
| Bus sharing | ULA contention on shared RAM | PCIe bus arbitration |

The Z80's separate I/O address space is a concept that survives only in x86's `IN`/`OUT` instructions (for legacy compatibility). ARM and RISC-V use **memory-mapped I/O exclusively** — all device registers are accessed as memory addresses.

---

## Programming Model Comparison

### Instruction Set Philosophy

| Philosophy | Z80 | Modern (x86-64) | Modern (ARM64) |
|------------|-----|-----------------|----------------|
| Design | CISC (Complex) | CISC (decoded to µops) | RISC (Load/Store) |
| Encoding | Variable (1–4 bytes) | Variable (1–15 bytes) | Fixed (4 bytes) |
| Operand model | Accumulator-centric | Two-operand (any register) | Three-operand |
| Memory access | Register+memory ALU ops | Register+memory ALU ops | Load/store only |
| Instruction count | ~698 | ~1,500+ | ~1,000 |
| Multiply | Software only | Hardware (1–3 cycles) | Hardware (1–3 cycles) |
| Divide | Software only | Hardware (~20–80 cycles) | Hardware (~4–20 cycles) |
| Floating point | None | Hardware (SSE/AVX) | Hardware (NEON/SVE) |
| SIMD | None | AVX-512 (512-bit) | SVE (2048-bit scalable) |
| Bit manipulation | BIT/SET/RES (3 instructions × 8 bits × 8 registers = 192 opcodes) | BT/BTS/BTR/BTC | Single-bit instructions |

### The Accumulator-Centric Model

The most jarring difference for modern programmers: **the Z80's ALU is hardwired to the accumulator**. `ADD A,B` adds B to A — there is no `ADD B,C`. Modern architectures allow any register as source and destination:

```z80
; Z80: Swap two bytes in memory (HL) and (DE)
LD   A,(HL)       ; Load first byte into A
LD   B,A          ; Save in B
LD   A,(DE)       ; Load second byte into A
LD   (HL),A       ; Store second byte at (HL)
LD   A,B          ; Get first byte
LD   (DE),A       ; Store at (DE)
; 5 instructions, 30T, 5 bytes
```

```c
// Modern C equivalent (any register can be temp)
uint8_t temp = *hl;
*hl = *de;
*de = temp;
// Compiler uses any available register
```

### Addressing Mode Comparison

| Z80 Mode | Modern Equivalent | Notes |
|----------|-------------------|-------|
| `LD A,(HL)` | `mov al, [rsi]` / `ldr w0, [x1]` | Base register indirect — same concept |
| `LD A,(IX+d)` | `mov al, [rbx+offset]` / `ldr w0, [x1, #offset]` | Base + displacement — same concept |
| `LD A,(nn)` | `mov al, [0x4000]` / `ldr w0, =0x4000` | Absolute address — same concept |
| `LD HL,#nn` | `mov rsi, 0x4000` / `mov x1, #0x4000` | Immediate load — same concept |
| `JR e` | `jmp rel8` / `b offset` | Relative jump — same concept |
| `JP (HL)` | `jmp rsi` / `br x1` | Indirect jump — same concept |
| `RST p` | `int n` (x86) | Software interrupt — similar concept |
| No stack-relative | `[rsp+offset]` / `[sp, #offset]` | Z80 has NO stack-relative addressing! |

> [!WARNING]
> The Z80 has **no stack-relative addressing mode**. You cannot do `LD A,(SP+5)`. To access stack frames, you must `POP` values into registers or copy SP to another register (`LD HL,SP` doesn't exist — use `LD HL,0 / ADD HL,SP`). This makes C-style stack frames expensive on the Z80.

### Missing Features (What Modern Programmers Miss)

| Feature | Modern CPU | Z80 Equivalent | Workaround |
|---------|-----------|----------------|------------|
| Hardware multiply | 1–3 cycle `IMUL`/`MUL` | None | Software multiply loop (100–600 T-states) |
| Hardware divide | 4–80 cycle `IDIV`/`UDIV` | None | Software division (200–1000 T-states) |
| Barrel shifter | 1-cycle multi-bit shift | 1 bit per `SLA`/`SRA` instruction (8T) | Loop or lookup table |
| Cache | L1/L2/L3 | None | Keep hot data in registers |
| Virtual memory | MMU, page tables | None | Bank switching via I/O ports |
| Floating point | FPU, SSE, AVX | None | Software floating point (very slow) |
| Unaligned access | 1–2 cycles (x86) | **Not supported** | Must align 16-bit accesses |
| Conditional move | `CMOVcc` (x86) | None | Use conditional jumps |
| Addressing modes | Dozens | 10 | Many modern patterns require multiple Z80 instructions |

---

## Determinism vs. Speculation

### Z80: Fully Deterministic

Every instruction on the Z80 takes a **fixed, known number of T-states**. There is no cache, no pipeline, no branch prediction, no out-of-order execution. If you count T-states, you know exactly how long your code takes. This is why demoscene effects are possible — the programmer has **total control over timing**.

```
LD A,(HL)   ; Always 7 T-states. Period.
ADD A,B     ; Always 4 T-states. Period.
JR Z,loop   ; Always 12 T-states (taken) or 7 T-states (not taken). Period.
```

### Modern: Statistical Performance

Modern CPUs are **non-deterministic** at the cycle level. The same instruction sequence can take different amounts of time depending on:

- Cache state (hit or miss?)
- Branch prediction (correctly predicted?)
- Pipeline state (data dependencies?)
- Out-of-order execution (what else is in flight?)
- Hyperthreading contention (is the other thread using execution units?)
- Frequency scaling (turbo boost active?)
- OS preemption (context switch?)

```c
// Modern C: timing is unpredictable without careful measurement
int sum = 0;
for (int i = 0; i < 1000; i++) {
    sum += array[i];  // 1 cycle if L1 hit, 200+ cycles if miss
}
// Total time: anywhere from 1000 cycles to 200,000+ cycles
```

### Why This Matters

The ZX Spectrum's **ULA contention** is the one non-deterministic element — code in contended memory takes longer during screen drawing. But even contention is deterministic: the delay depends on the exact T-state position, which the programmer can calculate. On a modern CPU, cache behavior is genuinely unpredictable without hardware counters.

---

## Performance Programming: Then vs. Now

### Z80 Performance Techniques

| Technique | Why | Modern Equivalent |
|-----------|-----|-------------------|
| Minimize memory access | Every byte costs 3T (read) or 3T (write) | Cache-aware data layout |
| Use registers aggressively | 6 registers (+ shadow set) = maximum register pressure | Register allocation (compiler does this) |
| Avoid IX/IY | 19T vs. 7T for (HL) — 2.7× slower | Avoid complex addressing modes? (less relevant with caches) |
| Inline frequently called code | `CALL` costs 17T, `RET` costs 10T | Function inlining (compiler does this) |
| Use `LDIR` for block copies | Hardware loop — 21T/byte | `REP MOVSB` / `memcpy` |
| Self-modifying code | Change immediate operands at runtime | JIT compilation |
| Count T-states | Timing is deterministic | Cycle counting irrelevant (use profilers) |
| Run from ROM/uncontended RAM | Avoid ULA contention | Data placement in cache-friendly layout |

### Modern Performance Techniques That Don't Apply to Z80

| Technique | Why It Doesn't Apply |
|-----------|---------------------|
| Cache line alignment | No cache |
| Branch-free code (CMOV) | No conditional moves — branch prediction doesn't exist to mispredict |
| SIMD vectorization | No SIMD |
| Multi-threading | Single-core processor |
| Prefetching | No cache to prefetch into |
| Lock-free data structures | No other threads to contend with |
| Huge pages | No virtual memory |
| NUMA awareness | One memory bus |

---

## The Z80 in Context: Contemporary Processors

### 1976–1985 Competitive Landscape

| Feature | Z80 (1976) | 6502 (1975) | 6809 (1978) | 8086 (1978) | 68000 (1979) |
|---------|-----------|-------------|-------------|-------------|-------------|
| Clock | 2.5–8 MHz | 1–2 MHz | 1–2 MHz | 5–10 MHz | 4–12 MHz |
| Data width | 8-bit | 8-bit | 8-bit | 16-bit | 16/32-bit |
| Address width | 16-bit | 16-bit | 16-bit | 20-bit | 24-bit |
| Registers | 6 + shadow | 3 (A,X,Y) | 2 (A,B) | 4 (AX,BX,CX,DX) | 8 (D0-D7) |
| Index registers | 2 (IX,IY) | 1 (X or Y) | 1 (X) | 2 (SI,DI) | 8 (A0-A7) |
| Stack | Full stack (any depth) | Hardware stack (256 bytes) | Full stack | Full stack | Full stack |
| Block ops | LDIR/CPIR/etc. | None | None | REP MOVS (186+) | None |
| Bit ops | BIT/SET/RES | None | None | BT/BTS (386+) | None |
| Multiply | None | None | 8×8 hardware | None | 16×16 hardware |
| Interrupt modes | 3 | 1 | 3 | 256 (via PIC) | 256 (autovector) |
| Transistors | ~8,500 | ~3,510 | ~9,000 | ~29,000 | ~68,000 |
| Price (1976) | ~$200 | ~$25 | ~$50 | ~$60 | ~$75 |

### What Made the Z80 Special

1. **Binary compatibility with the 8080** — every CP/M program ran on the Z80 unmodified, giving it instant access to the largest software library of the era
2. **Shadow registers** — instant context switch for ISRs, no other 8-bit CPU had this
3. **Block instructions** — LDIR, CPIR, etc. provided hardware-accelerated memory operations that required loops on every other 8-bit CPU
4. **Bit manipulation** — BIT/SET/RES in hardware; the 6502 and 6809 required AND/OR/XOR combinations
5. **Three interrupt modes** — IM2's vector table was sophisticated for 1976
6. **Dynamic RAM refresh** — built-in refresh counter (R register) eliminated external refresh circuitry, reducing system cost

### What the Z80 Lacked

1. **No hardware multiply/divide** — the 6809 had 8×8 multiply, the 68000 had 16×16
2. **Accumulator bottleneck** — ALU operations always involve A; the 6809 had two accumulators (A,B)
3. **No addressing mode flexibility** — only 10 modes vs. the 6809's rich set
4. **Slow indexed addressing** — IX/IY operations cost 19T vs. 7T for (HL)
5. **No unaligned access** — 16-bit loads must be aligned (the Z80 reads two bytes sequentially, which is fine, but the programmer must be aware of byte order)

---

## Cross-Platform Z80 Family Evolution

| Chip | Year | Clock | Key Extension | Used In |
|------|------|-------|--------------|---------|
| Z80 | 1976 | 2.5–8 MHz | Base ISA | ZX Spectrum, MSX, CPC, Game Boy (LR35902) |
| Z180 / HD64180 | 1985 | 6–10 MHz | MMU, DMA, 2× UART, timers | Embedded, RC2014 |
| Z280 | 1986 | 6–20 MHz | 16-bit extensions, MMU, cache | Rare — Zilog's failed successor |
| eZ80 | 2001 | 50 MHz | 24-bit addressing, pipelined | TI-84+ CE calculators |
| Z80N (Next) | 2017 | 7/14/28 MHz | Extended ISA (MUL, SWAP, etc.) | ZX Spectrum Next |
| Game Boy LR35902 | 1989 | 4.19 MHz | Removed some Z80 ops, added others | Nintendo Game Boy |
| Z8S180 | 2000s | 33 MHz | Low power, static design | Embedded |

### The ZX Spectrum Next's Z80N Extensions

The ZX Spectrum Next extends the Z80 ISA with new instructions via the `ED` prefix:

| Instruction | Operation | Notes |
|-------------|-----------|-------|
| `MUL D,E` | DE = D × E | 8×8 unsigned multiply |
| `SWAPN` | Swap nibbles in A | A = (A>>4) | (A<<4) |
| `SWAP r` | Swap register pair halves | BC = C×256+B, etc. |
| `MIRROR A` | Reverse bit order in A | A = bit-reversed |
| `TEST #nn` | AND with immediate, set flags, don't modify A | Like `AND #nn` but A preserved |
| `BRLD/BSLA/etc.` | Various bit operations | |

These extensions make the ZX Spectrum Next significantly more capable for mathematical operations while maintaining full backward compatibility with the original Z80 ISA.

---

## Programming Mindset Shift

### From Modern to Z80

| Modern Habit | Z80 Reality |
|-------------|-------------|
| "Just use more memory" | 64 KB total — every byte counts |
| "Let the compiler optimize" | You ARE the optimizer — write assembly |
| "Use a hash map" | Binary search or lookup table — hash tables cost too much RAM |
| "Allocate on the heap" | No heap — use static buffers or stack |
| "Call a library function" | Write it yourself — no stdlib |
| "Don't worry about byte order" | Z80 is little-endian — but you must handle 16-bit manually |
| "It's fast enough" | At 3.5 MHz, nothing is fast enough without care |
| "Use floating point" | Use fixed-point or lookup tables — no FPU |
| "Cache-line align" | No cache — worry about contended vs. uncontended memory |
| "Profile and optimize" | Count T-states on paper — timing is deterministic |

### From Z80 to Modern

| Z80 Habit | Modern Reality |
|-----------|---------------|
| Count T-states | Use a profiler — cycle counting is meaningless with out-of-order execution |
| Avoid function calls | Function calls are nearly free with branch prediction |
| Use self-modifying code | Instruction caches make SMC expensive — use data instead |
| Prefer registers over memory | Caches make memory almost as fast as registers |
| Avoid IX/IY (too slow) | Modern addressing modes are all equally fast |
| Inline everything | Let the compiler decide — it knows the cache size |
| Write assembly | Compilers generate better code than humans 95% of the time |

---

## Best Practices for Modern Developers Learning Z80

1. **Think in bytes and T-states** — every variable is 8 bits, every operation has a fixed cost you can calculate.
2. **HL is your best friend** — `(HL)` is the fastest memory access; structure your data to be accessed sequentially through HL.
3. **Forget about objects and classes** — the Z80 has no stack frames, no heap, no objects. Think flat buffers and offsets.
4. **Learn to love lookup tables** — no multiply? Pre-compute a 256-byte table. No sin()? Pre-compute a quarter-wave table.
5. **Don't fight the accumulator** — everything goes through A. Plan your code flow around it.
6. **Use the shadow registers** — `EXX` / `EX AF,AF'` is essentially free context save. Use it in ISRs and inner loops.
7. **Embrace the constraints** — the creativity of ZX Spectrum programming comes FROM the limitations, not despite them.

---

## Antipatterns

### The Modern Mindset

```z80
; BAD: Writing Z80 like modern C code
; "I need an array of structures"
; Each struct: { x: byte, y: byte, color: byte, flags: byte }
; Access: LD A,(IX+0) / LD B,(IX+1) / ... — 19T per field!

; This is slow, bloated, and fights the hardware
```

```z80
; GOOD: Structure of Arrays — Z80 style
; Separate arrays: xs[], ys[], colors[], flags[]
; Sequential access via (HL) — 7T per element
LD   HL,xs_array   ; Point to x values
LD   A,(HL)        ; Get x — 7T
INC  HL            ; Next — 6T
; 13T per element vs. 38T+ with IX struct access
```

### The Premature Optimization

```z80
; BAD: Optimizing the wrong thing
; Spending hours on a 2T savings in an initialization routine
; that runs once — 0.00003% of frame time
```

```z80
; GOOD: Optimize the inner loop first
; A 1T savings in a loop that runs 6144 times saves 6144T per frame
; That's 8.8% of the entire frame budget!
```

---

## References

- **Zilog Z80 CPU User Manual (UM0080)** — Official ISA and architecture reference
- **Ken Shirriff, "Reverse-engineering the Z80"** ([righto.com](http://www.righto.com/2014/10/reverse-engineering-z80.html)) — Die-level analysis of Z80 internals
- [Rodnay Zaks, "Programming the Z80"](https://en.wikipedia.org/wiki/Rodnay_Zaks) — Classic textbook comparing Z80 to 8080/6502
- [Various community comparisons](https://zx-pk.ru) — Thread-level cross-references for Z80 vs. modern CPUs; the canonical discussion venues for benchmarking Z80 against ARM, RISC-V, and other modern ISAs.
- **ZX Spectrum Next Documentation** ([zxnext.io](https://zxnext.io/)) — Z80N extended ISA

### Cross-References

- [z80_architecture.md](z80_architecture.md) — Z80 register file and internal structure
- [z80_instruction_set.md](z80_instruction_set.md) — Complete ISA with per-instruction timing
- [z80_flags.md](z80_flags.md) — Flag register comparison to x86 RFLAGS
- [z80_timing.md](z80_timing.md) — Why deterministic timing matters
- [z80_undocumented.md](z80_undocumented.md) — Undocumented behavior that modern CPUs don't have
