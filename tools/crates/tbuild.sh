#!/bin/sh
# tbuild.sh DIR: build the test crate in /tmp/crates/DIR for IRIX; tally the errors.
cd /tmp/crates/$1 || exit 1
export RUSTFLAGS="--cap-lints warn" CARGO_HTTP_CAINFO=/etc/ssl/certs/ca-certificates.crt \
  CARGO_HOME=/tmp/crates/cargo-home \
  CARGO_TARGET_MIPS64_SGI_IRIX_LINKER=/build/pkgbuild/pkgsrc-irix/tools/bin/mipseb-sgi-irix6.5-clang \
  PATH=/build/pkgbuild/pkgsrc-irix/host/bin:$PATH
cargo build --release --target mips64-sgi-irix > /tmp/crates/$1.log 2>&1
echo "errors: $(grep -c '^error' /tmp/crates/$1.log)"
grep -A3 '^error' /tmp/crates/$1.log | grep -o 'cannot find [a-z ,]* `[A-Za-z0-9_]*`\|no field `[A-Za-z0-9_]*`\|unresolved import `[A-Za-z0-9_:]*`\|mismatched types\|no method named `[A-Za-z0-9_]*`' | sort | uniq -c | sort -rn | head -${2:-80}
