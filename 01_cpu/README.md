[← Home](../README.md) · [Z80 CPU](README.md)

# Z80 CPU — Deep Dive

The Z80 is the heart of every ZX Spectrum. This directory covers the CPU from silicon to software: how it decodes instructions, how it talks to memory and I/O, and how its timing quirks shape every demo and game ever written.

The article order follows the Zilog UM0080 User Manual chapter structure, then extends into undocumented behavior and modern comparisons.

---

## Articles

| # | Article | Description |
|---|---------|------------|
| 1 | [z80_architecture.md](z80_architecture.md) | Registers, ALU, pinout, bus interface, and internal datapath |
| 2 | [z80_addressing.md](z80_addressing.md) | All addressing modes — immediate, register, indirect, indexed, relative |
| 3 | [z80_flags.md](z80_flags.md) | S, Z, H, P/V, N, C flags — per-instruction behavior, DAA, BCD arithmetic |
| 4 | [z80_instruction_set.md](z80_instruction_set.md) | Complete ISA: 698 instructions, opcode encoding, timing, groups, decision guides |
| 5 | [z80_undocumented.md](z80_undocumented.md) | IX/IY halves, SLL, MEMPTR, F3/F5, OUT (C),0, clone detection, R register |
| 6 | [z80_timing.md](z80_timing.md) | T-states, M-cycles, bus timing, WAIT pin, per-instruction costs, prefix byte timing, DRAM refresh |
| 7 | [z80_interrupts.md](z80_interrupts.md) | IM0/IM1/IM2, NMI, IFF1/IFF2, vector tables, EI latency, per-model timing |
| 8 | [z80_vs_modern.md](z80_vs_modern.md) | Z80 vs x86-64/ARM64 comparison, register mapping, programming mindset shift |
| 9 | [z80_coding_practices.md](z80_coding_practices.md) | Register discipline, instruction selection, arithmetic tricks, contention-aware coding, stack blitter |

### Reading Order

**Start here if you're new to Z80 assembly:**

1. [Architecture](z80_architecture.md) — understand the register file and data paths
2. [Addressing](z80_addressing.md) — how the CPU addresses memory and I/O
3. [Flags](z80_flags.md) — how conditional logic works
4. [Instruction Set](z80_instruction_set.md) — the complete reference (bookmark this)

**For emulator authors and demoscene programmers:**

5. [Undocumented](z80_undocumented.md) — essential for accuracy (ZEXALL test suite requirements)
6. [Timing](z80_timing.md) — T-states, M-cycles, bus timing, and per-instruction costs
7. [ULA Timing](../02_hardware/original/ula_timing.md) — memory contention, frame timing, multicolor effects *(in Hardware → Original)*
8. [Clone Timing](../02_hardware/clones/clone_timing.md) — Pentagon, Scorpion, Kay, FPGA timing *(in Hardware → Clones)*
9. [Interrupts](z80_interrupts.md) — interrupt architecture and per-model differences

**For developers coming from modern platforms:**

10. [Z80 vs Modern](z80_vs_modern.md) — mindset translation guide

**Bridge to advanced optimization:**

11. [Coding Practices](z80_coding_practices.md) — practical patterns, T-state budgeting, and the path to demo-grade code

---

See [PLAN.md](../PLAN.md) for the full knowledge base catalog.
