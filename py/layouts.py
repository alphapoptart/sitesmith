"""HTML page rendering. Six layouts x four pages, built from shared sections."""

import html
import re

import content

import design
from design import icon_for, icon_svg

PAGES = [("index.html", "Home"), ("services.html", "Services"),
         ("about.html", "About"), ("contact.html", "Contact")]


def e(text):
    return html.escape(str(text or ""), quote=True)


def tel(number):
    return "tel:" + re.sub(r"[^0-9+]", "", number or "")


def _mark(b, t, size=32):
    return design.brand_html(b, t, height=size)


def _brand(b, t, size):
    """A wordmark logo already carries the name, so do not print it twice."""
    name = ("" if b.get("logo") and b.get("logo_has_name")
            else f'<span class="brand__name">{e(b["name"])}</span>')
    return (f'<a class="brand" href="index.html">{_mark(b, t, size)}{name}</a>')


def favicon_link(b):
    if b.get("logo") and b.get("logo_square"):
        mime = b["logo_mime"]
        return f'<link rel="icon" href="assets/logo.{b["logo_ext"]}" type="{mime}">'
    return '<link rel="icon" href="assets/favicon.svg" type="image/svg+xml">'


def head(b, t, page, title, description, layout):
    canonical = ""
    if b["site_url"]:
        path = "" if page == "index.html" else page
        canonical = f'\n  <link rel="canonical" href="{e(b["site_url"])}/{e(path)}">'
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{e(title)}</title>
  <meta name="description" content="{e(description)}">
  <meta name="theme-color" content="{t['accent']}">
  <meta property="og:title" content="{e(title)}">
  <meta property="og:description" content="{e(description)}">
  <meta property="og:type" content="website">
  <meta property="og:image" content="assets/og.svg">{canonical}
  {favicon_link(b)}
  <link rel="stylesheet" href="assets/site.css">
  <noscript><style>.reveal{{opacity:1;transform:none}}</style></noscript>
  <script type="application/ld+json">{local_business_jsonld(b)}</script>
</head>
<body class="layout-{layout} theme-{t['key']} page-{page.replace('.html', '')}">
<a class="btn skip" href="#main" style="position:absolute;left:-9999px;top:0;z-index:100"
   onfocus="this.style.left='1rem';this.style.top='1rem'"
   onblur="this.style.left='-9999px'">Skip to content</a>
"""


def local_business_jsonld(b):
    import json
    data = {
        "@context": "https://schema.org",
        "@type": "LocalBusiness",
        "name": b["name"],
        "description": b["tagline"],
    }
    if b["site_url"]:
        data["url"] = b["site_url"]
    if b["phone"]:
        data["telephone"] = b["phone"]
    if b["email"]:
        data["email"] = b["email"]
    if b["address"]:
        data["address"] = {"@type": "PostalAddress", "streetAddress": b["address"]}
    if b["city"]:
        data["areaServed"] = b["city"]
    if b["hours"]:
        data["openingHours"] = b["hours"]
    # Inside a <script> block, a "</script>" in any value would end the element,
    # so escape the characters that could close it.
    return (json.dumps(data, ensure_ascii=False)
            .replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026"))


def header(b, t, page, layout):
    links = "".join(
        f'<a href="{href}"{" aria-current=\"page\"" if href == page else ""}>{e(label)}</a>'
        for href, label in PAGES)
    side = ""
    if layout == "split":
        bits = []
        if b["phone"]:
            bits.append(f'<a href="{tel(b["phone"])}">{e(b["phone"])}</a>')
        if b["email"]:
            bits.append(f'<a href="mailto:{e(b["email"])}">{e(b["email"])}</a>')
        if b["address"]:
            bits.append(f"<span>{e(b['address'])}</span>")
        if b["hours"]:
            bits.append(f"<span>{e(b['hours'])}</span>")
        side = f'<div class="side-meta">{"".join(bits)}</div>'
    cta = ""
    if b["phone"]:
        cta = (f'<a class="btn nav__cta" href="{tel(b["phone"])}">'
               f'{icon_svg("phone", 18)}{e(b["phone"])}</a>')
    else:
        cta = f'<a class="btn nav__cta" href="contact.html">{e(b["cta"])}</a>'
    return f"""<header class="site-head">
  <div class="wrap site-head__inner">
    {_brand(b, t, 34)}
    <button class="nav-toggle" type="button" aria-expanded="false" aria-controls="nav" aria-label="Menu">
      {icon_svg('menu', 22)}
    </button>
    <nav class="nav" id="nav" aria-label="Main">{links}{cta}</nav>
    {side}
  </div>
</header>
<main id="main">
"""


def footer(b, t, layout):
    contact = []
    if b["phone"]:
        contact.append(f'<li><a href="{tel(b["phone"])}">{e(b["phone"])}</a></li>')
    if b["email"]:
        contact.append(f'<li><a href="mailto:{e(b["email"])}">{e(b["email"])}</a></li>')
    if b["address"]:
        contact.append(f"<li>{e(b['address'])}</li>")
    if b["hours"]:
        contact.append(f"<li>{e(b['hours'])}</li>")
    services = "".join(f'<li><a href="services.html">{e(s["title"])}</a></li>'
                       for s in b["services"][:5])
    nav = "".join(f'<li><a href="{h}">{e(l)}</a></li>' for h, l in PAGES)
    area = f" Serving {e(b['city'])}." if b["city"] else ""
    return f"""</main>
<footer class="site-foot">
  <div class="wrap">
    <div class="foot-grid">
      <div>
        {_brand(b, t, 30)}
        <p class="muted" style="margin-top:1rem;font-size:.94rem;max-width:32ch">{e(b['tagline'])}.{area}</p>
      </div>
      <div><h4>Pages</h4><ul>{nav}</ul></div>
      <div><h4>Services</h4><ul>{services}</ul></div>
      <div><h4>Get in touch</h4><ul>{"".join(contact)}</ul></div>
    </div>
    <div class="colophon">
      <span>&copy; <span id="yr">2026</span> {e(b['name'])}. All rights reserved.</span>
      <span>Built with sitesmith</span>
    </div>
  </div>
</footer>
<script>document.getElementById('yr').textContent = new Date().getFullYear();</script>
<script src="assets/site.js" defer></script>
</body>
</html>
"""


# --- shared sections ---------------------------------------------------------

def price_tag(s, cls="svc-price"):
    """Whatever the owner typed, verbatim. Nothing is shown if they left it blank."""
    return f'<span class="{cls}">{e(s["price"])}</span>' if s.get("price") else ""


def svc_desc(s):
    """A description the owner has not written yet renders as a visible to-do, not
    as body copy — six untouched REPLACE sentences in a row just look broken."""
    if content.PLACEHOLDER in s["desc"]:
        return '<p class="svc-todo">Add a one-line description</p>'
    return f'<p>{e(s["desc"])}</p>'


def services_cards(b, t, limit=6):
    out = []
    for i, s in enumerate(b["services"][:limit]):
        out.append(f"""<article class="card card--lift reveal">
        <div class="icon-badge">{icon_svg(icon_for(s['title'] + ' ' + s['desc'], i), 22)}</div>
        <h3>{e(s['title'])}</h3>{price_tag(s)}{svc_desc(s)}</article>""")
    return f'<div class="grid grid--3">{"".join(out)}</div>'


def services_rows(b, t):
    out = []
    for i, s in enumerate(b["services"]):
        out.append(f"""<article class="row-item reveal">
        <div class="row-item__n">{i + 1:02d}</div>
        <div><h3>{e(s['title'])}</h3>{price_tag(s)}</div>
        {svc_desc(s)}</article>""")
    return f'<div class="rows">{"".join(out)}</div>'


def services_list(b, t):
    out = "".join(f'<li class="reveal"><div class="row-head"><h3>{e(s["title"])}</h3>'
                  f'{price_tag(s)}</div>{svc_desc(s)}</li>'
                  for s in b["services"])
    return f'<ul class="list-plain">{out}</ul>'


def services_tiles(b, t):
    out = []
    for i, s in enumerate(b["services"]):
        out.append(f"""<a class="tile reveal" href="contact.html">
        <span class="tile__art">{design.picture(b, t, i + 2, 600, 520, alt=s['title'])}</span>
        <span class="tile__body"><h3>{e(s['title'])}</h3>{price_tag(s, 'svc-price tile__price')}
        {svc_desc(s)}</span></a>""")
    return f'<div class="tiles">{"".join(out)}</div>'


def services_columns(b, t):
    """Magazine: services flowed down two text columns with a rule between."""
    out = []
    for i, s in enumerate(b["services"]):
        out.append(f"""<article class="reveal">
        <div class="icon-badge">{icon_svg(icon_for(s['title'] + ' ' + s['desc'], i), 20)}</div>
        <h3>{e(s['title'])}</h3>{price_tag(s)}{svc_desc(s)}</article>""")
    return f'<div class="cols">{"".join(out)}</div>'


def services_listing(b, t):
    """Directory: a menu-style list. The price column only exists if the brief
    actually has prices in it — nothing is invented to fill the space."""
    out = []
    for s in b["services"]:
        out.append(f"""<li class="reveal"><h3>{e(s['title'])}</h3>
        {price_tag(s, 'price')}
        {svc_desc(s)}</li>""")
    return f'<ul class="listing">{"".join(out)}</ul>'


def hours_table(b, t):
    rows = [r.strip() for r in re.split(r"[·|,]| and ", b["hours"] or "") if r.strip()]
    if not rows:
        return ""
    cells = []
    for row in rows:
        parts = re.split(r"\s+(?=\d|Closed|closed)", row, maxsplit=1)
        day = parts[0]
        when = parts[1] if len(parts) > 1 else ""
        cells.append(f"<tr><th>{e(day)}</th><td>{e(when)}</td></tr>")
    return f'<table class="hours"><tbody>{"".join(cells)}</tbody></table>'


def _stat_cells(b, t):
    """Years in business if the brief supplies it, then trust points. Never a
    made-up number."""
    items = []
    if str(b["years"]).strip():
        items.append((str(b["years"]), "Years in business"))
    for p in b["points"][:3 - len(items)]:
        items.append((None, p))
    cells = []
    for value, label in items:
        figure = (e(value) if value else icon_svg("check", 34, 2.4))
        cells.append(f'<div class="reveal"><div class="stat__n">{figure}</div>'
                     f'<div class="stat__l">{e(label)}</div></div>')
    return "".join(cells)


def photo_strip(b, t, heading="Recent work"):
    """Layouts that are type-first have nowhere to put a photo. Rather than let
    uploaded photos go unused there, they get a strip of their own — which only
    appears when photos actually exist, so photo-less output is unchanged."""
    if not b.get("has_photos"):
        return ""
    shots = "".join(f"<div>{design.picture(b, t, i, 500, 500)}</div>"
                    for i in range(min(6, len(b["photos"]))))
    return f"""<section class="section section--tint"><div class="wrap">
  <p class="eyebrow">Our work</p><h2>{e(heading)}</h2>
  <div class="strip" style="margin-top:2rem">{shots}</div>
</div></section>"""


def points_band(b, t):
    return (f'<section class="section stat-band"><div class="wrap">'
            f'<div class="stats">{_stat_cells(b, t)}</div></div></section>')


def _contact_items(b, t):
    lines = []
    if b["phone"]:
        lines.append(f'<li>{icon_svg("phone", 20)}<div><strong>Phone</strong><br>'
                     f'<a href="{tel(b["phone"])}">{e(b["phone"])}</a></div></li>')
    if b["email"]:
        lines.append(f'<li>{icon_svg("mail", 20)}<div><strong>Email</strong><br>'
                     f'<a href="mailto:{e(b["email"])}">{e(b["email"])}</a></div></li>')
    if b["address"]:
        maps = ("https://www.openstreetmap.org/search?query="
                + e(b["address"].replace(" ", "+")))
        lines.append(f'<li>{icon_svg("pin", 20)}<div><strong>Where</strong><br>'
                     f'<a href="{maps}" target="_blank" rel="noopener">'
                     f'{e(b["address"])}</a></div></li>')
    if b["hours"]:
        lines.append(f'<li>{icon_svg("clock", 20)}<div><strong>Hours</strong><br>'
                     f'{e(b["hours"])}</div></li>')
    if not lines:
        lines.append("<li>REPLACE — add a phone number and email to the brief.</li>")
    return "".join(lines)


def _factbox(b, t):
    """Directory hero sidebar: the facts someone actually came for."""
    rows = []
    if b["hours"]:
        rows.append(("Open", b["hours"].split("·")[0].strip()))
    if b["address"]:
        rows.append(("Find us", b["address"]))
    if b["city"] and not b["address"]:
        rows.append(("Area", b["city"]))
    dl = "".join(f"<dt>{e(k)}</dt><dd>{e(v)}</dd>" for k, v in rows)
    call = ""
    if b["phone"]:
        call = (f'<a class="bigcall" href="{tel(b["phone"])}">{e(b["phone"])}</a>')
    button = f'<a class="btn" href="contact.html">{e(b["cta"])}</a>'
    return f'{call}{f"<dl>{dl}</dl>" if dl else ""}{button}'


def steps_block(b, t):
    out = "".join(f'<div class="step reveal"><h3>{e(s["title"])}</h3>'
                  f'<p class="muted">{e(s["desc"])}</p></div>' for s in b["steps"])
    return f'<div class="steps">{out}</div>'


def faq_block(b, t):
    out = "".join(f"<details><summary>{e(f['q'])}</summary><p>{e(f['a'])}</p></details>"
                  for f in b["faq"])
    return f'<div class="faq reveal">{out}</div>'


def quote_block(b, t):
    return f"""<figure class="quote reveal" style="margin:0">
  <span class="placeholder-note">Placeholder</span>
  <p>Paste a real review here — one or two sentences, in the customer's own words.
     A specific one beats a glowing one.</p>
  <cite>Customer name, {e(b['city'] or 'town')}</cite>
</figure>"""


def cta_band(b, t, heading=None, sub=None):
    heading = heading or f"Ready when you are"
    sub = sub or (f"Tell us what you need and we'll come back with a straight answer"
                  f"{' and a fixed price' if b['preset'] in ('trades', 'home_services', 'auto') else ''}.")
    buttons = [f'<a class="btn btn--lg" href="contact.html">{e(b["cta"])}</a>']
    if b["phone"]:
        buttons.append(f'<a class="btn btn--lg btn--onhero" href="{tel(b["phone"])}">'
                       f'{icon_svg("phone", 18)}{e(b["phone"])}</a>')
    return f"""<section class="section cta-band"><div class="wrap center">
  <h2>{e(heading)}</h2><p class="lede">{e(sub)}</p>
  <div class="btn-row">{"".join(buttons)}</div>
</div></section>"""


def contact_block(b, t, with_form=True):
    lines = [_contact_items(b, t)]

    form = ""
    if with_form:
        form = f"""<form class="enquiry" name="enquiry" method="POST"
        data-netlify="true" netlify-honeypot="bot-field">
  <input type="hidden" name="form-name" value="enquiry">
  <p hidden><label>Leave blank: <input name="bot-field"></label></p>
  <div class="field"><label for="f-name">Your name</label>
    <input id="f-name" name="name" autocomplete="name" required></div>
  <div class="field"><label for="f-contact">Phone or email</label>
    <input id="f-contact" name="contact" autocomplete="email" required></div>
  <div class="field"><label for="f-msg">What do you need?</label>
    <textarea id="f-msg" name="message" required></textarea></div>
  <button class="btn btn--lg" type="submit">Send enquiry</button>
  <p class="form-note muted" hidden role="status" style="font-size:.9rem">
    This is a local preview, so nothing was sent. Once the site is deployed to Netlify
    the form delivers to your inbox — see DEPLOY.md.</p>
</form>"""
    return f"""<div class="contact-grid">
  <div class="reveal"><h2>Get in touch</h2>
    <p class="lede">The quickest way is the phone. If it's out of hours, send a message
      and we'll pick it up first thing.</p>
    <ul class="contact-list" style="margin-top:2rem">{"".join(lines)}</ul></div>
  <div class="reveal">{form}</div>
</div>"""


def about_body(b, t):
    return f"""<p class="lede">{e(b['about'])}</p>
<ul class="ticks">{"".join(f'<li>{icon_svg("check", 20)}<span>{e(p)}</span></li>' for p in b['points'])}</ul>"""


# --- layout-specific home pages ---------------------------------------------

def hero_buttons(b, t, on_hero=False):
    ghost = "btn--onhero" if on_hero else "btn--ghost"
    out = [f'<a class="btn btn--lg" href="contact.html">{e(b["cta"])}</a>']
    if b["phone"]:
        out.append(f'<a class="btn btn--lg {ghost}" href="{tel(b["phone"])}">'
                   f'{icon_svg("phone", 18)}{e(b["phone"])}</a>')
    else:
        out.append(f'<a class="btn btn--lg {ghost}" href="services.html">See what we do</a>')
    return f'<div class="btn-row">{"".join(out)}</div>'


def home(b, t, layout):
    eyebrow = e(b["city"] or b["tagline"][:34])

    if layout == "classic":
        badges = "".join(f'<span class="badge">{e(p)}</span>' for p in b["points"])
        return f"""<section class="hero"><div class="wrap"><div class="hero__grid">
  <div><p class="eyebrow">{eyebrow}</p>
    <h1>{e(b['headline'])}</h1>
    <p class="lede">{e(b['hero_lede'])}</p>
    {hero_buttons(b, t)}
    <div class="hero__badges">{badges}</div></div>
  <div class="hero-art">{design.picture(b, t, 0, 760, 570, alt=b['tagline'])}</div>
</div></div></section>
{points_band(b, t)}
<section class="section"><div class="wrap">
  <p class="eyebrow">What we do</p><h2>Services</h2>
  <p class="lede" style="margin-bottom:2.5rem">Everything below is priced up front.
     If you need something that isn't listed, ask — the answer is usually yes.</p>
  {services_cards(b, t)}
</div></section>
<section class="section section--tint"><div class="wrap">
  <div class="grid grid--2" style="align-items:center;gap:clamp(2rem,5vw,4rem)">
    <div class="reveal"><p class="eyebrow">About</p><h2>Who you're dealing with</h2>
      {about_body(b, t)}</div>
    <div class="hero-art reveal" style="aspect-ratio:1">{design.picture(b, t, 1, 620, 620)}</div>
  </div></div></section>
<section class="section"><div class="wrap">
  <p class="eyebrow">How it works</p><h2>Three steps, no surprises</h2>
  <div style="margin-top:2.5rem">{steps_block(b, t)}</div>
  <div style="margin-top:clamp(3rem,6vw,4.5rem);max-width:44rem">{quote_block(b, t)}</div>
</div></section>
{cta_band(b, t)}"""

    if layout == "bold":
        return f"""<section class="hero"><div class="wrap">
  <p class="eyebrow">{eyebrow}</p>
  <h1>{e(b['headline'])}</h1>
  <p class="lede">{e(b['hero_lede'])}</p>
  {hero_buttons(b, t, on_hero=True)}
</div></section>
{points_band(b, t)}
<section class="section"><div class="wrap">
  <p class="eyebrow">Services</p><h2>What we take on</h2>
  <div style="margin-top:2.5rem">{services_rows(b, t)}</div>
</div></section>
<section class="section section--tint"><div class="wrap">
  <div class="grid grid--2" style="gap:clamp(2rem,5vw,4rem);align-items:center">
    <div class="hero-art reveal" style="aspect-ratio:5/4">{design.picture(b, t, 1, 700, 560)}</div>
    <div class="reveal"><p class="eyebrow">About</p><h2>Who you're dealing with</h2>
      {about_body(b, t)}</div>
  </div></div></section>
<section class="section"><div class="wrap">
  <p class="eyebrow">Process</p><h2>How it works</h2>
  <div style="margin-top:2.5rem">{steps_block(b, t)}</div>
</div></section>
<section class="section section--tint"><div class="wrap" style="max-width:48rem">
  {quote_block(b, t)}</div></section>
{cta_band(b, t)}"""

    if layout == "split":
        return f"""<section class="hero"><div class="wrap">
  <p class="eyebrow">{eyebrow}</p>
  <h1>{e(b['headline'])}</h1>
  <p class="lede">{e(b['hero_lede'])}</p>
  {hero_buttons(b, t)}
  <div class="hero-art">{design.picture(b, t, 0, 900, 390, alt=b['tagline'])}</div>
</div></section>
<section class="section"><div class="wrap">
  <p class="eyebrow">Services</p><h2>What we do</h2>
  <div style="margin-top:2rem">{services_cards(b, t)}</div>
</div></section>
<section class="section"><div class="wrap">
  <p class="eyebrow">About</p><h2>Who you're dealing with</h2>{about_body(b, t)}
</div></section>
<section class="section"><div class="wrap">
  <p class="eyebrow">Process</p><h2>How it works</h2>
  <div style="margin-top:2rem">{steps_block(b, t)}</div>
</div></section>
<section class="section"><div class="wrap">{quote_block(b, t)}</div></section>
{cta_band(b, t)}"""

    if layout == "minimal":
        return f"""<section class="hero"><div class="wrap">
  <p class="eyebrow" style="justify-content:center">{eyebrow}</p>
  <h1>{e(b['headline'])}</h1>
  <p class="lede">{e(b['hero_lede'])}</p>
  {hero_buttons(b, t)}
</div></section>
<section class="section"><div class="wrap">
  <span class="label">Services</span>{services_list(b, t)}
</div></section>
<section class="section"><div class="wrap">
  <span class="label">About</span>{about_body(b, t)}
</div></section>
<section class="section"><div class="wrap">
  <span class="label">How it works</span>{steps_block(b, t)}
</div></section>
{photo_strip(b, t)}
<section class="section"><div class="wrap">{quote_block(b, t)}</div></section>
{cta_band(b, t)}"""

    if layout == "landing":
        trust = "".join(f'<span>{icon_svg("check", 16)}{e(p)}</span>' for p in b["points"])
        packages = _packages(b, t)
        return f"""<section class="hero"><div class="wrap"><div class="hero__grid">
  <div><p class="eyebrow">{eyebrow}</p>
    <h1>{e(b['headline'])}</h1>
    <p class="lede">{e(b['hero_lede'])}</p>
    {hero_buttons(b, t)}
    <div class="trust-row">{trust}</div></div>
  <div class="hero-art">{design.picture(b, t, 0, 700, 560, alt=b['tagline'])}</div>
</div></div></section>
<section class="section"><div class="wrap">
  <p class="eyebrow">Why us</p><h2>What you get</h2>
  <div style="margin-top:2.5rem">{services_cards(b, t, 3)}</div>
</div></section>
<section class="section section--tint"><div class="wrap">
  <p class="eyebrow">How it works</p><h2>Three steps</h2>
  <div style="margin-top:2.5rem">{steps_block(b, t)}</div>
</div></section>
<section class="section"><div class="wrap">
  <p class="eyebrow">Packages</p><h2>Straightforward pricing</h2>
  <p class="lede" style="margin-bottom:2.5rem">{
    "No hidden extras. What you see is what you pay."
    if b["has_prices"] else
    "REPLACE — set your prices and what each one includes. Three options works better than one."
  }</p>
  {packages}
</div></section>
<section class="section section--tint"><div class="wrap" style="max-width:48rem">
  {quote_block(b, t)}</div></section>
<section class="section"><div class="wrap">
  <p class="eyebrow">Questions</p><h2>Before you call</h2>
  <div style="margin-top:2rem">{faq_block(b, t)}</div>
</div></section>
{cta_band(b, t)}
{_callbar(b, t)}"""

    if layout == "magazine":
        return f"""<section class="hero"><div class="wrap"><div class="hero__grid">
  <div><p class="eyebrow">{eyebrow}</p><h1>{e(b['headline'])}</h1></div>
  <div><p class="lede">{e(b['hero_lede'])}</p>{hero_buttons(b, t)}</div>
</div>
<div class="hero-art">{design.picture(b, t, 0, 1200, 515, alt=b['tagline'])}</div>
</div></section>
<section class="section"><div class="wrap">
  <p class="eyebrow">About</p><h2 class="center">Who you're dealing with</h2>
  <p class="lede dropcap" style="margin-inline:auto">{e(b['about'])}</p>
  <ul class="ticks" style="max-width:36rem;margin-inline:auto">
    {"".join(f'<li>{icon_svg("check", 20)}<span>{e(p)}</span></li>' for p in b['points'])}
  </ul>
</div></section>
<section class="section"><div class="wrap">
  <p class="eyebrow">Services</p><h2 class="center">What we do</h2>
  <div style="margin-top:2.5rem">{services_columns(b, t)}</div>
</div></section>
<section class="section"><div class="wrap">{quote_block(b, t)}</div></section>
<section class="section"><div class="wrap">
  <p class="eyebrow">How it works</p><h2 class="center">Three steps</h2>
  <div style="margin-top:2.5rem">{steps_block(b, t)}</div>
</div></section>
{cta_band(b, t)}"""

    if layout == "panel":
        return f"""<section class="hero"><div class="wrap"><div class="panel"><div class="hero__grid">
  <div><p class="eyebrow">{eyebrow}</p>
    <h1>{e(b['headline'])}</h1>
    <p class="lede">{e(b['hero_lede'])}</p>
    {hero_buttons(b, t)}</div>
  <div class="hero-art">{design.picture(b, t, 0, 720, 540, alt=b['tagline'])}</div>
</div></div></div></section>
<section class="section stat-band"><div class="wrap"><div class="panel reveal">
  <div class="stats">{_stat_cells(b, t)}</div>
</div></div></section>
<section class="section"><div class="wrap"><div class="panel">
  <p class="eyebrow">Services</p><h2>What we do</h2>
  <div style="margin-top:2rem">{services_cards(b, t)}</div>
</div></div></section>
<section class="section"><div class="wrap"><div class="panel">
  <div class="grid grid--2" style="gap:clamp(2rem,5vw,3.5rem);align-items:center">
    <div class="reveal"><p class="eyebrow">About</p><h2>Who you're dealing with</h2>
      {about_body(b, t)}</div>
    <div class="hero-art reveal" style="aspect-ratio:1">{design.picture(b, t, 1, 620, 620)}</div>
  </div>
</div></div></section>
<section class="section"><div class="wrap"><div class="panel">
  <p class="eyebrow">How it works</p><h2>Three steps, no surprises</h2>
  <div style="margin-top:2.5rem">{steps_block(b, t)}</div>
</div></div></section>
<section class="section"><div class="wrap"><div class="panel" style="max-width:48rem;margin-inline:auto">
  {quote_block(b, t)}</div></div></section>
<div class="wrap">{cta_band(b, t)}</div>"""

    if layout == "directory":
        return f"""<section class="hero"><div class="wrap"><div class="hero__grid">
  <div><p class="eyebrow">{eyebrow}</p>
    <h1>{e(b['headline'])}</h1>
    <p class="lede">{e(b['hero_lede'])}</p></div>
  <div class="factbox reveal">{_factbox(b, t)}</div>
</div></div></section>
<nav class="subnav" aria-label="Sections"><ul>
  <li><a href="#services">Services &amp; prices</a></li>
  <li><a href="#visit">Hours &amp; where</a></li>
  <li><a href="#how">How it works</a></li>
  <li><a href="#questions">Questions</a></li>
</ul></nav>
<section class="section" id="services"><div class="wrap">
  <p class="eyebrow">Services</p><h2>What we do, and what it costs</h2>
  <div style="margin-top:2rem">{services_listing(b, t)}</div>
</div></section>
<section class="section section--tint" id="visit"><div class="wrap">
  <div class="grid grid--2" style="gap:clamp(2rem,5vw,4rem);align-items:start">
    <div class="reveal"><p class="eyebrow">Opening hours</p><h2>When we're open</h2>
      <div style="margin-top:1.5rem">{hours_table(b, t) or '<p class="muted">REPLACE — add your hours to brief.json.</p>'}</div>
    </div>
    <div class="reveal"><p class="eyebrow">Find us</p><h2>Where we are</h2>
      <ul class="contact-list" style="margin-top:1.5rem">{_contact_items(b, t)}</ul>
    </div>
  </div>
</div></section>
{photo_strip(b, t)}
<section class="section" id="how"><div class="wrap">
  <p class="eyebrow">How it works</p><h2>Three steps</h2>
  <div style="margin-top:2.5rem">{steps_block(b, t)}</div>
  <div style="margin-top:clamp(3rem,6vw,4rem);max-width:44rem">{quote_block(b, t)}</div>
</div></section>
<section class="section section--tint" id="questions"><div class="wrap">
  <p class="eyebrow">Questions</p><h2>Before you call</h2>
  <div style="margin-top:2rem">{faq_block(b, t)}</div>
</div></section>
{cta_band(b, t)}"""

    if layout == "poster":
        return f"""<section class="hero"><div class="wrap">
  <p class="eyebrow">{eyebrow}</p>
  <h1>{e(b['headline'])}</h1>
  <p class="lede">{e(b['hero_lede'])}</p>
  {hero_buttons(b, t, on_hero=True)}
</div></section>
<section class="band band--accent"><div class="wrap">
  <div class="stats">{_stat_cells(b, t)}</div>
</div></section>
<section class="band"><div class="wrap">
  <p class="eyebrow">Services</p><h2>What we take on</h2>
  <div style="margin-top:2.5rem">{services_rows(b, t)}</div>
</div></section>
{photo_strip(b, t)}
<section class="band band--dark"><div class="wrap">
  <div class="grid grid--2" style="gap:clamp(2rem,5vw,4rem);align-items:center">
    <div class="reveal"><p class="eyebrow">About</p><h2>Who you're dealing with</h2>
      <p class="lede">{e(b['about'])}</p></div>
    <div class="reveal">{quote_block(b, t)}</div>
  </div>
</div></section>
<section class="band"><div class="wrap">
  <p class="eyebrow">How it works</p><h2>Three steps, no surprises</h2>
  <div style="margin-top:2.5rem">{steps_block(b, t)}</div>
</div></section>
{cta_band(b, t)}"""

    # showcase
    return f"""<section class="hero"><div class="wrap">
  <p class="eyebrow">{eyebrow}</p>
  <h1>{e(b['headline'])}</h1>
  <p class="lede">{e(b['hero_lede'])}</p>
  {hero_buttons(b, t)}
  <div class="collage">
    <div>{design.picture(b, t, 0, 900, 680, alt=b['tagline'])}</div>
    <div>{design.picture(b, t, 1, 500, 660)}</div>
    <div>{design.picture(b, t, 2, 1200, 350)}</div>
  </div>
</div></section>
<section class="section"><div class="wrap">
  <p class="eyebrow">Services</p><h2>What we do</h2>
  <div style="margin-top:2.5rem">{services_tiles(b, t)}</div>
</div></section>
{points_band(b, t)}
<section class="section"><div class="wrap">
  <div class="grid grid--2" style="gap:clamp(2rem,5vw,4rem);align-items:center">
    <div class="reveal"><p class="eyebrow">About</p><h2>Who you're dealing with</h2>
      {about_body(b, t)}</div>
    <div class="hero-art reveal" style="aspect-ratio:4/5">{design.picture(b, t, 1, 560, 700)}</div>
  </div></div></section>
<section class="section section--tint"><div class="wrap">
  <p class="eyebrow">Recent work</p><h2>A look at the job book</h2>
  <p class="lede" style="margin-bottom:2rem">REPLACE — swap these for real photos of your
     work. Six good ones beat thirty average ones.</p>
  <div class="strip">
    {"".join(f"<div>{design.picture(b, t, i, 400, 400)}</div>" for i in range(6))}
  </div>
</div></section>
<section class="section"><div class="wrap" style="max-width:48rem">{quote_block(b, t)}</div></section>
{cta_band(b, t)}"""


def _packages(b, t):
    """With real prices in the brief, this becomes a priced menu of the actual
    services. Without them it is an unmistakably blank tier scaffold — it never
    prints a number the owner did not supply."""
    if b["has_prices"]:
        cards = []
        priced = [s for s in b["services"] if s["price"]] or b["services"]
        for i, s in enumerate(priced[:3]):
            featured = i == 1 and len(priced) > 1
            tag = '<span class="pkg__tag">Most popular</span>' if featured else ""
            cards.append(f"""<article class="card card--lift reveal{
                ' pkg__featured' if featured else ''}">
  {tag}<h3>{e(s['title'])}</h3><div class="price">{e(s['price'])}</div>
  {svc_desc(s)}
  <a class="btn{'' if featured else ' btn--ghost'}" href="contact.html">{e(b['cta'])}</a>
</article>""")
        return f'<div class="pkg">{"".join(cards)}</div>'

    tiers = [
        ("Callout", "REPLACE — your entry price", False,
         ["REPLACE — what's included", "REPLACE — second inclusion", "REPLACE — third inclusion"]),
        ("Standard", "REPLACE — your most popular option", True,
         ["Everything in Callout", "REPLACE — the extra bit", "REPLACE — another extra",
          "REPLACE — a guarantee"]),
        ("Full job", "REPLACE — your premium option", False,
         ["Everything in Standard", "REPLACE — the premium extra", "REPLACE — priority booking"]),
    ]
    cards = []
    for name, sub, featured, items in tiers:
        lis = "".join(f'<li>{icon_svg("check", 16)}<span>{e(i)}</span></li>' for i in items)
        tag = '<span class="pkg__tag">Most popular</span>' if featured else ""
        cards.append(f"""<article class="card card--lift reveal{
            ' pkg__featured' if featured else ''}">
  {tag}<h3>{e(name)}</h3>
  <div class="price"><span class="placeholder-note">Set your price</span></div>
  <p class="muted" style="font-size:.94rem">{e(sub)}</p>
  <ul>{lis}</ul>
  <a class="btn{'' if featured else ' btn--ghost'}" href="contact.html">{e(b['cta'])}</a>
</article>""")
    return f'<div class="pkg">{"".join(cards)}</div>'


def _callbar(b, t):
    if not b["phone"]:
        return ""
    return f"""<div class="callbar">
  <a class="btn" href="{tel(b['phone'])}">{icon_svg('phone', 18)}Call now</a>
  <a class="btn btn--ghost" href="contact.html">Message</a>
</div>"""


# --- inner pages -------------------------------------------------------------

def page_head_block(b, t, layout, eyebrow, title, lede):
    if layout in ("minimal", "magazine"):
        return f"""<section class="hero"><div class="wrap">
  <p class="eyebrow" style="justify-content:center">{e(eyebrow)}</p>
  <h1>{e(title)}</h1><p class="lede">{e(lede)}</p></div></section>"""
    if layout in ("bold", "poster"):
        return f"""<section class="hero" style="min-height:auto;padding-block:clamp(4.5rem,10vw,6.5rem) clamp(2.5rem,6vw,4rem)">
  <div class="wrap"><p class="eyebrow">{e(eyebrow)}</p><h1 style="font-size:clamp(2.4rem,1.4rem+4vw,4.4rem)">{e(title)}</h1>
  <p class="lede">{e(lede)}</p></div></section>"""
    if layout == "panel":
        return f"""<section class="hero"><div class="wrap"><div class="panel">
  <p class="eyebrow">{e(eyebrow)}</p><h1>{e(title)}</h1>
  <p class="lede">{e(lede)}</p></div></div></section>"""
    return f"""<section class="hero" style="padding-block:clamp(2.75rem,6vw,4.5rem)">
  <div class="wrap"><p class="eyebrow">{e(eyebrow)}</p><h1>{e(title)}</h1>
  <p class="lede">{e(lede)}</p></div></section>"""


def _pane(layout, inner):
    """The panel layout puts each section's contents inside a floating card."""
    return f'<div class="panel">{inner}</div>' if layout == "panel" else inner


def services_page(b, t, layout):
    body = {"bold": services_rows, "poster": services_rows,
            "minimal": services_list, "showcase": services_tiles,
            "magazine": services_columns,
            "directory": services_listing}.get(layout, services_cards)(b, t)
    return f"""{page_head_block(b, t, layout, 'Services', 'What we do',
        'Priced up front, explained in plain language. If what you need is not on this list, ask.')}
<section class="section"><div class="wrap">{_pane(layout, body)}</div></section>
<section class="section section--tint"><div class="wrap">{_pane(layout, f'''
  <p class="eyebrow">How it works</p><h2>From first call to finished</h2>
  <div style="margin-top:2.5rem">{steps_block(b, t)}</div>''')}</div></section>
<section class="section"><div class="wrap">{_pane(layout, f'''
  <p class="eyebrow">Questions</p><h2>Common questions</h2>
  <div style="margin-top:2rem">{faq_block(b, t)}</div>''')}</div></section>
{cta_band(b, t)}"""


def about_page(b, t, layout):
    art = "" if layout == "minimal" else f"""
  <div class="hero-art reveal" style="aspect-ratio:4/5">{design.picture(b, t, 1, 620, 780)}</div>"""
    grid_open = ('<div class="grid grid--2" style="gap:clamp(2rem,5vw,4rem);align-items:start">'
                 if art else "<div>")
    who = ""
    if b["owner"]:
        who = (f'<p class="muted" style="margin-top:1.5rem"><strong>{e(b["owner"])}</strong>'
               f' &middot; {e(b["owner_title"])}</p>')
    return f"""{page_head_block(b, t, layout, 'About', f"About {b['name']}",
        b['tagline'] + ('. Serving ' + b['city'] if b['city'] else ''))}
<section class="section"><div class="wrap">{_pane(layout, f'''
  {grid_open}
    <div class="reveal">{about_body(b, t)}{who}</div>{art}
  </div>''')}</div></section>
<section class="section section--tint"><div class="wrap">{_pane(layout, f'''
  <p class="eyebrow">How we work</p><h2>Three steps, no surprises</h2>
  <div style="margin-top:2.5rem">{steps_block(b, t)}</div>''')}</div></section>
<section class="section"><div class="wrap" style="max-width:48rem">
  {_pane(layout, quote_block(b, t))}</div></section>
{cta_band(b, t)}"""


def contact_page(b, t, layout):
    return f"""{page_head_block(b, t, layout, 'Contact', 'Get in touch',
        'Tell us what you need. We answer every message, usually the same day.')}
<section class="section"><div class="wrap">{_pane(layout, contact_block(b, t))}</div></section>
<section class="section section--tint"><div class="wrap">{_pane(layout, f'''
  <p class="eyebrow">Questions</p><h2>Before you call</h2>
  <div style="margin-top:2rem">{faq_block(b, t)}</div>''')}</div></section>"""


def not_found_page(b, t, layout):
    return f"""{page_head_block(b, t, layout, 'Error 404', 'Page not found',
        'That link has moved or never existed. Everything else is still where it was.')}
<section class="section"><div class="wrap">{_pane(layout, '''
  <div class="btn-row" style="margin-top:0">
    <a class="btn btn--lg" href="index.html">Back to the home page</a>
    <a class="btn btn--lg btn--ghost" href="contact.html">Contact us</a>
  </div>''')}</div></section>"""


BODIES = {
    "index.html": home,
    "services.html": lambda b, t, l: services_page(b, t, l),
    "about.html": lambda b, t, l: about_page(b, t, l),
    "contact.html": lambda b, t, l: contact_page(b, t, l),
    "404.html": lambda b, t, l: not_found_page(b, t, l),
}

TITLES = {
    "index.html": lambda b: (f"{b['name']} — {b['tagline']}",
                             f"{b['tagline']}"
                             + (f" Serving {b['city']}." if b['city'] else "")),
    "services.html": lambda b: (f"Services — {b['name']}",
                                f"What {b['name']} does, and what it costs."),
    "about.html": lambda b: (f"About — {b['name']}",
                             f"Who runs {b['name']} and how we work."),
    "contact.html": lambda b: (f"Contact — {b['name']}",
                               f"Phone, email and opening hours for {b['name']}."),
    "404.html": lambda b: (f"Page not found — {b['name']}", "That page does not exist."),
}


def render(page, b, t, layout):
    title, desc = TITLES[page](b)
    return (head(b, t, page, title, desc, layout)
            + header(b, t, page if page != "404.html" else "index.html", layout)
            + BODIES[page](b, t, layout)
            + footer(b, t, layout))
