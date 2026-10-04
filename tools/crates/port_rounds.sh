#!/bin/sh
# port_rounds.sh TEST CRATEDIR... [-- MISSING_NAME...]: build test crate TEST; between builds, take
# IRIX out of the cfgs of failing lines in the CRATEDIRs (drop-only), then, for errors naming one
# of the MISSING_NAMEs (things IRIX lacks), exclude IRIX where a not(any(...)) list allows.
T=$1; shift
C=; while [ $# -gt 0 ] && [ "$1" != -- ]; do C="$C $1"; shift; done
[ "$1" = -- ] && shift
cd /tmp/crates
sh tbuild.sh $T 0 >/dev/null
for round in 1 2 3 4 5; do
  n=0
  for c in $C; do n=$((n + $(python3 cfg_autofix.py $T.log $c | grep -c '^dropped'))); done
  if [ $# -gt 0 ]; then
    python3 filter_log.py $T.log "$@" > $T-missing.log
    for c in $C; do n=$((n + $(python3 cfg_autofix.py $T-missing.log $c --exclude | grep -c '^dropped\|^excluded'))); done
  fi
  echo "round $round: $n fixed; $(sh tbuild.sh $T 0)"
  [ $n = 0 ] && break
done
sh tbuild.sh $T 40
