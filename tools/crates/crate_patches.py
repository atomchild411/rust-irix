#!/usr/bin/env python3
"""crate_patches.py OUTDIR CRATEDIR=NOTE...: pkgsrc patch files (paths under the crate's
directory, WRKSRC being WRKDIR) from each crate tree's uncommitted git diff."""
import os, re, subprocess, sys
out = sys.argv[1]
os.makedirs(out, exist_ok=True)
for arg in sys.argv[2:]:
    c, note = arg.split('=', 1)
    d = subprocess.run(['git', '-C', c, 'diff', '--no-color'], capture_output=True, text=True, check=True).stdout
    for part in re.split(r'(?m)^(?=diff --git )', d):
        if not part.strip():
            continue
        f = re.match(r'diff --git a/(\S+) b/', part).group(1)
        body = part[part.index('\n@@ ') + 1:]
        path = os.path.basename(c) + '/' + f
        name = 'patch-' + path.replace('_', '__').replace('/', '_')
        open(os.path.join(out, name), 'w').write(
            '$NetBSD$\n\nIRIX 6.5 (mips64-sgi-irix): ' + note + '\n\n--- ' + path + '.orig\n+++ ' + path + '\n' + body)
        print(name)
