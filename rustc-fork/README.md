# The rustc fork

The fork lives on pkgsrc-bulk-00 at /build/pkgbuild/src/rust, branch `irix`, on rust-lang/rust
0abfedbc7cd4e725f126913880c95800394f7c37 (the 2026-10-02 nightly this repository's `library/`
came from). These are its commits as patches, so the fork can be rebuilt from here:

    git fetch --depth 1 https://github.com/rust-lang/rust.git 0abfedbc7cd4e725f126913880c95800394f7c37
    git checkout -b irix FETCH_HEAD && git am rustc-fork/*.patch

Its `irix/README.md` says how to build it.
