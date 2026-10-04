# Porting crates to IRIX

Crates that pick their code by operating system need IRIX named. Most of the time IRIX behaves
like a system the crate already knows; the work is choosing which, and then correcting where IRIX
parts from it. The results become pkgsrc patches in `lang/rust-irix-crates`.

## The tools

- `add_like.py DIR REF irix`: add `target_os = "irix"` to every cfg list (several systems, in
  Rust sources and Cargo.toml target tables) that names `REF`.
- `drop_before.py FILE MARKER`: take IRIX out of the cfg just above each line containing
  MARKER; `exclude_before.py FILE MARKER` adds it to a `not(any(...))` list there instead.
- `cfgedit.py`: the same as a library (`set_os(path, anchor, 'prev'|'next', present)`), for the
  per-crate scripts.
- `cfg_autofix.py LOG DIR [--exclude]`: from a build log, take IRIX out of the cfg that governs
  each failing line. Without `--exclude` it only drops IRIX from positive lists (safe after
  `add_like.py`); `--exclude` also adds it to `not(any(...))` lists, which is right only where the
  failing code uses something IRIX lacks: run it on a log narrowed by `filter_log.py LOG NAME...`.
- `irix_only_deps.py DIR...`: drop the dependency tables of a crate's Cargo.toml whose cfg is
  false for IRIX (a small cfg evaluator), and fix the features that named them. A crate patched
  in with `[patch.crates-io]` must resolve against a package's vendored crates; a newer version's
  Windows or WASI dependencies are not among them, and cargo then quietly uses the vendored,
  unported crate instead.
- `crate_patches.py OUT DIR=NOTE...`: pkgsrc patch files from each crate tree's git diff, with
  paths under the crate's directory (`lang/rust-irix-crates` extracts every crate in WRKDIR).
- `mkdistinfo.py DISTDIR PATCHDIR DISTFILE...`: the package's distinfo.
- `tbuild.sh DIR`: build a test crate for IRIX and tally the errors.

The scripts name the build host's paths (the IRIX cross toolchain under
`/build/pkgbuild/pkgsrc-irix`, crates unpacked in `/tmp/crates`, each a git tree).

## The ports

| Crate | Versions | IRIX is like | Then |
|---|---|---|---|
| getrandom | 0.2, 0.3, 0.4 | AIX (`/dev/urandom`) | errno from `__oserror()`: `getrandom_irix.py` |
| mio | 0.8 | Vita | `add_like.py mio vita irix` and `aix irix`; not in the `sin_len`/`sin6_len` or `pipe2` lists |
| mio | 1 | QNX (`nto`) | not in the `sin_len`/`sin6_len` lists |
| parking_lot_core | 0.9 | Android: no `pthread_condattr_setclock`, `CLOCK_REALTIME` timeouts | `plc_irix.py` |
| socket2 | 0.4, 0.5, 0.6 | Haiku | not in the `ss_len`/`sin_len`/`sin6_len` lists; `IP_TOS` back (`socket2_tos.py`); 0.4: not in the `recv_tos` lists |
| libloading | 0.7, 0.8 | (none) | IRIX's `RTLD_*` values: `libloading_irix.py` |
| rustix | 0.38, 1 | Haiku | `cfg_autofix.py` rounds, `--exclude` for the missing calls (fadvise, posix_madvise, fallocate, futimens, ppoll, clock_nanosleep, TCP keepalive tuning, ...), then `rustix_irix.py` (standard sockaddr layouts, XPG msghdr, `ioctl(int, int, ...)`, `madvise()`, no `TIOCSCTTY`, and `fix_y2038`: N32's `time_t` is 32 bits) |
| errno | 0.3 | (none) | errno at `__oserror()`: `errno_irix.py` |
| tokio | 1 | (none) | no peer credentials (an error, not uid 0), signed uid/gid as on QNX: `tokio_irix.py`; ships with tokio-macros 2.7.1 unchanged, which it needs |

Every crate also gets `irix_only_deps.py`. Each port was checked at run time on IRIX with the
test crates in `../../tests`.

What IRIX lacks, for reference: no epoll or kqueue (`poll`), no `accept4`, `pipe2`, `dup3` or
`ppoll`, no `futimens` (a descriptor's times cannot be set), no `posix_fadvise`,
`posix_madvise` or `posix_fallocate`, no `pthread_condattr_setclock`, no socket timeouts
(`SO_RCVTIMEO`/`SO_SNDTIMEO` fail with `ENOPROTOOPT`), no TCP keepalive tuning, no IPv6, no
`TIOCSCTTY`, no peer credentials on UNIX-domain sockets, and no BSD `sa_len` fields.
