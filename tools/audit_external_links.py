#!/usr/bin/env python3
"""
audit_external_links.py (v2)

Scan every article in the ZX knowledge base for References sections.
For each bullet, classify:

  HAS_HTTP_URL:    bullet contains an external https:// markdown link
  HAS_INTERNAL:    bullet contains a relative-path markdown link [text](file.md)
  HAS_BARE_DOMAIN: bullet has no link but mentions a domain like zx-pk.ru in prose
  NO_LINK:         pure prose, no link, no domain mentioned

A bullet is "good" if HAS_HTTP_URL (in External references section) or
HAS_INTERNAL (in Cross-references section). Otherwise it needs fixing.

Output:
  - Overall stats
  - Files with most NO_LINK + HAS_BARE_DOMAIN bullets in External sections
  - Grouped list of truly-URL-less bullets
"""

import os
import re
from collections import defaultdict

# Section pattern: any h2 or h3 that IS a References/Sources/External section
# (must START with one of these keywords, after optional numbering like "10.3 ")
# EXCLUDING Cross-references.
# Fix 2026-07-19: allow trailing period in section numbering (e.g., '## 10. References')
SECTION_RE = re.compile(
    r'^#{2,3}\s+(?!.*Cross-?[Rr]ef)(?:\d+(?:\.\d+)*\.?\s+|:\s+)?'
    r'(?:[Ee]xternal\b|[Rr]eferences?\b|[Ss]ources\b|[Ff]urther\s[Rr]eading|'
    r'[Pp]rimary\s[Ss]ources|[Aa]dditional\s[Rr]eferences|'
    r'[Bb]ooks(?:\s+and\s+[Aa]rticles)?|[Mm]agazines?\b|'
    r'[Ww]eb\s+[Rr]eferences|[Oo]nline\s+[Rr]eferences)',
    re.MULTILINE,
)
CROSSREF_SECTION_RE = re.compile(r'^#{2,3}\s.*Cross-?[Rr]ef', re.MULTILINE)

BULLET_RE = re.compile(r'^\s*[-*]\s+(.+)$', re.MULTILINE)
HTTP_URL_RE = re.compile(r'\[[^]]+\]\(https?://[^)]+\)|<https?://[^>]+>|\bhttps?://[^\s)]+')
INTERNAL_LINK_RE = re.compile(r'\[[^]]+\]\([^)]+\.md[^)]*\)')

# Bare domains: when found in prose, we can auto-wrap them as markdown links
DOMAIN_PATTERNS = [
    (r'\b(?:zx-pk\.ru)\b',                   'https://zx-pk.ru'),
    (r'\b(?:zxpress\.ru)\b',                 'https://zxpress.ru'),
    (r'\b(?:worldofspectrum\.org)\b',        'https://worldofspectrum.org'),
    (r'\b(?:worldofspectrum\.net)\b',        'https://worldofspectrum.net'),
    (r'\b(?:zxart\.ee)\b',                   'https://zxart.ee'),
    (r'\b(?:zxnext\.io)\b',                  'https://zxnext.io'),
    (r'\b(?:problemkaputt\.de)\b',           'http://problemkaputt.de'),
    (r'\b(?:nedopc\.com)\b',                 'https://nedopc.com'),
    (r'\b(?:zxevo\.ru)\b',                   'https://zxevo.ru'),
    (r'\b(?:pouet\.net)\b',                  'https://www.pouet.net'),
    (r'\b(?:righto\.com)\b',                 'http://www.righto.com'),
    (r'\b(?:chibiakumas\.com)\b',            'https://chibiakumas.com'),
    (r'\b(?:speccy\.wiki)\b',                'https://speccy.wiki'),
    (r'\b(?:sinclairfaq\.com)\b',            'http://www.sinclairfaq.com'),
    (r'\b(?:wikipedia\.org)\b',              'https://en.wikipedia.org'),
    (r'\b(?:archive\.org)\b',                'https://archive.org'),
    (r'\b(?:julien-nevo\.com)\b',            'https://www.julien-nevo.com'),
    (r'\b(?:mtc\.se)\b',                     'http://mtc.se'),
    (r'\b(?:k1\.spb\.ru)\b',                 'http://k1.spb.ru'),
    (r'\b(?:speccy\.xyz)\b',                 'https://speccy.xyz'),
    (r'\b(?:speccy\.cz)\b',                  'https://speccy.cz'),
    (r'\b(?:sizif\.xx\.ua)\b',               'https://sizif.xx.ua'),
    (r'\b(?:tslabs\.at\.ua)\b',              'https://tslabs.at.ua'),
    (r'\b(?:pdb\.underterritory\.com)\b',    'https://pdb.underterritory.com'),
    (r'\b(?:zurich\.mingw\.org)\b',          'https://zurich.mingw.org'),
    (r'\b(?:sdcc\.sourceforge\.net)\b',      'https://sdcc.sourceforge.net'),
    (r'\b(?:z88dk\.sourceforge\.net)\b',     'https://z88dk.sourceforge.net'),
    (r'\b(?:sourceforge\.net)\b',            'https://sourceforge.net'),
]

EXCLUDE_FILES = {'README.md', 'AGENTS.md', 'PLAN.md', 'TODO.md'}


def iter_articles():
    for dirpath, dirs, files in os.walk('.'):
        dirs[:] = [d for d in dirs if d not in ('.git', 'tools', 'assets') and not d.startswith('.')]
        for f in files:
            if f.endswith('.md') and f not in EXCLUDE_FILES and not f.endswith('.meta.md'):
                yield os.path.join(dirpath, f)


def extract_sections(content, want='external'):
    """Return text of references sections.
    want='external' → only External references sections
    want='all'      → all References-style sections (incl. Cross-references)
    """
    sections = []
    lines = content.split('\n')
    in_section = False
    is_crossref = False
    current = []
    for line in lines:
        if SECTION_RE.match(line) or (want == 'all' and CROSSREF_SECTION_RE.match(line)):
            in_section = True
            is_crossref = bool(CROSSREF_SECTION_RE.match(line))
            current = [line]
            continue
        if in_section:
            if re.match(r'^##\s', line) and not (SECTION_RE.match(line) or (want == 'all' and CROSSREF_SECTION_RE.match(line))):
                sections.append(('\n'.join(current), is_crossref))
                in_section = False
                current = []
                continue
            current.append(line)
    if current:
        sections.append(('\n'.join(current), is_crossref))
    return sections


def classify_bullet(b):
    """Return one of: 'http_url', 'internal_link', 'bare_domain', 'no_link'."""
    if HTTP_URL_RE.search(b):
        return 'http_url'
    if INTERNAL_LINK_RE.search(b):
        return 'internal_link'
    for pat, _ in DOMAIN_PATTERNS:
        if re.search(pat, b):
            return 'bare_domain'
    return 'no_link'


def main():
    stats = {
        'total_articles': 0,
        'articles_with_ext_refs': 0,
        'ext_bullets_total': 0,
        'ext_http_url': 0,
        'ext_internal': 0,    # mistake: internal link in External section
        'ext_bare_domain': 0,
        'ext_no_link': 0,
    }
    fixable_per_file = []  # (path, total_prose, bare_domain, no_link)
    no_link_examples = []

    for path in iter_articles():
        stats['total_articles'] += 1
        with open(path, encoding='utf-8') as f:
            content = f.read()
        sections = extract_sections(content, want='external')
        if not sections:
            continue
        stats['articles_with_ext_refs'] += 1
        ext_text = '\n\n'.join(s[0] for s in sections if not s[1])
        bullets = BULLET_RE.findall(ext_text)
        total = bare_d = no_l = 0
        for b in bullets:
            b = b.strip()
            if not b or b.startswith('!['):
                continue
            total += 1
            cls = classify_bullet(b)
            stats['ext_bullets_total'] += 1
            if cls == 'http_url':
                stats['ext_http_url'] += 1
            elif cls == 'internal_link':
                stats['ext_internal'] += 1
            elif cls == 'bare_domain':
                stats['ext_bare_domain'] += 1
                bare_d += 1
            else:
                stats['ext_no_link'] += 1
                no_l += 1
                if len(no_link_examples) < 200:
                    no_link_examples.append((path, b))
        if total:
            fixable_per_file.append((path, total, bare_d, no_l))

    print('=' * 72)
    print('OVERALL — External references sections only')
    print('=' * 72)
    print(f"  Articles with External refs:        {stats['articles_with_ext_refs']}")
    print(f"  Total external bullets:             {stats['ext_bullets_total']}")
    good = stats['ext_http_url']
    fixable = stats['ext_bare_domain']
    bad = stats['ext_no_link']
    mispl = stats['ext_internal']
    print(f"  HAS http URL (good):                {good} ({100*good/max(1,stats['ext_bullets_total']):.1f}%)")
    print(f"  HAS bare domain (auto-fixable):     {fixable} ({100*fixable/max(1,stats['ext_bullets_total']):.1f}%)")
    print(f"  Pure prose (needs manual URL):      {bad} ({100*bad/max(1,stats['ext_bullets_total']):.1f}%)")
    print(f"  Internal link in External (odd):    {mispl}")
    print()

    print('=' * 72)
    print('PER-FILE — most fixable first')
    print('=' * 72)
    fixable_per_file.sort(key=lambda t: -(t[2]+t[3]))
    for path, total, bd, nl in fixable_per_file[:60]:
        print(f"  {bd:3d} bare / {nl:3d} prose / {total:3d} total   {path}")


if __name__ == '__main__':
    main()
