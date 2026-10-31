"""Builds the whole website into the _site folder. Run: python scripts/build.py"""
import datetime as dt
import email.utils
import html
import json
import pathlib
import re
import shutil
import urllib.parse

import markdown

from covers import make_cover

from common import PAGES_DIR, POSTS_DIR, ROOT, load_site, parse_front_matter

OUT = ROOT / "_site"
SITE = load_site()
BASE_URL = SITE["url"].rstrip("/")
if SITE.get("custom_domain"):
    BASE_URL = "https://" + SITE["custom_domain"].strip().strip("/")
BP = urllib.parse.urlparse(BASE_URL).path.rstrip("/")  # e.g. "/secbrief" on github.io
CATS = SITE.get("categories", {})
KIND = {"news": "News", "weekly-recap": "Recap", "theory": "Theory", "practical": "Practical"}
SEV_LABEL = {"critical": "Critical", "high": "High", "medium": "Medium", "low": "Low", "unscored": "Not scored"}
e = html.escape


def url(path):
    return f"{BP}{path}"


def render_md(text):
    """Markdown to HTML with raw HTML switched off, so posts can never inject scripts."""
    md = markdown.Markdown(extensions=["tables", "pymdownx.superfences", "sane_lists"])
    md.preprocessors.deregister("html_block")
    md.inlinePatterns.deregister("html")
    out = md.convert(text)
    out = re.sub(r'href="\s*(javascript|data|vbscript):[^"]*"', 'href="#"', out, flags=re.I)
    return out.replace("<table>", '<div class="table-wrap"><table>').replace("</table>", "</table></div>")


def load_posts():
    posts = []
    for path in sorted(POSTS_DIR.glob("*.md")):
        meta, body = parse_front_matter(path.read_text(encoding="utf-8"))
        if not meta.get("title") or meta.get("draft", "").lower() == "true":
            continue
        meta["slug"] = path.stem
        meta["path"] = f"/posts/{path.stem}/"
        meta["html"] = render_md(body)
        meta["minutes"] = max(1, round(len(body.split()) / 200))
        meta.setdefault("category", "news")
        meta.setdefault("severity", "")
        meta.setdefault("summary", "")
        meta["date"] = meta.get("date") or dt.date.today().isoformat()
        own = pathlib.Path(meta.get("image", "")).name  # your own photo in assets/images/
        if own and (ROOT / "assets" / "images" / own).is_file():
            meta["cover"], meta["cover_alt"], meta["own_image"] = f"/assets/images/{own}", meta.get("image_alt", ""), True
        else:
            meta["cover"], meta["cover_alt"], meta["own_image"] = f"/covers/{path.stem}.jpg", "", False
        posts.append(meta)
    posts.sort(key=lambda p: (p["date"], p["slug"]), reverse=True)
    return posts


def nice_date(iso):
    try:
        return dt.date.fromisoformat(iso[:10]).strftime("%-d %b %Y")
    except ValueError:
        return iso


ICON = {
    "news": '<path d="M4 5h13v14H6a2 2 0 0 1-2-2V5Z"/><path d="M17 9h3v8a2 2 0 0 1-2 2"/><path d="M7 9h7M7 12h7M7 15h4"/>',
    "weekly-recap": '<rect x="3.5" y="5" width="17" height="15" rx="2"/><path d="M3.5 10h17M8 3v4M16 3v4"/><path d="M8 14h2M12 14h2M16 14h.5M8 17h2M12 17h2"/>',
    "exploited-vulnerabilities": '<path d="M12 3 4.5 6v6c0 4.5 3.2 7.8 7.5 9 4.3-1.2 7.5-4.5 7.5-9V6L12 3Z"/><path d="M12 8v5M12 16h.01"/>',
    "theory": '<path d="M9 18h6M10 21h4"/><path d="M12 3a6 6 0 0 0-3.5 10.9c.6.5 1 1.2 1 2.1h5c0-.9.4-1.6 1-2.1A6 6 0 0 0 12 3Z"/>',
    "practical": '<path d="M14.5 6.5a4 4 0 0 0-5.3 5.3l-5 5a1.7 1.7 0 0 0 2.4 2.4l5-5a4 4 0 0 0 5.3-5.3l-2.5 2.5-2.4-.4-.4-2.4 2.9-2.1Z"/>',
    "share": '<circle cx="18" cy="5" r="2.5"/><circle cx="6" cy="12" r="2.5"/><circle cx="18" cy="19" r="2.5"/><path d="m8.2 10.8 7.6-4.5M8.2 13.2l7.6 4.5"/>',
    "send": '<path d="M21 3 3 10.5l7 2.5 2.5 7L21 3Z"/><path d="m10 13 4.5-4.5"/>',
    "bell": '<path d="M6 16V11a6 6 0 1 1 12 0v5l1.5 2h-15L6 16Z"/><path d="M10 20a2 2 0 0 0 4 0"/>',
    "people": '<circle cx="9" cy="8" r="3.2"/><path d="M3.5 19a5.5 5.5 0 0 1 11 0"/><circle cx="17" cy="9" r="2.4"/><path d="M15.5 14.2A4.5 4.5 0 0 1 21 18.5"/>',
    "camera": '<rect x="3" y="6.5" width="18" height="13" rx="3"/><path d="M8.5 6.5 10 4h4l1.5 2.5"/><circle cx="12" cy="13" r="3.5"/>',
    "music": '<path d="M9 18V5l11-2v13"/><circle cx="6.5" cy="18" r="2.5"/><circle cx="17.5" cy="16" r="2.5"/>',
    "play": '<rect x="2.5" y="5" width="19" height="14" rx="4"/><path d="m10 9 5 3-5 3V9Z"/>',
    "chat": '<path d="M4 19.5 5.3 16A8 8 0 1 1 8.6 19L4 19.5Z"/><path d="M9 10.5h6M9 13.5h4"/>',
    "pen": '<path d="M4 20h4L19 9l-4-4L4 16v4Z"/><path d="m13.5 6.5 4 4"/>',
    "briefcase": '<rect x="3" y="7" width="18" height="13" rx="2.5"/><path d="M9 7V5.5A1.5 1.5 0 0 1 10.5 4h3A1.5 1.5 0 0 1 15 5.5V7M3 12.5h18"/>',
    "link": '<path d="M10 14a4 4 0 0 0 5.7 0l3-3a4 4 0 0 0-5.7-5.7l-1 1"/><path d="M14 10a4 4 0 0 0-5.7 0l-3 3a4 4 0 0 0 5.7 5.7l1-1"/>',
    "thumb": '<path d="M7 11v9H4v-9h3Z"/><path d="M7 11l4-7a2 2 0 0 1 2 2.3L12.5 10H18a2 2 0 0 1 2 2.3l-1.2 6A2 2 0 0 1 16.8 20H7"/>',
}


def icon(name, size=24):
    return (f'<svg class="ico" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
            f'stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{ICON[name]}</svg>')


CHANNEL = {  # label in site.json "social" -> (icon, color tone)
    "facebook": ("people", "t-news"), "instagram": ("camera", "t-theory"), "tiktok": ("music", "t-exploit"),
    "youtube": ("play", "t-exploit"), "whatsapp": ("chat", "t-practical"), "telegram": ("send", "t-news"),
    "blog": ("pen", "t-recap"), "linkedin": ("briefcase", "t-news"),
}


def social_channels():
    """Your channels from site.json, in the order written there (only full https:// links)."""
    out = []
    for label, link in (SITE.get("social") or {}).items():
        link = str(link).strip()
        if link.startswith("https://"):
            ico, tone = CHANNEL.get(label.lower(), ("link", "t-recap"))
            out.append((label, link, ico, tone))
    return out


def social_pills(cls="follow"):
    items = "".join(f'<li><a class="chan {tone}" href="{e(link)}" rel="noopener" target="_blank">'
                    f'<span class="chan-ico">{icon(ico, 18)}</span>{e(label)}</a></li>'
                    for label, link, ico, tone in social_channels())
    return f'<ul class="{cls}">{items}</ul>' if items else ""


PILLARS = [
    ("news", "/category/news/", "Latest news", "Today’s security stories, explained in plain language."),
    ("weekly-recap", "/category/weekly-recap/", "Weekly recap", "Every Monday: news, ransomware and web defacement."),
    ("exploited-vulnerabilities", "/category/exploited-vulnerabilities/", "Exploited vulnerabilities", "What attackers are using right now, and how to patch."),
    ("theory", "/category/theory/", "Theory", "Security concepts made clear, from basics to advanced."),
    ("practical", "/category/practical/", "Practical guides", "Hands-on steps to protect real systems."),
]
TONE = {"news": "t-news", "weekly-recap": "t-recap", "exploited-vulnerabilities": "t-exploit", "theory": "t-theory", "practical": "t-practical"}


def layout(title, body, description="", path="/", og_type="website", image="/assets/og-image.jpg"):
    full_title = title if title == SITE["name"] else f"{title} | {SITE['name']}"
    desc = description or SITE["description"]
    canonical = BASE_URL + path
    def nav_link(href, label):
        here = ' aria-current="page"' if path == href else ""
        return f'<a href="{url(href)}"{here}>{e(label)}</a>'
    nav = "".join(nav_link(f"/category/{slug}/", name) for slug, name in CATS.items())
    subscribe = (f'<a class="subscribe" href="{e(SITE["newsletter_url"])}" rel="noopener">Get the email briefing</a>'
                 if SITE.get("newsletter_url") else "")
    year = dt.date.today().year
    social = "".join(f'<li><a class="foot-chan" href="{e(link)}" rel="noopener" target="_blank">{icon(ico, 16)}{e(label)}</a></li>'
                     for label, link, ico, tone in social_channels())
    return f"""<!doctype html>
<html lang="{e(SITE.get('language', 'en'))}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src https://fonts.gstatic.com; img-src 'self' data:; connect-src 'self'; object-src 'none'; base-uri 'self'; form-action 'none'; upgrade-insecure-requests">
<meta name="referrer" content="strict-origin-when-cross-origin">
<title>{e(full_title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{e(canonical)}">
<meta property="og:type" content="{og_type}">
<meta property="og:title" content="{e(full_title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{e(canonical)}">
<meta property="og:site_name" content="{e(SITE['name'])}">
<meta property="og:image" content="{BASE_URL}{image}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:image" content="{BASE_URL}{image}">
<meta name="theme-color" content="#040a1f">
<link rel="alternate" type="application/rss+xml" title="{e(SITE['name'])}" href="{url('/feed.xml')}">
<link rel="icon" href="{url('/assets/favicon-32.png')}" sizes="32x32" type="image/png">
<link rel="icon" href="{url('/assets/icon-512.png')}" sizes="512x512" type="image/png">
<link rel="apple-touch-icon" href="{url('/assets/apple-touch-icon.png')}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wdth,wght@62..125,400..800&family=Literata:opsz,wght@7..72,400;7..72,600&display=swap">
<link rel="stylesheet" href="{url('/assets/style.css')}">
<script src="{url('/assets/app.js')}"></script>
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="masthead">
  <div class="wrap masthead-row">
    <a class="brand" href="{url('/')}"><img class="logo-on-light" src="{url('/assets/logo-light.png')}" alt="{e(SITE['name'])}" width="379" height="120"><img class="logo-on-dark" src="{url('/assets/logo.png')}" alt="{e(SITE['name'])}" width="347" height="184"></a>
    <div class="tools">
      <div class="search">
        <label class="visually-hidden" for="search-input">Search briefings</label>
        <input id="search-input" type="search" placeholder="Search news, CVEs, topics" autocomplete="off" data-index="{url('/search-index.json')}">
        <ul id="search-results" hidden></ul>
      </div>
      <button id="theme-toggle" type="button" aria-label="Switch light or dark theme">
        <svg width="18" height="18" viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M12 3a9 9 0 1 0 9 9 7 7 0 0 1-9-9Z"/></svg>
      </button>
    </div>
  </div>
  <nav class="wrap catnav" aria-label="Categories">{nav_link("/posts/", "All posts")}{nav}</nav>
  <div class="color-strip" aria-hidden="true"></div>
</header>
<main id="main" class="wrap">
{body}
</main>
<footer class="footer">
  <div class="color-strip" aria-hidden="true"></div>
  <div class="wrap footer-grid">
    <div class="footer-brand">
      <img src="{url('/assets/logo.png')}" alt="{e(SITE['name'])}" width="347" height="184" loading="lazy">
      <p class="mission">{e(SITE.get('mission') or SITE['description'])}</p>
    </div>
    <nav aria-label="Sections"><h2>Explore</h2><ul>{"".join(f'<li><a href="{url("/category/" + s + "/")}">{e(n)}</a></li>' for s, n in CATS.items())}</ul></nav>
    <div><h2>Follow us</h2><ul class="foot-follow">{social}<li><a class="foot-chan" href="{url('/feed.xml')}">{icon("bell", 16)}RSS feed</a></li>{('<li>' + subscribe + '</li>') if subscribe else ''}</ul>
      <h2 class="foot-more">More</h2><ul><li><a href="{url('/about/')}">About</a></li><li><a href="{url('/privacy/')}">Privacy</a></li></ul></div>
  </div>
  <div class="wrap footer-bottom">
    <p class="motto"><span>Stay curious.</span> <span>Stay secure.</span> <span>Stay ahead.</span></p>
    <p class="fine">© {year} {e(SITE['name'])}. Content summarises public sources. Always confirm details with the vendor or original report.</p>
  </div>
</footer>
</body>
</html>
"""


def score_cell(p):
    score = p.get("score") or ""
    sev = p.get("severity") or ""
    if not sev:
        kind = KIND.get(p.get("category"), "Brief")
        return f'<span class="score kind kind-{e(p.get("category", ""))}"><span class="kind-label">{e(kind)}</span></span>'
    shown = score if score else "?"
    return (f'<span class="score sev-{e(sev)}" title="{e(SEV_LABEL.get(sev, sev))}">'
            f'<span class="score-num">{e(str(shown))}</span>'
            f'<span class="score-sev">{e(SEV_LABEL.get(sev, sev))}</span></span>')


def row(p):
    who = " ".join(x for x in [p.get("vendor", ""), p.get("product", "")] if x) or p.get("source", "")
    meta = f'<span>{e(who)}</span>' if who else f'<span>{e(CATS.get(p["category"], p["category"]))}</span>'
    return (f'<li class="row"><a href="{url(p["path"])}">{score_cell(p)}'
            f'<span class="row-main"><span class="row-title">{e(p["title"])}</span>'
            f'<span class="row-sum">{e(p["summary"])}</span>'
            f'<span class="row-meta">{meta}<time datetime="{e(p["date"])}">{nice_date(p["date"])}</time></span>'
            f'</span><span class="row-thumb"><img src="{url(p["cover"])}" alt="" width="240" height="126" loading="lazy" decoding="async"></span></a></li>')


def post_list(posts, empty="No briefings here yet. New ones appear after they are approved."):
    if not posts:
        return f'<p class="empty">{e(empty)}</p>'
    return '<ol class="rows">' + "".join(row(p) for p in posts) + "</ol>"


def write(path, content):
    target = OUT / path.lstrip("/")
    if path.endswith("/"):
        target = target / "index.html"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")


def build_post(p, posts):
    sev = p.get("severity")
    facts = []
    for label, key in [("CVE", "cve"), ("Vendor", "vendor"), ("Product", "product"), ("CVSS score", "score")]:
        if p.get(key):
            facts.append(f"<div><dt>{label}</dt><dd>{e(str(p[key]))}</dd></div>")
    if sev:
        facts.append(f"<div><dt>Severity</dt><dd>{e(SEV_LABEL.get(sev, sev))}</dd></div>")
    if p.get("level"):
        facts.append(f"<div><dt>Level</dt><dd>{e(p['level'])}</dd></div>")
    if p["category"] in ("theory", "practical", "weekly-recap"):
        facts.append(f"<div><dt>Reading time</dt><dd>{p['minutes']} min</dd></div>")
    if p.get("source") and p.get("source_url", "").startswith("http"):
        facts.append(f'<div><dt>Original report</dt><dd><a href="{e(p["source_url"])}" rel="noopener">{e(p["source"])}</a></dd></div>')
    if p.get("ransomware", "").lower() == "known":
        facts.append("<div><dt>Ransomware use</dt><dd>Reported by CISA</dd></div>")
    meter = ""
    if p.get("score"):
        try:
            v = max(0.0, min(10.0, float(p["score"])))
            meter = (f'<div class="meter sev-{e(sev)}" role="img" aria-label="CVSS {v} out of 10">'
                     f'<span style="width:{v * 10:.0f}%"></span></div>')
        except ValueError:
            pass
    related = [x for x in posts if x["category"] == p["category"] and x["slug"] != p["slug"]][:3]
    related_html = f'<section class="related"><h2>More {e(CATS.get(p["category"], "briefings")).lower()}</h2>{post_list(related)}</section>' if related else ""
    share_url = urllib.parse.quote(BASE_URL + p["path"], safe="")
    share_text = urllib.parse.quote(p["title"], safe="")
    body = f"""<article class="post">
  <figure class="cover"><img src="{url(p['cover'])}" alt="{e(p['cover_alt'])}" width="1200" height="630" decoding="async"></figure>
  <header class="post-head">
    <p class="crumb"><a href="{url('/category/' + p['category'] + '/')}">{e(CATS.get(p['category'], p['category']))}</a>
    <time datetime="{e(p['date'])}">{nice_date(p['date'])}</time></p>
    <h1>{e(p['title'])}</h1>
    {f'<p class="lead">{e(p["summary"])}</p>' if p['summary'] else ''}
    {meter}
    {f'<dl class="facts">{"".join(facts)}</dl>' if facts else ''}
  </header>
  <div class="prose">{p['html']}</div>
  <section class="thanks" aria-labelledby="thanks-title">
    <h2 id="thanks-title">Thank you for reading!</h2>
    <p>Let’s continue to build a safer and more trustworthy digital future together.</p>
    <ul class="thanks-actions">
      <li><a class="act t-news" href="https://www.linkedin.com/sharing/share-offsite/?url={share_url}" rel="noopener"><span class="act-ico">{icon("thumb")}</span><strong>Share</strong><span>on LinkedIn</span></a></li>
      <li><a class="act t-recap" href="https://www.facebook.com/sharer/sharer.php?u={share_url}" rel="noopener"><span class="act-ico">{icon("share")}</span><strong>Share</strong><span>on Facebook</span></a></li>
      <li><a class="act t-practical" href="https://t.me/share/url?url={share_url}&amp;text={share_text}" rel="noopener"><span class="act-ico">{icon("send")}</span><strong>Send</strong><span>on Telegram</span></a></li>
      <li><a class="act t-theory" href="{e(SITE.get('newsletter_url') or url('/feed.xml'))}" rel="noopener"><span class="act-ico">{icon("bell")}</span><strong>Subscribe</strong><span>for new posts</span></a></li>
    </ul>
    {('<p class="thanks-follow">Follow ZNexora Tech</p>' + social_pills()) if social_channels() else ''}
    <p class="thanks-motto">Stay curious. Stay secure. Stay ahead.</p>
  </section>
</article>
{related_html}"""
    write(p["path"], layout(p["title"], body, p["summary"], p["path"], "article", p["cover"]))


def build_home(posts):
    by = lambda *cats: [p for p in posts if p["category"] in cats]
    recap = by("weekly-recap")[:1]
    recap_html = ""
    if recap:
        r = recap[0]
        recap_html = f"""<section class="recap-feature">
  <a class="recap-art" href="{url(r['path'])}" tabindex="-1" aria-hidden="true"><img src="{url(r['cover'])}" alt="" width="1200" height="630" loading="lazy"></a>
  <p class="recap-kicker">This week in security</p>
  <h2><a href="{url(r['path'])}">{e(r['title'])}</a></h2>
  <p>{e(r['summary'])}</p>
  <a class="recap-link" href="{url(r['path'])}">Read the weekly recap</a>
</section>"""

    def block(title, items, link, empty, tone):
        return (f'<section class="{tone}"><div class="section-head"><h2>{e(title)}</h2>'
                f'<a href="{url(link)}">See all</a></div>{post_list(items, empty)}</section>')

    community = ""
    if social_channels():
        community = (f'<section class="community"><div><h2>Join the ZNexora community</h2>'
                     f'<p>Daily security news, tips and guides on your favourite platform.</p></div>{social_pills()}</section>')

    pillars = "".join(
        f'<li><a class="pillar {TONE[c]}" href="{url(link)}"><span class="pillar-ico">{icon(c, 26)}</span>'
        f'<strong>{e(name)}</strong><span>{e(text)}</span></a></li>' for c, link, name, text in PILLARS)

    body = f"""<section class="hero">
  <figure class="hero-cover"><picture>
    <source media="(max-width: 700px)" srcset="{url('/assets/cover-900.jpg')}">
    <img src="{url('/assets/cover.jpg')}" width="1536" height="1024" fetchpriority="high"
      alt="ZNexora Tech cover: Empowering minds. Securing futures. Cyber security, IT knowledge, AI and automation, cloud technologies and practical solutions.">
  </picture></figure>
  <div class="hero-intro">
    <h1>{e(SITE['tagline'])}</h1>
    <p>{e(SITE['description'])}</p>
  </div>
  <ul class="pillars">{pillars}</ul>
</section>
{recap_html}
{community}
<div class="home-grid">
  <div>
    {block("Latest news", by("news")[:6], "/category/news/", "The latest stories appear here once they are approved.", "t-news")}
    {block("Exploited vulnerabilities", by("exploited-vulnerabilities")[:5], "/category/exploited-vulnerabilities/", "New exploited vulnerabilities appear here once they are approved.", "t-exploit")}
  </div>
  <div>
    {block("Learn: theory and practice", by("theory", "practical")[:6], "/learn/", "Theory articles and practical guides appear here once they are approved.", "t-theory")}
  </div>
</div>"""
    write("/", layout(SITE["name"], body))


BANNER_TEXT = {
    "news": "The security stories that matter, in plain language.",
    "weekly-recap": "Every Monday: news, ransomware and web defacement in one read.",
    "exploited-vulnerabilities": "Vulnerabilities attackers are using right now.",
    "theory": "Security concepts, clearly explained.",
    "practical": "Hands-on guides for defending your systems.",
}


def banner(key, title, category, subtitle=""):
    """Make (once) and return the graphic for a section page."""
    rel = f"/covers/section-{key}.jpg"
    make_cover(OUT / rel.lstrip("/"), title, category, subtitle=subtitle, key="section-" + key)
    return rel


def list_page(path, title, items, key, category, subtitle):
    img = banner(key, title, category, subtitle)
    body = (f'<figure class="banner"><img src="{url(img)}" alt="" width="1200" height="630" decoding="async"></figure>'
            f'<h1 class="visually-hidden">{e(title)}</h1>{post_list(items)}')
    write(path, layout(title, body, f"{title}: {subtitle}", path, image=img))


def build_lists(posts):
    learn = [p for p in posts if p["category"] in ("theory", "practical")]
    list_page("/learn/", "Learn: theory and practice", learn, "learn", "theory", "Concepts and hands-on guides for defenders.")
    list_page("/posts/", "All posts", posts, "all", "news", "Everything published on ZNexora Tech.")
    for slug, name in CATS.items():
        list_page(f"/category/{slug}/", name, [p for p in posts if p["category"] == slug], slug, slug,
                  BANNER_TEXT.get(slug, ""))


def build_pages():
    for path in PAGES_DIR.glob("*.md"):
        meta, body = parse_front_matter(path.read_text(encoding="utf-8"))
        title = meta.get("title", path.stem.title())
        figure, img = "", "/assets/og-image.jpg"
        if path.stem == "about":
            img = "/assets/og-image.jpg"
            figure = f'<figure class="cover"><img src="{url(img)}" alt="ZNexora Tech logo" width="1200" height="630"></figure>'
        follow = ""
        if path.stem == "about" and social_channels():
            follow = '<section class="about-follow"><h2>Follow ZNexora Tech</h2>' + social_pills() + '</section>'
        write(f"/{path.stem}/", layout(title, f'<article class="post">{figure}<h1 class="page-title">{e(title)}</h1>'
                                              f'<div class="prose">{render_md(body)}</div>{follow}</article>', path=f"/{path.stem}/", image=img))


def build_feeds(posts):
    index = [{"t": p["title"], "u": url(p["path"]), "s": p["summary"], "c": p.get("cve", ""),
              "v": f'{p.get("vendor", "")} {p.get("product", "")}'} for p in posts]
    (OUT / "search-index.json").write_text(json.dumps(index, ensure_ascii=False), encoding="utf-8")

    def rfc822(iso):
        d = dt.datetime.fromisoformat(iso[:10]).replace(hour=8, tzinfo=dt.timezone.utc)
        return email.utils.format_datetime(d)
    items = "".join(f"""<item><title>{e(p['title'])}</title><link>{BASE_URL}{p['path']}</link>
<guid isPermaLink="true">{BASE_URL}{p['path']}</guid><pubDate>{rfc822(p['date'])}</pubDate>
<description>{e(p['summary'])}</description></item>""" for p in posts[:30])
    (OUT / "feed.xml").write_text(f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0"><channel><title>{e(SITE['name'])}</title><link>{BASE_URL}/</link>
<description>{e(SITE['description'])}</description><language>{e(SITE.get('language', 'en'))}</language>
{items}</channel></rss>
""", encoding="utf-8")

    pages = ["/", "/posts/", "/learn/"] + [f"/category/{s}/" for s in CATS] + [p["path"] for p in posts]
    urls = "".join(f"<url><loc>{BASE_URL}{u}</loc></url>" for u in pages)
    (OUT / "sitemap.xml").write_text(f'<?xml version="1.0" encoding="UTF-8"?>\n'
                                     f'<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>\n')
    (OUT / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {BASE_URL}/sitemap.xml\n")


def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()
    shutil.copytree(ROOT / "assets", OUT / "assets")
    posts = load_posts()
    for p in posts:
        if not p["own_image"]:
            make_cover(OUT / "covers" / f"{p['slug']}.jpg", p["title"], p["category"],
                       p.get("score", ""), p.get("severity", ""), key=p["slug"])
    print(f"Drew {sum(not p['own_image'] for p in posts)} graphic(s)")
    for p in posts:
        build_post(p, posts)
    build_home(posts)
    build_lists(posts)
    build_pages()
    build_feeds(posts)
    write("/404.html", layout("Page not found", '<h1 class="page-title">Page not found</h1>'
                                                f'<p>This page does not exist. <a href="{url("/")}">Go to the latest briefings</a> or search above.</p>'))
    (OUT / ".nojekyll").write_text("")
    if SITE.get("custom_domain"):
        (OUT / "CNAME").write_text(SITE["custom_domain"].strip() + "\n")
    print(f"Built {len(posts)} post(s) into _site/")


if __name__ == "__main__":
    main()
