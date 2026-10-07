#!/usr/bin/env python3
"""
build_blog.py — Analyze '22 blogs in 1 HTML file' and generate a modern,
single-file blog magazine using cutting-edge CSS (2026).

Heaviest GPU/compositor features used (this is the point):
  - backdrop-filter: blur() on hundreds of sticky, overlapping layers
  - position: sticky stacking contexts inside scroll-driven animations
  - @keyframes infinite animations on filter/transform/opacity (no will-change caps)
  - mix-blend-mode + isolation storms
  - SVG feTurbulence noise at viewport scale (CPU-side rasterization)
  - conic/radial gradients animated via registered custom properties (@property)
  - text-wrap: balance / hyphens on every block
"""

import re
import html as htmllib
from pathlib import Path
from bs4 import BeautifulSoup

SRC = Path("/workspace/22 blogs in 1 HTML file")
OUT = Path("/workspace/blog.html")

# ---------------------------------------------------------------- metadata
POST_HDR_RE = re.compile(r"POST\s+(\d+)/22:")


def parse_meta(raw: str):
    """Parse each post's banner comment block (tolerates truncated '-->' closings)."""
    posts = []
    for m in POST_HDR_RE.finditer(raw):
        # collect the banner: consecutive '<!--' lines starting at this header line
        line_start = raw.rfind("\n", 0, m.start()) + 1
        lines = []
        pos = line_start
        while True:
            nl = raw.find("\n", pos)
            line = raw[pos:] if nl == -1 else raw[pos:nl]
            if not line.lstrip().startswith("<!--"):
                break
            lines.append(line)
            if nl == -1 or len(lines) > 12:
                break
            pos = nl + 1

        def field(name):
            out, active = [], False
            for ln in lines:
                body = re.sub(r"^\s*<!--\s*", "", ln)
                if name == "POST":
                    mm = re.match(r"POST\s+\d+/22:\s*(.*)$", body)
                    if mm:
                        out.append(mm.group(1))
                    continue
                mm = re.match(r"([A-Z]+):\s*(.*)$", body)
                if mm and mm.group(1) != name:
                    active = False
                elif mm and mm.group(1) == name:
                    active = True
                    out.append(mm.group(2))
                elif active:
                    out.append(body)
            val = clean_multiline(" ".join(out))
            # drop banner artifacts like '============' that bleed into truncated closings
            val = re.sub(r"\s*=+\s*$", "", val).strip()
            return val

        posts.append({
            "num": int(m.group(1)),
            "htag": field("POST"),
            "url": field("URL"),
            "title": field("TITLE"),
            "permalink": field("PERMALINK") or f"post-{m.group(1)}",
            "labels": [l.strip().rstrip(".") for l in field("LABELS").split(",") if l.strip()][:6],
        })
    return posts


def clean_multiline(s: str) -> str:
    """Collapse continuation comment lines ('<!--        foo -->') into one string."""
    s = re.sub(r"<!--\s*", " ", s)
    s = re.sub(r"-->\s*", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return htmllib.unescape(s)


# ---------------------------------------------------------------- body split
def split_posts(raw: str, n_posts: int):
    """Return list of HTML fragment strings, one per post, by POST marker lines."""
    marker = re.compile(r"<!--\s*=+\s*-->\s*<!--\s*POST \d+/22", re.S)
    starts = [m.start() for m in marker.finditer(raw)]
    # last post runs to EOF (source is truncated mid-sentence; we close it gracefully)
    chunks = []
    for i, s in enumerate(starts):
        e = starts[i + 1] if i + 1 < len(starts) else len(raw)
        chunks.append(raw[s:e])
    return chunks


def strip_inline_styles(fragment_html: str) -> str:
    soup = BeautifulSoup(fragment_html, "lxml")
    body = soup.body or soup
    for tag in body.find_all(style=True):
        del tag["style"]
    for tag in body.find_all(["tbody", "thead"]):
        tag.decompose() if not tag.get_text(strip=True) else None
    # remove leading banner comment block (the ==== header)
    text = str(body)
    text = re.sub(r"^<!--[^>]*-->|^\s*<!--\s*=+[\s\S]*?=+\s*-->", "", text)
    # drop leftover single-line comments between sections (keep them as data-anchors? just remove)
    text = re.sub(r"<!-- SECTION \d+:.*?-->", "", text)
    text = re.sub(r"<!-- POST INTRO.*?-->", "", text)
    text = re.sub(r"<!--[^>]*-->", "", text)
    return text.strip()


def first_paragraph(frag: str) -> str:
    soup = BeautifulSoup(frag, "lxml")
    p = soup.find("p")
    if not p:
        return ""
    txt = p.get_text(" ", strip=True)
    return txt[:240] + ("…" if len(txt) > 240 else "")


def count_words(frag: str) -> int:
    soup = BeautifulSoup(frag, "lxml")
    return max(1, round(len(soup.get_text(" ").split()) / 200))  # ~ minutes


# ---------------------------------------------------------------- themes
THEMES = [
    {"id": "siam",     "name": "Bangkok Neon",   "a": "#ff2d95", "b": "#7b2dff", "c": "#00e5c7"},
    {"id": "vault",    "name": "Deep Vault",     "a": "#ffb347", "b": "#ff5e5b", "c": "#33ffe8"},
    {"id": "liminal",  "name": "Liminal Haze",   "a": "#8ef7ff", "b": "#b388ff", "c": "#fff59d"},
    {"id": "static",   "name": "Signal Static",  "a": "#39ff14", "b": "#00b3ff", "c": "#ff3860"},
    {"id": "terrazzo", "name": "Dark Terrazzo",  "a": "#f6d365", "b": "#fd6e6a", "c": "#84fab0"},
]


def derive_cat(title: str, labels: list[str]) -> str:
    t = (title + " " + " ".join(labels)).lower()
    if any(k in t for k in ["thai", "pronunciation", "accent", "english teaching"]):
        return "Language & Culture"
    if any(k in t for k in ["confluence", "digital power", "information architecture"]):
        return "Digital Power"
    if any(k in t for k in ["gaslighting", "environmental"]):
        return "Environmental Gaslighting"
    if any(k in t for k in ["coercion", "control", "enforcement", "security", "camera"]):
        return "Coercive Systems"
    if any(k in t for k in ["liminal", "construction", "exit", "autonomy", "safety"]):
        return "Liminal Spaces"
    if any(k in t for k in ["acoustic", "drilling", "noise", "air", "tenant"]):
        return "Domestic Rights"
    return "Power Dynamics"


# ---------------------------------------------------------------- page CSS
CSS = r"""
/* ============================ 2026 CSS: overkill edition ============================ */
@property --ang   { syntax:"<angle>";  inherits:true; initial-value:0deg }
@property --hueA  { syntax:"<number>"; inherits:true; initial-value:320 }
@property --hueB  { syntax:"<number>"; inherits:true; initial-value:265 }
@property --warp  { syntax:"<percentage>"; inherits:true; initial-value:0% }
@property --grain-x { syntax:"<length>"; inherits:false; initial-value:0px }

@property --a { syntax:"<color>"; inherits:true; initial-value:#ff2d95 }
@property --b { syntax:"<color>"; inherits:true; initial-value:#7b2dff }
@property --c { syntax:"<color>"; inherits:true; initial-value:#00e5c7 }

:root {
  color-scheme: dark;
  --bg: #05060f;
  --ink: #eef0ff;
  --muted: #a7abc9;
  --panel: rgba(255,255,255,.045);
  --line: rgba(255,255,255,.12);
  --radius: 22px;
  --font-display: ui-rounded, "SF Pro Rounded", "Nunito", system-ui, sans-serif;
  --font-body: Charter, "Iowan Old Style", Georgia, "Times New Roman", serif;
  --font-mono: ui-monospace, "JetBrains Mono", "Cascadia Code", monospace;
  view-transition-name: none;
}

* { box-sizing: border-box }

html { scroll-behavior: smooth; scrollbar-color: var(--a) transparent }

body {
  margin: 0;
  background: var(--bg);
  color: var(--ink);
  font-family: var(--font-body);
  font-size: clamp(1rem, .9rem + .4vw, 1.18rem);
  line-height: 1.72;
  overflow-x: clip;
  text-wrap: pretty;
  /* VRAM glutton #1: full-page animated gradient mesh under everything */
  background-image:
    radial-gradient(60vw 60vw at 12% 8%,  color-mix(in oklab, var(--a) 26%, transparent), transparent 60%),
    radial-gradient(55vw 55vw at 88% 22%, color-mix(in oklab, var(--b) 24%, transparent), transparent 62%),
    radial-gradient(70vw 70vw at 50% 96%, color-mix(in oklab, var(--c) 18%, transparent), transparent 65%),
    linear-gradient(conic-gradient(from var(--ang) at 50% 50%,
       color-mix(in oklab, var(--a) 10%, transparent),
       color-mix(in oklab, var(--b) 12%, transparent) 30%,
       color-mix(in oklab, var(--c) 10%, transparent) 60%,
       color-mix(in oklab, var(--a) 10%, transparent)),
     fixed);
  animation: spin-angle 24s linear infinite;
}
@keyframes spin-angle { to { --ang: 360deg } }

::selection { background: color-mix(in oklab, var(--a) 70%, black); color: white }

/* ---------- grain layer: SVG turbulence, blurred, blended, fullscreen, sticky ---------- */
.grain {
  position: fixed; inset: -20%;
  z-index: 40; pointer-events: none;
  opacity: .5; mix-blend-mode: overlay;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='100%25' height='100%25'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.84' numOctaves='4' stitchTiles='stitch'/%3E%3CfeColorMatrix type='saturate' values='0'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='0.55'/%3E%3C/svg%3E");
  animation: grain-shift 1.1s steps(6) infinite;
  will-change: transform, filter;
  filter: contrast(140%) brightness(90%);
}
@keyframes grain-shift {
  0%   { transform: translate3d(0,0,0) }
  20%  { transform: translate3d(-2%, 1.4%, 0) rotate(.3deg) }
  40%  { transform: translate3d(1.6%, -2%, 0) }
  60%  { transform: translate3d(-1%, 2%, 0) rotate(-.2deg) }
  80%  { transform: translate3d(2%, -1%, 0) }
  100% { transform: translate3d(0,0,0) }
}

/* ---------- aurora blobs: giant blurred orbs, infinite, GPU-melting ---------- */
.aurora { position: fixed; inset: 0; z-index: -1; overflow: clip; contain: strict; pointer-events: none }
.blob {
  position: absolute; width: 62vmax; height: 62vmax; border-radius: 43%;
  filter: blur(90px) saturate(190%) hue-rotate(0turn);
  mix-blend-mode: screen; opacity: .55;
  animation: blob-drift 19s ease-in-out infinite alternate, blob-hue 11s linear infinite;
  will-change: transform, filter;
}
.blob:nth-child(1){ background: radial-gradient(circle at 30% 30%, var(--a), transparent 65%); top:-18%; left:-12%; animation-duration: 21s, 9s }
.blob:nth-child(2){ background: radial-gradient(circle at 70% 40%, var(--b), transparent 65%); top:22%; right:-20%; animation-duration: 26s, 13s; animation-delay:-6s,-3s }
.blob:nth-child(3){ background: radial-gradient(circle at 40% 70%, var(--c), transparent 65%); bottom:-24%; left:18%; animation-duration: 17s, 15s; animation-delay:-9s,-7s }
.blob:nth-child(4){ background: conic-gradient(from 90deg, var(--a), var(--b), var(--c), var(--a)); top:44%; left:-26%; animation-duration: 31s, 8s; animation-delay:-14s,-5s; opacity:.4 }
@keyframes blob-drift { from { transform: translate3d(-6%, -4%, 0) rotate(0deg) scale(1) }
                        50%  { transform: translate3d(7%, 5%, 0) rotate(22deg) scale(1.25) }
                        to   { transform: translate3d(-9%, 8%, 0) rotate(-14deg) scale(.92) } }
@keyframes blob-hue { to { filter: blur(90px) saturate(190%) hue-rotate(1turn) } }

/* ---------- header ---------- */
.masthead {
  position: relative;
  padding: clamp(2.5rem, 8vh, 6rem) 1.4rem 3.2rem;
  text-align: center;
  isolation: isolate;
}
.kicker {
  font-family: var(--font-mono); letter-spacing: .34em; text-transform: uppercase;
  font-size: .78rem; color: var(--c);
}
.wordmark {
  font-family: var(--font-display);
  font-weight: 900;
  font-size: clamp(2.6rem, 9vw, 7.5rem);
  line-height: .98; margin: .35em 0 .25em;
  text-wrap: balance;
  background: linear-gradient(100deg, var(--a), var(--b) 45%, var(--c));
  background-size: 220% 100%;
  -webkit-background-clip: text; background-clip: text; color: transparent;
  animation: shimmer 6s ease-in-out infinite alternate;
  filter: drop-shadow(0 0 26px color-mix(in oklab, var(--b) 45%, transparent));
}
@keyframes shimmer { to { background-position: 100% 0 } }
.tagline { max-width: 56ch; margin-inline:auto; color: var(--muted); font-style: italic }

.stats { display:flex; gap:.8rem; justify-content:center; flex-wrap:wrap; margin-top:1.6rem }
.stat {
  padding:.5rem 1.05rem; border-radius:999px;
  border:1px solid var(--line);
  background: color-mix(in oklab, var(--panel), transparent 20%);
  backdrop-filter: blur(14px) saturate(160%);
  -webkit-backdrop-filter: blur(14px) saturate(160%);
  font-family: var(--font-mono); font-size:.8rem; color:var(--ink);
  box-shadow: 0 10px 30px -18px color-mix(in oklab, var(--a) 60%, transparent);
}
.stat b { color: var(--c) }

/* ---------- theme chips ---------- */
.themes { position:relative; z-index:60; display:flex; gap:.6rem; justify-content:center; flex-wrap:wrap; padding: 0 1rem 2rem }
.chip-theme {
  cursor:pointer; border:1px solid var(--line); border-radius:999px; padding:.45rem .95rem;
  font-family:var(--font-mono); font-size:.78rem; color:var(--ink);
  background:
    linear-gradient(var(--bg),var(--bg)) padding-box,
    linear-gradient(120deg, var(--ta), var(--tb)) border-box;
  transition: translate .25s, scale .25s;
}
.chip-theme:hover { translate:0 -3px; scale:1.06 }
.chip-theme[aria-pressed="true"] { background: linear-gradient(120deg, var(--ta), var(--tb)); color:#07081a; font-weight:700 }

/* ---------- nav / TOC (sticky glass) ---------- */
nav.toc {
  position: sticky; top: 0; z-index: 50;
  display:flex; gap:.5rem; align-items:center;
  overflow-x:auto; scrollbar-width:none;
  padding:.7rem 1rem;
  background: color-mix(in oklab, var(--bg) 55%, transparent);
  backdrop-filter: blur(22px) saturate(180%) brightness(1.15);
  -webkit-backdrop-filter: blur(22px) saturate(180%) brightness(1.15);
  border-block: 1px solid var(--line);
}
nav.toc::-webkit-scrollbar{ display:none }
nav.toc a {
  flex:0 0 auto; text-decoration:none; color:var(--muted);
  font-family:var(--font-mono); font-size:.74rem; letter-spacing:.04em;
  padding:.42rem .8rem; border-radius:999px; border:1px solid transparent;
  transition: color .2s, border-color .2s, background .2s;
}
nav.toc a:hover, nav.toc a:focus-visible {
  color: var(--ink); border-color: var(--line);
  background: color-mix(in oklab, var(--a) 16%, transparent);
}
nav.toc .brand { font-weight:800; color:var(--a); font-family:var(--font-display); padding-right:.6rem; white-space:nowrap }

/* reading progress via scroll-driven animation */
.progress {
  position: fixed; inset: 0 0 auto 0; height: 4px; z-index: 70;
  background: linear-gradient(90deg, var(--a), var(--b), var(--c));
  transform-origin: 0 50%;
  animation: grow linear both;
  animation-timeline: scroll(root block);
}
@keyframes grow { from { transform: scaleX(0) } to { transform: scaleX(1) } }

/* ---------- layout ---------- */
main { max-width: 1240px; margin-inline: auto; padding: 1.2rem clamp(1rem, 3vw, 2rem) 4rem }

h2.section-title {
  font-family: var(--font-display); font-weight: 900;
  font-size: clamp(1.5rem, 1.1rem + 2vw, 2.4rem);
  margin: 3.4rem 0 1.4rem; text-wrap: balance;
  position: sticky; top: 3.4rem; z-index: 5;
  backdrop-filter: blur(10px);
  width: fit-content; padding: .2rem .9rem; border-radius: 999px;
  background: color-mix(in oklab, var(--bg) 60%, transparent);
  border: 1px solid var(--line);
}

/* card grid with container queries */
.grid {
  display: grid; gap: 1.2rem;
  grid-template-columns: repeat(auto-fill, minmax(min(340px, 100%), 1fr));
  container-type: inline-size;
}
@container (min-width: 900px) { .grid { gap: 1.5rem } }

article.card {
  --i: sibling-index();
  position: relative;
  border-radius: var(--radius);
  border: 1px solid var(--line);
  background: color-mix(in oklab, var(--panel) 70%, transparent);
  backdrop-filter: blur(18px) saturate(150%);
  -webkit-backdrop-filter: blur(18px) saturate(150%);
  padding: 1.4rem 1.4rem 1.2rem;
  overflow: clip;
  display: flex; flex-direction: column; gap: .8rem;
  transition: transform .5s cubic-bezier(.2,.9,.2,1), box-shadow .5s, border-color .5s;
  animation: card-pop .8s cubic-bezier(.2,.9,.25,1.2) both;
  animation-delay: calc(var(--i) * 90ms);
}
@keyframes card-pop { from { opacity:0; transform: translateY(26px) scale(.96) rotateX(12deg) } }
article.card:hover {
  transform: translateY(-6px) rotate3d(1,-1,0,2.5deg);
  border-color: color-mix(in oklab, var(--a) 55%, var(--line));
  box-shadow:
    0 30px 60px -30px color-mix(in oklab, var(--b) 55%, transparent),
    0 0 0 1px color-mix(in oklab, var(--a) 25%, transparent) inset;
}
/* VRAM glutton #2: animated chromatic aura behind each card */
article.card::before {
  content:""; position:absolute; inset:-40%;
  background: conic-gradient(from calc(var(--ang) * 2), var(--a), var(--b), var(--c), var(--a));
  filter: blur(60px) saturate(180%);
  opacity:.16; z-index:-1;
  animation: halo 9s linear infinite;
  mix-blend-mode: plus-lighter;
}
@keyframes halo { to { rotate: 360deg } }

.card .num {
  font-family: var(--font-mono); font-size:.72rem; letter-spacing:.2em;
  color: var(--c); text-transform: uppercase;
  display:flex; justify-content:space-between; align-items:center; gap:.6rem;
}
.card h3 { font-family: var(--font-display); font-size: 1.28rem; line-height:1.25; margin:0; text-wrap: balance }
.card h3 a { color: inherit; text-decoration: none }
.card h3 a::after { content:""; position:absolute; inset:0; border-radius: var(--radius) }
.card p.excerpt { color: var(--muted); font-size:.95rem; margin:0; display:-webkit-box; -webkit-line-clamp:4; -webkit-box-orient:vertical; overflow:hidden }
.badges { display:flex; flex-wrap:wrap; gap:.4rem; margin-top:auto }
.badge {
  font-family: var(--font-mono); font-size:.68rem; padding:.28rem .6rem; border-radius:8px;
  background: color-mix(in oklab, var(--b) 22%, transparent);
  border:1px solid color-mix(in oklab, var(--b) 40%, transparent);
  color: color-mix(in oklab, var(--b) 70%, white);
  transition: translate .2s;
}
.card:hover .badge { animation: badge-float 2.4s ease-in-out infinite; animation-delay: calc(var(--i) * 120ms) }
@keyframes badge-float { 50% { translate: 0 -3px } }
.meta-row { display:flex; gap:.9rem; font-family:var(--font-mono); font-size:.7rem; color:var(--muted) }

/* ---------- long-form post sections ---------- */
.post {
  margin-top: 4rem;
  border-radius: calc(var(--radius) + 8px);
  border: 1px solid var(--line);
  background:
    linear-gradient(color-mix(in oklab, var(--bg) 72%, transparent), color-mix(in oklab, var(--bg) 88%, transparent)),
    repeating-linear-gradient(115deg, transparent 0 26px, color-mix(in oklab, var(--b) 6%, transparent) 26px 27px);
  backdrop-filter: blur(26px) saturate(160%);
  -webkit-backdrop-filter: blur(26px) saturate(160%) brightness(1.05);
  box-shadow: 0 40px 120px -50px color-mix(in oklab, var(--a) 40%, transparent);
  padding: clamp(1.4rem, 4vw, 3.4rem);
  position: relative;
  overflow: clip;
  /* scroll-driven reveal */
  animation: reveal linear both;
  animation-timeline: view();
  animation-range: entry 0% cover 28%;
}
@keyframes reveal { from { opacity:.15; transform: translateY(40px) scale(.985); filter: blur(6px) } }

.post-head { position: relative; margin-bottom: 2rem; isolation: isolate }
.post-head .idx {
  font-family: var(--font-display); font-weight: 900;
  font-size: clamp(4rem, 12vw, 9rem); line-height:.8;
  position:absolute; right:0; top:-.35em; z-index:-1;
  color: transparent;
  -webkit-text-stroke: 2px color-mix(in oklab, var(--a) 50%, transparent);
  animation: idx-pulse 5s ease-in-out infinite;
}
@keyframes idx-pulse { 50% { -webkit-text-stroke-color: color-mix(in oklab, var(--c) 60%, transparent); transform: scale(1.02) } }
.post h1.title {
  font-family: var(--font-display); font-weight: 900;
  font-size: clamp(1.7rem, 1.2rem + 2.6vw, 3rem);
  line-height: 1.08; text-wrap: balance; margin: 0 0 .8rem;
  background: linear-gradient(120deg, var(--ink) 30%, color-mix(in oklab, var(--a) 85%, white));
  -webkit-background-clip: text; background-clip: text; color: transparent;
}
.post .subline { color: var(--muted); font-family: var(--font-mono); font-size:.78rem; display:flex; flex-wrap:wrap; gap:1rem }
.post .subline a { color: var(--c) }

.prose { columns: 1; }
@supports (not (-webkit-touch-callout: none)) {
  @media (min-width: 1100px) { .prose.two-col { column-count: 2; column-gap: 2.6rem; column-rule: 1px dashed color-mix(in oklab, var(--b) 40%, transparent) } }
}
.prose > *:first-child { margin-top: 0 }
.prose h2 {
  font-family: var(--font-display); font-size: clamp(1.3rem, 1rem + 1.4vw, 1.8rem);
  margin: 2.2em 0 .6em; text-wrap: balance;
  padding-left: .9rem;
  border-left: .32rem solid;
  border-image: linear-gradient(180deg, var(--a), var(--c)) 1;
}
.prose h3 { font-family: var(--font-display); font-size: 1.22rem; margin: 1.8em 0 .5em; color: color-mix(in oklab, var(--c) 75%, white); text-wrap: balance }
.prose h4 { font-family: var(--font-mono); font-size: .82rem; letter-spacing: .14em; text-transform: uppercase; color: var(--muted); margin: 1.6em 0 .5em }
.prose p { margin: 0 0 1.1em; hyphens: auto; max-width: 74ch }
.prose strong { color: color-mix(in oklab, var(--a) 60%, white) }
.prose em { color: color-mix(in oklab, var(--c) 50%, var(--ink)) }
.prose ul, ol { padding-inline-start: 1.3em; margin: 0 0 1.2em; max-width: 72ch }
.prose li { margin-bottom: .45em }
.prose li::marker { color: var(--a); font-weight: 700 }
.prose a { color: var(--c); text-decoration: underline dotted from-color 2px; text-underline-offset: 3px }
.prose hr { border:0; height:1px; background:linear-gradient(90deg, transparent, var(--line), transparent); margin:2.4rem 0 }

.prose table {
  width: 100%; border-collapse: separate; border-spacing: 0;
  margin: 1.4rem 0 1.8rem; font-size: .92rem;
  border-radius: 14px; overflow: clip;
  border: 1px solid var(--line);
  background: color-mix(in oklab, var(--panel), transparent 30%);
  backdrop-filter: blur(8px);
}
.prose th {
  font-family: var(--font-mono); font-size:.74rem; letter-spacing:.08em; text-transform:uppercase;
  text-align:left; padding:.7rem .8rem;
  background: linear-gradient(120deg, color-mix(in oklab, var(--a) 30%, transparent), color-mix(in oklab, var(--b) 30%, transparent));
}
.prose td { padding: .7rem .8rem; border-top: 1px solid var(--line); vertical-align: top }
.prose tr { transition: background .2s }
.prose tbody tr:hover { background: color-mix(in oklab, var(--c) 9%, transparent) }

blockquote {
  margin: 1.6rem 0; padding: 1rem 1.4rem;
  border-radius: 16px;
  border: 1px solid color-mix(in oklab, var(--b) 45%, transparent);
  background: color-mix(in oklab, var(--b) 12%, transparent);
  font-style: italic; color: color-mix(in oklab, var(--ink) 88%, var(--b));
  position: relative;
}
blockquote::before {
  content: "“"; position:absolute; top:-.18em; left:.2rem;
  font-size: 3.4em; font-family: var(--font-display);
  color: color-mix(in oklab, var(--b) 40%, transparent);
  mix-blend-mode: screen;
}

/* floating back-to-top with morph */
a.top-link {
  position: fixed; right: 1.1rem; bottom: 1.1rem; z-index: 65;
  width: 52px; height: 52px; display: grid; place-items: center;
  border-radius: 30% 70% 70% 30% / 30% 30% 70% 70%;
  background: linear-gradient(140deg, var(--a), var(--b));
  color: #0a0b1e; font-weight: 900; text-decoration: none; font-family: var(--font-display);
  backdrop-filter: blur(6px);
  box-shadow: 0 12px 40px -10px color-mix(in oklab, var(--a) 70%, transparent);
  animation: morph 6s ease-in-out infinite, bob 3s ease-in-out infinite;
}
@keyframes morph {
  0%,100% { border-radius: 30% 70% 70% 30% / 30% 30% 70% 70% }
  33%     { border-radius: 60% 40% 30% 70% / 60% 30% 70% 40% }
  66%     { border-radius: 40% 60% 70% 30% / 40% 70% 30% 60% }
}
@keyframes bob { 50% { translate: 0 -7px } }

footer.colophon {
  margin-top: 5rem; padding: 2.4rem 1.4rem; text-align:center;
  border-top: 1px solid var(--line);
  background: color-mix(in oklab, var(--panel), transparent 40%);
  backdrop-filter: blur(16px);
}
footer .css-list { display:flex; flex-wrap:wrap; gap:.5rem; justify-content:center; margin-top:1rem }
footer code {
  font-family: var(--font-mono); font-size:.72rem; padding:.3rem .6rem; border-radius:8px;
  background: color-mix(in oklab, var(--c) 14%, transparent); border:1px solid color-mix(in oklab, var(--c) 35%, transparent);
  color: color-mix(in oklab, var(--c) 80%, white);
}

/* reduced motion mercy */
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after { animation-duration: .01ms !important; animation-iteration-count: 1 !important; transition-duration: .01ms !important }
  .grain, .aurora { display: none }
}

@media print { .grain, .aurora, nav.toc, .progress, a.top-link { display:none } body{background:#fff;color:#000} }
"""

JS = r"""
// Theme switcher: writes custom properties on :root (animated via @property)
const THEMES = %THEMES_JSON%;
const root = document.documentElement;
function setTheme(id){
  const t = THEMES.find(x=>x.id===id)||THEMES[0];
  root.style.setProperty('--a', t.a);
  root.style.setProperty('--b', t.b);
  root.style.setProperty('--c', t.c);
  document.querySelectorAll('.chip-theme').forEach(c=>
    c.setAttribute('aria-pressed', String(c.dataset.theme===id)));
  try{ localStorage.setItem('blog-theme', id);}catch(e){}
}
document.addEventListener('click', e=>{
  const chip = e.target.closest('.chip-theme');
  if(chip) setTheme(chip.dataset.theme);
});
let saved=null; try{saved=localStorage.getItem('blog-theme')}catch(e){}
setTheme(saved || (matchMedia('(prefers-color-scheme: light)').matches ? THEMES[2].id : THEMES[0].id));

// Popularity: animate word counts when visible
if (HTMLViewTransitions=false, 'animate' in Element.prototype && matchMedia('(display-mode: browser)').matches){
  // nothing extra — CSS scroll-driven animations do the heavy lifting
}
""".replace("HTMLViewTransitions=false, ", "")


def esc(s: str) -> str:
    return htmllib.escape(s, quote=True)


def build():
    raw = SRC.read_text(encoding="utf-8", errors="replace")
    posts = parse_meta(raw)
    frags = split_posts(raw, len(posts))
    assert len(posts) == len(frags), f"{len(posts)} meta vs {len(frags)} fragments"

    cleaned = []
    for p, f in zip(posts, frags):
        body = strip_inline_styles(f)
        p["body"] = body
        p["excerpt"] = first_paragraph(body)
        p["mins"] = count_words(body)
        p["cat"] = derive_cat(p["title"], p["labels"])
        p["theme"] = THEMES[(p["num"] - 1) % len(THEMES)]
        cleaned.append(p)

    total_words = sum(count_words(p["body"]) for p in cleaned) * 200

    # ---------------- TOC ----------------
    toc_links = "\n".join(
        f'<a href="#post-{p["num"]}">{p["num"]:02d} · {esc(p["htag"][:38])}</a>' for p in cleaned
    )

    # ---------------- featured cards ----------------
    def card(p):
        badges = "".join(f'<span class="badge">{esc(l)}</span>' for l in p["labels"][:4])
        return f"""
      <article class="card" id="c{p['num']}" style="--ta:{p['theme']['a']};--tb:{p['theme']['b']}">
        <div class="num"><span>Post {p['num']:02d}/22</span><span>{esc(p['cat'])}</span></div>
        <h3><a href="#post-{p['num']}">{esc(p['title'])}</a></h3>
        <p class="excerpt">{esc(p['excerpt'])}</p>
        <div class="meta-row"><span>⏱ {p['mins']} min read</span><span>🔗 {esc(p['permalink'][:34])}</span></div>
        <div class="badges">{badges}</div>
      </article>"""

    featured = "\n".join(card(p) for p in cleaned[:10])
    more = "\n".join(card(p) for p in cleaned[10:])

    # ---------------- full posts ----------------
    full = []
    for p in cleaned:
        labels = " · ".join(esc(l) for l in p["labels"]) or "&nbsp;"
        two_col = ' two-col' if p["num"] % 2 == 0 else ''
        full.append(f"""
    <section class="post" id="post-{p['num']}">
      <header class="post-head">
        <span class="idx">{p['num']:02d}</span>
        <h1 class="title">{esc(p['title'])}</h1>
        <div class="subline">
          <span>◈ {esc(p['cat'])}</span>
          <span>⏱ {p['mins']} min</span>
          <span>🏷 {labels}</span>
          <a href="{esc(p['url'])}">original URL</a>
          <a href="#top">↑ index</a>
        </div>
      </header>
      <div class="prose{two_col}">
        {p['body']}
      </div>
    </section>""")

    theme_chips = "\n".join(
        f'<button class="chip-theme" data-theme="{t["id"]}" style="--ta:{t["a"]};--tb:{t["b"]}" aria-pressed="false">{t["name"]}</button>'
        for t in THEMES
    )

    import json
    js = JS.replace("%THEMES_JSON%", json.dumps(THEMES))

    page = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="color-scheme" content="dark light">
<meta name="description" content="Wordformanipulativebehavior — 22 essays on coercive systems, environmental gaslighting, liminal spaces, and language. Rendered with maximum-CSS 2026.">
<meta property="og:title" content="THE CONTROL FILES — 22 Essays in One Page">
<meta property="og:description" content="A single-page magazine of 22 SEO essays powered by 2026's heaviest CSS: scroll-driven animations, backdrop-filter stacks, @property gradients and turbulence grain.">
<title>THE CONTROL FILES · 22 Essays on Power, Gaslighting & Liminal Spaces</title>
<style>{CSS}</style>
</head>
<body id="top">

<div class="aurora" aria-hidden="true">
  <div class="blob"></div><div class="blob"></div><div class="blob"></div><div class="blob"></div>
</div>
<div class="grain" aria-hidden="true"></div>
<div class="progress" aria-hidden="true"></div>

<header class="masthead">
  <p class="kicker">wordformanipulativebehavior · consolidated archive · aug 2026</p>
  <h1 class="wordmark">THE&nbsp;CONTROL&nbsp;FILES</h1>
  <p class="tagline">Twenty-two field guides to coercive architecture — from Thai-accent love stories in Bangkok to elevators that gaslight, drills that dominate, and vents that lie.</p>
  <div class="stats">
    <span class="stat"><b>22</b> essays</span>
    <span class="stat"><b>~{total_words:,}</b> words</span>
    <span class="stat"><b>{sum(p['mins'] for p in cleaned)}</b> min total read</span>
    <span class="stat">one <b>insane</b> CSS page</span>
  </div>
</header>

<div class="themes" role="group" aria-label="Color theme">{theme_chips}</div>

<nav class="toc" aria-label="Table of contents">
  <span class="brand">☰ INDEX</span>
  {toc_links}
</nav>

<main>
  <h2 class="section-title">✦ Featured Dispatches</h2>
  <div class="grid">{featured}</div>

  <h2 class="section-title">✦ The Back Half</h2>
  <div class="grid">{more}</div>

  <h2 class="section-title">✦ Full Text — All Twenty-Two</h2>
  {''.join(full)}
</main>

<a class="top-link" href="#top" aria-label="Back to top">↑</a>

<footer class="colophon">
  <p style="font-family:var(--font-display);font-weight:900;font-size:1.3rem">Rendered with CSS that asked for forgiveness, not permission.</p>
  <p style="color:var(--muted)">Source analyzed: <code style="font-size:.8rem">22 blogs in 1 HTML file</code> — all 22 posts parsed, de-styled, and re-cast in semantic HTML.</p>
  <div class="css-list">
    <code>@property</code><code>scroll-driven animations</code><code>animation-timeline: view()</code>
    <code>backdrop-filter ×∞</code><code>sibling-index()</code><code>container queries</code>
    <code>color-mix(in oklab)</code><code>text-wrap: balance</code><code>conic-gradient halos</code>
    <code>SVG feTurbulence grain</code><code>mix-blend-mode: plus-lighter</code><code>view transitions ready</code>
  </div>
</footer>

<script>{js}</script>
</body>
</html>
"""
    OUT.write_text(page, encoding="utf-8")
    print(f"Wrote {OUT} ({len(page):,} bytes)")
    print(f"Parsed posts: {len(cleaned)}")
    for p in cleaned:
        print(f"  {p['num']:02d}. [{p['cat']}] {p['title'][:70]}… ({p['mins']} min)")


if __name__ == "__main__":
    build()
