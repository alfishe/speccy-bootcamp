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
    r'^#{2,3}\s(?!.*Cross-?[Rr]ef).*?(?:[Rr]eferences|[Ss]ources\b|[Ff]urther\s[Rr]eading|[Ee]xternal)',
    re.MULTILINE,
)
CROSSREF_SECTION_RE = re.compile(r'^#{2,3}\s.*Cross-?[Rr]ef', re.MULTILINE)
HTTP_URL_RE = re.compile(r'\[[^\]]+\]\(https?://[^)]+\)')

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
    (r'sinclairfaq\.com',         'http://www.sinclairfaq.com'),
    (r'archive\.org',             'https://archive.org'),
    (r'julien-nevo\.com',         'https://www.julien-nevo.com'),
    (r'mtc\.se',                  'http://mtc.se'),
    (r'k1\.spb\.ru',              'http://k1.spb.ru'),
    (r'speccy\.xyz',              'https://speccy.xyz'),
    (r'speccy\.cz',               'https://speccy.cz'),
    (r'sdcc\.sourceforge\.net',   'https://sdcc.sourceforge.net'),
    (r'sourceforge\.net',         'https://sourceforge.net'),
]

# Pattern A: bullet starts with **`domain`...** (backticked domain inside bold)
# Captures the rest of the title (between closing backtick and closing **)
PAT_A = re.compile(
    r'^\*\*`((?:' + '|'.join(pat for pat, _ in DOMAIN_TO_URL) + r'))`\s*(.*?)\*\*'
)

# Pattern B: bare domain in prose (no preceding code/link/paren)
PAT_B = re.compile(
    r'(?<![`/\[(.])(' + '|'.join(pat for pat, _ in DOMAIN_TO_URL) + r')(?![/)`])'
)

# Pattern C: **Title** (Author, `domain/path`) — common form in batch-6 articles
# Captures: group(1) = Title, group(2) = full backticked content (domain or domain/path)
_DOMAIN_OR_PATH = r'(?:https?://)?(?:' + '|'.join(pat for pat, _ in DOMAIN_TO_URL) + r')(?:/[^`]+)?'
_GITHUB_PATH = r'(?:https?://)?github\.com/[A-Za-z0-9_-]+/[A-Za-z0-9_.-]+'
PAT_C = re.compile(
    r'^\*\*([^*]+?)\*\*\s+\([^)]*?,\s*`(' + _DOMAIN_OR_PATH + r'|' + _GITHUB_PATH + r')`\)'
)

# Pattern D: **Title** (`domain`) — backticked domain in trailing parens (no author)
PAT_D = re.compile(
    r'^\*\*([^*]+?)\*\*\s+\(`(' + _DOMAIN_OR_PATH + r')`\)'
)

# Pattern E: **Title** (domain) — bare domain in parens, no backticks
PAT_E = re.compile(
    r'^\*\*([^*]+?)\*\*\s+\(((?:https?://)?(?:' + '|'.join(pat for pat, _ in DOMAIN_TO_URL) + r')(?:/[^)]+)?)\)'
)

# Pattern F: **Title** (`https://full-url/`) — full URL already in backticks
PAT_F = re.compile(
    r'^\*\*([^*]+?)\*\*\s+\(`((?:https?://)[^`]+)`\)'
)

# Pattern H: **Title (`domain`)** — backticked domain in parens INSIDE the bold span
# e.g., **ZXArt (`zxart.ee`)** — desc
PAT_H = re.compile(
    r'^\*\*([^(*]+?)\s+\(`(' + '|'.join(pat for pat, _ in DOMAIN_TO_URL) + r')`\)\*\*'
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
]


def _url_for_domain(domain_str):
    for pat, url in DOMAIN_TO_URL:
        if re.fullmatch(pat, domain_str):
            return url
    return 'https://' + domain_str


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
        m = re.match(pat, s)
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
    bold_match = re.match(r'^\*\*(.+?)\*\*(?:\*|\s|\(|$)', text)
    if bold_match:
        title = bold_match.group(1)
        # If title has unmatched italic markers (odd count of *), strip them
        if title.count('*') % 2 == 1:
            title = title.replace('*', '')
        for pat, url in NAMED_SOURCES:
            if ' ' in url or not url.startswith(('http', 'https')):
                continue
            if re.search(pat, title):
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
                sep = ' ' if after and not after[0].isspace() else ''
                new_text = f'[{title}]({url})' + sep + after
                return new_text, True
    else:
        # No bold title — search whole text
        for pat, url in NAMED_SOURCES:
            if ' ' in url or not url.startswith(('http', 'https')):
                continue
            m = re.search(pat, text)
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
