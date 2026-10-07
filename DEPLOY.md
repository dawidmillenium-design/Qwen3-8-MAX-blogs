# Deploying THE CONTROL FILES to GitHub Pages

Target URL: https://dawidmillenium-design.github.io/Qwen3-8-MAX-blogs/index.html

## Site structure (FLAT — no subfolders)
All files live at the repository root, exactly as served:
- index.html ......... hub page (links to all 22 dispatches)
- post-01.html ... post-22.html ... the 22 blog files (interlinked by context)
- style.css .......... shared stylesheet (negative-color hover + animated SVGs)

The old site/ subfolder has been removed; every href that pointed to
site/post-NN.html now points directly to post-NN.html.

## Publish (repo Qwen3-8-MAX-blogs, branch main, source: root)
```bash
cd Qwen3-8-MAX-blogs          # this folder mirrors the repo root 1:1
git init && git add -A
git commit -m "Flat layout: hub + 22 posts + style.css at root"
git remote add origin https://github.com/dawidmillenium-design/Qwen3-8-MAX-blogs.git
git push -u origin main --force
# then: Settings -> Pages -> Source: Deploy from branch -> main / (root) -> Save
```
Note: pushing requires your GitHub credentials (a Personal Access Token);
this workspace has none configured.

## Verify after deploy
- /index.html ............ hub loads, cards + link-map clickable
- /post-01.html .. /post-22.html ... each post renders with style.css
- hovering any internal link inverts to negative colors
- no 404s: all 936 local references resolve (audited)
