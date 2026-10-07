[← Home](../../README.md) · [Operating Systems](README.md)

# NedoOS — a Multitasking OS for ZX Clones, Still Shipping

**NedoOS** is a **multitasking operating system** for ZX Spectrum-family clones that have large memory and a block device (SD card or IDE disk). It runs on the **ATM Turbo 2** and on the **ZX Evolution / ATM Turbo 3** board, boots directly from FAT media, and — unusually for anything in this ecosystem — is in **active nightly development** (its release archive of October 2026 carries 6,648 files, kernels dated within days). For the ZX-Evo owner it is the modern general-purpose OS alongside [TS-Conf](../../02_hardware/newgen/ts_conf.md)'s Wild Commander ecosystem.

## Where to Get It

One rolling archive, always the latest build, on two mirrors: [nedoos.ru/images/release.zip](http://nedoos.ru/images/release.zip) (preferred) and [kulich.su/images/release.zip](http://kulich.su/images/release.zip). There is no version number — a download is identified by its checksum and the newest internal file date. The project site is [nedoos.ru](http://nedoos.ru/); the sources live in an official SVN (`svn://nedoos.ru/nedoas/nedoas`).

## What Is in the Release

The archive **is a ready SD card**: copy the folders plus exactly one kernel file to a FAT card's root and boot from it. The kernel `.$C` files are board-specific:

| Kernel | Board / device |
|---|---|
| `sd_boot.$C`, `sd_bootesp.$C` | ZX-Evo (BaseConf), Z-Controller SD; the `esp` variant drives an ESP network module on the COM port instead of the Wiznet card |
| `osatm3sd.$C`, `osatm3hd.$C` | ATM3 (ZX-Evo) with SD or Nemo IDE |
| `osatm2hd.$C`, `osatm2hdesp.$C`, `osatm2hm.$C`… | ATM Turbo 2, ATM IDE |

`bin/` carries ~156 programs: the shell (`term.com`, `cmd.com`), the Norton-style file manager `nc.com`, the `texted.com` editor, compilers and assemblers, **network tools** (`wizcfg`, `ping`, `telnet`, `wget`, IRC and FTP clients, and `moon.com` — the **Moon Rabbit** Gopher-style web browser by Alexander Nihirash), **emulators of other machines** (`z80.com`, `x86.com`, `vic20.com`), and the ZEXALL/ZEXDOC CPU test suites. `doc/` holds the manual (`nedoas_en.md`) and the API texts (`api_base.txt`, `api_net.txt`); `ini/` holds network and association settings.

## System Facts (from the manual)

- **Drive letters**: `A`–`D` TR-DOS floppies; `E`–`H` IDE master; `I`–`L` IDE slave; **`M` the Z-Controller SD card** (the ZX-Evo's card); `N` the NeoGS SD card; `O` USB flash.
- **Up to 16 tasks**, 8 open FAT files, 8 TR-DOS files, 8 pipes.
- On the ZX-Evo the keyboard comes **only from the AVR's PS/2 scancodes** — there is no matrix keyboard path.
- Recommended companions: Kempston mouse, DDp 4+4+4 palette, Mr. Gluk's RTC, ZXNETUSB, General Sound / NeoGS, TurboSound FM.

## Music Players — and a Naming Trap

| Program | Plays | Hardware |
|---------|-------|----------|
| `ngsplay.com` | `.S3M`, `.MOD`, `.MP3` | **NeoGS** — the OS uploads its own driver to the card, which does the mixing |
| `modplay.com`, `ptgs.com` | MOD / PT | — |
| `cdplay.com` | Audio CD | an ATAPI CD drive |
| `pt.com`, `tgvplay.com`, `rcpplay.com`, … | assorted tracker formats | — |

> [!WARNING]
> **`moon*.com` is not MoonSound.** The `moon.com` / `moonua.com` / `moonue.com` files are the *Moon Rabbit browser* — nothing to do with the OPL4 card. The release contains **no MoonSound player at all** (checked on both mirrors): no `.MWM`/MoonBlaster/OPL support; the nearest thing is the NeoGS player above.

## Emulation Notes

- Boot needs only the matching `.$C` kernel plus `bin/term.com`, `cmd.com` and `autoexec.bat` in a host folder — the OS formats nothing itself.
- The `esp` kernel variants speak the ESP serial protocol over the board's COM port (the same link the ATM Turbo 2+ drives through its i8031 keyboard controller) — an emulation of the serial path is enough for the network stack.
- NedoOS does **not** boot from or read data CDs; its `cdplay.com` is audio-only (see [cdrom_ide.md](../03_io/storage/cdrom_ide.md)).

---

## Cross-References

- [BaseConf](../../02_hardware/newgen/baseconf.md) / [ZX Evolution](../../02_hardware/newgen/zx_evo.md) — the primary host board
- [ATM Turbo](../../02_hardware/clones/atm_turbo.md) — the second host family
- [esxdos.md](esxdos.md), [is_dos.md](is_dos.md), [trdos.md](trdos.md) — the other ZX disk-OS lineages
- [GS / NeoGS](../../06_sound/hardware/gs_general_sound.md) — the sound card its flagship player targets

## References

- **[nedoos.ru](http://nedoos.ru/)** — project site and the rolling `release.zip` (facts above verified on the 2026-10-04 build: 31,016,955 bytes, SHA-256 `581abee8…d41dc97`)
- **`doc/nedoas_en.md`, `api_base.txt`, `api_net.txt`** — the manual and API texts inside the release
- **Moon Rabbit browser** — Alexander Nihirash, ships as `moon.com` in `bin/`
