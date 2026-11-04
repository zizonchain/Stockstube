"""Extract YouTube links from comment text/HTML."""
import re, html, urllib.parse
ID = r'([A-Za-z0-9_-]{11})'
HOST = r'(?:https?://)?(?:www\.|m\.|music\.)?(?:youtube\.com|youtube-nocookie\.com|youtu\.be)'
URL_RE = re.compile(r'(?:https?://)?(?:www\.|m\.|music\.)?(?:youtube\.com|youtube-nocookie\.com|youtu\.be)[^\s<>"\')\]]*', re.I)
def _t(v):
    if not v: return None
    v = v.strip()
    if v.isdigit(): return int(v)
    m = re.fullmatch(r'(?:(\d+)h)?(?:(\d+)m)?(?:(\d+)s?)?', v)
    if m and any(m.groups()):
        h, mi, s = (int(x or 0) for x in m.groups()); return h*3600+mi*60+s
    return None
def normalize(text):
    t = html.unescape(text or '')
    for _ in range(2):
        t = urllib.parse.unquote(t) if '%2F' in t or '%3A' in t or '%3F' in t else t
    return t.replace('\\_', '_')
def extract(text):
    """Return list of dicts: kind(video|short|playlist|channel), id, t, start, end."""
    t = normalize(text); out = []
    for m in URL_RE.finditer(t):
        u = m.group(0).rstrip('.,;:!*')
        if not u.lower().startswith('http'): u = 'https://' + u
        p = urllib.parse.urlparse(u); q = urllib.parse.parse_qs(p.query)
        path = p.path; host = p.netloc.lower()
        ts = _t((q.get('t') or q.get('start') or [None])[0] or (re.search(r't=([0-9hms]+)', p.fragment) or [None, None])[1])
        vid = None; kind = 'video'
        if 'youtu.be' in host:
            mm = re.match(r'/' + ID, path); vid = mm and mm.group(1)
        elif path.startswith('/watch'):
            v = (q.get('v') or [''])[0]; vid = v[:11] if re.fullmatch(ID, v[:11] or 'x') else None
            if not vid and q.get('list'): out.append(dict(kind='playlist', id=q['list'][0], t=None, start=m.start(), end=m.end())); continue
        else:
            mm = re.match(r'/(embed|v|live|shorts|e)/' + ID, path)
            if mm: vid = mm.group(2); kind = 'short' if mm.group(1) == 'shorts' else 'video'
            elif path.startswith('/playlist') and q.get('list'):
                out.append(dict(kind='playlist', id=q['list'][0], t=None, start=m.start(), end=m.end())); continue
            elif re.match(r'/(channel|c|user|@)', path) or path.startswith('/@'):
                out.append(dict(kind='channel', id=path.strip('/').split('/')[0] if not path.startswith('/channel') else path.split('/')[2] if len(path.split('/'))>2 else '', t=None, start=m.start(), end=m.end())); continue
        if vid and re.fullmatch(ID, vid):
            out.append(dict(kind=kind, id=vid, t=ts, start=m.start(), end=m.end()))
    return out, t
def context(text, start, end, n=500):
    pad = max(0, (n - (end - start)) // 2)
    s = text[max(0, start-pad): end+pad]
    s = re.sub(r'<[^>]+>', ' ', s); return re.sub(r'\s+', ' ', s).strip()[:n]
if __name__ == '__main__':
    tests = ['<a href="https://www.youtube.com/watch?v=dQw4w9WgXcQ&amp;t=2m30s">x</a>', '[talk](https://youtu.be/abcdefghijk?t=123)',
             'https://m.youtube.com/watch?feature=share&v=abcdefghijk', 'https://www.youtube-nocookie.com/embed/abcdefghijk?start=60',
             'https://www.google.com/url?q=https%3A%2F%2Fwww.youtube.com%2Fwatch%3Fv%3Dabcdefghijk', 'https://youtube.com/shorts/abcdefghijk',
             'https://www.youtube.com/live/abcdefghijk', 'https://www.youtube.com/playlist?list=PL123', 'https://www.youtube.com/@Bogleheads', 'youtube.com/watch?v=abc\\_defghij&t=1h2m3s']
    for x in tests: print(extract(x)[0])
