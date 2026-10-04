# Rust for IRIX

Rust for SGI IRIX 6.5: the `mips64-sgi-irix` target (N32 ABI, MIPS IV, big-endian), its standard
library, and what it takes to build Rust programs for IRIX, by hand or with pkgsrc.

What runs: `std` (files, threads, processes, sockets, time), unwinding with symbolized
backtraces, and crates.io programs such as ripgrep, and crates such as tokio, rustix, mio and
socket2, cross-built on Linux and run on IRIX 6.5.22.

## Where the pieces are

| Repository | What it holds |
|---|---|
| [atomchild411/libc](https://github.com/atomchild411/libc/tree/irix), branch `irix` | the `libc` crate's IRIX module (types, layouts, constants and functions, part generated from clang's view of the IRIX headers: `ci/irix/`) |
| [atomchild411/rust](https://github.com/atomchild411/rust/tree/irix), branch `irix` | rustc with `mips64-sgi-irix` built in, and std's IRIX support (`irix/README.md` says how to build it) |
| [atomchild411/pkgsrc](https://github.com/atomchild411/pkgsrc/tree/irix), branch `irix` | `lang/rust` with the target and std for IRIX as a cross target (`RUST_EXTRA_TARGETS`), `rust.mk`/`cargo.mk` cross-building (`RUST_CROSS_TARGET`), and `lang/rust-irix-crates`: crates.io crates taught IRIX, used in place of the vendored ones |
| this repository | the rest: the porting tools, the tests, the target spec |

This repository's branches:

- `main`: these tools and tests.
- `std-1.96.1`: std's IRIX support on Rust 1.96.1 (pkgsrc's version), and in `pkgsrc-1.96.1/`
  how pkgsrc's `lang/rust` patches are made from it.
- `std-nightly`: the first port, std on the 2026-10-02 nightly as `rust-src` ships it, built with
  `-Z build-std` and the JSON target spec; superseded by the rustc fork.

## The toolchain underneath

Rust programs for IRIX link with the IRIX cross toolchain: clang 21 with IRIX support (header
wrappers that supply what IRIX lacks, and compiler-rt builtins for the missing POSIX calls),
lld, and the IRIX 6.5.22 headers and libraries as the sysroot. The libc crate describes IRIX
as that toolchain presents it: where clang's wrappers rename a function (`__irix_*`), libc
links the renamed one.

## Layout of this branch

- `target/mips64-sgi-irix.json`: the target as a JSON spec, for a stock nightly with
  `-Z build-std` (the rustc fork has it built in).
- `tests/std-smoke`: std on IRIX, one line per area (args/env, fs, threads, condvar/time,
  process, net, misc, unwinding).
- `tests/{ctest,stest,ltest,rtest,ttest}`: the ported crates at run time (getrandom and mio;
  socket2; libloading; rustix; tokio). Their `[patch.crates-io]` names sibling directories
  holding the ported crates.
- `tools/crates`: how crates are ported; see its README.
- `tools/spike/sync-build.sh`: the first spike's driver (std from source with `-Z build-std`).
