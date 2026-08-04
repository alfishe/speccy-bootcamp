#!/usr/bin/env python3
"""
Insert the section-appropriate breadcrumb as line 1 of every article that's
missing one. Breadcrumb patterns are taken from each section's README.md.

Target: AGENTS.md line 131 mandate — every article must start with a
navigation breadcrumb on line 1.
"""
import os
import re
import sys

# Section-relative breadcrumb patterns (verified against section READMEs)
SECTION_BREADCRUMBS = {
    '03_io/storage/':     '[← Home](../../README.md) · [I/O](../) · [Storage](README.md)',
    '03_io/peripherals/': '[← Home](../../README.md) · [Peripherals](README.md)',
}

# Files explicitly excluded (README/PLAN/AGENTS/TODO already excluded by name)
EXCLUDE_FILES = {'README.md', 'PLAN.md', 'AGENTS.md', 'TODO.md'}

BREADCRUMB_RE = re.compile(r'^\[←\s')

def fix_section(section_dir, breadcrumb):
    """Insert breadcrumb as line 1 of every .md file in section_dir missing one."""
    fixed = []
    skipped = []
    for fn in sorted(os.listdir(section_dir)):
        if not fn.endswith('.md') or fn in EXCLUDE_FILES:
            continue
        path = os.path.join(section_dir, fn)
        if not os.path.isfile(path):
            continue
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        # Skip .meta.md asset metadata files
        if fn.endswith('.meta.md'):
            continue
        first_line = content.split('\n', 1)[0]
        if BREADCRUMB_RE.match(first_line):
            skipped.append(path)
            continue
        # Insert breadcrumb + blank line before existing content
        new_content = breadcrumb + '\n\n' + content
        with open(path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        fixed.append(path)
    return fixed, skipped

def main():
    root = sys.argv[1] if len(sys.argv) > 1 else '.'
    os.chdir(root)
    total_fixed = 0
    total_skipped = 0
    for section, crumb in SECTION_BREADCRUMBS.items():
        if not os.path.isdir(section):
            print(f"SKIP (not a dir): {section}", file=sys.stderr)
            continue
        fixed, skipped = fix_section(section, crumb)
        print(f"\n=== {section} ===")
        print(f"Breadcrumb: {crumb}")
        print(f"Fixed ({len(fixed)}):")
        for p in fixed:
            print(f"  + {p}")
        print(f"Already had breadcrumb ({len(skipped)}):")
        for p in skipped:
            print(f"  = {p}")
        total_fixed += len(fixed)
        total_skipped += len(skipped)
    print(f"\n=== TOTALS ===")
    print(f"Fixed:   {total_fixed}")
    print(f"Skipped: {total_skipped}")

if __name__ == '__main__':
    main()
