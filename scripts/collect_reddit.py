"""Arctic Shift per-subreddit collector. Usage: collect_reddit.py SUB. Caches per window; splits windows on timeout."""
import httpx, json, os, time, sys, datetime as dt
SUB = sys.argv[1]
RAW = os.path.join(os.path.dirname(__file__), '..', 'data', 'raw', 'reddit', SUB); os.makedirs(RAW, exist_ok=True)
C = httpx.Client(timeout=90, headers={'User-Agent': 'StocksTube-research/0.1 (personal non-commercial index)'})
B = 'https://arctic-shift.photon-reddit.com/api/'
def ts(y, m): return int(dt.datetime(y, m, 1, tzinfo=dt.timezone.utc).timestamp())
def call(ep, params):
    for i in range(6):
        try:
            r = C.get(B + ep, params=params)
            if r.status_code == 429: time.sleep(20*(i+1)); continue
            d = r.json()
            if d.get('error'):
                if 'Timeout' in d['error']: return 'TIMEOUT'
                raise RuntimeError(d['error'])
            return d['data']
        except (httpx.HTTPError, ValueError): time.sleep(5*(i+1))
    return 'TIMEOUT'
def window(kind, key, val, a, b, fields):
    f = os.path.join(RAW, f'{kind}_{key}_{val.replace("/","").replace(":","")}_{a}_{b}.json')
    if os.path.exists(f): return
    out, cur = [], a
    while True:
        d = call(f'{kind}/search', {'subreddit': SUB, key: val, 'after': cur, 'before': b, 'limit': 100, 'sort': 'asc', 'fields': fields})
        time.sleep(1)
        tries = 0
        while d == 'TIMEOUT' and tries < 4:
            tries += 1; time.sleep(15*tries)
            d = call(f'{kind}/search', {'subreddit': SUB, key: val, 'after': cur, 'before': b, 'limit': 100, 'sort': 'asc', 'fields': fields})
        if d == 'TIMEOUT':
            if b - cur > 86400*20:
                m = (cur + b)//2; window(kind, key, val, cur, m, fields); window(kind, key, val, m, b, fields)
                for g in (f'{kind}_{key}_{val.replace("/","").replace(":","")}_{cur}_{m}.json', f'{kind}_{key}_{val.replace("/","").replace(":","")}_{m}_{b}.json'):
                    p = os.path.join(RAW, g)
                    if os.path.exists(p): out += json.load(open(p))
                break
            print('GIVEUP', kind, val, cur, b, flush=True); open(os.path.join(RAW, 'giveup.log'), 'a').write(f'{kind} {val} {cur} {b}\n'); break
        out += d
        if len(d) < 100: break
        cur = d[-1]['created_utc']
    json.dump(out, open(f, 'w')); print(SUB, kind, val, a, len(out), flush=True)
now = dt.datetime.utcnow()
months = [(y, m) for y in range(2008, now.year+1) for m in range(1, 13) if (y, m) <= (now.year, now.month)]
CF = 'id,author,body,created_utc,link_id,parent_id,score'
PF = 'id,author,title,url,selftext,created_utc,score'
for y in range(now.year, 2007, -1):
    a, b = ts(y, 1), ts(y+1, 1) if y < now.year else int(time.time())
    for v in ['youtube', 'youtu.be']: window('comments', 'body', v, a, b, CF)
    for v in ['https://www.youtube.com', 'https://youtu.be', 'https://youtube.com', 'https://m.youtube.com']: window('posts', 'url', v, a, b, PF)
    window('posts', 'selftext', 'youtube', a, b, PF)
print('DONE', SUB, flush=True)
