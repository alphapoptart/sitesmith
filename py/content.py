"""Industry presets and the brief -> page-copy pass.

Copy here is deliberately plain: short sentences, concrete nouns, no marketing
filler. Anything that would be a factual claim about the business (reviews,
awards, stats) is emitted as an obvious placeholder rather than invented.
"""

import base64
import json
import re
import struct
import unicodedata
import urllib.parse

PLACEHOLDER = "REPLACE"

PRESETS = {
    "trades": dict(
        label="Trades — plumbing, electrical, heating, handyman",
        services=[
            ("Emergency call-outs", "Burst pipes, dead sockets, no heating. We pick up the phone."),
            ("Repairs & fault finding", "We find the actual cause before anything gets replaced."),
            ("Installations", "New units fitted, tested and signed off in one visit."),
            ("Servicing & safety checks", "Annual checks with the paperwork you need for landlords or insurers."),
            ("Bathrooms & kitchens", "Full fit-outs, managed start to finish."),
            ("Maintenance contracts", "Fixed monthly cover for landlords and small businesses."),
        ],
        steps=[("Call or message", "Tell us what's happening. We'll say straight away if it's urgent."),
               ("Fixed quote", "We look, we price it, and that price is what you pay."),
               ("Job done", "Cleaned up behind us, with a receipt and a guarantee.")],
        points=["Fully insured", "Fixed prices, quoted up front", "We clean up after ourselves"],
        faq=[("Do you charge a call-out fee?", "REPLACE — state your call-out policy here."),
             ("How fast can you get here?", "REPLACE — your realistic response time."),
             ("Are you insured and certified?", "REPLACE — list your registration numbers.")],
        cta="Get a fixed quote",
        intro="Fixed prices, quoted before we start. Emergencies answered day and night."),
    "home_services": dict(
        label="Home services — cleaning, landscaping, pest, window cleaning",
        services=[
            ("Regular visits", "Weekly or fortnightly, same person each time."),
            ("One-off deep clean", "End of tenancy, post-build, or just a reset."),
            ("Outdoor work", "Lawns, hedges, borders and clearance."),
            ("Seasonal jobs", "The twice-a-year work that's easy to put off."),
            ("Commercial contracts", "Offices, lets and communal areas."),
            ("Extras on request", "Ovens, carpets, gutters — ask and we'll price it."),
        ],
        steps=[("Free walk-round", "We look at the place and agree what's included."),
               ("Fixed weekly price", "No hourly guessing, no surprise add-ons."),
               ("Same team, every time", "You get people who already know the job.")],
        points=["Same team every visit", "Fully insured", "No long contracts"],
        faq=[("Do I need to be home?", "REPLACE — your access arrangements."),
             ("What if I need to skip a week?", "REPLACE — your cancellation notice."),
             ("Do you bring your own supplies?", "REPLACE — what you provide.")],
        cta="Book a free quote",
        intro="The same team every visit, a price agreed up front, and no long contract."),
    "beauty": dict(
        label="Beauty & grooming — salon, barber, nails, spa",
        services=[
            ("Cuts & styling", "A proper consultation first, then the cut you actually asked for."),
            ("Colour", "Full head, balayage, root touch-ups and correction work."),
            ("Treatments", "Conditioning, scalp and repair treatments."),
            ("Nails", "Gel, acrylic, and a shape that lasts."),
            ("Special occasions", "Weddings, parties and shoots, booked in advance."),
            ("Walk-ins", "Chairs kept free where we can."),
        ],
        steps=[("Book online or call", "Pick your stylist and your slot."),
               ("Consultation", "Ten minutes to get the brief right before we start."),
               ("Aftercare", "What to use at home, and when to come back.")],
        points=["Patch tests on all colour", "Online booking", "Late nights on request"],
        faq=[("Do you need a patch test?", "REPLACE — your patch-test policy."),
             ("Can I request a specific stylist?", "REPLACE — how requests work."),
             ("What's your cancellation policy?", "REPLACE — your notice period.")],
        cta="Book an appointment",
        intro="Book online, get a proper consultation, and leave with something you actually like."),
    "food": dict(
        label="Food & drink — cafe, restaurant, bakery, catering",
        services=[
            ("Breakfast & brunch", "Served all morning, every day."),
            ("Lunch", "A short menu, changed when the produce changes."),
            ("Coffee", "Beans roasted locally, ground to order."),
            ("Cakes & bakes", "Made here, in the morning, in small batches."),
            ("Private hire", "The whole room, evenings and Sundays."),
            ("Catering", "Trays and platters for offices and parties."),
        ],
        steps=[("Drop in", "No booking needed for tables of four or fewer."),
               ("Order at the counter", "Or book ahead for bigger groups."),
               ("Take some home", "Beans, loaves and cakes to go.")],
        points=["Made on site daily", "Local suppliers", "Dog friendly"],
        faq=[("Do you take bookings?", "REPLACE — your booking policy."),
             ("Do you cater for allergies?", "REPLACE — what you can accommodate."),
             ("Is there parking?", "REPLACE — parking and access details.")],
        cta="See the menu",
        intro="Made here every morning. Walk in, or book the room for the evening."),
    "health": dict(
        label="Health — dental, physio, clinic, therapy, veterinary",
        services=[
            ("New patient assessment", "A full look at where things are before any treatment."),
            ("Routine care", "Regular appointments to keep small problems small."),
            ("Treatment plans", "Written down, priced, and explained in plain language."),
            ("Urgent appointments", "Slots held back each day for people in pain."),
            ("Follow-up", "We check the result, not just the appointment."),
            ("Referrals", "Straight through to a specialist when that's the right call."),
        ],
        steps=[("Get in touch", "Phone or the contact form — whichever you prefer."),
               ("First appointment", "Assessment, options, and a written plan."),
               ("Ongoing care", "Reminders when you're due, not before.")],
        points=["Registered practitioners", "Written treatment plans", "Evening appointments"],
        faq=[("Do you take new patients?", "REPLACE — current availability."),
             ("What does a first visit cost?", "REPLACE — your fee."),
             ("Do you offer payment plans?", "REPLACE — finance options.")],
        cta="Book an appointment",
        intro="An assessment, your options, and a written plan in language that makes sense."),
    "creative": dict(
        label="Creative — photography, video, design, studio",
        services=[
            ("Portraits", "Headshots and personal work, in studio or on location."),
            ("Events", "Full coverage, edited and delivered within the week."),
            ("Commercial", "Product, interiors and team shots for your own site."),
            ("Video", "Short films, interviews and social cuts."),
            ("Editing & retouching", "Work you've already shot, finished properly."),
            ("Prints", "Archival prints and albums."),
        ],
        steps=[("Tell me the brief", "What it's for, where it's going, and when you need it."),
               ("Shoot day", "Planned in advance so nothing runs over."),
               ("Delivery", "Edited gallery, licensed and ready to use.")],
        points=["Full usage rights included", "Delivered within 7 days", "Backup gear on every job"],
        faq=[("How far ahead should I book?", "REPLACE — your typical lead time."),
             ("What's included in the price?", "REPLACE — what a package covers."),
             ("Do you travel?", "REPLACE — your travel radius and charges.")],
        cta="Check availability",
        intro="Tell me what it's for and when you need it, and I'll tell you what it costs."),
    "fitness": dict(
        label="Fitness — gym, personal training, yoga, sports coaching",
        services=[
            ("One-to-one training", "Programmed around your schedule, not a template."),
            ("Small group sessions", "Four people maximum, so form still gets watched."),
            ("Classes", "Timetabled mornings and evenings."),
            ("Online coaching", "Programme, check-ins and video review."),
            ("Nutrition support", "Practical changes, not a meal plan you'll abandon."),
            ("Assessments", "Baseline testing so progress is measured, not guessed."),
        ],
        steps=[("Free consultation", "Goals, history, injuries, time available."),
               ("Your programme", "Written for you and adjusted as you go."),
               ("Review every 4 weeks", "What's working stays. What isn't, changes.")],
        points=["First session free", "No joining fee", "Cancel any time"],
        faq=[("I've never trained before — is that ok?", "REPLACE — how you handle beginners."),
             ("What are your opening hours?", "REPLACE — your hours."),
             ("Is there a contract?", "REPLACE — your terms.")],
        cta="Book a free session",
        intro="A programme written for you, reviewed every four weeks."),
    "auto": dict(
        label="Automotive — garage, MOT, bodywork, detailing, mobile mechanic",
        services=[
            ("Servicing", "Manufacturer schedule without the main dealer price."),
            ("Diagnostics", "Proper fault codes read and interpreted, not guessed at."),
            ("Repairs", "Brakes, clutches, suspension and exhausts."),
            ("Tyres", "Supplied, fitted and balanced while you wait."),
            ("Bodywork", "Dents, scuffs and paint correction."),
            ("Courtesy car", "So you're not stuck without one."),
        ],
        steps=[("Book a slot", "Online or over the phone."),
               ("We call before we start", "You approve the work and the price first."),
               ("Collect", "Itemised invoice, old parts kept if you want them.")],
        points=["No work done without your say-so", "Courtesy cars available", "12-month parts guarantee"],
        faq=[("Will this affect my warranty?", "REPLACE — your warranty position."),
             ("How long does a service take?", "REPLACE — typical turnaround."),
             ("Do you collect and deliver?", "REPLACE — your collection service.")],
        cta="Book your car in",
        intro="Nothing gets touched until you have approved the work and the price."),
    "professional": dict(
        label="Professional services — consulting, accounting, legal, IT, agency",
        services=[
            ("Initial review", "A clear read on where you actually are."),
            ("Ongoing advice", "A named contact who knows your file."),
            ("Compliance & filing", "Deadlines met without you chasing."),
            ("Projects", "Scoped, priced and delivered to a date."),
            ("Training", "So your team can do it without us next time."),
            ("Second opinions", "A straight answer on work someone else has done."),
        ],
        steps=[("Free first conversation", "Thirty minutes, no obligation, no sales script."),
               ("Written proposal", "Scope, price and timeline in one page."),
               ("Delivery", "Regular updates, and no invoice you weren't expecting.")],
        points=["Fixed fees, agreed up front", "A named contact", "Plain-English advice"],
        faq=[("How are you priced?", "REPLACE — fixed fee, retainer or hourly."),
             ("How quickly can you start?", "REPLACE — current availability."),
             ("Do you work remotely?", "REPLACE — how you work with clients.")],
        cta="Book a free consultation",
        intro="Fixed fees agreed up front, and a named person who knows your file."),
    "property": dict(
        label="Property — estate agency, lettings, construction, architecture",
        services=[
            ("Valuations", "Honest numbers, based on what's actually selling."),
            ("Sales", "Photography, listing, viewings and negotiation."),
            ("Lettings & management", "Tenants found, referenced and looked after."),
            ("Project work", "Extensions, conversions and refurbishments."),
            ("Planning & drawings", "Submitted and followed through."),
            ("Maintenance", "One number for everything that goes wrong."),
        ],
        steps=[("Free valuation", "We come out, look properly, and give you a number."),
               ("Go to market", "Professional photos and a listing that reads well."),
               ("Completion", "Chased weekly so it doesn't stall.")],
        points=["No sale, no fee", "Accompanied viewings", "Weekly progress updates"],
        faq=[("What are your fees?", "REPLACE — your fee structure."),
             ("How long are you tied in for?", "REPLACE — contract length."),
             ("Do you do viewings at weekends?", "REPLACE — your viewing hours.")],
        cta="Book a free valuation",
        intro="An honest valuation, professional photos, and weekly progress updates."),
    "retail": dict(
        label="Retail & makers — shop, boutique, workshop, craft",
        services=[
            ("In store", "Everything we make and stock, under one roof."),
            ("Made to order", "Tell us the size, the colour and the deadline."),
            ("Repairs & alterations", "We'd rather fix it than sell you a new one."),
            ("Gift cards", "Any amount, valid for a year."),
            ("Workshops", "Small classes, tools provided."),
            ("Wholesale", "Trade terms for stockists."),
        ],
        steps=[("Come in or message", "Tell us what you're after."),
               ("We'll source or make it", "With a price and a date before we start."),
               ("Collect or delivered", "Whichever suits you.")],
        points=["Made on site", "Repairs welcome", "Gift wrapping free"],
        faq=[("Do you ship?", "REPLACE — delivery options and cost."),
             ("Can I return something?", "REPLACE — your returns policy."),
             ("Do you do custom orders?", "REPLACE — lead time for custom work.")],
        cta="Visit the shop",
        intro="Made and repaired on site. Come in and tell us what you are after."),
    "education": dict(
        label="Education & childcare — tutoring, nursery, driving, music",
        services=[
            ("One-to-one", "Sessions built around what's actually not clicking."),
            ("Small groups", "Cheaper per head, and they learn from each other."),
            ("Exam preparation", "Past papers, technique and timing."),
            ("Beginners welcome", "No assumed knowledge, no rushing."),
            ("Progress reports", "Written updates so you know it's working."),
            ("Holiday courses", "Intensive weeks during school breaks."),
        ],
        steps=[("Free first chat", "Where they're at, and what they're aiming for."),
               ("Trial session", "No commitment until everyone's happy."),
               ("Regular sessions", "Same slot each week, with progress written down.")],
        points=["DBS checked", "Free trial session", "Progress reports every half term"],
        faq=[("Are you DBS checked?", "REPLACE — your checks and certificates."),
             ("Do you teach online?", "REPLACE — online and in-person options."),
             ("What do you charge?", "REPLACE — your rates.")],
        cta="Book a free trial",
        intro="A free trial session first, then a regular slot and progress in writing."),
    "general": dict(
        label="Something else / general business",
        services=[
            ("What we do", "REPLACE — describe your main service in one line."),
            ("How we help", "REPLACE — describe a second service."),
            ("Getting started", "REPLACE — describe a third service."),
        ],
        steps=[("Get in touch", "Tell us what you need."),
               ("We'll come back with a price", "Clear, fixed and in writing."),
               ("Job done", "On time, and to the standard we agreed.")],
        points=["REPLACE — a reason to choose you",
                "REPLACE — a second reason",
                "REPLACE — a third reason"],
        faq=[("REPLACE — a question customers actually ask", "REPLACE — your answer."),
             ("REPLACE — a second question", "REPLACE — your answer."),
             ("REPLACE — a third question", "REPLACE — your answer.")],
        cta="Get in touch",
        intro="REPLACE — one sentence on why someone should call you rather than anyone else."),
}

PRESET_ORDER = list(PRESETS)


def slugify(text):
    s = re.sub(r"[^a-z0-9]+", "-", (text or "").lower()).strip("-")
    return s or "business"


LOGO_MAX_BYTES = 512 * 1024

_MIME_EXT = {
    "image/png": "png", "image/jpeg": "jpg", "image/gif": "gif",
    "image/webp": "webp", "image/svg+xml": "svg",
}


def parse_data_uri(uri):
    """-> (mime, raw bytes). Raises ValueError on anything that is not an image
    data URI, so a bad paste fails loudly at brief time rather than silently
    producing a broken <img> on every page."""
    uri = (uri or "").strip()
    if not uri.startswith("data:"):
        raise ValueError("logo must be a data: URI")
    head, _, payload = uri[5:].partition(",")
    if not payload:
        raise ValueError("logo data URI has no payload")
    bits = head.split(";")
    mime = bits[0].lower() or "application/octet-stream"
    if mime not in _MIME_EXT:
        raise ValueError(f"unsupported logo type {mime!r} — use PNG, JPEG, GIF, "
                         f"WebP or SVG")
    if "base64" in bits[1:]:
        pad = "=" * (-len(payload) % 4)
        try:
            data = base64.b64decode(payload + pad, validate=False)
        except Exception as exc:
            raise ValueError(f"logo base64 will not decode: {exc}")
    else:
        data = urllib.parse.unquote_to_bytes(payload)
    if not data:
        raise ValueError("logo decoded to zero bytes")
    return mime, data


def _svg_size(data):
    text = data.decode("utf-8", "replace")[:4000]
    def attr(name):
        m = re.search(rf'\b{name}\s*=\s*["\']([^"\']+)["\']', text)
        if not m:
            return None
        num = re.match(r"\s*([0-9.]+)", m.group(1))
        return float(num.group(1)) if num else None
    w, h = attr("width"), attr("height")
    if w and h:
        return w, h
    box = re.search(r'\bviewBox\s*=\s*["\']([^"\']+)["\']', text)
    if box:
        parts = re.split(r"[\s,]+", box.group(1).strip())
        if len(parts) == 4:
            try:
                return abs(float(parts[2])), abs(float(parts[3]))
            except ValueError:
                pass
    return None


def image_size(data, mime):
    """(width, height) in pixels, or None if the header cannot be read. Enough
    header parsing to lay a logo out without distorting it — no decoding."""
    try:
        if mime == "image/png" and data[:8] == b"\x89PNG\r\n\x1a\n":
            w, h = struct.unpack(">II", data[16:24])
            return float(w), float(h)
        if mime == "image/gif" and data[:3] == b"GIF":
            w, h = struct.unpack("<HH", data[6:10])
            return float(w), float(h)
        if mime == "image/jpeg" and data[:2] == b"\xff\xd8":
            i = 2
            while i + 9 < len(data):
                if data[i] != 0xFF:
                    i += 1
                    continue
                marker = data[i + 1]
                if marker in (0xD8, 0x01) or 0xD0 <= marker <= 0xD7:
                    i += 2
                    continue
                length = struct.unpack(">H", data[i + 2:i + 4])[0]
                if 0xC0 <= marker <= 0xCF and marker not in (0xC4, 0xC8, 0xCC):
                    h, w = struct.unpack(">HH", data[i + 5:i + 9])
                    return float(w), float(h)
                i += 2 + length
            return None
        if mime == "image/webp" and data[:4] == b"RIFF" and data[8:12] == b"WEBP":
            chunk = data[12:16]
            if chunk == b"VP8X":
                w = int.from_bytes(data[24:27], "little") + 1
                h = int.from_bytes(data[27:30], "little") + 1
                return float(w), float(h)
            if chunk == b"VP8 ":
                w = struct.unpack("<H", data[26:28])[0] & 0x3FFF
                h = struct.unpack("<H", data[28:30])[0] & 0x3FFF
                return float(w), float(h)
            if chunk == b"VP8L":
                bits = int.from_bytes(data[21:25], "little")
                return float((bits & 0x3FFF) + 1), float(((bits >> 14) & 0x3FFF) + 1)
            return None
        if mime == "image/svg+xml":
            return _svg_size(data)
    except Exception:
        return None
    return None


_NUMBER = re.compile(r"\d[\d,]*(?:\.\d+)?")


def has_currency(text):
    """True if the string already carries a currency mark of any kind."""
    return any(unicodedata.category(ch) == "Sc" for ch in str(text))


def format_price(raw, currency="", after=False):
    """Apply the brief's currency to a bare number, and otherwise leave the owner's
    text alone. Idempotent, so re-running the build never doubles the symbol up."""
    raw = (raw or "").strip()
    if not raw or not currency:
        return raw
    if not _NUMBER.search(raw):        # "POA", "Free", "On request"
        return raw
    if currency in raw or has_currency(raw):
        return raw
    if after:
        return _NUMBER.sub(lambda m: f"{m.group(0)} {currency}", raw, count=1)
    return _NUMBER.sub(lambda m: f"{currency}{m.group(0)}", raw, count=1)


DEFAULT_BRIEF = {
    "name": "", "tagline": "", "preset": "general", "city": "",
    "currency": "", "currency_after": False,
    "logo": "", "logo_has_name": False, "logo_needs_light": True,
    "phone": "", "email": "", "address": "", "hours": "Mon–Fri, 8am – 6pm",
    "services": [], "owner": "", "owner_title": "", "domain": "",
    "cta": "", "years": "", "about": "", "layout": "classic", "theme": "slate",
}


def load(path):
    with open(path, encoding="utf-8") as fh:
        data = json.load(fh)
    brief = dict(DEFAULT_BRIEF)
    brief.update({k: v for k, v in data.items() if k in DEFAULT_BRIEF})
    return normalise(brief)


def normalise(brief):
    b = dict(DEFAULT_BRIEF)
    b.update(brief)
    if b["preset"] not in PRESETS:
        b["preset"] = "general"
    preset = PRESETS[b["preset"]]

    b["name"] = (b["name"] or "Your Business").strip()
    b["slug"] = slugify(b["name"])
    if not b["tagline"]:
        b["tagline"] = f"{preset['label'].split('—')[0].strip()} you can rely on"
    if not b["cta"]:
        b["cta"] = preset["cta"]
    if not b["owner_title"]:
        b["owner_title"] = "Owner"

    # A logo that will not parse is dropped rather than emitted as a broken <img> on
    # every page — the reason lands in CONTENT.md via logo_error.
    b["logo_error"] = ""
    b["logo_mime"] = b["logo_ext"] = ""
    b["logo_w"] = b["logo_h"] = 0.0
    b["logo_square"] = False
    if b["logo"]:
        try:
            mime, data = parse_data_uri(b["logo"])
            if len(data) > LOGO_MAX_BYTES:
                raise ValueError(
                    f"logo is {len(data) // 1024} KB — keep it under "
                    f"{LOGO_MAX_BYTES // 1024} KB so pages stay quick to load")
            size = image_size(data, mime)
            b["logo_mime"] = mime
            b["logo_ext"] = _MIME_EXT[mime]
            if size:
                b["logo_w"], b["logo_h"] = size
                ratio = b["logo_w"] / b["logo_h"] if b["logo_h"] else 0
                b["logo_square"] = 0.8 <= ratio <= 1.25
            else:
                # Unknown dimensions: assume square so nothing gets stretched.
                b["logo_w"] = b["logo_h"] = 1.0
                b["logo_square"] = True
        except ValueError as exc:
            b["logo_error"] = str(exc)
            b["logo"] = ""

    # Prices stay free text ("from £120", "POA", "£45/hr"). The currency, if the brief
    # sets one, is only applied to a price typed as a bare number.
    currency = (b.get("currency") or "").strip()
    after = bool(b.get("currency_after"))

    def money(raw):
        return format_price(raw, currency, after)

    def preset_desc(title):
        match = next((s for s in preset["services"]
                      if s[0].lower() == title.lower()), None)
        return match[1] if match else f"{PLACEHOLDER} — one line on what this involves."

    services = []
    for item in b["services"] or []:
        if isinstance(item, str):
            title = item.strip()
            services.append({"title": title, "desc": preset_desc(title), "price": ""})
        elif isinstance(item, dict) and item.get("title"):
            title = item["title"].strip()
            services.append({"title": title,
                             "desc": item.get("desc") or preset_desc(title),
                             "price": money(item.get("price"))})
    if not services:
        services = [{"title": t, "desc": d, "price": ""}
                    for t, d in preset["services"][:6]]
    b["services"] = services[:6]
    b["has_prices"] = any(s["price"] for s in b["services"])

    b["steps"] = [{"title": t, "desc": d} for t, d in preset["steps"]]
    b["points"] = list(preset["points"])
    b["faq"] = [{"q": q, "a": a} for q, a in preset["faq"]]

    where = f" in {b['city']}" if b["city"] else ""
    if not b["about"]:
        years = (f"We have been at it for {b['years']} years. "
                 if str(b["years"]).strip() else "")
        b["about"] = (
            f"{b['name']} is a small team{where} doing one thing properly: "
            f"{b['tagline'][0].lower() + b['tagline'][1:] if b['tagline'] else 'good work'}. "
            f"{years}"
            f"{PLACEHOLDER} — two or three sentences here in your own words. "
            f"Who you are, why you started, and what a customer can expect. "
            f"Plain language beats clever."
        )
    # The h1 is the tagline alone — the business name is already in the header and
    # the footer, and repeating it makes the headline too long to set well.
    b["headline"] = b["tagline"].rstrip(".")
    b["hero_lede"] = (f"{b['name']}"
                      + (f", {b['city']}." if b["city"] else ".")
                      + f" {preset['intro']}")
    b["where"] = where.strip()
    b["site_url"] = site_url(b)
    return b


def site_url(brief):
    domain = (brief.get("domain") or "").strip()
    if not domain:
        return ""
    domain = re.sub(r"^https?://", "", domain).strip("/")
    return f"https://{domain}"


def contact_lines(b):
    out = []
    if b["phone"]:
        out.append(("phone", b["phone"], f"tel:{re.sub(r'[^0-9+]', '', b['phone'])}"))
    if b["email"]:
        out.append(("mail", b["email"], f"mailto:{b['email']}"))
    if b["address"]:
        out.append(("pin", b["address"], ""))
    if b["hours"]:
        out.append(("clock", b["hours"], ""))
    return out


def placeholders(b):
    """Every spot the owner still needs to fill in, for CONTENT.md."""
    found = []

    def scan(label, text):
        if isinstance(text, str) and PLACEHOLDER in text:
            found.append((label, text))

    scan("About paragraph", b["about"])
    scan("Hero sub-heading", b.get("hero_lede", ""))
    if b.get("logo_error"):
        found.append(("Logo", f"not used — {b['logo_error']}"))
    for s in b["services"]:
        scan(f"Service: {s['title']}", s["desc"])
    for p in b["points"]:
        scan("Reason to choose you", p)
    for f in b["faq"]:
        scan(f"FAQ: {f['q']}", f["a"])
        scan("FAQ question", f["q"])
    if not b["phone"]:
        found.append(("Phone number", "not set — the call buttons are hidden"))
    if not b["email"]:
        found.append(("Email address", "not set — the contact form has nowhere to send"))
    if not b["domain"]:
        found.append(("Domain", "not set — the business card QR points at the placeholder URL"))
    return found
