#!/usr/bin/env python3
"""Categorize C-style hex (0xNNNN) violations in prose for AGENTS.md compliance."""
import os
import re
import sys

CATEGORIES = {
    'memory_address': [],   # 0x4000-0xFFFF — should be #NNNN
    'port_address': [],     # 0xFE, 0x1F, 0xFFFD, 0x7FFD — should be #NN
    'byte_value_table': [], # 0xED 0xED, 0x55 0xAA — debatable, in tables
    'byte_value_prose': [], # 0xFF in prose — debatable
    'cli_arg': [],          # --origin=0x8000 — leave alone
}

def categorize(line, hex_str, path, lineno):
    value = int(hex_str, 16)
    context = line.strip()[:140]

    # CLI args (--option=0x8000)
    if re.search(r'--?\w+[=\s]"?0x', line) or '=0x' in line.replace(' ', ''):
        CATEGORIES['cli_arg'].append((path, lineno, hex_str, context))
        return

    # Memory address: 0xNNNN with NNNN >= 0x4000
    if value >= 0x4000 and len(hex_str) >= 6:
        CATEGORIES['memory_address'].append((path, lineno, hex_str, context))
        return

    # Port address: small values 0xFE, 0x1F, 0xFFFD, 0x7FFD, 0xBFFD, 0x3FFD, 0x5FFD
    port_indicators = ['port', 'IORQ', 'iorq', '#FE', '#1F', 'FFFD', '7FFD', 'BFFD', '3FFD', '5FFD', '1FFD', '0xFE', '0x1F', '0xFFFD', '0x7FFD', '0xBFFD', 'Kempston']
    if any(p in line for p in port_indicators):
        CATEGORIES['port_address'].append((path, lineno, hex_str, context))
        return

    # In a table row (starts with |)
    if line.lstrip().startswith('|'):
        CATEGORIES['byte_value_table'].append((path, lineno, hex_str, context))
        return

    # Otherwise: byte value in prose
    CATEGORIES['byte_value_prose'].append((path, lineno, hex_str, context))


def scan(path):
    in_code = False
    with open(path) as f:
        for lineno, line in enumerate(f, 1):
            stripped = line.strip()
            if stripped.startswith('```'):
                in_code = not in_code
                continue
            if in_code:
                continue
            # Strip inline code spans
            cleaned = re.sub(r'`[^`]*`', '', line)
            for m in re.finditer(r'0x[0-9A-Fa-f]{2,4}\b', cleaned):
                categorize(line, m.group(), path, lineno)


def main():
    root = sys.argv[1] if len(sys.argv) > 1 else '.'
    if os.path.isfile(root):
        scan(root)
    else:
        for dirpath, _, files in os.walk(root):
            if '.git' in dirpath:
                continue
            for fn in files:
                if fn.endswith('.md'):
                    scan(os.path.join(dirpath, fn))

    print("=== Categorization ===")
    for cat, items in CATEGORIES.items():
        print(f"  {cat}: {len(items)}")
    print()

    for cat in ['memory_address', 'port_address']:
        print(f"=== {cat} samples (first 15 of {len(CATEGORIES[cat])}) ===")
        for v in CATEGORIES[cat][:15]:
            print(f"  {v[0]}:{v[1]}: {v[2]:10s} → {v[3][:90]}")
        print()


if __name__ == '__main__':
    main()
