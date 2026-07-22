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
| [debugging.md](debugging.md) | **Debugging** — the three-layer model: native monitor-debuggers (STS 5.0, MONS, Zeus Monitor), built-in emulator debuggers (ZEsarUX, Fuse, CSpect, UnrealSpeccy, ZXMAK2, MAME), and source-level / IDE-integrated debuggers (DeZog, z88dk-gdb, z88dk-ticks, mainline GDB with the Z80 target merged July 2021, SpectNetIDE, tagged-source Fuse). Compiler integration deep dive — SLD (SjASMPlus), `.lis` + `.map` + `.list` (z88dk), DWARF (GAS), `.cdb` (SDCC) — and the CSpect debug pseudo-instructions (`break`, `exit`, `setbrk`, `clrbrk`). Comparison matrix across 8 debuggers, decision tree mermaid, three recommended end-to-end workflows (SjASMPlus+DeZog+ZEsarUX, z88dk+z88dk-gdb+Fuse, mainline GDB+DWARF), best practices, pitfalls, and bidirectional cross-references to sjasmplus.md and z88dk.md. |
| [asset_tools.md](asset_tools.md) | **Asset Pipeline** — the three-stage model (authoring → conversion → integration). Screen graphics: `.scr` (6912 B), `.sch`, `.nic` (Next layer 2), `.chk` formats; ZX Paintbrush, SevenUp, png2scr, zx-modules, ZX Spectrumizer. Software sprites: unmasked / pre-shifted / masked / aligned / attribute-aware layouts; hardware sprites (Next, 64 sprites, 4-bpp/8-bpp). Fonts: 8×8 fixed-width (768 B, ROM-compatible) vs FZX proportional (full spec, relocatable, up to 244 chars); FZX Editor, Fony, ZX Paintbrush, ttf2fzx. Music: AY-3-8910 trackers (Vortex Tracker II `.pt3`, Arkos Tracker 2 `.akg`/`.akm`) and 1-bit beeper engines (Beepola, BeepFX); ayFX for SFX. Compression: ZX0 / ZX1 / ZX2 / ZX7 family (Einar Saukas), MegaLZ, LZSA, APLIB, RCS preprocessing, executable packers. Tile maps: Tiled + Python scripts, Next hardware tilemap. Comparison matrix, decision-tree mermaid, a full worked Makefile-driven pipeline, best practices, pitfalls, and cross-references. |
| [sdcc.md](sdcc.md) | **SDCC** — the canonical reference for using the Small Device C Compiler standalone (without z88dk's `zcc` wrapper). Z80 port history (2003 → 2025), installation, the complete toolchain (`sdcc`, `sdasz80`, `sdldz80`, `sdcdb`, `makebin`, `ucsim`), Z80-specific flag reference, the stack-based ABI (right-to-left push, caller-cleans, IX frame pointer), calling C from assembly and vice versa, custom CRT0, `.cdb` debug format and the `sdcdb` debugger, integration with SjASMPlus (`.rel` ↔ binary bridge), and a worked bare-metal 48K Spectrum example built end-to-end. Detailed comparison with z88dk's `-compiler=sdcc` wrapper (same backend, different library / CRT0 / output formats), a decision-tree mermaid, best practices, pitfalls, and bidirectional cross-references to z88dk.md and debugging.md. |

### Planned Deep Dives

Beyond the articles above and the two overviews, this directory will host detailed per-tool references. See [PLAN.md](../PLAN.md) for the full catalog. Planned topics include:

- **Native assemblers**: `zeus_assembler.md`, `devpac_gens_mons.md`, `alasm_sts.md`, `xas_assembler.md`, `tasm_native.md`, `zxasm_native.md`, `pikasm.md`, `laser_genius.md`, `avras.md`, `spectrum_basic_mcode.md`
- **Cross-platform assemblers**: `pasmo.md`, `z88dk_z80asm.md`, `vasm.md`, `wla_dx.md`, `zmac.md`, `zasm_kio.md`, `tniasm.md`, `rasm.md`, `sarcasm.md`, `tasm_cross.md`, `as_macro_assembler.md`
- **IDEs**: `zdevstudio.md`, `vscode_integration.md`, `zxdstudio.md`, `zx_spin.md`
- **C compilers**: `boriel_zxbasic.md`
- **Build and debug**: `testing.md`
- **Note**: `zezarux_debug.md` and `fuse_debug.md` are now covered by [debugging.md](debugging.md); `makefiles.md` is descoped (build system setup is not Spectrum-specific).

## Cross-References

- [05_development/02_assembly/](../05_development/02_assembly/README.md) — Z80 assembly programming concepts the toolchain supports
- [05_development/01_basic/](../05_development/01_basic/README.md) — Sinclair BASIC (the pre-assembler environment)
- [06_sound/trackers_and_formats/](../06_sound/trackers_and_formats/README.md) — music toolchain (trackers, module formats)
- [11_emulation/software/](../11_emulation/software/) — emulator deep dives (Fuse, ZEsarUX, CSpect)
