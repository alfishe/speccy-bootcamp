#!/usr/bin/env python3
"""
autolink_references.py (v3 - minimal, safe)

Only handles the cleanest transformations:

  Pattern A: **`domain` rest of title** — desc
             → [domain rest of title](url) — desc

  Pattern B: bare domain mentioned in prose (no backticks, no parens)
             → wrap in [domain](url)

Anything else (parens, project names, GitHub repos) is left for manual fixing.
This avoids producing broken markdown.
"""

import os
import re
import sys

SECTION_RE = re.compile(
    r'^#{2,3}\s+(?!.*Cross-?[Rr]ef)(?:\d+(?:\.\d+)*\s+|:\s+)?'
    r'(?:[Ee]xternal\b|[Rr]eferences?\b|[Ss]ources\b|[Ff]urther\s[Rr]eading|'
    r'[Pp]rimary\s[Ss]ources|[Aa]dditional\s[Rr]eferences|'
    r'[Bb]ooks(?:\s+and\s+[Aa]rticles)?|[Mm]agazines?\b|'
    r'[Ww]eb\s+[Rr]eferences|[Oo]nline\s+[Rr]eferences)',
    re.MULTILINE,
)
CROSSREF_SECTION_RE = re.compile(r'^#{2,3}\s.*Cross-?[Rr]ef', re.MULTILINE)
# Conservative: skip ANY bullet that already contains http(s):// anywhere.
# This prevents re-processing bullets that already have URLs (proper links,
# bare URLs, or malformed/nested links from earlier auto-linker runs).
HTTP_URL_RE = re.compile(r'https?://')

DOMAIN_TO_URL = [
    (r'zx-pk\.ru',                'https://zx-pk.ru'),
    (r'zxpress\.ru',              'https://zxpress.ru'),
    (r'worldofspectrum\.org',     'https://worldofspectrum.org'),
    (r'worldofspectrum\.net',     'https://worldofspectrum.net'),
    (r'zxart\.ee',                'https://zxart.ee'),
    (r'zxnext\.io',               'https://zxnext.io'),
    (r'problemkaputt\.de',        'http://problemkaputt.de'),
    (r'nedopc\.com',              'https://nedopc.com'),
    (r'zxevo\.ru',                'https://zxevo.ru'),
    (r'pouet\.net',               'https://www.pouet.net'),
    (r'righto\.com',              'http://www.righto.com'),
    (r'chibiakumas\.com',         'https://chibiakumas.com'),
    (r'speccy\.wiki',             'https://speccy.wiki'),
    (r'speccy\.info',             'https://speccy.info'),
    (r'sinclairfaq\.com',         'http://www.sinclairfaq.com'),
    (r'archive\.org',             'https://archive.org'),
    (r'julien-nevo\.com',         'https://www.julien-nevo.com'),
    (r'mtc\.se',                  'http://mtc.se'),
    (r'k1\.spb\.ru',              'http://k1.spb.ru'),
    (r'speccy\.xyz',              'https://speccy.xyz'),
    (r'speccy\.cz',               'https://speccy.cz'),
    (r'velesoft\.speccy\.cz',    'https://velesoft.speccy.cz'),
    (r'tbbs\.net',                'http://tbbs.net'),
    (r'sdmmc\.sourceforge\.net',  'https://sdcc.sourceforge.net'),
    (r'sdcc\.sourceforge\.net',   'https://sdcc.sourceforge.net'),
    (r'sourceforge\.net',         'https://sourceforge.net'),
    (r'worldofspectrum\.net/zx-modules', 'https://worldofspectrum.net/zx-modules/'),
    (r'elm-chan\.org',              'https://elm-chan.org'),
    (r'bulba\.unterground\.net',    'http://bulba.unterground.net'),
    (r'unterground\.net',           'http://bulba.unterground.net'),
    (r'specnext\.org',              'https://specnext.org'),
    (r'specnext\.dev',              'https://specnext.dev'),
    (r'retroscene\.org',            'https://hype.retroscene.org/'),
    (r'hype\.retroscene\.org',      'https://hype.retroscene.org/'),
    (r'computinghistory\.org\.uk',  'https://www.computinghistory.org.uk/'),
    (r'cpmtools\.sourceforge\.net', 'http://cpmtools.sourceforge.net'),
    # Added 2026-07-19: more domains found in prose External bullets
    (r'zx-art\.ru',                  'http://zx-art.ru'),
    (r'zxbyte\.ru',                  'http://zxbyte.ru'),
    (r'nedopc\.ru',                  'https://nedopc.ru'),
    (r'didaktik\.sk',                'https://www.didaktik.sk'),
    (r'scene\.org',                  'https://www.scene.org'),
    (r'bbb\.retroscene\.org',       'https://bbb.retroscene.org'),
    (r'speedrun\.com',               'https://www.speedrun.com'),
    (r'spectrumcomputing\.co\.uk',   'https://spectrumcomputing.co.uk'),
    (r'spectrum-computing\.co\.uk',  'https://spectrumcomputing.co.uk'),
    (r'vc\.ru',                      'https://vc.ru'),
    (r'sinclair\.wiki',              'https://sinclair.wiki.zx/'),
    (r'github\.com',                 'https://github.com'),
    (r'gitlab\.com',                 'https://gitlab.com'),
    (r'youtube\.com',                'https://www.youtube.com'),
    (r'wikipedia\.org',              'https://en.wikipedia.org'),
    (r'creativecommons\.org',        'https://creativecommons.org'),
    (r'raspberrypi\.com',            'https://www.raspberrypi.com'),
    (r'raspberrypi\.org',            'https://www.raspberrypi.org'),
    (r'analog\.com',                 'https://www.analog.com'),
    (r'ti\.com',                     'https://www.ti.com'),
    (r'intel\.com',                  'https://www.intel.com'),
    (r'zilog\.com',                  'https://www.zilog.com'),
    (r'espressif\.com',              'https://www.espressif.com'),
    (r'goodreads\.com',              'https://www.goodreads.com'),
    (r'amigadev\.elowar\.com',      'https://www.amigadev.elowar.com'),
    (r'hex-rays\.com',               'https://hex-rays.com'),
    (r'ghidra-sre\.org',             'https://ghidra-sre.org'),
    (r'demozoo\.org',                'https://demozoo.org'),
    (r'ganssle\.com',                'https://www.ganssle.com'),
    (r'arxiv\.org',                  'https://arxiv.org'),
    (r'datatracker\.ietf\.org',     'https://datatracker.ietf.org'),
    (r'groups\.google\.com',        'https://groups.google.com'),
    (r'computer-engineering\.org',   'https://www.computer-engineering.org'),
    (r'ddwg\.org',                   'https://www.ddwg.org'),
    (r'hdmi\.org',                   'https://www.hdmi.org'),
    (r'usb\.org',                    'https://www.usb.org'),
    (r'sdcard\.org',                 'https://www.sdcard.org'),
]

# Pattern A: bullet starts with **`domain`...** (backticked domain inside bold)
# Captures the rest of the title (between closing backtick and closing **)
PAT_A = re.compile(
    r'^\*\*`((?:' + '|'.join(pat for pat, _ in DOMAIN_TO_URL) + r'))`\s*(.*?)\*\*', re.IGNORECASE
)

# Pattern B: bare domain in prose (no preceding code/link/paren)
PAT_B = re.compile(
    r'(?<![`/\[(.])(' + '|'.join(pat for pat, _ in DOMAIN_TO_URL) + r')(?![/)`])', re.IGNORECASE
)

# Pattern C: **Title** (Author, `domain/path`) — common form in batch-6 articles
# Captures: group(1) = Title, group(2) = full backticked content (domain or domain/path)
_DOMAIN_OR_PATH = r'(?:https?://)?(?:' + '|'.join(pat for pat, _ in DOMAIN_TO_URL) + r')(?:/[^`]+)?'
_GITHUB_PATH = r'(?:https?://)?github\.com/[A-Za-z0-9_-]+/[A-Za-z0-9_.-]+'
PAT_C = re.compile(
    r'^\*\*([^*]+?)\*\*\s+\([^)]*?,\s*`(' + _DOMAIN_OR_PATH + r'|' + _GITHUB_PATH + r')`\)', re.IGNORECASE
)

# Pattern D: **Title** (`domain`) — backticked domain in trailing parens (no author)
PAT_D = re.compile(
    r'^\*\*([^*]+?)\*\*\s+\(`(' + _DOMAIN_OR_PATH + r')`\)', re.IGNORECASE
)

# Pattern I: **Title** (`domain` extra) — backticked domain with trailing text in parens
# e.g., **TS-Conf documentation** (`zxevo.ru` wiki) — desc
PAT_I = re.compile(
    r'^\*\*([^*]+?)\*\*\s+\(`(' + _DOMAIN_OR_PATH + r')`\s+[^)]*\)', re.IGNORECASE
)

# Pattern K: **domain** — bolded bare domain without backticks (e.g., **velesoft.speccy.cz**)
PAT_K = re.compile(
    r'^\*\*(' + '|'.join(pat for pat, _ in DOMAIN_TO_URL) + r')\*\*', re.IGNORECASE
)

# Pattern E: **Title** (domain) — bare domain in parens, no backticks
PAT_E = re.compile(
    r'^\*\*([^*]+?)\*\*\s+\(((?:https?://)?(?:' + '|'.join(pat for pat, _ in DOMAIN_TO_URL) + r')(?:/[^)]+)?)\)', re.IGNORECASE
)

# Pattern F: **Title** (`https://full-url/`) — full URL already in backticks
PAT_F = re.compile(
    r'^\*\*([^*]+?)\*\*\s+\(`((?:https?://)[^`]+)`\)'
)

# Pattern H: **Title (`domain`)** — backticked domain in parens INSIDE the bold span
# e.g., **ZXArt (`zxart.ee`)** — desc
PAT_H = re.compile(
    r'^\*\*([^(*]+?)\s+\(`(' + '|'.join(pat for pat, _ in DOMAIN_TO_URL) + r')`\)\*\*', re.IGNORECASE
)

# Pattern G: Named source mapping (e.g., Chris Smith ULA book, Spectrumpedia, magazines)
# Each entry: (regex_pattern, url) — applied to ANY bullet without http URL
NAMED_SOURCES = [
    (r'Chris Smith.*ZX Spectrum ULA',                       'http://www.zxdesign.info/'),
    (r'ZX Spectrum ULA.*How to Design',                     'http://www.zxdesign.info/'),
    (r'Complete Spectrum ROM Disassembly',                  'https://worldofspectrum.org/ROMdisassembly.zip'),
    (r"Logan.*O.Hara",                                       'https://worldofspectrum.org/ROMdisassembly.zip'),
    (r'Tony Stratton.*Spectrum ROM Disassembly',            'https://worldofspectrum.org/ROMdisassembly.zip'),
    (r'Spectrumpedia.*Grussu',                              'https://speccy.wiki/'),
    (r'Alessandro Grussu.*Spectrumpedia',                   'https://speccy.wiki/'),
    (r'\bSpectrumpedia\b',                                  'https://speccy.wiki/'),
    (r'Sinclair ZX Specifications.*Korth',                  'http://problemkaputt.de/zxdocs.htm'),
    (r'\bMartin Korth\b',                                   'http://problemkaputt.de/zxdocs.htm'),
    (r'\bCrash magazine\b',                                 'https://archive.org/details/crash-magazine'),
    (r'\bYour Sinclair\b',                                  'https://archive.org/details/yoursinclair-magazine'),
    (r'\bSinclair User\b',                                  'https://archive.org/details/sinclair-user-magazine'),
    (r'\bZX-Format\b',                                      'https://zxpress.ru/library/categories.php?id=2'),
    (r'\bSpectrofon\b',                                     'https://zxpress.ru/library/categories.php?id=4'),
    (r'\bAdventurer.*magazine\b',                           'https://zxpress.ru/library/categories.php?id=8'),
    (r'\bZX-Review\b',                                      'https://zxpress.ru/library/'),
    (r'\bRodnay Zaks\b',                                    'https://en.wikipedia.org/wiki/Rodnay_Zaks'),
    (r'Programming the Z80',                                 'https://www.goodreads.com/book/show/1840904.Programming_the_Z80'),
    (r'\bDemozoo\b',                                        'https://demozoo.org/'),
    (r'\bPouet\b',                                          'https://www.pouet.net/'),
    (r'\bSpeedlock\b',                                      'https://worldofspectrum.org/forums/discussion/52570/'),
    (r'\bAlkatraz\b',                                       'https://worldofspectrum.org/forums/discussion/52570/'),
    (r'\bTipshop\b',                                        'https://thetipshop.org/'),
    (r'\bThe Tipshop Archive\b',                            'https://thetipshop.org/'),
    (r'\bWoS archive\b',                                    'https://worldofspectrum.org/'),
    (r'\bWorld of Spectrum\b',                              'https://worldofspectrum.org/'),
    (r'\bWoS forums?\b',                                    'https://worldofspectrum.org/forums/'),
    (r'\bcomp\.sys\.sinclair\b',                           'https://groups.google.com/g/comp.sys.sinclair'),
    (r'\bIDA Pro\b',                                        'https://hex-rays.com/ida-pro/'),
    (r'\bGhidra\b',                                         'https://ghidra-sre.org/'),
    (r'\bDeZog\b',                                          'https://github.com/maziac/DeZog'),
    (r'\bz88dk-appmake\b',                                  'https://github.com/z88dk/z88dk/wiki/appmake'),
    (r'\bz88dk\b',                                          'https://github.com/z88dk/z88dk'),
    (r'\bsjasmplus\b',                                      'https://github.com/z00m128/sjasmplus'),
    (r'\bsdcc\b',                                           'https://sdcc.sourceforge.net/'),
    (r'\bPasmo\b',                                          'https://www.naslag.info/pasmo/'),
    (r'\bZX Spectrum Next Weekend Assembly\b',               'https://zxnext.io/'),
    (r'\bNextZXOS\b',                                       'https://gitlab.com/thesmog358/tbblue'),
    (r'\bSpecEmu\b',                                        'https://sourceforge.net/projects/specemu/'),
    (r'\bUnrealSpeccy\b',                                   'https://sdkcad.free.fr/'),
    (r'\bZEsarUX\b',                                        'https://github.com/chernandezba/zesarux'),
    (r'\bFuse\b.*emulator',                                 'https://fuse-emulator.sourceforge.net/'),
    (r'\bAmstrad.*Service Manual\b',                        'https://www.worldofspectrum.org/hardware.html'),
    (r'\bSinclair.*Service Manual\b',                       'https://www.worldofspectrum.org/hardware.html'),
    (r'\bAmstrad.*User Manual\b',                           'https://www.worldofspectrum.org/hardware.html'),
    (r'\bZX Spectrum.*Manual\b',                            'https://www.worldofspectrum.org/hardware.html'),
    (r'\bIEEE 754\b',                                       'https://en.wikipedia.org/wiki/IEEE_754'),
    (r'\bATA/ATAPI\b',                                      'https://www.t13.org/standards'),
    (r'\bSD.*Specification\b',                              'https://www.sdcard.org/downloads/'),
    (r'\bFAT.*Specification\b',                             'https://learn.microsoft.com/en-us/windows/win32/fileio/exfat-specification'),
    (r'\bGreaseWeazle\b',                                   'https://github.com/keirf/Greaseweazle'),
    (r'\bKryoFlux\b',                                       'https://kryoflux.com/'),
    (r'\bsamdisk\b',                                        'https://github.com/samdisk71/samdisk'),
    (r'\blibdsk\b',                                         'https://www.danceswithferrets.org/gnu/libdsk/'),
    (r'\bZX-Blockeditor\b',                                 'https://www.raxoft.de/'),
    (r'\bspeedlock\.net\b',                                'https://speedrun.net/'),
    (r'Gerton Lunter.*Multicolor',                          'https://worldofspectrum.org/'),
    (r"Andrew Owen.*Multicolor Tutorial",                   'https://worldofspectrum.org/forums/'),
    (r'\bZXMak\b',                                          'https://worldofspectrum.org/'),
    (r'\bUnreal.*Speccy\b',                                 'https://sdkcad.free.fr/'),
    (r'\bESXDOS\b',                                         'https://github.com/joneiricon/ESXDOS'),
    (r'\.tzx\b.*Format.*Spec',                              'https://worldofspectrum.org/TZXformat.html'),
    (r'\.tap\b.*Format',                                    'https://worldofspectrum.org/faq/reference/formats.htm'),
    (r'\.scr\b.*Format',                                    'https://worldofspectrum.org/faq/reference/formats.htm'),
    (r'\.z80\b.*Format.*Spec',                              'https://worldofspectrum.org/z80format/'),
    # Tools and packers
    (r'\bzx7\b.*Villena|Antonio Villena.*zx7',              'https://github.com/AntoniVillena/zx7'),
    (r'\bzx7\b',                                            'https://github.com/AntoniVillena/zx7'),
    (r'\bMegaLZ\b',                                         'https://github.com/ladislav-zezula/MegaLZ'),
    (r'\blz4\b',                                            'https://github.com/lz4/lz4'),
    (r'\baplib\b|\baPLib\b',                               'https://ibsensoftware.com/products_aplib.html'),
    (r'\bExomizer\b',                                       'https://bitbucket.org/magli143/exomizer/wiki/Home'),
    (r'\bPucrunch\b',                                       'https://github.com/mhaben/pucrunch'),
    (r'\bz88dk-appmake\b',                                  'https://github.com/z88dk/z88dk/wiki/appmake'),
    (r'\bSevenUp\b.*[Pp]lus|SevenUp Plus',                  'https://worldofspectrum.org/'),
    (r'\bSevenUp\b',                                        'https://worldofspectrum.org/'),
    (r'\bZX Paintbrush\b',                                  'https://www.usebox.net/jjm/zxpaintbrush/'),
    (r'\bZX-Modules\b',                                     'https://worldofspectrum.net/zx-modules/'),
    (r'\bpng2scr\b',                                        'https://github.com/reidrac/png2scr'),
    (r'\bzx-tools\b',                                       'https://github.com/anton-bulanov/zx-tools'),
    (r'\bArkos Tracker\b',                                  'https://www.julien-nevo.com/arkostracker/'),
    (r'\bWally\b.*[Bb]epler|\bBepler\b',                   'https://worldofspectrum.org/'),
    (r'\bZX Spectrum Next Weekend Assembly\b',               'https://zxnext.io/'),
    (r'\bSpecEmu\b',                                        'https://sourceforge.net/projects/specemu/'),
    (r'\bZero\b.*emulator|\bZEsarUX\b',                    'https://github.com/chernandezba/zesarux'),
    # Hardware / peripherals
    (r'\bSpectranet\b',                                     'https://github.com/spectrum-pi/spectranet'),
    (r'\bDivIDE\b',                                         'https://github.com/westonrf/divide-ide'),
    (r'\bDivMMC\b',                                         'https://github.com/westonrf/divide-ide'),
    (r'\bZXMMC\b',                                          'https://github.com/Zaxos/ZXMMC'),
    (r'\bZX-Uno\b',                                         'https://github.com/zxdos/zx-uno'),
    (r'\bMB02\b',                                           'https://worldofspectrum.org/'),
    (r'\bPlus D\b',                                         'https://worldofspectrum.org/'),
    (r'\bOpus Discovery\b',                                 'https://worldofspectrum.org/'),
    (r'\bInterface 1\b|\bInterface I\b',                   'https://worldofspectrum.org/'),
    (r'\bSpeccyTelnet\b|\bSpeccyIRC\b',                   'https://github.com/spectrum-pi/spectranet'),
    (r'\bTelnet BBS Guide\b|\btbbs\.net\b',               'http://tbbs.net/'),
    (r'\bKen Shirriff\b',                                   'http://www.righto.com/'),
    (r'\bAndrew Owen\b',                                    'https://github.com/spectrum-pi/spectranet'),
    # Russian / Soviet specific
    (r'\bTS-Conf\b',                                        'https://zxevo.ru/'),
    (r'\bBaseConf\b',                                       'https://nedopc.com/'),
    (r'\bNedoDOS\b',                                        'https://nedopc.com/'),
    (r'\bDivMMC\b',                                         'https://nedopc.com/'),
    (r'\bPentagon\b.*schematic|\bPentagon\b.*hardware',   'https://zx-pk.ru/'),
    (r'\bKay\b.*2006|\bKay\b.*CPLD',                       'https://zxpress.ru/'),
    (r'\bVelesoft\b',                                       'https://velesoft.speccy.cz/'),
    (r'\bGasman\b.*Compatibility|\bGasman\b.*Russian',     'https://zxpress.ru/'),
    (r'\bIvan Roshchin\b',                                  'https://zxpress.ru/'),
    (r'\bSubliminal Extacy\b',                              'https://zxart.ee/'),
    # Books and resources
    (r'\bSpectrum Compendium\b',                            'https://archive.org/'),
    (r"O'Hara",                                              'https://worldofspectrum.org/ROMdisassembly.zip'),
    (r"\bLogan\b.*ROM",                                     'https://worldofspectrum.org/ROMdisassembly.zip'),
    (r'\bRodnay Zaks\b',                                    'https://en.wikipedia.org/wiki/Rodnay_Zaks'),
    (r'\bProgramming the Z80\b',                            'https://www.goodreads.com/book/show/1840904.Programming_the_Z80'),
    (r'\bComp.sys.sinclair\b',                              'https://groups.google.com/g/comp.sys.sinclair'),
    (r'\bdef-guide\b|\bDefinitive Guide\b',               'https://worldofspectrum.org/'),
    (r'\bMelbourne House\b',                                'https://archive.org/'),
    (r'\bHewson\b',                                         'https://archive.org/'),
    (r'\bUltimate Play the Game\b',                         'https://archive.org/'),
    (r'\bGremlin Graphics\b',                               'https://archive.org/'),
    (r'\bImagine Software\b',                               'https://archive.org/'),
    (r'\bOcean Software\b',                                 'https://archive.org/'),
    # MCU / modern hardware
    (r'\bRP2040\b|\bRP2350\b',                            'https://www.raspberrypi.com/documentation/microcontrollers/'),
    (r'\bRaspberry Pi Pico\b',                              'https://www.raspberrypi.com/documentation/microcontrollers/'),
    (r'\bPicoVGA\b',                                        'https://github.com/Panda385/PicoVGA'),
    (r'\bPico DVI\b',                                       'https://github.com/Wren6991/pico-dvi'),
    (r'\bRGB-to-HDMI\b|\bRGBtoHDMI\b',                    'https://github.com/hoglet67/RGBtoHDMI'),
    (r'\bADV7513\b',                                        'https://www.analog.com/en/products/adv7513.html'),
    (r'\bADV7125\b',                                        'https://www.analog.com/en/products/adv7125.html'),
    (r'\bTinyUSB\b',                                        'https://github.com/hathach/tinyusb'),
    (r'\bTinyVGA\b',                                        'https://gitlab.com/b9lab/tinyvga'),
    (r'\bRetroleum\b',                                      'https://retroleum.co.uk/'),
    (r'\bZX-HD\b',                                          'https://retroleum.co.uk/'),
    (r'\bSMARTi\b',                                         'https://retroleum.co.uk/'),
    (r'\bSpectra\b.*adapter|\bSpectra\b.*video',           'https://retroleum.co.uk/'),
    # Electronics / datasheets
    (r'\b74HCT245\b|\b74HCT541\b',                        'https://www.ti.com/lit/ds/symlink/sn74hct245.pdf'),
    (r'\b74LVC245\b',                                       'https://www.ti.com/lit/ds/symlink/sn74lvc245a.pdf'),
    (r'\bTXB0108\b|\bTXS0108E\b',                         'https://www.ti.com/lit/ds/symlink/txb0108.pdf'),
    (r'\bZilog Z80\b.*[Dd]atasheet|\bZ84C00\b',            'https://www.zilog.com/docs/z80/um0080.pdf'),
    (r'\bZ80 CPU Manual\b|\bZ80 CPU User Manual\b',        'https://www.zilog.com/docs/z80/um0080.pdf'),
    (r'\bARM Cortex-M0\b|\bCortex-M0\+\b',               'https://developer.arm.com/documentation/dui0662/b/'),
    (r'\bDVI specification\b|\bDVI spec\b',                'https://www.ddwg.org/'),
    (r'\bVGA timing\b',                                     'https://en.wikipedia.org/wiki/VGA-compatible_text_mode'),
    (r'\bHDMI specification\b|\bHDMI spec\b',              'https://www.hdmi.org/'),
    (r'\bUSB HID\b',                                        'https://usb.org/document-library/usb-hid-usage-tables-14'),
    (r'\bPS/2 Keyboard Protocol\b|\bPS/2 protocol\b',     'https://www.computer-engineering.org/ps2keyboard/'),
    (r'\bAdam Chapweske\b',                                 'https://www.computer-engineering.org/ps2keyboard/'),
    (r'\bJack Ganssle\b|\bGanssle.*[Dd]ebounce\b',         'https://www.ganssle.com/debouncing.htm'),
    (r'\bEli Hughes\b',                                     'https://www.youtube.com/user/emnhub'),
    (r'\bKempston\b.*joystick|\bKempston\b.*interface',   'https://worldofspectrum.org/'),
    (r'\bKempston\b.*mouse',                                'https://worldofspectrum.org/'),
    # Famous compressors / authors
    (r'\bYann Collet\b|\bLZ4 Block Format\b',             'https://github.com/lz4/lz4'),
    (r'\bPasi Ojala\b|\bpucrunch.*Optimizing\b',          'https://github.com/mhaben/pucrunch'),
    (r'\bJarek Duda\b|\basymmetric numeral systems\b',    'https://arxiv.org/abs/1311.2540'),
    (r'\bPaul G\. Howard\b|\bJeffrey S\. Vitter\b',      'https://www.cs.brown.edu/cgc/stc/ddms/'),
    (r'\bCharles Bloom\b|\bcbloom\b',                     'http://cbloomrants.blogspot.com/'),
    (r'\bPhil Katz\b|\bDEFLATE.*RFC\b|\bRFC 1951\b',     'https://datatracker.ietf.org/doc/html/rfc1951'),
    (r'\bIntrospec\b.*compression|\bencode\.su.*8-bit\b', 'https://encode.su/threads/1893-State-of-the-art-byte-compression-for-8-bit-computers'),
    (r'\bEinar Saukas\b',                                   'https://github.com/einar-saukas'),
    (r'\bEmmanuel Marty\b',                                 'https://github.com/emmanuel-marty'),
    # Magazines / publications (broader)
    (r'\bMicronet 800\b',                                   'https://archive.org/'),
    (r'\bPrestel\b',                                        'https://archive.org/'),
    (r'\bVTX-5000\b',                                       'https://archive.org/'),
    (r'\bSpectrum Computing\b.*archive',                    'https://spectrumcomputing.co.uk/'),
    (r'\bspectrumcomputing\.co\.uk\b',                    'https://spectrumcomputing.co.uk/'),
    (r'\bZX-Spectrum\.info\b|\bzx-spectrum\.info\b',     'https://speccy.info/'),
    (r'\bdef-guide\b|\bDefinitive Guide\b',               'https://worldofspectrum.org/'),
    # More tools / libraries
    (r'\bFatFs\b.*Elm-Chan|\bElm-Chan\b',                  'https://elm-chan.org/fsw/ff/00index_e.html'),
    (r'\bVortex Tracker\b',                                'http://bulba.unterground.net/'),
    (r'\bcpmtools\b',                                      'http://cpmtools.sourceforge.net/'),
    (r'\bPicoROM\b',                                       'https://github.com/MarkOdnw/PR'),
    (r'\bSE BASIC\b|\bOpenSE BASIC\b',                    'https://github.com/cheveron/sebasic'),
    (r'\bAltera MAX II\b|\bMAX II CPLD\b',                'https://www.intel.com/content/www/us/en/products/details/fpga/max.html'),
    (r'\bEPM240\b|\bEPM570\b|\bEPM1270\b',              'https://www.intel.com/content/www/us/en/products/details/fpga/max.html'),
    (r'\bWD179[0-9X]\b|\bVG93\b|\bFD179\b',             'https://www.worldofspectrum.org/hardware.html'),
    (r'\bWestern Digital.*Floppy',                          'https://www.worldofspectrum.org/hardware.html'),
    (r'\bapp\.note 17\b|\bapp note 17\b',                 'https://www.worldofspectrum.org/hardware.html'),
    (r'\bCentre for Computing History\b',                  'https://www.computinghistory.org.uk/'),
    (r'\bComputing History\b',                             'https://www.computinghistory.org.uk/'),
    (r'\bSprinter FAQ\b|\bPeters Plus\b',                 'https://zxpress.ru/'),
    (r'\bAlex Goryachev\b',                                'https://zxpress.ru/'),
    (r'\bAY-3-8912.*register|\bAY-3-8910.*register',       'http://www.worldofspectrum.org/'),
    (r'\bVortex II\b',                                     'http://bulba.unterground.net/'),
    (r'\bBulba\b',                                         'http://bulba.unterground.net/'),
    (r'\bMoonSound\b',                                     'https://www.msx.org/wiki/MoonSound'),
    (r'\bRetroGFX\b',                                      'https://github.com/'),
    (r'\bRamsoft\b.*ROM|\bRamsoft\b.*fault',             'https://worldofspectrum.org/'),
    (r"\bSpectrum ROM disassembly\b|\bSpectrum's ROM disassembly", 'https://worldofspectrum.org/ROMdisassembly.zip'),
    (r'\bAlone Coder\b',                                   'https://zxpress.ru/'),
    (r'\bACNews\b',                                        'https://zxpress.ru/'),
    (r'\bKramis\b|\bCondor\b.*Profi',                    'https://zx-pk.ru/'),
    (r'\bTurboSound Next\b',                               'https://specnext.org/'),
    (r'\bTBBlue\b',                                        'https://specnext.org/'),
    (r'\bPentagon 1024\b.*specification',                  'https://zx-pk.ru/'),
    (r'\bHarlequin project\b|\bHarlequin\b.*Chris Smith', 'http://www.zxdesign.info/'),
    (r'\bZX Spectrum Next forum\b',                        'https://specnext.org/'),
    (r'\bZX Spectrum Next Weekend Assembly\b',              'https://zxnext.io/'),
    (r'\bZX Spectrum Next.*documentation\b',                'https://specnext.dev/'),
    # Cross-platform archives (other platforms)
    (r'\bCSDb\.dk\b|\bCSDb\b.*Commodore',                  'https://csdb.dk/'),
    (r'\bHall of Light\b|\bhol\.abime\.net\b',              'https://hol.abime.net/'),
    (r'\bAtariLegend\b',                                    'https://www.atarilegend.com/'),
    (r'\batarimania\.com\b',                                'https://www.atarimania.com/'),
    (r'\bGeneration-MSX\b|\bgeneration-msx\.nl\b',          'https://www.generation-msx.nl/'),
    (r'\bCPC-Wiki\b|\bcpc-wiki\.eu\b',                      'https://www.cpc-wiki.eu/'),
    (r'\bAmstrad WWW Repository\b|\bCPC Repository\b',       'https://www.cpcwiki.eu/'),
    (r'\bChristian Bauer\b.*Amiga|\bSecret of the Amiga\b',  'https://www.amigadev.elowar.com/'),
    (r'\bCommodore 64 Programmer.*Reference\b',              'https://www.ko-wapper.de/hp/c64-prg/'),
    (r'\bAtari ST Profibuch\b|\bDon French\b.*Atari',        'https://www.atariarchives.org/'),
    (r'\bMSX RED Book\b|\bMSX Red Book\b',                   'https://www.msxarchive.nl/'),
    (r'\bUNESCO.*demoscene\b|\bdemoscene.*UNESCO\b',         'https://en.wikipedia.org/wiki/Demoscene'),
    (r'\bRevision demoparty\b',                              'https://revisionparty.net/'),
    (r'\bPiotr Marecki\b|\bDemoscena ZX Spectrum\b',         'https://press.uj.edu.pl/catalog/'),
    # ESP / WiFi
    (r'\bESP8266\b|\bESP-IDF\b',                            'https://www.espressif.com/en/support/documents/technical-documents'),
    (r'\bEspressif\b',                                      'https://www.espressif.com/'),
    (r'\bArduino-ESP8266\b',                                'https://github.com/esp8266/Arduino'),
    (r'\bZiFi\b.*project|\bZiFi\b.*WiFi',                   'https://zx-pk.ru/'),
    (r'\bParadise WiFi\b',                                  'https://zx-pk.ru/'),
    (r'\bWiC64\b',                                          'https://www.wic64.de/'),
    # FPGA / hardware
    (r'\bSprinter\b.*Peters|\bPeters Plus\b',                'https://zxpress.ru/'),
    (r'\bSizif\b.*Harlequin|\bSizif\b.*ZX',                 'https://github.com/MarkOdnw/Sizif'),
    (r'\bHarlequin\b',                                      'http://www.zxdesign.info/'),
    (r'\bZXUno\b|\bZX-Uno\b',                               'https://github.com/zxdos/zx-uno'),
    (r'\bMister\b.*Spectrum|\bMiSTer\b.*ZX',                'https://github.com/MiSTer-devel/ZX-Spectrum_MiSTer'),
    # Software / formats
    (r'\bOpus Discovery\b',                                 'https://worldofspectrum.org/'),
    (r'\bAlasm\b|\bALASM\b',                                'https://zxpress.ru/'),
    (r'\bSTS\b.*tracker|\bSTS\b.*SounDrive',                'https://zxpress.ru/'),
    (r'\bzxasm\b|\bZXASM\b',                                'https://zxpress.ru/'),
    (r'\bXAS\b.*assembler|\bXAS\b.*compiler',                'https://zxpress.ru/'),
    (r'\bSjASM\b|\bsjasmplus\b',                           'https://github.com/z00m128/sjasmplus'),
    (r'\bPasmo\b',                                          'https://www.naslag.info/pasmo/'),
    (r'\bTNASM\b|\btapecut\b',                              'https://zxpress.ru/'),
    (r'\bZDevStudio\b|\bzdevstudio\b',                      'https://github.com/z00m128/zdevstudio'),
    # Compression tools
    (r'\bZX0\b',                                            'https://github.com/einar-saukas/ZX0'),
    (r'\bZX1\b',                                            'https://github.com/einar-saukas/ZX0'),
    (r'\bZX2\b',                                            'https://github.com/einar-saukas/ZX0'),
    (r'\bLZSA\b',                                           'https://github.com/emmanuel-marty/lzsa'),
    (r'\bRCS\b.*reversible|\bRCS\b.*screen',                'https://github.com/einar-saukas/rcs'),
    (r'\bHRUM\b|\bHRUST\b',                                'https://github.com/lvd2/mhmt'),
    (r'\bmhmt\b',                                           'https://github.com/lvd2/mhmt'),
    (r'\boh1c\b|\boh2c\b',                                  'https://zx-pk.ru/'),
]


def _url_for_domain(domain_str):
    for pat, url in DOMAIN_TO_URL:
        if re.fullmatch(pat, domain_str, re.IGNORECASE):
            return url
    return 'https://' + domain_str.lower()


def _resolve_backticked(s):
    """Given a backticked string like 'problemkaputt.de/zxdocs.htm' or
    'github.com/USER/REPO', return the canonical URL."""
    # Strip any leading http(s)://
    s = re.sub(r'^https?://', '', s)
    # GitHub?
    m = re.match(r'^(github\.com/[A-Za-z0-9_-]+/[A-Za-z0-9_.-]+)', s)
    if m:
        return 'https://' + m.group(1)
    # Known domain?
    for pat, url in DOMAIN_TO_URL:
        m = re.match(pat, s, re.IGNORECASE)
        if m:
            # If there's a path beyond the domain, use the full string as URL
            if len(s) > m.end():
                return 'https://' + s if not s.startswith('problemkaputt') else 'http://' + s
            return url
    # Fallback
    return 'https://' + s


def transform_bullet(text):
    """Return (new_text, changed). Skip if bullet already has http URL."""
    if HTTP_URL_RE.search(text):
        return text, False

    # Pattern A: **`domain` rest** → [domain rest](url)
    m = PAT_A.match(text)
    if m:
        domain = m.group(1)
        rest = m.group(2)
        url = _url_for_domain(domain)
        # Build link text: domain + (space + rest) if rest is non-empty
        link_text = domain + (f' {rest}' if rest else '')
        replacement = f'[{link_text}]({url})'
        new_text = replacement + text[m.end():]
        return new_text, True

    # Pattern C: **Title** (Author, `domain/path`) → [Title](url)
    m = PAT_C.match(text)
    if m:
        title = m.group(1)
        backticked = m.group(2)  # e.g., 'problemkaputt.de/zxdocs.htm' or 'github.com/USER/REPO'
        url = _resolve_backticked(backticked)
        after = text[m.end():]
        sep = ' ' if after and not after[0].isspace() else ''
        new_text = f'[{title}]({url})' + sep + after
        return new_text, True

    # Pattern D: **Title** (`domain`) → [Title](url)
    m = PAT_D.match(text)
    if m:
        title = m.group(1)
        backticked = m.group(2)
        url = _resolve_backticked(backticked)
        after = text[m.end():]
        sep = ' ' if after and not after[0].isspace() else ''
        new_text = f'[{title}]({url})' + sep + after
        return new_text, True

    # Pattern I: **Title** (`domain` extra) — backticked domain + trailing text in parens
    m = PAT_I.match(text)
    if m:
        title = m.group(1)
        backticked = m.group(2)
        url = _resolve_backticked(backticked)
        after = text[m.end():]
        sep = ' ' if after and not after[0].isspace() else ''
        new_text = f'[{title}]({url})' + sep + after
        return new_text, True

    # Pattern K: **domain** — bolded bare domain (e.g., **velesoft.speccy.cz**)
    m = PAT_K.match(text)
    if m:
        domain = m.group(1)
        url = _url_for_domain(domain)
        after = text[m.end():]
        sep = ' ' if after and not after[0].isspace() else ''
        new_text = f'[{domain}]({url})' + sep + after
        return new_text, True

    # Pattern E: **Title** (domain) — bare domain in parens
    m = PAT_E.match(text)
    if m:
        title = m.group(1)
        bare = m.group(2)
        url = _resolve_backticked(bare)
        after = text[m.end():]
        sep = ' ' if after and not after[0].isspace() else ''
        new_text = f'[{title}]({url})' + sep + after
        return new_text, True

    # Pattern F: **Title** (`https://full-url`) → [Title](full-url)
    m = PAT_F.match(text)
    if m:
        title = m.group(1)
        url = m.group(2)
        after = text[m.end():]
        sep = ' ' if after and not after[0].isspace() else ''
        new_text = f'[{title}]({url})' + sep + after
        return new_text, True

    # Pattern H: **Title (`domain`)** — backticked domain in parens INSIDE bold
    m = PAT_H.match(text)
    if m:
        title = m.group(1).strip()
        domain = m.group(2)
        url = _url_for_domain(domain)
        after = text[m.end():]
        sep = ' ' if after and not after[0].isspace() else ''
        new_text = f'[{title}]({url})' + sep + after
        return new_text, True

    # Pattern G: Named source mapping — find known source in TITLE, build link
    # CRITICAL: when there's a leading **bold title**, only consider matches that
    # occur INSIDE the title text. This prevents words like "Speedlock" in the
    # description from hijacking the URL of a bullet whose title is unrelated.
    bold_match = re.match(r'^\*\*(.+?)\*\*(?:\*|\s|\(|,|\.|;|:|$)', text)
    if bold_match:
        title = bold_match.group(1)
        # If title has unmatched italic markers (odd count of *), strip them
        if title.count('*') % 2 == 1:
            title = title.replace('*', '')
        for pat, url in NAMED_SOURCES:
            if ' ' in url or not url.startswith(('http', 'https')):
                continue
            if re.search(pat, title, re.IGNORECASE):
                # Compute the after-text (post bold close)
                after_stars = text[bold_match.end()-1:]
                skip = 0
                while after_stars[skip:skip+1] == '*':
                    skip += 1
                after = text[bold_match.end()-1 + skip:]
                if after.startswith(' '):
                    after = after[1:]
                paren_match = re.match(r'^\([^)]*\)\s*', after)
                if paren_match:
                    after = after[paren_match.end():]
                # Don't add separator if after starts with space or punctuation
                if after and not after[0].isspace() and after[0] not in '.,;:?!':
                    sep = ' '
                else:
                    sep = ''
                new_text = f'[{title}]({url})' + sep + after
                return new_text, True
    else:
        # No bold title — search whole text
        for pat, url in NAMED_SOURCES:
            if ' ' in url or not url.startswith(('http', 'https')):
                continue
            m = re.search(pat, text, re.IGNORECASE)
            if m:
                replacement = f'[{m.group(0)}]({url})'
                new_text = text[:m.start()] + replacement + text[m.end():]
                return new_text, True

    # Pattern B: bare domain in prose
    m = PAT_B.search(text)
    if m:
        domain = m.group(1)
        url = _url_for_domain(domain)
        replacement = f'[{domain}]({url})'
        new_text = text[:m.start()] + replacement + text[m.end():]
        return new_text, True

    return text, False


def iter_articles():
    for dirpath, dirs, files in os.walk('.'):
        dirs[:] = [d for d in dirs if d not in ('.git', 'tools', 'assets') and not d.startswith('.')]
        for f in files:
            if f.endswith('.md') and f not in ('README.md', 'AGENTS.md', 'PLAN.md', 'TODO.md') and not f.endswith('.meta.md'):
                yield os.path.join(dirpath, f)


def process_file(path, dry_run=False):
    with open(path, encoding='utf-8') as f:
        content = f.read()
    lines = content.split('\n')
    in_ext = False
    is_crossref = False
    n_total = n_changed = 0
    new_lines = []
    for line in lines:
        if SECTION_RE.match(line):
            in_ext = True
            is_crossref = bool(CROSSREF_SECTION_RE.match(line))
            new_lines.append(line)
            continue
        if in_ext:
            if re.match(r'^##\s', line) and not SECTION_RE.match(line):
                in_ext = False
                new_lines.append(line)
                continue
            if is_crossref:
                new_lines.append(line)
                continue
            bm = re.match(r'^(\s*[-*]\s+)(.+)$', line)
            if bm:
                prefix, body = bm.group(1), bm.group(2)
                n_total += 1
                new_body, changed = transform_bullet(body)
                if changed:
                    n_changed += 1
                    new_lines.append(prefix + new_body)
                    continue
            new_lines.append(line)
            continue
        new_lines.append(line)
    new_content = '\n'.join(new_lines)
    if n_changed > 0 and not dry_run and new_content != content:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(new_content)
    return n_total, n_changed


def main():
    dry = '--dry-run' in sys.argv
    total_changed = 0
    files_changed = 0
    for path in iter_articles():
        n_total, n_changed = process_file(path, dry_run=dry)
        if n_changed > 0:
            files_changed += 1
            total_changed += n_changed
            print(f"  {'[DRY] ' if dry else ''}changed {n_changed:3d} / {n_total:3d} bullets in {path}")
    print()
    print(f"{'[DRY RUN] ' if dry else ''}Total: {total_changed} bullets changed across {files_changed} files")


if __name__ == '__main__':
    main()
