#!/bin/sh
# all_patches.sh OUT: the pkgsrc patches for every crate rust-irix-crates ports (from the crate
# trees in /tmp/crates), each with its note. libc's come from the libc fork instead.
OUT=${1:-pkgpatches}; [ $# -gt 0 ] && shift
T=" Cargo.toml: only the dependencies (and features) IRIX builds and the build host use."
G="/dev/urandom, as on AIX; errno from __oserror().$T"
M="the poll() selector and plain accept/pipe, as on the systems without epoll, kqueue, accept4 or pipe2.$T"
P="no pthread_condattr_setclock, so condvar timeouts in CLOCK_REALTIME, as on Android.$T"
S="the options IRIX has (none of the BSD sockaddr lengths, IPv6 receive options or TCP keepalive tuning), as on Haiku, and IP_TOS.$T"
L="IRIX dlfcn.h values: RTLD_LAZY 1, RTLD_NOW 2, RTLD_GLOBAL 4, RTLD_LOCAL 0.$T"
R="IRIX as Haiku is, where it is (poll, no accept4/pipe2/ppoll, no fadvise/posix_madvise/fallocate/futimens, no TCP keepalive tuning or TIOCSCTTY), with the standard sockaddr layouts, XPG msghdr, ioctl(int, int, ...), madvise() with MADV_* and, IRIX N32 time_t being 32 bits, fix_y2038.$T"
E="errno is at __oserror().$T"
K="no peer credentials for UNIX-domain sockets (an error); signed uid_t/gid_t, as on QNX.$T"
rm -rf "$OUT"
python3 "$(dirname "$0")/crate_patches.py" "$OUT" \
  "getrandom-0.2.17=$G" "getrandom-0.3.4=$G" "getrandom-0.4.3=$G" \
  "mio-0.8.11=$M" "mio-1.2.3=$M" "parking_lot_core-0.9.12=$P" \
  "socket2-0.4.10=$S" "socket2-0.5.10=$S" "socket2-0.6.5=$S" \
  "libloading-0.7.4=$L" "libloading-0.8.9=$L" \
  "rustix-0.38.44=$R" "rustix-1.1.5=$R" "errno-0.3.14=$E" "tokio-1.53.1=$K" "$@"
