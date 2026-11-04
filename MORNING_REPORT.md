Open the site: `cd ~/stockstube/site && python3 -m http.server 8000` (in this session the folder is `/home/user/hallseat/stockstube/site`)
Then visit http://localhost:8000

# StocksTube: morning report

## What you have

A working static site with 499 investing videos, each recommended by at least two different people. It has five tabs (For you, Top, Deep cuts, Durable, Longs) plus Saved. You can filter by category, decade, community and length, and search titles, speakers and events, all in the browser. Each video page has a nocookie player, a plain title, the mentions with links back, "moments" where people linked a timestamp, other uploads, and 12 related videos. Watch history stays in localStorage, and For you is built from it. The About page carries a data zip with hashed usernames.

`python build.py` rebuilds everything from the cached raw data. Add `--fetch` to also pull metadata for new video ids.

The biggest gap: **almost all of the data is from Hacker News.** Reddit through Arctic Shift barely worked tonight (details below), so the list reads like "what HN's finance-minded readers recommend", not yet "what investing communities recommend".

## Headline numbers

| | |
|---|---|
| HN comments and stories scanned (all that link YouTube, 2007 to now) | 410,249 |
| Reddit comments and posts scanned | 577 |
| YouTube video links found (mentions) | 414,933 |
| Unique videos | 261,903 |
| Videos with 2+ distinct recommenders (metadata fetched) | 45,206 |
| Of those, deleted or private | 3,407 |
| Candidates reviewed by hand in session (title, channel, length) | 2,096 |
| Judged relevant | 519 |
| Final entries after merges and the "Other" drop | 499 |
| Duplicate uploads merged / clips attached | see merges.csv (6) |
| Playlist / channel links counted, not ranked | 9,305 / 15,285 |

Smoke test: Buffett at the University of Florida in 1998, Munger's "Psychology of Human Misjudgment" and Damodaran's valuation sessions all appear, found by the pipeline and not added by hand. The Munger talk has a second upload merged into it, and a 9-minute part of the Buffett talk is attached to the full version as a clip.

## Top 30

| # | Title | People | Communities | Years |
|---|---|---|---|---|
| 1 | Ray Dalio · How the Economic Machine Works | 111 | 2 | 13 |
| 2 | Dan Olson · Line Goes Up: The Problem With NFTs | 71 | 1 | 4 |
| 3 | Milton Friedman · I, Pencil | 33 | 1 | 13 |
| 4 | Jim Simons · Numberphile interview | 33 | 1 | 10 |
| 5 | Ray Dalio · Principles for Dealing with the Changing World Order | 35 | 1 | 5 |
| 6 | Keynes vs. Hayek rap battle, round one | 23 | 1 | 10 |
| 7 | How airlines became banks: loyalty programs as the profit center | 23 | 1 | 6 |
| 8 | Charlie Munger · The Psychology of Human Misjudgment | 16 | 2 | 10 |
| 9 | David Graeber · Debt: The First 5,000 Years · Talks at Google | 17 | 1 | 12 |
| 10 | Peter Thiel · The Portal episode 1 with Eric Weinstein | 20 | 1 | 6 |
| 11 | Peter Thiel on Google's $50B cash pile · CNN | 17 | 1 | 6 |
| 12 | Bill Gurley · 2,851 Miles: regulatory capture · All-In Summit | 18 | 1 | 4 |
| 13 | Coffeezilla · Exposing Tether | 18 | 1 | 4 |
| 14 | Keynes vs. Hayek rap battle, round two | 15 | 1 | 8 |
| 15 | Tom Scott · How to slow down a stock exchange | 15 | 1 | 6 |
| 16 | Dan Olson · This Is Financial Advice: meme stocks and GameStop | 17 | 1 | 3 |
| 17 | Patrick Boyle · SpaceX and IPO history's biggest money losers | 18 | 1 | 1 |
| 18 | Coffeezilla · Crypto CEO describes a Ponzi scheme | 16 | 1 | 2 |
| 19 | The Spider's Web: Britain's Second Empire · offshore finance | 12 | 1 | 7 |
| 20 | Chamath Palihapitiya · Money as an instrument of change · Stanford GSB | 13 | 1 | 4 |
| 21 | Naval Ravikant · Joe Rogan Experience #1309 | 13 | 1 | 3 |
| 22 | The South Sea Bubble, part 1 · Extra History | 10 | 1 | 6 |
| 23 | Thomas Peterffy on market integrity after GameStop · CNBC | 12 | 1 | 1 |
| 24 | Chamath Palihapitiya on venture capital as a Ponzi scheme | 10 | 1 | 4 |
| 25 | Patrick Boyle · The SpaceX IPO scandal | 11 | 1 | 1 |
| 26 | Ben Felix · Renting vs. buying a home: the 5% rule | 9 | 1 | 5 |
| 27 | John Oliver · Retirement plans and fees | 9 | 1 | 5 |
| 28 | Benn Jordan · Why Spotify will ultimately fail | 10 | 1 | 2 |
| 29 | The housing crisis is the everything crisis | 9 | 1 | 4 |
| 30 | Bill Ackman · Everything you need to know about finance and investing · Big Think | 8 | 1 | 5 |

**Top 20 deep cuts** (3+ people, under 250k views, ranked by people / log10(views))

| # | Title | People |
|---|---|---|
| 1 | Peter Thiel on Google's $50B cash pile · CNN | 17 |
| 2 | Peter Thiel and Marc Andreessen debate · Milken Institute | 8 |
| 3 | The MONIAC hydraulic economy computer · Reserve Bank of New Zealand | 8 |
| 4 | Chamath Palihapitiya on rebuilding Social Capital · This Week in Startups | 8 |
| 5 | Ben Felix · Why bad economic news doesn't always hurt stocks | 8 |
| 6 | Sam Bankman-Fried and Matt Levine on making money in crypto · Odd Lots | 6 |
| 7 | Stuart Kirk · Why investors shouldn't fear climate risk · FT Moral Money | 6 |
| 8 | Odd Lots · Converting office buildings to apartments | 4 |
| 9 | Chris Sacca · Foundation 07 with Kevin Rose | 5 |
| 10 | Webull's Anthony Denier on GameStop restrictions · Benzinga | 5 |
| 11 | Chris Sacca · This Week in Startups #291 | 5 |
| 12 | Michael Green · A new look at active vs. passive | 4 |
| 13 | Marc Cohodes and Keith McCullough · Hedgeye Investing Summit | 4 |
| 14 | Brian Armstrong · Foundation 35 with Kevin Rose | 4 |
| 15 | Tether's CTO and general counsel interviewed · CNBC | 4 |
| 16 | Chris Sacca · Carlson School commencement | 4 |
| 17 | Sam Bankman-Fried's first interview after FTX's collapse | 4 |
| 18 | Alan Greenspan on the government's ability to create money | 4 |
| 19 | Julien Garran · the AI bubble · MacroStrategy Partnership | 3 |
| 20 | Charlie Munger · USC Law commencement, part 1 | 4 |

## Ten surprising finds

1. Dalio's 30-minute animation has 110 HN recommenders. Nothing else is close.
2. Dan Olson's NFT documentary is #2, ahead of every Buffett and Munger video.
3. A 1949 water-powered economy computer (MONIAC) has recommenders across 4 different years.
4. A 6-minute CNN clip of Thiel needling Eric Schmidt about Google's cash is the top deep cut.
5. Keynes vs. Hayek rap battles, rounds one and two, both make the top 20.
6. Roaring Kitty's 2020 GameStop analysis gets linked as a primary source, not as a meme.
7. Wendover's airline loyalty-program video beats every valuation lecture.
8. Patrick Boyle has more entries than any other channel: 31.
9. Bank of England's own money-creation explainer has 4 years of recommendations.
10. Peter Schiff's 2006 mortgage bankers speech survives as a "he called it" reference across 4 years.

## What failed or was skipped

- **Reddit (Arctic Shift).** Full-text search answered most requests with "Timeout. Maybe slow down a bit", even at one request every 3 to 4 seconds with backoff. Year windows mostly failed and fell back to months, at about a minute each. In about 4 hours it covered only r/ValueInvesting comments from March 2014 to March 2020 (377 items, 45 YouTube links). No other subreddit was reached, and no link posts. The collector is resumable and still has everything queued: `scripts/run_reddit.sh comments <subs...>` and then `posts`. Gaps are in `data/raw/reddit/*/giveup.log`.
- **Forums.** Skipped. ValuePickr is Discourse, and robots.txt allows `/search`. Its search blurbs strip the video id, though, so each hit needs a `/posts/{id}.json` call. At 1 request a second that is a few hours for a full pass. Bogleheads (phpBB) needs a robots and terms check first. I didn't look at Corner of Berkshire & Fairfax or the Motley Fool boards.
- **Critical stance per excerpt.** Not classified. Every mention counts as a recommendation, so the critical count on video pages is 0 for now.
- **Self-promotion.** The fuzzy username-to-channel rule and the "3+ videos from one channel" rule run, but HN rarely triggers either. They matter once Reddit data arrives.
- **"Why people recommend it".** Written for the top 30 only.

## Main decisions (all in DECISIONS.md)

- Classification was done in-session as reading, not through an API. A rule prefilter (keywords plus YouTube category) picked 2,096 candidates from 45,206 videos with 2+ recommenders. I reviewed every candidate's title, channel and length and wrote labels to `data/labels/`. Unlabelled videos only show if a rule matches **and** an investing subreddit recommends them.
- I counted as relevant: markets, investing, macro and money, company or business economics, financial history and fraud, and notable investors and operators. I left out general politics, startup advice, tech and pure inequality debate.
- I dropped film clips and gags (the "Other" category) from the site.
- Deep cuts are capped at 250k views. The brief's formula alone just reproduced Top.
- Merges need the same speakers, event and year **and** similar titles. Without the title check, two All-In episodes were merged by mistake.
- No hand edits to the ranking. Every change is a rule, rerun from cache.

## Money and quota

No paid API was called, so spend was $0. The YouTube Data API used about 906 units of the 10,000 daily units, all on `videos.list`. The key was pasted into chat, so rotate it.

## What needs you

- **Pushing.** The session's permission check refused `git push` to `zizonchain/stockstube`, so all commits are local in this container. Push them before the container is reclaimed.
- Publishing and a domain when you want them. The site is static and drops onto any host.
- Whether "business economics" explainers (airlines, Spotify, McDonald's) belong. They are about a quarter of the list. A one-line rule change removes them.
- Whether one-year news spikes (the 2026 SpaceX IPO videos) should rank lower. Right now the years factor is only +5% a year.

## Next

1. Finish Reddit. Either run the queued collector for a day, or use the Academic Torrents per-subreddit dumps and scan them locally, which avoids the API entirely.
2. Write labels for the new Reddit candidates in the same batch format, then add per-mention stance so critical links stop counting.
3. Do ValuePickr through Discourse search plus post fetches at 1 request a second.
4. Write recommendation summaries beyond the top 30.
