#!/usr/bin/env python3
"""
fix_titles.py — convert hub titles into CSS title-cards + repair broken markup.

1. Every <h2> cluster heading and every <h3> post-title in index.html /
   index-copy.html becomes a self-contained CSS "title card":
     h2 -> .tcard.cat   (glass panel, animated gradient border via @property)
     h3 -> .tcard.post  (negative-colour hover + glide right, container query)
   Text is wrapped in <span class="tt"> so the card chrome animates, not glyphs.
2. Repairs:
   - escaped literal `&lt;span&gt;...` junk inside headings (was rendering as
     visible "<span>" text = the "broken" look) -> real <span class="badge">
   - footer text `site/post-01 … post-22` -> clickable flat links
   - same repairs mirrored in root workspace copies & blog-index-hub.html
3. Injects the .tcard CSS block once per file (idempotent marker).
"""
import re, glob, os

MARK = "/* TCARD-TITLES v1 */"

CARD_CSS = """
__MARK__
/* ===================== TITLE CARDS (h2/h3 -> CSS cards) ===================== */
@property --tc-a { syntax:"<angle>"; inherits:false; initial-value:0deg }
@property --tc-x { syntax:"<percentage>"; inherits:false; initial-value:0% }
.tcard{ position:relative; isolation:isolate; display:block; width:fit-content;
  max-width:100%; margin:0 auto 1.4rem; padding:.85rem 1.5rem; border-radius:16px;
  background:color-mix(in oklab,#171325 82%,transparent);
  backdrop-filter:blur(14px) saturate(1.5);
  border:1px solid color-mix(in oklab,var(--ink) 12%,transparent);
  box-shadow:0 10px 30px -18px #000, inset 0 0 0 1px color-mix(in oklab,var(--b) 10%,transparent);
  transition:translate .35s cubic-bezier(.2,.9,.3,1.4), rotate .35s ease, scale .35s ease;
}
/* animated gradient ring drawn from registered custom angle */
.tcard::before{ content:""; position:absolute; inset:-1.5px; z-index:-1; border-radius:inherit;
  background:conic-gradient(from var(--tc-a),var(--a),var(--b),var(--c),var(--a));
  filter:blur(1px); opacity:.55; animation:tspin 6s linear infinite; }
.tcard::after{ content:""; position:absolute; inset:0; z-index:-1; border-radius:inherit;
  background:linear-gradient(115deg at var(--tc-x) 50%,
    transparent 0 42%, color-mix(in oklab,#fff 26%,transparent) 50%, transparent 58% 100%);
  animation:tsheen 4.5s ease-in-out infinite; opacity:0; transition:opacity .3s }
@keyframes tspin{ to{ --tc-a:360deg } }
@keyframes tsheen{ 0%{--tc-x:0%} 55%,100%{--tc-x:140%} }
.tcard .tt{ font:inherit; }
/* negative colour on hover + glide a few degrees right */
.tcard:hover{ filter:invert(1) hue-rotate(180deg) contrast(1.3) saturate(1.5);
  mix-blend-mode:difference; translate:12px 0; rotate:1.4deg; scale:1.03 }
.tcard:hover::after{ opacity:1 }
.tcard.cat{ text-align:center }
.tcard.cat .tt{ display:inline-block; font-size:clamp(1.15rem,2.6vw,1.7rem); letter-spacing:-.01em;
  background:linear-gradient(100deg,var(--a),var(--b) 55%,var(--c));
  -webkit-background-clip:text; background-clip:text; color:transparent }
.tcard.post{ margin:0 0 .55rem; padding:.55rem 1rem; width:100% }
.tcard.post .tt{ font-size:1.02rem; line-height:1.3; text-wrap:balance; color:var(--ink) }
.badge{ display:inline-flex; gap:.35ch; margin-left:.6rem; vertical-align:.12em;
  font:700 .62rem/1 var(--fd,inherit); letter-spacing:.08em; text-transform:uppercase;
  color:#0b0916; background:linear-gradient(100deg,var(--b),var(--c));
  padding:.32em .6em; border-radius:99px; white-space:nowrap }
@container (max-width:520px){ .tcard{ width:100% } .tcard.cat{ margin-inline:auto } }
@media (prefers-reduced-motion:reduce){ .tcard::before,.tcard::after{ animation:none } }
""".replace("__MARK__", MARK)

def inject_css(html: str) -> str:
    if MARK in html:
        return html
    i = html.find("</style>")
    if i == -1:
        return html
    return html[:i] + CARD_CSS + "\n" + html[i:]

BAD_SPAN = re.compile(r'&lt;span&gt;([^<]*?)</span>')          # escaped junk w/ close tag
BAD_SPAN_OPEN = re.compile(r'&lt;span&gt;([^<]*?)(?=</h[1-6]>)')  # escaped junk, no close

def fix_junk(html: str) -> str:
    def rep(m):
        txt = m.group(1).strip()
        return f'<span class="badge">{txt}</span>'
    out = BAD_SPAN.sub(rep, html)
    out = BAD_SPAN_OPEN.sub(lambda m: f'<span class="badge">{m.group(1).strip()}</span>', out)
    return out

H2 = re.compile(r'<h2(?P<attrs>[^>]*)>(?P<body>.*?)</h2>', re.S)
H3 = re.compile(r'<h3(?P<attrs>[^>]*)>(?P<body>.*?)</h3>', re.S)

def mk(cls):
    """regex replacer: turn an h2/h3 into a CSS title-card."""
    def r(m):
        body = m.group('body').strip()
        # unwrap legacy <span class="t">title</span>
        body = re.sub(r'^<span class="t">(.*?)</span>$', r'\1', body, flags=re.S)
        badges = re.findall(r'<span class="badge">.*?</span>', body)
        plain = re.sub(r'<span class="badge">.*?</span>', '', body, flags=re.S)
        plain = re.sub(r'<[^>]+>', '', plain).strip()
        tag = m.group(0)[1:3]  # 'h2' / 'h3'
        return (f'<{tag}{m.group("attrs")}>'
                f'<span class="tcard {cls}" role="presentation">'
                f'<span class="tt">{plain}</span>{"".join(badges)}'
                f'</span></{tag}>')
    return r

FOOTER_OLD = 'THE CONTROL FILES · hub for site/post-01 … post-22 · generated by make_hub.py'
FOOTER_NEW = ('THE CONTROL FILES · hub for '
              '<a class="xlink" href="post-01.html">post-01</a> … '
              '<a class="xlink" href="post-22.html">post-22</a> · generated by make_hub.py')

def process(path: str):
    html = open(path).read()
    orig = html
    html = fix_junk(html)                       # escaped-span junk -> real badges
    html = html.replace(FOOTER_OLD, FOOTER_NEW) # dead footer text -> live links
    if 'hubcard' in html or 'class="cluster"' in html:
        html = H2.sub(mk('cat'), html)          # cluster titles  -> cards
        html = H3.sub(mk('post'), html)         # dispatch titles -> cards
    html = inject_css(html)
    if html != orig:
        open(path, 'w').write(html)
        print("fixed:", path)

for pat in ("Qwen3-8-MAX-blogs/index.html", "Qwen3-8-MAX-blogs/index-copy.html",
            "index.html", "index-copy.html", "blog-index-hub.html"):
    p = os.path.join("/workspace", pat)
    if os.path.exists(p):
        process(p)
print("done")
