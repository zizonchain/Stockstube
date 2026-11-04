# PROGRESS
Spend: $0. YouTube quota: 906 units (videos.list only).
## Done
- HN complete via Algolia (data/raw/hn). Reddit partial: r/ValueInvesting comments 2014 to 2020-03 (data/raw/reddit).
- Metadata for all 45,206 ids with 2+ recommenders (data/raw/youtube).
- In-session labels for 2,096 candidates (data/labels). Summaries for top 30.
- Site in site/, data in site/data, zip on About. python build.py rebuilds.
- MORNING_REPORT.md written.
## Resume
- Reddit: scripts/run_reddit.sh comments <subs...>, then posts. It skips cached windows. Then python build.py --fetch, label new candidates, rerun.
