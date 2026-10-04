#!/usr/bin/env python3
"""pkgsrc patch files for lang/rust from the prep-196 tree: for every file the IRIX commit touches,
pristine -> final (so a file pkgsrc already patches gets one combined patch).
usage: gen-pkgsrc-patches.py TREE PKGSRC_PATCHES_DIR OUTDIR"""
import os, subprocess, sys

tree, pkpatches, out = sys.argv[1:4]
git = lambda *a: subprocess.run(["git", "-C", tree, *a], capture_output=True, text=True, check=True).stdout
first, pk, head = git("rev-list", "--reverse", "HEAD").split()[:3]
files = [f for f in git("diff", "--name-only", pk, head).split() if not f.endswith(".cargo-checksum.json")]
os.makedirs(out, exist_ok=True)
cksums = []
NOTE = "IRIX: the mips64-sgi-irix target (IRIX 6.5, MIPS IV, N32) and its std."
for f in sorted(files):
    name = "patch-" + f.replace("_", "__").replace("/", "_")
    old = os.path.join(pkpatches, name)
    if os.path.exists(old):
        hdr = open(old).read().split("\n--- ", 1)[0].rstrip("\n") + "\n\n" + NOTE + "\n"
    else:
        hdr = "$NetBSD$\n\n" + NOTE + "\n"
    d = git("diff", "--no-color", "-U3", first, head, "--", f)
    body = d[d.index("\n@@ ") + 1:]
    new = "new file mode" in d.split("\n@@ ")[0]
    text = hdr + "\n--- " + f + ".orig\n+++ " + f + "\n" + body
    open(os.path.join(out, name), "w").write(text)
    if f.startswith("vendor/") and not new:
        import hashlib
        a = hashlib.sha256(git("show", first + ":" + f).encode()).hexdigest()
        b = hashlib.sha256(open(os.path.join(tree, f), "rb").read()).hexdigest()
        cksums.append("# " + f + "\nCKSUMS+=\t" + a + "\nCKSUMS+=\t" + b)
    print(("new  " if new else ("merge" if os.path.exists(old) else "add  ")), name)
print("\n".join(cksums))
