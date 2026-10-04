#!/usr/bin/env python3
"""mkdistinfo.py DISTDIR PATCHDIR DISTFILE...: a pkgsrc distinfo on stdout."""
import hashlib, os, re, sys
dd, pd = sys.argv[1:3]
L = ['$NetBSD$', '']
for f in sys.argv[3:]:
    b = open(os.path.join(dd, f), 'rb').read()
    L += ['BLAKE2s (%s) = %s' % (f, hashlib.blake2s(b).hexdigest()),
          'SHA512 (%s) = %s' % (f, hashlib.sha512(b).hexdigest()),
          'Size (%s) = %d bytes' % (f, len(b))]
for p in sorted(os.listdir(pd)):
    if not p.startswith('patch-'):
        continue
    t = open(os.path.join(pd, p), 'rb').read().decode('utf-8', 'surrogateescape')
    body = ''.join(l for l in t.splitlines(True) if not re.search(r'\$NetBSD', l))
    L.append('SHA1 (%s) = %s' % (p, hashlib.sha1(body.encode('utf-8', 'surrogateescape')).hexdigest()))
print('\n'.join(L))
