#!/bin/sh
# Push code/rust-libc, code/rust-library-irix and a test crate to the VM, build it for IRIX.
# usage: sync-build.sh [crate]   (hello-std, or a directory under scratch/rust-irix)
set -e
C=${1:-hello-std}
# TC=1.96.1 builds against that release (the irix-1.96.1 branch must be checked out)
TC=${TC:-nightly}
SRC=rust-src; [ "$TC" = nightly ] || SRC=rust-src-$TC
W=/Volumes/portable/workspace-claude/IRIX
V=root@pkgsrc-bulk-00
S=/build/pkgbuild/rust-spike
rsync -a --delete --exclude target --exclude .git $W/code/rust-libc/ $V:$S/libc/
rsync -a --delete --exclude target --exclude .git $W/code/rust-library-irix/library/ $V:$S/$SRC/library/
if [ -d $W/scratch/rust-irix/$C ]; then
  rsync -a --exclude target $W/scratch/rust-irix/$C/ $V:$S/$C/
  rsync -a $W/scratch/rust-irix/mips64-sgi-irix.json $V:$S/$C/
fi
# build-std crates are fingerprinted by version, not by their sources: start clean.
ssh $V "chown -R pkgbuild: $S/libc $S/$SRC $S/$C && su pkgbuild -c 'cd $S/$C && rm -rf target; export RUSTUP_HOME=$S/rustup CARGO_HOME=$S/cargo PATH=$S/cargo/bin:\$PATH RUSTC_BOOTSTRAP=1 __CARGO_TESTS_ONLY_SRC_ROOT=$S/$SRC/library; timeout 1500 cargo +$TC build --release -Z build-std=std,panic_unwind -Z json-target-spec --target mips64-sgi-irix.json > ../$C-$TC-build.log 2>&1; echo exit \$?; grep -c \"^error\" ../$C-$TC-build.log'" || true
