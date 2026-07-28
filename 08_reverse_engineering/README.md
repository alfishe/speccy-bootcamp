[← Plan](../PLAN.md) · [Reverse Engineering](README.md)

# Reverse Engineering

This directory covers ZX Spectrum reverse engineering: methodology, copy protection, disassembly, static/dynamic analysis, snapshot repair, and decompilation.

| # | Article | Description |
|---|---------|-------------|
| 1 | [methodology.md](methodology.md) | ZX Spectrum RE workflow: starting points (tape/disk/snapshot formats), snapshot-driven analysis, static analysis (disassembly, ROM-call recognition, asset detection), dynamic analysis (ZEsarUX, DeZog, trace logs, reverse debugging), heuristics (engine fingerprints, music players, asset formats), patching (NOPs, trampolines, xdelta), tools, pitfalls (SMC, multi-model code, anti-debugging), ethics tradition |
| 2 | [protection_techniques.md](protection_techniques.md) | Tape loaders (Speedlock, Alkatraz), disk schemes (weak bits, non-standard sectors), NMI/snapshot defenses, snapshot devices (Multiface, MAGIC button, Shadow Monitor), memory integrity checks, code obfuscation, and bypass techniques |

See [PLAN.md](../PLAN.md) for the full article catalog.