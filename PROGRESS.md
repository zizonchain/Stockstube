# PROGRESS
Spend: $0 (no paid APIs). YouTube quota used: ~440 units of 10,000.
## Done
- Phase 0 setup. HN Algolia collection (data/raw/hn, nearly complete). YouTube metadata for 21,664 ids with 2+ recommenders (data/raw/youtube).
- Crude end to end: python build.py -> site/data. Site in site/ (index.html, app.js, style.css).
## Running
- Reddit queue (scripts/run_reddit.sh) via Arctic Shift; heavy throttling, gaps in data/raw/reddit/*/giveup.log.
## Next
- In-session classification into data/labels/*.jsonl (candidates from rule prefilter), rerun rank.py.
- Site QA with Playwright, report.
