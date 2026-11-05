Live site: https://stockstube.org/

Open the site: `cd ~/stockstube/site && python3 -m http.server 8000` (in this session the folder is `/home/user/hallseat/stockstube/site`)
Then visit http://localhost:8000

# StocksTube: morning report

## What you have

A working static site with **597 investing videos**, each recommended by at least two different people. It has five tabs (For you, Top, Deep cuts, Durable, Longs) plus Saved. You can filter by category, decade, community and length, and search titles, speakers and events, all in the browser. Each video page has a nocookie player, a plain title, "Why people recommend it" (written for all of the top 100), the mentions with links back and any critical ones marked, moments people pointed to, other uploads, and 12 related videos. Watch history stays in localStorage, and For you is built from it. The About page carries a data zip with hashed usernames. `python build.py` rebuilds everything from the cached raw data, and `--fetch` also pulls metadata for new ids.

The main limit: **most of the evidence still comes from Hacker News.** Reddit added link posts from four subreddits. 125 of the 597 entries have at least one Reddit recommender.

## Headline numbers

| | |
|---|---|
| HN comments and stories scanned (every one that links YouTube, 2007 to now) | 410,249 |
| Reddit posts and comments scanned | 4,076 (r/ValueInvesting 2,444 links, r/SecurityAnalysis 1,148, r/investing 103, r/Bogleheads 51) |
| YouTube video links found | 418,634 |
| Unique videos | 265,008 |
| Videos with 2+ distinct recommenders (metadata fetched) | 45,361 |
| Of those, deleted or private | 3,429 |
| Candidates reviewed by hand in session | 2,242 |
| Judged relevant | 625 (11 more rejected as self-promotion or scams) |
| Final entries after merges and the film-clip drop | 597 |
| Duplicate uploads merged / clips attached | 8 (merges.csv) |
| Playlist / channel links counted, not ranked | 9,316 / 15,295 |

Smoke test: Buffett at the University of Florida in 1998 (with a 9-minute part merged in as a clip), Munger's "Psychology of Human Misjudgment" (a second upload merged), Damodaran's valuation sessions and Peter Lynch's 1994 lecture (two uploads merged) all appear. They came from the data, not from hand-picking.

## Top 30

| # | Title | People | Communities | Years |
|---|---|---|---|---|
| 1 | Ray Dalio · How the Economic Machine Works | 113 | 3 | 13 |
| 2 | Dan Olson · Line Goes Up: The Problem With NFTs | 71 | 1 | 4 |
| 3 | Johnny Harris · Why McDonald's ice cream machines break: the Taylor franchise business | 44 | 2 | 5 |
| 4 | Ray Dalio · Principles for Dealing with the Changing World Order | 36 | 2 | 5 |
| 5 | Milton Friedman · I, Pencil | 33 | 1 | 13 |
| 6 | Jim Simons · Numberphile interview | 33 | 1 | 10 |
| 7 | Keynes vs. Hayek rap battle, round one | 23 | 1 | 10 |
| 8 | How airlines became banks: loyalty programs as the profit center | 23 | 1 | 6 |
| 9 | Charlie Munger · The Psychology of Human Misjudgment | 17 | 2 | 10 |
| 10 | Peter Thiel · Competition is for losers · Stanford CS183B | 18 | 2 | 8 |
| 11 | David Graeber · Debt: The First 5,000 Years · Talks at Google | 17 | 1 | 12 |
| 12 | Peter Thiel · The Portal episode 1 with Eric Weinstein | 20 | 1 | 6 |
| 13 | Patrick Boyle · SpaceX and IPO history's biggest money losers | 19 | 2 | 1 |
| 14 | Peter Thiel on Google's $50B cash pile · CNN | 17 | 1 | 6 |
| 15 | Coffeezilla · Exposing Tether | 18 | 1 | 4 |
| 16 | Bill Gurley · 2,851 Miles: regulatory capture · All-In Summit | 18 | 1 | 4 |
| 17 | Keynes vs. Hayek rap battle, round two | 15 | 1 | 8 |
| 18 | Tom Scott · How to slow down a stock exchange | 15 | 1 | 6 |
| 19 | Dan Olson · This Is Financial Advice: meme stocks and GameStop | 17 | 1 | 3 |
| 20 | Quantitative easing explained (animated) | 14 | 1 | 7 |
| 21 | Bill Ackman · Everything you need to know about finance and investing · Big Think | 11 | 3 | 6 |
| 22 | Coffeezilla · Crypto CEO describes a Ponzi scheme | 16 | 1 | 2 |
| 23 | Clayton Christensen · Where does growth come from? · Talks at Google | 11 | 2 | 6 |
| 24 | The Spider's Web: Britain's Second Empire · offshore finance | 12 | 1 | 7 |
| 25 | Chamath Palihapitiya · Money as an instrument of change · Stanford GSB | 13 | 1 | 4 |
| 26 | Scott Galloway · The Four Horsemen: Amazon, Apple, Facebook, Google · DLD | 12 | 2 | 2 |
| 27 | Naval Ravikant · Joe Rogan Experience #1309 | 13 | 1 | 3 |
| 28 | John Oliver · Retirement plans and fees | 10 | 2 | 5 |
| 29 | Steve Jobs · D8 conference, full interview | 10 | 2 | 5 |
| 30 | The South Sea Bubble, part 1 · Extra History | 10 | 1 | 6 |

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
| 8 | Tether's CTO and general counsel interviewed · CNBC | 5 |
| 9 | Odd Lots · Converting office buildings to apartments | 4 |
| 10 | Chris Sacca · Foundation 07 with Kevin Rose | 5 |
| 11 | Webull's Anthony Denier on GameStop restrictions · Benzinga | 5 |
| 12 | Chris Sacca · This Week in Startups #291 | 5 |
| 13 | Benedict Evans · The end of the beginning · a16z | 5 |
| 14 | Michael Green · A new look at active vs. passive | 4 |
| 15 | Marc Cohodes and Keith McCullough · Hedgeye Investing Summit | 4 |
| 16 | Brian Armstrong · Foundation 35 with Kevin Rose | 4 |
| 17 | Asianometry · Hongxin: China's billion-dollar chip failure | 4 |
| 18 | Chris Sacca · Carlson School commencement | 4 |
| 19 | Sam Bankman-Fried's first interview after FTX's collapse | 4 |
| 20 | Alan Greenspan on the government's ability to create money | 4 |

## Ten surprising finds

1. Dalio's 30-minute animation has 113 recommenders. Nothing else is close.
2. Dan Olson's NFT documentary is #2, ahead of every Buffett and Munger video.
3. A video on why McDonald's ice cream machines break (franchise economics) has 44 recommenders.
4. A 1949 water-powered economy computer (MONIAC) has recommenders across 4 different years.
5. A 6-minute CNN clip of Thiel needling Google about its cash pile tops Deep cuts.
6. Keynes vs. Hayek rap battles, rounds one and two, both rank high.
7. Roaring Kitty's 2020 GameStop analysis gets linked as a primary source, not as a meme.
8. Patrick Boyle has more entries than any other channel: 32.
9. The Bank of England's own money-creation explainer has 4 years of recommendations.
10. Peter Schiff's 2006 speech to mortgage bankers survives across 4 years as a "he called it" reference.

## What failed or was skipped

- **Reddit is partial.** Arctic Shift's full-text comment search was throttled all night. Its plain listings work, but return 100 items per call even with `limit=auto`, so r/investing alone would need about 100,000 calls. The URL-prefix post search worked. I finished link posts for r/SecurityAnalysis and r/ValueInvesting, got r/investing and r/Bogleheads partly (5 windows were given up), and didn't reach the other seven subreddits. I didn't collect Reddit comments, apart from r/ValueInvesting 2014 to early 2020. Resume with `python3 -I scripts/collect_reddit2.py posts <subs>`, then `comments <subs>`. It skips cached windows and retries given-up ones.
- **Academic Torrents dumps.** The site sits behind a Cloudflare redirect, and no torrent client is installed here. Skipped.
- **Forums.** Skipped. ValuePickr is Discourse and robots.txt allows `/search`. Its search blurbs strip the video id, though, so each hit needs a `/posts/{id}.json` call: a few hours at 1 request a second.
- **Review coverage.** Every candidate that passed the keyword-and-category prefilter, or had a Reddit mention, was reviewed. HN-only videos that fail the keyword prefilter were not. The McDonald's video surfaced only because a Reddit post pulled it in, so there are probably more like it.

## Main decisions (all in DECISIONS.md)

- I classified in session by reading title, channel and length. I counted as relevant: markets, investing, macro and money, company or business economics, financial history and fraud, and notable investors and operators. I left out general politics, startup advice, tech and pure inequality debate. Film clips and gags are dropped.
- **Stance:** I flagged every mention on a listed video that contains negative words (about 70) and read each one. 3 were critical of the video itself: two on Naval's "How to Get Rich", one on the SBF DealBook interview. Critical mentions don't count toward recommenders and are marked on the page.
- **Self-promotion:** besides the automatic rules (username matches the channel; 3+ videos from one channel), I rejected 11 videos pushed by one or two accounts or showing scam signs.
- Merges need the same speakers, event and year, plus similar titles. Durations must be within 10%, or within 25% when the clean titles are identical (trimmed re-uploads).
- Deep cuts are capped at 250k views. The brief's formula alone reproduced Top.
- No hand edits to the ranking. Every change is a rule or a label, rerun from cache.

## Money and quota

No paid API was called, so spend was $0. The YouTube Data API used 911 of the 10,000 daily units, all on `videos.list`. The key was pasted into chat, so rotate it.

## What needs you

- Publishing and a domain when you want them. The site is static.
- Whether business-economics explainers (airlines, McDonald's, Spotify) belong. They are a sizeable share of the top 50, and a one-line rule removes them.
- Whether one-year news spikes (the 2026 SpaceX IPO videos) should rank lower. The years factor is only +5% a year.

## Next

1. Finish Reddit link posts for the remaining seven subreddits, then comments for the small subreddits.
2. Widen the review to HN-only videos with 5+ recommenders that failed the keyword prefilter.
3. Do ValuePickr through Discourse search plus post fetches.
