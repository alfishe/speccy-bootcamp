#!/usr/bin/env python3
"""
British → American English cleanup for ZX Spectrum knowledge base.
- Skips fenced code blocks (``` ... ```)
- Skips inline code spans (`...`)
- Skips lines that explicitly discuss British spelling (containing "British")
- Preserves case
- Word-boundary safe
"""
import os
import re
import sys

REPLACEMENTS = [
    # -our -> -or
    (r'\bcolour\b', 'color'),
    (r'\bcolours\b', 'colors'),
    (r'\bcoloured\b', 'colored'),
    (r'\bColoured\b', 'Colored'),
    (r'\bcolouring\b', 'coloring'),
    (r'\bbehaviour\b', 'behavior'),
    (r'\bbehaviours\b', 'behaviors'),
    (r'\bfavour\b', 'favor'),
    (r'\bfavoured\b', 'favored'),
    (r'\bfavourite\b', 'favorite'),
    (r'\bfavourites\b', 'favorites'),
    (r'\bflavour\b', 'flavor'),
    (r'\bflavours\b', 'flavors'),
    (r'\bharbour\b', 'harbor'),
    (r'\bhonour\b', 'honor'),
    (r'\bhonoured\b', 'honored'),
    (r'\blabour\b', 'labor'),
    (r'\bneighbour\b', 'neighbor'),
    (r'\bneighbours\b', 'neighbors'),
    (r'\brumour\b', 'rumor'),
    (r'\brumours\b', 'rumors'),
    (r'\bhumour\b', 'humor'),
    (r'\bvapour\b', 'vapor'),
    (r'\barmour\b', 'armor'),
    (r'\bvigour\b', 'vigor'),
    (r'\brigour\b', 'rigor'),
    (r'\bsplendour\b', 'splendor'),
    (r'\bsavour\b', 'savor'),
    (r'\bvalour\b', 'valor'),
    (r'\bodour\b', 'odor'),
    (r'\bglamour\b', 'glamor'),

    # -ise -> -ize
    (r'\borganise\b', 'organize'),
    (r'\borganised\b', 'organized'),
    (r'\borganises\b', 'organizes'),
    (r'\borganising\b', 'organizing'),
    (r'\boptimise\b', 'optimize'),
    (r'\boptimised\b', 'optimized'),
    (r'\bcapitalise\b', 'capitalize'),
    (r'\bcapitalised\b', 'capitalized'),
    (r'\bmonetise\b', 'monetize'),
    (r'\bunauthorised\b', 'unauthorized'),
    (r'\brecognise\b', 'recognize'),
    (r'\brecognised\b', 'recognized'),
    (r'\brecognises\b', 'recognizes'),
    (r'\brecognising\b', 'recognizing'),
    (r'\bspecialise\b', 'specialize'),
    (r'\bspecialised\b', 'specialized'),
    (r'\bspecialisation\b', 'specialization'),
    (r'\bemphasise\b', 'emphasize'),
    (r'\bemphasised\b', 'emphasized'),
    (r'\banalyse\b', 'analyze'),
    (r'\banalysed\b', 'analyzed'),
    (r'\bparalyse\b', 'paralyze'),
    (r'\bparalysed\b', 'paralyzed'),
    (r'\bcatalyse\b', 'catalyze'),
    (r'\bcriticise\b', 'criticize'),
    (r'\bcriticised\b', 'criticized'),
    (r'\bminimise\b', 'minimize'),
    (r'\bminimised\b', 'minimized'),
    (r'\bmaximise\b', 'maximize'),
    (r'\bmaximised\b', 'maximized'),
    (r'\brealise\b', 'realize'),
    (r'\brealised\b', 'realized'),
    (r'\brealises\b', 'realizes'),
    (r'\brealisation\b', 'realization'),
    (r'\bmodernise\b', 'modernize'),
    (r'\bstandardise\b', 'standardize'),
    (r'\bstandardised\b', 'standardized'),
    (r'\bnormalise\b', 'normalize'),
    (r'\bnormalised\b', 'normalized'),
    (r'\bformalise\b', 'formalize'),
    (r'\bformalised\b', 'formalized'),
    (r'\bmemorise\b', 'memorize'),
    (r'\bjeopardise\b', 'jeopardize'),
    (r'\bharmonise\b', 'harmonize'),
    (r'\bharmonised\b', 'harmonized'),
    (r'\bcivilise\b', 'civilize'),
    (r'\bcolonise\b', 'colonize'),
    (r'\bcolonised\b', 'colonized'),
    (r'\bcustomise\b', 'customize'),
    (r'\bcustomised\b', 'customized'),
    (r'\bfinalise\b', 'finalize'),
    (r'\bfinalised\b', 'finalized'),
    (r'\bgeneralise\b', 'generalize'),
    (r'\bgeneralised\b', 'generalized'),
    (r'\billegalise\b', 'illegalize'),
    (r'\bidealise\b', 'idealize'),
    (r'\blegalise\b', 'legalize'),
    (r'\bpenalise\b', 'penalize'),
    (r'\bpublicise\b', 'publicize'),
    (r'\brationalise\b', 'rationalize'),
    (r'\brationalised\b', 'rationalized'),
    (r'\bsatirise\b', 'satirize'),
    (r'\bsymbolise\b', 'symbolize'),
    (r'\bsymbolised\b', 'symbolized'),
    (r'\butilise\b', 'utilize'),
    (r'\butilised\b', 'utilized'),
    (r'\boxidise\b', 'oxidize'),
    (r'\bserialise\b', 'serialize'),
    (r'\bserialised\b', 'serialized'),
    (r'\bsynchronise\b', 'synchronize'),
    (r'\bsynchronised\b', 'synchronized'),
    (r'\bsynchronises\b', 'synchronizes'),
    (r'\bcharacterise\b', 'characterize'),
    (r'\bcharacterised\b', 'characterized'),
    (r'\bprioritise\b', 'prioritize'),
    (r'\bprioritised\b', 'prioritized'),
    (r'\bsynthesise\b', 'synthesize'),
    (r'\bsynthesised\b', 'synthesized'),
    (r'\boptimising\b', 'optimizing'),
    (r'\bcustomising\b', 'customizing'),

    # -ce -> -se
    (r'\bdefence\b', 'defense'),
    (r'\boffence\b', 'offense'),
    (r'\blicence\b', 'license'),
    (r'\blicences\b', 'licenses'),
    (r'\bpretence\b', 'pretense'),

    # practise (verb) -> practice
    (r'\bpractise\b', 'practice'),
    (r'\bpractised\b', 'practiced'),

    # -lle -> -l (doubled consonant)
    (r'\benrol\b', 'enroll'),
    (r'\benrolment\b', 'enrollment'),
    (r'\bwilful\b', 'willful'),
    (r'\binstal\b', 'install'),
    (r'\binstalment\b', 'installment'),
    (r'\bmarvellous\b', 'marvelous'),
    (r'\btravelled\b', 'traveled'),
    (r'\btravelling\b', 'traveling'),
    (r'\btraveller\b', 'traveler'),
    (r'\bcounselled\b', 'counseled'),
    (r'\bcounselling\b', 'counseling'),
    (r'\bcounsellor\b', 'counselor'),
    (r'\bequalling\b', 'equaling'),
    (r'\bsignalling\b', 'signaling'),
    (r'\bsignalled\b', 'signaled'),
    (r'\bmodelled\b', 'modeled'),
    (r'\bmodelling\b', 'modeling'),
    (r'\blabelled\b', 'labeled'),
    (r'\blabelling\b', 'labeling'),
    (r'\bcancelled\b', 'canceled'),
    (r'\bcancelling\b', 'canceling'),

    # -mme -> -m
    (r'\bgramme\b', 'gram'),
    (r'\bgrammes\b', 'grams'),
    (r'\bprogramme\b', 'program'),
    (r'\bprogrammes\b', 'programs'),

    # -re -> -er (length/measure)
    (r'\bmetre\b', 'meter'),
    (r'\bmetres\b', 'meters'),
    (r'\blitre\b', 'liter'),
    (r'\blitres\b', 'liters'),
    (r'\bfibre\b', 'fiber'),
    (r'\bcentre\b', 'center'),
    (r'\bcentred\b', 'centered'),
    (r'\bcentres\b', 'centers'),
    (r'\btheatre\b', 'theater'),
    (r'\bsceptre\b', 'scepter'),

    # -logue -> -log
    (r'\bcatalogue\b', 'catalog'),
    (r'\bcatalogues\b', 'catalogs'),
    (r'\bcatalogued\b', 'cataloged'),
    (r'\bcataloguing\b', 'cataloging'),
    (r'\banalogue\b', 'analog'),
    (r'\banalogues\b', 'analogs'),
    (r'\bdialogue\b', 'dialog'),
    (r'\bmonologue\b', 'monolog'),

    # mould / smoulder / plough
    (r'\bmould\b', 'mold'),
    (r'\bmoulds\b', 'molds'),
    (r'\bmoulded\b', 'molded'),
    (r'\bsmoulder\b', 'smolder'),
    (r'\bsmouldering\b', 'smoldering'),
    (r'\bplough\b', 'plow'),

    # direction / relation
    (r'\btowards\b', 'toward'),
    (r'\bwhilst\b', 'while'),
    (r'\bamidst\b', 'amid'),
    (r'\bamongst\b', 'among'),
    (r'\bafterwards\b', 'afterward'),
    (r'\bbackwards\b', 'backward'),
    (r'\bforwards\b', 'forward'),
    (r'\bdownwards\b', 'downward'),
    (r'\bupwards\b', 'upward'),

    # manoeuvre
    (r'\bmanoeuvre\b', 'maneuver'),
    (r'\bmanoeuvres\b', 'maneuvers'),
    (r'\bmanoeuvring\b', 'maneuvering'),

    # gaol
    (r'\bgaol\b', 'jail'),
    (r'\bgaoler\b', 'jailer'),
]

COMPILED = [(re.compile(p), r) for p, r in REPLACEMENTS]

def fix_line(line):
    parts = re.split(r'(`[^`]*`)', line)
    for i, part in enumerate(parts):
        if part.startswith('`') and part.endswith('`'):
            continue
        for pattern, replacement in COMPILED:
            parts[i] = pattern.sub(replacement, parts[i])
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
        if 'British' in line or 'UK English' in line or 'British English' in line:
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
