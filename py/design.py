"""Themes and generated vector assets. No external fonts, images or CDNs."""

import hashlib
import html as _html


def esc(text):
    """SVG and HTML share escaping rules for text nodes and attribute values."""
    return _html.escape(str(text or ""), quote=True)

# System font stacks — render instantly, cost nothing, load nothing.
SANS = ("ui-sans-serif, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, "
        "'Helvetica Neue', Arial, sans-serif")
GROTESK = ("'Helvetica Neue', Helvetica, 'Segoe UI', Roboto, Arial, sans-serif")
SERIF = ("ui-serif, 'Iowan Old Style', 'Palatino Linotype', Palatino, Georgia, "
         "'Times New Roman', serif")
ROUNDED = ("ui-rounded, 'SF Pro Rounded', 'Avenir Next', Avenir, 'Segoe UI', "
           "'Trebuchet MS', sans-serif")
CONDENSED = ("'Avenir Next Condensed', 'HelveticaNeue-CondensedBold', "
             "'Arial Narrow', 'Segoe UI', sans-serif")

THEMES = {
    "slate": dict(
        label="Slate", blurb="Confident corporate blue on cool grey. The safe, sharp default.",
        bg="#ffffff", surface="#f5f7fa", surface2="#eaeef4", text="#111827",
        muted="#5b6676", line="#dde3ec", accent="#1d4ed8", accent2="#3b82f6",
        on_accent="#ffffff", hero_bg="#0f172a", hero_ink="#ffffff",
        font_display=SANS, font_body=SANS, display_weight="750",
        display_tracking="-0.03em", display_case="none",
        radius="12px", radius_sm="8px", pill="10px", pattern="grid", dark=False),
    "midnight": dict(
        label="Midnight", blurb="Dark, high-contrast, gradient accents. Tech and creative.",
        bg="#0b0e14", surface="#12161f", surface2="#1a2030", text="#f2f5fa",
        muted="#98a3b8", line="#242c3d", accent="#22d3ee", accent2="#818cf8",
        on_accent="#06101a", hero_bg="#0b0e14", hero_ink="#f2f5fa",
        font_display=SANS, font_body=SANS, display_weight="700",
        display_tracking="-0.035em", display_case="none",
        radius="16px", radius_sm="10px", pill="999px", pattern="rings", dark=True),
    "sand": dict(
        label="Sand", blurb="Warm cream and terracotta with a serif voice. Calm and human.",
        bg="#fbf7f1", surface="#ffffff", surface2="#f2e9dd", text="#2a231d",
        muted="#6d6055", line="#e4d7c6", accent="#b8552f", accent2="#d98b5f",
        on_accent="#fffaf4", hero_bg="#2a231d", hero_ink="#fbf7f1",
        font_display=SERIF, font_body=SANS, display_weight="600",
        display_tracking="-0.015em", display_case="none",
        radius="6px", radius_sm="4px", pill="4px", pattern="waves", dark=False),
    "forest": dict(
        label="Forest", blurb="Deep green and brass, serif headings. Established and premium.",
        bg="#ffffff", surface="#f4f7f4", surface2="#e6ede7", text="#16241c",
        muted="#556158", line="#d5e0d7", accent="#1c5c3c", accent2="#a8823c",
        on_accent="#ffffff", hero_bg="#12291d", hero_ink="#f3f7f3",
        font_display=SERIF, font_body=SANS, display_weight="600",
        display_tracking="-0.01em", display_case="none",
        radius="4px", radius_sm="3px", pill="3px", pattern="diag", dark=False),
    "coral": dict(
        label="Coral", blurb="Rounded, bright and friendly. Salons, food, anything for families.",
        bg="#fffdfc", surface="#fff4f0", surface2="#ffe6de", text="#2b1d19",
        muted="#7a635c", line="#ffdbd0", accent="#f2542d", accent2="#ff9f68",
        on_accent="#ffffff", hero_bg="#f2542d", hero_ink="#ffffff",
        font_display=ROUNDED, font_body=ROUNDED, display_weight="800",
        display_tracking="-0.02em", display_case="none",
        radius="24px", radius_sm="16px", pill="999px", pattern="dots", dark=False),
    "mono": dict(
        label="Mono", blurb="Black, white, one red. Sharp corners, editorial. Architecture and studios.",
        bg="#ffffff", surface="#f4f4f4", surface2="#e8e8e8", text="#0a0a0a",
        muted="#5e5e5e", line="#d6d6d6", accent="#e0231a", accent2="#0a0a0a",
        on_accent="#ffffff", hero_bg="#0a0a0a", hero_ink="#ffffff",
        font_display=CONDENSED, font_body=GROTESK, display_weight="700",
        display_tracking="-0.02em", display_case="uppercase",
        radius="0px", radius_sm="0px", pill="0px", pattern="grid", dark=False),
    "ocean": dict(
        label="Ocean", blurb="Navy and teal, airy and clinical. Medical, dental, marine, finance.",
        bg="#ffffff", surface="#f2f8fa", surface2="#e2eff4", text="#0d2b36",
        muted="#4f6b76", line="#cfe3ea", accent="#0e7490", accent2="#38bdf8",
        on_accent="#ffffff", hero_bg="#0b3b4a", hero_ink="#ffffff",
        font_display=SANS, font_body=SANS, display_weight="700",
        display_tracking="-0.025em", display_case="none",
        radius="10px", radius_sm="8px", pill="999px", pattern="waves", dark=False),
    "plum": dict(
        label="Plum", blurb="Cream and deep plum with pill buttons. Boutique and beauty.",
        bg="#fdfbfd", surface="#f8f2f7", surface2="#efe2ed", text="#241a26",
        muted="#6b5a6d", line="#e6d6e4", accent="#7b2d63", accent2="#c084b8",
        on_accent="#ffffff", hero_bg="#2c1329", hero_ink="#fdf7fb",
        font_display=SERIF, font_body=SANS, display_weight="600",
        display_tracking="-0.015em", display_case="none",
        radius="14px", radius_sm="10px", pill="999px", pattern="rings", dark=False),
    "citrus": dict(
        label="Citrus", blurb="Charcoal and lime with tight grotesk type. Energetic without shouting.",
        bg="#ffffff", surface="#f7f8f4", surface2="#eaeee0", text="#14180f",
        muted="#59604f", line="#dbe1cd", accent="#4d7c0f", accent2="#a3e635",
        on_accent="#ffffff", hero_bg="#14180f", hero_ink="#f7f8f4",
        font_display=GROTESK, font_body=SANS, display_weight="700",
        display_tracking="-0.03em", display_case="none",
        radius="6px", radius_sm="4px", pill="4px", pattern="diag", dark=False),
    "berry": dict(
        label="Berry", blurb="Hot magenta on off-white with soft corners. Bold and a bit fun.",
        bg="#fffcfd", surface="#fdf2f8", surface2="#fbe0ee", text="#1f1023",
        muted="#6b5270", line="#f5d3e5", accent="#c81e6b", accent2="#f472b6",
        on_accent="#ffffff", hero_bg="#3b0a2e", hero_ink="#fff0f7",
        font_display=ROUNDED, font_body=SANS, display_weight="750",
        display_tracking="-0.025em", display_case="none",
        radius="20px", radius_sm="14px", pill="999px", pattern="dots", dark=False),
    "stone": dict(
        label="Stone", blurb="Warm greys and a soft black serif. Architectural, quiet, expensive-looking.",
        bg="#f6f5f2", surface="#ffffff", surface2="#e8e6df", text="#1c1b18",
        muted="#63605a", line="#dad7cf", accent="#3f3d37", accent2="#8a8578",
        on_accent="#f6f5f2", hero_bg="#1c1b18", hero_ink="#f6f5f2",
        font_display=SERIF, font_body=SANS, display_weight="600",
        display_tracking="-0.015em", display_case="none",
        radius="2px", radius_sm="2px", pill="2px", pattern="grid", dark=False),
    "mint": dict(
        label="Mint", blurb="Emerald on white with generous rounding. Fresh and approachable.",
        bg="#ffffff", surface="#f2fbf6", surface2="#d8f3e6",
        text="#0e2019", muted="#4b6a5e", line="#c4ebd9", accent="#0b7a56", accent2="#5eead4",
        on_accent="#ffffff", hero_bg="#0b3b2c", hero_ink="#f2fbf6",
        font_display=ROUNDED, font_body=SANS, display_weight="700",
        display_tracking="-0.025em", display_case="none",
        radius="18px", radius_sm="12px", pill="999px", pattern="waves", dark=False),
    "ink": dict(
        label="Ink", blurb="Cream paper and deep indigo, serif throughout. Reads like good letterhead.",
        bg="#fbfaf6", surface="#ffffff", surface2="#ececf5", text="#14142b",
        muted="#545470", line="#dcdceb", accent="#312e81", accent2="#6366f1",
        on_accent="#fbfaf6", hero_bg="#14142b", hero_ink="#f4f4fb",
        font_display=SERIF, font_body=SERIF, display_weight="600",
        display_tracking="-0.012em", display_case="none",
        radius="4px", radius_sm="3px", pill="3px", pattern="rings", dark=False),
    "harbor": dict(
        label="Harbor", blurb="Deep navy with a warm amber accent. Dark, but not cold.",
        bg="#0e1a26", surface="#152534", surface2="#1e3145", text="#eef4f9",
        muted="#93a8bb", line="#24384c", accent="#e0a458", accent2="#f2c98a",
        on_accent="#0e1a26", hero_bg="#0a1420", hero_ink="#eef4f9",
        font_display=SANS, font_body=SANS, display_weight="700",
        display_tracking="-0.03em", display_case="none",
        radius="8px", radius_sm="6px", pill="6px", pattern="waves", dark=True),
    "noir": dict(
        label="Noir", blurb="Near-black and antique gold with a serif voice. Restaurants, law, anything premium.",
        bg="#0d0c0a", surface="#161410", surface2="#211e18", text="#f3efe6",
        muted="#a49c8b", line="#2c2820", accent="#c9a227", accent2="#e6c76a",
        on_accent="#0d0c0a", hero_bg="#0d0c0a", hero_ink="#f3efe6",
        font_display=SERIF, font_body=SANS, display_weight="600",
        display_tracking="-0.01em", display_case="none",
        radius="2px", radius_sm="2px", pill="2px", pattern="diag", dark=True),
    "sunset": dict(
        label="Sunset", blurb="Violet-black with an orange-to-purple gradient. Nightlife and creative studios.",
        bg="#120e1c", surface="#1b1528", surface2="#261e38", text="#f4f0fb",
        muted="#a397ba", line="#302747", accent="#f97316", accent2="#a855f7",
        on_accent="#1a1005", hero_bg="#120e1c", hero_ink="#f4f0fb",
        font_display=SANS, font_body=SANS, display_weight="750",
        display_tracking="-0.035em", display_case="none",
        radius="20px", radius_sm="14px", pill="999px", pattern="rings", dark=True),
}

LAYOUTS = {
    "classic": "Centred nav, split hero, three-up services, testimonials, contact. The reliable local-business standard.",
    "bold": "Full-height hero with oversized type, big numbered service rows, stat band, dark call-to-action.",
    "split": "Fixed left sidebar with brand, nav and contact details; content scrolls beside it. Agency feel.",
    "minimal": "Narrow single column, huge whitespace, hairline rules, small-caps labels. Editorial and quiet.",
    "landing": "One-page conversion flow: hero, benefits, how it works, packages, FAQ, sticky mobile call bar.",
    "showcase": "Visual-first grid with an overlapping collage hero. Trades, salons, photographers, anyone with work to show.",
    "magazine": "Newspaper masthead, multi-column text, hairline rules and pull quotes. For businesses with something to say.",
    "panel": "Floating rounded panels on a tinted page, pill navigation. The modern app look.",
    "directory": "Information-dense: anchor sub-nav, a priced service list with dotted leaders, hours and address up front. Menus and clinics.",
    "poster": "Overlaid nav on a full-bleed type poster, then alternating full-width colour bands. Graphic and loud.",
}


def theme(key):
    t = dict(THEMES[key])
    t["key"] = key
    return t


def _seed(text):
    return int(hashlib.sha256(text.encode("utf-8")).hexdigest()[:8], 16)


def initials(name):
    words = [w for w in "".join(c if c.isalnum() or c.isspace() else " "
                               for c in name).split() if w]
    skip = {"the", "and", "of", "co", "inc", "llc", "ltd"}
    keep = [w for w in words if w.lower() not in skip] or words
    if len(keep) == 1:
        return keep[0][:2].upper()
    return (keep[0][0] + keep[1][0]).upper()


MARKS = ("shield", "hex", "circle", "square", "arch", "diamond")


def logo_mark(name, t, size=64, ink=None, plate=None):
    """Deterministic monogram mark — same business always gets the same shape."""
    ink = ink or t["accent"]
    plate = plate or "none"
    shape = MARKS[_seed(name) % len(MARKS)]
    mono = initials(name)
    s = size
    body = {
        "shield": f'<path d="M32 4 58 14v22c0 14-11 22-26 26C17 58 6 50 6 36V14z"/>',
        "hex": '<path d="M32 3 57 17.5v29L32 61 7 46.5v-29z"/>',
        "circle": '<circle cx="32" cy="32" r="29"/>',
        "square": '<rect x="4" y="4" width="56" height="56" rx="12"/>',
        "arch": '<path d="M6 60V30a26 26 0 0 1 52 0v30z"/>',
        "diamond": '<path d="M32 2 62 32 32 62 2 32z"/>',
    }[shape]
    fs = 25 if len(mono) > 1 else 30
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" width="{s}" '
        f'height="{s}" role="img" aria-label="{esc(name)} logo">'
        f'<g fill="{ink}">{body}</g>'
        f'<text x="32" y="32" text-anchor="middle" dominant-baseline="central" '
        f'fill="{plate if plate != "none" else t["bg"]}" font-family="{SANS}" '
        f'font-size="{fs}" font-weight="700" letter-spacing="-0.02em">{esc(mono)}</text>'
        f'</svg>'
    )


def favicon(name, t):
    return logo_mark(name, t, size=64, ink=t["accent"], plate=t["bg"])


def brand_html(b, t, height=34, on_dark=False):
    """The mark as it appears in page markup: the owner's logo if they gave one,
    otherwise the generated monogram."""
    if b.get("logo"):
        # logo_href lets callers point at a shared copy (the 160 gallery previews)
        # or at the data URI itself (a self-contained preview page).
        href = b.get("logo_href") or f"assets/logo.{b['logo_ext']}"
        return (f'<img class="brand__logo" src="{esc(href)}" '
                f'alt="{esc(b["name"])}" height="{height}" '
                f'style="height:{height}px">')
    ink = t["hero_ink"] if on_dark else t["accent"]
    plate = t["hero_bg"] if on_dark else t["bg"]
    return logo_mark(b["name"], t, size=height, ink=ink, plate=plate)


def brand_svg(b, t, x, y, box, on_dark=False, max_w=None):
    """The mark as an SVG fragment for the business card and the social image.
    The logo is embedded as its data URI so the file stays self-contained, and it
    sits on a light plate over dark artwork unless the brief says it does not need
    one — a dark logo on a dark card is otherwise invisible in print."""
    if not b.get("logo"):
        ink = t["hero_ink"] if on_dark else t["accent"]
        plate = t["hero_bg"] if on_dark else t["bg"]
        mark = logo_mark(b["name"], t, size=box, ink=ink, plate=plate)
        inner = mark[mark.index(">") + 1:mark.rindex("</svg>")]
        return (f'<svg x="{x}" y="{y}" width="{box}" height="{box}" '
                f'viewBox="0 0 64 64">{inner}</svg>')

    # `box` caps the height; a wordmark is allowed to run wider than it is tall
    # rather than being shrunk to fit a square.
    w, h = b["logo_w"] or 1.0, b["logo_h"] or 1.0
    scale = min((max_w or box) / w, box / h)
    dw, dh = w * scale, h * scale
    plate = ""
    if on_dark and b.get("logo_needs_light", True):
        pad = box * 0.14
        plate = (f'<rect x="{x - pad:.0f}" y="{y + (box - dh) / 2 - pad:.0f}" '
                 f'width="{dw + pad * 2:.0f}" height="{dh + pad * 2:.0f}" '
                 f'rx="{box * 0.1:.0f}" fill="{t["hero_ink"]}"/>')
    return (f'{plate}<image x="{x:.0f}" y="{y + (box - dh) / 2:.0f}" '
            f'width="{dw:.0f}" height="{dh:.0f}" '
            f'preserveAspectRatio="xMidYMid meet" href="{esc(b["logo"])}"/>')


def pattern_svg(t, ink=None, opacity=0.10):
    """Seamless background texture as a data-URI-safe SVG string."""
    ink = ink or t["accent"]
    kind = t["pattern"]
    if kind == "grid":
        inner = ('<path d="M40 0H0V40" fill="none" stroke="INK" stroke-width="1"/>')
        size = 40
    elif kind == "dots":
        inner = '<circle cx="10" cy="10" r="2" fill="INK"/>'
        size = 20
    elif kind == "rings":
        inner = ('<circle cx="30" cy="30" r="22" fill="none" stroke="INK" stroke-width="1"/>'
                 '<circle cx="30" cy="30" r="11" fill="none" stroke="INK" stroke-width="1"/>')
        size = 60
    elif kind == "waves":
        inner = ('<path d="M0 20c10-12 20-12 30 0s20 12 30 0" fill="none" stroke="INK" '
                 'stroke-width="1.5"/>')
        size = 60
    else:  # diag
        inner = '<path d="M0 24 24 0M-6 6 6-6M18 30 30 18" stroke="INK" stroke-width="1.5" fill="none"/>'
        size = 24
    inner = inner.replace("INK", ink)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" '
            f'viewBox="0 0 {size} {size}" opacity="{opacity}">{inner}</svg>')


def data_uri(svg):
    safe = (svg.replace("#", "%23").replace('"', "'")
               .replace("<", "%3C").replace(">", "%3E")
               .replace("\n", "").replace("  ", " "))
    return f"url(\"data:image/svg+xml,{safe}\")"


COMPOSITIONS = ("arcs", "grid", "topo", "waves", "columns")


def _arcs(w, h, s, g, ink):
    r = min(w, h) * 0.92
    cx, cy = w * 0.74, h * 0.3
    ring = min(w, h) * 0.3
    return [
        f'<path d="M0 {h} L0 {h - r:.0f} A {r:.0f} {r:.0f} 0 0 0 {r:.0f} {h} Z" fill="url(#{g})"/>',
        f'<circle cx="{cx:.0f}" cy="{cy:.0f}" r="{ring:.0f}" fill="none" stroke="{ink}" '
        f'stroke-width="{max(2, w / 220):.1f}" opacity="0.45"/>',
        f'<circle cx="{cx:.0f}" cy="{cy:.0f}" r="{ring * 0.62:.0f}" fill="none" stroke="{ink}" '
        f'stroke-width="{max(2, w / 220):.1f}" opacity="0.3"/>',
        f'<circle cx="{cx:.0f}" cy="{cy:.0f}" r="{ring * 0.26:.0f}" fill="{ink}" opacity="0.85"/>',
        f'<rect x="0" y="{h * 0.16:.0f}" width="{w * 0.34:.0f}" height="{max(4, h / 70):.0f}" '
        f'fill="{ink}" opacity="0.55"/>',
    ]


def _grid(w, h, s, g, ink):
    step = max(28, int(min(w, h) / 9))
    lines = []
    x = step
    while x < w:
        lines.append(f'<path d="M{x} 0V{h}" stroke="{ink}" stroke-width="1" opacity="0.16"/>')
        x += step
    y = step
    while y < h:
        lines.append(f'<path d="M0 {y}H{w}" stroke="{ink}" stroke-width="1" opacity="0.16"/>')
        y += step
    cells = []
    cols, rows = max(1, w // step), max(1, h // step)
    for i in range(4):
        cx = ((s >> (i * 4)) % cols) * step
        cy = ((s >> (i * 5 + 2)) % rows) * step
        span = 1 + ((s >> (i * 3)) % 2)
        cells.append(f'<rect x="{cx}" y="{cy}" width="{step * span}" height="{step * span}" '
                     f'fill="url(#{g})" opacity="{0.95 - i * 0.18:.2f}"/>')
    cells.append(f'<circle cx="{w * 0.68:.0f}" cy="{h * 0.62:.0f}" r="{min(w, h) * 0.3:.0f}" '
                 f'fill="none" stroke="{ink}" stroke-width="{max(2, w / 200):.1f}" opacity="0.5"/>')
    return lines + cells


def _topo(w, h, s, g, ink):
    cx, cy = w * (0.3 + (s % 40) / 100), h * 0.5
    out = [f'<circle cx="{cx:.0f}" cy="{cy:.0f}" r="{min(w, h) * 0.17:.0f}" fill="url(#{g})"/>']
    step = min(w, h) * 0.115
    for i in range(1, 9):
        r = min(w, h) * 0.17 + step * i
        out.append(f'<circle cx="{cx + i * w * 0.012:.0f}" cy="{cy - i * h * 0.008:.0f}" '
                   f'r="{r:.0f}" fill="none" stroke="{ink}" '
                   f'stroke-width="{max(1.5, w / 320):.1f}" opacity="{0.5 - i * 0.045:.2f}"/>')
    return out


def _waves(w, h, s, g, ink):
    out = []
    bands = 5
    for i in range(bands):
        base = h * (0.32 + i * 0.15)
        amp = h * (0.10 - i * 0.012)
        q = w / 4
        d = (f"M0 {base:.0f} "
             f"Q{q:.0f} {base - amp:.0f} {2 * q:.0f} {base:.0f} "
             f"T{4 * q:.0f} {base:.0f} L{w} {h} L0 {h} Z")
        fill = f"url(#{g})" if i == bands - 1 else ink
        out.append(f'<path d="{d}" fill="{fill}" opacity="{0.16 + i * 0.16:.2f}"/>')
    out.append(f'<circle cx="{w * 0.76:.0f}" cy="{h * 0.22:.0f}" r="{min(w, h) * 0.13:.0f}" '
               f'fill="{ink}" opacity="0.9"/>')
    return out


def _columns(w, h, s, g, ink):
    n = 7
    gap = w / n
    bar = gap * 0.56
    out = []
    for i in range(n):
        frac = 0.28 + ((s >> (i * 3)) % 60) / 100
        bh = h * frac
        out.append(f'<rect x="{i * gap + (gap - bar) / 2:.0f}" y="{h - bh:.0f}" '
                   f'width="{bar:.0f}" height="{bh:.0f}" fill="url(#{g})" '
                   f'opacity="{0.55 + (i % 3) * 0.18:.2f}" rx="{bar * 0.12:.0f}"/>')
    out.append(f'<circle cx="{w * 0.3:.0f}" cy="{h * 0.28:.0f}" r="{min(w, h) * 0.2:.0f}" '
               f'fill="{ink}" opacity="0.32"/>')
    return out


def artwork(name, t, variant=0, w=800, h=600):
    """Abstract, industry-neutral hero/gallery art — a deliberate geometric
    composition rather than scattered shapes. Deterministic per business."""
    s = _seed(name + str(variant))
    kind = COMPOSITIONS[(s >> 3) % len(COMPOSITIONS)]
    # _seed is a sha256 digest, not hash() — Python randomises string hashing per
    # process, which made the same brief produce different bytes on every build.
    gid = f"g{_seed(name + '#' + str(variant)) % 100000}"
    rot = [15, 135, 45, 210, 300][s % 5]
    builder = {"arcs": _arcs, "grid": _grid, "topo": _topo,
               "waves": _waves, "columns": _columns}[kind]
    shapes = builder(w, h, s, gid, t["accent2"])
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
        f'width="{w}" height="{h}" role="img" aria-label="Decorative artwork" '
        f'preserveAspectRatio="xMidYMid slice">'
        f'<defs><linearGradient id="{gid}" gradientTransform="rotate({rot})">'
        f'<stop offset="0%" stop-color="{t["accent"]}"/>'
        f'<stop offset="100%" stop-color="{t["accent2"]}"/></linearGradient>'
        f'<clipPath id="c{gid}"><rect width="{w}" height="{h}"/></clipPath></defs>'
        f'<g clip-path="url(#c{gid})">'
        f'<rect width="{w}" height="{h}" fill="{t["surface2"]}"/>'
        f'{"".join(shapes)}</g></svg>'
    )


def picture(b, t, slot, w, h, alt=""):
    """A real photo for this slot if the brief has one, otherwise generated artwork.

    Slots cycle through whatever photos exist, so one photo fills every position
    rather than leaving half the page abstract and half photographic.
    """
    photos = b.get("photos") or []
    if photos:
        index = slot % len(photos)
        photo = photos[index]
        # By default the page links the written asset; photo_hrefs lets a preview
        # point at data URIs instead, so five pages do not each inline every photo.
        hrefs = b.get("photo_hrefs")
        href = hrefs[index] if hrefs else f"assets/photo-{index + 1}.{photo['ext']}"
        label = alt or photo.get("alt") or f"{b.get('name', '')} — our work"
        return (f'<img class="shot" src="{esc(href)}" alt="{esc(label)}" '
                f'loading="lazy" decoding="async" '
                f'width="{int(photo["w"])}" height="{int(photo["h"])}">')
    return artwork(b.get("name", ""), t, variant=slot, w=w, h=h)


ICONS = {
    "wrench": "M14 6a4 4 0 0 0-5.5 4.8L3 16.3 5.7 19l5.5-5.5A4 4 0 0 0 16 8l-2.2 2.2-1.9-1.9L14 6z",
    "spark": "M12 2l2.2 6.1L20 10l-5.8 1.9L12 18l-2.2-6.1L4 10l5.8-1.9z",
    "leaf": "M20 4C10 4 4 9 4 16v4h4v-4c0-5 4-8 12-8-2 6-6 9-11 10",
    "shield": "M12 2l8 3v6c0 5-3.4 8.7-8 11-4.6-2.3-8-6-8-11V5z",
    "clock": "M12 3a9 9 0 1 0 0 18 9 9 0 0 0 0-18zm0 4v5l3.5 2",
    "chat": "M4 5h16v10H9l-5 4z",
    "star": "M12 3l2.7 5.9 6.3.7-4.7 4.3 1.3 6.1L12 17l-5.6 3 1.3-6.1L3 9.6l6.3-.7z",
    "home": "M4 11l8-7 8 7v9h-6v-6h-4v6H4z",
    "truck": "M2 6h11v9H2zM13 9h4l3 3v3h-7zM6 18a2 2 0 1 0 0-.1M17 18a2 2 0 1 0 0-.1",
    "check": "M4 12l5 5L20 6",
    "phone": "M5 3h4l2 5-2.5 1.5a12 12 0 0 0 6 6L16 13l5 2v4a2 2 0 0 1-2 2A16 16 0 0 1 3 5a2 2 0 0 1 2-2z",
    "mail": "M3 6h18v12H3zM3 6l9 7 9-7",
    "pin": "M12 22s7-6.4 7-12A7 7 0 0 0 5 10c0 5.6 7 12 7 12zm0-9a3 3 0 1 0 0-6 3 3 0 0 0 0 6z",
    "scissors": "M6 4l12 12M18 4L6 16M7 19a2.5 2.5 0 1 0 0-5 2.5 2.5 0 0 0 0 5zm10 0a2.5 2.5 0 1 0 0-5 2.5 2.5 0 0 0 0 5z",
    "camera": "M3 7h4l2-2h6l2 2h4v12H3zm9 9a4 4 0 1 0 0-8 4 4 0 0 0 0 8z",
    "cup": "M4 4h12v8a6 6 0 0 1-12 0zM16 6h3a2 2 0 0 1 0 6h-3M3 21h14",
    "paw": "M12 13c3 0 5 2 5 4s-2 3-5 3-5-1-5-3 2-4 5-4zM7 8a2 2 0 1 0 0-4 2 2 0 0 0 0 4zm10 0a2 2 0 1 0 0-4 2 2 0 0 0 0 4zM4 13a2 2 0 1 0 0-4 2 2 0 0 0 0 4zm16 0a2 2 0 1 0 0-4 2 2 0 0 0 0 4z",
    "bolt": "M13 2L4 14h6l-1 8 9-12h-6z",
    "book": "M4 4h7a2 2 0 0 1 2 2v14a2 2 0 0 0-2-2H4zm16 0h-7a2 2 0 0 0-2 2v14a2 2 0 0 1 2-2h7z",
    "tooth": "M8 3c2 0 2 1 4 1s2-1 4-1a4 4 0 0 1 4 4c0 4-2 5-2.5 9S16 21 15 21s-1.2-2-1.5-4-.7-3-1.5-3-1.2 1-1.5 3S9.9 21 9 21s-1.5-1-2-5S4 11 4 7a4 4 0 0 1 4-4z",
    "key": "M14 4a6 6 0 1 1-4.2 10.2L4 20v-3h3v-3h3l-.8-.8A6 6 0 0 1 14 4zm2 4a1.5 1.5 0 1 0 0 3 1.5 1.5 0 0 0 0-3z",
    "dumbbell": "M3 9v6M6 7v10M18 7v10M21 9v6M6 12h12",
    "brush": "M14 3l7 7-8 8-4-4zM7 15l-3 6 6-3z",
    "gauge": "M12 20a8 8 0 1 1 8-8M12 12l5-3",
    "menu": "M4 7h16M4 12h16M4 17h16",
}

ICON_ORDER = ["check", "spark", "shield", "clock", "star", "chat", "bolt", "home"]

KEYWORD_ICONS = [
    (("pipe", "drain", "plumb", "leak", "faucet", "boiler", "water"), "wrench"),
    (("wire", "electric", "panel", "light", "power", "outlet", "ev"), "bolt"),
    (("lawn", "garden", "tree", "landscap", "mow", "hedge", "yard"), "leaf"),
    (("clean", "maid", "wash", "tidy", "sanit"), "spark"),
    (("cut", "hair", "barber", "style", "colour", "color", "salon", "nail"), "scissors"),
    (("photo", "video", "shoot", "portrait", "film"), "camera"),
    (("coffee", "cafe", "espresso", "brunch", "menu", "cater", "kitchen"), "cup"),
    (("dog", "cat", "pet", "groom", "walk", "boarding"), "paw"),
    (("train", "fitness", "gym", "coach", "workout", "strength"), "dumbbell"),
    (("tooth", "dental", "hygiene", "whiten", "implant", "ortho"), "tooth"),
    (("paint", "decor", "render", "plaster", "tiling", "design"), "brush"),
    (("car", "auto", "brake", "tyre", "tire", "engine", "mot", "service"), "gauge"),
    (("roof", "build", "extension", "renovat", "kitchen", "bathroom", "loft"), "home"),
    (("tutor", "lesson", "course", "class", "exam", "learn"), "book"),
    (("deliver", "haul", "move", "transport", "removal"), "truck"),
    (("law", "legal", "convey", "will", "estate", "property", "letting"), "key"),
    (("emergency", "24", "call out", "urgent", "same-day"), "clock"),
    (("consult", "strategy", "audit", "advice", "plan"), "chat"),
    (("guarantee", "warranty", "insured", "certified", "safe"), "shield"),
]


def icon_for(text, fallback_index=0):
    low = text.lower()
    for words, name in KEYWORD_ICONS:
        if any(w in low for w in words):
            return name
    return ICON_ORDER[fallback_index % len(ICON_ORDER)]


def icon_svg(name, size=24, stroke=2):
    path = ICONS.get(name, ICONS["check"])
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" '
            f'width="{size}" height="{size}" fill="none" stroke="currentColor" '
            f'stroke-width="{stroke}" stroke-linecap="round" stroke-linejoin="round" '
            f'aria-hidden="true"><path d="{path}"/></svg>')
