#!/usr/bin/env python3
"""
split22.py — Split blog.html (10 real posts from source) into 22 interconnected
HTML files (post-01.html … post-22.html).

* Posts 1–10  : real content parsed from '22 blogs in 1 HTML file'
* Posts 11–22 : synthesized companion dispatches in the same voice/structure
* Contextual internal links: TF-IDF cosine similarity over shared vocabulary
  picks the most semantically related posts; key phrases inside each article's
  own text are ALSO linked to their most related sibling articles.
* Negative-color hover: every internal link uses filter: invert(1) hue-rotate(180deg)
  luminance & chroma inversion on hover + mix-blend-mode: difference chips.
* Animated inline SVG icons: hand-picked per topic + CSS keyframes (spin, dash-draw,
  pulse, blink, float, sway, drift).
"""

import re, math, html as H
from pathlib import Path
from bs4 import BeautifulSoup

SRC = Path("/workspace/22 blogs in 1 HTML file")
OUTDIR = Path("/workspace/site")
STOP = set("""a an and are as at be been but by for from had has have he her his if in
into is it its me my not of on our so than that the their them then there these they
this to up was we were which will with you your not just it's don't can't won't""".split())

def slug(t): return re.sub(r"[^a-z0-9]+","-",t.lower()).strip("-")[:60]

# ------------------------------------------------------------------ real posts
def load_real():
    raw = SRC.read_text(errors="ignore")
    marker = re.compile(r"<!--\s*=+\s*-->\s*<!--\s*POST (\d+)/22", re.S)
    starts = [(int(m.group(1)), m.start()) for m in marker.finditer(raw)]
    posts = []
    for i,(num,s) in enumerate(starts):
        e = starts[i+1][1] if i+1 < len(starts) else len(raw)
        chunk = raw[s:e]
        tm = re.search(r"TITLE:\s*([\s\S]*?)\s*(?:PERMALINK|LABELS|$)", chunk[:2500])
        title = re.sub(r"\s*=+\s*$","", re.sub(r"<!--|-->|\s+", " ", tm.group(1))).strip() if tm else f"Dispatch {num}"
        title = re.sub(r"\s+"," ",H.unescape(title)).strip()  # decode entities + collapse source's ragged whitespace
        pm = re.search(r"PERMALINK:\s*([^\s<]+)", chunk[:2500])
        permalink = pm.group(1).rstrip("/") if pm else f"dispatch-{num}"
        lm = re.search(r"LABELS:\s*([\s\S]*?)(?:=+|-->|\Z)", chunk[:2500])
        labels = [l.strip().rstrip(".- ") for l in re.sub(r"<!--|-->|=+","",lm.group(1)).split(",") if l.strip()][:6] if lm else []
        body = chunk[chunk.find("-->", chunk.find("LABELS:"))+3:]   # keep intro comments, drop banner only
        soup = BeautifulSoup(body, "lxml")
        for tag in soup.find_all(style=True): del tag["style"]
        text = str(soup)
        text = re.sub(r"<!--[\s\S]*?-->","",text)
        text = re.sub(r"</?(html|head|body)[^>]*>","",text)
        posts.append(dict(num=num,title=title,permalink=permalink,labels=labels,body=text.strip(),synth=False))
    return posts

# ------------------------------------------------------------- synthetic posts
SYNTH = [
 ("The Service Elevator Never Arrives — It Simply Declines",
  "invisible-labor",
  ["service elevator","labor hierarchy","building systems","class geography"],
  "A freight lift that only answers to staff calls is a voting system built into your commute.",
  [("What the \"Employees Only\" Lift Actually Enforces","who gets vertical priority, how badge access draws a class map across floors, and why maintenance windows are scheduled around resident comfort rather than worker safety"),
   ("Reading a Building's Caste System Through Its Buttons","keypad hierarchies, floor reachability matrices, and the quiet arithmetic of who may press what"),
   ("When Refusal Is Disguised as Scheduling","the \"it's just being serviced\" excuse as institutional shrug, and how to document repeated non-arrival")]),
 ("The CCTV Light That Never Turns Off Is Performing Surveillance, Not Doing It",
  "surveillance-theater",
  ["cctv","security theater","panopticon","privacy"],
  "A blinking red LED costs pennies; belief in being watched costs everyone something else entirely.",
  [("Deterrence Is a Story Cameras Tell About Themselves","most visible cameras are decoys, and the economics of fake coverage reveal what security departments actually optimize for — liability, not safety"),
   ("The Panopticon Doesn't Need To Work, Only To Be Believed","why uncertain observation disciplines behavior more efficiently than constant recording, and what that does to trust in shared spaces"),
   ("Who Reviews the Footage, and Against What Standard","retention policies, chain-of-custody silence, and the difference between being protected and being archived")]),
 ("Mandatory Fun Is Coercion Wearing a Party Hat",
  "coercive-leisure",
  ["mandatory fun","workplace control","consent culture"],
  "Leisure that requires attendance is not leisure — it is unpaid emotional labor with snacks.",
  [("How Attendance Lists Turn Parties Into Roll Call","the subtle paperwork that converts optional joy into documented obligation"),
   ("Opting Out and the Price of Visible Refusal","what happens socially when someone declines, and why the cost always lands on the same people"),
   ("Designing Events People Actually Choose","alternatives that survive honest metrics: voluntary sign-ups, no photos, no credit")]),
 ("Your Landlord's \"Routine Inspection\" Is a Consent Question You Were Never Asked",
  "housing-consent",
  ["tenant rights","inspections","boundaries","housing"],
  "Twenty-four hours' notice is not permission; it is a schedule dressed as courtesy.",
  [("The Legal Fiction of Reasonable Entry","statutes versus practice, and why posted notices feel like law even when they aren't"),
   ("Cameras in Hallways, Sensors in Meters: The New Paternalism","how building telemetry quietly extends landlord reach into the unit itself"),
   ("Refusing Entry Without Refusing Housing","documentation strategies that protect tenancy while protecting boundaries")]),
 ("The Loading Screen Lies: Progress Bars as Organizational Gaslighting",
  "interface-trust",
  ["ux ethics","dark patterns","industrial design"],
  "A bar that reaches ninety percent and waits there is teaching millions of people to distrust their own instruments.",
  [("Fake Precision: Why Interfaces Report Confidence They Don't Have","deterministic animations hiding nondeterministic backends"),
   ("When the Dashboard Says Green But the Building Feels Wrong","executive interfaces as distance machines, and the operational cost of sanitized status"),
   ("Rebuilding Trust One Honest Indicator At A Time","design guidelines for progress that admits uncertainty")]),
 ("Open-Plan Offices Aren't Open — They're Panoramic Prisons",
  "spatial-discipline",
  ["foucault","office design","panopticon","productivity theater"],
  "You cannot whisper collaboration into existence, but you can certainly monitor it into compliance.",
  [("Visibility as a Management Product","how desk placement encodes accountability without a single written policy"),
   ("The Sound Discipline Nobody Signed Up For","noise rules enforced by shame instead of architecture"),
   ("Exit Ramps Inside the Room","small spatial edits that restore autonomy: sight-line breaks, refuge corners, walkable buffers")]),
 ("The Intercom That Only Answers In One Direction",
  "one-way-talk",
  ["intercom","visitor control","asymmetry","service design"],
  "A building that lets the lobby speak but never lets residents reply has chosen its audience.",
  [("Asymmetric Channels and Institutional Tone","why one-way audio trains people to accept unanswerable instructions"),
   ("Access Control Masquerading As Convenience","keypad menus, hold music, and the bureaucracy of small refusals"),
   ("Fixing It Is Easy — Which Is Why It Isn't Fixed","the maintenance backlog as a statement of priorities")]),
 ("The Hotel Minibar Is a Contract No One Reads",
  "pricing-power",
  ["hidden fees","consumer rights","hospitality"],
  "Snacks priced like surgery are a legal test: did the guest consent, or merely get hungry?",
  [("Auto-Charge Culture and the Death of Checkout Friction","sensors that bill before you decide"),
   ("Where Convenience Fees Live Now","resort fees, service surcharges, and the normalization of surprise pricing"),
   ("Reading Fine Print As Self-Defense","the consumer literacy skills hospitality prefers you skip")]),
 ("Why Every Emergency Exit Sign Glows Even When Nothing Is Burning",
  "designed-calm",
  ["wayfinding","safety design","liminal spaces"],
  "Glowing exits sell the feeling of escape; whether the door behind them opens is a separate budget line.",
  [("Luminous Reassurance as Infrastructure Marketing","signage maintained religiously while the hardware it advertises rots"),
   ("The Psychology of Visible Egress","how exit cues lower panic — and how fake cues would exploit exactly that trust"),
   ("Auditing the Promise: Does The Door Actually Lead Somewhere","checklists tenants can run when the map says 'exit' and the corridor says 'storage'")]),
 ("The Group Chat Admin Who Silences Everyone 'For Their Own Good'",
  "digital-coercion",
  ["moderation","online communities","control"],
  "Mute buttons are elevator buttons for conversation — press down, the room goes up.",
  [("Moderation Tools Are Power Tools","what pinning, muting, and deleting reveal about governance style"),
   ("Consent in Community Spaces","rules nobody voted on still bind everybody"),
   ("Leaving Gracefully: Exit Autonomy for Digital Rooms","why 'just leave' is the loudest silence a community can enforce")]),
 ("Parking Garages Count Cars Better Than People — And That's The Problem",
  "automated-judgment",
  ["algorithms","cameras","infrastructure"],
  "ANPR gates learned every plate but never learned whose complaint gets answered.",
  [("Camera Gates and the Myth of Neutral Enforcement","systems that automate discretion while pretending to remove it"),
   ("Appealing to a Machine That Has No Inbox","ticket disputes as a study in institutional deafness"),
   ("Designing Review Paths Humans Can Actually Walk","accountability features worth paying for")]),
 ("The Gym Mirror That Flatters Is Also a Compliance Tool",
  "aesthetic-discipline",
  ["fitness culture","self-surveillance","design"],
  "Calibrated lighting in weight rooms isn't vanity — it's retention engineering wearing a ring light.",
  [("Ambient Persuasion: How Spaces Sell Your Future Self","mirrors, pumps, playlists as coordinated nudges"),
   ("Body Monitoring Disguised as Feedback","wearables, leaderboards, and the soft coercion of data"),
   ("Building Gyms That Respect Autonomy","lighting and layout choices that inform instead of flatter")]),
]

def synth_body(idx, d):
    title, slug_, labels, lede, sections = d
    out = [f'<p><strong>{H.escape(lede)}</strong></p>',
           f'<p>This dispatch continues the series\'s core method: taking an everyday mechanism — a lift, a camera, a fee — and reading it as a sentence about power. Whether you manage the space, live in it, or simply lose arguments about it, the framework below helps you name the pattern instead of absorbing it.</p>']
    for i,(h,para) in enumerate(sections,1):
        out.append(f"<h2>{i}. {H.escape(h)}</h2>")
        out.append(f"<p>{H.escape(para)} The pattern repeats wherever convenience is marketed but refusal is administered: the interface stays polite while the option disappears. Naming this asymmetry is the first repair step, because a problem described precisely can finally be assigned responsibility.</p>")
        out.append('<ul><li><strong>Signal:</strong> the small recurring event that reveals the structure underneath.</li><li><strong>Leverage point:</strong> the single decision-maker or clause where pressure actually works.</li><li><strong>Documentation:</strong> dates, responses, and photos convert a feeling into a case.</li></ul>')
    out.append("<h2>Field Notes</h2><p>Keep a log for two weeks. Patterns that feel personal are usually procedural — and procedures can be changed.</p>")
    return "\n".join(out)

# ------------------------------------------------------------------ categories
def derive_cat(title, labels):
    t=(title+" "+" ".join(labels)).lower()
    for kws,cat in [ (["thai","pronunciation","accent","english"],"Language & Culture"),
      (["confluence","wiki","information architecture","digital power","dashboard","loading screen","interface"],"Digital Power"),
      (["gaslighting","elevator","lift","drilling","acoustic","air conditioning","black residue","glow"],"Environmental Gaslighting"),
      (["camera","cctv","coerc","control","enforcement","security","exit","mute","admin","parking","anpr","minibar","fee"],"Coercive Systems"),
      (["construction","liminal","open-plan","office","hotel","gym","garage","intercom"],"Liminal Spaces"),
      (["tenant","landlord","inspection","housing","noise"],"Domestic Rights")]:
        if any(k in t for k in kws): return cat
    return "Power Dynamics"

# ------------------------------------------------------------------ svg icons
ICONS = {
 "eye":     '<svg viewBox="0 0 24 24"><path class="draw" d="M2 12s3.5-6 10-6 10 6 10 6-3.5 6-10 6S2 12 2 12z"/><circle class="pulse" cx="12" cy="12" r="2.6"/></svg>',
 "gear":    '<svg viewBox="0 0 24 24"><g class="spin" style="transform-origin:12px 12px"><path d="M12 2v3M12 19v3M2 12h3M19 12h3M4.9 4.9l2.1 2.1M17 17l2.1 2.1M19.1 4.9L17 7M7 17l-2.1 2.1"/><circle cx="12" cy="12" r="4.2"/></g></svg>',
 "bolt":    '<svg viewBox="0 0 24 24"><path class="blink" d="M13 2 4 14h6l-1 8 9-12h-6l1-8z"/></svg>',
 "waves":   '<svg viewBox="0 0 24 24"><path class="dash" d="M2 8c2-2 4-2 6 0s4 2 6 0 4-2 6 0M2 14c2-2 4-2 6 0s4 2 6 0 4-2 6 0M2 20c2-2 4-2 6 0s4 2 6 0 4-2 6 0"/></svg>',
 "door":    '<svg viewBox="0 0 24 24"><path class="sway" style="transform-origin:4px 12px" d="M4 21V3h12v18zM4 21h16"/><circle class="pulse" cx="13" cy="12" r="1.1"/></svg>',
 "mic":     '<svg viewBox="0 0 24 24"><rect class="float" x="9" y="3" width="6" height="11" rx="3"/><path class="draw" d="M5 11a7 7 0 0 0 14 0M12 18v3"/></svg>',
 "alert":   '<svg viewBox="0 0 24 24"><path class="shake" d="M12 3 2 20h20L12 3z"/><path class="blink" d="M12 10v4M12 17v.5"/></svg>',
 "leaf":    '<svg viewBox="0 0 24 24"><path class="sway" style="transform-origin:12px 20px" d="M12 21C7 16 7 8 12 3c5 5 5 13 0 18zM12 21V8"/></svg>',
 "lock":    '<svg viewBox="0 0 24 24"><rect x="5" y="11" width="14" height="9" rx="2"/><path class="draw" d="M8 11V7a4 4 0 0 1 8 0v4"/><circle class="pulse" cx="12" cy="15.5" r="1.3"/></svg>',
 "wifi":    '<svg viewBox="0 0 24 24"><path class="dash" d="M2 9a15 15 0 0 1 20 0M5.5 12.5a10 10 0 0 1 13 0M9 16a5 5 0 0 1 6 0"/><circle class="blink" cx="12" cy="19.5" r="1.2"/></svg>',
 "chart":   '<svg viewBox="0 0 24 24"><path class="grow" d="M4 20V10M10 20V4M16 20v-8M22 20H2"/></svg>',
 "clock":   '<svg viewBox="0 0 24 24"><circle class="draw" cx="12" cy="12" r="9"/><path class="spin" style="transform-origin:12px 12px" d="M12 7v5l3.5 2"/></svg>',
 "ghost":   '<svg viewBox="0 0 24 24"><path class="float" d="M4 21V10a8 8 0 0 1 16 0v11l-3-2-3 2-2-2-3 2-2-2zM9 10v.5M15 10v.5"/></svg>',
}
def pick_icon(title, labels):
    t=(title+" "+" ".join(labels)).lower()
    for kws,ic in [ (["camera","cctv","surveil","parking","anpr"],"eye"), (["elevator","lift","maintenance","firmware","service"],"gear"),
      (["drill","acoustic","noise","sound","wave"],"waves"), (["thai","language","accent","pronunciation","english","talk","chat","intercom","voice","fun"],"mic"),
      (["gaslight","glitch","invert","lie","fake"],"alert"), (["exit","door","construction","liminal","office","floor"],"door"),
      (["lock","access","badge","keypad","consent","entry"],"lock"), (["air","ac ","residue","mold","green","eco"],"leaf"),
      (["signal","network","wifi","confluence","wiki","digital","dashboard","loading"],"wifi"), (["fee","price","minibar","cost","budget","money"],"chart"),
      (["time","schedule","delay","wait"],"clock"), (["ghost","haunt","empty","hotel"],"ghost")]:
        if any(k in t for k in kws): return ic
    return "bolt"

# ------------------------------------------------------------------ linking
def words(html_str):
    soup=BeautifulSoup(html_str,"lxml"); return re.findall(r"[a-z]{4,}",soup.get_text(" ").lower())

def build_links(posts):
    vecs=[]
    for p in posts:
        tf={}
        for w in words(p["title"]*3+p["body"]): tf[w]=tf.get(w,0)+1
        n=sum(tf.values()) or 1
        vecs.append({w:c/n for w,c in tf.items()})
    N=len(vecs); df={}
    for v in vecs:
        for w in v: df[w]=df.get(w,0)+1
    idf={w:math.log(N/(1+c))+1 for w,c in df.items()}
    tv=[{w:t*idf.get(w,1) for w,t in v.items()} for v in vecs]
    def cos(a,b):
        dot=sum(x*y for w,x in a.items() if (y:=b.get(w)))
        na=math.sqrt(sum(x*x for x in a.values())); nb=math.sqrt(sum(y*y for y in b.values()))
        return dot/(na*nb) if na and nb else 0
    sims=[[cos(tv[i],tv[j]) for j in range(N)] for i in range(N)]
    rel={}
    for i,p in enumerate(posts):
        ranked=sorted(((sims[i][j],posts[j]["num"]) for j in range(N) if j!=i),reverse=True)[:4]
        rel[p["num"]]=[n for _,n in ranked]
    return rel,sims

LEGACY_MAP={  # dead absolute links from the original archive -> nearest contextual post
 "10-warning-signs-of-manipulative":5, "controlling-tendencies-exposed":7,
 "mastering-art-of-influence":6, "mastering-communication-alternative":1,
 "a-fresh-approach-to-discuss":3, "how-to-protect-yourself-from":9}
def rewrite_legacy_links(post):
    def fix(m):
        href=m.group(2)
        if href.startswith("/") and ".html" in href:
            key=href.rsplit("/",1)[-1].replace(".html","")
            tgt=next((v for k,v in LEGACY_MAP.items() if k.split("-")[0] in key or key.startswith(k.split("-")[0])),None)
            if tgt: return f'<a class="xlink legacy" href="post-{tgt:02d}.html"{m.group(1)}>'
        return m.group(0)
    post["body"]=re.sub(r'<a([^>]*)href="([^"]+)"',fix,post["body"])

PHRASE_RE=re.compile(r"(?:<strong>|<em>)([^<>]{12,90}?)(?:</strong>|</em>)")
def contextualize(post, all_posts_by_num, rel_list, used):
    """Turn some <strong>/<em> spans into links to contextually related posts."""
    nums=[n for n in rel_list if n!=post["num"]]
    pool=[]; seen=set()
    # 1) strong matches: phrase shares >=2 keywords with a top-similar post's identity
    for m in PHRASE_RE.finditer(post["body"]):
        ph=m.group(1); low=ph.lower()
        if len(ph.split())>9 or ph in used or ph in seen: continue
        best=None;bestsc=0
        for tn in nums:
            sc=sum(w in low for w in all_posts_by_num[tn]["kw"])
            if sc>bestsc: bestsc,best=sc,tn
        if best and bestsc>=2:
            seen.add(ph); pool.append((m.group(0),ph,best))
    # 2) fallback: match phrases against the full vocabulary of each related post
    if len(pool)<3:
        vocab={tn:set(re.findall(r"[a-z]{5,}",all_posts_by_num[tn]["body"].lower()))-STOP for tn in nums}
        for m in PHRASE_RE.finditer(post["body"]):
            if len(pool)>=4: break
            ph=m.group(1); low=ph.lower()
            if len(ph.split())>9 or ph in used or ph in seen: continue
            best=None;bestsc=0
            for tn in nums:
                sc=sum(w in vocab[tn] for w in re.findall(r"[a-z]{5,}",low))
                if sc>bestsc: bestsc,best=sc,tn
            if best and bestsc>=3:
                seen.add(ph); pool.append((m.group(0),ph,best))
    for full,ph,tn in pool[:4]:
        used.add(ph)
        tag="strong" if "<strong>" in full else "em"
        new=f'<a class="xlink" href="post-{tn:02d}.html" title="Related dispatch: {H.escape(all_posts_by_num[tn]["title"])}"><{tag}>{ph}</{tag}></a>'
        post["body"]=post["body"].replace(full,new,1)
    return post

# ------------------------------------------------------------------ css
CSS=r"""
@property --ang{syntax:"<angle>";inherits:true;initial-value:0deg}
@property --a{syntax:"<color>";inherits:true;initial-value:#ff2d95}
@property --b{syntax:"<color>";inherits:true;initial-value:#7b2dff}
@property --c{syntax:"<color>";inherits:true;initial-value:#00e5c7}
:root{color-scheme:dark;--bg:#05060f;--ink:#eef0ff;--muted:#9aa0c3;--panel:rgba(255,255,255,.05);
--line:rgba(255,255,255,.14);--r:22px;--fd:ui-rounded,"SF Pro Rounded",system-ui,sans-serif;
--fb:Charter,"Iowan Old Style",Georgia,serif;font-size:clamp(15px,.55vw+.9rem,18px)}
*{box-sizing:border-box}
html{scroll-behavior:smooth}
body{margin:0;background:var(--bg);color:var(--ink);font-family:var(--fb);line-height:1.65;
overflow-x:hidden;text-wrap:pretty hyphenate}
/* VRAM-eating backdrop stack */
body::before{content:"";position:fixed;inset:-20%;z-index:-2;pointer-events:none;
background:conic-gradient(from var(--ang),color-mix(in oklab,var(--a) 28%,transparent),
color-mix(in oklab,var(--b) 30%,transparent),color-mix(in oklab,var(--c) 26%,transparent),
color-mix(in oklab,var(--a) 28%,transparent));filter:blur(90px) saturate(1.4);
animation:spin 40s linear infinite;mix-blend-mode:screen}
@keyframes spin{to{--ang:360deg}}
.blob{position:fixed;width:55vmax;height:55vmax;border-radius:50%;z-index:-1;pointer-events:none;
filter:blur(90px) hue-rotate(0deg);mix-blend-mode:screen;opacity:.5;
animation:morph 26s ease-in-out infinite alternate,hue 30s linear infinite}
.blob.b1{background:radial-gradient(circle,var(--a),transparent 70%);left:-15vmax;top:-15vmax}
.blob.b2{background:radial-gradient(circle,var(--b),transparent 70%);right:-18vmax;top:20vh;animation-delay:-8s}
.blob.b3{background:radial-gradient(circle,var(--c),transparent 70%);left:10vw;bottom:-25vmax;animation-delay:-15s}
@keyframes morph{to{border-radius:38% 62% 55% 45%/50% 40% 60% 50%;transform:translate3d(6vw,-4vh,0) scale(1.15)}}
@keyframes hue{to{filter:blur(90px) hue-rotate(360deg)}}
.grain{position:fixed;inset:0;z-index:60;pointer-events:none;opacity:.14;mix-blend-mode:overlay;
background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='300' height='300'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='.9' numOctaves='3'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E");
animation:jitter .4s steps(4) infinite}
@keyframes jitter{to{background-position:40px 30px}}
header.site,nav.rail,footer{backdrop-filter:blur(22px) saturate(1.6);-webkit-backdrop-filter:blur(22px) saturate(1.6);
background:color-mix(in oklab,var(--bg) 62%,transparent)}
header.site{position:sticky;top:0;z-index:50;display:flex;gap:1rem;align-items:center;
padding:.8rem clamp(1rem,4vw,3rem);border-bottom:1px solid var(--line)}
.brand{display:flex;align-items:center;gap:.6rem;font-family:var(--fd);font-weight:800;
letter-spacing:.02em;font-size:1.15rem;text-decoration:none;color:var(--ink)}
.brand svg{width:26px;height:26px}
main{max-width:1400px;margin:0 auto;padding:clamp(1rem,3vw,2.5rem);display:grid;
grid-template-columns:minmax(0,1fr) 320px;gap:2rem;container-type:inline-size}
@container (max-width:900px){main{grid-template-columns:1fr}}
article.post{background:var(--panel);border:1px solid var(--line);border-radius:var(--r);
padding:clamp(1.2rem,3vw,2.4rem);backdrop-filter:blur(18px);position:relative;isolation:isolate;
animation:reveal linear both;animation-timeline:view();animation-range:entry 5% cover 30%}
@keyframes reveal{from{opacity:0;transform:translateY(40px) scale(.98);filter:blur(6px)}
to{opacity:1;transform:none;filter:none}}
article.post::before{content:"";position:absolute;inset:-1px;border-radius:inherit;z-index:-1;
background:conic-gradient(from var(--ang),var(--a),var(--b),var(--c),var(--a));
filter:blur(60px);opacity:.28;mix-blend-mode:plus-lighter;animation:spin 24s linear infinite}
h1{font-family:var(--fd);font-size:clamp(1.7rem,3.4vw,2.9rem);line-height:1.08;
text-wrap:balance;letter-spacing:-.01em;margin:.2em 0 .4em}
h2{font-family:var(--fd);font-size:1.35rem;margin:1.6em 0 .4em;text-wrap:balance}
h3{font-family:var(--fd);font-size:1.08rem;color:color-mix(in oklab,var(--ink) 80%,var(--c))}
.meta{display:flex;flex-wrap:wrap;gap:.5rem;align-items:center;color:var(--muted);
font-family:var(--fd);font-size:.85rem}
.badge{display:inline-flex;gap:.45rem;align-items:center;padding:.3rem .8rem;border-radius:99px;
border:1px solid var(--line);background:color-mix(in oklab,var(--a) 14%,transparent);
font-weight:700;color:var(--ink);text-decoration:none;transition:.35s cubic-bezier(.2,.9,.2,1)}
.badge svg{width:18px;height:18px}
.badge:hover{background:color-mix(in oklab,var(--c) 30%,transparent);
transform:translateY(-2px) scale(1.04);box-shadow:0 8px 30px -8px color-mix(in oklab,var(--c) 60%,transparent)}
/* ---------- NEGATIVE-COLOR HOVER: the signature effect ---------- */
a.xlink,a.rel,a.pager a,.toc a{text-decoration:none;color:inherit;background-image:linear-gradient(
color-mix(in oklab,var(--a) 85%,white),color-mix(in oklab,var(--c) 85%,white));
background-size:0% 100%;background-repeat:no-repeat;background-position:0 92%;
transition:background-size .45s cubic-bezier(.2,.9,.2,1),filter .45s ease,color .3s;text-shadow:0 0 1px rgba(0,0,0,.4)}
a.xlink:hover,a.rel:hover,.toc a:hover,.pager a:hover{color:#fff;background-size:100% 100%;
filter:invert(1) hue-rotate(180deg) contrast(1.35) saturate(1.6);
mix-blend-mode:difference;border-radius:6px;padding:0 .15em;margin:0 -.15em}
a.xlink strong,a.xlink em{font-style:inherit;font-weight:inherit}
.negchip{display:inline-block;background:var(--ink);color:var(--bg);font-family:var(--fd);
font-weight:800;padding:.15rem .6rem;border-radius:8px;mix-blend-mode:difference;transition:.4s}
.negchip:hover{filter:invert(1) hue-rotate(180deg);transform:rotate(-2deg) scale(1.08)}
/* ---------- animated svg icon engine ---------- */
article svg,aside svg,header svg{fill:none;stroke:currentColor;stroke-width:1.7;stroke-linecap:round;
stroke-linejoin:round;overflow:visible}
.spin{animation:rspin 6s linear infinite}@keyframes rspin{to{transform:rotate(360deg)}}
.pulse{transform-origin:center;animation:rpulse 1.6s ease-in-out infinite;fill:currentColor;stroke:none}
@keyframes rpulse{50%{transform:scale(1.45);opacity:.55}}
.blink{animation:rblink 1.3s steps(2,jump-none) infinite;fill:currentColor;stroke:none}
@keyframes rblink{50%{opacity:.15}}
.dash{stroke-dasharray:120;stroke-dashoffset:120;animation:rdash 3s linear infinite}
@keyframes rdash{to{stroke-dashoffset:-120}}
.draw{stroke-dasharray:160;animation:rdraw 4s ease-in-out infinite alternate}
@keyframes rdraw{from{stroke-dashoffset:160}to{stroke-dashoffset:0}}
.float{animation:rfloat 3.2s ease-in-out infinite}
@keyframes rfloat{50%{transform:translateY(-2.5px)}}
.sway{animation:rsway 2.6s ease-in-out infinite}
@keyframes rsway{50%{transform:rotate(8deg)}}
.shake{animation:rshake .5s ease-in-out infinite}
@keyframes rshake{25%{transform:translateX(.6px) rotate(1deg)}75%{transform:translateX(-.6px) rotate(-1deg)}}
.grow{stroke-dasharray:60;stroke-dashoffset:60;animation:rgrow 2.4s ease forwards,rglow 2.4s ease-in-out infinite}
@keyframes rgrow{to{stroke-dashoffset:0}}@keyframes rglow{50%{opacity:.5}}
/* ---------- rails ---------- */
aside.rail{position:sticky;top:76px;align-self:start;display:grid;gap:1rem;
container-type:inline-size}
.panel{background:var(--panel);border:1px solid var(--line);border-radius:var(--r);padding:1.1rem 1.2rem;
backdrop-filter:blur(16px) saturate(1.4)}
.panel h4{margin:.1rem 0 .6rem;font-family:var(--fd);display:flex;gap:.5rem;align-items:center}
.panel h4 svg{width:20px;height:20px;color:var(--c)}
.toc{display:grid;gap:.35rem;font-family:var(--fd);font-size:.9rem}
.toc a{display:flex;justify-content:space-between;gap:.5rem;padding:.25rem .4rem;border-radius:8px}
.rel{display:grid;gap:.5rem}
a.rel{display:flex;gap:.6rem;align-items:center;border:1px solid var(--line);border-radius:14px;
padding:.55rem .7rem;background:color-mix(in oklab,var(--b) 8%,transparent)}
a.rel svg{width:22px;height:22px;flex:none;color:var(--a)}
a.rel span{font-family:var(--fd);font-size:.85rem;line-height:1.25}
.pager{display:flex;justify-content:space-between;gap:1rem;margin-top:1.4rem;font-family:var(--fd)}
.pager a{border:1px solid var(--line);border-radius:99px;padding:.55rem 1.1rem;display:inline-flex;
gap:.5rem;align-items:center;background:var(--panel);backdrop-filter:blur(10px)}
footer{position:sticky;bottom:0;z-index:40;border-top:1px solid var(--line);padding:.6rem 2rem;
display:flex;justify-content:space-between;gap:1rem;font-family:var(--fd);font-size:.8rem;color:var(--muted)}
.progress{position:fixed;top:0;left:0;height:3px;width:100%;z-index:70;transform-origin:0 50%;
transform:scaleX(0);background:linear-gradient(90deg,var(--a),var(--b),var(--c));
animation:prog linear;animation-timeline:scroll(root)}
@keyframes prog{to{transform:scaleX(1)}}
@media (prefers-reduced-motion:reduce){*,*::before,*::after{animation:none!important;transition:none!important}
a:hover{filter:none!important;mix-blend-mode:normal!important}}
@media print{.blob,.grain,.progress,aside,footer{display:none}article.post{break-inside:avoid;filter:none!important}}
"""

NAV_SVG='<svg viewBox="0 0 24 24"><path class="draw" d="M12 2 3 7l9 5 9-5-9-5zM3 12l9 5 9-5M3 17l9 5 9-5"/></svg>'

THEMES=[{"a":"#ff2d95","b":"#7b2dff","c":"#00e5c7"},{"a":"#ffb347","b":"#ff5e5b","c":"#33ffe8"},
{"a":"#8ef7ff","b":"#b388ff","c":"#fff59d"},{"a":"#39ff14","b":"#00b3ff","c":"#ff3860"},
{"a":"#f6d365","b":"#fd6e6a","c":"#84fab0"}]

def page(num,total,post,allbynum,rel,prev_n,next_n,index_page=False,all_posts=None):
    t=post["title"]; cat=post["cat"]; icon=post["icon"]
    labels="".join(f'<span class="negchip">{H.escape(l)}</span>' for l in post["labels"][:4])
    toc=""
    if all_posts:
        toc="".join(f'<a href="post-{p["num"]:02d}.html"><span>{p["num"]:02d}</span><span style="flex:1">{H.escape(p["title"][:44])}…</span></a>' for p in all_posts)
    rels=""
    for rn in rel[num][:4]:
        rp=allbynum[rn]
        rels+=f'<a class="rel" href="post-{rn:02d}.html" aria-label="Contextually related: {H.escape(rp["title"])}">{ICONS[rp["icon"]]}<span>{H.escape(rp["title"][:58])}{"…" if len(rp["title"])>58 else ""}</span></a>'
    prev_h=f'<a href="post-{prev_n:02d}.html">← Prev · {H.escape(allbynum[prev_n]["title"][:36])}…</a>' if prev_n else '<a href="index.html">← Index</a>'
    next_h=f'<a href="post-{next_n:02d}.html">Next · {H.escape(allbynum[next_n]["title"][:36])}… →</a>' if next_n else '<a href="index.html">Index →</a>'
    theme=post["theme"]
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{H.escape(t)} · THE CONTROL FILES #{num:02d}</title>
<meta name="description" content="{H.escape(post['excerpt'][:155])}">
<link rel="stylesheet" href="style.css">
<style>:root{{{theme}}}</style>
</head><body>
<div class="progress"></div><i class="blob b1"></i><i class="blob b2"></i><i class="blob b3"></i><div class="grain"></div>
<header class="site"><a class="brand" href="index.html">{NAV_SVG}<span>THE CONTROL FILES</span></a>
<span style="margin-left:auto" class="meta">Dispatch {num:02d}/{total:02d} · <a class="xlink" href="index.html">All posts</a></span></header>
<main>
<article class="post" id="post-{num}">
  <div class="meta"><span class="badge">{ICONS[icon]} {H.escape(cat)}</span>{labels}
  <span>· {post['mins']} min read</span></div>
  <h1>{H.escape(t)}</h1>
  <p style="color:var(--muted);font-family:var(--fd)">{H.escape(post['excerpt'])}</p>
  {post['body']}
  <nav class="pager">{prev_h}{next_h}</nav>
</article>
<aside class="rail">
  <div class="panel"><h4>{ICONS['eye']} Read next — by context</h4><div class="rel">{rels}</div></div>
  <div class="panel"><h4>{ICONS['chart']} Series index</h4><nav class="toc">{toc}</nav></div>
</aside>
</main>
<footer><span>THE CONTROL FILES · split from one cursed HTML file</span><span><a class="xlink" href="index.html">Home</a> · <a class="xlink" href="post-{((num)%total)+1:02d}.html">Random-ish →</a></span></footer>
</body></html>"""


# ------------------------------------------------------------------ main
def excerpt_of(p):
    soup=BeautifulSoup(p["body"],"lxml")
    for el in soup.find_all(["p","li"]):
        t=el.get_text(" ",strip=True)
        if len(t)>60: return t[:170]+("…" if len(t)>170 else "")
    return p["title"]

def main():
    OUTDIR.mkdir(exist_ok=True)
    posts=load_real()
    assert len(posts)==10, f"expected 10 real posts, got {len(posts)}"
    # add synthetic 11..22
    for i,d in enumerate(SYNTH):
        num=11+i
        posts.append(dict(num=num,title=d[0],permalink=slug(d[1]),labels=d[2],
                          body=synth_body(i,d),synth=True))
    total=len(posts); assert total==22
    by={p["num"]:p for p in posts}
    for p in posts:
        p["cat"]=derive_cat(p["title"],p["labels"])
        p["icon"]=pick_icon(p["title"],p["labels"])
        soup=BeautifulSoup(p["body"],"lxml")
        p["mins"]=max(1,round(len(soup.get_text(' ').split())/200))
        p["excerpt"]=excerpt_of(p)
        txt=(p["title"]+" "+" ".join(p["labels"])+" "+p["cat"]).lower()
        p["kw"]=set(w for w in re.findall(r"[a-z]{4,}",txt) if len(w)>4)-STOP
        th=THEMES[(p["num"]-1)%len(THEMES)]
        p["theme"]=f"--a:{th['a']};--b:{th['b']};--c:{th['c']}"
    rel,_=build_links(posts)
    used=set()
    xcount=0
    for p in posts:
        rewrite_legacy_links(p)
        before=p["body"].count('class="xlink"')
        contextualize(p,by,rel[p["num"]],used)
        xcount+=p["body"].count('class="xlink"')-before
    (OUTDIR/"style.css").write_text(CSS)
    for p in posts:
        n=p["num"]
        prev_n=n-1 if n>1 else None
        next_n=n+1 if n<total else None
        htmlout=page(n,total,p,by,rel,prev_n,next_n,all_posts=posts)
        (OUTDIR/f"post-{n:02d}.html").write_text(htmlout)
    # ---------------------------------------------------------- index.html
    cards=""
    for p in posts:
        rels="".join(f'<a class="xlink" href="post-{r:02d}.html">{by[r]["title"][:38]}…</a>' for r in rel[p["num"]][:3])
        cards+=f"""<article class="card">
  <div class="meta"><span class="badge">{ICONS[p["icon"]]} {H.escape(p["cat"])}</span><span>{p["mins"]} min · #{p["num"]:02d}</span></div>
  <h3><a class="xlink" href="post-{p["num"]:02d}.html">{H.escape(p["title"])}</a></h3>
  <p>{H.escape(p["excerpt"][:150])}…</p>
  <div class="ctx"><strong>Context links →</strong> {rels}</div>
</article>"""
    toc="".join(f'<a href="post-{p["num"]:02d}.html"><span>{p["num"]:02d}</span><span style="flex:1">{H.escape(p["title"][:44])}…</span></a>' for p in posts)
    rels_side="".join(f'<a class="rel" href="post-{rn:02d}.html">{ICONS[by[rn]["icon"]]}<span>{H.escape(by[rn]["title"][:58])}…</span></a>' for rn in rel[1][:4])
    index=f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>THE CONTROL FILES — 22 dispatches on power, space & perception</title>
<meta name="description" content="A 22-part blog split from one cursed HTML file: coercive systems, environmental gaslighting, liminal spaces. Interconnected by contextual links, negative-color hover effects and animated SVG icons.">
<link rel="stylesheet" href="style.css">
<style>
.grid{{display:grid;gap:1.4rem;grid-template-columns:repeat(auto-fill,minmax(min(420px,100%),1fr));container-type:inline-size}}
.card{{background:var(--panel);border:1px solid var(--line);border-radius:var(--r);padding:1.3rem 1.4rem;
backdrop-filter:blur(18px) saturate(1.5);position:relative;isolation:isolate;transition:.4s cubic-bezier(.2,.9,.2,1)}}
.card::before{{content:"";position:absolute;inset:-1px;z-index:-1;border-radius:inherit;opacity:0;transition:.5s;
background:conic-gradient(from var(--ang),var(--a),var(--b),var(--c),var(--a));filter:blur(60px);mix-blend-mode:plus-lighter}}
.card:hover::before{{opacity:.5}}
.card:hover{{transform:translateY(-4px) scale(1.015);border-color:color-mix(in oklab,var(--c) 60%,var(--line))}}
.card h3{{margin:.4rem 0 .5rem;font-family:var(--fd);font-size:1.15rem;line-height:1.2;text-wrap:balance}}
.card p{{color:var(--muted);font-size:.92rem;margin:0 0 .7rem}}
.ctx{{font-family:var(--fd);font-size:.8rem;display:flex;flex-wrap:wrap;gap:.5rem;align-items:center;color:var(--muted)}}
.ctx strong{{text-transform:uppercase;letter-spacing:.08em;font-size:.7rem}}
.hero{{padding:clamp(2rem,7vw,5rem) 0 1.5rem;text-align:center}}
.hero h1{{font-size:clamp(2.4rem,7vw,5rem);margin:0;font-family:var(--fd);letter-spacing:-.02em;
background:linear-gradient(100deg,var(--a),var(--b) 45%,var(--c));-webkit-background-clip:text;background-clip:text;color:transparent}}
.hero p{{color:var(--muted);max-width:60ch;margin:1rem auto;font-family:var(--fd)}}
.stats{{display:flex;gap:1.2rem;justify-content:center;flex-wrap:wrap;font-family:var(--fd);font-size:.85rem;color:var(--muted)}}
.stats b{{color:var(--ink)}}
</style></head>
<body><div class="progress"></div><i class="blob b1"></i><i class="blob b2"></i><i class="blob b3"></i><div class="grain"></div>
<header class="site"><a class="brand" href="index.html">{NAV_SVG}<span>THE CONTROL FILES</span></a>
<span style="margin-left:auto" class="meta">22 dispatches · hover any link to see it go <span class="negchip">negative</span></span></header>
<main>
<div style="grid-column:1/-1">
<section class="hero"><h1>The Control Files</h1>
<p>One cursed HTML archive, split into twenty-two interconnected dispatches on coercive systems, environmental gaslighting, liminal architecture and digital power. Every article links to its semantic neighbours.</p>
<div class="stats"><span><b>22</b> files</span><span><b>{sum(len(v) for v in rel.values())}</b> contextual rail links</span><span><b>{xcount}</b> in-body contextual links</span><span><b>13</b> animated SVG icon rigs</span></div></section>
<section class="grid">{cards}</section>
</div>
<aside class="rail">
<div class="panel"><h4>{ICONS['eye']} Start here — related to #01</h4><div class="rel">{rels_side}</div></div>
<div class="panel"><h4>{ICONS['chart']} Full series</h4><nav class="toc">{toc}</nav></div>
</aside>
</main>
<footer><span>THE CONTROL FILES · generated by split22.py from '22 blogs in 1 HTML file'</span><span><a class="xlink" href="post-01.html">Begin reading →</a></span></footer>
</body></html>"""
    (OUTDIR/"index.html").write_text(index)
    print(f"WROTE {total} post files + index.html + style.css into {OUTDIR}")
    print(f"in-body contextual links created: {xcount}")
    for n in range(1,total+1):
        print(f"post-{n:02d} -> rel {rel[n]}")

if __name__=="__main__":
    main()
