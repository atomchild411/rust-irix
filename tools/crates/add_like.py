#!/usr/bin/env python3
"""add_like.py DIR REF NEW: wherever a cfg list of several OSes names target_os = REF, name
target_os = NEW too (Rust sources and Cargo.toml target tables). Single-OS cfgs are left alone."""
import os, re, sys
d, ref, new = sys.argv[1:4]
R, N = 'target_os = "%s"' % ref, 'target_os = "%s"' % new
count = 0
for root, _, files in os.walk(d):
    if '/.git' in root or '/target' in root:
        continue
    for f in files:
        if not (f.endswith('.rs') or f == 'Cargo.toml'):
            continue
        p = os.path.join(root, f)
        lines = open(p).read().split('\n')
        out = []
        for i, l in enumerate(lines):
            out.append(l)
            if N in l:
                continue
            s = l.strip()
            # an item of a multi-line list: `target_os = "ref",`
            if s == R + ',' or (s == R and i + 1 < len(lines) and lines[i + 1].strip().startswith(')')):
                ind = l[:len(l) - len(l.lstrip())]
                if s == R:   # last item without comma
                    out[-1] = l + ','
                    out.append(ind + N)
                else:
                    out.append(ind + N + ',')
                count += 1
            # inline lists: any(... target_os = "ref" ...)
            elif R in l and re.search(r'any\(', l) and l.count('target_os') > 1:
                out[-1] = l.replace(R, R + ', ' + N)
                count += 1
        open(p, 'w').write('\n'.join(out))
print(count, 'lists in', d)
