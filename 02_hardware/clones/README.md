[← Home](../../README.md) · [Clone Hardware](README.md)

# Hardware — Soviet Clone Ecosystem

This directory covers Soviet ZX Spectrum clones: Pentagon, Scorpion, Kay, ATM Turbo, Profi, and dozens more.

---

## Articles

| # | Article | Description |
|---|---------|------------|
| 1 | [pentagon.md](pentagon.md) | The People's Spectrum: Mikhalchenkov's 1989 discrete-TTL Soviet clone, the most popular Spectrum ever built — 320-line / 48.83 Hz frame, zero memory contention, Beta 128 FDC + TR-DOS standard, Soviet demoscene target platform |
| 2 | [clone_timing.md](clone_timing.md) | Clone video timing — Pentagon, Scorpion, Kay, ATM Turbo, FPGA implementations, detection techniques |
| 3 | [clone_joysticks.md](clone_joysticks.md) | Clone joysticks: built-in Kempston on Pentagon/Scorpion/ATM, Beta 128 coexistence, two-player conventions, single-standard software culture |
| 4 | [atm_turbo.md](atm_turbo.md) | ATM Turbo: CP/M mode, 7 MHz turbo, 4 video modes (320×200 16-color, 640×200, 80×25 text), IDE controller, flexible memory paging, 64-color RGBI palette |
| 5 | [scorpion.md](scorpion.md) | Scorpion ZS-256: Serge Zonov / Leningrad lineage, true 48K timing (69,888 T-states), Shadow Service Monitor, port #1FFD turbo+extended paging, #FF floating bus (correct), SMUC ISA bridge, GMX 2 MB / 640×200×16, ProfROM |

> This directory is being populated. One article remains planned: `ula_replacements.md` (Soviet-made gate arrays like the Т34ВГ1, whose timing differences affect software compatibility). The originally planned `pentagon_1024.md`, `kay.md`, `profi.md`, `byte.md`, `other_clones.md`, and `sizif_harlequin.md` were **descoped** — their frame-timing and memory-paging content is already covered in [video_frame_other_soviet.md](../../05_development/05_display_and_timing/video_frame_other_soviet.md), [memory_and_io_pentagon.md](../../05_development/03_memory_and_io/memory_and_io_pentagon.md), [clone_timing.md](clone_timing.md), and [11_emulation/fpga/harlequin_sizif.md](../../11_emulation/fpga/harlequin_sizif.md). See [PLAN.md](../../PLAN.md) for details.
