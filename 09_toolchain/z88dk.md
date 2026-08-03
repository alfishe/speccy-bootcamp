[← Toolchain](README.md) · [Cross-Platform Toolchain](cross_platform_toolchain.md)

# z88dk — C Compiler, Assembler, and Standard Library for the Z80 Family

---

## Overview

z88dk is a complete C development kit for the Z80 family. Where SjASMPlus is the tool of choice for hand-written assembly, z88dk is the tool of choice when you want to write in **C** — or mix C and assembly freely — and produce a working binary for the ZX Spectrum, ZX Spectrum Next, Pentagon, Scorpion, +3 (in CP/M mode), Timex Sinclair, Cambridge Z88, MSX, Amstrad CPC, CP/M machines, RC2014, and roughly **100 other Z80 targets**.

The toolkit is unique in three respects:

1. **Two C compilers in one box.** The legacy **sccz80** (derived from Small-C, now nearly C90-compliant) and a patched **SDCC** (the well-known Small Device C Compiler, customized for z88dk's library model). Both compilers can target any of the supported machines, and with the classic library they can even be mixed in the same project.
2. **Two standard libraries.** The **classic library** covers ~100 targets with broad hardware-specific extensions. The **new library** (`_DEVELOPMENT` / "newlib") is a C11-subset rewrite focused on tighter code, faster performance, and modern target support including the ZX Spectrum Next.
3. **An extensive assembly-language subroutine library** that the C compilers call into. This is what gives z88dk its benchmark-leading performance: the C compiler emits calls to hand-optimized assembly routines for `memcpy`, `printf`, math, graphics, and dozens of platform-specific functions. The same library is available to assembly-language programmers directly, making z88dk a useful toolkit even for projects that never compile a line of C.

The front-end `zcc` orchestrates everything: preprocessing, compilation, assembly, linking, and post-processing into a target-ready binary (`.tap`, `.sna`, `.nex`, `.rom`, `.cpm`, etc.). For most projects you never need to invoke any other tool directly.

---

## History

| Period | Milestone |
|---|---|
| **1990s** | Original **Small-C** lineage; targets the Cambridge Z88 (hence the name "z88dk"). |
| **Early 2000s** | **sccz80** matures into a near-C90 compiler; classic library expands to dozens of targets. |
| **2010s** | **SDCC integration**: z88dk patches SDCC to share the same library and target model, giving users a choice of compilers. |
| **2015–2018** | **New C library** (`_DEVELOPMENT`) rewrite: C11 subset, hand-optimized assembly library, performance focus. ZX Spectrum Next support added as first-class. |
| **2020s** | Active maintenance; nightly builds; ~100 targets; RC2014, HBios, z180, ez80, Rabbit 2000/3000 support added. |

The project is community-maintained on GitHub at [z88dk/z88dk](https://github.com/z88dk/z88dk). The wiki at [z88dk.org/wiki](https://www.z88dk.org/wiki) is the canonical documentation, though it is being progressively migrated to the GitHub Wiki.

---

## Tool Layout

z88dk is a toolkit of cooperating tools. You normally only invoke `zcc`, but knowing what is underneath helps when debugging build issues.

### User-facing tools

| Tool | Purpose |
|---|---|
| `zcc` | **The front end.** Accepts `.c`, `.i`, `.asm`, `.opt`, `.o` files; runs preprocess, compile, optimize, assemble, link, and post-process stages as needed. The `-target` flag (e.g., `+zx`) selects the machine. |
| `z88dk-ticks` | Cycle-counting emulator with built-in debugger and disassembler. Run code fragments and read T-state counts. |
| `z88dk-dis` | Standalone disassembler for 8080, 8085, GBZ80, Z80, Z180, Z80N, EZ80, R800, Rabbit 2000/3000. Reads `.map` files for symbolic output. |
| `z88dk-lib` | Installer for third-party libraries (manages install/remove/list). |
| `z88dk-zx0`, `z88dk-zx7` | Data compression tools (with companion Z80 decompression code in the library). |
| `z88dk-dzx0`, `z88dk-dzx7` | Decompression counterparts for testing. |

### Compiler backends

| Tool | Purpose |
|---|---|
| `z88dk-sccz80` | The native C compiler. Default. Near-C90 compliant. |
| `z88dk-zsdcc` | Patched SDCC. Better at floating point; some code-quality advantages for certain patterns. |
| `z88dk-80cc` | Alternative Small-C compiler front end; shares classic library linkage. Mostly used in benchmarks. |

Select with `-compiler=sccz80` (default) or `-compiler=sdcc` on the `zcc` command line.

### Internal tools (invoked by zcc)

| Tool | Purpose |
|---|---|
| `z88dk-ucpp` | C preprocessor (used by both sccz80 and zsdcc). |
| `z88dk-zpragma` | Processes `#pragma` directives embedded in C source. |
| `z88dk-z80asm` | The assembler / linker / librarian. Implements sections, modules, and library archives. Not to be confused with several unrelated projects also called "z80asm." |
| `z88dk-z80nm` | Symbol/library inspector. Lists functions or data in an object or library file. |
| `z88dk-copt` | Regular-expression peephole optimizer for sccz80; post-processor for both compilers. |
| `z88dk-appmake` | Converts linked binary into target-ready format: Intel HEX, TAP, TZX, ROM, NEX, DSK, etc. |
| `m4` | Optional macro preprocessor (runs ahead of the C preprocessor). |
| `z88dk-gdb` | gdbserver-compatible debugger bridge for emulators and real hardware. |

The `-v` (verbose) flag to `zcc` shows exactly which internal tools are invoked and with what arguments.

> [!TIP]
> **`z88dk-gdb` and `z88dk-ticks` are documented in depth in [debugging.md](debugging.md).** That article covers the full ZX Spectrum debugger landscape across three layers (native monitor-debuggers, emulator debuggers, source-level / IDE-integrated), with the complete `z88dk-gdb` + Fuse `gdbserver` workflow, the `.lis` / `.map` / `.list` debug-metadata pipeline, and a comparison against mainline GDB's Z80 target (merged July 2021). See especially [§ GDB-based Debuggers and the GDB Z80 Target](debugging.md#gdb-based-debuggers-and-the-gdb-z80-target) and [§ Compiler Integration](debugging.md#compiler-integration--producing-debug-metadata).

---

## Installation

### Pre-built binaries

- **Windows**: nightly `.exe` installer from the [nightly build page](https://github.com/z88dk/z88dk/releases/tag/nightly). Includes all binaries and the library source tree.
- **macOS**: nightly `.pkg` installer (same page).
- **Snap** (Linux): `sudo snap install z88dk`
- **Docker**: `docker pull z88dk/z88dk`

### Build from source

```bash
git clone --recursive https://github.com/z88dk/z88dk.git
cd z88dk

# Build the native C backend (sccz80, z80asm, appmake, etc.):
export ZCCCFG=/path/to/z88dk/lib/config
BUILD_SDCC=1 bash build.sh           # or: build.sh --without-boost

# Optionally build SDCC patch:
# (already handled by BUILD_SDCC=1 above if you have sdcc source available)

# Set environment variables (add to ~/.bashrc or ~/.zshrc):
export PATH=$PATH:$(pwd)/bin
export ZCCCFG=$(pwd)/lib/config
```

On Windows, use MSYS2 with `pacman -S make gcc python zlib-devel boost`. The build.sh script works in the MSYS2 shell.

### Verify installation

```bash
zcc --version
z88dk-sccz80 --version
z88dk-z80asm --version
appmake +zx --help | head -5
```

---

## The Two Standard Libraries

The single most important architectural decision when starting a z88dk project is **which C library to link against**. The two libraries are not interchangeable — they have different function signatures, different CRT0 startup files, different performance characteristics, and slightly different target coverage.

### Decision matrix

| Criterion | Classic library | New library (`_DEVELOPMENT` / "newlib") |
|---|---|---|
| **Targets** | ~100 (broadest coverage; everything z88dk has ever supported) | ~20 (ZX Spectrum, ZX Next, MSX, Sega Master System, RC2014, HBios, scz180, yaz180, CP/M, + generic z80/z180 bare bones) |
| **C standard** | Near-C90 (some C99 features) | C11 subset |
| **Performance** | Adequate; long history of incremental improvements | **Hand-optimized assembly**; benchmark-leading performance (memcpy, printf, math) |
| **Code size** | Larger (more code paths, more backward compatibility) | Smaller; library auto-prunes unused functions at link time |
| **Math** | `genmath`, `math48`, `mbf32`, IEEE `math32` | `math48` (default), `math32` (IEEE) |
| **Compiler mixing** | ✅ sccz80 + zsdcc objects in one binary | ❌ Pick one compiler per project |
| **CRT0 customization** | Via `#pragma output` and `-startup=N` flags | Via target-specific `_DEVELOPMENT/srt0_*.asm` files |
| **Mixing classic + newlib in one project** | Not supported | Not supported |
| **Recommended for** | Existing projects, unusual targets, mixing compilers, legacy code | New projects on common targets (ZX, Next, MSX) — better performance |

### How to select

The library is chosen by the `-clib=` flag on the `zcc` command line:

```bash
# Classic library (default):
zcc +zx -clib=classic program.c -o program.bin -create-app
# (Or omit -clib= entirely; classic is the default.)

# New library:
zcc +zx -clib=new program.c -o program.bin -create-app
# (Some targets accept -clib=sdcc_ix or -clib=sdcc_iy for newlib+SDCC variants.)
```

### What "newlib" actually is

The new library lives under `libsrc/_DEVELOPMENT/`. Its design principles:

- **One function per source file** so the linker can prune unused code perfectly.
- **Hand-written assembly** for every public function, including C standard library calls like `memcpy`, `strlen`, `printf`.
- **Calling convention choice**: `__z88dk_fastcall` (single argument passed in DEHL), `__z88dk_callee` (callee cleans up stack), `__smallc` (caller cleans up), `__stdc` (caller cleans up, C89). The library is built multiple times under different calling conventions, and the link step picks the variant that matches your compile flags.
- **Section-based memory layout**. The newlib uses z80asm's section mechanism (`bss_zx`, `code_zx`, `data_zx`, `rodata_zx`) to place code and data in correct memory regions automatically.

### Library source organization

```
libsrc/
├── _DEVELOPMENT/       # new library
│   ├── EXAMPLES/       # example programs (compile lines at top of each)
│   ├── adt/            # abstract data types (queues, stacks, trees)
│   ├── alloc/          # malloc / free implementations
│   ├── ctype/
│   ├── errno/
│   ├── font/           # 4×6, 6×8, 8×8, fzx fonts
│   ├── graphics/       # line, circle, polygon, blit, stencil
│   ├── input/          # keyboard, joystick, mouse
│   ├── locale/
│   ├── math/           # math48, math32, mbf32, etc.
│   ├── setjmp/
│   ├── sound/          # beeper, AY, music players
│   ├── stdio/
│   ├── stdlib/
│   ├── string/
│   ├── target/zx/      # ZX-specific: hardware regs, ULAplus, sprites, etc.
│   ├── target/zxn/     # ZX Next: Layer 2, hardware sprites, tilemap
│   ├── time/
│   └── z80/            # raw Z80 utilities (delay loops, etc.)
├── ctype/              # classic library (parallel structure)
├── math/
├── stdio/
├── ...
└── target/
    ├── zx/             # classic: ZX-specific library code
    └── zxn/            # classic: ZX Next support
```

---

## Targets

Every `zcc` invocation names a **target** with the `+name` flag (e.g. `+zx`, `+zxn`, `+cpm`). The target controls:

- The default CRT0 startup file.
- The default memory map (where code, data, bss, and heap live).
- Which library variant is linked (`libsrc/target/<name>/`).
- The output format produced by `-create-app` (TAP, SNA, NEX, ROM, DSK, …).
- Appmake's post-processing rules (which loaders, headers, and boot sectors to apply).

The target list lives in `lib/config/<target>.cfg`. There are ~100 of them; the ones most relevant to a ZX Spectrum developer:

### Spectrum family

| Target | Machine | Library | Output (`-create-app`) |
|---|---|---|---|
| `+zx` | ZX Spectrum 16K / 48K | classic + new | TAP (custom BASIC loader), or SNA via `-subtype=sna` |
| `+zx128` | ZX Spectrum 128 / +2 / +2A / +3 (128K RAM, banking via 7FFDh) | classic + new | TAP, SNA, or `.scr` snapshot |
| `+zxn` | ZX Spectrum Next (Z80N, Layer 2, banking via 233Bh + 7FFDh) | new only | NEX (Next executable) |
| `+zx81` | Sinclair ZX81 (16K/32K/48K) | classic | P (native file format) |
| `+zx80` | Sinclair ZX80 | classic | .o (native file format) |
| `+ts2068` | Timex Sinclair 2068 (US sibling of Spectrum, dual display modes) | classic | TAP |
| `+pps` | Spectrum +3 booted in CP/M Plus mode | classic | DSK (CP/M `.EMS` file on +3 disk) |

### Other common Z80 targets

| Target | Machine | Notes |
|---|---|---|
| `+cpm` | Generic CP/M 2.2 machine (BDOS at 0005h) | Portability baseline; works on Kaypro, Osborne, Epson PX-8, Bondwell, etc. |
| `+z88` | Cambridge Z88 (the platform z88dk was originally written for) | 32K–128K RAM, OZ 3/4 ROM, memory banked |
| `+msx` | MSX / MSX2 / MSX2+ | BIOS-driven; works on real MSX and emulators |
| `+cpc` | Amstrad CPC 464 / 664 / 6128 | AMSDOS |
| `+sam` | SAM Coupé | Spectrum-compatible architecture, expanded video |
| `+gb` | Game Boy / Super Game Boy (Sharp LR35902) | Requires `-mgbz80` compiler mode |
| `+rc2014` | RC2014 bus machine (bare Z80) | Newlib target; ROMmable |
| `+scz180` | Hitachi HD64180 / Zilog Z180 boards | Newlib target; serial I/O |
| `+trs80` | TRS-80 Model I / III / 4 | |
| `+enterprise` | Enterprise 64/128 | |
| `+gal` | Galaksija (Yugoslav Spectrum-clone) | |
| `+p2000` | Philips P2000 | |
| `+s1mp3` | Generic s1mp3 MP3 player (Z80-based) | |
| `+ti82`, `+ti83`, `+ti83p`, `+ti85`, `+ti86` | Texas Instruments Z80 graphing calculators | |
| `+special` | Generic bare Z80 | Bring-your-own CRT0 |

The full list is enumerable with `zcc --list-targets` (recent builds) or by inspecting `lib/config/*.cfg`.

### ZX Spectrum 48K memory map (newlib default)

```
#0000  +-----------+
       |    ROM    |
#4000  +-----------+
       |  BASIC    |
       |  RAM      |   <- CRT0 lives here, near the top of RAM
       |           |
       |  ...      |   <- code_zx, rodata_zx
       |           |
       |  heap ↓   |   <- grows down
       |           |
       |  stack ↑  |   <- grows up from (RAMTOP+1)
       |           |
       |  far heap |   <- if -clib=new and banked buffers are used
#FF00  +-----------+
#FFFF  |  system   |   <- ROM-resident routines, workspace, ULA mirror
       +-----------+
```

The compiler reserves the top ~256 bytes for the BASIC stack; it is *your* responsibility to set RAMTOP (via `CLEAR` or the loader) low enough that the C stack and heap do not collide with it. Newlib's CRT0 honors `#pragma output STACKPTR` to relocate SP at startup.

---

## The `zcc` Front End

You invoke z88dk through one tool: **`zcc`**. It is a driver script that picks the correct preprocessor, compiler, assembler, linker, and post-processor based on the target and library selection, then chains them in order. The vast majority of options exist purely to be forwarded to the right downstream tool.

### Anatomy of a `zcc` invocation

```bash
zcc +zx -clib=new -vn -O3 hello.c -o hello.bin -create-app
│     │    │         │   │   │       │           │
│     │    │         │   │   │       │           └─ run appmake → hello.tap
│     │    │         │   │   │       └─ output base name
│     │    │         │   │   └─ input file (C source)
│     │    │         │   └─ optimize level 3 (peephole)
│     │    │         └─ no verbosity (also: -v for verbose)
│     │    └─ use new C library
│     └─ target: ZX Spectrum 48K
└─ always `zcc` (the driver)
```

### Most-used flags

| Flag | Effect |
|---|---|
| `+<target>` | Select target (mandatory). e.g. `+zx`, `+zxn`, `+cpm`. |
| `-clib=<name>` | Choose C library variant: `classic` (default) or `new`. Newlib targets further accept `sdcc_ix`, `sdcc_iy`, `sccz80` (the last is the newlib+sccz80 combination). |
| `-compiler=<c>` | Pick C compiler: `sccz80` (default) or `sdcc`. |
| `-o <file>` | Output base name. Final app output adds `.tap`, `.sna`, `.nex`, etc. |
| `-create-app` | Run appmake after link to produce the target-native container. Without it, only raw `.bin` is produced. |
| `-subtype=<s>` | Override appmake's default subtype (e.g. `-subtype=sna` for `+zx` to make a snapshot instead of a TAP; `-subtype=wav` for a TAP plus audio). |
| `-O[0-3]` | Peephole optimizer level (classic library). 0 disables; 3 is most aggressive. |
| `-SO[0-3]` | SDCC's internal optimizer level (when `-compiler=sdcc`). |
| `-v` / `-vn` | Verbose / silent. `-v` echoes every internal command — invaluable for debugging build issues. |
| `-lm` | Link math library (`-lm` for classic, `-lmath48` or `-lmath32` for newlib). |
| `-l<name>` | Link extra library (in `libsrc/`). |
| `-I<path>` | Add include search path (forwarded to preprocessor). |
| `-D<sym>[=<val>]` | Define preprocessor symbol (forwarded to preprocessor). |
| `-pragma-define:<name>=<value>` | Define a `#pragma output` symbol from the command line. |
| `-pragma-need:<name>` | Mark a `#pragma output` symbol as required (errors if not used). |
| `-Cz<opt>` | Pass `<opt>` through to appmake. |
| `-Cc<opt>` | Pass `<opt>` through to the C compiler. |
| `-Ca<opt>` | Pass `<opt>` through to the assembler (z80asm). |
| `-Cl<opt>` | Pass `<opt>` through to the linker. |
| `-custom-copt-rules=<file>` | Inject custom peephole rules. |
| `-g` | Emit debug symbols for `z88dk-gdb` / `z88dk-ticks`. |
| `-m` | Emit a `.map` file (symbols + addresses). Essential for cross-referencing with DeZog / emulators. |
| `-s` | Emit an assembly listing (`.asm`) for each compiled C file — use to inspect compiler output. |
| `--list-targets` | Print all available targets (recent builds only). |

### Preprocessing pipeline

When `zcc` processes `hello.c`, it runs approximately:

```mermaid
flowchart LR
    Src[hello.c] --> M4[optional m4]
    M4 --> CPP[z88dk-ucpp<br/>with target config headers]
    CPP --> ZP[z88dk-zpragma<br/>extracts #pragma]
    ZP --> CC[sccz80 or zsdcc]
    CC --> OPT[z88dk-copt<br/>peephole passes]
    OPT --> ASM[.asm files]
    ASM --> Z80ASM[z88dk-z80asm<br/>link + section placement]
    Z80ASM --> BIN[hello.bin + hello.map]
    BIN --> APPMAKE[z88dk-appmake<br/>+zx +create-app]
    APPMAKE --> Out[hello.tap / hello.sna / hello.nex]
```

The `-v` flag prints every command in this chain. If a build behaves unexpectedly, the first diagnostic step is always `zcc -v ...`.

### File extensions

| Extension | Meaning |
|---|---|
| `.c` | C source (compiled). |
| `.i` | Pre-processed C (skip preprocessor). |
| `.asm` | Assembly source (z80asm syntax, m4-compatible). |
| `.opt` | Peephole optimizer rules (input to `z88dk-copt`). |
| `.o` | Object file from z80asm. |
| `.lib` | Library archive. |
| `.bin` | Raw linked binary. |
| `.map` | Symbol map. |
| `.tap`, `.sna`, `.nex`, `.rom`, `.dsk` | Target-app containers produced by appmake. |

---

## Pragmas

z88dk uses C-source `#pragma` directives as the primary way to communicate non-portable decisions to the linker and CRT0. These pragmas are extracted from the source by `z88dk-zpragma` and turned into linker symbols before the C compiler even sees the file — they are not standard C `#pragma` and are not seen by the compiler.

There are three pragma families:

### `#pragma output` — control CRT0 behavior

`#pragma output NAME=value` defines a symbol that the CRT0 startup file consults. The classic library's CRT0 (`crt0_zx.asm` and friends) reads dozens of these symbols. If a symbol is defined, the corresponding behavior is enabled; if it is undefined, the default behavior is used.

```c
#pragma output CRT_ORG_CODE    = 24000      // relocate code to address 24000
#pragma output REGISTER_SP      = 0xFF57     // set SP at startup
#pragma output STACKPTR         = 0xFF57     // (alias)
#pragma output CLIB_EXIT        = 1          // emit exit() vector (classic only)
#pragma output CLIB_STDIO_HEAP  = 4096       // stdio heap size in bytes
#pragma output CRT_ENABLE_STDIO = 1          // ensure stdio is linked
#pragma output CLIB_DISABLE_IBMCHARS = 1     // no IBM-PC extended ASCII glyphs in default font
#pragma output CLIB_DEFAULT_SCREEN_MODE = 1  // enter hires mode on startup (Spectrum 64×192)
```

The full list is in `libsrc/_DEVELOPMENT/target/<target>/configuration/<target>_config.m4`. Some symbols are common to all targets; some are target-specific (e.g. `CRT_ORG_BSS_BANKED` for banked memory layouts).

### `#pragma redirect` — define weak aliases

`#pragma redirect SYMBOL=EXPRESSION` declares a function or variable as an alias. The most common use is to install your own interrupt handler:

```c
#pragma redirect CRT_INTERRUPT_HANDLER=my_isr
#pragma redirect CRT_INTERRUPT_HANDLER_EXIST=my_isr

void my_isr(void) {
    // ... called every 50 Hz interrupt
    // (you are responsible for swapping the I register and the AF/AF' alternates)
}
```

### `#pragma string` — name a string literal

`#pragma string NAME="text"` exposes the C string as `NAME` in the linker symbol table — used for metadata strings that the loader or appmake reads.

### Equivalent command-line flags

Any pragma can also be specified on the command line:

```bash
# Instead of #pragma output STACKPTR=0xFF57 in source:
zcc +zx -clib=new -pragma-define:STACKPTR=0xFF57 hello.c -o hello.bin -create-app

# Require a pragma symbol to be defined (errors if not used):
zcc +zx -clib=new -pragma-need:STACKPTR hello.c -o hello.bin -create-app
```

This is the canonical way to override CRT0 behavior in a Makefile without editing source files — e.g. switching between a RAM-resident build (at `24000`) and a ROM build (at `0000`) via `make RAM=1` / `make ROM=1`.

### Common `#pragma output` symbols for ZX Spectrum

| Symbol | Default | Purpose |
|---|---|---|
| `CRT_ORG_CODE` | 24000 (newlib), 30000 (classic) | Origin of the `code_zx` section. Override for custom loaders (e.g. Multiface slot, ROM-pack). |
| `CRT_ORG_BSS` | (computed) | Origin of `bss_zx`. Override to place uninitialized data in a banked page. |
| `REGISTER_SP` / `STACKPTR` | #FF57 | Initial stack pointer. |
| `CLIB_EXIT` | 0 (new), 1 (classic) | If 1, `main()` returns to a clean shutdown that swaps a stack frame and executes `RST 0` (or jumps to the Spectrum's `COPY_LINE` to return to BASIC). If 0, `main()` returns directly to the loader stub; in the 48K Spectrum case, the program ends but BASIC may be unstable. |
| `CLIB_STDIO_HEAP` | 0 (none) | Size in bytes of the stdio heap (for `fopen_zfile` etc.). |
| `CRT_ENABLE_RELOC` | 0 | If 1, CRT0 self-relocates on startup — required for ROMMable builds. |
| `CLIB_FOPEN_MAX` | 1 | Max simultaneously open files. |
| `CLIB_DEFAULT_SCREEN_MODE` | 0 | Enter this Spectrum mode (0/1/2) at startup. |
| `CRT_INTERRUPT_CLOSE` | 0 | If 1, disable interrupts at exit. |
| `CLIB_DISABLE_IBMCHARS` | 0 | If 1, strip IBM-PC glyphs 128–255 from default font (saves 256 bytes). |

> [!TIP]
> If a `#pragma output` symbol has no effect, check (a) that you are using the correct name — classic vs newlib differ, and (b) that the CRT0 actually reads it. Run `zcc -v` and grep for the CRT0 `.asm` file in the link step, then read that file to see which symbols it consults.

---

## Sections, Memory Layout, and Calling Conventions

### Sections

z88dk's assembler `z80asm` (and therefore `zcc`) is **section-aware**. A *section* is a named region of memory that the linker fills with code or data in the order it encounters them. The default section for the classic library is `code` (a flat blob); newlib uses **target-qualified section names**:

| Section | Contents | Default placement (`+zx`, newlib) |
|---|---|---|
| `code_zx` | Executable code, including CRT0. | Begins at `CRT_ORG_CODE` (default 24000). |
| `rodata_zx` | Read-only data: string literals, `const` globals, jump tables. | Concatenated after `code_zx`. |
| `data_zx` | Initialized writable data. | Concatenated after `rodata_zx`. |
| `bss_zx` | Uninitialized writable data (zero-filled at startup). | Concatenated after `data_zx`. |
| `smc_clib` | Self-modifying-code scratch space (rare). | After `bss`. |
| `HEAP_zx` | The `malloc` heap. | Grows down from `(STACKPTR - 32)`. |

For `+zx128` and `+zxn`, the suffix becomes `zx128` / `zxn` and additional banked sections (`bss_bank1_zx128`, `bss_bank2_zx128`, `bss_bank3_zx128`, `bss_bank6_zx128`, `bss_bank7_zx128`) cover the contended banks 1/2/3/6/7. The linker fills the home bank first, then spills into the banked sections in numerical order.

In assembly source, you switch sections with the `SECTION` directive:

```z80
SECTION code_user
PUBLIC my_function
my_function:
    ld a, 1
    ret

SECTION rodata_user
PUBLIC my_string
my_string:    defm "Hello", 0

SECTION bss_user
PUBLIC my_buffer
my_buffer:    defs 256
```

In C, you switch sections with `#pragma code <section-name>` (classic) or by declaring a variable with the section attribute (newlib):

```c
#pragma code code_user
void my_function(void) { ... }
#pragma code code_crt_init    // restore default

// newlib alternative:
__address(0x6000) uint8_t screen_at_6000[6144];  // raw address placement
```

### Calling conventions

z88dk supports four calling conventions. The choice is governed by **function attributes** in C and by **library variant** at link time. The library is built multiple times (once per convention) and the right one is selected by the linker based on your compile flags.

| Convention | Keyword | Caller / Callee stack cleanup | Argument passing | Typical use |
|---|---|---|---|---|
| `__z88dk_fastcall` | `__z88dk_fastcall` | n/a (1 arg, no stack) | One 8/16/32-bit argument in A, DEHL, or on stack (float) | Single-argument functions; **zero stack overhead**. |
| `__z88dk_callee` | `__z88dk_callee` | **Callee** pops arguments | Multi-arg; rightmost in HL/DE/BC, rest on stack | Library functions; smallest + fastest multi-arg convention. |
| `__smallc` (sdcc) / `__smallc` (sccz80) | `__smallc` | **Caller** pops | Left-to-right push | Standard for many classic-library functions. |
| `__stdc` | `__stdc` | **Caller** pops | Right-to-left push (C89/C99 ABI) | When interop with other Z80 C compilers is required. |

Example:

```c
// Fastcall: argument in DEHL (16-bit) or L (8-bit).
uint8_t  read_port(uint8_t port) __z88dk_fastcall;
uint16_t read_addr(uint16_t addr) __z88dk_fastcall;

// Callee: caller pushes args, callee pops them. Faster code at call sites.
void fill_rect(int x, int y, int w, int h, uint8_t color) __z88dk_callee;

// Default (no attribute): classic library uses __smallc, newlib uses __z88dk_callee.
void mylib_init(void);  // subject to -clib=... default
```

### Mixing C and assembly

The standard idiom: declare the assembly function `PUBLIC` in `.asm` and `extern` in C, then either link them or use z88dk's inline assembly:

```c
extern uint8_t in_(uint16_t port) __z88dk_fastcall;  // port in DE

// Inline assembly within C source (sccz80 syntax):
#asm
PUBLIC get_high_score
get_high_score:
    ld hl, (_high_score)
    ret
#endasm
```

With `-compiler=sdcc`, inline assembly syntax differs slightly (`__asm` / `__endasm`):

```c
__asm
PUBLIC set_border_color
set_border_color:
    ld a, (COLOR)
    out (254), a
    ret
__endasm
```

---

## ZX Spectrum Library APIs

The real selling point of z88dk over standalone SDCC or hand-written assembly is the **library**: tens of thousands of lines of pre-written, hand-optimized assembly routines covering graphics, sound, input, file I/O, math, text, and platform-specific hardware. This section catalogs the most useful APIs for the ZX Spectrum target.

Headers are in `include/`; the canonical entry point is `<arch/zx.h>` (target-specific) and `<stdio.h>` / `<graphics.h>` / `<games.h>` / `<sound.h>` (portable).

### `<arch/zx.h>` — ZX Spectrum primitives

```c
#include <arch/zx.h>

// Direct access to memory regions:
extern uint8_t  zx_speakerpos[];   // 23692 (BORDCR / FRAMES1 byte 3)
extern uint8_t  zx_cx[];            // 23677 (COORDS-x)
extern uint8_t  zx_cy[];            // 23678 (COORDS-y)
extern uint8_t  zx_p(2,1);          // ATTR_P, ATTR (use the macros below)

void zx_border(uint8_t color);              // OUT (254),A with bits 0-2
void zx_paper(uint8_t color);               // PAPER color
void zx_ink(uint8_t color);                 // INK color
void zx_cls(void);                          // CLS via ROM 0D6Bh
void zx_cls_attr(struct zx_attr *attr);     // CLS with custom attribute
void zx_print_str(uint8_t x, uint8_t y, const char *s);  // LPRINT at coords
uint8_t zx_attr(uint8_t y, uint8_t x);      // read ATTR byte
uint8_t zx_attr_addr(uint16_t addr);        // address-to-ATTR helper
uint8_t zx_screenmode(uint8_t mode);        // 0/1/2 (Spectrum hi-res via ROM hack)
```

### `<arch/zx/esxdos.h>` — ESXDOS API (DivMMC, +3E, NEXT)

Direct calls into the ESXDOS ROM API for file I/O, directory enumeration, and the LFN (long filename) subsystem. Required if you target DivMMC hardware.

### `<graphics.h>` — portable primitives

Provides portable drawing routines shared across targets. On the Spectrum they fall back to the Speccy's pixel-address math:

```c
#include <graphics.h>

void clg(void);                                          // clear graphics screen
void plot(int x, int y);                                 // set pixel
void unplot(int x, int y);                               // clear pixel
void xorplot(int x, int y);                              // XOR pixel
int  point(int x, int y);                                // test pixel
void draw(int x1, int y1, int x2, int y2);               // draw line
void drawr(int dx, int dy);                              // draw relative
void drawto(int x2, int y2);                             // draw to absolute
void circle(int x, int y, int radius, int skip);         // circle (skip=1 dotted)
void undraw(int x1, int y1, int x2, int y2);             // clear line
void fill(unsigned char x, unsigned char y);             // flood fill
void stencil_init(struct stencil *st);                   // multi-outline fill
void stencil_add_point(struct stencil *st, int x, int y);
void stencil_render(struct stencil *st, unsigned char colour);
```

### `<arch/zx.h>` `zx_pattern_t` — tile blitting

The Spectrum-specific `zx_pattern_plot`, `zx_pattern_draw`, `zx_pattern_paint` family blits 8×8 tiles — useful for platform games, tile maps, and software sprites.

### `<games.h>` — input abstraction

```c
#include <games.h>

void  joystick(joy_funcs funcs);                          // install joystick handler
unsigned int  joystick_sc(unsigned int index);            // scan a joystick
unsigned int  get_stick_in(unsigned int index);           // poll
unsigned char get_fire_in(unsigned int index);            // fire button

// Pre-defined drivers (linked with -l<name>):
//   joystick(kempston);    joystick(sinclair1);   joystick(sinclair2);
//   joystick(fuller);      joystick(cursor);       joystick(opus);
//   joystick(swatch);      joystick(db23);         joystick(db9);

// Keyboard scanner
void  kbd_set_kbrepeat(uint8_t row, uint8_t mask);  // install hotkeys
unsigned int in_KeyPressed(unsigned int key);       // test unified keycode
unsigned int in_inkey(void);                       // ASCII or 0
void  in_wait_nokey(void);  void  in_wait_key(void);
```

### `<sound.h>` — beeper and AY driver

```c
#include <sound.h>
#include <arch/zx.h>

void bit_open(void);                // initialize beeper driver (call once)
void bit_click(void);               // toggle speaker once
void bit_noise(int duration, int period);   // white-noise burst
void bit_beep(int duration, int period);    // square wave
void bit_beepfx(int duration, int period, void (*wave)(int t));

// AY-3-8910 (Spectrum 128 / +2 / +3 / Next):
void ay_init();
void ay_reset();
void ay_snd_drum_taut();           // pre-built drum sounds
void ay_snd_drum_loose();
void ay_effect_1();
void ay_effect_2();
```

For music, the **`z88dk-vt`** (`VTII` player) and **`z88dk-pt`** (`ProTracker`) libraries are integrated — they accept compiled song modules and play them in the background via the AY interrupt.

### `<arch/zxn.h>` — ZX Spectrum Next

```c
#include <arch/zxn.h>

// Layer 2 (256×192×256 palette)
void zxnx_layer2_write(uint8_t row, uint8_t *buf, uint16_t n);
void zxnx_layer2_clear(uint8_t color);

// Hardware sprites (Next's 256 sprites)
void zxnx_sprite_setup(uint8_t sprite, uint8_t x, uint8_t y, uint8_t pattern);
void zxnx_sprite_show(uint8_t sprite, uint8_t show);

// Tilemap (80×60, 8bpp, two layers)
void zxnx_tilemap_setup(uint8_t rows, uint8_t cols);
void zxnx_tilemap_write(uint16_t offset, uint8_t tile);

// NextReg access
void zxnx_nextreg(uint8_t reg, uint8_t value);     // out (0x243B),reg : out (0x253B),val
uint8_t zxnx_nextreg_read(uint8_t reg);
```

### Fonts and text

```c
#include <font.h>
#include <arch/zx/fzx.h>

void_fzx_t *_fzx_fonts[] = { &font_8x8, &font_4x6, &font_6x8, &font_fzx }; // choices
void fzx_draw(struct fzx_state *fs, char c);
void fzx_set_buffer(struct fzx_state *fs, char *buf, uint16_t len);
void fzx_at(struct fzx_state *fs, int x, int y);
```

`fzx` is a free proportional font system introduced by z88dk that can render any arbitrary font file in the FZX format; the library bundles a handful of fonts (4×6, 6×8, 8×8 monospaced, plus proportional fonts).

### File I/O and streams

The classic library uses `fopen` / `fread` / `fwrite` with target-specific prefixes:

```c
FILE *f = fopen("K","foo.txt","r");   // 'K' = tape (classic Spectrum)
FILE *f = fopen("R","data.bin","w");   // 'R' = +3 DOS (DOS catalog)
FILE *f = fopen("I2","data.bin","r");  // 'I2' = IF1 microdrive 2
FILE *f = fopen("MD1","notes","a");    // 'MD1' = Opus Discovery

fclose(f);
fread(buf, 1, 256, f);
fwrite(buf, 1, 256, f);
```

Newlib uses the cleaner `fopen_zc` / `fopen_zx` / `fopen_esxdos` / `fopen_plus3` family, each returning a `FILE *` to a target-specific device driver.

---

## appmake and Output Formats

`z88dk-appmake` is the post-processor that converts a raw linked `.bin` (or `.ihx`) into the format a real Spectrum or emulator can actually load. It is normally invoked for you by `zcc -create-app`, but it can be run standalone for batch conversion, custom loaders, or post-mortem analysis.

### Invocation

```bash
z88dk-appmake +<target> [-subtype=<s>] [options]
```

### Common targets and subtypes

| Target | Subtype (`-subtype=`) | Output | Notes |
|---|---|---|---|
| `+zx` | (default) | `.tap` | BASIC loader: `LOAD ""CODE: RANDOMIZE USR <org>` — works on every Spectrum model. |
| `+zx` | `sna` | `.sna` | 48K SNA snapshot. |
| `+zx` | `tzx` | `.tzx` | TZX tape image (preserves turbo-load blocks). |
| `+zx` | `wav` | `.tap` + `.wav` | Audio file for real tape. |
| `+zx` | `bin` | `.bin` | Raw binary (passthrough — disables appmake processing). |
| `+zx` | `ts2050` | `.tap` | Use Ts2050-style turbo loader. |
| `+zx` | `main` | `.tap` | Stack-clearing loader variant. |
| `+zx` | `z80` | `.z80` | Z80 snapshot (v1/v2/v3 versions). |
| `+zx128` | (default) | `.tap` | Loader that also sets 7FFDh for banking. |
| `+zx128` | `sna` | `.sna` | 128K SNA snapshot (all 128K RAM banks). |
| `+zxn` | (default) | `.nex` | NEX (Next executable) — includes core 2/3 headers and optional palette/sprite/tilemap payloads. |
| `+zxn` | `sna` | `.sna` | Snapshot in 48K or 128K mode (no Layer 2 / NextReg restore). |
| `+3` | `+3dos` | `.dsk` | +3 DOS disk image. |
| `+cpm` | (default) | `.com` | CP/M `.COM` executable (raw, max 64K-256). |
| `+cpm` | `dsk` | `.dsk` | CP/M disk image (adds a PIP directory entry). |

### Useful appmake options

| Option | Effect |
|---|---|
| `-b <file>` / `--binfile <file>` | Input binary. |
| `-o <file>` / `--output <file>` | Output base name. |
| `-c` / `--crt0` | Embed the CRT0 origin in the loader. |
| `-r <addr>` / `--org <addr>` | Override origin. |
| `--blockname <name>` | Title shown in the tape header. |
| `--audio` | Generate matching `.wav` for tape targets. |
| `--ts2068hr` | For `+zx`: emit TS2068 hi-res mode toggle in loader. |
| `--diskfuel` | CP/M: write a blank formatted disk first. |
| `-ls` / `--list` | Inspect an existing binary's structure. |

### Direct invocation example

```bash
# Convert hello.bin (loaded at 0x8000) to a TAP with a custom block name:
z88dk-appmake +zx -b hello.bin -o hello --org 32768 --blockname "HELLO WORLD"

# Convert to SNA snapshot, requires knowing the binary's start address:
z88dk-appmake +zx -b hello.bin -o hello --subtype=sna --org 32768

# Convert to NEX for ZX Spectrum Next:
z88dk-appmake +zxn -b hello.bin -o hello --org 0x8000 --nex-header=5
```

### Standalone uses

`appmake` is also useful for tasks outside the normal `zcc` pipeline:

- **Tape image inspection**: `appmake +zx -ls --binfile foo.tap` decodes the blocks and prints their type, length, and flags.
- **Binary trimming**: `--org 24000 -r 24000` and a `.tap` subtype produces a loader that knows the true entry address.
- **Snapshot comparison**: `appmake +zx -ls` on two SNA files reveals at a glance which bytes differ.
- **Multifile disks**: `-Cz--dsk-create-empty` plus `-Cz--dsk-add` lets you compose a multi-file +3 disk.

---

## Worked Example: Hello, Spectrum

A complete first program that prints a centered greeting, draws a frame, plays a tone, and exits cleanly on any keypress.

### hello.c

```c
#include <arch/zx.h>
#include <input.h>
#include <sound.h>
#include <graphics.h>
#include <stdio.h>

#pragma output STACKPTR       = 0xFF57    // SP at top of BASIC RAM
#pragma output CLIB_EXIT      = 1          // clean return to BASIC
#pragma output CLIB_STDIO_HEAP = 1024       // for printf streams

int main(void) {
    zx_border(1);            // blue border
    zx_cls();                // clear screen

    // Print centered text at row 12, col 11:
    zx_print_str(11, 12, "Hello, Spectrum!");

    // Draw a frame around the text using portable graphics:
    draw(40,  80, 216,  80);     // top
    draw(216, 80, 216, 100);    // right
    draw(216, 100, 40, 100);    // bottom
    draw(40,  100, 40,  80);    // left

    // Short tone on the beeper (duration 500, period 2000):
    bit_open();
    bit_beep(500, 2000);

    // Wait for any key:
    in_wait_nokey();
    in_wait_key();

    zx_border(0);            // black border on exit
    return 0;
}
```

### Makefile

```makefile
ZCC      := zcc
TARGET   := +zx
CLIB     := new
CFLAGS   := -vn -O3 -clib=$(CLIB) -pragma-define:STACKPTR=0xFF57
LDFLAGS  := -lndos -lgfxspectrumsys

hello.tap: hello.c
	$(ZCC) $(TARGET) $(CFLAGS) hello.c -o hello.bin -create-app $(LDFLAGS)
	mv hello.tap $@

clean:
	rm -f hello.bin hello.tap hello.map zcc_opt.def hello.lm

run: hello.tap
	fuse-sdl $< || (echo "load fuse-sdl" && false)

.PHONY: clean run
```

### Build and run

```bash
make            # produces hello.tap
fuse hello.tap  # or ZEsarUX, UnrealSpeccy, etc.
```
In the emulator: type `LOAD ""` then press PLAY on the virtual tape, then `RANDOMIZE USR <org>` — but z88dk's appmake already wraps that in the loader, so just `LOAD ""` does everything.

### What the compiler emitted

Run `zcc -v +zx -clib=new hello.c -s -o hello.bin` to see the assembly output (`hello.asm`). You will find:

- A single `SECTION code_user` with the inlined `main`.
- Calls into `zx_cls`, `zx_print_str`, `draw`, `bit_beep`, `in_wait_key` (all library routines, all `__z88dk_callee` or `__z88dk_fastcall` — minimum stack traffic).
- A small CRT0 prologue that sets SP to #FF57, initializes bss to zero, calls `_main`, then returns to the loader.

The same source can be cross-compiled for the Spectrum Next by changing the target and adding a `+zxn` include:

```bash
zcc +zxn -clib=new -O3 hello.c -o hello.nex -create-app
```

---

## Comparison: z88dk vs Standalone SDCC

> [!TIP]
> **This section is the brief version.** For the canonical standalone SDCC reference — including the complete Z80-specific flag reference, the stack-based ABI, calling C from assembly and vice versa, custom CRT0, `.cdb` debug format and the `sdcdb` debugger, integration with SjASMPlus, and a worked bare-metal 48K Spectrum example — see [sdcc.md](sdcc.md). That article is the complement to this one: this article covers z88dk (which wraps SDCC); sdcc.md covers SDCC standalone.

SDCC (Small Device C Compiler) is the other major open-source C compiler that targets the Z80. z88dk actually *includes* SDCC as one of its two backends, so the comparison is really "use SDCC inside z88dk" vs "use SDCC standalone":

| Criterion | SDCC standalone | z88dk (with `-compiler=sdcc`) |
|---|---|---|
| **C compiler** | Upstream SDCC | Patched SDCC (z88dk fork) |
| **C library** | sdcc's own (small, portable, slow) | z88dk's newlib or classic (hand-optimized assembly) |
| **Code quality** | Good | Same as SDCC (compiler is identical) — *but* generated code calls into faster library functions |
| **Targets** | Z80, Z180, GBZ80, Rabbit 2000/3000, R800 — generic | +100 specific machines, including the entire ZX Spectrum family |
| **Output formats** | `.ihx` (Intel HEX) only | `.tap`, `.sna`, `.nex`, `.tzx`, `.dsk`, `.rom`, etc. via appmake |
| **Floating point** | sdcc's `_fadd`, `_fmul`, etc. | `math48`, `math32` (IEEE), `mbf32` — choice of math library |
| **Library API for ZX** | None | Full `<arch/zx.h>`, `<graphics.h>`, `<games.h>`, `<sound.h>` |
| **IDE integration** | Plain Makefile | zcc wraps SDCC; integrates with VS Code + DeZog + sjasmplus toolchain |
| **License** | GPL + some exceptions | The classic library is Clarified Artistic; newlib is BSD-like; the SDCC patches inherit SDCC's license |

**Bottom line**: if you are targeting the ZX Spectrum, use z88dk. Standalone SDCC's only advantage is for targets where z88dk's library doesn't exist (rare exotic Z80 hardware); even there, the patched SDCC inside z88dk is binary-identical in code generation.

## Comparison: z88dk vs Hand-Written Assembly (SjASMPlus)

| Criterion | Hand-written assembly (SjASMPlus) | z88dk (C + newlib) |
|---|---|---|
| **Development speed** | Slow; every byte counts. | Fast; 10× faster to write equivalent logic. |
| **Code size** | The minimum. | 2–5× larger for typical app logic; library routines add ~2 KB baseline. |
| **Code speed** | Whatever you write. | Slower for tight loops (compiler overhead), but library routines match hand-optimized assembly. |
| **Maintainability** | Poor; refactoring is painful. | Excellent; refactor freely. |
| **Reusability** | Poor; copy-paste heavy. | Excellent; standard C library, portable across targets. |
| **Hardware access** | Direct, no abstraction. | Direct via `<arch/zx.h>` macros or inline `__asm` blocks. |
| **Recommended for** | Demos, intros ≤4K, IRQ handlers, codec kernels, the inner loops of games. | Application logic, game engines, file/menu systems, loaders, tooling, anything ≥16K. |

The two are complementary, not exclusive. The standard idiom for a serious Spectrum project is to write the high-level logic in C with z88dk, profile, then rewrite the hot spots as SjASMPlus assembly linked in via `extern` declarations.

---

## When to Use z88dk

**Use z88dk when:**

- You want to write in C, period.
- You need to target multiple Z80 machines from one source tree (portability).
- You want benchmark-leading performance for things like `memcpy`, `printf`, `sqrt`, line drawing — without writing them yourself.
- You want a ZX Spectrum Next executable (`.nex`) with a single command.
- You are building a tool, a game engine, a menu system, a file browser, or anything more than a few KB.
- You want to bring up new hardware (RC2014, Z180 board) without writing yet another BIOS.
- You want to mix C and assembly in the same project.

**Do not use z88dk (use SjASMPlus directly) when:**

- You are writing a 1K/4K intro or a demo effect.
- Cycle-exact raster timing matters (IRQ handlers, cycle-stealing DMA emulation).
- You need a specific banking trick that the CRT0 doesn't support.
- You want full manual control of every byte.

---

## Best Practices

- **Start every project with `-clib=new`** unless you specifically need a target only the classic library supports. Newlib is faster, smaller, and better maintained.
- **Use `-pragma-define:`** rather than editing `#pragma output` in source for build-configuration switches. Keep source files build-system-agnostic.
- **Always emit a map file** (`-m`). The map is essential for debugging with DeZog or `z88dk-gdb`, and for sizing sections in CI.
- **Use `__z88dk_fastcall` on single-argument functions.** It eliminates stack traffic entirely. The compiler cannot infer this optimization automatically because the calling convention is part of the ABI.
- **Use `__z88dk_callee` on multi-argument hot functions.** Saves a `pop` per call site.
- **Make `bss` large, `data` small.** Initialized data costs bytes in the binary; uninitialized data is zero-filled at startup for free.
- **Use sections for memory placement.** Don't compute addresses in macros; declare `SECTION bss_bank1_zx128` and let the linker do the work.
- **Inline assembly for hardware access.** `__asm` / `__endasm` blocks within C functions are fine for one-off port writes; large routines should be separate `.asm` files.
- **Profile before optimizing.** Use `z88dk-ticks` to count T-states on isolated functions.
- **Pin a known z88dk nightly in CI.** The project ships frequent improvements; pinning prevents surprise regressions.

---

## Pitfalls

### Library selection

- **Mixing `-clib=classic` and `-clib=new` in one project is unsupported.** You cannot link a classic-library object file against newlib (or vice versa). The CRT0 startup files, calling conventions, and section names are all different.
- **Default library is `classic`.** New projects often forget `-clib=new` and silently get the slower library.
- **`-clib=new` is not the same as `-clib=new -compiler=sdcc`.** The former uses sccz80 + newlib; the latter uses SDCC + newlib. Different ABI choices, different code generation.

### Stack and RAMTOP

- **If you forget to set RAMTOP in the loader, BASIC and the C stack collide.** The CRT0 sets SP to `STACKPTR` (default `0xFF57`), but if your program is loaded at e.g. 24000 and the BASIC stack lives above 25000, you will overwrite BASIC and corrupt memory. Use `CLEAR 24000` in the loader, or `STACKPTR=0xFF57` if you keep BASIC usable.
- **The default `STACKPTR` of `0xFF57` is in the printer buffer area.** If you use the LPRINT-strap ROM routine or any ROM-based printer code, override with a lower value (e.g. `0xE000`) and adjust RAMTOP accordingly.
- **Recursion is dangerous.** The C stack lives in the same memory as the heap; deeply recursive C functions can overflow into the heap and silently corrupt data. Use iteration for unbounded depth.

### Section placement

- **The compiler does not warn when `bss` overflows the home bank.** If your uninitialized data exceeds the home bank on `+zx128`, the linker silently extends into banked sections — which works, but requires the runtime banking code (linked automatically by newlib). On classic, the data ends up in contended memory pages that the loader doesn't initialize.
- **`SECTION code_user` is a classic-library convention; newlib uses `code_zx`.** Mixing the two will produce "duplicate section" warnings.

### Code generation

- **`-O3` can occasionally produce larger code than `-O2`.** The aggressive inlining at level 3 trades size for speed. Try both if code size matters.
- **SDCC's switch-table optimization needs `-SO3`.** sccz80 defaults to a jump table; SDCC needs the explicit flag.
- **sccz80 does not understand C99 `__restrict`.** Use `__z88dk_fastcall` instead for the same intent.
- **Float variables silently pull in a full float library (~2 KB).** If you use one `float` anywhere, you pay for the entire math library. Use fixed-point (`int32_t` with manual scaling) if size matters.

### Build environment

- **`ZCCCFG` must point to `lib/config`.** Many "zcc: cannot find target" errors are a missing or stale `ZCCCFG`.
- **Building z88dk from source requires Boost for SDCC patching.** On Linux, install `libboost-all-dev` or use `build.sh --without-boost` to skip SDCC patching.
- **`#include <stdio.h>` in classic library pulls in the full FILE-based stdio** (~3 KB). Use `<stdio.h>`'s `printf` only when you actually need formatting; `zx_print_str` from `<arch/zx.h>` is much smaller.

### Mixing with assembly

- **Callee-saved registers differ between classic and newlib.** sccz80-classic preserves IY; SDCC+newlib uses IY as a frame pointer. If your assembly clobbers IY, declare it in the function attribute or `__asm` block.
- **`rst 0x08` (Spectrum ROM PRINT-A) and similar ROM calls trash AF, BC, DE.** Wrap them in `di`/`ei` if interrupts matter.
- **Assembly functions callable from C must end with `ret` and respect the declared calling convention.** A function declared `__z88dk_callee` that pops the wrong number of bytes will leave the stack desynchronized.

---

## Cross-References

- [Cross-Platform Toolchain](cross_platform_toolchain.md) — survey article that situates z88dk among all the cross-platform tools (SjASMPlus, SDCC, Pasmo, vasm, etc.)
- [sjasmplus.md](sjasmplus.md) — the natural complement: hand-written assembly for hot spots, IRQ handlers, and code that must fit in a tight space.
- [native_toolchain.md](native_toolchain.md) — the pre-cross-platform world (zeus, devpac/gens-mons, alasm+sts, xas). Useful context for understanding why z88dk's API design choices look the way they do.
- [../05_development/02_assembly/](../05_development/02_assembly/README.md) — Z80 assembly programming; see especially the planned `c_with_z88dk.md`, `c_with_sdcc.md`, and `mixed_c_asm.md` articles covering C-language development patterns and mixing C with assembly.
- [../08_reverse_engineering/](../08_reverse_engineering/README.md) — z88dk's `z88dk-dis` and `z88dk-ticks` are foundational tools for binary analysis.
- [../11_emulation/software/](../11_emulation/software/) — emulators (Fuse, ZEsarUX, CSpect) that load z88dk-produced `.tap` / `.sna` / `.nex` files.

---

## References

### Official

- [z88dk/z88dk on GitHub](https://github.com/z88dk/z88dk) — source repository, issue tracker, nightly builds.
- [z88dk wiki](https://www.z88dk.org/wiki/doku.php) — canonical documentation. Highlights:
  - [Platform: ZX Spectrum](https://www.z88dk.org/wiki/doku.php?id=platform:zx) — `+zx` and `+zx128` reference.
  - [Library: New (Development)](https://www.z88dk.org/wiki/doku.php?id=library:new) — newlib design notes.
  - [Toolchain: zcc](https://www.z88dk.org/wiki/doku.php?id=toolchain:zcc) — front-end flag reference.
- [Nightly builds](https://github.com/z88dk/z88dk/releases/tag/nightly) — Windows `.exe`, macOS `.pkg`, source tarball.

### Community

- [z88dk Discord](https://discord.gg/3SaFVhfd) — most active discussion; questions answered within hours.
- [z88dk forum](https://z88dk.org/forum/) — historical questions, deeper threads.
- [r/zxspectrum](https://www.reddit.com/r/zxspectrum/) and [#ZXDev on Libera.Chat](https://web.libera.chat/) — broader Spectrum community.

### Tutorials and deep dives

- [z88dk examples directory](https://github.com/z88dk/z88dk/tree/master/libsrc/_DEVELOPMENT/EXAMPLES) — ~150 example programs, each with a one-line build command at the top.
- [z88dk-tools](https://github.com/z88dk/z88dk/tree/master/src/ticks) — `ticks` cycle-counter documentation.
- [arjunaecc/z88dk-tutorial](https://github.com/arjunaecc/z88dk-tutorial) — community-maintained walkthrough series.
- [The zx-spectrum-dev tag on Stack Overflow](https://stackoverflow.com/questions/tagged/zx-spectrum) — focused Q&A.

### Adjacent

- [SDCC](https://sdcc.sourceforge.net/) — the upstream of z88dk's `-compiler=sdcc`.
- [DeZog](https://github.com/mazog/DeZog) — VS Code debugger; consumes z88dk's `.map` and `.lbl` files.
- [ZX Spectrum Next](https://www.specnext.com/) — primary newlib hardware platform.

