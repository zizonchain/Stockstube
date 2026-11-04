"""YouTube videos.list for video ids (priority: >=2 distinct recommenders). Cached per batch."""
import httpx, json, os, glob, pandas as pd, time
D = os.path.join(os.path.dirname(__file__), '..', 'data'); RAW = f'{D}/raw/youtube'; os.makedirs(RAW, exist_ok=True)
KEY = [l.split('=',1)[1].strip() for l in open(os.path.join(D, '..', '.env')) if l.startswith('YOUTUBE_API_KEY')][0]
m = pd.read_parquet(f'{D}/mentions.parquet')
m = m[~m.author.str.lower().isin(['automoderator','[deleted]'])]
m = m.assign(who=m.source + ':' + m.author); n = m.groupby('video_id').who.nunique()
MIN = int(os.environ.get('MIN_RECS', 2))
ids = sorted(n[n >= MIN].index, key=lambda v: -n[v])
done = set()
for f in glob.glob(f'{RAW}/*.json'): done |= set(json.load(open(f))['requested'])
todo = [i for i in ids if i not in done]; print('need', len(todo), 'of', len(ids))
C = httpx.Client(timeout=30); calls = 0
for k in range(0, len(todo), 50):
    b = todo[k:k+50]
    r = C.get('https://www.googleapis.com/youtube/v3/videos', params=dict(part='snippet,contentDetails,statistics,status', id=','.join(b), key=KEY, maxResults=50))
    if r.status_code != 200: print('ERR', r.status_code, r.text[:200].replace(KEY,'***')); break
    json.dump(dict(requested=b, items=r.json().get('items', [])), open(f'{RAW}/{int(time.time()*1000)}.json', 'w')); calls += 1
print('calls', calls)
