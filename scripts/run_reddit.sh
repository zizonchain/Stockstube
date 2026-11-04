#!/bin/bash
cd "$(dirname "$0")/.."
for s in "$@"; do python3 -I scripts/collect_reddit.py $s >> data/reddit_$s.log 2>&1; done
