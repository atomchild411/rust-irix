#!/usr/bin/env python3
"""filter_log.py LOG NAME...: the error blocks of LOG that mention one of the NAMEs."""
import re, sys
text = open(sys.argv[1]).read()
names = sys.argv[2:]
for b in re.split(r'(?m)^(?=error|warning)', text):
    if b.startswith('error') and any(re.search(r'\b%s\b' % re.escape(n), b.split('\n')[0] + b) for n in names):
        print(b, end='')
