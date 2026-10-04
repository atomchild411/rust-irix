#!/usr/bin/env python3
"""rustix_irix.py CRATEDIR: the hand-made part of rustix's IRIX port, after add_like.py (haiku),
irix_only_deps.py and the cfg_autofix.py rounds: where IRIX parts from Haiku."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cfgedit import set_os, replace

d = sys.argv[1]
P = lambda p: os.path.join(d, p)

# poll() and no ppoll
set_os(P('src/backend/libc/event/syscalls.rs'), '// If we have `ppoll`', 'next', False)
set_os(P('src/backend/libc/event/syscalls.rs'), "// If we don't have `ppoll`", 'next', False)
# XPG msghdr: size_t msg_controllen
set_os(P('src/backend/libc/net/msghdr.rs'), 'fn msg_control_len(len: usize) -> c::socklen_t', 'prev', False)
set_os(P('src/backend/libc/net/msghdr.rs'), 'fn msg_control_len(len: usize) -> c::size_t', 'prev', False)
# no BSD sockaddr lengths: a u16 family
for f in ('src/backend/libc/net/read_sockaddr.rs',):
    for a in ('sa_len: u8,', 'ss_len: u8,', 'sa_family: u8,', 'ss_family: u8,'):
        set_os(P(f), a, 'prev', False)
    for a in ('sa_family: u16,', 'ss_family: u16,'):
        set_os(P(f), a, 'prev', False)
# ioctl(int, int, ...)
set_os(P('src/ioctl/mod.rs'), 'type _Opcode = c::c_ulong;', 'prev', False)
set_os(P('src/ioctl/mod.rs'), '// AIX, Emscripten, Fuchsia, Solaris, and WASI use a `int`.', 'next', True)
# madvise() with MADV_*, as on Android (no posix_madvise)
s = open(P('src/backend/libc/mm/syscalls.rs')).read()
i = s.index('pub(crate) fn madvise(')
j = s.index('\n}\n', i)
body = s[i:j].replace('#[cfg(not(target_os = "android"))]',
                      '#[cfg(not(any(target_os = "android", target_os = "irix")))]').replace(
                      '#[cfg(target_os = "android")]', '#[cfg(any(target_os = "android", target_os = "irix"))]')
open(P('src/backend/libc/mm/syscalls.rs'), 'w').write(s[:i] + body + s[j:])
# no fallocate
set_os(P('src/backend/libc/fs/syscalls.rs'), 'pub(crate) fn fallocate(', 'prev', True)
set_os(P('src/fs/fd.rs'), 'pub fn fallocate<', 'prev', True)
# standard struct layouts (Haiku's differ): sin_zero[8], u16 families, sa_data[14], sun_path[108]
for f, anchors in [('src/backend/libc/net/write_sockaddr.rs', ['sin_zero: [0; 8_usize],']),
                   ('src/backend/libc/net/read_sockaddr.rs', ['sa_family: 0_u16,', 'sa_data: [0; 14],']),
                   ('src/backend/libc/net/addr.rs', ['sun_path: [0; 108],', 'sun_family: 0_u16,'])]:
    for a in anchors:
        if os.path.exists(P(f)):
            set_os(P(f), a, 'prev', False)
# 0.38: the opcode type is _RawOpcode, msg_control_len lives in conv.rs
if os.path.exists(P('src/backend/libc/conv.rs')):
    set_os(P('src/backend/libc/conv.rs'), 'pub(crate) fn msg_control_len(len: usize) -> c::socklen_t', 'prev', False)
    set_os(P('src/backend/libc/conv.rs'), 'pub(crate) fn msg_control_len(len: usize) -> c::size_t', 'prev', False)
set_os(P('src/ioctl/mod.rs'), 'type _RawOpcode = c::c_ulong;', 'prev', False)
# no TIOCSCTTY (IRIX gives a session leader its controlling terminal on open)
for a in ('pub fn ioctl_tiocsctty<', 'struct Tiocsctty;'):
    set_os(P('src/process/ioctl.rs'), a, 'prev', True)
# IRIX N32's time_t is 32 bits (its arch is mips64, which the build script's check misses):
# rustix 1 must convert its 64-bit Timespec
b = P('build.rs')
t = open(b).read()
if '        use_feature("fix_y2038");' in t and 'os == "irix"' not in t:
    i = t.index('        use_feature("fix_y2038");')
    j = t.rindex('    if libc\n', 0, i)
    t = t[:j] + '    if (libc && os == "irix")\n        ||' + t[j + len('    if'):]
    open(b, 'w').write(t)
# ... but its futimens helper for that has nothing to call on IRIX
f = P('src/backend/libc/fs/syscalls.rs')
t = open(f).read()
t = t.replace('#[cfg(all(fix_y2038, not(apple)))]\nfn futimens_old(',
              '#[cfg(all(fix_y2038, not(apple), not(target_os = "irix")))]\nfn futimens_old(')
open(f, 'w').write(t)
print('ok', d)
