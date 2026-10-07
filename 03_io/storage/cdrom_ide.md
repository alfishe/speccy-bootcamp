[← Home](../../README.md) · [Storage](README.md)

# CD-ROM on the ZX Spectrum — ATAPI over IDE, the CD Boot Standard, and Audio CD

A Spectrum reading a **CD** is not a joke: from the ZX Evolution's Nemo IDE onward, every IDE-capable clone can host a PC ATAPI CD-ROM drive, and a small but real software corpus exists around it — including *Time Gal*, the first ZX game shipped on CD (185 MB of video), and **DNA OS**, an operating system distributed as a bootable ISO. This article covers how a CD drive talks over the Spectrum's 8-bit IDE ports, the **CD autorun standard** the ZX-Evo firmware implements, what real software sends to the drive, and how audio-CD playback works through the same cable.

> [!NOTE]
> The machine side (IDE port decodes, 16-bit word assembly, the board-by-board footprints) is covered in [ide_interface.md](ide_interface.md). This article is the CD-specific layer on top.

---

## ATAPI over the Spectrum's IDE

A CD drive on IDE does not use the ATA command set a hard disk uses; it speaks **ATAPI**: the host sends a **12-byte packet** (a SCSI command, e.g. READ(10)) through the IDE data register. Three facts make it work on an 8-bit machine:

- **Drive-type detection**: asked "who are you?" with the hard-disk command IDENTIFY (`#EC`), a CD drive refuses and leaves the signature **`#EB14`** in the cylinder registers — that is how software tells a CD from a disk without a driver table.
- **Sectors are 2048 bytes**, LBA-numbered from 0; the file system is **ISO 9660** (primary volume descriptor at sector 16 → root directory of fixed-size records).
- **Sense / unit attention**: after a failure the drive keeps an error code — "not ready, medium not present" means no disc; "unit attention, medium changed" fires once after an insert. Polling loops must consume both.

Any Spectrum IDE board can carry the drive; the ZX Evolution ships with it on the **slave** of its single connector, and the same ATAPI layer has been used on the Pentagon's Nemo boards, the ATM Turbo 2+ (via xBIOS), the Profi, the Scorpion SMUC, TS-Conf and the Sprinter (Flex Navigator's `CDPLAYER.FLX`).

## The CD Autorun Standard — `AUTORUN.ZX`

Published by Alone Coder in *Info Guide* #9 (2006) together with *Time Gal*, and adopted verbatim by the ZX-Evo's EVO Reset Service (**ERS**, the BaseConf start menu):

- The disc's **first data session** is read; the file **`AUTORUN.ZX`** in the **root directory** is loaded to **`#6000`** and jumped to **with interrupts off**.
- The file is **raw Z80 code, no header**, at most **32 KB** by the published standard (the ERS loader physically fits 34,816 bytes). Anything bigger must be loaded by the program itself with its own driver.

### What the ZX-Evo's "D. CD boot" actually does

Verified against the ERS source (`pentevo/rom/mainmenu/src/hdd_cd_boot.a80`, ERS 0.58.03):

1. Zeroes RAM pages 0, 1, 3, 4, 6, 7; applies the Setup turbo and memory mode; sets `SP = #6000`.
2. Copies the loader from ROM to **`#E800`** and runs it from RAM (the stack sits just below `#6000`).
3. Selects the drive — **hardwired at assembly time to the slave** (`device EQU #B0`): no master fallback, no menu.
4. Talks Nemo IDE ports (`#10`/`#11` data … `#F0` status), refuses IDENTIFY until it sees the `#EB14` signature, spins the drive up (START STOP UNIT), reads the TOC, finds the first data session, walks ISO 9660 to `AUTORUN.ZX`, loads and jumps.

> [!WARNING]
> **There is no way out.** A missing disc, the wrong disc, or a hard disk on the slave makes the ERS retry forever — only a good disc or a reset escapes. The loader is not ZX-Evo-specific either: it is the 2006 *Time Gal* loader byte for byte in the parts that talk to the drive.

## Real Software and Its Command Sets

| Software | What it is | ATAPI/ATA commands it sends |
|---|---|---|
| **ERS "D. CD boot"** (ZX-Evo) | autorun boot | ATA `#08`, `#EC`, `#A0`; packets TEST UNIT READY `#00`, SET CD SPEED `#BB`, READ(10) `#28`, READ TOC `#43` |
| ***Time Gal*** (ZX-Evo build) | first ZX game on CD (185 MB of video) | the same set (READ CD `#BE` only in commented-out code) |
| **DNA OS** | an OS shipped as a bootable ISO with its own ISO 9660 driver | binary only |
| **NedoVIDEO Player / ZX-video CD No. 1** | full-screen video from CD (Maksagor) | its own driver |
| **CDBOOT.COM** (iS-DOS) | boot shim for iS-DOS | its own driver |
| **xBIOS CD boot** (ATM Turbo 2+) | boot shim | MODE SENSE(10), READ CAPACITY, READ CD `#BE` |
| **NedoOS `cdplay.com`** | audio-CD player only (NedoOS does not boot or read data CDs) | PLAY AUDIO MSF `#47`, PAUSE/RESUME `#4B`, STOP `#4E`, READ SUB-CHANNEL `#42`, READ TOC |

A minimal data-CD drive implementation needs TEST UNIT READY, REQUEST SENSE, INQUIRY, READ CAPACITY, READ(10), READ TOC and the PACKET mechanics; audio playback adds the PLAY/PAUSE/STOP/SUB-CHANNEL family.

## Audio CD (CDDA) through the IDE cable

Audio playback is driven by MMC commands, not by reading sectors: PLAY AUDIO (MSF/LBA), PAUSE/RESUME, STOP, READ SUB-CHANNEL (position) and READ TOC — the drive's own DAC does the decoding. The semantics that bite implementations (per MMC-3):

- A **PLAY whose end lies past the lead-out plays to the session's lead-out** — refusing it (as naive drives do) breaks real players like the Sprinter's `CDPLAYER.FLX`, which routinely asks for `00:02:00 – 80:00:74`.
- A **data track inside the requested range** is refused with "end of user area encountered on this track" — but an MSF-addressed play still reproduces the audio before it.
- Output routing and volume go through MODE page `0Eh` (audio control): left/right channel routing and volume per channel, which is how software mixes CD audio against AY output.

Disc images that carry audio: ISO (data only), **CUE/BIN** (with MOTOROLA/WAVE track files, pregaps and postgaps), raw BIN, and MAME's CHD.

---

## Cross-References

- [IDE interfaces](ide_interface.md) — the board-level port maps ATAPI rides on
- [ZX Evolution](../../02_hardware/newgen/zx_evo.md) / [BaseConf](../../02_hardware/newgen/baseconf.md) — the ERS and Nemo IDE
- [Sprinter](../../02_hardware/newgen/sprinter.md) — CD-Player in the bundled software
- [esxdos.md](esxdos.md), [is_dos.md](is_dos.md) — the DOS side of optical storage

## References

- **The CD autorun standard** — Alone Coder, *Info Guide* #09 (2006): [about *Time Gal*, the first CD game for ZX](http://zxpress.ru/article.php?id=8645); [Video Player for ATM](https://zxpress.ru/article.php?id=8646)
- **ERS loader source** — `pentevo/rom/mainmenu/src/hdd_cd_boot.a80` (in [tslabs/zx-evo](https://github.com/tslabs/zx-evo)); *Time Gal* sources in `pentevo/z80_soft/timegal/`
- **Alone Coder's ZX page** (Time Gal, `TGCDBOOT.zip`, DNA OS ISO) — [alonecoder.nedopc.com/zx](http://alonecoder.nedopc.com/zx/); *Time Gal* ISO at [archive.org](https://archive.org/download/timegal-zx/timegal.iso)
- MMC-3 command semantics — the SCSI Multimedia Commands standard (PLAY AUDIO §5.13 and friends)
