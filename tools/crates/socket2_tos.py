# IRIX has IP_TOS: socket2's TOS methods (left out with Haiku's) apply.
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cfgedit import set_os
f = sys.argv[1] + '/src/socket.rs'
n = sum(set_os(f, a, 'prev', False) for a in ('pub fn set_tos_v4(', 'pub fn tos_v4(', 'pub fn set_tos(', 'pub fn tos('))
u = sys.argv[1] + '/src/sys/unix.rs'
n += set_os(u, 'pub(crate) use libc::IP_TOS;', 'prev', False)
print('ok', sys.argv[1], n)
