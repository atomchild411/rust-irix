#!/usr/bin/env python3
"""irix_only_deps.py CRATEDIR...: drop the [target.'cfg(...)'.*] tables of a crate's Cargo.toml
whose cfg is false both for mips64-sgi-irix and for the build host (x86_64-unknown-linux-gnu: build
scripts and proc macros use the same patched crate there). Cargo resolves every target's
dependencies, so a crate patched in for IRIX builds would otherwise need, say, the Windows crates
its version asks for, which a package's vendored crates (for an older version) do not have."""
import re, sys

IRIX = {'target_os': 'irix', 'target_family': 'unix', 'target_arch': 'mips64', 'target_env': '',
        'target_vendor': 'sgi', 'target_pointer_width': '32', 'target_endian': 'big',
        'target_abi': 'abin32', 'target_has_atomic': None}
HOST = {'target_os': 'linux', 'target_family': 'unix', 'target_arch': 'x86_64', 'target_env': 'gnu',
        'target_vendor': 'unknown', 'target_pointer_width': '64', 'target_endian': 'little',
        'target_abi': '', 'target_has_atomic': None}
FLAGS = {'unix': True, 'windows': False}


def parse(s, env):
    toks = re.findall(r'[A-Za-z_][A-Za-z0-9_]*|"[^"]*"|[(),=]', s)
    pos = [0]

    def peek():
        return toks[pos[0]] if pos[0] < len(toks) else None

    def take():
        t = toks[pos[0]]
        pos[0] += 1
        return t

    def expr():
        name = take()
        if peek() == '(' and name in ('any', 'all', 'not'):
            take()
            args = []
            while peek() != ')':
                args.append(expr())
                if peek() == ',':
                    take()
            take()
            if name == 'any':
                return any(args)
            if name == 'all':
                return all(args)
            return not args[0]
        if peek() == '=':
            take()
            val = take().strip('"')
            if name not in env:
                return False
            return env[name] is None or env[name] == val
        return FLAGS.get(name, False)

    return expr()


def dep_names(table):
    """The dependency names a dependency table declares."""
    m = re.match(r'\[[^\]]*dependencies\.([A-Za-z0-9_-]+)\]', table)
    if m:
        return {m.group(1)}
    if re.match(r'\[[^\]]*dependencies\]', table):
        return set(re.findall(r'(?m)^([A-Za-z0-9_-]+)\s*=', table))
    return set()


def strip(path):
    s = open(path).read()
    # tables run from their header to the next header
    parts = re.split(r'(?m)^(?=\[)', s)
    out, dropped, gone = [], [], set()
    for p in parts:
        m = re.match(r"""\[target\.(['"])cfg\((.*)\)\1\.""", p)
        if m and not (parse(m.group(2), IRIX) or parse(m.group(2), HOST)):
            dropped.append(m.group(2))
            gone |= dep_names(p)
            continue
        out.append(p)
    # ... and the features naming dependencies no table declares any more; a dependency left
    # only in non-optional tables loses its "?" and "dep:" in features
    kept = set().union(*(dep_names(p) for p in out))
    optional = set().union(*(dep_names(p) for p in out if re.search(r'(?m)^optional\s*=\s*true', p)))
    required = kept - optional
    gone -= kept
    for i, p in enumerate(out):
        if p.startswith('[features]'):
            for d in gone:
                p = re.sub(r'\n\s*"(?:dep:%s|%s\??/[^"]*|%s)",?(?=\n)' % ((re.escape(d),) * 3), '', p)
                p = re.sub(r'"(?:dep:%s|%s\??/[^"]*|%s)",?\s*' % ((re.escape(d),) * 3), '', p)
            features = set(re.findall(r'(?m)^([A-Za-z0-9_-]+)\s*=', p))
            for d in required:
                p = p.replace('"%s?/' % d, '"%s/' % d)
                p = re.sub(r'\n\s*"dep:%s",?(?=\n)' % re.escape(d), '', p)
                if d not in features:   # enabling a required dependency
                    p = re.sub(r'\n\s*"%s",?(?=\n)' % re.escape(d), '', p)
                    p = re.sub(r'"%s",?\s*' % re.escape(d), '', p)
            out[i] = p
    open(path, 'w').write(''.join(out))
    return dropped + ['dependency ' + d for d in sorted(gone)]


for d in sys.argv[1:]:
    for c in strip(d.rstrip('/') + '/Cargo.toml'):
        print('%s: dropped cfg(%s)' % (d, c))
