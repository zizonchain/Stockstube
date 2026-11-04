"""Arctic Shift collector, second version. Usage: collect_reddit2.py posts|comments SUB [SUB...]

Arctic Shift answers "Timeout. Maybe slow down a bit" in two different situations:
  - fast (<3 s): the per-client budget for the current window is spent -> wait for x-ratelimit-reset, retry same query
  - slow (>=8 s): the query itself is too heavy -> split the time window in half
Posts use the indexed url-prefix filter over the whole history; comments use body search in yearly windows.
Every finished window is cached in data/raw/reddit/<SUB>/v2_*.json and never refetched."""
import httpx, json, os, sys, time, datetime as dt
MODE, SUBS = sys.argv[1], sys.argv[2:]
C = httpx.Client(timeout=120, headers={'User-Agent': 'StocksTube-research/0.1 (personal non-commercial index; slow polite crawler)'})
B = 'https://arctic-shift.photon-reddit.com/api/'
PACE = 6  # seconds between requests, well under observed limits
def call(ep, params):
    """Returns list, or 'HEAVY' when the query itself timed out."""
    for i in range(12):
        t = time.time()
        try: r = C.get(B + ep, params=params)
        except httpx.HTTPError: time.sleep(20); continue
        took = time.time() - t
        if os.environ.get('VERBOSE'): print('  call', ep, params.get(next(iter(k for k in params if k in ('url','body'))), ''), params['after'], params['before'], r.status_code, round(took, 1), r.text[:60].replace('\n', ' '), flush=True)
        reset = int(r.headers.get('x-ratelimit-reset', '30') or 30)
        if r.status_code == 429: time.sleep(reset + 5); continue
        try: d = r.json()
        except ValueError: time.sleep(20); continue
        if d.get('error'):
            if 'Timeout' in d['error'] and took >= 7: time.sleep(PACE * 2); return 'HEAVY'
            if 'Timeout' in d['error']: time.sleep(reset + 3); continue
            print('ERR', d['error'], flush=True); return []
        time.sleep(PACE)
        return d['data'] or []
    return 'HEAVY'
def window(raw, sub, kind, key, val, a, b, fields, depth=0):
    f = os.path.join(raw, f'v2_{kind}_{key}_{val.replace("/", "").replace(":", "")}_{a}_{b}.json')
    if os.path.exists(f): return
    out, end = [], b
    while True:
        d = call(f'{kind}/search', {'subreddit': sub, key: val, 'after': a, 'before': end, 'limit': 100, 'fields': fields})
        if d == 'HEAVY':
            if b - a > 86400 * 4 and depth < int(os.environ.get("MAXDEPTH", 5)):
                m = (a + end) // 2
                window(raw, sub, kind, key, val, a, m, fields, depth + 1); window(raw, sub, kind, key, val, m, end, fields, depth + 1)
                break
            open(os.path.join(raw, 'giveup_v2.log'), 'a').write(f'{kind} {val} {a} {end}\n'); break
        out += d
        if len(d) < 100: break
        end = d[-1]['created_utc']
    json.dump(out, open(f, 'w'))
    print(sub, kind, val, dt.datetime.utcfromtimestamp(a).date(), dt.datetime.utcfromtimestamp(b).date(), len(out), flush=True)
now = 1793750400  # fixed end (2026-11-04 00:00 UTC) so window cache names are stable across restarts
for sub in SUBS:
    raw = os.path.join(os.path.dirname(__file__), '..', 'data', 'raw', 'reddit', sub); os.makedirs(raw, exist_ok=True)
    if MODE == 'posts':
        for v in ['https://www.youtube.com', 'https://youtu.be', 'https://youtube.com', 'https://m.youtube.com']:
            window(raw, sub, 'posts', 'url', v, 1136073600, now, 'id,author,title,url,selftext,created_utc,score')
    else:
        for y in range(2026, 2007, -1):
            a = int(dt.datetime(y, 1, 1, tzinfo=dt.timezone.utc).timestamp()); b = min(now, int(dt.datetime(y + 1, 1, 1, tzinfo=dt.timezone.utc).timestamp()))
            for v in ['youtube', 'youtu.be']:
                window(raw, sub, 'comments', 'body', v, a, b, 'id,author,body,created_utc,link_id,parent_id,score')
    print('DONE', MODE, sub, flush=True)
