# DECISIONS
- HackerTube zip holds only the 6,454 kept videos and caps mentions at 20/video, so it is not a full HN YouTube census. Used Algolia for HN instead; zip kept in data/raw/hackertube for reference only.
- HN via Algolia search_by_date with queries "youtube.com" and "youtu.be", comments and stories, windows halved until under the 1,000-hit cap.
- Arctic Shift full-text search throttles bursts with a fake "Timeout" error. Collector uses yearly windows, 1 req/s, backs off 15/30/45/60s, splits a window only after that. Newest years first so a cut-off run keeps recent data.
- Reddit comment thread titles are not in the comment record; left null for comments (posts carry titles). Cost of a lookup per thread was not worth it tonight.
- Thumbnail: hq2.jpg (YouTube's 50% still; hq1/hq3 are 25%/75%). Checked it exists on sample ids; site falls back to hqdefault.jpg on error.
- Recommender = distinct (source, author). AutoModerator and [deleted] dropped from counting entirely (simpler than once-per-thread; [deleted] is rare in these API pulls).
