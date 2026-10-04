#!/bin/sh
# pkg_resolve.sh PKGPATH [CRATE]: set a pkgsrc Rust package up the way cargo.mk does (its distfile,
# its vendored crates, the IRIX overlays as [patch.crates-io], the patched crates dropped from
# Cargo.lock) in /tmp/resolve/PKG, then resolve for IRIX offline: say which overlays cargo leaves
# unused and, for CRATE, why (cargo update --precise to the overlay's version).
set -e
P=$1; C=$2
PKGSRC=${PKGSRC:-/build/pkgbuild/src/pkgsrc-test}
D=${DISTDIR:-/build/pkgbuild/pkgsrc-irix/distfiles}
O=${OVERLAYS:-/tmp/crates}
W=/tmp/resolve/$(echo "$P" | tr / _)
export CARGO_HOME=$W/cargo-home CARGO_HTTP_CAINFO=/etc/ssl/certs/ca-certificates.crt
export PATH=/build/pkgbuild/pkgsrc-irix/host/bin:$PATH
rm -rf "$W"; mkdir -p "$W/vendor" "$CARGO_HOME"
cd "$W"
mk=$PKGSRC/$P/Makefile
dist=$(cd "$PKGSRC/$P" && bmake show-var VARNAME=DISTFILES 2>/dev/null | tr ' ' '\n' | grep -v '\.crate$' | head -1)
[ -n "$dist" ] && tar xf "$D/$dist" 2>/dev/null || true
src=$(cd "$PKGSRC/$P" && bmake show-var VARNAME=CARGO_WRKSRC 2>/dev/null | sed "s|.*/work[^/]*/||")
for c in $(sed -n 's/^CARGO_CRATE_DEPENDS+=[[:space:]]*//p' "$PKGSRC/$P/cargo-depends.mk"); do
  tar xf "$D/$c.crate" -C vendor
  printf '{"package":"%s","files":{}}' "$(sha256sum < "$D/$c.crate" | cut -d' ' -f1)" > "vendor/$c/.cargo-checksum.json"
done
cat > "$CARGO_HOME/config.toml" <<EOF
[source.crates-io]
replace-with = "vendored-sources"
[source.vendored-sources]
directory = "$W/vendor"
[patch.crates-io]
EOF
for o in "$O"/libc-0.2.189 "$O"/getrandom-* "$O"/mio-* "$O"/parking_lot_core-* "$O"/socket2-* \
         "$O"/libloading-* "$O"/rustix-* "$O"/errno-* "$O"/tokio-1* "$O"/tokio-macros-* "$O"/linux-raw-sys-*; do
  [ -d "$o" ] || continue
  b=$(basename "$o"); n=${b%-[0-9]*}; v=${b##*-}
  printf '%s = { path = "%s", package = "%s" }\n' "$(echo "$n-$v" | tr . _)" "$o" "$n" >> "$CARGO_HOME/config.toml"
done
cd "$W/$src"
for n in $(sed -n 's/^\([a-z0-9_-]*\) = { path.*package = "\([^"]*\)".*/\2/p' "$CARGO_HOME/config.toml" | sort -u); do
  awk -v n="$n" 'BEGIN { RS = ""; ORS = "\n\n" } index($0, "\nname = \"" n "\"\n") == 0' Cargo.lock > Cargo.lock.x && mv Cargo.lock.x Cargo.lock
done
cargo metadata --offline --format-version 1 2>&1 >/dev/null | grep -i 'not used\|error' | sed 's/ (\/[^)]*)//' || true
if [ -n "$C" ]; then
  v=$(ls -d "$O/$C"-* | tail -1 | sed 's/.*-//')
  cargo update --offline -p "$C" --precise "$v" 2>&1 | tail -20
fi
