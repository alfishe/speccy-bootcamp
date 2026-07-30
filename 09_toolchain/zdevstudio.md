[← Home](../README.md) · [Toolchain](README.md)

# zDevStudio — Z80 Development Studio (Pasmo-Based IDE)

**zDevStudio** (sometimes styled *ZXDevStudio* or *zDev Studio*) is an open source Z80 development environment built around the [Pasmo](pasmo.md) assembler. Registered on SourceForge on **22 February 2011** and last released at **version 0.8**, zDevStudio bundles a source editor, the Pasmo assembler, a basic emulator integration, sprite and screen editors, and (since 0.8) an internal disassembler into a single cross-platform application. It is licensed under **GPLv3** and built with **Lazarus / Free Pascal**, giving it native GTK+ binaries on Linux and Win32 binaries on Windows.

zDevStudio's historical role was **lowering the barrier to entry** for new Spectrum developers in the late 2000s and 2010s. At a time when assembling a Spectrum program meant installing a command-line tool, configuring a separate editor, finding a third-party emulator, and writing batch scripts to wire them together, zDevStudio offered a one-install, one-window workflow that was particularly attractive for **teaching, classroom use, and hobbyists transitioning from BASIC to assembly**.

> [!NOTE]
> zDevStudio is **not actively maintained** as of 2025 — the last binary release is 0.8, dating to the mid-2010s. For new projects, consider [Klive IDE](https://github.com/speccyfan/klive) or [VS Code with Z80 extensions](vscode_integration.md). This article is preserved for developers maintaining existing zDevStudio projects or evaluating it for educational use.

---

## Quick Start

### Installation

**Windows**: download the installer from the [SourceForge project page](https://sourceforge.net/projects/zdevstudio/) and run it. The installer bundles a static build of Pasmo, so no separate assembler installation is required.

**Linux**: download the `.tar.gz` for your architecture, extract it, and run the `zdevstudio` binary. The Linux build depends on `gtk2` and `libpasmo`; on modern distributions you may need to install `libgtk2.0-0` from your package manager.

**macOS**: no official binary is distributed. Because zDevStudio is built with Lazarus / Free Pascal, it can in principle be compiled from source on macOS, but this requires setting up the Lazarus IDE and rebuilding Pasmo as a static library. For macOS users, [VS Code with Z80 extensions](vscode_integration.md) is the recommended alternative.

### Hello World

1. Launch zDevStudio.
2. `File > New Project`. Choose a target format — for a Sinclair Spectrum program, choose **`.tap`** (tape image) or **`.bin`** (raw binary).
3. Paste the following source:

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
```

4. Press **F9** (or `Project > Build`). zDevStudio invokes Pasmo internally, displays assembly output in a pane at the bottom of the window, and writes the output file to the project directory.
5. Press **F5** (or `Project > Run`). zDevStudio launches its bundled emulator with the assembled program loaded at `#8000`. To invoke the routine from BASIC, type `RANDOMIZE USR 32768` in the emulator's BASIC prompt.

That is the entire workflow — no separate assembler invocation, no batch file, no manual emulator loading. This is the single biggest reason zDevStudio remained popular in classrooms long after more powerful toolchains became available.

---

## History and Design Philosophy

### The 2008–2012 IDE Wave

In the late 2000s and early 2010s, the Spectrum development scene saw a small wave of **integrated development environments** trying to bring the workflow experience of modern IDEs (Visual Studio, Eclipse, Xcode) to retro Z80 development. The wave included:

- **BASin** (Andrew Battersby, ~2003–2008) — a Sinclair BASIC IDE with assembler passthrough
- **SpectNetIDE** (Dotneteer, 2017–2020) — Visual Studio extension
- **ZX Spin** (Mark Woodmass / Dunny, 2004–2010) — emulator with built-in assembler ([separate article](zx_spin.md))
- **zDevStudio** (~2010–2015) — this article
- **Klive IDE** (Speccyfan, 2021–present) — the modern cross-platform successor

zDevStudio's distinguishing angle was that it was **cross-platform from day one** (Windows + Linux), explicitly GPLv3, and built around an existing mature assembler (Pasmo) rather than shipping its own. The choice of Lazarus / Free Pascal as the implementation language was deliberate — Lazarus applications compile to native code on both Win32 and GTK+ with minimal platform-specific code.

### Why Pasmo?

zDevStudio chose Pasmo as its backend for several reasons:

1. **Mature and stable** — Pasmo had been the de facto Spectrum cross-assembler since the early 2000s, with a clean codebase and predictable behavior
2. **Public domain** — no licensing friction for bundling
3. **Single binary** — Pasmo is a single statically-linked binary with no runtime dependencies, making it trivial to bundle inside an IDE
4. **Multiple output formats** — Pasmo directly emits `.tap`, `.tzx`, `.bin`, and raw snapshot formats, which meant zDevStudio did not need to write its own post-processing layer

This last point is important: by deferring all assembler behavior to Pasmo, zDevStudio's architecture stayed simple. Adding a new output format meant using the corresponding Pasmo flag rather than implementing new binary file writers.

### Version Timeline

| Version | Year (approx.) | Notable additions |
|---|---|---|
| 0.1–0.3 | 2010–2011 | Initial editor + Pasmo integration + `.tap` output |
| 0.4–0.5 | 2011–2012 | Sprite editor, screen designer, snapshot export |
| 0.6 | 2013 | Bundled emulator launch (basic — invoked a separate emulator binary) |
| 0.7 | 2014 | Project file format, multi-file projects |
| **0.8** | mid-2010s | **Internal disassembler**, bug fixes — last release |

Version 0.8 is the version most users will encounter on SourceForge as of 2025. The internal disassembler added in 0.8 was a significant addition — it allowed round-tripping between binary inspection and source editing without leaving the IDE.

### Why Development Stopped

zDevStudio's last binary release was around 2015–2016. Several factors contributed to development winding down:

- **Pasmo itself stagnated** — Pasmo's last meaningful release was around the same time, removing the upstream driver for IDE improvements
- **Rise of SjASMPlus** — SjASMPlus became the preferred assembler for serious Spectrum development, but zDevStudio was architecturally tied to Pasmo and would have needed a substantial rewrite to support multiple backends
- **VS Code ecosystem emerged** — by 2017–2018, VS Code with extension-based tooling became the obvious choice for cross-platform development, eroding the case for a custom IDE
- **No macOS build** — the lack of macOS binaries excluded a growing segment of retro-computing developers

Despite this, zDevStudio remained in classroom use well into the early 2020s because the single-application install was uniquely convenient for instructors.

---

## Architecture

zDevStudio is a **Lazarus / Free Pascal** application. The high-level architecture is:

```
┌─────────────────────────────────────────────────┐
│              zDevStudio GUI (LCL)                │
│  ┌───────────┐  ┌─────────┐  ┌──────────────┐ │
│  │ Source     │  │ Sprite  │  │ Disassembler │ │
│  │ editor    │  │ editor  │  │ view (v0.8+) │ │
│  └─────┬─────┘  └────┬────┘  └──────┬───────┘ │
│        │             │              │          │
│        └─────────────┴─────────┬────┘          │
│                                  │              │
│         ┌────────────────────┐   │              │
│         │ Build orchestrator │◀──┘              │
│         └─────────┬──────────┘                 │
│                   │                            │
│                   ▼                            │
│         ┌────────────────────┐                 │
│         │   Pasmo (bundled)  │                 │
│         │   .tap / .bin out  │                 │
│         └─────────┬──────────┘                 │
│                   │                            │
└───────────────────┼────────────────────────────┘
                    ▼
              Output file
              (launched in
               emulator)
```

The **build orchestrator** is the key component — it shells out to the bundled Pasmo binary, captures stdout/stderr, parses error messages into clickable editor locations, and writes the output file. The orchestrator's behavior mirrors the Pasmo command line, so experienced Pasmo users can predict zDevStudio's output exactly.

## Editor Features

The source editor in zDevStudio provides:

- **Z80 syntax highlighting** with separate color schemes for mnemonics, registers, labels, numbers, comments, and strings
- **Brace matching** for `(` `)` and inline expressions
- **Auto-indentation** that respects label field, opcode field, and operand field columns — a convention inherited from the Zilog-style source format
- **Comment toggle** (`Ctrl+.` or `Cmd+/`) on selected lines
- **Search and replace** with optional regex
- **Goto line** (`Ctrl+G`)
- **Bookmarks** — toggle on/off with `Ctrl+K n` (Borland-style), jump with `Ctrl+Q n`
- **Configurable tab width** (defaults to 8 spaces, common in Zilog-style source)

What it does **not** provide, compared to a modern editor like VS Code:

- No **language server** (no real-time error squiggles, no hover-for-documentation)
- No **rename refactoring** across files
- No **find all references** for a label
- No **integrated Git**
- No **terminal pane** for running external tools

These limitations are inherent to the era zDevStudio was built in — when VS Code eventually offered all of these via extensions, the case for a custom Z80 IDE became much weaker.

## Asset Editors

zDevStudio's bundled asset editors were one of its selling points:

### Sprite Editor

A small sprite editor for designing 8×8 or 16×16 sprites with attribute color. Output is emitted as Z80 `DB` statements or as a raw binary blob for inclusion with `INCBIN`. The editor supports:

- Pixel-level drawing with a 2× zoom view
- **Attribute color** editing per-character (foreground + bright + paper + flash)
- Mirror / rotate / invert transforms
- Multiple sprites in a single sheet (numbered or labeled)
- Export to `.asm` (`DB ...` statements) or `.bin`

### Screen Designer

A full-screen Spectrum attribute/pixel editor for designing complete 256×192 loading screens, UI mockups, or static backgrounds. Supports:

- Two editing modes: **pixel mode** (drawing with attributes inherited from current cell) and **attribute mode** (painting attributes over existing pixels)
- The **two-color-per-8×1-cell constraint** of the Spectrum display is enforced visually
- Import/export of `.scr` files (the standard 6912-byte Spectrum screen format — see [color_system](../05_development/05_display_and_timing/color_system.md) for details on the screen layout)
- Import of `.bmp`, `.png`, `.gif` with automatic color quantization to the Spectrum palette

### Memory Viewer

A live memory view of the running emulator, useful for inspecting VRAM state, stack contents, or custom data structures during debugging.

### Internal Disassembler (v0.8+)

Added in version 0.8, the internal disassembler accepts a binary file (or memory dump) and produces Z80 assembly source. This is essentially a graphical wrapper around a Z80 disassembler engine, similar in output style to [z80dasm](disassemblers.md). It is **not interactive** in the sense that IDA Pro or Ghidra are — you cannot rename labels, mark data blocks as arrays, or follow cross-references. It is a one-shot converter suitable for getting a starting point for analyzing a binary.

---

## Source Language (Pasmo Dialect)

Because zDevStudio delegates all assembly work to the bundled Pasmo binary, the source language is **exactly Pasmo's dialect** — documented in detail in [pasmo.md](pasmo.md). A quick summary:

- **Number formats**: `#FE` (Sinclair/Zilog), `$FE`, `0FEh`, `11111110b` — all accepted
- **Directives**: `ORG`, `END`, `DB`/`DW`, `EQU`, `INCLUDE`, `INCBIN`, `ALIGN`, `BINARY`, `OUTPUT` (Pasmo's directive to specify output filename inline)
- **Macros**: Pasmo supports a simple `MACRO`/`ENDM` block with positional parameters
- **Conditional assembly**: `IF`/`ELSE`/`ENDIF`
- **Output formats**: controlled by file extension (`.bin` → raw, `.tap` → Sinclair tape, `.tzx` → TZX tape) or by the project's Build Options dialog

What zDevStudio **adds** to Pasmo's plain-text command-line experience:

- A **project file format** (`.zdp`) listing source files, output filename, target format, and Pasmo flags
- A **Build Options** GUI for choosing output format without editing the source file's `OUTPUT` directive
- Per-project **include paths** for multi-file projects with shared headers

### Project File Format

A zDevStudio project (`.zdp`) file is an XML document storing the project configuration. A simplified example:

```xml
<?xml version="1.0"?>
<zdevproject version="0.8">
  <name>hello</name>
  <sources>
    <file>main.asm</file>
    <file>print.asm</file>
    <file>data.asm</file>
  </sources>
  <includepaths>
    <path>inc/</path>
  </includepaths>
  <output>hello.tap</output>
  <format>tap</format>
  <pasmo_flags>--nodbg --tzx</pasmo_flags>
  <emulator>/usr/bin/fuse</emulator>
</zdevproject>
```

The `<emulator>` field is the path to the external emulator binary that zDevStudio launches when you press **F5**. On a default Linux install, this is typically `/usr/bin/fuse` or `/usr/bin/zesarux`; on Windows it might be `C:\Spectrum\fuse.exe`. zDevStudio does not have a true built-in emulator — the bundled "emulator" is a minimal Spectrum ROM + RAM viewer that can run a program from `#8000`, sufficient for smoke-testing small routines but not for accurate timing-sensitive demos.

---

## When to Choose zDevStudio

### Recommended For

- **Classroom and workshop settings** where you want a single-application install with no command-line interaction
- **Hobbyists transitioning from Sinclair BASIC** who find a CLI toolchain intimidating
- **Maintaining existing zDevStudio projects** from the 2010s that are not worth migrating
- **Quick prototyping** of small routines (under 1 KB) where the overhead of setting up a modern toolchain is not justified

### Choose Something Else If

- You need **SjASMPlus-specific features** (modern directives, SNA-only extensions, ZX Spectrum Next support) — use [VS Code with extensions](vscode_integration.md) + SjASMPlus
- You need **source-level debugging** with breakpoints, watch expressions, and step-over — use [Klive IDE](https://github.com/speccyfan/klive) or [DeZog](https://github.com/maziac/DeZog) with VS Code
- You need **T-state metering** for cycle-counting-sensitive code — use [VS Code with Z80 Assembly Meter](vscode_integration.md#z80-assembly-meter)
- You are on **macOS** — zDevStudio has no official macOS build; use VS Code or Klive
- You need a **disassembler** for serious reverse engineering — use [SkoolKit](https://skoolkit.ca/) or [IDA Pro / Ghidra](disassemblers.md)
- You want **active maintenance** — zDevStudio's last release was 0.8 in the mid-2010s

### Comparison Matrix

| Feature | zDevStudio | VS Code + extensions | Klive IDE | SpectNetIDE | ZX Spin |
|---|---|---|---|---|---|
| **Cross-platform** | ⚠️ (Win + Linux only) | ✅ (Win/Mac/Linux) | ⚠️ (Win/Mac) | ❌ (Win + VS 2017/19) | ❌ (Win only) |
| **Single-install workflow** | ✅ | ❌ (multi-tool setup) | ✅ | ✅ | ✅ |
| **Underlying assembler** | Pasmo (bundled) | any (external) | Klive Z80 Asm | SpectNet Asm | built-in |
| **Source-level debugger** | ⚠️ (memory view only) | ✅ (DeZog) | ✅ | ✅ | ⚠️ (basic) |
| **T-state meter** | ❌ | ✅ (extension) | ⚠️ (planned) | ❌ | ❌ |
| **Sprite / screen editors** | ✅ | ❌ (external) | ⚠️ (planned) | ✅ | ⚠️ |
| **Internal disassembler** | ✅ (v0.8+) | ❌ (external) | ✅ | ✅ | ⚠️ |
| **Actively maintained** | ❌ (last release mid-2010s) | ✅ | ✅ | ❌ (last release ~2020) | ❌ (last release ~2015) |
| **License** | GPLv3 | MIT (core) | MIT | MIT | Freeware |

---

## Common Pitfalls

### 1. Trying to use SjASMPlus syntax

Because zDevStudio uses Pasmo under the hood, **SjASMPlus-specific directives are not recognized**. Common ones that fail:

| SjASMPlus directive | What happens in zDevStudio |
|---|---|
| `STRUCT`/`ENDSTRUCT` | Pasmo errors out — no struct support |
| `MMU` (ZX Next banking) | Not supported |
| `SAVESNA`/`SAVETAP` | Use Pasmo's file-extension convention instead (`.tap` output) |
| `ASSERT` | Not supported |
| `BLOCK` (size, fill) | Use `DB` with `DUP`-style macro, or define a byte array |

If your project requires these features, switch to [SjASMPlus directly](cross_platform_toolchain.md#sjasmplus-recommended-for-new-projects).

### 2. Expecting accurate emulation

zDevStudio's bundled "emulator" is a **smoke-test viewer**, not an accurate Spectrum emulator. It does not model:

- **Contention** (memory access timing on the upper RAM area)
- **Floating bus** effects
- **Multi-mode support** (128K banking, Pentagon, Scorpion, ZX Next)
- **Tape loading signals** beyond the initial program load

For any program that depends on cycle-exact behavior, set the external emulator (in the project file) to [Fuse](https://fuse-emulator.sourceforge.net/) or [ZEsarUX](https://github.com/chernoval/zesarux) and use the **F5** launch feature.

### 3. macOS rebuild attempts

zDevStudio's SourceForge page does not distribute macOS binaries. Attempting to rebuild from source on macOS involves:

1. Installing Lazarus via Homebrew (`brew install --cask lazarus`)
2. Cloning zDevStudio source (the repository is on SourceForge SVN)
3. Resolving GTK-specific calls in the source (the Linux build uses GTK widget bindings that may not cleanly map to Lazarus's macOS Carbon/Cocoa backend)
4. Rebuilding Pasmo as a 64-bit static library compatible with the IDE's calling convention

In practice, this is **several hours of work** with uncertain results. For macOS, use [VS Code with Z80 extensions](vscode_integration.md) — it is a one-command install via Homebrew.

### 4. Source files with non-ASCII encoding

The zDevStudio editor on Linux uses the system locale for source file I/O. If your source files contain UTF-8 characters (e.g., Cyrillic comments common in Russian-scene code shared via zDevStudio), the editor may display them incorrectly on a system with a non-UTF-8 locale. Set `LC_ALL=en_US.UTF-8` before launching zDevStudio to avoid this.

### 5. The list generation option documented for Pasmo does not work

Per a [2016 user review on SourceForge](https://sourceforge.net/projects/zdevstudio/reviews/), the listing-option flag that Pasmo supports on its command line is not exposed in zDevStudio's Build Options GUI. If you need a listing file (`.lst`), invoke Pasmo directly from a terminal alongside zDevStudio, or use the External Tools feature if your zDevStudio version supports it.

---

## FAQ

**Q: Is zDevStudio the same thing as ZXDevStudio?**
A: Yes. The project is variously styled *zDevStudio*, *ZXDevStudio*, *zDev Studio*, or *Z80 Development Studio*. The executable on all platforms is `zdevstudio`; the SourceForge project URL is `zdevstudio`; the documentation title is *zDevStudio - Z80 Development Studio*. This article uses *zDevStudio* throughout for consistency with the canonical SourceForge spelling.

**Q: Is zDevStudio related to ZXDStudio?**
A: **No.** [ZXDStudio](https://zx-pk.ru/threads/12842-zx-disk-studio-programma-dlya-raboty-s-obrazami-diskov.html) (also written *ZX Disk Studio*) is a Russian-scene **disk image utility** for working with TR-DOS `.trd` disk images — it is unrelated to Z80 development. The similar names are coincidental.

**Q: Why doesn't zDevStudio ship with a more accurate emulator?**
A: Bundling a full-featured Spectrum emulator (Fuse, ZEsarUX) would have substantially increased the project's binary size and maintenance burden. The decision was to provide a minimal smoke-test viewer and let users configure an external emulator via the project file. This was a reasonable trade-off for the 2010s but is one of the reasons the IDE feels limited by modern standards.

**Q: Will zDevStudio ever get a 0.9 release?**
A: There is **no indication** of continued development. The project's SourceForge page shows no releases since 0.8, and the discussion forums have been quiet for years. If you need a maintained Z80 IDE, use [Klive IDE](https://github.com/speccyfan/klive).

**Q: Can I use zDevStudio with SjASMPlus instead of Pasmo?**
A: Not without modifying the source code. The build orchestrator passes arguments to the bundled Pasmo binary and parses Pasmo-style error messages. Switching to SjASMPlus would require forking zDevStudio and rewriting the orchestrator. Several community attempts to do this have been started but none have produced a maintained fork as of 2025.

**Q: Does zDevStudio support the ZX Spectrum Next?**
A: No. The ZX Spectrum Next requires SjASMPlus for its extended Z80N instruction set and `.nex` output format. zDevStudio is Spectrum 48K/128K only.

**Q: Where is the zDevStudio source code hosted?**
A: The canonical source repository is on SourceForge, accessible from the [project page](https://sourceforge.net/projects/zdevstudio/). It uses Subversion (SVN), not Git. The source is Lazarus / Free Pascal.

---

## Cross-References

- [Pasmo](pasmo.md) — the assembler bundled inside zDevStudio; detailed reference for the source dialect
- [zx_spin.md](zx_spin.md) — contemporary Windows-only IDE with built-in assembler (Spin's own, not Pasmo)
- [vscode_integration.md](vscode_integration.md) — modern replacement for zDevStudio on all platforms, especially macOS
- [cross_platform_toolchain.md](cross_platform_toolchain.md) — broader survey of cross-platform toolchain options
- [disassemblers.md](disassemblers.md) — alternatives to zDevStudio's internal disassembler
- [color_system](../05_development/05_display_and_timing/color_system.md) — Spectrum screen format details, relevant to the screen designer's `.scr` import/export
- [tap_format.md](../03_io/storage/tap_format.md) — details on the `.tap` output format produced by zDevStudio
- [trd_disk_format.md](../03_io/storage/trd_disk_format.md) — TR-DOS disk format (not produced by zDevStudio, but useful for understanding why ZXDStudio is sometimes confused with it)

---

## References

- **SourceForge project**: [zDevStudio - Z80 Development Studio](https://sourceforge.net/projects/zdevstudio/) — official download location, last binary release v0.8
- **License**: GNU General Public License version 3.0 (GPLv3)
- **Implementation language**: Lazarus / Free Pascal — cross-platform native-code application framework
- **Categories on SourceForge**: Cross Compilers, Assemblers, Disassemblers
- **Operating systems**: Linux (GTK+), Windows (Win32 / Aero)
- **User reviews on SourceForge**: [zDevStudio reviews page](https://sourceforge.net/projects/zdevstudio/reviews/) — two reviews as of 2025 (4.0/5 average)
- **User review (taylorjpt, 2025-05-12)**: notes good error trapping, easy to use, missing list generation option
- **User review (quitarzaan, 2016-03-25)**: confirms Pasmo listing option is not exposed
- **Registered on SourceForge**: 22 February 2011
