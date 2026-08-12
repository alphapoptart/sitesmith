#!/usr/bin/env python3
"""sitesmith — answer a few questions, get a whole website and matching business cards.

  python3 sitesmith.py new                     interview, then build the preview gallery
  python3 sitesmith.py gallery --brief b.json  rebuild the gallery from an existing brief
  python3 sitesmith.py build --layout bold --theme sand
  python3 sitesmith.py serve                   preview locally
  python3 sitesmith.py list                    show every layout and theme

Everything is stdlib. Nothing is uploaded. Nothing costs money.
"""

import argparse
import json
import os
import shutil
import sys
import webbrowser

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import cards
import content
import css
import design
import layouts
from design import LAYOUTS, THEMES, data_uri, favicon, logo_mark, pattern_svg

DEFAULT_OUT = "sitesmith-out"


# --- interview ---------------------------------------------------------------

def ask(prompt, default="", required=False):
    suffix = f" [{default}]" if default else ""
    while True:
        try:
            value = input(f"  {prompt}{suffix}: ").strip()
        except EOFError:
            print()
            return default
        if not value:
            value = default
        if value or not required:
            return value
        print("    ^ needed, this one shows up all over the site")


def choose(prompt, options, default_key):
    print(f"\n  {prompt}")
    keys = list(options)
    for i, key in enumerate(keys, 1):
        label = options[key]
        print(f"    {i:>2}. {label}")
    while True:
        raw = input(f"  Number [{keys.index(default_key) + 1}]: ").strip()
        if not raw:
            return default_key
        if raw.isdigit() and 1 <= int(raw) <= len(keys):
            return keys[int(raw) - 1]
        if raw in options:
            return raw
        print("    ^ pick one of the numbers")


def ask_yes(prompt, default=False):
    suffix = "[Y/n]" if default else "[y/N]"
    try:
        raw = input(f"  {prompt} {suffix}: ").strip().lower()
    except EOFError:
        print()
        return default
    if not raw:
        return default
    return raw[0] == "y"


def ask_prices(names):
    """Per-service prices, typed as free text so any currency or wording works.
    Blank means that service simply shows no price."""
    print()
    if not ask_yes("Show prices on the site?"):
        return [{"title": n, "price": ""} for n in names], "", False

    currency = ask("Currency symbol (blank for none)", "£")
    after = False
    if currency:
        # Symbols normally lead, currency words normally trail — default to whichever
        # matches, but let them say otherwise.
        after = not content.has_currency(currency)
        example_before, example_after = f"{currency}18", f"18 {currency}"
        shown = example_after if after else example_before
        other = example_before if after else example_after
        print(f'    A price typed as "18" will show as "{shown}".')
        if ask_yes(f'Show it as "{other}" instead?', False):
            after = not after

    print("  Type prices however you want them to read — 18, from 120, 45/hr, POA, Free.")
    print("  Press Enter to leave a service without a price.\n")
    out = []
    for name in names:
        raw = ask(f'Price for "{name}"', "")
        out.append({"title": name, "price": raw})
    if not any(s["price"] for s in out):
        print("  No prices entered — the price column will be left off.")
    return out, currency, after


def interview():
    print("\n  sitesmith — a few questions, then a whole website.")
    print("  Press Enter to accept anything in [brackets]. You can edit brief.json later.\n")
    b = dict(content.DEFAULT_BRIEF)

    b["name"] = ask("Business name", required=True)
    b["tagline"] = ask("What do you do, in one line?",
                       "Honest work, done properly")
    b["preset"] = choose("Which is closest to your line of work?",
                         {k: v["label"] for k, v in content.PRESETS.items()}, "general")
    preset = content.PRESETS[b["preset"]]

    b["city"] = ask("Town / city / area you serve")
    b["phone"] = ask("Phone number")
    b["email"] = ask("Email address")
    b["address"] = ask("Street address (optional)")
    b["hours"] = ask("Opening hours", "Mon–Fri, 8am – 6pm")

    print("\n  Services — comma separated. Enter accepts the defaults for your trade:")
    print("    " + ", ".join(s[0] for s in preset["services"][:6]))
    raw = ask("Services", "")
    names = [s.strip() for s in raw.split(",") if s.strip()]
    if not names:
        names = [s[0] for s in preset["services"][:6]]
    b["services"], b["currency"], b["currency_after"] = ask_prices(names)

    b["owner"] = ask("Name on the business card")
    b["owner_title"] = ask("Job title on the card", "Owner")
    b["years"] = ask("Years in business (optional)")
    b["domain"] = ask("Domain, if you have one (e.g. riversideplumbing.co.uk)")
    b["cta"] = ask("Main button text", preset["cta"])

    return content.normalise(b)


# --- writing a site ----------------------------------------------------------

def write_site(out_dir, b, t, layout, pages=None, preview=False):
    """`preview=True` skips the assets a one-page thumbnail never references —
    at 160 gallery combinations that is a few hundred files saved."""
    os.makedirs(out_dir, exist_ok=True)
    assets = os.path.join(out_dir, "assets")
    os.makedirs(assets, exist_ok=True)

    for page in (pages or [p for p, _ in layouts.PAGES] + ["404.html"]):
        with open(os.path.join(out_dir, page), "w", encoding="utf-8") as fh:
            fh.write(layouts.render(page, b, t, layout))

    with open(os.path.join(assets, "site.css"), "w", encoding="utf-8") as fh:
        fh.write(css.base_css(t) + "\n" + css.layout_css(layout, t))
    with open(os.path.join(assets, "site.js"), "w", encoding="utf-8") as fh:
        fh.write(css.site_js())
    with open(os.path.join(assets, "favicon.svg"), "w", encoding="utf-8") as fh:
        fh.write(favicon(b["name"], t))
    if not preview:
        with open(os.path.join(assets, "logo.svg"), "w", encoding="utf-8") as fh:
            fh.write(logo_mark(b["name"], t, size=256, ink=t["accent"], plate=t["bg"]))
        with open(os.path.join(assets, "og.svg"), "w", encoding="utf-8") as fh:
            fh.write(og_image(b, t))
    return out_dir


def og_image(b, t):
    """1200x630 social preview card."""
    name = layouts.e(b["name"])
    tag = layouts.e(b["tagline"])
    mark = logo_mark(b["name"], t, size=110, ink=t["accent"], plate=t["hero_bg"])
    mark = cards._nested(mark, 90, 90, 110)
    n_size = cards.fit_size(b["name"], 1020, 92, 44)
    lines = cards.wrap(b["tagline"], 1020, 38, 2)
    tag_svg = "".join(
        f'<text x="90" y="{432 + i * 52}" fill="{t["hero_ink"]}" opacity="0.75" '
        f'font-family="{t["font_body"]}" font-size="38">{layouts.e(l)}</text>'
        for i, l in enumerate(lines))
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="630" '
        f'viewBox="0 0 1200 630" role="img" aria-label="{name}">'
        f'<rect width="1200" height="630" fill="{t["hero_bg"]}"/>'
        f'<path d="M1200 250 L1200 630 L820 630 Z" fill="{t["accent"]}" opacity="0.85"/>'
        f'{mark}'
        f'<text x="90" y="360" fill="{t["hero_ink"]}" font-family="{t["font_display"]}" '
        f'font-size="{n_size}" font-weight="{t["display_weight"]}" letter-spacing="-2"'
        f'{cards._case(t)}>{name}</text>{tag_svg}'
        f'<text x="90" y="570" fill="{t["hero_ink"]}" opacity="0.6" '
        f'font-family="{t["font_body"]}" font-size="28" letter-spacing="2">'
        f'{layouts.e(b["city"] or (b["site_url"] or "").replace("https://", ""))}</text>'
        f'</svg>')


# --- gallery -----------------------------------------------------------------

GALLERY_CSS = """
:root { color-scheme: light dark; --ink:#10131a; --sub:#5d6675; --bg:#f2f4f8;
        --card:#fff; --line:#dfe4ec; --accent:#1d4ed8; }
@media (prefers-color-scheme: dark) {
  :root { --ink:#eef1f7; --sub:#98a3b5; --bg:#0c0f15; --card:#141922; --line:#242b38;
          --accent:#7aa2ff; }
}
* { box-sizing: border-box; }
body { margin:0; background:var(--bg); color:var(--ink);
       font:15px/1.6 ui-sans-serif,-apple-system,"Segoe UI",Roboto,sans-serif; }
header { padding:2.5rem clamp(1rem,4vw,3rem) 1.5rem; }
h1 { margin:0 0 .35rem; font-size:clamp(1.6rem,1.2rem+1.6vw,2.3rem); letter-spacing:-.03em; }
header p { margin:0; color:var(--sub); max-width:70ch; }
.bar { position:sticky; top:0; z-index:10; padding:1rem clamp(1rem,4vw,3rem);
       background:color-mix(in srgb, var(--bg) 88%, transparent); backdrop-filter:blur(12px);
       border-bottom:1px solid var(--line); display:flex; flex-wrap:wrap; gap:1.25rem 2rem; }
.bar fieldset { border:0; margin:0; padding:0; display:flex; flex-wrap:wrap;
                gap:.4rem; align-items:center; }
.bar legend { float:left; font-size:.72rem; letter-spacing:.14em; text-transform:uppercase;
              color:var(--sub); margin-right:.7rem; padding:0; }
.chip { border:1px solid var(--line); background:var(--card); color:var(--ink);
        padding:.36rem .78rem; border-radius:999px; cursor:pointer; font:inherit;
        font-size:.86rem; transition:.15s; }
.chip:hover { border-color:var(--accent); }
.chip[aria-pressed="true"] { background:var(--accent); border-color:var(--accent); color:#fff; }
.count { margin-left:auto; color:var(--sub); font-size:.86rem; align-self:center; }
main { padding:1.75rem clamp(1rem,4vw,3rem) 5rem;
       display:grid; gap:1.75rem;
       grid-template-columns:repeat(auto-fill,minmax(min(100%,340px),1fr)); }
figure { margin:0; background:var(--card); border:1px solid var(--line);
         border-radius:14px; overflow:hidden; display:flex; flex-direction:column; }
figure[hidden] { display:none; }
/* JS scales each iframe to its card width; these are the pre-JS defaults. */
.shot { height:390px; overflow:hidden; position:relative; background:#fff;
        border-bottom:1px solid var(--line); }
.shot iframe { width:1280px; height:1560px; border:0; transform:scale(.25);
               transform-origin:0 0; pointer-events:none; }
figcaption { padding:.9rem 1.1rem 1.1rem; display:grid; gap:.55rem; }
.title { font-weight:650; letter-spacing:-.01em; }
.title span { color:var(--sub); font-weight:400; }
.blurb { color:var(--sub); font-size:.85rem; margin:0; }
.acts { display:flex; gap:.5rem; flex-wrap:wrap; }
.acts a, .acts button { font:inherit; font-size:.85rem; padding:.42rem .8rem;
    border-radius:8px; border:1px solid var(--line); background:transparent;
    color:var(--ink); text-decoration:none; cursor:pointer; }
.acts .primary { background:var(--accent); border-color:var(--accent); color:#fff; }
.acts a:hover, .acts button:hover { border-color:var(--accent); }
code { font:12.5px/1.5 ui-monospace,SFMono-Regular,Menlo,monospace; color:var(--sub);
       word-break:break-all; }
.empty { grid-column:1/-1; text-align:center; color:var(--sub); padding:4rem 0; }
"""

GALLERY_JS = """
// Each preview is a real 1280px-wide page scaled down, so the scale has to track
// the card width or the right-hand side gets clipped.
var SHOT_W = 1280, SHOT_H = 1560;
function fitShots() {
  document.querySelectorAll('.shot').forEach(function (shot) {
    var frame = shot.querySelector('iframe');
    var k = shot.clientWidth / SHOT_W;
    frame.style.transform = 'scale(' + k + ')';
    shot.style.height = Math.round(SHOT_H * k) + 'px';
  });
}
window.addEventListener('resize', fitShots);
window.addEventListener('load', fitShots);

var state = { layout: 'all', theme: 'all' };
function apply() {
  var shown = 0;
  document.querySelectorAll('figure').forEach(function (f) {
    var ok = (state.layout === 'all' || f.dataset.layout === state.layout) &&
             (state.theme === 'all' || f.dataset.theme === state.theme);
    f.hidden = !ok;
    if (ok) shown++;
  });
  document.querySelector('.count').textContent = shown + ' of ' + TOTAL + ' shown';
  document.querySelector('.empty').hidden = shown > 0;
  fitShots();
}
document.querySelectorAll('.chip').forEach(function (chip) {
  chip.addEventListener('click', function () {
    var group = chip.dataset.group;
    state[group] = chip.dataset.value;
    document.querySelectorAll('.chip[data-group="' + group + '"]').forEach(function (c) {
      c.setAttribute('aria-pressed', String(c === chip));
    });
    apply();
  });
});
document.querySelectorAll('button.copy').forEach(function (btn) {
  btn.addEventListener('click', function () {
    navigator.clipboard.writeText(btn.dataset.cmd).then(function () {
      var old = btn.textContent;
      btn.textContent = 'Copied';
      setTimeout(function () { btn.textContent = old; }, 1400);
    });
  });
});
apply();
"""


def build_gallery(out_root, b, brief_path, open_it=True):
    gal = os.path.join(out_root, "_gallery")
    if os.path.isdir(gal):
        shutil.rmtree(gal)
    os.makedirs(gal, exist_ok=True)

    figures = []
    total = 0
    for layout in LAYOUTS:
        for theme_key in THEMES:
            t = design.theme(theme_key)
            combo = f"{layout}__{theme_key}"
            write_site(os.path.join(gal, combo), b, t, layout,
                       pages=["index.html"], preview=True)
            cmd = (f"python3 sitesmith.py build --brief {brief_path} "
                   f"--layout {layout} --theme {theme_key}")
            figures.append(f"""<figure data-layout="{layout}" data-theme="{theme_key}">
  <div class="shot"><iframe src="{combo}/index.html" loading="lazy" tabindex="-1"
       title="{layout} layout, {theme_key} theme" scrolling="no"></iframe></div>
  <figcaption>
    <div class="title">{layout.title()} <span>/ {THEMES[theme_key]['label']}</span></div>
    <p class="blurb">{layouts.e(THEMES[theme_key]['blurb'])}</p>
    <div class="acts">
      <a class="primary" href="{combo}/index.html" target="_blank" rel="noopener">Open full size</a>
      <button class="copy" data-cmd="{layouts.e(cmd)}">Copy build command</button>
    </div>
    <code>--layout {layout} --theme {theme_key}</code>
  </figcaption>
</figure>""")
            total += 1

    def chips(group, items, labels):
        out = [f'<button class="chip" data-group="{group}" data-value="all" '
               f'aria-pressed="true">All</button>']
        for key in items:
            out.append(f'<button class="chip" data-group="{group}" data-value="{key}" '
                       f'aria-pressed="false">{layouts.e(labels[key])}</button>')
        return "".join(out)

    html = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{layouts.e(b['name'])} — pick a design</title>
<style>{GALLERY_CSS}</style></head><body>
<header>
  <h1>{layouts.e(b['name'])} — pick a design</h1>
  <p>{total} combinations, all built with your own content. Filter, open one full size,
     then run its build command to generate the complete site, the business cards and
     the deploy notes.</p>
</header>
<div class="bar">
  <fieldset><legend>Layout</legend>{chips('layout', LAYOUTS, {k: k.title() for k in LAYOUTS})}</fieldset>
  <fieldset><legend>Theme</legend>{chips('theme', THEMES, {k: v['label'] for k, v in THEMES.items()})}</fieldset>
  <span class="count"></span>
</div>
<main>{''.join(figures)}<p class="empty" hidden>Nothing matches those two filters.</p></main>
<script>var TOTAL = {total};{GALLERY_JS}</script>
</body></html>"""

    index = os.path.join(gal, "index.html")
    with open(index, "w", encoding="utf-8") as fh:
        fh.write(html)
    if open_it:
        webbrowser.open("file://" + os.path.abspath(index))
    return index, total


# --- docs --------------------------------------------------------------------

def deploy_md(b, t, layout, site_dir):
    domain = b["domain"] or "yourbusiness.com"
    return f"""# Deploying {b['name']}

The site in this folder is plain HTML, CSS and one small JavaScript file. No build
step, no framework, no dependencies. Any static host will serve it, and the three
below are free.

## Preview it locally first

```bash
cd {os.path.basename(site_dir)} && python3 -m http.server 8080
```

Then open <http://localhost:8080>. Stop it with Ctrl-C.

## Option 1 — Netlify Drop (easiest, and the contact form works)

1. Go to <https://app.netlify.com/drop>
2. Drag this whole folder onto the page.
3. It is live in about ten seconds on a `something.netlify.app` address.

The contact form is already wired for Netlify Forms — submissions land in the Netlify
dashboard under **Forms**, and you can have them emailed to you. Free tier covers 100
submissions a month.

To use your own domain: Netlify → Domain settings → Add a domain. Free HTTPS is
issued automatically.

## Option 2 — Cloudflare Pages

1. <https://pages.cloudflare.com> → Create a project → Direct Upload.
2. Upload this folder. Free, unlimited bandwidth, free HTTPS.

The contact form will **not** work here as-is — see "Making the form work elsewhere".

## Option 3 — GitHub Pages

```bash
cd {os.path.basename(site_dir)}
git init && git add -A && git commit -m "site"
gh repo create {b['slug']}-site --public --source=. --push
```

Then repo → Settings → Pages → Deploy from branch → `main` / root.

## Making the form work elsewhere

If you are not on Netlify, sign up at <https://formspree.io> (free tier: 50 submissions
a month), then in `contact.html` change:

```html
<form class="enquiry" name="enquiry" method="POST" data-netlify="true"
```

to:

```html
<form class="enquiry" name="enquiry" method="POST" action="https://formspree.io/f/YOURID"
```

Until then the phone and email links work fine on every host.

## Your own domain

A `.com` runs about $10–15 a year — that and hosting are the only things here that
cost anything. Cloudflare Registrar sells at cost. Point it at your host with the DNS
records the host gives you.

{"After you buy `" + domain + "`, set `domain` in brief.json and re-run the build so the QR code on the business card points at the real address." if not b['domain'] else "The business card QR code points at https://" + domain + " — make sure that resolves before you print."}

## What was generated

- `index.html`, `services.html`, `about.html`, `contact.html`, `404.html`
- `assets/` — one stylesheet, one script, logo, favicon and social preview image
- `cards/` — print-ready business cards, see `cards/README.md`
- `CONTENT.md` — the list of things still to fill in
- `sitemap.xml`, `robots.txt`

Design: **{layout}** layout, **{THEMES[t['key']]['label']}** theme.
Rebuild with a different one at any time:

```bash
python3 sitesmith.py build --brief brief.json --layout bold --theme midnight
```
"""


def cards_md(b, t):
    payload, caption = cards.qr_payload(b)
    target = ("your website" if b["site_url"]
              else "a contact card that saves straight into a phone")
    return f"""# Business cards — {b['name']}

## Send this to the printer

`cards.pdf` — two pages (front, back), 3.75 × 2.25 in, 300 dpi, bleed included,
no crop marks. That is exactly what VistaPrint, Moo, Solopress, Instantprint and
most online printers ask for. Upload it as a double-sided design.

## Check it first

Open `cards-proof.html` in a browser. It shows both sides at actual size with the
trim line (red) and safe zone (blue) marked. Anything past the red line gets cut off —
that is intentional, it is what stops a white sliver appearing at the edge.

## The QR code

It points at {target}. It was tested against a real decoder, but scan it off the proof
with your own phone before you order a thousand of them.

Payload: `{payload[:90]}{"…" if len(payload) > 90 else ""}`
Caption on the card: "{caption}"

## Editing

`card-front.svg` and `card-back.svg` open in Figma, Inkscape, Illustrator or Affinity —
all vector, all editable. Free option: Inkscape (<https://inkscape.org>). If you change
them, re-export and print from the SVGs rather than the old PDF.

Or change `brief.json` and re-run the build, which regenerates everything together.

## No Chrome?

If `cards.pdf` is missing, open `cards-print.html` in any browser and print to PDF with
paper size 3.75 × 2.25 in and margins set to none.
"""


def content_md(b, t, layout):
    items = content.placeholders(b)
    priced = [s for s in b["services"] if s["price"]]
    cur = (b.get("currency") or "").strip()
    where = ("after" if b.get("currency_after") else "before")
    cur_note = (f" Your currency is `{cur}`, added {where} any price typed as a bare "
                f"number; anything you write out in full is left exactly as typed."
                if cur else
                " No currency is set, so prices appear exactly as typed — add "
                "`\"currency\": \"£\"` to `brief.json` if you would rather type bare "
                "numbers.")
    if not priced:
        price_note = ("You gave no prices, so nothing about cost appears anywhere on "
                      "the site. Add a `price` to any service in `brief.json` "
                      "(free text — `75`, `from 120`, `45/hr`, `POA`) and re-run "
                      "the build to switch the price column on.")
    elif len(priced) < len(b["services"]):
        missing = ", ".join(s["title"] for s in b["services"] if not s["price"])
        price_note = (f"{len(priced)} of {len(b['services'])} services have a price. "
                      f"The rest show none at all, which is fine — but check that is "
                      f"deliberate for: {missing}.{cur_note}")
    else:
        price_note = ("Every service has a price. Make sure they are current before "
                      "this goes live — a stale price on a website is an argument "
                      f"waiting to happen.{cur_note}")
    if items:
        rows = "\n".join(f"- **{label}** — {text}" for label, text in items)
        head = (f"{len(items)} things still need your words. Everything marked "
                f"`REPLACE` on the site is listed here.\n\n{rows}")
    else:
        head = "Nothing is left as a placeholder. Read it through anyway."
    return f"""# Still to do — {b['name']}

## Placeholders

{head}

## Always worth checking

- **The prices.** {price_note}
- **The testimonial.** It is a labelled placeholder on purpose. Paste in a real review
  with a real name, or delete the block. Do not invent one.
- **The three reasons to choose you** (insured, fixed prices, and so on) came from a
  template for your trade. Make sure each one is actually true of you before it goes live.
- **Photos.** The artwork is generated shapes — deliberately abstract, and free. Real
  photos of real work will beat it every time. Drop them in `assets/` and swap the
  `<svg>` blocks for `<img src="assets/your-photo.jpg" alt="...">`.
- **The about paragraph.** Two or three sentences in your own voice does more than
  anything a generator can write for you.

## Where things live

| What | File |
| --- | --- |
| Headline, tagline, services, prices, contact details | `brief.json` (then re-run the build) |
| One-off wording tweaks | the `.html` files directly |
| Colours, spacing, fonts | `assets/site.css` — the `:root` block at the top |
| Business card content | `brief.json` → `owner`, `owner_title`, `phone`, `email`, `domain` |

Re-running the build overwrites the HTML, so make wording changes in `brief.json` if
you plan to try other designs.
"""


def sitemap(b):
    if not b["site_url"]:
        return None
    urls = "".join(f"  <url><loc>{b['site_url']}/{'' if p == 'index.html' else p}</loc></url>\n"
                   for p, _ in layouts.PAGES)
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
            f"{urls}</urlset>\n")


# --- commands ----------------------------------------------------------------

def cmd_build(args, b):
    t = design.theme(args.theme)
    site_dir = os.path.join(args.out, b["slug"])
    if os.path.isdir(site_dir):
        shutil.rmtree(site_dir)
    write_site(site_dir, b, t, args.layout)

    card_files, warning = cards.write(os.path.join(site_dir, "cards"), b, t)

    b_out = dict(b)
    b_out["layout"], b_out["theme"] = args.layout, args.theme
    for key in ("slug", "steps", "points", "faq", "headline", "hero_lede",
                "where", "site_url", "has_prices"):
        b_out.pop(key, None)
    with open(os.path.join(site_dir, "brief.json"), "w", encoding="utf-8") as fh:
        json.dump(b_out, fh, indent=2, ensure_ascii=False)

    docs = {"DEPLOY.md": deploy_md(b, t, args.layout, site_dir),
            "CONTENT.md": content_md(b, t, args.layout),
            "cards/README.md": cards_md(b, t),
            "robots.txt": ("User-agent: *\nAllow: /\n"
                           + (f"Sitemap: {b['site_url']}/sitemap.xml\n" if b["site_url"] else ""))}
    sm = sitemap(b)
    if sm:
        docs["sitemap.xml"] = sm
    for name, text in docs.items():
        with open(os.path.join(site_dir, name), "w", encoding="utf-8") as fh:
            fh.write(text)

    todo = len(content.placeholders(b))
    print(f"\n  Built {b['name']} — {args.layout} / {THEMES[args.theme]['label']}")
    print(f"  {site_dir}/")
    print(f"    index, services, about, contact, 404   5 pages")
    print(f"    cards/cards.pdf                        {'yes' if not warning else 'NOT BUILT'}")
    print(f"    CONTENT.md                             {todo} placeholder{'s' if todo != 1 else ''} to fill in")
    print(f"    DEPLOY.md                              free hosting, step by step")
    if warning:
        print(f"\n  ! {warning}")
    print(f"\n  Preview it:\n    cd {site_dir} && python3 -m http.server 8080")
    return site_dir


def cmd_list():
    print("\n  Layouts\n")
    for key, blurb in LAYOUTS.items():
        print(f"    {key:<10} {blurb}")
    print("\n  Themes\n")
    for key, t in THEMES.items():
        print(f"    {key:<10} {t['blurb']}")
    print()


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd")

    def common(p):
        p.add_argument("--brief", default="brief.json")
        p.add_argument("--out", default=DEFAULT_OUT)

    p_new = sub.add_parser("new", help="interview, then build the preview gallery")
    common(p_new)
    p_new.add_argument("--no-open", action="store_true")

    p_gal = sub.add_parser("gallery", help="rebuild the gallery from an existing brief")
    common(p_gal)
    p_gal.add_argument("--no-open", action="store_true")

    p_build = sub.add_parser("build", help="build the full site + cards")
    common(p_build)
    p_build.add_argument("--layout", choices=list(LAYOUTS))
    p_build.add_argument("--theme", choices=list(THEMES))

    p_all = sub.add_parser("build-all", help="build every combination as its own site")
    common(p_all)

    p_serve = sub.add_parser("serve", help="preview a folder over http")
    p_serve.add_argument("path", nargs="?", default=DEFAULT_OUT)
    p_serve.add_argument("--port", type=int, default=8080)

    sub.add_parser("list", help="show every layout and theme")

    p_demo = sub.add_parser("demo", help="build a sample business end to end")
    common(p_demo)

    args = ap.parse_args()
    cmd = args.cmd or "new"

    if cmd == "list":
        return cmd_list()

    if cmd == "serve":
        import http.server
        import socketserver
        os.chdir(args.path)
        handler = http.server.SimpleHTTPRequestHandler
        with socketserver.TCPServer(("", args.port), handler) as httpd:
            url = f"http://localhost:{args.port}"
            print(f"  Serving {os.getcwd()} at {url}  (Ctrl-C to stop)")
            webbrowser.open(url)
            try:
                httpd.serve_forever()
            except KeyboardInterrupt:
                print("\n  stopped")
        return

    if cmd == "demo":
        b = content.normalise(json.loads(DEMO_BRIEF))
        args.layout, args.theme = b["layout"], b["theme"]
        os.makedirs(args.out, exist_ok=True)
        with open(os.path.join(args.out, "brief.json"), "w", encoding="utf-8") as fh:
            json.dump(json.loads(DEMO_BRIEF), fh, indent=2)
        return cmd_build(args, b)

    if cmd == "new":
        b = interview()
        os.makedirs(args.out, exist_ok=True)
        brief_path = os.path.join(args.out, "brief.json")
        raw = {k: v for k, v in b.items() if k in content.DEFAULT_BRIEF}
        with open(brief_path, "w", encoding="utf-8") as fh:
            json.dump(raw, fh, indent=2, ensure_ascii=False)
        print(f"\n  Saved {brief_path}")
        print("  Building previews of every layout and theme…")
        index, total = build_gallery(args.out, b, brief_path, open_it=not args.no_open)
        print(f"  {total} previews → {index}")
        print("\n  Pick one, then run the command shown under it. For example:")
        print(f"    python3 {os.path.basename(__file__)} build --brief {brief_path} "
              f"--layout classic --theme slate")
        return

    if not os.path.exists(args.brief):
        sys.exit(f"  No brief at {args.brief}. Run `new` first, or pass --brief.")
    b = content.load(args.brief)

    if cmd == "gallery":
        index, total = build_gallery(args.out, b, args.brief, open_it=not args.no_open)
        print(f"  {total} previews → {index}")
        return

    if cmd == "build-all":
        for layout in LAYOUTS:
            for theme_key in THEMES:
                t = design.theme(theme_key)
                d = os.path.join(args.out, "all", f"{layout}__{theme_key}")
                if os.path.isdir(d):
                    shutil.rmtree(d)
                write_site(d, b, t, layout)
                cards.write(os.path.join(d, "cards"), b, t)
        print(f"  Built {len(LAYOUTS) * len(THEMES)} sites in {args.out}/all/")
        return

    if cmd == "build":
        args.layout = args.layout or b.get("layout") or "classic"
        args.theme = args.theme or b.get("theme") or "slate"
        return cmd_build(args, b)


DEMO_BRIEF = json.dumps({
    "name": "Riverside Plumbing & Heating",
    "tagline": "Emergency plumbing and boiler work, seven days a week",
    "preset": "trades",
    "city": "Shrewsbury",
    "phone": "01743 555 0142",
    "email": "hello@riversideplumbing.co.uk",
    "address": "4 Mill Yard, Shrewsbury SY1 2AB",
    "hours": "Mon–Sat 7am – 8pm · Emergencies 24/7",
    "currency": "£",
    "currency_after": False,
    "services": [
        {"title": "Emergency call-outs", "price": "from 90"},
        {"title": "Repairs & fault finding", "price": "from 65"},
        {"title": "Installations", "price": "Quoted per job"},
        {"title": "Servicing & safety checks", "price": "85"},
        {"title": "Bathrooms & kitchens", "price": "Quoted per job"},
        {"title": "Maintenance contracts", "price": "from 25/month"},
    ],
    "owner": "Dan Whitcombe",
    "owner_title": "Master Plumber",
    "years": "18",
    "domain": "riversideplumbing.co.uk",
    "cta": "Get a fixed quote",
    "layout": "bold",
    "theme": "ocean",
})

if __name__ == "__main__":
    main()
