"""mentions + YouTube metadata + labels -> data/videos.parquet, data/ranked.json, site/data/*."""
import json, glob, os, re, math, hashlib, zipfile, io, datetime as dt, collections
import pandas as pd
from rapidfuzz import fuzz
R = os.path.join(os.path.dirname(__file__), '..'); D = f'{R}/data'; S = f'{R}/site/data'
os.makedirs(f'{S}/v', exist_ok=True)
BOTS = {'automoderator', '[deleted]', 'remindmebot', 'savevideo', 'savevideobot', 'youtubot', 'video_descriptionbot', 'timestamp_bot', 'sneakpeekbot', 'converter-bot', 'helperbot_', 'wikitextbot', 'nfcaaofficialrefbot', 'nfcaaofficialbot', 'transcribot', 'totesmessenger', 'repostsleuthbot'}
def isbot(a): a = (a or '').lower(); return a in BOTS or a.endswith('bot') or a.endswith('_bot')

# ---- metadata
meta = {}
for f in glob.glob(f'{D}/raw/youtube/*.json'):
    j = json.load(open(f))
    for it in j['items']: meta[it['id']] = it
    for i in j['requested']: meta.setdefault(i, None)
def dur(s):
    m = re.fullmatch(r'P(?:(\d+)D)?T?(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', s or '')
    return 0 if not m else sum(int(x or 0) * k for x, k in zip(m.groups(), (86400, 3600, 60, 1)))
vrows = []
for vid, it in meta.items():
    if not it: vrows.append(dict(video_id=vid, alive=False)); continue
    sn, cd, st, stt = it['snippet'], it['contentDetails'], it.get('statistics', {}), it.get('status', {})
    vrows.append(dict(video_id=vid, alive=stt.get('privacyStatus') != 'private', title=sn.get('title'), channel=sn.get('channelTitle'), channel_id=sn.get('channelId'),
                      uploaded=sn.get('publishedAt', '')[:10], duration=dur(cd.get('duration')), views=int(st.get('viewCount', 0) or 0), category_id=int(sn.get('categoryId', 0) or 0),
                      language=sn.get('defaultAudioLanguage') or sn.get('defaultLanguage'), embeddable=bool(stt.get('embeddable', True)), description=(sn.get('description') or '')[:500],
                      tags=' '.join(sn.get('tags', [])[:30])))
V = pd.DataFrame(vrows).set_index('video_id')

# ---- labels (in-session classification batches, data/labels/*.jsonl)
labels = {}
for f in sorted(glob.glob(f'{D}/labels/*.jsonl')):
    for line in open(f):
        if line.strip(): j = json.loads(line); labels[j['id']] = {**labels.get(j['id'], {}), **j}

# ---- mentions
M = pd.read_parquet(f'{D}/mentions.parquet')
SECRET = re.compile(r'(AKIA|ASIA)[0-9A-Z]{16}|AIza[0-9A-Za-z_\-]{35}|gh[pousr]_[0-9A-Za-z]{36,}|github_pat_[0-9A-Za-z_]{40,}|xox[baprs]-[0-9A-Za-z-]{10,}|-----BEGIN[A-Z ]*PRIVATE KEY-----|sk-[A-Za-z0-9_\-]{20,}|(?<![A-Za-z0-9/+])[A-Za-z0-9/+]{40}(?![A-Za-z0-9/+])')
M['text'] = M.text.fillna('').map(lambda t: SECRET.sub('[redacted]', t))
M['year'] = pd.to_datetime(M.created).dt.year
M = M[~M.author.map(isbot)]
M['who'] = M.source + ':' + M.author
crit = {(l['id'], i) for l in labels.values() for i in l.get('critical_items', [])}
M['critical'] = [(v, i) in crit for v, i in zip(M.video_id, M.item_id)]
# self-promotion: username ~ channel name
ch = V['channel'].to_dict()
def selfpromo(a, v):
    c = ch.get(v)
    if not isinstance(c, str): return False
    a2, c2 = re.sub(r'[^a-z0-9]', '', a.lower()), re.sub(r'[^a-z0-9]', '', c.lower())
    return len(a2) >= 4 and len(c2) >= 4 and fuzz.ratio(a2, c2) >= 85 or (len(a2) >= 6 and a2 in c2)
M['self'] = [selfpromo(a, v) for a, v in zip(M.author, M.video_id)]
# author linked >=3 videos from the same channel and is the main recommender of them
M['channel'] = M.video_id.map(ch)
g = M[M.channel.notna()].groupby(['who', 'channel']).video_id.nunique()
heavy = set(g[g >= 3].index)
whocount = M.groupby('video_id').who.nunique()
M['self'] = M['self'].values | pd.Series([((w, c) in heavy and whocount.get(v, 0) <= 2) for w, c, v in zip(M.who, M.channel, M.video_id)], index=M.index).values
M['flag_self'] = [(labels.get(v, {}).get('flags') or {}).get('self_promotion', False) and w in (labels.get(v, {}).get('self_whos') or [w]) for v, w in zip(M.video_id, M.who)]
REC = M[~M.critical & ~M.self & ~M.flag_self & ~M.is_short]

# ---- relevance: labels first, then rules for unlabelled
KW = re.compile(r'\b(invest\w*|stock(s|market)?|equit(y|ies)|buffett|munger|berkshire|damodaran|valuation|value investing|hedge fund|private equity|portfolio|dividend\w*|index fund|bogle|vanguard|bond(s)?|treasur(y|ies)|federal reserve|the fed\b|interest rates?|inflation|recession|econom\w*|financ\w*|wall street|bank(s|ing)?|capital(ism)?|market(s)?|trading|trader|crash|bubble|money|wealth|retire\w*|accounting|balance sheet|earnings|10-k|annual meeting|shareholder\w*|ackman|dalio|soros|druckenmiller|klarman|howard marks|peter lynch|graham|thorp|simons|renaissance|asness|greenblatt|pabrai|li lu|chanos|minsky|keynes|hayek|friedman|monetary|fiscal|debt|credit|currency|gold|bitcoin|crypto\w*|real estate|mortgage|tax(es)?|fire movement|frugal|budget\w*)\b', re.I)
def rule_rel(v):
    if v.get('category_id') in (10, 20, 17, 23, 1, 2, 19, 30, 43, 44): return False
    txt = f"{v.get('title','')} {v.get('channel','')} {v.get('tags','')} {v.get('description','')[:300]}"
    return len(KW.findall(txt)) >= 2 or bool(KW.search(v.get('title') or ''))

# ---- aggregate per video
agg = REC.groupby('video_id').agg(recs=('who', 'nunique'), comms=('community', 'nunique'), years=('year', 'nunique'), y0=('year', 'min'), y1=('year', 'max'))
crit_n = M[M.critical].groupby('video_id').size()
agg = agg[agg.recs >= 2].join(V, how='left')
agg = agg[agg.alive.fillna(False).astype(bool)]
inv_comm = REC[REC.source != 'hn'].groupby('video_id').size()
def relevant(vid, row):
    l = labels.get(vid)
    if l and 'relevant' in l: return bool(l['relevant'])
    return None  # unknown: decided below
agg['label_rel'] = [relevant(i, r) for i, r in agg.iterrows()]
agg['rule_rel'] = [rule_rel(r.to_dict()) for _, r in agg.iterrows()]
agg['relevant'] = [lr if lr is not None else (rr and inv_comm.get(v, 0) > 0) for v, lr, rr in zip(agg.index, agg.label_rel, agg.rule_rel)]
STRICT = os.environ.get('STRICT', '1') == '1'  # unlabelled videos only from investing subreddits are trusted less
agg['labelled'] = agg.label_rel.notna()

def L(v): return labels.get(v) or {}
# ---- merges (same speakers+event+year from labels, durations within 10%; much shorter -> clip)
def key(vid):
    l = labels.get(vid) or {}
    if not l.get('speakers') or not l.get('event') or not l.get('event_year'): return None
    return (tuple(sorted(s.lower() for s in l['speakers'])), re.sub(r'\W+', ' ', l['event'].lower()).strip(), l['event_year'])
groups = collections.defaultdict(list)
for vid in agg.index:
    k = key(vid)
    if k: groups[k].append(vid)
parent, merges = {}, []
for k, vids in groups.items():
    if len(vids) < 2: continue
    vids.sort(key=lambda v: (-agg.at[v, 'recs'], -agg.at[v, 'duration'], -agg.at[v, 'views']))
    canon = max(vids, key=lambda v: (agg.at[v, 'duration'] * 0 + agg.at[v, 'recs'], agg.at[v, 'duration'], agg.at[v, 'views']))
    longest = max(agg.at[v, 'duration'] for v in vids)
    for v in vids:
        if v == canon: continue
        d0, d1 = agg.at[v, 'duration'], agg.at[canon, 'duration']
        if fuzz.token_set_ratio(L(v).get('clean_title', ''), L(canon).get('clean_title', '')) < 60: continue  # same show, different episode
        if d1 and abs(d0 - d1) / max(d0, d1) <= 0.10: parent[v] = (canon, 'duplicate')
        elif d0 < 0.5 * d1: parent[v] = (canon, 'clip')
        else: continue
        merges.append(dict(child=v, parent=canon, kind=parent[v][1], key=' | '.join(map(str, k)), child_title=agg.at[v, 'title'], parent_title=agg.at[canon, 'title']))
pd.DataFrame(merges, columns=['child', 'parent', 'kind', 'key', 'child_title', 'parent_title']).to_csv(f'{R}/merges.csv', index=False)
REC = REC.assign(entry=REC.video_id.map(lambda v: parent.get(v, (v,))[0]))
E = REC.groupby('entry').agg(recs=('who', 'nunique'), comms=('community', 'nunique'), years=('year', 'nunique'), y0=('year', 'min'), y1=('year', 'max'), cmlist=('community', lambda s: sorted(set(s))))
E = E[E.index.isin(agg.index) & ~E.index.isin(parent.keys())]
E = E.join(agg[['title', 'channel', 'uploaded', 'duration', 'views', 'embeddable', 'relevant', 'labelled', 'description']])
E = E[(E.recs >= 2) & E.relevant.astype(bool) & (E.duration > 60)]
E['score'] = E.recs * (1 + 0.15 * (E.comms - 1)) * (1 + 0.05 * (E.years - 1).clip(upper=10))
E['deep'] = E.recs / (E.views + 10).map(math.log10)
E = E.sort_values('score', ascending=False)

# ---- related: shared threads + shared recommenders + same speakers
R2 = REC[REC.entry.isin(E.index)]
pairs = collections.Counter()
for col, w in (('thread_id', 1.0), ('who', 1.0)):
    for _, grp in R2.groupby(col).entry:
        u = list(set(grp))
        if 1 < len(u) <= 40:
            for a in u:
                for b in u:
                    if a != b: pairs[(a, b)] += w / math.log2(1 + len(u))
spk = collections.defaultdict(list)
for v in E.index:
    for s in (labels.get(v) or {}).get('speakers') or []: spk[s.lower()].append(v)
for s, vs in spk.items():
    if len(vs) <= 60:
        for a in vs:
            for b in vs:
                if a != b: pairs[(a, b)] += 1.5
rel = collections.defaultdict(list)
for (a, b), w in pairs.items(): rel[a].append((w + 0.001 * E.at[b, 'score'], b))

# ---- moments
def moments(vid):
    ts = sorted(int(t) for t in REC[(REC.entry == vid) & REC.t.notna()].t if t and t > 0)
    out = []
    for t in ts:
        if out and t - out[-1]['t0'] <= 60: out[-1]['n'] += 1
        else: out.append(dict(t0=t, t=t, n=1))
    return [dict(t=m['t'], n=m['n']) for m in out if m['n'] >= 2]

def L(v): return labels.get(v) or {}
URLX = re.compile(r'\(?(?:https?://)?(?:www\.|m\.)?(?:youtube\.com|youtu\.be|youtube-nocookie\.com)\S*', re.I)
def excerpt(t, n=200):
    t = re.sub(r'\s+', ' ', t or '').strip()
    m = URLX.search(t); c = m.start() if m else len(t) // 2
    t2 = URLX.sub('[video]', t); c = min(c, len(t2))
    a = max(0, c - n // 2); b = min(len(t2), a + n); a = max(0, b - n)
    x = t2[a:b]
    if a > 0: x = '…' + x[x.find(' ') + 1:] if ' ' in x[:30] else '…' + x
    if b < len(t2): x = (x[:x.rfind(' ')] if ' ' in x[-30:] else x) + '…'
    x = re.sub(r'(\[video\]\s*)+', '[video] ', x).strip()
    return x if x.strip('…[]video ') else ''
def clean_title(v, row):
    if L(v).get('clean_title'): return L(v)['clean_title']
    t = re.sub(r'[\U0001F000-\U0001FFFF☀-➿]', '', row.title or '').strip()
    t = re.sub(r'\s*[|#].*$', '', t) if len(re.sub(r'\s*[|#].*$', '', t)) > 15 else t
    return t[:110]
CATS = ['Lecture or course', 'Talk or speech', 'Shareholder meeting', 'Interview or conversation', 'Documentary', 'Explainer', 'News segment', 'Other']
def cat(v, row):
    if L(v).get('category') in CATS: return L(v)['category']
    t = (row.title or '').lower()
    for c, pat in (('Shareholder meeting', r'annual meeting|shareholder'), ('Lecture or course', r'lecture|class|course|session \d|mba|university|school'), ('Interview or conversation', r'interview|podcast|conversation|with '),
                   ('Documentary', r'documentary'), ('Talk or speech', r'talk|speech|keynote|address')):
        if re.search(pat, t): return c
    return 'Other'
idx, built = [], dt.date.today().isoformat()
E['ct'] = [clean_title(v, r) for v, r in E.iterrows()]; E['catg'] = [cat(v, r) for v, r in E.iterrows()]
E = E[E.catg != 'Other']  # film clips, pitches and gags people link in passing; see DECISIONS.md
for v, r in E.iterrows():
    idx.append(dict(i=v, t=r.ct, d=int(r.duration), c=r.catg, r=int(r.recs), n=int(r.comms), y=[int(r.y0), int(r.y1)], ny=int(r.years), s=round(r.score, 2), dc=round(r.deep, 3),
                    ev=L(v).get('event_year'), sp=', '.join(L(v).get('speakers') or []), e=L(v).get('event'), cm=r.cmlist, ot=r.title))
byid = {x['i']: x for x in idx}
childs = collections.defaultdict(list)
for c, (p, k) in parent.items(): childs[p].append((c, k))
for v, r in E.iterrows():
    mm = M[(M.video_id.isin([v] + [c for c, _ in childs[v]])) & ~M.self & ~M.flag_self].sort_values('created')
    seen, ms = set(), []
    for _, m in mm.iterrows():
        if m.who in seen: continue
        seen.add(m.who); ms.append(dict(c=m.community, d=str(m.created)[:10], u=m.permalink, x=excerpt(m.text), cr=bool(m.critical)))
    top = [b for _, b in sorted(rel[v], reverse=True) if b in byid][:12]
    if len(top) < 12:  # pad with the strongest entries of the same category
        top += [x['i'] for x in idx if x['c'] == r.catg and x['i'] != v and x['i'] not in top][:12 - len(top)]
    json.dump(dict(i=v, t=r.ct, ot=r.title, ch=r.channel, up=r.uploaded, d=int(r.duration), c=r.catg, r=int(r.recs), n=int(r.comms), y=[int(r.y0), int(r.y1)], embed=bool(r.embeddable),
                   why=L(v).get('why'), critical=int(crit_n.get(v, 0)), mentions=ms[:60], moments=moments(v),
                   others=[dict(i=c, t=agg.at[c, 'title'], d=int(agg.at[c, 'duration']), clip=k == 'clip') for c, k in childs[v]],
                   related=[byid[b] for b in top]), open(f'{S}/v/{v}.json', 'w'), separators=(',', ':'))
slim = lambda x: {k: x[k] for k in x if k not in ('ot',) or True}
json.dump(idx, open(f'{S}/all.json', 'w'), separators=(',', ':'))
top300 = [{k: v for k, v in x.items() if k not in ('ot', 's', 'sp', 'e')} for x in idx[:300]]
json.dump(top300, open(f'{S}/top.json', 'w'), separators=(',', ':'))
src = M.groupby('community').size().sort_values(ascending=False)
cms = collections.Counter(c for x in idx for c in x['cm'])
json.dump(dict(built=built, entries=len(idx), categories=[c for c in CATS if any(x['c'] == c for x in idx)], decades=sorted({x['ev'] // 10 * 10 for x in idx if x['ev']}),
               communities=sorted(cms.items(), key=lambda kv: -kv[1]), sources=[[k, int(v)] for k, v in src.items()]), open(f'{S}/meta.json', 'w'))
json.dump(idx, open(f'{D}/ranked.json', 'w'), indent=0)
agg.reset_index().drop(columns=['description']).to_parquet(f'{D}/videos.parquet')
# ---- public zip with hashed usernames
h = lambda a: hashlib.sha256(('stockstube:' + a).encode()).hexdigest()[:12]
pub = REC[REC.entry.isin(E.index)][['source', 'community', 'item_id', 'permalink', 'who', 'created', 'video_id', 'entry', 't', 'kind_item', 'score', 'text']].copy()
pub['who'] = pub.who.map(h); pub['text'] = pub.text.map(excerpt); pub = pub.rename(columns={'who': 'author_hash'})
buf = io.BytesIO()
with zipfile.ZipFile(f'{S}/stockstube-data.zip', 'w', zipfile.ZIP_DEFLATED) as z:
    z.writestr('ranked.json', json.dumps(idx)); z.writestr('videos.csv', E.drop(columns=['cmlist', 'description']).to_csv()); z.writestr('mentions.csv', pub.to_csv(index=False))
    z.writestr('README.txt', 'StocksTube data. Usernames are salted SHA-256 hashes. Excerpts are capped at 200 characters; follow permalinks for originals. Not investment advice.')
print('entries', len(idx), 'labelled', int(E.labelled.sum()), 'merges', len(merges), 'top size KB', os.path.getsize(f'{S}/top.json') // 1024)
