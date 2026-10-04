#!/usr/bin/env python3
"""drop_before.py FILE MARKER [OS]: take OS (default irix) out of the cfg attribute just above
every line containing MARKER (where IRIX parts from the OS it was listed with)."""
import sys
p, marker = sys.argv[1], sys.argv[2]
os_ = sys.argv[3] if len(sys.argv) > 3 else "irix"
N = 'target_os = "%s"' % os_
L = open(p).read().split('\n')
n = 0
for i in [i for i, l in enumerate(L) if marker in l]:
    j = i - 1
    while j >= 0 and '#[cfg' not in L[j] and 'cfg_if' not in L[j]:
        j -= 1
    for k in range(j, i):
        if L[k].strip() in (N + ',', N):
            L[k] = None; n += 1
        elif N in L[k]:
            L[k] = L[k].replace(', ' + N, '').replace(N + ', ', ''); n += 1
    L = [l for l in L if l is not None] if None in L else L
open(p, 'w').write('\n'.join(L))
print(n, 'removed in', p)
