# sitesmith

Build a small business website and matching print-ready business cards, from a phone,
with no signal.

Answer about a dozen questions, look through 160 layout-and-theme combinations rendered
with your own words, pick one, and get a complete static site plus 3.75 × 2.25 in cards
with a scannable QR code. Publish straight to GitHub Pages, or take the zip anywhere.

## It runs real Python

The generator is Python. Rather than maintain a second JavaScript version that would
quietly drift, the app ships [Pyodide](https://pyodide.org) and runs the same code the
desktop tool runs. Output is byte-identical — verified by diffing a phone-generated site
against a desktop build, all 20 files.

`py/` is a copy of the generator, made by `sync.py`. Only `py/bridge.py` is app code.

## Offline

A service worker precaches the shell, the generator and the ~13 MB runtime on first
load. After that it never needs the network — it boots, generates and exports with the
server unreachable. Publishing is the only part that wants a connection.

## Layout

```
index.html app.css app.js      the app
sw.js manifest.webmanifest     offline + install
py/                            the generator, synced from the skill
py/bridge.py                   the seam between the UI and the generator
vendor/pyodide/                the runtime, committed so offline is real
sync.py                        copy the generator in, re-stamp the cache
```

## Running it locally

```bash
python3 -m http.server 8124 --directory .
```

Then open <http://localhost:8124>. Service workers need `localhost` or HTTPS, so opening
`index.html` off the filesystem will not exercise offline mode.

## Updating

```bash
python3 sync.py && git add -A && git commit -m "sync generator" && git push
```

`sync.py` stamps a content digest into `sw.js`, which is what makes phones pick up the
change instead of serving the old cache forever.

## Your data

Everything you type stays in `localStorage` on your device. Nothing is uploaded. The
only outbound request the app ever makes is to `api.github.com`, and only when you tap
Publish. A GitHub token, if you save one, is stored on that device and sent nowhere else.
