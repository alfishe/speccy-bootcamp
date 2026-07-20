[← Plan](../PLAN.md) · [Toolchain](README.md)

# Toolchain

This directory covers development tools: assemblers (native and cross-platform), IDEs, C compilers, build systems, debuggers, asset tools, and disassemblers.

## Start Here

Two overview articles survey the entire toolchain landscape:

| Article | Scope |
|---|---|
| [native_toolchain.md](native_toolchain.md) | **Native Toolchain** — assemblers, monitors, and editors that ran on the Spectrum itself (1982–2000s). Zeus, HiSoft DevPac / GENS-MONS, ALASM+STS, XAS, plus minor tools. The pre-assembler era, the editor workflow evolution, debugger traditions, and the Soviet vs Western toolchain split. |
| [cross_platform_toolchain.md](cross_platform_toolchain.md) | **Cross-Platform Toolchain** — modern ZX Spectrum development on PC, Mac, and Linux. SjASMPlus, z88dk, SDCC, Pasmo, vasm, WLA-DX, zmac, RASM. VS Code + DeZog + Klive IDE. Fuse, ZEsarUX, CSpect, JSSpeccy 3, MAME. Build systems, CI/CD, asset pipeline, recommended setup decision matrix, and a worked Hello World example. |

## Per-Tool Deep Dives (Planned)

Beyond the two overview articles, this directory will host detailed per-tool references. See [PLAN.md](../PLAN.md) for the full catalog. Planned topics include:

- **Native assemblers**: `zeus_assembler.md`, `devpac_gens_mons.md`, `alasm_sts.md`, `xas_assembler.md`, `tasm_native.md`, `zxasm_native.md`, `pikasm.md`, `laser_genius.md`, `avras.md`, `spectrum_basic_mcode.md`
- **Cross-platform assemblers**: `sjasmplus.md`, `pasmo.md`, `z88dk_z80asm.md`, `vasm.md`, `wla_dx.md`, `zmac.md`, `zasm_kio.md`, `tniasm.md`, `rasm.md`, `sarcasm.md`, `tasm_cross.md`, `as_macro_assembler.md`
- **IDEs**: `zdevstudio.md`, `vscode_integration.md`, `zxdstudio.md`, `zx_spin.md`
- **C compilers**: `z88dk.md`, `sdcc.md`, `boriel_zxbasic.md`
- **Build and debug**: `makefiles.md`, `debugging.md`, `testing.md`, `zezarux_debug.md`, `fuse_debug.md`, `asset_tools.md`, `disassemblers.md`

## Cross-References

- [05_development/02_assembly/](../05_development/02_assembly/README.md) — Z80 assembly programming concepts the toolchain supports
- [05_development/01_basic/](../05_development/01_basic/README.md) — Sinclair BASIC (the pre-assembler environment)
- [06_sound/trackers_and_formats/](../06_sound/trackers_and_formats/README.md) — music toolchain (trackers, module formats)
- [11_emulation/software/](../11_emulation/software/) — emulator deep dives (Fuse, ZEsarUX, CSpect)
