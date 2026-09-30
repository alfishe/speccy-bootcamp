#!/usr/bin/env python3
"""
Quality scoring for ZX Spectrum knowledge base articles.
Scores each article against AGENTS.md "Deep" criteria.

Different article shapes want different sections. A hardware deep-dive
needs registers/mermaid/pitfalls; a history article needs none of that but
should be strong on history_context and use_cases; a narrow methodology or
case-study article is legitimately thin on registers/mermaid/api_reference
while needing strong code examples and cross-references. Scoring every
article against one universal checklist punishes the latter kinds for not
being the former kind.

An article declares its profile with a line anywhere in the file:

    > **Type**: methodology

Recognized values: concept (default fallback for anything untagged and not
auto-detected as reference), reference, history_culture, methodology,
case_study. If no tag is present, falls back to the old heuristic:
filename-pattern-based reference detection, else 'concept'.

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
    ('overview',        [r'^## (?:Overview|Introduction|Synopsis|About|Background)\b', r'^## §\d+\. Introduction', r'^## \d+\. Introduction', r'^## \d+\. Overview', r'^Scope:', r'^\*\*Scope:\*\*', r'^>\s*\*\*Scope\*\*:', r'^>\s*\*\*Scope:\*\*']),
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
    # 'references' = dedicated section listing external sources. Exclude 'Cross-references' (internal links).
    ('references',      [r'(?i)^#{2,3} (?!.*Cross-?ref).*Reference', r'(?i)^#{2,3} (?!.*Cross-?ref).*Sources', r'(?i)^#{2,3} .*Further Reading', r'(?i)^#{2,3} .*Bibliography', r'(?i)^#{2,3} .*Citations', r'(?i)^#{2,3} .*Primary Sources']),
    ('cross_refs',      [r'(?i)^#{2,3} .*Cross-?ref', r'(?i)^#{2,3} .*See Also', r'(?i)^#{2,3} .*Related', r'(?i)^#{2,3} .*Internal Links', r'(?i)^#{2,3} .*Next Steps']),
    ('mermaid',         [r'```mermaid']),
    ('code_example',    [r'```z80', r'```asm', r'```c\b', r'```basic', r'```sdcc', r'```z80asm', r'```assembly']),
    ('tables',          [r'\|[ -]+\|[\s\S]+\|[ -]+\|']),  # at least one table
    ('contention_aware',[r'contend', r'contention', r'> \[!WARNING\]', r'> \[!NOTE\]']),
    ('track_note',      [r'Pentagon', r'Soviet', r'clone', r'128K', r'\+2', r'\+3', r'Next', r'Sinclair', r'Amstrad']),  # 3-track awareness
]

def is_reference_article(content, path):
    """Fallback heuristic for reference-shaped articles when no explicit Type tag is present."""
    # Reference articles: file format specs, token tables, opcode tables, port maps, memory maps
    ref_patterns = [
        r'_format\.md', r'_table\.md', r'_map\.md', r'_reference\.md',
        r'token_table', r'opcode', r'pinout', r'error_code', r'character_set',
        r'color_palette', r'memory_map', r'rom_routine', r'timing_reference',
    ]
    return any(re.search(p, path, re.IGNORECASE) for p in ref_patterns)

# Explicit self-declared type tag: a line anywhere in the article like
#   > **Type**: methodology
TYPE_TAG_RE = re.compile(r'^\s*>?\s*\*\*Type\*\*:\s*([a-z_]+)', re.IGNORECASE | re.MULTILINE)

# Per-profile weights. Every profile lists every section so scoring stays a
# simple sum/max lookup; a 0 weight means "not expected for this shape of
# article" rather than "missing = penalty".
PROFILES = {
    # Hardware / subsystem deep-dives, architecture docs — the original,
    # unmodified checklist. Also the fallback for untagged, non-reference
    # articles so ~270 pre-existing articles keep their current scores.
    'concept': {
        'breadcrumb': 2, 'title': 2, 'overview': 2, 'references': 2, 'cross_refs': 2,
        'architecture': 3, 'examples': 3, 'pitfalls': 3, 'when_to_use': 2,
        'history_context': 2, 'mermaid': 2, 'registers': 1, 'tables': 1,
        'api_reference': 1, 'decision_guide': 1, 'use_cases': 1, 'faq': 1,
        'code_example': 2, 'contention_aware': 1, 'track_note': 1,
    },
    # File format specs, opcode/token/port tables, memory maps — looked up,
    # not read cover-to-cover.
    'reference': {
        'breadcrumb': 2, 'title': 2, 'overview': 2, 'references': 2, 'cross_refs': 2,
        'architecture': 1, 'examples': 1, 'pitfalls': 1, 'when_to_use': 0,
        'history_context': 0, 'mermaid': 0, 'registers': 3, 'tables': 3,
        'api_reference': 1, 'decision_guide': 1, 'use_cases': 1, 'faq': 1,
        'code_example': 2, 'contention_aware': 1, 'track_note': 1,
    },
    # History/culture narratives — no hardware register tables or code to
    # show; strength is in historical narrative and named examples.
    'history_culture': {
        'breadcrumb': 2, 'title': 2, 'overview': 2, 'references': 2, 'cross_refs': 2,
        'architecture': 0, 'examples': 1, 'pitfalls': 0, 'when_to_use': 0,
        'history_context': 4, 'mermaid': 0, 'registers': 0, 'tables': 1,
        'api_reference': 0, 'decision_guide': 1, 'use_cases': 2, 'faq': 1,
        'code_example': 0, 'contention_aware': 0, 'track_note': 1,
    },
    # A discipline or technique explained and justified (squeeze tricks,
    # compression strategy, math tricks) — strong on worked code examples,
    # pitfalls/when-to-use, and cross-references; no register tables, no
    # mermaid, no hardware architecture diagrams expected.
    'methodology': {
        'breadcrumb': 2, 'title': 2, 'overview': 2, 'references': 1, 'cross_refs': 2,
        'architecture': 1, 'examples': 3, 'pitfalls': 2, 'when_to_use': 2,
        'history_context': 1, 'mermaid': 0, 'registers': 0, 'tables': 1,
        'api_reference': 0, 'decision_guide': 2, 'use_cases': 1, 'faq': 1,
        'code_example': 3, 'contention_aware': 1, 'track_note': 0,
    },
    # A named, sourced deep-dive into one real production/program — strong
    # on code examples and named-source history, not on generic register
    # tables or decision matrices.
    'case_study': {
        'breadcrumb': 2, 'title': 2, 'overview': 2, 'references': 2, 'cross_refs': 2,
        'architecture': 2, 'examples': 2, 'pitfalls': 1, 'when_to_use': 1,
        'history_context': 2, 'mermaid': 0, 'registers': 0, 'tables': 1,
        'api_reference': 0, 'decision_guide': 1, 'use_cases': 2, 'faq': 0,
        'code_example': 3, 'contention_aware': 1, 'track_note': 1,
    },
}
PROFILES['hardware'] = PROFILES['concept']  # explicit alias for self-tagging clarity

def detect_type(content, path):
    """Explicit '> **Type**: x' tag wins; else fall back to the old heuristic."""
    m = TYPE_TAG_RE.search(content)
    if m:
        tag = m.group(1).lower()
        if tag in PROFILES:
            return tag
        print(f"WARNING: unknown Type tag '{tag}' in {path}, falling back to heuristic", file=sys.stderr)
    return 'reference' if is_reference_article(content, path) else 'concept'

def score_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    lines = content.count('\n')
    article_type = detect_type(content, path)
    weights = PROFILES[article_type]

    present = []
    missing = []
    for name, patterns in SECTIONS:
        found = any(re.search(p, content, re.MULTILINE) for p in patterns)
        # A weight of 0 means this profile doesn't expect the section at
        # all — don't count it as "missing" (that's not a real gap).
        if found:
            present.append(name)
        elif weights.get(name, 0) > 0:
            missing.append(name)

    score = sum(weights[n] for n in present)
    max_score = sum(weights.values())
    pct = round(100 * score / max_score, 1)

    return {
        'lines': lines,
        'type': article_type,
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
    print(f"{'pct':>5} {'lines':>5} {'type':>16} path")
    for r in results[:30]:
        print(f"{r['pct']:>5} {r['lines']:>5} {r['type']:>16} {r['path']}")

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
