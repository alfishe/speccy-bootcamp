[← Home](../README.md) · [References](README.md)

# ZX Ports Full Table — Complete English Translation of Black_Cat's Port Guide

The complete English translation of **"Guide to the ZX Spectrum ports"** by Black_Cat (BC Info Guide #4, 2008, © Black_Cat, zx.clan.su) — the most exhaustive raw port table ever published for the ZX Spectrum family, covering every original Sinclair/Amstrad machine, the major Soviet clones, and more than thirty add-on interfaces. Each entry lists the canonical port address, the actual decoding mask, and the read/write function per machine. This is the lookup companion to [io_port_map.md](io_port_map.md), which adds annotations, register layouts, and conflict warnings; the concepts of partial address decoding are covered in [io_port_decoding.md](../05_development/03_memory_and_io/io_port_decoding.md).

> [!NOTE]
> **Translation fidelity.** Every port address, binary mask, model code, and function assignment is reproduced verbatim from the original. Russian-only comments are translated; spelling in function names is normalized ("Adress" → "Address", "managetment" → management); the original's typos in data values are preserved and flagged in [Translator's Notes](#translators-notes). The original file is preserved in the [tslabs/zx-evo repository](https://github.com/tslabs/zx-evo/blob/master/pentevo/docs/ZX/zx-ports-full-table.txt).

## How to Read the Table

Columns follow the original: **Port** (canonical hex address, decimal value in parentheses), **Address** (the full 16-bit pattern A15…A0 of the canonical port), **Decoding** (which lines the hardware actually compares), **Read** and **Write** (function per machine, in the source's own shorthand).

Within the address/decoding patterns:

- `x` — don't-care line: ignored by the hardware, generates mirrors
- `0` / `1` — line must be low / high for the port to respond
- `?` — decoding unknown or unverified
- **Uppercase letters** (`A`, `B`, `C`, …, `J`, `K`, `L`) — **variable bits**: address lines that are not compared but passed through to the device, typically selecting an on-chip register. In `xxxxxxxx0BAxxx11` (Beta 128 interface), the `B`/`A` lines pick one of four WD1793 registers
- `—` — no function on any listed machine

## Computer Model Codes

The parenthesized codes after each function name identify **which machines** implement that decoding variant:

| Code | Computer |
|------|----------|
| `1` / `+1` | ZX Spectrum (issue 1–2 / issue 3–6) |
| `2` | ZX Spectrum +128, +2 |
| `3` / `+3` | ZX Spectrum +2a, +2b / +3 |
| `4` | Timex Computer 2048 |
| `5` | Didaktik Gama |
| `6` | Scorpion ZS-256 Turbo+ |
| `7` | KAY-1024SL / Beta Turbo |
| `8` | Pentagon 128 (1991) |
| `9` | Profi-1 (v3.x) |
| `A` | ATM Turbo-2+ |
| `B` | Scorpion GMX |
| `C` | Quorum 128/+ |
| `D` | Pentagon-1024SL (ver. 28.09.2006) |

> [!WARNING]
> These codes are **clone-centric** and do not follow Sinclair model numbering: `7` is KAY (not Pentagon), `8` is Pentagon 128, `9` is Profi, `B` is Scorpion GMX, `C` is Quorum. Code ranges expand accordingly — e.g. `KeyTp(1,7-9)` on port `#FE` means ZX Spectrum (1), KAY (7), Pentagon 128 (8), Profi (9). Misreading this legend is the single most common error when quoting this table.

## Function Codes

| Code | Meaning |
|------|---------|
| `??` | Unknown decoding |
| `?5` | Decoding not confirmed for computer `5` (Didaktik Gama) |
| `*?` | Not confirmed that the peripheral attaches to the computer |
| `Atr` | Video attributes port |
| `Brd` | Border color port |
| `Key` | Keyboard port |
| `Kjoy` | Kempston joystick port |
| `Kmou` | Kempston mouse port |
| `Pag` | Memory paging port |
| `Pal` | Video palette port |
| `PLLFC` | RAM phase-locked-loop frequency control port |
| `Prn` | Printer port |
| `Reg` | Configuration/management port |
| `Shdw` | Shadow mode enable port |
| `Tp` | Tape port |
| `Trb` | Turbo mode port |
| `TRD` | TR-DOS mode port |
| `Vid` | Video mode port |

---

## System Ports

| Port | Address (A15–A0) | Decoding (A15–A0) | READ | WRITE |
|------|------------------|--------------------|------|-------|
| `#00` (0) | `xxxxxxxx00000000` | `xxxxxxxx00000000` | — | Reg(B) |
| | | `xxxxxxxx0xx0xxx0` | — | Pag(C) |
| `#7E` (126) | `xxxxxxxx01111110` | `xxxxxxxx0xx11xx0` | Key(C) | — |
| `#F6` (246) | `xxxxxxxx11110110` | `xxxxxxxxxxxx0110` | — | Brd(A) |
| `#FE` (254) | `xxxxxxxx11111110` | `xxxxxxxxxxxxxxx0` | KeyTp(1,7-9) Prn(7) | BrdTpSpk(1,7-9) |
| | | `xxxxxxxxxxxxxxx0` | Key(D) | BrdSpk(D) |
| | | `xxxxxxxxxxxxx110` | KeyTp(A) | BrdTpSpk(A) |
| | | `xxxxxxxxxx1xxx10` | KeyTpPrn(6) | BrdTpSpk(6) |
| | | `xxxxxxxx1xxxxxx0` | KeyTp(+1) | BrdTpSpk(+1) |
| | | `xxxxxxxx1xx11xx0` | KeyTp(C) | BrdTpSpk(C) |
| `#FF` (255) | `xxxxxxxx11111111` | `xxxxxxxxxxxxxxxx` | Atr(1-2) | — |
| | | `xxxxxxxxxxxxx111` | Atr(A) | — |
| | | `xxxxxxxxxx1xxx11` | Atr(6) | — |
| | | `xxxxxxxx????????` | Atr(4,5) | Vid/Pag(4/5) |
| `#1FFD` (8189) | `0001111111111101` | `0001xxxxxxxxxx0x` | — | PagPrn/FD(3/+3) |
| | | `00xxxxxxxxxxxx01` | — | Pag(7) |
| | | `00xxxxxxxx1xxx01` | Trb-OFF(6) | Pag(6) |
| | | `0x0xx111xx1xxx01` | — | Pag(?B) |
| `#78FD` (30973) | `0111100011111101` | `0x1xx000xx1xxx01` | — | Pag(?B) |
| `#7AFD` (31485) | `0111101011111101` | `0x1xx010xx1xxx01` | — | Vid(?B) |
| `#7CFD` (31997) | `0111110011111101` | `0x1xx100xx1xxx01` | — | Vid(?B) |
| `#7EFD` (32509) | `0111111011111101` | `0x1xx110xx1xxx01` | — | Rag(?B) *(sic)* |
| `#7FFD` (32765) | `0111111111111101` | `0xxxxxxxxxxxxx0x` | — | Pag(2,8,9,A) |
| | | `0xxxxxxxxxxxxx01` | — | Pag(D) |
| | | `0xxxxxxxxxx11x0x` | — | Pag(C) |
| | | `01xxxxxxxxxxxx0x` | — | Pag(3,?5) |
| | | `01xxxxxxxxxxxx01` | — | Pag(7) |
| | | `01xxxxxxxx1xxx01` | Trb-ON(6) | Pag(6) |
| | | `0x1xx111xx1xxx01` | — | Pag(?B) |
| `#80FD` (33021) | `1000000011111101` | `1x0xxxxxxxx11x0x` | — | CP/MPag(C) |
| `#DFFD` (57341) | `1101111111111101` | `xx0xxxxxxxxxxx0x` | — | Pag(9) |
| | | `1x0xx111xx1xxx01` | — | Pag(?B) |
| `#EFF7` (61431) | `1110111111110111` | `1110xxxxxxxx0xxx` | — | PagVidTrbReg(8) |
| | | `1110xxxxxxxx0xx1` | — | PagVidTrbReg(D) |

## Peripherals Ports

| Port | Address (A15–A0) | Decoding (A15–A0) | READ | WRITE |
|------|------------------|--------------------|------|-------|
| `#1B` (27) | `xxxxxxxx00011x11` | `xxxxxxxx0xx11xx1` | Prn(C) | — |
| `#1F` (31) | `xxxxxxxx00011111` | `xxxxxxxxxxxxxxx1` | Kjoy(7) | — |
| | | `xxxxxxxxxx0xxxx1` | Kjoy(D) | — |
| | | `xxxxxxxx0xx11xx1` | KjoyPrn(C) | — |
| | | `xxxxxxxx0x0xxx11` | Kjoy(6) | — |
| `#1F`/`#3F`/`#5F`/`#7F` | `xxxxxxxx0BA11111` | `xxxxxxxx0xxxxxxx` | 8255(5) | 8255(5) |
| | | `xxxxxxxx0xxxxx11` | 8255(9) | 8255(9) |
| `#7B` (123) | `xxxxxxxx01111011` | `xxxxxxxxxxxxx011` | — | Prn(A) |
| | | `xxxxxxxx0xx110x1` | — | Prn(C) |
| `#FA` (250) | `xxxxxxxx11111010` | `xxxxxxxxxxxxx010` | IO(A) | IO(A) |
| `#FB` (251) | `xxxxxxxx11111011` | `xxxxxxxxxxxxx0xx` | Prn(8,D) | Prn(8,D) |
| | | `xxxxxxxxxxxxx011` | Prn(A) | PrnDAC(A) |
| | | `xxxxxxxx1xx110x1` | — | Prn(C) |
| `#0FFD` (4093) | `0000111111111101` | `0000xxxxxxxxxx0x` | Prn(?3/+3) | Prn(?3/+3) |
| `#2FFD` (12285) | `0010111111111101` | `0010xxxxxxxxxx0x` | — | 8272status(?+3) |
| `#3FFD` (16381) | `0011111111111101` | `0011xxxxxxxxxx0x` | 8272data(?+3) | 8272data(?+3) |
| `#7DFD` (32253) | `0111110111111101` | `0xxxxx0xxxxxxx0x` | ADC(A) | — |
| `#7FFD` (32765) | `0111111111111101` | `0xxxxx1xxxxxxx0x` | IDE,ADC(A) | — |
| `#BFFD` (49149) | `1011111111111101` | `10xxxxxxxxxxxx0x` | — | AYdat(2,3,?5,A) |
| | | `10xxxxxxxxxxxx01` | — | AYdat(7) |
| | | `1x1xxxxxxxxxxx0x` | — | AYdat(D) |
| | | `101xxxxxxxxxxx0x` | — | AYdat(8,9) |
| | | `101xxxxxxxx1xx0x` | — | AYdat(C) |
| | | `101xxxxxxx1xxx01` | — | AYdat(6) |
| `#FFDD` (65501) | `1111111111011101` | `xxxxxxxxxx0xxx01` | — | Prn(6) |
| `#FFFD` (65533) | `1111111111111101` | `11xxxxxxxxxxxx0x` | AYdat(2,3,?5,A) | AYadr(2,3,?5,A) |
| | | `11xxxxxxxxxxxx01` | AYdat(7) | AYadr(7) |
| | | `111xxxxxxxxxxx0x` | AYdat(8,9,D) | AYadr(8,9,D) |
| | | `111xxxxxxxx1xx0x` | AYdat(C) | AYadr(C) |
| | | `111xxxxxxx1xxx01` | AYdat(6) | AYadr(6) |

## Shadow Ports

ATM Turbo (A) software configuration ports, addressed in two dimensions: the port address itself and three strapping lines `L`, `K`, `J` decoded from the upper address bits. The `#xx77` family is write-only.

| Port | Address (A15–A0) | Decoding (A15–A0) | READ | WRITE |
|------|------------------|--------------------|------|-------|
| `#77` | `xxxxxxxx01110111` | `xxxxxxxx0xx10111` | — | VidTrbReg(A) |
| `#xx77` | `xLxxxxKJ01110111` | `xLxxxxKJ0xx10111` | — (write-only) | soft config (A) |
| `#3FF7`–`#FFF7` | `BA11111111110111` | `BAxxxx111xx10111` | — | RAMPag(A) |
| `#FEE7`/`#FFE7` | `1111111A11100111` | `xxxxxxxAxxx00111` | Reserved(A) | Reserved(A) |

Soft-port matrix — the `L`/`K`/`J` address bits select the function:

| Soft port | Decoding (A15–A0) | L | K | J | Effect |
|-----------|--------------------|---|---|---|--------|
| `#BD77`/`#FF77` (#0177) | `xLxxxxK10xx10111` | 0 | 0 | 1 | L,K=0 → Pal, PLLFC, shadow on |
| `#BF77`/`#FF77` | `xLxxxx110xx10111` | 0 | 1 | 1 | L=0 → Pal, PLLFC on |
| `#FD77`/`#FF77` (#4177) | `x1xxxxK10xx10111` | 1 | 0 | 1 | K=0 → shadow on |
| `#FE77`/`#FF77` | `x1xxxx1J0xx10111` | 1 | 1 | 0 | J=0 → paging off, CP/M ROM mapped to CPU banks 0–3 |

## SMUC — Scorpion & MOA Universal Controller

| Port | Address (A15–A0) | Decoding (A15–A0) | READ | WRITE |
|------|------------------|--------------------|------|-------|
| `#18E6`–`#7FFE` | `0ED11CBA111GF110` | ISA: `xx1IHGFEDCBA` | ISA:#200–#3FF | ISA:#200–#3FF |
| `#5FBA` (24506) | `0101111110111010` | `0x011xxx101xx010` | Version | — |
| `#5FBE` (24510) | `0101111110111110` | `0x011xxx101xx110` | Revision | — |
| `#7EBE` (32446) | `0111111010111110` | `0x111xx0101xx110` | 8259 | 8259 |
| `#7FBA` (32698) | `0111111110111010` | `0x111xxx101xx010` | VirtualFDD | VirtualFDD |
| `#7FBE` (32702) | `0111111110111110` | `0x111xx1101xx110` | 8259 | 8259 |
| `#D8BE` (55486) | `1101100010111110` | `1x011xxx101xx110` | IDE-Hi | IDE-Hi |
| `#DFBA` (57274) | `1101111110111010` | `1x011xxx101xx010` | DS1685RTC | DS1685RTC |
| `#F8BE`–`#FFBE` | `11111CBA10111110` | `1x111xxx101xx110` | IDE#1Fx/#3F6 | IDE#1Fx/#3F6 |
| `#FFBA` (65466) | `1111111110111010` | `1x111xxx101xx010` | SYS | SYS |

## Beta 128 Disk Interface

| Port | Address (A15–A0) | Decoding (A15–A0) | READ | WRITE |
|------|------------------|--------------------|------|-------|
| `#1F`/`#3F`/`#5F`/`#7F` | `xxxxxxxx0BA11111` | `xxxxxxxx0BAxxx11` | WD1793(6,7,8,D) | WD1793(6,7,8,D) |
| | | `xxxxxxxx0BAx11x1` | WD1793(C) | WD1793(C) |
| | | `xxxxxxxx0BA11111` | WD1793(A) | WD1793(A) |
| | | `0xxxxxxx0BAxxx11` | WD1793(9) | WD1793(9) |
| `#FF` (255) | `xxxxxxxx11111111` | `xxxxxxxx1xxxxx11` | FDsys(6,7,8,D) | FDsys(6,7,8,D) |
| | | `xxxxxxxx1xxx11x1` | FDsys(C) | FDsys(C) |
| | | `xxxxxxxx1xx11111` | FDsys(A) | FDsysPLLFC(A) |
| | | `0xxxxxxx111xxx11` | FDsys(9) | FDsys(9) |

## ATM IDE

| Port | Address (A15–A0) | Decoding (A15–A0) | READ | WRITE |
|------|------------------|--------------------|------|-------|
| `#FE0F`/`#FF0F` | `1111111A00001111` | `xxxxxxxA00001111` | IDEdat-Lo/Hi(A) | IDEdat-Lo/Hi(A) |
| `#FF2F` (65327) | `1111111100101111` | `xxxxxxxx00101111` | IDEerror(A) | IDEparam(A) |
| `#FF4F` (65359) | `1111111101001111` | `xxxxxxxx01001111` | IDEsect(A) | IDEsect(A) |
| `#FF6F` (65391) | `1111111101101111` | `xxxxxxxx01101111` | IDEstartsect(A) | IDEstartsect(A) |
| `#FF8F` (65423) | `1111111110001111` | `xxxxxxxx10001111` | IDEcyl-Lo(A) | IDEcyl-Lo(A) |
| `#FFAF` (65455) | `1111111110101111` | `xxxxxxxx10101111` | IDEcyl-Hi(A) | IDEcyl-Hi(A) |
| `#FFCF` (65487) | `1111111111001111` | `xxxxxxxx11001111` | IDEdevice(A) | IDEhead(A) |
| `#FFEF` (65519) | `1111111111101111` | `xxxxxxxx11101111` | IDEcomnd(A) | IDEstatus(A) |

## Peripheral Device Ports

| Port | Address (A15–A0) | Decoding (A15–A0) | READ | WRITE | Note |
|------|------------------|--------------------|------|-------|------|
| `#0B`/`#6B` (11/107) | `xxxxxxxx0AA01011` | `xxxxxxxx0Ax01011` | Z80DMA | Z80DMA | *1 |
| `#0E` (14) | `xxxxxxxx00001110` | `xxxxxxxx0000xxxx` | PC<->ZXDrBeep | PC<->ZXDrBeep | *2 |
| `#1F` (31) | `xxxxxxxx00011111` | `xxxxxxxxxx0xxxxx` | KempstonIF | — | *1 |
| | | `xxxxxxxx0xxxxxx1` | Kempston-M | — | *1 |
| | | `xxxxxxxx00011111` | AMIGA-MOUSE | — | *1 |
| `#3F` (63) | `xxxxxxxx00111111` | `xxxxxxxxx0xxxxxx` | LIGHT PEN | — | *1 |
| `#B7` (183) | `xxxxxxxx10110111` | `xxxxxxxx10110111` | XTR modem | XTR modem | |
| `#EF` (239) | `xxxxxxxx11101111` | `xxxxxxxx1xx01xxx` | C-DOS modem | C-DOS modem | |
| `#F7` (247) | `xxxxxxxx11110111` | `xxxxxxxxxxxx0xxx` | — | DIGITIZER(VMG) | |

## MB-02+ (*3)

| Port | Address (A15–A0) | Decoding (A15–A0) | READ | WRITE |
|------|------------------|--------------------|------|-------|
| `#0003`–`#0F03` | `xxxxDCBA00000011` | `xxxxDCBA0xx00011` | RTC-72421 | RTC-72421 |
| `#07` (11) *(sic)* | `xxxxxxxx00000111` | `xxxxxxxx0xx00111` | IDEcontrol | IDEcontrol |
| `#0B` (11) | `xxxxxxxx00001011` | `xxxxxxxx0xx01011` | Z80DMA | Z80DMA |
| `#0F`/`#2F`/`#4F`/`#6F` | `xxxxxxxx0BA01111` | `xxxxxxxx0BA01111` | WD2797 | WD2797 |
| `#13` (19) | `xxxxxxxx00010011` | `xxxxxxxx0xx10011` | FDcontrol | — |
| | | `xxxxxxxx00010011` | — | FDcontrol |
| `#17` (23) | `xxxxxxxx00010111` | `xxxxxxxx0xx10111` | memsel | memsel |
| `#1B`/`#3B`/`#5B`/`#7B` | `xxxxxxxx0BA11011` | `xxxxxxxx0BA11011` | 8255-2 | 8255-2 |
| `#1F`/`#3F`/`#5F`/`#7F` | `xxxxxxxx0BA11111` | `xxxxxxxx0BA11111` | 8255-1 | 8255-1 |
| `#A3`–`#BF` | `xxxxxxxx101CBA11` | `xxxxxxxx101CBA11` | IDE#1Fx | IDE#1Fx |

## NemoIDE

| Port | Address (A15–A0) | Decoding (A15–A0) | READ | WRITE |
|------|------------------|--------------------|------|-------|
| `#10`–`#F0` | `xxxxxxxxCBA10000` | `xxxxxxxxCBA10000` | IDE#1Fx | IDE#1Fx |
| `#11` (17) | `xxxxxxxx00010001` | `xxxxxxxxxxxxx001` | IDE-hi | IDE-hi |
| `#C8` (200) | `xxxxxxxx11001000` | `xxxxxxxxCBA01000` | IDE#3F6 | IDE#3F6 |

## SoundDrive v1.02

| Port | Address (A15–A0) | Decoding (A15–A0) | READ | WRITE |
|------|------------------|--------------------|------|-------|
| `#0F` (15) | `xxxxxxxx00001111` | `xxxxxxxxx0001111` | — | L channel A |
| `#1F` (31) | `xxxxxxxx00011111` | `xxxxxxxxx0011111` | — | L channel B |
| `#3F` (63) | `xxxxxxxx00111111` | `xxxxxxxxx0111111` | — | L Rg8255 |
| `#4F` (79) | `xxxxxxxx01001111` | `xxxxxxxxx1001111` | — | R channel C |
| `#5F` (95) | `xxxxxxxx01011111` | `xxxxxxxxx1011111` | — | R channel D |
| `#7F` (127) | `xxxxxxxx01111111` | `xxxxxxxxx1111111` | — | R Rg8255 |

## SoundDrive v1.05 (SoundDrive/Covox)

| Port | Address (A15–A0) | Decoding (A15–A0) | READ | WRITE |
|------|------------------|--------------------|------|-------|
| `#0F`/`#1F`/`#4F`/`#5F` | `xxxxxxxx0B0A1111` | `xxxxxxxxxB0Axxx1` | — | LA,LB,RA,RB |
| `#F1`/`#F3`/`#F9`/`#FB` | `xxxxxxxx1111B0A1` | `xxxxxxxxxxB0A1` | — | LA,LB,RA,RB |

## ZXMMC+ (*4)

| Port | Address (A15–A0) | Decoding (A15–A0) | READ | WRITE |
|------|------------------|--------------------|------|-------|
| `#1F` (31) | `xxxxxxxx00011111` | `xxxxxxxx00011111` | KempstonIF | CScard |
| `#3F` (63) | `xxxxxxxx00111111` | `xxxxxxxx00111111` | SPIRegRX | SPIRegTX |
| `#5F` (95) | `xxxxxxxx01011111` | `xxxxxxxx01011111` | RS232status | — |
| `#7F` (127) | `xxxxxxxx01111111` | `xxxxxxxx01111111` | RS232RegRX | RS232RegTX |

## Kempston Mouse Turbo by Velesoft (*1)

Address line A selects master (A=0) or slave (A=1) mouse.

| Port | Address (A15–A0) | Decoding (A15–A0) | READ | WRITE |
|------|------------------|--------------------|------|-------|
| `#1F`/`#7F` | `xxxxxxxx00011111` | `xxxxxxxx0AA11111` | AMIGAmou/FULLERjoy | — |
| `#7ADF`/`#FADF` | `1111101011011111` | `Axxxx0x011011111` | KmouTrb_B | — |
| `#7BDF`/`#FBDF` | `1111101111011111` | `Axxxx0x111011111` | KmouTrb_X | — |
| `#7EDF`/`#FEDF` | `1111111011011111` | `Axxxx1x011011111` | KmouTrb_detect | — |
| `#7FDF`/`#FFDF` | `1111111111011111` | `Axxxx1x111011111` | KmouTrb_Y | — |

## 8-bit IDE by Pera Putnik (*5)

| Port | Address (A15–A0) | Decoding (A15–A0) | READ | WRITE |
|------|------------------|--------------------|------|-------|
| `#2B`–`#EF` | `xxxxxxxxCB101A11` | `xxxxxxxxCBx0xAxx` | IDE#1Fx | IDE#1Fx |

## ZX LPRINT-III

| Port | Address (A15–A0) | Decoding (A15–A0) | READ | WRITE |
|------|------------------|--------------------|------|-------|
| `#7B` (123) | `xxxxxxxx01111011` | `xxxxxxxx0xxxx0xx` | ROMCS-off | /STROBE |
| `#FB` (251) | `xxxxxxxx11111011` | `xxxxxxxx1xxxx0xx` | — | DATA(/TxD) |
| | | `00xxxxxx1xxxx0xx` | ROMCS-on,BUSY,DSR | — |

## D40/80 (Didaktik 40/80)

| Port | Address (A15–A0) | Decoding (A15–A0) | READ | WRITE |
|------|------------------|--------------------|------|-------|
| `#81`/`#83`/`#85`/`#87` | `xxxxxxxx10000BA1` | `xxxxxxxx10000BA1` | WD2797 | WD2797 |
| `#89`/`#8B`/`#8D`/`#8F` | `xxxxxxxx10001xx1` | `xxxxxxxx10001xx1` | — | FDsys |
| `#91` (145) | `xxxxxxxx10010001` | `xxxxxxxx10010xx1` | — | 8255off&reset |
| `#99` (153) | `xxxxxxxx10011001` | `xxxxxxxx10011xx1` | — | 8255on |
| `#1F`/`#3F`/`#5F`/`#7F` | `xxxxxxxx0BA11111` | `xxxxxxxx0BAxxxxx` | 8255 | 8255 |

## divIDE (*1)

| Port | Address (A15–A0) | Decoding (A15–A0) | READ | WRITE |
|------|------------------|--------------------|------|-------|
| `#A3`–`#BF` | `xxxxxxxx101CBA11` | `xxxxxxxx101CBA11` | IDE#1Fx | IDE#1Fx |
| `#E3` (227) | `xxxxxxxx11100011` | `xxxxxxxx11100011` | — | divIDEcontrol |

## General Sound

| Port | Address (A15–A0) | Decoding (A15–A0) | READ | WRITE |
|------|------------------|--------------------|------|-------|
| `#B3` (179) | `xxxxxxxx10110011` | `xxxxxxxx10110011` | Data | Data |
| `#BB` (187) | `xxxxxxxx10111011` | `xxxxxxxx10111011` | Status | Comnd |

## +D (Issue 4)

| Port | Address (A15–A0) | Decoding (A15–A0) | READ | WRITE |
|------|------------------|--------------------|------|-------|
| `#E3`/`#EB`/`#F3`/`#FB` | `xxxxxxxx111BA011` | `xxxxxxxxx11BA01x` | WD1772 | WD1772 |
| `#E7` (231) | `xxxxxxxx11100111` | `xxxxxxxxx110011x` | — | romsel |
| `#EF` (239) | `xxxxxxxx11101111` | `xxxxxxxxx110111x` | — | FDsysLPTstrobe |
| `#F7` (247) | `xxxxxxxx11110111` | `xxxxxxxxx111011x` | LPTdata | LPTbusy |

## ZX Interface 1

| Port | Address (A15–A0) | Decoding (A15–A0) | READ | WRITE |
|------|------------------|--------------------|------|-------|
| `#E7` (231) | `xxxxxxxx11100111` | `xxxxxxxxxxx00xx1` | MicrodriveData | MicrodriveData |
| `#EF` (239) | `xxxxxxxx11101111` | `xxxxxxxxxxx01xx1` | Status | Comnd |
| `#F7` (247) | `xxxxxxxx11110111` | `xxxxxxxxxxx10xx1` | NetRS232Data | NetRS232Data |

## ZXMC-1 (ZX Multi Card-1 by Kamil Karimov, v1.2)

| Port | Address (A15–A0) | Decoding (A15–A0) | READ | WRITE |
|------|------------------|--------------------|------|-------|
| `#00EF` (239) | `0000000011101111` | `0000000011101111` | Version | — |
| `#00DF` (223) | `0000000011011111` | `0000000011011111` | Version | — |
| `#FE` (254) | `xxxxxxxx11111110` | `xxxxxxxx11111110` | Key | — |
| `#08EF`–`#0FEF` | `00001CBA11101111` | `00001CBA11101111` | SDcard | SDcard |
| `#80DF`–`#87DF` | `10000CBA11011111` | `10000CBA11011111` | PCKey | — |
| `#E0EF`–`#E7EF` | `11100CBA11101111` | `11100CBA11101111` | ZXMCRTC | ZXMCRTC |
| `#F8EF`–`#FFEF` | `11111CBA11101111` | `11111CBA11101111` | ISACOM1 | ISACOM1 |
| `#FADF` (64223) | `1111101011011111` | `1111101011011111` | Kmou_B | — |
| `#FBDF` (64479) | `1111101111011111` | `1111101111011111` | Kmou_X | — |
| `#FFDF` (65503) | `1111111111011111` | `1111111111011111` | Kmou_Y | — |

## ZXMC-2 (ZX Multi Card-2 by Kamil Karimov)

| Port | Address (A15–A0) | Decoding (A15–A0) | READ | WRITE |
|------|------------------|--------------------|------|-------|
| `#00F7` (247) | `0000000011110111` | `0000000011110111` | Version | — |
| `#FE` (254) | `xxxxxxxx11111110` | `xxxxxxxx11111110` | Key | — |
| `#08EF`–`#0FEF` | `00001CBA11101111` | `00001CBA11101111` | SDcard | SDcard |
| `#80DF`–`#87DF` | `10000CBA11011111` | `10000CBA11011111` | PCKey | — |
| `#BFF7` (49143) | `1011111111110111` | `1011111111110111` | GLUKRTCData | GLUKRTCData |
| `#DFF7` (57335) | `1101111111110111` | `1101111111110111` | — | GLUKRTCAddress |
| `#E0EF`–`#E7EF` | `11100CBA11101111` | `11100CBA11101111` | ZXMCRTC | ZXMCRTC |
| `#EFF7` (61431) | `1110111111110111` | `1110111111110111` | — | GLUKRTCon/off |
| `#F8EF`–`#FFEF` | `11111CBA11101111` | `11111CBA11101111` | ISACOM1 | ISACOM1 |
| `#FADF` (64223) | `1111101011011111` | `1111101011011111` | Kmou_B | — |
| `#FBDF` (64479) | `1111101111011111` | `1111101111011111` | Kmou_X | — |
| `#FFDF` (65503) | `1111111111011111` | `1111111111011111` | Kmou_Y | — |

## Keyboard Proface (*1)

| Port | Address (A15–A0) | Decoding (A15–A0) | READ | WRITE |
|------|------------------|--------------------|------|-------|
| `#FA` (250) | `xxxxxxxx11111010` | `xxxxxxxxxxxxx0x0` | — | Pro/Keyface |
| `#FE` (254) | `xxxxxxxx11111110` | `xxxxxxxxxxxxxxx0` | Pro/Keyface | — |

## SAM Coupe Sound SAA1099 (*1)

SAA1099 sound interface for the ZX Spectrum, named after the SAM Coupe's sound chip.

| Port | Address (A15–A0) | Decoding (A15–A0) | READ | WRITE |
|------|------------------|--------------------|------|-------|
| `#00FF` (255) | `0000000011111111` | `xxxxxxx011111111` | — | Data |
| `#01FF` (511) | `0000000111111111` | `xxxxxxx111111111` | — | Address |

## DMA USC (DMA Ultra Sound Controller)

| Port | Address (A15–A0) | Decoding (A15–A0) | READ | WRITE |
|------|------------------|--------------------|------|-------|
| `#0777`–`#3777` | `00BA011101110111` | `00BA0x1101110xxx` | — | Channel |
| `#0C77`–`#FC77` | `DCBA110001110111` | `DCBAxx0001110xxx` | 8237 | 8237 |
| `#3D77`–`#FD77` | `BA11110101110111` | `BAxxxx0101110xxx` | — | 8253-1 |
| `#3E77`–`#FE77` | `BA11111001110111` | `BAxxxx1001110xxx` | — | 8253-2 |
| `#3F77`–`#FF77` | `BA11111101110111` | `BAxx1x1101110xxx` | — | Volume |
| `#F777` (63351) | `1111011101110111` | `11xx0x1101110xxx` | — | DMAIntMask |

## COM Ports by VIC

| Port | Address (A15–A0) | Decoding (A15–A0) | READ | WRITE |
|------|------------------|--------------------|------|-------|
| `#80F7`–`#83F7` | `100000BA11110111` | `1000xxBAxxxx0xxx` | — | 8253 |
| `#90F7`/`#91F7` | `1001000A11110111` | `1001xxxAxxxx0xxx` | 8251-1 | 8251-1 |
| `#A0F7`/`#A1F7` | `1010000A11110111` | `1010xxxAxxxx0xxx` | 8251-2 | 8251-2 |
| `#B0F7`/`#B1F7` | `1011000A11110111` | `1011xxxAxxxx0xxx` | 8251-3 | 8251-3 |

## GLUK CMOS RTC

| Port | Address (A15–A0) | Decoding (A15–A0) | READ | WRITE |
|------|------------------|--------------------|------|-------|
| `#BFF7` (49143) | `1011111111110111` | `1011xxxxxxxx0xxx` | DS1685Data | DS1685Data |
| `#DFF7` (57335) | `1101111111110111` | `1101xxxxxxxx0xxx` | — | DS1685Address |
| `#EFF7` (61431) | `1110111111110111` | `1110xxxxxxxx0xxx` | — | on/off |

## Profi COM Port & Soft XT Keyboard

| Port | Address (A15–A0) | Decoding (A15–A0) | READ | WRITE |
|------|------------------|--------------------|------|-------|
| `#E0FB` (57595) | `1110000011111011` | `1110000x1xx1x011` | — | XTKey |
| `#E8FB` (59643) | `1110100011111011` | `1110100x1xx1x011` | Reg | Reg |
| `#EAFB`/`#EBFB` | `1110101A11111011` | `1110101A1xx1x011` | 8251 | 8251 |
| `#ECFB`–`#EFFB` | `111011BA11111011` | `111011BA1xx1x011` | 8253 | 8253 |

## ZX Interface 2

| Port | Address (A15–A0) | Decoding (A15–A0) | READ | WRITE |
|------|------------------|--------------------|------|-------|
| `#EFFE` (61438) | `1110111111111110` | `xxx0xxxxxxxxxxx0` | Right Joystick | — |
| `#F7FE` (63486) | `1111011111111110` | `xxxx0xxxxxxxxxx0` | Left Joystick | — |

## ISA COM1/Modem by Kondratyev (8250 / *82450 / *82550)

Address line A selects IRQ4-ON (A=0) or IRQ4-OFF (A=1).

| Port | Address (A15–A0) | Decoding (A15–A0) | READ | WRITE |
|------|------------------|--------------------|------|-------|
| `#F0EF`/`#F8EF` | `1111A00011101111` | `xxxxA000xxx0xxxx` | RBR/DivLchLSB | THR/DivLchLSB |
| `#F1EF`/`#F9EF` | `1111A00111101111` | `xxxxA001xxx0xxxx` | IER/DivLchMSB | IER/DivLchMSB |
| `#F2EF`/`#FAEF` | `1111A01011101111` | `xxxxA010xxx0xxxx` | IIR | — |
| `#F3EF`/`#FBEF` | `1111A01111101111` | `xxxxA011xxx0xxxx` | LCR | LCR |
| `#F4EF`/`#FCEF` | `1111A10011101111` | `xxxxA100xxx0xxxx` | MCR | MCR |
| `#F5EF`/`#FDEF` | `1111A10111101111` | `xxxxA101xxx0xxxx` | LSR | — |
| `#F6EF`/`#FEEF` | `1111A11011101111` | `xxxxA110xxx0xxxx` | MSR | — |
| `#F7EF`/`#FFEF` | `1111A11111101111` | `xxxxA111xxx0xxxx` | ScratchReg* | ScratchReg* |

## Kempston Mouse (*1)

| Port | Address (A15–A0) | Decoding (A15–A0) | READ | WRITE |
|------|------------------|--------------------|------|-------|
| `#FADF` (64223) | `1111101011011111` | `xxxxxx10xx0xxxxx` | Kmou_B | — |
| `#FBDF` (64479) | `1111101111011111` | `xxxxx011xx0xxxxx` | Kmou_X | — |
| `#FFDF` (65503) | `1111111111011111` | `xxxxx111xx0xxxxx` | Kmou_Y | — |

## USSR Kempston Mouse

The source's heading for a second hardware variant — same three ports, same buttons/X/Y protocol, **different decoding**, and not a looser one: this variant checks five lines uniformly (A10, A8, A7, A5, A0) against three to four on the interface above, giving **2,048 mirrors per port** versus 8,192 (`#FADF`) and 4,096 (`#FBDF`/`#FFDF`). The required `1` on A0 means it answers only on **odd** addresses — its mirror set never intersects the ULA's A0=0 decode space, whereas half of the original variant's mirrors are even addresses. The two variants therefore respond to overlapping but not identical address sets.

| Port | Address (A15–A0) | Decoding (A15–A0) | READ | WRITE |
|------|------------------|--------------------|------|-------|
| `#FADF` (64223) | `1111101011011111` | `xxxxx0x01x0xxxx1` | Kmou_B | — |
| `#FBDF` (64479) | `1111101111011111` | `xxxxx0x11x0xxxx1` | Kmou_X | — |
| `#FFDF` (65503) | `1111111111011111` | `xxxxx1x11x0xxxx1` | Kmou_Y | — |

---

## Footnotes (INFO)

Section markers `*1`–`*5` refer to the original's own information sources (several URLs have since gone offline; preserved verbatim as citations):

| Marker | Source |
|--------|--------|
| `*1` | [velesoft.speccy.cz/zxporty-cz.htm](http://velesoft.speccy.cz/zxporty-cz.htm) — Velesoft's ZX port list |
| `*2` | [zxspectrum.00freehost.com/zxpc.html](http://www.zxspectrum.00freehost.com/zxpc.html) — ZX-PC interface |
| `*3` | [8bc.com/sinclair](http://www.8bc.com/sinclair/index.html) — MB-02+ documentation |
| `*4` | [zxbada.bbk.org/zxmmc](http://www.zxbada.bbk.org/zxmmc/index.htm) — ZXMMC+ documentation |
| `*5` | [ppest.org/zx/simpif.htm](http://www.ppest.org/zx/simpif.htm) — Simple Interface (Pera Putnik IDE) |

## Translator's Notes

1. **`#7EFD` — `Rag(?B)`**: preserved verbatim; presumably a typo for `Pag(?B)`, matching the `#78FD`/`#7AFD`/`#7CFD` Byte paging-series pattern.
2. **MB-02+ `#07` decimal label**: the original prints `#07/11`; the decimal value of `#07` is 7, not 11. Preserved with a *(sic)* marker.
3. **`ScratchReg*` and `*82450/*82550`** in the ISA COM1 section: the asterisks are unexplained in the original; likely they mark register behavior specific to the enhanced 16450/16550-class UART variants.
4. **SoundDrive v1.05 second-row mask**: the original's decoding `xxxxxxxxxxB0A1` is 14 characters (all other masks are 16); preserved verbatim.
5. **Spelling normalization**: "Adress" → "Address", "managetment" → management, "Kamil' Karimov" → Kamil Karimov. No technical content changed.
6. **Legend placement**: the original places the COMPUTERS/CODES/INFO legends at the end of the file; this translation moves them up front for lookup convenience.

## References

- Original: Black_Cat, *BC Info Guide #4* (2008), [zx-ports-full-table.txt](https://github.com/tslabs/zx-evo/blob/master/pentevo/docs/ZX/zx-ports-full-table.txt) as preserved in the tslabs/zx-evo repository
- Author's site (historical): zx.clan.su
- Velesoft's ZX port list: [velesoft.speccy.cz/zxporty-cz.htm](http://velesoft.speccy.cz/zxporty-cz.htm)

## Cross-References

- [io_port_map.md](io_port_map.md) — annotated port reference built on this table: per-model deep-dives, register layouts, conflict warnings
- [io_port_decoding.md](../05_development/03_memory_and_io/io_port_decoding.md) — why partial decoding exists and how mirrors arise
- [memory_maps.md](memory_maps.md) — what the `Pag` ports actually switch, per machine
- [floating_bus.md](../05_development/05_display_and_timing/floating_bus.md) — the `#FF`/`Atr` attribute port in action
