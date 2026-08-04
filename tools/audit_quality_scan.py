#!/usr/bin/env python3
"""
Quality scoring for ZX Spectrum knowledge base articles.
Scores each article against AGENTS.md "Deep" criteria.

Output: TSV with columns: path, lines, type, score, missing_sections
"""
import os
import re
import sys

# Required sections per AGENTS.md
# Each tuple: (section_name, list_of_regex_patterns_to_detect_it)
# Patterns are matched case-insensitively where possible
SECTIONS = [
    ('breadcrumb',      [r'^\[← Home\]', r'^\[← Plan\]']),
    ('title',           [r'^# ']),
    ('overview',        [r'^## (?:Overview|Introduction|Synopsis|About|Background)\b', r'^## §\d+\. Introduction', r'^## \d+\. Introduction', r'^## \d+\. Overview', r'^Scope:', r'^\*\*Scope:\*\*']),
    ('architecture',    [r'^## .*Architect', r'^## .*How It Works', r'^## .*Design', r'^## .*Implementation', r'^## .*Hardware', r'^## .*Internal']),
    ('registers',       [r'^## .*Register', r'^## .*Port Map', r'^## .*I/O Port', r'^## .*Layout', r'\| Port +\|', r'\| Offset +\|', r'^## .*Byte.*Layout', r'^## .*Format.*Spec']),
    ('api_reference',   [r'^## .*API', r'^## .*ROM Routine', r'^## .*Routine', r'^## .*Calling', r'^## .*Function']),
    ('decision_guide',  [r'^## .*Decision', r'^## .*Comparison', r'^## .*Choosing', r'^## .*When to Use', r'^## .*Trade.?Off']),
    ('history_context', [r'^## .*Histor', r'^## .*Background', r'^## .*Origin', r'^## .*Etymology', r'^## .*Cultural']),
    ('examples',        [r'^## .*Example', r'^## .*Sample', r'^## .*Demo', r'^## .*Cookbook', r'^## .*Tutorial', r'^## .*Code', r'^## .*Programming']),
    ('when_to_use',     [r'^## .*When to Use', r'^## .*When NOT', r'^## .*Best Practice', r'^## .*Antipattern', r'^## .*Anti-pattern', r'^## .*Anti-?Pattern']),
    ('pitfalls',        [r'^## .*Pitfall', r'^## .*Common Mistake', r'^## .*Gotcha', r'^## .*Warning', r'^## .*Troubleshoot']),
    ('use_cases',       [r'^## .*Use Case', r'^## .*Use-Case', r'^## .*Applications', r'^## .*Practical', r'^## .*In the Wild']),
    ('faq',             [r'^## FAQ', r'^## .*Frequently Asked']),
    ('references',      [r'^## .*Reference', r'^## .*Sources', r'^## .*Further Reading', r'^## .*Bibliography', r'^## .*Citations']),
    ('cross_refs',      [r'^## .*Cross-?ref', r'^## .*See Also', r'^## .*Related', r'^## .*Internal Links', r'^## .*Next Steps']),
    ('mermaid',         [r'```mermaid']),
    ('code_example',    [r'```z80', r'```asm', r'```c\b', r'```basic', r'```sdcc', r'```z80asm', r'```assembly']),
    ('tables',          [r'\|[ -]+\|[\s\S]+\|[ -]+\|']),  # at least one table
    ('contention_aware',[r'contend', r'contention', r'> \[!WARNING\]', r'> \[!NOTE\]']),
    ('track_note',      [r'Pentagon', r'Soviet', r'clone', r'128K', r'\+2', r'\+3', r'Next', r'Sinclair', r'Amstrad']),  # 3-track awareness
]

def is_reference_article(content, path):
    """Detect Type B (reference) vs Type A (concept)."""
    # Reference articles: file format specs, token tables, opcode tables, port maps, memory maps
    ref_patterns = [
        r'_format\.md', r'_table\.md', r'_map\.md', r'_reference\.md',
        r'token_table', r'opcode', r'pinout', r'error_code', r'character_set',
        r'color_palette', r'memory_map', r'rom_routine', r'timing_reference',
    ]
    return any(re.search(p, path, re.IGNORECASE) for p in ref_patterns)

def score_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    lines = content.count('\n')
    is_ref = is_reference_article(content, path)

    present = []
    missing = []
    for name, patterns in SECTIONS:
        found = any(re.search(p, content, re.MULTILINE) for p in patterns)
        if found:
            present.append(name)
        else:
            missing.append(name)

    # Weighted scoring — mandatory sections weighted higher
    # Mandatory for all: breadcrumb, title, overview, references, cross_refs
    # Mandatory for concept: architecture, examples, pitfalls, when_to_use, history_context, mermaid
    # Mandatory for reference: registers, tables
    # Bonus: decision_guide, faq, use_cases, contention_aware, track_note
    weights = {
        'breadcrumb': 2, 'title': 2, 'overview': 2, 'references': 2, 'cross_refs': 2,
        'architecture': 3 if not is_ref else 1,
        'examples': 3 if not is_ref else 1,
        'pitfalls': 3 if not is_ref else 1,
        'when_to_use': 2 if not is_ref else 0,
        'history_context': 2 if not is_ref else 0,
        'mermaid': 2 if not is_ref else 0,
        'registers': 3 if is_ref else 1,
        'tables': 3 if is_ref else 1,
        'api_reference': 1, 'decision_guide': 1, 'use_cases': 1, 'faq': 1,
        'code_example': 2, 'contention_aware': 1, 'track_note': 1,
    }
    score = sum(weights[n] for n in present)
    max_score = sum(weights.values())
    pct = round(100 * score / max_score, 1)

    return {
        'lines': lines,
        'type': 'ref' if is_ref else 'concept',
        'present': present,
        'missing': missing,
        'score': score,
        'max_score': max_score,
        'pct': pct,
    }

def main():
    root = sys.argv[1] if len(sys.argv) > 1 else '.'
    results = []
    for dirpath, _, files in os.walk(root):
        if '.git' in dirpath or '/tools/' in dirpath or '/assets/' in dirpath:
            continue
        for fn in files:
            # Skip asset metadata files, README/PLAN/AGENTS/TODO
            if fn.endswith('.meta.md') or fn in ('README.md', 'PLAN.md', 'AGENTS.md', 'TODO.md'):
                continue
            if not fn.endswith('.md'):
                continue
            path = os.path.join(dirpath, fn)
            try:
                r = score_file(path)
                r['path'] = path
                results.append(r)
            except Exception as e:
                print(f"ERROR scoring {path}: {e}", file=sys.stderr)

    # Sort by score ascending (lowest first)
    results.sort(key=lambda r: r['pct'])

    print("=== Lowest 30 articles by quality score ===")
    print(f"{'pct':>5} {'lines':>5} {'type':>7} path")
    for r in results[:30]:
        print(f"{r['pct']:>5} {r['lines']:>5} {r['type']:>7} {r['path']}")

    print()
    print("=== Distribution ===")
    brackets = [(0, 50), (50, 60), (60, 70), (70, 80), (80, 90), (90, 101)]
    for lo, hi in brackets:
        n = sum(1 for r in results if lo <= r['pct'] < hi)
        print(f"  {lo:>3}-{hi:>3}: {n:>4} articles")

    print()
    print("=== Most-missing sections (across all articles) ===")
    from collections import Counter
    missing_counts = Counter()
    for r in results:
        for m in r['missing']:
            missing_counts[m] += 1
    total = len(results)
    for sec, cnt in missing_counts.most_common():
        print(f"  {sec:>20}: {cnt:>4} missing ({100*cnt//total}% of articles)")

    print()
    print("=== Concept articles only — lowest 15 ===")
    concept = [r for r in results if r['type'] == 'concept']
    print(f"{'pct':>5} {'lines':>5} path")
    for r in concept[:15]:
        print(f"{r['pct']:>5} {r['lines']:>5} {r['path']}")
        print(f"           missing: {', '.join(r['missing'][:8])}")

if __name__ == '__main__':
    main()
