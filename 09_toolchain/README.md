[← Plan](../PLAN.md) · [Toolchain](README.md)

# Toolchain

This directory covers development tools: assemblers (native and cross-platform), IDEs, C compilers, build systems, debuggers, asset tools, and disassemblers.

## Start Here

Two overview articles survey the entire toolchain landscape:

| Article | Scope |
|---|---|
| [native_toolchain.md](native_toolchain.md) | **Native Toolchain** — assemblers, monitors, and editors that ran on the Spectrum itself (1982–2000s). Zeus, HiSoft DevPac / GENS-MONS, ALASM+STS, XAS, plus minor tools. The pre-assembler era, the editor workflow evolution, debugger traditions, and the Soviet vs Western toolchain split. |
| [cross_platform_toolchain.md](cross_platform_toolchain.md) | **Cross-Platform Toolchain** — modern ZX Spectrum development on PC, Mac, and Linux. SjASMPlus, z88dk, SDCC, Pasmo, vasm, WLA-DX, zmac, RASM. VS Code + DeZog + ASM Code Lens + Z80 Macro-Assembler + Z80 Assembly Meter + Hex Editor extensions. Standalone IDEs: Klive IDE (deep dive), SpectNetIDE, ZXDevStudio, ZX Spin. Fuse, ZEsarUX, CSpect, JSSpeccy 3, MAME. Disassemblers (z80dasm, IDA Pro, Ghidra) and hex editors. Build systems, CI/CD, asset pipeline, recommended setup decision matrix, and a worked Hello World example. |

## Per-Tool Deep Dives

| Article | Scope |
|---|---|
| [sjasmplus.md](sjasmplus.md) | **SjASMPlus** — the de facto standard Z80 cross-assembler. Three-pass assembly, virtual device mode (14 built-in machines), Lua 5.5 scripting, ZX Spectrum Next Z80N support, complete ZX Spectrum output directives (SAVESNA/SAVETAP/SAVETRD/SAVENEX), source-level debugging data, breakpoint list export, structures, modules, macros, fake instructions, and a comparison matrix against every alternative. |
| [z88dk.md](z88dk.md) | **z88dk** — the complete C development kit for the Z80 family. Two C compilers (sccz80 + patched SDCC), two standard libraries (classic + newlib), the `+target` system (~100 machines), the `zcc` front-end pipeline, sections and calling conventions, the full ZX Spectrum library API (`<arch/zx.h>`, `<graphics.h>`, `<games.h>`, `<sound.h>`, `<arch/zxn.h>`), `appmake` output formats, `#pragma output` symbols, mixing C with assembly, a worked example with Makefile, and pitfalls. |
| [disassemblers.md](disassemblers.md) | **Disassemblers** — from raw Z80 bytes to annotated source. Three approaches (linear, smart static, trace-driven) with a mermaid diagram. Tools covered: z80dasm (reversible with z80asm), z88dk-dis (multi-CPU + `.map` aware), z80dismblr / DeZog (code-flow-graph, MAME trace input), z80-smart-disassembler (Python, template-driven, string-aware), SkoolKit (the Spectrum-native toolkit with `.skool` file format and built-in cycle-exact Z80 simulator with MEMPTR/WZ + 128K banking), IDA Pro (no Hex-Rays decompiler for Z80), Ghidra (community Z80 module, undocumented-opcode caveats), Reko (.NET tracing). Comparison matrices (features, CPU coverage), a decision-tree mermaid, Fuse profiler + SkoolKit `trace.py` workflow, best practices, pitfalls, and cross-references. |

### Planned Deep Dives

Beyond the articles above and the two overviews, this directory will host detailed per-tool references. See [PLAN.md](../PLAN.md) for the full catalog. Planned topics include:

- **Native assemblers**: `zeus_assembler.md`, `devpac_gens_mons.md`, `alasm_sts.md`, `xas_assembler.md`, `tasm_native.md`, `zxasm_native.md`, `pikasm.md`, `laser_genius.md`, `avras.md`, `spectrum_basic_mcode.md`
- **Cross-platform assemblers**: `pasmo.md`, `z88dk_z80asm.md`, `vasm.md`, `wla_dx.md`, `zmac.md`, `zasm_kio.md`, `tniasm.md`, `rasm.md`, `sarcasm.md`, `tasm_cross.md`, `as_macro_assembler.md`
- **IDEs**: `zdevstudio.md`, `vscode_integration.md`, `zxdstudio.md`, `zx_spin.md`
- **C compilers**: `sdcc.md`, `boriel_zxbasic.md`
- **Build and debug**: `makefiles.md`, `debugging.md`, `testing.md`, `zezarux_debug.md`, `fuse_debug.md`, `asset_tools.md`

## Cross-References

- [05_development/02_assembly/](../05_development/02_assembly/README.md) — Z80 assembly programming concepts the toolchain supports
- [05_development/01_basic/](../05_development/01_basic/README.md) — Sinclair BASIC (the pre-assembler environment)
- [06_sound/trackers_and_formats/](../06_sound/trackers_and_formats/README.md) — music toolchain (trackers, module formats)
- [11_emulation/software/](../11_emulation/software/) — emulator deep dives (Fuse, ZEsarUX, CSpect)
