"""Editorial layer: data/labels/curated.json -> site/data/curated.json (+ video pages for picks the data never found).
Curated videos are labelled 'Editor's pick' on the site and never enter the ranked tabs."""
import json, os, re, httpx
H = os.path.dirname(os.path.abspath(__file__)); D = f'{H}/../data'; S = f'{H}/../site/data'
cur = json.load(open(f'{D}/labels/curated.json'))
idx = {x['i']: x for x in json.load(open(f'{S}/all.json'))}
ids = set(cur['legends']) | {p['i'] for p in cur['picks']} | {v[0] for pl in cur['playlists'] for v in pl['videos']}
cache_f = f'{D}/raw/extra_meta.json'; cache = json.load(open(cache_f)) if os.path.exists(cache_f) else {}
need = [i for i in ids if i not in idx and i not in cache]
key = next((l.split('=', 1)[1].strip() for l in open(f'{H}/../.env') if l.startswith('YOUTUBE_API_KEY=')), '')
for k in range(0, len(need), 50):
    r = httpx.get('https://www.googleapis.com/youtube/v3/videos', params={'part': 'snippet,contentDetails,statistics,status', 'id': ','.join(need[k:k + 50]), 'key': key}, timeout=60).json()
    for it in r.get('items', []): cache[it['id']] = it
json.dump(cache, open(cache_f, 'w'))
def dur(x):
    m = re.match(r'P(?:(\d+)D)?T?(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', x or ''); d, h, mi, s = (int(g or 0) for g in m.groups()) if m else (0, 0, 0, 0)
    return d * 86400 + h * 3600 + mi * 60 + s
titles = {p['i']: p for p in cur['picks']}
for pl in cur['playlists']:
    for v in pl['videos']:
        if len(v) > 1: titles.setdefault(v[0], {'t': v[1]})
def entry(i):
    if i in idx: return dict(idx[i])
    it = cache.get(i)
    if not it: return None  # deleted or private: drop
    sn, st = it['snippet'], it.get('statistics', {}); p = titles.get(i, {})
    e = dict(i=i, t=p.get('t') or sn['title'], d=dur(it['contentDetails'].get('duration')), c=p.get('c', 'Interview or conversation'), v=int(st.get('viewCount', 0) or 0),
             u=int(sn['publishedAt'][:4]), ch=sn.get('channelTitle'), ep=1)
    vf = f'{S}/v/{i}.json'
    if not os.path.exists(vf) or json.load(open(vf)).get('ep'):
        json.dump(dict(e, ot=sn['title'], up=sn['publishedAt'][:10], embed=it.get('status', {}).get('embeddable', True), why=p.get('why'), mentions=[], critical=0, related=[]),
                  open(vf, 'w'), separators=(',', ':'))
    return e
def mark(e, i):
    if e is not None and i in titles and titles[i].get('why'): e['why'] = titles[i]['why']
    return e
out = dict(legends=[e for e in map(entry, cur['legends']) if e],
           picks=[dict(e, ep=1) for p in cur['picks'] for e in [mark(entry(p['i']), p['i'])] if e],
           playlists=[dict(id=pl['id'], title=pl['title'], note=pl['note'], items=[e for e in (entry(v[0]) for v in pl['videos']) if e]) for pl in cur['playlists']])
json.dump(out, open(f'{S}/curated.json', 'w'), separators=(',', ':'))
missing = [i for i in ids if i not in idx and i not in cache]
print('curated: legends', len(out['legends']), 'picks', len(out['picks']), 'playlists', [(p['id'], len(p['items'])) for p in out['playlists']], 'unavailable', missing)
