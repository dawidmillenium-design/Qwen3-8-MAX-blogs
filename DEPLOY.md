# Deploying THE CONTROL FILES hub to GitHub Pages

Target URL: https://dawidmillenium-design.github.io/Qwen3-8-MAX-blogs/index.html

## Layout (already prepared in this repo)
```
index.html          ← HUB PAGE (links to all 22 dispatches)
site/index.html     ← original 22-card overview
site/post-01..22.html
site/style.css      ← shared design system (negative hover + SVG rigs)
Qwen3-8-MAX-blogs/  ← ready-made copy of the same deploy bundle
docs/index.html     ← generated hub (source of root index.html, via make_hub.py)
```

## Push steps (needs your GitHub credentials — none present in this sandbox)
```bash
cd Qwen3-8-MAX-blogs
git init -b main
git add -A
git commit -m "Hub page + 22 interconnected dispatches"
git remote add origin https://github.com/dawidmillenium-design/Qwen3-8-MAX-blogs.git
git push -u origin main --force        # or use a fine-grained PAT: https://<token>@github.com/...
```
Then: repo → Settings → Pages → Source: **Deploy from a branch** → `main` / `/ (root)` → Save.
The hub goes live at `/index.html`; every post is reachable at `/site/post-NN.html`.

Regenerate the hub any time with: `python3 make_hub.py` (reads site/, writes docs/index.html).
