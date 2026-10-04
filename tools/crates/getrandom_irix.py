# IRIX in getrandom: /dev/urandom as on AIX, errno from __oserror.
import re, sys, os
d = sys.argv[1]
def sub(path, a, b, n=None):
    p = os.path.join(d, path); s = open(p).read()
    c = s.count(a)
    assert c and (n is None or c == n), (path, a, c)
    open(p, 'w').write(s.replace(a, b))
if os.path.exists(os.path.join(d, 'src/backends.rs')):           # 0.3, 0.4
    sub('src/backends.rs', '        target_os = "nto",\n        target_os = "aix",\n',
        '        target_os = "nto",\n        target_os = "aix",\n        target_os = "irix",\n', 1)
    e = 'src/util_libc.rs' if os.path.exists(os.path.join(d, 'src/util_libc.rs')) else 'src/utils/get_errno.rs'
    sub(e, '    } else if #[cfg(target_os = "aix")] {\n        use libc::_Errno as errno_location;\n',
        '    } else if #[cfg(target_os = "aix")] {\n        use libc::_Errno as errno_location;\n'
        '    } else if #[cfg(target_os = "irix")] {\n        use libc::__oserror as errno_location;\n', 1)
else:                                                             # 0.2
    sub('src/lib.rs', 'target_os = "nto", target_os = "aix"))] {', 'target_os = "nto", target_os = "aix", target_os = "irix"))] {', 1)
    sub('src/util_libc.rs', '    } else if #[cfg(target_os = "aix")] {\n        use libc::_Errno as errno_location;\n',
        '    } else if #[cfg(target_os = "aix")] {\n        use libc::_Errno as errno_location;\n'
        '    } else if #[cfg(target_os = "irix")] {\n        use libc::__oserror as errno_location;\n', 1)
print('ok', d)
