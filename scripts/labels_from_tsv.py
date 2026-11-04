"""Convert in-session label batches (data/labels/batch_*.txt) into jsonl.
Line: id|C|clean title|speaker;speaker|event|year   C: L T S I D E N O. Every id listed in the batch's
review file (data/labels/reviewed_*.txt) but not labelled is marked relevant=false."""
import glob, json, os
D = os.path.join(os.path.dirname(__file__), '..', 'data', 'labels')
C = dict(L='Lecture or course', T='Talk or speech', S='Shareholder meeting', I='Interview or conversation', D='Documentary', E='Explainer', N='News segment', O='Other')
for f in sorted(glob.glob(f'{D}/batch_*.txt')):
    out, seen = [], set()
    for line in open(f):
        line = line.rstrip('\n')
        if not line.strip() or line.startswith('#'): continue
        p = (line.split('|') + [''] * 6)[:6]
        flags = {}
        if p[1].endswith('!'): flags['likely_fake_or_ai_voice'] = True; p[1] = p[1][:-1]
        if p[1].endswith('$'): flags['self_promotion'] = True; p[1] = p[1][:-1]
        rec = dict(id=p[0].strip(), relevant=True, category=C.get(p[1].strip(), 'Other'), clean_title=p[2].strip(), speakers=[s.strip() for s in p[3].split(';') if s.strip()] or None,
                   event=p[4].strip() or None, event_year=int(p[5]) if p[5].strip().isdigit() else None, flags=flags)
        if flags: rec['relevant'] = False
        out.append(rec); seen.add(rec['id'])
    rv = f.replace('batch_', 'reviewed_')
    if os.path.exists(rv):
        for i in open(rv).read().split():
            if i not in seen: out.append(dict(id=i, relevant=False))
    json.dump
    with open(f.replace('.txt', '.jsonl'), 'w') as g:
        for r in out: g.write(json.dumps(r) + '\n')
    print(os.path.basename(f), sum(r['relevant'] for r in out), 'relevant of', len(out))
