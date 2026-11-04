"""List unlabelled videos with 2+ recommenders and at least one Reddit/forum mention, for in-session labelling."""
import pandas as pd, json, glob, os
D = os.path.join(os.path.dirname(__file__), '..', 'data')
V = pd.read_parquet(f'{D}/videos.parquet').set_index('video_id')
lab = set()
for f in glob.glob(f'{D}/labels/*.jsonl'):
    for l in open(f): j = json.loads(l); lab.add(j['id']) if 'relevant' in j else None
m = pd.read_parquet(f'{D}/mentions.parquet'); r = set(m[m.source != 'hn'].video_id)
c = V[~V.index.isin(lab) & V.index.isin(r) & (V.recs >= 2) & (V.duration > 60)].sort_values('recs', ascending=False)
for i, x in c.iterrows(): print(f"{i}|{x.recs}|{int(x.duration)//60}m|{str(x.channel)[:20]}|{str(x.title)[:80]}")
