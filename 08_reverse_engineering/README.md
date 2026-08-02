[← Plan](../PLAN.md) · [Reverse Engineering](README.md)

# Reverse Engineering

This directory covers ZX Spectrum reverse engineering: the complete workflow from snapshot to annotated disassembly, protection cracking, asset extraction, code compression analysis, and snapshot repair.

## Reading Order

Start with the methodology article (the high-level workflow), then use the practical articles as references for specific tasks.

| # | Article | Description |
|---|---|---|
| 1 | [methodology.md](methodology.md) | RE workflow hub: starting points (tape/disk/snapshot formats), snapshot-driven analysis, standard workflow, heuristics, patching, tools, pitfalls, ethics |
| 2 | [protection_techniques.md](protection_techniques.md) | Protection catalog: tape loaders (Speedlock, Alkatraz), disk schemes, NMI/snapshot defenses, memory integrity, code obfuscation, bypass techniques |
| 3 | [analysis_techniques.md](analysis_techniques.md) | Practical static/dynamic analysis: SkoolKit disassembly workflow, code/data separation, ROM call labeling, ZEsarUX/DeZog debugging, trace logging, reverse debugging, memory diffing |
| 4 | [protection_cracking.md](protection_cracking.md) | Byte-level cracking: Speedlock/Alkatraz decryption analysis, timing check bypass, disk protection defeat, NMI countermeasure defeat, clean snapshot technique |
| 5 | [game_reversing.md](game_reversing.md) | Game RE: engine identification (Ultimate, Ocean, Graftgold, Hewson), sprite/map/music ripping, cheat code creation, save game analysis, Z80-to-C reconstruction |
| 6 | [code_crunching.md](code_crunching.md) | Compression RE: packer survey (MegaLZ, HRUM, Hrust, ZX0), format identification, LZSS fundamentals, generic depacker template, overlap depacking |
| 7 | [snapshot_repair.md](snapshot_repair.md) | Fixing corrupted .SNA/.Z80: header validation, PC/SP repair, decompression error handling, format conversion (.SNA <-> .Z80), fixing mid-load crashes |

## Article Relationships

```
methodology.md (high-level workflow)
    |
    +-- analysis_techniques.md (how to disassemble and debug)
    |       |
    |       +-- game_reversing.md (what to do with the disassembly)
    |       +-- code_crunching.md (handling compressed data)
    |
    +-- protection_techniques.md (what protections exist)
    |       |
    |       +-- protection_cracking.md (how to crack them)
    |
    +-- snapshot_repair.md (fixing broken files)
```

> **Scope note**: Articles 1-2 are general references. Articles 3-7 are practical tutorials with worked examples and code. Cross-reference tables at the end of each article link to related content across the knowledge base.
