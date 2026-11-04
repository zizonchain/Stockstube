# PROGRESS
Spend: $0. YouTube quota: 911 units (videos.list only).
## Done
- HN complete (Algolia). Reddit link posts: r/SecurityAnalysis, r/ValueInvesting complete; r/investing, r/Bogleheads partial. r/ValueInvesting comments 2014 to 2020-03.
- Metadata for all 45,361 ids with 2+ recommenders. In-session labels for 2,242 candidates (data/labels). Summaries for top 100. Stance reviewed.
- Site in site/, python build.py rebuilds. MORNING_REPORT.md final.
## Resume
- python3 -I scripts/collect_reddit2.py posts <subs>; then comments <subs>. Then python build.py --fetch, python3 -I scripts/new_candidates.py, label in data/labels/batch_NNN.txt, python3 -I scripts/labels_from_tsv.py, python3 -I scripts/rank.py.
