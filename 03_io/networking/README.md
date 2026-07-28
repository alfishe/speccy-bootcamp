[← Plan](../../PLAN.md) · [Networking](README.md)

# I/O — Networking

This directory covers ZX Spectrum networking: ZX Net, modems, Spectranet, ZiFi, ESP WiFi, and the ZX Spectrum Next's WiFi capability.

## Articles

| # | Article | Description |
|---|---------|-------------|
| 1 | [zx_net.md](zx_net.md) | Sinclair's 1983 classroom local area network for the ZX Spectrum (with the ZX Interface 1): up to 64 stations daisy-chained via ribbon cable, polling-based MAC protocol, packet format, ROM API (`*NET`, `*LOAD name N`), file system, software ecosystem, commercial failure, comparison with Econet, modern emulation in Fuse/ZEsarUX |
| 2 | [modems.md](modems.md) | Telephone-line connectivity for the ZX Spectrum (1982–2000s): acoustic couplers (300 bit/s V.21), direct-connect modems (Prestel 1200/75, V.23, V.22, V.22 bis, V.32, V.34), Spectrum interfaces (Interface 1 RS-232, Kempston SIO, +2A/+3 serial, Beta 128), Prism VTX-5000, Russian modems (Analog 14400, Idustria), Prestel/Micronet 800 videotex services, BBS software (BBStar, Commstar), Russian FidoNet (T-mail mailer), early Internet, modern alternatives (Spectranet/ZiFi/ESP WiFi) |
| 3 | [spectranet.md](spectranet.md) | Modern (2007+) Ethernet + TCP/IP interface for the ZX Spectrum, designed by Andrew Owen: ENC28J60 single-chip 10base-T Ethernet controller via SPI, on-board flash ROM with TCP/IP stack (TCP/UDP/ICMP/DHCP/DNS/HTTP/FTP/telnet/IRC/NTP), hardware compatibility with all Sinclair/clones/modern hardware, ROM API exposed via BASIC extensions (`*` commands) and BSD-style socket API (`RST #08` hook code), software ecosystem (telnet/FTP/HTTP/IRC clients, Spectrum HTTP server, multiplayer games), comparison with ZiFi, IPv4-only, FAQ, summary, references |
| 4 | [zifi.md](zifi.md) | *Planned* — ZiFi: WiFi module for ZX Spectrum, AT command interface |
| 5 | [esp_wifi.md](esp_wifi.md) | *Planned* — ESP-based WiFi: ESP8266/ESP32 modules for various Spectrum interfaces |
| 6 | [zx_next_wifi.md](zx_next_wifi.md) | *Planned* — ZX Spectrum Next WiFi: ESP module, TCP/IP stack |

See [PLAN.md](../../PLAN.md) for the full article catalog.
