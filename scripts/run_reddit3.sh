#!/bin/bash
# Finish link-post gaps, then collect YouTube-linking comments, smallest subreddit first.
cd "$(dirname "$0")/.."
python3 -I scripts/collect_reddit2.py posts investing Bogleheads
python3 -I scripts/collect_reddit3.py comments econmonitor SecurityAnalysis quant finance ValueInvesting dividends Bogleheads StockMarket financialindependence investing stocks
