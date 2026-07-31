[← Home](../../README.md) · [Development](../README.md)

# Development — Z80 Assembly Programming

This directory is a six-article tutorial series covering **Z80 assembly programming** on the ZX Spectrum, from first program to performance optimization and mixed C/asm development. The series is sequential — each article builds on the previous — but experienced programmers can use the table below to jump to specific topics.

---

## Articles

| # | Article | Description |
|---|---|---|
| 1 | [assembly_intro.md](assembly_intro.md) | **Getting started with Z80 assembly**: why assembly (3 quantified reasons), toolchain setup (SjASMPlus + Fuse + VSCode/DeZog), source file structure, essential directives, syntax differences across assemblers, 48K memory map (ASCII diagram), where to place code and stack, complete annotated Hello World walkthrough (line-by-line), building pipeline (.asm to .tap/.sna), output format comparison (SNA/TAP/TZX/TRD/NEX), first debugging session, when to use asm vs C vs BASIC. |
| 2 | [rom_calls.md](rom_calls.md) | **Calling the ROM from assembly**: ROM entry-point landscape (RST/CALL/helpers), save/restore state discipline (IY = #5C3A, ERR_SP try/catch), cookbook for character output (RST #10), keyboard input (KEY-INPUT/BREAK-KEY/direct port scan), screen management (CLS, border, attributes, pixel plotting via PLOT-SUB), BEEP limitations, math via FP calculator (RST #28), 128K-specific routines (PLAY handler), AY-3-8912 direct access (OUT #FFFD/#BFFD), ROM-call wrapper macros, when NOT to use ROM. |
| 3 | [stack_and_rst.md](stack_and_rst.md) | **Stack, RST vectors, and calling conventions**: stack mechanics with T-state table for all PUSH/POP/CALL/RET variants, SP placement and contended memory, the balanced stack rule (symmetric patterns, conditional pushes, early returns), the eight RST vectors (single-byte calls), five calling conventions (caller/callee-saved, register vs stack params, FASTCALL), shadow registers via EXX/EX AF,AF', stack as temporary storage, computed calls (JP (HL) trick, PUSH+RET dispatch), stack frames for locals, ERR_SP try/catch, recursion and reentrancy. |
| 4 | [assembly_patterns.md](assembly_patterns.md) | **Assembly design patterns**: state machines (Moore/Mealy, hierarchical), jump/dispatch tables (indexed CALL via PUSH+RET, bounds checking), table-driven code (enemy spawn tables, level data, message systems), function pointer tables (plugin architecture, sound driver abstraction), coroutine patterns via stack swapping, self-modifying code (SMC) patterns (counter patching, address patching, code toggling), macro systems for readability, modular file organization (INCLUDE/INCBIN, SECTION placement), 128K memory banking patterns (bank switching, banked code/data, common-area design). |
| 5 | [assembly_optimization.md](assembly_optimization.md) | **Performance optimization**: the optimization workflow (measure, identify, rewrite, re-measure), T-state budgeting (69,888T/frame breakdown), hot-loop techniques (loop invariants, register reassignment, LDIR vs manual, DJNZ, unrolling), lookup tables (sine, fast multiply via squares identity), fast multiply without tables (shift-and-add, 16-bit), fast divide (shift-subtract, constant divisors), SMC in hot loops, memory access patterns (contended vs uncontended), instruction reordering, 10-recipe performance cookbook (clear screen, strlen, multiply by 10, bit reverse, LFSR RNG, byte swap). |
| 6 | [c_interop.md](c_interop.md) | **Mixed C and assembly programming**: why mix (80/20 rule), the two compilers (sccz80 vs zsdcc), calling conventions in depth (sccz80 classic, FASTCALL, SDCC sdcccall(0)/(1), preserves_regs), C calling assembly (extern declarations, assembly wrapper, LDIR-based memset_fast), assembly calling C (stack discipline, return values, save IY), inline assembly (__asm blocks, register access, clobbering), shared global variables (PUBLIC/EXTERN, endianness, struct layout), project structure (multi-file, Makefile), build pipeline (zcc front-end, map files), performance patterns (which C operations are slow on Z80), decision matrix, library interop (z88dk newlib routines), complete worked multi-file project. |

---

## Reading Order

The series is designed to be read sequentially:

```
Article 1 (Intro) ──► Article 2 (ROM Calls) ──► Article 3 (Stack/RST)
                                                        │
                                                        ▼
Article 6 (C Interop) ◄── Article 5 (Optimization) ◄── Article 4 (Patterns)
```

If you already know Z80 assembly basics, start at Article 3 (Stack/RST) — the calling conventions there are referenced by every subsequent article.

---

## What This Series Does NOT Cover

These topics have their own dedicated articles elsewhere:

| Topic | Location |
|---|---|
| Z80 instruction set reference | [z80_instruction_set.md](../../01_cpu/z80_instruction_set.md) |
| Z80 architecture (registers, ALU, bus) | [z80_architecture.md](../../01_cpu/z80_architecture.md) |
| Z80 addressing modes | [z80_addressing.md](../../01_cpu/z80_addressing.md) |
| Z80 flags register | [z80_flags.md](../../01_cpu/z80_flags.md) |
| Z80 instruction timing (T-states) | [z80_timing.md](../../01_cpu/z80_timing.md) |
| Z80 interrupts (CPU level) | [z80_interrupts.md](../../01_cpu/z80_interrupts.md) |
| Micro-level coding practices | [z80_coding_practices.md](../../01_cpu/z80_coding_practices.md) |
| Undocumented instructions | [z80_undocumented.md](../../01_cpu/z80_undocumented.md) |
| ROM routine lookup table | [rom_routines.md](../../10_references/rom_routines.md) |
| ROM internals (48K) | [rom_48k.md](../../04_operating_systems/rom_48k.md) |
| ROM internals (128K) | [rom_128k.md](../../04_operating_systems/rom_128k.md) |
| Interrupt programming (IM1/IM2) | [interrupt_programming.md](../04_interrupts/interrupt_programming.md) |
| ULA contention model | [ula_contention.md](../../02_hardware/original/ula_contention.md) |
| z88dk toolchain reference | [z88dk.md](../../09_toolchain/z88dk.md) |
| SDCC compiler reference | [sdcc.md](../../09_toolchain/sdcc.md) |
| Debugging tools | [debugging.md](../../09_toolchain/debugging.md) |

---

See [PLAN.md](../../PLAN.md) for the full article catalog.
