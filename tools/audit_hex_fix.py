#!/usr/bin/env python3
"""
C-style hex (0xNNNN) → Z80 convention (#NNNN) for prose.
- Skips fenced code blocks
- Skips inline code spans
- Skips CLI arguments (--origin=0x8000)
- Preserves case
"""
import os
import re
import sys

# Match 0x followed by 2-4 hex digits at word boundary
HEX_PATTERN = re.compile(r'\b0x([0-9A-Fa-f]{2,4})\b')

# CLI argument context: --option=0xNNNN or option=0xNNNN
CLI_PATTERN = re.compile(r'--?\w+[=\s]"?0x')

def is_cli_arg(line, pos):
    """Check if the 0x at position `pos` is part of a CLI argument."""
    # Look 30 chars before for --option= pattern
    before = line[max(0, pos-30):pos]
    if re.search(r'--?\w+[=\s]"?$', before):
        return True
    # =0xNNNN assignment
    if before.endswith('='):
        return True
    return False

def fix_line(line):
    """Replace 0xNNNN with #NNNN, skipping CLI args."""
    def replace(m):
        if is_cli_arg(line, m.start()):
            return m.group()
        return '#' + m.group(1).upper()
    # Split out inline code spans
    parts = re.split(r'(`[^`]*`)', line)
    for i, part in enumerate(parts):
        if part.startswith('`') and part.endswith('`'):
            continue
        parts[i] = HEX_PATTERN.sub(replace, part)
    return ''.join(parts)

def fix_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    in_code = False
    changed = 0
    new_lines = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith('```'):
            in_code = not in_code
            new_lines.append(line)
            continue
        if in_code:
            new_lines.append(line)
            continue
        new = fix_line(line)
        if new != line:
            changed += 1
        new_lines.append(new)
    if changed > 0:
        with open(path, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
    return changed

def main():
    if len(sys.argv) > 1:
        paths = sys.argv[1:]
    else:
        paths = ['.']
    total = 0
    files_changed = 0
    for root in paths:
        if os.path.isfile(root):
            n = fix_file(root)
            if n:
                files_changed += 1
                print(f"{root}: {n} lines")
                total += n
            continue
        for dirpath, _, files in os.walk(root):
            if '.git' in dirpath:
                continue
            for fn in files:
                if not fn.endswith('.md'):
                    continue
                path = os.path.join(dirpath, fn)
                n = fix_file(path)
                if n:
                    files_changed += 1
                    print(f"{path}: {n} lines")
                    total += n
    print(f"\nTotal: {total} lines changed across {files_changed} files")

if __name__ == '__main__':
    main()
