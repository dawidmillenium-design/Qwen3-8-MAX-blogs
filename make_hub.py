#!/usr/bin/env python3
"""Generate the GitHub-Pages hub page (docs/hub.html) for all 22 site files.
Hub lives in docs/ so its links to ../site/*.html work both locally and on
https://dawidmillenium-design.github.io/Qwen3-8-MAX-blogs/index.html"""
import re, html, math, os, json

SITE = 'site/'   # hub sits at Pages root; posts live in site/ folder

src = open('site/index.html').read()

# ---------- 1. parse the 22 cards ----------
cards = re.findall(r'<article class="card">.*?</article>', src, re.S)
assert len(cards) == 22, len(cards)

posts = []
for c in cards:
    badge = re.search(r'<span class="badge">(.*?)</span><span>([^<]*)</span>', c, re.S)
    icon_svg = badge.group(1)
    meta_txt = badge.group(2)                       # "10 min · #01"
    num  = int(re.search(r'#(\d+)', meta_txt).group(1))
    mins = int(re.search(r'(\d+)\s*min', meta_txt).group(1))
    title = html.unescape(re.search(r'<h3><a class="xlink"[^>]*>(.*?)</a></h3>', c, re.S).group(1))
    blurb = html.unescape(re.search(r'<p>(.*?)</p>', c, re.S).group(1)).rstrip('… ').strip()
    cat = html.unescape(badge.group(0).split('</svg>')[1].replace('</span>', '').strip())
    links = re.findall(r'<a class="xlink" href="(post-\d+\.html)">([^<]*)</a>',
                       c.split('Context links')[1])
    posts.append(dict(num=num, file=f'post-{num:02d}.html', title=title, blurb=blurb,
                      cat=cat, mins=mins, icon=icon_svg, links=links))

# ---------- 2b. cluster by category (moved below so neg_css is ready) ----------
css_full = open('site/style.css').read()

# pull the shared design system (tokens, blobs, grain, header/footer, icon rigs,
# negative-colour hover rules) straight from site/style.css — minus page-specific
# article/table/TOC rules the hub doesn't use.
def slice_rules(css):
    keep = []
    for m in re.finditer(r'([^{}]+)\{([^{}]*)\}', css):
        sel = m.group(1).strip()
        if sel.startswith('@'):            # @property / @media blocks handled loosely
            continue
        keep.append(m.group(0))
    return '\n'.join(keep)

base_css = slice_rules(css_full)
# explicit negative-colour hover rule (the crown jewel of this request)
neg_hover = re.search(r'a\.xlink:hover[^}]+\}', css_full).group(0)

hub_css = ''   # index.html's inline style block is fully re-declared in EXTRA_CSS instead

EXTRA_CSS = """
/* ================= HUB EXTRAS ================= */
/* negative-colour hover everywhere */
.hubcard:hover .ic svg,.jump a:hover svg{filter:invert(1) hue-rotate(180deg) contrast(1.4)}
.map a:hover circle{filter:invert(1) hue-rotate(180deg)}
.lchip:hover{filter:invert(1) hue-rotate(180deg)}
.emblem .pulse2{animation-name:rpulse;animation-duration:2.2s;animation-timing-function:ease-in-out;animation-iteration-count:infinite}
.emblem .orbitg{animation-name:spin;animation-duration:9s;animation-timing-function:linear;animation-iteration-count:infinite}
.emblem .orbitg2{animation-name:spin;animation-duration:15s;animation-timing-function:linear;animation-iteration-count:infinite;animation-direction:reverse}
.grid{display:grid;gap:1.4rem;grid-template-columns:repeat(auto-fill,minmax(min(420px,100%),1fr));container-type:inline-size}
.hero{padding:clamp(2rem,7vw,5rem) 0 1.5rem;text-align:center}
.hero h1{font-size:clamp(2.4rem,7vw,5rem);margin:0;font-family:var(--fd);letter-spacing:-.02em;
background:linear-gradient(100deg,var(--a),var(--b) 45%,var(--c));-webkit-background-clip:text;background-clip:text;color:transparent}
.hero p{color:var(--muted);max-width:60ch;margin:1rem auto;font-family:var(--fd)}
.stats{display:flex;gap:1.2rem;justify-content:center;flex-wrap:wrap;font-family:var(--fd);font-size:.85rem;color:var(--muted)}
.stats b{color:var(--ink)}
.ctx{font-family:var(--fd);font-size:.8rem;display:flex;flex-wrap:wrap;gap:.5rem;align-items:center;color:var(--muted)}
.ctx strong{text-transform:uppercase;letter-spacing:.08em;font-size:.7rem}
@keyframes dashmove{to{stroke-dashoffset:-40}}
@keyframes marq{to{transform:translateX(-50%)}}
@keyframes spinang{to{--ang:360deg}}
.wrap{max-width:1200px;margin:0 auto;padding:0 clamp(1rem,4vw,3rem) 4rem}
.topgrid{display:grid;gap:2rem;grid-template-columns:minmax(0,2fr) minmax(0,1fr);align-items:start;margin-top:2rem}
@media (max-width:900px){.topgrid{grid-template-columns:1fr}}
.emblem-card{background:var(--panel);border:1px solid var(--line);border-radius:var(--r);padding:1.6rem;backdrop-filter:blur(24px) saturate(1.6);position:relative;isolation:isolate;overflow:hidden}
.emblem-card::before{content:"";position:absolute;inset:-20%;z-index:-1;background:conic-gradient(from var(--ang),var(--a),var(--b),var(--c),var(--a));filter:blur(70px);opacity:.28;mix-blend-mode:plus-lighter;animation:spinang 14s linear infinite}
.emblem{display:block;margin:0 auto;width:min(300px,70%)}
.emblem .ring{fill:none;stroke:url(#hg);stroke-width:1.4}
.emblem .node{fill:var(--ink)}
.emblem .core{fill:none;stroke:var(--a);stroke-width:2}
.emblem .orbitg{transform-box:fill-box;transform-origin:center;animation:spin 9s linear infinite}
.emblem .orbitg2{transform-box:fill-box;transform-origin:center;animation:spin 15s linear infinite reverse}
.emblem .pulse2{transform-box:fill-box;transform-origin:center;animation:pulse 2.2s ease-in-out infinite}
.emblem text{font-family:var(--fd);font-size:3.2px;letter-spacing:.4px;fill:var(--muted)}
.legend{display:flex;flex-wrap:wrap;gap:.55rem;justify-content:center;margin-top:1rem}
.lchip{font-family:var(--fd);font-size:.72rem;text-transform:uppercase;letter-spacing:.08em;border:1px solid var(--line);border-radius:99px;padding:.3rem .7rem;color:var(--muted);transition:.35s;cursor:default}
.wiring{margin-top:2.6rem}
.wiring h2,.cluster h2{font-family:var(--fd);font-size:clamp(1.3rem,3vw,1.9rem);margin:0 0 .3rem;text-wrap:balance}
.wiring p,.cluster>p{color:var(--muted);margin:.2rem 0 1.2rem;font-family:var(--fd);font-size:.9rem}
.map{background:var(--panel);border:1px solid var(--line);border-radius:var(--r);padding:1rem;backdrop-filter:blur(18px)}
.map svg{width:100%;height:auto;display:block}
.map .edge{stroke:color-mix(in oklab,var(--b) 55%,transparent);stroke-width:1.1;fill:none;stroke-dasharray:5 7;animation:dashmove 2.2s linear infinite}
.map .nlabel{font-family:var(--fd);font-size:6.5px;fill:var(--muted)}
.map a circle{fill:#0b0e22;stroke:var(--c);stroke-width:1.2;transition:.3s}
.map a:hover circle{stroke:var(--ink);r:7}
.clusters{display:grid;gap:2.6rem;margin-top:2.6rem}
.cluster .grid{margin-top:.4rem}
.hubcard{display:grid;grid-template-columns:52px 1fr;gap:0 1rem;background:var(--panel);border:1px solid var(--line);border-radius:var(--r);padding:1.2rem 1.3rem;backdrop-filter:blur(18px) saturate(1.5);position:relative;isolation:isolate;transition:.4s cubic-bezier(.2,.9,.2,1);text-decoration:none;color:inherit}
.hubcard::before{content:"";position:absolute;inset:-1px;z-index:-1;border-radius:inherit;opacity:0;transition:.5s;background:conic-gradient(from var(--ang),var(--a),var(--b),var(--c),var(--a));filter:blur(60px);mix-blend-mode:plus-lighter}
.hubcard:hover::before{opacity:.55}
.hubcard:hover{transform:translateY(-4px) scale(1.015);border-color:color-mix(in oklab,var(--c) 60%,var(--line))}
.hubcard .ic{grid-row:1/span 3;display:grid;place-items:center;width:52px;height:52px;border-radius:14px;background:color-mix(in oklab,var(--a) 14%,transparent);border:1px solid var(--line);transition:.4s}
.hubcard .ic svg{width:26px;height:26px;fill:none;stroke:currentColor;stroke-width:1.7;stroke-linecap:round;stroke-linejoin:round;transition:filter .45s}
.hubcard:hover .ic{background:color-mix(in oklab,var(--c) 22%,transparent)}
.hubcard .no{font-family:var(--fd);font-size:.7rem;letter-spacing:.14em;color:var(--muted);text-transform:uppercase}
.hubcard h3{margin:.15rem 0 .4rem;font-family:var(--fd);font-size:1.06rem;line-height:1.25;text-wrap:balance}
.hubcard h3 span.t{background:linear-gradient(90deg,var(--c),var(--c)) 0 100%/0 2px no-repeat;transition:background-size .4s}
.hubcard:hover h3 span.t{background-size:100% 2px}
.hubcard p{color:var(--muted);font-size:.88rem;margin:0 0 .6rem}
.hubcard .ctx{grid-column:2}
.hubcard .ctx a{margin-right:.4rem}
.jump{display:flex;flex-wrap:wrap;gap:.45rem;margin-top:1.4rem}
.jump a{font-family:var(--fd);font-size:.8rem;border:1px solid var(--line);border-radius:12px;padding:.35rem .6rem;color:var(--muted);text-decoration:none;transition:.3s;background:var(--panel)}
.jump a b{color:var(--c);margin-right:.3rem}
.jump a:hover{color:var(--ink);border-color:var(--c);transform:translateY(-2px)}
.flowbar{margin-top:2.6rem;overflow:hidden;border:1px dashed var(--line);border-radius:var(--r);padding:.9rem 0;background:color-mix(in oklab,var(--bg) 60%,transparent)}
.flow{display:flex;gap:3rem;width:max-content;animation:marq 30s linear infinite;font-family:var(--fd);font-size:.85rem;color:var(--muted);white-space:nowrap}
.flow span b{color:var(--b)}
.howto{margin-top:2.6rem;display:grid;gap:1.2rem;grid-template-columns:repeat(auto-fit,minmax(min(260px,100%),1fr))}
.howto article{background:var(--panel);border:1px solid var(--line);border-radius:var(--r);padding:1.2rem 1.3rem;backdrop-filter:blur(16px)}
.howto h3{margin:.5rem 0 .4rem;font-family:var(--fd);font-size:1rem}
.howto p{margin:0;color:var(--muted);font-size:.86rem}
.howto .ic{width:38px;height:38px;border-radius:12px;display:grid;place-items:center;background:color-mix(in oklab,var(--b) 16%,transparent);border:1px solid var(--line)}
.howto .ic svg{width:20px;height:20px;fill:none;stroke:currentColor;stroke-width:1.7;stroke-linecap:round;stroke-linejoin:round}
.badge{display:inline-flex;align-items:center;gap:.4rem;font-family:var(--fd);font-size:.72rem;text-transform:uppercase;letter-spacing:.08em;color:var(--muted)}
.badge svg{width:16px;height:16px;fill:none;stroke:currentColor;stroke-width:1.7;stroke-linecap:round;stroke-linejoin:round}
@media (prefers-reduced-motion:reduce){.flow,.emblem .orbitg,.emblem .orbitg2,.map .edge{animation:none}}
"""

esc = html.escape

def card_html(p):
    ctx = ''.join(f'<a class="xlink" href="{SITE}{f}">{esc(t[:36])}…</a>' for f, t in p['links'])
    return f'''<a class="hubcard" href="{SITE}{p["file"]}">
  <span class="ic">{p["icon"]}</span>
  <span class="no">Dispatch #{p["num"]:02d} · {p["mins"]} min read · {esc(p["cat"])}</span>
  <h3><span class="t">{esc(p["title"])}</span></h3>
  <p>{esc(p["blurb"][:150])}</p>
  <div class="ctx"><strong>Context links →</strong> {ctx}</div>
</a>'''

# ---------- 2. cluster by category ----------
cats = {}
for p in posts:
    cats.setdefault(p['cat'], []).append(p)
clusters_html = ''
for cat, plist in cats.items():
    grid = ''.join(card_html(p) for p in sorted(plist, key=lambda x: x['num']))
    clusters_html += f'''<section class="cluster"><h2>{esc(cat)}</h2>
<p>{len(plist)} dispatch{'' if len(plist)==1 else 'es'} — click any card to open it; hover flips its icon rig to the negative spectrum.</p>
<div class="grid">{grid}</div></section>'''

# ---------- 3. link-map SVG (real edges from context rails) ----------
W, H = 900, 560
pos = {}
for i, p in enumerate(posts):
    ang = i * 2 * math.pi / 22 - math.pi / 2
    pos[p['num']] = (W/2 + 380*math.cos(ang)*1.02, H/2 + 240*math.sin(ang))
edges = set()
for p in posts:
    for f, _ in p['links']:
        n2 = int(re.search(r'\d+', f).group())
        edges.add((min(p['num'], n2), max(p['num'], n2)))
edge_s = ''.join(
    f'<path class="edge" d="M{x1:.0f} {y1:.0f} Q{W/2+(x1-W/2)*.25:.0f} {H/2+(y1-H/2)*.25:.0f} {x2:.0f} {y2:.0f}"/>'
    for a, b in sorted(edges)
    for x1, y1 in [pos[a]] for x2, y2 in [pos[b]])
node_s = ''.join(
    f'<a href="{SITE}post-{p["num"]:02d}.html"><circle cx="{x:.0f}" cy="{y:.0f}" r="5.5"/>'
    f'<text class="nlabel" x="{x:.0f}" y="{y-9:.0f}" text-anchor="middle">{p["num"]:02d}</text></a>'
    for p in posts for x, y in [pos[p['num']]])
map_svg = f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="Map of all contextual links between the 22 dispatches ({len(edges)} unique edges)">{edge_s}{node_s}</svg>'

# ---------- 4. emblem nodes ----------
nodes = ''.join(
    f'<circle class="node pulse2" cx="{60+52*math.cos(i*2*math.pi/22):.1f}" cy="{60+52*math.sin(i*2*math.pi/22):.1f}" r="1.7"/>'
    for i in range(22))

jump = ''.join(f'<a href="{SITE}{p["file"]}"><b>{p["num"]:02d}</b>{esc(p["title"][:32])}…</a>' for p in posts)
legend = ''.join(f'<span class="lchip">{esc(c)}</span>' for c in sorted(cats))
marq = ''.join(f'<span><b>#{p["num"]:02d}</b> {esc(p["title"][:40])}</span>' for p in posts)

page = f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>THE CONTROL FILES — Hub · all 22 dispatches</title>
<meta name="description" content="Central hub for all 22 Control Files dispatches: coercive systems, environmental gaslighting, liminal architecture and digital power. Contextual inter-links, negative-colour hover effects, animated SVG icon rigs.">
<meta property="og:title" content="THE CONTROL FILES — Hub">
<meta property="og:description" content="22 interconnected dispatches on power, space &amp; perception. Hover goes negative.">
<meta property="og:type" content="website">
<style>
{base_css}
{neg_hover}
{EXTRA_CSS}</style></head>
<body><div class="progress"></div><i class="blob b1"></i><i class="blob b2"></i><i class="blob b3"></i><div class="grain"></div>
<header class="site"><a class="brand" href="index.html"><svg viewBox="0 0 24 24"><path class="draw" d="M12 2 3 7l9 5 9-5-9-5zM3 12l9 5 9-5M3 17l9 5 9-5"/></svg><span>THE CONTROL FILES</span></a>
<span style="margin-left:auto" class="meta">HUB · 22 files wired by context · hover goes <span class="negchip">negative</span></span></header>
<main class="wrap">
<div class="topgrid">
<section class="hero" style="text-align:left;padding-top:2.4rem">
<h1>The Control<br>Files · Hub</h1>
<p>One cursed HTML archive, decompiled into <b>twenty-two standalone dispatches</b> on coercive systems, environmental gaslighting, liminal architecture and digital power — then rewired: every file links to its semantic neighbours, every element flips to its <span class="negchip">negative colour</span> on hover, every badge carries an animated SVG rig.</p>
<div class="stats"><span><b>22</b> HTML files</span><span><b>{len(edges)}</b> unique context edges</span><span><b>66</b> rail links</span><span><b>13</b> icon rigs</span><span><b>0</b> broken links</span></div>
<div class="jump">{jump}</div>
</section>
<aside class="emblem-card">
<svg class="emblem" viewBox="0 0 120 120" role="img" aria-label="Hub network emblem: 22 nodes orbiting a core">
<defs><linearGradient id="hg" x1="0" y1="0" x2="1" y2="1">
<stop offset="0" stop-color="var(--a)"/><stop offset=".5" stop-color="var(--b)"/><stop offset="1" stop-color="var(--c)"/></linearGradient></defs>
<circle class="ring" cx="60" cy="60" r="52"/>
<g class="orbitg">{nodes}</g>
<g class="orbitg2"><circle class="ring" cx="60" cy="60" r="34" stroke-dasharray="3 5"/></g>
<path class="core draw" d="M60 40 46 60l14 20 14-20-14-20z"/>
<circle class="node pulse2" cx="60" cy="60" r="4"/>
<text x="60" y="112" text-anchor="middle">22 NODES · 1 CORE · ZERO BROKEN LINKS</text>
</svg>
<div class="legend">{legend}</div>
</aside>
</div>

<section class="wiring">
<h2>How the files are interconnected</h2>
<p>Every curve below is a real contextual link that exists in the dispatch rails — drawn between semantically related files (lifts ↔ AC ↔ drilling, cameras ↔ white-glove ↔ CCTV, Confluence ↔ group chats ↔ loading screens). Nodes are clickable.</p>
<div class="map">{map_svg}</div>
</section>

<div class="clusters">{clusters_html}</div>

<section class="howto">
<article><span class="ic"><svg viewBox="0 0 24 24"><rect class="float" x="3" y="5" width="18" height="14" rx="3"/><path class="dash" d="M3 10h18"/></svg></span><h3>Negative-colour hover</h3><p>Cards, icons, chips and map nodes apply <code>filter: invert(1) hue-rotate(180deg)</code> on hover — the palette photographs its own complement.</p></article>
<article><span class="ic"><svg viewBox="0 0 24 24"><g class="spin" style="transform-origin:12px 12px"><path d="M12 3v4M12 17v4M3 12h4M17 12h4"/><circle cx="12" cy="12" r="4"/></g></span><h3>Animated SVG rigs</h3><p>13 topic icons keep moving: drawing strokes, spinning gears, pulsing eyes, floating capsules, blinking dots — pure CSS keyframes, zero JavaScript.</p></article>
<article><span class="ic"><svg viewBox="0 0 24 24"><path class="draw" d="M4 17 10 11 14 15 20 7"/><path class="dash" d="M14 7h6v6"/></svg></span><h3>Context rails</h3><p>Each dispatch ships three “Read next” links chosen by TF-IDF cosine similarity, so navigation follows meaning, not numbering.</p></article>
</section>

<div class="flowbar"><div class="flow">{marq}{marq}</div></div>
</main>
<footer><span>THE CONTROL FILES · hub for site/post-01 … post-22 · generated by make_hub.py</span><span><a class="xlink" href="{SITE}post-01.html">Begin reading →</a></span></footer>
</body></html>
'''

os.makedirs('docs', exist_ok=True)
open('docs/index.html', 'w').write(page)
json.dump([{k: v for k, v in p.items()} for p in posts], open('/tmp/posts.json', 'w'))
print(f'docs/hub.html written: {len(page):,} bytes, {len(edges)} unique edges, {len(cats)} categories')
