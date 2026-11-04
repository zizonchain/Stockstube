"""Arctic Shift collector, third version: adaptive windows, fully resumable.
Usage: collect_reddit3.py comments|posts SUB [SUB...]

Throttle handling (learned from v1/v2):
  - fast "Timeout. Maybe slow down a bit" (<6 s) = per-client budget spent: sleep x-ratelimit-reset, retry the same query
  - slow one (>=6 s) = the query is too heavy for the server: split the window in half, down to one day;
    a one-day window that is still heavy is retried 3 times with long sleeps, then logged and left uncached
Comments: body search for "youtube" and "youtu.be". Posts: url-prefix search.
Every completed window is cached in data/raw/reddit/<SUB>/v3_*.json and never refetched."""
import httpx, json, os, sys, time, datetime as dt
MODE, SUBS = sys.argv[1], sys.argv[2:]
C = httpx.Client(timeout=120, headers={'User-Agent': 'StocksTube-research/0.1 (personal non-commercial index; slow polite crawler)'})
API = 'https://arctic-shift.photon-reddit.com/api/'
PACE, DAY = 5, 86400
END = 1793750400  # 2026-11-04 00:00 UTC, fixed so cache names stay stable
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data', 'raw', 'reddit')
YEARLY = {'econmonitor', 'SecurityAnalysis', 'quant', 'finance'}  # under ~1M comments
FIELDS = {'comments': 'id,author,body,created_utc,link_id,parent_id,score', 'posts': 'id,author,title,url,selftext,created_utc,score'}
def log(*a): print(dt.datetime.utcnow().strftime('%H:%M:%S'), *a, flush=True)

def call(ep, params):
    """list of items, or 'HEAVY' if the server timed out on the query itself."""
    for i in range(30):
        t = time.time()
        try: r = C.get(API + ep, params=params)
        except httpx.HTTPError: time.sleep(30); continue
        took = time.time() - t
        reset = int(r.headers.get('x-ratelimit-reset', '30') or 30)
        if r.status_code == 429: time.sleep(reset + 5); continue
        try: d = r.json()
        except ValueError: time.sleep(30); continue
        if d.get('error'):
            if 'Timeout' in d['error'] and took >= 6: time.sleep(PACE); return 'HEAVY'
            if 'Timeout' in d['error']: time.sleep(reset + 3); continue
            log('ERR', d['error']); return []
        time.sleep(PACE)
        return d['data'] or []
    return 'HEAVY'

def window(raw, sub, kind, key, val, a, b, stats):
    f = os.path.join(raw, f'v3_{kind}_{key}_{val.replace("/", "").replace(":", "")}_{a}_{b}.json')
    if os.path.exists(f): stats['cached'] += 1; return True
    out, end, tries = [], b, 0
    while True:
        d = call(f'{kind}/search', {'subreddit': sub, key: val, 'after': a, 'before': end, 'limit': 100, 'fields': FIELDS[kind]})
        if d == 'HEAVY':
            if end - a > DAY:  # split what is left of this window
                m = (a + end) // 2
                ok = window(raw, sub, kind, key, val, a, m, stats) & window(raw, sub, kind, key, val, m, end, stats)
                if not ok: return False  # leave parent uncached so a rerun retries the gap
                break
            tries += 1
            if tries <= 3: time.sleep(60 * tries); continue
            open(os.path.join(raw, 'giveup_v3.log'), 'a').write(f'{kind} {val} {a} {end}\n'); stats['giveup'] += 1
            return False
        out += d
        if len(d) < 100: break
        end = d[-1]['created_utc']
    json.dump(out, open(f, 'w')); stats['windows'] += 1; stats['items'] += len(out)
    return True

def start(sub):
    d = call('comments/search', {'subreddit': sub, 'after': '2005-06-01', 'limit': 1, 'sort': 'asc', 'fields': 'created_utc'})
    return d[0]['created_utc'] if isinstance(d, list) and d else 1136073600

for sub in SUBS:
    raw = os.path.join(ROOT, sub); os.makedirs(raw, exist_ok=True)
    stats = dict(windows=0, cached=0, items=0, giveup=0)
    first = start(sub)
    vals = ['youtube', 'youtu.be'] if MODE == 'comments' else ['https://www.youtube.com', 'https://youtu.be']
    key = 'body' if MODE == 'comments' else 'url'
    y0 = dt.datetime.utcfromtimestamp(first).year
    months = [1] if sub in YEARLY else range(12, 0, -1)  # small subs start with year windows; splitting adapts
    for y in range(2026, y0 - 1, -1):  # newest first: a cut-off run keeps recent years
        for mth in months:
            a = max(first - 1, int(dt.datetime(y, mth, 1, tzinfo=dt.timezone.utc).timestamp()))
            nxt = (y + 1, 1) if sub in YEARLY else (y + (mth == 12), mth % 12 + 1)
            b = min(END, int(dt.datetime(*nxt, 1, tzinfo=dt.timezone.utc).timestamp()))
            if a >= b: continue
            for v in vals: window(raw, sub, MODE, key, v, a, b, stats)
        log(sub, MODE, y, stats)
    log('DONE', MODE, sub, stats)
