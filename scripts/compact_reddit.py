"""Raw Reddit caches -> data/reddit_extract/<SUB>.jsonl.gz (committed) + windows_done.txt.
Keeps only what the brief allows: id, permalink parts, hashed author, date, community, score,
thread title, and the text around each YouTube link (not full comments). Merges with what is
already in the extract, so a run on a fresh machine (GitHub Actions) only adds."""
import glob, gzip, hashlib, json, os, sys
sys.path.insert(0, os.path.dirname(__file__)); from ytlinks import extract, context
D = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data')
OUT = f'{D}/reddit_extract'; os.makedirs(OUT, exist_ok=True)
KEEP = {'AutoModerator', '[deleted]', '[removed]', None, ''}
def who(a): return a if a in KEEP else 'h_' + hashlib.sha256(a.encode()).hexdigest()[:16]
def snip(text, url=''):
    items, norm = extract(text or '')
    parts = [context(norm, it['start'], it['end']) for it in items if it['end']][:4]
    return ' … '.join(dict.fromkeys(parts))[:1600]
done = set(open(f'{OUT}/windows_done.txt').read().split()) if os.path.exists(f'{OUT}/windows_done.txt') else set()
for sub_dir in sorted(glob.glob(f'{D}/raw/reddit/*/')):
    sub = sub_dir.rstrip('/').split('/')[-1]
    path = f'{OUT}/{sub}.jsonl.gz'
    rows = {}
    if os.path.exists(path):
        for l in gzip.open(path, 'rt'): r = json.loads(l); rows[(r['k'], r['id'])] = r
    for f in glob.glob(f'{sub_dir}[wv]*_*.json'):
        post = '_posts_' in '_' + os.path.basename(f)
        for h in json.load(open(f)):
            if post:
                url = h.get('url') or ''
                if not extract(url)[0] and not extract(h.get('selftext') or '')[0]: continue
                r = dict(k='p', id=h['id'], a=who(h.get('author')), t=h['created_utc'], s=h.get('score'), ti=(h.get('title') or '')[:300], u=url[:300], x=snip(h.get('selftext')))
            else:
                x = snip(h.get('body'))
                if not x: continue
                r = dict(k='c', id=h['id'], a=who(h.get('author')), t=h['created_utc'], s=h.get('score'), l=(h.get('link_id') or '').replace('t3_', ''), x=x)
            rows[(r['k'], r['id'])] = r
        if os.path.basename(f).startswith('v3_'): done.add(f'{sub}/{os.path.basename(f)}')
    with gzip.open(path, 'wt') as g:
        for r in sorted(rows.values(), key=lambda r: (r['t'], r['id'])): g.write(json.dumps(r, separators=(',', ':')) + '\n')
    print(sub, len(rows))
open(f'{OUT}/windows_done.txt', 'w').write('\n'.join(sorted(done)) + '\n')
