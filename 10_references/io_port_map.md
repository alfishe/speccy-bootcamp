[← Home](../README.md) · [References](README.md)

# I/O Port Map — Complete ZX Spectrum Port Reference

Every I/O port across all ZX Spectrum models and clones, with decoding bitmasks and per-model applicability. The port tables are reproduced from **Black_Cat's ZX Ports Full Table** (BC Info Guide #4, 2008), preserved in the [tslabs/zx-evo repository](https://github.com/tslabs/zx-evo/blob/master/pentevo/docs/ZX/zx-ports-full-table.txt). Annotations and supplementary data (joystick, mouse, DivIDE, sound cards, ZX Spectrum Next) are from the [World of Spectrum ports reference](https://worldofspectrum.org/faq/reference/ports.htm) and community documentation.

> [!NOTE]
> For the *concepts* of partial address decoding (how mirrors work, why they matter), see [io_port_decoding.md](../05_development/03_memory_and_io/io_port_decoding.md). This article is the **lookup reference** — you come here to find which port does what on which machine.

---

## How to Read This Table

Each entry shows the **canonical port address**, the **binary address pattern** (A15–A0), and the **decoding mask** — which address lines the hardware actually checks. Lines marked `x` are don't-care; the peripheral ignores them.

```
Port     Address (A15–A0)  Decoding (A15–A0)  READ          WRITE
#FE      xxxxxxxx11111110  xxxxxxxxxxxxxxxx0  Key(Brd(Spk(
                            only A0 checked     keyboard)     border/speaker)
```

- **Address column**: the full 16-bit value on the bus for the canonical port.
- **Decoding column**: which bits the hardware actually compares. `x` = don't-care, `0` = must be low, `1` = must be high.
- **Fewer checked bits = more mirrors**. A port that checks only A0 (1 line) responds at 32,768 addresses. A port that checks 8 lines responds at 256 addresses.

### Model Codes

The parenthesized codes after each function indicate **which models** implement that particular decoding variant:

| Code | Model |
|------|-------|
| 1 | Sinclair ZX Spectrum 16K / 48K |
| 2 | Sinclair ZX Spectrum 128K "Toastrack" |
| 3 | Amstrad ZX Spectrum +2 (grey) |
| 4 | Amstrad ZX Spectrum +2A |
| 5 | Amstrad ZX Spectrum +3 |
| 6 | Scorpion ZS-256 |
| 7 | Pentagon 128K |
| 8 | Pentagon 512K / 1024K |
| 9 | Kay 1024 |
| A | ATM Turbo |
| B | Byte |
| C | Profi |
| D | Pentagon with EFF7 extension (ProfiScorp compatibility) |

> [!WARNING]
> The same port number can have **completely different functions** on different models. For example, `#1FFD` controls extended paging on the +2A/+3, but controls the Beta 128 FDC on the Pentagon/Scorpion. Always check model codes before using a port.

### Abbreviations

| Abbreviation | Full Name |
|---|---|
| Pag | Memory paging register |
| Reg | Configuration register |
| Brd | Border color |
| Spk | Speaker (beeper) |
| Tp | Tape (EAR/MIC) |
| Key | Keyboard |
| Prn | Printer |
| Vid | Video configuration |
| Trb | Turbo mode control |
| AYdat | AY-3-8912 / YM2149 data |
| AYadr | AY-3-8912 / YM2149 address select |
| FD | Floppy disk control |
| Kjoy | Kempston joystick |
| IDE | IDE hard disk interface |
| ADC | Analog-to-digital converter |
| PLLFC | Phase-locked loop floppy controller |
| Shdw | Shadow screen / video mode |

---

## Black_Cat's ZX Spectrum Ports — Complete Table

Source: Black_Cat, BC Info Guide #4, 2008 ([original](https://github.com/tslabs/zx-evo/blob/master/pentevo/docs/ZX/zx-ports-full-table.txt)). Model codes: 1=48K, 2=128K, 3=+2, 4=+2A, 5=+3, 6=Scorpion, 7=Pentagon, 8=Pentagon 512K, 9=Kay, A=ATM Turbo, B=Byte, C=Profi, D=Pentagon EFF7.

### System Ports

| Port | Address (A15–A0) | Decoding Mask | READ | WRITE |
|------|-------------------|---------------|------|-------|
| `#00` | `xxxxxxxx00000000` | `xxxxxxxx00000000` | — | Reg(B) |
| | | `xxxxxxxx0xx0xxx0` | — | Pag(C) |
| `#7E` | `xxxxxxxx01111110` | `xxxxxxxx0xx11xx0` | Key(C) | — |
| `#F6` | `xxxxxxxx11110110` | `xxxxxxxxxxxx0110` | — | Brd(A) |
| `#FE` | `xxxxxxxx11111110` | `xxxxxxxxxxxxxxxx0` | KeyTp(1,7-9) Prn(7) | BrdTpSpk(1,7-9) |
| | | `xxxxxxxxxxxxxxxx0` | Key(D) | BrdSpk(D) |
| | | `xxxxxxxxxxxxxx110` | KeyTp(A) | BrdTpSpk(A) |
| | | `xxxxxxxxxx1xxx10` | KeyTpPrn(6) | BrdTpSpk(6) |
| | | `xxxxxxxx1xxxxxx0` | KeyTp(+1) | BrdTpSpk(+1) |
| | | `xxxxxxxx1xx11xx0` | KeyTp(C) | BrdTpSpk(C) |
| `#FF` | `xxxxxxxx11111111` | `xxxxxxxxxxxxxxxx` | Atr(1-2) | — |
| | | `xxxxxxxxxxxxx111` | Atr(A) | — |
| | | `xxxxxxxxxx1xxx11` | Atr(6) | — |
| | | `xxxxxxxx????????` | Atr(4,5) | Vid/Pag(4/5) |
| `#1FFD` | `0001111111111101` | `0001xxxxxxxxxx0x` | — | PagPrn/FD(3/+3) |
| | | `00xxxxxxxxxxxx01` | — | Pag(7) |
| | | `00xxxxxxxx1xxx01` | Trb-OFF(6) | Pag(6) |
| | | `0x0xx111xx1xxx01` | — | Pag(?B) |
| `#78FD` | `0111100011111101` | `0x1xx000xx1xxx01` | — | Pag(?B) |
| `#7AFD` | `0111101011111101` | `0x1xx010xx1xxx01` | — | Vid(?B) |
| `#7CFD` | `0111110011111101` | `0x1xx100xx1xxx01` | — | Vid(?B) |
| `#7EFD` | `0111111011111101` | `0x1xx110xx1xxx01` | — | Rag(?B) |
| `#7FFD` | `0111111111111101` | `0xxxxxxxxxxxxx0x` | — | Pag(2,8,9,A) |
| | | `0xxxxxxxxxxxxx01` | — | Pag(D) |
| | | `0xxxxxxxxxx11x0x` | — | Pag(C) |
| | | `01xxxxxxxxxxxx0x` | — | Pag(3,?5) |
| | | `01xxxxxxxxxxxx01` | — | Pag(7) |
| | | `01xxxxxxxx1xxx01` | Trb-ON(6) | Pag(6) |
| | | `0x1xx111xx1xxx01` | — | Pag(?B) |
| `#80FD` | `1000000011111101` | `1x0xxxxxxxx11x0x` | — | CP/MPag(C) |
| `#DFFD` | `1101111111111101` | `xx0xxxxxxxxxxx0x` | — | Pag(9) |
| | | `1x0xx111xx1xxx01` | — | Pag(?B) |
| `#EFF7` | `1110111111110111` | `1110xxxxxxxx0xxx` | — | PagVidTrbReg(8) |
| | | `1110xxxxxxxx0xx1` | — | PagVidTrbReg(D) |

### Peripheral Ports

| Port | Address (A15–A0) | Decoding Mask | READ | WRITE |
|------|-------------------|---------------|------|-------|
| `#1B` | `xxxxxxxx00011x11` | `xxxxxxxx0xx11xx1` | Prn(C) | — |
| `#1F` | `xxxxxxxx00011111` | `xxxxxxxxxxxxxxxx1` | Kjoy(7) | — |
| | | `xxxxxxxxxx0xxxx1` | Kjoy(D) | — |
| | | `xxxxxxxx0xx11xx1` | KjoyPrn(C) | — |
| | | `xxxxxxxx0x0xxx11` | Kjoy(6) | — |
| `#1F`/`#3F`/`#5F`/`#7F` | `xxxxxxxx0BA11111` | `xxxxxxxx0xxxxxxx` | 8255(5) | 8255(5) |
| | | `xxxxxxxx0xxxxx11` | 8255(9) | 8255(9) |
| `#7B` | `xxxxxxxx01111011` | `xxxxxxxxxxxxx011` | — | Prn(A) |
| | | `xxxxxxxx0xx110x1` | — | Prn(C) |
| `#FA` | `xxxxxxxx11111010` | `xxxxxxxxxxxxx010` | IO(A) | IO(A) |
| `#FB` | `xxxxxxxx11111011` | `xxxxxxxxxxxxx0xx` | Prn(8,D) | Prn(8,D) |
| | | `xxxxxxxxxxxxx011` | Prn(A) | PrnDAC(A) |
| | | `xxxxxxxx1xx110x1` | — | Prn(C) |
| `#0FFD` | `0000111111111101` | `0000xxxxxxxxxx0x` | Prn(?3/+3) | Prn(?3/+3) |
| `#2FFD` | `0010111111111101` | `0010xxxxxxxxxx0x` | — | 8272status(?+3) |
| `#3FFD` | `0011111111111101` | `0011xxxxxxxxxx0x` | 8272data(?+3) | 8272data(?+3) |
| `#7DFD` | `0111110111111101` | `0xxxxx0xxxxxxx0x` | ADC(A) | — |
| `#7FFD` | `0111111111111101` | `0xxxxx1xxxxxxx0x` | IDE,ADC(A) | — |
| `#BFFD` | `1011111111111101` | `10xxxxxxxxxxxx0x` | — | AYdat(2,3,?5,A) |
| | | `10xxxxxxxxxxxx01` | — | AYdat(7) |
| | | `1x1xxxxxxxxxxx0x` | — | AYdat(D) |
| | | `101xxxxxxxxxxx0x` | — | AYdat(8,9) |
| | | `101xxxxxxxx1xx0x` | — | AYdat(C) |
| | | `101xxxxxxx1xxx01` | — | AYdat(6) |
| `#FFDD` | `1111111111011101` | `xxxxxxxxxx0xxx01` | — | Prn(6) |
| `#FFFD` | `1111111111111101` | `11xxxxxxxxxxxx0x` | AYdat(2,3,?5,A) | AYadr(2,3,?5,A) |
| | | `11xxxxxxxxxxxx01` | AYdat(7) | AYadr(7) |
| | | `111xxxxxxxxxxx0x` | AYdat(8,9,D) | AYadr(8,9,D) |
| | | `111xxxxxxxx1xx0x` | AYdat(C) | AYadr(C) |
| | | `111xxxxxxx1xxx01` | AYdat(6) | AYadr(6) |

### Shadow Ports

| Port | Address (A15–A0) | Decoding Mask | READ | WRITE |
|------|-------------------|---------------|------|-------|
| `#77` | `xxxxxxxx01110111` | `xxxxxxxx0xx10111` | — | VidTrbReg(A) |
| `#xx77` | `xLxxxxKJ01110111` | `xLxxxxKJ0xx10111` | WRITE_ONLY(A) | WRITE_ONLY(A) |
| `#BD77`/`#FF77` | (soft port #0177) | `xLxxxxK10xx10111` | L,K=0 → Pal,PLLFC,Shdw-on | L\\K\\J = 0,0,1 |
| `#BF77`/`#FF77` | | `xLxxxx110xx10111` | L=0 → Pal,PLLFC on | L\\K\\J = 0,1,1 |
| `#FD77`/`#FF77` | (soft port #4177) | `x1xxxxK10xx10111` | K=0 → Shdw-on | L\\K\\J = 1,0,1 |
| `#FE77`/`#FF77` | | `x1xxxx1J0xx10111` | J=0 → Pag-off, CP/M ROM > CPU 0-3 | L\\K\\J = 1,1,0 |
| `#3FF7`–`#FFF7` | `BA11111111110111` | `BAxxxx111xx10111` | — | RAMPag(A) |
| `#FEE7`/`#FFE7` | `1111111A11100111` | `xxxxxxxAxxx00111` | Reserved(A) | Reserved(A) |

### SMUC (Scorpion & MOA Universal Controller)

| Port | Address (A15–A0) | Decoding Mask | READ | WRITE |
|------|-------------------|---------------|------|-------|
| `#18E6`–`#7FFE` | `0ED11CBA111GF110` | ISA: `xx1IHGFEDCBA` | ISA:#200–#3FF | ISA:#200–#3FF |
| `#5FBA` | `0101111110111010` | `0x011xxx101xx010` | Version | — |
| `#5FBE` | `0101111110111110` | `0x011xxx101xx110` | Revision | — |
| `#7EBE` | `0111111010111110` | `0x111xx0101xx110` | 8259 | 8259 |
| `#7FBA` | `0111111110111010` | `0x111xxx101xx010` | VirtualFDD | VirtualFDD |
| `#7FBE` | `0111111110111110` | `0x111xx1101xx110` | 8259 | 8259 |
| `#D8BE` | `1101100010111110` | `1x011xxx101xx110` | IDE-Hi | IDE-Hi |
| `#DFBA` | `1101111110111010` | `1x011xxx101xx010` | DS1685RTC | DS1685RTC |
| `#F8BE`–`#FFBE` | `11111CBA10111110` | `1x111xxx101xx110` | IDE#1Fx/#3F6 | IDE#1Fx/#3F6 |
| `#FFBA` | `1111111110111010` | `1x111xxx101xx010` | SYS | SYS |

### Beta 128 Disk Interface

| Port | Address (A15–A0) | Decoding Mask | READ | WRITE |
|------|-------------------|---------------|------|-------|
| `#1F`/`#3F`/`#5F`/`#7F` | `xxxxxxxx0BA11111` | `xxxxxxxx0BAxxx11` | WD1793(6,7,8,D) | WD1793(6,7,8,D) |
| | | `xxxxxxxx0BAx11x1` | WD1793(C) | WD1793(C) |
| | | `xxxxxxxx0BA11111` | WD1793(A) | WD1793(A) |
| | | `0xxxxxxx0BAxxx11` | WD1793(9) | WD1793(9) |
| `#FF` | `xxxxxxxx11111111` | `xxxxxxxx1xxxxx11` | FDsys(6,7,8,D) | FDsys(6,7,8,D) |
| | | `xxxxxxxx1xxx11x1` | FDsys(C) | FDsys(C) |
| | | `xxxxxxxx1xx11111` | FDsys(A) | FDsysPLLFC(A) |
| | | `0xxxxxxx111xxx11` | FDsys(9) | FDsys(9) |

### ATM IDE

| Port | Address (A15–A0) | Decoding Mask | READ | WRITE |
|------|-------------------|---------------|------|-------|
| `#FE0F`/`#FF0F` | `1111111A00001111` | `xxxxxxxA00001111` | IDEdat-Lo/Hi(A) | IDEdat-Lo/Hi(A) |
| `#FF2F` | `1111111100101111` | `xxxxxxxx00101111` | IDEerror(A) | IDEparam(A) |
| `#FF4F` | `1111111101001111` | `xxxxxxxx01001111` | IDEsect(A) | IDEsect(A) |
| `#FF6F` | `1111111101101111` | `xxxxxxxx01101111` | IDEstartsect(A) | IDEstartsect(A) |
| `#FF8F` | `1111111110001111` | `xxxxxxxx10001111` | IDEcyl-Lo(A) | IDEcyl-Lo(A) |
| `#FFAF` | `1111111110101111` | `xxxxxxxx10101111` | IDEcyl-Hi(A) | IDEcyl-Hi(A) |
| `#FFCF` | `1111111111001111` | `xxxxxxxx11001111` | IDEdevice(A) | IDEhead(A) |
| `#FFEF` | `1111111111101111` | `xxxxxxxx11101111` | IDEcomnd(A) | IDEstatus(A) |

### Peripheral Device Ports

| Port | Address (A15–A0) | Decoding Mask | READ | WRITE |
|------|-------------------|---------------|------|-------|
| `#0B`/`#6B` | `xxxxxxxx0AA01011` | `xxxxxxxx0Ax01011` | Z80DMA | Z80DMA |
| `#0E` | `xxxxxxxx00001110` | `xxxxxxxx0000xxxx` | PC<->ZXDrBeep | PC<->ZXDrBeep |
| `#1F` | `xxxxxxxx00011111` | `xxxxxxxxxx0xxxxx` | KempstonIF | — |
| | | `xxxxxxxx0xxxxxx1` | Kempston-M | — |
| | | `xxxxxxxx00011111` | AMIGA-MOUSE | — |
| `#3F` | `xxxxxxxx00111111` | `xxxxxxxxx0xxxxxx` | LIGHT PEN | — |
| `#B7` | `xxxxxxxx10110111` | `xxxxxxxx10110111` | XTR modem | XTR modem |
| `#EF` | `xxxxxxxx11101111` | `xxxxxxxx1xx01xxx` | C-DOS modem | C-DOS modem |
| `#F7` | `xxxxxxxx11110111` | `xxxxxxxxxxxx0xxx` | — | DIGITIZER(VMG) |

The sections below provide **detailed annotations** for each port group — per-model differences, data byte layouts, conflict warnings, and programming notes.

---

## Annotated System Ports

These ports control fundamental machine behavior: memory paging, border color, keyboard reading, speaker, and tape I/O. Every Spectrum program that touches hardware uses at least one of these.

### #FE — ULA Port (Border, Speaker, Tape, Keyboard)

The single most important port on the machine. The original 48K Ferranti ULA decodes **only A0** — it responds to any address where A0=0, giving **32,768 mirrors** across half the I/O space.

```
Port     Address (A15–A0)  Decoding (A15–A0)       READ              WRITE

#FE      xxxxxxxx11111110  xxxxxxxxxxxxxxx0       KeyTp(1,7-9)     BrdTpSpk(1,7-9)
                           A0=0 only              Prn(7)            BrdTpSpk(1,7-9)
                                                  Key(D)            BrdSpk(D)
                                                  KeyTp(A)          BrdTpSpk(A)
                                                  KeyTpPrn(6)       BrdTpSpk(6)
                                                  KeyTp(+1)         BrdTpSpk(+1)
                                                  KeyTp(C)          BrdTpSpk(C)
```

**Per-model decoding differences:**

| Model | Decoding | R | W | Notes |
|-------|----------|---|---|-------|
| 48K (1) | A0=0 only | Keyboard + EAR | Border + Beeper + MIC | Ferranti ULA TR6 inverts A0 |
| 128K/+2 (2,3) | A0=0 only | Same + `?` | Same | Same ULA core |
| +2A/+3 (4,5) | A0=0 only | Same | Same | Amstrad gate array |
| Scorpion (6) | `xxxxxxxx1xx11xx0` — checks A4,A3,A0 | KeyTpPrn | BrdTpSpk | More selective decode via EPLD |
| Pentagon (7) | A0=0 only | Key(D) | BrdSpk(D) | Discrete TTL, simplest decode |
| ATM Turbo (A) | `xxxxxxxx1xx11xx0` | KeyTp | BrdTpSpk | Checks additional lines |
| Profi (C) | `xxxxxxxx1xx11xx0` | KeyTp | BrdTpSpk | Same as ATM pattern |
| +2 (3) | `xxxxxxxx1xxxxxx0` | KeyTp(+1) | BrdTpSpk(+1) | Checks A6 line |

**Write data byte (OUT (#FE), A):**

```
Bit 7-5  4     3     2    1    0
?????  Spk   MIC   ?   G    B
              ?    Grn  Red
              ?    ?    Blue
```

- Bits 0–2: Border color (INK colors 0–7)
- Bit 3: MIC output (tape save signal on some models)
- Bit 4: Speaker output (1-bit beeper)

**Read data byte (IN A, (#FE)):**

- Bits 0–4: Keyboard rows (active low, 5 keys per row from current half-row)
- Bit 6: EAR input (tape load signal)
- Bit 7: Not used (typically 1 on 48K)

> [!WARNING]
> Writing to `#FE` simultaneously changes border color AND toggles the speaker AND MIC. There is no way to change one without affecting the others. Software that needs border effects without audible clicks must read the port first, modify only the border bits, and write back.

### #FF — Attribute Port / FDC System Register

On the 48K, reading `#FF` returns the **attribute byte** currently being output by the ULA during screen generation. This is the basis of the **floating bus** technique used for raster synchronization.

```
Port     Address (A15–A0)  Decoding (A15–A0)    READ              WRITE

#FF      xxxxxxxx11111111  xxxxxxxxxxxxxxxx    Atr(1-2)          -
                           All bits = 1        Atr(A)             -
                           xxxxxxxxxx1xxx11    Atr(6)             -
                           xxxxxxxx????????   Atr(4,5)          Vid/Pag(4/5)
```

| Model | Decoding | R | W | Notes |
|-------|----------|---|---|-------|
| 48K/128K (1,2) | All 16 bits = 1 | Attribute byte | — | Returns ULA's current attribute output |
| ATM Turbo (A) | `xxxxxxxxxxxxx111` | Atr | — | Only low 3 lines checked |
| Scorpion (6) | `xxxxxxxxxx1xxx11` | Atr | — | Checks A2,A1,A0 |
| +2A/+3 (4,5) | `xxxxxxxx????????` | Atr | Vid/Pag | Gate array uses #FF differently |

> [!WARNING]
> The floating bus technique (reading #FF for raster sync) **does not work** on the +2A/+3, Pentagon, or most Soviet clones. See [floating_bus.md](../05_development/05_display_and_timing/floating_bus.md) for per-model behavior.

### #7FFD — 128K Memory Paging Register

The primary paging port on all 128K-compatible machines. Introduced with the Sinclair 128K Toastrack, it controls RAM bank selection, ROM switching, screen selection, and a lock bit.

```
Port     Address (A15–A0)  Decoding (A15–A0)       READ        WRITE

#7FFD    0111111111111101  0xxxxxxxxxxxxx0x       -           Pag(2,8,9,A)
                           A15=0,A14-A11=0111                 Pag(D)
                           A1=0                    -           Pag(C)
                           6 lines checked         -           Pag(3,?5)
                                                              Pag(7)
                           01xxxxxxxxxxxx0x       -           Pag(3,?5)
                           01xxxxxxxxxxxx01       -           Pag(7)
                           01xxxxxxxx1xxx01  Trb-ON(6)       Pag(6)
                           0x1xx111xx1xxx01       -           Pag(?B)
```

**Per-model decoding:**

| Model | Decoding | Notes |
|-------|----------|-------|
| 128K/+2 (2,3) | `0xxxxxxxxxxxxx0x` — 6 lines via 74HC138 | Standard 128K paging |
| Pentagon (8,9,A) | Same as 128K | Compatible decoding |
| Pentagon EFF7 (D) | `0xxxxxxxxxxxxx01` | Slightly different mask for extended mode |
| Profi (C) | `0xxxxxxxxxx11x0x` | Different decoding for Profi's paging scheme |
| +2A/+3 (3) | `01xxxxxxxxxxxx0x` | Amstrad gate array checks more lines |
| Scorpion (6) | `01xxxxxxxx1xxx01` with Trb-ON | Scorpion adds turbo control to same port |
| Byte (?B) | `0x1xx111xx1xxx01` | Unique extended decode |

**Write data byte (OUT (#7FFD), A):**

```
Bit 7    6    5    4    3    2    1    0
Lock   ?    ?   ROM  Scr  Bank bits
                Sel  Sel  (0-7)
```

- Bits 0–2: RAM bank mapped at `#C000` (banks 0–7)
- Bit 3: Screen select (0=Bank 5 / normal, 1=Bank 7 / shadow)
- Bit 4: ROM select (0=ROM 0 / 128K editor, 1=ROM 1 / 48K BASIC)
- Bit 5: Reserved on Sinclair, used differently on some clones
- Bit 6: Unused on most models
- Bit 7: **Lock bit** — when set to 1, prevents further writes to `#7FFD` until reset

> [!IMPORTANT]
> The lock bit is a one-shot fuse. Once bit 7 is written as 1, the paging register is frozen until the machine is reset. The 128K ROM sets this bit during initialization. Software that needs to page RAM must either disable the lock or use it carefully.

### #1FFD — Extended Paging / FDC Control

This is the most **dangerous port** for cross-model compatibility. On the +2A/+3 it controls extended paging modes and the floppy disk motor. On Soviet clones it controls the Beta 128 FDC — a completely different function with the same port address.

```
Port     Address (A15–A0)  Decoding (A15–A0)     READ        WRITE

#1FFD    0001111111111101  0001xxxxxxxxxx0x     -           PagPrn/FD(3/+3)
                           A15=0,A14=0,A13=0               Pag(7)
                           A12=1,A1=0                       Pag(6)
                           10+ lines checked
```

**Per-model — completely different functions:**

| Model | Function | Decoding | Notes |
|-------|----------|----------|-------|
| +2/+2A/+3 (3,+3) | Extended paging + floppy disk motor + printer | `0001xxxxxxxxxx0x` | 4 paging modes combined with #7FFD bit 5 |
| Pentagon (7) | Memory paging extension | `00xxxxxxxxxxxx01` | Different mask, paging only |
| Scorpion (6) | Memory paging + Turbo OFF | `00xxxxxxxx1xxx01` | Turbo control via same port |
| Byte (?B) | Memory paging | `0x0xx111xx1xxx01` | Unique extended decode |

> [!WARNING]
> **Port collision!** Writing `#1FFD` on a +3 controls paging and disk. Writing `#1FFD` on a Pentagon/Scorpion controls the Beta 128 FDC. Code that works on one machine **will corrupt data** on the other. Always detect the machine type before using this port. See [memory_and_io_plus3.md](../05_development/03_memory_and_io/memory_and_io_plus3.md) and [memory_and_io_pentagon.md](../05_development/03_memory_and_io/memory_and_io_pentagon.md).

### #EFF7 — Pentagon Extended Memory

Exclusive to the Pentagon 512K/1024K. Decoded via a **74HC688 8-bit identity comparator** for an almost-exact match — very few mirrors.

```
Port     Address (A15–A0)  Decoding (A15–A0)    READ        WRITE

#EFF7    1110111111110111  1110xxxxxxxx0xxx    -           PagVidTrbReg(8)
                           8+ lines checked                PagVidTrbReg(D)
```

| Model | Function | Notes |
|-------|----------|-------|
| Pentagon 512K+ (8) | Extended paging + video + turbo + config register | Decoded by 74688 comparator |
| Pentagon EFF7 (D) | Same functions, slightly different mask variant | `1110xxxxxxxx0xx1` |

This port does **not exist** on any Sinclair/Amstrad machine. Writing to it on a 48K or 128K has no effect (the address is simply not decoded by any hardware).

### #DFFD — Alternative Pentagon Paging

Used on some Pentagon configurations as an alternative to `#EFF7` for extended memory paging.

```
Port     Address (A15–A0)  Decoding (A15–A0)    READ        WRITE

#DFFD    1101111111111101  xx0xxxxxxxxxxx0x    -           Pag(9)
```

| Model | Function | Notes |
|-------|----------|-------|
| Kay 1024 (9) | Memory paging extension | Checks fewer lines than #EFF7 |
| Byte (?B) | Memory paging | `1x0xx111xx1xxx01` |

### #00 — Reset / Configuration Register

On certain clone hardware, writing to port `#00` triggers a reset or configuration latch.

```
Port     Address (A15–A0)  Decoding (A15–A0)    READ        WRITE

#00      xxxxxxxx00000000  xxxxxxxx00000000    -           Reg(B)
                           Full 8-bit match                Pag(C)
```

| Model | Function | Notes |
|-------|----------|-------|
| Byte (B) | Configuration register | Full low-byte match |
| Profi (C) | Memory paging | `xxxxxxxx0xx0xxx0` — fewer lines checked |

### #80FD — CP/M Paging Control

Used on the Profi clone to control CP/M mode paging.

```
Port     Address (A15–A0)  Decoding (A15–A0)    READ        WRITE

#80FD    1000000011111101  1x0xxxxxxxx11x0x    -           CP/MPag(C)
```

| Model | Function | Notes |
|-------|----------|-------|
| Profi (C) | CP/M mode paging control | A15=1 isolates it from #7FFD (A15=0) |

### #7E — Keyboard Read (Scorpion)

A secondary keyboard read port on the Scorpion, decoded more tightly than `#FE`.

```
Port     Address (A15–A0)  Decoding (A15–A0)    READ        WRITE

#7E      xxxxxxxx01111110  xxxxxxxx0xx11xx0    Key(C)      -
```

### #F6 — Border Control (ATM Turbo)

ATM Turbo uses a separate port for border color, independent of the ULA `#FE` port.

```
Port     Address (A15–A0)  Decoding (A15–A0)    READ        WRITE

#F6      xxxxxxxx11110110  xxxxxxxxxxxx0110    -           Brd(A)
```

### Additional Paging Ports (Byte, Profi)

The Byte and Profi clones use additional paging ports decoded at specific address ranges:

```
Port     Address (A15–A0)  Decoding (A15–A0)    READ        WRITE

#78FD    0111100011111101  0x1xx000xx1xxx01    -           Pag(?B)
#7AFD    0111101011111101  0x1xx010xx1xxx01    -           Vid(?B)
#7CFD    0111110011111101  0x1xx100xx1xxx01    -           Vid(?B)
#7EFD    0111111011111101  0x1xx110xx1xxx01    -           Rag(?B)
```

These are Byte-specific ports for extended memory, video configuration, and register access. The decoding pattern `0x1xx???xx1xxx01` shows a family of related ports that share the same upper-bit structure but differ in the middle bit group.

---

## Peripheral Ports

Ports for sound chips (AY-3-8912), printer interfaces, analog-to-digital converters, and IDE interfaces.

### #FFFD / #BFFD — AY-3-8912 / YM2149 PSG

The AY sound chip is present on all 128K-compatible machines and most clones. Two ports control it: `#FFFD` selects the active register, `#BFFD` reads/writes the selected register's data.

```
Port     Address (A15–A0)  Decoding (A15–A0)     READ          WRITE

#BFFD    1011111111111101  10xxxxxxxxxxxx0x     -             AYdat(2,3,?5,A)
                           A15=1,A14=0,A1=0                   AYdat(7)
                           2-3 lines checked                   AYdat(8,9)
                                                               AYdat(C)
                                                               AYdat(6)
                           1x1xxxxxxxxxxx0x     -             AYdat(D)

#FFFD    1111111111111101  11xxxxxxxxxxxx0x     AYdat(2,3,?5,A)  AYadr(2,3,?5,A)
                           A15=1,A14=1,A1=0     AYdat(7)         AYadr(7)
                           2-3 lines checked     AYdat(8,9,D)     AYadr(8,9,D)
                                                AYdat(C)         AYadr(C)
                                                AYdat(6)         AYadr(6)
```

**Per-model AY decoding:**

| Model | #FFFD Decoding | #BFFD Decoding | Notes |
|-------|---------------|----------------|-------|
| 128K/+2 (2,3) | `11xxxxxxxxxxxx0x` | `10xxxxxxxxxxxx0x` | Standard — A15, A14, A1 checked |
| +2A/+3 (4,5) | Same | Same | Compatible |
| Pentagon (7) | `11xxxxxxxxxxxx01` | `10xxxxxxxxxxxx01` | Slightly different mask |
| Pentagon EFF7 (D) | `1x1xxxxxxxxxxx0x` | `1x1xxxxxxxxxxx0x` | Checks A13 instead of A14 |
| Scorpion (6) | `111xxxxxxx1xxx01` | `101xxxxxxx1xxx01` | More lines checked |
| Kay (9) | `101xxxxxxxxxxx0x` | `101xxxxxxxxxxx0x` | Same as Scorpion pattern |
| ATM Turbo (A) | `101xxxxxxxx1xx0x` | `101xxxxxxxx1xx0x` | Checks A10 additionally |
| Profi (C) | `111xxxxxxxx1xx0x` | `101xxxxxxxx1xx0x` | Similar to ATM |

The AY chip has 16 registers controlling 3 tone channels, noise generator, envelope, and I/O port. The programming sequence is: write register number to `#FFFD`, then read/write data at `#BFFD`.

> [!NOTE]
> The 48K Spectrum (model 1) has **no AY chip**. These ports do nothing on original 48K hardware.

### #1B / #7B — Printer Ports

Printer interfaces with varying decode precision:

```
Port     Address (A15–A0)  Decoding (A15–A0)    READ        WRITE

#1B      xxxxxxxx00011x11  xxxxxxxx0xx11xx1    Prn(C)      -
#7B      xxxxxxxx01111011  xxxxxxxxxxxxx011    -           Prn(A)
                           xxxxxxxx0xx110x1    -           Prn(C)
```

### #FA / #FB — ATM Turbo I/O and Printer

```
Port     Address (A15–A0)  Decoding (A15–A0)    READ        WRITE

#FA      xxxxxxxx11111010  xxxxxxxxxxxxx010    IO(A)       IO(A)
#FB      xxxxxxxx11111011  xxxxxxxxxxxxx0xx    Prn(8,D)    Prn(8,D)
                           xxxxxxxxxxxxx011    Prn(A)      PrnDAC(A)
                           xxxxxxxx1xx110x1    -           Prn(C)
```

ATM Turbo uses `#FA` as a general-purpose I/O port, while `#FB` serves double duty as printer port on multiple machines and a DAC output on the ATM.

### #0FFD / #2FFD / #3FFD — +3 Floppy Disk Controller

The +3's internal floppy uses a WD1772 (or compatible) FDC accessed through these ports:

```
Port     Address (A15–A0)  Decoding (A15–A0)    READ              WRITE

#0FFD    0000111111111101  0000xxxxxxxxxx0x    Prn(?3/+3)        Prn(?3/+3)
#2FFD    0010111111111101  0010xxxxxxxxxx0x    -                 8272status(?+3)
#3FFD    0011111111111101  0011xxxxxxxxxx0x    8272data(?+3)     8272data(?+3)
```

| Port | Function | Notes |
|------|----------|-------|
| `#0FFD` | Printer data / control | Also used for centronics interface |
| `#2FFD` | FDC status register | Write = command, Read = status |
| `#3FFD` | FDC data register | Track/sector/data transfer |

### #7DFD / #7FFD — ADC and IDE (ATM Turbo)

```
Port     Address (A15–A0)  Decoding (A15–A0)    READ        WRITE

#7DFD    0111110111111101  0xxxxx0xxxxxxx0x    ADC(A)      -
#7FFD    0111111111111101  0xxxxx1xxxxxxx0x    IDE,ADC(A)  -
```

ATM Turbo places IDE and ADC behind the same upper-bit structure as `#7FFD`, differentiated by bit 11.

---

## Shadow Ports

Shadow ports are a concept unique to Soviet clones — secondary ports at address `#xx77` that control video modes, palettes, turbo, and memory paging. They are decoded by checking additional address lines beyond what the ULA sees, allowing them to coexist with standard hardware without conflict.

### #77 — Shadow Port Base

The base shadow port address. On ATM Turbo hardware, this controls video mode, turbo, and configuration registers.

```
Port     Address (A15–A0)  Decoding (A15–A0)    READ        WRITE

#77      xxxxxxxx01110111  xxxxxxxx0xx10111    -           VidTrbReg(A)
```

### #xx77 — Shadow Port Family (ATM Turbo)

The ATM Turbo decodes a family of shadow ports by checking additional address lines (L, K, J bits) on top of the base `#77` pattern. Each combination of L/K/J enables different features:

```
Port            Decoding                    WRITE effect

#BD77/#FF77     xLxxxxK10xx10111    L,K=0 -> Pal,PLLFC,Shdw-on
(#0177-soft)                            Palette + PLL FDC + Shadow ON

#BF77/#FF77     xLxxxx110xx10111    L=0  -> Pal,PLLFC -on
                                        Palette + PLL FDC only

#FD77/#FF77     x1xxxxK10xx10111    K=0  -> Shdw-on
(#4177-soft)                            Shadow screen ON only

#FE77/#FF77     x1xxxx1J0xx10111    J=0  -> Pag-off, CP/M rom > CPU0-3
                                        Disable paging, map CP/M ROM

#3FF7–#FFF7     BA11111111110111    RAMPag(A)
                BAxxxx111xx10111    RAM-based paging (ATM Turbo)
```

**L / K / J bit positions** — these are specific address lines that the ATM's glue logic checks beyond the standard shadow port decode:

| Bit | Address Line | Effect when 0 | Effect when 1 |
|-----|-------------|---------------|---------------|
| L | Specific high address line | Enable palette + PLL FDC | Normal operation |
| K | Specific high address line | Enable shadow screen | Shadow off |
| J | Specific high address line | Disable paging, CP/M ROM to CPU banks 0–3 | Normal paging |

> [!NOTE]
> Shadow ports are **write-only**. Reading them returns undefined data. This is by design — they control hardware state that cannot be read back.

### #FEE7 / #FFE7 — Reserved (ATM Turbo)

```
Port     Address (A15–A0)  Decoding (A15–A0)    READ        WRITE

#FEE7    1111111A11100111  xxxxxxxAxxx00111    Reserved(A) Reserved(A)
```

Reserved for future use on ATM Turbo hardware.

---

## SMUC — Scorpion & MOA Universal Controller

The SMUC is an expansion board for the Scorpion that provides an ISA bus, IDE hard disk interface, real-time clock, and interrupt controller. It has its own port decoding scheme layered on top of the Scorpion's EPLD.

```
Port     Address (A15–A0)  Decoding (A15–A0)         READ              WRITE

#18E6–   0ED11CBA111GF110   ISA:xx1IHGFEDCBA        ISA:#200–#3FF     ISA:#200–#3FF
#7FFE                        ISA bus bridge

#5FBA    0101111110111010   0x011xxx101xx010         Version           -
#5FBE    0101111110111110   0x011xxx101xx110         Revision          -

#7EBE    0111111010111110   0x111xx0101xx110         8259              8259
#7FBA    0111111110111010   0x111xxx101xx010         VirtualFDD        VirtualFDD
#7FBE    0111111110111110   0x111xx1101xx110         8259              8259

#D8BE    1101100010111110   1x011xxx101xx110         IDE-Hi            IDE-Hi
#DFBA    1101111110111010   1x011xxx101xx010         DS1685RTC         DS1685RTC

#F8BE–   11111CBA10111110   1x111xxx101xx110         IDE#1Fx/#3F6      IDE#1Fx/#3F6
#FFBE                        Maps ISA IDE registers

#FFBA    1111111110111010   1x111xxx101xx010         SYS               SYS
```

**SMUC port breakdown:**

| Port Range | Device | Notes |
|-----------|--------|-------|
| `#18E6`–`#7FFE` | ISA bus bridge | Maps ISA I/O space `#200`–`#3FF` |
| `#5FBA` | Version register | Read hardware version |
| `#5FBE` | Revision register | Read hardware revision |
| `#7EBE` / `#7FBE` | Intel 8259 PIC | Programmable Interrupt Controller |
| `#7FBA` | Virtual FDD | Floppy disk emulation |
| `#D8BE` | IDE (high address) | 16-bit IDE access, high byte |
| `#DFBA` | DS1685 RTC | Dallas real-time clock |
| `#F8BE`–`#FFBE` | IDE task file | Maps standard IDE registers `#1Fx` and `#3F6` |
| `#FFBA` | System control | SMUC system register |

The SMUC uses a complex decoding scheme where multiple address line groups select different sub-devices. The `CBA` and `GF` bit groups in the address encode the ISA register offset.

---

## Beta 128 Disk Interface

The Beta 128 is the **dominant floppy disk interface** in the Soviet clone world. It uses a WD1793 / KR1818VG93 Floppy Disk Controller (FDC) and is present on most Pentagon, Scorpion, and Kay machines. It pages its own TR-DOS ROM at `#0000`–`#3FFF` when activated.

The FDC has 4 internal registers selected by address lines A8 (`B`) and A7 (`A`):

```
Port     Address (A15–A0)  Decoding (A15–A0)         READ              WRITE

#1F      xxxxxxxx00011111  xxxxxxxx0BAxxx11         WD1793(6,7,8,D)   WD1793(6,7,8,D)
#3F      xxxxxxxx00111111                           WD1793 command/status
#5F      xxxxxxxx01011111  xxxxxxxx0BAx11x1         WD1793(C)         WD1793(C)
#7F      xxxxxxxx01111111  xxxxxxxx0BA11111         WD1793(A)         WD1793(A)

#FF      xxxxxxxx11111111  xxxxxxxx1xxxxx11         FDsys(6,7,8,D)    FDsys(6,7,8,D)
                           xxxxxxxx1xxx11x1         FDsys(C)          FDsys(C)
                           xxxxxxxx1xx11111         FDsys(A)          FDsysPLLFC(A)
                           0xxxxxxx111xxx11         FDsys(9)          FDsys(9)
```

**WD1793 register map (via A8/A1/A0):**

| Port | A8 | A1 | A0 | Register (Read) | Register (Write) |
|------|-----|-----|-----|-----------------|------------------|
| `#1F` | 0 | 0 | 1 | Status | Command |
| `#3F` | 0 | 1 | 1 | Track | Track |
| `#5F` | 1 | 0 | 1 | Sector | Sector |
| `#7F` | 1 | 1 | 1 | Data | Data |

**System port `#FF`:** Controls FDC system functions — motor on/off, drive select, density, and side select.

| Model | Beta 128 Present | Notes |
|-------|-----------------|-------|
| Pentagon (7) | Yes | Most common configuration |
| Scorpion (6) | Yes | Built-in or expansion |
| Kay (9) | Yes | Built-in |
| ATM Turbo (A) | Yes | With VG93 FDC |
| Profi (C) | Yes | Via expansion |
| All Sinclair/Amstrad | No | Uses +3 FDC or tape only |

> [!WARNING]
> Ports `#1F`–`#7F` overlap with the **Kempston joystick** port `#1F`. On machines with both Beta 128 and Kempston, the FDC is selected by the `B` and `A` address lines (A8/A7) while Kempston uses the low bits. However, cheap Kempston interfaces with poor decoding can conflict. The system port `#FF` can also conflict with the attribute/floating-bus port `#FF`.

---

## ATM IDE Interface

The ATM Turbo has its own built-in IDE interface with a 16-bit data path. IDE registers are accessed via a set of ports in the `#FFxx` range, selected by address lines A4–A7.

```
Port     Address (A15–A0)  Decoding (A15–A0)    READ              WRITE

#FE0F/   1111111A00001111  xxxxxxxA00001111   IDEdat-Lo/Hi(A)   IDEdat-Lo/Hi(A)
#FF0F                        16-bit data xfer

#FF2F    1111111100101111  xxxxxxxx00101111   IDEerror(A)       IDEparam(A)
#FF4F    1111111101001111  xxxxxxxx01001111   IDEsect(A)        IDEsect(A)
#FF6F    1111111101101111  xxxxxxxx01101111   IDEstartsect(A)   IDEstartsect(A)
#FF8F    1111111110001111  xxxxxxxx10001111   IDEcyl-Lo(A)      IDEcyl-Lo(A)
#FFAF    1111111110101111  xxxxxxxx10101111   IDEcyl-Hi(A)      IDEcyl-Hi(A)
#FFCF    1111111111001111  xxxxxxxx11001111   IDEdevice(A)      IDEhead(A)
#FFEF    1111111111101111  xxxxxxxx11101111   IDEcomnd(A)       IDEstatus(A)
```

**ATM IDE register map:**

| Port | IDE Register | Read | Write |
|------|-------------|------|-------|
| `#FE0F` / `#FF0F` | Data (16-bit) | Read sector data | Write sector data |
| `#FF2F` | Error / Features | Error code | Set feature |
| `#FF4F` | Sector count | — | Sectors to transfer |
| `#FF6F` | Start sector | — | LBA low / CHS sector |
| `#FF8F` | Cylinder low | Cylinder low byte | Cylinder low byte |
| `#FFAF` | Cylinder high | Cylinder high byte | Cylinder high byte |
| `#FFCF` | Device / Head | Device select info | Head select / LBA mid |
| `#FFEF` | Command / Status | Status byte | Command byte |

The `#FE0F` / `#FF0F` data port is notable: address line A8 (`A` in Black_Cat notation) selects between Lo byte and Hi byte of a 16-bit IDE transfer. This allows the 8-bit Z80 to perform 16-bit ATA transfers with two consecutive 8-bit reads/writes.

---

## Peripheral Device Ports

Individual peripheral devices — DMA controllers, modems, light pens, digitizers, and mice.

### #0B / #6B — Z80 DMA

```
Port     Address (A15–A0)  Decoding (A15–A0)    READ        WRITE

#0B/#6B  xxxxxxxx0AA01011  xxxxxxxx0Ax01011    Z80DMA      Z80DMA
```

A Z80 DMA controller (rarely present on Spectrum hardware). The `A` bit selects between two register banks. Only responds when the indicated address lines match.

### #1F — Kempston Mouse (AMX variant)

```
Port     Address (A15–A0)  Decoding (A15–A0)    READ        WRITE

#1F      xxxxxxxx00011111  xxxxxxxx0xxxxxx1    Kempston-M  -
                           xxxxxxxx00011111    AMIGA-MOUSE -
```

The Kempston mouse uses the same base address as the Kempston joystick but is differentiated by additional address lines being checked.

### #0E — PC-to-ZX Doctor Beeper

```
Port     Address (A15–A0)  Decoding (A15–A0)    READ        WRITE

#0E      xxxxxxxx00001110  xxxxxxxx0000xxxx    PC<->ZXDrBeep   PC<->ZXDrBeep
```

A peripheral for bidirectional PC-to-Spectrum communication with beeper feedback.

### #3F — Light Pen

```
Port     Address (A15–A0)  Decoding (A15–A0)    READ        WRITE

#3F      xxxxxxxx00111111  xxxxxxxxx0xxxxxx    LIGHT PEN   -
```

Light pen input — reads horizontal/vertical position. Decoding checks A6=0.

### #B7 — XTR Modem

```
Port     Address (A15–A0)  Decoding (A15–A0)    READ        WRITE

#B7      xxxxxxxx10110111  xxxxxxxx10110111    XTR modem   XTR modem
```

Full 8-bit decode — a specific modem interface with exact address matching.

### #EF — C-DOS Modem

```
Port     Address (A15–A0)  Decoding (A15–A0)    READ        WRITE

#EF      xxxxxxxx11101111  xxxxxxxx1xx01xxx    C-DOS modem C-DOS modem
```

Modem interface for C-DOS communication software.

### #F7 — Digitizer (VMG)

```
Port     Address (A15–A0)  Decoding (A15–A0)    READ        WRITE

#F7      xxxxxxxx11110111  xxxxxxxxxxxx0xxx    -           DIGITIZER(VMG)
```

Video digitizer peripheral — write-only control port.

---

## Joystick Ports (World of Spectrum Reference)

Joystick interfaces use various decoding schemes. The four major standards are:

### Kempston Joystick — #1F

```
Port     Decoding                    R/W   Function

#1F      xxxxxxxxxxxxxxx1            R     Kempston(7) — only A0 checked
         xxxxxxxxxx0xxxx1            R     Kempston(D)
         xxxxxxxx0xx11xx1            R     Kempston+Printer(6)
         xxxxxxxx0x0xxx11            R     Kempston(6)
```

**Read data byte:**

```
Bit 7  6   5   4   3   2   1   0
 ?    ?   LE  DO  SP  RI  UP  FI
              ft  wn  ce  ght     re
```

Active high — bit set means direction/button pressed. Only bits 0–5 are meaningful.

> [!WARNING]
> The Kempston joystick port `#1F` **conflicts with the Beta 128 FDC** command/status register. On machines with both devices, the Kempston typically decodes more lines to avoid collision. Reading `#1F` during TR-DOS operations returns FDC status, not joystick state.

### Sinclair Interface 2 Joysticks — #EFFE / #F7FE

Two joystick ports mapped to keyboard matrix positions:

```
Port     Decoding                R/W   Function

#EFFE    ---0 ---- ---- ----     R     Sinclair Joystick 1 (67890 keys)
#F7FE    ---- 0--- ---- ----     R     Sinclair Joystick 2 (12345 keys)
```

**Sinclair 1 (#EFFE) bit mapping:**

```
Bit 0 = ENTER (fire)      Bit 1 = L (left)
Bit 2 = D (down)          Bit 3 = U (up)
Bit 4 = R (right)         Bits 5-7 = unused
```

Active **low** — bit cleared means direction/button pressed (inverted compared to Kempston).

### Fuller Joystick Box — #7F

```
Port     Decoding                R/W   Function

#7F      ---- ---- 0111 1111     R     Fuller joystick
```

The Fuller box also includes an AY sound chip at ports `#3F` (control) and `#5F` (data).

### Cursor / Protek Joystick

Uses keyboard matrix ports — no dedicated hardware port. Reads from specific half-rows of the keyboard (ports `#EFFE`, `#F7FE`, `#FBFE`, `#FDFE`, `#FEFE`).

---

## Mouse Ports (World of Spectrum Reference)

### Kempston Mouse — #FADF / #FBDF / #FFDF

Three ports for buttons, X position, and Y position:

```
Port     Decoding                    R/W   Function

#FADF    ---- ---0 --0- ----        R     Buttons
#FBDF    ---- -0-1 --0- ----        R     X position
#FFDF    ---- -1-1 --0- ----        R     Y position
```

**Button byte (#FADF):**

```
Bit 7  6   5   4   3   2   1   0
 ?    ?   ?   ?   ?   MB  MR  ML
                      Right Left
```

Active **low** — bit cleared means button pressed. X and Y ports return position counters (8-bit, wrapping).

### AMX Mouse — #FADF / #FBDF / #FFDF

Same port addresses as Kempston mouse but different decoding and protocol. The AMX mouse is less common and uses a different initialization sequence.

---

## DivIDE / DivMMC IDE Interface

The DivIDE and DivMMC are compact IDE interfaces that attach to the Spectrum expansion bus. They provide IDE hard disk or CompactFlash access plus a FAT filesystem via ESXDOS.

```
Port     Decoding                R/W   Function

#E3      ---- ---- 1110 0011     R/W   IDE command/status (+D compatible)
#E7      ---- ---- 1110 0111     W     Memory paging (+D compatible)
#EB      ---- ---- 1110 1011     R/W   IDE track register
#EF      ---- ---- 1110 1111     R/W   IDE system register / control
#F3      ---- ---- 1111 0011     R/W   IDE sector register
#F7      ---- ---- 1111 0111     R/W   IDE data / printer
#FB      ---- ---- 1111 1011     R/W   IDE data port
```

The DivIDE uses a +D-compatible port mapping, which itself borrows from the Beta 128 style but at different addresses. DivMMC uses the same ports with slightly different paging behavior.

> [!NOTE]
> For programming details, see [divide_divmmc.md](../03_io/storage/divide_divmmc.md) (planned) and [esxdos.md](../04_operating_systems/esxdos.md) (planned).

---

## Sound Card Ports

The ZX Spectrum ecosystem accumulated a remarkable variety of sound hardware. Each card has its own port decoding:

### General Sound (GS) — #B3 / #BB

A dedicated Z80-based sound card with 4-channel sample playback. Has its own Z80 CPU, RAM, and DAC.

```
Port     Address (A15–A0)  Decoding (A15–A0)    READ        WRITE

#B3      xxxxxxxx10110011  xxxxxxxx10110011    GS status   GS command
#BB      xxxxxxxx10111011  xxxxxxxx10111011    GS data     GS data
```

Full 8-bit low-byte decode on both ports. The GS is a self-contained subsystem — you send commands and sample data, and the card's internal Z80 handles mixing and playback.

### TurboSound — #FF

TurboSound places **two AY-3-8912 chips** behind a single bank-select port. The active chip is selected by writing to `#FF`:

```
Port     Decoding                R/W   Function

#FF      xxxxxxxx11111111        W     TurboSound chip select
```

After selecting chip 0 or 1 via `#FF`, standard AY ports `#FFFD` / `#BFFD` access the selected chip. This gives 6 total channels (2 × 3-channel AY).

> [!WARNING]
> TurboSound `#FF` conflicts with both the Beta 128 system port and the floating bus attribute read. Only write to this port if you know TurboSound is present.

### TurboSound FM — #FF

Adds a YM2203 (OPN) FM synthesis chip. Uses the same `#FF` bank-select mechanism as TurboSound, extended with additional chip indices for the FM chip.

### Covox / SounDrive — Various

Simple 8-bit DAC (digital-to-analog converter) ports for direct sample playback:

| Port | Decoding | Card | Notes |
|------|----------|------|-------|
| `#FB` | `xxxxxxxxxxxxxx011` | ATM Turbo DAC | Built into ATM hardware |
| `#DF` | varies | Covox Speech Thing | Simple resistor DAC |
| `#1F` | `xxxxxxxx0xx11xx1` | SounDrive (4-channel) | 4 ports for 4 DAC channels |

Covox is the simplest sound output — write a byte and it appears as an analog voltage on the output. No register protocol, no chip, just a resistor ladder.

### SAA1099 — #FF / #FE

Philips SAA1099 PSG with 6 stereo channels:

```
Port     Function
#FF      SAA1099 address select
#FE      SAA1099 data write
```

Present on some Soviet clone sound cards (ZXM Soundcard) combined with TurboSound FM.

---

## Multiface Ports

The Multiface is a hardware overlay tool that pages its own RAM and ROM via specific port sequences.

| Version | Page-In Port | Page-Out Port | Notes |
|---------|-------------|--------------|-------|
| Multiface I | `#9F` (IN) | `#1F` (OUT) | 48K only |
| Multiface 128 | `#BF` (IN) or `#9F` (Disciple variant) | `#3F` (OUT) | 128K compatible |
| Multiface 3 | `#3F` (IN) | `#BF` (OUT) | +3 compatible, also reads `#7FFD` and `#1FFD` via `#7F3F` and `#1F3F` |

---

## ZX Spectrum Next Ports

The ZX Spectrum Next implements full 16-bit decoding in its FPGA, adding many new ports for its enhanced features. These ports only exist on the Next hardware.

### Core Configuration

| Port | R/W | Function |
|------|-----|----------|
| `#50`–`#57` | W | MMU slot mapping (8 slots × 8 KB pages) |
| `#243B` | W | Next register select |
| `#253B` | R/W | Next register data access |

### Layer 2 (256-color)

| Port | R/W | Function |
|------|-----|----------|
| `#123B` | W | Layer 2 paging (select 16K bank for access at `#0000`–`#3FFF`) |

### Sprites

| Port | R/W | Function |
|------|-----|----------|
| `#55` | W | Sprite slot select (via `#303B` + relative ports) |
| `#57` | W | Sprite attributes upload |
| `#303B` | W | Sprite pattern select |

### Copper

| Port | R/W | Function |
|------|-----|----------|
| `#60` | W | Copper instruction low byte |
| `#61` | W | Copper instruction high byte |

### DMA

| Port | R/W | Function |
|------|-----|----------|
| `#6B` | W | DMA register select |
| `#7B` | R/W | DMA data transfer |

### Turbo / Speed

| Port | R/W | Function |
|------|-----|----------|
| `#1FFD` (Next reuses this) | W | Speed/turbo control |

> [!NOTE]
> The ZX Spectrum Next has many more ports for its full feature set (tilemap, UART, SPI, RTC, ESP WiFi). For the complete list, see the official Next documentation at [zxnext.io](https://www.zxnext.io/).

---

## Cross-References

### In This Repository

- **Port decoding concepts** (how mirrors work, schematics, Verilog): [io_port_decoding.md](../05_development/03_memory_and_io/io_port_decoding.md)
- **48K memory and ports** (#FE, keyboard, beeper): [memory_and_io_48k.md](../05_development/03_memory_and_io/memory_and_io_48k.md)
- **128K memory and ports** (#7FFD, AY, shadow screen): [memory_and_io_128k.md](../05_development/03_memory_and_io/memory_and_io_128k.md)
- **+2A/+3 memory and ports** (#1FFD, 4 paging modes): [memory_and_io_plus3.md](../05_development/03_memory_and_io/memory_and_io_plus3.md)
- **Pentagon memory and ports** (#EFF7, Beta 128, TR-DOS): [memory_and_io_pentagon.md](../05_development/03_memory_and_io/memory_and_io_pentagon.md)
- **ZX Spectrum Next memory and ports** (2MB MMU, copper, sprites): [memory_and_io_next.md](../05_development/03_memory_and_io/memory_and_io_next.md)
- **Floating bus per-model behavior**: [floating_bus.md](../05_development/05_display_and_timing/floating_bus.md)
- **Contention model** (which ports are contended): [contention_model.md](../05_development/03_memory_and_io/contention_model.md)
- **Bank switching patterns** (practical paging techniques): [bank_switching_patterns.md](../05_development/03_memory_and_io/bank_switching_patterns.md)
- **Screen pixel layout** (nonlinear addressing): [screen_layout.md](../05_development/03_memory_and_io/screen_layout.md)
- **ULA timing** (contention, multicolor windows): [ula_timing.md](../02_hardware/original/ula_timing.md)
- **Clone timing** (per-clone port and timing differences): [clone_timing.md](../02_hardware/clones/clone_timing.md)
- **Z80 addressing modes** (how I/O instructions form the port address): [z80_addressing.md](../01_cpu/z80_addressing.md)
- **Z80 architecture** (CPU bus interface): [z80_architecture.md](../01_cpu/z80_architecture.md)

### External Sources

- **Black_Cat's ZX Ports Full Table** (BC Info Guide #4, 2008) — the source for per-model port decoding data: [zx-ports-full-table.txt](https://github.com/tslabs/zx-evo/blob/master/pentevo/docs/ZX/zx-ports-full-table.txt)
- **World of Spectrum Hardware Ports** — original hardware peripheral reference with bitmask notation: [ports.htm](https://worldofspectrum.org/faq/reference/ports.htm)
- **ZX Spectrum Next Register Reference** — complete Next port map: [zxnext.io](https://www.zxnext.io/)
- **Z80 I/O timing** (T-states for IN/OUT instructions): [z80_timing.md](../01_cpu/z80_timing.md)
