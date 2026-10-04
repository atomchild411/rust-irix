#!/bin/sh
# Make /build/pkgbuild/src/rustc-1.96.1-src: pkgsrc's rustc 1.96.1 source plus the IRIX target,
# std and vendored libc. Run as pkgbuild on pkgsrc-bulk-00 with this directory's files in $P and
# code/rust-library-irix's irix-1.96.1 changes as $P/lib196.diff.
set -e
P=${P:-/tmp/prep196}
R=/build/pkgbuild/src/rustc-1.96.1-src
cd /build/pkgbuild/src
rm -rf "$R"
tar xzf /build/pkgbuild/pkgsrc-irix/distfiles/rustc-1.96.1-src.tar.gz
cd "$R"
git init -q && git config user.name atomchild411 \
  && git config user.email 143453386+atomchild411@users.noreply.github.com
git add -A >/dev/null 2>&1 && git commit -qm "rustc 1.96.1 source"
# pkgsrc's lang/rust patches first, when given (PKGSRC_PATCHES=.../lang/rust/patches)
if [ -n "$PKGSRC_PATCHES" ]; then
  for f in "$PKGSRC_PATCHES"/patch-*; do patch -p0 -s -E --no-backup-if-mismatch < "$f"; done
  git add -A >/dev/null 2>&1 && git commit -qm "pkgsrc lang/rust patches"
fi
# compiler: the target files from the nightly fork's commit, the registrations by hand
git apply --include='compiler/rustc_target/src/spec/base/irix.rs' \
  --include='compiler/rustc_target/src/spec/targets/mips64_sgi_irix.rs' "$P/0001.patch"
python3 "$P/spec196.py"
# library: std's IRIX arms (the tree's own Cargo.toml/Cargo.lock: std uses the vendored libc)
# (as a diff, on top of pkgsrc's own library patches; not its Cargo.toml/Cargo.lock libc path)
git apply --exclude=library/Cargo.toml --exclude=library/Cargo.lock "$P/lib196.diff"
# vendored libc 0.2.183: our IRIX module, and the two hunks 0.2.183 lays out differently
cd vendor/libc-0.2.183
patch -p1 -s --no-backup-if-mismatch < "$P/libc-irix.diff" || true
rm -f src/unix/mod.rs.rej
python3 "$P/libc183.py"
cd "$R"
# every vendored file pkgsrc's patches or ours changed gets its .cargo-checksum.json entry redone
# (pkgsrc's Makefile does this with CKSUM_CRATES/CKSUMS)
git diff --name-only HEAD -- vendor > /tmp/prep196-changed.txt
git diff --name-only d9bc0b6 -- vendor >> /tmp/prep196-changed.txt 2>/dev/null || true
git ls-files --others --exclude-standard vendor >> /tmp/prep196-changed.txt
python3 - <<'PY'
import json, hashlib, os
root = "/build/pkgbuild/src/rustc-1.96.1-src/"
first = os.popen("git -C " + root + " rev-list --max-parents=0 HEAD").read().strip()
changed = set(os.popen("git -C " + root + " diff --name-only " + first + " -- vendor").read().split())
changed |= set(l.strip() for l in open("/tmp/prep196-changed.txt") if l.strip())
crates = {}
for f in changed:
    parts = f.split("/")
    if len(parts) > 2:
        crates.setdefault(parts[1], set()).add("/".join(parts[2:]))
for c, files in crates.items():
    p = root + "vendor/" + c + "/.cargo-checksum.json"
    if not os.path.exists(p):
        continue
    j = json.load(open(p))
    for f in files:
        if f in j["files"]:
            j["files"][f] = hashlib.sha256(open(root + "vendor/" + c + "/" + f, "rb").read()).hexdigest()
    json.dump(j, open(p, "w"), separators=(",", ":"))
print("checksums redone for", len(crates), "crates")
PY
find . -name '*.rej' | sed 's/^/REJECT /'
git add -A >/dev/null 2>&1 && git commit -qm "IRIX: mips64-sgi-irix target, std, vendored libc" && git log --oneline -2
cp "$P/bootstrap.toml" bootstrap.toml
# pkgsrc's SUBST of @PREFIX@ (pre-configure), uncommitted so the commits stay patch material
sed -i 's|@PREFIX@|/build/pkgbuild/pkgsrc-irix/host|g' compiler/rustc_codegen_ssa/src/back/linker.rs \
  compiler/rustc_target/src/spec/base/netbsd.rs src/bootstrap/src/core/build_steps/compile.rs \
  src/bootstrap/src/core/builder/cargo.rs src/bootstrap/bootstrap.py
