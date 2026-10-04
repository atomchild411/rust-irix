#!/usr/bin/env python3
"""cfg_autofix.py BUILDLOG CRATEDIR [OS] [--exclude]: for every compile error inside CRATEDIR, take
OS (default irix) out of the cfg that governs the failing line: drop it from a positive list that
names it (or, with --exclude, add it to a not(any(...)) list: only where the code that list leaves
out is code OS cannot use). Prints what it did and what it left alone (to fix by hand)."""
import re, sys, os
args = [a for a in sys.argv[1:] if not a.startswith('--')]
log, crate = args[0], os.path.realpath(args[1])
os_ = args[2] if len(args) > 2 else 'irix'
exclude_ok = '--exclude' in sys.argv
N = 'target_os = "%s"' % os_
locs = []
for m in re.finditer(r'^error.*\n(?:.*\n){0,3}?\s*--> (\S+?):(\d+):\d+', open(log).read(), re.M):
    f = os.path.realpath(m.group(1))
    if f.startswith(crate + '/'):
        locs.append((f, int(m.group(2))))
done, manual = set(), []
for f, line in sorted(set(locs), key=lambda x: (x[0], -x[1])):
    L = open(f).read().split('\n')
    i = line - 1
    # the attribute or cfg_if branch that governs line i: the nearest one above at a lower or
    # equal indentation, scanning past the item's own lines
    j, ind = i, len(L[i]) - len(L[i].lstrip())
    found = None
    while j > 0:
        j -= 1
        t = L[j]
        if '#[cfg' in t or re.search(r'\bif #\[cfg', t) or 'cfg_if' in t:
            k = j
            block = [L[k]]
            while not re.search(r'\)\]|\)\)\]\s*\{?|\] \{', L[k]) and k + 1 < i:
                k += 1
                block.append(L[k])
            found = (j, k)
            break
        tind = len(t) - len(t.lstrip())
        if t.strip() and tind < ind and not t.strip().startswith(('//', '#', '.', ')', ']', '}')):
            ind = tind
    if not found or (f, found[0]) in done:
        if not found:
            manual.append('%s:%d (no cfg above)' % (f, line))
        continue
    j, k = found
    text = '\n'.join(L[j:k + 1])
    if N in text and 'not(' not in text.split(N)[0][-40:]:
        new = text.replace(N + ',\n', '').replace(', ' + N, '').replace(N + ', ', '')
        # a lone multi-line item without comma
        new = re.sub(r'\n\s*' + re.escape(N) + r'\n', '\n', new)
        action = 'dropped'
    elif exclude_ok and 'not(any(' in text and N not in text:
        new = text.replace('not(any(', 'not(any(' + N + ', ', 1)
        action = 'excluded'
    else:
        manual.append('%s:%d: %s' % (f, line, text.strip()[:100]))
        continue
    L[j:k + 1] = new.split('\n')
    open(f, 'w').write('\n'.join(L))
    done.add((f, j))
    print(action, '%s:%d' % (os.path.relpath(f, crate), j + 1))
for m in manual:
    print('MANUAL', m)
