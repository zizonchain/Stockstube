"""Arctic Shift per-subreddit collector. Usage: collect_reddit.py SUB.
Monthly windows newest-first, descending pagination, cached per window, 1 req/s, backoff on throttle."""
import httpx, json, os, time, sys, datetime as dt
SUB = sys.argv[1]
RAW = os.path.join(os.path.dirname(__file__), '..', 'data', 'raw', 'reddit', SUB); os.makedirs(RAW, exist_ok=True)
C = httpx.Client(timeout=90, headers={'User-Agent': 'StocksTube-research/0.1 (personal non-commercial index)'})
B = 'https://arctic-shift.photon-reddit.com/api/'
def ts(y, m): return int(dt.datetime(y, m, 1, tzinfo=dt.timezone.utc).timestamp())
def call(ep, params, tries=4):
    for i in range(tries):
        try:
            r = C.get(B + ep, params=params); time.sleep(3)
            if r.status_code == 429: time.sleep(20*(i+1)); continue
            d = r.json()
            if d.get('error'):
                if 'Timeout' in d['error']: time.sleep(20); continue
                raise RuntimeError(d['error'])
            return d['data']
        except (httpx.HTTPError, ValueError): time.sleep(5*(i+1))
    return None
def window(kind, key, val, a, b, fields):
    f = os.path.join(RAW, f'w_{kind}_{key}_{val.replace("/","").replace(":","")}_{a}_{b}.json')
    if os.path.exists(f): return json.load(open(f))
    out, end = [], b
    while True:
        d = call(f'{kind}/search', {'subreddit': SUB, key: val, 'after': a, 'before': end, 'limit': 100, 'fields': fields}, tries=1 if b - a > 86400*40 else 3)
        if d is None:
            if not out and b - a > 86400*40:
                ms = [(y2, m2) for (y2, m2) in months if a <= ts(y2, m2) < b]
                cuts = [ts(y2, m2) for y2, m2 in ms] + [b]
                out = []
                for c0, c1 in zip(cuts, cuts[1:]): out += window(kind, key, val, c0, c1, fields)
                break
            if False:
                m = (a + b)//2; out = window(kind, key, val, a, m, fields) + window(kind, key, val, m, b, fields); break
            open(os.path.join(RAW, 'giveup.log'), 'a').write(f'{kind} {val} {a} {end} got={len(out)}\n'); print('GIVEUP', kind, val, a, end, flush=True); break
        out += d
        if len(d) < 100: break
        end = d[-1]['created_utc']
    json.dump(out, open(f, 'w')); print(SUB, kind, val, dt.datetime.utcfromtimestamp(a).date(), len(out), flush=True); return out
now = dt.datetime.now(dt.timezone.utc)
first = call('comments/search', {'subreddit': SUB, 'after': '2005-06-01', 'limit': 1, 'sort': 'asc', 'fields': 'created_utc'})
fd = dt.datetime.utcfromtimestamp(first[0]['created_utc']) if first else dt.datetime(2008, 1, 1)
print(SUB, 'first comment', fd.date(), flush=True)
months = [(y, m) for y in range(max(fd.year, 2005), now.year+1) for m in range(1, 13) if (fd.year, fd.month) <= (y, m) <= (now.year, now.month)]
CF = 'id,author,body,created_utc,link_id,parent_id,score'
PF = 'id,author,title,url,selftext,created_utc,score'
MODE = sys.argv[2] if len(sys.argv) > 2 else 'comments'
years = sorted({y for y, _ in months})
for y in years:
    a = max(ts(y, 1), ts(*months[0])); b = ts(y+1, 1) if y < now.year else int(time.time())
    if MODE == 'comments':
        for v in ['youtube', 'youtu.be']: window('comments', 'body', v, a, b, CF)
    else:
        for v in ['https://www.youtube.com', 'https://youtu.be', 'https://youtube.com']: window('posts', 'url', v, a, b, PF)
print('DONE', SUB, flush=True)
