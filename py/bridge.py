"""The seam between the browser UI and the sitesmith generator.

Everything here runs inside Pyodide against the unmodified generator modules, so
whatever the phone produces is what the Mac produces. Nothing in this file
re-implements generation — it only marshals arguments and collects output.
"""

import base64
import io
import json
import os
import shutil

import cards
import content
import design
import layouts
import sitesmith


def catalogue():
    """Everything the UI needs to draw its pickers."""
    return json.dumps({
        "layouts": [{"key": k, "label": k.title(), "blurb": v}
                    for k, v in design.LAYOUTS.items()],
        "themes": [{"key": k, "label": t["label"], "blurb": t["blurb"],
                    "dark": t["dark"], "accent": t["accent"], "bg": t["bg"],
                    "text": t["text"]}
                   for k, t in design.THEMES.items()],
        "presets": [{"key": k, "label": v["label"],
                     "services": [s[0] for s in v["services"][:6]],
                     "cta": v["cta"]}
                    for k, v in content.PRESETS.items()],
        "defaults": content.DEFAULT_BRIEF,
    })


def _brief(brief_json):
    raw = json.loads(brief_json)
    merged = dict(content.DEFAULT_BRIEF)
    merged.update({k: v for k, v in raw.items() if k in content.DEFAULT_BRIEF})
    return content.normalise(merged)


def normalise(brief_json):
    """Round-trip a brief so the UI can show derived copy and price formatting."""
    b = _brief(brief_json)
    return json.dumps({
        "headline": b["headline"], "hero_lede": b["hero_lede"],
        "services": b["services"], "has_prices": b["has_prices"],
        "slug": b["slug"], "cta": b["cta"],
        "placeholders": [{"where": w, "text": t} for w, t in content.placeholders(b)],
    })


def preview(brief_json, layout, theme_key):
    """One self-contained page for a gallery tile — styles inlined so the iframe
    needs no network and no file paths."""
    b = _brief(brief_json)
    if b.get("logo"):
        b = dict(b, logo_href=b["logo"])
    t = design.theme(theme_key)
    html = layouts.render("index.html", b, t, layout)
    sheet = css_for(layout, t)
    html = html.replace('<link rel="stylesheet" href="assets/site.css">',
                        f"<style>{sheet}</style>")
    html = html.replace('<link rel="icon" href="assets/favicon.svg" type="image/svg+xml">', "")
    html = html.replace('<script src="assets/site.js" defer></script>',
                        f"<script>{_site_js()}</script>")
    return html


def css_for(layout, t):
    import css as css_mod
    return css_mod.base_css(t) + "\n" + css_mod.layout_css(layout, t)


def _site_js():
    import css as css_mod
    return css_mod.site_js()


def build(brief_json, layout, theme_key):
    """Generate the whole site into the in-memory filesystem, then hand every file
    back to JavaScript so it can be zipped or previewed."""
    b = _brief(brief_json)
    t = design.theme(theme_key)
    root = "/tmp/build"
    if os.path.isdir(root):
        shutil.rmtree(root)
    site = os.path.join(root, b["slug"])
    sitesmith.write_site(site, b, t, layout)

    card_dir = os.path.join(site, "cards")
    os.makedirs(card_dir, exist_ok=True)
    front, back = cards.front(b, t), cards.back(b, t)
    files = {
        "cards/card-front.svg": front,
        "cards/card-back.svg": back,
        "cards/cards-print.html": cards.PRINT_HTML.format(
            name=cards.esc(b["name"]), front=front, back=back,
            w=cards.TRIM_W_IN + cards.BLEED_IN * 2,
            h=cards.TRIM_H_IN + cards.BLEED_IN * 2),
        "cards/cards-proof.html": cards.PROOF_HTML.format(
            name=cards.esc(b["name"]), front=front, back=back),
        "cards/README.md": sitesmith.cards_md(b, t),
        "DEPLOY.md": sitesmith.deploy_md(b, t, layout, site),
        "CONTENT.md": sitesmith.content_md(b, t, layout),
        "robots.txt": ("User-agent: *\nAllow: /\n"
                       + (f"Sitemap: {b['site_url']}/sitemap.xml\n" if b["site_url"] else "")),
    }
    sm = sitesmith.sitemap(b)
    if sm:
        files["sitemap.xml"] = sm

    # Follow DEFAULT_BRIEF's key order rather than whatever order the UI happened to
    # send, so the file is byte-identical to a desktop build of the same brief.
    raw = json.loads(brief_json)
    keep = {k: raw[k] for k in content.DEFAULT_BRIEF if k in raw}
    keep["services"] = b["services"]
    # Persist the generated about paragraph the same way a desktop build does, so
    # the file round-trips and the owner has something to edit.
    keep["about"] = b["about"]
    keep["layout"], keep["theme"] = layout, theme_key
    files["brief.json"] = json.dumps(keep, indent=2, ensure_ascii=False)

    for rel, text in files.items():
        path = os.path.join(site, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(text)

    # A logo asset is bytes, not text, so anything that will not decode as UTF-8 is
    # handed over base64-encoded and rebuilt as a Uint8Array on the JavaScript side.
    out, blobs = {}, {}
    for dirpath, _dirs, names in os.walk(site):
        for name in names:
            full = os.path.join(dirpath, name)
            rel = os.path.relpath(full, site).replace(os.sep, "/")
            data = open(full, "rb").read()
            try:
                out[rel] = data.decode("utf-8")
            except UnicodeDecodeError:
                blobs[rel] = base64.b64encode(data).decode("ascii")

    return json.dumps({
        "slug": b["slug"], "name": b["name"], "files": out, "binary": blobs,
        "placeholders": len(content.placeholders(b)),
        "cards_print": files["cards/cards-print.html"],
        "cards_proof": files["cards/cards-proof.html"],
    })


def card_proof(brief_json, theme_key):
    """Just the card proof, for the preview pane — cheaper than a whole build."""
    b = _brief(brief_json)
    t = design.theme(theme_key)
    front, back = cards.front(b, t), cards.back(b, t)
    return json.dumps({
        "proof": cards.PROOF_HTML.format(name=cards.esc(b["name"]),
                                         front=front, back=back),
        "print": cards.PRINT_HTML.format(
            name=cards.esc(b["name"]), front=front, back=back,
            w=cards.TRIM_W_IN + cards.BLEED_IN * 2,
            h=cards.TRIM_H_IN + cards.BLEED_IN * 2),
    })


def demo_brief():
    return sitesmith.DEMO_BRIEF
