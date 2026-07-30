[← Home](../README.md) · [Toolchain](README.md)

# ZX Spin — Emulator with Built-in Assembler and Debugger

**ZX Spin** is a ZX Spectrum emulator for Windows, originally developed by **Mark Woodmass** (handle "Dunny") and the Spin team, first released around 2005. Alongside Fuse, Spectaculator, and ZEsarUX, ZX Spin is one of the most widely used Spectrum emulators. Its distinguishing feature in the toolchain context is its **built-in BASIC editor, assembler, and debugger** — making it a self-contained IDE for Spectrum development without external tools.

ZX Spin is notable for being the **first major emulator** to ship with an integrated assembler (BASin, later replaced by Spin's own assembler). It also pioneered several features that later emulators adopted, including the **memory tracker**, **breakpoint system**, and **real-time disassembly view**.

> [!NOTE]
> This article focuses on ZX Spin as a **development tool** (assembler, debugger, IDE). For ZX Spin as an emulator for running games, see [emulation](../11_emulation/README.md).

---

## Quick Start

Download ZX Spin from the [Spectrum Spin site](http://www.zxspectrum4.net/) or a retro-computing mirror. It runs on Windows (XP through 11). On macOS and Linux, use WINE.

To write and assemble a small program inside ZX Spin:

1. Launch ZX Spin
2. Press **F8** to open the assembler window (or use `Tools > Assembler`)
3. Type your source:

```z80
        org  #8000

start:  ld   hl, message
        call print_string
        ret

message:
        db   "Hello, World!", 13, 0

print_string:
        ld   a, (hl)
        or   a
        ret  z
        rst  16
        inc  hl
        jr   print_string

        end  start
```

4. Press **F9** to assemble. ZX Spin assembles the code, places it in emulated memory at `#8000`, and offers to set a breakpoint at `start`.
5. Press **F5** to run. The emulator runs and stops at the breakpoint.
6. Use the debugger to step through, inspect registers and memory.
7. Type `RANDOMIZE USR 32768` in the BASIC window to call the routine from BASIC.

---

## History and Design Philosophy

ZX Spin was started in 2004 by Mark Woodmass ("Dunny"), with contributions from Andrew Barker, Simon Owen, and others in the Spectrum scene. The goal was a **high-accuracy emulator** that doubled as a **development environment**. At the time, most emulators were pure run-time environments — to develop Spectrum software, you needed a separate assembler (like Pasmo or SjASMPlus) and a separate debugger.

Spin's integration of:
- A Z80 assembler
- A symbol-aware debugger
- A memory tracker
- A BASIC editor with syntax highlighting

...in a single Windows executable made it a popular choice for hobbyist Spectrum developers throughout the late 2000s and early 2010s.

### Version Timeline

| Year | Version | Highlights |
|---|---|---|
| 2004 | 0.1-0.5 | Initial releases; core Z80 emulation |
| 2005 | 0.66 | BASin-style integrated BASIC editor |
| 2006 | 0.7 | Built-in assembler added |
| 2007 | 0.725 | Debugger with breakpoints; memory tracker |
| 2010 | 0.83 | Improved 128K / +2A / +3 support |
| 2015 | 1.0 | Final release from Dunny; project enters maintenance mode |
| 2020s | — | Available from retro mirrors; no active development |

### Current Status

ZX Spin is **not actively maintained**. The last official release was version 1.0 in 2015. The project's source code is partially available (Delphi/Pascal), and forks exist, but no single fork has become the canonical successor. For modern development, the active alternatives are:

- [**ZEsarUX**](../11_emulation/) — most feature-rich modern emulator, cross-platform
- [**Fuse**](../11_emulation/) — most accurate, cross-platform
- [**Spectacular**](../11_emulation/) — commercial, Windows-only

Despite being unmaintained, ZX Spin remains a popular teaching tool because of its integrated IDE.

---

## Built-In Assembler

ZX Spin's integrated assembler is a Z80 cross-assembler that writes directly to emulated memory. It is similar in syntax to Pasmo and SjASMPlus.

### Syntax Features

- **Hex**: `#NN` (preferred), `$NN`, `0xNN`, `NNh` all accepted
- **Number formats**: decimal, hex (multiple styles), binary (`%10101010`)
- **Directives**: `org`, `db`/`defb`, `dw`/`defw`, `ds`, `equ`, `include`, `incbin`, `if`/`else`/`endif`, `macro`/`endm`, `rept`/`endr`, `end`
- **Operators**: full C-like expression evaluator
- **Macros**: named-parameter, with `rept` for repeat blocks
- **Labels**: standard alphanumeric with `.` for local labels

### Code Complete and Symbolic Debugging

The assembler emits a symbol table that the debugger uses. This means when you set a breakpoint, you can refer to it by **symbolic name** (like `print_string`) rather than raw address. The disassembly view also uses these symbols, making the debugging experience much closer to a modern IDE than to a raw memory dump.

### Integration with Emulated Memory

When you assemble in ZX Spin, the resulting bytes go directly into emulated Spectrum memory at the address specified by `org`. There is no intermediate file. This means you can:

- Edit, assemble, and run in seconds
- Inspect the result with the memory tracker
- Set breakpoints on specific labels
- Single-step through the source as written (not just the disassembly)

This workflow is similar to developing on a native assembler like [ALASM](alasm_sts.md), but with the accuracy and convenience of a cross-platform emulator.

---

## Built-In Debugger

ZX Spin's debugger was, at its release, one of the best Spectrum debuggers available. Features include:

### Breakpoints

- **Execution breakpoints**: stop when the PC reaches a specific address
- **Memory read breakpoints**: stop when a specific address is read
- **Memory write breakpoints**: stop when a specific address is written
- **Port I/O breakpoints**: stop on IN or OUT to a specific port
- **Symbolic breakpoints**: refer to addresses by symbol (if you assembled with the built-in assembler)

### Register View

All Z80 registers are displayed: AF, BC, DE, HL, AF', BC', DE', HL', IX, IY, SP, PC, I, R, IFF1, IFF2, IM. The view updates in real time as you single-step.

### Memory View

A memory dump with optional ASCII column. You can edit memory in-place (hex or ASCII). The view can follow the PC or follow a specific address.

### Disassembly View

Real-time disassembly follows the PC. Symbolic labels from the built-in assembler are shown. Conditional jumps show their branch targets.

### Memory Tracker

The memory tracker watches for any memory write and logs it. This is invaluable for finding:

- Where a value comes from (track a write to a system variable back to its source)
- When a buffer is corrupted
- How a game's state machine changes

---

## Built-In BASIC Editor (BASin Integration)

ZX Spin includes a **BASIC editor** that provides a modern text-editor interface to Sinclair BASIC. Features:

- Syntax highlighting for Sinclair BASIC keywords
- Auto-indenting
- Symbolic label support (within BASIC)
- Direct tokenization into Spectrum memory
- Save/load as `.tap` or `.z80`

This makes ZX Spin useful not only for machine code but also for BASIC development. The editor can write BASIC programs directly into the emulated Spectrum's memory without tape loading.

---

## When to Use ZX Spin

### Strengths

- **Integrated IDE** — assembler + debugger + BASIC editor in one window
- **Symbolic debugging** — breakpoints and disassembly use your source labels
- **Memory tracker** — invaluable for reverse-engineering
- **Windows-native** — no WINE needed on Windows
- **Small, fast, lightweight** — runs on older hardware
- **Good compatibility** — runs most Spectrum software accurately

### Weaknesses

- **Windows-only** — requires WINE on macOS and Linux
- **Not actively maintained** — last release was 2015
- **Less accurate than Fuse or ZEsarUX** — for the most precise cycle-accurate work, prefer Fuse
- **No Z80N (Spectrum Next) support** — for Next development, use CSpect
- **No scriptability** — no Lua or Python automation like ZEsarUX
- **No cross-platform build** — tied to Windows and Delphi

### Comparison Matrix

| Feature | ZX Spin | **Fuse** | **ZEsarUX** | **Spectaculator** |
|---|---|---|---|---|
| Year started | 2004 | 1999 | 2013 | 1997 |
| Active development | ❌ (2015) | ✅ | ✅ | ✅ (commercial) |
| Built-in assembler | ✅ | ❌ | ❌ | ❌ |
| Built-in debugger | ✅ | ⚠️ (basic) | ✅ (extensive) | ✅ |
| Memory tracker | ✅ | ❌ | ✅ | ⚠️ |
| Symbolic debugging | ✅ | ❌ | ❌ | ❌ |
| BASIC editor | ✅ | ❌ | ❌ | ❌ |
| Cross-platform | ❌ | ✅ | ✅ | ❌ |
| ZX Spectrum Next (Z80N) | ❌ | ❌ | ✅ | ❌ |
| Scriptable (Lua/Python) | ❌ | ❌ | ✅ | ❌ |
| License | Free | GPL | GPL | Commercial |

### Decision Guide

Choose **ZX Spin** when:
- You are on Windows and want an all-in-one IDE
- You want to learn Spectrum assembly with symbolic debugging
- You are teaching or learning Spectrum development
- You want to combine BASIC and machine code in one tool

Choose **ZEsarUX** when:
- You want the most features and the most active development
- You want cross-platform support
- You want to target ZX Spectrum Next
- You want scriptability (Lua)

Choose **Fuse** when:
- You want maximum accuracy for compatibility testing
- You want a simple, fast, well-maintained emulator

---

## Common Pitfalls

1. **Windows-only** — ZX Spin is a native Windows application. On macOS and Linux, you need WINE, which adds complexity.

2. **No active maintenance** — bugs from 2015 are unlikely to be fixed. Some features may not work correctly on modern Windows.

3. **No cross-platform build** — unlike Fuse and ZEsarUX, the source code is Delphi/Pascal and not portable to non-Windows systems.

4. **Limited Z80N support** — for ZX Spectrum Next development, ZX Spin is the wrong choice. Use CSpect, ZEsarUX, or a real Next.

5. **Built-in assembler is single-file** — the built-in assembler does not support multi-file projects with linking. Use [SjASMPlus](sjasmplus.md) or [z88dk z80asm](z88dk_z80asm.md) for complex projects, and load the resulting binary into ZX Spin for debugging.

6. **Symbolic debugging requires the built-in assembler** — to get symbolic breakpoints, you must assemble within ZX Spin. If you assemble with SjASMPlus externally, ZX Spin can debug the code but only at the address level (no labels).

7. **Disk image support is limited** — ZX Spin supports `.dsk` (TR-DOS) but has weaker disk support than ZEsarUX for obscure formats.

---

## FAQ

**Q: Is ZX Spin still the best Spectrum IDE?**

A: For pure Windows users who want an integrated IDE, ZX Spin remains a strong choice. For cross-platform or active development, ZEsarUX is better. For modern cross-development workflows, most programmers use [SjASMPlus](sjasmplus.md) + [VS Code](vscode_integration.md) + Fuse or ZEsarUX for debugging.

**Q: Where can I download ZX Spin?**

A: From [zxspectrum4.net](http://www.zxspectrum4.net/) or various retro-computing mirrors. The last version is 1.0 from 2015.

**Q: Does ZX Spin support ZX Spectrum Next?**

A: No. For Next development, use CSpect (the Next-specific emulator) or ZEsarUX (which has Z80N support).

**Q: Can I use ZX Spin's debugger with code assembled by SjASMPlus?**

A: Yes, but you lose the symbolic debugging. Load the `.sna` or `.tap` produced by SjASMPlus into ZX Spin and set breakpoints by address, not by label. Some SjASMPlus versions can emit a `.sym` file that ZX Spin can load — check the documentation for both tools.

**Q: What is the relationship between ZX Spin and BASin?**

A: BASin (Basic Assembler INterface) is a separate project by Dunny that focused on BASIC editing. ZX Spin integrated many BASin concepts. BASin is also unmaintained.

**Q: Is ZX Spin open source?**

A: Partially. The Delphi/Pascal source has been shared in various forms over the years, but there is no canonical public repository with active maintenance.

---

## Cross-References

- [vscode_integration.md](vscode_integration.md) — modern alternative for editor + toolchain integration
- [debugging.md](debugging.md) — debugging strategies and tools survey
- [sjasmplus.md](sjasmplus.md) — recommended external assembler to pair with ZX Spin
- [pasmo.md](pasmo.md) — another external assembler option
- [alasm_sts.md](alasm_sts.md) — STS, the native equivalent of ZX Spin's debugger
- [native_toolchain.md](native_toolchain.md) — survey of native assemblers
- [cross_platform_toolchain.md](cross_platform_toolchain.md) — survey of cross-assemblers
- [../11_emulation/README.md](../11_emulation/README.md) — broader emulator coverage

---

## References

- Mark Woodmass ("Dunny") — ZX Spin releases and documentation
- ZX Spin home — [zxspectrum4.net](http://www.zxspectrum4.net/)
- BASin project — separate but related, by the same author
- Forum threads on World of Spectrum (now archived) documenting ZX Spin's development
- Comparison articles in retro-computing magazines covering ZX Spin vs Spectaculator vs Fuse
