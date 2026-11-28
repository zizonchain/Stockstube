'use strict';
const $ = s => document.querySelector(s), app = $('#app');
const LS = {get(k, d) { try { return JSON.parse(localStorage.getItem('st_' + k)) ?? d } catch (e) { return d } },
  set(k, v) { try { localStorage.setItem('st_' + k, JSON.stringify(v)) } catch (e) {} }};
let ALL = null, META = null, CUR = {red: [], legends: [], picks: [], playlists: []}, full = false;
const state = {cat: '', dec: '', com: '', len: '', q: ''};
const esc = s => String(s ?? '').replace(/[&<>"']/g, c => ({'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'}[c]));
const fmtDur = s => { if (!s) return ''; const h = Math.floor(s / 3600), m = Math.floor(s % 3600 / 60), x = s % 60; return (h ? h + ':' + String(m).padStart(2, '0') : m) + ':' + String(x).padStart(2, '0') };
const thumb = id => `<img loading="lazy" alt="" src="https://i.ytimg.com/vi/${id}/hq2.jpg" onerror="this.onerror=null;this.src='https://i.ytimg.com/vi/${id}/hqdefault.jpg'">`;
const years = v => v.y[0] === v.y[1] ? v.y[0] : `${v.y[0]} to ${v.y[1]}`;
const fmtViews = n => n >= 1e9 ? (n / 1e9).toFixed(1).replace(/\.0$/, '') + 'B' : n >= 1e6 ? (n / 1e6).toFixed(1).replace(/\.0$/, '') + 'M' : n >= 1e3 ? Math.round(n / 1e3) + 'K' : String(n);
const evidence = v => `${fmtViews(v.v || 0)} views${v.u ? ` · ${v.u}` : ''}`;
async function getJSON(u) { const r = await fetch(u); if (!r.ok) throw new Error(u + ' ' + r.status); return r.json() }
async function load() {
  META = await getJSON('data/meta.json'); ALL = await getJSON('data/top.json');
  try { CUR = await getJSON('data/curated.json') } catch (e) {}
  getJSON('data/all.json').then(a => { ALL = a; full = true; if (!location.hash.startsWith('#/v/')) route() }).catch(() => {});
}
function watched() { return LS.get('watched', []) } function hidden() { return LS.get('hidden', []) } function saved() { return LS.get('saved', []) }
function markWatched(id) { const w = watched().filter(x => x.id !== id); w.unshift({id, at: Date.now()}); LS.set('watched', w.slice(0, 300)) }
function toggle(k, id) { let a = LS.get(k, []); a = a.includes(id) ? a.filter(x => x !== id) : [id, ...a]; LS.set(k, a); return a.includes(id) }
const TABS = [['red', 'Red day remedies'], ['legends', 'Legends'], ['deep', 'Hidden gems'], ['durable', 'Recommended year after year'], ['longs', 'Lectures, shareholder meetings and long interviews'], ['picks', "Editor's picks"], ['playlists', 'Playlists'], ['saved', 'Saved'], ['foryou', 'For you'], ['top', 'All']];
// Channel variety for ranked lists: at most 2 videos from one channel in any run of 10. Order otherwise unchanged.
function diversify(list) { const out = [], wait = []; const ok = v => out.slice(-9).filter(x => x.ch && x.ch === v.ch).length < 2;
  for (const v of list) { for (let k = 0; k < wait.length; k++) if (ok(wait[k])) { out.push(wait.splice(k, 1)[0]); k = -1 }
    if (ok(v)) out.push(v); else wait.push(v) }
  for (const v of wait) out.push(v); return out }
async function forYou() {
  const w = watched().slice(0, 25), hid = new Set([...hidden(), ...watched().map(x => x.id)]);
  if (!w.length) return null;
  const score = new Map(); const cache = LS.get('relcache', {});
  await Promise.all(w.map(async (x, i) => {
    let rel = cache[x.id]; if (!rel) { try { rel = (await getJSON(`data/v/${x.id}.json`)).related.map(r => r.i); cache[x.id] = rel } catch (e) { rel = [] } }
    const wt = 1 / (1 + i * 0.25);
    rel.forEach((id, j) => { if (!hid.has(id)) score.set(id, (score.get(id) || 0) + wt * (1 - j / 15)) });
  }));
  LS.set('relcache', cache);
  const byId = new Map(ALL.map(v => [v.i, v]));
  return [...score].sort((a, b) => b[1] - a[1]).map(([id]) => byId.get(id)).filter(Boolean);
}
function applyFilters(list) {
  const q = state.q.toLowerCase().trim(), hid = new Set(hidden());
  return list.filter(v => !hid.has(v.i) && (!state.cat || v.c === state.cat) && (!state.dec || (v.ev && Math.floor(v.ev / 10) * 10 == state.dec)) &&
    (!state.com || v.cm.includes(state.com)) && (!state.len || (state.len === 's' ? v.d < 1200 : state.len === 'm' ? v.d >= 1200 && v.d < 3600 : v.d >= 3600)) &&
    (!q || (v.t + ' ' + (v.sp || '') + ' ' + (v.e || '') + ' ' + (v.ot || '')).toLowerCase().includes(q)));
}
function opt(name, label, vals) { return `<select data-f="${name}" aria-label="${label}"><option value="">${label}</option>${vals.map(([v, l]) => `<option value="${esc(v)}" ${state[name] == v ? 'selected' : ''}>${esc(l)}</option>`).join('')}</select>` }
function card(v, w, n) { return `<a class="card${w.has(v.i) ? ' watched' : ''}" href="#/v/${v.i}"><div class="thumb">${thumb(v.i)}<span class="dur">${fmtDur(v.d)}</span>${n ? `<span class="num">${n}</span>` : ''}</div><h3>${esc(v.t)}</h3><div class="ev">${v.ep ? `<span class="chip ep">Editor's pick</span>` : `<span class="chip">${esc(v.c)}</span>`}${evidence(v)}</div></a>` }
let shown = 60;
async function home(tab) {
  let list, note = '';
  const w = new Set(watched().map(x => x.id));
  if (tab === 'foryou') { list = await forYou(); if (!list || !list.length) { list = ALL.slice(); note = watched().length ? '' : '' } }
  else if (tab === 'deep') list = ALL.filter(v => v.r >= 3 && v.v < 250000).sort((a, b) => b.dc - a.dc);
  else if (tab === 'durable') list = ALL.filter(v => v.ny >= 5);
  else if (tab === 'red') list = (CUR.red && CUR.red.length) ? CUR.red.slice() : ALL.filter(v => v.rd);
  else if (tab === 'longs') list = ALL.filter(v => v.d >= 3600);
  else if (tab === 'legends') list = CUR.legends.slice();
  else if (tab === 'picks') list = CUR.picks.slice();
  else if (tab === 'playlists') return playlists();
  else if (tab === 'saved') { const s = saved(), m = new Map([...CUR.playlists.flatMap(p => p.items), ...CUR.picks, ...CUR.legends, ...ALL].map(v => [v.i, v])); list = s.map(id => m.get(id)).filter(Boolean) }
  else list = ALL.slice();
  list = applyFilters(list);
  if (['top', 'deep', 'durable', 'longs'].includes(tab)) list = diversify(list);
  const decs = META.decades.map(d => [d, d + 's']), coms = META.communities.map(c => [c[0], `${c[0]} (${c[1]})`]);
  app.innerHTML = `${nav(tab)}
  <div class="filters">${opt('cat', 'Category', META.categories.map(c => [c, c]))}${opt('dec', 'Decade of event', decs)}${opt('com', 'Community', coms)}${opt('len', 'Length', [['s', 'Under 20 min'], ['m', '20 to 60 min'], ['l', 'Over 60 min']])}</div>
  ${list.length ? `<div class="grid">${list.slice(0, shown).map(v => card(v, w)).join('')}</div>${list.length > shown ? `<p style="text-align:center"><button class="more" id="more">Show more (${list.length - shown})</button></p>` : ''}` : `<p class="empty">Nothing here yet.</p>`}`;
  app.querySelectorAll('select').forEach(s => s.onchange = () => { state[s.dataset.f] = s.value; shown = 60; route() });
  const m = $('#more'); if (m) m.onclick = () => { shown += 120; route() };
}
function nav(tab) { return `<nav class="tabs">${TABS.map(([k, l]) => `<a href="#/${k}" class="t-${k}${k === tab ? ' on' : ''}">${l}</a>`).join('')}</nav>` }
function playlists() {
  app.innerHTML = `${nav('playlists')}<div class="grid">${CUR.playlists.map(p => `<a class="card" href="#/pl/${p.id}"><div class="thumb">${p.items[0] ? thumb(p.items[0].i) : ''}<span class="dur">${p.items.length} videos</span></div><h3>${esc(p.title)}</h3><div class="ev">${esc(p.note)}</div></a>`).join('')}</div>` }
function playlist(id) {
  const p = CUR.playlists.find(x => x.id === id); if (!p) { app.innerHTML = '<p class="empty">Playlist not found.</p>'; return }
  document.title = p.title + ' · StocksTube'; const w = new Set(watched().map(x => x.id));
  app.innerHTML = `${nav('playlists')}<div class="prose"><h1>${esc(p.title)}</h1><p class="meta">${esc(p.note)}</p></div><div class="grid">${p.items.map((v, k) => card(v, w, k + 1)).join('')}</div>`; window.scrollTo(0, 0) }
async function video(id) {
  let v; try { v = await getJSON(`data/v/${id}.json`) } catch (e) { app.innerHTML = '<p class="empty">Video not found.</p>'; return }
  const start = new URLSearchParams(location.hash.split('?')[1] || '').get('t');
  const yt = `https://www.youtube.com/watch?v=${id}${start ? '&t=' + start + 's' : ''}`;
  document.title = v.t + ' · StocksTube';
  const lw = new Set(watched().map(x => x.id));
  app.innerHTML = `<div class="vp">${v.embed ? `<div id="pl"><button class="thumb" id="play" style="border:0;padding:0;width:100%;cursor:pointer" aria-label="Play">${thumb(id)}<span class="dur">▶ Play</span></button></div>` : `<a href="${yt}" target="_blank" rel="noopener" class="thumb" style="display:block" data-yt>${thumb(id)}<span class="dur">Watch on YouTube</span></a>`}
  <h1>${esc(v.t)}</h1><div class="meta">${esc(v.ot)} · ${esc(v.ch)} · uploaded ${esc(v.up)} · ${fmtDur(v.d)} · <a href="${yt}" target="_blank" rel="noopener" data-yt>YouTube</a></div>
  <div class="ev" style="margin-top:6px">${v.ep ? `<span class="chip ep">Editor's pick</span>` : `<span class="chip">${esc(v.c)}</span>`}${evidence(v)}</div>
  <div class="acts"><button id="sv" class="${saved().includes(id) ? 'on' : ''}">${saved().includes(id) ? 'Saved' : 'Save'}</button><button id="hd">${hidden().includes(id) ? 'Unhide' : 'Hide'}</button></div>
  ${v.why ? `<h2>${v.ep ? "Why it's here" : 'Why people recommend it'}</h2><p class="why">${esc(v.why)}</p>` : ''}
  ${v.moments && v.moments.length ? `<h2>Moments people pointed to</h2>${v.moments.map(m => `<div class="mention"><a href="#/v/${id}?t=${m.t}">${fmtDur(m.t)}</a> · ${m.n} mentions</div>`).join('')}` : ''}
  ${v.ep && !v.mentions.length ? `<h2>Mentions</h2><p class="meta">Added by the editor. No community recommendations in our data yet.</p>` : `<h2>Mentions (${v.mentions.length})${v.critical ? ` · ${v.critical} critical` : ''}</h2>`}
  ${v.mentions.map(m => `<div class="mention"><div class="ev">${esc(m.c)} · ${esc(m.d)}${m.cr ? ' · <span class="chip">critical</span>' : ''} · <a href="${esc(m.u)}" target="_blank" rel="noopener">original</a></div>${esc(m.x)}</div>`).join('')}
  ${v.others && v.others.length ? `<h2>Other uploads and clips</h2>${v.others.map(o => `<div class="mention"><a href="https://www.youtube.com/watch?v=${o.i}" target="_blank" rel="noopener">${esc(o.t)}</a> <span class="ev">${fmtDur(o.d)}${o.clip ? ' · clip' : ''}</span></div>`).join('')}` : ''}
  ${(v.related || []).length ? `<h2>Related</h2><div class="grid">${v.related.map(r => card(r, lw)).join('')}</div>` : ''}</div>`;
  const p = $('#play'); if (p) p.onclick = () => { markWatched(id); $('#pl').innerHTML = `<iframe class="player" src="https://www.youtube-nocookie.com/embed/${id}?autoplay=1${start ? '&start=' + start : ''}" allow="autoplay; encrypted-media; picture-in-picture" allowfullscreen title="${esc(v.t)}"></iframe>` };
  app.querySelectorAll('[data-yt]').forEach(a => a.addEventListener('click', () => markWatched(id)));
  $('#sv').onclick = e => { const on = toggle('saved', id); e.target.textContent = on ? 'Saved' : 'Save'; e.target.classList.toggle('on', on) };
  $('#hd').onclick = e => { const on = toggle('hidden', id); e.target.textContent = on ? 'Unhide' : 'Hide' };
  window.scrollTo(0, 0);
}
function about() {
  document.title = 'About · StocksTube';
  app.innerHTML = `<div class="prose"><h1>About</h1>
  <p>StocksTube lists the investing videos that people in investing communities keep recommending to each other. It reads public comments on Hacker News and investing subreddits and ranks each video by how many separate months new people recommended it, so a video people kept recommending for years beats a one-week spike.</p>
  <p>A video needs at least two different people recommending it. Bots, critical mentions and people linking their own channels do not count. Duplicate uploads of the same talk are merged. Titles are plain labels written from the video and the comments, not the uploader's title.</p>
  <h2>Sources</h2><table>${META.sources.map(s => `<tr><td>${esc(s[0])}</td><td>${s[1].toLocaleString()} mentions</td></tr>`).join('')}</table>
  <p>${META.entries.toLocaleString()} videos listed. Data built ${esc(META.built)}.</p>
  <h2>Credit</h2><p>The idea and the approach come from <a href="https://hackertube.org">HackerTube</a> by Andrej Karpathy.</p>
  <p>These are videos community members recommended. They are not endorsements and not investment advice.</p>
  <p>Your watch history, saved and hidden videos stay in this browser. There are no accounts and no tracking.</p></div>`;
}
let qt; $('#q').addEventListener('input', e => { clearTimeout(qt); qt = setTimeout(() => { state.q = e.target.value; shown = 60; const h = location.hash.slice(2).split('?')[0]; if (state.q && !['top', 'deep', 'durable', 'longs', 'red'].includes(h)) location.hash = '#/top'; else route() }, 150) });
async function route() {
  const h = location.hash.slice(2).split('?')[0];
  if (h.startsWith('v/')) return video(h.slice(2));
  if (h.startsWith('pl/')) return playlist(h.slice(3));
  document.title = 'StocksTube';
  if (h === 'about') return about();
  return home(TABS.some(t => t[0] === h) ? h : 'red');
}
window.addEventListener('hashchange', route);
load().then(route).catch(e => { app.innerHTML = `<p class="empty">Could not load data. Run python build.py first.</p>` });
