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
| 6 | [pentagon_1024.md](pentagon_1024.md) | Pentagon 1024: EFF7 extended paging (74HC688 full decode, 64 banks), 1024SL integrated variant, port #77 turbo/SVGA/PS-2, detection routine |
| 7 | [kay.md](kay.md) | Kay 1024: Nemo 60-pin bus with digital RGB, #DFFD extended paging, 8-bit IDE controller (#A0-#B7), Kay 2006 NB CPLD video modes (GigaScreen, multicolor, 512×192) |
| 8 | [profi.md](profi.md) | Profi 5.03/1024: #DFFD multi-function register (banking + turbo + VGA + ROM bank), ISA bus, VGA output, paper-offset quirk (T=12,580 vs 14,335) |
| 9 | [byte.md](byte.md) | Byte 48/128: compact Ukrainian clone with minimal IC count (~28), 4464 DRAM, CMOS logic, 48K-exact timing, no contention |
| 10 | [other_clones.md](other_clones.md) | Leningrad (Pentagon precursor), Hobbit (educational), Mikrosha (state factory), Quorum 64/128/256 (T34VG1 gate array), LEC 48/528 (non-power-of-two RAM), Composite |
| 11 | [sizif_harlequin.md](sizif_harlequin.md) | Modern 48K recreations: Harlequin (Chris Smith, discrete CMOS, ~40 ICs) and Sizif-512 (Kladov, Altera MAX II CPLD, multi-machine 48K/128K/Pentagon) |

> Planned: `ula_replacements.md` (Soviet gate arrays — Т34ВГ1, etc.). See [PLAN.md](../../PLAN.md) for the full catalog.
