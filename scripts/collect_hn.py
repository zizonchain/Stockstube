"""HN comments+stories mentioning YouTube via Algolia, adaptive time windows. Resumable: caches each window."""
import httpx, json, os, time, sys
RAW = os.path.join(os.path.dirname(__file__), '..', 'data', 'raw', 'hn'); os.makedirs(RAW, exist_ok=True)
C = httpx.Client(timeout=60, headers={'User-Agent': 'StocksTube-research/0.1 (personal non-commercial index)'})
START, END = 1167609600, int(time.time())
def get(q, tag, a, b, page=0):
    for i in range(6):
        try:
            r = C.get('https://hn.algolia.com/api/v1/search_by_date', params=dict(query=q, tags=tag, hitsPerPage=1000, page=page,
                numericFilters=f'created_at_i>={a},created_at_i<{b}', attributesToRetrieve='comment_text,story_text,url,title,author,created_at_i,story_id,story_title,objectID,points'))
            if r.status_code == 429: time.sleep(30*(i+1)); continue
            r.raise_for_status(); return r.json()
        except httpx.HTTPError: time.sleep(5*(i+1))
    raise RuntimeError('failed')
def run(q, tag):
    stack = [(START, END)]
    while stack:
        a, b = stack.pop()
        f = os.path.join(RAW, f'{tag}_{q}_{a}_{b}.json')
        if os.path.exists(f): continue
        d = get(q, tag, a, b)
        if d['nbHits'] > 1000 and b - a > 3600:
            m = (a + b) // 2; stack += [(a, m), (m, b)]; continue
        json.dump(d['hits'], open(f, 'w')); time.sleep(0.3)
        print(tag, q, a, len(d['hits']), flush=True)
for q in ['youtube.com', 'youtu.be']:
    for tag in ['comment', 'story']: run(q, tag)
print('DONE')
