"""Raw caches -> data/mentions.parquet, data/links_other.parquet."""
import json, glob, os, datetime as dt, pandas as pd, sys
sys.path.insert(0, os.path.dirname(__file__)); from ytlinks import extract, context
D = os.path.join(os.path.dirname(__file__), '..', 'data')
rows, other = [], []
def add(src, comm, iid, perma, author, created, text, kind, score, title, thread, url_field=None):
    items, norm = extract(text or '')
    if url_field:
        ui, _ = extract(url_field); items = [dict(x, start=0, end=0) for x in ui] + items
    seen = set()
    for it in items:
        key = (it['kind'], it['id'])
        if key in seen: continue
        seen.add(key)
        ctx = context(norm, it['start'], it['end']) if it['end'] else (title or '')[:500]
        base = dict(source=src, community=comm, item_id=str(iid), permalink=perma, author=author or '[deleted]',
                    created=dt.datetime.utcfromtimestamp(int(created)), kind_item=kind, score=score, thread_title=title, thread_id=str(thread), text=ctx)
        if it['kind'] in ('video', 'short'): rows.append(dict(base, video_id=it['id'], t=it['t'], is_short=it['kind'] == 'short'))
        else: other.append(dict(base, link_kind=it['kind'], link_id=it['id']))
for f in glob.glob(f'{D}/raw/hn/*.json'):
    for h in json.load(open(f)):
        if f.split('/')[-1].startswith('comment'):
            add('hn', 'HN', h['objectID'], f"https://news.ycombinator.com/item?id={h['objectID']}", h.get('author'), h['created_at_i'], h.get('comment_text'), 'comment', None, h.get('story_title'), h.get('story_id'))
        else:
            add('hn', 'HN', h['objectID'], f"https://news.ycombinator.com/item?id={h['objectID']}", h.get('author'), h['created_at_i'], h.get('story_text'), 'post', h.get('points'), h.get('title'), h['objectID'], h.get('url'))
import gzip  # Reddit comes from the committed compact extract (scripts/compact_reddit.py), authors hashed
for f in glob.glob(f'{D}/reddit_extract/*.jsonl.gz'):
    sub = os.path.basename(f)[:-len('.jsonl.gz')]
    for l in gzip.open(f, 'rt'):
        h = json.loads(l)
        if h['k'] == 'p':
            add('reddit', f'r/{sub}', h['id'], f"https://www.reddit.com/r/{sub}/comments/{h['id']}/", h['a'], h['t'], h.get('x'), 'post', h.get('s'), h.get('ti'), h['id'], h.get('u'))
        else:
            add('reddit', f'r/{sub}', h['id'], f"https://www.reddit.com/r/{sub}/comments/{h['l']}/_/{h['id']}/", h['a'], h['t'], h.get('x'), 'comment', h.get('s'), None, h['l'])
m = pd.DataFrame(rows).drop_duplicates(['source', 'item_id', 'video_id'])
m.to_parquet(f'{D}/mentions.parquet'); pd.DataFrame(other).drop_duplicates(['source','item_id','link_id']).to_parquet(f'{D}/links_other.parquet')
print('mentions', len(m), 'videos', m.video_id.nunique(), 'other', len(other)); print(m.groupby('community').size().sort_values().tail(20))
