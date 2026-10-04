#!/usr/bin/env python3
"""exclude_before.py FILE MARKER [OS]: add OS (default irix) to the not(any(...)) list of the
cfg attribute just above every line containing MARKER."""
import sys, re
p, marker = sys.argv[1], sys.argv[2]
os_ = sys.argv[3] if len(sys.argv) > 3 else "irix"
N = 'target_os = "%s"' % os_
L = open(p).read().split('\n')
n = 0
for i in sorted([i for i, l in enumerate(L) if marker in l and not l.lstrip().startswith(('#', '//'))], reverse=True):
    j = i - 1
    while j >= 0 and '#[cfg' not in L[j]:
        j -= 1
    block = '\n'.join(L[j:i])
    if j < 0 or 'not(any(' not in block or N in block:
        continue
    for k in range(j, i):
        if 'not(any(' in L[k]:
            if L[k].rstrip().endswith('not(any('):
                ind = re.match(r'\s*', L[k + 1]).group(0)
                L.insert(k + 1, ind + N + ',')
            else:
                L[k] = L[k].replace('not(any(', 'not(any(' + N + ', ', 1)
            n += 1
            break
open(p, 'w').write('\n'.join(L))
print(n, 'added in', p)
