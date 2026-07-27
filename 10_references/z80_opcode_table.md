[← Home](../README.md) · [References](README.md)

# Z80 Opcode Table — One-Page Lookup

Every documented Z80 opcode organised by group, with byte count, T-state cost, and flag effects. Compresses the prose from [z80_instruction_set.md](../01_cpu/z80_instruction_set.md) into scan-able tables. For undocumented opcodes (SLL, `OUT (C),0`, IX/IY half-registers, MEMPTR), see [z80_undocumented.md](../01_cpu/z80_undocumented.md).

> [!NOTE]
> T-states are for unconditional execution at 3.5 MHz (1 T-state = 285 ns). On the ZX Spectrum, add **contention delay** when accessing contended memory or I/O during the screen-rendering window — see [contention_model.md](../05_development/03_memory_and_io/contention_model.md). All timing assumes no `WAIT` insertion.

---

## Quick Cost Reference

| Operand form | Example | T-states | Bytes |
|---|---|---|---|
| Register `r` | `ADD A,B` | 4 | 1 |
| Immediate `n` | `LD A,#42` / `ADD A,#42` | 7 | 2 |
| `(HL)` indirect | `LD A,(HL)` / `ADD A,(HL)` | 7 | 1 |
| `(IX+d)` / `(IY+d)` | `LD A,(IX+#05)` | 19 | 3 |
| `(nn)` absolute (A only) | `LD A,(#4000)` | 13 | 3 |
| `(nn)` absolute (other rp, ED prefix) | `LD BC,(#C000)` | 20 | 4 |

The **register encoding table** used throughout the matrix:

| Index | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 |
|---|---|---|---|---|---|---|---|---|
| Register | B | C | D | E | H | L | (HL) | A |

---

## 1. 8-Bit Load (`LD r,r'` / `LD r,n` / `LD r,(HL)`)

**`LD r,r'`** — 4T, 1 byte, no flags. Opcode matrix `#40`–`#7F`:

```
       B    C    D    E    H    L   (HL)  A
B:   40   41   42   43   44   45   46   47
C:   48   49   4A   4B   4C   4D   4E   4F
D:   50   51   52   53   54   55   56   57
E:   58   59   5A   5B   5C   5D   5E   5F
H:   60   61   62   63   64   65   66   67
L:   68   69   6A   6B   6C   6D   6E   6F
(HL): 70   71   72   73   74   75  [76]  77    #76 = HALT, not LD (HL),(HL)
A:   78   79   7A   7B   7C   7D   7E   7F
```

| Form | Opcode | T | Bytes | Notes |
|---|---|---|---|---|
| `LD r,n` | `06/0E/16/1E/26/2E/36/3E nn` | 7 | 2 | Load immediate |
| `LD r,(HL)` | `46/4E/56/5E/66/6E/76/7E` | 7 | 1 | |
| `LD (HL),r` | `70–77` | 7 | 1 | |
| `LD (HL),n` | `36 nn` | 10 | 2 | |
| `LD A,(BC)` | `0A` | 7 | 1 | |
| `LD A,(DE)` | `1A` | 7 | 1 | |
| `LD (BC),A` | `02` | 7 | 1 | |
| `LD (DE),A` | `12` | 7 | 1 | |
| `LD A,(nn)` | `3A nn nn` | 13 | 3 | |
| `LD (nn),A` | `32 nn nn` | 13 | 3 | |
| `LD r,(IX+d)` / `LD (IX+d),r` | `DD _ d` | 19 | 3 | DD prefix + base opcode + d |
| `LD r,(IY+d)` / `LD (IY+d),r` | `FD _ d` | 19 | 3 | FD prefix |
| `LD (IX+d),n` | `DD 36 d nn` | 19 | 4 | |
| `LD (IY+d),n` | `FD 36 d nn` | 19 | 4 | |

### A ↔ I/R

| Instruction | Opcode | T | Bytes | Flags |
|---|---|---|---|---|
| `LD I,A` | `ED 47` | 9 | 2 | None |
| `LD A,I` | `ED 57` | 9 | 2 | S,Z,H=0; **P/V=IFF2**; N=0 |
| `LD R,A` | `ED 4F` | 9 | 2 | None |
| `LD A,R` | `ED 5F` | 9 | 2 | S,Z,H=0; **P/V=IFF2**; N=0 |

> `LD A,I` / `LD A,R` are the **only documented way to read interrupt state** (IFF2 → P/V). Useful for saving/restoring interrupt enable around NMI.

---

## 2. 16-Bit Load

| Instruction | Opcode | T | Bytes | Notes |
|---|---|---|---|---|
| `LD rp,nn` | `01/11/21/31 lo hi` | 10 | 3 | BC/DE/HL/SP |
| `LD HL,(nn)` | `2A nn nn` | 16 | 3 | No ED prefix |
| `LD (nn),HL` | `22 nn nn` | 16 | 3 | No ED prefix |
| `LD rp,(nn)` | `ED 4B/5B/6B/7B nn nn` | 20 | 4 | BC/DE/HL/SP (ED prefix) |
| `LD (nn),rp` | `ED 43/53/63/73 nn nn` | 20 | 4 | BC/DE/HL/SP (ED prefix) |
| `LD SP,HL` | `F9` | 6 | 1 | Fastest SP set |
| `PUSH rp2` | `C5/D5/E5/F5` | 11 | 1 | BC/DE/HL/AF |
| `POP rp2` | `C1/D1/E1/F1` | 10 | 1 | BC/DE/HL/AF |

> `PUSH` writes high byte first (SP−2=high, SP−1=low); `POP` reads low byte first.

---

## 3. Exchange

| Instruction | Opcode | T | Bytes | Operation |
|---|---|---|---|---|
| `EX DE,HL` | `EB` | 4 | 1 | DE ↔ HL |
| `EX AF,AF'` | `08` | 4 | 1 | AF ↔ AF' |
| `EXX` | `D9` | 4 | 1 | BC/DE/HL ↔ BC'/DE'/HL' |
| `EX (SP),HL` | `E3` | 19 | 1 | HL ↔ (SP) |
| `EX (SP),IX` | `DD E3` | 23 | 2 | |
| `EX (SP),IY` | `FD E3` | 23 | 2 | |

> Minimal ISR save: `EX AF,AF'` + `EXX` = 8T for full register-set swap (vs 42T for `PUSH AF/BC/DE/HL`/`POP HL/DE/BC/AF`).

---

## 4. 8-Bit Arithmetic & Logic

**Pattern:** `OP A,src` where src ∈ `{B,C,D,E,H,L,(HL),A,n}`. The eight operations, indexed by opcode bits 5–3:

| Index | Op | C-flag after |
|---|---|---|
| 0 | `ADD A,src` | Carry from bit 7 |
| 1 | `ADC A,src` | Carry from bit 7 |
| 2 | `SUB src` | Borrow into bit 7 |
| 3 | `SBC A,src` | Borrow into bit 7 |
| 4 | `AND src` | Always reset (0) |
| 5 | `XOR src` | Always reset (0) |
| 6 | `OR src` | Always reset (0) |
| 7 | `CP src` | Borrow (compare) |

All operations update **S, Z, H, P/V, N, C**.

| Source form | Opcode | T | Bytes |
|---|---|---|---|
| `OP A,r` (r=B..A) | `80–BF` (matrix) | 4 | 1 |
| `OP A,(HL)` | `86/8E/96/9E/A6/AE/B6/BE` | 7 | 1 |
| `OP A,n` | `C6/CE/D6/DE/E6/EE/F6/FE nn` | 7 | 2 |
| `OP A,(IX+d)` | `DD _ d` | 19 | 3 |

> `XOR A` is the standard idiom for "set A=0 and clear carry" (4T, 1 byte). FASTER and SHORTER than `LD A,0` + `OR A`.

### INC / DEC (8-bit) — flags updated **except C**

| Form | Opcode | T | Bytes |
|---|---|---|---|
| `INC r` | `04/0C/14/1C/24/2C/34/3C` | 4 | 1 |
| `DEC r` | `05/0D/15/1D/25/2D/35/3D` | 4 | 1 |
| `INC (HL)` | `34` | 11 | 1 | Read-modify-write |
| `DEC (HL)` | `35` | 11 | 1 | |
| `INC (IX+d)` | `DD 34 d` | 23 | 3 | |
| `DEC (IX+d)` | `DD 35 d` | 23 | 3 | |

> `INC`/`DEC` preserve Carry so you can use them as loop counters inside multi-precision arithmetic without disturbing the carry chain.

---

## 5. 16-Bit Arithmetic

| Instruction | Opcode | T | Bytes | Flags |
|---|---|---|---|---|
| `ADD HL,rp` | `09/19/29/39` | 11 | 1 | H, N=0, C; **S,Z,P/V unchanged** |
| `ADC HL,rp` | `ED 4A/5A/6A/7A` | 15 | 2 | All six flags |
| `SBC HL,rp` | `ED 42/52/62/72` | 15 | 2 | All six flags |
| `INC rp` | `03/13/23/33` | 6 | 1 | **No flags affected** |
| `DEC rp` | `0B/1B/2B/3B` | 6 | 1 | **No flags affected** |

> `ADD HL,HL` (`#29`, 11T) is a **16-bit left shift** — the fastest way to multiply HL by 2.
>
> `INC rp` / `DEC rp` affect no flags. To test BC for zero after `DEC BC`: `LD A,B / OR C / JR Z,done`.

---

## 6. General-Purpose Arithmetic

| Instruction | Opcode | T | Bytes | Operation |
|---|---|---|---|---|
| `DAA` | `27` | 4 | 1 | BCD adjust A based on N and C |
| `CPL` | `2F` | 4 | 1 | A = NOT A |
| `NEG` | `ED 44` | 8 | 2 | A = 0 − A |
| `CCF` | `3F` | 4 | 1 | C = NOT C |
| `SCF` | `37` | 4 | 1 | C = 1 |

---

## 7. Rotate & Shift

### Accumulator-only (no CB prefix, inherited from 8080)

| Instruction | Opcode | T | Bytes | Flags |
|---|---|---|---|---|
| `RLCA` | `07` | 4 | 1 | C=old bit 7; H=0, N=0; S,Z,P/V unchanged |
| `RRCA` | `0F` | 4 | 1 | C=old bit 0; H=0, N=0 |
| `RLA` | `17` | 4 | 1 | C=old bit 7; H=0, N=0 |
| `RRA` | `1F` | 4 | 1 | C=old bit 0; H=0, N=0 |

> These are **faster** (4T vs 8T) than `RLC A` etc. Always prefer `RLA` over `RLC A` when rotating A.

### CB-Prefixed Rotate/Shift

**Pattern:** `CB _` (2 bytes for register, 3 for `(HL)`).

| Index | Mnemonic | Operation |
|---|---|---|
| 0 | `RLC r` | Rotate left circular (bit 7 → bit 0 and C) |
| 1 | `RRC r` | Rotate right circular (bit 0 → bit 7 and C) |
| 2 | `RL r` | Rotate left through carry |
| 3 | `RR r` | Rotate right through carry |
| 4 | `SLA r` | Shift left arithmetic (bit 0 = 0) — **multiply by 2** |
| 5 | `SRA r` | Shift right arithmetic (bit 7 preserved) — **signed ÷ 2** |
| 6 | `SLL r` * | Undocumented — shift left, bit 0 = 1 (see [z80_undocumented.md](../01_cpu/z80_undocumented.md)) |
| 7 | `SRL r` | Shift right logical (bit 7 = 0) — **unsigned ÷ 2** |

| Operand | T | Bytes |
|---|---|---|
| Register `r` | 8 | 2 |
| `(HL)` | 15 | 2 |
| `(IX+d)` / `(IY+d)` | 23 | 4 |

All flags updated (S, Z, H=0, P/V=parity, N=0, C).

### RLD / RRD — BCD digit rotation (ED prefix, 18T, 2 bytes)

| Instruction | Opcode | Operation |
|---|---|---|
| `RLD` | `ED 6F` | 12-bit rotate between A's low nibble and (HL)'s two nibbles; A high nibble preserved |
| `RRD` | `ED 67` | Reverse direction |

---

## 8. Bit Manipulation (`BIT b,r` / `SET b,r` / `RES b,r`)

All CB-prefix, 3 operations × 8 bits × 8 registers = 192 instructions.

| Operation | Bytes | T (reg) | T ((HL)) | Flags |
|---|---|---|---|---|
| `BIT b,r` | 2 | 8 | 12 | Z = NOT bit; H=1; N=0; P/V=Z; S set if bit 7 of `(HL)` reads as set |
| `SET b,r` | 2 | 8 | 15 | None |
| `RES b,r` | 2 | 8 | 15 | None |

> `RES 7,(HL)` is the idiomatic "clear bit 7 of memory" (15T, 2 bytes) — used heavily for masking sprites.

---

## 9. Jump

| Instruction | Opcode | T (taken / not taken) | Bytes |
|---|---|---|---|
| `JP nn` | `C3 nn nn` | 10 / 10 | 3 |
| `JP cc,nn` | `C2/CA/D2/DA/E2/EA/F2/FA nn nn` | 10 / 10 | 3 |
| `JP (HL)` | `E9` | 4 | 1 |
| `JP (IX)` | `DD E9` | 8 | 2 |
| `JP (IY)` | `FD E9` | 8 | 2 |
| `JR d` | `18 d` | 12 / 12 | 2 |
| `JR cc,d` (NZ/Z/NC/C only) | `20/28/30/38 d` | 12 / 7 | 2 |
| `DJNZ d` | `10 d` | 13 / 8 | 2 |

**Condition code table** (for `cc`):

| Index | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 |
|---|---|---|---|---|---|---|---|---|
| Condition | NZ | Z | NC | C | PO | PE | P | M |

> `JR` only supports NZ/Z/NC/C (no parity/sign). For PO/PE/P/M you must use `JP cc,nn`.

> `JR d` and `JP nn` cost the same (10T taken, 12T for JR taken) but `JR` is **2 bytes vs 3** — always prefer `JR` when the target is within ±127 bytes.

---

## 10. Call & Return

| Instruction | Opcode | T (taken / not taken) | Bytes |
|---|---|---|---|
| `CALL nn` | `CD nn nn` | 17 | 3 |
| `CALL cc,nn` | `C4/CC/D4/DC/E4/EC/F4/FC nn nn` | 17 / 10 | 3 |
| `RET` | `C9` | 10 | 1 |
| `RET cc` | `C0/C8/D0/D8/E0/E8/F0/F8` | 11 / 5 | 1 |
| `RETI` | `ED 4D` | 14 | 2 | Interrupt return — signals Z80 PIO/CTC to release priority chain |
| `RETN` | `ED 45` | 14 | 2 | NMI return — copies IFF2 → IFF1 |
| `RST p` | `C7/CF/D7/DF/E7/EF/F7/FF` | 11 | 1 | Call to fixed address `00/08/10/18/20/28/30/38` |

> `RST` instructions are 1-byte calls — invaluable for compact ISR dispatchers. The Spectrum 48K ROM uses `RST #38` (single byte `#FF`) as the maskable interrupt entry, which is why IM1 vectors there.

---

## 11. Input / Output

| Instruction | Opcode | T | Bytes | Notes |
|---|---|---|---|---|
| `IN A,(n)` | `DB n` | 11 | 2 | Port address = A8–A15 ← A, A0–A7 ← n |
| `OUT (n),A` | `D3 n` | 11 | 2 | Same addressing |
| `IN r,(C)` | `ED 40–7F` (y≠6) | 12 | 2 | Full 16-bit address from BC |
| `OUT (C),r` | `ED 41–7F` (y≠6) | 12 | 2 | |
| `INI` / `IND` | `ED A2 / ED AA` | 16 | 2 | Single block input, HL±1, B−1 |
| `INIR` / `INDR` | `ED B2 / ED BA` | 21 / 16 | 2 | Repeat until B=0 |
| `OUTI` / `OUTD` | `ED A3 / ED AB` | 16 | 2 | |
| `OTIR` / `OTDR` | `ED B3 / ED BB` | 21 / 16 | 2 | |

> I/O instructions add an **automatic 1 T-state wait** (so 4T minimum per I/O cycle, not 3T like memory). The ZX Spectrum's ULA inserts **additional contention delay** on contended port writes — see [contention_model.md](../05_development/03_memory_and_io/contention_model.md#contended-io).
>
> `OUT (C),0` (y=6 on the ED prefix) is **officially undocumented** — some Z80 variants output 0, others output whatever was on the internal bus. The Spectrum's ULA treats this as "OUT (#FE),#00", which is harmless. See [z80_undocumented.md](../01_cpu/z80_undocumented.md).

---

## 12. Block Transfer & Search (ED Prefix)

| Instruction | Opcode | T | Bytes | Effect |
|---|---|---|---|---|
| `LDI` | `ED A0` | 16 | 2 | (DE) ← (HL); HL+1; DE+1; BC−1; P/V = (BC≠0) |
| `LDD` | `ED A8` | 16 | 2 | Same, HL−1; DE−1 |
| `LDIR` | `ED B0` | 21 / 16 | 2 | Repeat LDI until BC=0; 21T/iter, 16T last |
| `LDDR` | `ED B8` | 21 / 16 | 2 | Repeat LDD until BC=0 |
| `CPI` | `ED A1` | 16 | 2 | A − (HL); HL+1; BC−1; P/V = (BC≠0); Z if A=(HL) |
| `CPD` | `ED A9` | 16 | 2 | Same, HL−1 |
| `CPIR` | `ED B1` | 21 / 16 | 2 | Repeat CPI until BC=0 or match found |
| `CPDR` | `ED B9` | 21 / 16 | 2 | Repeat CPD |

> A `LDIR` of N bytes takes `16 + 5×N` T-states (final iteration is 16T, all others 21T). For copying the Spectrum framebuffer (6912 bytes): 34,816 T-states — about half a frame.

---

## 13. CPU Control

| Instruction | Opcode | T | Bytes | Operation |
|---|---|---|---|---|
| `NOP` | `00` | 4 | 1 | No operation |
| `HALT` | `76` | 4 | 1 | Suspend CPU until INT/NMI (executes NOPs internally to keep refresh alive) |
| `DI` | `F3` | 4 | 1 | Disable maskable interrupts (IFF1=IFF2=0) |
| `EI` | `FB` | 4 | 1 | Enable maskable interrupts (IFF1=IFF2=1); takes effect after the **next** instruction |
| `IM 0` | `ED 46` | 8 | 2 | Interrupt mode 0 (8080-style: instruction on bus) |
| `IM 1` | `ED 56` | 8 | 2 | Interrupt mode 1 (RST #38) |
| `IM 2` | `ED 5E` | 8 | 2 | Interrupt mode 2 (vector table: I × 256 + bus byte) |

> `EI` defers interrupt enablement by one instruction — this lets you write `EI / RET` to safely return from an ISR without being re-interrupted before RET executes.
>
> The ZX Spectrum powers up in **IM 0** but the ROM switches to **IM 1** immediately. Most user programs and ISRs use IM 2 for custom vector dispatch — see [interrupt_programming.md](../05_development/04_interrupts/interrupt_programming.md).

---

## Prefix Pages Summary

| Prefix | Opcode | Valid Instructions | What it does |
|---|---|---|---|
| (none) | `00–FF` except CB/DD/ED/FD | 248 | Main ISA |
| `CB` | `CB 00–FF` | 256 | Bit ops / rotates / shifts |
| `ED` | `ED 00–FF` | ~60 valid | Block ops, 16-bit ADC/SBC, IM, RETI/N, RLD/RRD |
| `DD` | replaces `ED`-prefixed HL ops | mirrors main | HL → IX, (HL) → (IX+d) |
| `FD` | replaces `ED`-prefixed HL ops | mirrors main | HL → IY, (HL) → (IY+d) |
| `DDCB` / `FDCB` | `DD CB d op` / `FD CB d op` | 256 each | Bit ops on (IX+d) / (IY+d) — **4 bytes** |

---

## Cross-References

- [Z80 Instruction Set](../01_cpu/z80_instruction_set.md) — the full prose reference with examples and encoding explanations
- [Z80 Undocumented Instructions](../01_cpu/z80_undocumented.md) — SLL, `OUT (C),0`, IXH/IXL, MEMPTR, etc.
- [Z80 Flags](../01_cpu/z80_flags.md) — detailed flag behaviour per instruction group
- [Z80 Addressing Modes](../01_cpu/z80_addressing.md) — register/immediate/indexed/indirect explanations
- [Z80 Timing](../01_cpu/z80_timing.md) — M-cycles, bus timing, WAIT pin
- [Contention Model](../05_development/03_memory_and_io/contention_model.md) — how the ULA adds delay during screen-rendering windows
- [Interrupt Programming](../05_development/04_interrupts/interrupt_programming.md) — IM0/IM1/IM2 setup and ISR patterns

---

## Primary Sources

- **Zilog Z80 CPU User Manual (UM0080)** — [zilog.com/docs/z80/um0080.pdf](https://www.zilog.com/docs/z80/um0080.pdf). The canonical ISA reference; opcode tables; flag definitions; electrical timing.
- **z80.info** — [z80.info](http://www.z80.info). Community-maintained opcode tables, undocumented behaviour references (Deczl Y Gyr), and per-clone divergence notes.
- **The Undocumented Z80 Documented** — Sean Young's canonical reference for undocumented instructions, MEMPTR/WZ, and flag quirks. Hosted at [mydocuments.nl](http://www.mydocuments.nl/z80/).
- **z80 Instruction Set Reference** — [clrhome.org/support/rgbasm/docs/z80](https://clrhome.org/support/rgbasm/docs/z80/). Online opcode search; useful for quick lookups.
