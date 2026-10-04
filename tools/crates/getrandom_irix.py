#!/usr/bin/env python3
"""getrandom_irix.py CRATEDIR: IRIX in getrandom (0.2, 0.3, 0.4): getentropy(), which the IRIX
toolchain's compiler-rt provides, as on macOS and OpenBSD; errno from __oserror()."""
import os, sys

d = sys.argv[1]


def sub(path, a, b, n=1):
    p = os.path.join(d, path)
    s = open(p).read()
    assert s.count(a) == n, (path, a, s.count(a))
    open(p, 'w').write(s.replace(a, b))


ERRNO_AIX = '    } else if #[cfg(target_os = "aix")] {\n        use libc::_Errno as errno_location;\n'
ERRNO_IRIX = ERRNO_AIX + '    } else if #[cfg(target_os = "irix")] {\n        use libc::__oserror as errno_location;\n'
LIST = '        target_os = "vita",\n        target_os = "emscripten",\n'

if os.path.exists(os.path.join(d, 'src/backends.rs')):           # 0.3, 0.4
    sub('src/backends.rs', LIST, LIST + '        target_os = "irix",\n')
    e = 'src/util_libc.rs' if os.path.exists(os.path.join(d, 'src/util_libc.rs')) else 'src/utils/get_errno.rs'
    sub(e, ERRNO_AIX, ERRNO_IRIX)
    # getentropy's libc dependency
    sub('Cargo.toml', 'target_os = "vita", target_os = "emscripten"))\'.dependencies.libc]',
        'target_os = "vita", target_os = "emscripten", target_os = "irix"))\'.dependencies.libc]')
else:                                                             # 0.2
    sub('src/lib.rs', LIST, LIST + '        target_os = "irix",\n')
    sub('src/util_libc.rs', ERRNO_AIX, ERRNO_IRIX)
print('ok', d)
