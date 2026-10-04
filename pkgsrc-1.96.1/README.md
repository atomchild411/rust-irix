# IRIX in pkgsrc's lang/rust 1.96.1

How pkgsrc's lang/rust patches for IRIX are made, on pkgsrc-bulk-00:

- `prep-196.sh` builds /build/pkgbuild/src/rustc-1.96.1-src from pkgsrc's rustc-1.96.1-src.tar.gz:
  pkgsrc's own lang/rust patches (PKGSRC_PATCHES), then the IRIX target (`spec196.py`, plus the two
  new target files from the nightly fork's first patch), this branch's std (`lib196.diff` =
  `git diff 60b31ed irix-1.96.1 -- library`), and the libc fork's IRIX module on the vendored libc
  0.2.183 (`libc-irix.diff` = rust-libc `git diff 0.2.189 irix -- src`, adjusted by `libc183.py`).
  It redoes vendored checksums and pkgsrc's @PREFIX@ SUBST so the tree builds as pkgsrc's would
  (with `bootstrap-196.toml`: `./x.py build --stage 1 library`).
- `gen-pkgsrc-patches.py` writes the pkgsrc patch files (pristine to final per file, merged with
  pkgsrc's) and prints the CKSUMS for lang/rust's Makefile.
