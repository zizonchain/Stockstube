#!/bin/bash
# Usage: run_reddit.sh MODE SUB...   (MODE = comments | posts)
cd "$(dirname "$0")/.."
mode=$1; shift
for s in "$@"; do python3 -I scripts/collect_reddit.py $s $mode >> data/reddit_$s.log 2>&1; done
