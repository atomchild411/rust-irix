#!/usr/bin/env python3
"""cfgedit: set_os(path, anchor, where, present) puts target_os = OS in, or takes it out of, the
cfg attribute just before ('prev') or just after ('next') each occurrence of anchor; replace(path,
old, new) for the rest. Used by the per-crate IRIX port scripts."""
import re

OS = 'irix'
N = 'target_os = "%s"' % OS


def _blocks(s, anchor, where):
    out, pos = [], 0
    while True:
        a = s.find(anchor, pos)
        if a < 0:
            return out
        if where == 'next':
            j = s.find('#[cfg', a)
        else:
            j = s.rfind('#[cfg', 0, a)
        if j >= 0:
            depth, k = 0, s.index('(', j)
            while True:
                if s[k] == '(':
                    depth += 1
                elif s[k] == ')':
                    depth -= 1
                    if depth == 0:
                        break
                k += 1
            out.append((j, k + 1))
        pos = a + len(anchor)


def set_os(path, anchor, where, present):
    s = open(path).read()
    n = 0
    for j, k in reversed(_blocks(s, anchor, where)):
        b = s[j:k]
        if present and N not in b:
            m = re.search(r'any\(', b)
            if not m:
                continue
            nb = b[:m.end()] + N + ', ' + b[m.end():]
        elif not present and N in b:
            nb = re.sub(r'\n\s*' + re.escape(N) + r',?(?=\n)', '', b)
            nb = nb.replace(', ' + N, '').replace(N + ', ', '').replace(N + ',', '')
        else:
            continue
        s = s[:j] + nb + s[k:]
        n += 1
    open(path, 'w').write(s)
    return n


def replace(path, old, new, count=None):
    s = open(path).read()
    c = s.count(old)
    assert c and (count is None or c == count), (path, old[:60], c)
    open(path, 'w').write(s.replace(old, new))
