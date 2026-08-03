[← Plan](../../PLAN.md) · [Interrupts](README.md)

# Development — Interrupt Programming

This series covers ZX Spectrum interrupt programming from the ground up: the foundational IM1/IM2 mechanics, then specialized topics including raster-synchronized multicolor, NMI and the Multiface, demoscene IM2 effect patterns, disk-load-with-AY-music concurrency math, and the advanced multi-source interrupt models on the ZX Spectrum Next and TS-Conf.

## Reading Order

| # | Article | Description |
|---|---|---|
| 1 | [interrupt_programming.md](interrupt_programming.md) | Foundational reference: IM1/IM2 mechanics, 257-byte vector table, ISR design patterns, T-state budgets, contention, cookbook, antipatterns |
| 2 | [race_the_beam.md](race_the_beam.md) | Raster-synchronized multicolor: 8×8 constraint reframed, T-state budget per scanline, 5 sync strategies (HALT, floating bus, port-#FF, line interrupt, copper), BIFROST* engine deep dive |
| 3 | [nmi.md](nmi.md) | NMI vs INT, Multiface hardware (74LS74 flip-flops), 4 NMI-safe code rules, NMI during common operations, DivIDE/ESXDOS magic button |
| 4 | [im2_effects.md](im2_effects.md) | Demoscene IM2 patterns: vector table placement rules, 15-game disassembly survey (256 vs 257-byte tables), 3 manager patterns (direct/JP/Hudson Hawk), 5 ISR effect catalog |
| 5 | [im2_disk_music.md](im2_disk_music.md) | Disk load with AY music: WD1793 byte budget, Ivan Roshchin concurrency math (Pentagon 48.83 Hz, 9.77 interrupts/rev), 3 workaround patterns, Western DOS comparison |
| 6 | [im2_advanced.md](im2_advanced.md) | Advanced platforms: Next hardware IM2 mode (core 3.02+), TS-Conf separate vectors, copper vs ISR decision matrix, Hudson Hawk bank-switching ISR, sample-rate ISRs |

## Cross-Reference Table

| This series | Canonical reference |
|---|---|
| [interrupt_programming.md](interrupt_programming.md) | [z80_interrupts.md](../../01_cpu/z80_interrupts.md), [video_frame_overview.md](../05_display_and_timing/video_frame_overview.md), [ula_timing.md](../../02_hardware/original/ula_timing.md) |
| [race_the_beam.md](race_the_beam.md) | [video_frame_overview.md](../05_display_and_timing/video_frame_overview.md), [ula_timing.md](../../02_hardware/original/ula_timing.md), [clone_timing.md](../../02_hardware/clones/clone_timing.md) |
| [nmi.md](nmi.md) | [multiface.md](../../03_io/peripherals/multiface.md), [divide_divmmc.md](../../03_io/storage/divide_divmmc.md) |
| [im2_effects.md](im2_effects.md) | [bank_switching_patterns.md](../03_memory_and_io/bank_switching_patterns.md), [system_variables.md](../../04_operating_systems/system_variables.md) |
| [im2_disk_music.md](im2_disk_music.md) | [trdos_programming.md](../08_dos_tape/trdos_programming.md), [fdc_vg93.md](../../03_io/storage/fdc_vg93.md), [ay_3_8912.md](../../06_sound/hardware/ay_3_8912.md) |
| [im2_advanced.md](im2_advanced.md) | [video_frame_next.md](../05_display_and_timing/video_frame_next.md), [memory_and_io_next.md](../03_memory_and_io/memory_and_io_next.md), [ay_3_8912.md](../../06_sound/hardware/ay_3_8912.md) |

> **Scope note**: Article 1 is the canonical foundation — read it first. Articles 2-6 are specialized deep dives that build on article 1's IM2 mechanics. The CPU-level interrupt architecture (IFF1/IFF2, bus cycles, acknowledge timing) is covered in [z80_interrupts.md](../../01_cpu/z80_interrupts.md); this series focuses on the programmer's practical perspective with working code, real-game disassembly data, and demoscene patterns.
