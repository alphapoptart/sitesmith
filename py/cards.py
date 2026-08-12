"""Print-ready business cards.

The SVG is the single source of truth; the PDF is Chrome printing a page that
contains that same SVG at exact physical size, so the two can never drift.

Geometry: 3.5in x 2in trim + 0.125in bleed on every edge = 3.75in x 2.25in.
Everything important stays inside a further 0.125in safety margin. Units below
are pixels at 300dpi, which is what commercial printers want.
"""

import os
import re
import shutil
import subprocess
import tempfile
import time

import qr
from design import brand_svg, icon_svg, pattern_svg

DPI = 300
BLEED_IN = 0.125
TRIM_W_IN, TRIM_H_IN = 3.5, 2.0
W = int((TRIM_W_IN + BLEED_IN * 2) * DPI)   # 1125
H = int((TRIM_H_IN + BLEED_IN * 2) * DPI)   # 675
SAFE = int(0.25 * DPI)                       # 75px from the outer edge

CHROME_PATHS = [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
    "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser",
]


def find_chrome():
    for p in CHROME_PATHS:
        if os.path.exists(p):
            return p
    for name in ("google-chrome", "chromium", "chromium-browser", "microsoft-edge"):
        found = shutil.which(name)
        if found:
            return found
    return None


def esc(text):
    return (str(text or "").replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


# Rough advance widths as a fraction of font size. Good enough to shrink-to-fit
# without shipping font metrics.
_WIDE = set("MWmw@%")
_NARROW = set("iljtfrI.,;:'!|()[] ")


def text_width(text, size):
    total = 0.0
    for ch in str(text):
        if ch in _WIDE:
            total += 0.86
        elif ch in _NARROW:
            total += 0.30
        elif ch.isupper() or ch.isdigit():
            total += 0.62
        else:
            total += 0.52
    return total * size


def fit_size(text, max_width, start, minimum):
    size = start
    while size > minimum and text_width(text, size) > max_width:
        size -= 1
    return size


def wrap(text, max_width, size, max_lines=2):
    words, lines, current = str(text).split(), [], ""
    for word in words:
        trial = (current + " " + word).strip()
        if current and text_width(trial, size) > max_width:
            lines.append(current)
            current = word
            if len(lines) == max_lines:
                break
        else:
            current = trial
    if current and len(lines) < max_lines:
        lines.append(current)
    if len(lines) == max_lines and len(" ".join(lines)) < len(text.strip()):
        lines[-1] = lines[-1].rstrip(" ,.;") + "…"
    return lines


def qr_payload(b):
    """A URL if they have one, otherwise a contact card that works offline."""
    if b["site_url"]:
        return b["site_url"], "Scan for the website"
    bits = ["MECARD:"]
    if b["owner"]:
        bits.append(f"N:{b['owner']};")
    bits.append(f"ORG:{b['name']};")
    if b["phone"]:
        bits.append(f"TEL:{re.sub(r'[^0-9+]', '', b['phone'])};")
    if b["email"]:
        bits.append(f"EMAIL:{b['email']};")
    if b["address"]:
        bits.append(f"ADR:,,{b['address']};")
    bits.append(";")
    payload = "".join(bits)
    if len(payload.encode("utf-8")) > 213:
        payload = f"MECARD:ORG:{b['name']};TEL:{re.sub(r'[^0-9+]', '', b['phone'] or '')};;"
    return payload, "Scan to save our details"


def _open_svg(extra=""):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
            f'viewBox="0 0 {W} {H}"{extra}>')


def _nested(svg_markup, x, y, size):
    """Drop a standalone <svg> in as a positioned child."""
    inner = svg_markup.replace(
        '<svg xmlns="http://www.w3.org/2000/svg"',
        f'<svg x="{x}" y="{y}" width="{size}" height="{size}" '
        'xmlns="http://www.w3.org/2000/svg"', 1)
    return re.sub(r'(<svg[^>]*?) width="\d+" height="\d+"(?= )', r"\1", inner, count=1)


def front(b, t):
    ink = t["hero_ink"]
    bg = t["hero_bg"]
    body = [f'<rect width="{W}" height="{H}" fill="{bg}"/>']

    pat = pattern_svg(t, ink=ink, opacity=0.14)
    pat_body = pat[pat.index(">") + 1:pat.rindex("</svg>")]
    m = re.search(r'width="(\d+)" height="(\d+)"', pat)
    pw, ph = int(m.group(1)), int(m.group(2))
    body.append(
        f'<defs><pattern id="pt" width="{pw * 2}" height="{ph * 2}" '
        f'patternUnits="userSpaceOnUse">'
        f'<g transform="scale(2)" opacity="0.14">{pat_body}</g></pattern></defs>'
        f'<rect width="{W}" height="{H}" fill="url(#pt)"/>')

    # accent wedge in the bottom-right, bled off the edge
    body.append(f'<path d="M{W} {H - 300} L{W} {H} L{W - 420} {H} Z" '
                f'fill="{t["accent"]}" opacity="0.9"/>')

    # On the dark front, the mark has to key off hero_ink — some themes have a dark
    # accent, and accent-on-hero_bg would put dark letters on a dark plate. A real
    # logo gets a light plate underneath unless the brief says it does not need one.
    body.append(brand_svg(b, t, SAFE + 5, SAFE + 5, 150, on_dark=True,
                          max_w=460))

    # QR on the front as well as the back. It sits on a light plate over the accent
    # wedge: an inverted QR (light modules on dark) is read inconsistently by
    # scanners, and the plate's padding doubles as the quiet zone the spec wants.
    payload, _caption = qr_payload(b)
    qr_px, pad = 180, 28
    plate = qr_px + pad * 2
    qx, qy = W - SAFE - plate, H - SAFE - plate
    body.append(f'<rect x="{qx}" y="{qy}" width="{plate}" height="{plate}" '
                f'rx="{max(4, int(plate * 0.06))}" fill="{ink}"/>')
    body.append(_nested(qr.svg(payload, dark=bg, light=None, quiet=0, module=6),
                        qx + pad, qy + pad, qr_px))

    # The text column now stops short of the QR so nothing runs underneath it.
    name_max = qx - (SAFE + 5) - 36
    n_size = fit_size(b["name"], name_max, 74, 34)
    name_lines = wrap(b["name"], name_max, n_size, 2)
    y = SAFE + 240
    for line in name_lines:
        body.append(f'<text x="{SAFE + 5}" y="{y}" fill="{ink}" '
                    f'font-family="{t["font_display"]}" font-size="{n_size}" '
                    f'font-weight="{t["display_weight"]}" letter-spacing="-1.5" '
                    f'{_case(t)}>{esc(line)}</text>')
        y += int(n_size * 1.12)

    tag_size = 30
    for line in wrap(b["tagline"], name_max, tag_size, 2):
        y += 8
        body.append(f'<text x="{SAFE + 5}" y="{y + 22}" fill="{ink}" opacity="0.72" '
                    f'font-family="{t["font_body"]}" font-size="{tag_size}">'
                    f'{esc(line)}</text>')
        y += tag_size + 6

    footer = b["site_url"].replace("https://", "") if b["site_url"] else (b["city"] or "")
    if footer:
        body.append(f'<text x="{SAFE + 5}" y="{H - SAFE - 8}" fill="{ink}" opacity="0.8" '
                    f'font-family="{t["font_body"]}" font-size="26" '
                    f'letter-spacing="1.5">{esc(footer)}</text>')
    return _open_svg(' role="img" aria-label="Business card, front"') + "".join(body) + "</svg>"


def _case(t):
    return ' style="text-transform:uppercase"' if t["display_case"] == "uppercase" else ""


def back(b, t):
    ink = t["text"]
    body = [f'<rect width="{W}" height="{H}" fill="{t["bg"]}"/>',
            f'<rect width="{W}" height="26" fill="{t["accent"]}"/>']

    payload, caption = qr_payload(b)
    qr_px = 276
    qr_x = W - SAFE - qr_px
    qr_y = int((H - qr_px) / 2) - 16
    code = qr.svg(payload, dark=ink, light=None, quiet=2, module=6)
    body.append(_nested(code, qr_x, qr_y, qr_px))
    body.append(f'<text x="{qr_x + qr_px // 2}" y="{qr_y + qr_px + 32}" fill="{t["muted"]}" '
                f'font-family="{t["font_body"]}" font-size="20" text-anchor="middle">'
                f'{esc(caption)}</text>')

    x = SAFE + 5
    col_w = qr_x - x - 50

    rows = []
    if b["phone"]:
        rows.append(("phone", b["phone"]))
    if b["email"]:
        rows.append(("mail", b["email"]))
    if b["site_url"]:
        rows.append(("home", b["site_url"].replace("https://", "")))
    if b["address"]:
        rows.append(("pin", b["address"]))
    rows = rows[:4]

    # Centre the whole left column so short details do not leave the card bottom-heavy.
    name_h = 78 if b["owner"] else 52
    block_h = name_h + 34 + len(rows) * 46
    y = max(SAFE + 46, int((H - block_h) / 2) + 40)

    if b["owner"]:
        size = fit_size(b["owner"], col_w, 52, 30)
        body.append(f'<text x="{x}" y="{y}" fill="{ink}" font-family="{t["font_display"]}" '
                    f'font-size="{size}" font-weight="{t["display_weight"]}" '
                    f'letter-spacing="-1">{esc(b["owner"])}</text>')
        y += 34
        body.append(f'<text x="{x}" y="{y}" fill="{t["accent"]}" '
                    f'font-family="{t["font_body"]}" font-size="24" letter-spacing="1.6" '
                    f'style="text-transform:uppercase">{esc(b["owner_title"])}</text>')
        y += 44
    else:
        size = fit_size(b["name"], col_w, 50, 28)
        body.append(f'<text x="{x}" y="{y}" fill="{ink}" font-family="{t["font_display"]}" '
                    f'font-size="{size}" font-weight="{t["display_weight"]}" '
                    f'letter-spacing="-1"{_case(t)}>{esc(b["name"])}</text>')
        y += 52

    body.append(f'<rect x="{x}" y="{y - 14}" width="70" height="5" fill="{t["accent"]}"/>')
    y += 34

    for name, value in rows:
        size = fit_size(value, col_w - 46, 27, 17)
        icon = icon_svg(name, size=30, stroke=2)
        icon = icon.replace('stroke="currentColor"', f'stroke="{t["accent"]}"')
        body.append(_nested(icon, x, y - 22, 30))
        body.append(f'<text x="{x + 46}" y="{y}" fill="{ink}" '
                    f'font-family="{t["font_body"]}" font-size="{size}">{esc(value)}</text>')
        y += 46

    return _open_svg(' role="img" aria-label="Business card, back"') + "".join(body) + "</svg>"


PRINT_HTML = """<!doctype html>
<html><head><meta charset="utf-8"><title>{name} — business cards</title>
<style>
  @page {{ size: {w}in {h}in; margin: 0; }}
  html, body {{ margin: 0; padding: 0; background: #fff; }}
  .card {{ width: {w}in; height: {h}in; overflow: hidden; page-break-after: always;
           break-after: page; }}
  .card:last-child {{ page-break-after: auto; break-after: auto; }}
  .card svg {{ width: {w}in; height: {h}in; display: block; }}
</style></head><body>
<div class="card">{front}</div>
<div class="card">{back}</div>
</body></html>
"""

PROOF_HTML = """<!doctype html>
<html><head><meta charset="utf-8"><title>{name} — card proof</title>
<style>
  body {{ margin: 0; padding: 2.5rem; background: #eceff3; color: #111;
         font: 15px/1.6 ui-sans-serif, -apple-system, "Segoe UI", Roboto, sans-serif; }}
  h1 {{ font-size: 1.4rem; margin: 0 0 .3rem; }}
  p {{ color: #55606e; margin: 0 0 2rem; max-width: 62ch; }}
  .row {{ display: flex; flex-wrap: wrap; gap: 2.5rem; }}
  figure {{ margin: 0; }}
  figcaption {{ font-size: .8rem; color: #55606e; margin-top: .6rem;
                letter-spacing: .1em; text-transform: uppercase; }}
  .stage {{ position: relative; width: 3.75in; height: 2.25in;
            box-shadow: 0 10px 40px -14px rgba(0,0,0,.5); background: #fff; }}
  .stage svg {{ width: 100%; height: 100%; display: block; }}
  .guide {{ position: absolute; pointer-events: none; }}
  .trim {{ inset: .125in; outline: 1px dashed rgba(255,0,0,.85); }}
  .safe {{ inset: .25in; outline: 1px dashed rgba(0,120,255,.7); }}
  .key {{ margin-top: 2rem; font-size: .85rem; color: #55606e; }}
  .key b {{ font-weight: 600; }}
  @media print {{ body {{ background: #fff; padding: .5in; }} .stage {{ box-shadow: none; }} }}
</style></head><body>
<h1>{name} — business card proof</h1>
<p>Shown at actual size. The red dashed line is where the printer cuts; the blue line is
   the safe zone. Anything outside the red line is bleed and gets trimmed off.</p>
<div class="row">
  <figure><div class="stage">{front}<div class="guide trim"></div><div class="guide safe"></div></div>
    <figcaption>Front</figcaption></figure>
  <figure><div class="stage">{back}<div class="guide trim"></div><div class="guide safe"></div></div>
    <figcaption>Back</figcaption></figure>
</div>
<p class="key"><b>Send to the printer:</b> cards.pdf — 3.75 &times; 2.25 in, two pages,
   bleed included, no crop marks. That is what VistaPrint, Moo, Solopress and most
   online printers ask for.</p>
</body></html>
"""


def write(out_dir, b, t):
    """Write card sources + PDF. Returns (files_written, warning_or_None)."""
    os.makedirs(out_dir, exist_ok=True)
    f_svg, b_svg = front(b, t), back(b, t)
    written = []

    for name, data in (("card-front.svg", f_svg), ("card-back.svg", b_svg)):
        path = os.path.join(out_dir, name)
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(data)
        written.append(path)

    print_html = PRINT_HTML.format(name=esc(b["name"]), front=f_svg, back=b_svg,
                                   w=TRIM_W_IN + BLEED_IN * 2, h=TRIM_H_IN + BLEED_IN * 2)
    proof_html = PROOF_HTML.format(name=esc(b["name"]), front=f_svg, back=b_svg)
    for name, data in (("cards-print.html", print_html), ("cards-proof.html", proof_html)):
        path = os.path.join(out_dir, name)
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(data)
        written.append(path)

    chrome = find_chrome()
    if not chrome:
        return written, ("No Chrome/Chromium/Edge found, so cards.pdf was not built. "
                         "Open cards-print.html in any browser and print to PDF — "
                         "set paper to 3.75 x 2.25 in with margins off. The .svg files "
                         "are print-ready either way.")

    pdf_path = os.path.join(out_dir, "cards.pdf")
    if os.path.exists(pdf_path):
        os.remove(pdf_path)
    ok = _chrome_print(chrome, os.path.abspath(os.path.join(out_dir, "cards-print.html")),
                       pdf_path)
    if not ok:
        return written, ("Chrome ran but did not produce a usable cards.pdf. "
                         "Open cards-print.html in any browser and print to PDF — "
                         "paper 3.75 x 2.25 in, margins none.")
    written.append(pdf_path)
    return written, None


def _chrome_print(chrome, src_html, pdf_path, deadline=60.0):
    """Chrome writes the PDF and then does not always exit, so watch the file
    instead of the process and shut it down once the output has settled."""
    profile = tempfile.mkdtemp(prefix="sitesmith-chrome-")
    cmd = [chrome, "--headless=old", "--disable-gpu", "--no-sandbox", "--no-first-run",
           "--disable-extensions", "--disable-background-networking",
           "--disable-default-apps", "--mute-audio",
           f"--user-data-dir={profile}", "--no-pdf-header-footer",
           "--virtual-time-budget=5000", f"--print-to-pdf={pdf_path}",
           "file://" + src_html]
    proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    settled_at = None
    last_size = -1
    start = time.time()
    try:
        while time.time() - start < deadline:
            if proc.poll() is not None:
                break
            size = os.path.getsize(pdf_path) if os.path.exists(pdf_path) else 0
            if size > 1000 and size == last_size:
                if settled_at is None:
                    settled_at = time.time()
                elif time.time() - settled_at > 0.6:
                    break
            else:
                settled_at = None
            last_size = size
            time.sleep(0.25)
    finally:
        if proc.poll() is None:
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait(timeout=5)
        shutil.rmtree(profile, ignore_errors=True)

    return (os.path.exists(pdf_path) and os.path.getsize(pdf_path) > 1000
            and open(pdf_path, "rb").read(5) == b"%PDF-")
