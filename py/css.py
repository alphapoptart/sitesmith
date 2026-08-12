"""Stylesheet generation: shared base + per-layout rules, built from theme tokens."""

from design import data_uri, pattern_svg


def base_css(t):
    return f""":root {{
  --bg: {t['bg']};
  --surface: {t['surface']};
  --surface-2: {t['surface2']};
  --text: {t['text']};
  --muted: {t['muted']};
  --line: {t['line']};
  --accent: {t['accent']};
  --accent-2: {t['accent2']};
  --on-accent: {t['on_accent']};
  --hero-bg: {t['hero_bg']};
  --hero-ink: {t['hero_ink']};
  --radius: {t['radius']};
  --radius-sm: {t['radius_sm']};
  --pill: {t['pill']};
  --font-display: {t['font_display']};
  --font-body: {t['font_body']};
  --display-weight: {t['display_weight']};
  --display-tracking: {t['display_tracking']};
  --display-case: {t['display_case']};
  --maxw: 1140px;
  --gap: clamp(1rem, 2.5vw, 1.75rem);
  --section-y: clamp(3.5rem, 8vw, 7rem);
  --shadow: 0 1px 2px rgba(0,0,0,.05), 0 8px 24px -12px rgba(0,0,0,.18);
  --shadow-lg: 0 2px 4px rgba(0,0,0,.05), 0 24px 60px -24px rgba(0,0,0,.28);
}}

*, *::before, *::after {{ box-sizing: border-box; }}
html {{ scroll-behavior: smooth; -webkit-text-size-adjust: 100%; }}
body {{
  margin: 0;
  background: var(--bg);
  color: var(--text);
  font-family: var(--font-body);
  font-size: clamp(1rem, 0.96rem + 0.2vw, 1.075rem);
  line-height: 1.65;
  -webkit-font-smoothing: antialiased;
  overflow-x: hidden;
}}
img, svg {{ max-width: 100%; height: auto; display: block; }}
a {{ color: inherit; }}

h1, h2, h3, h4, .display {{
  font-family: var(--font-display);
  font-weight: var(--display-weight);
  letter-spacing: var(--display-tracking);
  text-transform: var(--display-case);
  line-height: 1.08;
  margin: 0 0 .6em;
  text-wrap: balance;
}}
h1 {{ font-size: clamp(2.35rem, 1.4rem + 4.4vw, 4.4rem); }}
h2 {{ font-size: clamp(1.85rem, 1.25rem + 2.6vw, 2.9rem); }}
h3 {{ font-size: clamp(1.15rem, 1.02rem + 0.6vw, 1.4rem); line-height: 1.25; }}
p {{ margin: 0 0 1.1em; }}
p:last-child {{ margin-bottom: 0; }}

.wrap {{ width: min(100% - 2.5rem, var(--maxw)); margin-inline: auto; }}
.section {{ padding-block: var(--section-y); }}
.section--tint {{ background: var(--surface); }}
.section--edge {{ border-top: 1px solid var(--line); }}
.lede {{
  font-size: clamp(1.08rem, 1rem + 0.5vw, 1.3rem);
  color: var(--muted); max-width: 62ch; text-wrap: pretty;
}}
.eyebrow {{
  font-family: var(--font-display);
  font-size: .78rem; font-weight: 700; letter-spacing: .16em;
  text-transform: uppercase; color: var(--accent);
  margin: 0 0 1rem; display: flex; align-items: center; gap: .6rem;
}}
.eyebrow::after {{ content: ""; height: 1px; flex: 1; background: var(--line); max-width: 5rem; }}
.center {{ text-align: center; }}
.center .eyebrow {{ justify-content: center; }}
.center .eyebrow::after {{ display: none; }}
.center .lede {{ margin-inline: auto; }}
.muted {{ color: var(--muted); }}

/* --- buttons --- */
.btn {{
  --btn-bg: var(--accent); --btn-ink: var(--on-accent); --btn-line: var(--accent);
  display: inline-flex; align-items: center; justify-content: center; gap: .55rem;
  padding: .85rem 1.5rem; border-radius: var(--pill);
  background: var(--btn-bg); color: var(--btn-ink);
  border: 1.5px solid var(--btn-line);
  font-family: var(--font-display); font-weight: 650; font-size: 1rem;
  letter-spacing: .01em; text-decoration: none; cursor: pointer;
  transition: transform .18s ease, box-shadow .18s ease, background .18s ease, color .18s ease;
  white-space: nowrap;
}}
.btn:hover {{ transform: translateY(-2px); box-shadow: var(--shadow); }}
.btn:active {{ transform: translateY(0); }}
.btn--ghost {{ --btn-bg: transparent; --btn-ink: var(--text); --btn-line: var(--line); }}
.btn--ghost:hover {{ --btn-line: var(--accent); --btn-ink: var(--accent); }}
.btn--onhero {{ --btn-bg: transparent; --btn-ink: var(--hero-ink); --btn-line: color-mix(in srgb, var(--hero-ink) 45%, transparent); }}
.btn--onhero:hover {{ --btn-bg: var(--hero-ink); --btn-ink: var(--hero-bg); --btn-line: var(--hero-ink); }}
.btn--lg {{ padding: 1.05rem 2rem; font-size: 1.05rem; }}
.btn-row {{ display: flex; flex-wrap: wrap; gap: .8rem; margin-top: 1.9rem; }}
.center .btn-row {{ justify-content: center; }}

:where(a, button, summary, input, textarea, select):focus-visible {{
  outline: 3px solid var(--accent-2); outline-offset: 3px; border-radius: 4px;
}}

/* --- header --- */
.site-head {{
  position: sticky; top: 0; z-index: 50;
  background: color-mix(in srgb, var(--bg) 88%, transparent);
  backdrop-filter: saturate(1.6) blur(12px);
  border-bottom: 1px solid transparent;
  transition: border-color .2s ease, box-shadow .2s ease;
}}
.site-head.is-stuck {{ border-bottom-color: var(--line); box-shadow: 0 6px 24px -20px rgba(0,0,0,.5); }}
.site-head__inner {{ display: flex; align-items: center; gap: 1.25rem; padding-block: .85rem; }}
.brand {{ display: inline-flex; align-items: center; gap: .65rem; text-decoration: none; font-family: var(--font-display); font-weight: 700; letter-spacing: -.02em; font-size: 1.12rem; }}
.brand svg {{ flex: none; }}
.brand__name {{ text-transform: var(--display-case); }}
.nav {{ display: flex; gap: .35rem; margin-left: auto; align-items: center; }}
.nav a {{
  text-decoration: none; padding: .5rem .8rem; border-radius: var(--radius-sm);
  font-weight: 550; font-size: .97rem; color: var(--muted);
  transition: color .15s ease, background .15s ease;
}}
.nav a:hover {{ color: var(--text); background: var(--surface); }}
.nav a[aria-current="page"] {{ color: var(--accent); }}
/* the .nav a rules above are more specific than .btn — put the button back */
.nav a.btn {{ color: var(--btn-ink); background: var(--btn-bg); }}
.nav a.btn:hover {{ color: var(--btn-ink); background: var(--btn-bg); }}
.nav__cta {{ margin-left: .5rem; }}
.nav-toggle {{
  display: none; margin-left: auto; background: none; border: 1.5px solid var(--line);
  border-radius: var(--radius-sm); padding: .5rem .7rem; cursor: pointer; color: var(--text);
}}

@media (max-width: 860px) {{
  .nav-toggle {{ display: inline-flex; }}
  /* the open panel is full-width, so keep the brand and the close button on top of it */
  .brand, .nav-toggle {{ position: relative; z-index: 2; }}
  .nav {{
    position: fixed; inset: 0 0 auto; top: 0; margin: 0; z-index: 1;
    flex-direction: column; align-items: stretch; gap: .25rem;
    background: var(--bg); padding: 5.5rem 1.5rem 2rem;
    border-bottom: 1px solid var(--line);
    transform: translateY(-100%); transition: transform .28s cubic-bezier(.4,0,.2,1);
    box-shadow: var(--shadow-lg);
  }}
  .nav.is-open {{ transform: translateY(0); }}
  .nav a {{ padding: .85rem .5rem; font-size: 1.1rem; border-bottom: 1px solid var(--line); border-radius: 0; }}
  .nav__cta {{ margin: 1rem 0 0; }}
}}

/* --- cards & grids --- */
.grid {{ display: grid; gap: var(--gap); }}
.grid--2 {{ grid-template-columns: repeat(auto-fit, minmax(min(100%, 20rem), 1fr)); }}
.grid--3 {{ grid-template-columns: repeat(auto-fit, minmax(min(100%, 17rem), 1fr)); }}
.card {{
  background: var(--surface); border: 1px solid var(--line);
  border-radius: var(--radius); padding: clamp(1.4rem, 3vw, 2rem);
  transition: transform .22s ease, box-shadow .22s ease, border-color .22s ease;
}}
.card--lift:hover {{ transform: translateY(-4px); box-shadow: var(--shadow-lg); border-color: color-mix(in srgb, var(--accent) 35%, var(--line)); }}
.card h3 {{ margin-bottom: .45rem; }}
.card p {{ color: var(--muted); font-size: .98rem; }}
.icon-badge {{
  width: 3rem; height: 3rem; border-radius: var(--radius-sm);
  display: grid; place-items: center; margin-bottom: 1.1rem;
  background: color-mix(in srgb, var(--accent) 12%, transparent); color: var(--accent);
}}

.svc-price {{
  display: inline-block; font-family: var(--font-display); font-weight: 650;
  color: var(--accent); font-size: .98rem; letter-spacing: -.01em;
  margin: 0 0 .5rem;
}}
.card .svc-price {{ margin-top: -.15rem; }}
/* a description the owner has not written yet — reads as a to-do, not as copy */
.svc-todo {{
  color: var(--muted); font-size: .9rem; font-style: italic;
  border-bottom: 1px dashed color-mix(in srgb, var(--accent) 45%, transparent);
  display: inline-block; padding-bottom: .12rem; opacity: .8;
}}

.ticks {{ list-style: none; margin: 1.6rem 0 0; padding: 0; display: grid; gap: .7rem; }}
.ticks li {{ display: flex; gap: .7rem; align-items: flex-start; }}
.ticks svg {{ flex: none; color: var(--accent); margin-top: .2rem; }}

.stat-band {{ background: var(--surface-2); }}
.stats {{ display: grid; gap: var(--gap); grid-template-columns: repeat(auto-fit, minmax(min(100%, 13rem), 1fr)); text-align: center; }}
.stat__n {{ font-family: var(--font-display); font-size: clamp(2rem, 1.4rem + 2.2vw, 3rem); font-weight: var(--display-weight); color: var(--accent); line-height: 1; }}
.stat__l {{ color: var(--muted); font-size: .95rem; margin-top: .4rem; }}

.steps {{ counter-reset: step; display: grid; gap: var(--gap); grid-template-columns: repeat(auto-fit, minmax(min(100%, 16rem), 1fr)); }}
.step {{ position: relative; padding-top: 3.4rem; }}
.step::before {{
  counter-increment: step; content: counter(step, decimal-leading-zero);
  position: absolute; top: 0; left: 0;
  font-family: var(--font-display); font-size: 2.1rem; font-weight: var(--display-weight);
  color: color-mix(in srgb, var(--accent) 32%, transparent); line-height: 1;
}}

.quote {{ border-left: 3px solid var(--accent); padding-left: 1.5rem; }}
.quote p {{ font-family: var(--font-display); font-size: clamp(1.2rem, 1rem + 1vw, 1.6rem); line-height: 1.35; font-weight: 500; letter-spacing: -.01em; text-transform: none; }}
.quote cite {{ display: block; font-style: normal; color: var(--muted); font-size: .92rem; margin-top: .9rem; }}
.placeholder-note {{
  display: inline-block; font-size: .72rem; letter-spacing: .1em; text-transform: uppercase;
  font-weight: 700; color: var(--accent); background: color-mix(in srgb, var(--accent) 12%, transparent);
  padding: .2rem .5rem; border-radius: 3px; margin-bottom: .8rem;
}}

.faq {{ display: grid; gap: .6rem; max-width: 46rem; }}
.faq details {{ border: 1px solid var(--line); border-radius: var(--radius-sm); background: var(--surface); }}
.faq summary {{
  cursor: pointer; padding: 1.05rem 1.3rem; font-family: var(--font-display);
  font-weight: 650; font-size: 1.03rem; list-style: none;
  display: flex; justify-content: space-between; gap: 1rem; align-items: center;
}}
.faq summary::-webkit-details-marker {{ display: none; }}
.faq summary::after {{ content: "+"; color: var(--accent); font-size: 1.4rem; line-height: 1; flex: none; }}
.faq details[open] summary::after {{ content: "–"; }}
.faq details > p {{ padding: 0 1.3rem 1.2rem; color: var(--muted); margin: 0; }}

/* --- contact --- */
.contact-grid {{ display: grid; gap: clamp(2rem, 5vw, 4rem); grid-template-columns: repeat(auto-fit, minmax(min(100%, 20rem), 1fr)); align-items: start; }}
.contact-list {{ list-style: none; margin: 0; padding: 0; display: grid; gap: 1.1rem; }}
.contact-list li {{ display: flex; gap: .9rem; align-items: flex-start; }}
.contact-list svg {{ flex: none; color: var(--accent); margin-top: .25rem; }}
.contact-list a {{ text-decoration: none; border-bottom: 1px solid var(--line); }}
.contact-list a:hover {{ border-color: var(--accent); color: var(--accent); }}
form.enquiry {{ display: grid; gap: 1rem; }}
.field {{ display: grid; gap: .4rem; }}
.field label {{ font-size: .88rem; font-weight: 600; color: var(--muted); }}
.field input, .field textarea, .field select {{
  font: inherit; font-size: 1rem; color: var(--text); background: var(--bg);
  border: 1.5px solid var(--line); border-radius: var(--radius-sm); padding: .8rem .9rem;
  width: 100%; transition: border-color .15s ease;
}}
.field input:focus, .field textarea:focus {{ border-color: var(--accent); }}
.field textarea {{ min-height: 8rem; resize: vertical; }}

/* --- cta band ---
   Dark themes set hero-bg equal to the page background, so the band would vanish;
   step up to surface-2 there instead of painting dark on dark. */
.cta-band {{ background: {'var(--surface-2)' if t['dark'] else 'var(--hero-bg)'};
             color: var(--hero-ink); position: relative; overflow: hidden; }}
.cta-band::before {{ content: ""; position: absolute; inset: 0; background-image: {data_uri(pattern_svg(t, ink=t['hero_ink'], opacity=0.12))}; }}
.cta-band .wrap {{ position: relative; }}
.cta-band h2 {{ margin-bottom: .5rem; }}
.cta-band p {{ color: color-mix(in srgb, var(--hero-ink) 75%, transparent); }}

/* --- footer --- */
.site-foot {{ border-top: 1px solid var(--line); padding-block: 3rem 2rem; background: var(--surface); }}
.foot-grid {{ display: grid; gap: 2rem; grid-template-columns: repeat(auto-fit, minmax(min(100%, 14rem), 1fr)); }}
.foot-grid h4 {{ font-size: .8rem; letter-spacing: .14em; text-transform: uppercase; color: var(--muted); margin-bottom: .9rem; }}
.foot-grid ul {{ list-style: none; margin: 0; padding: 0; display: grid; gap: .5rem; font-size: .95rem; }}
.foot-grid a {{ text-decoration: none; color: var(--muted); }}
.foot-grid a:hover {{ color: var(--accent); }}
.colophon {{ margin-top: 2.5rem; padding-top: 1.5rem; border-top: 1px solid var(--line); display: flex; flex-wrap: wrap; gap: .75rem 1.5rem; justify-content: space-between; font-size: .87rem; color: var(--muted); }}

/* --- reveal --- */
.reveal {{ opacity: 0; transform: translateY(18px); transition: opacity .6s ease, transform .6s cubic-bezier(.2,.7,.3,1); }}
.reveal.is-in {{ opacity: 1; transform: none; }}
@media (prefers-reduced-motion: reduce) {{
  html {{ scroll-behavior: auto; }}
  *, *::before, *::after {{ animation-duration: .01ms !important; transition-duration: .01ms !important; }}
  .reveal {{ opacity: 1; transform: none; }}
}}

@media print {{
  .site-head, .nav, .cta-band, .site-foot, .btn {{ display: none !important; }}
  body {{ color: #000; background: #fff; }}
}}
"""


def layout_css(name, t):
    """Structure that makes each layout genuinely different, not just re-skinned."""
    common_hero_art = f"""
.hero-art {{ position: relative; border-radius: var(--radius); overflow: hidden; box-shadow: var(--shadow-lg); }}
.hero-art svg {{ width: 100%; height: 100%; object-fit: cover; }}
"""
    if name == "classic":
        return common_hero_art + f"""
.hero {{ padding-block: clamp(3rem, 7vw, 5.5rem); background: var(--surface); border-bottom: 1px solid var(--line); }}
.hero__grid {{ display: grid; gap: clamp(2rem, 5vw, 3.5rem); grid-template-columns: 1fr; align-items: center; }}
@media (min-width: 900px) {{ .hero__grid {{ grid-template-columns: 1.05fr .95fr; }} }}
.hero-art {{ aspect-ratio: 4 / 3; }}
.hero__badges {{ display: flex; flex-wrap: wrap; gap: .5rem; margin-top: 1.75rem; }}
.badge {{ font-size: .85rem; color: var(--muted); background: var(--bg); border: 1px solid var(--line); padding: .35rem .75rem; border-radius: var(--pill); }}
.site-head__inner {{ padding-block: 1rem; }}
"""
    if name == "bold":
        return common_hero_art + f"""
.hero {{
  min-height: min(88vh, 780px); display: grid; align-items: center;
  background: var(--hero-bg); color: var(--hero-ink); position: relative; overflow: hidden;
  padding-block: clamp(4rem, 10vw, 7rem);
}}
.hero::before {{ content: ""; position: absolute; inset: -20%; background-image: {data_uri(pattern_svg(t, ink=t['hero_ink'], opacity=0.14))}; }}
.hero::after {{
  content: ""; position: absolute; right: -12%; top: -18%; width: min(62vw, 700px); aspect-ratio: 1;
  background: radial-gradient(circle at 35% 35%, var(--accent), transparent 62%);
  opacity: .55; filter: blur(8px);
}}
.hero .wrap {{ position: relative; z-index: 1; }}
.hero h1 {{ font-size: clamp(2.9rem, 1.2rem + 8vw, 6.2rem); max-width: 16ch; }}
.hero .lede {{ color: color-mix(in srgb, var(--hero-ink) 78%, transparent); font-size: clamp(1.15rem, 1rem + 0.7vw, 1.45rem); }}
.hero .eyebrow {{ color: var(--accent-2); }}
.hero .eyebrow::after {{ background: color-mix(in srgb, var(--hero-ink) 30%, transparent); }}
.rows {{ display: grid; }}
.row-item {{
  display: grid; gap: 1rem 2.5rem; grid-template-columns: 1fr; align-items: baseline;
  padding-block: clamp(1.6rem, 3.5vw, 2.4rem); border-top: 1px solid var(--line);
  transition: background .2s ease, padding-inline .2s ease;
}}
@media (min-width: 820px) {{ .row-item {{ grid-template-columns: 5rem 1fr 1.1fr; }} }}
.row-item:last-child {{ border-bottom: 1px solid var(--line); }}
.row-item:hover {{ background: var(--surface); padding-inline: 1rem; }}
.row-item__n {{ font-family: var(--font-display); font-size: 1.05rem; color: var(--accent); font-weight: 700; letter-spacing: .1em; }}
.row-item h3 {{ font-size: clamp(1.3rem, 1.05rem + 1.1vw, 1.9rem); margin: 0; }}
.row-item p {{ color: var(--muted); margin: 0; }}
.row-item .svc-price {{ margin: .3rem 0 0; }}
.site-head {{ background: color-mix(in srgb, var(--bg) 92%, transparent); }}
"""
    if name == "split":
        return common_hero_art + f"""
@media (min-width: 1000px) {{
  body {{ padding-left: 19rem; }}
  .site-head {{
    position: fixed; inset: 0 auto 0 0; width: 19rem; z-index: 60;
    background: var(--surface); border-right: 1px solid var(--line); border-bottom: none;
    backdrop-filter: none; display: flex; overflow-y: auto;
  }}
  .site-head__inner {{
    flex-direction: column; align-items: stretch; gap: 2rem;
    padding: 2.4rem 1.9rem; width: 100%;
  }}
  .nav {{ flex-direction: column; align-items: stretch; margin-left: 0; gap: .1rem; }}
  .nav a {{ padding: .55rem .7rem; font-size: 1.02rem; }}
  .nav a[aria-current="page"] {{ background: var(--bg); }}
  .nav__cta {{ margin: 1.2rem 0 0; }}
  .side-meta {{ margin-top: auto; padding-top: 2rem; border-top: 1px solid var(--line); font-size: .89rem; color: var(--muted); display: grid; gap: .6rem; }}
  .side-meta a {{ text-decoration: none; }}
  .side-meta a:hover {{ color: var(--accent); }}
  .wrap {{ width: min(100% - 3.5rem, 60rem); margin-inline: 0 auto; }}
  .colophon {{ justify-content: flex-start; }}
}}
@media (max-width: 999px) {{ .side-meta {{ display: none; }} }}
.hero {{ padding-block: clamp(3rem, 8vw, 6rem) clamp(2rem, 5vw, 3.5rem); }}
.hero h1 {{ font-size: clamp(2.3rem, 1.4rem + 3.6vw, 3.9rem); }}
.hero-art {{ aspect-ratio: 21 / 9; margin-top: 2.8rem; }}
.section {{ padding-block: clamp(2.75rem, 6vw, 4.75rem); }}
.section + .section {{ border-top: 1px solid var(--line); }}
.section--tint {{ background: transparent; }}
"""
    if name == "minimal":
        return f"""
:root {{ --maxw: 46rem; --section-y: clamp(3rem, 7vw, 5.5rem); }}
body {{ font-size: clamp(1.02rem, 0.98rem + 0.25vw, 1.12rem); line-height: 1.75; }}
.site-head {{ background: var(--bg); backdrop-filter: none; }}
.site-head__inner {{ padding-block: 1.6rem; }}
.hero {{ padding-block: clamp(4.5rem, 12vw, 9rem) clamp(3rem, 7vw, 5rem); text-align: center; }}
.hero h1 {{ font-size: clamp(2.4rem, 1.4rem + 4vw, 4rem); max-width: 18ch; margin-inline: auto; }}
.hero .lede {{ margin-inline: auto; }}
.hero .btn-row {{ justify-content: center; }}
.rule {{ height: 1px; background: var(--line); border: 0; margin: 0; }}
.section {{ border-top: 1px solid var(--line); }}
.section--tint {{ background: transparent; }}
.label {{
  font-family: var(--font-display); font-size: .74rem; letter-spacing: .22em;
  text-transform: uppercase; color: var(--muted); margin-bottom: 1.8rem; display: block;
}}
.list-plain {{ list-style: none; margin: 0; padding: 0; }}
.list-plain li {{ padding-block: 1.35rem; border-bottom: 1px solid var(--line); }}
.list-plain li:first-child {{ border-top: 1px solid var(--line); }}
.list-plain h3 {{ margin: 0 0 .3rem; font-size: 1.12rem; }}
.list-plain p {{ margin: 0; color: var(--muted); font-size: .98rem; }}
.list-plain .row-head {{ display: flex; gap: 1rem; align-items: baseline;
                         justify-content: space-between; }}
.list-plain .row-head h3 {{ margin: 0 0 .3rem; }}
.list-plain .svc-price {{ margin: 0; white-space: nowrap; }}
.card {{ background: transparent; border: 0; padding: 0; }}
.icon-badge {{ background: transparent; width: auto; height: auto; margin-bottom: .8rem; }}
.grid {{ gap: clamp(1.8rem, 4vw, 2.6rem); }}
.quote {{ border: 0; padding: 0; text-align: center; }}
.quote p {{ font-size: clamp(1.3rem, 1.05rem + 1.2vw, 1.85rem); }}
.cta-band {{ background: var(--bg); color: var(--text); border-top: 1px solid var(--line); }}
.cta-band::before {{ display: none; }}
.cta-band p {{ color: var(--muted); }}
.site-foot {{ background: transparent; }}
"""
    if name == "landing":
        return common_hero_art + f"""
.hero {{ padding-block: clamp(3.5rem, 8vw, 6rem); background: var(--surface); position: relative; overflow: hidden; }}
.hero::before {{ content: ""; position: absolute; inset: 0; background-image: {data_uri(pattern_svg(t, opacity=0.07))}; }}
.hero .wrap {{ position: relative; }}
.hero__grid {{ display: grid; gap: clamp(2rem, 5vw, 3.5rem); align-items: center; }}
@media (min-width: 940px) {{ .hero__grid {{ grid-template-columns: 1.1fr .9fr; }} }}
.hero-art {{ aspect-ratio: 5 / 4; }}
.trust-row {{ display: flex; flex-wrap: wrap; gap: .6rem 1.6rem; margin-top: 2rem; font-size: .92rem; color: var(--muted); }}
.trust-row span {{ display: inline-flex; align-items: center; gap: .45rem; }}
.trust-row svg {{ color: var(--accent); }}
.pkg {{ display: grid; gap: var(--gap); grid-template-columns: repeat(auto-fit, minmax(min(100%, 17rem), 1fr)); align-items: stretch; }}
.pkg .card {{ display: flex; flex-direction: column; }}
.pkg .card ul {{ list-style: none; margin: 1.2rem 0 1.6rem; padding: 0; display: grid; gap: .6rem; font-size: .96rem; color: var(--muted); }}
.pkg .card ul li {{ display: flex; gap: .55rem; }}
.pkg .card ul svg {{ flex: none; color: var(--accent); margin-top: .25rem; }}
.pkg .card .btn {{ margin-top: auto; }}
.pkg__featured {{ border-color: var(--accent); box-shadow: var(--shadow-lg); position: relative; }}
.pkg__tag {{ position: absolute; top: -.75rem; left: 50%; transform: translateX(-50%); background: var(--accent); color: var(--on-accent); font-size: .72rem; font-weight: 700; letter-spacing: .1em; text-transform: uppercase; padding: .3rem .8rem; border-radius: var(--pill); white-space: nowrap; }}
.price {{ font-family: var(--font-display); font-size: 2.1rem; font-weight: var(--display-weight); line-height: 1; margin: .4rem 0 .2rem; }}
.callbar {{ display: none; }}
@media (max-width: 720px) {{
  .callbar {{
    display: flex; position: fixed; inset: auto 0 0; z-index: 70; gap: .6rem;
    padding: .7rem .9rem calc(.7rem + env(safe-area-inset-bottom));
    background: color-mix(in srgb, var(--bg) 94%, transparent);
    backdrop-filter: blur(12px); border-top: 1px solid var(--line);
  }}
  .callbar .btn {{ flex: 1; padding-inline: .8rem; }}
  body {{ padding-bottom: 4.5rem; }}
}}
"""
    if name == "magazine":
        return common_hero_art + f"""
:root {{ --maxw: 1080px; }}
.site-head {{ background: var(--bg); backdrop-filter: none; border-bottom: 3px double var(--line); }}
.site-head__inner {{ flex-direction: column; gap: .9rem; padding-block: 1.5rem 1rem; }}
.site-head .brand {{ font-size: clamp(1.3rem, 1rem + 1.4vw, 1.9rem); }}
.nav {{ margin-left: 0; border-top: 1px solid var(--line); padding-top: .7rem; width: 100%;
        justify-content: center; }}
.nav a {{ font-size: .82rem; letter-spacing: .13em; text-transform: uppercase; font-weight: 600; }}
@media (min-width: 861px) {{ .nav__cta {{ display: none; }} }}
.hero {{ padding-block: clamp(2.5rem, 6vw, 4rem); border-bottom: 1px solid var(--line); }}
.hero__grid {{ display: grid; gap: clamp(1.5rem, 4vw, 3rem); }}
@media (min-width: 900px) {{
  .hero__grid {{ grid-template-columns: 1.5fr 1fr; }}
  .hero__grid > :last-child {{ border-left: 1px solid var(--line); padding-left: clamp(1.5rem, 3vw, 2.5rem); }}
}}
.hero h1 {{ font-size: clamp(2.4rem, 1.2rem + 5vw, 4.6rem); }}
.hero-art {{ aspect-ratio: 21 / 9; margin-top: 2rem; border-radius: 0; box-shadow: none;
             border: 1px solid var(--line); }}
.dropcap::first-letter {{
  float: left; font-family: var(--font-display); font-size: 3.6em; line-height: .78;
  padding: .06em .1em 0 0; font-weight: var(--display-weight); color: var(--accent);
}}
.cols {{ column-count: 1; column-gap: clamp(2rem, 4vw, 3.5rem); column-rule: 1px solid var(--line); }}
@media (min-width: 760px) {{ .cols {{ column-count: 2; }} }}
.cols > article {{ break-inside: avoid; padding-bottom: 1.6rem; margin-bottom: 1.6rem;
                   border-bottom: 1px solid var(--line); }}
.cols > article:last-child {{ border-bottom: 0; }}
.cols h3 {{ margin-bottom: .3rem; font-size: 1.1rem; }}
.cols p {{ margin: 0; color: var(--muted); font-size: .96rem; }}
.section {{ border-top: 1px solid var(--line); }}
.section--tint {{ background: transparent; }}
.card {{ background: transparent; border: 0; padding: 0; }}
.icon-badge {{ background: transparent; width: auto; height: auto; margin-bottom: .6rem; }}
.quote {{ border-left: 0; border-top: 3px double var(--line); border-bottom: 3px double var(--line);
          padding: 1.8rem 0; text-align: center; }}
.quote p {{ font-size: clamp(1.3rem, 1rem + 1.4vw, 2rem); font-style: italic; }}
.eyebrow {{ justify-content: center; }}
.eyebrow::after {{ display: none; }}
.cta-band {{ background: var(--bg); color: var(--text); border-top: 3px double var(--line); }}
.cta-band::before {{ display: none; }}
.cta-band p {{ color: var(--muted); }}
"""

    if name == "panel":
        return common_hero_art + f"""
body {{ background: var(--surface-2); }}
.site-head {{
  position: sticky; top: .85rem; z-index: 60; background: transparent;
  backdrop-filter: none; border: 0; margin-bottom: 1.25rem;
}}
.site-head.is-stuck {{ box-shadow: none; }}
.site-head__inner {{
  background: color-mix(in srgb, var(--bg) 90%, transparent);
  backdrop-filter: saturate(1.6) blur(14px);
  border: 1px solid var(--line); border-radius: var(--pill, 999px);
  border-radius: 999px; padding: .6rem .7rem .6rem 1.2rem; box-shadow: var(--shadow);
}}
.panel {{
  background: var(--bg); border: 1px solid var(--line); border-radius: clamp(16px, 2vw, 28px);
  padding: clamp(1.6rem, 4vw, 3.5rem); box-shadow: var(--shadow);
}}
.section {{ padding-block: 0 1.25rem; }}
.section--tint {{ background: transparent; }}
.section:last-of-type {{ padding-bottom: 2.5rem; }}
.hero {{ padding-block: 0 1.25rem; }}
.hero .panel {{ overflow: hidden; }}
.hero__grid {{ display: grid; gap: clamp(2rem, 4vw, 3rem); align-items: center; }}
@media (min-width: 920px) {{ .hero__grid {{ grid-template-columns: 1.05fr .95fr; }} }}
.hero-art {{ aspect-ratio: 4 / 3; border-radius: clamp(10px, 1.4vw, 18px); }}
.card {{ background: var(--surface); border-radius: clamp(12px, 1.6vw, 20px); }}
.stat-band {{ background: transparent; }}
.stat-band .panel {{ background: var(--surface); }}
.cta-band {{ border-radius: clamp(16px, 2vw, 28px); margin-bottom: 1.25rem; }}
.cta-band .wrap {{ padding-block: clamp(2.5rem, 6vw, 4rem); }}
.site-foot {{ background: transparent; border-top: 0; }}
@media (max-width: 860px) {{ .site-head {{ top: 0; margin-bottom: .75rem; }} }}
"""

    if name == "directory":
        return common_hero_art + f"""
.hero {{ padding-block: clamp(2.5rem, 6vw, 4rem); background: var(--surface); }}
.hero__grid {{ display: grid; gap: clamp(1.5rem, 4vw, 3rem); align-items: end; }}
@media (min-width: 900px) {{ .hero__grid {{ grid-template-columns: 1.4fr 1fr; }} }}
.hero h1 {{ font-size: clamp(2.1rem, 1.3rem + 3.4vw, 3.6rem); }}
.factbox {{ background: var(--bg); border: 1px solid var(--line); border-radius: var(--radius);
            padding: 1.4rem 1.5rem; display: grid; gap: .8rem; }}
.factbox dl {{ margin: 0; display: grid; grid-template-columns: auto 1fr; gap: .55rem 1rem; font-size: .95rem; }}
.factbox dt {{ color: var(--muted); }}
.factbox dd {{ margin: 0; font-weight: 600; text-align: right; }}
.factbox .btn {{ width: 100%; }}
.subnav {{
  position: sticky; top: 0; z-index: 40; background: color-mix(in srgb, var(--bg) 92%, transparent);
  backdrop-filter: blur(10px); border-block: 1px solid var(--line); overflow-x: auto;
}}
.subnav ul {{ list-style: none; margin: 0 auto; padding: 0; display: flex; gap: .25rem;
              width: min(100% - 2.5rem, var(--maxw)); }}
.subnav a {{ display: block; padding: .85rem .9rem; text-decoration: none; color: var(--muted);
             font-size: .9rem; font-weight: 600; white-space: nowrap; border-bottom: 2px solid transparent; }}
.subnav a:hover {{ color: var(--accent); border-bottom-color: var(--accent); }}
.listing {{ list-style: none; margin: 0; padding: 0; }}
.listing li {{ display: grid; grid-template-columns: 1fr auto; align-items: baseline;
               gap: .3rem .8rem; padding-block: 1.05rem; border-bottom: 1px dotted var(--line); }}
.listing li:first-child {{ border-top: 1px solid var(--line); }}
.listing h3 {{ margin: 0; font-size: 1.06rem; }}
.listing .leader {{ display: none; }}
.listing .price {{ font-family: var(--font-display); font-weight: 650; color: var(--accent);
                   white-space: nowrap; font-size: 1rem; }}
.listing p {{ grid-column: 1 / -1; margin: .25rem 0 0; color: var(--muted); font-size: .93rem; max-width: 62ch; }}
.hours {{ width: 100%; border-collapse: collapse; font-size: .96rem; }}
.hours th {{ text-align: left; font-weight: 600; padding: .6rem 0; border-bottom: 1px solid var(--line); }}
.hours td {{ text-align: right; color: var(--muted); padding: .6rem 0; border-bottom: 1px solid var(--line); }}
.section {{ padding-block: clamp(2.5rem, 5.5vw, 4rem); scroll-margin-top: 4rem; }}
.bigcall {{ font-family: var(--font-display); font-size: clamp(1.8rem, 1.2rem + 2.6vw, 3rem);
            font-weight: var(--display-weight); letter-spacing: -.03em; text-decoration: none;
            color: var(--accent); display: inline-block; }}
.bigcall:hover {{ text-decoration: underline; }}
"""

    if name == "poster":
        return common_hero_art + f"""
.site-head {{ position: absolute; inset: 0 0 auto; background: transparent; backdrop-filter: none;
              border: 0; }}
.site-head.is-stuck {{ box-shadow: none; border-color: transparent; }}
.hero {{
  min-height: min(100vh, 860px); display: grid; align-items: center; position: relative;
  background: var(--hero-bg); color: var(--hero-ink); overflow: hidden;
  padding-block: clamp(6rem, 14vw, 9rem) clamp(3rem, 8vw, 5rem);
}}
.hero::before {{ content: ""; position: absolute; inset: 0;
  background-image: {data_uri(pattern_svg(t, ink=t['hero_ink'], opacity=0.16))}; }}
.hero::after {{ content: ""; position: absolute; left: -10%; bottom: -30%; width: min(70vw, 760px);
  aspect-ratio: 1; background: radial-gradient(circle at 50% 50%, var(--accent), transparent 60%);
  opacity: .5; }}
.hero .wrap {{ position: relative; z-index: 1; }}
.hero h1 {{ font-size: clamp(3rem, 1rem + 11vw, 8.5rem); line-height: .93; max-width: 13ch;
            margin-bottom: .35em; }}
.hero .lede {{ color: color-mix(in srgb, var(--hero-ink) 80%, transparent);
               font-size: clamp(1.1rem, 1rem + 0.7vw, 1.45rem); }}
.hero .eyebrow {{ color: var(--hero-ink); opacity: .75; }}
.hero .eyebrow::after {{ background: currentColor; }}
.site-head .brand {{ color: var(--hero-ink); }}
.site-head .nav a {{ color: color-mix(in srgb, var(--hero-ink) 80%, transparent); }}
.site-head .nav a:hover, .site-head .nav a[aria-current="page"] {{ color: var(--hero-ink); background: transparent; }}
.nav-toggle {{ color: var(--hero-ink); border-color: color-mix(in srgb, var(--hero-ink) 45%, transparent); }}
@media (max-width: 860px) {{
  .site-head .nav a {{ color: var(--text); }}
  .site-head .nav a[aria-current="page"] {{ color: var(--accent); }}
}}
.band {{ padding-block: clamp(3.5rem, 8vw, 6rem); }}
.band--accent {{ background: var(--accent); color: var(--on-accent); }}
.band--accent .eyebrow, .band--accent .stat__n {{ color: var(--on-accent); opacity: .8; }}
.band--accent .eyebrow::after {{ background: currentColor; }}
.band--accent p, .band--accent .lede, .band--accent .stat__l {{ color: color-mix(in srgb, var(--on-accent) 82%, transparent); }}
.band--accent .row-item {{ border-color: color-mix(in srgb, var(--on-accent) 28%, transparent); }}
.band--accent .row-item:hover {{ background: color-mix(in srgb, var(--on-accent) 10%, transparent); }}
.band--accent .row-item__n {{ color: var(--on-accent); opacity: .7; }}
.band--dark {{ background: {'var(--surface-2)' if t['dark'] else 'var(--hero-bg)'};
               color: var(--hero-ink); }}
.band--dark p, .band--dark .lede {{ color: color-mix(in srgb, var(--hero-ink) 78%, transparent); }}
.band--dark .quote {{ border-color: var(--accent-2); }}
.rows {{ display: grid; }}
.row-item {{ display: grid; gap: .6rem 2.5rem; grid-template-columns: 1fr;
             padding-block: clamp(1.4rem, 3vw, 2rem); border-top: 1px solid var(--line);
             align-items: baseline; transition: background .2s ease, padding-inline .2s ease; }}
@media (min-width: 820px) {{ .row-item {{ grid-template-columns: 4.5rem 1fr 1.1fr; }} }}
.row-item:last-child {{ border-bottom: 1px solid var(--line); }}
.row-item:hover {{ background: var(--surface); padding-inline: 1rem; }}
.row-item__n {{ font-family: var(--font-display); font-weight: 700; color: var(--accent);
                letter-spacing: .1em; font-size: 1rem; }}
.row-item h3 {{ margin: 0; font-size: clamp(1.25rem, 1rem + 1.1vw, 1.9rem); }}
.row-item p {{ margin: 0; }}
.row-item .svc-price {{ margin: .3rem 0 0; }}
.section--tint {{ background: var(--surface); }}
"""

    # showcase
    return common_hero_art + f"""
.hero {{ padding-block: clamp(3rem, 7vw, 5rem) 0; }}
.hero h1 {{ font-size: clamp(2.5rem, 1.3rem + 5.4vw, 4.8rem); max-width: 15ch; }}
.collage {{ display: grid; grid-template-columns: repeat(6, 1fr); gap: .8rem; margin-top: clamp(2.5rem, 6vw, 4rem); }}
.collage > * {{ border-radius: var(--radius); overflow: hidden; box-shadow: var(--shadow); }}
.collage > :nth-child(1) {{ grid-column: span 6; aspect-ratio: 16/9; }}
.collage > :nth-child(2) {{ grid-column: span 3; aspect-ratio: 4/3; }}
.collage > :nth-child(3) {{ grid-column: span 3; aspect-ratio: 4/3; }}
@media (min-width: 820px) {{
  .collage {{ gap: 1.1rem; }}
  .collage > :nth-child(1) {{ grid-column: span 4; aspect-ratio: 4/3; }}
  .collage > :nth-child(2) {{ grid-column: span 2; aspect-ratio: 3/4; }}
  .collage > :nth-child(3) {{ grid-column: span 6; aspect-ratio: 21/6; }}
}}
.tiles {{ display: grid; gap: 1.1rem; grid-template-columns: repeat(auto-fit, minmax(min(100%, 18rem), 1fr)); }}
.tile {{
  position: relative; overflow: hidden; border-radius: var(--radius);
  min-height: 17rem; display: flex; align-items: flex-end;
  padding: 1.5rem; color: #fff; isolation: isolate; text-decoration: none;
}}
.tile__art {{ position: absolute; inset: 0; z-index: -2; }}
.tile__art svg {{ width: 100%; height: 100%; }}
.tile::after {{
  content: ""; position: absolute; inset: 0; z-index: -1;
  background: linear-gradient(to top, rgba(0,0,0,.82) 0%, rgba(0,0,0,.35) 45%, rgba(0,0,0,.05) 100%);
  transition: opacity .25s ease;
}}
.tile:hover::after {{ opacity: .82; }}
.tile__body h3 {{ margin: 0 0 .3rem; color: #fff; }}
.tile__body p {{ margin: 0; font-size: .95rem; color: rgba(255,255,255,.86); }}
.tile .svc-price {{ color: #fff; margin: 0 0 .35rem; }}
.tile__art svg {{ transition: transform .5s cubic-bezier(.2,.7,.3,1); }}
.tile:hover .tile__art svg {{ transform: scale(1.06); }}
.strip {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(min(100%, 11rem), 1fr)); gap: .8rem; }}
.strip > * {{ border-radius: var(--radius-sm); overflow: hidden; aspect-ratio: 1; }}
"""


def site_js():
    return """(function () {
  var head = document.querySelector('.site-head');
  var toggle = document.querySelector('.nav-toggle');
  var nav = document.getElementById('nav');

  if (toggle && nav) {
    toggle.addEventListener('click', function () {
      var open = nav.classList.toggle('is-open');
      toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
    nav.addEventListener('click', function (e) {
      if (e.target.tagName === 'A') {
        nav.classList.remove('is-open');
        toggle.setAttribute('aria-expanded', 'false');
      }
    });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape') {
        nav.classList.remove('is-open');
        toggle.setAttribute('aria-expanded', 'false');
      }
    });
  }

  if (head) {
    var onScroll = function () {
      head.classList.toggle('is-stuck', window.scrollY > 8);
    };
    onScroll();
    window.addEventListener('scroll', onScroll, { passive: true });
  }

  var targets = document.querySelectorAll('.reveal');
  if (!('IntersectionObserver' in window) ||
      window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
    targets.forEach(function (el) { el.classList.add('is-in'); });
  } else {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add('is-in');
          io.unobserve(entry.target);
        }
      });
    }, { rootMargin: '0px 0px -8% 0px', threshold: 0.08 });
    targets.forEach(function (el, i) {
      el.style.transitionDelay = Math.min(i % 4, 3) * 70 + 'ms';
      io.observe(el);
    });
  }

  // The form posts to Netlify Forms once deployed. Opened from disk or a local
  // preview server there is nothing to post to, so say so instead of failing.
  var form = document.querySelector('form.enquiry');
  if (form) {
    var isPreview = location.protocol === 'file:' ||
      /^(localhost|127\\.0\\.0\\.1|\\[::1\\])$/.test(location.hostname);
    form.addEventListener('submit', function (e) {
      if (isPreview) {
        e.preventDefault();
        var note = form.querySelector('.form-note');
        if (note) { note.hidden = false; note.setAttribute('tabindex', '-1'); note.focus(); }
      }
    });
  }
})();
"""
